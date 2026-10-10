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
    o.append(sled(P, 476, base + 54, 59))
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


def night_window(P, x, y, w, h, seed, flip=False):
    """A tall window onto a snowy night: cream frame, dark blue panes with falling snow, tied-back cranberry curtain, candle on the sill."""
    out = [cast(x + w / 2, y + h + 8, w * 0.7, 6, "#0A1A12", 0.4, seed)]
    pane = org_rect(x, y, w, h, seed, 0.6, 14, 2)
    sky = [sky_wash(P, "#1A2448", "#4A5A90", ["#24305A", "#2E4070", "#3A5684"], seed, box=(x, y, x + w, y + h), n=24, length=(20, 50), width=(2, 5))]
    sky.append(f'<path d="{smooth_closed([(x - 6, y + h * 0.78), (x + w * 0.4, y + h * 0.7), (x + w + 6, y + h * 0.76), (x + w + 6, y + h + 6), (x - 6, y + h + 6)])}" fill="#C9CBE8"/>')
    sky.append(far_trees(P, y + h * 0.76, seed + 1, "#2A3A60", 6, (18, 34), x=(x - 6, x + w + 6), snow=True))
    sky.append(flakes(seed + 2, 18, (x, y, x + w, y + h), (1, 2.4)))
    cid = P.clip(f'<path d="{pane}"/>')
    out.append(f'<g clip-path="url(#{cid})">{"".join(sky)}</g>')
    fr = "#F2E8D6"
    out.append(ink(f"M {_f(x + w / 2)} {_f(y)} L {_f(x + w / 2)} {_f(y + h)} M {_f(x)} {_f(y + h * 0.5)} L {_f(x + w)} {_f(y + h * 0.5)}", fr, 6, seed, 1, 1))
    out.append(ink(pane, fr, 9, seed, 1, 1) + ink(pane, INK, 2, seed + 1, 1, 0.7))
    out.append(ink(org_rect(x - 5, y - 5, w + 10, h + 10, seed + 3, 0.4, 14, 2), INK, 1.8, seed + 3, 1, 0.6))
    # curtain tied back on the outer side
    sx = x - 4 if not flip else x + w + 4
    sg = 1 if not flip else -1
    cur = smooth_closed([(sx - sg * 10, y - 14), (sx + sg * w * 0.42, y - 14), (sx + sg * w * 0.16, y + h * 0.48), (sx + sg * w * 0.3, y + h + 14), (sx - sg * 10, y + h + 14)])
    out.append(paint(P, cur, CRAN, [RED, RED_D, "#B03040"], bbox([(sx - 10, y - 14), (sx + sg * w * 0.45, y + h + 14), (sx + 10, y)]), seed + 4, angle=-90, n=30,
                     shade=RED_D, shade_op=0.5, shade_dir=(0, 0, 1, 0) if not flip else (1, 0, 0, 0), ink_c=INK))
    out.append(f'<path d="{blob(sx + sg * w * 0.16, y + h * 0.5, 8, 5, seed + 5, 0.1, 8)}" fill="{GOLD}" stroke="{INK}" stroke-width="1.2"/>')
    # rod + sill + candle
    out.append(ink(f"M {_f(x - 18)} {_f(y - 14)} L {_f(x + w + 18)} {_f(y - 14)}", GOLD_D, 4, seed, 1, 1))
    sill = org_rect(x - 12, y + h + 2, w + 24, 10, seed + 6, 0.4, 12, 2)
    out.append(paint(P, sill, fr, ["#FFFFFF", "#D8CCB4"], (x - 12, y + h + 2, x + w + 12, y + h + 12), seed + 6, angle=0, n=6, ink_c=INK))
    out.append(candle(P, x + w / 2, y + h + 2, 26, 12, CREAM, seed + 7))
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
    o.append(night_window(P, 70, 262, 78, 150, 41) + night_window(P, 452, 262, 78, 150, 42, flip=True))
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
    for si, (a, m, b) in enumerate(swags):
        for t in ((0.3, 0.62, 0.9) if si == 0 else (0.1, 0.38, 0.7)):
            x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * m[0] + t * t * b[0]
            y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * m[1] + t * t * b[1]
            if not (-10 < x < 610):
                continue
            dx = 2 * (1 - t) * (m[0] - a[0]) + 2 * t * (b[0] - m[0])
            dy = 2 * (1 - t) * (m[1] - a[1]) + 2 * t * (b[1] - m[1])
            rot = math.degrees(math.atan2(dy, dx)) * 0.5 + rnd.uniform(-10, 10)
            o.append(bulb(P, x, y + 2, 28, cols[k % len(cols)], rot, 85 + k, ink_c="#0B1F14"))
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
    o.append(P.glow(300, 510, 170, "#FFB040", 0.7))
    # logs and fire
    for k, (x1, x2, y) in enumerate(((210, 380, 530), (230, 400, 518))):
        ld = org_rect(x1, y - 14, x2 - x1, 26, 125 + k, 0.8, 12, 10)
        o.append(paint(P, ld, WOOD, [WOOD_L, WOOD_D], (x1, y - 14, x2, y + 12), 125 + k, angle=0, n=20, ink_c=INK))
    o.append(flame(P, 300, 522, 120, 150, 126))
    o.append(flame(P, 250, 526, 60, 80, 127) + flame(P, 350, 526, 64, 90, 128))
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
        lg_ = P.lg([(0, "#FFD27A", 0.32), (1, "#FFD27A", 0)])
        o.append(f'<path d="{smooth_closed([(x - 24, 480), (x + 24, 480), (x + 50, 548), (x - 50, 548)])}" fill="url(#{lg_})"/>')
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
    o.append(btext(P, 300, sy0 + 60, "NORTH POLE", CINZEL, 46, CRAN, [RED, RED_D, "#B03040"], 190, ls=2, max_w=226))
    o.append(btext(P, 300, sy0 + shh - 30, "POST OFFICE", BEBAS, 66, "#2F5C8E", ["#4A7AAE", "#1E3E66", "#6A96C4"], 191, ls=6, max_w=sw - 60))
    o.append(f'<text x="{px0 + pw - 8}" y="{py0 + ph - 10}" text-anchor="end" {BEBAS} font-size="26" fill="{CREAM}">25¢</text>')
    o.append("</g>")
    # postmark (smudgy ink) + wavy cancel lines bleeding off the right edge
    pmx, pmy = 484, 126
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


# ---------------------------------------------------------------
def wreath(P, cx, cy, R, seed, bow=RED, ink_c=INK, berries=True, lights=False):
    """Painted fir wreath: a dark ring wash, hundreds of needle strokes swirling round it, berries, a loopy bow."""
    rnd = random.Random(seed)
    out = [cast(cx + R * 0.08, cy + R * 0.12, R * 1.05, R * 1.05, "#2A1410", 0.22, seed)]
    ring = f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(R)}" fill="none" stroke="{PINE_D}" stroke-width="{_f(R * 0.5)}"/>'
    out.append(ring)
    nd = []
    greens = [PINE_D, PINE, PINE_L, "#2F6A4C", SAGE, "#3E7A58"]
    for i in range(int(R * 9)):
        a = rnd.uniform(0, 2 * math.pi)
        rr = R + rnd.uniform(-R * 0.26, R * 0.26)
        px, py = cx + rr * math.cos(a), cy + rr * math.sin(a)
        t = a + math.pi / 2 + rnd.uniform(-0.9, 0.9)          # needles sweep round the ring
        ln = R * rnd.uniform(0.12, 0.24)
        nd.append(f'<path d="M {_f(px)} {_f(py)} l {_f(math.cos(t) * ln)} {_f(math.sin(t) * ln)}" stroke="{rnd.choice(greens)}" '
                  f'stroke-width="{rnd.uniform(1.2, 2.4):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.7, 1):.2f}"/>')
    out.append("".join(nd))
    # a light dusting of snow on the upper rim
    for i in range(int(R / 4)):
        a = math.radians(rnd.uniform(-160, -20))
        rr = R + rnd.uniform(-R * 0.2, R * 0.3)
        out.append(f'<path d="{blob(cx + rr * math.cos(a), cy + rr * math.sin(a), R * 0.06, R * 0.035, seed + i, 0.2, 8)}" fill="{SNOW}" opacity="0.85"/>')
    if berries:
        for i in range(7):
            a = math.radians(i * 51 + 20)
            for j in range(3):
                bx_ = cx + R * math.cos(a) + rnd.uniform(-R * 0.08, R * 0.08)
                by_ = cy + R * math.sin(a) + rnd.uniform(-R * 0.08, R * 0.08)
                out.append(ball_paint(P, bx_, by_, max(2.4, R * 0.07), RED, seed + 30 + i * 3 + j, ink_c=ink_c))
    if lights:
        for i in range(10):
            a = math.radians(i * 36 + 8)
            lx, ly = cx + R * 1.08 * math.cos(a), cy + R * 1.08 * math.sin(a)
            c = [GOLD_L, "#FFE9A0"][i % 2]
            out.append(P.glow(lx, ly, R * 0.22, c, 0.8) + f'<circle cx="{_f(lx)}" cy="{_f(ly)}" r="{max(1.6, R * 0.04):.1f}" fill="#FFF6D8"/>')
    for sg in (-1, 1):
        tail = smooth_closed([(cx, cy + R), (cx + sg * R * 0.18, cy + R * 1.5), (cx + sg * R * 0.36, cy + R * 1.9), (cx + sg * R * 0.24, cy + R * 1.94), (cx + sg * R * 0.06, cy + R * 1.4)])
        out.append(paint(P, tail, bow, [lt(bow, 0.3), dk(bow, 0.25)], (cx - R * 0.4, cy + R, cx + R * 0.4, cy + R * 2), seed + 60 + sg, angle=70, n=6,
                         ink_c=ink_c, ink_w=max(1, R * 0.03), ink_op=0.7))
    out.append(bow_p(P, cx, cy + R * 1.0, R * 0.62, bow, seed + 50, ink_c))
    return "".join(out)


def snowy_letters(P, s, font, sz, ls, base, seed, thick=10, cap_frac=0.7):
    """Snow resting on the tops of centred capital letters."""
    w = measure(s, font, sz, ls)
    left = 300 - w / 2
    top = base - sz * cap_frac
    out = []
    for i, ch in enumerate(s):
        x = left + (measure(s[:i], font, sz, ls) + ls if i else 0)
        adv = measure(ch, font, sz)
        pts = [(x + adv * 0.06 + j * adv * 0.88 / 5, top + 1.5 + (2.5 if j in (0, 5) else 0)) for j in range(6)]
        out.append(snow_cap(P, pts, thick, seed + i * 5))
    return "".join(out)


def lamppost(P, x, base, head_y, seed):
    """Victorian street lamp: tapered iron post, lantern glowing hot, a light cone full of snow, a wreath tied on."""
    out = []
    out.append(P.glow(x, head_y, 200, "#FFD98A", 0.55) + P.glow(x, head_y, 70, "#FFE9B0", 0.8))
    g = P.lg([(0, "#FFE6A8", 0.45), (1, "#FFE6A8", 0)])
    out.append(f'<path d="M {_f(x - 16)} {_f(head_y + 18)} L {_f(x - 150)} {_f(base + 40)} L {_f(x + 130)} {_f(base + 40)} L {_f(x + 16)} {_f(head_y + 18)} Z" fill="url(#{g})"/>')
    iron, iron_l = "#1E2A30", "#4A5C66"
    post = org_poly([(x - 5, head_y + 40), (x + 5, head_y + 40), (x + 7, base - 40), (x - 7, base - 40)], seed, 0.4, 16, 1)
    out.append(paint(P, post, iron, [iron_l, "#10181C"], (x - 8, head_y + 40, x + 8, base - 40), seed, angle=-90, n=12, ink_c=INK_N, ink_op=0.8))
    ped = smooth_closed([(x - 7, base - 46), (x + 7, base - 46), (x + 10, base - 30), (x + 18, base - 10), (x + 20, base), (x - 20, base), (x - 18, base - 10), (x - 10, base - 30)])
    out.append(paint(P, ped, iron, [iron_l, "#10181C"], (x - 20, base - 46, x + 20, base), seed + 1, angle=-90, n=10, ink_c=INK_N))
    out.append(f'<path d="M {_f(x - 3)} {_f(head_y + 44)} L {_f(x - 4)} {_f(base - 44)}" stroke="#9AB0BC" stroke-width="1.6" opacity="0.6"/>')
    # ladder bar + collar
    out.append(ink(f"M {_f(x - 22)} {_f(head_y + 46)} L {_f(x + 22)} {_f(head_y + 46)}", iron, 3.4, seed, 1, 1))
    for sx in (x - 23, x + 23):
        out.append(f'<circle cx="{_f(sx)}" cy="{_f(head_y + 46)}" r="3.4" fill="{iron}"/>')
    out.append(f'<path d="{org_rect(x - 9, head_y + 24, 18, 18, seed + 2, 0.3, 6, 2)}" fill="{iron}"/>')
    # lantern
    lan = org_poly([(x - 13, head_y + 24), (x - 21, head_y - 22), (x + 21, head_y - 22), (x + 13, head_y + 24)], seed + 3, 0.4, 8, 1.5)
    gg = P.rg([(0, "#FFFBEA"), (0.5, "#FFE39A"), (1, "#F5A940")], cx=0.5, cy=0.55, r=0.7)
    out.append(f'<path d="{lan}" fill="url(#{gg})"/>')
    out.append(P.glow(x, head_y, 34, "#FFFFFF", 0.7))
    out.append(ink(f"M {_f(x)} {_f(head_y - 22)} L {_f(x)} {_f(head_y + 24)}", INK_N, 2, seed, 1, 0.8))
    out.append(ink(lan, INK_N, 3, seed + 3, 2, 0.95))
    cap = org_poly([(x - 30, head_y - 20), (x - 6, head_y - 44), (x + 6, head_y - 44), (x + 30, head_y - 20)], seed + 4, 0.4, 8, 2)
    out.append(paint(P, cap, iron, [iron_l], (x - 30, head_y - 44, x + 30, head_y - 20), seed + 4, angle=0, n=6, ink_c=INK_N))
    out.append(f'<path d="M {_f(x)} {_f(head_y - 44)} l 0 -10" stroke="{iron}" stroke-width="3.6" stroke-linecap="round"/><circle cx="{_f(x)}" cy="{_f(head_y - 57)}" r="4.4" fill="{iron}"/>')
    out.append(snow_cap(P, [(x - 32, head_y - 19), (x - 6, head_y - 44), (x + 6, head_y - 44), (x + 32, head_y - 19)], 7, seed + 5))
    out.append(snow_cap(P, [(x - 26, head_y + 44), (x, head_y + 43), (x + 26, head_y + 44)], 3.6, seed + 6, drips=False))
    return "".join(out)


