"""Christmas, painted edition: every magnet is a small gouache-style illustration (graded light, glows, glass
reflections, knit and wood textures, snow with blue shadows) paired with designed type.

Run: python3 christmas_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save, star_points
import paint as pt
from paint import P, dots, rough, y_on
from places_painted import Cam, puff_column
from poster import ANTON

COL = "christmas"
PINE, PINE2, CRAN, RED, GOLD, CREAM, INK, NAVY = "#173F30", "#245C45", "#8E2234", "#B8312F", "#E2B04A", "#F6EDE0", "#2A1E18", "#1F3550"


# ---------------------------------------------------------------- colour + defs helpers
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


class Defs:
    """Collects gradients / clips for one design, with ids prefixed by the design's key."""

    def __init__(self, u):
        self.u, self.items, self.n, self.cache = u, [], 0, {}

    def id(self, p="g"):
        self.n += 1
        return f"{self.u}-{p}{self.n}"

    def lg(self, stops, x1=0, y1=0, x2=0, y2=1, units="objectBoundingBox"):
        i = self.id()
        self.items.append(pt.lg(i, stops, x1, y1, x2, y2, units))
        return i

    def rg(self, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None):
        i = self.id()
        self.items.append(pt.rg(i, stops, cx, cy, r, fx, fy))
        return i

    def clip(self, inner):
        i = self.id("c")
        self.items.append(f'<clipPath id="{i}">{inner}</clipPath>')
        return i

    def ball(self, col):
        """Glossy sphere: light falls from the upper left."""
        k = ("ball", col)
        if k not in self.cache:
            self.cache[k] = self.rg([(0, lt(col, 0.6)), (0.25, lt(col, 0.2)), (0.7, col), (1, dk(col, 0.45))], cx=0.42, cy=0.42, r=0.62, fx=0.32, fy=0.3)
        return self.cache[k]

    def glow(self, col, s=0.8):
        k = ("glow", col, s)
        if k not in self.cache:
            self.cache[k] = self.rg([(0, col, s), (0.3, col, s * 0.5), (1, col, 0)])
        return self.cache[k]

    def svg(self):
        return "<defs>" + "".join(self.items) + "</defs>"


def T(x, y, s, font, size, fill, max_w=480, ls=0, anchor="middle", extra=""):
    sz = fit_size(s, font, size, max_w, ls)
    if anchor == "middle" and ls:
        x += ls / 2
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" {font} font-size="{sz}"{lsa} fill="{fill}"{extra}>{esc(s)}</text>'


def TS(x, y, s, font, size, fill, shadow, dx=0, dy=5, **kw):
    return T(x + dx, y + dy, s, font, size, shadow, **kw) + T(x, y, s, font, size, fill, **kw)


def TO(x, y, s, font, size, fill, stroke, sw=8, **kw):
    """Text with an outline painted underneath (paint-order) so it sits on busy art."""
    ex = kw.pop("extra", "")
    return T(x, y, s, font, size, fill, extra=f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" paint-order="stroke"{ex}', **kw)


def side_rules(cy, s, font, size, ls, col, max_w=480, gap=18, L=50, sw=3, star=True):
    """Two short rules flanking a centred word (measured, so they never touch it)."""
    w = measure(s, font, fit_size(s, font, size, max_w, ls), ls) - ls
    x0, x1 = 300 - w / 2 - gap, 300 + w / 2 + gap
    out = f'<g stroke="{col}" stroke-width="{sw}" stroke-linecap="round"><line x1="{x0 - L:.1f}" y1="{cy}" x2="{x0:.1f}" y2="{cy}"/><line x1="{x1:.1f}" y1="{cy}" x2="{x1 + L:.1f}" y2="{cy}"/></g>'
    if star:
        out += twinkle(x0 - L - 10, cy, 8, col) + twinkle(x1 + L + 10, cy, 8, col)
    return out


def twinkle(x, y, r, col, op=1.0):
    q = r * 0.14
    return (f'<path d="M {x:.1f} {y - r:.1f} Q {x + q:.1f} {y - q:.1f} {x + r:.1f} {y:.1f} Q {x + q:.1f} {y + q:.1f} {x:.1f} {y + r:.1f} '
            f'Q {x - q:.1f} {y + q:.1f} {x - r:.1f} {y:.1f} Q {x - q:.1f} {y - q:.1f} {x:.1f} {y - r:.1f} Z" fill="{col}" opacity="{op}"/>')


def snowfall(seed, n, box=(0, 0, 600, 600), r=(1.2, 3.6), col="#FFFFFF", op=(0.45, 0.95), avoid=None):
    rnd = random.Random(seed)
    out = []
    while len(out) < n:
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        if avoid and any(a[0] < x < a[2] and a[1] < y < a[3] for a in avoid):
            continue
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(*r):.1f}" opacity="{rnd.uniform(*op):.2f}"/>')
    return f'<g fill="{col}">' + "".join(out) + "</g>"


def soft_flakes(D, seed, n, box=(0, 0, 600, 600), r=(5, 12), col="#FFFFFF", s=0.7, avoid=None):
    g = D.glow(col, s)
    rnd = random.Random(seed)
    out = []
    while len(out) < n:
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        if avoid and any(a[0] < x < a[2] and a[1] < y < a[3] for a in avoid):
            continue
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(*r):.1f}"/>')
    return f'<g fill="url(#{g})">' + "".join(out) + "</g>"


def speck(seed, n, color, box=(0, 0, 600, 600), r=(0.6, 1.8), op=(0.15, 0.45)):
    return dots(n, seed, box, color, r=r, opacity=op)


def light(D, x, y, r, col, halo=4.0, s=0.75):
    """A glowing little bulb: soft halo plus a hot core."""
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * halo:.1f}" fill="url(#{D.glow(col, s)})"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{lt(col, 0.55)}"/>'
            f'<circle cx="{x - r * 0.3:.1f}" cy="{y - r * 0.3:.1f}" r="{r * 0.45:.1f}" fill="#FFFFFF" opacity="0.85"/>')


def ball(D, x, y, r, col, cap=GOLD, hook=True):
    out = []
    if hook:
        out.append(f'<rect x="{x - r * 0.3:.1f}" y="{y - r * 1.18:.1f}" width="{r * 0.6:.1f}" height="{r * 0.34:.1f}" rx="{r * 0.08:.1f}" fill="{cap}"/>')
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="url(#{D.ball(col)})"/>')
    out.append(f'<ellipse cx="{x - r * 0.38:.1f}" cy="{y - r * 0.4:.1f}" rx="{r * 0.22:.1f}" ry="{r * 0.14:.1f}" transform="rotate(-35 {x - r * 0.38:.1f} {y - r * 0.4:.1f})" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


def star5(D, x, y, r, col=GOLD, glow_r=None, rot=-90):
    out = []
    if glow_r:
        out.append(f'<circle cx="{x}" cy="{y}" r="{glow_r}" fill="url(#{D.glow("#FFE7A8", 0.7)})"/>')
    out.append(f'<polygon points="{star_points(x, y, r, r * 0.42, rot=rot)}" fill="{col}"/>')
    # bevel: light facets on the upper-left arms
    pts = star_points(x, y, r, r * 0.42, rot=rot).split()
    cxy = (x, y)
    for i in range(0, 10, 2):
        ax, ay = map(float, pts[i].split(","))
        bx, by = map(float, pts[(i + 1) % 10].split(","))
        lit = (ax - x) * -0.6 + (ay - y) * -0.8 > -r * 0.2
        out.append(f'<polygon points="{x:.1f},{y:.1f} {ax:.1f},{ay:.1f} {bx:.1f},{by:.1f}" fill="{"#FFF3C8" if lit else dk(col, 0.25)}" opacity="{0.55 if lit else 0.35}"/>')
    return "".join(out)


# ---------------------------------------------------------------- painted fir
def fir(D, cx, base, h, w, seed, light_c="#5C9A68", mid="#2F6A4C", dark="#163C2E", tiers=6, snow=False, needles=True, lean=0.0):
    """Lush fir built from overlapping drooping tiers; light from the left, needle strokes, shadow under each tier.
    Returns (svg, tiers) where tiers = [(apex_y, hem_y, half_w)] top first, for placing decorations."""
    rnd = random.Random(seed)
    g = D.lg([(0, light_c), (0.42, mid), (1, dark)], cx - w / 2, 0, cx + w / 2, 0, units="userSpaceOnUse")
    top = base - h
    info = []
    for k in range(tiers):
        f = k / (tiers - 1)
        hem = top + h * (0.24 + 0.76 * f)
        apex = top if k == 0 else info[k - 1][1] - h * 0.13
        hw = w / 2 * (0.34 + 0.66 * f)
        info.append((apex, hem, hw))
    shapes = []
    for k, (apex, hem, hw) in enumerate(info):
        ax = cx + lean * (base - apex) * 0.1
        n = 4 + k
        d = f"M {ax:.1f} {apex:.1f} Q {cx - hw * 0.35:.1f} {apex + (hem - apex) * 0.55:.1f} {cx - hw:.1f} {hem - 4:.1f}"
        for j in range(n):
            x0 = cx - hw + 2 * hw * j / n
            x1 = cx - hw + 2 * hw * (j + 1) / n
            drop = rnd.uniform(6, 13)
            d += f" Q {x0 + (x1 - x0) * 0.35:.1f} {hem + drop:.1f} {x1:.1f} {hem - rnd.uniform(1, 6):.1f}"
        d += f" Q {cx + hw * 0.35:.1f} {apex + (hem - apex) * 0.55:.1f} {ax:.1f} {apex:.1f} Z"
        shapes.append(d)
    out = []
    for k in range(tiers - 1, -1, -1):
        apex, hem, hw = info[k]
        out.append(f'<path d="{shapes[k]}" fill="url(#{g})"/>')
        if needles:
            st = []
            cnt = int(hw * (hem - apex) / 34)
            for _ in range(cnt):
                y = rnd.uniform(apex + 6, hem + 2)
                lim = hw * (y - apex) / (hem - apex) * 0.95
                x = rnd.uniform(cx - lim, cx + lim)
                side = 1 if x > cx else -1
                L = rnd.uniform(6, 13)
                col = light_c if (x - cx) < -lim * 0.15 and rnd.random() < 0.8 else (dark if x - cx > lim * 0.3 else mix(mid, light_c, 0.4))
                st.append(f'<path d="M {x:.1f} {y:.1f} l {side * L * 0.75:.1f} {L * 0.55:.1f}" stroke="{col}"/>')
            out.append(f'<g stroke-width="2" stroke-linecap="round" opacity="0.8">{"".join(st)}</g>')
        if k > 0:
            ua, uh, uw = info[k - 1]
            c = D.clip(f'<path d="{shapes[k]}"/>')
            out.append(f'<g clip-path="url(#{c})"><ellipse cx="{cx + uw * 0.15:.1f}" cy="{uh + 6:.1f}" rx="{uw * 1.05:.1f}" ry="12" fill="{dark}" opacity="0.55"/></g>')
        if snow:
            sh, sn = [], []
            n = 4 + k
            for j in range(n + 1):
                x = cx - hw * 0.92 + 1.84 * hw * j / n + rnd.uniform(-4, 4)
                rr = rnd.uniform(5, 9) * (0.7 + 0.5 * k / tiers)
                sh.append(f'<ellipse cx="{x + 1:.1f}" cy="{hem - 2:.1f}" rx="{rr * 1.5:.1f}" ry="{rr * 0.75:.1f}"/>')
                sn.append(f'<ellipse cx="{x:.1f}" cy="{hem - 5:.1f}" rx="{rr * 1.45:.1f}" ry="{rr * 0.68:.1f}"/>')
            out.append(f'<g fill="#B9CCDC">{"".join(sh)}</g><g fill="#FFFFFF">{"".join(sn)}</g>')
    return "".join(out), info


def snow_cap(points, thick=10, seed=1, col="#FFFFFF", shade="#BFD0DE", drips=True):
    """Lumpy snow resting on a line (list of points left to right): rounded ends, soft bumps, a few drips."""
    rnd = random.Random(seed)
    tops = [(x, y - thick * rnd.uniform(0.6, 1.15)) for x, y in points]
    (x0, y0), (x1, y1) = points[0], points[-1]
    d = f"M {x0 - thick * 0.2:.1f} {y0 + 1:.1f} Q {x0 - thick * 0.7:.1f} {tops[0][1]:.1f} {tops[0][0]:.1f} {tops[0][1]:.1f}"
    for (ax, ay), (bx, by) in zip(tops, tops[1:]):
        d += f" Q {(ax + bx) / 2:.1f} {min(ay, by) - thick * 0.45:.1f} {bx:.1f} {by:.1f}"
    d += f" Q {x1 + thick * 0.7:.1f} {tops[-1][1]:.1f} {x1 + thick * 0.2:.1f} {y1 + 1:.1f}"
    under = []
    for i, (x, y) in enumerate(reversed(points)):
        dy = 2
        if drips and 0 < i < len(points) - 1 and rnd.random() < 0.3:
            dy = rnd.uniform(5, 10)
        under.append((x, y + dy))
    d2 = d + "".join(f" Q {x + 3:.1f} {y + 2:.1f} {x:.1f} {y:.1f}" for x, y in under) + " Z"
    return (f'<path d="{d2}" fill="{shade}" transform="translate(1.5 3)"/>'
            f'<path d="{d2}" fill="{col}"/>')


def steam(D, x, y, h, seed, col="#FFFFFF", n=3, spread=26, op=0.55, w=7):
    rnd = random.Random(seed)
    g = D.lg([(0, col, 0), (0.35, col, op), (1, col, 0)], 0, 1, 0, 0)
    out = []
    for i in range(n):
        x0 = x + (i - (n - 1) / 2) * spread
        a = rnd.uniform(10, 18) * (1 if i % 2 else -1)
        d = f"M {x0:.1f} {y:.1f} c {a:.1f} {-h * 0.2:.1f} {-a:.1f} {-h * 0.35:.1f} 0 {-h * 0.55:.1f} s {-a * 0.8:.1f} {-h * 0.3:.1f} {a * 0.4:.1f} {-h * 0.45:.1f}"
        out.append(f'<path d="{d}" fill="none" stroke="url(#{g})" stroke-width="{w}" stroke-linecap="round"/>')
    return "".join(out)


def gift(D, x, y, w, h, d, col, rib, pattern=None, pcol=None, bow=True, tilt=0):
    """3/4-view wrapped box. (x, y) = bottom-left front corner. Light from the upper left."""
    dx, dy = d * 0.75, -d * 0.45
    front = [(x, y), (x + w, y), (x + w, y - h), (x, y - h)]
    side = [(x + w, y), (x + w + dx, y + dy), (x + w + dx, y - h + dy), (x + w, y - h)]
    top = [(x, y - h), (x + w, y - h), (x + w + dx, y - h + dy), (x + dx, y - h + dy)]
    fg = D.lg([(0, lt(col, 0.12)), (1, dk(col, 0.12))], 0, 0, 1, 1)
    out = [f'<g transform="rotate({tilt} {x + w / 2:.1f} {y:.1f})">',
           f'<ellipse cx="{x + w / 2 + dx * 0.6:.1f}" cy="{y + 2:.1f}" rx="{w * 0.62 + dx * 0.5:.1f}" ry="{max(5, d * 0.22):.1f}" fill="#000" opacity="0.22"/>',
           f'<polygon points="{P(front)}" fill="url(#{fg})"/>',
           f'<polygon points="{P(side)}" fill="{dk(col, 0.3)}"/>',
           f'<polygon points="{P(top)}" fill="{lt(col, 0.18)}"/>']
    if pattern:
        pc = pcol or lt(col, 0.6)
        pat = []
        if pattern == "dots":
            for i in range(int(w / 14) + 1):
                for j in range(int(h / 14) + 1):
                    pat.append(f'<circle cx="{x + 7 + i * 14 + (7 if j % 2 else 0):.1f}" cy="{y - 7 - j * 14:.1f}" r="2.6" fill="{pc}"/>')
        elif pattern == "stripes":
            for i in range(-int(h / 12) - 2, int(w / 12) + 2):
                xx = x + i * 16
                pat.append(f'<path d="M {xx:.1f} {y:.1f} l {h:.1f} {-h:.1f} l 6 0 l {-h:.1f} {h:.1f} Z" fill="{pc}"/>')
        elif pattern == "plaid":
            for i in range(int(w / 18) + 1):
                pat.append(f'<rect x="{x + i * 18 + 4:.1f}" y="{y - h:.1f}" width="6" height="{h:.1f}" fill="{pc}" opacity="0.45"/>')
            for j in range(int(h / 18) + 1):
                pat.append(f'<rect x="{x:.1f}" y="{y - h + j * 18 + 4:.1f}" width="{w:.1f}" height="6" fill="{pc}" opacity="0.45"/>')
        elif pattern == "hearts":
            from common import heart
            for i in range(int(w / 22) + 1):
                for j in range(int(h / 22) + 1):
                    pat.append(heart(x + 11 + i * 22 + (11 if j % 2 else 0), y - 11 - j * 22, 6, pc))
        elif pattern == "stars":
            rnd = random.Random(int(x * 7 + y))
            for i in range(int(w * h / 500)):
                pat.append(f'<polygon points="{star_points(x + rnd.uniform(6, w - 6), y - rnd.uniform(6, h - 6), 4.5, 2)}" fill="{pc}"/>')
        c = D.clip(f'<polygon points="{P(front)}"/>')
        out.append(f'<g clip-path="url(#{c})">{"".join(pat)}</g>')
        # pattern faintly on the side and top too
        c2 = D.clip(f'<polygon points="{P(side)}"/>')
        out.append(f'<g clip-path="url(#{c2})" opacity="0.4"><rect x="{x + w:.1f}" y="{y - h + dy:.1f}" width="{dx:.1f}" height="{h - dy:.1f}" fill="{dk(col, 0.3)}"/></g>')
    rw = max(6, w * 0.13)
    rg_ = D.lg([(0, lt(rib, 0.35)), (0.5, rib), (1, dk(rib, 0.2))], 0, 0, 1, 0)
    cxf = x + w / 2
    # ribbon: front vertical, side vertical, top cross
    out.append(f'<rect x="{cxf - rw / 2:.1f}" y="{y - h:.1f}" width="{rw:.1f}" height="{h:.1f}" fill="url(#{rg_})"/>')
    sx = x + w + dx / 2
    out.append(f'<polygon points="{P([(sx - rw * 0.3, y + dy / 2), (sx + rw * 0.3, y + dy / 2), (sx + rw * 0.3, y - h + dy / 2), (sx - rw * 0.3, y - h + dy / 2)])}" fill="{dk(rib, 0.25)}"/>')
    out.append(f'<polygon points="{P([(cxf - rw / 2, y - h), (cxf + rw / 2, y - h), (cxf + rw / 2 + dx, y - h + dy), (cxf - rw / 2 + dx, y - h + dy)])}" fill="{lt(rib, 0.15)}"/>')
    out.append(f'<polygon points="{P([(x + dx / 2 - rw * 0.3, y - h + dy / 2 - rw * 0.25), (x + w + dx / 2 + rw * 0.3, y - h + dy / 2 - rw * 0.25), (x + w + dx / 2 + rw * 0.3, y - h + dy / 2 + rw * 0.35), (x + dx / 2 - rw * 0.3, y - h + dy / 2 + rw * 0.35)])}" fill="{rib}"/>')
    # edge highlight
    out.append(f'<polyline points="{P([(x, y), (x, y - h), (x + dx, y - h + dy)])}" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity="0.35"/>')
    if bow:
        bx, by = cxf + dx / 2, y - h + dy / 2
        s = max(12, w * 0.24)
        out.append(bow_svg(bx, by, s, rib))
    out.append("</g>")
    return "".join(out)


def bow_svg(bx, by, s, rib):
    hi, lo = lt(rib, 0.35), dk(rib, 0.3)
    return (f'<path d="M {bx:.1f} {by:.1f} q {-s * 0.4:.1f} {s * 0.6:.1f} {-s * 0.7:.1f} {s * 0.95:.1f} l {s * 0.3:.1f} {-s * 0.05:.1f} l {s * 0.12:.1f} {s * 0.22:.1f} Z" fill="{lo}"/>'
            f'<path d="M {bx:.1f} {by:.1f} q {s * 0.4:.1f} {s * 0.6:.1f} {s * 0.8:.1f} {s * 0.85:.1f} l {-s * 0.25:.1f} {s * 0.1:.1f} l {-s * 0.05:.1f} {s * 0.25:.1f} Z" fill="{lo}"/>'
            f'<path d="M {bx:.1f} {by:.1f} C {bx - s * 0.6:.1f} {by - s * 0.9:.1f} {bx - s * 1.35:.1f} {by - s * 0.3:.1f} {bx - s * 0.9:.1f} {by + s * 0.12:.1f} C {bx - s * 0.6:.1f} {by + s * 0.3:.1f} {bx - s * 0.2:.1f} {by + s * 0.1:.1f} {bx:.1f} {by:.1f} Z" fill="{rib}"/>'
            f'<path d="M {bx:.1f} {by:.1f} C {bx + s * 0.6:.1f} {by - s * 0.9:.1f} {bx + s * 1.35:.1f} {by - s * 0.3:.1f} {bx + s * 0.9:.1f} {by + s * 0.12:.1f} C {bx + s * 0.6:.1f} {by + s * 0.3:.1f} {bx + s * 0.2:.1f} {by + s * 0.1:.1f} {bx:.1f} {by:.1f} Z" fill="{dk(rib, 0.12)}"/>'
            f'<path d="M {bx - s * 0.2:.1f} {by - s * 0.15:.1f} C {bx - s * 0.5:.1f} {by - s * 0.55:.1f} {bx - s * 0.95:.1f} {by - s * 0.35:.1f} {bx - s * 0.85:.1f} {by - s * 0.05:.1f}" fill="none" stroke="{hi}" stroke-width="{max(1.5, s * 0.1):.1f}" stroke-linecap="round" opacity="0.8"/>'
            f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="{s * 0.2:.1f}" ry="{s * 0.16:.1f}" fill="{dk(rib, 0.05)}"/>'
            f'<ellipse cx="{bx - s * 0.05:.1f}" cy="{by - s * 0.05:.1f}" rx="{s * 0.08:.1f}" ry="{s * 0.06:.1f}" fill="{hi}"/>')


def plaid_bg(D, base, bands, box=(0, 0, 600, 600), step=60, seed=0, vscale=1.0):
    """Woven tartan: wide translucent bands both ways + thin lines + a twill texture."""
    x0, y0, x1, y1 = box
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{base}"/>']
    for col, off, wd, op in bands:
        for i in range(-1, int((x1 - x0) / step) + 2):
            out.append(f'<rect x="{x0 + i * step + off:.1f}" y="{y0}" width="{wd}" height="{y1 - y0}" fill="{col}" opacity="{op}"/>')
        for j in range(-1, int((y1 - y0) / (step * vscale)) + 2):
            out.append(f'<rect x="{x0}" y="{y0 + (j * step + off) * vscale:.1f}" width="{x1 - x0}" height="{wd * vscale:.1f}" fill="{col}" opacity="{op}"/>')
    tw = "".join(f'<line x1="{x0 + i * 6}" y1="{y0}" x2="{x0 + i * 6 + (y1 - y0)}" y2="{y1}"/>' for i in range(-int((y1 - y0) / 6), int((x1 - x0) / 6)))
    out.append(f'<g stroke="#000" stroke-width="1.2" opacity="0.07">{tw}</g>')
    c = D.clip(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/>')
    return f'<g clip-path="url(#{c})">' + "".join(out) + "</g>"


# ======================================================================== REPAINTS
def merry_and_bright():
    u = "mab"
    D = Defs(u)
    out = []
    bg = D.rg([(0, "#2C6C51"), (0.55, "#1A4A38"), (1, "#0C281E")], cx=0.5, cy=0.56, r=0.78)
    out.append(f'<rect width="600" height="600" fill="url(#{bg})"/>')
    # out-of-focus lights behind
    rnd = random.Random(4)
    cols = ["#F2C25A", "#F7E2B0", "#E0574F", "#8FD3C8", "#F2C25A"]
    bok = []
    for _ in range(60):
        x, y = rnd.uniform(-20, 620), rnd.uniform(160, 640)
        if 80 < x < 520 and 200 < y < 470:
            continue
        r = rnd.uniform(8, 30)
        c = rnd.choice(cols)
        g = D.rg([(0, c, 0.34), (0.75, c, 0.24), (0.92, c, 0.3), (1, c, 0)]) if ("bk", c) not in D.cache else D.cache[("bk", c)]
        D.cache[("bk", c)] = g
        bok.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="url(#{g})" opacity="{rnd.uniform(0.4, 1):.2f}"/>')
    out.append("".join(bok))
    # the strand: two swags across the top, C9 bulbs hanging
    sw = [((-20, 58), (150, 190), (300, 74)), ((300, 74), (450, 190), (620, 58))]

    def qb(seg, t):
        (ax, ay), (cx_, cy_), (bx, by) = seg
        x = (1 - t) ** 2 * ax + 2 * (1 - t) * t * cx_ + t * t * bx
        y = (1 - t) ** 2 * ay + 2 * (1 - t) * t * cy_ + t * t * by
        tx_ = 2 * (1 - t) * (cx_ - ax) + 2 * t * (bx - cx_)
        ty_ = 2 * (1 - t) * (cy_ - ay) + 2 * t * (by - cy_)
        return x, y, math.degrees(math.atan2(ty_, tx_))
    bulbs = []
    palette = ["#E8443A", "#F2B33D", "#3FA36B", "#4F8FD8", "#F07F2E", "#E8443A", "#F2B33D", "#3FA36B", "#4F8FD8", "#F07F2E", "#E8443A"]
    k = 0
    for seg in sw:
        for t in (0.12, 0.3, 0.5, 0.7, 0.88):
            x, y, a = qb(seg, t)
            bulbs.append((x, y, a * 0.35 + rnd.uniform(-8, 8), palette[k % len(palette)]))
            k += 1
    out += [f'<circle cx="{x:.1f}" cy="{y + 32:.1f}" r="58" fill="url(#{D.glow(c, 0.55)})"/>' for x, y, a, c in bulbs]
    out.append('<path d="M -20 58 Q 150 190 300 74 Q 450 190 620 58" fill="none" stroke="#0B2018" stroke-width="3.2"/>')
    out.append('<path d="M -20 62 Q 150 194 300 78 Q 450 194 620 62" fill="none" stroke="#0B2018" stroke-width="2.4" opacity="0.7"/>')
    sock = D.lg([(0, "#3D5C4A"), (0.4, "#5E7E6A"), (1, "#14281E")], 0, 0, 1, 0)
    for x, y, a, c in bulbs:
        bg_ = D.rg([(0, lt(c, 0.85)), (0.3, lt(c, 0.35)), (0.75, c), (1, dk(c, 0.3))], cx=0.45, cy=0.55, r=0.62, fx=0.4, fy=0.5)
        out.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({a:.1f})">'
                   f'<rect x="-7.5" y="-3" width="15" height="21" rx="2.5" fill="url(#{sock})"/>'
                   '<g stroke="#0B2018" stroke-width="1.6" opacity="0.6"><line x1="-7" y1="4" x2="7" y2="4"/><line x1="-7" y1="9" x2="7" y2="9"/><line x1="-7" y1="14" x2="7" y2="14"/></g>'
                   f'<path d="M -8.5 17 C -22 27 -19 48 0 66 C 19 48 22 27 8.5 17 Z" fill="url(#{bg_})"/>'
                   f'<path d="M -2 20 C -2 32 -1 46 0 60" stroke="{dk(c, 0.15)}" stroke-width="1.5" opacity="0.35" fill="none"/>'
                   '<path d="M -7 24 C -13 32 -12 44 -5 54" stroke="#FFFFFF" stroke-width="3.2" opacity="0.65" fill="none" stroke-linecap="round"/>'
                   '<circle cx="6" cy="28" r="2.4" fill="#FFFFFF" opacity="0.6"/></g>')
    # words with a warm glow behind
    out.append(pt.mist(300, 380, 250, 120, "#F2C25A", f"{u}-mist", 0.22))
    gold = D.lg([(0, "#FFF0B8"), (0.45, "#F2C25A"), (1, "#C98A26")])
    out.append(TS(300, 352, "merry", SERIF_IT, 150, CREAM, "#0A2018", dy=6, max_w=420))
    out.append(T(300, 486, "& BRIGHT", BEBAS, 138, "#0A2018", ls=10, max_w=470, extra=' transform="translate(0 6)"'))
    out.append(T(300, 486, "& BRIGHT", BEBAS, 138, f"url(#{gold})", ls=10, max_w=470))
    for x, y, r in ((112, 248, 14), (488, 232, 18), (96, 420, 10), (515, 440, 12), (460, 290, 8), (140, 320, 7)):
        out.append(f'<circle cx="{x}" cy="{y}" r="{r * 2.2}" fill="url(#{D.glow("#FFE7A8", 0.5)})"/>' + twinkle(x, y, r, "#FFF3D2"))
    out.append(T(300, 535, "HAPPY HOLIDAYS", MONO, 18, "#F7E2B0", ls=7, max_w=400, extra=' opacity="0.85"'))
    return D.svg() + "\n".join(out)


def merry_christmas():
    u = "mxc"
    D = Defs(u)
    out = []
    wall = D.lg([(0, "#235E47"), (1, "#163F31")])
    out.append(f'<rect width="600" height="420" fill="url(#{wall})"/>')
    # striped wallpaper with tiny gold sprigs
    out.append('<g fill="#2C6C52" opacity="0.55">' + "".join(f'<rect x="{x}" y="0" width="14" height="400"/>' for x in range(-6, 600, 44)) + "</g>")
    out.append('<g fill="#D9B45A" opacity="0.35">' + "".join(f'<circle cx="{x + 30}" cy="{y + (22 if (x // 44) % 2 else 0)}" r="2.2"/>' for x in range(-6, 600, 44) for y in range(20, 400, 44)) + "</g>")
    # warm light from the tree
    out.append(pt.glow(330, 260, 300, "#FFC86A", f"{u}-room", 0.45))
    # window with snowy night
    wx0, wy0, wx1, wy1 = 70, 104, 178, 286
    night = D.lg([(0, "#1B2C4C"), (1, "#3E5A82")])
    out.append(f'<rect x="{wx0 - 12}" y="{wy0 - 12}" width="{wx1 - wx0 + 24}" height="{wy1 - wy0 + 26}" rx="3" fill="#E9DCC6"/>')
    out.append(f'<rect x="{wx0 - 12}" y="{wy0 - 12}" width="{wx1 - wx0 + 24}" height="6" fill="#FFF6E6" opacity="0.7"/>')
    out.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="url(#{night})"/>')
    c = D.clip(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}"/>')
    hills = f'<path d="M {wx0} {wy1 - 30} Q {wx0 + 40} {wy1 - 46} {wx0 + 70} {wy1 - 34} T {wx1} {wy1 - 40} L {wx1} {wy1} L {wx0} {wy1} Z" fill="#DCE6F0"/>'
    trees = "".join(pt.conifer(x, wy1 - 34 + (x - wx0) * 0.02, hh, "#1E3350", x) for x, hh in ((86, 30), (98, 22), (156, 36), (168, 26)))
    out.append(f'<g clip-path="url(#{c})">{hills}{trees}{snowfall(9, 40, (wx0, wy0, wx1, wy1), r=(0.8, 2.2))}<circle cx="{wx1 - 26}" cy="{wy0 + 28}" r="12" fill="#F4EBD0"/>'
               f'<path d="M {wx0} {wy0} L {wx0 + 40} {wy0} L {wx0} {wy0 + 70} Z" fill="#FFFFFF" opacity="0.08"/></g>')
    out.append(f'<g fill="#E9DCC6"><rect x="{(wx0 + wx1) / 2 - 3}" y="{wy0}" width="6" height="{wy1 - wy0}"/><rect x="{wx0}" y="{(wy0 + wy1) / 2 - 3}" width="{wx1 - wx0}" height="6"/></g>')
    out.append(f'<path d="M {wx0} {wy1} q 12 -8 24 -2 q 14 -10 30 -2 q 16 -8 30 0 q 12 -6 24 -2 L {wx1} {wy1} Z" fill="#FFFFFF" opacity="0.9"/>')
    out.append(f'<rect x="{wx0 - 18}" y="{wy1 + 8}" width="{wx1 - wx0 + 36}" height="10" rx="2" fill="#F4EAD8"/><rect x="{wx0 - 18}" y="{wy1 + 16}" width="{wx1 - wx0 + 36}" height="4" fill="#000" opacity="0.2"/>')
    # a little candle on the sill
    out.append(f'<rect x="{wx1 - 30}" y="{wy1 - 16}" width="12" height="24" rx="2" fill="#F6EFE2"/><path d="M {wx1 - 24} {wy1 - 18} q -5 -8 0 -14 q 5 6 0 14 Z" fill="#FFC24A"/>'
               f'<circle cx="{wx1 - 24}" cy="{wy1 - 24}" r="20" fill="url(#{D.glow("#FFD98E", 0.6)})"/>')
    # floor
    floor = D.lg([(0, "#5E3B26"), (1, "#24160F")])
    out.append(f'<rect x="0" y="388" width="600" height="212" fill="url(#{floor})"/>')
    out.append('<rect x="0" y="380" width="600" height="12" fill="#E6D6BC"/><rect x="0" y="390" width="600" height="3" fill="#000" opacity="0.3"/>')
    out.append('<g stroke="#1A0F0A" stroke-width="1.6" opacity="0.5">' + "".join(
        f'<line x1="{300 + (x - 300) * 0.35:.1f}" y1="393" x2="{x}" y2="600"/>' for x in range(-500, 1101, 70)) + "</g>")
    out.append('<g stroke="#1A0F0A" stroke-width="1.2" opacity="0.35">' + "".join(f'<line x1="0" y1="{y}" x2="600" y2="{y}"/>' for y in (404, 424, 452, 490, 540)) + "</g>")
    out.append(pt.mist(330, 420, 230, 40, "#FFC86A", f"{u}-fl", 0.4))
    # rug
    out.append(f'<ellipse cx="330" cy="404" rx="190" ry="22" fill="#7E1F2C"/><ellipse cx="330" cy="404" rx="176" ry="17" fill="none" stroke="#E2B04A" stroke-width="2" stroke-dasharray="6 5"/>')
    # the tree
    tsvg, tiers = fir(D, 330, 396, 286, 250, 11, light_c="#5FA06C", mid="#2E6B4C", dark="#143829", tiers=6)
    out.append(f'<rect x="322" y="372" width="16" height="26" fill="#4A2E1E"/>')
    out.append(tsvg)
    rnd = random.Random(31)
    # garland of warm lights: swooping lines across each tier
    for k, (apex, hem, hw) in enumerate(tiers[1:], 1):
        y0, y1 = hem - (hem - apex) * 0.5, hem - (hem - apex) * 0.28
        out.append(f'<path d="M {330 - hw * 0.6:.1f} {y0:.1f} Q 330 {y1 + 14:.1f} {330 + hw * 0.75:.1f} {y1 - 4:.1f}" fill="none" stroke="#E2B04A" stroke-width="2" opacity="0.8"/>')
    for k, (apex, hem, hw) in enumerate(tiers):
        for _ in range(3 + k * 2):
            y = rnd.uniform(apex + (hem - apex) * 0.35, hem - 6)
            lim = hw * (y - apex) / (hem - apex) * 0.85
            out.append(light(D, rnd.uniform(330 - lim, 330 + lim), y, 2.6, "#FFD98E", halo=4.5))
    cols = ["#C7343A", "#E2B04A", "#F3E9D6", "#7FB8D6", "#C7343A"]
    for k, (apex, hem, hw) in enumerate(tiers[1:], 1):
        for j in range(1 + k):
            y = hem - rnd.uniform(6, 16)
            lim = hw * (y - apex) / (hem - apex) * 0.78
            x = 330 - lim + 2 * lim * (j + 0.5) / (1 + k) + rnd.uniform(-6, 6)
            out.append(ball(D, x, y, rnd.uniform(6.5, 9), cols[(j + k) % len(cols)]))
    out.append(star5(D, 330, 104, 22, glow_r=70))
    # gifts
    out.append(gift(D, 186, 414, 74, 52, 30, "#B8312F", "#E9C46A", pattern="dots", pcol="#F3E3C8"))
    out.append(gift(D, 268, 420, 54, 36, 22, "#F2E7D4", "#2F7A57", pattern="stripes", pcol="#E8C9C0"))
    out.append(gift(D, 380, 418, 86, 62, 30, "#E2B04A", "#9E2430", pattern="plaid", pcol="#B87A20"))
    out.append(gift(D, 470, 424, 40, 30, 18, "#3F7FA8", "#F3E9D6", pattern="stars", pcol="#F3E9D6"))
    # type: script overlapping caps
    gold = D.lg([(0, "#FFE9A8"), (0.5, "#E9B949"), (1, "#C08424")])
    out.append(T(300, 541, "CHRISTMAS", BEBAS, 110, "#120B07", ls=9, max_w=470, extra=' transform="translate(0 5)" opacity="0.7"'))
    out.append(T(300, 541, "CHRISTMAS", BEBAS, 110, f"url(#{gold})", ls=9, max_w=470))
    out.append(TO(236, 474, "merry", SERIF_IT, 80, CREAM, "#2A1810", sw=10, max_w=300))
    return D.svg() + "\n".join(out)


def ho_ho_ho():
    u = "hoh"
    D = Defs(u)
    out = []
    coat = D.lg([(0, "#C8343A"), (1, "#951C24")])
    out.append(f'<rect width="600" height="600" fill="url(#{coat})"/>')
    # velvet folds: soft vertical light / shadow bands
    rnd = random.Random(5)
    for x in range(-40, 640, 70):
        xx = x + rnd.uniform(-16, 16)
        g = D.lg([(0, "#000", 0), (0.5, "#5A0E14", 0.35), (1, "#000", 0)], 0, 0, 1, 0)
        out.append(f'<path d="M {xx:.1f} 0 C {xx + 20:.1f} 150 {xx - 16:.1f} 300 {xx + 10:.1f} 600 L {xx + 46:.1f} 600 C {xx + 22:.1f} 300 {xx + 56:.1f} 150 {xx + 38:.1f} 0 Z" fill="url(#{g})"/>')
        out.append(f'<path d="M {xx + 44:.1f} 0 C {xx + 62:.1f} 150 {xx + 30:.1f} 300 {xx + 52:.1f} 600" fill="none" stroke="#E8565A" stroke-width="5" opacity="0.18"/>')
    out.append(speck(6, 400, "#5A0E14", op=(0.1, 0.3)))
    # fur trim down the coat front (below the belt) and along the hem
    def fur(path_pts, r=(12, 22), seed=1, n=3):
        rr = random.Random(seed)
        base, sh, hi = [], [], []
        for (x0, y0), (x1, y1) in zip(path_pts, path_pts[1:]):
            L = math.hypot(x1 - x0, y1 - y0)
            for i in range(int(L / 7)):
                t = i / max(1, int(L / 7))
                cx_, cy_ = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                for _ in range(n):
                    rad = rr.uniform(*r)
                    px, py = cx_ + rr.uniform(-1, 1) * rad, cy_ + rr.uniform(-1, 1) * rad
                    base.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rad:.1f}"/>')
                    sh.append(f'<circle cx="{px + rad * 0.25:.1f}" cy="{py + rad * 0.3:.1f}" r="{rad * 0.6:.1f}"/>')
                    hi.append(f'<circle cx="{px - rad * 0.3:.1f}" cy="{py - rad * 0.35:.1f}" r="{rad * 0.45:.1f}"/>')
        return (f'<g fill="#E9E0D4">{"".join(base)}</g><g fill="#D2C6B8" opacity="0.55">{"".join(sh)}</g>'
                f'<g fill="#FFFDF8" opacity="0.6">{"".join(hi)}</g>')
    out.append(fur([(300, 404), (300, 640)], r=(15, 25), seed=3, n=5))
    out.append(fur([(-30, 560), (630, 560)], r=(12, 22), seed=4, n=5))
    # belt
    belt = D.lg([(0, "#3A3230"), (0.18, "#1E1918"), (0.8, "#141010"), (1, "#060404")])
    out.append('<rect x="0" y="330" width="600" height="86" fill="#000" opacity="0.35" transform="translate(0 6)"/>')
    out.append(f'<rect x="0" y="326" width="600" height="86" fill="url(#{belt})"/>')
    out.append('<g fill="none" stroke="#5A4E48" stroke-width="2" stroke-dasharray="7 6"><line x1="0" y1="336" x2="600" y2="336"/><line x1="0" y1="402" x2="600" y2="402"/></g>')
    out.append('<rect x="0" y="328" width="600" height="4" fill="#FFFFFF" opacity="0.12"/>')
    # belt holes at the right
    out.append("".join(f'<ellipse cx="{x}" cy="369" rx="5" ry="6" fill="#050303"/><ellipse cx="{x}" cy="371" rx="4" ry="3" fill="#3A3230" opacity="0.6"/>' for x in (430, 462, 494)))
    # candy cane tucked behind the belt
    cc = []
    d = "M 120 470 L 120 300 Q 120 262 152 262 Q 184 262 184 294"
    cid = D.id("m")
    cc.append(f'<mask id="{cid}"><path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="20" stroke-linecap="round"/></mask>')
    stripes = "".join(f'<line x1="60" y1="{y}" x2="220" y2="{y - 80}" stroke="#C7343A" stroke-width="9"/>' for y in range(240, 560, 22))
    out.append(f'<g transform="translate(-6 46) rotate(-14 120 380)"><path d="{d}" fill="none" stroke="#000" stroke-width="22" stroke-linecap="round" opacity="0.25" transform="translate(5 5)"/>'
               f'{"".join(cc)}<path d="{d}" fill="none" stroke="#FBF6EE" stroke-width="20" stroke-linecap="round"/><g mask="url(#{cid})">{stripes}</g>'
               f'<path d="M 113 460 L 113 300 Q 113 268 140 266" fill="none" stroke="#FFFFFF" stroke-width="4" opacity="0.7" stroke-linecap="round"/></g>')
    # belt redrawn over the cane's lower half
    out.append(f'<rect x="60" y="326" width="120" height="86" fill="url(#{belt})"/><g fill="none" stroke="#5A4E48" stroke-width="2" stroke-dasharray="7 6"><line x1="60" y1="336" x2="180" y2="336"/><line x1="60" y1="402" x2="180" y2="402"/></g>')
    # buckle
    gb = D.lg([(0, "#FFF0B0"), (0.35, "#E9B949"), (0.7, "#B9821F"), (1, "#7A5212")], 0, 0, 1, 1)
    out.append('<rect x="226" y="302" width="148" height="134" rx="18" fill="#000" opacity="0.4" transform="translate(5 7)"/>')
    out.append(f'<rect x="226" y="302" width="148" height="134" rx="18" fill="url(#{gb})"/>')
    out.append('<rect x="250" y="326" width="100" height="86" rx="8" fill="url(#' + belt + ')"/>')
    out.append('<rect x="250" y="326" width="100" height="86" rx="8" fill="none" stroke="#7A5212" stroke-width="3"/>')
    out.append(f'<rect x="276" y="356" width="70" height="26" rx="4" fill="url(#{belt})"/>')
    out.append(f'<rect x="234" y="356" width="56" height="26" rx="4" fill="url(#{gb})"/>')
    out.append('<path d="M 234 310 L 366 310" stroke="#FFF8D8" stroke-width="3" opacity="0.8" stroke-linecap="round"/>'
               '<path d="M 232 314 L 232 420" stroke="#FFF8D8" stroke-width="3" opacity="0.55" stroke-linecap="round"/>')
    out.append(twinkle(240, 316, 12, "#FFFFFF") + f'<circle cx="240" cy="316" r="20" fill="url(#{D.glow("#FFF6D8", 0.6)})"/>')
    # jingle bell hanging from the belt
    bb = D.ball("#E2B04A")
    out.append('<path d="M 452 410 q -2 14 4 26" stroke="#2A1E18" stroke-width="3" fill="none"/>'
               f'<circle cx="458" cy="458" r="24" fill="url(#{bb})"/><path d="M 446 466 q 12 8 24 0" stroke="#5A3A10" stroke-width="3" fill="none"/>'
               '<circle cx="458" cy="472" r="4" fill="#3A2610"/><path d="M 438 446 q 4 -12 16 -14" stroke="#FFF6D0" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.8"/>')
    # type
    out.append(T(300, 120, "MERRY CHRISTMAS", MONO, 20, "#FCE3C8", ls=8, max_w=380))
    out.append('<g stroke="#FCE3C8" stroke-width="2" opacity="0.8"><line x1="62" y1="114" x2="102" y2="114"/><line x1="498" y1="114" x2="538" y2="114"/></g>')
    out.append(T(300, 276, "HO HO HO!", BEBAS, 170, "#5A0C12", ls=10, max_w=476, extra=' transform="translate(0 7)"'))
    out.append(T(300, 276, "HO HO HO!", BEBAS, 170, "#FBF3E6", ls=10, max_w=476))
    return D.svg() + "\n".join(out)


