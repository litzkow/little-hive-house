"""Puerto Rico, hand-painted (gouache / storybook) edition: 30 magnets for boricuas on the island, in the States and
anyone who is boricua at heart. Puerto Rican Spanish first, with correct accents and local words.

Painted in the house gouache idiom of brasil_painted.py / mexico_painted.py: warm paper, layered washes with pooled
edges, brush strokes that follow each form, a warm brown pen line, hand-placed brush lettering, soft light and grain.
Colour story: flag red and sky blue, flamboyán vermilion, Caribbean turquoise, Old San Juan pastels and blue
adoquines, rainforest greens, plantain gold and coffee brown.

Run from tools/designs:  python3 puerto_rico_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (blooms, bbox, cast, dab_crown, grass, hill, label, letters, mix, painted, pline, ridge,
                            ruled, shift, sky, soft_glow, specks, taper, catmull, mist, cinnamon_stick)
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from poster import ANTON
from summer_gouache import (rot, rect_pts, poly_pts, frond, palm, puff_cloud, sparkle, hibiscus, banana_leaf, sea,
                            wave_lines, seagull)
import holidays_gouache as hg
from brasil_painted import (Doc2, ell_pts, pd, shade_over, light_over, cloth, leaf_simple, bird_v, heart_d, p_heart,
                            steam, wood_planks, finish_b, cup_saucer)

COL = "puerto-rico"
INK = "#3A2418"
FLECK = "#8A6A4A"
lt, dk = hg.lt, hg.dk

# (light, base, dark) gouache palettes
ROJO = ("#F4867A", "#D52B1E", "#8A1410")       # flag red
AZUL = ("#7AB4F0", "#2F6CC6", "#123A7A")       # flag blue
CELESTE = ("#C4E4FA", "#72B2E8", "#2E70B0")
FLAMB = ("#FF9466", "#E8401E", "#94180C")      # flamboyán
FLAMB2 = ("#FFB86A", "#F26A1E", "#A83A0E")
CARIBE = ("#9AF0E6", "#1FB5B2", "#0A666E")
SELVA = ("#86CC74", "#2E8A44", "#0F4A26")
HOJA = ("#B6E07A", "#5AA83E", "#245E1E")
PLATANO = ("#FFE89A", "#F2BE3A", "#B07A12")
VERDEPL = ("#CDE592", "#7DA83C", "#3A5E14")
ADOQ = ("#9AB4D2", "#4E7098", "#22385A")
WOOD = ("#D8A06A", "#A86A3A", "#5E3618")
CAOBA = ("#C0703E", "#8A3A1E", "#4A1A0A")      # mahogany
CREAM = ("#FFFDF6", "#F4EAD6", "#C8B494")
WHITE = ("#FFFFFF", "#F4F0E8", "#B8B0A6")
CHOC = ("#8A5A3A", "#5A3018", "#2A1408")
ALUM = ("#F2F4F6", "#B8BEC6", "#6A707A")       # caldero aluminium
COQ = ("#E6C08A", "#B08050", "#5E3C1E")        # coquí skin

PASTELS = [("#FFD0D8", "#F49AAE", "#B4566C"), ("#FFF0A8", "#F6D24A", "#B8901A"), ("#C8F0DC", "#7CCCA8", "#3A8A66"),
           ("#D8D0F6", "#A898DE", "#5E4E9A"), ("#FFD8B8", "#F6A66E", "#B0602A"), ("#C4E8F6", "#7EC4E2", "#3A82A2")]

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def pal_of(c, a=0.38, b=0.38):
    return (lt(c, a), c, dk(c, b))


# ================================================================ puerto rico toolkit
def disc(cx, cy, r, col, op=1.0):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}" opacity="{op:.2f}"/>'


def dashes(seed, clip, box, n, cols, L=(4, 7), w=(2.2, 3.2), ang=None, op=(0.75, 1.0), D=None):
    """Lots of short rounded marks (rice grains, sugar, crumbs), clipped to a shape."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        a = math.radians(ang + rnd.uniform(-25, 25)) if ang is not None else rnd.uniform(0, math.pi)
        l = rnd.uniform(*L)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(a) * l:.1f} {math.sin(a) * l:.1f}" stroke="{rnd.choice(cols)}" '
                   f'stroke-width="{rnd.uniform(*w):.1f}" opacity="{rnd.uniform(*op):.2f}"/>')
    body = f'<g stroke-linecap="round">{"".join(out)}</g>'
    if clip and D:
        cp = D.clip('<path d="' + clip + '"/>')
        return f'<g {cp}>{body}</g>'
    return body


def star_d(cx, cy, ro, ri=None, rot_=-90):
    ri = ri or ro * 0.382
    return pd(hg.star_pts(cx, cy, ro, ri, 5, rot_))


def firefly(D, x, y, r=12, col="#F2FF9A"):
    return D.glow(x, y, r, col, 0.55) + disc(x, y, max(1.6, r * 0.16), "#FFFFE8")


def toes(base, tips, col, w, disc_r, op=1.0):
    out = []
    for tx, ty in tips:
        out.append(taper([base, ((base[0] + tx) / 2, (base[1] + ty) / 2 - 0.5), (tx, ty)], w, w * 0.6, col, op))
        out.append(disc(tx, ty, disc_r, col, op))
    return "".join(out)


# ---------------------------------------------------------------- the coquí
def coqui(D, cx, cy, s, seed, flip=False, sing=True, skin=COQ, sac="#F6E6C8"):
    """Eleutherodactylus coqui, sitting, head to the left: big bronze eyes, sticky toe discs, singing throat sac."""
    sx = -1 if flip else 1

    def P(pts):
        return [(cx + sx * x * s, cy + y * s) for x, y in pts]

    def Q(x, y):
        return (cx + sx * x * s, cy + y * s)

    rnd = random.Random(seed)
    out = [cast(D, cx + sx * 4 * s, cy + 36 * s, 52 * s, 7 * s, "#06140C", 0.45, seed)]
    far = skin[2], mix(skin[2], skin[1], 0.4)
    # far front arm and far hind foot (behind the body)
    out.append(painted(D, P([(-40, 6), (-34, 8), (-40, 24), (-44, 33), (-49, 32), (-46, 22)]), (skin[1], far[1], skin[2]), seed + 1,
                       sk=0.15, n=4, inkw=1.0, hi=0.2))
    out.append(toes(Q(-46, 32), [Q(-56, 33), Q(-53, 37), Q(-46, 38)], far[0], 2.2 * s, 2.2 * s))
    # body
    body = P([(-56, -5), (-53, -14), (-45, -21), (-34, -27), (-22, -28), (-8, -26), (8, -23), (24, -17), (38, -8), (46, 3), (44, 14),
              (32, 20), (12, 22), (-8, 20), (-24, 16), (-38, 10), (-50, 3)])
    out.append(painted(D, body, skin, seed + 2, sdir=(0.3, 1), sk=0.14, angle=-20, n=40, slen=(6 * s, 16 * s), sw=(0.8, 2.2),
                       inkw=1.6, inkop=0.7, hi=0.4, hik=0.08))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    inner = [f'<path d="{smooth_closed(P([(-48, 2), (-30, 8), (0, 16), (30, 16), (40, 10), (36, 24), (-10, 24), (-44, 12)]))}" fill="#F4DCB0" opacity="0.75"/>']
    # dark W-band across the shoulders, mottles, the pale dorsolateral line
    inner.append(f'<path d="{smooth_closed(P([(-24, -28), (-14, -18), (-6, -24), (2, -16), (10, -24), (14, -20), (4, -10), (-6, -16), (-14, -8), (-26, -20)]))}" fill="{skin[2]}" opacity="0.55"/>')
    for _ in range(18):
        x, y = rnd.uniform(-20, 40), rnd.uniform(-22, 8)
        inner.append(f'<path d="{blob(*Q(x, y), rnd.uniform(2, 4.5) * s, rnd.uniform(1.5, 3) * s, rnd.randint(0, 999), 0.2, 8)}" fill="{skin[2]}" opacity="{rnd.uniform(0.25, 0.5):.2f}"/>')
    inner.append(taper(P([(-26, -21), (-6, -19), (16, -13), (36, -3)]), 3 * s, 1, "#F6E0B8", 0.7))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # hind leg: thigh folded against the body, shin forward, long toes
    thigh = P([(14, -4), (30, -10), (44, -4), (50, 8), (46, 18), (30, 21), (16, 14)])
    out.append(painted(D, thigh, skin, seed + 3, sdir=(0.4, 1), sk=0.18, angle=-30, n=14, inkw=1.4, inkop=0.6, hi=0.45))
    for k in range(3):
        out.append(taper(P([(22 + k * 8, -6 + k * 2), (28 + k * 8, 6 + k), (24 + k * 8, 16)]), 2.6 * s, 0.8, skin[2], 0.45))
    shin = P([(48, 10), (53, 19), (45, 27), (24, 31), (6, 33), (3, 27), (22, 23), (40, 17)])
    out.append(painted(D, shin, skin, seed + 4, sdir=(0.2, 1), sk=0.2, angle=0, n=10, inkw=1.4, inkop=0.6, hi=0.4))
    out.append(toes(Q(5, 31), [Q(-20, 30), Q(-18, 35.5), Q(-12, 39), Q(-3, 40), Q(5, 39)], skin[1], 2.8 * s, 2.5 * s))
    out.append(toes(Q(5, 31), [Q(-20, 30), Q(-18, 35.5), Q(-12, 39), Q(-3, 40)], lt(skin[0], 0.3), 0.9 * s, 0.9 * s, 0.6))
    # singing throat sac
    if sing:
        sd = blob(*Q(-39, 15), 16 * s, 13.5 * s, seed + 5, 0.03, 16)
        out.append(f'<path d="{sd}" fill="{sac}" opacity="0.88"/>')
        g = D.rad([(0, "#FFFFFF", 0.0), (0.6, "#FFFFFF", 0.0), (1, "#C8A070", 0.55)])
        out.append(f'<path d="{sd}" fill="{g}"/>')
        out.append(f'<path d="{blob(*Q(-44, 9), 5 * s, 2.6 * s, seed + 6, 0.1, 8, -30)}" fill="#FFFFFF" opacity="0.85"/>')
        out.append(ink(sd, "#8A6A44", 1.2, seed + 7, 1, 0.55))
    # near front arm with splayed fingers and discs
    arm = P([(-25, 8), (-16, 11), (-18, 22), (-22, 33), (-28, 34), (-27, 22)])
    out.append(painted(D, arm, skin, seed + 8, sdir=(0.6, 0.8), sk=0.2, n=6, inkw=1.3, inkop=0.6, hi=0.45))
    out.append(toes(Q(-25, 33), [Q(-37, 35), Q(-33, 39.5), Q(-25, 40.5), Q(-17, 38.5)], skin[1], 2.6 * s, 2.4 * s))
    # eye: lid bump, bronze iris, horizontal pupil
    out.append(painted(D, blob_pts(*Q(-30, -24), 11 * s, 10 * s, seed + 9, 0.04, 12), skin, seed + 9, sk=0.12, n=4, inkw=1.2, hi=0.5))
    ir = blob(*Q(-30, -25), 8 * s, 7.6 * s, seed + 10, 0.02, 14)
    out.append(f'<path d="{ir}" fill="#C88A2A"/>')
    out.append(f'<path d="{ir}" fill="{D.rad([(0, "#FFE08A"), (0.6, "#D89A30"), (1, "#6A3A10")], cx=0.4, cy=0.35)}"/>')
    out.append(f'<ellipse cx="{Q(-30, -25)[0]:.1f}" cy="{Q(-30, -25)[1]:.1f}" rx="{5.2 * s:.1f}" ry="{2.6 * s:.1f}" fill="#120804"/>')
    out.append(disc(*Q(-32.5, -28), 1.8 * s, "#FFFFFF", 0.95))
    out.append(disc(*Q(-27, -22), 0.9 * s, "#FFFFFF", 0.6))
    out.append(ink(ir, "#2A1406", 1.3, seed + 11, 1, 0.8))
    # mouth line, nostril
    out.append(pline(P([(-55, -4), (-46, -2), (-36, -5), (-30, -12)]), skin[2], 1.4, seed + 12, 0.75, 1))
    out.append(disc(*Q(-51, -11), 1.1 * s, skin[2], 0.9))
    return "".join(out)


def tree_fern(D, x, base, h, seed, cols, trunk="#0E2A26", op=1.0):
    """Puerto Rican tree fern (helecho gigante) silhouette: a slim trunk and an umbrella of arching fronds."""
    rnd = random.Random(seed)
    top = (x + rnd.uniform(-10, 10), base - h)
    out = [f'<g opacity="{op}">', taper([(x, base), ((x + top[0]) / 2 + 4, base - h / 2), top], 9, 5, trunk)]
    for k in range(11):
        ang = -180 + k * 18 + rnd.uniform(-6, 6)
        L = h * rnd.uniform(0.32, 0.45)
        out.append(frond(top[0], top[1], ang, L, seed * 5 + k, cols, droop=0.55, blade=0.16, n=18, sw=1.4))
    out.append("</g>")
    return "".join(out)


# ---------------------------------------------------------------- simple 3d projection (chairs, carts, tables)
class Cam3:
    """Orthographic-ish view: yaw around the vertical axis, a little pitch, scale and screen origin."""

    def __init__(self, ox, oy, s, yaw=-30, pitch=14):
        self.ox, self.oy, self.s = ox, oy, s
        self.cy, self.sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        self.cp, self.sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def __call__(self, x, y, z):
        xr = x * self.cy + z * self.sy
        zr = -x * self.sy + z * self.cy
        return (self.ox + self.s * xr, self.oy - self.s * (y * self.cp + zr * self.sp))

    def depth(self, x, y, z):
        return -x * self.sy + z * self.cy

    def pts(self, ps):
        return [self(*p) for p in ps]


def rod(C, a, b, w0, w1, pal, seed, inkw=1.2):
    """A turned wooden rod between two 3d points: tapered fill, a lit stripe, a shade stripe."""
    pa, pb = C(*a), C(*b)
    out = [taper([pa, ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2), pb], w0, w1, pal[1])]
    dx, dy = pb[0] - pa[0], pb[1] - pa[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    o = w0 * 0.22
    out.append(taper([(pa[0] - nx * o, pa[1] - ny * o), (pb[0] - nx * o, pb[1] - ny * o)], w0 * 0.3, w1 * 0.3, pal[0], 0.75))
    out.append(taper([(pa[0] + nx * o * 1.3, pa[1] + ny * o * 1.3), (pb[0] + nx * o * 1.3, pb[1] + ny * o * 1.3)], w0 * 0.3, w1 * 0.3, pal[2], 0.6))
    if inkw:
        L1 = [(pa[0] + nx * w0 / 2, pa[1] + ny * w0 / 2), (pb[0] + nx * w1 / 2, pb[1] + ny * w1 / 2)]
        L2 = [(pa[0] - nx * w0 / 2, pa[1] - ny * w0 / 2), (pb[0] - nx * w1 / 2, pb[1] - ny * w1 / 2)]
        out.append(pline(L1, INK, inkw, seed, 0.6, 1) + pline(L2, INK, inkw, seed + 1, 0.6, 1))
    return "".join(out)


def cane(D, pts, seed, base="#E8C88A", line="#A8783A", hole="#5A3A1A", step=7.0):
    """Woven cane (pajilla) panel: honey ground, two diagonal weaves, an orthogonal weave and octagon holes."""
    d = smooth_closed(pts) if len(pts) > 4 else pd(pts)
    x0, y0, x1, y1 = bbox(pts)
    out = [f'<path d="{d}" fill="{base}"/>']
    cid = D.clip(f'<path d="{d}"/>')
    g = []
    span = int((x1 - x0 + y1 - y0) / step) + 4
    for i in range(-span, span):
        c = x0 + i * step
        g.append(f'<path d="M {c:.1f} {y0 - 5:.1f} l {y1 - y0 + 10:.1f} {y1 - y0 + 10:.1f}" stroke="{line}" stroke-width="1.3" opacity="0.7"/>')
        g.append(f'<path d="M {c:.1f} {y1 + 5:.1f} l {y1 - y0 + 10:.1f} {-(y1 - y0 + 10):.1f}" stroke="{line}" stroke-width="1.3" opacity="0.7"/>')
    for i in range(int((x1 - x0) / step) + 2):
        g.append(f'<path d="M {x0 + i * step + step / 2:.1f} {y0:.1f} L {x0 + i * step + step / 2:.1f} {y1:.1f}" stroke="#F6E2B0" stroke-width="1" opacity="0.55"/>')
    for i in range(int((x1 - x0) / step) + 2):
        for j in range(int((y1 - y0) / step) + 2):
            g.append(f'<circle cx="{x0 + i * step:.1f}" cy="{y0 + j * step:.1f}" r="{step * 0.2:.1f}" fill="{hole}" opacity="0.55"/>')
    g.append(shade_over(D, d, "#3A1A06", 0.35, 0, 0, 1, 1, 0.4))
    out.append(f'<g {cid}>{"".join(g)}</g>')
    return "".join(out)


def tile_floor(D, y0, y1, seed, a="#C8382E", b="#1E5A8A", ground="#F4E8D4", cell=58, squash=0.42, op=1.0):
    """Cement mosaic floor (losas criollas) seen in perspective: a tiled pattern squashed vertically."""
    c = cell
    tile = (f'<rect width="{c}" height="{c}" fill="{ground}"/>'
            f'<path d="M 0 0 L {c * 0.32} 0 A {c * 0.32} {c * 0.32} 0 0 1 0 {c * 0.32} Z M {c} 0 L {c} {c * 0.32} A {c * 0.32} {c * 0.32} 0 0 1 {c * 0.68} 0 Z '
            f'M {c} {c} L {c * 0.68} {c} A {c * 0.32} {c * 0.32} 0 0 1 {c} {c * 0.68} Z M 0 {c} L 0 {c * 0.68} A {c * 0.32} {c * 0.32} 0 0 1 {c * 0.32} {c} Z" fill="{a}"/>'
            f'<path d="M {c / 2} {c * 0.2} L {c * 0.8} {c / 2} L {c / 2} {c * 0.8} L {c * 0.2} {c / 2} Z" fill="{b}"/>'
            f'<circle cx="{c / 2}" cy="{c / 2}" r="{c * 0.1}" fill="{ground}"/>'
            f'<path d="M 0 0 L {c} 0 L {c} {c} L 0 {c} Z" fill="none" stroke="#8A7A6A" stroke-width="1.2" opacity="0.6"/>')
    pat = D.pattern(c, c, tile, transform=f"translate(300 {y0}) scale(1 {squash}) rotate(45)")
    out = [f'<rect y="{y0}" width="600" height="{y1 - y0}" fill="{pat}" opacity="{op}"/>']
    g = D.lin([(0, "#2A1A10", 0.35), (0.5, "#2A1A10", 0.08), (1, "#2A1A10", 0.0)])
    out.append(f'<rect y="{y0}" width="600" height="{y1 - y0}" fill="{g}"/>')
    out.append(strokes(D.nid(), f"M 0 {y0} L 600 {y0} L 600 {y1} L 0 {y1} Z", (-40, y0, 600, y1), ["#FFFFFF", "#8A6A4A"], seed, n=60,
                       angle=0, length=(40, 120), width=(1, 3), opacity=(0.06, 0.16)))
    return "".join(out)


# ================================================================ 1. coquí — singing on a leaf, a rainforest night
@design("coqui")
def coqui_d():
    D = Doc2("prcq")
    out = [sky(D, [(0, "#0A1E2C"), (0.5, "#0F3436"), (1, "#173F2E")], 101, 600, ["#16404A", "#0A1A22", "#1E4A40"], 90, sop=(0.06, 0.16))]
    rnd = random.Random(102)
    for _ in range(36):
        out.append(disc(rnd.uniform(40, 560), rnd.uniform(30, 250), rnd.uniform(0.6, 1.5), "#E8F4E0", rnd.uniform(0.3, 0.8)))
    out.append(soft_glow(D, 452, 262, 190, "#D8F0C8", 0.32))
    out.append(painted(D, blob_pts(452, 262, 30, 30, 103, 0.02, 20), ("#FFFFF0", "#F4F0D0", "#C8C8A0"), 103, sk=0.1, n=10, inkw=0, hi=0.3))
    out.append(f'<path d="{blob(444, 256, 9, 6, 104, 0.2, 8)}" fill="#D8D4B0" opacity="0.6"/><path d="{blob(462, 272, 6, 4, 105, 0.2, 8)}" fill="#D8D4B0" opacity="0.5"/>')
    # layers of tree ferns and mist
    out.append(tree_fern(D, 92, 470, 330, 106, ["#123A36", "#0E302C", "#184640"], op=0.9))
    out.append(tree_fern(D, 586, 470, 300, 107, ["#123A36", "#0E302C", "#184640"], op=0.85))
    out.append(f'<rect y="300" width="600" height="120" fill="{D.lin([(0, "#B8E0D0", 0), (0.5, "#B8E0D0", 0.12), (1, "#B8E0D0", 0)])}"/>')
    out.append(tree_fern(D, 210, 520, 230, 109, ["#1A4A40", "#143E36", "#22564A"], op=0.95))
    out.append(tree_fern(D, 430, 520, 200, 110, ["#1A4A40", "#143E36", "#22564A"], op=0.95))
    out.append(f'<rect y="410" width="600" height="90" fill="{D.lin([(0, "#A8D8C4", 0), (0.5, "#A8D8C4", 0.1), (1, "#A8D8C4", 0)])}"/>')
    # framing leaf from the right, darker, behind
    out.append(banana_leaf(D, 640, 560, -160, 240, 52, 112, pal=("#3E7A4A", "#1E5230", "#0C2E1A")))
    # the big glossy leaf the coquí sits on
    out.append(banana_leaf(D, 0, 630, -22, 640, 104, 113, pal=("#7ECB6A", "#2E8A44", "#0F4A26")))
    out.append(taper([(150, 566), (300, 508), (440, 452), (520, 420)], 2, 4, "#E8FFD8", 0.3))
    # rain drops on the leaf
    for k, (x, y, r) in enumerate(((120, 576, 7), (176, 556, 5), (476, 470, 6), (536, 430, 4.5), (430, 520, 4))):
        out.append(f'<path d="{blob(x, y, r, r * 0.8, 120 + k, 0.08, 10)}" fill="#BFF0D0" opacity="0.55"/>')
        out.append(ink(blob(x, y, r, r * 0.8, 120 + k, 0.08, 10), "#0C3A1E", 1, 120 + k, 1, 0.5))
        out.append(disc(x - r * 0.35, y - r * 0.3, r * 0.3, "#FFFFFF", 0.9))
    # the coquí, singing
    out.append(soft_glow(D, 320, 420, 150, "#D8F0C8", 0.2))
    out.append(coqui(D, 330, 422, 2.25, 130))
    # its song: little arcs from the throat and the two notes
    for k, r in enumerate((30, 46, 62)):
        a0, a1 = math.radians(160), math.radians(220)
        cx, cy = 222, 450
        out.append(pline([(cx + r * math.cos(a0 + (a1 - a0) * t / 6), cy + r * math.sin(a0 + (a1 - a0) * t / 6)) for t in range(7)], "#F2F6C8", 2.6, 131 + k, 0.75 - k * 0.15, 1))
    out.append(f'<text x="132" y="392" text-anchor="middle" {JOS} font-size="28" fill="#F4F6CE" transform="rotate(-14 132 392)">co-QUÍ!</text>')
    out.append(f'<text x="108" y="334" text-anchor="middle" {JOS} font-size="19" fill="#F4F6CE" opacity="0.7" transform="rotate(-18 108 334)">co-quí</text>')
    for x, y, r in ((530, 312, 13), (400, 290, 10), (80, 470, 11), (556, 520, 9), (240, 280, 9), (160, 250, 8)):
        out.append(firefly(D, x, y, r))
    # lettering
    out.append(letters(D, 300, 156, "coquí", SERIF_IT, 140, "#F2F6D6", ["#FFFFFF", "#D8EAB8", "#F6F2C4"], 140, max_w=380,
                       shadow="#04120C", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 200, "EL CANTO DE MI ISLA", "#CFE8B0", font=JOS, size=19, ls=6, line_w=34, gap=14))
    return finish_b(D, out, 141, "#FFFFFF", 0.45)


# ================================================================ 2. mofongo — majado en el pilón
def pilon(D, cx, rim_y, rim_rx, base_y, seed, pal=("#C88A52", "#8A5228", "#46240E")):
    """Wooden pilón (mortar): wide bowl on a turned waist and a flared foot, grain following the form."""
    rr = rim_rx
    waist_y = rim_y + (base_y - rim_y) * 0.62
    body = [(cx - rr, rim_y), (cx - rr * 0.97, rim_y + 30), (cx - rr * 0.84, rim_y + 66), (cx - rr * 0.6, waist_y - 26), (cx - rr * 0.36, waist_y),
            (cx - rr * 0.33, waist_y + 18), (cx - rr * 0.52, base_y - 22), (cx - rr * 0.78, base_y - 6), (cx - rr * 0.8, base_y + 4), (cx, base_y + 12),
            (cx + rr * 0.8, base_y + 4), (cx + rr * 0.78, base_y - 6), (cx + rr * 0.52, base_y - 22), (cx + rr * 0.33, waist_y + 18), (cx + rr * 0.36, waist_y),
            (cx + rr * 0.6, waist_y - 26), (cx + rr * 0.84, rim_y + 66), (cx + rr * 0.97, rim_y + 30), (cx + rr, rim_y)]
    out = [cast(D, cx + 30, base_y + 8, rr * 1.05, 18, strength=0.5, seed=seed)]
    out.append(painted(D, body, pal, seed, sdir=(1, 0.2), sk=0.16, angle=-90, n=90, slen=(14, 46), sw=(1, 3),
                       cols=[pal[0], pal[2], "#E0A870", "#5A2E12"], inkw=2.2, hi=0.45, hik=0.06))
    d = smooth_closed(body)
    cid = D.clip(f'<path d="{d}"/>')
    rnd = random.Random(seed)
    g = []
    # grain lines curving with the bowl, and two carved bands
    for k in range(-7, 8):
        t = k / 7
        g.append(pline([(cx + t * rr * 0.98, rim_y + 4), (cx + t * rr * 0.86, rim_y + 60), (cx + t * rr * 0.4, waist_y)], dk(pal[2], 0.1), 1.2, seed + k, 0.35, 1))
    for yy, w in ((rim_y + 22, rr * 0.99), (rim_y + 30, rr * 0.98), (base_y - 14, rr * 0.66)):
        g.append(pline([(cx - w, yy - 4), (cx, yy + 10), (cx + w, yy - 4)], "#2E1406", 2.2, seed + int(yy), 0.6, 1))
        g.append(pline([(cx - w, yy - 2), (cx, yy + 12), (cx + w, yy - 2)], "#E8B07A", 1.2, seed + int(yy) + 1, 0.4, 1))
    for _ in range(3):
        kx, ky = cx + rnd.uniform(-rr * 0.6, rr * 0.6), rim_y + rnd.uniform(40, 80)
        g.append(f'<ellipse cx="{kx:.1f}" cy="{ky:.1f}" rx="7" ry="3.5" fill="none" stroke="{pal[2]}" stroke-width="1.4" opacity="0.6"/>')
    g.append(shade_over(D, d, "#1A0802", 0.5, 0, 0, 1, 0, 0.45))
    out.append(f'<g {cid}>{"".join(g)}</g>')
    # rim lip
    rim = ell_pts(cx, rim_y, rr, rr * 0.2, 0, 360, 32)
    out.append(f'<path d="{smooth_closed(rim)}" fill="{pal[0]}"/>')
    out.append(f'<path d="{blob(cx, rim_y + 1, rr - 9, rr * 0.2 - 7, seed + 3, 0.01, 30)}" fill="#3A1A08"/>')
    out.append(ink(smooth_closed(rim), INK, 1.8, seed + 4, 1, 0.7))
    return "".join(out)


def chicharron(D, x, y, s, seed, ang=0):
    """Crispy pork crackling chunk: a puffed, blistered golden slab with a pale fat layer along one side."""
    rnd = random.Random(seed)
    pts = rot(blob_pts(x, y, s, s * 0.62, seed, 0.28, 9), x, y, ang)
    out = [cast(D, x + 2, y + s * 0.5, s * 0.9, s * 0.25, "#5A2A06", 0.3, seed)]
    fat = rot([(x - s * 0.7, y + s * 0.32), (x - s * 0.2, y + s * 0.56), (x + s * 0.4, y + s * 0.55), (x + s * 0.75, y + s * 0.3), (x + s * 0.3, y + s * 0.42), (x - s * 0.3, y + s * 0.44)], x, y, ang)
    out.append(painted(D, pts, ("#F8C46A", "#D0822E", "#7A3A0C"), seed, sdir=(0.5, 0.9), sk=0.25, angle=ang, n=6, inkw=1.2, inkop=0.7, hi=0.55, hik=0.12))
    out.append(f'<path d="{smooth_closed(fat)}" fill="#F8DCA8" opacity="0.8"/>')
    for _ in range(7):
        bx, by = x + rnd.uniform(-s * 0.6, s * 0.6), y + rnd.uniform(-s * 0.45, s * 0.05)
        out.append(disc(bx, by, s * rnd.uniform(0.07, 0.12), "#FFE6B0", 0.85) + disc(bx + s * 0.05, by + s * 0.06, s * 0.05, "#8A4410", 0.55))
    return "".join(out)


def garlic(D, cx, cy, r, seed):
    """Garlic head: plump papery bulb tapering to a neck, clove seams, faint purple streaks and a root tuft."""
    pts = [(cx, cy - 1.15 * r), (cx + 0.2 * r, cy - 0.85 * r), (cx + 0.7 * r, cy - 0.35 * r), (cx + 0.92 * r, cy + 0.2 * r), (cx + 0.66 * r, cy + 0.7 * r),
           (cx, cy + 0.84 * r), (cx - 0.66 * r, cy + 0.7 * r), (cx - 0.92 * r, cy + 0.2 * r), (cx - 0.7 * r, cy - 0.35 * r), (cx - 0.2 * r, cy - 0.85 * r)]
    out = [cast(D, cx + 4, cy + r * 0.85, r * 1.0, r * 0.22, strength=0.4, seed=seed)]
    out.append(painted(D, pts, ("#FFFFFF", "#F2EADC", "#B8A894"), seed, sdir=(0.8, 0.5), sk=0.18, angle=-90, n=16, inkw=1.5, inkop=0.7, hi=0.6))
    for k, dx in enumerate((-0.55, -0.22, 0.12, 0.45)):
        out.append(pline([(cx + dx * 0.25 * r, cy - 0.95 * r), (cx + dx * 1.25 * r, cy + 0.05 * r), (cx + dx * 0.9 * r, cy + 0.78 * r)], "#C8B8A0", 1.3, seed + k, 0.75, 1))
        out.append(taper([(cx + dx * 0.4 * r + 3, cy - 0.6 * r), (cx + dx * 1.1 * r + 3, cy + 0.1 * r)], 2.4, 1, "#B890B0", 0.45))
    out.append(taper([(cx, cy - 1.1 * r), (cx + 2, cy - 1.35 * r), (cx - 2, cy - 1.55 * r)], 5, 3, "#D8C8A0"))
    for k in range(6):
        out.append(pline([(cx - 8 + k * 3, cy + 0.82 * r), (cx - 10 + k * 4, cy + 0.82 * r + 6)], "#A8946A", 1.1, seed + 20 + k, 0.8, 1))
    return "".join(out)


def garlic(D, cx, cy, r, seed):
    """Garlic head: papery white cloves bulging, purple-streaked, with a dry stalk."""
    out = [cast(D, cx + 4, cy + r * 0.85, r * 1.05, r * 0.24, strength=0.4, seed=seed)]
    for k, dx in enumerate((-0.5, 0.5, -0.2, 0.22, 0)):
        pts = blob_pts(cx + dx * r, cy + 0.05 * r, r * 0.42, r * 0.78, seed + k, 0.05, 14)
        pts = [(x, y) for x, y in pts]
        out.append(painted(D, pts, ("#FFFFFF", "#F2EADC", "#B8A894"), seed + k, sdir=(0.7, 0.6), sk=0.2, angle=-90, n=8, inkw=1.2, inkop=0.6, hi=0.5))
    for dx in (-0.35, -0.08, 0.18, 0.4):
        out.append(pline([(cx + dx * r, cy - 0.55 * r), (cx + dx * r * 1.15, cy), (cx + dx * r * 0.9, cy + 0.7 * r)], "#A88AA8", 1.2, seed + int(dx * 10), 0.6, 1))
    out.append(taper([(cx, cy - 0.7 * r), (cx + 2, cy - 1.05 * r), (cx - 3, cy - 1.3 * r)], 6, 3, "#C8B48A"))
    out.append(taper([(cx - 0.4 * r, cy + 0.82 * r), (cx, cy + 0.9 * r), (cx + 0.4 * r, cy + 0.82 * r)], 3, 3, "#B8A07A", 0.8))
    return "".join(out)


def plantain(D, a, b, w, seed, pal=VERDEPL, bend=0.18, tips="#3A2A14"):
    """A plantain from a (stem end) to b (tip): curved, ridged, a dark stem and a blackened tip."""
    (x0, y0), (x1, y1) = a, b
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    top, bot, mid = [], [], []
    for i in range(17):
        t = i / 16
        bb = -bend * L * 4 * t * (1 - t)
        px, py = x0 + ux * L * t + nx * bb, y0 + uy * L * t + ny * bb
        ww = w * (0.32 + 0.68 * math.sin(math.pi * (0.08 + 0.84 * t)) ** 0.6)
        top.append((px + nx * ww / 2, py + ny * ww / 2))
        bot.append((px - nx * ww / 2, py - ny * ww / 2))
        mid.append((px, py))
    out = [cast(D, (x0 + x1) / 2 + 6, (y0 + y1) / 2 + w * 0.6, L * 0.5, w * 0.3, strength=0.35, seed=seed)]
    out.append(painted(D, top + bot[::-1], pal, seed, sdir=(nx, ny), sk=0.2, angle=math.degrees(math.atan2(uy, ux)), n=20, inkw=1.6, hi=0.4))
    out.append(pline([(x + nx * w * 0.12, y + ny * w * 0.12) for x, y in mid[2:-2]], pal[2], 1.4, seed + 1, 0.5, 1))
    out.append(taper([mid[0], (x0 - ux * 14, y0 - uy * 14)], w * 0.32, w * 0.24, "#5A4A22"))
    out.append(disc(mid[-1][0], mid[-1][1], w * 0.14, tips))
    return "".join(out)


@design("mofongo")
def mofongo():
    D = Doc2("prmf")
    out = [paper(D.nid(), "#F6E4BA", FLECK, 201)]
    out.append(blooms(202, ["#F2C878", "#E8B060", "#FFF0C8"], 6, (0, 0, 600, 380), (110, 200), (0.1, 0.18)))
    out.append(soft_glow(D, 150, 120, 320, "#FFF6D8", 0.55))
    # turquoise wainscot and the wooden counter
    out.append(f'<path d="{hg.org_rect(-10, 364, 620, 70, 203, 0.6, 30, 1)}" fill="#2E9A94"/>')
    out.append(strokes(D.nid(), "M -10 364 L 610 364 L 610 434 L -10 434 Z", (-40, 364, 610, 434), ["#5AC0B8", "#1E7A74", "#7AD0C8"], 204, n=50,
                       angle=0, length=(40, 120), width=(2, 5), opacity=(0.15, 0.35)))
    for k in range(19):
        out.append(pline([(k * 34 + 8, 366), (k * 34 + 9, 432)], "#E8F4EE", 1.4, 205 + k, 0.45, 1))
    out.append(pline([(-10, 399), (610, 400)], "#E8F4EE", 1.4, 229, 0.45, 1))
    out.append(f'<path d="{hg.org_rect(-10, 356, 620, 10, 205, 0.4, 30, 1)}" fill="#1E6A66"/>')
    out.append(wood_planks(D, 434, 600, 206, ("#D8A26A", "#A8703E", "#5E361A"), 3))
    out.append(f'<rect y="430" width="600" height="8" fill="#4A2A12" opacity="0.5"/>')
    # a green plantain and a garlic head on the left, broth on the right
    out.append(plantain(D, (46, 466), (204, 436), 34, 207))
    out.append(garlic(D, 100, 518, 34, 208))
    for k, (x, y, a) in enumerate(((152, 560, 70), (176, 542, -30))):
        clove = rot([(x - 12, y + 4), (x - 4, y - 6), (x + 8, y - 8), (x + 13, y - 2), (x + 6, y + 6), (x - 4, y + 7)], x, y, a)
        out.append(painted(D, clove, ("#FFFFFF", "#F4ECDE", "#B8A894"), 210 + k, sdir=(0.5, 1), sk=0.2, n=3, inkw=1.1, hi=0.5))
    # little bowl of caldo
    bx, by = 508, 466
    out.append(cast(D, bx + 6, by + 34, 66, 10, strength=0.4, seed=212))
    bowl = [(bx - 62, by), (bx - 56, by + 22), (bx - 30, by + 38), (bx + 30, by + 38), (bx + 56, by + 22), (bx + 62, by)]
    out.append(painted(D, bowl, ("#FFFFFF", "#F2EEE4", "#B8B0A0"), 213, sdir=(0.8, 0.5), sk=0.16, angle=-90, n=12, inkw=1.6, hi=0.5))
    out.append(pline([(bx - 58, by + 10), (bx, by + 16), (bx + 58, by + 10)], "#2E9A94", 3, 214, 0.9, 1))
    out.append(f'<path d="{smooth_closed(ell_pts(bx, by, 62, 12, 0, 360, 24))}" fill="#F2EEE4"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(bx, by + 1, 56, 9, 0, 360, 24))}" fill="#D8963A"/>')
    out.append(f'<path d="{blob(bx - 14, by, 18, 3, 215, 0.1, 8)}" fill="#F6C878" opacity="0.8"/>')
    for k, (x, y) in enumerate(((bx + 18, by - 1), (bx - 30, by + 2))):
        out.append(f'<path d="M {x - 8} {y} q 8 -8 16 0" stroke="#F28A6A" stroke-width="5" fill="none" stroke-linecap="round"/>')
    out.append(ink(smooth_closed(ell_pts(bx, by, 62, 12, 0, 360, 24)), INK, 1.4, 216, 1, 0.7))
    out.append(steam(bx, by - 8, 40, 217, "#FFFFFF", 2, 22, 6, 0.6))
    # the pilón and the mofongo mounded in it
    cx, rim_y = 300, 324
    out.append(pilon(D, cx, rim_y, 132, 528, 220))
    mound = [(cx - 128, rim_y + 4), (cx - 122, rim_y - 26), (cx - 100, rim_y - 62), (cx - 62, rim_y - 92), (cx - 18, rim_y - 104), (cx + 26, rim_y - 102),
             (cx + 70, rim_y - 86), (cx + 104, rim_y - 56), (cx + 124, rim_y - 22), (cx + 128, rim_y + 4), (cx + 60, rim_y + 22), (cx - 60, rim_y + 22)]
    md = smooth_closed(mound)
    out.append(painted(D, mound, ("#F6D27E", "#D9A246", "#8A5A1A"), 221, sdir=(0.7, 0.6), sk=0.14, angle=-40, n=90, slen=(10, 30), sw=(2, 5),
                       cols=["#FFE6A0", "#B8782A", "#E8B85A", "#A0641E"], inkw=2, hi=0.4))
    cid = D.clip(f'<path d="{md}"/>')
    rnd = random.Random(222)
    lumps = []
    for _ in range(70):
        x, y = rnd.uniform(cx - 120, cx + 120), rnd.uniform(rim_y - 100, rim_y + 10)
        lit = -(x - cx) / 130 - (y - rim_y + 60) / 90
        col = rnd.choice(["#FFE6A0", "#F6D07A"]) if lit > 0.2 else rnd.choice(["#C8862E", "#B07020", "#D89A42"])
        lumps.append(f'<path d="{blob(x, y, rnd.uniform(6, 13), rnd.uniform(4, 9), rnd.randint(0, 999), 0.25, 8, rnd.uniform(0, 180))}" fill="{col}" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>')
    for _ in range(40):
        x, y = rnd.uniform(cx - 115, cx + 115), rnd.uniform(rim_y - 96, rim_y + 10)
        lumps.append(f'<path d="M {x:.1f} {y:.1f} q 3 -4 6 0" stroke="#7A4410" stroke-width="1.6" fill="none" opacity="0.55"/>')
    lumps.append(specks(223, (cx - 120, rim_y - 100, cx + 120, rim_y + 10), ["#FFF6DC", "#FFFFFF"], 50, (1.2, 2.4), (0.6, 0.95)))
    lumps.append(specks(224, (cx - 120, rim_y - 100, cx + 120, rim_y + 10), ["#3E7A2A", "#5A9A3A"], 30, (1, 2), (0.6, 0.9)))
    lumps.append(f'<path d="{blob(cx - 52, rim_y - 70, 26, 10, 225, 0.2, 10, -30)}" fill="#FFF8DC" opacity="0.5"/>')
    out.append(f'<g {cid}>{"".join(lumps)}</g>')
    for k, (x, y, s, a) in enumerate(((cx - 72, rim_y - 50, 17, -20), (cx + 40, rim_y - 74, 15, 25), (cx + 88, rim_y - 22, 16, 10),
                                      (cx - 18, rim_y - 22, 16, -35), (cx - 104, rim_y - 6, 13, 15), (cx - 24, rim_y - 84, 12, 8))):
        out.append(chicharron(D, x, y, s, 230 + k, a))
    # a sprig of cilantro on top
    for k, (dx, a) in enumerate(((-6, -120), (4, -70), (0, -95))):
        out.append(leaf_simple(D, cx + dx, rim_y - 98, 20, 7, a, HOJA, 240 + k, vein=False, inkw=1))
    # the wooden pestle lying in front
    # the wooden maceta (pestle) lying in front: slim handle, swelling into a round club head
    ax0, ay0, ax1, ay1 = 380, 574, 566, 522
    L = math.hypot(ax1 - ax0, ay1 - ay0)
    ux, uy = (ax1 - ax0) / L, (ay1 - ay0) / L
    nx, ny = -uy, ux
    prof = [(0, 7), (0.1, 8), (0.45, 9), (0.55, 12), (0.7, 18), (0.86, 20), (0.95, 17), (1, 8)]
    up = [(ax0 + ux * L * t + nx * w, ay0 + uy * L * t + ny * w) for t, w in prof]
    dn = [(ax0 + ux * L * t - nx * w, ay0 + uy * L * t - ny * w) for t, w in prof]
    out.append(cast(D, 486, 566, 100, 12, strength=0.45, seed=245))
    out.append(painted(D, up + dn[::-1], ("#E0A86E", "#A06A36", "#4E2810"), 246, sdir=(0.3, 1), sk=0.22, angle=-16, n=26, inkw=1.8, hi=0.5))
    for t in (0.12, 0.5):
        a = (ax0 + ux * L * t + nx * 8.5, ay0 + uy * L * t + ny * 8.5)
        b = (ax0 + ux * L * t - nx * 8.5, ay0 + uy * L * t - ny * 8.5)
        out.append(pline([a, b], "#3A1A08", 1.6, 247 + int(t * 10), 0.55, 1))
    # lettering
    out.append(letters(D, 300, 150, "mofongo", SERIF_IT, 128, "#B8361E", ["#D8583A", "#8A2410", "#E8784A"], 250, max_w=440,
                       shadow="#5A1A0A", soff=(0.02, 0.035), angle=-40, hi="#FFD8B8"))
    out.append(ruled(300, 194, "MAJADO EN EL PILÓN", "#1E6A66", font=JOS, size=20, ls=6, line_w=34, gap=14))
    return finish_b(D, out, 251)


# ================================================================ 3. bendición — abuela's rocking chair on the balcony
def rejas(D, x0, y0, x1, y1, seed, col="#FFFFFF", shade="#3A2A3A", cell=56):
    """Puerto Rican wrought-iron rejas: a frame of bars with paired scrolls and a central lozenge in each bay."""
    out = []
    lines = []
    for y in (y0, y1):
        lines.append(f"M {x0} {y} L {x1} {y}")
    n = int((x1 - x0) / cell)
    w = (x1 - x0) / n
    for i in range(n + 1):
        x = x0 + i * w
        lines.append(f"M {x:.1f} {y0} L {x:.1f} {y1}")
    mid = (y0 + y1) / 2
    for i in range(n):
        x = x0 + i * w + w / 2
        h = (y1 - y0) / 2 - 6
        lines.append(f"M {x:.1f} {mid - h:.1f} L {x + w * 0.32:.1f} {mid:.1f} L {x:.1f} {mid + h:.1f} L {x - w * 0.32:.1f} {mid:.1f} Z")
        for sg in (-1, 1):
            lines.append(f"M {x:.1f} {mid - h:.1f} q {sg * w * 0.42:.1f} {h * 0.1:.1f} {sg * w * 0.38:.1f} {h * 0.42:.1f} q {-sg * w * 0.04:.1f} {h * 0.14:.1f} {-sg * w * 0.14:.1f} {h * 0.06:.1f}")
            lines.append(f"M {x:.1f} {mid + h:.1f} q {sg * w * 0.42:.1f} {-h * 0.1:.1f} {sg * w * 0.38:.1f} {-h * 0.42:.1f} q {-sg * w * 0.04:.1f} {-h * 0.14:.1f} {-sg * w * 0.14:.1f} {-h * 0.06:.1f}")
        lines.append(f"M {x - 4:.1f} {mid:.1f} a 4 4 0 1 0 8 0 a 4 4 0 1 0 -8 0")
    d = " ".join(lines)
    out.append(f'<path d="{d}" fill="none" stroke="{shade}" stroke-width="6.5" stroke-linejoin="round" stroke-linecap="round" opacity="0.35" transform="translate(2.5 3)"/>')
    out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>')
    out.append(f'<path d="{d}" fill="none" stroke="#B8B0C0" stroke-width="1.2" stroke-linejoin="round" opacity="0.6" transform="translate(1 1.4)"/>')
    return "".join(out)


def rocking_chair(D, ox, oy, s, seed, yaw=-34, wood=CAOBA):
    """Caned mahogany rocking chair (sillón de pajilla) built in 3d and projected."""
    C = Cam3(ox, oy, s, yaw, 12)
    X = 60

    def rk(z):
        return 10 * ((z - 50) / 100) ** 2 * 4 - 2

    def pz(h):
        return 100 + 34 * (h - 110) / 190

    out = [cast(D, ox + 10 * s, oy + 6, 150 * s, 26 * s, strength=0.45, seed=seed)]
    parts = []
    # order by depth of each side: draw the far side first
    sides = sorted((-X, X), key=lambda x: -C.depth(x, 0, 50))
    for k, x in enumerate(sides):
        far = k == 0
        pal = tuple(dk(c, 0.18) for c in wood) if far else wood
        rpts = [C(x, rk(z), z) for z in range(-55, 165, 10)]
        parts.append(taper(rpts, 9 * s, 9 * s, pal[1]))
        parts.append(pline(rpts, pal[2], 1.6, seed + k, 0.7, 1))
        parts.append(taper([(px, py - 3 * s) for px, py in rpts[2:-2]], 2.4 * s, 2.4 * s, pal[0], 0.6))
        parts.append(rod(C, (x, rk(0), 0), (x, 182, 0), 9 * s, 8 * s, pal, seed + 10 + k))
        parts.append(rod(C, (x, rk(100), 100), (x, 110, 100), 9 * s, 8.5 * s, pal, seed + 20 + k))
        if far:
            parts.append(("BACK",))
        parts.append(rod(C, (x, 110, 100), (x * 0.97, 300, pz(300)), 8.5 * s, 7 * s, pal, seed + 30 + k))
        parts.append(disc(*C(x * 0.97, 306, pz(306)), 6 * s, pal[1]) + disc(*C(x * 0.97, 308, pz(308)), 2.5 * s, pal[0], 0.7))
        parts.append(rod(C, (x * 1.05, 192, pz(192)), (x * 1.08, 184, -12), 10 * s, 11 * s, pal, seed + 40 + k))
        parts.append(rod(C, (x, 40, 0), (x, 40, 100), 5 * s, 5 * s, pal, seed + 50 + k, 0.8))
        if far:
            parts.append(("SEAT",))
    for p in parts:
        if isinstance(p, tuple) and p[0] == "BACK":
            back = C.pts([(-X * 0.9, 150, pz(150)), (X * 0.9, 150, pz(150)), (X * 0.9, 282, pz(282)), (-X * 0.9, 282, pz(282))])
            out.append(cane(D, back, seed + 60, step=6.2 * s / 1.0))
            out.append(ink(pd(back), INK, 1.4, seed + 61, 1, 0.6))
            crest = [C(x, 288 + 10 * (1 - (x / X) ** 2), pz(292)) for x in range(-X, X + 1, 10)]
            out.append(taper(crest, 14 * s, 14 * s, wood[1]))
            out.append(taper([(px, py - 4 * s) for px, py in crest], 3 * s, 3 * s, wood[0], 0.7))
            out.append(pline(crest, wood[2], 1.4, seed + 62, 0.6, 1))
            out.append(rod(C, (-X, 148, pz(148)), (X, 148, pz(148)), 7 * s, 7 * s, wood, seed + 63))
        elif isinstance(p, tuple) and p[0] == "SEAT":
            seat = C.pts([(-X, 112, 0), (X, 112, 0), (X, 112, 100), (-X, 112, 100)])
            out.append(cane(D, seat, seed + 70, step=6.2 * s))
            out.append(ink(pd(seat), INK, 1.4, seed + 71, 1, 0.6))
            out.append(rod(C, (-X, 106, -2), (X, 106, -2), 9 * s, 9 * s, wood, seed + 72))
        else:
            out.append(p)
    return "".join(out), C


def rosary(D, pts, seed, bead="#F6F0F8", cross="#C8A040"):
    out = [pline(pts, "#8A7A6A", 1.0, seed, 0.8, 1)]
    path = catmull(pts, 6)
    for i, (x, y) in enumerate(path[::2]):
        out.append(disc(x, y, 2.6, bead) + disc(x - 0.7, y - 0.8, 0.9, "#FFFFFF", 0.9))
    ex, ey = path[-1]
    out.append(f'<path d="M {ex - 1.6:.1f} {ey:.1f} h 3.2 v 6 h 4 v 3 h -4 v 10 h -3.2 v -10 h -4 v -3 h 4 Z" fill="{cross}" stroke="#7A5A1A" stroke-width="0.8"/>')
    return "".join(out)


def mata_en_lata(D, cx, base, w, seed, kind="sansevieria", can=("#F2F2F4", "#B8BCC6", "#6A707A"), label_col="#D52B1E"):
    """Mami's plants in old painted cans: a tin (painted band), soil, and a plant."""
    rnd = random.Random(seed)
    h = w * 1.05
    out = [cast(D, cx + 6, base, w * 0.75, 7, strength=0.45, seed=seed)]
    out.append(painted(D, rect_pts(cx - w / 2, base - h, cx + w / 2, base, 12, seed, 0.4), can, seed, sdir=(1, 0.2), sk=0.2, angle=-90, n=14, inkw=1.4, hi=0.5))
    out.append(f'<path d="{hg.org_rect(cx - w / 2, base - h * 0.62, w, h * 0.34, seed + 1, 0.4, 10, 1)}" fill="{label_col}"/>')
    out.append(f'<path d="{hg.org_rect(cx - w / 2, base - h * 0.62, w, h * 0.34, seed + 1, 0.4, 10, 1)}" fill="{D.lin([(0, "#FFFFFF", 0.25), (0.4, "#FFFFFF", 0), (1, "#000000", 0.3)], 0, 0, 1, 0)}"/>')
    for k in range(4):
        out.append(pline([(cx - w / 2 + 2, base - h + 4 + k * 3 + (h - 10) * (k // 2) * 0.9), (cx + w / 2 - 2, base - h + 4 + k * 3 + (h - 10) * (k // 2) * 0.9)], can[2], 0.9, seed + k, 0.5, 1))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - h, w / 2, w * 0.12, 0, 360, 16))}" fill="#4A2A14"/>')
    if kind == "sansevieria":
        for k in range(7):
            x = cx + (k - 3) * w * 0.12
            L = w * rnd.uniform(1.3, 2.1)
            a = -90 + (k - 3) * 9 + rnd.uniform(-4, 4)
            out.append(leaf_simple(D, x, base - h + 2, L, w * 0.09, a, ("#B8D87A", "#3E8A4A", "#1E4A2A"), seed + 10 + k, vein=False, inkw=0.9))
            out.append(pline([(x, base - h - L * 0.3), (x + math.cos(math.radians(a)) * L * 0.6, base - h + math.sin(math.radians(a)) * L * 0.6)], "#E8E070", 1.2, seed + k, 0.5, 1))
    elif kind == "coleo":
        for k in range(9):
            a = -90 + (k - 4) * 22 + rnd.uniform(-6, 6)
            L = w * rnd.uniform(0.8, 1.2)
            out.append(leaf_simple(D, cx + (k - 4) * 2, base - h, L, L * 0.35, a, rnd.choice([("#F68AB0", "#C8306A", "#6A1036"), ("#D8E87A", "#8AA83A", "#3E5A14")]), seed + 20 + k, vein=True, inkw=0.9))
    else:  # amapola (hibiscus bush)
        for k in range(8):
            a = -90 + (k - 3.5) * 24
            out.append(leaf_simple(D, cx, base - h, w * 0.9, w * 0.28, a, SELVA, seed + 30 + k, vein=True, inkw=0.9))
        for k, (dx, dy) in enumerate(((-0.4, -1.1), (0.35, -1.3), (0.05, -1.6))):
            out.append(hibiscus(D, cx + dx * w, base - h + dy * w * 0.6, w * 0.24, ROJO, seed + 40 + k, k * 40, inkw=1))
    return "".join(out)


@design("bendicion")
def bendicion():
    D = Doc2("prbn")
    # late-afternoon sky over the hills, seen through the balcony rejas
    out = [sky(D, [(0, "#FBEFD8"), (0.45, "#F8D8B8"), (0.75, "#F2B48E"), (1, "#E89A7A")], 301, 600, ["#FFF4E0", "#F2C8A8", "#FFE8D0"], 80, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 470, 330, 200, "#FFE6A8", 0.6))
    out.append(hill(D, ridge([(-20, 352), (120, 316), (260, 340), (400, 300), (620, 330)], 302, 10, 4), 480, ("#C8B8C8", "#A898B4", "#7A6A90"), 303, inkw=0, sop=(0.08, 0.2)))
    out.append(hill(D, ridge([(-20, 380), (160, 352), (320, 372), (470, 346), (620, 366)], 304, 8, 4), 480, ("#8AB88A", "#5E9A6A", "#3A6A4A"), 305, inkw=1.2, inkop=0.3))
    rnd = random.Random(306)
    for _ in range(14):
        x = rnd.uniform(0, 600)
        out.append(f'<path d="{blob(x, 372 + rnd.uniform(-6, 14), rnd.uniform(5, 9), rnd.uniform(4, 6), rnd.randint(0, 999), 0.2, 8)}" fill="{rnd.choice(["#FFF4E8", "#F2D8C8", "#F8E8A8"])}" opacity="0.9"/>')
    # balcony wall: low parapet and the white rejas above it
    out.append(painted(D, rect_pts(-10, 392, 610, 480, 30, 307, 0.5), ("#FFF6E8", "#F2E2CC", "#C8B094"), 307, sdir=(0.2, 1), sk=0.1, angle=0, n=40, inkw=1.6, hi=0.3))
    out.append(f'<path d="{hg.org_rect(-10, 386, 620, 12, 308, 0.4, 30, 1)}" fill="#E8D4B8"/>')
    out.append(rejas(D, -12, 272, 612, 386, 309, cell=62))
    # mosaic floor
    out.append(tile_floor(D, 480, 600, 310, a="#C04A3A", b="#2E5E86", cell=46, squash=0.4, op=0.75))
    out.append(f'<rect y="480" width="600" height="120" fill="#F4E8D4" opacity="0.2"/>')
    out.append(f'<rect y="476" width="600" height="7" fill="#7A5A3A" opacity="0.45"/>')
    # potted plants in cans by the wall
    out.append(mata_en_lata(D, 548, 492, 52, 311, "sansevieria", label_col="#2F6CC6"))
    # side table with café and an abanico
    tx, ty = 128, 414
    out.append(cast(D, tx + 20, 546, 70, 12, strength=0.45, seed=312))
    out.append(taper([(tx, ty + 8), (tx + 2, 490), (tx - 1, 534)], 12, 9, CAOBA[1]))
    for sg in (-1, 1):
        out.append(taper([(tx, 530), (tx + sg * 30, 542)], 7, 5, CAOBA[1]))
    out.append(painted(D, ell_pts(tx, ty, 74, 16, 0, 360, 28), CAOBA, 313, sdir=(0.5, 1), sk=0.2, angle=0, n=12, inkw=1.6, hi=0.45))
    out.append(f'<path d="{smooth_closed(ell_pts(tx, ty + 6, 74, 16, 0, 180, 14) + ell_pts(tx, ty, 74, 16, 180, 0, 14))}" fill="{CAOBA[2]}" opacity="0.7"/>')
    out.append(cloth(D, [(tx - 50, ty - 6), (tx + 46, ty - 10), (tx + 52, ty + 4), (tx + 20, ty + 30), (tx - 30, ty + 28), (tx - 56, ty + 6)], "#2F6CC6", 314, cell=7, inkw=1.0))
    out.append(cup_saucer(D, tx + 6, ty + 6, 46, 315, rim=("#F4867A", "#D52B1E", "#8A1410")))
    out.append(steam(tx + 6, ty - 36, 40, 316, "#FFFFFF", 2, 16, 5, 0.75))
    # the rocking chair
    ch, C = rocking_chair(D, 364, 548, 0.88, 320)
    out.append(ch)
    # her rosary hanging over the arm
    ax, ay = C(-63, 186, -4)
    out.append(rosary(D, [(ax - 6, ay - 2), (ax - 12, ay + 14), (ax - 6, ay + 30), (ax + 4, ay + 22), (ax + 4, ay + 6)], 322))
    out.append(rosary(D, [(ax - 6, ay + 30), (ax - 9, ay + 44)], 323))
    # flamboyán petals blown onto the floor
    for k in range(9):
        x, y = rnd.uniform(60, 560), rnd.uniform(500, 580)
        out.append(f'<path d="{blob(x, y, 5, 3, 330 + k, 0.2, 8, rnd.uniform(0, 180))}" fill="#E8401E" opacity="0.9"/>')
    # lettering
    out.append(letters(D, 300, 128, "Bendición,", SERIF_IT, 104, "#1E4E9A", ["#3A6EC0", "#123A7A", "#5A8AD0"], 340, max_w=470,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#C8DCF6"))
    out.append(letters(D, 312, 202, "Abuela", SERIF_IT, 76, "#C8302A", ["#E85A48", "#8A1A12", "#F07A60"], 341, max_w=300,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#FFD0C0"))
    out.append(ruled(300, 238, "DIOS TE BENDIGA", "#7A3A28", font=JOS, size=18, ls=6, line_w=30, gap=12))
    return finish_b(D, out, 342)


# ================================================================ 4. flamboyán — the red umbrella tree over a country road
def flamboyan_tree(D, cx, base, w, h, seed, haze=0.0):
    """Royal poinciana: a short trunk splitting into wide limbs under a flat, spreading crown of scarlet blossom
    with feathery green leaves showing underneath."""
    rnd = random.Random(seed)
    hz = (lambda c: mix(c, "#E8D8D8", haze)) if haze else (lambda c: c)
    out = [cast(D, cx + 10, base + 4, w * 0.55, 16, "#1A3A10", 0.35, seed)]
    top = base - h
    # limbs
    trunk = ("#B09080", "#7A5A4A", "#3E2A22")
    limbs = [(-0.42, 0.62), (-0.24, 0.8), (-0.05, 0.92), (0.16, 0.85), (0.36, 0.68), (0.46, 0.55)]
    fork = (cx + 4, base - h * 0.32)
    out.append(taper([(cx - 6, base), (cx - 2, base - h * 0.18), fork], w * 0.1, w * 0.07, hz(trunk[1])))
    out.append(taper([(cx - 6 - w * 0.06, base + 2), (cx - 6, base - 10), (cx - 6 + w * 0.06, base + 2)], 6, 6, hz(trunk[1])))
    for k, (dx, hy) in enumerate(limbs):
        end = (cx + dx * w, base - h * hy)
        mid = ((fork[0] + end[0]) / 2 + rnd.uniform(-8, 8), (fork[1] + end[1]) / 2 + 12)
        out.append(taper([fork, mid, end], w * 0.04, w * 0.012, hz(trunk[1])))
        out.append(taper([(fork[0] - 2, fork[1] - 2), (mid[0] - 2, mid[1] - 2), (end[0] - 1, end[1] - 1)], w * 0.012, w * 0.004, hz(trunk[0]), 0.6))
    out.append(pline([(cx - 6 - w * 0.03, base), (cx - w * 0.028, base - h * 0.18), (fork[0] - w * 0.03, fork[1])], hz(trunk[2]), 1.6, seed, 0.6, 1))
    # the crown: a wide, flat-topped umbrella with a lumpy top and scalloped hanging edge
    ccx, ccy = cx, top + h * 0.3
    rx, ry = w * 0.5, h * 0.26
    bumps = [(rnd.uniform(0, 1), rnd.uniform(0.06, 0.12), rnd.uniform(0.04, 0.09)) for _ in range(9)]

    def top_y(t):
        y = ccy - ry * (math.sin(math.pi * t) ** 0.45)
        for c, wdt, amp in bumps:
            y -= ry * amp * 2.2 * math.exp(-((t - c) / wdt) ** 2)
        return y

    upper = [(ccx - rx + 2 * rx * t, top_y(t)) for t in [i / 40 for i in range(41)]]
    lower = []
    for i in range(41):
        t = 1 - i / 40
        lob = abs(math.sin(t * math.pi * 7)) * ry * 0.22
        lower.append((ccx - rx + 2 * rx * t, ccy + ry * 0.32 * math.sin(math.pi * t) ** 0.5 + lob))
    sil = upper + lower
    sd = smooth_closed(sil)
    # shade under the canopy and the feathery green leaflets along its underside
    out.append(f'<path d="{blob(ccx, ccy + ry * 0.75, rx * 0.92, ry * 0.42, seed + 1, 0.08, 20)}" fill="{hz("#1E3A14")}" opacity="0.45"/>')
    for _ in range(140):
        t = rnd.uniform(0.03, 0.97)
        x = ccx - rx + 2 * rx * t
        y = ccy + ry * 0.32 * math.sin(math.pi * t) ** 0.5 + rnd.uniform(0, ry * 0.4)
        out.append(f'<path d="{blob(x, y, rnd.uniform(5, 10), rnd.uniform(1.8, 3.2), rnd.randint(0, 999), 0.2, 8, rnd.uniform(-25, 25))}" fill="{hz(rnd.choice(["#4E8A2E", "#6AA83A", "#3A6A22", "#86BE4A"]))}"/>')
    out.append(wash(sd, hz("#A81E10"), seed + 2, 2, 1.2, 0.5))
    cid = D.clip(f'<path d="{sd}"/>')
    dabs = []
    for _ in range(int(rx * ry * 0.09)):
        t = rnd.random()
        x = ccx - rx + 2 * rx * t + rnd.uniform(-4, 4)
        y0, y1 = top_y(t), ccy + ry * 0.5
        y = rnd.uniform(y0 - 4, y1)
        v = (y - y0) / max(1, y1 - y0)                    # 0 top .. 1 bottom
        lit = (1 - v) * 0.8 + (1 - t) * 0.35 + rnd.uniform(-0.2, 0.2)
        if lit > 0.85:
            col = rnd.choice(["#FFB07A", "#FF9466", "#FFC890"])
        elif lit > 0.5:
            col = rnd.choice(["#F25A2A", "#E8401E", "#FF7A4A"])
        elif lit > 0.25:
            col = rnd.choice(["#D8301A", "#C8281A", "#E0401E"])
        else:
            col = rnd.choice(["#9A1A0E", "#7A120A", "#B0200E"])
        r = rnd.uniform(4, 8.5)
        dabs.append(f'<path d="{blob(x, y, r, r * 0.8, rnd.randint(0, 9999), 0.25, 8, rnd.uniform(0, 180))}" fill="{hz(col)}" opacity="{rnd.uniform(0.8, 1):.2f}"/>')
    out.append(f'<g {cid}>{"".join(dabs)}</g>')
    # frilly blossoms breaking the silhouette
    for _ in range(90):
        t = rnd.random()
        x = ccx - rx + 2 * rx * t
        y = top_y(t) + rnd.uniform(-3, 5)
        col = rnd.choice(["#FF9466", "#F25A2A", "#FFB07A"]) if t < 0.6 else rnd.choice(["#E8401E", "#D8301A"])
        out.append(f'<path d="{blob(x, y, rnd.uniform(3.5, 6), rnd.uniform(3, 4.5), rnd.randint(0, 9999), 0.3, 8)}" fill="{hz(col)}"/>')
    for _ in range(40):
        t = rnd.uniform(0.04, 0.96)
        x = ccx - rx + 2 * rx * t
        y = ccy + ry * 0.32 * math.sin(math.pi * t) ** 0.5 + abs(math.sin(t * math.pi * 7)) * ry * 0.22 + rnd.uniform(-2, 4)
        out.append(f'<path d="{blob(x, y, rnd.uniform(3, 5), rnd.uniform(2.5, 4), rnd.randint(0, 9999), 0.3, 8)}" fill="{hz(rnd.choice(["#B0200E", "#C8281A"]))}"/>')
    # a few dark seed pods hanging under the canopy
    for k in range(5):
        x = cx + rnd.uniform(-w * 0.36, w * 0.36)
        y = ccy + ry * 0.55
        out.append(taper([(x, y), (x + 3, y + 22), (x - 1, y + 42)], 4.5, 3, hz("#4A2A16"), 0.9))
    out.append(ink(smooth_open(upper), "#6A1408", 1.8, seed, 1, 0.4))
    return "".join(out)


def casita(D, x, base, w, h, seed, wall=("#D8F0D0", "#9AD0A8", "#4A8A64"), roof=ROJO, haze=0.0):
    """A small concrete country house: flat-ish roof edge, a balcony with rejas and Miami louvre windows."""
    hz = (lambda c: mix(c, "#D8E0E8", haze)) if haze else (lambda c: c)
    out = [painted(D, rect_pts(x, base - h, x + w, base, 10, seed, 0.4), tuple(hz(c) for c in wall), seed, sdir=(1, 0.2), sk=0.12, angle=-85, n=10, inkw=1.2, hi=0.3)]
    out.append(f'<path d="{hg.org_rect(x - 3, base - h - 4, w + 6, 6, seed + 1, 0.3, 10, 1)}" fill="{hz("#F8F4EC")}"/>')
    out.append(f'<path d="{hg.org_rect(x + w * 0.12, base - h * 0.72, w * 0.3, h * 0.4, seed + 2, 0.3, 8, 1)}" fill="{hz("#CFD4DA")}"/>')
    for k in range(5):
        yy = base - h * 0.72 + 3 + k * h * 0.075
        out.append(f'<path d="M {x + w * 0.12 + 1:.1f} {yy:.1f} l {w * 0.3 - 2:.1f} 0" stroke="{hz("#7A8494")}" stroke-width="1.2"/>')
    out.append(f'<path d="{hg.org_rect(x + w * 0.58, base - h * 0.66, w * 0.2, h * 0.66, seed + 3, 0.3, 8, 1)}" fill="{hz(roof[1])}"/>')
    out.append(f'<path d="M {x:.1f} {base - h * 0.36:.1f} L {x + w:.1f} {base - h * 0.36:.1f}" stroke="{hz("#FFFFFF")}" stroke-width="1.6"/>')
    return "".join(out)


def egret(x, y, s, flip=1):
    """Cattle egret (garza) in a pasture: white body, S-neck, yellow bill, dark legs."""
    f = flip
    body = blob(x, y, 9 * s, 5.5 * s, int(x), 0.06, 12, -12 * f)
    return (f'<path d="M {x - 2 * s:.1f} {y + 4 * s:.1f} l {-1 * s:.1f} {9 * s:.1f} M {x + 2 * s:.1f} {y + 4 * s:.1f} l {1 * s:.1f} {9 * s:.1f}" stroke="#3A3A2A" stroke-width="{max(1, 1 * s):.1f}"/>'
            f'<path d="{body}" fill="#FFFFFF"/>'
            f'<path d="M {x - 6 * s * f:.1f} {y - 2 * s:.1f} q {-4 * s * f:.1f} {-3 * s:.1f} {-2 * s * f:.1f} {-8 * s:.1f}" stroke="#FFFFFF" stroke-width="{3.2 * s:.1f}" fill="none" stroke-linecap="round"/>'
            f'<path d="M {x - 8.5 * s * f:.1f} {y - 10 * s:.1f} l {-5 * s * f:.1f} {1.2 * s:.1f}" stroke="#F2B83A" stroke-width="{1.4 * s:.1f}" stroke-linecap="round"/>'
            + ink(body, "#8A8A7A", 0.8, int(y), 1, 0.6))


@design("flamboyan")
def flamboyan():
    D = Doc2("prfb")
    out = [sky(D, [(0, "#4A9AE0"), (0.5, "#8EC8F0"), (1, "#D8EEF6")], 401, 440, ["#B8E0F8", "#6AB0E8", "#FFFFFF"], 70)]
    out.append(puff_cloud(D, 470, 236, 150, 402))
    out.append(puff_cloud(D, 96, 252, 110, 403))
    # distant mogotes (karst hills) and the cordillera
    out.append(hill(D, ridge([(-20, 300), (140, 270), (300, 290), (450, 262), (620, 284)], 404, 10, 4), 600, ("#B8D0DC", "#9AB8CC", "#7A98B0"), 405, inkw=0, sop=(0.06, 0.16)))
    mog = []
    for k, (x, w, h) in enumerate(((30, 70, 40), (110, 60, 52), (182, 80, 44), (420, 70, 50), (500, 60, 38), (568, 70, 46))):
        mog.append(painted(D, [(x - w / 2, 330), (x - w * 0.42, 330 - h * 0.7), (x - w * 0.2, 330 - h), (x + w * 0.2, 330 - h), (x + w * 0.44, 330 - h * 0.6), (x + w / 2, 330)],
                           ("#9ACB9A", "#6AA87A", "#3E7A56"), 406 + k, sdir=(0.8, 0.4), sk=0.18, n=10, inkw=0.9, inkop=0.35, hi=0.3))
    out.append("".join(mog))
    out.append(hill(D, ridge([(-20, 336), (160, 320), (340, 334), (480, 318), (620, 330)], 412, 6, 3), 600, ("#A8D27A", "#7AB24E", "#4A7A2E"), 413, inkw=1.2, inkop=0.35))
    # little house and a palm on the far pasture
    out.append(casita(D, 470, 344, 60, 34, 414))
    out.append(palm(D, (548, 350), (556, 282), 415, L=42, width=6, nuts=False))
    # the road sweeping in from the bottom
    road = [(352, 640), (404, 548), (446, 456), (472, 388), (482, 354), (490, 354), (498, 388), (518, 456), (556, 548), (622, 640)]
    out.append(hill(D, ridge([(-20, 360), (200, 350), (420, 364), (620, 352)], 416, 6, 3), 600, ("#B8DC80", "#86BA52", "#4E8A2E"), 417, inkw=0, sop=(0.12, 0.3)))
    out.append(painted(D, road, ("#A8A0A8", "#7E7882", "#4E4856"), 418, sdir=(1, 0), sk=0.1, angle=-75, n=40, inkw=1.4, inkop=0.5, hi=0.2))
    for k in range(9):
        t0, t1 = k / 9, k / 9 + 0.05
        y0, y1 = 352 + 254 * t0 ** 1.5, 352 + 254 * t1 ** 1.5
        x0, x1 = 486 - 4 * t0, 486 - 4 * t1
        out.append(taper([(x0, y0), (x1, y1)], 1 + 5 * t0, 1 + 5 * t1, "#F6D24A", 0.9))
    out.append(grass(420, (0, 380, 600, 600), ["#5E9A3A", "#8ABE52", "#3E7A2A", "#A8D46A"], 260, (8, 18), 1.4))
    out.append(egret(116, 420, 1.2))
    out.append(egret(156, 432, 1.0, -1))
    # the flamboyán
    out.append(flamboyan_tree(D, 238, 500, 430, 318, 421))
    # fallen petals carpeting the grass and the road
    rnd = random.Random(422)
    for _ in range(140):
        x = rnd.gauss(236, 120)
        y = rnd.uniform(470, 600)
        if y < 470 + abs(x - 236) * 0.1:
            continue
        out.append(f'<path d="{blob(x, y, rnd.uniform(2.5, 5), rnd.uniform(1.6, 3), rnd.randint(0, 999), 0.25, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#E8401E", "#F26A1E", "#D82A1A", "#FF8A5A"])}" opacity="0.9"/>')
    for _ in range(14):
        x, y = rnd.uniform(60, 540), rnd.uniform(160, 440)
        if 120 < y < 360 and 40 < x < 440:
            continue
        out.append(f'<path d="{blob(x, y, 4, 2.6, rnd.randint(0, 999), 0.25, 8, rnd.uniform(0, 180))}" fill="#E8401E" opacity="0.85"/>')
    # lettering
    out.append(letters(D, 300, 116, "flamboyán", SERIF_IT, 112, "#C8241A", ["#E8483A", "#8A1408", "#F2704A"], 430, max_w=460,
                       shadow="#FFFFFF", soff=(0.016, 0.028), angle=-40, hi="#FFD0C0"))
    out.append(ruled(300, 158, "FLORECE EN JUNIO", "#1E4E8A", font=JOS, size=19, ls=7, line_w=36, gap=14))
    return finish_b(D, out, 431)


# ================================================================ 5. ¡wepa! — plena panderos and confetti
def ellipse_pts(cx, cy, rx, ry, ang, a0=0, a1=360, n=36):
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    out = []
    for i in range(n + 1):
        t = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out


def pandero(D, cx, cy, r, tilt, ang, seed, head=("#FFF6E0", "#F2E2C0", "#C8A878"), rim=("#E8B478", "#A86A34", "#5A3416"), flag=False):
    """Plena pandero: a jingle-less frame drum, goatskin head tucked into a deep wooden hoop, seen tilted."""
    ry = r * tilt
    dep = r * 0.32 * math.sqrt(max(0.05, 1 - tilt * tilt))
    dx, dy = -math.sin(math.radians(ang)) * dep, math.cos(math.radians(ang)) * dep
    out = [cast(D, cx + dx * 1.6 + 10, cy + dy * 1.6 + 12, r * 1.02, ry * 1.05, "#3A0A04", 0.35, seed)]
    back = ellipse_pts(cx + dx, cy + dy, r, ry, ang)
    out.append(f'<path d="{smooth_closed(back[:-1])}" fill="{rim[2]}"/>')
    band = ellipse_pts(cx, cy, r, ry, ang, 0, 180, 18) + ellipse_pts(cx + dx, cy + dy, r, ry, ang, 180, 0, 18)
    out.append(painted(D, band, rim, seed, sdir=(0, 1), sk=0.12, angle=ang, n=30, slen=(r * 0.1, r * 0.3), inkw=1.8, hi=0.45, hik=0.15))
    # tacks along the hoop
    for k in range(9):
        t = 18 + k * 18
        (ax, ay), (bx, by) = ellipse_pts(cx, cy, r, ry, ang, t, t, 1)[0], ellipse_pts(cx + dx, cy + dy, r, ry, ang, t, t, 1)[0]
        out.append(disc(ax + (bx - ax) * 0.3, ay + (by - ay) * 0.3, max(1.6, r * 0.022), "#E8E0D0") + disc(ax + (bx - ax) * 0.3 + 0.6, ay + (by - ay) * 0.3 + 0.6, max(0.8, r * 0.01), "#5A4A3A", 0.7))
    # the wooden lip around the head, then the skin
    lip = ellipse_pts(cx, cy, r, ry, ang)
    out.append(f'<path d="{smooth_closed(lip[:-1])}" fill="{rim[0]}"/>')
    hd = smooth_closed(ellipse_pts(cx, cy, r * 0.93, ry * 0.92, ang)[:-1])
    out.append(f'<path d="{hd}" fill="{head[1]}"/>')
    cid = D.clip(f'<path d="{hd}"/>')
    inner = []
    if flag:
        x0, hh = cx - r, 2 * r
        fl = []
        for i in range(5):
            if i % 2 == 0:
                fl.append(f'<rect x="{x0:.1f}" y="{cy - r + i * hh / 5:.1f}" width="{2 * r:.1f}" height="{hh / 5 + 0.5:.1f}" fill="#D52B1E" opacity="0.9"/>')
        fl.append(f'<path d="M {x0:.1f} {cy - r:.1f} L {x0 + r * 1.3:.1f} {cy:.1f} L {x0:.1f} {cy + r:.1f} Z" fill="#2F6CC6"/>')
        fl.append(f'<path d="{star_d(x0 + r * 0.45, cy, r * 0.26)}" fill="#FFFFFF"/>')
        inner.append(f'<g transform="translate({cx} {cy}) rotate({ang}) scale(1 {tilt}) translate({-cx} {-cy})">{"".join(fl)}</g>')
    inner.append(strokes(D.nid(), hd, (cx - r, cy - r, cx + r, cy + r), [head[0], head[2], "#FFFFFF"], seed + 4, n=int(r * 0.9), angle=ang - 20,
                         length=(r * 0.2, r * 0.6), width=(1, 3), opacity=(0.08, 0.25)))
    inner.append(f'<path d="{blob(cx + r * 0.18, cy + ry * 0.05, r * 0.26, ry * 0.24, seed + 5, 0.3, 12, ang)}" fill="#8A6A3A" opacity="0.16"/>')
    inner.append(f'<path d="{hd}" fill="{D.rad([(0, "#FFFFFF", 0.35), (0.55, "#FFFFFF", 0), (1, "#3A1A06", 0.4)], cx=0.36, cy=0.32, r=0.75)}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(hd, INK, 1.4, seed + 6, 1, 0.6))
    out.append(ink(smooth_closed(lip[:-1]), INK, 2, seed + 7, 2, 0.7))
    out.append(ink(smooth_open(ellipse_pts(cx + dx, cy + dy, r, ry, ang, 0, 180, 18)), INK, 2, seed + 8, 1, 0.7))
    out.append(taper(ellipse_pts(cx, cy, r * 0.985, ry * 0.97, ang, 200, 300, 10), 2.6, 2.6, "#FFF0D0", 0.7))
    return "".join(out)


def serpentina(x, y, L, ang, seed, col, w=5.0, loops=2.5, R=12):
    """A curled paper streamer (serpentina) uncoiling from (x, y)."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    pts = []
    for i in range(70):
        t = i / 69
        ph = t * loops * 2 * math.pi + rnd.uniform(0, 0.05)
        rr = R * (0.6 + 0.4 * t)
        pts.append((x + ux * L * t + rr * math.cos(ph) * 0.9 - ux * rr, y + uy * L * t + rr * math.sin(ph)))
    return taper(pts, w, w * 0.8, col) + taper([(px - 0.8, py - 1.2) for px, py in pts], w * 0.3, w * 0.25, lt(col, 0.5), 0.7)


def pr_bunting(D, x0, y0, x1, y1, sag, n, seed, size=26):
    """A fiesta string of little Puerto Rican flags alternating with plain pennants."""
    out = []

    def pt(t):
        return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)

    out.append(ink(smooth_open([pt(i / 30) for i in range(31)]), "#6A4A2A", 1.8, seed, 2, 0.95))
    rnd = random.Random(seed)
    for i in range(n):
        t0, t1 = (i + 0.12) / n, (i + 0.88) / n
        a, b = pt(t0), pt(t1)
        h = size * rnd.uniform(0.95, 1.08)
        sw = rnd.uniform(-1.5, 1.5)
        if i % 2 == 0:
            # a little flag hanging from its top edge
            w = b[0] - a[0]
            fx, fy = a[0], (a[1] + b[1]) / 2
            g = [f'<rect x="{fx:.1f}" y="{fy + k * h / 5:.1f}" width="{w:.1f}" height="{h / 5 + 0.3:.1f}" fill="{"#D52B1E" if k % 2 == 0 else "#FFFFFF"}"/>' for k in range(5)]
            g.append(f'<path d="M {fx:.1f} {fy:.1f} L {fx + h * 0.72:.1f} {fy + h / 2:.1f} L {fx:.1f} {fy + h:.1f} Z" fill="#2F6CC6"/>')
            g.append(f'<path d="{star_d(fx + h * 0.24, fy + h / 2, h * 0.14)}" fill="#FFFFFF"/>')
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            out.append(f'<g transform="rotate({ang:.1f} {fx:.1f} {fy:.1f}) skewX({sw:.1f})">{"".join(g)}'
                       f'<path d="M {fx:.1f} {fy:.1f} h {w:.1f} v {h:.1f} h {-w:.1f} Z" fill="none" stroke="{INK}" stroke-width="1.2" opacity="0.55"/></g>')
        else:
            col = rnd.choice(["#F6C21C", "#1FB5B2", "#FFFFFF", "#F26A1E"])
            tip = ((a[0] + b[0]) / 2 + sw * 2, (a[1] + b[1]) / 2 + h * 1.1)
            dd = hg.org_poly([a, b, tip], seed + i, 0.4, 8, 1.5)
            out.append(f'<path d="{dd}" fill="{col}"/>' + ink(dd, INK, 1.2, seed + i, 1, 0.55))
    return "".join(out)


def streamer(D, pts, w, col, seed):
    path = catmull(pts, 8)
    out = [taper(path, w, w * 0.7, col)]
    out.append(taper([(x - 1, y - w * 0.25) for x, y in path], w * 0.25, w * 0.15, lt(col, 0.5), 0.6))
    return "".join(out)


@design("wepa")
def wepa():
    D = Doc2("prwp")
    out = [paper(D.nid(), "#FCE6A8", FLECK, 501)]
    # a hand-painted sunburst from below
    cx, cy = 300, 470
    rays = []
    for k in range(28):
        a0 = math.radians(-180 + k * 360 / 28)
        a1 = math.radians(-180 + (k + 0.5) * 360 / 28)
        rays.append(f'<path d="M {cx} {cy} L {cx + 900 * math.cos(a0):.1f} {cy + 900 * math.sin(a0):.1f} L {cx + 900 * math.cos(a1):.1f} {cy + 900 * math.sin(a1):.1f} Z" fill="#F6B03A" opacity="0.38"/>')
    out.append("".join(rays))
    out.append(soft_glow(D, cx, cy, 340, "#FFF6D8", 0.65))
    out.append(blooms(502, ["#F2A23A", "#FFE8A0", "#E8803A"], 7, (0, 0, 600, 600), (90, 180), (0.06, 0.12)))
    out.append(pr_bunting(D, -20, 262, 620, 262, 40, 13, 503, size=30))
    # serpentinas uncoiling over everything
    out.append(serpentina(40, 330, 150, 20, 504, "#2F6CC6"))
    out.append(serpentina(420, 316, 150, 15, 505, "#D52B1E"))
    out.append(serpentina(60, 560, 120, -25, 506, "#1FB5B2", 4))
    out.append(serpentina(440, 572, 120, -15, 507, "#F6C21C", 4))
    # three panderos: seguidor (big), punteador with the flag, requinto
    out.append(pandero(D, 196, 432, 116, 0.62, -16, 510))
    out.append(pandero(D, 414, 420, 100, 0.66, 18, 511, flag=True))
    out.append(pandero(D, 306, 512, 74, 0.55, -2, 512, rim=("#F0C080", "#C88A44", "#6A4018")))
    # confetti
    rnd = random.Random(513)
    for _ in range(90):
        x, y = rnd.uniform(40, 560), rnd.uniform(300, 580)
        if math.hypot(x - 196, (y - 440) / 0.75) < 118 or math.hypot(x - 414, (y - 428) / 0.75) < 102 or math.hypot(x - 306, (y - 518) / 0.65) < 78:
            continue
        c = rnd.choice(["#D52B1E", "#2F6CC6", "#FFFFFF", "#F6C21C", "#1FB5B2"])
        a = rnd.uniform(0, 180)
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{rnd.uniform(6, 10):.1f}" height="{rnd.uniform(3, 5):.1f}" fill="{c}" transform="rotate({a:.0f} {x:.1f} {y:.1f})" stroke="#3A2418" stroke-width="0.6" stroke-opacity="0.4"/>')
    for x, y in ((80, 222), (526, 214), (556, 520), (48, 470)):
        out.append(sparkle(x, y, 10, "#FFFFFF", 0.9))
    # lettering
    out.append(letters(D, 300, 178, "¡Wepa!", SERIF_IT, 150, "#D52B1E", ["#F05A4A", "#9A1410", "#FF7A60"], 530, max_w=440,
                       shadow="#123A7A", soff=(0.025, 0.04), angle=-40, hi="#FFD0C0"))
    out.append(ruled(300, 232, "¡QUE SIGA LA PLENA!", "#123A7A", font=JOS, size=20, ls=5, line_w=30, gap=12))
    return finish_b(D, out, 531)


# ================================================================ 6. arroz con gandules — the caldero and its pegao
def caldero(D, cx, cy, rx, ry, depth, seed):
    """Cast-aluminium caldero seen from above at an angle: thick rim, two loop handles, soot on the belly."""
    out = [cast(D, cx + 14, cy + depth + ry * 0.6, rx * 1.06, ry * 0.5, "#0A0A0A", 0.5, seed)]
    # handles
    for sg in (-1, 1):
        hx = cx + sg * rx
        hp = [(hx - sg * 6, cy - 6), (hx + sg * 30, cy - 4), (hx + sg * 40, cy + 14), (hx + sg * 28, cy + 30), (hx - sg * 4, cy + 26)]
        out.append(ink(smooth_open(hp), "#4A4E56", 13, seed + sg, 1, 1))
        out.append(ink(smooth_open(hp), "#C8CCD4", 6, seed + sg + 3, 1, 1))
    # body below the rim
    body = ell_pts(cx, cy, rx, ry, 0, 180, 20) + [(cx - rx * 0.92, cy + depth * 0.4)][:0]
    body = [(cx + rx, cy)] + [(cx + rx * 0.97, cy + depth * 0.6), (cx + rx * 0.82, cy + depth * 0.95)] + \
           [(cx + rx * 0.82 * math.cos(math.radians(a)), cy + depth + ry * 0.75 * math.sin(math.radians(a))) for a in range(10, 171, 20)] + \
           [(cx - rx * 0.82, cy + depth * 0.95), (cx - rx * 0.97, cy + depth * 0.6), (cx - rx, cy)]
    out.append(painted(D, body, ALUM, seed, sdir=(1, 0.3), sk=0.2, angle=-90, n=40, slen=(10, 30), sw=(1, 3), cols=["#FFFFFF", "#8A909A", "#D8DCE2"], inkw=2, hi=0.5, hik=0.06))
    bd = smooth_closed(body)
    cid = D.clip(f'<path d="{bd}"/>')
    out.append(f'<g {cid}><path d="{blob(cx + 20, cy + depth + ry * 0.6, rx * 0.95, ry * 0.7, seed + 2, 0.1, 18)}" fill="#2A2A30" opacity="0.55"/>'
               f'<path d="{blob(cx - rx * 0.55, cy + depth * 0.5, rx * 0.12, depth * 0.35, seed + 3, 0.1, 10)}" fill="#FFFFFF" opacity="0.6"/></g>')
    # rim
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, 40))}" fill="#D8DCE2"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, 40))}" fill="{D.lin([(0, "#FFFFFF", 0.7), (0.5, "#FFFFFF", 0), (1, "#3A3E46", 0.5)], 0, 0, 1, 1)}"/>')
    out.append(ink(smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, 40)), "#2A2E36", 2, seed + 4, 1, 0.8))
    return "".join(out)


@design("arroz-con-gandules")
def arroz_con_gandules():
    D = Doc2("prag")
    out = [sky(D, [(0, "#1E5E62"), (1, "#123E44")], 601, 600, ["#2E7478", "#0E3438", "#3A8A88"], 110, angle=-80, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 300, 380, 300, "#FFE0A0", 0.28))
    out.append(blooms(602, ["#2E7A78", "#0E3438"], 6, (0, 0, 600, 600), (100, 180), (0.08, 0.14)))
    # a checked kitchen towel under one side and a few loose gandules in their pods
    out.append(cloth(D, [(-20, 470), (150, 452), (230, 520), (200, 620), (-20, 620)], "#D52B1E", 603, cell=13, rot_=-14,
                     folds=[((20, 500), (90, 540), (130, 610))]))
    for k, (x, y, a) in enumerate(((520, 520, -30), (470, 560, 10))):
        pod = rot([(x - 46, y), (x - 30, y - 10), (x + 30, y - 10), (x + 50, y - 2), (x + 30, y + 10), (x - 30, y + 10)], x, y, a)
        out.append(painted(D, pod, ("#C8D88A", "#8AA850", "#4A6A22"), 604 + k, sk=0.2, angle=a, n=8, inkw=1.4, hi=0.4))
        for j in range(4):
            px, py = rot([(x - 26 + j * 17, y - 1)], x, y, a)[0]
            out.append(f'<path d="{blob(px, py, 6.5, 5, 610 + j + k * 7, 0.1, 8)}" fill="#7A8A3A" stroke="#3A4A14" stroke-width="0.8"/>')
    # the caldero
    cx, cy, rx, ry = 300, 392, 196, 112
    out.append(caldero(D, cx, cy, rx, ry, 70, 620))
    rice = blob(cx, cy + 6, rx - 16, ry - 12, 621, 0.01, 40)
    out.append(f'<path d="{rice}" fill="#E8A83A"/>')
    cid = D.clip(f'<path d="{rice}"/>')
    rnd = random.Random(622)
    inner = [f'<path d="{rice}" fill="{D.rad([(0, "#FFD27A"), (0.7, "#E8A23A"), (1, "#B8701E")], cx=0.45, cy=0.4, r=0.6)}"/>']
    # the dark inner wall of the pot at the back edge
    inner.append(f'<path d="{smooth_closed(ell_pts(cx, cy - ry * 0.95, rx * 0.95, ry * 0.4, 0, 360, 30))}" fill="#4A4E56" opacity="0.8"/>')
    inner.append(dashes(623, None, (cx - rx, cy - ry, cx + rx, cy + ry), 1100, ["#FFF0C0", "#FFE08A", "#F6C860", "#E8A23A", "#FFF6DA", "#D88A2A"], L=(3.5, 6.5), w=(2.4, 3.4)))
    for _ in range(70):
        x, y = rnd.uniform(cx - rx * 0.9, cx + rx * 0.9), rnd.uniform(cy - ry * 0.7, cy + ry * 0.9)
        inner.append(f'<path d="{blob(x, y, 5.2, 4.6, rnd.randint(0, 999), 0.12, 8)}" fill="{rnd.choice(["#7A7A2E", "#6A6A26", "#8A8A3A", "#5E5A22"])}"/>' +
                     disc(x - 1.6, y - 1.6, 1.3, "#E8E8A8", 0.7))
    for _ in range(14):
        x, y = rnd.uniform(cx - rx * 0.8, cx + rx * 0.8), rnd.uniform(cy - ry * 0.6, cy + ry * 0.8)
        inner.append(f'<path d="{blob(x, y, 7, 3.4, rnd.randint(0, 999), 0.2, 8, rnd.uniform(0, 180))}" fill="#D8302A"/>')
    for _ in range(8):
        x, y = rnd.uniform(cx - rx * 0.7, cx + rx * 0.7), rnd.uniform(cy - ry * 0.5, cy + ry * 0.7)
        inner.append(disc(x, y, 6.5, "#7A8A2A") + disc(x, y, 2.6, "#D8302A") + disc(x - 2, y - 2.4, 1.4, "#E8F0A8", 0.8))
    for _ in range(12):
        x, y = rnd.uniform(cx - rx * 0.8, cx + rx * 0.8), rnd.uniform(cy - ry * 0.6, cy + ry * 0.8)
        inner.append(f'<path d="{hg.org_rect(x, y, 9, 7, rnd.randint(0, 999), 0.5, 6, 1.5)}" fill="#E89A8A" stroke="#A8504A" stroke-width="0.8"/>')
    inner.append(specks(624, (cx - rx, cy - ry, cx + rx, cy + ry), ["#3E8A2A", "#2E6A1E"], 40, (1, 2.2), (0.7, 1)))
    inner.append(f'<path d="{rice}" fill="{D.rad([(0, "#000000", 0), (0.75, "#000000", 0), (1, "#3A1A04", 0.45)])}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # the scraped-up pegao: a golden-brown crust on a wooden spoon, lifted toward us
    sx0, sy0, sx1, sy1 = 360, 404, 560, 262
    out.append(taper([(sx0 + 30, sy0 - 20), ((sx0 + sx1) / 2, (sy0 + sy1) / 2 - 10), (sx1, sy1)], 13, 10, "#A86A34"))
    out.append(taper([(sx0 + 30, sy0 - 24), ((sx0 + sx1) / 2, (sy0 + sy1) / 2 - 14), (sx1, sy1 - 4)], 4, 3, "#E0A868", 0.7))
    bowl = rot(blob_pts(sx0 + 10, sy0 - 6, 50, 30, 625, 0.04, 16), sx0 + 10, sy0 - 6, -34)
    out.append(painted(D, bowl, ("#E0A868", "#A86A34", "#5A3416"), 625, sk=0.2, angle=-34, n=12, inkw=1.8, hi=0.4))
    crust = rot(blob_pts(sx0 + 8, sy0 - 10, 44, 24, 626, 0.12, 16), sx0 + 8, sy0 - 10, -30)
    out.append(painted(D, crust, ("#F2B860", "#B8701E", "#6A3A0A"), 626, sk=0.2, angle=-30, n=20, inkw=1.6, hi=0.5))
    out.append(dashes(627, smooth_closed(crust), bbox(crust), 120, ["#FFE0A0", "#8A4A10", "#C8802A", "#5A2A06"], L=(3, 5), w=(2, 3), D=D))
    out.append(specks(628, bbox(crust), ["#3A1A04"], 12, (1, 2), (0.5, 0.8)))
    out.append(steam(cx - 40, cy - 30, 60, 629, "#FFFFFF", 3, 30, 7, 0.45))
    # lettering
    out.append(letters(D, 300, 112, "arroz con", SERIF_IT, 84, "#FFF2D8", ["#FFFFFF", "#F2DCB4"], 630, max_w=380,
                       shadow="#06201E", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(letters(D, 300, 192, "gandules", SERIF_IT, 104, "#F6C21C", ["#FFE07A", "#D89A10", "#FFF0A0"], 631, max_w=420,
                       shadow="#06201E", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 242, "¡EL PEGAO ES MÍO!", "#FFF2D8", font=JOS, size=20, ls=5, line_w=30, gap=12, line="#F6C21C"))
    return finish_b(D, out, 632, "#FFFFFF", 0.5)


# ================================================================ 7. viejo san juan — blue adoquines running down to the bay
class Persp:
    """Pinhole camera looking down a street: x across, y up, z into the picture."""

    def __init__(self, F=300, eye=3.2, vx=300, vy=318):
        self.F, self.eye, self.vx, self.vy = F, eye, vx, vy

    def __call__(self, x, y, z):
        return (self.vx + self.F * x / z, self.vy - self.F * (y - self.eye) / z)

    def pts(self, ps):
        return [self(*p) for p in ps]


def yg(z):
    return -0.2 * max(0.0, z - 1.5)


def sj_facade(D, P, side, z0, z1, H, pal, seed, shutters, n=2, balcony=True, trim="#FFFFFF", plants=True):
    """One colonial row house on a street wall: painted pastel facade, white cornice, tall shuttered doors below,
    balcony doors and a wooden balcony above."""
    X = 3.4 * side
    rnd = random.Random(seed)
    zm = (z0 + z1) / 2
    y0 = yg(zm)
    top = y0 + H
    out = []
    wall = P.pts([(X, yg(z0), z0), (X, yg(z1), z1), (X, top, z1), (X, top, z0)])
    out.append(painted(D, poly_pts(wall, 14, seed, 0.4), pal, seed, sdir=(0.2, 1), sk=0.06, angle=-88, n=40, slen=(8, 30), sw=(1, 3),
                       inkw=1.2, inkop=0.5, hi=0.2))
    # base plinth band and cornice
    out.append(f'<path d="{pd(P.pts([(X, yg(z0), z0), (X, yg(z1), z1), (X, yg(z1) + 0.45, z1), (X, yg(z0) + 0.45, z0)]))}" fill="{dk(pal[1], 0.18)}" opacity="0.7"/>')
    out.append(f'<path d="{pd(P.pts([(X, top - 0.55, z0), (X, top - 0.55, z1), (X, top - 0.2, z1), (X, top - 0.2, z0)]))}" fill="{trim}"/>')
    out.append(f'<path d="{pd(P.pts([(X - side * 0.18, top - 0.2, z0), (X - side * 0.18, top - 0.2, z1), (X - side * 0.18, top, z1), (X - side * 0.18, top, z0)]))}" fill="{trim}"/>')
    out.append(pline(P.pts([(X, top - 0.55, z0), (X, top - 0.55, z1)]), dk(pal[1], 0.3), 1.2, seed, 0.6, 1))
    out.append(pline(P.pts([(X - side * 0.18, top - 0.2, z0), (X - side * 0.18, top - 0.2, z1)]), dk(pal[1], 0.35), 1.4, seed + 1, 0.6, 1))
    dw = min(0.62, (z1 - z0) / n * 0.42)
    for i in range(n):
        zc = z0 + (i + 0.5) * (z1 - z0) / n
        za, zb = zc - dw / 2, zc + dw / 2
        sc = shutters[i % len(shutters)]
        # ground floor door: white frame, wooden shutter doors with louvres
        fr = P.pts([(X, yg(za - 0.1), za - 0.1), (X, yg(zb + 0.1), zb + 0.1), (X, y0 + 2.85, zb + 0.1), (X, y0 + 2.85, za - 0.1)])
        out.append(f'<path d="{pd(fr)}" fill="{trim}"/>')
        dr = P.pts([(X, yg(za), za), (X, yg(zb), zb), (X, y0 + 2.7, zb), (X, y0 + 2.7, za)])
        out.append(f'<path d="{pd(dr)}" fill="{sc}"/>')
        for k in range(1, 12):
            yy = yg(zc) + (y0 + 2.7 - yg(zc)) * k / 12
            out.append(pline(P.pts([(X, yy, za + 0.02), (X, yy, zb - 0.02)]), dk(sc, 0.35), 1.1, seed + k, 0.6, 1))
        out.append(pline(P.pts([(X, yg(zc), zc), (X, y0 + 2.7, zc)]), dk(sc, 0.45), 1.4, seed + 20 + i, 0.8, 1))
        if rnd.random() < 0.45:
            # one leaf ajar: the dark inside shows
            out.append(f'<path d="{pd(P.pts([(X, yg(zc), zc), (X, yg(zb), zb), (X, y0 + 2.7, zb), (X, y0 + 2.7, zc)]))}" fill="#2A2028" opacity="0.75"/>')
        if H > 5.6:
            # upstairs balcony door and the balcony
            ub = y0 + 3.45
            out.append(f'<path d="{pd(P.pts([(X, ub - 0.05, za - 0.1), (X, ub - 0.05, zb + 0.1), (X, ub + 2.05, zb + 0.1), (X, ub + 2.05, za - 0.1)]))}" fill="{trim}"/>')
            out.append(f'<path d="{pd(P.pts([(X, ub, za), (X, ub, zb), (X, ub + 1.95, zb), (X, ub + 1.95, za)]))}" fill="{sc}"/>')
            for k in range(1, 9):
                yy = ub + 1.95 * k / 9
                out.append(pline(P.pts([(X, yy, za + 0.02), (X, yy, zb - 0.02)]), dk(sc, 0.35), 1.0, seed + 40 + k, 0.55, 1))
            if balcony:
                bz0, bz1 = za - 0.3, zb + 0.3
                Xb = X - side * 0.62
                slab = P.pts([(X, ub - 0.1, bz0), (X, ub - 0.1, bz1), (Xb, ub - 0.1, bz1), (Xb, ub - 0.1, bz0)])
                out.append(f'<path d="{pd(slab)}" fill="{dk(pal[1], 0.3)}" opacity="0.8"/>')
                out.append(f'<path d="{pd(P.pts([(Xb, ub - 0.1, bz0), (Xb, ub - 0.1, bz1), (Xb, ub - 0.3, bz1), (Xb, ub - 0.3, bz0)]))}" fill="{trim}"/>')
                rail = rnd.choice(["#24242C", "#24242C", "#6A3A1E"])
                bars = []
                m = max(5, int((bz1 - bz0) / 0.16))
                for k in range(m + 1):
                    zz = bz0 + (bz1 - bz0) * k / m
                    a, b = P(Xb, ub - 0.1, zz), P(Xb, ub + 0.95, zz)
                    bars.append(f"M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}")
                bw = max(1.0, 0.05 * P.F / zm)
                out.append(f'<path d="{" ".join(bars)}" stroke="{rail}" stroke-width="{bw:.1f}"/>')
                out.append(pline(P.pts([(Xb, ub + 0.95, bz0), (Xb, ub + 0.95, bz1)]), rail, max(2, bw * 2), seed + 70, 1, 1))
                out.append(pline(P.pts([(X, ub + 0.95, bz0), (Xb, ub + 0.95, bz0)]), rail, max(1.6, bw * 1.6), seed + 71, 1, 1))
                if plants and rnd.random() < 0.7:
                    px, py = P(Xb, ub + 1.0, (bz0 + bz1) / 2)
                    r = 0.42 * P.F / zm
                    for j in range(7):
                        out.append(f'<path d="{blob(px + rnd.uniform(-r, r), py - rnd.uniform(0, r * 0.7), r * 0.32, r * 0.26, rnd.randint(0, 999), 0.2, 8)}" fill="{rnd.choice(["#3E8A3A", "#5AA83E", "#2E6A2A"])}"/>')
                    for j in range(5):
                        out.append(disc(px + rnd.uniform(-r, r), py - rnd.uniform(0, r * 0.8), r * 0.16, rnd.choice(["#E8302A", "#F25A8A", "#FFFFFF"])))
    # weathering stains under the cornice
    for _ in range(3):
        zz = rnd.uniform(z0 + 0.3, z1 - 0.3)
        a, b = P(X, top - 0.6, zz), P(X, top - 1.4, zz)
        out.append(taper([a, b], min(8, 0.06 * P.F / zm), 0.5, dk(pal[1], 0.15), 0.25))
    return "".join(out)


def bougainvillea(D, pts, seed, n=70, pal=("#FF8AC8", "#E0308A", "#8A1050")):
    rnd = random.Random(seed)
    path = catmull(pts, 6)
    out = [pline(pts, "#5A3A22", 2.2, seed, 0.9, 1)]
    for _ in range(n):
        x, y = rnd.choice(path)
        x += rnd.uniform(-14, 14)
        y += rnd.uniform(-10, 14)
        if rnd.random() < 0.3:
            out.append(f'<path d="{blob(x, y, 5, 3, rnd.randint(0, 999), 0.2, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#3E7A2E", "#5A9A3A"])}"/>')
        else:
            c = rnd.choice(pal)
            out.append(f'<path d="{blob(x, y, rnd.uniform(3.5, 6), rnd.uniform(3, 5), rnd.randint(0, 999), 0.25, 8)}" fill="{c}"/>')
    return "".join(out)


def sitting_cat(D, cx, base, s, seed, coat=("#F2B060", "#C87A2E", "#7A4214"), flip=1):
    """A street cat of Old San Juan sitting on a step, seen from behind three-quarter, tail curled."""
    out = [cast(D, cx, base, 26 * s, 5 * s, strength=0.4, seed=seed)]
    body = [(cx - 16 * s, base), (cx - 18 * s, base - 18 * s), (cx - 10 * s, base - 34 * s), (cx + 4 * s, base - 38 * s), (cx + 14 * s, base - 26 * s), (cx + 16 * s, base)]
    out.append(painted(D, body, coat, seed, sdir=(0.7, 0.5), sk=0.18, angle=-80, n=10, inkw=1.2, hi=0.4))
    hx, hy = cx + 1 * s * flip, base - 44 * s
    head = blob_pts(hx, hy, 11 * s, 10 * s, seed + 1, 0.05, 12)
    out.append(painted(D, head, coat, seed + 1, sdir=(0.6, 0.6), sk=0.18, n=6, inkw=1.2, hi=0.4))
    for sg in (-1, 1):
        ear = [(hx + sg * 3 * s, hy - 8 * s), (hx + sg * 9 * s, hy - 19 * s), (hx + sg * 11 * s, hy - 5 * s)]
        out.append(painted(D, ear, coat, seed + 2 + sg, sk=0.2, n=2, inkw=1.0, hi=0.3))
    for k in range(3):
        out.append(pline([(cx - 12 * s, base - (10 + k * 9) * s), (cx, base - (12 + k * 9) * s), (cx + 12 * s, base - (9 + k * 9) * s)], coat[2], 1.6 * s, seed + 5 + k, 0.45, 1))
    out.append(taper([(cx + 14 * s, base - 2 * s), (cx + 26 * s, base - 4 * s), (cx + 30 * s, base - 14 * s), (cx + 26 * s, base - 22 * s)], 5 * s, 2.5 * s, coat[1]))
    return "".join(out)


@design("viejo-san-juan")
def viejo_san_juan():
    D = Doc2("prsj")
    P = Persp(300, 3.2, 300, 318)
    out = [sky(D, [(0, "#6AAAE0"), (0.55, "#B8DCF2"), (1, "#FCE8CC")], 701, 318, ["#FFFFFF", "#A8D0F0", "#FCE8D0"], 60)]
    out.append(puff_cloud(D, 132, 248, 120, 702, pal=("#FFFFFF", "#FFF4EC", "#E8C8D0")))
    out.append(puff_cloud(D, 470, 230, 100, 703, pal=("#FFFFFF", "#FFF4EC", "#E8C8D0")))
    # the bay at the end of the street, the far shore and a sail
    out.append(sea(D, 316, 420, [(0, "#2E8AB8"), (1, "#1FA5B0")], 704, ["#7AD0E0", "#1E6A9A", "#FFFFFF"], 50))
    out.append(f'<path d="M 180 318 Q 260 308 330 314 L 330 320 L 180 320 Z" fill="#6A9A8A" opacity="0.7"/>')
    out.append(f'<path d="M 318 316 l 7 -18 l 3 18 Z" fill="#FFFFFF"/><path d="M 312 318 l 20 0 l -3 3 l -14 0 Z" fill="#3A4A6A"/>')
    # street: sidewalks, then adoquines brick by brick
    zs, ze = 2.4, 11.8
    for side in (-1, 1):
        sw = P.pts([(side * 2.75, yg(zs) + 0.15, zs), (side * 3.4, yg(zs) + 0.15, zs), (side * 3.4, yg(ze) + 0.15, ze), (side * 2.75, yg(ze) + 0.15, ze)])
        out.append(f'<path d="{pd(sw)}" fill="#C8C0B8"/>')
        cb = P.pts([(side * 2.75, yg(zs), zs), (side * 2.75, yg(zs) + 0.15, zs), (side * 2.75, yg(ze) + 0.15, ze), (side * 2.75, yg(ze), ze)])
        out.append(f'<path d="{pd(cb)}" fill="#8A8480"/>')
        for k in range(int((ze - zs) / 0.6)):
            z = zs + k * 0.6
            out.append(pline(P.pts([(side * 2.75, yg(z) + 0.15, z), (side * 3.4, yg(z) + 0.15, z)]), "#9A928A", 1.0, 705 + k, 0.6, 1))
    road = P.pts([(-2.75, yg(zs), zs), (2.75, yg(zs), zs), (2.75, yg(ze), ze), (-2.75, yg(ze), ze)])
    out.append(f'<path d="{pd(road)}" fill="#3A4E6A"/>')
    rnd = random.Random(706)
    bricks = []
    z = zs
    row = 0
    while z < ze:
        dz = 0.2 * (1 + (z - zs) * 0.02)
        off = 0.22 if row % 2 else 0
        x = -2.75 - off
        while x < 2.75:
            xa, xb = max(-2.75, x + 0.025), min(2.75, x + 0.44 - 0.025)
            if xb - xa > 0.05:
                q = P.pts([(xa, yg(z + 0.02), z + 0.02), (xb, yg(z + 0.02), z + 0.02), (xb, yg(z + dz - 0.02), z + dz - 0.02), (xa, yg(z + dz - 0.02), z + dz - 0.02)])
                c = rnd.choice(["#5A7AA2", "#4E6E96", "#6A8AB2", "#46648A", "#7898BE", "#587898"])
                bricks.append(f'<path d="{pd(q)}" fill="{c}"/>')
                if rnd.random() < 0.35 and z < 7:
                    (x0, y0_), (x1, y1_) = q[3], q[2]
                    bricks.append(f'<path d="M {x0 + (x1 - x0) * 0.2:.1f} {y0_ + 1:.1f} L {x0 + (x1 - x0) * 0.75:.1f} {y1_ + 1:.1f}" stroke="#C8E0F8" stroke-width="{max(0.8, 6 / z):.1f}" opacity="0.6" stroke-linecap="round"/>')
            x += 0.44
        z += dz
        row += 1
    out.append("".join(bricks))
    out.append(f'<path d="{pd(road)}" fill="{D.lin([(0, "#FCE8CC", 0.55), (0.35, "#FCE8CC", 0.0), (1, "#000000", 0.15)], 0, 0, 0, 1)}"/>')
    # sea wall at the end of the street
    out.append(f'<path d="{pd(P.pts([(-3.5, yg(ze), ze), (3.5, yg(ze), ze), (3.5, yg(ze) + 1.0, ze), (-3.5, yg(ze) + 1.0, ze)]))}" fill="#E8D8B8"/>')
    out.append(pline(P.pts([(-3.5, yg(ze) + 1.0, ze), (3.5, yg(ze) + 1.0, ze)]), "#8A7A5A", 1.4, 707, 0.7, 1))
    # the two street walls, far to near
    left = [(9.2, 11.8, 6.6, 0, ["#2E7A5A"]), (6.9, 9.2, 6.0, 1, ["#2F6CC6"]), (4.4, 6.9, 6.8, 2, ["#8A3A1E", "#2E7A5A"]), (1.5, 4.4, 6.4, 3, ["#2F6CC6"])]
    right = [(9.0, 11.8, 6.2, 4, ["#7A3A5A"]), (6.6, 9.0, 6.8, 5, ["#2E7A5A"]), (4.0, 6.6, 6.2, 1, ["#3A5AA8", "#2E7A5A"]), (1.5, 4.0, 6.8, 0, ["#2E6A4A"])]
    walls = [(-1, *a) for a in left] + [(1, *a) for a in right]
    walls.sort(key=lambda w: -w[1])
    for side, z0, z1, H, pk, sh in walls:
        out.append(sj_facade(D, P, side, z0, z1, H, PASTELS[pk], 710 + int(z0 * 10) + side, sh, n=2 if z1 - z0 > 2.2 else 1, balcony=z0 > 3))
    # a lantern on the left wall and bougainvillea spilling over the right roof
    lx, ly = P(-3.3, yg(5.0) + 3.1, 5.0)
    out.append(pline([(lx, ly), (lx + 16, ly + 4)], "#1A1A22", 2.4, 760, 1, 1))
    out.append(f'<path d="M {lx + 10} {ly + 4} l 12 0 l -2 18 l -8 0 Z" fill="#2A2A32"/><path d="M {lx + 12} {ly + 7} l 8 0 l -1.6 12 l -4.8 0 Z" fill="#FFE8A0"/>')
    out.append(bougainvillea(D, [(612, 150), (560, 168), (540, 210), (552, 258), (540, 300)], 761, 90))
    # a street cat on the right sidewalk, pigeons on the stones
    out.append(sitting_cat(D, 498, 556, 1.1, 762))
    for k, (x, z) in enumerate(((-0.9, 3.9), (-0.3, 4.3), (0.7, 5.0))):
        px, py = P(x, yg(z), z)
        sc = 6.0 / z
        out.append(f'<path d="{blob(px, py - 6 * sc, 9 * sc, 5 * sc, 770 + k, 0.1, 10, -10)}" fill="#8A8A9A"/>' + disc(px - 8 * sc, py - 10 * sc, 3.6 * sc, "#6A6A7A") +
                   f'<path d="M {px - 11 * sc:.1f} {py - 10 * sc:.1f} l {-3 * sc:.1f} {1 * sc:.1f}" stroke="#E8A040" stroke-width="{max(1, 1.4 * sc):.1f}"/>')
    # lettering in the sky
    out.append(letters(D, 300, 120, "Viejo San Juan", SERIF_IT, 84, "#1E3E7A", ["#3A5EA0", "#122A5A", "#5A7EC0"], 780, max_w=440,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#C8DCF6"))
    out.append(ruled(300, 160, "ADOQUINES AZULES", "#7A2E4A", font=JOS, size=19, ls=7, line_w=30, gap=12))
    return finish_b(D, out, 781)


# ================================================================ 8. el morro — a garita at sunset, kites over the esplanade
def kite(D, cx, cy, s, ang, seed, cols, tail_to=None):
    """Chiringa: a diamond paper kite with a cross spar, a bowed tail of little bows and its string."""
    pts = rot([(cx, cy - s), (cx + s * 0.62, cy - s * 0.15), (cx, cy + s * 0.9), (cx - s * 0.62, cy - s * 0.15)], cx, cy, ang)
    out = []
    if tail_to:
        out.append(pline([pts[2], ((pts[2][0] + tail_to[0]) / 2 + 30, (pts[2][1] + tail_to[1]) / 2), tail_to], "#3A2A3A", 1.1, seed, 0.5, 1))
    quads = [[pts[0], pts[1], (cx, cy)], [pts[1], pts[2], (cx, cy)], [pts[2], pts[3], (cx, cy)], [pts[3], pts[0], (cx, cy)]]
    for k, q in enumerate(quads):
        out.append(f'<path d="{pd(q)}" fill="{cols[k % len(cols)]}"/>')
    out.append(pline([pts[0], pts[2]], "#5A3A2A", 1.4, seed + 1, 0.8, 1) + pline([pts[1], pts[3]], "#5A3A2A", 1.4, seed + 2, 0.8, 1))
    out.append(ink(pd(pts), INK, 1.4, seed + 3, 1, 0.7))
    tail = [pts[2]]
    rnd = random.Random(seed)
    for k in range(1, 7):
        tail.append((pts[2][0] + math.sin(k * 1.1) * 10 - k * 3, pts[2][1] + k * s * 0.28))
    out.append(pline(tail, "#5A3A2A", 1.2, seed + 4, 0.8, 1))
    for k, (x, y) in enumerate(tail[1:]):
        c = cols[k % len(cols)]
        out.append(f'<path d="M {x - 5:.1f} {y - 3:.1f} L {x + 5:.1f} {y + 3:.1f} L {x + 5:.1f} {y - 3:.1f} L {x - 5:.1f} {y + 3:.1f} Z" fill="{c}"/>')
    return "".join(out)


def garita(D, cx, base, top, r, seed, stone=("#F6CE96", "#D29A62", "#8A5A3A"), shade="#6A4A7A"):
    """Spanish colonial sentry box: corbelled cone under it, cylindrical body with slit windows, moulded rings,
    a dome and a finial; sunlit from the left, violet shade on the right."""
    out = []
    # corbel cone hanging below the wall top
    cone = [(cx - r * 1.06, base), (cx - r * 0.7, base + r * 0.55), (cx - r * 0.25, base + r * 1.05), (cx, base + r * 1.2), (cx + r * 0.25, base + r * 1.05),
            (cx + r * 0.7, base + r * 0.55), (cx + r * 1.06, base)]
    out.append(painted(D, cone, stone, seed, sdir=(1, 0.3), sk=0.25, angle=-60, n=20, inkw=1.6, hi=0.4))
    for k in range(1, 4):
        t = k / 4
        out.append(pline([(cx - r * 1.06 * (1 - t * 0.9), base + r * 1.2 * t * 0.85), (cx, base + r * 1.2 * t + 4), (cx + r * 1.06 * (1 - t * 0.9), base + r * 1.2 * t * 0.85)],
                         stone[2], 1.4, seed + k, 0.5, 1))
    # body
    body = [(cx - r, top), (cx - r, base), (cx - r * 0.5, base + r * 0.12), (cx + r * 0.5, base + r * 0.12), (cx + r, base), (cx + r, top)]
    out.append(painted(D, rect_pts(cx - r, top, cx + r, base, 14, seed + 5, 0.4), stone, seed + 5, sdir=(1, 0), sk=0.1, angle=-88, n=50, inkw=1.8, hi=0.3))
    bd = pd(rect_pts(cx - r, top, cx + r, base, 14, seed + 5, 0.4))
    cid = D.clip(f'<path d="{bd}"/>')
    g = D.lin([(0, "#FFF0C8", 0.5), (0.35, "#FFFFFF", 0), (0.62, shade, 0.2), (1, shade, 0.62)], 0, 0, 1, 0)
    inner = [f'<rect x="{cx - r:.1f}" y="{top:.1f}" width="{2 * r:.1f}" height="{base - top:.1f}" fill="{g}"/>']
    rnd = random.Random(seed)
    for k in range(1, int((base - top) / 16)):
        y = top + k * 16
        inner.append(pline([(cx - r, y - 3), (cx, y + 3), (cx + r, y - 3)], stone[2], 1.1, seed + 10 + k, 0.35, 1))
    for _ in range(14):
        x = rnd.uniform(cx - r, cx + r)
        y = rnd.uniform(top, base - 30)
        inner.append(taper([(x, y), (x + rnd.uniform(-2, 2), y + rnd.uniform(16, 40))], rnd.uniform(2, 4), 0.6, "#5A4A3A", 0.18))
    inner.append(specks(seed + 30, (cx - r, top, cx + r, base), ["#8A9A6A", "#5A4A3A", "#FFF0D0"], 50, (0.8, 2), (0.2, 0.5)))
    # slit windows: one facing us, one turning away on the right
    for (sx, w, op) in ((cx - r * 0.12, 13, 1), (cx + r * 0.72, 6, 0.85)):
        sl = [(sx - w / 2, top + 30), (sx - w / 2, top + 94), (sx + w / 2, top + 94), (sx + w / 2, top + 30), (sx, top + 24)]
        inner.append(f'<path d="{smooth_closed(sl)}" fill="#2A1A2A" opacity="{op}"/>')
        inner.append(pline([(sx - w / 2 - 1, top + 30), (sx - w / 2 - 1, top + 94)], "#FFE8C0", 1.6, seed + 40, 0.6 * op, 1))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # moulded rings
    for y, rr, h in ((base - 4, r * 1.1, 12), (top + 2, r * 1.14, 14)):
        ring = rect_pts(cx - rr, y - h / 2, cx + rr, y + h / 2, 10, seed + int(y), 0.3)
        out.append(painted(D, ring, (lt(stone[0], 0.2), stone[0], stone[2]), seed + int(y), sdir=(1, 0.4), sk=0.15, angle=0, n=8, inkw=1.4, hi=0.5))
        out.append(f'<path d="{pd(ring)}" fill="{D.lin([(0, "#FFFFFF", 0.2), (0.4, "#FFFFFF", 0), (1, shade, 0.55)], 0, 0, 1, 0)}"/>')
    # dome
    dh = r * 1.05
    dome = [(cx - r * 1.02, top - 5)] + [(cx - r * 1.02 * math.cos(math.radians(a)), top - 5 - dh * math.sin(math.radians(a)) ** 0.9) for a in range(12, 170, 12)] + [(cx + r * 1.02, top - 5)]
    out.append(painted(D, dome, stone, seed + 50, sdir=(1, 0.2), sk=0.16, angle=-60, n=24, inkw=1.8, hi=0.5, hik=0.12))
    dd = smooth_closed(dome)
    out.append(f'<path d="{dd}" fill="{D.lin([(0, "#FFF4D8", 0.4), (0.4, "#FFFFFF", 0), (1, shade, 0.6)], 0, 0, 1, 0)}"/>')
    for k in range(-3, 4):
        out.append(pline([(cx + k * r * 0.26, top - 6), (cx + k * r * 0.18, top - dh * 0.55), (cx + k * r * 0.05, top - dh * 0.95)], stone[2], 1.1, seed + 60 + k, 0.35, 1))
    # finial
    fy = top - 5 - dh
    out.append(painted(D, rect_pts(cx - 7, fy - 8, cx + 7, fy + 2, 6, seed + 70, 0.3), stone, seed + 70, sk=0.2, n=3, inkw=1.2, hi=0.4))
    out.append(painted(D, blob_pts(cx, fy - 16, 8, 8, seed + 71, 0.03, 10), stone, seed + 71, sdir=(1, 0.3), sk=0.25, n=4, inkw=1.2, hi=0.5))
    out.append(taper([(cx, fy - 22), (cx, fy - 36)], 4, 1, stone[2]))
    return "".join(out)


@design("el-morro")
def el_morro():
    D = Doc2("prmr")
    hy = 376
    out = [sky(D, [(0, "#3E3C82"), (0.35, "#9A5A9A"), (0.62, "#E87A7A"), (0.85, "#F8A85A"), (1, "#FFD07A")], 801, hy, ["#FFB0A0", "#7A5AA0", "#FFD8A0"], 70)]
    out.append(soft_glow(D, 170, hy - 20, 260, "#FFE0A0", 0.7))
    # long streaky sunset clouds
    rnd = random.Random(802)
    for k, (x, y, w) in enumerate(((120, 250, 180), (420, 220, 220), (300, 296, 260), (520, 316, 140), (70, 330, 120))):
        cl = blob(x, y, w / 2, 7 + k % 2 * 3, 803 + k, 0.15, 16)
        out.append(f'<path d="{cl}" fill="#C86A8A" opacity="0.55"/><path d="{blob(x - 8, y - 3, w / 2 * 0.85, 4, 810 + k, 0.15, 14)}" fill="#FFC8A0" opacity="0.8"/>')
    out.append(D.glow(170, hy - 22, 46, "#FFF6C8", 0.9))
    out.append(disc(170, hy - 22, 30, "#FFF2C0"))
    # sea with the sun's path
    out.append(sea(D, hy, 600, [(0, "#C86A7A"), (0.25, "#6A5A9A"), (1, "#2A3A7A")], 820, ["#FFB08A", "#3A3A7A", "#8A6AA8"], 70))
    for k in range(26):
        y = hy + 4 + k * k * 0.35
        w = 14 + k * 3.2
        out.append(taper([(170 - w / 2 + rnd.uniform(-8, 8), y), (170 + w / 2 + rnd.uniform(-8, 8), y)], 2.4, 1.2, rnd.choice(["#FFE0A0", "#FFC878", "#FFF0C8"]), 0.8))
    out.append(f'<path d="M 0 {hy} L 600 {hy}" stroke="#FFE0B0" stroke-width="1.5" opacity="0.7"/>')
    # a ship far out and pelicans
    out.append(f'<path d="M 470 {hy - 2} l 46 0 l -6 6 l -36 0 Z M 486 {hy - 2} l 0 -8 l 14 0 l 0 8 Z" fill="#4A3A6A" opacity="0.8"/>')
    for x, y, s in ((300, 238, 9), (330, 252, 7), (360, 240, 8)):
        out.append(bird_v(x, y, s, "#3A2A4A", 0.85))
    # kites over the esplanade
    out.append(kite(D, 88, 214, 28, -14, 830, ["#F6C21C", "#D52B1E", "#2F6CC6", "#FFFFFF"], tail_to=(0, 470)))
    out.append(kite(D, 236, 252, 22, 10, 831, ["#1FB5B2", "#F26A8A"], tail_to=(120, 480)))
    out.append(kite(D, 540, 210, 20, 12, 832, ["#D52B1E", "#FFFFFF"], tail_to=(610, 470)))
    # the fortress wall: sloped sandstone with the rounded cordón along its top
    wall_top = [(-10, 486), (300, 466), (610, 452)]
    wall = wall_top + [(610, 610), (-10, 610)]
    out.append(painted(D, wall, ("#F2C890", "#C8915A", "#7A4E2E"), 840, sdir=(0.6, 1), sk=0.04, angle=-6, n=90, slen=(20, 60), sw=(2, 5), inkw=1.6, hi=0.2))
    wd = smooth_closed(wall)
    cid = D.clip(f'<path d="{wd}"/>')
    blocks = [f'<path d="{wd}" fill="{D.lin([(0, "#FFE0B0", 0.3), (0.5, "#FFFFFF", 0), (1, "#5A3A6A", 0.45)], 0, 0, 1, 0.3)}"/>']
    for k in range(1, 9):
        y0 = 486 + k * 16
        blocks.append(pline([(-10, y0), (610, y0 - 34 + k * 0.5)], "#8A5A3A", 1.2, 841 + k, 0.4, 1))
        for j in range(12):
            x = j * 56 + (28 if k % 2 else 0) + rnd.uniform(-4, 4)
            y = y0 - x * 34 / 620
            blocks.append(pline([(x, y), (x + 1, y + 16)], "#8A5A3A", 1.0, 850 + k * 12 + j, 0.35, 1))
    blocks.append(specks(860, (0, 450, 600, 600), ["#5A4A3A", "#FFF0D0", "#8A9A6A"], 120, (0.8, 2.2), (0.2, 0.5)))
    out.append(f'<g {cid}>{"".join(blocks)}</g>')
    out.append(taper([(-10, 484), (300, 464), (610, 450)], 12, 12, "#E8B880"))
    out.append(taper([(-10, 480), (300, 460), (610, 446)], 4, 4, "#FFE6B8", 0.8))
    out.append(pline([(-10, 491), (300, 471), (610, 457)], "#7A4E2E", 1.6, 861, 0.6, 1))
    # the garita on the corner
    out.append(garita(D, 402, 462, 322, 56, 862))
    # lettering
    out.append(letters(D, 300, 126, "El Morro", SERIF_IT, 112, "#FFF0D8", ["#FFFFFF", "#FFD8B8", "#F8E8D0"], 870, max_w=420,
                       shadow="#2A2050", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 168, "CHIRINGAS AL ATARDECER", "#FFE6C0", font=JOS, size=18, ls=5, line_w=26, gap=12))
    return finish_b(D, out, 871, "#FFFFFF", 0.45)


# ================================================================ 9. pa'lante — the ruta panorámica at sunrise
def road_ribbon(center, w0, w1):
    """Polygon around a centre polyline whose width goes from w0 (start) to w1 (end)."""
    n = len(center)
    left, right = [], []
    for i, (x, y) in enumerate(center):
        a, b = center[max(0, i - 1)], center[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = (w0 + (w1 - w0) * (i / (n - 1)) ** 0.7) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left, right


def bamboo(D, x, base, h, lean, seed, cols=("#C8D86A", "#8AAA3A", "#4E6E1E")):
    """A clump stalk of bamboo arching over: segmented culm with nodes, and drooping leaf sprays."""
    rnd = random.Random(seed)
    pts = []
    for i in range(16):
        t = i / 15
        pts.append((x + lean * h * t * t, base - h * t + lean * h * 0.15 * t ** 3))
    out = [taper(pts, 11, 5, cols[1]), taper([(px - 2.4, py) for px, py in pts], 3, 1.4, cols[0], 0.8)]
    for i in range(1, 15):
        px, py = pts[i]
        out.append(pline([(px - 6 + i * 0.2, py), (px + 6 - i * 0.2, py + 1)], cols[2], 1.8, seed + i, 0.85, 1))
    for i in range(6, 16, 2):
        px, py = pts[i]
        for k in range(5):
            a = math.radians(rnd.uniform(-10, 190) if lean < 0 else rnd.uniform(-10, 190))
            L = rnd.uniform(18, 30)
            ex, ey = px + math.cos(a) * L * 0.8, py + abs(math.sin(a)) * L * 0.6 + 6
            out.append(leaf_simple(D, px, py, L, 3.6, math.degrees(math.atan2(ey - py, ex - px)), rnd.choice([("#D8E88A", "#8AB03A", "#3E6A1E"), ("#B8D86A", "#6A9A2E", "#2E5A14")]),
                                   seed + 30 + i * 5 + k, vein=False, inkw=0.6))
    return "".join(out)


def curve_sign(D, x, base, seed):
    """Yellow diamond road sign with a winding-road arrow, on a metal post."""
    out = [taper([(x, base), (x, base - 70)], 4, 4, "#8A8A92"), taper([(x - 1, base), (x - 1, base - 70)], 1.2, 1.2, "#D8D8E0", 0.8)]
    cy = base - 92
    dmd = [(x, cy - 30), (x + 30, cy), (x, cy + 30), (x - 30, cy)]
    out.append(painted(D, dmd, ("#FFE88A", "#F6C21C", "#B8860A"), seed, sk=0.15, n=6, inkw=2, hi=0.4))
    out.append(ink(pd([(x, cy - 25), (x + 25, cy), (x, cy + 25), (x - 25, cy)]), "#1A1A1A", 2, seed + 1, 1, 0.9))
    out.append(ink(smooth_open([(x - 6, cy + 18), (x + 6, cy + 8), (x - 6, cy - 2), (x + 4, cy - 12)]), "#1A1A1A", 4, seed + 2, 1, 1))
    out.append(f'<path d="M {x + 4} {cy - 20} l 6 9 l -11 1 Z" fill="#1A1A1A"/>')
    return "".join(out)


@design("pa-lante")
def pa_lante():
    D = Doc2("prpl")
    out = [sky(D, [(0, "#8CBCE6"), (0.45, "#D8D8E8"), (0.75, "#FCD8B0"), (1, "#FFC07A")], 901, 330, ["#FFFFFF", "#F8D0B0", "#B8D0EC"], 60)]
    sx, sy = 400, 306
    out.append(soft_glow(D, sx, sy, 260, "#FFE8A8", 0.75))
    for k in range(14):
        a = math.radians(-180 + k * 180 / 13)
        out.append(taper([(sx + math.cos(a) * 44, sy + math.sin(a) * 44), (sx + math.cos(a) * 130, sy + math.sin(a) * 130)], 6, 0.5, "#FFF2C8", 0.45))
    out.append(disc(sx, sy, 38, "#FFF0C0"))
    out.append(puff_cloud(D, 130, 238, 110, 902, pal=("#FFFFFF", "#FFF0E8", "#E8C0C8")))
    # layered cordillera with mist between the ridges
    out.append(hill(D, ridge([(-20, 312), (90, 290), (200, 304), (330, 284), (470, 300), (620, 290)], 903, 8, 4), 600, ("#C8C0DC", "#B0A8CC", "#8A84AC"), 904, inkw=0, sop=(0.06, 0.16)))
    out.append(f'<rect y="300" width="600" height="40" fill="{D.lin([(0, "#FFF0E0", 0), (0.5, "#FFF0E0", 0.55), (1, "#FFF0E0", 0)])}"/>')
    out.append(hill(D, ridge([(-20, 346), (120, 322), (260, 342), (380, 318), (520, 336), (620, 326)], 905, 10, 4), 600, ("#9AB8C0", "#7A9EAC", "#56788A"), 906, inkw=0, sop=(0.08, 0.2)))
    out.append(f'<rect y="340" width="600" height="40" fill="{D.lin([(0, "#F8F0E8", 0), (0.5, "#F8F0E8", 0.45), (1, "#F8F0E8", 0)])}"/>')
    r3 = ridge([(-20, 392), (100, 372), (240, 386), (360, 366), (500, 384), (620, 372)], 907, 10, 4)
    out.append(hill(D, r3, 600, ("#8ABE8A", "#5E9A6E", "#3A6A4E"), 908, inkw=1, inkop=0.3))
    # a far stretch of the road on the third ridge
    far = catmull([(222, 388), (262, 382), (300, 380), (332, 376)], 4)
    fl, fr = road_ribbon(far, 7, 4)
    out.append(f'<path d="{smooth_closed(fl + fr[::-1])}" fill="#8A8494" opacity="0.8"/>')
    out.append(f'<rect y="380" width="600" height="50" fill="{D.lin([(0, "#F4F0E8", 0), (0.5, "#F4F0E8", 0.35), (1, "#F4F0E8", 0)])}"/>')
    # near hillside
    r4 = ridge([(-20, 452), (140, 426), (300, 446), (430, 420), (620, 440)], 909, 8, 4)
    out.append(hill(D, r4, 640, ("#9ACB6A", "#5E9A3A", "#2E6A22"), 910, inkw=1.4, inkop=0.4))
    out.append(grass(911, (0, 440, 600, 600), ["#4E8A2E", "#7AB04A", "#3A6A22", "#A8D06A"], 200, (8, 18), 1.4))
    # the road winding up and over the crest
    ctr = catmull([(200, 650), (300, 560), (420, 506), (474, 476), (440, 456), (370, 444), (322, 436)], 10)
    n = len(ctr)
    widths = [300 * (1 - i / (n - 1)) ** 1.8 + 14 for i in range(n)]
    L, R, ML, MR = [], [], [], []
    for i, (x, y) in enumerate(ctr):
        a, b = ctr[max(0, i - 1)], ctr[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ll = math.hypot(dx, dy) or 1
        nx, ny = -dy / ll, dx / ll
        w = widths[i] / 2
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
        ML.append((x + nx * w * 0.05, y + ny * w * 0.05))
        MR.append((x - nx * w * 0.05, y - ny * w * 0.05))
    road = L + R[::-1]
    out.append(painted(D, road, ("#9A94A6", "#77718A", "#4E4A5E"), 912, sdir=(1, 0.3), sk=0.05, angle=-20, n=60, inkw=1.4, inkop=0.5, hi=0.2))
    for line in (ML, MR):
        for k in range(len(line) - 1):
            w = max(0.8, widths[k] * 0.022)
            out.append(taper([line[k], line[k + 1]], w, w, "#F6D24A", 0.95))
    for k, edge in enumerate((L, R)):
        inner = [(x + (cx_ - x) * 0.06, y + (cy_ - y) * 0.06) for (x, y), (cx_, cy_) in zip(edge, ctr)]
        out.append(pline(inner, "#FFFFFF", 2.2, 913 + k, 0.75, 1))
    # wildflowers on the verge, the curve sign, bamboo arching from the left
    rnd = random.Random(915)
    for _ in range(40):
        x, y = rnd.uniform(0, 600), rnd.uniform(470, 600)
        out.append(disc(x, y, rnd.uniform(2, 3.4), rnd.choice(["#FFFFFF", "#F6D24A", "#F28AB0", "#E8401E"]), 0.95))
    out.append(curve_sign(D, 532, 560, 916))
    for k, (x, h, lean) in enumerate(((10, 400, 0.32), (36, 360, 0.42), (62, 300, 0.5), (-10, 330, 0.2))):
        out.append(bamboo(D, x, 620, h, lean, 920 + k))
    # lettering
    out.append(letters(D, 304, 126, "Pa’lante", SERIF_IT, 124, "#1E4E8A", ["#3A6EB0", "#123A6E", "#5A8AC8"], 930, max_w=420,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#D8E8F8"))
    out.append(ruled(300, 170, "¡Y NO PA’TRÁS!", "#B8361E", font=JOS, size=20, ls=6, line_w=36, gap=14))
    return finish_b(D, out, 931)


# ================================================================ 10. pasteles — tied in pairs, Christmas table, top-down
def pastel_wrapped(D, cx, cy, w, h, ang, seed):
    """A pastel wrapped in banana leaf: a pillow of glossy green leaf, folded ends, leaf ribs."""
    pts = rot(rect_pts(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 12, seed, 1.2), cx, cy, ang)
    out = [cast(D, cx + 8, cy + 10, w * 0.58, h * 0.6, "#2A1A0A", 0.4, seed)]
    out.append(painted(D, pts, ("#7AB86A", "#3E7A3A", "#1A4A1E"), seed, sdir=(0.6, 0.8), sk=0.14, angle=ang, n=40, slen=(w * 0.15, w * 0.5), sw=(1, 3),
                       cols=["#9ACB7A", "#2E6A2A", "#5A9A4A", "#C8E0A0"], inkw=1.8, hi=0.45, hik=0.08))
    for k in range(1, 9):
        t = k / 9
        a = rot([(cx - w / 2 + 4, cy - h / 2 + h * t)], cx, cy, ang)[0]
        b = rot([(cx + w / 2 - 4, cy - h / 2 + h * t)], cx, cy, ang)[0]
        out.append(pline([a, b], "#C8E8A8", 1.0, seed + k, 0.4, 1))
    for sg in (-1, 1):
        fold = rot([(cx + sg * w * 0.5, cy - h * 0.5), (cx + sg * w * 0.34, cy - h * 0.1), (cx + sg * w * 0.34, cy + h * 0.1), (cx + sg * w * 0.5, cy + h * 0.5)], cx, cy, ang)
        out.append(pline(fold, "#1A4A1E", 1.6, seed + 20 + sg, 0.6, 1))
    return "".join(out)


def string_tie(D, cx, cy, w, h, ang, seed, col="#FFFDF4"):
    """Kitchen string tied around a parcel lengthwise and crosswise, with a knot and a loose end."""
    out = []
    for p in ([(cx - w / 2 - 2, cy), (cx + w / 2 + 2, cy)], [(cx, cy - h / 2 - 2), (cx, cy + h / 2 + 2)]):
        q = rot(p, cx, cy, ang)
        out.append(pline(q, "#8A7A5A", 4, seed, 0.5, 1) + pline(q, col, 2.4, seed + 1, 1, 1))
    k = rot([(cx, cy)], cx, cy, ang)[0]
    out.append(disc(k[0], k[1], 5, col) + ink(blob(k[0], k[1], 5, 5, seed, 0.1, 8), "#8A7A5A", 1, seed, 1, 0.7))
    for sg in (-1, 1):
        out.append(pline([k, (k[0] + 14 * sg, k[1] - 16), (k[0] + 22 * sg, k[1] - 8)], col, 2.2, seed + 3 + sg, 1, 1))
    return "".join(out)


def poinsettia(D, cx, cy, r, seed, rot_=0):
    rnd = random.Random(seed)
    out = []
    for k in range(7):
        a = rot_ + k * 360 / 7 + rnd.uniform(-8, 8)
        out.append(leaf_simple(D, cx, cy, r * 1.25, r * 0.3, a + 20, ("#7AB86A", "#2E6A2A", "#143A14"), seed + 20 + k, vein=True, inkw=1))
    for k in range(7):
        a = rot_ + k * 360 / 7 + rnd.uniform(-6, 6)
        out.append(leaf_simple(D, cx, cy, r, r * 0.3, a, ("#FF7A6A", "#D8242A", "#7A0A10"), seed + k, vein=True, inkw=1.1))
    for k in range(5):
        a = rot_ + 36 + k * 72
        out.append(leaf_simple(D, cx, cy, r * 0.6, r * 0.2, a, ("#FF8A7A", "#E8302A", "#8A1414"), seed + 10 + k, vein=False, inkw=1))
    for k in range(6):
        a = math.radians(k * 60)
        out.append(disc(cx + math.cos(a) * 4, cy + math.sin(a) * 4, 2.6, "#F6D24A") + disc(cx + math.cos(a) * 4, cy + math.sin(a) * 4, 1, "#3E8A2A"))
    return "".join(out)


@design("pasteles")
def pasteles():
    D = Doc2("prps")
    out = [wood_planks(D, 0, 600, 1001, ("#C89060", "#946036", "#4E2C14"), 6)]
    out.append(soft_glow(D, 260, 360, 360, "#FFE6B0", 0.35))
    # banana leaves laid across the table
    out.append(banana_leaf(D, 640, 150, 160, 520, 120, 1002, pal=("#6AA85A", "#2E6A32", "#123E1A")))
    out.append(banana_leaf(D, -40, 600, -32, 700, 150, 1003, pal=("#86C46E", "#3E8A44", "#164A22")))
    # the yunta: two pasteles tied together
    out.append(pastel_wrapped(D, 452, 300, 170, 96, 24, 1010))
    out.append(pastel_wrapped(D, 476, 360, 170, 96, 18, 1011))
    out.append(string_tie(D, 466, 334, 186, 160, 21, 1012))
    # the plate with one pastel opened
    pcx, pcy, pr_ = 236, 418, 142
    out.append(cast(D, pcx + 12, pcy + 16, pr_ + 6, pr_, "#1A0A04", 0.45, 1020))
    out.append(painted(D, blob_pts(pcx, pcy, pr_, pr_, 1021, 0.01, 30), ("#FFFFFF", "#F6F2EA", "#C8C0B0"), 1021, sk=0.06, n=30, inkw=2, hi=0.4))
    out.append(ink(blob(pcx, pcy, pr_ - 22, pr_ - 22, 1022, 0.01, 30), "#C8BEB0", 1.4, 1022, 1, 0.7))
    for i in range(36):
        a = 2 * math.pi * i / 36
        out.append(disc(pcx + math.cos(a) * (pr_ - 10), pcy + math.sin(a) * (pr_ - 10), 2.6, "#2F6CC6", 0.8))
    leaf = rot(rect_pts(pcx - 104, pcy - 66, pcx + 104, pcy + 66, 12, 1023, 2.4), pcx, pcy, -8)
    out.append(painted(D, leaf, ("#5E9A4E", "#2E6A2E", "#143E14"), 1023, sk=0.12, angle=-8, n=40, cols=["#7AB86A", "#1E4A1E", "#4A8A3A"], inkw=1.6, hi=0.35))
    for k in range(1, 12):
        a = rot([(pcx - 100, pcy - 66 + k * 11)], pcx, pcy, -8)[0]
        b = rot([(pcx + 100, pcy - 66 + k * 11)], pcx, pcy, -8)[0]
        out.append(pline([a, b], "#9AC88A", 0.9, 1024 + k, 0.35, 1))
    # masa, with a forkful already taken from the right end so the filling shows at the cut
    R_ = lambda pts: rot(pts, pcx, pcy, -8)
    masa = R_([(pcx - 76, pcy - 36), (pcx - 70, pcy - 44), (pcx + 30, pcy - 44), (pcx + 40, pcy - 40), (pcx + 26, pcy - 14), (pcx + 34, pcy + 14),
               (pcx + 52, pcy + 40), (pcx + 44, pcy + 44), (pcx - 70, pcy + 44), (pcx - 76, pcy + 36)])
    out.append(painted(D, masa, ("#FFD08A", "#E89A4A", "#A85A1E"), 1030, sdir=(0.5, 0.9), sk=0.1, angle=-8, n=40, slen=(10, 30), sw=(1, 3),
                       cols=["#FFE0A8", "#D8823A", "#F2B068"], inkw=1.6, hi=0.5))
    cut = R_([(pcx + 40, pcy - 40), (pcx + 26, pcy - 14), (pcx + 34, pcy + 14), (pcx + 52, pcy + 40)])
    out.append(taper(cut, 16, 14, "#C86A2A", 0.9))
    rnd = random.Random(1031)
    for k in range(7):
        t = (k + 0.5) / 7
        i = min(2, int(t * 3))
        a, b = cut[i], cut[i + 1]
        f = t * 3 - i
        x, y = a[0] + (b[0] - a[0]) * f - 4, a[1] + (b[1] - a[1]) * f
        if k in (2, 5):
            out.append(disc(x, y, 5.5, "#F2D89A") + disc(x - 1.6, y - 1.6, 1.6, "#FFFFFF", 0.6))
        elif k == 3:
            out.append(disc(x, y, 5.5, "#7A8A2A") + disc(x, y, 2.2, "#D8302A"))
        else:
            out.append(painted(D, blob_pts(x, y, rnd.uniform(6, 8), rnd.uniform(4, 6), 1032 + k, 0.2, 8), ("#D8784A", "#A8482A", "#5A1A0A"), 1032 + k, sk=0.25, n=3, inkw=0.8, hi=0.5))
    for k in range(5):
        x, y = R_([(pcx + rnd.uniform(-64, 10), pcy + rnd.uniform(-30, 30))])[0]
        out.append(f'<path d="{blob(x, y, rnd.uniform(6, 12), rnd.uniform(3, 5), rnd.randint(0, 999), 0.2, 8, -8)}" fill="#FFE6B0" opacity="0.35"/>')
    out.append(taper(R_([(pcx - 64, pcy - 38), (pcx - 10, pcy - 40)]), 3, 1, "#FFF2D0", 0.8))
    # a fork resting on the plate
    fx0, fy0 = pcx + 60, pcy + 96
    fork = [(fx0, fy0), (fx0 + 120, fy0 + 40)]
    out.append(taper(fork, 9, 7, "#C8CCD4") + taper([(fx0 + 4, fy0 - 2), (fx0 + 120, fy0 + 37)], 2.4, 2, "#FFFFFF", 0.8))
    for k in range(4):
        out.append(taper([(fx0 - 4, fy0 - 4 + k * 3), (fx0 - 36, fy0 - 16 + k * 4)], 2.6, 2, "#B8BCC4"))
    out.append(painted(D, blob_pts(fx0 - 24, fy0 - 8, 16, 11, 1039, 0.12, 10), ("#FFD08A", "#E89A4A", "#A85A1E"), 1039, sk=0.2, n=6, inkw=1.2, hi=0.5))
    out.append(painted(D, blob_pts(fx0 - 22, fy0 - 10, 6, 4, 1038, 0.2, 8), ("#D8784A", "#A8482A", "#5A1A0A"), 1038, sk=0.25, n=2, inkw=0.8, hi=0.5))
    # a little bowl of pique with its peppers
    bx, by = 506, 520
    out.append(cast(D, bx + 6, by + 8, 50, 46, "#1A0A04", 0.4, 1040))
    out.append(painted(D, blob_pts(bx, by, 46, 46, 1041, 0.02, 20), ("#FFFFFF", "#F2EEE6", "#B8B0A6"), 1041, sk=0.1, n=10, inkw=1.6, hi=0.4))
    out.append(f'<path d="{blob(bx, by, 36, 36, 1042, 0.02, 20)}" fill="#E8A040" opacity="0.85"/>')
    for k, (dx, dy, a, c) in enumerate(((-12, -8, 30, "#D8302A"), (10, 4, -40, "#6AA83A"), (-4, 14, 80, "#F28A2A"), (14, -14, 10, "#D8302A"))):
        out.append(leaf_simple(D, bx + dx - 8, by + dy, 22, 4, a, pal_of(c), 1043 + k, vein=False, inkw=0.8))
    out.append(specks(1048, (bx - 30, by - 30, bx + 30, by + 30), ["#3E6A1E", "#F6E0A0"], 20, (1, 2), (0.6, 0.9)))
    # a poinsettia in the corner
    out.append(poinsettia(D, 72, 530, 54, 1050, 10))
    # lettering, on a parchment band so it reads over the table
    band = rect_pts(70, 70, 530, 214, 30, 1060, 1.6)
    out.append(cast(D, 306, 222, 236, 14, "#1A0A04", 0.45, 1061))
    out.append(painted(D, band, ("#FFFDF4", "#F6EEDC", "#C8B898"), 1060, sk=0.05, angle=0, n=30, inkw=1.6, hi=0.3))
    out.append(letters(D, 300, 162, "pasteles", SERIF_IT, 116, "#2E6A32", ["#3E8A44", "#1A4A1E", "#5AA05A"], 1062, max_w=400,
                       shadow="#C8B898", soff=(0.016, 0.026), angle=-40, hi="#C8E8B8"))
    out.append(ruled(300, 198, "AMARRADOS EN YUNTA", "#B8361E", font=JOS, size=18, ls=6, line_w=30, gap=12))
    return finish_b(D, out, 1064)


# ================================================================ 11. coquito — titi's bottle with a bow, two glasses
def bottle(D, cx, base, h, w, seed, liquid=("#FFF6E2", "#EEDCB8", "#B8A07A"), fill_to=0.68):
    """Clear glass bottle (no label): body, sloping shoulders, neck and a cork; creamy contents with a meniscus."""
    sh = base - h * 0.58
    nk = base - h * 0.84
    top = base - h
    nw = w * 0.2
    body = [(cx - w / 2, base - 8), (cx - w / 2, sh), (cx - w * 0.36, sh - h * 0.12), (cx - nw, nk), (cx - nw, top + 10), (cx + nw, top + 10), (cx + nw, nk),
            (cx + w * 0.36, sh - h * 0.12), (cx + w / 2, sh), (cx + w / 2, base - 8), (cx + w / 2 - 8, base), (cx - w / 2 + 8, base)]
    out = [cast(D, cx + 12, base, w * 0.75, 12, "#0A1A10", 0.5, seed)]
    bd = smooth_closed(body)
    out.append(f'<path d="{bd}" fill="#CFE6D8" opacity="0.45"/>')
    out.append(f'<path d="{bd}" fill="{D.lin([(0, "#FFFFFF", 0.35), (0.3, "#FFFFFF", 0.05), (0.8, "#0A2A1A", 0.15), (1, "#0A2A1A", 0.35)], 0, 0, 1, 0)}"/>')
    lvl = base - (base - sh) * fill_to - 30
    cid = D.clip(f'<path d="{bd}"/>')
    inner = [f'<rect x="{cx - w / 2 - 4:.1f}" y="{lvl:.1f}" width="{w + 8:.1f}" height="{base - lvl:.1f}" fill="{liquid[1]}"/>',
             f'<rect x="{cx - w / 2 - 4:.1f}" y="{lvl:.1f}" width="{w + 8:.1f}" height="{base - lvl:.1f}" fill="{D.lin([(0, liquid[0], 0.8), (0.4, liquid[0], 0), (1, liquid[2], 0.6)], 0, 0, 1, 0)}"/>',
             f'<path d="{smooth_closed(ell_pts(cx, lvl, w / 2, 6, 0, 360, 20))}" fill="{liquid[0]}"/>',
             specks(seed + 1, (cx - w / 2, lvl + 10, cx + w / 2, base), ["#B8885A", "#A07040"], 30, (0.8, 1.6), (0.3, 0.6)),
             strokes(D.nid(), bd, (cx - w / 2, lvl, cx + w / 2, base), [liquid[0], liquid[2]], seed + 2, n=30, angle=-90, length=(10, 40), width=(1, 3), opacity=(0.1, 0.3))]
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # glass highlights and edges
    out.append(taper([(cx - w * 0.36, sh + 8), (cx - w * 0.38, base - 30)], 9, 6, "#FFFFFF", 0.65))
    out.append(taper([(cx - w * 0.28, sh - 6), (cx - nw * 0.6, nk + 10)], 4, 2, "#FFFFFF", 0.6))
    out.append(taper([(cx + w * 0.4, sh + 20), (cx + w * 0.42, base - 40)], 3, 2, "#FFFFFF", 0.4))
    out.append(ink(bd, "#2E4A3A", 2.4, seed + 3, 2, 0.85))
    out.append(ink(smooth_open([(cx - w / 2 + 3, sh + 2), (cx - w * 0.36 + 2, sh - h * 0.12 + 2), (cx - nw + 2, nk + 2)]), "#FFFFFF", 2, seed + 6, 1, 0.5))
    # cork
    out.append(painted(D, rect_pts(cx - nw * 0.9, top - 10, cx + nw * 0.9, top + 14, 8, seed + 4, 0.4), ("#E8C08A", "#C08A50", "#7A5028"), seed + 4, sk=0.2, n=8, inkw=1.4, hi=0.4))
    out.append(specks(seed + 5, (cx - nw * 0.8, top - 8, cx + nw * 0.8, top + 12), ["#7A5028"], 12, (0.8, 1.4), (0.5, 0.8)))
    return "".join(out), (cx, nk + 12, nw)


def ribbon_bow(D, cx, cy, s, seed, pal=ROJO, edge="#F6C21C"):
    out = []
    for sg in (-1, 1):
        loop = [(cx, cy), (cx + sg * s * 0.9, cy - s * 0.55), (cx + sg * s * 1.15, cy - s * 0.1), (cx + sg * s * 0.95, cy + s * 0.35), (cx, cy + 2)]
        out.append(painted(D, loop, pal, seed + sg, sdir=(0.3 * sg, 1), sk=0.2, n=8, inkw=1.4, hi=0.45))
        tail = [(cx, cy + 2), (cx + sg * s * 0.35, cy + s * 0.9), (cx + sg * s * 0.55, cy + s * 1.35), (cx + sg * s * 0.3, cy + s * 1.25), (cx + sg * s * 0.05, cy + s * 0.5)]
        out.append(painted(D, tail, pal, seed + 5 + sg, sdir=(0.3 * sg, 1), sk=0.2, n=6, inkw=1.3, hi=0.4))
        out.append(pline([(cx + sg * s * 0.2, cy - s * 0.2), (cx + sg * s * 0.9, cy - s * 0.4)], edge, 1.6, seed + 9 + sg, 0.8, 1))
    out.append(painted(D, blob_pts(cx, cy, s * 0.24, s * 0.22, seed + 12, 0.05, 10), pal, seed + 12, sk=0.25, n=3, inkw=1.3, hi=0.5))
    return "".join(out)


def tumbler(D, cx, base, w, h, seed, liquid=("#FFF6E2", "#EEDCB8", "#B8A07A"), fill=0.72, stick=False):
    """Short glass (vasito) of coquito, cinnamon dusted on top."""
    out = [cast(D, cx + 8, base, w * 0.7, 8, "#0A1A10", 0.45, seed)]
    body = [(cx - w / 2, base - h), (cx - w * 0.44, base - 4), (cx - w * 0.38, base), (cx + w * 0.38, base), (cx + w * 0.44, base - 4), (cx + w / 2, base - h)]
    bd = smooth_closed(body)
    out.append(f'<path d="{bd}" fill="#E8F0E8" opacity="0.3"/>')
    lvl = base - h * fill
    cid = D.clip(f'<path d="{bd}"/>')
    out.append(f'<g {cid}><rect x="{cx - w:.1f}" y="{lvl:.1f}" width="{2 * w:.1f}" height="{h:.1f}" fill="{liquid[1]}"/>'
               f'<rect x="{cx - w:.1f}" y="{lvl:.1f}" width="{2 * w:.1f}" height="{h:.1f}" fill="{D.lin([(0, liquid[0], 0.8), (0.45, liquid[0], 0), (1, liquid[2], 0.6)], 0, 0, 1, 0)}"/>'
               f'<rect x="{cx - w:.1f}" y="{base - 10:.1f}" width="{2 * w:.1f}" height="12" fill="#C8D8D0" opacity="0.6"/></g>')
    top = smooth_closed(ell_pts(cx, lvl, w * 0.47, w * 0.1, 0, 360, 20))
    out.append(f'<path d="{top}" fill="{liquid[0]}"/>')
    out.append(specks(seed + 1, (cx - w * 0.36, lvl - w * 0.06, cx + w * 0.36, lvl + w * 0.06), ["#A8682E", "#8A4E1E", "#C8884A"], 26, (0.8, 1.8), (0.6, 1)))
    if stick:
        out.append(cinnamon_stick(D, cx - 6, lvl + 4, cx + w * 0.5, base - h - 40, 12, seed + 2))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - h, w / 2, w * 0.11, 0, 360, 20))}" fill="none" stroke="#5A6A60" stroke-width="1.6" opacity="0.7"/>')
    out.append(taper([(cx - w * 0.34, base - h + 8), (cx - w * 0.32, base - 10)], 5, 3, "#FFFFFF", 0.65))
    out.append(ink(bd, "#5A6A60", 1.8, seed + 3, 1, 0.7))
    return "".join(out)


def coconut_half(D, cx, cy, r, seed):
    """Half a coconut: hairy brown shell, thick white meat, a little milk shining inside."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 6, cy + r * 0.55, r * 1.05, r * 0.25, "#0A1A10", 0.45, seed)]
    shell = ell_pts(cx, cy, r, r * 0.35, 0, 180, 16) + [(cx - r, cy)]
    shell = [(cx + r, cy)] + [(cx + r * 0.95, cy + r * 0.35), (cx + r * 0.6, cy + r * 0.62), (cx, cy + r * 0.72), (cx - r * 0.6, cy + r * 0.62), (cx - r * 0.95, cy + r * 0.35), (cx - r, cy)]
    out.append(painted(D, shell, ("#B07A4A", "#7A4A26", "#3E2210"), seed, sk=0.2, angle=-60, n=30, inkw=1.6, hi=0.35))
    for _ in range(40):
        x = rnd.uniform(cx - r * 0.9, cx + r * 0.9)
        y = cy + rnd.uniform(r * 0.05, r * 0.6)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-6, 6):.1f} {rnd.uniform(2, 6):.1f}" stroke="#5A3418" stroke-width="1.1" opacity="0.6"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy, r, r * 0.32, 0, 360, 24))}" fill="#FFFDF6"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy + 2, r * 0.8, r * 0.24, 0, 360, 24))}" fill="#E8E0D0"/>')
    out.append(f'<path d="{blob(cx - r * 0.2, cy + 2, r * 0.3, r * 0.06, seed + 1, 0.1, 10)}" fill="#FFFFFF" opacity="0.9"/>')
    out.append(ink(smooth_closed(ell_pts(cx, cy, r, r * 0.32, 0, 360, 24)), INK, 1.6, seed + 2, 1, 0.7))
    return "".join(out)


def bokeh(D, seed, n, box, cols, r=(10, 26)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    return "".join(D.glow(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(*r), rnd.choice(cols), rnd.uniform(0.35, 0.7)) for _ in range(n))


@design("coquito")
def coquito():
    D = Doc2("prcc")
    out = [sky(D, [(0, "#1A3E2E"), (1, "#0E2A20")], 1101, 600, ["#24503A", "#0A2018", "#2E5E46"], 100, angle=-80, sop=(0.06, 0.16))]
    out.append(bokeh(D, 1102, 26, (0, 230, 600, 440), ["#FFD27A", "#FF8A6A", "#FFF0C0", "#8AE0C8"], (10, 28)))
    out.append(soft_glow(D, 260, 380, 300, "#FFE6B0", 0.3))
    out.append(wood_planks(D, 470, 600, 1103, ("#C88A5A", "#8A5230", "#4A2410"), 3))
    out.append(f'<rect y="466" width="600" height="8" fill="#2A1408" opacity="0.6"/>')
    # cinnamon sticks and a pine sprig on the table
    out.append(cinnamon_stick(D, 330, 560, 430, 540, 14, 1104))
    out.append(cinnamon_stick(D, 340, 574, 446, 560, 14, 1105))
    # titi's bottle with a bow and a little tag
    bt, (nx, ny, nw) = bottle(D, 232, 536, 330, 132, 1110, fill_to=0.92)
    out.append(bt)
    out.append(ribbon_bow(D, nx, ny + 4, 34, 1111))
    tx, ty = nx + 60, ny + 70
    out.append(pline([(nx + 10, ny + 10), (tx - 4, ty - 26)], "#C8A060", 1.4, 1112, 0.9, 1))
    tag = rot([(tx - 30, ty - 26), (tx + 34, ty - 26), (tx + 40, ty), (tx + 34, ty + 26), (tx - 30, ty + 26)], tx, ty, 14)
    out.append(painted(D, tag, ("#FFFDF4", "#F6EBD4", "#C8B08A"), 1113, sk=0.1, n=6, inkw=1.3, hi=0.3))
    out.append(f'<text x="{tx + 2}" y="{ty + 7}" text-anchor="middle" {SERIF_IT} font-size="22" fill="#B8361E" transform="rotate(14 {tx} {ty})">de Titi</text>')
    # two little glasses and half a coconut
    out.append(tumbler(D, 420, 548, 74, 92, 1120, stick=True))
    out.append(tumbler(D, 514, 528, 64, 80, 1121))
    out.append(coconut_half(D, 92, 520, 58, 1122))
    # lettering
    out.append(letters(D, 300, 132, "coquito", SERIF_IT, 136, "#FFF2D8", ["#FFFFFF", "#F2DCB4", "#FFE8C0"], 1130, max_w=420,
                       shadow="#06180E", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 178, "EL DE TITI ES EL MEJOR", "#F6C21C", font=JOS, size=19, ls=5, line_w=30, gap=12))
    return finish_b(D, out, 1131, "#FFFFFF", 0.5)


# ================================================================ 12. ¡ay, bendito! — a sato pup on the doorstep
@design("ay-bendito")
def ay_bendito():
    import furry_friends_painted as ff
    D = Doc2("prab")
    u = ff.Ids("prab")
    # a sunny yellow wall and a blue wooden door with panels
    out = [sky(D, [(0, "#F8D878"), (1, "#F2C04A")], 1201, 600, ["#FFE8A0", "#D8A02A", "#FFF0B8"], 110, angle=-84, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 160, 140, 340, "#FFF8E0", 0.5))
    dx0, dx1, dy0 = 132, 468, 236
    out.append(painted(D, rect_pts(dx0 - 22, dy0 - 22, dx1 + 22, 520, 24, 1202, 0.6), ("#FFFFFF", "#F2EEE6", "#C8BEB0"), 1202, sk=0.1, angle=-88, n=20, inkw=1.6, hi=0.3))
    out.append(painted(D, rect_pts(dx0, dy0, dx1, 520, 24, 1203, 0.6), ("#6AA8E0", "#2F6CC6", "#163E7A"), 1203, sdir=(1, 0.2), sk=0.1, angle=-88, n=70,
                       slen=(20, 60), sw=(1.5, 4), inkw=2, hi=0.3))
    mid = (dx0 + dx1) / 2
    for x0, x1 in ((dx0 + 20, mid - 12), (mid + 12, dx1 - 20)):
        for y0, y1 in ((dy0 + 24, dy0 + 110), (dy0 + 130, 500)):
            out.append(f'<path d="{hg.org_rect(x0, y0, x1 - x0, y1 - y0, int(x0 + y0), 0.6, 14, 2)}" fill="#245AA8"/>')
            out.append(pline([(x0, y1), (x0, y0), (x1, y0)], "#123A7A", 2.4, int(x0 + y0), 0.8, 1) + pline([(x0 + 1, y1), (x1, y1), (x1, y0 + 1)], "#8AC0F0", 2, int(x0 + y0) + 1, 0.8, 1))
    out.append(pline([(mid, dy0 + 4), (mid, 518)], "#123A7A", 3, 1204, 0.9, 1))
    out.append(disc(mid - 16, 360, 6, "#E8C060") + disc(mid + 16, 360, 6, "#E8C060"))
    # stone doorstep and the adoquines
    out.append(painted(D, rect_pts(dx0 - 40, 512, dx1 + 40, 540, 20, 1205, 0.5), ("#E8E0D4", "#C8C0B4", "#8A8478"), 1205, sk=0.15, angle=0, n=16, inkw=1.6, hi=0.4))
    out.append(f'<rect y="540" width="600" height="70" fill="#4E6E96"/>')
    rnd = random.Random(1206)
    for row, y in enumerate((544, 566, 588)):
        x = -20 + (24 if row % 2 else 0)
        while x < 620:
            out.append(f'<path d="{hg.org_rect(x, y, 46, 18, rnd.randint(0, 999), 0.6, 12, 3)}" fill="{rnd.choice(["#5A7AA2", "#6A8AB2", "#46648A", "#7898BE"])}"/>')
            out.append(f'<path d="M {x + 6} {y + 4} l 26 0" stroke="#C8E0F8" stroke-width="1.6" opacity="0.5"/>')
            x += 50
    # potted plant beside the door
    out.append(mata_en_lata(D, 530, 540, 56, 1207, "coleo", label_col="#D52B1E"))
    # the sato, sitting on the step looking up at you
    coat = ("#D99A5A", "#9A5A26", "#F2C690")
    white = ("#F6F0E6", "#D2C6B6", "#FFFFFF")
    d = ff.Dog(u, 300, 352, 1.02, coat, 1210, ink_c="#5A2E10", ears="drop", ear_len=0.62, ear_w=0.9, ear_y=6, skull=74, cheek=82,
               kind="smooth", nose_y=56, muzzle_w=34, tilt=9, look=(0.0, -0.9), eye_r=17, eye_x=36, mouth="closed",
               eyes=("#A8682A", "#3A1A06"), muzzle=white, chest_w=1.0, chest_len=300, round_top=0.5)

    def head(dd):
        return dd.blaze(white, 1211, 6, 14, 10)

    def chest(dd):
        return dd.bib(white, 1212, 0.8, dd.nose_y + 30)
    out.append(cast(D, 306, 530, 150, 16, strength=0.45, seed=1213))
    out.append(d.draw(marks_head=head, marks_chest=chest))
    # a little mango he was hoping to share
    out.append(painted(D, rot(blob_pts(430, 516, 26, 18, 1214, 0.06, 14), 430, 516, -20), ("#FFD27A", "#F28A2A", "#B8461A"), 1214, sdir=(0.6, 0.8), sk=0.2, angle=-20, n=12, inkw=1.6, hi=0.5))
    out.append(f'<path d="{blob(416, 506, 12, 8, 1215, 0.1, 10, -20)}" fill="#C8D86A" opacity="0.6"/>')
    out.append(taper([(450, 504), (458, 494)], 3, 2, "#5A3A1A"))
    # lettering
    out.append(letters(D, 300, 116, "¡Ay, bendito!", SERIF_IT, 96, "#B8261E", ["#D8483A", "#8A1408", "#E8684A"], 1220, max_w=470,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#FFD0C0"))
    out.append(ruled(300, 160, "MIRA ESA CARITA", "#1E4E9A", font=JOS, size=19, ls=7, line_w=34, gap=14))
    return finish_b(D, out, 1221)


# ================================================================ 13. vejigante — a horned festival mask, its vejiga and the cape
def horn(D, bx, by, ang, L, w, seed, pal, band=None, dots=None):
    """One papier-mâché horn: a curved cone from a base point, painted with bands or dots."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    bend = L * 0.18
    left, right, mid = [], [], []
    for i in range(13):
        t = i / 12
        b = bend * t * t
        px, py = bx + ux * L * t + nx * b, by + uy * L * t + ny * b
        ww = w / 2 * (1 - t) ** 0.9 + 0.6
        left.append((px + nx * ww, py + ny * ww))
        right.append((px - nx * ww, py - ny * ww))
        mid.append((px, py))
    pts = left + right[::-1]
    out = [painted(D, pts, pal, seed, sdir=(nx, ny), sk=0.22, angle=ang, n=8, inkw=1.4, inkop=0.7, hi=0.45)]
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    if band:
        for k in (3, 6, 9):
            x, y = mid[k]
            ww = w / 2 * (1 - k / 12) ** 0.9 + 1
            inner.append(taper([(x + nx * ww * 1.2 - ux * 3, y + ny * ww * 1.2 - uy * 3), (x - nx * ww * 1.2 + ux * 3, y - ny * ww * 1.2 + uy * 3)], 5, 5, band))
    if dots:
        for k in range(2, 11, 2):
            x, y = mid[k]
            inner.append(disc(x, y, max(1.6, w * 0.1 * (1 - k / 12) + 1.2), dots))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(out)


def vejigante_mask(D, cx, cy, s, seed):
    """Ponce-style vejigante mask: a yellow polka-dotted face crowned by colourful horns, big round eyes, a long
    snout and a grin full of pointed teeth, cheeks painted with spirals."""
    rnd = random.Random(seed)
    out = []
    hp = [(ROJO[0], ROJO[1], ROJO[2]), ("#7AD0A0", "#1F9A5A", "#0E5A30"), ("#7AB4F0", "#2F6CC6", "#123A7A"), ("#FFE07A", "#F6B81C", "#A8700A"),
          ("#FF9AC8", "#E0308A", "#8A1050")]
    horns = []
    for k in range(13):
        ang = -200 + k * 220 / 12 + rnd.uniform(-5, 5)
        L = s * rnd.uniform(0.5, 0.8) * (0.85 if 4 <= k <= 8 else 1.05)
        r = math.radians(ang)
        bx, by = cx + math.cos(r) * s * 0.42, cy - s * 0.12 + math.sin(r) * s * 0.4
        horns.append((bx, by, ang, L, k))
    for bx, by, ang, L, k in sorted(horns, key=lambda h: -h[3]):
        pal = hp[k % len(hp)]
        out.append(horn(D, bx, by, ang, L, s * 0.17, seed + k, pal, band="#FFFFFF" if k % 2 else None, dots=None if k % 2 else "#FFF6D0"))
    # the face
    face = [(cx, cy - s * 0.5), (cx + s * 0.34, cy - s * 0.42), (cx + s * 0.48, cy - s * 0.12), (cx + s * 0.46, cy + s * 0.22), (cx + s * 0.32, cy + s * 0.5),
            (cx, cy + s * 0.6), (cx - s * 0.32, cy + s * 0.5), (cx - s * 0.46, cy + s * 0.22), (cx - s * 0.48, cy - s * 0.12), (cx - s * 0.34, cy - s * 0.42)]
    out.append(painted(D, face, ("#FFE88A", "#F6C21C", "#B8820A"), seed + 20, sdir=(0.6, 0.7), sk=0.14, angle=-60, n=60, inkw=2.4, hi=0.45))
    fd = smooth_closed(face)
    cid = D.clip(f'<path d="{fd}"/>')
    inner = []
    for _ in range(60):
        x, y = cx + rnd.uniform(-s * 0.48, s * 0.48), cy + rnd.uniform(-s * 0.5, s * 0.6)
        inner.append(disc(x, y, rnd.uniform(s * 0.018, s * 0.032), rnd.choice(["#D52B1E", "#D52B1E", "#1A1A1A", "#2F6CC6"])))
    for sg in (-1, 1):
        x, y = cx + sg * s * 0.3, cy + s * 0.2
        inner.append(f'<path d="{blob(x, y, s * 0.11, s * 0.08, seed + 30 + sg, 0.1, 10)}" fill="#F28A6A" opacity="0.8"/>')
        sp = [(x + math.cos(t) * s * 0.012 * t, y + math.sin(t) * s * 0.012 * t) for t in [i * 0.5 for i in range(14)]]
        inner.append(pline(sp, "#D52B1E", 2.2, seed + 32 + sg, 0.9, 1))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # brows and eyes
    for sg in (-1, 1):
        ex, ey = cx + sg * s * 0.19, cy - s * 0.14
        out.append(taper([(ex - sg * s * 0.14, ey - s * 0.14), (ex, ey - s * 0.2), (ex + sg * s * 0.12, ey - s * 0.13)], s * 0.05, s * 0.02, "#1A1A1A"))
        out.append(painted(D, blob_pts(ex, ey, s * 0.13, s * 0.12, seed + 40 + sg, 0.03, 14), ("#FFFFFF", "#F6F2EA", "#C8C0B0"), seed + 40 + sg, sk=0.12, n=6, inkw=0, hi=0.4))
        out.append(ink(blob(ex, ey, s * 0.13, s * 0.12, seed + 40 + sg, 0.03, 14), "#D52B1E", 3.2, seed + 42 + sg, 1, 0.95))
        out.append(disc(ex + sg * s * 0.01, ey + s * 0.02, s * 0.065, "#1E6A3A") + disc(ex + sg * s * 0.01, ey + s * 0.02, s * 0.038, "#0A0A0A"))
        out.append(disc(ex - s * 0.02, ey - s * 0.015, s * 0.018, "#FFFFFF"))
        for k in range(5):
            a = math.radians(-150 + k * 30) if sg < 0 else math.radians(-150 + k * 30)
            out.append(pline([(ex + math.cos(a) * s * 0.13, ey + math.sin(a) * s * 0.12), (ex + math.cos(a) * s * 0.19, ey + math.sin(a) * s * 0.18)], "#1A1A1A", 2, seed + 50 + k, 0.9, 1))
    # snout
    sn = [(cx - s * 0.08, cy - s * 0.06), (cx + s * 0.08, cy - s * 0.06), (cx + s * 0.13, cy + s * 0.14), (cx + s * 0.08, cy + s * 0.2), (cx - s * 0.08, cy + s * 0.2), (cx - s * 0.13, cy + s * 0.14)]
    out.append(painted(D, sn, ("#FF8A6A", "#E8401E", "#94180C"), seed + 60, sdir=(0.6, 0.8), sk=0.2, n=8, inkw=1.6, hi=0.5))
    for sg in (-1, 1):
        out.append(disc(cx + sg * s * 0.05, cy + s * 0.15, s * 0.025, "#3A0A04"))
    # grin with teeth
    mouth = [(cx - s * 0.3, cy + s * 0.26), (cx, cy + s * 0.32), (cx + s * 0.3, cy + s * 0.26), (cx + s * 0.2, cy + s * 0.46), (cx, cy + s * 0.52), (cx - s * 0.2, cy + s * 0.46)]
    out.append(painted(D, mouth, ("#C8303A", "#8A1018", "#4A0408"), seed + 70, sk=0.2, n=8, inkw=2, hi=0.2))
    md = smooth_closed(mouth)
    mc = D.clip(f'<path d="{md}"/>')
    teeth = []
    for k in range(9):
        x = cx - s * 0.27 + k * s * 0.0675
        y = cy + s * 0.27 + abs(k - 4) * -s * 0.008 + s * 0.03
        teeth.append(f'<path d="M {x - s * 0.03:.1f} {y - s * 0.03:.1f} L {x + s * 0.03:.1f} {y - s * 0.03:.1f} L {x:.1f} {y + s * 0.07:.1f} Z" fill="#FFFDF2" stroke="#8A7A6A" stroke-width="0.8"/>')
    for k in range(6):
        x = cx - s * 0.16 + k * s * 0.064
        y = cy + s * 0.5
        teeth.append(f'<path d="M {x - s * 0.028:.1f} {y + s * 0.02:.1f} L {x + s * 0.028:.1f} {y + s * 0.02:.1f} L {x:.1f} {y - s * 0.06:.1f} Z" fill="#FFFDF2" stroke="#8A7A6A" stroke-width="0.8"/>')
    out.append(f'<g {mc}>{"".join(teeth)}</g>')
    out.append(ink(md, "#1A1A1A", 2.4, seed + 71, 1, 0.9))
    return "".join(out)


def vejiga(D, cx, cy, r, seed):
    """The dried, inflated bladder the vejigantes carry: a translucent amber balloon, painted with stripes, on a cord."""
    out = [pline([(cx, cy + r * 0.9), (cx - 6, cy + r * 1.4), (cx + 4, cy + r * 1.9)], "#5A3A1A", 2, seed, 0.9, 1)]
    pts = blob_pts(cx, cy, r * 0.86, r, seed, 0.06, 16)
    out.append(painted(D, pts, ("#FFE8B0", "#E8B860", "#A8701E"), seed, sdir=(0.6, 0.7), sk=0.18, angle=-70, n=20, inkw=1.8, hi=0.55, hik=0.12))
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    out.append(f'<g {cid}>' + "".join(taper([(cx + k * r * 0.4 - r * 0.2, cy - r), (cx + k * r * 0.5, cy), (cx + k * r * 0.4 + r * 0.1, cy + r)], 7, 7, c, 0.75)
                                      for k, c in ((-1, "#D52B1E"), (0, "#1F9A5A"), (1, "#2F6CC6"))) + '</g>')
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.45, r * 0.18, r * 0.1, seed + 1, 0.2, 10, -40)}" fill="#FFFFFF" opacity="0.8"/>')
    out.append(painted(D, blob_pts(cx, cy + r * 0.98, r * 0.12, r * 0.09, seed + 2, 0.1, 8), ("#E8B860", "#A8701E", "#5A3A0A"), seed + 2, sk=0.2, n=2, inkw=1, hi=0.3))
    return "".join(out)


@design("vejigante")
def vejigante():
    D = Doc2("prvj")
    out = [paper(D.nid(), "#FCE8C8", FLECK, 1301)]
    # the costume's bat-wing cape, spread behind the mask: two printed fabrics with ribbon edges
    for sg, base, dots, seed in ((-1, ("#F27A6A", "#D52B1E", "#8A1410"), "#F6C21C", 1302), (1, ("#7AD0C8", "#1F9A8A", "#0E5A50"), "#FFFFFF", 1303)):
        wing = [(300, 420), (300 + sg * 110, 352), (300 + sg * 220, 292), (300 + sg * 330, 250), (300 + sg * 300, 330), (300 + sg * 330, 410),
                (300 + sg * 280, 480), (300 + sg * 310, 560), (300 + sg * 230, 610), (300 + sg * 150, 640), (300, 640)]
        out.append(painted(D, wing, base, seed, sdir=(sg * 0.6, 0.8), sk=0.12, angle=-70, n=80, inkw=2, hi=0.3))
        wd = smooth_closed(wing)
        cid = D.clip(f'<path d="{wd}"/>')
        rnd = random.Random(seed)
        pat = []
        for _ in range(110):
            pat.append(disc(rnd.uniform(0, 600), rnd.uniform(220, 640), rnd.uniform(4, 7), dots, 0.9))
        for k in range(5):
            y = 300 + k * 70
            pat.append(taper([(300, y), (300 + sg * 160, y - 30), (300 + sg * 320, y + 10)], 12, 6, dk(base[1], 0.25), 0.35))
        out.append(f'<g {cid}>{"".join(pat)}</g>')
        edge = [(300 + sg * 330, 250), (300 + sg * 300, 330), (300 + sg * 330, 410), (300 + sg * 280, 480), (300 + sg * 310, 560), (300 + sg * 230, 610)]
        for k, c in enumerate(("#F6C21C", "#2F6CC6", "#FFFFFF", "#E0308A")):
            out.append(taper([(x + sg * (6 + k * 6), y + k * 2) for x, y in catmull(edge, 6)], 6, 6, c, 0.95))
    out.append(soft_glow(D, 300, 380, 230, "#FFF6D8", 0.55))
    # the mask
    out.append(cast(D, 314, 520, 150, 20, "#3A0A04", 0.35, 1310))
    out.append(vejigante_mask(D, 300, 408, 206, 1311))
    # the vejiga floating at the side, confetti
    out.append(vejiga(D, 508, 470, 44, 1320))
    rnd = random.Random(1321)
    for _ in range(26):
        x, y = rnd.uniform(60, 540), rnd.uniform(200, 560)
        if 170 < x < 430 and 220 < y < 530:
            continue
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="8" height="4" fill="{rnd.choice(["#D52B1E", "#2F6CC6", "#F6C21C", "#FFFFFF", "#1F9A5A"])}" transform="rotate({rnd.uniform(0, 180):.0f} {x:.1f} {y:.1f})"/>')
    # lettering
    out.append(letters(D, 300, 128, "vejigante", SERIF_IT, 116, "#D52B1E", ["#F05A4A", "#9A1410", "#FF7A60"], 1330, max_w=440,
                       shadow="#123A7A", soff=(0.022, 0.036), angle=-40, hi="#FFD0C0"))
    out.append(ruled(300, 180, "DE LOÍZA A PONCE", "#123A7A", font=JOS, size=19, ls=7, line_w=34, gap=14))
    return finish_b(D, out, 1331)


# ================================================================ 14. café colao — dawn on a mountain balcony, the cloth colador on its nail
def coffee_branch(D, pts, seed, n_leaves=8, clusters=4):
    """A coffee branch: glossy opposite leaves with wavy edges and clusters of red and green cherries at the nodes."""
    rnd = random.Random(seed)
    path = catmull(pts, 6)
    out = [taper(path, 6, 3, "#6A5A3A")]
    for i in range(n_leaves):
        t = (i + 0.5) / n_leaves
        x, y = path[int(t * (len(path) - 1))]
        for sg in (-1, 1):
            a = math.degrees(math.atan2(path[-1][1] - path[0][1], path[-1][0] - path[0][0])) + sg * rnd.uniform(40, 70)
            out.append(leaf_simple(D, x, y, rnd.uniform(48, 70), rnd.uniform(14, 18), a, ("#7AB86A", "#2E7A3A", "#0E4A1E"), seed + i * 2 + (sg > 0), vein=True, inkw=1.2))
    for c in range(clusters):
        t = (c + 0.7) / (clusters + 0.5)
        x, y = path[int(t * (len(path) - 1))]
        for k in range(6):
            bx, by = x + rnd.uniform(-12, 12), y + rnd.uniform(-6, 12)
            col = rnd.choice([ROJO, ROJO, ("#FF8A6A", "#C8302A", "#6A0A0A"), ("#C8D86A", "#7AA83A", "#3A5A14")])
            out.append(painted(D, blob_pts(bx, by, 7, 8, seed + 50 + c * 7 + k, 0.05, 10), col, seed + 50 + c * 7 + k, sk=0.25, n=3, inkw=1.0, hi=0.55))
            out.append(disc(bx - 2.4, by - 3, 1.6, "#FFFFFF", 0.8))
    return "".join(out)


def enamel_cup(D, cx, base, w, h, seed, body=WHITE, rim=AZUL, coffee="#2A1206", handle=1):
    """Enamel tin cup: white body, blue rolled rim, chipped edge, coffee inside."""
    out = [cast(D, cx + 8, base, w * 0.72, 8, strength=0.45, seed=seed)]
    hx = cx + handle * w / 2
    hp = [(hx - 2 * handle, base - h * 0.85), (hx + 22 * handle, base - h * 0.82), (hx + 26 * handle, base - h * 0.5), (hx + 16 * handle, base - h * 0.25), (hx - 2 * handle, base - h * 0.25)]
    out.append(ink(smooth_open(hp), rim[2], 9, seed, 1, 1) + ink(smooth_open(hp), body[0], 5, seed + 1, 1, 1))
    pts = rect_pts(cx - w / 2, base - h, cx + w / 2, base, 10, seed, 0.4)
    out.append(painted(D, pts, body, seed, sdir=(1, 0.2), sk=0.16, angle=-90, n=14, inkw=1.6, hi=0.5))
    out.append(f'<path d="{blob(cx + w * 0.22, base - h * 0.3, 4, 3, seed + 3, 0.2, 8)}" fill="#1E1E28"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - h, w / 2, w * 0.13, 0, 360, 20))}" fill="{rim[1]}"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - h + 1, w / 2 - 4, w * 0.1, 0, 360, 20))}" fill="{coffee}"/>')
    out.append(f'<path d="{blob(cx - w * 0.15, base - h, w * 0.14, w * 0.025, seed + 4, 0.1, 8)}" fill="#C8905A" opacity="0.7"/>')
    out.append(pline([(cx - w / 2 + 1, base - 4), (cx, base + 2), (cx + w / 2 - 1, base - 4)], rim[1], 3.4, seed + 5, 0.95, 1))
    return "".join(out)


@design("cafe-colao")
def cafe_colao():
    D = Doc2("prcf")
    out = [sky(D, [(0, "#F6C8A0"), (0.4, "#F8DCC0"), (0.7, "#FCEEDC"), (1, "#EAF0E8")], 1401, 480, ["#FFFFFF", "#F8D0B0", "#FFF0E0"], 60)]
    out.append(soft_glow(D, 430, 230, 260, "#FFF2C8", 0.75))
    out.append(disc(430, 230, 30, "#FFF6D8", 0.95))
    # misty coffee mountains, layer on layer
    for k, (y, pal) in enumerate(((268, ("#D8CCD8", "#C4B8CC", "#A098B4")), (300, ("#B8C8C8", "#9AB4B4", "#7898A0")),
                                  (340, ("#9ABEA4", "#78A488", "#4E7A64")), (390, ("#7AAE78", "#5A9A5E", "#2E6A3E")))):
        line = ridge([(-20, y), (90, y - 34 + k * 4), (210, y - 6), (330, y - 40), (450, y - 10), (560, y - 30), (620, y - 8)], 1402 + k, 12, 4)
        out.append(hill(D, line, 600, pal, 1406 + k, inkw=0 if k < 2 else 1, inkop=0.3, sop=(0.08, 0.22)))
        out.append(f'<rect y="{y - 10}" width="600" height="46" fill="{D.lin([(0, "#FFF8F0", 0), (0.5, "#FFF8F0", 0.42 - k * 0.06), (1, "#FFF8F0", 0)])}"/>')
    # a hacienda roof and coffee rows on the near slope
    out.append(painted(D, [(458, 372), (520, 372), (530, 384), (448, 384)], ("#E87A5A", "#B8461E", "#6A1A08"), 1410, sk=0.2, n=4, inkw=1, hi=0.3))
    out.append(f'<path d="M 452 384 L 526 384 L 526 400 L 452 400 Z" fill="#F6F0E4"/>')
    rnd = random.Random(1411)
    for row in range(6):
        y = 404 + row * 13
        for k in range(22):
            x = -10 + k * 30 + (15 if row % 2 else 0) + rnd.uniform(-3, 3)
            out.append(f'<path d="{blob(x, y, 9, 5, rnd.randint(0, 999), 0.2, 8)}" fill="{rnd.choice(["#3E7A3A", "#2E6A2E", "#4E8A44"])}"/>')
    for x, y, s in ((160, 200, 8), (186, 214, 6), (520, 170, 7)):
        out.append(bird_v(x, y, s, "#6A5A6A", 0.8))
    # the balcony: a wooden post on the left, the railing beam across
    post = rect_pts(70, -10, 116, 610, 30, 1412, 0.6)
    out.append(painted(D, post, ("#C8905E", "#8E5A30", "#4A2A12"), 1412, sdir=(1, 0), sk=0.15, angle=-90, n=50, slen=(30, 90), sw=(1, 3), inkw=2, hi=0.35))
    rail = rect_pts(-10, 470, 610, 500, 30, 1413, 0.6)
    out.append(cast(D, 300, 512, 330, 12, strength=0.4, seed=1414))
    out.append(painted(D, rail, ("#D8A06A", "#A06A38", "#5A3214"), 1413, sdir=(0, 1), sk=0.2, angle=0, n=60, slen=(30, 100), sw=(1, 3), inkw=2, hi=0.45))
    for x in (150, 230, 310, 390, 470, 550):
        out.append(painted(D, rect_pts(x - 8, 500, x + 8, 610, 20, 1415 + x, 0.4), ("#C8905E", "#8E5A30", "#4A2A12"), 1415 + x, sdir=(1, 0), sk=0.2, angle=-90, n=10, inkw=1.4, hi=0.3))
    # the cloth colador hanging from its nail on the post
    nx_, ny_ = 106, 168
    out.append(disc(nx_, ny_, 4, "#3A3A42"))
    out.append(painted(D, rect_pts(nx_ - 4, ny_ - 2, nx_ + 6, ny_ + 96, 10, 1420, 0.4), ("#D8A06A", "#9A6232", "#4A2410"), 1420, sk=0.2, angle=-90, n=6, inkw=1.4, hi=0.4))
    rx_, ry_ = nx_ + 30, ny_ + 112
    out.append(ink(smooth_closed(ell_pts(rx_, ry_, 34, 10, 0, 360, 24)), "#5A5A62", 3, 1421, 1, 0.95))
    bag = [(rx_ - 34, ry_), (rx_ - 30, ry_ + 40), (rx_ - 16, ry_ + 84), (rx_ + 2, ry_ + 104), (rx_ + 14, ry_ + 96), (rx_ + 28, ry_ + 50), (rx_ + 34, ry_)]
    bd = smooth_closed(bag)
    out.append(f'<path d="{bd}" fill="#F2E8D4"/>')
    cid = D.clip(f'<path d="{bd}"/>')
    g = D.lin([(0, "#F2E8D4", 0), (0.4, "#C89A62", 0.5), (0.75, "#7A4A22", 0.9), (1, "#3A1A08", 1)])
    out.append(f'<g {cid}><rect x="{rx_ - 40}" y="{ry_}" width="80" height="110" fill="{g}"/>'
               + strokes(D.nid(), bd, (rx_ - 40, ry_, rx_ + 40, ry_ + 110), ["#FFFFFF", "#B8925E", "#8A5A2E"], 1422, n=40, angle=-95, length=(10, 30), width=(1, 2.4), opacity=(0.15, 0.4))
               + shade_over(D, bd, "#2A1206", 0.4, 0, 0, 1, 0, 0.5) + '</g>')
    out.append(ink(bd, INK, 1.8, 1423, 2, 0.75))
    out.append(ink(smooth_open(ell_pts(rx_, ry_, 34, 10, 0, 180, 12)), "#5A5A62", 3, 1424, 1, 0.95))
    out.append(pline([(nx_ + 4, ny_ + 92), (rx_ - 30, ry_ - 4)], "#5A5A62", 2.4, 1425, 0.95, 1))
    for k, (x, y, r) in enumerate(((rx_ + 4, ry_ + 116, 3.2), (rx_ + 5, ry_ + 134, 2.6))):
        out.append(f'<path d="{smooth_closed([(x, y - r * 2.2)] + [(x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))) for a in range(-20, 201, 20)])}" fill="#4A2410"/>')
    # on the rail: the enamel cup of café, a little tin of sugar
    out.append(enamel_cup(D, 330, 474, 76, 62, 1430))
    out.append(steam(330, 404, 70, 1431, "#FFFFFF", 3, 20, 6, 0.75))
    out.append(painted(D, rect_pts(424, 432, 470, 474, 10, 1432, 0.4), ("#F4867A", "#D52B1E", "#8A1410"), 1432, sdir=(1, 0.2), sk=0.18, angle=-90, n=8, inkw=1.4, hi=0.5))
    out.append(f'<path d="{smooth_closed(ell_pts(447, 432, 23, 5, 0, 360, 16))}" fill="#E8E8EE" stroke="#8A8A92" stroke-width="1.2"/>')
    out.append(pline([(426, 452), (468, 452)], "#FFFFFF", 2, 1433, 0.8, 1))
    # a coffee branch reaching into the frame
    out.append(coffee_branch(D, [(620, 600), (560, 548), (500, 530), (440, 548)], 1440, 5, 3))
    # lettering
    out.append(letters(D, 300, 120, "café colao", SERIF_IT, 108, "#6A2E12", ["#8A4A22", "#4A1A06", "#A86A3A"], 1450, max_w=440,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#E8C8A8"))
    out.append(ruled(316, 162, "Y UN BUENOS DÍAS", "#2E6A3A", font=JOS, size=19, ls=7, line_w=30, gap=12))
    return finish_b(D, out, 1451)


# ================================================================ 15. tostones — on the oilcloth with mayoketchup
def toston(D, cx, cy, r, seed, tilt=0.62, rot_=0):
    """A tostón: a flattened, twice-fried green plantain round, golden with crisp darker frills and faint rings."""
    rnd = random.Random(seed)
    pts = []
    for i in range(26):
        a = 2 * math.pi * i / 26
        rr = r * (1 + rnd.uniform(-0.08, 0.1))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * tilt))
    pts = rot(pts, cx, cy, rot_)
    out = [cast(D, cx + 5, cy + r * tilt * 0.5, r * 1.05, r * tilt * 0.8, "#3A1A04", 0.35, seed)]
    out.append(painted(D, pts, ("#FFEA9A", "#F2C24E", "#B07020"), seed, sdir=(0.5, 0.9), sk=0.1, angle=rot_ - 20, n=16, inkw=1.6, inkop=0.7, hi=0.55))
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    inner = [f'<path d="{d}" fill="none" stroke="#B8701E" stroke-width="{r * 0.22:.1f}" opacity="0.45"/>']
    for k in (0.62, 0.36):
        inner.append(ink(smooth_closed(rot([(cx + r * k * math.cos(a), cy + r * k * math.sin(a) * tilt) for a in [i * 0.4 for i in range(16)]], cx, cy, rot_)), "#C8862E", 1.2, seed + int(k * 10), 1, 0.5))
    for _ in range(int(r * 0.5)):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, r * 0.9)
        x, y = rot([(cx + rr * math.cos(a), cy + rr * math.sin(a) * tilt)], cx, cy, rot_)[0]
        inner.append(disc(x, y, rnd.uniform(0.8, 1.8), rnd.choice(["#8A4A10", "#FFF4C8", "#C07A22"]), rnd.uniform(0.5, 0.9)))
    for _ in range(10):
        a = rnd.uniform(0, 6.28)
        x, y = rot([(cx + r * 0.3 * math.cos(a), cy + r * 0.3 * math.sin(a) * tilt)], cx, cy, rot_)[0]
        inner.append(disc(x, y, 1.4, "#FFFFFF", 0.95))
    inner.append(f'<path d="{blob(cx - r * 0.3, cy - r * 0.25 * tilt, r * 0.3, r * 0.12, seed + 2, 0.2, 10, rot_ - 15)}" fill="#FFF6D0" opacity="0.6"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(out)


def lemon_print(cx, cy, s, seed):
    """Oilcloth print motif: a lemon with two leaves and a white blossom."""
    out = [f'<path d="{blob(cx, cy, s, s * 0.72, seed, 0.06, 14, -20)}" fill="#F6D24A"/>',
           f'<path d="{blob(cx - s * 0.3, cy - s * 0.25, s * 0.35, s * 0.15, seed + 1, 0.1, 8, -20)}" fill="#FFF0A0"/>']
    for sg in (-1, 1):
        out.append(f'<path d="{blob(cx + sg * s * 0.9, cy - s * 0.7, s * 0.6, s * 0.24, seed + 2 + sg, 0.1, 10, sg * 35)}" fill="#3E9A4A"/>')
    for k in range(5):
        a = math.radians(k * 72)
        out.append(disc(cx + s * 1.3 + math.cos(a) * s * 0.18, cy + s * 0.5 + math.sin(a) * s * 0.18, s * 0.14, "#FFFFFF"))
    out.append(disc(cx + s * 1.3, cy + s * 0.5, s * 0.08, "#F6C21C"))
    return "".join(out)


@design("tostones")
def tostones():
    D = Doc2("prts")
    # turquoise oilcloth printed with lemons, seen at a low angle
    tile = (f'<rect width="150" height="150" fill="#3CB8B0"/>' + lemon_print(40, 44, 18, 1) + lemon_print(115, 112, 16, 2) +
            '<circle cx="110" cy="30" r="4" fill="#FFFFFF" opacity="0.7"/><circle cx="30" cy="120" r="4" fill="#FFFFFF" opacity="0.7"/>')
    pat = D.pattern(150, 150, tile, transform="translate(0 210) scale(1 0.62)")
    out = [f'<rect width="600" height="600" fill="{pat}"/>']
    out.append(f'<rect width="600" height="600" fill="{D.lin([(0, "#0E3A38", 0.45), (0.45, "#0E3A38", 0.0), (1, "#0E3A38", 0.25)])}"/>')
    out.append(soft_glow(D, 280, 380, 320, "#FFF6E0", 0.4))
    # the platter of tostones
    cx, cy = 288, 404
    out.append(cast(D, cx + 16, cy + 26, 236, 118, "#0A2A28", 0.5, 1501))
    out.append(painted(D, ell_pts(cx, cy, 228, 128, 0, 360, 40), ("#FFFFFF", "#F6F2EA", "#C8C0B0"), 1502, sk=0.08, n=30, inkw=2, hi=0.4))
    out.append(ink(smooth_closed(ell_pts(cx, cy + 4, 196, 104, 0, 360, 40)), "#D8D0C4", 1.6, 1503, 1, 0.8))
    for i in range(40):
        a = 2 * math.pi * i / 40
        out.append(disc(cx + math.cos(a) * 214, cy + math.sin(a) * 118, 3, "#D52B1E" if i % 2 else "#2F6CC6", 0.85))
    spots = [(cx - 120, cy - 10, -10), (cx - 52, cy - 46, 10), (cx + 30, cy - 52, -6), (cx + 108, cy - 28, 12), (cx - 96, cy + 46, 6), (cx - 18, cy + 18, -14),
             (cx + 64, cy + 30, 4), (cx + 132, cy + 52, -8), (cx + 4, cy + 72, 10)]
    for k, (x, y, a) in enumerate(sorted(spots, key=lambda p: p[1])):
        out.append(toston(D, x, y, 46, 1510 + k, 0.6, a))
    # salt
    out.append(specks(1530, (cx - 180, cy - 80, cx + 180, cy + 100), ["#FFFFFF"], 80, (0.8, 1.6), (0.7, 1)))
    # mayoketchup in a little bowl, a tostón dipped in it
    bx, by = 476, 520
    out.append(cast(D, bx + 8, by + 24, 70, 18, "#0A2A28", 0.45, 1531))
    bowl = [(bx - 62, by - 6), (bx - 54, by + 18), (bx - 30, by + 34), (bx + 30, by + 34), (bx + 54, by + 18), (bx + 62, by - 6)]
    out.append(painted(D, bowl, ("#FFF2C0", "#F6C21C", "#B8860A"), 1532, sdir=(0.8, 0.5), sk=0.16, angle=-90, n=12, inkw=1.6, hi=0.5))
    out.append(f'<path d="{smooth_closed(ell_pts(bx, by - 6, 62, 16, 0, 360, 24))}" fill="#FFE8A0"/>')
    sauce = blob(bx, by - 5, 54, 12, 1533, 0.03, 20)
    out.append(f'<path d="{sauce}" fill="#F2905A"/>')
    out.append(f'<path d="{blob(bx - 16, by - 8, 18, 3.4, 1534, 0.1, 10)}" fill="#FFC8A0" opacity="0.8"/>')
    out.append(ink(smooth_closed(ell_pts(bx, by - 6, 62, 16, 0, 360, 24)), INK, 1.4, 1535, 1, 0.7))
    # a green plantain, peeled and sliced, waiting its turn on a little board
    tx, ty = 112, 540
    out.append(cast(D, tx + 10, ty + 22, 100, 18, "#0A2A28", 0.45, 1540))
    out.append(painted(D, rot(rect_pts(tx - 92, ty - 30, tx + 92, ty + 30, 14, 1541, 0.6), tx, ty, -6), ("#E8B47A", "#B07840", "#5E3A18"), 1541,
                       sdir=(0.4, 1), sk=0.15, angle=-6, n=20, inkw=1.6, hi=0.45))
    out.append(plantain(D, (tx - 80, ty - 4), (tx + 10, ty - 14), 26, 1542, pal=("#F2F2B0", "#D8DC8A", "#8A9A3A"), bend=0.08, tips="#E8E8A8"))
    for k, (x, y) in enumerate(((tx + 34, ty + 4), (tx + 62, ty - 6))):
        out.append(painted(D, blob_pts(x, y, 15, 10, 1543 + k, 0.06, 12), ("#F6F6C8", "#E0E4A0", "#8A9A3A"), 1543 + k, sk=0.15, n=4, inkw=1.2, hi=0.5))
        out.append(ink(blob(x, y, 9, 6, 1545 + k, 0.08, 10), "#C8C88A", 1, 1545 + k, 1, 0.6))
    # lettering
    out.append(letters(D, 300, 132, "tostones", SERIF_IT, 128, "#FFF4D8", ["#FFFFFF", "#F6E0B0", "#FFE8C0"], 1550, max_w=440,
                       shadow="#0A3A36", soff=(0.022, 0.036), angle=-40, hi="#FFFFFF"))
    band = rect_pts(118, 152, 482, 190, 20, 1551, 0.8)
    out.append(painted(D, band, ("#FFFDF4", "#F6EEDC", "#C8B898"), 1551, sk=0.1, angle=0, n=12, inkw=1.4, hi=0.3))
    out.append(label(300, 179, "CON MAYOKETCHUP, CLARO", JOS, 20, "#B8361E", ls=4, max_w=340))
    return finish_b(D, out, 1552)


# ================================================================ 16. parranda — the asalto at the door, instruments at the ready
CUATRO_HALF = [(0, 0.0), (0.13, 0.01), (0.21, 0.05), (0.25, 0.14), (0.245, 0.24), (0.215, 0.31), (0.24, 0.345), (0.17, 0.375), (0.15, 0.45),
               (0.165, 0.52), (0.235, 0.55), (0.215, 0.585), (0.28, 0.64), (0.31, 0.73), (0.29, 0.84), (0.22, 0.935), (0.1, 0.985), (0, 1.0)]


def cuatro(D, cx, top, S, ang, seed, wood=("#F0C890", "#D49A5A", "#8A5428"), side=("#A8642E", "#6E3A14", "#3A1A06")):
    """The Puerto Rican cuatro: violin-like body with pointed bouts, a ring of small sound holes, five double courses
    of strings, a long fretted neck and a flat headstock with ten pegs. `top` is where the neck meets the body."""
    def T(pts):
        return rot([(cx + x * S, top + y * S) for x, y in pts], cx, top, ang)

    out = []
    half = CUATRO_HALF
    outline = half + [(-x, y) for x, y in reversed(half[1:-1])]
    body = T(outline)
    depth = T([(x + 0.035, y + 0.02) for x, y in outline])
    out.append(f'<path d="{smooth_closed(depth)}" fill="{side[1]}"/>')
    out.append(painted(D, body, wood, seed, sdir=(0.6, 0.8), sk=0.1, angle=ang - 90, n=40, slen=(S * 0.1, S * 0.3), sw=(1, 2.4), inkw=2, hi=0.45, hik=0.06))
    bd = smooth_closed(body)
    cid = D.clip(f'<path d="{bd}"/>')
    inner = [shade_over(D, bd, "#3A1A06", 0.35, 0, 0, 1, 1, 0.5)]
    # purfling just inside the edge
    inner.append(ink(smooth_closed(T([(x * 0.92, 0.04 + y * 0.92) for x, y in outline])), side[1], 1.6, seed + 1, 1, 0.6))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # sound holes: a ring of little holes around a centre hole
    hx, hy = 0, 0.42
    out.append(disc(*T([(hx, hy)])[0], S * 0.055, "#2A1406"))
    for k in range(10):
        a = 2 * math.pi * k / 10
        out.append(disc(*T([(hx + math.cos(a) * 0.1, hy + math.sin(a) * 0.1)])[0], S * 0.016, "#2A1406"))
    out.append(ink(smooth_closed(T([(hx + math.cos(a) * 0.14, hy + math.sin(a) * 0.14) for a in [i * 0.4 for i in range(16)]])), side[1], 1.4, seed + 2, 1, 0.6))
    # bridge
    out.append(f'<path d="{pd(T([(-0.14, 0.76), (0.14, 0.76), (0.14, 0.79), (-0.14, 0.79)]))}" fill="{side[2]}"/>')
    # neck, fretboard and headstock
    neck = T([(-0.06, 0.02), (0.06, 0.02), (0.05, -0.82), (-0.05, -0.82)])
    out.append(painted(D, neck, ("#8A5428", "#5A3014", "#2A1406"), seed + 3, sk=0.15, angle=ang - 90, n=8, inkw=1.4, hi=0.35))
    for k in range(1, 12):
        y = -0.8 + k * 0.07
        out.append(pline(T([(-0.05, y), (0.05, y)]), "#E8E0D0", 1.2, seed + 10 + k, 0.8, 1))
    head = T([(-0.06, -0.82), (0.06, -0.82), (0.09, -1.08), (0.0, -1.12), (-0.09, -1.08)])
    out.append(painted(D, head, wood, seed + 4, sk=0.15, angle=ang - 90, n=6, inkw=1.4, hi=0.4))
    for k in range(5):
        y = -0.88 - k * 0.045
        for sg in (-1, 1):
            out.append(disc(*T([(sg * 0.11, y)])[0], S * 0.018, "#E8E0D0") + disc(*T([(sg * 0.075, y)])[0], S * 0.01, "#5A4A3A"))
    # five double courses of strings
    for k in range(5):
        for j in (-0.006, 0.006):
            x0 = -0.08 + k * 0.04 + j
            x1 = -0.03 + k * 0.015 + j
            out.append(pline(T([(x0, 0.78), (x1, -0.82)]), "#F6F2EA", 0.8, seed + 20 + k, 0.9, 1))
    return "".join(out)


def guiro(D, cx, cy, L, ang, seed):
    """Güiro: a long gourd with carved parallel grooves and a gentle neck; natural brown with a lighter belly."""
    pts = []
    for i in range(25):
        t = i / 24
        w = L * 0.13 * (math.sin(math.pi * t) ** 0.6) * (1.0 if t > 0.35 else 0.75 + 0.7 * t)
        pts.append((cx - L / 2 + L * t, cy - w))
    for i in range(24, -1, -1):
        t = i / 24
        w = L * 0.13 * (math.sin(math.pi * t) ** 0.6) * (1.0 if t > 0.35 else 0.75 + 0.7 * t)
        pts.append((cx - L / 2 + L * t, cy + w))
    pts = rot(pts, cx, cy, ang)
    out = [cast(D, cx + 6, cy + L * 0.14, L * 0.5, L * 0.06, "#0A0A20", 0.45, seed)]
    out.append(painted(D, pts, ("#F6D490", "#D09A50", "#7A4A1A"), seed, sdir=(0.3, 1), sk=0.2, angle=ang, n=24, inkw=1.8, hi=0.55))
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    g = []
    for k in range(26):
        t = 0.3 + k * 0.024
        a = rot([(cx - L / 2 + L * t, cy - L * 0.2)], cx, cy, ang)[0]
        b = rot([(cx - L / 2 + L * t + L * 0.01, cy + L * 0.2)], cx, cy, ang)[0]
        g.append(pline([a, b], "#4A2A0E", 1.4, seed + k, 0.7, 1))
    out.append(f'<g {cid}>{"".join(g)}</g>')
    for k, t in enumerate((0.55, 0.7)):
        x, y = rot([(cx - L / 2 + L * t, cy - L * 0.06)], cx, cy, ang)[0]
        out.append(disc(x, y, L * 0.018, "#2A1406"))
    return "".join(out)


def maraca(D, x, y, r, ang, seed, pal=FLAMB2, band="#2F6CC6"):
    hx, hy = x + math.cos(math.radians(ang)) * r * 2.6, y + math.sin(math.radians(ang)) * r * 2.6
    out = [taper([(x, y), (hx, hy)], r * 0.32, r * 0.24, "#8A5428")]
    out.append(painted(D, blob_pts(x, y, r, r * 0.92, seed, 0.03, 14), pal, seed, sdir=(0.6, 0.8), sk=0.2, n=10, inkw=1.6, hi=0.55))
    d = blob(x, y, r, r * 0.92, seed, 0.03, 14)
    cid = D.clip(f'<path d="{d}"/>')
    a = math.radians(ang + 90)
    out.append(f'<g {cid}>' + taper([(x + math.cos(a) * r * 1.2 - math.cos(math.radians(ang)) * r * 0.2, y + math.sin(a) * r * 1.2 - math.sin(math.radians(ang)) * r * 0.2),
                                      (x - math.cos(a) * r * 1.2 - math.cos(math.radians(ang)) * r * 0.2, y - math.sin(a) * r * 1.2 - math.sin(math.radians(ang)) * r * 0.2)], r * 0.3, r * 0.3, band) + '</g>')
    out.append(disc(x - r * 0.35, y - r * 0.35, r * 0.18, "#FFFFFF", 0.7))
    return "".join(out)


def pava(D, cx, cy, s, seed, band=ROJO):
    """The jíbaro's pava: a wide straw brim turned up at the front, a low rounded crown, a band."""
    out = [cast(D, cx + 6, cy + s * 0.35, s * 1.1, s * 0.18, "#0A0A20", 0.35, seed)]
    straw = ("#FFF0B8", "#E8C870", "#A8823A")
    brim = blob_pts(cx, cy, s, s * 0.34, seed, 0.03, 26)
    brim = [(x, y - (s * 0.16 if y < cy and abs(x - cx) < s * 0.5 else 0) * (1 - abs(x - cx) / (s * 0.5))) for x, y in brim]
    out.append(painted(D, brim, straw, seed, sdir=(0.4, 1), sk=0.12, angle=0, n=30, inkw=1.6, hi=0.4))
    d = smooth_closed(brim)
    cid = D.clip(f'<path d="{d}"/>')
    weave = []
    for k in range(1, 8):
        weave.append(ink(smooth_closed(ell_pts(cx, cy, s * k / 8, s * 0.34 * k / 8, 0, 360, 24)), straw[2], 1.0, seed + k, 1, 0.4))
    out.append(f'<g {cid}>{"".join(weave)}</g>')
    crown = [(cx - s * 0.42, cy - s * 0.02), (cx - s * 0.4, cy - s * 0.28), (cx - s * 0.2, cy - s * 0.42), (cx + s * 0.2, cy - s * 0.42), (cx + s * 0.4, cy - s * 0.28), (cx + s * 0.42, cy - s * 0.02)]
    out.append(painted(D, crown, straw, seed + 1, sdir=(0.7, 0.6), sk=0.18, angle=-90, n=16, inkw=1.6, hi=0.45))
    out.append(taper([(cx - s * 0.42, cy - s * 0.1), (cx, cy - s * 0.06), (cx + s * 0.42, cy - s * 0.1)], s * 0.1, s * 0.1, band[1]))
    out.append(taper([(cx - s * 0.42, cy - s * 0.13), (cx, cy - s * 0.09), (cx + s * 0.42, cy - s * 0.13)], s * 0.025, s * 0.025, band[0], 0.7))
    return "".join(out)


def light_string(D, x0, y0, x1, y1, sag, n, seed, cols=("#FF5A4A", "#FFD24A", "#4AC8FF", "#7AE07A", "#FF8AD8")):
    """Christmas lights: a dark wire and glowing bulbs hanging from it."""
    def pt(t):
        return x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)
    out = [pline([pt(i / 30) for i in range(31)], "#1A2A1A", 1.6, seed, 0.95, 1)]
    for i in range(n):
        x, y = pt((i + 0.5) / n)
        c = cols[i % len(cols)]
        out.append(D.glow(x, y + 9, 20, c, 0.55))
        out.append(f'<path d="{blob(x, y + 9, 4, 6.5, seed + i, 0.05, 10)}" fill="{c}"/>' + disc(x - 1.2, y + 7, 1.4, "#FFFFFF", 0.9))
        out.append(f'<rect x="{x - 2.5:.1f}" y="{y - 1:.1f}" width="5" height="5" fill="#2A3A2A"/>')
    return "".join(out)


@design("parranda")
def parranda():
    D = Doc2("prpr")
    out = [sky(D, [(0, "#0E1640"), (0.7, "#1E2A62"), (1, "#2A3470")], 1601, 240, ["#2A3A80", "#0A1030"], 50)]
    rnd = random.Random(1602)
    for _ in range(46):
        out.append(disc(rnd.uniform(0, 600), rnd.uniform(0, 220), rnd.uniform(0.6, 1.8), "#FFF6D8", rnd.uniform(0.4, 1)))
    out.append(sparkle(548, 196, 10, "#FFF6C8", 0.95) + sparkle(60, 190, 8, "#FFF6C8", 0.9))
    # the house front: a mint concrete wall in lamplight
    out.append(painted(D, rect_pts(-10, 222, 610, 520, 30, 1604, 0.5), ("#B8E8D0", "#7CC4A8", "#3A7A62"), 1604, sdir=(0.2, 1), sk=0.06, angle=-88, n=60, inkw=1.6, hi=0.2))
    out.append(f'<rect x="-10" y="222" width="620" height="300" fill="{D.lin([(0, "#0A1030", 0.45), (0.5, "#0A1030", 0.15), (1, "#0A1030", 0.35)])}"/>')
    out.append(f'<path d="{hg.org_rect(-10, 210, 620, 18, 1605, 0.5, 30, 1)}" fill="#F2F0E8"/>')
    out.append(light_string(D, -10, 226, 300, 226, 26, 9, 1606))
    out.append(light_string(D, 300, 226, 610, 226, 22, 9, 1607))
    # window with Miami louvres, lit from inside
    wx, wy, ww, wh = 70, 292, 150, 118
    out.append(D.glow(wx + ww / 2, wy + wh / 2, 150, "#FFC860", 0.45))
    out.append(f'<path d="{hg.org_rect(wx - 8, wy - 8, ww + 16, wh + 16, 1608, 0.5, 14, 1)}" fill="#F2F0E8"/>')
    out.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="#FFE29A"/>')
    for k in range(9):
        y = wy + 6 + k * 12.5
        out.append(f'<path d="M {wx + 2} {y:.1f} L {wx + ww - 2} {y:.1f} L {wx + ww - 2} {y + 6:.1f} L {wx + 2} {y + 6:.1f} Z" fill="#C8CCD6" opacity="0.85"/>')
        out.append(pline([(wx + 2, y + 6), (wx + ww - 2, y + 6)], "#8A90A0", 1, 1609 + k, 0.8, 1))
    for x in (wx + ww / 3, wx + 2 * ww / 3):
        out.append(f'<path d="M {x:.1f} {wy} L {x:.1f} {wy + wh}" stroke="#F2F0E8" stroke-width="4"/>')
    # rejas over the window
    out.append(rejas(D, wx - 4, wy - 4, wx + ww + 4, wy + wh + 4, 1610, col="#F8F8F8", cell=52))
    # the door, ajar, warm light spilling out
    dx0, dx1, dy0 = 344, 482, 268
    out.append(D.glow(410, 520, 200, "#FFC860", 0.4, ry=60))
    out.append(f'<path d="{hg.org_rect(dx0 - 12, dy0 - 12, dx1 - dx0 + 24, 520 - dy0 + 12, 1611, 0.5, 14, 1)}" fill="#F2F0E8"/>')
    out.append(f'<rect x="{dx0}" y="{dy0}" width="{dx1 - dx0}" height="{520 - dy0}" fill="#FFD27A"/>')
    out.append(f'<rect x="{dx0}" y="{dy0}" width="{dx1 - dx0}" height="{520 - dy0}" fill="{D.rad([(0, "#FFF4C8", 0.9), (1, "#F2A23A", 0.6)], cx=0.3, cy=0.5, r=0.8)}"/>')
    door = [(dx0 + 44, dy0), (dx1, dy0 - 10), (dx1, 530), (dx0 + 44, 520)]
    out.append(painted(D, door, ("#E8806A", "#C04A3A", "#6A1E14"), 1612, sdir=(1, 0.2), sk=0.1, angle=-88, n=40, inkw=2, hi=0.3))
    for y0, y1 in ((dy0 + 16, dy0 + 110), (dy0 + 130, 500)):
        out.append(f'<path d="{pd([(dx0 + 58, y0), (dx1 - 12, y0 - 6), (dx1 - 12, y1 - 4), (dx0 + 58, y1)])}" fill="none" stroke="#7A2418" stroke-width="2.4" opacity="0.7"/>')
    out.append(disc(dx0 + 54, 400, 5, "#F6C21C"))
    # a little wreath on the door
    wcx, wcy = 430, 316
    for k in range(22):
        a = 2 * math.pi * k / 22
        out.append(leaf_simple(D, wcx + math.cos(a) * 22, wcy + math.sin(a) * 22, 16, 5, math.degrees(a) + 100, ("#7AB86A", "#2E6A2E", "#143A14"), 1613 + k, vein=False, inkw=0.6))
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.3
        out.append(disc(wcx + math.cos(a) * 22, wcy + math.sin(a) * 22, 4, "#E8302A"))
    out.append(ribbon_bow(D, wcx, wcy + 26, 14, 1640))
    # porch floor
    out.append(tile_floor(D, 520, 600, 1641, a="#A85A4A", b="#3A5A7A", ground="#D8CCB8", cell=34, squash=0.45))
    out.append(f'<rect y="520" width="600" height="80" fill="#1A1430" opacity="0.25"/>')
    out.append(f'<rect y="516" width="600" height="6" fill="#2A1A10" opacity="0.5"/>')
    # the pava on a nail, the cuatro leaning on the wall, güiro and maracas on the floor
    out.append(disc(282, 262, 3, "#3A3A42"))
    out.append(pava(D, 282, 296, 56, 1650))
    out.append(cuatro(D, 262, 368, 170, 14, 1651))
    out.append(guiro(D, 172, 538, 184, -14, 1652))
    out.append(maraca(D, 430, 560, 26, -160, 1653))
    out.append(maraca(D, 500, 548, 24, -118, 1654, pal=("#7AD0A0", "#1F9A5A", "#0E5A30"), band="#F6C21C"))
    # music drifting out the door
    for k, (x, y, sc) in enumerate(((330, 238, 1.0), (498, 250, 0.9), (220, 250, 0.8))):
        out.append(f'<path d="M {x} {y} l 0 {-22 * sc:.1f} l {12 * sc:.1f} {4 * sc:.1f}" stroke="#FFE8A0" stroke-width="2.4" fill="none"/>'
                   f'<ellipse cx="{x - 4 * sc:.1f}" cy="{y}" rx="{5.5 * sc:.1f}" ry="{4 * sc:.1f}" fill="#FFE8A0" transform="rotate(-20 {x - 4 * sc:.1f} {y})"/>')
    # lettering
    out.append(letters(D, 300, 120, "parranda", SERIF_IT, 120, "#FFE6A8", ["#FFF4D0", "#F2C878", "#FFFFFF"], 1660, max_w=430,
                       shadow="#060A20", soff=(0.022, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 166, "¡ASALTO NAVIDEÑO!", "#F6A0B8", font=JOS, size=20, ls=6, line_w=30, gap=12))
    return finish_b(D, out, 1661, "#FFFFFF", 0.45)


# ================================================================ 17. boricua — the flag, waving
def pr_flag(D, x0, y0, W, H, seed, amp=18, waves=1.25, phase=0.3, red=ROJO[1], blue="#2F6CC6", white="#FFFDF6", inkw=2.0):
    """The Puerto Rican flag as a waving cloth: five stripes, the blue triangle and the white star, with folds lit
    and shaded along the wave."""
    def F(u, v):
        wv = amp * math.sin(2 * math.pi * (waves * u) + phase) * (0.25 + 0.75 * u)
        wv += amp * 0.3 * math.sin(2 * math.pi * (2.3 * u) + phase * 2) * u
        return (x0 + u * W - 8 * u * u, y0 + v * H * (1 - 0.08 * u) + wv + u * H * 0.05)

    N = 40
    us = [i / N for i in range(N + 1)]
    out = []
    outline = [F(u, 0) for u in us] + [F(u, 1) for u in reversed(us)]
    od = smooth_closed(outline)
    out.append(f'<path d="{od}" fill="#2A0A0A" opacity="0.18" transform="translate(8 12)"/>')
    for i in range(5):
        poly = [F(u, i / 5) for u in us] + [F(u, (i + 1) / 5) for u in reversed(us)]
        out.append(f'<path d="{pd(poly)}" fill="{red if i % 2 == 0 else white}"/>')
    tip = 0.42
    tri = [F(0, 0)] + [F(tip * t / 10, 0.5 * t / 10) for t in range(1, 11)] + [F(tip * (1 - t / 10), 0.5 + 0.5 * t / 10) for t in range(1, 11)]
    out.append(f'<path d="{pd(tri)}" fill="{blue}"/>')
    sx, sy = F(tip / 3, 0.5)
    out.append(f'<path d="{star_d(sx, sy, H * 0.14)}" fill="{white}"/>')
    # folds: light and shade bands following the slope of the wave
    cid = D.clip(f'<path d="{od}"/>')
    sh = []
    for i in range(N):
        u = (us[i] + us[i + 1]) / 2
        slope = math.cos(2 * math.pi * waves * u + phase)
        q = [F(us[i], 0), F(us[i + 1], 0), F(us[i + 1], 1), F(us[i], 1)]
        q = [(q[0][0], q[0][1] - 4), (q[1][0] + 1, q[1][1] - 4), (q[2][0] + 1, q[2][1] + 4), (q[3][0], q[3][1] + 4)]
        if slope > 0:
            sh.append(f'<path d="{pd(q)}" fill="#FFFFFF" opacity="{0.22 * slope:.2f}"/>')
        else:
            sh.append(f'<path d="{pd(q)}" fill="#1A0A20" opacity="{0.32 * -slope:.2f}"/>')
    sh.append(strokes(D.nid(), od, bbox(outline), ["#FFFFFF", "#1A0A20"], seed, n=120, angle=-80, length=(14, 40), width=(1, 3), opacity=(0.05, 0.16)))
    out.append(f'<g {cid}>{"".join(sh)}</g>')
    out.append(ink(od, INK, inkw, seed + 1, 2, 0.7))
    return "".join(out), F


@design("boricua")
def boricua():
    D = Doc2("prbo")
    out = [sky(D, [(0, "#5AA4E4"), (0.6, "#A8D4F2"), (1, "#F6EAD4")], 1701, 600, ["#FFFFFF", "#8EC4EC", "#F8E8D0"], 70)]
    out.append(soft_glow(D, 470, 250, 260, "#FFF6E0", 0.55))
    out.append(puff_cloud(D, 500, 210, 130, 1702))
    # the island below: sea, a green coast with palms, a flamboyán and a little house
    out.append(sea(D, 486, 600, [(0, "#4CC0CC"), (1, "#1F8AA8")], 1703, ["#AEEAF0", "#1E6A9A", "#FFFFFF"], 30))
    out.append(hill(D, ridge([(120, 520), (260, 494), (400, 502), (520, 486), (620, 494)], 1708, 6, 3), 640, ("#A8D27A", "#6AA84A", "#2E6A2A"), 1709, inkw=1.4, inkop=0.4))
    out.append(palm(D, (520, 500), (536, 440), 1716, L=34, width=6, nuts=False))
    out.append(palm(D, (556, 500), (566, 452), 1717, L=28, width=5, nuts=False))
    out.append(casita(D, 400, 512, 46, 26, 1718, wall=PASTELS[1]))
    out.append(dab_crown(D, 300, 486, 34, 14, [FLAMB, FLAMB2], 1719, n=50, size=(3, 6), inkw=0))
    out.append(taper([(300, 512), (302, 494)], 4, 3, "#5A3A22"))
    # the flagpole and its golden finial
    px = 92
    out.append(taper([(px, 610), (px, 196)], 9, 7, "#C8CCD4") + taper([(px - 2, 610), (px - 2, 196)], 2.6, 2, "#FFFFFF", 0.8) + taper([(px + 3, 610), (px + 3, 196)], 2, 2, "#6A707A", 0.7))
    out.append(painted(D, blob_pts(px, 186, 12, 12, 1704, 0.03, 14), ("#FFE89A", "#F2B83A", "#A8700A"), 1704, sk=0.25, n=5, inkw=1.4, hi=0.6))
    # the flag
    fl, F = pr_flag(D, px + 4, 210, 430, 260, 1705, amp=24, waves=1.15, phase=0.6)
    out.append(fl)
    for k, v in enumerate((0.03, 0.97)):
        x, y = F(0, v)
        out.append(disc(px + 4, y, 4, "#C8CCD4") + ink(blob(px + 4, y, 4, 4, 1706 + k, 0.1, 8), "#6A707A", 1, 1706 + k, 1, 0.8))
    # breeze and blossoms
    for k, (x, y) in enumerate(((520, 236), (548, 300), (530, 420))):
        out.append(pline([(x - 30, y), (x, y - 4), (x + 20, y + 2)], "#FFFFFF", 2.4, 1710 + k, 0.7, 1))
    rnd = random.Random(1715)
    for _ in range(12):
        x, y = rnd.uniform(140, 560), rnd.uniform(410, 470)
        out.append(f'<path d="{blob(x, y, 5, 3, rnd.randint(0, 999), 0.2, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#E8401E", "#F26A1E"])}" opacity="0.9"/>')
    # lettering
    out.append(letters(D, 300, 140, "Boricua", SERIF_IT, 140, "#123A7A", ["#2E5AA0", "#0A2456", "#3E6AB0"], 1720, max_w=420,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#C8DCF6"))
    band = rect_pts(110, 510, 490, 546, 20, 1722, 0.8)
    out.append(painted(D, band, ("#FFFDF4", "#F6EEDC", "#C8B898"), 1722, sk=0.1, angle=0, n=12, inkw=1.4, hi=0.3))
    out.append(label(300, 536, "DE AQUÍ, DE ALLÁ, DE CORAZÓN", JOS, 19, "#8A1410", ls=3, max_w=360))
    return finish_b(D, out, 1721)


# ================================================================ 18. mi isla — a painted map of the island
PR_COAST = [(-67.27, 18.37), (-67.22, 18.42), (-67.16, 18.47), (-67.10, 18.515), (-66.95, 18.49), (-66.82, 18.48), (-66.70, 18.48), (-66.55, 18.48),
            (-66.45, 18.487), (-66.30, 18.475), (-66.20, 18.47), (-66.10, 18.468), (-66.02, 18.45), (-65.95, 18.44), (-65.80, 18.40), (-65.70, 18.39),
            (-65.62, 18.38), (-65.63, 18.30), (-65.65, 18.25), (-65.70, 18.19), (-65.75, 18.12), (-65.82, 18.04), (-65.92, 17.97), (-66.02, 17.96),
            (-66.10, 17.95), (-66.22, 17.94), (-66.32, 17.95), (-66.45, 17.97), (-66.55, 17.98), (-66.63, 17.985), (-66.72, 17.97), (-66.80, 17.96),
            (-66.92, 17.94), (-67.02, 17.95), (-67.10, 17.95), (-67.19, 17.93), (-67.21, 17.97), (-67.19, 18.05), (-67.18, 18.12), (-67.16, 18.20),
            (-67.20, 18.26), (-67.24, 18.31)]
VIEQUES = [(-65.58, 18.12), (-65.50, 18.15), (-65.42, 18.16), (-65.30, 18.15), (-65.26, 18.12), (-65.32, 18.09), (-65.42, 18.085), (-65.53, 18.09)]
CULEBRA = [(-65.34, 18.33), (-65.28, 18.345), (-65.23, 18.32), (-65.25, 18.29), (-65.31, 18.295)]


def geo(lon, lat):
    return (296 + (lon + 66.27) * 228, 386 - (lat - 18.22) * 218)


def tiny_garita(D, x, base, s, seed):
    out = [painted(D, rect_pts(x - 5 * s, base - 14 * s, x + 5 * s, base, 6, seed, 0.2), ("#F6D8A8", "#D8A868", "#8A5A3A"), seed, sk=0.25, n=3, inkw=1, hi=0.3)]
    out.append(painted(D, [(x - 6 * s, base - 14 * s), (x - 4 * s, base - 20 * s), (x, base - 23 * s), (x + 4 * s, base - 20 * s), (x + 6 * s, base - 14 * s)],
                       ("#F6D8A8", "#D8A868", "#8A5A3A"), seed + 1, sk=0.25, n=2, inkw=1, hi=0.3))
    out.append(f'<rect x="{x - 1 * s:.1f}" y="{base - 11 * s:.1f}" width="{2 * s:.1f}" height="{6 * s:.1f}" fill="#3A2418"/>')
    return "".join(out)


def tiny_lighthouse(x, base, s):
    return (f'<path d="M {x - 4 * s:.1f} {base} L {x - 2.6 * s:.1f} {base - 20 * s:.1f} L {x + 2.6 * s:.1f} {base - 20 * s:.1f} L {x + 4 * s:.1f} {base} Z" fill="#FFFFFF" stroke="#3A2418" stroke-width="1"/>'
            f'<rect x="{x - 3.4 * s:.1f}" y="{base - 13 * s:.1f}" width="{6.8 * s:.1f}" height="{3 * s:.1f}" fill="#D52B1E"/>'
            f'<rect x="{x - 2.4 * s:.1f}" y="{base - 25 * s:.1f}" width="{4.8 * s:.1f}" height="{5 * s:.1f}" fill="#F6D24A" stroke="#3A2418" stroke-width="1"/>'
            f'<path d="M {x - 3 * s:.1f} {base - 25 * s:.1f} L {x:.1f} {base - 29 * s:.1f} L {x + 3 * s:.1f} {base - 25 * s:.1f} Z" fill="#3A2418"/>')


def compass(D, cx, cy, r, seed):
    out = [disc(cx, cy, r * 0.62, "#FFF6E0", 0.9), ink(blob(cx, cy, r * 0.62, r * 0.62, seed, 0.01, 20), "#8A5A3A", 1.4, seed, 1, 0.7)]
    for k in range(8):
        a = math.radians(k * 45 - 90)
        L = r if k % 2 == 0 else r * 0.55
        tip = (cx + math.cos(a) * L, cy + math.sin(a) * L)
        l = (cx + math.cos(a - 0.5) * r * 0.16, cy + math.sin(a - 0.5) * r * 0.16)
        rr = (cx + math.cos(a + 0.5) * r * 0.16, cy + math.sin(a + 0.5) * r * 0.16)
        out.append(f'<path d="{pd([(cx, cy), l, tip])}" fill="{"#D52B1E" if k == 0 else "#8A5A3A"}"/><path d="{pd([(cx, cy), rr, tip])}" fill="{"#F28A7A" if k == 0 else "#D8B48A"}"/>')
    out.append(f'<text x="{cx}" y="{cy - r - 6}" text-anchor="middle" {JOS} font-size="18" fill="#8A3A1E">N</text>')
    return "".join(out)


def sea_turtle(D, cx, cy, s, ang, seed):
    out = []
    for sg in (-1, 1):
        for k, (dy, L) in enumerate(((-0.35, 0.9), (0.45, 0.6))):
            fl = rot([(cx + sg * s * 0.4, cy + dy * s), (cx + sg * s * (0.4 + L), cy + dy * s - s * 0.2 * (1 if k == 0 else -0.3)), (cx + sg * s * (0.3 + L * 0.6), cy + dy * s + s * 0.18)], cx, cy, ang)
            out.append(f'<path d="{smooth_closed(fl)}" fill="#5A8A4A"/>')
    out.append(f'<path d="{smooth_closed(rot(blob_pts(cx, cy - s * 0.85, s * 0.22, s * 0.26, seed, 0.05, 10), cx, cy, ang))}" fill="#6A9A5A"/>')
    sh = rot(blob_pts(cx, cy, s * 0.55, s * 0.7, seed + 1, 0.04, 14), cx, cy, ang)
    out.append(painted(D, sh, ("#C8A060", "#8A6A30", "#4A3A14"), seed + 1, sk=0.2, n=6, inkw=1.2, hi=0.4))
    for k in range(3):
        out.append(f'<path d="{smooth_closed(rot(blob_pts(cx, cy - s * 0.3 + k * s * 0.3, s * 0.16, s * 0.12, seed + 3 + k, 0.1, 8), cx, cy, ang))}" fill="#5A4A1E" opacity="0.5"/>')
    return "".join(out)


@design("mi-isla")
def mi_isla():
    D = Doc2("prmi")
    out = [sky(D, [(0, "#7ED6E0"), (0.5, "#4CC0CC"), (1, "#2EA0B8")], 1801, 600, ["#AEEAF0", "#2E98B0", "#FFFFFF"], 120, angle=-2, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 300, 390, 300, "#E8FFF8", 0.35))
    out.append(wave_lines(1802, (40, 230, 560, 560), ["#E8FCFF", "#B8F0F4"], 60, (10, 22), 2.0, 2.5, (0.35, 0.7)))
    # shallow reef light around the coast
    coast = [geo(*p) for p in PR_COAST]
    vq = [geo(*p) for p in VIEQUES]
    cu = [geo(*p) for p in CULEBRA]
    for poly in (coast, vq, cu):
        out.append(f'<path d="{smooth_closed(poly)}" fill="#BFF4EC" stroke="#BFF4EC" stroke-width="20" stroke-linejoin="round" opacity="0.6"/>')
        out.append(f'<path d="{smooth_closed(poly)}" fill="#F6E6B8" stroke="#F6E6B8" stroke-width="7" stroke-linejoin="round"/>')
    # the island: painted green, darker inland
    out.append(painted(D, coast, ("#B8DC80", "#6EAA4A", "#2E6A2A"), 1803, sdir=(0.3, 1), sk=0.06, angle=-10, n=120, slen=(10, 30), sw=(1.5, 4), inkw=2, hi=0.3))
    for poly, sd in ((vq, 1804), (cu, 1805)):
        out.append(painted(D, poly, ("#C8E090", "#7AB452", "#3A7A2E"), sd, sk=0.1, n=10, inkw=1.6, hi=0.3))
    cd = smooth_closed(coast)
    cid = D.clip(f'<path d="{cd}"/>')
    inner = [f'<path d="{blob(*geo(-66.5, 18.17), 140, 26, 1806, 0.15, 16)}" fill="#3E7A36" opacity="0.4"/>']
    # the cordillera central and the sierra de luquillo as little painted peaks
    rnd = random.Random(1807)
    peaks = [(-67.0, 18.18, 14), (-66.88, 18.19, 18), (-66.76, 18.17, 20), (-66.64, 18.17, 24), (-66.52, 18.16, 22), (-66.40, 18.15, 20),
             (-66.28, 18.13, 18), (-66.16, 18.10, 16), (-66.06, 18.08, 14), (-65.96, 18.09, 12)]
    for lon, lat, h in peaks:
        x, y = geo(lon, lat)
        w = h * 1.4
        pk = [(x - w, y + 4), (x - w * 0.3, y - h * 0.7), (x, y - h), (x + w * 0.35, y - h * 0.6), (x + w, y + 4)]
        inner.append(painted(D, pk, ("#9ACB7A", "#4E8A42", "#1E4E22"), int(lon * -100), sdir=(1, 0.3), sk=0.3, angle=-60, n=4, inkw=1.0, inkop=0.5, hi=0.4))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # el yunque: rainforest crown, a waterfall
    yx, yy = geo(-65.79, 18.30)
    out.append(dab_crown(D, yx, yy, 26, 14, [SELVA, ("#5AA84A", "#1E6A2E", "#0A3A1A")], 1808, n=50, size=(3, 6), inkw=1.0))
    out.append(taper([(yx + 4, yy - 2), (yx + 5, yy + 14)], 3, 2, "#E8FCFF", 0.95))
    # flamboyán trees and palms dotted around
    for k, (lon, lat) in enumerate(((-66.70, 18.30), (-66.35, 18.30), (-66.90, 18.05))):
        x, y = geo(lon, lat)
        out.append(taper([(x, y + 8), (x, y)], 2.4, 2, "#5A3A22"))
        out.append(f'<path d="{blob(x, y - 3, 11, 5, 1810 + k, 0.2, 10)}" fill="#E8401E"/><path d="{blob(x - 3, y - 5, 6, 2.6, 1813 + k, 0.2, 8)}" fill="#FF9466"/>')
    for k, (lon, lat) in enumerate(((-65.95, 18.43), (-66.62, 18.0), (-67.18, 18.38), (-65.67, 18.30), (-65.40, 18.13))):
        x, y = geo(lon, lat)
        out.append(palm(D, (x, y + 4), (x + 2, y - 14), 1816 + k, L=10, width=2.6, nuts=False, rings=False))
    # landmarks: the garita in san juan, the lighthouse at cabo rojo, the coquí in the heart of the island
    out.append(tiny_garita(D, *geo(-66.12, 18.48), 1.3, 1825))
    out.append(tiny_lighthouse(*geo(-67.19, 17.94), 1.1))
    out.append(coqui(D, *geo(-66.48, 18.28), 0.5, 1826, sing=True))
    # sea life and a sailboat, a compass
    out.append(sea_turtle(D, *geo(-65.62, 18.56), 16, 30, 1827))
    sx, sy = geo(-66.95, 17.78)
    out.append(f'<path d="M {sx} {sy} l 0 -34 l 22 30 Z" fill="#FFFFFF" stroke="#3A2418" stroke-width="1.2"/><path d="M {sx - 2} {sy - 30} l -14 26 l 14 0 Z" fill="#F6D24A" stroke="#3A2418" stroke-width="1.2"/>'
               f'<path d="M {sx - 20} {sy + 2} l 46 0 l -8 9 l -30 0 Z" fill="#D52B1E" stroke="#3A2418" stroke-width="1.2"/>')
    out.append(pline([(sx - 30, sy + 14), (sx + 30, sy + 14)], "#FFFFFF", 1.6, 1828, 0.7, 1))
    out.append(compass(D, 506, 516, 28, 1829))
    # place names (small, on the sea where they read)
    for name, lon, lat, dy in (("San Juan", -66.04, 18.46, -40), ("Ponce", -66.62, 17.98, 26)):
        x, y = geo(lon, lat)
        out.append(disc(x, y, 3.4, "#D52B1E") + label(x, y + dy, name, JOS, 17, "#0E3A4E", ls=1))
    vx, vy = geo(-65.42, 18.07)
    out.append(label(vx, vy + 24, "Vieques", JOS, 16, "#0E3A4E", ls=1))
    cx_, cy_ = geo(-65.28, 18.33)
    out.append(label(cx_ - 26, cy_ - 16, "Culebra", JOS, 16, "#0E3A4E", ls=1))
    out.append(label(206, 258, "OCÉANO ATLÁNTICO", JOS, 16, "#E8FCFF", ls=4))
    out.append(label(300, 512, "MAR CARIBE", JOS, 16, "#E8FCFF", ls=6))
    # lettering
    out.append(letters(D, 300, 140, "Mi Isla", SERIF_IT, 132, "#FFFDF0", ["#FFFFFF", "#E8F8F0", "#FFF6D8"], 1840, max_w=380,
                       shadow="#0E5A6A", soff=(0.022, 0.036), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 184, "ISLA DEL ENCANTO", "#FFF6D8", font=JOS, size=19, ls=7, line_w=34, gap=14, line="#F6C21C"))
    return finish_b(D, out, 1841, "#0E3A4E", 0.6)


# ================================================================ 19. chinas — sweet oranges, one peeled the roadside way
def china(D, cx, cy, r, seed, rot_=0):
    """A ripe china: dimpled orange skin, a shaded side, a highlight and a little green stem scar."""
    rnd = random.Random(seed)
    pts = blob_pts(cx, cy, r, r * 0.95, seed, 0.03, 16)
    out = [painted(D, pts, ("#FFC060", "#F28A1E", "#A8460A"), seed, sdir=(0.6, 0.8), sk=0.2, angle=-50, n=int(r * 0.8), inkw=1.6, hi=0.5, hik=0.1)]
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    dots = "".join(disc(cx + rnd.uniform(-r, r), cy + rnd.uniform(-r, r), rnd.uniform(0.6, 1.3), rnd.choice(["#C8640E", "#FFD08A"]), 0.6) for _ in range(int(r * 2.2)))
    out.append(f'<g {cid}>{dots}</g>')
    a = math.radians(rot_ - 60)
    sx, sy = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55
    out.append(disc(sx, sy, r * 0.09, "#6A7A2A") + disc(sx, sy, r * 0.04, "#3A4A14"))
    out.append(f'<path d="{blob(cx - r * 0.38, cy - r * 0.4, r * 0.22, r * 0.12, seed + 3, 0.2, 10, -40)}" fill="#FFF0C8" opacity="0.7"/>')
    return "".join(out)


def peeled_china(D, cx, cy, r, seed):
    """The street-vendor china: the skin shaved off by the hand-crank peeler, leaving a pale yellow, faintly
    orange ball with spiral peeler marks, the top sliced off to show the juice, and one long ribbon of peel."""
    out = [cast(D, cx + 6, cy + r * 0.95, r * 1.1, r * 0.2, "#3A2A06", 0.4, seed)]
    rib = []
    for i in range(110):
        t = i / 109
        ang = t * 6 * math.pi
        rr = r * (0.55 + 0.35 * t)
        rib.append((cx + r * 0.4 + t * r * 2.0 + math.cos(ang) * rr * 0.5, cy + r * 0.3 + t * r * 0.7 + math.sin(ang) * rr * 0.22))
    out.append(taper(rib, r * 0.24, r * 0.18, "#F07A14"))
    out.append(taper([(x - 1, y - 2) for x, y in rib], r * 0.08, r * 0.06, "#FFB860", 0.8))
    out.append(taper([(x + 1, y + 2.5) for x, y in rib], r * 0.07, r * 0.05, "#FFF6E0", 0.9))
    pts = blob_pts(cx, cy, r, r * 0.96, seed, 0.025, 16)
    out.append(painted(D, pts, ("#FFEAB0", "#F8C870", "#C0782A"), seed, sdir=(0.6, 0.8), sk=0.2, angle=-20, n=int(r * 0.6), inkw=1.6, hi=0.45))
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    seg = [f'<path d="{blob(cx + r * 0.25, cy + r * 0.25, r * 0.7, r * 0.55, seed + 9, 0.2, 12)}" fill="#F29A2A" opacity="0.35"/>']
    for k in range(9):
        y = cy - r + k * r * 0.25
        seg.append(pline([(cx - r, y + 6), (cx, y - 2), (cx + r, y - 10)], "#F2C878", 1.4, seed + k, 0.55, 1))
    out.append(f'<g {cid}>{"".join(seg)}</g>')
    tx, ty = cx - r * 0.05, cy - r * 0.62
    cap = smooth_closed(ell_pts(tx, ty, r * 0.48, r * 0.17, 0, 360, 20))
    out.append(f'<path d="{cap}" fill="#FFF4D0"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(tx, ty, r * 0.4, r * 0.13, 0, 360, 20))}" fill="#F6A030"/>')
    for k in range(10):
        a = 2 * math.pi * k / 10
        out.append(pline([(tx, ty), (tx + math.cos(a) * r * 0.4, ty + math.sin(a) * r * 0.13)], "#FFE0A0", 1.2, seed + 20 + k, 0.8, 1))
    out.append(disc(tx - r * 0.12, ty - r * 0.03, r * 0.05, "#FFFFFF", 0.8))
    out.append(ink(cap, "#B8862A", 1.2, seed + 30, 1, 0.6))
    return "".join(out)


def huacal(D, x0, y0, x1, y1, seed, pal=("#E8C890", "#C09A5A", "#6E4E22")):
    """Slatted wooden produce crate seen from the front."""
    out = []
    h = (y1 - y0)
    for k in range(3):
        sy0 = y0 + k * h / 3 + 3
        out.append(painted(D, rect_pts(x0, sy0, x1, sy0 + h / 3 - 8, 20, seed + k, 0.5), pal, seed + k, sdir=(0, 1), sk=0.2, angle=0, n=16, inkw=1.4, hi=0.4))
    for x in (x0 + 4, x1 - 22):
        out.append(painted(D, rect_pts(x, y0 - 6, x + 18, y1 + 2, 10, seed + int(x), 0.4), pal, seed + int(x), sdir=(1, 0), sk=0.2, angle=-90, n=8, inkw=1.4, hi=0.4))
    return "".join(out)


@design("chinas")
def chinas():
    D = Doc2("prch")
    out = [sky(D, [(0, "#6AB4E8"), (0.6, "#B8E0F2"), (1, "#F2F0D8")], 1901, 420, ["#FFFFFF", "#8EC8EE"], 50)]
    out.append(puff_cloud(D, 480, 250, 140, 1902))
    out.append(hill(D, ridge([(-20, 380), (140, 340), (300, 368), (460, 330), (620, 360)], 1903, 10, 4), 600, ("#9ACB7A", "#5E9A4E", "#2E6A2E"), 1904, inkw=1, inkop=0.3))
    out.append(soft_glow(D, 300, 420, 300, "#FFF4D0", 0.4))
    # roadside table with an oilcloth
    out.append(painted(D, rect_pts(-10, 440, 610, 610, 30, 1905, 0.5), ("#FFE0D0", "#F2A8A0", "#B05A5A"), 1905, sdir=(0, 1), sk=0.05, angle=0, n=40, inkw=1.6, hi=0.2))
    out.append(cloth(D, [(-10, 440), (610, 440), (610, 610), (-10, 610)], "#D52B1E", 1906, cell=16, light=(0, 0, 0.3, 1), inkw=0))
    out.append(f'<rect y="436" width="600" height="8" fill="#5A1A0A" opacity="0.35"/>')
    # the crate heaped with chinas
    cx0, cy0, cx1, cy1 = 72, 360, 336, 500
    rnd = random.Random(1907)
    heap = []
    for row, (y, n, off) in enumerate(((356, 5, 0), (330, 4, 26), (306, 3, 52))):
        for k in range(n):
            heap.append((cx0 + 34 + off + k * 52 + rnd.uniform(-4, 4), y + rnd.uniform(-4, 4), rnd.uniform(26, 30)))
    for k, (x, y, r) in enumerate(sorted(heap, key=lambda h: h[1])):
        out.append(china(D, x, y, r, 1910 + k, rnd.uniform(-40, 40)))
    out.append(cast(D, 200, 500, 160, 12, strength=0.45, seed=1930))
    out.append(huacal(D, cx0, cy0, cx1, cy1, 1931))
    # leaves tucked in the heap
    for k, (x, y, a) in enumerate(((112, 296, -140), (250, 286, -40), (300, 330, 10))):
        out.append(leaf_simple(D, x, y, 40, 12, a, ("#8ACB6A", "#2E7A3A", "#0E4A1E"), 1935 + k, vein=True, inkw=1.1))
    # the peeled china and a whole one on the table
    out.append(peeled_china(D, 392, 440, 54, 1940))
    # a halved china showing its juicy segments
    hx, hy, hr = 470, 548, 34
    out.append(cast(D, hx + 4, hy + 10, hr * 1.1, hr * 0.3, "#3A2A06", 0.35, 1946))
    out.append(painted(D, ell_pts(hx, hy, hr, hr * 0.62, 0, 360, 24), ("#FFC060", "#F28A1E", "#A8460A"), 1947, sk=0.15, n=10, inkw=1.6, hi=0.4))
    out.append(f'<path d="{smooth_closed(ell_pts(hx, hy - 4, hr * 0.92, hr * 0.52, 0, 360, 24))}" fill="#FFF4D8"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(hx, hy - 4, hr * 0.82, hr * 0.44, 0, 360, 24))}" fill="#F8A032"/>')
    for k in range(10):
        a = 2 * math.pi * k / 10
        out.append(pline([(hx, hy - 4), (hx + math.cos(a) * hr * 0.82, hy - 4 + math.sin(a) * hr * 0.44)], "#FFE6B0", 1.6, 1948 + k, 0.9, 1))
    out.append(disc(hx, hy - 4, 3, "#FFF4D8") + f'<path d="{blob(hx - 12, hy - 12, 8, 3, 1958, 0.2, 8, -20)}" fill="#FFFFFF" opacity="0.7"/>')
    # hand-lettered cardboard sign

    sg = rot(rect_pts(366, 286, 548, 360, 20, 1942, 1.4), 457, 323, 5)
    out.append(cast(D, 462, 366, 92, 8, strength=0.35, seed=1943))
    out.append(painted(D, sg, ("#E8C890", "#C8A060", "#8A6430"), 1942, sk=0.1, n=14, inkw=1.6, hi=0.3))
    out.append(f'<text x="457" y="335" text-anchor="middle" {ANTON} font-size="34" fill="#D52B1E" transform="rotate(5 457 323)">¡DULCES!</text>')

    # lettering
    out.append(letters(D, 300, 132, "chinas", SERIF_IT, 140, "#E8641A", ["#FF8A3A", "#B8460A", "#FFA860"], 1950, max_w=400,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#FFE0B0"))
    out.append(ruled(300, 176, "NO SON NARANJAS", "#1E5E3A", font=JOS, size=20, ls=7, line_w=34, gap=14))
    return finish_b(D, out, 1951)


# ================================================================ 20. ¡capicú! — dominoes on the plaza table, top-down
PIPS = {0: [], 1: [(0, 0)], 2: [(-0.5, -0.5), (0.5, 0.5)], 3: [(-0.5, -0.5), (0, 0), (0.5, 0.5)], 4: [(-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)],
        5: [(-0.5, -0.5), (0.5, -0.5), (0, 0), (-0.5, 0.5), (0.5, 0.5)], 6: [(-0.5, -0.55), (0.5, -0.55), (-0.5, 0), (0.5, 0), (-0.5, 0.55), (0.5, 0.55)]}


def domino(D, cx, cy, s, a, b, ang, seed, down=False):
    """One domino tile seen from above: ivory face, centre bar and brass pin, the two halves' pips."""
    w, h = s, s * 2
    pts = rot(rect_pts(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 8, seed, 0.3), cx, cy, ang)
    out = [f'<path d="{smooth_closed(rot(rect_pts(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 8, seed, 0.3), cx, cy, ang))}" fill="#1A0A04" opacity="0.35" transform="translate(4 5)"/>']
    if down:
        out.append(painted(D, pts, ("#3A5A8A", "#1E3A6A", "#0A1A3A"), seed, sk=0.15, angle=ang, n=6, inkw=1.4, hi=0.3))
        return "".join(out)
    out.append(painted(D, pts, ("#FFFDF6", "#F4ECDA", "#C8B898"), seed, sdir=(0.5, 0.9), sk=0.12, angle=ang, n=6, inkw=1.6, hi=0.5))
    out.append(pline(rot([(cx - w * 0.38, cy), (cx + w * 0.38, cy)], cx, cy, ang), "#2A1A10", 1.6, seed + 1, 0.9, 1))
    out.append(disc(*rot([(cx, cy)], cx, cy, ang)[0], s * 0.05, "#C8A040"))
    for half, val in ((-1, a), (1, b)):
        for px, py in PIPS[val]:
            x, y = rot([(cx + px * w * 0.52, cy + half * h * 0.25 + py * w * 0.52)], cx, cy, ang)[0]
            out.append(disc(x, y, s * 0.085, "#1A1A1A") + disc(x - s * 0.02, y - s * 0.02, s * 0.03, "#5A5A5A"))
    return "".join(out)


@design("capicu")
def capicu():
    D = Doc2("prcp")
    # a weathered green-painted plaza table, dappled with shade from the tree overhead
    out = [wood_planks(D, 0, 600, 2001, ("#5AA88A", "#2E7A62", "#14483A"), 5, vertical=True)]
    rnd = random.Random(2002)
    for _ in range(14):
        out.append(f'<path d="{blob(rnd.uniform(0, 600), rnd.uniform(200, 600), rnd.uniform(40, 90), rnd.uniform(20, 50), rnd.randint(0, 999), 0.25, 12, rnd.uniform(-30, 30))}" fill="#0A2A20" opacity="0.22"/>')
    out.append(soft_glow(D, 300, 380, 300, "#FFF6D0", 0.3))
    # the game: a train of tiles snaking across, both ends showing the same number
    s = 34
    # horizontal tiles at 90 degrees put their first value on the right: pairs below are (right, left)
    train = [(96, 300, 90, 3, 2), (166, 300, 90, 3, 3), (236, 300, 90, 6, 3), (306, 300, 90, 1, 6), (376, 300, 90, 1, 1), (446, 300, 90, 4, 1),
             (498, 352, 0, 4, 4), (498, 426, 0, 4, 6), (446, 478, 90, 6, 0), (376, 478, 90, 0, 5)]
    for k, (x, y, a, p, q) in enumerate(train):
        out.append(domino(D, x, y, s, p, q, a, 2010 + k))
    # the winning tile, slammed down at the end: 2 | 5 fits either open end, that's capicú
    out.append(domino(D, 300, 486, s, 5, 2, 82, 2030))
    for k in range(4):
        a = math.radians(160 + k * 14)
        out.append(pline([(300 + math.cos(a) * 50, 486 + math.sin(a) * 40), (300 + math.cos(a) * 66, 486 + math.sin(a) * 52)], "#FFF6D8", 3, 2031 + k, 0.85, 1))
    # the boneyard: tiles face down, and someone's hand of tiles standing
    for k, (x, y, a) in enumerate(((108, 430, 20), (150, 456, -10), (128, 500, 60), (180, 410, 80))):
        out.append(domino(D, x, y, s, 0, 0, a, 2040 + k, down=True))
    # café pocillo and the score sheet
    out.append(cup_saucer(D, 520, 210, 54, 2050, rim=("#7AB4F0", "#2F6CC6", "#123A7A")))
    out.append(steam(520, 150, 40, 2051, "#FFFFFF", 2, 16, 5, 0.6))
    pad = rot(rect_pts(40, 168, 170, 260, 14, 2052, 0.8), 105, 214, -8)
    out.append(cast(D, 110, 262, 66, 8, strength=0.4, seed=2053))
    out.append(painted(D, pad, ("#FFFFFF", "#F6F2E6", "#C8C0B0"), 2052, sk=0.08, n=8, inkw=1.4, hi=0.3))
    for k in range(4):
        y = 192 + k * 18
        out.append(pline(rot([(52, y), (158, y)], 105, 214, -8), "#8AB0D8", 1.2, 2054 + k, 0.7, 1))
    for k, (x, y, n) in enumerate(((70, 200, 4), (120, 200, 5), (70, 236, 3), (120, 236, 2))):
        for j in range(n):
            out.append(pline(rot([(x + j * 7, y - 7), (x + j * 7 + 1, y + 7)], 105, 214, -8), "#2A2A3A", 2, 2060 + k * 7 + j, 0.9, 1))
        if n == 5:
            out.append(pline(rot([(x - 3, y + 5), (x + 31, y - 5)], 105, 214, -8), "#2A2A3A", 2, 2070 + k, 0.9, 1))
    # fallen flamboyán blossoms on the table
    for k in range(7):
        x, y = rnd.uniform(60, 540), rnd.uniform(380, 560)
        out.append(f'<path d="{blob(x, y, 6, 4, rnd.randint(0, 999), 0.25, 8, rnd.uniform(0, 180))}" fill="#E8401E"/>')
    # lettering on a painted board
    out.append(letters(D, 300, 128, "¡Capicú!", SERIF_IT, 120, "#FFF6DC", ["#FFFFFF", "#F2E2B8", "#FFF0C8"], 2080, max_w=420,
                       shadow="#0A2A20", soff=(0.022, 0.036), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 540, "DOMINÓ EN LA PLAZA", "#FFF6DC", font=JOS, size=19, ls=7, line_w=30, gap=12, line="#F6C21C"))
    return finish_b(D, out, 2081, "#FFFFFF", 0.4)


# ================================================================ 21. piraguas — the cart, the syrups and a cone of shaved ice
def piragua(D, cx, top, h, w, seed, syrup=(("#FF8A8A", "#E8263A", "#8A0A1A"),)):
    """A piragua: a paper cone filled with shaved ice packed into a tall pyramid, syrup soaking down from the top."""
    rnd = random.Random(seed)
    cone_top = top + h * 0.55
    cone = [(cx - w / 2, cone_top), (cx + w / 2, cone_top), (cx + w * 0.06, top + h), (cx - w * 0.06, top + h)]
    out = [painted(D, cone, ("#FFFFFF", "#F2EEE6", "#B8B0A6"), seed, sdir=(1, 0.3), sk=0.18, angle=-90, n=10, inkw=1.6, hi=0.4)]
    for k in range(3):
        out.append(pline([(cx - w * 0.44 + k * w * 0.08, cone_top + 6 + k * 18), (cx + w * 0.44 - k * w * 0.08, cone_top + 6 + k * 18)], "#2F6CC6", 2.2, seed + k, 0.7, 1))
    ice = [(cx - w * 0.52, cone_top + 4), (cx - w * 0.36, top + h * 0.3), (cx - w * 0.06, top + 6), (cx, top), (cx + w * 0.06, top + 6), (cx + w * 0.36, top + h * 0.3), (cx + w * 0.52, cone_top + 4)]
    out.append(painted(D, ice, ("#FFFFFF", "#EEF4FA", "#B8C8D8"), seed + 5, sdir=(0.8, 0.4), sk=0.18, angle=-60, n=20, inkw=1.6, hi=0.4))
    d = smooth_closed(ice)
    cid = D.clip(f'<path d="{d}"/>')
    pal = syrup[0]
    g = D.lin([(0, pal[1], 0.95), (0.55, pal[1], 0.8), (0.85, pal[0], 0.3), (1, pal[0], 0)])
    inner = [f'<rect x="{cx - w:.1f}" y="{top:.1f}" width="{2 * w:.1f}" height="{h * 0.6:.1f}" fill="{g}"/>']
    for _ in range(int(w * 1.2)):
        x, y = rnd.uniform(cx - w / 2, cx + w / 2), rnd.uniform(top, cone_top)
        inner.append(disc(x, y, rnd.uniform(0.8, 2), rnd.choice(["#FFFFFF", pal[0], pal[2]]), rnd.uniform(0.4, 0.9)))
    inner.append(shade_over(D, d, "#1A0A10", 0.3, 0, 0, 1, 0, 0.5))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    for k in range(3):
        x = cx + (k - 1) * w * 0.25
        out.append(taper([(x, cone_top - 2), (x + 1, cone_top + 12 + k * 4)], 4, 2.4, pal[1], 0.9))
    return "".join(out)


def syrup_bottle(D, cx, base, h, w, col, seed, label_col="#FFFFFF"):
    pal = pal_of(col, 0.4, 0.4)
    body = [(cx - w / 2, base), (cx - w / 2, base - h * 0.62), (cx - w * 0.2, base - h * 0.82), (cx - w * 0.16, base - h), (cx + w * 0.16, base - h),
            (cx + w * 0.2, base - h * 0.82), (cx + w / 2, base - h * 0.62), (cx + w / 2, base)]
    out = [painted(D, body, pal, seed, sdir=(1, 0.2), sk=0.18, angle=-90, n=8, inkw=1.4, hi=0.5, hik=0.12)]
    out.append(f'<rect x="{cx - w * 0.16:.1f}" y="{base - h - 8:.1f}" width="{w * 0.32:.1f}" height="9" fill="#C8CCD4"/>')
    out.append(f'<path d="{hg.org_rect(cx - w * 0.42, base - h * 0.5, w * 0.84, h * 0.24, seed + 1, 0.3, 8, 1)}" fill="{label_col}"/>')
    out.append(taper([(cx - w * 0.3, base - h * 0.6), (cx - w * 0.3, base - 8)], 4, 3, "#FFFFFF", 0.6))
    return "".join(out)


@design("piraguas")
def piraguas():
    D = Doc2("prpg")
    out = [sky(D, [(0, "#3AA8E0"), (0.7, "#9AD8F2"), (1, "#E8F6F8")], 2101, 600, ["#FFFFFF", "#7AC8EE"], 60)]
    out.append(soft_glow(D, 470, 150, 220, "#FFFDE8", 0.7))
    # a pastel facade behind the plaza and the paving
    out.append(painted(D, rect_pts(-10, 300, 610, 470, 30, 2102, 0.5), PASTELS[0], 2102, sdir=(0.2, 1), sk=0.06, angle=-88, n=40, inkw=1.4, hi=0.2))
    for k, x in enumerate((40, 170, 430, 560)):
        out.append(f'<path d="{hg.org_rect(x - 22, 330, 44, 110, 2103 + k, 0.4, 12, 1)}" fill="#FFFFFF"/><path d="{hg.org_rect(x - 16, 336, 32, 104, 2107 + k, 0.4, 12, 1)}" fill="#2E7A5A"/>')
    out.append(f'<path d="{hg.org_rect(-10, 296, 620, 12, 2111, 0.4, 30, 1)}" fill="#FFFFFF"/>')
    out.append(f'<rect y="470" width="600" height="140" fill="#C8B8A8"/>')
    out.append(strokes(D.nid(), "M 0 470 L 600 470 L 600 610 L 0 610 Z", (-40, 470, 600, 610), ["#E8DCD0", "#A89888"], 2112, n=60, angle=0, length=(30, 90), width=(2, 5), opacity=(0.2, 0.4)))
    # the cart: striped umbrella, a glass shelf of syrups, the ice block under a towel, wooden body and wheels
    cx = 300
    out.append(taper([(cx, 470), (cx, 200)], 6, 5, "#8A8A92"))
    def rim(t):
        return (cx - 210 + 420 * t, 236 + 26 * math.sin(math.pi * t))
    for k in range(8):
        a0, a1 = k / 8, (k + 1) / 8
        pts_ = [(cx, 170)] + [(rim(a0 + (a1 - a0) * j / 6)[0], rim(a0 + (a1 - a0) * j / 6)[1] - 6 * math.sin(math.pi * j / 6)) for j in range(7)]
        out.append(painted(D, pts_, (ROJO if k % 2 == 0 else ("#FFFFFF", "#F6F0E6", "#B8B0A6")), 2113 + k, sdir=(0.3, 1), sk=0.15, angle=-60, n=8, inkw=1.4, hi=0.4))
    out.append(f'<path d="{smooth_closed([rim(t / 20) for t in range(21)] + [(cx + 140, 214), (cx, 206), (cx - 140, 214)])}" fill="#3A0A10" opacity="0.15"/>')
    out.append(disc(cx, 168, 6, "#F6C21C"))
    body = rect_pts(cx - 170, 360, cx + 170, 470, 20, 2120, 0.6)
    out.append(cast(D, cx, 512, 210, 16, strength=0.45, seed=2121))
    out.append(painted(D, body, ("#6AB4F0", "#2F6CC6", "#123A7A"), 2120, sdir=(1, 0.3), sk=0.12, angle=0, n=40, inkw=2, hi=0.4))
    for k in range(5):
        out.append(pline([(cx - 166, 382 + k * 18), (cx + 166, 382 + k * 18)], "#123A7A", 1.4, 2122 + k, 0.5, 1))
    out.append(f'<path d="{hg.org_rect(cx - 130, 396, 260, 46, 2127, 0.6, 20, 4)}" fill="#FFF6DC"/>')
    out.append(f'<text x="{cx}" y="430" text-anchor="middle" {ANTON} font-size="32" letter-spacing="3" fill="#D52B1E">PIRAGUAS</text>')
    for k, x in enumerate((cx - 140, cx + 140)):
        out.append(painted(D, blob_pts(x, 486, 26, 26, 2128 + k, 0.02, 16), ("#5A5A62", "#2A2A32", "#0A0A12"), 2128 + k, sk=0.2, n=6, inkw=1.6, hi=0.3))
        out.append(disc(x, 486, 9, "#C8CCD4"))
    # counter: the towel-covered ice block and the shaver, bottles of syrup in a row
    out.append(painted(D, rect_pts(cx - 180, 346, cx + 180, 362, 20, 2130, 0.4), ("#D8A06A", "#A86A3A", "#5E3618"), 2130, sk=0.2, angle=0, n=10, inkw=1.6, hi=0.4))
    out.append(painted(D, [(cx - 70, 346), (cx - 64, 300), (cx + 64, 300), (cx + 70, 346)], ("#FFFFFF", "#F2F2F6", "#B8BCC8"), 2131, sk=0.15, n=10, inkw=1.4, hi=0.4))
    for k in range(3):
        out.append(pline([(cx - 64, 312 + k * 10), (cx + 64, 312 + k * 10)], "#2F6CC6", 2, 2132 + k, 0.7, 1))
    flavours = [("#E8263A", 2140), ("#F6C21C", 2141), ("#3EA84A", 2142), ("#8A4A1E", 2143), ("#FFFFFF", 2144), ("#F26A9A", 2145)]
    for k, (col, sd) in enumerate(flavours):
        x = cx - 160 + k * 24 if k < 3 else cx + 100 + (k - 3) * 24
        out.append(syrup_bottle(D, x, 346, 60, 20, col, sd, label_col="#FFFDF4" if col != "#FFFFFF" else "#2F6CC6"))
    # the piragua held up front, a second one waiting
    out.append(piragua(D, 482, 308, 200, 90, 2150))
    out.append(piragua(D, 118, 344, 164, 74, 2151, syrup=(("#C8986A", "#8A4A1E", "#4A2008"),)))
    # lettering
    out.append(letters(D, 300, 128, "piraguas", SERIF_IT, 124, "#FFFFFF", ["#FFFFFF", "#E8F6FC", "#FFF6E8"], 2160, max_w=430,
                       shadow="#123A7A", soff=(0.022, 0.036), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 540, "FRAMBUESA · TAMARINDO · COCO", "#123A7A", font=JOS, size=18, ls=3, line_w=20, gap=10))
    return finish_b(D, out, 2161)


# ================================================================ 22. quesitos — at the panadería counter
def quesito(D, cx, cy, L, r, ang, seed):
    """A quesito: puff pastry rolled around sweet cream cheese, baked puffy and golden, brushed with shiny syrup;
    flaky spiral layers at the ends with the cheese oozing out."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux

    def A(t, o):
        return (cx + ux * L * t + nx * r * o, cy + uy * L * t + ny * r * o)

    top, bot = [], []
    for i in range(15):
        t = -0.5 + i / 14
        puff = 1 + 0.1 * math.sin(i * 1.9 + seed) - 0.12 * (abs(t) * 2) ** 4
        top.append(A(t, -puff))
        bot.append(A(t, puff * 0.95))
    pts = top + [A(0.5 + 0.06, -0.4), A(0.5 + 0.08, 0.3)] + bot[::-1] + [A(-0.5 - 0.08, 0.3), A(-0.5 - 0.06, -0.4)]
    out = [cast(D, cx + 6, cy + r * 1.1, L * 0.55, r * 0.4, "#3A1A04", 0.4, seed)]
    out.append(painted(D, pts, ("#FFD88A", "#E0A048", "#94561A"), seed, sdir=(0.2, 1), sk=0.2, angle=ang, n=36, slen=(L * 0.08, L * 0.25), sw=(1, 3),
                       cols=["#FFE8B0", "#B8742A", "#F2C070", "#8A4A12"], inkw=1.8, hi=0.5, hik=0.14))
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    # the diagonal seams of the roll and puffed, blistered pastry
    for k in range(-3, 4):
        t = k / 7.5
        inner.append(pline([A(t - 0.06, -1.2), A(t + 0.02, 0), A(t + 0.1, 1.2)], "#9A5A1A", 1.6, seed + k, 0.5, 1))
        inner.append(pline([A(t - 0.05, -1.2), A(t + 0.03, 0), A(t + 0.11, 1.2)], "#FFE6A8", 1.2, seed + k + 10, 0.5, 1))
    for _ in range(18):
        x, y = A(rnd.uniform(-0.45, 0.45), rnd.uniform(-0.9, 0.6))
        inner.append(f'<path d="{blob(x, y, rnd.uniform(3, 6), rnd.uniform(2, 3.5), rnd.randint(0, 999), 0.2, 8, ang)}" fill="#FFF0C0" opacity="0.45"/>')
    # syrup glaze: glassy highlights and a few sugar crystals
    inner.append(taper([A(-0.42, -0.55), A(0, -0.62), A(0.4, -0.5)], r * 0.18, r * 0.08, "#FFFDF0", 0.85))
    inner.append(taper([A(-0.3, -0.2), A(0.2, -0.26)], r * 0.08, r * 0.04, "#FFFDF0", 0.6))
    inner.append(specks(seed + 3, bbox(pts), ["#FFFFFF"], 30, (0.7, 1.4), (0.6, 1)))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # the open end: flaky spiral and cream cheese oozing out
    ex, ey = A(0.53, 0)
    end = rot(blob_pts(ex, ey, r * 0.34, r * 0.86, seed + 5, 0.1, 14), ex, ey, ang)
    out.append(f'<path d="{smooth_closed(end)}" fill="#F0B860"/>')
    sw = [(ex + math.cos(t) * r * 0.06 * t * 0.35, ey + math.sin(t) * r * 0.06 * t) for t in [i * 0.55 for i in range(14)]]
    out.append(pline(rot(sw, ex, ey, ang), "#A8641A", 1.4, seed + 6, 0.8, 1))
    ooze = rot([(ex + r * 0.1, ey - r * 0.4), (ex + r * 0.42, ey - r * 0.25), (ex + r * 0.5, ey + r * 0.1), (ex + r * 0.36, ey + r * 0.42), (ex + r * 0.06, ey + r * 0.3)], ex, ey, ang)
    out.append(painted(D, ooze, ("#FFFFFF", "#FBF6EC", "#D8CCB8"), seed + 7, sk=0.2, n=4, inkw=1.2, inkop=0.5, hi=0.5))
    out.append(ink(smooth_closed(end), "#94561A", 1.4, seed + 8, 1, 0.7))
    return "".join(out)


@design("quesitos")
def quesitos():
    D = Doc2("prqs")
    # bakery: a warm cream wall with a chalk price board, a glass case edge, the counter
    out = [paper(D.nid(), "#F6E2C4", FLECK, 2201)]
    out.append(blooms(2202, ["#F2C890", "#E8B070", "#FFF0D0"], 6, (0, 0, 600, 400), (100, 180), (0.1, 0.16)))
    out.append(soft_glow(D, 300, 260, 320, "#FFF8E0", 0.6))
    # shelves of bread behind (soft, out of focus)
    for row, y in enumerate((244, 318)):
        out.append(painted(D, rect_pts(-10, y, 610, y + 10, 30, 2203 + row, 0.4), WOOD, 2203 + row, sk=0.2, angle=0, n=10, inkw=1.2, hi=0.3))
        rnd = random.Random(2205 + row)
        x = 10
        while x < 600:
            w = rnd.uniform(40, 70)
            out.append(f'<path d="{blob(x + w / 2, y - 12, w / 2, 13, rnd.randint(0, 999), 0.08, 12)}" fill="{rnd.choice(["#E0A860", "#D8984A", "#F0C078"])}" opacity="0.75"/>')
            out.append(taper([(x + w * 0.2, y - 16), (x + w * 0.8, y - 18)], 3, 2, "#FFF0C8", 0.5))
            x += w + rnd.uniform(6, 14)
    out.append(f'<rect y="200" width="600" height="140" fill="#F6E2C4" opacity="0.35"/>')
    # the counter top
    out.append(wood_planks(D, 380, 600, 2207, ("#C88A5A", "#8A5230", "#4A2410"), 3))
    out.append(f'<rect y="374" width="600" height="10" fill="#3A1A08" opacity="0.5"/>')
    # paper bag
    bag = [(62, 300), (172, 296), (182, 520), (52, 524)]
    out.append(cast(D, 122, 526, 70, 10, strength=0.45, seed=2208))
    out.append(painted(D, bag, ("#E8C890", "#C8A060", "#7A5A2A"), 2208, sdir=(1, 0.3), sk=0.15, angle=-90, n=20, inkw=1.6, hi=0.35))
    out.append(pline([(66, 300), (118, 316), (172, 296)], "#7A5A2A", 1.6, 2209, 0.7, 1))
    out.append(f'<text x="118" y="420" text-anchor="middle" {SERIF_IT} font-size="21" fill="#8A3A1E" transform="rotate(-2 118 420)">panadería</text>')
    out.append(pline([(80, 432), (156, 430)], "#8A3A1E", 1.6, 2210, 0.7, 1))
    # wax paper and the quesitos
    sheet = rot(rect_pts(170, 430, 520, 560, 20, 2211, 1.6), 345, 495, -4)
    out.append(cast(D, 350, 566, 180, 12, strength=0.35, seed=2212))
    out.append(painted(D, sheet, ("#FFFFFF", "#F6F0E4", "#C8BEB0"), 2211, sk=0.08, n=20, inkw=1.2, hi=0.3))
    for k, (x, y, a) in enumerate(((290, 450, -8), (420, 470, 12), (330, 520, -2))):
        out.append(quesito(D, x, y, 130, 30, a, 2220 + k))
    out.append(specks(2230, (200, 430, 500, 560), ["#FFFFFF", "#F6E8C8"], 40, (0.8, 1.6), (0.6, 0.95)))
    # café con leche in a glass cup
    gx, gb = 520, 420
    out.append(cast(D, gx + 6, gb, 40, 7, strength=0.45, seed=2231))
    cup = [(gx - 32, gb - 92), (gx + 32, gb - 92), (gx + 27, gb), (gx - 27, gb)]
    out.append(painted(D, cup, ("#F2DCC0", "#C89A6A", "#7A4A26"), 2232, sdir=(1, 0.2), sk=0.16, angle=-90, n=10, inkw=1.6, hi=0.4))
    out.append(f'<path d="{smooth_closed(ell_pts(gx, gb - 92, 32, 7, 0, 360, 16))}" fill="#F6E6CC"/>')
    out.append(taper([(gx - 22, gb - 84), (gx - 20, gb - 10)], 5, 3, "#FFFFFF", 0.65))
    out.append(steam(gx, gb - 100, 50, 2233, "#FFFFFF", 2, 16, 5, 0.7))
    # lettering
    out.append(letters(D, 300, 124, "quesitos", SERIF_IT, 128, "#B8461A", ["#D8683A", "#8A2E0A", "#E88A52"], 2240, max_w=430,
                       shadow="#5A2210", soff=(0.02, 0.035), angle=-40, hi="#FFE2B8"))
    out.append(ruled(300, 168, "CON UN CAFECITO", "#5A2A10", font=JOS, size=19, ls=7, line_w=34, gap=14))
    return finish_b(D, out, 2241)


# ================================================================ 23. el yunque — the rainforest falls, a parrot on the branch
def iguaca(D, x, y, s, seed, flip=1):
    """Puerto Rican parrot: bright green body, red forehead band, white eye ring, blue flight feathers."""
    f = flip
    def P(pts):
        return [(x + px * s * f, y + py * s) for px, py in pts]
    out = []
    # tail
    out.append(painted(D, P([(4, 20), (16, 46), (10, 50), (-2, 24)]), ("#7ACB6A", "#2E8A3A", "#0E4A1E"), seed, sk=0.2, n=4, inkw=1.0, hi=0.4))
    body = P([(-8, -18), (4, -22), (12, -12), (14, 4), (10, 22), (0, 26), (-8, 16), (-12, 0)])
    out.append(painted(D, body, ("#A8E07A", "#4AAA3A", "#1E6A22"), seed + 1, sdir=(0.5 * f, 0.8), sk=0.2, angle=-70, n=12, inkw=1.4, hi=0.45))
    wing = P([(-2, -8), (10, -6), (14, 8), (10, 20), (2, 14)])
    out.append(painted(D, wing, ("#8ACB6A", "#2E8A3A", "#0E4A1E"), seed + 2, sk=0.2, n=6, inkw=1.2, hi=0.3))
    out.append(taper(P([(6, 8), (10, 18), (8, 24)]), 4 * s, 1.6 * s, "#2F6CC6"))
    head = P([(-12, -26), (-4, -34), (6, -32), (10, -22), (2, -16), (-8, -16)])
    out.append(painted(D, head, ("#B8E88A", "#5ABA44", "#2A7A2A"), seed + 3, sk=0.2, n=5, inkw=1.3, hi=0.45))
    out.append(taper(P([(-9, -30), (-4, -34), (2, -33)]), 3 * s, 2 * s, "#D52B1E"))
    ex, ey = P([(-2, -26)])[0]
    out.append(disc(ex, ey, 3.2 * s, "#FFFFFF") + disc(ex, ey, 1.6 * s, "#2A1A06") + disc(ex - 0.5 * s, ey - 0.6 * s, 0.6 * s, "#FFFFFF"))
    beak = P([(-10, -26), (-17, -23), (-15, -16), (-9, -18)])
    out.append(painted(D, beak, ("#FFF6E0", "#F2E2C0", "#B8A07A"), seed + 4, sk=0.2, n=2, inkw=1.2, hi=0.4))
    for k in (-3, 3):
        out.append(taper(P([(k, 24), (k - 1, 30)]), 2.4 * s, 2 * s, "#8A8A7A"))
    return "".join(out)


def heliconia(D, x, base, h, seed, ang=-90):
    """Hanging lobster-claw heliconia: zig-zag red bracts tipped yellow on a green stalk."""
    out = [taper([(x, base), (x + 4, base - h * 0.5), (x, base - h)], 5, 3, "#3E7A2A")]
    for k in range(5):
        t = 0.45 + k * 0.11
        y = base - h * t
        sg = 1 if k % 2 else -1
        br = [(x, y), (x + sg * 24, y - 6), (x + sg * 30, y - 16), (x + sg * 6, y - 14)]
        out.append(painted(D, br, ("#FF8A6A", "#E0301E", "#8A0A06"), seed + k, sk=0.2, n=4, inkw=1.0, hi=0.5))
        out.append(f'<path d="M {x + sg * 26:.1f} {y - 10:.1f} l {sg * 5:.1f} -4" stroke="#F6D24A" stroke-width="3" stroke-linecap="round"/>')
    return "".join(out)


@design("el-yunque")
def el_yunque():
    D = Doc2("pryq")
    out = [sky(D, [(0, "#CFE8D8"), (0.5, "#A8D0B8"), (1, "#5E9A7A")], 2301, 600, ["#E8F6EC", "#8ABCA0"], 60)]
    out.append(soft_glow(D, 310, 160, 300, "#FFFFF0", 0.8))
    # light rays through the canopy
    for k in range(6):
        x = 200 + k * 50
        out.append(f'<path d="M {x} 120 L {x + 40} 120 L {x + 140} 600 L {x + 60} 600 Z" fill="#FFFFF0" opacity="0.08"/>')
    # misty distant canopy
    out.append(dab_crown(D, 100, 210, 140, 60, [("#C8E4D0", "#A8CCB8", "#88B0A0")], 2302, n=120, size=(8, 16), inkw=0))
    out.append(dab_crown(D, 520, 210, 140, 60, [("#C8E4D0", "#A8CCB8", "#88B0A0")], 2303, n=120, size=(8, 16), inkw=0))
    # the rock face and the waterfall
    rock = [(170, 230), (250, 216), (370, 218), (440, 236), (470, 330), (450, 470), (150, 470), (130, 330)]
    out.append(painted(D, rock, ("#9A9488", "#6A6458", "#3A362E"), 2304, sdir=(1, 0.2), sk=0.12, angle=-80, n=60, inkw=1.6, hi=0.3))
    rd = smooth_closed(rock)
    cid = D.clip(f'<path d="{rd}"/>')
    rnd = random.Random(2305)
    moss = "".join(f'<path d="{blob(rnd.uniform(140, 470), rnd.uniform(220, 470), rnd.uniform(10, 26), rnd.uniform(6, 14), rnd.randint(0, 999), 0.25, 10)}" fill="{rnd.choice(["#4E8A3A", "#3A6A2E", "#6AA84A"])}" opacity="0.7"/>' for _ in range(26))
    out.append(f'<g {cid}>{moss}</g>')
    fall = [(256, 222), (346, 222), (360, 300), (372, 400), (384, 470), (220, 470), (232, 400), (244, 300)]
    out.append(painted(D, fall, ("#FFFFFF", "#DCEEF2", "#9ABCC8"), 2306, sdir=(1, 0), sk=0.1, angle=-90, n=40, inkw=1.2, inkop=0.4, hi=0.4))
    fd = smooth_closed(fall)
    fc = D.clip(f'<path d="{fd}"/>')
    streaks = []
    for _ in range(70):
        x = rnd.uniform(226, 380)
        y = rnd.uniform(220, 440)
        streaks.append(taper([(x, y), (x + (x - 300) * 0.04, y + rnd.uniform(30, 80))], rnd.uniform(1.5, 4), 0.6, rnd.choice(["#FFFFFF", "#B8D4DC", "#8AB0BC"]), rnd.uniform(0.5, 0.9)))
    out.append(f'<g {fc}>{"".join(streaks)}</g>')
    # the pool, foam and spray
    out.append(painted(D, ell_pts(300, 486, 210, 36, 0, 360, 30), ("#7AC8C0", "#2E8A8A", "#0E4A50"), 2307, sk=0.15, angle=0, n=30, inkw=1.6, hi=0.3))
    out.append(wave_lines(2308, (120, 466, 480, 512), ["#FFFFFF", "#B8E8E0"], 30, (8, 22), 1.8, 2, (0.5, 0.9)))
    for _ in range(30):
        out.append(f'<path d="{blob(rnd.uniform(200, 400), rnd.uniform(450, 480), rnd.uniform(10, 24), rnd.uniform(5, 10), rnd.randint(0, 999), 0.2, 10)}" fill="#FFFFFF" opacity="{rnd.uniform(0.4, 0.8):.2f}"/>')
    out.append(mist(D, 450, 70, 2309, "#FFFFFF", 0.35, 140, 460))
    # foreground: tree ferns and sierra palm fronds framing both sides, boulders, heliconias
    for k, (x, y, r) in enumerate(((150, 530, 50), (460, 540, 60), (310, 560, 40))):
        out.append(painted(D, blob_pts(x, y, r, r * 0.6, 2310 + k, 0.08, 14), ("#A8A498", "#6E6A5E", "#3A362E"), 2310 + k, sdir=(0.6, 0.8), sk=0.2, n=12, inkw=1.6, hi=0.4))
        out.append(f'<path d="{blob(x - r * 0.2, y - r * 0.35, r * 0.6, r * 0.18, 2313 + k, 0.2, 10)}" fill="#5A9A3A" opacity="0.8"/>')
    out.append(f'<rect y="560" width="600" height="50" fill="#1E4A2A" opacity="0.85"/>')
    out.append(tree_fern(D, 46, 600, 400, 2320, ["#3E8A44", "#2E7A3A", "#5AA050"], trunk="#3A2A1A"))
    out.append(tree_fern(D, 566, 610, 380, 2321, ["#3E8A44", "#2E7A3A", "#5AA050"], trunk="#3A2A1A"))
    out.append(heliconia(D, 120, 600, 140, 2322))
    out.append(heliconia(D, 500, 600, 120, 2323))
    for k, (bx, by, a, L) in enumerate(((-20, 600, -50, 230), (620, 600, -130, 230), (-20, 380, -20, 160), (620, 400, -160, 150))):
        out.append(banana_leaf(D, bx, by, a, L, 40, 2324 + k, pal=("#7ACB6A", "#2E8A44", "#0F4A26")))
    # the iguaca on a mossy branch
    out.append(taper([(-10, 300), (80, 312), (150, 300)], 12, 6, "#5A4A2E"))
    out.append(taper([(-10, 296), (80, 308), (150, 296)], 4, 2, "#7AAA4A", 0.8))
    out.append(iguaca(D, 106, 274, 1.5, 2330, flip=-1))
    # lettering
    out.append(letters(D, 300, 128, "El Yunque", SERIF_IT, 116, "#FFFFFF", ["#FFFFFF", "#E8F6EC", "#F6FFF0"], 2340, max_w=430,
                       shadow="#1E4A2A", soff=(0.022, 0.036), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 170, "BOSQUE LLUVIOSO", "#1E4A2A", font=JOS, size=19, ls=7, line_w=34, gap=14, line="#2E7A3A"))
    return finish_b(D, out, 2341)


# ================================================================ 24. bahía bioluminiscente — a kayak through glowing water
@design("bahia-bioluminiscente")
def bahia_bioluminiscente():
    D = Doc2("prbb")
    out = [sky(D, [(0, "#060A24"), (0.6, "#0E1A44"), (1, "#1A2A5A")], 2401, 340, ["#1A2A6A", "#04081A"], 50)]
    rnd = random.Random(2402)
    # the milky way and stars
    out.append(f'<path d="{blob(330, 210, 340, 46, 2403, 0.2, 18, -24)}" fill="#8A9AE0" opacity="0.12"/>')
    out.append(f'<path d="{blob(330, 210, 260, 22, 2404, 0.25, 16, -24)}" fill="#C8D0F6" opacity="0.12"/>')
    for _ in range(140):
        out.append(disc(rnd.uniform(0, 600), rnd.uniform(0, 330), rnd.uniform(0.5, 1.6), "#FFFFFF", rnd.uniform(0.3, 1)))
    for x, y in ((90, 250), (500, 120), (420, 280)):
        out.append(sparkle(x, y, 6, "#FFFFFF", 0.9))
    # mangroves on the far shore: dark bushy silhouettes with arching prop roots
    shore = ridge([(-20, 330), (100, 314), (220, 326), (330, 310), (460, 324), (620, 312)], 2405, 8, 4)
    out.append(f'<path d="{smooth_open(shore)} L 620 352 L -20 352 Z" fill="#050A14"/>')
    for k in range(40):
        x = k * 16 - 10
        y = 336 + rnd.uniform(-2, 4)
        out.append(pline([(x, y - 10), (x + 5, y - 2), (x + 8, y + 10)], "#050A14", 2, 2406 + k, 1, 1))
    # the bay
    out.append(sea(D, 340, 600, [(0, "#0A1638"), (1, "#04081C")], 2407, ["#14245A", "#020410"], 50))
    for _ in range(50):
        x, y = rnd.uniform(0, 600), rnd.uniform(346, 600)
        out.append(taper([(x, y), (x + rnd.uniform(14, 40), y)], 1.6, 0.6, "#2AD8E8", rnd.uniform(0.15, 0.45)))
    # star reflections
    for _ in range(30):
        out.append(disc(rnd.uniform(0, 600), rnd.uniform(350, 420), rnd.uniform(0.5, 1.2), "#FFFFFF", rnd.uniform(0.2, 0.6)))
    # the glowing wake behind the kayak and around the paddles
    kx, ky = 300, 470
    out.append(f'<path d="{smooth_closed([(kx + 40, ky + 4), (kx - 120, ky - 6), (kx - 330, ky - 66), (kx - 360, ky - 40), (kx - 140, ky + 30), (kx + 40, ky + 18)])}" fill="#3AF0FF" opacity="0.2"/>')
    out.append(D.glow(kx - 60, ky + 10, 200, "#3AF0FF", 0.45, ry=46))
    for _ in range(220):
        t = rnd.random()
        x = kx + 30 - t * 360 + rnd.uniform(-8, 8)
        y = ky + 10 - t * 60 + rnd.gauss(0, 6 + t * 18)
        out.append(disc(x, y, rnd.uniform(0.6, 2.2), rnd.choice(["#AFFCFF", "#3AF0FF", "#FFFFFF", "#7AF6E8"]), rnd.uniform(0.4, 1)))
    for px, py in ((kx - 92, ky + 30), (kx + 74, ky + 28), (kx - 20, ky + 34)):
        out.append(D.glow(px, py, 40, "#7AFCFF", 0.7))
        for _ in range(26):
            a, r = rnd.uniform(0, 6.28), rnd.uniform(4, 30)
            out.append(disc(px + math.cos(a) * r, py + math.sin(a) * r * 0.45, rnd.uniform(0.6, 1.8), "#C8FFFF", rnd.uniform(0.5, 1)))
    # the kayak with two silhouetted paddlers
    hull = [(kx - 140, ky + 2), (kx - 60, ky - 8), (kx + 60, ky - 8), (kx + 150, ky), (kx + 60, ky + 16), (kx - 60, ky + 16)]
    out.append(painted(D, hull, ("#F6C26A", "#E88A2A", "#8A3A0A"), 2410, sdir=(0, 1), sk=0.2, angle=0, n=14, inkw=1.6, hi=0.4))
    out.append(taper([(kx - 130, ky + 10), (kx, ky + 15), (kx + 140, ky + 6)], 3, 2, "#8AF6FF", 0.7))
    for k, (dx, ang) in enumerate(((-56, -28), (40, 24))):
        hx, hy = kx + dx, ky - 10
        out.append(f'<path d="{blob(hx, hy - 14, 12, 16, 2411 + k, 0.06, 12)}" fill="#0A0E1E"/>' + disc(hx, hy - 38, 9, "#0A0E1E"))
        a = math.radians(ang)
        p0 = (hx - math.cos(a) * 70, hy - 14 - math.sin(a) * 70)
        p1 = (hx + math.cos(a) * 70, hy - 14 + math.sin(a) * 70)
        out.append(taper([p0, p1], 3.4, 3.4, "#0A0E1E"))
        for p in (p0, p1):
            out.append(f'<path d="{blob(p[0], p[1], 8, 4, 2413 + k, 0.1, 8, math.degrees(a))}" fill="#0A0E1E"/>')
    # lettering
    out.append(letters(D, 300, 116, "bahía", SERIF_IT, 120, "#E8FCFF", ["#FFFFFF", "#B8F6FF", "#E8FFFF"], 2420, max_w=360,
                       shadow="#000814", soff=(0.022, 0.036), angle=-40, hi="#FFFFFF"))
    out.append(D.glow(300, 158, 220, "#3AF0FF", 0.18, ry=30))
    out.append(label(300, 166, "BIOLUMINISCENTE", JOS, 34, "#8AF6FF", ls=6, max_w=440))
    out.append(ruled(300, 538, "VIEQUES · LAJAS · FAJARDO", "#AFEAF6", font=JOS, size=18, ls=4, line_w=26, gap=12))
    return finish_b(D, out, 2421, "#FFFFFF", 0.4)


# ================================================================ 25. mami — y sus matas (her plants on the balcony)
def hanging_fern(D, cx, top, s, seed):
    """Helecho in a hanging basket: chains, a woven pot, and long arching fronds spilling down."""
    rnd = random.Random(seed)
    out = []
    for dx in (-0.5, 0, 0.5):
        out.append(pline([(cx, top), (cx + dx * s * 0.9, top + s * 0.9)], "#4A4A52", 1.4, seed + int(dx * 10), 0.9, 1))
    pot = [(cx - s * 0.5, top + s * 0.9), (cx + s * 0.5, top + s * 0.9), (cx + s * 0.4, top + s * 1.35), (cx - s * 0.4, top + s * 1.35)]
    fronds = []
    for k in range(14):
        a = -170 + k * 160 / 13 + rnd.uniform(-6, 6)
        L = s * rnd.uniform(1.0, 1.7)
        fronds.append(frond(cx + rnd.uniform(-s * 0.3, s * 0.3), top + s * 0.92, a, L, seed + k,
                            ["#8ACB5A", "#4E9A3A", "#2E6A22", "#A8DC6A"], droop=1.1, blade=0.22, n=16, sw=1.2))
    out.append("".join(fronds[:7]))
    out.append(painted(D, pot, ("#E8B47A", "#B07840", "#5E3A18"), seed, sk=0.2, angle=0, n=8, inkw=1.4, hi=0.4))
    for k in range(3):
        out.append(pline([(cx - s * 0.48 + k * 2, top + s * (1.0 + k * 0.12)), (cx + s * 0.48 - k * 2, top + s * (1.0 + k * 0.12))], "#7A4A1E", 1.2, seed + 30 + k, 0.6, 1))
    out.append("".join(fronds[7:]))
    return "".join(out)


def watering_can(D, cx, base, s, seed, pal=("#7AD0C8", "#1F9A8A", "#0E5A50")):
    body = [(cx - s * 0.5, base), (cx - s * 0.46, base - s * 0.8), (cx + s * 0.46, base - s * 0.8), (cx + s * 0.5, base)]
    out = [cast(D, cx + 6, base, s * 0.7, s * 0.08, strength=0.4, seed=seed)]
    out.append(taper([(cx + s * 0.4, base - s * 0.25), (cx + s * 0.9, base - s * 0.75), (cx + s * 1.05, base - s * 0.85)], s * 0.14, s * 0.08, pal[2]))
    out.append(painted(D, rot(blob_pts(cx + s * 1.08, base - s * 0.88, s * 0.1, s * 0.07, seed + 1, 0.1, 8), cx + s * 1.08, base - s * 0.88, -40), pal, seed + 1, sk=0.2, n=2, inkw=1, hi=0.4))
    out.append(ink(smooth_open([(cx - s * 0.3, base - s * 0.8), (cx - s * 0.1, base - s * 1.2), (cx + s * 0.25, base - s * 0.8)]), pal[2], s * 0.08, seed + 2, 1, 1))
    out.append(painted(D, body, pal, seed, sdir=(1, 0.2), sk=0.18, angle=-90, n=12, inkw=1.6, hi=0.5))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - s * 0.8, s * 0.46, s * 0.08, 0, 360, 16))}" fill="{pal[2]}"/>')
    return "".join(out)


def aloe(D, cx, base, s, seed):
    """Sábila (aloe vera) in a clay pot: thick spiky leaves with pale freckles."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 5, base, s * 0.55, s * 0.07, strength=0.4, seed=seed)]
    for k in range(9):
        a = -90 + (k - 4) * 17 + rnd.uniform(-5, 5)
        L = s * rnd.uniform(0.8, 1.25)
        out.append(leaf_simple(D, cx + (k - 4) * 2, base - s * 0.55, L, s * 0.09, a, ("#B8D8A0", "#6E9A6A", "#2E5A3A"), seed + k, vein=False, inkw=1.0))
    pot = [(cx - s * 0.42, base - s * 0.58), (cx + s * 0.42, base - s * 0.58), (cx + s * 0.32, base), (cx - s * 0.32, base)]
    out.append(painted(D, pot, ("#F0A070", "#C8603A", "#7A3218"), seed + 20, sdir=(1, 0.2), sk=0.18, angle=-90, n=10, inkw=1.6, hi=0.45))
    out.append(f'<path d="{hg.org_rect(cx - s * 0.46, base - s * 0.66, s * 0.92, s * 0.12, seed + 21, 0.4, 8, 1)}" fill="#D8703E"/>')
    return "".join(out)


@design("mami")
def mami():
    D = Doc2("prmm")
    out = [sky(D, [(0, "#F8D2D0"), (1, "#F2B8B8")], 2501, 600, ["#FFE4E0", "#E8A0A4", "#FFF0EC"], 100, angle=-84, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 140, 140, 340, "#FFF8F0", 0.55))
    # rejas across the balcony opening, the green beyond
    out.append(f'<path d="{hg.org_rect(-10, 228, 620, 220, 2502, 0.5, 30, 1)}" fill="#BFE0C0"/>')
    out.append(dab_crown(D, 140, 300, 180, 70, [("#A8D88A", "#6AA84A", "#3E7A2E")], 2503, n=110, size=(8, 16), inkw=0))
    out.append(dab_crown(D, 480, 290, 170, 70, [("#A8D88A", "#6AA84A", "#3E7A2E"), FLAMB], 2504, n=110, size=(8, 16), inkw=0))
    out.append(rejas(D, -12, 228, 612, 448, 2505, cell=74))
    out.append(f'<path d="{hg.org_rect(-10, 218, 620, 14, 2506, 0.4, 30, 1)}" fill="#FFFFFF"/>')
    # the ledge
    out.append(painted(D, rect_pts(-10, 468, 610, 610, 30, 2507, 0.5), ("#FFF6EC", "#F2E4D4", "#C8B098"), 2507, sdir=(0, 1), sk=0.06, angle=0, n=40, inkw=1.6, hi=0.2))
    out.append(f'<path d="{hg.org_rect(-10, 464, 620, 14, 2508, 0.4, 30, 1)}" fill="#E8D4BC"/>')
    for k in range(13):
        x = k * 50
        out.append(f'<path d="{hg.org_rect(x, 530, 46, 46, 2509 + k, 0.6, 12, 2)}" fill="{"#2F6CC6" if k % 2 else "#FFFFFF"}" opacity="0.85"/>')
        out.append(f'<path d="M {x + 23} {536} l 17 17 l -17 17 l -17 -17 Z" fill="{"#FFFFFF" if k % 2 else "#2F6CC6"}" opacity="0.8"/>')
    # mami's plants: in cans, in clay, hanging from the ceiling
    out.append(hanging_fern(D, 506, 214, 60, 2520))
    out.append(mata_en_lata(D, 96, 478, 76, 2521, "amapola", label_col="#2F6CC6"))
    out.append(aloe(D, 208, 478, 92, 2522))
    out.append(mata_en_lata(D, 318, 478, 70, 2523, "coleo", label_col="#F6C21C"))
    out.append(mata_en_lata(D, 422, 478, 64, 2524, "sansevieria", label_col="#D52B1E"))
    out.append(watering_can(D, 510, 478, 64, 2525))
    # lettering
    out.append(letters(D, 300, 150, "Mami", SERIF_IT, 156, "#B8264A", ["#D8486A", "#8A1030", "#E8688A"], 2530, max_w=360,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#FFD0DC"))
    out.append(ruled(300, 198, "Y SUS MATAS", "#2E6A3A", font=JOS, size=21, ls=8, line_w=34, gap=14))
    return finish_b(D, out, 2531)


# ================================================================ 26. ¡llegamos! — the island through the airplane window
@design("llegamos")
def llegamos():
    D = Doc2("prll")
    out = [sky(D, [(0, "#E8E4DC"), (1, "#CFC8BE")], 2601, 600, ["#F6F2EA", "#B8B0A6"], 80, angle=-80, sop=(0.05, 0.12))]
    out.append(soft_glow(D, 300, 350, 260, "#FFFFFF", 0.6))
    wx0, wy0, wx1, wy1 = 168, 218, 432, 512
    def win(x0, y0, x1, y1, r):
        pts = []
        for cx_, cy_, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
            for k in range(7):
                a = math.radians(a0 + k * 15)
                pts.append((cx_ + r * math.cos(a), cy_ + r * math.sin(a)))
        return pts
    outer = win(wx0 - 30, wy0 - 30, wx1 + 30, wy1 + 30, 110)
    out.append(painted(D, outer, ("#FFFFFF", "#F2EEE6", "#B8B0A4"), 2602, sdir=(0.5, 0.9), sk=0.08, angle=-90, n=30, inkw=1.6, hi=0.4))
    inner = win(wx0, wy0, wx1, wy1, 96)
    idd = smooth_closed(inner)
    out.append(f'<path d="{idd}" fill="#8AC8F0"/>')
    cid = D.clip(f'<path d="{idd}"/>')
    v = []
    # the view: sky, a sea of turquoise, the north coast of the island with beach, green hills and a little town
    v.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="120" fill="{D.lin([(0, "#5AAAE8"), (1, "#C8E8F8")])}"/>')
    v.append(sea(D, wy0 + 110, wy1, [(0, "#2EB8C8"), (1, "#1E8AB0")], 2603, ["#8EE8F0", "#1E6A9A", "#FFFFFF"], 40))
    land = [(wx0 - 10, wy0 + 150), (wx0 + 60, wy0 + 140), (wx0 + 130, wy0 + 160), (wx0 + 200, wy0 + 150), (wx1 + 10, wy0 + 170), (wx1 + 10, wy0 + 110), (wx0 - 10, wy0 + 112)]
    v.append(painted(D, land, ("#9ACB7A", "#5E9A4E", "#2E6A2E"), 2604, sdir=(0, 1), sk=0.1, angle=0, n=40, inkw=1.0, inkop=0.4, hi=0.3))
    v.append(hill(D, ridge([(wx0 - 10, wy0 + 118), (wx0 + 80, wy0 + 100), (wx0 + 170, wy0 + 112), (wx1 + 10, wy0 + 104)], 2605, 6, 3), wy0 + 130,
                  ("#A8B8C8", "#8A9EB4", "#6A7E98"), 2606, inkw=0, sop=(0.06, 0.16)))
    v.append(taper([(wx0 - 10, wy0 + 152), (wx0 + 60, wy0 + 142), (wx0 + 130, wy0 + 162), (wx0 + 200, wy0 + 152), (wx1 + 10, wy0 + 172)], 7, 7, "#F6E8C0"))
    v.append(taper([(wx0 - 10, wy0 + 160), (wx0 + 60, wy0 + 150), (wx0 + 130, wy0 + 170), (wx0 + 200, wy0 + 160), (wx1 + 10, wy0 + 180)], 8, 8, "#BFF4EC", 0.8))
    rnd = random.Random(2607)
    for _ in range(40):
        x, y = rnd.uniform(wx0, wx1), rnd.uniform(wy0 + 116, wy0 + 150)
        v.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{rnd.uniform(3, 6):.1f}" height="{rnd.uniform(2, 4):.1f}" fill="{rnd.choice(["#FFFFFF", "#F6D2C8", "#F8E8A0", "#C8E0F0"])}"/>')
    for _ in range(14):
        x, y = rnd.uniform(wx0, wx1), rnd.uniform(wy0 + 120, wy0 + 150)
        v.append(f'<path d="{blob(x, y, 5, 3, rnd.randint(0, 999), 0.2, 8)}" fill="#3E7A3A"/>')
    v.append(wave_lines(2608, (wx0, wy0 + 190, wx1, wy1), ["#FFFFFF", "#B8F0F4"], 30, (8, 20), 1.6, 2, (0.4, 0.8)))
    v.append(puff_cloud(D, wx0 + 70, wy0 + 260, 130, 2609, pal=("#FFFFFF", "#F6F8FA", "#C8D4E0")))
    v.append(puff_cloud(D, wx1 - 40, wy0 + 60, 110, 2610, pal=("#FFFFFF", "#F6F8FA", "#C8D4E0")))
    # the wing with its winglet
    wing = [(wx1 + 30, wy0 + 196), (wx0 + 112, wy1 - 62), (wx0 + 96, wy1 - 40), (wx1 + 30, wy1 + 20)]
    v.append(painted(D, wing, ("#FFFFFF", "#DCE0E8", "#8A92A0"), 2611, sdir=(0, 1), sk=0.12, angle=-30, n=30, inkw=1.8, hi=0.5))
    v.append(pline([(wx1 + 30, wy0 + 236), (wx0 + 112, wy1 - 54)], "#9AA2B0", 1.6, 2613, 0.7, 1))
    v.append(pline([(wx1 + 30, wy0 + 300), (wx0 + 104, wy1 - 46)], "#9AA2B0", 1.4, 2614, 0.6, 1))
    v.append(painted(D, [(wx0 + 112, wy1 - 62), (wx0 + 100, wy1 - 122), (wx0 + 86, wy1 - 124), (wx0 + 96, wy1 - 40)], ("#F4867A", "#D52B1E", "#8A1410"), 2612, sk=0.2, n=6, inkw=1.4, hi=0.4))
    v.append(f'<path d="{idd}" fill="{D.lin([(0, "#FFFFFF", 0.25), (0.4, "#FFFFFF", 0), (1, "#FFFFFF", 0.1)], 0, 0, 1, 1)}"/>')
    out.append(f'<g {cid}>{"".join(v)}</g>')
    # the shade pulled up, the window rim
    shade = [(wx0 + 30, wy0 + 6), (wx1 - 30, wy0 + 6), (wx1 - 18, wy0 + 30), (wx0 + 18, wy0 + 30)]
    out.append(f'<g {cid}>' + painted(D, rect_pts(wx0, wy0 - 10, wx1, wy0 + 24, 10, 2614, 0.4), ("#FFFFFF", "#ECE8E0", "#B8B0A4"), 2614, sk=0.2, angle=0, n=6, inkw=1.2, hi=0.4) + '</g>')
    out.append(ink(idd, "#8A847A", 3, 2615, 2, 0.8))
    out.append(ink(smooth_closed(outer), "#8A847A", 1.6, 2616, 1, 0.6))
    # clapping marks around the window
    for k, (x, y, a) in enumerate(((128, 300, 200), (472, 300, -20), (122, 420, 160), (478, 420, 20))):
        for j in range(3):
            ang = math.radians(a + (j - 1) * 22)
            out.append(pline([(x + math.cos(ang) * 6, y + math.sin(ang) * 6), (x + math.cos(ang) * 20, y + math.sin(ang) * 20)], "#D52B1E", 3, 2620 + k * 3 + j, 0.85, 1))
    # lettering
    out.append(letters(D, 300, 134, "¡Llegamos!", SERIF_IT, 116, "#1E4E9A", ["#3A6EC0", "#123A7A", "#5A8AD0"], 2630, max_w=450,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#C8DCF6"))
    out.append(ruled(300, 176, "Y TODO EL AVIÓN APLAUDIÓ", "#B8361E", font=JOS, size=19, ls=4, line_w=24, gap=10))
    return finish_b(D, out, 2631)


# ================================================================ 27. ¡nene, a comer! — mami calls from the kitchen window
def baseball_glove(D, cx, cy, s, seed, ang=-10):
    pts = rot([(cx - s * 0.5, cy + s * 0.4), (cx - s * 0.62, cy - s * 0.1), (cx - s * 0.5, cy - s * 0.5), (cx - s * 0.2, cy - s * 0.66), (cx + s * 0.1, cy - s * 0.62),
               (cx + s * 0.36, cy - s * 0.5), (cx + s * 0.6, cy - s * 0.2), (cx + s * 0.58, cy + s * 0.2), (cx + s * 0.3, cy + s * 0.5), (cx - s * 0.1, cy + s * 0.58)], cx, cy, ang)
    out = [cast(D, cx + 6, cy + s * 0.55, s * 0.7, s * 0.14, "#1A2A10", 0.45, seed)]
    out.append(painted(D, pts, ("#E0A060", "#A8642A", "#5A2E0E"), seed, sdir=(0.6, 0.8), sk=0.2, angle=ang - 60, n=16, inkw=1.8, hi=0.45))
    for k in range(4):
        a = rot([(cx - s * 0.36 + k * s * 0.22, cy - s * 0.58), (cx - s * 0.3 + k * s * 0.2, cy - s * 0.1)], cx, cy, ang)
        out.append(pline(a, "#5A2E0E", 1.6, seed + k, 0.7, 1))
    for k in range(6):
        a = rot([(cx - s * 0.4 + k * s * 0.15, cy + s * 0.3)], cx, cy, ang)[0]
        out.append(f'<path d="M {a[0] - 3:.1f} {a[1]:.1f} l 6 0" stroke="#F2D8A8" stroke-width="2"/>')
    out.append(f'<path d="{smooth_closed(rot(blob_pts(cx + s * 0.05, cy - s * 0.05, s * 0.28, s * 0.22, seed + 9, 0.1, 10), cx, cy, ang))}" fill="#7A3E14" opacity="0.6"/>')
    return "".join(out)


def baseball(D, cx, cy, r, seed):
    out = [cast(D, cx + 3, cy + r * 0.9, r, r * 0.25, "#1A2A10", 0.4, seed)]
    out.append(painted(D, blob_pts(cx, cy, r, r, seed, 0.02, 14), ("#FFFFFF", "#F2EEE6", "#B8B0A6"), seed, sk=0.2, n=4, inkw=1.4, hi=0.5))
    for sg in (-1, 1):
        seam = [(cx + sg * r * 0.55, cy - r * 0.8), (cx + sg * r * 0.3, cy), (cx + sg * r * 0.55, cy + r * 0.8)]
        out.append(pline(seam, "#D52B1E", 1.6, seed + sg, 0.9, 1))
    return "".join(out)


@design("a-comer")
def a_comer():
    D = Doc2("prac")
    out = [sky(D, [(0, "#FFE6A8"), (1, "#F8D088")], 2701, 600, ["#FFF2C8", "#E8B860"], 90, angle=-84, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 300, 320, 280, "#FFF8E0", 0.5))
    # the kitchen window: frame, Miami louvres tilted open, the stove and a caldero inside, steam drifting out
    wx0, wy0, wx1, wy1 = 100, 226, 500, 452
    out.append(f'<path d="{hg.org_rect(wx0 - 18, wy0 - 18, wx1 - wx0 + 36, wy1 - wy0 + 36, 2702, 0.6, 16, 2)}" fill="#FFFFFF"/>')
    out.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="#F6E2B8"/>')
    out.append(D.glow(300, 380, 200, "#FFE6A0", 0.5))
    # inside: a tiled wall, the stove and the steaming caldero of habichuelas
    for k in range(8):
        out.append(pline([(wx0 + k * 44, wy0), (wx0 + k * 44, wy1)], "#E8D0A0", 1.2, 2703 + k, 0.6, 1))
    out.append(f'<rect x="{wx0}" y="{wy1 - 40}" width="{wx1 - wx0}" height="40" fill="#E8E8EC"/>')
    out.append(f'<rect x="{wx0 + 40}" y="{wy1 - 44}" width="{wx1 - wx0 - 80}" height="10" fill="#2A2A32"/>')
    out.append(caldero(D, 214, 368, 86, 24, 40, 2711))
    out.append(f'<path d="{blob(214, 370, 74, 18, 2712, 0.02, 20)}" fill="#8A3A22"/>')
    out.append(specks(2713, (148, 358, 280, 384), ["#C86A4A", "#5A1A0A", "#F2C04A", "#F6E0B0"], 60, (1.6, 3.4), (0.7, 1)))
    out.append(caldero(D, 392, 372, 76, 22, 36, 2716))
    out.append(f'<path d="{blob(392, 374, 64, 16, 2717, 0.02, 20)}" fill="#F6E6B8"/>')
    out.append(dashes(2718, None, (334, 362, 450, 388), 120, ["#FFFFFF", "#F6E6B8", "#E8D29A"], L=(3, 5), w=(2, 3)))
    out.append(steam(214, 342, 90, 2714, "#FFFFFF", 3, 28, 7, 0.8))
    out.append(steam(392, 350, 80, 2719, "#FFFFFF", 2, 28, 6, 0.75))
    # louvres (open) and rejas over them
    for k in range(5):
        y = wy0 + 10 + k * 26
        out.append(f'<path d="M {wx0 + 4} {y} L {wx1 - 4} {y} L {wx1 - 4} {y + 7} L {wx0 + 4} {y + 7} Z" fill="#D8DCE4" opacity="0.92"/>')
        out.append(pline([(wx0 + 4, y + 7), (wx1 - 4, y + 7)], "#7A8090", 1.4, 2715 + k, 0.8, 1))
    out.append(f'<path d="M 300 {wy0} L 300 {wy1}" stroke="#FFFFFF" stroke-width="6"/>')
    val = [(wx0 - 6, wy0 - 4), (wx1 + 6, wy0 - 4)] + [(wx1 + 6 - k * (wx1 - wx0 + 12) / 12, wy0 + 30 + (8 if k % 2 else 0)) for k in range(13)]
    out.append(cloth(D, val, "#D52B1E", 2729, cell=11, light=(0, 0, 0.3, 1), inkw=1.4))
    # sill with a little plant can
    out.append(painted(D, rect_pts(wx0 - 30, wy1 + 14, wx1 + 30, wy1 + 30, 20, 2723, 0.4), ("#FFFFFF", "#F2EEE6", "#B8B0A6"), 2723, sk=0.2, angle=0, n=8, inkw=1.6, hi=0.4))
    out.append(mata_en_lata(D, 470, wy1 + 16, 40, 2724, "coleo", label_col="#2F6CC6"))
    # the steam (and the smell) drifting out the window
    for k, (x, y) in enumerate(((210, 222), (260, 200), (330, 214))):
        out.append(steam(x, y + 20, 60, 2725 + k, "#FFFFFF", 1, 0, 6, 0.65))
    # the yard: grass, the glove and ball and a bat left mid-game
    out.append(hill(D, [(-20, 504), (200, 498), (400, 504), (620, 498)], 620, ("#A8D27A", "#6AA84A", "#2E6A2A"), 2730, inkw=1.4, inkop=0.4))
    out.append(grass(2731, (0, 498, 600, 600), ["#4E8A2E", "#7AB04A", "#3A6A22", "#A8D06A"], 180, (8, 16), 1.4))
    out.append(baseball_glove(D, 164, 540, 86, 2732, -14))
    out.append(baseball(D, 246, 560, 18, 2733))
    out.append(taper([(310, 568), (530, 516)], 9, 20, "#C88A4A") + taper([(310, 563), (530, 509)], 2, 5, "#F2C890", 0.8) + disc(310, 568, 7, "#8A5428"))
    # lettering on the wall above the window
    out.append(letters(D, 300, 128, "¡Nene, a comer!", SERIF_IT, 92, "#B8261E", ["#D8483A", "#8A1408", "#E8684A"], 2740, max_w=470,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#FFD0C0"))
    out.append(ruled(300, 172, "¡QUE SE ENFRÍA!", "#1E4E9A", font=JOS, size=20, ls=7, line_w=34, gap=14))
    return finish_b(D, out, 2741)


# ================================================================ 28. piñones — frituras by the sea
def alcapurria(D, cx, cy, L, ang, seed):
    """Alcapurria: a torpedo of grated yautía and green banana dough, deep-fried dark gold, bumpy."""
    rnd = random.Random(seed)
    pts = rot(blob_pts(cx, cy, L / 2, L * 0.17, seed, 0.06, 16), cx, cy, ang)
    out = [cast(D, cx + 5, cy + L * 0.16, L * 0.5, L * 0.08, "#3A1A04", 0.4, seed)]
    out.append(painted(D, pts, ("#E8A050", "#B0602A", "#5E2A0A"), seed, sdir=(0.3, 1), sk=0.25, angle=ang, n=14, inkw=1.6, hi=0.5))
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    bumps = "".join(disc(cx + rnd.uniform(-L * 0.45, L * 0.45), cy + rnd.uniform(-L * 0.14, L * 0.14), rnd.uniform(1.2, 2.6), rnd.choice(["#FFD08A", "#7A3A10"]), rnd.uniform(0.5, 0.9))
                    for _ in range(int(L * 0.6)))
    out.append(f'<g {cid}>{bumps}</g>')
    return "".join(out)


def bacalaito(D, cx, cy, r, seed, rot_=0):
    """Bacalaíto: a big, thin, lacy codfish fritter, crisp golden with bubbled holes."""
    rnd = random.Random(seed)
    pts = []
    for i in range(30):
        a = 2 * math.pi * i / 30
        rr = r * rnd.uniform(0.82, 1.08)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.62))
    pts = rot(pts, cx, cy, rot_)
    out = [cast(D, cx + 5, cy + r * 0.4, r * 1.05, r * 0.5, "#3A1A04", 0.35, seed)]
    out.append(painted(D, pts, ("#FFDA8A", "#E8A848", "#9A5A18"), seed, sdir=(0.4, 0.9), sk=0.12, angle=rot_, n=20, inkw=1.4, hi=0.5))
    d = smooth_closed(pts)
    cid = D.clip(f'<path d="{d}"/>')
    holes = "".join(f'<path d="{blob(cx + rnd.uniform(-r * 0.8, r * 0.8), cy + rnd.uniform(-r * 0.45, r * 0.45), rnd.uniform(2, 5), rnd.uniform(1.4, 3), rnd.randint(0, 999), 0.3, 8)}" fill="{rnd.choice(["#9A5A18", "#C8802E", "#FFF0C0"])}" opacity="0.8"/>'
                    for _ in range(int(r * 0.6)))
    out.append(f'<g {cid}>{holes}</g>')
    return "".join(out)


def coco_frio(D, cx, base, s, seed):
    """A green drinking coconut with its top machete-cut, a striped straw."""
    out = [cast(D, cx + 6, base, s * 0.6, s * 0.1, "#3A1A04", 0.4, seed)]
    body = [(cx - s * 0.5, base - s * 0.5), (cx - s * 0.42, base - s * 0.1), (cx - s * 0.2, base), (cx + s * 0.2, base), (cx + s * 0.42, base - s * 0.1), (cx + s * 0.5, base - s * 0.5),
            (cx + s * 0.4, base - s * 0.85), (cx + s * 0.18, base - s * 1.0), (cx - s * 0.18, base - s * 1.0), (cx - s * 0.4, base - s * 0.85)]
    out.append(painted(D, body, ("#B8DC70", "#6AA83A", "#2E6A1A"), seed, sdir=(0.7, 0.6), sk=0.2, angle=-80, n=16, inkw=1.6, hi=0.5))
    cut = smooth_closed(ell_pts(cx, base - s * 0.98, s * 0.2, s * 0.07, 0, 360, 14))
    out.append(f'<path d="{cut}" fill="#FFFDF2"/>' + f'<path d="{smooth_closed(ell_pts(cx, base - s * 0.98, s * 0.12, s * 0.04, 0, 360, 14))}" fill="#E8E0C8"/>')
    out.append(taper([(cx + 2, base - s * 0.98), (cx + s * 0.3, base - s * 1.55)], 6, 6, "#FFFFFF"))
    for k in range(4):
        t = 0.2 + k * 0.2
        out.append(taper([(cx + 2 + s * 0.28 * t, base - s * 0.98 - s * 0.57 * t), (cx + 2 + s * 0.28 * (t + 0.08), base - s * 0.98 - s * 0.57 * (t + 0.08))], 6, 6, "#D52B1E"))
    return "".join(out)


@design("pinones")
def pinones():
    D = Doc2("prpn")
    out = [sky(D, [(0, "#4AA8E8"), (0.6, "#9AD6F4"), (1, "#E8F6F4")], 2801, 330, ["#FFFFFF", "#7AC8EE"], 50)]
    out.append(puff_cloud(D, 120, 240, 120, 2802))
    out.append(puff_cloud(D, 470, 200, 100, 2803))
    out.append(sea(D, 300, 420, [(0, "#1E9AC8"), (1, "#3AC8C8")], 2804, ["#8EE8F0", "#1E6A9A", "#FFFFFF"], 40, ticks=["#FFFFFF"]))
    out.append(f'<path d="M 0 400 Q 150 392 300 404 T 600 398 L 600 440 L 0 440 Z" fill="#F6E2B0"/>')
    out.append(wave_lines(2805, (0, 392, 600, 404), ["#FFFFFF"], 14, (20, 50), 2.2, 2, (0.6, 0.9)))
    out.append(palm(D, (90, 440), (130, 236), 2806, L=88, width=13))
    out.append(palm(D, (520, 440), (490, 250), 2807, L=80, width=12))
    out.append(palm(D, (560, 440), (580, 300), 2808, L=60, width=9))
    # the kiosk: a painted wooden front with a hand-lettered board and a zinc roof edge
    out.append(painted(D, rect_pts(40, 300, 560, 330, 20, 2810, 0.6), ("#E8E8EE", "#B8BCC6", "#6A707A"), 2810, sk=0.2, angle=0, n=14, inkw=1.6, hi=0.4))
    for k in range(14):
        out.append(pline([(46 + k * 37, 302), (46 + k * 37, 328)], "#8A909A", 1.4, 2811 + k, 0.6, 1))
    for x in (60, 540):
        out.append(painted(D, rect_pts(x - 10, 326, x + 10, 470, 10, 2830 + x, 0.4), ("#F6D24A", "#E8A82A", "#8A5A0A"), 2830 + x, sdir=(1, 0), sk=0.2, angle=-90, n=10, inkw=1.4, hi=0.4))
    board = rect_pts(150, 334, 450, 384, 20, 2840, 0.8)
    out.append(painted(D, board, ("#F4867A", "#D52B1E", "#8A1410"), 2840, sk=0.12, angle=0, n=16, inkw=1.8, hi=0.35))
    out.append(f'<text x="300" y="373" text-anchor="middle" {ANTON} font-size="36" letter-spacing="5" fill="#FFF6DC">FRITURAS</text>')
    # the counter and a paper plate of frituras, the coco frío
    out.append(painted(D, rect_pts(-10, 450, 610, 476, 30, 2841, 0.5), ("#E0A868", "#A86A34", "#5A3416"), 2841, sdir=(0, 1), sk=0.2, angle=0, n=24, inkw=1.8, hi=0.45))
    out.append(painted(D, rect_pts(-10, 476, 610, 610, 30, 2842, 0.5), ("#7AD0C8", "#1F9A8A", "#0E5A50"), 2842, sdir=(0, 1), sk=0.1, angle=-88, n=40, inkw=1.6, hi=0.2))
    for k in range(13):
        out.append(pline([(k * 48, 478), (k * 48 + 1, 610)], "#0E5A50", 1.6, 2843 + k, 0.5, 1))
    pcx, pcy = 270, 486
    out.append(cast(D, pcx + 10, pcy + 14, 170, 30, "#1A2A10", 0.45, 2860))
    out.append(painted(D, ell_pts(pcx, pcy, 168, 50, 0, 360, 36), ("#FFFFFF", "#F6F2EA", "#C8C0B0"), 2861, sk=0.08, n=20, inkw=1.6, hi=0.4))
    for i in range(36):
        a = 2 * math.pi * i / 36
        out.append(pline([(pcx + math.cos(a) * 140, pcy + math.sin(a) * 40), (pcx + math.cos(a) * 166, pcy + math.sin(a) * 49)], "#D8D0C4", 1.2, 2862 + i, 0.8, 1))
    out.append(bacalaito(D, pcx - 70, pcy - 6, 62, 2900, -8))
    out.append(bacalaito(D, pcx + 40, pcy - 14, 56, 2901, 10))
    out.append(alcapurria(D, pcx - 20, pcy + 6, 96, -10, 2902))
    out.append(alcapurria(D, pcx + 80, pcy + 8, 90, 12, 2903))
    out.append(coco_frio(D, 486, 500, 92, 2904))
    # a little bottle of pique
    bx, bb = 102, 476
    out.append(cast(D, bx + 4, bb, 18, 4, strength=0.4, seed=2905))
    out.append(painted(D, [(bx - 14, bb), (bx - 14, bb - 46), (bx - 6, bb - 58), (bx - 6, bb - 74), (bx + 6, bb - 74), (bx + 6, bb - 58), (bx + 14, bb - 46), (bx + 14, bb)],
                       ("#FFE0A0", "#F2A23A", "#9A5A0A"), 2906, sk=0.2, n=6, inkw=1.4, hi=0.5))
    for k, (dx, dy, c) in enumerate(((-4, -20, "#D52B1E"), (4, -30, "#3EA84A"), (-2, -40, "#F26A1E"))):
        out.append(f'<path d="{blob(bx + dx, bb + dy, 3, 8, 2907 + k, 0.1, 8, 20)}" fill="{c}"/>')
    out.append(f'<rect x="{bx - 7}" y="{bb - 82}" width="14" height="9" fill="#F2F2F6" stroke="#8A8A92"/>')
    # lettering
    out.append(letters(D, 300, 128, "Piñones", SERIF_IT, 124, "#FFFFFF", ["#FFFFFF", "#E8F6FC", "#FFF6E8"], 2920, max_w=420,
                       shadow="#123A7A", soff=(0.022, 0.036), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 172, "FRITURAS FRENTE AL MAR", "#123A7A", font=JOS, size=19, ls=5, line_w=26, gap=12))
    return finish_b(D, out, 2921)


# ================================================================ 29. tembleque — the wobbly coconut pudding
@design("tembleque")
def tembleque():
    D = Doc2("prtb")
    out = [paper(D.nid(), "#F4C8A8", "#8A5A3A", 2951)]
    out.append(blooms(2952, ["#F8D8C0", "#E8A880", "#FFE8D8"], 7, (0, 0, 600, 600), (100, 200), (0.1, 0.18)))
    out.append(soft_glow(D, 300, 380, 300, "#FFFFFF", 0.6))
    # a lace doily, the plate, the molded tembleque with a slice cut out
    cx, cy = 300, 420
    lace = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        lace.append((cx + math.cos(a) * (230 + 12 * math.cos(a * 16)), cy + math.sin(a) * (92 + 5 * math.cos(a * 16))))
    out.append(f'<path d="{smooth_closed(lace)}" fill="#FFFFFF" opacity="0.92"/>')
    for i in range(24):
        a = 2 * math.pi * i / 24
        out.append(f'<ellipse cx="{cx + math.cos(a) * 200:.1f}" cy="{cy + math.sin(a) * 80:.1f}" rx="9" ry="4" fill="#F4C8A8"/>')
        out.append(f'<ellipse cx="{cx + math.cos(a) * 168:.1f}" cy="{cy + math.sin(a) * 67:.1f}" rx="4" ry="2" fill="#F4C8A8"/>')
    out.append(ink(smooth_closed(lace), "#B8C8D0", 1.2, 2953, 1, 0.6))
    out.append(cast(D, cx + 10, cy + 12, 170, 50, "#2A4A5A", 0.3, 2954))
    out.append(painted(D, ell_pts(cx, cy, 170, 58, 0, 360, 36), ("#FFFFFF", "#F2F6F8", "#B8C4CC"), 2955, sk=0.06, n=20, inkw=1.8, hi=0.4))
    for i in range(30):
        a = 2 * math.pi * i / 30
        out.append(disc(cx + math.cos(a) * 156, cy + math.sin(a) * 52, 2.6, "#2F6CC6", 0.8))
    # the tembleque: a flower-molded dome with ridges, the wedge removed at the front right
    top_y, base_y = cy - 120, cy + 8
    lobes = 8
    def edge(t, yy, k):
        return (cx + 128 * k * math.cos(t) * (1 + 0.06 * math.cos(lobes * t)), yy + 44 * k * math.sin(t) * (1 + 0.06 * math.cos(lobes * t)))
    body = [edge(math.radians(a), base_y, 1.0) for a in range(0, 181, 10)] + [edge(math.radians(a), top_y + 20, 0.82) for a in range(180, -1, -10)]
    out.append(painted(D, body, ("#FFFFFF", "#F8F4EA", "#D0C8B4"), 2956, sdir=(0.8, 0.4), sk=0.14, angle=-90, n=30, inkw=1.8, hi=0.5))
    bd = smooth_closed(body)
    cid = D.clip(f'<path d="{bd}"/>')
    ridges = []
    for k in range(17):
        a = math.radians(k * 180 / 16)
        p0, p1 = edge(a, top_y + 20, 0.82), edge(a, base_y, 1.0)
        ridges.append(pline([p0, p1], "#E0D8C4", 2.2, 2957 + k, 0.7, 1))
    ridges.append(shade_over(D, bd, "#5A6A7A", 0.35, 0, 0, 1, 0, 0.5))
    out.append(f'<g {cid}>{"".join(ridges)}</g>')
    topd = smooth_closed([edge(math.radians(a), top_y + 20, 0.82) for a in range(0, 360, 10)])
    out.append(f'<path d="{topd}" fill="#FFFDF6"/>')
    out.append(specks(2958, (cx - 100, top_y - 20, cx + 100, top_y + 56), ["#A8682E", "#8A4E1E", "#C8884A"], 160, (0.8, 1.8), (0.6, 1)))
    out.append(ink(topd, "#C8BCA8", 1.4, 2959, 1, 0.7))
    out.append(f'<path d="{blob(cx - 60, top_y + 10, 30, 6, 2960, 0.2, 10)}" fill="#FFFFFF" opacity="0.8"/>')
    out.append(taper([(cx - 96, top_y + 52), (cx - 104, top_y + 90), (cx - 98, top_y + 120)], 6, 3, "#FFFFFF", 0.9))
    # wobble marks
    for sg in (-1, 1):
        for k in range(2):
            x = cx + sg * (150 + k * 16)
            out.append(pline([(x, cy - 70), (x + sg * 4, cy - 50), (x, cy - 30)], "#2A5A8A", 2.6, 2961 + k + sg, 0.8, 1))
    # a slice on its own little plate with a spoon, cinnamon sticks, a hibiscus
    sx, sy = 470, 534
    out.append(cast(D, sx + 6, sy + 8, 74, 18, "#2A4A5A", 0.35, 2965))
    out.append(painted(D, ell_pts(sx, sy, 74, 24, 0, 360, 24), ("#FFFFFF", "#F2F6F8", "#B8C4CC"), 2966, sk=0.06, n=8, inkw=1.6, hi=0.4))
    wedge = [(sx - 40, sy - 4), (sx + 20, sy - 14), (sx + 34, sy + 2), (sx + 34, sy - 26), (sx + 20, sy - 40), (sx - 40, sy - 30)]
    out.append(painted(D, wedge, ("#FFFFFF", "#F8F4EA", "#D0C8B4"), 2967, sdir=(0.8, 0.4), sk=0.14, n=8, inkw=1.4, hi=0.5))
    out.append(specks(2968, (sx - 38, sy - 40, sx + 30, sy - 28), ["#A8682E", "#8A4E1E"], 30, (0.8, 1.6), (0.6, 1)))
    out.append(taper([(sx + 40, sy + 10), (sx + 96, sy - 14)], 5, 4, "#C8CCD4") + f'<path d="{blob(sx + 34, sy + 12, 11, 6, 2969, 0.1, 8, -20)}" fill="#C8CCD4"/>')
    out.append(cinnamon_stick(D, 70, 560, 170, 540, 14, 2970))
    out.append(cinnamon_stick(D, 84, 576, 186, 562, 14, 2971))
    out.append(hibiscus(D, 112, 470, 30, ROJO, 2972, 20))
    out.append(leaf_simple(D, 120, 480, 46, 13, 40, SELVA, 2973, vein=True, inkw=1))
    # lettering
    out.append(letters(D, 300, 136, "tembleque", SERIF_IT, 116, "#2A5A8A", ["#3E78B0", "#1A3E66", "#5A90C8"], 2980, max_w=430,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#D8ECF6"))
    out.append(ruled(300, 178, "BLANQUITO Y CON CANELA", "#8A4A1E", font=JOS, size=19, ls=5, line_w=26, gap=12))
    return finish_b(D, out, 2981)


# ================================================================ 30. día de reyes — the shoebox of grass for the camels
def camel(x, base, s, col, flip=1):
    """Camel silhouette walking: hump, long neck, legs mid-stride."""
    f = flip
    P = lambda pts: [(x + px * s * f, base + py * s) for px, py in pts]
    body = P([(-22, -30), (-14, -46), (-4, -50), (6, -44), (14, -34), (24, -34), (30, -46), (34, -56), (42, -58), (46, -54), (40, -50), (36, -40), (32, -28),
              (26, -22), (24, 0), (20, 0), (18, -20), (6, -22), (2, 0), (-2, 0), (-4, -20), (-14, -20), (-16, 0), (-20, 0), (-20, -22), (-26, -26)])
    return f'<path d="{smooth_closed(body)}" fill="{col}"/>' + pline(P([(-24, -28), (-30, -20), (-28, -10)]), col, 2 * s, int(x), 1, 1)


@design("dia-de-reyes")
def dia_de_reyes():
    D = Doc2("prdr")
    # night window over the hills: the star, three camels on the ridge
    out = [sky(D, [(0, "#0E1640"), (0.6, "#24306A"), (1, "#3A3A7A")], 3001, 600, ["#2A3A80", "#0A1030"], 60)]
    wx0, wy0, wx1, wy1 = 150, 196, 450, 400
    out.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="{D.lin([(0, "#0E1A4A"), (1, "#3A3A82")])}"/>')
    rnd = random.Random(3002)
    for _ in range(40):
        out.append(disc(rnd.uniform(wx0, wx1), rnd.uniform(wy0, wy1 - 60), rnd.uniform(0.6, 1.6), "#FFF6D8", rnd.uniform(0.4, 1)))
    out.append(D.glow(380, 236, 70, "#FFF0B0", 0.7))
    out.append(f'<path d="{star_d(380, 236, 14, 4)}" fill="#FFF6D0"/>')
    out.append(taper([(380, 252), (360, 300)], 3, 0.5, "#FFF0B0", 0.6))
    hills = [(wx0, 372), (220, 352), (300, 362), (380, 344), (wx1, 360), (wx1, wy1), (wx0, wy1)]
    out.append(f'<path d="{smooth_closed(hills)}" fill="#1A2448"/>')
    for k, (x, sc) in enumerate(((246, 0.8), (290, 0.85), (334, 0.8))):
        out.append(camel(x, 356 - k * 2, sc, "#0A0E24"))
    # the room: a warm wall, window frame and curtains, a little tree with lights
    room = f"M -10 -10 L 610 -10 L 610 610 L -10 610 Z M {wx0} {wy0} L {wx0} {wy1} L {wx1} {wy1} L {wx1} {wy0} Z"
    out.append(f'<path d="{room}" fill="#E8B880" fill-rule="evenodd"/>')
    out.append(f'<path d="{room}" fill="{D.rad([(0, "#FFE0A8", 0.6), (1, "#8A4A2A", 0.5)], cx=0.5, cy=0.6, r=0.7)}" fill-rule="evenodd"/>')
    out.append(f'<path d="{hg.org_rect(wx0 - 14, wy0 - 14, wx1 - wx0 + 28, wy1 - wy0 + 28, 3003, 0.5, 14, 2)}" fill="none" stroke="#FFFFFF" stroke-width="12"/>')
    out.append(f'<path d="M 300 {wy0} L 300 {wy1} M {wx0} 298 L {wx1} 298" stroke="#FFFFFF" stroke-width="6"/>')
    out.append(painted(D, rect_pts(wx0 - 60, wy0 - 22, wx1 + 60, wy0 - 12, 20, 3009, 0.3), ("#E8C08A", "#B08040", "#6A4418"), 3009, sk=0.2, angle=0, n=8, inkw=1.4, hi=0.4))
    for sg in (-1, 1):
        x = 300 + sg * 176
        cur = [(x - sg * 34, wy0 - 14), (x + sg * 40, wy0 - 14), (x + sg * 44, wy1 + 60), (x + sg * 6, wy1 + 64), (x - sg * 8, 330), (x - sg * 30, 300)]
        out.append(painted(D, cur, ("#F48A7A", "#D8463A", "#8A1A14"), 3004 + sg, sdir=(sg * 0.5, 0.6), sk=0.15, angle=-90, n=16, inkw=1.6, hi=0.35))
        for k in range(3):
            fx = x - sg * 20 + sg * k * 18
            out.append(pline([(fx, wy0 - 10), (fx + sg * 6, 300), (fx + sg * 12, wy1 + 56)], "#8A1A14", 1.6, 3020 + k + sg * 5, 0.5, 1))
        out.append(taper([(x - sg * 14, 332), (x + sg * 30, 338)], 8, 8, "#F6C21C"))
    out.append(painted(D, rect_pts(wx0 - 34, wy1 + 14, wx1 + 34, wy1 + 30, 20, 3006, 0.4), ("#FFFFFF", "#F2EEE6", "#B8B0A6"), 3006, sk=0.2, angle=0, n=8, inkw=1.6, hi=0.4))
    # the floor
    out.append(wood_planks(D, 470, 600, 3007, ("#C88A5A", "#8A5230", "#4A2410"), 3))
    out.append(f'<rect y="464" width="600" height="8" fill="#3A1A08" opacity="0.6"/>')
    # small christmas tree corner, lights
    out.append(hg.fir(D, 556, 476, 260, 140, 3008, cols=("#1E4A2A", "#2E6A3A", "#5A9A5A"), tiers=4))
    for _ in range(14):
        x = rnd.uniform(500, 600)
        y = rnd.uniform(280, 460)
        if abs(x - 540) < (y - 220) * 0.28:
            c = rnd.choice(["#FF5A4A", "#FFD24A", "#4AC8FF", "#7AE07A"])
            out.append(D.glow(x, y, 12, c, 0.6) + disc(x, y, 3, c))
    # the shoebox heaped with fresh-cut grass, a glass of water, a paper crown a child made
    bx0, by0, bx1, by1 = 160, 470, 420, 548
    out.append(cast(D, 300, 552, 160, 14, strength=0.5, seed=3009))
    out.append(painted(D, [(bx0, by0), (bx1, by0), (bx1 + 4, by1), (bx0 - 4, by1)], ("#E8C8A0", "#C8A070", "#7A5A30"), 3010, sdir=(0, 1), sk=0.15, angle=0, n=16, inkw=1.8, hi=0.4))
    out.append(f'<path d="{hg.org_rect(bx0 + 30, by0 + 18, 110, 34, 3011, 0.5, 12, 2)}" fill="#FFFDF4"/>')
    out.append(f'<text x="{bx0 + 85}" y="{by0 + 42}" text-anchor="middle" {SERIF_IT} font-size="19" fill="#B8261E">Reyes</text>')
    out.append(f'<path d="{smooth_closed(ell_pts(300, by0, 130, 12, 0, 360, 24))}" fill="#3A5A1E"/>')
    out.append(grass(3012, (bx0 - 4, by0 - 6, bx1 + 4, by0 + 8), ["#7AC84A", "#5AA83A", "#A8E06A", "#3E8A2A"], 360, (18, 44), 2.0, (-0.5, 0.5)))
    out.append(grass(3013, (bx0 + 10, by0 - 10, bx1 - 10, by0), ["#8AD85A", "#B8EA7A"], 120, (24, 50), 1.8, (-0.4, 0.4)))
    gx, gb = 470, 548
    out.append(cast(D, gx + 4, gb, 30, 6, strength=0.45, seed=3014))
    out.append(f'<path d="M {gx - 24} {gb - 70} L {gx + 24} {gb - 70} L {gx + 20} {gb} L {gx - 20} {gb} Z" fill="#CFE6F2" opacity="0.6"/>')
    out.append(f'<path d="M {gx - 23} {gb - 52} L {gx + 23} {gb - 52} L {gx + 20} {gb} L {gx - 20} {gb} Z" fill="#8AC8F0" opacity="0.55"/>')
    out.append(taper([(gx - 15, gb - 64), (gx - 13, gb - 8)], 4, 3, "#FFFFFF", 0.7))
    out.append(ink(pd([(gx - 24, gb - 70), (gx + 24, gb - 70), (gx + 20, gb), (gx - 20, gb)]), "#5A7A8A", 1.6, 3015, 1, 0.8))
    crown = [(76, 548), (76, 512), (90, 528), (102, 504), (114, 528), (128, 512), (128, 548)]
    out.append(painted(D, crown, ("#FFE89A", "#F2B83A", "#A8700A"), 3016, sk=0.2, n=6, inkw=1.6, hi=0.5))
    for k, (x, c) in enumerate(((90, "#D52B1E"), (102, "#2F6CC6"), (114, "#1F9A5A"))):
        out.append(disc(x, 538, 4, c))
    # lettering
    out.append(letters(D, 300, 110, "Día de Reyes", SERIF_IT, 96, "#7A1E1A", ["#9A3A2A", "#5A0E0A", "#B85A3A"], 3030, max_w=440,
                       shadow="#FFE0B0", soff=(0.016, 0.028), angle=-40, hi="#F2B8A0"))
    out.append(ruled(300, 152, "LA YERBITA PA’ LOS CAMELLOS", "#2E5A1E", font=JOS, size=18, ls=3, line_w=18, gap=10))
    return finish_b(D, out, 3031)


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
