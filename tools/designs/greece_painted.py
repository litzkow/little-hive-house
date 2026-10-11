"""Greece, hand-painted (gouache / storybook) edition: 30 magnets for Greek-American families and anyone who loves Greece.

Same painted idiom as the Brasil and Italia sets (brasil_painted.py, italia_painted.py): warm paper, layered washes
with pooled edges, brush strokes that follow each form, a warm brown pen line, hand-placed brush lettering, soft light
and paper grain. Colour story: Aegean cobalt and sky blue, whitewash with cool blue shadows, olive silver-green,
honey gold, terracotta, bougainvillea magenta and tomato red.

The site fonts carry no Greek alphabet (only Δ Ω μ π), so the hero words are romanized Greek ("Yia mas!", "Kalimera")
the way Greek-Americans write them, glossed lightly in English. Short Greek capitals (ΚΑΛΗΜΕΡΑ, ΓΙΑΓΙΑ, ΑΓΑΠΗ ΜΟΥ...)
are composed glyph by glyph by `gr_caps`: Latin look-alikes (Α Β Ε Ζ Η Ι Κ Μ Ν Ο Ρ Τ Υ Χ), the font's own Δ and Ω, Λ as a
turned V, Γ as a mirrored L, and Π Σ Φ Ξ built from stems, bars and bowls in the same stroke weights.

Run from tools/designs:  python3 greece_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ridge, ruled, shift, sky, soft_glow, specks, taper, qpts, catmull, steam_wisps)
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines, stripes_in, sea, seagull
from brasil_painted import (Doc2, ell_pts, pd, shade_over, light_over, gingham, cloth, leaf_simple, bird_v, heart_d,
                            p_heart, steam, wood_planks, cup_saucer, stamp, branch)
from italia_painted import olive, olive_leaf, olive_branch, lemon_it, citrus_leaf, plate_34, string_lights, geranium, \
    geranium_leaf, tomato, wine_glass, vine_leaf
from summer_gouache import honeybee
from paint import streaks
import holidays_gouache as hg

COL = "greece"
INK = "#3A2418"
FLECK = "#8A6A4A"

# (light, base, dark) gouache palettes
AEGEAN = ("#6A9AE0", "#1F56A8", "#0C2C66")
DEEP = ("#4A72C0", "#16397E", "#0A1C46")
SKYB = ("#C8E6F6", "#86C4EA", "#3A86C0")
TURQ = ("#9AE4E0", "#2AAAB4", "#0E6470")
WASH = ("#FFFFFF", "#F5F2EC", "#B4BCCC")      # whitewash with a cool blue shadow
WASH_W = ("#FFFDF6", "#F4EAD8", "#C8B494")    # warm whitewash in low sun
OLIVE = ("#C6CEA2", "#8A9858", "#46522A")
OLIVE_D = ("#9AA86A", "#5E6E34", "#2E3A16")
HONEY = ("#FFE08A", "#EDAA2C", "#A8640A")
GOLDEN = ("#FFE6A0", "#E8B456", "#A86E22")     # baked phyllo
TERRA = ("#EEA27A", "#C8643C", "#7A3218")
BOUG = ("#FF9AD0", "#D8287E", "#7E0C46")
TOMATO = ("#FF9A72", "#E23A26", "#8E140C")
RED = ("#F48A7A", "#D42A2A", "#7E1010")
COPPER = ("#F8C08A", "#C8743C", "#7A3816")
WOOD = ("#D8A06A", "#A86A3A", "#5E3618")
NOCE = ("#B07A4E", "#7A4A28", "#3E220E")
CREAM = ("#FFFDF6", "#F4EAD6", "#C8B494")
WHITE = ("#FFFFFF", "#F4F0E8", "#B8B0A6")
FETA = ("#FFFFFF", "#F8F4E6", "#CFC6A8")
ALU = ("#F6F8FC", "#B4BAC4", "#5E6470")
LEMON = ("#FFF39A", "#F8D42A", "#BE940A")
GREEN = ("#9AD27A", "#4A9A3A", "#1E5A1E")
ROCK = ("#C8A890", "#8A6A58", "#4A3428")

lt, dk = hg.lt, hg.dk

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def finish_g(D, out, seed, color=INK, op=1.0):
    return finish(D, out, seed, color, op)


def pal3(c, a=0.35, b=0.35):
    return (lt(c, a), c, dk(c, b))


# ================================================================ Greek capitals, composed glyph by glyph
LATIN_LIKE = {"Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H", "Ι": "I", "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O",
              "Ρ": "P", "Τ": "T", "Υ": "Y", "Χ": "X", "Δ": "Δ", "Ω": "Ω", " ": " "}


def _gr_adv(ch, font, size):
    if ch in LATIN_LIKE:
        return measure(LATIN_LIKE[ch], font, size)
    return {"Λ": measure("V", font, size), "Γ": measure("L", font, size) * 0.96, "Π": measure("H", font, size) * 1.0,
            "Σ": measure("E", font, size) * 1.02, "Φ": measure("O", font, size) * 0.98, "Ξ": measure("E", font, size)}[ch]


def gr_width(word, font, size, ls=0):
    return sum(_gr_adv(c, font, size) for c in word) + ls * max(0, len(word) - 1)


def gr_glyphs(x0, y, word, font, size, ls=0, stem=0.13, hair=0.055):
    """Glyph elements (no fill) for a Greek capital word starting at x0 on baseline y. stem / hair: thick and thin
    stroke weights as a fraction of the size (Cinzel 600 ~ 0.13 / 0.055)."""
    cap = size * 0.70
    cy = y - cap / 2
    S, Hh = size * stem, size * hair
    g = []
    x = x0
    for ch in word:
        adv = _gr_adv(ch, font, size)
        if ch in LATIN_LIKE:
            if ch != " ":
                g.append(f'<text x="{x:.1f}" y="{y:.1f}" {font} font-size="{size:.1f}">{esc(LATIN_LIKE[ch])}</text>')
        elif ch == "Λ":
            g.append(f'<text x="{x:.1f}" y="{y:.1f}" {font} font-size="{size:.1f}" transform="rotate(180 {x + adv / 2:.1f} {cy:.1f})">V</text>')
        elif ch == "Γ":
            g.append(f'<text x="{x:.1f}" y="{y:.1f}" {font} font-size="{size:.1f}" transform="translate(0 {2 * cy:.1f}) scale(1 -1)">L</text>')
        elif ch == "Π":
            # two serifed stems (the I glyph) under a hairline-plus top bar
            wI = measure("I", font, size)
            m = adv * 0.1
            g.append(f'<text x="{x + m - wI * 0.08:.1f}" y="{y:.1f}" {font} font-size="{size:.1f}">I</text>')
            g.append(f'<text x="{x + adv - m - wI * 0.92:.1f}" y="{y:.1f}" {font} font-size="{size:.1f}">I</text>')
            g.append(f'<rect x="{x + m - wI * 0.02:.1f}" y="{y - cap:.1f}" width="{adv - 2 * m + wI * 0.04:.1f}" height="{max(Hh * 1.35, 1.5):.1f}"/>')
        elif ch == "Σ":
            w = adv * 0.86
            l = x + adv * 0.07
            pts = [(l, y - cap), (l + w, y - cap), (l + w + Hh * 0.2, y - cap + cap * 0.24), (l + w - Hh * 0.6, y - cap + cap * 0.24),
                   (l + w - Hh * 0.9, y - cap + Hh * 1.2), (l + S * 1.15, y - cap + Hh * 1.2),
                   (l + w * 0.52, y - cap * 0.5), (l + w * 0.52 - S * 0.25, y - cap * 0.5 + S * 0.25),
                   (l + Hh * 2.4, y - Hh * 1.2), (l + w - Hh * 0.9, y - Hh * 1.2), (l + w - Hh * 0.6, y - cap * 0.26),
                   (l + w + Hh * 0.3, y - cap * 0.26), (l + w + Hh * 0.6, y), (l - Hh * 0.2, y), (l - Hh * 0.2, y - Hh * 0.6),
                   (l + w * 0.44, y - cap * 0.52), (l - Hh * 0.1, y - cap + Hh * 0.3)]
            g.append(f'<path d="{pd(pts)}"/>')
        elif ch == "Φ":
            ocx = x + adv / 2
            rx, ry = adv * 0.43, cap * 0.33
            g.append(f'<path d="M {ocx - rx:.1f} {cy:.1f} a {rx:.1f} {ry:.1f} 0 1 0 {2 * rx:.1f} 0 a {rx:.1f} {ry:.1f} 0 1 0 {-2 * rx:.1f} 0 Z '
                     f'M {ocx - rx + S * 0.7:.1f} {cy:.1f} a {rx - S * 0.7:.1f} {ry - Hh * 0.9:.1f} 0 1 1 {2 * (rx - S * 0.7):.1f} 0 a {rx - S * 0.7:.1f} {ry - Hh * 0.9:.1f} 0 1 1 {-2 * (rx - S * 0.7):.1f} 0 Z" fill-rule="evenodd"/>')
            g.append(f'<rect x="{ocx - S / 2:.1f}" y="{y - cap:.1f}" width="{S:.1f}" height="{cap:.1f}"/>')
            g.append(f'<rect x="{ocx - S * 1.7:.1f}" y="{y - cap:.1f}" width="{S * 3.4:.1f}" height="{max(Hh, 1.2):.1f}"/>')
            g.append(f'<rect x="{ocx - S * 1.7:.1f}" y="{y - max(Hh, 1.2):.1f}" width="{S * 3.4:.1f}" height="{max(Hh, 1.2):.1f}"/>')
        elif ch == "Ξ":
            w = adv * 0.84
            l = x + adv * 0.08
            hb = max(Hh * 1.5, 1.6)
            g.append(f'<rect x="{l:.1f}" y="{y - cap:.1f}" width="{w:.1f}" height="{hb:.1f}"/>')
            g.append(f'<rect x="{l + w * 0.14:.1f}" y="{cy - hb / 2:.1f}" width="{w * 0.72:.1f}" height="{hb:.1f}"/>')
            g.append(f'<rect x="{l:.1f}" y="{y - hb:.1f}" width="{w:.1f}" height="{hb:.1f}"/>')
            for xx, yy in ((l, y - cap), (l + w - Hh, y - cap), (l, y - cap * 0.18), (l + w - Hh, y - cap * 0.18)):
                g.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="{max(Hh, 1.2):.1f}" height="{cap * 0.18:.1f}"/>')
        x += adv + ls
    return "".join(g)


def gr_caps(x, y, word, font, size, fill, ls=0, max_w=480, shadow=None, soff=(1.5, 2), stem=0.13, hair=0.055, op=1.0):
    """Centred Greek capitals at (x, baseline y), fitted to max_w."""
    while size > 10 and gr_width(word, font, size, ls) > max_w:
        size -= 1
    W = gr_width(word, font, size, ls)
    G = gr_glyphs(x - W / 2, y, word, font, size, ls, stem, hair)
    out = []
    if shadow:
        out.append(f'<g fill="{shadow}" transform="translate({soff[0]} {soff[1]})" opacity="{op}">{G}</g>')
    out.append(f'<g fill="{fill}" opacity="{op}">{G}</g>')
    return "".join(out)


def gr_ruled(x, y, word, fill, font=CINZEL, size=22, ls=4, line_w=40, gap=14, line=None, seed=3, max_w=380):
    while size > 10 and gr_width(word, font, size, ls) > max_w:
        size -= 1
    w = gr_width(word, font, size, ls)
    mid = y - size * 0.35
    lc = line or fill
    out = [gr_caps(x, y, word, font, size, fill, ls, max_w)]
    for sg in (-1, 1):
        a = x + sg * (w / 2 + gap)
        b = x + sg * (w / 2 + gap + line_w)
        out.append(pline([(a, mid), ((a + b) / 2, mid + 1.2), (b, mid - 0.6)], lc, 2.2, seed + sg, 0.9))
    return "".join(out)


# ================================================================ greek toolkit
def meander_path(x0, y0, unit, n, closed_ends=True):
    """Running Greek key (meander) as one polyline: n periods, each `unit` wide and `unit` tall, starting at the
    bottom-left (x0, y0 + unit). Grid of fifths so the bands and gaps read evenly."""
    u = unit / 10
    pts = []
    for k in range(n):
        bx = x0 + k * unit
        seg = [(0, 10), (0, 0), (8, 0), (8, 6), (4, 6), (4, 4), (6, 4), (6, 2), (2, 2), (2, 10)]
        pts += [(bx + px * u, y0 + py * u) for px, py in seg]
    pts.append((x0 + n * unit, y0 + 10 * u))
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def meander_band(D, x0, x1, y, h, col, bg=None, seed=1, w=None, rule=True, op=1.0):
    """A painted Greek-key border between x0 and x1, top at y, height h (the key itself fills ~70%)."""
    out = []
    if bg:
        d = hg.org_rect(x0, y, x1 - x0, h, seed, 0.6, 20, 1)
        out.append(f'<path d="{d}" fill="{bg}"/>')
    unit = h * 0.62
    n = int(math.ceil((x1 - x0) / unit)) + 1
    start = x0 - ((n * unit) - (x1 - x0)) / 2
    ky = y + (h - unit) / 2
    sw = w or unit * 0.13
    cid = D.clip(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="{h}"/>')
    path = meander_path(start, ky, unit, n)
    out.append(f'<g {cid} opacity="{op}"><path d="{path}" fill="none" stroke="{col}" stroke-width="{sw:.1f}" stroke-linejoin="miter" stroke-linecap="square"/>'
               f'<path d="{path}" fill="none" stroke="{lt(col, 0.35)}" stroke-width="{sw * 0.25:.1f}" stroke-linejoin="miter" opacity="0.35" transform="translate(-0.6 -0.6)"/></g>')
    if rule:
        for yy in (y + h * 0.06, y + h * 0.94):
            out.append(ink(hg.hline(x0, yy, x1, yy, seed + int(yy), 0.6, 30), col, max(1.6, sw * 0.6), seed, 1, 0.9 * op))
    return "".join(out)


def cool_shadow(D, d, op=0.35, x1=0, y1=0, x2=1, y2=0, start=0.4, col="#3A5A9A"):
    return shade_over(D, d, col, op, x1, y1, x2, y2, start)


def cube_house(D, x, base, w, h, seed, side=0.25, door=AEGEAN, shutters=None, windows=1, light="left", haze=0.0,
               roof_lip=True, sun_wall=None, door_arch=True, step=True):
    """Cycladic cube house in 3/4 view: lit whitewashed front, cool blue-grey side wall, a parapet lip, a painted
    door and small deep-set windows with coloured shutters."""
    rnd = random.Random(seed)
    hz = (lambda c: mix(c, "#C8D8EC", haze)) if haze else (lambda c: c)
    out = []
    sw_ = w * side
    sd = -1 if light == "right" else 1           # side wall to the right when light comes from the left
    front = rect_pts(x, base - h, x + w, base, 12, seed, 0.5)
    sx = x + w if sd > 0 else x
    sidep = [(sx, base - h), (sx + sw_ * sd, base - h - sw_ * 0.4), (sx + sw_ * sd, base - sw_ * 0.4), (sx, base)]
    out.append(f'<path d="{hg.org_poly(sidep, seed, 0.5, 12, 1)}" fill="{hz("#B8C4DA")}"/>')
    out.append(strokes(D.nid(), pd(sidep), bbox(sidep), [hz("#A8B6D0"), hz("#D0D8E8")], seed, n=max(4, int(sw_ * h / 140)), angle=-85,
                       length=(8, 24), width=(1, 2.4), opacity=(0.2, 0.45)))
    wall = sun_wall or WASH
    out.append(painted(D, front, tuple(hz(c) for c in wall), seed, sdir=(1 * sd, 0.4), sk=0.06, angle=-85,
                       n=max(6, int(w * h / 160)), inkw=1.0, inkop=0.45, hi=0.3, slen=(6, 22)))
    if roof_lip:
        lip = [(x - 2, base - h - 4), (x + w + 2, base - h - 4), (x + w + 2, base - h + 1), (x - 2, base - h + 1)]
        out.append(f'<path d="{hg.org_poly(lip, seed + 1, 0.4, 10, 1)}" fill="{hz("#FFFFFF")}"/>')
        out.append(f'<path d="M {x - 2:.1f} {base - h + 1.5:.1f} L {x + w + 2:.1f} {base - h + 1.5:.1f}" stroke="{hz("#A8B4CC")}" stroke-width="1.4" opacity="0.8"/>')
        tp = [(x - 2, base - h - 4), (sx + sw_ * sd + (2 if sd > 0 else -2), base - h - sw_ * 0.4 - 4), (sx + sw_ * sd, base - h - sw_ * 0.4 + 1),
              (x + w + 2 if sd > 0 else x - 2, base - h + 1)] if sd > 0 else None
        if sd > 0:
            out.append(f'<path d="{pd([(x + w + 2, base - h - 4), (x + w + sw_ + 2, base - h - sw_ * 0.4 - 4), (x + w + sw_ + 2, base - h - sw_ * 0.4 + 1), (x + w + 2, base - h + 1)])}" fill="{hz("#DCE2EE")}"/>')
    # windows
    sh = shutters or door or AEGEAN
    for k in range(windows):
        wx = x + w * ((k + 0.5) / windows) - min(10, w * 0.14) / 2 + (w * 0.12 if windows == 1 else 0)
        wy = base - h * 0.74
        ww_, wh_ = min(11, w * 0.16), min(13, h * 0.24)
        out.append(f'<rect x="{wx - 1:.1f}" y="{wy - 1:.1f}" width="{ww_ + 2:.1f}" height="{wh_ + 2:.1f}" fill="{hz("#C8D0DE")}"/>')
        out.append(f'<path d="{hg.org_rect(wx, wy, ww_, wh_, seed + 10 + k, 0.3, 6, 1)}" fill="{hz(sh[1])}"/>')
        out.append(f'<path d="M {wx + ww_ / 2:.1f} {wy:.1f} L {wx + ww_ / 2:.1f} {wy + wh_:.1f}" stroke="{hz(sh[2])}" stroke-width="1"/>')
        out.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{ww_:.1f}" height="2" fill="{hz(sh[0])}" opacity="0.6"/>')
    # door
    if door:
        dw, dh = min(14, w * 0.22), min(h * 0.5, 26)
        dx = x + w * 0.16 if windows == 1 else x + w * 0.5 - dw / 2
        if door_arch:
            dd = f"M {dx:.1f} {base:.1f} L {dx:.1f} {base - dh + dw / 2:.1f} A {dw / 2:.1f} {dw / 2:.1f} 0 0 1 {dx + dw:.1f} {base - dh + dw / 2:.1f} L {dx + dw:.1f} {base:.1f} Z"
        else:
            dd = hg.org_rect(dx, base - dh, dw, dh, seed + 20, 0.3, 6, 1)
        out.append(f'<path d="{dd}" fill="{hz(door[1])}"/>')
        out.append(f'<path d="{dd}" fill="none" stroke="{hz(door[2])}" stroke-width="1.2"/>')
        out.append(f'<path d="M {dx + dw * 0.5:.1f} {base - dh + 3:.1f} L {dx + dw * 0.5:.1f} {base:.1f}" stroke="{hz(door[2])}" stroke-width="0.9" opacity="0.7"/>')
        if step:
            out.append(f'<rect x="{dx - 3:.1f}" y="{base - 2.5:.1f}" width="{dw + 6:.1f}" height="3" fill="{hz("#FFFFFF")}"/>')
    return "".join(out)


def blue_dome(D, cx, base, r, seed, pal=AEGEAN, cross=True, drum=0.35, light=(-0.7, -0.6), haze=0.0, belt=True):
    """Whitewashed church drum topped by a blue painted dome with a little iron cross."""
    hz = (lambda c: mix(c, "#C8D8EC", haze)) if haze else (lambda c: c)
    out = []
    dh = r * drum
    drum_pts = rect_pts(cx - r * 0.92, base - dh, cx + r * 0.92, base, 10, seed, 0.3)
    out.append(painted(D, drum_pts, tuple(hz(c) for c in WASH), seed, sdir=(-light[0], 0.2), sk=0.12, angle=-90, n=10, inkw=1.0, inkop=0.4, hi=0.3))
    if belt:
        out.append(f'<path d="M {cx - r * 0.95:.1f} {base - dh:.1f} L {cx + r * 0.95:.1f} {base - dh:.1f}" stroke="{hz("#FFFFFF")}" stroke-width="{max(2, r * 0.08):.1f}"/>')
        for k in range(-2, 3):
            out.append(f'<rect x="{cx + k * r * 0.34 - r * 0.05:.1f}" y="{base - dh * 0.8:.1f}" width="{r * 0.1:.1f}" height="{dh * 0.6:.1f}" rx="{r * 0.05:.1f}" fill="{hz("#3A4A6A")}"/>')
    pts = [(cx + r * 0.94 * math.cos(math.radians(a)), base - dh - r * 0.98 * math.sin(math.radians(a))) for a in range(0, 181, 12)]
    out.append(painted(D, pts, tuple(hz(c) for c in pal), seed + 1, sdir=(-light[0], -light[1]), sk=0.2, angle=-60, n=int(r * 0.9) + 6,
                       inkw=max(1, r * 0.03), inkop=0.6, hi=0.45, hik=0.1))
    out.append(taper([(cx - r * 0.6, base - dh - r * 0.45), (cx - r * 0.45, base - dh - r * 0.75), (cx - r * 0.18, base - dh - r * 0.9)], max(1.4, r * 0.06), max(1, r * 0.03), hz("#FFFFFF"), 0.55))
    if cross:
        top = base - dh - r * 0.98
        out.append(f'<rect x="{cx - max(1.6, r * 0.03):.1f}" y="{top - r * 0.32:.1f}" width="{max(3, r * 0.06):.1f}" height="{r * 0.34:.1f}" fill="{hz("#3A3A40")}"/>')
        out.append(f'<rect x="{cx - r * 0.11:.1f}" y="{top - r * 0.24:.1f}" width="{r * 0.22:.1f}" height="{max(2.4, r * 0.05):.1f}" fill="{hz("#3A3A40")}"/>')
    return "".join(out)


def bougainvillea(D, cx, cy, rx, ry, seed, n=90, pal=BOUG, size=(4, 9), leaves=True, light=(-0.6, -0.7)):
    """A cascade of bougainvillea: papery magenta bracts in clusters with a few dark leaves showing through."""
    rnd = random.Random(seed)
    out = []
    if leaves:
        out.append(dab_crown(D, cx, cy, rx * 0.95, ry * 0.95, [GREEN, ("#7AB85A", "#3A7A2A", "#1A4416")], seed, n=int(n * 0.4), size=(size[0] * 0.9, size[1] * 0.9),
                             light=light, inkw=0, base=True))
    items = []
    for i in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        r = math.sqrt(rnd.random()) * 0.95
        x, y = cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r
        l = -(math.cos(a) * light[0] + math.sin(a) * light[1]) * r
        col = pal[0] if l > 0.3 else (pal[2] if l < -0.4 else rnd.choice([pal[1], pal[1], lt(pal[1], 0.15)]))
        items.append((l, x, y, col))
    for l, x, y, col in sorted(items):
        s = rnd.uniform(*size)
        for j in range(3):
            aa = j * 2.09 + rnd.uniform(0, 1)
            out.append(f'<path d="{blob(x + math.cos(aa) * s * 0.45, y + math.sin(aa) * s * 0.45, s * 0.6, s * 0.48, rnd.randint(0, 9999), 0.15, 8, math.degrees(aa))}" fill="{col}" opacity="{rnd.uniform(0.8, 1):.2f}"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(0.8, s * 0.12):.1f}" fill="#FFF2C8" opacity="0.85"/>')
    return "".join(out)


def mati(D, cx, cy, r, seed, rim=True, tilt=0):
    """Evil-eye glass bead (mati): cobalt glass disc, white ring, pale blue ring, black pupil, glassy highlights."""
    out = [cast(D, cx + r * 0.12, cy + r * 0.16, r * 1.05, r * 1.0, strength=0.28, seed=seed)]
    out.append(painted(D, blob_pts(cx, cy, r, r * 0.97, seed, 0.02, 24, tilt), DEEP, seed, sdir=(0.6, 0.7), sk=0.14, angle=-40, n=int(r * 0.8) + 6,
                       inkw=max(1, r * 0.035), inkop=0.6, hi=0.35, hik=0.08))
    out.append(f'<path d="{blob(cx, cy, r * 0.6, r * 0.58, seed + 1, 0.02, 20)}" fill="#FFFFFF"/>')
    out.append(f'<path d="{blob(cx, cy, r * 0.44, r * 0.43, seed + 2, 0.02, 18)}" fill="#7EC4F0"/>')
    out.append(f'<path d="{blob(cx + r * 0.04, cy + r * 0.05, r * 0.44, r * 0.43, seed + 2, 0.02, 18)}" fill="#3A8AD0" opacity="0.35"/>')
    out.append(f'<path d="{blob(cx, cy, r * 0.22, r * 0.22, seed + 3, 0.02, 14)}" fill="#0E0E18"/>')
    out.append(f'<path d="{blob(cx - r * 0.3, cy - r * 0.42, r * 0.2, r * 0.08, seed + 4, 0.1, 10, -35)}" fill="#FFFFFF" opacity="0.75"/>')
    out.append(f'<circle cx="{cx - r * 0.07:.1f}" cy="{cy - r * 0.07:.1f}" r="{r * 0.06:.1f}" fill="#FFFFFF" opacity="0.9"/>')
    out.append(taper([(cx + r * 0.5, cy + r * 0.6), (cx + r * 0.72, cy + r * 0.3), (cx + r * 0.8, cy)], max(1, r * 0.03), max(1.4, r * 0.06), "#9AC8F8", 0.6))
    if rim:
        out.append(ink(blob(cx, cy, r * 0.6, r * 0.58, seed + 1, 0.02, 20), "#14347A", max(0.8, r * 0.02), seed, 1, 0.4))
    return "".join(out)


def caique(D, cx, wl, L, seed, hull=WASH, band=AEGEAN, trim=RED, cabin=True, flip=False, mast=True, reflect=True, wake=None):
    """Greek wooden caique (kaiki): high pointed bow and stern, sweeping sheer, white hull with a blue band and red
    rubbing strake, small wheelhouse. (cx, wl) = centre on the waterline."""
    f = -1 if flip else 1
    def P(x, y):
        return (cx + f * x * L, wl + y * L)
    out = []
    if reflect:
        rp = [P(-0.48, 0.0), P(0.46, 0.0), P(0.36, 0.12), P(-0.36, 0.12)]
        out.append(f'<path d="{smooth_closed(rp)}" fill="{band[1]}" opacity="0.18"/>')
    hullp = [P(-0.52, -0.2), P(-0.3, -0.13), P(0.0, -0.11), P(0.3, -0.13), P(0.54, -0.24), P(0.5, -0.12), P(0.42, -0.02),
             P(0.2, 0.03), P(-0.2, 0.03), P(-0.42, -0.02), P(-0.49, -0.1)]
    out.append(painted(D, hullp, hull, seed, sdir=(0, 1), sk=0.1, angle=0, n=int(L * 0.25) + 6, inkw=max(1.2, L * 0.012), inkop=0.7, hi=0.3))
    hd = smooth_closed(hullp)
    cid = D.clip(f'<path d="{hd}"/>')
    inner = [f'<path d="{smooth_open([P(-0.55, -0.15), P(-0.3, -0.07), P(0, -0.05), P(0.3, -0.07), P(0.56, -0.18)])} L {P(0.56, 0.2)[0]:.1f} {P(0.56, 0.2)[1]:.1f} L {P(-0.56, 0.2)[0]:.1f} {P(-0.56, 0.2)[1]:.1f} Z" fill="{band[1]}"/>',
             f'<path d="{smooth_open([P(-0.55, -0.15), P(-0.3, -0.07), P(0, -0.05), P(0.3, -0.07), P(0.56, -0.18)])}" stroke="{trim[1]}" stroke-width="{max(2, L * 0.022):.1f}" fill="none"/>',
             f'<path d="{smooth_open([P(-0.55, -0.0), P(0, 0.0), P(0.56, -0.0)])}" stroke="{TERRA[1]}" stroke-width="{max(2, L * 0.03):.1f}" fill="none"/>',
             shade_over(D, hd, "#0A1A3A", 0.3, 0, 0, 0, 1, 0.5)]
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(smooth_open([P(-0.52, -0.2), P(-0.3, -0.13), P(0.0, -0.11), P(0.3, -0.13), P(0.54, -0.24)]), "#7A4A28", max(1.6, L * 0.016), seed, 1, 0.9))
    if cabin:
        cb = rect_pts(*sorted([P(-0.3, -0.24)[0], P(-0.08, -0.24)[0]]), P(0, -0.24)[1], P(0, -0.12)[1], 8, seed, 0.3) if False else None
        x0, x1 = sorted([P(-0.32, 0)[0], P(-0.1, 0)[0]])
        y0, y1 = P(0, -0.25)[1], P(0, -0.115)[1]
        out.append(painted(D, rect_pts(x0, y0, x1, y1, 8, seed + 3, 0.3), WASH, seed + 3, sdir=(1, 0.3), sk=0.12, angle=-90, n=6, inkw=1, inkop=0.6, hi=0.3))
        out.append(f'<rect x="{x0 - 2:.1f}" y="{y0 - 3:.1f}" width="{x1 - x0 + 4:.1f}" height="4" fill="{band[1]}"/>')
        for k in range(2):
            wx = x0 + (x1 - x0) * (0.18 + 0.44 * k)
            out.append(f'<rect x="{wx:.1f}" y="{y0 + (y1 - y0) * 0.25:.1f}" width="{(x1 - x0) * 0.24:.1f}" height="{(y1 - y0) * 0.35:.1f}" fill="#2A3A5A"/>')
    if mast:
        mx, my = P(0.18, -0.12)
        out.append(taper([(mx, my), (mx + f * L * 0.01, my - L * 0.32)], max(2, L * 0.016), max(1, L * 0.008), "#7A5A3A"))
        out.append(pline([(mx + f * L * 0.01, my - L * 0.3), P(0.52, -0.23)], "#5A4A3A", 1, seed, 0.7, 1))
    return "".join(out)


def ouzo_glass(D, cx, base, h, seed, w=None, fill=0.78, milky=True, ice=True, tilt=0):
    """Tall narrow ouzo glass: clouded white anise drink with ice cubes, glassy edges and highlights."""
    w = w or h * 0.42
    out = [cast(D, cx + 4, base, w * 0.75, 6, strength=0.35, seed=seed)]
    g = []
    top = base - h
    body = [(cx - w / 2, top), (cx - w * 0.46, base - 6), (cx - w * 0.38, base), (cx + w * 0.38, base), (cx + w * 0.46, base - 6), (cx + w / 2, top)]
    bd = pd(body)
    g.append(f'<path d="{bd}" fill="#E8F2F4" opacity="0.55"/>')
    lt_ = base - h * fill
    liq = [(cx - w * 0.48, lt_), (cx - w * 0.45, base - 7), (cx - w * 0.36, base - 3), (cx + w * 0.36, base - 3), (cx + w * 0.45, base - 7), (cx + w * 0.48, lt_)]
    ld = pd(liq)
    grad = D.lin([(0, "#FFFFFF", 0.96), (0.45, "#F4F2EA", 0.94), (0.8, "#D8DEE4", 0.95), (1, "#AEBCC8", 0.95)], 0, 0, 1, 0)
    g.append(f'<path d="{ld}" fill="{grad if milky else "#E8F6FA"}"/>')
    cid = D.clip(f'<path d="{ld}"/>')
    inner = [strokes(D.nid(), ld, bbox(liq), ["#FFFFFF", "#C8D4DE", "#E8E4D8", "#B8C8D8"], seed, n=26, angle=-90, length=(10, 34), width=(1.5, 4), opacity=(0.2, 0.55)),
             f'<rect x="{cx - w / 2:.1f}" y="{base - 12:.1f}" width="{w:.1f}" height="12" fill="#C8D8E0" opacity="0.5"/>']
    if ice:
        rnd = random.Random(seed)
        for k in range(3):
            ix, iy, s = cx + rnd.uniform(-w * 0.2, w * 0.2), lt_ + 8 + k * h * 0.17, w * rnd.uniform(0.32, 0.4)
            cube = rot(rect_pts(ix - s / 2, iy - s / 2, ix + s / 2, iy + s / 2, 6, seed + k, 0.4), ix, iy, rnd.uniform(-20, 20))
            inner.append(f'<path d="{smooth_closed(cube)}" fill="#FFFFFF" opacity="0.55"/>')
            inner.append(ink(smooth_closed(cube), "#B8C8D0", 1.1, seed + k, 1, 0.7))
            inner.append(f'<path d="M {ix - s * 0.3:.1f} {iy - s * 0.25:.1f} l {s * 0.25:.1f} {-s * 0.05:.1f}" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>')
    out.append("".join(g))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, lt_, w * 0.48, w * 0.1, 0, 360, 16))}" fill="#FFFFFF" opacity="0.9"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, w / 2, w * 0.11, 0, 360, 18))}" fill="none" stroke="#9AB0B8" stroke-width="1.6"/>')
    out.append(ink(bd, "#7A8A90", 1.6, seed, 1, 0.75))
    out.append(taper([(cx - w * 0.36, top + 8), (cx - w * 0.34, base - h * 0.4), (cx - w * 0.3, base - 10)], 3.2, 1.2, "#FFFFFF", 0.85))
    out.append(taper([(cx + w * 0.33, top + 14), (cx + w * 0.32, top + h * 0.3)], 1.6, 0.8, "#FFFFFF", 0.7))
    out.append(f'<path d="{smooth_open(ell_pts(cx, base - 2, w * 0.38, 3, 0, 180, 10))}" stroke="#9AB0B8" stroke-width="2.4" fill="none"/>')
    return "".join(out)


def demitasse(D, cx, base, w, seed, glaze=WHITE, band=None, coffee=True, handle=1, foam=True):
    """Small Greek coffee cup (flitzani) on its saucer, with the tan foam (kaimaki) on top."""
    out = [cast(D, cx + 6, base, w * 0.8, 7, strength=0.4, seed=seed)]
    sau = ell_pts(cx, base - 6, w * 0.74, w * 0.15, 0, 360, 28)
    out.append(painted(D, sau, glaze, seed, sdir=(0.5, 1), sk=0.15, angle=0, n=10, inkw=1.6, hi=0.4))
    if band:
        out.append(ink(smooth_open(ell_pts(cx, base - 7, w * 0.64, w * 0.12, 15, 165, 12)), band, 2.2, seed, 1, 0.85))
    top, h = base - 9 - w * 0.68, w * 0.68
    l, r = cx - w / 2, cx + w / 2
    hx = r if handle > 0 else l
    hp = f"M {hx - 3 * handle:.1f} {top + h * 0.22:.1f} q {w * 0.3 * handle:.1f} {-h * 0.04:.1f} {w * 0.22 * handle:.1f} {h * 0.4:.1f} q {-w * 0.06 * handle:.1f} {h * 0.2:.1f} {-w * 0.22 * handle:.1f} {h * 0.2:.1f}"
    out.append(ink(hp, glaze[2], 5, seed, 1, 1) + ink(hp, glaze[0], 2.2, seed + 1, 1, 1))
    cup = [(l, top), (l + w * 0.02, top + h * 0.5), (l + w * 0.12, top + h * 0.88), (cx, top + h), (r - w * 0.12, top + h * 0.88), (r - w * 0.02, top + h * 0.5), (r, top)]
    out.append(painted(D, cup, glaze, seed + 2, sdir=(0.9, 0.3), sk=0.18, angle=-90, n=14, inkw=1.8, hi=0.5, hik=0.08))
    if band:
        out.append(ink(smooth_open([(l + 1.5, top + h * 0.16), (cx, top + h * 0.24), (r - 1.5, top + h * 0.16)]), band, 2.8, seed + 3, 1, 0.9))
        out.append(ink(smooth_open([(l + 3, top + h * 0.3), (cx, top + h * 0.38), (r - 3, top + h * 0.3)]), band, 1.3, seed + 4, 1, 0.8))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, w / 2, w * 0.12, 0, 360, 24))}" fill="{glaze[1]}"/>')
    if coffee:
        out.append(f'<path d="{smooth_closed(ell_pts(cx, top + 1.5, w / 2 - 3.5, w * 0.095, 0, 360, 24))}" fill="{"#C89A62" if foam else "#2A1206"}"/>')
        if foam:
            rnd = random.Random(seed)
            for _ in range(int(w * 0.5)):
                a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random())
                out.append(f'<circle cx="{cx + math.cos(a) * rr * (w / 2 - 6):.1f}" cy="{top + 1.5 + math.sin(a) * rr * (w * 0.08):.1f}" r="{rnd.uniform(0.6, 1.6):.1f}" fill="{rnd.choice(["#E8C898", "#9A6A3A", "#F2DCB4"])}" opacity="0.8"/>')
            out.append(f'<path d="{smooth_open(ell_pts(cx, top + 1.5, w / 2 - 3.5, w * 0.095, 180, 360, 14))}" stroke="#7A4A22" stroke-width="1.2" fill="none" opacity="0.6"/>')
    out.append(ink(smooth_closed(ell_pts(cx, top, w / 2, w * 0.12, 0, 360, 24)), INK, 1.4, seed + 4, 1, 0.7))
    out.append(taper([(l + w * 0.1, top + h * 0.2), (l + w * 0.14, top + h * 0.62)], 3, 1, "#FFFFFF", 0.9))
    return "".join(out)


def water_glass(D, cx, base, h, seed, w=None, level=0.82):
    """Plain glass of cold water, beaded with condensation."""
    w = w or h * 0.6
    top = base - h
    body = [(cx - w / 2, top), (cx - w * 0.44, base), (cx + w * 0.44, base), (cx + w / 2, top)]
    out = [cast(D, cx + 5, base, w * 0.7, 6, strength=0.3, seed=seed)]
    out.append(f'<path d="{pd(body)}" fill="#DCEEF4" opacity="0.6"/>')
    wl_ = base - h * level
    liq = [(cx - w * 0.48, wl_), (cx - w * 0.44, base - 2), (cx + w * 0.44, base - 2), (cx + w * 0.48, wl_)]
    out.append(f'<path d="{pd(liq)}" fill="{D.lin([(0, "#BEE4F2", 0.8), (1, "#8CC8E0", 0.8)])}"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, wl_, w * 0.48, w * 0.08, 0, 360, 16))}" fill="#E8F8FC" opacity="0.9"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, w / 2, w * 0.09, 0, 360, 16))}" fill="none" stroke="#8AA8B4" stroke-width="1.5"/>')
    out.append(ink(pd(body), "#6A8A98", 1.5, seed, 1, 0.75))
    out.append(taper([(cx - w * 0.33, top + 6), (cx - w * 0.3, base - 8)], 3.5, 1.2, "#FFFFFF", 0.85))
    rnd = random.Random(seed)
    for _ in range(int(h * 0.5)):
        x, y = rnd.uniform(cx - w * 0.4, cx + w * 0.42), rnd.uniform(wl_ + 4, base - 6)
        r = rnd.uniform(0.8, 2.2)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#FFFFFF" opacity="0.75"/><circle cx="{x + r * 0.3:.1f}" cy="{y + r * 0.3:.1f}" r="{r * 0.6:.1f}" fill="#6A9AB0" opacity="0.35"/>')
    return "".join(out)


def cat(D, cx, base, s, seed, pal=("#FFD8A0", "#E89A48", "#9A5418"), pose="loaf", stripes=True, flip=False, eyes="closed"):
    """A Greek island cat. pose='loaf' (tucked, front view-ish), 'curl' (asleep in a ring), 'sit' (side, sitting)."""
    f = -1 if flip else 1
    def P(x, y):
        return (cx + f * x * s, base + y * s)
    out = [cast(D, cx, base, s * 0.6, s * 0.07, strength=0.35, seed=seed)]
    if pose == "curl":
        body = [P(-0.5, -0.02), P(-0.52, -0.2), P(-0.36, -0.36), P(-0.06, -0.42), P(0.26, -0.38), P(0.46, -0.24), P(0.5, -0.06), P(0.3, 0.0), P(-0.2, 0.01)]
        out.append(painted(D, body, pal, seed, sdir=(0.5, 0.8), sk=0.16, angle=-20, n=int(s * 0.4), inkw=max(1.2, s * 0.012), hi=0.4))
        if stripes:
            bd = smooth_closed(body)
            cid = D.clip(f'<path d="{bd}"/>')
            st = []
            for k in range(6):
                t = -0.35 + k * 0.14
                st.append(taper([P(t, -0.44), P(t + 0.04, -0.3), P(t - 0.01, -0.16)], max(2, s * 0.04), 1, pal[2], 0.55))
            out.append(f'<g {cid}>{"".join(st)}</g>')
        # tail wrapping round the front
        out.append(taper([P(0.44, -0.08), P(0.2, 0.02), P(-0.1, 0.02), P(-0.32, -0.04)], max(4, s * 0.1), max(2, s * 0.05), pal[1]))
        out.append(taper([P(0.44, -0.1), P(0.2, -0.0), P(-0.1, -0.0)], max(1.2, s * 0.02), 0.6, pal[0], 0.7))
        out.append(pline([P(0.44, -0.04), P(0.2, 0.05), P(-0.1, 0.05), P(-0.32, -0.01)], INK, max(1, s * 0.01), seed, 0.5, 1))
        # head tucked at the left, ears up
        hx, hy = P(-0.36, -0.2)
        head = blob_pts(hx, hy, s * 0.18, s * 0.15, seed + 2, 0.04, 16)
        out.append(painted(D, head, pal, seed + 2, sdir=(0.5, 0.8), sk=0.15, angle=-30, n=10, inkw=max(1.2, s * 0.012), hi=0.4))
        for dx in (-0.12, 0.06):
            ex = hx + f * dx * s
            ear = [(ex - f * s * 0.05, hy - s * 0.1), (ex - f * s * 0.01, hy - s * 0.25), (ex + f * s * 0.07, hy - s * 0.1)]
            out.append(f'<path d="{pd(ear)}" fill="{pal[1]}"/><path d="{pd([(ex - f * s * 0.02, hy - s * 0.11), (ex, hy - s * 0.2), (ex + f * s * 0.04, hy - s * 0.11)])}" fill="#F2A8A0"/>')
            out.append(ink(pd(ear, False), INK, max(1, s * 0.01), seed, 1, 0.6))
        for dx in (-0.08, 0.06):
            ex = hx + f * dx * s
            out.append(pline([(ex - s * 0.035, hy - s * 0.01), (ex, hy + s * 0.012), (ex + s * 0.035, hy - s * 0.01)], "#2A1A10", max(1.4, s * 0.012), seed, 0.9, 1))
        out.append(f'<path d="M {hx - s * 0.015:.1f} {hy + s * 0.05:.1f} l {s * 0.03:.1f} 0 l {-s * 0.015:.1f} {s * 0.02:.1f} Z" fill="#D87A7A"/>')
        for sg in (-1, 1):
            out.append(pline([(hx + sg * s * 0.06, hy + s * 0.06), (hx + sg * s * 0.2, hy + s * 0.05)], "#FFFFFF", 1, seed + sg, 0.7, 1))
        return "".join(out)
    if pose == "sit":
        body = [P(-0.18, 0), P(-0.24, -0.2), P(-0.16, -0.46), P(-0.02, -0.6), P(0.12, -0.56), P(0.2, -0.36), P(0.26, -0.12), P(0.2, 0)]
        out.append(taper([P(0.2, -0.02), P(0.42, -0.02), P(0.5, -0.12), P(0.46, -0.24)], max(4, s * 0.07), max(2, s * 0.04), pal[1]))
        out.append(painted(D, body, pal, seed, sdir=(0.7, 0.5), sk=0.18, angle=-80, n=int(s * 0.3), inkw=max(1.2, s * 0.012), hi=0.4))
        if stripes:
            bd = smooth_closed(body)
            cid = D.clip(f'<path d="{bd}"/>')
            st = [taper([P(-0.3, -0.12 - k * 0.1), P(0, -0.15 - k * 0.1), P(0.3, -0.1 - k * 0.1)], max(2, s * 0.035), 1, pal[2], 0.5) for k in range(4)]
            out.append(f'<g {cid}>{"".join(st)}</g>')
        hx, hy = P(-0.02, -0.66)
        head = blob_pts(hx, hy, s * 0.15, s * 0.13, seed + 2, 0.04, 16)
        out.append(painted(D, head, pal, seed + 2, sdir=(0.5, 0.8), sk=0.15, angle=-30, n=10, inkw=max(1.2, s * 0.012), hi=0.4))
        for dx in (-0.09, 0.08):
            ex = hx + dx * s
            ear = [(ex - s * 0.05, hy - s * 0.07), (ex, hy - s * 0.22), (ex + s * 0.05, hy - s * 0.07)]
            out.append(f'<path d="{pd(ear)}" fill="{pal[1]}"/><path d="{pd([(ex - s * 0.025, hy - s * 0.08), (ex, hy - s * 0.17), (ex + s * 0.025, hy - s * 0.08)])}" fill="#F2A8A0"/>')
            out.append(ink(pd(ear, False), INK, max(1, s * 0.01), seed, 1, 0.6))
        for dx in (-0.055, 0.055):
            ex = hx + dx * s
            if eyes == "closed":
                out.append(pline([(ex - s * 0.03, hy - s * 0.0), (ex, hy + s * 0.015), (ex + s * 0.03, hy - s * 0.0)], "#2A1A10", max(1.4, s * 0.012), seed, 0.9, 1))
            else:
                out.append(f'<ellipse cx="{ex:.1f}" cy="{hy:.1f}" rx="{s * 0.022:.1f}" ry="{s * 0.03:.1f}" fill="#9AB83A"/><ellipse cx="{ex:.1f}" cy="{hy:.1f}" rx="{s * 0.007:.1f}" ry="{s * 0.026:.1f}" fill="#1A1A10"/>')
        out.append(f'<path d="M {hx - s * 0.015:.1f} {hy + s * 0.04:.1f} l {s * 0.03:.1f} 0 l {-s * 0.015:.1f} {s * 0.02:.1f} Z" fill="#D87A7A"/>')
        for sg in (-1, 1):
            out.append(pline([(hx + sg * s * 0.05, hy + s * 0.055), (hx + sg * s * 0.18, hy + s * 0.045)], "#FFFFFF", 1, seed + sg, 0.7, 1))
        out.append(f'<path d="{blob(P(-0.08, -0.02)[0], P(0, -0.02)[1], s * 0.05, s * 0.03, seed + 7, 0.1, 8)}" fill="{pal[0]}"/>')
        out.append(f'<path d="{blob(P(0.06, -0.02)[0], P(0, -0.02)[1], s * 0.05, s * 0.03, seed + 8, 0.1, 8)}" fill="{pal[0]}"/>')
        return "".join(out)
    return "".join(out)


def phyllo_flakes(seed, box, cols=("#FFF2C8", "#C8862E", "#F6D68A", "#A8661E"), n=40, clip=None):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        L = rnd.uniform(4, 12)
        a = rnd.uniform(-0.6, 0.6)
        out.append(f'<path d="M {x:.1f} {y:.1f} q {L / 2:.1f} {-2 + a * 3:.1f} {L:.1f} {a * L * 0.3:.1f}" stroke="{rnd.choice(cols)}" stroke-width="{rnd.uniform(1, 2.2):.1f}" fill="none" stroke-linecap="round" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
    return "".join(out)


# ================================================================ 1. spanakopita — the round tapsi straight from the oven
class PieGrid:
    """Diamond scoring on a round pie seen in 3/4 view. Plane coords (u, v) -> screen (cx + u, cy + v * k)."""

    def __init__(self, cx, cy, rx, ry, sp, angs=(32, 148)):
        self.cx, self.cy, self.rx, self.k, self.sp = cx, cy, rx, ry / rx, sp
        self.n = [(-math.sin(math.radians(a)), math.cos(math.radians(a))) for a in angs]

    def plane(self, a, b):
        (a1, b1), (a2, b2) = self.n
        det = a1 * b2 - a2 * b1
        u = (a * b2 - b * b1) / det
        v = (a1 * b - a2 * a) / det
        return u, v

    def scr(self, u, v):
        return self.cx + u, self.cy + v * self.k

    def corner(self, i, j):
        return self.scr(*self.plane(i * self.sp, j * self.sp))

    def cell(self, i, j):
        return [self.corner(i, j), self.corner(i + 1, j), self.corner(i + 1, j + 1), self.corner(i, j + 1)]

    def center(self, i, j):
        return self.scr(*self.plane((i + 0.5) * self.sp, (j + 0.5) * self.sp))

    def lines(self):
        out = []
        for f in range(2):
            ux, uy = -self.n[f][1], self.n[f][0]
            nx, ny = self.n[f]
            for i in range(-14, 15):
                ox, oy = nx * i * self.sp, ny * i * self.sp
                b = ox * ux + oy * uy
                c = ox * ox + oy * oy - self.rx * self.rx
                disc = b * b - c
                if disc <= 0:
                    continue
                t0, t1 = -b - math.sqrt(disc), -b + math.sqrt(disc)
                out.append((self.scr(ox + ux * t0, oy + uy * t0), self.scr(ox + ux * t1, oy + uy * t1)))
        return out


def layered_face(D, a_, b_, depth, seed, shade=0.0, filling=("#8ABA5A", "#4A7A2A", "#24461A")):
    """Cut face of spanakopita between top edge a_-b_ and depth below: phyllo leaves on top, spinach and feta, a base crust."""
    rnd = random.Random(seed)
    face = [a_, b_, (b_[0], b_[1] + depth), (a_[0], a_[1] + depth)]
    fd = pd(face)
    out = [f'<path d="{fd}" fill="{filling[1]}"/>']
    cid = D.clip(f'<path d="{fd}"/>')
    inner = []
    for (t0, t1, col) in ((0, 0.34, GOLDEN[1]), (0.84, 1.0, GOLDEN[2])):
        inner.append(f'<path d="{pd([(a_[0], a_[1] + depth * t0), (b_[0], b_[1] + depth * t0), (b_[0], b_[1] + depth * t1), (a_[0], a_[1] + depth * t1)])}" fill="{col}"/>')
    for j in range(4):
        t = 0.05 + j * 0.075
        inner.append(f'<path d="M {a_[0]:.1f} {a_[1] + depth * t:.1f} L {b_[0]:.1f} {b_[1] + depth * t:.1f}" stroke="{[GOLDEN[0], "#FFF4D0", GOLDEN[2], GOLDEN[0]][j]}" stroke-width="0.9" opacity="0.85"/>')
    L = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
    for _ in range(int(L * 0.7)):
        t, v = rnd.random(), rnd.uniform(0.4, 0.8)
        x, y = a_[0] + (b_[0] - a_[0]) * t, a_[1] + (b_[1] - a_[1]) * t + depth * v
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.9, 2.3):.1f}" fill="{rnd.choice(["#FFFFFF", "#FFFDF0", filling[2], filling[0], filling[0]])}" opacity="0.92"/>')
    if shade:
        inner.append(f'<path d="{fd}" fill="#1A1006" opacity="{shade}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(fd, INK, 1.2, seed, 1, 0.55))
    return "".join(out)


def pillow_top(D, quad, seed, light=(-0.5, -0.8)):
    """The flaky, puffed top of one diamond: golden fill, a lit crown, crisp phyllo flakes, a browned rim."""
    rnd = random.Random(seed)
    cx = sum(p[0] for p in quad) / 4
    cy = sum(p[1] for p in quad) / 4
    d = pd(quad)
    base = mix(GOLDEN[1], rnd.choice(["#C8822A", "#F2C870", "#D89A40"]), rnd.uniform(0.1, 0.45))
    out = [f'<path d="{d}" fill="{base}"/>']
    cid = D.clip(f'<path d="{d}"/>')
    w = max(p[0] for p in quad) - min(p[0] for p in quad)
    h = max(p[1] for p in quad) - min(p[1] for p in quad)
    inner = [f'<path d="{blob(cx + light[0] * w * 0.08, cy + light[1] * h * 0.1, w * 0.3, h * 0.28, seed, 0.2, 10)}" fill="{GOLDEN[0]}" opacity="0.75"/>',
             f'<path d="{blob(cx - light[0] * w * 0.22, cy - light[1] * h * 0.26, w * 0.34, h * 0.2, seed + 1, 0.2, 10)}" fill="#A8601A" opacity="0.35"/>']
    for _ in range(int(w * 0.35)):
        x, y = rnd.uniform(cx - w * 0.45, cx + w * 0.45), rnd.uniform(cy - h * 0.45, cy + h * 0.45)
        L = rnd.uniform(3, 9)
        a = rnd.uniform(-0.5, 0.5)
        inner.append(f'<path d="M {x:.1f} {y:.1f} q {L / 2:.1f} {-1.6 + a * 2:.1f} {L:.1f} {a * L * 0.3:.1f}" stroke="{rnd.choice(["#FFF4D0", "#B8701E", "#FFE6A8", "#8A4A10"])}" '
                     f'stroke-width="{rnd.uniform(0.8, 1.7):.1f}" fill="none" stroke-linecap="round" opacity="{rnd.uniform(0.45, 0.9):.2f}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(out)


@design("spanakopita")
def spanakopita():
    D = Doc2("grsp")
    out = [paper(D.nid(), "#F4EAD6", FLECK, 31)]
    out.append(blooms(6, ["#E8D4A8", "#F2E2C0", "#C8D8E0"], 7, (40, 40, 560, 300), (110, 190), (0.08, 0.14)))
    # wooden table
    out.append(wood_planks(D, 318, 600, 32, WOOD, 4))
    out.append(f'<rect y="314" width="600" height="8" fill="#5E3618" opacity="0.5"/>')
    out.append(soft_glow(D, 300, 400, 280, "#FFE6A0", 0.45))
    # a striped kitchen towel lying under the pan, off the corner
    tw = poly_pts([(352, 610), (430, 446), (620, 452), (620, 610)], 18, 33, 0.6)
    out.append(painted(D, tw, ("#FFFFFF", "#F4F0E8", "#B8B4B0"), 33, sdir=(0.3, 1), sk=0.1, angle=-12, n=24, inkw=1.6, hi=0.3))
    cidt = D.clip(f'<path d="{smooth_closed(tw)}"/>')
    out.append(f'<g {cidt}>' + "".join(taper([(470 + k * 34, 440), (450 + k * 34, 530), (424 + k * 34, 620)], 8, 9, AEGEAN[1], 0.85) for k in range(6)) + "</g>")
    # the tapsi
    cx, cy, rx, ry, dep = 300, 416, 206, 110, 24
    out.append(cast(D, cx + 18, cy + ry + dep - 4, rx + 16, 26, strength=0.5, seed=34))
    side = ell_pts(cx, cy, rx, ry, 0, 180, 30) + [(x, y) for x, y in reversed(ell_pts(cx, cy + dep, rx - 6, ry - 3, 0, 180, 30))]
    sd_ = smooth_closed(side)
    out.append(f'<path d="{sd_}" fill="{D.lin([(0, "#E8ECF2"), (0.3, "#A8B0BC"), (0.62, "#DCE0E8"), (1, "#7A828E")], 0, 0, 1, 0)}"/>')
    cid = D.clip(f'<path d="{sd_}"/>')
    out.append(f'<g {cid}>' + strokes(D.nid(), sd_, (cx - rx, cy, cx + rx, cy + ry + dep), ["#FFFFFF", "#8A929E"], 35, n=50, angle=-88, length=(8, 20), width=(1, 3), opacity=(0.15, 0.4)) + "</g>")
    out.append(ink(sd_, "#4A505A", 1.8, 36, 2, 0.7))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, 48))}" fill="#C8CED6"/>')
    out.append(ink(smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, 48)), "#4A505A", 1.8, 37, 1, 0.7))
    out.append(taper(ell_pts(cx, cy, rx - 3, ry - 2, 195, 300, 14), 2.4, 1, "#FFFFFF", 0.8))
    prx, pry = rx - 9, ry - 6
    pie = ell_pts(cx, cy + 1, prx, pry, 0, 360, 48)
    pdd = smooth_closed(pie)
    out.append(f'<path d="{pdd}" fill="{GOLDEN[1]}"/>')
    cid = D.clip(f'<path d="{pdd}"/>')
    G = PieGrid(cx, cy + 1, prx, pry, 52, (18, 108))
    inner = []
    # pick the missing piece: the cell nearest the front-right
    cells = [(i, j) for i in range(-8, 9) for j in range(-8, 9)]
    hole = min(cells, key=lambda c: math.hypot(G.center(*c)[0] - (cx + 78), G.center(*c)[1] - (cy + 44)))
    for (i, j) in cells:
        q = G.cell(i, j)
        mx, my = G.center(i, j)
        if math.hypot((mx - cx) / prx, (my - cy) / pry) > 1.12 or (i, j) == hole:
            continue
        inner.append(pillow_top(D, q, 300 + (i + 9) * 20 + j))
    # browned, crinkled rim where the phyllo meets the pan
    rnd = random.Random(41)
    for a in range(0, 360, 5):
        r0 = 0.94 + rnd.uniform(-0.02, 0.02)
        x0, y0 = cx + prx * r0 * math.cos(math.radians(a)), cy + 1 + pry * r0 * math.sin(math.radians(a))
        x1, y1 = cx + prx * 1.02 * math.cos(math.radians(a + 4)), cy + 1 + pry * 1.02 * math.sin(math.radians(a + 4))
        inner.append(taper([(x0, y0), ((x0 + x1) / 2 + rnd.uniform(-2, 2), (y0 + y1) / 2 - 1), (x1, y1)], 5, 2, rnd.choice(["#A8601A", "#C8822A", "#8A4A12"]), 0.55))
        inner.append(taper([(x0, y0 - 1.5), (x1, y1 - 1.5)], 1.6, 0.6, "#FFE8B0", 0.7))
    for (p0, p1) in G.lines():
        inner.append(taper([p0, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2), p1], 5, 5, "#7A3E10", 0.22))
        inner.append(taper([p0, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2), p1], 1.6, 1.6, "#6A3008", 0.8))
        inner.append(f'<path d="M {p0[0] + 1.2:.1f} {p0[1] + 2:.1f} L {p1[0] + 1.2:.1f} {p1[1] + 2:.1f}" stroke="#FFE8B0" stroke-width="1.1" opacity="0.6"/>')
    # the hole: pan bottom with crumbs, and the cut faces of the neighbours on its far edges
    hq = G.cell(*hole)
    th = 16
    inner.append(f'<path d="{pd(hq)}" fill="#8A929C"/>')
    inner.append(f'<path d="{pd([(x, y + th) for x, y in hq])}" fill="#B8C0CA"/>')
    top_v = min(hq, key=lambda p: p[1])
    ti = hq.index(top_v)
    for a_, b_ in ((hq[(ti - 1) % 4], top_v), (top_v, hq[(ti + 1) % 4])):
        lft, rgt = (a_, b_) if a_[0] < b_[0] else (b_, a_)
        inner.append(layered_face(D, lft, rgt, th, 42 + int(a_[0]), 0.18 if lft == top_v else 0.0))
    for _ in range(12):
        inner.append(f'<circle cx="{rnd.uniform(min(p[0] for p in hq) + 10, max(p[0] for p in hq) - 10):.1f}" cy="{rnd.uniform(top_v[1] + th + 4, max(p[1] for p in hq) + 4):.1f}" r="{rnd.uniform(1, 2.4):.1f}" fill="{rnd.choice([GOLDEN[1], "#4A7A2A", GOLDEN[0]])}"/>')
    inner.append(shade_over(D, pdd, "#2A1206", 0.28, 0, 0, 1, 1, 0.5))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(pdd, "#8A4A12", 1.6, 43, 1, 0.5))
    # the missing piece, on a little plate with a fork
    out.append(plate_34(D, 122, 526, 86, 36, 44, glaze=WHITE, rim=AEGEAN[1]))
    hc = (sum(p[0] for p in hq) / 4, sum(p[1] for p in hq) / 4)
    pq = [((x - hc[0]) * 1.3 + 118, (y - hc[1]) * 1.3 + 504) for x, y in hq]
    dep2 = 21
    out.append(cast(D, 124, 506 + 26, 52, 9, strength=0.4, seed=45))
    bot_v = max(pq, key=lambda p: p[1])
    bi = pq.index(bot_v)
    for a_, b_ in ((pq[(bi - 1) % 4], bot_v), (bot_v, pq[(bi + 1) % 4])):
        lft, rgt = (a_, b_) if a_[0] < b_[0] else (b_, a_)
        out.append(layered_face(D, lft, rgt, dep2, 46 + int(a_[0]), 0.22 if rgt == bot_v else 0.0))
    out.append(pillow_top(D, pq, 47))
    out.append(ink(pd(pq), "#8A4A12", 1.3, 48, 1, 0.6))
    out.append(taper([(150, 556), (196, 532), (226, 516)], 4, 3, "#9AA2AE"))
    for j in range(4):
        out.append(taper([(222 + j * 2.6, 518 + j * 1.4), (242 + j * 2.6, 506 + j * 1.4)], 1.8, 1.4, "#9AA2AE"))
    # steam
    out.append(steam(250, 350, 70, 47, "#FFFFFF", 3, 30, 7, 0.55))
    out.append(steam(390, 366, 50, 48, "#FFFFFF", 2, 26, 6, 0.45))
    # lettering
    out.append(letters(D, 300, 176, "spanakopita", SERIF_IT, 112, "#2E5A22", ["#3E7A2E", "#1E3E14", "#4A8A3A"], 49, max_w=470,
                       shadow="#F2D08A", soff=(0.02, 0.035), angle=-40, hi="#B8E0A0"))
    out.append(ruled(300, 222, "STRAIGHT FROM YIAYIA'S OVEN", "#9A4A16", font=JOS, size=19, ls=4, line_w=30, gap=12))
    return finish_g(D, out, 50)


# ================================================================ 2. kafedaki — Greek coffee from the briki, kaimaki on top
def briki(D, cx, base, h, seed, tilt=0):
    """Copper briki: wide hammered body, pinched waist, flared lip with a pour spout, long brass handle."""
    out = [cast(D, cx + 8, base, h * 0.5, 7, strength=0.4, seed=seed)]
    w0, w1, wl = h * 0.42, h * 0.3, h * 0.36
    top = base - h
    body = [(cx - wl, top), (cx - w1, top + h * 0.2), (cx - w0 * 0.95, base - h * 0.25), (cx - w0, base - 5), (cx - w0 + 6, base),
            (cx + w0 - 6, base), (cx + w0, base - 5), (cx + w0 * 0.95, base - h * 0.25), (cx + w1, top + h * 0.2), (cx + wl + 8, top - 4)]
    # long handle going up-left
    hpts = [(cx - w1 + 2, top + h * 0.26), (cx - w1 - h * 0.42, top - h * 0.02), (cx - w1 - h * 0.74, top - h * 0.2)]
    out.append(taper(hpts, 9, 7, "#6A4214"))
    out.append(taper([(x, y - 2) for x, y in hpts], 3, 2, "#E8B868", 0.7))
    out.append(ink(smooth_open(hpts), INK, 1.4, seed, 1, 0.5))
    out.append(painted(D, body, COPPER, seed, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=40, slen=(10, 30), sw=(1.5, 4), inkw=2, hi=0.5, hik=0.07))
    bd = smooth_closed(body)
    cid = D.clip(f'<path d="{bd}"/>')
    rnd = random.Random(seed)
    ham = "".join(f'<path d="{blob(rnd.uniform(cx - w0, cx + w0), rnd.uniform(top, base), 4, 3, rnd.randint(0, 999), 0.2, 8)}" fill="{rnd.choice(["#FFE0B8", "#8A3E12"])}" opacity="{rnd.uniform(0.15, 0.35):.2f}"/>' for _ in range(40))
    out.append(f'<g {cid}>{ham}<path d="M {cx - w0:.1f} {base - h * 0.32:.1f} L {cx + w0:.1f} {base - h * 0.32:.1f}" stroke="#7A3816" stroke-width="2" opacity="0.4"/></g>')
    out.append(taper([(cx - w0 * 0.6, base - h * 0.6), (cx - w0 * 0.7, base - h * 0.3), (cx - w0 * 0.6, base - 10)], 7, 2, "#FFE8C8", 0.7))
    # rim and the dark coffee inside
    out.append(f'<path d="{smooth_closed(ell_pts(cx + 4, top - 2, wl + 4, 6, 0, 360, 20))}" fill="#5A2A0E"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx + 4, top - 1, wl, 4, 0, 360, 20))}" fill="#C89A62"/>')
    out.append(ink(smooth_closed(ell_pts(cx + 4, top - 2, wl + 4, 6, 0, 360, 20)), INK, 1.6, seed, 1, 0.75))
    return "".join(out)


def loukoumi(D, cx, cy, s, seed, col=("#FFD8E0", "#F4A8BC", "#C86A84")):
    """A cube of loukoumi dusted with icing sugar."""
    top = [(cx - s * 0.6, cy - s * 0.3), (cx + s * 0.1, cy - s * 0.5), (cx + s * 0.7, cy - s * 0.25), (cx, cy - s * 0.05)]
    front = [(cx - s * 0.6, cy - s * 0.3), (cx, cy - s * 0.05), (cx, cy + s * 0.5), (cx - s * 0.58, cy + s * 0.25)]
    right = [(cx, cy - s * 0.05), (cx + s * 0.7, cy - s * 0.25), (cx + s * 0.68, cy + s * 0.25), (cx, cy + s * 0.5)]
    out = [cast(D, cx + 4, cy + s * 0.5, s * 0.8, 4, strength=0.3, seed=seed)]
    for poly, c in ((front, col[1]), (right, col[2]), (top, col[0])):
        out.append(f'<path d="{hg.org_poly(poly, seed, 0.4, 6, 2)}" fill="{c}"/>')
    out.append(specks(seed, (cx - s * 0.6, cy - s * 0.5, cx + s * 0.7, cy + s * 0.5), ["#FFFFFF"], int(s * 3), (0.5, 1.4), (0.6, 1)))
    out.append(ink(hg.org_poly([top[0], top[1], top[2], right[2], right[3], front[3]], seed, 0.4, 6, 2), INK, 1.2, seed, 1, 0.5))
    return "".join(out)


@design("kafedaki")
def kafedaki():
    D = Doc2("grkf")
    # sunlit whitewashed kafeneio wall, a window's light falling across it
    out = [paper(D.nid(), "#F6EEDE", FLECK, 51)]
    out.append(blooms(5, ["#E8CFA0", "#F2DDB4", "#D8B888"], 6, (0, 0, 600, 400), (120, 200), (0.08, 0.14)))
    win = [(318, -10), (612, -10), (612, 250), (520, 352), (360, 352)]
    out.append(f'<path d="{pd(win)}" fill="#FFF2CC" opacity="0.6"/>')
    out.append(f'<path d="M 448 -10 L 452 352 M 330 120 L 612 96" stroke="#E6D2AC" stroke-width="12" opacity="0.6"/>')
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 360 L 0 360 Z", (-40, 0, 600, 360), ["#EADCC0", "#FFFFFF", "#E2CCA4"], 52, n=90, angle=-80,
                       length=(30, 90), width=(4, 10), opacity=(0.08, 0.2)))
    # painted blue table, worn at the edges
    out.append(wood_planks(D, 352, 600, 53, ("#5A86CC", "#2A5AA8", "#143A7A"), 4))
    out.append(f'<rect y="352" width="600" height="250" fill="{D.lin([(0, "#FFFFFF", 0.0), (1, "#0A1A3A", 0.3)])}"/>')
    out.append(specks(54, (0, 360, 600, 600), ["#F2E6CC", "#D8C8A8"], 40, (1, 3), (0.25, 0.55)))
    out.append(f'<rect y="346" width="600" height="10" fill="#0C2C66" opacity="0.5"/>')
    out.append(soft_glow(D, 320, 430, 240, "#FFE8B0", 0.35))
    # briki, glass of water, cup with kaimaki, loukoumi on a saucer
    out.append(water_glass(D, 466, 476, 128, 55, w=74))
    out.append(briki(D, 196, 470, 136, 56))
    out.append(plate_34(D, 452, 540, 64, 20, 64, glaze=WHITE, rim=AEGEAN[1]))
    out.append(loukoumi(D, 436, 532, 22, 58))
    out.append(loukoumi(D, 470, 528, 20, 65, col=("#FFFFFF", "#F2EEE6", "#C8C0B0")))
    out.append(demitasse(D, 316, 548, 120, 57, glaze=WHITE, band=AEGEAN[1]))
    out.append(steam(316, 438, 70, 59, "#FFFFFF", 3, 26, 7, 0.6))
    out.append(steam(204, 318, 46, 60, "#FFFFFF", 2, 20, 6, 0.55))
    # a little spill from the briki
    out.append(f'<path d="{blob(96, 506, 16, 5, 61, 0.2, 10)}" fill="#3A1A0A" opacity="0.45"/>')
    # lettering
    out.append(ruled(300, 92, "ENA METRIO, PARAKALO", "#1F56A8", font=JOS, size=20, ls=4, line_w=32, gap=12))
    out.append(letters(D, 300, 214, "kafedaki", SERIF_IT, 128, "#6A2E10", ["#8A4220", "#4A1E08", "#A0582E"], 62, max_w=430,
                       shadow="#E8C890", soff=(0.02, 0.035), angle=-40, hi="#F2C8A0"))
    out.append(label(300, 258, "one Greek coffee, medium sweet, please", SERIF_IT, 21, "#7A4A28", max_w=420))
    return finish_g(D, out, 63)


# ================================================================ 3. yia mas — two ouzo glasses clink at a seaside taverna
def tentacle(D, pts, w0, w1, seed, pal=("#E89080", "#B8483A", "#6A1E18"), suckers=True, char=True, side=1, speck_cols=("#2A1A10", "#5A2A1A", "#8AA040")):
    """A grilled octopus tentacle along pts: thick tapering body, lit top edge, a row of pale suckers along the
    underside, a few charred grill marks."""
    path = catmull(pts, 8)
    n = len(path)
    out = [taper(path, w0, w1, pal[1])]
    out.append(taper([(x, y - w0 * 0.12) for x, y in path], w0 * 0.45, w1 * 0.3, pal[0], 0.7))
    out.append(taper([(x, y + w0 * 0.2) for x, y in path], w0 * 0.4, w1 * 0.3, pal[2], 0.45))
    rnd = random.Random(seed)
    if suckers:
        for i in range(2, n - 2, 3):
            (x0, y0), (x1, y1) = path[i - 1], path[i + 1]
            L = math.hypot(x1 - x0, y1 - y0) or 1
            nx, ny = -(y1 - y0) / L * side, (x1 - x0) / L * side
            w = (w0 + (w1 - w0) * i / n) / 2
            x, y = path[i][0] + nx * w * 0.75, path[i][1] + ny * w * 0.75
            r = max(1.2, w * 0.32)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#F8D0C0"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.45:.1f}" fill="#C87868"/>')
    if char:
        for i in range(3, n - 4, 6):
            x, y = path[i]
            w = (w0 + (w1 - w0) * i / n) / 2
            out.append(f'<path d="M {x - w * 0.5:.1f} {y - w * 0.7:.1f} l {w * 0.6:.1f} {w * 1.2:.1f}" stroke="#2A0E08" stroke-width="{max(1.5, w * 0.3):.1f}" stroke-linecap="round" opacity="0.7"/>')
    if speck_cols:
        out.append(specks(seed, bbox(path), list(speck_cols), int(n * 0.8), (0.6, 1.5), (0.4, 0.8)))
    out.append(ink(smooth_open(path), INK, 0.9, seed, 1, 0.25))
    return "".join(out)


@design("yia-mas")
def yia_mas():
    D = Doc2("grym")
    out = [sky(D, [(0, "#2A3A7A"), (0.3, "#7A6AA8"), (0.52, "#E89A8A"), (0.62, "#F6C88A")], 64, 360,
               ["#8A7AB8", "#F2B09A", "#5A5A9A"], 60, angle=-2, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 430, 330, 220, "#FFD890", 0.6))
    out.append(f'<circle cx="430" cy="336" r="26" fill="#FFE6A8"/>')
    # islands on the horizon
    il = ridge([(-20, 340), (60, 322), (150, 316), (220, 330), (260, 340)], 65, 6, 3)
    out.append(f'<path d="{smooth_open(il)} L 260 344 L -20 344 Z" fill="#6A5A8A"/>')
    il2 = ridge([(500, 340), (560, 326), (620, 330)], 66, 4, 3)
    out.append(f'<path d="{smooth_open(il2)} L 620 344 L 500 344 Z" fill="#7A6A98"/>')
    out.append(sea(D, 340, 470, [(0, "#E8A8A0"), (0.3, "#8A80B0"), (1, "#2E3E80")], 67, ["#FFD8B0", "#5A5A9A", "#F2B8A8"], 70))
    for k in range(9):
        y = 346 + k * 9
        w = 40 - k * 2
        out.append(taper([(430 - w, y), (430, y + 1), (430 + w, y)], 1, 3.2, "#FFE6A8", 0.8 - k * 0.06))
    # string lights draped across the top
    out.append(string_lights(D, -20, 56, 620, 46, 46, 11, 68))
    # tabletop: blue-and-white checked cloth
    tab = rect_pts(-20, 452, 620, 620, 20, 69, 0.3)
    out.append(cloth(D, tab, AEGEAN[1], 69, cell=22, rot_=0, light=(0, 0, 0, 1), inkw=0))
    out.append(f'<rect y="448" width="600" height="6" fill="#0C2C66" opacity="0.35"/>')
    # meze plate: grilled octopus, olives, a wedge of lemon
    out.append(plate_34(D, 140, 524, 108, 44, 70, glaze=WHITE))
    sp_ = [(58, 530), (90, 508), (128, 498)]
    for i in range(14):
        a = math.radians(-120 + i * 32)
        r = 26 * (1 - i / 16)
        sp_.append((160 + math.cos(a) * r, 522 + math.sin(a) * r))
    out.append(tentacle(D, sp_, 24, 4, 70, pal=("#EEA0A0", "#A8404A", "#5A1424"), side=-1))
    for j, (x, y) in enumerate(((206, 540), (220, 548), (196, 552), (214, 532))):
        out.append(olive(x, y, 7, 20 + j * 30, ("#7A5A6A", "#3E2230", "#1A0A12")))
    wedge = [(70, 540), (104, 534), (98, 556)]
    out.append(painted(D, wedge, LEMON, 72, sdir=(0.5, 0.8), sk=0.15, n=6, inkw=1.2, hi=0.4))
    out.append(pline([(72, 541), (100, 553)], "#FFF8D0", 2, 72, 0.9, 1))
    # the two glasses, clinking
    out.append(f'<g transform="rotate(-9 270 560)">{ouzo_glass(D, 292, 560, 168, 73, fill=0.64)}</g>')
    out.append(f'<g transform="rotate(9 400 560)">{ouzo_glass(D, 378, 560, 168, 74, fill=0.64)}</g>')
    rnd = random.Random(75)
    for _ in range(9):
        a = rnd.uniform(-2.6, -0.5)
        r = rnd.uniform(14, 40)
        x, y = 336 + math.cos(a) * r, 404 + math.sin(a) * r
        out.append(f'<path d="{blob(x, y, rnd.uniform(2, 4), rnd.uniform(2.5, 5), rnd.randint(0, 99), 0.1, 8)}" fill="#FFFFFF" opacity="0.9"/>')
    out.append(sparkle(336, 396, 12, "#FFFFFF", 0.95))
    out.append(sparkle(306, 378, 6, "#FFF2C8", 0.9))
    out.append(sparkle(368, 380, 7, "#FFF2C8", 0.9))
    # lettering
    out.append(letters(D, 300, 196, "Yia mas!", SERIF_IT, 132, "#FFF4E0", ["#FFFFFF", "#F8DCC0", "#FFE8D0"], 76, max_w=440,
                       shadow="#2A1E4A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 244, "TO OUR HEALTH", "#5A2E5A", font=JOS, size=20, ls=5, line_w=36, gap=14))
    return finish_g(D, out, 77, "#2A1E3A", 0.8)


# ================================================================ 4. ftou ftou — the mati charm on a whitewashed wall
def glass_bead(D, cx, cy, r, col, seed):
    out = [f'<path d="{blob(cx, cy, r, r * 0.92, seed, 0.04, 10)}" fill="{col[1]}"/>',
           f'<path d="{blob(cx + r * 0.2, cy + r * 0.2, r * 0.7, r * 0.6, seed + 1, 0.05, 10)}" fill="{col[2]}" opacity="0.5"/>',
           f'<circle cx="{cx - r * 0.3:.1f}" cy="{cy - r * 0.32:.1f}" r="{r * 0.28:.1f}" fill="#FFFFFF" opacity="0.8"/>']
    out.append(ink(blob(cx, cy, r, r * 0.92, seed, 0.04, 10), INK, max(0.8, r * 0.1), seed, 1, 0.4))
    return "".join(out)


def twisted_cord(pts, w, cols, seed):
    """Two-colour twisted cord along pts: a base line plus diagonal twists."""
    path = catmull(pts, 8)
    out = [taper(path, w, w, cols[0])]
    rnd = random.Random(seed)
    for i in range(1, len(path) - 1):
        (x0, y0), (x1, y1) = path[i - 1], path[i + 1]
        L = math.hypot(x1 - x0, y1 - y0) or 1
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        nx, ny = -uy, ux
        x, y = path[i]
        out.append(f'<path d="M {x - nx * w * 0.5 - ux * w * 0.4:.1f} {y - ny * w * 0.5 - uy * w * 0.4:.1f} L {x + nx * w * 0.5 + ux * w * 0.4:.1f} {y + ny * w * 0.5 + uy * w * 0.4:.1f}" '
                   f'stroke="{cols[1]}" stroke-width="{w * 0.38:.1f}" stroke-linecap="round"/>')
    out.append(ink(smooth_open(path), INK, 0.9, seed, 1, 0.4))
    return "".join(out)


@design("ftou-ftou")
def ftou_ftou():
    D = Doc2("grft")
    # whitewashed plaster, cool shadow at the top, sun from the left
    out = [paper(D.nid(), "#FAF6EE", "#7A8AA8", 81)]
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 600 L 0 600 Z", (-40, -10, 600, 600), ["#E8ECF2", "#FFFFFF", "#DCE2EC"], 82, n=160, angle=-70,
                       length=(30, 90), width=(5, 12), opacity=(0.15, 0.35)))
    out.append(blooms(83, ["#C8D4E8", "#D8E0EE", "#B8C8E0"], 7, (0, 0, 600, 600), (100, 200), (0.1, 0.18)))
    # the edge of a blue louvred shutter at the right, bleeding off
    out.append(f'<rect x="530" y="0" width="80" height="600" fill="#3A5A9A" opacity="0.18"/>')
    out.append(painted(D, rect_pts(540, -10, 620, 610, 30, 84, 0.5), AEGEAN, 84, sdir=(1, 0), sk=0.1, angle=-90, n=50, inkw=2, hi=0.3))
    for k in range(30):
        y = -4 + k * 21
        out.append(f'<path d="M 552 {y} L 612 {y + 6} L 612 {y + 14} L 552 {y + 9} Z" fill="{AEGEAN[2]}" opacity="0.45"/>')
        out.append(f'<path d="M 552 {y + 9} L 612 {y + 14}" stroke="{AEGEAN[0]}" stroke-width="1.8" opacity="0.8"/>')
    out.append(f'<rect x="540" y="-10" width="12" height="620" fill="{AEGEAN[1]}"/><rect x="540" y="-10" width="3" height="620" fill="{AEGEAN[0]}" opacity="0.6"/>')
    # a bougainvillea sprig reaching in from the top-left corner
    out.append(taper([(-10, 30), (50, 52), (110, 58), (160, 82), (184, 110)], 6, 2, "#6A4A2A"))
    out.append(taper([(110, 58), (140, 50), (170, 56)], 3, 1.5, "#6A4A2A"))
    for k, (x, y, rx_, ry_) in enumerate(((22, 40, 34, 22), (88, 62, 30, 20), (150, 86, 22, 16), (182, 112, 16, 13), (170, 56, 18, 13))):
        out.append(bougainvillea(D, x, y, rx_, ry_, 96 + k, n=int(rx_ * 0.9)))
    # nail and its shadow
    nx_, ny_ = 280, 78
    out.append(f'<circle cx="{nx_ + 3}" cy="{ny_ + 4}" r="6" fill="#3A4A6A" opacity="0.25"/><circle cx="{nx_}" cy="{ny_}" r="5.5" fill="#6A6A70"/><circle cx="{nx_ - 1.5}" cy="{ny_ - 1.5}" r="2" fill="#D8D8E0"/>')
    # cord loops over the nail, down to the eye
    mx, my, R = 280, 300, 96
    cords = [[(nx_ - 2, ny_ + 2), (nx_ - 10, ny_ + 60), (mx - 16, my - R - 6)], [(nx_ + 2, ny_ + 2), (nx_ + 12, ny_ + 60), (mx + 16, my - R - 6)]]
    out.append(f'<g opacity="0.2" transform="translate(6 8)">' + "".join(taper(catmull(c, 6), 5, 5, "#2A3A5A") for c in cords) + "</g>")
    for i, c in enumerate(cords):
        out.append(twisted_cord(c, 5, ("#FFFFFF", "#1F56A8"), 86 + i))
    # little beads on each cord
    for i, c in enumerate(cords):
        for t in (0.35, 0.62):
            pth = catmull(c, 8)
            x, y = pth[int(t * (len(pth) - 1))]
            out.append(glass_bead(D, x, y, 7.5 if t < 0.5 else 6, (("#FFF0A0", "#E8B830", "#9A6A0A") if t < 0.5 else ("#8AC8F8", "#2A7AD0", "#0E3A7A")), 88 + i))
    # the mati
    out.append(cast(D, mx + 18, my + 22, R * 1.02, R * 0.98, strength=0.22, seed=89))
    out.append(mati(D, mx, my, R, 90))
    # metal bail at the top of the eye
    out.append(f'<rect x="{mx - 9}" y="{my - R - 14}" width="18" height="16" rx="4" fill="#C8A048"/><rect x="{mx - 6}" y="{my - R - 11}" width="5" height="10" rx="2" fill="#FFF2B8" opacity="0.8"/>')
    out.append(ink(f"M {mx - 9} {my - R - 14} h 18 v 16 h -18 Z", INK, 1.2, 91, 1, 0.6))
    # a tiny tassel hanging below
    for j in range(9):
        dx = (j - 4) * 2.4
        out.append(pline([(mx + dx * 0.4, my + R + 20), (mx + dx, my + R + 50 + abs(dx) * 0.4)], ["#1F56A8", "#14387A", "#3A7AD0"][j % 3], 2.2, 92 + j, 0.95, 1))
    out.append(glass_bead(D, mx, my + R + 14, 9, ("#8AC8F8", "#1F56A8", "#0C2C66"), 93))
    out.append(f'<rect x="{mx - 7}" y="{my + R + 19}" width="14" height="7" rx="3" fill="#E8B830"/>')
    out.append(f'<path d="M {mx} {my + R} L {mx} {my + R + 6}" stroke="#C8A048" stroke-width="3"/>')
    # sparkles of glass
    for x, y, s in ((mx - 124, my - 30, 12), (mx + 122, my + 50, 9), (mx - 104, my + 92, 7), (mx + 110, my - 90, 7)):
        out.append(sparkle(x, y, s, "#1F56A8", 0.8))
    # lettering
    out.append(letters(D, 280, 512, "Ftou, ftou!", SERIF_IT, 106, "#14387A", ["#1F56A8", "#0C2462", "#2E6AC8"], 94, max_w=420,
                       shadow="#C8D8F0", soff=(0.02, 0.035), angle=-40, hi="#8AB0F0"))
    out.append(ruled(280, 550, "KEEP THE EVIL EYE AWAY", "#9A2A1E", font=JOS, size=19, ls=4, line_w=28, gap=12))
    return finish_g(D, out, 95, "#3A4A6A", 0.8)


# ================================================================ 5. santorini — blue domes over the caldera at sunset
def bell_tower(D, cx, base, w, h, seed, haze=0.0):
    """Cycladic bell tower (kampanario): stepped white wall with two arched openings holding bells, cross on top."""
    hz = (lambda c: mix(c, "#E8D8D0", haze)) if haze else (lambda c: c)
    out = []
    body = [(cx - w / 2, base), (cx - w / 2, base - h * 0.62), (cx - w * 0.36, base - h * 0.62), (cx - w * 0.36, base - h * 0.86),
            (cx - w * 0.1, base - h * 0.86), (cx, base - h * 0.96), (cx + w * 0.1, base - h * 0.86), (cx + w * 0.36, base - h * 0.86),
            (cx + w * 0.36, base - h * 0.62), (cx + w / 2, base - h * 0.62), (cx + w / 2, base)]
    out.append(painted(D, poly_pts(body, 6, seed, 0.35), tuple(hz(c) for c in WASH_W), seed, sdir=(1, 0.3), sk=0.06, angle=-90, n=24, inkw=1.3, inkop=0.5, hi=0.3))
    # arches
    for (ax, ay, aw, ah) in ((cx - w * 0.3, base - h * 0.6, w * 0.24, h * 0.3), (cx + w * 0.06, base - h * 0.6, w * 0.24, h * 0.3), (cx - w * 0.12, base - h * 0.84, w * 0.24, h * 0.17)):
        d = f"M {ax:.1f} {ay + ah:.1f} L {ax:.1f} {ay + aw / 2:.1f} A {aw / 2:.1f} {aw / 2:.1f} 0 0 1 {ax + aw:.1f} {ay + aw / 2:.1f} L {ax + aw:.1f} {ay + ah:.1f} Z"
        out.append(f'<path d="{d}" fill="{hz("#F2A880")}"/>')
        bx, by = ax + aw / 2, ay + aw * 0.55
        bs = aw * 0.32
        out.append(f'<path d="M {bx - bs:.1f} {by + bs * 1.3:.1f} Q {bx - bs * 0.8:.1f} {by:.1f} {bx:.1f} {by - bs * 0.1:.1f} Q {bx + bs * 0.8:.1f} {by:.1f} {bx + bs:.1f} {by + bs * 1.3:.1f} Z" fill="{hz("#7A5A3A")}"/>')
        out.append(f'<path d="M {bx - bs * 0.5:.1f} {by + bs * 0.4:.1f} Q {bx - bs * 0.45:.1f} {by + bs * 0.1:.1f} {bx - bs * 0.1:.1f} {by:.1f}" stroke="#E8C080" stroke-width="1.4" fill="none"/>')
        out.append(ink(d, INK, 1, seed, 1, 0.4))
    out.append(f'<rect x="{cx - 1.5:.1f}" y="{base - h * 0.96 - 14:.1f}" width="3" height="14" fill="#3A3A40"/><rect x="{cx - 5:.1f}" y="{base - h * 0.96 - 10:.1f}" width="10" height="2.5" fill="#3A3A40"/>')
    return "".join(out)


@design("santorini")
def santorini():
    D = Doc2("grst")
    out = [sky(D, [(0, "#3A5AA0"), (0.32, "#8A8AC0"), (0.6, "#F2A88A"), (0.8, "#FFD49A")], 101, 420, ["#9A9AC8", "#F8C0A0", "#6A7AB8"], 70, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 120, 300, 220, "#FFDC98", 0.75))
    out.append(f'<circle cx="120" cy="298" r="22" fill="#FFF0C0"/>')
    for x, y, w in ((470, 92, 120), (200, 76, 90)):
        out.append(puff_cloud(D, x, y, w, 102 + x, pal=("#FFE2D0", "#E8B0B0", "#A880A8"), op=0.85, rows=1))
    # caldera: Thirasia and the volcano islands on the horizon, the sea far below
    hz = ridge([(-20, 300), (60, 280), (160, 272), (260, 286), (330, 300)], 103, 8, 3)
    out.append(f'<path d="{smooth_open(hz)} L 330 306 L -20 306 Z" fill="#8A6E8E"/>')
    out.append(f'<path d="{smooth_open(ridge([(240, 304), (300, 294), (380, 296), (420, 306)], 104, 4, 3))} L 420 310 L 240 310 Z" fill="#7A607E"/>')
    out.append(sea(D, 304, 600, [(0, "#E8A8A0"), (0.2, "#6A78B0"), (1, "#1E3A80")], 105, ["#FFD0B0", "#3A5A9A", "#8A9AD0"], 90))
    for k in range(10):
        y = 310 + k * 10
        w = 46 - k * 3
        out.append(taper([(120 - w, y), (120, y + 1), (120 + w, y)], 1, 3.4, "#FFE6A8", 0.8 - k * 0.06))
    out.append(caique(D, 96, 404, 46, 106, reflect=True, cabin=True, mast=False))
    out.append(taper([(120, 406), (170, 410), (220, 412)], 2, 0.5, "#FFFFFF", 0.6))
    # the cliff village: cascading white houses on the right and front
    cliff = [(250, 600), (262, 520), (300, 470), (330, 400), (370, 330), (420, 300), (520, 282), (620, 270), (620, 600)]
    out.append(f'<path d="{smooth_closed(cliff)}" fill="#8A5A4A"/>')
    out.append(strokes(D.nid(), smooth_closed(cliff), (240, 260, 620, 600), ["#A86A50", "#6A3A2E", "#C88A6A"], 107, n=50, angle=-70, length=(20, 50), width=(2, 5), opacity=(0.2, 0.45)))
    rnd = random.Random(108)
    houses = []
    for row in range(7):
        y = 312 + row * 40
        x = 360 - row * 16 + rnd.uniform(-6, 6)
        while x < 620:
            w = rnd.uniform(34, 58)
            h = rnd.uniform(26, 40)
            houses.append((x, y + rnd.uniform(-5, 5), w, h, row))
            x += w + rnd.uniform(2, 10)
    for i, (x, y, w, h, row) in enumerate(houses):
        if (x < 300 and y > 470) or (x > 120 and x + w < 150):
            continue
        wall = WASH_W if rnd.random() < 0.82 else (("#FFE0B0", "#F6C880", "#B88A4A") if rnd.random() < 0.5 else ("#FFC8B0", "#E89A80", "#A8604A"))
        vault = rnd.random() < 0.35
        out.append(cube_house(D, x, y, w, h, 120 + i, side=0.2, door=rnd.choice([AEGEAN, TURQ, RED]), windows=1 + (w > 48), light="left",
                              sun_wall=wall, haze=0.06 * (6 - row) / 6, step=False, roof_lip=not vault))
        if vault:   # the barrel-vaulted roofs of the old cave houses
            vd = f"M {x - 1:.1f} {y - h + 1:.1f} A {w / 2 + 1:.1f} {h * 0.32:.1f} 0 0 1 {x + w + 1:.1f} {y - h + 1:.1f} Z"
            out.append(f'<path d="{vd}" fill="{wall[0]}"/><path d="{vd}" fill="{D.lin([(0, "#FFFFFF", 0.0), (1, "#8A90B8", 0.35)], 0, 0, 1, 0)}"/>')
            out.append(ink(vd, INK, 1, 140 + i, 1, 0.45))
    # foreground: the blue-domed church and its bell tower
    out.append(cast(D, 260, 528, 160, 18, strength=0.35, seed=109))
    church = rect_pts(150, 450, 350, 540, 6, 110, 0.4)
    out.append(painted(D, church, WASH_W, 110, sdir=(1, 0.3), sk=0.06, angle=-90, n=30, inkw=1.4, inkop=0.5, hi=0.3))
    out.append(f'<path d="{hg.org_rect(176, 486, 22, 34, 111, 0.4, 8, 2)}" fill="{AEGEAN[1]}"/><path d="{hg.org_rect(306, 486, 22, 34, 112, 0.4, 8, 2)}" fill="{AEGEAN[1]}"/>')
    out.append(blue_dome(D, 250, 452, 86, 113, pal=AEGEAN, light=(-0.8, -0.4)))
    out.append(bell_tower(D, 404, 520, 84, 176, 114))
    # terrace wall and bougainvillea spilling into the corner
    out.append(painted(D, rect_pts(-10, 536, 620, 620, 8, 115, 0.5), WASH_W, 115, sdir=(0.3, 1), sk=0.1, angle=0, n=40, inkw=1.6, hi=0.3))
    out.append(f'<path d="M -10 540 L 620 540" stroke="#FFFFFF" stroke-width="5"/>')
    out.append(bougainvillea(D, 560, 520, 72, 56, 116, n=80))
    out.append(bougainvillea(D, 36, 548, 52, 32, 117, n=40))
    for x, y in ((320, 132), (346, 146), (300, 152)):
        out.append(bird_v(x, y, 7, "#4A3A5A", 0.8))
    out.append(letters(D, 300, 124, "Santorini", SERIF_IT, 120, "#FFF6EA", ["#FFFFFF", "#FFE8D8", "#F8D8C8"], 118, max_w=440,
                       shadow="#3A2A5A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 170, "OIA · AT SUNSET", "#FFE8C0", font=JOS, size=20, ls=6, line_w=40, gap=14))
    return finish_g(D, out, 119, "#2A1E3A", 0.8)


# ================================================================ 6. yiayia — her apron on the hook, flour and all
def cross_stitch_rose(cx, cy, s, col="#C8242A", leaf="#2E7A3A"):
    """A little cross-stitched folk rose (Greek embroidery motif) built from tiny x's on a grid."""
    grid = ["..XXX..", ".XXOXX.", "XXOOOXX", "XOOXOOX", "XXOOOXX", ".XXXXX.", "..LLL..", ".L.L.L.", "L..L..L"]
    out = []
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            col_ = {"X": col, "O": dk(col, 0.25), "L": leaf}[ch]
            x, y = cx + (c - 3) * s, cy + (r - 4) * s
            out.append(f'<path d="M {x - s * 0.4:.1f} {y - s * 0.4:.1f} L {x + s * 0.4:.1f} {y + s * 0.4:.1f} M {x + s * 0.4:.1f} {y - s * 0.4:.1f} L {x - s * 0.4:.1f} {y + s * 0.4:.1f}" stroke="{col_}" stroke-width="{max(1.1, s * 0.32):.1f}" stroke-linecap="round"/>')
    return "".join(out)


def garlic_braid(D, x, top, n, seed):
    out = [taper([(x, top), (x + 3, top + n * 34 + 20)], 6, 4, "#C8B080")]
    for i in range(n):
        y = top + 26 + i * 34
        for sg in (-1, 1):
            gx = x + sg * 14
            bulb = [(gx, y - 18), (gx + 13, y - 2), (gx + 11, y + 12), (gx, y + 16), (gx - 11, y + 12), (gx - 13, y - 2)]
            out.append(painted(D, bulb, ("#FFFFFF", "#F2E8E0", "#C8A8A8"), seed + i * 2 + sg, sdir=(0.6, 0.6), sk=0.18, angle=-90, n=8, inkw=1.2, hi=0.4))
            for dx in (-5, 0, 5):
                out.append(pline([(gx + dx * 0.4, y - 14), (gx + dx, y), (gx + dx * 0.6, y + 13)], "#C89AA8", 1, seed + i, 0.7, 1))
    return "".join(out)


def herb_bunch(D, x, top, seed, col=("#B8C890", "#7A8A50", "#4A5A2A")):
    """A bunch of oregano drying upside down, tied with string."""
    rnd = random.Random(seed)
    out = [pline([(x, top - 30), (x, top)], "#8A6A4A", 1.6, seed, 0.9, 1)]
    for k in range(14):
        a = rnd.uniform(-0.5, 0.5)
        L = rnd.uniform(60, 96)
        tip = (x + math.sin(a) * L, top + math.cos(a) * L)
        out.append(pline([(x, top + 4), ((x + tip[0]) / 2 + rnd.uniform(-4, 4), (top + tip[1]) / 2), tip], "#6A5A3A", 1.3, seed + k, 0.8, 1))
        for j in range(5):
            t = 0.45 + j * 0.12
            px, py = x + (tip[0] - x) * t, top + (tip[1] - top) * t
            out.append(f'<path d="{blob(px, py, 4.5, 3.2, seed + k * 7 + j, 0.2, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(col)}"/>')
        out.append(f'<path d="{blob(tip[0], tip[1], 4, 4, seed + k, 0.2, 8)}" fill="#E8E0C8"/>')
    out.append(f'<rect x="{x - 7}" y="{top - 2}" width="14" height="7" rx="2" fill="#C8A878"/>')
    return "".join(out)


@design("yiayia")
def yiayia():
    D = Doc2("gryy")
    # blue painted plank wall of the kitchen
    out = [paper(D.nid(), "#E8EEF2", FLECK, 121)]
    out.append(wood_planks(D, -10, 610, 122, ("#8AB0D8", "#5A86BC", "#2E5A92"), 7, vertical=True, x0=-10, x1=610))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFF6E0", 0.4), (0.7, "#FFF6E0", 0.05), (1, "#0A1A3A", 0.25)], 0.4, 0.4, 0.8)}"/>')
    # peg rail
    out.append(painted(D, rect_pts(-10, 186, 610, 206, 30, 123, 0.5), WOOD, 123, sdir=(0, 1), sk=0.25, angle=0, n=30, inkw=1.6, hi=0.4))
    out.append(f'<rect x="-10" y="206" width="620" height="6" fill="#0A1A3A" opacity="0.25"/>')
    for x in (300, 96, 506):
        out.append(f'<path d="{blob(x, 196, 7, 7, x, 0.05, 10)}" fill="#7A4A28"/><circle cx="{x - 2}" cy="194" r="2.4" fill="#E8B880"/>')
    # oregano and garlic hanging from the side pegs
    out.append(herb_bunch(D, 96, 214, 124))
    out.append(garlic_braid(D, 506, 206, 4, 125))
    # the apron
    neck = [(300, 196), (262, 214), (252, 250)]
    out.append(taper([(300, 194), (270, 206), (256, 236), (256, 252)], 5, 5, "#E8DCC8"))
    out.append(taper([(300, 194), (330, 206), (344, 236), (344, 252)], 5, 5, "#E8DCC8"))
    # waist ties hanging down each side (behind the skirt)
    for sg in (-1, 1):
        for k, (dx, L) in enumerate(((0, 168), (12, 138))):
            tie = [(300 + sg * 78, 342), (300 + sg * (100 + dx), 372), (300 + sg * (112 + dx), 420), (300 + sg * (118 + dx * 1.4), 342 + L)]
            out.append(taper(tie, 12, 11, "#E8DCC4" if k else "#FBF4E6"))
            out.append(pline(tie, INK, 1.1, 131 + sg + k, 0.45, 1))
            ex, ey = tie[-1]
            out.append(pline([(ex - 6, ey - 6), (ex + 6, ey - 6)], "#C8242A", 2.2, 140 + k, 0.85, 1))
    bib = [(250, 250), (350, 250), (356, 330), (382, 338), (414, 548), (300, 560), (186, 548), (218, 338), (244, 330)]
    out.append(cast(D, 312, 420, 130, 170, strength=0.22, seed=126))
    out.append(painted(D, bib, ("#FFFBF0", "#F0E6D2", "#C0B298"), 127, sdir=(0.7, 0.4), sk=0.1, angle=-88, n=70, inkw=2, hi=0.35))
    bd = smooth_closed(bib)
    cid = D.clip(f'<path d="{bd}"/>')
    inner = []
    # soft vertical folds of the linen
    for x0 in (236, 272, 320, 362, 392):
        inner.append(taper([(x0, 344), (x0 + 4, 450), (x0 + (x0 - 300) * 0.15, 556)], 8, 14, "#8A7A60", 0.12))
        inner.append(taper([(x0 - 6, 344), (x0 - 3, 450), (x0 - 6 + (x0 - 300) * 0.15, 556)], 3, 5, "#FFFFFF", 0.5))
    # red cross-stitch border near the hem and a band on the bib
    for k in range(8):
        inner.append(cross_stitch_rose(208 + k * 27, 520, 2.6))
    inner.append(f'<path d="M 180 498 L 420 498" stroke="#C8242A" stroke-width="2.4" stroke-dasharray="5 3"/>')
    inner.append(f'<path d="M 180 542 L 420 542" stroke="#C8242A" stroke-width="2.4" stroke-dasharray="5 3"/>')
    inner.append(cross_stitch_rose(300, 286, 3.2))
    # a floury handprint
    rnd = random.Random(128)
    hx_, hy_ = 384, 404
    palm_ = blob_pts(hx_, hy_ + 8, 13, 15, 128, 0.06, 14, 15)
    hand = [f'<path d="{smooth_closed(palm_)}"/>']
    for k, (fa, fl) in enumerate(((-38, 24), (-14, 28), (8, 27), (30, 22))):
        a_ = math.radians(fa - 90 + 15)
        x0, y0 = hx_ + math.cos(a_) * 10, hy_ + math.sin(a_) * 10
        x1, y1 = hx_ + math.cos(a_) * fl, hy_ + math.sin(a_) * fl
        hand.append(f'<path d="M {x0:.1f} {y0:.1f} L {x1:.1f} {y1:.1f}" stroke-width="8" stroke-linecap="round"/>')
    hand.append(f'<path d="M {hx_ - 8:.1f} {hy_ + 12:.1f} L {hx_ - 24:.1f} {hy_ + 2:.1f}" stroke-width="8.5" stroke-linecap="round"/>')
    inner.append(f'<g fill="#FFFFFF" stroke="#FFFFFF" opacity="0.88">{"".join(hand)}</g>')
    inner.append(specks(129, (350, 370, 420, 440), ["#FFFFFF"], 40, (0.6, 1.8), (0.5, 0.95)))
    inner.append(shade_over(D, bd, "#3A2A1A", 0.2, 0, 0, 1, 0, 0.5))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(bd, INK, 2, 130, 2, 0.6))
    out.append(f'<path d="M 218 338 Q 300 350 382 338" stroke="#C8242A" stroke-width="3" fill="none" stroke-dasharray="6 3" opacity="0.9"/>')
    # front pocket with a wooden spoon and a sprig of dill
    out.append(taper([(278, 448), (292, 360), (300, 326)], 7, 5, "#C8925A"))
    out.append(f'<path d="{blob(302, 316, 13, 19, 132, 0.05, 12, 12)}" fill="#D8A26A"/>' + ink(blob(302, 316, 13, 19, 132, 0.05, 12, 12), INK, 1.4, 132, 1, 0.6))
    out.append(f'<path d="{blob(298, 310, 6, 10, 133, 0.05, 10, 12)}" fill="#B07A44" opacity="0.6"/>')
    for j in range(6):
        t = j / 5
        bx, by = 332 + t * 14, 432 - t * 70
        for sg in (-1, 1):
            out.append(pline([(bx, by), (bx + sg * 9, by - 9)], "#4A8A3A", 1.5, j * 3 + sg, 0.9, 1))
    out.append(pline([(330, 440), (338, 400), (346, 362)], "#5A8A3A", 2, 134, 0.9, 1))
    pk = [(244, 420), (360, 420), (356, 486), (248, 486)]
    out.append(painted(D, poly_pts(pk, 16, 135, 0.5), ("#FFFFFF", "#F2EADA", "#C0B49C"), 135, sdir=(0.6, 0.6), sk=0.12, angle=-88, n=20, inkw=1.8, hi=0.3))
    out.append(f'<path d="M 248 428 L 356 428" stroke="#C8242A" stroke-width="2.2" stroke-dasharray="4 3"/>')
    out.append(gr_caps(302, 468, "ΓΙΑΓΙΑ", CINZEL, 26, "#C8242A", ls=3, max_w=96))
    # lettering
    out.append(letters(D, 300, 132, "Yiayia", SERIF_IT, 128, "#FFF6EA", ["#FFFFFF", "#F2E8D8", "#FFF0E0"], 136, max_w=400,
                       shadow="#1E3E72", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(label(300, 172, "HER KITCHEN, HER RULES", JOS, 20, "#FFE8B8", ls=4))
    return finish_g(D, out, 137)


# ================================================================ 7. horiatiki — the village salad, feta slab on top
def tomato_wedge(D, cx, cy, r, ang, seed):
    """A tomato wedge seen from the side: red skin arc, pale flesh, seed pockets with yellow seeds."""
    a = math.radians(ang)
    pts = [(cx + math.cos(a + t) * r * (1.0 if abs(t) < 0.9 else 0.92), cy + math.sin(a + t) * r * 0.62) for t in [i * 0.2 - 1.0 for i in range(11)]]
    pts.append((cx - math.cos(a) * r * 0.2, cy - math.sin(a) * r * 0.12))
    out = [painted(D, pts, TOMATO, seed, sdir=(0.5, 0.8), sk=0.18, angle=ang + 90, n=8, inkw=1.1, inkop=0.55, hi=0.45)]
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    fx, fy = cx + math.cos(a) * r * 0.25, cy + math.sin(a) * r * 0.15
    inner = [f'<path d="{blob(fx, fy, r * 0.62, r * 0.3, seed, 0.1, 10, ang)}" fill="#F87A62"/>']
    for k in (-1, 1):
        sx, sy = fx + math.cos(a + k * 1.2) * r * 0.28, fy + math.sin(a + k * 1.2) * r * 0.16
        inner.append(f'<path d="{blob(sx, sy, r * 0.22, r * 0.12, seed + k, 0.15, 8, ang)}" fill="#FFB060" opacity="0.9"/>')
        for j in range(3):
            inner.append(f'<circle cx="{sx + (j - 1) * r * 0.08:.1f}" cy="{sy:.1f}" r="{max(0.8, r * 0.04):.1f}" fill="#FFF0A0"/>')
    inner.append(f'<path d="{blob(fx - r * 0.1, fy - r * 0.08, r * 0.2, r * 0.07, seed + 5, 0.2, 8, ang)}" fill="#FFFFFF" opacity="0.5"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(out)


def cucumber(D, cx, cy, r, ang, seed, half=True):
    """A cucumber half-moon: dark green rind arc, pale juicy flesh, seed ring."""
    out = []
    if half:
        pts = [(cx + r * math.cos(math.radians(t)), cy + r * 0.55 * math.sin(math.radians(t))) for t in range(0, 181, 20)]
        pts = rot(pts, cx, cy, ang)
    else:
        pts = ell_pts(cx, cy, r, r * 0.55, 0, 360, 20)
        pts = rot(pts, cx, cy, ang)
    out.append(f'<path d="{smooth_closed(pts)}" fill="#2E6A2A"/>')
    inner = [(cx + (r - 3) * math.cos(math.radians(t)), cy + (r - 3) * 0.55 * math.sin(math.radians(t))) for t in (range(4, 177, 16) if half else range(0, 360, 18))]
    inner = rot(inner, cx, cy, ang)
    out.append(f'<path d="{smooth_closed(inner)}" fill="#E8F2C0"/>')
    seeds = rot([(cx + r * 0.45 * math.cos(math.radians(t)), cy + r * 0.25 * math.sin(math.radians(t))) for t in (range(25, 160, 30) if half else range(0, 360, 40))], cx, cy, ang)
    for x, y in seeds:
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{max(1, r * 0.08):.1f}" ry="{max(0.7, r * 0.05):.1f}" fill="#C8D890"/>')
    out.append(ink(smooth_closed(pts), "#1E4A1A", 1, seed, 1, 0.5))
    return "".join(out)


def ring(D, cx, cy, r, ang, col, w, seed, ry=0.45):
    pts = rot(ell_pts(cx, cy, r, r * ry, 0, 360, 18), cx, cy, ang)
    return ink(smooth_closed(jitter(pts, seed, 0.6)), col, w, seed, 1, 0.95) + ink(smooth_closed(jitter(pts, seed + 1, 0.4)), "#FFFFFF", w * 0.3, seed, 1, 0.45)


def kalamata(cx, cy, r, ang):
    return olive(cx, cy, r, ang, ("#9A6A8A", "#4A2240", "#1E0A18"))


def feta_slab(D, cx, cy, w, h, t, seed, ang=-6):
    """A thick slab of feta on top: crumbly white top face with tiny holes, cut side faces, oregano and an oil gloss."""
    rnd = random.Random(seed)
    top = rot([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2 - 4), (cx + w / 2 + 4, cy + h / 2), (cx - w / 2 + 4, cy + h / 2 + 4)], cx, cy, ang)
    front = [top[3], top[2], (top[2][0], top[2][1] + t), (top[3][0], top[3][1] + t)]
    side = [top[2], top[1], (top[1][0], top[1][1] + t), (top[2][0], top[2][1] + t)]
    out = [cast(D, cx + 8, cy + h / 2 + t, w * 0.6, 8, strength=0.35, seed=seed)]
    for poly, col in ((front, "#ECE6D2"), (side, "#D8D0B8")):
        d = hg.org_poly(poly, seed, 0.8, 6, 1.5)
        out.append(f'<path d="{d}" fill="{col}"/>')
        out.append(specks(seed + 1, bbox(poly), ["#C8BC9A", "#FFFFFF"], int(w * 0.3), (0.5, 1.5), (0.4, 0.8)))
        out.append(ink(d, "#A89870", 1.1, seed, 1, 0.6))
    d = hg.org_poly(top, seed + 2, 1.2, 8, 3)
    out.append(f'<path d="{d}" fill="#FFFEF8"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = [f'<path d="{blob(cx + w * 0.12, cy + h * 0.1, w * 0.3, h * 0.25, seed, 0.3, 10, ang)}" fill="#E8E0C4" opacity="0.6"/>']
    for _ in range(int(w * 0.5)):
        x, y = rnd.uniform(cx - w / 2, cx + w / 2), rnd.uniform(cy - h / 2, cy + h / 2)
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 1.8):.1f}" fill="#D8CCA8" opacity="0.6"/>')
    # olive oil pooled in a glossy streak
    inner.append(taper([(cx - w * 0.4, cy - h * 0.1), (cx - w * 0.05, cy + h * 0.08), (cx + w * 0.35, cy - h * 0.05)], h * 0.22, h * 0.1, "#E8D060", 0.45))
    inner.append(taper([(cx - w * 0.3, cy - h * 0.12), (cx, cy + h * 0.02)], 2.2, 1, "#FFFFFF", 0.8))
    for _ in range(int(w * 0.5)):
        x, y = rnd.uniform(cx - w / 2, cx + w / 2), rnd.uniform(cy - h / 2, cy + h / 2)
        inner.append(f'<path d="{blob(x, y, rnd.uniform(1, 2.4), rnd.uniform(0.8, 1.6), rnd.randint(0, 999), 0.3, 6, rnd.uniform(0, 180))}" fill="{rnd.choice(["#5A6A2A", "#7A8A3A", "#3E4A1A"])}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, "#A89870", 1.3, seed + 3, 1, 0.6))
    return "".join(out)


def bowl_side(D, cx, cy, rx, ry, depth, seed, glaze=WHITE, band=AEGEAN):
    """A wide ceramic bowl in 3/4 view, rim ellipse at cy. Returns (inside, front): draw `inside`, then whatever sits
    in the bowl, then `front` (the outer wall between the rim's near arc and the bowl's belly)."""
    inside = [f'<path d="{smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, 40))}" fill="{glaze[1]}"/>',
              f'<path d="{smooth_closed(ell_pts(cx, cy + 4, rx - 6, ry - 4, 0, 360, 40))}" fill="{dk(glaze[1], 0.12)}"/>',
              shade_over(D, smooth_closed(ell_pts(cx, cy + 4, rx - 6, ry - 4, 0, 360, 40)), "#2A3A5A", 0.25, 0, 0, 1, 1, 0.3)]
    pts = ell_pts(cx, cy, rx, ry, 0, 180, 30) + ell_pts(cx, cy - 2, rx * 0.99, ry + depth, 180, 0, 30)[1:-1]
    front = [painted(D, pts, glaze, seed, sdir=(0.8, 0.6), sk=0.14, angle=-6, n=40, inkw=2, hi=0.45, hik=0.06)]
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    if band:
        b1 = ell_pts(cx, cy + depth * 0.3, rx * 0.985, ry + depth * 0.32, 0, 180, 30)
        b2 = ell_pts(cx, cy + depth * 0.5, rx * 0.97, ry + depth * 0.5, 0, 180, 30)
        front.append(f'<g {cid}>' + taper(b1, 7, 7, band[1], 0.92) + taper(b2, 2.6, 2.6, band[1], 0.85) +
                     taper(ell_pts(cx, cy + depth * 0.62, rx * 0.95, ry + depth * 0.62, 0, 180, 30), 2.6, 2.6, band[1], 0.85) + "</g>")
    front.append(f'<path d="{smooth_open(ell_pts(cx, cy, rx, ry, 0, 180, 30))}" fill="none" stroke="#FFFFFF" stroke-width="4"/>')
    front.append(ink(smooth_open(ell_pts(cx, cy, rx, ry, 0, 180, 30)), INK, 1.6, seed, 1, 0.7))
    front.append(ink(smooth_open(ell_pts(cx, cy, rx, ry, 180, 360, 30)), INK, 1.4, seed + 1, 1, 0.55))
    return "".join(inside), "".join(front)


def bread_slice(D, cx, cy, w, seed, rot_=0):
    """A slice of village bread lying flat-ish: thick brown crust, open crumb with holes, sesame on the crust."""
    rnd = random.Random(seed)
    outer = [(cx - w * 0.5, cy + w * 0.12), (cx - w * 0.46, cy - w * 0.12), (cx - w * 0.28, cy - w * 0.26), (cx, cy - w * 0.3), (cx + w * 0.3, cy - w * 0.25),
             (cx + w * 0.48, cy - w * 0.1), (cx + w * 0.5, cy + w * 0.12), (cx + w * 0.3, cy + w * 0.2), (cx - w * 0.3, cy + w * 0.2)]
    outer = rot(outer, cx, cy, rot_)
    out = [cast(D, cx + 6, cy + w * 0.2, w * 0.55, 8, strength=0.35, seed=seed)]
    out.append(painted(D, outer, ("#D8904A", "#9A5A22", "#5A2E0E"), seed, sdir=(0.5, 0.8), sk=0.15, n=12, inkw=1.6, hi=0.35))
    crumb = rot([(x * 0.84 + cx * 0.16, y * 0.8 + cy * 0.2 + 2) for x, y in rot(outer, cx, cy, -rot_)], cx, cy, rot_)
    out.append(f'<path d="{smooth_closed(crumb)}" fill="#FFF0D4"/>')
    cid = D.clip(f'<path d="{smooth_closed(crumb)}"/>')
    holes = "".join(f'<path d="{blob(rnd.uniform(cx - w * 0.38, cx + w * 0.38), rnd.uniform(cy - w * 0.2, cy + w * 0.15), rnd.uniform(1.5, 4.5), rnd.uniform(1, 3), rnd.randint(0, 999), 0.3, 8)}" fill="#E2C89A"/>' for _ in range(int(w * 0.4)))
    out.append(f'<g {cid}>{holes}' + shade_over(D, smooth_closed(crumb), "#8A5A22", 0.25, 0, 0, 1, 1, 0.4) + "</g>")
    for _ in range(14):
        a = rnd.uniform(3.4, 6.0)
        x, y = cx + math.cos(a) * w * 0.46, cy + math.sin(a) * w * 0.27 - 2
        out.append(f'<path d="{blob(x, y, 2.2, 1.2, rnd.randint(0, 999), 0.1, 6, rnd.uniform(0, 180))}" fill="#FFF4D8"/>')
    return "".join(out)


@design("horiatiki")
def horiatiki():
    D = Doc2("grho")
    # dappled shade under a vine pergola
    out = [sky(D, [(0, "#E8D8A0"), (0.6, "#F2E6C0"), (1, "#F6EED6")], 141, 600, ["#E0CC90", "#F8F0D0", "#D8C080"], 80, angle=-30, sop=(0.06, 0.16))]
    out.append(blooms(142, ["#C8D890", "#E8D8A0", "#B8C880"], 8, (0, 0, 600, 360), (80, 160), (0.1, 0.18)))
    rnd = random.Random(143)
    for x in range(-20, 640, 54):
        y = rnd.uniform(-10, 30)
        out.append(vine_leaf(D, x + rnd.uniform(-10, 10), y, rnd.uniform(26, 36), rnd.uniform(0, 360), 144 + x))
    out.append(taper([(-10, 36), (150, 22), (300, 40), (460, 20), (610, 34)], 5, 3, "#6A4A2A", 0.8))
    for k in range(3):
        gx = 110 + k * 190 + rnd.uniform(-20, 20)
        for j in range(9):
            out.append(f'<circle cx="{gx + rnd.uniform(-8, 8):.1f}" cy="{40 + j * 5 + rnd.uniform(-2, 2):.1f}" r="{5.5 - j * 0.35:.1f}" fill="{rnd.choice(["#9AB050", "#B8C860", "#7A9A3A"])}"/>')
    # paper tablecloth over the table
    tab = rect_pts(-20, 330, 620, 620, 20, 145, 0.4)
    out.append(painted(D, tab, ("#FFFFFF", "#F8F6F0", "#C8CCD8"), 145, sdir=(0, 1), sk=0.05, angle=-4, n=60, inkw=0, hi=0))
    out.append(f'<rect y="330" width="600" height="270" fill="{D.lin([(0, "#3A5A9A", 0.18), (0.3, "#FFFFFF", 0), (1, "#3A5A9A", 0.12)])}"/>')
    for k in range(-8, 12):   # leaf-shadow dapples
        out.append(f'<path d="{blob(rnd.uniform(0, 600), rnd.uniform(340, 600), rnd.uniform(14, 40), rnd.uniform(6, 14), rnd.randint(0, 999), 0.3, 10)}" fill="#7A8A5A" opacity="0.12"/>')
    out.append(f'<path d="M -10 331 L 610 331" stroke="#B8BCC8" stroke-width="3"/>')
    # bread on the side and a cruet of olive oil
    out.append(cast(D, 498, 404, 70, 10, strength=0.35, seed=146))
    cr = [(484, 404), (478, 360), (486, 322), (494, 300), (496, 280), (504, 280), (506, 300), (514, 322), (522, 360), (516, 404)]
    out.append(f'<path d="{smooth_closed(cr)}" fill="#E8F0E0" opacity="0.6"/>')
    oil = [(486, 400), (481, 362), (488, 330), (512, 330), (519, 362), (514, 400)]
    out.append(f'<path d="{smooth_closed(oil)}" fill="{D.lin([(0, "#E8D058"), (1, "#B89A1A")], 0, 0, 1, 0)}" opacity="0.92"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(500, 330, 14, 3, 0, 360, 12))}" fill="#F6E27A"/>')
    out.append(ink(smooth_closed(cr), "#6A7A60", 1.4, 147, 1, 0.75))
    out.append(taper([(489, 380), (486, 342), (492, 314)], 3, 1, "#FFFFFF", 0.85))
    out.append(f'<rect x="494" y="270" width="12" height="12" rx="3" fill="#8A6A44"/>')
    # the bowl and the salad heap
    cx, cy, rx, ry = 290, 452, 188, 60
    out.append(cast(D, cx + 18, cy + ry + 56, rx * 0.78, 18, strength=0.45, seed=148))
    inside, front = bowl_side(D, cx, cy, rx, ry, 66, 149)
    out.append(inside)
    items = []
    kinds = ["tom", "tom", "tom", "cuc", "cuc", "cuc", "on", "pep", "pep", "ol", "ol"]
    for i in range(170):          # a full layer filling the bowl
        a = rnd.uniform(0, 2 * math.pi)
        r = math.sqrt(rnd.random())
        items.append((cy + math.sin(a) * (ry - 8) * r - 6, cx + math.cos(a) * (rx - 26) * r, rnd.choice(kinds)))
    for i in range(70):           # the heap rising in the middle
        a = rnd.uniform(0, 2 * math.pi)
        r = math.sqrt(rnd.random())
        items.append((cy + math.sin(a) * (ry - 20) * r - (1 - r * r) * 64 - 10, cx + math.cos(a) * (rx - 70) * r, rnd.choice(kinds)))
    slab_y = cy - 66

    def draw(it, i):
        y, x, kind = it
        s_ = 150 + i * 3
        if kind == "tom":
            return tomato_wedge(D, x, y, rnd.uniform(24, 32), rnd.uniform(-40, 220), s_)
        if kind == "cuc":
            return cucumber(D, x, y, rnd.uniform(15, 20), rnd.uniform(-30, 30), s_, half=rnd.random() < 0.7)
        if kind == "on":
            return ring(D, x, y, rnd.uniform(14, 22), rnd.uniform(-30, 30), "#A04A9A", 3.2, s_)
        if kind == "pep":
            return ring(D, x, y, rnd.uniform(14, 18), rnd.uniform(-30, 30), "#5AA03A", 3.6, s_, 0.5)
        return kalamata(x, y, rnd.uniform(7, 9), rnd.uniform(0, 180))
    items.sort()
    for i, it in enumerate(items):
        out.append(draw(it, i))
    out.append(feta_slab(D, cx + 6, slab_y, 136, 56, 24, 160, ang=-5))
    for k, (x, y, kind) in enumerate(((cx - 66, slab_y + 50, "tom"), (cx + 70, slab_y + 46, "cuc"), (cx - 10, slab_y + 58, "ol"), (cx + 30, slab_y + 56, "tom"), (cx - 50, slab_y + 40, "on"))):
        out.append(draw((y, x, kind), 400 + k))
    out.append(front)
    # fork and a slice of village bread at the front
    out.append(taper([(510, 586), (548, 520), (566, 490)], 6, 4, "#9AA2AE"))
    for j in range(4):
        out.append(taper([(561 + j * 3.4, 494 + j * 1.6), (578 + j * 3.4, 468 + j * 1.6)], 2.4, 1.6, "#9AA2AE"))
    out.append(bread_slice(D, 102, 556, 120, 161, rot_=-8))
    # lettering
    out.append(letters(D, 300, 170, "horiatiki", SERIF_IT, 128, "#B8281E", ["#D8382E", "#8A140C", "#E85A40"], 165, max_w=430,
                       shadow="#FFF6E0", soff=(0.02, 0.035), angle=-40, hi="#FFB0A0"))
    out.append(ruled(300, 214, "THE FETA GOES ON TOP", "#2E5A22", font=JOS, size=20, ls=5, line_w=34, gap=14))
    return finish_g(D, out, 166)


# ================================================================ 8. souvlaki — ena me ola, one with everything
def pita_wrap(D, cx, base, w, h, seed, tilt=0):
    """Souvlaki pita wrapped in paper: grilled pita folded round, pork, tomato, onion, tzatziki and fries up top,
    a white paper cone with a blue stripe below."""
    rnd = random.Random(seed)
    out = [f'<g transform="rotate({tilt} {cx} {base})">']
    top = base - h
    # fillings rising out of the pita
    fries = []
    for k in range(7):
        fx = cx + (k - 3) * w * 0.12 + rnd.uniform(-4, 4)
        fh = rnd.uniform(0.12, 0.2) * h
        ang = (k - 3) * 7 + rnd.uniform(-6, 6)
        p = rot(rect_pts(fx - 6.5, top - fh, fx + 6.5, top + h * 0.12, 6, seed + k, 0.5), fx, top + h * 0.1, ang)
        fries.append(painted(D, p, ("#FFF2B0", "#F0C454", "#B07A22"), seed + k, sdir=(1, 0.3), sk=0.25, angle=-90, n=5, inkw=1.2, inkop=0.6, hi=0.45)
                     + f'<path d="{blob(*rot([(fx, top - fh + 3)], fx, top + h * 0.1, ang)[0], 6, 3, seed + k, 0.2, 8)}" fill="#C8862A" opacity="0.6"/>')
    out.append("".join(fries[::2]))
    # pork pieces
    for k in range(6):
        mx, my = cx + (k - 2.5) * w * 0.13 + rnd.uniform(-4, 4), top + h * 0.06 + rnd.uniform(-6, 6)
        out.append(painted(D, blob_pts(mx, my, w * 0.09, w * 0.07, seed + 20 + k, 0.15, 10), ("#C8804A", "#8A4A22", "#4A2210"), seed + 20 + k, sk=0.25, n=6, inkw=1, hi=0.3))
        out.append(f'<path d="M {mx - 4:.1f} {my - 3:.1f} l 7 -2" stroke="#3A1A08" stroke-width="2" stroke-linecap="round" opacity="0.6"/>')
    out.append("".join(fries[1::2]))
    # tomato slices, onion, parsley, tzatziki
    for k, dx in enumerate((-0.34, -0.1, 0.16, 0.36)):
        tx, ty = cx + dx * w, top + h * (0.1 + 0.02 * (k % 2))
        out.append(f'<path d="{blob(tx, ty, w * 0.12, w * 0.07, seed + 30 + k, 0.1, 12, 10 - k * 12)}" fill="#E23A26"/>')
        out.append(f'<path d="{blob(tx, ty - 1, w * 0.08, w * 0.04, seed + 33 + k, 0.1, 10, 10 - k * 12)}" fill="#FF8A6A"/>')
        out.append(f'<circle cx="{tx - 4:.1f}" cy="{ty - 1:.1f}" r="1.6" fill="#FFF0A0"/><circle cx="{tx + 4:.1f}" cy="{ty:.1f}" r="1.6" fill="#FFF0A0"/>')
    for k in range(5):
        px = cx + (k - 2) * w * 0.17
        out.append(f'<path d="{blob(px, top + h * 0.06, 5, 3.5, seed + 90 + k, 0.3, 8)}" fill="#3E8A2E"/><path d="{blob(px + 4, top + h * 0.05, 4, 3, seed + 95 + k, 0.3, 8)}" fill="#5AAA3A"/>')
    for k in range(3):
        out.append(pline([(cx - w * 0.3 + k * w * 0.22, top + h * 0.1), (cx - w * 0.2 + k * w * 0.22, top + h * 0.04), (cx - w * 0.1 + k * w * 0.22, top + h * 0.1)], "#B86AB0", 3, seed + k, 0.9, 1))
    tz = blob_pts(cx + w * 0.02, top + h * 0.08, w * 0.3, w * 0.09, seed + 40, 0.18, 14)
    out.append(painted(D, tz, ("#FFFFFF", "#F4F6EE", "#C8CCC0"), seed + 40, sdir=(0.4, 1), sk=0.15, n=8, inkw=1.2, hi=0.4))
    out.append(specks(seed + 41, (cx - w * 0.2, top + h * 0.03, cx + w * 0.25, top + h * 0.12), ["#4A8A3A", "#2E6A2A"], 12, (1, 1.8), (0.7, 1)))
    out.append(taper([(cx + w * 0.22, top + h * 0.1), (cx + w * 0.24, top + h * 0.2), (cx + w * 0.22, top + h * 0.28)], 7, 4, "#FFFFFF", 0.95))
    # the pita, folded round (back lip and front lip)
    pita = [(cx - w * 0.5, top + h * 0.08), (cx - w * 0.3, top + h * 0.16), (cx, top + h * 0.2), (cx + w * 0.3, top + h * 0.16), (cx + w * 0.5, top + h * 0.08),
            (cx + w * 0.47, top + h * 0.66), (cx + w * 0.2, top + h * 0.72), (cx - w * 0.2, top + h * 0.72), (cx - w * 0.47, top + h * 0.66)]
    out.append(painted(D, pita, ("#FCE2A8", "#E8B466", "#A8702A"), seed + 50, sdir=(0.7, 0.5), sk=0.2, angle=-20, n=26, inkw=1.8, hi=0.45))
    pd_ = smooth_closed(pita)
    cid = D.clip(f'<path d="{pd_}"/>')
    marks = []
    for k in range(7):
        x0 = cx - w * 0.42 + k * w * 0.13
        marks.append(f'<path d="{blob(x0, top + h * (0.3 + 0.05 * (k % 2)), w * 0.045, w * 0.02, seed + 60 + k, 0.2, 8, 25)}" fill="#7A3E14" opacity="0.7"/>')
    marks.append(specks(seed + 61, (cx - w * 0.5, top + h * 0.1, cx + w * 0.5, top + h * 0.5), ["#C8822A", "#8A4A12", "#FFF0C0"], 30, (0.8, 1.8), (0.4, 0.8)))
    out.append(f'<g {cid}>{"".join(marks)}</g>')
    # paper cone with the stripe
    pap = [(cx - w * 0.54, top + h * 0.6), (cx - w * 0.22, top + h * 0.56), (cx - w * 0.02, top + h * 0.62), (cx + w * 0.54, top + h * 0.54),
           (cx + w * 0.34, base - 6), (cx, base + 4), (cx - w * 0.34, base - 6)]
    out.append(painted(D, pap, ("#FFFFFF", "#F6F2EA", "#C0BCB4"), seed + 70, sdir=(0.8, 0.4), sk=0.14, angle=-80, n=30, inkw=1.8, hi=0.4))
    pp = smooth_closed(pap)
    cid = D.clip(f'<path d="{pp}"/>')
    out.append(f'<g {cid}>' + taper([(cx - w * 0.6, top + h * 0.8), (cx, top + h * 0.83), (cx + w * 0.6, top + h * 0.77)], 12, 12, AEGEAN[1], 0.9) +
               taper([(cx - w * 0.6, top + h * 0.88), (cx, top + h * 0.91), (cx + w * 0.6, top + h * 0.85)], 3, 3, AEGEAN[1], 0.9) +
               taper([(cx - w * 0.2, top + h * 0.48), (cx - w * 0.1, top + h * 0.7), (cx - w * 0.04, base)], 8, 3, "#8A8A90", 0.12) + "</g>")
    out.append(taper([(cx - w * 0.22, top + h * 0.56), (cx - w * 0.02, top + h * 0.62), (cx + w * 0.5, top + h * 0.55)], 2, 2, "#FFFFFF", 0.9))
    out.append(pline([(cx - w * 0.02, top + h * 0.62), (cx + w * 0.06, base - 4)], "#C8C0B4", 1.4, seed, 0.7, 1))
    out.append("</g>")
    return "".join(out)


def skewer_meat(D, x0, y0, x1, y1, seed, n=6):
    """Pork souvlaki on a wooden skewer: charred cubes in a row."""
    out = [taper([(x0, y0), (x1, y1)], 4, 3, "#C8A06A")]
    rnd = random.Random(seed)
    for k in range(n):
        t = 0.15 + k * 0.7 / (n - 1)
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        s = rnd.uniform(17, 20)
        p = rot(rect_pts(x - s, y - s * 0.85, x + s, y + s * 0.85, 6, seed + k, 1.2), x, y, math.degrees(math.atan2(y1 - y0, x1 - x0)) + rnd.uniform(-10, 10))
        out.append(painted(D, p, ("#D8905A", "#94502A", "#4A2210"), seed + k, sdir=(0.4, 1), sk=0.22, angle=-30, n=8, inkw=1.2, hi=0.35))
        for j in range(2):
            out.append(f'<path d="M {x - s * 0.6 + j * s * 0.6:.1f} {y - s * 0.5:.1f} l {s * 0.4:.1f} {s * 0.9:.1f}" stroke="#2A0E06" stroke-width="2.4" stroke-linecap="round" opacity="0.65"/>')
        out.append(specks(seed + 10 + k, (x - s, y - s * 0.6, x + s, y + s * 0.6), ["#5A7A2A", "#2A1A08"], 6, (0.8, 1.5), (0.6, 1)))
    out.append(taper([(x1 - (x1 - x0) * 0.1, y1 - (y1 - y0) * 0.1), (x1, y1)], 3, 1, "#C8A06A"))
    return "".join(out)


@design("souvlaki")
def souvlaki():
    D = Doc2("grsv")
    # warm grill-house glow: terracotta wall, charcoal light from below
    out = [sky(D, [(0, "#E8823E"), (0.55, "#F2A452"), (1, "#F6C878")], 171, 600, ["#F4B060", "#D8682A", "#FFD08A"], 90, angle=-75, sop=(0.06, 0.16))]
    out.append(blooms(172, ["#FFD08A", "#D8642A", "#F8B868"], 8, (0, 0, 600, 600), (90, 180), (0.08, 0.14)))
    rnd = random.Random(173)
    for k in range(40):   # rising embers
        x, y = rnd.uniform(40, 560), rnd.uniform(60, 420)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1, 2.6):.1f}" fill="#FFF0B0" opacity="{rnd.uniform(0.3, 0.8):.2f}"/>')
    # metal tray on a wooden counter
    out.append(wood_planks(D, 430, 600, 174, NOCE, 3))
    out.append(f'<rect y="424" width="600" height="8" fill="#3A1E0A" opacity="0.5"/>')
    tray = rect_pts(70, 456, 530, 560, 10, 175, 0.4)
    out.append(cast(D, 310, 560, 250, 16, strength=0.45, seed=176))
    out.append(painted(D, tray, ALU, 175, sdir=(0.3, 1), sk=0.1, angle=0, n=30, inkw=2, hi=0.4))
    # greaseproof paper on the tray
    gp = poly_pts([(110, 466), (500, 462), (510, 548), (96, 552)], 14, 177, 0.8)
    out.append(painted(D, gp, ("#FFFDF4", "#F2EAD6", "#C8B898"), 177, sdir=(0.3, 1), sk=0.08, angle=-6, n=20, inkw=1.2, hi=0.3))
    # two skewers, a lemon half, a ramekin of tzatziki
    out.append(skewer_meat(D, 330, 500, 540, 470, 178, n=5))
    rx_, ry_ = 446, 528
    out.append(cast(D, rx_ + 2, ry_ + 14, 44, 8, strength=0.4, seed=180))
    out.append(painted(D, [(rx_ - 40, ry_ - 12), (rx_ - 34, ry_ + 12), (rx_ + 34, ry_ + 12), (rx_ + 40, ry_ - 12)], ("#FFFFFF", "#F4F0E8", "#B8B0A6"), 182, sdir=(0.8, 0.3), sk=0.15, angle=-90, n=8, inkw=1.6, hi=0.4))
    out.append(painted(D, ell_pts(rx_, ry_ - 12, 40, 12, 0, 360, 20), ("#FFFFFF", "#F4F0E8", "#B8B0A6"), 181, sk=0.1, n=8, inkw=1.6, hi=0.4))
    out.append(f'<path d="{blob(rx_, ry_ - 14, 33, 8, 183, 0.08, 14)}" fill="#F8FAF0"/>')
    out.append(specks(184, (rx_ - 26, ry_ - 20, rx_ + 26, ry_ - 8), ["#4A8A3A", "#2E6A2A"], 14, (0.8, 1.6), (0.7, 1)))
    out.append(f'<path d="{blob(rx_ + 6, ry_ - 16, 6, 2.5, 185, 0.2, 8)}" fill="#D8C850" opacity="0.8"/>')
    lem = ell_pts(118, 528, 26, 15, 0, 360, 18)
    out.append(painted(D, lem, LEMON, 186, sdir=(0.6, 0.8), sk=0.15, n=6, inkw=1.4, hi=0.4))
    out.append(f'<path d="{smooth_closed(ell_pts(118, 524, 21, 11, 0, 360, 18))}" fill="#FFF6B8"/>')
    for k in range(8):
        a = math.radians(k * 45)
        out.append(f'<path d="M 118 524 L {118 + math.cos(a) * 18:.1f} {524 + math.sin(a) * 9:.1f}" stroke="#E8D060" stroke-width="1.4"/>')
    # the hero wrap, standing
    out.append(cast(D, 270, 536, 80, 10, strength=0.45, seed=187))
    out.append(pita_wrap(D, 270, 534, 170, 236, 188, tilt=-4))
    out.append(steam(276, 290, 34, 189, "#FFFFFF", 3, 24, 5, 0.5))
    # lettering
    out.append(ruled(300, 80, "ENA ME OLA!", "#FFF4D8", font=JOS, size=24, ls=6, line_w=40, gap=14, line="#FFE0A8"))
    out.append(letters(D, 300, 212, "souvlaki", SERIF_IT, 120, "#FFF8EC", ["#FFFFFF", "#FFE8C8", "#FFF2DC"], 190, max_w=400,
                       shadow="#7A2A0A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(label(300, 110, "one with everything, please", SERIF_IT, 22, "#7A2A0A", max_w=360))
    return finish_g(D, out, 191, "#3A1A0A", 0.8)


# ================================================================ 9. loukoumades — honey puffs, cinnamon, walnuts
def puff(D, cx, cy, r, seed):
    """A loukoumas: craggy golden fried dough ball, glossy with honey."""
    rnd = random.Random(seed)
    pts = blob_pts(cx, cy, r, r * 0.9, seed, 0.1, 16)
    out = [painted(D, pts, ("#FFD88A", "#D8902E", "#8A4A10"), seed, sdir=(0.6, 0.8), sk=0.22, angle=-40, n=int(r * 0.9) + 4, slen=(r * 0.2, r * 0.6),
                   sw=(r * 0.05, r * 0.12), cols=["#FFE6A8", "#B8661A", "#F8C068"], inkw=max(1, r * 0.05), inkop=0.6, hi=0.45, hik=0.1, curve=0.5)]
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    inner = [f'<path d="{blob(cx - r * 0.3, cy - r * 0.38, r * 0.34, r * 0.18, seed + 1, 0.2, 10, -30)}" fill="#FFFFFF" opacity="0.7"/>',
             f'<circle cx="{cx + r * 0.25:.1f}" cy="{cy - r * 0.15:.1f}" r="{r * 0.08:.1f}" fill="#FFFFFF" opacity="0.8"/>']
    for _ in range(3):
        inner.append(f'<path d="{blob(cx + rnd.uniform(-r, r) * 0.5, cy + rnd.uniform(-r, r) * 0.5, r * 0.18, r * 0.1, rnd.randint(0, 999), 0.3, 8)}" fill="#8A4A10" opacity="0.35"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(out)


def honey_pot(D, cx, base, h, seed):
    """Clay honey pot with a ribbed rim and a wooden dipper dripping honey."""
    w = h * 0.9
    top = base - h
    body = [(cx - w * 0.36, top + 8), (cx - w * 0.5, top + h * 0.4), (cx - w * 0.44, base - 8), (cx - w * 0.3, base), (cx + w * 0.3, base),
            (cx + w * 0.44, base - 8), (cx + w * 0.5, top + h * 0.4), (cx + w * 0.36, top + 8)]
    out = [cast(D, cx + 8, base, w * 0.6, 8, strength=0.4, seed=seed)]
    out.append(painted(D, body, TERRA, seed, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=30, inkw=2, hi=0.45))
    bd = smooth_closed(body)
    cid = D.clip(f'<path d="{bd}"/>')
    out.append(f'<g {cid}>' + meander_band(D, cx - w * 0.6, cx + w * 0.6, top + h * 0.38, h * 0.2, "#3A1A0A", None, seed, rule=True, op=0.75) + "</g>")
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top + 6, w * 0.38, 9, 0, 360, 20))}" fill="{TERRA[0]}"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top + 7, w * 0.3, 6, 0, 360, 20))}" fill="#C88A1A"/>')
    out.append(ink(smooth_closed(ell_pts(cx, top + 6, w * 0.38, 9, 0, 360, 20)), INK, 1.6, seed, 1, 0.7))
    # honey running down the lip
    out.append(taper([(cx - w * 0.2, top + 8), (cx - w * 0.22, top + 22), (cx - w * 0.2, top + 30)], 8, 5, "#E8A020", 0.95))
    out.append(f'<circle cx="{cx - w * 0.2:.1f}" cy="{top + 31:.1f}" r="4.5" fill="#E8A020"/>')
    return "".join(out)


def honey_dipper(D, x0, y0, x1, y1, seed):
    """Wooden honey dipper with its grooved head at (x1, y1)."""
    out = [taper([(x0, y0), (x1, y1)], 7, 6, "#C8925A")]
    out.append(taper([(x0, y0 - 2), (x1, y1 - 2)], 2, 1.5, "#F2D0A0", 0.7))
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    head = rot(ell_pts(x1, y1, 22, 13, 0, 360, 20), x1, y1, ang)
    out.append(painted(D, head, ("#F2C890", "#C8925A", "#7A4E22"), seed, sk=0.2, n=8, inkw=1.4, hi=0.4))
    for k in range(-2, 3):
        p = rot([(x1 + k * 7, y1 - 13), (x1 + k * 7, y1 + 13)], x1, y1, ang)
        out.append(pline(p, "#7A4E22", 2, seed + k, 0.8, 1))
    out.append(f'<path d="{smooth_closed(head)}" fill="#E8A020" opacity="0.45"/>')
    return "".join(out)


@design("loukoumades")
def loukoumades():
    D = Doc2("grlk")
    out = [paper(D.nid(), "#F8E6C0", FLECK, 201)]
    out.append(blooms(202, ["#F2C878", "#FFE2A0", "#E8B060"], 8, (0, 0, 600, 600), (100, 200), (0.1, 0.18)))
    # honeycomb hexes faintly painted in the background corners
    for (hx, hy) in ((60, 300), (560, 120), (548, 360), (40, 80)):
        for k in range(3):
            for j in range(2):
                x, y = hx + k * 30 + (15 if j % 2 else 0), hy + j * 26
                pts = [(x + 15 * math.cos(math.radians(30 + 60 * i)), y + 15 * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
                out.append(f'<path d="{pd(pts)}" fill="#F2B848" opacity="0.18" stroke="#D8962A" stroke-width="1.6" stroke-opacity="0.3"/>')
    # table
    out.append(wood_planks(D, 450, 600, 203, WOOD, 3))
    out.append(f'<rect y="446" width="600" height="8" fill="#5E3618" opacity="0.5"/>')
    out.append(soft_glow(D, 290, 380, 240, "#FFF2C0", 0.6))
    # plate with the pile
    out.append(plate_34(D, 270, 470, 176, 64, 204, glaze=WHITE, rim=AEGEAN[1], rim2=AEGEAN[1]))
    balls = [(170, 452, 30), (226, 462, 32), (288, 466, 33), (350, 460, 31), (196, 424, 31), (258, 432, 33), (320, 428, 32), (372, 436, 28),
             (226, 396, 30), (290, 398, 32), (346, 404, 28), (262, 366, 29), (318, 370, 28), (290, 340, 26)]
    for i, (x, y, r) in enumerate(sorted(balls, key=lambda b: b[1])):
        out.append(puff(D, x, y, r, 210 + i))
    # honey ribbon falling from the dipper onto the pile, pooled glossy honey on the plate
    out.append(honey_dipper(D, 520, 190, 400, 252, 230))
    out.append(taper([(396, 266), (380, 292), (352, 316), (316, 336), (300, 344)], 7, 4, "#E8A020", 0.92))
    out.append(taper([(394, 268), (378, 294), (350, 316)], 2, 1, "#FFF2B0", 0.9))
    rnd = random.Random(231)
    for k in range(8):   # honey trickles over the balls
        x = rnd.uniform(200, 380)
        y = rnd.uniform(370, 450)
        out.append(taper([(x, y), (x + rnd.uniform(-4, 4), y + 12), (x + rnd.uniform(-3, 3), y + rnd.uniform(18, 28))], 6, 3, "#E8A020", 0.75))
        out.append(f'<circle cx="{x - 1:.1f}" cy="{y + 4:.1f}" r="1.6" fill="#FFF6C8" opacity="0.9"/>')
    out.append(f'<path d="{blob(270, 492, 130, 18, 232, 0.2, 18)}" fill="#E8A020" opacity="0.55"/>')
    out.append(taper([(170, 488), (260, 496), (360, 490)], 2, 2, "#FFF2B0", 0.7))
    # cinnamon dust and chopped walnuts
    out.append(specks(233, (170, 330, 390, 480), ["#7A3E18", "#5A2A0E", "#9A5A2A"], 140, (0.6, 1.6), (0.5, 0.9)))
    for k in range(18):
        x, y = rnd.uniform(190, 370), rnd.uniform(340, 470)
        out.append(f'<path d="{blob(x, y, rnd.uniform(3, 5), rnd.uniform(2.5, 4), rnd.randint(0, 999), 0.35, 8)}" fill="{rnd.choice(["#E8C890", "#C89A5A", "#F2DCA8"])}" stroke="#7A4E22" stroke-width="0.8"/>')
    # honey pot and a little bee come for a taste
    out.append(honey_pot(D, 488, 560, 110, 234))
    out.append(honeybee(D, 120, 312, 22, 235, rot_=-10))
    out.append(f'<path d="{smooth_open([(146, 300), (176, 286), (204, 296), (196, 316), (176, 312), (186, 296), (222, 290), (260, 300)])}" fill="none" stroke="#7A4E22" stroke-width="1.8" stroke-dasharray="5 6" stroke-linecap="round" opacity="0.6"/>')
    out.append(f'<g opacity="0.0">{pline([(0, 0), (1, 1)], INK, 1, 1, 1, 1)}</g>')
    # lettering
    out.append(letters(D, 300, 146, "loukoumades", SERIF_IT, 110, "#8A3A0A", ["#A84E14", "#6A2A06", "#C8661E"], 237, max_w=470,
                       shadow="#FFF2C0", soff=(0.02, 0.035), angle=-40, hi="#FFD08A"))
    out.append(ruled(300, 192, "HONEY · CINNAMON · WALNUTS", "#1F56A8", font=JOS, size=19, ls=4, line_w=28, gap=12))
    return finish_g(D, out, 238)


# ================================================================ 10. frappé — on the beach, under the straw umbrella
def frappe_glass(D, cx, base, h, seed):
    """Tall frappé glass: dark coffee at the bottom, thick beige foam above, ice, condensation, a bendy straw."""
    w = h * 0.4
    top = base - h
    out = [cast(D, cx + 10, base, w * 0.8, 8, strength=0.4, seed=seed)]
    body = [(cx - w / 2, top), (cx - w * 0.43, base - 6), (cx - w * 0.36, base), (cx + w * 0.36, base), (cx + w * 0.43, base - 6), (cx + w / 2, top)]
    bd = pd(body)
    # straw behind the foam top
    sx = cx + w * 0.16
    out.append(taper([(sx, base - h * 0.3), (sx + 2, top - 4), (sx + 6, top - 26)], 9, 9, "#FFFFFF"))
    out.append(f'<g>' + "".join(taper([(sx + 1, top - 4 - k * 8), (sx + 4, top - 8 - k * 8)], 9, 9, "#E0302A", 0.9) for k in range(0, 2)) + "</g>")
    out.append(taper([(sx + 6, top - 26), (sx + 16, top - 40), (sx + 40, top - 46)], 9, 9, "#FFFFFF"))
    for k in range(4):
        t = k / 4
        out.append(taper([(sx + 6 + t * 30, top - 28 - t * 16), (sx + 12 + t * 30, top - 32 - t * 16)], 9.5, 9.5, "#E0302A", 0.9))
    out.append(ink(smooth_open([(sx - 4, top), (sx + 2, top - 26), (sx + 16, top - 44), (sx + 42, top - 50)]), INK, 1, seed, 1, 0.35))
    out.append(f'<path d="{bd}" fill="#EEF4F4" opacity="0.5"/>')
    lvl_coffee, lvl_foam = base - h * 0.42, top + h * 0.1
    cof = [(cx - w * 0.47, lvl_coffee), (cx - w * 0.43, base - 7), (cx - w * 0.35, base - 3), (cx + w * 0.35, base - 3), (cx + w * 0.43, base - 7), (cx + w * 0.47, lvl_coffee)]
    foam = [(cx - w * 0.49, lvl_foam), (cx - w * 0.47, lvl_coffee + 6), (cx + w * 0.47, lvl_coffee + 6), (cx + w * 0.49, lvl_foam)]
    out.append(f'<path d="{pd(foam)}" fill="{D.lin([(0, "#F2DEC0"), (0.6, "#D8B488"), (1, "#B88A58")])}"/>')
    out.append(f'<path d="{pd(cof)}" fill="{D.lin([(0, "#8A5A32"), (1, "#3A1E0E")])}"/>')
    cid = D.clip(f'<path d="{pd(foam)}"/>')
    rnd = random.Random(seed)
    bub = "".join(f'<circle cx="{rnd.uniform(cx - w / 2, cx + w / 2):.1f}" cy="{rnd.uniform(lvl_foam, lvl_coffee + 6):.1f}" r="{rnd.uniform(0.6, 2):.1f}" fill="{rnd.choice(["#FFF4E0", "#A87A4A"])}" opacity="0.6"/>' for _ in range(60))
    out.append(f'<g {cid}>{bub}</g>')
    # ice cubes in the coffee and foam
    for k, (dx, dy, a) in enumerate(((-0.18, 0.62, 12), (0.14, 0.5, -15), (-0.05, 0.36, 25))):
        ix, iy, s = cx + dx * w, top + dy * h, w * 0.3
        cube = rot(rect_pts(ix - s / 2, iy - s / 2, ix + s / 2, iy + s / 2, 6, seed + k, 0.4), ix, iy, a)
        out.append(f'<path d="{smooth_closed(cube)}" fill="#FFFFFF" opacity="0.35"/>' + ink(smooth_closed(cube), "#E8DCC8", 1, seed + k, 1, 0.7))
    # foam top dome
    out.append(f'<path d="{smooth_closed(ell_pts(cx, lvl_foam, w * 0.49, w * 0.1, 0, 360, 18))}" fill="#F6E6CC"/>')
    out.append(specks(seed + 3, (cx - w * 0.4, lvl_foam - 4, cx + w * 0.4, lvl_foam + 4), ["#C89A6A", "#FFFFFF"], 20, (0.6, 1.6), (0.5, 0.9)))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, w / 2, w * 0.1, 0, 360, 18))}" fill="none" stroke="#9AB0B8" stroke-width="1.6"/>')
    out.append(ink(bd, "#6A8088", 1.6, seed, 1, 0.75))
    out.append(taper([(cx - w * 0.36, top + 10), (cx - w * 0.33, base - 14)], 4, 1.4, "#FFFFFF", 0.8))
    for _ in range(int(h * 0.4)):
        x, y = rnd.uniform(cx - w * 0.42, cx + w * 0.44), rnd.uniform(top + 10, base - 8)
        r = rnd.uniform(0.8, 2.2)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#FFFFFF" opacity="0.7"/>')
    out.append(taper([(sx - 1, top + 2), (sx, lvl_foam + 4)], 9, 9, "#FFFFFF", 0.0))
    return "".join(out)


def straw_umbrella(D, cx, cy, r, seed, pole_to=None):
    """Thatched beach umbrella (the straw parasols on Greek beaches) seen from below-side."""
    out = []
    if pole_to:
        out.append(taper([(cx, cy), pole_to], 7, 6, "#9A7A4A"))
    pts = [(cx - r, cy + r * 0.12), (cx - r * 0.7, cy - r * 0.18), (cx, cy - r * 0.42), (cx + r * 0.7, cy - r * 0.18), (cx + r, cy + r * 0.12)]
    fringe = []
    for i in range(25):
        t = i / 24
        x = cx - r + 2 * r * t
        fringe.append((x, cy + r * 0.12 + 10 + (6 if i % 2 else 0)))
    shape = pts + fringe[::-1]
    out.append(painted(D, shape, ("#F2D28A", "#D8A850", "#8A6228"), seed, sdir=(0.3, 1), sk=0.18, angle=-60, n=int(r * 1.2), slen=(10, 40), sw=(1, 2.5),
                       cols=["#F8E2A0", "#B8862E", "#E8C070", "#7A5222"], inkw=1.6, hi=0.4))
    rnd = random.Random(seed)
    d = smooth_closed(shape)
    cid = D.clip(f'<path d="{d}"/>')
    st = "".join(f'<path d="M {cx + rnd.uniform(-r * 0.2, r * 0.2):.1f} {cy - r * 0.42:.1f} L {cx + r * rnd.uniform(-1.05, 1.05):.1f} {cy + r * 0.3:.1f}" stroke="{rnd.choice(["#8A6228", "#F8E2A0"])}" stroke-width="1.2" opacity="0.5"/>' for _ in range(60))
    out.append(f'<g {cid}>{st}</g>')
    return "".join(out)


@design("frappe")
def frappe():
    D = Doc2("grfr")
    out = [sky(D, [(0, "#5AB8E8"), (0.6, "#A8DCF2"), (1, "#E2F4F8")], 241, 300, ["#C8ECF8", "#6AC0E8"], 40, sop=(0.06, 0.14))]
    out.append(puff_cloud(D, 520, 252, 110, 242, op=0.9))
    # sea: deep blue to turquoise shallows, a rocky headland
    hd = ridge([(330, 286), (420, 262), (520, 258), (620, 272)], 243, 8, 3)
    out.append(f'<path d="{smooth_open(hd)} L 620 300 L 330 300 Z" fill="#9A8A7A"/>')
    out.append(f'<path d="{smooth_open([(x, y + 6) for x, y in hd])} L 620 300 L 330 300 Z" fill="#7A6A5E" opacity="0.6"/>')
    out.append(sea(D, 296, 430, [(0, "#1E5AA8"), (0.5, "#2A9AC0"), (1, "#7ADCD8")], 244, ["#FFFFFF", "#1E4E98", "#9AE8E0"], 70, ticks=["#FFFFFF"]))
    # sand
    sand_line = [(-20, 430), (200, 420), (420, 428), (620, 418)]
    out.append(hill(D, sand_line, 620, ("#FFF0D0", "#F2DCA8", "#C8A870"), 245, angle=-4, inkw=0, sop=(0.1, 0.3)))
    out.append(taper([(-20, 432), (200, 422), (420, 430), (620, 420)], 5, 5, "#FFFFFF", 0.8))
    out.append(specks(246, (0, 440, 600, 600), ["#C8A870", "#FFFFFF", "#A88A58"], 140, (0.8, 2), (0.3, 0.7)))
    # the straw umbrella overhead (top-left) and its shadow on the sand
    out.append(f'<path d="{blob(170, 540, 230, 44, 247, 0.1, 18)}" fill="#8A6A3A" opacity="0.18"/>')
    out.append(straw_umbrella(D, 40, 120, 170, 248, pole_to=(84, 470)))
    # small wooden beach table with the frappé
    for x in (232, 470):
        out.append(painted(D, rect_pts(x - 7, 490, x + 7, 590, 10, 250 + x, 0.4), WOOD, 250 + x, sdir=(1, 0), sk=0.2, angle=-90, n=6, inkw=1.2, hi=0.3))
    out.append(painted(D, rect_pts(206, 462, 496, 476, 10, 249, 0.4), WOOD, 249, sdir=(0, 1), sk=0.2, angle=0, n=16, inkw=1.6, hi=0.4))
    out.append(painted(D, rect_pts(202, 476, 500, 494, 10, 251, 0.4), ("#B87A44", "#8A5428", "#4A2810"), 251, sdir=(0, 1), sk=0.2, angle=0, n=14, inkw=1.6, hi=0.3))
    out.append(frappe_glass(D, 346, 468, 222, 252))
    # sunglasses and a seashell on the table
    out.append(pline([(428, 462), (442, 456), (458, 462)], "#2A2A30", 2.4, 253, 1, 1))
    for x0 in (422, 452):
        out.append(f'<path d="{blob(x0 + 4, 462, 13, 8, 254 + x0, 0.1, 10)}" fill="#2A3A4A"/><path d="{blob(x0, 459, 4, 2, 255 + x0, 0.2, 8)}" fill="#8AB8D8" opacity="0.8"/>')
    out.append(f'<path d="{blob(256, 460, 14, 8, 256, 0.1, 10)}" fill="#F8D8C8"/>' + "".join(pline([(256, 467), (248 + k * 5, 453)], "#C8907A", 1.2, k, 0.7, 1) for k in range(4)))
    # lettering, top right over the sky
    out.append(letters(D, 396, 126, "frappé", SERIF_IT, 112, "#7A3E14", ["#8A4A1E", "#5A2A08", "#A86A3A"], 257, max_w=280,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#E8B88A"))
    out.append(ruled(396, 166, "GLYKO ME GALA", "#14387A", font=JOS, size=20, ls=5, line_w=22, gap=10, max_w=230))
    out.append(label(396, 194, "sweet, with milk", SERIF_IT, 20, "#14387A", max_w=240))
    return finish_g(D, out, 258)


# ================================================================ 11. opa! — plates flying at the taverna
def flying_plate(D, cx, cy, rx, ry, rot_, seed, band=AEGEAN):
    out = [f'<g transform="rotate({rot_} {cx} {cy})">']
    out.append(painted(D, ell_pts(cx, cy, rx, ry, 0, 360, 36), WHITE, seed, sdir=(0.3, 1), sk=0.12, angle=0, n=16, inkw=1.8, hi=0.45))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy + ry * 0.05, rx * 0.66, ry * 0.62, 0, 360, 30))}" fill="#EAE6DE"/>')
    out.append(ink(smooth_closed(ell_pts(cx, cy, rx * 0.86, ry * 0.84, 0, 360, 36)), band[1], max(1.6, rx * 0.04), seed, 1, 0.9))
    out.append("</g>")
    return "".join(out)


def shard(D, cx, cy, s, rot_, seed, band=AEGEAN):
    rnd = random.Random(seed)
    n = rnd.randint(3, 5)
    pts = [(cx + math.cos(a) * s * rnd.uniform(0.5, 1.1), cy + math.sin(a) * s * rnd.uniform(0.4, 0.9)) for a in sorted(rnd.uniform(0, 6.28) for _ in range(n))]
    pts = rot(pts, cx, cy, rot_)
    d = pd(pts)
    out = [f'<path d="{d}" fill="#FAF8F2"/>', f'<path d="M {pts[0][0]:.1f} {pts[0][1]:.1f} L {pts[1][0]:.1f} {pts[1][1]:.1f}" stroke="{band[1]}" stroke-width="{max(1.5, s * 0.15):.1f}"/>',
           ink(d, INK, 1.1, seed, 1, 0.6)]
    return "".join(out)


def carnation(D, cx, cy, r, seed, col=RED, stem=None):
    rnd = random.Random(seed)
    out = []
    if stem:
        out.append(taper([(cx, cy + r * 0.6), stem], 3, 2, "#4A7A3A"))
    for k in range(14):
        a = rnd.uniform(0, 6.28)
        rr = r * rnd.uniform(0.3, 0.95)
        x, y = cx + math.cos(a) * rr * 0.9, cy + math.sin(a) * rr * 0.7
        pts = [(x + math.cos(a + t) * r * 0.42, y + math.sin(a + t) * r * 0.32) for t in (-0.9, -0.45, 0, 0.45, 0.9)] + [(x - math.cos(a) * r * 0.1, y - math.sin(a) * r * 0.1)]
        out.append(f'<path d="{smooth_closed(jitter(pts, seed + k, 1.2))}" fill="{rnd.choice(col)}"/>')
    out.append(f'<path d="{blob(cx, cy + r * 0.55, r * 0.28, r * 0.2, seed, 0.1, 8)}" fill="#5A8A3A"/>')
    return "".join(out)


def plate_piece(D, cx, cy, rx, ry, a0, a1, seed, off=(0, 0), spin=0, band=AEGEAN, crack_seed=0):
    """One wedge of a broken plate (between angles a0..a1, degrees), jagged on its broken edges."""
    rnd = random.Random(seed)
    def rim(a, k=1.0):
        return (cx + rx * k * math.cos(math.radians(a)), cy + ry * k * math.sin(math.radians(a)))
    def jag(p, q, sd):
        r = random.Random(sd)
        pts = []
        for i in range(1, 5):
            t = i / 5
            x, y = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
            pts.append((x + r.uniform(-6, 6), y + r.uniform(-3, 3)))
        return pts
    c = (cx + rnd.uniform(-4, 4), cy + rnd.uniform(-2, 2))
    arc = [rim(a0 + (a1 - a0) * i / 10) for i in range(11)]
    poly = [c] + jag(c, arc[0], crack_seed + int(a0)) + arc + jag(arc[-1], c, crack_seed + int(a1))
    mid = math.radians((a0 + a1) / 2)
    ox, oy = off
    poly = [(x + ox, y + oy) for x, y in poly]
    poly = rot(poly, cx + ox, cy + oy, spin)
    d = pd(poly)
    out = [f'<path d="{d}" fill="#3A0E0A" opacity="0.25" transform="translate(4 6)"/>', f'<path d="{d}" fill="#FAF8F2"/>']
    cid = D.clip(f'<path d="{d}"/>')
    g = f'<g transform="translate({ox:.1f} {oy:.1f}) rotate({spin:.1f} {cx:.1f} {cy:.1f})">'
    inner = [g, f'<path d="{smooth_closed(ell_pts(cx, cy + ry * 0.04, rx * 0.66, ry * 0.64, 0, 360, 30))}" fill="#ECE8E0"/>',
             ink(smooth_closed(ell_pts(cx, cy + ry * 0.04, rx * 0.66, ry * 0.64, 0, 360, 30)), "#D0C8BC", 1.4, seed, 1, 0.8)]
    for k in (0.9, 0.76):
        inner.append(ink(smooth_closed(ell_pts(cx, cy, rx * k, ry * k, 0, 360, 40)), band[1], 2.4, seed, 1, 0.95))
    for i in range(36):   # little key ticks between the two blue rings
        a = math.radians(i * 10)
        x, y = cx + rx * 0.83 * math.cos(a), cy + ry * 0.83 * math.sin(a)
        inner.append(f'<rect x="{x - 2.6:.1f}" y="{y - 2.6:.1f}" width="5.2" height="5.2" fill="{band[1]}" transform="rotate({math.degrees(a):.0f} {x:.1f} {y:.1f})"/>')
    inner.append("</g>")
    out.append(f'<g {cid}>{"".join(inner)}' + shade_over(D, d, "#5A2A1A", 0.22, 0, 0, 1, 1, 0.5) + "</g>")
    out.append(ink(d, INK, 1.5, seed, 1, 0.7))
    return "".join(out)


@design("opa")
def opa():
    D = Doc2("grop")
    # deep taverna red wall, warm light, string of lights
    out = [sky(D, [(0, "#5A1418"), (0.55, "#9A2A22"), (1, "#C8502E")], 261, 600, ["#B8382A", "#6A1A1A", "#D8603A"], 100, angle=-80, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 300, 360, 300, "#FFB070", 0.5))
    out.append(string_lights(D, -20, 40, 620, 52, 40, 10, 262))
    # stone floor
    rnd = random.Random(263)
    out.append(f'<rect y="470" width="600" height="140" fill="#B89A80"/>')
    for row in range(5):
        y = 470 + row * 30
        x = -rnd.uniform(0, 40)
        while x < 620:
            w = rnd.uniform(50, 90)
            out.append(f'<path d="{hg.org_rect(x + 2, y + 2, w - 4, 26, int(x * 3 + y), 1.2, 10, 4)}" fill="{rnd.choice(["#C8AA8E", "#B09078", "#D2B89C", "#A88A72"])}"/>')
            x += w
    out.append(f'<rect y="470" width="600" height="140" fill="{D.lin([(0, "#3A0E0A", 0.5), (1, "#3A0E0A", 0.05)])}"/>')
    # the plate, mid-shatter, with its pieces flying apart
    cx, cy, rx, ry = 300, 404, 132, 60
    out.append(soft_glow(D, cx, cy, 170, "#FFF0D0", 0.45))
    cuts = [0, 52, 118, 170, 232, 290, 360]
    for k in range(6):
        a0, a1 = cuts[k] - 8, cuts[k + 1] - 8
        mid = math.radians((a0 + a1) / 2)
        d_ = 22 + rnd.uniform(0, 16)
        out.append(plate_piece(D, cx, cy, rx, ry, a0, a1, 300 + k, off=(math.cos(mid) * d_ * 1.5, math.sin(mid) * d_ * 0.8 - 6), spin=rnd.uniform(-8, 8), crack_seed=7))
    # burst: shards, dust and speed lines radiating out
    for k in range(22):
        a = rnd.uniform(0, 2 * math.pi)
        dist = rnd.uniform(1.25, 1.9)
        x, y = cx + math.cos(a) * rx * dist, cy + math.sin(a) * ry * dist * 1.1
        out.append(taper([(cx + math.cos(a) * rx * 1.05, cy + math.sin(a) * ry * 1.1), (x - math.cos(a) * 10, y - math.sin(a) * 5)], 0.6, 2.4, "#FFE8C8", 0.45))
        out.append(shard(D, x, y, rnd.uniform(6, 14), rnd.uniform(0, 360), 320 + k))
    for k in range(10):
        a = rnd.uniform(0, 2 * math.pi)
        out.append(f'<path d="{blob(cx + math.cos(a) * rx * 1.2, cy + math.sin(a) * ry * 1.3, rnd.uniform(10, 20), rnd.uniform(6, 10), 340 + k, 0.3, 10)}" fill="#FFF4E0" opacity="0.25"/>')
    # a second plate on its way in, top left
    out.append(flying_plate(D, 112, 290, 46, 18, -24, 266))
    for k in range(3):
        out.append(taper([(40 - k * 6, 330 + k * 9), (80 - k * 4, 310 + k * 7)], 1, 4, "#FFE0C0", 0.5))
    # shards on the floor
    for k in range(18):
        out.append(shard(D, rnd.uniform(60, 540), rnd.uniform(500, 560), rnd.uniform(7, 14), rnd.uniform(0, 360), 264 + k))
    # red carnations thrown in the air
    for k, (x, y) in enumerate(((84, 430), (522, 300), (504, 452), (472, 336), (90, 360))):
        out.append(carnation(D, x, y, 15, 280 + k, ("#E8302A", "#C8181E", "#F8604A"), stem=(x + 14, y + 24)))
    for k in range(22):
        x, y = rnd.uniform(60, 540), rnd.uniform(270, 560)
        out.append(f'<path d="{blob(x, y, 4, 2.6, 290 + k, 0.2, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#E8302A", "#F8604A", "#C8181E"])}" opacity="0.85"/>')
    # lettering
    out.append(letters(D, 300, 196, "Opa!", SERIF_IT, 168, "#FFF4E0", ["#FFFFFF", "#FFE2C8", "#FFF0E0"], 291, max_w=360,
                       shadow="#2A0606", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 240, "LET THE PLATES FLY", "#FFD8A0", font=JOS, size=20, ls=5, line_w=36, gap=14))
    return finish_g(D, out, 292, "#2A0A0A", 0.8)


# ================================================================ 12. mykonos — the windmills of Kato Mili
def windmill(D, x, base, h, seed, sail_ang=10, haze=0.0, sails=True, light=(-0.8, -0.3)):
    """Cycladic windmill: whitewashed tapered cylinder, conical thatched cap, wooden spars with triangular
    canvas sails, small door and window."""
    hz = (lambda c: mix(c, "#E8C8B8", haze)) if haze else (lambda c: c)
    w0, w1 = h * 0.5, h * 0.42
    body = [(x - w0 / 2, base), (x - w1 / 2, base - h), (x + w1 / 2, base - h), (x + w0 / 2, base)]
    out = [painted(D, poly_pts(body, 8, seed, 0.4), tuple(hz(c) for c in WASH_W), seed, sdir=(-light[0], 0.2), sk=0.22, angle=-90, n=int(h * 0.4), inkw=1.3, inkop=0.5, hi=0.35)]
    out.append(f'<path d="{hg.org_rect(x - h * 0.06, base - h * 0.32, h * 0.12, h * 0.32, seed, 0.4, 8, 2)}" fill="{hz(AEGEAN[1])}"/>')
    out.append(f'<path d="{hg.org_rect(x + h * 0.06, base - h * 0.7, h * 0.08, h * 0.1, seed + 1, 0.3, 6, 1)}" fill="{hz("#3A2A2A")}"/>')
    # conical cap
    cap = [(x - w1 / 2 - 4, base - h + 2), (x - w1 * 0.2, base - h - h * 0.22), (x + h * 0.02, base - h - h * 0.3), (x + w1 * 0.3, base - h - h * 0.2), (x + w1 / 2 + 4, base - h + 2)]
    out.append(painted(D, cap, tuple(hz(c) for c in ("#D8B888", "#A8845A", "#5E4628")), seed + 2, sdir=(-light[0], 0.5), sk=0.25, angle=-60, n=12, inkw=1.2, inkop=0.6, hi=0.4))
    hub = (x - w1 * 0.12, base - h - h * 0.08)
    if sails:
        L = h * 0.8
        tips = []
        for k in range(8):
            a = math.radians(sail_ang + k * 45)
            tips.append((hub[0] + math.cos(a) * L * 0.6, hub[1] + math.sin(a) * L * 0.6))
        out.append(ink(pd(tips), hz("#7A6A5A"), 0.9, seed, 1, 0.7))
        for k in range(8):
            a = math.radians(sail_ang + k * 45)
            tip = (hub[0] + math.cos(a) * L, hub[1] + math.sin(a) * L)
            if k % 2 == 0:
                a2 = a + math.radians(16)
                t1 = (hub[0] + math.cos(a) * L * 0.96, hub[1] + math.sin(a) * L * 0.96)
                t2 = (hub[0] + math.cos(a2) * L * 0.72, hub[1] + math.sin(a2) * L * 0.72)
                t3 = (hub[0] + math.cos(a) * L * 0.32, hub[1] + math.sin(a) * L * 0.32)
                out.append(f'<path d="{pd([t3, t1, t2])}" fill="{hz("#FFF8EC")}" opacity="0.95"/>' + ink(pd([t3, t1, t2]), hz("#8A7A6A"), 1, seed + k, 1, 0.6))
            out.append(pline([hub, tip], hz("#5A3E22"), max(1.5, h * 0.018), seed + k, 0.95, 1))
        out.append(f'<circle cx="{hub[0]:.1f}" cy="{hub[1]:.1f}" r="{max(2.5, h * 0.035):.1f}" fill="{hz("#4A3A2A")}"/>')
    return "".join(out)


@design("mykonos")
def mykonos():
    D = Doc2("grmy")
    out = [sky(D, [(0, "#1E5AB8"), (0.45, "#5A9AE0"), (0.8, "#B8DCF4"), (0.9, "#E2F2FA")], 301, 380, ["#8AB8EA", "#D8ECF8"], 60, sop=(0.06, 0.14))]
    out.append(soft_glow(D, 520, 90, 160, "#FFFFFF", 0.5))
    for x, y, w in ((150, 236, 130), (480, 220, 100)):
        out.append(puff_cloud(D, x, y, w, 302 + x, op=0.95))
    out.append(sea(D, 350, 600, [(0, "#4A8AD0"), (0.3, "#1E5AA8"), (1, "#0E3A80")], 303, ["#FFFFFF", "#0E3A80", "#7AC0E8"], 80, ticks=["#FFFFFF"]))
    # distant island
    out.append(f'<path d="{smooth_open(ridge([(-20, 352), (60, 340), (140, 344), (200, 352)], 304, 4, 3))} L 200 356 L -20 356 Z" fill="#9AB0CC"/>')
    # the windmill ridge: golden grassy hill rising to the right
    line = [(-20, 520), (100, 468), (220, 430), (340, 404), (460, 390), (620, 380)]
    out.append(hill(D, line, 620, ("#F2D49A", "#D8AC6A", "#8A6A3A"), 305, angle=-14, inkw=1.6, lit="#FFF0C8"))
    out.append(grass(306, (0, 400, 600, 600), ["#C89A5A", "#E8C88A", "#A87A3A"], n=160, h=(6, 14)))
    # stone path up the ridge
    path_ = [(150, 620), (190, 560), (250, 500), (320, 450), (380, 418)]
    out.append(taper(path_, 60, 12, "#E8DCC8", 0.85))
    rnd = random.Random(307)
    for k in range(30):
        t = rnd.random()
        i = min(len(path_) - 2, int(t * (len(path_) - 1)))
        x = path_[i][0] + (path_[i + 1][0] - path_[i][0]) * (t * (len(path_) - 1) - i) + rnd.uniform(-14, 14) * (1 - t)
        y = path_[i][1] + (path_[i + 1][1] - path_[i][1]) * (t * (len(path_) - 1) - i)
        out.append(f'<path d="{blob(x, y, 6 * (1 - t * 0.6), 3.5 * (1 - t * 0.6), k, 0.2, 8)}" fill="#C8B8A0" opacity="0.7"/>')
    # windmills along the ridge, receding to the right
    for k, (x, base, h, ang) in enumerate(((522, 388, 54, 8), (438, 396, 72, 28), (330, 412, 98, 14), (188, 452, 128, 2))):
        out.append(cast(D, x + h * 0.3, base + 2, h * 0.4, 6, strength=0.35, seed=308 + k))
        out.append(windmill(D, x, base, h, 310 + k, sail_ang=ang, haze=0.25 * (3 - k) / 3))
    # dry stone wall in the front corner with a little chapel
    out.append(cast(D, 520, 542, 60, 8, strength=0.35, seed=319))
    out.append(cube_house(D, 466, 540, 72, 48, 320, side=0.22, door=RED, windows=0, light="left"))
    out.append(blue_dome(D, 502, 492, 23, 321, pal=RED, drum=0.3, belt=False))
    # Little Venice: a row of houses with coloured wooden balconies right on the water, bottom left
    rnd2 = random.Random(326)
    lv = [(-20, 548, 44, 66), (22, 552, 42, 58), (62, 556, 46, 70), (106, 562, 40, 54)]
    for i, (x, b_, w_, h_) in enumerate(lv):
        out.append(cube_house(D, x, b_, w_, h_, 327 + i, side=0.18, door=None, windows=2, light="left", step=False))
        bc = rnd2.choice([RED, AEGEAN, ("#FFE08A", "#F2C040", "#A8800A"), GREEN])
        out.append(painted(D, rect_pts(x + 2, b_ - h_ * 0.5, x + w_ - 2, b_ - h_ * 0.36, 6, 331 + i, 0.3), bc, 331 + i, sk=0.2, n=3, inkw=1, hi=0.3))
        for j in range(5):
            out.append(f'<rect x="{x + 4 + j * (w_ - 8) / 4:.1f}" y="{b_ - h_ * 0.5:.1f}" width="2" height="{h_ * 0.14:.1f}" fill="{bc[2]}"/>')
    # lettering
    out.append(letters(D, 300, 124, "Mykonos", SERIF_IT, 124, "#FFFFFF", ["#FFFFFF", "#F2F4FA", "#E8ECF8"], 324, max_w=420,
                       shadow="#1E3E7A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 170, "THE WINDMILLS OF KATO MILI", "#14387A", font=JOS, size=19, ls=4, line_w=28, gap=12))
    return finish_g(D, out, 325)


# ================================================================ 13. philoxenia — a spoon sweet and a glass of cold water
def lace_doily(D, cx, cy, rx, ry, seed, col="#FFFFFF"):
    """Crocheted lace doily in 3/4 view: scalloped edge, rings of holes, a rosette in the middle."""
    out = []
    pts = []
    for i in range(96):
        a = 2 * math.pi * i / 96
        k = 1 + 0.06 * math.cos(a * 24)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    d = smooth_closed(pts)
    out.append(f'<path d="{d}" fill="{col}" opacity="0.92"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for ring_k, n, r_ in ((0.88, 24, 0.035), (0.7, 20, 0.04), (0.52, 16, 0.04), (0.34, 12, 0.035)):
        for i in range(n):
            a = 2 * math.pi * (i + 0.5 * (ring_k > 0.6)) / n
            x, y = cx + rx * ring_k * math.cos(a), cy + ry * ring_k * math.sin(a)
            inner.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx * r_:.1f}" ry="{ry * r_ * 0.9:.1f}" fill="#8A6A4A" opacity="0.35"/>')
        inner.append(ink(smooth_closed(ell_pts(cx, cy, rx * (ring_k + 0.08), ry * (ring_k + 0.08), 0, 360, 40)), "#C8BCA8", 1, seed, 1, 0.7))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, "#C8BCA8", 1.2, seed, 1, 0.8))
    return "".join(out)


def silver_tray(D, cx, cy, rx, ry, seed):
    out = [cast(D, cx + 12, cy + ry * 0.4, rx * 1.02, ry * 0.8, strength=0.35, seed=seed)]
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy + 6, rx, ry, 0, 360, 44))}" fill="#6A7080"/>')
    out.append(painted(D, ell_pts(cx, cy, rx, ry, 0, 360, 44), ("#FFFFFF", "#D8DCE4", "#8A909C"), seed, sdir=(0.5, 0.9), sk=0.1, angle=-20, n=30, inkw=1.8, hi=0.5))
    # embossed rim: a ring of beads
    for i in range(60):
        a = 2 * math.pi * i / 60
        x, y = cx + rx * 0.93 * math.cos(a), cy + ry * 0.92 * math.sin(a)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.1" fill="{"#FFFFFF" if math.sin(a) < 0 else "#9AA0AC"}" opacity="0.9"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy + 2, rx * 0.84, ry * 0.82, 0, 360, 40))}" fill="{D.lin([(0, "#F4F6FA"), (0.5, "#C8CCD6"), (1, "#E8ECF2")], 0, 0, 1, 1)}"/>')
    out.append(ink(smooth_closed(ell_pts(cx, cy + 2, rx * 0.84, ry * 0.82, 0, 360, 40)), "#8A909C", 1.2, seed, 1, 0.7))
    out.append(taper(ell_pts(cx, cy + 2, rx * 0.78, ry * 0.76, 200, 300, 12), 4, 1, "#FFFFFF", 0.8))
    return "".join(out)


def cherry_sweet_dish(D, cx, base, w, seed):
    """Small glass dish on a stem holding vissino (sour cherry spoon sweet): glossy dark cherries in ruby syrup."""
    rnd = random.Random(seed)
    top = base - w * 0.62
    out = [cast(D, cx + 6, base, w * 0.5, 6, strength=0.35, seed=seed)]
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - 4, w * 0.3, w * 0.07, 0, 360, 18))}" fill="#E8F2F4" opacity="0.8"/>' + ink(smooth_closed(ell_pts(cx, base - 4, w * 0.3, w * 0.07, 0, 360, 18)), "#8AA4AC", 1.2, seed, 1, 0.7))
    out.append(f'<path d="M {cx - 4:.1f} {base - 6:.1f} L {cx - 3:.1f} {top + w * 0.3:.1f} L {cx + 3:.1f} {top + w * 0.3:.1f} L {cx + 4:.1f} {base - 6:.1f} Z" fill="#E8F2F4" opacity="0.8"/>')
    bowl = ell_pts(cx, top, w / 2, w * 0.13, 0, 180, 20) + [(cx - w * 0.3, top + w * 0.3), (cx + w * 0.3, top + w * 0.3)][::-1][::-1]
    bowl = [(cx + w / 2, top)] + [(cx + w * 0.36, top + w * 0.24), (cx, top + w * 0.32), (cx - w * 0.36, top + w * 0.24)] + [(cx - w / 2, top)]
    bd = smooth_closed(bowl + ell_pts(cx, top, w / 2, w * 0.13, 180, 360, 20)[1:-1][::-1][::-1])
    syrup = [(cx + w * 0.47, top + 2)] + [(cx + w * 0.34, top + w * 0.23), (cx, top + w * 0.3), (cx - w * 0.34, top + w * 0.23)] + [(cx - w * 0.47, top + 2)]
    out.append(f'<path d="{smooth_closed(syrup)}" fill="#8A0E1E" opacity="0.92"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top + 1, w * 0.47, w * 0.11, 0, 360, 22))}" fill="#A8142A"/>')
    for k in range(9):
        x, y = cx + rnd.uniform(-w * 0.34, w * 0.34), top + rnd.uniform(-w * 0.06, w * 0.06) - 3
        r = w * 0.075
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#4A0410"/><circle cx="{x - r * 0.35:.1f}" cy="{y - r * 0.4:.1f}" r="{r * 0.28:.1f}" fill="#FFD0D8" opacity="0.9"/>')
    out.append(f'<path d="{bd}" fill="#E8F4F8" opacity="0.18"/>')
    out.append(ink(smooth_open(bowl), "#8AA4AC", 1.4, seed, 1, 0.8))
    out.append(ink(smooth_closed(ell_pts(cx, top, w / 2, w * 0.13, 0, 360, 22)), "#8AA4AC", 1.4, seed + 1, 1, 0.8))
    out.append(taper([(cx - w * 0.38, top + 6), (cx - w * 0.26, top + w * 0.2)], 3, 1, "#FFFFFF", 0.85))
    return "".join(out)


def teaspoon(D, x0, y0, x1, y1, seed, metal=("#FFFFFF", "#C8CCD6", "#7A808C")):
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    out = [taper([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 - 2), (x1, y1)], 3, 5, metal[1])]
    out.append(taper([(x0, y0 - 1), (x1, y1 - 1)], 1, 1.6, metal[0], 0.9))
    bowl = rot(ell_pts(x0 - 9 * math.cos(math.radians(ang)), y0 - 9 * math.sin(math.radians(ang)), 12, 7, 0, 360, 16), x0 - 9 * math.cos(math.radians(ang)), y0 - 9 * math.sin(math.radians(ang)), ang)
    out.append(painted(D, bowl, metal, seed, sk=0.2, n=4, inkw=1.2, hi=0.5))
    return "".join(out)


@design("philoxenia")
def philoxenia():
    D = Doc2("grph")
    # deep cobalt wall, a warm lamp glow, wooden sideboard
    out = [sky(D, [(0, "#1E3E7E"), (1, "#2E5A9E")], 351, 600, ["#2A4E92", "#16306A", "#3A66AA"], 120, angle=-80, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 300, 380, 300, "#FFE0A0", 0.35))
    out.append(blooms(352, ["#3A62A8", "#14306A"], 6, (0, 0, 600, 600), (100, 180), (0.08, 0.14)))
    out.append(wood_planks(D, 400, 600, 353, NOCE, 3))
    out.append(f'<rect y="394" width="600" height="10" fill="#1E0E06" opacity="0.5"/>')
    out.append(lace_doily(D, 300, 470, 236, 90, 354))
    out.append(silver_tray(D, 300, 462, 190, 74, 355))
    # glass of cold water, the dish of sour-cherry sweet, a spoon resting on the glass
    out.append(water_glass(D, 382, 490, 176, 356, w=100))
    out.append(cherry_sweet_dish(D, 236, 504, 134, 357))
    out.append(teaspoon(D, 290, 532, 356, 520, 358))
    # a sprig of jasmine on the tray
    for k, (x, y) in enumerate(((150, 498), (168, 510), (140, 514))):
        for j in range(5):
            a = math.radians(j * 72 + k * 20)
            out.append(f'<path d="{blob(x + math.cos(a) * 5, y + math.sin(a) * 3.4, 5, 3, 360 + k * 5 + j, 0.15, 8, math.degrees(a))}" fill="#FFFFFF"/>')
        out.append(f'<circle cx="{x}" cy="{y}" r="2" fill="#F2D86A"/>')
    out.append(leaf_simple(D, 124, 512, 26, 7, 160, GREEN, 361, vein=False, inkw=1))
    out.append(leaf_simple(D, 174, 520, 22, 6, 20, GREEN, 362, vein=False, inkw=1))
    # lettering
    out.append(gr_ruled(300, 92, "ΦΙΛΟΞΕΝΙΑ", "#F2D08A", size=24, ls=5, line_w=44, gap=14))
    out.append(letters(D, 300, 206, "philoxenia", SERIF_IT, 120, "#FFF6E8", ["#FFFFFF", "#F2E6D0", "#FFF0DC"], 363, max_w=440,
                       shadow="#0A1A44", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(label(300, 250, "a spoon sweet and a glass of cold water", SERIF_IT, 23, "#F2D08A", max_w=430))
    return finish_g(D, out, 364, "#0A1A3A", 0.8)


# ================================================================ 14. siga siga — a cat asleep on whitewashed steps
def tin_pot(D, cx, base, w, h, seed, plant="geranium", paint=("#FFFFFF", "#F2F0EA", "#A8ACB8")):
    """An old olive-oil tin painted white and planted: geraniums or basil."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 6, base, w * 0.7, 5, strength=0.35, seed=seed)]
    if plant == "geranium":
        for k in range(5):
            out.append(geranium_leaf(D, cx + rnd.uniform(-w * 0.6, w * 0.6), base - h - rnd.uniform(6, 22), rnd.uniform(9, 13), seed + k))
        for k, (dx, dy) in enumerate(((-0.25, 1.1), (0.3, 1.25), (0.0, 1.55))):
            out.append(pline([(cx + dx * w * 0.5, base - h), (cx + dx * w, base - h * dy)], "#4A7A2A", 1.6, seed + k, 0.9, 1))
            out.append(geranium(D, cx + dx * w, base - h * dy, rnd.uniform(11, 14), seed + 10 + k))
    else:
        out.append(dab_crown(D, cx, base - h - w * 0.4, w * 0.62, w * 0.5, [GREEN, ("#B8E07A", "#6AAA3A", "#2E6A1E")], seed, n=50, size=(3.5, 6.5), inkw=1))
    body = rect_pts(cx - w / 2, base - h, cx + w / 2, base, 6, seed, 0.5)
    out.append(painted(D, body, paint, seed + 20, sdir=(1, 0.3), sk=0.2, angle=-90, n=8, inkw=1.4, hi=0.4))
    out.append(f'<path d="M {cx - w / 2:.1f} {base - h + 3:.1f} L {cx + w / 2:.1f} {base - h + 3:.1f}" stroke="#8A8A90" stroke-width="1.6" opacity="0.7"/>')
    for _ in range(3):
        x, y = rnd.uniform(cx - w * 0.4, cx + w * 0.4), rnd.uniform(base - h * 0.8, base - 4)
        out.append(f'<path d="{blob(x, y, rnd.uniform(2, 4), rnd.uniform(1.5, 3), rnd.randint(0, 99), 0.3, 8)}" fill="#B86A3A" opacity="0.6"/>')
    return "".join(out)


@design("siga-siga")
def siga_siga():
    D = Doc2("grsg")
    out = [paper(D.nid(), "#FBF6EC", "#7A8AA8", 371)]
    # sunlit whitewashed wall with a blue door at the top of the steps
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 600 L 0 600 Z", (-40, -10, 600, 600), ["#F2EEE6", "#FFFFFF", "#E6E4EA"], 372, n=120, angle=-70,
                       length=(30, 90), width=(5, 12), opacity=(0.15, 0.35)))
    dx0, dy0, dw, dh = 392, 150, 128, 222
    out.append(f'<path d="{hg.org_rect(dx0 - 12, dy0 - 12, dw + 24, dh + 12, 373, 0.6, 12, 2)}" fill="#E4E6EE"/>')
    door = [(dx0, dy0 + dh), (dx0, dy0 + dw / 2), (dx0 + dw / 2, dy0), (dx0 + dw, dy0 + dw / 2), (dx0 + dw, dy0 + dh)]
    dd = f"M {dx0} {dy0 + dh} L {dx0} {dy0 + dw / 2} A {dw / 2} {dw / 2} 0 0 1 {dx0 + dw} {dy0 + dw / 2} L {dx0 + dw} {dy0 + dh} Z"
    out.append(f'<path d="{dd}" fill="{AEGEAN[1]}"/>')
    cid = D.clip(f'<path d="{dd}"/>')
    inner = [strokes(D.nid(), dd, (dx0, dy0, dx0 + dw, dy0 + dh), [AEGEAN[0], AEGEAN[2]], 374, n=40, angle=-90, length=(20, 60), width=(2, 4), opacity=(0.2, 0.45))]
    for k in range(1, 4):
        inner.append(f'<path d="M {dx0 + k * dw / 4:.1f} {dy0} L {dx0 + k * dw / 4:.1f} {dy0 + dh}" stroke="{AEGEAN[2]}" stroke-width="2" opacity="0.6"/>')
    inner.append(f'<path d="M {dx0} {dy0 + dh * 0.55} L {dx0 + dw} {dy0 + dh * 0.55}" stroke="{AEGEAN[2]}" stroke-width="3" opacity="0.6"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(dd, INK, 1.8, 375, 2, 0.7))
    out.append(f'<circle cx="{dx0 + dw * 0.2}" cy="{dy0 + dh * 0.6}" r="4" fill="#C8A048"/>')
    # bougainvillea spilling over the top of the door
    out.append(bougainvillea(D, 470, 132, 120, 46, 376, n=120))
    out.append(bougainvillea(D, 552, 210, 46, 80, 377, n=60))
    # the steps, rising from bottom-left to the door, each with a lit tread and a shaded riser
    steps = []
    for k in range(6):
        x0 = -20 + k * 70
        y = 600 - k * 46
        steps.append((x0, y))
    for k, (x0, y) in enumerate(steps):
        tread = [(x0, y - 46), (620, y - 46), (620, y - 40), (x0 - 4, y - 40)]
        riser = [(x0 - 4, y - 40), (620, y - 40), (620, y + 6), (x0 - 4, y + 6)]
        out.append(f'<path d="{hg.org_poly(riser, 380 + k, 0.6, 14, 1)}" fill="#D2D8E6"/>')
        out.append(f'<path d="{hg.org_poly([(x0 - 4, y - 46), (620, y - 46), (620, y - 30), (x0 - 4, y - 30)], 390 + k, 0.6, 14, 1)}" fill="#FFFFFF"/>')
        out.append(f'<path d="M {x0 - 4} {y - 30} L 620 {y - 30}" stroke="#B8C0D4" stroke-width="2"/>')
        out.append(f'<path d="M {x0 - 4} {y - 46} L {x0 - 4} {y + 6}" stroke="#E8ECF4" stroke-width="3"/>')
    # cool blue shadow of the house next door falling across the lower steps
    out.append(f'<path d="M -20 380 L 150 600 L -20 600 Z" fill="#5A7AB8" opacity="0.22"/>')
    # tins with geraniums and basil on the steps
    out.append(tin_pot(D, 330, 370 - 2, 42, 40, 400, "geranium"))
    out.append(tin_pot(D, 556, 324, 40, 38, 401, "basil"))
    out.append(tin_pot(D, 108, 554 - 0, 38, 36, 402, "basil", paint=("#8AB8E8", "#3A78C8", "#1E4A8A")))
    out.append(tin_pot(D, 248, 462, 44, 42, 403, "geranium", paint=("#F8C0A0", "#E8885A", "#A8502A")))
    # the cat, curled up in the sun on a step
    out.append(cat(D, 200, 508, 150, 404, pose="curl"))
    out.append(f'<text x="190" y="420" {SERIF_IT} font-size="24" fill="#5A6A8A" opacity="0.8">z</text><text x="208" y="400" {SERIF_IT} font-size="18" fill="#5A6A8A" opacity="0.7">z</text>')
    # lettering, upper left
    out.append(letters(D, 196, 150, "siga", SERIF_IT, 118, "#1F4FA0", ["#2E62B8", "#14347A", "#3A72C8"], 405, max_w=260,
                       shadow="#D8E2F2", soff=(0.02, 0.035), angle=-40, hi="#9AB8F0"))
    out.append(letters(D, 236, 246, "siga", SERIF_IT, 118, "#1F4FA0", ["#2E62B8", "#14347A", "#3A72C8"], 406, max_w=260,
                       shadow="#D8E2F2", soff=(0.02, 0.035), angle=-40, hi="#9AB8F0"))
    out.append(label(206, 290, "SLOWLY, SLOWLY", JOS, 19, "#B8401E", ls=5, max_w=260))
    return finish_g(D, out, 407, "#3A4A6A", 0.8)


# ================================================================ 15. kefi — the bouzouki on the taverna chair
def kafeneio_chair(D, x, base, s, seed, pal=AEGEAN, view="front", rush=("#F2D488", "#C89A48", "#7A5A22")):
    """The classic Greek kafeneio chair in a slight perspective: square-legged painted wood, two curved back rails,
    a woven rush seat with its four triangular panels. view='front' (seat towards us) or 'back' (we see its back,
    as if it faces the view)."""
    def P(px, py):
        return (x + px * s, base + py * s)
    lw = max(3, s * 0.055)
    out = []

    def bar(p0, p1, w, col):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L * w / 2, dx / L * w / 2
        return f'<path d="{pd([(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)])}" fill="{col}"/>'

    def leg(px, top_y, bot_y, sd):
        a_, b_ = P(px, top_y), P(px, bot_y)
        return painted(D, rect_pts(a_[0] - lw / 2, a_[1], b_[0] + lw / 2, b_[1], 10, sd, 0.3), pal, sd, sdir=(1, 0), sk=0.25, angle=-90, n=5, inkw=1.1, hi=0.3)

    def rails(near):
        r = []
        k = 1.0 if near else 0.82
        y_off = 0 if near else -0.1
        for py in (-1.02, -0.84):
            yy = py + y_off
            r.append(taper([P(-0.36 * k, yy + 0.02), P(0, yy - 0.025), P(0.36 * k, yy + 0.02)], s * 0.075, s * 0.075, pal[1]))
            r.append(taper([P(-0.34 * k, yy - 0.004), P(0, yy - 0.045), P(0.34 * k, yy - 0.004)], s * 0.02, s * 0.02, pal[0], 0.8))
            r.append(ink(smooth_open([P(-0.37 * k, yy + 0.055), P(0, yy + 0.012), P(0.37 * k, yy + 0.055)]), INK, 1, seed, 1, 0.5))
        return "".join(r)

    def seat(far_y, near_y, far_w, near_w):
        q = [P(-far_w, far_y), P(far_w, far_y), P(near_w, near_y), P(-near_w, near_y)]
        d = pd(q)
        r = [f'<path d="{d}" fill="{rush[1]}"/>']
        cid = D.clip(f'<path d="{d}"/>')
        c = P(0, (far_y + near_y) / 2)
        w = []
        for k in range(1, 9):
            t = k / 9
            ring = [(c[0] + (p[0] - c[0]) * t, c[1] + (p[1] - c[1]) * t) for p in q]
            w.append(f'<path d="{pd(ring)}" fill="none" stroke="{rush[2] if k % 2 else rush[0]}" stroke-width="{max(1.2, s * 0.012):.1f}" opacity="0.8"/>')
        for p in q:
            w.append(f'<path d="M {c[0]:.1f} {c[1]:.1f} L {p[0]:.1f} {p[1]:.1f}" stroke="{rush[2]}" stroke-width="1.4"/>')
        w.append(shade_over(D, d, "#3A2A10", 0.3, 0, 0, 0, 1, 0.4))
        r.append(f'<g {cid}>{"".join(w)}</g>')
        r.append(ink(d, INK, 1.2, seed, 1, 0.6))
        r.append(bar(P(-near_w - 0.02, near_y), P(near_w + 0.02, near_y), lw * 0.9, pal[1]))
        return "".join(r)

    if view == "front":
        out.append(leg(-0.3, -1.08, -0.1, seed + 1) + leg(0.3, -1.08, -0.1, seed + 2))
        out.append(rails(near=False).replace("", "") if False else "")
        for py in (-1.12, -0.94):
            out.append(taper([P(-0.32, py + 0.02), P(0, py - 0.02), P(0.32, py + 0.02)], s * 0.07, s * 0.07, pal[1]))
            out.append(taper([P(-0.3, py), P(0, py - 0.036), P(0.3, py)], s * 0.018, s * 0.018, pal[0], 0.8))
            out.append(ink(smooth_open([P(-0.33, py + 0.05), P(0, py + 0.012), P(0.33, py + 0.05)]), INK, 1, seed, 1, 0.5))
        out.append(seat(-0.6, -0.44, 0.33, 0.42))
        out.append(leg(-0.4, -0.44, 0.04, seed + 3) + leg(0.4, -0.44, 0.04, seed + 4))
        out.append(bar(P(-0.38, -0.16), P(0.38, -0.16), lw * 0.7, pal[1]))
    else:
        out.append(leg(-0.32, -0.6, -0.1, seed + 3) + leg(0.32, -0.6, -0.1, seed + 4))
        out.append(bar(P(-0.3, -0.24), P(0.3, -0.24), lw * 0.6, pal[2]))
        out.append(seat(-0.6, -0.46, 0.32, 0.41))
        out.append(leg(-0.4, -1.04, 0.04, seed + 1) + leg(0.4, -1.04, 0.04, seed + 2))
        out.append(bar(P(-0.38, -0.16), P(0.38, -0.16), lw * 0.7, pal[1]))
        out.append(rails(near=True))
    return "".join(out)


def bouzouki(D, cx, cy, s, seed, rot_=0):
    """Bouzouki, front view: pear-shaped body with a pick guard, soundhole rosette with mother-of-pearl inlay,
    long fretted neck and a scrolled headstock with eight pegs. (cx, cy) = centre of the bowl; s = bowl width."""
    out = [f'<g transform="rotate({rot_} {cx} {cy})">']
    w, h = s, s * 1.18
    neck_top = cy - h * 0.5 - s * 1.6
    # neck and headstock
    out.append(painted(D, rect_pts(cx - s * 0.075, neck_top, cx + s * 0.075, cy - h * 0.3, 8, seed, 0.3), ("#5A3A22", "#3A2414", "#1A0E06"), seed, sdir=(1, 0), sk=0.2, angle=-90, n=10, inkw=1.2, hi=0.3))
    for k in range(18):
        y = cy - h * 0.34 - (k ** 0.9) * s * 0.1
        if y < neck_top + 6:
            break
        out.append(f'<path d="M {cx - s * 0.075:.1f} {y:.1f} L {cx + s * 0.075:.1f} {y:.1f}" stroke="#D8D8D8" stroke-width="1.3"/>')
        if k in (3, 5, 7, 9, 12):
            out.append(f'<circle cx="{cx:.1f}" cy="{y + s * 0.04:.1f}" r="{s * 0.014:.1f}" fill="#F8F2E8"/>')
    head = [(cx - s * 0.1, neck_top + 4), (cx - s * 0.12, neck_top - s * 0.34), (cx - s * 0.06, neck_top - s * 0.46), (cx + s * 0.06, neck_top - s * 0.46),
            (cx + s * 0.12, neck_top - s * 0.34), (cx + s * 0.1, neck_top + 4)]
    out.append(painted(D, head, ("#7A4E2A", "#4A2E16", "#1E1006"), seed + 1, sk=0.2, n=8, inkw=1.4, hi=0.3))
    for k in range(4):
        y = neck_top - s * 0.06 - k * s * 0.09
        for sg in (-1, 1):
            out.append(f'<path d="{blob(cx + sg * s * 0.17, y, s * 0.045, s * 0.022, seed + k * 2 + sg, 0.1, 8)}" fill="#F2EAD8"/>')
            out.append(f'<path d="M {cx + sg * s * 0.1:.1f} {y:.1f} L {cx + sg * s * 0.14:.1f} {y:.1f}" stroke="#C8A048" stroke-width="2"/>')
    # body
    body = []
    for i in range(36):
        a = 2 * math.pi * i / 36
        bx = w / 2 * math.sin(a)
        by = -h / 2 * math.cos(a)
        k = 1 - 0.32 * max(0, -math.cos(a)) ** 1.5
        body.append((cx + bx * k, cy + by))
    out.append(painted(D, body, ("#F2D8A8", "#D8AA6A", "#8A5A2A"), seed + 2, sdir=(0.6, 0.6), sk=0.15, angle=-90, n=40, slen=(10, 40), sw=(1, 3),
                       cols=["#F8E2B8", "#B8823E", "#E8C080"], inkw=1.8, hi=0.45))
    bd = smooth_closed(body)
    cid = D.clip(f'<path d="{bd}"/>')
    inner = []
    # pick guard (dark, teardrop) and the inlaid rosette
    inner.append(f'<path d="{smooth_closed([(cx - w * 0.06, cy + h * 0.06), (cx - w * 0.36, cy + h * 0.18), (cx - w * 0.3, cy + h * 0.38), (cx - w * 0.08, cy + h * 0.36)])}" fill="#2A1A10" opacity="0.85"/>')
    rr = w * 0.17
    sy = cy - h * 0.1
    for k, (r_, col) in enumerate(((rr * 1.55, "#1E3E3A"), (rr * 1.4, "#F2EAD8"), (rr * 1.28, "#2A6A5A"), (rr * 1.16, "#F2EAD8"))):
        inner.append(f'<circle cx="{cx:.1f}" cy="{sy:.1f}" r="{r_:.1f}" fill="{col}"/>')
    for i in range(16):
        a = 2 * math.pi * i / 16
        inner.append(f'<circle cx="{cx + math.cos(a) * rr * 1.47:.1f}" cy="{sy + math.sin(a) * rr * 1.47:.1f}" r="{rr * 0.07:.1f}" fill="#F8F4EC"/>')
    inner.append(f'<circle cx="{cx:.1f}" cy="{sy:.1f}" r="{rr:.1f}" fill="#1A0E06"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # bridge, tailpiece and strings
    out.append(f'<rect x="{cx - w * 0.14:.1f}" y="{cy + h * 0.24:.1f}" width="{w * 0.28:.1f}" height="{s * 0.03:.1f}" fill="#2A1A10"/>')
    out.append(f'<path d="{pd([(cx - w * 0.07, cy + h * 0.38), (cx + w * 0.07, cy + h * 0.38), (cx + w * 0.05, cy + h * 0.48), (cx - w * 0.05, cy + h * 0.48)])}" fill="#C8C8CC"/>')
    for k in range(4):
        x = cx - s * 0.045 + k * s * 0.03
        out.append(f'<path d="M {x:.1f} {neck_top - 2:.1f} L {x + (k - 1.5) * 0.6:.1f} {cy + h * 0.4:.1f}" stroke="#F4F4F0" stroke-width="1" opacity="0.9"/>')
    out.append(taper([(cx - w * 0.36, cy - h * 0.1), (cx - w * 0.42, cy + h * 0.1), (cx - w * 0.36, cy + h * 0.3)], 5, 2, "#FFF4D8", 0.6))
    out.append("</g>")
    return "".join(out)


@design("kefi")
def kefi():
    D = Doc2("grkp")
    # taverna at night: warm ochre wall, a lamp, lights
    out = [sky(D, [(0, "#3A2A5A"), (0.35, "#7A3A4A"), (1, "#C8763A")], 411, 600, ["#8A4A4A", "#4A2A5A", "#D8864A"], 90, angle=-80, sop=(0.06, 0.14))]
    out.append(soft_glow(D, 300, 330, 320, "#FFC870", 0.5))
    out.append(string_lights(D, -20, 46, 620, 40, 52, 10, 412))
    # floor of terracotta tiles
    rnd = random.Random(413)
    out.append(f'<rect y="500" width="600" height="110" fill="#B8603A"/>')
    for row in range(4):
        y = 500 + row * 28
        for col in range(-1, 9):
            x = col * 76 + (38 if row % 2 else 0) - row * 6
            out.append(f'<path d="{hg.org_rect(x + 2, y + 2, 72, 24, int(x * 7 + y), 0.8, 12, 2)}" fill="{rnd.choice(["#C8704A", "#B86040", "#D07E52", "#A85636"])}"/>')
    out.append(f'<rect y="500" width="600" height="110" fill="{D.lin([(0, "#2A0E06", 0.5), (1, "#2A0E06", 0.1)])}"/>')
    # small table at right with a carafe of wine and a glass
    out.append(cast(D, 470, 548, 90, 10, strength=0.4, seed=414))
    out.append(painted(D, rect_pts(386, 430, 576, 446, 10, 415, 0.4), AEGEAN, 415, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.3))
    for x in (400, 562):
        out.append(painted(D, rect_pts(x - 4, 446, x + 4, 548, 10, 416 + x, 0.3), AEGEAN, 416 + x, sdir=(1, 0), sk=0.25, angle=-90, n=4, inkw=1, hi=0.3))
    out.append(wine_glass(D, 440, 430, 66, 417, fill=0.5))
    car = [(498, 430), (490, 400), (500, 372), (504, 348), (520, 348), (524, 372), (534, 400), (526, 430)]
    out.append(f'<path d="{smooth_closed(car)}" fill="#E8F0E8" opacity="0.5"/>')
    out.append(f'<path d="{smooth_closed([(500, 428), (492, 402), (500, 384), (524, 384), (532, 402), (524, 428)])}" fill="#8A1424" opacity="0.9"/>')
    out.append(ink(smooth_closed(car), "#6A7A70", 1.4, 418, 1, 0.75))
    out.append(taper([(500, 420), (496, 396), (504, 364)], 3, 1, "#FFFFFF", 0.8))
    # chair with the bouzouki leaning on it
    out.append(cast(D, 206, 552, 130, 12, strength=0.45, seed=419))
    out.append(kafeneio_chair(D, 200, 552, 230, 420))
    out.append(bouzouki(D, 214, 430, 130, 421, rot_=-26))
    # music in the air (no lyrics, just notes)
    for k, (x, y, s_) in enumerate(((330, 330, 18), (372, 302, 14), (90, 300, 15), (520, 320, 13), (70, 400, 12))):
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{s_ * 0.45:.1f}" ry="{s_ * 0.32:.1f}" fill="#FFE8B0" transform="rotate(-20 {x} {y})"/>')
        out.append(f'<path d="M {x + s_ * 0.4:.1f} {y} L {x + s_ * 0.4:.1f} {y - s_ * 1.4:.1f} q {s_ * 0.3:.1f} {s_ * 0.3:.1f} {s_ * 0.6:.1f} {s_ * 0.3:.1f}" stroke="#FFE8B0" stroke-width="2.2" fill="none"/>')
    out.append(letters(D, 398, 200, "kefi", SERIF_IT, 160, "#FFF2D8", ["#FFFFFF", "#FFE6C0", "#FFF4E0"], 422, max_w=280,
                       shadow="#2A0E1A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(label(398, 244, "THE JOY THAT", JOS, 19, "#FFD898", ls=4, max_w=260))
    out.append(label(398, 270, "MAKES YOU DANCE", JOS, 19, "#FFD898", ls=4, max_w=260))
    return finish_g(D, out, 423, "#2A0E1A", 0.8)


# ================================================================ 16. agapi mou — two chairs facing the sunset
@design("agapi-mou")
def agapi_mou():
    D = Doc2("grag")
    out = [sky(D, [(0, "#E86A8A"), (0.35, "#F49A8A"), (0.62, "#FFC88E"), (0.7, "#FFE0A8")], 431, 360, ["#F8A8A0", "#FFD0A0", "#E8708A"], 60, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 300, 336, 230, "#FFE6A8", 0.7))
    out.append(f'<path d="M 262 340 A 38 38 0 0 1 338 340 Z" fill="#FFF0C8"/>')
    for x, y, w in ((110, 210, 110), (500, 240, 90)):
        out.append(puff_cloud(D, x, y, w, 432 + x, pal=("#FFE0D8", "#F2A8A8", "#C87890"), op=0.8, rows=1))
    out.append(sea(D, 340, 470, [(0, "#F2A8A0"), (0.25, "#B87AA0"), (1, "#4A4A8A")], 433, ["#FFD8B0", "#8A6A9A", "#FFB8A8"], 70))
    for k in range(10):
        y = 346 + k * 10
        w = 50 - k * 3.5
        out.append(taper([(300 - w, y), (300, y + 1), (300 + w, y)], 1, 3.4, "#FFE6A8", 0.85 - k * 0.07))
    out.append(f'<path d="{smooth_open(ridge([(-20, 342), (60, 326), (130, 330), (180, 342)], 434, 4, 3))} L 180 344 L -20 344 Z" fill="#A8708A"/>')
    out.append(f'<path d="{smooth_open(ridge([(440, 342), (520, 330), (620, 334)], 435, 4, 3))} L 620 344 L 440 344 Z" fill="#9A6A8A"/>')
    # whitewashed terrace parapet and floor
    out.append(painted(D, rect_pts(-10, 456, 620, 486, 8, 436, 0.4), WASH_W, 436, sdir=(0, 1), sk=0.1, angle=0, n=30, inkw=1.4, hi=0.3))
    out.append(f'<rect x="-10" y="486" width="620" height="130" fill="#F2E2D2"/>')
    out.append(f'<rect x="-10" y="486" width="620" height="130" fill="{D.lin([(0, "#C87A7A", 0.35), (1, "#C87A7A", 0.0)])}"/>')
    rnd = random.Random(437)
    for k in range(12):   # flagstone joints
        x = rnd.uniform(0, 600)
        out.append(f'<path d="M {x:.1f} 488 L {x + (x - 300) * 0.4:.1f} 610" stroke="#D8C0B0" stroke-width="2" opacity="0.7"/>')
    for y in (520, 566):
        out.append(f'<path d="M -10 {y} L 610 {y}" stroke="#D8C0B0" stroke-width="2" opacity="0.6"/>')
    # two chairs, side by side, leaning in a little
    out.append(cast(D, 300, 566, 170, 14, strength=0.35, seed=438))
    out.append(f'<g transform="rotate(-3 196 566)">{kafeneio_chair(D, 196, 566, 158, 439, view="back")}</g>')
    out.append(f'<g transform="rotate(3 404 566)">{kafeneio_chair(D, 404, 566, 158, 440, view="back")}</g>')
    # a little heart rising between them
    out.append(p_heart(D, 300, 420, 18, RED, 441))
    out.append(sparkle(330, 402, 7, "#FFFFFF", 0.9))
    out.append(sparkle(272, 436, 5, "#FFFFFF", 0.8))
    out.append(f'<path d="{smooth_open([(300, 438), (292, 456), (304, 472), (296, 488)])}" fill="none" stroke="#FFFFFF" stroke-width="1.6" stroke-dasharray="3 5" opacity="0.7"/>')
    # bougainvillea at the corners
    out.append(bougainvillea(D, 30, 446, 60, 40, 442, n=50))
    out.append(bougainvillea(D, 574, 440, 56, 44, 443, n=50))
    # lettering
    out.append(gr_ruled(300, 88, "ΑΓΑΠΗ ΜΟΥ", "#FFFFFF", size=24, ls=5, line_w=40, gap=14))
    out.append(letters(D, 300, 196, "agapi mou", SERIF_IT, 120, "#FFFFFF", ["#FFFFFF", "#FFE8E8", "#FFF2F0"], 444, max_w=440,
                       shadow="#A8304A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(label(300, 238, "my love", SERIF_IT, 26, "#8A1E3A", max_w=300))
    return finish_g(D, out, 445, "#3A1A2A", 0.8)


# ================================================================ 17. kalimera — the rooster on the village wall at sunrise
def rooster(D, ox, oy, s, seed):
    """A village rooster crowing, facing right, head thrown back: arching dark-green sickle tail, rust body, golden
    hackle cape, scalloped wing, red comb and wattles. (ox, oy) = feet on the wall."""
    def L(pts):
        return [(ox + x * s, oy + y * s) for x, y in pts]
    out = []
    # tail: long arching sickles, darkest at the back
    tails = [([(-44, -70), (-62, -118), (-92, -150), (-122, -138), (-128, -104)], 13, "#0E3A2A"),
             ([(-46, -72), (-58, -126), (-80, -164), (-108, -166), (-118, -140)], 12, "#145040"),
             ([(-44, -66), (-70, -104), (-100, -116), (-120, -96)], 12, "#1E6A4A"),
             ([(-42, -74), (-48, -120), (-62, -150), (-84, -158)], 10, "#2A7A5A"),
             ([(-44, -62), (-74, -84), (-104, -80), (-118, -64)], 10, "#103A2E")]
    for k, (pts, w, col) in enumerate(tails):
        path = catmull(L(pts), 8)
        out.append(taper(path, w * s, 2.5 * s, col))
        out.append(taper([(x - 1.5 * s, y - 1.5 * s) for x, y in path[:len(path) * 2 // 3]], 2.4 * s, 0.6 * s, "#6AC0A0", 0.55))
    out.append(ink(smooth_open(catmull(L(tails[1][0]), 6)), "#06180E", 1, seed, 1, 0.4))
    # legs
    for dx in (-6, 10):
        out.append(pline(L([(dx, -32), (dx + 1, -14), (dx + 2, 0)]), "#E8B040", 3.4 * s, seed + dx, 1, 1))
        out.append(pline(L([(dx - 8, 2), (dx + 2, 0), (dx + 11, 2)]), "#E8B040", 2.4 * s, seed + dx + 1, 1, 1))
        out.append(pline(L([(dx + 2, 0), (dx - 2, 3)]), "#C8902A", 2 * s, seed + dx + 2, 1, 1))
    # body
    body = L([(-50, -60), (-44, -82), (-20, -96), (14, -98), (40, -84), (46, -60), (30, -36), (2, -28), (-28, -36)])
    out.append(painted(D, body, ("#E8884A", "#B4462A", "#5E1A0E"), seed + 3, sdir=(0.4, 0.9), sk=0.2, angle=-20, n=36, inkw=1.6, hi=0.4))
    bd = smooth_closed(body)
    cid = D.clip(f'<path d="{bd}"/>')
    rnd = random.Random(seed)
    fl = "".join(f'<path d="M {ox + rnd.uniform(-40, 40) * s:.1f} {oy + rnd.uniform(-90, -36) * s:.1f} q {2 * s:.1f} {4 * s:.1f} {6 * s:.1f} {2 * s:.1f}" stroke="#4A1408" stroke-width="{1.2 * s:.1f}" fill="none" opacity="0.5"/>' for _ in range(26))
    out.append(f'<g {cid}>{fl}<path d="{blob(ox + 34 * s, oy - 58 * s, 16 * s, 22 * s, seed, 0.1, 10)}" fill="#3A0E06" opacity="0.35"/></g>')
    # wing with a scalloped trailing edge
    wing = [(-30, -66), (-14, -84), (12, -88), (26, -74), (20, -58)]
    for k in range(5):
        t = k / 4
        wing.append((20 - t * 52 + 3, -54 + t * 6 + (4 if k % 2 else 0)))
    out.append(painted(D, L(wing), ("#C8603A", "#8A2C16", "#3E1006"), seed + 4, sdir=(0.4, 0.9), sk=0.2, angle=-10, n=14, inkw=1.4, hi=0.35))
    for k in range(4):
        out.append(pline(L([(-22 + k * 11, -72), (-26 + k * 11, -56)]), "#E8A070", 1.4 * s, seed + k, 0.5, 1))
    # golden hackle cape over the shoulders, pointed feather tips
    cape = [(16, -152), (32, -158), (44, -144), (46, -116), (50, -92)]
    for k in range(7):
        t = k / 6
        cape.append((50 - t * 52, -92 + (8 if k % 2 else 0) - t * 6))
    cape += [(-6, -108), (8, -132)]
    out.append(painted(D, L(cape), ("#FFE09A", "#F0A848", "#A8601A"), seed + 5, sdir=(0.4, 0.9), sk=0.15, angle=80, n=26, inkw=1.4, hi=0.45))
    for k in range(7):
        out.append(taper(L([(4 + k * 6.5, -130 + k * 3), (2 + k * 7, -96 + (4 if k % 2 else 0))]), 2.6 * s, 0.6 * s, "#C8782A", 0.6))
    # head thrown back, beak open to the sky
    hx, hy = ox + 32 * s, oy - 160 * s
    head = blob_pts(hx, hy, 12 * s, 11 * s, seed + 6, 0.05, 12)
    out.append(painted(D, head, ("#FFD08A", "#E8983A", "#A8601A"), seed + 6, sk=0.15, n=6, inkw=1.4, hi=0.4))
    comb = L([(18, -166), (16, -180), (24, -176), (26, -190), (33, -180), (38, -190), (42, -178), (46, -170), (40, -164), (24, -162)])
    out.append(painted(D, comb, ("#FF6A5A", "#E0201E", "#8A0A0A"), seed + 7, sk=0.15, n=8, inkw=1.2, hi=0.4))
    out.append(f'<path d="{pd(L([(42, -166), (58, -180), (46, -160)]))}" fill="#F2C040"/>' + ink(pd(L([(42, -166), (58, -180), (46, -160)])), INK, 1, seed, 1, 0.5))
    out.append(f'<path d="{pd(L([(44, -156), (60, -160), (45, -152)]))}" fill="#D8A030"/>')
    out.append(painted(D, L([(38, -152), (46, -150), (46, -138), (39, -140)]), ("#FF6A5A", "#E0201E", "#8A0A0A"), seed + 8, sk=0.1, n=3, inkw=1, hi=0.3))
    out.append(f'<circle cx="{hx + 4 * s:.1f}" cy="{hy - 3 * s:.1f}" r="{2.4 * s:.1f}" fill="#2A1A08"/><circle cx="{hx + 3.4 * s:.1f}" cy="{hy - 3.6 * s:.1f}" r="{0.8 * s:.1f}" fill="#FFFFFF"/>')
    return "".join(out)


@design("kalimera")
def kalimera():
    D = Doc2("grkl")
    out = [sky(D, [(0, "#7AB8E8"), (0.4, "#BEDCF0"), (0.7, "#FFE2B8"), (0.82, "#FFD08A")], 451, 380, ["#C8E4F4", "#FFE8C8"], 60, sop=(0.05, 0.12))]
    out.append(soft_glow(D, 430, 360, 220, "#FFE6A0", 0.8))
    out.append(f'<path d="M 386 372 A 44 44 0 0 1 474 372 Z" fill="#FFF2C0"/>')
    for k in range(9):
        a = math.radians(-170 + k * 20)
        out.append(taper([(430 + math.cos(a) * 60, 372 + math.sin(a) * 60), (430 + math.cos(a) * 110, 372 + math.sin(a) * 110)], 6, 1, "#FFF4C8", 0.45))
    out.append(sea(D, 370, 470, [(0, "#FFE0A8"), (0.3, "#8AB0D8"), (1, "#3A6AB0")], 452, ["#FFF2C8", "#5A8AC8"], 60))
    for k in range(8):
        y = 376 + k * 10
        w = 46 - k * 4
        out.append(taper([(430 - w, y), (430, y + 1), (430 + w, y)], 1, 3.2, "#FFF0B8", 0.85 - k * 0.08))
    out.append(f'<path d="{smooth_open(ridge([(-20, 372), (80, 352), (180, 360), (240, 372)], 453, 5, 3))} L 240 376 L -20 376 Z" fill="#8AA0C8"/>')
    # whitewashed village wall across the bottom with its rounded coping
    wall_top = 470
    out.append(painted(D, rect_pts(-10, wall_top, 620, 620, 10, 454, 0.4), WASH, 454, sdir=(0.3, 1), sk=0.06, angle=-4, n=60, inkw=0, hi=0.3))
    out.append(f'<path d="{smooth_open([(-10, wall_top + 2), (150, wall_top - 4), (300, wall_top), (460, wall_top - 5), (620, wall_top + 1)])} L 620 {wall_top + 14} L -10 {wall_top + 14} Z" fill="#FFFFFF"/>')
    out.append(f'<path d="M -10 {wall_top + 16} L 620 {wall_top + 16}" stroke="#B8C4DA" stroke-width="4" opacity="0.8"/>')
    out.append(f'<path d="M -10 {wall_top + 20} L 620 {wall_top + 20} L 620 {wall_top + 60} L -10 {wall_top + 60} Z" fill="#9AB0D8" opacity="0.18"/>')
    # pots of basil and a geranium tin on the wall
    out.append(tin_pot(D, 96, wall_top + 2, 46, 42, 455, "basil"))
    out.append(tin_pot(D, 520, wall_top + 2, 44, 40, 456, "geranium", paint=("#8AB8E8", "#3A78C8", "#1E4A8A")))
    # the rooster crowing to the sun
    out.append(cast(D, 300, wall_top + 2, 46, 6, strength=0.3, seed=457))
    out.append(rooster(D, 300, wall_top, 1.42, 458))
    # little sound marks from the beak
    for k in range(3):
        bx, by = 398 + k * 12, 214 - k * 10
        out.append(pline([(bx - 6, by + 4), (bx, by - 4), (bx + 8, by - 6)], "#C8501E", 2.4, 459 + k, 0.8, 1))
    for x, y in ((150, 230), (180, 246), (520, 210)):
        out.append(bird_v(x, y, 8, "#4A5A7A", 0.8))
    # lettering
    out.append(letters(D, 300, 140, "Kalimera!", SERIF_IT, 124, "#C84A1A", ["#E06A2A", "#9A300E", "#F08A40"], 460, max_w=440,
                       shadow="#FFF4E0", soff=(0.02, 0.035), angle=-40, hi="#FFC890"))
    out.append(gr_ruled(300, 186, "ΚΑΛΗΜΕΡΑ", "#1F4FA0", size=22, ls=5, line_w=30, gap=12))
    out.append(label(300, 548, "GOOD MORNING", JOS, 22, "#1F4FA0", ls=8))
    return finish_g(D, out, 461)


# ================================================================ 18. athina — the Parthenon at dawn
def parthenon(D, x0, base, w, seed, light=(-0.8, -0.3)):
    """The Parthenon in 3/4 view from the north-west: stepped base, the west front of eight Doric columns, the long
    north colonnade receding, entablature with triglyphs, a broken pediment. Warm marble lit from the left."""
    out = []
    marble = ("#FFF0D8", "#E8C8A0", "#A88A6A")
    shade = ("#E8C8B0", "#C0A08A", "#7A6050")
    fw = w * 0.42                      # front width
    side_dx, side_dy = w * 0.58, -w * 0.07   # direction of the north side receding to the right
    h = w * 0.2                        # column height
    # stylobate steps
    for k in range(3):
        y = base - k * 5
        front = [(x0 - 6 + k * 3, y), (x0 + fw + 6 - k * 3, y), (x0 + fw + 6 - k * 3, y - 5), (x0 - 6 + k * 3, y - 5)]
        out.append(f'<path d="{pd(front)}" fill="{marble[1]}"/>')
        side = [(x0 + fw + 6 - k * 3, y), (x0 + fw + side_dx + 6 - k * 3, y + side_dy), (x0 + fw + side_dx + 6 - k * 3, y + side_dy - 5), (x0 + fw + 6 - k * 3, y - 5)]
        out.append(f'<path d="{pd(side)}" fill="{shade[1]}"/>')
        out.append(f'<path d="M {front[3][0]:.1f} {front[3][1]:.1f} L {front[2][0]:.1f} {front[2][1]:.1f} L {side[2][0]:.1f} {side[2][1]:.1f}" stroke="{marble[0]}" stroke-width="1.4"/>')
    top_y = base - 15
    # cella wall behind the side colonnade (shadow)
    cw = [(x0 + fw, top_y - h), (x0 + fw + side_dx, top_y - h + side_dy), (x0 + fw + side_dx, top_y + side_dy), (x0 + fw, top_y)]
    out.append(f'<path d="{pd(cw)}" fill="#8A6A5A"/>')
    # north colonnade receding (columns get slimmer and closer)
    n_side = 12
    for i in range(n_side, 0, -1):
        t = i / n_side
        cx = x0 + fw + side_dx * t - 4
        cy = top_y + side_dy * t
        cwid = w * 0.028 * (1 - 0.25 * t)
        col = [(cx - cwid / 2, cy), (cx - cwid * 0.42, cy - h), (cx + cwid * 0.42, cy - h), (cx + cwid / 2, cy)]
        out.append(f'<path d="{pd(col)}" fill="{shade[1]}"/>')
        out.append(f'<path d="M {cx - cwid * 0.2:.1f} {cy:.1f} L {cx - cwid * 0.15:.1f} {cy - h:.1f}" stroke="{marble[0]}" stroke-width="1.2" opacity="0.7"/>')
        out.append(f'<path d="M {cx + cwid * 0.3:.1f} {cy:.1f} L {cx + cwid * 0.26:.1f} {cy - h:.1f}" stroke="{shade[2]}" stroke-width="1" opacity="0.6"/>')
    # west front: eight columns with fluting and light
    n = 8
    gap = fw / n
    for i in range(n):
        cx = x0 + gap * (i + 0.5)
        cwid = gap * 0.62
        col = [(cx - cwid / 2, top_y), (cx - cwid * 0.42, top_y - h), (cx + cwid * 0.42, top_y - h), (cx + cwid / 2, top_y)]
        out.append(painted(D, poly_pts(col, 6, seed + i, 0.3), marble, seed + i, sdir=(-light[0], 0), sk=0.25, angle=-90, n=6, inkw=1, inkop=0.45, hi=0.4))
        for f in (-0.25, 0, 0.25):
            out.append(f'<path d="M {cx + f * cwid:.1f} {top_y - 2:.1f} L {cx + f * cwid * 0.84:.1f} {top_y - h + 4:.1f}" stroke="{marble[2]}" stroke-width="1" opacity="0.45"/>')
        out.append(f'<path d="{pd([(cx - cwid * 0.62, top_y - h), (cx + cwid * 0.62, top_y - h), (cx + cwid * 0.5, top_y - h + 5), (cx - cwid * 0.5, top_y - h + 5)])}" fill="{marble[0]}"/>')
    # entablature: architrave, frieze with triglyphs, cornice — front and side
    eh = h * 0.32
    ey = top_y - h
    ent_f = [(x0 - 4, ey), (x0 + fw + 4, ey), (x0 + fw + 4, ey - eh), (x0 - 4, ey - eh)]
    ent_s = [(x0 + fw + 4, ey), (x0 + fw + side_dx + 4, ey + side_dy), (x0 + fw + side_dx + 4, ey + side_dy - eh), (x0 + fw + 4, ey - eh)]
    out.append(painted(D, poly_pts(ent_f, 8, seed + 20, 0.3), marble, seed + 20, sdir=(0, 1), sk=0.1, angle=0, n=10, inkw=1, inkop=0.45, hi=0.3))
    out.append(f'<path d="{pd(ent_s)}" fill="{shade[1]}"/>')
    for i in range(16):
        tx = x0 + 2 + i * fw / 16
        out.append(f'<rect x="{tx:.1f}" y="{ey - eh * 0.82:.1f}" width="{fw / 40:.1f}" height="{eh * 0.4:.1f}" fill="{marble[2]}" opacity="0.6"/>')
    for i in range(28):
        t = i / 28
        tx, ty = x0 + fw + 6 + side_dx * t, ey + side_dy * t
        out.append(f'<rect x="{tx:.1f}" y="{ty - eh * 0.82:.1f}" width="{fw / 60:.1f}" height="{eh * 0.4:.1f}" fill="{shade[2]}" opacity="0.6"/>')
    out.append(f'<path d="M {x0 - 4:.1f} {ey - eh * 0.4:.1f} L {x0 + fw + 4:.1f} {ey - eh * 0.4:.1f} L {x0 + fw + side_dx + 4:.1f} {ey - eh * 0.4 + side_dy:.1f}" stroke="{marble[2]}" stroke-width="1.2" fill="none" opacity="0.7"/>')
    # broken pediment over the west front
    py = ey - eh
    ped = [(x0 - 8, py), (x0 + fw * 0.08, py - fw * 0.03), (x0 + fw * 0.14, py - fw * 0.025), (x0 + fw * 0.2, py - fw * 0.06), (x0 + fw * 0.5, py - fw * 0.13),
           (x0 + fw * 0.62, py - fw * 0.1), (x0 + fw * 0.7, py - fw * 0.095), (x0 + fw * 0.84, py - fw * 0.04), (x0 + fw + 8, py)]
    out.append(painted(D, ped, marble, seed + 30, sdir=(0.6, 0.6), sk=0.1, angle=-20, n=8, inkw=1, inkop=0.5, hi=0.3))
    out.append(f'<path d="{pd([(x0 + fw + 8, py), (x0 + fw + side_dx + 8, py + side_dy), (x0 + fw + side_dx + 8, py + side_dy + 4), (x0 + fw + 8, py + 4)])}" fill="{shade[0]}"/>')
    out.append(ink(pd(ent_f), INK, 1, seed, 1, 0.35))
    return "".join(out)


@design("athina")
def athina():
    D = Doc2("grat")
    out = [sky(D, [(0, "#6A7AB8"), (0.35, "#C8A0C0"), (0.6, "#F8C8A8"), (0.78, "#FFE2B0")], 471, 470, ["#E8B8C0", "#FFE0C0", "#9A90C8"], 60, sop=(0.05, 0.14))]
    out.append(soft_glow(D, 80, 380, 260, "#FFE4A8", 0.75))
    for x, y, w in ((470, 120, 130), (150, 250, 100)):
        out.append(puff_cloud(D, x, y, w, 472 + x, pal=("#FFE8DC", "#F2B8B0", "#B888A8"), op=0.75, rows=1))
    # Lycabettus and the city haze far behind
    out.append(f'<path d="{smooth_open(ridge([(380, 470), (440, 420), (468, 396), (500, 420), (620, 450)], 473, 4, 3))} L 620 480 L 380 480 Z" fill="#B8A0C0"/>')
    out.append(f'<path d="M 485 400 l 4 -8 l 4 8 Z" fill="#FFFFFF" opacity="0.8"/>')
    rnd = random.Random(474)
    for k in range(140):
        x, y = rnd.uniform(-10, 610), rnd.uniform(440, 500)
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{rnd.uniform(6, 16):.1f}" height="{rnd.uniform(4, 10):.1f}" fill="{rnd.choice(["#F2D8D0", "#E8C8C8", "#FFFFFF", "#D8B8C0"])}" opacity="0.7"/>')
    out.append(f'<rect y="430" width="600" height="80" fill="{D.lin([(0, "#F8D8C8", 0.6), (1, "#F8D8C8", 0)])}"/>')
    # the Acropolis rock: sheer limestone cliffs, a fortification wall along the top, pines at the foot
    rock = [(-20, 540), (-20, 470), (30, 452), (56, 420), (70, 380), (530, 372), (552, 404), (590, 420), (620, 446), (620, 540), (300, 552)]
    out.append(f'<path d="{pd(rock)}" fill="#B88A6A"/>')
    rd = pd(rock)
    cid = D.clip(f'<path d="{rd}"/>')
    inner = [streaks(110, 475, (-20, 380, 620, 560), ["#D8AA82", "#8A5E46", "#C89874", "#E8C098", "#7A4E3A"], w=(2, 7), length=(20, 90), opacity=(0.3, 0.6), slant=0.1),
             f'<path d="{rd}" fill="{D.lin([(0, "#FFE0B0", 0.45), (0.45, "#FFE0B0", 0), (1, "#3A1E2A", 0.4)], 0, 0, 1, 0)}"/>',
             f'<rect x="-20" y="470" width="640" height="140" fill="{D.lin([(0, "#5A3A3A", 0), (1, "#5A3A3A", 0.4)])}"/>']
    for k in range(9):
        x = rnd.uniform(0, 600)
        inner.append(taper([(x, 380), (x + rnd.uniform(-8, 8), 430), (x + rnd.uniform(-10, 10), 500)], 3, 1, "#6A4436", 0.5))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    wall = [(64, 392), (536, 384), (536, 368), (64, 376)]
    out.append(painted(D, poly_pts(wall, 10, 476, 0.5), ("#F2D8B8", "#D8B898", "#A88A6A"), 476, sdir=(0.8, 0.3), sk=0.15, angle=0, n=20, inkw=1.2, inkop=0.5, hi=0.4))
    for k in range(22):
        out.append(f'<path d="M {66 + k * 21.4:.1f} 382 l 18 0" stroke="#A88A6A" stroke-width="1.1" opacity="0.6"/>')
    out.append(ink(pd(rock), INK, 1.4, 477, 1, 0.4))
    # the temple
    out.append(parthenon(D, 92, 372, 440, 478))
    out.append(soft_glow(D, 150, 300, 140, "#FFE8B8", 0.3))
    # the city at the foot of the rock
    for k in range(120):
        x, y = rnd.uniform(-10, 610), rnd.uniform(522, 600)
        w_, h_ = rnd.uniform(10, 24), rnd.uniform(8, 16)
        col = rnd.choice(["#FFF2E8", "#F2DCD0", "#FFFFFF", "#E8D0C8", "#F8E4D0"])
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w_:.1f}" height="{h_:.1f}" fill="{col}"/><rect x="{x + w_:.1f}" y="{y:.1f}" width="{w_ * 0.25:.1f}" height="{h_:.1f}" fill="#C8A8B0"/>')
        if rnd.random() < 0.5:
            out.append(f'<rect x="{x + w_ * 0.3:.1f}" y="{y + h_ * 0.3:.1f}" width="2.5" height="3" fill="#7A6A8A"/>')
    out.append(f'<rect y="516" width="600" height="90" fill="{D.lin([(0, "#F8D8C8", 0.55), (1, "#F8D8C8", 0.05)])}"/>')
    # a belt of pines and cypress along the foot of the rock hides where it meets the town
    for k in range(16):
        x = -10 + k * 41 + rnd.uniform(-8, 8)
        out.append(dab_crown(D, x, 536 + rnd.uniform(-6, 6), rnd.uniform(26, 36), rnd.uniform(14, 20), [("#8AA868", "#4A6A3A", "#22361C")], 480 + k, n=30, size=(5, 9), inkw=0))
    # olive branch framing the bottom-left corner
    out.append(olive_branch(D, [(-20, 620), (60, 560), (150, 540), (230, 548)], 477, olives=((0.5, 1, ("#9A9A5A", "#5E6A2A", "#2E3A12")), (0.75, -1, ("#5A3A4A", "#2E1A28", "#120810"))),
                            w=7, leaves=18, L=(34, 50)))
    for x, y in ((380, 210), (404, 222), (360, 226)):
        out.append(bird_v(x, y, 7, "#5A4A6A", 0.8))
    out.append(letters(D, 300, 132, "Athina", SERIF_IT, 128, "#FFFFFF", ["#FFFFFF", "#FFF0E8", "#FFE8E0"], 478, max_w=400,
                       shadow="#5A3A6A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 176, "ATHENS · THE PARTHENON AT DAWN", "#4A2E5A", font=JOS, size=18, ls=4, line_w=22, gap=10))
    return finish_g(D, out, 479, "#2A1A2A", 0.8)


# ================================================================ 19. meteora — monasteries on the rock pillars, mist at dawn
def rock_pillar(D, x0, x1, top, base, seed, pal=("#E2C8A8", "#B0906E", "#5E4A3C"), light=(-0.8, -0.3), caves=True, haze=0.0):
    """A Meteora sandstone pillar: rounded dome top, near-vertical flanks, deep vertical grooves and wind caves."""
    rnd = random.Random(seed)
    hz = (lambda c: mix(c, "#E8D8E0", haze)) if haze else (lambda c: c)
    w = x1 - x0
    pts = [(x0, base), (x0 + w * 0.02, top + (base - top) * 0.45), (x0 + w * 0.08, top + (base - top) * 0.12), (x0 + w * 0.3, top + 2), (x0 + w * 0.55, top - 4),
           (x0 + w * 0.8, top + 6), (x0 + w * 0.95, top + (base - top) * 0.15), (x1, top + (base - top) * 0.5), (x1 + w * 0.03, base)]
    pts = jitter(pts, seed, 2)
    d = smooth_closed(pts)
    out = [f'<path d="{d}" fill="{hz(pal[1])}"/>']
    cid = D.clip(f'<path d="{d}"/>')
    inner = [streaks(int(w * 0.5), seed, (x0, top, x1, base), [hz(pal[0]), hz(pal[2]), hz(mix(pal[1], pal[2], 0.3))], w=(2, 6), length=(30, 120), opacity=(0.3, 0.6), slant=0.05),
             f'<path d="{d}" fill="{D.lin([(0, hz("#FFF0D8"), 0.55), (0.45, hz("#FFF0D8"), 0), (1, hz("#2A1E2A"), 0.45)], 0, 0, 1, 0)}"/>']
    for k in range(int(w / 26)):
        x = x0 + rnd.uniform(0.1, 0.9) * w
        inner.append(taper([(x, top + rnd.uniform(10, 40)), (x + rnd.uniform(-4, 4), (top + base) / 2), (x + rnd.uniform(-6, 6), base)], rnd.uniform(2, 4), 1.5, hz(pal[2]), 0.45))
    if caves:
        for k in range(int(w / 40)):
            cx, cy = x0 + rnd.uniform(0.15, 0.85) * w, rnd.uniform(top + (base - top) * 0.25, top + (base - top) * 0.8)
            inner.append(f'<path d="{blob(cx, cy, rnd.uniform(4, 9), rnd.uniform(3, 6), rnd.randint(0, 999), 0.2, 8)}" fill="{hz("#3A2A28")}" opacity="0.7"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, hz(INK), 1.4, seed, 1, 0.4))
    return "".join(out), pts


def monastery(D, x, top, w, seed, haze=0.0):
    """Monastery perched on a pillar top: stone walls with small windows, terracotta roofs, a little dome and a cypress."""
    rnd = random.Random(seed)
    hz = (lambda c: mix(c, "#E8D8E0", haze)) if haze else (lambda c: c)
    out = []
    blocks = [(0.0, 0.34, 22), (0.3, 0.62, 34), (0.58, 0.92, 26)]
    for k, (a, b, h) in enumerate(blocks):
        bx0, bx1 = x + a * w, x + b * w
        out.append(painted(D, rect_pts(bx0, top - h, bx1, top + 4, 8, seed + k, 0.4), tuple(hz(c) for c in ("#F2E2C8", "#D8C0A0", "#8A7458")), seed + k, sdir=(1, 0.3), sk=0.18, angle=-90, n=8, inkw=1, inkop=0.5, hi=0.35))
        roof = [(bx0 - 3, top - h + 1), ((bx0 + bx1) / 2, top - h - 10), (bx1 + 3, top - h + 1)]
        out.append(f'<path d="{pd(roof)}" fill="{hz(TERRA[1])}"/><path d="{pd([roof[1], roof[2], (roof[2][0], roof[2][1] + 0), ((bx0 + bx1) / 2, top - h - 9)])}" fill="{hz(TERRA[2])}" opacity="0.5"/>')
        for j in range(int((bx1 - bx0) / 10)):
            out.append(f'<rect x="{bx0 + 4 + j * 10:.1f}" y="{top - h * 0.6:.1f}" width="3" height="5" fill="{hz("#3A2A2A")}"/>')
    # little dome
    dx_ = x + w * 0.44
    out.append(f'<path d="M {dx_ - 9:.1f} {top - 34:.1f} A 9 9 0 0 1 {dx_ + 9:.1f} {top - 34:.1f} Z" fill="{hz(TERRA[1])}"/><rect x="{dx_ - 0.8:.1f}" y="{top - 49:.1f}" width="1.6" height="8" fill="{hz("#3A3A3A")}"/>')
    out.append(f'<path d="M {x + w * 0.96:.1f} {top + 4:.1f} q 4 -18 0 -36 q -4 18 0 36 Z" fill="{hz("#2E4A2A")}"/>')
    return "".join(out)


@design("meteora")
def meteora():
    D = Doc2("grme")
    out = [sky(D, [(0, "#7A98D0"), (0.4, "#C8B8D8"), (0.68, "#FFD4B0"), (1, "#FFE6C4")], 491, 600, ["#C8C8E0", "#FFE0C8"], 60, sop=(0.05, 0.12))]
    out.append(soft_glow(D, 488, 268, 200, "#FFF0C0", 0.7))
    out.append(f'<circle cx="488" cy="268" r="22" fill="#FFF6D8"/>')
    for x, y, w in ((140, 212, 110), (520, 160, 80)):
        out.append(puff_cloud(D, x, y, w, 492 + x, pal=("#FFFFFF", "#FBEFF0", "#D8C8D8"), op=0.75, rows=1))
    grey = ("#EAD8C0", "#A8967E", "#4A3E36")
    # far massif, hazy blue-violet
    for k, (x0, x1, top) in enumerate(((400, 470, 330), (452, 540, 300), (520, 640, 350), (-30, 40, 340), (20, 90, 380))):
        p_, _ = rock_pillar(D, x0, x1, top, 560, 493 + k, pal=grey, haze=0.6, caves=False)
        out.append(p_)
    out.append(mist(D, 470, 80, 494, "#FFF4F0", 0.5))
    # middle pillar with a small monastery on its crown
    p_, _ = rock_pillar(D, 64, 186, 300, 600, 495, pal=grey, haze=0.25)
    out.append(p_)
    out.append(monastery(D, 84, 304, 92, 496, haze=0.25))
    # the hero massif: a tall pillar and a lower shoulder joined by a cleft, the big monastery on top
    p_, _ = rock_pillar(D, 360, 470, 300, 640, 497, pal=grey)
    out.append(p_)
    p_, _ = rock_pillar(D, 220, 390, 246, 640, 498, pal=grey)
    out.append(p_)
    out.append(taper([(388, 300), (384, 420), (390, 600)], 7, 3, "#2E2620", 0.5))
    out.append(monastery(D, 240, 250, 140, 499))
    # a footpath of steps cut up the shoulder
    for k in range(7):
        out.append(f'<path d="M {404 + k * 3} {404 - k * 16} l 14 -4" stroke="#F2E2C8" stroke-width="2.4" stroke-linecap="round" opacity="0.8"/>')
    out.append(mist(D, 520, 70, 500, "#FFFFFF", 0.6))
    # forest filling the valley floor
    rnd = random.Random(501)
    for row, (y0, sz) in enumerate(((540, 1.0), (566, 1.15), (592, 1.3))):
        for k in range(16):
            x = -20 + k * 42 + rnd.uniform(-10, 10) + row * 14
            out.append(dab_crown(D, x, y0 + rnd.uniform(-6, 6), 26 * sz, 18 * sz, [("#9AB878", "#5A7A48", "#2E4428"), ("#B8C888", "#7A9A58", "#3E5A30")],
                                 502 + row * 20 + k, n=26, size=(4, 8), inkw=0))
    out.append(mist(D, 548, 40, 560, "#FFFFFF", 0.35))
    for x, y in ((180, 214), (200, 224), (162, 228)):
        out.append(bird_v(x, y, 7, "#4A4A6A", 0.8))
    out.append(letters(D, 300, 128, "Meteora", SERIF_IT, 124, "#FFFFFF", ["#FFFFFF", "#F4F0F8", "#FFF4EC"], 521, max_w=420,
                       shadow="#5A4A6A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 172, "SUSPENDED IN THE AIR", "#4A3A5A", font=JOS, size=20, ls=5, line_w=30, gap=12))
    return finish_g(D, out, 522, "#2A1E2A", 0.8)


def mist(D, y, h, seed, col="#FFFFFF", op=0.7, x0=-40, x1=640):
    rnd = random.Random(seed)
    out = []
    for k in range(7):
        cx = rnd.uniform(x0, x1)
        out.append(f'<path d="{blob(cx, y + rnd.uniform(-h * 0.3, h * 0.3), rnd.uniform(120, 220), h * rnd.uniform(0.25, 0.45), rnd.randint(0, 999), 0.2, 14)}" fill="{col}" opacity="{op * rnd.uniform(0.35, 0.6):.2f}"/>')
    return "".join(out)


# ================================================================ 20. kalokairi — octopus drying in the harbor
def drying_octopus(D, x, y, s, seed, pal=("#F2B0B8", "#C8607A", "#7A2440"), lean=0):
    """An octopus hung over a line to dry in the sun: the bulbous mantle sagging above the line with its eyes,
    eight tentacles hanging below in a fan, rows of pale suckers showing, the tips curled. A clothes peg holds it."""
    rnd = random.Random(seed)
    out = []
    order = list(range(8))
    for k in order:
        t = (k - 3.5) / 3.5
        L = s * rnd.uniform(0.62, 0.86) * (1 - 0.18 * abs(t))
        curl = 1 if t > 0 else -1
        x0 = x + t * s * 0.12
        pts = [(x0, y + s * 0.04), (x0 + t * s * 0.12, y + L * 0.35), (x0 + t * s * 0.2, y + L * 0.7), (x0 + t * s * 0.22 + curl * s * 0.05, y + L * 0.9),
               (x0 + t * s * 0.22 + curl * s * 0.1, y + L * 0.94), (x0 + t * s * 0.22 + curl * s * 0.09, y + L * 0.86)]
        out.append(tentacle(D, pts, s * 0.085, s * 0.018, seed + k, pal=pal, side=-curl, char=False, speck_cols=None))
    # mantle: a soft sack leaning over to one side, with two eyes at its base
    m = rot([(x - s * 0.13, y + s * 0.02), (x - s * 0.16, y - s * 0.1), (x - s * 0.12, y - s * 0.26), (x, y - s * 0.33), (x + s * 0.12, y - s * 0.27),
             (x + s * 0.16, y - s * 0.1), (x + s * 0.13, y + s * 0.02), (x, y + s * 0.06)], x, y, lean)
    out.append(painted(D, m, pal, seed + 20, sdir=(0.5, 0.8), sk=0.22, angle=-80, n=14, inkw=1.4, hi=0.45))
    md = smooth_closed(m)
    cid = D.clip(f'<path d="{md}"/>')
    sp = "".join(f'<circle cx="{x + rnd.uniform(-s * 0.13, s * 0.13):.1f}" cy="{y - rnd.uniform(0, s * 0.3):.1f}" r="{rnd.uniform(1, 2.6):.1f}" fill="{rnd.choice([pal[2], pal[0]])}" opacity="0.45"/>' for _ in range(36))
    out.append(f'<g {cid}>{sp}</g>')
    for sg in (-1, 1):
        ex, ey = x + sg * s * 0.11, y - s * 0.03
        out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{s * 0.02:.1f}" ry="{s * 0.014:.1f}" fill="{pal[0]}"/><ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{s * 0.012:.1f}" ry="{s * 0.005:.1f}" fill="#3A1418"/>')
    return "".join(out)


@design("kalokairi")
def kalokairi():
    D = Doc2("grka")
    out = [sky(D, [(0, "#4AA8E8"), (0.7, "#A8DCF4"), (1, "#E4F4F8")], 531, 250, ["#C8ECF8", "#6AC0E8"], 40, sop=(0.05, 0.12))]
    # island hill and harbour houses
    hl = ridge([(-20, 210), (120, 170), (260, 160), (420, 180), (620, 196)], 532, 10, 3)
    out.append(hill(D, hl, 300, ("#D8C8A0", "#B0A078", "#7A6A4A"), 533, angle=-10, inkw=1.2))
    rnd = random.Random(534)
    hs = []
    for row in range(3):
        x = -10 + row * 14
        while x < 610:
            w = rnd.uniform(30, 52)
            hs.append((x, 236 + row * 18 + rnd.uniform(-4, 4), w, rnd.uniform(24, 36)))
            x += w + rnd.uniform(4, 16)
    for i, (x, b, w, h) in enumerate(hs):
        out.append(cube_house(D, x, b, w, h, 535 + i, side=0.2, door=rnd.choice([AEGEAN, TURQ, RED, GREEN]), windows=1 + (w > 44), light="left", step=False,
                              sun_wall=rnd.choice([WASH_W, WASH_W, WASH_W, ("#FFE8C0", "#F6D090", "#B89050")])))
    out.append(blue_dome(D, 452, 214, 22, 560))
    # quay
    out.append(painted(D, rect_pts(-10, 292, 620, 310, 10, 561, 0.4), ("#F2E8D8", "#D8C8B0", "#9A8A70"), 561, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=1.2, hi=0.3))
    # harbour water
    out.append(sea(D, 308, 610, [(0, "#2A8AB8"), (0.5, "#3AB0C0"), (1, "#7ADCD0")], 562, ["#FFFFFF", "#1E6A98", "#9AE8E0"], 90, ticks=["#FFFFFF", "#D8F4F4"]))
    out.append(caique(D, 170, 392, 170, 563, hull=WASH, band=AEGEAN, trim=RED))
    out.append(caique(D, 470, 350, 110, 564, hull=("#FFF0B8", "#F2CC5A", "#A88A2A"), band=RED, trim=AEGEAN, flip=True, mast=False))
    out.append(taper([(560, 322), (600, 316)], 2, 1, "#5A4A3A", 0.8))
    # foreground: line strung between two posts with octopuses drying, a taverna chair end
    out.append(taper([(46, 610), (46, 432)], 9, 8, "#8A6A4A"))
    out.append(taper([(560, 610), (560, 424)], 9, 8, "#8A6A4A"))
    line = [(46, 438), (300, 470), (560, 430)]
    out.append(pline(line, "#4A3A2A", 1.8, 565, 0.95, 1))
    for k, (x, y, ln) in enumerate(((150, 452, -8), (300, 462, 5), (446, 450, -4))):
        out.append(drying_octopus(D, x, y, 156, 566 + k * 10, lean=ln))
    for x, y in ((360, 98), (380, 112), (100, 120)):
        out.append(seagull(x, y, 10, "#3A4A6A"))
    out.append(letters(D, 300, 130, "Kalokairi", SERIF_IT, 120, "#FFFFFF", ["#FFFFFF", "#F2F8FC", "#E8F4FA"], 590, max_w=430,
                       shadow="#14508A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 172, "SUMMER IN THE HARBOR", "#0E3A6A", font=JOS, size=19, ls=5, line_w=30, gap=12))
    return finish_g(D, out, 591)


# ================================================================ 21. philotimo — the amphora and the word with no translation
def amphora(D, cx, base, h, seed):
    """Black-figure style neck amphora: terracotta body, black glaze bands, a meander on the neck, a frieze of
    leaping dolphins on the shoulder, rays at the foot; two handles."""
    w = h * 0.5
    top = base - h
    body = [(cx - w * 0.17, top), (cx - w * 0.15, top + h * 0.06), (cx - w * 0.17, top + h * 0.2), (cx - w * 0.42, top + h * 0.34), (cx - w * 0.5, top + h * 0.52),
            (cx - w * 0.38, top + h * 0.78), (cx - w * 0.16, top + h * 0.9), (cx - w * 0.2, base), (cx + w * 0.2, base), (cx + w * 0.16, top + h * 0.9),
            (cx + w * 0.38, top + h * 0.78), (cx + w * 0.5, top + h * 0.52), (cx + w * 0.42, top + h * 0.34), (cx + w * 0.17, top + h * 0.2), (cx + w * 0.15, top + h * 0.06), (cx + w * 0.17, top)]
    out = [cast(D, cx + 10, base, w * 0.6, 9, strength=0.45, seed=seed)]
    for sg in (-1, 1):
        hp = [(cx + sg * w * 0.16, top + h * 0.1), (cx + sg * w * 0.36, top + h * 0.1), (cx + sg * w * 0.4, top + h * 0.2), (cx + sg * w * 0.34, top + h * 0.3)]
        out.append(ink(smooth_open(hp), "#1A0E08", 9, seed, 1, 1) + ink(smooth_open(hp), "#3A2418", 4, seed + 1, 1, 0.6))
    out.append(painted(D, body, ("#F4A86A", "#D8783E", "#8A3E18"), seed, sdir=(0.9, 0.3), sk=0.18, angle=-90, n=60, inkw=2, hi=0.45))
    bd = smooth_closed(body)
    cid = D.clip(f'<path d="{bd}"/>')
    inner = []
    # black bands
    for (y0, y1) in ((top, top + h * 0.06), (top + h * 0.3, top + h * 0.33), (top + h * 0.62, top + h * 0.66), (top + h * 0.86, base)):
        inner.append(f'<rect x="{cx - w:.1f}" y="{y0:.1f}" width="{2 * w:.1f}" height="{y1 - y0:.1f}" fill="#1E120A"/>')
    inner.append(meander_band(D, cx - w * 0.2, cx + w * 0.2, top + h * 0.08, h * 0.1, "#1E120A", None, seed, rule=False))
    # dolphins leaping around the belly
    for k in range(3):
        dx = cx - w * 0.32 + k * w * 0.32
        dy = top + h * 0.47 + (6 if k % 2 else -4)
        dol = [(dx - 26, dy + 6), (dx - 14, dy - 8), (dx + 6, dy - 12), (dx + 22, dy - 6), (dx + 30, dy - 2), (dx + 22, dy + 2), (dx + 4, dy + 2), (dx - 12, dy + 8)]
        inner.append(f'<path d="{smooth_closed(dol)}" fill="#1E120A"/>')
        inner.append(f'<path d="{pd([(dx - 24, dy + 6), (dx - 36, dy - 2), (dx - 32, dy + 10)])}" fill="#1E120A"/>')
        inner.append(f'<path d="{pd([(dx + 2, dy - 10), (dx - 4, dy - 20), (dx + 10, dy - 11)])}" fill="#1E120A"/>')
        inner.append(f'<circle cx="{dx + 18:.1f}" cy="{dy - 6:.1f}" r="1.6" fill="#D8783E"/>')
    for k in range(-2, 3):   # waves under the dolphins
        inner.append(f'<path d="M {cx + k * w * 0.2 - 16:.1f} {top + h * 0.58:.1f} q 8 -8 16 0 q 8 8 16 0" stroke="#1E120A" stroke-width="3" fill="none"/>')
    # rays at the foot
    for k in range(-5, 6):
        x = cx + k * w * 0.075
        inner.append(f'<path d="{pd([(x - 6, top + h * 0.86), (x, top + h * 0.72), (x + 6, top + h * 0.86)])}" fill="#1E120A"/>')
    inner.append(shade_over(D, bd, "#1A0804", 0.4, 0, 0, 1, 0, 0.4))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(taper([(cx - w * 0.36, top + h * 0.38), (cx - w * 0.44, top + h * 0.52), (cx - w * 0.34, top + h * 0.72)], 8, 3, "#FFE0B8", 0.5))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, w * 0.2, w * 0.05, 0, 360, 16))}" fill="#1E120A"/>')
    return "".join(out)


@design("philotimo")
def philotimo():
    D = Doc2("grpt")
    out = [sky(D, [(0, "#14306E"), (1, "#1F4A92")], 601, 600, ["#1E3E80", "#0C2458", "#2A56A0"], 120, angle=-80, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 300, 360, 250, "#FFE0A0", 0.3))
    # meander frame bleeding off all four edges
    for (x0, y0, x1, h, rotd) in ((0, 0, 600, 48, 0), (0, 552, 600, 48, 0)):
        out.append(meander_band(D, x0, x1, y0, h, "#F2D08A", "#14306E", 602 + y0, rule=True))
    for x in (0, 552):
        out.append(f'<g transform="rotate(90 {x + 24} 300) translate(0 0)">' + meander_band(D, x + 24 - 300, x + 24 + 300, 276, 48, "#F2D08A", "#14306E", 603 + x, rule=True) + "</g>")
    # laurel/olive wreath behind the amphora
    for sg in (-1, 1):
        pts = [(300 + sg * 20, 560), (300 + sg * 140, 470), (300 + sg * 160, 330), (300 + sg * 110, 240)]
        out.append(olive_branch(D, pts, 604 + sg, olives=((0.4, sg, ("#C8C080", "#8A8A3A", "#4A4A1A")),), w=4, leaves=14, pal=("#E8E0A8", "#B8B070", "#6A6A30"), L=(26, 36)))
    # plinth
    out.append(painted(D, rect_pts(226, 516, 374, 540, 8, 605, 0.4), ("#F4ECDC", "#D8CCB4", "#8A7E68"), 605, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.4))
    out.append(amphora(D, 300, 518, 264, 606))
    out.append(gr_ruled(300, 104, "ΦΙΛΟΤΙΜΟ", "#F2D08A", size=24, ls=6, line_w=36, gap=14))
    out.append(letters(D, 300, 196, "philotimo", SERIF_IT, 112, "#FFF6E4", ["#FFFFFF", "#F2E6D0", "#FFF0DC"], 607, max_w=400,
                       shadow="#08163A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(label(300, 236, "the Greek word with no translation", SERIF_IT, 22, "#F2D08A", max_w=400))
    return finish_g(D, out, 608, "#08163A", 0.8)


# ================================================================ 22. pappou — tavli, komboloi and a coffee at the kafeneio
def tavli(D, x0, y0, x1, y1, seed):
    """An open tavli (backgammon) board seen from above-front: inlaid wooden case, two halves with long triangles,
    a few checkers in play and two dice."""
    rnd = random.Random(seed)
    out = [cast(D, (x0 + x1) / 2 + 10, y1 + 4, (x1 - x0) * 0.55, 12, strength=0.45, seed=seed)]
    frame = rect_pts(x0, y0, x1, y1, 10, seed, 0.4)
    out.append(painted(D, frame, ("#C8925A", "#8A5428", "#4A2810"), seed, sdir=(0.3, 1), sk=0.15, angle=0, n=30, inkw=2, hi=0.35))
    # inlay border
    out.append(f'<rect x="{x0 + 6}" y="{y0 + 6}" width="{x1 - x0 - 12}" height="{y1 - y0 - 12}" fill="none" stroke="#F2D8A8" stroke-width="1.6" stroke-dasharray="4 3" opacity="0.8"/>')
    mid = (x0 + x1) / 2
    for (a, b) in ((x0 + 14, mid - 8), (mid + 8, x1 - 14)):
        field = [(a, y0 + 14), (b, y0 + 14), (b, y1 - 14), (a, y1 - 14)]
        out.append(f'<path d="{pd(field)}" fill="#E8C890"/>')
        out.append(strokes(D.nid(), pd(field), (a, y0, b, y1), ["#D8B070", "#F2DCA8"], seed + int(a), n=30, angle=0, length=(20, 60), width=(1, 2), opacity=(0.2, 0.4)))
        tw = (b - a) / 6
        for i in range(6):
            tx = a + i * tw
            for top_side, cols in ((True, ("#7A1E14", "#2A1A10")), (False, ("#2A1A10", "#7A1E14"))):
                c = cols[i % 2]
                if top_side:
                    tri = [(tx + 1, y0 + 14), (tx + tw - 1, y0 + 14), (tx + tw / 2, y0 + 14 + (y1 - y0 - 28) * 0.42)]
                else:
                    tri = [(tx + 1, y1 - 14), (tx + tw - 1, y1 - 14), (tx + tw / 2, y1 - 14 - (y1 - y0 - 28) * 0.42)]
                out.append(f'<path d="{pd(tri)}" fill="{c}" opacity="0.92"/>')
    out.append(f'<rect x="{mid - 8}" y="{y0 + 10}" width="16" height="{y1 - y0 - 20}" fill="#6A3A18"/>')
    # checkers
    spots = [(x0 + 30, y0 + 30, "w"), (x0 + 30, y0 + 50, "w"), (x0 + 30, y0 + 70, "w"), (x1 - 40, y1 - 30, "b"), (x1 - 40, y1 - 50, "b"),
             (mid + 40, y0 + 30, "b"), (mid - 50, y1 - 30, "w"), (mid - 50, y1 - 50, "w"), (x1 - 80, y0 + 30, "w"), (x0 + 90, y1 - 30, "b")]
    r = (x1 - x0) * 0.028
    for (x, y, c) in spots:
        pal = ("#FFFFFF", "#F2EAD8", "#A89880") if c == "w" else ("#6A4A3A", "#2A1A12", "#0A0604")
        out.append(f'<ellipse cx="{x + 1.5:.1f}" cy="{y + 2.5:.1f}" rx="{r:.1f}" ry="{r * 0.9:.1f}" fill="#1A0A04" opacity="0.4"/>')
        out.append(painted(D, ell_pts(x, y, r, r * 0.9, 0, 360, 14), pal, int(x + y), sk=0.15, n=4, inkw=1, hi=0.4))
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.55:.1f}" fill="none" stroke="{pal[2]}" stroke-width="1"/>')
    # dice
    for k, (x, y, n_) in enumerate(((mid + 70, (y0 + y1) / 2, 5), (mid + 100, (y0 + y1) / 2 + 10, 3))):
        out.append(painted(D, rot(rect_pts(x - 10, y - 10, x + 10, y + 10, 6, seed + k, 0.3), x, y, 15 * (k * 2 - 1)), ("#FFFFFF", "#F4F0E8", "#B8B0A6"), seed + k, sk=0.2, n=3, inkw=1.2, hi=0.4))
        pips = {5: [(-5, -5), (5, -5), (0, 0), (-5, 5), (5, 5)], 3: [(-5, -5), (0, 0), (5, 5)]}[n_]
        for px, py in rot([(x + a, y + b) for a, b in pips], x, y, 15 * (k * 2 - 1)):
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.8" fill="#2A1A10"/>')
    return "".join(out)


def komboloi(D, pts, seed, bead=("#FFD08A", "#E89A2A", "#9A5A0A"), r=7):
    """Worry beads: amber beads along a looped cord, a shield bead and a silky tassel."""
    path = catmull(pts, 10)
    out = [pline(path, "#5A3A1A", 1.4, seed, 0.9, 1)]
    L = 0
    acc = [0]
    for (a, b) in zip(path, path[1:]):
        L += math.hypot(b[0] - a[0], b[1] - a[1])
        acc.append(L)
    n = int(L / (r * 2.05))
    for i in range(n):
        d = (i + 0.5) * L / n
        j = max(k for k in range(len(acc)) if acc[k] <= d) if d > 0 else 0
        j = min(j, len(path) - 2)
        t = (d - acc[j]) / max(1e-6, acc[j + 1] - acc[j])
        x = path[j][0] + (path[j + 1][0] - path[j][0]) * t
        y = path[j][1] + (path[j + 1][1] - path[j][1]) * t
        out.append(f'<ellipse cx="{x + 1.5:.1f}" cy="{y + 2:.1f}" rx="{r:.1f}" ry="{r * 0.9:.1f}" fill="#3A1A04" opacity="0.3"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{bead[1]}"/><circle cx="{x + r * 0.2:.1f}" cy="{y + r * 0.25:.1f}" r="{r * 0.7:.1f}" fill="{bead[2]}" opacity="0.4"/>'
                   f'<circle cx="{x - r * 0.35:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.3:.1f}" fill="#FFF4D8" opacity="0.85"/>')
        out.append(ink(smooth_closed(ell_pts(x, y, r, r, 0, 360, 12)), "#7A3E0A", 0.9, seed + i, 1, 0.5))
    ex, ey = path[-1]
    out.append(f'<rect x="{ex - 5:.1f}" y="{ey - 2:.1f}" width="10" height="14" rx="3" fill="#C8A048"/>')
    for k in range(9):
        out.append(pline([(ex + (k - 4) * 0.8, ey + 12), (ex + (k - 4) * 2.4, ey + 46)], ["#C8282A", "#A81818", "#E04040"][k % 3], 2.2, seed + k, 0.95, 1))
    return "".join(out)


def flat_cap(D, cx, cy, w, seed):
    """Navy wool fisherman's cap (the Greek captain's cap) seen from above-front: soft crown, braided cord, black peak."""
    crown = [(cx - w * 0.5, cy + w * 0.06), (cx - w * 0.42, cy - w * 0.18), (cx - w * 0.1, cy - w * 0.28), (cx + w * 0.24, cy - w * 0.24), (cx + w * 0.5, cy - w * 0.06), (cx + w * 0.46, cy + w * 0.12), (cx, cy + w * 0.16)]
    out = [cast(D, cx + 8, cy + w * 0.2, w * 0.55, 10, strength=0.4, seed=seed)]
    peak = [(cx - w * 0.36, cy + w * 0.08), (cx + w * 0.34, cy + w * 0.1), (cx + w * 0.28, cy + w * 0.3), (cx, cy + w * 0.36), (cx - w * 0.3, cy + w * 0.28)]
    out.append(painted(D, peak, ("#4A4A52", "#1A1A20", "#08080A"), seed, sdir=(0.3, 1), sk=0.15, n=8, inkw=1.4, hi=0.5))
    out.append(painted(D, crown, ("#4A5A8A", "#22305A", "#0C1430"), seed + 1, sdir=(0.5, 0.8), sk=0.2, angle=-20, n=30, inkw=1.6, hi=0.4))
    for k in range(3):
        out.append(taper([(cx - w * 0.36, cy + w * 0.06 + k * 3), (cx, cy + w * 0.14 + k * 3), (cx + w * 0.36, cy + w * 0.08 + k * 3)], 2, 2, "#1A1A20" if k % 2 else "#3A3A48", 0.9))
    out.append(f'<circle cx="{cx - w * 0.36:.1f}" cy="{cy + w * 0.08:.1f}" r="3" fill="#C8A048"/><circle cx="{cx + w * 0.36:.1f}" cy="{cy + w * 0.09:.1f}" r="3" fill="#C8A048"/>')
    return "".join(out)


@design("pappou")
def pappou():
    D = Doc2("grpp")
    # top-down kafeneio table: painted green wood, a slice of sunlight
    out = [wood_planks(D, -10, 610, 611, ("#7AB89A", "#3E8A6A", "#1E4E3A"), 6)]
    out.append(f'<path d="M 0 0 L 360 0 L 600 300 L 600 600 L 260 600 L 0 220 Z" fill="#FFF4D0" opacity="0.18"/>')
    out.append(specks(612, (0, 0, 600, 600), ["#E8DCC0", "#C8B890"], 60, (1, 3), (0.2, 0.5)))
    out.append(tavli(D, 140, 280, 520, 500, 613))
    out.append(demitasse(D, 112, 560, 84, 614, glaze=WHITE, band=AEGEAN[1]))
    out.append(water_glass(D, 90, 468, 96, 615, w=58))
    out.append(flat_cap(D, 452, 214, 150, 616))
    out.append(komboloi(D, [(250, 230), (300, 214), (346, 236), (334, 266), (290, 276), (256, 262), (250, 236)], 617))
    # reading glasses
    for x0 in (164, 210):
        out.append(f'<ellipse cx="{x0}" cy="232" rx="20" ry="15" fill="#E8F4F8" opacity="0.35"/>' + ink(smooth_closed(ell_pts(x0, 232, 20, 15, 0, 360, 18)), "#3A2A1A", 2.4, x0, 1, 0.95))
    out.append(pline([(184, 230), (187, 226), (190, 230)], "#3A2A1A", 2.2, 618, 0.95, 1))
    out.append(pline([(144, 228), (122, 222), (110, 206)], "#3A2A1A", 2, 619, 0.9, 1))
    out.append(letters(D, 300, 140, "Pappou", SERIF_IT, 120, "#FFF8E8", ["#FFFFFF", "#F2EAD8", "#FFF4E0"], 620, max_w=400,
                       shadow="#0E2E20", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 182, "TAVLI, KOMBOLOI AND STORIES", "#FFE8B0", font=JOS, size=18, ls=4, line_w=26, gap=12))
    return finish_g(D, out, 621)


# ================================================================ 23. kalo pascha — red eggs, tsoureki and the Easter candle
def red_egg(D, cx, cy, r, seed, rot_=0, cracked=False):
    pts = rot([(cx + r * 0.78 * math.sin(math.radians(a)) * (1 - 0.12 * math.cos(math.radians(a))), cy - r * math.cos(math.radians(a))) for a in range(0, 360, 15)], cx, cy, rot_)
    out = [cast(D, cx + 4, cy + r * 0.95, r * 0.7, r * 0.15, strength=0.35, seed=seed)]
    out.append(painted(D, pts, ("#F8606A", "#C8101E", "#6A040A"), seed, sdir=(0.5, 0.8), sk=0.2, angle=-60, n=10, inkw=1.4, hi=0.5, hik=0.1))
    out.append(f'<path d="{blob(cx - r * 0.3, cy - r * 0.45, r * 0.2, r * 0.1, seed, 0.2, 8, -40)}" fill="#FFFFFF" opacity="0.7"/>')
    if cracked:
        out.append(pline([(cx - r * 0.4, cy - r * 0.6), (cx - r * 0.2, cy - r * 0.45), (cx - r * 0.05, cy - r * 0.62), (cx + r * 0.15, cy - r * 0.44), (cx + r * 0.35, cy - r * 0.6)], "#FFF4E8", 1.6, seed, 0.9, 1))
    return "".join(out)


def tsoureki(D, cx, cy, w, seed):
    """Braided Easter bread seen from the side: a long glossy mahogany loaf whose three strands show as alternating
    slanted lobes, flaked almonds on top."""
    out = [cast(D, cx + 12, cy + w * 0.12, w * 0.56, 12, strength=0.45, seed=seed)]
    base = ell_pts(cx, cy, w * 0.5, w * 0.12, 0, 360, 30)
    out.append(painted(D, base, ("#C87A3A", "#8A4A18", "#3A1A06"), seed, sdir=(0.5, 0.8), sk=0.2, n=10, inkw=1.4, hi=0.3))
    n = 8
    for k in range(n):
        t = (k + 0.5) / n
        x = cx - w * 0.46 + t * w * 0.92
        prof = math.sin(math.pi * t) ** 0.6
        sg = 1 if k % 2 else -1
        y = cy - w * 0.035 * prof - sg * w * 0.012
        lobe = blob_pts(x, y, w * 0.075 * (0.7 + 0.3 * prof), w * 0.055 * (0.75 + 0.25 * prof), seed + k, 0.05, 14, sg * 38)
        out.append(painted(D, lobe, ("#F0A868", "#B4642A", "#5A2808"), seed + k, sdir=(0.5, 0.8), sk=0.22, angle=-30, n=6, inkw=1.2, hi=0.55, hik=0.12))
        out.append(f'<path d="{blob(x - w * 0.02, y - w * 0.025, w * 0.03, w * 0.012, seed + k, 0.2, 8, sg * 38)}" fill="#FFE8C0" opacity="0.7"/>')
    rnd = random.Random(seed)
    for _ in range(20):
        x, y = cx + rnd.uniform(-w * 0.4, w * 0.4), cy - w * 0.05 + rnd.uniform(-w * 0.03, w * 0.02)
        out.append(f'<path d="{blob(x, y, 4, 1.8, rnd.randint(0, 999), 0.1, 8, rnd.uniform(-40, 40))}" fill="#FFF0D0" stroke="#C8A070" stroke-width="0.6"/>')
    return "".join(out)


def koulouraki(D, cx, cy, s, seed, rot_=0):
    """Koulouraki: a rope of butter dough twisted on itself into a plait, egg-washed golden, with a pale underside."""
    out = [cast(D, cx + 3, cy + s * 0.18, s * 0.65, s * 0.12, strength=0.3, seed=seed)]
    n = 7
    for k in range(n):
        t = k / (n - 1)
        x, y = rot([(cx - s * 0.55 + t * s * 1.1, cy)], cx, cy, rot_)[0]
        sg = 1 if k % 2 else -1
        lobe = rot(blob_pts(x, y + sg * s * 0.05, s * 0.16, s * 0.12, seed + k, 0.08, 10, 40 * sg), x, y, rot_)
        out.append(painted(D, lobe, ("#FFD890", "#D8943E", "#8A5218"), seed + k, sdir=(0.5, 0.8), sk=0.22, n=4, inkw=1, hi=0.55, hik=0.12))
    return "".join(out)


@design("kalo-pascha")
def kalo_pascha():
    D = Doc2("grkp2")
    out = [paper(D.nid(), "#F8EEE0", FLECK, 631)]
    out.append(blooms(632, ["#F2C8C0", "#F8E0C8", "#E8C8D8"], 7, (0, 0, 600, 600), (110, 200), (0.1, 0.16)))
    # embroidered tablecloth band
    out.append(painted(D, rect_pts(-10, 400, 620, 620, 12, 633, 0.4), ("#FFFFFF", "#F6F0E4", "#C8BCA8"), 633, sdir=(0, 1), sk=0.05, angle=-4, n=40, inkw=0, hi=0))
    for k in range(12):
        out.append(cross_stitch_rose(30 + k * 50, 588, 2.6))
    out.append(f'<path d="M -10 568 L 610 568" stroke="#C8242A" stroke-width="2.4" stroke-dasharray="5 3"/>')
    # the lambada: tall white Easter candle with a ribbon bow
    out.append(soft_glow(D, 470, 190, 110, "#FFE6A0", 0.75))
    cand = rect_pts(458, 210, 482, 470, 10, 634, 0.4)
    out.append(painted(D, cand, ("#FFFFFF", "#F8F2E6", "#C8BCA8"), 634, sdir=(1, 0), sk=0.2, angle=-90, n=10, inkw=1.4, hi=0.5))
    out.append(f'<path d="{blob(470, 194, 7, 15, 635, 0.05, 12)}" fill="#FFD050"/><path d="{blob(470, 198, 3.5, 8, 636, 0.05, 10)}" fill="#FFFFFF"/>')
    out.append(pline([(470, 210), (470, 204)], "#2A1A10", 1.6, 637, 1, 1))
    for sg in (-1, 1):
        out.append(painted(D, [(470, 300), (470 + sg * 36, 284), (470 + sg * 40, 306), (470 + sg * 8, 306)], ("#9AD8F8", "#3A90D8", "#1A4A8A"), 638 + sg, sk=0.2, n=4, inkw=1.2, hi=0.4))
        out.append(taper([(470, 304), (470 + sg * 20, 340), (470 + sg * 14, 380)], 9, 6, "#3A90D8"))
    out.append(f'<circle cx="470" cy="302" r="7" fill="#2A70B8"/>')
    for k in range(3):
        out.append(cross_stitch_rose(470, 400 + k * 22, 1.4, col="#C8242A"))
    # tsoureki on a board, red eggs in a bowl, koulourakia on a plate
    out.append(painted(D, rect_pts(70, 400, 380, 432, 10, 639, 0.4), WOOD, 639, sdir=(0, 1), sk=0.2, angle=0, n=16, inkw=1.6, hi=0.4))
    out.append(tsoureki(D, 222, 386, 300, 640))
    out.append(red_egg(D, 222, 360, 20, 641))
    inside, front = bowl_side(D, 210, 492, 116, 32, 46, 642, band=AEGEAN)
    out.append(inside)
    for k, (x, y, r) in enumerate(((168, 478, 22), (214, 470, 23), (258, 478, 22), (190, 494, 22), (236, 494, 22), (150, 496, 20), (278, 496, 20))):
        out.append(red_egg(D, x, y, r, 643 + k, rot_=(k - 3) * 8, cracked=(k == 4)))
    out.append(front)
    out.append(plate_34(D, 452, 524, 86, 30, 650, glaze=WHITE, rim=AEGEAN[1]))
    for k, (x, y, r_) in enumerate(((424, 510, -14), (480, 506, 10), (444, 532, 16), (494, 530, -8))):
        out.append(koulouraki(D, x, y, 52, 651 + k, r_))
    out.append(letters(D, 250, 146, "Kalo Pascha", SERIF_IT, 104, "#B8141E", ["#D8282A", "#8A0A10", "#E84A40"], 660, max_w=380,
                       shadow="#FFE8D8", soff=(0.02, 0.035), angle=-40, hi="#FFA898"))
    out.append(gr_ruled(250, 196, "ΧΡΙΣΤΟΣ ΑΝΕΣΤΗ", "#1F4FA0", size=22, ls=4, line_w=24, gap=10, max_w=320))
    out.append(label(250, 228, "Christ is risen!", SERIF_IT, 21, "#7A3A2A", max_w=320))
    return finish_g(D, out, 661)


# ================================================================ 24. kala christougenna — the lit karavaki and kourabiedes
def karavaki(D, cx, wl, L, seed):
    """The little Christmas boat: a wooden model sailing boat with a white sail, strung with warm lights."""
    out = [caique(D, cx, wl, L, seed, hull=("#F8E0B8", "#D8A868", "#8A5A2A"), band=("#E86A5A", "#C8282A", "#6A0E0E"), trim=AEGEAN, cabin=False, mast=False, reflect=False)]
    mx = cx + L * 0.05
    top = wl - L * 0.9
    out.append(taper([(mx, wl - L * 0.12), (mx, top)], max(3, L * 0.025), max(2, L * 0.015), "#7A4A22"))
    sail = [(mx + 4, top + L * 0.08), (mx + 4, wl - L * 0.2), (mx + L * 0.36, wl - L * 0.22), (mx + L * 0.16, top + L * 0.4)]
    out.append(painted(D, sail, ("#FFFFFF", "#F6F2EA", "#C8C0B0"), seed + 3, sdir=(1, 0.3), sk=0.15, angle=-60, n=10, inkw=1.4, hi=0.5))
    jib = [(mx - 6, top + L * 0.3), (mx - 6, wl - L * 0.22), (cx - L * 0.32, wl - L * 0.24)]
    out.append(painted(D, jib, ("#FFFFFF", "#F2EEE6", "#C0B8A8"), seed + 4, sdir=(1, 0.3), sk=0.15, angle=-60, n=8, inkw=1.4, hi=0.4))
    out.append(f'<path d="{pd([(mx - 2, top - 4), (mx + 18, top + 2), (mx - 2, top + 8)])}" fill="#1F56A8"/>')
    # lights strung from bow to masthead to stern
    rnd = random.Random(seed)
    for (a, b) in (((cx - L * 0.52, wl - L * 0.2), (mx, top)), ((mx, top), (cx + L * 0.54, wl - L * 0.24))):
        out.append(pline([a, b], "#3A2A1A", 1.2, seed, 0.8, 1))
        for i in range(9):
            t = (i + 0.5) / 9
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            col = rnd.choice(["#FFE29A", "#FFE29A", "#FF9A8A", "#9AD0FF"])
            out.append(D.glow(x, y, 14, col, 0.55))
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{col}"/><circle cx="{x - 0.8:.1f}" cy="{y - 0.8:.1f}" r="1.1" fill="#FFFFFF"/>')
    return "".join(out)


def kourabies(D, cx, cy, s, seed, rot_=0):
    """Kourabies: a plump crescent butter cookie buried in snowy icing sugar."""
    outer = [(cx + s * math.cos(math.radians(a)), cy + s * 0.62 * math.sin(math.radians(a))) for a in range(190, 351, 10)]
    inner = [(cx + s * 0.6 * math.cos(math.radians(a)), cy - s * 0.3 + s * 0.42 * math.sin(math.radians(a))) for a in range(330, 209, -10)]
    pts = rot(outer + inner, cx, cy, rot_ + 180)
    out = [cast(D, cx + 3, cy + s * 0.3, s * 0.9, s * 0.16, strength=0.3, seed=seed)]
    out.append(painted(D, pts, ("#FFFFFF", "#F6F2EC", "#C8BEB4"), seed, sdir=(0.5, 0.8), sk=0.2, n=10, inkw=1.2, inkop=0.5, hi=0.6))
    out.append(specks(seed, bbox(pts), ["#FFFFFF", "#E8E0D8"], int(s * 2.4), (0.6, 1.8), (0.7, 1)))
    return "".join(out)


def melomakarono(D, cx, cy, s, seed):
    """Melomakarono: an oval honey cookie, dark and syrupy, with crushed walnuts on top."""
    pts = blob_pts(cx, cy, s, s * 0.62, seed, 0.06, 14)
    out = [cast(D, cx + 3, cy + s * 0.5, s, s * 0.15, strength=0.3, seed=seed)]
    out.append(painted(D, pts, ("#B8703A", "#7A3E14", "#3A1804"), seed, sdir=(0.5, 0.8), sk=0.2, n=10, inkw=1.2, hi=0.5))
    out.append(specks(seed + 1, (cx - s * 0.6, cy - s * 0.4, cx + s * 0.6, cy + s * 0.2), ["#E8C890", "#C89A5A", "#F2DCA8"], int(s * 1.2), (1, 2.2), (0.8, 1)))
    out.append(f'<path d="{blob(cx - s * 0.3, cy - s * 0.25, s * 0.25, s * 0.08, seed, 0.2, 8, -10)}" fill="#FFE0A0" opacity="0.6"/>')
    return "".join(out)


@design("kala-christougenna")
def kala_christougenna():
    D = Doc2("grkc")
    # a deep blue night through the window, stars, the karavaki glowing on the sill
    out = [sky(D, [(0, "#0E1A44"), (0.7, "#1E3A7A"), (1, "#3A5A9A")], 671, 600, ["#1E3470", "#0A1438"], 80, sop=(0.05, 0.12))]
    rnd = random.Random(672)
    for _ in range(60):
        x, y = rnd.uniform(0, 600), rnd.uniform(0, 380)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 1.8):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    for x, y, r in ((96, 250, 9), (520, 230, 11), (470, 300, 6)):
        out.append(sparkle(x, y, r, "#FFF2C0", 0.95))
    # whitewashed village rooftops with lit windows far below the sill
    for i, x in enumerate(range(-10, 620, 46)):
        h = rnd.uniform(26, 50)
        out.append(cube_house(D, x, 420, rnd.uniform(36, 48), h, 673 + i, side=0.2, door=None, windows=1, light="left", haze=0.0, step=False,
                              sun_wall=("#A8B4D8", "#7A8AB8", "#3A4A7A"), shutters=("#FFE6A0", "#FFD070", "#C89A3A")))
    out.append(blue_dome(D, 140, 392, 20, 690, pal=("#5A7AC0", "#2A4A90", "#0E2050")))
    # window frame: the sill across the bottom
    out.append(painted(D, rect_pts(-10, 420, 620, 452, 10, 691, 0.4), WASH, 691, sdir=(0, 1), sk=0.15, angle=0, n=30, inkw=1.6, hi=0.4))
    out.append(f'<rect x="-10" y="452" width="620" height="160" fill="#E8E2D8"/>')
    out.append(f'<rect x="-10" y="452" width="620" height="160" fill="{D.lin([(0, "#2A3A6A", 0.3), (1, "#2A3A6A", 0.05)])}"/>')
    out.append(soft_glow(D, 300, 380, 230, "#FFD890", 0.45))
    out.append(karavaki(D, 300, 432, 230, 692))
    # plate of kourabiedes and melomakarona in front
    out.append(plate_34(D, 300, 524, 168, 44, 693, glaze=("#5A86D0", "#2A56A8", "#0E2A66"), rim="#F2D08A"))
    for k, (x, y, r_) in enumerate(((232, 506, -10), (292, 498, 8), (352, 506, -4), (258, 528, 14), (322, 530, -12), (292, 516, 4))):
        out.append(kourabies(D, x, y, 36, 694 + k, r_))
    for k, (x, y) in enumerate(((404, 520), (420, 540), (182, 534))):
        out.append(melomakarono(D, x, y, 26, 700 + k))
    out.append(specks(705, (130, 500, 470, 560), ["#FFFFFF"], 50, (0.6, 1.6), (0.6, 1)))
    out.append(letters(D, 300, 116, "Kala", SERIF_IT, 96, "#FFF4DC", ["#FFFFFF", "#FFE8C0", "#FFF2DC"], 706, max_w=300,
                       shadow="#06102E", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(letters(D, 300, 196, "Christougenna", SERIF_IT, 84, "#FFD878", ["#FFE8A0", "#E8B040", "#FFF0C0"], 707, max_w=460,
                       shadow="#06102E", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 236, "MERRY CHRISTMAS", "#FFE8C0", font=JOS, size=19, ls=6, line_w=36, gap=14))
    return finish_g(D, out, 708, "#06102E", 0.8)


# ================================================================ 25. chronia polla — the name-day tray of sweets
def baklava_piece(D, cx, cy, s, seed):
    """A diamond of baklava in 3/4 view: golden flaky top with a clove, layered side showing the green nut filling."""
    top = [(cx - s, cy), (cx, cy - s * 0.42), (cx + s, cy), (cx, cy + s * 0.42)]
    dep = s * 0.5
    out = []
    for a_, b_ in ((top[0], top[3]), (top[3], top[2])):
        face = [a_, b_, (b_[0], b_[1] + dep), (a_[0], a_[1] + dep)]
        out.append(f'<path d="{pd(face)}" fill="#C8862E"/>')
        for t in (0.3, 0.45, 0.62):
            out.append(f'<path d="M {a_[0]:.1f} {a_[1] + dep * t:.1f} L {b_[0]:.1f} {b_[1] + dep * t:.1f}" stroke="{"#6A9A3A" if t == 0.45 else "#F2C870"}" stroke-width="{2.4 if t == 0.45 else 1}"/>')
        out.append(ink(pd(face), "#6A3A0E", 0.9, seed, 1, 0.6))
    out.append(painted(D, top, ("#FFE0A0", "#E0A040", "#8A5212"), seed, sdir=(0.5, 0.8), sk=0.18, n=6, inkw=1, hi=0.55))
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s * 0.08:.1f}" fill="#3A1A08"/>')
    out.append(f'<path d="{blob(cx - s * 0.2, cy - s * 0.1, s * 0.3, s * 0.08, seed, 0.2, 8, -20)}" fill="#FFF6D0" opacity="0.6"/>')
    return "".join(out)


def kataifi_roll(D, cx, cy, s, seed):
    """Kataifi: a roll of shredded pastry threads, golden, syrup-glossy, crushed pistachio at the ends."""
    rnd = random.Random(seed)
    out = [painted(D, ell_pts(cx, cy, s, s * 0.45, 0, 360, 18), ("#FFE0A0", "#D89A3A", "#7A4A10"), seed, sk=0.2, n=4, inkw=1, hi=0.5)]
    cid = D.clip(f'<path d="{smooth_closed(ell_pts(cx, cy, s, s * 0.45, 0, 360, 18))}"/>')
    th = "".join(f'<path d="M {cx - s + rnd.uniform(-4, 4):.1f} {cy + rnd.uniform(-s * 0.5, s * 0.5):.1f} q {s * 0.6:.1f} {rnd.uniform(-6, 6):.1f} {s * 2:.1f} {rnd.uniform(-4, 4):.1f}" stroke="{rnd.choice(["#FFF0C0", "#B8761E", "#F2C870"])}" stroke-width="1" fill="none" opacity="0.8"/>' for _ in range(int(s * 1.2)))
    out.append(f'<g {cid}>{th}</g>')
    for sg in (-1, 1):
        out.append(f'<path d="{blob(cx + sg * s * 0.9, cy, s * 0.14, s * 0.3, seed + sg, 0.2, 8)}" fill="#7AAA4A"/>')
    return "".join(out)


def galaktoboureko_piece(D, cx, cy, s, seed):
    """A square of galaktoboureko: thick pale custard between golden phyllo, top dusted with cinnamon."""
    top = [(cx - s * 0.9, cy - s * 0.05), (cx - s * 0.1, cy - s * 0.42), (cx + s * 0.9, cy - s * 0.12), (cx + s * 0.1, cy + s * 0.25)]
    dep = s * 0.62
    out = []
    for a_, b_ in ((top[0], top[3]), (top[3], top[2])):
        face = [a_, b_, (b_[0], b_[1] + dep), (a_[0], a_[1] + dep)]
        out.append(f'<path d="{pd(face)}" fill="#FFF2B8"/>')
        out.append(f'<path d="{pd([a_, b_, (b_[0], b_[1] + dep * 0.18), (a_[0], a_[1] + dep * 0.18)])}" fill="#E0A040"/>')
        out.append(f'<path d="{pd([(a_[0], a_[1] + dep * 0.86), (b_[0], b_[1] + dep * 0.86), (b_[0], b_[1] + dep), (a_[0], a_[1] + dep)])}" fill="#C8862E"/>')
        out.append(ink(pd(face), "#8A5A1A", 0.9, seed, 1, 0.6))
    out.append(painted(D, top, ("#FFE6A8", "#E8AA48", "#8A5212"), seed, sdir=(0.5, 0.8), sk=0.15, n=6, inkw=1, hi=0.5))
    out.append(specks(seed, bbox(top), ["#8A4A1A"], 14, (0.6, 1.2), (0.5, 0.8)))
    return "".join(out)


@design("chronia-polla")
def chronia_polla():
    D = Doc2("grcp")
    out = [paper(D.nid(), "#FBE8E4", "#8A5A5A", 711)]
    out.append(blooms(712, ["#F8C8C8", "#FFE0D8", "#F2B8C0"], 8, (0, 0, 600, 600), (100, 200), (0.1, 0.18)))
    rnd = random.Random(713)
    for _ in range(60):   # confetti, kept out of the lettering
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 360)
        if 70 < x < 530 and 70 < y < 250:
            continue
        out.append(f'<path d="{blob(x, y, rnd.uniform(3, 6), rnd.uniform(1.6, 3), rnd.randint(0, 999), 0.2, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#1F56A8", "#F2C040", "#E84A6A", "#2AAAB4", "#FFFFFF"])}" opacity="0.9"/>')
    out.append(wood_planks(D, 380, 600, 714, WOOD, 3))
    out.append(f'<rect y="376" width="600" height="8" fill="#5E3618" opacity="0.5"/>')
    # the pastry-shop paper, opened out, and the gold card tray
    ppr = poly_pts([(64, 548), (110, 372), (500, 360), (550, 540)], 16, 715, 0.8)
    out.append(cast(D, 314, 548, 250, 16, strength=0.4, seed=716))
    out.append(painted(D, ppr, ("#FFFFFF", "#F8F0F0", "#D8C8CC"), 715, sdir=(0.3, 1), sk=0.08, angle=-10, n=40, inkw=1.6, hi=0.3))
    cidp = D.clip(f'<path d="{smooth_closed(ppr)}"/>')
    out.append(f'<g {cidp}>' + "".join(taper([(40, 380 + k * 34), (620, 360 + k * 34)], 3, 3, "#E87A9A", 0.35) for k in range(6)) + "</g>")
    tray = poly_pts([(124, 520), (150, 402), (464, 394), (494, 512)], 14, 717, 0.5)
    out.append(painted(D, tray, ("#FFF0A8", "#E2B04A", "#8A6418"), 717, sdir=(0.3, 1), sk=0.12, angle=-6, n=40, inkw=1.6, hi=0.45))
    out.append(ink(smooth_closed(poly_pts([(136, 512), (158, 410), (456, 402), (482, 504)], 14, 718, 0.4)), "#B8862A", 1.2, 718, 1, 0.8))
    # rows of sweets: baklava at the back, kataifi in the middle, galaktoboureko at the front
    for k in range(4):
        out.append(baklava_piece(D, 206 + k * 68, 420, 34, 720 + k))
    for k in range(4):
        out.append(kataifi_roll(D, 202 + k * 70, 458, 32, 730 + k))
    for k in range(3):
        out.append(galaktoboureko_piece(D, 222 + k * 92, 486, 42, 740 + k))
    # ribbon with curled ends falling off the paper
    bx_, by_ = 476, 396
    out.append(taper([(bx_, by_), (500, 420), (514, 456), (504, 490), (520, 516)], 8, 6, "#1F56A8"))
    out.append(taper([(bx_, by_), (500, 380), (524, 384), (532, 368)], 8, 6, "#1F56A8"))
    out.append(pline([(520, 516), (530, 532), (516, 540), (512, 528)], "#1F56A8", 3, 750, 0.95, 1))
    out.append(pline([(532, 368), (540, 354), (530, 348), (524, 358)], "#1F56A8", 3, 751, 0.95, 1))
    for sg in (-1, 1):
        out.append(painted(D, [(bx_, by_), (bx_ + sg * 30, by_ - 18), (bx_ + sg * 34, by_ + 14)], ("#5A8AE0", "#1F56A8", "#0C2C66"), 752 + sg, sk=0.2, n=4, inkw=1.2, hi=0.4))
    out.append(f'<circle cx="{bx_}" cy="{by_}" r="7" fill="#14387A"/>')
    # little card with a heart
    card = rot(rect_pts(70, 300, 160, 360, 8, 753, 0.4), 115, 330, -10)
    out.append(painted(D, card, ("#FFFFFF", "#FFF8F0", "#C8B8B0"), 753, sk=0.1, n=6, inkw=1.4, hi=0.3))
    out.append(p_heart(D, 115, 330, 13, RED, 754))
    out.append(letters(D, 300, 152, "Chronia polla!", SERIF_IT, 104, "#C8284A", ["#E04A6A", "#8A1430", "#F06A80"], 755, max_w=470,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFB0C0"))
    out.append(gr_ruled(300, 198, "ΧΡΟΝΙΑ ΠΟΛΛΑ", "#1F4FA0", size=22, ls=5, line_w=30, gap=12))
    out.append(label(300, 232, "happy name day, many happy returns", SERIF_IT, 21, "#7A3A3A", max_w=420))
    return finish_g(D, out, 756)


# ================================================================ 26. spiti mou — the little island house
def olive_tree_small(D, x, base, h, seed):
    rnd = random.Random(seed)
    out = [taper([(x, base), (x - 6, base - h * 0.3), (x + 4, base - h * 0.55)], h * 0.12, h * 0.05, "#7A6A50")]
    out.append(taper([(x - 4, base - h * 0.35), (x - h * 0.2, base - h * 0.6)], h * 0.06, h * 0.03, "#7A6A50"))
    out.append(dab_crown(D, x, base - h * 0.7, h * 0.42, h * 0.3, [OLIVE, ("#D8E0B8", "#A0AC70", "#5A6438")], seed, n=60, size=(4, 8), inkw=0))
    return "".join(out)


@design("spiti-mou")
def spiti_mou():
    D = Doc2("grsm")
    out = [sky(D, [(0, "#6AB4E8"), (0.6, "#B8E0F4"), (1, "#E8F6FA")], 761, 330, ["#C8ECF8", "#7AC0E8"], 40, sop=(0.05, 0.12))]
    out.append(puff_cloud(D, 110, 250, 120, 762, op=0.9))
    out.append(puff_cloud(D, 500, 214, 90, 763, op=0.85))
    out.append(sea(D, 300, 380, [(0, "#3A8AD0"), (1, "#5AB8D8")], 764, ["#FFFFFF", "#2A6AB0"], 40, ticks=["#FFFFFF"]))
    # hillside garden
    gl = [(-20, 372), (150, 360), (300, 364), (450, 356), (620, 368)]
    out.append(hill(D, gl, 620, ("#E8D8A8", "#C8B080", "#8A7448"), 765, angle=-6, inkw=1.2))
    out.append(grass(766, (0, 380, 600, 600), ["#A8A060", "#C8B878", "#8A8448"], n=120, h=(6, 14)))
    # the house: one whitewashed cube, blue door, two windows with open shutters, a roof terrace railing
    x0, x1, top, base = 170, 430, 300, 520
    out.append(cast(D, 320, base + 4, 200, 14, strength=0.4, seed=767))
    side = [(x1, top), (x1 + 40, top - 16), (x1 + 40, base - 16), (x1, base)]
    out.append(f'<path d="{pd(side)}" fill="#BCC6DC"/>')
    out.append(strokes(D.nid(), pd(side), bbox(side), ["#A8B6D0", "#D0D8E8"], 768, n=20, angle=-88, length=(10, 30), width=(1, 3), opacity=(0.2, 0.45)))
    front = rect_pts(x0, top, x1, base, 8, 769, 0.4)
    out.append(painted(D, front, WASH, 769, sdir=(1, 0.4), sk=0.06, angle=-85, n=60, inkw=1.6, inkop=0.5, hi=0.3))
    out.append(f'<path d="{pd([(x0 - 4, top - 8), (x1 + 4, top - 8), (x1 + 44, top - 24), (x1 + 44, top - 18), (x1 + 4, top - 2), (x0 - 4, top - 2)])}" fill="#FFFFFF"/>')
    out.append(f'<path d="M {x0 - 4} {top - 2} L {x1 + 4} {top - 2}" stroke="#A8B4CC" stroke-width="2"/>')
    # roof railing and a chimney
    for k in range(14):
        out.append(f'<rect x="{x0 + 10 + k * 18}" y="{top - 30}" width="3" height="22" fill="{AEGEAN[1]}"/>')
    out.append(f'<rect x="{x0 + 6}" y="{top - 34}" width="{x1 - x0 - 12}" height="5" fill="{AEGEAN[1]}"/>')
    out.append(painted(D, rect_pts(x1 - 46, top - 58, x1 - 22, top - 8, 6, 770, 0.3), WASH, 770, sk=0.15, n=4, inkw=1.2, hi=0.3))
    out.append(f'<path d="M {x1 - 50} {top - 58} L {x1 - 34} {top - 70} L {x1 - 18} {top - 58} Z" fill="#FFFFFF" stroke="#A8B4CC" stroke-width="1.4"/>')
    # door
    dx, dw, dh = 286, 52, 116
    dd = f"M {dx} {base} L {dx} {base - dh + dw / 2} A {dw / 2} {dw / 2} 0 0 1 {dx + dw} {base - dh + dw / 2} L {dx + dw} {base} Z"
    out.append(f'<path d="{dd}" fill="{AEGEAN[1]}"/>')
    cid = D.clip(f'<path d="{dd}"/>')
    out.append(f'<g {cid}>' + strokes(D.nid(), dd, (dx, base - dh, dx + dw, base), [AEGEAN[0], AEGEAN[2]], 771, n=20, angle=-90, length=(20, 50), width=(2, 4), opacity=(0.2, 0.45)) +
               "".join(f'<path d="M {dx + k * dw / 3:.1f} {base - dh} L {dx + k * dw / 3:.1f} {base}" stroke="{AEGEAN[2]}" stroke-width="1.6" opacity="0.6"/>' for k in (1, 2)) + "</g>")
    out.append(ink(dd, INK, 1.6, 772, 1, 0.7))
    out.append(f'<circle cx="{dx + dw - 10}" cy="{base - dh * 0.45}" r="3.4" fill="#C8A048"/>')
    out.append(f'<path d="{blob(dx + dw / 2, base - dh - 18, 10, 6, 773, 0.05, 10)}" fill="#C8A048"/>')   # a little lamp over the door
    out.append(painted(D, rect_pts(dx - 10, base - 4, dx + dw + 10, base + 6, 8, 774, 0.3), WASH, 774, sk=0.15, n=4, inkw=1, hi=0.3))
    # windows with open shutters and pots on the sills
    for k, wx in enumerate((202, 372)):
        wy, ww, wh = 360, 46, 60
        out.append(f'<rect x="{wx - 2}" y="{wy - 2}" width="{ww + 4}" height="{wh + 4}" fill="#D8DEEA"/>')
        out.append(f'<path d="{hg.org_rect(wx, wy, ww, wh, 775 + k, 0.4, 8, 1)}" fill="#2A3A5A"/>')
        out.append(f'<path d="M {wx + ww / 2} {wy} L {wx + ww / 2} {wy + wh} M {wx} {wy + wh / 2} L {wx + ww} {wy + wh / 2}" stroke="#FFFFFF" stroke-width="3"/>')
        out.append(f'<path d="{blob(wx + 12, wy + 14, 8, 10, 777 + k, 0.2, 8)}" fill="#7AA0D8" opacity="0.4"/>')
        for sg, sx in ((-1, wx - ww * 0.5), (1, wx + ww)):
            sh = [(sx, wy - 2), (sx + ww * 0.5, wy - 2), (sx + ww * 0.5, wy + wh + 2), (sx, wy + wh + 2)]
            out.append(painted(D, poly_pts(sh, 8, 779 + k + sg, 0.3), AEGEAN, 779 + k + sg, sdir=(1, 0), sk=0.2, angle=-90, n=6, inkw=1.2, hi=0.3))
            for j in range(5):
                out.append(f'<path d="M {sx + 3} {wy + 8 + j * 11} L {sx + ww * 0.5 - 3} {wy + 8 + j * 11}" stroke="{AEGEAN[2]}" stroke-width="1.6" opacity="0.7"/>')
        out.append(painted(D, rect_pts(wx - 6, wy + wh, wx + ww + 6, wy + wh + 7, 8, 781 + k, 0.3), WASH, 781 + k, sk=0.15, n=3, inkw=1, hi=0.3))
        out.append(tin_pot(D, wx + ww / 2, wy + wh, 26, 22, 783 + k, "geranium" if k else "basil"))
    # bougainvillea climbing the left corner, olive tree on the right, a bench
    out.append(taper([(178, 520), (172, 420), (180, 320)], 5, 3, "#6A4A2A"))
    out.append(bougainvillea(D, 190, 300, 70, 40, 785, n=70))
    out.append(bougainvillea(D, 166, 372, 26, 50, 786, n=30))
    out.append(olive_tree_small(D, 520, 540, 150, 787))
    out.append(painted(D, rect_pts(206, 488, 270, 498, 6, 788, 0.3), AEGEAN, 788, sk=0.2, n=4, inkw=1.2, hi=0.3))
    for x in (212, 262):
        out.append(f'<rect x="{x}" y="498" width="4" height="22" fill="{AEGEAN[2]}"/>')
    out.append(cat(D, 236, 488, 60, 789, pose="sit", eyes="open", pal=("#F8F4EC", "#D8D0C4", "#7A7068"), stripes=False))
    # path of whitewashed stones
    for k in range(6):
        out.append(f'<path d="{blob(312 + (k % 2) * 8 - k * 4, 532 + k * 13, 22 - k, 6, 790 + k, 0.2, 10)}" fill="#FFFFFF" opacity="0.9"/>')
    out.append(letters(D, 300, 132, "spiti mou", SERIF_IT, 120, "#14387A", ["#1F56A8", "#0C2462", "#2E6AC8"], 796, max_w=420,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#8AB0F0"))
    out.append(ruled(300, 176, "SPITI MOU, SPITAKI MOU", "#9A2A1E", font=JOS, size=19, ls=4, line_w=28, gap=12))
    out.append(label(300, 204, "my home, my little home", SERIF_IT, 21, "#14387A", max_w=360))
    return finish_g(D, out, 797)


# ================================================================ 27. ellada mou — the flag over the chapel and the sea
def greek_flag(D, x, y, w, seed, wave=10, phase=0.0):
    """The Greek flag (3:2, nine blue and white stripes, white cross on blue in the canton) rippling from a pole at x."""
    h = w * 2 / 3
    rnd = random.Random(seed)
    def P(u, v):
        dy = math.sin(u * 2.4 * math.pi + phase) * wave * (0.1 + 0.9 * u) + v * u * wave * 0.35
        dx = -u * u * wave * 0.5 * (0.5 + 0.5 * math.sin(v * math.pi * 2 + phase))
        return (x + u * w + dx, y + v * h + dy)
    def quad(u0, v0, u1, v1, n=10):
        pts = [P(u0 + (u1 - u0) * i / n, v0) for i in range(n + 1)] + [P(u1, v0 + (v1 - v0) * i / 3) for i in range(1, 4)]
        pts += [P(u1 - (u1 - u0) * i / n, v1) for i in range(1, n + 1)] + [P(u0, v1 - (v1 - v0) * i / 3) for i in range(1, 3)]
        return pd(pts)
    blue = "#0D5EAF"
    out = [f'<path d="{quad(0, 0, 1, 1, 30)}" fill="#FFFFFF"/>']
    for k in range(9):
        if k % 2 == 0:
            out.append(f'<path d="{quad(0, k / 9, 1, (k + 1) / 9, 30)}" fill="{blue}"/>')
    cw = (5 / 9) * h / w
    out.append(f'<path d="{quad(0, 0, cw, 5 / 9, 10)}" fill="{blue}"/>')
    out.append(f'<path d="{quad(cw * 0.4, 0, cw * 0.6, 5 / 9, 10)}" fill="#FFFFFF"/>')
    out.append(f'<path d="{quad(0, 2 / 9, cw, 3 / 9, 10)}" fill="#FFFFFF"/>')
    # folds: light and shade bands following the ripple
    for i in range(12):
        u = (i + 0.5) / 12
        sh = math.cos(u * 2.4 * math.pi + phase) * (0.4 + 0.6 * u)
        col = "#FFFFFF" if sh > 0 else "#0A1A3A"
        out.append(f'<path d="{quad(u - 0.045, 0, u + 0.045, 1, 4)}" fill="{col}" opacity="{abs(sh) * 0.28:.2f}"/>')
    out.append(ink(quad(0, 0, 1, 1, 30), "#0A2A5A", 1.2, seed, 1, 0.5))
    return "".join(out)


@design("ellada-mou")
def ellada_mou():
    D = Doc2("grem")
    out = [sky(D, [(0, "#2E7AD0"), (0.5, "#7AB8E8"), (1, "#D8EEF8")], 801, 420, ["#9ACCF0", "#4A90D8"], 50, sop=(0.05, 0.12))]
    out.append(puff_cloud(D, 470, 320, 140, 802, op=0.9))
    out.append(puff_cloud(D, 120, 360, 100, 803, op=0.85))
    out.append(sea(D, 390, 610, [(0, "#4A9AD8"), (0.4, "#1E5AA8"), (1, "#0E3A80")], 804, ["#FFFFFF", "#0E3A80", "#7AC0E8"], 80, ticks=["#FFFFFF"]))
    # distant island
    out.append(f'<path d="{smooth_open(ridge([(380, 394), (460, 372), (540, 376), (620, 388)], 805, 4, 3))} L 620 396 L 380 396 Z" fill="#8AA0C0"/>')
    # rocky headland with the chapel, bottom left
    hd = [(-20, 610), (-20, 420), (60, 410), (150, 418), (230, 446), (300, 500), (340, 560), (360, 610)]
    out.append(f'<path d="{smooth_closed(hd)}" fill="#B89A80"/>')
    out.append(f'<g {D.clip(f"<path d=\'{smooth_closed(hd)}\'/>")}>' + streaks(60, 806, (-20, 420, 360, 610), ["#D8BCA0", "#8A6A54", "#C8A88A"], w=(2, 6), length=(20, 70), opacity=(0.3, 0.6), slant=0.3) + "</g>")
    out.append(ink(smooth_open(hd[1:]), INK, 1.4, 807, 1, 0.5))
    out.append(grass(808, (0, 420, 220, 450), ["#A8A060", "#C8B878"], n=40, h=(6, 12)))
    # the chapel
    out.append(cast(D, 150, 440, 120, 10, strength=0.35, seed=809))
    out.append(cube_house(D, 70, 440, 140, 80, 810, side=0.18, door=AEGEAN, windows=0, light="left"))
    out.append(blue_dome(D, 140, 362, 48, 811))
    # bell gable at the front with a bell
    bg = [(78, 362), (78, 330), (96, 312), (114, 330), (114, 362)]
    out.append(painted(D, poly_pts(bg, 6, 812, 0.3), WASH, 812, sk=0.1, n=4, inkw=1.2, hi=0.3))
    out.append(f'<path d="M 88 340 L 88 330 A 8 8 0 0 1 104 330 L 104 340 Z" fill="#7AB8E8"/><path d="M 90 340 Q 96 326 102 340 Z" fill="#8A6A3A"/>')
    # the flagpole and the flag
    out.append(taper([(250, 470), (252, 228)], 6, 4, "#E8E4DC"))
    out.append(f'<circle cx="252" cy="226" r="5" fill="#F2D08A"/>')
    out.append(greek_flag(D, 252, 234, 250, 813, wave=16))
    for x, y in ((460, 410), (486, 420), (440, 424)):
        out.append(bird_v(x, y, 8, "#1E3A6A", 0.8))
    out.append(letters(D, 300, 120, "Ellada mou", SERIF_IT, 116, "#FFFFFF", ["#FFFFFF", "#F2F8FC", "#E8F2FA"], 814, max_w=440,
                       shadow="#0E3A80", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(gr_ruled(300, 166, "ΕΛΛΑΔΑ ΜΟΥ", "#FFFFFF", size=22, ls=5, line_w=30, gap=12))
    out.append(label(300, 196, "my Greece", SERIF_IT, 22, "#0E3A80", max_w=300))
    return finish_g(D, out, 815, "#0A1A3A", 0.8)


# ================================================================ 28. apo to chorio — the tin of oil from the village
def oil_tin(D, x, base, w, h, seed, tape_word="ΛΑΔΙ"):
    """A five-litre square tin in 3/4 view, plain and dented, with a wire handle, a screw cap and a strip of tape on
    which someone wrote ΛΑΔΙ (oil) in marker."""
    dx = w * 0.32
    dy = -w * 0.16
    out = [cast(D, x + w * 0.6, base + 2, w * 0.85, 12, strength=0.45, seed=seed)]
    front = rect_pts(x, base - h, x + w, base, 8, seed, 0.6)
    side = [(x + w, base - h), (x + w + dx, base - h + dy), (x + w + dx, base + dy), (x + w, base)]
    top = [(x, base - h), (x + dx, base - h + dy), (x + w + dx, base - h + dy), (x + w, base - h)]
    tin = ("#F4F6F8", "#C8CCD4", "#6A707C")
    out.append(painted(D, poly_pts(side, 8, seed + 1, 0.5), ("#C8CCD4", "#9AA0AC", "#4A505C"), seed + 1, sdir=(1, 0), sk=0.15, angle=-90, n=16, inkw=1.6, hi=0.3))
    out.append(painted(D, front, tin, seed, sdir=(1, 0.3), sk=0.12, angle=-88, n=40, inkw=1.8, hi=0.45))
    out.append(painted(D, poly_pts(top, 8, seed + 2, 0.4), ("#FFFFFF", "#E2E6EC", "#8A909C"), seed + 2, sdir=(0, 1), sk=0.1, angle=10, n=10, inkw=1.6, hi=0.4))
    # rolled seams and a couple of dents and old oil drips
    for (a, b) in (((x, base - h + 6), (x + w, base - h + 6)), ((x, base - 6), (x + w, base - 6))):
        out.append(pline([a, b], "#8A909C", 2, seed, 0.8, 1))
    out.append(f'<path d="{blob(x + w * 0.7, base - h * 0.3, 14, 9, seed + 3, 0.2, 10)}" fill="#8A909C" opacity="0.35"/>')
    out.append(taper([(x + w * 0.25, base - h + 8), (x + w * 0.24, base - h + 40), (x + w * 0.26, base - h + 58)], 5, 2, "#D8B830", 0.55))
    # cap and wire handle
    cx_, cy_ = x + w * 0.72 + dx * 0.5, base - h + dy * 0.5
    out.append(f'<path d="{smooth_closed(ell_pts(cx_, cy_ - 6, 14, 6, 0, 360, 14))}" fill="#C8A048"/><rect x="{cx_ - 14:.1f}" y="{cy_ - 6:.1f}" width="28" height="8" fill="#B8902A"/>'
               f'<path d="{smooth_closed(ell_pts(cx_, cy_ + 2, 14, 6, 0, 180, 10) + [(cx_ - 14, cy_ - 6)])}" fill="#A87E22"/>')
    hx0, hx1 = x + w * 0.2 + dx * 0.5, x + w * 0.45 + dx * 0.5
    out.append(pline([(hx0, base - h + dy * 0.5), (hx0 + 6, base - h - 36), (hx1 - 6, base - h - 40), (hx1, base - h + dy * 0.5)], "#3A3A40", 2.6, seed, 1, 1))
    out.append(painted(D, rect_pts(hx0 + 2, base - h - 44, hx1 - 2, base - h - 30, 6, seed + 4, 0.3), ("#4A4A50", "#1A1A20", "#0A0A0E"), seed + 4, sk=0.1, n=3, inkw=1, hi=0.4))
    # a printed green band with an olive sprig (no maker, no words)
    band = rect_pts(x, base - h * 0.28, x + w, base - h * 0.12, 8, seed + 6, 0.3)
    out.append(f'<path d="{smooth_closed(band)}" fill="#4A6A2A" opacity="0.9"/>')
    out.append(taper([(x + w * 0.2, base - h * 0.2), (x + w * 0.5, base - h * 0.22), (x + w * 0.8, base - h * 0.19)], 2, 1.4, "#E8E0A8", 0.9))
    for k in range(6):
        t = 0.25 + k * 0.1
        out.append(f'<path d="{blob(x + w * t, base - h * (0.2 + (0.025 if k % 2 else -0.02)), 7, 2.6, seed + k, 0.1, 8, 30 if k % 2 else -30)}" fill="#E8E0A8" opacity="0.9"/>')
    out.append(f'<path d="{smooth_closed(rect_pts(x + w, base - h * 0.28, x + w + dx, base - h * 0.12, 8, seed + 7, 0.2))}" fill="#2E4A1A" opacity="0" />')
    out.append(f'<path d="{pd([(x + w, base - h * 0.28), (x + w + dx, base - h * 0.28 + dy), (x + w + dx, base - h * 0.12 + dy), (x + w, base - h * 0.12)])}" fill="#2E4A1A" opacity="0.85"/>')
    # masking tape label with the word in marker
    tp = rot(rect_pts(x + w * 0.12, base - h * 0.58, x + w * 0.88, base - h * 0.34, 8, seed + 5, 0.8), x + w / 2, base - h * 0.46, -4)
    out.append(painted(D, tp, ("#FFF4D0", "#F2E2B0", "#C8B07A"), seed + 5, sdir=(0.3, 1), sk=0.1, angle=-4, n=10, inkw=0, hi=0.3))
    out.append(f'<g transform="rotate(-4 {x + w / 2} {base - h * 0.46})">' + gr_caps(x + w / 2, base - h * 0.39, tape_word, JOS, w * 0.2, "#1A1A3A", ls=3, max_w=w * 0.7, stem=0.12, hair=0.1) + "</g>")
    return "".join(out)


@design("apo-to-chorio")
def apo_to_chorio():
    D = Doc2("grac")
    out = [paper(D.nid(), "#F2E6CC", FLECK, 821)]
    out.append(blooms(822, ["#D8D0A0", "#E8D8B0", "#C8C890"], 8, (0, 0, 600, 400), (100, 200), (0.12, 0.2)))
    # dappled olive-leaf shadows on the wall
    rnd = random.Random(823)
    for _ in range(40):
        out.append(f'<path d="{blob(rnd.uniform(0, 600), rnd.uniform(0, 380), rnd.uniform(14, 30), rnd.uniform(4, 8), rnd.randint(0, 999), 0.3, 10, rnd.uniform(-40, 40))}" fill="#8A8A5A" opacity="0.12"/>')
    out.append(wood_planks(D, 400, 600, 824, NOCE, 3))
    out.append(f'<rect y="394" width="600" height="10" fill="#2A1406" opacity="0.5"/>')
    # olive branch hanging into the top left corner
    out.append(olive_branch(D, [(-20, 250), (70, 286), (160, 300), (230, 290)], 825,
                            olives=((0.35, 1, ("#7A5A6A", "#3E2230", "#1A0A12")), (0.55, 1, ("#9A9A5A", "#5E6A2A", "#2E3A12")), (0.75, -1, ("#5A3A4A", "#2E1A28", "#120810"))), w=6, leaves=16))
    # the tin
    out.append(oil_tin(D, 186, 520, 200, 256, 826))
    # a bowl of olives, bread dipped in a saucer of oil
    inside, front = bowl_side(D, 466, 470, 76, 24, 36, 827, glaze=TERRA, band=None)
    out.append(inside)
    for k in range(20):
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random())
        out.append(kalamata(466 + math.cos(a) * 58 * r, 464 + math.sin(a) * 16 * r - (1 - r) * 10, 9, rnd.uniform(0, 180)))
    out.append(front)
    out.append(plate_34(D, 452, 552, 86, 26, 828, glaze=WHITE, rim=AEGEAN[1]))
    out.append(f'<path d="{smooth_closed(ell_pts(452, 552, 62, 17, 0, 360, 20))}" fill="#D8B828" opacity="0.85"/>')
    out.append(taper([(424, 548), (452, 544), (478, 548)], 2, 2, "#FFF2A0", 0.8))
    out.append(bread_slice(D, 486, 540, 86, 829, rot_=-20))
    out.append(letters(D, 300, 134, "apo to chorio", SERIF_IT, 104, "#4A5A1E", ["#5E6E2A", "#2E3A0E", "#7A8A3A"], 830, max_w=460,
                       shadow="#F8EED8", soff=(0.02, 0.035), angle=-40, hi="#C8D890"))
    out.append(ruled(300, 178, "OLIVE OIL FROM THE VILLAGE", "#8A3A10", font=JOS, size=19, ls=4, line_w=26, gap=12))
    return finish_g(D, out, 831)


# ================================================================ 29. kali orexi — the meze table from above
def round_dish(D, cx, cy, r, seed, glaze=WHITE, rim=None):
    out = [f'<circle cx="{cx + 5:.1f}" cy="{cy + 7:.1f}" r="{r:.1f}" fill="#2A1A0A" opacity="0.2"/>']
    out.append(painted(D, ell_pts(cx, cy, r, r, 0, 360, 30), glaze, seed, sdir=(0.5, 0.8), sk=0.06, angle=-20, n=12, inkw=1.6, hi=0.4))
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.74:.1f}" fill="{dk(glaze[1], 0.04)}"/>')
    if rim:
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.87:.1f}" fill="none" stroke="{rim}" stroke-width="{max(2, r * 0.05):.1f}"/>')
    return "".join(out)


def dolma(D, cx, cy, s, ang, seed):
    pts = rot(rect_pts(cx - s, cy - s * 0.42, cx + s, cy + s * 0.42, 6, seed, 0.8), cx, cy, ang)
    out = [painted(D, pts, ("#B8C878", "#6A7A34", "#2E3A12"), seed, sdir=(0.5, 0.8), sk=0.25, n=6, inkw=1.2, hi=0.45)]
    for k in range(3):
        a, b = rot([(cx - s * 0.6 + k * s * 0.5, cy - s * 0.4), (cx - s * 0.4 + k * s * 0.5, cy + s * 0.4)], cx, cy, ang)
        out.append(pline([a, b], "#3E4A1A", 1.2, seed + k, 0.6, 1))
    out.append(f'<path d="{blob(*rot([(cx - s * 0.3, cy - s * 0.15)], cx, cy, ang)[0], s * 0.35, s * 0.1, seed, 0.2, 8, ang)}" fill="#F2F8C8" opacity="0.45"/>')
    return "".join(out)


def keftes(D, cx, cy, r, seed):
    out = [painted(D, blob_pts(cx, cy, r, r * 0.92, seed, 0.1, 12), ("#C8804A", "#8A4A22", "#3A1A08"), seed, sdir=(0.5, 0.8), sk=0.25, n=6, inkw=1.2, hi=0.4)]
    out.append(specks(seed, (cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7), ["#2E6A2A", "#E8B880", "#3A1A08"], int(r), (0.6, 1.4), (0.6, 1)))
    return "".join(out)


@design("kali-orexi")
def kali_orexi():
    D = Doc2("grko")
    # paper tablecloth with a blue meander print, seen from above
    out = [paper(D.nid(), "#FBFAF6", "#7A8AA8", 841)]
    out.append(meander_band(D, -10, 610, 0, 34, "#1F56A8", None, 842, rule=True, op=0.75))
    out.append(meander_band(D, -10, 610, 566, 34, "#1F56A8", None, 843, rule=True, op=0.75))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFF6E0", 0.0), (1, "#3A4A6A", 0.18)], 0.5, 0.5, 0.75)}"/>')
    rnd = random.Random(844)
    # tzatziki
    out.append(round_dish(D, 150, 330, 74, 845, rim=AEGEAN[1]))
    out.append(f'<path d="{blob(150, 330, 53, 51, 846, 0.08, 16)}" fill="#F8FAF2"/>')
    out.append(specks(847, (110, 290, 190, 370), ["#4A8A3A", "#2E6A2A"], 30, (0.8, 1.6), (0.7, 1)))
    out.append(f'<path d="{blob(160, 322, 18, 10, 848, 0.3, 10)}" fill="#D8C030" opacity="0.6"/>')
    out.append(kalamata(146, 332, 9, 30))
    for k in range(4):
        out.append(f'<path d="{blob(116 + k * 4, 300 + k * 14, 9, 3, 849 + k, 0.2, 8, 30)}" fill="#C8E0A8" stroke="#6A9A4A" stroke-width="1"/>')
    # dolmades on a long plate
    out.append(round_dish(D, 300, 420, 86, 850, glaze=("#FFFFFF", "#F2EEE6", "#B8B0A6"), rim=AEGEAN[1]))
    for k, (x, y, a) in enumerate(((262, 394, 20), (300, 386, 20), (338, 394, 20), (262, 430, 20), (300, 424, 20), (338, 434, 20))):
        out.append(dolma(D, x, y, 22, a, 851 + k))
    lw = [(316, 470), (346, 452), (360, 462), (334, 480)]
    out.append(painted(D, [(318, 452), (356, 440), (352, 460)], LEMON, 857, sk=0.15, n=4, inkw=1.2, hi=0.4))
    # keftedes
    out.append(round_dish(D, 456, 316, 74, 858, glaze=TERRA))
    for k, (x, y) in enumerate(((432, 298), (466, 290), (486, 320), (446, 332), (472, 348), (424, 334))):
        out.append(keftes(D, x, y, 17, 859 + k))
    # feta with oregano and oil
    out.append(round_dish(D, 474, 478, 60, 865, rim=AEGEAN[1]))
    out.append(painted(D, rot(rect_pts(444, 456, 504, 500, 8, 866, 1), 474, 478, 12), FETA, 866, sk=0.1, n=6, inkw=1.2, hi=0.3))
    out.append(specks(867, (448, 460, 500, 496), ["#5A6A2A", "#7A8A3A"], 24, (0.8, 1.6), (0.8, 1)))
    out.append(taper([(452, 474), (472, 470), (494, 478)], 4, 2, "#E8D060", 0.6))
    # olives, bread basket
    out.append(round_dish(D, 122, 470, 50, 868, glaze=WHITE))
    for k in range(9):
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 26
        out.append(kalamata(122 + math.cos(a) * r, 470 + math.sin(a) * r, 8, rnd.uniform(0, 180)))
    for k, (x, y, a) in enumerate(((196, 530, -14), (240, 526, 6))):
        out.append(bread_slice(D, x, y, 70, 870 + k, rot_=a))
    # cutlery and two glasses of wine from above
    out.append(taper([(360, 556), (420, 506)], 5, 4, "#9AA2AE"))
    for j in range(4):
        out.append(taper([(418 + j * 3, 500 + j * 3), (434 + j * 3, 486 + j * 3)], 2, 1.6, "#9AA2AE"))
    out.append(f'<circle cx="330" cy="520" r="26" fill="#E8F0F4" opacity="0.6"/><circle cx="330" cy="520" r="19" fill="#8A1424"/><circle cx="324" cy="514" r="4" fill="#FFFFFF" opacity="0.6"/>' + ink(smooth_closed(ell_pts(330, 520, 26, 26, 0, 360, 20)), "#7A8A90", 1.4, 872, 1, 0.8))
    out.append(letters(D, 300, 148, "Kali orexi!", SERIF_IT, 120, "#14387A", ["#1F56A8", "#0C2462", "#2E6AC8"], 873, max_w=440,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#8AB0F0"))
    out.append(ruled(300, 196, "ENJOY YOUR MEAL", "#9A2A1E", font=JOS, size=20, ls=5, line_w=34, gap=14))
    return finish_g(D, out, 874)


# ================================================================ 30. avgolemono — yiayia's egg-lemon soup
@design("avgolemono")
def avgolemono():
    D = Doc2("grav")
    out = [paper(D.nid(), "#FFF6DC", FLECK, 881)]
    out.append(blooms(882, ["#FFE89A", "#F8F0C0", "#E8F0D0"], 8, (0, 0, 600, 600), (100, 200), (0.12, 0.2)))
    # a lemon branch from the yard reaching in at the top right
    out.append(branch(D, [(640, 238), (560, 262), (480, 250), (430, 268)], 9, 3, 897))
    for k, (x, y, L, ang) in enumerate(((560, 262, 50, 120), (520, 255, 46, -60), (480, 250, 44, 110), (450, 262, 40, -150), (600, 250, 46, -80), (500, 254, 40, 70))):
        out.append(citrus_leaf(D, x, y, L, ang, 898 + k))
    out.append(lemon_it(D, 536, 306, 22, 904, rot_=80, leaf=False))
    out.append(lemon_it(D, 470, 296, 18, 905, rot_=100, leaf=False))
    # blue gingham cloth on the table
    out.append(wood_planks(D, 350, 600, 883, WOOD, 3))
    tc = poly_pts([(30, 610), (90, 384), (560, 376), (600, 610)], 16, 884, 0.6)
    out.append(cloth(D, tc, AEGEAN[1], 884, cell=16, rot_=-4, light=(0, 0, 0.3, 1), inkw=1.4))
    out.append(soft_glow(D, 300, 420, 220, "#FFF4C0", 0.5))
    # the soup bowl
    cx, cy, rx, ry = 290, 430, 170, 52
    out.append(cast(D, cx + 12, cy + ry + 54, rx * 0.8, 16, strength=0.45, seed=885))
    inside, front = bowl_side(D, cx, cy, rx, ry, 70, 886, glaze=WHITE, band=AEGEAN)
    out.append(inside)
    soup = ell_pts(cx, cy + 4, rx - 10, ry - 7, 0, 360, 36)
    out.append(f'<path d="{smooth_closed(soup)}" fill="{D.rad([(0, "#FFF6C8"), (0.7, "#F6E09A"), (1, "#E8C870")], 0.4, 0.4, 0.7)}"/>')
    rnd = random.Random(887)
    for _ in range(80):   # rice grains
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random())
        x, y = cx + math.cos(a) * (rx - 22) * r, cy + 4 + math.sin(a) * (ry - 12) * r
        out.append(f'<path d="{blob(x, y, 3, 1.4, rnd.randint(0, 999), 0.1, 6, rnd.uniform(0, 180))}" fill="#FFFDF2" stroke="#E0C88A" stroke-width="0.5"/>')
    for k in range(5):   # shreds of chicken
        x, y = cx + rnd.uniform(-80, 80), cy + rnd.uniform(-14, 14)
        out.append(f'<path d="{blob(x, y, 10, 4, 888 + k, 0.3, 8, rnd.uniform(-30, 30))}" fill="#F2DCB0" stroke="#C8A070" stroke-width="0.8"/>')
    out.append(specks(889, (cx - 100, cy - 20, cx + 100, cy + 24), ["#2A1A10"], 30, (0.5, 1.2), (0.5, 0.9)))   # black pepper
    out.append(f'<path d="{blob(cx - 50, cy - 6, 30, 6, 890, 0.2, 10)}" fill="#FFFFFF" opacity="0.4"/>')
    out.append(front)
    out.append(steam(cx, cy - 26, 90, 891, "#FFFFFF", 3, 40, 8, 0.65))
    # lemons and a wooden spoon
    for k, (x, y, r_, a) in enumerate(((104, 486, 30, -20), (150, 520, 28, 30))):
        out.append(lemon_it(D, x, y, r_, 892 + k, rot_=a, leaf=False))
    half = ell_pts(498, 506, 38, 24, 0, 360, 20)
    out.append(painted(D, half, LEMON, 894, sk=0.15, n=6, inkw=1.6, hi=0.4))
    out.append(f'<path d="{smooth_closed(ell_pts(498, 503, 32, 19, 0, 360, 20))}" fill="#FFF6B8"/>')
    for k in range(10):
        a = math.radians(k * 36)
        out.append(f'<path d="M 498 503 L {498 + math.cos(a) * 28:.1f} {503 + math.sin(a) * 16:.1f}" stroke="#E8D060" stroke-width="1.8"/>')
    out.append(f'<circle cx="498" cy="503" r="4" fill="#F2E080"/>')
    out.append(taper([(400, 560), (470, 590), (540, 600)], 9, 7, "#C8925A"))
    out.append(letters(D, 300, 162, "avgolemono", SERIF_IT, 112, "#B87A0A", ["#D89A1A", "#8A5A06", "#E8B030"], 895, max_w=460,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFE890"))
    out.append(ruled(300, 206, "THE CURE FOR EVERYTHING", "#1F56A8", font=JOS, size=20, ls=5, line_w=30, gap=12))
    return finish_g(D, out, 896)


def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