def bench(P, x0, x1, seat_y, ground, seed):
    """Park bench, front view: painted wooden slats, curly cast-iron ends, snow on seat and backrest."""
    out = []
    iron = "#24262E"
    w = x1 - x0
    # shadow on the snow (lamp on the right -> shadow falls left)
    out.append(cast((x0 + x1) / 2 - 30, ground + 4, w * 0.62, 12, "#5A5A9A", 0.5, seed))
    wood, wood_d, wood_l = "#A4683E", "#6E3E22", "#D09A64"
    # back slats
    for k, yy in enumerate((seat_y - 74, seat_y - 54, seat_y - 34)):
        d = org_rect(x0 - 4, yy, w + 8, 14, seed + k, 0.6, 18, 3)
        out.append(paint(P, d, wood, [wood_l, wood_d, "#B87A48"], (x0 - 4, yy, x1 + 4, yy + 14), seed + k, angle=0, n=40, length=(20, 60),
                         width=(0.8, 2), shade=wood_d, shade_op=0.55, shade_dir=(0, 0, 0, 1), ink_c=INK_N, ink_op=0.7, ink_w=1.6))
    # iron ends: back post, scroll arm, front leg
    for sx, sg in ((x0 + 14, -1), (x1 - 14, 1)):
        d = (f"M {_f(sx)} {_f(seat_y - 86)} L {_f(sx)} {_f(ground)} "
             f"M {_f(sx)} {_f(seat_y - 20)} q {_f(sg * 26)} -4 {_f(sg * 28)} 10 q 0 10 {_f(-sg * 10)} 8 "
             f"M {_f(sx + sg * 10)} {_f(seat_y + 10)} q {_f(sg * 4)} 30 {_f(-sg * 2)} {_f(ground - seat_y - 10)}")
        out.append(ink(d, iron, 6, seed + int(sx), 1, 1))
        out.append(f'<path d="M {_f(sx - 1.5)} {_f(seat_y - 84)} L {_f(sx - 1.5)} {_f(ground - 4)}" stroke="#6A7080" stroke-width="1.4" opacity="0.6"/>')
        out.append(f'<path d="M {_f(sx)} {_f(ground - 34)} c {_f(-sg * 10)} -4 {_f(-sg * 12)} -18 {_f(-sg * 2)} -18 c 6 0 6 8 1 9" stroke="{iron}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    # seat (front edge seen as two slats)
    for k, yy in enumerate((seat_y, seat_y + 12)):
        d = org_rect(x0 - 8, yy, w + 16, 11, seed + 10 + k, 0.5, 18, 3)
        out.append(paint(P, d, wood_d if k else wood, [wood_l, wood_d], (x0 - 8, yy, x1 + 8, yy + 11), seed + 10 + k, angle=0, n=30, length=(20, 60),
                         width=(0.8, 2), shade=dk(wood_d, 0.3), shade_op=0.5, shade_dir=(0, 0, 0, 1), ink_c=INK_N, ink_op=0.7, ink_w=1.6))
    # snow: thick on the seat, a ridge on the backrest top
    out.append(snow_cap(P, [(x0 - 10, seat_y + 2), (x0 + w * 0.2, seat_y - 6), (x0 + w * 0.45, seat_y - 3), (x0 + w * 0.7, seat_y - 8), (x1 + 10, seat_y + 2)], 14, seed + 20))
    out.append(snow_cap(P, [(x0 - 6, seat_y - 72), (x0 + w * 0.3, seat_y - 75), (x0 + w * 0.6, seat_y - 73), (x1 + 6, seat_y - 72)], 9, seed + 21))
    return "".join(out)


def mitten(P, cx, cy, s, rot, col, cuff, seed, pattern=CREAM):
    """Knitted mitten: thumb + hand as one organic form, ribbed cuff, a tiny painted snowflake."""
    k = s / 60
    pts = [(-22, 40), (-26, 0), (-24, -32), (-10, -48), (10, -48), (24, -34), (26, -6), (34, -18), (44, -18), (44, -6), (30, 20), (24, 40)]
    pts = [(cx + px * k, cy + py * k) for px, py in pts]
    d = smooth_closed(jitter(pts, seed, 0.6))
    bx = bbox(pts)
    o = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    o.append(paint(P, d, col, [lt(col, 0.25), dk(col, 0.25), col], bx, seed, angle=-90, n=50, length=(3, 8), width=(0.8, 2), op=(0.25, 0.55),
                   shade=dk(col, 0.45), shade_op=0.5, shade_dir=(0, 0, 1, 0.3), ink_c=INK, ink_w=2))
    o.append(snowflake(cx - 2 * k, cy - 14 * k, 12 * k, pattern, seed, sw=2.2 * k, op=0.95))
    for j in range(5):
        o.append(f'<circle cx="{_f(cx - 18 * k + j * 9 * k)}" cy="{_f(cy + 12 * k)}" r="{_f(1.8 * k)}" fill="{pattern}"/>')
    cd = org_rect(cx - 25 * k, cy + 34 * k, 51 * k, 20 * k, seed + 2, 0.6, 8, 4)
    o.append(paint(P, cd, cuff, ["#FFFFFF", dk(cuff, 0.12)], (cx - 25 * k, cy + 34 * k, cx + 26 * k, cy + 54 * k), seed + 2, angle=-90, n=0, ink_c=INK, ink_w=1.8))
    for j in range(8):
        xx = cx - 21 * k + j * 6 * k
        o.append(f'<path d="M {_f(xx)} {_f(cy + 37 * k)} l 0 {_f(14 * k)}" stroke="{dk(cuff, 0.18)}" stroke-width="{_f(1.6 * k)}" stroke-linecap="round"/>')
    o.append("</g>")
    return "".join(o)


def let_it_snow():
    """Blue-hour park: a snowy bench with a forgotten scarf and mittens, a street lamp pouring warm light into the falling snow."""
    P = Pn("let-it-snow")
    o = [sky_wash(P, "#26326A", "#C7B3D2", ["#2E3A74", "#3E4A86", "#5A64A0", "#7A7EB6", "#9C94C4"], 201, box=(0, 0, 600, 470), n=300,
                  mid=(0.55, "#5A62A2"), angle=-6)]
    o.append(mottle(202, ["#8A8AC4", "#1A2050"], 9, (0, 0, 600, 420)))
    o.append(P.glow(300, 470, 330, "#F2C6C8", 0.35, ry=130))
    # far snowy hills and woods
    o.append(f'<path d="{smooth_closed([(-20, 420), (110, 392), (240, 410), (380, 388), (520, 404), (620, 392), (620, 480), (-20, 480)])}" fill="#A9A4CE"/>')
    o.append(far_trees(P, 414, 203, "#8C88BC", 40, (26, 62), snow=True))
    o.append(far_trees(P, 438, 204, "#6A6AA2", 30, (30, 74), snow=True, x=(-20, 250)))
    o.append(far_trees(P, 440, 205, "#6A6AA2", 14, (30, 64), snow=True, x=(380, 620)))
    ground = smooth_closed([(-20, 446), (140, 456), (300, 450), (460, 458), (620, 448), (620, 620), (-20, 620)])
    o.append(snow_field(P, ground, (-20, 444, 620, 620), 206, edge_c=None))
    # a curving footpath through the snow
    path = smooth_closed([(250, 452), (290, 452), (360, 520), (430, 620), (250, 620), (262, 520)])
    o.append(f'<path d="{path}" fill="{SNOW_SH[0]}" opacity="0.45"/>')
    for j in range(9):
        fy = 470 + j * 16
        fx = 282 + j * j * 0.9 + (7 if j % 2 else -7)
        o.append(f'<path d="{blob(fx, fy, 4.2 + j * 0.25, 2.6 + j * 0.15, 207 + j, 0.1, 8)}" fill="{SNOW_SH[3]}" opacity="0.6"/>')
    # the lamp, then the bench under its light
    o.append(P.glow(462, 532, 170, "#FFD98A", 0.5, ry=40))
    o.append(f'<g transform="translate(470 528) scale(1.15) translate(-470 -528)">{lamppost(P, 470, 528, 372, 208)}</g>')
    o.append(bench(P, 96, 352, 470, 520, 209))
    # scarf draped over the backrest, mittens left on the seat
    sc = smooth_closed([(170, 392), (214, 390), (226, 404), (222, 470), (226, 512), (204, 514), (198, 470), (192, 412), (164, 410), (158, 396)])
    scb = bbox([(158, 388), (228, 516)])
    body = [paint(P, sc, RED, [RED_L, RED_D, "#D24A3A"], scb, 210, angle=-90, n=40, length=(4, 10), width=(1, 2.4), shade=RED_D, shade_op=0.5,
                  shade_dir=(0, 0, 1, 0), ink_c=None)]
    for yy in (430, 448, 466, 484):
        body.append(f'<path d="{hline(150, yy, 240, yy + 2, 211 + yy, 0.6)}" stroke="{CREAM}" stroke-width="5" fill="none" opacity="0.9"/>')
    cid = P.clip(f'<path d="{sc}"/>')
    o.append(f'<g clip-path="url(#{cid})">{"".join(body)}</g>' + ink(sc, INK, 2, 212, 2, 0.8))
    for k in range(7):
        fx = 202 + k * 3.6
        o.append(f'<path d="M {_f(fx)} 512 l {_f(k * 0.4 - 1)} 11" stroke="{RED}" stroke-width="2.4" stroke-linecap="round"/>')
    o.append(snow_cap(P, [(160, 392), (190, 389), (228, 392)], 6, 213, drips=False))
    o.append(mitten(P, 276, 446, 30, -14, PINE, CREAM, 214, pattern=CREAM))
    o.append(mitten(P, 312, 448, 30, 18, PINE_L, CREAM, 215, pattern=CREAM))
    o.append(snow_cap(P, [(256, 430), (276, 426), (296, 430)], 4, 216, drips=False))
    # firs framing the left edge
    o.append(fir(P, 40, 560, 230, 110, 217, cols=("#16324A", "#24485E", "#46708A"), snow=True, tiers=5, ink_c=INK_N, ink_op=0.6))
    # snowfall: brighter inside the lamplight
    o.append(flakes(218, 90, (0, 0, 600, 600), (1.1, 3.0), avoid=((60, 60, 540, 290),)))
    o.append(flakes(219, 40, (360, 300, 590, 560), (1.6, 3.6), col="#FFF6DE", op=(0.8, 1)))
    # lettering
    o.append(btext(P, 300, 112, "let it", SERIF_IT, 92, PINK_L, ["#FFFFFF", PINK, "#F9E2DE", "#E9B8B8"], 220, max_w=300, shadow="#151B44", hi="#FFFFFF"))
    sz = fit_size("SNOW", BEBAS, 190, 430, 24)
    o.append(btext(P, 300, 266, "SNOW", BEBAS, 190, SNOW, ["#FFFFFF", SNOW_SH[2], SNOW_SH[0], ICE_L], 221, ls=24, max_w=430, shadow="#141A44", sh=(0.025, 0.035)))
    o.append(snowy_letters(P, "SNOW", BEBAS, sz, 24, 266, 222, thick=11))
    return finish(P, "".join(o), 223)


# ---------------------------------------------------------------
def garland(P, pts, thick, seed, greens=(PINE_D, PINE, PINE_L, "#2F6A4C", SAGE), berries=0):
    """Fir garland along a polyline: a dark core and dense needle strokes fanning out on both sides."""
    rnd = random.Random(seed)
    core = smooth_open(pts)
    out = [f'<path d="{core}" stroke="{PINE_D}" stroke-width="{_f(thick * 0.9)}" fill="none" stroke-linecap="round" opacity="0.9"/>']
    segs = list(zip(pts, pts[1:]))
    nd = []
    for (a, b) in segs:
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        for _ in range(int(L * 1.6)):
            f = rnd.random()
            px, py = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
            t = ang + rnd.choice((-1, 1)) * math.radians(rnd.uniform(25, 75)) + (math.pi if rnd.random() < 0.3 else 0)
            ln = thick * rnd.uniform(0.6, 1.15)
            nd.append(f'<path d="M {_f(px)} {_f(py)} l {_f(math.cos(t) * ln)} {_f(math.sin(t) * ln)}" stroke="{rnd.choice(greens)}" '
                      f'stroke-width="{rnd.uniform(1.4, 2.6):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.75, 1):.2f}"/>')
    out.append("".join(nd))
    for i in range(berries):
        a, b = rnd.choice(segs)
        f = rnd.random()
        out.append(ball_paint(P, a[0] + (b[0] - a[0]) * f + rnd.uniform(-4, 4), a[1] + (b[1] - a[1]) * f + rnd.uniform(-4, 4), 3.4, RED, seed + 100 + i))
    return "".join(out)


def lantern(P, x, top, s, seed):
    """Wall lantern: iron bracket, glass box glowing, little snow on the cap."""
    out = [P.glow(x, top + s * 0.9, s * 3.4, "#FFD27A", 0.6)]
    iron = "#23272C"
    out.append(ink(f"M {_f(x)} {_f(top - s * 0.4)} q {_f(-s * 0.1)} {_f(-s * 0.2)} 0 {_f(-s * 0.32)}", iron, 3, seed, 1, 1))
    box = org_poly([(x - s * 0.42, top + s * 0.25), (x + s * 0.42, top + s * 0.25), (x + s * 0.34, top + s * 1.55), (x - s * 0.34, top + s * 1.55)], seed, 0.3, 8, 1.5)
    g = P.rg([(0, "#FFFBEA"), (0.5, "#FFE39A"), (1, "#F2A33A")], cx=0.5, cy=0.6, r=0.7)
    out.append(f'<path d="{box}" fill="url(#{g})"/>')
    out.append(P.glow(x, top + s * 0.95, s * 0.6, "#FFFFFF", 0.8))
    out.append(f'<path d="M {_f(x)} {_f(top + s * 1.2)} q -4 -6 0 -14 q 4 8 0 14 Z" fill="#FFB43C"/>')
    out.append(ink(f"M {_f(x)} {_f(top + s * 0.25)} L {_f(x)} {_f(top + s * 1.55)}", iron, 1.8, seed, 1, 0.8))
    out.append(ink(box, iron, 3, seed, 2, 0.95))
    cap = org_poly([(x - s * 0.58, top + s * 0.27), (x, top - s * 0.3), (x + s * 0.58, top + s * 0.27)], seed + 1, 0.3, 8, 2)
    out.append(paint(P, cap, iron, ["#4A5258"], (x - s * 0.6, top - s * 0.3, x + s * 0.6, top + s * 0.3), seed + 1, n=4, ink_c=INK))
    out.append(snow_cap(P, [(x - s * 0.6, top + s * 0.27), (x, top - s * 0.3), (x + s * 0.6, top + s * 0.27)], s * 0.14, seed + 2, drips=False))
    out.append(paint(P, org_rect(x - s * 0.36, top + s * 1.55, s * 0.72, s * 0.16, seed + 3, 0.3, 8, 1), iron, ["#4A5258"], (x - s * 0.4, top + s * 1.5, x + s * 0.4, top + s * 1.75), seed + 3, n=0, ink_c=INK))
    return "".join(out)


def urn_fir(P, cx, base, h, seed):
    """A small potted fir by the door: stone urn, snowy tree wrapped in tiny lights."""
    out = [cast(cx + 6, base + 2, h * 0.32, 7, "#5A5A9A", 0.45, seed)]
    out.append(fir(P, cx, base - h * 0.2, h * 0.86, h * 0.48, seed, cols=(PINE_D, PINE, PINE_L), tiers=4, snow=True, trunk=False, ink_op=0.65))
    rnd = random.Random(seed)
    for i in range(14):
        t = rnd.uniform(0.12, 0.92)
        yy = base - h * 0.2 - h * 0.86 * t
        xx = cx + rnd.uniform(-1, 1) * h * 0.22 * (1 - t)
        c = rnd.choice([GOLD_L, "#FFE9A0", "#FFF6D8"])
        out.append(P.glow(xx, yy, 7, c, 0.9) + f'<circle cx="{_f(xx)}" cy="{_f(yy)}" r="1.8" fill="#FFF8E0"/>')
    urn = smooth_closed([(cx - h * 0.2, base - h * 0.22), (cx + h * 0.2, base - h * 0.22), (cx + h * 0.15, base - h * 0.08), (cx + h * 0.12, base),
                         (cx - h * 0.12, base), (cx - h * 0.15, base - h * 0.08)])
    out.append(paint(P, urn, "#D9CCB4", ["#EFE4D0", "#B8A88E"], (cx - h * 0.2, base - h * 0.22, cx + h * 0.2, base), seed + 1, angle=-90, n=16,
                     shade="#6A5E7A", shade_op=0.5, shade_dir=(0, 0, 1, 0), ink_c=INK))
    out.append(snow_cap(P, [(cx - h * 0.21, base - h * 0.22), (cx, base - h * 0.235), (cx + h * 0.21, base - h * 0.22)], 5, seed + 2, drips=False))
    return "".join(out)


def seasons_greetings():
    """A cranberry front door at dusk: fir wreath, fanlight glowing, lanterns lit, garland and potted firs; words on the snow."""
    P = Pn("seasons-greetings")
    o = [sky_wash(P, "#E9DCC2", "#D4C4A8", ["#F4EBD8", "#DCCFB4", "#E2D6BE", "#CDBE9F"], 231, box=(0, 0, 600, 450), n=160, angle=-2)]
    # clapboard siding: overlapping boards with a shadow line under each
    for k in range(17):
        yy = 6 + k * 27
        o.append(f'<path d="{hline(-10, yy, 610, yy + 1, 232 + k, 0.8)}" stroke="#A8957A" stroke-width="2.4" fill="none" opacity="0.65"/>')
        o.append(f'<path d="{hline(-10, yy + 3, 610, yy + 4, 260 + k, 0.8)}" stroke="#FFF8EA" stroke-width="2" fill="none" opacity="0.6"/>')
    g = P.lg([(0, "#2A2A4A", 0.25), (0.3, "#2A2A4A", 0), (0.7, "#2A2A4A", 0), (1, "#2A2A4A", 0.3)], 0, 0, 1, 0)
    o.append(f'<rect width="600" height="450" fill="url(#{g})"/>')
    o.append(P.glow(300, 280, 260, "#FFC86A", 0.35))
    # snowy ground in front (the steps sit on it)
    ground = smooth_closed([(-20, 434), (150, 438), (300, 444), (450, 438), (620, 432), (620, 620), (-20, 620)])
    o.append(snow_field(P, ground, (-20, 430, 620, 620), 268, edge_c=None))
    o.append('<g transform="translate(300 66) scale(0.94) translate(-300 -66)">')
    # lanterns either side
    o.append(lantern(P, 132, 196, 40, 233) + lantern(P, 468, 196, 40, 234))
    # door surround: pilasters, cornice, fanlight
    stone, stone_d, stone_l = "#F6F0E4", "#C9BBA0", "#FFFFFF"
    for px in (184, 386):
        pd = org_rect(px, 120, 30, 306, 235 + px, 0.8, 16, 2)
        o.append(paint(P, pd, stone, [stone_l, stone_d], (px, 120, px + 30, 426), 235 + px, angle=-90, n=30, shade=stone_d, shade_op=0.5,
                       shade_dir=(0, 0, 1, 0), ink_c=INK, ink_op=0.7))
        o.append(f'<path d="{org_rect(px + 8, 136, 14, 270, 236 + px, 0.4, 16, 2)}" fill="none" stroke="{stone_d}" stroke-width="2" opacity="0.8"/>')
    corn = org_poly([(168, 116), (432, 116), (420, 90), (300, 66), (180, 90)], 237, 0.8, 16, 2)
    o.append(paint(P, corn, stone, [stone_l, stone_d], (168, 66, 432, 118), 237, angle=0, n=30, shade=stone_d, shade_op=0.45, shade_dir=(0, 0, 0, 1), ink_c=INK))
    o.append(f'<path d="{org_poly([(196, 110), (404, 110), (300, 78)], 238, 0.4, 16, 2)}" fill="none" stroke="{stone_d}" stroke-width="2" opacity="0.8"/>')
    # fanlight (half moon of warm glass over the door)
    fan = smooth_closed([(214, 158), (230, 138), (262, 124), (300, 120), (338, 124), (370, 138), (386, 158)])
    gg = P.rg([(0, "#FFF6D8"), (0.6, "#FFD27A"), (1, "#F2A33A")], cx=0.5, cy=1, r=0.9)
    o.append(f'<path d="{fan}" fill="url(#{gg})"/>')
    for a in (30, 60, 90, 120, 150):
        ra = math.radians(a)
        o.append(f'<path d="M 300 158 L {_f(300 - 86 * math.cos(ra))} {_f(158 - 38 * math.sin(ra))}" stroke="{INK}" stroke-width="2" opacity="0.85"/>')
    o.append(ink(fan, INK, 2.6, 239, 2, 0.9))
    # the door
    dd = org_rect(214, 160, 172, 262, 240, 0.8, 18, 2)
    o.append(paint(P, dd, CRAN, [RED, RED_D, "#B03040", RED_L], (214, 160, 386, 422), 240, angle=-88, n=110, shade=RED_D, shade_op=0.55,
                   shade_dir=(0, 0, 1, 0), light=RED_L, light_op=0.3, ink_c=INK))
    for (px, py, pw, ph) in ((230, 296, 60, 108), (310, 296, 60, 108), (230, 176, 60, 30), (310, 176, 60, 30)):
        pd = org_rect(px, py, pw, ph, 241 + px + py, 0.5, 12, 2)
        o.append(f'<path d="{pd}" fill="{RED_D}" opacity="0.35"/>')
        o.append(f'<path d="M {px + 2} {py + ph - 1} L {px + pw - 1} {py + ph - 1} L {px + pw - 1} {py + 2}" stroke="{RED_L}" stroke-width="2" fill="none" opacity="0.6"/>')
        o.append(ink(pd, INK, 1.6, 242 + px, 1, 0.6))
    # brass knob, letter slot, kick plate
    o.append(ball_paint(P, 368, 300, 7, GOLD, 243))
    o.append(paint(P, org_rect(276, 268, 48, 10, 244, 0.3, 8, 2), GOLD, [GOLD_L, GOLD_D], (276, 268, 324, 278), 244, n=4, ink_c=INK))
    o.append(paint(P, org_rect(222, 400, 156, 16, 245, 0.4, 12, 2), GOLD, [GOLD_L, GOLD_D], (222, 400, 378, 416), 245, angle=0, n=12, ink_c=INK))
    # wreath on the door
    o.append(wreath(P, 300, 226, 40, 246, bow=GOLD))
    # garland swagged over the cornice, ends falling down the pilasters, lights tucked in
    gl = [(168, 150), (170, 118), (210, 104), (250, 112), (300, 100), (350, 112), (390, 104), (430, 118), (432, 150)]
    o.append(garland(P, [(166, 196), (162, 170)] + gl + [(438, 170), (434, 196)], 15, 247, berries=10))
    for i, (lx, ly) in enumerate(((166, 186), (168, 140), (196, 108), (232, 110), (272, 104), (328, 104), (368, 110), (404, 108), (432, 140), (434, 186))):
        c = [GOLD_L, "#FFE9A0", RED_L, "#FFF6D8"][i % 4]
        o.append(P.glow(lx, ly, 14, c, 0.9) + f'<circle cx="{lx}" cy="{ly}" r="2.8" fill="#FFF8E0"/>')
    o.append(bow_p(P, 300, 96, 22, RED, 264))
    # steps with snow
    for k, (sx, sw, sy) in enumerate(((176, 248, 422), (156, 288, 440))):
        sd = org_rect(sx, sy, sw, 20, 265 + k, 0.6, 16, 2)
        o.append(paint(P, sd, "#C7C2C8", ["#E2DEE4", "#9E98A6"], (sx, sy, sx + sw, sy + 20), 265 + k, angle=0, n=20, shade="#6A6488", shade_op=0.5,
                       shade_dir=(0, 0, 0, 1), ink_c=INK))
        o.append(snow_cap(P, [(sx - 2, sy + 3), (sx + sw * 0.3, sy + 1), (sx + sw * 0.7, sy + 2), (sx + sw + 2, sy + 3)], 6, 267 + k, drips=True))
    o.append("</g>")
    o.append(P.glow(300, 456, 160, "#FFD27A", 0.3, ry=24))
    # potted firs
    o.append(urn_fir(P, 92, 440, 186, 269) + urn_fir(P, 508, 440, 186, 270))
    o.append(flakes(271, 60, (0, 0, 600, 600), (1.1, 2.8), col="#FFFFFF", avoid=((150, 440, 450, 545),)))
    # lettering on the snow
    o.append(btext(P, 300, 496, "season's", SERIF_IT, 78, CRAN, [RED, RED_D, "#B03040", RED_L], 272, max_w=330, shadow="#B8B4D8", sh=(0.02, 0.03), hi="#F6C0B8",
                   halo=SNOW, halo_w=8))
    o.append(btext(P, 300, 538, "GREETINGS", BEBAS, 50, PINE, [PINE_L, PINE_D, "#2F6A4C", SAGE], 273, ls=14, max_w=340, shadow="#B8B4D8", sh=(0.02, 0.03)))
    return finish(P, "".join(o), 274)


# ---------------------------------------------------------------
def cookie_round(P, cx, cy, r, seed, bite=False):
    """Chocolate-chip cookie: craggy golden disc, toasted edge, chips and a bite."""
    pts = blob_pts(cx, cy, r, r * 0.96, seed, 0.06, 22)
    if bite:
        bx_, by_ = cx + r * 0.72, cy - r * 0.62
        pts2 = []
        for (x, y) in pts:
            dd = math.hypot(x - bx_, y - by_)
            if dd < r * 0.42:
                k = r * 0.42 / max(dd, 0.1)
                x, y = bx_ + (x - bx_) * k * 1.02, by_ + (y - by_) * k * 1.02
            pts2.append((x, y))
        pts = pts2
    d = smooth_closed(pts)
    out = [cast(cx + 5, cy + 7, r * 1.02, r * 0.98, "#6A4A3A", 0.3, seed)]
    out.append(paint(P, d, "#D49A52", ["#E8B672", "#B87A3A", "#F2CC8A", "#A86A30"], (cx - r, cy - r, cx + r, cy + r), seed, angle=-30, n=60, length=(4, 12),
                     width=(1, 3), shade="#8A5226", shade_op=0.55, shade_dir=(0.1, 0.1, 0.9, 0.9), ink_c=INK, ink_w=2))
    rnd = random.Random(seed)
    for _ in range(int(r * 0.22)):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, r * 0.75)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        if bite and math.hypot(x - (cx + r * 0.72), y - (cy - r * 0.62)) < r * 0.55:
            continue
        s = rnd.uniform(r * 0.07, r * 0.12)
        out.append(f'<path d="{blob(x, y, s, s * 0.85, rnd.randint(0, 999), 0.2, 7)}" fill="#4A2A1A"/>'
                   f'<circle cx="{_f(x - s * 0.3)}" cy="{_f(y - s * 0.3)}" r="{_f(s * 0.25)}" fill="#8A5A3A" opacity="0.8"/>')
    out.append(dab_dots(seed + 1, int(r * 0.6), (cx - r * 0.8, cy - r * 0.8, cx + r * 0.8, cy + r * 0.8), ["#FFF0C8", "#8A5226"], (0.6, 1.4), (0.3, 0.6)))
    return "".join(out)


