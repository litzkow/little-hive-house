"""Americana, hand-painted (gouache / storybook) edition: 30 magnets of everyday American life.

Not landmarks (those live in the USA Places set) but the things Americans grew up with: the chrome diner with
its neon EAT sign, pie cooling on the sill, the county fair, the lemonade stand, sweet tea on the porch, the
Fourth of July cookout, Main Street, the red barn, the yellow school bus, Friday-night football, the drive-in,
the mailbox with its little red flag, s'mores, Southern biscuits, Texas brisket, a Maine lobster roll, a
Chicago deep dish, and a few sayings ("Bless your heart", "Y'all come back now").

Painted in the house gouache idiom shared with the Brasil set: warm paper, layered washes with pooled edges,
brush strokes that follow each form, a warm brown pen line, hand-placed lettering, soft light and paper grain.
Colour story: barn red, faded denim and navy, cream, mustard, diner aqua and warm wood.
No brands, logos, team marks or lyrics (the 1908 ball-game title and the 1814 anthem line are public domain).

Run from tools/designs:  python3 americana_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (qpts, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline, ridge,
                            ruled, shift, sky, soft_glow, specks, taper, blooms, apple, mist)
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from poster import ANTON
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, lemon, citrus_slice
from brasil_painted import (Doc2, ell_pts, pd, shade_over, light_over, gingham, cloth, wood_planks, steam, leaf_simple,
                            bird_v, heart_d, p_heart, stitched, lazy_daisy, stitch_leaf)
import holidays_gouache as hg
import figures

COL = "americana"
INK = "#3A2418"
FLECK = "#8A6A4A"

lt, dk = hg.lt, hg.dk

# (light, base, dark) gouache palettes
BARN = ("#EE8A72", "#B8352A", "#6A1812")
CHERRY = ("#FF8A7A", "#D8302A", "#821010")
NAVY = ("#6A86C0", "#243C70", "#0E1C3E")
DENIM = ("#9AB6D8", "#5A7AA8", "#2A4068")
CREAM = ("#FFFDF4", "#F2E6CC", "#C4AE88")
WHITE = ("#FFFFFF", "#F4F0E8", "#B8B0A6")
MUSTARD = ("#FFE08A", "#EAAE3A", "#A8701E")
AQUA = ("#AEE8E0", "#4AB2A8", "#1E6A64")
SAGE = ("#C8D6A8", "#8AA070", "#4E6440")
GRASS = ("#B8D87A", "#6A9A3E", "#2E5A22")
WOOD = ("#D8A06A", "#A86A3A", "#5E3618")
OAK = ("#E8C08A", "#C08A52", "#7A5228")
CHROME = ("#FFFFFF", "#C8D0DA", "#5E6878")
CRUST = ("#FCE2A0", "#E0A04A", "#9A5A1A")
LEATHER = ("#F0A868", "#B8682E", "#6A3412")
IRON = ("#6A6870", "#33323A", "#141318")

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def finish_a(D, out, seed, color=INK, op=1.0):
    return finish(D, out, seed, color, op)


def pal3(c, a=0.38, b=0.4):
    return (lt(c, a), c, dk(c, b))


def pp(corners, step=12, seed=0, j=0.4):
    """Polygon corners -> dense, slightly hand-drawn point list (keeps edges straight under smooth_closed)."""
    return poly_pts(corners, step, seed, j)


# ================================================================ americana toolkit
def neon(D, x, y, s, font, size, col, seed, ls=0, max_w=400, anchor="middle", core="#FFF8F0", glow=True, flicker=None):
    """Glass neon tube lettering: a wide soft halo, the coloured tube and a white-hot core (no filters)."""
    fs = fit_size(s, font, size, max_w, ls)
    lsa = f' letter-spacing="{ls}"' if ls else ""
    t = lambda st, w, op: (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" {font} font-size="{fs}"{lsa} fill="none" stroke="{st}" '
                          f'stroke-width="{w:.1f}" stroke-linejoin="round" opacity="{op}">{esc(s)}</text>')
    out = []
    if glow:
        W = measure(s, font, fs, ls)
        cx = x if anchor == "middle" else x + W / 2
        out.append(D.glow(cx, y - fs * 0.35, max(W, fs) * 0.75, col, 0.45))
    out += [t(col, fs * 0.22, 0.10), t(col, fs * 0.13, 0.18), t(col, fs * 0.075, 0.45), t(col, fs * 0.045, 1.0), t(core, fs * 0.016, 0.95)]
    return "".join(out)


def neon_path(D, d, col, w=5, core="#FFF8F0", glow=None):
    out = []
    if glow:
        out.append(D.glow(*glow, col, 0.4))
    for k, op in ((4.4, 0.1), (2.6, 0.18), (1.5, 0.45), (1.0, 1.0)):
        out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w * k:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>')
    out.append(f'<path d="{d}" fill="none" stroke="{core}" stroke-width="{w * 0.36:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="0.95"/>')
    return "".join(out)


def stars_field(seed, n, box, col="#FFF6D8", r=(0.6, 1.8), op=(0.4, 1.0), avoid=()):
    rnd = random.Random(seed)
    out = []
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if any(a[0] < x < a[2] and a[1] < y < a[3] for a in avoid):
            continue
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(*r):.1f}" fill="{col}" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


def car50(D, x, base, L, seed, body=AQUA, roof=CREAM, flip=1, lights=False, tail=False, shadow=True):
    """A generic 1950s two-tone sedan in side view (no badges): rounded fenders, chrome spear and bumpers,
    whitewall tyres. (x, base) = centre of the car on the ground; L = overall length; flip=1 faces right."""
    def P(u, v):
        return (x + u * L * flip, base + v * L)
    out = []
    if shadow:
        out.append(cast(D, x, base + 1, L * 0.55, L * 0.035, strength=0.55, seed=seed))
    # lower body
    bodyp = [(-0.5, -0.07), (-0.505, -0.13), (-0.48, -0.175), (-0.40, -0.19), (-0.27, -0.2), (-0.2, -0.205), (0.17, -0.205),
             (0.3, -0.198), (0.42, -0.188), (0.49, -0.165), (0.505, -0.12), (0.5, -0.07), (0.38, -0.055), (-0.38, -0.055)]
    cab = [(-0.27, -0.2), (-0.2, -0.31), (-0.13, -0.335), (0.06, -0.335), (0.13, -0.31), (0.21, -0.205)]
    cpts = [P(u, v) for u, v in cab]
    out.append(painted(D, cpts, roof, seed + 1, sdir=(0, 1), sk=0.12, angle=0, n=8, inkw=1.6, hi=0.5, hik=0.12))
    # windows
    for wp in ([(-0.235, -0.205), (-0.185, -0.29), (-0.125, -0.312), (-0.05, -0.312), (-0.05, -0.205)],
               [(-0.025, -0.205), (-0.025, -0.312), (0.05, -0.312), (0.115, -0.292), (0.175, -0.205)]):
        pp = [P(u, v) for u, v in wp]
        g = D.lin([(0, "#E8F4F8"), (0.45, "#8AB0C8"), (1, "#3A5068")])
        out.append(f'<path d="{smooth_closed(pp)}" fill="{g}"/>')
        out.append(taper([P(wp[1][0] + 0.03, wp[1][1] + 0.01), P(wp[1][0] + 0.06, wp[0][1] - 0.01)], 2.2, 1, "#FFFFFF", 0.7))
        out.append(ink(smooth_closed(pp), "#E8ECF0", 1.6, seed, 1, 0.9))
    bp = [P(u, v) for u, v in bodyp]
    out.append(painted(D, bp, body, seed, sdir=(0, 1), sk=0.14, angle=0, n=22, slen=(L * 0.05, L * 0.16), sw=(1, 2.4), inkw=1.8, hi=0.55, hik=0.1))
    # two-tone swoop on the flank and chrome spear
    sw_ = [P(u, v) for u, v in [(-0.46, -0.165), (-0.1, -0.15), (0.2, -0.125), (0.44, -0.12), (0.44, -0.105), (0.2, -0.11), (-0.1, -0.13), (-0.46, -0.14)]]
    out.append(f'<path d="{smooth_closed(sw_)}" fill="{roof[1]}"/>')
    out.append(ink(smooth_open([P(-0.47, -0.168), P(-0.1, -0.153), P(0.2, -0.128), P(0.45, -0.122)]), "#FFFFFF", 2.2, seed + 3, 1, 0.95))
    out.append(ink(smooth_open([P(-0.47, -0.138), P(-0.1, -0.128), P(0.2, -0.108), P(0.45, -0.102)]), "#6A7280", 1.4, seed + 4, 1, 0.8))
    # door seam and handle
    out.append(pline([P(-0.03, -0.2), P(-0.035, -0.12), P(-0.03, -0.065)], dk(body[2], 0.2), 1.3, seed, 0.7, 1))
    hx, hy = P(-0.07, -0.17)
    out.append(f'<path d="M {hx:.1f} {hy:.1f} l {-8 * flip * L / 200:.1f} 0" stroke="#F4F6FA" stroke-width="2.4" stroke-linecap="round"/>')
    # bumpers
    for u0, u1 in ((-0.52, -0.43), (0.43, 0.52)):
        a, b = P(u0, -0.09), P(u1, -0.06)
        out.append(f'<path d="{hg.org_rect(min(a[0], b[0]), a[1], abs(b[0] - a[0]), b[1] - a[1], seed + int(u0 * 10), 0.2, 6, 3)}" fill="#D8DEE6"/>')
        out.append(f'<path d="M {min(a[0], b[0]) + 2:.1f} {a[1] + 2:.1f} L {max(a[0], b[0]) - 2:.1f} {a[1] + 2:.1f}" stroke="#FFFFFF" stroke-width="1.6" opacity="0.9"/>')
    # lights
    fx, fy = P(0.49, -0.14)
    rx_, ry_ = P(-0.495, -0.15)
    out.append(f'<path d="{blob(fx, fy, L * 0.012, L * 0.02, seed, 0.05, 8)}" fill="#FFF6C8"/>')
    out.append(f'<path d="{blob(rx_, ry_, L * 0.01, L * 0.022, seed + 1, 0.05, 8)}" fill="#E8302A"/>')
    if lights:
        out.append(D.glow(fx + 10 * flip, fy, L * 0.25, "#FFE8A0", 0.5))
    if tail:
        out.append(D.glow(rx_, ry_, L * 0.12, "#FF4A3A", 0.55))
    # wheels with whitewalls and chrome caps
    for u in (-0.3, 0.31):
        wx, wy = P(u, -0.062)
        r = L * 0.068
        out.append(f'<path d="{blob(wx, wy - r * 0.2, r * 1.25, r * 1.05, seed + 7, 0.02, 14)}" fill="{dk(body[2], 0.5)}"/>')
        out.append(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="{r:.1f}" fill="#1C1A20"/>')
        out.append(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="{r * 0.68:.1f}" fill="#F4F2EC"/>')
        out.append(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="{r * 0.46:.1f}" fill="{D.rad([(0, "#FFFFFF"), (0.6, "#C8CED8"), (1, "#6A7280")], 0.4, 0.35, 0.7)}"/>')
        out.append(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="{r * 0.12:.1f}" fill="#5E6878"/>')
        out.append(ink(f"M {wx - r:.1f} {wy:.1f} a {r:.1f} {r:.1f} 0 1 0 {2 * r:.1f} 0 a {r:.1f} {r:.1f} 0 1 0 {-2 * r:.1f} 0", "#0A0A0E", 1.4, seed, 1, 0.7))
    return "".join(out)


def us_flag(D, x, y, w, h, seed, wave=0.1, flip=1, stars=True, inkw=1.2):
    """A waving Stars and Stripes hung from its hoist at (x, y): 13 stripes, a navy canton with stars,
    shading in the folds. flip=-1 flies it to the left."""
    ph = random.Random(seed).uniform(0, 6.28)

    def P(u, v):
        dy = wave * h * math.sin(2 * math.pi * u * 1.3 + ph) * u
        return (x + u * w * flip, y + v * h + dy)

    def band(u0, u1, v0, v1, n=10):
        top = [P(u0 + (u1 - u0) * i / n, v0) for i in range(n + 1)]
        bot = [P(u0 + (u1 - u0) * i / n, v1) for i in range(n, -1, -1)]
        return pd(top + bot)

    out = []
    outline = band(0, 1, 0, 1, 16)
    out.append(f'<path d="{outline}" fill="#F6F2EA"/>')
    for i in range(0, 13, 2):
        out.append(f'<path d="{band(0, 1, i / 13, (i + 1) / 13, 16)}" fill="#C8302A"/>')
    out.append(f'<path d="{band(0, 0.42, 0, 7 / 13, 8)}" fill="#22386A"/>')
    if stars:
        for r_ in range(5):
            for c_ in range(6 if r_ % 2 == 0 else 5):
                u = 0.035 + (c_ + (0.5 if r_ % 2 else 0)) * 0.066
                v = 0.06 + r_ * 0.1
                sx, sy = P(u, v)
                out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{max(0.7, h * 0.018):.1f}" fill="#FFFFFF"/>')
    # fold shading
    for k in range(12):
        u0, u1 = k / 12, (k + 1) / 12
        slope = math.cos(2 * math.pi * (u0 + u1) / 2 * 1.3 + ph)
        if slope > 0:
            out.append(f'<path d="{band(u0, u1, 0, 1, 2)}" fill="#1A0A10" opacity="{0.22 * slope:.2f}"/>')
        else:
            out.append(f'<path d="{band(u0, u1, 0, 1, 2)}" fill="#FFFFFF" opacity="{-0.14 * slope:.2f}"/>')
    if inkw:
        out.append(ink(outline, INK, inkw, seed, 1, 0.6))
    return "".join(out)


def picket_fence(D, x0, x1, top, bot, seed, w=15, gap=9, pal=WHITE, shade="#7A8AA8", rails=True):
    """Painted white picket fence: pointed pickets, two rails behind, soft shade on one side."""
    out = []
    rnd = random.Random(seed)
    if rails:
        for ry in (top + (bot - top) * 0.28, top + (bot - top) * 0.72):
            out.append(painted(D, rect_pts(x0 - 10, ry - 4, x1 + 10, ry + 4, 30, seed + int(ry), 0.4), pal, seed + int(ry), sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.1, inkop=0.5, hi=0.2))
    x = x0
    k = 0
    while x < x1:
        h = rnd.uniform(-2, 2)
        pts = [(x, bot), (x, top + w * 0.5 + h), (x + w / 2, top + h), (x + w, top + w * 0.5 + h), (x + w, bot)]
        out.append(painted(D, pts, pal, seed + k, sdir=(1, 0.2), sk=0.18, angle=-90, n=4, inkw=1.2, inkop=0.55, hi=0.4, hik=0.1))
        out.append(f'<path d="M {x + w * 0.72:.1f} {top + w * 0.6 + h:.1f} L {x + w * 0.72:.1f} {bot - 2:.1f}" stroke="{shade}" stroke-width="{w * 0.3:.1f}" opacity="0.18"/>')
        x += w + gap
        k += 1
    return "".join(out)


def bulbs_row(D, pts, seed, col="#FFE6A0", r=3.2, glow=True):
    out = []
    for i, (x, y) in enumerate(pts):
        if glow:
            out.append(D.glow(x, y, r * 4.5, col, 0.45))
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}"/><circle cx="{x - r * 0.3:.1f}" cy="{y - r * 0.3:.1f}" r="{r * 0.4:.1f}" fill="#FFFFFF"/>')
    return "".join(out)


def fluted(D, d, box, seed, top="#2A3A6A", mid="#E8EEF4", bot="#7A6A7A", step=7, hor=True, warm=None):
    """Polished stainless panel: a sky-to-ground reflection gradient with ribbed flutes."""
    x0, y0, x1, y1 = box
    stops = [(0, top), (0.42, mid), (0.55, "#FFFFFF"), (0.7, mid), (1, bot)]
    g = D.lin(stops) if hor else D.lin(stops, 0, 0, 1, 0)
    out = [f'<path d="{d}" fill="{g}"/>']
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    if hor:
        y = y0 + step / 2
        while y < y1:
            inner.append(f'<path d="M {x0 - 5:.1f} {y:.1f} L {x1 + 5:.1f} {y:.1f}" stroke="#FFFFFF" stroke-width="1.4" opacity="0.5"/>')
            inner.append(f'<path d="M {x0 - 5:.1f} {y + step * 0.45:.1f} L {x1 + 5:.1f} {y + step * 0.45:.1f}" stroke="#20283A" stroke-width="1.2" opacity="0.28"/>')
            y += step
    else:
        x = x0 + step / 2
        while x < x1:
            inner.append(f'<path d="M {x:.1f} {y0 - 5:.1f} L {x:.1f} {y1 + 5:.1f}" stroke="#FFFFFF" stroke-width="1.4" opacity="0.5"/>')
            inner.append(f'<path d="M {x + step * 0.45:.1f} {y0 - 5:.1f} L {x + step * 0.45:.1f} {y1 + 5:.1f}" stroke="#20283A" stroke-width="1.2" opacity="0.28"/>')
            x += step
    if warm:
        inner.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{D.lin([(0, warm, 0), (1, warm, 0.35)], 0, 0, 1, 0)}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(out)


def ticket_stub(D, cx, cy, w, h, ang, seed, col=("#FFE8A8", "#F2C860", "#B88A2A"), lines=("ADMIT ONE",), font=BEBAS, size=20, ink_c="#7A2A14"):
    """A torn paper ticket (notched corners, perforated end) with printed lines."""
    pts = [(cx - w / 2 + 6, cy - h / 2), (cx + w / 2 - 6, cy - h / 2), (cx + w / 2, cy - h / 2 + 6), (cx + w / 2, cy + h / 2 - 6),
           (cx + w / 2 - 6, cy + h / 2), (cx - w / 2 + 6, cy + h / 2), (cx - w / 2, cy + h / 2 - 6), (cx - w / 2, cy - h / 2 + 6)]
    out = [f'<g transform="rotate({ang} {cx:.1f} {cy:.1f})">', cast(D, cx + 4, cy + h * 0.4, w * 0.52, h * 0.3, strength=0.3, seed=seed)]
    out.append(painted(D, pts, col, seed, sdir=(0.3, 1), sk=0.08, angle=0, n=14, inkw=1.4, hi=0.3))
    out.append(f'<path d="{hg.org_rect(cx - w / 2 + 7, cy - h / 2 + 6, w - 14, h - 12, seed + 1, 0.3, 10, 2)}" fill="none" stroke="{ink_c}" stroke-width="1.4" opacity="0.7"/>')
    for k in range(int(h / 7)):
        out.append(f'<circle cx="{cx + w / 2 - 16:.1f}" cy="{cy - h / 2 + 6 + k * 7:.1f}" r="1.3" fill="{ink_c}" opacity="0.6"/>')
    n = len(lines)
    for i, s in enumerate(lines):
        fs = fit_size(s, font, size, w - 38)
        yy = cy + (i - (n - 1) / 2) * (fs * 1.05) + fs * 0.35
        out.append(f'<text x="{cx - 8:.1f}" y="{yy:.1f}" text-anchor="middle" {font} font-size="{fs}" fill="{ink_c}">{esc(s)}</text>')
    out.append("</g>")
    return "".join(out)


def gingham_cloth_top(D, pts, col, seed, cell=16, rot_=12, base="#FFFDF6"):
    return cloth(D, pts, col, seed, base=base, cell=cell, rot_=rot_, light=(0.0, 0.0, 1.0, 1.0))


# ---------------------------------------------------------------- pies
def apple_filling(D, d, box, seed, pal=("#F6D27A", "#D89A3A", "#7A3A10")):
    """Glossy baked-apple filling: amber syrup with sliced apple crescents and cinnamon specks."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = [f'<path d="{d}" fill="{pal[2]}"/>']
    cid = D.clip(f'<path d="{d}"/>')
    inner = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{D.lin([(0, "#B8681E", 0.6), (1, "#5A2408", 0.5)])}"/>']
    for _ in range(int((x1 - x0) * (y1 - y0) / 140)):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        a = rnd.uniform(0, 180)
        s = rnd.uniform(7, 12)
        inner.append(f'<path d="{blob(x, y, s, s * 0.42, rnd.randint(0, 9999), 0.12, 10, a)}" fill="{rnd.choice([pal[0], pal[1], "#E8B05A"])}" opacity="0.95"/>')
        inner.append(f'<path d="M {x - s * 0.7 * math.cos(math.radians(a)):.1f} {y - s * 0.7 * math.sin(math.radians(a)):.1f} l {s * 1.2 * math.cos(math.radians(a)):.1f} {s * 1.2 * math.sin(math.radians(a)):.1f}" stroke="#FFF2C0" stroke-width="1.2" opacity="0.6"/>')
    inner.append(specks(seed + 3, box, ["#5A2A0A", "#7A3A10"], int((x1 - x0) * 0.5), (0.6, 1.4), (0.4, 0.8)))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(out)


def cherry_filling(D, d, box, seed):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = [f'<path d="{d}" fill="#6A0A14"/>']
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for _ in range(int((x1 - x0) * (y1 - y0) / 110)):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(5, 8)
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{rnd.choice(["#B8142A", "#9A0A1E", "#D8283A"])}"/>')
        inner.append(f'<circle cx="{x - r * 0.35:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.3:.1f}" fill="#FFC8C8" opacity="0.7"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(out)


def lattice_pie(D, cx, cy, rx, ry, seed, filling="apple", depth=None, strips=6, pan=True, crust=CRUST, sugar=True):
    """Lattice-top pie in a tin, seen at an angle: tin side, golden crimped rim, woven lattice over a
    glossy filling peeking through. (cx, cy) = centre of the top ellipse."""
    rnd = random.Random(seed)
    depth = depth if depth is not None else ry * 0.55
    out = [cast(D, cx + rx * 0.06, cy + depth + ry * 0.35, rx * 1.15, ry * 0.5, strength=0.45, seed=seed)]
    if pan:
        top = ell_pts(cx, cy + 2, rx * 1.06, ry * 1.06, 0, 180, 24)
        bot = ell_pts(cx, cy + depth, rx * 0.92, ry * 0.92, 0, 180, 24)
        side = top + bot[::-1]
        g = D.lin([(0, "#E8ECF0"), (0.18, "#9AA2AE"), (0.45, "#F4F6F8"), (0.7, "#A8AEB8"), (1, "#5E6470")], 0, 0, 1, 0)
        sd = pd(side)
        out.append(f'<path d="{sd}" fill="{g}"/>')
        cid0 = D.clip(f'<path d="{sd}"/>')
        flutes = "".join(f'<path d="M {cx + rx * 1.06 * math.cos(math.radians(a)):.1f} {cy + ry * 1.06 * math.sin(math.radians(a)) + 2:.1f} L {cx + rx * 0.92 * math.cos(math.radians(a)):.1f} {cy + depth + ry * 0.92 * math.sin(math.radians(a)):.1f}" stroke="#5E6470" stroke-width="1.2" opacity="0.35"/>'
                         for a in range(4, 180, 9))
        out.append(f'<g {cid0}>{flutes}</g>')
        out.append(ink(sd, INK, 1.6, seed, 1, 0.6))
    # crust disc (the rim) and the filling well
    rim = blob_pts(cx, cy, rx, ry, seed + 1, 0.015, 40)
    out.append(painted(D, rim, crust, seed + 2, sdir=(0.4, 1), sk=0.12, angle=0, n=40, inkw=1.6, inkop=0.6, hi=0.35))
    well_d = blob(cx, cy - ry * 0.02, rx * 0.84, ry * 0.8, seed + 3, 0.02, 30)
    box = (cx - rx, cy - ry, cx + rx, cy + ry)
    if filling == "cherry":
        out.append(cherry_filling(D, well_d, box, seed + 4))
    else:
        out.append(apple_filling(D, well_d, box, seed + 4))
    out.append(f'<path d="{well_d}" fill="{D.lin([(0, "#2A0A02", 0.45), (0.3, "#2A0A02", 0), (1, "#2A0A02", 0)])}"/>')
    # lattice strips in pie-plane coordinates (u, v in -1..1)
    cid = D.clip(f'<path d="{blob(cx, cy, rx * 0.95, ry * 0.93, seed + 5, 0.01, 30)}"/>')
    sw = 1.55 / strips

    def strip(u0, u1, v0, v1, k):
        pts = [(cx + u * rx, cy + v * ry) for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))]
        d = hg.org_poly(pts, seed + 30 + k, 0.5, 14, min(rx, ry) * 0.04)
        o = [f'<path d="{d}" fill="{crust[1]}"/>']
        horiz = (u1 - u0) > (v1 - v0)
        g = D.lin([(0, crust[0]), (0.5, mix(crust[0], crust[1], 0.5)), (1, crust[2])], 0, 0, 0 if horiz else 1, 1 if horiz else 0)
        o.append(f'<path d="{d}" fill="{g}" opacity="0.75"/>')
        o.append(strokes(D.nid(), d, bbox(pts), [crust[0], crust[2], "#FFF2C8"], seed + 60 + k, n=10, angle=0 if horiz else -90,
                         length=(8, 24), width=(0.8, 1.8), opacity=(0.2, 0.45)))
        o.append(ink(d, "#8A4A14", 1.2, seed + k, 1, 0.55))
        return "".join(o)

    pos = [-0.78 + i * (1.56 / (strips - 1)) for i in range(strips)]
    inner = []
    for i, u in enumerate(pos):              # strips running "down" the pie
        inner.append(strip(u - sw / 2, u + sw / 2, -1.1, 1.1, i))
    for j, v in enumerate(pos):              # strips running across, woven over/under
        inner.append(strip(-1.1, 1.1, v - sw / 2, v + sw / 2, 20 + j))
        for i, u in enumerate(pos):
            if (i + j) % 2 == 0:
                inner.append(strip(u - sw / 2, u + sw / 2, v - sw / 2 - 0.02, v + sw / 2 + 0.02, 40 + i * 7 + j))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # crimped rim: scallops around the edge
    n = 30
    for i in range(n):
        a = 2 * math.pi * i / n
        px, py = cx + rx * 0.93 * math.cos(a), cy + ry * 0.92 * math.sin(a)
        lit = -math.sin(a) * 0.6 - math.cos(a) * 0.4
        c = crust[0] if lit > 0.2 else (mix(crust[1], crust[2], 0.35) if lit < -0.3 else crust[1])
        out.append(f'<path d="{blob(px, py, rx * 0.11, ry * 0.12, seed + 100 + i, 0.1, 10, math.degrees(a))}" fill="{c}"/>')
        out.append(ink(f"M {cx + rx * 0.84 * math.cos(a + 0.05):.1f} {cy + ry * 0.83 * math.sin(a + 0.05):.1f} L {cx + rx * 1.0 * math.cos(a + 0.05):.1f} {cy + ry * 0.99 * math.sin(a + 0.05):.1f}",
                       "#9A5A1A", 1.2, seed + i, 1, 0.5))
    out.append(ink(smooth_closed(rim), "#7A4210", 1.6, seed + 9, 1, 0.55))
    if sugar:
        out.append(specks(seed + 11, (cx - rx * 0.8, cy - ry * 0.8, cx + rx * 0.8, cy + ry * 0.8), ["#FFFFFF", "#FFF6D8"], int(rx * 0.5), (0.6, 1.4), (0.5, 0.95)))
    return "".join(out)


def pie_slice(D, cx, cy, s, seed, filling="apple", plate=True, plate_col=WHITE, rim=None, fork=False):
    """A wedge of lattice pie on a small plate, point toward the viewer."""
    out = []
    if plate:
        out.append(cast(D, cx + s * 0.08, cy + s * 0.32, s * 1.05, s * 0.34, strength=0.4, seed=seed))
        out.append(painted(D, ell_pts(cx, cy + s * 0.18, s, s * 0.34, 0, 360, 36)[:-1], plate_col, seed, sdir=(0.3, 1), sk=0.08, angle=0, n=16, inkw=1.6, hi=0.4))
        out.append(f'<path d="{blob(cx, cy + s * 0.16, s * 0.72, s * 0.22, seed + 1, 0.02, 24)}" fill="{plate_col[2]}" opacity="0.28"/>')
        if rim:
            out.append(ink(smooth_closed(ell_pts(cx, cy + s * 0.18, s * 0.9, s * 0.29, 0, 360, 36)[:-1]), rim, 2.4, seed, 1, 0.85))
    # wedge: back arc crust, top face, two cut sides showing layers
    tip = (cx - s * 0.05, cy + s * 0.3)
    bl, br = (cx - s * 0.62, cy - s * 0.12), (cx + s * 0.56, cy - s * 0.18)
    h = s * 0.3
    side_l = [tip, bl, (bl[0], bl[1] - h), (tip[0], tip[1] - h)]
    side_r = [tip, br, (br[0], br[1] - h), (tip[0], tip[1] - h)]
    fill_pal = ("#F2C86A", "#D8963A", "#8A4A14") if filling == "apple" else ("#E83A4A", "#A8142A", "#5A0610")
    for sp, k, shadow_ in ((side_l, 0, 0.0), (side_r, 1, 0.25)):
        out.append(painted(D, pp(sp), fill_pal, seed + 3 + k, sdir=(0, 1), sk=0.1, angle=-20, n=12, inkw=1.4, hi=0.25))
        x0, y0, x1, y1 = bbox(sp)
        cid = D.clip(f'<path d="{smooth_closed(sp)}"/>')
        rnd = random.Random(seed + k)
        inner = []
        if filling == "apple":
            for _ in range(10):
                t = rnd.uniform(0.1, 0.9)
                px = sp[0][0] + (sp[1][0] - sp[0][0]) * t
                py = sp[0][1] + (sp[1][1] - sp[0][1]) * t - h * rnd.uniform(0.25, 0.75)
                inner.append(f'<path d="{blob(px, py, s * 0.07, s * 0.035, rnd.randint(0, 999), 0.12, 8, rnd.uniform(-20, 20))}" fill="#FFE8A0" opacity="0.9"/>')
        else:
            for _ in range(8):
                t = rnd.uniform(0.1, 0.9)
                px = sp[0][0] + (sp[1][0] - sp[0][0]) * t
                py = sp[0][1] + (sp[1][1] - sp[0][1]) * t - h * rnd.uniform(0.25, 0.75)
                inner.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{s * 0.045:.1f}" fill="#D8283A"/>')
        # bottom crust band
        inner.append(taper([sp[0], sp[1]], s * 0.08, s * 0.08, CRUST[1], 1))
        if shadow_:
            inner.append(f'<path d="{smooth_closed(sp)}" fill="#2A0A04" opacity="{shadow_}"/>')
        out.append(f'<g {cid}>{"".join(inner)}</g>')
    topf = [(tip[0], tip[1] - h), (bl[0], bl[1] - h), (cx - s * 0.3, cy - s * 0.3 - h), (cx + s * 0.2, cy - s * 0.34 - h), (br[0], br[1] - h)]
    out.append(painted(D, topf, CRUST, seed + 6, sdir=(0.3, 1), sk=0.08, angle=10, n=16, inkw=1.6, hi=0.3))
    cid = D.clip(f'<path d="{smooth_closed(topf)}"/>')
    lat = []
    for k in range(3):
        t = 0.3 + k * 0.25
        a = (tip[0] + (bl[0] - tip[0]) * t, tip[1] - h + (bl[1] - tip[1]) * t)
        b = (tip[0] + (br[0] - tip[0]) * (t + 0.1), tip[1] - h + (br[1] - tip[1]) * (t + 0.1))
        lat.append(taper([(a[0], a[1] - 2), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 6), (b[0], b[1] - 2)], s * 0.035, s * 0.035, "#7A3A10", 0.55))
    lat.append(f'<path d="{blob(cx - s * 0.12, cy - s * 0.12 - h, s * 0.18, s * 0.05, seed, 0.2, 10, -10)}" fill="#FFF2C8" opacity="0.5"/>')
    out.append(f'<g {cid}>{"".join(lat)}</g>')
    # crimped back edge
    for i in range(7):
        t = i / 6
        px = bl[0] + (br[0] - bl[0]) * t
        py = bl[1] - h + (br[1] - bl[1]) * t - s * 0.16 * math.sin(math.pi * t)
        out.append(f'<path d="{blob(px, py, s * 0.1, s * 0.07, seed + 20 + i, 0.1, 10)}" fill="{CRUST[0] if i % 2 else CRUST[1]}"/>')
        out.append(ink(blob(px, py, s * 0.1, s * 0.07, seed + 20 + i, 0.1, 10), "#9A5A1A", 1.1, seed + i, 1, 0.5))
    if fork:
        fx, fy = cx + s * 0.75, cy + s * 0.12
        out.append(taper([(fx - s * 0.05, fy + s * 0.1), (fx + s * 0.18, fy - s * 0.12)], s * 0.05, s * 0.04, "#C8D0DA"))
        for k in range(4):
            out.append(taper([(fx - s * 0.22 + k * s * 0.03, fy + s * 0.24 - k * s * 0.01), (fx - s * 0.06 + k * s * 0.02, fy + s * 0.11)], s * 0.018, s * 0.022, "#B8C0CA"))
    return "".join(out)


# ================================================================ 1. pie & coffee — the chrome diner at night, neon EAT sign
def rrect_pts(x0, y0, x1, y1, r, n=6):
    """Rounded rectangle as a dense point list (straight edges stay straight under pd())."""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def diner_interior(D, x0, y0, x1, y1, seed):
    """What you see through the diner windows: warm back wall, pie case, pendant lamps, folks at the counter."""
    rnd = random.Random(seed)
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{D.lin([(0, "#FFE6A0"), (0.55, "#FFC86A"), (1, "#E88A3A")])}"/>']
    # back-bar shelf with cups, a coffee urn, the pie case
    out.append(f'<rect x="{x0}" y="{y0 + (y1 - y0) * 0.36:.1f}" width="{x1 - x0}" height="3" fill="#B86A2A" opacity="0.7"/>')
    for x in range(int(x0) + 8, int(x1) - 8, 14):
        if rnd.random() < 0.55:
            out.append(f'<path d="{hg.org_rect(x, y0 + (y1 - y0) * 0.36 - 7, 8, 7, x, 0.2, 4, 1)}" fill="#FFF8E8" opacity="0.85"/>')
    for k in range(4):
        lx = x0 + 30 + k * (x1 - x0 - 60) / 3
        out.append(f'<path d="M {lx:.1f} {y0} L {lx:.1f} {y0 + 7}" stroke="#6A3A1A" stroke-width="1.2"/>')
        out.append(f'<path d="M {lx - 6:.1f} {y0 + 12} Q {lx:.1f} {y0 + 3} {lx + 6:.1f} {y0 + 12} Z" fill="#2E8A80"/>')
        out.append(D.glow(lx, y0 + 14, 26, "#FFF6C8", 0.7))
    pcx = x0 + (x1 - x0) * 0.62
    out.append(f'<path d="M {pcx - 14:.1f} {y1 - 13} Q {pcx:.1f} {y1 - 34} {pcx + 14:.1f} {y1 - 13} Z" fill="#FFFFFF" opacity="0.55"/>')
    out.append(f'<path d="M {pcx - 9:.1f} {y1 - 14} L {pcx + 9:.1f} {y1 - 14} L {pcx + 6:.1f} {y1 - 20} L {pcx - 6:.1f} {y1 - 20} Z" fill="#C8782A"/>')
    # people at the counter (backs and profiles), a waitress with a coffee pot
    folk = [(0.08, "#5A2E3A", "#3A2018"), (0.2, "#2E4A6A", "#6A3A1A"), (0.33, "#7A3A2A", "#1A1010"), (0.47, "#3A5A3A", "#C8964E"),
            (0.75, "#6A2A4A", "#2A1A10"), (0.88, "#2A3A5A", "#9A6634")]
    for t, coat, hair in folk:
        px = x0 + (x1 - x0) * t + rnd.uniform(-4, 4)
        base = y1 - 10
        out.append(f'<path d="M {px - 12:.1f} {base:.1f} Q {px - 11:.1f} {base - 16:.1f} {px:.1f} {base - 17:.1f} Q {px + 11:.1f} {base - 16:.1f} {px + 12:.1f} {base:.1f} Z" fill="{coat}"/>')
        out.append(f'<circle cx="{px:.1f}" cy="{base - 22:.1f}" r="6.2" fill="{hair}"/>')
        if rnd.random() < 0.5:
            out.append(f'<path d="M {px - 9:.1f} {base - 24:.1f} L {px + 9:.1f} {base - 24:.1f} L {px + 6:.1f} {base - 30:.1f} L {px - 6:.1f} {base - 30:.1f} Z" fill="{dk(coat, 0.3)}"/>')
    wx = x0 + (x1 - x0) * 0.6
    out.append(f'<path d="M {wx - 9:.1f} {y1 - 14} L {wx - 7:.1f} {y0 + 28} L {wx + 7:.1f} {y0 + 28} L {wx + 9:.1f} {y1 - 14} Z" fill="#E8F0F0"/>')
    out.append(f'<circle cx="{wx:.1f}" cy="{y0 + 21}" r="6" fill="#E8B48E"/><path d="M {wx - 7:.1f} {y0 + 18} q 7 -9 14 0 Z" fill="#B8462A"/>')
    out.append(f'<path d="M {wx - 7:.1f} {y0 + 18} L {wx + 7:.1f} {y0 + 18}" stroke="#FFFFFF" stroke-width="2"/>')
    # the counter itself, red with a chrome lip
    out.append(f'<rect x="{x0}" y="{y1 - 10}" width="{x1 - x0}" height="10" fill="#C8382E"/><rect x="{x0}" y="{y1 - 11}" width="{x1 - x0}" height="2.4" fill="#F4F6FA"/>')
    return "".join(out)


@design("pie-and-coffee")
def pie_and_coffee():
    D = Doc2("us-pc")
    out = [sky(D, [(0, "#0E1234"), (0.5, "#232A62"), (0.8, "#4A3A72"), (1, "#7A4A6A")], 3, 470, ["#2A3274", "#0A0E2A", "#4A3A7A"], 70)]
    out.append(stars_field(5, 70, (0, 0, 600, 290), avoid=((170, 70, 560, 230),)))
    out.append(D.glow(510, 88, 70, "#FFF2C8", 0.35))
    out.append(f'<path d="M 522 66 A 26 26 0 1 0 530 114 A 21 21 0 1 1 522 66 Z" fill="#FFF4D0"/>')
    # distant low hills, a water tower and a few far lights
    out.append(hill(D, ridge([(-20, 296), (200, 284), (420, 292), (620, 280)], 7, 3), 470, ("#3A3462", "#2A2650", "#1A1838"), 7, inkw=0, sop=(0.06, 0.16)))
    tx = 520
    out.append(f'<path d="M {tx - 16} 286 L {tx - 10} 248 M {tx + 16} 286 L {tx + 10} 248 M {tx - 13} 270 L {tx + 13} 266" stroke="#1C1A38" stroke-width="2.4"/>')
    out.append(f'<path d="{hg.org_rect(tx - 18, 230, 36, 20, 8, 0.3, 8, 6)}" fill="#24223E"/><path d="M {tx - 20} 232 L {tx} 220 L {tx + 20} 232 Z" fill="#24223E"/>')
    rnd = random.Random(11)
    for _ in range(9):
        x = rnd.uniform(180, 600)
        out.append(f'<circle cx="{x:.1f}" cy="{rnd.uniform(288, 300):.1f}" r="1.4" fill="#FFD890"/>')
    # wet asphalt lot
    out.append(f'<rect y="452" width="600" height="148" fill="{D.lin([(0, "#2A2440"), (1, "#14121E")])}"/>')
    out.append(strokes(D.nid(), "M 0 452 L 600 452 L 600 600 L 0 600 Z", (-40, 452, 600, 600), ["#3A3458", "#0E0C16", "#4A3A5A"], 9, n=70, angle=0,
                       length=(40, 140), width=(2, 5), opacity=(0.15, 0.35)))
    x0, x1, top, bot = 172, 566, 300, 444
    # reflections in the puddles: soft colour pools broken by ripples
    out.append(f'<ellipse cx="{(x0 + x1) / 2}" cy="486" rx="230" ry="30" fill="{D.rad([(0, "#FFC060", 0.5), (1, "#FFC060", 0)])}"/>')
    out.append(f'<ellipse cx="112" cy="500" rx="40" ry="60" fill="{D.rad([(0, "#FF3A5A", 0.45), (1, "#FF3A5A", 0)])}"/>')
    for _ in range(46):
        x = rnd.uniform(40, 580)
        y = rnd.uniform(462, 560)
        col = "#FF6A80" if x < 160 else rnd.choice(["#FFD080", "#FFC060", "#F4F0E8"])
        L = rnd.uniform(10, 34)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {L:.1f} 0" stroke="{col}" stroke-width="{rnd.uniform(1.2, 2.6):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.25, 0.6):.2f}"/>')
    # parking stripes
    for k in range(5):
        a = 70 + k * 120
        out.append(f'<path d="M {a} 520 L {a - 40} 600" stroke="#E8E2D0" stroke-width="5" opacity="0.35"/>')
    # ---- the diner: a stainless railcar with rounded ends
    out.append(painted(D, rect_pts(x0 + 8, bot - 6, x1 - 8, bot + 10, 30, 12, 0.5), ("#7A5A5A", "#4A3238", "#241820"), 12, sdir=(0, 1), sk=0.1, angle=0, n=10, inkw=1.2, hi=0.2))
    for k in range(10):
        bx = x0 + 20 + k * (x1 - x0 - 40) / 9
        out.append(f'<path d="{hg.org_rect(bx - 3, bot + 2, 6, 6, k, 0.2, 4, 1)}" fill="#1A1218"/>')
    body = rrect_pts(x0, top, x1, bot, 30)
    bd = pd(body)
    out.append(fluted(D, bd, (x0, top, x1, bot), 13, top="#2A3468", mid="#C8D4E8", bot="#8A6A78", step=7, warm="#FFB060"))
    roofp = rrect_pts(x0 + 2, top - 4, x1 - 2, top + 22, 14)
    out.append(painted(D, roofp, ("#8A9AC8", "#3A4478", "#1A2048"), 14, sdir=(0, 1), sk=0.1, angle=0, n=16, inkw=1.4, hi=0.5))
    out.append(taper([(x0 + 40, top + 1), ((x0 + x1) / 2, top - 1), (x1 - 60, top + 1)], 2.4, 1, "#FFF6E0", 0.7))
    for y, hh in ((top + 24, 11), (bot - 34, 9)):
        out.append(painted(D, rect_pts(x0 + 3, y, x1 - 3, y + hh, 40, int(y), 0.3), CHERRY, int(y), sdir=(0, 1), sk=0.15, angle=0, n=18, inkw=1.2, hi=0.4))
    # windows: one continuous interior, chrome mullions over it
    wy0, wy1 = top + 44, top + 92
    ex0, ex1 = 330, 384
    for a, b in ((x0 + 18, ex0 - 8), (ex1 + 8, x1 - 18)):
        win = f"M {a} {wy0} L {b} {wy0} L {b} {wy1} L {a} {wy1} Z"
        cid = D.clip(f'<path d="{win}"/>')
        out.append(f'<g {cid}>{diner_interior(D, a, wy0, b, wy1, 20 + a)}</g>')
        n = max(2, round((b - a) / 40))
        for k in range(n + 1):
            mx = a + k * (b - a) / n
            out.append(f'<rect x="{mx - 2.5:.1f}" y="{wy0}" width="5" height="{wy1 - wy0}" fill="{D.lin([(0, "#FFFFFF"), (0.5, "#C8D0DA"), (1, "#5E6878")], 0, 0, 1, 0)}"/>')
        out.append(f'<rect x="{a}" y="{wy0 + 13}" width="{b - a}" height="3" fill="#C8D0DA" opacity="0.9"/>')
        out.append(ink(win, "#1A1A2A", 2, 30 + a, 1, 0.8))
        out.append(taper([(a + 6, wy0 + 30), (a + 22, wy0 + 18)], 3, 1, "#FFFFFF", 0.5))
    out.append(D.glow((x0 + x1) / 2, (wy0 + wy1) / 2, 260, "#FFC060", 0.2, ry=70))
    out.append(painted(D, rect_pts(x0 + 90, top + 2, x1 - 90, top + 21, 30, 15, 0.3), CREAM, 15, sdir=(0, 1), sk=0.1, angle=0, n=10, inkw=1.4, hi=0.3))
    out.append(label((x0 + x1) / 2 + 2, top + 18, "D  I  N  E  R", BEBAS, 20, "#B8352A"))
    # entry vestibule with a lit door
    out.append(painted(D, rect_pts(ex0 - 6, top + 32, ex1 + 6, bot + 2, 16, 16, 0.4), ("#F4E8D8", "#C8B8B0", "#6A5A62"), 16, sdir=(1, 0.2), sk=0.15, angle=-90, n=12, inkw=1.6, hi=0.4))
    out.append(painted(D, pp([(ex0 - 14, top + 32), (ex1 + 14, top + 32), (ex1 + 10, top + 23), (ex0 - 10, top + 23)]), CHERRY, 17, sk=0.15, n=6, inkw=1.4, hi=0.4))
    g = D.lin([(0, "#FFF6D0"), (1, "#F0A040")])
    out.append(f'<path d="{hg.org_rect(ex0 + 6, top + 44, ex1 - ex0 - 12, bot - top - 48, 18, 0.3, 8, 3)}" fill="{g}"/>')
    out.append(ink(hg.org_rect(ex0 + 6, top + 44, ex1 - ex0 - 12, bot - top - 48, 18, 0.3, 8, 3), "#3A2A30", 2, 19, 1, 0.85))
    out.append(f'<path d="M {(ex0 + ex1) / 2} {top + 48} L {(ex0 + ex1) / 2} {bot - 4}" stroke="#3A2A30" stroke-width="1.6"/>')
    out.append(f'<circle cx="{(ex0 + ex1) / 2 + 6}" cy="{(top + bot) / 2 + 20}" r="2" fill="#C8D0DA"/>')
    out.append(D.glow((ex0 + ex1) / 2, bot, 70, "#FFD080", 0.45))
    for k in range(2):
        out.append(painted(D, rect_pts(ex0 - 4 - k * 6, bot + 2 + k * 8, ex1 + 4 + k * 6, bot + 10 + k * 8, 12, 40 + k, 0.3), ("#8A8090", "#5A5060", "#2A2430"), 40 + k, sdir=(0, 1), sk=0.15, angle=0, n=4, inkw=1, hi=0.3))
    out.append(ink(bd, "#1A1A2A", 2.2, 21, 2, 0.75))
    # ---- the pole sign: neon EAT, and a neon pie slice
    px = 110
    out.append(taper([(px, 476), (px, 300)], 9, 8, "#2A2234"))
    out.append(taper([(px - 2, 476), (px - 2, 300)], 2, 2, "#6A6080", 0.8))
    sx0, sx1, sy0, sy1 = 68, 152, 100, 296
    out.append(D.glow(px, 200, 150, "#FF3A5A", 0.35))
    sign = [(sx0, sy0 + 14), (sx0 + 14, sy0), (sx1 - 14, sy0), (sx1, sy0 + 14), (sx1, sy1 - 14), (sx1 - 14, sy1), (sx0 + 14, sy1), (sx0, sy1 - 14)]
    out.append(painted(D, sign, ("#4A3A6A", "#2A2244", "#140E24"), 22, sdir=(1, 0.3), sk=0.12, angle=-90, n=16, inkw=2, hi=0.3))
    out.append(neon_path(D, smooth_closed([(sx0 + 6, sy0 + 16), (sx0 + 16, sy0 + 6), (sx1 - 16, sy0 + 6), (sx1 - 6, sy0 + 16), (sx1 - 6, sy1 - 16), (sx1 - 16, sy1 - 6), (sx0 + 16, sy1 - 6), (sx0 + 6, sy1 - 16)]),
                         "#3AE0D0", 1.6))
    for k, ch in enumerate("EAT"):
        out.append(neon(D, px, sy0 + 62 + k * 62, ch, ANTON, 60, "#FF3A5A", 24 + k, glow=False))
    py0 = 310
    out.append(f'<path d="{hg.org_rect(px - 34, py0, 68, 46, 25, 0.3, 8, 6)}" fill="#1E1830" stroke="#140E24" stroke-width="2"/>')
    out.append(neon_path(D, f"M {px - 22} {py0 + 34} L {px + 22} {py0 + 34} L {px + 10} {py0 + 12} Q {px - 10} {py0 + 6} {px - 22} {py0 + 34} Z", "#FFC23A", 2.2,
                         glow=(px, py0 + 22, 46)))
    out.append(neon_path(D, f"M {px - 8} {py0 + 26} q 4 -5 9 0 M {px + 2} {py0 + 20} q 3 -3 6 0", "#FFC23A", 1.5))
    out.append(f'<path d="M {px - 24} {py0} L {px - 24} {py0 - 14} M {px + 24} {py0} L {px + 24} {py0 - 14}" stroke="#2A2234" stroke-width="2"/>')
    # ---- a two-tone sedan parked out front, in the foreground
    out.append(car50(D, 398, 556, 250, 31, body=AQUA, roof=CREAM, flip=-1))
    for _ in range(14):
        x = rnd.uniform(290, 510)
        out.append(f'<path d="M {x:.1f} {rnd.uniform(566, 590):.1f} l {rnd.uniform(8, 22):.1f} 0" stroke="#7AD0C8" stroke-width="2" stroke-linecap="round" opacity="0.35"/>')
    # lettering
    out.append(letters(D, 362, 150, "Pie & Coffee", SERIF_IT, 76, "#FFF2D8", ["#FFFFFF", "#F2DCB4", "#FFE8C0"], 33, max_w=356,
                       shadow="#0A0C24", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(362, 204, "OPEN ALL NIGHT", "#FFC23A", font=JOS, size=22, ls=6, line_w=26, gap=12, max_w=300))
    return finish_a(D, out, 34)


def curtain(D, rod_y, x_out, x_in, tie, bot_y, bot_out, bot_in, col, seed, cell=12):
    """A gingham café curtain gathered on a rod and tied back: straight top, sweeping inner edge,
    vertical folds, a little ruffle along the rod and a fabric tie."""
    side = 1 if x_in > x_out else -1
    tx, ty = tie
    d = (f"M {x_out:.1f} {rod_y:.1f} L {x_in:.1f} {rod_y:.1f} C {x_in:.1f} {rod_y + 70:.1f} {tx + side * 26:.1f} {ty - 70:.1f} {tx:.1f} {ty:.1f} "
         f"C {tx + side * 4:.1f} {ty + 30:.1f} {bot_in - side * 6:.1f} {bot_y - 50:.1f} {bot_in:.1f} {bot_y:.1f} L {bot_out:.1f} {bot_y:.1f} "
         f"C {bot_out - side * 4:.1f} {bot_y - 60:.1f} {x_out - side * 2:.1f} {ty:.1f} {x_out:.1f} {rod_y:.1f} Z")
    out = [gingham(D, d, col, "#FFFDF6", cell, 0)]
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    n = 5
    for k in range(n):
        f = (k + 0.5) / n
        a = (x_out + (x_in - x_out) * f, rod_y)
        b = (x_out + (tx - x_out) * (0.35 + 0.65 * f), ty)
        c = (bot_out + (bot_in - bot_out) * f, bot_y)
        inner.append(taper([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), b, c], 9, 12, "#3A0A06", 0.16))
        inner.append(taper([(a[0] + 5, a[1]), ((a[0] + b[0]) / 2 + 5, (a[1] + b[1]) / 2), (b[0] + 3, b[1]), (c[0] + 5, c[1])], 4, 5, "#FFFFFF", 0.3))
    inner.append(f'<rect x="{min(x_out, bot_out) - 20:.1f}" y="{rod_y:.1f}" width="{abs(x_in - x_out) + 60:.1f}" height="{bot_y - rod_y:.1f}" fill="{D.lin([(0, "#2A0A04", 0.0), (1, "#2A0A04", 0.22)], 0 if side > 0 else 1, 0, 1 if side > 0 else 0, 0)}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, INK, 1.8, seed, 2, 0.7))
    # ruffle on the rod
    w = abs(x_in - x_out)
    for k in range(int(w / 12) + 1):
        x = min(x_out, x_in) + k * 12
        out.append(f'<path d="{blob(x + 6, rod_y + 2, 7, 6, seed + k, 0.15, 8)}" fill="{col if k % 2 else "#FFFDF6"}" stroke="{INK}" stroke-width="1" opacity="0.95"/>')
    # fabric tie
    out.append(taper([(tx - side * 30, ty - 6), (tx - side * 10, ty + 2), (tx + side * 8, ty - 2)], 9, 8, "#2E5AA8"))
    out.append(f'<path d="{blob(tx + side * 6, ty, 7, 6, seed + 50, 0.1, 8)}" fill="#2E5AA8" stroke="{INK}" stroke-width="1"/>')
    return "".join(out)


# ================================================================ 2. american as apple pie — cooling on the windowsill
@design("american-as-apple-pie")
def american_as_apple_pie():
    D = Doc2("us-ap")
    # wallpaper: butter-yellow with a tiny sprig print
    out = [paper(D.nid(), "#F8EBC4", FLECK, 41)]
    rnd = random.Random(42)
    for yy in range(0, 640, 40):
        for xx in range(0, 640, 40):
            x, y = xx + (20 if (yy // 40) % 2 else 0) + rnd.uniform(-2, 2), yy + rnd.uniform(-2, 2)
            out.append(f'<path d="M {x:.1f} {y + 5:.1f} q 1 -6 0 -10" stroke="#8AA070" stroke-width="1.3" fill="none" opacity="0.55"/>'
                       f'<circle cx="{x:.1f}" cy="{y - 6:.1f}" r="2.2" fill="#D86A5A" opacity="0.6"/>')
    out.append(blooms(43, ["#E8C890", "#F2D8A0"], 6, (0, 0, 600, 600), (90, 170), (0.06, 0.12)))
    # window opening: summer garden outside
    wx0, wx1, wy0, wy1 = 128, 472, 214, 430
    win = f"M {wx0} {wy0} L {wx1} {wy0} L {wx1} {wy1} L {wx0} {wy1} Z"
    cid = D.clip(f'<path d="{win}"/>')
    g = []
    g.append(sky(D, [(0, "#7AB8E8"), (0.7, "#BFE0F2"), (1, "#E8F4F0")], 44, 430, ["#9ACAEE", "#E8F6FF"], 30, y0=190))
    g.append(puff_cloud(D, 230, 250, 120, 45, pal=("#FFFFFF", "#F4F8FC", "#C8D8E8")))
    g.append(puff_cloud(D, 420, 232, 80, 46, pal=("#FFFFFF", "#F4F8FC", "#C8D8E8")))
    # far rolling hills and a red barn
    g.append(hill(D, ridge([(100, 330), (260, 316), (380, 326), (500, 312)], 47, 3), 440, ("#C8DCA0", "#9AB878", "#6A8A54"), 47, inkw=0))
    bxx = 372
    g.append(painted(D, rect_pts(bxx, 300, bxx + 34, 326, 10, 48, 0.4), BARN, 48, sk=0.1, n=4, inkw=1, hi=0.3))
    g.append(painted(D, pp([(bxx - 4, 302), (bxx + 17, 286), (bxx + 38, 302)]), ("#8A8A9A", "#5A5A6A", "#2A2A3A"), 49, sk=0.1, n=3, inkw=1, hi=0.3))
    g.append(f'<path d="M {bxx + 12} 326 L {bxx + 12} 312 L {bxx + 22} 312 L {bxx + 22} 326" fill="none" stroke="#FFFFFF" stroke-width="1.4"/>')
    g.append(hill(D, ridge([(100, 360), (300, 350), (500, 362)], 50, 3), 440, GRASS, 50, inkw=0))
    # apple tree, branch reaching into the view
    g.append(taper([(200, 440), (196, 380), (186, 340)], 18, 10, "#6A4A2E"))
    g.append(dab_crown(D, 186, 296, 92, 70, [GRASS, SAGE, ("#A8D070", "#5A8A30", "#2A4A1A")], 51, n=140, size=(7, 13), inkw=1.2))
    for k in range(9):
        a = rnd.uniform(0, 6.28)
        r_ = rnd.uniform(0, 0.8)
        ax, ay = 186 + math.cos(a) * 80 * r_, 296 + math.sin(a) * 58 * r_
        g.append(f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="5.5" fill="#D8302A"/><circle cx="{ax - 1.6:.1f}" cy="{ay - 1.6:.1f}" r="1.8" fill="#FFB8A8"/>')
    # picket fence and a robin on it
    g.append(picket_fence(D, 112, 480, 362, 420, 52, w=13, gap=8))
    g.append(grass(53, (110, 404, 480, 432), ["#5A8A30", "#8AB850", "#2E5A1E"], 120, (6, 16)))
    rx_, ry_ = 410, 356
    g.append(painted(D, blob_pts(rx_, ry_, 12, 9, 54, 0.05, 12), ("#9A8A7A", "#6A5A4E", "#3A2E26"), 54, sk=0.2, n=4, inkw=1.2, hi=0.3))
    g.append(f'<path d="{blob(rx_ + 4, ry_ + 3, 7, 6, 55, 0.08, 10)}" fill="#E8603A"/>')
    g.append(f'<circle cx="{rx_ + 12}" cy="{ry_ - 7}" r="6" fill="#4A3A30"/><circle cx="{rx_ + 14}" cy="{ry_ - 8}" r="1.3" fill="#FFFFFF"/>'
             f'<path d="M {rx_ + 17} {ry_ - 7} l 5 1 l -5 1 Z" fill="#E8A83A"/><path d="M {rx_ - 10} {ry_ - 2} l -10 -3 l 2 6 Z" fill="#4A3A30"/>')
    out.append(f'<g {cid}>{"".join(g)}</g>')
    # window frame (painted wood, cream) with a mullion cross on the upper sash
    fr = CREAM
    for pts in ([(wx0 - 20, wy0 - 22), (wx1 + 20, wy0 - 22), (wx1 + 20, wy0), (wx0 - 20, wy0)],
                [(wx0 - 20, wy0 - 22), (wx0, wy0 - 22), (wx0, wy1), (wx0 - 20, wy1)],
                [(wx1, wy0 - 22), (wx1 + 20, wy0 - 22), (wx1 + 20, wy1), (wx1, wy1)]):
        out.append(painted(D, pts, fr, 60 + int(pts[0][0]), sdir=(0.3, 1), sk=0.12, angle=-90, n=10, inkw=1.8, hi=0.35))
    # upper sash (window raised): rail + muntin
    out.append(painted(D, rect_pts(wx0, 286, wx1, 298, 30, 61, 0.3), fr, 61, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.6, hi=0.3))
    out.append(painted(D, rect_pts(298, wy0, 304, 286, 20, 62, 0.3), fr, 62, sdir=(1, 0), sk=0.2, angle=-90, n=6, inkw=1.4, hi=0.3))
    out.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{286 - wy0}" fill="#FFFFFF" opacity="0.12"/>')
    out.append(taper([(wx0 + 20, 270), (wx0 + 70, 214)], 6, 2, "#FFFFFF", 0.35))
    out.append(taper([(wx1 - 90, 270), (wx1 - 40, 220)], 4, 1, "#FFFFFF", 0.3))
    # gingham café curtains on a rod, tied back
    out.append(taper([(wx0 - 52, wy0 - 26), (wx1 + 52, wy0 - 26)], 5, 5, "#8A5A30"))
    for ex_ in (wx0 - 56, wx1 + 56):
        out.append(f'<circle cx="{ex_}" cy="{wy0 - 26}" r="6" fill="#8A5A30"/>')
    out.append(curtain(D, wy0 - 24, wx0 - 44, wx0 + 44, (wx0 - 2, 346), 448, wx0 - 48, wx0 + 16, "#D8382E", 63))
    out.append(curtain(D, wy0 - 24, wx1 + 44, wx1 - 44, (wx1 + 2, 346), 448, wx1 + 48, wx1 - 16, "#D8382E", 64))
    # the sill and the pie, cooling on a folded towel
    out.append(painted(D, rect_pts(wx0 - 44, 426, wx1 + 44, 452, 30, 64, 0.4), fr, 64, sdir=(0, 1), sk=0.15, angle=0, n=20, inkw=2, hi=0.4))
    out.append(f'<rect x="{wx0 - 40}" y="452" width="{wx1 - wx0 + 80}" height="10" fill="#6A4A2A" opacity="0.25"/>')
    towel = [(170, 420), (440, 414), (452, 446), (430, 470), (176, 474), (160, 448)]
    out.append(cloth(D, towel, "#2E5AA8", 65, base="#FFFDF6", cell=10, rot_=6, light=(0, 0, 0.3, 1)))
    out.append(lattice_pie(D, 304, 404, 116, 40, 66, "apple", depth=26))
    out.append(steam(304, 350, 64, 67, "#FFFFFF", 2, 44, 6, 0.65))
    # beadboard wainscot below
    out.append(f'<rect y="462" width="600" height="138" fill="#E8DCC4"/>')
    for x in range(0, 600, 24):
        out.append(f'<path d="M {x} 462 L {x} 600" stroke="#B8A888" stroke-width="2" opacity="0.6"/><path d="M {x + 2} 462 L {x + 2} 600" stroke="#FFFFFF" stroke-width="1" opacity="0.5"/>')
    out.append(f'<rect y="462" width="600" height="20" fill="#2A1A0A" opacity="0.12"/>')
    # lettering
    out.append(ruled(300, 82, "AS AMERICAN AS", "#2E5AA8", font=JOS, size=24, ls=7, line_w=40, gap=14))
    out.append(letters(D, 300, 150, "apple pie", SERIF_IT, 92, "#B8352A", ["#D8503A", "#8A1E12", "#E8704A"], 68, max_w=420,
                       shadow="#FFF6E0", soff=(0.02, 0.03), angle=-40, hi="#FFC8A8"))
    out.append(label(300, 538, "FRESH FROM THE OVEN", MONO, 19, "#7A4A2A", ls=4))
    return finish_a(D, out, 69)


# ================================================================ 3. root beer float — soda fountain counter
def soda_glass(D, cx, base, h, seed, drink=("#9A4A1E", "#5A1E08", "#2A0A02"), fill=0.78):
    """Tall fluted soda-fountain glass on a short foot; dark root beer with a creamy head."""
    out = [cast(D, cx + 10, base + 2, h * 0.32, h * 0.04, strength=0.5, seed=seed)]
    w_top, w_bot = h * 0.27, h * 0.11
    stem_h = h * 0.12
    bowl_bot = base - stem_h
    # foot and stem
    foot = ell_pts(cx, base - 3, h * 0.17, h * 0.035, 0, 360, 20)[:-1]
    out.append(painted(D, foot, ("#FFFFFF", "#D8E4EC", "#8AA0B0"), seed, sdir=(0.3, 1), sk=0.1, angle=0, n=6, inkw=1.4, hi=0.5))
    out.append(painted(D, pp([(cx - 5, base - 4), (cx - 4, bowl_bot), (cx + 4, bowl_bot), (cx + 5, base - 4)]), ("#FFFFFF", "#D8E4EC", "#8AA0B0"), seed + 1, sk=0.1, n=3, inkw=1.2, hi=0.5))
    top = base - h
    bowl = [(cx - w_top, top), (cx - w_top * 0.96, top + h * 0.2), (cx - w_bot * 1.4, top + h * 0.62), (cx - w_bot, bowl_bot - 6), (cx - w_bot * 0.6, bowl_bot),
            (cx + w_bot * 0.6, bowl_bot), (cx + w_bot, bowl_bot - 6), (cx + w_bot * 1.4, top + h * 0.62), (cx + w_top * 0.96, top + h * 0.2), (cx + w_top, top)]
    bd = smooth_closed(bowl)
    out.append(f'<path d="{bd}" fill="#E8F2F6" opacity="0.5"/>')
    cid = D.clip(f'<path d="{bd}"/>')
    lvl = top + h * (1 - fill) * 0.9
    inner = [f'<rect x="{cx - w_top - 4:.1f}" y="{lvl:.1f}" width="{2 * w_top + 8:.1f}" height="{bowl_bot - lvl + 4:.1f}" fill="{D.lin([(0, drink[0]), (0.5, drink[1]), (1, drink[2])], 0, 0, 1, 0)}"/>']
    rnd = random.Random(seed)
    for _ in range(26):
        bx, by = rnd.uniform(cx - w_top * 0.8, cx + w_top * 0.8), rnd.uniform(lvl + 20, bowl_bot - 8)
        inner.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{rnd.uniform(0.8, 2.2):.1f}" fill="#FFD8A8" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    # cream swirling down from the ice cream
    inner.append(taper([(cx - w_top * 0.3, lvl + 4), (cx - w_top * 0.1, lvl + 40), (cx + w_top * 0.2, lvl + 80), (cx, lvl + 120)], 16, 4, "#E8C8A0", 0.45))
    # flutes in the glass
    for k in range(-3, 4):
        fx = cx + k * w_top * 0.26
        inner.append(f'<path d="M {fx:.1f} {top:.1f} Q {fx * 0.6 + cx * 0.4:.1f} {top + h * 0.5:.1f} {cx + (fx - cx) * 0.3:.1f} {bowl_bot:.1f}" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.25"/>')
    inner.append(shade_over(D, bd, "#0A0402", 0.4, 0, 0, 1, 0, 0.55))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(taper([(cx - w_top * 0.82, top + 10), (cx - w_top * 0.7, top + h * 0.4), (cx - w_bot * 1.1, top + h * 0.7)], 6, 2, "#FFFFFF", 0.75))
    out.append(taper([(cx + w_top * 0.7, top + 30), (cx + w_top * 0.55, top + h * 0.42)], 3, 1, "#FFFFFF", 0.5))
    # condensation beads
    for _ in range(30):
        t = rnd.uniform(0.15, 0.85)
        yy = top + 20 + rnd.uniform(0, h * 0.6)
        half = w_top if yy < top + h * 0.2 else w_top - (w_top - w_bot * 1.4) * (yy - top - h * 0.2) / (h * 0.42)
        xx = cx + (t * 2 - 1) * half * 0.9
        r = rnd.uniform(1, 2.4)
        out.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="{r:.1f}" fill="#FFFFFF" opacity="0.55"/><circle cx="{xx + r * 0.3:.1f}" cy="{yy + r * 0.3:.1f}" r="{r * 0.5:.1f}" fill="#3A1A0A" opacity="0.25"/>')
    out.append(ink(bd, "#5A6A78", 1.8, seed + 2, 2, 0.7))
    out.append(ink(smooth_closed(ell_pts(cx, top, w_top, w_top * 0.18, 0, 360, 24)[:-1]), "#8AA0B0", 1.4, seed + 3, 1, 0.7))
    return "".join(out), top, w_top


def scoop_vanilla(D, cx, cy, r, seed, drip=True):
    pts = []
    rnd = random.Random(seed)
    for i in range(30):
        a = 2 * math.pi * i / 30
        rr = r * (1 + (0.08 * math.sin(a * 7 + seed) if math.sin(a) > 0.2 else 0.03 * rnd.uniform(-1, 1)))
        pts.append((cx + rr * math.cos(a), cy + rr * 0.86 * math.sin(a)))
    out = [painted(D, pts, ("#FFFFFF", "#FBF1DC", "#D8C098"), seed, sdir=(0.5, 0.8), sk=0.18, angle=-30, n=int(r * 0.9), inkw=1.6, hi=0.5, hik=0.1, curve=0.4)]
    out.append(specks(seed + 1, (cx - r * 0.7, cy - r * 0.6, cx + r * 0.7, cy + r * 0.5), ["#3A2010", "#5A3A1A"], int(r * 0.6), (0.6, 1.2), (0.5, 0.9)))
    if drip:
        for k in range(3):
            dx = cx + rnd.uniform(-r * 0.7, r * 0.7)
            L = rnd.uniform(r * 0.3, r * 0.7)
            out.append(taper([(dx, cy + r * 0.6), (dx + 1, cy + r * 0.6 + L * 0.6), (dx, cy + r * 0.6 + L)], 7, 6, "#FBF1DC", 1))
            out.append(f'<circle cx="{dx - 1:.1f}" cy="{cy + r * 0.6 + L * 0.5:.1f}" r="1.4" fill="#FFFFFF"/>')
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.35, r * 0.3, r * 0.15, seed + 2, 0.2, 10, -30)}" fill="#FFFFFF" opacity="0.9"/>')
    return "".join(out)


def straw(D, x0, y0, x1, y1, w, seed, cols=("#D8302A", "#FFFFFF")):
    a = math.atan2(y1 - y0, x1 - x0)
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -math.sin(a), math.cos(a)
    pts = [(x0 + nx * w / 2, y0 + ny * w / 2), (x1 + nx * w / 2, y1 + ny * w / 2), (x1 - nx * w / 2, y1 - ny * w / 2), (x0 - nx * w / 2, y0 - ny * w / 2)]
    d = pd(pts)
    out = [f'<path d="{d}" fill="{cols[1]}"/>']
    cid = D.clip(f'<path d="{d}"/>')
    st = []
    k = 0
    while k * w * 0.9 < L + w * 2:
        t = k * w * 0.9
        px, py = x0 + math.cos(a) * t, y0 + math.sin(a) * t
        st.append(taper([(px + nx * w - math.cos(a) * w * 0.6, py + ny * w - math.sin(a) * w * 0.6), (px - nx * w + math.cos(a) * w * 0.6, py - ny * w + math.sin(a) * w * 0.6)], w * 0.42, w * 0.42, cols[0]))
        k += 1
    st.append(f'<path d="M {x0 + nx * w * 0.25:.1f} {y0 + ny * w * 0.25:.1f} L {x1 + nx * w * 0.25:.1f} {y1 + ny * w * 0.25:.1f}" stroke="#FFFFFF" stroke-width="{w * 0.18:.1f}" opacity="0.6"/>')
    st.append(f'<path d="M {x0 - nx * w * 0.35:.1f} {y0 - ny * w * 0.35:.1f} L {x1 - nx * w * 0.35:.1f} {y1 - ny * w * 0.35:.1f}" stroke="#3A0A0A" stroke-width="{w * 0.2:.1f}" opacity="0.25"/>')
    out.append(f'<g {cid}>{"".join(st)}</g>')
    out.append(ink(d, INK, 1.2, seed, 1, 0.6))
    out.append(f'<path d="{smooth_closed(ell_pts(x1, y1, w * 0.5, w * 0.22, 0, 360, 10)[:-1])}" fill="#E8D8D0" transform="rotate({math.degrees(a) + 90:.1f} {x1:.1f} {y1:.1f})"/>')
    return "".join(out)


def cherry(D, cx, cy, r, seed, stem_ang=-60):
    out = []
    sx, sy = cx + r * 0.1, cy - r * 0.8
    out.append(pline([(sx, sy), (sx + math.cos(math.radians(stem_ang)) * r * 1.2, sy + math.sin(math.radians(stem_ang)) * r * 1.6),
                      (sx + math.cos(math.radians(stem_ang)) * r * 1.6, sy + math.sin(math.radians(stem_ang)) * r * 2.6)], "#5A6A2A", max(2, r * 0.16), seed, 1, 1))
    out.append(painted(D, blob_pts(cx, cy, r, r * 0.92, seed, 0.04, 14), CHERRY, seed, sdir=(0.6, 0.7), sk=0.2, angle=-40, n=6, inkw=1.4, hi=0.3))
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.35, r * 0.3, r * 0.18, seed + 1, 0.1, 8, -40)}" fill="#FFFFFF" opacity="0.9"/>')
    return "".join(out)


@design("root-beer-float")
def root_beer_float():
    D = Doc2("us-rb")
    # aqua soda-fountain wall with pink pinstripes
    out = [paper(D.nid(), "#9ED8D0", "#2A6A64", 71)]
    for x in range(-10, 620, 44):
        out.append(f'<path d="M {x} 0 L {x} 430" stroke="#F8C8C8" stroke-width="7" opacity="0.5"/><path d="M {x + 12} 0 L {x + 12} 430" stroke="#FFFFFF" stroke-width="2" opacity="0.45"/>')
    out.append(blooms(72, ["#7EC8C0", "#C8F0E8", "#5AB0A8"], 7, (0, 0, 600, 430), (90, 170), (0.08, 0.14)))
    out.append(soft_glow(D, 300, 300, 260, "#FFF6E0", 0.5))
    # chrome-edged counter with a pink formica top
    out.append(f'<path d="M 0 430 L 600 430 L 600 470 L 0 470 Z" fill="{D.lin([(0, "#F8C8C8"), (1, "#E8A0A8")])}"/>')
    out.append(specks(73, (0, 432, 600, 468), ["#FFFFFF", "#D88090", "#C8A0A8"], 120, (0.8, 1.8), (0.4, 0.8)))
    out.append(fluted(D, "M 0 466 L 600 466 L 600 600 L 0 600 Z", (0, 466, 600, 600), 74, top="#FFFFFF", mid="#C8D0DA", bot="#6A7280", step=8))
    out.append(f'<rect y="466" width="600" height="6" fill="#FFFFFF" opacity="0.9"/>')
    out.append(f'<rect y="472" width="600" height="8" fill="#2A3040" opacity="0.18"/>')
    for x in range(0, 620, 120):
        out.append(f'<path d="M {x} 482 L {x} 600" stroke="#D8302A" stroke-width="10" opacity="0.85"/>')
    # the float, set to the right; the words stack on the left
    gx = 392
    g, top, wt = soda_glass(D, gx, 452, 266, 75)
    out.append(g)
    out.append(straw(D, gx + 6, top + 70, gx + 50, top - 120, 12, 76))
    out.append(straw(D, gx - 8, top + 72, gx - 36, top - 104, 12, 77, cols=("#2E5AA8", "#FFFFFF")))
    foam = [(gx - wt - 6, top + 4), (gx - wt + 10, top - 12), (gx, top - 16), (gx + wt - 10, top - 12), (gx + wt + 6, top + 4), (gx + wt - 6, top + 14), (gx - wt + 6, top + 14)]
    out.append(painted(D, foam, ("#FFF8EC", "#F0DEC0", "#B89A70"), 78, sdir=(0.3, 1), sk=0.2, angle=0, n=20, inkw=1.6, hi=0.5))
    out.append(specks(79, (gx - wt, top - 10, gx + wt, top + 10), ["#C8A878", "#FFFFFF"], 30, (1, 2.6), (0.4, 0.9)))
    for k, dx in enumerate((-wt + 6, wt - 10)):
        out.append(taper([(gx + dx, top + 6), (gx + dx + 2, top + 26), (gx + dx, top + 40)], 9, 6, "#F0DEC0", 1))
    out.append(scoop_vanilla(D, gx - 26, top - 30, 40, 80))
    out.append(scoop_vanilla(D, gx + 20, top - 52, 42, 81))
    out.append(cherry(D, gx + 28, top - 98, 14, 82))
    # a long spoon on the counter and a crumpled straw wrapper
    out.append(taper([(150, 450), (260, 440)], 4, 3, "#C8D0DA"))
    out.append(f'<path d="{blob(140, 452, 12, 6, 83, 0.05, 10, -6)}" fill="#D8DEE6" stroke="#6A7280" stroke-width="1"/>')
    out.append(pline([(500, 452), (518, 446), (532, 452), (548, 444), (560, 450)], "#FFFFFF", 5, 84, 1, 1))
    out.append(pline([(500, 452), (518, 446), (532, 452), (548, 444), (560, 450)], "#D8302A", 1.4, 85, 0.6, 1))
    # lettering, stacked on the left
    out.append(letters(D, 178, 172, "Root", SERIF_IT, 104, "#B8352A", ["#D8503A", "#8A1E12", "#E8704A"], 86, max_w=230,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-40, hi="#FFC8A8"))
    out.append(letters(D, 178, 270, "Beer", SERIF_IT, 104, "#B8352A", ["#D8503A", "#8A1E12", "#E8704A"], 87, max_w=230,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-40, hi="#FFC8A8"))
    out.append(f'<path d="{hg.org_rect(96, 296, 164, 50, 89, 0.4, 10, 6)}" fill="#243C70"/>')
    out.append(label(178, 334, "FLOAT", BEBAS, 44, "#FFFFFF", ls=12, max_w=150))
    out.append(label(300, 534, "TWO STRAWS, PLEASE", JOS, 22, "#2A3040", ls=6))
    return finish_a(D, out, 88)


# ================================================================ 4. take me out to the ball game — glove and ball on the bleachers
def baseball(D, cx, cy, r, seed, rot_=20):
    out = [painted(D, blob_pts(cx, cy, r, r, seed, 0.01, 24), ("#FFFFFF", "#F4EEE2", "#B8AA94"), seed, sdir=(0.6, 0.7), sk=0.2, angle=-40, n=int(r * 0.8), inkw=1.6, hi=0.5)]
    cid = D.clip(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>')
    seams = []
    for sg in (-1, 1):
        pts = []
        for i in range(19):
            t = -1 + i / 9
            a = math.radians(rot_)
            u = sg * (r * 0.62 + r * 0.32 * (1 - t * t))
            v = t * r * 1.05
            pts.append((cx + u * math.cos(a) - v * math.sin(a), cy + u * math.sin(a) + v * math.cos(a)))
        seams.append(pline(pts, "#C8B8A0", 1.6, seed + sg, 0.6, 1))
        for i in range(1, len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i - 1], pts[i + 1]
            ang = math.atan2(y1 - y0, x1 - x0)
            nx, ny = -math.sin(ang), math.cos(ang)
            x, y = pts[i]
            L = r * 0.09
            seams.append(f'<path d="M {x - nx * L + math.cos(ang) * L * 0.5:.1f} {y - ny * L + math.sin(ang) * L * 0.5:.1f} L {x:.1f} {y:.1f} L {x + nx * L + math.cos(ang) * L * 0.5:.1f} {y + ny * L + math.sin(ang) * L * 0.5:.1f}" '
                         f'stroke="#D8302A" stroke-width="{max(1.6, r * 0.05):.1f}" fill="none" stroke-linecap="round"/>')
    seams.append(shade_over(D, f"M {cx - r} {cy} a {r} {r} 0 1 0 {2 * r} 0 a {r} {r} 0 1 0 {-2 * r} 0", "#3A2A1A", 0.35, 0, 0, 1, 1, 0.45))
    out.append(f'<g {cid}>{"".join(seams)}</g>')
    out.append(f'<path d="{blob(cx - r * 0.38, cy - r * 0.4, r * 0.25, r * 0.14, seed + 3, 0.2, 10, -40)}" fill="#FFFFFF" opacity="0.9"/>')
    return "".join(out)


def mitt(D, cx, cy, s, seed, pal=LEATHER):
    """Fielder's glove, palm side up, fingers to the upper right: thumb, laced web, four fingers, pocket."""
    out = [cast(D, cx + s * 0.1, cy + s * 0.55, s * 0.75, s * 0.18, strength=0.5, seed=seed)]
    def P(u, v):
        a = math.radians(-18)
        return (cx + (u * math.cos(a) - v * math.sin(a)) * s, cy + (u * math.sin(a) + v * math.cos(a)) * s)
    # fingers (back to front)
    fingers = [(-0.02, 0.6), (0.17, 0.6), (0.35, 0.54), (0.52, 0.44)]
    for k, (u, L) in enumerate(fingers[::-1]):
        base_u = u
        pts = [P(base_u - 0.1, -0.05), P(base_u - 0.11, -0.05 - L * 0.6), P(base_u - 0.06, -0.05 - L), P(base_u + 0.02, -0.07 - L * 1.04), P(base_u + 0.08, -0.05 - L * 0.95),
               P(base_u + 0.1, -0.05 - L * 0.55), P(base_u + 0.09, -0.02)]
        out.append(painted(D, pts, pal, seed + k, sdir=(0.8, 0.4), sk=0.18, angle=-100, n=12, inkw=1.8, hi=0.4, curve=0.3))
        # rawhide lace binding the finger tips
        for j in range(4):
            t = j / 3
            a_ = P(base_u - 0.08 + 0.16 * t, -0.05 - L * (0.93 + 0.08 * math.sin(math.pi * t)))
            out.append(f'<path d="{blob(a_[0], a_[1], s * 0.022, s * 0.012, seed + j, 0.1, 6, 20)}" fill="#E8C08A" stroke="#6A3A14" stroke-width="0.8"/>')
        out.append(pline([P(base_u - 0.06, -0.08), P(base_u - 0.05, -0.05 - L * 0.7)], "#6A3412", 1.2, seed + k, 0.45, 1))
    # thumb
    th = [P(-0.36, 0.15), P(-0.5, -0.05), P(-0.52, -0.25), P(-0.44, -0.33), P(-0.36, -0.25), P(-0.3, -0.05), P(-0.18, 0.08)]
    out.append(painted(D, th, pal, seed + 10, sdir=(0.8, 0.4), sk=0.18, angle=-80, n=14, inkw=1.8, hi=0.4))
    # laced web between thumb and index
    web = [P(-0.38, -0.25), P(-0.3, -0.36), P(-0.14, -0.46), P(-0.1, -0.12), P(-0.3, -0.04)]
    wd = smooth_closed(web)
    out.append(f'<path d="{wd}" fill="{dk(pal[1], 0.15)}"/>')
    cid = D.clip(f'<path d="{wd}"/>')
    lace = []
    for k in range(6):
        a_, b_ = P(-0.42 + k * 0.06, -0.42), P(-0.42 + k * 0.06 + 0.06, 0.0)
        lace.append(taper([a_, b_], s * 0.03, s * 0.03, "#E8C08A"))
        lace.append(taper([P(-0.44, -0.38 + k * 0.07), P(-0.06, -0.38 + k * 0.07 - 0.08)], s * 0.026, s * 0.026, "#D8AA70"))
    out.append(f'<g {cid}>{"".join(lace)}</g>')
    out.append(ink(wd, INK, 1.4, seed + 11, 1, 0.6))
    # palm and heel pad
    palm = [P(-0.36, 0.2), P(-0.28, -0.06), P(-0.08, -0.14), P(0.2, -0.13), P(0.5, -0.06), P(0.62, 0.06), P(0.52, 0.26), P(0.2, 0.36), P(-0.14, 0.36)]
    out.append(painted(D, palm, pal, seed + 12, sdir=(0.7, 0.6), sk=0.2, angle=-20, n=26, inkw=2, hi=0.45))
    pocket = blob(*P(0.08, 0.08), s * 0.26, s * 0.14, seed + 13, 0.1, 14, -18)
    out.append(f'<path d="{pocket}" fill="{pal[2]}" opacity="0.35"/>')
    # stitching and the heel lacing
    out.append(f'<path d="{smooth_open([P(-0.3, 0.26), P(0.1, 0.32), P(0.48, 0.2)])}" stroke="#F4D8A8" stroke-width="1.4" fill="none" stroke-dasharray="4 4" opacity="0.8"/>')
    for k in range(5):
        a_ = P(-0.2 + k * 0.14, 0.33)
        out.append(f'<path d="{blob(a_[0], a_[1] + 4, s * 0.03, s * 0.014, seed + 20 + k, 0.1, 6, -18)}" fill="#E8C08A" stroke="#6A3A14" stroke-width="0.8"/>')
    return "".join(out)


@design("take-me-out-to-the-ball-game")
def ball_game():
    D = Doc2("us-bg")
    # afternoon sky over the ballpark
    out = [sky(D, [(0, "#4E8ED8"), (0.6, "#9ACCF0"), (1, "#DDF0F8")], 91, 380, ["#6AA8E8", "#C8E8FF"], 40)]
    out.append(puff_cloud(D, 470, 230, 140, 92, pal=("#FFFFFF", "#F6FAFF", "#C8D8EC")))
    out.append(puff_cloud(D, 110, 250, 100, 93, pal=("#FFFFFF", "#F6FAFF", "#C8D8EC")))
    # light towers
    for lx in (84, 520):
        out.append(f'<path d="M {lx} 330 L {lx} 220" stroke="#5A6478" stroke-width="4"/>')
        out.append(f'<path d="{hg.org_rect(lx - 26, 196, 52, 26, lx, 0.3, 8, 2)}" fill="#3A4258"/>')
        for i in range(3):
            for j in range(2):
                out.append(f'<circle cx="{lx - 17 + i * 17}" cy="{203 + j * 12}" r="4" fill="#E8F0F8"/>')
    # outfield wall and grandstand far side
    out.append(painted(D, rect_pts(-10, 300, 610, 336, 30, 94, 0.4), ("#4A9A6A", "#2A6A4A", "#14402A"), 94, sdir=(0, 1), sk=0.1, angle=0, n=30, inkw=1.2, hi=0.2))
    rnd = random.Random(95)
    for i in range(200):
        x, y = rnd.uniform(-10, 610), rnd.uniform(302, 322)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.4, 2.4):.1f}" fill="{rnd.choice(["#F2E2C8", "#D8302A", "#2E4A8A", "#FFFFFF", "#E8B05A"])}" opacity="0.8"/>')
    out.append(f'<rect y="326" width="600" height="10" fill="#1E4A32"/>')
    # the field: mown stripes, infield dirt arc
    fld = "M -10 336 L 610 336 L 610 430 L -10 430 Z"
    out.append(f'<path d="{fld}" fill="#4A9A3E"/>')
    for k in range(-6, 8):
        x = 300 + k * 70
        out.append(f'<path d="M {x} 336 L {x + 35} 336 L {300 + (x + 35 - 300) * 2.2:.1f} 430 L {300 + (x - 300) * 2.2:.1f} 430 Z" fill="#6AB84E" opacity="0.55"/>')
    out.append(f'<path d="M 120 430 Q 300 360 480 430 Z" fill="#C8884A"/>')
    out.append(f'<path d="M 190 430 Q 300 386 410 430 Z" fill="#5AA840"/>')
    out.append(f'<path d="M 120 430 Q 300 360 480 430" stroke="#FFFFFF" stroke-width="1.6" fill="none" opacity="0.4"/>')
    out.append(f'<path d="M 300 372 L 300 376" stroke="#FFFFFF" stroke-width="3"/>')
    # bleacher planks, worn green paint over wood
    for i, (y0, y1) in enumerate(((430, 470), (476, 516), (522, 600))):
        out.append(painted(D, rect_pts(-10, y0, 610, y1, 40, 96 + i, 0.6), ("#7AB88A", "#3E7A5A", "#1E4A36"), 96 + i, sdir=(0, 1), sk=0.12, angle=0, n=50,
                           slen=(40, 140), sw=(1, 3), inkw=1.6, hi=0.3))
        for _ in range(16):
            cx_, cy_ = rnd.uniform(0, 600), rnd.choice([y0 + rnd.uniform(2, 6), y1 - rnd.uniform(2, 6)])
            out.append(f'<path d="{blob(cx_, cy_, rnd.uniform(5, 14), rnd.uniform(1.5, 3), rnd.randint(0, 999), 0.3, 10)}" fill="#C8A070" opacity="0.7"/>')
        for _ in range(5):
            cx_ = rnd.uniform(0, 600)
            out.append(pline([(cx_, rnd.uniform(y0 + 8, y1 - 8)), (cx_ + rnd.uniform(30, 80), rnd.uniform(y0 + 8, y1 - 8))], "#14281E", 1.2, int(cx_), 0.35, 1))
        out.append(f'<rect y="{y1}" width="600" height="6" fill="#14281E" opacity="0.6"/>')
    # peanuts in the shell spilling from a paper bag
    bx, by = 112, 494
    bag = [(bx - 40, by + 26), (bx - 34, by - 40), (bx + 34, by - 46), (bx + 44, by + 22)]
    out.append(cast(D, bx + 6, by + 28, 54, 8, strength=0.5, seed=97))
    out.append(painted(D, pp(bag), ("#F2DCA8", "#D8B474", "#8A6A3A"), 98, sdir=(1, 0.3), sk=0.15, angle=-90, n=14, inkw=1.8, hi=0.4))
    out.append(pline([(bx - 34, by - 40), (bx - 20, by - 50), (bx - 4, by - 42), (bx + 14, by - 54), (bx + 34, by - 46)], INK, 1.6, 99, 0.7))
    out.append(label(bx + 2, by - 4, "HOT", BEBAS, 20, "#B8352A", ls=2))
    out.append(label(bx + 2, by + 16, "PEANUTS", BEBAS, 18, "#B8352A", ls=1))
    for k, (x, y, a) in enumerate(((bx + 54, by + 20, 30), (bx + 70, by + 8, -20), (bx + 46, by + 2, 70), (bx - 46, by + 34, 10), (bx + 86, by + 26, 50))):
        pts = []
        for i in range(20):
            t = 2 * math.pi * i / 20
            rr = 1 - 0.18 * math.cos(2 * t) ** 2
            pts.append((x + 13 * rr * math.cos(t), y + 6.5 * math.sin(t)))
        pts = rot(pts, x, y, a)
        out.append(painted(D, pts, ("#F2DCA8", "#D8B474", "#8A6A3A"), 100 + k, sk=0.2, n=4, inkw=1.2, hi=0.4))
        out.append(specks(110 + k, (x - 8, y - 3, x + 8, y + 3), ["#8A6A3A"], 6, (0.6, 1), (0.5, 0.8)))
    # glove and ball
    out.append(mitt(D, 330, 478, 150, 120))
    out.append(baseball(D, 338, 474, 38, 121))
    # ticket stub
    out.append(ticket_stub(D, 482, 520, 130, 56, -8, 122, lines=("ADMIT ONE", "BLEACHERS · ROW 9"), size=22))
    # lettering
    out.append(letters(D, 300, 100, "Take me out to the", SERIF_IT, 50, "#FFFFFF", ["#FFFFFF", "#EAF4FF"], 123, max_w=420,
                       shadow="#244A80", soff=(0.025, 0.04), angle=-40))
    out.append(letters(D, 300, 184, "BALL GAME", ANTON, 92, "#B8352A", ["#D8503A", "#8A1E12", "#E8704A"], 124, ls=4, max_w=440,
                       shadow="#0E1C3E", soff=(0.02, 0.035), angle=-60, hi="#FFC8A8", wob=0.4))
    return finish_a(D, out, 125)


# ================================================================ 5. bless your heart — biscuits in the skillet, honey
def biscuit(D, cx, cy, r, seed, h=None):
    """Tall buttermilk biscuit seen from above at an angle: golden flaky top, pale layered sides."""
    rnd = random.Random(seed)
    h = h if h is not None else r * 0.55
    out = []
    side = ell_pts(cx, cy, r, r * 0.62, 0, 180, 20) + ell_pts(cx, cy - h, r * 0.97, r * 0.6, 180, 0, 20)
    out.append(painted(D, side, ("#FFF4D8", "#F2DCA8", "#B8945A"), seed, sdir=(0.6, 0.6), sk=0.18, angle=0, n=12, inkw=1.4, hi=0.3))
    cid = D.clip(f'<path d="{smooth_closed(side)}"/>')
    lay = []
    for k in range(1, 5):
        yy = cy - h * k / 5
        lay.append(pline(ell_pts(cx, yy + rnd.uniform(-1, 1), r * 0.99, r * 0.61, 10, 170, 12), "#C8A06A", 1.2, seed + k, 0.55, 1))
    out.append(f'<g {cid}>{"".join(lay)}</g>')
    topp = blob_pts(cx, cy - h, r * 0.97, r * 0.6, seed + 1, 0.05, 20)
    out.append(painted(D, topp, ("#FCE2A0", "#E8A84A", "#A8661E"), seed + 2, sdir=(0.5, 0.8), sk=0.2, angle=-20, n=int(r * 1.2), inkw=1.4, hi=0.35, curve=0.5,
                       cols=["#FFF0C0", "#C87A2A", "#F6CE76", "#A8661E"]))
    cid2 = D.clip(f'<path d="{smooth_closed(topp)}"/>')
    t = [f'<path d="{blob(cx + r * 0.1, cy - h + r * 0.05, r * 0.6, r * 0.35, seed + 3, 0.2, 12)}" fill="#B8681E" opacity="0.3"/>']
    for _ in range(int(r * 0.5)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r * 0.85
        t.append(f'<path d="M {cx + math.cos(a) * rr:.1f} {cy - h + math.sin(a) * rr * 0.6:.1f} l {rnd.uniform(-4, 4):.1f} {rnd.uniform(-2, 2):.1f}" stroke="{rnd.choice(["#8A4A10", "#FFF2C8"])}" stroke-width="1.4" stroke-linecap="round" opacity="0.6"/>')
    out.append(f'<g {cid2}>{"".join(t)}</g>')
    return "".join(out)


def skillet(D, cx, cy, rx, ry, seed, handle_ang=-160, depth=26):
    out = [cast(D, cx + 10, cy + depth + ry * 0.5, rx * 1.15, ry * 0.5, strength=0.55, seed=seed)]
    a = math.radians(handle_ang)
    hx, hy = cx + math.cos(a) * rx, cy + math.sin(a) * ry
    ex, ey = cx + math.cos(a) * (rx + 120), cy + math.sin(a) * (ry + 70) + 8
    out.append(taper([(hx, hy + 10), ((hx + ex) / 2, (hy + ey) / 2 + 8), (ex, ey + 6)], 30, 22, IRON[2]))
    out.append(taper([(hx, hy), ((hx + ex) / 2, (hy + ey) / 2), (ex, ey)], 26, 20, IRON[1]))
    out.append(taper([(hx, hy - 6), ((hx + ex) / 2, (hy + ey) / 2 - 6), (ex, ey - 5)], 4, 3, IRON[0], 0.8))
    out.append(f'<circle cx="{ex - math.cos(a) * 14:.1f}" cy="{ey - math.sin(a) * 6:.1f}" r="5" fill="#2A1E1A"/>')
    side = ell_pts(cx, cy, rx, ry, 0, 180, 24) + ell_pts(cx, cy + depth, rx * 0.96, ry * 0.96, 180, 0, 24)
    side = ell_pts(cx, cy + depth, rx * 0.96, ry * 0.96, 0, 180, 24) + ell_pts(cx, cy, rx, ry, 180, 0, 24)
    out.append(painted(D, side, IRON, seed + 1, sdir=(0.5, 1), sk=0.12, angle=0, n=30, inkw=2, hi=0.3))
    out.append(painted(D, ell_pts(cx, cy, rx, ry, 0, 360, 40)[:-1], ("#4A4850", "#24232A", "#0E0D12"), seed + 2, sdir=(0.3, 1), sk=0.06, angle=0, n=30, inkw=2, hi=0.2))
    out.append(f'<path d="{blob(cx, cy + 4, rx * 0.88, ry * 0.86, seed + 3, 0.01, 30)}" fill="#1A191E"/>')
    out.append(taper(ell_pts(cx, cy, rx - 3, ry - 3, 195, 300, 12), 3, 1, "#8A8890", 0.8))
    return "".join(out)


def honey_dipper(D, x, y, L, ang, seed):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    out = [taper([(x, y), (x + ux * L * 0.62, y + uy * L * 0.62)], 8, 6, "#C8905A")]
    out.append(taper([(x + 1, y - 2), (x + ux * L * 0.62 + 1, y + uy * L * 0.62 - 2)], 2, 1.5, "#F2D0A0", 0.8))
    hx, hy = x + ux * L * 0.8, y + uy * L * 0.8
    for k in range(5):
        t = 0.66 + k * 0.07
        px, py = x + ux * L * t, y + uy * L * t
        out.append(f'<path d="{blob(px, py, 7, 11 - abs(k - 2) * 1.2, seed + k, 0.05, 10, ang)}" fill="#E8A030" stroke="#8A4A0A" stroke-width="1"/>')
        out.append(f'<path d="{blob(px - 2, py - 3, 2.4, 4, seed + 10 + k, 0.1, 8, ang)}" fill="#FFE8A0" opacity="0.8"/>')
    out.append(taper([(hx, hy + 8), (hx + 2, hy + 40), (hx - 1, hy + 70)], 7, 2, "#E8A030", 0.95))
    out.append(taper([(hx - 1, hy + 10), (hx + 1, hy + 40)], 2, 1, "#FFF2C0", 0.8))
    return "".join(out)


@design("bless-your-heart")
def bless_your_heart():
    D = Doc2("us-bh")
    out = [paper(D.nid(), "#F6E8CE", FLECK, 131)]
    out.append(blooms(132, ["#E8C890", "#D8B07A", "#F2D8A8"], 6, (0, 0, 600, 600), (100, 200), (0.06, 0.12)))
    # blue gingham cloth across the table (top half is the wall/table edge)
    out.append(wood_planks(D, 236, 600, 133, OAK, 5))
    tc = [(-20, 300), (330, 268), (640, 318), (640, 640), (-20, 640)]
    out.append(cloth(D, tc, "#3A6AB8", 134, cell=22, rot_=-6, light=(0.0, 0.0, 1.0, 1.0), folds=[((60, 330), (120, 460), (90, 620)), ((520, 340), (470, 480), (520, 620))]))
    # skillet of biscuits
    out.append(skillet(D, 292, 404, 186, 104, 135, handle_ang=200, depth=28))
    spots = [(222, 352), (300, 340), (378, 352), (186, 410), (264, 404), (342, 404), (418, 412), (226, 460), (306, 462), (384, 458)]
    for i, (x, y) in enumerate(sorted(spots, key=lambda p: p[1])):
        out.append(biscuit(D, x, y, 40, 140 + i, h=22))
    # butter pat melting on top
    bx, by = 300, 316
    out.append(f'<path d="{blob(bx + 4, by + 8, 30, 12, 151, 0.2, 14)}" fill="#FFE88A" opacity="0.75"/>')
    out.append(painted(D, pp([(bx - 18, by - 4), (bx + 14, by - 10), (bx + 22, by + 4), (bx - 10, by + 10)]), ("#FFFCE0", "#FFE88A", "#D8B040"), 152, sk=0.15, n=6, inkw=1.2, hi=0.6))
    out.append(taper([(bx - 12, by - 2), (bx + 8, by - 6)], 3, 1, "#FFFFFF", 0.9))
    # honey dipper drizzling over the biscuits
    out.append(honey_dipper(D, 470, 248, 150, 150, 153))
    out.append(taper([(334, 330), (350, 340), (366, 336), (380, 346)], 6, 4, "#E8A030", 0.85))
    out.append(taper([(340, 332), (366, 338)], 2, 1, "#FFF2C0", 0.8))
    # a jar of honey with a gingham lid
    jx, jb = 504, 520
    out.append(cast(D, jx + 8, jb + 2, 46, 8, strength=0.5, seed=154))
    jar = [(jx - 38, jb - 82), (jx - 42, jb - 40), (jx - 38, jb - 4), (jx + 38, jb - 4), (jx + 42, jb - 40), (jx + 38, jb - 82)]
    out.append(painted(D, jar, ("#FFD86A", "#E89A1E", "#9A5A0A"), 155, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=14, inkw=1.8, hi=0.5))
    out.append(taper([(jx - 28, jb - 74), (jx - 30, jb - 14)], 6, 3, "#FFF6C8", 0.7))
    out.append(painted(D, rect_pts(jx - 30, jb - 66, jx + 30, jb - 30, 12, 156, 0.4), CREAM, 156, sk=0.1, n=6, inkw=1.2, hi=0.3))
    out.append(label(jx, jb - 42, "HONEY", BEBAS, 20, "#7A3A10", ls=2))
    lid = [(jx - 44, jb - 84), (jx - 34, jb - 104), (jx, jb - 108), (jx + 34, jb - 104), (jx + 44, jb - 84), (jx, jb - 78)]
    out.append(cloth(D, lid, "#D8382E", 157, cell=8))
    out.append(taper([(jx - 40, jb - 84), (jx + 40, jb - 84)], 3, 3, "#8A5A2A"))
    # a sprig of cotton for the South
    for k, (x, y) in enumerate(((84, 520), (112, 546))):
        out.append(pline([(x, y + 40), (x + 4, y + 10), (x, y)], "#6A4A2A", 3, 158 + k, 1, 1))
        for j in range(5):
            a = math.radians(j * 72 - 90)
            out.append(f'<path d="{blob(x + math.cos(a) * 10, y + math.sin(a) * 9, 11, 9, 160 + k * 7 + j, 0.15, 10)}" fill="#FFFFFF" stroke="#C8C0B0" stroke-width="1"/>')
        out.append(f'<path d="M {x - 12} {y + 10} l 8 -4 l 4 6 l 4 -6 l 8 4" stroke="#5A3A1A" stroke-width="2.4" fill="none"/>')
    # lettering
    out.append(letters(D, 300, 128, "Bless Your Heart", SERIF_IT, 82, "#8A2A1A", ["#B8452A", "#6A1A0E", "#D06040"], 161, max_w=470,
                       shadow="#FFF6E0", soff=(0.02, 0.03), angle=-40, hi="#F8B08A"))
    out.append(ruled(300, 178, "AND PASS THE BISCUITS", "#2E5AA8", font=JOS, size=22, ls=5, line_w=24, gap=12, max_w=380))
    return finish_a(D, out, 162)


# ================================================================ 6. the mother road — two-lane blacktop through the desert
def telephone_pole(x, base, h, col="#3A2418"):
    return (taper([(x, base), (x, base - h)], max(1.5, h * 0.04), max(1, h * 0.03), col) +
            f'<path d="M {x - h * 0.16:.1f} {base - h * 0.92:.1f} L {x + h * 0.16:.1f} {base - h * 0.92:.1f} M {x - h * 0.11:.1f} {base - h * 0.82:.1f} L {x + h * 0.11:.1f} {base - h * 0.82:.1f}" stroke="{col}" stroke-width="{max(1, h * 0.025):.1f}"/>')


def mesa(D, pts, bottom, pal, seed, strata=True):
    out = [hill(D, pts, bottom, pal, seed, angle=-90, inkw=1.2, inkop=0.4, sop=(0.1, 0.3))]
    if strata:
        rnd = random.Random(seed)
        xs = [p[0] for p in pts]
        top_y = min(p[1] for p in pts)
        for k in range(3):
            y = top_y + 10 + k * 12 + rnd.uniform(-2, 2)
            out.append(pline([(min(xs) + 20, y), ((min(xs) + max(xs)) / 2, y + rnd.uniform(-2, 2)), (max(xs) - 20, y + 1)], pal[2], 1.6, seed + k, 0.35, 1))
    return "".join(out)


def yucca(D, x, base, h, seed, col=("#B8C890", "#7A8A5A", "#3E4A2A")):
    rnd = random.Random(seed)
    out = []
    for k in range(14):
        a = math.radians(-90 + rnd.uniform(-70, 70))
        L = h * rnd.uniform(0.6, 1)
        out.append(taper([(x, base), (x + math.cos(a) * L, base + math.sin(a) * L)], 4, 0.6, rnd.choice(col)))
    out.append(taper([(x, base - h * 0.4), (x + 2, base - h * 1.8)], 3, 2, "#7A6A3A"))
    for k in range(6):
        out.append(f'<circle cx="{x + 2 + rnd.uniform(-5, 5):.1f}" cy="{base - h * (1.3 + k * 0.08):.1f}" r="3.2" fill="#FFF8E0" stroke="#C8B890" stroke-width="0.8"/>')
    return "".join(out)


@design("the-mother-road")
def the_mother_road():
    D = Doc2("us-mr")
    out = [sky(D, [(0, "#3A6AB0"), (0.35, "#E89A6A"), (0.62, "#FFD08A"), (1, "#FFE8B8")], 171, 380, ["#F2B080", "#FFE0A8", "#5A7AB8"], 50)]
    out.append(soft_glow(D, 300, 330, 220, "#FFF2C0", 0.75))
    out.append(f'<circle cx="300" cy="318" r="34" fill="#FFF4D0"/>')
    # thin painted clouds catching the light
    for k, (x, y, w) in enumerate(((120, 150, 180), (460, 120, 220), (330, 210, 150))):
        out.append(taper([(x - w / 2, y), (x, y - 6), (x + w / 2, y + 2)], 3, 10, "#FFC8A0", 0.7))
        out.append(taper([(x - w / 2 + 20, y + 6), (x, y + 2), (x + w / 2 - 20, y + 8)], 2, 6, "#D88A8A", 0.45))
    # mesas, far to near
    out.append(mesa(D, [(-20, 330), (40, 300), (60, 262), (170, 258), (190, 290), (250, 330)], 380, ("#E8A890", "#C08080", "#8A5A6A"), 172))
    out.append(mesa(D, [(360, 330), (400, 270), (420, 236), (520, 232), (540, 270), (620, 300)], 380, ("#E8A890", "#C07A78", "#8A5262"), 173))
    out.append(mesa(D, [(440, 340), (470, 300), (560, 296), (580, 320), (620, 330)], 380, ("#E89A72", "#B8604A", "#7A3A2E"), 174))
    # desert floor
    out.append(hill(D, [(-20, 350), (200, 346), (400, 350), (620, 344)], 620, ("#F2C890", "#D89A60", "#9A6034"), 175, angle=-2, inkw=0))
    # the road: two lanes narrowing to the vanishing point
    vp = (300, 348)
    road = [(vp[0] - 4, vp[1]), (vp[0] + 4, vp[1]), (560, 620), (40, 620)]
    out.append(painted(D, road, ("#6A6070", "#3E3844", "#1E1A22"), 176, sdir=(0, -1), sk=0.04, angle=-90, n=60, inkw=0, hi=0.0))
    out.append(f'<path d="{pd(road)}" fill="{D.lin([(0, "#FFD8A0", 0.35), (0.3, "#FFD8A0", 0), (1, "#000000", 0)])}"/>')
    # shoulders and centre dashes
    for sg in (-1, 1):
        out.append(pline([(vp[0] + sg * 3, vp[1] + 1), (300 + sg * 240, 620)], "#FFF2D8", 2.6, 177 + sg, 0.85, 1))
    for k in range(9):
        t0 = (k / 9) ** 1.8
        t1 = ((k + 0.5) / 9) ** 1.8
        y0, y1 = vp[1] + (620 - vp[1]) * t0, vp[1] + (620 - vp[1]) * t1
        w0, w1 = 1 + 8 * t0, 1 + 8 * t1
        out.append(f'<path d="M {300 - w0 / 2:.1f} {y0:.1f} L {300 + w0 / 2:.1f} {y0:.1f} L {300 + w1 / 2:.1f} {y1:.1f} L {300 - w1 / 2:.1f} {y1:.1f} Z" fill="#F6C83A"/>')
    # telephone poles receding along the left
    for k in range(7):
        t = (k / 7) ** 1.6
        x = vp[0] - 20 - (300 - 20 - 46) * t * 1.0
        base = vp[1] + 2 + (600 - vp[1]) * t * 0.92
        h = 14 + 210 * t
        out.append(telephone_pole(x, base, h, "#4A2E22"))
    # sagging wires between them
    tops = []
    for k in range(7):
        t = (k / 7) ** 1.6
        tops.append((vp[0] - 20 - (300 - 20 - 46) * t, vp[1] + 2 + (600 - vp[1]) * t * 0.92 - (14 + 210 * t) * 0.92))
    for a, b in zip(tops, tops[1:]):
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} Q {(a[0] + b[0]) / 2:.1f} {(a[1] + b[1]) / 2 + 10:.1f} {b[0]:.1f} {b[1]:.1f}" stroke="#4A2E22" stroke-width="1.2" fill="none" opacity="0.8"/>')
    # sagebrush, yucca and a roadside sign
    rnd = random.Random(178)
    for _ in range(26):
        x, y = rnd.choice([rnd.uniform(-10, 180), rnd.uniform(420, 610)]), rnd.uniform(360, 600)
        s = 3 + (y - 350) * 0.06
        out.append(dab_crown(D, x, y, s * 1.6, s, [SAGE, ("#B8C08A", "#8A9060", "#5A6040")], int(x * 3 + y), n=8, size=(s * 0.4, s * 0.7), inkw=0, base=False))
    out.append(yucca(D, 520, 560, 70, 179))
    out.append(yucca(D, 456, 436, 34, 180))
    sx, sb = 92, 470
    out.append(taper([(sx, sb), (sx, sb - 100)], 6, 5, "#6A4A30"))
    sp = [(sx - 46, sb - 136), (sx + 46, sb - 136), (sx + 46, sb - 92), (sx - 46, sb - 92)]
    out.append(painted(D, pp(sp), CREAM, 181, sk=0.1, n=8, inkw=1.8, hi=0.3))
    out.append(label(sx, sb - 116, "GAS · EATS", BEBAS, 22, "#B8352A", ls=2, max_w=80))
    out.append(label(sx, sb - 98, "NEXT EXIT", MONO, 12, "#3A2418", ls=1, max_w=80))
    # a two-tone sedan heading west into the sunset
    out.append(car50(D, 338, 492, 150, 182, body=CHERRY, roof=CREAM, flip=-1, tail=True))
    out.append(cast(D, 338, 498, 90, 6, strength=0.3, seed=183))
    # lettering
    out.append(letters(D, 300, 124, "the Mother Road", SERIF_IT, 78, "#FFF6E0", ["#FFFFFF", "#FFE8C8"], 184, max_w=440,
                       shadow="#7A2E2A", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 168, "CHICAGO TO THE PACIFIC", "#FFF6E0", font=JOS, size=20, ls=5, line_w=22, gap=10, max_w=380))
    return finish_a(D, out, 185)


# ================================================================ 7. county fair — Ferris wheel at dusk, blue-ribbon pie
def ferris_wheel(D, cx, cy, R, seed, base_y, cars=12):
    rnd = random.Random(seed)
    out = [D.glow(cx, cy, R * 1.5, "#FFC870", 0.25)]
    # A-frame legs
    for sg in (-1, 1):
        for dz, col, w in ((0, "#3A2A4A", 7), (10, "#5A4A6A", 4)):
            out.append(taper([(cx, cy), (cx + sg * (R * 0.55 + dz), base_y)], w, w + 2, col))
    out.append(pline([(cx - R * 0.3, cy + (base_y - cy) * 0.55), (cx + R * 0.3, cy + (base_y - cy) * 0.55)], "#3A2A4A", 4, seed, 1, 1))
    # spokes
    for i in range(cars * 2):
        a = 2 * math.pi * i / (cars * 2)
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {cx + math.cos(a) * R:.1f} {cy + math.sin(a) * R:.1f}" stroke="#F4E8F0" stroke-width="1.6" opacity="0.75"/>')
    # rims
    for rr, w, col in ((R, 5, "#F4E8F0"), (R * 0.9, 2.4, "#E8D0E0"), (R * 0.32, 2.2, "#E8D0E0")):
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}" fill="none" stroke="{col}" stroke-width="{w}"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="none" stroke="#3A2A4A" stroke-width="1.2" opacity="0.6"/>')
    # bulbs around the rim
    for i in range(cars * 4):
        a = 2 * math.pi * (i + 0.5) / (cars * 4)
        x, y = cx + math.cos(a) * R, cy + math.sin(a) * R
        col = "#FFE89A" if i % 2 else "#FF9AC0"
        out.append(D.glow(x, y, 9, col, 0.6))
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.4" fill="#FFFFFF"/>')
    for i in range(cars * 2):
        a = 2 * math.pi * i / (cars * 2)
        x, y = cx + math.cos(a) * R * 0.62, cy + math.sin(a) * R * 0.62
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.8" fill="#FFF2C0"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R * 0.08:.1f}" fill="#E8C048" stroke="#3A2A4A" stroke-width="2"/>')
    # gondolas hang straight down from the rim
    cols = [CHERRY, MUSTARD, AQUA, NAVY, ("#FFB8D8", "#E85A9A", "#9A2058"), CREAM]
    for i in range(cars):
        a = 2 * math.pi * i / cars + 0.12
        x, y = cx + math.cos(a) * R, cy + math.sin(a) * R
        c = cols[i % len(cols)]
        out.append(f'<path d="M {x:.1f} {y:.1f} L {x:.1f} {y + 10:.1f}" stroke="#3A2A4A" stroke-width="2"/>')
        car = [(x - 14, y + 10), (x + 14, y + 10), (x + 12, y + 26), (x + 6, y + 30), (x - 6, y + 30), (x - 12, y + 26)]
        out.append(painted(D, car, c, seed + i, sdir=(0.6, 0.6), sk=0.15, angle=0, n=4, inkw=1.4, inkop=0.8, hi=0.4))
        out.append(f'<path d="M {x - 16:.1f} {y + 10:.1f} Q {x:.1f} {y + 2:.1f} {x + 16:.1f} {y + 10:.1f}" fill="{c[2]}" stroke="#3A2A4A" stroke-width="1.2"/>')
    return "".join(out)


def big_top(D, cx, base, w, h, seed, cols=("#D8302A", "#FFF6E8"), flag="#F6C21C"):
    """Striped carnival tent: drum walls, conical roof with stripes to the peak, scalloped valance, a pennant."""
    out = [cast(D, cx, base, w * 0.6, 6, strength=0.4, seed=seed)]
    wall_h = h * 0.38
    peak = (cx, base - h)
    l, r = cx - w / 2, cx + w / 2
    wall = [(l, base), (l, base - wall_h), (r, base - wall_h), (r, base)]
    out.append(painted(D, pp(wall), ("#FFF6E8", "#F2E2CC", "#B8A08A"), seed, sk=0.1, n=6, inkw=1.4, hi=0.2))
    n = 8
    for k in range(n):
        if k % 2:
            continue
        a, b = l + w * k / n, l + w * (k + 1) / n
        out.append(f'<path d="M {a:.1f} {base:.1f} L {a:.1f} {base - wall_h:.1f} L {b:.1f} {base - wall_h:.1f} L {b:.1f} {base:.1f} Z" fill="{cols[0]}" opacity="0.92"/>')
    out.append(f'<path d="M {cx - w * 0.07:.1f} {base:.1f} L {cx:.1f} {base - wall_h * 0.85:.1f} L {cx + w * 0.07:.1f} {base:.1f} Z" fill="#2A1A2A"/>')
    out.append(f'<path d="{pd(wall)}" fill="{D.lin([(0, "#2A1A3A", 0), (1, "#2A1A3A", 0.35)], 0, 0, 1, 0)}"/>')
    roof = [(l - 6, base - wall_h), peak, (r + 6, base - wall_h)]
    out.append(painted(D, pp(roof), ("#FFF6E8", "#F2E2CC", "#B8A08A"), seed + 1, sk=0.1, n=6, inkw=1.6, hi=0.2))
    for k in range(n):
        if k % 2:
            continue
        a, b = l - 6 + (w + 12) * k / n, l - 6 + (w + 12) * (k + 1) / n
        out.append(f'<path d="M {a:.1f} {base - wall_h:.1f} L {peak[0]:.1f} {peak[1]:.1f} L {b:.1f} {base - wall_h:.1f} Z" fill="{cols[0]}" opacity="0.92"/>')
    out.append(f'<path d="{pd(roof)}" fill="{D.lin([(0, "#2A1A3A", 0), (1, "#2A1A3A", 0.35)], 0, 0, 1, 0)}"/>')
    for k in range(n):
        a = l - 6 + (w + 12) * (k + 0.5) / n
        out.append(f'<path d="M {a - (w + 12) / n / 2:.1f} {base - wall_h:.1f} Q {a:.1f} {base - wall_h + 12:.1f} {a + (w + 12) / n / 2:.1f} {base - wall_h:.1f}" fill="{cols[0] if k % 2 == 0 else "#FFF6E8"}" stroke="#3A2418" stroke-width="1"/>')
    out.append(ink(pd(roof), INK, 1.4, seed, 1, 0.6))
    out.append(f'<path d="M {peak[0]:.1f} {peak[1]:.1f} L {peak[0]:.1f} {peak[1] - 18:.1f}" stroke="#3A2418" stroke-width="2"/>')
    out.append(f'<path d="M {peak[0]:.1f} {peak[1] - 18:.1f} L {peak[0] + 16:.1f} {peak[1] - 13:.1f} L {peak[0]:.1f} {peak[1] - 8:.1f} Z" fill="{flag}"/>')
    return "".join(out)


def rosette(D, cx, cy, r, seed, col=("#6A9AE8", "#1E4AA8", "#0C2462"), text="1ST", sub="PRIZE", tails=80):
    """Blue-ribbon rosette: two tails, a pleated ring, a satin ring and a printed centre button."""
    out = []
    for sg in (-1, 1):
        tl = [(cx + sg * r * 0.12, cy), (cx + sg * r * 0.55, cy + tails * 0.5), (cx + sg * r * 0.7, cy + tails), (cx + sg * r * 0.48, cy + tails * 0.88),
              (cx + sg * r * 0.36, cy + tails + 6), (cx + sg * r * 0.3, cy + tails * 0.3)]
        out.append(painted(D, tl, col, seed + sg, sdir=(sg, 0.4), sk=0.15, angle=-80, n=10, inkw=1.6, hi=0.4))
        out.append(taper([(cx + sg * r * 0.2, cy + 6), (cx + sg * r * 0.45, cy + tails * 0.6)], 3, 1, "#FFFFFF", 0.45))
    n = 28
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n
        rr = r * (1.0 if i % 2 == 0 else 0.84)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    out.append(painted(D, pts, col, seed + 3, sdir=(0.6, 0.7), sk=0.06, angle=0, n=10, inkw=1.4, hi=0.3))
    for i in range(n):
        a = 2 * math.pi * i / n
        out.append(f'<path d="M {cx + math.cos(a) * r * 0.45:.1f} {cy + math.sin(a) * r * 0.45:.1f} L {cx + math.cos(a) * r * 0.92:.1f} {cy + math.sin(a) * r * 0.92:.1f}" stroke="{col[2] if i % 2 else col[0]}" stroke-width="1.6" opacity="0.6"/>')
    out.append(painted(D, blob_pts(cx, cy, r * 0.62, r * 0.62, seed + 4, 0.01, 24), (lt(col[0], 0.3), col[0], col[1]), seed + 4, sdir=(0.6, 0.7), sk=0.15, angle=-30, n=8, inkw=1.2, hi=0.4))
    out.append(painted(D, blob_pts(cx, cy, r * 0.46, r * 0.46, seed + 5, 0.01, 24), ("#FFF8E8", "#F2E8D0", "#B8A888"), seed + 5, sdir=(0.6, 0.7), sk=0.15, angle=-30, n=6, inkw=1.4, hi=0.4))
    fs = fit_size(text, BEBAS, r * 0.42, r * 0.7)
    out.append(f'<text x="{cx:.1f}" y="{cy + fs * 0.18:.1f}" text-anchor="middle" {BEBAS} font-size="{fs}" fill="{col[1]}">{esc(text)}</text>')
    if sub:
        fs2 = fit_size(sub, BEBAS, r * 0.17, r * 0.6)
        out.append(f'<text x="{cx:.1f}" y="{cy + fs * 0.18 + fs2 * 1.1:.1f}" text-anchor="middle" {BEBAS} font-size="{fs2}" letter-spacing="1" fill="{col[1]}">{esc(sub)}</text>')
    out.append(f'<path d="{blob(cx - r * 0.25, cy - r * 0.25, r * 0.12, r * 0.06, seed, 0.2, 8, -40)}" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


@design("county-fair")
def county_fair():
    D = Doc2("us-cf")
    out = [sky(D, [(0, "#2A2A64"), (0.38, "#7A4A8A"), (0.7, "#F2885A"), (1, "#FFD08A")], 191, 470, ["#4A3A7A", "#F2A07A", "#FFC890"], 60)]
    out.append(stars_field(192, 30, (0, 0, 600, 130), avoid=((80, 40, 520, 180),)))
    out.append(soft_glow(D, 200, 430, 260, "#FFD890", 0.5))
    # far tree line
    rnd = random.Random(193)
    out.append(hill(D, ridge([(-20, 432), (150, 424), (320, 430), (620, 422)], 193, 4), 600, ("#5A3A5A", "#3A2440", "#1E1428"), 193, inkw=0))
    for _ in range(26):
        x = rnd.uniform(-10, 610)
        out.append(dab_crown(D, x, 418, rnd.uniform(18, 30), rnd.uniform(14, 22), [("#5A3A5A", "#3A2440", "#24182E")], int(x * 7), n=10, size=(6, 10), inkw=0, base=False))
    # the wheel, tents, string lights
    out.append(ferris_wheel(D, 410, 304, 126, 194, 470))
    out.append(big_top(D, 130, 460, 176, 128, 195))
    out.append(big_top(D, 262, 462, 96, 84, 196, cols=("#1E5AA8", "#FFF6E8"), flag="#D8302A"))
    sl = [(-10, 330), (60, 352), (130, 334)]
    for (a, b) in zip(sl, sl[1:]):
        out.append(f'<path d="M {a[0]} {a[1]} Q {(a[0] + b[0]) / 2} {(a[1] + b[1]) / 2 + 14} {b[0]} {b[1]}" stroke="#2A1A2A" stroke-width="1.4" fill="none"/>')
    out.append(bulbs_row(D, [(-10 + t * 140, 330 + 14 * math.sin(math.pi * t * 2) * 0.5 + (4 if t > 0.5 else 0)) for t in [i / 9 for i in range(10)]], 197, r=2.6))
    # fairground and folks strolling
    out.append(f'<rect y="458" width="600" height="40" fill="{D.lin([(0, "#6A4A5A"), (1, "#3A2A3A")])}"/>')
    out.append(f'<ellipse cx="400" cy="462" rx="200" ry="20" fill="{D.rad([(0, "#FFC870", 0.5), (1, "#FFC870", 0)])}"/>')
    for k, (x, f) in enumerate(((210, 1), (236, -1), (330, 1), (470, -1), (500, -1), (560, 1))):
        out.append(figures.person(x, 476, 30 if k != 3 else 22, "walk" if k != 3 else "child_walk", f, None, 198 + k, rim="#FFC878", tint=("#5A3A6A", 0.3)))
    # judging table with a red checked cloth
    tbl = [(-20, 482), (620, 474), (620, 640), (-20, 640)]
    out.append(cloth(D, tbl, "#D8302A", 199, cell=18, rot_=0, light=(0, 0, 0.0, 1.0), folds=[((120, 500), (110, 560), (126, 620)), ((470, 500), (480, 560), (466, 620))]))
    out.append(f'<rect y="474" width="600" height="14" fill="#FFFFFF" opacity="0.2"/>')
    # the winning cherry pie on a cake stand, and its rosette
    sx, sy = 236, 520
    out.append(cast(D, sx + 10, sy + 64, 110, 12, strength=0.5, seed=200))
    out.append(painted(D, pp([(sx - 34, sy + 64), (sx - 12, sy + 26), (sx + 12, sy + 26), (sx + 34, sy + 64)]), ("#FFFFFF", "#E8EEF2", "#9AA8B4"), 201, sdir=(1, 0.2), sk=0.15, angle=-90, n=6, inkw=1.6, hi=0.5))
    out.append(painted(D, ell_pts(sx, sy + 22, 146, 20, 0, 360, 36)[:-1], ("#FFFFFF", "#E8EEF2", "#9AA8B4"), 202, sdir=(0.3, 1), sk=0.15, angle=0, n=12, inkw=1.6, hi=0.5))
    out.append(lattice_pie(D, sx, sy - 6, 124, 40, 203, "cherry", depth=22))
    out.append(rosette(D, 456, 494, 60, 204, text="1ST", sub="BEST PIE", tails=80))
    out.append(taper([(450, 452), (452, 440)], 3, 3, "#C8D0DA"))
    # lettering
    out.append(letters(D, 300, 124, "County Fair", SERIF_IT, 96, "#FFF2D8", ["#FFFFFF", "#FFE2C0", "#FFD0A8"], 205, max_w=440,
                       shadow="#5A1E3A", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 166, "BLUE RIBBON PIE", "#FFE08A", font=JOS, size=22, ls=6, line_w=28, gap=12, max_w=320))
    return finish_a(D, out, 206)


# ================================================================ 8. lemonade stand — a kid's stand on the sidewalk
def kid_letters(D, x, y, s, font, size, cols, seed, max_w=400, ls=2, outline="#3A2418", wob=6):
    """Hand-painted kid lettering: every letter its own colour and tilt, a wobbly marker outline."""
    fs = fit_size(s, font, size, max_w, ls)
    W = measure(s, font, fs, ls)
    rnd = random.Random(seed)
    gx = x - W / 2
    out = []
    for i, ch in enumerate(s):
        adv = measure(ch, font, fs) + ls
        if ch != " ":
            r = rnd.uniform(-wob, wob)
            dy = rnd.uniform(-3, 3)
            c = cols[i % len(cols)]
            cxg = gx + adv / 2
            t = f'<text x="{gx:.1f}" y="{y + dy:.1f}" {font} font-size="{fs}" transform="rotate({r:.1f} {cxg:.1f} {y:.1f})"'
            out.append(f'{t} fill="none" stroke="{outline}" stroke-width="{fs * 0.09:.1f}" stroke-linejoin="round">{esc(ch)}</text>')
            out.append(f'{t} fill="{c}">{esc(ch)}</text>')
            out.append(f'{t} fill="none" stroke="{lt(c, 0.5)}" stroke-width="{fs * 0.018:.1f}" opacity="0.7" transform="rotate({r:.1f} {cxg:.1f} {y:.1f}) translate(-1.5 -1.5)">{esc(ch)}</text>')
        gx += adv
    return "".join(out)


def pitcher_glass(D, cx, base, w, h, seed, drink=("#FFF6A0", "#F8E05A", "#C8A820"), ice=True, lemons=True, handle=1):
    out = [cast(D, cx + 8, base + 2, w * 0.7, 8, strength=0.45, seed=seed)]
    l, r = cx - w / 2, cx + w / 2
    top = base - h
    body = [(l + 6, top + 10), (l, top + h * 0.5), (l + 4, base - 6), (l + 12, base), (r - 12, base), (r - 4, base - 6), (r, top + h * 0.5), (r - 6, top + 10), (r + 4, top), (l - 12, top - 6)]
    hp = [(r - 4, top + 18), (r + 30 * handle, top + 20), (r + 34 * handle, top + h * 0.5), (r + 18 * handle, top + h * 0.78), (r - 2, top + h * 0.8)]
    out.append(ink(smooth_open(hp), "#C8DCE4", 9, seed, 1, 0.9))
    out.append(ink(smooth_open(hp), "#FFFFFF", 3, seed + 1, 1, 0.8))
    bd = smooth_closed(body)
    out.append(f'<path d="{bd}" fill="#EAF6F8" opacity="0.5"/>')
    cid = D.clip(f'<path d="{bd}"/>')
    lvl = top + h * 0.2
    inner = [f'<rect x="{l - 20:.1f}" y="{lvl:.1f}" width="{w + 40:.1f}" height="{h:.1f}" fill="{D.lin([(0, drink[0]), (0.6, drink[1]), (1, drink[2])], 0, 0, 1, 0)}"/>']
    rnd = random.Random(seed)
    if ice:
        for k in range(6):
            ix, iy = cx + rnd.uniform(-w * 0.3, w * 0.3), lvl + rnd.uniform(4, h * 0.6)
            inner.append(f'<path d="{hg.org_rect(ix - 10, iy - 10, 20, 18, seed + k, 0.8, 6, 4)}" fill="#FFFFFF" opacity="0.45" transform="rotate({rnd.uniform(-30, 30):.0f} {ix:.1f} {iy:.1f})"/>')
    if lemons:
        for k in range(2):
            lx, ly = cx + (-1) ** k * w * 0.18, lvl + 30 + k * 30
            inner.append(citrus_slice(D, lx, ly, w * 0.16, seed + 20 + k, ("#FFF6B0", "#FFE24A", "#D8B010"), "#FFFCE8", ("#FFF07A", "#FFD21A", "#C89A0A")))
    for _ in range(18):
        inner.append(f'<circle cx="{rnd.uniform(l, r):.1f}" cy="{rnd.uniform(lvl + 6, base - 6):.1f}" r="{rnd.uniform(0.8, 2):.1f}" fill="#FFFFFF" opacity="0.6"/>')
    inner.append(f'<path d="M {l - 20} {lvl:.1f} L {r + 20} {lvl:.1f}" stroke="#FFFCE0" stroke-width="3" opacity="0.8"/>')
    inner.append(shade_over(D, bd, "#4A3A0A", 0.25, 0, 0, 1, 0, 0.6))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(taper([(l + 10, top + 20), (l + 6, top + h * 0.5), (l + 12, base - 14)], 7, 2, "#FFFFFF", 0.75))
    out.append(ink(bd, "#7A9AA8", 1.8, seed + 2, 2, 0.7))
    return "".join(out)


@design("lemonade-stand")
def lemonade_stand():
    D = Doc2("us-ls")
    out = [sky(D, [(0, "#5AA0E0"), (0.7, "#A8D8F4"), (1, "#E0F2F8")], 211, 330, ["#7AB8EE", "#D8F0FF"], 30)]
    out.append(puff_cloud(D, 470, 120, 150, 212, pal=("#FFFFFF", "#F6FAFF", "#C8D8EC")))
    # a white house and picket fence across the street
    out.append(painted(D, rect_pts(330, 150, 640, 330, 30, 213, 0.4), ("#FFFFFF", "#EEF2F6", "#A8B4C4"), 213, sk=0.08, n=10, inkw=1.4, hi=0.2))
    for y in range(160, 330, 12):
        out.append(f'<path d="M 330 {y} L 640 {y}" stroke="#A8B4C4" stroke-width="1.4" opacity="0.6"/>')
    out.append(painted(D, pp([(310, 156), (470, 70), (640, 156)]), ("#8A9AB0", "#4A5A78", "#24304A"), 214, sk=0.1, n=10, inkw=1.6, hi=0.3))
    for wx in (380, 500):
        out.append(f'<path d="{hg.org_rect(wx, 190, 44, 56, wx, 0.3, 8, 2)}" fill="#3A5068"/>')
        out.append(f'<path d="M {wx + 22} 190 L {wx + 22} 246 M {wx} 218 L {wx + 44} 218" stroke="#FFFFFF" stroke-width="3"/>')
        for sx in (wx - 14, wx + 46):
            out.append(f'<path d="{hg.org_rect(sx, 188, 12, 60, sx, 0.3, 8, 1)}" fill="#2E5AA8"/>')
    # big shade tree on the left
    out.append(taper([(80, 340), (90, 240), (120, 160)], 30, 16, "#6A4A2E"))
    out.append(dab_crown(D, 110, 120, 170, 110, [GRASS, SAGE, ("#A8D070", "#5A8A30", "#2A4A1A")], 215, n=220, size=(9, 16), inkw=1.2))
    out.append(hill(D, [(-20, 326), (300, 322), (620, 326)], 420, GRASS, 216, angle=0, inkw=0))
    out.append(picket_fence(D, -10, 610, 290, 334, 217, w=12, gap=9))
    out.append(grass(218, (0, 326, 600, 420), ["#5A8A30", "#8AB850", "#2E5A1E"], 160, (6, 14)))
    # sidewalk with chalk drawings
    out.append(f'<path d="M 0 420 L 600 420 L 600 600 L 0 600 Z" fill="#D8D2C8"/>')
    out.append(strokes(D.nid(), "M 0 420 L 600 420 L 600 600 L 0 600 Z", (-40, 420, 600, 600), ["#C8C0B4", "#E8E2D8", "#B8B0A4"], 219, n=60, angle=0, length=(40, 120), width=(2, 5)))
    for y in (470, 540):
        out.append(f'<path d="M 0 {y} L 600 {y + 4}" stroke="#A8A094" stroke-width="2"/>')
    out.append(f'<circle cx="514" cy="560" r="16" fill="none" stroke="#F6C21C" stroke-width="4" opacity="0.8"/>')
    for k in range(8):
        a = math.radians(k * 45)
        out.append(f'<path d="M {514 + math.cos(a) * 22:.1f} {560 + math.sin(a) * 22:.1f} l {math.cos(a) * 9:.1f} {math.sin(a) * 9:.1f}" stroke="#F6C21C" stroke-width="4" stroke-linecap="round" opacity="0.8"/>')
    out.append(p_heart(D, 96, 558, 16, ("#FFB8D8", "#F06AA8", "#A8306A"), 220, -10, inkw=0))
    # the stand: crate legs, counter, striped awning on posts
    x0, x1, ct = 116, 484, 330
    out.append(cast(D, 300, 560, 220, 14, strength=0.45, seed=221))
    for px in (x0 + 10, x1 - 22):
        out.append(painted(D, rect_pts(px, 150, px + 12, 556, 20, int(px), 0.4), WOOD, int(px), sdir=(1, 0), sk=0.2, angle=-90, n=10, inkw=1.4, hi=0.3))
    aw = [(x0 - 16, 140), (x1 + 16, 140), (x1 + 22, 196), (x0 - 22, 196)]
    out.append(painted(D, pp(aw), ("#FFFDF0", "#FFF6D8", "#C8B888"), 222, sk=0.1, n=10, inkw=1.6, hi=0.2))
    for k in range(10):
        if k % 2 == 0:
            a0, a1 = x0 - 16 + (x1 - x0 + 32) * k / 10, x0 - 16 + (x1 - x0 + 32) * (k + 1) / 10
            b0, b1 = x0 - 22 + (x1 - x0 + 44) * k / 10, x0 - 22 + (x1 - x0 + 44) * (k + 1) / 10
            out.append(f'<path d="M {a0:.1f} 140 L {a1:.1f} 140 L {b1:.1f} 196 L {b0:.1f} 196 Z" fill="#F6C21C"/>')
    for k in range(10):
        b0, b1 = x0 - 22 + (x1 - x0 + 44) * k / 10, x0 - 22 + (x1 - x0 + 44) * (k + 1) / 10
        out.append(f'<path d="M {b0:.1f} 196 Q {(b0 + b1) / 2:.1f} 214 {b1:.1f} 196 Z" fill="{"#F6C21C" if k % 2 == 0 else "#FFF6D8"}" stroke="#3A2418" stroke-width="1.2"/>')
    out.append(f'<path d="M {x0 - 16} 140 L {x1 + 16} 140 L {x1 + 22} 196 L {x0 - 22} 196 Z" fill="{D.lin([(0, "#7A4A0A", 0.25), (1, "#7A4A0A", 0)])}"/>')
    out.append(kid_letters(D, 300, 184, "ICE COLD!", BEBAS, 34, ["#D8302A", "#2E5AA8", "#2E8A4A"], 223, max_w=260, ls=4, wob=4))
    # counter top and things on it
    out.append(painted(D, rect_pts(x0 - 14, ct, x1 + 14, ct + 16, 30, 224, 0.4), WOOD, 224, sdir=(0, 1), sk=0.2, angle=0, n=16, inkw=1.6, hi=0.4))
    out.append(pitcher_glass(D, 196, ct + 2, 90, 120, 225))
    # a sleeve of striped paper cups
    out.append(painted(D, pp([(282, ct - 76), (318, ct - 76), (314, ct), (286, ct)]), ("#FFFFFF", "#F4F0E8", "#B8B0A6"), 230, sdir=(0.9, 0.2), sk=0.15, angle=-90, n=6, inkw=1.4, hi=0.4))
    for k in range(6):
        y_ = ct - 8 - k * 12
        out.append(f'<path d="M {283 + k * 0.4:.1f} {y_} L {317 - k * 0.4:.1f} {y_}" stroke="#D8302A" stroke-width="2.2" opacity="0.75"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(300, ct - 76, 18, 4, 0, 360, 14)[:-1])}" fill="#F4F0E8" stroke="#8A8278" stroke-width="1.2"/>')
    # coin jar
    jx = 390
    out.append(painted(D, pp([(jx - 30, ct - 64), (jx - 32, ct - 30), (jx - 28, ct), (jx + 28, ct), (jx + 32, ct - 30), (jx + 30, ct - 64)]), ("#F4FAFC", "#D8E8EE", "#8AA4B0"), 231, sdir=(0.9, 0.3), sk=0.15, angle=-90, n=6, inkw=1.6, hi=0.5))
    rnd = random.Random(232)
    for _ in range(14):
        x, y = rnd.uniform(jx - 22, jx + 22), rnd.uniform(ct - 26, ct - 6)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="7" ry="3" fill="{rnd.choice(["#C8CED8", "#E8B05A", "#B8C0CA"])}" stroke="#6A7280" stroke-width="0.8"/>')
    out.append(taper([(jx - 22, ct - 56), (jx - 24, ct - 12)], 5, 2, "#FFFFFF", 0.7))
    out.append(painted(D, rect_pts(jx - 26, ct - 52, jx + 26, ct - 34, 8, 233, 0.3), CREAM, 233, sk=0.1, n=3, inkw=1.2, hi=0.3))
    out.append(label(jx, ct - 37, "TIPS", BEBAS, 16, "#2E5AA8", ls=2))
    out.append(lemon(D, 452, ct - 14, 18, 234, rot_=-10))
    out.append(lemon(D, 426, ct - 10, 16, 235, rot_=20))
    # front panel: a cardboard sign, hand lettered
    out.append(painted(D, rect_pts(x0 + 4, ct + 16, x1 - 4, 532, 30, 236, 0.5), WOOD, 236, sdir=(1, 0.2), sk=0.12, angle=0, n=40, inkw=1.8, hi=0.3))
    for y in (ct + 66, ct + 120, ct + 170):
        out.append(pline([(x0 + 6, y), (x1 - 6, y + 1)], "#5E3618", 2, int(y), 0.6, 1))
    card = [(x0 + 26, ct + 30), (x1 - 22, ct + 26), (x1 - 28, 518), (x0 + 30, 520)]
    out.append(painted(D, pp(card), ("#F2D8A8", "#DDB880", "#9A7A4A"), 237, sdir=(0.4, 1), sk=0.08, angle=0, n=20, inkw=1.6, hi=0.3))
    for (tx, ty) in ((x0 + 30, ct + 32), (x1 - 26, ct + 28), (x0 + 34, 516), (x1 - 32, 514)):
        out.append(f'<path d="{hg.org_rect(tx - 12, ty - 5, 24, 10, int(tx), 0.3, 6, 1)}" fill="#F6F0D8" opacity="0.85" transform="rotate(-30 {tx} {ty})"/>')
    out.append(kid_letters(D, 300, ct + 104, "LEMONADE", ANTON, 74, ["#F6C21C", "#D8302A", "#2E8A4A", "#2E5AA8", "#E85A9A"], 238, max_w=320, ls=3))
    out.append(kid_letters(D, 300, ct + 174, "25¢ A CUP", BEBAS, 52, ["#2E5AA8"], 239, max_w=220, ls=3, wob=3))
    return finish_a(D, out, 240)


# ================================================================ 9. sweet tea — on the porch rail at golden hour
def tumbler_tea(D, cx, base, w, h, seed):
    """Tall mason-jar glass of iced tea: amber tea, ice, a lemon wheel on the rim, mint, beads of water."""
    out = [cast(D, cx + 8, base + 2, w * 0.7, 7, strength=0.45, seed=seed)]
    l, r = cx - w / 2, cx + w / 2
    top = base - h
    body = [(l, top), (l - 2, top + h * 0.25), (l + 2, base - 8), (l + 10, base), (r - 10, base), (r - 2, base - 8), (r + 2, top + h * 0.25), (r, top)]
    bd = smooth_closed(body)
    out.append(f'<path d="{bd}" fill="#F4FAFA" opacity="0.4"/>')
    cid = D.clip(f'<path d="{bd}"/>')
    lvl = top + h * 0.1
    inner = [f'<rect x="{l - 10:.1f}" y="{lvl:.1f}" width="{w + 20:.1f}" height="{h:.1f}" fill="{D.lin([(0, "#E8A050"), (0.5, "#B8601E"), (1, "#6A2A08")], 0, 0, 1, 0)}"/>']
    rnd = random.Random(seed)
    for k in range(5):
        ix, iy = cx + rnd.uniform(-w * 0.28, w * 0.28), lvl + 8 + k * h * 0.15
        inner.append(f'<path d="{hg.org_rect(ix - 13, iy - 12, 26, 22, seed + k, 0.8, 6, 5)}" fill="#FFE8C8" opacity="0.4" transform="rotate({rnd.uniform(-30, 30):.0f} {ix:.1f} {iy:.1f})"/>')
        inner.append(f'<path d="M {ix - 8:.1f} {iy - 8:.1f} l 8 -2" stroke="#FFFFFF" stroke-width="2" opacity="0.7"/>')
    inner.append(citrus_slice(D, cx + w * 0.12, lvl + h * 0.48, w * 0.22, seed + 30, ("#FFF6B0", "#FFE24A", "#D8B010"), "#FFFCE8", ("#FFF07A", "#FFD21A", "#C89A0A")))
    # embossed jar ribs
    for k in range(1, 4):
        y = top + h * 0.25 * k
        inner.append(f'<path d="M {l} {y:.1f} Q {cx} {y + 6:.1f} {r} {y:.1f}" stroke="#FFFFFF" stroke-width="1.6" fill="none" opacity="0.3"/>')
    inner.append(shade_over(D, bd, "#2A0A00", 0.3, 0, 0, 1, 0, 0.55))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    for _ in range(26):
        x, y = rnd.uniform(l + 4, r - 4), rnd.uniform(lvl + 6, base - 8)
        rr = rnd.uniform(1, 2.4)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="#FFFFFF" opacity="0.55"/><circle cx="{x + rr * 0.3:.1f}" cy="{y + rr * 0.3:.1f}" r="{rr * 0.5:.1f}" fill="#3A1A0A" opacity="0.2"/>')
    out.append(taper([(l + 8, top + 14), (l + 6, top + h * 0.5), (l + 10, base - 16)], 6, 2, "#FFFFFF", 0.7))
    out.append(ink(bd, "#8A6A50", 1.6, seed + 2, 2, 0.7))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, w / 2, w * 0.12, 0, 360, 20)[:-1])}" fill="none" stroke="#8A6A50" stroke-width="1.4" opacity="0.8"/>')
    # lemon wheel perched on the rim and a mint sprig
    out.append(citrus_slice(D, r - 4, top + 4, w * 0.3, seed + 31, ("#FFF6B0", "#FFE24A", "#D8B010"), "#FFFCE8", ("#FFF07A", "#FFD21A", "#C89A0A")))
    for k, (dx, a) in enumerate(((-10, -110), (-2, -80), (-18, -140), (6, -60))):
        out.append(leaf_simple(D, cx + dx, top - 2, 26, 9, a, ("#A8E08A", "#4AA040", "#1E5A1E"), seed + 40 + k, inkw=1))
    out.append(straw(D, cx - 6, top + 40, cx - 26, top - 60, 9, seed + 50, cols=("#2E5AA8", "#FFFFFF")))
    return "".join(out)


def baluster_rail(D, x0, x1, top, bot, seed, step=34, pal=WHITE):
    out = []
    x = x0 + 8
    k = 0
    while x < x1:
        prof = [(x - 6, bot), (x - 7, bot - 12), (x - 4, bot - 22), (x - 9, (top + bot) / 2), (x - 4, top + 22), (x - 6, top + 14), (x + 6, top + 14), (x + 4, top + 22),
                (x + 9, (top + bot) / 2), (x + 4, bot - 22), (x + 7, bot - 12), (x + 6, bot)]
        out.append(painted(D, prof, pal, seed + k, sdir=(1, 0.1), sk=0.22, angle=-90, n=4, inkw=1.2, inkop=0.6, hi=0.4))
        x += step
        k += 1
    out.append(painted(D, rect_pts(x0 - 10, bot - 4, x1 + 10, bot + 8, 30, seed + 90, 0.3), pal, seed + 90, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.3))
    return "".join(out)


def rocking_chair(D, x, base, s, seed, pal=WOOD, flip=1):
    def P(u, v):
        return (x + u * s * flip, base + v * s)
    out = [cast(D, x, base, s * 0.5, s * 0.05, strength=0.35, seed=seed)]
    out.append(ink(smooth_open([P(-0.45, -0.02), P(-0.1, 0.03), P(0.3, 0.02), P(0.5, -0.06)]), pal[2], max(3, s * 0.035), seed, 1, 1))
    for u0, u1 in ((-0.3, -0.34), (0.22, 0.24)):
        out.append(ink(smooth_open([P(u0, 0.0), P(u1, -0.42)]), pal[1], max(3, s * 0.03), seed + 1, 1, 1))
    out.append(ink(smooth_open([P(-0.36, -0.42), P(0.28, -0.44)]), pal[1], max(4, s * 0.04), seed + 2, 1, 1))
    out.append(ink(smooth_open([P(0.24, -0.44), P(0.3, -0.75), P(0.36, -1.0)]), pal[1], max(3, s * 0.032), seed + 3, 1, 1))
    out.append(ink(smooth_open([P(0.08, -0.44), P(0.14, -0.75), P(0.2, -0.98)]), pal[1], max(3, s * 0.03), seed + 4, 1, 1))
    for k in range(4):
        v = -0.55 - k * 0.12
        out.append(ink(smooth_open([P(0.12 + k * 0.012, v), P(0.3 + k * 0.012, v - 0.01)]), pal[0], max(2, s * 0.02), seed + 5 + k, 1, 1))
    out.append(ink(smooth_open([P(-0.36, -0.6), P(0.0, -0.62), P(0.26, -0.66)]), pal[2], max(3, s * 0.03), seed + 9, 1, 1))
    return "".join(out)


@design("sweet-tea")
def sweet_tea():
    D = Doc2("us-st")
    out = [sky(D, [(0, "#F2A86A"), (0.5, "#FFD08A"), (1, "#FFEAC0")], 251, 600, ["#FFC890", "#FFE8B8"], 40)]
    out.append(soft_glow(D, 330, 330, 260, "#FFF2C8", 0.7))
    # live oak dripping with Spanish moss beyond the yard
    out.append(hill(D, ridge([(-20, 372), (300, 360), (620, 374)], 252, 3), 600, ("#C8C070", "#8A9A4A", "#4A5A2A"), 252, inkw=0))
    out.append(taper([(440, 380), (446, 320), (420, 270)], 26, 12, "#5A4A3A"))
    out.append(taper([(446, 316), (530, 280), (610, 274)], 14, 6, "#5A4A3A"))
    out.append(dab_crown(D, 470, 266, 170, 52, [SAGE, ("#A8B880", "#6A7A4A", "#3A4A2A")], 253, n=140, size=(8, 14), inkw=0))
    rnd = random.Random(254)
    for _ in range(20):
        x = rnd.uniform(320, 610)
        y = rnd.uniform(276, 300)
        out.append(taper([(x, y), (x + rnd.uniform(-4, 4), y + 24), (x + rnd.uniform(-6, 6), y + rnd.uniform(40, 64))], 5, 1, "#B8B8A0", 0.75))
    out.append(dab_crown(D, 60, 350, 90, 34, [SAGE], 2531, n=50, size=(7, 12), inkw=0))
    # porch: haint-blue ceiling, white posts, a hanging fern
    out.append(f'<path d="M -10 -10 L 610 -10 L 610 40 L -10 52 Z" fill="#9ED8D8"/>')
    for x in range(-10, 620, 30):
        out.append(f'<path d="M {x} -10 L {x} 46" stroke="#7AB8B8" stroke-width="2" opacity="0.6"/>')
    out.append(painted(D, pp([(-10, 40), (610, 30), (610, 52), (-10, 64)]), WHITE, 255, sk=0.15, n=12, inkw=1.6, hi=0.3))
    for px in (40, 560):
        out.append(painted(D, rect_pts(px - 20, 50, px + 20, 600, 40, px, 0.4), WHITE, px, sdir=(1, 0.1), sk=0.2, angle=-90, n=20, inkw=1.8, hi=0.4))
    from brasil_painted import samambaia
    out.append(pline([(100, 56), (100, 226)], "#6A4A2A", 1.6, 257, 0.9, 1))
    out.append(samambaia(D, 100, 258, 70, 256))
    # fireflies starting to blink in the yard
    for _ in range(10):
        x, y = rnd.uniform(80, 520), rnd.uniform(300, 380)
        out.append(D.glow(x, y, 10, "#FFF6A0", 0.8) + f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.7" fill="#FFFCE0"/>')
    # the rail and the tea on it
    out.append(baluster_rail(D, 58, 542, 452, 610, 258, step=36))
    out.append(painted(D, rect_pts(36, 428, 564, 452, 40, 259, 0.4), WHITE, 259, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.8, hi=0.5))
    out.append(cast(D, 310, 430, 230, 7, strength=0.35, seed=260))
    out.append(pitcher_glass(D, 222, 430, 124, 186, 261, drink=("#F2B06A", "#C0682A", "#6A2A08"), lemons=True))
    out.append(tumbler_tea(D, 384, 432, 84, 160, 262))
    out.append(lemon(D, 482, 414, 20, 263, rot_=-14))
    out.append(citrus_slice(D, 514, 424, 16, 264, ("#FFF6B0", "#FFE24A", "#D8B010"), "#FFFCE8", ("#FFF07A", "#FFD21A", "#C89A0A")))
    # lettering
    out.append(letters(D, 320, 146, "Sweet Tea", SERIF_IT, 100, "#7A2E14", ["#9A4A22", "#5A1E08", "#B8602E"], 265, max_w=380,
                       shadow="#FFF6E0", soff=(0.02, 0.03), angle=-40, hi="#F8C090"))
    out.append(ruled(320, 192, "ON THE FRONT PORCH", "#7A2E14", font=JOS, size=21, ls=5, line_w=24, gap=12, max_w=330))
    return finish_a(D, out, 266)


# ================================================================ 10. fourth of july — backyard cookout under the fireworks
def watermelon_wedge(D, cx, cy, s, seed, rot_=0, bite=False):
    """Classic picnic wedge: a slice cut from the round, tip at (cx, cy), rind arc at distance s (rot_=180 points it up)."""
    R = s
    tip = (cx, cy)

    def arcpts(rr):
        return [(cx + rr * math.sin(math.radians(t)), cy + rr * math.cos(math.radians(t))) for t in range(-32, 33, 4)]
    o = []
    rind = [tip] + arcpts(R)
    white = [tip] + arcpts(R * 0.9)
    flesh = [tip] + arcpts(R * 0.85)
    rind = rot(rind, cx, cy, rot_)
    white = rot(white, cx, cy, rot_)
    flesh = rot(flesh, cx, cy, rot_)
    o.append(painted(D, rind, ("#8ACB6A", "#2E7A3A", "#14401E"), seed, sk=0.1, n=6, inkw=1.6, hi=0.3))
    o.append(f'<path d="{pd(white)}" fill="#F0F6D8"/>')
    o.append(painted(D, flesh, ("#FF9A9A", "#E8303A", "#9A0E1A"), seed + 1, sdir=(0.5, 0.8), sk=0.12, angle=-90 + rot_, n=14, inkw=0, hi=0.35))
    rnd = random.Random(seed)
    for _ in range(int(s * 0.12)):
        t, rr = rnd.uniform(-24, 24), rnd.uniform(0.35, 0.75) * R
        x, y = rot([(cx + rr * math.sin(math.radians(t)), cy + rr * math.cos(math.radians(t)))], cx, cy, rot_)[0]
        o.append(f'<path d="{blob(x, y, 1.8, 3.2, rnd.randint(0, 999), 0.1, 8, rot_ - t)}" fill="#1A1010"/>')
    o.append(ink(pd(rind), INK, 1.6, seed + 2, 1, 0.6))
    return "".join(o)


def kettle_grill(D, cx, base, w, seed):
    out = [cast(D, cx, base, w * 0.7, 8, strength=0.45, seed=seed)]
    top = base - w * 1.1
    for sg in (-1, 0.3, 1):
        out.append(taper([(cx + sg * w * 0.08, top + w * 0.5), (cx + sg * w * 0.42, base)], 5, 4, "#2A2830"))
    out.append(f'<circle cx="{cx + w * 0.42:.1f}" cy="{base - 6:.1f}" r="8" fill="#1A1A20"/>')
    bowl = [(cx - w / 2, top + w * 0.08)] + [(cx + w / 2 * math.cos(math.radians(a)), top + w * 0.08 + w * 0.42 * math.sin(math.radians(a))) for a in range(0, 181, 15)]
    bowl = bowl[1:] + [bowl[0]]
    out.append(painted(D, bowl, ("#6A6870", "#2E2D36", "#121116"), seed, sdir=(0.6, 0.7), sk=0.15, angle=0, n=12, inkw=1.6, hi=0.4))
    # glowing coals and the grate, with patties
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top + w * 0.08, w / 2, w * 0.12, 0, 360, 24)[:-1])}" fill="#1A1014"/>')
    out.append(D.glow(cx, top + w * 0.08, w * 0.6, "#FF7A2A", 0.6))
    for k in range(-3, 4):
        out.append(f'<path d="M {cx + k * w * 0.12:.1f} {top + w * 0.08 - w * 0.1:.1f} L {cx + k * w * 0.12:.1f} {top + w * 0.08 + w * 0.1:.1f}" stroke="#8A8890" stroke-width="1.4" opacity="0.8"/>')
    for k, dx in enumerate((-0.22, 0.02, 0.24)):
        px = cx + dx * w
        out.append(f'<path d="{blob(px, top + w * 0.06, w * 0.1, w * 0.045, seed + k, 0.1, 10)}" fill="#5A2E1A" stroke="#2A140A" stroke-width="1"/>')
        out.append(f'<path d="M {px - w * 0.06:.1f} {top + w * 0.05:.1f} l {w * 0.12:.1f} 0" stroke="#2A140A" stroke-width="1.4" opacity="0.7"/>')
    # lid propped on the side
    lid = [(cx + w * 0.5, top + w * 0.06)] + [(cx + w * 0.5 + w * 0.14 * math.cos(math.radians(a)), top - w * 0.4 + w * 0.46 * math.sin(math.radians(a))) for a in range(-90, 91, 15)]
    out.append(painted(D, lid, ("#6A6870", "#2E2D36", "#121116"), seed + 5, sk=0.15, n=6, inkw=1.4, hi=0.4))
    return "".join(out)


@design("fourth-of-july")
def fourth_of_july():
    D = Doc2("us-fj")
    out = [sky(D, [(0, "#0A1030"), (0.55, "#1E2A5A"), (1, "#4A3A6A")], 271, 470, ["#24306A", "#0A0E28"], 60)]
    out.append(stars_field(272, 60, (0, 0, 600, 300), avoid=((90, 230, 510, 330),)))
    # fireworks over the yard
    out.append(hg.firework(D, 148, 128, 88, "#FF4A4A", 273, rays=26, col2="#FFD0C8"))
    out.append(hg.firework(D, 462, 112, 74, "#FFFFFF", 274, rays=22, col2="#FFE08A"))
    out.append(hg.firework(D, 316, 70, 36, "#5A8AFF", 275, rays=16, col2="#C8D8FF"))
    out.append(hg.firework(D, 548, 230, 34, "#FFE08A", 276, rays=14))
    for x, y0, y1 in ((148, 330, 214), (462, 330, 186)):
        out.append(taper([(x, y1 + 30), (x + 2, y0)], 1, 3, "#FFE8C0", 0.35))
    # the backyard: tree line, a house with lit windows and its flag, string lights
    out.append(hill(D, ridge([(-20, 392), (300, 384), (620, 394)], 277, 3), 600, ("#2E4A3A", "#1E3428", "#0E1E16"), 277, inkw=0))
    rr = random.Random(278)
    for k in range(16):
        x = rr.uniform(-10, 400)
        out.append(dab_crown(D, x, 372, rr.uniform(24, 34), rr.uniform(20, 30), [("#2E4A3A", "#1E3428", "#0E1E16")], 900 + k, n=12, size=(8, 12), inkw=0, base=False))
    out.append(painted(D, rect_pts(430, 322, 610, 400, 30, 278, 0.4), ("#4A5A7A", "#2E3A58", "#18203A"), 278, sk=0.1, n=10, inkw=1.2, hi=0.2))
    out.append(painted(D, pp([(414, 326), (526, 262), (630, 326)]), ("#3A4060", "#24283E", "#121424"), 279, sk=0.1, n=6, inkw=1.2, hi=0.2))
    for wx in (456, 540):
        out.append(D.glow(wx + 15, 356, 44, "#FFC860", 0.45))
        out.append(f'<path d="{hg.org_rect(wx, 340, 30, 34, wx, 0.3, 8, 2)}" fill="#FFD27A"/>')
        out.append(f'<path d="M {wx + 15} 340 L {wx + 15} 374 M {wx} 357 L {wx + 30} 357" stroke="#2E3A58" stroke-width="2.4"/>')
    out.append(bulbs_row(D, [(16 + i * 44, 384 + 7 * math.sin(i * 1.1)) for i in range(10)], 281, col="#FFE6A0", r=2.6))
    # the picnic table, red check, laden
    tbl = [(-20, 430), (620, 422), (620, 640), (-20, 640)]
    out.append(cloth(D, tbl, "#D8302A", 282, cell=20, rot_=0, light=(0, 0, 0, 1), folds=[((80, 450), (90, 540), (70, 620)), ((540, 440), (530, 540), (550, 620))]))
    out.append(f'<rect y="420" width="600" height="190" fill="{D.lin([(0, "#1E2A5A", 0.3), (1, "#0A0E28", 0.12)])}"/>')
    out.append(f'<ellipse cx="300" cy="500" rx="300" ry="90" fill="{D.rad([(0, "#FFE0A0", 0.25), (1, "#FFE0A0", 0)])}"/>')
    # the grill, smoke curling up
    out.append(kettle_grill(D, 516, 486, 96, 283))
    for k in range(3):
        sx_ = 496 + k * 16
        out.append(taper([(sx_, 420), (sx_ + 12, 384), (sx_ - 6, 350), (sx_ + 6, 318)], 9, 2, "#C8C8D8", 0.22))
    # a platter of watermelon wedges, standing tip-up
    out.append(cast(D, 214, 528, 160, 16, strength=0.5, seed=284))
    out.append(painted(D, ell_pts(206, 506, 150, 38, 0, 360, 36)[:-1], ("#FFFFFF", "#E8EEF2", "#9AA8B4"), 285, sdir=(0.3, 1), sk=0.12, angle=0, n=12, inkw=1.6, hi=0.4))
    out.append(f'<path d="{blob(206, 504, 118, 26, 286, 0.02, 24)}" fill="#C8D0D8" opacity="0.4"/>')
    for k, (x, a) in enumerate(((104, -14), (160, -6), (214, 2), (268, 10), (320, 16))):
        out.append(watermelon_wedge(D, x, 418 + abs(k - 2) * 4, 88, 287 + k, rot_=a))
    # a mason jar of little flags and a sparkler
    jx, jb = 404, 532
    out.append(cast(D, jx + 6, jb + 2, 36, 6, strength=0.5, seed=292))
    spx, spy = jx + 34, jb - 168
    out.append(f'<path d="M {jx + 8} {jb - 70} L {spx} {spy}" stroke="#8A8890" stroke-width="2.6"/>')
    for k, (dx, a) in enumerate(((-12, -14), (6, 6))):
        sx_, sy_ = jx + dx, jb - 64
        tx, ty = sx_ + math.sin(math.radians(a)) * 92, sy_ - math.cos(math.radians(a)) * 92
        out.append(f'<path d="M {sx_} {sy_} L {tx:.1f} {ty:.1f}" stroke="#E8D8B8" stroke-width="2.4"/>')
        out.append(us_flag(D, tx, ty, 54, 34, 293 + k, wave=0.1, flip=1 if k else -1))
    out.append(D.glow(spx, spy, 80, "#FFE8A0", 0.75))
    rnd = random.Random(295)
    for k in range(30):
        a = rnd.uniform(0, 6.28)
        L = rnd.uniform(10, 38)
        out.append(f'<path d="M {spx:.1f} {spy:.1f} l {math.cos(a) * L:.1f} {math.sin(a) * L:.1f}" stroke="#FFF2C0" stroke-width="1.5" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
        out.append(f'<circle cx="{spx + math.cos(a) * L:.1f}" cy="{spy + math.sin(a) * L:.1f}" r="1.5" fill="#FFFFFF"/>')
    jar = rect_pts(jx - 28, jb - 72, jx + 28, jb, 12, 296, 0.4)
    out.append(painted(D, jar, ("#F4FAFC", "#B8D0DA", "#5A7A8A"), 296, sdir=(0.9, 0.3), sk=0.15, angle=-90, n=8, inkw=1.6, hi=0.5))
    out.append(painted(D, rect_pts(jx - 30, jb - 80, jx + 30, jb - 68, 10, 297, 0.3), CHROME, 297, sk=0.15, n=4, inkw=1.4, hi=0.5))
    out.append(taper([(jx - 20, jb - 62), (jx - 22, jb - 10)], 5, 2, "#FFFFFF", 0.7))
    # lettering
    out.append(letters(D, 300, 300, "Fourth of July", SERIF_IT, 84, "#FFF2D8", ["#FFFFFF", "#FFE2C0"], 298, max_w=450,
                       shadow="#7A1414", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 340, "HAPPY BIRTHDAY, AMERICA", "#FFD27A", font=JOS, size=19, ls=5, line_w=22, gap=10, max_w=360))
    return finish_a(D, out, 299)


# ================================================================ 11. small town, big heart — Main Street with the barber pole
def pickup50(D, x, base, L, seed, body=BARN, flip=1, lights=False, shadow=True, snow=False):
    """A generic 1950s step-side pickup in side view (no badges). (x, base) = centre on the ground."""
    def P(u, v):
        return (x + u * L * flip, base + v * L)

    def Q(pts):
        return [P(u, v) for u, v in pts]
    out = []
    if shadow:
        out.append(cast(D, x, base + 1, L * 0.55, L * 0.035, strength=0.55, seed=seed))
    # bed box and rear step fender
    out.append(painted(D, pp(Q([(-0.5, -0.27), (-0.06, -0.27), (-0.06, -0.1), (-0.5, -0.1)]), 8, seed), body, seed, sdir=(0, 1), sk=0.12, angle=0, n=14, inkw=1.6, hi=0.45))
    out.append(pline(Q([(-0.49, -0.255), (-0.07, -0.255)]), lt(body[0], 0.4), 2, seed, 0.8, 1))
    for k in range(4):
        u = -0.46 + k * 0.12
        out.append(pline(Q([(u, -0.25), (u, -0.12)]), body[2], 1.2, seed + k, 0.35, 1))
    rf = Q([(-0.44, -0.1), (-0.42, -0.17), (-0.36, -0.205), (-0.26, -0.205), (-0.2, -0.17), (-0.18, -0.1)])
    out.append(painted(D, rf, (lt(body[1], 0.2), dk(body[1], 0.15), dk(body[2], 0.3)), seed + 1, sdir=(0, 1), sk=0.15, angle=0, n=8, inkw=1.6, hi=0.4))
    # cab
    cab = Q([(-0.08, -0.1), (-0.08, -0.43), (-0.04, -0.465), (0.1, -0.465), (0.15, -0.43), (0.2, -0.3), (0.2, -0.1)])
    out.append(painted(D, pp(cab, 8, seed + 2), body, seed + 2, sdir=(0, 1), sk=0.12, angle=-90, n=12, inkw=1.8, hi=0.5))
    win = Q([(-0.04, -0.29), (-0.04, -0.42), (0.09, -0.42), (0.13, -0.38), (0.165, -0.29)])
    g = D.lin([(0, "#E8F4F8"), (0.45, "#8AB0C8"), (1, "#3A5068")])
    out.append(f'<path d="{pd(win)}" fill="{g}"/>')
    out.append(ink(pd(win), "#E8ECF0", 1.6, seed, 1, 0.9))
    out.append(taper([P(0.0, -0.4), P(0.03, -0.31)], 2, 1, "#FFFFFF", 0.7))
    out.append(pline(Q([(0.09, -0.28), (0.09, -0.12)]), body[2], 1.2, seed, 0.6, 1))
    hx, hy = P(0.06, -0.25)
    out.append(f'<path d="M {hx:.1f} {hy:.1f} l {-6 * flip:.1f} 0" stroke="#F4F6FA" stroke-width="2.2" stroke-linecap="round"/>')
    # hood and the big rounded front fender
    hood = Q([(0.18, -0.3), (0.42, -0.29), (0.49, -0.25), (0.5, -0.18), (0.5, -0.1), (0.2, -0.1)])
    out.append(painted(D, pp(hood, 8, seed + 3), body, seed + 3, sdir=(0, 1), sk=0.12, angle=0, n=10, inkw=1.6, hi=0.5))
    ff = Q([(0.2, -0.1), (0.22, -0.18), (0.3, -0.23), (0.42, -0.23), (0.5, -0.18), (0.53, -0.1)])
    out.append(painted(D, ff, (lt(body[1], 0.2), dk(body[1], 0.12), dk(body[2], 0.3)), seed + 4, sdir=(0, 1), sk=0.15, angle=0, n=8, inkw=1.6, hi=0.5))
    # running board, chrome bits
    out.append(painted(D, pp(Q([(-0.2, -0.105), (0.22, -0.105), (0.22, -0.085), (-0.2, -0.085)]), 8, seed + 5), IRON, seed + 5, sk=0.1, n=4, inkw=1, hi=0.3))
    out.append(painted(D, pp(Q([(0.48, -0.12), (0.535, -0.12), (0.535, -0.085), (0.48, -0.085)]), 6, seed + 6), CHROME, seed + 6, sk=0.1, n=2, inkw=1, hi=0.5))
    out.append(painted(D, pp(Q([(-0.53, -0.13), (-0.48, -0.13), (-0.48, -0.1), (-0.53, -0.1)]), 6, seed + 7), CHROME, seed + 7, sk=0.1, n=2, inkw=1, hi=0.5))
    fx, fy = P(0.47, -0.2)
    out.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{L * 0.022:.1f}" fill="#FFF6C8" stroke="#C8D0DA" stroke-width="2"/>')
    if lights:
        out.append(D.glow(fx + 14 * flip, fy, L * 0.3, "#FFE8A0", 0.55))
    tx, ty = P(-0.5, -0.2)
    out.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="{L * 0.012:.1f}" fill="#E8302A"/>')
    for u in (-0.31, 0.36):
        wx, wy = P(u, -0.065)
        r = L * 0.065
        out.append(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="{r:.1f}" fill="#1C1A20"/>')
        out.append(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="{r * 0.55:.1f}" fill="{body[1]}"/>')
        out.append(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="{r * 0.3:.1f}" fill="{D.rad([(0, "#FFFFFF"), (0.6, "#C8CED8"), (1, "#6A7280")], 0.4, 0.35, 0.7)}"/>')
        out.append(ink(f"M {wx - r:.1f} {wy:.1f} a {r:.1f} {r:.1f} 0 1 0 {2 * r:.1f} 0 a {r:.1f} {r:.1f} 0 1 0 {-2 * r:.1f} 0", "#0A0A0E", 1.4, seed, 1, 0.7))
    if snow:
        for pts in ([(-0.08, -0.465), (0.1, -0.47), (0.15, -0.43)], [(0.18, -0.3), (0.42, -0.295), (0.49, -0.255)]):
            out.append(taper(Q(pts), L * 0.018, L * 0.01, "#FFFFFF", 0.95))
    return "".join(out)


def barber_pole(D, cx, top, h, w, seed):
    out = [D.glow(cx, top + h / 2, h * 0.8, "#FFF6E0", 0.35)]
    out.append(painted(D, rect_pts(cx - w * 0.75, top - 16, cx + w * 0.75, top + 2, 6, seed, 0.3), CHROME, seed, sk=0.15, n=4, inkw=1.4, hi=0.5))
    out.append(f'<path d="{blob(cx, top - 18, w * 0.5, w * 0.36, seed + 1, 0.04, 12)}" fill="{D.rad([(0, "#FFFFFF"), (0.6, "#C8D0DA"), (1, "#6A7280")], 0.4, 0.35, 0.7)}" stroke="#3A3A44" stroke-width="1.2"/>')
    body = f"M {cx - w / 2:.1f} {top:.1f} L {cx + w / 2:.1f} {top:.1f} L {cx + w / 2:.1f} {top + h:.1f} L {cx - w / 2:.1f} {top + h:.1f} Z"
    out.append(f'<path d="{body}" fill="#FFFFFF"/>')
    cid = D.clip(f'<path d="{body}"/>')
    st = []
    k = 0
    y = top - w * 2
    cols = ["#D8302A", "#FFFFFF", "#22386A", "#FFFFFF"]
    while y < top + h + w:
        c = cols[k % 4]
        if c != "#FFFFFF":
            st.append(f'<path d="M {cx - w:.1f} {y:.1f} L {cx + w:.1f} {y - w * 0.9:.1f} L {cx + w:.1f} {y - w * 0.9 + w * 0.42:.1f} L {cx - w:.1f} {y + w * 0.42:.1f} Z" fill="{c}"/>')
        y += w * 0.42
        k += 1
    st.append(f'<rect x="{cx - w / 2:.1f}" y="{top}" width="{w:.1f}" height="{h}" fill="{D.lin([(0, "#FFFFFF", 0.5), (0.3, "#FFFFFF", 0), (0.7, "#1A0A10", 0), (1, "#1A0A10", 0.45)], 0, 0, 1, 0)}"/>')
    out.append(f'<g {cid}>{"".join(st)}</g>')
    out.append(taper([(cx - w * 0.28, top + 6), (cx - w * 0.28, top + h - 6)], 3, 3, "#FFFFFF", 0.7))
    out.append(ink(body, "#3A3A44", 1.4, seed, 1, 0.8))
    out.append(painted(D, rect_pts(cx - w * 0.75, top + h - 2, cx + w * 0.75, top + h + 14, 6, seed + 2, 0.3), CHROME, seed + 2, sk=0.15, n=4, inkw=1.4, hi=0.5))
    out.append(f'<path d="{blob(cx, top + h + 18, w * 0.3, w * 0.26, seed + 3, 0.04, 10)}" fill="#C8D0DA" stroke="#3A3A44" stroke-width="1.2"/>')
    return "".join(out)


def storefront(D, x0, x1, top, base, seed, wall, sign, font, signc, awning, trim="#FFF6E8", brick=True, arch=False, lit=0.6):
    """Two-storey Main Street building: brick or painted front, cornice, upper windows, a sign band,
    a striped awning over a big shop window and a door."""
    rnd = random.Random(seed)
    w = x1 - x0
    out = [painted(D, rect_pts(x0, top, x1, base, 24, seed, 0.4), wall, seed, sdir=(0.6, 0.6), sk=0.08, angle=-90, n=int(w * (base - top) / 300), inkw=1.6, hi=0.25)]
    if brick:
        cid = D.clip(f'<path d="M {x0} {top} L {x1} {top} L {x1} {base} L {x0} {base} Z"/>')
        b = []
        for j, y in enumerate(range(int(top) + 8, int(base), 8)):
            b.append(f'<path d="M {x0} {y} L {x1} {y}" stroke="{wall[2]}" stroke-width="1" opacity="0.35"/>')
            for xx in range(int(x0) + (0 if j % 2 else 9), int(x1), 18):
                b.append(f'<path d="M {xx} {y - 8} L {xx} {y}" stroke="{wall[2]}" stroke-width="1" opacity="0.3"/>')
            if rnd.random() < 0.5:
                bx = rnd.uniform(x0, x1 - 18)
                b.append(f'<rect x="{bx:.1f}" y="{y - 8}" width="17" height="7" fill="{rnd.choice([wall[0], wall[2]])}" opacity="0.3"/>')
        out.append(f'<g {cid}>{"".join(b)}</g>')
    # cornice
    out.append(painted(D, rect_pts(x0 - 4, top - 8, x1 + 4, top + 12, 20, seed + 1, 0.3), (lt(trim, 0.2), trim, dk(trim, 0.35)), seed + 1, sdir=(0, 1), sk=0.2, angle=0, n=8, inkw=1.4, hi=0.3))
    for xx in range(int(x0) + 4, int(x1) - 2, 10):
        out.append(f'<rect x="{xx}" y="{top + 12}" width="5" height="6" fill="{trim}" stroke="{dk(trim, 0.4)}" stroke-width="0.8"/>')
    # upper windows
    nwin = 2 if w < 130 else 3
    ww = w * 0.18
    for k in range(nwin):
        cx = x0 + w * (k + 0.5) / nwin
        wy = top + 30
        wh = (base - top) * 0.26
        frame = [(cx - ww / 2 - 4, wy - 4), (cx + ww / 2 + 4, wy - 4), (cx + ww / 2 + 4, wy + wh + 4), (cx - ww / 2 - 4, wy + wh + 4)]
        out.append(f'<path d="{hg.org_poly(frame, seed + k, 0.4, 8, 2)}" fill="{trim}"/>')
        glass = "#FFD880" if rnd.random() < lit else "#5A7898"
        g = D.lin([(0, lt(glass, 0.3)), (1, dk(glass, 0.25))])
        if arch:
            gp = f"M {cx - ww / 2:.1f} {wy + wh:.1f} L {cx - ww / 2:.1f} {wy + ww / 2:.1f} A {ww / 2:.1f} {ww / 2:.1f} 0 0 1 {cx + ww / 2:.1f} {wy + ww / 2:.1f} L {cx + ww / 2:.1f} {wy + wh:.1f} Z"
        else:
            gp = f"M {cx - ww / 2:.1f} {wy:.1f} L {cx + ww / 2:.1f} {wy:.1f} L {cx + ww / 2:.1f} {wy + wh:.1f} L {cx - ww / 2:.1f} {wy + wh:.1f} Z"
        out.append(f'<path d="{gp}" fill="{g}"/>')
        out.append(f'<path d="M {cx:.1f} {wy + 2:.1f} L {cx:.1f} {wy + wh:.1f} M {cx - ww / 2:.1f} {wy + wh * 0.5:.1f} L {cx + ww / 2:.1f} {wy + wh * 0.5:.1f}" stroke="{trim}" stroke-width="2"/>')
        out.append(taper([(cx - ww / 2 + 4, wy + wh - 6), (cx - 4, wy + 8)], 3, 1, "#FFFFFF", 0.4))
        out.append(f'<rect x="{cx - ww / 2 - 6:.1f}" y="{wy + wh + 3:.1f}" width="{ww + 12:.1f}" height="4" fill="{dk(trim, 0.2)}"/>')
    # sign band
    sy = top + (base - top) * 0.48
    out.append(painted(D, rect_pts(x0 + 8, sy, x1 - 8, sy + 26, 14, seed + 5, 0.3), (lt(signc[1], 0.2), signc[1], signc[2]), seed + 5, sk=0.12, n=6, inkw=1.4, hi=0.3))
    out.append(label((x0 + x1) / 2, sy + 20, sign, font, 20, signc[0], ls=1, max_w=w - 26))
    # awning
    ay0, ay1 = sy + 32, sy + 62
    aw = [(x0 + 4, ay0), (x1 - 4, ay0), (x1 + 4, ay1), (x0 - 4, ay1)]
    out.append(painted(D, pp(aw, 10, seed + 6), ("#FFFDF4", "#F4EAD8", "#C8B898"), seed + 6, sk=0.08, n=6, inkw=1.4, hi=0.2))
    n = max(4, int(w / 18))
    for k in range(n):
        if k % 2 == 0:
            a0, a1 = x0 + 4 + (w - 8) * k / n, x0 + 4 + (w - 8) * (k + 1) / n
            b0, b1 = x0 - 4 + (w + 8) * k / n, x0 - 4 + (w + 8) * (k + 1) / n
            out.append(f'<path d="M {a0:.1f} {ay0} L {a1:.1f} {ay0} L {b1:.1f} {ay1} L {b0:.1f} {ay1} Z" fill="{awning}"/>')
    for k in range(n):
        b0, b1 = x0 - 4 + (w + 8) * k / n, x0 - 4 + (w + 8) * (k + 1) / n
        out.append(f'<path d="M {b0:.1f} {ay1} Q {(b0 + b1) / 2:.1f} {ay1 + 9} {b1:.1f} {ay1} Z" fill="{awning if k % 2 == 0 else "#FFFDF4"}" stroke="{INK}" stroke-width="1"/>')
    out.append(f'<path d="M {x0 + 4} {ay0} L {x1 - 4} {ay0} L {x1 + 4} {ay1} L {x0 - 4} {ay1} Z" fill="{D.lin([(0, "#3A1A0A", 0.25), (1, "#3A1A0A", 0)])}"/>')
    # shop window and door under the awning (in shade)
    gy0 = ay1 + 6
    dw = w * 0.2
    dx = x1 - dw - 12 if seed % 2 else x0 + 12
    sx0, sx1 = (x0 + 12, dx - 8) if seed % 2 else (dx + dw + 8, x1 - 12)
    g = D.lin([(0, "#FFE8B0"), (1, "#E8A860")])
    out.append(f'<path d="{hg.org_rect(sx0, gy0, sx1 - sx0, base - gy0 - 14, seed + 7, 0.3, 10, 2)}" fill="{g}"/>')
    out.append(f'<path d="{hg.org_rect(sx0, base - 14, sx1 - sx0, 14, seed + 8, 0.3, 10, 1)}" fill="{trim}"/>')
    for k in range(5):
        px = sx0 + 8 + k * (sx1 - sx0 - 16) / 4
        out.append(f'<path d="{blob(px, base - 22, 6, 7, seed + 20 + k, 0.1, 8)}" fill="{rnd.choice(["#D8302A", "#F6C21C", "#2E8A4A", "#8A5A2A", "#2E5AA8"])}" opacity="0.85"/>')
    out.append(taper([(sx0 + 6, base - 20), (sx0 + 30, gy0 + 6)], 4, 1, "#FFFFFF", 0.5))
    out.append(ink(hg.org_rect(sx0, gy0, sx1 - sx0, base - gy0 - 14, seed + 7, 0.3, 10, 2), INK, 1.6, seed, 1, 0.8))
    out.append(painted(D, rect_pts(dx, gy0, dx + dw, base, 8, seed + 9, 0.3), (lt(awning, 0.3), dk(awning, 0.1), dk(awning, 0.45)), seed + 9, sk=0.12, n=4, inkw=1.4, hi=0.3))
    out.append(f'<path d="{hg.org_rect(dx + 5, gy0 + 6, dw - 10, (base - gy0) * 0.45, seed + 10, 0.3, 8, 1)}" fill="#FFE8B0"/>')
    out.append(f'<circle cx="{dx + dw - 6:.1f}" cy="{(gy0 + base) / 2 + 8:.1f}" r="2" fill="#F6C21C"/>')
    return "".join(out)


def street_lamp(D, x, base, h, seed, flag=True, basket=True):
    out = [taper([(x, base), (x, base - h)], 7, 5, "#1E2A3A")]
    out.append(painted(D, rect_pts(x - 8, base - 10, x + 8, base, 6, seed, 0.3), ("#4A5A6A", "#1E2A3A", "#0A1018"), seed, sk=0.1, n=2, inkw=1, hi=0.3))
    out.append(D.glow(x, base - h - 12, 40, "#FFE8A0", 0.55))
    out.append(f'<path d="M {x - 10} {base - h} L {x + 10} {base - h} L {x + 7} {base - h - 22} L {x - 7} {base - h - 22} Z" fill="#FFF2C0" stroke="#1E2A3A" stroke-width="2"/>')
    out.append(f'<path d="M {x - 12} {base - h - 22} L {x + 12} {base - h - 22} L {x} {base - h - 32} Z" fill="#1E2A3A"/>')
    if basket:
        out.append(f'<path d="M {x - 30} {base - h * 0.55} L {x} {base - h * 0.55}" stroke="#1E2A3A" stroke-width="2"/>')
        out.append(f'<path d="{blob(x - 30, base - h * 0.55 + 12, 16, 12, seed + 1, 0.1, 10)}" fill="#6A4A2A"/>')
        rnd = random.Random(seed)
        for k in range(14):
            fx, fy = x - 30 + rnd.uniform(-18, 18), base - h * 0.55 + rnd.uniform(-4, 18)
            out.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{rnd.uniform(3, 5):.1f}" fill="{rnd.choice(["#E85A9A", "#D8302A", "#FFFFFF", "#7A3AA8", "#3E8A3A"])}"/>')
    if flag:
        out.append(f'<path d="M {x - 2} {base - h * 0.8} L {x - 30} {base - h * 0.97}" stroke="#C8B8A0" stroke-width="2"/>')
        out.append(us_flag(D, x - 30, base - h * 0.97, 46, 28, seed + 5, wave=0.12, flip=-1))
    return "".join(out)


@design("small-town-big-heart")
def small_town():
    D = Doc2("us-sm")
    out = [sky(D, [(0, "#5A8AC8"), (0.55, "#F2B48A"), (1, "#FFD8A0")], 301, 470, ["#7AA0D8", "#FFC8A0"], 50)]
    out.append(soft_glow(D, 120, 260, 220, "#FFF0C0", 0.6))
    # water tower and a steeple over the rooftops
    tx = 470
    for sg in (-1, 1):
        out.append(f'<path d="M {tx + sg * 30} 300 L {tx + sg * 18} 216" stroke="#6A6A80" stroke-width="3"/>')
    out.append(f'<path d="M {tx - 26} 262 L {tx + 26} 262 M {tx - 28} 284 L {tx + 28} 284" stroke="#6A6A80" stroke-width="2"/>')
    out.append(painted(D, rect_pts(tx - 34, 186, tx + 34, 222, 10, 302, 0.3), ("#E8ECF0", "#B8C2CC", "#6A7484"), 302, sdir=(1, 0.2), sk=0.2, angle=-90, n=8, inkw=1.4, hi=0.4))
    out.append(painted(D, pp([(tx - 38, 188), (tx, 166), (tx + 38, 188)]), ("#C8D0DA", "#8A94A4", "#4A5464"), 303, sk=0.1, n=4, inkw=1.4, hi=0.4))
    out.append(p_heart(D, tx, 205, 12, CHERRY, 304, 0, inkw=1))
    sx = 150
    out.append(painted(D, pp([(sx - 14, 260), (sx + 14, 260), (sx + 14, 214), (sx - 14, 214)]), CREAM, 305, sk=0.15, n=4, inkw=1.2, hi=0.4))
    out.append(painted(D, pp([(sx - 16, 216), (sx, 168), (sx + 16, 216)]), CREAM, 306, sk=0.15, n=4, inkw=1.2, hi=0.4))
    out.append(f'<path d="M {sx} 168 L {sx} 154 M {sx - 5} 159 L {sx + 5} 159" stroke="#3A2418" stroke-width="2"/>')
    # the row of storefronts
    out.append(storefront(D, -10, 150, 232, 470, 311, ("#E8806A", "#B8483A", "#7A2418"), "BARBER", BEBAS, ("#FFF6E8", "#22386A", "#0E1C3E"), "#D8302A", arch=True))
    out.append(storefront(D, 150, 310, 254, 470, 312, ("#F2D8A0", "#D8B070", "#8A6A3A"), "Hardware", DMS, ("#FFF6E8", "#2E5A3A", "#163A22"), "#2E8A4A", brick=False))
    out.append(storefront(D, 310, 464, 222, 470, 313, ("#D8806A", "#A8503A", "#6A2A1A"), "SODA FOUNTAIN", BEBAS, ("#FFFFFF", "#D8302A", "#7A1010"), "#4AB2A8", arch=True))
    out.append(storefront(D, 464, 610, 246, 470, 314, ("#C8D8C0", "#98B094", "#5A7458"), "Bakery", SERIF_IT, ("#7A2E14", "#FFF2D8", "#C8B080"), "#E85A7A", brick=False))
    # sidewalk and curb
    out.append(painted(D, rect_pts(-10, 466, 610, 500, 30, 315, 0.4), ("#E8E0D2", "#D0C6B6", "#9A907E"), 315, sdir=(0, 1), sk=0.1, angle=0, n=30, inkw=1.2, hi=0.3))
    for x in range(-10, 620, 60):
        out.append(f'<path d="M {x} 468 L {x - 8} 498" stroke="#A89E8C" stroke-width="1.6"/>')
    out.append(painted(D, rect_pts(-10, 498, 610, 508, 30, 316, 0.3), ("#F4F0E8", "#C8C2B8", "#8A8478"), 316, sk=0.1, n=10, inkw=1.2, hi=0.3))
    # the street
    out.append(f'<rect y="508" width="600" height="92" fill="{D.lin([(0, "#6A6470"), (1, "#3A3640")])}"/>')
    out.append(strokes(D.nid(), "M 0 508 L 600 508 L 600 600 L 0 600 Z", (-40, 508, 600, 600), ["#7A7480", "#2E2A34"], 317, n=40, angle=0, length=(40, 120), width=(2, 4)))
    # lamp with a flag, a bench, the barber pole
    out.append(street_lamp(D, 452, 494, 206, 318))
    bx = 214
    out.append(painted(D, rect_pts(bx - 40, 462, bx + 40, 470, 10, 319, 0.3), WOOD, 319, sk=0.1, n=4, inkw=1.2, hi=0.3))
    out.append(painted(D, rect_pts(bx - 40, 440, bx + 40, 448, 10, 320, 0.3), WOOD, 320, sk=0.1, n=4, inkw=1.2, hi=0.3))
    for sg in (-1, 1):
        out.append(f'<path d="M {bx + sg * 34} 436 L {bx + sg * 34} 488" stroke="#1E2A3A" stroke-width="3"/>')
    out.append(painted(D, rect_pts(96, 336, 102, 346, 4, 321, 0.2), IRON, 321, sk=0.1, n=2, inkw=1, hi=0.3))
    out.append(barber_pole(D, 118, 330, 96, 26, 322))
    # an old pickup parked at the curb
    out.append(pickup50(D, 330, 566, 250, 323, body=("#9ACAE0", "#4A8AB0", "#1E4A6A")))
    # lettering
    out.append(letters(D, 300, 122, "Small Town", SERIF_IT, 92, "#FFFFFF", ["#FFFFFF", "#FFEAD8"], 324, max_w=420,
                       shadow="#2A3A6A", soff=(0.025, 0.04), angle=-40))
    out.append(p_heart(D, 412, 156, 13, CHERRY, 325, -8, inkw=1.2))
    out.append(letters(D, 290, 174, "BIG HEART", ANTON, 46, "#B8352A", ["#D8503A", "#8A1E12"], 326, ls=6, max_w=230, shadow="#FFF2D8", soff=(0.03, 0.05), wob=0.3))
    return finish_a(D, out, 327)


# ================================================================ 12. down on the farm — the red barn and its barn quilt
def barn_quilt(D, cx, cy, s, seed, cols=("#D8302A", "#22386A", "#EAAE3A", "#FFF6E8")):
    """A painted barn-quilt square: an eight-point star with corner blocks, hung on the gable."""
    red, navy, gold, cream = cols
    h = s / 2
    out = [painted(D, rect_pts(cx - h - 6, cy - h - 6, cx + h + 6, cy + h + 6, 10, seed, 0.3), WHITE, seed, sk=0.12, n=6, inkw=1.6, hi=0.3)]
    out.append(f'<rect x="{cx - h:.1f}" y="{cy - h:.1f}" width="{s:.1f}" height="{s:.1f}" fill="{cream}"/>')
    q = s / 4
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        x0 = cx + (h - q if sx > 0 else -h)
        y0 = cy + (h - q if sy > 0 else -h)
        out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{q:.1f}" height="{q:.1f}" fill="{gold}"/>')
        out.append(f'<path d="M {x0:.1f} {y0:.1f} L {x0 + q:.1f} {y0 + q:.1f}" stroke="{dk(gold, 0.3)}" stroke-width="1.2" opacity="0.6"/>')
    for k in range(8):
        a = math.radians(k * 45 - 90)
        tip = (cx + math.cos(a) * h * 0.98, cy + math.sin(a) * h * 0.98)
        l = (cx + math.cos(a - math.radians(22.5)) * h * 0.52, cy + math.sin(a - math.radians(22.5)) * h * 0.52)
        r = (cx + math.cos(a + math.radians(22.5)) * h * 0.52, cy + math.sin(a + math.radians(22.5)) * h * 0.52)
        c = red if k % 2 == 0 else navy
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {l[0]:.1f} {l[1]:.1f} L {tip[0]:.1f} {tip[1]:.1f} L {r[0]:.1f} {r[1]:.1f} Z" fill="{c}"/>')
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {tip[0]:.1f} {tip[1]:.1f} L {r[0]:.1f} {r[1]:.1f} Z" fill="#000000" opacity="0.14"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s * 0.07:.1f}" fill="{gold}"/>')
    out.append(strokes(D.nid(), f"M {cx - h} {cy - h} L {cx + h} {cy - h} L {cx + h} {cy + h} L {cx - h} {cy + h} Z", (cx - h, cy - h, cx + h, cy + h),
                       ["#FFFFFF", "#3A2418"], seed + 1, n=24, angle=-30, length=(8, 20), width=(0.8, 2), opacity=(0.08, 0.22)))
    out.append(ink(f"M {cx - h} {cy - h} L {cx + h} {cy - h} L {cx + h} {cy + h} L {cx - h} {cy + h} Z", INK, 1.4, seed, 1, 0.7))
    return "".join(out)


def hay_roll(D, cx, base, r, seed):
    out = [cast(D, cx + r * 0.3, base, r * 1.2, r * 0.18, strength=0.45, seed=seed)]
    side = [(cx - r * 0.9, base - r * 1.7), (cx + r * 0.6, base - r * 1.85), (cx + r * 0.7, base), (cx - r * 0.8, base + 2)]
    out.append(painted(D, pp(side, 10, seed), ("#F6D88A", "#D8A84A", "#8A6420"), seed, sdir=(0.4, 1), sk=0.12, angle=0, n=30, inkw=1.6, hi=0.4))
    face = blob_pts(cx - r * 0.85, base - r * 0.88, r * 0.42, r * 0.9, seed + 1, 0.04, 20)
    out.append(painted(D, face, ("#FAE0A0", "#E2B65A", "#9A7028"), seed + 1, sk=0.15, n=6, inkw=1.6, hi=0.4))
    for k in range(4):
        out.append(ink(smooth_closed(ell_pts(cx - r * 0.85, base - r * 0.88, r * 0.42 * (1 - k * 0.22), r * 0.9 * (1 - k * 0.22), 0, 360, 20)[:-1]), "#A8742A", 1.2, seed + k, 1, 0.55))
    rnd = random.Random(seed)
    for _ in range(26):
        x, y = rnd.uniform(cx - r * 0.5, cx + r * 0.6), rnd.uniform(base - r * 1.7, base - 4)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(6, 16):.1f} {rnd.uniform(-2, 2):.1f}" stroke="#FFF2C0" stroke-width="1.2" opacity="0.7"/>')
    return "".join(out)


@design("down-on-the-farm")
def down_on_the_farm():
    D = Doc2("us-df")
    out = [sky(D, [(0, "#7AB0E0"), (0.6, "#C8E0F0"), (1, "#FFF0D8")], 331, 400, ["#9AC4EC", "#FFF6E8"], 40)]
    out.append(puff_cloud(D, 470, 200, 150, 332, pal=("#FFFFFF", "#F6FAFF", "#C8D8EC")))
    out.append(puff_cloud(D, 110, 236, 90, 333, pal=("#FFFFFF", "#F6FAFF", "#C8D8EC")))
    # far fields and a tree line
    out.append(hill(D, ridge([(-20, 370), (200, 352), (420, 364), (620, 350)], 334, 3), 600, ("#C8DCA0", "#9AB878", "#6A8A54"), 334, inkw=0))
    rnd = random.Random(335)
    for _ in range(14):
        x = rnd.uniform(-10, 610)
        out.append(dab_crown(D, x, 352 + rnd.uniform(-6, 6), rnd.uniform(14, 22), rnd.uniform(10, 16), [SAGE, GRASS], int(x) + 900, n=10, size=(5, 8), inkw=0, base=False))
    # windmill far right
    wx = 548
    out.append(f'<path d="M {wx - 12} 372 L {wx} 296 L {wx + 12} 372" stroke="#6A5A4A" stroke-width="2" fill="none"/>')
    for k in range(12):
        a = math.radians(k * 30)
        out.append(f'<path d="M {wx} 292 L {wx + math.cos(a) * 18:.1f} {292 + math.sin(a) * 18:.1f}" stroke="#7A6A5A" stroke-width="2.4"/>')
    # silo
    sx0, sx1, st, sb = 404, 470, 226, 466
    out.append(painted(D, rect_pts(sx0, st, sx1, sb, 16, 336, 0.4), ("#E8E0D4", "#C8BCAC", "#7A6E62"), 336, sdir=(1, 0.1), sk=0.25, angle=-90, n=24, inkw=1.8, hi=0.4))
    for y in range(int(st) + 20, sb, 22):
        out.append(f'<path d="M {sx0} {y} Q {(sx0 + sx1) / 2} {y + 6} {sx1} {y}" stroke="#7A6E62" stroke-width="1.6" fill="none" opacity="0.6"/>')
    out.append(painted(D, [(sx0 - 3, st + 2)] + ell_pts((sx0 + sx1) / 2, st + 2, (sx1 - sx0) / 2 + 3, 30, 180, 360, 16)[1:], ("#C8D0DA", "#8A94A4", "#4A5464"), 337, sk=0.15, n=6, inkw=1.6, hi=0.5))
    # the barn: gambrel front, side wall receding
    bx0, bx1, eave, base = 110, 380, 340, 470
    cx = (bx0 + bx1) / 2
    knee_y, peak_y = 278, 214
    side = [(bx1, base), (bx1, eave), (bx1 + 34, eave - 16), (bx1 + 34, base - 10)]
    out.append(painted(D, pp(side, 10, 338), (dk(BARN[0], 0.1), dk(BARN[1], 0.25), dk(BARN[2], 0.3)), 338, sdir=(1, 0), sk=0.15, angle=-90, n=10, inkw=1.6, hi=0.2))
    roof_side = [(bx1 - 2, eave + 2), (bx1 - 30, knee_y), (cx + 4, peak_y), (cx + 40, peak_y - 14), (bx1 + 4, knee_y - 16), (bx1 + 36, eave - 14)]
    out.append(painted(D, pp(roof_side, 10, 339), ("#9AA0AE", "#5E6472", "#2E323C"), 339, sdir=(0.6, 1), sk=0.12, angle=-20, n=16, inkw=1.6, hi=0.4))
    front = [(bx0, base), (bx0, eave), (bx0 + 30, knee_y), (cx, peak_y), (bx1 - 30, knee_y), (bx1, eave), (bx1, base)]
    out.append(painted(D, pp(front, 10, 340), BARN, 340, sdir=(0.6, 0.6), sk=0.08, angle=-90, n=60, slen=(20, 60), sw=(1, 3), inkw=2, hi=0.3))
    cid = D.clip(f'<path d="{pd(front)}"/>')
    boards = "".join(f'<path d="M {x} {peak_y} L {x} {base}" stroke="#6A1812" stroke-width="1.4" opacity="0.4"/>' for x in range(bx0 + 12, bx1, 14))
    out.append(f'<g {cid}>{boards}</g>')
    # white trim on the gable and corners
    out.append(pline([(bx0 - 4, eave + 4), (bx0 + 30, knee_y), (cx, peak_y - 2), (bx1 - 30, knee_y), (bx1 + 4, eave + 4)], "#FFF6E8", 7, 341, 1, 1))
    out.append(pline([(bx0 - 4, eave + 4), (bx0 + 30, knee_y), (cx, peak_y - 2), (bx1 - 30, knee_y), (bx1 + 4, eave + 4)], INK, 1.4, 342, 0.6, 1))
    for x in (bx0 + 3, bx1 - 3):
        out.append(pline([(x, eave + 4), (x, base)], "#FFF6E8", 6, 343 + x, 1, 1))
    # the barn quilt on the gable
    out.append(barn_quilt(D, cx, 270, 62, 344))
    # hayloft door with a pulley beam
    out.append(painted(D, rect_pts(cx - 28, 312, cx + 28, 352, 10, 345, 0.3), (dk(BARN[0], 0.1), dk(BARN[1], 0.2), BARN[2]), 345, sk=0.1, n=4, inkw=1.6, hi=0.2))
    out.append(f'<path d="M {cx - 28} 312 L {cx + 28} 352 M {cx + 28} 312 L {cx - 28} 352" stroke="#FFF6E8" stroke-width="4"/>')
    out.append(f'<path d="{hg.org_rect(cx - 28, 312, 56, 40, 346, 0.3, 8, 1)}" fill="none" stroke="#FFF6E8" stroke-width="4"/>')
    # big sliding doors with white X braces
    for k, (d0, d1) in enumerate(((cx - 70, cx), (cx, cx + 70))):
        out.append(painted(D, rect_pts(d0 + 2, 376, d1 - 2, base, 12, 347 + k, 0.3), BARN, 347 + k, sdir=(0.5, 0.5), sk=0.1, angle=-90, n=10, inkw=1.6, hi=0.2))
        out.append(f'<path d="{hg.org_rect(d0 + 2, 376, d1 - d0 - 4, base - 376, 349 + k, 0.3, 8, 1)}" fill="none" stroke="#FFF6E8" stroke-width="5"/>')
        out.append(f'<path d="M {d0 + 4} 378 L {d1 - 4} {base - 2} M {d1 - 4} 378 L {d0 + 4} {base - 2}" stroke="#FFF6E8" stroke-width="4.5"/>')
    out.append(painted(D, rect_pts(cx - 80, 366, cx + 80, 374, 12, 351, 0.3), IRON, 351, sk=0.1, n=3, inkw=1, hi=0.3))
    for x in (bx0 + 26, bx1 - 50):
        out.append(f'<path d="{hg.org_rect(x, 386, 24, 26, x, 0.3, 6, 1)}" fill="#3A2A2A" stroke="#FFF6E8" stroke-width="3"/>')
    # weather vane rooster
    out.append(f'<path d="M {cx} {peak_y} L {cx} {peak_y - 26} M {cx - 12} {peak_y - 16} L {cx + 12} {peak_y - 16}" stroke="#3A2418" stroke-width="2"/>')
    out.append(f'<path d="M {cx - 10} {peak_y - 30} q 6 -12 14 -6 l 4 -6 l 2 8 q 2 8 -8 10 Z" fill="#3A2418"/>')
    # foreground pasture, fence, hay rolls, flowers
    out.append(hill(D, ridge([(-20, 462), (300, 470), (620, 456)], 352, 3), 600, GRASS, 352, angle=-4, inkw=0))
    out.append(grass(353, (0, 470, 600, 600), ["#5A8A30", "#8AB850", "#2E5A1E", "#A8D070"], 260, (8, 20)))
    for k, x in enumerate(range(-20, 620, 80)):
        out.append(painted(D, rect_pts(x - 5, 486, x + 5, 548, 10, 354 + k, 0.4), WOOD, 354 + k, sdir=(1, 0), sk=0.2, angle=-90, n=4, inkw=1.4, hi=0.3))
    for y in (496, 520):
        out.append(taper([(-20, y), (300, y + 4), (620, y - 2)], 7, 7, "#8A5A30"))
        out.append(taper([(-20, y - 2), (300, y + 2), (620, y - 4)], 2, 2, "#D8A06A", 0.8))
    out.append(hay_roll(D, 486, 530, 50, 362))
    out.append(hay_roll(D, 92, 556, 40, 363))
    for _ in range(40):
        x, y = rnd.uniform(0, 600), rnd.uniform(536, 600)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(2, 3.6):.1f}" fill="{rnd.choice(["#FFFFFF", "#F6C21C", "#E8604A", "#9A7AE0"])}"/>')
    # lettering
    out.append(letters(D, 300, 112, "Down on the Farm", SERIF_IT, 76, "#8A2418", ["#B8352A", "#6A1812", "#D0503A"], 364, max_w=460,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-40, hi="#FFC8A8"))
    out.append(ruled(300, 156, "FRESH EGGS · HAY · SWEET CORN", "#22386A", font=JOS, size=19, ls=4, line_w=20, gap=10, max_w=400))
    return finish_a(D, out, 365)


# ================================================================ 13. home for the holidays — pickup bringing the tree home, snow
def fir_tree_lying(D, x0, y0, L, H, seed, ang=-8):
    """A fresh-cut fir lying in a truck bed: tapering mass of needle tufts, cut trunk at the back, twine."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    out = []
    for i in range(120):
        t = rnd.uniform(0, 1)
        w = H * (1 - t) ** 0.8 * 0.5
        o = rnd.uniform(-1, 1) * w
        x, y = x0 + ux * L * t + nx * o, y0 + uy * L * t + ny * o
        s = rnd.uniform(8, 16) * (1 - t * 0.5)
        col = rnd.choice(["#2E6A3A", "#1E4E2A", "#3E7A44", "#14361E"])
        out.append(f'<path d="{blob(x, y, s, s * 0.6, rnd.randint(0, 9999), 0.25, 8, math.degrees(a) + rnd.uniform(-40, 40))}" fill="{col}"/>')
    for i in range(80):
        t = rnd.uniform(0, 1)
        w = H * (1 - t) ** 0.8 * 0.5
        o = rnd.uniform(-1, 1) * w
        x, y = x0 + ux * L * t + nx * o, y0 + uy * L * t + ny * o
        dx = rnd.uniform(-1, 1) * 8
        out.append(f'<path d="M {x:.1f} {y:.1f} l {ux * 9 + dx:.1f} {uy * 9 + rnd.uniform(-5, 5):.1f}" stroke="{rnd.choice(["#5A9A5A", "#7AB86A", "#14361E"])}" stroke-width="1.6" stroke-linecap="round"/>')
    for i in range(16):
        t = rnd.uniform(0.05, 0.9)
        w = H * (1 - t) ** 0.8 * 0.45
        x, y = x0 + ux * L * t - nx * w * rnd.uniform(0.5, 1), y0 + uy * L * t - ny * w * rnd.uniform(0.5, 1)
        out.append(f'<path d="{blob(x, y, rnd.uniform(5, 10), rnd.uniform(2.5, 4), rnd.randint(0, 999), 0.2, 8, math.degrees(a))}" fill="#FFFFFF" opacity="0.95"/>')
    for t in (0.25, 0.55):
        w = H * (1 - t) ** 0.8 * 0.5
        cxp, cyp = x0 + ux * L * t, y0 + uy * L * t
        out.append(pline([(cxp - nx * w, cyp - ny * w), (cxp + nx * w * 0.2 + ux * 4, cyp + ny * w * 0.2), (cxp + nx * w, cyp + ny * w)], "#C8A060", 2, seed + int(t * 10), 0.95, 1))
    tx, ty = x0 - ux * 18, y0 - uy * 18
    out.append(taper([(tx, ty), (x0 + ux * 10, y0 + uy * 10)], 12, 10, "#7A5A3A"))
    out.append(f'<path d="{blob(tx, ty, 6, 6, seed, 0.1, 8)}" fill="#E8C890" stroke="#7A5A3A" stroke-width="1.2"/>')
    return "".join(out)


def wreath(D, cx, cy, r, seed):
    rnd = random.Random(seed)
    out = []
    for k in range(40):
        a = rnd.uniform(0, 6.28)
        rr = r * rnd.uniform(0.75, 1.05)
        out.append(f'<path d="{blob(cx + math.cos(a) * rr, cy + math.sin(a) * rr, r * 0.32, r * 0.16, rnd.randint(0, 999), 0.2, 8, math.degrees(a) + 90)}" fill="{rnd.choice(["#2E6A3A", "#1E4E2A", "#4A8A4A"])}"/>')
    for k in range(7):
        a = rnd.uniform(0, 6.28)
        out.append(f'<circle cx="{cx + math.cos(a) * r * 0.9:.1f}" cy="{cy + math.sin(a) * r * 0.9:.1f}" r="{r * 0.12:.1f}" fill="#D8302A"/>')
    out.append(f'<path d="M {cx - r * 0.4:.1f} {cy + r * 0.9:.1f} l {r * 0.4:.1f} {-r * 0.2:.1f} l {r * 0.4:.1f} {r * 0.2:.1f} l {-r * 0.1:.1f} {r * 0.4:.1f} l {-r * 0.3:.1f} {-r * 0.3:.1f} l {-r * 0.3:.1f} {r * 0.3:.1f} Z" fill="#D8302A" stroke="{INK}" stroke-width="1"/>')
    return "".join(out)


@design("home-for-the-holidays")
def home_for_the_holidays():
    D = Doc2("us-hh")
    out = [sky(D, [(0, "#1E2A5A"), (0.6, "#4A5A9A"), (1, "#9AA8D8")], 371, 420, ["#2E3A7A", "#6A7AB8"], 50)]
    out.append(D.glow(300, 380, 300, "#E8C8E8", 0.3, ry=90))
    # snowy hills, a tree line, a farmhouse with lit windows
    out.append(hill(D, ridge([(-20, 360), (220, 340), (420, 352), (620, 336)], 372, 4), 600, ("#FFFFFF", "#DDE4F4", "#9AA4CC"), 372, inkw=0))
    out.append(hg.far_trees(D, 352, 373, "#24304E", n=34, h=(24, 50), snow=True))
    fx = 150
    out.append(painted(D, rect_pts(fx - 60, 300, fx + 50, 358, 14, 374, 0.4), ("#F4E8D8", "#D8C8B4", "#8A7A68"), 374, sk=0.1, n=8, inkw=1.4, hi=0.3))
    out.append(painted(D, pp([(fx - 70, 304), (fx - 6, 262), (fx + 60, 304)]), ("#FFFFFF", "#E8ECF8", "#A8B0D0"), 375, sk=0.1, n=6, inkw=1.4, hi=0.3))
    out.append(f'<path d="M {fx + 26} 280 L {fx + 26} 258 L {fx + 38} 258 L {fx + 38} 292 Z" fill="#8A4A3A"/>')
    out.append(taper([(fx + 32, 254), (fx + 40, 230), (fx + 30, 206), (fx + 44, 180)], 6, 14, "#C8C8E0", 0.4))
    for wx in (fx - 46, fx - 16, fx + 20):
        out.append(D.glow(wx + 8, 324, 30, "#FFC860", 0.6))
        out.append(f'<path d="{hg.org_rect(wx, 314, 16, 20, wx, 0.3, 6, 1)}" fill="#FFD27A" stroke="#5A3A2A" stroke-width="1.6"/>')
    # the snowy lane and the truck
    out.append(hill(D, ridge([(-20, 440), (300, 432), (620, 446)], 376, 2), 600, ("#FFFFFF", "#E2E8F6", "#A8B2D6"), 376, angle=-2, inkw=0))
    out.append(f'<path d="M -10 470 Q 300 452 610 476 L 610 530 Q 300 506 -10 524 Z" fill="#C8D0E8" opacity="0.6"/>')
    for k in range(2):
        out.append(pline([(-10, 486 + k * 20), (300, 470 + k * 20), (610, 492 + k * 20)], "#9AA4CC", 2, 377 + k, 0.5, 1))
    out.append(pickup50(D, 300, 512, 330, 378, body=BARN, flip=1, lights=True, snow=True))
    out.append(fir_tree_lying(D, 140, 408, 200, 100, 379, ang=-12))
    out.append(wreath(D, 466, 456, 16, 380))
    # foreground snowbank and a couple of pines
    out.append(hill(D, ridge([(-20, 560), (200, 548), (400, 556), (620, 544)], 381, 3), 620, ("#FFFFFF", "#E8EEF8", "#B0BAD8"), 381, angle=-2, inkw=1.2, inkop=0.3))
    out.append(hg.fir(D, 52, 566, 150, 84, 382, snow=True))
    out.append(hg.fir(D, 560, 572, 120, 70, 383, snow=True))
    # falling snow
    out.append(hg.flakes(384, 120, (0, 0, 600, 600), r=(1.2, 3.2)))
    # lettering
    out.append(letters(D, 300, 114, "Home for the", SERIF_IT, 64, "#FFFFFF", ["#FFFFFF", "#E8ECFF"], 385, max_w=380,
                       shadow="#0E1438", soff=(0.025, 0.04), angle=-40))
    out.append(letters(D, 300, 196, "Holidays", SERIF_IT, 96, "#FFE2A0", ["#FFF2C8", "#F6C21C", "#FFD27A"], 386, max_w=400,
                       shadow="#7A1414", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    return finish_a(D, out, 387)


# ================================================================ 14. friday night football — under the lights
def football(D, cx, cy, L, seed, rot_=-20, stripes=True):
    """Leather football: prolate body, pebbled hide, white stripes near the tips, white laces."""
    pts = []
    for i in range(36):
        t = 2 * math.pi * i / 36
        x = L / 2 * math.cos(t)
        y = L * 0.31 * math.sin(t) * (1 - 0.18 * math.cos(t) ** 2)
        pts.append((cx + x, cy + y))
    pts = rot(pts, cx, cy, rot_)
    out = [cast(D, cx + L * 0.08, cy + L * 0.3, L * 0.5, L * 0.08, strength=0.5, seed=seed)]
    out.append(painted(D, pts, ("#C8783A", "#8A4218", "#4A1E08"), seed, sdir=(0.5, 0.8), sk=0.2, angle=rot_, n=int(L * 0.6), inkw=1.8, hi=0.45, hik=0.08))
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    inner = [specks(seed + 1, (cx - L / 2, cy - L / 3, cx + L / 2, cy + L / 3), ["#3A1A08", "#D8905A"], int(L * 1.2), (0.6, 1.3), (0.3, 0.7))]
    if stripes:
        for sg in (-1, 1):
            u = sg * L * 0.3
            a = rot([(cx + u, cy - L * 0.4), (cx + u + sg * 6, cy + L * 0.4)], cx, cy, rot_)
            b = rot([(cx + u + sg * 10, cy - L * 0.4), (cx + u + sg * 16, cy + L * 0.4)], cx, cy, rot_)
            inner.append(f'<path d="M {a[0][0]:.1f} {a[0][1]:.1f} L {a[1][0]:.1f} {a[1][1]:.1f} L {b[1][0]:.1f} {b[1][1]:.1f} L {b[0][0]:.1f} {b[0][1]:.1f} Z" fill="#FFF6E8" opacity="0.92"/>')
    seam = rot([(cx - L * 0.36, cy - L * 0.02), (cx, cy - L * 0.1), (cx + L * 0.36, cy - L * 0.02)], cx, cy, rot_)
    inner.append(pline(seam, "#2A0E04", 1.4, seed, 0.6, 1))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    lace = rot([(cx - L * 0.15, cy - L * 0.16), (cx, cy - L * 0.19), (cx + L * 0.15, cy - L * 0.16)], cx, cy, rot_)
    out.append(pline(lace, "#FFFFFF", max(2.5, L * 0.022), seed + 1, 1, 1))
    for k in range(7):
        t = -0.13 + k * 0.043
        a = rot([(cx + L * t, cy - L * 0.23), (cx + L * t, cy - L * 0.12)], cx, cy, rot_)
        out.append(f'<path d="M {a[0][0]:.1f} {a[0][1]:.1f} L {a[1][0]:.1f} {a[1][1]:.1f}" stroke="#FFFFFF" stroke-width="{max(2.6, L * 0.024):.1f}" stroke-linecap="round"/>')
    out.append(f'<path d="{blob(*rot([(cx - L * 0.12, cy - L * 0.12)], cx, cy, rot_)[0], L * 0.12, L * 0.04, seed + 2, 0.2, 10, rot_)}" fill="#FFE0C0" opacity="0.4"/>')
    return "".join(out)


def light_tower(D, x, top, base, seed, rows=3, cols=4, flare=True):
    out = [f'<path d="M {x - 6} {base} L {x - 2} {top + 20} M {x + 6} {base} L {x + 2} {top + 20}" stroke="#2A2E48" stroke-width="3"/>']
    for k in range(int((base - top - 20) / 16)):
        y = top + 26 + k * 16
        out.append(f'<path d="M {x - 5} {y} L {x + 5} {y + 12}" stroke="#2A2E48" stroke-width="1.2"/>')
    w = cols * 13 + 6
    out.append(f'<path d="{hg.org_rect(x - w / 2, top - 4, w, rows * 13 + 8, seed, 0.3, 8, 2)}" fill="#1E2238"/>')
    if flare:
        out.append(D.glow(x, top + rows * 6, 130, "#F4F8FF", 0.55))
        rnd = random.Random(seed)
        for k in range(14):
            a = math.radians(k * 360 / 14 + rnd.uniform(-6, 6))
            L = rnd.uniform(40, 90)
            out.append(taper([(x, top + rows * 6), (x + math.cos(a) * L, top + rows * 6 + math.sin(a) * L)], 3, 0.4, "#FFFFFF", 0.35))
    for i in range(rows):
        for j in range(cols):
            out.append(f'<circle cx="{x - w / 2 + 9.5 + j * 13:.1f}" cy="{top + 6 + i * 13:.1f}" r="5" fill="#FFFFFF"/>')
    return "".join(out)


@design("friday-night-football")
def friday_night_football():
    D = Doc2("us-fn")
    out = [sky(D, [(0, "#080C24"), (0.6, "#1A2250"), (1, "#3A4A7A")], 391, 330, ["#1A2250", "#060818"], 50)]
    out.append(stars_field(392, 40, (0, 0, 600, 200), avoid=((90, 50, 510, 180),)))
    # stadium glow, far stands, scoreboard
    out.append(D.glow(300, 330, 320, "#C8E0FF", 0.35, ry=90))
    out.append(painted(D, rect_pts(-10, 262, 610, 300, 30, 393, 0.4), ("#4A4A6A", "#2A2A48", "#14142A"), 393, sk=0.1, n=20, inkw=0, hi=0.2))
    rnd = random.Random(394)
    for _ in range(320):
        x, y = rnd.uniform(-10, 610), rnd.uniform(266, 296)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.2, 2.2):.1f}" fill="{rnd.choice(["#D8302A", "#FFFFFF", "#E8D8C8", "#B8C8E8", "#D8302A"])}" opacity="0.75"/>')
    sb_x, sb_y = 300, 206
    out.append(f'<path d="M {sb_x - 40} 264 L {sb_x - 40} {sb_y + 40} M {sb_x + 40} 264 L {sb_x + 40} {sb_y + 40}" stroke="#2A2E48" stroke-width="5"/>')
    out.append(painted(D, rect_pts(sb_x - 82, sb_y - 8, sb_x + 82, sb_y + 46, 14, 395, 0.3), ("#2E3A2E", "#1A241A", "#0A120A"), 395, sk=0.1, n=6, inkw=1.6, hi=0.2))
    for k, (lab, num) in enumerate((("HOME", "21"), ("GUEST", "17"))):
        x = sb_x - 42 + k * 84
        out.append(label(x, sb_y + 8, lab, BEBAS, 14, "#FFFFFF", ls=2, max_w=60))
        out.append(f'<text x="{x}" y="{sb_y + 38}" text-anchor="middle" {MONO} font-size="26" fill="#FFB43A">{num}</text>')
    out.append(f'<text x="{sb_x}" y="{sb_y + 38}" text-anchor="middle" {MONO} font-size="12" fill="#FF6A5A">Q4</text>')
    # the light towers
    out.append(light_tower(D, 70, 182, 300, 396))
    out.append(light_tower(D, 530, 182, 300, 397))
    # the field, end-zone view: yard lines get closer toward the far end
    fld = [(60, 300), (540, 300), (680, 470), (-80, 470)]
    out.append(f'<path d="{pd(fld)}" fill="{D.lin([(0, "#4A9A4A"), (1, "#2E7A34")])}"/>')
    cid = D.clip(f'<path d="{pd(fld)}"/>')
    f = []
    for k in range(-6, 8):
        x = 300 + k * 60
        f.append(f'<path d="M {300 + (x - 300) * 0.5:.1f} 300 L {300 + (x + 30 - 300) * 0.5:.1f} 300 L {300 + (x + 30 - 300) * 1.45:.1f} 470 L {300 + (x - 300) * 1.45:.1f} 470 Z" fill="#5AAE52" opacity="0.4"/>')
    for k in range(9):
        t = k / 8
        y = 300 + 170 * t ** 1.6
        half = 240 + 140 * t ** 1.6
        f.append(f'<path d="M {300 - half:.1f} {y:.1f} L {300 + half:.1f} {y:.1f}" stroke="#FFFFFF" stroke-width="{1.2 + 2.4 * t:.1f}" opacity="0.85"/>')
    f.append(f'<path d="M 60 300 L -80 470 M 540 300 L 680 470" stroke="#FFFFFF" stroke-width="3"/>')
    f.append(f'<rect x="0" y="300" width="600" height="170" fill="{D.rad([(0, "#E8F4FF", 0.25), (1, "#E8F4FF", 0)], 0.5, 0.2, 0.7)}"/>')
    out.append(f'<g {cid}>{"".join(f)}</g>')
    # far goal post
    out.append(f'<path d="M 300 318 L 300 296 M 270 296 L 330 296 M 270 296 L 270 262 M 330 296 L 330 262" stroke="#F6D23A" stroke-width="3" fill="none"/>')
    # players lined up at the line of scrimmage
    for k in range(11):
        for side, col, y in ((0, "#D8302A", 360), (1, "#F4F0E8", 346)):
            x = 170 + k * 26 + side * 4
            out.append(f'<ellipse cx="{x}" cy="{y + 14}" rx="7" ry="2" fill="#0A2A0A" opacity="0.4"/>')
            out.append(f'<path d="{hg.org_rect(x - 5, y - 6, 10, 12, k * 7 + side, 0.3, 4, 3)}" fill="{col}"/>')
            out.append(f'<rect x="{x - 4}" y="{y + 5}" width="8" height="8" fill="#E8E2D8"/>')
            out.append(f'<circle cx="{x}" cy="{y - 9}" r="4.4" fill="{"#E8B83A" if side == 0 else "#2A3A6A"}"/>')
    # foreground bleacher: aluminium bench, blanket, cocoa, the ball, fans' backs
    out.append(f'<rect y="452" width="600" height="148" fill="{D.lin([(0, "#2A2E44"), (1, "#14162A")])}"/>')
    for y in (470, 540):
        out.append(fluted(D, f"M -10 {y} L 610 {y} L 610 {y + 22} L -10 {y + 22} Z", (-10, y, 610, y + 22), 398 + y, top="#8A94B0", mid="#E8EEF6", bot="#4A5070", step=6))
    for k, (x, base, coat, hair, hat) in enumerate(((60, 474, "#B8302A", "#2A1A10", "beanie"), (150, 470, "#22386A", "#6A3A1A", None), (520, 474, "#3A5A3A", "#C8964E", "cap"))):
        out.append(f'<path d="M {x - 34} {base + 4} Q {x - 32} {base - 46} {x} {base - 50} Q {x + 32} {base - 46} {x + 34} {base + 4} Z" fill="{coat}"/>')
        out.append(f'<path d="M {x - 34} {base + 4} Q {x - 32} {base - 46} {x} {base - 50} Q {x + 32} {base - 46} {x + 34} {base + 4} Z" fill="{D.lin([(0, "#FFFFFF", 0.18), (1, "#000000", 0.3)], 0, 0, 1, 0)}"/>')
        out.append(f'<circle cx="{x}" cy="{base - 66}" r="17" fill="{hair}"/>')
        if hat == "beanie":
            out.append(f'<path d="M {x - 18} {base - 68} Q {x} {base - 100} {x + 18} {base - 68} Z" fill="#F4F0E8"/><circle cx="{x}" cy="{base - 92}" r="6" fill="#D8302A"/>'
                       f'<path d="M {x - 18} {base - 70} L {x + 18} {base - 70}" stroke="#D8302A" stroke-width="5"/>')
        if hat == "cap":
            out.append(f'<path d="M {x - 17} {base - 70} Q {x} {base - 92} {x + 17} {base - 70} Z" fill="#D8302A"/>')
        if k == 1:
            out.append(f'<path d="M {x + 24} {base - 30} L {x + 46} {base - 120}" stroke="#E8B48E" stroke-width="9" stroke-linecap="round"/>')
            out.append(painted(D, pp([(x + 46, base - 120), (x + 120, base - 100), (x + 46, base - 92)]), CHERRY, 399, sk=0.1, n=4, inkw=1.4, hi=0.3))
            out.append(label(x + 74, base - 103, "GO!", BEBAS, 18, "#FFFFFF", ls=1, extra=f' transform="rotate(14 {x + 74} {base - 108})"'))
    # plaid stadium blanket and hot cocoa
    bl = pp([(236, 520), (430, 508), (446, 620), (226, 620)], 14, 400)
    out.append(cloth(D, bl, "#22386A", 400, base="#C8302A", cell=16, rot_=10, folds=[((280, 530), (290, 570), (284, 610)), ((380, 524), (372, 570), (380, 610))]))
    cx_ = 222
    out.append(painted(D, pp([(cx_ - 22, 476), (cx_ + 22, 476), (cx_ + 17, 534), (cx_ - 17, 534)]), ("#FFFFFF", "#F2EEE6", "#B8B0A6"), 401, sdir=(0.9, 0.2), sk=0.15, angle=-90, n=6, inkw=1.6, hi=0.4))
    out.append(f'<path d="{smooth_closed(ell_pts(cx_, 476, 22, 5, 0, 360, 14)[:-1])}" fill="#6A3A1A" stroke="#B8B0A6" stroke-width="2"/>')
    out.append(steam(cx_, 466, 40, 402, "#FFFFFF", 2, 16, 5, 0.55))
    out.append(football(D, 372, 470, 170, 403, rot_=-18))
    # lettering
    out.append(letters(D, 300, 112, "Friday Night", SERIF_IT, 84, "#FFFFFF", ["#FFFFFF", "#E8F0FF"], 404, max_w=360,
                       shadow="#0A0C24", soff=(0.025, 0.04), angle=-40))
    out.append(ruled(300, 156, "UNDER THE LIGHTS", "#FFB43A", font=JOS, size=22, ls=6, line_w=22, gap=12, max_w=300))
    return finish_a(D, out, 405)


# ================================================================ 15. school days — the yellow bus, a lunchbox on the curb
def school_bus(D, x0, y0, L, seed):
    """Conventional yellow school bus in side view facing right; (x0, y0) = rear bottom corner on the ground."""
    H = L * 0.36
    out = [cast(D, x0 + L * 0.5, y0 + 2, L * 0.55, 10, strength=0.5, seed=seed)]
    YEL = ("#FFE07A", "#F6B21C", "#B8740A")
    body = [(x0, y0 - 18), (x0, y0 - H + 10), (x0 + 8, y0 - H), (x0 + L * 0.78, y0 - H), (x0 + L * 0.8, y0 - H + 8), (x0 + L * 0.8, y0 - H * 0.52),
            (x0 + L * 0.97, y0 - H * 0.5), (x0 + L, y0 - H * 0.42), (x0 + L, y0 - 18)]
    out.append(painted(D, pp(body, 14, seed), YEL, seed, sdir=(0.2, 1), sk=0.1, angle=0, n=60, slen=(30, 90), sw=(1.4, 3), inkw=2, hi=0.45))
    # roof highlight and black rub rails
    out.append(taper([(x0 + 10, y0 - H + 4), (x0 + L * 0.77, y0 - H + 4)], 3, 3, "#FFF2B8", 0.8))
    for k, f in enumerate((0.38, 0.27, 0.16)):
        out.append(pline([(x0 + 2, y0 - H * f), (x0 + L * 0.995, y0 - H * f)], "#1A1A1A", 3.2, seed + k, 0.95, 1))
    out.append(pline([(x0 + 2, y0 - H * 0.66), (x0 + L * 0.8, y0 - H * 0.66)], "#1A1A1A", 2.6, seed + 5, 0.9, 1))
    # windows with kids
    nwin = 8
    ww = L * 0.066
    rnd = random.Random(seed)
    for k in range(nwin):
        wx = x0 + L * 0.05 + k * L * 0.086
        wy = y0 - H * 0.9
        wh = H * 0.24
        g = D.lin([(0, "#D8EEF8"), (0.5, "#8AB6D0"), (1, "#4A6E88")])
        out.append(f'<path d="{hg.org_rect(wx, wy, ww, wh, seed + k, 0.3, 8, 3)}" fill="{g}"/>')
        if k not in (0, 6):
            hx = wx + ww * rnd.uniform(0.3, 0.7)
            hc = rnd.choice(["#2A1A10", "#6A3A1A", "#C8964E", "#1A1010", "#9A6634"])
            out.append(f'<path d="M {hx - 9:.1f} {wy + wh:.1f} Q {hx:.1f} {wy + wh - 16:.1f} {hx + 9:.1f} {wy + wh:.1f} Z" fill="{rnd.choice(["#D8302A", "#2E5AA8", "#3E8A4A", "#E8A030", "#8A4AA8"])}"/>')
            out.append(f'<circle cx="{hx:.1f}" cy="{wy + wh - 18:.1f}" r="6.4" fill="{rnd.choice(figures.SKINS[:6])}"/>')
            out.append(f'<path d="M {hx - 7:.1f} {wy + wh - 20:.1f} Q {hx:.1f} {wy + wh - 30:.1f} {hx + 7:.1f} {wy + wh - 20:.1f} Z" fill="{hc}"/>')
            if k == 3:
                out.append(f'<path d="M {hx + 6:.1f} {wy + wh - 10:.1f} L {hx + 14:.1f} {wy - 6:.1f}" stroke="#E8B48E" stroke-width="4" stroke-linecap="round"/>'
                           f'<circle cx="{hx + 15:.1f}" cy="{wy - 9:.1f}" r="4" fill="#E8B48E"/>')
        out.append(f'<path d="M {wx:.1f} {wy + wh * 0.45:.1f} L {wx + ww:.1f} {wy + wh * 0.45:.1f}" stroke="#E8E8E8" stroke-width="2"/>')
        out.append(ink(hg.org_rect(wx, wy, ww, wh, seed + k, 0.3, 8, 3), "#1A1A1A", 2, seed + k, 1, 0.9))
        out.append(taper([(wx + 4, wy + wh - 4), (wx + ww * 0.5, wy + 4)], 2.4, 1, "#FFFFFF", 0.55))
    # SCHOOL BUS lettering on the belt
    out.append(label(x0 + L * 0.4, y0 - H * 0.44, "SCHOOL BUS", BEBAS, H * 0.17, "#1A1A1A", ls=4, max_w=L * 0.5))
    # door and driver window
    dx = x0 + L * 0.715
    out.append(f'<path d="{hg.org_rect(dx, y0 - H * 0.92, L * 0.075, H * 0.88, seed + 20, 0.3, 8, 2)}" fill="#3A4A58"/>')
    for k in range(2):
        out.append(f'<path d="{hg.org_rect(dx + 4 + k * L * 0.036, y0 - H * 0.86, L * 0.03, H * 0.4, seed + 21 + k, 0.3, 6, 2)}" fill="#A8C8DC"/>')
    # hood, grille, headlight, bumper
    out.append(painted(D, rect_pts(x0 + L * 0.985, y0 - H * 0.44, x0 + L * 1.02, y0 - 16, 6, seed + 22, 0.3), CHROME, seed + 22, sk=0.1, n=3, inkw=1.4, hi=0.5))
    out.append(f'<circle cx="{x0 + L * 0.95:.1f}" cy="{y0 - H * 0.38:.1f}" r="{H * 0.05:.1f}" fill="#FFF6C8" stroke="#1A1A1A" stroke-width="1.6"/>')
    out.append(painted(D, rect_pts(x0 - 6, y0 - 26, x0 + L + 8, y0 - 12, 20, seed + 23, 0.3), ("#5A5A60", "#1A1A1E", "#0A0A0C"), seed + 23, sk=0.1, n=8, inkw=1, hi=0.3))
    # warning lights on the roof corners
    for x, c in ((x0 + 10, "#D8302A"), (x0 + 26, "#F6A01C"), (x0 + L * 0.77, "#D8302A"), (x0 + L * 0.75, "#F6A01C")):
        out.append(f'<path d="{blob(x, y0 - H + 4, 6, 5, int(x), 0.1, 8)}" fill="{c}" stroke="#1A1A1A" stroke-width="1.2"/>')
    out.append(D.glow(x0 + L * 0.77, y0 - H + 4, 26, "#FF4A3A", 0.6))
    # stop arm
    sx, sy = x0 + L * 0.62, y0 - H * 0.6
    out.append(f'<path d="M {sx + 14:.1f} {sy:.1f} L {sx + 2:.1f} {sy:.1f}" stroke="#1A1A1A" stroke-width="3"/>')
    oc = [(sx - 22 + 22 * math.cos(math.radians(22.5 + 45 * k)), sy + 22 * math.sin(math.radians(22.5 + 45 * k))) for k in range(8)]
    out.append(f'<path d="{pd(oc)}" fill="#D8302A" stroke="#FFFFFF" stroke-width="2.4"/>')
    out.append(label(sx - 22, sy + 5, "STOP", BEBAS, 15, "#FFFFFF", ls=1, max_w=34))
    # wheels
    for u in (0.17, 0.86):
        wx, wy = x0 + L * u, y0 - 12
        r = H * 0.2
        out.append(f'<path d="M {wx - r * 1.3:.1f} {wy:.1f} A {r * 1.3:.1f} {r * 1.3:.1f} 0 0 1 {wx + r * 1.3:.1f} {wy:.1f} Z" fill="#1A1A1A"/>')
        out.append(f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="{r:.1f}" fill="#1C1C20"/><circle cx="{wx:.1f}" cy="{wy:.1f}" r="{r * 0.45:.1f}" fill="#C8CED8"/><circle cx="{wx:.1f}" cy="{wy:.1f}" r="{r * 0.15:.1f}" fill="#5E6878"/>')
    return "".join(out)


def lunchbox(D, cx, base, w, h, seed, col=CHERRY):
    out = [cast(D, cx + 6, base + 2, w * 0.6, 7, strength=0.5, seed=seed)]
    out.append(ink(f"M {cx - w * 0.25:.1f} {base - h:.1f} Q {cx - w * 0.25:.1f} {base - h - 24:.1f} {cx:.1f} {base - h - 24:.1f} Q {cx + w * 0.25:.1f} {base - h - 24:.1f} {cx + w * 0.25:.1f} {base - h:.1f}", "#1A1A1E", 6, seed, 1, 1))
    out.append(ink(f"M {cx - w * 0.25:.1f} {base - h - 2:.1f} Q {cx - w * 0.25:.1f} {base - h - 24:.1f} {cx:.1f} {base - h - 24:.1f}", "#6A6A74", 2, seed + 1, 1, 0.8))
    bx = rect_pts(cx - w / 2, base - h, cx + w / 2, base, 10, seed, 0.4)
    out.append(painted(D, bx, col, seed, sdir=(0.7, 0.6), sk=0.12, angle=0, n=14, inkw=1.8, hi=0.4))
    band = f"M {cx - w / 2 + 3:.1f} {base - h * 0.62:.1f} L {cx + w / 2 - 3:.1f} {base - h * 0.62:.1f} L {cx + w / 2 - 3:.1f} {base - h * 0.28:.1f} L {cx - w / 2 + 3:.1f} {base - h * 0.28:.1f} Z"
    out.append(gingham(D, band, "#22386A", "#F6C21C", 8))
    out.append(ink(band, INK, 1.2, seed, 1, 0.6))
    out.append(painted(D, rect_pts(cx - w / 2 - 2, base - h - 4, cx + w / 2 + 2, base - h + 8, 8, seed + 1, 0.3), col, seed + 1, sk=0.15, n=4, inkw=1.4, hi=0.4))
    for sg in (-1, 1):
        out.append(f'<path d="{hg.org_rect(cx + sg * w * 0.3 - 5, base - h + 2, 10, 12, seed + sg, 0.2, 4, 2)}" fill="#D8DEE6" stroke="#4A4A54" stroke-width="1"/>')
    return "".join(out)


@design("school-days")
def school_days():
    D = Doc2("us-sd")
    out = [sky(D, [(0, "#7AB4E8"), (0.7, "#CDE6F4"), (1, "#FFF2DA")], 411, 420, ["#9AC8EE", "#FFF6E8"], 40)]
    out.append(puff_cloud(D, 470, 196, 120, 412, pal=("#FFFFFF", "#F6FAFF", "#C8D8EC")))
    # autumn maples and a white schoolhouse far off
    out.append(hill(D, ridge([(-20, 384), (300, 374), (620, 382)], 413, 3), 600, ("#C8D890", "#9AB068", "#6A8040"), 413, inkw=0))
    out.append(painted(D, rect_pts(400, 318, 470, 372, 12, 414, 0.3), BARN, 414, sk=0.1, n=4, inkw=1.2, hi=0.3))
    out.append(painted(D, pp([(394, 320), (435, 292), (476, 320)]), WHITE, 415, sk=0.1, n=3, inkw=1.2, hi=0.3))
    out.append(painted(D, rect_pts(428, 270, 442, 296, 6, 416, 0.3), WHITE, 416, sk=0.1, n=2, inkw=1.2, hi=0.3))
    out.append(f'<path d="M 435 258 L 435 270 M 430 262 L 440 262" stroke="#3A2418" stroke-width="2"/>')
    for k, (x, r) in enumerate(((80, 70), (190, 54), (540, 74))):
        out.append(taper([(x, 392), (x + 2, 330)], 12, 8, "#5A3A22"))
        out.append(dab_crown(D, x, 318, r, r * 0.8, [("#FFC870", "#F28A2A", "#A8461A"), ("#FF9A70", "#D8402A", "#7A1E12"), ("#FFE08A", "#EAAE3A", "#A8701E")], 417 + k,
                             n=int(r * 2.2), size=(7, 12), inkw=1.2))
    # road
    out.append(f'<path d="M -10 392 L 610 392 L 610 470 L -10 470 Z" fill="#6A6672"/>')
    out.append(f'<path d="M -10 392 L 610 392" stroke="#E8E0D0" stroke-width="3"/>')
    for x in range(-10, 620, 70):
        out.append(f'<path d="M {x} 436 L {x + 36} 436" stroke="#F6C21C" stroke-width="4"/>')
    out.append(school_bus(D, 56, 452, 470, 420))
    # curb and grass foreground with the lunchbox, books, an apple, leaves
    out.append(painted(D, rect_pts(-10, 466, 610, 480, 30, 421, 0.3), ("#F2EEE6", "#C8C2B8", "#8A8478"), 421, sk=0.1, n=10, inkw=1.2, hi=0.3))
    out.append(hill(D, [(-20, 478), (300, 476), (620, 480)], 620, GRASS, 422, angle=-4, inkw=0))
    out.append(grass(423, (0, 480, 600, 600), ["#5A8A30", "#8AB850", "#2E5A1E"], 160, (8, 18)))
    out.append(lunchbox(D, 156, 566, 118, 76, 424))
    # strapped books
    bks = [(370, 570, 150, 22, ("#5A8AD0", "#22386A", "#0E1C3E")), (376, 548, 136, 22, ("#7AC08A", "#2E7A4A", "#14402A")), (366, 526, 144, 22, CHERRY)]
    out.append(cast(D, 376, 574, 90, 8, strength=0.5, seed=425))
    for k, (cx, by, w, h, pal) in enumerate(bks):
        out.append(painted(D, rect_pts(cx - w / 2, by - h, cx + w / 2, by, 12, 426 + k, 0.4), pal, 426 + k, sdir=(0, 1), sk=0.12, angle=0, n=8, inkw=1.6, hi=0.4))
        out.append(f'<path d="M {cx - w / 2 + 4} {by - h + 4} L {cx + w / 2 - 4} {by - h + 4}" stroke="#FFF6E8" stroke-width="1.6" opacity="0.6"/>')
    out.append(painted(D, rect_pts(326, 502, 342, 572, 6, 429, 0.3), LEATHER, 429, sk=0.1, n=4, inkw=1.2, hi=0.3))
    out.append(apple(D, 400, 488, 24, seed=430))
    rnd = random.Random(431)
    for k in range(7):
        from fall_gouache_a import leaf as fleaf
        x, y = rnd.uniform(70, 540), rnd.uniform(200, 590)
        if 250 < y < 470:
            continue
        out.append(fleaf(D, "maple", x, y, rnd.uniform(12, 16), rnd.choice(["red", "orange", "gold"]), rnd.uniform(0, 360), seed=432 + k))
    # lettering
    out.append(letters(D, 300, 122, "School Days", SERIF_IT, 90, "#B8352A", ["#D8503A", "#8A1E12", "#E8704A"], 433, max_w=420,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-40, hi="#FFC8A8"))
    out.append(ruled(300, 164, "DON'T MISS THE BUS!", "#22386A", font=JOS, size=21, ls=5, line_w=24, gap=12, max_w=330))
    return finish_a(D, out, 434)


# ================================================================ 16. pass the gravy — Thanksgiving at grandma's table
def taper_candle(D, x, base, h, seed, col=("#FFFCEA", "#F2E6C8", "#B8A47A")):
    out = [painted(D, rect_pts(x - 16, base - 10, x + 16, base, 6, seed, 0.3), MUSTARD, seed, sk=0.15, n=3, inkw=1.4, hi=0.5)]
    out.append(painted(D, pp([(x - 5, base - 10), (x + 5, base - 10), (x + 3, base - 30), (x - 3, base - 30)]), MUSTARD, seed + 1, sk=0.15, n=3, inkw=1.2, hi=0.5))
    out.append(f'<path d="{blob(x, base - 32, 11, 4, seed + 2, 0.05, 10)}" fill="{MUSTARD[1]}" stroke="{INK}" stroke-width="1"/>')
    out.append(painted(D, rect_pts(x - 6, base - 32 - h, x + 6, base - 32, 8, seed + 3, 0.3), col, seed + 3, sdir=(1, 0), sk=0.25, angle=-90, n=4, inkw=1.2, hi=0.5))
    fx, fy = x, base - 34 - h
    out.append(D.glow(fx, fy - 8, 80, "#FFC860", 0.45))
    f = [(fx, fy - 22), (fx + 5, fy - 10), (fx + 5, fy - 3), (fx, fy + 1), (fx - 5, fy - 3), (fx - 5, fy - 10)]
    out.append(f'<path d="{smooth_closed(f)}" fill="#FFB43A"/>')
    out.append(f'<path d="{smooth_closed([(fx, fy - 15), (fx + 2.6, fy - 7), (fx, fy - 2), (fx - 2.6, fy - 7)])}" fill="#FFF4C0"/>')
    return "".join(out)


def roast_turkey(D, cx, cy, s, seed):
    """Golden roast turkey on its back, drumsticks up and out with paper frills, glossy crackling skin."""
    rnd = random.Random(seed)
    SKIN = ("#F6C46A", "#C8782A", "#6A3410")
    out = [cast(D, cx + s * 0.05, cy + s * 0.42, s * 0.95, s * 0.2, strength=0.5, seed=seed)]
    # wings tucked low at the sides
    for sg in (-1, 1):
        w = blob_pts(cx + sg * s * 0.62, cy + s * 0.18, s * 0.24, s * 0.16, seed + sg, 0.08, 14, sg * 20)
        out.append(painted(D, w, (SKIN[0], dk(SKIN[1], 0.15), SKIN[2]), seed + 3 + sg, sk=0.2, n=8, inkw=1.6, hi=0.3))
    body = []
    for i in range(36):
        a = 2 * math.pi * i / 36
        k = 1 + 0.06 * math.cos(2 * a)
        body.append((cx + s * 0.72 * math.cos(a) * k, cy + s * 0.44 * math.sin(a) * (1.05 if math.sin(a) > 0 else 0.95)))
    out.append(painted(D, body, SKIN, seed, sdir=(0.5, 0.8), sk=0.2, angle=-20, n=int(s * 0.9), slen=(s * 0.08, s * 0.3), sw=(1.2, 3.4),
                       cols=["#FFE0A0", "#A8581A", "#E8A048", "#8A4010"], inkw=2, hi=0.45, curve=0.5))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    inner = [f'<path d="{blob(cx, cy - s * 0.06, s * 0.08, s * 0.38, seed + 5, 0.05, 12)}" fill="#7A3A10" opacity="0.18"/>']
    for sg in (-1, 1):
        inner.append(f'<path d="{blob(cx + sg * s * 0.26, cy - s * 0.12, s * 0.26, s * 0.2, seed + 6 + sg, 0.1, 12, sg * 15)}" fill="#FFE8B0" opacity="0.32"/>')
        inner.append(taper([(cx + sg * s * 0.36, cy - s * 0.26), (cx + sg * s * 0.18, cy - s * 0.3)], s * 0.05, s * 0.02, "#FFF8E0", 0.7))
    for _ in range(int(s * 0.5)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.9
        x, y = cx + math.cos(a) * s * 0.7 * rr, cy + math.sin(a) * s * 0.42 * rr
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.8, 2):.1f}" fill="{rnd.choice(["#7A3A10", "#FFF0C8", "#5A2A08"])}" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # drumsticks: plump clubs at the front, angled up and in, bone tips with paper frills
    for sg in (-1, 1):
        ax, ay = cx + sg * s * 0.34, cy + s * 0.3
        bx, by = cx + sg * s * 0.6, cy - s * 0.16
        ang = math.degrees(math.atan2(by - ay, bx - ax))
        mx, my = (ax + bx) / 2, (ay + by) / 2
        L = math.hypot(bx - ax, by - ay)
        club = []
        for k in range(28):
            t = 2 * math.pi * k / 28
            u = math.cos(t)
            w = 0.5 * (1 - 0.38 * u) * (0.36 * s)
            club.append((u * L * 0.55, math.sin(t) * w))
        club = [(mx + x * math.cos(math.radians(ang)) - y * math.sin(math.radians(ang)), my + x * math.sin(math.radians(ang)) + y * math.cos(math.radians(ang))) for x, y in club]
        club = [(x, y) for x, y in club]
        out.append(painted(D, club, SKIN, seed + 10 + sg, sdir=(sg * 0.6, 0.8), sk=0.22, angle=ang, n=int(s * 0.3), inkw=1.8, hi=0.45))
        tx, ty = bx + (bx - ax) / L * s * 0.04, by + (by - ay) / L * s * 0.04
        ex, ey = bx + (bx - ax) / L * s * 0.16, by + (by - ay) / L * s * 0.16
        out.append(taper([(tx, ty), (ex, ey)], s * 0.06, s * 0.05, "#F6EEDC"))
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{s * 0.04:.1f}" fill="#F6EEDC" stroke="{INK}" stroke-width="1"/>')
        fr = []
        nx_, ny_ = -(by - ay) / L, (bx - ax) / L
        ux_, uy_ = (bx - ax) / L, (by - ay) / L
        for k in range(9):
            t = k / 8 - 0.5
            dd = s * (0.07 if k % 2 == 0 else 0.03)
            fr.append((ex + nx_ * t * s * 0.14 + ux_ * dd, ey + ny_ * t * s * 0.14 + uy_ * dd))
        fr += [(ex - nx_ * 0.5 * s * 0.14 - ux_ * s * 0.02, ey - ny_ * 0.5 * s * 0.14 - uy_ * s * 0.02)][::-1]
        fr = [(ex + nx_ * (-0.5) * s * 0.14 - ux_ * s * 0.02, ey + ny_ * (-0.5) * s * 0.14 - uy_ * s * 0.02)] + fr + [(ex + nx_ * 0.5 * s * 0.14 - ux_ * s * 0.02, ey + ny_ * 0.5 * s * 0.14 - uy_ * s * 0.02)]
        out.append(f'<path d="{pd(fr)}" fill="#FFFFFF" stroke="{INK}" stroke-width="1.2"/>')
    return "".join(out)


def gravy_boat(D, cx, cy, s, seed):
    """Porcelain gravy boat on its saucer: spout to the right, looped handle left, glossy gravy, a ladle."""
    out = [cast(D, cx + s * 0.06, cy + s * 0.32, s * 0.95, s * 0.2, strength=0.5, seed=seed)]
    out.append(painted(D, ell_pts(cx, cy + s * 0.24, s * 0.9, s * 0.24, 0, 360, 36)[:-1], WHITE, seed, sdir=(0.3, 1), sk=0.1, angle=0, n=12, inkw=1.6, hi=0.4))
    out.append(ink(smooth_closed(ell_pts(cx, cy + s * 0.24, s * 0.8, s * 0.2, 0, 360, 36)[:-1]), "#2E5AA8", 2.2, seed, 1, 0.8))
    # handle (behind on the left)
    out.append(ink(f"M {cx - s * 0.48:.1f} {cy - s * 0.12:.1f} C {cx - s * 0.86:.1f} {cy - s * 0.3:.1f} {cx - s * 0.86:.1f} {cy + s * 0.14:.1f} {cx - s * 0.5:.1f} {cy + s * 0.12:.1f}", "#B8B0A6", s * 0.07, seed, 1, 1))
    out.append(ink(f"M {cx - s * 0.48:.1f} {cy - s * 0.12:.1f} C {cx - s * 0.86:.1f} {cy - s * 0.3:.1f} {cx - s * 0.86:.1f} {cy + s * 0.14:.1f} {cx - s * 0.5:.1f} {cy + s * 0.12:.1f}", "#FFFFFF", s * 0.03, seed + 1, 1, 0.8))
    body = [(cx - s * 0.55, cy - s * 0.14), (cx - s * 0.5, cy + s * 0.08), (cx - s * 0.3, cy + s * 0.2), (cx + s * 0.1, cy + s * 0.22), (cx + s * 0.4, cy + s * 0.12),
            (cx + s * 0.62, cy - s * 0.04), (cx + s * 0.8, cy - s * 0.22), (cx + s * 0.6, cy - s * 0.16), (cx + s * 0.2, cy - s * 0.16)]
    out.append(painted(D, body, WHITE, seed + 2, sdir=(0.5, 1), sk=0.15, angle=0, n=14, inkw=1.8, hi=0.5))
    out.append(pline([(cx - s * 0.5, cy - s * 0.02), (cx - s * 0.1, cy + s * 0.08), (cx + s * 0.4, cy + s * 0.02), (cx + s * 0.66, cy - s * 0.12)], "#2E5AA8", 2.4, seed + 3, 0.85, 1))
    top = [(cx - s * 0.55, cy - s * 0.14), (cx - s * 0.2, cy - s * 0.24), (cx + s * 0.3, cy - s * 0.24), (cx + s * 0.8, cy - s * 0.22), (cx + s * 0.4, cy - s * 0.08), (cx - s * 0.2, cy - s * 0.04)]
    out.append(f'<path d="{smooth_closed(top)}" fill="#F4F0E8" stroke="{INK}" stroke-width="1.4"/>')
    gr = [(cx - s * 0.48, cy - s * 0.14), (cx - s * 0.2, cy - s * 0.21), (cx + s * 0.3, cy - s * 0.21), (cx + s * 0.62, cy - s * 0.18), (cx + s * 0.36, cy - s * 0.1), (cx - s * 0.2, cy - s * 0.07)]
    out.append(f'<path d="{smooth_closed(gr)}" fill="{D.lin([(0, "#A8642A"), (1, "#5A2A0A")])}"/>')
    out.append(f'<path d="{blob(cx - s * 0.05, cy - s * 0.17, s * 0.2, s * 0.025, seed + 4, 0.2, 10)}" fill="#E8A868" opacity="0.7"/>')
    # ladle
    out.append(taper([(cx + s * 0.1, cy - s * 0.15), (cx + s * 0.02, cy - s * 0.5), (cx - s * 0.08, cy - s * 0.66)], s * 0.05, s * 0.06, "#C8D0DA"))
    out.append(taper([(cx + s * 0.08, cy - s * 0.18), (cx + s * 0.0, cy - s * 0.5)], s * 0.015, s * 0.015, "#FFFFFF", 0.8))
    out.append(taper([(cx + s * 0.62, cy - s * 0.14), (cx + s * 0.7, cy - s * 0.04), (cx + s * 0.66, cy + s * 0.08)], s * 0.05, s * 0.02, "#7A3A10", 0.9))
    out.append(steam(cx + s * 0.05, cy - s * 0.3, s * 0.4, seed + 5, "#FFFFFF", 2, s * 0.22, 6, 0.6))
    return "".join(out)


def cranberry_jelly(D, cx, base, w, h, seed):
    """Canned cranberry sauce, slid out whole: ridged ruby cylinder on a glass dish, one slice cut."""
    out = [cast(D, cx + 6, base + 4, w * 1.1, 10, strength=0.45, seed=seed)]
    out.append(painted(D, ell_pts(cx, base, w * 1.05, w * 0.26, 0, 360, 30)[:-1], ("#FFFFFF", "#D8E8F0", "#8AA8B8"), seed, sdir=(0.3, 1), sk=0.12, angle=0, n=10, inkw=1.4, hi=0.6))
    top = base - h
    body = ell_pts(cx, base - 4, w / 2, w * 0.12, 0, 180, 16) + ell_pts(cx, top, w / 2, w * 0.12, 180, 360, 16)
    out.append(painted(D, body, ("#F05A6A", "#B8142A", "#5A0410"), seed + 1, sdir=(0.9, 0.2), sk=0.25, angle=-90, n=10, inkw=1.6, hi=0.4))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    rid = []
    for k in range(1, 6):
        y = top + h * k / 6
        rid.append(pline(ell_pts(cx, y, w / 2, w * 0.12, 15, 165, 12), "#FF8A9A", 2, seed + k, 0.5, 1))
        rid.append(pline(ell_pts(cx, y + 3, w / 2, w * 0.12, 15, 165, 12), "#4A0010", 1.6, seed + k, 0.35, 1))
    out.append(f'<g {cid}>{"".join(rid)}</g>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, w / 2, w * 0.12, 0, 360, 20)[:-1])}" fill="#D8283A" stroke="{INK}" stroke-width="1.4"/>')
    out.append(f'<path d="{blob(cx - w * 0.12, top - 1, w * 0.14, w * 0.04, seed + 3, 0.2, 8)}" fill="#FFC8D0" opacity="0.7"/>')
    out.append(taper([(cx - w * 0.36, top + 8), (cx - w * 0.36, base - 10)], 4, 2, "#FFB8C0", 0.6))
    # a slice fallen to the side
    sx, sy = cx + w * 0.82, base - 8
    out.append(painted(D, blob_pts(sx, sy, w * 0.36, w * 0.14, seed + 4, 0.04, 16, -8), ("#F05A6A", "#C8203A", "#6A0614"), seed + 4, sk=0.2, n=4, inkw=1.4, hi=0.5))
    return "".join(out)


@design("pass-the-gravy")
def pass_the_gravy():
    D = Doc2("us-pg")
    # dining-room wall: deep green with a small gold print, warm candlelight
    out = [paper(D.nid(), "#2E4A3A", "#0E1E16", 441)]
    rnd = random.Random(442)
    for yy in range(0, 260, 34):
        for xx in range(0, 640, 34):
            x = xx + (17 if (yy // 34) % 2 else 0)
            out.append(f'<path d="{blob(x, yy, 3.4, 5, x + yy, 0.1, 8)}" fill="#C8A04A" opacity="0.35"/>')
    out.append(soft_glow(D, 300, 240, 300, "#FFC870", 0.45))
    out.append(painted(D, rect_pts(-10, 228, 610, 244, 30, 443, 0.3), WOOD, 443, sk=0.15, n=10, inkw=1.4, hi=0.3))
    # the table under a cream cloth with a plaid runner
    out.append(f'<rect y="244" width="600" height="356" fill="#F6EEDC"/>')
    out.append(strokes(D.nid(), "M 0 244 L 600 244 L 600 600 L 0 600 Z", (-40, 244, 600, 600), ["#FFFFFF", "#E2D6BE"], 444, n=60, angle=0, length=(40, 140), width=(2, 5)))
    run = pd([(-10, 270), (610, 262), (610, 380), (-10, 390)])
    out.append(gingham(D, run, "#C8682A", "#F2C870", 16))
    out.append(f'<path d="{run}" fill="{D.lin([(0, "#3A1A06", 0.2), (1, "#3A1A06", 0)])}"/>')
    out.append(ink(run, INK, 1.4, 445, 1, 0.4))
    out.append(f'<rect y="244" width="600" height="356" fill="{D.rad([(0, "#FFD890", 0.3), (1, "#FFD890", 0)], 0.5, 0.2, 0.7)}"/>')
    out.append(taper_candle(D, 70, 300, 110, 446))
    out.append(taper_candle(D, 530, 300, 110, 447))
    # the platter and the bird
    out.append(cast(D, 306, 384, 190, 26, strength=0.45, seed=448))
    out.append(painted(D, ell_pts(300, 352, 188, 62, 0, 360, 40)[:-1], WHITE, 449, sdir=(0.3, 1), sk=0.1, angle=0, n=16, inkw=1.8, hi=0.4))
    out.append(ink(smooth_closed(ell_pts(300, 352, 170, 54, 0, 360, 40)[:-1]), "#2E5AA8", 2.2, 450, 1, 0.75))
    for k in range(18):
        a = math.radians(k * 20)
        out.append(f'<path d="{blob(300 + 160 * math.cos(a), 352 + 48 * math.sin(a), 6, 3, 451 + k, 0.1, 8, k * 20)}" fill="#2E5AA8" opacity="0.6"/>')
    for k, (x, y) in enumerate(((160, 360), (190, 382), (420, 384), (448, 360), (300, 400))):
        for j in range(6):
            out.append(f'<path d="{blob(x + rnd.uniform(-10, 10), y + rnd.uniform(-6, 6), 7, 5, 460 + k * 7 + j, 0.2, 8)}" fill="{rnd.choice(["#4A8A3A", "#2E6A2A", "#6AAA4A"])}"/>')
        for j in range(3):
            out.append(f'<circle cx="{x + rnd.uniform(-12, 12):.1f}" cy="{y + rnd.uniform(-6, 6):.1f}" r="4" fill="#C8142A" stroke="#5A0010" stroke-width="0.8"/>')
    out.append(roast_turkey(D, 300, 316, 150, 470))
    # front: cranberry jelly and the gravy boat (and a fork)
    out.append(cranberry_jelly(D, 132, 520, 74, 72, 480))
    out.append(gravy_boat(D, 404, 498, 150, 481))
    out.append(taper([(560, 470), (548, 590)], 6, 7, "#C8D0DA"))
    for k in range(4):
        out.append(taper([(552 + k * 4, 470), (553 + k * 4, 440)], 2.2, 2, "#B8C0CA"))
    # lettering
    out.append(letters(D, 300, 116, "Pass the Gravy", SERIF_IT, 84, "#FFF2D8", ["#FFFFFF", "#FFE2C0", "#FFD0A0"], 482, max_w=440,
                       shadow="#0E1E16", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 164, "THANKSGIVING AT GRANDMA'S", "#F6C870", font=JOS, size=19, ls=4, line_w=20, gap=10, max_w=380))
    return finish_a(D, out, 483)


# ================================================================ 17. wicked good — Maine lobster roll on the dock
def lobster_roll(D, cx, cy, s, seed):
    """New England split-top roll, griddled golden, heaped with lobster in a little mayo, chives, lettuce."""
    rnd = random.Random(seed)
    out = [cast(D, cx + s * 0.05, cy + s * 0.32, s * 0.95, s * 0.14, strength=0.5, seed=seed)]
    # paper boat tray, red check
    tray = [(cx - s * 1.0, cy - s * 0.02), (cx + s * 1.0, cy - s * 0.1), (cx + s * 0.9, cy + s * 0.34), (cx - s * 0.9, cy + s * 0.4)]
    out.append(gingham(D, pd(tray), "#D8302A", "#FFFDF6", s * 0.12, -4))
    out.append(f'<path d="{pd(tray)}" fill="{D.lin([(0, "#3A0A06", 0.25), (1, "#3A0A06", 0)])}"/>')
    out.append(ink(pd(tray), INK, 1.6, seed, 1, 0.7))
    # split-top bun: soft pale crust edges, a golden griddled flank
    bun = rrect_pts(cx - s * 0.84, cy - s * 0.2, cx + s * 0.84, cy + s * 0.2, s * 0.14, 6)
    out.append(painted(D, bun, ("#FFF2D0", "#F2DAA0", "#B8925A"), seed + 1, sdir=(0, 1), sk=0.12, angle=0, n=20, inkw=1.8, hi=0.4))
    face = rrect_pts(cx - s * 0.78, cy - s * 0.12, cx + s * 0.78, cy + s * 0.15, s * 0.1, 6)
    fd = pd(face)
    out.append(f'<path d="{fd}" fill="{D.lin([(0, "#F2B860"), (0.5, "#D8902E"), (1, "#A8601A")])}"/>')
    cid = D.clip(f'<path d="{fd}"/>')
    g = []
    for _ in range(46):
        x, y = rnd.uniform(cx - s * 0.78, cx + s * 0.78), rnd.uniform(cy - s * 0.1, cy + s * 0.14)
        g.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(5, 14):.1f} {rnd.uniform(-1, 1):.1f}" stroke="{rnd.choice(["#8A4A10", "#FFE0A0"])}" stroke-width="1.3" opacity="0.45"/>')
    g.append(taper([(cx - s * 0.6, cy - s * 0.06), (cx + s * 0.5, cy - s * 0.08)], s * 0.04, s * 0.02, "#FFF4C8", 0.6))
    out.append(f'<g {cid}>{"".join(g)}</g>')
    out.append(ink(fd, "#8A5A1A", 1.2, seed, 1, 0.5))
    # lettuce frill along the opening
    for k in range(15):
        x = cx - s * 0.8 + k * s * 0.114
        out.append(f'<path d="{blob(x, cy - s * 0.22, s * 0.085, s * 0.05, seed + k, 0.3, 8)}" fill="{rnd.choice(["#8AC85A", "#6AAA3A", "#A8D870"])}" stroke="#3A6A1A" stroke-width="0.8"/>')
    # lobster heaped up: claw pieces and tail medallions, glossed with a little mayo
    chunks = []
    for k in range(17):
        x = cx + (-0.7 + 1.4 * k / 16 + rnd.uniform(-0.04, 0.04)) * s
        y = cy - s * 0.27 - rnd.uniform(0, 0.2) * s * (1 - abs(x - cx) / s * 0.8)
        chunks.append((y, x, k))
    for y, x, k in sorted(chunks):
        r = rnd.uniform(0.11, 0.15) * s
        a = rnd.uniform(-40, 40)
        if k % 3 == 0:   # claw: curved crescent, red-orange back, white belly
            cp = []
            for t in range(13):
                th = math.radians(200 + t * 11)
                cp.append((x + r * 1.3 * math.cos(th), y + r * 0.9 * math.sin(th)))
            for t in range(12, -1, -1):
                th = math.radians(200 + t * 11)
                cp.append((x + r * 0.7 * math.cos(th) + r * 0.2, y + r * 0.45 * math.sin(th) + r * 0.25))
            cp = rot(cp, x, y, a)
            dd = smooth_closed(cp)
            out.append(f'<path d="{dd}" fill="#FFF6EC"/>')
            cl = D.clip(f'<path d="{dd}"/>')
            out.append(f'<g {cl}><path d="{blob(x - r * 0.1, y - r * 0.5, r * 1.3, r * 0.55, rnd.randint(0, 999), 0.1, 10, a)}" fill="#E8402A"/>'
                       f'<path d="{blob(x - r * 0.3, y - r * 0.62, r * 0.6, r * 0.18, rnd.randint(0, 999), 0.1, 8, a)}" fill="#FF9A7A" opacity="0.8"/></g>')
            out.append(ink(dd, "#A83A1A", 1.1, k, 1, 0.6))
        else:            # tail medallion
            p = blob_pts(x, y, r, r * 0.82, rnd.randint(0, 999), 0.12, 12, a)
            dd = smooth_closed(p)
            out.append(f'<path d="{dd}" fill="#FFF4EA"/>')
            cl = D.clip(f'<path d="{dd}"/>')
            out.append(f'<g {cl}><path d="{blob(x, y - r * 0.55, r * 1.2, r * 0.5, rnd.randint(0, 999), 0.1, 10, a)}" fill="#F05A3A"/>'
                       f'<path d="M {x - r:.1f} {y - r * 0.1:.1f} Q {x:.1f} {y - r * 0.35:.1f} {x + r:.1f} {y - r * 0.1:.1f}" stroke="#FF8A6A" stroke-width="2" fill="none"/></g>')
            out.append(ink(dd, "#B8582A", 1.1, k, 1, 0.55))
        out.append(f'<path d="{blob(x + r * 0.3, y + r * 0.2, r * 0.3, r * 0.12, rnd.randint(0, 999), 0.2, 8)}" fill="#FFFFFF" opacity="0.75"/>')
    out.append(specks(seed + 5, (cx - s * 0.7, cy - s * 0.52, cx + s * 0.7, cy - s * 0.22), ["#2E7A2A", "#4AA040"], int(s * 0.45), (1.2, 2.2), (0.8, 1)))
    return "".join(out)


def buoy(D, x, y, L, seed, cols=(("#FFE07A", "#F6C21C", "#B8860A"), ("#FF8A7A", "#D8302A", "#821010"), WHITE)):
    out = [pline([(x, y - 30), (x, y)], "#C8A060", 2.4, seed, 1, 1)]
    pts = rect_pts(x - L * 0.16, y, x + L * 0.16, y + L, 8, seed, 0.3)
    d = smooth_closed(pts)
    out.append(f'<path d="{d}" fill="{cols[0][1]}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    b = [f'<rect x="{x - L * 0.2:.1f}" y="{y + L * (0.3 + k * 0.28):.1f}" width="{L * 0.4:.1f}" height="{L * 0.14:.1f}" fill="{cols[1 + k % 2][1]}"/>' for k in range(2)]
    b.append(f'<path d="{d}" fill="{D.lin([(0, "#FFFFFF", 0.4), (0.35, "#FFFFFF", 0), (1, "#2A0A04", 0.4)], 0, 0, 1, 0)}"/>')
    out.append(f'<g {cid}>{"".join(b)}</g>')
    out.append(ink(d, INK, 1.6, seed, 1, 0.75))
    out.append(taper([(x, y + L), (x, y + L * 1.25)], L * 0.08, L * 0.06, "#8A6A4A"))
    return "".join(out)


def lighthouse_small(D, cx, base, top, seed, w0=74, w1=44, bands=CHERRY):
    """summer_gouache.lighthouse, adapted: the little window sits at a fixed fraction of the tower height."""
    out = []
    # tower
    tower = [(cx - w0 / 2, base), (cx - w1 / 2, top + 40), (cx + w1 / 2, top + 40), (cx + w0 / 2, base)]
    tp = poly_pts(tower, 20, seed, 0.6)
    td = smooth_closed(tp)
    out.append(f'<path d="{td}" fill="#FFFFFF"/>')
    cid = D.clip(f'<path d="{td}"/>')
    st = []
    H = base - (top + 40)
    for k in range(5):
        if k % 2 == 0:
            y0 = top + 40 + H * k / 5
            y1 = top + 40 + H * (k + 1) / 5
            st.append(f'<path d="M {cx - 60} {y0 + 6:.1f} Q {cx} {y0 + 14:.1f} {cx + 60} {y0 + 6:.1f} L {cx + 60} {y1 + 6:.1f} Q {cx} {y1 + 14:.1f} {cx - 60} {y1 + 6:.1f} Z" fill="{bands[1]}"/>')
    st.append(f'<path d="{td}" fill="{D.lin([(0, "#FFFFFF", 0.3), (0.35, "#FFFFFF", 0), (0.7, "#3A1A2A", 0.12), (1, "#3A1A2A", 0.4)], 0, 0, 1, 0)}"/>')
    out.append(f'<g {cid}>{"".join(st)}</g>')
    out.append(strokes(D.nid(), td, (cx - w0, top, cx + w0, base), ["#FFFFFF", "#000000", bands[0]], seed, n=60, angle=-90, length=(10, 30), width=(1, 3), opacity=(0.08, 0.2)))
    out.append(ink(td, INK, 2.2, seed, 2, 0.8))
    # door & window
    out.append(painted(D, [(cx - 7, base), (cx - 7, base - 18), (cx, base - 24), (cx + 7, base - 18), (cx + 7, base)], NAVY, seed + 1, sk=0.2, n=3, inkw=1.4, hi=0.3))
    out.append(painted(D, rect_pts(cx - 4, top + 40 + (base - top - 40) * 0.35, cx + 4, top + 40 + (base - top - 40) * 0.35 + 12, 6, seed, 0.3), ("#FFF6C0", "#FFD23A", "#C88A12"), seed + 2, sk=0.1, n=2, inkw=1.2, hi=0.3))
    # gallery, lantern room, dome
    gal = rect_pts(cx - w1 / 2 - 12, top + 32, cx + w1 / 2 + 12, top + 42, 10, seed, 0.4)
    out.append(painted(D, gal, NAVY, seed + 3, sk=0.2, n=3, inkw=1.6, hi=0.3))
    for k in range(7):
        x = cx - w1 / 2 - 8 + k * (w1 + 16) / 6
        out.append(pline([(x, top + 32), (x, top + 18)], NAVY[2], 1.6, k, 0.9, 1))
    out.append(pline([(cx - w1 / 2 - 10, top + 18), (cx + w1 / 2 + 10, top + 18)], NAVY[2], 2, seed, 0.9, 1))
    out.append(soft_glow(D, cx, top + 6, 90, "#FFF2A0", 0.85))
    lr = rect_pts(cx - w1 / 2 + 4, top - 6, cx + w1 / 2 - 4, top + 32, 8, seed, 0.3)
    out.append(painted(D, lr, ("#FFFCE0", "#FFE27A", "#E8A020"), seed + 4, sk=0.2, n=4, inkw=1.6, hi=0.5))
    out.append(pline([(cx - 4, top - 6), (cx - 4, top + 32)], NAVY[2], 1.6, seed, 0.8, 1) + pline([(cx + 8, top - 6), (cx + 8, top + 32)], NAVY[2], 1.6, seed + 1, 0.8, 1))
    dome = [(cx - w1 / 2, top - 4), (cx - w1 / 2 + 6, top - 18), (cx, top - 30), (cx + w1 / 2 - 6, top - 18), (cx + w1 / 2, top - 4)]
    out.append(painted(D, dome, bands, seed + 5, sdir=(1, 0.3), sk=0.2, angle=-30, n=4, inkw=1.8, hi=0.4))
    out.append(pline([(cx, top - 30), (cx, top - 42)], INK, 2.4, seed, 1, 1) + f'<circle cx="{cx}" cy="{top - 44}" r="3" fill="{INK}"/>')
    return "".join(out)


def lobster(D, cx, cy, s, ang, seed):
    """A cooked Maine lobster seen from above, head toward `ang` (degrees, -90 = up): fanned tail, segmented
    shell, carapace with its spike, two big claws on jointed arms, legs and long antennae."""
    RED = ("#FF8A6A", "#D8382A", "#7A1010")
    out = [cast(D, cx + 6, cy + 8, s * 0.42, s * 0.3, strength=0.4, seed=seed)]
    rr = ang + 90

    def R(pts):
        return rot([(cx + x * s, cy + y * s) for x, y in pts], cx, cy, rr)
    for sg in (-1, 1):
        for k in range(4):
            y0 = -0.02 + k * 0.07
            out.append(pline(R([(sg * 0.08, y0), (sg * 0.2, y0 - 0.04), (sg * 0.27, y0 + 0.06)]), RED[2], max(1.6, s * 0.014), seed + k, 0.9, 1))
        out.append(pline(R([(sg * 0.03, -0.3), (sg * 0.2, -0.55), (sg * 0.42, -0.62), (sg * 0.6, -0.5)]), RED[2], max(1.2, s * 0.008), seed + sg, 0.8, 1))
    # tail fan and segments
    for k, a in enumerate((-36, -16, 0, 16, 36)):
        bl = R([(0, 0.6), (math.sin(math.radians(a)) * 0.12 - 0.04, 0.6 + math.cos(math.radians(a)) * 0.14), (math.sin(math.radians(a)) * 0.13, 0.6 + math.cos(math.radians(a)) * 0.18),
                (math.sin(math.radians(a)) * 0.12 + 0.04, 0.6 + math.cos(math.radians(a)) * 0.14)])
        out.append(painted(D, bl, RED, seed + 10 + k, sk=0.2, n=3, inkw=1.2, hi=0.4))
    for k in range(5):
        y = 0.2 + k * 0.08
        w = 0.15 - k * 0.012
        seg = R([(-w, y), (w, y), (w * 0.95, y + 0.1), (-w * 0.95, y + 0.1)])
        out.append(painted(D, pp(seg, 6, seed + 20 + k), RED, seed + 20 + k, sdir=(0.3, 1), sk=0.2, angle=rr, n=4, inkw=1.2, hi=0.45))
    # carapace and head
    car = R([(-0.16, 0.22), (-0.18, -0.02), (-0.14, -0.2), (-0.06, -0.3), (0, -0.36), (0.06, -0.3), (0.14, -0.2), (0.18, -0.02), (0.16, 0.22)])
    out.append(painted(D, car, RED, seed + 30, sdir=(0.5, 0.8), sk=0.2, angle=rr, n=14, inkw=1.6, hi=0.5))
    out.append(specks(seed + 31, bbox(car), ["#FFC8A8", "#8A1A10"], int(s * 0.3), (0.8, 1.6), (0.5, 0.9)))
    for sg in (-1, 1):
        ex, ey = R([(sg * 0.05, -0.3)])[0]
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{max(2, s * 0.018):.1f}" fill="#1A0A04"/>')
        # arm and claw
        arm = R([(sg * 0.12, -0.18), (sg * 0.24, -0.3), (sg * 0.26, -0.42)])
        out.append(taper(arm, s * 0.07, s * 0.06, RED[1]))
        out.append(taper(arm, s * 0.02, s * 0.02, RED[0], 0.7))
        claw = R([(sg * 0.2, -0.42), (sg * 0.34, -0.46), (sg * 0.36, -0.62), (sg * 0.3, -0.76), (sg * 0.2, -0.72), (sg * 0.16, -0.56)])
        out.append(painted(D, claw, RED, seed + 40 + sg, sdir=(0.5, 0.8), sk=0.2, angle=rr, n=10, inkw=1.6, hi=0.5))
        pin = R([(sg * 0.2, -0.7), (sg * 0.16, -0.82), (sg * 0.2, -0.86), (sg * 0.24, -0.74)])
        out.append(painted(D, pin, RED, seed + 44 + sg, sk=0.2, n=3, inkw=1.2, hi=0.5))
        out.append(specks(seed + 46 + sg, bbox(claw), ["#FFC8A8", "#8A1A10"], int(s * 0.12), (0.8, 1.6), (0.5, 0.9)))
    return "".join(out)


@design("wicked-good")
def wicked_good():
    D = Doc2("us-wg")
    out = [sky(D, [(0, "#6AA8E0"), (0.7, "#BFE0F4"), (1, "#E8F4F6")], 491, 330, ["#8AC0EC", "#E8F6FF"], 40)]
    out.append(puff_cloud(D, 470, 150, 130, 492, pal=("#FFFFFF", "#F6FAFF", "#C8D8EC")))
    # sea
    out.append(f'<rect y="300" width="600" height="160" fill="{D.lin([(0, "#3A7AB0"), (1, "#1E4A7A")])}"/>')
    rnd = random.Random(493)
    for _ in range(60):
        x, y = rnd.uniform(-10, 600), rnd.uniform(306, 440)
        L = rnd.uniform(10, 30) * (0.5 + (y - 300) / 200)
        out.append(f'<path d="M {x:.1f} {y:.1f} q {L / 2:.1f} -3 {L:.1f} 0" stroke="#FFFFFF" stroke-width="1.6" fill="none" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    # rocky point with pines and the lighthouse
    out.append(hill(D, [(-20, 314), (60, 296), (150, 290), (230, 304), (290, 330), (300, 340), (-20, 340)], 340, ("#9A9AA8", "#6A6A7A", "#3A3A48"), 494, inkw=1.4))
    for k, x in enumerate((26, 54, 200, 232)):
        out.append(hg.fir(D, x, 304 + (k % 2) * 4, 70 - k * 6, 34, 495 + k, cols=("#1E3A2A", "#2E5A3A", "#4A7A54")))
    out.append(lighthouse_small(D, 130, 298, 214, 499, w0=38, w1=24, bands=("#FF8A7A", "#D8302A", "#821010")))
    # a lobster boat on its mooring
    bx, by = 430, 352
    out.append(painted(D, pp([(bx - 60, by - 14), (bx + 54, by - 18), (bx + 70, by - 28), (bx + 44, by + 8), (bx - 54, by + 8)]), WHITE, 500, sk=0.15, n=8, inkw=1.6, hi=0.4))
    out.append(f'<path d="M {bx - 58} {by - 4} L {bx + 52} {by - 8}" stroke="#D8302A" stroke-width="3"/>')
    out.append(painted(D, rect_pts(bx + 2, by - 44, bx + 36, by - 16, 8, 501, 0.3), WHITE, 501, sk=0.15, n=4, inkw=1.4, hi=0.4))
    out.append(f'<rect x="{bx + 8}" y="{by - 38}" width="10" height="10" fill="#3A5068"/><rect x="{bx + 22}" y="{by - 38}" width="10" height="10" fill="#3A5068"/>')
    out.append(f'<path d="M {bx - 30} {by - 14} L {bx - 30} {by - 52}" stroke="#3A2418" stroke-width="2"/>')
    out.append(f'<path d="M {bx - 66} {by + 10} q 60 8 124 -2" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.6"/>')
    # the dock: weathered grey planks seen from above
    out.append(wood_planks(D, 440, 600, 502, ("#C8C0B4", "#9A9084", "#5A5248"), 4))
    out.append(f'<rect y="436" width="600" height="8" fill="#2A2420" opacity="0.5"/>')
    for x in (40, 560):
        out.append(painted(D, rect_pts(x - 14, 380, x + 14, 470, 10, 503 + x, 0.4), ("#B8B0A4", "#8A8074", "#4A4238"), 503 + x, sdir=(1, 0), sk=0.2, angle=-90, n=8, inkw=1.6, hi=0.3))
        out.append(f'<path d="{smooth_closed(ell_pts(x, 380, 14, 4, 0, 360, 12)[:-1])}" fill="#D8D0C4" stroke="{INK}" stroke-width="1.2"/>')
    # a coil of rope and buoys hung on the piling
    for k in range(4):
        out.append(ink(smooth_closed(ell_pts(84, 566, 46 - k * 10, 16 - k * 3.4, 0, 360, 20)[:-1]), "#C8A060", 6, 504 + k, 1, 1))
        out.append(ink(smooth_closed(ell_pts(84, 566, 46 - k * 10, 16 - k * 3.4, 0, 360, 20)[:-1]), "#8A6A3A", 1.2, 508 + k, 1, 0.7))
    out.append(buoy(D, 70, 400, 74, 512))
    out.append(buoy(D, 540, 404, 66, 513, cols=(("#9AD0F0", "#2E8AD0", "#14507A"), WHITE, ("#FFE07A", "#F6C21C", "#B8860A"))))
    # the roll, with lemon and chips
    out.append(lobster_roll(D, 264, 508, 160, 514))
    out.append(lobster(D, 478, 462, 128, -125, 523))
    out.append(citrus_slice(D, 132, 470, 22, 515, ("#FFF6B0", "#FFE24A", "#D8B010"), "#FFFCE8", ("#FFF07A", "#FFD21A", "#C89A0A")))
    for k in range(5):
        x, y = 112 + rnd.uniform(-16, 16), 512 + rnd.uniform(-10, 10)
        out.append(painted(D, blob_pts(x, y, 18, 12, 516 + k, 0.2, 12, rnd.uniform(0, 180)), ("#FFF0B0", "#F2C860", "#B8862A"), 516 + k, sk=0.2, n=4, inkw=1.2, hi=0.5))
    # lettering
    out.append(letters(D, 300, 120, "Wicked Good", SERIF_IT, 88, "#C8302A", ["#E04A3A", "#8A1A12"], 521, max_w=430,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-40, hi="#FFC8A8"))
    out.append(ruled(300, 162, "MAINE LOBSTER ROLL", "#1E3A6A", font=JOS, size=21, ls=6, line_w=24, gap=12, max_w=330))
    return finish_a(D, out, 522)


# ================================================================ 18. low & slow — Texas brisket on butcher paper (from above)
def brisket_slice(D, cx, cy, L, W, ang, seed):
    """One slice of smoked brisket lying flat: a peppery black bark rim, the pink smoke ring just inside it,
    rosy-brown meat with grain and a pale seam of rendered fat, a juicy sheen."""
    rnd = random.Random(seed)
    pts = rot(rrect_pts(cx - L / 2, cy - W / 2, cx + L / 2, cy + W / 2, W * 0.3, 5), cx, cy, ang)
    pts = jitter(pts, seed, 1.2)
    d = smooth_closed(pts)
    out = [cast(D, cx + 4, cy + 8, L * 0.55, W * 0.6, strength=0.35, seed=seed)]
    out.append(f'<path d="{d}" fill="{D.lin([(0, "#A8664A"), (1, "#7A4028")])}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    g = [f'<g transform="rotate({ang} {cx} {cy})">']
    g.append(f'<path d="M {cx - L * 0.1:.1f} {cy - W:.1f} Q {cx + L * 0.05:.1f} {cy:.1f} {cx - L * 0.08:.1f} {cy + W:.1f}" stroke="#F2D8BC" stroke-width="{W * 0.12:.1f}" fill="none" opacity="0.85"/>')
    for k in range(18):
        x = cx - L / 2 + k * L / 17 + rnd.uniform(-2, 2)
        g.append(f'<path d="M {x:.1f} {cy - W * 0.35:.1f} Q {x + 3:.1f} {cy:.1f} {x:.1f} {cy + W * 0.35:.1f}" stroke="#6A2A18" stroke-width="1.1" fill="none" opacity="0.45"/>')
    g.append(f'<path d="{blob(cx + L * 0.12, cy - W * 0.08, L * 0.22, W * 0.1, seed, 0.2, 10)}" fill="#FFE8D8" opacity="0.35"/>')
    g.append("</g>")
    g.append(f'<path d="{d}" fill="none" stroke="#C8564A" stroke-width="{W * 0.34:.1f}" opacity="0.55"/>')
    g.append(f'<path d="{d}" fill="none" stroke="#1A0A04" stroke-width="{W * 0.22:.1f}"/>')
    for _ in range(int(L * 0.7)):
        k = rnd.randrange(len(pts))
        x, y = pts[k]
        g.append(f'<circle cx="{x + rnd.uniform(-3, 3):.1f}" cy="{y + rnd.uniform(-3, 3):.1f}" r="{rnd.uniform(0.6, 1.5):.1f}" fill="{rnd.choice(["#000000", "#5A3A26", "#C8A888"])}" opacity="0.85"/>')
    out.append(f'<g {cid}>{"".join(g)}</g>')
    out.append(ink(d, "#0A0402", 1.6, seed, 1, 0.7))
    return "".join(out)


def pickle_chip(D, cx, cy, r, seed):
    out = [f'<path d="{blob(cx, cy, r, r * 0.95, seed, 0.05, 14)}" fill="#7A9A2A" stroke="#3A5010" stroke-width="1.4"/>']
    out.append(f'<path d="{blob(cx, cy, r * 0.72, r * 0.68, seed + 1, 0.05, 12)}" fill="#C8D86A"/>')
    rnd = random.Random(seed)
    for k in range(6):
        a = k * 1.05 + rnd.uniform(-0.2, 0.2)
        out.append(f'<path d="{blob(cx + math.cos(a) * r * 0.4, cy + math.sin(a) * r * 0.4, r * 0.12, r * 0.07, seed + k, 0.1, 6, math.degrees(a))}" fill="#F2F0C0"/>')
    out.append(f'<path d="{blob(cx - r * 0.3, cy - r * 0.35, r * 0.25, r * 0.1, seed + 9, 0.2, 8, -30)}" fill="#FFFFFF" opacity="0.6"/>')
    return "".join(out)


@design("low-and-slow")
def low_and_slow():
    D = Doc2("us-ls2")
    out = [wood_planks(D, 0, 600, 531, ("#6A4A32", "#4A3020", "#24160C"), 6, vertical=True)]
    out.append(soft_glow(D, 300, 380, 300, "#FFB060", 0.25))
    # smoke drifting across
    for k, (y, op) in enumerate(((200, 0.25), (240, 0.18))):
        out.append(taper([(-20, y + 20), (120, y - 10), (300, y + 14), (480, y - 8), (620, y + 10)], 30, 10, "#E8E0D8", op))
    # sheet tray lined with butcher paper
    tray = rect_pts(70, 214, 530, 566, 20, 532, 0.6)
    out.append(cast(D, 310, 580, 250, 22, strength=0.6, seed=533))
    out.append(painted(D, tray, CHROME, 533, sk=0.1, n=20, inkw=2, hi=0.5))
    paperp = rot(rect_pts(92, 226, 516, 552, 18, 534, 2.2), 304, 390, -3)
    out.append(painted(D, paperp, ("#F8D8C0", "#E8B898", "#A87A5A"), 534, sdir=(0.4, 1), sk=0.06, angle=10, n=50, slen=(30, 90), sw=(1, 3), inkw=1.4, hi=0.3))
    rnd = random.Random(535)
    for _ in range(9):
        x, y = rnd.uniform(110, 500), rnd.uniform(240, 540)
        out.append(pline([(x, y), (x + rnd.uniform(30, 70), y + rnd.uniform(-20, 20))], "#C8987A", 1.6, int(x), 0.5, 1))
    for _ in range(8):
        x, y = rnd.uniform(120, 500), rnd.uniform(250, 530)
        out.append(f'<path d="{blob(x, y, rnd.uniform(10, 24), rnd.uniform(6, 14), rnd.randint(0, 999), 0.3, 10)}" fill="#C8783A" opacity="0.2"/>')
    # brisket: a row of slices fanned, the uncut end beside them
    end = rot(rect_pts(132, 270, 252, 346, 12, 536, 1.8), 192, 308, -6)
    out.append(cast(D, 196, 318, 70, 44, strength=0.4, seed=536))
    out.append(f'<path d="{smooth_closed(end)}" fill="#1A0A04"/>')
    out.append(specks(537, (132, 266, 252, 350), ["#000000", "#4A3020", "#8A5A3A"], 120, (0.8, 2), (0.5, 0.9)))
    out.append(taper([(140, 286), (240, 276)], 6, 3, "#5A3A2A", 0.6))
    out.append(ink(smooth_closed(end), "#000000", 1.4, 538, 1, 0.5))
    face = rot(rrect_pts(232, 276, 258, 340, 6, 3), 192, 308, -6)
    out.append(f'<path d="{pd(face)}" fill="#9A5A40"/>')
    out.append(f'<path d="{pd(face)}" fill="none" stroke="#C8564A" stroke-width="6" opacity="0.6"/>')
    out.append(f'<path d="{pd(face)}" fill="none" stroke="#1A0A04" stroke-width="3"/>')
    for k in range(5):
        a_, b_ = rot([(236, 284 + k * 12), (254, 286 + k * 12)], 192, 308, -6)
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#6A2A18" stroke-width="1" opacity="0.5"/>')
    for k in range(6):
        out.append(brisket_slice(D, 384 + k * 8, 276 + k * 34, 168, 66, -8 + k * 1.5, 539 + k))
    # white bread, pickles, onions, jalapeños, a cup of sauce
    for k, (x, y, a) in enumerate(((180, 430, -12), (208, 452, 6))):
        pts = rot(rect_pts(x - 50, y - 46, x + 50, y + 46, 12, 545 + k, 1), x, y, a)
        out.append(painted(D, pts, ("#FFFFFF", "#F6F0E2", "#C8B898"), 545 + k, sdir=(0.4, 1), sk=0.1, angle=a, n=12, inkw=1.4, hi=0.3))
        out.append(ink(smooth_closed(rot(rect_pts(x - 46, y - 42, x + 46, y + 42, 12, 547 + k, 1), x, y, a)), "#C8A06A", 3, 547 + k, 1, 0.7))
    for k, (x, y) in enumerate(((330, 470), (360, 492), (300, 498), (340, 520), (380, 462))):
        out.append(pickle_chip(D, x, y, 15, 550 + k))
    for k, (x, y) in enumerate(((440, 480), (468, 500), (424, 514))):
        out.append(f'<path d="{blob(x, y, 20, 14, 556 + k, 0.05, 14)}" fill="none" stroke="#F8F4EE" stroke-width="6"/>')
        out.append(f'<path d="{blob(x, y, 20, 14, 556 + k, 0.05, 14)}" fill="none" stroke="#C8C0D8" stroke-width="1.2" opacity="0.7"/>')
    for k, (x, y) in enumerate(((140, 520), (164, 534), (118, 540))):
        out.append(f'<circle cx="{x}" cy="{y}" r="11" fill="#3E8A2E" stroke="#1E4A14" stroke-width="1.2"/><circle cx="{x}" cy="{y}" r="6.5" fill="#C8E08A"/>')
        for j in range(4):
            out.append(f'<circle cx="{x + math.cos(j * 1.6) * 3:.1f}" cy="{y + math.sin(j * 1.6) * 3:.1f}" r="1.2" fill="#FFFFFF"/>')
    sx, sy = 470, 260
    out.append(cast(D, sx + 4, sy + 30, 46, 16, strength=0.5, seed=560))
    out.append(painted(D, blob_pts(sx, sy, 40, 34, 561, 0.02, 24), WHITE, 561, sk=0.12, n=8, inkw=1.6, hi=0.5))
    out.append(f'<path d="{blob(sx, sy + 2, 32, 26, 562, 0.03, 20)}" fill="{D.rad([(0, "#C8402A"), (1, "#6A1408")], 0.4, 0.4, 0.7)}"/>')
    out.append(f'<path d="{blob(sx - 10, sy - 8, 10, 4, 563, 0.2, 8, -30)}" fill="#FFB8A0" opacity="0.6"/>')
    # lettering on the wood above
    out.append(letters(D, 300, 128, "Low & Slow", SERIF_IT, 100, "#FFF2D8", ["#FFFFFF", "#FFE2C0", "#FFD0A0"], 564, max_w=440,
                       shadow="#120804", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 180, "TEXAS BARBECUE", "#F6A84A", font=JOS, size=22, ls=7, line_w=26, gap=12, max_w=320))
    return finish_a(D, out, 565)


# ================================================================ 19. hot dog! — the corner cart in New York
def hot_dog(D, cx, cy, s, seed, ang=-6):
    """A frank in a soft bun: mustard zigzag, onions in red sauce, on a paper tray."""
    rnd = random.Random(seed)
    out = [cast(D, cx + s * 0.04, cy + s * 0.3, s * 0.95, s * 0.12, strength=0.5, seed=seed)]
    tray = rot(rrect_pts(cx - s * 0.92, cy - s * 0.12, cx + s * 0.92, cy + s * 0.3, s * 0.1, 5), cx, cy, ang)
    out.append(painted(D, tray, ("#FFFFFF", "#F2EEE6", "#B8B0A4"), seed, sdir=(0.3, 1), sk=0.1, angle=ang, n=12, inkw=1.6, hi=0.4))
    for k in range(-6, 7):
        a, b = rot([(cx + k * s * 0.13, cy - s * 0.1), (cx + k * s * 0.13, cy + s * 0.28)], cx, cy, ang)
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#C8C0B4" stroke-width="1.2" opacity="0.6"/>')
    # back half of the bun
    back = rot(rrect_pts(cx - s * 0.74, cy - s * 0.2, cx + s * 0.74, cy + s * 0.02, s * 0.1, 5), cx, cy, ang)
    out.append(painted(D, back, ("#FCE0A0", "#E8A84A", "#A8661E"), seed + 1, sdir=(0, 1), sk=0.12, angle=ang, n=14, inkw=1.6, hi=0.4))
    # the frank, poking out at both ends
    fr = rot(rrect_pts(cx - s * 0.86, cy - s * 0.1, cx + s * 0.86, cy + s * 0.06, s * 0.08, 6), cx, cy, ang)
    out.append(painted(D, fr, ("#F0886A", "#B8442A", "#6A1A0E"), seed + 2, sdir=(0, 1), sk=0.2, angle=ang, n=12, inkw=1.6, hi=0.5))
    out.append(taper(rot([(cx - s * 0.8, cy - s * 0.06), (cx + s * 0.8, cy - s * 0.07)], cx, cy, ang), s * 0.03, s * 0.02, "#FFC8B0", 0.7))
    # onions in sauce and mustard
    for _ in range(18):
        x, y = rot([(cx + rnd.uniform(-0.6, 0.6) * s, cy - s * rnd.uniform(0.07, 0.13))], cx, cy, ang)[0]
        out.append(f'<path d="{blob(x, y, s * 0.04, s * 0.022, rnd.randint(0, 999), 0.3, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#C8442A", "#E8783A", "#A8301A"])}" stroke="#6A1A0A" stroke-width="0.6"/>')
    zz = []
    for k in range(15):
        t = -0.7 + 1.4 * k / 14
        zz.append((cx + t * s, cy - s * (0.04 if k % 2 else 0.14)))
    out.append(taper(rot(zz, cx, cy, ang), s * 0.035, s * 0.03, "#F6C21C"))
    out.append(taper(rot([(x - 1, y - 1.5) for x, y in zz], cx, cy, ang), s * 0.01, s * 0.008, "#FFF0A0", 0.9))
    # front half of the bun
    front = rot(rrect_pts(cx - s * 0.76, cy - s * 0.02, cx + s * 0.76, cy + s * 0.18, s * 0.1, 5), cx, cy, ang)
    out.append(painted(D, front, ("#FFE6A8", "#F0B860", "#B8762A"), seed + 3, sdir=(0, 1), sk=0.15, angle=ang, n=16, inkw=1.8, hi=0.5))
    out.append(taper(rot([(cx - s * 0.6, cy + s * 0.02), (cx + s * 0.5, cy + s * 0.01)], cx, cy, ang), s * 0.03, s * 0.015, "#FFF6D8", 0.8))
    return "".join(out)


def brownstone(D, x0, x1, top, base, seed, wall=("#B8846A", "#8A5A44", "#4A2A1E"), lit=0.5):
    rnd = random.Random(seed)
    w = x1 - x0
    out = [painted(D, rect_pts(x0, top, x1, base, 24, seed, 0.4), wall, seed, sk=0.08, angle=-90, n=int(w * (base - top) / 300), inkw=1.4, hi=0.2)]
    out.append(painted(D, rect_pts(x0 - 4, top - 6, x1 + 4, top + 10, 20, seed + 1, 0.3), (lt(wall[1], 0.2), dk(wall[1], 0.2), wall[2]), seed + 1, sk=0.2, n=6, inkw=1.4, hi=0.3))
    rows = int((base - top - 40) / 64)
    for r in range(rows):
        for c in range(3):
            wx = x0 + w * (0.12 + c * 0.3)
            wy = top + 26 + r * 64
            g = "#FFD880" if rnd.random() < lit else "#4A5A72"
            out.append(f'<path d="{hg.org_rect(wx - 3, wy - 6, w * 0.18 + 6, 44, seed + r * 7 + c, 0.3, 8, 2)}" fill="{lt(wall[1], 0.35)}"/>')
            out.append(f'<path d="{hg.org_rect(wx, wy, w * 0.18, 36, seed + r * 9 + c, 0.3, 8, 1)}" fill="{D.lin([(0, lt(g, 0.3)), (1, dk(g, 0.2))])}"/>')
            out.append(f'<path d="M {wx + w * 0.09:.1f} {wy} L {wx + w * 0.09:.1f} {wy + 36}" stroke="{lt(wall[1], 0.4)}" stroke-width="2"/>')
        # fire escape across the middle bays
        fy = top + 70 + r * 64
        out.append(f'<path d="M {x0 + w * 0.36:.1f} {fy} L {x0 + w * 0.68:.1f} {fy}" stroke="#1E1E24" stroke-width="3"/>')
        for k in range(9):
            xx = x0 + w * 0.36 + k * w * 0.04
            out.append(f'<path d="M {xx:.1f} {fy} L {xx:.1f} {fy - 14}" stroke="#1E1E24" stroke-width="1.2"/>')
        out.append(f'<path d="M {x0 + w * 0.36:.1f} {fy - 14} L {x0 + w * 0.68:.1f} {fy - 14}" stroke="#1E1E24" stroke-width="1.6"/>')
        if r < rows - 1:
            out.append(f'<path d="M {x0 + w * 0.4:.1f} {fy} L {x0 + w * 0.62:.1f} {fy + 50}" stroke="#1E1E24" stroke-width="1.6"/>')
    return "".join(out)


@design("hot-dog")
def hot_dog_cart():
    D = Doc2("us-hd")
    out = [sky(D, [(0, "#8AB8E0"), (1, "#E8E0D0")], 571, 420, ["#A8C8E8"], 20)]
    out.append(brownstone(D, -20, 210, 206, 430, 572))
    out.append(brownstone(D, 210, 420, 186, 430, 573, wall=("#C89A7A", "#9A6A50", "#5A3424")))
    out.append(brownstone(D, 420, 620, 214, 430, 574, wall=("#A87A6A", "#7A4A3E", "#3E2018")))
    out.append(f'<rect y="120" width="600" height="320" fill="{D.lin([(0, "#FFF6E0", 0.0), (1, "#FFF6E0", 0.25)])}"/>')
    # sidewalk and curb
    out.append(painted(D, rect_pts(-10, 424, 610, 600, 30, 575, 0.4), ("#D8D2C8", "#B8B0A4", "#7A7468"), 575, sdir=(0, 1), sk=0.05, angle=0, n=40, inkw=0, hi=0.2))
    for x in range(-10, 620, 80):
        out.append(f'<path d="M {x} 424 L {x - 30} 600" stroke="#9A9286" stroke-width="1.6"/>')
    # the cart: umbrella, stainless box, wheels, steam
    cx = 300
    out.append(f'<path d="M {cx} 420 L {cx} 214" stroke="#5A5A64" stroke-width="5"/>')
    um = [(cx - 170, 274)] + [(cx + 170 * math.cos(math.radians(a)), 274 - 86 * math.sin(math.radians(a))) for a in range(180, -1, -10)][1:]
    out.append(cast(D, cx, 300, 150, 16, strength=0.25, seed=576))
    out.append(f'<path d="{pd(um)}" fill="#F6C21C"/>')
    cid = D.clip(f'<path d="{pd(um)}"/>')
    st = []
    for k in range(8):
        a0, a1 = 180 - k * 22.5, 180 - (k + 1) * 22.5
        if k % 2 == 0:
            p0 = (cx + 170 * math.cos(math.radians(a0)), 274 - 86 * math.sin(math.radians(a0)))
            p1 = (cx + 170 * math.cos(math.radians(a1)), 274 - 86 * math.sin(math.radians(a1)))
            st.append(f'<path d="M {cx} 188 L {p0[0]:.1f} {p0[1]:.1f} L {p1[0]:.1f} {p1[1]:.1f} Z" fill="#2E5AA8"/>')
    st.append(f'<path d="{pd(um)}" fill="{D.lin([(0, "#FFFFFF", 0.3), (0.5, "#FFFFFF", 0), (1, "#0A1030", 0.35)], 0, 0, 1, 0)}"/>')
    out.append(f'<g {cid}>{"".join(st)}</g>')
    for k in range(8):
        x0_, x1_ = cx - 170 + k * 42.5, cx - 170 + (k + 1) * 42.5
        out.append(f'<path d="M {x0_:.1f} 274 Q {(x0_ + x1_) / 2:.1f} 288 {x1_:.1f} 274 Z" fill="{"#F6C21C" if k % 2 else "#2E5AA8"}" stroke="{INK}" stroke-width="1"/>')
    out.append(ink(pd(um), INK, 1.8, 577, 2, 0.75))
    out.append(f'<circle cx="{cx}" cy="186" r="5" fill="#C8D0DA" stroke="{INK}" stroke-width="1.2"/>')
    box = (cx - 120, 330, cx + 120, 446)
    out.append(fluted(D, pd(rect_pts(*box, 20, 578, 0.3)), box, 578, top="#E8EEF6", mid="#FFFFFF", bot="#6A7280", step=8))
    out.append(ink(pd(rect_pts(*box, 20, 578, 0.3)), "#3A3A44", 1.8, 579, 1, 0.8))
    out.append(painted(D, rect_pts(cx - 128, 318, cx + 128, 334, 20, 580, 0.3), CHROME, 580, sk=0.15, n=8, inkw=1.6, hi=0.5))
    out.append(painted(D, rect_pts(cx - 100, 360, cx + 100, 404, 16, 581, 0.3), ("#FF8A7A", "#D8302A", "#7A1010"), 581, sk=0.1, n=8, inkw=1.6, hi=0.4))
    out.append(label(cx, 380, "HOT DOGS", BEBAS, 26, "#FFFFFF", ls=4, max_w=180))
    out.append(label(cx, 399, "PRETZELS · SODA", JOS, 13, "#FFE8C8", ls=2, max_w=170))
    for sx, col, cap in ((cx - 70, "#F6C21C", "#E8302A"), (cx - 46, "#D8302A", "#FFFFFF")):
        out.append(painted(D, rect_pts(sx - 9, 282, sx + 9, 320, 6, int(sx), 0.3), (lt(col, 0.3), col, dk(col, 0.35)), int(sx), sdir=(1, 0), sk=0.25, angle=-90, n=4, inkw=1.4, hi=0.5))
        out.append(f'<path d="M {sx - 5} 282 L {sx} 266 L {sx + 5} 282 Z" fill="{cap}" stroke="{INK}" stroke-width="1"/>')
    for k, x in enumerate((cx + 20, cx + 70)):
        out.append(f'<path d="{hg.org_rect(x - 22, 306, 44, 14, 582 + k, 0.3, 6, 3)}" fill="#C8D0DA" stroke="#3A3A44" stroke-width="1.2"/>')
        out.append(steam(x, 300, 50, 584 + k, "#FFFFFF", 2, 18, 6, 0.6))
    for wx in (cx - 84, cx + 84):
        out.append(f'<circle cx="{wx}" cy="452" r="22" fill="#26242C"/><circle cx="{wx}" cy="452" r="11" fill="#C8D0DA"/><circle cx="{wx}" cy="452" r="4" fill="#5E6878"/>')
    out.append(cast(D, cx, 474, 160, 10, strength=0.4, seed=586))
    # pigeons on the curb
    for k, (px, f) in enumerate(((102, 1), (520, -1))):
        out.append(painted(D, blob_pts(px, 470, 16, 10, 587 + k, 0.05, 12), ("#B8B8C8", "#7A7A8E", "#3E3E50"), 587 + k, sk=0.2, n=4, inkw=1.2, hi=0.3))
        out.append(f'<circle cx="{px + f * 14}" cy="458" r="7" fill="#6A6A80"/><path d="M {px + f * 20} 458 l {f * 6} 2 l {-f * 6} 2 Z" fill="#E8A83A"/>'
                   f'<path d="{blob(px + f * 10, 466, 5, 3, 589 + k, 0.1, 8)}" fill="#5AA88A" opacity="0.8"/>'
                   f'<path d="M {px - 2} 480 l -2 6 M {px + 4} 480 l 2 6" stroke="#E86A5A" stroke-width="2"/>')
    # the hot dog, close up
    out.append(hot_dog(D, 300, 520, 200, 590))
    # lettering
    out.append(letters(D, 300, 132, "Hot Dog!", SERIF_IT, 96, "#D8302A", ["#E84A3A", "#9A1A12"], 591, max_w=400,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-40, hi="#FFC8A8"))
    out.append(ruled(300, 174, "ONE WITH EVERYTHING", "#22386A", font=JOS, size=21, ls=6, line_w=22, gap=12, max_w=340))
    return finish_a(D, out, 592)


# ================================================================ 20. deep dish — Chicago, a slice pulled from the pan
def deep_dish_pan(D, cx, cy, rx, ry, depth, seed):
    """Deep-dish pizza in its dark pan, a wedge already served: chunky sauce on top; the cut faces show
    the tall golden crust, a thick layer of mozzarella and a sausage patty."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 10, cy + depth + ry * 0.4, rx * 1.1, ry * 0.45, strength=0.55, seed=seed)]
    side = ell_pts(cx, cy + depth, rx, ry, 0, 180, 30) + ell_pts(cx, cy, rx, ry, 180, 0, 30)
    out.append(painted(D, side, IRON, seed, sdir=(0.5, 1), sk=0.1, angle=0, n=20, inkw=2, hi=0.3))
    out.append(taper(ell_pts(cx, cy + depth * 0.5, rx - 2, ry, 20, 160, 14), 2.2, 2.2, "#8A8890", 0.6))
    # crust rim and sauce top
    out.append(painted(D, ell_pts(cx, cy, rx * 0.98, ry * 0.97, 0, 360, 40)[:-1], CRUST, seed + 1, sk=0.12, angle=0, n=24, inkw=1.6, hi=0.4))
    top = blob(cx, cy, rx * 0.88, ry * 0.84, seed + 2, 0.02, 36)
    out.append(f'<path d="{top}" fill="#B8281A"/>')
    cid = D.clip(f'<path d="{top}"/>')
    t = []
    for _ in range(int(rx * 1.4)):
        x, y = cx + rnd.uniform(-1, 1) * rx * 0.86, cy + rnd.uniform(-1, 1) * ry * 0.82
        t.append(f'<path d="{blob(x, y, rnd.uniform(3, 8), rnd.uniform(2, 5), rnd.randint(0, 9999), 0.3, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#D8402A", "#8A1A10", "#E8603A", "#A82A1A"])}"/>')
    t.append(specks(seed + 3, (cx - rx, cy - ry, cx + rx, cy + ry), ["#FFF8E0", "#E8E0B0", "#3E6A2A"], int(rx * 0.8), (0.8, 1.8), (0.6, 0.95)))
    t.append(f'<path d="{blob(cx - rx * 0.3, cy - ry * 0.4, rx * 0.3, ry * 0.12, seed + 4, 0.2, 10)}" fill="#FFFFFF" opacity="0.18"/>')
    out.append(f'<g {cid}>{"".join(t)}</g>')
    # the missing wedge toward the viewer
    a1, a2 = 96, 140
    p1 = (cx + rx * 0.98 * math.cos(math.radians(a1)), cy + ry * 0.97 * math.sin(math.radians(a1)))
    p2 = (cx + rx * 0.98 * math.cos(math.radians(a2)), cy + ry * 0.97 * math.sin(math.radians(a2)))
    c = (cx, cy)
    hole = [c, p1] + ell_pts(cx, cy, rx * 0.98, ry * 0.97, a1, a2, 6)[1:-1] + [p2]
    out.append(f'<path d="{pd([(x, y + depth * 0.85) for x, y in hole])}" fill="#141218"/>')
    out.append(f'<path d="{pd(hole)}" fill="#1A1418" opacity="0.85"/>')
    for (a, b) in ((c, p1), (c, p2)):
        face = [a, b, (b[0], b[1] + depth * 0.85), (a[0], a[1] + depth * 0.85)]
        fd = pd(face)
        out.append(f'<path d="{fd}" fill="#E8B060"/>')
        cl = D.clip(f'<path d="{fd}"/>')
        h = depth * 0.85
        bands = [(0, 0.22, "#C8301E"), (0.22, 0.6, "#FFF0C8"), (0.42, 0.56, "#7A3A22"), (0.6, 1, "#E8B060")]
        # the bands follow the slope of the cut line
        g = []
        for y0, y1, col in bands:
            g.append(f'<path d="M {a[0]:.1f} {a[1] + h * y0:.1f} L {b[0]:.1f} {b[1] + h * y0:.1f} L {b[0]:.1f} {b[1] + h * y1:.1f} L {a[0]:.1f} {a[1] + h * y1:.1f} Z" fill="{col}"/>')
        g.append(f'<path d="{fd}" fill="#1A0A04" opacity="{0.25 if b == p1 else 0.05}"/>')
        out.append(f'<g {cl}>{"".join(g)}</g>')
        out.append(ink(fd, INK, 1.2, seed, 1, 0.6))
    # front pan wall drawn again over the hole
    front = ell_pts(cx, cy + depth, rx, ry, a1 - 6, a2 + 6, 10) + ell_pts(cx, cy + depth * 0.15, rx, ry, a2 + 6, a1 - 6, 10)
    out.append(painted(D, front, IRON, seed + 6, sdir=(0.5, 1), sk=0.1, angle=0, n=8, inkw=1.6, hi=0.3))
    return "".join(out)


def pizza_slice_side(D, cx, cy, s, seed, ang=0):
    """A deep-dish wedge on its plate, tip toward the viewer: chunky sauce on top, a thick seam of melted
    mozzarella with sausage, a thin golden bottom crust and the tall crust wall at the back."""
    rnd = random.Random(seed)
    out = []
    tip = (cx, cy + s * 0.2)
    bl, br = (cx - s * 0.6, cy - s * 0.12), (cx + s * 0.6, cy - s * 0.16)
    h = s * 0.26
    for (a, b, sh) in ((tip, bl, 0.0), (tip, br, 0.2)):
        face = [a, b, (b[0], b[1] - h), (a[0], a[1] - h)]
        fd = pd(face)
        out.append(f'<path d="{fd}" fill="#FFF0C0"/>')
        cl = D.clip(f'<path d="{fd}"/>')
        g = []

        def band(y0, y1, col):
            return f'<path d="M {a[0]:.1f} {a[1] - h + h * y0:.1f} L {b[0]:.1f} {b[1] - h + h * y0:.1f} L {b[0]:.1f} {b[1] - h + h * y1:.1f} L {a[0]:.1f} {a[1] - h + h * y1:.1f} Z" fill="{col}"/>'
        g.append(band(0, 0.34, "#B8281A"))
        g.append(band(0.34, 0.8, "#FFF2C8"))
        g.append(band(0.8, 1.02, "#E2A852"))
        for _ in range(16):
            t = rnd.uniform(0.05, 0.95)
            px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t - h
            g.append(f'<path d="{blob(px, py + h * rnd.uniform(0.05, 0.3), s * 0.03, s * 0.02, rnd.randint(0, 999), 0.3, 8)}" fill="{rnd.choice(["#E8483A", "#7A140A"])}"/>')
            g.append(f'<path d="{blob(px, py + h * rnd.uniform(0.5, 0.7), s * 0.03, s * 0.018, rnd.randint(0, 999), 0.3, 8)}" fill="#8A4A2A" opacity="0.9"/>')
            g.append(f'<path d="M {px:.1f} {py + h * 0.36:.1f} l 0 {h * rnd.uniform(0.1, 0.3):.1f}" stroke="#FFFFFF" stroke-width="1.6" opacity="0.7"/>')
        g.append(f'<path d="{fd}" fill="#1A0A04" opacity="{sh}"/>')
        out.append(f'<g {cl}>{"".join(g)}</g>')
        out.append(ink(fd, INK, 1.4, seed, 1, 0.65))
    topf = [(tip[0], tip[1] - h), (bl[0], bl[1] - h), (cx - s * 0.3, cy - s * 0.3 - h), (cx + s * 0.3, cy - s * 0.32 - h), (br[0], br[1] - h)]
    out.append(f'<path d="{smooth_closed(topf)}" fill="#B8281A"/>')
    cl = D.clip(f'<path d="{smooth_closed(topf)}"/>')
    t = [f'<path d="{blob(rnd.uniform(cx - s * 0.45, cx + s * 0.45), rnd.uniform(cy - s * 0.32 - h, cy + s * 0.1 - h), rnd.uniform(3, 7), rnd.uniform(2, 4), rnd.randint(0, 999), 0.3, 8)}" fill="{rnd.choice(["#D8402A", "#8A1A10", "#E8603A"])}"/>' for _ in range(50)]
    t.append(specks(seed + 1, (cx - s * 0.6, cy - s * 0.4 - h, cx + s * 0.6, cy - h), ["#FFF8E0", "#3E6A2A"], 50, (0.8, 1.8), (0.7, 1)))
    out.append(f'<g {cl}>{"".join(t)}</g>')
    out.append(ink(smooth_closed(topf), INK, 1.4, seed + 1, 1, 0.6))
    # the tall crust wall at the back
    back = [(bl[0] - 2, bl[1] - h + 2), (cx - s * 0.3, cy - s * 0.3 - h - 2), (cx + s * 0.3, cy - s * 0.32 - h - 2), (br[0] + 2, br[1] - h + 2)]
    out.append(taper(back, s * 0.08, s * 0.08, "#E2A852"))
    out.append(taper([(x, y - s * 0.025) for x, y in back], s * 0.035, s * 0.035, "#F6D08A"))
    out.append(pline([(x, y - s * 0.05) for x, y in back], "#9A5A1A", 1.4, seed + 3, 0.7, 1))
    return "".join(out)


@design("deep-dish")
def deep_dish():
    D = Doc2("us-dd")
    # brick wall of the pizzeria and a warm pendant light
    out = [f'<rect width="600" height="600" fill="#8A3A2A"/>']
    rnd = random.Random(601)
    for j, y in enumerate(range(-6, 300, 22)):
        for x in range(-40 + (0 if j % 2 else 24), 640, 48):
            c = mix("#A8483A", rnd.choice(["#7A2A1E", "#C0604A", "#9A3A2A"]), rnd.uniform(0.2, 0.6))
            out.append(f'<path d="{hg.org_rect(x, y, 44, 18, x * 7 + y, 0.5, 8, 2)}" fill="{c}"/>')
    out.append(f'<rect width="600" height="300" fill="{D.rad([(0, "#FFD890", 0.45), (1, "#1A0806", 0.35)], 0.5, 0.15, 0.75)}"/>')
    out.append(f'<path d="M 300 0 L 300 30" stroke="#1A1A1A" stroke-width="2"/>')
    out.append(f'<path d="M 270 46 Q 300 18 330 46 Z" fill="#2E6A3A" stroke="#14301A" stroke-width="1.6"/>')
    out.append(D.glow(300, 50, 90, "#FFE8A0", 0.6))
    # table with a red-check cloth
    out.append(wood_planks(D, 286, 600, 602, WOOD, 4))
    tc = pp([(-20, 312), (620, 300), (620, 640), (-20, 640)], 20, 603)
    out.append(cloth(D, tc, "#C8302A", 603, cell=22, rot_=0, light=(0, 0, 0, 1)))
    out.append(deep_dish_pan(D, 334, 352, 186, 60, 54, 604))
    # the served slice on a plate, cheese stretching back to the pan
    out.append(cast(D, 222, 560, 150, 18, strength=0.5, seed=605))
    out.append(painted(D, ell_pts(214, 536, 150, 42, 0, 360, 36)[:-1], WHITE, 606, sdir=(0.3, 1), sk=0.1, angle=0, n=12, inkw=1.6, hi=0.4))
    out.append(ink(smooth_closed(ell_pts(214, 536, 132, 34, 0, 360, 36)[:-1]), "#C8302A", 2.2, 607, 1, 0.7))
    out.append(pizza_slice_side(D, 214, 520, 168, 608))
    for k, (a, b) in enumerate((((270, 452), (300, 410)), ((250, 452), (286, 414)), ((290, 456), (312, 418)))):
        m = ((a[0] + b[0]) / 2 + 6, (a[1] + b[1]) / 2 + 6)
        out.append(taper([a, m, b], 4.5 - k, 3, "#FFF2C8", 0.95))
        out.append(taper([(a[0] + 1.5, a[1]), (m[0] + 1.5, m[1]), (b[0] + 1.5, b[1])], 1.2, 1, "#E8C890", 0.8))
    # parmesan shaker and chili flakes
    sx = 496
    out.append(painted(D, rect_pts(sx - 22, 452, sx + 22, 520, 10, 609, 0.3), ("#F4FAFC", "#D8E4EA", "#8AA0AE"), 609, sk=0.2, n=6, inkw=1.6, hi=0.5))
    out.append(f'<rect x="{sx - 20}" y="470" width="40" height="48" fill="#F6F0DC" opacity="0.8"/>')
    out.append(painted(D, pp([(sx - 24, 452), (sx - 16, 430), (sx + 16, 430), (sx + 24, 452)]), CHROME, 610, sk=0.2, n=4, inkw=1.4, hi=0.5))
    sx = 420
    out.append(painted(D, rect_pts(sx - 20, 462, sx + 20, 520, 10, 611, 0.3), ("#F4FAFC", "#D8E4EA", "#8AA0AE"), 611, sk=0.2, n=6, inkw=1.6, hi=0.5))
    out.append(specks(612, (sx - 18, 476, sx + 18, 518), ["#C8301E", "#E8A040", "#7A1A10"], 80, (1, 2), (0.8, 1)))
    out.append(painted(D, pp([(sx - 22, 462), (sx - 14, 440), (sx + 14, 440), (sx + 22, 462)]), CHROME, 613, sk=0.2, n=4, inkw=1.4, hi=0.5))
    # lettering on the brick
    out.append(letters(D, 300, 166, "Deep Dish", SERIF_IT, 104, "#FFF2D8", ["#FFFFFF", "#FFE2C0", "#FFD0A0"], 614, max_w=420,
                       shadow="#2A0A06", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 214, "CHICAGO STYLE", "#FFD27A", font=JOS, size=22, ls=7, line_w=28, gap=12, max_w=300))
    return finish_a(D, out, 615)


# ================================================================ 21. heartland — cornfield with a storm coming
def corn_plant(D, x, base, h, seed, pals=(("#B8D87A", "#5A8A2E", "#244A14"),), lean=0.0, ear=True, rim="#FFF2A0"):
    rnd = random.Random(seed)
    out = []
    top = (x + lean * h, base - h)
    out.append(taper([(x, base), (x + lean * h * 0.4, base - h * 0.5), top], max(3, h * 0.03), max(1.5, h * 0.012), "#6A8A2A"))
    for i in range(9):
        t = 0.12 + i * 0.085
        px, py = x + lean * h * t, base - h * t
        side = 1 if (i + seed) % 2 else -1
        L = h * rnd.uniform(0.32, 0.5) * (1 - t * 0.4)
        tip = (px + side * L, py + L * rnd.uniform(0.15, 0.6))
        mid = (px + side * L * 0.45, py - L * rnd.uniform(0.15, 0.35))
        pal = rnd.choice(pals)
        blade = qpts((px, py), mid, tip, 10)
        w = max(5, h * 0.045)
        out.append(taper(blade, w, 1, pal[1]))
        out.append(taper([(bx_, by_ - w * 0.15) for bx_, by_ in blade[:-1]], w * 0.35, 0.6, pal[0], 0.8))
        out.append(pline(blade, pal[2], 1, seed + i, 0.5, 1))
        if side < 0:
            out.append(pline(blade[1:6], rim, 1.4, seed + i + 50, 0.55, 1))
    if ear:
        ex, ey = x + lean * h * 0.5, base - h * 0.5
        out.append(painted(D, blob_pts(ex + 10, ey - 6, 9, 24, seed + 70, 0.05, 12, 20), ("#D8E8A0", "#8AB04A", "#4A6A1E"), seed + 70, sk=0.2, n=4, inkw=1.2, hi=0.4))
        for k in range(5):
            out.append(f'<path d="M {ex + 14:.1f} {ey - 28:.1f} q {2 + k * 2:.1f} -8 {k * 3 - 4:.1f} -14" stroke="#C88A3A" stroke-width="1.4" fill="none"/>')
    for k in range(6):
        a = math.radians(-90 + rnd.uniform(-35, 35))
        L = h * rnd.uniform(0.06, 0.1)
        out.append(taper([top, (top[0] + math.cos(a) * L, top[1] + math.sin(a) * L)], 2.6, 0.8, "#D8B860"))
    return "".join(out)


@design("heartland")
def heartland():
    D = Doc2("us-hl")
    out = [sky(D, [(0, "#3A4458"), (0.5, "#7A7A8A"), (0.8, "#E8C890"), (1, "#FFE8B0")], 621, 360, ["#4A5468", "#9A9AA8", "#2A3040"], 60)]
    # the storm: dark anvil on the right, rain shafts, a lightning fork
    out.append(f'<path d="{blob(470, 150, 240, 110, 622, 0.18, 24)}" fill="#2A3040" opacity="0.85"/>')
    out.append(f'<path d="{blob(520, 210, 180, 70, 623, 0.2, 20)}" fill="#1E2432" opacity="0.8"/>')
    out.append(puff_cloud(D, 420, 120, 260, 624, pal=("#8A90A4", "#4A5266", "#1E2432"), rows=2))
    for k in range(12):
        x = 420 + k * 16
        out.append(taper([(x, 240), (x - 14, 340)], 6, 3, "#9AA4BC", 0.18))
    out.append(D.glow(500, 250, 90, "#E8F0FF", 0.35))
    out.append(pline([(492, 214), (480, 250), (500, 256), (476, 310), (488, 314), (470, 346)], "#FFFFFF", 3, 625, 1, 1))
    out.append(pline([(492, 214), (480, 250), (500, 256), (476, 310), (488, 314), (470, 346)], "#C8D8FF", 7, 626, 0.35, 1))
    # golden light breaking through on the left
    out.append(soft_glow(D, 110, 300, 230, "#FFF0B0", 0.6))
    out.append(puff_cloud(D, 150, 268, 110, 627, pal=("#FFF2D8", "#E8C8A0", "#9A8A8A")))
    # horizon: farmhouse, red barn, windmill, a lone oak
    out.append(hill(D, ridge([(-20, 352), (300, 344), (620, 350)], 628, 2), 600, ("#C8B05A", "#A8903A", "#6A5A20"), 628, inkw=0))
    out.append(dab_crown(D, 92, 312, 46, 38, [("#8A9A4A", "#5A6A2A", "#2E3A14")], 629, n=40, size=(6, 10), inkw=0))
    out.append(taper([(92, 350), (92, 320)], 6, 4, "#3A2A1A"))
    out.append(painted(D, rect_pts(176, 318, 226, 350, 10, 630, 0.3), BARN, 630, sk=0.1, n=4, inkw=1.2, hi=0.3))
    out.append(painted(D, pp([(172, 320), (186, 302), (216, 302), (230, 320)]), ("#8A8A9A", "#5A5A6A", "#2A2A3A"), 631, sk=0.1, n=3, inkw=1.2, hi=0.3))
    out.append(painted(D, rect_pts(238, 326, 270, 350, 8, 632, 0.3), WHITE, 632, sk=0.1, n=3, inkw=1.2, hi=0.3))
    out.append(painted(D, pp([(234, 328), (254, 312), (274, 328)]), ("#6A6A7A", "#3A3A4A", "#1A1A2A"), 633, sk=0.1, n=3, inkw=1.2, hi=0.3))
    out.append(f'<path d="M 316 350 L 326 300 L 336 350" stroke="#3A3A3A" stroke-width="1.6" fill="none"/>')
    for k in range(10):
        a = math.radians(k * 36)
        out.append(f'<path d="M 326 298 L {326 + math.cos(a) * 12:.1f} {298 + math.sin(a) * 12:.1f}" stroke="#3A3A3A" stroke-width="2"/>')
    # cornfield rows converging to the horizon
    vp = (300, 346)
    out.append(f'<path d="M -10 352 L 610 352 L 610 600 L -10 600 Z" fill="#4A7A2A"/>')
    rnd = random.Random(634)
    for k in range(-12, 13):
        x_bot = 300 + k * 64
        for j in range(26):
            t = (j / 25) ** 1.7
            x = vp[0] + (x_bot - vp[0]) * t
            y = vp[1] + (600 - vp[1]) * t
            s = 2 + 14 * t
            lit = rnd.random() < 0.5
            out.append(f'<path d="{blob(x + rnd.uniform(-2, 2), y - s * 0.5, s * 1.1, s * 0.7, rnd.randint(0, 9999), 0.3, 8)}" fill="{rnd.choice(["#8AB84A", "#C8D870"] if lit else ["#3E6A22", "#5A8A2E"])}"/>')
    for k in range(-12, 13):
        x_bot = 300 + k * 64 + 32
        out.append(pline([(vp[0], vp[1] + 4), (x_bot, 610)], "#2A4A14", 2, 635 + k, 0.35, 1))
    out.append(f'<rect y="346" width="600" height="80" fill="{D.lin([(0, "#E8D8A0", 0.45), (1, "#E8D8A0", 0)])}"/>')
    # tall stalks framing the edges
    for k, (x, h, ln) in enumerate(((30, 330, 0.05), (82, 280, -0.02), (548, 320, -0.05), (500, 260, 0.03))):
        out.append(corn_plant(D, x, 640, h, 636 + k, pals=(("#B8D87A", "#5A8A2E", "#244A14"), ("#A8C86A", "#4A7A24", "#1E3E10")), lean=ln, ear=k % 2 == 0))
    # lettering
    out.append(letters(D, 300, 136, "Heartland", SERIF_IT, 112, "#FFF6E0", ["#FFFFFF", "#FFEACC"], 640, max_w=430,
                       shadow="#1E2432", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 182, "KNEE-HIGH BY THE FOURTH OF JULY", "#FFE8B0", font=JOS, size=18, ls=3, line_w=16, gap=8, max_w=400))
    return finish_a(D, out, 641)


# ================================================================ 22. drive-in tonight — the big screen at dusk, cars lined up
def car_rear(D, cx, base, w, seed, body=AQUA, roof=CREAM, couple=True, fins=True):
    """A 1950s car seen from behind (no badges): tail fins, glowing tail lights, chrome bumper,
    a rear window with two heads leaning together."""
    out = [cast(D, cx, base + 2, w * 0.62, w * 0.06, strength=0.5, seed=seed)]
    h = w * 0.5
    for sg in (-1, 1):
        out.append(f'<path d="{hg.org_rect(cx + sg * w * 0.36 - w * 0.08, base - w * 0.12, w * 0.16, w * 0.12, seed + sg, 0.3, 6, 3)}" fill="#141218"/>')
    cab = pp([(cx - w * 0.34, base - h * 0.62), (cx - w * 0.26, base - h * 1.02), (cx + w * 0.26, base - h * 1.02), (cx + w * 0.34, base - h * 0.62)], 10, seed)
    out.append(painted(D, cab, roof, seed + 1, sdir=(0, 1), sk=0.12, angle=0, n=8, inkw=1.6, hi=0.4))
    win = [(cx - w * 0.28, base - h * 0.66), (cx - w * 0.22, base - h * 0.94), (cx + w * 0.22, base - h * 0.94), (cx + w * 0.28, base - h * 0.66)]
    out.append(f'<path d="{pd(win)}" fill="{D.lin([(0, "#E8E0FF"), (1, "#6A6A9A")])}"/>')
    if couple:
        for k, (dx, c) in enumerate(((-0.07, "#2A1A10"), (0.06, "#6A3A1A"))):
            hx = cx + dx * w
            out.append(f'<circle cx="{hx:.1f}" cy="{base - h * 0.8:.1f}" r="{w * 0.065:.1f}" fill="{c}"/>')
            out.append(f'<path d="M {hx - w * 0.1:.1f} {base - h * 0.66:.1f} Q {hx:.1f} {base - h * 0.78:.1f} {hx + w * 0.1:.1f} {base - h * 0.66:.1f} Z" fill="{c}"/>')
    out.append(ink(pd(win), "#E8ECF0", 1.6, seed, 1, 0.9))
    bodyp = pp([(cx - w * 0.5, base - w * 0.08), (cx - w * 0.5, base - h * 0.62), (cx + w * 0.5, base - h * 0.62), (cx + w * 0.5, base - w * 0.08)], 10, seed + 2)
    out.append(painted(D, bodyp, body, seed + 2, sdir=(0, 1), sk=0.12, angle=0, n=16, inkw=1.8, hi=0.5))
    if fins:
        for sg in (-1, 1):
            fin = [(cx + sg * w * 0.5, base - h * 0.6), (cx + sg * w * 0.5, base - h * 0.9), (cx + sg * w * 0.38, base - h * 0.62)]
            out.append(painted(D, pp(fin, 6, seed + 3 + sg), body, seed + 3 + sg, sk=0.15, n=4, inkw=1.6, hi=0.5))
    out.append(pline([(cx - w * 0.46, base - h * 0.48), (cx + w * 0.46, base - h * 0.48)], dk(body[2], 0.2), 1.4, seed, 0.6, 1))
    for sg in (-1, 1):
        lx, ly = cx + sg * w * 0.43, base - h * 0.45
        out.append(D.glow(lx, ly, w * 0.22, "#FF3A2A", 0.6))
        out.append(f'<path d="{hg.org_rect(lx - w * 0.04, ly - h * 0.16, w * 0.08, h * 0.26, seed + 6 + sg, 0.3, 6, 3)}" fill="#FF4A3A" stroke="#7A1010" stroke-width="1.2"/>')
        out.append(f'<circle cx="{lx:.1f}" cy="{ly - h * 0.06:.1f}" r="{w * 0.015:.1f}" fill="#FFE0D0"/>')
    out.append(painted(D, rect_pts(cx - w * 0.54, base - w * 0.12, cx + w * 0.54, base - w * 0.06, 10, seed + 8, 0.3), CHROME, seed + 8, sk=0.1, n=4, inkw=1.4, hi=0.6))
    out.append(f'<path d="{hg.org_rect(cx - w * 0.1, base - h * 0.4, w * 0.2, h * 0.16, seed + 9, 0.3, 6, 2)}" fill="#F4F0E0" stroke="{INK}" stroke-width="1"/>')
    return "".join(out)


def popcorn_box(D, cx, base, w, h, seed):
    out = [cast(D, cx + 6, base + 2, w * 0.7, 7, strength=0.5, seed=seed)]
    box = pp([(cx - w / 2, base - h), (cx + w / 2, base - h), (cx + w * 0.38, base), (cx - w * 0.38, base)], 10, seed)
    d = smooth_closed(box)
    out.append(f'<path d="{d}" fill="#FFFDF4"/>')
    cid = D.clip(f'<path d="{d}"/>')
    st = []
    for k in range(-4, 5):
        if k % 2 == 0:
            st.append(f'<path d="M {cx + k * w * 0.11:.1f} {base - h - 2:.1f} L {cx + (k + 1) * w * 0.11:.1f} {base - h - 2:.1f} L {cx + (k + 1) * w * 0.085:.1f} {base + 2:.1f} L {cx + k * w * 0.085:.1f} {base + 2:.1f} Z" fill="#D8302A"/>')
    st.append(f'<path d="{d}" fill="{D.lin([(0, "#FFFFFF", 0.3), (0.4, "#FFFFFF", 0), (1, "#1A0A04", 0.35)], 0, 0, 1, 0)}"/>')
    out.append(f'<g {cid}>{"".join(st)}</g>')
    out.append(ink(d, INK, 1.6, seed, 1, 0.75))
    rnd = random.Random(seed)
    for k in range(30):
        x = cx + rnd.uniform(-w * 0.52, w * 0.52)
        y = base - h - rnd.uniform(-4, w * 0.3) * (1 - abs(x - cx) / w)
        r = rnd.uniform(5, 8)
        out.append(f'<path d="{blob(x, y, r, r * 0.85, rnd.randint(0, 999), 0.3, 9)}" fill="{rnd.choice(["#FFF8E0", "#FFF0C0", "#FFFFFF"])}" stroke="#C8A060" stroke-width="0.9"/>')
        out.append(f'<circle cx="{x + rnd.uniform(-2, 2):.1f}" cy="{y + rnd.uniform(-2, 2):.1f}" r="1.3" fill="#E8B860"/>')
    return "".join(out)


@design("drive-in-tonight")
def drive_in_tonight():
    D = Doc2("us-di")
    out = [sky(D, [(0, "#14183E"), (0.45, "#3A2E6A"), (0.75, "#A84A6A"), (1, "#F2905A")], 651, 380, ["#2A2E6A", "#6A3A7A"], 60)]
    out.append(stars_field(652, 50, (0, 0, 600, 200), avoid=((100, 50, 500, 180),)))
    out.append(hill(D, ridge([(-20, 362), (160, 344), (380, 356), (620, 340)], 653, 4), 600, ("#3A2A4A", "#241A30", "#120C1A"), 653, inkw=0))
    # the screen on its scaffold
    sx0, sx1, sy0, sy1 = 148, 452, 196, 352
    for x in range(sx0 + 20, sx1, 56):
        out.append(f'<path d="M {x} {sy1} L {x} 384" stroke="#2A2234" stroke-width="5"/>')
        out.append(f'<path d="M {x} {sy1 + 4} L {x + 56} 384" stroke="#2A2234" stroke-width="2"/>')
    out.append(D.glow(300, 274, 260, "#E8E8FF", 0.35, ry=140))
    out.append(painted(D, rect_pts(sx0 - 8, sy0 - 8, sx1 + 8, sy1 + 8, 20, 654, 0.3), ("#4A4060", "#2A2240", "#141020"), 654, sk=0.1, n=8, inkw=1.6, hi=0.2))
    scr = f"M {sx0} {sy0} L {sx1} {sy0} L {sx1} {sy1} L {sx0} {sy1} Z"
    out.append(f'<path d="{scr}" fill="{D.rad([(0, "#FFFFFF"), (0.7, "#D8D8E8"), (1, "#9A9AB0")], 0.5, 0.5, 0.7)}"/>')
    # film-leader countdown on the screen
    cx, cy = 300, 274
    out.append(f'<path d="M {cx} {cy} L {cx} {sy0} A 110 110 0 0 1 {cx + 66} {cy - 54} Z" fill="#5A5A6A" opacity="0.35"/>')
    for r in (64, 52):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#2A2A34" stroke-width="3"/>')
    out.append(f'<path d="M {sx0} {cy} L {sx1} {cy} M {cx} {sy0} L {cx} {sy1}" stroke="#2A2A34" stroke-width="2.4"/>')
    out.append(f'<text x="{cx}" y="{cy + 34}" text-anchor="middle" {ANTON} font-size="96" fill="#2A2A34">3</text>')
    out.append(specks(655, (sx0, sy0, sx1, sy1), ["#2A2A34", "#FFFFFF"], 60, (0.6, 1.6), (0.3, 0.7)))
    # projector beam from the booth
    out.append(f'<path d="M 300 470 L {sx0 + 10} {sy0 + 10} L {sx1 - 10} {sy0 + 10} Z" fill="{D.lin([(0, "#E8F0FF", 0.0), (1, "#E8F0FF", 0.35)], 0, 0, 0, 1)}" opacity="0.6"/>')
    rnd = random.Random(656)
    for _ in range(40):
        t = rnd.uniform(0.1, 0.9)
        y = 470 - (470 - sy0) * t
        half = (sx1 - sx0) / 2 * t * 0.9
        out.append(f'<circle cx="{300 + rnd.uniform(-half, half):.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 1.4):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.3, 0.8):.2f}"/>')
    # the lot and the cars, rear view
    out.append(f'<path d="M -10 384 L 610 384 L 610 600 L -10 600 Z" fill="{D.lin([(0, "#3A2E44"), (1, "#1A1420")])}"/>')
    for k in range(5):
        y = 400 + k * 22
        out.append(f'<path d="M -10 {y} Q 300 {y - 10} 610 {y}" stroke="#4A3E54" stroke-width="2" fill="none" opacity="0.6"/>')
    for k, x in enumerate((70, 530)):
        out.append(f'<path d="M {x} 470 L {x} 420" stroke="#8A8494" stroke-width="3"/>')
        out.append(f'<path d="{hg.org_rect(x - 9, 410, 18, 14, 657 + k, 0.3, 4, 2)}" fill="#C8C2D0" stroke="#3A3440" stroke-width="1"/>')
    out.append(car_rear(D, 160, 470, 150, 658, body=CHERRY, roof=CREAM))
    out.append(car_rear(D, 440, 470, 150, 659, body=AQUA, roof=CREAM))
    # projection booth
    out.append(painted(D, rect_pts(260, 452, 340, 500, 10, 660, 0.3), ("#E8D8C8", "#B8A898", "#6A5A4E"), 660, sk=0.1, n=6, inkw=1.6, hi=0.3))
    out.append(f'<path d="{hg.org_rect(292, 462, 16, 12, 661, 0.2, 4, 1)}" fill="#FFF6D0"/>')
    out.append(D.glow(300, 468, 30, "#FFF6D0", 0.7))
    out.append(painted(D, pp([(250, 454), (300, 434), (350, 454)]), CHERRY, 662, sk=0.1, n=4, inkw=1.4, hi=0.3))
    # popcorn and sodas in the foreground
    out.append(popcorn_box(D, 120, 572, 96, 92, 663))
    for k, x in enumerate((452, 500)):
        cup = pp([(x - 20, 492), (x + 20, 492), (x + 16, 572), (x - 16, 572)], 10, 664 + k)
        out.append(cast(D, x + 4, 574, 24, 5, strength=0.5, seed=664 + k))
        out.append(painted(D, cup, ("#FFFFFF", "#F4F0E8", "#B8B0A6"), 664 + k, sdir=(0.9, 0.2), sk=0.15, angle=-90, n=6, inkw=1.6, hi=0.4))
        out.append(f'<path d="M {x - 18} 516 L {x + 18} 516 L {x + 17} 532 L {x - 17} 532 Z" fill="#2E5AA8"/>')
        out.append(f'<path d="{smooth_closed(ell_pts(x, 492, 21, 5, 0, 360, 14)[:-1])}" fill="#F4F0E8" stroke="{INK}" stroke-width="1.2"/>')
        out.append(straw(D, x + (4 if k else -4), 492, x + (16 if k else -10), 452, 7, 666 + k))
    # lettering
    out.append(letters(D, 300, 128, "Drive-In", SERIF_IT, 100, "#FFF2D8", ["#FFFFFF", "#FFE2C0"], 668, max_w=360,
                       shadow="#7A1A3A", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 170, "DOUBLE FEATURE TONIGHT", "#FFD27A", font=JOS, size=19, ls=5, line_w=20, gap=10, max_w=360))
    return finish_a(D, out, 669)


# ================================================================ 23. letters from home — the mailbox with its flag up
def morning_glory(D, cx, cy, r, seed, col=("#B8D0FF", "#5A7AE8", "#2A3A9A")):
    out = [f'<path d="{blob(cx, cy, r, r * 0.92, seed, 0.06, 16)}" fill="{col[1]}"/>']
    out.append(f'<path d="{blob(cx, cy, r * 0.62, r * 0.58, seed + 1, 0.08, 12)}" fill="{col[0]}" opacity="0.7"/>')
    for k in range(5):
        a = math.radians(k * 72 + 18)
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {cx + math.cos(a) * r * 0.95:.1f} {cy + math.sin(a) * r * 0.95:.1f}" stroke="#FFFFFF" stroke-width="1.2" opacity="0.7"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.22:.1f}" fill="#FFF6C0"/>')
    out.append(ink(blob(cx, cy, r, r * 0.92, seed, 0.06, 16), col[2], 1.1, seed, 1, 0.6))
    return "".join(out)


def envelope(D, x, y, w, h, ang, seed, airmail=True):
    pts = rot([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)], x, y, ang)
    d = hg.org_poly(pts, seed, 0.3, 10, 1.5)
    out = [f'<path d="{d}" fill="#FFFAF0" stroke="{INK}" stroke-width="1.2"/>']
    if airmail:
        cid = D.clip(f'<path d="{d}"/>')
        st = []
        for k in range(-12, 14):
            a = rot([(x - w / 2 + k * 9, y - h / 2 - 2), (x - w / 2 + k * 9 + 5, y - h / 2 - 2), (x - w / 2 + k * 9 + 9, y - h / 2 + 5), (x - w / 2 + k * 9 + 4, y - h / 2 + 5)], x, y, ang)
            st.append(f'<path d="{pd(a)}" fill="{"#D8302A" if k % 2 else "#2E5AA8"}"/>')
        out.append(f'<g {cid}>{"".join(st)}</g>')
    return "".join(out)


@design("letters-from-home")
def letters_from_home():
    D = Doc2("us-lh")
    out = [sky(D, [(0, "#8ABCE8"), (0.6, "#FFE0B0"), (1, "#FFC890")], 671, 380, ["#A8D0F0", "#FFE8C8"], 40)]
    out.append(soft_glow(D, 470, 330, 220, "#FFF2C0", 0.75))
    out.append(puff_cloud(D, 150, 230, 120, 672, pal=("#FFFFFF", "#FFF2E8", "#E8C8C8")))
    # rolling farmland and a gravel road to the farmhouse
    out.append(hill(D, ridge([(-20, 340), (200, 326), (420, 336), (620, 322)], 673, 3), 600, ("#C8D890", "#9AB068", "#6A8040"), 673, inkw=0))
    fx = 448
    out.append(painted(D, rect_pts(fx - 30, 306, fx + 30, 334, 10, 674, 0.3), WHITE, 674, sk=0.1, n=4, inkw=1.2, hi=0.3))
    out.append(painted(D, pp([(fx - 36, 308), (fx, 288), (fx + 36, 308)]), BARN, 675, sk=0.1, n=3, inkw=1.2, hi=0.3))
    out.append(dab_crown(D, fx + 54, 300, 26, 24, [GRASS, SAGE], 676, n=26, size=(5, 8), inkw=0))
    out.append(hill(D, ridge([(-20, 380), (300, 364), (620, 384)], 677, 3), 600, GRASS, 677, inkw=0))
    road = f"M 600 600 Q 420 470 {fx - 10} 336 L {fx + 4} 336 Q 470 470 640 560 Z"
    out.append(f'<path d="{road}" fill="#E2D2B4"/>')
    out.append(specks(678, (380, 340, 600, 600), ["#B8A07A", "#FFFFFF"], 120, (0.8, 2), (0.4, 0.9)))
    out.append(grass(679, (0, 380, 600, 600), ["#5A8A30", "#8AB850", "#2E5A1E", "#A8D070"], 220, (8, 22)))
    # the post, wrapped in morning glories
    px = 250
    out.append(painted(D, rect_pts(px - 16, 400, px + 16, 610, 14, 680, 0.4), WOOD, 680, sdir=(1, 0), sk=0.2, angle=-90, n=20, inkw=1.8, hi=0.3))
    rnd = random.Random(681)
    vine = [(px - 18 + 36 * ((k % 2)), 600 - k * 26) for k in range(8)]
    out.append(pline(vine, "#3E7A2A", 2.4, 682, 0.9, 1))
    for k, (x, y) in enumerate(vine[1:]):
        out.append(leaf_simple(D, x, y, 24, 10, rnd.choice((-30, -150, 200, 20)), ("#A8D870", "#4A9A3A", "#1E5A1E"), 683 + k, vein=False, inkw=1))
        if k % 2 == 0:
            out.append(morning_glory(D, x + rnd.uniform(-8, 8), y - 8, 13, 690 + k))
    # the mailbox: rounded tunnel, door ajar, letters peeking, red flag up
    mx0, mx1, mtop, mbot = 96, 404, 290, 410
    side = [(mx0, mbot), (mx0, mtop + 44)] + [(mx0 + 44 - 44 * math.cos(math.radians(a)), mtop + 44 - 44 * math.sin(math.radians(a))) for a in range(0, 91, 15)] + \
           [(mx1 - 44 + 44 * math.cos(math.radians(a)), mtop + 44 - 44 * math.sin(math.radians(a))) for a in range(90, -1, -15)] + [(mx1, mbot)]
    side = pp(side, 10, 700)
    out.append(cast(D, 250, 418, 170, 9, strength=0.5, seed=700))
    out.append(painted(D, side, ("#F4F6FA", "#B8C2CE", "#5A6474"), 701, sdir=(0, 1), sk=0.15, angle=0, n=30, inkw=2, hi=0.55))
    cid = D.clip(f'<path d="{smooth_closed(side)}"/>')
    rib = "".join(f'<path d="M {mx0} {y} L {mx1} {y}" stroke="#FFFFFF" stroke-width="1.6" opacity="0.5"/>' for y in range(mtop + 10, mbot, 14))
    rib += f'<rect x="{mx0}" y="{mtop}" width="{mx1 - mx0}" height="20" fill="#FFFFFF" opacity="0.25"/>'
    out.append(f'<g {cid}>{rib}</g>')
    # front door hanging open (seen edge-on) and the mouth with letters
    out.append(f'<path d="M {mx1 - 4} {mbot} L {mx1 + 14} {mbot + 8} L {mx1 + 22} {mtop + 46} L {mx1 + 6} {mtop + 30} Z" fill="#8A94A4" stroke="{INK}" stroke-width="1.4"/>')
    out.append(envelope(D, mx1 - 24, mbot - 30, 76, 46, -14, 702))
    out.append(envelope(D, mx1 - 8, mbot - 18, 70, 42, 8, 703, airmail=False))
    out.append(label(250, 368, "No. 12", DMS, 30, "#22386A", ls=1))
    # flag
    fpx = mx0 + 22
    out.append(painted(D, rect_pts(fpx - 4, mtop - 70, fpx + 4, mtop + 40, 8, 704, 0.3), CHERRY, 704, sk=0.15, n=3, inkw=1.2, hi=0.4))
    out.append(painted(D, rect_pts(fpx - 4, mtop - 70, fpx + 44, mtop - 40, 8, 705, 0.3), CHERRY, 705, sk=0.15, n=4, inkw=1.4, hi=0.5))
    out.append(f'<circle cx="{fpx}" cy="{mtop + 30}" r="4" fill="#C8D0DA" stroke="{INK}" stroke-width="1"/>')
    # a bluebird on the roof of the box
    bx, by = 300, mtop - 12
    out.append(painted(D, blob_pts(bx, by, 16, 11, 706, 0.05, 12), ("#9AC0FF", "#3A6AD8", "#1A3A8A"), 706, sk=0.2, n=4, inkw=1.2, hi=0.4))
    out.append(f'<path d="{blob(bx + 4, by + 5, 9, 6, 707, 0.1, 10)}" fill="#E8884A"/>')
    out.append(f'<circle cx="{bx + 14}" cy="{by - 9}" r="7" fill="#3A6AD8"/><circle cx="{bx + 16}" cy="{by - 10}" r="1.4" fill="#FFFFFF"/>'
               f'<path d="M {bx + 20} {by - 9} l 6 1 l -6 2 Z" fill="#3A2A1A"/><path d="M {bx - 14} {by - 2} l -12 -4 l 2 8 Z" fill="#1A3A8A"/>')
    # wildflowers at the base
    for _ in range(40):
        x, y = rnd.uniform(60, 560), rnd.uniform(470, 600)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(2.4, 4):.1f}" fill="{rnd.choice(["#FFFFFF", "#F6C21C", "#E8604A", "#9A7AE0", "#F6C21C"])}"/>')
    # lettering
    out.append(letters(D, 300, 124, "Letters from Home", SERIF_IT, 70, "#22386A", ["#2E4A8A", "#14244A"], 708, max_w=460,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-40, hi="#A8C0F0"))
    out.append(ruled(300, 166, "THE FLAG IS UP", "#B8352A", font=JOS, size=21, ls=6, line_w=26, gap=12, max_w=300))
    return finish_a(D, out, 709)


# ================================================================ 24. land of the free — a hand-pieced flag quilt
def calico(D, d, base, motif, seed, cell=22, kind="flower"):
    rnd = random.Random(seed)
    inner = [f'<rect width="{cell}" height="{cell}" fill="{base}"/>']
    if kind == "flower":
        for (fx, fy) in ((0.25, 0.3), (0.75, 0.78)):
            for k in range(5):
                a = math.radians(k * 72)
                inner.append(f'<circle cx="{fx * cell + math.cos(a) * 2.4:.1f}" cy="{fy * cell + math.sin(a) * 2.4:.1f}" r="1.7" fill="{motif}"/>')
            inner.append(f'<circle cx="{fx * cell:.1f}" cy="{fy * cell:.1f}" r="1" fill="#F6E8B0"/>')
        inner.append(f'<path d="M {cell * 0.6:.1f} {cell * 0.2:.1f} q 3 3 1 6" stroke="{motif}" stroke-width="1" fill="none" opacity="0.7"/>')
    elif kind == "dots":
        for (fx, fy) in ((0.25, 0.25), (0.75, 0.75)):
            inner.append(f'<circle cx="{fx * cell:.1f}" cy="{fy * cell:.1f}" r="{cell * 0.09:.1f}" fill="{motif}"/>')
    elif kind == "ticking":
        inner.append(f'<rect x="{cell * 0.1:.1f}" width="{cell * 0.12:.1f}" height="{cell}" fill="{motif}"/><rect x="{cell * 0.55:.1f}" width="{cell * 0.05:.1f}" height="{cell}" fill="{motif}"/>')
    elif kind == "check":
        inner.append(f'<rect width="{cell / 2:.1f}" height="{cell}" fill="{motif}" opacity="0.45"/><rect width="{cell}" height="{cell / 2:.1f}" fill="{motif}" opacity="0.45"/>')
    elif kind == "stars":
        for (fx, fy) in ((0.3, 0.3), (0.8, 0.75)):
            inner.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in hg.star_pts(fx * cell, fy * cell, cell * 0.12, cell * 0.05))}" fill="{motif}"/>')
    pat = D.pattern(cell, cell, "".join(inner), transform=f"rotate({rnd.choice([0, 0, 45, -20])})")
    return f'<path d="{d}" fill="{pat}"/>'


@design("land-of-the-free")
def land_of_the_free():
    D = Doc2("us-lf")
    reds = [("#C8302A", "#F2C8B8", "flower"), ("#B8282A", "#FFFFFF", "dots"), ("#D8402E", "#8A1A14", "check"), ("#A8241E", "#F6D8C0", "ticking"), ("#C8382A", "#FFE8D8", "stars")]
    creams = [("#F6EEDC", "#C8382A", "flower"), ("#FFF8EA", "#2E4A8A", "dots"), ("#F2E6CE", "#B8A07A", "ticking"), ("#FAF2E2", "#C8302A", "check"), ("#F4EAD6", "#22386A", "stars")]
    blues = [("#22386A", "#F2E6CC", "stars"), ("#2E4A8A", "#C8D8F0", "dots"), ("#1E3060", "#8AA0D0", "flower")]
    out = [f'<rect width="600" height="600" fill="#F4EAD6"/>']
    rnd = random.Random(711)
    # 13 stripes of patchwork, each pieced from several fabrics
    sh = 600 / 13
    canton_w, canton_h = 270, sh * 7
    for i in range(13):
        y0 = i * sh
        x = canton_w if i < 7 else 0
        while x < 600:
            w = rnd.uniform(70, 140)
            pal = rnd.choice(reds if i % 2 == 0 else creams)
            d = hg.org_rect(x, y0, w + 1, sh + 1, int(x * 3 + i), 0.6, 14, 1)
            out.append(calico(D, d, pal[0], pal[1], int(x + i * 37), cell=rnd.choice([18, 22, 26]), kind=pal[2]))
            out.append(f'<path d="M {x:.1f} {y0 + 2:.1f} L {x:.1f} {y0 + sh - 2:.1f}" stroke="{INK}" stroke-width="1" opacity="0.35"/>')
            x += w
        out.append(f'<path d="M 0 {y0 + sh:.1f} L 600 {y0 + sh:.1f}" stroke="{INK}" stroke-width="1" opacity="0.3"/>')
    # canton: blocks of blue prints with appliquéd stars
    for r in range(3):
        for c in range(3):
            pal = blues[(r + c) % 3]
            x0, y0 = c * canton_w / 3, r * canton_h / 3
            d = hg.org_rect(x0, y0, canton_w / 3 + 1, canton_h / 3 + 1, 720 + r * 3 + c, 0.6, 14, 1)
            out.append(calico(D, d, pal[0], pal[1], 730 + r * 3 + c, cell=20, kind=pal[2]))
            sx, sy = x0 + canton_w / 6, y0 + canton_h / 6
            st = hg.star_pts(sx, sy, 30, 12)
            sd = hg.org_poly(st, 740 + r * 3 + c, 0.5, 8, 1)
            out.append(f'<path d="{sd}" fill="#FFF8EA" transform="translate(2 3)" opacity="0.3"/>')
            out.append(calico(D, sd, "#FFF8EA", "#C8D8F0", 750 + r + c, cell=12, kind="dots"))
            out.append(f'<path d="{sd}" fill="none" stroke="#C8302A" stroke-width="1.6" stroke-dasharray="3 3"/>')
    out.append(f'<path d="M 0 {canton_h:.1f} L {canton_w} {canton_h:.1f} L {canton_w} 0" stroke="{INK}" stroke-width="1.6" opacity="0.5" fill="none"/>')
    # quilting stitches: diagonal running stitch across everything
    for k in range(-12, 14):
        out.append(f'<path d="M {k * 50} 0 L {k * 50 + 600} 600" stroke="#FFFFFF" stroke-width="1.6" stroke-dasharray="6 6" opacity="0.4"/>')
    # soft puffs of batting between the stitch lines
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 600 L 0 600 Z", (-40, 0, 600, 600), ["#FFFFFF", "#3A2418"], 760, n=120, angle=45, length=(30, 70), width=(3, 8), opacity=(0.04, 0.12)))
    # the embroidered label panel, appliquéd in the middle
    lx0, lx1, ly0, ly1 = 92, 508, 316, 488
    out.append(f'<path d="{hg.org_rect(lx0 + 6, ly0 + 8, lx1 - lx0, ly1 - ly0, 761, 0.6, 14, 6)}" fill="#3A2418" opacity="0.25"/>')
    out.append(painted(D, rect_pts(lx0, ly0, lx1, ly1, 20, 762, 0.6), ("#FFFDF4", "#F6EEDC", "#C8B898"), 762, sk=0.05, n=30, inkw=0, hi=0.2))
    out.append(f'<path d="{hg.org_rect(lx0 + 10, ly0 + 10, lx1 - lx0 - 20, ly1 - ly0 - 20, 763, 0.5, 14, 4)}" fill="none" stroke="#22386A" stroke-width="2.2" stroke-dasharray="7 5"/>')
    out.append(f'<path d="{hg.org_rect(lx0, ly0, lx1 - lx0, ly1 - ly0, 764, 0.5, 14, 4)}" fill="none" stroke="#C8302A" stroke-width="3"/>')
    out.append(letters(D, 300, 400, "Land of the Free", SERIF_IT, 66, "#B8282A", ["#C8302A", "#8A1A14"], 765, max_w=380,
                       shadow="#F2D8C8", soff=(0.02, 0.03), angle=-40, hi="#FFC8B8", wob=0.6))
    out.append(ruled(300, 448, "HOME OF THE BRAVE", "#22386A", font=JOS, size=22, ls=6, line_w=22, gap=10, max_w=320))
    for k, x in enumerate((116, 484)):
        out.append(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in hg.star_pts(x, 434, 11, 4.5))}" fill="#22386A"/>')
    return finish_a(D, out, 766)


# ================================================================ 25. s'mores — by the campfire
def graham(D, cx, cy, w, h, ang, seed, bite=False):
    pts = rot(rrect_pts(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 3, 3), cx, cy, ang)
    pts = jitter(pts, seed, 0.8)
    out = [painted(D, pts, ("#F2C88A", "#D8A060", "#8A5A2A"), seed, sdir=(0.4, 1), sk=0.12, angle=ang, n=10, inkw=1.4, hi=0.35)]
    a, b = rot([(cx, cy - h / 2 + 3), (cx, cy + h / 2 - 3)], cx, cy, ang)
    out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#9A6A34" stroke-width="1.6" stroke-dasharray="3 3"/>')
    for i in range(2):
        for j in range(2):
            px, py = rot([(cx + (-0.25 + 0.5 * i) * w, cy + (-0.25 + 0.5 * j) * h)], cx, cy, ang)[0]
            for k in range(4):
                qx, qy = rot([(px + (k % 2 - 0.5) * w * 0.12, py + (k // 2 - 0.5) * h * 0.18)], px, py, ang)[0]
                out.append(f'<circle cx="{qx:.1f}" cy="{qy:.1f}" r="1.5" fill="#8A5A2A"/>')
    out.append(specks(seed + 1, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), ["#B8803A", "#FFE0A8"], int(w * 0.5), (0.6, 1.2), (0.4, 0.8)))
    return "".join(out)


def marshmallow_on_stick(D, x0, y0, x1, y1, seed, toast="golden", fire=False):
    """A roasting stick from (x0, y0) to its tip (x1, y1) with a marshmallow near the tip."""
    out = [taper([(x0, y0), ((x0 + x1) / 2 + 6, (y0 + y1) / 2), (x1, y1)], 7, 3, "#7A5230")]
    out.append(taper([(x0, y0 - 2), ((x0 + x1) / 2 + 6, (y0 + y1) / 2 - 2), (x1, y1 - 2)], 2, 1, "#C8A070", 0.7))
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    mx, my = x0 + (x1 - x0) * 0.86, y0 + (y1 - y0) * 0.86
    pts = rot(rrect_pts(mx - 22, my - 17, mx + 22, my + 17, 10, 4), mx, my, ang)
    if toast == "golden":
        pal = ("#FFF0C0", "#E8A84A", "#8A4A10")
    else:
        pal = ("#6A4A3A", "#2A1A14", "#0A0604")
    out.append(painted(D, pts, pal, seed, sdir=(0.3, 1), sk=0.25, angle=ang, n=10, inkw=1.6, hi=0.5))
    if toast == "golden":
        out.append(f'<path d="{blob(mx - 6, my - 8, 12, 5, seed + 1, 0.2, 8, ang)}" fill="#FFFAEC" opacity="0.8"/>')
        out.append(taper([(mx - 6, my + 12), (mx - 4, my + 22), (mx - 6, my + 28)], 5, 3, "#FFF6E0", 0.9))
    if fire:
        out.append(D.glow(mx, my - 18, 40, "#FFB040", 0.6))
        for k, (dx, h) in enumerate(((-8, 30), (4, 40), (14, 26))):
            f = [(mx + dx, my - 10 - h), (mx + dx + 8, my - 10 - h * 0.4), (mx + dx + 6, my - 6), (mx + dx - 6, my - 6), (mx + dx - 8, my - 10 - h * 0.4)]
            out.append(f'<path d="{smooth_closed(f)}" fill="{["#FF7A2A", "#FFB43A", "#FF9A30"][k]}"/>')
        out.append(f'<path d="{smooth_closed([(mx + 4, my - 36), (mx + 9, my - 18), (mx + 4, my - 8), (mx - 1, my - 18)])}" fill="#FFF2B0"/>')
    return "".join(out)


def campfire(D, cx, base, w, seed):
    rnd = random.Random(seed)
    out = [D.glow(cx, base - w * 0.3, w * 2.2, "#FF9A3A", 0.5, ry=w * 1.2)]
    out.append(f'<ellipse cx="{cx}" cy="{base}" rx="{w * 1.1:.1f}" ry="{w * 0.24:.1f}" fill="{D.rad([(0, "#FF8A2A", 0.7), (1, "#FF8A2A", 0)])}"/>')
    # ring of stones (back half)
    for k in range(9):
        a = math.radians(180 + k * 22.5)
        x, y = cx + math.cos(a) * w * 0.85, base + math.sin(a) * w * 0.2
        out.append(painted(D, blob_pts(x, y, w * 0.13, w * 0.09, seed + k, 0.15, 10), ("#A89A8A", "#6A5E54", "#2E2622"), seed + k, sdir=(0, 1), sk=0.25, n=4, inkw=1.2, hi=0.5))
    # logs in a teepee
    for k, (a, L) in enumerate(((-70, 0.95), (-110, 0.95), (-90, 0.85), (-55, 0.8), (-125, 0.8))):
        r = math.radians(a)
        x0, y0 = cx - math.cos(r) * w * 0.55, base + 4
        x1, y1 = x0 + math.cos(r) * w * L, y0 + math.sin(r) * w * L
        out.append(taper([(x0, y0), (x1, y1)], w * 0.12, w * 0.08, "#5A3A22"))
        out.append(taper([(x0 - 2, y0 - 2), (x1 - 2, y1 - 2)], w * 0.03, w * 0.02, "#FF9A4A", 0.7))
    # flames
    for k, (dx, h, col) in enumerate(((-0.28, 0.9, "#E8501E"), (0.25, 1.0, "#E8501E"), (0, 1.35, "#FF7A2A"), (-0.15, 1.0, "#FFA43A"), (0.14, 1.05, "#FFA43A"), (0, 0.8, "#FFE07A"))):
        fx = cx + dx * w
        fh = h * w
        fw = w * (0.3 if k < 3 else 0.2)
        f = [(fx + rnd.uniform(-6, 6), base - fh), (fx + fw * 0.6, base - fh * 0.5), (fx + fw, base - fh * 0.15), (fx, base), (fx - fw, base - fh * 0.15), (fx - fw * 0.6, base - fh * 0.5)]
        out.append(f'<path d="{smooth_closed(f)}" fill="{col}" opacity="0.95"/>')
    out.append(f'<path d="{smooth_closed([(cx, base - w * 0.55), (cx + w * 0.1, base - w * 0.2), (cx, base - 2), (cx - w * 0.1, base - w * 0.2)])}" fill="#FFF8D8"/>')
    for _ in range(26):
        x, y = cx + rnd.uniform(-w * 0.8, w * 0.8), base - w * rnd.uniform(1.2, 2.6)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1, 2.2):.1f}" fill="{rnd.choice(["#FFD27A", "#FF9A3A", "#FFF2C0"])}"/>')
    # front stones
    for k in range(7):
        a = math.radians(10 + k * 26.6)
        x, y = cx + math.cos(a) * w * 0.9, base + math.sin(a) * w * 0.22
        out.append(painted(D, blob_pts(x, y, w * 0.15, w * 0.1, seed + 20 + k, 0.15, 10), ("#C8B8A8", "#8A7A6E", "#3A322C"), seed + 20 + k, sdir=(0, 1), sk=0.25, n=4, inkw=1.4, hi=0.5))
        out.append(f'<path d="{blob(x, y - w * 0.06, w * 0.1, w * 0.03, seed + 30 + k, 0.2, 8)}" fill="#FFB060" opacity="0.5"/>')
    return "".join(out)


@design("smores")
def smores():
    D = Doc2("us-sm2")
    out = [sky(D, [(0, "#0E1A30"), (0.6, "#1E2E4A"), (1, "#2E3A50")], 801, 600, ["#1A2840", "#0A1020"], 50)]
    out.append(stars_field(802, 80, (0, 0, 600, 300), avoid=((110, 50, 490, 200),)))
    out.append(D.glow(500, 230, 50, "#FFF6D8", 0.4) + '<circle cx="500" cy="230" r="16" fill="#FFF6D8"/>')
    # pine forest silhouettes, lit warm from the fire below
    out.append(hg.far_trees(D, 380, 803, "#14202E", n=30, h=(90, 160)))
    out.append(hg.far_trees(D, 410, 804, "#0E1822", n=22, h=(110, 190)))
    out.append(f'<rect y="300" width="600" height="300" fill="{D.rad([(0, "#FF9A3A", 0.35), (1, "#FF9A3A", 0)], 0.5, 0.75, 0.6)}"/>')
    # a glowing tent
    tx = 112
    tent = pp([(tx - 70, 420), (tx, 330), (tx + 70, 420)], 10, 805)
    out.append(painted(D, tent, ("#FFD27A", "#F29A3A", "#A8501A"), 805, sk=0.1, n=8, inkw=1.6, hi=0.4))
    out.append(D.glow(tx, 396, 70, "#FFD27A", 0.5))
    out.append(f'<path d="M {tx - 18} 420 L {tx} 362 L {tx + 18} 420 Z" fill="#7A3A10" opacity="0.7"/>')
    out.append(f'<path d="M {tx - 70} 420 L {tx - 94} 428 M {tx + 70} 420 L {tx + 94} 428 M {tx} 330 L {tx} 320" stroke="#2A1A10" stroke-width="2"/>')
    # ground
    out.append(f'<path d="M -10 416 Q 300 400 610 418 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#3A2A22"), (1, "#1A120E")])}"/>')
    out.append(f'<ellipse cx="300" cy="470" rx="300" ry="90" fill="{D.rad([(0, "#FF8A3A", 0.4), (1, "#FF8A3A", 0)])}"/>')
    out.append(campfire(D, 300, 468, 120, 806))
    # two roasting sticks: one perfectly golden, one ... on fire
    out.append(marshmallow_on_stick(D, 40, 560, 236, 360, 807, toast="golden"))
    out.append(marshmallow_on_stick(D, 580, 540, 380, 350, 808, toast="burnt", fire=True))
    # the assembled s'more on a flat stone
    sx, sy = 448, 518
    out.append(painted(D, blob_pts(sx, sy + 10, 92, 30, 809, 0.1, 18), ("#B8AA9A", "#7A6E62", "#3A322C"), 809, sdir=(0, 1), sk=0.2, n=10, inkw=1.6, hi=0.5))
    out.append(graham(D, sx, sy + 2, 92, 52, -4, 810))
    out.append(f'<path d="{blob(sx, sy - 10, 46, 14, 811, 0.15, 14)}" fill="#FFF6E0" stroke="#C8A070" stroke-width="1.2"/>')
    out.append(taper([(sx - 30, sy - 4), (sx - 34, sy + 10), (sx - 30, sy + 18)], 7, 4, "#FFF6E0"))
    out.append(taper([(sx + 32, sy - 6), (sx + 38, sy + 8)], 6, 4, "#FFF6E0"))
    out.append(painted(D, rect_pts(sx - 36, sy - 26, sx + 30, sy - 12, 8, 812, 0.3), ("#7A4A30", "#4A2614", "#24100A"), 812, sk=0.15, n=4, inkw=1.2, hi=0.4))
    out.append(f'<path d="M {sx - 3} {sy - 26} L {sx - 3} {sy - 12}" stroke="#24100A" stroke-width="1.4"/>')
    out.append(graham(D, sx + 2, sy - 34, 90, 50, 3, 813))
    # a chocolate bar in foil
    bx, by = 136, 528
    out.append(painted(D, rot(rect_pts(bx - 50, by - 22, bx + 50, by + 22, 10, 814, 0.4), bx, by, -8), ("#E8ECF2", "#B8C0CA", "#6A7280"), 814, sk=0.15, n=8, inkw=1.4, hi=0.6))
    bar = rot(rect_pts(bx - 48, by - 18, bx + 10, by + 18, 8, 815, 0.3), bx, by, -8)
    out.append(painted(D, bar, ("#8A5A3A", "#5A2E18", "#2A1408"), 815, sk=0.15, n=6, inkw=1.2, hi=0.4))
    for k in range(4):
        a, b = rot([(bx - 48 + k * 14.5, by - 18), (bx - 48 + k * 14.5, by + 18)], bx, by, -8)
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#2A1408" stroke-width="1.4"/>')
    a, b = rot([(bx - 48, by), (bx + 10, by)], bx, by, -8)
    out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#2A1408" stroke-width="1.4"/>')
    # lettering
    out.append(letters(D, 300, 138, "S'mores", SERIF_IT, 110, "#FFE8B0", ["#FFF2C8", "#FFD27A", "#FFB860"], 816, max_w=380,
                       shadow="#5A1E08", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 182, "BY THE CAMPFIRE", "#FFB860", font=JOS, size=22, ls=6, line_w=24, gap=12, max_w=320))
    return finish_a(D, out, 817)


# ================================================================ 26. y'all come back now — the screen door and its painted sign
def peach(D, cx, cy, r, seed):
    pts = blob_pts(cx, cy, r, r * 0.95, seed, 0.05, 16)
    out = [painted(D, pts, ("#FFE2B8", "#F8A878", "#C8604A"), seed, sdir=(0.6, 0.7), sk=0.2, angle=-50, n=int(r), inkw=1.3, hi=0.4,
                   cols=["#FFE8C8", "#E8505A", "#F6B888", "#D8404A"])]
    out.append(f'<path d="{blob(cx + r * 0.25, cy + r * 0.1, r * 0.6, r * 0.55, seed + 2, 0.15, 12)}" fill="#E04A4A" opacity="0.45"/>')
    out.append(pline([(cx - r * 0.1, cy - r * 0.8), (cx + r * 0.05, cy), (cx - r * 0.05, cy + r * 0.7)], "#C8502A", 1.4, seed, 0.6, 1))
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.35, r * 0.22, r * 0.14, seed + 1, 0.2, 8, -30)}" fill="#FFF0D8" opacity="0.7"/>')
    return "".join(out)


@design("yall-come-back-now")
def yall_come_back_now():
    D = Doc2("us-yc")
    # white clapboard siding in late-afternoon light
    out = [f'<rect width="600" height="600" fill="#F4F0E6"/>']
    for y in range(0, 520, 22):
        out.append(f'<path d="M 0 {y + 21} L 600 {y + 21}" stroke="#B8B4C4" stroke-width="3" opacity="0.7"/><path d="M 0 {y + 1} L 600 {y + 1}" stroke="#FFFFFF" stroke-width="2" opacity="0.9"/>')
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 520 L 0 520 Z", (-40, 0, 600, 520), ["#FFFFFF", "#D8D2C8"], 821, n=60, angle=0, length=(40, 140), width=(2, 5)))
    out.append(f'<rect width="600" height="520" fill="{D.lin([(0, "#FFE0A0", 0.35), (0.5, "#FFE0A0", 0), (1, "#3A3A6A", 0.2)], 0, 0, 1, 0.3)}"/>')
    # porch light
    out.append(D.glow(70, 170, 90, "#FFE0A0", 0.5))
    out.append(painted(D, rect_pts(52, 136, 88, 196, 8, 822, 0.3), ("#4A4A52", "#2A2A30", "#121216"), 822, sk=0.1, n=3, inkw=1.4, hi=0.3))
    out.append(f'<path d="{hg.org_rect(58, 146, 24, 40, 823, 0.3, 6, 2)}" fill="#FFE8A8"/>')
    # door frame trim and the screen door
    dx0, dx1, dy0, dy1 = 162, 438, 40, 520
    out.append(painted(D, rect_pts(dx0 - 22, dy0 - 22, dx1 + 22, dy1, 20, 824, 0.4), WHITE, 824, sk=0.1, n=14, inkw=1.6, hi=0.3))
    out.append(f'<path d="M {dx0} {dy0} L {dx1} {dy0} L {dx1} {dy1} L {dx0} {dy1} Z" fill="{D.lin([(0, "#6A4A3A"), (1, "#2A1A14")])}"/>')
    out.append(D.glow(300, 300, 200, "#FFC870", 0.35))
    rnd = random.Random(825)
    # hints of the hallway inside: a runner, a hall table, a lamp
    out.append(f'<path d="M 240 520 L 360 520 L 330 380 L 270 380 Z" fill="#8A2A2A" opacity="0.5"/>')
    out.append(f'<rect x="200" y="330" width="70" height="8" fill="#3A2418" opacity="0.6"/>')
    out.append(D.glow(232, 300, 40, "#FFE8A0", 0.6))
    # screen mesh
    mesh = "".join(f'<path d="M {dx0} {y} L {dx1} {y}" stroke="#1A1A20" stroke-width="0.8" opacity="0.35"/>' for y in range(dy0, dy1, 4))
    mesh += "".join(f'<path d="M {x} {dy0} L {x} {dy1}" stroke="#1A1A20" stroke-width="0.8" opacity="0.35"/>' for x in range(dx0, dx1, 4))
    out.append(mesh)
    out.append(f'<path d="M {dx0} {dy0} L {dx1} {dy0} L {dx1} {dy1} L {dx0} {dy1} Z" fill="#8A9AA8" opacity="0.18"/>')
    MINT = ("#C8F0E2", "#7ACBB4", "#2E7A68")
    for pts in (rect_pts(dx0, dy0, dx1, dy0 + 26, 14, 826, 0.3), rect_pts(dx0, dy1 - 60, dx1, dy1, 14, 827, 0.3), rect_pts(dx0, dy0, dx0 + 26, dy1, 14, 828, 0.3),
                rect_pts(dx1 - 26, dy0, dx1, dy1, 14, 829, 0.3), rect_pts(dx0, 330, dx1, 352, 14, 830, 0.3)):
        out.append(painted(D, pts, MINT, int(pts[0][0] + pts[0][1]), sdir=(0.6, 0.6), sk=0.15, angle=-90, n=10, inkw=1.6, hi=0.4))
    # gingerbread corner brackets
    for (x, y, sx_, sy_) in ((dx0 + 26, dy0 + 26, 1, 1), (dx1 - 26, dy0 + 26, -1, 1)):
        out.append(f'<path d="M {x} {y} L {x + sx_ * 46} {y} Q {x + sx_ * 18} {y + sy_ * 10} {x} {y + sy_ * 46} Z" fill="{MINT[1]}" stroke="{INK}" stroke-width="1.4"/>')
        out.append(f'<circle cx="{x + sx_ * 14}" cy="{y + sy_ * 14}" r="5" fill="#F4F0E6" stroke="{INK}" stroke-width="1.2"/>')
    # brass push bar and kick plate
    out.append(painted(D, rect_pts(dx0 + 40, 360, dx1 - 40, 372, 10, 831, 0.3), MUSTARD, 831, sk=0.15, n=4, inkw=1.2, hi=0.6))
    # the hand-painted sign hanging from a nail
    sx0, sx1, sy0, sy1 = 148, 452, 152, 300
    out.append(f'<circle cx="300" cy="96" r="4" fill="#5A5A60"/>')
    out.append(pline([(300, 96), (178, sy0 + 6)], "#C8A060", 2.4, 832, 1, 1) + pline([(300, 96), (422, sy0 + 6)], "#C8A060", 2.4, 833, 1, 1))
    out.append(cast(D, 306, sy1 + 4, 160, 12, strength=0.35, seed=834))
    out.append(painted(D, rect_pts(sx0, sy0, sx1, sy1, 16, 835, 0.6), ("#F6E8CC", "#E8D4AE", "#A88A5A"), 835, sdir=(0.5, 1), sk=0.1, angle=0, n=40, slen=(30, 90), sw=(1, 2.4), inkw=2, hi=0.3))
    for y in (sy0 + 50, sy0 + 100):
        out.append(pline([(sx0 + 4, y), (sx1 - 4, y + 1)], "#B8986A", 1.6, int(y), 0.5, 1))
    out.append(f'<path d="{hg.org_rect(sx0 + 10, sy0 + 10, sx1 - sx0 - 20, sy1 - sy0 - 20, 836, 0.4, 12, 4)}" fill="none" stroke="#2E7A68" stroke-width="2"/>')
    out.append(letters(D, 300, sy0 + 82, "Y'all", SERIF_IT, 86, "#A8301E", ["#C8402A", "#7A1A10"], 837, max_w=240, shadow="#FFF6E0", soff=(0.02, 0.03), angle=-40))
    out.append(label(300, sy0 + 124, "COME BACK NOW", BEBAS, 34, "#2E5A4A", ls=5, max_w=260))
    for k, x in enumerate((sx0 + 34, sx1 - 34)):
        for j in range(5):
            a = math.radians(j * 72 - 90)
            out.append(f'<path d="{blob(x + math.cos(a) * 7, sy0 + 46 + math.sin(a) * 7, 7, 4.5, 838 + k * 9 + j, 0.1, 8, math.degrees(a))}" fill="#FFFDF4" stroke="#B8A888" stroke-width="0.8"/>')
        out.append(f'<circle cx="{x}" cy="{sy0 + 46}" r="3" fill="#E8C048"/>')
    # porch floor, mat, peaches, geraniums
    out.append(wood_planks(D, 516, 600, 840, ("#B8B8C4", "#8A8A98", "#4A4A58"), 3))
    out.append(f'<rect y="512" width="600" height="8" fill="#2A2A34" opacity="0.4"/>')
    mat = pp([(196, 512), (404, 512), (420, 558), (180, 558)], 12, 841)
    out.append(painted(D, mat, ("#E8C890", "#C8A060", "#7A5A2A"), 841, sk=0.1, n=30, angle=-90, slen=(4, 10), sw=(0.8, 1.4), inkw=1.4, hi=0.3))
    out.append(label(300, 541, "YA HEAR?", BEBAS, 24, "#5A3A1A", ls=6, max_w=180))
    # bushel of Georgia peaches
    bx, bb = 504, 576
    out.append(cast(D, bx + 6, bb + 2, 70, 8, strength=0.5, seed=842))
    bas = pp([(bx - 56, bb - 64), (bx + 56, bb - 64), (bx + 44, bb), (bx - 44, bb)], 10, 843)
    out.append(painted(D, bas, ("#E8C08A", "#C08A4A", "#7A5228"), 843, sk=0.15, n=16, angle=0, inkw=1.6, hi=0.4))
    for y in range(int(bb - 56), int(bb), 10):
        out.append(pline([(bx - 52, y), (bx + 52, y)], "#8A5A2A", 1.2, y, 0.5, 1))
    for k, (x, y) in enumerate(((-30, -70), (0, -78), (30, -70), (-14, -92), (16, -90), (44, -82))):
        out.append(peach(D, bx + x, bb + y, 20, 844 + k))
    out.append(leaf_simple(D, bx - 2, bb - 104, 30, 10, -60, ("#A8D870", "#4A9A3A", "#1E5A1E"), 851))
    # geraniums in a clay pot
    gx, gb = 92, 578
    out.append(cast(D, gx + 6, gb + 2, 50, 7, strength=0.5, seed=852))
    out.append(painted(D, pp([(gx - 38, gb - 60), (gx + 38, gb - 60), (gx + 30, gb), (gx - 30, gb)], 10, 853), ("#EE9E72", "#C8603A", "#7A3218"), 853, sk=0.15, n=8, inkw=1.6, hi=0.4))
    for k in range(10):
        a = rnd.uniform(-2.9, -0.2)
        out.append(leaf_simple(D, gx, gb - 60, rnd.uniform(26, 40), 14, math.degrees(a), ("#A8D870", "#4A9A3A", "#1E5A1E"), 854 + k, vein=False, inkw=1))
    for k, (x, y) in enumerate(((gx - 24, gb - 104), (gx + 14, gb - 112), (gx + 34, gb - 90), (gx - 2, gb - 86))):
        for j in range(9):
            a = rnd.uniform(0, 6.28)
            out.append(f'<circle cx="{x + math.cos(a) * rnd.uniform(0, 12):.1f}" cy="{y + math.sin(a) * rnd.uniform(0, 10):.1f}" r="5" fill="{rnd.choice(["#E8304A", "#D8202A", "#FF5A6A"])}" stroke="#7A0A1A" stroke-width="0.8"/>')
    return finish_a(D, out, 870)


# ================================================================ 27. home sweet home — a cross-stitch sampler in its hoop
HOUSE_PX = [
    "......RR......",
    ".....RRRR.....",
    "....RRRRRR....",
    "...RRRRRRRR...",
    "..RRRRRRRRRR..",
    ".RRRRRRRRRRRR.",
    "..CCCCCCCCCC..",
    "..CBBCCCCBBC..",
    "..CBBCCCCBBC..",
    "..CCCCNNCCCC..",
    "..CBBCNNCBBC..",
    "..CBBCNNCBBC..",
    "..CCCCNNCCCC..",
]
HEART_PX = [".RR.RR.", "RRRRRRR", "RRRRRRR", ".RRRRR.", "..RRR..", "...R..."]
TREE_PX = ["..G..", ".GGG.", "GGGGG", ".GGG.", "GGGGG", "..W.."]


def xstitch(x0, y0, px, cell, cols, seed, w=None):
    """Cross-stitches on the linen grid for a little pixel motif."""
    rnd = random.Random(seed)
    w = w or cell * 0.3
    out = []
    for r, row in enumerate(px):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            col = cols[ch]
            x, y = x0 + c * cell, y0 + r * cell
            j = lambda: rnd.uniform(-0.3, 0.3)
            out.append(f'<path d="M {x + 1 + j():.1f} {y + 1 + j():.1f} L {x + cell - 1 + j():.1f} {y + cell - 1 + j():.1f}" stroke="{dk(col, 0.12)}" stroke-width="{w:.1f}" stroke-linecap="round"/>')
            out.append(f'<path d="M {x + cell - 1 + j():.1f} {y + 1 + j():.1f} L {x + 1 + j():.1f} {y + cell - 1 + j():.1f}" stroke="{col}" stroke-width="{w:.1f}" stroke-linecap="round"/>')
    return "".join(out)


@design("home-sweet-home")
def home_sweet_home():
    D = Doc2("us-hs")
    # pine-board wall behind the hoop
    out = [wood_planks(D, 0, 600, 861, ("#F2DCB8", "#DDBE90", "#A8865A"), 5, vertical=True)]
    out.append(soft_glow(D, 300, 300, 300, "#FFF6E0", 0.4))
    cx, cy, R = 300, 316, 226
    out.append(cast(D, cx + 10, cy + 16, R * 1.02, R * 1.02, strength=0.4, seed=862))
    # linen
    lin = blob(cx, cy, R - 6, R - 6, 863, 0.003, 60)
    out.append(f'<path d="{lin}" fill="#F6EEDC"/>')
    cid = D.clip(f'<path d="{lin}"/>')
    weave = "".join(f'<path d="M {cx - R} {y} L {cx + R} {y}" stroke="#D8CCB4" stroke-width="0.8" opacity="0.6"/>' for y in range(int(cy - R), int(cy + R), 5))
    weave += "".join(f'<path d="M {x} {cy - R} L {x} {cy + R}" stroke="#D8CCB4" stroke-width="0.8" opacity="0.5"/>' for x in range(int(cx - R), int(cx + R), 5))
    weave += f'<path d="{lin}" fill="{D.rad([(0, "#FFFFFF", 0.0), (0.8, "#FFFFFF", 0), (1, "#8A7A5A", 0.25)])}"/>'
    out.append(f'<g {cid}>{weave}</g>')
    cols = {"R": "#C8302A", "C": "#F2E6CC", "B": "#2E4A8A", "N": "#8A5A2A", "G": "#3E7A44", "W": "#7A5230"}
    cols["C"] = "#E8C878"
    # top line, little house with trees and hearts, a stitched border band
    out.append(stitched(D, cx, 214, "Home", SERIF_IT, 74, ("#E8604A", "#C8302A", "#8A1A14"), 864, max_w=260))
    out.append(stitched(D, cx, 270, "Sweet Home", SERIF_IT, 58, ("#5A7AC8", "#2E4A8A", "#14244A"), 865, max_w=320))
    cell = 9
    out.append(xstitch(cx - 7 * cell, 300, HOUSE_PX, cell, cols, 866))
    for k, x in enumerate((cx - 7 * cell - 66, cx + 7 * cell + 22)):
        out.append(xstitch(x, 348, TREE_PX, 9, cols, 867 + k))
    for k, x in enumerate((cx - 150, cx + 92)):
        out.append(xstitch(x, 312, HEART_PX, 8, cols, 869 + k))
    for k in range(13):
        x = cx - 156 + k * 26
        if k % 2:
            out.append(xstitch(x, 438, ["RR", "RR"], 6, cols, 870 + k))
        else:
            out.append(xstitch(x, 438, ["BB", "BB"], 6, cols, 870 + k))
    out.append(stitched(D, cx, 494, "BLESS THIS HOUSE", JOS, 20, ("#7AA0C8", "#3E5A8A", "#1E2E4A"), 885, max_w=220, ls=3))
    for k, x in enumerate((cx - 142, cx + 142)):
        out.append(lazy_daisy(x, 487, 11, "#E8607A", 886 + k, center="#F6C21C"))
    out.append(lazy_daisy(cx, 152, 11, "#E8607A", 888, center="#F6C21C"))
    for k, (x, a) in enumerate(((cx - 20, 200), (cx + 20, -20))):
        out.append(stitch_leaf(x, 152, 22, a, "#4A8A4A", 889 + k))
    # the wooden hoop: inner and outer rings with the brass screw at the top
    for rr, w, pal in ((R, 16, OAK), (R + 9, 12, ("#F2D0A0", "#D8A868", "#8A5A2A"))):
        out.append(ink(smooth_closed(blob_pts(cx, cy, rr, rr, 890, 0.003, 60)), pal[2], w + 3, 891, 1, 1))
        out.append(ink(smooth_closed(blob_pts(cx, cy, rr, rr, 890, 0.003, 60)), pal[1], w, 892, 1, 1))
        out.append(taper(ell_pts(cx, cy, rr - w * 0.2, rr - w * 0.2, 200, 320, 16), w * 0.25, w * 0.25, pal[0], 0.8))
    out.append(painted(D, rect_pts(cx - 20, cy - R - 28, cx + 20, cy - R - 6, 6, 893, 0.3), ("#F2D0A0", "#D8A868", "#8A5A2A"), 893, sk=0.15, n=4, inkw=1.4, hi=0.4))
    out.append(painted(D, rect_pts(cx - 30, cy - R - 24, cx + 30, cy - R - 16, 6, 894, 0.3), MUSTARD, 894, sk=0.15, n=3, inkw=1.2, hi=0.6))
    out.append(f'<circle cx="{cx - 32}" cy="{cy - R - 20}" r="6" fill="{MUSTARD[1]}" stroke="{INK}" stroke-width="1.2"/>')
    # a needle and red thread tucked in
    out.append(taper([(cx + 150, 196), (cx + 196, 150)], 2.4, 1.2, "#C8D0DA"))
    out.append(pline([(cx + 152, 194), (cx + 186, 230), (cx + 214, 214), (cx + 230, 250)], "#C8302A", 1.8, 895, 0.95, 1))
    return finish_a(D, out, 896)


# ================================================================ 28. bald eagle — field-guide plate
def eagle(D, cx, cy, s, seed):
    """Bald eagle perched, three-quarter view facing left: white head and hooked yellow beak, dark brown
    body with layered feathers, folded wing, white tail, feathered legs and yellow talons."""
    rnd = random.Random(seed)
    BR = ("#8A6A50", "#4A3020", "#1E120A")
    out = []
    # tail (behind)
    tail = [(cx + s * 0.06, cy + s * 0.5), (cx + s * 0.3, cy + s * 0.52), (cx + s * 0.38, cy + s * 0.92), (cx + s * 0.18, cy + s * 0.98), (cx + s * 0.02, cy + s * 0.9)]
    out.append(painted(D, tail, WHITE, seed, sdir=(1, 0.3), sk=0.2, angle=80, n=14, inkw=1.6, hi=0.4))
    for k in range(5):
        out.append(pline([(cx + s * (0.1 + k * 0.05), cy + s * 0.56), (cx + s * (0.06 + k * 0.07), cy + s * 0.94)], "#B8B0A6", 1.2, seed + k, 0.6, 1))
    # body
    body = [(cx - s * 0.14, cy - s * 0.3), (cx + s * 0.16, cy - s * 0.3), (cx + s * 0.3, cy - s * 0.05), (cx + s * 0.32, cy + s * 0.3), (cx + s * 0.22, cy + s * 0.58),
            (cx - s * 0.02, cy + s * 0.6), (cx - s * 0.2, cy + s * 0.38), (cx - s * 0.24, cy + s * 0.05)]
    out.append(painted(D, body, BR, seed + 1, sdir=(0.7, 0.4), sk=0.2, angle=80, n=40, slen=(s * 0.04, s * 0.12), sw=(1, 2.6), inkw=2, hi=0.3))
    from fall_gouache_a import feather_rows
    out.append(feather_rows(cx - s * 0.02, cy + s * 0.18, s * 0.2, s * 0.32, seed + 3, "#8A6A50", rows=8, per=5, s=s * 0.035, w=1.6, op=0.6))
    # folded wing over the body
    wing = [(cx + s * 0.02, cy - s * 0.22), (cx + s * 0.26, cy - s * 0.16), (cx + s * 0.36, cy + s * 0.12), (cx + s * 0.34, cy + s * 0.5), (cx + s * 0.24, cy + s * 0.72),
            (cx + s * 0.12, cy + s * 0.5), (cx + s * 0.04, cy + s * 0.2)]
    out.append(painted(D, wing, ("#7A5A40", "#3A2416", "#140A04"), seed + 4, sdir=(0.8, 0.3), sk=0.18, angle=75, n=30, inkw=1.8, hi=0.25))
    for k in range(6):
        y = cy + s * (0.14 + k * 0.09)
        out.append(pline([(cx + s * 0.08, y - s * 0.02), (cx + s * 0.2, y + s * 0.04), (cx + s * 0.32, y + s * 0.03)], "#A8886A", 1.4, seed + 10 + k, 0.55, 1))
    for k in range(5):
        a, b = (cx + s * (0.16 + k * 0.035), cy + s * 0.44), (cx + s * (0.2 + k * 0.02), cy + s * 0.72)
        out.append(pline([a, b], "#0A0402", 1.4, seed + 20 + k, 0.6, 1))
    # white head and neck
    head = [(cx - s * 0.16, cy - s * 0.24), (cx - s * 0.24, cy - s * 0.42), (cx - s * 0.2, cy - s * 0.58), (cx - s * 0.04, cy - s * 0.66), (cx + s * 0.12, cy - s * 0.6),
            (cx + s * 0.18, cy - s * 0.42), (cx + s * 0.16, cy - s * 0.22), (cx + s * 0.02, cy - s * 0.16)]
    out.append(painted(D, head, WHITE, seed + 5, sdir=(0.8, 0.5), sk=0.15, angle=-80, n=24, inkw=1.8, hi=0.4))
    for k in range(10):
        x = cx + s * rnd.uniform(-0.14, 0.14)
        y = cy - s * rnd.uniform(0.2, 0.3)
        out.append(pline([(x, y), (x + s * 0.02, y + s * 0.05)], "#C8C0B6", 1.4, seed + 30 + k, 0.7, 1))
    # hooked yellow beak
    beak = [(cx - s * 0.2, cy - s * 0.52), (cx - s * 0.32, cy - s * 0.52), (cx - s * 0.42, cy - s * 0.46), (cx - s * 0.42, cy - s * 0.38), (cx - s * 0.36, cy - s * 0.4),
            (cx - s * 0.3, cy - s * 0.42), (cx - s * 0.2, cy - s * 0.4)]
    out.append(painted(D, beak, MUSTARD, seed + 6, sdir=(0.3, 1), sk=0.2, angle=0, n=8, inkw=1.6, hi=0.5))
    out.append(pline([(cx - s * 0.36, cy - s * 0.44), (cx - s * 0.26, cy - s * 0.44), (cx - s * 0.2, cy - s * 0.45)], "#8A5A0A", 1.4, seed, 0.8, 1))
    out.append(f'<path d="{blob(cx - s * 0.26, cy - s * 0.5, s * 0.02, s * 0.01, seed, 0.1, 6)}" fill="#3A2A0A"/>')
    # fierce eye with brow
    ex, ey = cx - s * 0.12, cy - s * 0.52
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{s * 0.032:.1f}" fill="#F6D23A" stroke="#3A2A0A" stroke-width="1.2"/>')
    out.append(f'<circle cx="{ex - s * 0.004:.1f}" cy="{ey:.1f}" r="{s * 0.016:.1f}" fill="#0A0604"/><circle cx="{ex - s * 0.012:.1f}" cy="{ey - s * 0.01:.1f}" r="{s * 0.006:.1f}" fill="#FFFFFF"/>')
    out.append(taper([(ex - s * 0.06, ey - s * 0.035), (ex + s * 0.04, ey - s * 0.05)], s * 0.025, s * 0.01, "#E8E2D8"))
    out.append(pline([(ex - s * 0.06, ey - s * 0.03), (ex + s * 0.04, ey - s * 0.045)], "#7A7268", 1.4, seed, 0.8, 1))
    # feathered legs and talons gripping the branch
    for k, dx in enumerate((-0.06, 0.1)):
        lx = cx + s * dx
        out.append(painted(D, pp([(lx - s * 0.06, cy + s * 0.48), (lx + s * 0.06, cy + s * 0.48), (lx + s * 0.05, cy + s * 0.62), (lx - s * 0.05, cy + s * 0.62)], 8, seed + 40 + k), BR, seed + 40 + k, sk=0.2, n=6, inkw=1.4, hi=0.3))
        for j, (tx, ty) in enumerate(((-0.08, 0.7), (-0.02, 0.72), (0.04, 0.7))):
            out.append(taper([(lx, cy + s * 0.62), (lx + s * tx, cy + s * ty)], s * 0.035, s * 0.025, "#F2C83A"))
            out.append(taper([(lx + s * tx, cy + s * ty), (lx + s * (tx - 0.01), cy + s * (ty + 0.03))], s * 0.015, s * 0.004, "#1A1008"))
    return "".join(out)


@design("bald-eagle")
def bald_eagle():
    D = Doc2("us-be")
    out = [paper(D.nid(), "#F6EEDC", FLECK, 901)]
    out.append(blooms(902, ["#C8D8E8", "#E8D8C0", "#D8E4D0"], 6, (60, 60, 540, 540), (100, 180), (0.08, 0.14)))
    # plate frame with corner dots
    out.append(f'<path d="{hg.org_rect(58, 58, 484, 484, 903, 0.4, 20, 2)}" fill="none" stroke="#22386A" stroke-width="2.4"/>')
    out.append(f'<path d="{hg.org_rect(68, 68, 464, 464, 904, 0.4, 20, 2)}" fill="none" stroke="#22386A" stroke-width="1.2"/>')
    for (x, y) in ((58, 58), (542, 58), (58, 542), (542, 542)):
        out.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#B8352A"/>')
    out.append(ruled(300, 106, "BIRDS OF AMERICA · No. 1", "#22386A", font=MONO, size=17, ls=3, line_w=28, gap=10, max_w=380))
    # a faint wash of mountains and sky behind the bird
    out.append(f'<path d="{blob(300, 300, 190, 150, 905, 0.08, 20)}" fill="#C8DCEC" opacity="0.45"/>')
    out.append(hill(D, ridge([(130, 380), (200, 300), (260, 336), (330, 268), (420, 330), (470, 380)], 906, 5), 400, ("#E8EEF4", "#B8C8D8", "#7A90A8"), 906, inkw=0, sop=(0.06, 0.16)))
    # pine branch
    out.append(taper([(110, 416), (300, 402), (500, 410)], 14, 8, "#6A4A2E"))
    out.append(taper([(110, 412), (300, 398), (500, 406)], 3, 2, "#A8805A", 0.8))
    rnd = random.Random(907)
    for k in range(9):
        bx = 120 + k * 46
        by = 408 - (bx - 110) * 0.02
        for j in range(12):
            a = math.radians(rnd.uniform(-160, -20) if j % 2 else rnd.uniform(20, 160))
            L = rnd.uniform(18, 30)
            out.append(taper([(bx, by), (bx + math.cos(a) * L, by + math.sin(a) * L)], 2.4, 0.6, rnd.choice(["#2E5A3A", "#3E7A4A", "#1E4A2A"])))
    out.append(painted(D, blob_pts(452, 434, 12, 20, 908, 0.05, 12, 10), ("#C8946A", "#8A5A34", "#4A2E14"), 908, sk=0.2, n=6, inkw=1.4, hi=0.3))
    for k in range(5):
        out.append(f'<path d="M {442} {422 + k * 6} Q 452 {426 + k * 6} 462 {422 + k * 6}" stroke="#4A2E14" stroke-width="1" fill="none"/>')
    out.append(eagle(D, 304, 282, 190, 909))
    # name
    out.append(letters(D, 300, 498, "Bald Eagle", SERIF_IT, 64, "#22386A", ["#2E4A8A", "#14244A"], 910, max_w=360,
                       shadow="#FFFFFF", soff=(0.015, 0.025), angle=-40, wob=0.5))
    out.append(label(300, 524, "HALIAEETUS LEUCOCEPHALUS", JOS, 15, "#7A5A3A", ls=3, max_w=320))
    return finish_a(D, out, 911)


# ================================================================ 29. short stack — pancakes at the diner counter
def boomerang_formica(D, seed, top=0, bot=600, base="#9ED8D0"):
    rnd = random.Random(seed)
    out = [f'<rect y="{top}" width="600" height="{bot - top}" fill="{base}"/>']
    for _ in range(46):
        x, y = rnd.uniform(-20, 620), rnd.uniform(top, bot)
        a = rnd.uniform(0, 360)
        c = rnd.choice(["#F2E8D0", "#E86A5A", "#2E4A6A", "#F6C21C"])
        out.append(f'<path d="M {x:.1f} {y:.1f} q 10 -12 22 -4 q -10 -2 -14 10 Z" fill="{c}" opacity="0.55" transform="rotate({a:.0f} {x:.1f} {y:.1f})"/>')
    for _ in range(60):
        out.append(f'<circle cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(top, bot):.1f}" r="1.4" fill="{rnd.choice(["#FFFFFF", "#2E4A6A"])}" opacity="0.6"/>')
    return "".join(out)


def pancake(D, cx, cy, rx, ry, th, seed):
    out = [painted(D, ell_pts(cx, cy + th, rx, ry, 0, 180, 18) + ell_pts(cx, cy, rx * 1.01, ry, 180, 0, 18)[1:-1], ("#F6DCA0", "#E2B060", "#9A6A2A"), seed, sdir=(0.3, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.3)]
    top = blob_pts(cx, cy, rx, ry, seed + 1, 0.03, 26)
    out.append(painted(D, top, ("#F2B860", "#C8782A", "#7A400E"), seed + 2, sdir=(0.3, 1), sk=0.06, angle=10, n=20, inkw=1.4, hi=0.25, cols=["#E8A048", "#A85A1A", "#F6C878"]))
    out.append(f'<path d="{blob(cx, cy, rx * 0.86, ry * 0.8, seed + 3, 0.04, 20)}" fill="#B8681E" opacity="0.3"/>')
    out.append(specks(seed + 4, (cx - rx * 0.7, cy - ry * 0.6, cx + rx * 0.7, cy + ry * 0.6), ["#8A4A10", "#F6D08A"], int(rx * 0.4), (0.8, 1.8), (0.4, 0.8)))
    return "".join(out)


@design("short-stack")
def short_stack():
    D = Doc2("us-ss")
    out = [f'<rect width="600" height="600" fill="#FFF6E8"/>']
    # diner wall: cream with a red band and chrome trim, a menu board
    out.append(f'<rect y="200" width="600" height="26" fill="#D8302A"/>')
    out.append(fluted(D, "M 0 226 L 600 226 L 600 240 L 0 240 Z", (0, 226, 600, 240), 921, top="#FFFFFF", mid="#C8D0DA", bot="#6A7280", step=4))
    out.append(boomerang_formica(D, 922, 240, 600))
    out.append(f'<rect y="240" width="600" height="360" fill="{D.rad([(0, "#FFFFFF", 0.3), (1, "#000000", 0.12)], 0.5, 0.4, 0.7)}"/>')
    # a cup of coffee in a heavy diner mug
    mx, mb = 478, 392
    out.append(cast(D, mx + 8, mb + 2, 60, 10, strength=0.45, seed=923))
    out.append(ink(f"M {mx + 34} {mb - 70} q 34 4 28 32 q -4 20 -30 18", "#B8B0A6", 12, 924, 1, 1))
    out.append(ink(f"M {mx + 34} {mb - 70} q 34 4 28 32 q -4 20 -30 18", "#FFFFFF", 5, 925, 1, 0.8))
    out.append(painted(D, pp([(mx - 40, mb - 96), (mx + 40, mb - 96), (mx + 36, mb), (mx - 36, mb)], 10, 926), WHITE, 926, sdir=(0.9, 0.2), sk=0.2, angle=-90, n=10, inkw=1.8, hi=0.5))
    out.append(pline([(mx - 39, mb - 80), (mx + 39, mb - 80)], "#2E8A80", 3, 927, 0.9, 1))
    out.append(f'<path d="{smooth_closed(ell_pts(mx, mb - 96, 40, 9, 0, 360, 18)[:-1])}" fill="#4A2410" stroke="#B8B0A6" stroke-width="3"/>')
    out.append(steam(mx, mb - 108, 46, 928, "#FFFFFF", 2, 18, 6, 0.6))
    # the plate and the stack
    cx = 262
    out.append(cast(D, cx + 14, 530, 200, 24, strength=0.5, seed=929))
    out.append(painted(D, ell_pts(cx, 504, 200, 54, 0, 360, 40)[:-1], WHITE, 930, sdir=(0.3, 1), sk=0.1, angle=0, n=14, inkw=1.8, hi=0.4))
    out.append(ink(smooth_closed(ell_pts(cx, 504, 180, 46, 0, 360, 40)[:-1]), "#2E8A80", 2.6, 931, 1, 0.8))
    for k in range(5):
        out.append(pancake(D, cx + (k % 2) * 6 - 3, 482 - k * 30, 150 - k * 3, 40, 24, 932 + k * 5))
    top_y = 482 - 4 * 30
    # syrup pouring from a little glass pitcher and running down the sides
    out.append(f'<path d="{blob(cx + 6, top_y + 2, 112, 26, 960, 0.1, 18)}" fill="#A8540E" opacity="0.88"/>')
    out.append(f'<path d="{blob(cx - 20, top_y - 4, 50, 8, 961, 0.2, 12)}" fill="#E8A040" opacity="0.7"/>')
    for k, (x, L) in enumerate(((cx - 96, 80), (cx - 40, 120), (cx + 40, 60), (cx + 104, 100), (cx + 10, 150))):
        out.append(taper([(x, top_y + 14), (x + 2, top_y + 14 + L * 0.6), (x, top_y + 14 + L)], 12, 9, "#A8540E", 0.9))
        out.append(f'<circle cx="{x:.1f}" cy="{top_y + 14 + L:.1f}" r="6.5" fill="#A8540E" opacity="0.9"/>')
        out.append(taper([(x - 3, top_y + 18), (x - 2, top_y + 10 + L * 0.6)], 2.4, 1.4, "#F6C878", 0.8))
    pxx, pyy = cx + 150, top_y - 100
    pit = rot(rrect_pts(pxx - 30, pyy - 44, pxx + 30, pyy + 34, 12, 4), pxx, pyy, -100)
    out.append(painted(D, pit, ("#F4FAFC", "#D8E8EE", "#8AA4B0"), 962, sk=0.15, n=6, inkw=1.6, hi=0.6))
    syr = rot(rrect_pts(pxx - 26, pyy - 6, pxx + 26, pyy + 30, 10, 4), pxx, pyy, -100)
    out.append(f'<path d="{pd(syr)}" fill="#B8601A" opacity="0.8"/>')
    lid = rot(rrect_pts(pxx - 32, pyy - 62, pxx + 32, pyy - 42, 8, 3), pxx, pyy, -100)
    out.append(painted(D, lid, CHROME, 964, sk=0.15, n=4, inkw=1.4, hi=0.6))
    sp = rot([(pxx - 22, pyy - 62), (pxx - 34, pyy - 84), (pxx - 26, pyy - 86), (pxx - 12, pyy - 62)], pxx, pyy, -100)
    out.append(f'<path d="{pd(sp)}" fill="#C8D0DA" stroke="{INK}" stroke-width="1.2"/>')
    out.append(taper(rot([(pxx - 22, pyy - 36), (pxx - 22, pyy + 24)], pxx, pyy, -100), 4, 2, "#FFFFFF", 0.7))
    out.append(taper([(pxx - 78, pyy + 44), (pxx - 92, pyy + 70), (cx + 46, top_y + 2)], 6, 4, "#B8600E", 0.95))
    # butter pat melting on top, blueberries scattered
    bx, by = cx - 14, top_y - 12
    out.append(painted(D, pp([(bx - 26, by - 6), (bx + 20, by - 14), (bx + 30, by + 6), (bx - 16, by + 14)], 8, 965), ("#FFFCE0", "#FFE88A", "#D8B040"), 965, sk=0.15, n=6, inkw=1.2, hi=0.6))
    out.append(taper([(bx - 18, by - 2), (bx + 10, by - 8)], 3, 1, "#FFFFFF", 0.9))
    rnd = random.Random(966)
    for _ in range(9):
        x, y = cx + rnd.uniform(-170, 170), 510 + rnd.uniform(-14, 22)
        if abs(x - cx) < 140 and y < 520:
            continue
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#3A4A8A" stroke="#14204A" stroke-width="1"/><circle cx="{x - 2:.1f}" cy="{y - 2:.1f}" r="2.4" fill="#A8B8E8"/>')
    for x, y in ((cx - 50, top_y - 4), (cx + 40, top_y + 4), (cx + 10, top_y - 16)):
        out.append(f'<circle cx="{x}" cy="{y}" r="8" fill="#3A4A8A" stroke="#14204A" stroke-width="1"/><circle cx="{x - 2}" cy="{y - 2}" r="2.4" fill="#A8B8E8"/>')
    # fork
    out.append(taper([(80, 560), (128, 430)], 7, 6, "#C8D0DA"))
    for k in range(4):
        out.append(taper([(124 + k * 5, 432), (134 + k * 5, 396)], 2.4, 2, "#B8C0CA"))
    # lettering
    out.append(letters(D, 300, 128, "Short Stack", SERIF_IT, 92, "#B8352A", ["#D8503A", "#8A1E12", "#E8704A"], 967, max_w=440,
                       shadow="#FFE8C8", soff=(0.02, 0.03), angle=-40, hi="#FFC8A8"))
    out.append(ruled(300, 172, "EXTRA SYRUP, HON", "#2E6A64", font=JOS, size=21, ls=6, line_w=24, gap=12, max_w=320))
    return finish_a(D, out, 968)


# ================================================================ 30. howdy, partner — boots and hat on the ranch fence
def cowboy_boot(D, x, base, s, seed, pal=LEATHER, stitch="#F6D8A0", flip=1):
    """A tooled leather cowboy boot in side view, toe to the right: tall shaft with stitched scrolls and pull
    straps, a pointed toe, an underslung heel, and a spur."""
    def P(u, v):
        return (x + u * s * flip, base + v * s)
    out = [cast(D, x + s * 0.1 * flip, base, s * 0.55, s * 0.05, strength=0.5, seed=seed)]
    shaft = [P(-0.26, -0.3), P(-0.28, -0.98), P(-0.2, -1.04), P(0.06, -1.04), P(0.14, -0.98), P(0.1, -0.42), P(0.16, -0.3)]
    foot = [P(-0.3, -0.06), P(-0.28, -0.34), P(0.1, -0.38), P(0.3, -0.28), P(0.56, -0.12), P(0.66, -0.04), P(0.6, 0.0), P(-0.08, 0.0)]
    out.append(painted(D, shaft, pal, seed, sdir=(0.8, 0.3), sk=0.2, angle=-90, n=30, inkw=2, hi=0.35))
    cid = D.clip(f'<path d="{smooth_closed(shaft)}"/>')
    sc = []
    for k in range(3):
        cyy = -0.88 + k * 0.2
        sc.append(f'<path d="M {P(-0.18, cyy)[0]:.1f} {P(-0.18, cyy)[1]:.1f} Q {P(-0.06, cyy - 0.12)[0]:.1f} {P(-0.06, cyy - 0.12)[1]:.1f} {P(0.04, cyy)[0]:.1f} {P(0.04, cyy)[1]:.1f} '
                  f'Q {P(-0.06, cyy + 0.1)[0]:.1f} {P(-0.06, cyy + 0.1)[1]:.1f} {P(-0.18, cyy)[0]:.1f} {P(-0.18, cyy)[1]:.1f}" stroke="{stitch}" stroke-width="1.6" fill="none" stroke-dasharray="3 2"/>')
    sc.append(f'<path d="M {P(-0.08, -1.0)[0]:.1f} {P(-0.08, -1.0)[1]:.1f} L {P(-0.07, -0.4)[0]:.1f} {P(-0.07, -0.4)[1]:.1f}" stroke="{dk(pal[2], 0.3)}" stroke-width="1.4" opacity="0.6"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(painted(D, foot, (lt(pal[1], 0.15), dk(pal[1], 0.15), pal[2]), seed + 1, sdir=(0.3, 1), sk=0.2, angle=0, n=20, inkw=2, hi=0.45))
    out.append(pline([P(-0.2, -0.3), P(0.12, -0.32), P(0.4, -0.2), P(0.58, -0.08)], stitch, 1.6, seed, 0.8, 1))
    out.append(painted(D, pp([P(-0.3, -0.12), P(-0.08, -0.12), P(-0.1, 0.0), P(-0.28, 0.0)], 6, seed + 2), ("#5A3A22", "#2E1C10", "#140A04"), seed + 2, sk=0.15, n=4, inkw=1.6, hi=0.3))
    out.append(taper([P(-0.32, -0.02), P(0.62, -0.01)], s * 0.025, s * 0.02, "#2E1C10"))
    for k in (-1, 1):
        tx = -0.2 if k < 0 else 0.04
        out.append(ink(smooth_open([P(tx, -1.02), P(tx + 0.03 * k, -1.12), P(tx + 0.06 * k, -1.02)]), dk(pal[2], 0.2), 4, seed + 3 + k, 1, 1))
    # spur
    sx, sy = P(-0.32, -0.1)
    out.append(taper([(sx, sy), (sx - s * 0.12 * flip, sy - s * 0.02)], 3, 2, "#B8C0CA"))
    for k in range(8):
        a = math.radians(k * 45)
        out.append(f'<path d="M {sx - s * 0.14 * flip:.1f} {sy - s * 0.02:.1f} l {math.cos(a) * s * 0.04:.1f} {math.sin(a) * s * 0.04:.1f}" stroke="#C8D0DA" stroke-width="2"/>')
    return "".join(out)


def cowboy_hat(D, cx, cy, s, seed, pal=("#E8C890", "#C8A060", "#7A5A2A"), band="#5A2A1A"):
    out = [cast(D, cx + s * 0.05, cy + s * 0.18, s * 0.7, s * 0.12, strength=0.35, seed=seed)]
    brim = [(cx - s * 0.62, cy - s * 0.1), (cx - s * 0.4, cy + s * 0.06), (cx, cy + s * 0.12), (cx + s * 0.4, cy + s * 0.06), (cx + s * 0.62, cy - s * 0.1),
            (cx + s * 0.48, cy - s * 0.02), (cx, cy + s * 0.02), (cx - s * 0.48, cy - s * 0.02)]
    out.append(painted(D, brim, pal, seed, sdir=(0.3, 1), sk=0.2, angle=0, n=16, inkw=1.8, hi=0.45))
    crown = [(cx - s * 0.3, cy - s * 0.02), (cx - s * 0.32, cy - s * 0.3), (cx - s * 0.2, cy - s * 0.44), (cx - s * 0.06, cy - s * 0.38), (cx, cy - s * 0.44),
             (cx + s * 0.06, cy - s * 0.38), (cx + s * 0.2, cy - s * 0.44), (cx + s * 0.32, cy - s * 0.3), (cx + s * 0.3, cy - s * 0.02)]
    out.append(painted(D, crown, pal, seed + 1, sdir=(0.8, 0.3), sk=0.2, angle=-90, n=16, inkw=1.8, hi=0.4))
    out.append(pline([(cx, cy - s * 0.42), (cx + s * 0.01, cy - s * 0.2)], pal[2], 1.6, seed, 0.6, 1))
    out.append(painted(D, pp([(cx - s * 0.31, cy - s * 0.12), (cx + s * 0.31, cy - s * 0.12), (cx + s * 0.3, cy - s * 0.03), (cx - s * 0.3, cy - s * 0.03)], 8, seed + 2), (lt(band, 0.3), band, dk(band, 0.4)), seed + 2, sk=0.15, n=4, inkw=1.2, hi=0.3))
    for k in range(5):
        out.append(f'<circle cx="{cx - s * 0.24 + k * s * 0.12:.1f}" cy="{cy - s * 0.075:.1f}" r="{s * 0.012:.1f}" fill="#E8ECF0"/>')
    return "".join(out)


@design("howdy-partner")
def howdy_partner():
    D = Doc2("us-hp")
    out = [sky(D, [(0, "#3A4A8A"), (0.4, "#E8806A"), (0.75, "#FFC07A"), (1, "#FFE0A8")], 931, 400, ["#5A5A9A", "#FFA878"], 50)]
    out.append(soft_glow(D, 430, 360, 230, "#FFF2C0", 0.7))
    out.append(f'<circle cx="430" cy="352" r="38" fill="#FFF0C8"/>')
    out.append(hill(D, ridge([(-20, 360), (120, 330), (220, 348), (360, 336), (620, 356)], 932, 4), 600, ("#C8846A", "#9A5A4A", "#5A3030"), 932, inkw=0))
    out.append(hill(D, ridge([(-20, 384), (300, 376), (620, 388)], 933, 2), 600, ("#E8B87A", "#C8904A", "#7A5228"), 933, inkw=0))
    # windmill and a longhorn far off
    wx = 520
    out.append(f'<path d="M {wx - 14} 384 L {wx} 290 L {wx + 14} 384 M {wx - 10} 350 L {wx + 10} 346" stroke="#3A2A2A" stroke-width="2" fill="none"/>')
    for k in range(12):
        a = math.radians(k * 30)
        out.append(f'<path d="M {wx} 286 L {wx + math.cos(a) * 22:.1f} {286 + math.sin(a) * 22:.1f}" stroke="#3A2A2A" stroke-width="2.6"/>')
    out.append(f'<path d="M {wx} 286 L {wx + 34} 290 L {wx + 34} 282 Z" fill="#3A2A2A"/>')
    lx, ly = 160, 380
    out.append(f'<path d="{blob(lx, ly, 22, 10, 934, 0.1, 12)}" fill="#3A2A2A"/><path d="M {lx - 18} {ly - 4} l -12 -4 l 6 8 Z M {lx - 26} {ly - 6} q -14 -8 -22 -2 M {lx - 26} {ly - 6} q 6 -12 18 -10" stroke="#3A2A2A" stroke-width="2" fill="#3A2A2A"/>'
               f'<path d="M {lx - 14} {ly + 6} l 0 12 M {lx - 4} {ly + 6} l 0 12 M {lx + 8} {ly + 6} l 0 12 M {lx + 16} {ly + 6} l 0 12" stroke="#3A2A2A" stroke-width="2.4"/>')
    for x in (60, 250, 330, 420):
        out.append(f'<path d="M {x} 392 l 0 -26 M {x} 380 l -8 -6 M {x} 376 l 8 -8" stroke="#4A6A3A" stroke-width="4" stroke-linecap="round"/>')
    # split-rail fence across the middle ground
    for k, x in enumerate((40, 300, 560)):
        out.append(painted(D, rect_pts(x - 12, 300, x + 12, 470, 12, 935 + k, 0.4), WOOD, 935 + k, sdir=(1, 0), sk=0.2, angle=-90, n=10, inkw=1.8, hi=0.3))
        out.append(f'<path d="{smooth_closed(ell_pts(x, 300, 12, 4, 0, 360, 10)[:-1])}" fill="#C8905A" stroke="{INK}" stroke-width="1.2"/>')
    for y in (336, 396):
        out.append(painted(D, rect_pts(-10, y - 8, 610, y + 8, 30, 938 + y, 0.8), WOOD, 938 + y, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=1.6, hi=0.3))
    # horseshoe nailed to the post (open end up, for luck), a coiled lariat on the other post
    hx, hy = 300, 300 + 32
    out.append(pline([(hx + 14 * math.cos(math.radians(a)), hy - 6 + 16 * math.sin(math.radians(a))) for a in range(-10, 191, 10)], "#8A94A4", 6, 941, 1, 1))
    out.append(pline([(hx + 14 * math.cos(math.radians(a)), hy - 7 + 16 * math.sin(math.radians(a))) for a in range(-10, 191, 10)], "#D8E0EA", 1.6, 942, 0.8, 1))
    for k in range(4):
        out.append(ink(smooth_closed(ell_pts(560, 366, 34 - k * 4, 30 - k * 3.6, 0, 360, 20)[:-1]), "#E8C890" if k % 2 else "#C8A060", 4, 943 + k, 1, 1))
    out.append(pline([(560, 396), (566, 430), (556, 460)], "#C8A060", 4, 948, 1, 1))
    # the hat hung on the left post
    out.append(cowboy_hat(D, 96, 300, 176, 949))
    # porch boards and the boots
    out.append(wood_planks(D, 470, 600, 950, ("#C8946A", "#9A6A44", "#5A3A22"), 3))
    out.append(f'<rect y="466" width="600" height="8" fill="#3A2214" opacity="0.5"/>')
    out.append(cowboy_boot(D, 236, 560, 196, 951, pal=LEATHER))
    out.append(cowboy_boot(D, 358, 574, 196, 952, pal=("#E89060", "#A8502A", "#5A240E"), flip=1))
    # lettering
    out.append(letters(D, 300, 128, "Howdy, Partner", SERIF_IT, 86, "#FFF2D8", ["#FFFFFF", "#FFE2C0"], 953, max_w=460,
                       shadow="#5A2A3A", soff=(0.025, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 172, "FROM THE LONE STAR STATE", "#FFE8B0", font=JOS, size=19, ls=4, line_w=20, gap=10, max_w=380))
    return finish_a(D, out, 954)


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