def cardinal(D, x, y, s=1.0, flip=False):
    """Northern cardinal perched, facing left; (x, y) = where the feet grip."""
    body = D.rg([(0, "#F0584A"), (0.5, "#C8262A"), (1, "#7E1218")], cx=0.38, cy=0.35, r=0.75)
    wing = D.lg([(0, "#B01E24"), (1, "#6E1016")], 0, 0, 1, 1)
    sx = -s if flip else s
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({sx} {s})">'
            # tail behind
            '<path d="M 34 -40 C 62 -20 86 10 104 44 L 92 52 C 74 22 52 -4 26 -22 Z" fill="#8E161C"/>'
            '<path d="M 34 -40 C 62 -20 86 10 104 44" fill="none" stroke="#C8343A" stroke-width="2" opacity="0.7"/>'
            '<path d="M 40 -30 C 64 -8 80 16 96 48" fill="none" stroke="#5E0C12" stroke-width="1.6" opacity="0.6"/>'
            # body + crest
            f'<path d="M -46 -112 C -50 -132 -36 -146 -18 -146 L -2 -170 L 6 -138 C 22 -128 30 -110 40 -86 C 50 -62 48 -38 30 -20 C 14 -6 -10 -4 -26 -18 C -44 -34 -50 -64 -48 -86 Z" fill="url(#{body})"/>'
            # breast light
            '<path d="M -44 -92 C -46 -64 -36 -34 -18 -20 C -30 -42 -36 -66 -34 -92 Z" fill="#F57A62" opacity="0.6"/>'
            # wing
            f'<path d="M -12 -104 C 14 -110 40 -90 48 -56 C 52 -40 46 -28 38 -22 C 30 -46 10 -72 -16 -84 Z" fill="url(#{wing})"/>'
            '<g fill="none" stroke="#4E080C" stroke-width="1.8" opacity="0.7" stroke-linecap="round"><path d="M 0 -96 C 18 -86 32 -66 40 -40"/><path d="M -8 -88 C 10 -76 24 -56 32 -32"/><path d="M 10 -100 C 26 -92 38 -76 44 -58"/></g>'
            '<path d="M -10 -104 C 12 -110 32 -98 42 -78" fill="none" stroke="#F5826E" stroke-width="2" opacity="0.6" stroke-linecap="round"/>'
            # mask + beak + eye
            '<path d="M -58 -124 C -50 -130 -36 -128 -28 -120 C -26 -110 -32 -98 -44 -92 C -54 -96 -60 -110 -58 -124 Z" fill="#1A0E0E"/>'
            '<path d="M -50 -126 C -60 -124 -72 -118 -78 -110 C -70 -106 -58 -104 -48 -104 Z" fill="#F2913A"/>'
            '<path d="M -50 -126 C -60 -124 -72 -118 -78 -110 L -50 -114 Z" fill="#FFC27A"/>'
            '<circle cx="-38" cy="-118" r="4" fill="#000"/><circle cx="-39.5" cy="-119.5" r="1.6" fill="#FFFFFF"/>'
            # crest highlight + rim light on the back
            '<path d="M -16 -144 L -4 -164" stroke="#FF8A72" stroke-width="2.2" stroke-linecap="round"/>'
            '<path d="M 8 -136 C 24 -124 32 -108 40 -88" fill="none" stroke="#FFB8A0" stroke-width="2.4" opacity="0.7" stroke-linecap="round"/>'
            # feet
            '<g stroke="#4A2E24" stroke-width="3" stroke-linecap="round" fill="none"><path d="M -14 -14 L -16 2 M -16 2 l -8 2 M -16 2 l 2 6"/><path d="M 4 -14 L 6 2 M 6 2 l -8 3 M 6 2 l 3 6"/></g>'
            "</g>")


def let_it_snow():
    u = "lis"
    D = Defs(u)
    out = []
    sky = D.lg([(0, "#6F8BA6"), (0.5, "#A9BDCB"), (1, "#E6ECEC")])
    out.append(f'<rect width="600" height="600" fill="url(#{sky})"/>')
    # distant snowy forest, hazy
    poly, line = pt.ridge_poly([(-10, 470), (150, 452), (320, 466), (470, 448), (610, 462)], 7, amp=6, base=600, fill="#C6D3DB")
    out.append(pt.tree_line(line, 3, ["#94A9B8", "#8AA0B0", "#A0B3C0"], density=1.8, hmin=40, hmax=110, sink=6))
    out.append(poly)
    out.append(pt.tree_line([(-10, 520), (610, 515)], 4, ["#7E96A8", "#748DA0"], density=1.0, hmin=60, hmax=140, sink=6))
    out.append(f'<rect x="0" y="380" width="600" height="220" fill="url(#{D.lg([(0, "#E6ECEC", 0), (1, "#E6ECEC", 0.7)])})"/>')
    out.append(soft_flakes(D, 6, 26, r=(6, 14), s=0.6, avoid=[(60, 60, 540, 300)]))
    # type
    navy = "#21364E"
    out.append(T(300, 128, "let it", SERIF_IT, 96, CRAN, max_w=300))
    sz = fit_size("SNOW", BEBAS, 188, 440, 22)
    base = 290
    out.append(T(300, base + 5, "SNOW", BEBAS, 188, "#0E1C2C", ls=22, max_w=440, extra=' opacity="0.25"'))
    out.append(T(300, base, "SNOW", BEBAS, 188, navy, ls=22, max_w=440))
    # snow resting on the letters
    w = measure("SNOW", BEBAS, sz, 22)
    x = 300 - w / 2 + 11
    top = base - sz * 0.7
    rnd = random.Random(2)
    for ch in "SNOW":
        adv = measure(ch, BEBAS, sz)
        cx_ = x + adv / 2
        pts = [(cx_ - adv * 0.44 + i * adv * 0.88 / 6, top + 1) for i in range(7)]
        out.append(snow_cap(pts, thick=11, seed=rnd.randint(0, 99)))
        x += adv + 22
    # branch with needles and snow
    br = [(-30, 504), (100, 486), (220, 474), (330, 466), (450, 452), (630, 432)]
    out.append(f'<path d="M {P(br).replace(" ", " L ")}" fill="none" stroke="#3E2A20" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<path d="M {P([(x_, y_ - 3) for x_, y_ in br]).replace(" ", " L ")}" fill="none" stroke="#7A5A44" stroke-width="3" stroke-linecap="round" opacity="0.8"/>')
    out.append('<path d="M 160 480 Q 190 506 214 526" stroke="#3E2A20" stroke-width="6" fill="none" stroke-linecap="round"/><path d="M 470 450 Q 500 472 528 480" stroke="#3E2A20" stroke-width="6" fill="none" stroke-linecap="round"/>')
    needles = []
    rnd = random.Random(8)
    for i in range(520):
        t = rnd.random()
        bx = -20 + t * 640
        by = y_on(br, bx) or 470
        if 290 < bx < 380 and rnd.random() < 0.7:
            continue
        a = rnd.uniform(-160, -20) if rnd.random() < 0.55 else rnd.uniform(20, 160)
        L = rnd.uniform(14, 30)
        col = rnd.choice(["#1E4A38", "#2A5E46", "#163A2C", "#3E7456"])
        needles.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx + L * math.cos(math.radians(a)):.1f}" y2="{by + L * math.sin(math.radians(a)):.1f}" stroke="{col}"/>')
    out.append(f'<g stroke-width="2.4" stroke-linecap="round">{"".join(needles)}</g>')
    out.append(snow_cap([(x_, (y_on(br, x_) or 470) - 14) for x_ in range(-20, 290, 14)], thick=14, seed=3))
    out.append(snow_cap([(x_, (y_on(br, x_) or 470) - 14) for x_ in range(380, 625, 14)], thick=14, seed=4))
    out.append(cardinal(D, 330, 466, 0.98))
    # red berries
    for bx, by in ((420, 480), (432, 488), (426, 472), (150, 504), (138, 512)):
        out.append(f'<circle cx="{bx}" cy="{by}" r="7" fill="url(#{D.ball("#C7262E")})"/>')
    out.append(snowfall(12, 160, r=(1.2, 3.6), op=(0.6, 1)))
    return D.svg() + "\n".join(out)


def mitten(D, x, y, s, rot, col, accent, seed=1):
    """Knitted mitten, cuff at the bottom; (x, y) = cuff centre."""
    g = D.lg([(0, lt(col, 0.15)), (1, dk(col, 0.25))], 0, 0, 1, 0)
    shape = "M -34 0 L -36 -84 C -38 -124 -16 -142 6 -140 C 30 -138 40 -116 38 -84 L 36 0 Z"
    thumb = "M -36 -62 C -52 -66 -66 -82 -62 -98 C -58 -110 -46 -108 -40 -96 L -36 -84 Z"
    c = D.clip(f'<path d="{shape}"/><path d="{thumb}"/>')
    knit = "".join(f'<path d="M {xx} {yy} l 4 5 l 4 -5" />' for xx in range(-44, 44, 8) for yy in range(-150, 0, 7))
    flake = "".join(f'<line x1="2" y1="-74" x2="{2 + 18 * math.cos(math.radians(a)):.1f}" y2="{-74 + 18 * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 60))
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">'
            f'<path d="{shape}" fill="#000" opacity="0.2" transform="translate(6 8)"/>'
            f'<path d="{thumb}" fill="url(#{g})"/><path d="{shape}" fill="url(#{g})"/>'
            f'<g clip-path="url(#{c})"><g fill="none" stroke="{dk(col, 0.25)}" stroke-width="1.6" opacity="0.55">{knit}</g>'
            f'<g stroke="{accent}" stroke-width="4" stroke-linecap="round">{flake}</g>'
            f'<g fill="{accent}">' + "".join(f'<rect x="{xx}" y="-38" width="7" height="7" transform="rotate(45 {xx + 3.5} -34.5)"/>' for xx in range(-34, 40, 14)) + "</g>"
            f'<path d="M -40 -150 L -20 -150 L -20 0 L -40 0 Z" fill="#FFFFFF" opacity="0.12"/></g>'
            f'<rect x="-38" y="-6" width="76" height="34" rx="6" fill="{accent}"/>'
            f'<g stroke="{dk(accent, 0.15)}" stroke-width="2.4">' + "".join(f'<line x1="{xx}" y1="-4" x2="{xx}" y2="26"/>' for xx in range(-32, 36, 7)) + "</g>"
            "</g>")


