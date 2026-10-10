"""Christmas, hand-painted (gouache / storybook) edition, part B.

Repaints naughty-or-nice, fresh-cut-trees, joy-to-the-world, snow-much-fun, ho-ho-ho, wrapped-with-love and
oh-deer, and adds eight new pieces. Every magnet is built like a small gouache painting: warm paper or a brushy
wash ground, organic shapes laid in as layered washes, visible brush strokes clipped inside each form, warm-brown
ink drawing on the main objects, snow with blue-violet shadows, warm window glow, brush-textured lettering and a
final paper grain.

Run: python3 christmas_gouache_b.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save, star_points
import paint as pt
from gouache import blob, blob_pts, grain, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from poster import ANTON

COL = "christmas"

# ---------------------------------------------------------------- shared palette (keep in step with part A)
INK = "#3A2418"          # warm brown pen line
PAPER = "#F4ECDD"
FLECK = "#8A6A4A"
CREAM = "#FBF4E6"
GREEN, GREEN_D, GREEN_L, SAGE = "#2C5B45", "#173A2C", "#4F8160", "#86A584"
CRAN, CRAN_D, RED, RED_L = "#A3243A", "#6E1526", "#C8383A", "#E2705E"
GOLD, GOLD_D, GOLD_L = "#D9A441", "#A8741E", "#F2D284"
ICE, ICE_D, ICE_L = "#BFD5E2", "#86A8C0", "#E3EEF3"
SNOW = "#FBF9F4"
SHADE, SHADE_D, SHADE_L = "#B4B6E0", "#8C8FC8", "#D8DAF0"   # blue-violet snow shadow
PINK, PINK_L = "#E7A3AC", "#F6D3D3"
NAVY, NAVY_D = "#22325A", "#141E3A"
BROWN, BROWN_L, BROWN_D = "#8A5A36", "#B88352", "#5A3620"


def _hx(c):
    c = c.lstrip("#")
    return [int(c[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    A, B = _hx(a), _hx(b)
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * t) for x, y in zip(A, B))


def lt(c, t):
    return mix(c, "#FFFFFF", t)


def dk(c, t):
    return mix(c, "#000000", t)


def F(v):
    return f"{v:.1f}"


class C:
    """Per-design id factory and gradient collector (every id is prefixed with the design key)."""

    def __init__(self, u):
        self.u, self.n, self.defs = u, 0, []

    def id(self, p="g"):
        self.n += 1
        return f"{self.u}-{p}{self.n}"

    def lg(self, stops, x1=0, y1=0, x2=0, y2=1):
        i = self.id()
        self.defs.append(pt.lg(i, stops, x1, y1, x2, y2))
        return i

    def rg(self, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None):
        i = self.id()
        self.defs.append(pt.rg(i, stops, cx, cy, r, fx, fy))
        return i

    def glow(self, x, y, r, col, s=0.7):
        g = self.rg([(0, col, s), (0.35, col, s * 0.45), (1, col, 0)])
        return f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(r)}" fill="url(#{g})"/>'

    def oglow(self, x, y, rx, ry, col, s=0.7):
        g = self.rg([(0, col, s), (0.4, col, s * 0.45), (1, col, 0)])
        return f'<ellipse cx="{F(x)}" cy="{F(y)}" rx="{F(rx)}" ry="{F(ry)}" fill="url(#{g})"/>'

    def svg(self):
        return "<defs>" + "".join(self.defs) + "</defs>"


# ---------------------------------------------------------------- painting primitives
def bbox(pts, pad=6):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad)


def shape(c, pts, base, tints, seed, angle=-80, n=None, inkc=INK, iw=2.2, length=(12, 34), width=(2, 5),
          op=(0.18, 0.48), curve=0.2, layers=2, edge=None, ink_op=0.8, d=None):
    """One painted form: layered wash, clipped brush strokes in related tints, then the pen line."""
    d = d or smooth_closed(pts)
    box = bbox(pts)
    area = (box[2] - box[0]) * (box[3] - box[1])
    n = n if n is not None else max(12, int(area / 160))
    out = [wash(d, base, seed, layers=layers, spread=1.0, opacity=0.45, edge=edge)]
    if tints and n:
        out.append(strokes(c.id("s"), d, box, tints, seed + 1, n=n, angle=angle, length=length, width=width, opacity=op, curve=curve))
    if inkc:
        out.append(ink(d, inkc, iw, seed + 2, 2, ink_op))
    return "".join(out)


def clip_strokes(c, d, box, tints, seed, op=(0.18, 0.5), **kw):
    return strokes(c.id("s"), d, box, tints, seed, opacity=op, **kw)


def wash_bg(c, base, tints, seed, angle=-18, n=320, length=(40, 120), width=(6, 16), op=(0.08, 0.26), box=(-40, -40, 640, 640)):
    """Full-bleed brushy gouache ground."""
    d = "M -20 -20 L 620 -20 L 620 620 L -20 620 Z"
    return (f'<rect width="600" height="600" fill="{base}"/>'
            + strokes(c.id("bg"), d, box, tints, seed, n=n, angle=angle, length=length, width=width, opacity=op, curve=0.15))


def spatter(seed, n, box, colors, r=(0.8, 3.0), op=(0.25, 0.75), avoid=()):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n * 3):
        if len(out) >= n:
            break
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if any(a <= x <= b and cc <= y <= dd for a, cc, b, dd in avoid):
            continue
        rr = rnd.uniform(*r)
        if rr > 2.2:
            out.append(f'<path d="{blob(x, y, rr, rr * rnd.uniform(0.8, 1.05), rnd.randint(0, 999), 0.12, 8)}" fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*op):.2f}"/>')
        else:
            out.append(f'<circle cx="{F(x)}" cy="{F(y)}" r="{rr:.2f}" fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


def flake(x, y, r, col="#FFFFFF", w=2.2, rot=0, op=0.95):
    """Hand-painted six-arm snowflake with little V ticks."""
    arms = []
    for k in range(6):
        a = math.radians(rot + 60 * k)
        ex, ey = x + r * math.cos(a), y + r * math.sin(a)
        mx, my = x + 0.55 * r * math.cos(a), y + 0.55 * r * math.sin(a)
        arms.append(f"M {F(x)} {F(y)} L {F(ex)} {F(ey)}")
        for s in (-1, 1):
            b = a + s * math.radians(42)
            arms.append(f"M {F(mx)} {F(my)} L {F(mx + 0.32 * r * math.cos(b))} {F(my + 0.32 * r * math.sin(b))}")
    return f'<path d="{" ".join(arms)}" stroke="{col}" stroke-width="{w}" stroke-linecap="round" fill="none" opacity="{op}"/>'


def glint(x, y, r, col="#FFF6D8", op=1.0):
    """Four-point painted sparkle."""
    k = r * 0.22
    d = (f"M {F(x)} {F(y - r)} Q {F(x + k)} {F(y - k)} {F(x + r)} {F(y)} Q {F(x + k)} {F(y + k)} {F(x)} {F(y + r)} "
         f"Q {F(x - k)} {F(y + k)} {F(x - r)} {F(y)} Q {F(x - k)} {F(y - k)} {F(x)} {F(y - r)} Z")
    return f'<path d="{d}" fill="{col}" opacity="{op}"/>'


def cast(x, y, rx, ry, col=SHADE_D, op=0.4, seed=1):
    return f'<path d="{blob(x, y, rx, ry, seed, 0.08, 14)}" fill="{col}" opacity="{op}"/>'


def lettering(c, x, y, s, font, size, color, tints, max_w=480, ls=0, anchor="middle", angle=-70, shadow=None,
              sdx=0.03, sdy=0.04, density=1.0, seed=1, extra="", outline=None, ow=2.0):
    """Brush-textured lettering: offset shadow, flat paint, brush strokes clipped to the glyphs."""
    size = fit_size(s, font, size, max_w, ls)
    w = measure(s, font, size, ls)
    if anchor == "middle":
        x0 = x - w / 2
        xa = x + ls / 2
    elif anchor == "end":
        x0, xa = x - w, x
    else:
        x0, xa = x, x
    t = esc(s)
    lsa = f' letter-spacing="{ls}"' if ls else ""
    base = f'text-anchor="{anchor}" {font} font-size="{size}"{lsa}{extra}'
    out = []
    if shadow:
        out.append(f'<text x="{F(xa + size * sdx)}" y="{F(y + size * sdy)}" {base} fill="{shadow}">{t}</text>')
    if outline:
        out.append(f'<text x="{F(xa)}" y="{F(y)}" {base} fill="none" stroke="{outline}" stroke-width="{ow}" stroke-linejoin="round">{t}</text>')
    out.append(f'<text x="{F(xa)}" y="{F(y)}" {base} fill="{color}">{t}</text>')
    rnd = random.Random(seed)
    n = int(70 * density * w / size) + 20
    uid = c.id("t")
    st = []
    for _ in range(n):
        px, py = rnd.uniform(x0 - size * 0.3, x0 + w + size * 0.1), rnd.uniform(y - size * 0.95, y + size * 0.25)
        L = rnd.uniform(size * 0.25, size * 0.6)
        ww = rnd.uniform(size * 0.025, size * 0.07)
        a = math.radians(angle + rnd.uniform(-10, 10))
        dx, dy = L * math.cos(a), L * math.sin(a)
        nx, ny = -math.sin(a), math.cos(a)
        mx, my = px + dx / 2, py + dy / 2
        st.append(f'<path d="M {F(px)} {F(py)} Q {F(mx + nx * ww)} {F(my + ny * ww)} {F(px + dx)} {F(py + dy)} Q {F(mx - nx * ww)} {F(my - ny * ww)} {F(px)} {F(py)} Z" fill="{rnd.choice(tints)}" opacity="{rnd.uniform(0.22, 0.6):.2f}"/>')
    out.append(f'<clipPath id="{uid}"><text x="{F(xa)}" y="{F(y)}" {base}>{t}</text></clipPath><g clip-path="url(#{uid})">{"".join(st)}</g>')
    return "".join(out), size, w


def L(*a, **k):
    return lettering(*a, **k)[0]


def snow_field(c, top_pts, seed, bottom=620, base=SNOW, inkc=None, shade_box=None, n=None):
    """Painted snow: off-white wash, horizontal blue-violet / white strokes, a lit crest line."""
    pts = list(top_pts) + [(top_pts[-1][0], bottom), (top_pts[0][0], bottom)]
    d = smooth_open(top_pts) + f" L {F(top_pts[-1][0])} {bottom} L {F(top_pts[0][0])} {bottom} Z"
    box = bbox(pts)
    out = [f'<path d="{d}" fill="{base}"/>']
    nn = n or int((box[2] - box[0]) * (box[3] - box[1]) / 260)
    out.append(strokes(c.id("sn"), d, box, [SHADE_L, SHADE, "#FFFFFF", ICE_L], seed, n=nn, angle=-4, length=(30, 90),
                       width=(2, 6), opacity=(0.18, 0.5), curve=0.12))
    if shade_box:
        out.append(strokes(c.id("sn"), d, shade_box, [SHADE, SHADE_D, SHADE_L], seed + 3, n=int(nn * 0.5), angle=-6,
                           length=(30, 80), width=(3, 8), opacity=(0.2, 0.45), curve=0.12))
    out.append(f'<path d="{smooth_open(top_pts)}" fill="none" stroke="#FFFFFF" stroke-width="3" opacity="0.8"/>')
    if inkc:
        out.append(ink(smooth_open(top_pts), inkc, 1.6, seed, 1, 0.45))
    return "".join(out)


def snow_lump(c, pts, seed, inkc=SHADE_D, iw=1.4, shade=True):
    """A soft cap of snow (on a branch, roof, ledge): white wash with violet underside strokes."""
    d = smooth_closed(pts)
    box = bbox(pts)
    out = [f'<path d="{d}" fill="{SNOW}"/>']
    if shade:
        lo = (box[0], box[1] + (box[3] - box[1]) * 0.45, box[2], box[3])
        out.append(strokes(c.id("sl"), d, lo, [SHADE, SHADE_L, SHADE_D], seed, n=max(8, int((box[2] - box[0]) / 3)), angle=-3,
                           length=(8, 26), width=(1.5, 4), opacity=(0.3, 0.6), curve=0.2))
    out.append(strokes(c.id("sl"), d, box, ["#FFFFFF"], seed + 1, n=max(6, int((box[2] - box[0]) / 6)), angle=-3,
                       length=(8, 26), width=(1.5, 3), opacity=(0.5, 0.9), curve=0.2))
    if inkc:
        out.append(ink(d, inkc, iw, seed + 2, 1, 0.5))
    return "".join(out)


def drape(a, b, thick, seed, drips=3, up=2.0):
    """Points for a snow cap draped along the segment a->b (thickness hangs below the line)."""
    rnd = random.Random(seed)
    (x1, y1), (x2, y2) = a, b
    n = 8
    top, bot = [], []
    for i in range(n + 1):
        t = i / n
        x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        bulge = math.sin(math.pi * t)
        top.append((x, y - up - bulge * thick * 0.35))
        drip = thick * (0.6 + 0.5 * bulge) * (1.6 if rnd.random() < drips / n else 1.0)
        bot.append((x + rnd.uniform(-1, 1), y + drip * (0.4 + 0.6 * bulge) * rnd.uniform(0.8, 1.15)))
    return top + bot[::-1]


def needles(c, pts, seed, length=(16, 30), greens=(GREEN_D, GREEN, GREEN_L, "#3E6E50", SAGE), density=1.0, w=2.6, spread=60, up_bias=0):
    """Pine needles brushed along a branch polyline."""
    rnd = random.Random(seed)
    back, front = [], []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        seg = math.hypot(x2 - x1, y2 - y1)
        ang = math.atan2(y2 - y1, x2 - x1)
        for i in range(int(seg * 0.9 * density)):
            t = rnd.random()
            x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            side = rnd.choice((-1, 1))
            a = ang + side * math.radians(rnd.uniform(spread - 25, spread + 15)) + math.radians(up_bias)
            Ln = rnd.uniform(*length)
            ex, ey = x + Ln * math.cos(a), y + Ln * math.sin(a)
            col = rnd.choice(greens)
            s = f'<path d="M {F(x)} {F(y)} Q {F((x + ex) / 2 + rnd.uniform(-2, 2))} {F((y + ey) / 2 + rnd.uniform(-2, 2))} {F(ex)} {F(ey)}" stroke="{col}" stroke-width="{rnd.uniform(w * 0.6, w):.1f}" opacity="{rnd.uniform(0.7, 1):.2f}"/>'
            (back if col in greens[:2] else front).append(s)
    return f'<g fill="none" stroke-linecap="round">{"".join(back)}{"".join(front)}</g>'


def berry(c, x, y, r, col=RED, seed=1):
    g = c.rg([(0, lt(col, 0.45)), (0.45, col), (1, dk(col, 0.35))], cx=0.4, cy=0.38, r=0.65, fx=0.32, fy=0.3)
    return (f'<path d="{blob(x, y, r, r, seed, 0.06, 10)}" fill="url(#{g})"/>'
            f'<path d="{blob(x, y, r, r, seed, 0.06, 10)}" fill="none" stroke="{dk(col, 0.5)}" stroke-width="1.1" opacity="0.6"/>'
            f'<circle cx="{F(x - r * 0.35)}" cy="{F(y - r * 0.38)}" r="{F(max(0.9, r * 0.22))}" fill="#FFFFFF" opacity="0.85"/>')


def holly_leaf(c, x, y, L, rot, seed, col=GREEN, iw=1.6):
    """Spiky holly leaf from (x, y) pointing along rot (degrees)."""
    rnd = random.Random(seed)
    pts = []
    k = 5
    for side in (1, -1):
        rng = range(k + 1) if side == 1 else range(k, -1, -1)
        for i in rng:
            t = i / k
            wv = math.sin(math.pi * t) * 0.3 * L
            spike = 1.18 if i % 2 == 1 else 0.82
            pts.append((t * L, side * wv * spike + rnd.uniform(-0.6, 0.6)))
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    P_ = [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]
    d = "M " + " ".join(f"{F(px)} {F(py)}" if j == 0 else f"Q {F((px + P_[j - 1][0]) / 2 + (py - P_[j - 1][1]) * 0.18)} {F((py + P_[j - 1][1]) / 2 - (px - P_[j - 1][0]) * 0.18)} {F(px)} {F(py)}" for j, (px, py) in enumerate(P_)) + " Z"
    tip = (x + L * ca, y + L * sa)
    out = [wash(d, col, seed, 2, 0.8, 0.5),
           strokes(c.id("hl"), d, bbox(P_), [lt(col, 0.3), dk(col, 0.3), lt(col, 0.15)], seed, n=int(L * 0.6), angle=rot + 35,
                   length=(L * 0.15, L * 0.35), width=(1, 2.4), opacity=(0.25, 0.55)),
           f'<path d="M {F(x)} {F(y)} Q {F((x + tip[0]) / 2 - sa * 2)} {F((y + tip[1]) / 2 + ca * 2)} {F(tip[0])} {F(tip[1])}" stroke="{lt(col, 0.45)}" stroke-width="1.6" fill="none" opacity="0.8"/>',
           ink(d, INK, iw, seed, 1, 0.7)]
    return "".join(out)


def holly(c, x, y, s, rot=0, seed=1, berries=3):
    out = [holly_leaf(c, x, y, 46 * s, rot - 150, seed, GREEN), holly_leaf(c, x, y, 42 * s, rot - 30, seed + 4, "#3B6E52"),
           holly_leaf(c, x, y, 34 * s, rot + 80, seed + 7, GREEN_D)]
    for k, (dx, dy) in enumerate(((-5, -3), (5, -4), (0, 5))[:berries]):
        out.append(berry(c, x + dx * s, y + dy * s, 7 * s, RED, seed + k))
    return "".join(out)


def fir(c, cx, base, h, w, seed, cols=(GREEN, GREEN_D, GREEN_L, "#3E6E50"), tiers=5, snow=True, inkc=INK, iw=1.8,
        trunk=BROWN_D, star=None):
    """Storybook fir: overlapping scalloped tiers (bottom first), clipped needle strokes, snow on the outer slopes."""
    rnd = random.Random(seed)
    out = []
    if trunk:
        tw = max(4, w * 0.08)
        out.append(shape(c, [(cx - tw, base + 2), (cx - tw * 0.8, base - h * 0.2), (cx + tw * 0.8, base - h * 0.2), (cx + tw, base + 2)],
                         trunk, [BROWN, dk(trunk, 0.2)], seed, angle=-90, n=8, iw=1.2, inkc=inkc))
    top = base - h
    body_h = h * 0.92
    for i in range(tiers):
        f = i / tiers                                   # 0 = bottom tier
        ybot = base - h * 0.1 - body_h * f * 0.86
        ytop = top + (ybot - top) * (0.05 if i == tiers - 1 else 0.0) - (0 if i == tiers - 1 else -body_h * 0.02)
        ytop = top if i == tiers - 1 else max(top, ybot - body_h * 0.42)
        wi = w / 2 * (1 - f * 0.78) * rnd.uniform(0.94, 1.04)
        pts = [(cx + rnd.uniform(-1, 1), ytop)]
        pts.append((cx + wi * 0.5, ytop + (ybot - ytop) * 0.55))
        pts.append((cx + wi, ybot + 2))
        sc = 4 + (1 if wi > 50 else 0)
        for k in range(1, sc):
            t = k / sc
            xx = cx + wi - 2 * wi * t
            pts.append((xx + wi / sc * 0.5, ybot - 3 + rnd.uniform(-1, 1)))
            pts.append((xx, ybot + 5 + rnd.uniform(-1, 2)))
        pts.append((cx - wi, ybot + 2))
        pts.append((cx - wi * 0.5, ytop + (ybot - ytop) * 0.55))
        d = smooth_closed(pts)
        col = cols[0]
        out.append(wash(d, col, seed + i, 2, 0.8, 0.5))
        b = bbox(pts)
        out.append(strokes(c.id("fl"), d, (b[0], b[1], cx, b[3]), [cols[1], cols[2], cols[3]], seed + i * 3, n=int(wi * 0.9) + 6,
                           angle=118, length=(8, 24), width=(1.5, 3.5), opacity=(0.3, 0.7), curve=0.15))
        out.append(strokes(c.id("fr"), d, (cx, b[1], b[2], b[3]), [cols[1], cols[1], cols[3]], seed + i * 3 + 1, n=int(wi * 0.9) + 6,
                           angle=62, length=(8, 24), width=(1.5, 3.5), opacity=(0.35, 0.75), curve=0.15))
        if inkc:
            out.append(ink(d, inkc, iw, seed + i, 1, 0.6))
        if snow:
            for sgn in (-1, 1):
                a = (cx + sgn * wi * 0.98, ybot + 1)
                bb = (cx + sgn * wi * 0.38, ytop + (ybot - ytop) * 0.62)
                out.append(snow_lump(c, drape(bb, a, max(3.5, wi * 0.09), seed + i * 7 + sgn, 2), seed + i * 5 + sgn, iw=1.0))
    if star:
        out.append(c.glow(cx, top - 4, h * 0.18, GOLD_L, 0.7))
        out.append(f'<path d="{smooth_closed(jitter([(x, y) for x, y in _star_xy(cx, top - 4, h * 0.075, h * 0.033)], seed, 0.6))}" fill="{GOLD}"/>')
    return "".join(out)


def _star_xy(cx, cy, ro, ri, n=5, rot=-90):
    pts = []
    for k in range(n * 2):
        r = ro if k % 2 == 0 else ri
        a = math.radians(rot + k * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def pstar(c, cx, cy, ro, col=GOLD, seed=1, ri=None, iw=1.4, tints=None):
    pts = _star_xy(cx, cy, ro, ri or ro * 0.45)
    d = "M " + " L ".join(f"{F(x)} {F(y)}" for x, y in jitter(pts, seed, ro * 0.03)) + " Z"
    return (wash(d, col, seed, 2, 0.6, 0.5) + strokes(c.id("st"), d, bbox(pts), tints or [GOLD_L, GOLD_D, "#FFF0B8"], seed, n=int(ro * 1.4),
                                                    angle=-60, length=(ro * 0.2, ro * 0.5), width=(1, ro * 0.08 + 1), opacity=(0.3, 0.6))
            + ink(d, INK, iw, seed, 1, 0.65))


def P(pts):
    return " ".join(f"{F(x)},{F(y)}" for x, y in pts)


def tx(pts, ox, oy, s=1.0, flip=False):
    return [(ox + (-x if flip else x) * s, oy + y * s) for x, y in pts]


def finish(c, body, seed=9, gop=0.9):
    return c.svg() + body + grain(c.id("gr"), INK, seed, gop)


# ================================================================ NEW: winter-wonder (cardinal on a snowy bough)
def cardinal(c, ox, oy, s=1.0, seed=3, flip=False):
    """Plump storybook cardinal facing left; (ox, oy) = body centre."""
    T = lambda pts: tx(pts, ox, oy, s, flip)
    out = []
    tail = T([(30, -4), (76, 22), (122, 52), (116, 64), (70, 52), (24, 30)])
    out.append(shape(c, tail, "#9E1C26", ["#C8343A", "#7A121C", "#B42630"], seed, angle=30 if not flip else 150, n=30, iw=2.0))
    body = T([(-50, -60), (-44, -80), (-30, -102), (-22, -118), (-14, -100), (-6, -88), (10, -80), (22, -62), (44, -38),
              (58, -10), (56, 18), (36, 42), (6, 54), (-24, 46), (-46, 26), (-58, -4), (-62, -34)])
    out.append(shape(c, body, "#C62F34", ["#E2524A", "#A81E28", "#F07058", "#B82830"], seed + 1, angle=-110 if not flip else -70,
                     n=150, length=(10, 26), width=(2, 5), op=(0.25, 0.55), iw=2.4))
    # belly light and back shadow
    cl = c.id("cb")
    out.append(f'<clipPath id="{cl}"><path d="{smooth_closed(body)}"/></clipPath><g clip-path="url(#{cl})">'
               f'<path d="{blob(*T([(-30, 22)])[0], 34 * s, 26 * s, seed + 2, 0.1)}" fill="#F48A6A" opacity="0.4"/>'
               f'<path d="{blob(*T([(46, -30)])[0], 30 * s, 50 * s, seed + 3, 0.1)}" fill="#7A121C" opacity="0.35"/></g>')
    wing = T([(-12, -34), (20, -42), (52, -16), (74, 22), (88, 44), (54, 34), (18, 16), (-6, -6)])
    out.append(shape(c, wing, "#A21E28", ["#7E141E", "#C23038", "#6A1018"], seed + 4, angle=28 if not flip else 152, n=60,
                     length=(10, 24), width=(1.5, 3.5), iw=2.0))
    # feather lines on the wing
    for k, (a, b) in enumerate((((4, -8), (60, 28)), ((14, -24), (72, 18)), ((30, -32), (82, 34)))):
        pa, pb = T([a, b])
        out.append(ink(f"M {F(pa[0])} {F(pa[1])} Q {F((pa[0] + pb[0]) / 2)} {F((pa[1] + pb[1]) / 2 - 6 * s)} {F(pb[0])} {F(pb[1])}", "#5A0C14", 1.6, seed + k, 1, 0.6))
    mask = T([(-66, -64), (-50, -68), (-34, -60), (-30, -46), (-38, -32), (-52, -24), (-64, -34)])
    out.append(shape(c, mask, "#2A1A1C", ["#4A3034", "#1A1012"], seed + 5, n=14, iw=1.2))
    beak = T([(-60, -62), (-88, -50), (-60, -38), (-54, -50)])
    out.append(shape(c, beak, "#EE8A3A", ["#F8B060", "#C8641E"], seed + 6, n=10, iw=1.6))
    out.append(ink(smooth_open(T([(-86, -50), (-66, -50), (-56, -50)])), "#7A3A12", 1.2, seed, 1, 0.8))
    e = T([(-42, -52)])[0]
    out.append(f'<circle cx="{F(e[0])}" cy="{F(e[1])}" r="{F(4.6 * s)}" fill="#120A0A"/><circle cx="{F(e[0] - 1.4 * s)}" cy="{F(e[1] - 1.6 * s)}" r="{F(1.6 * s)}" fill="#FFFFFF"/>')
    # crest highlight
    out.append(ink(smooth_open(T([(-40, -82), (-28, -104), (-22, -114)])), "#F28A72", 2.2, seed, 1, 0.7))
    return "".join(out)


def winter_wonder():
    c = C("wwo")
    o = [paper(c.id("pp"), PAPER, FLECK, 21)]
    # icy painted wash behind the bird
    bd = blob(300, 352, 250, 210, 4, 0.1, 24)
    o.append(wash(bd, "#D6E4EA", 5, 3, 4, 0.4))
    o.append(clip_strokes(c, bd, (40, 130, 560, 580), ["#C2D6E0", "#E6EEF2", "#AFC8D6", "#FFFFFF"], 6, n=170, angle=-18,
                          length=(30, 90), width=(4, 11), op=(0.15, 0.4)))
    o.append(c.oglow(330, 380, 170, 140, "#FFFFFF", 0.55))
    # back bough (paler, upper right)
    back = [(610, 300), (520, 318), (450, 346), (404, 372)]
    o.append(ink(smooth_open(back), "#7A6A5A", 4, 4, 1, 0.6))
    o.append(needles(c, back, 8, length=(14, 26), greens=("#6E9480", "#7FA08C", "#8FB09A", "#A2BEAA", "#7A9C88"), density=0.7, w=2.2))
    o.append(snow_lump(c, drape((470, 336), (600, 296), 7, 3), 3, iw=0.9))
    # main bough
    br = [(-10, 488), (90, 470), (200, 452), (300, 438), (400, 432), (470, 420), (560, 398), (620, 384)]
    o.append(ink(smooth_open(br), BROWN_D, 9, 2, 1, 1))
    o.append(ink(smooth_open([(x, y - 2) for x, y in br]), BROWN_L, 3, 3, 1, 0.6))
    o.append(ink(smooth_open([(200, 452), (170, 418), (150, 400)]), BROWN_D, 5, 4, 1, 1))
    o.append(needles(c, br[:3], 11, density=1.6, length=(18, 36), w=3))
    o.append(needles(c, br[3:], 12, density=1.5, length=(18, 36), w=3))
    o.append(needles(c, [(200, 452), (170, 418), (148, 398)], 13, density=1.6, length=(16, 30), w=3))
    # pine cone hanging under the bough
    cone = [(372, 446), (390, 450), (394, 478), (384, 504), (374, 510), (362, 494), (360, 466)]
    o.append(shape(c, cone, "#8A5A32", ["#B07A48", "#5A3418", "#C9925A"], 14, angle=-90, n=30, iw=1.6))
    o.append('<g fill="none" stroke="#4A2A14" stroke-width="1.4" opacity="0.7">' + "".join(
        f'<path d="M {F(362 + k * 0.4)} {460 + k * 9} q 14 6 30 -2"/>' for k in range(5)) + "</g>")
    # snow on the bough
    for k, (a, b, t) in enumerate((((40, 470), (96, 462), 13), ((84, 464), (150, 454), 15), ((140, 456), (200, 446), 12),
                                   ((396, 426), (446, 420), 12), ((436, 422), (500, 410), 15), ((490, 412), (548, 396), 12))):
        o.append(snow_lump(c, drape(a, b, t, 40 + k, 2, up=t * 0.5), 40 + k))
    o.append(snow_lump(c, drape((140, 396), (192, 436), 9, 7, 2, up=4), 17, iw=0.9))
    # holly & berries tucked in at left
    o.append(holly(c, 132, 470, 1.0, 10, 18))
    # the bird, with its little feet gripping the bough
    o.append('<g fill="none" stroke="#5A3A24" stroke-width="3" stroke-linecap="round">'
             '<path d="M 306 426 l 0 10 q -2 6 -9 6 M 306 436 q 4 6 8 5"/><path d="M 334 424 l 0 10 q -2 6 -9 6 M 334 434 q 4 6 8 5"/></g>')
    o.append(cardinal(c, 318, 380, 1.06, 3))
    o.append(snow_lump(c, drape((248, 442), (296, 438), 8, 9, 1, up=4), 19, iw=0.9))
    # snowfall
    o.append(spatter(22, 70, (60, 130, 560, 560), ["#FFFFFF"], r=(1.2, 3.6), op=(0.7, 1), avoid=[(70, 70, 530, 240)]))
    for x, y, r, rt in ((96, 300, 12, 8), (512, 270, 14, 20), (470, 520, 10, 0), (86, 540, 9, 15)):
        o.append(flake(x, y, r, "#FFFFFF", 2.4, rt))
    # lettering
    o.append(L(c, 300, 132, "winter", SERIF_IT, 92, GREEN_D, [GREEN, "#0E2A1E", GREEN_L], max_w=380, shadow="#E4CFA8", seed=4, angle=-35))
    o.append(L(c, 300, 240, "WONDER", BEBAS, 132, CRAN, [RED, CRAN_D, "#C8404A", "#8A1A2E"], max_w=430, ls=10, shadow="#5A1020",
               seed=5, angle=-75))
    o.append(glint(118, 200, 10, GOLD) + glint(488, 112, 12, GOLD) + glint(470, 152, 6, GOLD))
    return finish(c, "".join(o))


# ================================================================ REPAINT: snow-much-fun (snowman)
def snowball(c, cx, cy, r, seed):
    pts = blob_pts(cx, cy, r, r * 0.95, seed, 0.035, 20)
    d = smooth_closed(pts)
    cl = c.id("ball")
    return (wash(d, SNOW, seed, 2, 0.8, 0.5)
            + f'<clipPath id="{cl}"><path d="{d}"/></clipPath><g clip-path="url(#{cl})">'
            + f'<path d="{blob(cx + r * 0.5, cy + r * 0.5, r * 0.9, r * 0.8, seed + 1, 0.08)}" fill="{SHADE}" opacity="0.32"/>'
            + f'<path d="{blob(cx + r * 0.62, cy + r * 0.7, r * 0.6, r * 0.5, seed + 2, 0.08)}" fill="{SHADE_D}" opacity="0.22"/>'
            + "</g>"
            + strokes(c.id("bs"), d, bbox(pts), ["#FFFFFF", SHADE_L, ICE_L, SHADE], seed + 3, n=int(r * 1.3), angle=-30,
                      length=(r * 0.2, r * 0.5), width=(2, 4.5), opacity=(0.2, 0.5), curve=0.35)
            + f'<path d="M {F(cx - r * 0.62)} {F(cy - r * 0.2)} Q {F(cx - r * 0.55)} {F(cy - r * 0.62)} {F(cx - r * 0.12)} {F(cy - r * 0.72)}" stroke="#FFFFFF" stroke-width="{F(r * 0.09)}" fill="none" stroke-linecap="round" opacity="0.9"/>'
            + ink(d, "#5A4A5A", 2.2, seed, 2, 0.6))


def snow_much_fun():
    c = C("smf")
    o = [wash_bg(c, "#C9DDE6", ["#B4CEDB", "#DCE9EE", "#A8C4D3", "#E9F1F3"], 3, angle=-14, n=300)]
    o.append(c.oglow(420, 120, 260, 160, "#FFFFFF", 0.5))
    # distant blue firs
    rnd = random.Random(4)
    for x in range(-20, 640, 34):
        h = rnd.uniform(44, 86)
        o.append(fir(c, x + rnd.uniform(-8, 8), 402 + rnd.uniform(-6, 4), h, h * 0.55, rnd.randint(0, 999),
                     cols=("#8FAEC0", "#7A9AB0", "#A6C2D0", "#86A6BA"), tiers=4, snow=False, inkc=None, trunk=None))
    o.append(snow_field(c, [(-20, 400), (120, 392), (260, 404), (420, 388), (620, 398)], 5, n=60))
    o.append(snow_field(c, [(-20, 470), (140, 452), (300, 462), (460, 448), (620, 458)], 6,
                        shade_box=(-20, 450, 620, 520), inkc="#8C8FC8"))
    # sled with footprints
    o.append(cast(170, 540, 90, 8, SHADE_D, 0.45, 3))
    o.append('<g transform="rotate(-5 170 520)">')
    seat = [(92, 510), (240, 506), (244, 520), (94, 524)]
    o.append(shape(c, seat, RED, ["#E2524A", CRAN, "#F07058"], 7, angle=-4, n=30, iw=1.8))
    o.append(ink("M 96 516 L 242 512", CRAN_D, 1.5, 2, 1, 0.6))
    o.append(ink("M 82 536 L 236 532 Q 262 532 262 512", INK, 3.8, 3, 2, 0.95))
    o.append(ink("M 110 524 L 108 534 M 220 520 L 222 532", INK, 3, 4, 1, 0.9))
    o.append(ink("M 244 510 Q 300 486 340 500", GOLD_D, 2.4, 5, 1, 0.9))
    o.append("</g>")
    for k in range(5):
        o.append(cast(270 + k * 16, 552 - k * 8, 5, 3, SHADE_D, 0.4, k))
    # snowman
    sx = 404
    o.append(cast(sx + 16, 524, 110, 13, SHADE_D, 0.45, 8))
    o.append(snowball(c, sx, 452, 84, 11))
    o.append(snowball(c, sx + 2, 340, 64, 12))
    o.append(snowball(c, sx - 2, 252, 50, 13))
    # stick arms
    o.append(ink(smooth_open([(sx - 58, 344), (sx - 88, 382), (sx - 104, 412)]), BROWN_D, 5, 4, 2, 1))
    o.append(ink("M 312 380 L 296 382", BROWN_D, 3.5, 5, 1, 1))
    o.append(ink(smooth_open([(sx + 58, 322), (sx + 92, 292), (sx + 110, 258)]), BROWN_D, 5, 6, 2, 1))
    o.append(ink(f"M {sx + 92} 292 L {sx + 116} 294", BROWN_D, 3.5, 7, 1, 1))
    # mitten on the waving arm
    mit = [(sx + 98, 270), (sx + 96, 240), (sx + 104, 222), (sx + 120, 220), (sx + 128, 236), (sx + 138, 230), (sx + 144, 240),
           (sx + 134, 262), (sx + 122, 276)]
    o.append(shape(c, mit, RED, ["#E2524A", CRAN, "#F07058"], 9, angle=-70, n=24, iw=2))
    o.append(f'<path d="{smooth_closed([(sx + 94, 266), (sx + 126, 276), (sx + 124, 290), (sx + 92, 282)])}" fill="{CREAM}"/>'
             + ink(smooth_closed([(sx + 94, 266), (sx + 126, 276), (sx + 124, 290), (sx + 92, 282)]), INK, 1.4, 3, 1, 0.6))
    for k in range(3):
        o.append(glint(sx + 108 + k * 8, 244 + (k % 2) * 8, 3.5, CREAM))
    # coal buttons
    for k, y in enumerate((318, 350, 384, 430, 470)):
        if y in (384,):
            continue
        o.append(f'<path d="{blob(sx + 2 + (y - 340) * 0.03, y, 6.5, 6, k + 30, 0.15, 8)}" fill="#2E2830"/><circle cx="{F(sx)}" cy="{y - 2}" r="1.8" fill="#8A8496"/>')
    # face
    o.append(f'<path d="{blob(sx - 16, 244, 5.5, 6.2, 41, 0.12, 8)}" fill="#1E1A20"/><path d="{blob(sx + 14, 244, 5.5, 6.2, 42, 0.12, 8)}" fill="#1E1A20"/>'
             f'<circle cx="{sx - 18}" cy="242" r="1.8" fill="#FFFFFF"/><circle cx="{sx + 12}" cy="242" r="1.8" fill="#FFFFFF"/>')
    o.append("".join(f'<circle cx="{F(sx + dx)}" cy="{F(268 + dy)}" r="3" fill="#2E2830"/>' for dx, dy in ((-20, -2), (-10, 3), (0, 5), (10, 3), (20, -2))))
    o.append(f'<circle cx="{sx - 30}" cy="262" r="8" fill="{PINK}" opacity="0.55"/><circle cx="{sx + 28}" cy="262" r="8" fill="{PINK}" opacity="0.55"/>')
    carrot = [(sx - 2, 250), (sx - 58, 266), (sx - 2, 264)]
    o.append(shape(c, carrot, "#EE8A3A", ["#F8B060", "#C8641E"], 43, angle=170, n=10, iw=1.6, d="M " + " L ".join(f"{x} {y}" for x, y in carrot) + " Z"))
    o.append(ink(f"M {sx - 22} 256 l 2 6 M {sx - 36} 260 l 2 5", "#A04A14", 1.4, 4, 1, 0.8))
    # knit hat with pom-pom
    hat = [(sx - 50, 226), (sx - 46, 192), (sx - 24, 168), (sx + 4, 162), (sx + 30, 170), (sx + 48, 194), (sx + 50, 226)]
    o.append(shape(c, hat, GREEN, [GREEN_L, GREEN_D, "#3E6E50"], 44, angle=-90, n=60, iw=2.2))
    cl = c.id("hk")
    o.append(f'<clipPath id="{cl}"><path d="{smooth_closed(hat)}"/></clipPath><g clip-path="url(#{cl})" fill="none" stroke="{CREAM}" stroke-width="3.2" stroke-linecap="round" opacity="0.9">'
             + "".join(f'<path d="M {x} 186 l 5 9 l 5 -9"/>' for x in range(sx - 46, sx + 48, 12)) + "</g>")
    cuff = [(sx - 56, 218), (sx + 56, 218), (sx + 58, 238), (sx - 58, 238)]
    o.append(shape(c, cuff, RED, ["#E2524A", CRAN, "#F07058"], 45, angle=-90, n=40, length=(6, 14), width=(1.5, 3), iw=2))
    o.append(f'<g stroke="{CRAN_D}" stroke-width="1.6" opacity="0.6">' + "".join(f'<path d="M {x} 222 l 1 13"/>' for x in range(sx - 50, sx + 54, 7)) + "</g>")
    pom = blob_pts(sx + 4, 156, 17, 16, 46, 0.18, 14)
    o.append(shape(c, pom, CREAM, ["#FFFFFF", SHADE_L, "#E8DCC8"], 46, angle=-60, n=24, length=(4, 9), width=(1.5, 3), iw=1.6))
    # striped scarf with a hanging tail
    sc = [(sx - 56, 290), (sx, 306), (sx + 58, 290), (sx + 60, 308), (sx, 326), (sx - 58, 308)]
    tail = [(sx + 18, 312), (sx + 46, 310), (sx + 54, 392), (sx + 26, 398)]
    for pts_, sd in ((tail, 47), (sc, 48)):
        cl = c.id("sc")
        d = smooth_closed(pts_)
        o.append(wash(d, RED, sd, 2, 0.8, 0.5))
        o.append(f'<clipPath id="{cl}"><path d="{d}"/></clipPath><g clip-path="url(#{cl})">'
                 + ("".join(f'<rect x="{x}" y="280" width="9" height="60" fill="{CREAM}"/>' for x in range(sx - 50, sx + 60, 24)) if pts_ is sc
                    else "".join(f'<rect x="{sx + 10}" y="{y}" width="60" height="9" fill="{CREAM}"/>' for y in range(326, 400, 22)))
                 + "</g>")
        o.append(strokes(c.id("ss"), d, bbox(pts_), ["#E2524A", CRAN, "#FFFFFF"], sd, n=40, angle=-80 if pts_ is tail else -10,
                         length=(8, 20), width=(1.5, 3), opacity=(0.2, 0.45)))
        o.append(ink(d, INK, 2, sd, 1, 0.7))
    o.append(f'<g stroke="{RED}" stroke-width="3.4" stroke-linecap="round">' + "".join(f'<path d="M {sx + 28 + k * 5} {397 - k * 0.6:.1f} l 1 12"/>' for k in range(5)) + "</g>")
    # falling snow
    o.append(spatter(51, 90, (0, 0, 600, 600), ["#FFFFFF"], r=(1.2, 3.8), op=(0.75, 1), avoid=[(50, 60, 310, 410)]))
    for x, y, r, rt in ((530, 120, 13, 10), (300, 90, 9, 0), (546, 360, 10, 20), (90, 470, 10, 5)):
        o.append(flake(x, y, r, "#FFFFFF", 2.4, rt))
    # lettering stacked at left
    o.append(L(c, 66, 150, "snow", SERIF_IT, 96, NAVY, [NAVY_D, "#34507A", "#1A2A4C"], max_w=250, anchor="start", shadow="#F6FAFB", seed=1, angle=-35))
    o.append(L(c, 70, 236, "much", SERIF_IT, 96, NAVY, [NAVY_D, "#34507A", "#1A2A4C"], max_w=250, anchor="start", shadow="#F6FAFB", seed=2, angle=-35))
    o.append(L(c, 64, 386, "FUN!", BEBAS, 176, RED, ["#E2524A", CRAN, CRAN_D, "#F07058"], max_w=236, anchor="start", ls=4,
               shadow=CRAN_D, seed=3, angle=-75))
    return finish(c, "".join(o))


# ================================================================ REPAINT: naughty-or-nice (Santa's list)
def naughty_or_nice():
    c = C("non")
    o = [wash_bg(c, "#24503E", ["#2E6450", "#1A3E30", "#33705A", "#173A2C"], 4, angle=-24, n=340)]
    o.append(c.oglow(300, 300, 320, 300, "#3E7A60", 0.5))
    rnd = random.Random(5)
    for _ in range(26):
        x, y = rnd.uniform(14, 586), rnd.uniform(14, 586)
        if 90 < x < 510 and 60 < y < 540:
            continue
        o.append(glint(x, y, rnd.uniform(4, 8), GOLD_L, rnd.uniform(0.5, 0.9)))
    o.append(spatter(6, 60, (0, 0, 600, 600), [GOLD_L, "#FFFFFF"], r=(0.8, 2.2), op=(0.25, 0.6), avoid=[(100, 70, 500, 530)]))
    # the list: a sheet of notepaper, slightly turned
    o.append('<g transform="rotate(-3 300 300)">')
    sheet = [(116, 92), (300, 86), (486, 94), (490, 300), (494, 492), (420, 500), (300, 506), (180, 498), (110, 504), (112, 300)]
    sheet = jitter(sheet, 3, 2)
    d = "M " + " L ".join(f"{F(x)} {F(y)}" for x, y in sheet) + " Z"
    o.append(f'<path d="{d}" fill="#0A1E16" opacity="0.35" transform="translate(9 11)"/>')
    o.append(shape(c, sheet, "#FBF2DF", ["#F2E2C2", "#FFF9EE", "#EAD6B2"], 6, angle=-12, n=140, length=(30, 80), width=(4, 10),
                   op=(0.15, 0.4), iw=2.2, d=d))
    o.append(c.oglow(300, 300, 200, 220, "#FFFFFF", 0.35))
    # ruled lines + red margin
    o.append('<g fill="none" stroke="#9DB6CC" stroke-width="1.6" opacity="0.55">' + "".join(
        f'<path d="M 120 {y} q 90 {rnd.uniform(-1.5, 1.5):.1f} 180 0 t 186 0"/>' for y in range(216, 492, 36)) + "</g>")
    o.append(ink("M 150 96 L 148 500", "#D86A6A", 2, 4, 1, 0.55))
    # edges aged
    o.append(strokes(c.id("ag"), d, (100, 80, 500, 120), ["#D9BE8E"], 7, n=30, angle=0, length=(30, 60), width=(3, 7), opacity=(0.2, 0.4)))
    o.append(strokes(c.id("ag"), d, (100, 470, 500, 510), ["#D9BE8E"], 8, n=30, angle=0, length=(30, 60), width=(3, 7), opacity=(0.2, 0.4)))
    # title
    o.append(L(c, 312, 168, "SANTA'S LIST", CINZEL, 44, CRAN, [RED, CRAN_D], max_w=310, ls=3, seed=7, angle=-20, density=0.8))
    o.append(ink("M 168 186 Q 310 178 456 186", CRAN, 3, 8, 2, 0.85))
    # hand-drawn check boxes
    def box(x, y, sd):
        bp = jitter([(x, y), (x + 54, y - 1), (x + 55, y + 54), (x - 1, y + 55)], sd, 1.6)
        bd_ = "M " + " L ".join(f"{F(px)} {F(py)}" for px, py in bp) + " Z"
        return f'<path d="{bd_}" fill="#FFFFFF" opacity="0.5"/>' + ink(bd_, INK, 4, sd, 2, 0.9)
    o.append(box(168, 226, 1))
    o.append(L(c, 254, 278, "NAUGHTY", BEBAS, 92, INK, ["#5A3A28", "#22140C", "#6E4A34"], max_w=224, anchor="start", ls=3, seed=9, angle=-80))
    o.append(box(168, 320, 2))
    o.append(L(c, 254, 372, "NICE", BEBAS, 92, RED, ["#E2524A", CRAN, "#F07058"], max_w=224, anchor="start", ls=3, seed=10, angle=-80))
    # a scribbled-out naughty (just a little) and the big painted check
    o.append(ink("M 300 248 q 18 -6 34 2 q 18 6 32 -2", INK, 2.2, 11, 1, 0.35))
    chk = "M 176 350 Q 188 358 198 380 Q 212 340 246 302"
    o.append(ink(chk, CRAN_D, 13, 12, 1, 0.35).replace('transform="', 'transform="translate(3 3) '))
    o.append(ink(chk, RED, 11, 13, 1, 1))
    o.append(ink("M 202 368 Q 216 336 242 308", "#F7A090", 2.4, 14, 1, 0.8))
    o.append(L(c, 312, 452, "(mostly)", SERIF_IT, 64, INK, ["#5A3A28", "#22140C"], max_w=260, seed=15, angle=-30))
    o.append("</g>")
    # holly pinned at the top-left corner, a candy-cane pencil lying across the bottom right
    o.append(holly(c, 124, 104, 1.25, 20, 21))
    o.append('<g transform="rotate(-36 470 470)">')
    pen = [(380, 462), (548, 462), (548, 482), (380, 482)]
    pd = "M 380 462 L 548 462 L 548 482 L 380 482 Z"
    o.append(f'<path d="{pd}" fill="#0A1E16" opacity="0.3" transform="translate(6 8)"/>')
    o.append(f'<path d="{pd}" fill="{CREAM}"/>')
    cl = c.id("pc")
    o.append(f'<clipPath id="{cl}"><path d="{pd}"/></clipPath><g clip-path="url(#{cl})">' + "".join(
        f'<path d="M {x} 490 L {x + 18} 454 L {x + 28} 454 L {x + 10} 490 Z" fill="{RED}"/>' for x in range(372, 556, 24)) + "</g>")
    o.append(strokes(c.id("ps"), pd, (380, 460, 548, 484), ["#FFFFFF", CRAN], 22, n=30, angle=0, length=(10, 30), width=(1, 2), opacity=(0.2, 0.4)))
    o.append(ink(pd, INK, 1.8, 3, 1, 0.8))
    o.append(shape(c, [(380, 462), (352, 472), (380, 482)], "#E9C99A", ["#D9B47A"], 23, n=6, iw=1.6, d="M 380 462 L 350 472 L 380 482 Z"))
    o.append(f'<path d="M 358 469 L 350 472 L 358 475 Z" fill="{INK}"/>')
    o.append(f'<path d="M 548 462 L 562 462 Q 568 472 562 482 L 548 482 Z" fill="{PINK}"/>' + ink("M 548 462 L 562 462 Q 568 472 562 482 L 548 482", INK, 1.6, 4, 1, 0.8))
    o.append("</g>")
    return finish(c, "".join(o))


def limb(path, w0, w1):
    """Closed outline around a polyline, tapering from width w0 to w1."""
    n = len(path)
    left, right = [], []
    for i, (x, y) in enumerate(path):
        a = path[max(i - 1, 0)]
        b = path[min(i + 1, n - 1)]
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        nx, ny = -math.sin(ang), math.cos(ang)
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left + right[::-1]


def fluff(c, pts, seed, base=SNOW, shade=SHADE, bumps=0.1, n=26, inkc="#7A7090", iw=1.5, curls=True):
    """Cloud-like white form (beard, fur trim, snow puff): scalloped edge, violet shading, curl strokes."""
    rnd = random.Random(seed)
    sm = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
        sm.append((x1, y1))
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        L_ = math.hypot(x2 - x1, y2 - y1)
        nx, ny = (y2 - y1) / (L_ or 1), -(x2 - x1) / (L_ or 1)
        cx_ = sum(p[0] for p in pts) / len(pts)
        cy_ = sum(p[1] for p in pts) / len(pts)
        if (mx - cx_) * nx + (my - cy_) * ny < 0:
            nx, ny = -nx, -ny
        k = L_ * bumps * rnd.uniform(0.7, 1.3)
        sm.append((mx + nx * k, my + ny * k))
    d = smooth_closed(sm)
    box = bbox(sm)
    cl = c.id("fl")
    out = [f'<path d="{d}" fill="{base}"/>',
           f'<clipPath id="{cl}"><path d="{d}"/></clipPath><g clip-path="url(#{cl})">'
           f'<path d="{blob((box[0] + box[2]) / 2 + (box[2] - box[0]) * 0.25, (box[1] + box[3]) / 2 + (box[3] - box[1]) * 0.3, (box[2] - box[0]) * 0.45, (box[3] - box[1]) * 0.4, seed, 0.1)}" fill="{shade}" opacity="0.22"/></g>']
    if curls:
        cs = []
        for _ in range(n):
            x, y = rnd.uniform(box[0] + 6, box[2] - 6), rnd.uniform(box[1] + 6, box[3] - 6)
            r = rnd.uniform(5, 10)
            a0 = rnd.uniform(0, 6.28)
            a1 = a0 + rnd.uniform(2.2, 3.6)
            cs.append(f'<path d="M {F(x + r * math.cos(a0))} {F(y + r * math.sin(a0))} A {F(r)} {F(r)} 0 0 1 {F(x + r * math.cos(a1))} {F(y + r * math.sin(a1))}" stroke-width="{rnd.uniform(1.4, 2.4):.1f}"/>')
        out.append(f'<g clip-path="url(#{cl})" fill="none" stroke="{shade}" stroke-linecap="round" opacity="0.5">{"".join(cs)}</g>')
    out.append(strokes(c.id("fs"), d, box, ["#FFFFFF", lt(shade, 0.5)], seed + 1, n=int((box[2] - box[0]) * 0.5), angle=-60,
                       length=(6, 16), width=(1.5, 3.5), opacity=(0.4, 0.8), curve=0.4))
    if inkc:
        out.append(ink(d, inkc, iw, seed, 1, 0.55))
    return "".join(out)


# ================================================================ REPAINT: ho-ho-ho (jolly Santa portrait)
def ho_ho_ho():
    c = C("hoh")
    o = [paper(c.id("pp"), PAPER, FLECK, 31)]
    bd = blob(300, 410, 236, 222, 7, 0.08, 24)
    o.append(wash(bd, "#2F6450", 8, 3, 3, 0.5))
    o.append(clip_strokes(c, bd, (40, 170, 560, 640), [GREEN_D, GREEN_L, "#3E7A60", "#24503E"], 9, n=220, angle=-24,
                          length=(30, 80), width=(5, 12), op=(0.15, 0.4)))
    o.append(spatter(10, 50, (70, 190, 530, 600), ["#FFFFFF"], r=(1.2, 3.4), op=(0.6, 0.95)))
    for x, y, r, rt in ((104, 300, 11, 5), (496, 400, 12, 20), (118, 470, 9, 12)):
        o.append(flake(x, y, r, "#FFFFFF", 2.2, rt))
    # coat shoulders with fur collar
    coat = [(70, 640), (96, 560), (150, 520), (300, 506), (450, 520), (504, 560), (530, 640)]
    o.append(shape(c, coat, RED, ["#E2524A", CRAN, CRAN_D], 11, angle=-80, n=120, iw=2.4))
    # hair at the sides
    for sx_ in (-1, 1):
        hp = [(300 + sx_ * 74, 330), (300 + sx_ * 104, 336), (300 + sx_ * 112, 380), (300 + sx_ * 100, 420), (300 + sx_ * 78, 400)]
        o.append(fluff(c, hp, 12 + sx_, n=6))
    # ears and face
    for sx_ in (-1, 1):
        o.append(shape(c, blob_pts(300 + sx_ * 84, 372, 14, 20, 14 + sx_, 0.08, 12), "#EBB08E", ["#D98E70", "#F6C8A8"], 15, n=10, iw=1.6))
    face = blob_pts(300, 368, 84, 74, 16, 0.04, 20)
    o.append(shape(c, face, "#F2C3A2", ["#F8D6BA", "#E6A888", "#EDB898"], 17, angle=-60, n=80, length=(8, 20), width=(2, 4), op=(0.2, 0.45), iw=2.2))
    o.append(f'<path d="{blob(252, 390, 22, 16, 18, 0.1)}" fill="#E8848A" opacity="0.5"/><path d="{blob(348, 390, 22, 16, 19, 0.1)}" fill="#E8848A" opacity="0.5"/>')
    # beard
    beard = [(214, 380), (230, 410), (262, 424), (300, 430), (338, 424), (370, 410), (386, 380), (398, 420), (394, 470), (374, 514),
             (342, 548), (300, 562), (258, 548), (226, 514), (206, 470), (202, 420)]
    o.append(fluff(c, beard, 20, n=40, bumps=0.16))
    # laughing mouth
    mouth = [(272, 432), (300, 428), (328, 432), (324, 452), (300, 466), (276, 452)]
    o.append(shape(c, mouth, "#7A1E26", ["#5A1018", "#9A2A30"], 21, n=10, iw=1.8))
    o.append(f'<path d="{blob(300, 456, 15, 7, 22, 0.1)}" fill="#E06A6E"/>')
    # mustache
    for sx_ in (-1, 1):
        m = [(300, 404), (300 + sx_ * 26, 396), (300 + sx_ * 60, 400), (300 + sx_ * 86, 418), (300 + sx_ * 96, 440), (300 + sx_ * 76, 432),
             (300 + sx_ * 50, 432), (300 + sx_ * 22, 426)]
        o.append(fluff(c, m, 23 + sx_, n=5, bumps=0.06))
    # nose
    o.append(shape(c, blob_pts(300, 392, 21, 18, 24, 0.05, 14), "#E88A76", ["#F6A890", "#C8645A"], 25, n=16, iw=1.8))
    o.append(f'<path d="{blob(293, 385, 6, 4, 26, 0.1)}" fill="#FFFFFF" opacity="0.7"/>')
    # happy closed eyes and fluffy brows
    for sx_ in (-1, 1):
        ex = 300 + sx_ * 34
        o.append(ink(f"M {ex - 13} 366 Q {ex} 350 {ex + 13} 366", "#2A1810", 4.2, 27 + sx_, 2, 0.95))
        o.append(ink(f"M {ex + sx_ * 15} 362 l {sx_ * 7} -3", "#2A1810", 2, 28, 1, 0.8))
        brow = [(ex - 22, 342), (ex - 6, 330), (ex + 16, 332), (ex + 24, 342), (ex + 4, 346)]
        o.append(fluff(c, brow, 29 + sx_, n=3, bumps=0.12, iw=1.2))
    # hat: red with a floppy tip, fur brim and pom-pom
    hat = [(194, 318), (204, 262), (246, 222), (306, 204), (368, 210), (422, 236), (460, 274), (482, 312), (466, 320),
           (440, 290), (410, 276), (408, 318)]
    o.append(shape(c, hat, RED, ["#E2524A", CRAN, "#F07058", CRAN_D], 30, angle=-60, n=170, length=(14, 34), width=(3, 7), iw=2.4))
    cl = c.id("hs")
    o.append(f'<clipPath id="{cl}"><path d="{smooth_closed(hat)}"/></clipPath><g clip-path="url(#{cl})">'
             f'<path d="{blob(410, 262, 60, 40, 31, 0.1)}" fill="{CRAN_D}" opacity="0.45"/><path d="{blob(260, 236, 50, 18, 32, 0.1, rot=-20)}" fill="#F7907A" opacity="0.4"/></g>')
    brim = [(178, 300), (240, 290), (300, 288), (360, 290), (422, 300), (426, 330), (360, 326), (300, 326), (240, 326), (176, 332)]
    o.append(fluff(c, brim, 33, n=14, bumps=0.14))
    o.append(fluff(c, blob_pts(486, 322, 24, 23, 34, 0.1, 10), 34, n=5, bumps=0.15))
    # collar fur
    collar = [(150, 526), (220, 512), (300, 520), (380, 512), (450, 526), (456, 556), (380, 548), (300, 560), (220, 548), (146, 558)]
    o.append(fluff(c, collar, 35, n=14, bumps=0.12))
    # lettering
    o.append(L(c, 300, 160, "HO HO HO!", BEBAS, 138, CRAN, [RED, CRAN_D, "#C8404A", "#8A1A2E"], max_w=470, ls=8, shadow="#E4C79A",
               sdx=0.035, sdy=0.05, seed=36, angle=-75))
    o.append(glint(86, 92, 9, GOLD) + glint(520, 196, 10, GOLD) + glint(540, 120, 6, GOLD))
    return finish(c, "".join(o))


# ================================================================ REPAINT: wrapped-with-love (painted gift stack)
def gift(c, x0, x1, top, bot, col, tints, rib, pattern, pcol, seed, lid=0.26, tilt=0):
    """Front-on gift box: lid + body as organic washes, painted pattern, ribbon band, pen line."""
    out = [f'<g transform="rotate({tilt} {(x0 + x1) / 2} {bot})">']
    h = bot - top
    ly = top + h * lid
    body = jitter([(x0 + 4, ly), (x1 - 4, ly), (x1 - 3, bot), (x0 + 3, bot)], seed, 1.2)
    lidp = jitter([(x0 - 6, top), (x1 + 6, top), (x1 + 7, ly + 2), (x0 - 7, ly + 2)], seed + 1, 1.2)
    out.append(f'<path d="M {x0 + 10} {bot - 2} L {x1 + 10} {bot - 2} L {x1 + 12} {bot + 8} L {x0 + 12} {bot + 8} Z" fill="{dk(col, 0.6)}" opacity="0.18"/>')
    for pts_, k in ((body, 0), (lidp, 1)):
        d = "M " + " L ".join(f"{F(px)} {F(py)}" for px, py in pts_) + " Z"
        out.append(wash(d, col if k == 0 else lt(col, 0.08), seed + k, 2, 0.8, 0.5))
        cl = c.id("gp")
        b = bbox(pts_, 0)
        pat = []
        rnd = random.Random(seed + k)
        if pattern == "dots":
            for yy in range(int(b[1]) + 10, int(b[3]), 22):
                for xx in range(int(b[0]) + (11 if (yy // 22) % 2 else 0), int(b[2]), 22):
                    pat.append(f'<path d="{blob(xx, yy, 4.2, 4, rnd.randint(0, 999), 0.12, 8)}" fill="{pcol}"/>')
        elif pattern == "stripes":
            for xx in range(int(b[0]) - 60, int(b[2]) + 20, 26):
                pat.append(f'<path d="M {xx} {b[3] + 4} L {xx + 50} {b[1] - 4} L {xx + 62} {b[1] - 4} L {xx + 12} {b[3] + 4} Z" fill="{pcol}" opacity="0.9"/>')
        elif pattern == "hearts":
            from common import heart
            for yy in range(int(b[1]) + 12, int(b[3]), 24):
                for xx in range(int(b[0]) + (12 if (yy // 24) % 2 else 0), int(b[2]), 24):
                    pat.append(heart(xx, yy, 5.5, pcol))
        out.append(f'<clipPath id="{cl}"><path d="{d}"/></clipPath><g clip-path="url(#{cl})">{"".join(pat)}'
                   f'<rect x="{b[0]}" y="{b[3] - (b[3] - b[1]) * 0.4:.1f}" width="{b[2] - b[0]}" height="{(b[3] - b[1]) * 0.4:.1f}" fill="{dk(col, 0.5)}" opacity="{0.12 if k == 0 else 0.2}"/></g>')
        out.append(strokes(c.id("gs"), d, b, tints, seed + 3 + k, n=int((b[2] - b[0]) * (b[3] - b[1]) / 140), angle=-80 if k == 0 else -8,
                           length=(10, 30), width=(2, 5), opacity=(0.15, 0.4)))
        out.append(ink(d, INK, 2.2, seed + k, 2, 0.8))
    # ribbon band
    cx = (x0 + x1) / 2
    rw = (x1 - x0) * 0.13
    rb = jitter([(cx - rw / 2, top), (cx + rw / 2, top), (cx + rw / 2, bot), (cx - rw / 2, bot)], seed + 5, 0.8)
    d = "M " + " L ".join(f"{F(px)} {F(py)}" for px, py in rb) + " Z"
    out.append(shape(c, rb, rib, [lt(rib, 0.3), dk(rib, 0.25)], seed + 6, angle=-90, n=16, iw=1.8, d=d))
    out.append(f'<path d="M {F(cx - rw / 2 + 3)} {top + 3} L {F(cx - rw / 2 + 3)} {bot - 3}" stroke="#FFFFFF" stroke-width="2" opacity="0.5"/>')
    out.append(ink(f"M {x0 - 6} {F(ly + 2)} L {x1 + 7} {F(ly + 2)}", INK, 2.4, seed + 7, 1, 0.85))
    out.append("</g>")
    return "".join(out)


def bow(c, x, y, s, rib, seed=1):
    out = []
    for sx_ in (-1, 1):
        tail = [(x, y + 4), (x + sx_ * 18 * s, y + 40 * s), (x + sx_ * 34 * s, y + 62 * s), (x + sx_ * 22 * s, y + 66 * s), (x + sx_ * 6 * s, y + 30 * s)]
        out.append(shape(c, tail, dk(rib, 0.08), [lt(rib, 0.3), dk(rib, 0.3)], seed + sx_, angle=70 if sx_ > 0 else 110, n=12, iw=1.8))
    for sx_ in (-1, 1):
        loop = [(x, y), (x + sx_ * 26 * s, y - 34 * s), (x + sx_ * 56 * s, y - 40 * s), (x + sx_ * 66 * s, y - 18 * s), (x + sx_ * 50 * s, y + 6 * s), (x + sx_ * 20 * s, y + 8 * s)]
        out.append(shape(c, loop, rib, [lt(rib, 0.35), dk(rib, 0.3), lt(rib, 0.15)], seed + 3 + sx_, angle=-20 if sx_ > 0 else -160, n=30, iw=2.2))
        inner = [(x + sx_ * 12 * s, y - 4 * s), (x + sx_ * 34 * s, y - 24 * s), (x + sx_ * 50 * s, y - 22 * s), (x + sx_ * 40 * s, y - 6 * s)]
        out.append(f'<path d="{smooth_closed(inner)}" fill="{dk(rib, 0.35)}" opacity="0.5"/>')
        out.append(ink(smooth_open([(x + sx_ * 18 * s, y - 20 * s), (x + sx_ * 40 * s, y - 32 * s), (x + sx_ * 54 * s, y - 32 * s)]), lt(rib, 0.55), 2, seed, 1, 0.7))
    out.append(shape(c, blob_pts(x, y - 2 * s, 13 * s, 12 * s, seed + 9, 0.08, 10), dk(rib, 0.05), [lt(rib, 0.3), dk(rib, 0.3)], seed + 9, n=8, iw=2))
    return "".join(out)


def wrapped_with_love():
    c = C("wwl")
    o = [wash_bg(c, "#F6D6D2", ["#F2C4C0", "#FBE6E2", "#EDB4B2", "#FFF0EC"], 3, angle=-20, n=300)]
    from common import heart
    rnd = random.Random(4)
    for _ in range(40):
        x, y = rnd.uniform(10, 590), rnd.uniform(10, 590)
        if 130 < x < 470 and 70 < y < 560:
            continue
        o.append(f'<g transform="rotate({rnd.uniform(-25, 25):.0f} {x:.0f} {y:.0f})" opacity="{rnd.uniform(0.45, 0.85):.2f}">{heart(x, y, rnd.uniform(5, 9), rnd.choice(["#FFFFFF", "#E88A96", "#FBEFEA"]))}</g>')
    o.append(c.oglow(300, 420, 230, 170, "#FFF6F2", 0.6))
    o.append(cast(300, 538, 196, 14, "#B8606C", 0.3, 5))
    o.append(gift(c, 140, 460, 420, 536, CRAN, ["#C23A4A", CRAN_D, "#B8304A"], PINK_L, "dots", "#FBE6E2", 11, lid=0.24))
    o.append(gift(c, 186, 414, 336, 422, PINK, ["#F2B8C0", "#D98A96", "#F8CCD2"], CRAN, "stripes", "#FBEFEA", 12, lid=0.28, tilt=-2))
    o.append(gift(c, 228, 366, 270, 338, "#FBF2E8", ["#FFFFFF", "#EADCCB"], RED, "hearts", "#E26A78", 13, lid=0.3, tilt=3))
    # a sprig of pine and berries tucked under the bow
    o.append(needles(c, [(316, 268), (356, 252), (384, 240)], 14, length=(12, 22), density=1.4, w=2.6))
    o.append(berry(c, 352, 258, 6, RED, 1) + berry(c, 362, 264, 6, RED, 2) + berry(c, 360, 251, 5.5, RED, 3))
    o.append(bow(c, 300, 262, 1.0, RED, 15))
    # gift tag on a string
    o.append(ink("M 448 446 Q 480 470 488 494", INK, 1.6, 16, 1, 0.8))
    o.append('<g transform="rotate(-16 500 512)">')
    tag = [(472, 498), (484, 486), (538, 486), (538, 532), (484, 532), (472, 520)]
    td = "M " + " L ".join(f"{px} {py}" for px, py in tag) + " Z"
    o.append(f'<path d="{td}" fill="#7A3040" opacity="0.2" transform="translate(4 5)"/>')
    o.append(shape(c, tag, "#EFD9B8", ["#E2C49A", "#F8E8CC"], 17, angle=-10, n=20, iw=1.8, d=td))
    o.append(f'<circle cx="485" cy="509" r="3.6" fill="#B8956A"/>{heart(512, 510, 11, RED)}</g>')
    for x, y, r, col in ((112, 330, 10, GOLD), (494, 320, 12, GOLD), (96, 470, 7, RED), (520, 410, 7, GOLD)):
        o.append(glint(x, y, r, col))
    # lettering
    o.append(L(c, 300, 124, "wrapped with", SERIF_IT, 76, CRAN, [RED, CRAN_D, "#C8404A"], max_w=440, shadow="#FFF4EE", seed=18, angle=-35))
    o.append(L(c, 300, 222, "LOVE", BEBAS, 104, RED, ["#E2524A", CRAN, "#F07058", CRAN_D], max_w=200, ls=14, shadow=CRAN_D, seed=19, angle=-75))
    for sx_ in (-1, 1):
        o.append(ink(f"M {300 + sx_ * 128} 186 Q {300 + sx_ * 160} 182 {300 + sx_ * 196} 188", CRAN, 3, 20 + sx_, 2, 0.85))
        o.append(f'<g transform="rotate({sx_ * 12} {300 + sx_ * 212} 188)">{heart(300 + sx_ * 212, 188, 9, RED)}</g>')
    return finish(c, "".join(o))


# ================================================================ REPAINT: oh-deer (storybook deer in a birch wood)
def birch(c, x, top, bot, w, seed, lean=0):
    rnd = random.Random(seed)
    pts = [(x - w / 2, bot), (x - w / 2 + lean * 0.5, (top + bot) / 2), (x - w * 0.45 + lean, top), (x + w * 0.45 + lean, top),
           (x + w / 2 + lean * 0.5, (top + bot) / 2), (x + w / 2, bot)]
    d = "M " + " L ".join(f"{F(px)} {F(py)}" for px, py in pts) + " Z"
    out = [f'<path d="{d}" fill="#F7F3EA"/>',
           strokes(c.id("bk"), d, bbox(pts), ["#D8D6DE", "#C6C8DA", "#FFFFFF"], seed, n=int((bot - top) / 5), angle=-90,
                   length=(14, 40), width=(1, 3), opacity=(0.3, 0.6))]
    cl = c.id("bc")
    marks = []
    for _ in range(int((bot - top) / 18)):
        yy = rnd.uniform(top, bot - 6)
        side = rnd.choice((-1, 1))
        L_ = w * rnd.uniform(0.3, 0.7)
        x0 = x + lean * (1 - (yy - top) / (bot - top)) + side * w / 2
        marks.append(f'<path d="M {F(x0)} {F(yy)} q {F(-side * L_ * 0.5)} {F(-1.5)} {F(-side * L_)} {F(0.5)} l 0 {rnd.uniform(1.8, 3.6):.1f} q {F(side * L_ * 0.5)} 1.5 {F(side * L_)} 0 Z" fill="#3A3438" opacity="0.85"/>')
    out.append(f'<clipPath id="{cl}"><path d="{d}"/></clipPath><g clip-path="url(#{cl})">{"".join(marks)}'
               f'<rect x="{x}" y="{top}" width="{w}" height="{bot - top}" fill="{SHADE}" opacity="0.35"/></g>')
    out.append(ink(d, "#6A6070", 1.4, seed, 1, 0.55))
    return "".join(out)


def deer(c, seed=5):
    """Storybook deer facing left, antlers strung with little lights, red scarf. Drawn in a 600 box."""
    o = []
    hide, hide_l, hide_d = "#A86E3C", "#C98E58", "#7A4A24"
    # far legs (darker)
    for path in ([(296, 398), (298, 450), (294, 506)], [(394, 400), (402, 452), (390, 506)]):
        lp = limb(path, 18, 9)
        o.append(shape(c, lp, dk(hide, 0.22), [dk(hide, 0.35), hide_d], seed, angle=-90, n=12, iw=1.6))
        hx, hy = path[-1]
        o.append(f'<path d="{blob(hx, hy + 2, 7, 5, seed, 0.1, 8)}" fill="#3A2418"/>')
    # far ear + far antler
    ear2 = [(222, 232), (238, 208), (256, 196), (252, 214), (236, 236)]
    o.append(shape(c, ear2, dk(hide, 0.15), [hide_d], seed + 1, n=6, iw=1.6))
    body = [(168, 268), (172, 256), (194, 240), (212, 230), (232, 234), (246, 254), (256, 290), (284, 320), (330, 322), (380, 320),
            (414, 328), (434, 352), (434, 386), (420, 410), (396, 420), (330, 418), (284, 414), (260, 398), (248, 368), (240, 330),
            (226, 296), (206, 282), (184, 280), (170, 276)]
    # near legs
    near = []
    for path in ([(272, 396), (268, 452), (264, 508)], [(414, 398), (424, 452), (414, 508)]):
        lp = limb(path, 22, 10)
        near.append(shape(c, lp, hide, [hide_l, hide_d], seed + 2, angle=-90, n=16, iw=1.8))
        hx, hy = path[-1]
        near.append(f'<path d="{blob(hx, hy + 2, 8, 5.5, seed + 3, 0.1, 8)}" fill="#3A2418"/>')
    o.append("".join(near))
    o.append(shape(c, body, hide, [hide_l, hide_d, "#B87A44", "#94602F"], seed + 4, angle=-12, n=170, length=(12, 30), width=(2, 5),
                   op=(0.2, 0.5), iw=2.4))
    cl = c.id("dc")
    o.append(f'<clipPath id="{cl}"><path d="{smooth_closed(body)}"/></clipPath><g clip-path="url(#{cl})">'
             f'<path d="{blob(340, 424, 90, 22, seed, 0.1)}" fill="#F1DDBE"/>'                       # pale belly
             f'<path d="{blob(244, 360, 18, 46, seed + 1, 0.1, rot=-20)}" fill="#F1DDBE"/>'           # throat / chest
             f'<path d="{blob(180, 274, 22, 12, seed + 2, 0.1)}" fill="#E9CDA6"/>'                    # muzzle
             f'<path d="{blob(340, 324, 110, 14, seed + 3, 0.1)}" fill="{hide_d}" opacity="0.45"/>'   # dark back
             f'<path d="{blob(410, 380, 34, 40, seed + 4, 0.1)}" fill="{hide_d}" opacity="0.25"/></g>')
    # spots on the back (storybook)
    rnd = random.Random(seed)
    for _ in range(9):
        o.append(f'<path d="{blob(rnd.uniform(300, 410), rnd.uniform(336, 366), rnd.uniform(3.5, 5.5), rnd.uniform(2.6, 4), rnd.randint(0, 99), 0.15, 8)}" fill="#F7E8CE" opacity="0.85"/>')
    # tail
    o.append(shape(c, [(432, 340), (446, 326), (452, 334), (440, 352)], "#F7EEDD", [hide_l], seed + 5, n=6, iw=1.6))
    # near ear
    ear = [(234, 240), (258, 222), (282, 216), (272, 234), (246, 246)]
    o.append(shape(c, ear, hide, [hide_l, hide_d], seed + 6, n=8, iw=1.8))
    o.append(f'<path d="{smooth_closed([(244, 238), (262, 226), (274, 224), (264, 234), (248, 242)])}" fill="#E8A8A0" opacity="0.8"/>')
    # antlers
    ant = [
        [(214, 232), (206, 206), (208, 178), (220, 152), (236, 134)],
        [(208, 196), (190, 184), (178, 166)],
        [(210, 172), (196, 150), (194, 132)],
        [(222, 150), (238, 150), (250, 140)],
        [(226, 232), (240, 206), (262, 184), (280, 160), (292, 140)],
        [(250, 196), (274, 196), (290, 186)],
        [(268, 176), (264, 152), (270, 134)],
    ]
    for a in ant:
        o.append(ink(smooth_open(a), INK, 10, seed, 1, 0.9))
    for a in ant:
        o.append(ink(smooth_open(a), "#EAD6B2", 6.4, seed + 1, 1, 1))
        o.append(ink(smooth_open([(x - 1.2, y - 1) for x, y in a]), "#FFF4DE", 2, seed + 2, 1, 0.7))
    # string of lights wound on the antlers
    wire = [(204, 214), (216, 196), (222, 176), (210, 160), (222, 146), (240, 160), (256, 190), (272, 176), (282, 156)]
    o.append(ink(smooth_open(wire), "#2E4A36", 1.6, seed, 1, 0.9))
    cols = [GOLD, RED, "#4E9A6A", GOLD, "#6AA8D0", RED, GOLD, "#4E9A6A", RED]
    for (x, y), col in zip(wire[::1], cols):
        o.append(c.glow(x, y + 3, 11, lt(col, 0.4), 0.55))
        o.append(f'<path d="{blob(x, y + 4, 3.6, 5, seed + int(x), 0.1, 8)}" fill="{col}"/><circle cx="{F(x - 1)}" cy="{F(y + 2.5)}" r="1.3" fill="#FFFFFF" opacity="0.9"/>')
    # face
    o.append(f'<path d="{blob(171, 266, 8, 6.5, seed, 0.1, 10)}" fill="#2A1810"/><circle cx="168" cy="263.5" r="1.8" fill="#FFFFFF" opacity="0.7"/>')
    o.append(f'<path d="{blob(206, 252, 6.5, 7, seed + 1, 0.08, 10)}" fill="#1E120C"/><circle cx="204" cy="249.5" r="2.2" fill="#FFFFFF"/>')
    o.append(ink("M 198 246 q 6 -6 14 -3", "#1E120C", 1.8, seed, 1, 0.9) + ink("M 176 276 q 6 4 12 1", "#5A3020", 1.4, seed, 1, 0.8))
    o.append(f'<path d="{blob(216, 268, 9, 6, seed + 2, 0.1)}" fill="{PINK}" opacity="0.55"/>')
    # red scarf around the neck, tail fluttering back
    tail = [(250, 304), (276, 314), (300, 330), (318, 352), (300, 352), (282, 338), (256, 326)]
    o.append(shape(c, tail, CRAN, [RED, CRAN_D], seed + 7, angle=30, n=16, iw=1.8))
    sc = [(226, 290), (254, 282), (266, 300), (262, 322), (236, 330), (232, 312)]
    sc = [(222, 292), (246, 280), (262, 292), (266, 312), (244, 326), (230, 316)]
    o.append(shape(c, sc, RED, ["#E2524A", CRAN], seed + 8, angle=-70, n=18, iw=2))
    o.append(f'<g stroke="{CREAM}" stroke-width="3" opacity="0.85">' + "".join(f'<path d="M {x} {y} l 8 12"/>' for x, y in ((236, 290), (248, 286), (282, 322), (296, 334))) + "</g>")
    return "".join(o)


def oh_deer():
    c = C("ohd")
    o = [wash_bg(c, "#DCE8EC", ["#CADDE4", "#EEF4F5", "#BFD3DD", "#F6F8F6"], 3, angle=-12, n=280)]
    o.append(c.oglow(160, 250, 260, 200, "#FFF8EC", 0.6))
    # far misty forest
    rnd = random.Random(6)
    for x in range(-20, 640, 26):
        h = rnd.uniform(50, 100)
        o.append(fir(c, x + rnd.uniform(-8, 8), 346 + rnd.uniform(-6, 4), h, h * 0.5, rnd.randint(0, 999),
                     cols=("#A9C2CE", "#98B4C2", "#BCD0D8", "#A2BCC8"), tiers=4, snow=False, inkc=None, trunk=None))
    o.append(snow_field(c, [(-20, 346), (160, 336), (320, 348), (480, 334), (620, 342)], 7, n=50))
    # birches
    for x, w, top, sd, ln in ((70, 22, -20, 1, 0), (112, 13, 40, 2, 3), (522, 20, -20, 3, -2), (556, 12, 30, 4, 2)):
        o.append(birch(c, x, top, 420, w, sd, ln))
    o.append(ink("M 70 160 q 24 -18 44 -20 M 522 200 q -26 -16 -46 -16", "#5A5060", 2.6, 5, 1, 0.8))
    o.append(snow_field(c, [(-20, 412), (150, 400), (320, 410), (470, 398), (620, 408)], 8, shade_box=(-20, 420, 620, 470), inkc=SHADE_D))
    o.append(cast(320, 446, 140, 12, SHADE_D, 0.45, 9))
    o.append(f'<g transform="translate(-6 -70)">{deer(c)}</g>')
    o.append(spatter(10, 110, (0, 0, 600, 600), ["#FFFFFF"], r=(1.2, 3.6), op=(0.75, 1), avoid=[(60, 450, 540, 545)]))
    for x, y, r, rt in ((92, 250, 11, 5), (476, 120, 12, 20), (440, 230, 9, 12), (150, 100, 9, 0)):
        o.append(flake(x, y, r, "#FFFFFF", 2.4, rt))
    # lettering on the snow, one line
    w1 = measure("oh", SERIF_IT, 104)
    w2 = measure("DEER", BEBAS, 140, 10)
    x0 = 300 - (w1 + 22 + w2) / 2
    o.append(L(c, x0, 530, "oh", SERIF_IT, 104, CRAN, [RED, CRAN_D, "#C8404A"], anchor="start", max_w=200, shadow=SHADE_L, seed=11, angle=-35))
    o.append(L(c, x0 + w1 + 22, 530, "DEER", BEBAS, 140, NAVY, [NAVY_D, "#34507A", "#2A3E68"], anchor="start", max_w=300, ls=10,
               shadow=SHADE, seed=12, angle=-75))
    return finish(c, "".join(o))


# ================================================================ REPAINT: joy-to-the-world (the O is a little painted globe)
def globe(c, cx, cy, r, seed=3):
    o = []
    d = blob(cx, cy, r, r, seed, 0.015, 24)
    o.append(f'<path d="{blob(cx + 8, cy + r + 6, r * 0.8, 9, seed, 0.1)}" fill="{INK}" opacity="0.12"/>')
    o.append(wash(d, "#4F8AAE", seed, 2, 0.8, 0.5))
    o.append(strokes(c.id("oc"), d, (cx - r, cy - r, cx + r, cy + r), ["#6EA6C6", "#3A6E92", "#8CBCD6", "#2E5E80"], seed, n=int(r * 2.4),
                     angle=-20, length=(r * 0.15, r * 0.4), width=(2, 5), opacity=(0.25, 0.55), curve=0.4))
    cl = c.id("gl")
    land = []
    # stylised Americas + a sliver of Europe / Africa on the right
    na = [(-0.62, -0.52), (-0.3, -0.72), (0.0, -0.66), (0.08, -0.46), (-0.08, -0.3), (-0.2, -0.12), (-0.34, -0.1), (-0.5, -0.24)]
    sa = [(-0.16, 0.0), (0.06, 0.04), (0.2, 0.2), (0.12, 0.44), (-0.02, 0.72), (-0.1, 0.6), (-0.16, 0.3), (-0.24, 0.12)]
    gr = [(0.12, -0.84), (0.3, -0.86), (0.32, -0.72), (0.18, -0.7)]
    af = [(0.62, -0.3), (0.86, -0.28), (0.98, 0.0), (0.9, 0.36), (0.72, 0.5), (0.62, 0.2), (0.56, -0.08)]
    for k, poly in enumerate((na, sa, gr, af)):
        pts = [(cx + x * r, cy + y * r) for x, y in poly]
        pd = smooth_closed(jitter(pts, seed + k, r * 0.02))
        land.append(f'<path d="{pd}" fill="#6E9E58"/>')
        land.append(strokes(c.id("ld"), pd, bbox(pts), ["#8EBA6A", "#4E7E40", "#A8C878", "#D9C27A"], seed + k, n=int(r * 0.5),
                            angle=-60, length=(r * 0.06, r * 0.16), width=(1.5, 3), opacity=(0.4, 0.75)))
        land.append(ink(pd, "#3E5A30", 1.2, seed + k, 1, 0.55))
    o.append(f'<clipPath id="{cl}"><path d="{d}"/></clipPath><g clip-path="url(#{cl})">{"".join(land)}'
             f'<path d="{blob(cx + r * 0.42, cy + r * 0.45, r * 0.95, r * 0.9, seed, 0.06)}" fill="{NAVY}" opacity="0.28"/>'
             f'<g fill="none" stroke="#FFFFFF" stroke-width="1.4" opacity="0.28">'
             f'<ellipse cx="{cx}" cy="{cy}" rx="{r * 0.45:.1f}" ry="{r}"/><path d="M {cx - r} {cy} L {cx + r} {cy}"/>'
             f'<path d="M {cx - r} {cy - r * 0.45:.1f} Q {cx} {cy - r * 0.38:.1f} {cx + r} {cy - r * 0.45:.1f}"/>'
             f'<path d="M {cx - r} {cy + r * 0.45:.1f} Q {cx} {cy + r * 0.52:.1f} {cx + r} {cy + r * 0.45:.1f}"/></g></g>')
    o.append(f'<path d="M {F(cx - r * 0.66)} {F(cy - r * 0.2)} Q {F(cx - r * 0.6)} {F(cy - r * 0.62)} {F(cx - r * 0.18)} {F(cy - r * 0.74)}" stroke="#FFFFFF" stroke-width="{F(r * 0.08)}" fill="none" stroke-linecap="round" opacity="0.75"/>')
    o.append(ink(d, INK, 3, seed, 2, 0.85))
    return "".join(o)


def joy_to_the_world():
    c = C("joy")
    o = [paper(c.id("pp"), PAPER, FLECK, 41)]
    bd = blob(300, 330, 262, 200, 9, 0.1, 26)
    o.append(wash(bd, "#F1D9A8", 10, 3, 4, 0.4))
    o.append(clip_strokes(c, bd, (30, 110, 570, 520), ["#EBCB8C", "#F8E6C0", "#E2B870", "#FFF2D6"], 11, n=200, angle=-20,
                          length=(30, 90), width=(5, 12), op=(0.15, 0.4)))
    o.append(c.oglow(300, 300, 240, 170, "#FFF6E0", 0.6))
    # hanging garland of little stars across the top
    o.append(ink("M 40 70 Q 300 150 560 70", "#8A6A4A", 1.6, 12, 1, 0.7))
    for k in range(7):
        t = (k + 0.5) / 7
        x = 40 + 520 * t
        y = (1 - t) ** 2 * 70 + 2 * (1 - t) * t * 150 + t * t * 70
        o.append(ink(f"M {F(x)} {F(y)} l 0 {14 + (k % 2) * 10}", "#8A6A4A", 1.2, k, 1, 0.7))
        o.append(pstar(c, x, y + 26 + (k % 2) * 10, 11, [GOLD, RED, GOLD, GREEN_L][k % 4], k, iw=1.2))
    # J  [globe]  Y
    size = 236
    wj = measure("J", DMS, size)
    wy = measure("Y", DMS, size)
    R = 84
    gap = 14
    tot = wj + gap + 2 * R + gap + wy
    x0 = 300 - tot / 2
    base_y = 394
    o.append(L(c, x0, base_y, "J", DMS, size, CRAN, [RED, CRAN_D, "#C8404A", "#8A1A2E"], anchor="start", max_w=200, shadow="#C9984E",
               seed=13, angle=-75, sdx=0.02, sdy=0.025))
    o.append(L(c, x0 + wj + gap + 2 * R + gap, base_y, "Y", DMS, size, CRAN, [RED, CRAN_D, "#C8404A", "#8A1A2E"], anchor="start", max_w=200,
               shadow="#C9984E", seed=14, angle=-75, sdx=0.02, sdy=0.025))
    gx, gy = x0 + wj + gap + R, base_y - size * 0.35
    o.append(globe(c, gx, gy, R, 15))
    # a sprig of holly on top of the world and a little star above
    o.append(holly(c, gx + 30, gy - R + 10, 0.9, -30, 16))
    o.append(c.glow(gx - 20, gy - R - 36, 40, GOLD_L, 0.7) + pstar(c, gx - 20, gy - R - 36, 18, GOLD, 17))
    o.append(L(c, 300, 490, "to the world", SERIF_IT, 76, GREEN_D, [GREEN, "#0E2A1E", GREEN_L], max_w=420, shadow="#F6E6C2", seed=18, angle=-35))
    o.append(ink("M 196 516 Q 300 532 404 516", GOLD_D, 2.6, 19, 2, 0.8))
    for x, y, r in ((86, 250, 10), (520, 260, 12), (110, 420, 7), (500, 430, 8), (300, 548, 7)):
        o.append(glint(x, y, r, GOLD))
    o.append(spatter(20, 50, (40, 180, 560, 560), [GOLD, GOLD_L], r=(0.8, 2.2), op=(0.3, 0.7), avoid=[(150, 160, 450, 520)]))
    return finish(c, "".join(o))


# ================================================================ REPAINT: fresh-cut-trees (painted farm sign in the snow)
def plank(c, x0, x1, y0, y1, seed, col="#A8723E"):
    pts = jitter([(x0, y0), ((x0 + x1) / 2, y0 - 1), (x1, y0 + 1), (x1 + 2, y1), ((x0 + x1) / 2, y1 + 1), (x0 - 1, y1)], seed, 1.2)
    d = "M " + " L ".join(f"{F(px)} {F(py)}" for px, py in pts) + " Z"
    o = [wash(d, col, seed, 2, 0.8, 0.5),
         strokes(c.id("wd"), d, bbox(pts), ["#C88E52", "#7A4A24", "#B67C44", "#E0A868", "#6A3E1E"], seed, n=int((x1 - x0) * (y1 - y0) / 70),
                 angle=-1, length=(30, 90), width=(1, 3), opacity=(0.3, 0.65), curve=0.05)]
    rnd = random.Random(seed)
    kx = rnd.uniform(x0 + 40, x1 - 40)
    o.append(f'<path d="{blob(kx, (y0 + y1) / 2 + rnd.uniform(-6, 6), 9, 4.5, seed, 0.1)}" fill="none" stroke="#5A3418" stroke-width="1.6" opacity="0.6"/>')
    o.append(f'<path d="M {x0 + 2} {y0 + 2} L {x1 - 2} {y0 + 2}" stroke="#E8B47A" stroke-width="2.4" opacity="0.6"/>')
    o.append(ink(d, INK, 2, seed, 2, 0.85))
    for nx in (x0 + 16, x1 - 16):
        o.append(f'<circle cx="{nx}" cy="{(y0 + y1) / 2:.1f}" r="3.2" fill="#3A2A20"/><circle cx="{nx - 1}" cy="{(y0 + y1) / 2 - 1:.1f}" r="1.2" fill="#C8B8A0"/>')
    return "".join(o)


def fresh_cut_trees():
    c = C("fct")
    sky = c.lg([(0, "#9CB8CE"), (0.5, "#E6D2C4"), (1, "#F6DCC0")])
    o = [f'<rect width="600" height="600" fill="url(#{sky})"/>',
         strokes(c.id("sk"), "M -20 -20 L 620 -20 L 620 360 L -20 360 Z", (-40, -40, 640, 360), ["#B4CADA", "#F2DCCC", "#FFFFFF", "#D8C6C8"], 3,
                 n=200, angle=-8, length=(50, 130), width=(5, 12), opacity=(0.1, 0.3), curve=0.1)]
    o.append(c.glow(460, 250, 220, "#FFE6C0", 0.7))
    # distant pale hills with tiny firs
    hill = [(-20, 300), (120, 276), (260, 292), (420, 270), (620, 290)]
    rnd = random.Random(4)
    for x in range(-10, 620, 16):
        h = rnd.uniform(18, 34)
        o.append(fir(c, x + rnd.uniform(-5, 5), 290 - 10 * math.sin(x / 120) + rnd.uniform(-2, 2), h, h * 0.55, rnd.randint(0, 999),
                     cols=("#9AAFC0", "#8AA0B4", "#AFC2CE", "#94AABC"), tiers=3, snow=False, inkc=None, trunk=None))
    o.append(snow_field(c, hill, 5, n=40))
    # a little red barn far off
    o.append('<g transform="translate(118 280)">' + shape(c, [(0, 0), (0, -20), (18, -34), (36, -20), (36, 0)], "#B0383A", ["#C84A48", "#8A2A2C"], 6, n=10, iw=1.2,
                                                            d="M 0 0 L 0 -20 L 18 -34 L 36 -20 L 36 0 Z")
             + f'<path d="M -4 -18 L 18 -36 L 40 -18" stroke="{SNOW}" stroke-width="4" fill="none" stroke-linecap="round"/><rect x="13" y="-12" width="10" height="12" fill="#5A1E16"/></g>')
    # rows of young trees
    for row, (yb, h0, step, cols) in enumerate(((346, 46, 46, ("#5E8A70", "#476E5A", "#7AA48A", "#557E66")),
                                                (402, 66, 64, ("#3F7058", GREEN_D, "#5E9070", "#355E4A")))):
        o.append(snow_field(c, [(-20, yb - 16), (200, yb - 24), (420, yb - 14), (620, yb - 22)], 7 + row, n=60))
        for i, x in enumerate(range(-6 + row * 22, 640, step)):
            h = h0 * rnd.uniform(0.85, 1.12)
            o.append(cast(x + 10, yb + 2, h * 0.32, 4, SHADE_D, 0.35, i))
            o.append(fir(c, x + rnd.uniform(-5, 5), yb, h, h * 0.62, rnd.randint(0, 999), cols=cols, tiers=4, iw=1.2, inkc=INK if row else None))
    o.append(snow_field(c, [(-20, 446), (160, 436), (340, 448), (480, 438), (620, 446)], 9, shade_box=(-20, 450, 620, 520), inkc=SHADE_D))
    # big fir at left behind the sign
    o.append(fir(c, 88, 470, 250, 150, 21, tiers=6))
    # posts and sign
    o.append(cast(300, 474, 200, 10, SHADE_D, 0.4, 10))
    for px in (162, 438):
        pp = jitter([(px - 10, 228), (px + 10, 228), (px + 11, 474), (px - 11, 474)], px, 1)
        o.append(shape(c, pp, "#6E4628", ["#8A5A36", "#4A2A16"], px, angle=-90, n=20, iw=1.8, d="M " + " L ".join(f"{F(a)} {F(b)}" for a, b in pp) + " Z"))
    o.append('<g transform="rotate(-2 300 300)">')
    o.append(f'<path d="M 114 188 L 494 188 L 494 410 L 114 410 Z" fill="{INK}" opacity="0.22" transform="translate(7 9)"/>')
    o.append(plank(c, 112, 488, 186, 246, 31, "#AE7840"))
    o.append(plank(c, 108, 492, 246, 350, 32, "#A06A36"))
    o.append(plank(c, 114, 486, 350, 404, 33, "#AA7440"))
    o.append(L(c, 300, 234, "FRESH CUT", BEBAS, 54, CREAM, ["#FFFFFF", "#E8D8BE", "#D8C4A4"], max_w=300, ls=8, seed=34, angle=-80,
               shadow="#5A3418", sdx=0.02, sdy=0.04))
    for sx_ in (-1, 1):
        o.append(pstar(c, 300 + sx_ * 170, 216, 11, CREAM, 35 + sx_, tints=["#FFFFFF", "#E8D8BE"], iw=1.0))
    o.append(L(c, 300, 336, "TREES", BEBAS, 118, RED, ["#E2524A", CRAN, "#F07058", CRAN_D], max_w=340, ls=10, seed=36, angle=-80,
               shadow=CREAM, sdx=0.025, sdy=0.03))
    o.append(L(c, 300, 386, "U-CUT · FAMILY FARM", JOS, 24, CREAM, ["#FFFFFF", "#E8D8BE"], max_w=320, ls=4, seed=37, angle=-80, density=0.6))
    # snow on top of the sign
    o.append(snow_lump(c, [(104, 190), (150, 168), (220, 176), (300, 166), (380, 174), (450, 164), (500, 186), (480, 198), (420, 194),
                           (360, 198), (300, 194), (240, 200), (180, 196), (122, 202)], 38))
    o.append("</g>")
    # a cut tree leaning on the right post, tied with twine, with a SOLD tag
    o.append(f'<g transform="translate(484 482) rotate(14)">{fir(c, 0, 0, 190, 96, 41, tiers=6, trunk=BROWN_D)}</g>')
    for k, (ax, ay) in enumerate(((452, 380), (466, 340))):
        o.append(ink(f"M {ax} {ay} q 26 6 50 14", "#C9A87A", 2.6, k, 1, 0.95))
    o.append(ink("M 470 352 L 478 382", RED, 1.6, 3, 1, 0.9))
    o.append('<g transform="rotate(16 488 402)">'
             + shape(c, [(468, 384), (508, 384), (508, 420), (468, 420)], CREAM, ["#E8D8BE"], 42, n=8, iw=1.6, d="M 468 384 L 508 384 L 508 420 L 468 420 Z")
             + f'<circle cx="488" cy="391" r="2.6" fill="#B8A890"/><text x="488" y="414" text-anchor="middle" {BEBAS} font-size="19" fill="{RED}">SOLD</text></g>')
    # lantern glowing on the left post
    o.append(c.glow(150, 440, 46, "#FFD98E", 0.6))
    o.append(ink("M 150 408 L 150 418", INK, 2, 1, 1, 1) + f'<path d="M 140 422 L 150 414 L 160 422 Z" fill="{INK}"/>'
             + f'<rect x="141" y="422" width="18" height="26" rx="2" fill="#FFE6A8"/>' + ink("M 141 422 L 159 422 L 159 448 L 141 448 Z", INK, 2.4, 2, 1, 0.9)
             + '<path d="M 147 442 q 3 -8 3 -12 q 0 4 3 12 Z" fill="#F8A83A"/>')
    o.append(spatter(43, 120, (0, 0, 600, 600), ["#FFFFFF"], r=(1.2, 3.4), op=(0.7, 1), avoid=[(110, 160, 495, 410)]))
    return finish(c, "".join(o))


DESIGNS = {
    "winter-wonder": winter_wonder,
    "snow-much-fun": snow_much_fun,
    "naughty-or-nice": naughty_or_nice,
    "ho-ho-ho": ho_ho_ho,
    "wrapped-with-love": wrapped_with_love,
    "oh-deer": oh_deer,
    "joy-to-the-world": joy_to_the_world,
    "fresh-cut-trees": fresh_cut_trees,
}


def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())
        print("saved", slug)


if __name__ == "__main__":
    build(sys.argv[1:] or None)
