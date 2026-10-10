"""Holidays & Dates, hand-painted edition: a gouache / storybook magnet for every date of the year, from New Year's
Eve to Christmas-week Hanukkah, plus the life moments in between (birthdays, weddings, babies, new homes).
Paper ground with tooth, organic hand-drawn shapes, layered washes with pooled edges, brush strokes that follow
each form, warm-brown ink under the paint, soft light and brush-textured lettering. Each piece has its own colour
story inside one warm paper family.

Run from tools/designs:  python3 holidays_gouache.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from gouache import blob, blob_pts, grain, ink, jitter, maple_leaf, oak, paper, smooth_closed, smooth_open, strokes, wash
import paint as pt
from poster import ANTON

COL = "holidays"

# ---------------------------------------------------------------- shared Christmas gouache palette
PINE, PINE_D, PINE_L, SAGE = "#24533F", "#13301F", "#4F8463", "#93B38D"
CRAN, RED, RED_D, RED_L = "#9B2335", "#C23A30", "#6E1621", "#E2685A"
GOLD, GOLD_L, GOLD_D = "#E0A73C", "#F6D683", "#A8711E"
CREAM, PAPER = "#F7EEDD", "#F4ECDD"
ICE, ICE_L, ICE_D = "#8FB8D0", "#D3E6EF", "#4F7C9C"
PINK, PINK_L = "#E7A3A6", "#F6D4D2"
NIGHT, NIGHT_D, NIGHT_L = "#2A3560", "#161D3A", "#4B5690"
SNOW = "#FBF8F2"
SNOW_SH = ["#C9CAE8", "#B2B6DE", "#DCDAF0", "#A3A8D6"]   # blue-violet snow shadows
WOOD, WOOD_D, WOOD_L = "#8A5532", "#5A321C", "#B87D4E"
INK = "#3A2418"        # warm brown ink
INK_N = "#22182A"      # ink for night scenes


# ---------------------------------------------------------------- colour helpers
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


def _f(v):
    return f"{v:.1f}"


# ---------------------------------------------------------------- per-design painter (ids + defs)
class Pn:
    def __init__(self, u):
        self.u, self.k, self.defs = u, 0, []

    def id(self, p="g"):
        self.k += 1
        return f"{self.u}-{p}{self.k}"

    def lg(self, stops, x1=0, y1=0, x2=0, y2=1, units="objectBoundingBox"):
        i = self.id()
        self.defs.append(pt.lg(i, stops, x1, y1, x2, y2, units))
        return i

    def rg(self, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None):
        i = self.id()
        self.defs.append(pt.rg(i, stops, cx, cy, r, fx, fy))
        return i

    def glow(self, x, y, r, col, s=0.7, ry=None):
        g = self.rg([(0, col, s), (0.35, col, s * 0.5), (1, col, 0)])
        if ry:
            return f'<ellipse cx="{_f(x)}" cy="{_f(y)}" rx="{_f(r)}" ry="{_f(ry)}" fill="url(#{g})"/>'
        return f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r)}" fill="url(#{g})"/>'

    def clip(self, inner):
        i = self.id("c")
        self.defs.append(f'<clipPath id="{i}">{inner}</clipPath>')
        return i

    def wrap(self, body):
        return "<defs>" + "".join(self.defs) + "</defs>" + body


# ---------------------------------------------------------------- hand-drawn geometry
def org_poly(pts, seed, amt=1.4, sub=14, corner=3.0):
    """A polygon redrawn by hand: edges subdivided and wobbled, corners kept fairly crisp."""
    rnd = random.Random(seed)
    out = []
    n = len(pts)
    for i in range(n):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
        L = math.hypot(x2 - x1, y2 - y1) or 1
        c = min(corner, L * 0.25) / L
        out.append((x1 + rnd.uniform(-amt, amt) * 0.4, y1 + rnd.uniform(-amt, amt) * 0.4))
        out.append((x1 + (x2 - x1) * c, y1 + (y2 - y1) * c))
        k = max(1, int(L / sub))
        for j in range(1, k):
            t = j / k
            out.append((x1 + (x2 - x1) * t + rnd.uniform(-amt, amt), y1 + (y2 - y1) * t + rnd.uniform(-amt, amt)))
        out.append((x1 + (x2 - x1) * (1 - c), y1 + (y2 - y1) * (1 - c)))
    return smooth_closed(out)


def org_rect(x, y, w, h, seed, amt=1.4, sub=14, corner=3.0):
    return org_poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], seed, amt, sub, corner)


def hline(x1, y1, x2, y2, seed, amt=1.2, sub=18):
    """A slightly wavering hand-drawn line (open path)."""
    rnd = random.Random(seed)
    L = math.hypot(x2 - x1, y2 - y1)
    k = max(2, int(L / sub))
    pts = [(x1, y1)] + [(x1 + (x2 - x1) * j / k + rnd.uniform(-amt, amt) * 0.3, y1 + (y2 - y1) * j / k + rnd.uniform(-amt, amt)) for j in range(1, k)] + [(x2, y2)]
    return smooth_open(pts)


def star_pts(cx, cy, ro, ri, n=5, rot=-90):
    return [(cx + (ro if i % 2 == 0 else ri) * math.cos(math.radians(rot + i * 180 / n)),
             cy + (ro if i % 2 == 0 else ri) * math.sin(math.radians(rot + i * 180 / n))) for i in range(2 * n)]


def bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


# ---------------------------------------------------------------- painting primitives
def paint(P, d, base, tints, box, seed, angle=-90, n=None, length=None, width=None, op=(0.2, 0.5), curve=0.2,
          ink_c=INK, ink_w=None, ink_op=0.8, edge=None, shade=None, shade_op=0.4, light=None, light_op=0.35,
          shade_dir=(0.15, 0.05, 0.95, 0.95), density=230):
    """The workhorse: a gouache wash, brush strokes inside following the form, a shadow side, an ink line."""
    x0, y0, x1, y1 = box
    w, h = max(1, x1 - x0), max(1, y1 - y0)
    m = min(w, h)
    n = n if n is not None else min(520, max(10, int(w * h / density)))
    length = length or (max(4, m * 0.16), max(8, m * 0.48))
    width = width or (max(0.7, m * 0.014), max(1.4, m * 0.04))
    out = [wash(d, base, seed, layers=2, spread=1.0, opacity=0.5, edge=edge, edge_w=2)]
    if light:
        g = P.lg([(0, light, light_op), (0.55, light, 0)], *shade_dir)
        out.append(f'<path d="{d}" fill="url(#{g})"/>')
    if n:
        out.append(strokes(P.id("s"), d, (x0 - 4, y0 - 4, x1 + 4, y1 + 4), tints, seed, n, angle, length, width, op, curve))
    if shade:
        a, b, c, e = shade_dir
        g = P.lg([(0, shade, 0), (0.45, shade, 0), (1, shade, shade_op)], a, b, c, e)
        out.append(f'<path d="{d}" fill="url(#{g})"/>')
    if ink_c:
        out.append(ink(d, ink_c, ink_w or max(1.3, min(2.8, m * 0.018)), seed + 1, 2, ink_op))
    return "".join(out)


def ball_paint(P, cx, cy, r, base, seed, tints=None, ink_c=INK, hi=True, rough=0.03):
    """Painted sphere (ornament, bauble, berry): wash, curved strokes, radial shading, dry-brush highlight."""
    d = blob(cx, cy, r, r, seed, rough, 16)
    tints = tints or [lt(base, 0.35), dk(base, 0.25), base, lt(base, 0.6)]
    g = P.rg([(0, lt(base, 0.55), 0.85), (0.45, base, 0), (0.8, dk(base, 0.4), 0.35), (1, dk(base, 0.55), 0.7)], cx=0.38, cy=0.36, r=0.7, fx=0.3, fy=0.28)
    out = [wash(d, base, seed, 2, 0.6, 0.5),
           strokes(P.id("s"), d, (cx - r, cy - r, cx + r, cy + r), tints, seed, max(6, int(r * 1.1)), angle=-60,
                   length=(r * 0.4, r * 1.1), width=(max(0.6, r * 0.05), max(1.2, r * 0.12)), opacity=(0.2, 0.5), curve=0.5),
           f'<path d="{d}" fill="url(#{g})"/>']
    if hi and r > 5:
        out.append(f'<path d="M {_f(cx - r * 0.62)} {_f(cy - r * 0.05)} Q {_f(cx - r * 0.6)} {_f(cy - r * 0.6)} {_f(cx - r * 0.05)} {_f(cy - r * 0.68)}" '
                   f'stroke="#FFFFFF" stroke-width="{max(1.2, r * 0.13):.1f}" fill="none" stroke-linecap="round" opacity="0.7"/>')
        out.append(f'<circle cx="{_f(cx - r * 0.42)}" cy="{_f(cy - r * 0.44)}" r="{max(0.8, r * 0.1):.1f}" fill="#FFFFFF" opacity="0.85"/>')
    if ink_c:
        out.append(ink(d, ink_c, max(1.1, min(2.4, r * 0.07)), seed, 2, 0.75))
    return "".join(out)


def sky_wash(P, top, bot, tints, seed, box=(0, 0, 600, 600), n=260, angle=-4, length=(50, 150), width=(3, 10), op=(0.1, 0.3), mid=None):
    """Full-bleed painted sky/wall: graded base plus long loose brush strokes."""
    x0, y0, x1, y1 = box
    stops = [(0, top), (1, bot)] if not mid else [(0, top), (mid[0], mid[1]), (1, bot)]
    g = P.lg(stops)
    d = f"M {x0} {y0} L {x1} {y0} L {x1} {y1} L {x0} {y1} Z"
    return (f'<path d="{d}" fill="url(#{g})"/>'
            + strokes(P.id("s"), d, (x0 - 60, y0 - 10, x1 + 10, y1 + 10), tints, seed, n, angle, length, width, op, 0.12))


def mottle(seed, colors, n=10, box=(0, 0, 600, 600), r=(50, 140), op=(0.04, 0.09)):
    """Uneven gouache dry patches (big soft organic blotches)."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        out.append(f'<path d="{blob(rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3]), rnd.uniform(*r), rnd.uniform(*r) * 0.7, seed + i, 0.15, 14)}" '
                   f'fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*op):.3f}"/>')
    return "".join(out)


def snow_field(P, d, box, seed, shadow_top=False, n=None, base=SNOW, edge_c="#8C90C4", ink_op=0.45):
    """Painted snow: off-white wash, blue-violet shadow strokes, a lavender gradient where it turns from the light."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    n = n or min(420, int(w * h / 260))
    stops = [(0, SNOW_SH[1], 0.55), (0.35, SNOW_SH[0], 0.12), (1, SNOW_SH[0], 0)] if shadow_top else [(0, "#FFFFFF", 0), (0.5, SNOW_SH[0], 0.12), (1, SNOW_SH[1], 0.5)]
    g = P.lg(stops)
    return (wash(d, base, seed, 2, 0.8, 0.5)
            + strokes(P.id("s"), d, (x0 - 30, y0 - 4, x1 + 4, y1 + 4), SNOW_SH + ["#FFFFFF", "#FFFFFF"], seed, n, angle=-3,
                      length=(w * 0.06 + 10, w * 0.2 + 20), width=(1.2, 4.5), opacity=(0.18, 0.5), curve=0.1)
            + f'<path d="{d}" fill="url(#{g})"/>'
            + (ink(d, edge_c, 1.6, seed, 1, ink_op) if edge_c else ""))


def snow_cap(P, pts, thick, seed, drips=True, ink_c="#7F84B8"):
    """A cap of snow lying along a polyline (roof edge, branch, sign top): rounded top, blue-violet underside."""
    rnd = random.Random(seed)
    top = []
    for i, (x, y) in enumerate(pts):
        top.append((x, y - thick * rnd.uniform(0.75, 1.05)))
    bot = []
    for i, (x, y) in enumerate(reversed(pts)):
        dy = thick * 0.25
        if drips and 0 < i < len(pts) - 1 and rnd.random() < 0.45:
            dy += thick * rnd.uniform(0.35, 0.9)
        bot.append((x, y + dy))
    ends = [(pts[-1][0] + thick * 0.35, pts[-1][1] - thick * 0.25)]
    st = [(pts[0][0] - thick * 0.35, pts[0][1] - thick * 0.25)]
    allp = st + top + ends + bot
    d = smooth_closed(allp)
    bx = bbox(allp)
    g = P.lg([(0, "#FFFFFF", 0), (0.55, SNOW_SH[0], 0.2), (1, SNOW_SH[1], 0.85)])
    return (f'<path d="{d}" fill="{SNOW}"/>'
            f'<path d="{d}" fill="url(#{g})"/>'
            + strokes(P.id("s"), d, (bx[0] - 10, bx[1], bx[2], bx[3]), ["#FFFFFF", SNOW_SH[2], SNOW_SH[0]], seed, max(4, int((bx[2] - bx[0]) / 6)),
                      angle=-4, length=(8, 26), width=(0.8, 2.2), opacity=(0.3, 0.7), curve=0.1)
            + ink(d, ink_c, 1.3, seed, 1, 0.55))


def cast(x, y, rx, ry, col="#5A4A8A", op=0.28, seed=1):
    """Soft cast shadow (two offset organic washes)."""
    return (f'<path d="{blob(x, y, rx, ry, seed, 0.08, 14)}" fill="{col}" opacity="{op * 0.6:.2f}"/>'
            f'<path d="{blob(x, y, rx * 0.75, ry * 0.7, seed + 1, 0.08, 14)}" fill="{col}" opacity="{op * 0.6:.2f}"/>')


def flakes(seed, n, box=(0, 0, 600, 600), r=(1.2, 3.4), col="#FFFFFF", op=(0.5, 0.95), avoid=()):
    """Falling snow: little dabs of white gouache, slightly irregular."""
    rnd = random.Random(seed)
    out = []
    tries = 0
    while len(out) < n and tries < n * 20:
        tries += 1
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        if any(a[0] < x < a[2] and a[1] < y < a[3] for a in avoid):
            continue
        rr = rnd.uniform(*r)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rr * rnd.uniform(0.85, 1.2):.1f}" ry="{rr * rnd.uniform(0.75, 1.0):.1f}" opacity="{rnd.uniform(*op):.2f}"/>')
    return f'<g fill="{col}">' + "".join(out) + "</g>"


def twinkle(x, y, r, col, op=1.0, w=0.16):
    q = r * w
    return (f'<path d="M {x:.1f} {y - r:.1f} Q {x + q:.1f} {y - q:.1f} {x + r:.1f} {y:.1f} Q {x + q:.1f} {y + q:.1f} {x:.1f} {y + r:.1f} '
            f'Q {x - q:.1f} {y + q:.1f} {x - r:.1f} {y:.1f} Q {x - q:.1f} {y - q:.1f} {x:.1f} {y - r:.1f} Z" fill="{col}" opacity="{op}"/>')


def dab_dots(seed, n, box, colors, r=(0.8, 2.2), op=(0.3, 0.8)):
    rnd = random.Random(seed)
    return "".join(f'<circle cx="{rnd.uniform(box[0], box[2]):.1f}" cy="{rnd.uniform(box[1], box[3]):.1f}" r="{rnd.uniform(*r):.1f}" fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*op):.2f}"/>' for _ in range(n))


# ---------------------------------------------------------------- lettering
def btext(P, x, y, s, font, size, color, tints, seed, ls=0, max_w=480, shadow=None, sh=(0.025, 0.04), angle=-12,
          anchor="middle", rot=0, halo=None, halo_w=8, n=None, op=(0.22, 0.55), ink_c=None, hi=None):
    """Brush-textured lettering: solid colour, visible strokes clipped inside the letters, an offset painted shadow,
    an optional soft halo to lift it off busy paint, and an optional dry-brush highlight colour."""
    sz = fit_size(s, font, size, max_w, ls)
    w = measure(s, font, sz, ls) - ls
    if anchor == "middle" and ls:
        x += ls / 2
    lsa = f' letter-spacing="{ls}"' if ls else ""
    st = esc(s)
    base = f'text-anchor="{anchor}" {font} font-size="{sz}"{lsa}'
    x0 = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
    tr = f' transform="rotate({rot} {_f(x)} {_f(y)})"' if rot else ""
    out = [f"<g{tr}>"]
    if halo:
        out.append(f'<text x="{_f(x)}" y="{_f(y)}" {base} fill="{halo}" stroke="{halo}" stroke-width="{halo_w}" stroke-linejoin="round" opacity="0.9">{st}</text>')
    if shadow:
        out.append(f'<text x="{_f(x + sz * sh[0])}" y="{_f(y + sz * sh[1])}" {base} fill="{shadow}">{st}</text>')
    out.append(f'<text x="{_f(x)}" y="{_f(y)}" {base} fill="{color}">{st}</text>')
    cid = P.id("t")
    rnd = random.Random(seed)
    n = n or int(w / sz * 46) + 12
    sts = []
    for _ in range(n):
        px, py = rnd.uniform(x0 - sz * 0.3, x0 + w + 4), rnd.uniform(y - sz * 0.95, y + sz * 0.3)
        L = rnd.uniform(sz * 0.2, sz * 0.6)
        ww = rnd.uniform(sz * 0.025, sz * 0.07)
        a = math.radians(angle + rnd.uniform(-10, 10))
        dx, dy = L * math.cos(a), L * math.sin(a)
        nx, ny = -math.sin(a), math.cos(a)
        mx, my = px + dx / 2, py + dy / 2
        sts.append(f'<path d="M {_f(px)} {_f(py)} Q {_f(mx + nx * ww)} {_f(my + ny * ww)} {_f(px + dx)} {_f(py + dy)} Q {_f(mx - nx * ww)} {_f(my - ny * ww)} {_f(px)} {_f(py)} Z" '
                   f'fill="{rnd.choice(tints)}" opacity="{rnd.uniform(*op):.2f}"/>')
    if hi:
        # dry-brush light catching the top of the letters
        for _ in range(int(n * 0.35)):
            px, py = rnd.uniform(x0 - 4, x0 + w), rnd.uniform(y - sz * 0.9, y - sz * 0.45)
            L = rnd.uniform(sz * 0.08, sz * 0.25)
            sts.append(f'<path d="M {_f(px)} {_f(py)} l {_f(L)} {_f(-L * 0.12)}" stroke="{hi}" stroke-width="{max(0.8, sz * 0.018):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    out.append(f'<clipPath id="{cid}"><text x="{_f(x)}" y="{_f(y)}" {base}>{st}</text></clipPath><g clip-path="url(#{cid})">{"".join(sts)}</g>')
    if ink_c:
        out.append(f'<text x="{_f(x)}" y="{_f(y)}" {base} fill="none" stroke="{ink_c}" stroke-width="{max(1, sz * 0.012):.1f}" opacity="0.55">{st}</text>')
    out.append("</g>")
    return "".join(out)


def ptext(x, y, s, font, size, fill, max_w=420, ls=0, anchor="middle", extra=""):
    """Small supporting text (plain fill, measured to fit)."""
    sz = fit_size(s, font, size, max_w, ls)
    if anchor == "middle" and ls:
        x += ls / 2
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return f'<text x="{_f(x)}" y="{_f(y)}" text-anchor="{anchor}" {font} font-size="{sz}"{lsa} fill="{fill}"{extra}>{esc(s)}</text>'


def text_w(s, font, size, max_w, ls=0):
    sz = fit_size(s, font, size, max_w, ls)
    return measure(s, font, sz, ls) - ls, sz


def flank(cy, s, font, size, ls, col, max_w=420, gap=16, L=44, seed=1, sw=2.4, dots=True):
    """Hand-inked rules either side of a centred word."""
    w, _ = text_w(s, font, size, max_w, ls)
    a, b = 300 - w / 2 - gap, 300 + w / 2 + gap
    out = ink(hline(a - L, cy, a, cy, seed), col, sw, seed, 2, 0.9) + ink(hline(b, cy, b + L, cy, seed + 1), col, sw, seed + 1, 2, 0.9)
    if dots:
        out += f'<circle cx="{_f(a - L - 9)}" cy="{cy}" r="3" fill="{col}"/><circle cx="{_f(b + L + 9)}" cy="{cy}" r="3" fill="{col}"/>'
    return out


# ---------------------------------------------------------------- painted pieces
def fir(P, cx, base, h, w, seed, cols=(PINE_D, PINE, PINE_L), tiers=4, snow=False, ink_c=INK, trunk=True,
        ink_op=0.7, lean=0.0, n_scale=1.0, light_side=-1):
    """Storybook fir: stacked scalloped tiers painted with needle strokes, shadow side, snow clumps."""
    rnd = random.Random(seed)
    dark, mid, light = cols
    out = []
    top = base - h
    if trunk:
        tw = max(4, w * 0.09)
        out.append(paint(P, org_rect(cx - tw / 2, base - h * 0.14, tw, h * 0.15, seed + 50, 0.8, 8, 1.5), WOOD, [WOOD_D, WOOD_L], (cx - tw, base - h * 0.15, cx + tw, base), seed + 50,
                         n=6, ink_c=ink_c, ink_op=ink_op))
    body_h = h * 0.9
    for i in range(tiers):
        t0 = i / tiers                              # 0 bottom tier .. top
        tb = base - h * 0.1 - body_h * t0 * 0.82    # tier bottom y
        tt = top if i == tiers - 1 else base - h * 0.1 - body_h * (t0 * 0.82 + 0.42)
        tt = max(tt, top)
        half = w / 2 * (1 - t0 * 0.78)
        ax = cx + lean * (base - tt) * 0.1
        pts = [(ax, tt)]
        # right edge down
        steps = 3
        for k in range(1, steps + 1):
            f = k / (steps + 1)
            pts.append((ax + half * f * rnd.uniform(0.92, 1.05), tt + (tb - tt) * f))
        pts.append((cx + half, tb))
        # scalloped lower edge right -> left
        sc = max(3, int(half / 14))
        for k in range(1, sc * 2):
            xx = cx + half - (2 * half) * k / (sc * 2)
            yy = tb + (h * 0.035 if k % 2 else -h * 0.012) * rnd.uniform(0.6, 1.2)
            pts.append((xx, yy))
        pts.append((cx - half, tb))
        for k in range(steps, 0, -1):
            f = k / (steps + 1)
            pts.append((ax - half * f * rnd.uniform(0.92, 1.05), tt + (tb - tt) * f))
        d = smooth_closed(pts)
        bx = (cx - half, tt, cx + half, tb + h * 0.04)
        if i > 0:
            out.append(f'<path d="{d}" fill="{dark}" opacity="0.55" transform="translate(0 {h * 0.03:.1f})"/>')
        nn = int(min(260, max(14, half * (tb - tt) / 70)) * n_scale)
        out.append(wash(d, mid, seed + i, 2, 0.8, 0.5))
        out.append(strokes(P.id("s"), d, (bx[0], bx[1], cx, bx[3]), [light, mid, dark, lt(light, 0.25)], seed + i * 3, nn // 2, angle=110,
                           length=(h * 0.05, h * 0.14), width=(max(0.6, h * 0.006), max(1.2, h * 0.016)), opacity=(0.3, 0.7), curve=0.3))
        out.append(strokes(P.id("s"), d, (cx, bx[1], bx[2], bx[3]), [light, mid, dark, dark], seed + i * 3 + 1, nn // 2, angle=70,
                           length=(h * 0.05, h * 0.14), width=(max(0.6, h * 0.006), max(1.2, h * 0.016)), opacity=(0.3, 0.7), curve=0.3))
        g = P.lg([(0, dark, 0), (0.5, dark, 0.05), (1, dark, 0.55)], 0 if light_side < 0 else 1, 0, 1 if light_side < 0 else 0, 0.3)
        out.append(f'<path d="{d}" fill="url(#{g})"/>')
        if snow:
            # clumps of snow resting on the tier's upper side
            for k in range(max(2, int(half / 12))):
                f = rnd.uniform(0.2, 0.95)
                side = rnd.choice((-1, 1))
                sx = ax + side * half * f * 0.9
                sy = tt + (tb - tt) * f - h * 0.005
                rw = max(3, h * rnd.uniform(0.03, 0.055))
                out.append(snow_cap(P, [(sx - rw, sy + side * rw * 0.25), (sx, sy - 1), (sx + rw, sy - side * rw * 0.25)], max(2.2, h * 0.018), seed + k * 7 + i, drips=False, ink_c="#9095C4"))
        if ink_c:
            out.append(ink(d, ink_c, max(1.1, min(2.2, h * 0.008)), seed + i, 2, ink_op))
    return "".join(out)


def far_trees(P, line_y, seed, col, n=26, h=(30, 70), x=(-20, 620), w=0.42, op=1.0, snow=False):
    """Distant firs as simple painted silhouettes (pale, bluish)."""
    rnd = random.Random(seed)
    out = []
    xs = sorted(rnd.uniform(*x) for _ in range(n))
    for i, xx in enumerate(xs):
        hh = rnd.uniform(*h)
        b = line_y + rnd.uniform(-4, 6)
        pts = [(xx, b - hh)]
        k = 5
        for j in range(1, k + 1):
            f = j / k
            pts.append((xx + hh * w / 2 * f * rnd.uniform(0.7, 1.1), b - hh + hh * f - (hh * 0.06 if j < k else 0)))
            if j < k:
                pts.append((xx + hh * w / 2 * f * 0.55, b - hh + hh * f + hh * 0.02))
        pts2 = [(2 * xx - px, py) for px, py in reversed(pts[1:])]
        d = smooth_closed(pts + pts2)
        out.append(f'<path d="{d}" fill="{col}" opacity="{op}"/>')
        if snow:
            out.append(f'<path d="M {_f(xx - hh * 0.08)} {_f(b - hh * 0.62)} q {_f(hh * 0.08)} {_f(-hh * 0.05)} {_f(hh * 0.16)} 0" stroke="#FFFFFF" stroke-width="{max(1.2, hh * 0.04):.1f}" fill="none" stroke-linecap="round" opacity="0.7"/>')
    return "".join(out)


def lit_window(P, x, y, w, h, seed, panes=(2, 2), frame="#3A2418", glow_c="#FFC45C", hot="#FFF2C4", warm="#F2A33A",
               glow=True, arch=False, sill=True, halo=1.5, curtain=None, fw=None):
    """Warm glowing window: halo on the wall, lit pane graded hot->warm, painted mullions, snow on the sill."""
    out = []
    if glow:
        out.append(P.glow(x + w / 2, y + h / 2, max(w, h) * halo, glow_c, 0.5))
    if arch:
        pts = [(x, y + h), (x, y + w / 2)] + [(x + w / 2 - w / 2 * math.cos(math.radians(a)), y + w / 2 - w / 2 * math.sin(math.radians(a))) for a in range(20, 170, 30)] + [(x + w, y + w / 2), (x + w, y + h)]
        d = org_poly(pts, seed, 0.6, 8, 1.5)
    else:
        d = org_rect(x, y, w, h, seed, 0.7, 10, 1.5)
    g = P.rg([(0, hot), (0.55, mix(hot, warm, 0.5)), (1, warm)], cx=0.5, cy=0.6, r=0.75)
    out.append(f'<path d="{d}" fill="url(#{g})"/>')
    out.append(strokes(P.id("s"), d, (x, y, x + w, y + h), [hot, GOLD_L, warm], seed, max(4, int(w * h / 60)), angle=-80,
                       length=(h * 0.2, h * 0.6), width=(0.6, max(1, w * 0.06)), opacity=(0.2, 0.45)))
    if curtain:
        cw = w * 0.22
        out.append(f'<path d="M {_f(x)} {_f(y)} L {_f(x + cw)} {_f(y)} Q {_f(x + cw * 0.5)} {_f(y + h * 0.5)} {_f(x + cw * 0.9)} {_f(y + h)} L {_f(x)} {_f(y + h)} Z" fill="{curtain}" opacity="0.85"/>')
        out.append(f'<path d="M {_f(x + w)} {_f(y)} L {_f(x + w - cw)} {_f(y)} Q {_f(x + w - cw * 0.5)} {_f(y + h * 0.5)} {_f(x + w - cw * 0.9)} {_f(y + h)} L {_f(x + w)} {_f(y + h)} Z" fill="{curtain}" opacity="0.85"/>')
    fw = fw or max(1.4, min(w, h) * 0.08)
    cols, rows = panes
    for c in range(1, cols):
        xx = x + w * c / cols
        out.append(ink(hline(xx, y + 1, xx, y + h - 1, seed + c, 0.5, 8), frame, fw, seed + c, 1, 0.9))
    for r in range(1, rows):
        yy = y + h * r / rows
        out.append(ink(hline(x + 1, yy, x + w - 1, yy, seed + 10 + r, 0.5, 8), frame, fw, seed + r, 1, 0.9))
    out.append(ink(d, frame, fw * 1.1, seed, 2, 0.9))
    if sill:
        out.append(snow_cap(P, [(x - w * 0.12, y + h + fw * 0.6), (x + w / 2, y + h + fw * 0.4), (x + w * 1.12, y + h + fw * 0.6)], max(2.5, h * 0.09), seed + 3, drips=False))
    return "".join(out)


def bulb(P, x, y, s, col, rot, seed, glow=True, ink_c=INK):
    """C9 holiday bulb hanging from a socket at (x, y), pointing along rot (0 = straight down)."""
    out = [f'<g transform="rotate({rot:.1f} {_f(x)} {_f(y)})">']
    if glow:
        out.append(P.glow(x, y + s * 1.25, s * 2.6, col, 0.55))
    sock = org_rect(x - s * 0.28, y - s * 0.1, s * 0.56, s * 0.48, seed, 0.3, 6, 1)
    out.append(f'<path d="{sock}" fill="#2C4A36"/>'
               f'<path d="M {_f(x - s * 0.22)} {_f(y + s * 0.08)} l {_f(s * 0.44)} 0 M {_f(x - s * 0.22)} {_f(y + s * 0.22)} l {_f(s * 0.44)} 0" stroke="#5C8068" stroke-width="{max(0.7, s * 0.05):.1f}"/>')
    pts = [(x - s * 0.3, y + s * 0.36), (x - s * 0.52, y + s * 0.85), (x - s * 0.42, y + s * 1.45), (x, y + s * 1.95),
           (x + s * 0.42, y + s * 1.45), (x + s * 0.52, y + s * 0.85), (x + s * 0.3, y + s * 0.36)]
    d = smooth_closed(jitter(pts, seed, s * 0.02))
    g = P.rg([(0, lt(col, 0.75)), (0.45, lt(col, 0.2)), (1, col)], cx=0.42, cy=0.6, r=0.6)
    out.append(f'<path d="{d}" fill="url(#{g})"/>')
    out.append(strokes(P.id("s"), d, (x - s * 0.6, y + s * 0.3, x + s * 0.6, y + s * 2), [lt(col, 0.6), col, dk(col, 0.15)], seed, 8,
                       angle=90, length=(s * 0.5, s * 1.2), width=(s * 0.04, s * 0.1), opacity=(0.25, 0.5)))
    out.append(f'<path d="M {_f(x - s * 0.22)} {_f(y + s * 0.65)} q {_f(-s * 0.12)} {_f(s * 0.4)} {_f(s * 0.02)} {_f(s * 0.8)}" stroke="#FFFFFF" stroke-width="{max(1, s * 0.11):.1f}" fill="none" stroke-linecap="round" opacity="0.75"/>')
    out.append(ink(d, ink_c, max(1, s * 0.07), seed, 2, 0.6))
    out.append("</g>")
    return "".join(out)


def holly(P, x, y, s, rot, seed, berries=3, leaf_c=PINE, ink_c=INK):
    """Painted holly sprig: two spiky leaves and a cluster of glossy berries."""
    out = [f'<g transform="rotate({rot} {_f(x)} {_f(y)})">']
    for k, (ang, L) in enumerate(((-28, 1.0), (205, 0.95))):
        a = math.radians(ang)
        tx, ty = x + math.cos(a) * s * L, y + math.sin(a) * s * L
        nx, ny = -math.sin(a), math.cos(a)
        pts = []
        spikes = 4
        for j in range(spikes * 2 + 1):
            f = j / (spikes * 2)
            px, py = x + (tx - x) * f, y + (ty - y) * f
            wdt = s * 0.3 * math.sin(math.pi * f) * (1.25 if j % 2 else 0.8)
            pts.append((px + nx * wdt, py + ny * wdt))
        for j in range(spikes * 2 - 1, 0, -1):
            f = j / (spikes * 2)
            px, py = x + (tx - x) * f, y + (ty - y) * f
            wdt = s * 0.3 * math.sin(math.pi * f) * (1.25 if j % 2 else 0.8)
            pts.append((px - nx * wdt, py - ny * wdt))
        d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts) + " Z"
        out.append(paint(P, d, leaf_c, [lt(leaf_c, 0.3), dk(leaf_c, 0.3), lt(leaf_c, 0.15)], (min(x, tx) - s * 0.3, min(y, ty) - s * 0.3, max(x, tx) + s * 0.3, max(y, ty) + s * 0.3),
                         seed + k, angle=ang, n=10, ink_c=ink_c, ink_w=max(1, s * 0.035), ink_op=0.7))
        out.append(f'<path d="M {_f(x)} {_f(y)} L {_f(tx)} {_f(ty)}" stroke="{lt(leaf_c, 0.45)}" stroke-width="{max(0.8, s * 0.03):.1f}" opacity="0.8"/>')
    for k in range(berries):
        a = math.radians(-90 + (k - (berries - 1) / 2) * 50)
        out.append(ball_paint(P, x + math.cos(a) * s * 0.14, y + math.sin(a) * s * 0.12 + s * 0.02, s * 0.13, RED, seed + 20 + k, ink_c=ink_c))
    out.append("</g>")
    return "".join(out)


def pine_sprig(P, x1, y1, x2, y2, seed, cols=(PINE_D, PINE, PINE_L), needle=10, ink_c=None, density=1.0):
    """A fir branch: a woody twig with painted needle strokes fanning along it."""
    rnd = random.Random(seed)
    L = math.hypot(x2 - x1, y2 - y1)
    a = math.atan2(y2 - y1, x2 - x1)
    out = [f'<path d="{hline(x1, y1, x2, y2, seed, 1.5)}" stroke="{WOOD_D}" stroke-width="{max(1.5, needle * 0.22):.1f}" fill="none" stroke-linecap="round"/>']
    n = int(L / 2.2 * density)
    for i in range(n):
        f = rnd.uniform(0, 1)
        px, py = x1 + (x2 - x1) * f, y1 + (y2 - y1) * f
        side = rnd.choice((-1, 1))
        ang = a + side * math.radians(rnd.uniform(35, 70))
        ln = needle * rnd.uniform(0.7, 1.15) * (0.55 + 0.45 * math.sin(math.pi * min(1, f * 1.2 + 0.1)))
        ex, ey = px + math.cos(ang) * ln, py + math.sin(ang) * ln
        out.append(f'<path d="M {_f(px)} {_f(py)} L {_f(ex)} {_f(ey)}" stroke="{rnd.choice(cols)}" stroke-width="{rnd.uniform(1.3, 2.4):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.7, 1):.2f}"/>')
    return "".join(out)


def figure(P, x, base, hh, coat, seed, scarf=None, hat=None, flip=1, ink_c=INK_N):
    """A tiny painted villager (storybook silhouette with a coloured coat)."""
    head = hh * 0.17
    body = blob(x, base - hh * 0.38, hh * 0.17, hh * 0.36, seed, 0.05, 12)
    out = [cast(x + 4 * flip, base + 1, hh * 0.28, hh * 0.05, "#5A5A9A", 0.4, seed),
           f'<path d="M {_f(x - hh * 0.07)} {_f(base - hh * 0.1)} l 0 {_f(hh * 0.1)} M {_f(x + hh * 0.07)} {_f(base - hh * 0.1)} l 0 {_f(hh * 0.1)}" stroke="{ink_c}" stroke-width="{max(1.5, hh * 0.06):.1f}" stroke-linecap="round"/>',
           f'<path d="{body}" fill="{coat}"/>',
           f'<path d="{body}" fill="none" stroke="{ink_c}" stroke-width="1.2" opacity="0.6"/>',
           f'<path d="{blob(x, base - hh * 0.82, head, head * 1.05, seed + 1, 0.04, 10)}" fill="#E8B898"/>']
    if scarf:
        out.append(f'<path d="M {_f(x - hh * 0.15)} {_f(base - hh * 0.68)} q {_f(hh * 0.15)} {_f(hh * 0.06)} {_f(hh * 0.3)} 0 l 0 {_f(hh * 0.06)} q {_f(-hh * 0.15)} {_f(hh * 0.06)} {_f(-hh * 0.3)} 0 Z" fill="{scarf}"/>'
                   f'<path d="M {_f(x + hh * 0.08 * flip)} {_f(base - hh * 0.64)} l {_f(hh * 0.06 * flip)} {_f(hh * 0.2)}" stroke="{scarf}" stroke-width="{max(1.5, hh * 0.06):.1f}" stroke-linecap="round"/>')
    if hat:
        out.append(f'<path d="{blob(x, base - hh * 0.9, head * 1.05, head * 0.65, seed + 2, 0.05, 10)}" fill="{hat}"/>'
                   f'<circle cx="{_f(x)}" cy="{_f(base - hh * 1.0)}" r="{max(1.2, hh * 0.05):.1f}" fill="{SNOW}"/>')
    return "".join(out)


def gift(P, x, y, w, h, col, rib, seed, pattern=None, pcol=None, lid=True, bow=True, ink_c=INK):
    """Painted present: box with a lid, ribbons, painted pattern and a loopy bow."""
    out = [cast(x + w / 2 + 4, y + h + 2, w * 0.62, max(4, h * 0.08), "#3A2418", 0.35, seed)]
    d = org_rect(x, y, w, h, seed, 0.9, 12, 2)
    body = [paint(P, d, col, [lt(col, 0.25), dk(col, 0.2), col], (x, y, x + w, y + h), seed, angle=-75, shade=dk(col, 0.45), shade_op=0.45,
                  shade_dir=(0, 0, 1, 0.2), ink_c=None)]
    if pattern == "dots":
        rnd = random.Random(seed)
        for _ in range(int(w * h / 180)):
            body.append(f'<circle cx="{rnd.uniform(x + 3, x + w - 3):.1f}" cy="{rnd.uniform(y + 3, y + h - 3):.1f}" r="{rnd.uniform(1.6, 2.6):.1f}" fill="{pcol}" opacity="0.9"/>')
    elif pattern == "stripes":
        for k in range(-int(h / 10), int(w / 10) + 2):
            sx = x + k * 13
            body.append(f'<path d="M {_f(sx)} {_f(y + h)} L {_f(sx + h * 0.6)} {_f(y)}" stroke="{pcol}" stroke-width="4" opacity="0.75"/>')
    elif pattern == "stars":
        rnd = random.Random(seed)
        for _ in range(int(w * h / 330)):
            body.append(twinkle(rnd.uniform(x + 5, x + w - 5), rnd.uniform(y + 5, y + h - 5), rnd.uniform(3, 5), pcol, 0.9))
    cid = P.clip(f'<path d="{d}"/>')
    out.append(f'<g clip-path="url(#{cid})">{"".join(body)}</g>')
    rw = max(4, w * 0.13)
    out.append(paint(P, org_rect(x + w / 2 - rw / 2, y, rw, h, seed + 1, 0.5, 10, 1), rib, [lt(rib, 0.4), dk(rib, 0.2)], (x + w / 2 - rw, y, x + w / 2 + rw, y + h), seed + 1, n=6, ink_c=None))
    if lid:
        lh = max(6, h * 0.2)
        ld = org_rect(x - w * 0.04, y - lh * 0.2, w * 1.08, lh, seed + 2, 0.7, 10, 1.5)
        out.append(paint(P, ld, lt(col, 0.08), [lt(col, 0.35), dk(col, 0.15)], (x - w * 0.04, y - lh * 0.2, x + w * 1.04, y + lh * 0.8), seed + 2, angle=0, n=8,
                         shade=dk(col, 0.4), shade_op=0.35, ink_c=ink_c, ink_op=0.7))
        out.append(f'<path d="{org_rect(x + w / 2 - rw / 2, y - lh * 0.2, rw, lh, seed + 3, 0.4, 8, 1)}" fill="{rib}"/>')
    out.append(ink(d, ink_c, max(1.2, min(2.2, w * 0.025)), seed, 2, 0.75))
    if bow:
        out.append(bow_p(P, x + w / 2, y - (h * 0.04 if lid else 0), max(8, w * 0.26), rib, seed + 4, ink_c))
    return "".join(out)


def bow_p(P, bx, by, s, rib, seed, ink_c=INK):
    out = []
    for sg in (-1, 1):
        d = smooth_closed(jitter([(bx, by), (bx + sg * s * 0.55, by - s * 0.55), (bx + sg * s * 0.95, by - s * 0.3), (bx + sg * s * 0.75, by + s * 0.02)], seed + sg, s * 0.03))
        out.append(paint(P, d, rib, [lt(rib, 0.35), dk(rib, 0.25)], (bx - s, by - s * 0.6, bx + s, by + s * 0.1), seed + sg, angle=-40 * sg, n=6,
                         ink_c=ink_c, ink_w=max(1, s * 0.07), ink_op=0.7))
        out.append(f'<path d="M {_f(bx)} {_f(by)} q {_f(sg * s * 0.25)} {_f(s * 0.35)} {_f(sg * s * 0.45)} {_f(s * 0.6)}" stroke="{rib}" stroke-width="{max(2, s * 0.16):.1f}" fill="none" stroke-linecap="round"/>')
    out.append(f'<path d="{blob(bx, by - s * 0.02, s * 0.16, s * 0.14, seed, 0.05, 10)}" fill="{dk(rib, 0.1)}"/>')
    return "".join(out)


def star_painted(P, cx, cy, r, seed, col=GOLD, glow=True, rot=-90, ink_c=INK, n=5, inner=0.45):
    out = []
    if glow:
        out.append(P.glow(cx, cy, r * 3.2, GOLD_L, 0.6))
    pts = star_pts(cx, cy, r, r * inner, n, rot)
    d = org_poly(pts, seed, r * 0.02, r, r * 0.06)
    out.append(paint(P, d, col, [GOLD_L, lt(GOLD_L, 0.5), GOLD_D, col], (cx - r, cy - r, cx + r, cy + r), seed, angle=-60, n=int(r * 1.4),
                     shade=GOLD_D, shade_op=0.5, ink_c=ink_c, ink_w=max(1.2, r * 0.06)))
    out.append(f'<path d="M {_f(cx - r * 0.1)} {_f(cy - r * 0.55)} L {_f(cx - r * 0.02)} {_f(cy - r * 0.05)}" stroke="#FFF6D8" stroke-width="{max(1, r * 0.08):.1f}" stroke-linecap="round" opacity="0.8"/>')
    return "".join(out)


def finish(P, body, seed):
    """Paper grain over everything (the very last layer)."""
    return P.wrap(body + grain(P.id("grain"), INK, seed, 1.0))

def arc_text(P, cx, cy, r, s, font, size, fill, ls=0, top=True, op=1.0):
    pid = P.id("arc")
    if top:
        d = f"M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"
    else:
        d = f"M {cx - r} {cy} A {r} {r} 0 0 0 {cx + r} {cy}"
    P.defs.append(f'<path id="{pid}" d="{d}"/>')
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return f'<text {font} font-size="{size}"{lsa} fill="{fill}" opacity="{op}"><textPath href="#{pid}" startOffset="50%" text-anchor="middle">{esc(s)}</textPath></text>'



# =============================================================== holiday pieces (new for this collection)
CORAL, CORAL_D, CORAL_L = "#E2725B", "#B04A38", "#F4A78E"
TEAL, TEAL_D, TEAL_L = "#2E6E74", "#1C4448", "#6FA6A4"
NAVY, NAVY_D, NAVY_L = "#22305A", "#141C38", "#3E4E86"
BLUSH, BLUSH_L, ROSE = "#F2C4C0", "#F9E0DA", "#D9606E"
MINT, MINT_L = "#A8D4C0", "#D6ECE0"
BUTTER, BUTTER_L = "#F2D06B", "#FBEAB0"
LILAC, LILAC_L, PLUM = "#B8A2D6", "#DCD0EC", "#5A3A6E"
LEAF, LEAF_D, LEAF_L = "#5E8A4A", "#355A2E", "#94B874"
SKY, SKY_L = "#8CBCD8", "#CFE4EE"


def heart_pts(cx, cy, s, rot=0, n=30, seed=None, amt=0.0):
    """Organic heart outline (s = half width), point down; rot in degrees."""
    k = s / 16.5
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        out.append((x * k, (y + 2.5) * k))
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = [(cx + x * c - y * sn, cy + x * sn + y * c) for x, y in out]
    if seed is not None and amt:
        out = jitter(out, seed, amt)
    return out


def heart_d(cx, cy, s, rot=0, seed=1, amt=None):
    return smooth_closed(heart_pts(cx, cy, s, rot, 30, seed, s * 0.015 if amt is None else amt))


def p_heart(P, cx, cy, s, col, seed, rot=0, ink_c=INK, hi=True, n=None, glossy=True):
    """Painted heart: wash, strokes following the lobes, round shading, dry-brush highlight."""
    d = heart_d(cx, cy, s, rot, seed)
    out = [paint(P, d, col, [lt(col, 0.3), dk(col, 0.2), col, lt(col, 0.5)], (cx - s, cy - s, cx + s, cy + s), seed, angle=-60 + rot,
                 n=n if n is not None else max(6, int(s * 1.2)), length=(s * 0.3, s * 0.9), width=(max(0.6, s * 0.04), max(1.2, s * 0.1)),
                 curve=0.5, ink_c=None)]
    if glossy:
        g = P.rg([(0, lt(col, 0.55), 0.7), (0.5, col, 0), (0.85, dk(col, 0.35), 0.35), (1, dk(col, 0.5), 0.6)], cx=0.36, cy=0.32, r=0.75, fx=0.3, fy=0.26)
        out.append(f'<path d="{d}" fill="url(#{g})"/>')
    if hi and s > 7:
        c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        def R(x, y):
            return cx + x * c - y * sn, cy + x * sn + y * c
        a, b, e = R(-s * 0.66, -s * 0.12), R(-s * 0.68, -s * 0.52), R(-s * 0.3, -s * 0.62)
        out.append(f'<path d="M {_f(a[0])} {_f(a[1])} Q {_f(b[0])} {_f(b[1])} {_f(e[0])} {_f(e[1])}" stroke="#FFFFFF" stroke-width="{max(1.2, s * 0.09):.1f}" '
                   f'fill="none" stroke-linecap="round" opacity="0.6"/>')
    if ink_c:
        out.append(ink(d, ink_c, max(1.1, min(2.6, s * 0.06)), seed, 2, 0.75))
    return "".join(out)


def leaf_shape(x, y, L, ang, wfrac=0.32, seed=1, tip=1.0, n=9):
    """Leaf outline from base (x, y) along ang (degrees), length L."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    rnd = random.Random(seed)
    left, right = [], []
    for i in range(1, n):
        f = i / n
        w = L * wfrac * math.sin(math.pi * f ** (0.8 * tip)) * (1 - 0.15 * f)
        px, py = x + ux * L * f, y + uy * L * f
        j = rnd.uniform(0.92, 1.06)
        left.append((px + nx * w * j, py + ny * w * j))
        right.append((px - nx * w * j, py - ny * w * j))
    return [(x, y)] + left + [(x + ux * L, y + uy * L)] + list(reversed(right))


def p_leaf(P, x, y, L, ang, col, seed, wfrac=0.32, ink_c=INK, vein=True, ink_w=None, shade=True):
    pts = leaf_shape(x, y, L, ang, wfrac, seed)
    d = smooth_closed(pts)
    bx = bbox(pts)
    out = [paint(P, d, col, [lt(col, 0.3), dk(col, 0.25), lt(col, 0.15), col], bx, seed, angle=ang, n=max(5, int(L * 0.45)),
                 length=(L * 0.15, L * 0.45), width=(max(0.6, L * 0.02), max(1.1, L * 0.05)), curve=0.2, ink_c=None)]
    if shade:
        # one half of the leaf a touch darker (light from the upper left)
        a = math.radians(ang)
        half = [(x, y)] + pts[1:len(pts) // 2 + 1]
        out.append(f'<path d="{smooth_closed(half)}" fill="{dk(col, 0.35)}" opacity="0.28"/>')
    if vein:
        a = math.radians(ang)
        ex, ey = x + math.cos(a) * L * 0.85, y + math.sin(a) * L * 0.85
        out.append(f'<path d="M {_f(x)} {_f(y)} Q {_f((x + ex) / 2 + math.sin(a) * L * 0.04)} {_f((y + ey) / 2 - math.cos(a) * L * 0.04)} {_f(ex)} {_f(ey)}" '
                   f'stroke="{lt(col, 0.45)}" stroke-width="{max(0.8, L * 0.025):.1f}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    if ink_c:
        out.append(ink(d, ink_c, ink_w or max(1.0, min(2.0, L * 0.035)), seed, 2, 0.7))
    return "".join(out)


def stem(P, pts, col, w, seed, ink_c=None):
    d = smooth_open(pts)
    out = [f'<path d="{d}" stroke="{col}" stroke-width="{_f(w)}" fill="none" stroke-linecap="round"/>',
           f'<path d="{d}" stroke="{lt(col, 0.35)}" stroke-width="{_f(max(0.6, w * 0.3))}" fill="none" stroke-linecap="round" opacity="0.6" transform="translate(-{_f(w * 0.2)} 0)"/>']
    if ink_c:
        out.append(ink(d, ink_c, max(0.8, w * 0.25), seed, 1, 0.4))
    return "".join(out)


def petal_pts(cx, cy, L, wid, ang, seed, notch=0.0, base_w=0.25):
    """A petal from the flower centre outward."""
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    rnd = random.Random(seed)
    prof = [(0.0, base_w * 0.5), (0.25, 0.75), (0.55, 1.0), (0.8, 0.9), (0.95, 0.55)]
    left = [(cx + ux * L * f + nx * wid * w * rnd.uniform(0.94, 1.06), cy + uy * L * f + ny * wid * w * rnd.uniform(0.94, 1.06)) for f, w in prof]
    right = [(cx + ux * L * f - nx * wid * w * rnd.uniform(0.94, 1.06), cy + uy * L * f - ny * wid * w * rnd.uniform(0.94, 1.06)) for f, w in prof]
    tip = [(cx + ux * L * (1 - notch), cy + uy * L * (1 - notch))] if notch else [(cx + ux * L, cy + uy * L)]
    if notch:
        tip = [(cx + ux * L * 0.99 + nx * wid * 0.25, cy + uy * L * 0.99 + ny * wid * 0.25), tip[0], (cx + ux * L * 0.99 - nx * wid * 0.25, cy + uy * L * 0.99 - ny * wid * 0.25)]
    return left + tip + list(reversed(right))


def peony(P, cx, cy, r, col, seed, ink_c=INK, center=None, rot=0):
    """Full painted peony / garden rose: ruffled outer petals, cupped inner petals, a deeper heart."""
    rnd = random.Random(seed)
    out = [cast(cx + r * 0.08, cy + r * 0.12, r * 1.02, r * 0.95, dk(col, 0.6), 0.18, seed)]
    for ring, (k, rad, wid, shade) in enumerate(((8, 1.0, 0.5, 0.18), (7, 0.78, 0.46, 0.08), (6, 0.56, 0.42, 0.0))):
        base = mix(col, dk(col, 0.25), ring * 0.3) if ring else lt(col, 0.12)
        for i in range(k):
            ang = rot + i * 360 / k + ring * 23 + rnd.uniform(-8, 8)
            pts = petal_pts(cx, cy, r * rad * rnd.uniform(0.92, 1.05), r * wid, ang, seed + ring * 20 + i, notch=0.05 if ring == 0 else 0)
            d = smooth_closed(pts)
            bx = bbox(pts)
            out.append(paint(P, d, base, [lt(col, 0.45), lt(col, 0.25), dk(col, 0.15), col], bx, seed + ring * 20 + i, angle=ang + 180, n=7,
                             length=(r * 0.15, r * 0.45), width=(max(0.6, r * 0.025), max(1, r * 0.06)), curve=0.4, op=(0.25, 0.55),
                             ink_c=ink_c, ink_w=max(0.9, r * 0.022), ink_op=0.5))
            if ring == 0:
                a = math.radians(ang)
                out.append(f'<path d="M {_f(cx + math.cos(a) * r * 0.35)} {_f(cy + math.sin(a) * r * 0.35)} L {_f(cx + math.cos(a) * r * 0.8)} {_f(cy + math.sin(a) * r * 0.8)}" '
                           f'stroke="{dk(col, 0.3)}" stroke-width="{max(0.8, r * 0.015):.1f}" opacity="0.35"/>')
    # cupped centre: a few nested arcs
    cc = center or dk(col, 0.25)
    out.append(f'<path d="{blob(cx, cy, r * 0.3, r * 0.26, seed + 70, 0.1, 12)}" fill="{cc}"/>')
    for j in range(5):
        a0 = rnd.uniform(0, 360)
        rr = r * (0.08 + j * 0.05)
        a1, a2 = math.radians(a0), math.radians(a0 + 200)
        out.append(f'<path d="M {_f(cx + math.cos(a1) * rr)} {_f(cy + math.sin(a1) * rr)} A {_f(rr)} {_f(rr * 0.85)} 0 1 1 {_f(cx + math.cos(a2) * rr)} {_f(cy + math.sin(a2) * rr)}" '
                   f'stroke="{lt(col, 0.5) if j % 2 else dk(col, 0.4)}" stroke-width="{max(1, r * 0.04):.1f}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    g = P.rg([(0, "#FFFFFF", 0.3), (0.5, "#FFFFFF", 0), (1, dk(col, 0.5), 0.25)], cx=0.38, cy=0.35, r=0.65)
    out.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 1.05)}" fill="url(#{g})"/>')
    return "".join(out)


def daisy(P, cx, cy, r, seed, petal="#FFFDF6", center=BUTTER, ink_c=INK, n=14, rot=0, tilt=1.0):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        ang = rot + i * 360 / n + rnd.uniform(-4, 4)
        pts = petal_pts(cx, cy, r * rnd.uniform(0.9, 1.05), r * 0.17, ang, seed + i, notch=0.04)
        pts = [(cx + (x - cx), cy + (y - cy) * tilt) for x, y in pts]
        d = smooth_closed(pts)
        out.append(f'<path d="{d}" fill="{petal}"/>'
                   f'<path d="{d}" fill="none" stroke="{ink_c}" stroke-width="{max(0.8, r * 0.02):.1f}" opacity="0.45"/>')
        a = math.radians(ang)
        out.append(f'<path d="M {_f(cx + math.cos(a) * r * 0.3)} {_f(cy + math.sin(a) * r * 0.3 * tilt)} L {_f(cx + math.cos(a) * r * 0.8)} {_f(cy + math.sin(a) * r * 0.8 * tilt)}" '
                   f'stroke="#D8CCC0" stroke-width="{max(0.7, r * 0.03):.1f}" opacity="0.6"/>')
    out.append(ball_paint(P, cx, cy, r * 0.3, center, seed + 50, ink_c=ink_c, hi=False))
    out.append(dab_dots(seed + 51, int(r * 0.6), (cx - r * 0.2, cy - r * 0.2 * tilt, cx + r * 0.2, cy + r * 0.2 * tilt), [dk(center, 0.3), dk(center, 0.5)], (0.6, 1.4), (0.5, 0.9)))
    return "".join(out)


def blossom(P, cx, cy, r, seed, col="#F6C6CC", center="#C2505E", ink_c=INK, rot=0):
    """Five-petal blossom (cherry / apple)."""
    out = []
    for i in range(5):
        ang = rot + i * 72
        pts = petal_pts(cx, cy, r, r * 0.42, ang, seed + i, notch=0.12, base_w=0.3)
        d = smooth_closed(pts)
        out.append(paint(P, d, col, [lt(col, 0.5), dk(col, 0.12), "#FFFFFF"], bbox(pts), seed + i, angle=ang, n=4, length=(r * 0.2, r * 0.5),
                         width=(0.6, max(1, r * 0.08)), ink_c=ink_c, ink_w=max(0.8, r * 0.04), ink_op=0.5))
    out.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 0.2)}" fill="{center}"/>')
    rnd = random.Random(seed)
    for i in range(7):
        a = math.radians(rnd.uniform(0, 360))
        out.append(f'<path d="M {_f(cx)} {_f(cy)} L {_f(cx + math.cos(a) * r * 0.42)} {_f(cy + math.sin(a) * r * 0.42)}" stroke="{center}" stroke-width="{max(0.6, r * 0.04):.1f}"/>'
                   f'<circle cx="{_f(cx + math.cos(a) * r * 0.44)}" cy="{_f(cy + math.sin(a) * r * 0.44)}" r="{max(0.8, r * 0.06):.1f}" fill="{BUTTER}"/>')
    return "".join(out)


def tulip(P, x, base, h, col, seed, lean=0.0, ink_c=INK, leaves=True, head=None):
    """Garden tulip: tapered stem, two long leaves, a cup of three petals."""
    hx, hy = x + lean * h, base - h
    s = head or h * 0.2
    out = []
    out.append(stem(P, [(x, base), (x + lean * h * 0.3, base - h * 0.5), (hx, hy + s * 0.5)], LEAF, max(2.5, s * 0.16), seed, INK))
    if leaves:
        out.append(p_leaf(P, x, base, h * 0.55, -100 + lean * 40, LEAF, seed + 1, 0.2, ink_c))
        out.append(p_leaf(P, x + 2, base - 2, h * 0.45, -68 + lean * 40, LEAF_L, seed + 2, 0.2, ink_c))
    back = smooth_closed(jitter([(hx - s * 0.5, hy + s * 0.2), (hx - s * 0.45, hy - s * 0.6), (hx - s * 0.15, hy - s * 0.95), (hx, hy - s * 0.65), (hx + s * 0.15, hy - s * 0.95),
                                 (hx + s * 0.45, hy - s * 0.6), (hx + s * 0.5, hy + s * 0.2), (hx, hy + s * 0.55)], seed, s * 0.02))
    out.append(paint(P, back, dk(col, 0.15), [lt(col, 0.3), dk(col, 0.3)], (hx - s * 0.5, hy - s, hx + s * 0.5, hy + s * 0.55), seed + 3, angle=-90, n=8, ink_c=ink_c, ink_w=max(1, s * 0.05)))
    for sg in (-1, 1):
        fr = smooth_closed(jitter([(hx, hy + s * 0.55), (hx + sg * s * 0.55, hy + s * 0.1), (hx + sg * s * 0.4, hy - s * 0.6), (hx + sg * s * 0.05, hy - s * 0.75),
                                   (hx - sg * s * 0.05, hy - s * 0.2)], seed + 4 + sg, s * 0.02))
        out.append(paint(P, fr, col, [lt(col, 0.4), dk(col, 0.2), lt(col, 0.2)], (hx - s * 0.6, hy - s * 0.8, hx + s * 0.6, hy + s * 0.6), seed + 5 + sg, angle=-90, n=8,
                         shade=dk(col, 0.4), shade_op=0.35, shade_dir=(0.5 - sg * 0.5, 0, 0.5 + sg * 0.5, 0.3), ink_c=ink_c, ink_w=max(1, s * 0.05)))
    out.append(f'<path d="M {_f(hx - s * 0.3)} {_f(hy - s * 0.4)} q {_f(-s * 0.06)} {_f(s * 0.3)} {_f(s * 0.06)} {_f(s * 0.6)}" stroke="#FFFFFF" stroke-width="{max(1, s * 0.07):.1f}" fill="none" stroke-linecap="round" opacity="0.55"/>')
    return "".join(out)


def cloud(P, cx, cy, w, h, seed, base="#FFFFFF", shade="#C9D6E6", ink_c=None, op=1.0, puffs=None):
    """Storybook cloud from overlapping painted puffs, shaded underneath."""
    rnd = random.Random(seed)
    puffs = puffs or [(-0.36, 0.15, 0.26), (-0.12, -0.12, 0.36), (0.16, -0.18, 0.32), (0.38, 0.08, 0.24), (0.0, 0.18, 0.3)]
    ds = [blob(cx + dx * w, cy + dy * h * 1.6, r * w * rnd.uniform(0.92, 1.05), r * w * 0.82, seed + i, 0.05, 14) for i, (dx, dy, r) in enumerate(puffs)]
    allp = " ".join(ds)
    cid = P.clip("".join(f'<path d="{d}"/>' for d in ds))
    g = P.lg([(0, "#FFFFFF", 0), (0.5, shade, 0.2), (1, shade, 0.9)])
    body = (f'<rect x="{_f(cx - w)}" y="{_f(cy - h * 1.5)}" width="{_f(2 * w)}" height="{_f(h * 3)}" fill="{base}"/>'
            f'<rect x="{_f(cx - w)}" y="{_f(cy - h * 0.6)}" width="{_f(2 * w)}" height="{_f(h * 1.5)}" fill="url(#{g})"/>'
            + strokes(P.id("s"), allp, (cx - w, cy - h * 1.3, cx + w, cy + h), ["#FFFFFF", shade, lt(shade, 0.5)], seed, int(w * 0.5), angle=-10,
                      length=(w * 0.1, w * 0.35), width=(1, max(1.5, h * 0.05)), opacity=(0.25, 0.6), curve=0.4))
    out = [f'<g opacity="{op}"><g clip-path="url(#{cid})">{body}</g>']
    if ink_c:
        for d in ds:
            out.append(f'<path d="{d}" fill="none" stroke="{ink_c}" stroke-width="1.2" opacity="0.18"/>')
    out.append("</g>")
    return "".join(out)


def ribbon(P, cx, cy, w, h, col, seed, tail=40, drop=14, ink_c=INK, curve=10):
    """Painted ribbon banner (gently arched) with folded, notched tails."""
    out = []
    for sg in (-1, 1):
        ex = cx + sg * w / 2
        tp = [(ex - sg * 6, cy - h / 2 + drop + curve * 0.3), (ex + sg * tail, cy - h / 2 + drop + curve * 0.3), (ex + sg * (tail - 14), cy + drop * 0.5 + curve * 0.3),
              (ex + sg * tail, cy + h / 2 + drop + curve * 0.3), (ex - sg * 6, cy + h / 2 + drop + curve * 0.3)]
        d = org_poly(tp, seed + sg, 0.6, 12, 1.5)
        out.append(paint(P, d, dk(col, 0.22), [dk(col, 0.35), col], bbox(tp), seed + sg, angle=0, n=8, ink_c=ink_c, ink_w=1.6))
        fold = [(ex - sg * 2, cy + h / 2 + curve * 0.3), (ex + sg * 14, cy + h / 2 + drop + curve * 0.3), (ex - sg * 2, cy + h / 2 + drop + curve * 0.3)]
        out.append(f'<path d="M {" L ".join(f"{_f(a)} {_f(b)}" for a, b in fold)} Z" fill="{dk(col, 0.5)}"/>')
    top = [(cx - w / 2 + w * i / 8, cy - h / 2 + curve * (1 - ((i - 4) / 4) ** 2) * -1 + curve) for i in range(9)]
    bot = [(x, y + h) for x, y in reversed(top)]
    d = smooth_closed(jitter(top, seed, 0.6) + jitter(bot, seed + 1, 0.6))
    out.append(paint(P, d, col, [lt(col, 0.3), dk(col, 0.15), col], (cx - w / 2, cy - h / 2 - curve, cx + w / 2, cy + h / 2 + curve), seed, angle=-2, n=int(w * 0.25),
                     length=(20, 60), width=(1.5, 4), shade=dk(col, 0.4), shade_op=0.35, shade_dir=(0, 0, 0, 1), ink_c=ink_c, ink_w=2))
    return "".join(out)


def ribbon_text_path(P, cx, cy, w, curve=10):
    """Path for text that follows the ribbon arch (returns its id)."""
    pid = P.id("rt")
    P.defs.append(f'<path id="{pid}" d="M {_f(cx - w / 2)} {_f(cy)} Q {_f(cx)} {_f(cy - curve * 2)} {_f(cx + w / 2)} {_f(cy)}"/>')
    return pid


def bunting(P, x0, y0, x1, y1, sag, n, cols, seed, size=34, ink_c=INK, pattern=None, rope="#8A6A4A"):
    """A string of painted pennant flags hanging along a sagging cord."""
    out = []
    def pt(t):
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)
        return x, y
    pts = [pt(i / 40) for i in range(41)]
    out.append(ink(smooth_open(pts), rope, 2.4, seed, 2, 0.95))
    rnd = random.Random(seed)
    for i in range(n):
        t0 = (i + 0.12) / n
        t1 = (i + 0.88) / n
        a, b = pt(t0), pt(t1)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        L = size * 1.25
        tip = (mx - math.sin(ang) * -L, my + math.cos(ang) * L)
        col = cols[i % len(cols)]
        poly = [a, b, tip]
        d = org_poly(poly, seed + i, 0.5, 10, 2)
        out.append(paint(P, d, col, [lt(col, 0.3), dk(col, 0.2)], bbox(poly), seed + i, angle=-80, n=8, shade=dk(col, 0.4), shade_op=0.3, ink_c=ink_c, ink_w=1.5))
        if pattern == "dots":
            for k in range(3):
                f = 0.3 + 0.2 * k
                px, py = a[0] + (tip[0] - a[0]) * f * 0.5 + (b[0] - a[0]) * 0.5 * (1 - f * 0.5), a[1] + (tip[1] - a[1]) * f
                out.append(f'<circle cx="{_f(px)}" cy="{_f(py)}" r="2.6" fill="#FFF8EC" opacity="0.85"/>')
        elif pattern == "stars" and i % 2 == 0:
            out.append(f'<polygon points="{" ".join(f"{_f(px)},{_f(py)}" for px, py in star_pts(mx * 0.62 + tip[0] * 0.38, my * 0.62 + tip[1] * 0.38, size * 0.24, size * 0.1))}" fill="#FFF8EC"/>')
    return "".join(out)


def firework(P, cx, cy, r, col, seed, rays=22, glow=True, col2=None, dots=True, w=3.0):
    """A burst: soft glow, tapered streaks with bright tips, a ring of sparkle dots."""
    rnd = random.Random(seed)
    out = []
    if glow:
        out.append(P.glow(cx, cy, r * 1.3, col, 0.35))
    for i in range(rays):
        a = math.radians(i * 360 / rays + rnd.uniform(-5, 5))
        r0, r1 = r * rnd.uniform(0.18, 0.3), r * rnd.uniform(0.78, 1.0)
        x0, y0 = cx + math.cos(a) * r0, cy + math.sin(a) * r0
        x1, y1 = cx + math.cos(a) * r1, cy + math.sin(a) * r1 + r * 0.04
        c = col2 if (col2 and i % 3 == 0) else col
        nx, ny = -math.sin(a), math.cos(a)
        ww = w * rnd.uniform(0.7, 1.1)
        out.append(f'<path d="M {_f(x0)} {_f(y0)} Q {_f((x0 + x1) / 2 + nx * ww)} {_f((y0 + y1) / 2 + ny * ww)} {_f(x1)} {_f(y1)} Q {_f((x0 + x1) / 2 - nx * ww)} {_f((y0 + y1) / 2 - ny * ww)} {_f(x0)} {_f(y0)} Z" fill="{c}" opacity="{rnd.uniform(0.75, 1):.2f}"/>')
        out.append(f'<circle cx="{_f(x1)}" cy="{_f(y1)}" r="{_f(ww * 0.75)}" fill="{lt(c, 0.6)}"/>')
    if dots:
        for i in range(rays):
            a = math.radians(i * 360 / rays + 180 / rays)
            rr = r * rnd.uniform(0.5, 0.65)
            out.append(f'<circle cx="{_f(cx + math.cos(a) * rr)}" cy="{_f(cy + math.sin(a) * rr)}" r="{_f(w * 0.5)}" fill="{lt(col, 0.4)}" opacity="0.9"/>')
    out.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(w * 0.9)}" fill="#FFFFFF" opacity="0.9"/>')
    return "".join(out)


def confetti(seed, n, box, cols, avoid=(), s=(5, 11), curls=0.25):
    """Painted paper confetti: little tilted slips, dots and curls."""
    rnd = random.Random(seed)
    out = []
    tries = 0
    while len(out) < n and tries < n * 30:
        tries += 1
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        if any(a[0] < x < a[2] and a[1] < y < a[3] for a in avoid):
            continue
        c = rnd.choice(cols)
        k = rnd.random()
        sz = rnd.uniform(*s)
        if k < curls:
            out.append(f'<path d="M {_f(x)} {_f(y)} q {_f(sz * 0.5)} {_f(-sz * 0.7)} {_f(sz)} 0 t {_f(sz)} 0" stroke="{c}" stroke-width="{_f(max(1.6, sz * 0.28))}" fill="none" stroke-linecap="round" '
                       f'transform="rotate({rnd.uniform(0, 360):.0f} {_f(x)} {_f(y)})"/>')
        elif k < 0.7:
            out.append(f'<path d="{org_rect(x - sz / 2, y - sz * 0.22, sz, sz * 0.44, rnd.randint(1, 999), 0.3, 6, 0.8)}" fill="{c}" transform="rotate({rnd.uniform(0, 180):.0f} {_f(x)} {_f(y)})"/>')
        else:
            out.append(f'<path d="{blob(x, y, sz * 0.32, sz * 0.3, rnd.randint(1, 999), 0.08, 8)}" fill="{c}"/>')
    return "".join(out)


def sparkles(seed, n, box, col, r=(5, 10), op=(0.7, 1.0), avoid=()):
    rnd = random.Random(seed)
    out = []
    tries = 0
    while len(out) < n and tries < n * 40:
        tries += 1
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        if any(a[0] < x < a[2] and a[1] < y < a[3] for a in avoid):
            continue
        out.append(twinkle(x, y, rnd.uniform(*r), col, round(rnd.uniform(*op), 2)))
    return "".join(out)


def paper_bg(P, base="#F6EEDF", fleck="#8A6A4A", seed=5, blobs=None, tints=None):
    """Warm paper ground plus a few soft painted washes behind the subject."""
    out = [paper(P.id("pp"), base, fleck, seed)]
    if tints:
        out.append(mottle(seed, tints, 9, op=(0.05, 0.1)))
    for (cx, cy, rx, ry, col, op) in (blobs or []):
        d = blob(cx, cy, rx, ry, seed + int(cx), 0.1, 18)
        out.append(f'<path d="{d}" fill="{col}" opacity="{op}"/>')
        out.append(strokes(P.id("s"), d, (cx - rx, cy - ry, cx + rx, cy + ry), [lt(col, 0.3), dk(col, 0.08), col], seed + int(cy), int(rx * ry / 500), angle=-15,
                           length=(rx * 0.15, rx * 0.5), width=(3, 9), opacity=(0.06, 0.18), curve=0.15))
    return "".join(out)


def word_w(s, font, size, max_w, ls=0):
    w, sz = text_w(s, font, size, max_w, ls)
    return w, sz


# =============================================================== designs
# --------------------------------------------------------------- New Year
def flute(P, bx, by, rot, seed, scale=1.0, ink_c="#1A1830", fill=0.62):
    """Champagne flute standing on (bx, by), tilted rot degrees: glass, golden wine, rising bubbles, glints."""
    s = scale
    out = [f'<g transform="rotate({rot} {_f(bx)} {_f(by)})">']
    foot = blob(bx, by - 4 * s, 40 * s, 9 * s, seed, 0.02, 18)
    stem_d = smooth_closed([(bx - 4 * s, by - 6 * s), (bx - 3 * s, by - 60 * s), (bx - 6 * s, by - 92 * s), (bx + 6 * s, by - 92 * s), (bx + 3 * s, by - 60 * s), (bx + 4 * s, by - 6 * s)])
    top, rim_w = by - 268 * s, 36 * s
    bowl_pts = [(bx, by - 90 * s), (bx - 18 * s, by - 112 * s), (bx - 30 * s, by - 160 * s), (bx - 34 * s, by - 220 * s), (bx - rim_w, top),
                (bx + rim_w, top), (bx + 34 * s, by - 220 * s), (bx + 30 * s, by - 160 * s), (bx + 18 * s, by - 112 * s)]
    bowl = smooth_closed(bowl_pts)
    glass = "#EEF4F6"
    out.append(f'<path d="{foot}" fill="{glass}" opacity="0.8"/><path d="{stem_d}" fill="{glass}" opacity="0.85"/>')
    out.append(f'<path d="M {_f(bx - 1.5 * s)} {_f(by - 10 * s)} L {_f(bx - 1 * s)} {_f(by - 86 * s)}" stroke="#FFFFFF" stroke-width="{_f(1.6 * s)}" opacity="0.9"/>')
    out.append(f'<path d="{bowl}" fill="{glass}" opacity="0.22"/>')
    # the wine, clipped inside the bowl
    lvl = top + (by - 90 * s - top) * (1 - fill)
    cid = P.clip(f'<path d="{bowl}"/>')
    g = P.lg([(0, "#FBE6A0"), (0.5, "#F2C25A"), (1, "#D99A2E")])
    wine = [f'<rect x="{_f(bx - 50 * s)}" y="{_f(lvl)}" width="{_f(100 * s)}" height="{_f(by - lvl)}" fill="url(#{g})"/>',
            strokes(P.id("s"), f"M {_f(bx - 50 * s)} {_f(lvl)} H {_f(bx + 50 * s)} V {_f(by - 88 * s)} H {_f(bx - 50 * s)} Z", (bx - 40 * s, lvl, bx + 40 * s, by - 88 * s),
                    ["#FFF2C0", "#E8A83A", "#F6D27A"], seed, 26, angle=-90, length=(20 * s, 60 * s), width=(1.5 * s, 4 * s), opacity=(0.2, 0.5)),
            f'<path d="M {_f(bx - 50 * s)} {_f(lvl)} q {_f(25 * s)} {_f(-5 * s)} {_f(50 * s)} 0 t {_f(50 * s)} 0 l 0 {_f(7 * s)} l {_f(-100 * s)} 0 Z" fill="#FFF6DA" opacity="0.85"/>']
    rnd = random.Random(seed)
    for _ in range(26):
        yy = rnd.uniform(lvl + 8 * s, by - 100 * s)
        half = 30 * s * min(1, (by - 90 * s - yy) / (70 * s) + 0.2)
        wob = rnd.uniform(-0.7, 0.7) * half
        rr = rnd.uniform(1.1, 2.8) * s
        wine.append(f'<circle cx="{_f(bx + wob)}" cy="{_f(yy)}" r="{_f(rr)}" fill="none" stroke="#FFFBEA" stroke-width="{_f(max(0.8, rr * 0.5))}" opacity="0.85"/>')
    wine.append(f'<rect x="{_f(bx + 6 * s)}" y="{_f(lvl)}" width="{_f(40 * s)}" height="{_f(by - lvl)}" fill="#8A4A10" opacity="0.18"/>')
    out.append(f'<g clip-path="url(#{cid})">{"".join(wine)}</g>')
    # glints on the glass
    out.append(f'<path d="M {_f(bx - 22 * s)} {_f(top + 20 * s)} q {_f(-6 * s)} {_f(70 * s)} {_f(2 * s)} {_f(130 * s)}" stroke="#FFFFFF" stroke-width="{_f(5 * s)}" fill="none" stroke-linecap="round" opacity="0.75"/>')
    out.append(f'<path d="M {_f(bx + 24 * s)} {_f(top + 40 * s)} q {_f(4 * s)} {_f(40 * s)} 0 {_f(70 * s)}" stroke="#FFFFFF" stroke-width="{_f(2.4 * s)}" fill="none" stroke-linecap="round" opacity="0.5"/>')
    out.append(f'<path d="M {_f(bx - 30 * s)} {_f(by - 6 * s)} q {_f(30 * s)} {_f(-8 * s)} {_f(60 * s)} 0" stroke="#FFFFFF" stroke-width="{_f(2.4 * s)}" fill="none" stroke-linecap="round" opacity="0.6"/>')
    # rim ellipse + ink lines
    out.append(f'<path d="{blob(bx, top, rim_w, 6 * s, seed + 3, 0.02, 16)}" fill="#FFFFFF" opacity="0.25"/>')
    out.append(ink(f'M {_f(bx - rim_w)} {_f(top)} A {_f(rim_w)} {_f(6 * s)} 0 0 0 {_f(bx + rim_w)} {_f(top)}', ink_c, 1.6 * s, seed, 1, 0.5))
    out.append(ink(f'M {_f(bx - rim_w)} {_f(top)} A {_f(rim_w)} {_f(6 * s)} 0 0 1 {_f(bx + rim_w)} {_f(top)}', ink_c, 1.4 * s, seed, 1, 0.35))
    out.append(ink(bowl, ink_c, 2.2 * s, seed, 2, 0.75) + ink(stem_d, ink_c, 1.6 * s, seed + 1, 1, 0.6) + ink(foot, ink_c, 1.8 * s, seed + 2, 2, 0.7))
    out.append("</g>")
    return "".join(out)


def streamer(P, pts, w, col, seed, ink_c=INK, twist=None):
    """A paper streamer: a flat band that twists, so it narrows and flips between its light face and its darker back."""
    pts = [p for p in pts]
    if len(pts) < 8:
        # resample the smooth path for a finer twist
        fine = []
        for i in range(len(pts) - 1):
            p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
            p3 = pts[min(i + 2, len(pts) - 1)]
            for k in range(10):
                t = k / 10
                t2, t3 = t * t, t * t * t
                fine.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
        fine.append(pts[-1])
        pts = fine
    twist = twist or max(4, len(pts) / 7)
    out = []
    n = len(pts)
    for i in range(n - 1):
        ph = math.sin(2 * math.pi * i / twist + seed)
        ww = w * (0.28 + 0.72 * abs(ph))
        c = lt(col, 0.18) if ph > 0 else dk(col, 0.28)
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        out.append(f'<path d="M {_f(x0)} {_f(y0)} L {_f(x1)} {_f(y1)}" stroke="{c}" stroke-width="{_f(ww)}" stroke-linecap="round"/>')
    edge = smooth_open(pts)
    return (f'<path d="{edge}" stroke="{dk(col, 0.45)}" stroke-width="{_f(w + 2)}" fill="none" stroke-linecap="round" opacity="0.35"/>'
            + "".join(out)
            + f'<path d="{edge}" stroke="{lt(col, 0.6)}" stroke-width="{_f(max(0.8, w * 0.18))}" fill="none" stroke-linecap="round" opacity="0.5" transform="translate(-0.8 -1)"/>')


def curl_pts(x, y, L, turns, r, ang, seed, drift=1.0):
    """Spiral curl (party streamer) as point list."""
    rnd = random.Random(seed)
    a0 = math.radians(ang)
    out = []
    n = int(turns * 16)
    for i in range(n + 1):
        t = i / n
        th = t * turns * 2 * math.pi
        cx_, cy_ = x + math.cos(a0) * L * t, y + math.sin(a0) * L * t
        rr = r * (0.6 + 0.4 * math.sin(math.pi * t)) * drift
        out.append((cx_ + math.cos(th) * rr + rnd.uniform(-0.5, 0.5), cy_ + math.sin(th) * rr * 0.6))
    return out


def cheers():
    """Midnight: two champagne flutes clink, a golden splash leaps up, confetti and paper curls drift down."""
    P = Pn("cheers")
    o = [sky_wash(P, "#18203E", "#2C3A6A", ["#22305A", "#34447A", "#1A2246", "#3E4E86"], 11, n=300, angle=-6, mid=(0.6, "#243262"))]
    o.append(mottle(12, ["#4A5A9A", "#101830"], 10))
    o.append(P.glow(300, 400, 300, "#F6C860", 0.32))
    # far city-glitter bokeh
    rnd = random.Random(13)
    for _ in range(16):
        x, y, r = rnd.uniform(40, 560), rnd.uniform(280, 500), rnd.uniform(14, 30)
        o.append(P.glow(x, y, r, rnd.choice([GOLD_L, "#F6C860", "#F4A78E"]), rnd.uniform(0.25, 0.45)))
    # paper curls drifting in from the edges
    o.append(streamer(P, curl_pts(28, 270, 150, 3.0, 16, 95, 14), 7, CORAL, 14, twist=16))
    o.append(streamer(P, curl_pts(572, 262, 160, 3.2, 16, 85, 15), 7, GOLD, 15, twist=16))
    o.append(streamer(P, curl_pts(70, 420, 110, 2.2, 13, 100, 16), 6, "#8FC8C0", 16, twist=16))
    o.append(streamer(P, curl_pts(532, 430, 100, 2.0, 13, 80, 17), 6, CORAL_L, 17, twist=16))
    o.append(confetti(18, 70, (20, 20, 580, 580), [GOLD, GOLD_L, CORAL, "#8FC8C0", "#FFFFFF", CORAL_L], avoid=((70, 40, 530, 252), (170, 250, 430, 560))))
    # table edge, lit warm by the candles off-frame
    tbl = org_poly([(-10, 522), (610, 518), (610, 610), (-10, 610)], 19, 1, 30, 2)
    o.append(paint(P, tbl, "#4A3450", ["#5A4260", "#2E2038", "#6A4E6A", "#7A5A5A"], (-10, 518, 610, 610), 19, angle=0, n=90, length=(40, 120), width=(2, 5), ink_c=None))
    o.append(f'<path d="{hline(-10, 522, 610, 518, 20, 0.6)}" stroke="#F6C860" stroke-width="2.4" fill="none" opacity="0.55"/>')
    o.append(cast(300, 530, 170, 10, "#000000", 0.35, 21))
    # flutes (right one in front), rims just touching
    o.append(flute(P, 208, 530, 14.5, 22, 0.93))
    o.append(flute(P, 392, 530, -14.5, 23, 0.93))
    # splash where the rims meet
    sx, sy = 300, 286
    o.append(P.glow(sx, sy, 80, "#FFE7A0", 0.6))
    for k, (dx, dy, r) in enumerate(((-30, -14, 5.5), (-14, -26, 4.5), (4, -32, 6), (22, -22, 4.5), (38, -8, 4), (-46, 0, 3.2), (52, 4, 3), (10, -10, 3))):
        o.append(f'<path d="{blob(sx + dx, sy + dy, r, r * 1.3, 24 + k, 0.08, 10)}" fill="#F6D27A" stroke="#8A5A14" stroke-width="1.2"/>'
                 f'<circle cx="{_f(sx + dx - r * 0.3)}" cy="{_f(sy + dy - r * 0.4)}" r="{_f(r * 0.32)}" fill="#FFFFFF" opacity="0.9"/>')
    o.append(twinkle(sx, sy + 4, 18, "#FFFFFF", 0.95) + twinkle(sx - 92, sy + 10, 8, GOLD_L) + twinkle(sx + 96, sy + 18, 7, GOLD_L))
    # lettering
    o.append(btext(P, 300, 168, "cheers", SERIF_IT, 168, GOLD, [GOLD_L, GOLD_D, "#F2C25A", "#FFF0B8"], 25, max_w=440, shadow="#0E1428", sh=(0.02, 0.035), hi="#FFF6D8"))
    o.append(flank(222, "TO THE NEW YEAR", BEBAS, 40, 9, "#F6EEDF", max_w=360, L=46, seed=26))
    o.append(ptext(300, 236, "TO THE NEW YEAR", BEBAS, 40, "#F6EEDF", max_w=360, ls=9))
    return finish(P, "".join(o), 27)


def clock_face(P, cx, cy, r, seed):
    """Gilded mantel-clock face at midnight: Roman numerals, minute ticks, both hands at XII."""
    out = [cast(cx + 10, cy + r + 14, r * 0.9, 12, "#3A2418", 0.3, seed)]
    # case: scalloped gold bezel
    pts = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        rr = r * (1.0 + (0.035 if i % 2 else 0))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    case = smooth_closed(pts)
    out.append(paint(P, case, GOLD, [GOLD_L, GOLD_D, "#F2C25A", "#FFF0B8"], (cx - r, cy - r, cx + r, cy + r), seed, angle=-45, n=90, length=(r * 0.1, r * 0.3),
                     width=(1, 3), curve=0.6, shade=GOLD_D, shade_op=0.6, light="#FFF6D8", light_op=0.5, ink_c=INK, ink_w=2.4))
    # bow / crown on top
    for sg in (-1, 1):
        lp = smooth_closed([(cx, cy - r * 1.05), (cx + sg * r * 0.22, cy - r * 1.28), (cx + sg * r * 0.34, cy - r * 1.14), (cx + sg * r * 0.14, cy - r * 1.0)])
        out.append(paint(P, lp, GOLD, [GOLD_L, GOLD_D], (cx - r * 0.4, cy - r * 1.3, cx + r * 0.4, cy - r), seed + sg, n=5, ink_c=INK, ink_w=1.8))
    out.append(ball_paint(P, cx, cy - r * 1.05, r * 0.08, GOLD, seed + 4))
    face = blob(cx, cy, r * 0.84, r * 0.84, seed + 5, 0.005, 36)
    g = P.rg([(0, "#FFFDF6"), (0.75, "#F7EEDD"), (1, "#E2D2B4")], cx=0.45, cy=0.42, r=0.6)
    out.append(f'<path d="{face}" fill="url(#{g})"/>')
    out.append(strokes(P.id("s"), face, (cx - r, cy - r, cx + r, cy + r), ["#FFFFFF", "#EADCC2"], seed + 6, 40, angle=-30, length=(r * 0.2, r * 0.5), width=(2, 5), opacity=(0.15, 0.35)))
    out.append(ink(face, INK, 2.2, seed + 5, 2, 0.8))
    out.append(ink(blob(cx, cy, r * 0.7, r * 0.7, seed + 7, 0.004, 36), GOLD_D, 1.3, seed + 7, 1, 0.6))
    for i in range(60):
        a = math.radians(i * 6 - 90)
        r0 = r * (0.7 if i % 5 == 0 else 0.74)
        out.append(f'<path d="M {_f(cx + math.cos(a) * r0)} {_f(cy + math.sin(a) * r0)} L {_f(cx + math.cos(a) * r * 0.79)} {_f(cy + math.sin(a) * r * 0.79)}" '
                   f'stroke="{INK}" stroke-width="{2.6 if i % 5 == 0 else 1.2}" stroke-linecap="round" opacity="0.85"/>')
    for i, num in enumerate(["XII", "I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "IX", "X", "XI"]):
        a = math.radians(i * 30 - 90)
        x, y = cx + math.cos(a) * r * 0.56, cy + math.sin(a) * r * 0.56
        sz = r * (0.17 if i % 3 == 0 else 0.12)
        out.append(f'<text x="{_f(x)}" y="{_f(y + sz * 0.36)}" text-anchor="middle" {CINZEL} font-size="{_f(sz)}" fill="{NAVY if i % 3 else CRAN}" '
                   f'transform="rotate({i * 30 if i not in (0,) else 0} {_f(x)} {_f(y)})">{num}</text>')
    # hands at midnight (hour slightly shorter & wider)
    for L, w, col in ((r * 0.42, 9, NAVY_D), (r * 0.66, 5, NAVY)):
        hp = smooth_closed([(cx - w / 2, cy + 8), (cx - w * 0.3, cy - L * 0.7), (cx - w, cy - L * 0.78), (cx, cy - L), (cx + w, cy - L * 0.78), (cx + w * 0.3, cy - L * 0.7), (cx + w / 2, cy + 8)])
        out.append(f'<path d="{hp}" fill="{col}"/>')
    out.append(ball_paint(P, cx, cy, 8, GOLD, seed + 9))
    out.append(f'<path d="M {_f(cx - r * 0.5)} {_f(cy - r * 0.45)} Q {_f(cx - r * 0.6)} {_f(cy)} {_f(cx - r * 0.45)} {_f(cy + r * 0.4)}" stroke="#FFFFFF" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.4"/>')
    return "".join(out)


def party_horn(P, x, y, L, ang, col, stripe, seed):
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    pts = [(x + nx * 4, y + ny * 4), (x + ux * L + nx * 15, y + uy * L + ny * 15), (x + ux * L * 1.03, y + uy * L * 1.03), (x + ux * L - nx * 15, y + uy * L - ny * 15), (x - nx * 4, y - ny * 4)]
    d = org_poly(pts, seed, 0.5, 10, 2)
    out = [paint(P, d, col, [lt(col, 0.3), dk(col, 0.2)], bbox(pts), seed, angle=ang, n=10, shade=dk(col, 0.4), shade_op=0.35, ink_c=None)]
    cid = P.clip(f'<path d="{d}"/>')
    st = "".join(f'<path d="M {_f(x + ux * L * f - nx * 30)} {_f(y + uy * L * f - ny * 30)} L {_f(x + ux * L * (f + 0.12) + nx * 30)} {_f(y + uy * L * (f + 0.12) + ny * 30)}" stroke="{stripe}" stroke-width="5"/>' for f in (0.1, 0.3, 0.5, 0.7, 0.9))
    out.append(f'<g clip-path="url(#{cid})">{st}</g>')
    out.append(ink(d, INK, 1.8, seed, 2, 0.75))
    # mouthpiece and fringe
    out.append(f'<path d="{org_rect(x - 10, y - 4, 12, 8, seed, 0.3, 6, 1)}" fill="{GOLD}" stroke="{INK}" stroke-width="1.2" transform="rotate({ang} {_f(x)} {_f(y)})"/>')
    ex, ey = x + ux * L, y + uy * L
    rnd = random.Random(seed)
    for k in range(9):
        t = -1 + k / 4
        bx, by = ex + nx * 15 * t, ey + ny * 15 * t
        out.append(f'<path d="M {_f(bx)} {_f(by)} l {_f(ux * rnd.uniform(10, 16) + nx * rnd.uniform(-3, 3))} {_f(uy * rnd.uniform(10, 16) + ny * rnd.uniform(-3, 3))}" stroke="{rnd.choice([GOLD_L, CORAL_L, "#FFFFFF"])}" stroke-width="2.2" stroke-linecap="round"/>')
    return "".join(out)


def happy_new_year():
    """A gilded clock strikes midnight, wrapped in paper streamers, a party horn and confetti on warm paper."""
    P = Pn("happy-new-year")
    o = [paper_bg(P, "#F6EEDF", seed=31, tints=["#E8D6B8", "#FFFFFF"], blobs=[(300, 410, 230, 170, "#BFDCD6", 0.55), (300, 400, 160, 120, "#F4D9B0", 0.35)])]
    o.append(confetti(32, 60, (30, 30, 570, 570), [TEAL, CORAL, GOLD, NAVY, CORAL_L, "#8FC8C0"], avoid=((60, 30, 540, 250), (170, 270, 430, 560))))
    o.append(clock_face(P, 300, 412, 118, 33))
    # streamers looping around the clock
    o.append(streamer(P, curl_pts(150, 500, 60, 1.6, 12, 160, 34), 6, TEAL, 34, twist=16))
    o.append(streamer(P, curl_pts(450, 500, 60, 1.6, 12, 20, 35), 6, CORAL, 35, twist=16))
    o.append(streamer(P, curl_pts(86, 280, 120, 2.6, 15, 90, 36), 6, GOLD, 36, twist=16))
    o.append(streamer(P, curl_pts(514, 280, 120, 2.6, 15, 90, 37), 6, TEAL_L, 37, twist=16))
    o.append(party_horn(P, 120, 452, 70, -30, CORAL, "#FFF6E8", 38))
    o.append(party_horn(P, 480, 452, 70, 210, TEAL, GOLD_L, 39))
    o.append(sparkles(40, 8, (70, 260, 530, 560), GOLD, (6, 11), avoid=((170, 280, 430, 540),)))
    o.append(btext(P, 300, 112, "happy", SERIF_IT, 96, CORAL_D, [CORAL, CORAL_D, "#C85A44", CORAL_L], 41, max_w=360, shadow="#E8CFA8", sh=(0.02, 0.03), hi="#FFD8C8"))
    o.append(btext(P, 300, 250, "NEW YEAR", ANTON, 112, TEAL_D, [TEAL, TEAL_D, "#245A60", TEAL_L], 42, ls=4, max_w=450, shadow=GOLD, sh=(0.025, 0.035), hi="#9CC8C4"))
    return finish(P, "".join(o), 43)


# --------------------------------------------------------------- Valentine's & Galentine's
def brush_x(P, cx, cy, s, col, seed):
    """An X painted with two loaded brush strokes."""
    out = []
    rnd = random.Random(seed)
    for k, (a, b) in enumerate((((-1, -1), (1, 1)), ((1, -1), (-1, 1)))):
        x0, y0 = cx + a[0] * s, cy + a[1] * s
        x1, y1 = cx + b[0] * s, cy + b[1] * s
        ang = math.atan2(y1 - y0, x1 - x0)
        nx, ny = -math.sin(ang), math.cos(ang)
        w0, w1 = s * 0.3, s * 0.16
        mx, my = (x0 + x1) / 2 + nx * rnd.uniform(-3, 3), (y0 + y1) / 2 + ny * rnd.uniform(-3, 3)
        d = (f"M {_f(x0 + nx * w0 * 0.5)} {_f(y0 + ny * w0 * 0.5)} Q {_f(mx + nx * w0)} {_f(my + ny * w0)} {_f(x1 + nx * w1 * 0.4)} {_f(y1 + ny * w1 * 0.4)} "
             f"L {_f(x1 - nx * w1 * 0.4)} {_f(y1 - ny * w1 * 0.4)} Q {_f(mx - nx * w0 * 0.7)} {_f(my - ny * w0 * 0.7)} {_f(x0 - nx * w0 * 0.5)} {_f(y0 - ny * w0 * 0.5)} Z")
        out.append(paint(P, d, col, [lt(col, 0.3), dk(col, 0.25)], (cx - s, cy - s, cx + s, cy + s), seed + k, angle=math.degrees(ang), n=10,
                         length=(s * 0.4, s), width=(1, s * 0.06), ink_c=None))
    return "".join(out)


def pencil(P, x, y, L, ang, seed, body="#E8B83A", w=18, ink_c=INK, lead=INK):
    """Wooden pencil: painted hexagon-faceted body, ferrule, eraser, sharpened cone."""
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    def Q(t, k):
        return (x + ux * t + nx * k, y + uy * t + ny * k)
    h = w / 2
    out = [cast(x + ux * L * 0.5 + 6, y + uy * L * 0.5 + 10, L * 0.5, w * 0.4, "#3A2418", 0.25, seed)]
    pts = [Q(0, -h), Q(L * 0.78, -h), Q(L * 0.78, h), Q(0, h)]
    d = org_poly(pts, seed, 0.4, 20, 1)
    out.append(paint(P, d, body, [lt(body, 0.3), dk(body, 0.15)], bbox(pts), seed, angle=ang, n=14, ink_c=None))
    for k, op in ((-h * 0.33, 0.0), (h * 0.33, 0.25)):
        out.append(f'<path d="M {_f(Q(2, k)[0])} {_f(Q(2, k)[1])} L {_f(Q(L * 0.78, k)[0])} {_f(Q(L * 0.78, k)[1])}" stroke="{dk(body, 0.3)}" stroke-width="1.2" opacity="0.6"/>')
    side = [Q(0, h * 0.33), Q(L * 0.78, h * 0.33), Q(L * 0.78, h), Q(0, h)]
    out.append(f'<path d="{org_poly(side, seed + 1, 0.3, 20, 1)}" fill="{dk(body, 0.3)}" opacity="0.35"/>')
    out.append(f'<path d="M {_f(Q(4, -h * 0.66)[0])} {_f(Q(4, -h * 0.66)[1])} L {_f(Q(L * 0.76, -h * 0.66)[0])} {_f(Q(L * 0.76, -h * 0.66)[1])}" stroke="#FFFFFF" stroke-width="2" opacity="0.5"/>')
    out.append(ink(d, ink_c, 1.6, seed, 2, 0.7))
    # cone + lead
    cone = [Q(L * 0.78, -h), Q(L, 0), Q(L * 0.78, h)]
    cd = org_poly(cone, seed + 2, 0.3, 10, 1)
    out.append(paint(P, cd, "#F2D6A8", ["#E8C08A", "#FFF0D0"], bbox(cone), seed + 2, angle=ang, n=6, ink_c=ink_c, ink_w=1.4))
    tip = [Q(L * 0.92, -h * 0.36), Q(L, 0), Q(L * 0.92, h * 0.36)]
    out.append(f'<path d="M {" L ".join(f"{_f(px)} {_f(py)}" for px, py in tip)} Z" fill="{lead}"/>')
    # ferrule + eraser at the back end
    fer = [Q(-w * 0.9, -h * 1.02), Q(0, -h * 1.02), Q(0, h * 1.02), Q(-w * 0.9, h * 1.02)]
    out.append(paint(P, org_poly(fer, seed + 3, 0.3, 8, 1), "#C8C2B2", ["#E8E4DA", "#9A9282"], bbox(fer), seed + 3, angle=ang + 90, n=6, ink_c=ink_c, ink_w=1.4))
    for t in (-w * 0.65, -w * 0.3):
        out.append(f'<path d="M {_f(Q(t, -h)[0])} {_f(Q(t, -h)[1])} L {_f(Q(t, h)[0])} {_f(Q(t, h)[1])}" stroke="#7A7262" stroke-width="1.4"/>')
    er = [Q(-w * 1.9, -h), Q(-w * 0.9, -h), Q(-w * 0.9, h), Q(-w * 1.9, h)]
    out.append(paint(P, org_poly(er, seed + 4, 0.4, 8, w * 0.3), "#E88A8A", ["#F4B0A8", "#C86060"], bbox(er), seed + 4, angle=ang, n=5, ink_c=ink_c, ink_w=1.4))
    return "".join(out)


def xoxo():
    """A tic-tac-toe game played in hearts and kisses, the winning line drawn straight through the hearts."""
    P = Pn("xoxo")
    o = [paper_bg(P, "#F8DCD6", "#9A4A4A", 51, tints=["#F2C4C0", "#FFFFFF"], blobs=[(300, 352, 200, 170, "#FBEAE4", 0.7)])]
    rnd = random.Random(52)
    for i in range(26):
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 580)
        if 90 < x < 510 and 60 < y < 540:
            continue
        o.append(f'<path d="{heart_d(x, y, rnd.uniform(6, 11), rnd.uniform(-20, 20), i)}" fill="{rnd.choice([ROSE, "#FFFFFF", CRAN])}" opacity="{rnd.uniform(0.35, 0.7):.2f}"/>')
    # grid
    gx, gy, c = 300, 344, 80
    for k in (-0.5, 0.5):
        o.append(ink(hline(gx + k * c, gy - 1.55 * c, gx + k * c + 3, gy + 1.55 * c, 53 + int(k * 4), 2.2, 22), "#6E1E2A", 7, 53, 2, 0.9))
        o.append(ink(hline(gx - 1.55 * c, gy + k * c, gx + 1.55 * c, gy + k * c - 3, 55 + int(k * 4), 2.2, 22), "#6E1E2A", 7, 55, 2, 0.9))
    board = {(0, 0): "h", (1, 1): "h", (2, 2): "h", (0, 2): "h", (1, 0): "x", (2, 0): "x", (0, 1): "x"}
    for (cx_, cy_), v in board.items():
        px, py = gx + (cx_ - 1) * c, gy + (cy_ - 1) * c
        if v == "h":
            o.append(p_heart(P, px, py + 2, c * 0.36, RED, 60 + cx_ * 3 + cy_, rot=rnd.uniform(-10, 10)))
        else:
            o.append(brush_x(P, px, py, c * 0.3, "#6A2A6E", 70 + cx_ * 3 + cy_))
    # the winning line, painted with one confident stroke
    x0, y0, x1, y1 = gx - 1.35 * c, gy - 1.3 * c, gx + 1.38 * c, gy + 1.33 * c
    d = f"M {_f(x0)} {_f(y0)} Q {_f(gx + 4)} {_f(gy - 8)} {_f(x1)} {_f(y1)}"
    o.append(f'<path d="{d}" stroke="{ROSE}" stroke-width="11" fill="none" stroke-linecap="round" opacity="0.85"/>'
             f'<path d="{d}" stroke="#F49AA4" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.8" transform="translate(-1.5 -2)"/>'
             f'<path d="{d}" stroke="#A8303E" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.6" transform="translate(1.5 3)"/>')
    o.append(pencil(P, 520, 300, 96, 118, 80, body=ROSE, w=16))
    o.append(sparkles(81, 5, (80, 230, 520, 470), GOLD, (6, 10), avoid=((170, 210, 430, 470),)))
    o.append(btext(P, 300, 182, "XOXO", BEBAS, 176, CRAN, [RED, RED_D, "#B03040", RED_L], 82, ls=14, max_w=430, shadow="#E8B0AA", sh=(0.025, 0.035), hi="#F6C0B8"))
    o.append(btext(P, 300, 532, "with love", SERIF_IT, 64, "#6E1E2A", ["#8E2E3A", "#5A1420", ROSE], 83, max_w=300, shadow="#F2C4C0", sh=(0.02, 0.03)))
    return finish(P, "".join(o), 84)


def wax_seal(P, cx, cy, r, col, seed, emboss="heart"):
    rnd = random.Random(seed)
    pts = []
    for i in range(22):
        a = 2 * math.pi * i / 22
        rr = r * (1 + rnd.uniform(-0.08, 0.1) + (0.12 if i % 5 == 0 else 0))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    d = smooth_closed(pts)
    out = [cast(cx + 3, cy + 5, r * 1.05, r * 0.9, "#2A0A10", 0.3, seed)]
    out.append(paint(P, d, col, [lt(col, 0.25), dk(col, 0.3)], (cx - r, cy - r, cx + r, cy + r), seed, angle=-50, n=10, shade=dk(col, 0.5), shade_op=0.5, ink_c=INK, ink_w=1.6))
    inner = blob(cx, cy, r * 0.72, r * 0.72, seed + 1, 0.02, 18)
    out.append(f'<path d="{inner}" fill="{dk(col, 0.2)}"/>'
               f'<path d="{inner}" fill="none" stroke="{lt(col, 0.35)}" stroke-width="1.6" opacity="0.7" transform="translate(-1 -1)"/>')
    if emboss == "heart":
        hd = heart_d(cx, cy + 1, r * 0.4, 0, seed)
        out.append(f'<path d="{hd}" fill="{dk(col, 0.35)}" transform="translate(1.2 1.6)"/><path d="{hd}" fill="{lt(col, 0.15)}"/>')
    out.append(f'<path d="M {_f(cx - r * 0.6)} {_f(cy - r * 0.3)} Q {_f(cx - r * 0.5)} {_f(cy - r * 0.7)} {_f(cx - r * 0.1)} {_f(cy - r * 0.78)}" stroke="#FFFFFF" stroke-width="2.4" fill="none" stroke-linecap="round" opacity="0.45"/>')
    return "".join(out)


def be_my_valentine():
    """A love letter sealed with a red wax heart, a garden rose tucked under the flap, on deep valentine red."""
    P = Pn("be-my-valentine")
    o = [sky_wash(P, "#B42A38", "#7A1422", ["#C23A48", "#962030", "#A82636", "#D04A58"], 91, n=300, angle=-12, mid=(0.5, "#A22232"))]
    o.append(mottle(92, ["#E25A68", "#5A0A16"], 12))
    rnd = random.Random(93)
    for row in range(7):
        for col_ in range(7):
            x, y = col_ * 92 + (46 if row % 2 else 0) - 6, row * 90 + 20
            o.append(f'<path d="{heart_d(x, y, 10, rnd.uniform(-15, 15), row * 7 + col_)}" fill="#F6B8B8" opacity="0.13"/>')
    o.append(P.glow(300, 420, 260, "#FF9A9A", 0.3))
    # card peeking out behind the envelope
    ex0, ey0, ew, eh = 142, 318, 316, 196
    card = org_rect(ex0 + 30, ey0 - 50, ew - 60, 120, 94, 0.8, 14, 2)
    o.append(paint(P, card, "#F9E0DA", ["#FFFFFF", "#F2C4C0"], (ex0 + 30, ey0 - 50, ex0 + ew - 30, ey0 + 70), 94, angle=-10, n=14, ink_c=INK, ink_w=1.8))
    o.append(f'<text x="{ex0 + ew / 2 - 52}" y="{ey0 - 16}" {SERIF_IT} font-size="30" fill="{CRAN}" transform="rotate(-4 {ex0 + ew / 2} {ey0 - 16})">xo, me</text>')
    o.append(p_heart(P, ex0 + ew / 2 + 74, ey0 - 26, 13, RED, 95, rot=12, n=6))
    # envelope (back view, flaps)
    o.append(cast(300 + 12, ey0 + eh + 4, ew * 0.55, 14, "#2A0A10", 0.45, 96))
    env = org_rect(ex0, ey0, ew, eh, 97, 0.9, 16, 3)
    o.append(paint(P, env, "#F6E8D6", ["#FFF6EA", "#E8D2B8", "#F2DEC6"], (ex0, ey0, ex0 + ew, ey0 + eh), 97, angle=-80, n=60, ink_c=INK, ink_w=2.2,
                   shade="#B89A80", shade_op=0.35, shade_dir=(0, 0, 0, 1)))
    # side and bottom flaps
    left = org_poly([(ex0, ey0 + 4), (ex0 + ew * 0.46, ey0 + eh * 0.58), (ex0, ey0 + eh - 2)], 98, 0.6, 14, 2)
    right = org_poly([(ex0 + ew, ey0 + 4), (ex0 + ew * 0.54, ey0 + eh * 0.58), (ex0 + ew, ey0 + eh - 2)], 99, 0.6, 14, 2)
    bottom = org_poly([(ex0 + 2, ey0 + eh), (ex0 + ew / 2, ey0 + eh * 0.46), (ex0 + ew - 2, ey0 + eh)], 100, 0.6, 14, 2)
    for k, d_ in enumerate((left, right, bottom)):
        o.append(f'<path d="{d_}" fill="{["#EEDCC6", "#E8D2BA", "#F2E2CE"][k]}"/>')
        o.append(strokes(P.id("s"), d_, (ex0, ey0, ex0 + ew, ey0 + eh), ["#FFF6EA", "#DCC4A8"], 101 + k, 18, angle=-70 + k * 50, length=(20, 50), width=(2, 4), opacity=(0.2, 0.4)))
        o.append(ink(d_, INK, 1.6, 101 + k, 1, 0.55))
    # rose tucked in at lower left with leaves
    o.append(stem(P, [(196, 486), (260, 452), (330, 428)], LEAF_D, 5, 103, INK))
    o.append(p_leaf(P, 226, 470, 52, -150, LEAF, 104, 0.34))
    o.append(p_leaf(P, 250, 460, 46, 60, LEAF_L, 105, 0.34))
    o.append(p_leaf(P, 300, 440, 40, -60, LEAF, 106, 0.34))
    # top flap with the seal
    top = org_poly([(ex0 - 2, ey0 + 2), (ex0 + ew + 2, ey0 + 2), (ex0 + ew / 2, ey0 + eh * 0.62)], 107, 0.6, 14, 3)
    o.append(f'<path d="{top}" fill="#2A0A10" opacity="0.18" transform="translate(0 5)"/>')
    o.append(paint(P, top, "#FAEEDF", ["#FFFFFF", "#EADAC4"], (ex0, ey0, ex0 + ew, ey0 + eh * 0.62), 107, angle=-20, n=26, ink_c=INK, ink_w=2.0))
    o.append(peony(P, 190, 488, 40, ROSE, 108, rot=10))
    o.append(blossom(P, 236, 506, 13, 109, col="#FBD8DC"))
    o.append(wax_seal(P, ex0 + ew / 2, ey0 + eh * 0.6, 32, "#B8202E", 110))
    for k, (hx, hy, hs, hr) in enumerate(((470, 300, 15, 14), (500, 252, 10, -10), (122, 286, 12, -16), (98, 240, 8, 10))):
        o.append(p_heart(P, hx, hy, hs, "#F6B8B8" if k % 2 else "#FBE0DC", 111 + k, rot=hr, ink_c="#6E1420", n=5))
    o.append(btext(P, 300, 118, "be my", SERIF_IT, 96, "#FBEDE4", ["#FFFFFF", "#F6D8D0", "#F2C4C0"], 115, max_w=300, shadow="#5A0A16", sh=(0.02, 0.035)))
    o.append(btext(P, 300, 232, "VALENTINE", BEBAS, 124, "#FBEDE4", ["#FFFFFF", "#F6D8D0", "#F2C4C0", "#FBE0DC"], 116, ls=8, max_w=460, shadow="#5A0A16", sh=(0.02, 0.035), hi="#FFFFFF"))
    return finish(P, "".join(o), 117)


def chocolate(P, cx, cy, r, seed, kind, cup="#5A2E1A"):
    """A bonbon in a fluted paper cup, seen from above, with its own topping."""
    rnd = random.Random(seed)
    out = []
    pts = []
    for i in range(28):
        a = 2 * math.pi * i / 28
        rr = r * (1.18 if i % 2 else 1.08)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.92))
    cd = smooth_closed(pts)
    out.append(f'<path d="{cd}" fill="{cup}"/>'
               + "".join(f'<path d="M {_f(cx + math.cos(a) * r * 0.9)} {_f(cy + math.sin(a) * r * 0.83)} L {_f(cx + math.cos(a) * r * 1.16)} {_f(cy + math.sin(a) * r * 1.06)}" stroke="{lt(cup, 0.3)}" stroke-width="1.3"/>'
                         for a in [2 * math.pi * i / 14 for i in range(14)])
               + ink(cd, INK, 1.2, seed, 1, 0.6))
    choc = {"dark": "#4A2414", "milk": "#8A5232", "white": "#F4E6CC", "pink": "#E89AA6"}
    base = choc.get(kind if kind in choc else "milk", "#6A361E")
    if kind == "heart":
        d = heart_d(cx, cy, r * 0.95, 0, seed)
        base = "#C2283A"
    else:
        d = blob(cx, cy, r * 0.92, r * 0.86, seed, 0.03, 16)
    g = P.rg([(0, lt(base, 0.35)), (0.6, base), (1, dk(base, 0.35))], cx=0.38, cy=0.36, r=0.7)
    out.append(f'<path d="{d}" fill="url(#{g})"/>')
    out.append(strokes(P.id("s"), d, (cx - r, cy - r, cx + r, cy + r), [lt(base, 0.3), dk(base, 0.2)], seed, 8, angle=-40, length=(r * 0.4, r), width=(1, r * 0.1), opacity=(0.2, 0.45), curve=0.5))
    if kind == "dark":
        for k in range(4):
            yy = cy - r * 0.45 + k * r * 0.3
            out.append(f'<path d="M {_f(cx - r * 0.6)} {_f(yy)} q {_f(r * 0.3)} {_f(-r * 0.2)} {_f(r * 0.6)} 0 t {_f(r * 0.6)} 0" stroke="#C88A5A" stroke-width="1.8" fill="none" opacity="0.9"/>')
    elif kind == "milk":
        out.append(f'<path d="{blob(cx, cy, r * 0.32, r * 0.22, seed + 1, 0.1, 10)}" fill="#E8C08A" stroke="{INK}" stroke-width="1"/>')
        out.append(f'<path d="M {_f(cx)} {_f(cy - r * 0.2)} L {_f(cx)} {_f(cy + r * 0.2)}" stroke="#A8743E" stroke-width="1.2"/>')
    elif kind == "white":
        out.append(dab_dots(seed + 2, 14, (cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6), [ROSE, "#E8B83A", "#8FC8C0", RED], (1.2, 2), (0.9, 1)))
    elif kind == "pink":
        for k in range(3):
            rr = r * (0.2 + k * 0.2)
            out.append(f'<path d="M {_f(cx - rr)} {_f(cy)} A {_f(rr)} {_f(rr)} 0 1 1 {_f(cx + rr * 0.6)} {_f(cy + rr * 0.8)}" stroke="#FFFFFF" stroke-width="1.8" fill="none" opacity="0.8"/>')
    elif kind == "gold":
        out.append(f'<path d="{blob(cx, cy, r * 0.5, r * 0.46, seed + 3, 0.15, 10)}" fill="{GOLD}" opacity="0.9"/>' + twinkle(cx - r * 0.1, cy - r * 0.1, r * 0.3, "#FFF6D8"))
    out.append(f'<path d="M {_f(cx - r * 0.5)} {_f(cy - r * 0.2)} Q {_f(cx - r * 0.45)} {_f(cy - r * 0.6)} {_f(cx - r * 0.05)} {_f(cy - r * 0.62)}" stroke="#FFFFFF" stroke-width="{max(1.2, r * 0.1):.1f}" fill="none" stroke-linecap="round" opacity="0.5"/>')
    out.append(ink(d, INK, 1.4, seed, 1, 0.6))
    return "".join(out)


def sweet_on_you():
    """A heart-shaped box of chocolates, lid off, each bonbon in its fluted cup, a satin bow at the corner."""
    P = Pn("sweet-on-you")
    o = [paper_bg(P, "#F7E4DA", "#8A5A4A", 121, tints=["#F2C8C0", "#FFFFFF"])]
    rnd = random.Random(122)
    for row in range(10):
        for c in range(10):
            x, y = c * 64 + (32 if row % 2 else 0), row * 64 + 12
            o.append(f'<circle cx="{x}" cy="{y}" r="{rnd.uniform(3.4, 4.6):.1f}" fill="{ROSE}" opacity="{rnd.uniform(0.18, 0.3):.2f}"/>')
    o.append(P.glow(300, 400, 260, "#FFF2E8", 0.6))
    cx, cy, S = 336, 356, 150
    # the lid, set down behind the box
    lc, lr = (166, 318), 100
    lid = heart_d(lc[0], lc[1], lr, -30, 120)
    o.append(f'<path d="{heart_d(lc[0] + 6, lc[1] + 8, lr, -30, 119)}" fill="#7A2A28" opacity="0.2"/>')
    o.append(paint(P, lid, "#A81E2C", [RED_L, RED_D, "#C83040"], (60, 210, 280, 440), 120, angle=-70, n=80, length=(16, 50), width=(2, 5),
                   shade=RED_D, shade_op=0.5, light="#F6A0A0", light_op=0.3, ink_c=INK, ink_w=2.2))
    o.append(ink(heart_d(lc[0], lc[1] + 2, lr * 0.86, -30, 118), GOLD, 3, 118, 1, 0.9))
    o.append(f'<text x="{lc[0] - 22}" y="{lc[1] - 4}" text-anchor="middle" {SERIF_IT} font-size="27" fill="{GOLD_L}" transform="rotate(-30 {lc[0] - 22} {lc[1] - 10})">for you</text>')
    o.append(f'<path d="{heart_d(cx + 8, cy + 12, S, 0, 123)}" fill="#7A2A28" opacity="0.18"/>')
    outer = heart_d(cx, cy, S, 0, 124)
    o.append(paint(P, outer, "#B8202E", [RED_L, RED_D, RED, "#D04050"], (cx - S, cy - S, cx + S, cy + S), 124, angle=-60, n=160, length=(20, 60), width=(2, 5),
                   shade=RED_D, shade_op=0.5, light="#F6A0A0", light_op=0.35, ink_c=INK, ink_w=2.6))
    rim = heart_d(cx, cy + 6, S * 0.87, 0, 125)
    o.append(paint(P, rim, "#F2D27A", [GOLD_L, GOLD, "#FFF0B8", GOLD_D], (cx - S, cy - S, cx + S, cy + S), 125, angle=-30, n=90, length=(10, 30), width=(1.5, 4),
                   shade=GOLD_D, shade_op=0.45, shade_dir=(0, 0, 1, 1), ink_c=INK, ink_w=1.8))
    inner = heart_d(cx, cy + 10, S * 0.8, 0, 126)
    o.append(f'<path d="{inner}" fill="#3A1A10"/>')
    spots = [(-74, -50, "dark"), (0, -22, "heart"), (74, -50, "white"), (-96, 8, "pink"), (-36, 34, "gold"), (36, 34, "milk"), (96, 8, "dark"),
             (-46, 88, "milk"), (46, 88, "pink"), (0, 134, "white")]
    for k, (dx, dy, kind) in enumerate(spots):
        if not kind:
            continue
        o.append(chocolate(P, cx + dx, cy + dy, 19 if dy > 120 else 23, 130 + k, kind))
    # an empty cup (one already eaten) and a few crumbs
    o.append(f'<path d="{blob(cx - 2, cy + 100, 24, 21, 141, 0.05, 16)}" fill="#5A2E1A" opacity="0" />')
    # satin bow on the upper-right lobe
    bx_, by_ = cx + 112, cy - 92
    for sg, L in ((-1, 64), (1, 56)):
        o.append(f'<path d="M {bx_} {by_} q {sg * 16} 26 {sg * 8 + 4} {L} l {sg * 8} -6 l 4 12" stroke="#D97A8A" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
                 f'<path d="M {bx_} {by_} q {sg * 16} 26 {sg * 8 + 4} {L}" stroke="#FBD8DC" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.7"/>')
    o.append(bow_p(P, bx_, by_, 46, "#E89AA6", 142))
    o.append(btext(P, 300, 132, "sweet on you", SERIF_IT, 100, "#5A2414", ["#7A3A20", "#3A1408", "#8A4A2A", "#6A2E18"], 143, max_w=470, shadow="#F2B8A8", sh=(0.02, 0.03), hi="#C8845A"))
    o.append(flank(178, "BE MINE", BEBAS, 32, 10, ROSE, max_w=200, L=40, seed=144))
    o.append(ptext(300, 190, "BE MINE", BEBAS, 32, CRAN, max_w=200, ls=10))
    return finish(P, "".join(o), 145)


def mug(P, cx, top, w, h, col, seed, pattern=None, pcol=None, handle=1, drink="#B87A54", foam=None, ink_c=INK):
    """A painted mug (front view) with handle, rim, drink surface and an optional pattern."""
    out = [cast(cx + 6, top + h + 2, w * 0.65, 9, "#3A2418", 0.35, seed)]
    hx = cx + handle * w / 2
    hd = smooth_closed([(hx - handle * 4, top + h * 0.2), (hx + handle * w * 0.3, top + h * 0.16), (hx + handle * w * 0.38, top + h * 0.48), (hx + handle * w * 0.22, top + h * 0.78),
                        (hx - handle * 4, top + h * 0.8), (hx - handle * 4, top + h * 0.66), (hx + handle * w * 0.18, top + h * 0.62), (hx + handle * w * 0.22, top + h * 0.44),
                        (hx + handle * w * 0.16, top + h * 0.32), (hx - handle * 4, top + h * 0.34)])
    out.append(paint(P, hd, col, [lt(col, 0.3), dk(col, 0.2)], (hx - w * 0.4, top, hx + w * 0.4, top + h), seed, n=8, shade=dk(col, 0.4), shade_op=0.4, ink_c=ink_c, ink_w=2))
    body = smooth_closed([(cx - w / 2, top), (cx - w / 2 + 2, top + h * 0.6), (cx - w / 2 + 8, top + h - 6), (cx - w / 2 + 22, top + h), (cx, top + h + 3),
                          (cx + w / 2 - 22, top + h), (cx + w / 2 - 8, top + h - 6), (cx + w / 2 - 2, top + h * 0.6), (cx + w / 2, top), (cx, top + 8)])
    inner = [paint(P, body, col, [lt(col, 0.3), dk(col, 0.15), col], (cx - w / 2, top, cx + w / 2, top + h), seed + 1, angle=-90, n=40, ink_c=None)]
    rnd = random.Random(seed)
    if pattern == "dots":
        for row in range(int(h / 18)):
            for k in range(-5, 6):
                inner.append(f'<circle cx="{_f(cx + k * 18 + (9 if row % 2 else 0))}" cy="{_f(top + 20 + row * 18)}" r="3.6" fill="{pcol}" opacity="0.9"/>')
    elif pattern == "hearts":
        for row in range(int(h / 30)):
            for k in range(-3, 4):
                inner.append(f'<path d="{heart_d(cx + k * 30 + (15 if row % 2 else 0), top + 26 + row * 30, 7, 0, row * 9 + k)}" fill="{pcol}"/>')
    elif pattern == "stripes":
        for row in range(int(h / 22)):
            inner.append(f'<path d="{hline(cx - w / 2 - 4, top + 16 + row * 22, cx + w / 2 + 4, top + 16 + row * 22, seed + row, 0.6)}" stroke="{pcol}" stroke-width="7" fill="none" opacity="0.9"/>')
    g = P.lg([(0, "#FFFFFF", 0.3), (0.28, "#FFFFFF", 0), (0.65, "#3A2418", 0), (1, "#3A2418", 0.38)], 0, 0, 1, 0)
    inner.append(f'<rect x="{_f(cx - w / 2)}" y="{_f(top)}" width="{_f(w)}" height="{_f(h + 6)}" fill="url(#{g})"/>')
    inner.append(f'<path d="M {_f(cx - w / 2 + w * 0.13)} {_f(top + 14)} q -4 {_f(h * 0.4)} 2 {_f(h * 0.75)}" stroke="#FFFFFF" stroke-width="{_f(max(3, w * 0.04))}" fill="none" stroke-linecap="round" opacity="0.5"/>')
    cid = P.clip(f'<path d="{body}"/>')
    out.append(f'<g clip-path="url(#{cid})">{"".join(inner)}</g>')
    out.append(ink(body, ink_c, 2.4, seed, 2, 0.85))
    rim = blob(cx, top, w / 2, max(6, w * 0.09), seed + 2, 0.01, 22)
    out.append(paint(P, rim, lt(col, 0.2), [lt(col, 0.4)], (cx - w / 2, top - 12, cx + w / 2, top + 12), seed + 2, n=0, ink_c=ink_c, ink_w=2))
    out.append(f'<path d="{blob(cx, top + 1.5, w / 2 - 7, max(4, w * 0.065), seed + 3, 0.02, 20)}" fill="{drink}"/>')
    if foam:
        out.append(f'<path d="{blob(cx, top + 1.5, w / 2 - 14, max(3, w * 0.05), seed + 4, 0.04, 20)}" fill="{foam}" opacity="0.95"/>')
    return "".join(out)


def donut(P, cx, cy, r, seed, icing="#F2A6B8", dough="#D89A5A", sprinkles=None, tilt=0.62):
    out = [cast(cx + 4, cy + r * tilt * 0.9, r * 1.02, r * 0.25, "#3A2418", 0.3, seed)]
    ring = blob(cx, cy, r, r * tilt, seed, 0.02, 20)
    out.append(paint(P, ring, dough, [lt(dough, 0.3), dk(dough, 0.2)], (cx - r, cy - r, cx + r, cy + r), seed, n=10, shade=dk(dough, 0.4), shade_op=0.45, ink_c=INK, ink_w=1.6))
    rnd = random.Random(seed)
    pts = []
    for i in range(22):
        a = 2 * math.pi * i / 22
        rr = r * (0.86 + (rnd.uniform(0.02, 0.08) if (i % 3 == 0 and math.sin(a) > 0) else 0))
        pts.append((cx + math.cos(a) * rr, cy - r * 0.04 + math.sin(a) * rr * tilt + (r * 0.12 if (i % 3 == 0 and math.sin(a) > 0.2) else 0)))
    ic = smooth_closed(pts)
    out.append(paint(P, ic, icing, [lt(icing, 0.35), dk(icing, 0.15)], (cx - r, cy - r, cx + r, cy + r), seed + 1, angle=-20, n=10, light="#FFFFFF", light_op=0.35, ink_c=INK, ink_w=1.4))
    hole = blob(cx, cy - r * 0.02, r * 0.3, r * 0.3 * tilt, seed + 2, 0.04, 12)
    out.append(f'<path d="{hole}" fill="{dk(dough, 0.35)}"/>' + ink(hole, INK, 1.2, seed + 2, 1, 0.6))
    for _ in range(18):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(r * 0.42, r * 0.78)
        x, y = cx + math.cos(a) * rr, cy - r * 0.04 + math.sin(a) * rr * tilt
        out.append(f'<path d="M {_f(x)} {_f(y)} l {_f(rnd.uniform(-4, 4))} {_f(rnd.uniform(-2.5, 2.5))}" stroke="{rnd.choice(sprinkles or ["#FFFFFF", GOLD, TEAL_L, CORAL])}" stroke-width="2.4" stroke-linecap="round"/>')
    return "".join(out)


def happy_galentines():
    """Brunch with the girls: two mugs clink over a plate of sprinkle donuts, the steam curling into a heart."""
    P = Pn("happy-galentines")
    o = [paper_bg(P, "#FBE4D8", "#8A5A4A", 151, tints=["#F6C8B8", "#FFFFFF"], blobs=[(300, 420, 240, 150, "#BFE0D2", 0.55)])]
    # plate of donuts
    o.append(cast(300, 516, 200, 22, "#3A2418", 0.25, 160))
    plate = blob(300, 500, 196, 40, 161, 0.01, 30)
    o.append(paint(P, plate, "#FFFBF4", ["#FFFFFF", "#E8E0D8"], (104, 460, 496, 540), 161, angle=0, n=20, shade="#C8BEC8", shade_op=0.5, ink_c=INK, ink_w=2))
    o.append(ink(blob(300, 496, 150, 26, 162, 0.01, 30), "#C8BEB4", 1.4, 162, 1, 0.8))
    o.append(donut(P, 236, 484, 48, 163, icing="#F2A6B8"))
    o.append(donut(P, 360, 488, 46, 164, icing="#7A4A2E", sprinkles=["#FFFFFF", "#F2A6B8", "#8FC8B4", GOLD_L]))
    o.append(donut(P, 300, 462, 40, 165, icing="#FBF4E8", sprinkles=[CORAL, "#8FC8B4", GOLD, ROSE]))
    # two mugs clinking
    o.append(f'<g transform="rotate(-9 196 420)">{mug(P, 186, 320, 118, 132, "#8FC8B4", 170, pattern="dots", pcol="#FFFBF4", handle=-1, foam="#F2DEC4")}</g>')
    o.append(f'<g transform="rotate(9 404 420)">{mug(P, 414, 320, 118, 132, CORAL, 171, pattern="hearts", pcol="#FBE4D8", handle=1, foam="#F2DEC4")}</g>')
    o.append(twinkle(300, 330, 14, GOLD) + twinkle(272, 318, 7, GOLD) + twinkle(328, 318, 6, GOLD))
    # steam rising into a heart
    for sg in (-1, 1):
        x0 = 300 + sg * 112
        d = f"M {x0} 304 C {x0 - sg * 14} 284 {x0 + sg * 16} 272 {x0 + sg * 2} 254 C {x0 - sg * 14} 236 {300 + sg * 70} 224 {300 + sg * 46} 252 C {300 + sg * 30} 270 {300 + sg * 8} 280 300 300"
        o.append(f'<path d="{d}" stroke="#FFFFFF" stroke-width="7" fill="none" stroke-linecap="round" opacity="0.85"/>'
                 f'<path d="{d}" stroke="#E8C8C0" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.6" transform="translate(1.5 2)"/>')
    o.append(p_heart(P, 300, 268, 15, CORAL, 176, n=5))
    rnd = random.Random(177)
    for k, (hx, hy) in enumerate(((84, 300), (520, 296), (110, 380), (496, 386), (70, 450), (532, 452))):
        o.append(p_heart(P, hx, hy, rnd.uniform(9, 13), [CORAL, "#8FC8B4", GOLD_L, BLUSH][k % 4], 178 + k, rot=rnd.uniform(-20, 20), n=4))
    o.append(btext(P, 300, 104, "happy", SERIF_IT, 88, CORAL_D, [CORAL, CORAL_D, "#C85A44"], 172, max_w=300, shadow="#F2C4B0", sh=(0.02, 0.03)))
    o.append(btext(P, 300, 192, "GALENTINE'S", BEBAS, 104, TEAL_D, [TEAL, TEAL_D, "#245A60", TEAL_L], 173, ls=5, max_w=450, shadow="#F2C4B0", sh=(0.025, 0.035), hi="#9CC8C4"))
    o.append(flank(222, "DAY", BEBAS, 30, 10, CORAL, max_w=120, L=60, seed=174))
    o.append(ptext(300, 233, "DAY", BEBAS, 30, CORAL_D, max_w=120, ls=10))
    return finish(P, "".join(o), 175)

# --------------------------------------------------------------- St. Patrick's Day
SHAM, SHAM_D, SHAM_L = "#3E8A4A", "#22582E", "#7CB86A"


def clover(P, cx, cy, s, seed, leaves=4, rot=0, col=SHAM, stem_len=None, ink_c=INK):
    """Shamrock / four-leaf clover: heart-shaped leaflets meeting at the centre, a pale chevron on each, a curved stem."""
    out = []
    L = stem_len if stem_len is not None else s * 1.3
    a = math.radians(rot + 90)
    out.append(stem(P, [(cx, cy), (cx + math.cos(a) * L * 0.5 + s * 0.12, cy + math.sin(a) * L * 0.5), (cx + math.cos(a) * L + s * 0.25, cy + math.sin(a) * L)], dk(col, 0.15), max(2.2, s * 0.1), seed, ink_c))
    for i in range(leaves):
        ang = rot - 90 + i * 360 / leaves + (45 if leaves == 4 else 0)
        r_ = math.radians(ang)
        hx, hy = cx + math.cos(r_) * s * 0.5, cy + math.sin(r_) * s * 0.5
        c = [col, lt(col, 0.08), dk(col, 0.06), col][i % 4]
        out.append(p_heart(P, hx, hy, s * 0.5, c, seed + i, rot=ang + 90, ink_c=ink_c, n=8, glossy=False, hi=False))
        # pale chevron mark
        px, py = cx + math.cos(r_) * s * 0.5, cy + math.sin(r_) * s * 0.5
        nx, ny = -math.sin(r_), math.cos(r_)
        out.append(f'<path d="M {_f(px + nx * s * 0.2 - math.cos(r_) * s * 0.02)} {_f(py + ny * s * 0.2 - math.sin(r_) * s * 0.02)} Q {_f(px + math.cos(r_) * s * 0.06)} {_f(py + math.sin(r_) * s * 0.06)} '
                   f'{_f(px - nx * s * 0.2 - math.cos(r_) * s * 0.02)} {_f(py - ny * s * 0.2 - math.sin(r_) * s * 0.02)}" stroke="{lt(col, 0.5)}" stroke-width="{max(1, s * 0.05):.1f}" fill="none" stroke-linecap="round" opacity="0.75"/>')
        out.append(f'<path d="M {_f(cx)} {_f(cy)} L {_f(cx + math.cos(r_) * s * 0.7)} {_f(cy + math.sin(r_) * s * 0.7)}" stroke="{dk(col, 0.25)}" stroke-width="{max(0.8, s * 0.025):.1f}" opacity="0.5"/>')
    out.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{max(1.5, s * 0.07):.1f}" fill="{dk(col, 0.3)}"/>')
    return "".join(out)


def coin(P, cx, cy, r, seed, tilt=1.0, rot=0, ink_c=INK, mark=True):
    """Gold coin: rim, stamped face, shine."""
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    edge = blob(cx, cy + r * 0.12 * tilt, r, r * tilt, seed, 0.01, 18)
    out.append(f'<path d="{edge}" fill="{GOLD_D}"/>')
    face = blob(cx, cy, r, r * tilt, seed + 1, 0.01, 18)
    g = P.rg([(0, "#FFF2B8"), (0.55, "#F2C24A"), (1, "#C8901E")], cx=0.36, cy=0.32, r=0.75)
    out.append(f'<path d="{face}" fill="url(#{g})"/>')
    out.append(f'<path d="{blob(cx, cy, r * 0.74, r * 0.74 * tilt, seed + 2, 0.01, 16)}" fill="none" stroke="{GOLD_D}" stroke-width="{max(1, r * 0.08):.1f}" opacity="0.7"/>')
    if mark and r > 9:
        out.append(f'<polygon points="{" ".join(f"{_f(x)},{_f(cy + (y - cy) * tilt)}" for x, y in star_pts(cx, cy, r * 0.38, r * 0.16))}" fill="{GOLD_D}" opacity="0.7"/>')
    out.append(f'<path d="M {_f(cx - r * 0.55)} {_f(cy - r * 0.25 * tilt)} Q {_f(cx - r * 0.45)} {_f(cy - r * 0.6 * tilt)} {_f(cx - r * 0.05)} {_f(cy - r * 0.68 * tilt)}" stroke="#FFFBE6" stroke-width="{max(1, r * 0.12):.1f}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    out.append(ink(face, ink_c, max(1, r * 0.07), seed, 1, 0.75))
    out.append("</g>")
    return "".join(out)


def horseshoe(P, cx, cy, R, seed, col="#E0A73C", ink_c=INK):
    """Lucky horseshoe, opening upward: forged band, flared heels, nail holes, a polished highlight."""
    r = R * 0.62
    a0, a1 = -28, 208
    outer = [(cx + math.cos(math.radians(a)) * R * (1.0 if 0 < a < 180 else 0.98), cy + math.sin(math.radians(a)) * R * 1.06) for a in range(a0, a1 + 1, 8)]
    inner = [(cx + math.cos(math.radians(a)) * r, cy + math.sin(math.radians(a)) * r * 1.1) for a in range(a1 - 6, a0 + 5, -8)]
    heel_r = [(outer[-1][0] - R * 0.03, outer[-1][1] - R * 0.12), (inner[0][0] + R * 0.02, inner[0][1] - R * 0.1)]
    heel_l = [(inner[-1][0] - R * 0.02, inner[-1][1] - R * 0.1), (outer[0][0] + R * 0.03, outer[0][1] - R * 0.12)]
    pts = outer + heel_r + inner + heel_l
    d = smooth_closed(pts)
    out = [f'<path d="{d}" fill="#3A2418" opacity="0.22" transform="translate(7 9)"/>']
    out.append(paint(P, d, col, [GOLD_L, GOLD_D, "#F2C25A", "#FFF0B8"], bbox(pts), seed, angle=-30, n=120, length=(R * 0.08, R * 0.25), width=(1.2, 3.5), curve=0.5,
                     shade=GOLD_D, shade_op=0.55, shade_dir=(0, 0, 1, 1), light="#FFF6D8", light_op=0.4, ink_c=ink_c, ink_w=2.6))
    # the groove (fuller) where the nails sit
    mid = [(cx + math.cos(math.radians(a)) * R * 0.81, cy + math.sin(math.radians(a)) * R * 0.86) for a in range(a0 + 12, a1 - 11, 6)]
    out.append(f'<path d="{smooth_open(mid)}" stroke="{GOLD_D}" stroke-width="{_f(R * 0.06)}" fill="none" stroke-linecap="round" opacity="0.6"/>')
    out.append(f'<path d="{smooth_open(mid)}" stroke="#FFF0B8" stroke-width="{_f(R * 0.015)}" fill="none" stroke-linecap="round" opacity="0.6" transform="translate(-1 -2)"/>')
    for a in (-6, 22, 50, 130, 158, 186):
        x, y = cx + math.cos(math.radians(a)) * R * 0.81, cy + math.sin(math.radians(a)) * R * 0.86
        out.append(f'<path d="{org_rect(x - R * 0.035, y - R * 0.05, R * 0.07, R * 0.1, seed + a, 0.3, 4, 1)}" fill="#5A3A14" transform="rotate({a + 90} {_f(x)} {_f(y)})"/>')
    hl = [(cx + math.cos(math.radians(a)) * R * 0.93, cy + math.sin(math.radians(a)) * R * 0.98) for a in range(150, 196, 6)]
    out.append(f'<path d="{smooth_open(hl)}" stroke="#FFFBE6" stroke-width="{_f(R * 0.05)}" fill="none" stroke-linecap="round" opacity="0.75"/>')
    return "".join(out)


def lucky():
    """A golden horseshoe brimming with clover and coins under big, bright brush lettering."""
    P = Pn("lucky")
    o = [paper_bg(P, "#F4EEDC", "#5A6A3A", 201, tints=["#DCE6C4", "#FFFFFF"], blobs=[(300, 420, 230, 150, "#C8DEB0", 0.6), (300, 410, 150, 100, "#F2E2A8", 0.35)])]
    rnd = random.Random(202)
    for i in range(16):
        x, y = rnd.uniform(30, 570), rnd.uniform(30, 570)
        if 80 < x < 520 and 50 < y < 550:
            continue
        o.append(clover(P, x, y, rnd.uniform(9, 14), 203 + i, leaves=3, rot=rnd.uniform(-40, 40), col=rnd.choice([SHAM_L, SHAM]), ink_c=None))
    o.append(horseshoe(P, 300, 392, 116, 210))
    # clover sprigs and coins tucked in the horseshoe
    for k, (x, y, s, rot, n) in enumerate(((208, 334, 44, -22, 3), (392, 330, 46, 24, 3), (300, 304, 54, 0, 4))):
        o.append(clover(P, x, y, s, 220 + k * 9, leaves=n, rot=rot, col=[SHAM, "#4C9A52", SHAM_D][k], stem_len=s * 1.4))
    for k, (x, y, r, rot) in enumerate(((256, 386, 22, -14), (300, 400, 24, 6), (346, 384, 22, 18), (280, 432, 20, -6), (326, 434, 20, 10), (300, 368, 18, 0))):
        o.append(coin(P, x, y, r, 240 + k, tilt=0.86, rot=rot))
    # coins spilled at the foot
    o.append(cast(300, 528, 170, 10, "#3A2418", 0.25, 250))
    for k, (x, y, r, t) in enumerate(((150, 520, 18, 0.45), (178, 508, 16, 0.5), (430, 518, 18, 0.45), (458, 504, 15, 0.5), (412, 532, 14, 0.42))):
        o.append(coin(P, x, y, r, 251 + k, tilt=t))
    o.append(clover(P, 112, 452, 38, 260, leaves=4, rot=-30, col="#4C9A52", stem_len=60))
    o.append(clover(P, 494, 446, 32, 261, leaves=3, rot=26, col=SHAM, stem_len=50))
    o.append(sparkles(262, 7, (90, 250, 510, 520), GOLD, (6, 12), avoid=((170, 270, 430, 520),)))
    o.append(ptext(300, 92, "HAPPY ST. PATRICK'S DAY", BEBAS, 30, SHAM_D, max_w=330, ls=6))
    o.append(flank(82, "HAPPY ST. PATRICK'S DAY", BEBAS, 30, 6, GOLD_D, max_w=330, L=30, seed=263, dots=False))
    o.append(btext(P, 300, 250, "LUCKY", ANTON, 138, SHAM, [SHAM_L, SHAM_D, "#4C9A52", "#2E6E3A"], 264, ls=8, max_w=420, shadow=GOLD, sh=(0.025, 0.035), hi="#B8E0A0"))
    return finish(P, "".join(o), 265)


def rainbow(P, cx, cy, R, band, seed, cols=("#E2574A", "#F2934A", "#F2CD5A", "#7CB86A", "#4A9AC8", "#7A62B0"), a0=180, a1=360):
    out = []
    for i, c in enumerate(cols):
        r0 = R - i * band
        pts_o = [(cx + math.cos(math.radians(a)) * r0, cy + math.sin(math.radians(a)) * r0) for a in range(a0, a1 + 1, 4)]
        pts_i = [(cx + math.cos(math.radians(a)) * (r0 - band), cy + math.sin(math.radians(a)) * (r0 - band)) for a in range(a1, a0 - 1, -4)]
        d = smooth_closed(jitter(pts_o, seed + i, 0.8) + jitter(pts_i, seed + 10 + i, 0.8))
        out.append(f'<path d="{d}" fill="{c}" opacity="0.92"/>')
        out.append(strokes(P.id("s"), d, (cx - R, cy - R, cx + R, cy), [lt(c, 0.3), dk(c, 0.12), "#FFFFFF"], seed + i, int(R * 0.5), angle=-45, length=(band, band * 3),
                           width=(1, band * 0.25), opacity=(0.15, 0.4), curve=0.6))
    return "".join(out)


def cauldron(P, cx, top, w, h, seed):
    """Black iron pot on three stubby legs, a rolled rim, a rim-light from the rainbow's glow."""
    out = [cast(cx + 6, top + h + 8, w * 0.62, 10, "#1A2410", 0.4, seed)]
    for dx in (-0.32, 0.32):
        out.append(f'<path d="{org_rect(cx + dx * w - 7, top + h - 14, 14, 26, seed + int(dx * 10), 0.6, 6, 3)}" fill="#1E1E24" stroke="{INK}" stroke-width="1.2"/>')
    body = smooth_closed([(cx - w * 0.5, top + 10), (cx - w * 0.56, top + h * 0.45), (cx - w * 0.44, top + h * 0.85), (cx, top + h + 4), (cx + w * 0.44, top + h * 0.85),
                          (cx + w * 0.56, top + h * 0.45), (cx + w * 0.5, top + 10), (cx, top + 20)])
    out.append(paint(P, body, "#2A2A32", ["#3E3E4A", "#16161C", "#4A4A58"], (cx - w * 0.6, top, cx + w * 0.6, top + h), seed, angle=-20, n=60, length=(w * 0.08, w * 0.25),
                     width=(1.5, 4), curve=0.6, shade="#08080C", shade_op=0.6, shade_dir=(0, 0, 1, 1), ink_c=INK, ink_w=2.2))
    out.append(f'<path d="M {_f(cx - w * 0.44)} {_f(top + h * 0.25)} Q {_f(cx - w * 0.52)} {_f(top + h * 0.55)} {_f(cx - w * 0.32)} {_f(top + h * 0.8)}" stroke="#A8B8D8" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.55"/>')
    rim = blob(cx, top + 8, w * 0.54, 16, seed + 1, 0.01, 20)
    out.append(paint(P, rim, "#3A3A46", ["#5A5A6A", "#24242C"], (cx - w * 0.55, top - 10, cx + w * 0.55, top + 26), seed + 1, angle=0, n=10, ink_c=INK, ink_w=2))
    return "".join(out)


def pot_of_gold():
    """The end of the rainbow: an iron pot heaped with gold on a green Irish hillside, clover in the grass."""
    P = Pn("pot-of-gold")
    o = [sky_wash(P, "#9CCAE2", "#E2F0F2", ["#B8DAEA", "#88BCD8", "#D8ECF2", "#FFFFFF"], 281, n=220, angle=-4, mid=(0.55, "#C4E2EE"))]
    o.append(P.glow(420, 420, 200, "#FFF2B0", 0.6))
    o.append(cloud(P, 92, 300, 60, 20, 280, shade="#C8D8E8", op=0.85))
    o.append(cloud(P, 520, 318, 54, 18, 279, shade="#C8D8E8", op=0.8))
    o.append(rainbow(P, 262, 520, 230, 15, 282))
    # hills
    back = smooth_closed([(-20, 452), (90, 420), (210, 436), (330, 414), (470, 428), (620, 410), (620, 620), (-20, 620)])
    o.append(paint(P, back, "#B4D49A", ["#C8E2B0", "#9CC484", "#D4EAC0"], (-20, 410, 620, 620), 278, angle=-3, n=80, length=(20, 60), width=(2, 5), ink_c=None))
    far = smooth_closed([(-20, 470), (120, 440), (260, 452), (400, 430), (620, 446), (620, 620), (-20, 620)])
    o.append(paint(P, far, "#8CBC6A", ["#A8D080", "#6E9E52", "#B8D890"], (-20, 430, 620, 620), 284, angle=-3, n=120, length=(20, 60), width=(2, 5), ink_c=INK, ink_w=1.6, ink_op=0.45))
    o.append(cloud(P, 82, 468, 84, 30, 283, shade="#B8CCE0"))
    near = smooth_closed([(-20, 520), (160, 500), (330, 512), (480, 496), (620, 506), (620, 620), (-20, 620)])
    o.append(paint(P, near, "#5E9A48", ["#7CB86A", "#46803A", "#8CC870", "#3E7034"], (-20, 494, 620, 620), 285, angle=-80, n=260, length=(6, 18), width=(1, 2.6), op=(0.4, 0.8), ink_c=INK, ink_w=1.6, ink_op=0.45))
    # the pot heaped with gold
    pcx, ptop = 420, 412
    o.append(P.glow(pcx, ptop - 10, 120, "#FFE07A", 0.75))
    o.append(cauldron(P, pcx, ptop, 150, 96, 286))
    heap = smooth_closed([(pcx - 78, ptop + 10), (pcx - 70, ptop - 14), (pcx - 40, ptop - 34), (pcx - 6, ptop - 44), (pcx + 34, ptop - 34), (pcx + 66, ptop - 16), (pcx + 80, ptop + 10), (pcx, ptop + 18)])
    o.append(paint(P, heap, "#E8B83A", [GOLD_L, GOLD_D, "#F6D27A"], (pcx - 80, ptop - 44, pcx + 80, ptop + 18), 287, n=20, ink_c=None))
    rnd = random.Random(288)
    for k in range(17):
        x = pcx + rnd.uniform(-66, 66)
        y = ptop + 6 - (40 - abs(x - pcx) * 0.5) * rnd.uniform(0.3, 1.0)
        o.append(coin(P, x, y, rnd.uniform(9, 13), 289 + k, tilt=rnd.uniform(0.35, 0.7), rot=rnd.uniform(-25, 25)))
    for k, (x, y, r) in enumerate(((336, 508, 12), (354, 520, 11), (510, 512, 12), (488, 528, 10))):
        o.append(coin(P, x, y, r, 310 + k, tilt=0.45))
    o.append(sparkles(315, 9, (330, 330, 520, 420), "#FFFBE6", (6, 12)))
    # clover in the grass
    for k in range(10):
        x = rnd.uniform(70, 540)
        y = rnd.uniform(522, 546)
        if 330 < x < 520:
            continue
        o.append(clover(P, x, y, rnd.uniform(10, 15), 320 + k, leaves=3, rot=rnd.uniform(-30, 30), col=rnd.choice([SHAM, SHAM_D, "#4C9A52"]), stem_len=10, ink_c=None))
    o.append(clover(P, 112, 540, 22, 340, leaves=4, rot=-10, col=SHAM_D, stem_len=18))
    o.append(btext(P, 300, 98, "pot of", SERIF_IT, 76, SHAM_D, [SHAM, SHAM_D, "#2E6E3A"], 341, max_w=280, shadow="#FFFFFF", sh=(0.02, 0.03)))
    o.append(btext(P, 300, 252, "GOLD", ANTON, 136, "#E0A21E", [GOLD_L, GOLD_D, "#F2C25A", "#FFF0B8"], 342, ls=10, max_w=330, shadow=SHAM_D, sh=(0.025, 0.035), hi="#FFF6D8"))
    return finish(P, "".join(o), 343)


# --------------------------------------------------------------- Easter
def fur(P, d, box, base, tints, seed, angle=-90, n=None, shade=None, shade_dir=(0.2, 0, 0.9, 1), ink_c=INK, ink_w=2.0, density=110):
    """Soft fur: wash plus many short fine strokes."""
    x0, y0, x1, y1 = box
    n = n or int((x1 - x0) * (y1 - y0) / density)
    return paint(P, d, base, tints, box, seed, angle=angle, n=n, length=(5, 14), width=(0.6, 1.6), op=(0.3, 0.7), curve=0.4,
                 shade=shade, shade_op=0.45, shade_dir=shade_dir, ink_c=ink_c, ink_w=ink_w)


def bunny(P, cx, base, s, seed, coat="#FBF5EC", inner="#F2B8BE", ink_c="#4A3428"):
    """A sitting storybook bunny facing us: soft painted fur, long ears (one flopped), closed happy eyes, rosy cheeks."""
    tints = ["#FFFFFF", "#E8DCCC", "#F2E8DA", "#D8C8B4"]
    out = [cast(cx + 6, base, s * 0.9, s * 0.1, "#3A2A4A", 0.3, seed)]
    hy = base - s * 1.18
    # ears
    for k, (ang, L, flop) in enumerate(((-104, s * 0.95, False), (-70, s * 0.8, True))):
        a = math.radians(ang)
        ex, ey = cx + (k * 2 - 1) * s * 0.18, hy - s * 0.3
        if flop:
            tip = (ex + math.cos(a) * L * 0.55, ey + math.sin(a) * L * 0.55)
            pts = [(ex - s * 0.1, ey), (ex - s * 0.1 + math.cos(a) * L * 0.3, ey + math.sin(a) * L * 0.4), (tip[0] - s * 0.05, tip[1] - s * 0.06), (tip[0] + s * 0.25, tip[1] + s * 0.05),
                   (tip[0] + s * 0.42, tip[1] + s * 0.28), (tip[0] + s * 0.3, tip[1] + s * 0.24), (ex + s * 0.12 + math.cos(a) * L * 0.25, ey + math.sin(a) * L * 0.25), (ex + s * 0.12, ey)]
        else:
            pts = leaf_shape(ex, ey + s * 0.05, L, ang, 0.2, seed + k)
        d = smooth_closed(pts)
        out.append(fur(P, d, bbox(pts), coat, tints, seed + k, angle=ang, shade="#C8B4A8", ink_c=ink_c))
        if not flop:
            ip = leaf_shape(ex + math.cos(a) * s * 0.06, ey + s * 0.02 + math.sin(a) * s * 0.06, L * 0.82, ang, 0.11, seed + k + 5)
            out.append(paint(P, smooth_closed(ip), inner, [lt(inner, 0.3), dk(inner, 0.15)], bbox(ip), seed + k + 5, angle=ang, n=8, ink_c=None))
        else:
            ip = [(ex - s * 0.02, ey - s * 0.02), (tip[0] + s * 0.02, tip[1] + s * 0.02), (tip[0] + s * 0.26, tip[1] + s * 0.18), (ex + s * 0.06, ey - s * 0.06)]
            out.append(f'<path d="{smooth_closed(ip)}" fill="{inner}" opacity="0.75"/>')
    # body
    body = smooth_closed([(cx - s * 0.5, base - s * 0.1), (cx - s * 0.6, base - s * 0.5), (cx - s * 0.42, base - s * 0.92), (cx, base - s * 1.02), (cx + s * 0.42, base - s * 0.92),
                          (cx + s * 0.6, base - s * 0.5), (cx + s * 0.5, base - s * 0.1), (cx, base + s * 0.02)])
    out.append(fur(P, body, (cx - s * 0.6, base - s, cx + s * 0.6, base), coat, tints, seed + 10, shade="#C8B4A8", ink_c=ink_c))
    out.append(f'<path d="{blob(cx, base - s * 0.38, s * 0.26, s * 0.3, seed + 11, 0.08, 14)}" fill="#FFFFFF" opacity="0.45"/>')
    # feet
    for sg in (-1, 1):
        fd = blob(cx + sg * s * 0.34, base - s * 0.06, s * 0.24, s * 0.1, seed + 12 + sg, 0.05, 14)
        out.append(fur(P, fd, (cx + sg * s * 0.34 - s * 0.25, base - s * 0.16, cx + sg * s * 0.34 + s * 0.25, base + s * 0.04), coat, tints, seed + 12 + sg, angle=0, n=12, ink_c=ink_c, ink_w=1.6))
        for t in (-0.1, 0.0, 0.1):
            out.append(f'<path d="M {_f(cx + sg * s * 0.34 + sg * s * (0.12 + t))} {_f(base - s * 0.1)} l 0 {_f(s * 0.05)}" stroke="{ink_c}" stroke-width="1.2" opacity="0.5"/>')
    # front paws
    for sg in (-1, 1):
        pd = blob(cx + sg * s * 0.13, base - s * 0.2, s * 0.09, s * 0.12, seed + 15 + sg, 0.05, 12)
        out.append(fur(P, pd, (cx + sg * s * 0.13 - s * 0.1, base - s * 0.32, cx + sg * s * 0.13 + s * 0.1, base - s * 0.08), "#F6EEE2", tints, seed + 15 + sg, n=8, ink_c=ink_c, ink_w=1.3))
    # head
    head = smooth_closed([(cx - s * 0.46, hy + s * 0.05), (cx - s * 0.38, hy - s * 0.3), (cx, hy - s * 0.42), (cx + s * 0.38, hy - s * 0.3), (cx + s * 0.46, hy + s * 0.05),
                          (cx + s * 0.32, hy + s * 0.3), (cx, hy + s * 0.36), (cx - s * 0.32, hy + s * 0.3)])
    out.append(fur(P, head, (cx - s * 0.46, hy - s * 0.42, cx + s * 0.46, hy + s * 0.36), coat, tints, seed + 20, shade="#C8B4A8", ink_c=ink_c))
    # muzzle, cheeks, face
    out.append(f'<path d="{blob(cx, hy + s * 0.14, s * 0.2, s * 0.13, seed + 21, 0.05, 12)}" fill="#FFFFFF" opacity="0.8"/>')
    for sg in (-1, 1):
        out.append(f'<path d="{blob(cx + sg * s * 0.26, hy + s * 0.1, s * 0.09, s * 0.06, seed + 22 + sg, 0.1, 10)}" fill="#F29AA4" opacity="0.6"/>')
        out.append(ink(f"M {_f(cx + sg * s * 0.24 - s * 0.07)} {_f(hy - s * 0.04)} q {_f(s * 0.07)} {_f(s * 0.07)} {_f(s * 0.14)} 0", "#3A2418", max(2, s * 0.025), seed + 24, 1, 0.95))
        for k in (-1, 0, 1):
            out.append(f'<path d="M {_f(cx + sg * s * 0.14)} {_f(hy + s * 0.14 + k * s * 0.03)} l {_f(sg * s * 0.24)} {_f(k * s * 0.05)}" stroke="#8A7A6A" stroke-width="1.1" opacity="0.6"/>')
    out.append(f'<path d="{smooth_closed([(cx - s * 0.05, hy + s * 0.08), (cx + s * 0.05, hy + s * 0.08), (cx, hy + s * 0.14)])}" fill="#E07A8A"/>')
    out.append(ink(f"M {_f(cx)} {_f(hy + s * 0.14)} l 0 {_f(s * 0.04)} M {_f(cx - s * 0.05)} {_f(hy + s * 0.2)} q {_f(s * 0.05)} {_f(s * 0.04)} {_f(s * 0.05)} {_f(-s * 0.02)} q 0 {_f(s * 0.06)} {_f(s * 0.05)} {_f(s * 0.02)}", ink_c, 1.4, seed + 25, 1, 0.8))
    return "".join(out)


def egg(P, cx, cy, w, h, col, seed, pattern=None, pcol="#FFFFFF", rot=0, ink_c=INK):
    """Painted Easter egg with a hand-painted pattern."""
    pts = []
    for i in range(24):
        t = 2 * math.pi * i / 24
        k = 1 - 0.18 * math.sin(t) if math.sin(t) < 0 else 1
        pts.append((cx + math.cos(t) * w / 2 * (0.86 + 0.14 * k) * (1 if math.sin(t) > 0 else 0.92), cy + math.sin(t) * h / 2))
    pts = jitter(pts, seed, w * 0.006)
    d = smooth_closed(pts)
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    inner = [paint(P, d, col, [lt(col, 0.3), dk(col, 0.15), col], (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), seed, angle=-70, n=12, ink_c=None)]
    rnd = random.Random(seed)
    if pattern == "stripes":
        for k in (-0.22, 0.05, 0.3):
            yy = cy + k * h
            inner.append(f'<path d="{hline(cx - w / 2, yy, cx + w / 2, yy - 3, seed + int(k * 10), 1, 8)}" stroke="{pcol}" stroke-width="{_f(h * 0.07)}" fill="none"/>')
    elif pattern == "zigzag":
        for k in (-0.12, 0.18):
            yy = cy + k * h
            zz = " ".join(f"{_f(cx - w / 2 + i * w / 8)},{_f(yy + (h * 0.05 if i % 2 else -h * 0.05))}" for i in range(9))
            inner.append(f'<polyline points="{zz}" stroke="{pcol}" stroke-width="{_f(h * 0.045)}" fill="none" stroke-linejoin="round"/>')
        inner.append(f'<path d="{hline(cx - w / 2, cy + 0.03 * h, cx + w / 2, cy + 0.03 * h, seed, 0.5)}" stroke="{lt(pcol, 0.4)}" stroke-width="{_f(h * 0.025)}" fill="none"/>')
    elif pattern == "dots":
        for _ in range(int(w * h / 260)):
            inner.append(f'<circle cx="{_f(rnd.uniform(cx - w / 2, cx + w / 2))}" cy="{_f(rnd.uniform(cy - h / 2, cy + h / 2))}" r="{_f(rnd.uniform(w * 0.03, w * 0.05))}" fill="{pcol}"/>')
    elif pattern == "flowers":
        for k, (fx, fy) in enumerate(((-0.15, -0.15), (0.2, 0.05), (-0.1, 0.25), (0.22, -0.3))):
            x, y = cx + fx * w, cy + fy * h
            for j in range(5):
                a = math.radians(j * 72 + k * 20)
                inner.append(f'<circle cx="{_f(x + math.cos(a) * w * 0.05)}" cy="{_f(y + math.sin(a) * w * 0.05)}" r="{_f(w * 0.04)}" fill="{pcol}"/>')
            inner.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(w * 0.03)}" fill="{GOLD}"/>')
    g = P.rg([(0, "#FFFFFF", 0.45), (0.45, "#FFFFFF", 0), (0.85, "#3A2418", 0.2), (1, "#3A2418", 0.35)], cx=0.36, cy=0.32, r=0.75)
    inner.append(f'<path d="{d}" fill="url(#{g})"/>')
    cid = P.clip(f'<path d="{d}"/>')
    out.append(f'<g clip-path="url(#{cid})">{"".join(inner)}</g>')
    out.append(f'<path d="M {_f(cx - w * 0.28)} {_f(cy - h * 0.12)} Q {_f(cx - w * 0.26)} {_f(cy - h * 0.34)} {_f(cx - w * 0.06)} {_f(cy - h * 0.4)}" stroke="#FFFFFF" stroke-width="{_f(max(1.5, w * 0.06))}" fill="none" stroke-linecap="round" opacity="0.6"/>')
    out.append(ink(d, ink_c, max(1.2, w * 0.03), seed, 2, 0.75))
    out.append("</g>")
    return "".join(out)


def grass_tufts(seed, box, cols, n=120, h=(8, 22), w=1.8, op=(0.6, 1.0)):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        hh = rnd.uniform(*h)
        lean = rnd.uniform(-0.4, 0.4) * hh
        out.append(f'<path d="M {_f(x)} {_f(y)} q {_f(lean * 0.3)} {_f(-hh * 0.5)} {_f(lean)} {_f(-hh)}" stroke="{rnd.choice(cols)}" stroke-width="{w}" fill="none" stroke-linecap="round" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


def hoppy_easter():
    """A soft white bunny sits among spring tulips and painted eggs, one ear flopped over."""
    P = Pn("hoppy-easter")
    o = [sky_wash(P, "#D8CCEC", "#EEE6F4", ["#E4DAF0", "#CABCE2", "#F2ECF6", "#FFFFFF"], 401, n=220, angle=-8, mid=(0.6, "#E2D8EE"))]
    o.append(mottle(402, ["#FFFFFF", "#B8A2D6"], 10))
    o.append(P.glow(300, 380, 220, "#FFF6E8", 0.7))
    ground = smooth_closed([(-20, 470), (150, 458), (300, 466), (450, 456), (620, 468), (620, 620), (-20, 620)])
    o.append(paint(P, ground, "#A8CC8A", ["#BEDCA0", "#8AB86E", "#C8E4AE"], (-20, 456, 620, 620), 403, angle=-80, n=240, length=(6, 16), width=(1, 2.4), op=(0.4, 0.8), ink_c=INK, ink_w=1.6, ink_op=0.4))
    # tulips each side
    for k, (x, h, col, lean) in enumerate(((96, 190, "#E86A7A", -0.06), (148, 150, "#F2A23A", 0.05), (452, 160, "#F2D06B", -0.05), (506, 196, "#E86A7A", 0.07), (66, 120, "#B88AD8", -0.1), (536, 124, "#F2A23A", 0.12))):
        o.append(tulip(P, x, 500 + (k % 2) * 8, h, col, 404 + k * 7, lean=lean))
    o.append(bunny(P, 300, 534, 138, 450))
    # eggs in the grass
    for k, (x, y, w, h, col, pat, pc, rot) in enumerate(((176, 516, 46, 58, "#8FC8E0", "zigzag", "#FFFFFF", -14), (232, 532, 40, 50, "#F2D06B", "dots", "#E86A7A", 10),
                                                         (382, 530, 44, 56, "#E8A0B4", "stripes", "#FFFFFF", -6), (430, 516, 38, 48, "#B8A2D6", "flowers", "#FFFFFF", 16))):
        o.append(cast(x + 4, y + h * 0.42, w * 0.55, 5, "#3A4A2A", 0.3, 460 + k))
        o.append(egg(P, x, y, w, h, col, 461 + k, pat, pc, rot))
    o.append(grass_tufts(470, (40, 520, 560, 548), ["#7AA85E", "#94C078", "#5E8A48"], 90))
    o.append(btext(P, 300, 92, "hoppy", SERIF_IT, 80, PLUM, ["#7A5A8E", "#3E2650", "#8A6AA0"], 471, max_w=300, shadow="#FFFFFF", sh=(0.02, 0.03)))
    o.append(btext(P, 300, 194, "EASTER", BEBAS, 100, "#E86A7A", ["#F29AA4", "#C84A5A", "#F2B8BE"], 472, ls=12, max_w=380, shadow=PLUM, sh=(0.02, 0.03), hi="#FFD8DC"))
    return finish(P, "".join(o), 473)


def songbird(P, x, y, s, seed, body="#7AA8C8", belly="#F6E2C8", wing=None, flip=1, ink_c=INK, beak="#E8A23A", cap=None, crest=False):
    """Little perched songbird in profile (facing right when flip=1)."""
    wing = wing or dk(body, 0.2)
    def X(px):
        return x + flip * px
    out = [f'<path d="M {_f(X(-s * 0.1))} {_f(y + s * 0.45)} l {_f(flip * -s * 0.05)} {_f(s * 0.18)} M {_f(X(s * 0.08))} {_f(y + s * 0.45)} l {_f(flip * s * 0.02)} {_f(s * 0.18)}" stroke="#5A3A2A" stroke-width="{max(1.4, s * 0.04):.1f}" stroke-linecap="round"/>']
    tail = [(X(-s * 0.45), y + s * 0.1), (X(-s * 0.95), y + s * 0.28), (X(-s * 0.9), y + s * 0.42), (X(-s * 0.38), y + s * 0.3)]
    out.append(paint(P, smooth_closed(tail), wing, [lt(wing, 0.3), dk(wing, 0.2)], bbox(tail), seed, angle=160 if flip > 0 else 20, n=6, ink_c=ink_c, ink_w=1.6))
    bd = smooth_closed([(X(-s * 0.55), y + s * 0.12), (X(-s * 0.3), y - s * 0.3), (X(s * 0.1), y - s * 0.42), (X(s * 0.42), y - s * 0.3), (X(s * 0.5), y + s * 0.02), (X(s * 0.25), y + s * 0.42), (X(-s * 0.2), y + s * 0.44)])
    out.append(paint(P, bd, body, [lt(body, 0.3), dk(body, 0.15), body], (x - s * 0.6, y - s * 0.45, x + s * 0.6, y + s * 0.45), seed + 1, angle=180 if flip > 0 else 0, n=20, length=(s * 0.1, s * 0.3),
                     width=(0.8, s * 0.04), shade=dk(body, 0.4), shade_op=0.35, ink_c=None))
    bl = smooth_closed([(X(-s * 0.3), y + s * 0.2), (X(s * 0.05), y - s * 0.02), (X(s * 0.42), y + s * 0.02), (X(s * 0.25), y + s * 0.4), (X(-s * 0.15), y + s * 0.42)])
    out.append(paint(P, bl, belly, [lt(belly, 0.4), dk(belly, 0.1)], (x - s * 0.4, y - s * 0.05, x + s * 0.45, y + s * 0.45), seed + 2, angle=0, n=10, ink_c=None))
    if cap:
        cp = smooth_closed([(X(s * 0.0), y - s * 0.38), (X(s * 0.28), y - s * 0.42), (X(s * 0.46), y - s * 0.24), (X(s * 0.2), y - s * 0.2)])
        out.append(f'<path d="{cp}" fill="{cap}" opacity="0.9"/>')
    if crest:
        cr = smooth_closed([(X(s * 0.0), y - s * 0.34), (X(s * 0.02), y - s * 0.7), (X(s * 0.2), y - s * 0.44), (X(s * 0.3), y - s * 0.36)])
        out.append(paint(P, cr, body, [lt(body, 0.3), dk(body, 0.2)], bbox([(x - s, y - s * 0.75), (x + s, y - s * 0.3)]), seed + 7, n=5, ink_c=ink_c, ink_w=1.4))
    out.append(ink(bd, ink_c, max(1.3, s * 0.035), seed + 1, 2, 0.75))
    wd = smooth_closed([(X(-s * 0.42), y + s * 0.02), (X(-s * 0.12), y - s * 0.18), (X(s * 0.18), y - s * 0.02), (X(-s * 0.05), y + s * 0.2), (X(-s * 0.5), y + s * 0.22)])
    out.append(paint(P, wd, wing, [lt(wing, 0.35), dk(wing, 0.25)], (x - s * 0.55, y - s * 0.2, x + s * 0.2, y + s * 0.25), seed + 3, angle=170 if flip > 0 else 10, n=10, ink_c=ink_c, ink_w=1.4))
    for k in range(3):
        out.append(f'<path d="M {_f(X(-s * (0.1 + k * 0.12)))} {_f(y + s * (0.0 + k * 0.03))} l {_f(flip * -s * 0.16)} {_f(s * 0.12)}" stroke="{dk(wing, 0.35)}" stroke-width="1.2" opacity="0.6"/>')
    bk = [(X(s * 0.46), y - s * 0.2), (X(s * 0.7), y - s * 0.12), (X(s * 0.47), y - s * 0.06)]
    out.append(f'<path d="M {" L ".join(f"{_f(a)} {_f(b)}" for a, b in bk)} Z" fill="{beak}" stroke="{ink_c}" stroke-width="1.2" stroke-linejoin="round"/>')
    out.append(f'<circle cx="{_f(X(s * 0.27))}" cy="{_f(y - s * 0.2)}" r="{max(1.8, s * 0.055):.1f}" fill="#1A1210"/><circle cx="{_f(X(s * 0.28) - flip * s * 0.015)}" cy="{_f(y - s * 0.215)}" r="{max(0.6, s * 0.018):.1f}" fill="#FFFFFF"/>')
    return "".join(out)


def nest(P, cx, cy, w, h, seed):
    """Woven twig nest: dark hollow, rim of looping twigs, stray straws."""
    rnd = random.Random(seed)
    out = [cast(cx + 8, cy + h * 0.55, w * 0.55, h * 0.12, "#3A2418", 0.3, seed)]
    bowl = smooth_closed([(cx - w / 2, cy - h * 0.1), (cx - w * 0.42, cy + h * 0.3), (cx - w * 0.2, cy + h * 0.52), (cx + w * 0.2, cy + h * 0.52), (cx + w * 0.42, cy + h * 0.3), (cx + w / 2, cy - h * 0.1), (cx, cy + h * 0.05)])
    out.append(paint(P, bowl, "#9A6A3E", ["#B8864E", "#6E4422", "#C8A06A", "#5A3418"], (cx - w / 2, cy - h * 0.2, cx + w / 2, cy + h * 0.55), seed, angle=-8, n=60,
                     length=(w * 0.08, w * 0.25), width=(1.2, 3), curve=0.5, shade="#3A2010", shade_op=0.5, ink_c=INK, ink_w=2))
    hollow = blob(cx, cy - h * 0.1, w * 0.42, h * 0.14, seed + 1, 0.03, 18)
    out.append(f'<path d="{hollow}" fill="#4A2C16"/>')
    return "".join(out)


def nest_rim(P, cx, cy, w, h, seed):
    rnd = random.Random(seed)
    out = []
    for i in range(70):
        a = rnd.uniform(math.pi * 0.0, math.pi * 1.0)
        x0 = cx + math.cos(a) * w * rnd.uniform(0.38, 0.52)
        y0 = cy - h * 0.1 + math.sin(a) * h * rnd.uniform(0.1, 0.32)
        L = rnd.uniform(w * 0.1, w * 0.26)
        ang = rnd.uniform(-0.5, 0.5) + (0 if rnd.random() < 0.5 else math.pi)
        out.append(f'<path d="M {_f(x0)} {_f(y0)} q {_f(math.cos(ang) * L * 0.5)} {_f(rnd.uniform(-6, 6))} {_f(math.cos(ang) * L)} {_f(math.sin(ang) * L * 0.3)}" '
                   f'stroke="{rnd.choice(["#B8864E", "#6E4422", "#C8A06A", "#8A5A30", "#E2C08A"])}" stroke-width="{rnd.uniform(1.4, 3):.1f}" fill="none" stroke-linecap="round"/>')
    for i in range(10):
        a = rnd.uniform(0, math.pi * 2)
        x0, y0 = cx + math.cos(a) * w * 0.5, cy - h * 0.05 + math.sin(a) * h * 0.25
        out.append(f'<path d="M {_f(x0)} {_f(y0)} q {_f(math.cos(a) * 14)} {_f(rnd.uniform(-8, 8))} {_f(math.cos(a) * 26)} {_f(rnd.uniform(-10, 4))}" stroke="#C8A06A" stroke-width="1.6" fill="none" stroke-linecap="round"/>')
    return "".join(out)


def branch(P, pts, w0, w1, seed, col="#6E4A30", ink_c=INK):
    """Tapered painted branch along pts."""
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[min(i + 1, n - 1)]
        b = pts[max(i - 1, 0)]
        ang = math.atan2(a[1] - b[1], a[0] - b[0])
        w = w0 + (w1 - w0) * i / (n - 1)
        left.append((x - math.sin(ang) * w / 2, y + math.cos(ang) * w / 2))
        right.append((x + math.sin(ang) * w / 2, y - math.cos(ang) * w / 2))
    d = smooth_closed(left + list(reversed(right)))
    return paint(P, d, col, [lt(col, 0.3), dk(col, 0.3), lt(col, 0.15)], bbox(left + right), seed, angle=math.degrees(math.atan2(pts[-1][1] - pts[0][1], pts[-1][0] - pts[0][0])), n=int(len(pts) * 10),
                 length=(10, 30), width=(0.8, 2.2), ink_c=ink_c, ink_w=1.8)


def happy_easter():
    """Four hand-painted eggs in a twig nest beneath a branch of apple blossom, a bluebird keeping watch."""
    P = Pn("happy-easter")
    o = [paper_bg(P, "#EEF2E4", "#5A6A4A", 501, tints=["#D8E8D0", "#FFFFFF"], blobs=[(300, 410, 230, 160, "#CFE6EE", 0.75), (360, 380, 120, 90, "#F8E6EA", 0.35)])]
    # blossom branch from the upper right
    dy_ = 66
    br = [(620, 230 + dy_), (540, 252 + dy_), (470, 262 + dy_), (410, 286 + dy_), (370, 300 + dy_)]
    o.append(branch(P, br, 14, 5, 502))
    o.append(branch(P, [(560, 248 + dy_), (580, 222 + dy_), (596, 206 + dy_)], 5, 3, 503))
    o.append(songbird(P, 470, 226 + dy_, 50, 545, body="#6E9CC8", belly="#F2C69A", beak="#E8B04A", flip=-1))
    for k, (x, y, r, rot) in enumerate(((396, 286, 20, 10), (430, 270, 22, -8), (514, 260, 22, 20), (584, 214, 17, 0), (548, 272, 20, 30), (360, 306, 14, -20), (500, 280, 14, 14))):
        o.append(blossom(P, x, y + dy_, r, 504 + k * 5, col=["#F8D2D8", "#FBE4E6", "#F6C2CA"][k % 3], rot=rot))
    for k, (x, y, L, a) in enumerate(((420, 296, 30, 120), (458, 266, 28, 110), (530, 266, 32, 70), (380, 304, 24, 160))):
        o.append(p_leaf(P, x, y + dy_, L, a, LEAF_L, 540 + k, 0.3))
    for k, (x, y, rot) in enumerate(((330, 380, 20), (120, 330, -30), (180, 300, 60))):
        o.append(f'<path d="{blob(x, y, 7, 4.5, 546 + k, 0.1, 8, rot)}" fill="#F6C2CA" opacity="0.85"/>')
    # nest + eggs
    nx_, ny_ = 264, 462
    o.append(nest(P, nx_, ny_, 300, 150, 550))
    for k, (dx, dy, w, h, col, pat, pc, rot) in enumerate(((-70, -28, 64, 82, "#8FC8E0", "zigzag", "#FFFFFF", -18), (-6, -44, 68, 88, "#F2A6B8", "flowers", "#FFFFFF", 4),
                                                           (62, -30, 62, 80, "#F2D06B", "stripes", "#E8829A", 18), (24, -6, 56, 70, "#B8A2D6", "dots", "#FFFFFF", -8))):
        o.append(egg(P, nx_ + dx * 1.1, ny_ + dy * 1.05, w * 1.1, h * 1.1, col, 551 + k, pat, pc, rot))
    o.append(nest_rim(P, nx_, ny_ + 10, 300, 150, 560))
    for k, (x, y, r) in enumerate(((454, 512, 16), (486, 500, 12), (112, 512, 14))):
        o.append(blossom(P, x, y, r, 570 + k, col="#FBE4E6", rot=k * 30))
    o.append(grass_tufts(575, (120, 520, 460, 536), ["#8AB86E", "#A8CC8A", "#6E9E52"], 40, h=(6, 14)))
    o.append(ptext(300, 96, "HAPPY", JOS, 34, "#C8506A", max_w=240, ls=12))
    o.append(flank(84, "HAPPY", JOS, 34, 12, "#E8A0B4", max_w=240, L=40, seed=576))
    o.append(btext(P, 300, 214, "Easter", DMS, 150, "#4E6E9A", ["#6E8EBA", "#3A5480", "#8AA8CC", "#2E466E"], 577, max_w=380, shadow="#F2C6CE", sh=(0.025, 0.035), hi="#C8DAEE"))
    return finish(P, "".join(o), 578)

# --------------------------------------------------------------- Earth Day, teachers, Mother's Day
def globe(P, cx, cy, r, seed, ocean="#4A9AC8", land=("#7CB86A", "#5E9A48", "#A8CC70")):
    """Painted Earth: ocean wash with swirling strokes, hand-drawn continents, cloud wisps, terminator shading."""
    out = [P.glow(cx, cy, r * 1.5, "#FFF2B0", 0.5)]
    d = blob(cx, cy, r, r, seed, 0.008, 36)
    inner = [paint(P, d, ocean, [lt(ocean, 0.3), dk(ocean, 0.2), "#7AC0DE", "#3A86B8"], (cx - r, cy - r, cx + r, cy + r), seed, angle=-20, n=int(r * 2.2),
                   length=(r * 0.12, r * 0.4), width=(1.5, 4), curve=0.6, ink_c=None)]
    conts = [
        [(-0.62, -0.5), (-0.3, -0.62), (-0.1, -0.5), (-0.18, -0.3), (-0.36, -0.12), (-0.3, 0.02), (-0.46, -0.04), (-0.6, -0.22), (-0.72, -0.34)],
        [(-0.34, 0.08), (-0.14, 0.12), (-0.08, 0.3), (-0.18, 0.56), (-0.3, 0.74), (-0.36, 0.5), (-0.42, 0.26)],
        [(0.1, -0.42), (0.36, -0.52), (0.56, -0.4), (0.46, -0.22), (0.3, -0.24), (0.18, -0.2)],
        [(0.14, -0.12), (0.4, -0.16), (0.56, 0.0), (0.5, 0.26), (0.36, 0.52), (0.24, 0.36), (0.2, 0.12)],
        [(0.62, 0.42), (0.78, 0.36), (0.8, 0.52), (0.66, 0.56)],
    ]
    for k, c in enumerate(conts):
        pts = jitter([(cx + x * r, cy + y * r) for x, y in c], seed + k, r * 0.02)
        dd = smooth_closed(pts)
        col = land[k % len(land)]
        inner.append(paint(P, dd, col, [lt(col, 0.3), dk(col, 0.25), "#C8D890"], bbox(pts), seed + 10 + k, angle=-60, n=int(r * 0.4), length=(r * 0.05, r * 0.15),
                           width=(1, 3), ink_c=INK, ink_w=1.6, ink_op=0.55))
    rnd = random.Random(seed)
    for k in range(5):
        y = cy + rnd.uniform(-0.7, 0.7) * r
        x = cx + rnd.uniform(-0.5, 0.3) * r
        inner.append(f'<path d="M {_f(x)} {_f(y)} q {_f(r * 0.15)} {_f(-r * 0.06)} {_f(r * 0.32)} 0 t {_f(r * 0.2)} {_f(r * 0.02)}" stroke="#FFFFFF" stroke-width="{_f(r * 0.035)}" fill="none" stroke-linecap="round" opacity="0.7"/>')
    g = P.rg([(0, "#FFFFFF", 0.3), (0.45, "#FFFFFF", 0), (0.8, "#1A3A5A", 0.25), (1, "#1A3A5A", 0.55)], cx=0.36, cy=0.34, r=0.72, fx=0.3, fy=0.28)
    inner.append(f'<path d="{d}" fill="url(#{g})"/>')
    cid = P.clip(f'<path d="{d}"/>')
    out.append(f'<g clip-path="url(#{cid})">{"".join(inner)}</g>')
    out.append(f'<path d="M {_f(cx - r * 0.72)} {_f(cy - r * 0.2)} Q {_f(cx - r * 0.7)} {_f(cy - r * 0.66)} {_f(cx - r * 0.24)} {_f(cy - r * 0.78)}" stroke="#FFFFFF" stroke-width="{_f(r * 0.06)}" fill="none" stroke-linecap="round" opacity="0.55"/>')
    out.append(ink(d, INK, 2.6, seed, 2, 0.85))
    return "".join(out)


def bee_p(P, x, y, s, seed, rot=0, ink_c=INK):
    """Little painted honeybee in flight."""
    out = [f'<g transform="rotate({rot} {_f(x)} {_f(y)})">']
    for k, (dx, ang) in enumerate(((-0.1, -120), (0.15, -70))):
        wd = leaf_shape(x + dx * s, y - s * 0.25, s * 0.75, ang, 0.36, seed + k)
        out.append(f'<path d="{smooth_closed(wd)}" fill="#EAF4FA" opacity="0.85" stroke="{ink_c}" stroke-width="1.1"/>')
    bd = blob(x, y, s * 0.55, s * 0.38, seed, 0.04, 14)
    cid = P.clip(f'<path d="{bd}"/>')
    st = "".join(f'<rect x="{_f(x - s * 0.55 + k * s * 0.3)}" y="{_f(y - s)}" width="{_f(s * 0.14)}" height="{_f(s * 2)}" fill="#3A2418"/>' for k in range(1, 4))
    g = P.rg([(0, "#FFE9A0"), (1, "#E8A82A")], cx=0.4, cy=0.35, r=0.7)
    out.append(f'<path d="{bd}" fill="url(#{g})"/><g clip-path="url(#{cid})">{st}</g>' + ink(bd, ink_c, 1.4, seed, 1, 0.85))
    out.append(f'<circle cx="{_f(x + s * 0.58)}" cy="{_f(y - s * 0.05)}" r="{_f(s * 0.22)}" fill="#3A2418"/>')
    out.append(f'<path d="M {_f(x - s * 0.55)} {_f(y)} l {_f(-s * 0.18)} {_f(s * 0.04)}" stroke="#3A2418" stroke-width="1.6" stroke-linecap="round"/>')
    out.append("</g>")
    return "".join(out)


def butterfly(P, x, y, s, seed, col="#F2A23A", rot=0, ink_c=INK):
    out = [f'<g transform="rotate({rot} {_f(x)} {_f(y)})">']
    for sg in (-1, 1):
        up = smooth_closed([(x, y - s * 0.05), (x + sg * s * 0.4, y - s * 0.75), (x + sg * s * 0.95, y - s * 0.6), (x + sg * s * 0.8, y - s * 0.1), (x + sg * s * 0.1, y + s * 0.05)])
        lo = smooth_closed([(x, y + s * 0.02), (x + sg * s * 0.7, y + s * 0.1), (x + sg * s * 0.62, y + s * 0.55), (x + sg * s * 0.2, y + s * 0.5)])
        for k, dd in enumerate((lo, up)):
            out.append(paint(P, dd, col if k else lt(col, 0.15), [lt(col, 0.35), dk(col, 0.2)], (x - s, y - s * 0.8, x + s, y + s * 0.6), seed + sg + k, angle=-60 * sg, n=6, ink_c=ink_c, ink_w=1.3))
        out.append(f'<circle cx="{_f(x + sg * s * 0.55)}" cy="{_f(y - s * 0.42)}" r="{_f(s * 0.1)}" fill="#FFF8EC"/>')
        out.append(f'<path d="M {_f(x)} {_f(y - s * 0.3)} q {_f(sg * s * 0.1)} {_f(-s * 0.3)} {_f(sg * s * 0.25)} {_f(-s * 0.35)}" stroke="{ink_c}" stroke-width="1.1" fill="none"/>')
    out.append(f'<path d="{blob(x, y, s * 0.07, s * 0.36, seed, 0.05, 10)}" fill="#3A2418"/>')
    out.append("</g>")
    return "".join(out)


def ladybug(P, x, y, s, seed, rot=0):
    out = [f'<g transform="rotate({rot} {_f(x)} {_f(y)})">']
    out.append(f'<circle cx="{_f(x + s * 0.55)}" cy="{_f(y)}" r="{_f(s * 0.3)}" fill="#2A1A14"/>')
    out.append(ball_paint(P, x, y, s * 0.55, "#D8342A", seed))
    out.append(f'<path d="M {_f(x + s * 0.5)} {_f(y)} L {_f(x - s * 0.55)} {_f(y)}" stroke="#2A1A14" stroke-width="1.4"/>')
    for dx, dy in ((-0.2, -0.28), (0.15, -0.3), (-0.25, 0.25), (0.15, 0.3), (-0.4, 0.0)):
        out.append(f'<circle cx="{_f(x + dx * s)}" cy="{_f(y + dy * s)}" r="{_f(s * 0.1)}" fill="#2A1A14"/>')
    out.append("</g>")
    return "".join(out)


def earth_day_every_day():
    """The whole round world, a seedling sprouting from the top, a leafy wreath, a bee and a butterfly on a sunny morning."""
    P = Pn("earth-day-every-day")
    o = [paper_bg(P, "#F2EEDA", "#5A6A3A", 601, tints=["#E2E8C4", "#FFFFFF"], blobs=[(300, 400, 236, 170, "#D8E8C0", 0.6)])]
    # soft sun rays
    for k in range(16):
        a = math.radians(k * 22.5)
        o.append(f'<path d="M {_f(300 + math.cos(a) * 150)} {_f(400 + math.sin(a) * 150)} L {_f(300 + math.cos(a - 0.08) * 260)} {_f(400 + math.sin(a - 0.08) * 260)} L {_f(300 + math.cos(a + 0.08) * 260)} {_f(400 + math.sin(a + 0.08) * 260)} Z" fill="#F6D27A" opacity="0.2"/>')
    cx, cy, r = 300, 390, 112
    # half wreath of leaves under the globe
    for side in (-1, 1):
        pts = [(cx + side * math.cos(math.radians(a)) * (r + 28), cy + math.sin(math.radians(a)) * (r + 20)) for a in range(-10, 100, 10)]
        o.append(ink(smooth_open(pts), LEAF_D, 3.4, 602 + side, 1, 0.9))
        for i, (px, py) in enumerate(pts[:-1]):
            a = math.degrees(math.atan2(pts[i + 1][1] - py, pts[i + 1][0] - px))
            o.append(p_leaf(P, px, py, 34, a - 150 * side + (0 if side > 0 else 0), [LEAF, LEAF_L, "#7A9A4A"][i % 3], 604 + i + side * 20, 0.34, ink_w=1.3))
            o.append(p_leaf(P, px, py, 30, a + 40 * side, [LEAF_L, LEAF, "#8AAE5A"][i % 3], 630 + i + side * 20, 0.34, ink_w=1.3))
    o.append(cast(cx + 8, cy + r + 18, r * 0.8, 10, "#3A4A2A", 0.25, 650))
    o.append(globe(P, cx, cy, r, 651))
    # seedling sprouting from the top
    o.append(stem(P, [(cx + 4, cy - r + 6), (cx + 2, cy - r - 20), (cx + 8, cy - r - 40)], LEAF_D, 5, 652, INK))
    o.append(p_leaf(P, cx + 6, cy - r - 34, 48, -155, LEAF_L, 653, 0.38))
    o.append(p_leaf(P, cx + 8, cy - r - 38, 54, -25, LEAF, 654, 0.38))
    o.append(f'<path d="{blob(cx + 4, cy - r + 4, 22, 6, 655, 0.1, 10)}" fill="#7A5A3A"/>')
    o.append(bee_p(P, 120, 300, 22, 656, rot=-10))
    o.append(f'<path d="M 140 304 C 170 330 150 360 182 352" stroke="#8A6A4A" stroke-width="1.8" fill="none" stroke-dasharray="3 6" stroke-linecap="round"/>')
    o.append(butterfly(P, 482, 296, 30, 657, col="#F2A23A", rot=14))
    o.append(ladybug(P, 172, 466, 12, 658, rot=-30))
    o.append(sparkles(659, 6, (80, 250, 520, 540), "#F2C25A", (6, 10), avoid=((160, 250, 450, 540),)))
    o.append(btext(P, 300, 108, "earth day", SERIF_IT, 92, "#2E6E74", [TEAL, TEAL_D, "#3E8A8E", TEAL_L], 660, max_w=420, shadow="#F6D27A", sh=(0.02, 0.03), hi="#A8D4D0"))
    o.append(flank(160, "EVERY DAY", BEBAS, 42, 12, LEAF, max_w=260, L=50, seed=661))
    o.append(ptext(300, 175, "EVERY DAY", BEBAS, 42, LEAF_D, max_w=260, ls=12))
    return finish(P, "".join(o), 662)


def apple_p(P, cx, cy, r, seed, col="#D2382A", rot=0, leaf=True, ink_c=INK):
    """Shiny red apple with a dimpled top, stem, leaf, blush and highlight."""
    pts = []
    for i in range(32):
        t = 2 * math.pi * i / 32
        x, y = math.cos(t), math.sin(t)
        k = 1 - 0.18 * max(0, -y) ** 6 - 0.1 * max(0, y) ** 4
        dent = 0.16 * math.exp(-((t - 1.5 * math.pi) ** 2) / 0.05)
        pts.append((cx + x * r * k * 1.04, cy + y * r * k * 0.96 + dent * r))
    d = smooth_closed(jitter(pts, seed, r * 0.008))
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    out.append(paint(P, d, col, [lt(col, 0.3), dk(col, 0.25), "#F2805A", "#8E1E16"], (cx - r, cy - r, cx + r, cy + r), seed, angle=-80, n=int(r * 1.6),
                     length=(r * 0.3, r * 0.9), width=(1, r * 0.06), curve=0.5, ink_c=None))
    out.append(f'<path d="{blob(cx + r * 0.3, cy + r * 0.2, r * 0.4, r * 0.35, seed + 1, 0.15, 12)}" fill="#F2C24A" opacity="0.22"/>')
    g = P.rg([(0, "#FFFFFF", 0.45), (0.35, "#FFFFFF", 0), (0.8, "#4A0A08", 0.25), (1, "#4A0A08", 0.5)], cx=0.34, cy=0.34, r=0.75)
    out.append(f'<path d="{d}" fill="url(#{g})"/>')
    out.append(f'<path d="M {_f(cx - r * 0.62)} {_f(cy - r * 0.05)} Q {_f(cx - r * 0.6)} {_f(cy - r * 0.55)} {_f(cx - r * 0.25)} {_f(cy - r * 0.68)}" stroke="#FFFFFF" stroke-width="{_f(r * 0.1)}" fill="none" stroke-linecap="round" opacity="0.7"/>')
    out.append(ink(d, ink_c, max(1.4, r * 0.04), seed, 2, 0.8))
    out.append(f'<path d="M {_f(cx)} {_f(cy - r * 0.72)} q {_f(r * 0.02)} {_f(-r * 0.25)} {_f(r * 0.14)} {_f(-r * 0.36)}" stroke="#5A3A1E" stroke-width="{_f(r * 0.09)}" fill="none" stroke-linecap="round"/>')
    if leaf:
        out.append(p_leaf(P, cx + r * 0.08, cy - r * 0.88, r * 0.62, -24, LEAF, seed + 2, 0.36, ink_c=ink_c))
    out.append("</g>")
    return "".join(out)


def book(P, x, y, w, h, col, seed, title_col=GOLD, pages="#FBF4E6", ink_c=INK, bands=True):
    """A closed book lying flat, spine toward us: cover, page block, gilt bands."""
    out = []
    cover = org_rect(x, y, w, h, seed, 0.6, 14, h * 0.25)
    out.append(paint(P, cover, col, [lt(col, 0.25), dk(col, 0.2)], (x, y, x + w, y + h), seed, angle=0, n=int(w / 6), length=(w * 0.1, w * 0.3), width=(1.2, 3),
                     shade=dk(col, 0.45), shade_op=0.4, shade_dir=(0, 0, 0, 1), ink_c=ink_c, ink_w=1.8))
    pg = org_rect(x + w - 2, y + h * 0.14, 10, h * 0.72, seed + 1, 0.3, 6, 2)
    out.append(f'<path d="{pg}" fill="{pages}" stroke="{ink_c}" stroke-width="1"/>')
    for k in range(3):
        yy = y + h * (0.3 + k * 0.2)
        out.append(f'<path d="M {_f(x + w)} {_f(yy)} l 8 0" stroke="#C8B89A" stroke-width="0.8"/>')
    if bands:
        for fx in (0.12, 0.88):
            out.append(f'<path d="M {_f(x + w * fx)} {_f(y + 2)} L {_f(x + w * fx)} {_f(y + h - 2)}" stroke="{title_col}" stroke-width="3" opacity="0.9"/>')
        out.append(f'<path d="{org_rect(x + w * 0.3, y + h * 0.3, w * 0.4, h * 0.4, seed + 2, 0.3, 8, 2)}" fill="{title_col}" opacity="0.85"/>')
    return "".join(out)


def chalk_text(P, x, y, s, font, size, col, seed, max_w=460, ls=0, anchor="middle", rot=0):
    """Chalk lettering: dusty fill, broken by speckled gaps, a faint smudge halo."""
    sz = fit_size(s, font, size, max_w, ls)
    if anchor == "middle" and ls:
        x += ls / 2
    lsa = f' letter-spacing="{ls}"' if ls else ""
    base = f'text-anchor="{anchor}" {font} font-size="{sz}"{lsa}'
    tr = f' transform="rotate({rot} {_f(x)} {_f(y)})"' if rot else ""
    w = measure(s, font, sz, ls)
    x0 = x - w / 2 if anchor == "middle" else x
    rnd = random.Random(seed)
    cid = P.id("ct")
    gaps = "".join(f'<path d="M {_f(rnd.uniform(x0, x0 + w))} {_f(rnd.uniform(y - sz, y + 4))} l {_f(rnd.uniform(4, 14))} {_f(rnd.uniform(-3, 1))}" stroke="#2E4A3A" stroke-width="{rnd.uniform(0.8, 2):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>'
                   for _ in range(int(w * sz / 70)))
    return (f'<g{tr}><text x="{_f(x)}" y="{_f(y)}" {base} fill="{col}" opacity="0.12" stroke="{col}" stroke-width="{_f(sz * 0.08)}" stroke-linejoin="round">{esc(s)}</text>'
            f'<text x="{_f(x)}" y="{_f(y)}" {base} fill="{col}" opacity="0.92">{esc(s)}</text>'
            f'<clipPath id="{cid}"><text x="{_f(x)}" y="{_f(y)}" {base}>{esc(s)}</text></clipPath><g clip-path="url(#{cid})">{gaps}</g></g>')


def thank_you_teacher():
    """Chalkboard lessons: chalk lettering, doodles, and the classic shiny apple on a stack of books with a pencil."""
    P = Pn("thank-you-teacher")
    o = [sky_wash(P, "#2E4A3A", "#26402F", ["#38584A", "#22382C", "#3E5E4E", "#4A6A5A"], 701, n=360, angle=-8, length=(60, 180), width=(6, 16), op=(0.08, 0.2))]
    o.append(mottle(702, ["#6A8A7A", "#1A2A20"], 12, op=(0.05, 0.12)))
    # half-erased smudges
    rnd = random.Random(703)
    for k in range(7):
        x, y = rnd.uniform(60, 540), rnd.uniform(60, 540)
        o.append(f'<path d="{blob(x, y, rnd.uniform(40, 80), rnd.uniform(16, 30), 704 + k, 0.2, 12, rnd.uniform(-20, 20))}" fill="#C8D8D0" opacity="0.05"/>')
    # wooden frame at the edges + chalk ledge
    for k, (x, y, w, h) in enumerate(((0, 0, 600, 26), (0, 574, 600, 26), (0, 0, 26, 600), (574, 0, 26, 600))):
        d = org_rect(x - 4, y - 4, w + 8, h + 8, 705 + k, 0.6, 30, 1)
        o.append(paint(P, d, WOOD, [WOOD_L, WOOD_D, "#A0683A"], (x, y, x + w, y + h), 705 + k, angle=0 if w > h else 90, n=60, length=(30, 90), width=(1, 3), ink_c=None))
    o.append(f'<rect x="26" y="26" width="548" height="548" fill="none" stroke="#1A2A20" stroke-width="3" opacity="0.6"/>')
    # chalk doodles
    W = "#F2F2EA"
    o.append(chalk_text(P, 118, 300, "A+", BEBAS, 56, "#F6D27A", 710, rot=-12))
    o.append(chalk_text(P, 500, 312, "abc", SERIF_IT, 40, W, 711, rot=8))
    o.append(chalk_text(P, 110, 466, "1+1=2", BEBAS, 34, "#F2B8C0", 712, rot=-6))
    o.append(f'<polygon points="{" ".join(f"{_f(x)},{_f(y)}" for x, y in star_pts(498, 450, 22, 10))}" fill="none" stroke="#F6D27A" stroke-width="2.6" stroke-linejoin="round" opacity="0.85"/>')
    o.append(f'<path d="M 470 390 q 20 -18 40 0 t 40 0" stroke="{W}" stroke-width="2.4" fill="none" stroke-linecap="round" opacity="0.6"/>')
    # books + apple + pencil on the ledge
    o.append(cast(300, 548, 170, 10, "#000000", 0.4, 713))
    o.append(book(P, 172, 500, 250, 46, "#C8503A", 714, title_col=GOLD_L))
    o.append(book(P, 186, 458, 222, 42, "#3E6E9A", 715, title_col=GOLD_L))
    o.append(book(P, 200, 420, 196, 38, "#E2A83A", 716, title_col="#7A4A1A"))
    o.append(pencil(P, 360, 418, 150, 180, 717, body="#F2C24A", w=16))
    o.append(apple_p(P, 290, 352, 64, 718))
    o.append(chalk_text(P, 300, 128, "thank you", SERIF_IT, 106, W, 719, max_w=450))
    o.append(chalk_text(P, 300, 236, "TEACHER", BEBAS, 110, "#F6D27A", 720, max_w=400, ls=10))
    o.append(f'<path d="{hline(150, 252, 450, 250, 721, 1.2)}" stroke="{W}" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.7"/>')
    return finish(P, "".join(o), 722)


def teacup(P, cx, cy, w, seed, col="#FBF6EE", band="#E8A0AA", leafc=LEAF_L, tea="#C88A4A"):
    """Porcelain teacup on a saucer, painted rosebud band, gold rim, curly handle."""
    h = w * 0.62
    out = [cast(cx + 6, cy + h * 0.62, w * 0.82, h * 0.1, "#3A2418", 0.3, seed)]
    sau = blob(cx, cy + h * 0.5, w * 0.78, h * 0.15, seed, 0.01, 30)
    out.append(paint(P, sau, col, ["#FFFFFF", "#E8E0D8"], (cx - w * 0.8, cy + h * 0.35, cx + w * 0.8, cy + h * 0.65), seed, angle=0, n=20, shade="#C8B8C0", shade_op=0.5, ink_c=INK, ink_w=2))
    out.append(ink(blob(cx, cy + h * 0.48, w * 0.66, h * 0.11, seed + 1, 0.01, 30), GOLD, 2.2, seed + 1, 1, 0.8))
    # handle
    hx = cx + w * 0.47
    hd = smooth_closed([(hx - 6, cy - h * 0.28), (hx + w * 0.2, cy - h * 0.36), (hx + w * 0.26, cy - h * 0.1), (hx + w * 0.1, cy + h * 0.16), (hx - 8, cy + h * 0.2),
                        (hx - 8, cy + h * 0.08), (hx + w * 0.08, cy + h * 0.02), (hx + w * 0.14, cy - h * 0.14), (hx + w * 0.1, cy - h * 0.24), (hx - 6, cy - h * 0.16)])
    out.append(paint(P, hd, col, ["#FFFFFF", "#E2D8CC"], (hx - 8, cy - h * 0.4, hx + w * 0.3, cy + h * 0.2), seed + 2, n=8, shade="#B8A8A0", shade_op=0.5, ink_c=INK, ink_w=2))
    body = smooth_closed([(cx - w / 2, cy - h * 0.42), (cx - w * 0.47, cy - h * 0.05), (cx - w * 0.32, cy + h * 0.32), (cx, cy + h * 0.44), (cx + w * 0.32, cy + h * 0.32), (cx + w * 0.47, cy - h * 0.05), (cx + w / 2, cy - h * 0.42), (cx, cy - h * 0.36)])
    inner = [paint(P, body, col, ["#FFFFFF", "#EEE4DA"], (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), seed + 3, n=20, ink_c=None)]
    # rosebud band
    by = cy - h * 0.12
    inner.append(f'<path d="{hline(cx - w / 2, by - h * 0.16, cx + w / 2, by - h * 0.16, seed + 4, 0.5)}" stroke="{GOLD}" stroke-width="2.4" fill="none"/>')
    for k in range(-3, 4):
        x = cx + k * w * 0.15
        yy = by + abs(k) * h * 0.02
        inner.append(p_leaf(P, x - 4, yy + 2, w * 0.07, 160, leafc, seed + 10 + k, 0.4, ink_c=None, vein=False, shade=False))
        inner.append(p_leaf(P, x + 4, yy + 2, w * 0.07, 20, leafc, seed + 20 + k, 0.4, ink_c=None, vein=False, shade=False))
        inner.append(f'<path d="{blob(x, yy - 2, w * 0.032, w * 0.028, seed + 30 + k, 0.1, 10)}" fill="{band}"/>'
                     f'<path d="M {_f(x - w * 0.015)} {_f(yy - 3)} q {_f(w * 0.015)} {_f(-w * 0.015)} {_f(w * 0.03)} 0" stroke="{dk(band, 0.3)}" stroke-width="1.2" fill="none"/>')
    g = P.lg([(0, "#FFFFFF", 0.4), (0.3, "#FFFFFF", 0), (0.7, "#7A5A6A", 0), (1, "#7A5A6A", 0.35)], 0, 0, 1, 0)
    inner.append(f'<rect x="{_f(cx - w / 2)}" y="{_f(cy - h / 2)}" width="{_f(w)}" height="{_f(h)}" fill="url(#{g})"/>')
    cid = P.clip(f'<path d="{body}"/>')
    out.append(f'<g clip-path="url(#{cid})">{"".join(inner)}</g>')
    out.append(ink(body, INK, 2.4, seed + 3, 2, 0.85))
    rim = blob(cx, cy - h * 0.42, w / 2, h * 0.1, seed + 5, 0.01, 26)
    out.append(f'<path d="{rim}" fill="{col}"/>' + ink(rim, GOLD_D, 2.2, seed + 5, 1, 0.8))
    out.append(f'<path d="{blob(cx, cy - h * 0.41, w / 2 - 8, h * 0.075, seed + 6, 0.02, 24)}" fill="{tea}"/>')
    out.append(f'<path d="{blob(cx - w * 0.1, cy - h * 0.42, w * 0.12, h * 0.025, seed + 7, 0.1, 12)}" fill="#F2C890" opacity="0.6"/>')
    return "".join(out)


def best_mom_ever():
    """Tea for the best mom: a rosebud teacup on its saucer, steam curling into a heart, garden peonies beside it."""
    P = Pn("best-mom-ever")
    o = [paper_bg(P, "#FBE8E4", "#8A5A5A", 801, tints=["#F6D2CC", "#FFFFFF"], blobs=[(300, 420, 230, 150, "#F6D0CC", 0.6), (300, 420, 160, 110, "#FFF4EC", 0.5)])]
    rnd = random.Random(802)
    for i in range(30):
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 580)
        if 70 < x < 530 and 40 < y < 550:
            continue
        o.append(f'<path d="{blob(x, y, rnd.uniform(4, 7), rnd.uniform(3, 5), i, 0.1, 8, rnd.uniform(0, 180))}" fill="{rnd.choice([ROSE, LEAF_L, "#F2B8BE"])}" opacity="0.5"/>')
    # peonies behind the cup, left
    for k, (x, y, L, a) in enumerate(((120, 420, 78, -150), (140, 470, 70, 170), (160, 392, 64, -100), (100, 400, 66, -125), (226, 470, 54, -30), (120, 470, 60, 130))):
        o.append(p_leaf(P, x, y, L, a, [LEAF, LEAF_L, "#6E9A5A"][k % 3], 803 + k, 0.36))
    o.append(peony(P, 140, 418, 62, "#E8899A", 810, rot=10))
    o.append(peony(P, 214, 482, 42, "#F6C2C8", 811, rot=-20))
    o.append(blossom(P, 96, 492, 15, 812, col="#FBE4E6"))
    o.append(blossom(P, 196, 360, 12, 820, col="#FBE4E6"))
    cx_, cy_ = 352, 442
    o.append(teacup(P, cx_, cy_, 232, 813))
    # steam into a heart
    hx = cx_ - 6
    d = f"M {hx - 22} 380 C {hx - 46} 352 {hx - 2} 340 {hx - 20} 316 C {hx - 40} 290 {hx - 64} 258 {hx - 32} 244 C {hx - 12} 236 {hx} 254 {hx} 266 C {hx} 254 {hx + 14} 236 {hx + 34} 244 C {hx + 66} 258 {hx + 36} 294 {hx} 322"
    o.append(f'<path d="{d}" stroke="#FFFFFF" stroke-width="8" fill="none" stroke-linecap="round" opacity="0.92"/>'
             f'<path d="{d}" stroke="#E8B0B4" stroke-width="2.2" fill="none" stroke-linecap="round" opacity="0.5" transform="translate(2 2.5)"/>')
    o.append(f'<path d="M {hx + 44} 380 c 14 -18 -8 -30 8 -48" stroke="#FFFFFF" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.7"/>')
    # a tea bag tag hanging over the rim
    o.append(f'<path d="M 444 372 q 18 12 20 44" stroke="#B8A88A" stroke-width="1.4" fill="none"/>')
    tag = org_rect(450, 414, 28, 32, 814, 0.4, 8, 2)
    o.append(paint(P, tag, "#FBF4E6", ["#FFFFFF"], (450, 414, 478, 446), 814, n=0, ink_c=INK, ink_w=1.4) + p_heart(P, 464, 431, 8, ROSE, 815, n=2, hi=False))
    o.append(sparkles(816, 6, (80, 250, 520, 540), GOLD, (6, 10), avoid=((70, 250, 480, 540),)))
    o.append(btext(P, 300, 104, "best", SERIF_IT, 90, ROSE, ["#E8899A", "#B84A5A", "#F2B8BE"], 817, max_w=240, shadow="#F6D0CC", sh=(0.02, 0.03)))
    o.append(btext(P, 300, 196, "MOM EVER", BEBAS, 112, "#7A2E46", ["#9A4A62", "#5A1A30", "#B85A74"], 818, ls=8, max_w=440, shadow="#F2B8BE", sh=(0.025, 0.035), hi="#E8A0B4"))
    o.append(ptext(300, 234, "HAPPY MOTHER'S DAY", BEBAS, 24, ROSE, max_w=260, ls=7))
    return finish(P, "".join(o), 819)


def mom_youre_the_best():
    """A hand-tied bouquet of peonies, tulips and daisies in kraft paper with a satin ribbon and a little gift tag."""
    P = Pn("mom-youre-the-best")
    o = [paper_bg(P, "#E6EEDC", "#4A5A3A", 901, tints=["#D2E2C4", "#FFFFFF"], blobs=[(300, 380, 210, 200, "#F6EEE0", 0.7)])]
    o.append(cast(312, 548, 90, 8, "#3A2418", 0.25, 902))
    o.append('<g transform="translate(300 548) scale(1.13) translate(-300 -548)">')
    # greenery fan behind the flowers
    for k, (x, y, L, a, col) in enumerate(((300, 400, 120, -150, LEAF), (300, 400, 120, -30, LEAF), (300, 400, 112, -122, LEAF_L), (300, 400, 112, -58, LEAF_L),
                                           (300, 400, 130, -98, "#7A9A5A"), (300, 400, 100, -170, "#6E9A5A"), (300, 400, 100, -10, "#6E9A5A"))):
        o.append(p_leaf(P, x, y, L * 1.35, a, col, 903 + k, 0.26))
    # eucalyptus sprigs
    for side in (-1, 1):
        for i in range(6):
            t = i / 6
            px, py = 300 + side * (60 + t * 120), 390 - t * 130
            o.append(f'<path d="{blob(px, py, 11, 9, 920 + i + side * 10, 0.1, 10)}" fill="#9AB8A8" stroke="{INK}" stroke-width="1" opacity="0.95"/>')
        o.append(ink(smooth_open([(300, 400), (300 + side * 120, 330), (300 + side * 182, 256)]), "#7A8A7A", 1.6, 930 + side, 1, 0.8))
    # tulips + flowers
    o.append(tulip(P, 232, 400, 122, "#F2A23A", 940, lean=-0.22, leaves=False, head=32))
    o.append(tulip(P, 372, 400, 126, "#E86A7A", 941, lean=0.2, leaves=False, head=32))
    o.append(peony(P, 300, 302, 62, "#E8899A", 942, rot=8))
    o.append(peony(P, 206, 342, 46, "#F6C2C8", 943, rot=-14))
    o.append(peony(P, 396, 346, 48, CORAL, 944, rot=20))
    o.append(daisy(P, 254, 384, 30, 945, rot=10))
    o.append(daisy(P, 352, 392, 28, 946, rot=-6))
    o.append(blossom(P, 300, 380, 16, 947, col="#FBE4E6"))
    # kraft paper cone
    cone_back = org_poly([(196, 386), (404, 386), (322, 548), (278, 548)], 950, 1, 14, 4)
    o.append(paint(P, cone_back, "#B8865A", ["#C8966A", "#9A6A40"], (196, 386, 404, 548), 950, n=20, ink_c=INK, ink_w=1.8))
    front = org_poly([(214, 420), (300, 396), (392, 418), (322, 552), (282, 552)], 951, 1, 14, 4)
    o.append(paint(P, front, "#D8A878", ["#E8C094", "#B8865A", "#F2D2A8"], (214, 396, 392, 552), 951, angle=-70, n=40, shade="#8A5A30", shade_op=0.4, shade_dir=(0, 0, 1, 0.2), ink_c=INK, ink_w=2.2))
    o.append(f'<path d="M 252 424 L 300 540 M 340 416 L 312 540" stroke="#9A6A40" stroke-width="1.4" opacity="0.5"/>')
    # ribbon bow + tag
    o.append(f'<path d="{org_rect(270, 470, 66, 14, 952, 0.5, 8, 2)}" fill="{ROSE}" stroke="{INK}" stroke-width="1.4"/>')
    for sg, L in ((-1, 56), (1, 48)):
        o.append(f'<path d="M 303 478 q {sg * 18} 26 {sg * 10} {L}" stroke="{ROSE}" stroke-width="8" fill="none" stroke-linecap="round"/>')
    o.append(bow_p(P, 303, 478, 40, ROSE, 953))
    o.append(f'<path d="M 316 482 q 36 10 56 28" stroke="#8A6A4A" stroke-width="1.4" fill="none"/>')
    tag = org_poly([(366, 500), (420, 488), (430, 528), (376, 540)], 954, 0.4, 10, 3)
    o.append(paint(P, tag, "#FBF4E6", ["#FFFFFF", "#EADCC6"], (366, 488, 430, 540), 954, n=4, ink_c=INK, ink_w=1.6))
    o.append(f'<circle cx="374" cy="506" r="3" fill="#8A6A4A"/>')
    o.append(f'<text x="400" y="522" text-anchor="middle" {SERIF_IT} font-size="20" fill="{CRAN}" transform="rotate(-12 400 520)">xo</text>')
    o.append('</g>')
    o.append(btext(P, 300, 110, "mom,", SERIF_IT, 104, "#7A2E46", ["#9A4A62", "#5A1A30", "#B85A74"], 955, max_w=260, shadow="#F6C2C8", sh=(0.02, 0.03), hi="#E8A0B4"))
    o.append(btext(P, 300, 182, "YOU'RE THE BEST", BEBAS, 58, LEAF_D, [LEAF, LEAF_D, "#4A7A3A"], 956, ls=6, max_w=440, shadow="#F6EEE0", sh=(0.02, 0.03)))
    return finish(P, "".join(o), 957)

# --------------------------------------------------------------- graduation
def tassel(P, x, top, knot_y, L, seed, col=GOLD, cord=True, ink_c=INK, sway=0.0):
    """Graduation tassel: cord, wrapped head, fanned strands, a little charm."""
    out = []
    if cord:
        out.append(ink(smooth_open([(x - 8, top), (x + 6 + sway * 0.3, (top + knot_y) / 2), (x + sway, knot_y)]), dk(col, 0.25), 5, seed, 1, 1))
        out.append(f'<path d="{smooth_open([(x - 8, top), (x + 6 + sway * 0.3, (top + knot_y) / 2), (x + sway, knot_y)])}" stroke="{lt(col, 0.4)}" stroke-width="1.6" fill="none" opacity="0.8"/>')
    hx = x + sway
    head = smooth_closed([(hx - 10, knot_y), (hx + 10, knot_y), (hx + 14, knot_y + 22), (hx + 18, knot_y + 34), (hx - 18, knot_y + 34), (hx - 14, knot_y + 22)])
    out.append(paint(P, head, col, [GOLD_L, GOLD_D], (hx - 18, knot_y, hx + 18, knot_y + 34), seed, n=8, shade=GOLD_D, shade_op=0.5, shade_dir=(0, 0, 1, 0), ink_c=ink_c, ink_w=1.6))
    for yy in (knot_y + 26, knot_y + 31):
        out.append(f'<path d="M {_f(hx - 17)} {_f(yy)} L {_f(hx + 17)} {_f(yy)}" stroke="{GOLD_D}" stroke-width="1.6"/>')
    rnd = random.Random(seed)
    fan = smooth_closed([(hx - 18, knot_y + 34), (hx + 18, knot_y + 34), (hx + 26, knot_y + 34 + L), (hx - 26, knot_y + 34 + L)])
    out.append(f'<path d="{fan}" fill="{dk(col, 0.1)}"/>')
    for k in range(46):
        x0 = hx + rnd.uniform(-17, 17)
        x1 = hx + (x0 - hx) * 1.5 + rnd.uniform(-3, 3)
        y1 = knot_y + 34 + L * rnd.uniform(0.9, 1.04)
        out.append(f'<path d="M {_f(x0)} {_f(knot_y + 34)} Q {_f(x0 + rnd.uniform(-2, 2))} {_f(knot_y + 34 + L * 0.5)} {_f(x1)} {_f(y1)}" stroke="{rnd.choice([GOLD_L, GOLD, GOLD_D, "#FFF0B8"])}" stroke-width="{rnd.uniform(1.2, 2.4):.1f}" fill="none" stroke-linecap="round"/>')
    out.append(ink(fan, ink_c, 1.4, seed, 1, 0.5))
    return "".join(out)


def mortarboard(P, cx, cy, w, seed, rot=0, col="#1E2A4A", tassel_side=1, tassel_len=70):
    """Graduation cap: board in perspective with a sheen, the skull cap beneath, button and tassel."""
    h = w * 0.42
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    sk = smooth_closed([(cx - w * 0.3, cy + h * 0.05), (cx - w * 0.3, cy + h * 0.55), (cx, cy + h * 0.72), (cx + w * 0.3, cy + h * 0.55), (cx + w * 0.3, cy + h * 0.05)])
    out.append(paint(P, sk, dk(col, 0.15), [lt(col, 0.2), dk(col, 0.3)], (cx - w * 0.3, cy, cx + w * 0.3, cy + h * 0.72), seed, angle=-90, n=30, shade="#000000", shade_op=0.4, shade_dir=(0, 0, 1, 0), ink_c=INK, ink_w=2.2))
    out.append(f'<path d="M {_f(cx - w * 0.3)} {_f(cy + h * 0.5)} Q {_f(cx)} {_f(cy + h * 0.7)} {_f(cx + w * 0.3)} {_f(cy + h * 0.5)}" stroke="{lt(col, 0.3)}" stroke-width="2" fill="none" opacity="0.6"/>')
    pts = [(cx - w / 2, cy), (cx, cy - h * 0.5), (cx + w / 2, cy), (cx, cy + h * 0.5)]
    board = org_poly(pts, seed + 1, 0.8, 14, 4)
    edge = org_poly([(cx - w / 2, cy), (cx, cy + h * 0.5), (cx + w / 2, cy), (cx + w / 2, cy + 8), (cx, cy + h * 0.5 + 8), (cx - w / 2, cy + 8)], seed + 2, 0.5, 14, 2)
    out.append(f'<path d="{edge}" fill="{dk(col, 0.4)}"/>' + ink(edge, INK, 1.8, seed + 2, 1, 0.8))
    out.append(paint(P, board, col, [lt(col, 0.25), dk(col, 0.2), lt(col, 0.4)], (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), seed + 1, angle=-25, n=60, length=(w * 0.05, w * 0.2),
                     width=(1.5, 4), light="#8A9ACC", light_op=0.4, shade_dir=(0, 0, 1, 1), ink_c=INK, ink_w=2.4))
    out.append(f'<path d="M {_f(cx - w * 0.36)} {_f(cy - h * 0.04)} L {_f(cx - w * 0.06)} {_f(cy - h * 0.4)}" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity="0.25"/>')
    tx = cx + tassel_side * w * 0.42
    out.append(ink(f"M {_f(cx)} {_f(cy)} Q {_f((cx + tx) / 2)} {_f(cy - h * 0.08)} {_f(tx)} {_f(cy + h * 0.05)}", GOLD_D, 4.5, seed + 3, 1, 1))
    out.append(f'<path d="M {_f(cx)} {_f(cy)} Q {_f((cx + tx) / 2)} {_f(cy - h * 0.08)} {_f(tx)} {_f(cy + h * 0.05)}" stroke="{GOLD_L}" stroke-width="1.5" fill="none"/>')
    out.append(ball_paint(P, cx, cy, 9, GOLD, seed + 4))
    out.append(tassel(P, tx, cy + h * 0.05, cy + h * 0.05 + 6, tassel_len, seed + 5, cord=False))
    out.append("</g>")
    return "".join(out)


def diploma(P, x0, y0, x1, y1, r, seed, ribbon_c=CRAN, ink_c=INK):
    """Rolled diploma lying at an angle: parchment roll with a spiral end and a tied ribbon."""
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    L = math.hypot(x1 - x0, y1 - y0)
    out = [cast((x0 + x1) / 2 + 6, (y0 + y1) / 2 + r + 6, L * 0.52, 8, "#3A2418", 0.3, seed)]
    out.append(f'<g transform="rotate({ang:.1f} {_f(x0)} {_f(y0)})">')
    body = org_rect(x0, y0 - r, L, 2 * r, seed, 0.6, 16, r * 0.4)
    out.append(paint(P, body, "#F6EAD0", ["#FFF8E8", "#E2CCA4", "#F2E0BC"], (x0, y0 - r, x0 + L, y0 + r), seed, angle=0, n=30, shade="#B89A6A", shade_op=0.5, shade_dir=(0, 0, 0, 1), ink_c=ink_c, ink_w=2))
    out.append(f'<path d="M {_f(x0 + 6)} {_f(y0 - r * 0.5)} L {_f(x0 + L - 10)} {_f(y0 - r * 0.5)}" stroke="#FFFFFF" stroke-width="3" opacity="0.6"/>')
    end = blob(x0 + L, y0, r * 0.45, r, seed + 1, 0.02, 14)
    out.append(f'<path d="{end}" fill="#EADBB8" stroke="{ink_c}" stroke-width="1.6"/>')
    out.append(f'<path d="M {_f(x0 + L)} {_f(y0 - r * 0.6)} a {_f(r * 0.3)} {_f(r * 0.6)} 0 1 1 {_f(-r * 0.05)} {_f(r * 1.0)} a {_f(r * 0.18)} {_f(r * 0.35)} 0 1 1 0 {_f(-r * 0.5)}" stroke="#B89A6A" stroke-width="1.6" fill="none"/>')
    mx = x0 + L * 0.5
    out.append(f'<path d="{org_rect(mx - 9, y0 - r - 1, 18, 2 * r + 2, seed + 2, 0.3, 6, 1)}" fill="{ribbon_c}" stroke="{ink_c}" stroke-width="1.2"/>')
    out.append(bow_p(P, mx, y0 + r * 0.1, r * 1.6, ribbon_c, seed + 3, ink_c))
    for sg in (-1, 1):
        out.append(f'<path d="M {_f(mx)} {_f(y0 + r * 0.1)} q {_f(sg * r * 0.4)} {_f(r * 1.2)} {_f(sg * r * 0.2)} {_f(r * 2)} l {_f(sg * 6)} -4" stroke="{ribbon_c}" stroke-width="6" fill="none" stroke-linecap="round"/>')
    out.append("</g>")
    return "".join(out)


def congrats_grad():
    """Caps in the air: a mortarboard tossed high against navy, tassel flying, confetti and gold stars falling."""
    P = Pn("congrats-grad")
    o = [sky_wash(P, "#1E2A4E", "#2E3E6E", [NAVY, NAVY_L, "#2A3A66", "#18224A"], 1001, n=300, angle=-10, mid=(0.5, "#24325C"))]
    o.append(mottle(1002, ["#4A5A9A", "#101830"], 10))
    o.append(P.glow(300, 210, 230, "#F6D27A", 0.35))
    # more caps far away in the toss
    o.append(f'<g opacity="0.55">{mortarboard(P, 112, 128, 86, 1003, rot=24, col="#3E4E86", tassel_len=26)}</g>')
    o.append(f'<g opacity="0.55">{mortarboard(P, 494, 112, 80, 1004, rot=-30, col="#3E4E86", tassel_side=-1, tassel_len=24)}</g>')
    o.append(confetti(1005, 80, (30, 30, 570, 570), [GOLD, GOLD_L, "#FFFFFF", CORAL_L, "#8FC8C0"], avoid=((120, 100, 480, 330), (60, 330, 540, 545))))
    o.append(sparkles(1006, 10, (60, 60, 540, 340), GOLD_L, (5, 11), avoid=((150, 120, 450, 330),)))
    o.append(mortarboard(P, 300, 196, 270, 1007, rot=-10, tassel_len=78))
    o.append(streamer(P, curl_pts(60, 300, 90, 2.2, 12, 100, 1008), 6, GOLD, 1008, twist=16))
    o.append(streamer(P, curl_pts(540, 290, 90, 2.2, 12, 80, 1009), 6, CORAL_L, 1009, twist=16))
    o.append(btext(P, 300, 410, "congrats", SERIF_IT, 116, GOLD, [GOLD_L, GOLD_D, "#F2C25A", "#FFF0B8"], 1010, max_w=440, shadow="#101830", sh=(0.02, 0.035), hi="#FFF6D8"))
    o.append(btext(P, 300, 532, "GRAD!", ANTON, 122, "#F6EEDF", ["#FFFFFF", "#E8DCC8", "#F2E8D6"], 1011, ls=10, max_w=360, shadow=CRAN, sh=(0.025, 0.035)))
    return finish(P, "".join(o), 1012)


def worth_the_hassle():
    """A gold tassel hangs beside the old joke in burgundy and gold, a beribboned diploma underneath."""
    P = Pn("worth-the-hassle")
    o = [paper_bg(P, "#F6EEDF", "#6A3A2A", 1101, tints=["#EADCC4", "#FFFFFF"], blobs=[(300, 300, 240, 220, "#F2E2C8", 0.5)])]
    BUR, BUR_D = "#7A1E30", "#4E0E1C"
    o.append(sparkles(1102, 10, (60, 60, 540, 540), GOLD, (5, 10), avoid=((60, 60, 400, 420), (400, 20, 540, 470), (90, 420, 520, 540))))
    # tassel hanging from the top edge
    o.append(cast(486, 470, 40, 6, "#3A2418", 0.2, 1103))
    o.append(tassel(P, 470, -10, 268, 150, 1104, sway=8))
    o.append(twinkle(512, 420, 10, GOLD) + twinkle(440, 300, 6, GOLD))
    o.append(btext(P, 70, 124, "the", SERIF_IT, 64, BUR, [BUR, BUR_D, "#9A3A4A"], 1105, anchor="start", max_w=200, shadow="#F2D2B8", sh=(0.02, 0.03)))
    o.append(btext(P, 66, 232, "TASSEL", ANTON, 116, BUR, [BUR, BUR_D, "#9A3A4A", "#A84A5A"], 1106, anchor="start", ls=3, max_w=340, shadow=GOLD, sh=(0.025, 0.035), hi="#D88A9A"))
    o.append(btext(P, 70, 296, "was worth the", SERIF_IT, 50, "#2E3E6E", [NAVY, NAVY_L, NAVY_D], 1107, anchor="start", max_w=340, shadow="#F2D2B8", sh=(0.02, 0.03)))
    o.append(btext(P, 66, 404, "HASSLE", ANTON, 116, BUR, [BUR, BUR_D, "#9A3A4A", "#A84A5A"], 1108, anchor="start", ls=3, max_w=340, shadow=GOLD, sh=(0.025, 0.035), hi="#D88A9A"))
    o.append(diploma(P, 120, 488, 470, 470, 22, 1109, ribbon_c=BUR))
    o.append(f'<path d="{hline(70, 316, 380, 316, 1110, 1)}" stroke="{GOLD}" stroke-width="2.4" fill="none" opacity="0.0"/>')
    return finish(P, "".join(o), 1111)


# --------------------------------------------------------------- Father's Day
def glasses(P, cx, cy, w, seed, rot=0, frame="#5A3018"):
    """Folded reading glasses: round tortoiseshell rims, glass glints, arms folded behind."""
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    r = w * 0.2
    for sg in (-1, 1):
        lx = cx + sg * w * 0.25
        out.append(f'<path d="M {_f(lx - sg * r * 0.2)} {_f(cy - r * 0.7)} q {_f(-sg * w * 0.05)} {_f(-r * 0.6)} {_f(-sg * w * 0.42)} {_f(-r * 0.2)}" stroke="{frame}" stroke-width="{_f(w * 0.035)}" fill="none" stroke-linecap="round"/>')
    for sg in (-1, 1):
        lx = cx + sg * w * 0.25
        lens = blob(lx, cy, r, r * 0.9, seed + sg, 0.02, 16)
        out.append(f'<path d="{lens}" fill="#D8EAF2" opacity="0.5"/>')
        out.append(f'<path d="M {_f(lx - r * 0.5)} {_f(cy + r * 0.2)} L {_f(lx - r * 0.05)} {_f(cy - r * 0.45)}" stroke="#FFFFFF" stroke-width="{_f(r * 0.16)}" stroke-linecap="round" opacity="0.85"/>')
        out.append(f'<path d="{lens}" fill="none" stroke="{frame}" stroke-width="{_f(w * 0.05)}"/>')
        out.append(f'<path d="{lens}" fill="none" stroke="#C88A4A" stroke-width="{_f(w * 0.018)}" stroke-dasharray="4 7" opacity="0.8"/>')
    out.append(f'<path d="M {_f(cx - w * 0.07)} {_f(cy - r * 0.2)} q {_f(w * 0.07)} {_f(-r * 0.4)} {_f(w * 0.14)} 0" stroke="{frame}" stroke-width="{_f(w * 0.04)}" fill="none"/>')
    out.append("</g>")
    return "".join(out)


def newspaper(P, x, y, w, h, seed, rot=0):
    out = [f'<g transform="rotate({rot} {_f(x + w / 2)} {_f(y + h / 2)})">']
    out.append(f'<path d="{org_rect(x + 6, y + 8, w, h, seed + 9, 0.6, 14, 2)}" fill="#3A2418" opacity="0.2"/>')
    d = org_rect(x, y, w, h, seed, 0.6, 14, 2)
    out.append(paint(P, d, "#F2EEE4", ["#FFFFFF", "#E2DCCC", "#EAE4D6"], (x, y, x + w, y + h), seed, angle=0, n=20, ink_c=INK, ink_w=1.8))
    out.append(f'<path d="{org_rect(x + 12, y + 12, w - 24, h * 0.16, seed + 1, 0.3, 10, 1)}" fill="#3A3A44"/>')
    out.append(f'<path d="{org_rect(x + w * 0.54, y + h * 0.36, w * 0.38, h * 0.3, seed + 2, 0.3, 10, 1)}" fill="#B8B4A8"/>')
    for k in range(9):
        yy = y + h * 0.36 + k * h * 0.065
        ww = (w * 0.42) if yy < y + h * 0.68 else (w - 24)
        out.append(f'<path d="M {_f(x + 12)} {_f(yy)} l {_f(ww * random.Random(seed + k).uniform(0.7, 1))} 0" stroke="#8A867A" stroke-width="2.2" opacity="0.8"/>')
    out.append(f'<path d="M {_f(x + w * 0.5)} {_f(y + 4)} L {_f(x + w * 0.5)} {_f(y + h - 4)}" stroke="#C8C2B2" stroke-width="1.4"/>')
    out.append("</g>")
    return "".join(out)


def best_dad_ever():
    """Sunday morning for Dad: his striped mug steaming, the paper folded, reading glasses set down on the table."""
    P = Pn("best-dad-ever")
    o = [sky_wash(P, "#22305A", "#2E3E6A", [NAVY, NAVY_L, "#2A3A66", "#1A2448"], 1201, box=(0, 0, 600, 430), n=260, angle=-6, mid=(0.6, "#26345E"))]
    # wallpaper pinstripes
    for k in range(13):
        x = 20 + k * 48
        o.append(f'<path d="{hline(x, 0, x + 2, 430, 1202 + k, 1, 40)}" stroke="#E2B04A" stroke-width="2" fill="none" opacity="0.18"/>')
    o.append(P.glow(330, 400, 240, "#F6C860", 0.3))
    table = org_poly([(-10, 424), (610, 420), (610, 610), (-10, 610)], 1220, 1, 30, 2)
    o.append(paint(P, table, "#A8703E", ["#C08A50", "#8A5A30", "#B87E48", "#7A4A26"], (-10, 420, 610, 610), 1220, angle=0, n=200, length=(40, 160), width=(1.2, 3.5), op=(0.25, 0.6), ink_c=None))
    for k in range(4):
        y = 448 + k * 42
        o.append(f'<path d="{hline(-10, y, 610, y + 2, 1221 + k, 0.8)}" stroke="#6A3E1E" stroke-width="2" fill="none" opacity="0.4"/>')
    o.append(f'<path d="{hline(-10, 424, 610, 420, 1225, 0.6)}" stroke="#3A2418" stroke-width="2.6" fill="none" opacity="0.7"/>')
    o.append(newspaper(P, 92, 368, 210, 130, 1230, rot=-8))
    o.append(mug(P, 384, 334, 150, 160, "#F2EADA", 1240, pattern="stripes", pcol=NAVY, handle=1, drink="#5A3420"))
    o.append(f'<path d="{org_rect(338, 390, 92, 54, 1241, 0.5, 10, 4)}" fill="#E2A83A" stroke="{INK}" stroke-width="1.6"/>')
    o.append(ptext(384, 432, "DAD", ANTON, 40, NAVY_D, max_w=80, ls=3))
    for k, sx in enumerate((354, 388, 418)):
        o.append(f'<path d="M {sx} 318 c -10 -10 8 -18 -2 -30 c -8 -10 6 -16 0 -24" stroke="#FFFFFF" stroke-width="{5 - k % 2}" fill="none" stroke-linecap="round" opacity="0.55"/>')
    o.append(cast(214, 524, 70, 6, "#3A2418", 0.3, 1251))
    o.append(glasses(P, 210, 504, 140, 1250, rot=-8))
    o.append(btext(P, 300, 104, "best", SERIF_IT, 92, "#E2A83A", [GOLD_L, GOLD_D, "#F2C25A"], 1260, max_w=240, shadow="#121a36", sh=(0.02, 0.035)))
    o.append(btext(P, 300, 214, "DAD EVER", BEBAS, 126, "#F6EEDF", ["#FFFFFF", "#E8DCC8", "#F2E8D6"], 1261, ls=8, max_w=440, shadow="#121A36", sh=(0.025, 0.035)))
    o.append(ptext(300, 254, "HAPPY FATHER'S DAY", BEBAS, 26, "#E2A83A", max_w=280, ls=8))
    return finish(P, "".join(o), 1262)


def trout(P, cx, cy, L, seed, rot=0):
    """A rainbow trout arching out of the water."""
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    h = L * 0.26
    body = smooth_closed([(cx - L * 0.5, cy), (cx - L * 0.3, cy - h * 0.8), (cx + L * 0.1, cy - h), (cx + L * 0.4, cy - h * 0.6), (cx + L * 0.52, cy - h * 0.1), (cx + L * 0.46, cy + h * 0.3),
                          (cx + L * 0.1, cy + h * 0.85), (cx - L * 0.3, cy + h * 0.6)])
    tail = smooth_closed([(cx - L * 0.46, cy), (cx - L * 0.68, cy - h * 0.9), (cx - L * 0.62, cy), (cx - L * 0.7, cy + h * 0.85)])
    out.append(paint(P, tail, "#7A8A5A", ["#9AAA6A", "#5A6A3A"], (cx - L * 0.7, cy - h, cx - L * 0.4, cy + h), seed, angle=180, n=8, ink_c=INK, ink_w=1.6))
    for fx, fy, sg in ((0.0, -0.95, -1), (-0.1, 0.8, 1)):
        fin = smooth_closed([(cx + fx * L, cy + fy * h), (cx + (fx - 0.12) * L, cy + (fy + sg * 0.5) * h), (cx + (fx - 0.2) * L, cy + fy * h * 0.9)])
        out.append(f'<path d="{fin}" fill="#8A9A6A" stroke="{INK}" stroke-width="1.2"/>')
    inner = [paint(P, body, "#B8C08A", ["#D8DCA8", "#8A9A62", "#C8CC98"], (cx - L * 0.5, cy - h, cx + L * 0.55, cy + h), seed + 1, angle=0, n=30, ink_c=None)]
    inner.append(f'<path d="M {_f(cx - L * 0.5)} {_f(cy - h * 0.2)} Q {_f(cx)} {_f(cy - h * 0.3)} {_f(cx + L * 0.5)} {_f(cy - h * 0.1)} L {_f(cx + L * 0.5)} {_f(cy - h)} L {_f(cx - L * 0.5)} {_f(cy - h)} Z" fill="#5E7A4A" opacity="0.7"/>')
    inner.append(f'<path d="M {_f(cx - L * 0.45)} {_f(cy + h * 0.05)} Q {_f(cx)} {_f(cy + h * 0.1)} {_f(cx + L * 0.45)} {_f(cy + h * 0.05)}" stroke="#E2786A" stroke-width="{_f(h * 0.32)}" fill="none" opacity="0.7"/>')
    inner.append(f'<path d="M {_f(cx - L * 0.5)} {_f(cy + h * 0.45)} Q {_f(cx)} {_f(cy + h * 0.6)} {_f(cx + L * 0.5)} {_f(cy + h * 0.3)} L {_f(cx + L * 0.5)} {_f(cy + h)} L {_f(cx - L * 0.5)} {_f(cy + h)} Z" fill="#F2EEDC" opacity="0.8"/>')
    inner.append(dab_dots(seed + 2, int(L * 0.4), (cx - L * 0.45, cy - h * 0.85, cx + L * 0.35, cy - h * 0.1), ["#2A3A1E", "#3A2A1E"], (1, 2.2), (0.6, 0.9)))
    cid = P.clip(f'<path d="{body}"/>')
    out.append(f'<g clip-path="url(#{cid})">{"".join(inner)}</g>')
    out.append(ink(body, INK, 2, seed, 2, 0.8))
    out.append(f'<path d="M {_f(cx + L * 0.32)} {_f(cy - h * 0.6)} q {_f(-L * 0.05)} {_f(h * 0.6)} {_f(L * 0.02)} {_f(h * 1.0)}" stroke="{INK}" stroke-width="1.4" fill="none" opacity="0.6"/>')
    out.append(f'<circle cx="{_f(cx + L * 0.4)}" cy="{_f(cy - h * 0.3)}" r="{_f(h * 0.13)}" fill="#1A1210"/><circle cx="{_f(cx + L * 0.41)}" cy="{_f(cy - h * 0.34)}" r="{_f(h * 0.04)}" fill="#FFFFFF"/>')
    out.append("</g>")
    return "".join(out)


def reel_cool_dad():
    """Sunrise on the lake: a fishing rod propped on the dock, the bobber dipping, a trout leaping clear of the water."""
    P = Pn("reel-cool-dad")
    o = [sky_wash(P, "#F6C8A0", "#FBE6C8", ["#F8D4B0", "#F2B890", "#FBE2C4", "#FFF0DC"], 1301, box=(0, 0, 600, 330), n=200, angle=-3, mid=(0.5, "#F8D8B4"))]
    o.append(P.glow(420, 300, 160, "#FFF2C0", 0.85))
    o.append(f'<path d="{blob(420, 300, 52, 52, 1302, 0.01, 24)}" fill="#FFE9A8" opacity="0.95"/>')
    o.append(cloud(P, 120, 226, 64, 14, 1303, base="#FFF4EA", shade="#F2C8B4", op=0.75))
    # far shore pines (cool, misty) and nearer ones
    o.append(far_trees(P, 330, 1304, "#8AA2A8", n=40, h=(30, 60), w=0.38))
    o.append(far_trees(P, 336, 1305, "#5E7E82", n=26, h=(40, 82), x=(-20, 260), w=0.4))
    o.append(far_trees(P, 336, 1306, "#5E7E82", n=14, h=(36, 70), x=(470, 620), w=0.4))
    # lake
    lake = "M -10 330 L 610 330 L 610 610 L -10 610 Z"
    g = P.lg([(0, "#9CC0C4"), (0.4, "#5E949C"), (1, "#2E6070")])
    o.append(f'<path d="{lake}" fill="url(#{g})"/>')
    o.append(strokes(P.id("s"), lake, (-30, 330, 610, 610), ["#B8D8D8", "#4A7E88", "#FFE2B8", "#7AAAB0"], 1307, 260, angle=0, length=(20, 80), width=(1, 3), opacity=(0.2, 0.5), curve=0.05))
    for k in range(12):
        y = 340 + k * 9
        w = 60 - k * 3
        o.append(f'<path d="M {420 - w} {y} L {420 + w} {y}" stroke="#FFE9A8" stroke-width="{3 - k * 0.15:.1f}" stroke-linecap="round" opacity="{0.8 - k * 0.05:.2f}"/>')
    o.append(f'<rect x="-10" y="330" width="620" height="12" fill="#FFFFFF" opacity="0.25"/>')
    # leaping trout + splash + ripples
    for k, rr in enumerate((24, 40, 58)):
        o.append(f'<ellipse cx="350" cy="500" rx="{rr * 1.6}" ry="{rr * 0.35}" fill="none" stroke="#E8F4F4" stroke-width="{3 - k * 0.6:.1f}" opacity="{0.8 - k * 0.2:.2f}"/>')
    o.append(trout(P, 352, 452, 128, 1310, rot=-22))
    rnd = random.Random(1311)
    for k in range(12):
        x, y = 350 + rnd.uniform(-60, 60), 494 - rnd.uniform(0, 50)
        o.append(f'<path d="{blob(x, y, rnd.uniform(2, 4.5), rnd.uniform(3, 6), 1312 + k, 0.1, 8)}" fill="#E8F6F6" stroke="#5E949C" stroke-width="0.8"/>')
    # dock
    dock = org_poly([(-10, 470), (230, 500), (230, 530), (-10, 520)], 1320, 0.8, 20, 2)
    o.append(paint(P, dock, "#A8784A", ["#C0905A", "#7A5230", "#D8A870"], (-10, 470, 230, 530), 1320, angle=6, n=60, length=(30, 80), width=(1.5, 3.5), shade="#5A3418", shade_op=0.4, ink_c=INK, ink_w=2))
    for k in range(5):
        x = 10 + k * 46
        o.append(f'<path d="M {x} {472 + k * 5.6} L {x + 4} {520 + k * 2}" stroke="#5A3418" stroke-width="2" opacity="0.6"/>')
    for k, x in enumerate((30, 120, 210)):
        post = org_rect(x - 9, 494 + k * 6, 18, 110, 1321 + k, 0.5, 12, 2)
        o.append(paint(P, post, "#7A5230", ["#8A6238", "#5A3418"], (x - 9, 494, x + 9, 610), 1321 + k, n=8, ink_c=INK, ink_w=1.6))
    o.append(f'<path d="{org_rect(-10, 520, 240, 14, 1324, 0.5, 20, 1)}" fill="#5A3418" opacity="0.7"/>')
    # tackle box
    tb = org_rect(70, 448, 70, 40, 1325, 0.5, 10, 3)
    o.append(paint(P, tb, "#3E7A5E", ["#5A9A7A", "#2A5A42"], (70, 448, 140, 488), 1325, n=8, shade="#1A3A2A", shade_op=0.4, ink_c=INK, ink_w=1.8))
    o.append(f'<path d="M 92 448 q 13 -12 26 0" stroke="#3A2418" stroke-width="3" fill="none"/><rect x="100" y="462" width="10" height="8" fill="{GOLD}" stroke="{INK}" stroke-width="1"/>')
    # rod propped from the dock, line to the bobber
    o.append(ink(f"M 150 500 L 452 262", "#3A2418", 5, 1330, 1, 1))
    o.append(f'<path d="M 150 500 L 452 262" stroke="#C8904A" stroke-width="2" opacity="0.8"/>')
    o.append(f'<path d="{org_rect(150, 494, 44, 12, 1331, 0.4, 8, 3)}" fill="#3A2418" transform="rotate(-38 150 500)"/>')
    o.append(f'<circle cx="196" cy="458" r="10" fill="#C8C2B2" stroke="{INK}" stroke-width="1.6"/><path d="M 196 458 l 8 6" stroke="{INK}" stroke-width="2"/>')
    o.append(f'<path d="M 452 262 Q 490 370 496 482" stroke="#F6F0E0" stroke-width="1.6" fill="none" opacity="0.9"/>')
    for k, rr in enumerate((12, 22)):
        o.append(f'<ellipse cx="498" cy="490" rx="{rr * 1.5}" ry="{rr * 0.32}" fill="none" stroke="#E8F4F4" stroke-width="1.8" opacity="{0.8 - k * 0.3:.2f}"/>')
    o.append(f'<path d="M 488 488 a 10 10 0 0 1 20 0 Z" fill="#D8342A" stroke="{INK}" stroke-width="1.4"/><path d="M 488 488 a 10 6 0 0 0 20 0 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="1.4"/>')
    o.append(btext(P, 300, 110, "reel cool", SERIF_IT, 100, "#2E5A66", ["#3E6E7A", "#1E4450", "#5A8A94"], 1340, max_w=420, shadow="#FBE6C8", sh=(0.02, 0.03), hi="#8ABAC2"))
    o.append(btext(P, 300, 248, "DAD", ANTON, 136, "#C8503A", ["#E2725B", "#9A3A28", "#D8604A"], 1341, ls=14, max_w=300, shadow="#2E5A66", sh=(0.025, 0.035), hi="#F4A78E"))
    return finish(P, "".join(o), 1342)

# --------------------------------------------------------------- weddings & summer
def wheel(P, cx, cy, r, seed, rim="#F2EEE4"):
    out = [f'<path d="{blob(cx, cy, r, r, seed, 0.01, 22)}" fill="#22201E"/>']
    out.append(strokes(P.id("s"), blob(cx, cy, r, r, seed, 0.01, 22), (cx - r, cy - r, cx + r, cy + r), ["#3A3632", "#141210"], seed, 16, angle=-40, length=(r * 0.3, r * 0.8), width=(1, 3), opacity=(0.3, 0.6), curve=0.6))
    out.append(f'<path d="{blob(cx, cy, r * 0.62, r * 0.62, seed + 1, 0.01, 18)}" fill="{rim}" stroke="{INK}" stroke-width="1.6"/>')
    g = P.rg([(0, "#FFFFFF"), (0.6, "#D8D4CC"), (1, "#8A867E")], cx=0.4, cy=0.38, r=0.6)
    out.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 0.4)}" fill="url(#{g})" stroke="{INK}" stroke-width="1.4"/>')
    out.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 0.1)}" fill="#8A867E"/>')
    out.append(ink(blob(cx, cy, r, r, seed, 0.01, 22), INK, 2, seed, 1, 0.8))
    return "".join(out)


def vintage_car(P, x, base, s, seed, body="#9CC8B4", roof="#F6EEDF", ink_c=INK):
    """Rounded 1950s coupe in profile, facing right: two-tone paint, chrome, whitewall tyres."""
    def S(px, py):
        return (x + px * s, base - py * s)
    out = [cast(x + 1.8 * s, base + 2, 2.0 * s, 0.1 * s, "#3A2418", 0.35, seed)]
    bodyp = [S(0, 0.32), S(0.02, 0.62), S(0.32, 0.72), S(0.85, 0.74), S(1.15, 1.2), S(2.25, 1.22), S(2.6, 0.82), S(3.3, 0.78), S(3.62, 0.6), S(3.64, 0.3), S(3.5, 0.18),
             S(0.2, 0.16)]
    bd = smooth_closed(jitter(bodyp, seed, s * 0.01))
    out.append(paint(P, bd, body, [lt(body, 0.3), dk(body, 0.2), lt(body, 0.15)], bbox(bodyp), seed, angle=-4, n=110, length=(s * 0.15, s * 0.5), width=(1.2, 3.5),
                     shade=dk(body, 0.4), shade_op=0.45, shade_dir=(0, 0, 0, 1), light="#FFFFFF", light_op=0.25, ink_c=None))
    # roof (two-tone) and windows
    rf = [S(1.1, 1.08), S(1.3, 1.5), S(1.55, 1.6), S(2.08, 1.6), S(2.42, 1.2), S(2.25, 1.12)]
    out.append(paint(P, smooth_closed(rf), roof, ["#FFFFFF", "#E2D8C8"], bbox(rf), seed + 1, angle=0, n=20, ink_c=ink_c, ink_w=2))
    for wp in ([S(1.3, 1.16), S(1.42, 1.44), S(1.62, 1.5), S(1.76, 1.5), S(1.76, 1.16)], [S(1.86, 1.16), S(1.86, 1.5), S(2.04, 1.5), S(2.28, 1.2)]):
        d = org_poly(wp, seed + 2, 0.3, 10, 4)
        g = P.lg([(0, "#E8F2F6"), (1, "#9CC0D0")])
        out.append(f'<path d="{d}" fill="url(#{g})"/>' + ink(d, ink_c, 1.6, seed + 2, 1, 0.8))
        bx = bbox(wp)
        out.append(f'<path d="M {_f(bx[0] + 6)} {_f(bx[3] - 4)} L {_f(bx[0] + 16)} {_f(bx[1] + 6)}" stroke="#FFFFFF" stroke-width="3" opacity="0.7"/>')
    # fenders, side spear, chrome
    out.append(f'<path d="{smooth_open([S(0.5, 0.5), S(1.6, 0.56), S(2.8, 0.54), S(3.4, 0.5)])}" stroke="#F6EEDF" stroke-width="{_f(s * 0.07)}" fill="none" stroke-linecap="round"/>')
    out.append(f'<path d="{smooth_open([S(0.5, 0.5), S(1.6, 0.56), S(2.8, 0.54), S(3.4, 0.5)])}" stroke="{ink_c}" stroke-width="1" fill="none" opacity="0.5" transform="translate(0 3)"/>')
    for (a, b) in ((S(-0.06, 0.26), S(0.3, 0.2)), (S(3.4, 0.2), S(3.72, 0.3))):
        d = org_rect(min(a[0], b[0]), min(a[1], b[1]) - 4, abs(b[0] - a[0]), s * 0.14, seed + 3, 0.3, 8, s * 0.05)
        out.append(paint(P, d, "#D8D4CC", ["#FFFFFF", "#9A968E"], bbox([a, b]), seed + 3, angle=0, n=4, ink_c=ink_c, ink_w=1.6))
    out.append(f'<path d="{blob(*S(3.56, 0.62), s * 0.07, s * 0.09, seed + 4, 0.05, 10)}" fill="#FFF2B8" stroke="{ink_c}" stroke-width="1.4"/>')
    out.append(f'<path d="{blob(*S(0.06, 0.56), s * 0.05, s * 0.08, seed + 5, 0.05, 10)}" fill="#E2574A" stroke="{ink_c}" stroke-width="1.4"/>')
    out.append(f'<path d="M {_f(S(1.95, 0.9)[0])} {_f(S(1.95, 0.9)[1])} l {_f(s * 0.16)} 0" stroke="#D8D4CC" stroke-width="4" stroke-linecap="round"/>')
    out.append(ink(bd, ink_c, 2.4, seed, 2, 0.85))
    # wheel wells + wheels
    for wx in (0.78, 2.92):
        cx_, cy_ = S(wx, 0.2)
        out.append(f'<path d="{blob(cx_, cy_ - s * 0.04, s * 0.42, s * 0.36, seed + 6, 0.02, 16)}" fill="#3A2E2A"/>')
        out.append(wheel(P, cx_, cy_, s * 0.32, seed + 7 + int(wx)))
    return "".join(out)


def tin_can(P, x, y, w, h, seed, rot=0):
    d = org_rect(x - w / 2, y - h / 2, w, h, seed, 0.4, 8, 2)
    out = [f'<g transform="rotate({rot} {_f(x)} {_f(y)})">']
    out.append(paint(P, d, "#C8C4BC", ["#FFFFFF", "#8A867E", "#E2DED6"], (x - w / 2, y - h / 2, x + w / 2, y + h / 2), seed, angle=-90, n=8, ink_c=INK, ink_w=1.4))
    for k in (0.25, 0.5, 0.75):
        out.append(f'<path d="M {_f(x - w / 2)} {_f(y - h / 2 + h * k)} l {_f(w)} 0" stroke="#8A867E" stroke-width="1" opacity="0.7"/>')
    out.append(f'<path d="{blob(x + w / 2, y, w * 0.12, h / 2, seed + 1, 0.02, 10)}" fill="#E2DED6" stroke="{INK}" stroke-width="1.2"/>')
    out.append("</g>")
    return "".join(out)


def heart_balloon(P, x, y, s, col, seed, sx, sy, rot=0):
    """Heart-shaped foil balloon on a curly string ending at (sx, sy)."""
    out = [f'<path d="M {_f(x)} {_f(y + s * 1.1)} C {_f(x + s * 0.4)} {_f(y + s * 1.8)} {_f(sx - s * 0.4)} {_f(sy - s * 1.2)} {_f(sx)} {_f(sy)}" stroke="#8A7A6A" stroke-width="1.6" fill="none"/>']
    out.append(p_heart(P, x, y, s, col, seed, rot=rot, n=10))
    out.append(f'<path d="M {_f(x - 3)} {_f(y + s * 1.08)} l 3 6 l 3 -6 Z" fill="{dk(col, 0.2)}"/>')
    return "".join(out)


def just_married():
    """The getaway car: a mint coupe trailing tin cans and ribbon, heart balloons tied on, petals in the air."""
    P = Pn("just-married")
    o = [paper_bg(P, "#F8EEE6", "#8A6A5A", 1401, tints=["#F2DCD4", "#FFFFFF"], blobs=[(300, 420, 250, 140, "#F4D8D4", 0.5), (320, 430, 180, 90, "#DCEADF", 0.45)])]
    rnd = random.Random(1402)
    for k in range(34):
        x, y = rnd.uniform(40, 560), rnd.uniform(240, 520)
        o.append(f'<path d="{blob(x, y, rnd.uniform(4, 7), rnd.uniform(2.5, 4), 1403 + k, 0.2, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#F2B8BE", "#FBE4E6", "#E8899A", "#FFFFFF"])}" opacity="0.85"/>')
    # road
    road = org_poly([(-10, 506), (610, 500), (610, 610), (-10, 610)], 1404, 0.8, 30, 2)
    o.append(paint(P, road, "#D8C8B8", ["#E2D4C4", "#C0AE9A", "#EADCCC"], (-10, 500, 610, 610), 1404, angle=0, n=120, length=(30, 90), width=(1.5, 4), ink_c=None))
    for k in range(6):
        o.append(f'<path d="{hline(20 + k * 100, 548 + (k % 2) * 16, 70 + k * 100, 548 + (k % 2) * 16, 1415 + k, 0.5)}" stroke="#FBF4EA" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.7"/>')
    o.append(f'<path d="{hline(-10, 506, 610, 500, 1405, 0.5)}" stroke="{INK}" stroke-width="2" fill="none" opacity="0.5"/>')
    # balloons behind the car
    o.append(heart_balloon(P, 280, 278, 30, ROSE, 1406, 300, 400, rot=-10))
    o.append(heart_balloon(P, 340, 262, 34, "#F2B8BE", 1407, 316, 400, rot=8))
    o.append(heart_balloon(P, 226, 300, 24, GOLD_L, 1408, 288, 402, rot=-16))
    # cans trailing on strings
    for k, (cx_, cy_, rot) in enumerate(((104, 494, -10), (146, 506, 14), (80, 516, 30))):
        o.append(f'<path d="M 212 470 Q {(cx_ + 212) / 2} {cy_ + 14} {cx_ + 10} {cy_}" stroke="#8A7A6A" stroke-width="1.4" fill="none"/>')
        o.append(tin_can(P, cx_, cy_, 26, 34, 1409 + k, rot + 90))
    for k, (pts, col) in enumerate((([(190, 452), (150, 446), (120, 460), (88, 450)], ROSE), ([(190, 458), (156, 470), (126, 470), (96, 484)], "#9CC8B4"))):
        o.append(streamer(P, pts, 6, col, 1412 + k))
    o.append(vintage_car(P, 176, 500, 94, 1420))
    # sign on the trunk
    sg = org_rect(176, 404, 92, 34, 1421, 0.5, 10, 3)
    o.append(f'<path d="{sg}" fill="#3A2418" opacity="0.2" transform="translate(3 4) rotate(-6 222 420)"/>')
    o.append(f'<g transform="rotate(-6 222 420)">' + paint(P, sg, "#FFFBF4", ["#FFFFFF", "#EADCCB"], (176, 404, 268, 438), 1421, n=6, ink_c=INK, ink_w=1.6)
             + f'<text x="222" y="428" text-anchor="middle" {SERIF_IT} font-size="19" fill="{CRAN}">just married</text></g>')
    o.append(btext(P, 300, 110, "just", SERIF_IT, 100, ROSE, ["#E8899A", "#B84A5A", "#F2B8BE"], 1430, max_w=240, shadow="#F6DCD8", sh=(0.02, 0.03)))
    o.append(btext(P, 300, 214, "MARRIED", BEBAS, 126, "#4E6E5E", ["#6E8E7A", "#34503E", "#8AAA94"], 1431, ls=12, max_w=440, shadow="#F2C4C0", sh=(0.025, 0.035), hi="#B8D4C0"))
    o.append(p_heart(P, 120, 182, 10, ROSE, 1432, n=3) + p_heart(P, 480, 182, 10, ROSE, 1433, n=3))
    return finish(P, "".join(o), 1434)


def fan_bunting(P, cx, top, R, seed, ink_c=INK):
    """Pleated patriotic half-rosette: red and white stripes, a starry navy centre, pleat shadows."""
    out = [f'<path d="{blob(cx + 4, top + 8, R, R * 0.9, seed + 9, 0.02, 30)}" fill="#3A2418" opacity="0.15"/>']
    n = 14
    for ring, (rr, cols) in enumerate(((1.0, ("#C8323A", "#B02A32")), (0.78, ("#FBF6EC", "#E8E0D2")), (0.58, ("#C8323A", "#B02A32")), (0.4, (NAVY, NAVY_D)))):
        for i in range(n):
            a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
            r = R * rr
            sc = r * 1.04
            pts = [(cx, top), (cx + math.cos(a0) * r, top + math.sin(a0) * r), (cx + math.cos((a0 + a1) / 2) * sc, top + math.sin((a0 + a1) / 2) * sc), (cx + math.cos(a1) * r, top + math.sin(a1) * r)]
            d = smooth_closed(pts) if ring == 0 else "M " + " L ".join(f"{_f(px)} {_f(py)}" for px, py in pts) + " Z"
            out.append(f'<path d="{d}" fill="{cols[i % 2]}"/>')
    rnd = random.Random(seed)
    out.append(strokes(P.id("s"), f"M {cx - R} {top} A {R} {R} 0 0 0 {cx + R} {top} Z", (cx - R, top, cx + R, top + R), ["#FFFFFF", "#8A1A22", "#E2574A"], seed, int(R * 1.2), angle=90,
                       length=(R * 0.1, R * 0.3), width=(1, 3), opacity=(0.1, 0.3), curve=0.2))
    for i in range(n + 1):
        a = math.pi * i / n
        out.append(f'<path d="M {_f(cx)} {_f(top)} L {_f(cx + math.cos(a) * R)} {_f(top + math.sin(a) * R)}" stroke="#5A1A20" stroke-width="1.2" opacity="0.45"/>')
    for k in range(5):
        a = math.pi * (k + 0.5) / 5
        out.append(f'<polygon points="{" ".join(f"{_f(x)},{_f(y)}" for x, y in star_pts(cx + math.cos(a) * R * 0.27, top + math.sin(a) * R * 0.27, R * 0.06, R * 0.025))}" fill="#FBF6EC"/>')
    out.append(ink(f"M {_f(cx - R)} {_f(top)} A {_f(R)} {_f(R)} 0 0 0 {_f(cx + R)} {_f(top)}", ink_c, 1.8, seed, 1, 0.6))
    return "".join(out)


def happy_4th():
    """Porch-rail bunting, painted starbursts and a big, proud 4th in navy and barn red."""
    P = Pn("happy-4th")
    o = [paper_bg(P, "#F6EEDF", "#6A4A3A", 1501, tints=["#EADCC4", "#FFFFFF"], blobs=[(300, 360, 240, 200, "#E6EEF2", 0.5)])]
    # pale fireworks behind the lettering
    o.append(f'<g opacity="0.5">{firework(P, 140, 320, 70, "#E2574A", 1502, rays=18, glow=False, w=3)}{firework(P, 470, 300, 80, "#4A6AA8", 1503, rays=20, glow=False, w=3)}'
             f'{firework(P, 430, 470, 48, GOLD, 1504, rays=14, glow=False, w=2.4)}</g>')
    # rail + bunting at the top
    o.append(f'<path d="{org_rect(-10, -10, 620, 30, 1505, 0.6, 30, 1)}" fill="#FBF6EC"/>' + paint(P, org_rect(-10, -10, 620, 30, 1505, 0.6, 30, 1), "#F2ECE0", ["#FFFFFF", "#D8D0C2"], (-10, -10, 610, 20), 1505, angle=0, n=30, ink_c=INK, ink_w=1.6))
    for k, (x, R) in enumerate(((96, 84), (300, 96), (504, 84))):
        o.append(fan_bunting(P, x, 14, R, 1506 + k))
    o.append(sparkles(1510, 10, (70, 130, 530, 540), GOLD, (6, 11), avoid=((90, 150, 520, 520),)))
    o.append(btext(P, 300, 214, "happy", SERIF_IT, 96, "#B02A32", ["#C8323A", "#8A1A22", "#E2574A"], 1511, max_w=280, shadow="#E8D8C4", sh=(0.02, 0.03)))
    # big 4 + th
    o.append(btext(P, 262, 460, "4", ANTON, 250, NAVY, [NAVY, NAVY_L, NAVY_D, "#4A5A8E"], 1512, max_w=200, shadow="#C8323A", sh=(0.03, 0.025), hi="#8A9ACC"))
    o.append(btext(P, 362, 376, "TH", ANTON, 96, "#B02A32", ["#C8323A", "#8A1A22", "#E2574A"], 1513, max_w=120, shadow=NAVY, sh=(0.03, 0.03)))
    o.append(f'<path d="{hline(330, 394, 404, 392, 1514, 0.8)}" stroke="{NAVY}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    for k, (x, y, r) in enumerate(((360, 430, 12), (392, 454, 9), (420, 428, 7))):
        o.append(star_painted(P, x, y, r, 1515 + k, col="#C8323A" if k == 1 else NAVY, glow=False))
    o.append(flank(510, "OF JULY", BEBAS, 44, 14, "#B02A32", max_w=240, L=46, seed=1518))
    o.append(ptext(300, 526, "OF JULY", BEBAS, 44, NAVY, max_w=240, ls=14))
    return finish(P, "".join(o), 1519)


def watermelon(P, cx, cy, r, seed, rot=0, bite=False):
    """A watermelon wedge: green rind, pale band, red flesh with seeds."""
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    tri = [(cx - r, cy), (cx + r, cy)] + [(cx + math.cos(math.radians(a)) * r, cy + math.sin(math.radians(a)) * r * 0.9) for a in range(10, 171, 20)]
    rind = smooth_closed([(cx - r, cy), (cx - r * 0.95, cy + r * 0.3), (cx - r * 0.6, cy + r * 0.78), (cx, cy + r * 0.92), (cx + r * 0.6, cy + r * 0.78), (cx + r * 0.95, cy + r * 0.3), (cx + r, cy)])
    out.append(paint(P, rind, "#4A8A3E", ["#6AAA5A", "#2E6A2A"], (cx - r, cy, cx + r, cy + r), seed, n=10, ink_c=INK, ink_w=1.6))
    pale = smooth_closed([(cx - r * 0.94, cy), (cx - r * 0.86, cy + r * 0.28), (cx - r * 0.54, cy + r * 0.68), (cx, cy + r * 0.8), (cx + r * 0.54, cy + r * 0.68), (cx + r * 0.86, cy + r * 0.28), (cx + r * 0.94, cy)])
    out.append(f'<path d="{pale}" fill="#E8F2C8"/>')
    flesh = smooth_closed([(cx - r * 0.9, cy), (cx - r * 0.8, cy + r * 0.24), (cx - r * 0.5, cy + r * 0.6), (cx, cy + r * 0.72), (cx + r * 0.5, cy + r * 0.6), (cx + r * 0.8, cy + r * 0.24), (cx + r * 0.9, cy)])
    out.append(paint(P, flesh, "#E8505A", ["#F27A7A", "#C8323A", "#F29A8A"], (cx - r, cy, cx + r, cy + r), seed + 1, angle=90, n=14, ink_c=None))
    rnd = random.Random(seed)
    for k in range(7):
        a = math.radians(30 + k * 20)
        rr = r * rnd.uniform(0.35, 0.55)
        out.append(f'<path d="{blob(cx + math.cos(a) * rr * 1.3 - r * 0.0, cy + math.sin(a) * rr * 0.9, 2.4, 3.6, seed + k, 0.1, 8, math.degrees(a) - 90)}" fill="#2A1A14"/>')
    out.append(ink(f"M {_f(cx - r)} {_f(cy)} L {_f(cx + r)} {_f(cy)}", INK, 1.6, seed, 1, 0.6))
    out.append("</g>")
    return "".join(out)


def mason_jar(P, cx, base, w, h, seed, liquid="#F6D86A", straw=True):
    out = [cast(cx + 4, base, w * 0.6, 5, "#3A2418", 0.3, seed)]
    jar = org_rect(cx - w / 2, base - h, w, h, seed, 0.5, 10, w * 0.15)
    out.append(f'<path d="{jar}" fill="#E8F2F4" opacity="0.6"/>')
    lq = org_rect(cx - w / 2 + 3, base - h * 0.78, w - 6, h * 0.76, seed + 1, 0.4, 10, w * 0.12)
    g = P.lg([(0, lt(liquid, 0.3)), (1, liquid)])
    out.append(f'<path d="{lq}" fill="url(#{g})" opacity="0.9"/>')
    for k in range(3):
        out.append(f'<path d="{blob(cx - w * 0.2 + k * w * 0.2, base - h * (0.55 - k * 0.1), w * 0.14, w * 0.12, seed + 3 + k, 0.1, 8)}" fill="#F2E8A0" stroke="#C8A83A" stroke-width="1"/>')
    if straw:
        out.append(f'<path d="M {_f(cx + w * 0.1)} {_f(base - h * 0.4)} L {_f(cx + w * 0.34)} {_f(base - h * 1.32)}" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round"/>'
                   f'<path d="M {_f(cx + w * 0.1)} {_f(base - h * 0.4)} L {_f(cx + w * 0.34)} {_f(base - h * 1.32)}" stroke="#C8323A" stroke-width="6" stroke-dasharray="6 6" stroke-linecap="butt"/>')
    out.append(f'<path d="{org_rect(cx - w / 2 - 2, base - h - 8, w + 4, 12, seed + 2, 0.3, 8, 2)}" fill="#C8C4BC" stroke="{INK}" stroke-width="1.4"/>')
    out.append(f'<path d="M {_f(cx - w * 0.32)} {_f(base - h * 0.85)} L {_f(cx - w * 0.32)} {_f(base - h * 0.15)}" stroke="#FFFFFF" stroke-width="3" opacity="0.7"/>')
    out.append(ink(jar, INK, 1.8, seed, 2, 0.75))
    return "".join(out)


def sparkler(P, x, y, L, ang, seed):
    a = math.radians(ang)
    ex, ey = x + math.cos(a) * L, y + math.sin(a) * L
    out = [f'<path d="M {_f(x)} {_f(y)} L {_f(ex)} {_f(ey)}" stroke="#8A867E" stroke-width="2.4" stroke-linecap="round"/>']
    sx, sy = x + math.cos(a) * L * 0.75, y + math.sin(a) * L * 0.75
    out.append(P.glow(sx, sy, 40, "#FFE9A0", 0.7))
    rnd = random.Random(seed)
    for k in range(26):
        b = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(8, 30)
        out.append(f'<path d="M {_f(sx + math.cos(b) * 4)} {_f(sy + math.sin(b) * 4)} l {_f(math.cos(b) * rr)} {_f(math.sin(b) * rr)}" stroke="{rnd.choice(["#FFF6D8", GOLD_L, "#FFFFFF"])}" stroke-width="1.4" stroke-linecap="round" opacity="0.9"/>')
    out.append(f'<circle cx="{_f(sx)}" cy="{_f(sy)}" r="5" fill="#FFFFFF"/>')
    return "".join(out)


def red_white_and_blue():
    """A Fourth of July picnic at dusk: gingham blanket, watermelon, lemonade and sparklers as the fireworks open overhead."""
    P = Pn("red-white-and-blue")
    o = [sky_wash(P, "#1A2448", "#E8A08A", ["#24305A", "#3A4478", "#C88A8A", "#F2B8A0"], 1601, box=(0, 0, 600, 400), n=240, angle=-3, mid=(0.62, "#5A5A8A"))]
    o.append(sparkles(1602, 26, (20, 20, 580, 200), "#FFFFFF", (2, 4), op=(0.5, 0.9)))
    o.append(firework(P, 136, 318, 74, "#E2574A", 1603, rays=22, col2=GOLD_L))
    o.append(firework(P, 452, 304, 82, "#8CC0F0", 1604, rays=24, col2="#FFFFFF"))
    o.append(firework(P, 296, 340, 44, "#FFF2D8", 1605, rays=18, col2="#E2574A", w=2.4))
    o.append(firework(P, 76, 236, 30, GOLD, 1606, rays=14, w=2))
    o.append(firework(P, 540, 226, 26, "#F2A6B8", 1623, rays=12, w=2))
    # tree line + distant town silhouette at the horizon
    o.append(far_trees(P, 404, 1607, "#2E3456", n=36, h=(24, 58), w=0.5))
    o.append(f'<path d="{org_rect(200, 380, 30, 28, 1608, 0.4, 8, 1)}" fill="#2E3456"/><path d="M 204 380 L 215 352 L 226 380 Z" fill="#2E3456"/>')
    field = org_poly([(-10, 400), (610, 396), (610, 610), (-10, 610)], 1609, 0.8, 30, 2)
    o.append(paint(P, field, "#4A6A4A", ["#5A7E52", "#34503A", "#6A8E5A"], (-10, 396, 610, 610), 1609, angle=-80, n=260, length=(6, 16), width=(1, 2.4), op=(0.4, 0.8), ink_c=None))
    # gingham blanket in perspective
    bl = [(70, 452), (530, 446), (600, 610), (0, 610)]
    bld = org_poly(bl, 1610, 1, 20, 3)
    inner = [f'<path d="{bld}" fill="#FBF4EA"/>']
    for k in range(-6, 8):
        x0 = 300 + k * 44
        inner.append(f'<path d="M {_f(300 + (x0 - 300) * 0.78)} 446 L {_f(300 + (x0 - 300) * 1.32)} 610 L {_f(300 + (x0 + 22 - 300) * 1.32)} 610 L {_f(300 + (x0 + 22 - 300) * 0.78)} 446 Z" fill="#C8323A" opacity="0.45"/>')
    for k, y in enumerate((452, 478, 510, 548, 592)):
        inner.append(f'<path d="M -10 {y} L 610 {y} L 610 {y + 10 + k * 3} L -10 {y + 10 + k * 3} Z" fill="#C8323A" opacity="0.45"/>')
    inner.append(strokes(P.id("s"), bld, (0, 446, 600, 610), ["#FFFFFF", "#8A1A22"], 1611, 80, angle=0, length=(20, 60), width=(1.5, 4), opacity=(0.1, 0.25)))
    inner.append(f'<rect x="0" y="440" width="600" height="170" fill="url(#{P.lg([(0, "#1A2448", 0.35), (1, "#1A2448", 0.1)])})"/>')
    cid = P.clip(f'<path d="{bld}"/>')
    o.append(f'<g clip-path="url(#{cid})">{"".join(inner)}</g>' + ink(bld, INK, 2, 1610, 1, 0.6))
    # picnic things
    o.append(watermelon(P, 180, 500, 46, 1612, rot=-8))
    o.append(watermelon(P, 244, 530, 40, 1613, rot=12))
    o.append(mason_jar(P, 420, 538, 48, 70, 1614))
    o.append(mason_jar(P, 474, 528, 36, 50, 1615, liquid="#F2A6B8", straw=False))
    o.append(sparkler(P, 470, 480, 100, -64, 1616))
    o.append(sparkler(P, 480, 480, 92, -96, 1617))
    o.append(mason_jar(P, 104, 548, 40, 46, 1618, liquid="#F2EEE4", straw=False))
    o.append(btext(P, 300, 104, "red, white", SERIF_IT, 92, "#F6EEDF", ["#FFFFFF", "#F2D8C8", "#E8C8B8"], 1620, max_w=440, shadow="#C8323A", sh=(0.025, 0.035)))
    o.append(btext(P, 300, 214, "& BLUE", ANTON, 110, "#9CC8F2", ["#B8DAF8", "#6E9ED0", "#D4E8FA"], 1621, ls=10, max_w=360, shadow="#141A38", sh=(0.025, 0.035), hi="#FFFFFF"))
    return finish(P, "".join(o), 1622)


def beach_chair(P, x, base, s, seed, a="#E2725B", b="#FBF4EA"):
    """Wooden deck chair with a striped canvas sling, seen in three-quarter."""
    out = [cast(x + s * 0.3, base, s * 0.75, s * 0.08, "#5A3A2A", 0.3, seed)]
    W = WOOD_L
    legs = [((x - s * 0.5, base), (x + s * 0.1, base - s * 1.05)), ((x + s * 0.45, base), (x - s * 0.15, base - s * 0.7)), ((x + s * 0.3, base), (x + s * 0.55, base - s * 0.45))]
    for (p0, p1) in legs:
        out.append(ink(f"M {_f(p0[0])} {_f(p0[1])} L {_f(p1[0])} {_f(p1[1])}", "#7A5230", s * 0.07, seed, 1, 1))
        out.append(f'<path d="M {_f(p0[0])} {_f(p0[1])} L {_f(p1[0])} {_f(p1[1])}" stroke="{W}" stroke-width="{_f(s * 0.04)}" stroke-linecap="round"/>')
    sling = [(x - s * 0.38, base - s * 0.96), (x + s * 0.3, base - s * 1.04), (x + s * 0.62, base - s * 0.42), (x - s * 0.04, base - s * 0.36)]
    d = smooth_closed([(x - s * 0.38, base - s * 0.96), (x + s * 0.3, base - s * 1.04), (x + s * 0.5, base - s * 0.62), (x + s * 0.62, base - s * 0.42), (x - s * 0.04, base - s * 0.36), (x - s * 0.12, base - s * 0.62)])
    inner = [f'<path d="{d}" fill="{b}"/>']
    for k in range(5):
        t0 = k / 5
        inner.append(f'<path d="M {_f(x - s * 0.38 + s * 0.68 * t0)} {_f(base - s * 0.96 - s * 0.08 * t0)} L {_f(x - s * 0.38 + s * 0.68 * (t0 + 0.1))} {_f(base - s * 0.96 - s * 0.08 * (t0 + 0.1))} '
                     f'L {_f(x - s * 0.04 + s * 0.66 * (t0 + 0.1))} {_f(base - s * 0.36 - s * 0.06 * (t0 + 0.1))} L {_f(x - s * 0.04 + s * 0.66 * t0)} {_f(base - s * 0.36 - s * 0.06 * t0)} Z" fill="{a}"/>')
    inner.append(strokes(P.id("s"), d, bbox(sling), ["#FFFFFF", dk(a, 0.2)], seed, 30, angle=60, length=(s * 0.1, s * 0.3), width=(1, 3), opacity=(0.15, 0.35)))
    inner.append(f'<path d="{d}" fill="url(#{P.lg([(0, "#3A2418", 0), (1, "#3A2418", 0.3)])})"/>')
    cid = P.clip(f'<path d="{d}"/>')
    out.append(f'<g clip-path="url(#{cid})">{"".join(inner)}</g>' + ink(d, INK, 2, seed, 2, 0.8))
    out.append(ink(f"M {_f(x - s * 0.42)} {_f(base - s * 0.98)} L {_f(x + s * 0.34)} {_f(base - s * 1.06)}", "#7A5230", s * 0.06, seed + 1, 1, 1))
    return "".join(out)


def so_long_summer():
    """Labor Day at the shore: the last sunset, an empty striped deck chair, folded umbrella, flip-flops and a gull."""
    P = Pn("so-long-summer")
    o = [sky_wash(P, "#F2A88A", "#FBE2C0", ["#F6B898", "#E8907A", "#FBD8B4", "#FFE8CC"], 1701, box=(0, 0, 600, 340), n=220, angle=-3, mid=(0.55, "#F8C4A0"))]
    o.append(P.glow(300, 330, 200, "#FFE9B0", 0.85))
    sun = blob(300, 336, 74, 74, 1702, 0.01, 30)
    o.append(f'<path d="{sun}" fill="#FFD27A"/>' + f'<path d="{sun}" fill="url(#{P.rg([(0, "#FFF4C8"), (1, "#F6A85A")], cx=0.5, cy=0.45, r=0.6)})"/>')
    o.append(cloud(P, 120, 250, 76, 14, 1703, base="#FBD8C4", shade="#E89A8A", op=0.85))
    o.append(cloud(P, 480, 216, 60, 12, 1704, base="#FBD8C4", shade="#E89A8A", op=0.8))
    # sea
    sea = "M -10 336 L 610 336 L 610 470 L -10 470 Z"
    o.append(f'<path d="{sea}" fill="url(#{P.lg([(0, "#E89A8A"), (0.3, "#6AA0B0"), (1, "#3E7E94")])})"/>')
    o.append(strokes(P.id("s"), sea, (-30, 336, 610, 470), ["#F6C8A8", "#4E8AA0", "#FFE2B8", "#8ABCC8"], 1705, 200, angle=0, length=(20, 70), width=(1, 3), opacity=(0.25, 0.55), curve=0.05))
    for k in range(10):
        y = 344 + k * 11
        w = 70 - k * 5
        o.append(f'<path d="M {300 - w} {y} L {300 + w} {y}" stroke="#FFE9A8" stroke-width="{3.4 - k * 0.25:.1f}" stroke-linecap="round" opacity="{0.85 - k * 0.06:.2f}"/>')
    o.append(f'<path d="M -10 334 L 610 334" stroke="#FBD8B4" stroke-width="3" opacity="0.7"/>')
    # surf + sand
    sand = smooth_closed([(-20, 470), (140, 462), (300, 472), (460, 460), (620, 468), (620, 620), (-20, 620)])
    o.append(paint(P, sand, "#F2D6A8", ["#F8E2BE", "#E2C090", "#FBE8C8", "#D8B47E"], (-20, 460, 620, 620), 1706, angle=-4, n=200, length=(10, 40), width=(1.2, 3), ink_c=None))
    o.append(f'<path d="{smooth_open([(-20, 468), (140, 460), (300, 470), (460, 458), (620, 466)])}" stroke="#FFFFFF" stroke-width="5" fill="none" opacity="0.8"/>')
    o.append(dab_dots(1707, 70, (0, 480, 600, 600), ["#C8A070", "#FFFFFF", "#B88A5A"], (0.8, 1.8), (0.4, 0.8)))
    # open beach umbrella, tilted into the breeze
    ux, uy = 436, 304
    o.append(cast(436, 530, 110, 10, "#5A3A2A", 0.22, 1711))
    o.append(ink(f"M 446 528 L {ux - 6} {uy + 6}", "#7A5230", 5, 1708, 1, 1))
    o.append(f'<path d="M 446 528 L {ux - 6} {uy + 6}" stroke="#C8A070" stroke-width="2"/>')
    o.append(f'<g transform="rotate(-10 {ux} {uy})">')
    R = 96
    scal = [(ux + math.cos(math.radians(a)) * R, uy + 38 + (6 if i % 2 else 0)) for i, a in enumerate(range(180, -1, -30))]
    can = smooth_closed([(ux - R, uy + 38), (ux - R * 0.8, uy - 10), (ux - R * 0.3, uy - 44), (ux, uy - 50), (ux + R * 0.3, uy - 44), (ux + R * 0.8, uy - 10), (ux + R, uy + 38)]
                        + [(ux + R - k * 2 * R / 6 - R / 6, uy + 50) if k % 1 == 0 else None for k in range(6)])
    inner = [f'<path d="{can}" fill="#FBF4EA"/>']
    for k in range(6):
        if k % 2 == 0:
            x0, x1 = ux - R + k * 2 * R / 6, ux - R + (k + 1) * 2 * R / 6
            inner.append(f'<path d="M {ux} {uy - 52} L {_f(x0)} {uy + 60} L {_f(x1)} {uy + 60} Z" fill="#3E8A9A"/>')
    inner.append(strokes(P.id("s"), can, (ux - R, uy - 50, ux + R, uy + 52), ["#FFFFFF", "#2A6A7A", "#F6C8A8"], 1709, 50, angle=-60, length=(10, 40), width=(1.5, 4), opacity=(0.15, 0.4)))
    inner.append(f'<path d="{can}" fill="url(#{P.lg([(0, "#FFFFFF", 0.25), (0.5, "#FFFFFF", 0), (1, "#3A2418", 0.3)])})"/>')
    cid = P.clip(f'<path d="{can}"/>')
    o.append(f'<g clip-path="url(#{cid})">{"".join(inner)}</g>' + ink(can, INK, 2.2, 1709, 2, 0.8))
    o.append(f'<circle cx="{ux}" cy="{uy - 52}" r="5" fill="#E2725B" stroke="{INK}" stroke-width="1.2"/></g>')
    o.append(beach_chair(P, 220, 540, 150, 1712))
    # flip-flops
    for k, (fx, fy, rot, col) in enumerate(((350, 516, -20, "#E2725B"), (378, 528, 10, "#F2C25A"))):
        ff = blob(fx, fy, 13, 26, 1713 + k, 0.06, 14, rot)
        o.append(f'<path d="{ff}" fill="{col}" stroke="{INK}" stroke-width="1.6"/>'
                 f'<path d="M {fx - 8} {fy - 4} L {fx} {fy - 16} L {fx + 8} {fy - 4}" stroke="#FBF4EA" stroke-width="3" fill="none" transform="rotate({rot} {fx} {fy})"/>')
    # starfish + shell
    o.append(f'<polygon points="{" ".join(f"{_f(x)},{_f(y)}" for x, y in star_pts(508, 528, 16, 7, 5, -70))}" fill="#E8906A" stroke="{INK}" stroke-width="1.4" stroke-linejoin="round"/>')
    o.append(f'<path d="M 92 520 q 14 -26 28 0 Z" fill="#FBE8D8" stroke="{INK}" stroke-width="1.4"/><path d="M 106 494 L 98 520 M 106 494 L 106 520 M 106 494 L 114 520" stroke="#C8A08A" stroke-width="1"/>')
    # gulls
    for (gx, gy, s_) in ((420, 250, 12), (450, 236, 8), (160, 300, 9)):
        o.append(f'<path d="M {gx - s_} {gy} q {s_ * 0.5} {-s_ * 0.6} {s_} 0 q {s_ * 0.5} {-s_ * 0.6} {s_} 0" stroke="#5A4A5A" stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    o.append(btext(P, 300, 100, "so long,", SERIF_IT, 90, "#8A3A3A", ["#A84A4A", "#6A2A2A", "#C8605A"], 1720, max_w=360, shadow="#FBE2C0", sh=(0.02, 0.03)))
    o.append(btext(P, 300, 220, "SUMMER", BEBAS, 122, "#2E6E7E", ["#3E8A9A", "#1E5060", "#5AA8B8"], 1721, ls=14, max_w=420, shadow="#FBE2C0", sh=(0.025, 0.035), hi="#9AD0D8"))
    return finish(P, "".join(o), 1722)

# --------------------------------------------------------------- back to school, Thanksgiving
def ruler(P, x, y, L, w, ang, seed):
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    pts = [(x, y), (x + ux * L, y + uy * L), (x + ux * L + nx * w, y + uy * L + ny * w), (x + nx * w, y + ny * w)]
    d = org_poly(pts, seed, 0.4, 16, 2)
    out = [paint(P, d, "#E8C882", ["#F2DCA0", "#C8A060"], bbox(pts), seed, angle=ang, n=12, ink_c=INK, ink_w=1.6)]
    for i in range(1, int(L / 8)):
        t = i * 8
        k = 0.45 if i % 5 == 0 else 0.25
        out.append(f'<path d="M {_f(x + ux * t)} {_f(y + uy * t)} l {_f(nx * w * k)} {_f(ny * w * k)}" stroke="{INK}" stroke-width="1.1" opacity="0.8"/>')
    return "".join(out)


def pencil_cup(P, cx, base, w, h, seed):
    """Tin pencil cup wrapped in a painted label, crammed with coloured pencils and a ruler."""
    out = []
    # pencils first (behind the cup front)
    for k, (dx, L, ang, col) in enumerate(((-0.34, 170, -98, "#E2574A"), (-0.16, 196, -92, "#F2C24A"), (0.04, 176, -86, "#4A8ACB"), (0.22, 186, -80, "#5EA05A"), (0.38, 150, -74, "#9A6AC8"))):
        a = math.radians(ang)
        x0, y0 = cx + dx * w, base - 10
        tip_x, tip_y = x0 + math.cos(a) * L, y0 + math.sin(a) * L
        out.append(pencil(P, tip_x - math.cos(a) * L, tip_y - math.sin(a) * L, L, ang, seed + k * 3, body=col, w=15) if False else
                   pencil(P, x0, y0, L, ang, seed + k * 3, body=col, w=15))
    out.append(ruler(P, cx - w * 0.06, base - 20, 210, 22, -100, seed + 20))
    out.append(cast(cx + 8, base + 2, w * 0.7, 8, "#3A2418", 0.3, seed + 21))
    body = org_rect(cx - w / 2, base - h, w, h, seed + 22, 0.6, 12, 4)
    out.append(paint(P, body, "#C8C4BC", ["#FFFFFF", "#8A867E"], (cx - w / 2, base - h, cx + w / 2, base), seed + 22, n=10, ink_c=None))
    lab = org_rect(cx - w / 2, base - h * 0.78, w, h * 0.6, seed + 23, 0.5, 12, 2)
    out.append(paint(P, lab, "#E2574A", ["#F2806A", "#B8323A"], (cx - w / 2, base - h * 0.78, cx + w / 2, base - h * 0.18), seed + 23, n=16, ink_c=None))
    for k in range(-3, 4):
        out.append(f'<circle cx="{_f(cx + k * w * 0.14)}" cy="{_f(base - h * 0.7)}" r="3" fill="#FBF4EA"/><circle cx="{_f(cx + k * w * 0.14 + w * 0.07)}" cy="{_f(base - h * 0.26)}" r="3" fill="#FBF4EA"/>')
    out.append(ptext(cx, base - h * 0.38, "ABC", ANTON, h * 0.3, "#FBF4EA", max_w=w * 0.7, ls=4))
    g = P.lg([(0, "#FFFFFF", 0.35), (0.3, "#FFFFFF", 0), (0.65, "#3A2418", 0), (1, "#3A2418", 0.4)], 0, 0, 1, 0)
    out.append(f'<path d="{body}" fill="url(#{g})"/>')
    out.append(ink(body, INK, 2.2, seed + 22, 2, 0.85))
    for yy in (base - h + 4, base - 4):
        out.append(f'<path d="{hline(cx - w / 2, yy, cx + w / 2, yy, seed + int(yy), 0.4)}" stroke="#8A867E" stroke-width="2.4" fill="none"/>')
    return "".join(out)


def comp_book(P, x, y, w, h, seed, rot=0, label="#FBF4EA"):
    """Composition notebook: marbled black-and-white cover, cloth spine, label box."""
    out = [f'<g transform="rotate({rot} {_f(x + w / 2)} {_f(y + h / 2)})">']
    out.append(f'<path d="{org_rect(x + 5, y + 7, w, h, seed + 9, 0.6, 14, 3)}" fill="#3A2418" opacity="0.22"/>')
    d = org_rect(x, y, w, h, seed, 0.6, 14, 3)
    out.append(f'<path d="{d}" fill="#24221F"/>')
    rnd = random.Random(seed)
    marb = "".join(f'<path d="M {_f(rnd.uniform(x, x + w))} {_f(rnd.uniform(y, y + h))} q {_f(rnd.uniform(-8, 8))} {_f(rnd.uniform(-6, 6))} {_f(rnd.uniform(-14, 14))} {_f(rnd.uniform(-10, 10))}" stroke="#FFFFFF" stroke-width="{rnd.uniform(0.8, 2.4):.1f}" fill="none" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>' for _ in range(int(w * h / 50)))
    cid = P.clip(f'<path d="{d}"/>')
    out.append(f'<g clip-path="url(#{cid})">{marb}<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w * 0.14)}" height="{_f(h)}" fill="#1A1816"/></g>')
    out.append(f'<path d="{org_rect(x + w * 0.3, y + h * 0.18, w * 0.6, h * 0.26, seed + 1, 0.4, 10, 2)}" fill="{label}" stroke="{INK}" stroke-width="1.2"/>')
    for k in range(2):
        out.append(f'<path d="M {_f(x + w * 0.36)} {_f(y + h * (0.28 + k * 0.09))} l {_f(w * 0.48)} 0" stroke="#8AA8C8" stroke-width="1.2"/>')
    out.append(ink(d, INK, 1.8, seed, 1, 0.8))
    out.append("</g>")
    return "".join(out)


def back_to_school():
    """First-day desk on ruled notebook paper: a tin cup of sharpened pencils and a ruler, a red apple, composition books."""
    P = Pn("back-to-school")
    o = [paper(P.id("pp"), "#FBF8EE", "#7A8AA8", 1801)]
    for k in range(20):
        y = 40 + k * 30
        o.append(f'<path d="{hline(-10, y, 610, y, 1802 + k, 0.4)}" stroke="#9CC0E2" stroke-width="1.6" fill="none" opacity="0.75"/>')
    o.append(f'<path d="{hline(76, -10, 78, 610, 1830, 0.6)}" stroke="#E8808A" stroke-width="2" fill="none" opacity="0.8"/>')
    for k in range(5):
        o.append(f'<circle cx="34" cy="{80 + k * 110}" r="11" fill="#E2DCCC" stroke="#B8B0A0" stroke-width="1.4"/>')
    # doodles in the margins
    o.append(f'<g opacity="0.75">'
             f'<polygon points="{" ".join(f"{_f(x)},{_f(y)}" for x, y in star_pts(512, 264, 16, 7))}" fill="none" stroke="#4A8ACB" stroke-width="2.2" stroke-linejoin="round"/>'
             f'<path d="M 488 300 q 14 -10 28 0 t 28 0" stroke="#E2574A" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
             f'<text x="112" y="282" {SERIF_IT} font-size="30" fill="#4A8ACB" transform="rotate(-8 112 282)">A+</text>'
             f'<path d="{heart_d(140, 318, 10, -10, 1831)}" fill="none" stroke="#E2574A" stroke-width="2"/></g>')
    o.append(cast(300, 534, 220, 12, "#3A2418", 0.22, 1832))
    o.append(comp_book(P, 330, 444, 170, 76, 1833, rot=-4))
    o.append(comp_book(P, 344, 404, 150, 68, 1834, rot=6, label="#F2D06B"))
    o.append(pencil_cup(P, 210, 524, 120, 130, 1840))
    o.append(apple_p(P, 400, 340, 54, 1850, rot=8))
    o.append(pencil(P, 104, 540, 120, -8, 1851, body="#F2C24A", w=14))
    o.append(btext(P, 300, 98, "back to", SERIF_IT, 84, "#2E5A8A", ["#4A7AAA", "#1E3E66", "#6A9AC8"], 1860, max_w=330, shadow="#FBF8EE", sh=(0.02, 0.03)))
    o.append(btext(P, 300, 238, "SCHOOL", ANTON, 118, "#D8423A", ["#E2574A", "#A8302A", "#F2806A"], 1861, ls=8, max_w=420, shadow="#2E5A8A", sh=(0.025, 0.035), hi="#F6A890"))
    return finish(P, "".join(o), 1862)


def wheat_stalk(P, x0, y0, x1, y1, seed, col=("#E9BE5E", "#B8862E", "#F8DC8E"), ink_c=INK):
    """A ripe wheat stalk: stem plus paired plump grains toward the head, a few whiskers."""
    out = [f'<path d="M {_f(x0)} {_f(y0)} L {_f(x1)} {_f(y1)}" stroke="{col[1]}" stroke-width="2.2" stroke-linecap="round"/>']
    a = math.atan2(y1 - y0, x1 - x0)
    L = math.hypot(x1 - x0, y1 - y0)
    rnd = random.Random(seed)
    for i in range(9):
        t = 0.62 + i * 0.045
        px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        for sg in (-1, 1):
            ga = a + sg * 0.55
            gx, gy = px + math.cos(ga) * 6, py + math.sin(ga) * 6
            g = blob(gx, gy, 6, 3.4, seed + i * 2 + sg, 0.05, 8, math.degrees(ga))
            out.append(f'<path d="{g}" fill="{rnd.choice(col)}" stroke="{col[1]}" stroke-width="0.9"/>')
            out.append(f'<path d="M {_f(gx)} {_f(gy)} l {_f(math.cos(ga - sg * 0.3) * 18)} {_f(math.sin(ga - sg * 0.3) * 18)}" stroke="{col[0]}" stroke-width="0.9" opacity="0.8"/>')
    return "".join(out)


def thankful():
    """A hand-tied sheaf of wheat with a gingham bow, ringed by painted maple and oak leaves and bittersweet berries."""
    P = Pn("thankful")
    o = [paper_bg(P, "#F6ECDA", "#7A4A2A", 1901, tints=["#EAD6B8", "#FFFFFF"], blobs=[(300, 420, 220, 140, "#F2D2B0", 0.55)])]
    RUST, RUST_D = "#B8532A", "#7A3214"
    # leaves fanned behind the sheaf
    for k, (x, y, s_, rot, fill, dark) in enumerate(((150, 430, 58, -40, "#C8502A", "#8A2E14"), (450, 426, 60, 38, "#E08A2E", "#A8561A"), (186, 500, 46, -70, "#E8A83A", "#B8781A"),
                                                     (418, 502, 44, 64, "#C8502A", "#8A2E14"), (132, 350, 42, -20, "#E8A83A", "#B8781A"), (470, 342, 40, 26, "#B8432A", "#7A2414"))):
        o.append(maple_leaf(x, y, s_, fill, dark, rot=rot, seed=1902 + k))
    for k, (x, y, rot) in enumerate(((236, 392, -30), (366, 388, 34))):
        o.append(oak(x, y, 30, "#9A7A3A", "#5A4418", rot=rot))
    # the sheaf
    cx, cy = 300, 440
    for k in range(17):
        t = (k - 8) / 8
        top_x, top_y = cx + t * 120, 250 + abs(t) * 60
        bot_x, bot_y = cx + t * 30, 540
        o.append(wheat_stalk(P, bot_x, bot_y, top_x, top_y, 1910 + k))
    # bittersweet berries
    rnd = random.Random(1930)
    for k in range(16):
        bx = rnd.choice((rnd.uniform(130, 200), rnd.uniform(400, 470)))
        by = rnd.uniform(330, 470)
        o.append(ball_paint(P, bx, by, rnd.uniform(5, 7), "#E2643A", 1931 + k, hi=False))
    # gingham ribbon around the waist
    band = org_rect(cx - 40, 452, 80, 24, 1950, 0.5, 10, 4)
    o.append(paint(P, band, "#C8502A", ["#E2725B", "#8A2E14"], (cx - 40, 452, cx + 40, 476), 1950, n=8, ink_c=INK, ink_w=1.6))
    for k in range(5):
        o.append(f'<path d="M {cx - 40 + k * 18} 452 l 0 24" stroke="#FBF0E0" stroke-width="5" opacity="0.5"/>')
    o.append(bow_p(P, cx, 462, 50, "#C8502A", 1951))
    for sg, L in ((-1, 50), (1, 44)):
        o.append(f'<path d="M {cx} 466 q {sg * 18} 22 {sg * 8} {L}" stroke="#C8502A" stroke-width="9" fill="none" stroke-linecap="round"/>')
    o.append(maple_leaf(96, 282, 16, "#C8502A", "#8A2E14", rot=30, seed=1970) + maple_leaf(512, 260, 14, "#E8A83A", "#B8781A", rot=-20, seed=1971) + maple_leaf(528, 520, 15, "#B8432A", "#7A2414", rot=60, seed=1972))
    o.append(btext(P, 300, 160, "thankful", SERIF_IT, 140, RUST, ["#C8602A", RUST_D, "#E2783A", "#9A3E18"], 1960, max_w=470, shadow="#EAD0B0", sh=(0.02, 0.03), hi="#F2B080"))
    o.append(flank(206, "GIVE THANKS", BEBAS, 30, 10, "#9A7A3A", max_w=220, L=44, seed=1961))
    o.append(ptext(300, 218, "GIVE THANKS", BEBAS, 30, "#6A4A1E", max_w=220, ls=10))
    return finish(P, "".join(o), 1962)


def pumpkin_pie(P, cx, cy, rx, ry, seed, cut=True):
    """Pumpkin pie from three-quarters: fluted crust, custard top, a slice cut out, crust leaves and whipped cream."""
    out = [cast(cx + 6, cy + ry * 0.9, rx * 1.05, ry * 0.35, "#1A2A2A", 0.3, seed)]
    # tin / side
    side = smooth_closed([(cx - rx, cy), (cx - rx * 0.92, cy + ry * 0.55), (cx, cy + ry * 0.75), (cx + rx * 0.92, cy + ry * 0.55), (cx + rx, cy)])
    out.append(paint(P, side, "#D89A5A", ["#E8B47A", "#B8783A"], (cx - rx, cy, cx + rx, cy + ry * 0.75), seed, angle=-90, n=30, shade="#8A4A1A", shade_op=0.45, ink_c=INK, ink_w=2))
    for k in range(18):
        a = math.pi * k / 17
        x = cx - math.cos(a) * rx * 0.96
        out.append(f'<path d="M {_f(x)} {_f(cy + math.sin(a) * ry * 0.5)} l 0 {_f(ry * 0.22)}" stroke="#A8682A" stroke-width="1.6" opacity="0.7"/>')
    # fluted crust ring
    pts = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        rr = 1.0 + (0.035 if i % 2 else -0.01)
        pts.append((cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr))
    crust = smooth_closed(pts)
    out.append(paint(P, crust, "#E8B47A", ["#F2CC94", "#C88A4A", "#FBE0B4"], (cx - rx, cy - ry, cx + rx, cy + ry), seed + 1, angle=-30, n=40, ink_c=INK, ink_w=2))
    fill = blob(cx, cy, rx * 0.84, ry * 0.8, seed + 2, 0.01, 30)
    g = P.rg([(0, "#E8904A"), (0.7, "#D07432"), (1, "#B85A22")], cx=0.45, cy=0.4, r=0.65)
    out.append(f'<path d="{fill}" fill="url(#{g})"/>')
    out.append(strokes(P.id("s"), fill, (cx - rx, cy - ry, cx + rx, cy + ry), ["#F2A060", "#B85A22", "#E88A44"], seed + 3, 40, angle=-10, length=(rx * 0.1, rx * 0.3), width=(1.5, 4), opacity=(0.2, 0.45), curve=0.5))
    out.append(dab_dots(seed + 4, 30, (cx - rx * 0.7, cy - ry * 0.6, cx + rx * 0.7, cy + ry * 0.6), ["#8A3A12", "#A84A1A"], (0.8, 1.6), (0.4, 0.8)))
    if cut == "wedge":
        wedge = smooth_closed([(cx + 4, cy + 2), (cx + rx * 0.98, cy + ry * 0.12), (cx + rx * 0.9, cy + ry * 0.5), (cx + rx * 0.62, cy + ry * 0.86)])
        out.append(f'<path d="{wedge}" fill="#C8C2B4"/>' + strokes(P.id("s"), wedge, (cx, cy, cx + rx, cy + ry), ["#E2DCCC", "#A8A090"], seed + 5, 12, angle=20, length=(10, 30), width=(2, 5), opacity=(0.3, 0.6)))
        cut_face = smooth_closed([(cx + 4, cy + 2), (cx + rx * 0.62, cy + ry * 0.86), (cx + rx * 0.62, cy + ry * 0.86 + 22), (cx + 4, cy + 26)])
        out.append(paint(P, cut_face, "#E2843E", ["#F2A060", "#C8642A"], (cx, cy, cx + rx * 0.7, cy + ry + 26), seed + 6, angle=0, n=10, ink_c=INK, ink_w=1.6))
        out.append(f'<path d="M {_f(cx + 4)} {_f(cy + 20)} L {_f(cx + rx * 0.62)} {_f(cy + ry * 0.86 + 16)}" stroke="#E8B47A" stroke-width="7"/>')
        out.append(ink(wedge, INK, 1.6, seed + 5, 1, 0.6))
    elif cut:
        for a in (-20, 60, 140, 220):
            ar = math.radians(a)
            out.append(f'<path d="M {_f(cx)} {_f(cy)} L {_f(cx + math.cos(ar) * rx * 0.84)} {_f(cy + math.sin(ar) * ry * 0.8)}" stroke="#A84A1A" stroke-width="1.6" opacity="0.6"/>')
    # crust leaves and cream dollop
    for k, (dx, dy, rot) in enumerate(((-0.62, -0.42, -30), (-0.3, -0.7, 10), (0.1, -0.74, 40), (-0.86, -0.02, -70))):
        out.append(maple_leaf(cx + dx * rx, cy + dy * ry, rx * 0.12, "#E8B47A", "#B87A3A", rot=rot, seed=seed + 10 + k, vein="#FBE0B4"))
    for k, (dx, dy, r) in enumerate(((-0.28, -0.08, 0.2), (-0.16, -0.18, 0.16), (-0.3, -0.26, 0.12), (-0.22, -0.34, 0.08))):
        d = blob(cx + dx * rx, cy + dy * ry, rx * r, rx * r * 0.7, seed + 20 + k, 0.08, 14)
        out.append(paint(P, d, "#FFFBF2", ["#FFFFFF", "#EDE0D2"], (cx - rx, cy - ry, cx + rx, cy + ry), seed + 20 + k, n=4, shade="#C8B8B0", shade_op=0.5, ink_c="#9A8A7A", ink_w=1.3, ink_op=0.6))
    return "".join(out)


def grateful():
    """Grateful, and full of pie: a pumpkin pie with a slice already gone, crust leaves and cream, on a mustard cloth."""
    P = Pn("grateful")
    o = [sky_wash(P, "#2E5A5E", "#24484C", [TEAL, TEAL_D, "#3E6E72", "#1E4246"], 2001, box=(0, 0, 600, 600), n=300, angle=-10)]
    o.append(mottle(2002, ["#5A8A8A", "#14302F"], 10))
    o.append(P.glow(300, 420, 260, "#F6D27A", 0.25))
    # mustard tablecloth with a stitched hem
    cloth = org_poly([(-10, 400), (610, 396), (610, 610), (-10, 610)], 2003, 1, 30, 2)
    o.append(paint(P, cloth, "#E2A83A", ["#F2C25A", "#B8801E", "#E8B84A"], (-10, 396, 610, 610), 2003, angle=0, n=160, length=(30, 90), width=(1.5, 4), ink_c=None))
    for k in range(9):
        x = 30 + k * 68
        o.append(f'<path d="{hline(x, 396, x + 20, 610, 2004 + k, 0.8, 30)}" stroke="#C8901E" stroke-width="3" fill="none" opacity="0.5"/>')
    o.append(f'<path d="{hline(-10, 412, 610, 408, 2015, 0.5)}" stroke="#FBF0D8" stroke-width="2" fill="none" stroke-dasharray="8 6" opacity="0.8"/>')
    o.append(f'<path d="{hline(-10, 398, 610, 394, 2016, 0.5)}" stroke="{INK}" stroke-width="2" fill="none" opacity="0.6"/>')
    # cake stand with the pie
    o.append(cast(250, 536, 150, 10, "#3A2418", 0.35, 2017))
    stand = smooth_closed([(210, 536), (222, 500), (234, 470), (266, 470), (278, 500), (290, 536)])
    o.append(paint(P, stand, "#FBF6EE", ["#FFFFFF", "#D8D0C8"], (210, 470, 290, 536), 2018, n=8, shade="#A8A0A8", shade_op=0.5, shade_dir=(0, 0, 1, 0), ink_c=INK, ink_w=2))
    plate = blob(250, 464, 186, 30, 2019, 0.01, 30)
    o.append(paint(P, plate, "#FBF6EE", ["#FFFFFF", "#E2DAD2"], (64, 434, 436, 494), 2019, n=10, shade="#B8B0B8", shade_op=0.5, ink_c=INK, ink_w=2))
    o.append(pumpkin_pie(P, 248, 400, 160, 64, 2020, cut=True))
    # the slice, served on a little plate with a fork
    o.append(cast(452, 540, 92, 10, "#3A2418", 0.3, 2030))
    sp = blob(448, 524, 88, 22, 2031, 0.01, 24)
    o.append(paint(P, sp, "#FBF6EE", ["#FFFFFF", "#E2DAD2"], (360, 502, 536, 546), 2031, n=6, shade="#B8B0B8", shade_op=0.5, ink_c=INK, ink_w=1.8))
    o.append(ink(blob(448, 522, 64, 15, 2032, 0.01, 24), TEAL_L, 2, 2032, 1, 0.8))
    tip, b1, b2 = (390, 520), (494, 476), (512, 506)
    side = org_poly([tip, b2, (512, 528), (390, 540)], 2033, 0.4, 12, 2)
    o.append(paint(P, side, "#E2843E", ["#F2A060", "#C8642A"], (390, 476, 512, 540), 2033, angle=0, n=8, ink_c=INK, ink_w=1.6))
    o.append(f'<path d="M 390 530 L 512 518" stroke="#E8B47A" stroke-width="7"/>')
    crust_back = smooth_closed([b1, (500, 470), (514, 482), (520, 500), b2, (510, 532), (518, 520)])
    o.append(paint(P, org_poly([b1, (506, 470), (522, 494), b2, (512, 528), (500, 500)], 2034, 0.5, 8, 4), "#E8B47A", ["#F2CC94", "#C88A4A"], (494, 466, 524, 532), 2034, n=6, ink_c=INK, ink_w=1.6))
    top = org_poly([tip, b1, b2], 2035, 0.5, 12, 2)
    o.append(paint(P, top, "#E08A44", ["#F2A060", "#B85A22"], (390, 476, 512, 520), 2035, angle=-10, n=10, ink_c=INK, ink_w=1.6))
    o.append(paint(P, blob(462, 494, 16, 10, 2036, 0.1, 12), "#FFFBF2", ["#FFFFFF", "#EDE0D2"], (446, 484, 478, 504), 2036, n=3, shade="#C8B8B0", shade_op=0.5, ink_c="#9A8A7A", ink_w=1.2))
    o.append(f'<path d="M 382 506 L 330 480" stroke="#C8C4BC" stroke-width="6" stroke-linecap="round"/><path d="M 382 506 L 330 480" stroke="{INK}" stroke-width="1" opacity="0.5"/>'
             f'<path d="M 384 507 l 18 9 M 386 502 l 18 9 M 382 511 l 18 9" stroke="#C8C4BC" stroke-width="2.4" stroke-linecap="round"/>')
    o.append(sparkles(2040, 8, (70, 260, 530, 400), GOLD_L, (5, 10), avoid=((110, 320, 490, 420),)))
    o.append(maple_leaf(98, 470, 22, "#C8502A", "#8A2E14", rot=-30, seed=2041) + maple_leaf(504, 476, 20, "#E8A83A", "#B8781A", rot=24, seed=2042))
    o.append(btext(P, 300, 160, "grateful", SERIF_IT, 136, "#F2C25A", [GOLD_L, GOLD_D, "#F6D27A", "#E2A83A"], 2050, max_w=470, shadow="#14302F", sh=(0.02, 0.035), hi="#FFF0B8"))
    o.append(flank(222, "& FULL OF PIE", BEBAS, 40, 10, "#F6EEDF", max_w=300, L=36, seed=2051))
    o.append(ptext(300, 236, "& FULL OF PIE", BEBAS, 40, "#F6EEDF", max_w=300, ls=10))
    return finish(P, "".join(o), 2052)


# --------------------------------------------------------------- winter: Hanukkah, happy holidays
def taper(P, x, base, h, w, col, seed, lit=True, stripes=None):
    out = []
    d = org_rect(x - w / 2, base - h, w, h, seed, 0.3, 8, 1.5)
    out.append(paint(P, d, col, [lt(col, 0.4), dk(col, 0.15)], (x - w / 2, base - h, x + w / 2, base), seed, n=4, shade=dk(col, 0.4), shade_op=0.4, shade_dir=(0, 0, 1, 0), ink_c=INK, ink_w=1.2))
    if stripes:
        cid = P.clip(f'<path d="{d}"/>')
        st = "".join(f'<path d="M {_f(x - w)} {_f(base - k * 9)} l {_f(2 * w)} {_f(-w)}" stroke="{stripes}" stroke-width="3"/>' for k in range(int(h / 9) + 2))
        out.append(f'<g clip-path="url(#{cid})">{st}</g>')
    if lit:
        out.append(P.glow(x, base - h - 10, 34, "#FFD27A", 0.6))
        fl = smooth_closed([(x, base - h - 22), (x + 5, base - h - 9), (x + 3.5, base - h - 2), (x, base - h), (x - 3.5, base - h - 2), (x - 5, base - h - 9)])
        out.append(f'<path d="{fl}" fill="#FFC24A"/><path d="{blob(x, base - h - 6, 2, 4, seed + 1, 0.05, 8)}" fill="#FFF6D8"/>')
        out.append(f'<path d="M {_f(x)} {_f(base - h)} l 0 -3" stroke="#3A2418" stroke-width="1.2"/>')
    return "".join(out)


def menorah(P, cx, base, s, seed, metal="#D8B060"):
    """Nine-branched menorah: curved arms, cups, a taller shamash at the centre, all candles lit."""
    out = [cast(cx, base, s * 1.05, s * 0.06, "#000000", 0.35, seed)]
    foot = smooth_closed([(cx - s * 0.32, base), (cx - s * 0.26, base - s * 0.08), (cx - s * 0.06, base - s * 0.14), (cx + s * 0.06, base - s * 0.14), (cx + s * 0.26, base - s * 0.08), (cx + s * 0.32, base)])
    tints = [lt(metal, 0.4), dk(metal, 0.3), "#FFF0B8"]
    out.append(paint(P, foot, metal, tints, (cx - s * 0.32, base - s * 0.14, cx + s * 0.32, base), seed, n=10, shade=dk(metal, 0.5), shade_op=0.5, shade_dir=(0, 0, 1, 0), ink_c=INK, ink_w=1.8))
    top_y = base - s * 0.86
    stem_w = s * 0.045
    # arms (concentric half-ellipses from the central stem)
    for k in range(1, 5):
        rx = s * 0.22 * k
        ry = s * 0.5 * (0.35 + 0.65 * k / 4)
        d = f"M {_f(cx - rx)} {_f(top_y)} A {_f(rx)} {_f(ry)} 0 0 0 {_f(cx + rx)} {_f(top_y)}"
        out.append(f'<path d="{d}" stroke="{dk(metal, 0.4)}" stroke-width="{_f(s * 0.05)}" fill="none" stroke-linecap="round"/>'
                   f'<path d="{d}" stroke="{metal}" stroke-width="{_f(s * 0.036)}" fill="none" stroke-linecap="round"/>'
                   f'<path d="{d}" stroke="#FFF0B8" stroke-width="{_f(s * 0.01)}" fill="none" stroke-linecap="round" opacity="0.7" transform="translate(-1 -1)"/>')
    stem_d = org_rect(cx - stem_w / 2, base - s * 0.98, stem_w, s * 0.86, seed + 1, 0.3, 10, 1)
    out.append(paint(P, stem_d, metal, tints, (cx - stem_w, base - s, cx + stem_w, base), seed + 1, n=6, ink_c=INK, ink_w=1.4))
    for k in range(3):
        out.append(ball_paint(P, cx, base - s * (0.22 + k * 0.2), s * 0.04, metal, seed + 2 + k, hi=False))
    # cups + candles
    cols = ["#4A7AC8", "#F6F2E8", "#4A7AC8", "#F6F2E8"]
    for k in range(-4, 5):
        x = cx + k * s * 0.22
        y = top_y - (s * 0.14 if k == 0 else 0)
        cup = smooth_closed([(x - s * 0.06, y - s * 0.03), (x + s * 0.06, y - s * 0.03), (x + s * 0.035, y + s * 0.03), (x - s * 0.035, y + s * 0.03)])
        out.append(paint(P, cup, metal, tints, (x - s * 0.06, y - s * 0.03, x + s * 0.06, y + s * 0.03), seed + 10 + k, n=3, ink_c=INK, ink_w=1.2))
        col = "#F6F2E8" if k == 0 else cols[abs(k) % 4]
        out.append(taper(P, x, y - s * 0.03, s * 0.2, s * 0.05, col, seed + 20 + k, stripes="#FFFFFF" if col != "#F6F2E8" else "#9CC0F0"))
    return "".join(out)


def dreidel(P, cx, cy, s, seed, col="#4A7AC8", rot=0, letter="ש"):
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    body = smooth_closed([(cx - s * 0.5, cy - s * 0.5), (cx + s * 0.5, cy - s * 0.5), (cx + s * 0.5, cy + s * 0.2), (cx, cy + s * 0.85), (cx - s * 0.5, cy + s * 0.2)])
    out.append(paint(P, body, col, [lt(col, 0.3), dk(col, 0.25)], (cx - s * 0.5, cy - s * 0.5, cx + s * 0.5, cy + s * 0.85), seed, n=10, shade=dk(col, 0.45), shade_op=0.5, shade_dir=(0, 0, 1, 0), ink_c=INK, ink_w=1.8))
    out.append(f'<path d="M {_f(cx + s * 0.18)} {_f(cy - s * 0.5)} L {_f(cx + s * 0.18)} {_f(cy + s * 0.5)}" stroke="{dk(col, 0.35)}" stroke-width="1.4" opacity="0.7"/>')
    out.append(f'<path d="{org_rect(cx - s * 0.08, cy - s * 0.9, s * 0.16, s * 0.42, seed + 1, 0.3, 6, 2)}" fill="{GOLD}" stroke="{INK}" stroke-width="1.4"/>')
    # a simple painted glyph mark (stylised, not text)
    out.append(f'<path d="M {_f(cx - s * 0.24)} {_f(cy - s * 0.26)} L {_f(cx - s * 0.24)} {_f(cy + s * 0.1)} L {_f(cx + s * 0.08)} {_f(cy + s * 0.1)} L {_f(cx + s * 0.08)} {_f(cy - s * 0.26)} '
               f'M {_f(cx - s * 0.08)} {_f(cy - s * 0.26)} L {_f(cx - s * 0.08)} {_f(cy + s * 0.02)}" stroke="#FFF6D8" stroke-width="{_f(s * 0.07)}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append("</g>")
    return "".join(out)


def happy_hanukkah():
    """Eight nights of light: a brass menorah fully lit on the windowsill, dreidels and chocolate gelt, a blue winter night."""
    P = Pn("happy-hanukkah")
    o = [sky_wash(P, "#1E3466", "#2E4A86", ["#24407A", "#3A5A9A", "#182C5A", "#4A6AAA"], 2101, n=300, angle=-6, mid=(0.5, "#264080"))]
    o.append(mottle(2102, ["#5A7ABA", "#101E40"], 10))
    rnd = random.Random(2103)
    for k in range(22):
        x, y = rnd.uniform(40, 560), rnd.uniform(40, 300)
        if 80 < x < 520 and 50 < y < 240:
            continue
        o.append(twinkle(x, y, rnd.uniform(3, 7), "#DCE6F6", round(rnd.uniform(0.5, 0.9), 2)))
    o.append(P.glow(300, 390, 280, "#FFD27A", 0.35))
    # windowsill / table
    sill = org_poly([(-10, 470), (610, 466), (610, 610), (-10, 610)], 2104, 0.8, 30, 2)
    o.append(paint(P, sill, "#E8EEF6", ["#FFFFFF", "#C8D4E6", "#DCE4F0"], (-10, 466, 610, 610), 2104, angle=0, n=140, length=(30, 90), width=(1.5, 4), ink_c=None))
    o.append(f'<path d="{hline(-10, 470, 610, 466, 2105, 0.5)}" stroke="#14244A" stroke-width="2.4" fill="none" opacity="0.6"/>')
    for k in range(4):
        y = 492 + k * 30
        o.append(f'<path d="{hline(-10, y, 610, y, 2106 + k, 0.5)}" stroke="#9AAAC8" stroke-width="1.6" fill="none" opacity="0.5"/>')
    o.append(menorah(P, 300, 508, 214, 2110))
    o.append(dreidel(P, 104, 470, 46, 2120, col="#4A7AC8", rot=-14))
    o.append(dreidel(P, 500, 482, 36, 2121, col="#E2B04A", rot=18))
    for k, (x, y, r) in enumerate(((150, 520, 14), (176, 532, 12), (430, 526, 14), (458, 540, 11))):
        o.append(coin(P, x, y, r, 2125 + k, tilt=0.5))
    o.append(btext(P, 300, 88, "happy", SERIF_IT, 78, "#F2D27A", [GOLD_L, GOLD_D, "#F6D27A"], 2130, max_w=280, shadow="#101E40", sh=(0.02, 0.035)))
    o.append(btext(P, 300, 202, "HANUKKAH", BEBAS, 104, "#F2F4FA", ["#FFFFFF", "#C8D4E6", "#DCE4F0", "#B8C8E0"], 2131, ls=10, max_w=440, shadow="#101E40", sh=(0.025, 0.035)))
    return finish(P, "".join(o), 2132)


def happy_holidays():
    """A cardinal on a snowy pine bough with winterberries, flakes drifting down through a cool blue morning."""
    P = Pn("happy-holidays")
    o = [sky_wash(P, "#CFDDE8", "#EEF2F4", ["#DCE6EE", "#BCCEDC", "#F2F6F8", "#FFFFFF"], 2201, n=240, angle=-8, mid=(0.6, "#E2EAF0"))]
    o.append(mottle(2202, ["#FFFFFF", "#9AB0C4"], 10))
    o.append(far_trees(P, 560, 2203, "#B8CADA", n=30, h=(60, 120), w=0.42, snow=True))
    o.append(far_trees(P, 600, 2204, "#9AB0C4", n=20, h=(60, 110), w=0.42, snow=True))
    # the bough
    br = [(-10, 432), (110, 414), (230, 402), (350, 404), (470, 384), (610, 372)]
    o.append(branch(P, br, 16, 8, 2205, col="#5A4030"))
    o.append(branch(P, [(300, 404), (366, 446), (420, 470)], 7, 4, 2206, col="#5A4030"))
    for k in range(9):
        x = -10 + k * 72
        y = 432 - k * 7
        o.append(pine_sprig(P, x, y + 4, x + 64, y - 22, 2207 + k, cols=(PINE_D, PINE, PINE_L, "#3E6E50"), needle=24, density=1.4))
        o.append(pine_sprig(P, x + 20, y + 4, x + 78, y + 30, 2220 + k, cols=(PINE_D, PINE, "#3E6E50"), needle=20, density=1.2))
    o.append(snow_cap(P, [(0, 422), (110, 404), (230, 392), (350, 394), (470, 374), (600, 362)], 16, 2230))
    # winterberries
    rnd = random.Random(2231)
    for k in range(22):
        bx = rnd.choice((rnd.uniform(70, 200), rnd.uniform(380, 520)))
        by = rnd.uniform(420, 480)
        o.append(ball_paint(P, bx, by, rnd.uniform(6, 8.5), "#C8282E", 2232 + k))
    o.append(holly(P, 456, 452, 34, -20, 2260))
    # the cardinal
    bx_, by_, bs = 270, 334, 128
    o.append(songbird(P, bx_, by_, bs, 2270, body="#C8282E", belly="#D84A3A", wing="#9A1E22", beak="#F2A23A", flip=1, crest=True))
    o.append(f'<path d="{smooth_closed([(bx_ + 0.3 * bs, by_ - 0.33 * bs), (bx_ + 0.62 * bs, by_ - 0.17 * bs), (bx_ + 0.44 * bs, by_ - 0.0 * bs), (bx_ + 0.2 * bs, by_ - 0.12 * bs)])}" fill="#24141A" opacity="0.85"/>')
    o.append(f'<path d="M {_f(bx_ + 0.46 * bs)} {_f(by_ - 0.2 * bs)} L {_f(bx_ + 0.72 * bs)} {_f(by_ - 0.12 * bs)} L {_f(bx_ + 0.47 * bs)} {_f(by_ - 0.06 * bs)} Z" fill="#F2A23A" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round"/>')
    o.append(f'<circle cx="{_f(bx_ + 0.3 * bs)}" cy="{_f(by_ - 0.2 * bs)}" r="5.6" fill="#1A1210"/><circle cx="{_f(bx_ + 0.29 * bs)}" cy="{_f(by_ - 0.215 * bs)}" r="2" fill="#FFFFFF"/>')
    o.append(flakes(2280, 60, (20, 20, 580, 580), avoid=((70, 50, 530, 240),)))
    o.append(btext(P, 300, 98, "happy", SERIF_IT, 88, "#C8282E", ["#D8423A", "#9A1E22", "#E2685A"], 2290, max_w=280, shadow="#FFFFFF", sh=(0.02, 0.03)))
    o.append(btext(P, 300, 230, "HOLIDAYS", BEBAS, 114, PINE, [PINE_L, PINE_D, "#2F6A4C", SAGE], 2291, ls=10, max_w=440, shadow="#FFFFFF", sh=(0.025, 0.035), hi="#A9CFA8"))
    return finish(P, "".join(o), 2292)

# --------------------------------------------------------------- life moments: birthday, anniversary, baby, new home
def balloon(P, x, y, r, col, seed, sx, sy):
    out = [f'<path d="M {_f(x)} {_f(y + r * 1.15)} C {_f(x - r * 0.4)} {_f(y + r * 2)} {_f(sx + r * 0.4)} {_f(sy - r * 1.2)} {_f(sx)} {_f(sy)}" stroke="#8A7A6A" stroke-width="1.6" fill="none"/>']
    d = smooth_closed([(x, y - r * 1.1), (x + r * 0.9, y - r * 0.55), (x + r * 0.85, y + r * 0.4), (x + r * 0.2, y + r * 1.1), (x, y + r * 1.15), (x - r * 0.2, y + r * 1.1), (x - r * 0.85, y + r * 0.4), (x - r * 0.9, y - r * 0.55)])
    out.append(paint(P, d, col, [lt(col, 0.3), dk(col, 0.2)], (x - r, y - r * 1.1, x + r, y + r * 1.15), seed, angle=-70, n=10, curve=0.5, ink_c=None))
    g = P.rg([(0, "#FFFFFF", 0.6), (0.35, col, 0), (1, dk(col, 0.4), 0.5)], cx=0.36, cy=0.3, r=0.75)
    out.append(f'<path d="{d}" fill="url(#{g})"/>' + ink(d, INK, 1.8, seed, 2, 0.75))
    out.append(f'<path d="M {_f(x - 5)} {_f(y + r * 1.13)} l 5 8 l 5 -8 Z" fill="{dk(col, 0.2)}"/>')
    out.append(f'<path d="M {_f(x - r * 0.55)} {_f(y - r * 0.35)} Q {_f(x - r * 0.5)} {_f(y - r * 0.8)} {_f(x - r * 0.1)} {_f(y - r * 0.9)}" stroke="#FFFFFF" stroke-width="{_f(r * 0.12)}" fill="none" stroke-linecap="round" opacity="0.65"/>')
    return "".join(out)


def layer_cake(P, cx, base, w, seed):
    """Three-layer celebration cake: frosting tiers with drips, sprinkles, rosettes and lit candles."""
    out = []
    tiers = [(w, 70, "#F6C2CC", "#E8899A"), (w * 0.78, 64, "#FBF4E8", "#E8D8C2"), (w * 0.56, 58, "#BFE0D2", "#8AC0AA")]
    y = base
    tops = []
    for k, (tw, th, col, dark) in enumerate(tiers):
        x0 = cx - tw / 2
        d = org_rect(x0, y - th, tw, th, seed + k, 0.6, 14, 6)
        out.append(paint(P, d, col, [lt(col, 0.35), dk(col, 0.12), col], (x0, y - th, x0 + tw, y), seed + k, angle=-90, n=int(tw / 5), shade=dark, shade_op=0.5, shade_dir=(0, 0, 1, 0), ink_c=INK, ink_w=2))
        # drips from the tier above's icing
        rnd = random.Random(seed + k)
        drip_c = ["#FFFBF4", "#E8899A", "#FBF4E8"][k]
        pts = [(x0 - 2, y - th - 2)]
        n = int(tw / 22)
        for i in range(n + 1):
            xx = x0 + tw * i / n
            pts.append((xx, y - th + rnd.uniform(10, 26) if i % 2 else y - th + 6))
        pts.append((x0 + tw + 2, y - th - 2))
        dd = smooth_closed(pts)
        out.append(f'<path d="{dd}" fill="{drip_c}"/>' + ink(dd, INK, 1.2, seed + 10 + k, 1, 0.45))
        out.append(dab_dots(seed + 20 + k, int(tw / 8), (x0 + 8, y - th + 26, x0 + tw - 8, y - 8), ["#E2574A", GOLD, "#4A8ACB", "#5EA05A", "#FFFFFF"], (1.4, 2.4), (0.8, 1)))
        y -= th
        tops.append((x0, y, tw))
    # top icing ellipse + rosettes
    x0, ty, tw = tops[-1]
    top = blob(cx, ty, tw / 2 + 2, 12, seed + 30, 0.02, 20)
    out.append(paint(P, top, "#FFFBF4", ["#FFFFFF", "#EDE0D2"], (cx - tw / 2, ty - 12, cx + tw / 2, ty + 12), seed + 30, n=6, ink_c=INK, ink_w=1.6))
    for k in range(5):
        rx = cx - tw * 0.4 + k * tw * 0.2
        out.append(ball_paint(P, rx, base - 70 + 3, 7, "#F6C2CC", seed + 40 + k, hi=False))
    for k in range(4):
        rx = cx - w * 0.3 + k * w * 0.2
        out.append(ball_paint(P, rx, base - 134 + 3, 6, "#FFFBF4", seed + 50 + k, hi=False))
    # candles
    for k, (dx, col) in enumerate(((-0.3, "#4A8ACB"), (-0.1, "#E2574A"), (0.1, "#F2C24A"), (0.3, "#5EA05A"))):
        out.append(taper(P, cx + dx * tw, ty + 2, 38, 9, col, seed + 60 + k, stripes="#FFFFFF"))
    return "".join(out)


def happy_birthday():
    """A three-tier party cake with drips, sprinkles and four lit candles, balloons and paper bunting all around."""
    P = Pn("happy-birthday")
    o = [paper_bg(P, "#E8F2EC", "#4A6A5A", 2301, tints=["#D2E8DC", "#FFFFFF"], blobs=[(300, 410, 220, 150, "#FBEFE2", 0.7)])]
    o.append(confetti(2302, 70, (30, 30, 570, 570), ["#E2574A", GOLD, "#4A8ACB", "#E8899A", "#5EA05A"], avoid=((70, 40, 530, 240), (140, 250, 460, 540))))
    o.append(balloon(P, 112, 300, 40, "#E8899A", 2303, 160, 470))
    o.append(balloon(P, 166, 268, 34, GOLD_L, 2304, 170, 470))
    o.append(balloon(P, 488, 290, 40, "#8AC0E2", 2305, 440, 470))
    o.append(balloon(P, 438, 262, 32, "#A8D4C0", 2306, 432, 470))
    # cake stand
    o.append(cast(300, 534, 170, 12, "#3A2418", 0.3, 2307))
    stand = smooth_closed([(256, 534), (268, 512), (280, 494), (320, 494), (332, 512), (344, 534)])
    o.append(paint(P, stand, "#FBF6EE", ["#FFFFFF", "#D8D0C8"], (256, 494, 344, 534), 2308, n=8, shade="#A8A0A8", shade_op=0.5, shade_dir=(0, 0, 1, 0), ink_c=INK, ink_w=2))
    plate = blob(300, 490, 150, 18, 2309, 0.01, 30)
    o.append(paint(P, plate, "#FBF6EE", ["#FFFFFF", "#E2DAD2"], (150, 472, 450, 508), 2309, n=8, shade="#B8B0B8", shade_op=0.5, ink_c=INK, ink_w=2))
    o.append(layer_cake(P, 300, 490, 250, 2310))
    o.append(sparkles(2390, 6, (80, 240, 520, 520), GOLD, (6, 10), avoid=((130, 240, 470, 520),)))
    o.append(btext(P, 300, 90, "happy", SERIF_IT, 82, "#C8506A", ["#E8899A", "#A83A54", "#F2B8BE"], 2391, max_w=280, shadow="#FBEFE2", sh=(0.02, 0.03)))
    o.append(btext(P, 300, 226, "BIRTHDAY", ANTON, 104, "#2E6E74", [TEAL, TEAL_D, "#3E8A8E", TEAL_L], 2392, ls=6, max_w=440, shadow=GOLD_L, sh=(0.025, 0.035), hi="#9CC8C4"))
    return finish(P, "".join(o), 2393)


def happy_anniversary():
    """Two lovebirds lean together on a blossoming branch, a heart floating between them."""
    P = Pn("happy-anniversary")
    o = [sky_wash(P, "#3E6E74", "#5A8A8A", [TEAL, "#4A7E82", "#5E9294", "#33626A"], 2401, n=280, angle=-10, mid=(0.5, "#4A7A7E"))]
    o.append(mottle(2402, ["#8ABAB8", "#1E4448"], 10))
    o.append(P.glow(300, 380, 220, "#FBE2C0", 0.4))
    br = [(-10, 500), (120, 482), (250, 474), (370, 478), (490, 462), (610, 444)]
    o.append(branch(P, br, 18, 9, 2403, col="#6A4A34"))
    o.append(branch(P, [(150, 482), (110, 440), (96, 410)], 6, 3, 2404, col="#6A4A34"))
    o.append(branch(P, [(430, 470), (482, 510), (520, 522)], 6, 3, 2405, col="#6A4A34"))
    for k, (x, y, L, a) in enumerate(((100, 430, 34, -130), (118, 460, 30, 160), (500, 512, 32, 40), (470, 500, 28, 100), (70, 490, 32, -90), (556, 450, 30, -60))):
        o.append(p_leaf(P, x, y, L, a, [LEAF_L, LEAF, "#8AAE5A"][k % 3], 2410 + k, 0.34))
    for k, (x, y, r) in enumerate(((96, 406, 15), (84, 480, 13), (520, 524, 15), (540, 440, 12), (190, 492, 11), (420, 482, 11))):
        o.append(blossom(P, x, y, r, 2420 + k, col=["#FBE4E6", "#F8D2D8"][k % 2], rot=k * 17))
    # the lovebirds
    o.append(songbird(P, 232, 408, 112, 2430, body=CORAL, belly="#FBD8C4", wing=CORAL_D, beak="#F2C24A", flip=1))
    o.append(songbird(P, 368, 408, 112, 2431, body="#F2C24A", belly="#FBEBC0", wing="#C8901E", beak=CORAL, flip=-1))
    o.append(p_heart(P, 300, 300, 30, "#E2574A", 2432, n=10))
    for k, (x, y, sz) in enumerate(((258, 264, 9), (342, 256, 7), (300, 244, 6))):
        o.append(p_heart(P, x, y, sz, "#F2A6B8", 2433 + k, n=3, hi=False))
    o.append(sparkles(2440, 8, (70, 250, 530, 520), "#FBE2C0", (5, 9), avoid=((150, 260, 450, 470),)))
    o.append(btext(P, 300, 96, "happy", SERIF_IT, 86, "#FBE2C0", ["#FFF2DC", "#F2CCA0", "#FBE8CC"], 2450, max_w=280, shadow="#1E4448", sh=(0.02, 0.035)))
    o.append(btext(P, 300, 214, "ANNIVERSARY", BEBAS, 100, "#FBF4EA", ["#FFFFFF", "#E8DCC8", "#F2E8D6"], 2451, ls=6, max_w=460, shadow="#C8503A", sh=(0.025, 0.035)))
    return finish(P, "".join(o), 2452)


def onesie(P, cx, top, w, col, seed, pattern=None, pcol="#FFFFFF"):
    h = w * 1.05
    pts = [(cx - w * 0.16, top), (cx - w * 0.5, top + h * 0.1), (cx - w * 0.56, top + h * 0.34), (cx - w * 0.36, top + h * 0.36), (cx - w * 0.34, top + h * 0.72),
           (cx - w * 0.14, top + h), (cx + w * 0.14, top + h), (cx + w * 0.34, top + h * 0.72), (cx + w * 0.36, top + h * 0.36), (cx + w * 0.56, top + h * 0.34),
           (cx + w * 0.5, top + h * 0.1), (cx + w * 0.16, top), (cx, top + h * 0.1)]
    d = org_poly(pts, seed, 0.6, 12, 4)
    inner = [paint(P, d, col, [lt(col, 0.3), dk(col, 0.12)], bbox(pts), seed, n=16, ink_c=None)]
    rnd = random.Random(seed)
    if pattern == "stars":
        for _ in range(9):
            x, y = rnd.uniform(cx - w * 0.4, cx + w * 0.4), rnd.uniform(top + h * 0.15, top + h * 0.85)
            inner.append(f'<polygon points="{" ".join(f"{_f(px)},{_f(py)}" for px, py in star_pts(x, y, w * 0.06, w * 0.026))}" fill="{pcol}"/>')
    elif pattern == "stripes":
        for k in range(6):
            yy = top + h * (0.18 + k * 0.13)
            inner.append(f'<path d="{hline(cx - w * 0.6, yy, cx + w * 0.6, yy, seed + k, 0.5)}" stroke="{pcol}" stroke-width="{_f(w * 0.05)}" fill="none"/>')
    elif pattern == "heart":
        inner.append(p_heart(P, cx, top + h * 0.45, w * 0.16, pcol, seed + 3, n=4))
    g = P.lg([(0, "#FFFFFF", 0.2), (0.5, "#FFFFFF", 0), (1, "#3A2418", 0.25)], 0, 0, 1, 0)
    inner.append(f'<path d="{d}" fill="url(#{g})"/>')
    cid = P.clip(f'<path d="{d}"/>')
    out = [f'<path d="{d}" fill="#3A2418" opacity="0.15" transform="translate(5 7)"/>', f'<g clip-path="url(#{cid})">{"".join(inner)}</g>', ink(d, INK, 1.8, seed, 2, 0.8)]
    out.append(f'<path d="M {_f(cx - w * 0.16)} {_f(top)} Q {_f(cx)} {_f(top + h * 0.14)} {_f(cx + w * 0.16)} {_f(top)}" stroke="{dk(col, 0.25)}" stroke-width="3" fill="none"/>')
    for k in (-1, 0, 1):
        out.append(f'<circle cx="{_f(cx + k * w * 0.08)}" cy="{_f(top + h * 0.95)}" r="2.2" fill="#FBF4EA" stroke="{INK}" stroke-width="0.8"/>')
    return "".join(out)


def sock(P, x, top, s, col, seed, flip=1):
    pts = [(x - s * 0.2, top), (x + s * 0.2, top), (x + s * 0.22, top + s * 0.7), (x + flip * s * 0.5 + s * 0.02, top + s * 0.86), (x + flip * s * 0.48, top + s * 1.06),
           (x - s * 0.04, top + s * 1.04), (x - s * 0.22, top + s * 0.82)]
    if flip < 0:
        pts = [(2 * x - px, py) for px, py in pts]
    d = smooth_closed(pts)
    out = [paint(P, d, col, [lt(col, 0.3), dk(col, 0.15)], bbox(pts), seed, n=10, ink_c=INK, ink_w=1.6)]
    out.append(f'<path d="{org_rect(x - s * 0.22, top, s * 0.44, s * 0.18, seed + 1, 0.3, 6, 2)}" fill="{lt(col, 0.5)}" stroke="{INK}" stroke-width="1.2"/>')
    for k in range(3):
        out.append(f'<path d="M {_f(x - s * 0.14 + k * s * 0.14)} {_f(top + 2)} l 0 {_f(s * 0.14)}" stroke="{dk(col, 0.15)}" stroke-width="1.2"/>')
    return "".join(out)


def clothespin(x, y, seed):
    return f'<path d="M {_f(x - 3.5)} {_f(y - 10)} l 7 0 l -1 22 l -5 0 Z" fill="#D8B07A" stroke="{INK}" stroke-width="1.2"/><path d="M {_f(x)} {_f(y - 10)} l 0 22" stroke="#A8804A" stroke-width="0.8"/>'


def welcome_baby():
    """Tiny clothes drying on the line in a soft spring breeze: onesies, socks and a bib, little clouds overhead."""
    P = Pn("welcome-baby")
    o = [sky_wash(P, "#CFE4EE", "#F4F2E6", ["#DCEBF2", "#BCD8E6", "#F2F6F2", "#FFFFFF"], 2501, n=220, angle=-6, mid=(0.6, "#E6EEEA"))]
    o.append(cloud(P, 92, 272, 60, 18, 2502, shade="#C8D8E6"))
    o.append(cloud(P, 510, 258, 52, 16, 2503, shade="#C8D8E6"))
    hill = smooth_closed([(-20, 500), (140, 478), (320, 490), (480, 474), (620, 486), (620, 620), (-20, 620)])
    o.append(paint(P, hill, "#B8D49A", ["#C8E2AE", "#9CC084", "#D8EAC0"], (-20, 474, 620, 620), 2504, angle=-80, n=200, length=(6, 16), width=(1, 2.4), op=(0.4, 0.8), ink_c=INK, ink_w=1.4, ink_op=0.4))
    rnd = random.Random(2505)
    for k in range(14):
        x, y = rnd.uniform(70, 530), rnd.uniform(500, 540)
        o.append(daisy(P, x, y, rnd.uniform(9, 13), 2506 + k, n=11, tilt=0.65))
    # posts and line
    for x in (70, 530):
        post = org_rect(x - 7, 310, 14, 210, 2530 + x, 0.5, 14, 2)
        o.append(paint(P, post, "#A8784A", ["#C0905A", "#7A5230"], (x - 7, 310, x + 7, 520), 2530 + x, n=8, ink_c=INK, ink_w=1.6))
    def line_y(x):
        return 326 + 30 * (1 - ((x - 300) / 230) ** 2)
    o.append(ink(smooth_open([(x, line_y(x)) for x in range(70, 531, 46)]), "#8A7A6A", 2, 2540, 1, 0.9))
    # the laundry
    o.append(onesie(P, 150, line_y(150) - 4, 108, "#F6D06B", 2541, "stars", "#FFFFFF"))
    o.append(clothespin(120, line_y(120), 1) + clothespin(180, line_y(180), 2))
    o.append(sock(P, 240, line_y(240) - 2, 54, "#A8D4C0", 2542))
    o.append(sock(P, 282, line_y(282) - 2, 54, "#A8D4C0", 2543))
    o.append(clothespin(240, line_y(240), 3) + clothespin(282, line_y(282), 4))
    o.append(onesie(P, 368, line_y(368) - 4, 112, "#F4F0E6", 2544, "stripes", "#9CC0E2"))
    o.append(clothespin(336, line_y(336), 5) + clothespin(400, line_y(400), 6))
    bx0 = 470
    bib = smooth_closed([(bx0 - 22, line_y(bx0 - 22)), (bx0 + 22, line_y(bx0 + 22)), (bx0 + 30, line_y(bx0) + 42), (bx0, line_y(bx0) + 74), (bx0 - 30, line_y(bx0) + 44)])
    o.append(paint(P, bib, "#F2B8BE", ["#FBD8DC", "#E8899A"], (bx0 - 32, line_y(bx0) - 4, bx0 + 32, line_y(bx0) + 76), 2545, n=10, ink_c=INK, ink_w=1.8))
    o.append(f'<path d="{org_rect(bx0 - 32, line_y(bx0) + 30, 64, 6, 2549, 0.3, 8, 2)}" fill="#FBF4EA" opacity="0"/>')
    o.append(p_heart(P, bx0, line_y(bx0) + 38, 11, "#FFFFFF", 2546, n=2, hi=False))
    o.append(clothespin(bx0 - 16, line_y(bx0 - 16), 7) + clothespin(bx0 + 16, line_y(bx0 + 16), 8))
    o.append(songbird(P, 516, 300, 32, 2547, body="#8AB8D8", belly="#FBE8D0", flip=-1))
    o.append(sparkles(2548, 6, (70, 240, 530, 470), GOLD_L, (5, 9), avoid=((90, 300, 510, 470),)))
    o.append(btext(P, 300, 108, "welcome", SERIF_IT, 100, "#5A8AA8", ["#7AA8C8", "#3E6A8A", "#9CC0DA"], 2550, max_w=400, shadow="#FFFFFF", sh=(0.02, 0.03)))
    o.append(btext(P, 300, 236, "BABY", ANTON, 130, "#E8A23A", [GOLD_L, "#C8801E", "#F2C25A"], 2551, ls=16, max_w=300, shadow="#5A8AA8", sh=(0.025, 0.035), hi="#FFF0B8"))
    return finish(P, "".join(o), 2552)


def key_p(P, x, y, L, ang, seed, col="#D8A848"):
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    out = []
    bow = blob(x, y, L * 0.2, L * 0.2, seed, 0.03, 16)
    out.append(paint(P, bow, col, [lt(col, 0.35), dk(col, 0.3)], (x - L * 0.2, y - L * 0.2, x + L * 0.2, y + L * 0.2), seed, n=6, shade=dk(col, 0.4), shade_op=0.4, ink_c=INK, ink_w=1.6))
    out.append(f'<path d="{blob(x, y, L * 0.09, L * 0.09, seed + 1, 0.05, 10)}" fill="#F2EEE4" stroke="{INK}" stroke-width="1.2"/>')
    sx, sy = x + ux * L * 0.18, y + uy * L * 0.18
    ex, ey = x + ux * L, y + uy * L
    out.append(ink(f"M {_f(sx)} {_f(sy)} L {_f(ex)} {_f(ey)}", INK, L * 0.1, seed, 1, 0.9))
    out.append(f'<path d="M {_f(sx)} {_f(sy)} L {_f(ex)} {_f(ey)}" stroke="{col}" stroke-width="{_f(L * 0.07)}" stroke-linecap="round"/>')
    for t, k in ((0.8, 0.14), (0.92, 0.2)):
        px, py = x + ux * L * t, y + uy * L * t
        out.append(f'<path d="M {_f(px)} {_f(py)} l {_f(nx * L * k)} {_f(ny * L * k)} l {_f(ux * L * 0.06)} {_f(uy * L * 0.06)} l {_f(-nx * L * k)} {_f(-ny * L * k)}" fill="{col}" stroke="{INK}" stroke-width="1.2"/>')
    return "".join(out)


def cottage(P, cx, base, w, h, seed):
    """Storybook cottage front: clapboard walls, shingled roof, blue door with a wreath, window boxes, chimney."""
    out = [cast(cx + 10, base + 4, w * 0.62, 10, "#3A2418", 0.3, seed)]
    x0 = cx - w / 2
    rh = h * 0.7
    # chimney behind roof
    ch = org_rect(cx + w * 0.22, base - h - rh * 0.85, w * 0.1, rh * 0.6, seed + 1, 0.4, 8, 2)
    out.append(paint(P, ch, "#B8604A", ["#C8705A", "#8A4030"], (cx + w * 0.22, base - h - rh * 0.85, cx + w * 0.32, base - h - rh * 0.25), seed + 1, n=6, ink_c=INK, ink_w=1.6))
    for k in range(3):
        y = base - h - rh * 0.8 + k * 12
        out.append(f'<path d="M {_f(cx + w * 0.22)} {_f(y)} l {_f(w * 0.1)} 0" stroke="#7A3424" stroke-width="1" opacity="0.6"/>')
    # walls
    wall = org_rect(x0, base - h, w, h, seed + 2, 0.6, 16, 3)
    inner = [paint(P, wall, "#F6EEDC", ["#FFFFFF", "#E2D6C0"], (x0, base - h, x0 + w, base), seed + 2, angle=0, n=40, ink_c=None)]
    for k in range(1, int(h / 14)):
        y = base - h + k * 14
        inner.append(f'<path d="{hline(x0, y, x0 + w, y, seed + k, 0.4)}" stroke="#C8B89C" stroke-width="1.4" fill="none" opacity="0.8"/>')
    inner.append(f'<rect x="{_f(x0)}" y="{_f(base - h)}" width="{_f(w)}" height="{_f(h)}" fill="url(#{P.lg([(0, "#3A2418", 0.18), (0.4, "#3A2418", 0), (1, "#3A2418", 0.12)], 0, 0, 1, 0)})"/>')
    cid = P.clip(f'<path d="{wall}"/>')
    out.append(f'<g clip-path="url(#{cid})">{"".join(inner)}</g>' + ink(wall, INK, 2.2, seed + 2, 2, 0.85))
    # roof
    roof_pts = [(x0 - w * 0.08, base - h + 6), (cx, base - h - rh), (x0 + w * 1.08, base - h + 6)]
    rd = org_poly(roof_pts, seed + 3, 0.8, 16, 4)
    rin = [paint(P, rd, "#5A7AA0", ["#6E8EB4", "#3E5A80", "#8AA8C8"], bbox(roof_pts), seed + 3, angle=-90, n=50, ink_c=None)]
    for k in range(1, 6):
        y = base - h + 6 - rh * k / 6
        rin.append(f'<path d="{hline(x0 - w * 0.1, y, x0 + w * 1.1, y, seed + 30 + k, 0.4)}" stroke="#2E4A6E" stroke-width="1.6" fill="none" opacity="0.6"/>')
        for j in range(14):
            xx = x0 - w * 0.1 + j * w * 0.09 + (w * 0.045 if k % 2 else 0)
            rin.append(f'<path d="M {_f(xx)} {_f(y)} l 0 {_f(rh / 6)}" stroke="#2E4A6E" stroke-width="1.2" opacity="0.45"/>')
    rcid = P.clip(f'<path d="{rd}"/>')
    out.append(f'<g clip-path="url(#{rcid})">{"".join(rin)}</g>' + ink(rd, INK, 2.4, seed + 3, 2, 0.85))
    # round attic window
    out.append(lit_window(P, cx - 16, base - h - rh * 0.55, 32, 32, seed + 4, panes=(2, 2), glow=False, sill=False, frame="#3A2418"))
    # door with wreath
    dw, dh = w * 0.2, h * 0.62
    door = org_poly([(cx - dw / 2, base), (cx - dw / 2, base - dh + dw / 2), (cx, base - dh), (cx + dw / 2, base - dh + dw / 2), (cx + dw / 2, base)], seed + 5, 0.4, 10, 3)
    out.append(paint(P, door, "#E2725B", [CORAL_L, CORAL_D, "#E88A6A"], (cx - dw / 2, base - dh, cx + dw / 2, base), seed + 5, n=14, ink_c=INK, ink_w=2))
    out.append(f'<circle cx="{_f(cx + dw * 0.3)}" cy="{_f(base - dh * 0.45)}" r="3" fill="{GOLD}" stroke="{INK}" stroke-width="1"/>')
    out.append(p_heart(P, cx, base - dh * 0.66, dw * 0.22, "#FBF4EA", seed + 6, n=3, hi=False))
    # windows with flower boxes
    for sg in (-1, 1):
        wx = cx + sg * w * 0.3 - w * 0.09
        out.append(lit_window(P, wx, base - h * 0.78, w * 0.18, h * 0.36, seed + 7 + sg, panes=(2, 2), glow=False, sill=False, frame="#3A2418", hot="#E8F2F6", warm="#A8C8DA", curtain="#F6C2C8"))
        bx = org_rect(wx - 6, base - h * 0.42, w * 0.18 + 12, 14, seed + 9 + sg, 0.4, 8, 2)
        out.append(paint(P, bx, "#8A5A3A", ["#A8784A", "#6A3E22"], (wx - 6, base - h * 0.42, wx + w * 0.18 + 6, base - h * 0.42 + 14), seed + 9 + sg, n=4, ink_c=INK, ink_w=1.4))
        rnd = random.Random(seed + sg)
        for k in range(7):
            fx = wx - 2 + k * (w * 0.18 + 4) / 6
            out.append(f'<circle cx="{_f(fx)}" cy="{_f(base - h * 0.42 - rnd.uniform(2, 8))}" r="{rnd.uniform(4, 6):.1f}" fill="{rnd.choice(["#E8899A", "#F2C24A", "#FFFFFF", "#E2574A"])}" stroke="{INK}" stroke-width="0.8"/>')
        for k in range(5):
            fx = wx + k * w * 0.045
            out.append(f'<path d="{blob(fx, base - h * 0.42 + 2, 6, 3, seed + 40 + k, 0.1, 8, rnd.uniform(-30, 30))}" fill="{LEAF}"/>')
    # step
    out.append(paint(P, org_rect(cx - dw * 0.7, base - 6, dw * 1.4, 12, seed + 12, 0.4, 8, 2), "#C8C0B4", ["#E2DCD2", "#A8A096"], (cx - dw, base - 6, cx + dw, base + 6), seed + 12, n=6, ink_c=INK, ink_w=1.4))
    return "".join(out)


def new_home():
    """A brand-new storybook cottage with flower boxes and a heart on the door, smoke curling up, keys in hand."""
    P = Pn("new-home")
    o = [paper_bg(P, "#F6EEDF", "#6A5A4A", 2601, tints=["#E8DCC6", "#FFFFFF"], blobs=[(300, 400, 236, 170, "#DCEAE6", 0.7)])]
    o.append(cloud(P, 120, 300, 54, 16, 2602, shade="#C8D8E0", op=0.9))
    o.append(cloud(P, 488, 286, 46, 14, 2603, shade="#C8D8E0", op=0.9))
    # garden ground and path
    ground = smooth_closed([(60, 520), (150, 500), (300, 506), (450, 498), (540, 516), (520, 548), (300, 556), (80, 548)])
    o.append(paint(P, ground, "#A8CC8A", ["#BEDCA0", "#8AB86E"], (60, 496, 540, 556), 2604, angle=-80, n=80, length=(5, 12), width=(1, 2.2), op=(0.4, 0.8), ink_c=None))
    for k, (x, y, r) in enumerate(((150, 500, 26), (452, 498, 28), (110, 512, 18), (494, 512, 20))):
        o.append(paint(P, blob(x, y, r, r * 0.8, 2605 + k, 0.12, 14), "#6E9A5A", ["#8AB86E", "#4E7A3E"], (x - r, y - r, x + r, y + r), 2605 + k, n=10, ink_c=INK, ink_w=1.4))
        o.append(dab_dots(2610 + k, 6, (x - r * 0.7, y - r * 0.6, x + r * 0.7, y + r * 0.2), ["#F2B8BE", "#FFFFFF", "#F2C24A"], (2, 3), (0.9, 1)))
    o.append(cottage(P, 300, 506, 262, 164, 2620))
    path = org_poly([(282, 504), (318, 504), (346, 556), (254, 556)], 2640, 0.6, 10, 3)
    o.append(paint(P, path, "#E2D2BA", ["#F2E6D2", "#C8B496"], (254, 504, 346, 556), 2640, n=10, ink_c=INK, ink_w=1.4, ink_op=0.5))
    # chimney smoke curling into a heart
    sx, sy = 372, 238
    o.append(f'<path d="M {sx} {sy} c -8 -10 10 -16 0 -26 c -6 -8 12 -12 8 -20" stroke="#FFFFFF" stroke-width="7" fill="none" stroke-linecap="round" opacity="0.85"/>')
    o.append(p_heart(P, sx + 24, sy - 50, 11, "#F2A6B8", 2641, n=3, hi=False, ink_c=None))
    # keys on a heart ring
    # mailbox on a post with its flag up
    mx, my = 488, 438
    o.append(cast(mx + 4, 528, 30, 5, "#3A2418", 0.3, 2645))
    o.append(paint(P, org_rect(mx - 6, my + 10, 12, 92, 2646, 0.4, 10, 1), "#A8784A", ["#C0905A", "#7A5230"], (mx - 6, my + 10, mx + 6, my + 102), 2646, n=6, ink_c=INK, ink_w=1.4))
    box = smooth_closed([(mx - 34, my + 18), (mx - 34, my - 8), (mx - 26, my - 22), (mx + 26, my - 22), (mx + 34, my - 8), (mx + 34, my + 18)])
    o.append(paint(P, box, "#3E7A8A", ["#5A9AAA", "#2A5A6A"], (mx - 34, my - 22, mx + 34, my + 18), 2647, n=10, shade="#1A3A4A", shade_op=0.4, shade_dir=(0, 0, 0, 1), ink_c=INK, ink_w=1.8))
    o.append(f'<path d="{blob(mx - 34, my - 2, 6, 20, 2648, 0.03, 10)}" fill="#5A9AAA" stroke="{INK}" stroke-width="1.4"/>')
    o.append(f'<path d="M {mx + 22} {my + 4} L {mx + 22} {my - 44} L {mx + 46} {my - 38} L {mx + 22} {my - 30}" fill="#E2574A" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>')
    o.append(p_heart(P, mx, my - 2, 8, "#FBF4EA", 2649, n=2, hi=False, ink_c=None))
    # a young tree planted on moving-in day
    tx, tb = 112, 512
    o.append(cast(tx + 6, tb + 2, 34, 5, "#3A2418", 0.3, 2642))
    o.append(paint(P, org_poly([(tx - 5, tb), (tx - 3, tb - 70), (tx + 3, tb - 70), (tx + 5, tb)], 2643, 0.4, 10, 1), "#7A5230", ["#9A6A40", "#5A3418"], (tx - 6, tb - 70, tx + 6, tb), 2643, n=6, ink_c=INK, ink_w=1.4))
    crown = blob(tx, tb - 104, 44, 52, 2644, 0.1, 18)
    o.append(paint(P, crown, "#6E9A5A", ["#8AB86E", "#4E7A3E", "#A8CC8A", "#5E8A48"], (tx - 44, tb - 156, tx + 44, tb - 52), 2644, angle=-60, n=60, length=(5, 14), width=(1.5, 3.5),
                   curve=0.6, shade="#2E4A2A", shade_op=0.45, shade_dir=(0.2, 0.1, 0.9, 1), ink_c=INK, ink_w=1.8))
    o.append(dab_dots(2645, 9, (tx - 30, tb - 140, tx + 30, tb - 70), ["#E2574A", "#F2B8BE"], (2.4, 3.6), (0.9, 1)))
    o.append(btext(P, 300, 104, "new home", SERIF_IT, 100, "#3E5A80", ["#5A7AA0", "#2E4A6E", "#6E8EB4"], 2650, max_w=440, shadow="#F2D2B8", sh=(0.02, 0.03)))
    o.append(flank(152, "HERE'S TO NEW BEGINNINGS", BEBAS, 30, 6, CORAL, max_w=330, L=26, seed=2651, dots=False))
    o.append(ptext(300, 164, "HERE'S TO NEW BEGINNINGS", BEBAS, 30, CORAL_D, max_w=330, ls=6))
    return finish(P, "".join(o), 2652)

# =============================================================== registry (calendar order)
ORDER = ["cheers", "happy-new-year", "xoxo", "be-my-valentine", "sweet-on-you", "happy-galentines", "lucky", "pot-of-gold", "hoppy-easter", "happy-easter", "earth-day-every-day", "thank-you-teacher", "best-mom-ever", "mom-youre-the-best", "congrats-grad", "worth-the-hassle", "best-dad-ever", "reel-cool-dad", "just-married", "happy-4th", "red-white-and-blue", "so-long-summer", "back-to-school", "thankful", "grateful", "happy-hanukkah", "happy-holidays", "happy-birthday", "happy-anniversary", "welcome-baby", "new-home"]


def build(only=None):
    for slug in ORDER:
        if only and slug not in only:
            continue
        save(COL, slug, globals()[slug.replace("-", "_")]())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