def hot_cocoa_season():
    u = "hcs"
    D = Defs(u)
    out = []
    wall = D.lg([(0, "#FBF3E6"), (1, "#EEDFC8")])
    out.append(f'<rect width="600" height="410" fill="url(#{wall})"/>')
    out.append(speck(3, 220, "#A24A3A", box=(0, 0, 600, 410), op=(0.08, 0.22)))
    # tiny snowflake wallpaper sprigs
    out.append('<g stroke="#D9C2A6" stroke-width="2" stroke-linecap="round" opacity="0.8">' + "".join(
        "".join(f'<line x1="{x}" y1="{y}" x2="{x + 7 * math.cos(math.radians(a)):.1f}" y2="{y + 7 * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 60))
        for x in range(30, 600, 90) for y in (40, 300) if not (60 < x < 540 and y < 290)) + "</g>")
    # plaid tablecloth
    out.append(plaid_bg(D, "#A6262F", [("#1F4A38", 10, 26, 0.55), ("#1F4A38", 42, 8, 0.45), ("#E9B949", 52, 3, 0.7), ("#5A0E14", 0, 6, 0.3)],
                        box=(0, 404, 600, 600), step=64, vscale=0.6))
    out.append('<rect x="0" y="404" width="600" height="8" fill="#000" opacity="0.15"/>')
    out.append(f'<rect x="0" y="404" width="600" height="196" fill="url(#{D.lg([(0, "#000", 0.25), (0.4, "#000", 0), (1, "#000", 0.25)])})"/>')
    # mittens lying to the right
    out.append(mitten(D, 470, 536, 0.84, -76, "#1F5A44", "#F6EDE0"))
    out.append(mitten(D, 494, 500, 0.84, -34, "#B42A30", "#F6EDE0"))
    # mug
    cx, top, bot, rx = 262, 330, 500, 84
    body = D.lg([(0, "#D8C8B2"), (0.18, "#FFFBF4"), (0.55, "#F1E6D6"), (0.85, "#C9B49A"), (1, "#A8917A")], 0, 0, 1, 0)
    out.append(f'<ellipse cx="{cx + 20}" cy="{bot + 6}" rx="{rx + 40}" ry="20" fill="#000" opacity="0.28"/>')
    # handle
    out.append(f'<path d="M {cx + rx - 4} {top + 40} C {cx + rx + 66} {top + 30} {cx + rx + 70} {top + 128} {cx + rx - 6} {top + 126}" fill="none" stroke="#B9A48A" stroke-width="30" stroke-linecap="round"/>'
               f'<path d="M {cx + rx - 4} {top + 40} C {cx + rx + 66} {top + 30} {cx + rx + 70} {top + 128} {cx + rx - 6} {top + 126}" fill="none" stroke="#F4EBDD" stroke-width="20" stroke-linecap="round"/>'
               f'<path d="M {cx + rx + 10} {top + 44} C {cx + rx + 50} {top + 46} {cx + rx + 52} {top + 100} {cx + rx + 20} {top + 112}" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity="0.8"/>')
    mug = f"M {cx - rx} {top} L {cx - rx + 6} {bot - 12} Q {cx - rx + 8} {bot + 14} {cx} {bot + 14} Q {cx + rx - 8} {bot + 14} {cx + rx - 6} {bot - 12} L {cx + rx} {top} Z"
    out.append(f'<path d="{mug}" fill="url(#{body})"/>')
    c = D.clip(f'<path d="{mug}"/>')
    band = D.lg([(0, "#D8424A"), (0.5, "#B42A30"), (1, "#7E161C")], 0, 0, 1, 0)
    pat = (f'<rect x="{cx - rx}" y="{top + 58}" width="{2 * rx}" height="58" fill="url(#{band})"/>'
           + "".join(f'<rect x="{x - 6}" y="{top + 81}" width="12" height="12" transform="rotate(45 {x} {top + 87})" fill="#FBF3E6"/>' for x in range(cx - rx + 10, cx + rx, 26))
           + "".join(f'<circle cx="{x}" cy="{top + 87}" r="2.4" fill="#FBF3E6"/>' for x in range(cx - rx + 23, cx + rx, 26))
           + f'<g stroke="#FBF3E6" stroke-width="2.4"><line x1="{cx - rx}" y1="{top + 66}" x2="{cx + rx}" y2="{top + 66}"/><line x1="{cx - rx}" y1="{top + 108}" x2="{cx + rx}" y2="{top + 108}"/></g>'
           + "".join(f'<path d="M {x} {top + 128} l 6 -9 l 6 9 Z" fill="#B42A30"/>' for x in range(cx - rx, cx + rx, 18))
           + f'<rect x="{cx - rx}" y="{top}" width="{2 * rx}" height="{bot - top + 20}" fill="url(#{D.lg([(0, "#000", 0), (0.6, "#000", 0), (1, "#000", 0.25)], 0, 0, 1, 0)})"/>')
    out.append(f'<g clip-path="url(#{c})">{pat}</g>')
    out.append(f'<path d="M {cx - rx + 14} {top + 14} L {cx - rx + 18} {bot - 10}" stroke="#FFFFFF" stroke-width="7" opacity="0.55" stroke-linecap="round"/>')
    # rim + cocoa
    cocoa = D.rg([(0, "#8A5232"), (0.7, "#5E321C"), (1, "#3A1E10")], cx=0.45, cy=0.4)
    out.append(f'<ellipse cx="{cx}" cy="{top}" rx="{rx}" ry="17" fill="#F7EFE3"/><ellipse cx="{cx}" cy="{top + 1}" rx="{rx - 7}" ry="12.5" fill="url(#{cocoa})"/>')
    out.append(f'<path d="M {cx - rx + 4} {top + 2} Q {cx} {top + 22} {cx + rx - 4} {top + 2}" fill="none" stroke="#D6C6B0" stroke-width="2"/>')
    # marshmallows bobbing
    for mx, my, r_, w_ in ((cx - 40, top - 6, -14, 30), (cx - 6, top - 12, 8, 32), (cx + 30, top - 4, -6, 28), (cx - 22, top + 2, 20, 26), (cx + 52, top - 2, 14, 22)):
        out.append(f'<g transform="rotate({r_} {mx} {my})"><rect x="{mx - w_ / 2}" y="{my - w_ * 0.45}" width="{w_}" height="{w_ * 0.8:.1f}" rx="7" fill="#FFFDF8"/>'
                   f'<rect x="{mx - w_ / 2}" y="{my + w_ * 0.1:.1f}" width="{w_}" height="{w_ * 0.25:.1f}" rx="5" fill="#E8DCCB"/>'
                   f'<rect x="{mx - w_ / 2 + 3}" y="{my - w_ * 0.45 + 3:.1f}" width="{w_ * 0.4:.1f}" height="5" rx="2.5" fill="#FFFFFF"/>'
                   f'<path d="M {mx + w_ / 2 - 6} {my - w_ * 0.45 + 2:.1f} q 4 6 2 12" stroke="#D9A86A" stroke-width="3" fill="none" opacity="0.7"/></g>')
    out.append(dots(26, 5, (cx - 60, top - 18, cx + 64, top + 8), "#7A4428", r=(0.8, 1.8), opacity=(0.5, 0.9)))
    # candy cane in the mug
    d = f"M {cx + 46} {top + 4} L {cx + 58} {top - 58} Q {cx + 64} {top - 86} {cx + 90} {top - 80} Q {cx + 114} {top - 72} {cx + 106} {top - 48}"
    mid = D.id("m")
    out.append(f'<mask id="{mid}"><path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="13" stroke-linecap="round"/></mask>'
               f'<path d="{d}" fill="none" stroke="#FBF6EE" stroke-width="13" stroke-linecap="round"/>'
               f'<g mask="url(#{mid})">' + "".join(f'<line x1="{cx}" y1="{y}" x2="{cx + 160}" y2="{y - 90}" stroke="#C7343A" stroke-width="7"/>' for y in range(top - 160, top + 120, 16)) + "</g>"
               f'<path d="M {cx + 42} {top - 4} L {cx + 53} {top - 56}" stroke="#FFFFFF" stroke-width="3" opacity="0.6" stroke-linecap="round"/>')
    out.append(f'<ellipse cx="{cx + 46}" cy="{top + 1}" rx="8" ry="4" fill="#5E321C"/>')
    out.append(steam(D, cx - 14, top - 22, 76, 4, col="#C9B49A", n=3, spread=30, op=0.45, w=14))
    out.append(steam(D, cx - 14, top - 22, 76, 4, col="#FFFFFF", n=3, spread=30, op=1, w=8))
    # type
    out.append(T(300, 128, "hot cocoa", SERIF_IT, 100, CRAN, max_w=470))
    out.append(T(300, 236, "SEASON", BEBAS, 118, PINE, ls=16, max_w=440))
    out.append('<g fill="#E2B04A">' + twinkle(118, 226, 10, "#D9A441") + twinkle(482, 226, 10, "#D9A441") + "</g>")
    return D.svg() + "\n".join(out)


def naughty_or_nice():
    u = "non"
    D = Defs(u)
    out = []
    bg = D.rg([(0, "#24624A"), (0.7, "#173F30"), (1, "#0D2A1F")], cy=0.45, r=0.75)
    out.append(f'<rect width="600" height="600" fill="url(#{bg})"/>')
    rnd = random.Random(3)
    out.append('<g fill="#E2B04A" opacity="0.28">' + "".join(f'<polygon points="{star_points(x + (22 if (y // 60) % 2 else 0), y, 6, 2.6)}"/>' for x in range(10, 620, 60) for y in range(10, 620, 60)) + "</g>")
    # parchment
    par = D.rg([(0, "#FBF1DC"), (0.7, "#F0DFBE"), (1, "#D9BE8E")], cx=0.45, cy=0.45, r=0.7)
    L, R, top, bot = 112, 488, 100, 500
    edge = rough([(L, top), (L - 4, (top + bot) / 2), (L, bot)], 3, amp=6, depth=4)
    edge2 = rough([(R, bot), (R + 4, (top + bot) / 2), (R, top)], 4, amp=6, depth=4)
    poly = edge + edge2
    out.append(f'<polygon points="{P([(x + 10, y + 12) for x, y in poly])}" fill="#000" opacity="0.3"/>')
    out.append(f'<polygon points="{P(poly)}" fill="url(#{par})"/>')
    c = D.clip(f'<polygon points="{P(poly)}"/>')
    out.append(f'<g clip-path="url(#{c})">' + pt.blobs(18, 7, (L, top, R, bot), ["#D9B98A", "#E8CFA4"], r=(10, 34), opacity=(0.15, 0.35), squash=0.8)
               + '<g stroke="#C9A97A" stroke-width="1.5" opacity="0.55">' + "".join(f'<line x1="{L + 20}" y1="{y}" x2="{R - 20}" y2="{y}"/>' for y in range(190, 480, 34)) + "</g>"
               + "</g>")
    # rolls at top and bottom
    roll = D.lg([(0, "#B8955E"), (0.35, "#FBF0D6"), (0.6, "#E8D3A8"), (1, "#8A6A3A")])
    for y0, flip in ((top - 22, 1), (bot - 14, -1)):
        out.append(f'<rect x="{L - 18}" y="{y0}" width="{R - L + 36}" height="38" rx="19" fill="url(#{roll})"/>')
        out.append(f'<ellipse cx="{R + 18 - 4}" cy="{y0 + 19}" rx="9" ry="19" fill="#C9A670"/><ellipse cx="{R + 18 - 4}" cy="{y0 + 19}" rx="5" ry="11" fill="#7A5A30"/>')
        out.append(f'<ellipse cx="{L - 18 + 4}" cy="{y0 + 19}" rx="9" ry="19" fill="#E8D3A8"/><path d="M {L - 14} {y0 + 19} m -3 0 a 4 9 0 1 0 8 0 a 2 5 0 1 0 -4 0" fill="none" stroke="#8A6A3A" stroke-width="2"/>')
    # ink type
    ink = "#3A2418"
    out.append(T(300, 172, "SANTA'S LIST", CINZEL, 40, "#8E2234", ls=5, max_w=330))
    out.append('<g stroke="#8E2234" stroke-width="2"><line x1="140" y1="186" x2="460" y2="186"/><line x1="160" y1="192" x2="440" y2="192" opacity="0.5"/></g>')

    def box(x, y, checked):
        s = f'<path d="M {x} {y} q 26 -3 52 1 q 3 26 -1 52 q -26 2 -52 -1 q -2 -26 1 -52 Z" fill="none" stroke="{ink}" stroke-width="4.5" stroke-linejoin="round"/>'
        if checked:
            s += (f'<path d="M {x + 8} {y + 26} Q {x + 18} {y + 36} {x + 24} {y + 48} Q {x + 40} {y + 10} {x + 74} {y - 22}" fill="none" stroke="#B8312F" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
                  f'<path d="M {x + 26} {y + 40} Q {x + 42} {y + 8} {x + 70} {y - 18}" fill="none" stroke="#E86A5E" stroke-width="2.5" stroke-linecap="round" opacity="0.7"/>')
        return s
    out.append(box(146, 222, False))
    out.append(T(222, 274, "NAUGHTY", BEBAS, 92, ink, ls=4, anchor="start", max_w=250))
    out.append(box(146, 318, True))
    out.append(T(222, 370, "NICE", BEBAS, 92, "#B8312F", ls=4, anchor="start", max_w=250))
    out.append(T(300, 446, "(mostly)", SERIF_IT, 56, ink, max_w=300))
    # an ink blot and a scribble crossing-out
    out.append(f'<path d="M 364 238 q 30 -8 60 4 q -28 6 -56 6 q 30 4 58 8" fill="none" stroke="{ink}" stroke-width="3" opacity="0.35"/>')
    out.append(f'<circle cx="430" cy="300" r="6" fill="{ink}" opacity="0.6"/><circle cx="440" cy="306" r="2.6" fill="{ink}" opacity="0.6"/>')
    # quill
    q = D.lg([(0, "#FFFFFF"), (1, "#D8CBB8")], 0, 0, 1, 0)
    out.append('<g transform="translate(468 444) rotate(-38)">'
               '<path d="M 0 0 C -16 -40 -14 -120 6 -190 C 26 -120 26 -40 6 0 Z" fill="#000" opacity="0.25" transform="translate(8 6)"/>'
               f'<path d="M 0 0 C -16 -40 -14 -120 6 -190 C 26 -120 26 -40 6 0 Z" fill="url(#{q})"/>'
               '<path d="M 3 10 L 3 -186" stroke="#B8A890" stroke-width="2.4"/>'
               '<g stroke="#C9BBA6" stroke-width="1.4" opacity="0.8">' + "".join(f'<line x1="3" y1="{-y}" x2="{-10 + y * 0.02:.1f}" y2="{-y - 14}"/><line x1="3" y1="{-y}" x2="{16 - y * 0.02:.1f}" y2="{-y - 14}"/>' for y in range(20, 180, 9)) + "</g>"
               '<path d="M 0 0 L 3 26 L 6 0 Z" fill="#2A1E18"/></g>')
    # wax seal
    out.append(f'<circle cx="150" cy="474" r="30" fill="#000" opacity="0.25" transform="translate(4 5)"/>'
               f'<path d="M 150 444 q 12 2 20 8 q 10 10 9 22 q -1 14 -12 22 q -10 7 -20 6 q -14 -2 -22 -12 q -8 -12 -4 -26 q 6 -16 29 -20 Z" fill="url(#{D.ball("#A8242E")})"/>'
               f'<circle cx="150" cy="474" r="18" fill="none" stroke="#7A141C" stroke-width="2.5"/><polygon points="{star_points(150, 474, 11, 4.6)}" fill="#7A141C"/>')
    return D.svg() + "\n".join(out)


def joy_to_the_world():
    u = "joy"
    D = Defs(u)
    out = []
    sky = D.lg([(0, "#0B1630"), (0.5, "#1B2E58"), (0.8, "#3A4A7C"), (1, "#6A6A94")])
    out.append(f'<rect width="600" height="600" fill="url(#{sky})"/>')
    out.append(dots(160, 2, (0, 0, 600, 420), "#F6EDE0", r=(0.6, 1.8), opacity=(0.3, 1)))
    # beam of light from the star to the stable
    beam = D.lg([(0, "#FFE7A8", 0.45), (1, "#FFE7A8", 0)])
    out.append(f'<polygon points="300,120 268,520 332,520" fill="url(#{beam})"/>')
    # star
    out.append(f'<circle cx="300" cy="118" r="150" fill="url(#{D.glow("#FFE7A8", 0.55)})"/>')
    out.append(f'<circle cx="300" cy="118" r="60" fill="url(#{D.glow("#FFFFFF", 0.7)})"/>')
    rays = []
    for a, L, w in ((-90, 70, 7), (90, 130, 7), (0, 76, 6), (180, 76, 6), (-45, 40, 4), (45, 40, 4), (135, 40, 4), (-135, 40, 4)):
        ra = math.radians(a)
        px, py = -math.sin(ra) * w, math.cos(ra) * w
        rays.append(f'<polygon points="{300 + px:.1f},{118 + py:.1f} {300 + L * math.cos(ra):.1f},{118 + L * math.sin(ra):.1f} {300 - px:.1f},{118 - py:.1f}" fill="#FFF3C8"/>')
    out.append("".join(rays))
    out.append(f'<circle cx="300" cy="118" r="10" fill="#FFFFFF"/>')
    # type
    gold = D.lg([(0, "#FFF0B8"), (0.5, "#E9B949"), (1, "#B37A1E")])
    out.append(T(300, 340, "JOY", CINZEL, 190, "#050B1A", ls=16, max_w=440, extra=' transform="translate(0 7)" opacity="0.6"'))
    out.append(T(300, 340, "JOY", CINZEL, 190, f"url(#{gold})", ls=16, max_w=440))
    out.append(T(300, 416, "to the world", SERIF_IT, 62, "#F6EDE0", max_w=400))
    # hills: far ridge with travellers, village, near hill with olive trees
    poly, far = pt.ridge_poly([(-10, 452), (120, 440), (250, 448), (380, 436), (610, 450)], 5, amp=4, base=600, fill="#2B3560")
    out.append(poly)
    # three travellers on camels on the far ridge
    for i, cxp in enumerate((470, 500, 532)):
        yb = (y_on(far, cxp) or 444) + 1
        out.append(f'<g transform="translate({cxp} {yb}) scale(-0.6 0.6)" fill="#141B38">'
                   '<path d="M -18 0 L -16 -18 Q -20 -30 -10 -34 Q 0 -44 10 -34 Q 16 -30 18 -24 L 26 -32 Q 30 -40 34 -34 L 32 -24 Q 26 -18 22 -16 L 20 0 L 16 0 L 14 -14 L -10 -14 L -12 0 Z"/>'
                   '<path d="M -4 -38 L -2 -54 Q 2 -60 6 -54 L 8 -38 Z"/><circle cx="2" cy="-60" r="5"/></g>')
    poly, mid = pt.ridge_poly([(-10, 500), (160, 478), (300, 488), (460, 472), (610, 490)], 6, amp=4, base=600, fill="#1A2248")
    out.append(poly)
    # flat-roofed village with lamp-lit windows
    rnd = random.Random(5)
    for x, w, h in ((370, 30, 26), (398, 24, 34), (424, 36, 22), (462, 26, 30), (490, 32, 20), (88, 28, 24), (114, 22, 32)):
        yb = (y_on(mid, x + w / 2) or 485) + 4
        out.append(f'<rect x="{x}" y="{yb - h:.1f}" width="{w}" height="{h + 6}" fill="#232C56"/><rect x="{x}" y="{yb - h:.1f}" width="{w}" height="3" fill="#3A4678"/>')
        for _ in range(2):
            if rnd.random() < 0.8:
                out.append(f'<rect x="{x + rnd.uniform(4, w - 9):.1f}" y="{yb - h + rnd.uniform(6, h - 10):.1f}" width="5" height="6" fill="#F7C873"/>')
    # stable in the centre, glowing
    sx, sy = 300, (y_on(mid, 300) or 488) + 6
    out.append(f'<circle cx="{sx}" cy="{sy - 20}" r="70" fill="url(#{D.glow("#FFC86A", 0.6)})"/>')
    out.append(f'<path d="M {sx - 40} {sy} L {sx - 40} {sy - 36} L {sx} {sy - 62} L {sx + 40} {sy - 36} L {sx + 40} {sy} Z" fill="#2A2440"/>'
               f'<path d="M {sx - 48} {sy - 32} L {sx} {sy - 68} L {sx + 48} {sy - 32}" fill="none" stroke="#4A3E5A" stroke-width="6" stroke-linejoin="round"/>'
               f'<path d="M {sx - 18} {sy} L {sx - 18} {sy - 30} Q {sx} {sy - 42} {sx + 18} {sy - 30} L {sx + 18} {sy} Z" fill="#FFC86A"/>'
               f'<path d="M {sx - 12} {sy} L {sx - 10} {sy - 14} L {sx + 10} {sy - 14} L {sx + 12} {sy} Z" fill="#E09A3A"/>'
               f'<polygon points="{sx - 18},{sy} {sx + 18},{sy} {sx + 34},{sy + 14} {sx - 34},{sy + 14}" fill="#FFC86A" opacity="0.35"/>')
    poly, near = pt.ridge_poly([(-10, 528), (140, 512), (300, 530), (450, 514), (610, 526)], 8, amp=5, base=600, fill="#0F1530")
    out.append(poly)
    # olive trees and a palm in silhouette on the near hill
    for x, s in ((86, 1.0), (520, 1.15)):
        yb = (y_on(near, x) or 520) + 2
        out.append(f'<g fill="#0F1530"><path d="M {x - 3} {yb} L {x - 2} {yb - 24 * s:.1f} L {x + 2} {yb - 24 * s:.1f} L {x + 3} {yb} Z"/>'
                   + "".join(f'<ellipse cx="{x + dx * s:.1f}" cy="{yb - (30 + dy) * s:.1f}" rx="{16 * s:.1f}" ry="{10 * s:.1f}"/>' for dx, dy in ((-12, 0), (10, -2), (0, 8), (-4, -8), (14, 8))) + "</g>")
    return D.svg() + "\n".join(out)


def toucan(D, x, y, s=1.0):
    """Toco toucan perched facing left in a Santa hat; (x, y) = feet on the branch."""
    beak = D.lg([(0, "#F7A23A"), (0.55, "#F4C04A"), (1, "#E8742A")], 0, 0, 1, 1)
    body = D.rg([(0, "#3A3A44"), (0.6, "#16161C"), (1, "#050508")], cx=0.35, cy=0.3, r=0.75)
    bib = D.rg([(0, "#FFFBEA"), (0.7, "#FBEFC4"), (1, "#E8D49A")], cx=0.4, cy=0.4)
    hat = D.lg([(0, "#E0484A"), (1, "#9A1C22")], 0, 0, 1, 1)
    return (f'<g transform="translate({x} {y}) scale({s})">'
            # tail
            '<path d="M 10 -40 C 20 -14 30 14 38 40 L 18 44 C 14 20 4 -4 -6 -30 Z" fill="#101016"/>'
            # body
            f'<path d="M -38 -150 C -54 -120 -50 -60 -30 -28 C -14 -4 16 -2 30 -30 C 42 -60 36 -120 18 -156 C 4 -180 -28 -174 -38 -150 Z" fill="url(#{body})"/>'
            # sheen on wing
            '<path d="M 18 -140 C 34 -104 34 -64 22 -36" fill="none" stroke="#5A6A8A" stroke-width="4" opacity="0.6" stroke-linecap="round"/>'
            '<path d="M 6 -120 C 20 -90 20 -60 12 -40" fill="none" stroke="#3A4660" stroke-width="3" opacity="0.6" stroke-linecap="round"/>'
            # undertail red
            '<path d="M -10 -24 C 0 -12 18 -12 26 -26 C 18 -14 4 -8 -10 -24 Z" fill="#D8262E"/>'
            '<ellipse cx="8" cy="-24" rx="16" ry="7" fill="#D8262E"/>'
            # white bib
            f'<path d="M -40 -160 C -52 -140 -48 -112 -34 -98 C -24 -112 -14 -136 -12 -160 C -20 -170 -34 -170 -40 -160 Z" fill="url(#{bib})"/>'
            '<path d="M -38 -100 C -30 -96 -22 -100 -18 -106" fill="none" stroke="#E8B43A" stroke-width="4" stroke-linecap="round"/>'
            # beak
            f'<path d="M -30 -176 C -60 -186 -110 -184 -150 -156 C -152 -152 -148 -148 -144 -149 C -100 -150 -60 -146 -32 -148 Z" fill="url(#{beak})"/>'
            '<path d="M -30 -176 C -60 -186 -110 -184 -150 -156" fill="none" stroke="#E8562A" stroke-width="3.5" stroke-linecap="round"/>'
            '<path d="M -150 -156 C -138 -166 -124 -168 -116 -162 C -122 -154 -134 -150 -146 -149 Z" fill="#1A1414"/>'
            '<path d="M -34 -160 C -60 -162 -96 -160 -132 -154" fill="none" stroke="#C8622A" stroke-width="2" opacity="0.6"/>'
            '<path d="M -40 -174 C -70 -178 -100 -174 -124 -164" fill="none" stroke="#FFE6A0" stroke-width="3" opacity="0.8" stroke-linecap="round"/>'
            '<path d="M -30 -176 L -28 -150" stroke="#1A1414" stroke-width="5" stroke-linecap="round"/>'
            # eye with blue skin
            '<ellipse cx="-12" cy="-166" rx="12" ry="10" fill="#4A9AD8"/><circle cx="-12" cy="-166" r="5.5" fill="#08080C"/><circle cx="-14" cy="-168" r="2" fill="#FFFFFF"/>'
            # feet
            '<g stroke="#5A7A9A" stroke-width="4.5" stroke-linecap="round" fill="none"><path d="M -12 -24 L -14 0 M -14 0 l -10 2 M -14 0 l 4 7"/><path d="M 6 -26 L 8 0 M 8 0 l -10 3 M 8 0 l 4 7"/></g>'
            # santa hat
            f'<path d="M -34 -186 C -30 -232 10 -250 50 -232 C 70 -222 82 -200 78 -176 C 66 -196 46 -206 24 -204 L 18 -186 Z" fill="url(#{hat})"/>'
            '<path d="M 10 -238 C 40 -244 66 -226 76 -196" fill="none" stroke="#F07070" stroke-width="3" opacity="0.6" stroke-linecap="round"/>'
            '<path d="M -44 -190 C -20 -204 8 -204 26 -190 C 28 -180 24 -174 18 -172 C 0 -184 -24 -184 -40 -174 C -48 -176 -50 -184 -44 -190 Z" fill="#FBF6EE"/>'
            '<path d="M -40 -178 C -22 -188 4 -188 20 -176" fill="none" stroke="#D9CFC2" stroke-width="3"/>'
            '<circle cx="80" cy="-172" r="14" fill="#FBF6EE"/><circle cx="84" cy="-168" r="8" fill="#E2D8CA"/><circle cx="76" cy="-176" r="5" fill="#FFFFFF"/>'
            "</g>")


def leaf(D, x, y, L, w, rot, col, seed, kind="banana"):
    """Painted tropical leaf from its stem base (x, y) pointing along rot (deg)."""
    g = D.lg([(0, lt(col, 0.18)), (1, dk(col, 0.3))], 0, 0, 0, 1)
    rnd = random.Random(seed)
    if kind == "banana":
        out = [f'<path d="M 0 0 C {L * 0.3:.1f} {-w:.1f} {L * 0.8:.1f} {-w * 0.9:.1f} {L:.1f} 0 C {L * 0.8:.1f} {w * 0.8:.1f} {L * 0.3:.1f} {w:.1f} 0 0 Z" fill="url(#{g})"/>',
               f'<path d="M 0 0 C {L * 0.3:.1f} {-w:.1f} {L * 0.8:.1f} {-w * 0.9:.1f} {L:.1f} 0 Z" fill="#FFFFFF" opacity="0.1"/>']
        for i in range(1, 14):
            t = i / 14
            out.append(f'<path d="M {L * t:.1f} 0 q {L * 0.04:.1f} {-w * 0.5:.1f} {L * 0.09:.1f} {-w * 0.85 * math.sin(math.pi * min(1, t + 0.06)):.1f}" fill="none" stroke="{dk(col, 0.35)}" stroke-width="1.6" opacity="0.6"/>')
            out.append(f'<path d="M {L * t:.1f} 0 q {L * 0.04:.1f} {w * 0.5:.1f} {L * 0.09:.1f} {w * 0.8 * math.sin(math.pi * min(1, t + 0.06)):.1f}" fill="none" stroke="{dk(col, 0.35)}" stroke-width="1.6" opacity="0.6"/>')
        # a couple of splits in the blade
        for _ in range(2):
            t = rnd.uniform(0.3, 0.8)
            out.append(f'<path d="M {L * t:.1f} {-w * 0.15:.1f} L {L * (t + 0.08):.1f} {-w * 0.9 * math.sin(math.pi * t):.1f}" stroke="#F6EDE0" stroke-width="3"/>')
        out.append(f'<path d="M 0 0 Q {L * 0.5:.1f} -3 {L:.1f} 0" fill="none" stroke="{lt(col, 0.45)}" stroke-width="3.5" stroke-linecap="round"/>')
    else:  # monstera-ish heart leaf with holes
        out = [f'<path d="M 0 0 C {-w * 0.2:.1f} {-L * 0.2:.1f} {-w:.1f} {-L * 0.3:.1f} {-w * 0.9:.1f} {-L * 0.65:.1f} C {-w * 0.8:.1f} {-L * 0.95:.1f} {-w * 0.2:.1f} {-L * 1.05:.1f} 0 {-L:.1f} '
               f'C {w * 0.2:.1f} {-L * 1.05:.1f} {w * 0.8:.1f} {-L * 0.95:.1f} {w * 0.9:.1f} {-L * 0.65:.1f} C {w:.1f} {-L * 0.3:.1f} {w * 0.2:.1f} {-L * 0.2:.1f} 0 0 Z" fill="url(#{g})"/>']
        for i in range(1, 6):
            t = i / 6
            for sg in (-1, 1):
                out.append(f'<path d="M 0 {-L * t:.1f} Q {sg * w * 0.4:.1f} {-L * t + 4:.1f} {sg * w * 0.8:.1f} {-L * t + L * 0.08:.1f}" fill="none" stroke="{dk(col, 0.3)}" stroke-width="2" opacity="0.6"/>')
                out.append(f'<ellipse cx="{sg * w * 0.45:.1f}" cy="{-L * t + L * 0.07:.1f}" rx="{w * 0.07:.1f}" ry="{L * 0.03:.1f}" fill="#F6EDE0" transform="rotate({sg * -20} {sg * w * 0.45:.1f} {-L * t + L * 0.07:.1f})"/>')
        out.append(f'<path d="M 0 0 L 0 {-L * 0.98:.1f}" stroke="{lt(col, 0.4)}" stroke-width="3"/>')
    return f'<g transform="translate({x} {y}) rotate({rot})">' + "".join(out) + "</g>"


def feliz_natal():
    u = "fnt"
    D = Defs(u)
    out = []
    bg = D.rg([(0, "#FFF8EA"), (0.7, "#F6EAD4"), (1, "#EAD7B8")], cy=0.4, r=0.8)
    out.append(f'<rect width="600" height="600" fill="url(#{bg})"/>')
    out.append(speck(7, 260, "#B8743F", op=(0.08, 0.25)))
    # tropical leaves framing the top corners
    out.append(leaf(D, -30, -20, 250, 54, 34, "#2F7A57", 1))
    out.append(leaf(D, -20, 196, 150, 36, -18, "#3E8E5E", 2))
    out.append(leaf(D, 630, -10, 260, 56, 150, "#24684A", 3))
    out.append(leaf(D, 620, 150, 200, 44, 184, "#2F7A57", 4))
    out.append(leaf(D, 600, 60, 170, 40, 160, "#1E5A40", 5))
    # ornaments hanging from the leaves
    for x, y, L, r, col in ((120, 60, 120, 20, "#C7343A"), (476, 70, 96, 17, "#E2B04A"), (512, 80, 156, 14, "#C7343A")):
        out.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + L - r - 4}" stroke="#B8862A" stroke-width="2"/>')
        out.append(ball(D, x, y + L, r, col))
    # branch with lights
    br = [(-20, 316), (120, 306), (260, 300), (400, 296), (470, 290)]
    out.append(f'<path d="M {P(br).replace(" ", " L ")}" fill="none" stroke="#5A3A24" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<path d="M {P([(a, b - 4) for a, b in br]).replace(" ", " L ")}" fill="none" stroke="#9A6E48" stroke-width="4" stroke-linecap="round" opacity="0.7"/>')
    out.append(leaf(D, 440, 292, 90, 22, -30, "#3E8E5E", 6))
    out.append(leaf(D, 120, 306, 80, 20, 150, "#2F7A57", 7))
    out.append(toucan(D, 300, 300, 1.08))
    wire = "M -20 296 Q 30 330 80 304 Q 130 280 180 314 Q 230 336 280 300 Q 330 280 380 312 Q 420 330 470 286"
    out.append(f'<path d="{wire}" fill="none" stroke="#1E3A2A" stroke-width="2.4"/>')
    for i, (x, yv) in enumerate(((20, 310), (62, 312), (110, 292), (150, 300), (204, 324), (250, 316), (346, 296), (400, 318), (440, 306))):
        out.append(light(D, x, yv + 4, 4.5, ["#F2C25A", "#E8443A", "#7FC4C0", "#F2C25A"][i % 4], halo=4))
    # type
    out.append(T(300, 428, "feliz", SERIF_IT, 100, "#1E5A40", max_w=300))
    out.append(T(300, 538, "NATAL", BEBAS, 136, "#B8312F", ls=18, max_w=420))
    out.append(twinkle(176, 392, 12, "#E2B04A") + twinkle(430, 380, 9, "#E2B04A") + twinkle(448, 404, 6, "#E2B04A"))
    return D.svg() + "\n".join(out)



