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


# ================================================================ NEW: winter-wonder (vintage ice skates hung by their laces)
def skate(c, ox, oy, s=1.0, seed=3, flip=False, rot=0, pom=RED):
    """Vintage white figure skate, side view, toe to the left (flip mirrors it). (ox, oy) = top of the cuff, centre."""
    T = lambda pts: tx(pts, 0, 0, 1, flip)
    sg = -1 if flip else 1
    o = [f'<g transform="translate({F(ox)} {F(oy)}) rotate({rot}) scale({s})">']
    # wall shadow of the whole skate (it hangs against the paper)
    sil = T([(-30, 0), (40, -6), (46, 60), (50, 170), (70, 232), (-100, 230), (-86, 160), (-28, 100)])
    o.append(f'<path d="{smooth_closed(sil)}" fill="{SHADE_D}" opacity="0.16" transform="translate({14 * sg} 12)"/>')
    # blade: stanchions + runner with a curled toe and toe-pick teeth
    for st in ([(-64, 192), (-46, 192), (-50, 222), (-66, 222)], [(18, 196), (38, 196), (40, 222), (20, 222)]):
        p_ = T(st)
        o.append(shape(c, p_, "#9AA8B8", ["#C6D2DE", "#6E7E92"], seed, angle=-90, n=6, iw=1.4, inkc="#3A4250",
                       d="M " + " L ".join(f"{F(x)} {F(y)}" for x, y in p_) + " Z"))
    blade = T([(-90, 208), (-102, 214), (-100, 226), (-86, 233), (40, 234), (68, 232), (78, 226), (70, 220), (-70, 220), (-84, 214)])
    g = c.lg([(0, "#F4F8FB"), (0.45, "#B8C6D4"), (1, "#6E8096")])
    o.append(f'<path d="{smooth_closed(blade)}" fill="url(#{g})"/>' + ink(smooth_closed(blade), "#2E3644", 1.8, seed, 2, 0.85))
    o.append(ink(smooth_open(T([(-80, 224), (0, 226), (66, 225)])), "#FFFFFF", 1.6, seed + 1, 1, 0.9))
    teeth = T([(-100, 222), (-106, 226), (-100, 228), (-104, 232), (-96, 232)])
    o.append(ink("M " + " L ".join(f"{F(x)} {F(y)}" for x, y in teeth), "#2E3644", 1.6, seed, 1, 0.9))
    # sole and heel block
    sole = T([(-82, 182), (44, 184), (46, 194), (-78, 194), (-86, 188)])
    o.append(shape(c, sole, "#6A4028", ["#8A5A36", "#4A2A16"], seed + 2, angle=0, n=10, iw=1.6))
    heel = T([(16, 192), (46, 192), (46, 204), (18, 204)])
    o.append(shape(c, heel, "#5A3620", ["#7A4A2A"], seed + 3, n=4, iw=1.4, d="M " + " L ".join(f"{F(x)} {F(y)}" for x, y in heel) + " Z"))
    # the boot
    boot = T([(-30, 2), (6, -4), (40, -4), (44, 40), (40, 92), (48, 132), (50, 168), (42, 184), (-60, 184), (-84, 178), (-88, 162),
              (-74, 146), (-44, 134), (-28, 102), (-30, 46)])
    o.append(shape(c, boot, "#F7F2EA", ["#FFFFFF", SHADE_L, "#EDE4D6", SHADE], seed + 4, angle=-90, n=110, length=(10, 30),
                   width=(2, 5), op=(0.2, 0.5), iw=2.4))
    cl = c.id("sk")
    o.append(f'<clipPath id="{cl}"><path d="{smooth_closed(boot)}"/></clipPath><g clip-path="url(#{cl})">'
             f'<path d="{blob(*T([(30, 100)])[0], 26, 110, seed, 0.08)}" fill="{SHADE}" opacity="0.3"/>'
             f'<path d="{blob(*T([(-40, 176)])[0], 60, 14, seed + 1, 0.08)}" fill="{SHADE_D}" opacity="0.3"/>'
             f'<path d="{blob(*T([(-4, 40)])[0], 10, 60, seed + 2, 0.1)}" fill="#FFFFFF" opacity="0.7"/></g>')
    # heel counter and vamp seams with stitching
    for seam in ([(40, 96), (14, 120), (10, 160), (16, 184)], [(-30, 104), (-6, 128), (-20, 160), (-58, 168), (-84, 170)]):
        o.append(ink(smooth_open(T(seam)), "#A89AA6", 1.8, seed, 1, 0.8))
        o.append(f'<path d="{smooth_open(T([(x + 4, y) for x, y in seam]))}" fill="none" stroke="#B9AEB8" stroke-width="1.3" stroke-dasharray="3 4" opacity="0.9"/>')
    # tongue peeking at the cuff + rolled collar
    tongue = T([(-34, 6), (-28, -14), (-6, -16), (-2, 6)])
    o.append(shape(c, tongue, "#EFE6D8", [SHADE_L, "#FFFFFF"], seed + 5, n=8, iw=1.6))
    o.append(ink(smooth_open(T([(-30, 2), (6, -4), (40, -4)])), "#8C8FC8", 3, seed, 1, 0.6))
    # eyelets + criss-cross red laces
    holes = [T([(-30 + k * 1.2, 14 + k * 20)])[0] for k in range(6)]
    holes2 = [T([(-12 + k * 0.6, 12 + k * 20)])[0] for k in range(6)]
    lace = []
    for k in range(5):
        lace.append(f"M {F(holes[k][0])} {F(holes[k][1])} L {F(holes2[k + 1][0])} {F(holes2[k + 1][1])}")
        lace.append(f"M {F(holes2[k][0])} {F(holes2[k][1])} L {F(holes[k + 1][0])} {F(holes[k + 1][1])}")
    o.append(f'<path d="{" ".join(lace)}" stroke="{CRAN_D}" stroke-width="4.4" stroke-linecap="round" fill="none"/>'
             f'<path d="{" ".join(lace)}" stroke="{RED}" stroke-width="2.8" stroke-linecap="round" fill="none"/>')
    for hx, hy in holes + holes2:
        o.append(f'<circle cx="{F(hx)}" cy="{F(hy)}" r="2.6" fill="#C9A24E" stroke="{INK}" stroke-width="0.9"/>')
    # pom-pom tied at the top of the laces
    pp = T([(-20, -8)])[0]
    o.append(shape(c, blob_pts(pp[0] - 14 * sg, pp[1] + 8, 15, 14, seed + 6, 0.2, 14), pom, [lt(pom, 0.3), dk(pom, 0.3), "#FFFFFF"],
                   seed + 6, angle=-60, n=30, length=(3, 8), width=(1.2, 2.4), op=(0.3, 0.7), iw=1.4))
    o.append("</g>")
    return "".join(o)


def winter_wonder():
    c = C("wwo")
    o = [paper(c.id("pp"), PAPER, FLECK, 21)]
    # icy painted wash behind the skates
    bd = blob(300, 400, 236, 186, 4, 0.1, 24)
    o.append(wash(bd, "#D6E4EA", 5, 3, 4, 0.4))
    o.append(clip_strokes(c, bd, (40, 200, 560, 600), ["#C2D6E0", "#E6EEF2", "#AFC8D6", "#FFFFFF"], 6, n=170, angle=-18,
                          length=(30, 90), width=(4, 11), op=(0.15, 0.4)))
    o.append(c.oglow(300, 400, 170, 140, "#FFFFFF", 0.5))
    # the peg: a little pine bough nailed up, laces looped over it
    kx, ky = 300, 282
    o.append(ink(smooth_open([(204, 276), (250, 284), (300, 282), (350, 276), (398, 284)]), BROWN_D, 5, 2, 1, 1))
    o.append(needles(c, [(196, 276), (250, 284), (300, 282)], 11, density=1.1, length=(14, 26), w=2.6))
    o.append(needles(c, [(300, 282), (350, 276), (404, 284)], 12, density=1.1, length=(14, 26), w=2.6))
    for k, (a, b, t) in enumerate((((214, 276), (262, 280), 8), ((334, 276), (390, 280), 8))):
        o.append(snow_lump(c, drape(a, b, t, 40 + k, 2, up=3), 40 + k, iw=0.9))
    # laces from the peg down to each skate
    la, lb = (216, 326), (388, 322)
    for (ex, ey), sd in ((la, 1), (lb, 2)):
        d = f"M {kx} {ky + 4} Q {F((kx + ex) / 2)} {F(ky + 6)} {F(ex)} {F(ey)}"
        o.append(ink(d, CRAN_D, 4.6, sd, 1, 1) + ink(d, RED, 2.8, sd + 1, 1, 1))
    # skates: left one hangs toe-left, right one toe-right, a little crossed
    o.append(skate(c, 240, 326, 0.88, 5, False, rot=8, pom=RED))
    o.append(skate(c, 362, 322, 0.88, 7, True, rot=-6, pom=GREEN))
    # bow where the laces meet + holly
    o.append(holly(c, kx, ky + 2, 0.95, 0, 18))
    for sx_ in (-1, 1):
        lp = [(kx, ky + 2), (kx + sx_ * 16, ky - 14), (kx + sx_ * 30, ky - 12), (kx + sx_ * 26, ky + 2), (kx + sx_ * 8, ky + 6)]
        o.append(shape(c, lp, RED, ["#E2524A", CRAN_D], 30 + sx_, n=10, iw=1.6))
    # snowfall + flakes
    o.append(spatter(22, 60, (60, 230, 560, 570), ["#FFFFFF"], r=(1.2, 3.4), op=(0.7, 1), avoid=[(120, 290, 480, 560)]))
    for x, y, r, rt in ((92, 330, 12, 8), (512, 300, 13, 20), (500, 520, 10, 0), (100, 520, 9, 15)):
        o.append(flake(x, y, r, "#FFFFFF", 2.4, rt))
    # lettering
    o.append(L(c, 300, 128, "winter", SERIF_IT, 96, GREEN_D, [GREEN, "#0E2A1E", GREEN_L], max_w=380, shadow="#E4CFA8", seed=4, angle=-35))
    o.append(L(c, 300, 238, "WONDER", BEBAS, 128, CRAN, [RED, CRAN_D, "#C8404A", "#8A1A2E"], max_w=430, ls=10, shadow="#5A1020",
               seed=5, angle=-75))
    o.append(glint(108, 196, 10, GOLD) + glint(494, 110, 12, GOLD) + glint(474, 150, 6, GOLD))
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
    o.append(ink(smooth_open([(sx - 58, 350), (sx - 76, 384), (sx - 84, 414)]), BROWN_D, 5, 4, 2, 1))
    o.append(ink(f"M {sx - 76} 386 L {sx - 92} 392", BROWN_D, 3.5, 5, 1, 1))
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
    # Santa framed in a round night-sky medallion: navy wash, stars, snowfall, a gold ink ring strung with little lights
    wx, wy, wr = 300, 378, 198
    bd = blob(wx, wy, wr, wr, 7, 0.025, 30)
    o.append(f'<path d="{blob(wx + 8, wy + 10, wr, wr, 7, 0.025, 30)}" fill="{INK}" opacity="0.15"/>')
    o.append(wash(bd, NAVY, 8, 3, 2, 0.5))
    o.append(clip_strokes(c, bd, (100, 190, 500, 580), ["#2E4470", NAVY_D, "#34507A", "#3E5A8A"], 9, n=180, angle=-24,
                          length=(30, 80), width=(5, 12), op=(0.2, 0.45)))
    o.append(c.glow(wx, wy - 20, 170, "#4E6AA0", 0.5))
    rs = random.Random(12)
    for _ in range(26):
        a_, rr = rs.uniform(0, 6.28), rs.uniform(30, wr - 16)
        x, y = wx + rr * math.cos(a_), wy + rr * math.sin(a_)
        o.append(glint(x, y, rs.uniform(2.5, 5), "#FFF6D8", rs.uniform(0.6, 1)) if rs.random() < 0.3 else
                 f'<circle cx="{F(x)}" cy="{F(y)}" r="{rs.uniform(1.2, 2.8):.1f}" fill="#FFFFFF" opacity="{rs.uniform(0.6, 1):.2f}"/>')
    o.append(f'<path d="{blob(wx, wy, wr, wr, 7, 0.025, 30)}" fill="none" stroke="{GOLD}" stroke-width="7"/>' + ink(bd, GOLD_D, 2, 10, 1, 0.8)
             + ink(blob(wx, wy, wr - 10, wr - 10, 11, 0.025, 30), GOLD_L, 1.6, 11, 1, 0.6))
    for k in range(16):
        a_ = math.radians(-90 + k * 360 / 16)
        x, y = wx + (wr + 1) * math.cos(a_), wy + (wr + 1) * math.sin(a_)
        col = [RED, GOLD_L, GREEN_L, "#6AA8D0"][k % 4]
        o.append(c.glow(x, y, 14, lt(col, 0.3), 0.55) + f'<path d="{blob(x, y, 5, 5, k, 0.08, 8)}" fill="{col}" stroke="{INK}" stroke-width="1"/>'
                 f'<circle cx="{F(x - 1.5)}" cy="{F(y - 1.5)}" r="1.5" fill="#FFFFFF" opacity="0.8"/>')
    for x, y, r, rt in ((90, 300, 11, 5), (510, 470, 12, 20), (92, 470, 9, 12)):
        o.append(flake(x, y, r, ICE_D, 2.2, rt, 0.8))
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
    o.append(L(c, 300, 118, "wrapped with", SERIF_IT, 76, CRAN, [RED, CRAN_D, "#C8404A"], max_w=440, shadow="#FFF4EE", seed=18, angle=-35))
    o.append(L(c, 300, 208, "LOVE", BEBAS, 100, RED, ["#E2524A", CRAN, "#F07058", CRAN_D], max_w=200, ls=14, shadow=CRAN_D, seed=19, angle=-75))
    for sx_ in (-1, 1):
        o.append(ink(f"M {300 + sx_ * 128} 174 Q {300 + sx_ * 160} 170 {300 + sx_ * 196} 176", CRAN, 3, 20 + sx_, 2, 0.85))
        o.append(f'<g transform="rotate({sx_ * 12} {300 + sx_ * 212} 176)">{heart(300 + sx_ * 212, 176, 9, RED)}</g>')
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
    o.append(cast(320, 436, 140, 12, SHADE_D, 0.45, 9))
    o.append(f'<g transform="translate(-6 -80)">{deer(c)}</g>')
    o.append(spatter(10, 110, (0, 0, 600, 600), ["#FFFFFF"], r=(1.2, 3.6), op=(0.75, 1), avoid=[(60, 450, 540, 545)]))
    for x, y, r, rt in ((92, 250, 11, 5), (476, 120, 12, 20), (440, 230, 9, 12), (150, 100, 9, 0)):
        o.append(flake(x, y, r, "#FFFFFF", 2.4, rt))
    # lettering on the snow, one line
    w1 = measure("oh", SERIF_IT, 104)
    w2 = measure("DEER", BEBAS, 140, 10)
    x0 = 300 - (w1 + 22 + w2) / 2
    o.append(L(c, x0, 534, "oh", SERIF_IT, 104, CRAN, [RED, CRAN_D, "#C8404A"], anchor="start", max_w=200, shadow=SHADE_L, seed=11, angle=-35))
    o.append(L(c, x0 + w1 + 22, 534, "DEER", BEBAS, 140, NAVY, [NAVY_D, "#34507A", "#2A3E68"], anchor="start", max_w=300, ls=10,
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
                     cols=("#9AAFC0", "#8AA0B4", "#AFC2CE", "#94AABC"), tiers=2, snow=False, inkc=None, trunk=None))
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
            o.append(fir(c, x + rnd.uniform(-5, 5), yb, h, h * 0.62, rnd.randint(0, 999), cols=cols, tiers=3, iw=1.2, inkc=INK if row else None, snow=bool(row)))
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