def iced_shape(P, d, box, base, icing, seed, sprinkles=True, ink_c=INK):
    """Sugar cookie: golden biscuit, a slightly smaller iced top, piped dots and sprinkles."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    out = [f'<path d="{d}" fill="#6A4A3A" opacity="0.25" transform="translate(5 7)"/>']
    out.append(paint(P, d, base, ["#F2CC8A", "#C88A48", "#E8B672"], box, seed, angle=-30, n=20, length=(4, 10), width=(1, 2.4), ink_c=ink_c, ink_w=2))
    s = 0.8
    ic = f'<path d="{d}" transform="translate({_f(cx * (1 - s))} {_f(cy * (1 - s) - 2)}) scale({s})" fill="{icing}"/>'
    out.append(ic)
    gid = P.clip(f'<path d="{d}" transform="translate({_f(cx * (1 - s))} {_f(cy * (1 - s) - 2)}) scale({s})"/>')
    rnd = random.Random(seed)
    body = [strokes(P.id("s"), f"M {x0} {y0} H {x1} V {y1} H {x0} Z", box, [lt(icing, 0.5), dk(icing, 0.08), "#FFFFFF"], seed, 30, angle=-40,
                    length=(6, 18), width=(1.5, 3.5), opacity=(0.3, 0.6))]
    g = P.lg([(0, "#FFFFFF", 0.0), (0.6, "#000000", 0), (1, "#3A2418", 0.18)], 0, 0, 1, 1)
    body.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{g})"/>')
    if sprinkles:
        for _ in range(int((x1 - x0) * (y1 - y0) / 200)):
            px, py = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            body.append(f'<rect x="{_f(px)}" y="{_f(py)}" width="6" height="2.4" rx="1.2" fill="{rnd.choice([RED, PINE_L, GOLD, PINK, ICE])}" transform="rotate({rnd.randint(0, 180)} {_f(px)} {_f(py)})"/>')
    out.append(f'<g clip-path="url(#{gid})">{"".join(body)}</g>')
    out.append(f'<path d="{d}" transform="translate({_f(cx * (1 - s))} {_f(cy * (1 - s) - 2)}) scale({s})" fill="none" stroke="{dk(icing, 0.15)}" stroke-width="1.6" opacity="0.6"/>')
    return "".join(out)


def gingerbread_man(P, cx, cy, s, seed, rot=0):
    """Painted gingerbread man: soft dough body, piped icing squiggles, gumdrop buttons, a smile."""
    k = s / 100
    pts = [(0, -62), (16, -58), (22, -44), (18, -30), (52, -26), (60, -14), (52, -4), (24, -4), (26, 18), (42, 50), (36, 62), (20, 60), (0, 30),
           (-20, 60), (-36, 62), (-42, 50), (-26, 18), (-24, -4), (-52, -4), (-60, -14), (-52, -26), (-18, -30), (-22, -44), (-16, -58)]
    pts = [(cx + px * k, cy + py * k) for px, py in pts]
    d = smooth_closed(jitter(pts, seed, 0.6 * k))
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">', f'<path d="{d}" fill="#4A2A1A" opacity="0.25" transform="translate(5 7)"/>']
    out.append(paint(P, d, "#B86E36", ["#D08A4A", "#8E4E22", "#E2A262", "#A0602E"], bbox(pts), seed, angle=-60, n=50, length=(4, 12), width=(1, 3),
                     shade="#6A3414", shade_op=0.5, shade_dir=(0.2, 0.1, 0.9, 1), ink_c=INK, ink_w=2.2))
    out.append(dab_dots(seed + 1, int(40 * k), bbox(pts), ["#6A3414", "#F0B47A"], (0.6, 1.4), (0.3, 0.6)))
    icing = "#FFFBF2"
    sq = lambda x1, y1, x2, y2: f'<path d="M {_f(cx + x1 * k)} {_f(cy + y1 * k)} q {_f((x2 - x1) * k / 4)} {_f(-5 * k)} {_f((x2 - x1) * k / 2)} 0 t {_f((x2 - x1) * k / 2)} 0" stroke="{icing}" stroke-width="{_f(3.2 * k)}" fill="none" stroke-linecap="round"/>'
    out.append(sq(-50, -16, -30, -16) + sq(30, -16, 50, -16) + sq(-34, 50, -20, 50) + sq(20, 50, 34, 50))
    out.append(f'<circle cx="{_f(cx - 7 * k)}" cy="{_f(cy - 48 * k)}" r="{_f(3.4 * k)}" fill="{INK}"/><circle cx="{_f(cx + 7 * k)}" cy="{_f(cy - 48 * k)}" r="{_f(3.4 * k)}" fill="{INK}"/>')
    out.append(f'<path d="M {_f(cx - 9 * k)} {_f(cy - 39 * k)} q {_f(9 * k)} {_f(8 * k)} {_f(18 * k)} 0" stroke="{icing}" stroke-width="{_f(3 * k)}" fill="none" stroke-linecap="round"/>')
    out.append(f'<circle cx="{_f(cx - 13 * k)}" cy="{_f(cy - 41 * k)}" r="{_f(3.4 * k)}" fill="{PINK}" opacity="0.7"/><circle cx="{_f(cx + 13 * k)}" cy="{_f(cy - 41 * k)}" r="{_f(3.4 * k)}" fill="{PINK}" opacity="0.7"/>')
    for j, c in enumerate((RED, PINE_L, RED)):
        out.append(ball_paint(P, cx, cy + (-14 + j * 13) * k, 4.6 * k, c, seed + 10 + j, ink_c=INK))
    out.append("</g>")
    return "".join(out)


def gingham(P, seed, a="#FBF4E6", b=RED, step=50):
    """Hand-painted gingham tablecloth: brushy bands both ways, darker where they cross."""
    out = [f'<rect width="600" height="600" fill="{a}"/>']
    rnd = random.Random(seed)
    for i in range(-1, 13):
        x = i * step + 10
        d = org_rect(x, -20, step / 2, 640, seed + i, 1.6, 30, 1)
        out.append(f'<path d="{d}" fill="{b}" opacity="0.42"/>')
        d2 = org_rect(-20, x, 640, step / 2, seed + 40 + i, 1.6, 30, 1)
        out.append(f'<path d="{d2}" fill="{b}" opacity="0.42"/>')
    out.append(strokes(P.id("s"), "M -20 -20 H 620 V 620 H -20 Z", (-40, -20, 640, 620), [b, a, dk(b, 0.2), "#FFFFFF"], seed, 260, angle=-2,
                       length=(30, 90), width=(2, 6), opacity=(0.06, 0.18)))
    return "".join(out)


def cookies_for_santa():
    """Christmas Eve plate seen from above on a red gingham cloth: iced cookies, a bitten chocolate chip, a note for Santa."""
    P = Pn("cookies-for-santa")
    o = [gingham(P, 281)]
    o.append(P.glow(300, 300, 360, "#FFF6E0", 0.25))
    # plate
    o.append(cast(312, 316, 244, 240, "#3A1410", 0.35, 282))
    rim = blob(300, 300, 238, 236, 283, 0.006, 40)
    o.append(paint(P, rim, "#FBF8F2", ["#FFFFFF", "#ECE6DC", "#F4EFE6"], (62, 62, 538, 538), 283, angle=-30, n=90, length=(20, 60), width=(2, 6),
                   op=(0.2, 0.45), shade="#B8B0C8", shade_op=0.5, shade_dir=(0.1, 0.1, 0.9, 0.9), ink_c=INK, ink_w=2.4))
    well = blob(300, 300, 168, 166, 284, 0.006, 36)
    g = P.rg([(0, "#FFFFFF"), (0.8, "#F6F1EA"), (1, "#DDD4C8")], cx=0.55, cy=0.58, r=0.55)
    o.append(f'<path d="{well}" fill="url(#{g})"/>')
    o.append(ink(well, "#B8AE9E", 1.8, 285, 1, 0.7))
    o.append(ink(blob(300, 300, 226, 224, 286, 0.004, 40), GOLD, 2.4, 286, 1, 0.9))
    o.append(ink(blob(300, 300, 178, 176, 287, 0.004, 40), GOLD, 1.8, 287, 1, 0.8))
    # holly on the rim at 9 and 3 o'clock
    o.append(holly(P, 92, 300, 30, 90, 288) + holly(P, 508, 300, 30, -90, 289))
    # rim lettering
    o.append(arc_text(P, 300, 300, 194, "COOKIES FOR SANTA", BEBAS, 50, CRAN, ls=7))
    o.append(arc_text(P, 300, 300, 212, "★  CHRISTMAS EVE  ★", MONO, 19, PINE, ls=5, top=False))
    # cookies
    star = org_poly(star_pts(226, 250, 68, 34, 5, -80), 290, 0.8, 14, 6)
    o.append(iced_shape(P, star, (158, 182, 294, 318), "#E2A862", "#FBF6EC", 290))
    o.append(cookie_round(P, 382, 234, 62, 291, bite=True))
    tree = org_poly([(300, 324), (346, 404), (326, 404), (338, 426), (262, 426), (274, 404), (254, 404)], 292, 0.8, 12, 4)
    o.append(iced_shape(P, tree, (254, 324, 346, 426), "#E2A862", "#7FB08A", 292))
    o.append(f'<path d="M 278 380 q 22 10 44 -4 M 270 410 q 30 10 62 -4" stroke="#FFFBF2" stroke-width="3" fill="none" stroke-linecap="round"/>')
    o.append(star_painted(P, 300, 330, 11, 293, glow=False))
    o.append(gingerbread_man(P, 410, 376, 106, 294, rot=-22))
    # folded note
    note = org_poly([(150, 352), (236, 336), (246, 388), (160, 404)], 295, 0.6, 12, 2)
    o.append(f'<path d="{note}" fill="#3A2418" opacity="0.18" transform="translate(4 6)"/>')
    o.append(paint(P, note, "#FFFDF6", ["#F2ECE0", "#FFFFFF"], (150, 336, 246, 404), 295, angle=-10, n=12, ink_c=INK, ink_w=1.8))
    o.append(f'<path d="M 155 378 L 241 362" stroke="#D8D0C2" stroke-width="1.4"/>')
    o.append(f'<text x="198" y="374" text-anchor="middle" {SERIF_IT} font-size="20" fill="{CRAN}" transform="rotate(-10 198 374)">for Santa</text>')
    o.append(f'<path d="M 218 390 c -4 -6 4 -10 6 -4 c 2 -6 10 -2 6 4 l -6 6 Z" fill="{RED}" transform="rotate(-10 222 390)"/>')
    # crumbs
    o.append(dab_dots(296, 26, (210, 280, 400, 330), ["#C88A48", "#8A5226", "#E8B672"], (1, 2.6), (0.6, 0.95)))
    return finish(P, "".join(o), 297)


# ---------------------------------------------------------------
def candy_cane(P, x, base, h, seed, rot=0, w=None, ink_c=INK):
    """Hooked candy cane: cream stick, red stripes wrapping it (clipped), a dry-brush shine."""
    w = w or max(8, h * 0.075)
    r = h * 0.17
    path = [(x, base), (x, base - h + r)] + [(x + r + r * math.cos(math.radians(180 - a)), base - h + r - r * math.sin(math.radians(180 - a))) for a in range(15, 181, 15)] + [(x + 2 * r, base - h + r + r * 0.45)]
    d = smooth_open(path)
    cid = P.clip(f'<path d="{d}" fill="none" stroke="#000" stroke-width="{_f(w)}" stroke-linecap="round"/>')
    stripes = "".join(f'<path d="M {_f(x - 40)} {_f(base - k * w * 1.6)} l {_f(80 + 2 * r)} {_f(-50)}" stroke="{RED}" stroke-width="{_f(w * 0.55)}"/>' for k in range(-4, int(h / (w * 1.6)) + 8))
    out = [f'<g transform="rotate({rot} {_f(x)} {_f(base)})">']
    out.append(f'<path d="{d}" fill="none" stroke="#3A2418" stroke-width="{_f(w + 3)}" stroke-linecap="round" opacity="0.8"/>')
    out.append(f'<path d="{d}" fill="none" stroke="#FFF8EE" stroke-width="{_f(w)}" stroke-linecap="round"/>')
    out.append(f'<g clip-path="url(#{cid})">{stripes}<path d="{d}" fill="none" stroke="#7A1018" stroke-width="{_f(w)}" stroke-linecap="round" opacity="0.18" transform="translate({_f(w * 0.3)} 0)"/></g>')
    out.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{_f(w * 0.18)}" stroke-linecap="round" opacity="0.7" transform="translate({_f(-w * 0.22)} 0)"/>')
    out.append("</g>")
    return "".join(out)


def mug_scene_marshmallow(P, x, y, s, seed, rot=0):
    d = org_rect(x - s / 2, y - s * 0.4, s, s * 0.8, seed, s * 0.03, s, s * 0.25)
    return (f'<g transform="rotate({rot} {_f(x)} {_f(y)})">'
            + paint(P, d, "#FFFBF4", ["#FFFFFF", "#F2E6DA", "#F8D8D0"], (x - s / 2, y - s * 0.4, x + s / 2, y + s * 0.4), seed, angle=-80, n=5,
                    shade="#D8B8B0", shade_op=0.6, shade_dir=(0, 0, 1, 1), ink_c=INK, ink_w=1.4, ink_op=0.6)
            + "</g>")


def hot_cocoa_season():
    """A Fair-Isle mug piled with cream and marshmallows on a tartan runner; mittens, cinnamon and steam."""
    P = Pn("hot-cocoa-season")
    o = [sky_wash(P, "#F6EBDA", "#EBD6BE", ["#FBF3E6", "#EEDCC4", "#F2E2CE", "#E6CDB2"], 301, box=(0, 0, 600, 420), n=200, angle=-88,
                  length=(60, 160), width=(4, 10))]
    # wallpaper: painted sprigs in a soft lattice
    rnd = random.Random(302)
    for row in range(8):
        for c in range(7):
            px, py = c * 96 + (48 if row % 2 else 0) - 10, row * 58 + 20
            o.append(f'<path d="M {px} {py + 8} q 2 -10 0 -18 M {px} {py - 2} l -6 -6 M {px} {py - 2} l 6 -6" stroke="{SAGE}" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.4"/>'
                     f'<circle cx="{px}" cy="{py - 12}" r="2.4" fill="{RED_L}" opacity="0.45"/>')
    o.append(P.glow(290, 360, 260, "#FFE2B0", 0.6))
    # table + tartan runner
    table = org_poly([(-10, 420), (610, 420), (610, 610), (-10, 610)], 303, 1, 30, 2)
    o.append(paint(P, table, WOOD, [WOOD_D, WOOD_L, "#9A6238"], (-10, 420, 610, 610), 303, angle=0, n=160, length=(40, 140), width=(1.5, 4), op=(0.25, 0.55), ink_c=None))
    run = org_poly([(-10, 436), (610, 436), (610, 610), (-10, 610)], 304, 1.2, 30, 2)
    tart = [f'<path d="{run}" fill="{CRAN}"/>']
    for k in range(-1, 14):
        x = k * 48
        tart.append(f'<path d="{org_rect(x, 420, 22, 200, 305 + k, 1, 30, 1)}" fill="{PINE}" opacity="0.55"/>')
        tart.append(f'<path d="M {x + 34} 420 L {x + 34} 620" stroke="{GOLD_L}" stroke-width="2" opacity="0.6"/>')
    for k in range(5):
        y = 446 + k * 40
        tart.append(f'<path d="{org_rect(-10, y, 620, 18, 320 + k, 1, 30, 1)}" fill="{PINE}" opacity="0.5"/>')
        tart.append(f'<path d="{hline(-10, y + 28, 610, y + 28, 330 + k, 0.6)}" stroke="{GOLD_L}" stroke-width="2" fill="none" opacity="0.6"/>')
    tart.append(strokes(P.id("s"), run, (-10, 436, 610, 610), [RED_D, RED_L, PINE_D], 306, 140, angle=0, length=(30, 80), width=(1.5, 4), opacity=(0.1, 0.25)))
    tart.append(f'<rect x="-10" y="436" width="620" height="180" fill="url(#{P.lg([(0, "#1A0A10", 0.0), (1, "#1A0A10", 0.35)])})"/>')
    cid = P.clip(f'<path d="{run}"/>')
    o.append(f'<g clip-path="url(#{cid})">{"".join(tart)}</g>')
    o.append(ink(hline(-10, 437, 610, 437, 307, 0.8), INK, 2.4, 307, 1, 0.6))
    for k in range(40):
        fx = k * 16 - 6
        o.append(f'<path d="M {fx} 436 l {rnd.uniform(-2, 2):.1f} -7" stroke="{CRAN}" stroke-width="2.4" stroke-linecap="round" opacity="0.9"/>')
    # cinnamon sticks + spilled marshmallows (left)
    for k, (x1, y1, x2, y2) in enumerate(((84, 520, 196, 488), (92, 536, 204, 508))):
        dd = smooth_closed([(x1, y1 - 7), (x2, y2 - 7), (x2 + 4, y2), (x2, y2 + 7), (x1, y1 + 7), (x1 - 4, y1)])
        o.append(cast((x1 + x2) / 2 + 4, (y1 + y2) / 2 + 10, 60, 6, "#2A0A10", 0.3, 308 + k))
        o.append(paint(P, dd, "#9A5A2E", ["#C07A44", "#6E3A1A"], (x1 - 4, min(y1, y2) - 8, x2 + 4, max(y1, y2) + 8), 308 + k, angle=-15, n=14, ink_c=INK, ink_w=1.6))
        o.append(f'<path d="{blob(x2, y2, 4, 7, 309 + k, 0.1, 8)}" fill="#C07A44" stroke="{INK}" stroke-width="1.2"/>')
    o.append(mug_scene_marshmallow(P, 166, 548, 26, 310, 20) + mug_scene_marshmallow(P, 196, 560, 22, 311, -10) + mug_scene_marshmallow(P, 132, 566, 22, 312, 40))
    # mittens (right)
    o.append(cast(470, 540, 80, 10, "#2A0A10", 0.35, 313))
    o.append(mitten(P, 438, 494, 54, -30, RED, CREAM, 314))
    o.append(mitten(P, 494, 506, 54, 24, RED_D, CREAM, 315))
    # the mug
    cx, top, bot, rx = 290, 326, 530, 96
    o.append(cast(cx + 14, bot + 4, rx * 1.15, 16, "#2A0A10", 0.45, 316))
    body = smooth_closed([(cx - rx, top), (cx - rx + 4, top + 100), (cx - rx + 12, bot - 20), (cx - rx + 40, bot), (cx, bot + 6), (cx + rx - 40, bot), (cx + rx - 12, bot - 20),
                          (cx + rx - 4, top + 100), (cx + rx, top), (cx, top + 16)])
    # handle behind body edge
    hd = smooth_closed([(cx + rx - 6, top + 40), (cx + rx + 50, top + 36), (cx + rx + 66, top + 96), (cx + rx + 40, top + 150), (cx + rx - 6, top + 160),
                        (cx + rx - 6, top + 136), (cx + rx + 30, top + 128), (cx + rx + 42, top + 96), (cx + rx + 34, top + 62), (cx + rx - 6, top + 64)])
    o.append(paint(P, hd, "#F7EEDD", ["#FFFFFF", "#E2D4BC"], (cx + rx - 6, top + 36, cx + rx + 66, top + 160), 317, angle=-70, n=14, shade="#B8A488", shade_op=0.55,
                   shade_dir=(0, 0, 1, 0), ink_c=INK))
    mb = [paint(P, body, "#F7EEDD", ["#FFFFFF", "#EADFCB", "#F2E8D6"], (cx - rx, top, cx + rx, bot), 318, angle=-90, n=70, ink_c=None)]
    # Fair Isle band
    by0, by1 = top + 70, top + 142
    mb.append(f'<path d="{org_rect(cx - rx - 10, by0, 2 * rx + 20, by1 - by0, 319, 0.8, 20, 1)}" fill="{RED}"/>')
    mb.append(strokes(P.id("s"), f"M {cx - rx} {by0} H {cx + rx} V {by1} H {cx - rx} Z", (cx - rx, by0, cx + rx, by1), [RED_L, RED_D, "#D24A3A"], 320, 50, angle=0,
                      length=(10, 30), width=(1, 3), opacity=(0.25, 0.5)))
    for k in range(-3, 4):
        tx = cx + k * 30
        mb.append(f'<path d="M {tx} {by0 + 20} l -10 18 l 7 0 l -9 14 l 24 0 l -9 -14 l 7 0 Z" fill="{CREAM}" opacity="0.95"/>' if k % 2 == 0 else
                  f'<path d="M {tx} {by0 + 24} c -4 -7 -14 -2 -8 6 l 8 8 l 8 -8 c 6 -8 -4 -13 -8 -6 Z" fill="{CREAM}" opacity="0.95"/>')
    for k in range(-8, 9):
        mb.append(f'<rect x="{cx + k * 12 - 3}" y="{by0 + 5}" width="6" height="6" fill="{CREAM}" transform="rotate(45 {cx + k * 12} {by0 + 8})"/>')
        mb.append(f'<rect x="{cx + k * 12 + 3}" y="{by1 - 11}" width="6" height="6" fill="{CREAM}" transform="rotate(45 {cx + k * 12 + 6} {by1 - 8})"/>')
    mb.append(f'<path d="{hline(cx - rx, by0 - 6, cx + rx, by0 - 6, 321, 0.5)}" stroke="{PINE}" stroke-width="4" fill="none"/>')
    mb.append(f'<path d="{hline(cx - rx, by1 + 6, cx + rx, by1 + 6, 322, 0.5)}" stroke="{PINE}" stroke-width="4" fill="none"/>')
    g = P.lg([(0, "#FFFFFF", 0.35), (0.3, "#FFFFFF", 0), (0.62, "#5A3A2A", 0), (1, "#5A3A2A", 0.42)], 0, 0, 1, 0)
    mb.append(f'<rect x="{cx - rx}" y="{top}" width="{2 * rx}" height="{bot - top + 10}" fill="url(#{g})"/>')
    mb.append(f'<path d="M {cx - rx + 22} {top + 30} q -6 90 4 170" stroke="#FFFFFF" stroke-width="7" fill="none" stroke-linecap="round" opacity="0.55"/>')
    mcid = P.clip(f'<path d="{body}"/>')
    o.append(f'<g clip-path="url(#{mcid})">{"".join(mb)}</g>')
    o.append(ink(body, INK, 2.6, 323, 2, 0.85))
    # rim + cocoa
    rim = blob(cx, top, rx, 20, 324, 0.01, 24)
    o.append(paint(P, rim, "#F7EEDD", ["#FFFFFF"], (cx - rx, top - 20, cx + rx, top + 20), 324, n=0, ink_c=INK, ink_w=2.4))
    o.append(f'<path d="{blob(cx, top + 2, rx - 9, 13, 325, 0.02, 20)}" fill="#5A2E1A"/>')
    # whipped cream: stacked swirls
    cream_c = "#FFFBF2"
    for k, (dx, dy, rw, rh) in enumerate(((-56, -6, 46, 24), (52, -6, 46, 24), (0, -10, 70, 30), (-26, -36, 44, 24), (28, -36, 44, 24), (0, -60, 36, 22), (6, -80, 16, 14))):
        dd = blob(cx + dx, top + dy, rw, rh, 326 + k, 0.08, 14)
        o.append(paint(P, dd, cream_c, ["#FFFFFF", "#EDE0D2", "#F6EAE0"], (cx + dx - rw, top + dy - rh, cx + dx + rw, top + dy + rh), 326 + k, angle=-20, n=8,
                       shade="#C8B4C8", shade_op=0.5, shade_dir=(0, 0, 0.6, 1), ink_c="#9A7A6A", ink_w=1.4, ink_op=0.55))
    o.append(dab_dots(333, 30, (cx - 60, top - 80, cx + 60, top - 10), ["#6A3A1E", "#8A5226"], (0.8, 1.8), (0.5, 0.9)))
    for k, (mx, my, ms, mr) in enumerate(((-58, -22, 26, -14), (58, -24, 26, 18), (-20, -52, 24, 8), (34, -54, 22, -22), (-74, 2, 22, 30))):
        o.append(mug_scene_marshmallow(P, cx + mx, top + my, ms, 334 + k, mr))
    o.append(candy_cane(P, cx + 50, top - 14, 100, 340, rot=30, w=12))
    # steam
    for k, (sx, amp) in enumerate(((206, 1), (226, -1), (402, 1))):
        o.append(f'<path d="M {sx} {top - 30 - k % 2 * 8} c {-14 * amp} -12 {12 * amp} -24 {-2 * amp} -38" stroke="#FFFFFF" stroke-width="{6 - k % 2 * 2}" fill="none" stroke-linecap="round" opacity="0.6"/>')
    # holly sprig on the table
    o.append(holly(P, 378, 556, 26, -20, 341))
    o.append(btext(P, 300, 122, "hot cocoa", SERIF_IT, 100, CRAN, [RED, RED_D, "#B03040", RED_L], 342, max_w=470, shadow="#E2C9A8", sh=(0.02, 0.03), hi="#F6C0B8"))
    o.append(btext(P, 300, 214, "SEASON", BEBAS, 92, PINE, [PINE_L, PINE_D, "#2F6A4C", SAGE], 343, ls=16, max_w=400, shadow="#E2C9A8", sh=(0.02, 0.03), hi="#A9CFA8"))
    o.append(twinkle(118, 186, 9, GOLD) + twinkle(484, 186, 9, GOLD) + twinkle(98, 96, 6, GOLD, 0.8) + twinkle(504, 92, 6, GOLD, 0.8))
    return finish(P, "".join(o), 344)


# ---------------------------------------------------------------
def tropical_leaf(P, x0, y0, x1, y1, wid, seed, col=PINE, bend=0.18, ink_c=INK):
    """Banana / heliconia-type leaf: a curved midrib, blade swelling to a soft point, side veins, wind tears."""
    rnd = random.Random(seed)
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    mx, my = (x0 + x1) / 2 + nx * L * bend, (y0 + y1) / 2 + ny * L * bend
    def mid(t):
        return ((1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * y1)
    def tang(t):
        dx = 2 * (1 - t) * (mx - x0) + 2 * t * (x1 - mx)
        dy = 2 * (1 - t) * (my - y0) + 2 * t * (y1 - my)
        l = math.hypot(dx, dy)
        return dx / l, dy / l
    left, right = [], []
    N = 16
    for i in range(N + 1):
        t = i / N
        px, py = mid(t)
        tx_, ty_ = tang(t)
        w = wid * (math.sin(math.pi * min(1, t * 1.08)) ** 0.7) * (1 if t < 0.97 else 0.3)
        left.append((px - ty_ * w * rnd.uniform(0.94, 1.04), py + tx_ * w * rnd.uniform(0.94, 1.04)))
        right.append((px + ty_ * w * rnd.uniform(0.94, 1.04), py - tx_ * w * rnd.uniform(0.94, 1.04)))
    d = smooth_closed(left + list(reversed(right)))
    bx = bbox(left + right)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    out = [paint(P, d, col, [lt(col, 0.25), dk(col, 0.3), lt(col, 0.45), col], bx, seed, angle=ang + 70, n=int(L * 0.9), length=(wid * 0.4, wid * 1.0),
                 width=(1, 3), op=(0.2, 0.5), shade=dk(col, 0.45), shade_op=0.4, shade_dir=(0, 0, 1, 1), ink_c=ink_c, ink_w=1.8, ink_op=0.7)]
    veins = []
    for i in range(2, N - 1):
        t = i / N
        px, py = mid(t)
        for side in (left[i], right[i]):
            veins.append(f"M {_f(px)} {_f(py)} Q {_f((px + side[0]) / 2 + ux * 6)} {_f((py + side[1]) / 2 + uy * 6)} {_f(side[0] + ux * 10)} {_f(side[1] + uy * 10)}")
    cid = P.clip(f'<path d="{d}"/>')
    out.append(f'<g clip-path="url(#{cid})"><path d="{" ".join(veins)}" stroke="{dk(col, 0.35)}" stroke-width="1.3" fill="none" opacity="0.55"/></g>')
    pts = [mid(i / 20) for i in range(21)]
    out.append(f'<path d="{smooth_open(pts)}" stroke="{lt(col, 0.55)}" stroke-width="{max(2, wid * 0.08):.1f}" fill="none" stroke-linecap="round" opacity="0.85"/>')
    return "".join(out)


def hibiscus(P, cx, cy, r, seed, col="#E2485A", rot=0):
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    for k in range(5):
        a = math.radians(k * 72 - 90)
        px, py = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55
        d = blob(px, py, r * 0.55, r * 0.46, seed + k, 0.1, 12, rot=k * 72 - 90)
        out.append(paint(P, d, col, [lt(col, 0.3), dk(col, 0.2), PINK], (px - r * 0.6, py - r * 0.6, px + r * 0.6, py + r * 0.6), seed + k, angle=k * 72 - 90, n=10,
                         ink_c=INK, ink_w=1.4, ink_op=0.6))
    out.append(P.glow(cx, cy, r * 0.5, "#7A0A20", 0.6))
    out.append(f'<path d="M {_f(cx)} {_f(cy)} q {_f(r * 0.3)} {_f(-r * 0.3)} {_f(r * 0.7)} {_f(-r * 0.6)}" stroke="{GOLD_L}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    out.append(dab_dots(seed, 7, (cx + r * 0.5, cy - r * 0.75, cx + r * 0.8, cy - r * 0.5), [GOLD_L, "#FFE9A0"], (1.2, 2.2), (0.9, 1)))
    out.append("</g>")
    return out and "".join(out)


def toucan(P, ox, oy, seed):
    """Toco toucan in a Santa hat, facing left. (ox, oy) is where its feet grip the branch."""
    o = []
    X = lambda x: ox + x
    Y = lambda y: oy + y
    blk, blk_l = "#1E1C26", "#3C3C5C"
    # tail (hangs behind the branch)
    tail = smooth_closed([(X(4), Y(-24)), (X(30), Y(-20)), (X(42), Y(30)), (X(40), Y(54)), (X(26), Y(58)), (X(16), Y(24))])
    o.append(paint(P, tail, blk, [blk_l, "#2A2A3A", "#4A4A6A"], (X(4), Y(-24), X(44), Y(58)), seed, angle=80, n=24, ink_c=INK_N, ink_w=1.8))
    # body
    body = smooth_closed([(X(-50), Y(-122)), (X(-20), Y(-142)), (X(22), Y(-130)), (X(40), Y(-90)), (X(42), Y(-40)), (X(24), Y(-6)), (X(-6), Y(0)), (X(-30), Y(-20)), (X(-46), Y(-64))])
    o.append(paint(P, body, blk, [blk_l, "#2A2A3A", "#46466A", "#14121A"], (X(-50), Y(-142), X(42), Y(0)), seed + 1, angle=70, n=70, length=(8, 22), width=(1, 3),
                   shade="#000000", shade_op=0.35, shade_dir=(0, 0, 1, 0.4), ink_c=INK_N, ink_w=2))
    # wing with feather strokes
    wing = smooth_closed([(X(-6), Y(-110)), (X(26), Y(-104)), (X(38), Y(-60)), (X(32), Y(-16)), (X(14), Y(-10)), (X(0), Y(-50))])
    o.append(paint(P, wing, "#14121A", ["#2E2E46", "#3C3C5C"], (X(-6), Y(-110), X(38), Y(-10)), seed + 2, angle=80, n=20, ink_c=INK_N, ink_w=1.6))
    for k in range(4):
        o.append(f'<path d="M {_f(X(6 + k * 6))} {_f(Y(-70 + k * 12))} q 8 18 4 34" stroke="#5A5A80" stroke-width="1.6" fill="none" opacity="0.7"/>')
    # red under-tail patch
    o.append(f'<path d="{blob(X(14), Y(-10), 14, 9, seed + 3, 0.1, 10, rot=-20)}" fill="{RED}"/>')
    # white-cream throat with a yellow wash and a red lower border
    th = smooth_closed([(X(-48), Y(-126)), (X(-30), Y(-132)), (X(-14), Y(-118)), (X(-12), Y(-88)), (X(-24), Y(-66)), (X(-42), Y(-70)), (X(-52), Y(-96))])
    o.append(paint(P, th, "#FFF6E2", ["#FFFFFF", "#FFE7A8", "#F6D88A"], (X(-52), Y(-132), X(-12), Y(-66)), seed + 4, angle=-80, n=16, light="#FFFFFF", light_op=0.5,
                   ink_c=INK_N, ink_w=1.6, ink_op=0.6))
    o.append(f'<path d="M {_f(X(-44))} {_f(Y(-70))} q 10 6 22 2" stroke="{RED}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    # head
    head = blob(X(-22), Y(-148), 30, 28, seed + 5, 0.04, 14)
    o.append(paint(P, head, blk, [blk_l, "#2A2A3A"], (X(-52), Y(-176), X(8), Y(-120)), seed + 5, angle=60, n=16, ink_c=INK_N, ink_w=1.8))
    # bill
    bill = smooth_closed([(X(-36), Y(-170)), (X(-80), Y(-176)), (X(-126), Y(-166)), (X(-160), Y(-146)), (X(-172), Y(-128)), (X(-160), Y(-124)),
                          (X(-120), Y(-128)), (X(-78), Y(-130)), (X(-40), Y(-132))])
    bb = (X(-172), Y(-178), X(-36), Y(-122))
    g = P.lg([(0, "#F7C04A"), (0.55, "#F59A2C"), (1, "#E2621E")], 1, 0, 0, 0.2)
    o.append(f'<path d="{bill}" fill="url(#{g})"/>')
    o.append(strokes(P.id("s"), bill, bb, ["#FFD670", "#E2621E", "#FFE9A0", "#D8501A"], seed + 6, 40, angle=-8, length=(14, 40), width=(1, 3), opacity=(0.25, 0.5)))
    o.append(f'<path d="M {_f(X(-140))} {_f(Y(-162))} Q {_f(X(-168))} {_f(Y(-140))} {_f(X(-172))} {_f(Y(-128))} Q {_f(X(-160))} {_f(Y(-126))} {_f(X(-150))} {_f(Y(-132))} Z" fill="#1E1C26" opacity="0.9"/>')
    o.append(f'<path d="M {_f(X(-40))} {_f(Y(-148))} Q {_f(X(-100))} {_f(Y(-150))} {_f(X(-162))} {_f(Y(-134))}" stroke="#A8461A" stroke-width="2" fill="none" opacity="0.8"/>')
    o.append(f'<path d="M {_f(X(-50))} {_f(Y(-168))} Q {_f(X(-100))} {_f(Y(-172))} {_f(X(-138))} {_f(Y(-158))}" stroke="#FFF2C4" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.7"/>')
    o.append(ink(bill, INK, 2.2, seed + 6, 2, 0.85))
    # eye: blue skin, orange ring, dark pupil, glint
    o.append(f'<path d="{blob(X(-22), Y(-150), 12, 11, seed + 7, 0.05, 10)}" fill="#5FB0D8"/>')
    o.append(f'<circle cx="{_f(X(-22))}" cy="{_f(Y(-150))}" r="6.5" fill="#F59A2C"/><circle cx="{_f(X(-22))}" cy="{_f(Y(-150))}" r="4.4" fill="#14121A"/>'
             f'<circle cx="{_f(X(-24))}" cy="{_f(Y(-152))}" r="1.6" fill="#FFFFFF"/>')
    # Santa hat
    hat = smooth_closed([(X(-50), Y(-166)), (X(-30), Y(-200)), (X(4), Y(-214)), (X(40), Y(-206)), (X(60), Y(-186)), (X(66), Y(-160)), (X(52), Y(-164)),
                         (X(38), Y(-184)), (X(10), Y(-176))])
    o.append(paint(P, hat, RED, [RED_L, RED_D, "#D24A3A"], (X(-50), Y(-214), X(66), Y(-160)), seed + 8, angle=20, n=30, shade=RED_D, shade_op=0.5, ink_c=INK))
    o.append(ball_paint(P, X(66), Y(-156), 9, SNOW, seed + 9, tints=["#FFFFFF", SNOW_SH[0]], ink_c="#8A8AB0"))
    fur = smooth_closed([(X(-54), Y(-160)), (X(-38), Y(-176)), (X(-6), Y(-184)), (X(18), Y(-178)), (X(20), Y(-164)), (X(-10), Y(-166)), (X(-40), Y(-154))])
    o.append(paint(P, fur, SNOW, ["#FFFFFF", SNOW_SH[0], SNOW_SH[2]], (X(-54), Y(-184), X(20), Y(-154)), seed + 10, angle=-90, n=20, length=(3, 6), width=(1, 2),
                   shade=SNOW_SH[1], shade_op=0.5, shade_dir=(0, 0, 0, 1), ink_c="#8A8AB0", ink_w=1.4))
    # feet gripping the branch
    for fx in (-14, 8):
        o.append(f'<path d="M {_f(X(fx))} {_f(Y(-8))} q -4 8 -10 10 M {_f(X(fx))} {_f(Y(-8))} q 2 9 -2 13 M {_f(X(fx))} {_f(Y(-8))} q 8 6 6 13" stroke="#6A8AB0" stroke-width="4" fill="none" stroke-linecap="round"/>')
    return "".join(o)


def feliz_natal():
    """Brazilian Christmas: a toco toucan in a Santa hat on a branch strung with lights, banana leaves, hibiscus, warm summer light."""
    P = Pn("feliz-natal")
    o = [sky_wash(P, "#FBEBD2", "#F4CDB0", ["#FDF3E2", "#F6DCC2", "#F2C8A8", "#FFF6E8"], 401, n=240, angle=-14, length=(60, 160), width=(5, 12))]
    o.append(P.glow(430, 170, 280, "#FFF2C8", 0.7))
    o.append(mottle(402, ["#F2B898", "#FFFFFF"], 8))
    # banana leaves from the top corners
    o.append(tropical_leaf(P, -30, 40, 230, 120, 52, 403, col="#2E6B4E", bend=-0.12))
    o.append(tropical_leaf(P, -20, -10, 150, 230, 40, 404, col=PINE, bend=0.15))
    o.append(tropical_leaf(P, 640, 30, 380, 92, 54, 405, col="#2E6B4E", bend=0.14))
    o.append(tropical_leaf(P, 630, 120, 470, 270, 44, 406, col=PINE_L, bend=-0.16))
    o.append(tropical_leaf(P, 600, -20, 520, 160, 30, 407, col=PINE, bend=0.1))
    # baubles hanging from the leaves
    for k, (bx_, by_, top_, r, c) in enumerate(((62, 238, 104, 13, GOLD), (132, 252, 196, 11, RED), (508, 232, 150, 14, RED), (440, 160, 98, 11, GOLD))):
        o.append(f'<path d="M {bx_} {top_} L {bx_} {by_ - r - 3}" stroke="{GOLD_D}" stroke-width="1.6"/>'
                 f'<path d="{org_rect(bx_ - 4, by_ - r - 5, 8, 6, 408 + k, 0.2, 4, 1)}" fill="{GOLD_L}" stroke="{INK}" stroke-width="1"/>' + ball_paint(P, bx_, by_, r, c, 410 + k))
    # branch
    br = [(-30, 340), (90, 330), (210, 318), (330, 306), (450, 290), (630, 272)]
    brd = smooth_open(br)
    o.append(f'<path d="{brd}" stroke="#5A3A24" stroke-width="18" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="{brd}" stroke="#8A5E3A" stroke-width="8" fill="none" stroke-linecap="round" transform="translate(0 -4)" opacity="0.8"/>')
    o.append(f'<path d="{brd}" stroke="#C49A6A" stroke-width="2" fill="none" stroke-linecap="round" transform="translate(0 -7)" opacity="0.6"/>')
    o.append(ink(smooth_open([(x, y + 9) for x, y in br]), INK, 1.8, 420, 1, 0.6))
    o.append(f'<path d="M 470 288 q 30 -26 66 -30" stroke="#5A3A24" stroke-width="8" fill="none" stroke-linecap="round"/>')
    o.append(tropical_leaf(P, 526, 260, 580, 216, 12, 421, col=PINE_L, bend=0.2))
    # string lights wrapped round the branch
    def ybr(x):
        for (a, b) in zip(br, br[1:]):
            if a[0] <= x <= b[0]:
                t = (x - a[0]) / (b[0] - a[0])
                return a[1] + (b[1] - a[1]) * t
        return br[-1][1]
    wire = smooth_open([(x, ybr(x) + 10 * math.sin(x / 26)) for x in range(-30, 640, 13)])
    o.append(f'<path d="{wire}" stroke="#1E3A2A" stroke-width="2" fill="none"/>')
    cols = [GOLD_L, RED_L, "#86C8EA", "#F29AB2", "#9BD48A"]
    for i, x in enumerate(range(-10, 620, 44)):
        if 250 < x < 340:
            continue
        y = ybr(x) + 10 * math.sin(x / 26) + 6
        c = cols[i % len(cols)]
        o.append(P.glow(x, y, 15, c, 0.9) + f'<path d="{blob(x, y, 3.4, 5, 422 + i, 0.05, 8)}" fill="{lt(c, 0.45)}" stroke="{INK}" stroke-width="0.8"/>')
    # hibiscus on the branch
    o.append(tropical_leaf(P, 100, 334, 50, 288, 14, 423, col=PINE, bend=0.2) + tropical_leaf(P, 104, 334, 160, 284, 13, 424, col=PINE_L, bend=-0.2))
    o.append(hibiscus(P, 104, 314, 36, 425, rot=-10))
    # toucan
    o.append(cast(306, 322, 40, 6, "#3A2418", 0.25, 426))
    o.append(f'<g transform="translate(306 308) scale(1.12) translate(-306 -308)">{toucan(P, 306, 308, 427)}</g>')
    # sparkles
    o.append(twinkle(370, 128, 10, GOLD) + twinkle(250, 98, 7, GOLD, 0.8) + twinkle(490, 360, 8, GOLD, 0.9) + twinkle(84, 400, 8, GOLD, 0.9) + twinkle(530, 410, 6, GOLD, 0.8))
    o.append(btext(P, 300, 466, "feliz", SERIF_IT, 96, PINE, [PINE_L, PINE_D, "#2F6A4C", SAGE], 428, max_w=300, shadow="#E8BFA0", sh=(0.02, 0.03), hi="#A9CFA8"))
    o.append(btext(P, 300, 538, "NATAL", BEBAS, 104, CRAN, [RED, RED_D, "#B03040", RED_L], 429, ls=18, max_w=380, shadow="#E8BFA0", sh=(0.02, 0.03), hi="#F6C0B8"))
    return finish(P, "".join(o), 430)


# ---------------------------------------------------------------
def bauble(P, cx, cy, r, col, style, seed, cap_rot=0, cap_c=GOLD):
    """Glass bauble lying in a box: painted sphere, a decoration style, metal cap with a wire loop."""
    out = [cast(cx + r * 0.18, cy + r * 0.22, r * 1.02, r * 0.98, "#6A3A3A", 0.3, seed)]
    a = math.radians(cap_rot - 90)
    capx, capy = cx + math.cos(a) * r * 0.98, cy + math.sin(a) * r * 0.98
    out.append(f'<g transform="rotate({cap_rot} {_f(capx)} {_f(capy)})">'
               f'<path d="M {_f(capx - 3)} {_f(capy - 8)} q 3 -9 6 0" stroke="{dk(cap_c, 0.2)}" stroke-width="1.8" fill="none"/>'
               + paint(P, org_rect(capx - r * 0.2, capy - r * 0.13, r * 0.4, r * 0.2, seed + 1, 0.3, 6, 1.5), cap_c, [lt(cap_c, 0.4), dk(cap_c, 0.3)],
                       (capx - r * 0.2, capy - r * 0.13, capx + r * 0.2, capy + r * 0.07), seed + 1, angle=-90, n=4, ink_c=INK, ink_w=1.4)
               + "</g>")
    d = blob(cx, cy, r, r, seed, 0.015, 18)
    out.append(ball_paint(P, cx, cy, r, col, seed, hi=False, ink_c=None))
    deco = []
    if style == "band":
        deco.append(f'<path d="{org_rect(cx - r - 4, cy - r * 0.22, 2 * r + 8, r * 0.44, seed + 2, 0.6, 12, 1)}" fill="{GOLD}"/>')
        for k in range(-2, 3):
            deco.append(twinkle(cx + k * r * 0.36, cy, r * 0.12, RED_D if col != RED_D else CREAM, 0.95))
        deco.append(f'<path d="{hline(cx - r, cy - r * 0.3, cx + r, cy - r * 0.3, seed, 0.4)}" stroke="{CREAM}" stroke-width="2" fill="none"/>'
                    f'<path d="{hline(cx - r, cy + r * 0.3, cx + r, cy + r * 0.3, seed + 1, 0.4)}" stroke="{CREAM}" stroke-width="2" fill="none"/>')
    elif style == "indent":
        for k in range(3):
            rr = r * (0.7 - k * 0.2)
            deco.append(f'<path d="{org_poly(star_pts(cx, cy, rr, rr * 0.5, 8, -90), seed + k, 0.4, 20, 1)}" fill="{lt(col, 0.2 + k * 0.2)}" stroke="{dk(col, 0.25)}" stroke-width="1.6" opacity="0.9"/>')
    elif style == "glitter":
        deco.append(dab_dots(seed, int(r * 4), (cx - r, cy - r, cx + r, cy + r), ["#FFF6D8", GOLD_D, "#FFFFFF", GOLD_L], (0.8, 1.8), (0.5, 1)))
    elif style == "flake":
        deco.append(snowflake(cx, cy, r * 0.58, CREAM, seed, sw=max(2, r * 0.07), op=0.95))
        deco.append(dab_dots(seed, 12, (cx - r, cy - r, cx + r, cy + r), [CREAM], (1, 1.8), (0.7, 1)))
    elif style == "stripes":
        for k in range(-4, 5):
            deco.append(f'<path d="M {_f(cx + k * r * 0.34 - r)} {_f(cy + r)} L {_f(cx + k * r * 0.34 + r)} {_f(cy - r)}" stroke="{CREAM}" stroke-width="{_f(r * 0.14)}" opacity="0.9"/>')
    cid = P.clip(f'<path d="{d}"/>')
    g = P.rg([(0, "#FFFFFF", 0.0), (0.7, "#000000", 0), (1, "#2A0A10", 0.35)], cx=0.38, cy=0.36, r=0.75)
    out.append(f'<g clip-path="url(#{cid})">{"".join(deco)}<rect x="{_f(cx - r)}" y="{_f(cy - r)}" width="{_f(2 * r)}" height="{_f(2 * r)}" fill="url(#{g})"/></g>')
    out.append(f'<path d="M {_f(cx - r * 0.6)} {_f(cy - r * 0.08)} Q {_f(cx - r * 0.58)} {_f(cy - r * 0.6)} {_f(cx - r * 0.06)} {_f(cy - r * 0.68)}" stroke="#FFFFFF" stroke-width="{max(1.6, r * 0.11):.1f}" fill="none" stroke-linecap="round" opacity="0.75"/>'
               f'<circle cx="{_f(cx - r * 0.4)}" cy="{_f(cy - r * 0.42)}" r="{max(1, r * 0.08):.1f}" fill="#FFFFFF" opacity="0.9"/>')
    out.append(ink(d, INK, max(1.4, r * 0.04), seed, 2, 0.8))
    return "".join(out)


def teardrop(P, cx, cy, L, col, seed, rot=0):
    """Vintage teardrop / finial ornament lying on its side."""
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    out.append(cast(cx + 6, cy + 8, L * 0.5, L * 0.18, "#6A3A3A", 0.3, seed))
    pts = [(cx - L * 0.5, cy), (cx - L * 0.36, cy - L * 0.14), (cx - L * 0.1, cy - L * 0.2), (cx + L * 0.08, cy - L * 0.12), (cx + L * 0.2, cy - L * 0.05),
           (cx + L * 0.5, cy), (cx + L * 0.2, cy + L * 0.05), (cx + L * 0.08, cy + L * 0.12), (cx - L * 0.1, cy + L * 0.2), (cx - L * 0.36, cy + L * 0.14)]
    d = smooth_closed(pts)
    out.append(paint(P, d, col, [lt(col, 0.35), dk(col, 0.25), GOLD_L], bbox(pts), seed, angle=0, n=20, shade=dk(col, 0.45), shade_op=0.5,
                     shade_dir=(0, 0, 0, 1), light=lt(col, 0.5), light_op=0.5, ink_c=None))
    cid = P.clip(f'<path d="{d}"/>')
    out.append(f'<g clip-path="url(#{cid})">'
               + "".join(f'<path d="M {_f(cx + k * L * 0.12)} {_f(cy - L * 0.3)} q 6 {_f(L * 0.3)} 0 {_f(L * 0.6)}" stroke="{GOLD_L}" stroke-width="3" fill="none" opacity="0.85"/>' for k in range(-3, 3))
               + "</g>")
    out.append(f'<path d="M {_f(cx - L * 0.32)} {_f(cy - L * 0.1)} Q {_f(cx - L * 0.1)} {_f(cy - L * 0.18)} {_f(cx + L * 0.1)} {_f(cy - L * 0.1)}" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.7"/>')
    out.append(ink(d, INK, 1.8, seed, 2, 0.8))
    out.append(paint(P, org_rect(cx - L * 0.6, cy - L * 0.06, L * 0.1, L * 0.12, seed + 1, 0.2, 4, 1), GOLD, [GOLD_L], (cx - L * 0.6, cy - L * 0.06, cx - L * 0.5, cy + L * 0.06), seed + 1, n=0, ink_c=INK, ink_w=1.3))
    out.append("</g>")
    return "".join(out)


def tissue(P, x, y, w, h, seed, col="#FBEAEA"):
    """Crumpled tissue paper filling a box cell."""
    rnd = random.Random(seed)
    d = org_rect(x, y, w, h, seed, 2.4, 14, 6)
    out = [paint(P, d, col, ["#FFFFFF", "#F2D2D4", "#FFF6F4"], (x, y, x + w, y + h), seed, angle=rnd.uniform(-60, 60), n=24, length=(10, 30), width=(2, 5),
                 shade="#C89898", shade_op=0.35, shade_dir=(0, 0, 1, 1), ink_c=None)]
    for _ in range(9):
        px, py = rnd.uniform(x + 6, x + w - 6), rnd.uniform(y + 6, y + h - 6)
        out.append(f'<path d="M {_f(px)} {_f(py)} l {rnd.uniform(-18, 18):.1f} {rnd.uniform(-12, 12):.1f} l {rnd.uniform(-10, 10):.1f} {rnd.uniform(-8, 8):.1f}" stroke="#D8A8AC" stroke-width="1.2" fill="none" opacity="0.7"/>')
    return "".join(out)


def trim_the_tree():
    """A vintage ornament box seen from above: six glass baubles nestled in tissue, stamped 'handle with care'."""
    P = Pn("trim-the-tree")
    o = [sky_wash(P, "#F6DAD4", "#EFC6C2", ["#FBE6E2", "#F2CCC8", "#EDB8B6", "#FFF0EC"], 501, n=260, angle=-20, length=(60, 160), width=(6, 14))]
    o.append(mottle(502, ["#E8A8A8", "#FFFFFF"], 10))
    # tinsel bits and a stray hook on the table
    rnd = random.Random(503)
    for _ in range(40):
        x, y = rnd.uniform(10, 590), rnd.uniform(10, 590)
        if 80 < x < 520 and 150 < y < 545:
            continue
        o.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-10, 10):.1f} {rnd.uniform(-10, 10):.1f}" stroke="{rnd.choice([GOLD, GOLD_L, "#E8E4EC"])}" stroke-width="1.6" stroke-linecap="round" opacity="0.8"/>')
    # fir sprigs at two corners
    for k in range(5):
        o.append(pine_sprig(P, 640, 620 - k * 14, 500 + k * 6, 560 - k * 10, 504 + k, needle=14))
        o.append(pine_sprig(P, -40, 620 - k * 12, 120 - k * 10, 560 - k * 12, 510 + k, needle=14))
    o.append(ball_paint(P, 520, 566, 9, RED, 516) + ball_paint(P, 536, 552, 8, RED, 517) + ball_paint(P, 100, 556, 8, RED, 518))
    # box: outer wall, interior floor, dividers
    kraft, kraft_d, kraft_l = "#C9A27A", "#9A7652", "#E2C29A"
    bx0, by0, bx1, by1 = 92, 168, 508, 470
    o.append(cast(306, 520, 236, 30, "#6A3A3A", 0.35, 519))
    front = org_poly([(bx0 - 4, by1 - 6), (bx1 + 4, by1 - 6), (bx1 + 2, 532), (bx0 - 2, 532)], 520, 0.6, 20, 3)
    o.append(paint(P, front, kraft, [kraft_l, kraft_d, "#B89068"], (bx0, by1, bx1, 532), 520, angle=0, n=70, length=(30, 80), width=(1, 3), shade=kraft_d,
                   shade_op=0.5, shade_dir=(0, 0, 0, 1), ink_c=INK))
    outer = org_rect(bx0 - 4, by0 - 10, bx1 - bx0 + 8, by1 - by0 + 6, 521, 0.6, 20, 3)
    o.append(paint(P, outer, kraft_l, [kraft, "#EED2AE"], (bx0 - 4, by0 - 10, bx1 + 4, by1), 521, angle=0, n=40, ink_c=INK))
    inner = org_rect(bx0 + 8, by0 + 2, bx1 - bx0 - 16, by1 - by0 - 18, 522, 0.5, 20, 2)
    o.append(paint(P, inner, kraft_d, [kraft, "#8A6644"], (bx0 + 8, by0 + 2, bx1 - 8, by1 - 16), 522, angle=-90, n=40, ink_c=None))
    cw, ch = (bx1 - bx0 - 16) / 3, (by1 - by0 - 18) / 2
    cells = [(bx0 + 8 + c * cw, by0 + 2 + r * ch) for r in range(2) for c in range(3)]
    for k, (cx_, cy_) in enumerate(cells):
        o.append(tissue(P, cx_ + 4, cy_ + 4, cw - 8, ch - 8, 523 + k, col=["#FBEAEA", "#FFF4F0", "#F8E2E4"][k % 3]))
    # inner shadow under the top wall
    o.append(f'<path d="M {bx0 + 8} {by0 + 2} L {bx1 - 8} {by0 + 2} L {bx1 - 8} {by0 + 16} L {bx0 + 8} {by0 + 16} Z" fill="#5A3A22" opacity="0.25"/>')
    # dividers
    for c in (1, 2):
        x = bx0 + 8 + c * cw
        o.append(f'<path d="{org_rect(x - 3, by0 + 2, 6, by1 - by0 - 18, 530 + c, 0.4, 20, 1)}" fill="{kraft_l}" stroke="{INK}" stroke-width="1.4" opacity="0.95"/>')
        o.append(f'<path d="M {x + 4} {by0 + 4} L {x + 6} {by1 - 18}" stroke="#5A3A22" stroke-width="4" opacity="0.2"/>')
    y = by0 + 2 + ch
    o.append(f'<path d="{org_rect(bx0 + 8, y - 3, bx1 - bx0 - 16, 6, 533, 0.4, 20, 1)}" fill="{kraft_l}" stroke="{INK}" stroke-width="1.4" opacity="0.95"/>')
    o.append(f'<path d="M {bx0 + 8} {y + 4} L {bx1 - 8} {y + 6}" stroke="#5A3A22" stroke-width="4" opacity="0.2"/>')
    # the ornaments
    specs = [(RED, "band", -30), ("#7FB2D0", "indent", 20), (GOLD, "glitter", 140), (PINE, "flake", -110), (PINK, "stripes", 60), (None, None, 0)]
    for k, ((cx_, cy_), (col, style, cr)) in enumerate(zip(cells, specs)):
        mx, my = cx_ + cw / 2, cy_ + ch / 2
        if col:
            o.append(bauble(P, mx, my + 2, 46, col, style, 540 + k * 5, cap_rot=cr, cap_c=GOLD if col != "#7FB2D0" else "#C9CED6"))
        else:
            o.append(teardrop(P, mx, my + 2, 116, CRAN, 570, rot=-34))
    # stamp on the front wall
    o.append('<g transform="rotate(-2 300 504)" opacity="0.88">')
    o.append(f'<path d="{org_rect(168, 486, 264, 36, 571, 0.6, 20, 2)}" fill="none" stroke="{RED_D}" stroke-width="2.4"/>')
    o.append(f'<path d="{org_rect(173, 490, 254, 28, 572, 0.5, 20, 2)}" fill="none" stroke="{RED_D}" stroke-width="1.2"/>')
    o.append(ptext(300, 511, "HANDLE WITH CARE", MONO, 19, RED_D, max_w=240, ls=4))
    o.append("</g>")
    o.append(btext(P, 300, 128, "Trim the Tree", DMS, 88, CRAN, [RED, RED_D, "#B03040", RED_L], 573, max_w=470, shadow="#E2AEA8", sh=(0.02, 0.03), hi="#F6C0B8"))
    o.append(twinkle(70, 150, 8, GOLD) + twinkle(530, 150, 8, GOLD))
    return finish(P, "".join(o), 574)


# ---------------------------------------------------------------
def gumdrop(P, x, y, r, col, seed):
    d = smooth_closed([(x - r, y), (x - r * 0.9, y - r * 0.6), (x - r * 0.4, y - r * 1.05), (x + r * 0.4, y - r * 1.05), (x + r * 0.9, y - r * 0.6), (x + r, y), (x, y + r * 0.12)])
    out = [paint(P, d, col, [lt(col, 0.35), dk(col, 0.2)], (x - r, y - r * 1.05, x + r, y + r * 0.12), seed, angle=-60, n=5, shade=dk(col, 0.4), shade_op=0.45,
                 shade_dir=(0, 0, 1, 0.6), ink_c=INK, ink_w=max(1, r * 0.08), ink_op=0.7)]
    out.append(dab_dots(seed, int(r * 1.2), (x - r * 0.8, y - r * 0.9, x + r * 0.8, y - r * 0.1), ["#FFFFFF"], (0.6, 1.2), (0.6, 0.95)))
    out.append(f'<path d="M {_f(x - r * 0.5)} {_f(y - r * 0.5)} q {_f(r * 0.1)} {_f(-r * 0.35)} {_f(r * 0.4)} {_f(-r * 0.4)}" stroke="#FFFFFF" stroke-width="{max(1.2, r * 0.15):.1f}" fill="none" stroke-linecap="round" opacity="0.7"/>')
    return "".join(out)


def peppermint(P, x, y, r, seed, rot=0):
    out = [f'<g transform="rotate({rot} {_f(x)} {_f(y)})">']
    d = blob(x, y, r, r, seed, 0.02, 14)
    out.append(f'<path d="{d}" fill="#FFF8F0"/>')
    for k in range(6):
        a0 = math.radians(k * 60)
        a1 = math.radians(k * 60 + 30)
        out.append(f'<path d="M {_f(x)} {_f(y)} Q {_f(x + r * 0.7 * math.cos(a0 + 0.5))} {_f(y + r * 0.7 * math.sin(a0 + 0.5))} {_f(x + r * math.cos(a0))} {_f(y + r * math.sin(a0))} '
                   f'A {_f(r)} {_f(r)} 0 0 1 {_f(x + r * math.cos(a1))} {_f(y + r * math.sin(a1))} Q {_f(x + r * 0.5 * math.cos(a1 + 0.3))} {_f(y + r * 0.5 * math.sin(a1 + 0.3))} {_f(x)} {_f(y)} Z" fill="{RED}"/>')
    out.append(f'<path d="M {_f(x - r * 0.6)} {_f(y - r * 0.2)} q {_f(r * 0.1)} {_f(-r * 0.4)} {_f(r * 0.5)} {_f(-r * 0.45)}" stroke="#FFFFFF" stroke-width="{max(1.2, r * 0.14):.1f}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    out.append(ink(d, INK, max(1.2, r * 0.07), seed, 2, 0.75))
    out.append("</g>")
    return "".join(out)


def lollipop(P, x, base, h, r, seed, a=RED, b="#FFF8F0"):
    out = [f'<path d="M {_f(x)} {_f(base)} L {_f(x)} {_f(base - h + r)}" stroke="#3A2418" stroke-width="7" stroke-linecap="round" opacity="0.7"/>'
           f'<path d="M {_f(x)} {_f(base)} L {_f(x)} {_f(base - h + r)}" stroke="#FFF8F0" stroke-width="4.6" stroke-linecap="round"/>']
    cy = base - h
    d = blob(x, cy, r, r, seed, 0.015, 16)
    out.append(f'<path d="{d}" fill="{b}"/>')
    sp = [(x + (r * t / 40) * 0.95 * math.cos(t * 0.42), cy + (r * t / 40) * 0.95 * math.sin(t * 0.42)) for t in range(0, 41)]
    out.append(f'<path d="{smooth_open(sp)}" stroke="{a}" stroke-width="{_f(r * 0.22)}" fill="none" stroke-linecap="round"/>')
    g = P.rg([(0, "#FFFFFF", 0.0), (0.7, "#000000", 0), (1, "#3A0A10", 0.3)], cx=0.4, cy=0.38, r=0.7)
    out.append(f'<path d="{d}" fill="url(#{g})"/>')
    out.append(f'<path d="M {_f(x - r * 0.6)} {_f(cy - r * 0.2)} q {_f(r * 0.1)} {_f(-r * 0.4)} {_f(r * 0.5)} {_f(-r * 0.45)}" stroke="#FFFFFF" stroke-width="{max(1.4, r * 0.12):.1f}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    out.append(ink(d, INK, max(1.2, r * 0.06), seed, 2, 0.8))
    out.append(bow_p(P, x, cy + r + 4, r * 0.55, PINE_L, seed + 1))
    return "".join(out)


def icing_drip(P, pts, thick, seed, col="#FFFBF2"):
    """Royal icing piped along an edge, with rounded drips hanging down."""
    rnd = random.Random(seed)
    top = [(x, y - thick * 0.5) for x, y in pts]
    bot = []
    for i, (x, y) in enumerate(reversed(pts)):
        dy = thick * 0.5
        if 0 < i < len(pts) - 1 and rnd.random() < 0.55:
            dy += thick * rnd.uniform(0.8, 2.2)
        bot.append((x, y + dy))
    d = smooth_closed(top + bot)
    return (f'<path d="{d}" fill="#3A2418" opacity="0.18" transform="translate(2 3)"/>'
            f'<path d="{d}" fill="{col}"/>'
            f'<path d="{smooth_open([(x, y - thick * 0.25) for x, y in pts])}" stroke="#FFFFFF" stroke-width="{_f(thick * 0.25)}" fill="none" stroke-linecap="round" opacity="0.9"/>'
            + ink(d, "#C8A890", 1.2, seed, 1, 0.6))


def gb_house(P, cx, base, w, h, rh, seed, roof="#F6D4D2", door_c="#8E4E22", big=False):
    """Gingerbread house: speckled dough walls, frosted roof with candy shingles and drips, lit windows, gumdrops."""
    out = []
    x0, x1 = cx - w / 2, cx + w / 2
    top = base - h
    dough, dough_d, dough_l = "#B86E36", "#7E4420", "#DE9A5E"
    wall = org_rect(x0, top, w, h, seed, 0.8, 14, 3)
    out.append(cast(cx + 10, base + 3, w * 0.6, 9, "#8A5A6A", 0.4, seed))
    out.append(paint(P, wall, dough, [dough_l, dough_d, "#C87E42", "#A0602E"], (x0, top, x1, base), seed, angle=-70, n=int(w * h / 120), length=(6, 16), width=(1, 3),
                     shade=dough_d, shade_op=0.5, shade_dir=(0, 0, 1, 0.2), ink_c=INK))
    out.append(dab_dots(seed + 1, int(w * h / 90), (x0 + 3, top + 3, x1 - 3, base - 3), ["#6A3414", "#F0B47A"], (0.6, 1.4), (0.3, 0.6)))
    # piped icing on the corners
    for xx in (x0 + 4, x1 - 4):
        out.append(f'<path d="M {_f(xx)} {_f(top + 6)} L {_f(xx)} {_f(base - 4)}" stroke="#FFFBF2" stroke-width="4" stroke-dasharray="0.1 8" stroke-linecap="round"/>')
    # windows (warm, with icing frames)
    ww = w * (0.2 if big else 0.26)
    wy = top + h * 0.2
    wxs = (x0 + w * 0.12, x1 - w * 0.12 - ww) if big else ((cx - ww / 2,) if not big else ())
    for k, wx in enumerate(wxs):
        out.append(lit_window(P, wx, wy, ww, ww * 1.05, seed + 10 + k, frame="#FFFBF2", sill=False, halo=1.4, fw=3.4))
        out.append(icing_drip(P, [(wx - 5, wy - 2), (wx + ww / 2, wy - 4), (wx + ww + 5, wy - 2)], 6, seed + 12 + k))
    # door
    if big:
        dw, dh = w * 0.22, h * 0.5
        dd = org_poly([(cx - dw / 2, base), (cx - dw / 2, base - dh + dw / 2), (cx, base - dh), (cx + dw / 2, base - dh + dw / 2), (cx + dw / 2, base)], seed + 3, 0.5, 8, 1.5)
        out.append(paint(P, dd, door_c, [dk(door_c, 0.2), lt(door_c, 0.2)], (cx - dw / 2, base - dh, cx + dw / 2, base), seed + 3, angle=-90, n=10, ink_c=INK))
        out.append(f'<path d="{dd}" fill="none" stroke="#FFFBF2" stroke-width="3.4" stroke-dasharray="0.1 7" stroke-linecap="round" transform="translate(0 0)"/>')
        out.append(gumdrop(P, cx + dw * 0.28, base - dh * 0.42, 4, GOLD, seed + 4))
        out.append(candy_cane(P, cx - dw / 2 - 14, base, dh * 1.0, seed + 5, w=7) + candy_cane(P, cx + dw / 2 + 4, base, dh * 1.0, seed + 6, w=7))
    # roof: thick frosting slab with candy shingles, drips on the eaves
    rf = org_poly([(x0 - w * 0.12, top + 8), (cx, top - rh), (x1 + w * 0.12, top + 8)], seed + 7, 0.8, 14, 4)
    rb = (x0 - w * 0.12, top - rh, x1 + w * 0.12, top + 8)
    out.append(paint(P, rf, "#FFF8F0", ["#FFFFFF", "#F2E6DA"], rb, seed + 7, angle=0, n=20, ink_c=INK))
    rnd = random.Random(seed)
    sh = []
    rows = max(3, int(rh / 16))
    for r in range(rows):
        t = (r + 0.7) / (rows + 0.6)
        yy = top - rh + rh * t + 4
        half = (w / 2 + w * 0.12) * t
        n = max(2, int(2 * half / 20))
        for j in range(n):
            xx = cx - half + (j + 0.5) * 2 * half / n + (5 if r % 2 else 0)
            col = rnd.choice([roof, PINK, "#F6E2B8", "#BFE0D0", roof])
            sh.append(f'<path d="{blob(xx, yy, 9, 6.5, seed + r * 20 + j, 0.08, 10)}" fill="{col}" stroke="{dk(col, 0.25)}" stroke-width="1.2"/>')
    cid = P.clip(f'<path d="{rf}"/>')
    out.append(f'<g clip-path="url(#{cid})">{"".join(sh)}</g>')
    out.append(icing_drip(P, [(x0 - w * 0.13, top + 8), (x0 + w * 0.1, top - rh * 0.4), (cx, top - rh - 2)], 9, seed + 8))
    out.append(icing_drip(P, [(cx, top - rh - 2), (x1 - w * 0.1, top - rh * 0.4), (x1 + w * 0.13, top + 8)], 9, seed + 9))
    # gumdrops along the ridge + a peppermint in the gable
    if big:
        for k, f in enumerate((-0.3, 0, 0.3)):
            gx = cx + f * (w / 2 + w * 0.12)
            gy = top - rh + abs(f) * (rh + 8) - 5
            out.append(gumdrop(P, gx, gy, 8, [RED, PINE_L, GOLD][k], seed + 30 + k))
        out.append(peppermint(P, cx, top - rh * 0.42, rh * 0.13, seed + 33))
    else:
        out.append(gumdrop(P, cx, top - rh - 4, 6, RED, seed + 30))
    return "".join(out)


def gingerbread_lane():
    """A little street of gingerbread houses on frosting snow: candy-cane posts, lollipop trees, a peppermint path, a gingerbread neighbour."""
    P = Pn("gingerbread-lane")
    o = [sky_wash(P, "#F7D9D6", "#FBEDE8", ["#F2C8C6", "#FBE4E0", "#F6D2D0", "#FFF2EE"], 601, n=260, angle=-10, length=(60, 160), width=(5, 12))]
    o.append(mottle(602, ["#EDB0B4", "#FFFFFF"], 10))
    o.append(P.glow(300, 380, 260, "#FFF2E0", 0.7))
    # distant frosting hills with tiny trees
    o.append(f'<path d="{smooth_closed([(-20, 410), (100, 380), (220, 396), (380, 372), (520, 392), (620, 380), (620, 470), (-20, 470)])}" fill="#F6E6E8"/>')
    o.append(ink(smooth_open([(-20, 410), (100, 380), (220, 396), (380, 372), (520, 392), (620, 380)]), "#D8B8C0", 1.6, 603, 1, 0.6))
    o.append(far_trees(P, 404, 604, "#BFDCCB", 22, (24, 46), snow=True))
    # side houses (smaller, set back)
    o.append(gb_house(P, 118, 452, 108, 74, 54, 605, roof="#BFE0D0"))
    o.append(gb_house(P, 482, 452, 108, 74, 54, 606, roof="#F6E2B8"))
    # frosting ground
    ground = smooth_closed([(-20, 448), (150, 456), (300, 450), (450, 456), (620, 448), (620, 620), (-20, 620)])
    o.append(snow_field(P, ground, (-20, 444, 620, 620), 607, edge_c=None))
    # the main house
    o.append(gb_house(P, 300, 470, 190, 136, 96, 608, roof="#F6D4D2", big=True))
    # peppermint stepping stones down the lane
    for k, (px, py, pr) in enumerate(((300, 488, 12), (290, 510, 14), (304, 534, 15), (318, 560, 16))):
        o.append(f'<g transform="translate({px} {py}) scale(1 0.55) translate({-px} {-py})">{peppermint(P, px, py, pr, 609 + k, rot=k * 23)}</g>')
    # lollipop trees + gumdrop bushes
    o.append(lollipop(P, 196, 486, 92, 20, 613, a=RED) + lollipop(P, 408, 486, 102, 22, 614, a=PINE_L))
    for k, (gx, gy, gr, gc) in enumerate(((222, 482, 9, RED), (240, 486, 7, GOLD), (362, 484, 9, PINE_L), (380, 488, 7, PINK), (64, 470, 8, PINK), (540, 470, 8, RED))):
        o.append(gumdrop(P, gx, gy, gr, gc, 615 + k))
    # a gingerbread neighbour waving on the lane
    o.append(cast(470, 532, 30, 5, "#8A5A6A", 0.4, 621))
    o.append(gingerbread_man(P, 470, 498, 64, 622, rot=6))
    o.append(candy_cane(P, 120, 534, 54, 623, rot=-6, w=8))
    # sugar snow
    o.append(flakes(624, 70, (0, 0, 600, 600), (1.1, 2.8), col="#FFFFFF", avoid=((60, 50, 540, 230),)))
    o.append(btext(P, 300, 122, "gingerbread", SERIF_IT, 84, "#7A3A1E", ["#9A5A2E", "#5A2A12", "#B8763E", "#6A3414"], 625, max_w=460, shadow="#FFFFFF", sh=(0.025, 0.04), hi="#E2A262"))
    o.append(btext(P, 300, 212, "LANE", BEBAS, 92, CRAN, [RED, RED_D, "#B03040", RED_L], 626, ls=24, max_w=300, shadow="#FFFFFF", sh=(0.025, 0.04), hi="#F6C0B8"))
    o.append(flank(178, "LANE", BEBAS, 92, 24, CRAN, max_w=300, L=56, seed=627))
    return finish(P, "".join(o), 628)


DESIGNS = {
    "peace-on-earth": peace_on_earth,
    "merry-christmas": merry_christmas,
    "believe": believe,
    "merry-and-bright": merry_and_bright,
    "tis-the-season": tis_the_season,
    "hung-with-care": hung_with_care,
    "warmest-wishes": warmest_wishes,
    "north-pole-post-office": north_pole_post_office,
    "let-it-snow": let_it_snow,
    "seasons-greetings": seasons_greetings,
    "cookies-for-santa": cookies_for_santa,
    "hot-cocoa-season": hot_cocoa_season,
    "feliz-natal": feliz_natal,
    "trim-the-tree": trim_the_tree,
    "gingerbread-lane": gingerbread_lane,
}


def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