# ======================================================================== NEW: scenes
def figure(x, base, hh, coat, scarf=None, hat=None, flip=1, extra=""):
    """Small walking person seen from the side-ish; hh = height in px."""
    k = hh / 100
    s = (f'<g transform="translate({x:.1f} {base:.1f}) scale({k * flip:.3f} {k:.3f})">'
         '<path d="M -10 -44 L -14 0 L -5 0 L -1 -30 L 4 0 L 13 0 L 10 -44 Z" fill="#1E1A28"/>'
         f'<path d="M -16 -86 Q 0 -96 16 -86 L 18 -40 L -18 -40 Z" fill="{coat}"/>'
         '<circle cx="0" cy="-97" r="10" fill="#E8C8A8"/>')
    if hat:
        s += f'<path d="M -11 -100 Q 0 -116 11 -100 Z" fill="{hat}"/><circle cx="0" cy="-114" r="4" fill="{hat}"/>'
    if scarf:
        s += f'<rect x="-12" y="-90" width="24" height="7" rx="3" fill="{scarf}"/><rect x="6" y="-86" width="6" height="18" rx="2" fill="{scarf}"/>'
    return s + extra + "</g>"


def peace_on_earth():
    u = "poe"
    D = Defs(u)
    out = []
    C = Cam(f=300, cx=300, vpy=318, eye=1.6)
    sky = D.lg([(0, "#141E44"), (0.4, "#2E3466"), (0.72, "#7A5482"), (1, "#EDA27E")], 0, 0, 0, 322, units="userSpaceOnUse")
    out.append(f'<rect width="600" height="460" fill="url(#{sky})"/>')
    out.append(dots(90, 3, (0, 0, 600, 150), "#F6EDE0", r=(0.6, 1.5), opacity=(0.4, 1)))
    out.append(pt.glow(300, 318, 260, "#FFC59A", f"{u}-hz", 0.55))
    # far hills and a snowy wood behind the church
    poly, ridge = pt.ridge_poly([(-10, 310), (150, 296), (300, 304), (450, 294), (610, 308)], 4, amp=4, base=360, fill="#5A4C78")
    out.append(poly)
    out.append(pt.tree_line(ridge, 5, ["#4A3F68", "#433A60"], density=2.2, hmin=10, hmax=22))
    # church at the end of the street
    Z = 44
    body = C.quad_z(Z, -5.5, 5.5, 0, 7.5)
    gab = [C(-6, 7.4, Z), C(0, 12.5, Z), C(6, 7.4, Z)]
    out.append(f'<polygon points="{P(body)}" fill="#CDBBB0"/><polygon points="{P(gab)}" fill="#E8E4EE"/>'
               f'<polygon points="{P([C(-5.5, 7.4, Z), C(0, 11.8, Z), C(5.5, 7.4, Z)])}" fill="#BCA9A0"/>')
    for wx in (-3.6, 2.6):
        out.append(f'<polygon points="{P(C.quad_z(Z - 0.1, wx, wx + 1, 2.4, 5.6))}" fill="#FFC86A"/>')
    tw = C.quad_z(Z - 1, -1.5, 1.5, 0, 16)
    out.append(f'<polygon points="{P(tw)}" fill="#D9C8BC"/><polygon points="{P(C.quad_z(Z - 1, 0.4, 1.5, 0, 16))}" fill="#B09E96"/>')
    out.append(f'<polygon points="{P([C(-1.9, 15.8, Z - 1), C(0, 27, Z - 1), C(1.9, 15.8, Z - 1)])}" fill="#3E3A5C"/>'
               f'<polygon points="{P([C(0, 27, Z - 1), C(1.9, 15.8, Z - 1), C(0.4, 15.8, Z - 1)])}" fill="#2C2946"/>'
               f'<polyline points="{P([C(-1.9, 15.8, Z - 1), C(0, 27, Z - 1)])}" fill="none" stroke="#F4F0F8" stroke-width="1.8"/>')
    cx_, cy_ = C(0, 28.6, Z - 1)
    out.append(f'<line x1="{cx_:.1f}" y1="{cy_ - 4:.1f}" x2="{cx_:.1f}" y2="{cy_ + 10:.1f}" stroke="#E9C46A" stroke-width="2"/><line x1="{cx_ - 4:.1f}" y1="{cy_ + 1:.1f}" x2="{cx_ + 4:.1f}" y2="{cy_ + 1:.1f}" stroke="#E9C46A" stroke-width="2"/>')
    bx, by = C(0, 12.2, Z - 1.1)
    out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="5" fill="#FFD98E"/><circle cx="{bx:.1f}" cy="{by:.1f}" r="16" fill="url(#{D.glow("#FFD98E", 0.6)})"/>')
    dq = C.quad_z(Z - 1.1, -0.8, 0.8, 0, 2.6)
    out.append(f'<polygon points="{P(dq)}" fill="#FFB85A"/>' + f'<circle cx="{C(0, 1.3, Z)[0]:.1f}" cy="{C(0, 1.3, Z)[1]:.1f}" r="30" fill="url(#{D.glow("#FFC86A", 0.5)})"/>')
    # street and sidewalks (snow)
    road = D.lg([(0, "#B4ADC8"), (0.4, "#D2CCE0"), (1, "#EDE9F2")], 0, 318, 0, 460, units="userSpaceOnUse")
    out.append(f'<polygon points="{P([C(-60, 0, Z), C(60, 0, Z), C(60, 0, 1.2), C(-60, 0, 1.2)])}" fill="url(#{road})"/>')
    for sx in (-1.7, -0.6, 0.6, 1.7):
        pts_ = [C(sx + 0.25 * math.sin(z * 0.35 + sx), 0, z) for z in [2 + i * 1.5 for i in range(28)]]
        out.append(f'<polyline points="{P(pts_)}" fill="none" stroke="#9A93B4" stroke-width="2.5" opacity="0.55"/>')
    out.append(dots(120, 41, (120, 380, 480, 450), "#FFFFFF", r=(1, 2.4), opacity=(0.5, 0.9)))
    for sg in (-1, 1):
        out.append(f'<polygon points="{P([C(sg * 5.6, 0.12, Z), C(sg * 7.5, 0.12, Z), C(sg * 7.5, 0.12, 1.5), C(sg * 5.6, 0.12, 1.5)])}" fill="#F4F1F7"/>')
        out.append(f'<polyline points="{P([C(sg * 5.6, 0.12, Z), C(sg * 5.6, 0.12, 1.5)])}" fill="none" stroke="#A39CBC" stroke-width="2"/>')
    # houses: gable fronts along both sides (z0, z1, wall h, gable h, colour)
    left = [(3, 9.5, 7, 3.6, "#9A4A3E"), (9.5, 15, 8.2, 3.2, "#D9C9A8"), (15, 20.5, 6.8, 3.8, "#5E7A6E"), (20.5, 26, 8.6, 3.2, "#A8744A"),
            (26, 31, 7.2, 3.4, "#4E6488"), (31, 36, 7.6, 3.0, "#9A4A3E"), (36, 41, 7, 3.2, "#CDB894")]
    right = [(3, 8.5, 7.6, 3.4, "#3F6A5A"), (8.5, 14.5, 7, 3.8, "#C78A50"), (14.5, 20, 8.8, 3.0, "#8A3E46"), (20, 25.5, 7, 3.6, "#E0D2B6"),
             (25.5, 31, 8, 3.2, "#5A6E92"), (31, 36.5, 7.2, 3.4, "#A8744A"), (36.5, 41, 7.6, 3.0, "#6E8A74")]
    dusk = D.lg([(0, "#1A1436", 0.55), (0.6, "#1A1436", 0.2), (1, "#1A1436", 0)], 0, 0, 0, 1)
    rnd = random.Random(12)
    for sg, blds in ((-1, left), (1, right)):
        X = sg * 7.5
        for k, (z0, z1, h, gh, col) in sorted(enumerate(blds), key=lambda t: -t[1][0]):
            zm = (z0 + z1) / 2
            wall = C.quad_x(X, z0, z1, 0, h)
            out.append(f'<polygon points="{P(wall)}" fill="{col}"/>')
            out.append(f'<polygon points="{P([C(X, h, z0), C(X, h + gh, zm), C(X, h, z1)])}" fill="{dk(col, 0.08)}"/>')
            # near roof slope covered in snow
            out.append(f'<polygon points="{P([C(X, h, z0 - 0.3), C(X, h + gh + 0.2, zm), C(X + sg * 9, h + gh + 0.2, zm), C(X + sg * 9, h, z0 - 0.3)])}" fill="#E4E2F0"/>')
            out.append(f'<polygon points="{P([C(X, h + gh * 0.5, (z0 + zm) / 2), C(X, h + gh + 0.2, zm), C(X + sg * 9, h + gh + 0.2, zm), C(X + sg * 9, h + gh * 0.5, (z0 + zm) / 2)])}" fill="#F7F6FB"/>')
            sw = max(1.5, 300 / zm * 0.32)
            out.append(f'<polyline points="{P([C(X, h - 0.1, z0 - 0.3), C(X, h + gh + 0.25, zm), C(X, h - 0.1, z1 + 0.3)])}" fill="none" stroke="#FBFAFF" stroke-width="{sw:.1f}" stroke-linejoin="round" stroke-linecap="round"/>')
            # windows
            for fl, y0 in enumerate((3.4, 5.6) if h > 7.8 else (3.6,)):
                for t in (0.25, 0.75):
                    za, zb = z0 + (z1 - z0) * (t - 0.11), z0 + (z1 - z0) * (t + 0.11)
                    on = rnd.random() < 0.8
                    q = C.quad_x(X, za, zb, y0, y0 + 1.5)
                    out.append(f'<polygon points="{P(q)}" fill="{rnd.choice(["#FFD27A", "#FFC45E", "#FFE0A0"]) if on else "#2A2440"}"/>')
                    m1, m2 = C(X, y0 + 0.75, za), C(X, y0 + 0.75, zb)
                    n1, n2 = C(X, y0, (za + zb) / 2), C(X, y0 + 1.5, (za + zb) / 2)
                    out.append(f'<path d="M {m1[0]:.1f} {m1[1]:.1f} L {m2[0]:.1f} {m2[1]:.1f} M {n1[0]:.1f} {n1[1]:.1f} L {n2[0]:.1f} {n2[1]:.1f}" stroke="{dk(col, 0.35)}" stroke-width="{max(0.8, 30 / zm):.1f}"/>')
                    sill = C.quad_x(X, za - 0.1, zb + 0.1, y0 - 0.15, y0)
                    out.append(f'<polygon points="{P(sill)}" fill="#FFFFFF"/>')
            # attic window in the gable
            q = C.quad_x(X, zm - 0.35, zm + 0.35, h + 0.7, h + 1.5)
            out.append(f'<polygon points="{P(q)}" fill="{"#FFD27A" if rnd.random() < 0.6 else "#2A2440"}"/>')
            # shop window / door with wreath on the ground floor
            dz = z0 + (z1 - z0) * 0.5
            out.append(f'<polygon points="{P(C.quad_x(X, dz - 0.5, dz + 0.5, 0, 2.2))}" fill="{dk(col, 0.45)}"/>')
            wx_, wy_ = C(X, 2.6, dz)
            out.append(f'<circle cx="{wx_:.1f}" cy="{wy_:.1f}" r="{max(1.5, 300 / dz * 0.3):.1f}" fill="none" stroke="#2F6A4C" stroke-width="{max(1, 300 / dz * 0.14):.1f}"/>')
            for t in (0.2, 0.8):
                za, zb = z0 + (z1 - z0) * (t - 0.13), z0 + (z1 - z0) * (t + 0.13)
                out.append(f'<polygon points="{P(C.quad_x(X, za, zb, 0.6, 2.2))}" fill="#FFCF7A"/>')
                spill = [C(X, 0.13, za), C(X, 0.13, zb), C(X - sg * 1.6, 0.13, zb), C(X - sg * 1.6, 0.13, za)]
                out.append(f'<polygon points="{P(spill)}" fill="#FFC86A" opacity="0.35"/>')
            out.append(f'<polygon points="{P(C.quad_x(X, z0, z0 + 0.25, 0, h))}" fill="#000" opacity="0.18"/>')
            out.append(f'<polygon points="{P(wall)}" fill="url(#{dusk})"/>')
    # town tree before the church
    tx, tb = C(-3.4, 0, 38)
    tsvg, tiers = fir(D, tx, tb, 300 / 38 * 7.5, 300 / 38 * 4.2, 21, light_c="#3E6A5A", mid="#24483E", dark="#162E2A", tiers=5, snow=False, needles=False)
    out.append(tsvg)
    rr = random.Random(4)
    for k, (apex, hem, hw) in enumerate(tiers):
        for _ in range(2 + k):
            y = rr.uniform(apex + (hem - apex) * 0.4, hem - 2)
            lim = hw * (y - apex) / (hem - apex) * 0.8
            out.append(light(D, rr.uniform(tx - lim, tx + lim), y, 1.4, rr.choice(["#FFD27A", "#FF7A6A", "#8FD3E8"]), halo=4))
    out.append(star5(D, tx, tb - 300 / 38 * 7.5 - 2, 5, glow_r=16))
    # street lamps
    for sg in (-1, 1):
        for z in (30, 18, 9):
            X = sg * 6.1
            a, b = C(X, 0, z), C(X, 3.6, z)
            w = 300 / z * 0.12
            out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#1E1A2C" stroke-width="{w:.1f}"/>')
            lx, ly = C(X, 3.85, z)
            s_ = 300 / z * 0.28
            out.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="{s_ * 4:.1f}" fill="url(#{D.glow("#FFD98E", 0.7)})"/>'
                       f'<rect x="{lx - s_ / 2:.1f}" y="{ly - s_ * 0.6:.1f}" width="{s_:.1f}" height="{s_ * 1.2:.1f}" fill="#FFE6A8" stroke="#1E1A2C" stroke-width="{max(1, s_ * 0.15):.1f}"/>'
                       f'<path d="M {lx - s_ * 0.7:.1f} {ly - s_ * 0.6:.1f} L {lx:.1f} {ly - s_ * 1.1:.1f} L {lx + s_ * 0.7:.1f} {ly - s_ * 0.6:.1f} Z" fill="#1E1A2C"/>'
                       f'<path d="M {lx - s_ * 0.7:.1f} {ly - s_ * 0.66:.1f} L {lx:.1f} {ly - s_ * 1.15:.1f} L {lx + s_ * 0.7:.1f} {ly - s_ * 0.66:.1f}" fill="none" stroke="#FFFFFF" stroke-width="{max(1, s_ * 0.18):.1f}"/>')
    # swags of lights across the street
    for z in (24, 13):
        pts = [C(-7.5 + 15 * t, 6.2 - 1.2 * math.sin(math.pi * t), z) for t in [i / 24 for i in range(25)]]
        out.append(f'<polyline points="{P(pts)}" fill="none" stroke="#1E1A2C" stroke-width="{300 / z * 0.04:.1f}"/>')
        for i, (x, y) in enumerate(pts[1:-1:2]):
            out.append(light(D, x, y + 2, 300 / z * 0.07, ["#FFD27A", "#FF6A5A", "#7FD3C0", "#FFD27A"][i % 4], halo=3.5))
    # people: a child pulling a sled, a couple, someone with a gift
    def pz(X, Z, h, coat, **kw):
        x, base = C(X, 0, Z)
        return figure(x, base, 300 * h / Z, coat, **kw)
    sled = '<path d="M 22 -8 L 60 -6" stroke="#3A2A22" stroke-width="2"/><rect x="58" y="-16" width="44" height="9" rx="3" fill="#B8312F"/><path d="M 56 -4 L 104 -4 Q 110 -4 108 -10" fill="none" stroke="#3A2A22" stroke-width="3"/>'
    out.append(pz(-2.0, 5.6, 1.05, "#2F6A9A", scarf="#E8C24A", hat="#C7343A", flip=-1, extra=sled))
    out.append(pz(2.6, 7.6, 1.75, "#7A3A4A", scarf="#F6EDE0"))
    out.append(pz(3.2, 7.75, 1.65, "#2E4A3A", scarf="#C7343A", hat="#2E4A3A"))
    out.append(pz(-0.8, 16, 1.7, "#8A5A3A", scarf="#2F6A4C", flip=-1))
    out.append(pz(-6.4, 19, 1.7, "#3A3A5A", extra='<rect x="-24" y="-78" width="20" height="18" fill="#C7343A"/><rect x="-16" y="-78" width="4" height="18" fill="#E9C46A"/>'))
    out.append(pz(6.6, 26, 1.7, "#5A4A6A", flip=-1))
    out.append(snowfall(14, 200, box=(0, 0, 600, 450), r=(1, 3.2), op=(0.5, 1)))
    out.append(soft_flakes(D, 15, 12, box=(0, 0, 600, 440), r=(6, 12), s=0.5))
    # band
    band = D.lg([(0, "#1E4D3A"), (1, "#123226")])
    out.append(f'<rect x="0" y="446" width="600" height="154" fill="url(#{band})"/><rect x="0" y="446" width="600" height="5" fill="#E2B04A"/>')
    out.append(T(300, 498, "Peace on Earth", SERIF_IT, 76, CREAM, max_w=460))
    out.append(T(300, 536, "CHRISTMAS EVE · MAIN STREET", MONO, 18, "#E9C46A", ls=5, max_w=440))
    return D.svg() + "\n".join(out)


def truck(D, x, y, k=1.0):
    """Red vintage pickup in profile facing right, a fresh tree in the bed. (x, y) = rear-wheel contact point."""
    red = D.lg([(0, "#E0484A"), (0.45, "#C2282E"), (1, "#7E141A")])
    chrome = D.lg([(0, "#FFFFFF"), (0.5, "#B8C4CC"), (1, "#6A7680")])
    glass = D.lg([(0, "#CFE4F0"), (0.6, "#7EA6C4"), (1, "#4A6A8A")], 0, 0, 1, 1)
    o = [f'<g transform="translate({x - 70 * k:.1f} {y:.1f}) scale({k})">']
    o.append('<ellipse cx="180" cy="2" rx="200" ry="10" fill="#4A5A7A" opacity="0.3"/>')
    # tree lying in the bed, tip out over the tailgate
    tsvg, _ = fir(D, 0, 0, 230, 96, 41, light_c="#5C9A6A", mid="#2E6A4C", dark="#173F30", tiers=6, snow=False)
    o.append(f'<g transform="translate(176 -112) rotate(-98)">{tsvg}</g>')
    o.append('<rect x="160" y="-122" width="22" height="12" rx="3" fill="#6A4630" transform="rotate(-8 170 -116)"/>')
    # bed
    o.append(f'<path d="M 8 -40 L 8 -100 L 172 -100 L 172 -40 Z" fill="url(#{red})"/>')
    o.append('<rect x="6" y="-104" width="168" height="7" rx="2" fill="#E8605E"/><rect x="8" y="-97" width="164" height="2" fill="#5A0E14" opacity="0.4"/>')
    o.append('<g fill="#7E141A">' + "".join(f'<rect x="{xx}" y="-96" width="7" height="10"/>' for xx in (20, 92, 160)) + "</g>")
    # rope over the tree
    o.append('<path d="M 60 -100 Q 66 -134 72 -150 M 128 -100 Q 132 -132 140 -146" stroke="#E8D4A8" stroke-width="3" fill="none" stroke-linecap="round"/>')
    # cab
    o.append(f'<path d="M 168 -40 L 168 -148 Q 168 -160 182 -160 L 228 -160 Q 242 -160 248 -148 L 268 -104 L 268 -40 Z" fill="url(#{red})"/>')
    o.append(f'<path d="M 182 -148 L 226 -148 Q 234 -148 238 -140 L 254 -108 L 182 -108 Z" fill="url(#{glass})"/>')
    o.append('<path d="M 196 -148 L 186 -110 M 214 -148 L 200 -110" stroke="#FFFFFF" stroke-width="5" opacity="0.45"/>')
    o.append('<path d="M 174 -106 L 174 -46 L 264 -46" fill="none" stroke="#7E141A" stroke-width="2.5"/><rect x="236" y="-96" width="16" height="5" rx="2" fill="url(#' + chrome + ')"/>')
    # hood and front
    o.append(f'<path d="M 264 -104 L 326 -98 Q 350 -96 352 -72 L 354 -40 L 264 -40 Z" fill="url(#{red})"/>')
    o.append('<path d="M 268 -102 L 326 -97 Q 344 -95 348 -80" fill="none" stroke="#F59A90" stroke-width="3" stroke-linecap="round" opacity="0.8"/>')
    # fenders
    o.append('<path d="M 26 -28 Q 30 -80 72 -82 Q 114 -80 118 -28 Z" fill="#A61E24"/><path d="M 34 -44 Q 40 -74 72 -76" fill="none" stroke="#F07070" stroke-width="3" opacity="0.6" stroke-linecap="round"/>')
    o.append('<path d="M 214 -28 Q 218 -88 268 -90 Q 322 -88 334 -28 Z" fill="#A61E24"/><path d="M 224 -46 Q 232 -82 268 -84" fill="none" stroke="#F07070" stroke-width="3" opacity="0.6" stroke-linecap="round"/>')
    o.append('<rect x="112" y="-36" width="108" height="9" rx="3" fill="#3A2A2A"/>')
    # grille, wreath, headlight, bumpers
    o.append(f'<rect x="342" y="-86" width="12" height="42" rx="3" fill="url(#{chrome})"/>')
    o.append(f'<rect x="346" y="-50" width="22" height="10" rx="4" fill="url(#{chrome})"/><rect x="-6" y="-46" width="20" height="9" rx="4" fill="url(#{chrome})"/>')
    o.append(f'<circle cx="318" cy="-92" r="10" fill="url(#{chrome})"/><circle cx="319" cy="-92" r="6.5" fill="#FFF3C8"/>')
    o.append(f'<circle cx="319" cy="-92" r="40" fill="url(#{D.glow("#FFE7A8", 0.6)})"/>')
    o.append('<circle cx="344" cy="-66" r="15" fill="none" stroke="#2F6A4C" stroke-width="7"/><circle cx="344" cy="-66" r="15" fill="none" stroke="#5C9A6A" stroke-width="2" stroke-dasharray="3 4"/>'
             '<circle cx="336" cy="-56" r="2.6" fill="#E8443A"/><circle cx="352" cy="-58" r="2.6" fill="#E8443A"/><path d="M 344 -50 l -7 9 l 5 0 Z M 344 -50 l 7 9 l -5 0 Z" fill="#C7343A"/><circle cx="344" cy="-51" r="3.5" fill="#C7343A"/>')
    o.append('<rect x="10" y="-82" width="8" height="12" rx="2" fill="#FF6A5A"/>')
    # wheels
    for wx in (72, 268):
        o.append(f'<circle cx="{wx}" cy="-30" r="30" fill="#1E1A1E"/><circle cx="{wx}" cy="-30" r="20" fill="#F2ECE2"/><circle cx="{wx}" cy="-30" r="14" fill="#C2282E"/>'
                 f'<circle cx="{wx}" cy="-30" r="7" fill="url(#{chrome})"/><path d="M {wx - 22} -42 A 26 26 0 0 1 {wx + 6} -56" fill="none" stroke="#5A5460" stroke-width="3"/>')
    # snow on the roof, hood and tree
    o.append(snow_cap([(172 + i * 10, -160) for i in range(8)], thick=9, seed=3))
    o.append(snow_cap([(270 + i * 12, -103 + i * 0.8) for i in range(6)], thick=6, seed=4))
    o.append("</g>")
    return "".join(o)


def tis_the_season():
    u = "tts"
    D = Defs(u)
    out = []
    sky = D.lg([(0, "#8FB1C9"), (0.55, "#E9D6C4"), (1, "#F7D2B0")])
    out.append(f'<rect width="600" height="600" fill="url(#{sky})"/>')
    out.append(pt.glow(420, 300, 260, "#FFE1B8", f"{u}-sun", 0.6))
    # three layers of snowy forest, hazier with distance
    for i, (yb, cols, hmin, hmax, dens, lc) in enumerate((
            (330, ["#9FB4C4", "#AABCCB"], 30, 70, 2.0, "#E8EEF4"),
            (372, ["#6E8A9C", "#7A95A6", "#66808F"], 50, 110, 1.6, "#DDE7EE"),
            (420, ["#3E5E58", "#355248", "#47685E"], 80, 170, 1.0, "#CFE0E6"))):
        line = rough([(-20, yb), (300, yb - 6), (620, yb + 4)], 10 + i, amp=6, depth=3)
        rnd = random.Random(30 + i)
        xs = sorted(rnd.uniform(-20, 620) for _ in range(int(640 * dens / 10)))
        for x in xs:
            if i == 2 and 120 < x < 500:
                continue
            h = rnd.uniform(hmin, hmax)
            out.append(pt.conifer(x, (y_on(line, x) or yb) + 4, h, rnd.choice(cols), rnd.random(), light=lc))
        out.append(f'<path d="M -20 {yb} Q 300 {yb - 14} 620 {yb + 2} L 620 600 L -20 600 Z" fill="{["#E4ECF2", "#DCE6EE", "#E8EFF4"][i]}"/>')
    # snowy road with tracks
    out.append(f'<path d="M -20 452 Q 300 432 620 448 L 620 600 L -20 600 Z" fill="url(#{D.lg([(0, "#D6E0EA"), (1, "#F6F8FA")])})"/>')
    out.append('<g fill="none" stroke="#B4C2D2" stroke-width="5" opacity="0.8"><path d="M -20 492 Q 300 474 620 488"/><path d="M -20 520 Q 300 500 620 514"/></g>')
    out.append(truck(D, 168, 506, 1.08))
    # foreground snow bank + big pines bleeding off the edges
    out.append(f'<path d="M -20 548 Q 120 528 260 546 Q 420 560 620 536 L 620 600 L -20 600 Z" fill="#FFFFFF"/>')
    out.append(f'<path d="M -20 548 Q 120 528 260 546 Q 420 560 620 536" fill="none" stroke="#C9D6E2" stroke-width="4"/>')
    for x, base, h, seed in ((10, 600, 330, 1), (596, 600, 300, 2)):
        tsvg, _ = fir(D, x, base, h, h * 0.5, seed, light_c="#4E7A6A", mid="#2A5446", dark="#173A30", tiers=7, snow=True)
        out.append(tsvg)
    out.append(snowfall(21, 140, r=(1.2, 3.4), op=(0.6, 1)))
    # type
    out.append(T(300, 122, "'tis the", SERIF_IT, 84, "#8E2234", max_w=360))
    out.append(T(300, 232, "SEASON", ANTON, 118, "#163F30", ls=10, max_w=440, extra=' transform="translate(0 5)" opacity="0.18"'))
    out.append(T(300, 232, "SEASON", ANTON, 118, "#1E5A40", ls=10, max_w=440))
    return D.svg() + "\n".join(out)