# ================================================================ shared new pieces: wreath, poinsettia, pine cone, lantern
def ring_pts(cx, cy, r, a0=0, a1=360, n=40, wob=0.0, seed=1):
    rnd = random.Random(seed)
    return [(cx + r * (1 + rnd.uniform(-wob, wob)) * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * (1 + rnd.uniform(-wob, wob)) * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def wreath(c, cx, cy, r, seed, needle=(10, 20), berries=True, snow=False, cones=True):
    """Small painted fir wreath: a dark ring wash, needles brushed along three concentric rings, berries, cones."""
    o = []
    rnd = random.Random(seed)
    th = r * 0.36
    d = (blob(cx, cy, r + th * 0.5, r + th * 0.5, seed, 0.03, 26) + " " + blob(cx, cy, r - th * 0.5, r - th * 0.5, seed + 1, 0.03, 22))
    o.append(f'<path d="{d}" fill="{GREEN_D}" fill-rule="evenodd"/>')
    for k, rr in enumerate((r - th * 0.3, r + th * 0.3, r)):
        o.append(needles(c, ring_pts(cx, cy, rr, rnd.uniform(0, 30), 390, 36, 0.02, seed + k), seed + 10 + k, length=needle,
                         density=0.55, w=2.2))
    if snow:
        for a in (-150, -110, -70, -30):
            p1 = (cx + r * 1.05 * math.cos(math.radians(a - 18)), cy + r * 1.05 * math.sin(math.radians(a - 18)))
            p2 = (cx + r * 1.05 * math.cos(math.radians(a + 18)), cy + r * 1.05 * math.sin(math.radians(a + 18)))
            o.append(snow_lump(c, drape(p1, p2, r * 0.07, seed + a, 2, up=2), seed + a, iw=0.8))
    if cones:
        for a in (200, 340):
            px, py = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
            o.append(pinecone(c, px, py, r * 0.006 + 0.1, a + 90, seed + a))
    if berries:
        for a in (130, 160, 20, 50, 250, 290):
            px, py = cx + r * 1.02 * math.cos(math.radians(a)), cy + r * 1.02 * math.sin(math.radians(a))
            for j in range(3):
                o.append(berry(c, px + rnd.uniform(-6, 6), py + rnd.uniform(-6, 6), r * 0.075 + 1.5, RED, seed + a + j))
    return "".join(o)


def pinecone(c, x, y, s, rot, seed):
    """Little painted pine cone, length ~ 70 * s, pointing along rot (deg, 90 = down)."""
    o = [f'<g transform="translate({F(x)} {F(y)}) rotate({F(rot - 90)}) scale({s:.3f})">']
    pts = [(0, -6), (14, 2), (19, 22), (16, 44), (8, 62), (0, 68), (-8, 62), (-16, 44), (-19, 22), (-14, 2)]
    o.append(shape(c, pts, "#8A5A32", ["#B07A48", "#5A3418", "#C9925A"], seed, angle=-90, n=24, iw=1.8))
    sc = []
    for row in range(6):
        yy = 6 + row * 10
        wv = 17 - abs(row - 2) * 2.4
        for k in range(-1, 2):
            xx = k * wv * 0.62
            sc.append(f"M {F(xx - 6)} {F(yy)} Q {F(xx)} {F(yy + 8)} {F(xx + 6)} {F(yy)}")
    o.append(f'<path d="{" ".join(sc)}" stroke="#4A2A14" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.75"/>')
    o.append(f'<path d="{" ".join(sc)}" stroke="#D9A46A" stroke-width="1.1" fill="none" stroke-linecap="round" opacity="0.6" transform="translate(0 -2)"/>')
    o.append("</g>")
    return "".join(o)


def leaf_pts(L, wfrac=0.34, tipk=1.0):
    W = L * wfrac
    return [(0, 0), (0.18 * L, 0.42 * W), (0.5 * L, 0.52 * W), (0.82 * L, 0.3 * W), (tipk * L, 0), (0.82 * L, -0.3 * W),
            (0.5 * L, -0.52 * W), (0.18 * L, -0.42 * W)]


def rot_pts(pts, x, y, a):
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
    return [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]


def painted_leaf(c, x, y, L, a, col, tints, seed, wfrac=0.34, vein=None, iw=1.6, veins=True):
    pts = rot_pts(jitter(leaf_pts(L, wfrac), seed, L * 0.015), x, y, a)
    o = [shape(c, pts, col, tints, seed, angle=a + 30, n=max(10, int(L * 0.7)), length=(L * 0.12, L * 0.3), width=(1.2, 2.8),
               op=(0.25, 0.55), iw=iw)]
    if veins:
        tip = rot_pts([(L * 0.92, 0)], x, y, a)[0]
        vc = vein or lt(col, 0.4)
        o.append(ink(f"M {F(x)} {F(y)} L {F(tip[0])} {F(tip[1])}", vc, 1.6, seed, 1, 0.75))
        side = []
        for t in (0.3, 0.5, 0.7):
            for sg in (-1, 1):
                p0 = rot_pts([(L * t, 0)], x, y, a)[0]
                p1 = rot_pts([(L * (t + 0.14), sg * L * wfrac * 0.36)], x, y, a)[0]
                side.append(f"M {F(p0[0])} {F(p0[1])} L {F(p1[0])} {F(p1[1])}")
        o.append(f'<path d="{" ".join(side)}" stroke="{vc}" stroke-width="1.1" opacity="0.6" fill="none" stroke-linecap="round"/>')
    return "".join(o)


def poinsettia(c, x, y, r, rot, seed):
    """Gouache poinsettia: green leaves underneath, two rings of veined red bracts, a gold-green centre."""
    rnd = random.Random(seed)
    o = []
    for k in range(3):
        a = rot + 30 + k * 120 + rnd.uniform(-10, 10)
        o.append(painted_leaf(c, x, y, r * 1.12, a, GREEN, [GREEN_L, GREEN_D, "#3E6E50"], seed + k, 0.4))
    for k in range(6):
        a = rot + k * 60 + rnd.uniform(-8, 8)
        o.append(painted_leaf(c, x, y, r * rnd.uniform(0.92, 1.02), a, "#B8232E", ["#D83A3A", "#8E1622", "#E2524A", CRAN_D], seed + 10 + k,
                              0.4, vein="#E66A5E"))
    for k in range(5):
        a = rot + 30 + k * 72 + rnd.uniform(-8, 8)
        o.append(painted_leaf(c, x, y, r * rnd.uniform(0.56, 0.66), a, "#D2343A", ["#E8564A", "#A81E2C", "#F07058"], seed + 20 + k,
                              0.42, vein="#F28A78", iw=1.3))
    for k in range(7):
        a = k * 51 + rnd.uniform(-10, 10)
        rr = 0 if k == 0 else r * 0.1
        px, py = x + rr * math.cos(math.radians(a)), y + rr * math.sin(math.radians(a))
        o.append(f'<path d="{blob(px, py, r * 0.055 + 1, r * 0.055 + 1, seed + k, 0.1, 8)}" fill="#7A9A3A" stroke="#3E4A18" stroke-width="1"/>'
                 f'<circle cx="{F(px - 1)}" cy="{F(py - 1)}" r="{F(r * 0.025 + 0.6)}" fill="{GOLD_L}"/>')
    o.append(f'<circle cx="{F(x + r * 0.06)}" cy="{F(y - r * 0.08)}" r="{F(r * 0.03 + 0.8)}" fill="{RED}"/>')
    return "".join(o)


def lantern(c, x, base, s, seed, glow=True):
    """Black tin lantern with a lit candle, standing at (x, base)."""
    o = []
    if glow:
        o.append(c.glow(x, base - 40 * s, 110 * s, "#FFC86A", 0.55))
    o.append(cast(x + 10 * s, base, 34 * s, 6 * s, "#2A1010", 0.35, seed))
    body = [(x - 22 * s, base - 8 * s), (x - 20 * s, base - 64 * s), (x + 20 * s, base - 64 * s), (x + 22 * s, base - 8 * s)]
    g = c.lg([(0, "#FFF2C4"), (0.5, "#FFD27A"), (1, "#F2A33A")])
    o.append(f'<path d="{smooth_closed(jitter(body, seed, 0.6))}" fill="url(#{g})"/>')
    o.append(c.glow(x, base - 30 * s, 16 * s, "#FFFFFF", 0.8))
    o.append(f'<path d="M {F(x - 6 * s)} {F(base - 10 * s)} L {F(x - 6 * s)} {F(base - 26 * s)} L {F(x + 6 * s)} {F(base - 26 * s)} L {F(x + 6 * s)} {F(base - 10 * s)} Z" fill="{CREAM}"/>'
             f'<path d="M {F(x)} {F(base - 44 * s)} Q {F(x + 6 * s)} {F(base - 32 * s)} {F(x)} {F(base - 27 * s)} Q {F(x - 6 * s)} {F(base - 32 * s)} {F(x)} {F(base - 44 * s)} Z" fill="#F8A83A"/>'
             f'<path d="M {F(x)} {F(base - 38 * s)} Q {F(x + 2.5 * s)} {F(base - 32 * s)} {F(x)} {F(base - 29 * s)} Q {F(x - 2.5 * s)} {F(base - 32 * s)} {F(x)} {F(base - 38 * s)} Z" fill="#FFF6D8"/>')
    frame = (f"M {F(x - 22 * s)} {F(base - 8 * s)} L {F(x - 20 * s)} {F(base - 64 * s)} L {F(x + 20 * s)} {F(base - 64 * s)} L {F(x + 22 * s)} {F(base - 8 * s)} Z "
             f"M {F(x)} {F(base - 64 * s)} L {F(x)} {F(base - 8 * s)}")
    o.append(ink(frame, "#1E1A1C", 3.4 * s, seed, 1, 1))
    o.append(shape(c, [(x - 28 * s, base - 8 * s), (x + 28 * s, base - 8 * s), (x + 26 * s, base), (x - 26 * s, base)], "#2A2628", ["#4A4448"], seed + 1, n=6,
                   iw=1.4, inkc="#121012", d=f"M {F(x - 28 * s)} {F(base - 8 * s)} L {F(x + 28 * s)} {F(base - 8 * s)} L {F(x + 26 * s)} {F(base)} L {F(x - 26 * s)} {F(base)} Z"))
    roof = [(x - 28 * s, base - 62 * s), (x, base - 84 * s), (x + 28 * s, base - 62 * s)]
    o.append(shape(c, roof, "#2A2628", ["#4A4448", "#5A5458"], seed + 2, n=8, iw=1.6, inkc="#121012",
                   d="M " + " L ".join(f"{F(a)} {F(b)}" for a, b in roof) + " Z"))
    o.append(ink(f"M {F(x - 10 * s)} {F(base - 84 * s)} Q {F(x)} {F(base - 104 * s)} {F(x + 10 * s)} {F(base - 84 * s)}", "#1E1A1C", 2.6 * s, seed, 1, 1))
    o.append(ink(f"M {F(x - 14 * s)} {F(base - 58 * s)} L {F(x - 14 * s)} {F(base - 14 * s)}", "#FFFFFF", 1.6 * s, seed, 1, 0.5))
    return "".join(o)


# ================================================================ NEW: sleigh-all-day (vintage sled + wreath on a red porch wall)
def sled_upright(c, ox, oy, s, seed):
    """Wooden slat sled stood on its tail against a wall, front curls at the top. Local: x -60..60, y 0..330."""
    o = [f'<g transform="translate({F(ox)} {F(oy)}) rotate(-4 0 330) scale({s})">']
    o.append(f'<path d="M -62 10 Q 0 -6 62 10 L 70 330 L -66 330 Z" fill="#3A0A0E" opacity="0.3" transform="translate(18 2)"/>')
    # iron runners with curled fronts
    for sg in (-1, 1):
        x = 60 * sg
        d = f"M {x} 330 L {x} 46 C {x} 14 {x - sg * 4} -2 {x - sg * 22} 0 C {x - sg * 38} 2 {x - sg * 36} 24 {x - sg * 20} 22"
        o.append(ink(d, "#1E1A1C", 10, seed, 1, 1))
        o.append(ink(f"M {x - sg * 2.5} 320 L {x - sg * 2.5} 50 C {x - sg * 2.5} 22 {x - sg * 6} 6 {x - sg * 20} 6", "#8A8288", 2.4, seed + 1, 1, 0.75))
        for yy in (120, 230, 310):
            o.append(ink(f"M {x} {yy} L {x - sg * 12} {yy - 6}", "#1E1A1C", 5, seed + yy, 1, 1))
    # four honey-wood slats
    for k, (x0, x1) in enumerate(((-54, -30), (-25, -2), (2, 25), (30, 54))):
        top, bot = (52, 324) if k in (1, 2) else (66, 316)
        xm, hw = (x0 + x1) / 2, (x1 - x0) / 2
        pts = [(x0, top + 10), (xm - hw * 0.7, top + 2.5), (xm, top), (xm + hw * 0.7, top + 2.5), (x1, top + 10), (x1, (top + bot) / 2),
               (x1, bot - 8), (xm + hw * 0.7, bot - 1.5), (xm, bot), (xm - hw * 0.7, bot - 1.5), (x0, bot - 8), (x0, (top + bot) / 2)]
        o.append(shape(c, pts, "#C98E52", ["#E0A868", "#A8723E", "#F2C489", "#8A5A2E"], seed + 2 + k, angle=-90, n=50,
                       length=(30, 90), width=(1, 2.6), op=(0.3, 0.65), curve=0.04, iw=1.8))
        o.append(ink(f"M {x0 + 4} {top + 14} L {x0 + 4} {bot - 12}", "#FBE0B0", 1.8, seed + k, 1, 0.55))
    # painted decoration down the middle slats: a red star and gold pinstripes
    o.append(ink("M -40 196 Q 0 176 40 196 M -40 276 Q 0 296 40 276", GOLD_D, 2.4, seed, 1, 0.85))
    o.append(pstar(c, 0, 236, 26, RED, seed + 9, tints=["#E2524A", CRAN, "#F07058"], iw=1.6))
    o.append(pstar(c, 0, 236, 9, GOLD_L, seed + 10, iw=0.8))
    # rear cross bar
    rb = [(-62, 292), (62, 292), (62, 306), (-62, 306)]
    o.append(shape(c, rb, "#A8723E", ["#C98E52", "#7A4A24"], seed + 11, angle=0, n=14, iw=1.8,
                   d="M -62 292 L 62 292 L 62 306 L -62 306 Z"))
    # steering bar, painted green, with bolts
    sb = [(-82, 70), (-76, 62), (76, 62), (82, 70), (76, 80), (-76, 80)]
    o.append(shape(c, sb, GREEN, [GREEN_L, GREEN_D], seed + 12, angle=0, n=24, iw=2.2))
    o.append(ink("M -74 66 L 74 66", "#9AC4A0", 2, seed, 1, 0.6))
    for bx in (-60, 60):
        o.append(f'<circle cx="{bx}" cy="71" r="3.4" fill="#2A2628"/><circle cx="{bx - 1}" cy="70" r="1.2" fill="#C8C0C4"/>')
    # wreath hung from the steering bar on a red ribbon
    o.append(ink("M -2 78 L 0 104", RED, 5, seed, 1, 1))
    o.append(wreath(c, 0, 150, 46, seed + 20, needle=(9, 16), cones=False))
    for sx_ in (-1, 1):
        lp = [(0, 106), (sx_ * 18, 90), (sx_ * 30, 94), (sx_ * 26, 110), (sx_ * 8, 112)]
        o.append(shape(c, lp, RED, ["#E2524A", CRAN_D], seed + 30 + sx_, n=10, iw=1.6))
        tl = [(0, 110), (sx_ * 12, 134), (sx_ * 20, 152), (sx_ * 10, 150), (sx_ * 2, 124)]
        o.append(shape(c, tl, CRAN, [RED, CRAN_D], seed + 33 + sx_, n=8, iw=1.4))
    o.append(shape(c, blob_pts(0, 108, 8, 7, seed + 35, 0.1, 10), CRAN, [RED], seed + 35, n=4, iw=1.4))
    o.append("</g>")
    return "".join(o)


def log_end(c, x, y, r, seed):
    o = [shape(c, blob_pts(x, y, r, r * 0.96, seed, 0.06, 14), "#D9B07A", ["#E8C894", "#B8864E"], seed, angle=-30, n=14, iw=1.8)]
    o.append("".join(f'<path d="{blob(x + 1, y + 1, r * k, r * k * 0.95, seed + int(k * 10), 0.08, 12)}" fill="none" stroke="#9A6A3A" stroke-width="1.2" opacity="0.7"/>'
                     for k in (0.28, 0.52, 0.76)))
    o.append(f'<path d="{blob(x, y, r, r * 0.96, seed, 0.06, 14)}" fill="none" stroke="#5A3418" stroke-width="{F(r * 0.14)}" opacity="0.85"/>')
    return "".join(o)


def sleigh_all_day():
    c = C("sad")
    o = [wash_bg(c, "#8E2A2C", ["#9E3434", "#7A2024", "#A8403A", "#6E1C20"], 3, angle=-90, n=320, length=(60, 160), width=(6, 14))]
    # board-and-batten: battens every 66 px, nail heads
    rnd = random.Random(4)
    for x in range(-10, 640, 66):
        bt = jitter([(x - 7, -10), (x + 7, -10), (x + 7, 520), (x - 7, 520)], x, 1)
        d = "M " + " L ".join(f"{F(a)} {F(b)}" for a, b in bt) + " Z"
        o.append(f'<path d="{d}" fill="#5A1418" opacity="0.35" transform="translate(4 0)"/>')
        o.append(f'<path d="{d}" fill="#962E30"/>' + strokes(c.id("bt"), d, (x - 8, -10, x + 8, 520), ["#B04440", "#7A2024"], x, n=30, angle=-90,
                                                                length=(40, 100), width=(1.5, 3), opacity=(0.3, 0.6)))
        o.append(ink(f"M {x - 7} -10 L {x - 7} 520", "#4A0E12", 1.6, x, 1, 0.6) + ink(f"M {x - 4} -10 L {x - 4} 520", "#C25A50", 1.2, x + 1, 1, 0.5))
        for yy in (150, 330, 480):
            o.append(f'<circle cx="{x}" cy="{yy + rnd.uniform(-4, 4):.0f}" r="2.2" fill="#3A0A0E" opacity="0.7"/>')
    # lantern glow wash on the wall
    o.append(c.oglow(130, 470, 210, 190, "#FFB25A", 0.45))
    o.append(c.oglow(300, 140, 300, 120, "#3A0A0E", 0.35))
    # porch floor
    fl = "M -20 512 L 620 512 L 620 620 L -20 620 Z"
    o.append(f'<path d="{fl}" fill="#8C8078"/>')
    o.append(strokes(c.id("fl"), fl, (-20, 510, 620, 620), ["#A89C92", "#6E625C", "#B8ACA0", "#7A6E66"], 5, n=160, angle=-1,
                     length=(40, 120), width=(1.5, 4), opacity=(0.3, 0.6), curve=0.03))
    for y in (512, 538, 568):
        o.append(ink(f"M -20 {y} L 620 {y + 2}", "#4A3E3A", 2 if y > 512 else 3.2, y, 1, 0.7))
    o.append(ink("M -20 515 L 620 516", "#C8BCB0", 1.4, 3, 1, 0.5))
    # drifted snow along the wall and in the corners
    o.append(snow_lump(c, [(-20, 482), (20, 474), (56, 486), (88, 504), (122, 520), (140, 530), (60, 534), (-20, 536)], 6, inkc=None))
    o.append(snow_lump(c, [(400, 528), (440, 512), (500, 498), (560, 480), (620, 474), (620, 538), (500, 538)], 7, inkc=None))
    o.append(spatter(8, 50, (0, 518, 600, 600), ["#FFFFFF"], r=(1.2, 3.2), op=(0.6, 0.95)))
    # firewood stack at right
    for (x, y, r), sd in zip(((444, 494, 24), (494, 494, 24), (544, 492, 24), (468, 452, 23), (518, 450, 23), (494, 410, 22)), range(6)):
        o.append(log_end(c, x, y, r, 40 + sd))
    o.append(snow_lump(c, [(470, 398), (476, 386), (494, 382), (512, 386), (520, 398), (506, 394), (494, 400), (480, 396)], 44, iw=0.8))
    # lantern at left
    o.append(lantern(c, 118, 530, 1.1, 50))
    # the sled
    o.append(cast(306, 532, 110, 8, "#2A1010", 0.4, 9))
    o.append(sled_upright(c, 300, 222, 0.93, 11))
    # falling snow outside the porch roof line
    o.append(spatter(12, 40, (0, 0, 600, 240), ["#FFFFFF"], r=(1.1, 2.8), op=(0.5, 0.9), avoid=[(80, 50, 520, 230)]))
    # lettering
    o.append(L(c, 300, 138, "sleigh", SERIF_IT, 106, CREAM, ["#FFFFFF", "#F2DCC0", "#E8CFA8"], max_w=360, shadow="#4A0E12", seed=13,
               angle=-35, sdx=0.025, sdy=0.04))
    o.append(L(c, 300, 202, "ALL DAY", BEBAS, 66, GOLD_L, [GOLD, "#FFF0B8", GOLD_D], max_w=250, ls=14, shadow="#4A0E12", seed=14, angle=-80))
    for sx_ in (-1, 1):
        o.append(pstar(c, 300 + sx_ * 150, 180, 10, GOLD_L, 15 + sx_, iw=1.0))
    return finish(c, "".join(o))


# ================================================================ NEW: warm-and-cozy (mulled cider in a glass mug)
def orange_slice(c, x, y, r, seed, rot=0):
    o = [f'<g transform="rotate({rot} {F(x)} {F(y)})">']
    o.append(shape(c, blob_pts(x, y, r, r, seed, 0.03, 18), "#E8762A", ["#F29A48", "#C85A1A"], seed, n=14, iw=1.8))
    o.append(f'<path d="{blob(x, y, r * 0.86, r * 0.86, seed + 1, 0.03, 16)}" fill="#FBEBD0"/>')
    o.append(f'<path d="{blob(x, y, r * 0.78, r * 0.78, seed + 2, 0.03, 16)}" fill="#F6A548"/>')
    segs = []
    for k in range(10):
        a = math.radians(k * 36 + 8)
        segs.append(f"M {F(x)} {F(y)} L {F(x + r * 0.78 * math.cos(a))} {F(y + r * 0.78 * math.sin(a))}")
    o.append(f'<path d="{" ".join(segs)}" stroke="#FBE6C4" stroke-width="{F(max(1.4, r * 0.06))}" stroke-linecap="round" fill="none"/>')
    rnd = random.Random(seed)
    for k in range(10):
        a = math.radians(k * 36 + 26)
        o.append(f'<path d="{blob(x + r * 0.5 * math.cos(a), y + r * 0.5 * math.sin(a), r * 0.12, r * 0.06, seed + k, 0.2, 8, rot=k * 36 + 26)}" fill="#FFD08A" opacity="0.8"/>')
    o.append(f'<circle cx="{F(x)}" cy="{F(y)}" r="{F(r * 0.1)}" fill="#FBEBD0"/>')
    o.append("</g>")
    return "".join(o)


def star_anise(c, x, y, r, seed, rot=0):
    o = []
    for k in range(8):
        a = rot + k * 45
        pts = rot_pts([(0, 0), (r * 0.3, r * 0.2), (r * 0.85, r * 0.18), (r, 0), (r * 0.85, -r * 0.18), (r * 0.3, -r * 0.2)], x, y, a)
        o.append(shape(c, pts, "#7A3E1E", ["#9A5A2E", "#5A2A12"], seed + k, n=4, iw=1.2, inkc="#3A1A0A"))
        sd = rot_pts([(r * 0.62, 0)], x, y, a)[0]
        o.append(f'<path d="{blob(sd[0], sd[1], r * 0.1, r * 0.07, seed + k, 0.1, 8, rot=a)}" fill="#C8884A"/>')
    o.append(f'<path d="{blob(x, y, r * 0.18, r * 0.18, seed, 0.1, 8)}" fill="#5A2A12"/>')
    return "".join(o)


def cinnamon(c, x1, y1, x2, y2, w, seed):
    a = math.atan2(y2 - y1, x2 - x1)
    nx, ny = -math.sin(a) * w / 2, math.cos(a) * w / 2
    pts = [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)]
    d = "M " + " L ".join(f"{F(px)} {F(py)}" for px, py in pts) + " Z"
    o = [shape(c, pts, "#8A4A22", ["#A8622E", "#6A3416", "#B87440"], seed, angle=math.degrees(a), n=int(math.hypot(x2 - x1, y2 - y1) / 3),
               length=(14, 40), width=(1, 2.4), op=(0.35, 0.7), iw=1.6, d=d)]
    o.append(ink(f"M {F(x1 + nx * 0.2)} {F(y1 + ny * 0.2)} L {F(x2 + nx * 0.2)} {F(y2 + ny * 0.2)}", "#4A2210", 1.4, seed, 1, 0.7))
    # rolled end
    o.append(f'<ellipse cx="{F(x2)}" cy="{F(y2)}" rx="{F(w * 0.5)}" ry="{F(w * 0.32)}" transform="rotate({F(math.degrees(a) + 90)} {F(x2)} {F(y2)})" fill="#C88A52" stroke="#4A2210" stroke-width="1.2"/>')
    o.append(f'<path d="M {F(x2 - nx * 0.5)} {F(y2 - ny * 0.5)} Q {F(x2 + nx * 0.3)} {F(y2 + ny * 0.3 - 2)} {F(x2 + nx * 0.1)} {F(y2 + ny * 0.1 + 2)}" stroke="#6A3416" stroke-width="1.2" fill="none"/>')
    return "".join(o)


def warm_and_cozy():
    c = C("wac")
    o = [wash_bg(c, "#E7B487", ["#EEC39A", "#DDA275", "#F4D0AA", "#D8966A"], 3, angle=-20, n=300)]
    o.append(c.oglow(300, 330, 300, 240, "#FFE6B8", 0.6))
    # out-of-focus fairy lights in the background
    rnd = random.Random(5)
    for _ in range(26):
        x, y = rnd.uniform(20, 580), rnd.uniform(200, 440)
        if 180 < x < 420 and y > 220:
            continue
        rr = rnd.uniform(8, 20)
        o.append(f'<path d="{blob(x, y, rr, rr, rnd.randint(0, 999), 0.06, 12)}" fill="{rnd.choice([GOLD_L, "#FFF2D0", "#F8C878"])}" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>')
    # walnut table
    tb = "M -20 452 L 620 452 L 620 620 L -20 620 Z"
    o.append(f'<path d="{tb}" fill="#6A3E24"/>')
    o.append(strokes(c.id("tb"), tb, (-20, 450, 620, 620), ["#8A5A36", "#4A2A16", "#9A6A40", "#5A3420"], 6, n=170, angle=-1,
                     length=(50, 140), width=(1.5, 4), opacity=(0.3, 0.6), curve=0.03))
    o.append(ink("M -20 452 L 620 454", "#B8845A", 2.6, 4, 1, 0.8) + ink("M -20 532 L 620 530", "#3A2012", 1.8, 5, 1, 0.5))
    # amber light thrown through the cider onto the table
    o.append(c.oglow(310, 482, 150, 30, "#F8A84A", 0.7))
    o.append(cast(300, 470, 104, 12, "#2A1408", 0.45, 6))
    # ---- the glass mug
    top_y, bot_y, rt, rb = 248, 462, 92, 80
    cx = 290
    body = [(cx - rt, top_y), (cx - rb, bot_y - 10), (cx - rb + 8, bot_y + 4), (cx, bot_y + 8), (cx + rb - 8, bot_y + 4), (cx + rb, bot_y - 10), (cx + rt, top_y)]
    bd = (f"M {cx - rt} {top_y} L {cx - rb} {bot_y - 10} Q {cx - rb} {bot_y + 8} {cx} {bot_y + 8} Q {cx + rb} {bot_y + 8} {cx + rb} {bot_y - 10} "
          f"L {cx + rt} {top_y} A {rt} 16 0 0 0 {cx - rt} {top_y} Z")
    o.append(f'<path d="{bd}" fill="#FFF6E8" opacity="0.35"/>')
    # handle (behind-ish, thick glass)
    hd = f"M {cx + rt - 6} 286 C {cx + rt + 54} 280 {cx + rt + 56} 410 {cx + rb - 4} 418"
    o.append(ink(hd, "#E8C9A0", 22, 1, 1, 0.55) + ink(hd, "#FFFFFF", 6, 2, 1, 0.55) + ink(hd, "#8A5A36", 1.6, 3, 1, 0.6))
    o.append(ink(f"M {cx + rt + 4} 296 C {cx + rt + 36} 294 {cx + rt + 38} 396 {cx + rb + 4} 404", "#8A5A36", 1.4, 4, 1, 0.5))
    # cinnamon stick standing in the drink (drawn before the cider so it shows through)
    stick = (cx - 22, 410, cx - 52, 196)
    o.append(cinnamon(c, *stick, 18, 7))
    # cider body
    sy = 274
    ld = (f"M {cx - rt + 2.4} {sy} L {cx - rb + 3} {bot_y - 18} Q {cx - rb + 4} {bot_y - 4} {cx} {bot_y - 4} Q {cx + rb - 4} {bot_y - 4} {cx + rb - 3} {bot_y - 18} "
          f"L {cx + rt - 2.4} {sy} Z")
    g = c.lg([(0, "#F0A443", 0.82), (0.55, "#D8762A", 0.88), (1, "#A8481A", 0.95)])
    o.append(f'<path d="{ld}" fill="url(#{g})"/>')
    o.append(strokes(c.id("cd"), ld, (cx - rt, sy, cx + rt, bot_y), ["#F8B85A", "#C8601E", "#FFD08A"], 8, n=60, angle=-88, length=(20, 60),
                     width=(2, 6), opacity=(0.15, 0.35)))
    # a submerged orange wheel and cranberries seen through the glass
    o.append(f'<g opacity="0.55">{orange_slice(c, cx + 30, 380, 40, 9, 10)}</g>')
    for k, (bx, by) in enumerate(((cx - 40, 430), (cx + 52, 440), (cx - 8, 444))):
        o.append(f'<g opacity="0.6">{berry(c, bx, by, 9, CRAN, 20 + k)}</g>')
    o.append(c.oglow(cx - 10, 360, 70, 80, "#FFE2A0", 0.35))
    # surface
    o.append(f'<ellipse cx="{cx}" cy="{sy}" rx="{rt - 3}" ry="14" fill="#F6B860"/>'
             f'<ellipse cx="{cx}" cy="{sy}" rx="{rt - 3}" ry="14" fill="none" stroke="#B8561E" stroke-width="1.6" opacity="0.6"/>'
             f'<ellipse cx="{cx - 20}" cy="{sy - 3}" rx="40" ry="5" fill="#FFE4A8" opacity="0.7"/>')
    o.append(star_anise(c, cx + 18, sy - 1, 15, 30, 10))
    o.append(berry(c, cx - 30, sy + 2, 8, CRAN, 31) + berry(c, cx + 52, sy + 3, 7, CRAN, 32))
    # stick above the surface again (in front of the surface)
    cl = c.id("ab")
    o.append(f'<clipPath id="{cl}"><path d="M 0 0 L 600 0 L 600 {sy - 2} L 0 {sy - 2} Z"/></clipPath><g clip-path="url(#{cl})">{cinnamon(c, *stick, 18, 7)}</g>')
    # glass: thick base, rim, reflections
    o.append(f'<path d="M {cx - rb + 2} {bot_y - 12} Q {cx} {bot_y + 2} {cx + rb - 2} {bot_y - 12} L {cx + rb} {bot_y - 6} Q {cx} {bot_y + 14} {cx - rb} {bot_y - 6} Z" fill="#FFF2DE" opacity="0.6"/>')
    o.append(ink(f"M {cx - rt + 12} {top_y + 18} L {cx - rb + 12} {bot_y - 22}", "#FFFFFF", 7, 3, 1, 0.65))
    o.append(ink(f"M {cx - rt + 26} {top_y + 24} L {cx - rb + 24} {bot_y - 60}", "#FFFFFF", 2.4, 4, 1, 0.5))
    o.append(ink(f"M {cx + rt - 14} {top_y + 22} L {cx + rb - 12} {bot_y - 24}", "#FFF4E0", 3, 5, 1, 0.5))
    o.append(f'<ellipse cx="{cx}" cy="{top_y}" rx="{rt}" ry="16" fill="none" stroke="#FFFFFF" stroke-width="3.4" opacity="0.8"/>')
    o.append(ink(f"M {cx - rt} {top_y} L {cx - rb} {bot_y - 10} Q {cx - rb} {bot_y + 8} {cx} {bot_y + 8} Q {cx + rb} {bot_y + 8} {cx + rb} {bot_y - 10} L {cx + rt} {top_y}",
                 "#7A4A2A", 2, 6, 2, 0.7))
    o.append(ink(f"M {cx - rt} {top_y} A {rt} 16 0 0 0 {cx + rt} {top_y}", "#7A4A2A", 1.6, 7, 1, 0.6))
    # orange wheel perched on the rim
    o.append(orange_slice(c, cx + 74, top_y + 6, 40, 40, -12))
    # steam
    for k, (sx_, sd) in enumerate(((cx - 34, 1), (cx + 6, 2), (cx + 40, 3))):
        d = f"M {sx_} {sy - 10} C {sx_ - 22} {sy - 34} {sx_ + 20} {sy - 52} {sx_} {sy - 76} C {sx_ - 14} {sy - 92} {sx_ + 8} {sy - 70 - 30} {sx_ + 2} {sy - 108 + k * 6}"
        o.append(ink(d, "#FFFFFF", 6 - k, sd, 1, 0.55))
    # props on the table
    o.append(cast(118, 520, 66, 9, "#2A1408", 0.4, 11))
    oh = blob_pts(118, 494, 58, 30, 12, 0.03, 18)
    o.append(shape(c, oh, "#E8762A", ["#F29A48", "#C85A1A", "#F8B060"], 12, angle=-10, n=40, iw=2))
    o.append(f'<g transform="translate(118 488) scale(1 0.42) translate(-118 -488)">{orange_slice(c, 118, 488, 52, 13)}</g>')
    o.append(cinnamon(c, 412, 524, 520, 500, 17, 14) + cinnamon(c, 404, 508, 516, 486, 17, 15) + cinnamon(c, 420, 540, 528, 516, 17, 16))
    o.append(ink("M 458 494 Q 470 520 474 538", "#D9B47A", 3.4, 17, 1, 0.95) + ink("M 462 492 q -10 -10 -6 -18 M 462 492 q 12 -8 16 -16", "#D9B47A", 2.4, 18, 1, 0.9))
    o.append(star_anise(c, 222, 520, 17, 19, 15) + star_anise(c, 498, 470, 13, 20, 30))
    for k, (bx, by) in enumerate(((186, 478), (200, 492), (372, 532), (388, 520), (560, 540), (60, 540))):
        o.append(berry(c, bx, by, 7.5, CRAN, 40 + k))
    o.append(spatter(41, 30, (40, 460, 560, 560), ["#3A1A0A"], r=(1, 2), op=(0.4, 0.7), avoid=[(60, 460, 540, 530)]))
    # lettering
    o.append(L(c, 300, 128, "warm & cozy", SERIF_IT, 104, "#7A2A1E", [CRAN_D, "#5A1E14", "#9A3A28"], max_w=460, shadow="#F8DCB8",
               seed=21, angle=-35))
    lw = measure("MULLED CIDER", JOS, 20, 6)
    o.append(f'<text x="303" y="176" text-anchor="middle" {JOS} font-size="20" letter-spacing="6" fill="#7A3A22">MULLED CIDER</text>')
    for sx_ in (-1, 1):
        o.append(ink(f"M {F(300 + sx_ * (lw / 2 + 12))} 170 L {F(300 + sx_ * (lw / 2 + 52))} 170", "#7A3A22", 2, 22 + sx_, 1, 0.8))
    return finish(c, "".join(o))


# ================================================================ NEW: home-for-christmas (candlelit window, a cat on the sill)
def sitting_cat(c, x, base, s, seed):
    """Ginger tabby sitting, seen from the front, backlit by the room; head turned up-left to watch the snow."""
    o = [f'<g transform="translate({F(x)} {F(base)}) scale({s})">']
    fur, fur_d, fur_l = "#D9823A", "#A85A22", "#F2A85E"
    tail = [(30, -6), (58, -14), (74, -32), (70, -44), (60, -30), (44, -20), (26, -18)]
    o.append(shape(c, tail, fur, [fur_d, fur_l], seed, angle=-30, n=14, iw=1.8))
    body = [(-40, 0), (-46, -30), (-40, -64), (-26, -86), (0, -92), (26, -86), (40, -64), (46, -30), (40, 0)]
    o.append(shape(c, body, fur, [fur_d, fur_l, "#C46E2C"], seed + 1, angle=-90, n=70, length=(8, 20), width=(2, 4), iw=2.2))
    cl = c.id("ct")
    o.append(f'<clipPath id="{cl}"><path d="{smooth_closed(body)}"/></clipPath><g clip-path="url(#{cl})">'
             f'<path d="{blob(0, -40, 18, 40, seed, 0.1)}" fill="#F8DCB4" opacity="0.9"/>'
             f'<path d="{blob(36, -40, 16, 50, seed + 1, 0.1)}" fill="{fur_d}" opacity="0.4"/>'
             + "".join(f'<path d="M {sg * 46} {y} q {sg * -14} -4 {sg * -22} 2" stroke="{fur_d}" stroke-width="4" fill="none" stroke-linecap="round"/>'
                       for sg in (-1, 1) for y in (-70, -52, -34)) + "</g>")
    # paws
    for sg in (-1, 1):
        o.append(shape(c, blob_pts(sg * 14, -4, 12, 7, seed + 2 + sg, 0.08, 10), "#F8DCB4", ["#FFFFFF", "#E8C49A"], seed + 2, n=6, iw=1.4))
        o.append(ink(f"M {sg * 14 - 3} -6 l 0 5 M {sg * 14 + 3} -6 l 0 5", INK, 1, seed, 1, 0.7))
    # head
    hx, hy = -4, -110
    head = [(hx - 38, hy + 4), (hx - 40, hy - 14), (hx - 36, hy - 48), (hx - 24, hy - 26), (hx, hy - 30), (hx + 24, hy - 26), (hx + 36, hy - 48),
            (hx + 40, hy - 14), (hx + 38, hy + 4), (hx + 24, hy + 22), (hx, hy + 28), (hx - 24, hy + 22)]
    o.append(shape(c, head, fur, [fur_d, fur_l], seed + 4, angle=-60, n=40, length=(6, 14), width=(1.5, 3.5), iw=2.2))
    for sg in (-1, 1):
        o.append(f'<path d="{smooth_closed([(hx + sg * 32, hy - 20), (hx + sg * 33, hy - 40), (hx + sg * 22, hy - 26)])}" fill="#F2A8A0" opacity="0.85"/>')
    o.append(ink(f"M {hx - 8} {hy - 26} l 2 10 M {hx} {hy - 28} l 0 12 M {hx + 8} {hy - 26} l -2 10", fur_d, 3, seed, 1, 0.8))
    o.append(f'<path d="{blob(hx, hy + 10, 16, 12, seed + 5, 0.1)}" fill="#F8DCB4"/>')
    # eyes looking up and to the left
    for sg in (-1, 1):
        ex, ey = hx + sg * 15, hy - 4
        o.append(f'<path d="{blob(ex, ey, 7.5, 6.5, seed + 6 + sg, 0.06, 10)}" fill="#9AC46A"/>'
                 f'<path d="{blob(ex - 2, ey - 1.5, 2.6, 5, seed, 0.06, 8)}" fill="#1A1410"/><circle cx="{F(ex - 3.6)}" cy="{F(ey - 3)}" r="1.6" fill="#FFFFFF"/>')
        o.append(ink(f"M {ex - 8} {ey} Q {ex} {ey - 9} {ex + 8} {ey}", INK, 1.8, seed + sg, 1, 0.9))
    o.append(f'<path d="M {hx - 4} {hy + 6} L {hx + 4} {hy + 6} L {hx} {hy + 11} Z" fill="#D8707A"/>')
    o.append(ink(f"M {hx} {hy + 11} q -4 6 -9 3 M {hx} {hy + 11} q 4 6 9 3", INK, 1.4, seed, 1, 0.8))
    o.append(ink(f"M {hx - 16} {hy + 10} l -24 -3 M {hx - 16} {hy + 14} l -22 4 M {hx + 16} {hy + 10} l 24 -3 M {hx + 16} {hy + 14} l 22 4",
                 "#FFF6E8", 1.2, seed, 1, 0.8))
    # warm rim light from the room behind
    o.append(ink(smooth_open([(hx - 36, hy - 46), (hx - 40, hy - 14), (hx - 38, hy + 4)]), "#FFE6A8", 2.4, seed, 1, 0.8))
    o.append(ink(smooth_open([(-40, -64), (-46, -30), (-40, 0)]), "#FFE6A8", 2.4, seed + 1, 1, 0.7))
    o.append("</g>")
    return "".join(o)


def candle(c, x, base, h, seed, col=CREAM, holder=GOLD):
    o = [c.glow(x, base - h - 14, 70, "#FFD98E", 0.75), c.glow(x, base - h - 14, 26, "#FFFFFF", 0.7)]
    body = [(x - 9, base - 4), (x - 9, base - h + 2), (x - 4, base - h), (x + 9, base - h + 1), (x + 9, base - 4)]
    o.append(shape(c, body, col, ["#FFFFFF", "#EADCC0"], seed, angle=-90, n=10, iw=1.4))
    o.append(f'<path d="M {x - 9} {base - h + 2} q -1 10 2 14 q 2 -6 0 -14 Z" fill="#FFFFFF" opacity="0.9"/>')
    o.append(ink(f"M {x} {base - h} l 0 -5", "#2A1810", 1.6, seed, 1, 1))
    o.append(f'<path d="M {x} {base - h - 30} Q {x + 8} {base - h - 14} {x} {base - h - 4} Q {x - 8} {base - h - 14} {x} {base - h - 30} Z" fill="#F8A83A"/>'
             f'<path d="M {x} {base - h - 22} Q {x + 4} {base - h - 12} {x} {base - h - 6} Q {x - 4} {base - h - 12} {x} {base - h - 22} Z" fill="#FFF6D8"/>')
    hp = [(x - 22, base), (x - 16, base - 8), (x + 16, base - 8), (x + 22, base), (x + 14, base + 4), (x - 14, base + 4)]
    o.append(shape(c, hp, holder, [GOLD_L, GOLD_D], seed + 1, n=8, iw=1.4))
    o.append(holly(c, x - 14, base - 4, 0.45, -10, seed + 2, berries=2))
    return "".join(o)


def home_for_christmas():
    c = C("hfc")
    o = [f'<rect width="600" height="600" fill="#24365A"/>']
    # clapboard siding at night
    for k, y in enumerate(range(-10, 620, 34)):
        bd = f"M -20 {y} L 620 {y} L 620 {y + 34} L -20 {y + 34} Z"
        o.append(strokes(c.id("cb"), bd, (-20, y, 620, y + 34), ["#2E4470", "#1C2C4C", "#344C7A"], k, n=30, angle=-1, length=(60, 160),
                         width=(2, 5), opacity=(0.3, 0.6), curve=0.02))
        o.append(ink(f"M -20 {y + 33} L 620 {y + 34}", "#121C34", 3, k, 1, 0.8) + ink(f"M -20 {y + 2} L 620 {y + 1}", "#4A6294", 1.2, k + 1, 1, 0.5))
    # the window throws warm light onto the siding
    o.append(c.oglow(300, 370, 300, 250, "#FFB25A", 0.55))
    # ---- window: trim, glass room, sashes
    X0, X1, Y0, Y1 = 160, 440, 258, 482
    trim = jitter([(140, 240), (460, 240), (460, 496), (140, 496)], 3, 1.2)
    o.append(f'<path d="M 146 246 L 468 246 L 468 504 L 146 504 Z" fill="#0E1628" opacity="0.4" transform="translate(6 6)"/>')
    o.append(shape(c, trim, "#EFE6D6", ["#FFFFFF", "#D8CCBA", SHADE_L], 4, angle=-90, n=60, iw=2.2, d="M " + " L ".join(f"{F(a)} {F(b)}" for a, b in trim) + " Z"))
    room = f"M {X0} {Y0} L {X1} {Y0} L {X1} {Y1} L {X0} {Y1} Z"
    g = c.lg([(0, "#E88A3A"), (0.6, "#F4B04E"), (1, "#F8C870")])
    o.append(f'<path d="{room}" fill="url(#{g})"/>')
    o.append(strokes(c.id("rm"), room, (X0, Y0, X1, Y1), ["#F8C878", "#E07A2A", "#FFD890"], 5, n=90, angle=-80, length=(20, 60), width=(4, 10),
                     opacity=(0.15, 0.35)))
    cl = c.id("rmc")
    inner = [c.glow(380, 330, 150, "#FFF2C4", 0.8)]
    # a Christmas tree glowing in the back of the room, softly out of focus
    tp = [(392, 272), (440, 400), (450, 486), (330, 486), (344, 400)]
    inner.append(f'<path d="{smooth_closed(tp)}" fill="#3E6A4A" opacity="0.85"/>')
    inner.append(strokes(c.id("tr"), smooth_closed(tp), (320, 260, 460, 490), ["#2C5B45", "#4F8160", "#5E9070"], 6, n=60, angle=-60,
                         length=(10, 24), width=(2, 4), opacity=(0.3, 0.6)))
    rnd = random.Random(7)
    for _ in range(26):
        yy = rnd.uniform(286, 470)
        half = (yy - 272) / (486 - 272) * 58
        xx = 392 + rnd.uniform(-half, half)
        col = rnd.choice([GOLD_L, "#FFF2D0", RED_L, "#9AD0E8", GOLD_L])
        inner.append(f'<circle cx="{F(xx)}" cy="{F(yy)}" r="{rnd.uniform(4, 8):.1f}" fill="{col}" opacity="{rnd.uniform(0.5, 0.85):.2f}"/>')
    inner.append(c.glow(392, 270, 20, "#FFF6C8", 0.9) + pstar(c, 392, 270, 10, GOLD, 8, iw=1))
    # interior sill
    inner.append(shape(c, [(X0 - 4, Y1 - 10), (X1 + 4, Y1 - 10), (X1 + 4, Y1 + 2), (X0 - 4, Y1 + 2)], "#C88E5A", ["#E0A868", "#A8723E"], 9, angle=0, n=20,
                       iw=1.4, d=f"M {X0 - 4} {Y1 - 10} L {X1 + 4} {Y1 - 10} L {X1 + 4} {Y1 + 2} L {X0 - 4} {Y1 + 2} Z"))
    inner.append(candle(c, 384, Y1 - 10, 50, 10))
    inner.append(sitting_cat(c, 246, Y1 - 10, 0.8, 11))
    o.append(f'<clipPath id="{cl}"><path d="{room}"/></clipPath><g clip-path="url(#{cl})">{"".join(inner)}'
             # glass reflections
             f'<path d="M {X0} {Y0 + 120} L {X0 + 120} {Y0} L {X0 + 150} {Y0} L {X0} {Y0 + 150} Z" fill="#FFFFFF" opacity="0.12"/>'
             f'<path d="M {X0 + 170} {Y1} L {X1} {Y0 + 70} L {X1} {Y0 + 86} L {X0 + 186} {Y1} Z" fill="#FFFFFF" opacity="0.1"/>'
             f'<path d="M {X0} {Y1 - 60} Q {X0 + 60} {Y1 - 40} {X0 + 120} {Y1 - 6} L {X0} {Y1} Z" fill="#FFFFFF" opacity="0.14"/></g>')
    # frost creeping in the pane corners
    o.append(f'<g clip-path="url(#{cl})">' + "".join(f'<path d="{blob(fx, fy, 40, 34, fx, 0.2, 14)}" fill="#FFFFFF" opacity="0.28"/>'
                                                     for fx, fy in ((X0, Y0), (X1, Y0), (X0, Y1))) + "</g>")
    # sashes: upper with muntins (3x2), meeting rail, lower clear pane
    sash = "#F2EADC"
    MR = 334
    bars = [(X0, MR - 6, X1, MR + 8), (X0, Y0, X1, Y0 + 8), (X0, Y0, X0 + 8, Y1), (X1 - 8, Y0, X1, Y1)]
    for xm in (X0 + (X1 - X0) / 3, X0 + 2 * (X1 - X0) / 3):
        bars.append((xm - 4, Y0, xm + 4, MR))
    bars.append((X0, (Y0 + MR) / 2 - 4, X1, (Y0 + MR) / 2 + 4))
    for k, (a, b, c2, d2) in enumerate(bars):
        bd = f"M {F(a)} {F(b)} L {F(c2)} {F(b)} L {F(c2)} {F(d2)} L {F(a)} {F(d2)} Z"
        o.append(f'<path d="{bd}" fill="{sash}"/>' + ink(bd, INK, 1.4, k, 1, 0.55))
    o.append(ink(f"M {X0} {MR - 6} L {X1} {MR - 6}", "#FFFFFF", 1.6, 2, 1, 0.8))
    # header cornice with snow and icicles
    hd = jitter([(124, 220), (476, 220), (482, 242), (118, 242)], 5, 1)
    o.append(shape(c, hd, "#EFE6D6", ["#FFFFFF", "#D8CCBA"], 6, angle=0, n=30, iw=2, d="M " + " L ".join(f"{F(a)} {F(b)}" for a, b in hd) + " Z"))
    o.append(snow_lump(c, [(114, 222), (150, 208), (220, 212), (300, 204), (380, 212), (450, 206), (488, 222), (440, 228), (300, 226), (160, 228)], 7))
    rnd = random.Random(9)
    for k, x in enumerate(range(130, 476, 18)):
        L_ = rnd.uniform(8, 26)
        o.append(f'<path d="M {x - 4} 241 Q {x - 1} {241 + L_ * 0.6:.1f} {x + rnd.uniform(-1, 1):.1f} {241 + L_:.1f} Q {x + 1.5} {241 + L_ * 0.5:.1f} {x + 4} 241 Z" fill="#E8F2F8" opacity="0.92"/>')
    # garland swag of bulbs across the header
    sw = [(120, 236), (210, 262), (300, 248), (390, 262), (480, 236)]
    o.append(needles(c, sw, 12, length=(10, 20), density=0.7, w=2.4))
    for k in range(9):
        t = (k + 0.5) / 9
        i = min(int(t * 4), 3)
        lt_ = t * 4 - i
        bx = sw[i][0] + (sw[i + 1][0] - sw[i][0]) * lt_
        by = sw[i][1] + (sw[i + 1][1] - sw[i][1]) * lt_ + 8
        col = [RED, GOLD, "#4E9A6A", "#6AA8D0"][k % 4]
        o.append(c.glow(bx, by + 6, 13, lt(col, 0.3), 0.6))
        o.append(f'<path d="{blob(bx, by + 6, 4.6, 7, k + 30, 0.08, 10)}" fill="{col}"/><circle cx="{F(bx - 1.4)}" cy="{F(by + 3)}" r="1.6" fill="#FFFFFF" opacity="0.85"/>')
    # exterior sill heaped with snow
    sl = jitter([(126, 494), (474, 494), (480, 512), (120, 512)], 8, 1)
    o.append(shape(c, sl, "#EFE6D6", ["#FFFFFF", "#D8CCBA"], 8, angle=0, n=30, iw=2, d="M " + " L ".join(f"{F(a)} {F(b)}" for a, b in sl) + " Z"))
    o.append(snow_lump(c, [(118, 496), (150, 472), (210, 478), (260, 466), (330, 474), (400, 468), (452, 476), (484, 496), (420, 502), (300, 500), (180, 502)], 9))
    o.append(holly(c, 150, 490, 0.8, -20, 13))
    # snowy shrubs in the corners with little lights
    for bx, sd in ((50, 1), (552, 2)):
        o.append(fir(c, bx, 620, 180, 170, 30 + sd, tiers=4, trunk=None, iw=1.4))
        for k in range(6):
            r2 = random.Random(sd * 10 + k)
            lx, ly = bx + r2.uniform(-60, 60), r2.uniform(530, 590)
            col = [GOLD_L, RED_L, "#9AD0E8"][k % 3]
            o.append(c.glow(lx, ly, 12, col, 0.6) + f'<circle cx="{F(lx)}" cy="{F(ly)}" r="3" fill="{col}"/>')
    o.append(snow_field(c, [(-20, 566), (120, 556), (300, 564), (480, 554), (620, 560)], 14, n=40))
    # falling snow
    o.append(spatter(15, 110, (0, 0, 600, 600), ["#FFFFFF"], r=(1.2, 3.4), op=(0.7, 1), avoid=[(150, 230, 460, 500), (70, 40, 530, 210)]))
    for x, y, r, rt in ((82, 300, 12, 5), (520, 330, 13, 20), (510, 440, 9, 12), (86, 430, 9, 0)):
        o.append(flake(x, y, r, "#FFFFFF", 2.4, rt))
    # lettering
    o.append(L(c, 300, 112, "home for", SERIF_IT, 88, CREAM, ["#FFFFFF", "#F2DCC0", "#E8CFA8"], max_w=360, shadow="#0E1628", seed=16, angle=-35))
    o.append(L(c, 300, 196, "CHRISTMAS", BEBAS, 92, GOLD_L, [GOLD, "#FFF0B8", GOLD_D], max_w=430, ls=10, shadow="#0E1628", seed=17, angle=-80))
    return finish(c, "".join(o), gop=0.7)


# ================================================================ NEW: hes-been-here (Santa's boots on the hearth)
def santa_boot(c, ox, oy, s, seed, flip=False, rot=0):
    """Black Santa boot with a white fur cuff, side view, toe to the left. (ox, oy) = sole under the heel."""
    T = lambda pts: tx(pts, 0, 0, 1, flip)
    sg = -1 if flip else 1
    o = [f'<g transform="translate({F(ox)} {F(oy)}) rotate({rot}) scale({s})">']
    o.append(cast(-24 * sg, 2, 96, 9, "#1A0A06", 0.45, seed))
    sole = T([(-104, -16), (46, -16), (50, -2), (-100, -4), (-108, -10)])
    o.append(shape(c, sole, "#2A1A14", ["#4A3024", "#120A08"], seed, angle=0, n=10, iw=1.4, inkc="#0A0604"))
    heel = T([(12, -6), (50, -6), (48, 4), (14, 4)])
    o.append(shape(c, heel, "#2A1A14", ["#4A3024"], seed + 1, n=4, iw=1.2, inkc="#0A0604", d="M " + " L ".join(f"{F(a)} {F(b)}" for a, b in heel) + " Z"))
    boot = T([(-36, -196), (40, -196), (44, -130), (48, -70), (56, -40), (52, -14), (40, -12), (-84, -12), (-104, -22), (-102, -44), (-84, -58),
              (-52, -68), (-40, -96), (-38, -150)])
    o.append(shape(c, boot, "#232024", ["#3A363C", "#121014", "#4A4650", "#2A2630"], seed + 2, angle=-90, n=110, length=(10, 30),
                   width=(2, 5), op=(0.3, 0.6), iw=2.2, inkc="#0A0808"))
    cl = c.id("bt")
    o.append(f'<clipPath id="{cl}"><path d="{smooth_closed(boot)}"/></clipPath><g clip-path="url(#{cl})">'
             # fire rim light on the back edge, cool sheen on the toe and shaft
             f'<path d="{blob(*T([(52, -90)])[0], 14, 110, seed, 0.1)}" fill="#F08A3A" opacity="0.55"/>'
             f'<path d="{blob(*T([(56, -40)])[0], 10, 30, seed + 1, 0.1)}" fill="#FFC070" opacity="0.6"/>'
             f'<path d="{blob(*T([(-70, -40)])[0], 22, 8, seed + 2, 0.1, rot=-20 * sg)}" fill="#C8CCE0" opacity="0.45"/>'
             f'<path d="{blob(*T([(-18, -140)])[0], 7, 44, seed + 3, 0.1)}" fill="#C8CCE0" opacity="0.35"/></g>')
    # creases at the ankle
    for cr in ([(-38, -96), (-10, -88), (20, -94)], [(-36, -110), (-6, -104), (30, -112)], [(-40, -80), (-20, -76)]):
        o.append(ink(smooth_open(T(cr)), "#0A0808", 2, seed, 1, 0.8) + ink(smooth_open(T([(x, y + 3) for x, y in cr])), "#5A5660", 1.2, seed, 1, 0.6))
    # fur cuff
    cuff = T([(-48, -226), (-20, -232), (20, -230), (52, -224), (56, -196), (54, -178), (20, -182), (-20, -180), (-50, -184), (-52, -204)])
    o.append(fluff(c, cuff, seed + 5, n=14, bumps=0.14, inkc="#7A6A70"))
    o.append(ink(smooth_open(T([(54, -220), (56, -196), (54, -180)])), "#FFB870", 2.4, seed, 1, 0.6))
    o.append("</g>")
    return "".join(o)


def bricks(c, box, seed, h=26, w=58, cols=("#9A4A36", "#8A3E2E", "#A8583E", "#7E3828", "#B0624A"), mortar="#5A2E22"):
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    o = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{mortar}"/>']
    for r, y in enumerate(range(int(y0), int(y1), h)):
        off = (w / 2) * (r % 2)
        x = x0 - off
        while x < x1:
            pts = jitter([(x + 2, y + 2), (x + w - 2, y + 2), (x + w - 2, y + h - 2), (x + 2, y + h - 2)], rnd.randint(0, 9999), 0.9)
            d = "M " + " L ".join(f"{F(a)} {F(b)}" for a, b in pts) + " Z"
            o.append(f'<path d="{d}" fill="{rnd.choice(cols)}"/>')
            if rnd.random() < 0.5:
                o.append(f'<path d="M {F(x + 5)} {F(y + 5)} L {F(x + w * rnd.uniform(0.4, 0.9))} {F(y + 5)}" stroke="#C87A5A" stroke-width="2" opacity="0.45"/>')
            x += w
    return "".join(o)


def hes_been_here():
    c = C("hbh")
    # wallpaper: deep green stripes
    o = [wash_bg(c, "#1F3D30", ["#24473A", "#183226", "#2A5040"], 3, angle=-90, n=200, length=(60, 160), width=(6, 14))]
    for x in range(-10, 620, 48):
        o.append(f'<path d="M {x} 0 L {x + 16} 0 L {x + 16} 240 L {x} 240 Z" fill="#2C5444" opacity="0.5"/>')
        o.append(f'<path d="M {x + 30} 0 L {x + 31.5} 0 L {x + 31.5} 240 L {x + 30} 240 Z" fill="{GOLD}" opacity="0.35"/>')
    o.append(c.oglow(300, 120, 300, 140, "#0E2018", 0.35))
    # brick surround with an arched firebox
    BY = 236
    br = bricks(c, (-10, BY, 610, 520), 3)
    arch = "M 150 500 L 150 330 Q 150 268 300 262 Q 450 268 450 330 L 450 500 Z"
    o.append(br)
    o.append(f'<path d="M -10 {BY} L 610 {BY} L 610 520 L -10 520 Z" fill="#000000" opacity="0.12"/>')
    # brick voussoir ring around the arch
    vs = []
    for k in range(15):
        a = math.radians(180 + k * 180 / 14)
        a2 = math.radians(180 + (k + 1) * 180 / 14)
        r1x, r1y, r2x, r2y = 150, 68, 178, 92
        cy_ = 330
        p = [(300 + r1x * math.cos(a), cy_ + r1y * math.sin(a)), (300 + r2x * math.cos(a), cy_ + r2y * math.sin(a)),
             (300 + r2x * math.cos(a2), cy_ + r2y * math.sin(a2)), (300 + r1x * math.cos(a2), cy_ + r1y * math.sin(a2))]
        vs.append(f'<path d="M {" L ".join(f"{F(px)} {F(py)}" for px, py in jitter(p, k, 0.8))} Z" fill="{["#A8583E", "#9A4A36", "#B0624A"][k % 3]}" stroke="#5A2E22" stroke-width="3"/>')
    o.append("".join(vs))
    # firebox: soot, embers, a low fire
    g = c.lg([(0, "#120A08"), (0.7, "#2A140C"), (1, "#5A2410")])
    o.append(f'<path d="{arch}" fill="url(#{g})"/>')
    o.append(strokes(c.id("fb"), arch, (150, 260, 450, 500), ["#2A1A14", "#0A0604", "#3A2018"], 4, n=60, angle=-90, length=(20, 60), width=(4, 10),
                     opacity=(0.3, 0.6)))
    o.append(c.oglow(300, 480, 170, 90, "#FF8A2A", 0.85))
    rnd = random.Random(5)
    for k in range(5):
        lx = 210 + k * 44
        o.append(shape(c, [(lx - 40, 486), (lx + 40, 478), (lx + 42, 492), (lx - 38, 498)], "#3A2014", ["#5A3020", "#1A0A06"], 6 + k, angle=-4, n=8, iw=1.2,
                       inkc="#0A0604"))
    for _ in range(40):
        ex, ey = rnd.uniform(180, 420), rnd.uniform(478, 500)
        o.append(f'<path d="{blob(ex, ey, rnd.uniform(3, 7), rnd.uniform(2, 4), rnd.randint(0, 999), 0.2, 8)}" fill="{rnd.choice(["#FF6A1A", "#FFB040", "#F8D070", "#C8341A"])}" opacity="{rnd.uniform(0.6, 1):.2f}"/>')
    for k, (fx, fh) in enumerate(((340, 52), (376, 84), (412, 64), (300, 40))):
        o.append(f'<path d="M {fx} {480 - fh} Q {fx + 18} {480 - fh * 0.5} {fx + 14} 482 L {fx - 14} 482 Q {fx - 18} {480 - fh * 0.5} {fx} {480 - fh} Z" fill="#F07A2A" opacity="0.9"/>'
                 f'<path d="M {fx} {480 - fh * 0.6} Q {fx + 9} {480 - fh * 0.3} {fx + 7} 482 L {fx - 7} 482 Q {fx - 9} {480 - fh * 0.3} {fx} {480 - fh * 0.6} Z" fill="#FFD27A"/>')
    o.append(ink(arch, "#3A1A10", 2.4, 3, 1, 0.8))
    # stone hearth
    hb = "M -20 506 L 620 506 L 620 620 L -20 620 Z"
    o.append(f'<path d="{hb}" fill="#A89888"/>')
    o.append(strokes(c.id("hb"), hb, (-20, 504, 620, 620), ["#BCAE9E", "#8C7C6E", "#C8BAAA", "#958676"], 7, n=150, angle=-2, length=(40, 110),
                     width=(2, 6), opacity=(0.3, 0.55), curve=0.05))
    for x in (110, 250, 390, 530):
        o.append(ink(f"M {x} 506 L {x - 6} 620", "#6A5A4E", 2, x, 1, 0.6))
    o.append(ink("M -20 506 L 620 506", "#E8D8C4", 2.6, 2, 1, 0.7))
    o.append(c.oglow(300, 520, 260, 70, "#FF9A3A", 0.5))
    # soot: scattered dust and sooty boot prints walking out of the fireplace
    o.append(spatter(9, 80, (150, 494, 450, 540), ["#2A2020", "#4A3E3A"], r=(0.8, 2.4), op=(0.3, 0.7)))
    for k, (px, py, a) in enumerate(((452, 532, 160), (498, 562, 154), (542, 594, 150))):
        pr = rot_pts([(-14, 0), (-10, -8), (10, -7), (16, 0), (10, 7), (-10, 8)], px, py, a)
        o.append(f'<path d="{smooth_closed(pr)}" fill="#2A2020" opacity="{0.5 - k * 0.1:.2f}"/>')
        hp_ = rot_pts([(24, 0)], px, py, a)[0]
        o.append(f'<path d="{blob(hp_[0], hp_[1], 7, 6, k, 0.1, 8, rot=a)}" fill="#2A2020" opacity="{0.5 - k * 0.1:.2f}"/>')
    # a jingle bell left behind and a candy cane leaning on the bricks
    bx, by = 408, 548
    o.append(cast(bx + 4, by + 14, 20, 4, "#1A0A06", 0.35, 3))
    o.append(shape(c, blob_pts(bx, by, 17, 16, 30, 0.03, 14), GOLD, [GOLD_L, GOLD_D, "#FFF0B8"], 30, angle=-60, n=16, iw=1.8))
    o.append(ink(f"M {bx - 10} {by + 4} Q {bx} {by + 8} {bx + 10} {by + 4}", "#5A3A10", 2.4, 31, 1, 0.9) + f'<circle cx="{bx}" cy="{by + 8}" r="2.6" fill="#3A2410"/>'
             f'<path d="{blob(bx - 6, by - 6, 4, 3, 32, 0.1)}" fill="#FFFFFF" opacity="0.8"/>')
    o.append(ink(f"M {bx - 4} {by - 16} q 4 -8 8 0", GOLD_D, 2.4, 33, 1, 0.9))
    cc = "M 528 506 L 532 380 Q 534 352 512 352 Q 494 352 494 372"
    o.append(ink(cc, "#8A1A20", 15, 34, 1, 0.5).replace('transform="', 'transform="translate(5 3) '))
    o.append(ink(cc, "#FFFFFF", 13, 35, 1, 1))
    o.append(f'<path d="{cc}" fill="none" stroke="{RED}" stroke-width="13" stroke-dasharray="9 11" stroke-linecap="butt"/>')
    o.append(ink(cc, INK, 1.4, 36, 1, 0.5))
    # the boots
    o.append(santa_boot(c, 300, 526, 0.9, 40, rot=3))
    o.append(santa_boot(c, 236, 546, 0.95, 41, rot=-2))
    # lettering
    o.append(L(c, 300, 112, "he's been", SERIF_IT, 90, GOLD_L, [GOLD, "#FFF0B8", GOLD_D], max_w=400, shadow="#0E2018", seed=50, angle=-35))
    o.append(L(c, 300, 212, "HERE!", BEBAS, 112, CREAM, ["#FFFFFF", "#F2DCC0", "#E8CFA8"], max_w=300, ls=12, shadow=CRAN, seed=51, angle=-80,
               sdx=0.035, sdy=0.04))
    for sx_ in (-1, 1):
        o.append(glint(300 + sx_ * 162, 176, 10, GOLD_L) + glint(300 + sx_ * 188, 150, 5, GOLD_L))
    return finish(c, "".join(o), gop=0.8)


# ================================================================ NEW: silent-night (a stable under the star, animals in the snow)
def donkey(c, x, base, s, seed, flip=False):
    """Small storybook donkey facing left. (x, base) = hooves."""
    sg = -1 if flip else 1
    o = [f'<g transform="translate({F(x)} {F(base)}) scale({F(s * sg)} {F(s)})">']
    hide, hide_d, belly = "#8E8494", "#5E5664", "#D8D2DA"
    o.append(cast(0, 0, 50, 5, SHADE_D, 0.5, seed))
    for lx, d_ in ((-26, 0.2), (30, 0.2)):
        o.append(shape(c, limb([(lx + 6, -40), (lx + 4, -20), (lx + 6, 0)], 9, 6), dk(hide, d_), [hide_d], seed + lx, angle=-90, n=4, iw=1.2, inkc=INK_N2))
    tail = [(40, -60), (50, -50), (52, -26), (46, -22), (44, -46)]
    o.append(shape(c, tail, hide_d, ["#3E3844"], seed + 1, n=4, iw=1.2, inkc=INK_N2))
    body = [(-36, -66), (-10, -72), (24, -72), (44, -62), (46, -44), (34, -32), (0, -30), (-30, -32), (-42, -46)]
    o.append(shape(c, body, hide, [hide_d, "#A8A0AE", "#7A7280"], seed + 2, angle=-10, n=40, length=(6, 16), width=(1.5, 3), iw=1.8, inkc=INK_N2))
    cl = c.id("dk")
    o.append(f'<clipPath id="{cl}"><path d="{smooth_closed(body)}"/></clipPath><g clip-path="url(#{cl})"><path d="{blob(4, -32, 40, 9, seed, 0.1)}" fill="{belly}"/></g>')
    for lx in (-32, 22):
        o.append(shape(c, limb([(lx + 4, -40), (lx, -20), (lx + 2, 0)], 10, 7), hide, [hide_d, "#A8A0AE"], seed + 3 + lx, angle=-90, n=5, iw=1.3, inkc=INK_N2))
        o.append(f'<path d="{blob(lx + 2, -1, 5, 3, seed, 0.1, 8)}" fill="#2A2228"/>')
    neck = [(-40, -50), (-34, -66), (-48, -94), (-60, -98), (-62, -84), (-50, -56)]
    o.append(shape(c, neck, hide, [hide_d, "#A8A0AE"], seed + 4, angle=-60, n=12, iw=1.6, inkc=INK_N2))
    o.append(ink(smooth_open([(-36, -66), (-42, -84), (-52, -100)]), "#3E3844", 4, seed, 1, 0.9))
    head = [(-52, -104), (-64, -104), (-84, -86), (-88, -76), (-78, -72), (-60, -82), (-50, -92)]
    o.append(shape(c, head, hide, [hide_d, "#A8A0AE"], seed + 5, angle=-150, n=12, iw=1.6, inkc=INK_N2))
    o.append(f'<path d="{blob(-82, -78, 8, 6, seed, 0.1, 10)}" fill="{belly}"/>')
    o.append(f'<circle cx="-66" cy="-92" r="2.2" fill="#1A1418"/><circle cx="-85" cy="-79" r="1.3" fill="#3A3238"/>')
    for ex, a in ((-54, -16), (-60, -36)):
        ear = rot_pts([(0, 0), (8, -4), (24, -1), (8, 4)], ex, -102, -90 + a)
        o.append(shape(c, ear, hide, [hide_d], seed + 6 + ex, n=4, iw=1.3, inkc=INK_N2))
    o.append("</g>")
    return "".join(o)


def sheep(c, x, base, s, seed, flip=False):
    """Woolly sheep facing right. (x, base) = hooves."""
    sg = -1 if flip else 1
    o = [f'<g transform="translate({F(x)} {F(base)}) scale({F(s * sg)} {F(s)})">']
    o.append(cast(0, 0, 36, 4, SHADE_D, 0.5, seed))
    for lx in (-18, -8, 10, 20):
        o.append(ink(f"M {lx} -16 L {lx + 1} 0", "#2E2428", 5, seed + lx, 1, 1))
    body = blob_pts(0, -30, 32, 20, seed, 0.05, 12)
    o.append(fluff(c, body, seed + 1, n=10, bumps=0.22, inkc="#6A6080", iw=1.3))
    o.append(shape(c, blob_pts(30, -38, 11, 9, seed + 2, 0.06, 10, rot=20), "#3A2E2A", ["#5A4A44"], seed + 2, n=6, iw=1.2, inkc="#1A1210"))
    o.append(shape(c, [(24, -46), (16, -50), (12, -44), (20, -42)], "#3A2E2A", ["#5A4A44"], seed + 3, n=3, iw=1, inkc="#1A1210"))
    o.append(fluff(c, blob_pts(24, -46, 9, 6, seed + 4, 0.1, 8), seed + 4, n=3, bumps=0.2, inkc=None, curls=False))
    o.append(f'<circle cx="33" cy="-40" r="1.6" fill="#FFFFFF" opacity="0.8"/>')
    o.append("</g>")
    return "".join(o)


INK_N2 = "#2A2236"


def silent_night():
    c = C("sin")
    sky = c.lg([(0, "#121A36"), (0.55, "#26346A"), (1, "#4A5890")])
    o = [f'<rect width="600" height="600" fill="url(#{sky})"/>',
         strokes(c.id("sk"), "M -20 -20 L 620 -20 L 620 420 L -20 420 Z", (-40, -40, 640, 420), ["#2E3E78", "#1A2450", "#3A4A86", "#4E5C98"], 3,
                 n=220, angle=-6, length=(50, 140), width=(5, 12), opacity=(0.12, 0.3), curve=0.1)]
    rnd = random.Random(4)
    for _ in range(70):
        x, y = rnd.uniform(0, 600), rnd.uniform(0, 330)
        if 110 < x < 490 and 130 < y < 230:
            continue
        if rnd.random() < 0.18:
            o.append(glint(x, y, rnd.uniform(3, 6), "#FFF6D8", rnd.uniform(0.6, 1)))
        else:
            o.append(f'<circle cx="{F(x)}" cy="{F(y)}" r="{rnd.uniform(0.7, 1.8):.1f}" fill="#FFF6E0" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    # the star: glow, long rays, a soft beam falling to the stable
    sx, sy = 300, 92
    o.append(c.glow(sx, sy, 170, "#F6D683", 0.45))
    o.append(f'<path d="M {sx - 4} {sy + 10} L {sx - 92} 330 L {sx + 92} 330 L {sx + 4} {sy + 10} Z" fill="#FFE8A8" opacity="0.1"/>')
    o.append(f'<path d="M {sx - 2} {sy + 10} L {sx - 46} 330 L {sx + 46} 330 L {sx + 2} {sy + 10} Z" fill="#FFE8A8" opacity="0.1"/>')
    for a, Lr, w in ((90, 120, 5), (-90, 48, 4), (0, 120, 4), (180, 120, 4), (45, 46, 2.6), (135, 46, 2.6), (-45, 46, 2.6), (-135, 46, 2.6)):
        ex, ey = sx + Lr * math.cos(math.radians(a)), sy + Lr * math.sin(math.radians(a))
        nx, ny = -math.sin(math.radians(a)) * w, math.cos(math.radians(a)) * w
        o.append(f'<path d="M {F(sx + nx)} {F(sy + ny)} L {F(ex)} {F(ey)} L {F(sx - nx)} {F(sy - ny)} Z" fill="#FFF0C0" opacity="0.85"/>')
    o.append(glint(sx, sy, 34, "#FFF6D8") + glint(sx, sy, 18, "#FFFFFF"))
    # distant snowy hills
    o.append(snow_field(c, [(-20, 340), (100, 318), (220, 334), (380, 314), (500, 330), (620, 316)], 5, base="#B8BEE0", n=50))
    for x in range(-10, 620, 22):
        h = rnd.uniform(14, 30)
        yb = 334 - 12 * math.sin(x / 90) + rnd.uniform(-3, 3)
        o.append(fir(c, x, yb, h, h * 0.55, rnd.randint(0, 999), cols=("#4A5888", "#3A4878", "#5A68A0", "#44528A"), tiers=3, snow=False, inkc=None, trunk=None))
    o.append(snow_field(c, [(-20, 372), (140, 358), (300, 366), (460, 354), (620, 366)], 6, base="#D4D6F0", n=60))
    # ---- the stable
    o.append(c.oglow(300, 380, 170, 90, "#FFC86A", 0.35))
    wall = jitter([(222, 314), (378, 314), (380, 420), (220, 420)], 7, 1.2)
    wd = "M " + " L ".join(f"{F(a)} {F(b)}" for a, b in wall) + " Z"
    o.append(wash(wd, "#5A3E34", 7, 2, 0.8, 0.5))
    o.append(strokes(c.id("pl"), wd, (218, 310, 382, 422), ["#6E4E40", "#3E2A24", "#7A6A8A", "#4A3A3A"], 8, n=60, angle=-90, length=(20, 60),
                     width=(2, 5), opacity=(0.3, 0.6)))
    o.append(f'<g stroke="#2A1C18" stroke-width="1.6" opacity="0.7">' + "".join(f'<path d="M {x} 316 L {x + 0.5} 420"/>' for x in range(236, 378, 16)) + "</g>")
    # open doorway with warm light, hay, manger and a hanging lantern
    door = "M 256 420 L 256 350 Q 256 336 270 336 L 330 336 Q 344 336 344 350 L 344 420 Z"
    g = c.lg([(0, "#F6B44A"), (0.6, "#E88A2E"), (1, "#C8641E")])
    o.append(f'<path d="{door}" fill="url(#{g})"/>')
    dc = c.id("dr")
    o.append(f'<clipPath id="{dc}"><path d="{door}"/></clipPath><g clip-path="url(#{dc})">'
             + c.glow(300, 360, 60, "#FFF2C4", 0.85)
             + strokes(c.id("hy"), door, (250, 396, 350, 422), ["#F2D07A", "#C9933A", "#FFE8A8"], 9, n=70, angle=-20, length=(8, 18), width=(0.8, 1.6), opacity=(0.6, 1))
             + f'<path d="M 270 398 L 330 398 L 324 414 L 276 414 Z" fill="#6A3E22"/>'
             + strokes(c.id("mg"), "M 268 388 Q 300 380 332 388 L 330 400 L 270 400 Z", (266, 378, 334, 402), ["#F6DA8A", "#E2B65A"], 10, n=30, angle=-80,
                       length=(6, 14), width=(0.8, 1.4), opacity=(0.8, 1))
             + "</g>")
    o.append(ink(door, "#2A1C18", 2.4, 4, 1, 0.9))
    o.append(ink("M 300 336 L 300 346", "#2A1C18", 1.4, 5, 1, 1) + c.glow(300, 354, 16, "#FFFFFF", 0.9) + f'<path d="{blob(300, 354, 4, 5.5, 3, 0.1, 8)}" fill="#FFF6D8"/>')
    for sx_ in (-1, 1):
        o.append(c.oglow(300 + sx_ * 46, 368, 10, 12, "#FFC86A", 0.6) +
                 f'<path d="M {300 + sx_ * 46 - 7} 360 L {300 + sx_ * 46 + 7} 360 L {300 + sx_ * 46 + 7} 376 L {300 + sx_ * 46 - 7} 376 Z" fill="#FFD27A" stroke="#2A1C18" stroke-width="1.6"/>')
    o.append(ink(wd, INK_N2, 2, 6, 1, 0.8))
    # roof with thick snow
    roof = jitter([(198, 322), (300, 254), (402, 322), (392, 330), (300, 268), (208, 330)], 9, 1.2)
    rd = "M " + " L ".join(f"{F(a)} {F(b)}" for a, b in roof) + " Z"
    o.append(shape(c, roof, "#4A3028", ["#6E4A3A", "#2E1E18"], 10, angle=-30, n=30, iw=1.8, inkc=INK_N2, d=rd))
    o.append(snow_lump(c, [(192, 324), (230, 290), (270, 262), (300, 246), (330, 262), (370, 290), (408, 324), (396, 330), (360, 312), (300, 268),
                           (240, 312), (204, 330)], 11, inkc="#7A80B8"))
    o.append(snow_lump(c, drape((262, 330), (338, 330), 7, 12, 2, up=3), 12, iw=0.8))
    # fence with snow
    for px in (78, 128, 178):
        o.append(shape(c, [(px - 5, 444), (px - 4, 400), (px + 4, 398), (px + 5, 444)], "#5A3E34", ["#6E4E40", "#3E2A24"], px, angle=-90, n=6, iw=1.4,
                       inkc=INK_N2, d=f"M {px - 5} 444 L {px - 4} 400 L {px + 4} 398 L {px + 5} 444 Z"))
        o.append(snow_lump(c, blob_pts(px, 398, 8, 4, px, 0.1, 8), px, iw=0.6))
    for ry in (410, 428):
        o.append(ink(f"M 66 {ry} L 196 {ry - 4}", "#4A3028", 5, ry, 1, 1))
        o.append(snow_lump(c, drape((70, ry - 2), (194, ry - 6), 2.5, ry, 1, up=2), ry, iw=0.5))
    # foreground snow
    o.append(snow_field(c, [(-20, 424), (120, 414), (300, 420), (470, 410), (620, 418)], 13, base="#E6E6F6",
                        shade_box=(-20, 470, 620, 620), inkc="#6E74B0"))
    o.append(c.oglow(300, 436, 140, 26, "#FFC86A", 0.45))
    # footprints winding up to the stable door
    for k in range(9):
        t = k / 8
        px = 330 + 40 * math.sin(t * 3.2) - 30 * t
        py = 520 - 84 * t
        side = 7 if k % 2 else -7
        o.append(f'<path d="{blob(px + side * (1 - t * 0.5), py, 5 - t * 2, 3.2 - t * 1.2, k, 0.1, 8)}" fill="{SHADE_D}" opacity="0.55"/>')
    # animals
    o.append(donkey(c, 446, 448, 0.98, 20))
    o.append(sheep(c, 176, 470, 1.05, 21))
    o.append(sheep(c, 112, 484, 0.8, 22))
    o.append(sheep(c, 252, 478, 0.9, 23, flip=False))
    # little blue firs at the edges
    for bx, sd, h in ((560, 31, 120), (38, 32, 100)):
        o.append(fir(c, bx, 470, h, h * 0.7, sd, cols=("#2E4A5A", "#1E3446", "#4A6878", "#36525E"), tiers=4, iw=1.2, inkc=INK_N2))
    o.append(spatter(24, 50, (0, 430, 600, 600), ["#FFFFFF"], r=(0.8, 2.2), op=(0.6, 1)))
    # lettering
    o.append(L(c, 300, 212, "silent night", SERIF_IT, 96, CREAM, ["#FFFFFF", "#F6E6C2", "#E8D6A8"], max_w=470, shadow="#0E1428", seed=40, angle=-35))
    lw = measure("CHRISTMAS EVE", CINZEL, 22, 4)
    o.append(f'<text x="301.5" y="528" text-anchor="middle" {CINZEL} font-size="22" letter-spacing="4" fill="#26305E">CHRISTMAS EVE</text>')
    for sx_ in (-1, 1):
        o.append(ink(f"M {F(300 + sx_ * (lw / 2 + 10))} 521 L {F(300 + sx_ * (lw / 2 + 44))} 521", "#26305E", 1.8, 41 + sx_, 1, 0.8))
        o.append(glint(300 + sx_ * (lw / 2 + 54), 521, 6, "#26305E"))
    return finish(c, "".join(o), gop=0.7)


# ================================================================ NEW: chill-out (polar bear in a scarf on an ice floe)
def chill_out():
    c = C("cho")
    sky = c.lg([(0, "#16234A"), (0.45, "#2C4C7E"), (0.8, "#6E92B8"), (1, "#B8CCE0")])
    o = [f'<rect width="600" height="600" fill="url(#{sky})"/>',
         strokes(c.id("sk"), "M -20 -20 L 620 -20 L 620 420 L -20 420 Z", (-40, -40, 640, 420), ["#2A4476", "#3E5E92", "#1E2E5A", "#7A9AC0"], 3,
                 n=220, angle=-8, length=(50, 140), width=(5, 12), opacity=(0.1, 0.28), curve=0.1)]
    rnd = random.Random(5)
    for _ in range(60):
        x, y = rnd.uniform(0, 600), rnd.uniform(0, 300)
        o.append(f'<circle cx="{F(x)}" cy="{F(y)}" r="{rnd.uniform(0.7, 1.8):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.3, 0.85):.2f}"/>')
    # aurora ribbons: soft bands filled with vertical brushwork
    for k, (pts, cols) in enumerate((
            ([(-20, 250), (120, 196), (260, 232), (420, 180), (620, 214)], ["#7FE0B0", "#5AC8A0", "#A8F0C8"]),
            ([(-20, 300), (140, 262), (300, 288), (460, 240), (620, 262)], ["#5AC0C8", "#7FD8D0", "#8A7AD8"]))):
        top = [(x, y - 70) for x, y in pts]
        d = smooth_open(top) + " " + smooth_open(pts[::-1]).replace("M", "L", 1) + " Z"
        ag = c.lg([(0, cols[0], 0), (0.55, cols[0], 0.2), (0.85, cols[1], 0.38), (1, cols[1], 0)])
        o.append(f'<path d="{d}" fill="url(#{ag})"/>')
        for j in range(0, 5):
            px, py = pts[j]
            o.append(c.oglow(px, py - 22, 110, 34, cols[2], 0.28))
        o.append(strokes(c.id("au"), d, (-20, 100, 620, 310), cols, 6 + k, n=150, angle=-90, length=(40, 90), width=(1.5, 4), opacity=(0.1, 0.32),
                         curve=0.03))
    # sea, distant bergs
    sea = "M -20 404 L 620 404 L 620 620 L -20 620 Z"
    g = c.lg([(0, "#3E6A90"), (1, "#16304E")])
    o.append(f'<path d="{sea}" fill="url(#{g})"/>')
    o.append(strokes(c.id("se"), sea, (-20, 404, 620, 620), ["#5A8AB0", "#1E3A5A", "#7FD0C0", "#2A4E74"], 7, n=170, angle=0, length=(30, 100),
                     width=(1.5, 4), opacity=(0.25, 0.55), curve=0.04))
    for bx, bw, bh, sd in ((60, 70, 30, 1), (520, 90, 40, 2), (150, 40, 16, 3)):
        bp = [(bx - bw / 2, 406), (bx - bw * 0.3, 406 - bh * 0.7), (bx - bw * 0.05, 406 - bh), (bx + bw * 0.2, 406 - bh * 0.8), (bx + bw / 2, 406)]
        o.append(shape(c, bp, "#DCE6F2", ["#FFFFFF", "#B4C4DC"], sd, angle=-80, n=10, iw=1.2, inkc="#4A6488"))
        o.append(f'<path d="M {bx - bw / 2} 408 L {bx + bw / 2} 408 L {bx + bw * 0.3} {410 + bh * 0.4} L {bx - bw * 0.3} {410 + bh * 0.4} Z" fill="#DCE6F2" opacity="0.25"/>')
    # ice floe
    floe_top = [(96, 512), (130, 488), (210, 478), (300, 474), (400, 478), (486, 490), (512, 512), (470, 536), (300, 546), (140, 538)]
    o.append(f'<path d="{smooth_closed([(x, y + 24) for x, y in floe_top])}" fill="#0E2238" opacity="0.4" transform="translate(6 8)"/>')
    side = smooth_closed([(x, y + (22 if y > 500 else 0)) for x, y in floe_top])
    o.append(f'<path d="{side}" fill="#7FA8CC"/>' + strokes(c.id("fs"), side, (90, 470, 520, 572), ["#9AC0DC", "#5A86AE", "#B8D4E8"], 8, n=40, angle=-85,
                                                             length=(8, 20), width=(2, 4), opacity=(0.3, 0.6)) + ink(side, "#2E4A6E", 1.8, 8, 1, 0.6))
    ft = smooth_closed(floe_top)
    o.append(f'<path d="{ft}" fill="{SNOW}"/>' + strokes(c.id("ft"), ft, (90, 470, 520, 550), [SHADE_L, "#FFFFFF", ICE_L, SHADE], 9, n=80, angle=-3,
                                                         length=(20, 60), width=(2, 5), opacity=(0.25, 0.55)) + ink(ft, "#6A7AA8", 1.6, 9, 1, 0.5))
    for k in range(4):
        o.append(ink(f"M {60 + k * 140} {566 + (k % 2) * 14} q 30 -5 60 0", "#9AC8DC", 2, k, 1, 0.6))
    # ---- the bear
    fur, fur_sh = "#F7F4EE", SHADE
    o.append(cast(300, 512, 130, 12, SHADE_D, 0.45, 10))
    body = blob_pts(300, 424, 98, 94, 11, 0.03, 20)
    o.append(shape(c, body, fur, ["#FFFFFF", SHADE_L, "#E8E4EE", fur_sh], 11, angle=-70, n=150, length=(8, 20), width=(2, 4.5), op=(0.25, 0.55),
                   iw=2.4, inkc="#4A4A6A"))
    cl = c.id("by")
    o.append(f'<clipPath id="{cl}"><path d="{smooth_closed(body)}"/></clipPath><g clip-path="url(#{cl})">'
             f'<path d="{blob(370, 450, 60, 100, 12, 0.1)}" fill="{SHADE}" opacity="0.4"/>'
             f'<path d="{blob(300, 380, 70, 30, 13, 0.1)}" fill="{SHADE_D}" opacity="0.25"/></g>')
    o.append(ink(smooth_open([(210, 452), (206, 410), (220, 368)]), "#C8F4E0", 2, 3, 1, 0.5))
    # hind feet with pads facing us
    for sx_ in (-1, 1):
        fx = 300 + sx_ * 66
        o.append(shape(c, blob_pts(fx, 506, 38, 26, 14 + sx_, 0.05, 14), fur, ["#FFFFFF", SHADE_L, fur_sh], 14 + sx_, n=24, iw=2.2, inkc="#4A4A6A"))
        o.append(f'<path d="{blob(fx, 512, 16, 11, 15 + sx_, 0.08, 12)}" fill="#4A4A5E"/>')
        for k in (-1, 0, 1):
            o.append(f'<path d="{blob(fx + k * 13, 494 - (0 if k else 3), 5.5, 5, 16 + k, 0.08, 8)}" fill="#4A4A5E"/>')
    # front legs hugging a red mug
    for sx_ in (-1, 1):
        arm = limb([(300 + sx_ * 66, 372), (300 + sx_ * 58, 414), (300 + sx_ * 34, 446)], 46, 36)
        o.append(shape(c, arm, fur, ["#FFFFFF", SHADE_L, fur_sh], 20 + sx_, angle=-60 * sx_ - 90, n=40, iw=2.2, inkc="#4A4A6A"))
    mx, my = 300, 438
    o.append(c.glow(mx, my - 40, 50, "#FFFFFF", 0.3))
    mug = [(mx - 26, my - 30), (mx + 26, my - 30), (mx + 24, my + 18), (mx - 24, my + 18)]
    md = f"M {mx - 26} {my - 30} L {mx + 26} {my - 30} Q {mx + 26} {my + 20} {mx + 20} {my + 20} L {mx - 20} {my + 20} Q {mx - 26} {my + 20} {mx - 26} {my - 30} Z"
    o.append(shape(c, mug, RED, ["#E2524A", CRAN, "#F07058"], 22, angle=-90, n=20, iw=2, d=md))
    o.append(f'<ellipse cx="{mx}" cy="{my - 30}" rx="26" ry="6" fill="#6A3420"/><ellipse cx="{mx}" cy="{my - 30}" rx="26" ry="6" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    o.append(flake(mx, my - 4, 11, CREAM, 2.2, 0))
    for k, sxs in enumerate((-10, 6)):
        o.append(ink(f"M {mx + sxs} {my - 40} q -10 -14 0 -26 q 10 -12 0 -26", "#FFFFFF", 3.4 - k, 23 + k, 1, 0.7))
    for sx_ in (-1, 1):
        o.append(shape(c, blob_pts(mx + sx_ * 30, my - 2, 18, 15, 24 + sx_, 0.06, 12), fur, ["#FFFFFF", SHADE_L], 24 + sx_, n=10, iw=2, inkc="#4A4A6A"))
    # scarf
    sc = [(232, 354), (300, 370), (368, 354), (372, 374), (300, 392), (228, 374)]
    tail = [(250, 376), (276, 382), (270, 452), (244, 456)]
    for pts_, sd in ((tail, 25), (sc, 26)):
        d = smooth_closed(pts_)
        o.append(wash(d, RED, sd, 2, 0.8, 0.5))
        cl2 = c.id("sc")
        if pts_ is sc:
            pat = "".join(f'<rect x="{x}" y="340" width="10" height="60" fill="{CREAM}"/>' for x in range(236, 372, 26))
        else:
            pat = "".join(f'<rect x="230" y="{y}" width="60" height="9" fill="{CREAM}"/>' for y in range(394, 460, 20))
        o.append(f'<clipPath id="{cl2}"><path d="{d}"/></clipPath><g clip-path="url(#{cl2})">{pat}</g>')
        o.append(strokes(c.id("ss"), d, bbox(pts_), ["#E2524A", CRAN, "#FFFFFF"], sd, n=40, angle=-80 if pts_ is tail else -8, length=(8, 20),
                         width=(1.5, 3), opacity=(0.2, 0.45)))
        o.append(ink(d, INK, 2, sd, 1, 0.7))
    o.append(f'<g stroke="{RED}" stroke-width="3.6" stroke-linecap="round">' + "".join(f'<path d="M {246 + k * 5.5} {456 - k * 0.8:.1f} l -1 12"/>' for k in range(5)) + "</g>")
    # head
    for sx_ in (-1, 1):
        o.append(shape(c, blob_pts(300 + sx_ * 50, 262, 18, 17, 27 + sx_, 0.05, 12), fur, ["#FFFFFF", fur_sh], 27 + sx_, n=10, iw=2.2, inkc="#4A4A6A"))
        o.append(f'<path d="{blob(300 + sx_ * 50, 264, 9, 8, 28 + sx_, 0.08, 10)}" fill="#C8C2D6"/>')
    head = blob_pts(300, 312, 70, 60, 29, 0.03, 20)
    o.append(shape(c, head, fur, ["#FFFFFF", SHADE_L, "#E8E4EE", fur_sh], 29, angle=-40, n=90, length=(6, 16), width=(1.8, 4), iw=2.4, inkc="#4A4A6A"))
    cl3 = c.id("hd")
    o.append(f'<clipPath id="{cl3}"><path d="{smooth_closed(head)}"/></clipPath><g clip-path="url(#{cl3})"><path d="{blob(352, 330, 40, 54, 30, 0.1)}" fill="{SHADE}" opacity="0.35"/></g>')
    o.append(ink(smooth_open([(238, 330), (234, 300), (248, 272)]), "#C8F4E0", 2, 4, 1, 0.5))
    o.append(shape(c, blob_pts(300, 336, 32, 23, 31, 0.05, 14), "#FBF8F2", ["#FFFFFF", SHADE_L], 31, n=14, iw=1.6, inkc="#6A6A8A"))
    o.append(f'<path d="M 286 320 Q 300 314 314 320 Q 312 332 300 336 Q 288 332 286 320 Z" fill="#2A2630"/><path d="M 292 320 q 5 -2 9 0" stroke="#8A8494" stroke-width="2" fill="none" stroke-linecap="round"/>')
    o.append(ink("M 300 336 L 300 344 M 288 346 Q 294 352 300 344 Q 306 352 312 346", "#2A2630", 2, 32, 1, 0.9))
    for sx_ in (-1, 1):
        ex = 300 + sx_ * 30
        o.append(ink(f"M {ex - 10} 304 Q {ex} 294 {ex + 10} 304", "#2A2630", 3.4, 33 + sx_, 1, 0.95))
        o.append(f'<path d="{blob(300 + sx_ * 46, 326, 12, 8, 34 + sx_, 0.1)}" fill="{PINK}" opacity="0.6"/>')
    # snowfall and sparkles
    o.append(spatter(35, 70, (0, 0, 600, 600), ["#FFFFFF"], r=(1.2, 3.2), op=(0.6, 1), avoid=[(200, 240, 400, 520), (80, 40, 520, 240)]))
    for x, y, r, rt in ((84, 330, 12, 5), (520, 340, 12, 20), (110, 440, 8, 12), (494, 446, 9, 0)):
        o.append(flake(x, y, r, "#FFFFFF", 2.4, rt))
    # lettering
    o.append(L(c, 300, 150, "chill", SERIF_IT, 132, "#FFFFFF", ["#FFFFFF", ICE_L, "#D8E8F0"], max_w=330, shadow="#16234A", seed=36, angle=-35,
               sdx=0.025, sdy=0.04))
    o.append(L(c, 300, 230, "OUT", BEBAS, 100, "#F07A6A", ["#E2524A", "#F8A090", RED], max_w=220, ls=16, shadow="#16234A", seed=37, angle=-80))
    for sx_ in (-1, 1):
        o.append(ink(f"M {300 + sx_ * 76} 192 L {300 + sx_ * 126} 192", "#FFFFFF", 2.4, 38 + sx_, 1, 0.8))
    return finish(c, "".join(o), gop=0.7)


# ================================================================ NEW: noel (poinsettia wreath, Rifle-Paper style)
def noel():
    c = C("noe")
    o = [paper(c.id("pp"), PAPER, FLECK, 51)]
    cx, cy, R = 300, 306, 190
    bd = blob(cx, cy, 150, 150, 3, 0.08, 22)
    o.append(wash(bd, "#F6E2C6", 4, 3, 3, 0.4))
    o.append(clip_strokes(c, bd, (140, 150, 460, 460), ["#F2D8B4", "#FBEEDC", "#EBCFA8"], 5, n=80, angle=-20, length=(30, 80), width=(4, 10),
                          op=(0.15, 0.35)))
    # ring of fir: dark underpainting then needles on three rings
    o.append(f'<path d="{blob(cx, cy, R + 22, R + 22, 6, 0.02, 30)} {blob(cx, cy, R - 22, R - 22, 7, 0.02, 30)}" fill="{GREEN_D}" fill-rule="evenodd" opacity="0.85"/>')
    for k, rr in enumerate((R - 16, R + 16, R, R - 4, R + 6)):
        o.append(needles(c, ring_pts(cx, cy, rr, k * 13, 360 + k * 13, 60, 0.015, 8 + k), 20 + k, length=(14, 28), density=0.5, w=2.6))
    # eucalyptus sprigs
    rnd = random.Random(9)
    for a in (-160, -100, -20, 40, 110, 160, 200):
        bx, by = cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))
        stem = [(bx, by)]
        for j in range(1, 4):
            ta = math.radians(a + 90 + 0)
            stem.append((bx + 18 * j * math.cos(ta) + rnd.uniform(-3, 3), by + 18 * j * math.sin(ta) + rnd.uniform(-3, 3)))
        o.append(ink(smooth_open(stem), "#6A7A60", 2, a, 1, 0.9))
        for j, (sxp, syp) in enumerate(stem[1:]):
            o.append(f'<path d="{blob(sxp, syp, 9, 8, a + j, 0.08, 10)}" fill="{SAGE}"/><path d="{blob(sxp - 2, syp - 2, 4, 3, a + j, 0.1, 8)}" fill="#B8CCB0" opacity="0.8"/>'
                     + ink(blob(sxp, syp, 9, 8, a + j, 0.08, 10), "#4A6050", 1.2, a + j, 1, 0.6))
    # cones, holly, berries, snowberries
    for a in (-60, 70, 150):
        px, py = cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))
        o.append(pinecone(c, px, py, 0.62, a + 70, a + 400))
    for a in (-120, 10, 120):
        px, py = cx + (R + 4) * math.cos(math.radians(a)), cy + (R + 4) * math.sin(math.radians(a))
        o.append(holly(c, px, py, 0.8, a, a + 500))
    for a in (-140, -40, 30, 95, 175, 220):
        px, py = cx + (R - 6) * math.cos(math.radians(a)), cy + (R - 6) * math.sin(math.radians(a))
        for j in range(4):
            o.append(f'<path d="{blob(px + rnd.uniform(-9, 9), py + rnd.uniform(-9, 9), 5, 5, a + j, 0.08, 8)}" fill="#FBF8F2" stroke="#9A98B8" stroke-width="1"/>')
    # poinsettias
    o.append(poinsettia(c, cx - 4, cy + R - 4, 64, 8, 60))
    o.append(poinsettia(c, cx - 120, cy + R * 0.66, 42, -20, 70))
    o.append(poinsettia(c, cx + 128, cy + R * 0.62, 46, 20, 80))
    o.append(poinsettia(c, cx - R * 0.74, cy - R * 0.66, 44, 40, 90))
    # velvet bow at the top
    bx, by = cx + 40, cy - R - 2
    for sx_ in (-1, 1):
        tl = [(bx, by + 4), (bx + sx_ * 14, by + 40), (bx + sx_ * 28, by + 66), (bx + sx_ * 16, by + 70), (bx + sx_ * 4, by + 34)]
        o.append(shape(c, tl, CRAN, [RED, CRAN_D], 100 + sx_, n=12, iw=1.8))
    for sx_ in (-1, 1):
        lp = [(bx, by), (bx + sx_ * 22, by - 30), (bx + sx_ * 48, by - 34), (bx + sx_ * 56, by - 14), (bx + sx_ * 42, by + 6), (bx + sx_ * 18, by + 8)]
        o.append(shape(c, lp, CRAN, [RED, CRAN_D, "#C8404A"], 104 + sx_, angle=-20 if sx_ > 0 else -160, n=26, iw=2))
        o.append(f'<path d="{smooth_closed([(bx + sx_ * 10, by - 4), (bx + sx_ * 28, by - 22), (bx + sx_ * 42, by - 20), (bx + sx_ * 34, by - 6)])}" fill="{CRAN_D}" opacity="0.5"/>')
    o.append(shape(c, blob_pts(bx, by - 2, 11, 10, 108, 0.08, 10), CRAN_D, [CRAN], 108, n=6, iw=1.8))
    # gold sparkles around
    o.append(spatter(114, 70, (40, 40, 560, 560), [GOLD, GOLD_L, RED], r=(1, 2.4), op=(0.4, 0.8), avoid=[(80, 80, 520, 530)]))
    for a, rr, sz in ((-80, R + 56, 9), (-30, R + 50, 6), (200, R + 48, 7), (60, R + 52, 6), (-170, R + 40, 5)):
        o.append(glint(cx + rr * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a)), sz, GOLD))
    # lettering
    o.append(c.glow(cx + 46, cy - 92, 30, GOLD_L, 0.6) + pstar(c, cx + 46, cy - 92, 14, GOLD, 110, iw=1.2))
    o.append(L(c, cx, cy + 42, "Noël", DMS, 150, CRAN, [RED, CRAN_D, "#C8404A", "#8A1A2E"], max_w=270, shadow="#E4C79A", seed=111, angle=-70,
               sdx=0.02, sdy=0.03))
    o.append(ink(f"M {cx - 70} {cy + 72} Q {cx} {cy + 86} {cx + 70} {cy + 72}", GOLD_D, 2.6, 112, 2, 0.85))
    o.append(f'<path d="{blob(cx, cy + 80, 4, 4, 113, 0.1, 8)}" fill="{GOLD}"/>')
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
    "sleigh-all-day": sleigh_all_day,
    "warm-and-cozy": warm_and_cozy,
    "home-for-christmas": home_for_christmas,
    "hes-been-here": hes_been_here,
    "silent-night": silent_night,
    "chill-out": chill_out,
    "noel": noel,
}


def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())
        print("saved", slug)


if __name__ == "__main__":
    build(sys.argv[1:] or None)
