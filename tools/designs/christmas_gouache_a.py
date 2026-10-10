"""Christmas, hand-painted edition (set A): the Christmas magnets repainted as gouache / storybook pieces.
Paper ground with tooth, organic hand-drawn shapes, layered washes with pooled edges, visible brush strokes that
follow each form, warm-brown ink lines under the paint, snow with blue-violet shadows, glowing windows and
brush-textured lettering.

Run from tools/designs:  python3 christmas_gouache_a.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from gouache import blob, blob_pts, grain, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
import paint as pt
from poster import ANTON

COL = "christmas"

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


# =============================================================== designs
def peace_on_earth():
    """A storybook Main Street on Christmas Eve: a row of snowy houses and the church, windows aglow, a big star."""
    P = Pn("peace-on-earth")
    o = []
    o.append(sky_wash(P, "#141B38", "#4A4F86", ["#222B52", "#2E3866", "#3C4478", "#1A2142", "#5A5C94"], 11, mid=(0.62, "#2D3767"), n=300))
    o.append(mottle(12, ["#6A6AA8", "#0E1430"], 9, (0, 0, 600, 420)))
    o.append(P.glow(300, 470, 300, "#F6C46A", 0.22, ry=160))
    # stars + the star of Bethlehem over the steeple
    rnd = random.Random(13)
    for _ in range(46):
        x, y = rnd.uniform(10, 590), rnd.uniform(10, 330)
        if 80 < y < 200 and 70 < x < 530:
            continue
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.8, 2.0):.1f}" fill="#FFF3D0" opacity="{rnd.uniform(0.4, 0.95):.2f}"/>')
    o.append(P.glow(300, 200, 120, "#FFE6A0", 0.5))
    o.append(twinkle(300, 200, 26, "#FFF4D2", 0.95, 0.12) + twinkle(300, 200, 13, "#FFFFFF", 1, 0.22))
    o.append(f'<g transform="rotate(45 300 200)">{twinkle(300, 200, 13, "#FFF4D2", 0.8, 0.14)}</g>')
    # distant snowy hill with a few far trees
    hill = smooth_closed([(-20, 410), (80, 382), (190, 392), (300, 376), (420, 390), (520, 378), (620, 396), (620, 470), (-20, 470)])
    o.append(f'<path d="{hill}" fill="#8F95C6"/>')
    o.append(far_trees(P, 392, 14, "#5E6699", 30, (16, 36), op=0.9))
    # houses along the street (left to right), church in the middle
    houses = [  # x, w, wall h, roof h, wall colour
        (-24, 104, 112, 58, CRAN), (78, 86, 88, 52, "#3F6E8C"), (164, 70, 120, 46, GOLD), (380, 72, 112, 48, "#4F7F5C"),
        (452, 84, 86, 54, CRAN), (536, 92, 116, 60, "#C9B48E")]
    base = 478
    for i, (x, w, h, rh, col) in enumerate(houses):
        o.append(house(P, x, base, w, h, rh, col, 30 + i * 7, chimney=(i % 2 == 0)))
    o.append(church(P, 300, base, 40))
    # street: snow with violet shadows, tracks, lamps, villagers
    street = smooth_closed([(-20, base - 6), (150, base - 2), (300, base - 8), (450, base - 2), (620, base - 6), (620, 620), (-20, 620)])
    o.append(snow_field(P, street, (-20, base - 10, 620, 620), 41, edge_c=None))
    for k, (x1, x2) in enumerate(((262, 150), (338, 450))):
        o.append(f'<path d="M {x1} {base + 6} Q {(x1 + x2) / 2:.0f} {base + 50} {x2} 640" stroke="{SNOW_SH[0]}" stroke-width="12" fill="none" opacity="0.35" stroke-linecap="round"/>')
        o.append(f'<path d="M {x1} {base + 6} Q {(x1 + x2) / 2:.0f} {base + 50} {x2} 640" stroke="{SNOW_SH[1]}" stroke-width="3" fill="none" opacity="0.35" stroke-linecap="round" transform="translate(-4 0)"/>')
    o.append(P.glow(300, base + 30, 120, "#FFD27A", 0.35, ry=34))
    o.append(fir(P, 44, base + 34, 96, 66, 57, snow=True, tiers=3, ink_c=INK_N, trunk=False))
    o.append(fir(P, 560, base + 40, 110, 74, 58, snow=True, tiers=3, ink_c=INK_N, trunk=False))
    o.append(sled(P, 452, base + 92, 59))
    for lx in (128, 472):
        o.append(lamp(P, lx, base + 40, 92, 50 + lx))
    o.append(figure(P, 214, base + 66, 46, RED, 61, scarf=CREAM, hat=PINE))
    o.append(figure(P, 236, base + 64, 36, "#3F6E8C", 62, scarf=RED, hat=RED, flip=-1))
    o.append(figure(P, 392, base + 62, 44, PINE, 63, scarf=GOLD, hat=CRAN, flip=-1))
    o.append(flakes(64, 70, (0, 0, 600, 600), (1.1, 3.0), avoid=((60, 70, 540, 170),)))
    # lettering on the night sky
    o.append(btext(P, 300, 128, "Peace on Earth", SERIF_IT, 78, CREAM, ["#FFFFFF", "#F3D9A8", "#E9C98A", CREAM], 65, max_w=470,
                   shadow="#0C1028", hi="#FFFFFF"))
    o.append(ptext(300, 168, "CHRISTMAS EVE · MAIN STREET", MONO, 18, GOLD_L, max_w=420, ls=4))
    return finish(P, "".join(o), 66)


def sled(P, x, y, seed):
    out = [cast(x + 4, y + 6, 46, 6, "#5A5A9A", 0.4, seed)]
    out.append(f'<path d="M {x - 44} {y} L {x + 34} {y} q 14 0 12 -12" stroke="{INK_N}" stroke-width="3.2" fill="none" stroke-linecap="round"/>')
    for k in (-26, 14):
        out.append(f'<path d="M {x + k} {y} l 4 -12" stroke="{INK_N}" stroke-width="3"/>')
    d = org_rect(x - 40, y - 20, 74, 9, seed, 0.5, 10, 1.5)
    out.append(paint(P, d, RED, [RED_L, RED_D], (x - 40, y - 20, x + 34, y - 11), seed, angle=0, n=8, ink_c=INK_N))
    out.append(snow_cap(P, [(x - 40, y - 20), (x - 2, y - 21), (x + 34, y - 20)], 4, seed + 1, drips=False))
    return "".join(out)


def house(P, x, base, w, h, rh, col, seed, chimney=False):
    rnd = random.Random(seed)
    out = []
    top = base - h
    wall = org_rect(x, top, w, h, seed, 1.0, 14, 2)
    out.append(paint(P, wall, col, [lt(col, 0.2), dk(col, 0.18), lt(col, 0.35)], (x, top, x + w, base), seed, angle=-88,
                     shade=dk(col, 0.6), shade_op=0.55, shade_dir=(0, 0, 1, 0.1), ink_c=INK_N, ink_op=0.65))
    if chimney:
        cx = x + w * 0.68
        cd = org_rect(cx, top - rh * 0.8, w * 0.14, rh * 0.6, seed + 1, 0.6, 8, 1)
        out.append(paint(P, cd, "#8A4A3A", ["#A86048", "#6A3428"], (cx, top - rh * 0.8, cx + w * 0.14, top), seed + 1, n=6, ink_c=INK_N, ink_op=0.6))
        out.append(snow_cap(P, [(cx - 2, top - rh * 0.8), (cx + w * 0.16, top - rh * 0.8)], 5, seed + 2, drips=False))
        # curling smoke
        sx, sy = cx + w * 0.07, top - rh * 0.85
        out.append(f'<path d="M {_f(sx)} {_f(sy)} c -10 -14 12 -22 2 -38 c -8 -12 10 -20 4 -34" stroke="#C9C8E4" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.35"/>')
    roof = org_poly([(x - 8, top + 2), (x + w / 2, top - rh), (x + w + 8, top + 2)], seed + 3, 1, 14, 2)
    rc = "#4A3A4E" if col not in ("#4A3A4E",) else PINE_D
    out.append(paint(P, roof, rc, ["#5E4C62", "#3A2C3E", "#6E5C72"], (x - 8, top - rh, x + w + 8, top + 2), seed + 3, angle=0, n=12, ink_c=INK_N, ink_op=0.6))
    # snow blanket on the roof
    out.append(snow_cap(P, [(x - 10, top + 4), (x + w * 0.25, top - rh * 0.5 + 2), (x + w / 2, top - rh + 1), (x + w * 0.75, top - rh * 0.5 + 2), (x + w + 10, top + 4)],
                        max(7, rh * 0.2), seed + 4))
    # windows: two per floor, warm, random few dark
    floors = 2 if h > 100 else 1
    ww, wh = w * 0.2, min(28, h * 0.22)
    for f in range(floors):
        wy = top + 16 + f * (h * 0.42)
        for k in (0.27, 0.73):
            if floors == 1 and k == 0.73 and w > 80:
                continue
            lit = rnd.random() > 0.12
            if lit:
                out.append(lit_window(P, x + w * k - ww / 2, wy, ww, wh, seed + f * 3 + int(k * 10), frame=INK_N, halo=1.2, curtain=None if rnd.random() < 0.5 else CRAN))
            else:
                out.append(f'<path d="{org_rect(x + w * k - ww / 2, wy, ww, wh, seed + 9, 0.5, 8, 1)}" fill="#2A2C4A" stroke="{INK_N}" stroke-width="1.6"/>')
    if floors == 1 and w > 80:
        dx = x + w * 0.62
        out.append(door(P, dx, base, w * 0.2, h * 0.5, seed + 7, RED_D if col != CRAN else PINE))
    return "".join(out)


def door(P, x, base, w, h, seed, col, wreath=True):
    d = org_poly([(x, base), (x, base - h + w / 2), (x + w / 2, base - h), (x + w, base - h + w / 2), (x + w, base)], seed, 0.5, 8, 1.5)
    out = [P.glow(x + w / 2, base - h / 2, h, "#FFC45C", 0.35),
           paint(P, d, col, [lt(col, 0.2), dk(col, 0.2)], (x, base - h, x + w, base), seed, angle=-90, n=8, ink_c=INK_N)]
    if wreath:
        r = w * 0.26
        out.append(f'<circle cx="{_f(x + w / 2)}" cy="{_f(base - h * 0.62)}" r="{_f(r)}" fill="none" stroke="{PINE_L}" stroke-width="{max(2, r * 0.6):.1f}"/>'
                   f'<circle cx="{_f(x + w / 2)}" cy="{_f(base - h * 0.62 + r)}" r="{max(1.2, r * 0.3):.1f}" fill="{RED}"/>')
    out.append(f'<circle cx="{_f(x + w * 0.8)}" cy="{_f(base - h * 0.4)}" r="1.5" fill="{GOLD_L}"/>')
    return "".join(out)


def lamp(P, x, base, h, seed):
    out = [P.glow(x, base - h + 6, 50, "#FFD27A", 0.6), P.glow(x, base + 4, 46, "#FFD98A", 0.35, ry=12)]
    out.append(ink(hline(x, base, x, base - h + 12, seed, 0.6), INK_N, 4, seed, 1, 1))
    out.append(f'<path d="M {_f(x - 8)} {base} l 16 0" stroke="{INK_N}" stroke-width="4" stroke-linecap="round"/>')
    lt_ = org_poly([(x - 9, base - h + 18), (x - 11, base - h + 2), (x + 11, base - h + 2), (x + 9, base - h + 18)], seed, 0.4, 6, 1)
    out.append(f'<path d="{lt_}" fill="#FFE9A8" stroke="{INK_N}" stroke-width="2.2"/>')
    out.append(f'<path d="M {_f(x - 13)} {_f(base - h + 3)} L {_f(x)} {_f(base - h - 8)} L {_f(x + 13)} {_f(base - h + 3)} Z" fill="{INK_N}"/>')
    out.append(snow_cap(P, [(x - 13, base - h + 1), (x, base - h - 9), (x + 13, base - h + 1)], 4, seed + 1, drips=False))
    # a sprig of holly on the post
    out.append(f'<path d="{blob(x, base - h * 0.55, 6, 4, seed, 0.1, 8)}" fill="{PINE_L}"/><circle cx="{x + 2}" cy="{_f(base - h * 0.55)}" r="2" fill="{RED}"/>')
    return "".join(out)


def church(P, cx, base, seed):
    out = []
    w, h = 104, 128
    x, top = cx - w / 2, base - h
    nave = org_rect(x, top, w, h, seed, 1.0, 14, 2)
    stone = "#E6D7BC"
    out.append(paint(P, nave, stone, ["#F4E8D2", "#CDBB9C", "#D9C7A8"], (x, top, x + w, base), seed, angle=-88, shade="#3A3560", shade_op=0.5,
                     shade_dir=(0, 0, 1, 0.1), ink_c=INK_N, ink_op=0.65))
    roof = org_poly([(x - 8, top + 2), (cx, top - 46), (x + w + 8, top + 2)], seed + 1, 1, 14, 2)
    out.append(paint(P, roof, "#3E4A6A", ["#506080", "#2E3850"], (x - 8, top - 46, x + w + 8, top), seed + 1, angle=0, n=12, ink_c=INK_N))
    out.append(snow_cap(P, [(x - 10, top + 4), (cx - w * 0.25, top - 21), (cx, top - 45), (cx + w * 0.25, top - 21), (x + w + 10, top + 4)], 9, seed + 2))
    # tower + spire
    tw = 44
    tx, ttop = cx - tw / 2, top - 78
    tower = org_rect(tx, ttop, tw, 82, seed + 3, 0.8, 12, 1.5)
    out.append(paint(P, tower, stone, ["#F4E8D2", "#CDBB9C"], (tx, ttop, tx + tw, top + 4), seed + 3, angle=-88, shade="#3A3560", shade_op=0.45,
                     shade_dir=(0, 0, 1, 0.1), ink_c=INK_N, ink_op=0.65))
    sp = org_poly([(tx - 6, ttop + 2), (cx, ttop - 54), (tx + tw + 6, ttop + 2)], seed + 4, 0.6, 10, 1.5)
    out.append(paint(P, sp, "#3E4A6A", ["#506080", "#2E3850", "#64749A"], (tx - 6, ttop - 54, tx + tw + 6, ttop), seed + 4, angle=-70, n=10, ink_c=INK_N))
    out.append(snow_cap(P, [(tx - 7, ttop + 3), (cx - 10, ttop - 24), (cx - 2, ttop - 40)], 5, seed + 5, drips=False))
    out.append(f'<path d="M {cx} {ttop - 54} l 0 -12 M {cx - 5} {ttop - 61} l 10 0" stroke="{GOLD_L}" stroke-width="2.4" stroke-linecap="round"/>')
    # belfry and round window
    out.append(lit_window(P, cx - 9, ttop + 14, 18, 26, seed + 6, panes=(1, 1), frame=INK_N, arch=True, sill=False, halo=1.6))
    out.append(P.glow(cx, ttop + 60, 24, "#FFC45C", 0.5))
    out.append(f'<circle cx="{cx}" cy="{ttop + 60}" r="9" fill="#FFE29A" stroke="{INK_N}" stroke-width="2"/>'
               f'<path d="M {cx - 9} {ttop + 60} l 18 0 M {cx} {ttop + 51} l 0 18" stroke="{INK_N}" stroke-width="1.6"/>')
    # tall arched windows and the open door
    for wx in (x + 12, x + w - 30):
        out.append(lit_window(P, wx, top + 26, 18, 44, seed + int(wx), panes=(1, 2), frame=INK_N, arch=True, sill=False, halo=1.2))
    dw, dh = 30, 54
    dd = org_poly([(cx - dw / 2, base), (cx - dw / 2, base - dh + dw / 2), (cx, base - dh), (cx + dw / 2, base - dh + dw / 2), (cx + dw / 2, base)], seed + 7, 0.5, 8, 1.5)
    out.append(P.glow(cx, base - 20, 70, "#FFC45C", 0.55))
    g = P.lg([(0, "#FFF0B8"), (1, "#F2A33A")])
    out.append(f'<path d="{dd}" fill="url(#{g})"/>' + ink(dd, INK_N, 2.4, seed, 2, 0.9))
    out.append(f'<path d="M {cx} {base - dh + 2} L {cx} {base}" stroke="{INK_N}" stroke-width="1.6" opacity="0.7"/>')
    # a wreath over the door
    out.append(f'<circle cx="{cx}" cy="{base - dh - 14}" r="9" fill="none" stroke="{PINE}" stroke-width="5"/><circle cx="{cx}" cy="{base - dh - 5}" r="2.6" fill="{RED}"/>')
    # light spilling onto the snow
    out.append(f'<path d="M {cx - dw / 2} {base} L {cx - 40} {base + 60} L {cx + 40} {base + 60} L {cx + dw / 2} {base} Z" fill="#FFD27A" opacity="0.25"/>')
    return "".join(out)


# ---------------------------------------------------------------
def merry_christmas():
    """Living-room tree in lamplight: words on the painted wall above, tree and presents below (no overlap)."""
    P = Pn("merry-christmas")
    o = []
    floor_y = 452
    o.append(sky_wash(P, "#1F4A39", "#1A3F31", [PINE_D, "#2B5E48", "#163828", "#33684F"], 21, box=(0, 0, 600, floor_y + 4), n=240, angle=-88,
                      length=(60, 160), width=(4, 12), op=(0.12, 0.3)))
    # painted wallpaper stripes with tiny gold dots
    for k in range(-1, 13):
        sx = k * 50 + 12
        sd = org_rect(sx, -10, 20, floor_y + 14, 220 + k, 1.6, 30, 1)
        o.append(f'<path d="{sd}" fill="#3C7458" opacity="0.32"/>')
        for j in range(9):
            o.append(f'<circle cx="{sx + 47:.1f}" cy="{j * 52 + (26 if k % 2 else 0) + 14:.1f}" r="2" fill="{GOLD_L}" opacity="0.35"/>')
    o.append(P.glow(300, 340, 260, "#F6C46A", 0.38))
    # wooden floor
    fl = org_poly([(-10, floor_y), (610, floor_y), (610, 610), (-10, 610)], 23, 1, 20, 2)
    o.append(paint(P, fl, WOOD, [WOOD_D, WOOD_L, "#9A6238", "#6E4024"], (-10, floor_y, 610, 610), 23, angle=0, n=300, length=(40, 140), width=(1.5, 4),
                   op=(0.25, 0.6), ink_c=None, shade=WOOD_D, shade_op=0.5, shade_dir=(0, 0, 0, 1)))
    for k in range(1, 6):
        yy = floor_y + k * k * 6 + 6
        o.append(f'<path d="{hline(-10, yy, 610, yy, 24 + k, 1)}" stroke="{WOOD_D}" stroke-width="1.6" fill="none" opacity="0.55"/>')
    o.append(f'<path d="{hline(-10, floor_y, 610, floor_y, 25, 0.8)}" stroke="{INK}" stroke-width="3" fill="none" opacity="0.7"/>')
    # rug
    rug = blob(300, 512, 220, 46, 26, 0.03, 22)
    o.append(paint(P, rug, CRAN, [RED, RED_D, "#B03040"], (80, 466, 520, 558), 26, angle=0, n=110, ink_c=INK, ink_op=0.6))
    o.append(f'<path d="{blob(300, 512, 190, 34, 27, 0.03, 22)}" fill="none" stroke="{GOLD_L}" stroke-width="3" stroke-dasharray="2 7" stroke-linecap="round" opacity="0.8"/>')
    o.append(cast(300, 506, 150, 16, "#2A0E10", 0.5, 28))
    # the tree
    o.append(fir(P, 300, 500, 262, 236, 29, cols=("#173A28", "#2E6247", "#5E9A6E"), tiers=4, ink_c=INK, ink_op=0.6))
    # garland swags (gold beads) + lights + ornaments
    tiers_y = [458, 404, 352, 300]
    rnd = random.Random(30)
    for i, ty in enumerate(tiers_y[:-1]):
        half = 118 * (1 - i * 0.24)
        pts = [(300 - half * 0.85, ty - 8), (300, ty + 6), (300 + half * 0.85, ty - 20)]
        dd = f"M {pts[0][0]:.1f} {pts[0][1]:.1f} Q {pts[1][0]:.1f} {pts[1][1] + 14:.1f} {pts[2][0]:.1f} {pts[2][1]:.1f}"
        o.append(f'<path d="{dd}" stroke="{GOLD_D}" stroke-width="4" fill="none" opacity="0.7" transform="translate(0 2)"/>')
        o.append(f'<path d="{dd}" stroke="{GOLD_L}" stroke-width="3" fill="none" stroke-dasharray="1 5" stroke-linecap="round"/>')
    lights = [(250, 440), (338, 446), (382, 426), (222, 416), (272, 388), (330, 380), (368, 362), (240, 352), (300, 330), (268, 300),
              (326, 306), (300, 270), (204, 450), (392, 456), (352, 410)]
    cols = [GOLD_L, "#FF8A6A", "#9ED6F0", "#FFE9A0", "#F6A0B4"]
    for i, (x, y) in enumerate(lights):
        c = cols[i % len(cols)]
        o.append(P.glow(x, y, 16, c, 0.75) + f'<circle cx="{x}" cy="{y}" r="3.2" fill="{lt(c, 0.5)}"/>')
    orn = [(232, 456, 11, RED), (352, 440, 12, GOLD), (288, 420, 10, "#7FB2D0"), (390, 470, 10, CRAN), (214, 386, 9, GOLD), (342, 392, 10, RED),
           (264, 346, 9, "#7FB2D0"), (318, 344, 8, GOLD), (286, 306, 8, RED), (208, 482, 9, "#E7A3A6")]
    for i, (x, y, r, c) in enumerate(orn):
        o.append(f'<path d="M {x} {y - r} l 0 -4" stroke="{GOLD_D}" stroke-width="1.6"/>' + ball_paint(P, x, y, r, c, 31 + i))
    o.append(star_painted(P, 300, 238, 24, 32))
    # presents (kept below the lettering; the words live on the wall above the tree)
    o.append(gift(P, 168, 470, 70, 50, RED, GOLD_L, 33, pattern="dots", pcol="#F6D4D2"))
    o.append(gift(P, 228, 492, 56, 34, CREAM, RED, 34, pattern="stripes", pcol="#E2685A"))
    o.append(gift(P, 344, 482, 60, 40, "#3F6E8C", CREAM, 35, pattern="stars", pcol="#F6D683"))
    o.append(gift(P, 398, 462, 52, 60, GOLD, RED_D, 36))
    o.append(gift(P, 296, 504, 44, 26, PINE_L, RED, 37, pattern="dots", pcol=CREAM))
    # lettering
    o.append(btext(P, 300, 104, "merry", SERIF_IT, 92, CREAM, ["#FFFFFF", "#F3E2C2", "#E8D4AE"], 38, max_w=360, shadow="#0E2A1E", hi="#FFFFFF"))
    o.append(btext(P, 300, 196, "CHRISTMAS", BEBAS, 104, GOLD, [GOLD_L, GOLD_D, "#F2C35A", "#FFE7A8"], 39, ls=8, max_w=470, shadow="#0E2A1E", hi="#FFF2C8"))
    o.append(twinkle(96, 70, 9, GOLD_L) + twinkle(510, 86, 11, GOLD_L) + twinkle(480, 210, 6, GOLD_L, 0.8) + twinkle(120, 196, 7, GOLD_L, 0.8))
    return finish(P, "".join(o), 40)


# ---------------------------------------------------------------
def believe():
    """A painted snow globe holding a tiny village; 'believe' brushed below in cranberry."""
    P = Pn("believe")
    o = [paper(P.id("paper"), PAPER, "#8A6A4A", 51)]
    o.append(f'<path d="{blob(300, 300, 262, 240, 52, 0.08, 20)}" fill="{ICE_L}" opacity="0.75"/>')
    o.append(strokes(P.id("s"), blob(300, 300, 262, 240, 52, 0.08, 20), (30, 50, 570, 550), [ICE_L, "#C2DAE6", "#E6F0F4", "#FFFFFF"], 53, 200,
                     angle=-20, length=(30, 90), width=(3, 9), opacity=(0.2, 0.45), curve=0.2))
    # painted snowflakes around
    for i, (x, y, r) in enumerate(((92, 120, 16), (508, 108, 13), (522, 330, 18), (78, 330, 12), (120, 230, 8), (486, 228, 9))):
        o.append(snowflake(x, y, r, ICE_D, i))
    cx, cy, R = 300, 222, 146
    # base first (glass sits in it), shadow on paper
    o.append(cast(300, 432, 160, 14, "#3A2418", 0.3, 54))
    base_d = smooth_closed(jitter([(176, 356), (300, 352), (424, 356), (434, 392), (446, 424), (300, 438), (154, 424), (166, 392)], 55, 1.0))
    o.append(paint(P, base_d, CRAN, [RED, RED_D, "#B03040", RED_L], (154, 352, 446, 438), 55, angle=0, n=120, shade=RED_D, shade_op=0.6,
                   shade_dir=(0, 0, 1, 0), light=RED_L, light_op=0.4))
    band = smooth_closed([(166, 386), (300, 392), (434, 386), (438, 404), (300, 410), (162, 404)])
    o.append(paint(P, band, GOLD, [GOLD_L, GOLD_D], (162, 386, 438, 410), 56, angle=0, n=30, ink_c=INK, ink_op=0.6))
    for k in range(7):
        x = 190 + k * 37
        o.append(twinkle(x, 398 + 5 * math.sin(math.pi * (x - 162) / 276), 5, CRAN, 0.9))
    lip = blob(300, 358, 126, 13, 57, 0.02, 18)
    o.append(paint(P, lip, GOLD, [GOLD_L, GOLD_D], (172, 345, 428, 372), 57, angle=0, n=24, ink_c=INK))
    # glass globe: inside painting clipped to the sphere
    gd = blob(cx, cy, R, R, 58, 0.008, 28)
    cid = P.clip(f'<path d="{gd}"/>')
    inner = [sky_wash(P, "#2C3B6E", "#7C93C4", ["#3A4A80", "#5468A0", "#28366A", "#8AA2D0"], 59, box=(cx - R, cy - R, cx + R, cy + R), n=90, length=(30, 90), width=(3, 8))]
    inner.append(f'<circle cx="{cx + 62}" cy="{cy - 78}" r="17" fill="#FFF3D0"/><circle cx="{cx + 62}" cy="{cy - 78}" r="30" fill="#FFF3D0" opacity="0.2"/>')
    inner.append(far_trees(P, cy + 52, 60, "#4C5E8C", 18, (22, 46), x=(cx - R, cx + R)))
    mound = smooth_closed([(cx - R - 10, cy + 62), (cx - 70, cy + 40), (cx + 10, cy + 50), (cx + 90, cy + 36), (cx + R + 10, cy + 58), (cx + R, cy + R + 10), (cx - R, cy + R + 10)])
    inner.append(snow_field(P, mound, (cx - R, cy + 30, cx + R, cy + R), 61, edge_c=None, n=80))
    inner.append(mini_house(P, cx - 110, cy + 74, 56, 44, RED, 62))
    inner.append(mini_house(P, cx + 40, cy + 66, 60, 46, "#4F7F5C", 63))
    inner.append(f'<g transform="translate({cx - 4} {cy + 70}) scale(1.25) translate({-(cx - 4)} {-(cy + 70)})">{mini_church(P, cx - 24, cy + 70, 64)}</g>')
    inner.append(fir(P, cx + 116, cy + 82, 58, 40, 65, snow=True, tiers=3, ink_c=INK_N, trunk=False))
    inner.append(fir(P, cx - 128, cy + 78, 46, 32, 66, snow=True, tiers=3, ink_c=INK_N, trunk=False))
    inner.append(fir(P, cx + 92, cy + 96, 34, 24, 67, snow=True, tiers=3, ink_c=INK_N, trunk=False))
    inner.append(figure(P, cx - 30, cy + 116, 26, RED, 68, scarf=CREAM, hat=CREAM))
    inner.append(figure(P, cx - 12, cy + 114, 20, "#3F6E8C", 168, scarf=RED, hat=RED, flip=-1))
    inner.append(flakes(69, 60, (cx - R, cy - R, cx + R, cy + R), (1.2, 3.2)))
    o.append(f'<g clip-path="url(#{cid})">{"".join(inner)}</g>')
    # glass: rim shading + reflections
    g = P.rg([(0, "#FFFFFF", 0), (0.78, "#FFFFFF", 0), (0.94, ICE_L, 0.45), (1, "#FFFFFF", 0.7)], cx=0.5, cy=0.5, r=0.5)
    o.append(f'<path d="{gd}" fill="url(#{g})"/>')
    o.append(f'<path d="M {cx - 118} {cy - 30} Q {cx - 108} {cy - 102} {cx - 42} {cy - 128}" stroke="#FFFFFF" stroke-width="9" fill="none" stroke-linecap="round" opacity="0.6"/>')
    o.append(f'<path d="M {cx - 126} {cy + 4} Q {cx - 128} {cy - 10} {cx - 125} {cy - 18}" stroke="#FFFFFF" stroke-width="6" fill="none" stroke-linecap="round" opacity="0.5"/>')
    o.append(f'<path d="M {cx + 108} {cy + 70} Q {cx + 126} {cy + 30} {cx + 128} {cy - 6}" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.45"/>')
    o.append(ink(gd, "#3E5A78", 2.6, 70, 2, 0.75))
    o.append(btext(P, 300, 532, "believe", SERIF_IT, 120, CRAN, [RED, RED_D, "#B03040", RED_L], 71, max_w=430, shadow="#E2C9A8", sh=(0.02, 0.03), hi="#F6C0B8"))
    return finish(P, "".join(o), 72)


def snowflake(x, y, r, col, seed, sw=None, op=0.85):
    sw = sw or max(1.6, r * 0.12)
    rnd = random.Random(seed)
    arms = []
    for k in range(6):
        a = math.radians(k * 60 + rnd.uniform(-4, 4))
        ex, ey = x + r * math.cos(a), y + r * math.sin(a)
        arms.append(f'M {x:.1f} {y:.1f} L {ex:.1f} {ey:.1f}')
        for f in (0.55,):
            bx, by = x + r * f * math.cos(a), y + r * f * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.radians(45)
                arms.append(f'M {bx:.1f} {by:.1f} l {r * 0.28 * math.cos(b):.1f} {r * 0.28 * math.sin(b):.1f}')
    return f'<path d="{" ".join(arms)}" stroke="{col}" stroke-width="{sw:.1f}" stroke-linecap="round" fill="none" opacity="{op}"/>'


def mini_house(P, x, base, w, h, col, seed):
    top = base - h
    out = [paint(P, org_rect(x, top, w, h, seed, 0.6, 10, 1.2), col, [lt(col, 0.25), dk(col, 0.2)], (x, top, x + w, base), seed, angle=-88, n=14,
                 shade=dk(col, 0.5), shade_op=0.45, shade_dir=(0, 0, 1, 0.1), ink_c=INK_N, ink_op=0.7)]
    out.append(paint(P, org_poly([(x - 5, top + 2), (x + w / 2, top - h * 0.6), (x + w + 5, top + 2)], seed + 1, 0.6, 10, 1.5), "#4A3A4E", ["#5E4C62", "#3A2C3E"],
                     (x - 5, top - h * 0.6, x + w + 5, top), seed + 1, n=6, ink_c=INK_N, ink_op=0.7))
    out.append(snow_cap(P, [(x - 6, top + 3), (x + w / 2, top - h * 0.6 + 1), (x + w + 6, top + 3)], 5, seed + 2))
    out.append(lit_window(P, x + w * 0.18, top + h * 0.3, w * 0.26, h * 0.32, seed + 3, frame=INK_N, sill=False, halo=1.3))
    out.append(f'<path d="{org_rect(x + w * 0.58, base - h * 0.55, w * 0.24, h * 0.55, seed + 4, 0.4, 6, 1)}" fill="#FFD27A" stroke="{INK_N}" stroke-width="1.6"/>')
    return "".join(out)


def mini_church(P, x, base, seed):
    w, h = 40, 50
    top = base - h
    stone = "#E6D7BC"
    out = [paint(P, org_rect(x, top, w, h, seed, 0.6, 10, 1.2), stone, ["#F4E8D2", "#CDBB9C"], (x, top, x + w, base), seed, angle=-88, n=16,
                 shade="#3A3560", shade_op=0.4, shade_dir=(0, 0, 1, 0.1), ink_c=INK_N, ink_op=0.7)]
    tx = x + w / 2 - 9
    out.append(paint(P, org_rect(tx, top - 30, 18, 32, seed + 1, 0.4, 8, 1), stone, ["#F4E8D2", "#CDBB9C"], (tx, top - 30, tx + 18, top), seed + 1, n=6, ink_c=INK_N, ink_op=0.7))
    out.append(paint(P, org_poly([(tx - 4, top - 28), (tx + 9, top - 66), (tx + 22, top - 28)], seed + 2, 0.4, 8, 1), RED_D, [CRAN, "#4A1018"], (tx - 4, top - 66, tx + 22, top - 28), seed + 2, n=6, ink_c=INK_N))
    out.append(snow_cap(P, [(tx - 5, top - 26), (tx + 4, top - 48)], 3.5, seed + 3, drips=False))
    out.append(paint(P, org_poly([(x - 4, top + 2), (x + w / 2, top - 18), (x + w + 4, top + 2)], seed + 4, 0.5, 8, 1), RED_D, [CRAN], (x - 4, top - 18, x + w + 4, top), seed + 4, n=4, ink_c=INK_N))
    out.append(snow_cap(P, [(x - 5, top + 3), (x + w / 2, top - 17), (x + w + 5, top + 3)], 4.5, seed + 5))
    out.append(lit_window(P, tx + 5, top - 22, 8, 12, seed + 6, panes=(1, 1), frame=INK_N, arch=True, sill=False, halo=1.4))
    out.append(lit_window(P, x + w / 2 - 7, base - 26, 14, 26, seed + 7, panes=(1, 1), frame=INK_N, arch=True, sill=False, halo=1.6))
    return "".join(out)


# ---------------------------------------------------------------
def merry_and_bright():
    """A strand of painted C9 bulbs glowing across a deep green wash; hand-brushed lettering."""
    P = Pn("merry-and-bright")
    o = [sky_wash(P, "#1E4A38", "#12301F", [PINE_D, "#2B5E48", "#163828", "#33684F", "#0E271A"], 81, n=320, angle=-20, length=(60, 170), width=(4, 12),
                  op=(0.12, 0.32))]
    o.append(P.glow(300, 360, 300, "#3F7A5A", 0.5))
    o.append(mottle(82, ["#4F8463", "#0B2015"], 10))
    # painted bokeh dabs
    rnd = random.Random(83)
    for _ in range(26):
        x, y, r = rnd.uniform(20, 580), rnd.uniform(160, 590), rnd.uniform(10, 34)
        c = rnd.choice([GOLD_L, "#FFE9B0", "#F6A0B4", "#9ED6F0", "#FFFFFF"])
        o.append(P.glow(x, y, r * 1.6, c, rnd.uniform(0.12, 0.3)))
    # the wire: two sagging swags
    swags = [((-30, 64), (150, 160), (300, 92)), ((300, 92), (450, 160), (630, 64))]
    pts = []
    for (a, m, b) in swags:
        for k in range(9):
            t = k / 8
            x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * m[0] + t * t * b[0]
            y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * m[1] + t * t * b[1]
            pts.append((x, y))
    o.append(ink(smooth_open(pts), "#0B1F14", 3.6, 84, 2, 0.95))
    o.append(f'<path d="{smooth_open(pts)}" stroke="#4F7A5E" stroke-width="1.2" fill="none" opacity="0.6" transform="translate(0 -1.4)"/>')
    cols = [RED_L, GOLD_L, "#86C8EA", "#F29AB2", "#9BD48A", "#FFB45A"]
    k = 0
    for (a, m, b) in swags:
        for t in (0.2, 0.5, 0.8):
            x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * m[0] + t * t * b[0]
            y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * m[1] + t * t * b[1]
            if not (-10 < x < 610):
                continue
            dx = 2 * (1 - t) * (m[0] - a[0]) + 2 * t * (b[0] - m[0])
            dy = 2 * (1 - t) * (m[1] - a[1]) + 2 * t * (b[1] - m[1])
            rot = math.degrees(math.atan2(dy, dx)) * 0.5 + rnd.uniform(-10, 10)
            o.append(bulb(P, x, y + 2, 24, cols[k % len(cols)], rot, 85 + k, ink_c="#0B1F14"))
            k += 1
    # lettering
    o.append(btext(P, 300, 352, "merry", SERIF_IT, 168, CREAM, ["#FFFFFF", "#F3E2C2", "#E8D4AE", "#FFF6E4"], 86, max_w=420, shadow="#0A1E13", hi="#FFFFFF"))
    o.append(btext(P, 300, 462, "& BRIGHT", BEBAS, 118, GOLD, [GOLD_L, GOLD_D, "#F2C35A", "#FFE7A8"], 87, ls=6, max_w=430, shadow="#0A1E13", hi="#FFF2C8"))
    o.append(ptext(300, 522, "HAPPY HOLIDAYS", MONO, 19, "#F3E2C2", max_w=380, ls=7))
    o.append(flank(516, "HAPPY HOLIDAYS", MONO, 19, 7, GOLD, max_w=380, L=34, seed=88))
    o.append(twinkle(108, 276, 10, GOLD_L) + twinkle(498, 244, 12, GOLD_L) + twinkle(520, 404, 7, GOLD_L, 0.8) + twinkle(84, 420, 7, GOLD_L, 0.8))
    return finish(P, "".join(o), 89)


# ---------------------------------------------------------------
def truck(P, ox, oy, k, seed):
    """Classic round-fendered pickup, side view facing right, painted cherry red; a fresh-cut tree in the bed."""
    o = [f'<g transform="translate({ox} {oy}) scale({k})">']
    o.append(cast(170, 2, 230, 12, "#5A5A9A", 0.45, seed))
    # the tree lying in the bed (drawn first so the bed side hides its lower half)
    o.append(f'<path d="M -54 -104 L 10 -112 L 12 -100 L -52 -94 Z" fill="{WOOD}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>')
    o.append(f'<ellipse cx="-54" cy="-99" rx="4" ry="5.5" fill="{WOOD_L}" stroke="{INK}" stroke-width="1.6"/>')
    o.append(f'<g transform="translate(0 -110) rotate(81)">{fir(P, 0, 0, 236, 104, seed + 1, cols=("#173A28", "#2E6247", "#5E9A6E"), tiers=4, snow=True, trunk=False, ink_op=0.6)}</g>')
    o.append(f'<path d="M 120 -150 Q 126 -120 118 -98" stroke="{RED_D}" stroke-width="3" fill="none"/>')
    red, redd, redl = "#C8352C", "#7E1A1C", "#E86A50"
    # bed side + rear fender
    bed = org_poly([(-4, -106), (176, -106), (176, -42), (-4, -42)], seed + 2, 0.8, 14, 4)
    o.append(paint(P, bed, red, [redl, redd, red, "#D84A3A"], (-4, -106, 176, -42), seed + 2, angle=-4, n=70, shade=redd, shade_op=0.55,
                   shade_dir=(0, 0, 0, 1), light=redl, light_op=0.45, ink_c=INK))
    o.append(f'<path d="{hline(4, -96, 168, -96, seed, 0.5)}" stroke="{redd}" stroke-width="2" fill="none" opacity="0.6"/>')
    rf = smooth_closed([(26, -40), (34, -70), (76, -86), (118, -70), (126, -40)])
    o.append(paint(P, rf, "#A82A26", [red, redd], (26, -86, 126, -40), seed + 3, angle=-30, n=24, shade=redd, shade_op=0.5, ink_c=INK))
    # cab
    cab = org_poly([(172, -40), (172, -138), (186, -166), (244, -168), (258, -150), (270, -112), (270, -40)], seed + 4, 0.7, 12, 9)
    o.append(paint(P, cab, red, [redl, redd, red], (172, -168, 270, -40), seed + 4, angle=-80, n=60, shade=redd, shade_op=0.5,
                   shade_dir=(0, 0, 1, 0.6), light=redl, light_op=0.45, ink_c=INK))
    win = org_poly([(186, -150), (192, -158), (240, -159), (250, -144), (254, -114), (186, -114)], seed + 5, 0.5, 10, 5)
    g = P.lg([(0, "#E7F2F6"), (1, "#9FC2D6")])
    o.append(f'<path d="{win}" fill="url(#{g})"/>' + ink(win, INK, 2.2, seed, 2, 0.85))
    o.append(f'<path d="M 204 -150 L 194 -120 M 220 -152 L 206 -118" stroke="#FFFFFF" stroke-width="4" opacity="0.7" stroke-linecap="round"/>')
    o.append(ink("M 180 -108 L 180 -46 M 180 -108 L 262 -108", INK, 1.6, seed, 1, 0.6))
    o.append(f'<path d="M 238 -96 l 14 0" stroke="#E9E2D2" stroke-width="3.4" stroke-linecap="round"/>')
    # hood + front fender
    hood = org_poly([(266, -114), (332, -110), (360, -98), (370, -72), (368, -40), (266, -40)], seed + 6, 0.7, 12, 10)
    o.append(paint(P, hood, red, [redl, redd, red], (266, -114, 370, -40), seed + 6, angle=-4, n=40, shade=redd, shade_op=0.5,
                   shade_dir=(0, 0, 0, 1), light=redl, light_op=0.45, ink_c=INK))
    ff = smooth_closed([(228, -40), (236, -72), (276, -88), (322, -74), (334, -40)])
    o.append(paint(P, ff, "#A82A26", [red, redd], (228, -88, 334, -40), seed + 7, angle=-30, n=24, shade=redd, shade_op=0.5, ink_c=INK))
    o.append(f'<path d="{hline(122, -40, 232, -40, seed, 0.3)}" stroke="#3A2A2A" stroke-width="7" stroke-linecap="round"/>')
    # chrome bumpers + headlight + wreath on the grille
    o.append(paint(P, org_rect(360, -56, 18, 14, seed + 8, 0.3, 6, 3), "#D9DCE0", ["#FFFFFF", "#9AA0A8"], (360, -56, 378, -42), seed + 8, n=4, ink_c=INK))
    o.append(paint(P, org_rect(-14, -58, 16, 14, seed + 9, 0.3, 6, 3), "#D9DCE0", ["#FFFFFF", "#9AA0A8"], (-14, -58, 2, -44), seed + 9, n=4, ink_c=INK))
    o.append(P.glow(372, -86, 40, "#FFE7A0", 0.6))
    o.append(f'<path d="{blob(360, -86, 9, 10, seed, 0.03, 10)}" fill="#FFF3C8" stroke="{INK}" stroke-width="2"/>')
    o.append(f'<circle cx="352" cy="-62" r="13" fill="none" stroke="{PINE}" stroke-width="7"/><circle cx="352" cy="-62" r="13" fill="none" stroke="{PINE_L}" stroke-width="2" stroke-dasharray="2 4"/>'
             f'<circle cx="345" cy="-71" r="2.4" fill="{RED}"/><circle cx="361" cy="-56" r="2.4" fill="{RED}"/>' + bow_p(P, 352, -49, 10, GOLD, seed + 10))
    # tail light
    o.append(f'<path d="{blob(4, -88, 4, 7, seed, 0.05, 8)}" fill="#FFB060" stroke="{INK}" stroke-width="1.4"/>')
    # wheels
    for wx in (76, 280):
        tire = blob(wx, -34, 34, 34, seed + wx, 0.015, 18)
        o.append(paint(P, tire, "#2E262A", ["#4A4048", "#1A1418"], (wx - 34, -68, wx + 34, 0), seed + wx, angle=-60, n=20, ink_c="#1A1418"))
        o.append(ball_paint(P, wx, -34, 17, "#EFE6D6", seed + wx + 1, ink_c=INK))
        o.append(f'<circle cx="{wx}" cy="-34" r="7" fill="{red}" stroke="{INK}" stroke-width="1.4"/>')
    # snow on the roof, hood and bed rail
    o.append(snow_cap(P, [(184, -166), (214, -171), (246, -168)], 7, seed + 11))
    o.append(snow_cap(P, [(272, -114), (300, -114), (330, -110), (352, -102)], 5, seed + 12))
    o.append(snow_cap(P, [(-4, -106), (60, -107), (120, -106), (174, -106)], 4.5, seed + 13))
    o.append("</g>")
    return "".join(o)


def tis_the_season():
    """Bringing the tree home: a cherry-red pickup with a fresh-cut fir, rolling through a snowy forest."""
    P = Pn("tis-the-season")
    o = [sky_wash(P, "#F6EBDA", "#B9D2E0", ["#EADCC6", "#CFE0E8", "#F8F0E2", "#B6CCDA", "#FFFFFF"], 101, box=(0, 0, 600, 430), n=200, angle=-6)]
    o.append(P.glow(470, 250, 230, "#FFF6E0", 0.6))
    o.append(far_trees(P, 332, 102, "#C3D3DD", 44, (40, 92), op=1, snow=True))
    o.append(far_trees(P, 362, 103, "#98B3C2", 40, (36, 78), snow=True))
    o.append(far_trees(P, 392, 104, "#6E8FA0", 36, (30, 64), snow=True))
    ground = smooth_closed([(-20, 392), (140, 400), (300, 394), (460, 402), (620, 392), (620, 620), (-20, 620)])
    o.append(snow_field(P, ground, (-20, 390, 620, 620), 105, edge_c=None))
    # tracks behind the truck
    for dy in (0, 26):
        o.append(f'<path d="M -20 {470 + dy} Q 60 {482 + dy} 120 {498 + dy}" stroke="{SNOW_SH[1]}" stroke-width="9" fill="none" opacity="0.4" stroke-linecap="round"/>')
    o.append(fir(P, 46, 586, 250, 132, 106, snow=True, tiers=5, ink_c=INK))
    o.append(fir(P, 566, 560, 210, 118, 107, snow=True, tiers=4, ink_c=INK))
    o.append(truck(P, 112, 508, 1.0, 108))
    o.append(holly(P, 104, 560, 26, 10, 109) if False else "")
    o.append(flakes(110, 60, (0, 0, 600, 600), (1.2, 3.2), col="#FFFFFF", avoid=((70, 50, 530, 240),)))
    o.append(btext(P, 300, 104, "'tis the", SERIF_IT, 72, CRAN, [RED, RED_D, "#B03040", RED_L], 111, max_w=330, shadow="#E6D2B8", sh=(0.02, 0.03)))
    o.append(btext(P, 300, 236, "SEASON", BEBAS, 150, PINE, [PINE_L, PINE_D, "#2F6A4C", SAGE], 112, ls=10, max_w=450, shadow="#C9B89C", sh=(0.02, 0.03), hi="#A9CFA8"))
    return finish(P, "".join(o), 113)


# ---------------------------------------------------------------
def stocking(P, x, top, s, col, cuff, kind, accent, seed, flip=False):
    """Knitted stocking hanging from (x, top): fuzzy cuff, heel and toe patches, a knit pattern, painted texture."""
    k = s / 60
    pts = [(0, 26), (60, 26), (62, 112), (96, 120), (110, 140), (98, 156), (40, 158), (8, 146), (-2, 120)]
    if flip:
        pts = [(60 - px, py) for px, py in pts]
    pts = [(x - 30 * k + px * k, top + py * k) for px, py in pts]
    d = smooth_closed(jitter(pts, seed, 0.8))
    bx = bbox(pts)
    o = [f'<path d="{d}" fill="#2A0A10" opacity="0.3" transform="translate(5 5)"/>']
    body = [paint(P, d, col, [lt(col, 0.25), dk(col, 0.2), col], bx, seed, angle=-90, n=60, length=(4, 9), width=(1, 2.2), op=(0.25, 0.55),
                  shade=dk(col, 0.45), shade_op=0.5, shade_dir=(0, 0, 1, 0.3), ink_c=None)]
    if kind == "stripes":
        for j in range(6):
            yy = top + (40 + j * 22) * k
            body.append(f'<path d="{hline(bx[0] - 20, yy, bx[2] + 20, yy - 8 * k, seed + j, 1)}" stroke="{accent}" stroke-width="{9 * k:.1f}" fill="none" opacity="0.92"/>')
    elif kind == "flake":
        body.append(snowflake(x + (6 if not flip else -6) * k, top + 76 * k, 18 * k, accent, seed, sw=3.2 * k, op=0.95))
        for j in range(5):
            body.append(f'<circle cx="{x - 22 * k + j * 11 * k:.1f}" cy="{top + 112 * k:.1f}" r="{2.2 * k:.1f}" fill="{accent}"/>')
            body.append(f'<circle cx="{x - 22 * k + j * 11 * k:.1f}" cy="{top + 44 * k:.1f}" r="{2.2 * k:.1f}" fill="{accent}"/>')
    elif kind == "zigzag":
        for j in range(4):
            yy = top + (46 + j * 26) * k
            zz = " ".join(f"L {bx[0] - 10 + i * 9 * k:.1f} {yy + (5 * k if i % 2 else -5 * k):.1f}" for i in range(int((bx[2] - bx[0] + 20) / (9 * k)) + 2))
            body.append(f'<path d="M {bx[0] - 10:.1f} {yy:.1f} {zz}" stroke="{accent}" stroke-width="{3.6 * k:.1f}" fill="none" stroke-linejoin="round"/>')
    # heel and toe
    hx = bx[2] if not flip else bx[0]
    body.append(f'<path d="{blob(hx - (18 if not flip else -18) * k, top + 146 * k, 22 * k, 18 * k, seed + 3, 0.05, 10)}" fill="{accent}" opacity="0.95"/>')
    body.append(f'<path d="{blob(x + (-30 if not flip else 30) * k, top + 140 * k, 16 * k, 20 * k, seed + 4, 0.05, 10)}" fill="{accent}" opacity="0.95"/>')
    # knit texture: little V stitches
    rnd = random.Random(seed)
    vs = []
    for _ in range(int(70 * k * k)):
        px, py = rnd.uniform(bx[0], bx[2]), rnd.uniform(bx[1] + 26 * k, bx[3])
        vs.append(f"M {px - 2 * k:.1f} {py - 2 * k:.1f} L {px:.1f} {py + 1.5 * k:.1f} L {px + 2 * k:.1f} {py - 2 * k:.1f}")
    body.append(f'<path d="{" ".join(vs)}" stroke="#FFFFFF" stroke-width="{0.9 * k:.1f}" fill="none" opacity="0.28"/>')
    cid = P.clip(f'<path d="{d}"/>')
    o.append(f'<g clip-path="url(#{cid})">{"".join(body)}</g>')
    o.append(ink(d, INK, 2.2, seed, 2, 0.8))
    # fuzzy cuff
    cd = org_rect(x - 36 * k, top, 72 * k, 30 * k, seed + 5, 1.6, 6, 6)
    o.append(paint(P, cd, cuff, ["#FFFFFF", lt(cuff, 0.4), dk(cuff, 0.12)], (x - 36 * k, top, x + 36 * k, top + 30 * k), seed + 5, angle=-90, n=40,
                   length=(3, 7), width=(1.2, 2.6), op=(0.4, 0.8), shade=dk(cuff, 0.3), shade_op=0.4, shade_dir=(0, 0, 0, 1), ink_c=INK, ink_op=0.65))
    o.append(dab_dots(seed + 6, int(26 * k), (x - 34 * k, top + 2, x + 34 * k, top + 28 * k), ["#FFFFFF", dk(cuff, 0.12)], (0.8, 1.8), (0.4, 0.9)))
    return "".join(o)


def flame(P, cx, base, w, h, seed):
    """Painted flame: nested tongues, red outside to pale yellow core."""
    o = [P.glow(cx, base - h * 0.4, max(w, h) * 1.3, "#FFB040", 0.55)]
    rnd = random.Random(seed)
    for col, sc in (("#D8452A", 1.0), ("#F58A2C", 0.78), ("#FFC94A", 0.55), ("#FFF2B0", 0.3)):
        pts = [(cx - w / 2 * sc, base), (cx - w / 2 * sc * 1.05, base - h * 0.3 * sc)]
        for t in range(3):
            pts.append((cx - w / 2 * sc * (0.7 - t * 0.2) + rnd.uniform(-3, 3), base - h * sc * (0.5 + t * 0.15)))
        pts.append((cx + rnd.uniform(-4, 4), base - h * sc))
        for t in range(2, -1, -1):
            pts.append((cx + w / 2 * sc * (0.7 - t * 0.2) + rnd.uniform(-3, 3), base - h * sc * (0.48 + t * 0.15)))
        pts.append((cx + w / 2 * sc * 1.05, base - h * 0.3 * sc))
        pts.append((cx + w / 2 * sc, base))
        o.append(f'<path d="{smooth_closed(pts)}" fill="{col}" opacity="0.95"/>')
    return "".join(o)


def candle(P, x, base, h, w, col, seed):
    d = org_rect(x - w / 2, base - h, w, h, seed, 0.5, 8, 2)
    o = [paint(P, d, col, [lt(col, 0.35), dk(col, 0.15)], (x - w / 2, base - h, x + w / 2, base), seed, angle=-90, n=10,
               shade=dk(col, 0.4), shade_op=0.45, shade_dir=(0, 0, 1, 0), ink_c=INK)]
    o.append(f'<path d="M {x - w / 2 + 3} {base - h + 2} q 2 10 -1 16" stroke="{lt(col, 0.6)}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="M {x} {base - h} l 0 -6" stroke="{INK}" stroke-width="1.6"/>')
    o.append(P.glow(x, base - h - 14, 46, "#FFD27A", 0.6))
    o.append(f'<path d="M {x} {base - h - 4} q -7 -8 0 -22 q 7 14 0 22 Z" fill="#FFB43C"/><path d="M {x} {base - h - 5} q -3 -5 0 -12 q 3 7 0 12 Z" fill="#FFF4C8"/>')
    return "".join(o)


def hung_with_care():
    """Three knitted stockings on a cream mantel, a garland of fir and lights, the fire crackling below."""
    P = Pn("hung-with-care")
    o = [sky_wash(P, "#8E2232", "#6A1624", ["#A02A3A", "#7A1C2A", "#5E1220", "#B03848"], 121, n=260, angle=-88, length=(60, 160), width=(5, 12), op=(0.12, 0.3))]
    rnd = random.Random(122)
    for row in range(11):
        for c in range(9):
            px, py = c * 70 + (35 if row % 2 else 0), row * 56 + 10
            o.append(f'<path d="M {px} {py - 6} l 5 6 l -5 6 l -5 -6 Z" fill="{GOLD_L}" opacity="0.13"/>')
    o.append(P.glow(300, 470, 300, "#FF9A40", 0.4))
    # fireplace: pillars, header, firebox with brick back, fire
    stone, stone_d, stone_l = "#EFE2CA", "#C9B593", "#FFF6E6"
    fb = org_rect(150, 330, 300, 290, 123, 1, 16, 3)
    o.append(paint(P, fb, "#2A1410", ["#3A1C14", "#1A0C08"], (150, 330, 450, 620), 123, angle=-90, n=30, ink_c=None))
    for r in range(8):
        for c in range(7):
            bx_ = 150 + c * 48 - (24 if r % 2 else 0)
            by_ = 336 + r * 26
            o.append(f'<path d="{org_rect(bx_ + 2, by_, 44, 22, 124 + r * 7 + c, 0.6, 12, 3)}" fill="#7A3424" opacity="{0.5 - r * 0.04:.2f}"/>')
    o.append(P.glow(300, 540, 170, "#FFB040", 0.7))
    # logs and fire
    for k, (x1, x2, y) in enumerate(((210, 380, 560), (230, 400, 548))):
        ld = org_rect(x1, y - 14, x2 - x1, 26, 125 + k, 0.8, 12, 10)
        o.append(paint(P, ld, WOOD, [WOOD_L, WOOD_D], (x1, y - 14, x2, y + 12), 125 + k, angle=0, n=20, ink_c=INK))
    o.append(flame(P, 300, 552, 120, 150, 126))
    o.append(flame(P, 250, 556, 60, 80, 127) + flame(P, 350, 556, 64, 90, 128))
    for side in (60, 450):
        pd = org_rect(side, 272, 90, 340, 129 + side, 1, 16, 3)
        o.append(paint(P, pd, stone, [stone_l, stone_d, "#E6D6B8"], (side, 272, side + 90, 612), 129 + side, angle=-90, n=60,
                       shade=stone_d, shade_op=0.5, shade_dir=(0, 0, 1, 0) if side < 300 else (1, 0, 0, 0), ink_c=INK))
        o.append(f'<path d="{org_rect(side + 18, 300, 54, 280, 130 + side, 0.6, 16, 3)}" fill="none" stroke="{stone_d}" stroke-width="2.4" opacity="0.8"/>')
    hd = org_rect(140, 272, 320, 58, 131, 1, 16, 3)
    o.append(paint(P, hd, stone, [stone_l, stone_d], (140, 272, 460, 330), 131, angle=0, n=50, shade=stone_d, shade_op=0.4, shade_dir=(0, 0, 0, 1), ink_c=INK))
    o.append(f'<path d="{org_rect(170, 284, 260, 34, 132, 0.5, 16, 3)}" fill="none" stroke="{stone_d}" stroke-width="2.4" opacity="0.8"/>')
    # shelf
    sh = org_rect(40, 246, 520, 28, 133, 1, 16, 4)
    o.append(paint(P, sh, stone_l, [stone, "#FFFFFF", stone_d], (40, 246, 560, 274), 133, angle=0, n=60, shade=stone_d, shade_op=0.5, shade_dir=(0, 0, 0, 1), ink_c=INK))
    o.append(f'<path d="{hline(44, 276, 556, 276, 134, 0.6)}" stroke="#3A0A10" stroke-width="5" opacity="0.35" fill="none"/>')
    # candles on the shelf
    o.append(candle(P, 92, 248, 36, 20, CREAM, 135) + candle(P, 120, 248, 24, 18, CREAM, 136))
    o.append(candle(P, 508, 248, 36, 20, CREAM, 137) + candle(P, 480, 248, 24, 18, CREAM, 138))
    # garland draped along the shelf edge
    for k in range(7):
        x1 = 132 + k * 50
        o.append(pine_sprig(P, x1, 246 + (k % 2) * 3, x1 + 62, 252 - (k % 2) * 4, 140 + k, needle=12))
    for k in range(6):
        x1 = 150 + k * 60
        o.append(pine_sprig(P, x1 + 30, 250, x1 - 4, 262, 150 + k, needle=10))
    for i, x in enumerate(range(146, 470, 26)):
        c = [GOLD_L, RED_L, "#9ED6F0", "#FFE9A0"][i % 4]
        y = 254 + 4 * math.sin(i * 1.3)
        o.append(P.glow(x, y, 12, c, 0.8) + f'<circle cx="{x}" cy="{y:.1f}" r="2.8" fill="{lt(c, 0.5)}"/>')
    for x in (180, 300, 420):
        o.append(f'<path d="M {x} 268 q -6 6 0 14" stroke="{GOLD_D}" stroke-width="2.6" fill="none"/>')
    o.append(holly(P, 300, 250, 28, 0, 160))
    # stockings
    o.append(stocking(P, 180, 278, 62, "#F4EADB", RED, "stripes", "#C23A30", 161, flip=True))
    o.append(stocking(P, 300, 282, 66, PINE, CREAM, "flake", CREAM, 162))
    o.append(stocking(P, 420, 278, 62, RED, CREAM, "zigzag", CREAM, 163))
    o.append(ptext(300, 90, "THE STOCKINGS WERE", MONO, 19, GOLD_L, max_w=380, ls=6))
    o.append(flank(84, "THE STOCKINGS WERE", MONO, 19, 6, GOLD_L, max_w=380, L=26, seed=164))
    o.append(btext(P, 300, 170, "hung with care", SERIF_IT, 76, CREAM, ["#FFFFFF", "#F3E2C2", "#E8D4AE"], 165, max_w=440, shadow="#3A0A12", hi="#FFFFFF"))
    return finish(P, "".join(o), 166)


# ---------------------------------------------------------------
def cabin(P, cx, base, w, h, seed):
    """Log cabin: stacked painted logs with round ends, a snow-heavy roof, glowing windows, string lights."""
    o = []
    x0, x1 = cx - w / 2, cx + w / 2
    top = base - h
    wall = org_rect(x0, top, w, h, seed, 0.8, 14, 2)
    logs = [paint(P, wall, "#7A4A2C", [WOOD_L, WOOD_D], (x0, top, x1, base), seed, n=0, ink_c=None)]
    nlog = 7
    lh = h / nlog
    for i in range(nlog):
        y = top + i * lh
        ld = org_rect(x0 - 6, y + 1, w + 12, lh - 1, seed + i, 0.6, 20, lh / 2)
        logs.append(paint(P, ld, "#8A5532" if i % 2 else "#7E4C2C", [WOOD_L, WOOD_D, "#A06A40"], (x0 - 6, y, x1 + 6, y + lh), seed + i, angle=0, n=26,
                          length=(20, 60), width=(0.8, 2), shade=WOOD_D, shade_op=0.6, shade_dir=(0, 0, 0, 1), ink_c=INK_N, ink_op=0.5, ink_w=1.2))
    o.append("".join(logs))
    for i in range(nlog):
        y = top + i * lh + lh / 2
        for ex in (x0 - 6, x1 + 6):
            o.append(f'<path d="{blob(ex, y, lh * 0.5, lh * 0.48, seed + i + int(ex), 0.05, 10)}" fill="#C9935E" stroke="{INK_N}" stroke-width="1.4"/>'
                     f'<path d="{blob(ex, y, lh * 0.25, lh * 0.22, seed + i, 0.1, 8)}" fill="none" stroke="#8A5532" stroke-width="1.1"/>')
    # night shading on the right
    g = P.lg([(0, "#1A1A3A", 0), (0.6, "#1A1A3A", 0.1), (1, "#1A1A3A", 0.45)], 0, 0, 1, 0)
    o.append(f'<path d="{wall}" fill="url(#{g})"/>')
    # windows + door
    o.append(lit_window(P, x0 + w * 0.1, top + h * 0.25, w * 0.2, h * 0.38, seed + 20, frame=INK_N, curtain=CRAN, halo=1.4))
    o.append(lit_window(P, x1 - w * 0.3, top + h * 0.25, w * 0.2, h * 0.38, seed + 21, frame=INK_N, curtain=CRAN, halo=1.4))
    dw = w * 0.17
    o.append(door(P, cx - dw / 2, base, dw, h * 0.72, seed + 22, PINE))
    # chimney (stone) behind roof
    chx = cx + w * 0.22
    chd = org_rect(chx, top - h * 0.95, w * 0.1, h * 0.7, seed + 23, 0.6, 8, 1.5)
    o.append(paint(P, chd, "#8E8478", ["#A8A094", "#6E6458"], (chx, top - h * 0.95, chx + w * 0.1, top - h * 0.25), seed + 23, n=10, ink_c=INK_N))
    o.append(snow_cap(P, [(chx - 3, top - h * 0.95), (chx + w * 0.1 + 3, top - h * 0.95)], 5, seed + 24, drips=False))
    # smoke puffs
    rnd = random.Random(seed)
    sx, sy = chx + w * 0.05, top - h * 0.98
    for j in range(7):
        sx += rnd.uniform(-6, 12)
        sy -= 16 + j * 3
        r = 8 + j * 2.6
        o.append(f'<path d="{blob(sx, sy, r, r * 0.8, seed + 40 + j, 0.12, 10)}" fill="#C9C8E4" opacity="{0.42 - j * 0.045:.2f}"/>')
    # roof with thick snow
    rf = org_poly([(x0 - 22, top + 4), (cx, top - h * 0.78), (x1 + 22, top + 4)], seed + 25, 1, 14, 3)
    o.append(paint(P, rf, "#4A3A3A", ["#5E4C4A", "#3A2C2A"], (x0 - 22, top - h * 0.78, x1 + 22, top + 4), seed + 25, n=20, ink_c=INK_N))
    o.append(snow_cap(P, [(x0 - 26, top + 6), (x0 + w * 0.2, top - h * 0.3), (cx, top - h * 0.78 - 1), (x1 - w * 0.2, top - h * 0.3), (x1 + 26, top + 6)], h * 0.17, seed + 26))
    # string of lights along the eaves
    for i in range(13):
        t = i / 12
        lx = x0 - 18 + (w + 36) * t
        ly = top + 10 + 7 * math.sin(math.pi * ((t * 4) % 1))
        c = [RED_L, GOLD_L, "#86C8EA", "#9BD48A"][i % 4]
        o.append(P.glow(lx, ly, 13, c, 0.85) + f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="3" fill="{lt(c, 0.4)}"/>')
    # porch step and lantern
    o.append(paint(P, org_rect(cx - dw * 0.9, base - 4, dw * 1.8, 10, seed + 27, 0.5, 10, 2), "#6E5A4A", ["#8E7A68"], (cx - dw, base - 4, cx + dw, base + 6), seed + 27, n=4, ink_c=INK_N))
    return "".join(o)


def warmest_wishes():
    """A log cabin at night in a snowy clearing: chimney smoke, glowing windows, light pooling on the snow."""
    P = Pn("warmest-wishes")
    o = [sky_wash(P, "#121A36", "#3C4880", ["#1C2448", "#283462", "#34407A", "#101634", "#4A5490"], 141, n=280, mid=(0.6, "#25305C"))]
    o.append(mottle(142, ["#5A64A0", "#0A1028"], 8, (0, 0, 600, 400)))
    rnd = random.Random(143)
    for _ in range(50):
        x, y = rnd.uniform(10, 590), rnd.uniform(10, 300)
        if 60 < x < 540 and 50 < y < 230:
            continue
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.8, 2):.1f}" fill="#FFF3D0" opacity="{rnd.uniform(0.4, 0.95):.2f}"/>')
    o.append(f'<path d="{blob(500, 290, 22, 22, 144, 0.02, 14)}" fill="#FFF0C8"/>' + P.glow(500, 290, 70, "#FFF0C8", 0.35))
    hill = smooth_closed([(-20, 380), (120, 350), (260, 372), (400, 348), (620, 378), (620, 450), (-20, 450)])
    o.append(f'<path d="{hill}" fill="#7C84B8"/>')
    o.append(far_trees(P, 380, 145, "#232C4E", 44, (40, 96), snow=True))
    o.append(far_trees(P, 410, 146, "#1A2240", 30, (50, 110), snow=True, x=(-30, 140)))
    o.append(far_trees(P, 410, 147, "#1A2240", 30, (50, 110), snow=True, x=(460, 630)))
    ground = smooth_closed([(-20, 440), (150, 452), (300, 444), (460, 452), (620, 440), (620, 620), (-20, 620)])
    o.append(snow_field(P, ground, (-20, 436, 620, 620), 148, edge_c=None))
    o.append(P.glow(300, 500, 220, "#FFC86A", 0.35, ry=60))
    o.append(cabin(P, 300, 476, 236, 104, 149))
    for x in (226, 374):
        o.append(f'<path d="M {x - 26} 480 L {x + 26} 480 L {x + 50} 540 L {x - 50} 540 Z" fill="#FFD27A" opacity="0.18"/>')
    # footprints to the door
    for j in range(8):
        fy = 492 + j * 15
        fx = 300 + math.sin(j * 0.8) * 10 + (6 if j % 2 else -6)
        o.append(f'<path d="{blob(fx, fy, 4, 2.6, 150 + j, 0.1, 8)}" fill="{SNOW_SH[1]}" opacity="0.7"/>')
    # firewood pile + sled
    for k in range(3):
        for j in range(3 - k):
            lx, ly = 112 + j * 14 + k * 7, 486 - k * 12
            o.append(f'<path d="{blob(lx, ly, 7, 6.5, 151 + j + k * 3, 0.06, 10)}" fill="#C9935E" stroke="{INK_N}" stroke-width="1.3"/>')
    o.append(snow_cap(P, [(104, 466), (126, 461), (148, 466)], 5, 152, drips=False))
    o.append(sled(P, 476, 506, 153))
    o.append(fir(P, 52, 560, 250, 120, 154, cols=("#0E2418", "#1E3E2E", "#3E6A50"), snow=True, tiers=5, ink_c=INK_N))
    o.append(fir(P, 556, 576, 270, 130, 155, cols=("#0E2418", "#1E3E2E", "#3E6A50"), snow=True, tiers=5, ink_c=INK_N))
    o.append(flakes(156, 70, avoid=((70, 50, 530, 230),)))
    o.append(btext(P, 300, 118, "warmest", SERIF_IT, 96, CREAM, ["#FFFFFF", "#F3E2C2", "#E8D4AE"], 157, max_w=420, shadow="#0A0E24", hi="#FFFFFF"))
    o.append(btext(P, 300, 214, "WISHES", BEBAS, 104, GOLD, [GOLD_L, GOLD_D, "#F2C35A", "#FFE7A8"], 158, ls=16, max_w=420, shadow="#0A0E24", hi="#FFF2C8"))
    return finish(P, "".join(o), 159)


# ---------------------------------------------------------------
def arc_text(P, cx, cy, r, s, font, size, fill, ls=0, top=True, op=1.0):
    pid = P.id("arc")
    if top:
        d = f"M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"
    else:
        d = f"M {cx - r} {cy} A {r} {r} 0 0 0 {cx + r} {cy}"
    P.defs.append(f'<path id="{pid}" d="{d}"/>')
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return f'<text {font} font-size="{size}"{lsa} fill="{fill}" opacity="{op}"><textPath href="#{pid}" startOffset="50%" text-anchor="middle">{esc(s)}</textPath></text>'


def north_pole_post_office():
    """An airmail envelope with a painted North Pole stamp and a smudgy Dec 24 postmark."""
    P = Pn("north-pole-post-office")
    o = [paper(P.id("paper"), "#F3E9D6", "#8A6A4A", 171)]
    # painted airmail border (bleeds off every edge)
    band = 50
    rnd = random.Random(172)
    stripes = []
    for i in range(-2, 34):
        for side in range(4):
            c = RED if i % 2 == 0 else "#2F5C8E"
            t = i * 22
            if side == 0:
                pts = [(t, -4), (t + 14, -4), (t + 14 - band, band), (t - band, band)]
            elif side == 1:
                pts = [(t, 604), (t + 14, 604), (t + 14 + band, 600 - band), (t + band, 600 - band)]
            elif side == 2:
                pts = [(-4, t), (-4, t + 14), (band, t + 14 + band), (band, t + band)]
            else:
                pts = [(604, t), (604, t + 14), (600 - band, t + 14 - band), (600 - band, t - band)]
            stripes.append(f'<path d="{org_poly(pts, 173 + i * 4 + side, 0.8, 12, 1)}" fill="{c}" opacity="{rnd.uniform(0.82, 0.95):.2f}"/>')
    inner = org_rect(band, band, 600 - 2 * band, 600 - 2 * band, 174, 0, 600, 0)
    frame_d = f"M -10 -10 L 610 -10 L 610 610 L -10 610 Z M {band} {band} L {band} {600 - band} L {600 - band} {600 - band} L {600 - band} {band} Z"
    cid = P.clip(f'<path d="{frame_d}" clip-rule="evenodd"/>')
    o.append(f'<g clip-path="url(#{cid})">{"".join(stripes)}</g>')
    o.append(ink(org_rect(band, band, 600 - 2 * band, 600 - 2 * band, 175, 0.8, 30, 2), "#B8A47E", 1.6, 175, 1, 0.6))
    # a scrawled address line hint top-left and the stamp
    sx0, sy0, sw, shh = 138, 92, 324, 412
    o.append(f'<g transform="rotate(-3 300 300)">')
    o.append(f'<rect x="{sx0 + 8}" y="{sy0 + 10}" width="{sw}" height="{shh}" fill="#3A2418" opacity="0.18"/>')
    # perforated stamp edge: scallops
    edge = []
    step = 14
    for x in range(sx0, sx0 + sw + 1, step):
        edge.append(f'<circle cx="{x}" cy="{sy0}" r="5.2"/><circle cx="{x}" cy="{sy0 + shh}" r="5.2"/>')
    for y in range(sy0, sy0 + shh + 1, step):
        edge.append(f'<circle cx="{sx0}" cy="{y}" r="5.2"/><circle cx="{sx0 + sw}" cy="{y}" r="5.2"/>')
    o.append(f'<rect x="{sx0}" y="{sy0}" width="{sw}" height="{shh}" fill="#FBF6EC"/>')
    o.append(strokes(P.id("s"), f"M {sx0} {sy0} h {sw} v {shh} h {-sw} Z", (sx0, sy0, sx0 + sw, sy0 + shh), ["#EFE4D0", "#FFFFFF"], 176, 60, angle=-80, length=(30, 80), width=(3, 8), opacity=(0.3, 0.6)))
    o.append(f'<g fill="#F3E9D6">{"".join(edge)}</g>')
    # painted scene panel
    px0, py0, pw, ph = sx0 + 22, sy0 + 78, sw - 44, shh - 172
    pd = org_rect(px0, py0, pw, ph, 177, 0.5, 30, 1)
    pc = P.clip(f'<path d="{pd}"/>')
    sc = [sky_wash(P, "#1A2448", "#4A6A9C", ["#24305A", "#2E4070", "#3A5684", "#5A7AAA"], 178, box=(px0, py0, px0 + pw, py0 + ph), n=80, length=(30, 80), width=(3, 8))]
    # aurora ribbons
    for j, (c, yy) in enumerate((("#6FD0A8", py0 + 46), ("#8FE0C0", py0 + 62), ("#A890E0", py0 + 34))):
        sc.append(f'<path d="M {px0 - 10} {yy + 20} C {px0 + 70} {yy - 30} {px0 + 150} {yy + 40} {px0 + pw + 10} {yy - 10}" stroke="{c}" stroke-width="{16 - j * 3}" fill="none" opacity="0.28" stroke-linecap="round"/>')
    sc.append(f'<circle cx="{px0 + pw - 56}" cy="{py0 + 52}" r="22" fill="#FFF3D0"/>' + P.glow(px0 + pw - 56, py0 + 52, 60, "#FFF3D0", 0.3))
    # tiny sleigh and reindeer crossing the moon
    sl = px0 + pw - 104
    sy_ = py0 + 50
    deer = "".join(f'<path d="M {sl + 18 + j * 15} {sy_ - 4 - j * 2} l 8 -2 l 2 -5 m -2 5 l 3 3 m -11 -1 l -2 5 m 8 -4 l 2 5" stroke="#1A2040" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
                   f'<ellipse cx="{sl + 22 + j * 15}" cy="{sy_ - 5 - j * 2}" rx="5.5" ry="3" fill="#1A2040"/>' for j in range(3))
    sc.append(f'<path d="M {sl - 14} {sy_ + 2} q 4 -10 14 -8 l 4 6 q -8 8 -20 4 Z" fill="#1A2040"/>' + deer)
    sc.append(f'<path d="M {sl} {sy_ - 2} L {sl + 64} {sy_ - 12}" stroke="#1A2040" stroke-width="1"/>')
    ground = smooth_closed([(px0 - 10, py0 + ph - 70), (px0 + 90, py0 + ph - 84), (px0 + 190, py0 + ph - 72), (px0 + pw + 10, py0 + ph - 86), (px0 + pw + 10, py0 + ph + 10), (px0 - 10, py0 + ph + 10)])
    sc.append(far_trees(P, py0 + ph - 74, 179, "#2A3A60", 14, (24, 44), x=(px0 - 10, px0 + pw + 10), snow=True))
    sc.append(snow_field(P, ground, (px0, py0 + ph - 90, px0 + pw, py0 + ph), 180, edge_c=None, n=60))
    sc.append(mini_house(P, px0 + 120, py0 + ph - 38, 92, 58, RED, 181))
    sc.append(fir(P, px0 + 244, py0 + ph - 26, 66, 44, 182, snow=True, tiers=3, ink_c=INK_N, trunk=False))
    sc.append(fir(P, px0 + 100, py0 + ph - 32, 44, 30, 183, snow=True, tiers=3, ink_c=INK_N, trunk=False))
    # the striped north pole with its sign
    polex = px0 + 56
    pole = org_rect(polex - 6, py0 + 58, 12, ph - 90, 184, 0.3, 20, 1)
    stripes2 = "".join(f'<path d="M {polex - 8} {py0 + 70 + j * 16} l 16 -9 l 0 7 l -16 9 Z" fill="{RED}"/>' for j in range(int((ph - 90) / 16) + 1))
    pc2 = P.clip(f'<path d="{pole}"/>')
    sc.append(f'<path d="{pole}" fill="#FBF6EC"/><g clip-path="url(#{pc2})">{stripes2}</g>' + ink(pole, INK_N, 1.6, 184, 1, 0.8))
    sc.append(f'<path d="{blob(polex, py0 + 56, 9, 9, 185, 0.03, 10)}" fill="{GOLD}" stroke="{INK_N}" stroke-width="1.4"/>')
    sc.append(snow_cap(P, [(polex - 9, py0 + 52), (polex, py0 + 47), (polex + 9, py0 + 52)], 4, 186, drips=False))
    sc.append(cast(polex + 14, py0 + ph - 32, 22, 4, "#5A5A9A", 0.5, 187))
    sc.append(flakes(188, 40, (px0, py0, px0 + pw, py0 + ph), (1, 2.6)))
    o.append(f'<g clip-path="url(#{pc})">{"".join(sc)}</g>')
    o.append(ink(pd, INK, 2.2, 189, 2, 0.8))
    o.append(btext(P, 300, sy0 + 60, "NORTH POLE", CINZEL, 46, CRAN, [RED, RED_D, "#B03040"], 190, ls=2, max_w=sw - 52))
    o.append(btext(P, 300, sy0 + shh - 30, "POST OFFICE", BEBAS, 66, "#2F5C8E", ["#4A7AAE", "#1E3E66", "#6A96C4"], 191, ls=6, max_w=sw - 60))
    o.append(f'<text x="{px0 + pw - 8}" y="{py0 + ph - 10}" text-anchor="end" {BEBAS} font-size="26" fill="{CREAM}">25¢</text>')
    o.append("</g>")
    # postmark (smudgy ink) + wavy cancel lines bleeding off the right edge
    pmx, pmy = 474, 132
    pm_ink = "#26304F"
    o.append(f'<g opacity="0.78">')
    o.append(ink(blob(pmx, pmy, 60, 60, 192, 0.015, 24), pm_ink, 3, 192, 2, 0.9))
    o.append(ink(blob(pmx, pmy, 38, 38, 193, 0.02, 20), pm_ink, 2, 193, 1, 0.8))
    o.append(arc_text(P, pmx, pmy, 47, "NORTH POLE", MONO, 16, pm_ink, ls=2))
    o.append(arc_text(P, pmx, pmy, 47 + 12, "★ ★ ★", MONO, 16, pm_ink, ls=4, top=False))
    o.append(f'<text x="{pmx}" y="{pmy - 4}" text-anchor="middle" {BEBAS} font-size="22" fill="{pm_ink}">DEC</text><text x="{pmx}" y="{pmy + 20}" text-anchor="middle" {BEBAS} font-size="26" fill="{pm_ink}">24</text>')
    o.append("</g>")
    for j in range(4):
        y = 92 + j * 13
        o.append(f'<path d="M 540 {y + 18} q 12 -8 24 0 t 24 0 t 24 0" stroke="{pm_ink}" stroke-width="2.4" fill="none" opacity="0.6"/>')
    return finish(P, "".join(o), 194)


DESIGNS = {
    "peace-on-earth": peace_on_earth,
    "merry-christmas": merry_christmas,
    "believe": believe,
    "merry-and-bright": merry_and_bright,
    "tis-the-season": tis_the_season,
    "hung-with-care": hung_with_care,
    "warmest-wishes": warmest_wishes,
    "north-pole-post-office": north_pole_post_office,
}


def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