def warmest_wishes():
    u = "wwc"
    D = Defs(u)
    out = []
    sky = D.lg([(0, "#0C1A30"), (0.55, "#1E3E5C"), (1, "#3E6A84")])
    out.append(f'<rect width="600" height="600" fill="url(#{sky})"/>')
    out.append(dots(140, 9, (0, 0, 600, 330), "#F6EDE0", r=(0.6, 1.7), opacity=(0.3, 1)))
    out.append(twinkle(96, 96, 7, "#FFF3D2") + twinkle(512, 70, 6, "#FFF3D2") + twinkle(470, 210, 5, "#FFF3D2"))
    # forest rows behind the clearing
    poly, l1 = pt.ridge_poly([(-10, 340), (200, 330), (420, 336), (610, 326)], 2, amp=3, base=600, fill="#1A3448")
    out.append(pt.tree_line(l1, 6, ["#1E3A4E", "#1A3446", "#22405A"], density=2.4, hmin=40, hmax=90))
    out.append(poly)
    out.append(pt.tree_line([(-10, 372), (610, 368)], 7, ["#132838", "#102230"], density=1.6, hmin=60, hmax=130, xmin=-10, xmax=170))
    out.append(pt.tree_line([(-10, 372), (610, 368)], 8, ["#132838", "#102230"], density=1.6, hmin=60, hmax=130, xmin=440, xmax=610))
    # snowy clearing
    snow = D.lg([(0, "#B9CCDC"), (0.5, "#DDE8F0"), (1, "#F2F6FA")])
    out.append(f'<path d="M -10 400 Q 150 380 300 392 Q 460 404 610 386 L 610 600 L -10 600 Z" fill="url(#{snow})"/>')
    # cabin (oblique 3/4 view)
    F0, F1, F2, F3, A = (180, 460), (322, 460), (322, 372), (180, 372), (251, 306)
    v = (104, -18)
    add = lambda p, q=v, s=1: (p[0] + q[0] * s, p[1] + q[1] * s)
    logf = D.lg([(0, "#8A5634"), (1, "#5A341E")])
    logs = D.lg([(0, "#6A4028"), (1, "#3E2414")])
    # side wall
    side = [F1, add(F1), add(F2), F2]
    out.append(f'<polygon points="{P(side)}" fill="url(#{logs})"/>')
    c = D.clip(f'<polygon points="{P(side)}"/>')
    out.append(f'<g clip-path="url(#{c})" stroke="#2A160C" stroke-width="2" opacity="0.7">' + "".join(
        f'<line x1="{F1[0]}" y1="{y:.1f}" x2="{F1[0] + v[0]}" y2="{y + v[1]:.1f}"/>' for y in range(F2[1] + 11, F1[1], 11)) + "</g>")
    # front gable wall
    front = [F0, F1, F2, A, F3]
    out.append(f'<polygon points="{P(front)}" fill="url(#{logf})"/>')
    c = D.clip(f'<polygon points="{P(front)}"/>')
    out.append(f'<g clip-path="url(#{c})"><g stroke="#3A2010" stroke-width="2.4" opacity="0.75">' + "".join(
        f'<line x1="170" y1="{y}" x2="340" y2="{y}"/>' for y in range(F0[1] - 11, A[1], -11)) + "</g>"
        '<g stroke="#B07A50" stroke-width="1.5" opacity="0.6">' + "".join(f'<line x1="170" y1="{y - 9}" x2="340" y2="{y - 9}"/>' for y in range(F0[1] - 11, A[1], -11)) + "</g></g>")
    # log ends at the front corner
    out.append("".join(f'<circle cx="{F1[0] + 2}" cy="{y - 5}" r="6" fill="#C8955E"/><circle cx="{F1[0] + 2}" cy="{y - 5}" r="2.5" fill="none" stroke="#8A5A34" stroke-width="1.2"/>' for y in range(F0[1], F2[1], -11)))
    out.append("".join(f'<circle cx="{F0[0] - 2}" cy="{y - 5}" r="6" fill="#B07E4C"/>' for y in range(F0[1], F3[1], -11)))
    # roof: visible right slope in snow, thick snowy bargeboard on the gable
    roof = [(A[0] - 2, A[1] - 8), add((A[0] - 2, A[1] - 8)), add((F2[0] + 16, F2[1] + 4)), (F2[0] + 16, F2[1] + 4)]
    out.append(f'<polygon points="{P(roof)}" fill="url(#{D.lg([(0, "#FFFFFF"), (1, "#C7D6E4")], 0, 0, 1, 1)})"/>')
    out.append(f'<path d="M {F3[0] - 18} {F3[1] + 6} L {A[0]} {A[1] - 10} L {F2[0] + 18} {F2[1] + 6}" fill="none" stroke="#3A2010" stroke-width="10" stroke-linejoin="round"/>')
    out.append(snow_cap(rough([(F3[0] - 20, F3[1] + 2), (A[0], A[1] - 14)], 3, amp=0, depth=3), thick=12, seed=4))
    out.append(snow_cap(rough([(A[0], A[1] - 14), (F2[0] + 20, F2[1] + 2)], 4, amp=0, depth=3), thick=12, seed=5))
    out.append(snow_cap([add((F2[0] + 16, F2[1] + 6), s=t) for t in [i / 6 for i in range(7)]], thick=8, seed=6))
    # chimney + smoke
    ch = [(392, 318), (412, 314), (412, 268), (392, 272)]
    out.append(f'<polygon points="{P(ch)}" fill="#7A6A64"/><polygon points="{P([(412, 314), (420, 312), (420, 266), (412, 268)])}" fill="#5A4C48"/>')
    out.append('<g fill="#5E504C">' + "".join(f'<rect x="{x}" y="{y}" width="8" height="5" rx="1"/>' for x, y in ((394, 300), (402, 290), (394, 280), (403, 306))) + "</g>")
    out.append(snow_cap([(390, 270), (400, 268), (410, 266), (422, 264)], thick=6, seed=7))
    pg = D.lg([(0, "#8A9AAE"), (1, "#E8EEF4")], 380, 0, 480, 0, units="userSpaceOnUse")
    out.append(f'<g opacity="0.7">{puff_column(u, 404, 260, 236, 3, r0=6, r1=22, drift=110, n=30, grad=pg, hi="#FFFFFF", hi_op=0.35)}</g>')
    # door + wreath
    out.append(f'<rect x="232" y="396" width="40" height="64" rx="3" fill="#7A2A20"/><rect x="236" y="400" width="32" height="56" fill="#5A1E16"/>')
    out.append('<circle cx="252" cy="416" r="9" fill="none" stroke="#2F6A4C" stroke-width="5"/><circle cx="252" cy="425" r="2.5" fill="#E8443A"/><circle cx="264" cy="430" r="2" fill="#E9C46A"/>')
    # windows: front and side, glowing
    for wx, wy, ww, wh in ((192, 388, 30, 30), (284, 388, 28, 30)):
        out.append(f'<circle cx="{wx + ww / 2}" cy="{wy + wh / 2}" r="48" fill="url(#{D.glow("#FFC86A", 0.5)})"/>')
        out.append(f'<rect x="{wx - 3}" y="{wy - 3}" width="{ww + 6}" height="{wh + 6}" fill="#2A160C"/><rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="#FFD27A"/>'
                   f'<path d="M {wx + ww / 2} {wy} L {wx + ww / 2} {wy + wh} M {wx} {wy + wh / 2} L {wx + ww} {wy + wh / 2}" stroke="#2A160C" stroke-width="3"/>'
                   f'<rect x="{wx - 5}" y="{wy + wh}" width="{ww + 10}" height="5" fill="#FFFFFF"/>')
    for t in (0.3, 0.7):
        bx, by = F1[0] + v[0] * t, F1[1] + v[1] * t - 62
        q = [(bx - 12, by), (bx + 12, by - 2), (bx + 12, by + 26), (bx - 12, by + 28)]
        out.append(f'<circle cx="{bx}" cy="{by + 14}" r="40" fill="url(#{D.glow("#FFC86A", 0.45)})"/><polygon points="{P(q)}" fill="#FFCF6A"/>'
                   f'<line x1="{bx}" y1="{by - 1}" x2="{bx}" y2="{by + 27}" stroke="#2A160C" stroke-width="2.5"/>')
    # light spill on snow
    out.append(pt.mist(270, 478, 170, 26, "#FFC86A", f"{u}-spill", 0.35))
    # string lights along the eaves
    pts = [(F3[0] - 14 + (A[0] - F3[0] + 14) * t, F3[1] + 10 + (A[1] - 4 - F3[1] - 10) * t) for t in [i / 7 for i in range(8)]]
    pts += [(A[0] + (F2[0] + 14 - A[0]) * t, A[1] - 4 + (F2[1] + 10 - A[1] + 4) * t) for t in [i / 7 for i in range(1, 8)]]
    pts += [add((F2[0] + 14, F2[1] + 12), s=t) for t in [i / 6 for i in range(1, 7)]]
    cols = ["#FF6A5A", "#FFD27A", "#7FD3E0", "#9AE08A"]
    out.append(f'<polyline points="{P(pts)}" fill="none" stroke="#1A1010" stroke-width="1.6"/>')
    out.append("".join(light(D, x, y + 4, 3, cols[i % 4], halo=4) for i, (x, y) in enumerate(pts)))
    # woodpile + sled leaning on the wall
    out.append('<rect x="130" y="430" width="44" height="34" fill="#4A2E1C"/>' + "".join(
        f'<circle cx="{136 + 10 * i + (5 if j % 2 else 0)}" cy="{458 - 9 * j}" r="5" fill="#C8955E" stroke="#6A4028" stroke-width="1.4"/>' for j in range(4) for i in range(4 - (j % 2))))
    out.append(snow_cap([(128, 428), (140, 425), (154, 424), (170, 426), (178, 428)], thick=8, seed=8))
    out.append('<g transform="translate(396 488) rotate(-6)"><ellipse cx="34" cy="10" rx="44" ry="6" fill="#8FA6BC" opacity="0.6"/>'
               '<path d="M -8 4 L 70 4 Q 84 4 84 -8" fill="none" stroke="#2A1E18" stroke-width="3.5" stroke-linecap="round"/>'
               '<g fill="#B8312F"><rect x="0" y="-14" width="68" height="7" rx="2"/><rect x="0" y="-5" width="68" height="6" rx="2"/></g>'
               '<path d="M 2 -14 L 4 2 M 64 -14 L 62 2" stroke="#2A1E18" stroke-width="2.5"/><rect x="0" y="-14" width="68" height="2" fill="#F08A80"/></g>')
    # foreground drifts, footpath, big pines at the edges
    out.append(f'<path d="M -10 520 Q 160 500 300 520 Q 440 540 610 512 L 610 600 L -10 600 Z" fill="#F4F8FB"/>')
    out.append(f'<path d="M -10 520 Q 160 500 300 520 Q 440 540 610 512" fill="none" stroke="#B9CCDC" stroke-width="3"/>')
    rnd = random.Random(3)
    out.append('<g fill="#A9BED0">' + "".join(f'<ellipse cx="{252 + (i % 2) * 12 - i * 3 + rnd.uniform(-2, 2):.1f}" cy="{470 + i * 14}" rx="4" ry="2.4"/>' for i in range(9)) + "</g>")
    for x, h, seed in ((20, 360, 31), (590, 330, 32)):
        tsvg, _ = fir(D, x, 610, h, h * 0.42, seed, light_c="#2E5A5A", mid="#1C3E42", dark="#0E2430", tiers=7, snow=True, needles=False)
        out.append(tsvg)
    out.append(snowfall(18, 120, box=(0, 0, 600, 600), r=(1, 3), op=(0.5, 0.95)))
    # type
    gold = D.lg([(0, "#FFF0B8"), (0.5, "#F2C25A"), (1, "#C98A26")])
    out.append(T(300, 120, "warmest", SERIF_IT, 100, CREAM, max_w=400))
    out.append(T(300, 212, "WISHES", BEBAS, 104, f"url(#{gold})", ls=18, max_w=420))
    return D.svg() + "\n".join(out)


def believe():
    u = "blv"
    D = Defs(u)
    out = []
    bg = D.rg([(0, "#EEF6F8"), (0.6, "#CFE3EA"), (1, "#9EC2D2")], cy=0.42, r=0.75)
    out.append(f'<rect width="600" height="600" fill="url(#{bg})"/>')
    from icons import snowflake
    rnd = random.Random(5)
    for x, y, r in ((80, 90, 26), (530, 120, 20), (70, 330, 18), (536, 360, 28), (110, 470, 14), (500, 500, 16), (300, 60, 0)):
        if r:
            out.append(f'<g opacity="0.55">{snowflake(x, y, r, "#FFFFFF", 3)}</g>')
    cx, cy, R = 300, 222, 152
    # base
    out.append('<g transform="translate(0 -26)">')
    base_red = D.lg([(0, "#7E141C"), (0.25, "#C8343A"), (0.55, "#9E1E26"), (1, "#5A0C12")], 0, 0, 1, 0)
    gold = D.lg([(0, "#8A5A14"), (0.3, "#FFF0B0"), (0.6, "#E2B04A"), (1, "#8A5A14")], 0, 0, 1, 0)
    out.append(f'<ellipse cx="{cx}" cy="456" rx="170" ry="16" fill="#3A5A6A" opacity="0.28"/>')
    out.append(f'<path d="M {cx - 120} 380 L {cx - 146} 448 Q {cx} 470 {cx + 146} 448 L {cx + 120} 380 Z" fill="url(#{base_red})"/>')
    out.append(f'<path d="M {cx - 146} 446 Q {cx} 468 {cx + 146} 446 L {cx + 148} 454 Q {cx} 476 {cx - 148} 454 Z" fill="url(#{gold})"/>')
    out.append(f'<path d="M {cx - 128} 400 Q {cx} 418 {cx + 128} 400 L {cx + 130} 408 Q {cx} 426 {cx - 130} 408 Z" fill="url(#{gold})"/>')
    out.append("".join(f'<polygon points="{star_points(cx + dx, 430 + abs(dx) * 0.05, 7, 3)}" fill="#F2C25A"/>' for dx in (-90, -45, 0, 45, 90)))
    out.append(f'<ellipse cx="{cx}" cy="378" rx="122" ry="14" fill="url(#{gold})"/>')
    out.append("</g>")
    # globe interior
    c = D.clip(f'<circle cx="{cx}" cy="{cy}" r="{R}"/>')
    night = D.lg([(0, "#14264A"), (0.6, "#2C4E7A"), (1, "#5A86A8")])
    inner = [f'<rect x="{cx - R}" y="{cy - R}" width="{2 * R}" height="{2 * R}" fill="url(#{night})"/>',
             dots(60, 3, (cx - R, cy - R, cx + R, cy + 40), "#FFFFFF", r=(0.6, 1.5), opacity=(0.4, 1)),
             f'<circle cx="{cx + 70}" cy="{cy - 90}" r="16" fill="#F7EFD6"/><circle cx="{cx + 70}" cy="{cy - 90}" r="40" fill="url(#{D.glow("#F7EFD6", 0.4)})"/>']
    hill = D.lg([(0, "#FFFFFF"), (1, "#C4D6E6")])
    inner.append(f'<path d="M {cx - R} {cy + 70} Q {cx - 60} {cy + 40} {cx + 20} {cy + 62} Q {cx + 100} {cy + 80} {cx + R} {cy + 54} L {cx + R} {cy + R} L {cx - R} {cy + R} Z" fill="#A9C0D6"/>')
    # tiny town
    def house(x, base, w, h, roof, wall, lit=True):
        s_ = (f'<rect x="{x}" y="{base - h}" width="{w}" height="{h}" fill="{wall}"/><rect x="{x + w * 0.6}" y="{base - h}" width="{w * 0.4}" height="{h}" fill="#000" opacity="0.12"/>'
              f'<path d="M {x - 4} {base - h + 2} L {x + w / 2} {base - h - w * 0.5} L {x + w + 4} {base - h + 2} Z" fill="{roof}"/>'
              f'<path d="M {x - 5} {base - h + 2} L {x + w / 2} {base - h - w * 0.5 - 2} L {x + w + 5} {base - h + 2} L {x + w / 2} {base - h - w * 0.5 + 6} Z" fill="#FFFFFF"/>')
        if lit:
            s_ += (f'<rect x="{x + w * 0.18:.1f}" y="{base - h * 0.7:.1f}" width="{w * 0.22:.1f}" height="{h * 0.25:.1f}" fill="#FFD27A"/>'
                   f'<rect x="{x + w * 0.6:.1f}" y="{base - h * 0.7:.1f}" width="{w * 0.22:.1f}" height="{h * 0.25:.1f}" fill="#FFD27A"/>'
                   f'<rect x="{x + w * 0.4:.1f}" y="{base - h * 0.32:.1f}" width="{w * 0.2:.1f}" height="{h * 0.32:.1f}" fill="#7A3A2A"/>')
        return s_
    town_base = cy + 74
    inner.append(house(cx - 120, town_base + 6, 40, 34, "#B8312F", "#E8D8C0"))
    inner.append(house(cx + 70, town_base + 4, 44, 38, "#2F6A4C", "#F0E2CC"))
    inner.append(house(cx + 26, town_base + 10, 34, 28, "#4E6A9A", "#E0CDB4"))
    # church centre
    inner.append(f'<rect x="{cx - 34}" y="{town_base - 46}" width="52" height="52" fill="#EFE4D2"/><rect x="{cx - 4}" y="{town_base - 46}" width="22" height="52" fill="#000" opacity="0.1"/>'
                 f'<path d="M {cx - 38} {town_base - 44} L {cx - 8} {town_base - 72} L {cx + 22} {town_base - 44} Z" fill="#8E2234"/>'
                 f'<rect x="{cx - 16}" y="{town_base - 110}" width="18" height="60" fill="#F6EEE0"/><path d="M {cx - 19} {town_base - 108} L {cx - 7} {town_base - 150} L {cx + 5} {town_base - 108} Z" fill="#8E2234"/>'
                 f'<path d="M {cx - 19} {town_base - 108} L {cx - 7} {town_base - 150}" stroke="#FFFFFF" stroke-width="2.5"/>'
                 f'<circle cx="{cx - 7}" cy="{town_base - 90}" r="5" fill="#FFD27A"/><path d="M {cx - 16} {town_base + 6} L {cx - 16} {town_base - 12} Q {cx - 8} {town_base - 22} {cx} {town_base - 12} L {cx} {town_base + 6} Z" fill="#FFC45E"/>'
                 f'<rect x="{cx - 30}" y="{town_base - 32}" width="8" height="12" rx="4" fill="#FFD27A"/><rect x="{cx + 8}" y="{town_base - 32}" width="8" height="12" rx="4" fill="#FFD27A"/>')
    for tx, th in ((cx - 60, 50), (cx + 128, 44), (cx - 140, 36), (cx + 2, 30)):
        tsvg, _ = fir(D, tx, town_base + 14, th, th * 0.55, int(tx), light_c="#4E8A6A", mid="#2A5E48", dark="#173F30", tiers=4, snow=True, needles=False)
        inner.append(tsvg)
    # lamp post with glow + a skater on a tiny pond
    lx = cx + 62
    inner.append(f'<line x1="{lx}" y1="{town_base + 30}" x2="{lx}" y2="{town_base - 6}" stroke="#2A2A3A" stroke-width="3"/><circle cx="{lx}" cy="{town_base - 8}" r="4" fill="#FFE6A8"/>'
                 f'<circle cx="{lx}" cy="{town_base - 8}" r="22" fill="url(#{D.glow("#FFD98E", 0.6)})"/>')
    inner.append(f'<path d="M {cx - R} {town_base + 18} Q {cx} {town_base + 2} {cx + R} {town_base + 16} L {cx + R} {cy + R} L {cx - R} {cy + R} Z" fill="url(#{hill})"/>')
    inner.append(f'<ellipse cx="{cx - 40}" cy="{town_base + 44}" rx="54" ry="10" fill="#9FC4DA"/><ellipse cx="{cx - 52}" cy="{town_base + 41}" rx="20" ry="3" fill="#FFFFFF" opacity="0.6"/>')
    inner.append(figure(cx - 30, town_base + 46, 26, "#C7343A", scarf="#F6EDE0", hat="#2F6A4C"))
    inner.append(snowfall(7, 120, box=(cx - R, cy - R, cx + R, cy + R), r=(1, 3), op=(0.7, 1)))
    out.append(f'<g clip-path="url(#{c})">{"".join(inner)}</g>')
    # glass: edge darkening, rim light, window reflections
    edge = D.rg([(0, "#FFFFFF", 0), (0.78, "#FFFFFF", 0), (0.94, "#DDEBF4", 0.35), (1, "#FFFFFF", 0.7)])
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#{edge})"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#FFFFFF" stroke-width="2.5" opacity="0.7"/>')
    out.append(f'<path d="M {cx - 128} {cy - 40} A {R - 22} {R - 22} 0 0 1 {cx - 30} {cy - 134}" fill="none" stroke="#FFFFFF" stroke-width="16" stroke-linecap="round" opacity="0.55"/>')
    out.append(f'<path d="M {cx - 140} {cy + 10} A {R - 16} {R - 16} 0 0 1 {cx - 134} {cy - 26}" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round" opacity="0.5"/>')
    out.append(f'<rect x="{cx + 66}" y="{cy - 120}" width="22" height="34" rx="6" fill="#FFFFFF" opacity="0.45" transform="rotate(28 {cx + 77} {cy - 103})"/>'
               f'<rect x="{cx + 94}" y="{cy - 104}" width="12" height="28" rx="5" fill="#FFFFFF" opacity="0.35" transform="rotate(32 {cx + 100} {cy - 90})"/>')
    out.append(f'<path d="M {cx + 40} {cy + 152} A {R - 8} {R - 8} 0 0 0 {cx + 140} {cy + 60}" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" opacity="0.45"/>')
    out.append(twinkle(cx - 92, cy - 96, 14, "#FFFFFF") + twinkle(cx + 132, cy - 20, 9, "#FFFFFF", 0.8))
    out.append(f'<path d="M {cx - 124} 350 Q {cx} 380 {cx + 124} 350 L {cx + 126} 362 Q {cx} 394 {cx - 126} 362 Z" fill="url(#{gold})"/>'
               f'<path d="M {cx - 118} 352 Q {cx} 380 {cx + 118} 352" fill="none" stroke="#FFF6D0" stroke-width="2" opacity="0.8"/>')
    # type
    out.append(T(300, 534, "believe", SERIF_IT, 98, "#8E2234", max_w=380))
    return D.svg() + "\n".join(out)


# ======================================================================== NEW: painted objects
def icing_line(pts, w=9, seed=1, col="#FFFDF8", drips=0.35):
    """Piped royal icing along a polyline, with rounded drips hanging below."""
    rnd = random.Random(seed)
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    out = [f'<path d="{d}" fill="none" stroke="#C9A9A0" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" transform="translate(1.5 2.5)"/>',
           f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>']
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        for i in range(int(L / 16)):
            if rnd.random() < drips:
                t = (i + 0.5) / max(1, int(L / 16))
                x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                h = rnd.uniform(6, 16)
                out.append(f'<path d="M {x - w * 0.4:.1f} {y:.1f} L {x - w * 0.3:.1f} {y + h:.1f} A {w * 0.32:.1f} {w * 0.32:.1f} 0 0 0 {x + w * 0.3:.1f} {y + h:.1f} L {x + w * 0.4:.1f} {y:.1f} Z" fill="{col}"/>')
    out.append(f'<path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{w * 0.3:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="0.9" transform="translate(-1 -1.5)"/>')
    return "".join(out)


def gumdrop(D, x, y, r, col):
    return (f'<path d="M {x - r:.1f} {y:.1f} Q {x - r:.1f} {y - r * 1.5:.1f} {x:.1f} {y - r * 1.5:.1f} Q {x + r:.1f} {y - r * 1.5:.1f} {x + r:.1f} {y:.1f} Z" fill="url(#{D.ball(col)})"/>'
            + dots(int(r), int(x * 3 + y), (x - r * 0.7, y - r * 1.2, x + r * 0.7, y - 2), "#FFFFFF", r=(0.5, 1.1), opacity=(0.5, 0.9))
            + f'<ellipse cx="{x - r * 0.35:.1f}" cy="{y - r * 0.95:.1f}" rx="{r * 0.25:.1f}" ry="{r * 0.15:.1f}" fill="#FFFFFF" opacity="0.8"/>')


def peppermint(D, x, y, r, rot=0):
    sl = "".join(f'<path d="M {x} {y} L {x + r * math.cos(math.radians(a)):.1f} {y + r * math.sin(math.radians(a)):.1f} A {r} {r} 0 0 1 {x + r * math.cos(math.radians(a + 30)):.1f} {y + r * math.sin(math.radians(a + 30)):.1f} Z" fill="#D8262E"/>'
                 for a in range(rot, rot + 360, 60))
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="#FFFDF8"/>{sl}'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#{D.rg([(0, "#FFFFFF", 0), (0.7, "#FFFFFF", 0), (1, "#7A1A1E", 0.35)], fx=0.35, fy=0.35)})"/>'
            f'<ellipse cx="{x - r * 0.35:.1f}" cy="{y - r * 0.4:.1f}" rx="{r * 0.3:.1f}" ry="{r * 0.16:.1f}" fill="#FFFFFF" opacity="0.8" transform="rotate(-35 {x - r * 0.35:.1f} {y - r * 0.4:.1f})"/>')


def gingerbread_man(D, cx, cy, s, wave=True):
    from icons import gingerbread
    body = D.lg([(0, "#D08A4A"), (1, "#A05A2A")], 0, 0, 1, 1)
    return (f'<ellipse cx="{cx + 6}" cy="{cy + s * 0.7:.1f}" rx="{s * 0.5:.1f}" ry="{s * 0.08:.1f}" fill="#9A5A5A" opacity="0.3"/>'
            + gingerbread(cx + 3, cy + 4, s, body="#7A4020", icing="#7A4020", button="#7A4020")
            + gingerbread(cx, cy, s, body=f"url(#{body})", icing="#FFFDF8", button="#D8262E")
            + f'<path d="M {cx - s * 0.12:.1f} {cy - s * 0.92:.1f} A {s * 0.3:.1f} {s * 0.3:.1f} 0 0 0 {cx - s * 0.28:.1f} {cy - s * 0.62:.1f}" fill="none" stroke="#F0B47A" stroke-width="{max(1.5, s * 0.04):.1f}" stroke-linecap="round"/>')


def gingerbread_lane():
    u = "gbl"
    D = Defs(u)
    out = []
    bg = D.rg([(0, "#FCE8E2"), (0.7, "#F5D0C9"), (1, "#EAB0A9")], cy=0.45, r=0.78)
    out.append(f'<rect width="600" height="600" fill="url(#{bg})"/>')
    out.append('<g fill="#FFFFFF" opacity="0.55">' + "".join(f'<circle cx="{x + (20 if (y // 40) % 2 else 0)}" cy="{y}" r="3"/>' for x in range(0, 620, 40) for y in range(10, 620, 40)) + "</g>")
    out.append(soft_flakes(D, 3, 14, r=(6, 12), s=0.6, avoid=[(60, 60, 540, 260)]))
    # icing snow ground
    out.append(f'<path d="M -10 478 Q 120 458 300 472 Q 470 486 610 466 L 610 600 L -10 600 Z" fill="#FFFDF8"/>')
    out.append(f'<path d="M -10 478 Q 120 458 300 472 Q 470 486 610 466" fill="none" stroke="#E9C8C4" stroke-width="4"/>')
    out.append(dots(80, 7, (0, 480, 600, 600), "#F2A8B0", r=(0.8, 1.8), opacity=(0.4, 0.9)))
    F0, F1, F2, F3, A = (198, 488), (372, 488), (372, 362), (198, 362), (285, 272)
    v = (82, -30)
    add = lambda p, s_=1: (p[0] + v[0] * s_, p[1] + v[1] * s_)
    out.append(f'<ellipse cx="320" cy="490" rx="200" ry="16" fill="#C98E8E" opacity="0.35"/>')
    out.append('<g transform="translate(290 498) scale(1.03) translate(-290 -490)">')
    dough = D.lg([(0, "#D48C4C"), (1, "#A65C2A")], 0, 0, 1, 1)
    side = [F1, add(F1), add(F2), F2]
    out.append(f'<polygon points="{P(side)}" fill="#8A4A22"/>')
    front = [F0, F1, F2, A, F3]
    out.append(f'<polygon points="{P(front)}" fill="url(#{dough})"/>')
    c1 = D.clip(f'<polygon points="{P(front)}"/><polygon points="{P(side)}"/>')
    out.append(f'<g clip-path="url(#{c1})">{dots(260, 5, (190, 260, 460, 490), "#7A3A18", r=(0.6, 1.5), opacity=(0.2, 0.5))}{dots(120, 6, (190, 260, 460, 490), "#F0B47A", r=(0.6, 1.3), opacity=(0.3, 0.6))}</g>')
    # roof: candy-wafer shingles on the visible slope
    E0, E1 = (F2[0] + 14, F2[1] + 8), add((F2[0] + 14, F2[1] + 8))
    R0, R1 = (A[0], A[1] - 6), add((A[0], A[1] - 6))
    roof = [R0, R1, E1, E0]
    out.append(f'<polygon points="{P(roof)}" fill="#F7E7E0"/>')
    c2 = D.clip(f'<polygon points="{P(roof)}"/>')
    sh = []
    rows = 7
    for i in range(rows + 1):
        f = i / rows
        a = (R0[0] + (E0[0] - R0[0]) * f, R0[1] + (E0[1] - R0[1]) * f)
        b = (R1[0] + (E1[0] - R1[0]) * f, R1[1] + (E1[1] - R1[1]) * f)
        n = 7
        for j in range(-1, n + 1):
            t = (j + (0.5 if i % 2 else 0)) / n
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            col = ["#F4A6B4", "#FFFDF8", "#E8707E"][(i + j) % 3]
            sh.append(f'<circle cx="{x:.1f}" cy="{y + 6:.1f}" r="10" fill="{col}" stroke="#C25A6A" stroke-width="1.5"/>')
    out.append(f'<g clip-path="url(#{c2})">{"".join(sh)}<polygon points="{P(roof)}" fill="url(#{D.lg([(0, "#FFFFFF", 0.25), (1, "#7A2A3A", 0.25)], 0, 0, 1, 1)})"/></g>')
    # chimney
    ch = [(392, 316), (416, 308), (416, 270), (392, 278)]
    out.append(f'<polygon points="{P(ch)}" fill="url(#{dough})"/><polygon points="{P([(416, 308), (424, 305), (424, 267), (416, 270)])}" fill="#8A4A22"/>')
    out.append(icing_line([(388, 278), (404, 272), (426, 266)], w=8, seed=9, drips=0.6))
    out.append(gumdrop(D, 408, 268, 9, "#4CB27A"))
    # icing on the gable edges and eaves
    out.append(icing_line([(F3[0] - 16, F3[1] + 10), (A[0], A[1] - 8), (F2[0] + 16, F2[1] + 10)], w=12, seed=2, drips=0.55))
    out.append(icing_line([(E0[0], E0[1] + 2), (E1[0], E1[1] + 2)], w=9, seed=3, drips=0.5))
    out.append(icing_line([R0, R1], w=8, seed=4, drips=0))
    for k in range(5):
        t = (k + 0.5) / 5
        out.append(f'<circle cx="{R0[0] + v[0] * t:.1f}" cy="{R0[1] + v[1] * t - 6:.1f}" r="6" fill="url(#{D.ball(["#D8262E", "#4CB27A", "#F2C25A"][k % 3])})"/>')
    # peppermint in the gable
    out.append(peppermint(D, A[0], A[1] + 44, 20, rot=10))
    out.append(f'<circle cx="{A[0]}" cy="{A[1] + 44}" r="23" fill="none" stroke="#FFFDF8" stroke-width="4" stroke-dasharray="1 6" stroke-linecap="round"/>')
    # windows with piped frames
    for wx in (214, 316):
        out.append(f'<circle cx="{wx + 20}" cy="{392}" r="40" fill="url(#{D.glow("#FFD27A", 0.5)})"/>'
                   f'<rect x="{wx}" y="374" width="40" height="38" rx="3" fill="#FFD27A"/><rect x="{wx}" y="374" width="40" height="12" fill="#FFF0C0"/>'
                   f'<path d="M {wx + 20} 374 L {wx + 20} 412 M {wx} 393 L {wx + 40} 393" stroke="#FFFDF8" stroke-width="4"/>'
                   f'<rect x="{wx - 2}" y="372" width="44" height="42" rx="4" fill="none" stroke="#FFFDF8" stroke-width="4" stroke-dasharray="1 7" stroke-linecap="round"/>'
                   f'<path d="M {wx - 6} 416 Q {wx + 20} 424 {wx + 46} 416" stroke="#FFFDF8" stroke-width="5" fill="none" stroke-linecap="round"/>')
    # side window
    sw = [(392, 400), (420, 390), (420, 420), (392, 430)]
    out.append(f'<polygon points="{P(sw)}" fill="#F7C25A"/><polygon points="{P(sw)}" fill="none" stroke="#FFFDF8" stroke-width="3.5" stroke-linejoin="round"/>')
    # door with candy-cane pillars
    out.append(f'<path d="M 266 488 L 266 440 Q 285 418 304 440 L 304 488 Z" fill="#5A2A16"/>'
               f'<path d="M 266 488 L 266 440 Q 285 418 304 440 L 304 488" fill="none" stroke="#FFFDF8" stroke-width="4" stroke-linecap="round"/>'
               f'<circle cx="296" cy="466" r="3.5" fill="#F2C25A"/>')
    for px in (254, 316):
        mid = D.id("m")
        out.append(f'<mask id="{mid}"><rect x="{px - 5}" y="426" width="10" height="62" fill="#FFFFFF"/></mask><rect x="{px - 5}" y="426" width="10" height="62" fill="#FFFDF8"/>'
                   f'<g mask="url(#{mid})">' + "".join(f'<line x1="{px - 10}" y1="{y}" x2="{px + 10}" y2="{y - 10}" stroke="#D8262E" stroke-width="4"/>' for y in range(426, 500, 9)) + "</g>")
    # gumdrop border along the base
    for i, x in enumerate(range(206, 372, 22)):
        out.append(gumdrop(D, x, 490, 9, ["#D8262E", "#4CB27A", "#F2C25A", "#F48AA0"][i % 4]))
    out.append("</g>")
    # gingerbread man waving beside the house + candy cane and lollipop in the snow
    out.append(gingerbread_man(D, 478, 470, 70))
    out.append(f'<g transform="rotate(-8 130 470)">' + f'<rect x="126" y="400" width="6" height="84" rx="3" fill="#FFFDF8"/>' + peppermint(D, 129, 392, 26, rot=0) + "</g>")
    out.append(snowfall(6, 50, box=(0, 0, 600, 600), r=(1.4, 3.4), op=(0.6, 1), avoid=[(60, 60, 540, 250)]))
    # type
    out.append(TS(300, 122, "gingerbread", SERIF_IT, 82, "#7A3A1E", "#FFFFFF", dy=4, max_w=470))
    out.append(T(300, 214, "LANE", BEBAS, 92, "#C7343A", ls=24, max_w=300))
    out.append(side_rules(182, "LANE", BEBAS, 92, 24, "#C7343A", max_w=300, L=56))
    return D.svg() + "\n".join(out)


def stocking(D, x, top, s, col, cuff, kind="stripes", accent="#FFFDF8", rot=0, flip=False):
    """Knit stocking hanging from (x, top), toe pointing left (or right if flip)."""
    g = D.lg([(0, lt(col, 0.15)), (0.6, col), (1, dk(col, 0.3))], 0, 0, 1, 0)
    shape = "M -30 0 L 30 0 L 32 104 C 34 146 10 166 -22 166 L -62 164 C -90 162 -94 120 -66 112 L -30 104 Z"
    c = D.clip(f'<path d="{shape}"/>')
    pat = []
    if kind == "stripes":
        pat += [f'<rect x="-100" y="{y}" width="200" height="12" fill="{accent}"/>' for y in range(42, 170, 30)]
    elif kind == "flake":
        pat += [f'<g stroke="{accent}" stroke-width="4" stroke-linecap="round">' + "".join(
            f'<line x1="0" y1="70" x2="{22 * math.cos(math.radians(a)):.1f}" y2="{70 + 22 * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 60)) + "</g>"]
        pat += [f'<circle cx="{xx}" cy="{yy}" r="3" fill="{accent}"/>' for xx, yy in ((-20, 50), (20, 46), (-16, 100), (18, 96), (-50, 140), (0, 140))]
    elif kind == "dots":
        pat += [f'<circle cx="{xx + (8 if (yy // 16) % 2 else 0)}" cy="{yy}" r="3.6" fill="{accent}"/>' for xx in range(-96, 40, 16) for yy in range(40, 170, 16)]
    pat.append(f'<path d="M -66 112 C -94 120 -90 162 -62 164 L -46 165 C -60 150 -62 128 -50 112 Z" fill="{dk(col, 0.25)}"/>')
    pat.append(f'<path d="M 32 104 C 34 130 26 150 12 160 L 8 120 Z" fill="{dk(col, 0.3)}" opacity="0.6"/>')
    knit = "".join(f'<path d="M {xx} {yy} l 3 4 l 3 -4"/>' for xx in range(-96, 36, 7) for yy in range(30, 170, 6))
    pat.append(f'<g fill="none" stroke="#000" stroke-width="1" opacity="0.12">{knit}</g>')
    sx = -s if flip else s
    return (f'<g transform="translate({x} {top}) rotate({rot}) scale({sx} {s})">'
            f'<path d="{shape}" fill="#000" opacity="0.25" transform="translate(6 6)"/>'
            f'<path d="{shape}" fill="url(#{g})"/><g clip-path="url(#{c})">{"".join(pat)}</g>'
            f'<path d="M -22 8 L -22 150" stroke="#FFFFFF" stroke-width="5" opacity="0.18" stroke-linecap="round"/>'
            f'<rect x="-36" y="-6" width="72" height="38" rx="10" fill="{cuff}"/>'
            + "".join(f'<circle cx="{xx}" cy="{yy}" r="{r}" fill="{lt(cuff, 0.4)}"/>' for xx, yy, r in ((-24, 2, 7), (-6, 0, 8), (14, 2, 7), (28, 8, 5), (-28, 20, 6), (0, 22, 7), (22, 24, 6)))
            + f'<rect x="-36" y="22" width="72" height="10" rx="5" fill="{dk(cuff, 0.12)}" opacity="0.6"/>'
            f'<path d="M -6 -6 Q 0 -22 6 -6" fill="none" stroke="{dk(cuff, 0.2)}" stroke-width="3"/>'
            "</g>")


def hung_with_care():
    u = "hwc"
    D = Defs(u)
    out = []
    wall = D.lg([(0, "#7E2030"), (1, "#5A1420")])
    out.append(f'<rect width="600" height="600" fill="url(#{wall})"/>')
    out.append('<g fill="#E2B04A" opacity="0.22">' + "".join(f'<rect x="{x - 4 + (24 if (y // 48) % 2 else 0)}" y="{y - 4}" width="8" height="8" transform="rotate(45 {x + (24 if (y // 48) % 2 else 0)} {y})"/>' for x in range(0, 620, 48) for y in range(0, 620, 48)) + "</g>")
    out.append(pt.glow(300, 470, 300, "#FFB060", f"{u}-fire", 0.5))
    # mantel
    cream = D.lg([(0, "#FBF5EA"), (1, "#E2D4BE")])
    out.append(f'<rect x="88" y="290" width="424" height="310" fill="url(#{cream})"/>')
    out.append('<rect x="100" y="300" width="400" height="56" fill="#EFE4D2"/><rect x="100" y="352" width="400" height="4" fill="#C9B79C"/>')
    out.append('<rect x="88" y="356" width="70" height="244" fill="#F4ECDE"/><rect x="442" y="356" width="70" height="244" fill="#E6D8C2"/>')
    out.append('<rect x="100" y="372" width="46" height="228" fill="none" stroke="#D2C2A8" stroke-width="2.5"/><rect x="454" y="372" width="46" height="228" fill="none" stroke="#C2B094" stroke-width="2.5"/>')
    # firebox with bricks and a fire
    out.append('<rect x="158" y="356" width="284" height="244" fill="#1A0E0C"/>')
    c = D.clip('<rect x="168" y="366" width="264" height="234"/>')
    bricks = "".join(f'<rect x="{x + (14 if (y // 14) % 2 else 0)}" y="{y}" width="26" height="12" rx="1" fill="#5A2A20"/>' for x in range(150, 450, 28) for y in range(366, 600, 14))
    out.append(f'<g clip-path="url(#{c})"><rect x="168" y="366" width="264" height="234" fill="#2A1410"/>{bricks}'
               f'<rect x="168" y="366" width="264" height="234" fill="url(#{D.rg([(0, "#FF9A3A", 0.75), (0.5, "#C2501E", 0.4), (1, "#1A0A08", 0.85)], cy=0.85, r=0.7)})"/></g>')
    out.append(f'<rect x="158" y="356" width="284" height="10" fill="#C9B79C"/>')
    # logs and flames
    out.append('<g><rect x="214" y="532" width="170" height="22" rx="11" fill="#4A2A18" transform="rotate(-6 300 543)"/><rect x="220" y="540" width="160" height="22" rx="11" fill="#5E3820" transform="rotate(7 300 551)"/>'
               '<circle cx="222" cy="552" r="9" fill="#C8955E"/><circle cx="380" cy="548" r="9" fill="#B9844E"/></g>')
    fl = D.lg([(0, "#FFF2B0"), (0.4, "#FFC24A"), (1, "#E2541E")], 0, 1, 0, 0)
    for fx, fh, fw in ((262, 120, 34), (300, 150, 42), (338, 110, 32), (284, 90, 24), (320, 96, 22)):
        out.append(f'<path d="M {fx - fw} 546 C {fx - fw} {546 - fh * 0.5} {fx - fw * 0.2} {546 - fh * 0.7} {fx} {546 - fh} C {fx + fw * 0.2} {546 - fh * 0.6} {fx + fw} {546 - fh * 0.5} {fx + fw} 546 Z" fill="url(#{fl})" opacity="0.92"/>')
    out.append(f'<ellipse cx="300" cy="520" rx="60" ry="40" fill="url(#{D.glow("#FFF2B0", 0.6)})"/>')
    out.append(dots(16, 4, (230, 400, 370, 470), "#FFD27A", r=(1, 2), opacity=(0.6, 1)))
    out.append('<rect x="60" y="586" width="480" height="20" fill="#5A4A48"/>')
    # shelf
    out.append('<rect x="70" y="276" width="460" height="18" rx="3" fill="#FFFBF2"/><rect x="70" y="292" width="460" height="6" fill="#000" opacity="0.25"/>')
    # candles at both ends
    for cx_ in (104, 496):
        out.append(f'<circle cx="{cx_}" cy="226" r="46" fill="url(#{D.glow("#FFD98E", 0.6)})"/>'
                   f'<rect x="{cx_ - 13}" y="236" width="26" height="40" rx="3" fill="#FBF3E2"/><rect x="{cx_ + 4}" y="236" width="9" height="40" fill="#000" opacity="0.08"/>'
                   f'<path d="M {cx_} 233 q -7 -10 0 -22 q 7 12 0 22 Z" fill="#FFC24A"/><path d="M {cx_} 231 q -3 -5 0 -11 q 3 6 0 11 Z" fill="#FFF6D0"/>'
                   f'<rect x="{cx_ - 20}" y="268" width="40" height="8" rx="3" fill="#D9A441"/>')
    # garland along the shelf
    rnd = random.Random(7)
    st = []
    gl = [(x, 278 + 6 * math.sin(x / 40)) for x in range(70, 534, 4)]
    for x, y in gl:
        for _ in range(3):
            a = rnd.uniform(-170, -10) if rnd.random() < 0.6 else rnd.uniform(10, 170)
            L = rnd.uniform(10, 20)
            st.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + L * math.cos(math.radians(a)):.1f}" y2="{y + L * math.sin(math.radians(a)) * 0.8:.1f}" stroke="{rnd.choice(["#1E4A38", "#2A5E46", "#163A2C", "#3E7456"])}"/>')
    out.append(f'<g stroke-width="2.6" stroke-linecap="round">{"".join(st)}</g>')
    for i, x in enumerate(range(84, 530, 26)):
        y = 278 + 6 * math.sin(x / 40) + rnd.uniform(-8, 6)
        out.append(light(D, x, y, 2.6, "#FFD98E", halo=4.5))
    for x in (150, 220, 380, 450):
        out.append(f'<ellipse cx="{x}" cy="270" rx="7" ry="11" fill="#7A4A2A" transform="rotate(30 {x} 270)"/><g stroke="#4A2A18" stroke-width="1.5" transform="rotate(30 {x} 270)">'
                   + "".join(f'<line x1="{x - 6}" y1="{270 + d}" x2="{x + 6}" y2="{270 + d}"/>' for d in (-6, -2, 2, 6)) + "</g>")
    for x, col in ((186, "#E2B04A"), (300, "#C7343A"), (414, "#E2B04A"), (256, "#C7343A"), (344, "#E2B04A")):
        out.append(ball(D, x, 284, 8, col, hook=False))
    out.append("".join(f'<circle cx="{x}" cy="{y}" r="4" fill="url(#{D.ball("#C7262E")})"/>' for x, y in ((120, 286), (126, 280), (478, 282), (472, 288), (230, 290), (236, 284), (366, 288))))
    # hooks + stockings
    for x in (180, 300, 420):
        out.append(f'<path d="M {x} 292 l 0 12 q 0 6 6 6" fill="none" stroke="#C9A04A" stroke-width="3.5" stroke-linecap="round"/>')
    out.append(stocking(D, 182, 300, 0.9, "#B8262E", "#FBF6EE", kind="stripes", accent="#FBF6EE", rot=2))
    out.append(stocking(D, 302, 300, 0.95, "#1F5A44", "#FBF6EE", kind="flake", accent="#FBF6EE", rot=-1))
    out.append(stocking(D, 422, 300, 0.9, "#F4E6D0", "#B8262E", kind="dots", accent="#C7343A", rot=1))
    # type
    out.append(T(300, 104, "THE STOCKINGS WERE", MONO, 19, "#F2D9A0", ls=6, max_w=380))
    out.append('<g stroke="#F2D9A0" stroke-width="2" opacity="0.8"><line x1="66" y1="98" x2="98" y2="98"/><line x1="502" y1="98" x2="534" y2="98"/></g>')
    out.append(TS(300, 196, "hung with care", SERIF_IT, 84, "#FBF3E6", "#2A0A10", dy=5, max_w=460))
    return D.svg() + "\n".join(out)


def wrapped_with_love():
    u = "wwl"
    D = Defs(u)
    out = []
    bg = D.rg([(0, "#FCE6E4"), (0.7, "#F6D0CE"), (1, "#EDB4B2")], cy=0.55, r=0.78)
    out.append(f'<rect width="600" height="600" fill="url(#{bg})"/>')
    from common import heart
    out.append('<g opacity="0.5">' + "".join(heart(x + (22 if (y // 44) % 2 else 0), y, 6, "#FFFFFF") for x in range(0, 620, 44) for y in range(10, 620, 44)) + "</g>")
    out.append(f'<ellipse cx="300" cy="530" rx="190" ry="18" fill="#B86A72" opacity="0.3"/>')
    out.append('<g transform="translate(0 6)">')
    out.append(gift(D, 158, 528, 236, 116, 62, "#C8303A", "#F4A6B4", pattern="dots", pcol="#FBEDEA", bow=False))
    out.append(gift(D, 196, 416, 176, 90, 50, "#F4A6B4", "#C8303A", pattern="stripes", pcol="#FBEDEA", bow=False, tilt=-3))
    out.append(gift(D, 238, 330, 104, 70, 36, "#FBF3EA", "#C8303A", pattern="hearts", pcol="#E8707E", bow=False, tilt=4))
    # big bow on top
    out.append(f'<g transform="rotate(4 290 330)">' + bow_svg(304, 254, 52, "#C8303A") + "</g>")
    out.append("</g>")
    # tag on a string
    out.append('<path d="M 400 384 Q 430 420 444 452" fill="none" stroke="#C8303A" stroke-width="2.5"/>')
    tag = D.lg([(0, "#F2DDBE"), (1, "#D9BC94")])
    out.append(f'<g transform="rotate(-14 470 470)"><path d="M 436 452 L 450 438 L 520 438 L 520 494 L 450 494 L 436 480 Z" fill="#000" opacity="0.2" transform="translate(4 5)"/>'
               f'<path d="M 436 452 L 450 438 L 520 438 L 520 494 L 450 494 L 436 480 Z" fill="url(#{tag})"/><circle cx="450" cy="466" r="4" fill="#C9A87A"/>'
               + heart(486, 468, 13, "#C8303A") + "</g>")
    # sprig of pine + berries tucked under the bow
    rnd = random.Random(3)
    out.append('<g stroke-width="2.4" stroke-linecap="round">' + "".join(
        f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + rnd.uniform(-14, 14):.1f}" y2="{y + rnd.uniform(-12, 4):.1f}" stroke="{rnd.choice(["#2A5E46", "#1E4A38", "#3E7456"])}"/>'
        for x, y in [(330 + i * 2.4, 262 - i * 0.4) for i in range(16)] for _ in range(3)) + "</g>")
    out.append("".join(f'<circle cx="{x}" cy="{y}" r="5" fill="url(#{D.ball("#B8262E")})"/>' for x, y in ((338, 262), (346, 268), (346, 257))))
    # confetti
    out.append("".join(twinkle(x, y, r, c) for x, y, r, c in ((104, 300, 10, "#C8303A"), (500, 290, 12, "#E2B04A"), (86, 430, 7, "#E2B04A"), (520, 380, 7, "#C8303A"))))
    # type
    out.append(T(300, 128, "wrapped with", SERIF_IT, 84, "#C8303A", max_w=440))
    out.append(T(300, 208, "LOVE", JOS, 84, "#8E1E2A", ls=26, max_w=320))
    out.append(side_rules(177, "LOVE", JOS, 84, 26, "#8E1E2A", max_w=320, L=44, star=False))
    return D.svg() + "\n".join(out)


def wreath(D, cx, cy, R, seed, bow_col="#B8262E"):
    rnd = random.Random(seed)
    out = [f'<circle cx="{cx + 6}" cy="{cy + 9}" r="{R}" fill="none" stroke="#000" stroke-width="{R * 0.5:.1f}" opacity="0.28"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#163A2C" stroke-width="{R * 0.5:.1f}"/>']
    st = []
    for i in range(int(R * 9)):
        a = rnd.uniform(0, 2 * math.pi)
        rr = R + rnd.uniform(-R * 0.26, R * 0.26)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        ta = a + math.pi / 2 + rnd.uniform(-0.6, 0.6)
        L = rnd.uniform(R * 0.12, R * 0.24)
        litf = -math.cos(a + math.radians(45))
        col = rnd.choice(["#4E8A5E", "#5C9A6A", "#3E7456"]) if litf > 0.2 and rnd.random() < 0.8 else rnd.choice(["#1E4A38", "#2A5E46", "#163A2C"])
        st.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + L * math.cos(ta):.1f}" y2="{y + L * math.sin(ta):.1f}" stroke="{col}"/>')
    out.append(f'<g stroke-width="{max(2, R * 0.04):.1f}" stroke-linecap="round">{"".join(st)}</g>')
    for i in range(9):
        a = math.radians(i * 40 + 10)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        if math.sin(a) > 0.8:
            continue
        for dx, dy in ((0, 0), (R * 0.07, R * 0.05), (-R * 0.05, R * 0.06)):
            out.append(f'<circle cx="{x + dx:.1f}" cy="{y + dy:.1f}" r="{R * 0.055:.1f}" fill="url(#{D.ball("#C7262E")})"/>')
    for a in (200, 330, 60):
        x, y = cx + R * 1.02 * math.cos(math.radians(a)), cy + R * 1.02 * math.sin(math.radians(a))
        out.append(f'<g transform="rotate({a + 90} {x:.1f} {y:.1f})"><ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{R * 0.09:.1f}" ry="{R * 0.15:.1f}" fill="#7A4A2A"/>'
                   + "".join(f'<path d="M {x - R * 0.08:.1f} {y + d * R:.1f} q {R * 0.08:.1f} {R * 0.04:.1f} {R * 0.16:.1f} 0" fill="none" stroke="#4A2A18" stroke-width="1.6"/>' for d in (-0.08, -0.02, 0.04, 0.1)) + "</g>")
    for a in (150, 20, 270):
        x, y = cx + R * 0.95 * math.cos(math.radians(a)), cy + R * 0.95 * math.sin(math.radians(a))
        out.append(ball(D, x, y, R * 0.08, "#E2B04A", hook=False))
    # velvet bow at the bottom with long tails
    bx, by = cx, cy + R * 0.95
    hi, lo = lt(bow_col, 0.3), dk(bow_col, 0.3)
    s = R * 0.55
    out.append(f'<path d="M {bx - s * 0.1:.1f} {by:.1f} C {bx - s * 0.3:.1f} {by + s * 0.8:.1f} {bx - s * 0.5:.1f} {by + s * 1.2:.1f} {bx - s * 0.7:.1f} {by + s * 1.6:.1f} L {bx - s * 0.42:.1f} {by + s * 1.5:.1f} L {bx - s * 0.36:.1f} {by + s * 1.75:.1f} C {bx - s * 0.16:.1f} {by + s * 1.1:.1f} {bx:.1f} {by + s * 0.6:.1f} {bx + s * 0.06:.1f} {by:.1f} Z" fill="{lo}"/>'
               f'<path d="M {bx + s * 0.1:.1f} {by:.1f} C {bx + s * 0.3:.1f} {by + s * 0.8:.1f} {bx + s * 0.4:.1f} {by + s * 1.2:.1f} {bx + s * 0.6:.1f} {by + s * 1.7:.1f} L {bx + s * 0.32:.1f} {by + s * 1.6:.1f} L {bx + s * 0.26:.1f} {by + s * 1.82:.1f} C {bx + s * 0.1:.1f} {by + s * 1.1:.1f} {bx:.1f} {by + s * 0.6:.1f} {bx - s * 0.06:.1f} {by:.1f} Z" fill="{dk(bow_col, 0.15)}"/>')
    out.append(bow_svg(bx, by, s, bow_col))
    return "".join(out)


def seasons_greetings():
    u = "ssg"
    D = Defs(u)
    out = []
    wall = D.lg([(0, "#EDE4D4"), (1, "#D9CCB6")])
    out.append(f'<rect width="600" height="600" fill="url(#{wall})"/>')
    out.append('<g>' + "".join(f'<rect x="0" y="{y}" width="600" height="3" fill="#B8A88E" opacity="0.6"/><rect x="0" y="{y + 3}" width="600" height="2" fill="#FFFFFF" opacity="0.5"/>' for y in range(14, 440, 24)) + "</g>")
    out.append(f'<rect x="0" y="0" width="600" height="440" fill="url(#{D.lg([(0, "#1A2A44", 0.25), (0.5, "#1A2A44", 0), (1, "#1A2A44", 0.2)], 0, 0, 1, 0)})"/>')
    snow = D.lg([(0, "#E4ECF4"), (1, "#FFFFFF")])
    out.append(f'<path d="M -10 418 Q 150 410 300 418 Q 450 426 610 412 L 610 600 L -10 600 Z" fill="url(#{snow})"/>')
    out.append('<g transform="translate(24 4.8) scale(0.92)">')
    # pediment + trim
    out.append('<path d="M 180 108 L 300 66 L 420 108 Z" fill="#FBF7EE"/><path d="M 194 104 L 300 78 L 406 104 Z" fill="#E6DCCA"/>'
               '<rect x="176" y="106" width="248" height="16" fill="#FBF7EE"/><rect x="176" y="120" width="248" height="4" fill="#000" opacity="0.15"/>')
    out.append('<rect x="192" y="122" width="216" height="292" fill="#FBF7EE"/><rect x="192" y="122" width="20" height="292" fill="#FFFFFF"/><rect x="388" y="122" width="20" height="292" fill="#E6DCCA"/>')
    # transom
    out.append('<rect x="214" y="128" width="172" height="34" fill="#2A3A54"/>' + "".join(f'<line x1="{x}" y1="128" x2="{x}" y2="162" stroke="#FBF7EE" stroke-width="3"/>' for x in (257, 300, 343))
               + f'<rect x="214" y="128" width="172" height="34" fill="url(#{D.lg([(0, "#FFD98E", 0.55), (1, "#FFD98E", 0.1)])})"/>')
    # door
    door = D.lg([(0, "#C2303A"), (0.5, "#A8232E"), (1, "#7E141C")], 0, 0, 1, 0)
    out.append(f'<rect x="214" y="166" width="172" height="248" fill="url(#{door})"/>')
    for x, y, w, h in ((228, 178, 64, 96), (308, 178, 64, 96), (228, 290, 64, 110), (308, 290, 64, 110)):
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#9A1E28"/><path d="M {x} {y + h} L {x} {y} L {x + w} {y}" fill="none" stroke="#6E1018" stroke-width="4"/>'
                   f'<path d="M {x} {y + h} L {x + w} {y + h} L {x + w} {y}" fill="none" stroke="#D84A52" stroke-width="3"/>')
    brass = D.lg([(0, "#FFF0B0"), (0.5, "#D9A441"), (1, "#8A5A14")], 0, 0, 1, 1)
    out.append(f'<circle cx="370" cy="300" r="8" fill="url(#{brass})"/><rect x="226" y="396" width="148" height="14" rx="2" fill="url(#{brass})"/>')
    out.append(f'<rect x="290" y="282" width="20" height="8" rx="2" fill="url(#{brass})"/>')
    out.append(wreath(D, 300, 226, 58, 5))
    # brass lanterns either side, glowing
    for lx in (128, 472):
        out.append(f'<circle cx="{lx}" cy="226" r="80" fill="url(#{D.glow("#FFD98E", 0.55)})"/>'
                   f'<rect x="{lx - 3}" y="170" width="6" height="16" fill="#2A2420"/><path d="M {lx - 20} 194 L {lx} 180 L {lx + 20} 194 Z" fill="#2A2420"/>'
                   f'<rect x="{lx - 16}" y="194" width="32" height="54" rx="2" fill="#FFE6A8" stroke="#2A2420" stroke-width="4"/>'
                   f'<line x1="{lx}" y1="194" x2="{lx}" y2="248" stroke="#2A2420" stroke-width="2.5"/><path d="M {lx - 6} 232 q 6 -16 6 -24 q 0 8 6 24 Z" fill="#FFB84A"/>'
                   f'<path d="M {lx - 20} 248 L {lx + 20} 248 L {lx + 12} 258 L {lx - 12} 258 Z" fill="#2A2420"/>')
    # garland swag over the door
    rnd = random.Random(9)
    st = []
    for i in range(70):
        t = i / 69
        x = 176 + 248 * t
        y = 112 + 26 * math.sin(math.pi * t) - 6
        for _ in range(3):
            st.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + rnd.uniform(-12, 12):.1f}" y2="{y + rnd.uniform(-10, 10):.1f}" stroke="{rnd.choice(["#1E4A38", "#2A5E46", "#3E7456"])}"/>')
    out.append(f'<g stroke-width="2.6" stroke-linecap="round">{"".join(st)}</g>')
    for i in range(9):
        t = (i + 0.5) / 9
        out.append(light(D, 176 + 248 * t, 112 + 26 * math.sin(math.pi * t) - 2, 2.6, "#FFD98E", halo=4))
    # step, snow, potted trees
    out.append('<rect x="150" y="414" width="300" height="20" fill="#9A9AA6"/><rect x="150" y="414" width="300" height="4" fill="#C8C8D2"/><rect x="130" y="432" width="340" height="16" fill="#86869A"/>')
    out.append(snow_cap([(150 + i * 25, 414) for i in range(13)], thick=6, seed=3))
    for px in (110, 490):
        out.append(f'<path d="M {px - 30} 446 L {px - 24} 400 L {px + 24} 400 L {px + 30} 446 Z" fill="#2A3A54"/><rect x="{px - 28}" y="396" width="56" height="10" rx="2" fill="#3A4A66"/>')
        tsvg, tiers = fir(D, px, 400, 140, 80, px, light_c="#4E8A5E", mid="#2A5E46", dark="#163A2C", tiers=5, snow=True, needles=True)
        out.append(tsvg)
        rr = random.Random(px)
        for k, (apex, hem, hw) in enumerate(tiers):
            for _ in range(2 + k):
                y = rr.uniform(apex + (hem - apex) * 0.4, hem - 4)
                lim = hw * (y - apex) / (hem - apex) * 0.8
                out.append(light(D, rr.uniform(px - lim, px + lim), y, 2, "#FFD98E", halo=4))
    out.append("</g>")
    out.append(dots(40, 4, (0, 430, 600, 600), "#B9C9DA", r=(1, 2.4), opacity=(0.5, 0.9)))
    out.append(snowfall(8, 80, r=(1.2, 3), op=(0.6, 1)))
    # type on the snow
    out.append(T(300, 482, "season's", SERIF_IT, 78, "#A8232E", max_w=380))
    out.append(T(300, 538, "GREETINGS", BEBAS, 64, "#1E4D3A", ls=16, max_w=420))
    return D.svg() + "\n".join(out)


def reindeer(D, ox=0, oy=0, k=1.0):
    """Reindeer standing in profile facing left, antlers wound with lights. Drawn in a 600 box, then offset/scaled."""
    coat = D.lg([(0, "#5A3C2A"), (0.55, "#8A6446"), (1, "#C9A880")])
    ant = D.lg([(0, "#F2E2C2"), (1, "#C2A27A")])
    o = [f'<g transform="translate({ox} {oy}) scale({k})">']
    o.append('<ellipse cx="330" cy="442" rx="150" ry="12" fill="#7A9AB0" opacity="0.35"/>')
    # far legs (darker)
    o.append('<path d="M 258 360 C 266 380 260 396 262 408 C 263 420 261 430 262 438 L 272 438 C 273 428 272 416 274 406 C 277 394 282 380 284 366 Z" fill="#4A3224"/>')
    o.append('<path d="M 404 350 C 420 370 428 384 424 398 C 421 410 418 422 419 438 L 430 438 C 430 424 434 412 437 400 C 442 384 442 366 436 348 Z" fill="#4A3224"/>')
    # far antler
    def antler(dx, dy, col, w):
        paths = ["M 200 222 C 194 190 204 160 228 140 C 244 126 248 108 244 90",
                 "M 202 196 C 190 188 178 182 170 166", "M 212 168 C 208 154 206 140 210 126",
                 "M 232 138 C 246 132 260 124 266 106", "M 244 108 C 252 100 258 92 270 88",
                 "M 199 214 C 188 212 176 206 168 196"]
        return f'<g transform="translate({dx} {dy})" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round">' + "".join(f'<path d="{d}"/>' for d in paths) + "</g>"
    o.append(antler(16, -6, "#A8885E", 8))
    # body
    body = "M 210 330 C 205 296 236 282 280 286 C 330 290 390 282 430 290 C 462 296 476 322 470 350 C 464 372 446 380 430 378 C 390 376 330 380 280 378 C 240 376 214 360 210 330 Z"
    o.append(f'<path d="{body}" fill="url(#{coat})"/>')
    o.append('<path d="M 470 300 C 482 296 488 306 480 314 C 474 318 468 312 470 300 Z" fill="#F4ECE0"/>')
    rnd = random.Random(4)
    fur = "".join(f'<path d="M {x:.1f} {y:.1f} q 4 3 9 3"/>' for x, y in [(rnd.uniform(240, 455), rnd.uniform(296, 368)) for _ in range(70)])
    o.append(f'<g fill="none" stroke="#3E2A1E" stroke-width="1.6" opacity="0.35" stroke-linecap="round">{fur}</g>')
    o.append('<path d="M 236 296 C 280 286 340 292 400 286 C 430 284 456 292 466 306" fill="none" stroke="#EAF4FA" stroke-width="3" opacity="0.75" stroke-linecap="round"/>')
    # near legs
    o.append('<path d="M 228 352 C 238 372 232 392 234 404 C 235 416 233 428 234 438 L 246 438 C 247 426 246 414 248 404 C 251 392 258 376 260 360 Z" fill="#5A3C2A"/>')
    o.append('<path d="M 430 346 C 446 366 456 382 452 398 C 449 410 444 422 444 438 L 456 438 C 457 424 462 412 465 400 C 470 384 470 364 466 344 Z" fill="#5A3C2A"/>')
    o.append('<path d="M 232 360 C 238 376 236 392 238 404" fill="none" stroke="#9A7454" stroke-width="2" opacity="0.6"/>')
    o.append('<g fill="#241812">' + "".join(f'<path d="M {x - 7} 438 L {x + 7} 438 L {x + 6} 444 L {x - 8} 444 Z"/>' for x in (239, 267, 450, 425)) + "</g>")
    o.append('<g fill="#F2EAE0">' + "".join(f'<rect x="{x - 7}" y="428" width="14" height="6" rx="3"/>' for x in (239, 450)) + "</g>")
    # neck + head
    o.append(f'<path d="M 214 336 C 200 300 186 270 180 244 L 214 228 C 222 258 240 286 262 300 Z" fill="#7A5638"/>')
    o.append('<path d="M 186 256 C 184 282 194 308 210 332 C 220 346 232 352 240 354 C 228 336 216 316 212 298 C 206 282 200 268 198 254 Z" fill="#EFE6D8"/>')
    o.append('<g stroke="#EFE6D8" stroke-width="3" stroke-linecap="round" fill="none">' + "".join(f'<path d="M {x} {y} l -6 8"/>' for x, y in ((190, 290), (196, 304), (204, 318), (212, 330), (222, 342))) + "</g>")
    o.append('<path d="M 210 222 C 190 210 168 216 150 228 C 134 238 118 248 118 258 C 120 266 132 268 146 264 C 162 260 182 254 200 252 C 214 248 222 234 210 222 Z" fill="#8A6446"/>')
    o.append('<path d="M 150 230 C 136 240 124 248 120 256" fill="none" stroke="#EAF4FA" stroke-width="2.5" opacity="0.7" stroke-linecap="round"/>')
    o.append('<path d="M 150 258 C 160 262 176 258 190 254 C 176 262 160 266 146 264 Z" fill="#E8DCCB"/>')
    o.append('<ellipse cx="124" cy="254" rx="8" ry="6" fill="#2A1A14"/><ellipse cx="121" cy="251" rx="2.5" ry="1.6" fill="#FFFFFF" opacity="0.6"/>')
    o.append('<circle cx="176" cy="234" r="4.2" fill="#140C08"/><circle cx="175" cy="232.5" r="1.5" fill="#FFFFFF"/>')
    o.append('<path d="M 208 222 C 220 206 238 202 246 208 C 238 218 224 226 210 232 Z" fill="#7A5638"/><path d="M 214 222 C 224 212 234 210 240 211" stroke="#C9A880" stroke-width="2.5" fill="none"/>')
    o.append(antler(0, 0, "url(#" + ant + ")", 9))
    o.append(antler(-1.5, -1.5, "#FFF8EA", 2.5).replace('stroke-width="2.5"', 'stroke-width="2.5" opacity="0.6"'))
    # lights wound around the antlers
    for i, (x, y) in enumerate(((198, 200), (204, 172), (216, 150), (232, 138), (246, 120), (174, 172), (208, 136), (262, 112), (180, 202), (242, 96))):
        o.append(light(D, x + rnd.uniform(-3, 3), y, 3.2, ["#FF6A5A", "#FFD27A", "#7FD3E0", "#9AE08A"][i % 4], halo=4))
    o.append('<path d="M 196 214 Q 204 196 198 184 Q 212 170 206 156 Q 222 146 226 136 Q 240 130 244 116" fill="none" stroke="#2A3A2A" stroke-width="1.4"/>')
    # collar with a bell
    o.append('<path d="M 186 270 Q 210 286 236 280" fill="none" stroke="#B8262E" stroke-width="9" stroke-linecap="round"/><path d="M 186 268 Q 210 283 236 277" fill="none" stroke="#E8605E" stroke-width="2.5" stroke-linecap="round"/>')
    o.append(f'<circle cx="212" cy="292" r="10" fill="url(#{D.ball("#E2B04A")})"/><path d="M 206 296 q 6 4 12 0" stroke="#7A5212" stroke-width="2" fill="none"/>')
    o.append("</g>")
    return "".join(o)


def oh_deer():
    u = "ohd"
    D = Defs(u)
    out = []
    sky = D.lg([(0, "#A9CADB"), (0.6, "#D6E8F0"), (1, "#EEF6F8")])
    out.append(f'<rect width="600" height="600" fill="url(#{sky})"/>')
    out.append(pt.glow(150, 150, 220, "#FFFFFF", f"{u}-sun", 0.6))
    poly, l1 = pt.ridge_poly([(-10, 360), (150, 330), (320, 352), (470, 326), (610, 344)], 3, amp=6, base=600, fill="#E2EEF4")
    out.append(pt.tree_line(l1, 4, ["#A6C0CE", "#9BB6C6", "#B0C8D4"], density=1.4, hmin=30, hmax=70))
    out.append(poly)
    # birches on the left and right
    for x, w, top in ((70, 16, -10), (104, 10, 40), (528, 14, -10), (556, 9, 60)):
        out.append(f'<rect x="{x - w / 2}" y="{top}" width="{w}" height="{470 - top}" fill="#F4F2EC"/><rect x="{x + w * 0.1}" y="{top}" width="{w * 0.4}" height="{470 - top}" fill="#C9D2D8"/>')
        rnd = random.Random(x)
        for _ in range(int((470 - top) / 24)):
            yy = rnd.uniform(top, 460)
            out.append(f'<path d="M {x - w / 2:.1f} {yy:.1f} q {w * 0.4:.1f} -2 {w * rnd.uniform(0.3, 0.8):.1f} 1 l 0 {rnd.uniform(2, 4):.1f} q {-w * 0.4:.1f} 1 {-w * rnd.uniform(0.3, 0.8):.1f} 0 Z" fill="#2A2A30"/>')
        out.append(f'<path d="M {x} {top + 120} q 24 -20 40 -22" stroke="#6A6A70" stroke-width="2.5" fill="none"/>' if x < 300 else f'<path d="M {x} {top + 150} q -26 -18 -42 -20" stroke="#6A6A70" stroke-width="2.5" fill="none"/>')
    snow = D.lg([(0, "#DDEAF2"), (1, "#FFFFFF")])
    out.append(f'<path d="M -10 420 Q 160 404 320 420 Q 470 436 610 414 L 610 600 L -10 600 Z" fill="url(#{snow})"/>')
    out.append(reindeer(D, 6, -18, 1.0))
    out.append(snowfall(9, 140, r=(1.2, 3.4), op=(0.7, 1)))
    out.append(soft_flakes(D, 10, 12, r=(5, 10), s=0.6))
    # type
    navy = "#1F3550"
    w1 = measure("oh", SERIF_IT, 104)
    w2 = measure("DEER", BEBAS, 136, 10) - 10
    x0 = 300 - (w1 + 22 + w2) / 2
    out.append(T(x0, 532, "oh", SERIF_IT, 104, "#B8262E", anchor="start", max_w=200))
    out.append(T(x0 + w1 + 22, 532, "DEER", BEBAS, 136, navy, ls=10, anchor="start", max_w=300))
    return D.svg() + "\n".join(out)


def snow_much_fun():
    u = "smf"
    D = Defs(u)
    out = []
    sky = D.lg([(0, "#8DB8D0"), (0.6, "#C9E0EA"), (1, "#EAF4F8")])
    out.append(f'<rect width="600" height="600" fill="url(#{sky})"/>')
    poly, l1 = pt.ridge_poly([(-10, 380), (160, 352), (330, 372), (470, 346), (610, 366)], 5, amp=6, base=600, fill="#E4EFF5")
    out.append(pt.tree_line(l1, 2, ["#7FA4B8", "#8CAFC2", "#7499AE"], density=1.6, hmin=40, hmax=90))
    out.append(poly)
    out.append(f'<path d="M -10 452 Q 160 432 330 448 Q 480 462 610 440 L 610 600 L -10 600 Z" fill="url(#{D.lg([(0, "#E6F0F6"), (1, "#FFFFFF")])})"/>')
    cx = 392
    ball_g = D.rg([(0, "#FFFFFF"), (0.55, "#F2F7FA"), (0.85, "#CFE0EC"), (1, "#A9C4D8")], cx=0.38, cy=0.35, r=0.7)
    out.append(f'<ellipse cx="{cx + 20}" cy="532" rx="110" ry="14" fill="#8FB0C8" opacity="0.45"/>')
    for y, r in ((452, 84), (342, 64), (256, 48)):
        out.append(f'<circle cx="{cx}" cy="{y}" r="{r}" fill="url(#{ball_g})"/>')
        out.append(dots(int(r * 0.6), y, (cx - r * 0.7, y - r * 0.7, cx + r * 0.7, y + r * 0.7), "#B9CEDE", r=(0.8, 2), opacity=(0.3, 0.7)))
    # stick arms, one waving with a mitten
    out.append('<g stroke="#5A3A24" stroke-width="6" stroke-linecap="round" fill="none"><path d="M 336 352 L 326 390 L 318 414"/><path d="M 326 390 L 312 392"/><path d="M 448 330 L 494 290 L 508 262"/><path d="M 494 290 L 514 288"/></g>')
    out.append(mitten(D, 508, 268, 0.42, 22, "#B8262E", "#F6EDE0"))
    # coal buttons, eyes, smile, carrot
    for y in (318, 350, 384, 430):
        out.append(f'<circle cx="{cx + (y - 330) * 0.02:.1f}" cy="{y}" r="7" fill="#2A2A30"/><circle cx="{cx - 2:.1f}" cy="{y - 2}" r="2" fill="#6A6A78"/>')
    out.append('<circle cx="376" cy="246" r="6" fill="#1E1E24"/><circle cx="406" cy="246" r="6" fill="#1E1E24"/><circle cx="374" cy="244" r="1.8" fill="#FFFFFF"/><circle cx="404" cy="244" r="1.8" fill="#FFFFFF"/>')
    out.append("".join(f'<circle cx="{x}" cy="{y}" r="3.4" fill="#2A2A30"/>' for x, y in ((372, 274), (381, 279), (391, 281), (401, 279), (410, 274))))
    carrot = D.lg([(0, "#FFA24A"), (1, "#D8601E")], 0, 0, 0, 1)
    out.append(f'<path d="M 390 254 L 340 268 L 392 266 Z" fill="url(#{carrot})"/><g stroke="#B04A14" stroke-width="1.5"><line x1="370" y1="258" x2="372" y2="264"/><line x1="356" y1="262" x2="358" y2="267"/></g>')
    out.append('<circle cx="366" cy="262" r="7" fill="#F2A6B4" opacity="0.45"/><circle cx="414" cy="262" r="7" fill="#F2A6B4" opacity="0.45"/>')
    # knit hat with pom-pom
    hat = D.lg([(0, "#2F7A57"), (1, "#1A4A36")], 0, 0, 1, 0)
    out.append(f'<path d="M 346 230 C 344 182 368 166 392 166 C 418 166 440 184 438 230 Z" fill="url(#{hat})"/>')
    out.append('<g stroke="#FBF6EE" stroke-width="5">' + "".join(f'<line x1="{x}" y1="{y}" x2="{x + 4}" y2="{y + 8}"/><line x1="{x + 8}" y1="{y}" x2="{x + 4}" y2="{y + 8}"/>' for x in range(352, 432, 12) for y in (192,)) + "</g>")
    out.append('<rect x="340" y="216" width="104" height="22" rx="10" fill="#B8262E"/><g stroke="#8A1A20" stroke-width="2.5">' + "".join(f'<line x1="{x}" y1="218" x2="{x}" y2="236"/>' for x in range(348, 440, 7)) + "</g>")
    pr = random.Random(6)
    pom = []
    for i in range(46):
        a, d = pr.uniform(0, 2 * math.pi), pr.uniform(0, 16)
        x, y = 392 + d * math.cos(a), 158 + d * math.sin(a)
        col = "#D2DCE6" if (math.cos(a) + math.sin(a)) * d > 8 else ("#FFFFFF" if d < 10 else "#EEF2F6")
        pom.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{pr.uniform(4, 7):.1f}" fill="{col}"/>')
    out.append("".join(sorted(pom, key=lambda t: "FFFFFF" in t)))
    # striped scarf with a tail
    scarf_c = D.clip('<path d="M 336 290 Q 392 318 448 290 L 450 308 Q 392 336 334 308 Z"/><path d="M 404 300 L 432 302 L 438 392 L 412 396 Z"/>')
    out.append(f'<path d="M 336 290 Q 392 318 448 290 L 450 308 Q 392 336 334 308 Z" fill="#B8262E"/><path d="M 404 300 L 432 302 L 438 392 L 412 396 Z" fill="#A61E26"/>')
    out.append(f'<g clip-path="url(#{scarf_c})">' + "".join(f'<rect x="{x}" y="280" width="9" height="130" fill="#FBF6EE"/>' for x in range(330, 400, 22))
               + "".join(f'<rect x="400" y="{y}" width="50" height="9" fill="#FBF6EE"/>' for y in range(320, 400, 22)) + "</g>")
    out.append('<g stroke="#B8262E" stroke-width="3.5" stroke-linecap="round">' + "".join(f'<line x1="{x}" y1="{394 - (x - 412) * 0.15:.1f}" x2="{x + 1}" y2="{408 - (x - 412) * 0.15:.1f}"/>' for x in range(414, 438, 5)) + "</g>")
    # a little sled and footprints
    out.append('<g transform="translate(96 520) rotate(-4)"><ellipse cx="60" cy="10" rx="70" ry="8" fill="#9DB8CC" opacity="0.6"/>'
               '<g fill="#B8262E"><rect x="0" y="-16" width="112" height="9" rx="3"/><rect x="0" y="-5" width="112" height="8" rx="3"/></g><rect x="0" y="-16" width="112" height="2.5" fill="#F08A80"/>'
               '<path d="M -10 6 L 112 6 Q 130 6 128 -10" fill="none" stroke="#2A1E18" stroke-width="4" stroke-linecap="round"/><path d="M 6 -16 L 8 4 M 104 -16 L 102 4" stroke="#2A1E18" stroke-width="3"/>'
               '<path d="M 112 -14 Q 160 -40 210 -22" fill="none" stroke="#E2B04A" stroke-width="2.5"/></g>')
    out.append(snowfall(13, 160, r=(1.2, 3.6), op=(0.7, 1)))
    out.append(soft_flakes(D, 14, 12, r=(5, 11), s=0.6, avoid=[(60, 60, 330, 400)]))
    # type, stacked to the left of the snowman
    navy = "#1F3550"
    out.append(T(64, 142, "snow", SERIF_IT, 92, navy, anchor="start", max_w=250))
    out.append(T(64, 228, "much", SERIF_IT, 92, navy, anchor="start", max_w=250))
    out.append(T(66, 376, "FUN!", BEBAS, 168, "#B8262E", ls=6, anchor="start", max_w=228))
    return D.svg() + "\n".join(out)


def glass_ornament(D, cx, cy, r, col, style, string_top=-10, cap="#C9CED6"):
    """Vintage blown-glass bauble with window reflections; hangs from string_top."""
    capg = D.lg([(0, lt(cap, 0.6)), (0.5, cap), (1, dk(cap, 0.45))], 0, 0, 1, 0)
    o = [f'<line x1="{cx}" y1="{string_top}" x2="{cx}" y2="{cy - r * 1.24:.1f}" stroke="#B8862A" stroke-width="2"/>',
         f'<circle cx="{cx}" cy="{cy - r * 1.24:.1f}" r="{r * 0.09:.1f}" fill="none" stroke="#B8862A" stroke-width="2"/>',
         f'<circle cx="{cx + r * 0.25:.1f}" cy="{cy + r * 0.3:.1f}" r="{r:.1f}" fill="#7A2A3A" opacity="0.18"/>']
    gid = D.rg([(0, lt(col, 0.65)), (0.22, lt(col, 0.2)), (0.62, col), (0.9, dk(col, 0.45)), (1, dk(col, 0.25))], cx=0.42, cy=0.4, r=0.62, fx=0.34, fy=0.3)
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gid})"/>')
    c = D.clip(f'<circle cx="{cx}" cy="{cy}" r="{r}"/>')
    inner = []
    if style == "band":
        inner.append(f'<rect x="{cx - r}" y="{cy - r * 0.22:.1f}" width="{2 * r}" height="{r * 0.44:.1f}" fill="#FBF3EA"/>')
        inner.append(f'<rect x="{cx - r}" y="{cy - r * 0.22:.1f}" width="{2 * r}" height="{r * 0.44:.1f}" fill="url(#{D.lg([(0, "#FFFFFF", 0), (0.7, "#000", 0.05), (1, "#000", 0.35)], 0, 0, 1, 0)})"/>')
        inner += [f'<line x1="{cx - r}" y1="{cy + d * r:.1f}" x2="{cx + r}" y2="{cy + d * r:.1f}" stroke="{lt(col, 0.3)}" stroke-width="{r * 0.05:.1f}"/>' for d in (-0.3, 0.3)]
        inner.append(dots(int(r * 1.2), int(cx), (cx - r, cy - r * 0.18, cx + r, cy + r * 0.18), "#E2B04A", r=(0.8, 2), opacity=(0.6, 1)))
        inner += [f'<polygon points="{star_points(cx + dx * r, cy, r * 0.12, r * 0.05)}" fill="{col}"/>' for dx in (-0.55, 0, 0.55)]
    elif style == "stripes":
        for i in range(-3, 4):
            inner.append(f'<ellipse cx="{cx + i * r * 0.3:.1f}" cy="{cy}" rx="{r * 0.08 + abs(i) * 0.02 * r:.1f}" ry="{r:.1f}" fill="#FBF3EA" opacity="0.9" transform="scale(1 1)"/>' if i % 2 else "")
    elif style == "indent":
        for k, f in enumerate((0.78, 0.6, 0.42, 0.24)):
            inner.append(f'<polygon points="{star_points(cx + r * 0.06, cy + r * 0.04, r * f, r * f * 0.72, n=8)}" fill="{lt(col, 0.45) if k % 2 == 0 else dk(col, 0.2)}" opacity="0.85"/>')
        inner.append(f'<circle cx="{cx + r * 0.06:.1f}" cy="{cy + r * 0.04:.1f}" r="{r * 0.1:.1f}" fill="#FFFFFF" opacity="0.8"/>')
    elif style == "glitter":
        inner.append(f'<path d="M {cx - r} {cy - r * 0.1:.1f} Q {cx} {cy - r * 0.45:.1f} {cx + r} {cy - r * 0.1:.1f} L {cx + r} {cy + r * 0.1:.1f} Q {cx} {cy - r * 0.25:.1f} {cx - r} {cy + r * 0.1:.1f} Z" fill="#FFFFFF" opacity="0.9"/>')
        inner.append(f'<path d="M {cx - r} {cy + r * 0.3:.1f} Q {cx} {cy - r * 0.05:.1f} {cx + r} {cy + r * 0.3:.1f} L {cx + r} {cy + r * 0.45:.1f} Q {cx} {cy + r * 0.1:.1f} {cx - r} {cy + r * 0.45:.1f} Z" fill="#E2B04A" opacity="0.9"/>')
        inner.append(dots(int(r * 1.5), int(cy), (cx - r, cy - r, cx + r, cy + r), "#FFFFFF", r=(0.6, 1.6), opacity=(0.4, 1)))
    # pink room light reflected along the lower right rim
    inner.append(f'<path d="M {cx + r * 0.95:.1f} {cy - r * 0.1:.1f} A {r} {r} 0 0 1 {cx - r * 0.2:.1f} {cy + r * 0.98:.1f}" fill="none" stroke="#F8C8CC" stroke-width="{r * 0.12:.1f}" opacity="0.55"/>')
    o.append(f'<g clip-path="url(#{c})">{"".join(inner)}</g>')
    # window reflections
    o.append(f'<g transform="rotate(-28 {cx - r * 0.42:.1f} {cy - r * 0.46:.1f})" fill="#FFFFFF">'
             f'<rect x="{cx - r * 0.56:.1f}" y="{cy - r * 0.66:.1f}" width="{r * 0.13:.1f}" height="{r * 0.32:.1f}" rx="{r * 0.05:.1f}" opacity="0.85"/>'
             f'<rect x="{cx - r * 0.39:.1f}" y="{cy - r * 0.66:.1f}" width="{r * 0.13:.1f}" height="{r * 0.32:.1f}" rx="{r * 0.05:.1f}" opacity="0.85"/>'
             f'<rect x="{cx - r * 0.56:.1f}" y="{cy - r * 0.3:.1f}" width="{r * 0.13:.1f}" height="{r * 0.12:.1f}" rx="{r * 0.04:.1f}" opacity="0.6"/>'
             f'<rect x="{cx - r * 0.39:.1f}" y="{cy - r * 0.3:.1f}" width="{r * 0.13:.1f}" height="{r * 0.12:.1f}" rx="{r * 0.04:.1f}" opacity="0.6"/></g>')
    o.append(f'<circle cx="{cx + r * 0.5:.1f}" cy="{cy + r * 0.52:.1f}" r="{r * 0.06:.1f}" fill="#FFFFFF" opacity="0.7"/>')
    # cap with ridges
    o.append(f'<rect x="{cx - r * 0.26:.1f}" y="{cy - r * 1.16:.1f}" width="{r * 0.52:.1f}" height="{r * 0.24:.1f}" rx="{r * 0.04:.1f}" fill="url(#{capg})"/>')
    o.append(f'<path d="M {cx - r * 0.3:.1f} {cy - r * 0.92:.1f} Q {cx:.1f} {cy - r * 0.86:.1f} {cx + r * 0.3:.1f} {cy - r * 0.92:.1f} L {cx + r * 0.26:.1f} {cy - r * 0.98:.1f} L {cx - r * 0.26:.1f} {cy - r * 0.98:.1f} Z" fill="{dk(cap, 0.2)}"/>')
    o.append(f'<g stroke="{dk(cap, 0.35)}" stroke-width="1.5">' + "".join(f'<line x1="{cx + d * r:.1f}" y1="{cy - r * 1.14:.1f}" x2="{cx + d * r:.1f}" y2="{cy - r * 0.96:.1f}"/>' for d in (-0.16, -0.06, 0.04, 0.14)) + "</g>")
    return "".join(o)


def finial(D, cx, top, L, col, cap="#E2B04A"):
    """Long teardrop finial ornament hanging from `top` (cap), length L."""
    capg = D.lg([(0, lt(cap, 0.6)), (0.5, cap), (1, dk(cap, 0.45))], 0, 0, 1, 0)
    g = D.lg([(0, lt(col, 0.55)), (0.3, lt(col, 0.15)), (0.7, col), (1, dk(col, 0.45))], 0, 0, 1, 0)
    w = L * 0.22
    y0 = top + 14
    shape = (f"M {cx} {y0} C {cx + w * 0.5:.1f} {y0:.1f} {cx + w * 0.55:.1f} {y0 + L * 0.12:.1f} {cx + w * 0.35:.1f} {y0 + L * 0.18:.1f} "
             f"C {cx + w * 1.1:.1f} {y0 + L * 0.25:.1f} {cx + w * 1.1:.1f} {y0 + L * 0.5:.1f} {cx + w * 0.3:.1f} {y0 + L * 0.62:.1f} "
             f"C {cx + w * 0.2:.1f} {y0 + L * 0.75:.1f} {cx + w * 0.05:.1f} {y0 + L * 0.9:.1f} {cx} {y0 + L:.1f} "
             f"C {cx - w * 0.05:.1f} {y0 + L * 0.9:.1f} {cx - w * 0.2:.1f} {y0 + L * 0.75:.1f} {cx - w * 0.3:.1f} {y0 + L * 0.62:.1f} "
             f"C {cx - w * 1.1:.1f} {y0 + L * 0.5:.1f} {cx - w * 1.1:.1f} {y0 + L * 0.25:.1f} {cx - w * 0.35:.1f} {y0 + L * 0.18:.1f} "
             f"C {cx - w * 0.55:.1f} {y0 + L * 0.12:.1f} {cx - w * 0.5:.1f} {y0:.1f} {cx} {y0} Z")
    c = D.clip(f'<path d="{shape}"/>')
    return (f'<line x1="{cx}" y1="-10" x2="{cx}" y2="{top}" stroke="#B8862A" stroke-width="2"/>'
            f'<path d="{shape}" fill="#7A2A3A" opacity="0.18" transform="translate(8 10)"/>'
            f'<path d="{shape}" fill="url(#{g})"/>'
            f'<g clip-path="url(#{c})">' + "".join(f'<path d="M {cx - w * 1.2:.1f} {y0 + L * f:.1f} Q {cx:.1f} {y0 + L * (f + 0.06):.1f} {cx + w * 1.2:.1f} {y0 + L * f:.1f}" fill="none" stroke="#FBF3EA" stroke-width="{L * 0.025:.1f}" opacity="0.9"/>' for f in (0.2, 0.3, 0.55, 0.66))
            + dots(30, int(cx), (cx - w, y0 + L * 0.34, cx + w, y0 + L * 0.5), "#FFFFFF", r=(0.6, 1.6), opacity=(0.5, 1)) + "</g>"
            f'<path d="M {cx - w * 0.55:.1f} {y0 + L * 0.3:.1f} Q {cx - w * 0.7:.1f} {y0 + L * 0.42:.1f} {cx - w * 0.45:.1f} {y0 + L * 0.52:.1f}" fill="none" stroke="#FFFFFF" stroke-width="{L * 0.035:.1f}" stroke-linecap="round" opacity="0.8"/>'
            f'<path d="M {cx - w * 0.12:.1f} {y0 + L * 0.68:.1f} L {cx - w * 0.06:.1f} {y0 + L * 0.84:.1f}" stroke="#FFFFFF" stroke-width="{L * 0.02:.1f}" stroke-linecap="round" opacity="0.7"/>'
            f'<rect x="{cx - 10}" y="{top}" width="20" height="16" rx="3" fill="url(#{capg})"/>'
            f'<g stroke="{dk(cap, 0.35)}" stroke-width="1.5">' + "".join(f'<line x1="{cx + d}" y1="{top + 2}" x2="{cx + d}" y2="{top + 14}"/>' for d in (-6, -2, 2, 6)) + "</g>")


def trim_the_tree():
    u = "ttt"
    D = Defs(u)
    out = []
    bg = D.rg([(0, "#FBE3E0"), (0.7, "#F4CCC8"), (1, "#E8AEAA")], cy=0.4, r=0.8)
    out.append(f'<rect width="600" height="600" fill="url(#{bg})"/>')
    out.append('<g fill="#FFFFFF" opacity="0.3">' + "".join(f'<rect x="{x}" y="0" width="10" height="600"/>' for x in range(14, 600, 40)) + "</g>")
    # a pine bough across the top the ornaments hang from
    rnd = random.Random(2)
    st = []
    for x in range(-10, 620, 4):
        y = 26 + 10 * math.sin(x / 70)
        for _ in range(3):
            a = rnd.uniform(20, 160)
            L = rnd.uniform(16, 34)
            st.append(f'<line x1="{x}" y1="{y:.1f}" x2="{x + L * math.cos(math.radians(a)):.1f}" y2="{y + L * math.sin(math.radians(a)):.1f}" stroke="{rnd.choice(["#1E4A38", "#2A5E46", "#163A2C", "#3E7456"])}"/>')
    out.append(f'<path d="M -10 22 Q 150 40 300 26 Q 450 12 610 30" fill="none" stroke="#4A2E1E" stroke-width="8"/>')
    out.append(f'<g stroke-width="2.6" stroke-linecap="round">{"".join(st)}</g>')
    for i, x in enumerate(range(20, 600, 46)):
        out.append(light(D, x, 40 + 10 * math.sin(x / 70) + (i % 2) * 8, 3, ["#FFD27A", "#FF7A6A", "#8FD3E0"][i % 3], halo=4))
    out.append(glass_ornament(D, 140, 196, 62, "#C8303A", "band", string_top=40, cap="#E2B04A"))
    out.append(finial(D, 300, 52, 210, "#F07A98", cap="#C9CED6"))
    out.append(glass_ornament(D, 456, 172, 58, "#7FC4C8", "indent", string_top=40, cap="#C9CED6"))
    out.append(glass_ornament(D, 206, 336, 40, "#E2B04A", "glitter", string_top=40, cap="#E2B04A"))
    out.append(glass_ornament(D, 404, 314, 44, "#B8262E", "stripes", string_top=40, cap="#E2B04A"))
    out.append(twinkle(80, 330, 10, "#FFFFFF") + twinkle(528, 300, 12, "#FFFFFF") + twinkle(300, 300, 8, "#FFFFFF", 0.8))
    # type
    out.append(T(300, 470, "Trim the Tree", DMS, 92, "#8E1E2A", max_w=470))
    out.append(T(300, 524, "HANDLE WITH CARE", MONO, 19, "#B8262E", ls=7, max_w=400))
    out.append(side_rules(518, "HANDLE WITH CARE", MONO, 19, 7, "#B8262E", max_w=400, L=28, sw=2, star=False).replace('y1="518"', 'y1="518"'))
    return D.svg() + "\n".join(out)


# ======================================================================== NEW: badges and labels
def north_pole_post_office():
    u = "npp"
    D = Defs(u)
    out = []
    paper = D.lg([(0, "#F4EEE2"), (1, "#E6DCC8")], 0, 0, 1, 1)
    out.append(f'<rect width="600" height="600" fill="url(#{paper})"/>')
    # airmail border bleeding off the edges
    stripes = "".join(f'<path d="M {x} 0 l 22 0 l -40 40 l -22 0 Z" fill="{["#C8303A", "#F4EEE2", "#2E5A8A", "#F4EEE2"][(x // 22) % 4]}"/>' for x in range(-44, 660, 22))
    for rot in (0, 90, 180, 270):
        out.append(f'<g transform="rotate({rot} 300 300)">{stripes}</g>')
    out.append(speck(5, 260, "#8A7A5A", box=(40, 40, 560, 560), op=(0.08, 0.2)))
    # handwritten address lines peeking out bottom-left
    out.append('<g fill="none" stroke="#3A4A6A" stroke-width="2.5" opacity="0.35" stroke-linecap="round">'
               '<path d="M 70 516 q 20 -8 40 0 t 40 0 t 40 0 t 40 -2"/><path d="M 70 540 q 18 -6 36 0 t 36 0 t 36 0"/></g>')
    # the stamp
    out.append('<g transform="translate(-22 30) rotate(-4 300 300) translate(300 300) scale(0.9) translate(-300 -300)">')
    x0, y0, x1, y1 = 112, 84, 488, 500
    perf = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#FFFDF7"/>']
    holes = "".join(f'<circle cx="{x}" cy="{y0}" r="7"/><circle cx="{x}" cy="{y1}" r="7"/>' for x in range(x0, x1 + 1, 19)) + \
            "".join(f'<circle cx="{x0}" cy="{y}" r="7"/><circle cx="{x1}" cy="{y}" r="7"/>' for y in range(y0, y1 + 1, 19))
    mid = D.id("m")
    out.append(f'<mask id="{mid}"><rect x="0" y="0" width="600" height="600" fill="#FFFFFF"/><g fill="#000">{holes}</g></mask>')
    out.append(f'<g mask="url(#{mid})"><rect x="{x0 + 6}" y="{y0 + 8}" width="{x1 - x0}" height="{y1 - y0}" fill="#5A4A30" opacity="0.25"/>{"".join(perf)}</g>')
    # illustration panel
    ix0, iy0, ix1, iy1 = 140, 170, 460, 400
    sky = D.lg([(0, "#1E3A62"), (0.6, "#4E7AA2"), (1, "#A9C8DC")])
    c = D.clip(f'<rect x="{ix0}" y="{iy0}" width="{ix1 - ix0}" height="{iy1 - iy0}"/>')
    ill = [f'<rect x="{ix0}" y="{iy0}" width="{ix1 - ix0}" height="{iy1 - iy0}" fill="url(#{sky})"/>',
           dots(50, 3, (ix0, iy0, ix1, iy0 + 120), "#FFFFFF", r=(0.6, 1.6), opacity=(0.4, 1)),
           f'<circle cx="390" cy="222" r="34" fill="#F7EFD6"/><circle cx="390" cy="222" r="70" fill="url(#{D.glow("#F7EFD6", 0.35)})"/>']
    # sleigh + reindeer silhouette across the moon
    deer = '<path d="M 0 0 l 6 -8 l 14 0 l 6 -6 l 4 -8 l 3 2 l -2 7 l 4 -3 l 2 2 l -6 6 l -4 8 l -2 10 l -3 0 l 1 -8 l -10 0 l -4 8 l -3 0 l 2 -9 Z"/>'
    ill.append('<g fill="#14243E" transform="translate(300 240) rotate(-10)">'
               + "".join(f'<g transform="translate({dx} {dy})">{deer}</g>' for dx, dy in ((40, -6), (68, -14), (96, -22)))
               + '<path d="M -40 2 Q -36 -14 -18 -14 L 8 -14 L 6 -2 Q 4 8 -10 8 L -36 8 Q -46 8 -46 0 Z"/><path d="M -48 12 L 10 12 Q 18 12 18 4" fill="none" stroke="#14243E" stroke-width="2.5"/>'
               '<circle cx="-26" cy="-20" r="6"/><path d="M -32 -20 Q -26 -34 -16 -26 Z"/><rect x="-14" y="-24" width="12" height="10" rx="2"/>'
               '<path d="M 10 -8 L 44 -10 M 30 -12 L 100 -26" stroke="#14243E" stroke-width="1.6"/></g>')
    # snowy ground, post office, the striped pole
    ill.append(f'<path d="M {ix0} 360 Q 260 340 {ix1} 356 L {ix1} {iy1} L {ix0} {iy1} Z" fill="#EEF4F8"/>')
    ill.append(pt.tree_line([(ix0, 356), (ix1, 352)], 4, ["#2A4A62", "#335670"], density=1.4, hmin=20, hmax=40, xmin=ix0, xmax=230))
    ill.append(pt.tree_line([(ix0, 356), (ix1, 352)], 5, ["#2A4A62", "#335670"], density=1.4, hmin=20, hmax=40, xmin=410, xmax=ix1))
    ill.append(f'<path d="M {ix0} 378 Q 300 362 {ix1} 376 L {ix1} {iy1} L {ix0} {iy1} Z" fill="#FFFFFF"/>')
    # post office building
    ill.append('<rect x="236" y="300" width="96" height="70" fill="#B8312F"/><rect x="300" y="300" width="32" height="70" fill="#8E2234"/>'
               '<path d="M 226 304 L 284 266 L 342 304 Z" fill="#EEF4F8"/><path d="M 226 304 L 284 266 L 342 304" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linejoin="round"/>'
               '<rect x="270" y="334" width="28" height="36" fill="#5A1E16"/><rect x="246" y="318" width="18" height="18" fill="#FFD27A"/><rect x="306" y="318" width="18" height="18" fill="#FFD27A"/>'
               '<rect x="252" y="284" width="64" height="16" fill="#F4EEE2"/><rect x="262" y="290" width="44" height="4" rx="2" fill="#8E2234"/>'
               '<rect x="314" y="246" width="12" height="34" fill="#7A6A64"/>')
    ill.append(f'<circle cx="284" cy="350" r="40" fill="url(#{D.glow("#FFC86A", 0.35)})"/>')
    # the north pole: candy striped with a gold ball
    mid2 = D.id("m")
    ill.append(f'<mask id="{mid2}"><rect x="186" y="236" width="14" height="140" fill="#FFFFFF"/></mask><rect x="186" y="236" width="14" height="140" fill="#FBF6EE"/>'
               f'<g mask="url(#{mid2})">' + "".join(f'<line x1="176" y1="{y}" x2="210" y2="{y - 16}" stroke="#C8303A" stroke-width="7"/>' for y in range(232, 400, 16)) + "</g>"
               f'<circle cx="193" cy="230" r="11" fill="url(#{D.ball("#E2B04A")})"/>'
               '<path d="M 200 270 L 238 266 L 244 274 L 238 282 L 200 284 Z" fill="#2F6A4C"/><path d="M 208 276 L 232 274" stroke="#FBF6EE" stroke-width="2.5" stroke-linecap="round"/>')
    ill.append('<rect x="352" y="340" width="20" height="26" rx="8" fill="#2E5A8A"/><rect x="360" y="366" width="4" height="12" fill="#2E5A8A"/><rect x="356" y="348" width="12" height="3" fill="#F4EEE2"/>')
    ill.append(snowfall(6, 50, box=(ix0, iy0, ix1, iy1), r=(0.8, 2.2), op=(0.7, 1)))
    out.append(f'<g clip-path="url(#{c})">{"".join(ill)}</g>')
    out.append(f'<rect x="{ix0}" y="{iy0}" width="{ix1 - ix0}" height="{iy1 - iy0}" fill="none" stroke="#C8303A" stroke-width="4"/>')
    out.append(f'<rect x="{x0 + 14}" y="{y0 + 14}" width="{x1 - x0 - 28}" height="{y1 - y0 - 28}" fill="none" stroke="#2E5A8A" stroke-width="2"/>')
    # stamp lettering
    out.append(T(300, 152, "NORTH POLE", CINZEL, 50, "#8E2234", ls=3, max_w=312))
    out.append(T(300, 472, "POST OFFICE", BEBAS, 66, "#2E5A8A", ls=8, max_w=300))
    out.append(T(442, 428, "25", ANTON, 28, "#C8303A", max_w=60).replace('text-anchor="middle"', 'text-anchor="middle"'))
    out.append("</g>")
    # postmark + wavy cancel lines
    ink = "#22324E"
    pm = (f'<g opacity="0.78" transform="translate(18 -26) rotate(10 448 150) translate(448 150) scale(0.9) translate(-448 -150)">'
          f'<circle cx="448" cy="150" r="66" fill="none" stroke="{ink}" stroke-width="4"/><circle cx="448" cy="150" r="44" fill="none" stroke="{ink}" stroke-width="2.5"/>'
          + _arc(448, 150, 54, "NORTH POLE", MONO, 19, ink, u + "-a1", 3) + _arc(448, 150, 56, "★ ★ ★", MONO, 19, ink, u + "-a2", 6, top=False)
          + f'<text x="448" y="146" text-anchor="middle" {BEBAS} font-size="26" fill="{ink}">DEC</text><text x="448" y="172" text-anchor="middle" {BEBAS} font-size="26" fill="{ink}">24</text>'
          "</g>")
    out.append(pm)
    out.append(f'<g fill="none" stroke="{ink}" stroke-width="4" opacity="0.7" stroke-linecap="round">' + "".join(
        f'<path d="M 360 {y} q 18 -10 36 0 t 36 0 t 36 0 t 36 0"/>' for y in (196, 212, 228)) + "</g>")
    return D.svg() + "\n".join(out)


def _arc(cx, cy, r, s, font, size, fill, uid, ls=0, top=True):
    if top:
        d = f"M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"
    else:
        d = f"M {cx - r} {cy} A {r} {r} 0 0 0 {cx + r} {cy}"
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return (f'<defs><path id="{uid}" d="{d}" fill="none"/></defs>'
            f'<text {font} font-size="{size}"{lsa} fill="{fill}" text-anchor="middle"><textPath href="#{uid}" startOffset="50%">{esc(s)}</textPath></text>')


def fresh_cut_trees():
    u = "fct"
    D = Defs(u)
    out = []
    sky = D.lg([(0, "#7FA2C2"), (0.55, "#E8C9B8"), (1, "#F6D8B4")])
    out.append(f'<rect width="600" height="600" fill="url(#{sky})"/>')
    out.append(pt.glow(470, 250, 200, "#FFE2B8", f"{u}-sun", 0.6))
    poly, mt = pt.ridge_poly([(-10, 236), (90, 170), (170, 214), (260, 150), (360, 210), (450, 176), (610, 230)], 6, amp=10, base=300, fill="#9AA8C4")
    out.append(poly)
    out.append(pt.ridge_poly([(-10, 236), (90, 170), (130, 196), (170, 214)], 7, amp=4, base=300, fill="#B2BED4")[0])
    out.append(f'<g fill="#F4F6FA">' + "".join(f'<polygon points="{x - w},{y + w * 0.7} {x},{y} {x + w},{y + w * 0.7} {x + w * 0.3},{y + w * 0.5} {x - w * 0.2},{y + w * 0.8}"/>' for x, y, w in ((90, 170, 22), (260, 150, 26), (450, 176, 20))) + "</g>")
    out.append(f'<rect x="0" y="180" width="600" height="110" fill="url(#{D.lg([(0, "#F6D8B4", 0), (1, "#F6D8B4", 0.7)])})"/>')
    out.append('<g fill="none" stroke="#3A3A4A" stroke-width="2" stroke-linecap="round"><path d="M 372 96 q 7 -5 13 0 q 6 -5 13 0"/><path d="M 404 116 q 5 -4 9 0 q 4 -4 9 0"/></g>')
    # rolling farm with rows of young firs, a red barn far off
    poly, l1 = pt.ridge_poly([(-10, 286), (180, 268), (360, 282), (610, 262)], 3, amp=5, base=600, fill="#E6ECF2")
    out.append(pt.tree_line(l1, 2, ["#8EA6B6", "#99B0BE"], density=2.0, hmin=16, hmax=34))
    out.append(poly)
    out.append('<g transform="translate(120 262)"><rect x="0" y="-22" width="38" height="24" fill="#A8323A"/><path d="M -4 -20 L 19 -38 L 42 -20 Z" fill="#E8EEF4"/><rect x="14" y="-12" width="10" height="14" fill="#5A1E16"/></g>')
    rnd = random.Random(8)
    for row, (yb, h0, cols) in enumerate(((318, 30, ["#5E8270", "#6A8E7A"]), (360, 44, ["#4A7260", "#557C68"]), (410, 62, ["#355E4C", "#3E6A56"]))):
        out.append(f'<path d="M -10 {yb - 6} Q 300 {yb - 22} 610 {yb - 4} L 610 600 L -10 600 Z" fill="{["#E8EEF4", "#EEF3F7", "#F4F7FA"][row]}"/>')
        step = 34 + row * 16
        for i, x in enumerate(range(-10 + row * 9, 620, step)):
            h = h0 * rnd.uniform(0.8, 1.15)
            out.append(pt.conifer(x + rnd.uniform(-4, 4), yb - 10 * math.sin(x / 190) + 2, h, rnd.choice(cols), rnd.random(), light="#DCEAF0"))
            out.append(f'<ellipse cx="{x + 8:.1f}" cy="{yb - 10 * math.sin(x / 190) + 3:.1f}" rx="{h * 0.3:.1f}" ry="3" fill="#B8C8D8" opacity="0.6"/>')
    out.append(f'<path d="M -10 466 Q 300 452 610 470 L 610 600 L -10 600 Z" fill="#FFFFFF"/>')
    # the sign: four planks on two posts
    wood = D.lg([(0, "#B07A4A"), (0.5, "#9A6638"), (1, "#7A4A26")])
    for px in (148, 452):
        out.append(f'<rect x="{px - 10}" y="300" width="20" height="200" fill="#6A4026"/><rect x="{px - 10}" y="300" width="6" height="200" fill="#8A5A36"/>')
    out.append(f'<ellipse cx="300" cy="500" rx="200" ry="10" fill="#A8B8C8" opacity="0.5"/>')
    planks = [(144, 196), (198, 270), (272, 344), (346, 398)]
    out.append('<g transform="rotate(-1.5 300 270)">')
    out.append('<rect x="96" y="148" width="408" height="256" rx="4" fill="#000" opacity="0.25" transform="translate(6 8)"/>')
    for k, (y0, y1) in enumerate(planks):
        out.append(f'<rect x="96" y="{y0}" width="408" height="{y1 - y0 - 2}" rx="3" fill="url(#{wood})"/>')
        rr = random.Random(k)
        grain = "".join(f'<path d="M 100 {y0 + rr.uniform(4, y1 - y0 - 6):.1f} q 100 {rr.uniform(-4, 4):.1f} 200 0 t 200 0"/>' for _ in range(5))
        out.append(f'<g fill="none" stroke="#5A3418" stroke-width="1.4" opacity="0.35">{grain}</g>')
        out.append(f'<ellipse cx="{rr.uniform(130, 470):.1f}" cy="{(y0 + y1) / 2:.1f}" rx="7" ry="4" fill="#5A3418" opacity="0.45"/>')
        out.append(f'<rect x="96" y="{y0}" width="408" height="3" fill="#D8A878" opacity="0.6"/>')
        out.append("".join(f'<circle cx="{x}" cy="{(y0 + y1) / 2:.1f}" r="3" fill="#3A2A20"/><circle cx="{x - 1}" cy="{(y0 + y1) / 2 - 1:.1f}" r="1.2" fill="#B8A890"/>' for x in (112, 488)))
    # painted lettering, slightly weathered
    cream = "#FBF1DE"
    out.append(T(300, 186, "FRESH CUT", BEBAS, 46, cream, ls=10, max_w=340))
    out.append(TS(300, 334, "TREES", ANTON, 120, "#D23A3A", "#4A2410", dy=4, ls=8, max_w=360))
    out.append(T(300, 386, "U-CUT · FAMILY FARM", MONO, 20, cream, ls=4, max_w=360))
    out.append(dots(90, 4, (110, 150, 490, 396), "#7A4A26", r=(0.8, 2.2), opacity=(0.3, 0.7)))
    # little painted tree icons either side of FRESH CUT
    for tx in (128, 472):
        out.append(f'<polygon points="{tx},{160} {tx + 13},{186} {tx - 13},{186}" fill="#3E7A56"/><rect x="{tx - 2}" y="186" width="4" height="6" fill="{cream}"/>')
    out.append(snow_cap([(96 + i * 34, 146) for i in range(13)], thick=11, seed=6))
    out.append("</g>")
    # a cut tree leaning on the right post with a paper tag
    tsvg, _ = fir(D, 0, 0, 170, 80, 9, light_c="#5C9A6A", mid="#2E6A4C", dark="#173F30", tiers=6)
    out.append(f'<g transform="translate(474 498) rotate(12)">{tsvg}<rect x="-4" y="-2" width="8" height="12" fill="#6A4630"/></g>')
    out.append('<path d="M 486 420 L 500 440" stroke="#C8303A" stroke-width="2"/><g transform="rotate(18 506 452)"><rect x="490" y="436" width="34" height="38" rx="3" fill="#F6EDE0"/><circle cx="507" cy="443" r="2.5" fill="#B8A890"/><text x="507" y="466" text-anchor="middle" ' + BEBAS + ' font-size="19" fill="#C8303A">SOLD</text></g>')
    # bucket of a lantern hanging from the sign corner
    out.append(f'<circle cx="104" cy="434" r="40" fill="url(#{D.glow("#FFD98E", 0.5)})"/><path d="M 104 404 L 104 414" stroke="#2A2420" stroke-width="2"/>'
               '<path d="M 94 418 L 104 410 L 114 418 Z" fill="#2A2420"/><rect x="95" y="418" width="18" height="26" rx="2" fill="#FFE6A8" stroke="#2A2420" stroke-width="3"/><path d="M 101 438 q 3 -8 3 -12 q 0 4 3 12 Z" fill="#FFB84A"/>')
    out.append(snowfall(4, 110, r=(1.2, 3.2), op=(0.6, 1)))
    return D.svg() + "\n".join(out)


def cookies_for_santa():
    u = "cfs"
    D = Defs(u)
    out = []
    # red gingham tablecloth
    out.append('<rect width="600" height="600" fill="#F6E8E0"/>')
    out.append('<g fill="#C8303A" opacity="0.5">' + "".join(f'<rect x="{x}" y="0" width="30" height="600"/>' for x in range(0, 600, 60)) + "</g>")
    out.append('<g fill="#C8303A" opacity="0.5">' + "".join(f'<rect x="0" y="{y}" width="600" height="30"/>' for y in range(0, 600, 60)) + "</g>")
    out.append(f'<rect width="600" height="600" fill="url(#{D.rg([(0, "#000", 0), (0.7, "#000", 0.05), (1, "#000", 0.3)])})"/>')
    # plate
    out.append('<circle cx="312" cy="314" r="240" fill="#5A1E1E" opacity="0.3"/>')
    plate = D.rg([(0, "#FFFFFF"), (0.7, "#F7F3EE"), (0.92, "#E4DDD4"), (1, "#C9C0B4")], cx=0.45, cy=0.42, r=0.6)
    out.append(f'<circle cx="300" cy="300" r="238" fill="url(#{plate})"/>')
    out.append('<circle cx="300" cy="300" r="232" fill="none" stroke="#1F5A44" stroke-width="5"/><circle cx="300" cy="300" r="222" fill="none" stroke="#C8303A" stroke-width="2"/>')
    out.append(f'<circle cx="300" cy="300" r="166" fill="url(#{D.rg([(0, "#FFFFFF"), (0.85, "#F6F1EA"), (1, "#E2D9CC")], cx=0.55, cy=0.58)})"/>')
    out.append('<circle cx="300" cy="300" r="168" fill="none" stroke="#D9CFC2" stroke-width="3"/>')
    # holly sprigs on the rim at left and right
    from icons import holly
    out.append(holly(92, 312, 30) + holly(508, 312, 30))
    # rim lettering
    out.append(_arc(300, 300, 186, "COOKIES FOR SANTA", BEBAS, 50, "#B8262E", u + "-top", 7))
    out.append(_arc(300, 300, 204, "★  CHRISTMAS EVE  ★", MONO, 19, "#1F5A44", u + "-bot", 5, top=False))
    # cookies: star, tree, gingerbread man, chocolate chip with a bite
    sugar = D.rg([(0, "#F6D6A0"), (1, "#D8A060")], cx=0.4, cy=0.4)
    out.append(f'<polygon points="{star_points(226, 250, 62, 30, rot=-80)}" fill="#8A5A2A" opacity="0.3" transform="translate(5 6)"/>'
               f'<polygon points="{star_points(226, 250, 62, 30, rot=-80)}" fill="url(#{sugar})"/>'
               f'<polygon points="{star_points(226, 250, 52, 25, rot=-80)}" fill="#FBF6EE"/>'
               f'<polygon points="{star_points(226, 250, 52, 25, rot=-80)}" fill="none" stroke="#E8E0D4" stroke-width="2"/>')
    rnd = random.Random(4)
    out.append("".join(f'<rect x="{226 + rnd.uniform(-22, 22):.1f}" y="{250 + rnd.uniform(-22, 22):.1f}" width="6" height="2.6" rx="1.3" fill="{rnd.choice(["#C8303A", "#3E9A6A", "#E2B04A", "#F48AA0"])}" transform="rotate({rnd.uniform(0, 180):.0f} 226 250)"/>' for _ in range(26)))
    # chocolate chip with a bite
    cc = D.rg([(0, "#E0A866"), (0.8, "#C08040"), (1, "#9A5E2A")], cx=0.4, cy=0.4)
    bite = "M 392 238 m -58 0 a 58 58 0 1 0 116 0 a 58 58 0 0 0 -30 -50 a 14 14 0 0 1 -22 8 a 14 14 0 0 1 -24 -2 a 14 14 0 0 1 -18 10 a 58 58 0 0 0 -22 34 Z"
    out.append(f'<path d="{bite}" fill="#7A4A2A" opacity="0.3" transform="translate(5 6)"/><path d="{bite}" fill="url(#{cc})"/>')
    out.append("".join(f'<ellipse cx="{x}" cy="{y}" rx="7" ry="5.5" fill="#4A2814" transform="rotate({r} {x} {y})"/>' for x, y, r in ((372, 228, 20), (408, 244, 60), (390, 268, 0), (362, 254, 40), (418, 218, 10), (384, 204, 70), (420, 272, 30))))
    out.append(dots(14, 6, (352, 172, 412, 192), "#C08040", r=(1.2, 2.8), opacity=(0.8, 1)))
    # tree cookie
    tg = D.lg([(0, "#5CB27A"), (1, "#2E7A50")])
    out.append(f'<path d="M 300 330 L 360 420 L 240 420 Z" fill="#8A5A2A" opacity="0.3" transform="translate(5 6)"/>'
               f'<path d="M 300 326 L 322 362 L 312 362 L 340 400 L 326 400 L 356 436 L 244 436 L 274 400 L 260 400 L 288 362 L 278 362 Z" fill="#D8A060"/>'
               f'<path d="M 300 334 L 318 364 L 308 364 L 334 398 L 320 398 L 346 430 L 254 430 L 280 398 L 266 398 L 292 364 L 282 364 Z" fill="url(#{tg})"/>'
               '<path d="M 268 418 Q 300 404 334 418 M 282 386 Q 300 376 320 386" fill="none" stroke="#FBF6EE" stroke-width="3" stroke-dasharray="1 5" stroke-linecap="round"/>'
               + "".join(f'<circle cx="{x}" cy="{y}" r="3.6" fill="{c}"/>' for x, y, c in ((300, 352, "#E2B04A"), (290, 398, "#C8303A"), (316, 404, "#E2B04A"), (276, 424, "#C8303A"), (326, 426, "#FBF6EE"))))
    out.append(f'<rect x="292" y="436" width="16" height="12" fill="#B07A44"/>')
    # gingerbread man lying on the plate
    out.append(f'<g transform="rotate(-24 414 364)">{gingerbread_man(D, 414, 376, 72)}</g>')
    # crumbs + a little note
    out.append(dots(30, 9, (180, 340, 440, 460), "#C08040", r=(1, 2.6), opacity=(0.7, 1)))
    out.append('<g transform="rotate(-8 190 380)"><rect x="140" y="352" width="104" height="60" rx="3" fill="#000" opacity="0.15" transform="translate(4 5)"/><rect x="140" y="352" width="104" height="60" rx="3" fill="#FFFCF2"/>'
               '<g stroke="#B8C8D8" stroke-width="1.2"><line x1="148" y1="380" x2="236" y2="380"/><line x1="148" y1="398" x2="236" y2="398"/></g>'
               f'<text x="192" y="390" text-anchor="middle" {SERIF_IT} font-size="24" fill="#B8262E">for Santa</text></g>')
    from common import heart
    out.append(heart(224, 404, 7, "#B8262E"))
    return D.svg() + "\n".join(out)

BUILD = {
    "merry-and-bright": merry_and_bright,
    "merry-christmas": merry_christmas,
    "ho-ho-ho": ho_ho_ho,
    "let-it-snow": let_it_snow,
    "hot-cocoa-season": hot_cocoa_season,
    "naughty-or-nice": naughty_or_nice,
    "joy-to-the-world": joy_to_the_world,
    "feliz-natal": feliz_natal,
    "peace-on-earth": peace_on_earth,
    "tis-the-season": tis_the_season,
    "warmest-wishes": warmest_wishes,
    "believe": believe,
    "gingerbread-lane": gingerbread_lane,
    "hung-with-care": hung_with_care,
    "wrapped-with-love": wrapped_with_love,
    "seasons-greetings": seasons_greetings,
    "oh-deer": oh_deer,
    "snow-much-fun": snow_much_fun,
    "trim-the-tree": trim_the_tree,
    "north-pole-post-office": north_pole_post_office,
    "fresh-cut-trees": fresh_cut_trees,
    "cookies-for-santa": cookies_for_santa,
}


def build(only=None):
    for slug, fn in BUILD.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:])
