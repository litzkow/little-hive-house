"""Fall, painted edition: every magnet is a small gouache-style illustration — graded light, shaded and
highlighted objects, knit / wood / paper textures, little storytelling details — paired with designed type.

Run from tools/designs:  python3 fall_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save, text
from paint import P, conifer, grass, lg, rough, y_on
from poster import ANTON, poster

COL = "fall"
RUST, MUSTARD, OLIVE, CREAM, BROWN, PLUM, ORANGE = "#B4532A", "#D9A23B", "#5E6B34", "#F6EDE0", "#4A2F1E", "#6B2E3A", "#E37B33"

# leaf palettes: (centre colour, tip colour)
L_RED = ("#EE7A3C", "#A8321E")
L_ORANGE = ("#F6AE4E", "#CF5E26")
L_GOLD = ("#F6D36A", "#CB8E26")
L_PLUM = ("#C0564C", "#6B2638")
L_OLIVE = ("#C2BC62", "#6E7434")
L_BROWN = ("#C88A4A", "#7A4A26")

# pumpkin palettes: (light, base, dark)
PK_ORANGE = ("#FFB866", "#EE7F2E", "#B24E18")
PK_DEEP = ("#F6A050", "#D9682A", "#943C14")
PK_CREAM = ("#FFFDF4", "#F1E4CB", "#C4AE8A")
PK_GOLD = ("#FFE08A", "#E6A93A", "#A8701E")
PK_GREEN = ("#9DAE72", "#5E7444", "#34462A")
PK_SAGE = ("#D8DCC0", "#AEB898", "#7A876A")


# ---------------------------------------------------------------- plumbing
def rgrad(uid, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None, units=None):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a[0]}"' if a else "") + "/>" for o, c, *a in stops)
    f = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
    u = f' gradientUnits="{units}"' if units else ""
    return f'<radialGradient id="{uid}" cx="{cx}" cy="{cy}" r="{r}"{f}{u}>{s}</radialGradient>'


class Doc:
    """Collects <defs> for one design and hands out unique ids (prefixed with the design's short code)."""

    def __init__(self, u):
        self.u, self.n, self.defs, self.cache = u, 0, [], {}

    def nid(self):
        self.n += 1
        return f"{self.u}-{self.n}"

    def lin(self, stops, x1=0, y1=0, x2=0, y2=1, units="objectBoundingBox", key=None):
        if key is not None and key in self.cache:
            return self.cache[key]
        i = self.nid()
        self.defs.append(lg(i, stops, x1, y1, x2, y2, units))
        if key is not None:
            self.cache[key] = f"url(#{i})"
        return f"url(#{i})"

    def rad(self, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None, units=None, key=None):
        if key is not None and key in self.cache:
            return self.cache[key]
        i = self.nid()
        self.defs.append(rgrad(i, stops, cx, cy, r, fx, fy, units))
        if key is not None:
            self.cache[key] = f"url(#{i})"
        return f"url(#{i})"

    def clip(self, inner):
        i = self.nid()
        self.defs.append(f'<clipPath id="{i}">{inner}</clipPath>')
        return f'clip-path="url(#{i})"'

    def pattern(self, w, h, inner, key=None, transform=""):
        if key is not None and key in self.cache:
            return self.cache[key]
        i = self.nid()
        t = f' patternTransform="{transform}"' if transform else ""
        self.defs.append(f'<pattern id="{i}" width="{w}" height="{h}" patternUnits="userSpaceOnUse"{t}>{inner}</pattern>')
        if key is not None:
            self.cache[key] = f"url(#{i})"
        return f"url(#{i})"

    def render(self, parts):
        return "<defs>" + "".join(self.defs) + "</defs>\n" + "\n".join(p for p in parts if p)


def glow(D, cx, cy, r, color, strength=0.8):
    g = D.rad([(0, color, strength), (0.35, color, strength * 0.45), (1, color, 0)])
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{g}"/>'


def shadow(D, cx, cy, rx, ry, color="#2A1608", strength=0.4):
    g = D.rad([(0, color, strength), (0.6, color, strength * 0.5), (1, color, 0)], key=("sh", color, strength))
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{g}"/>'


def grain(seed, color, n=380, box=(0, 0, 600, 600), r=(0.5, 1.3), op=0.12):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    a = "".join(f'<circle cx="{rnd.uniform(x0, x1):.0f}" cy="{rnd.uniform(y0, y1):.0f}" r="{rnd.uniform(*r):.1f}"/>' for _ in range(n // 2))
    b = "".join(f'<circle cx="{rnd.uniform(x0, x1):.0f}" cy="{rnd.uniform(y0, y1):.0f}" r="{rnd.uniform(*r):.1f}"/>' for _ in range(n // 2))
    return f'<g fill="{color}" opacity="{op}">{a}</g><g fill="{color}" opacity="{op * 0.5:.3f}">{b}</g>'


def washes(seed, colors, n=8, box=(0, 0, 600, 600), r=(70, 160), op=(0.03, 0.06)):
    """Big soft uneven blotches, like gouache dried unevenly on paper."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    return "".join(f'<ellipse cx="{rnd.uniform(x0, x1):.0f}" cy="{rnd.uniform(y0, y1):.0f}" rx="{rnd.uniform(*r):.0f}" ry="{rnd.uniform(*r) * 0.7:.0f}" '
                   f'transform="rotate({rnd.uniform(-40, 40):.0f} 300 300)" fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*op):.3f}"/>' for _ in range(n))


def paper(D, c0, c1, seed=1, ink="#3A2418", n=380, op=0.10, wash=None):
    out = [f'<rect width="600" height="600" fill="{D.rad([(0, c0), (1, c1)], cx=0.5, cy=0.45, r=0.78)}"/>']
    if wash:
        out.append(washes(seed + 7, wash))
    out.append(grain(seed, ink, n, op=op))
    return "".join(out)


def word(x, y, s, font, size, fill, max_w=470, ls=0, anchor="middle", sh=None, off=(0, 4), extra="", sh_op=None):
    fs = fit_size(s, font, size, max_w, ls)
    out = ""
    if sh:
        e = extra + (f' opacity="{sh_op}"' if sh_op else "")
        out += text(x + off[0], y + off[1], s, font, fs, sh, ls, anchor, e)
    return out + text(x, y, s, font, fs, fill, ls, anchor, extra)


def ruled(y, s, fill, size=18, ls=5, line_w=40, gap=14, font=MONO, line=None, sw=2):
    fs = fit_size(s, font, size, 380, ls)
    w = measure(s, font, fs, ls)
    mid = y - fs * 0.35
    lc = line or fill
    return (text(300, y, s, font, fs, fill, ls) +
            f'<line x1="{300 - w / 2 - gap - line_w:.1f}" y1="{mid:.1f}" x2="{300 - w / 2 - gap:.1f}" y2="{mid:.1f}" stroke="{lc}" stroke-width="{sw}" stroke-linecap="round"/>'
            f'<line x1="{300 + w / 2 + gap:.1f}" y1="{mid:.1f}" x2="{300 + w / 2 + gap + line_w:.1f}" y2="{mid:.1f}" stroke="{lc}" stroke-width="{sw}" stroke-linecap="round"/>')


def ribbon(D, cx, cy, w, h, col, dark, tail=46, drop=None):
    """Banner with folded swallow-tail ends behind it."""
    drop = h * 0.32 if drop is None else drop
    l, r, t, b = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    out = []
    for s in (-1, 1):
        e = l if s < 0 else r
        outer = e + s * tail
        tp = [(e, t + drop), (outer, t + drop), (outer - s * h * 0.28, t + drop + h / 2), (outer, b + drop), (e, b + drop)]
        out.append(f'<polygon points="{P(tp)}" fill="{dark}"/>')
        out.append(f'<polygon points="{P([(e - s * drop * 0.9, b), (e, b), (e, b + drop)])}" fill="#000" opacity="0.45"/>')
        out.append(f'<polygon points="{P([(e, t + drop), (e + s * 10, t + drop), (e + s * 10, b + drop), (e, b + drop)])}" fill="#000" opacity="0.18"/>')
    g = D.lin([(0, col), (0.5, col), (1, dark)], key=("rib", col, dark))
    out.append(f'<rect x="{l:.1f}" y="{t:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{g}"/>')
    out.append(f'<rect x="{l:.1f}" y="{t + 4:.1f}" width="{w:.1f}" height="2" fill="#FFFFFF" opacity="0.25"/>')
    out.append(f'<rect x="{l:.1f}" y="{b - 6:.1f}" width="{w:.1f}" height="2" fill="#000" opacity="0.15"/>')
    return "".join(out)


def rot(px, py, cx, cy, deg):
    a = math.radians(deg)
    dx, dy = px - cx, py - cy
    return cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)


# ---------------------------------------------------------------- painted leaves
MAPLE_R = [(0, -1.0), (0.06, -0.84), (0.12, -0.64), (0.22, -0.72), (0.33, -0.78), (0.31, -0.58), (0.27, -0.40),
           (0.42, -0.50), (0.64, -0.64), (0.61, -0.46), (0.56, -0.30), (0.75, -0.31), (0.98, -0.33), (0.87, -0.20),
           (0.78, -0.08), (0.87, -0.01), (0.92, 0.07), (0.70, 0.12), (0.50, 0.22), (0.54, 0.32), (0.56, 0.43),
           (0.36, 0.36), (0.18, 0.32), (0.10, 0.40), (0.04, 0.46)]


def maple(D, cx, cy, s, pal, rot_=0, vein="#FFF1D6", shade=0.22, spots=0, seed=0, stem=None, vein_op=0.55):
    c_in, c_out = pal
    pts = MAPLE_R + [(-x, y) for x, y in reversed(MAPLE_R[1:])]
    g = D.rad([(0, c_in), (0.55, c_in), (1, c_out)], cx=0.5, cy=0.8, r=0.72, key=("mp", pal))
    out = [f'<g transform="rotate({rot_:.1f} {cx:.1f} {cy:.1f})">',
           f'<path d="M {cx - 0.04 * s:.1f} {cy + 0.40 * s:.1f} Q {cx + 0.03 * s:.1f} {cy + 0.72 * s:.1f} {cx - 0.07 * s:.1f} {cy + 0.98 * s:.1f}" fill="none" stroke="{stem or c_out}" stroke-width="{max(1.8, s * 0.05):.1f}" stroke-linecap="round"/>',
           f'<polygon points="{P([(cx + x * s, cy + y * s) for x, y in pts])}" fill="{g}" stroke="{g}" stroke-width="{max(0.6, s * 0.012):.1f}" stroke-linejoin="round"/>']
    if shade:
        half = [(0, -1.0)] + MAPLE_R[1:] + [(0, 0.46)]
        out.append(f'<polygon points="{P([(cx + x * s, cy + y * s) for x, y in half])}" fill="#3A1206" opacity="{shade}"/>')
    bx, by = cx, cy + 0.36 * s
    vs = []
    for tx, ty in ((0, -0.86), (0.84, -0.28), (-0.84, -0.28), (0.5, 0.2), (-0.5, 0.2)):
        vs.append(f'<path d="M {bx:.1f} {by:.1f} Q {cx + tx * s * 0.45:.1f} {cy + (ty * 0.45 + 0.2) * s:.1f} {cx + tx * s:.1f} {cy + ty * s:.1f}"/>')
    for tx, ty, fx, fy in ((0, -0.45, 0.2, -0.62), (0, -0.45, -0.2, -0.62), (0.42, -0.14, 0.52, -0.44), (-0.42, -0.14, -0.52, -0.44),
                           (0.45, -0.15, 0.7, -0.05), (-0.45, -0.15, -0.7, -0.05)):
        vs.append(f'<path d="M {cx + tx * s:.1f} {cy + ty * s:.1f} L {cx + fx * s:.1f} {cy + fy * s:.1f}"/>')
    out.append(f'<g fill="none" stroke="{vein}" stroke-width="{max(1.2, s * 0.028):.1f}" stroke-linecap="round" opacity="{vein_op}">' + "".join(vs) + "</g>")
    if spots:
        rnd = random.Random(seed)
        out.append(f'<g fill="{c_out}" opacity="0.55">' + "".join(
            f'<circle cx="{cx + rnd.uniform(-0.5, 0.5) * s:.1f}" cy="{cy + rnd.uniform(-0.5, 0.1) * s:.1f}" r="{rnd.uniform(0.02, 0.05) * s:.1f}"/>' for _ in range(spots)) + "</g>")
    out.append("</g>")
    return "".join(out)


def maple_at(D, ax, ay, s, pal, rot_, **kw):
    """Maple leaf whose stem tip sits at (ax, ay)."""
    ox, oy = rot(0, 0.98 * s, 0, 0, rot_)
    ox += -0.07 * s * math.cos(math.radians(rot_))
    return maple(D, ax - ox, ay - oy, s, pal, rot_, **kw)


def oak(D, cx, cy, s, pal, rot_=0, vein="#FFF1D6", shade=0.2):
    c_in, c_out = pal
    N = 64
    right, left = [], []
    for i in range(N + 1):
        t = i / N
        env = math.sin(math.pi * min(1.0, t * 1.02)) ** 0.75 * (0.22 + 0.22 * t)
        lobe = 0.55 + 0.45 * abs(math.sin(t * math.pi * 4.6 + 0.3))
        y = cy + s * (0.85 - 1.85 * t)
        right.append((cx + s * env * lobe, y))
        left.append((cx - s * env * lobe, y))
    pts = right + left[::-1]
    g = D.rad([(0, c_in), (0.5, c_in), (1, c_out)], cx=0.5, cy=0.75, r=0.75, key=("ok", pal))
    out = [f'<g transform="rotate({rot_:.1f} {cx:.1f} {cy:.1f})">',
           f'<path d="M {cx:.1f} {cy + 0.8 * s:.1f} q {0.02 * s:.1f} {0.2 * s:.1f} {-0.04 * s:.1f} {0.34 * s:.1f}" stroke="{c_out}" stroke-width="{max(1.8, s * 0.05):.1f}" fill="none" stroke-linecap="round"/>',
           f'<polygon points="{P(pts)}" fill="{g}"/>']
    if shade:
        out.append(f'<polygon points="{P(right + [(cx, cy - s)] + [(cx, cy + 0.85 * s)])}" fill="#3A1206" opacity="{shade}"/>')
    vs = [f'<line x1="{cx:.1f}" y1="{cy + 0.82 * s:.1f}" x2="{cx:.1f}" y2="{cy - 0.85 * s:.1f}"/>']
    for k in range(4):
        t = 0.2 + k * 0.2
        y = cy + s * (0.85 - 1.85 * t)
        for sg in (-1, 1):
            vs.append(f'<line x1="{cx:.1f}" y1="{y + 0.06 * s:.1f}" x2="{cx + sg * 0.28 * s * (0.6 + t * 0.5):.1f}" y2="{y - 0.1 * s:.1f}"/>')
    out.append(f'<g stroke="{vein}" stroke-width="{max(1.1, s * 0.025):.1f}" stroke-linecap="round" opacity="0.5">' + "".join(vs) + "</g></g>")
    return "".join(out)


def slim_leaf(D, cx, cy, s, pal, rot_=0, vein="#FFF1D6", width=0.36, shade=0.2, serr=True):
    """Birch / elm / aspen type leaf, pointed, lightly serrated. Tip up, stem down."""
    c_in, c_out = pal
    N = 28
    right, left = [], []
    for i in range(N + 1):
        t = i / N
        w = width * s * math.sin(math.pi * t) ** 0.8 * (1 - 0.25 * t)
        z = (0.04 * s if (serr and i % 2) else 0)
        y = cy + s * (0.7 - 1.7 * t)
        right.append((cx + w + z, y))
        left.append((cx - w - z, y))
    pts = right + left[::-1]
    g = D.rad([(0, c_in), (0.5, c_in), (1, c_out)], cx=0.45, cy=0.7, r=0.75, key=("sl", pal))
    out = [f'<g transform="rotate({rot_:.1f} {cx:.1f} {cy:.1f})">',
           f'<path d="M {cx:.1f} {cy + 0.7 * s:.1f} q {0.03 * s:.1f} {0.16 * s:.1f} {-0.03 * s:.1f} {0.3 * s:.1f}" stroke="{c_out}" stroke-width="{max(1.6, s * 0.05):.1f}" fill="none" stroke-linecap="round"/>',
           f'<polygon points="{P(pts)}" fill="{g}"/>']
    if shade:
        out.append(f'<polygon points="{P(right)}" fill="#3A1206" opacity="{shade}"/>')
    vs = [f'<line x1="{cx:.1f}" y1="{cy + 0.7 * s:.1f}" x2="{cx:.1f}" y2="{cy - 0.85 * s:.1f}"/>']
    for k in range(5):
        y = cy + s * (0.45 - k * 0.27)
        for sg in (-1, 1):
            vs.append(f'<line x1="{cx:.1f}" y1="{y:.1f}" x2="{cx + sg * width * s * 0.75:.1f}" y2="{y - 0.2 * s:.1f}"/>')
    out.append(f'<g stroke="{vein}" stroke-width="{max(1.0, s * 0.022):.1f}" stroke-linecap="round" opacity="0.45">' + "".join(vs) + "</g></g>")
    return "".join(out)


def leaf_any(D, kind, cx, cy, s, pal, r, **kw):
    if kind == "maple":
        return maple(D, cx, cy, s, pal, r, **kw)
    if kind == "oak":
        return oak(D, cx, cy, s * 1.05, pal, r)
    return slim_leaf(D, cx, cy, s * 0.95, pal, r)


def acorn(D, cx, cy, s, rot_=0):
    nut = D.rad([(0, "#E3B070"), (0.6, "#B7783A"), (1, "#7A4A20")], cx=0.38, cy=0.35, r=0.7, key="acn")
    cap = D.rad([(0, "#9A7448"), (1, "#5A3E22")], cx=0.4, cy=0.3, r=0.7, key="acc")
    k = s
    cid = D.clip(f'<path d="M {cx - 0.52 * k:.1f} {cy:.1f} Q {cx:.1f} {cy - 0.62 * k:.1f} {cx + 0.52 * k:.1f} {cy:.1f} Q {cx:.1f} {cy + 0.14 * k:.1f} {cx - 0.52 * k:.1f} {cy:.1f} Z"/>')
    hatch = "".join(f'<path d="M {cx - 0.6 * k + i * 0.12 * k:.1f} {cy + 0.1 * k:.1f} l {0.25 * k:.1f} {-0.5 * k:.1f}"/>' for i in range(11))
    hatch2 = "".join(f'<path d="M {cx - 0.6 * k + i * 0.12 * k:.1f} {cy - 0.45 * k:.1f} l {0.25 * k:.1f} {0.5 * k:.1f}"/>' for i in range(11))
    return (f'<g transform="rotate({rot_:.1f} {cx:.1f} {cy:.1f})">'
            f'<path d="M {cx - 0.4 * k:.1f} {cy:.1f} Q {cx - 0.46 * k:.1f} {cy + 0.6 * k:.1f} {cx:.1f} {cy + 0.86 * k:.1f} Q {cx + 0.46 * k:.1f} {cy + 0.6 * k:.1f} {cx + 0.4 * k:.1f} {cy:.1f} Z" fill="{nut}"/>'
            f'<path d="M {cx - 0.18 * k:.1f} {cy + 0.12 * k:.1f} Q {cx - 0.24 * k:.1f} {cy + 0.45 * k:.1f} {cx - 0.06 * k:.1f} {cy + 0.66 * k:.1f}" stroke="#FFF0D6" stroke-width="{0.07 * k:.1f}" fill="none" stroke-linecap="round" opacity="0.55"/>'
            f'<path d="M {cx - 0.52 * k:.1f} {cy:.1f} Q {cx:.1f} {cy - 0.62 * k:.1f} {cx + 0.52 * k:.1f} {cy:.1f} Q {cx:.1f} {cy + 0.14 * k:.1f} {cx - 0.52 * k:.1f} {cy:.1f} Z" fill="{cap}"/>'
            f'<g {cid}><g stroke="#3E2814" stroke-width="{max(1, 0.035 * k):.1f}" opacity="0.5">{hatch}{hatch2}</g></g>'
            f'<path d="M {cx:.1f} {cy - 0.3 * k:.1f} q {0.02 * k:.1f} {-0.2 * k:.1f} {0.14 * k:.1f} {-0.3 * k:.1f}" stroke="#5A3E22" stroke-width="{0.1 * k:.1f}" fill="none" stroke-linecap="round"/></g>')


# ---------------------------------------------------------------- painted produce
def pumpkin(D, cx, cy, w, h, pal=PK_ORANGE, stem=("#B2A060", "#6E5A2A"), shade=True, curl=True, leaf=None, rot_=0,
            warts=0, stripes=None, seed=0, cast=0.4, lobes=5, stem_h=0.22, stem_lean=0.08):
    light, base, dark = pal
    g = D.rad([(0, light), (0.5, base), (1, dark)], cx=0.36, cy=0.32, r=0.78, key=("pk", pal))
    if lobes == 5:
        L = [(-0.31, 0.22, 0.42), (0.31, 0.22, 0.42), (-0.16, 0.25, 0.48), (0.16, 0.25, 0.48), (0, 0.25, 0.5)]
    else:
        L = [(-0.2, 0.3, 0.46), (0.2, 0.3, 0.46), (0, 0.28, 0.5)]
    ell = "".join(f'<ellipse cx="{cx + dx * w:.1f}" cy="{cy:.1f}" rx="{rx * w:.1f}" ry="{ry * h:.1f}"/>' for dx, rx, ry in L)
    cid = D.clip(ell)
    out = [f'<g transform="rotate({rot_:.1f} {cx:.1f} {cy + 0.4 * h:.1f})">']
    if cast:
        out.append(shadow(D, cx + 0.06 * w, cy + 0.44 * h, 0.58 * w, 0.11 * h, strength=cast))
    for k, (dx, rx, ry) in enumerate(L):
        out.append(f'<ellipse cx="{cx + dx * w:.1f}" cy="{cy:.1f}" rx="{rx * w:.1f}" ry="{ry * h:.1f}" fill="{g}"/>')
        if lobes == 5 and k < 2:
            out.append(f'<ellipse cx="{cx + dx * w:.1f}" cy="{cy:.1f}" rx="{rx * w:.1f}" ry="{ry * h:.1f}" fill="{dark}" opacity="0.22"/>')
    inner = []
    if stripes:
        for dx in (-0.36, -0.22, -0.08, 0.08, 0.22, 0.36):
            inner.append(f'<path d="M {cx + dx * w:.1f} {cy - 0.48 * h:.1f} Q {cx + dx * 1.3 * w:.1f} {cy:.1f} {cx + dx * w:.1f} {cy + 0.5 * h:.1f}" stroke="{stripes}" stroke-width="{0.035 * w:.1f}" fill="none" opacity="0.8"/>')
    if shade:
        sg = D.lin([(0, "#000", 0), (0.55, "#000", 0), (1, "#2A0E00", 0.38)], 0, 0, 1, 0.35, key="pkshade")
        inner.append(f'<rect x="{cx - 0.6 * w:.1f}" y="{cy - 0.6 * h:.1f}" width="{1.2 * w:.1f}" height="{1.2 * h:.1f}" fill="{sg}"/>')
        bg = D.lin([(0, "#000", 0), (0.7, "#000", 0), (1, "#2A0E00", 0.3)], key="pkbot")
        inner.append(f'<rect x="{cx - 0.6 * w:.1f}" y="{cy - 0.5 * h:.1f}" width="{1.2 * w:.1f}" height="{h:.1f}" fill="{bg}"/>')
    if lobes == 5:
        ribs = (-0.25, 0.25, -0.085, 0.085)
    else:
        ribs = (-0.12, 0.12)
    for dx in ribs:
        inner.append(f'<path d="M {cx + dx * w:.1f} {cy - 0.44 * h:.1f} Q {cx + dx * 1.45 * w:.1f} {cy:.1f} {cx + dx * w:.1f} {cy + 0.47 * h:.1f}" fill="none" stroke="{dark}" stroke-width="{max(1.5, 0.018 * w):.1f}" opacity="0.6"/>')
    if warts:
        rnd = random.Random(seed)
        for _ in range(warts):
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.uniform(0.1, 0.9)
            x, y = cx + math.cos(a) * d * 0.45 * w, cy + math.sin(a) * d * 0.42 * h
            rr = rnd.uniform(0.012, 0.028) * w
            inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="{dark}" opacity="0.5"/><circle cx="{x - rr * 0.3:.1f}" cy="{y - rr * 0.3:.1f}" r="{rr * 0.6:.1f}" fill="{light}" opacity="0.8"/>')
    out.append(f'<g {cid}>' + "".join(inner) + "</g>")
    # highlights on the lit lobes
    out.append(f'<g fill="none" stroke="#FFFFFF" stroke-linecap="round" opacity="0.42">'
               f'<path d="M {cx - 0.12 * w:.1f} {cy - 0.3 * h:.1f} Q {cx - 0.19 * w:.1f} {cy - 0.1 * h:.1f} {cx - 0.16 * w:.1f} {cy + 0.12 * h:.1f}" stroke-width="{max(2, 0.03 * w):.1f}"/>'
               f'<path d="M {cx - 0.36 * w:.1f} {cy - 0.18 * h:.1f} Q {cx - 0.41 * w:.1f} {cy - 0.02 * h:.1f} {cx - 0.38 * w:.1f} {cy + 0.1 * h:.1f}" stroke-width="{max(1.5, 0.02 * w):.1f}" opacity="0.6"/>'
               f'<path d="M {cx + 0.04 * w:.1f} {cy - 0.36 * h:.1f} q {0.04 * w:.1f} {-0.02 * h:.1f} {0.08 * w:.1f} 0" stroke-width="{max(1.5, 0.018 * w):.1f}"/></g>')
    # top dimple and stem
    out.append(f'<ellipse cx="{cx:.1f}" cy="{cy - 0.43 * h:.1f}" rx="{0.12 * w:.1f}" ry="{0.05 * h:.1f}" fill="{dark}" opacity="0.65"/>')
    sl, sd = stem
    sgr = D.lin([(0, sl), (0.55, sl), (1, sd)], 0, 0, 1, 0, key=("stem", stem))
    sx = cx + 0.01 * w
    sw = max(5, 0.075 * w)
    top = cy - 0.43 * h - stem_h * h
    lean = stem_lean * w
    out.append(f'<path d="M {sx - sw * 0.75:.1f} {cy - 0.42 * h:.1f} Q {sx - sw * 0.4:.1f} {top + 0.08 * h:.1f} {sx - sw * 0.45 + lean:.1f} {top:.1f} '
               f'L {sx + sw * 0.55 + lean:.1f} {top + 0.02 * h:.1f} Q {sx + sw * 0.5:.1f} {top + 0.1 * h:.1f} {sx + sw * 0.8:.1f} {cy - 0.42 * h:.1f} Z" fill="{sgr}"/>')
    out.append(f'<ellipse cx="{sx + 0.05 * sw + lean:.1f}" cy="{top + 0.01 * h:.1f}" rx="{sw * 0.52:.1f}" ry="{sw * 0.22:.1f}" fill="#D8CB98"/>')
    out.append(f'<path d="M {sx - sw * 0.1:.1f} {cy - 0.44 * h:.1f} Q {sx:.1f} {top + 0.1 * h:.1f} {sx + lean * 0.7:.1f} {top + 0.05 * h:.1f}" stroke="{sd}" stroke-width="1.5" fill="none" opacity="0.6"/>')
    if curl:
        out.append(f'<path d="M {sx + sw * 0.5:.1f} {cy - 0.46 * h:.1f} q {0.12 * w:.1f} {-0.02 * h:.1f} {0.14 * w:.1f} {-0.12 * h:.1f} q {0.02 * w:.1f} {-0.1 * h:.1f} {-0.05 * w:.1f} {-0.09 * h:.1f} q {-0.05 * w:.1f} {0.02 * h:.1f} {-0.01 * w:.1f} {0.07 * h:.1f}" '
                   f'fill="none" stroke="#6E7A38" stroke-width="{max(1.6, 0.014 * w):.1f}" stroke-linecap="round"/>')
    if leaf:
        out.append(slim_leaf(D, sx - 0.2 * w, cy - 0.5 * h, 0.16 * w, leaf, -62, shade=0.15))
    out.append("</g>")
    return "".join(out)


def apple(D, cx, cy, r, pal=("#F26A4A", "#C62E26", "#7A1616"), blush="#E8C24A", rot_=0, leaf=True, seed=0, cast=0.0):
    light, base, dark = pal
    g = D.rad([(0, light), (0.55, base), (1, dark)], cx=0.36, cy=0.36, r=0.75, key=("ap", pal))
    d = (f"M {cx:.1f} {cy - 0.68 * r:.1f} C {cx + 0.3 * r:.1f} {cy - 0.98 * r:.1f} {cx + 1.05 * r:.1f} {cy - 0.92 * r:.1f} {cx + r:.1f} {cy - 0.08 * r:.1f} "
         f"C {cx + 0.96 * r:.1f} {cy + 0.66 * r:.1f} {cx + 0.48 * r:.1f} {cy + 0.98 * r:.1f} {cx:.1f} {cy + 0.86 * r:.1f} "
         f"C {cx - 0.48 * r:.1f} {cy + 0.98 * r:.1f} {cx - 0.96 * r:.1f} {cy + 0.66 * r:.1f} {cx - r:.1f} {cy - 0.08 * r:.1f} "
         f"C {cx - 1.05 * r:.1f} {cy - 0.92 * r:.1f} {cx - 0.3 * r:.1f} {cy - 0.98 * r:.1f} {cx:.1f} {cy - 0.68 * r:.1f} Z")
    cid = D.clip(f'<path d="{d}"/>')
    rnd = random.Random(seed)
    specks = "".join(f'<circle cx="{cx + rnd.uniform(-0.8, 0.8) * r:.1f}" cy="{cy + rnd.uniform(-0.6, 0.8) * r:.1f}" r="{max(0.6, 0.025 * r):.1f}"/>' for _ in range(int(6 + r / 3)))
    bl = D.rad([(0, blush, 0.75), (1, blush, 0)], key=("bl", blush))
    out = [f'<g transform="rotate({rot_:.1f} {cx:.1f} {cy:.1f})">']
    if cast:
        out.append(shadow(D, cx + 0.1 * r, cy + 0.85 * r, 0.95 * r, 0.22 * r, strength=cast))
    out += [f'<path d="{d}" fill="{g}"/>',
            f'<g {cid}><ellipse cx="{cx - 0.45 * r:.1f}" cy="{cy + 0.45 * r:.1f}" rx="{0.7 * r:.1f}" ry="{0.5 * r:.1f}" fill="{bl}"/>'
            f'<g fill="#FFE9B0" opacity="0.6">{specks}</g>'
            f'<path d="M {cx + 0.2 * r:.1f} {cy - 0.6 * r:.1f} Q {cx + 0.9 * r:.1f} {cy - 0.2 * r:.1f} {cx + 0.6 * r:.1f} {cy + 0.9 * r:.1f} L {cx + 1.2 * r:.1f} {cy + r:.1f} L {cx + 1.2 * r:.1f} {cy - r:.1f} Z" fill="{dark}" opacity="0.25"/></g>',
            f'<ellipse cx="{cx - 0.42 * r:.1f}" cy="{cy - 0.3 * r:.1f}" rx="{0.14 * r:.1f}" ry="{0.24 * r:.1f}" transform="rotate(30 {cx - 0.42 * r:.1f} {cy - 0.3 * r:.1f})" fill="#FFFFFF" opacity="0.55"/>',
            f'<path d="M {cx - 0.1 * r:.1f} {cy - 0.62 * r:.1f} Q {cx:.1f} {cy - 0.5 * r:.1f} {cx + 0.12 * r:.1f} {cy - 0.6 * r:.1f}" fill="none" stroke="{dark}" stroke-width="{max(1.2, 0.05 * r):.1f}" opacity="0.6"/>',
            f'<path d="M {cx:.1f} {cy - 0.6 * r:.1f} Q {cx + 0.02 * r:.1f} {cy - 0.9 * r:.1f} {cx + 0.14 * r:.1f} {cy - 1.08 * r:.1f}" fill="none" stroke="#5A3A1E" stroke-width="{max(2, 0.08 * r):.1f}" stroke-linecap="round"/>']
    if leaf:
        out.append(slim_leaf(D, cx + 0.38 * r, cy - 0.98 * r, 0.42 * r, ("#8EA04A", "#4E6A2A"), 62, shade=0.18, serr=False))
    out.append("</g>")
    return "".join(out)


def cyl(D, light, base, dark, key=None):
    """Horizontal gradient that makes a flat shape read as a cylinder lit from the upper left."""
    return D.lin([(0, base), (0.22, light), (0.55, base), (0.9, dark), (1, dark)], 0, 0, 1, 0, key=key or ("cyl", light, base, dark))


def steam(D, x, y, h, col="#FFFFFF", n=3, gap=24, sw=7, op=0.7, seed=0):
    g = D.lin([(0, col, 0), (0.55, col, op * 0.55), (1, col, op)], 0, y - h, 0, y, units="userSpaceOnUse")
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x0 = x + (i - (n - 1) / 2) * gap
        a = rnd.uniform(10, 16) * (1 if i % 2 else -1)
        out.append(f'<path d="M {x0:.1f} {y:.1f} c {a:.1f} {-h * 0.18:.1f} {-a:.1f} {-h * 0.32:.1f} 0 {-h * 0.5:.1f} s {-a:.1f} {-h * 0.34:.1f} {a * 0.4:.1f} {-h * 0.5:.1f}"/>')
    return f'<g fill="none" stroke="{g}" stroke-width="{sw}" stroke-linecap="round">' + "".join(out) + "</g>"


def mug(D, cx, top, w, h, glaze=("#FFFBF2", "#F0E2CA", "#B8A07E"), liquid="#7A4626", band=None, handle_side=1):
    light, base, dark = glaze
    l, r, b = cx - w / 2, cx + w / 2, top + h
    body = (f"M {l:.1f} {top:.1f} L {r:.1f} {top:.1f} L {r - 0.05 * w:.1f} {b - 0.14 * h:.1f} Q {r - 0.07 * w:.1f} {b:.1f} {r - 0.2 * w:.1f} {b:.1f} "
            f"L {l + 0.2 * w:.1f} {b:.1f} Q {l + 0.07 * w:.1f} {b:.1f} {l + 0.05 * w:.1f} {b - 0.14 * h:.1f} Z")
    g = cyl(D, light, base, dark)
    hx = r if handle_side > 0 else l
    s = handle_side
    hp = (f"M {hx - s * 0.04 * w:.1f} {top + 0.2 * h:.1f} C {hx + s * 0.36 * w:.1f} {top + 0.12 * h:.1f} {hx + s * 0.36 * w:.1f} {top + 0.72 * h:.1f} {hx - s * 0.08 * w:.1f} {top + 0.74 * h:.1f}")
    out = [shadow(D, cx + 0.08 * w, b + 2, 0.62 * w, 0.08 * w, strength=0.45),
           f'<path d="{hp}" fill="none" stroke="{dark}" stroke-width="{0.13 * w:.1f}" stroke-linecap="round"/>',
           f'<path d="{hp}" fill="none" stroke="{base}" stroke-width="{0.085 * w:.1f}" stroke-linecap="round"/>',
           f'<path d="M {hx + s * 0.06 * w:.1f} {top + 0.2 * h:.1f} Q {hx + s * 0.26 * w:.1f} {top + 0.22 * h:.1f} {hx + s * 0.24 * w:.1f} {top + 0.42 * h:.1f}" fill="none" stroke="{light}" stroke-width="{0.025 * w:.1f}" stroke-linecap="round" opacity="0.8"/>',
           f'<path d="{body}" fill="{g}"/>']
    if band:
        cid = D.clip(f'<path d="{body}"/>')
        out.append(f'<g {cid}>{band(l, r, top, b)}<path d="{body}" fill="{D.lin([(0, "#000", 0.12), (0.22, "#FFF", 0.15), (0.55, "#000", 0), (1, "#000", 0.3)], 0, 0, 1, 0, key="mugsh")}"/></g>')
    out += [f'<ellipse cx="{cx:.1f}" cy="{top:.1f}" rx="{w / 2:.1f}" ry="{0.09 * w:.1f}" fill="{dark}"/>',
            f'<ellipse cx="{cx:.1f}" cy="{top + 0.012 * w:.1f}" rx="{w / 2 - 0.045 * w:.1f}" ry="{0.07 * w:.1f}" fill="{liquid}"/>',
            f'<ellipse cx="{cx - 0.08 * w:.1f}" cy="{top + 0.012 * w:.1f}" rx="{0.22 * w:.1f}" ry="{0.03 * w:.1f}" fill="#FFFFFF" opacity="0.18"/>',
            f'<ellipse cx="{cx:.1f}" cy="{top:.1f}" rx="{w / 2:.1f}" ry="{0.09 * w:.1f}" fill="none" stroke="{light}" stroke-width="{max(2, 0.025 * w):.1f}"/>',
            f'<path d="M {l + 0.16 * w:.1f} {top + 0.18 * h:.1f} L {l + 0.2 * w:.1f} {b - 0.2 * h:.1f}" stroke="#FFFFFF" stroke-width="{0.04 * w:.1f}" stroke-linecap="round" opacity="0.45"/>']
    return "".join(out)


def cinnamon(D, x1, y1, x2, y2, w=16):
    """A rolled cinnamon quill from (x1, y1) to (x2, y2); the open, rolled end is at (x2, y2)."""
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    L = math.hypot(x2 - x1, y2 - y1)
    g = D.lin([(0, "#C47A44"), (0.35, "#A65C2E"), (0.75, "#7A3E1C"), (1, "#5A2C12")], key="cinn")
    return (f'<g transform="translate({x1:.1f} {y1:.1f}) rotate({ang:.1f})">'
            f'<rect x="0" y="{-w / 2:.1f}" width="{L:.1f}" height="{w:.1f}" rx="{w * 0.2:.1f}" fill="{g}"/>'
            + "".join(f'<path d="M {t:.1f} {-w / 2:.1f} q 3 {w / 2:.1f} 0 {w:.1f}" stroke="#5A2C12" stroke-width="1.2" fill="none" opacity="0.5"/>' for t in range(14, int(L) - 6, 17))
            + f'<path d="M 4 {-w * 0.18:.1f} L {L - 6:.1f} {-w * 0.22:.1f}" stroke="#E0A06A" stroke-width="2" opacity="0.6"/>'
            f'<ellipse cx="{L:.1f}" cy="0" rx="{w * 0.24:.1f}" ry="{w / 2:.1f}" fill="#8A4A24"/>'
            f'<path d="M {L:.1f} {-w * 0.38:.1f} a {w * 0.17:.1f} {w * 0.38:.1f} 0 1 1 0 {w * 0.76:.1f} a {w * 0.1:.1f} {w * 0.22:.1f} 0 1 1 0 {-w * 0.44:.1f}" fill="none" stroke="#4A220E" stroke-width="1.6"/>'
            "</g>")


def star_anise(D, cx, cy, r, rot_=0):
    pod = D.rad([(0, "#B0683A"), (1, "#5E2E14")], cx=0.5, cy=0.8, r=0.8, key="anise")
    out = [f'<g transform="rotate({rot_:.1f} {cx:.1f} {cy:.1f})">']
    for i in range(8):
        a = i * 45
        x, y = rot(cx, cy - r * 0.55, cx, cy, a)
        out.append(f'<path d="M {cx:.1f} {cy:.1f} Q {x - r * 0.22:.1f} {y:.1f} {x:.1f} {y - 0.001:.1f}" fill="none"/>')
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 0.2:.1f}" ry="{r * 0.46:.1f}" transform="rotate({a} {x:.1f} {y:.1f})" fill="{pod}"/>')
        sx, sy = rot(cx, cy - r * 0.52, cx, cy, a)
        out.append(f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="{r * 0.07:.1f}" ry="{r * 0.12:.1f}" transform="rotate({a} {sx:.1f} {sy:.1f})" fill="#E8B060"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.15:.1f}" fill="#4A220E"/></g>')
    return "".join(out)


def knit_pattern(D, base, stitch, w=12, h=11, key=None, scale=1.0):
    k = scale
    inner = (f'<rect width="{w * k}" height="{h * k}" fill="{base}"/>'
             f'<ellipse cx="{3.2 * k}" cy="{5.5 * k}" rx="{2.5 * k}" ry="{5.2 * k}" transform="rotate(-30 {3.2 * k} {5.5 * k})" fill="{stitch}"/>'
             f'<ellipse cx="{8.8 * k}" cy="{5.5 * k}" rx="{2.5 * k}" ry="{5.2 * k}" transform="rotate(30 {8.8 * k} {5.5 * k})" fill="{stitch}"/>')
    return D.pattern(w * k, h * k, inner, key=key or ("knit", base, stitch, scale))


def foliage(D, cx, cy, rx, ry, pals, seed, n=160, size=(6, 13), light=(-0.7, -0.7), clip=None, leafy=False):
    """A tree crown painted from many dabs: shadow-side dabs first, then mid tones, then lit dabs on top."""
    rnd = random.Random(seed)
    groups = [{}, {}, {}]
    lx, ly = light
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.random() ** 0.6
        x, y = cx + math.cos(a) * d * rx, cy + math.sin(a) * d * ry
        facing = (math.cos(a) * lx + math.sin(a) * ly) * d + rnd.uniform(-0.35, 0.35)
        k = 0 if facing < -0.2 else (1 if facing < 0.35 else 2)
        s = rnd.uniform(*size)
        col = rnd.choice(pals[k])
        if leafy:
            el = f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{s:.1f}" ry="{s * 0.62:.1f}" transform="rotate({rnd.uniform(-60, 60):.0f} {x:.0f} {y:.0f})"/>'
        else:
            el = f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{s:.1f}"/>'
        groups[k].setdefault(col, []).append(el)
    body = "".join(f'<g fill="{c}">' + "".join(v) + "</g>" for g in groups for c, v in g.items())
    return f'<g {clip}>{body}</g>' if clip else body


def crown(D, cx, cy, r, pal, seed, light=(0.7, -0.7), n=10):
    """Cheap rounded tree crown: a shaded blob (radial gradient) plus a few lit and shadow dabs for texture."""
    sh, mid, lit = pal
    lx, ly = light
    g = D.rad([(0, lit[0]), (0.45, mid[0]), (1, sh[0])], cx=0.5 + lx * 0.22, cy=0.5 + ly * 0.22, r=0.7, key=("crown", pal[1][0], light))
    rnd = random.Random(seed)
    out = [f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{r:.1f}" ry="{r * 0.86:.1f}" fill="{g}"/>']
    for i in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(0.35, 0.95) * r
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d * 0.86
        facing = math.cos(a) * lx + math.sin(a) * ly
        col = rnd.choice(lit) if facing > 0.2 else (rnd.choice(sh) if facing < -0.3 else rnd.choice(mid))
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r * rnd.uniform(0.18, 0.34):.1f}" fill="{col}"/>')
    return "".join(out)


def wood_grain(seed, box, col, n=14, op=0.35, sw=1.4, vertical=False):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        if vertical:
            x = rnd.uniform(x0, x1)
            out.append(f'<path d="M {x:.1f} {y0:.1f} q {rnd.uniform(-5, 5):.1f} {(y1 - y0) / 2:.1f} {rnd.uniform(-3, 3):.1f} {y1 - y0:.1f}"/>')
        else:
            y = rnd.uniform(y0, y1)
            L = rnd.uniform(0.3, 1.0) * (x1 - x0)
            xs = rnd.uniform(x0, x1 - L)
            out.append(f'<path d="M {xs:.1f} {y:.1f} q {L / 2:.1f} {rnd.uniform(-3, 3):.1f} {L:.1f} {rnd.uniform(-1.5, 1.5):.1f}"/>')
    return f'<g fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" opacity="{op}">' + "".join(out) + "</g>"


def falling(D, specs):
    """specs: (kind, x, y, size, palette, rotation)."""
    return "".join(leaf_any(D, k, x, y, s, pal, r) for k, x, y, s, pal, r in specs)


DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


# ================================================================ 1. hello fall (repaint)
@design("hello-fall")
def hello_fall():
    D = Doc("hf")
    out = [paper(D, "#FBF4E8", "#ECDCC4", 3, wash=["#E9B07A", "#C9A86A"])]
    # a maple twig arching across the top, leaves hanging in a mix of colours
    bp = "M -12 156 C 90 118 190 98 300 102 C 400 106 470 96 612 52"
    out.append(f'<path d="{bp}" fill="none" stroke="#3E2616" stroke-width="10" stroke-linecap="round"/>')
    out.append(f'<path d="{bp}" fill="none" stroke="#8A6040" stroke-width="3" stroke-linecap="round" transform="translate(0 -3)" opacity="0.7"/>')
    twigs = [(118, 128, 128, 152), (214, 103, 224, 128), (300, 102, 296, 124), (350, 104, 352, 122), (392, 104, 404, 126), (484, 90, 490, 112), (160, 113, 150, 92), (430, 102, 446, 80)]
    out.append('<g fill="none" stroke="#3E2616" stroke-width="4" stroke-linecap="round">' + "".join(f'<path d="M {a} {b} L {c} {d}"/>' for a, b, c, d in twigs) + "</g>")
    out.append(maple_at(D, 150, 92, 30, L_OLIVE, 150, spots=3, seed=2))
    out.append(maple_at(D, 446, 80, 28, L_GOLD, 205))
    out.append(maple_at(D, 128, 152, 44, L_RED, 192, spots=4, seed=5))
    out.append(maple_at(D, 224, 128, 54, L_ORANGE, 168))
    out.append(maple_at(D, 296, 124, 46, L_PLUM, 186, spots=3, seed=9))
    out.append(acorn(D, 352, 134, 18, 4) + acorn(D, 364, 128, 15, -20))
    out.append(maple_at(D, 404, 126, 52, L_GOLD, 160))
    out.append(maple_at(D, 490, 112, 40, L_RED, 200))
    # leaves drifting down the sides
    out.append(falling(D, [("maple", 92, 318, 24, L_GOLD, 36), ("oak", 516, 282, 26, L_BROWN, -28), ("maple", 506, 448, 20, L_RED, 64),
                           ("slim", 86, 470, 22, L_OLIVE, -40)]))
    out.append(acorn(D, 104, 400, 22, -18))
    # type
    out.append(word(300, 316, "hello", SERIF_IT, 116, BROWN, max_w=330))
    fs = fit_size("FALL", BEBAS, 196, 420, 18)
    fill = D.lin([(0, "#D2622C"), (1, "#9A3418")], 0, 330, 0, 470, units="userSpaceOnUse")
    out.append(text(300, 474, "FALL", BEBAS, fs, "#E6CDB0", 18, extra=' transform="translate(5 5)"'))
    out.append(text(300, 474, "FALL", BEBAS, fs, fill, 18))
    out.append(ruled(522, "SEPT · OCT · NOV", BROWN, size=19, ls=6, line_w=44))
    return D.render(out)


# ================================================================ 2. pumpkin spice (repaint)
@design("pumpkin-spice")
def pumpkin_spice():
    D = Doc("ps")
    out = [paper(D, "#EDBE58", "#C2852A", 5, ink="#4A2A10", op=0.12, wash=["#F6D27A", "#A8601E"])]
    out.append(glow(D, 300, 200, 260, "#FFE7A8", 0.5))
    # saucer
    sau = D.rad([(0, "#FFFBF0"), (0.7, "#EFE0C4"), (1, "#C2A27A")], cx=0.45, cy=0.35, r=0.65)
    out.append(shadow(D, 306, 350, 170, 26, strength=0.4))
    out.append(f'<ellipse cx="300" cy="340" rx="160" ry="30" fill="{sau}"/>')
    out.append('<ellipse cx="300" cy="334" rx="112" ry="18" fill="#D8C29E" opacity="0.6"/>')
    out.append('<path d="M 142 340 Q 300 384 458 340" fill="none" stroke="#A88A62" stroke-width="3" opacity="0.6"/>')
    # small pumpkin behind on the left, cinnamon quills leaning on the right
    out.append(pumpkin(D, 138, 292, 112, 84, PK_DEEP, cast=0.25, leaf=None))
    out.append(cinnamon(D, 392, 336, 470, 214, 17))
    out.append(cinnamon(D, 410, 340, 498, 236, 15))
    # the mug
    def band(l, r, t, b):
        y = t + 62
        s = f'<rect x="{l - 5:.1f}" y="{y}" width="{r - l + 10:.1f}" height="30" fill="#B4532A"/>'
        s += "".join(f'<path d="M {x} {y + 15} l 7 -8 l 7 8 l -7 8 Z" fill="#F6EDE0"/>' for x in range(int(l) + 4, int(r), 22))
        s += f'<rect x="{l - 5:.1f}" y="{y - 7}" width="{r - l + 10:.1f}" height="3" fill="#B4532A"/><rect x="{l - 5:.1f}" y="{y + 34}" width="{r - l + 10:.1f}" height="3" fill="#B4532A"/>'
        return s
    out.append(mug(D, 290, 206, 178, 128, liquid="#8A5230", band=band))
    # whipped cream dome, dusted with cinnamon
    cream = D.rad([(0, "#FFFFFF"), (0.6, "#FBF1E2"), (1, "#D9C6AA")], cx=0.38, cy=0.3, r=0.8, key="whip")
    for cx, cy, rx, ry in ((290, 196, 84, 22), (250, 186, 40, 24), (330, 186, 42, 24), (290, 176, 56, 26), (270, 160, 34, 20), (310, 158, 34, 20), (292, 140, 28, 20), (298, 122, 14, 14)):
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{cream}"/>')
    out.append('<g fill="none" stroke="#D2BC9A" stroke-width="2.4" stroke-linecap="round" opacity="0.8"><path d="M 230 192 q 30 12 60 2"/><path d="M 300 196 q 26 6 54 -6"/><path d="M 262 168 q 24 10 50 0"/><path d="M 278 146 q 14 6 30 -2"/></g>')
    rnd = random.Random(4)
    out.append('<g fill="#8A4422">' + "".join(f'<circle cx="{rnd.uniform(244, 336):.1f}" cy="{rnd.uniform(126, 196):.1f}" r="{rnd.uniform(0.8, 2):.1f}" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>' for _ in range(70)) + "</g>")
    out.append(steam(D, 292, 112, 64, "#FFFFFF", n=3, gap=30, sw=6, op=0.8, seed=2))
    # star anise and cloves on the saucer
    out.append(star_anise(D, 190, 342, 26, 12))
    for x, y, r_ in ((398, 358, 30), (424, 350, -20), (222, 362, 70)):
        out.append(f'<g transform="rotate({r_} {x} {y})"><rect x="{x - 2}" y="{y - 8}" width="4" height="14" rx="2" fill="#4A220E"/><circle cx="{x}" cy="{y - 9}" r="4" fill="#5E2E14"/></g>')
    # type
    out.append(word(300, 446, "pumpkin spice", SERIF_IT, 84, BROWN, max_w=470))
    out.append(ribbon(D, 300, 498, 360, 52, "#B4532A", "#7E3416", tail=40))
    out.append(word(300, 517, "& EVERYTHING NICE", BEBAS, 48, CREAM, max_w=320, ls=4))
    return D.render(out)


# ================================================================ 3. sweater weather (repaint)
def folded_sweater(D, cx, top, w, h, base, light, dark, kind, seed=0, collar=False):
    l, r, b = cx - w / 2, cx + w / 2, top + h
    rr = h * 0.42
    shape = (f"M {l + rr:.1f} {top:.1f} L {r - rr:.1f} {top:.1f} Q {r + 4:.1f} {top:.1f} {r + 2:.1f} {top + h * 0.5:.1f} Q {r:.1f} {b:.1f} {r - rr:.1f} {b:.1f} "
             f"L {l + rr:.1f} {b:.1f} Q {l:.1f} {b:.1f} {l - 2:.1f} {top + h * 0.5:.1f} Q {l - 4:.1f} {top:.1f} {l + rr:.1f} {top:.1f} Z")
    cid = D.clip(f'<path d="{shape}"/>')
    fill = knit_pattern(D, base, light, scale=0.85, key=("kn", base, light))
    shade = D.lin([(0, "#FFFFFF", 0.18), (0.35, "#FFFFFF", 0), (0.75, "#000", 0.08), (1, "#1A0A00", 0.42)], key="swsh")
    side = D.lin([(0, "#1A0A00", 0.3), (0.12, "#000", 0), (0.85, "#000", 0), (1, "#1A0A00", 0.35)], 0, 0, 1, 0, key="swside")
    g = [f'<rect x="{l - 10:.1f}" y="{top - 4:.1f}" width="{w + 20:.1f}" height="{h + 8:.1f}" fill="{fill}"/>']
    if kind == "cable":
        for x0 in (cx - w * 0.22, cx + w * 0.22, cx):
            g.append(f'<rect x="{x0 - 15:.1f}" y="{top:.1f}" width="30" height="{h:.1f}" fill="{dark}" opacity="0.25"/>')
            for yy in range(int(top) - 10, int(b) + 10, 18):
                g.append(f'<path d="M {x0 - 11:.1f} {yy:.1f} C {x0 - 11:.1f} {yy + 10:.1f} {x0 + 11:.1f} {yy + 8:.1f} {x0 + 11:.1f} {yy + 18:.1f}" stroke="{light}" stroke-width="7" fill="none" stroke-linecap="round"/>'
                         f'<path d="M {x0 + 11:.1f} {yy:.1f} C {x0 + 11:.1f} {yy + 6:.1f} {x0 + 4:.1f} {yy + 8:.1f} {x0 + 2:.1f} {yy + 9:.1f}" stroke="{dark}" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.7"/>')
            g.append(f'<line x1="{x0 - 19:.1f}" y1="{top:.1f}" x2="{x0 - 19:.1f}" y2="{b:.1f}" stroke="{dark}" stroke-width="3" opacity="0.5"/>'
                     f'<line x1="{x0 + 19:.1f}" y1="{top:.1f}" x2="{x0 + 19:.1f}" y2="{b:.1f}" stroke="{dark}" stroke-width="3" opacity="0.5"/>')
    elif kind == "fair":
        y = top + h * 0.5
        g.append(f'<rect x="{l - 10:.1f}" y="{y - 17:.1f}" width="{w + 20:.1f}" height="34" fill="#B4532A"/>')
        g.append("".join(f'<path d="M {x} {y} l 9 -11 l 9 11 l -9 11 Z" fill="#F6EDE0"/><circle cx="{x + 9}" cy="{y}" r="2.6" fill="#B4532A"/>' for x in range(int(l) - 6, int(r) + 10, 24)))
        for yy in (y - 26, y + 26):
            g.append("".join(f'<path d="M {x} {yy + 4} l 5 -7 l 5 7" stroke="#5E6B34" stroke-width="3" fill="none"/>' for x in range(int(l) - 6, int(r) + 10, 12)))
    elif kind == "rib":
        g.append("".join(f'<rect x="{x:.1f}" y="{top - 4:.1f}" width="4" height="{h + 8:.1f}" fill="{dark}" opacity="0.35"/>' for x in [l + i * 11 for i in range(int(w / 11) + 2)]))
    # ribbed hem along the bottom, sleeve fold line, and an optional crew-neck collar on top
    g.append(f'<rect x="{l - 10:.1f}" y="{b - 13:.1f}" width="{w + 20:.1f}" height="13" fill="{dark}" opacity="0.22"/>')
    g.append("".join(f'<line x1="{x:.1f}" y1="{b - 13:.1f}" x2="{x:.1f}" y2="{b:.1f}" stroke="{dark}" stroke-width="2" opacity="0.45"/>' for x in [l + i * 6 for i in range(int(w / 6) + 2)]))
    g.append(f'<path d="M {l + w * 0.12:.1f} {top + h * 0.3:.1f} Q {cx:.1f} {top + h * 0.36:.1f} {r - w * 0.12:.1f} {top + h * 0.3:.1f}" stroke="{dark}" stroke-width="2.5" fill="none" opacity="0.35"/>')
    # ribbed cuff showing at the folded left end
    g.append(f'<rect x="{l - 6:.1f}" y="{top:.1f}" width="{w * 0.11:.1f}" height="{h:.1f}" fill="{dark}" opacity="0.18"/>')
    g.append("".join(f'<line x1="{l + i * 6:.1f}" y1="{top:.1f}" x2="{l + i * 6:.1f}" y2="{b:.1f}" stroke="{dark}" stroke-width="2" opacity="0.4"/>' for i in range(int(w * 0.11 / 6) + 1)))
    g.append(f'<rect x="{l - 10:.1f}" y="{top - 4:.1f}" width="{w + 20:.1f}" height="{h + 8:.1f}" fill="{shade}"/>')
    g.append(f'<rect x="{l - 10:.1f}" y="{top - 4:.1f}" width="{w + 20:.1f}" height="{h + 8:.1f}" fill="{side}"/>')
    g.append(f'<path d="M {l + rr:.1f} {top + 3:.1f} L {r - rr:.1f} {top + 3:.1f}" stroke="#FFFFFF" stroke-width="3" opacity="0.3" stroke-linecap="round"/>')
    lid = ""
    if collar:
        # the top face of the folded sweater, seen from slightly above, with a ribbed crew neck
        tf = (f"M {l + rr:.1f} {top + 6:.1f} Q {l + 4:.1f} {top + 4:.1f} {l + 22:.1f} {top - 22:.1f} Q {l + 30:.1f} {top - 32:.1f} {l + 50:.1f} {top - 32:.1f} "
              f"L {r - 50:.1f} {top - 32:.1f} Q {r - 30:.1f} {top - 32:.1f} {r - 22:.1f} {top - 22:.1f} Q {r - 4:.1f} {top + 4:.1f} {r - rr:.1f} {top + 6:.1f} Z")
        tid = D.clip(f'<path d="{tf}"/>')
        lid = (f'<path d="{tf}" fill="{base}"/><g {tid}><rect x="{l - 10:.1f}" y="{top - 40:.1f}" width="{w + 20:.1f}" height="50" fill="{fill}"/>'
               + "".join(f'<rect x="{x:.1f}" y="{top - 40:.1f}" width="4" height="50" fill="{dark}" opacity="0.3"/>' for x in [l + i * 11 for i in range(int(w / 11) + 2)])
               + f'<rect x="{l - 10:.1f}" y="{top - 40:.1f}" width="{w + 20:.1f}" height="50" fill="#FFFFFF" opacity="0.12"/></g>'
               f'<ellipse cx="{cx:.1f}" cy="{top - 13:.1f}" rx="50" ry="14" fill="{dark}"/>'
               f'<ellipse cx="{cx:.1f}" cy="{top - 13:.1f}" rx="50" ry="14" fill="none" stroke="{light}" stroke-width="9"/>'
               f'<ellipse cx="{cx:.1f}" cy="{top - 13:.1f}" rx="50" ry="14" fill="none" stroke="{dark}" stroke-width="9" stroke-dasharray="1.6 3" opacity="0.6"/>'
               f'<ellipse cx="{cx:.1f}" cy="{top - 11:.1f}" rx="36" ry="7" fill="#2A1406" opacity="0.55"/>'
               f'<path d="M {l + 40:.1f} {top - 26:.1f} L {cx - 50:.1f} {top - 16:.1f} M {r - 40:.1f} {top - 26:.1f} L {cx + 50:.1f} {top - 16:.1f}" stroke="{dark}" stroke-width="2" opacity="0.4"/>')
    return f'<path d="{shape}" fill="{base}"/><g {cid}>' + "".join(g) + "</g>" + lid


@design("sweater-weather")
def sweater_weather():
    D = Doc("sw")
    out = [f'<rect width="600" height="600" fill="{D.rad([(0, "#74833F"), (1, "#45512A")], cx=0.5, cy=0.4, r=0.8)}"/>']
    out.append(f'<rect width="600" height="600" fill="{knit_pattern(D, "#000000", "#FFFFFF", key="bgknit", scale=1.2)}" opacity="0.045"/>')
    out.append(grain(8, "#1E2410", 300, op=0.12))
    # type
    out.append(word(300, 172, "SWEATER", BEBAS, 150, CREAM, max_w=440, ls=10, sh="#2E3818", off=(0, 6)))
    out.append(word(300, 262, "weather", SERIF_IT, 98, "#F2C25A", max_w=360, sh="#2E3818", off=(0, 5)))
    # the stack
    out.append(shadow(D, 306, 536, 210, 22, "#141A08", 0.6))
    out.append(folded_sweater(D, 300, 462, 330, 74, "#A9482A", "#C8603A", "#6E2A14", "cable"))
    out.append(shadow(D, 300, 466, 160, 10, "#1A0A00", 0.5))
    out.append(folded_sweater(D, 304, 392, 306, 74, "#EFE3CC", "#FFF8EC", "#B8A486", "fair"))
    out.append(shadow(D, 302, 396, 148, 9, "#1A0A00", 0.5))
    out.append(folded_sweater(D, 298, 324, 280, 72, "#D9A23B", "#EDC062", "#9A6A1E", "rib", collar=True))
    # a stray leaf on top and a wooden toggle button
    out.append(maple(D, 418, 304, 28, L_RED, 64, spots=2, seed=4))
    return D.render(out)


# ================================================================ 4. cozy season (repaint)
def book(D, x, y, w, h, col, dark, band="#E9C46A"):
    g = D.lin([(0, dark), (0.25, col), (0.5, col), (1, dark)], key=("bk", col))
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{g}"/>'
            f'<rect x="{x + 18}" y="{y + 2}" width="3" height="{h - 4}" fill="{band}" opacity="0.85"/><rect x="{x + 25}" y="{y + 2}" width="2" height="{h - 4}" fill="{band}" opacity="0.85"/>'
            f'<rect x="{x + w - 27}" y="{y + 2}" width="2" height="{h - 4}" fill="{band}" opacity="0.85"/><rect x="{x + w - 21}" y="{y + 2}" width="3" height="{h - 4}" fill="{band}" opacity="0.85"/>'
            f'<rect x="{x + w * 0.36:.1f}" y="{y + h * 0.3:.1f}" width="{w * 0.28:.1f}" height="{h * 0.4:.1f}" rx="2" fill="{band}" opacity="0.3"/>'
            f'<rect x="{x + 4}" y="{y + 2}" width="{w - 8}" height="2" fill="#FFFFFF" opacity="0.18"/>')


@design("cozy-season")
def cozy_season():
    D = Doc("cz")
    out = [f'<rect width="600" height="600" fill="{D.rad([(0, "#6A4128"), (0.55, "#3E2616"), (1, "#2A170C")], cx=0.4, cy=0.3, r=0.85)}"/>']
    out.append(grain(9, "#F6EDE0", 260, op=0.05))
    out.append(glow(D, 240, 176, 300, "#FFB25A", 0.45))
    # shelf
    out.append(f'<rect x="-10" y="330" width="620" height="18" fill="{D.lin([(0, "#8A5634"), (1, "#4E2E18")])}"/>')
    out.append('<rect x="-10" y="330" width="620" height="3" fill="#D79A5E" opacity="0.6"/>')
    out.append(wood_grain(3, (-10, 334, 610, 346), "#3A2010", n=8, op=0.4, sw=1.2))
    out.append(f'<rect x="-10" y="348" width="620" height="26" fill="{D.lin([(0, "#120804", 0.55), (1, "#120804", 0)])}"/>')
    # wheat in a stoneware vase on the left
    for dx, top, lean in ((-12, 132, -26), (0, 116, -6), (10, 126, 14), (20, 142, 30)):
        x0 = 108 + dx * 0.3
        out.append(f'<path d="M {x0:.1f} 268 Q {x0 + lean * 0.3:.1f} {top + 60} {x0 + lean:.1f} {top + 18}" stroke="#C9A060" stroke-width="2.6" fill="none"/>')
        for i in range(6):
            yy = top + 6 + i * 9
            xx = x0 + lean - lean * i / 40
            for s in (-1, 1):
                out.append(f'<ellipse cx="{xx + s * 4.5:.1f}" cy="{yy}" rx="3.4" ry="7" transform="rotate({s * 28} {xx + s * 4.5:.1f} {yy})" fill="{"#E6C47A" if s < 0 else "#C79A4C"}"/>')
        out.append(f'<ellipse cx="{x0 + lean:.1f}" cy="{top}" rx="3" ry="7" fill="#E6C47A"/>')
    vase = cyl(D, "#B7C2B4", "#7E8E80", "#46524A")
    out.append(shadow(D, 112, 331, 40, 6, strength=0.5))
    out.append(f'<path d="M 92 262 Q 82 300 90 322 Q 94 330 108 330 L 116 330 Q 130 330 134 322 Q 142 300 132 262 Z" fill="{vase}"/>')
    out.append('<ellipse cx="112" cy="262" rx="21" ry="5" fill="#46524A"/><ellipse cx="112" cy="262" rx="21" ry="5" fill="none" stroke="#C9D2C4" stroke-width="2"/>')
    # stack of books with a candle in an amber jar
    out.append(shadow(D, 276, 332, 140, 8, strength=0.55))
    out.append(book(D, 150, 300, 252, 30, "#6E7A3C", "#3A4420"))
    out.append(book(D, 160, 274, 228, 26, "#B4532A", "#6E2A12"))
    out.append(book(D, 174, 250, 206, 24, "#7A3446", "#43182A"))
    out.append(glow(D, 240, 172, 120, "#FFD27A", 0.75))
    jar = D.lin([(0, "#C77A2A", 0.85), (0.3, "#F2B260", 0.75), (0.7, "#D58A34", 0.8), (1, "#8A4A16", 0.9)], 0, 0, 1, 0)
    out.append(f'<rect x="204" y="186" width="72" height="64" rx="10" fill="{jar}"/>')
    out.append('<rect x="204" y="214" width="72" height="22" fill="#F6EDE0" opacity="0.85"/>')
    out.append(maple(D, 240, 224, 9, L_RED, 0, shade=0.15, vein_op=0.3))
    out.append('<ellipse cx="240" cy="196" rx="30" ry="6" fill="#FBE6BE"/><ellipse cx="240" cy="186" rx="36" ry="7" fill="none" stroke="#FFE2A8" stroke-width="3" opacity="0.8"/>')
    out.append('<path d="M 212 192 L 214 244" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" opacity="0.35"/>')
    out.append('<line x1="240" y1="196" x2="240" y2="184" stroke="#3A2010" stroke-width="2.4"/>')
    flame = D.rad([(0, "#FFFFFF"), (0.35, "#FFE9A0"), (0.8, "#FFB040"), (1, "#F07A20")], cx=0.5, cy=0.72, r=0.6)
    out.append(f'<path d="M 240 140 C 252 160 252 176 240 186 C 228 176 228 160 240 140 Z" fill="{flame}"/>')
    # mug of cocoa on the right, steaming
    def band(l, r, t, b):
        return (f'<rect x="{l - 5:.1f}" y="{t + 34}" width="{r - l + 10:.1f}" height="20" fill="#D9A23B"/>'
                + "".join(f'<circle cx="{x}" cy="{t + 44}" r="3.4" fill="#4A2F1E"/>' for x in range(int(l) + 8, int(r), 14)))
    out.append(mug(D, 444, 246, 96, 84, glaze=("#F6E3C8", "#D9BE98", "#8A6A48"), liquid="#5A3018", band=band))
    out.append(steam(D, 446, 232, 80, "#FFE8C8", n=3, gap=22, sw=5, op=0.55, seed=6))
    # a leaf resting on the shelf and a tiny gourd
    out.append(maple(D, 520, 318, 18, L_GOLD, 112, shade=0.18))
    out.append(pumpkin(D, 352, 232, 52, 40, PK_CREAM, cast=0.3, curl=False))
    # type
    out.append(word(300, 464, "cozy", DMS, 140, "#FBEBD2", max_w=400, sh="#160A04", off=(0, 6)))
    out.append(word(300, 532, "SEASON", JOS, 38, "#E9B54A", max_w=380, ls=16))
    return D.render(out)


# ================================================================ 5. falling for you (repaint)
def in_heart(x, y):
    return (x * x + y * y - 1) ** 3 - x * x * y ** 3 < 0


@design("falling-for-you")
def falling_for_you():
    D = Doc("ffy")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#F4D3BC"), (0.55, "#FAEBDC"), (1, "#FBF3E8")])}"/>']
    out.append(washes(4, ["#F2B48A", "#E9C79A"], n=6, op=(0.05, 0.1)))
    out.append(grain(12, "#6B3A22", 300, op=0.08))
    out.append(glow(D, 470, 110, 160, "#FFF3D8", 0.7))
    out.append(birds([(470, 120, 8), (492, 110, 6)], "#7A4A3A", 2))
    # little knoll with fallen leaves
    knoll = D.lin([(0, "#9AA05A"), (1, "#6E7A3C")])
    out.append(f'<path d="M 120 340 Q 200 300 300 302 Q 400 300 480 340 Z" fill="{knoll}"/>')
    rnd = random.Random(7)
    out.append("".join(f'<ellipse cx="{rnd.uniform(160, 440):.1f}" cy="{rnd.uniform(318, 336):.1f}" rx="{rnd.uniform(3, 6):.1f}" ry="{rnd.uniform(1.6, 3):.1f}" fill="{rnd.choice(["#D0602A", "#F2A23A", "#B4532A", "#8E3A28"])}"/>' for _ in range(46)))
    # trunk and the branch with a swing
    tr = D.lin([(0, "#6E4A30"), (0.4, "#8A6040"), (1, "#3E2616")], 0, 0, 1, 0)
    out.append(f'<path d="M 284 318 Q 290 270 288 220 Q 270 190 244 176 L 252 170 Q 282 184 296 204 Q 306 180 334 166 L 340 174 Q 314 192 310 222 Q 308 270 318 318 Q 300 324 284 318 Z" fill="{tr}"/>')
    # heart-shaped crown painted in dabs, lit from the upper right
    pals = (["#6B2638", "#7A2A2E", "#8E3424"], ["#B4442A", "#C9562A", "#B4532A", "#D0682E"], ["#F2A23A", "#F6C45A", "#EC8A3A"])
    rnd = random.Random(21)
    layers = ([], [], [])
    n = 0
    while n < 560:
        hx, hy = rnd.uniform(-1.2, 1.2), rnd.uniform(-1.05, 1.3)
        if not in_heart(hx / 0.96, hy / 0.96):
            continue
        n += 1
        x, y = 300 + hx * 128, 196 - hy * 102
        facing = (hx * 0.55 + hy * 0.75) + rnd.uniform(-0.45, 0.45)
        k = 0 if facing < -0.35 else (1 if facing < 0.45 else 2)
        sz = rnd.uniform(6.5, 11)
        layers[k].append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{sz:.1f}" ry="{sz * 0.62:.1f}" transform="rotate({rnd.uniform(-70, 70):.0f} {x:.1f} {y:.1f})" fill="{rnd.choice(pals[k])}"/>')
    out.append("".join("".join(l) for l in layers))
    # swing hanging from a low branch
    out.append(f'<path d="M 290 262 Q 250 244 196 250" stroke="#4A2F1E" stroke-width="8" fill="none" stroke-linecap="round"/><path d="M 286 258 Q 250 241 200 246" stroke="#8A6040" stroke-width="2" fill="none" stroke-linecap="round"/>')
    out.append('<g stroke="#C9A877" stroke-width="2.4"><line x1="206" y1="250" x2="204" y2="300"/><line x1="240" y1="245" x2="242" y2="300"/></g>')
    out.append(f'<rect x="196" y="298" width="54" height="8" rx="3" fill="{D.lin([(0, "#B07A48"), (1, "#6E4628")])}"/>')
    # a carved heart in the bark
    out.append('<path d="M 300 292 c -6 -6 -10 -1 -6 4 l 6 6 l 6 -6 c 4 -5 0 -10 -6 -4 Z" fill="none" stroke="#D9B48A" stroke-width="1.8"/>')
    # leaves drifting down
    out.append(falling(D, [("maple", 470, 250, 22, L_RED, 30), ("maple", 520, 330, 18, L_GOLD, -24), ("slim", 96, 262, 18, L_ORANGE, 50),
                           ("maple", 438, 308, 14, L_PLUM, 70), ("oak", 120, 330, 16, L_GOLD, -30)]))
    out.append('<g fill="none" stroke="#B4532A" stroke-width="2" stroke-dasharray="1 7" stroke-linecap="round" opacity="0.55">'
               '<path d="M 420 218 Q 470 214 466 236"/><path d="M 486 280 Q 530 296 520 316"/></g>')
    # type
    out.append(word(300, 436, "falling", SERIF_IT, 104, BROWN, max_w=380))
    fs = fit_size("FOR YOU", JOS, 58, 300, 12)
    w = measure("FOR YOU", JOS, fs, 12)
    out.append(text(300, 524, "FOR YOU", JOS, fs, "#B4532A", 12))
    from common import heart
    out.append(heart(300 - w / 2 - 34, 504, 16, "#C2482A") + heart(300 + w / 2 + 34, 504, 16, "#C2482A"))
    return D.render(out)


# ================================================================ 6. harvest (repaint)
def wheat_stalk(D, x0, y0, x1, y1, n=7, gl="#F4D27A", gd="#C9953E", stalk="#C9A060"):
    out = [f'<path d="M {x0:.1f} {y0:.1f} Q {(x0 + x1) / 2 + (x1 - x0) * 0.1:.1f} {(y0 + y1) / 2:.1f} {x1:.1f} {y1:.1f}" stroke="{stalk}" stroke-width="2.6" fill="none"/>']
    ang = math.atan2(y1 - y0, x1 - x0)
    ux, uy = math.cos(ang), math.sin(ang)
    deg = math.degrees(ang) + 90
    for i in range(n):
        t = i * 9.5
        cx, cy = x1 - ux * t, y1 - uy * t
        for sgn in (-1, 1):
            gx, gy = cx - uy * 4.6 * sgn, cy + ux * 4.6 * sgn
            out.append(f'<ellipse cx="{gx:.1f}" cy="{gy:.1f}" rx="3.6" ry="7.2" transform="rotate({deg + sgn * 26:.0f} {gx:.1f} {gy:.1f})" fill="{gl if sgn < 0 else gd}"/>')
            out.append(f'<line x1="{gx:.1f}" y1="{gy:.1f}" x2="{gx + ux * 16 - uy * 6 * sgn:.1f}" y2="{gy + uy * 16 + ux * 6 * sgn:.1f}" stroke="{gd}" stroke-width="1" opacity="0.8"/>')
    out.append(f'<ellipse cx="{x1 + ux * 6:.1f}" cy="{y1 + uy * 6:.1f}" rx="3.2" ry="7" transform="rotate({deg:.0f} {x1 + ux * 6:.1f} {y1 + uy * 6:.1f})" fill="{gl}"/>')
    return "".join(out)


def corn(D, x0, y0, x1, y1, w=34):
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    L = math.hypot(x1 - x0, y1 - y0)
    cob = D.lin([(0, "#F8D86A"), (0.5, "#E9B23A"), (1, "#B0761E")], 0, 0, 0, 1, key="cob")
    kern = "".join(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="4" ry="3.2" fill="#FFF0A0" opacity="{0.35 + 0.3 * ((x // 8 + y // 7) % 2):.2f}"/>'
                   for x in range(int(L * 0.3), int(L) - 6, 8) for y in range(int(-w * 0.36), int(w * 0.38), 7))
    cid = D.clip(f'<path d="M {L * 0.25:.1f} {-w / 2:.1f} Q {L * 0.9:.1f} {-w / 2:.1f} {L:.1f} 0 Q {L * 0.9:.1f} {w / 2:.1f} {L * 0.25:.1f} {w / 2:.1f} Z"/>')
    husk = D.lin([(0, "#E6D49A"), (1, "#9A8A4A")], key="husk")
    return (f'<g transform="translate({x0:.1f} {y0:.1f}) rotate({ang:.1f})">'
            f'<path d="M {L * 0.25:.1f} {-w / 2:.1f} Q {L * 0.9:.1f} {-w / 2:.1f} {L:.1f} 0 Q {L * 0.9:.1f} {w / 2:.1f} {L * 0.25:.1f} {w / 2:.1f} Z" fill="{cob}"/>'
            f'<g {cid}>{kern}<rect x="0" y="{w * 0.15:.1f}" width="{L:.1f}" height="{w:.1f}" fill="#7A4A10" opacity="0.25"/></g>'
            f'<path d="M 0 -6 Q {L * 0.3:.1f} {-w * 0.9:.1f} {L * 0.72:.1f} {-w * 0.95:.1f} Q {L * 0.42:.1f} {-w * 0.4:.1f} {L * 0.36:.1f} 2 Z" fill="{husk}"/>'
            f'<path d="M 0 6 Q {L * 0.36:.1f} {w * 1.0:.1f} {L * 0.66:.1f} {w * 1.0:.1f} Q {L * 0.4:.1f} {w * 0.4:.1f} {L * 0.34:.1f} -2 Z" fill="#C9B878"/>'
            f'<path d="M 0 -4 Q {L * 0.22:.1f} {-w * 0.3:.1f} {L * 0.5:.1f} {-w * 0.62:.1f}" stroke="#8A7A3A" stroke-width="1.4" fill="none" opacity="0.7"/>'
            f'<rect x="-14" y="-5" width="18" height="10" rx="3" fill="#8A7A4A"/></g>')


def squash(D, cx, cy, s, rot_=0):
    g = D.rad([(0, "#F8DCA8"), (0.55, "#E6B676"), (1, "#A8783E")], cx=0.35, cy=0.35, r=0.75, key="squash")
    k = s
    d = (f"M {cx:.1f} {cy - 0.9 * k:.1f} Q {cx + 0.28 * k:.1f} {cy - 0.9 * k:.1f} {cx + 0.26 * k:.1f} {cy - 0.3 * k:.1f} Q {cx + 0.5 * k:.1f} {cy + 0.05 * k:.1f} {cx + 0.48 * k:.1f} {cy + 0.42 * k:.1f} "
         f"Q {cx + 0.42 * k:.1f} {cy + 0.86 * k:.1f} {cx:.1f} {cy + 0.86 * k:.1f} Q {cx - 0.42 * k:.1f} {cy + 0.86 * k:.1f} {cx - 0.48 * k:.1f} {cy + 0.42 * k:.1f} "
         f"Q {cx - 0.5 * k:.1f} {cy + 0.05 * k:.1f} {cx - 0.26 * k:.1f} {cy - 0.3 * k:.1f} Q {cx - 0.28 * k:.1f} {cy - 0.9 * k:.1f} {cx:.1f} {cy - 0.9 * k:.1f} Z")
    return (f'<g transform="rotate({rot_:.1f} {cx:.1f} {cy:.1f})"><path d="{d}" fill="{g}"/>'
            f'<path d="M {cx + 0.1 * k:.1f} {cy - 0.85 * k:.1f} Q {cx + 0.3 * k:.1f} {cy:.1f} {cx + 0.36 * k:.1f} {cy + 0.7 * k:.1f}" stroke="#8A5A2A" stroke-width="2" fill="none" opacity="0.25"/>'
            f'<path d="M {cx - 0.12 * k:.1f} {cy - 0.7 * k:.1f} Q {cx - 0.16 * k:.1f} {cy - 0.4 * k:.1f} {cx - 0.28 * k:.1f} {cy + 0.1 * k:.1f}" stroke="#FFFFFF" stroke-width="{0.06 * k:.1f}" fill="none" stroke-linecap="round" opacity="0.45"/>'
            f'<rect x="{cx - 0.06 * k:.1f}" y="{cy - 1.05 * k:.1f}" width="{0.12 * k:.1f}" height="{0.18 * k:.1f}" rx="2" fill="#7A6A3A"/>'
            f'<ellipse cx="{cx:.1f}" cy="{cy + 0.8 * k:.1f}" rx="{0.08 * k:.1f}" ry="{0.04 * k:.1f}" fill="#8A6A3A"/></g>')


def grapes(D, cx, cy, s):
    g = D.rad([(0, "#B48AB4"), (0.5, "#6E3A6A"), (1, "#3A1A3A")], cx=0.35, cy=0.3, r=0.7, key="grape")
    pos = [(0, 0), (-1, 0.1), (1, 0.1), (-0.5, 0.9), (0.5, 0.9), (-1.4, 0.95), (1.3, 0.95), (0, 1.75), (-0.95, 1.75), (0.95, 1.75), (-0.45, 2.55), (0.45, 2.55), (0, 3.3)]
    out = [f'<path d="M {cx:.1f} {cy - s:.1f} q {s * 0.4:.1f} {-s * 1.2:.1f} {s * 1.6:.1f} {-s * 1.4:.1f}" stroke="#6A5A2A" stroke-width="3" fill="none"/>']
    for x, y in sorted(pos, key=lambda p: -p[1]):
        out.append(f'<circle cx="{cx + x * s:.1f}" cy="{cy + y * s * 0.95:.1f}" r="{s * 0.62:.1f}" fill="{g}"/>')
        out.append(f'<circle cx="{cx + x * s - s * 0.2:.1f}" cy="{cy + y * s * 0.95 - s * 0.22:.1f}" r="{s * 0.13:.1f}" fill="#FFFFFF" opacity="0.6"/>')
    return "".join(out)


@design("harvest")
def harvest():
    D = Doc("hv")
    out = [paper(D, "#C8652E", "#7A3216", 13, ink="#2A0E04", op=0.14, wash=["#E9904A", "#5A220E"])]
    out.append(glow(D, 300, 190, 240, "#FFC77A", 0.35))
    out.append('<g transform="translate(300 236) scale(1.14) translate(-300 -236)">')
    # handle and back rim of the basket
    weave = D.lin([(0, "#E2B276"), (0.5, "#C28A4E"), (1, "#8A5A2A")], key="weave")
    out.append(f'<path d="M 182 262 C 176 98 424 98 418 262" stroke="#7A4E26" stroke-width="20" fill="none"/>')
    out.append(f'<path d="M 182 262 C 176 98 424 98 418 262" stroke="#C99A5E" stroke-width="12" fill="none"/>')
    out.append('<path d="M 182 262 C 176 98 424 98 418 262" stroke="#7A4E26" stroke-width="12" fill="none" stroke-dasharray="3 9"/>')
    out.append('<ellipse cx="300" cy="262" rx="134" ry="24" fill="#5A3416"/>')
    # produce
    for x0, x1, y1 in ((300, 212, 120), (300, 246, 98), (300, 286, 88), (300, 326, 92), (300, 364, 108), (300, 394, 132)):
        out.append(wheat_stalk(D, x0, 250, x1, y1))
    out.append(corn(D, 250, 244, 136, 156, 32))
    out.append(squash(D, 392, 200, 62, 34))
    out.append(maple(D, 214, 214, 30, L_RED, -40, spots=3, seed=3))
    out.append(pumpkin(D, 300, 226, 120, 86, PK_ORANGE, cast=0, stem_h=0.18))
    out.append(apple(D, 224, 244, 30, seed=1, rot_=-12))
    out.append(apple(D, 372, 248, 28, pal=("#F2E07A", "#C9B03A", "#7A6A1E"), blush="#E8743A", seed=2, rot_=14, leaf=False))
    out.append(maple(D, 430, 244, 26, L_GOLD, 70))
    # basket body with checkered weave and cylindrical shading
    body = "M 166 262 L 434 262 L 404 346 Q 300 360 196 346 Z"
    cid = D.clip(f'<path d="{body}"/>')
    seg = D.lin([(0, "#F0C88A"), (0.45, "#D29A5A"), (1, "#7A4A20")], key="seg")
    rows = [f'<rect x="150" y="256" width="300" height="104" fill="#3E2410"/>']
    for x in range(150, 452, 22):
        rows.append(f'<rect x="{x - 2}" y="256" width="5" height="104" fill="#A8743E"/>')
    for i, y in enumerate(range(262, 352, 11)):
        off = 11 if i % 2 else 0
        for x in range(150 - off, 452, 22):
            rows.append(f'<rect x="{x + 4}" y="{y + 1}" width="18" height="9.5" rx="4.5" fill="{seg}"/>')
    out.append(f'<path d="{body}" fill="#5A3416"/><g {cid}>' + "".join(rows) +
               f'<rect x="150" y="250" width="300" height="110" fill="{cyl(D, "#FFFFFF", "#000000", "#000000", key="bshade")}" opacity="0.22"/>'
               f'<rect x="150" y="262" width="300" height="20" fill="{D.lin([(0, "#2A1404", 0.6), (1, "#2A1404", 0)])}"/></g>')
    out.append(shadow(D, 300, 352, 150, 12, strength=0.45))
    out.append('<path d="M 166 262 A 134 24 0 0 0 434 262" stroke="#8A5A2A" stroke-width="13" fill="none"/>')
    out.append('<path d="M 166 262 A 134 24 0 0 0 434 262" stroke="#E2B276" stroke-width="9" fill="none" stroke-dasharray="7 5"/>')
    out.append(grapes(D, 410, 270, 12))
    out.append("</g>")
    # type
    out.append(word(300, 458, "HARVEST", CINZEL, 96, "#FBEBD2", max_w=440, ls=8, sh="#5A1E0A", off=(0, 5)))
    out.append(ruled(514, "gather & give thanks", "#F6C860", size=40, ls=0, font=SERIF_IT, line_w=34, gap=16))
    return D.render(out)


# ================================================================ 7. oh my gourd (repaint)
@design("oh-my-gourd")
def oh_my_gourd():
    D = Doc("omg")
    out = [paper(D, "#7E3648", "#3E1622", 31, ink="#F6EDE0", op=0.06, wash=["#9A4A5A", "#2A0E18"])]
    out.append(glow(D, 300, 300, 230, "#E07A5A", 0.28))
    out.append(word(300, 146, "oh my", SERIF_IT, 96, "#FBEBD2", max_w=320))
    # the stack, plus two little gourds at the base
    out.append(shadow(D, 300, 432, 210, 18, "#14040A", 0.6))
    out.append(pumpkin(D, 138, 404, 98, 66, PK_GREEN, warts=14, seed=3, cast=0.4, curl=False, stem_h=0.3))
    out.append(pumpkin(D, 462, 408, 88, 60, PK_GOLD, stripes="#7E8A3A", cast=0.4, stem_h=0.28, lobes=3))
    out.append(pumpkin(D, 300, 370, 236, 124, PK_ORANGE, cast=0, curl=False, stem_h=0.08))
    out.append(shadow(D, 300, 318, 90, 12, "#2A0A00", 0.5))
    out.append(pumpkin(D, 300, 282, 164, 92, PK_CREAM, cast=0, curl=False, stem_h=0.08))
    out.append(shadow(D, 302, 240, 54, 8, "#2A0A00", 0.45))
    out.append(pumpkin(D, 298, 212, 98, 66, PK_SAGE, cast=0, curl=True, stem_h=0.4, stem_lean=0.12, leaf=L_OLIVE))
    out.append(falling(D, [("maple", 112, 300, 22, L_RED, -30), ("maple", 494, 260, 20, L_GOLD, 40), ("slim", 476, 340, 16, L_ORANGE, -60)]))
    out.append(word(300, 534, "GOURD!", BEBAS, 128, "#F2B94A", max_w=420, ls=12, sh="#1E0810", off=(0, 6)))
    return D.render(out)


# ================================================================ 8. autumn is calling (repaint)
@design("autumn-is-calling")
def autumn_is_calling():
    D = Doc("aic")
    out = [paper(D, "#FBF3E6", "#EAD8BE", 17, wash=["#E9B07A", "#B8A06A"])]
    out.append(word(300, 156, "AUTUMN", ANTON, 116, "#B4532A", max_w=420, ls=8, sh="#E2C6A4", off=(4, 4)))
    out.append(word(300, 228, "is calling", SERIF_IT, 74, BROWN, max_w=360))
    # rotary desk phone, glossy mustard
    body_g = cyl(D, "#FFD27A", "#E0A23A", "#9A6418")
    out.append(shadow(D, 306, 522, 190, 20, strength=0.45))
    out.append(f'<path d="M 154 518 L 186 404 Q 196 364 240 360 L 360 360 Q 404 364 414 404 L 446 518 Q 300 532 154 518 Z" fill="{body_g}"/>')
    out.append(f'<path d="M 154 518 Q 300 532 446 518 L 446 508 Q 300 522 154 508 Z" fill="#7A4A10" opacity="0.55"/>')
    out.append('<path d="M 200 404 Q 210 376 244 374" stroke="#FFF2C8" stroke-width="6" stroke-linecap="round" fill="none" opacity="0.6"/>')
    # dial
    dial = D.rad([(0, "#FFFBF0"), (0.8, "#F2E4C8"), (1, "#C9B08A")], cx=0.4, cy=0.35, r=0.7)
    out.append(f'<ellipse cx="300" cy="448" rx="70" ry="62" fill="#9A6418" opacity="0.5"/><ellipse cx="300" cy="444" rx="68" ry="60" fill="{dial}"/>')
    for i in range(10):
        a = math.radians(-60 - i * 28)
        hx, hy = 300 + 48 * math.cos(a), 444 + 42 * math.sin(a)
        out.append(f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="9.5" ry="8.5" fill="#7A4A14"/><ellipse cx="{hx + 1:.1f}" cy="{hy + 1.5:.1f}" rx="6.5" ry="5.5" fill="#F6EDE0"/>')
    out.append(f'<ellipse cx="300" cy="444" rx="24" ry="21" fill="{D.rad([(0, "#F6EDE0"), (1, "#D9C6A4")])}" stroke="#B4532A" stroke-width="3"/>')
    out.append(maple(D, 300, 446, 11, L_RED, 0, shade=0.15, vein_op=0.3))
    out.append('<path d="M 352 470 l 20 10" stroke="#5A3A10" stroke-width="5" stroke-linecap="round"/>')
    # cradle and handset
    for x in (214, 386):
        out.append(f'<path d="M {x - 16} 368 L {x - 10} 330 L {x + 10} 330 L {x + 16} 368 Z" fill="#C88A2A"/><rect x="{x - 12}" y="322" width="24" height="10" rx="4" fill="#7A4A10"/>')
    hs = cyl(D, "#FFD27A", "#E0A23A", "#9A6418", key="hs")
    out.append(shadow(D, 300, 336, 160, 10, strength=0.35))
    out.append(f'<path d="M 166 312 Q 166 290 190 288 L 410 288 Q 434 290 434 312 L 440 330 Q 438 344 420 344 L 396 344 Q 384 340 380 328 L 380 314 L 220 314 L 220 328 Q 216 340 204 344 L 180 344 Q 162 344 160 330 Z" fill="{D.lin([(0, "#FFE29A"), (0.4, "#E8AE46"), (1, "#9A6418")])}"/>')
    out.append('<path d="M 194 296 L 404 296" stroke="#FFF6DC" stroke-width="5" stroke-linecap="round" opacity="0.7"/>')
    # coiled cord from the handset down to the base, with a leaf caught in it
    cord = []
    for i in range(30):
        t = i / 29
        x = 168 - 70 * math.sin(math.pi * t) + 26 * t
        y = 344 + 168 * t
        cord.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="13" ry="5" fill="none" stroke="#9A6418" stroke-width="4.5" transform="rotate(-14 {x:.1f} {y:.1f})"/>')
        cord.append(f'<ellipse cx="{x - 1:.1f}" cy="{y - 1:.1f}" rx="13" ry="5" fill="none" stroke="#F2C462" stroke-width="2" transform="rotate(-14 {x:.1f} {y:.1f})" opacity="0.8"/>')
    out.append("".join(cord))
    out.append(maple(D, 112, 440, 22, L_RED, -50, spots=2, seed=8))
    # ringing
    out.append('<g fill="none" stroke="#B4532A" stroke-width="4" stroke-linecap="round">'
               '<path d="M 146 280 q -14 -14 -10 -34"/><path d="M 128 290 q -22 -20 -16 -50"/>'
               '<path d="M 454 280 q 14 -14 10 -34"/><path d="M 472 290 q 22 -20 16 -50"/></g>')
    out.append(falling(D, [("maple", 498, 360, 24, L_GOLD, 30), ("oak", 520, 450, 20, L_BROWN, -20), ("slim", 86, 196, 18, L_OLIVE, -40), ("maple", 512, 190, 18, L_PLUM, 20)]))
    return D.render(out)


# ================================================================ scene helpers
class Cam:
    """Pinhole camera: X right, Y up (metres), Z forward. Screen centre (cx, vpy)."""

    def __init__(self, f=300, cx=300, vpy=290, eye=1.6):
        self.f, self.cx, self.vpy, self.eye = f, cx, vpy, eye

    def __call__(self, X, Y, Z):
        return (self.cx + self.f * X / Z, self.vpy + self.f * (self.eye - Y) / Z)


def mirror(svg, cx):
    return f'<g transform="translate({2 * cx:.1f} 0) scale(-1 1)">{svg}</g>'


def birds(spec, color="#3A2A3A", sw=2.2):
    return f'<g fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round">' + "".join(
        f'<path d="M {x - s:.1f} {y:.1f} q {s / 2:.1f} {-s * 0.6:.1f} {s:.1f} 0 q {s / 2:.1f} {-s * 0.6:.1f} {s:.1f} 0"/>' for x, y, s in spec) + "</g>"


def cloud_puffs(D, cx, cy, w, seed, col="#FFFFFF", shade="#C9B4C0", lit="#FFF6E6", n=16):
    rnd = random.Random(seed)
    base, sh, li = [], [], []
    for i in range(n):
        t = (i + 0.5) / n
        x = cx - w / 2 + w * t + rnd.uniform(-8, 8)
        r = (math.sin(math.pi * t) ** 0.7) * w * 0.17 + rnd.uniform(4, 9)
        y = cy - r * 0.45 + rnd.uniform(-4, 4)
        base.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>')
        sh.append(f'<circle cx="{x:.1f}" cy="{y + r * 0.35:.1f}" r="{r * 0.7:.1f}"/>')
        li.append(f'<circle cx="{x + r * 0.15:.1f}" cy="{y - r * 0.3:.1f}" r="{r * 0.55:.1f}"/>')
    flat = f'<rect x="{cx - w / 2:.1f}" y="{cy - 6:.1f}" width="{w:.1f}" height="10" rx="5"/>'
    return (f'<g fill="{col}">{"".join(base)}{flat}</g><g fill="{shade}" opacity="0.45">{"".join(sh)}</g>'
            f'<g fill="{lit}" opacity="0.7">{"".join(li)}</g>')


def person(x, base, h, coat, rim=None, child=False, flip=1, hat=None):
    """Small walking figure; x at feet, h in px."""
    k = h / 100
    out = [f'<g transform="translate({x:.1f} {base:.1f}) scale({k * flip:.3f} {k:.3f})">',
           '<path d="M -8 -46 L 9 -46 L 12 -2 L 6 -2 L 3 -28 L -1 -2 L -7 -2 L -10 -44 Z" fill="#2A2028"/>',
           f'<path d="M -13 -84 Q 0 -92 13 -84 L 15 -44 L -13 -44 Z" fill="{coat}"/>',
           '<circle cx="0" cy="-94" r="9" fill="#3A2A22"/>',
           f'<path d="M -12 -80 Q -18 -64 -14 -48 M 12 -80 Q 18 -64 16 -50" stroke="{coat}" stroke-width="6" stroke-linecap="round" fill="none"/>']
    if hat:
        out.append(f'<path d="M -11 -98 Q 0 -112 11 -98 Z" fill="{hat}"/><circle cx="0" cy="-110" r="3.5" fill="{hat}"/>')
    if rim:
        out.append(f'<path d="M 13 -84 L 15 -44" stroke="{rim}" stroke-width="3" stroke-linecap="round"/><path d="M 6 -101 Q 10 -95 8 -88" stroke="{rim}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    out.append("</g>")
    return "".join(out)


# ================================================================ 9. pumpkin patch at golden hour
@design("pumpkin-patch")
def pumpkin_patch():
    D = Doc("pp")
    C = Cam(f=300, cx=300, vpy=340, eye=1.6)
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#45457A"), (0.22, "#7A6290"), (0.42, "#C88A8E"), (0.53, "#F2B07A"), (0.62, "#FBD69A"), (1, "#FBD69A")])}"/>']
    out.append(glow(D, 446, 322, 300, "#FFE3A0", 0.85))
    out.append('<circle cx="446" cy="320" r="24" fill="#FFF4D2"/>')
    out.append('<g fill="#F6B88E" opacity="0.5">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="4"/>' for x, y, w in ((120, 280, 80), (80, 292, 50), (520, 262, 70), (360, 288, 60))) + "</g>")
    out.append(birds([(150, 300, 9), (176, 288, 7), (196, 304, 6)], "#5A3A4A"))
    # type in the sky
    out.append(word(300, 130, "pumpkin", SERIF_IT, 90, "#FCEBD2", max_w=380, sh="#2A2246", off=(0, 4), sh_op=0.6))
    out.append(word(300, 252, "PATCH", ANTON, 124, "#FCEBD2", max_w=440, ls=14, sh="#2A2246", off=(0, 5), sh_op=0.55))
    # far hills and the near tree line, hazy in the low sun
    line = rough([(-10, 326), (120, 316), (240, 326), (360, 318), (480, 324), (610, 316)], 3, amp=5)
    out.append(f'<polygon points="{P(line + [(610, 380), (-10, 380)])}" fill="#B497A6"/>')
    line2 = rough([(-10, 350), (150, 342), (300, 348), (420, 344), (610, 350)], 5, amp=3)
    out.append(f'<polygon points="{P(line2 + [(610, 400), (-10, 400)])}" fill="#9E7A78"/>')
    rnd = random.Random(8)
    for x in range(-10, 620, 22):
        if 400 < x < 480:
            continue
        cx = x + rnd.uniform(-6, 6)
        cy = 340 + rnd.uniform(-4, 6)
        r = rnd.uniform(12, 20)
        out.append(foliage(D, cx, cy, r, r * 0.8, (["#8E5A5A", "#7A4E58"], ["#B4705E", "#A8665A", "#C08A62"], ["#E2A070", "#EAB27A"]), int(x) + 3, n=22, size=(3.5, 7), light=(0.8, -0.6)))
    out.append(f'<rect x="0" y="300" width="600" height="70" fill="{D.lin([(0, "#FBD69A", 0), (1, "#FBD69A", 0.45)])}"/>')
    # red barn and silo, the gable end in shade and the long side lit by the sun
    silo = cyl(D, "#C8BCB4", "#9A8A88", "#6A5A5E")
    out.append(f'<rect x="262" y="290" width="34" height="88" fill="{silo}"/><path d="M 262 290 Q 279 266 296 290 Z" fill="#6E5A5E"/>'
               '<path d="M 279 268 Q 292 276 296 290" stroke="#F2C08A" stroke-width="2" fill="none"/>')
    out.append('<g stroke="#6A5A5E" stroke-width="1.2" opacity="0.6">' + "".join(f'<line x1="262" y1="{y}" x2="296" y2="{y}"/>' for y in range(300, 378, 9)) + "</g>")
    side = [(190, 326), (262, 332), (262, 380), (190, 382)]
    roof = [(145, 278), (182, 296), (194, 326), (266, 332), (256, 302), (218, 284)]
    gable = [(98, 326), (110, 296), (145, 278), (182, 296), (194, 326), (194, 382), (98, 382)]
    out.append(f'<polygon points="{P(side)}" fill="{D.lin([(0, "#C2402E"), (1, "#E0603A")], 0, 0, 1, 0)}"/>')
    out.append('<g stroke="#8E2A1E" stroke-width="1.2" opacity="0.5">' + "".join(f'<line x1="{x}" y1="{326 + (x - 190) * 0.08:.1f}" x2="{x}" y2="{382 - (x - 190) * 0.03:.1f}"/>' for x in range(196, 262, 6)) + "</g>")
    out.append(f'<polygon points="{P(roof)}" fill="#5E4A50"/><polyline points="{P(roof[2:5])}" fill="none" stroke="#F2C08A" stroke-width="2.4"/>')
    out.append(f'<polygon points="{P(gable)}" fill="#8E2E22"/>')
    out.append('<g stroke="#6E2018" stroke-width="1" opacity="0.6">' + "".join(f'<line x1="{x}" y1="300" x2="{x}" y2="382"/>' for x in range(104, 194, 6)) + "</g>")
    out.append(f'<polyline points="{P(gable[:5])}" fill="none" stroke="#F0E2CC" stroke-width="3" stroke-linejoin="round"/>')
    out.append('<rect x="124" y="336" width="44" height="46" fill="#7A2418" stroke="#F0E2CC" stroke-width="3"/><path d="M 124 336 L 168 382 M 168 336 L 124 382" stroke="#F0E2CC" stroke-width="2.6"/>')
    out.append('<rect x="136" y="298" width="20" height="20" fill="#3A1A14" stroke="#F0E2CC" stroke-width="2.6"/>')
    out.append('<g fill="#3A1A14" stroke="#F6E2C4" stroke-width="2">' + "".join(f'<rect x="{x}" y="{344 + (x - 190) * 0.06:.1f}" width="10" height="12"/>' for x in (206, 230)) + "</g>")
    out.append('<rect x="207" y="345.5" width="8" height="10" fill="#FFC870" opacity="0.8"/>')
    # round hay bales beside the barn
    for x, y, r in ((74, 380, 15), (54, 386, 13), (318, 380, 12)):
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{r * 1.2:.1f}" ry="{r}" fill="{D.rad([(0, "#F6D48A"), (1, "#B88A3E")], cx=0.65, cy=0.4, r=0.7, key="bale")}"/>'
                   f'<ellipse cx="{x - r * 0.6:.1f}" cy="{y}" rx="{r * 0.5:.1f}" ry="{r * 0.9:.1f}" fill="#A8783A"/><ellipse cx="{x - r * 0.6:.1f}" cy="{y}" rx="{r * 0.25:.1f}" ry="{r * 0.45:.1f}" fill="none" stroke="#7A5424" stroke-width="1.2"/>')
    # the field
    out.append(f'<rect x="-10" y="372" width="620" height="240" fill="{D.lin([(0, "#A8904E"), (0.25, "#7E7A3A"), (1, "#3E4422")])}"/>')
    out.append(f'<rect x="-10" y="372" width="620" height="60" fill="{D.rad([(0, "#FFD48A", 0.5), (1, "#FFD48A", 0)], cx=0.75, cy=0, r=0.6)}"/>')
    # split-rail fence
    fl = []
    for X in [-14 + i * 2.4 for i in range(14)]:
        a, b = C(X, 0, 13), C(X, 1.1, 13)
        fl.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
    out.append('<g stroke="#4A2E1E" stroke-width="3">' + "".join(fl) + "</g>")
    for Y in (0.45, 0.9):
        a, b = C(-15, Y, 13), C(15, Y, 13)
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#5A3A24" stroke-width="2.6"/>')
    # vine rows converging toward the sun
    rnd = random.Random(31)
    for X in (-7.5, -5.2, -2.9, -0.6, 1.7, 4.0, 6.3, 8.6):
        pts = [C(X + rnd.uniform(-0.15, 0.15), 0, Z) for Z in (13, 9, 6.5, 4.8, 3.6, 2.7, 2.0, 1.5)]
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        out.append(f'<path d="{d}" fill="none" stroke="#3E4A22" stroke-width="3" opacity="0.6"/>')
        for Z in [12 * 0.84 ** i for i in range(14)]:
            x, y = C(X + rnd.uniform(-0.5, 0.5), 0, Z)
            r = C.f * 0.22 / Z
            out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 1.2:.1f}" ry="{r * 0.6:.1f}" fill="{rnd.choice(["#4E5E2A", "#5E6E30", "#6E7A36"])}"/>'
                       f'<ellipse cx="{x + r * 0.3:.1f}" cy="{y - r * 0.2:.1f}" rx="{r * 0.6:.1f}" ry="{r * 0.3:.1f}" fill="#A8A85A" opacity="0.6"/>')
    # pumpkins, far to near, lit from the right with long shadows to the left
    pks = []
    for X in (-6.3, -4.0, -1.8, 0.5, 2.8, 5.2, 7.4):
        Z = 11
        while Z > 1.7:
            pks.append((Z * rnd.uniform(0.9, 1.05), X + rnd.uniform(-0.7, 0.7)))
            Z *= rnd.uniform(0.62, 0.78)
    pals = [PK_ORANGE, PK_ORANGE, PK_DEEP, PK_GOLD, PK_ORANGE, PK_CREAM]
    for Z, X in sorted(pks, reverse=True):
        x, y = C(X, 0, Z)
        if y > 580 or (Z < 3 and 150 < x < 450):
            continue
        w = C.f * 0.55 / Z
        out.append(f'<ellipse cx="{x - w * 0.5:.1f}" cy="{y:.1f}" rx="{w * 0.9:.1f}" ry="{w * 0.12:.1f}" fill="#2A2A10" opacity="0.4"/>')
        out.append(mirror(pumpkin(D, x, y - w * 0.32, w, w * 0.72, rnd.choice(pals), cast=0, curl=w > 30, shade=True), x))
    # a family with a little wagon, rim-lit
    px, pb = C(-1.4, 0, 8.6)
    out.append(person(px, pb, 52, "#3E4A6A", rim="#FFD48A", hat="#B4532A"))
    out.append(person(px + 22, pb + 1, 34, "#B4532A", rim="#FFD48A", hat="#E9B54A"))
    out.append(f'<rect x="{px - 40:.1f}" y="{pb - 14:.1f}" width="28" height="10" rx="2" fill="#B8302A"/><circle cx="{px - 36:.1f}" cy="{pb - 2:.1f}" r="3.6" fill="#2A2028"/>'
               f'<circle cx="{px - 16:.1f}" cy="{pb - 2:.1f}" r="3.6" fill="#2A2028"/><line x1="{px - 12:.1f}" y1="{pb - 8:.1f}" x2="{px - 4:.1f}" y2="{pb - 30:.1f}" stroke="#2A2028" stroke-width="2"/>')
    out.append(mirror(pumpkin(D, px - 26, pb - 22, 20, 14, PK_ORANGE, cast=0, curl=False), px - 26))
    # hero pumpkins in the foreground
    out.append('<ellipse cx="130" cy="560" rx="110" ry="14" fill="#1E220C" opacity="0.5"/><ellipse cx="452" cy="566" rx="96" ry="12" fill="#1E220C" opacity="0.5"/>')
    out.append(mirror(pumpkin(D, 180, 504, 150, 108, PK_ORANGE, cast=0, leaf=L_OLIVE), 180))
    out.append(mirror(pumpkin(D, 466, 520, 118, 84, PK_GOLD, cast=0), 466))
    out.append(mirror(pumpkin(D, 380, 548, 70, 50, PK_CREAM, cast=0, curl=False), 380))
    out.append(f'<g fill="none" stroke="#4E5E2A" stroke-width="4" stroke-linecap="round"><path d="M -10 590 Q 60 560 110 572 T 230 570"/><path d="M 300 600 Q 340 560 400 580 T 560 560"/></g>')
    for x, y, r_ in ((92, 568, 30), (250, 574, -20), (330, 584, 10), (560, 552, -30)):
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="26" ry="15" transform="rotate({r_} {x} {y})" fill="#5E6E30"/><ellipse cx="{x + 5}" cy="{y - 4}" rx="14" ry="7" transform="rotate({r_} {x} {y})" fill="#A8A85A" opacity="0.55"/>')
    return D.render(out)


# ================================================================ 10. apple picking (poster)
def apple_tree(D, C, X, Z, seed, ripe=0.5):
    rnd = random.Random(seed)
    bx, by = C(X, 0, Z)
    k = C.f / Z
    cx, cy = C(X, 2.5, Z)
    rx, ry = 1.9 * k, 1.35 * k
    out = [f'<ellipse cx="{bx - 0.7 * k:.1f}" cy="{by + 0.1 * k:.1f}" rx="{2.1 * k:.1f}" ry="{0.35 * k:.1f}" fill="#2E4220" opacity="0.45"/>',
           f'<path d="M {bx - 0.12 * k:.1f} {by:.1f} Q {bx - 0.1 * k:.1f} {by - 0.8 * k:.1f} {bx - 0.5 * k:.1f} {cy:.1f} L {bx - 0.36 * k:.1f} {cy:.1f} Q {bx:.1f} {by - 1.0 * k:.1f} {bx + 0.4 * k:.1f} {cy + 0.1 * k:.1f} '
           f'L {bx + 0.52 * k:.1f} {cy + 0.1 * k:.1f} Q {bx + 0.12 * k:.1f} {by - 0.8 * k:.1f} {bx + 0.14 * k:.1f} {by:.1f} Z" fill="#4A3424"/>']
    n = int(min(170, 12 + rx * 1.6))
    size = (max(1.2, rx * 0.09), max(2.2, rx * 0.18))
    out.append(foliage(D, cx, cy, rx, ry, (["#3E5A2A", "#4A6230"], ["#6A8236", "#7A8A3A", "#8A9640"], ["#B8B85A", "#C9B85A", "#D8C26A"]), seed, n=n, size=size, light=(0.75, -0.65), leafy=rx > 30))
    if rx > 6:
        ap = []
        for _ in range(int(rx * 0.5)):
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.random() ** 0.5 * 0.9
            x, y = cx + math.cos(a) * d * rx, cy + math.sin(a) * d * ry
            r = max(1.2, rx * 0.06)
            ap.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{rnd.choice(["#C62E26", "#D8402A", "#B0241E"])}"/><circle cx="{x - r * 0.3:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.35:.1f}" fill="#FFD8B0" opacity="0.7"/>')
        out.append("".join(ap))
    return "".join(out)


def crate(D, x, y, w, h, fill_fn=None):
    """Front-facing slatted wooden crate; fill_fn(x0, x1, top) paints what is piled inside."""
    wood = D.lin([(0, "#D8A86A"), (1, "#A8743E")], key="crwood")
    out = [f'<polygon points="{P([(x + 10, y - 16), (x + w - 10, y - 16), (x + w, y), (x, y)])}" fill="#5A3A20"/>']
    if fill_fn:
        out.append(fill_fn(x + 6, x + w - 6, y - 4))
    for i in range(3):
        sy = y + i * h / 3
        out.append(f'<rect x="{x}" y="{sy + 2:.1f}" width="{w}" height="{h / 3 - 4:.1f}" rx="2" fill="{wood}"/>')
        out.append(wood_grain(int(x + sy), (x + 4, sy + 4, x + w - 4, sy + h / 3 - 6), "#7A4A22", n=4, op=0.45, sw=1))
    out.append(f'<rect x="{x}" y="{y}" width="12" height="{h}" fill="#C08A4E"/><rect x="{x + w - 12}" y="{y}" width="12" height="{h}" fill="#8A5A2E"/>')
    for nx in (x + 6, x + w - 6):
        for i in range(3):
            out.append(f'<circle cx="{nx}" cy="{y + i * h / 3 + h / 6:.1f}" r="1.8" fill="#3A2A1E"/>')
    out.append(f'<rect x="{x + w * 0.3:.1f}" y="{y + h / 3 + 6:.1f}" width="{w * 0.4:.1f}" height="{h / 3 - 12:.1f}" rx="3" fill="#2A1A10" opacity="0.55"/>')
    return "".join(out)


def apple_picking_art():
    D = Doc("apk")
    C = Cam(f=300, cx=300, vpy=252, eye=1.7)
    out = [f'<rect width="600" height="444" fill="{D.lin([(0, "#7FA6C2"), (0.55, "#C9D6D2"), (1, "#F4E2BE")])}"/>']
    out.append(glow(D, 120, 120, 180, "#FFF4D8", 0.6))
    out.append(cloud_puffs(D, 160, 140, 170, 3, shade="#9AAABC") + cloud_puffs(D, 470, 110, 130, 5, shade="#9AAABC") + cloud_puffs(D, 360, 170, 80, 9, shade="#9AAABC", n=9))
    out.append(birds([(420, 150, 7), (438, 142, 5)], "#4A4A5A", 1.8))
    # distant hills in autumn colour, hazy
    line = rough([(-10, 238), (90, 226), (200, 236), (320, 222), (440, 234), (610, 224)], 7, amp=5)
    out.append(f'<polygon points="{P(line + [(610, 270), (-10, 270)])}" fill="#A8A0A0"/>')
    rnd = random.Random(4)
    for x in range(-10, 620, 13):
        out.append(f'<circle cx="{x + rnd.uniform(-4, 4):.1f}" cy="{240 + rnd.uniform(-3, 6):.1f}" r="{rnd.uniform(6, 10):.1f}" fill="{rnd.choice(["#C49A7A", "#B88A78", "#C9AE88", "#A8907E"])}"/>')
    out.append(f'<rect x="0" y="220" width="600" height="40" fill="{D.lin([(0, "#F4E2BE", 0), (1, "#F4E2BE", 0.6)])}"/>')
    # orchard floor and the mown aisle
    out.append(f'<rect x="0" y="250" width="600" height="200" fill="{D.lin([(0, "#9AA25A"), (1, "#56702E")])}"/>')
    aisle = [C(-1.6, 0, 400), C(1.6, 0, 400), C(1.6, 0, 1.5), C(-1.6, 0, 1.5)]
    out.append(f'<polygon points="{P(aisle)}" fill="#B8BC6A" opacity="0.55"/>')
    for X in (-0.8, 0, 0.8):
        out.append(f'<polygon points="{P([C(X - 0.35, 0, 400), C(X + 0.05, 0, 400), C(X + 0.05, 0, 1.5), C(X - 0.35, 0, 1.5)])}" fill="#D8D488" opacity="0.25"/>')
    # rows of apple trees, far to near
    trees = []
    for X in (-4.6, 4.6, -10, 10):
        Z = 7.5 if abs(X) < 6 else 13
        k = 0
        while Z < 220:
            trees.append((Z, X, int(Z * 10 + X * 3)))
            Z *= 1.32
            k += 1
    for Z, X, sd in sorted(trees, reverse=True):
        out.append(apple_tree(D, C, X + (0.2 if sd % 2 else -0.2), Z, sd))
    # fallen apples in the grass
    for X, Z in ((-3.4, 9), (-4.0, 8), (3.8, 10), (4.4, 8.4), (-2.6, 6.4), (3.0, 6)):
        x, y = C(X, 0, Z)
        out.append(f'<circle cx="{x:.1f}" cy="{y - 2:.1f}" r="{C.f * 0.05 / Z * 1.6:.1f}" fill="#C62E26"/>')
    # wooden orchard ladder leaning into the near right tree, a picker up top
    lx, lb = 456, 386
    out.append(f'<g stroke="#8A5A2E" stroke-width="5" stroke-linecap="round"><line x1="{lx - 20}" y1="{lb}" x2="{lx + 6}" y2="{lb - 168}"/><line x1="{lx + 22}" y1="{lb}" x2="{lx + 10}" y2="{lb - 168}"/></g>'
               f'<line x1="{lx + 44}" y1="{lb + 4}" x2="{lx + 10}" y2="{lb - 164}" stroke="#6E4422" stroke-width="4" stroke-linecap="round"/>'
               '<g stroke="#B8844A" stroke-width="3.4" stroke-linecap="round">' + "".join(
                   f'<line x1="{lx - 20 + 26 * t:.1f}" y1="{lb - 168 * t:.1f}" x2="{lx + 22 - 12 * t:.1f}" y2="{lb - 168 * t:.1f}"/>' for t in (0.14, 0.32, 0.5, 0.68, 0.86)) + "</g>")
    out.append(person(lx + 8, lb - 116, 74, "#2E5A7A", rim="#FFF0C8", hat="#E9B54A"))
    out.append(f'<path d="M {lx - 6} {lb - 150} q 10 16 24 2 l -2 -10 q -10 4 -20 -2 Z" fill="#E9C47A" stroke="#8A5A2E" stroke-width="1.5"/>')
    # foreground: a crate heaped with apples, more in the grass, a basket
    def heap(x0, x1, top):
        r = random.Random(12)
        s = []
        for row, yy in enumerate((top + 4, top - 14, top - 30)):
            n = 6 - row
            for i in range(n):
                x = x0 + 20 + row * 16 + i * (x1 - x0 - 40 - row * 32) / max(1, n - 1)
                s.append(apple(D, x + r.uniform(-4, 4), yy + r.uniform(-3, 3), 19 - row, seed=row * 9 + i, rot_=r.uniform(-30, 30), leaf=(row == 2 and i == 1),
                               pal=r.choice([("#F26A4A", "#C62E26", "#7A1616"), ("#F07A4A", "#D0402A", "#8A1E16"), ("#F2D26A", "#C9A83A", "#7A6A1E")])))
        return "".join(s)
    out.append(shadow(D, 190, 436, 150, 14, "#1A2A0A", 0.5))
    out.append(crate(D, 66, 356, 218, 80, heap))
    for x, y, r_ in ((312, 426, 18), (344, 434, 16)):
        out.append(apple(D, x, y, r_, seed=x, cast=0.3, leaf=False, rot_=20))
    out.append('<g stroke-linecap="round" fill="none" stroke-width="2">' + "".join(
        f'<path d="M {x:.1f} 444 q {random.Random(x).uniform(-3, 3):.1f} -8 {random.Random(x + 1).uniform(-5, 5):.1f} -16" stroke="{c}"/>' for x, c in
        [(i * 7.3 % 600, ("#7A8A3A", "#A8A85A", "#4E6228")[i % 3]) for i in range(80)]) + "</g>")
    out.append(maple(D, 400, 426, 16, L_GOLD, 120, shade=0.15))
    return D.render(out)


@design("apple-picking")
def apple_picking():
    return apple_picking_art()


# ================================================================ 11. take the scenic route (misty foliage road)
def catmull(pts, n=8):
    out = []
    pts = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(len(p1))))
    out.append(pts[-2])
    return out


def dab_fill(D, poly, seed, cols, n, size, light=(0.7, -0.7)):
    """Fill a polygon region with foliage dabs (clipped), light from `light`."""
    xs = [x for x, _ in poly]
    ys = [y for _, y in poly]
    cid = D.clip(f'<polygon points="{P(poly)}"/>')
    rnd = random.Random(seed)
    out = []
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(*size) * (0.6 + 0.6 * (y - y0) / max(1, y1 - y0))
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 0.8:.1f}" fill="{rnd.choice(cols)}"/>')
    return f'<g {cid}>' + "".join(out) + "</g>"


@design("scenic-route")
def scenic_route():
    D = Doc("sr")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#D9D2D6"), (0.3, "#EFE2D2"), (0.55, "#F6DFC2"), (1, "#F2D6B8")])}"/>']
    out.append(glow(D, 470, 210, 220, "#FFF2DA", 0.85))
    out.append(word(300, 104, "take the", SERIF_IT, 54, "#5A3A2E", max_w=300))
    out.append(word(300, 196, "SCENIC ROUTE", ANTON, 92, "#A8432A", max_w=460, ls=5, sh="#E8CDB0", off=(3, 4)))
    # far ridge, lavender haze
    r1 = rough([(-10, 248), (80, 236), (170, 244), (260, 228), (360, 240), (470, 230), (610, 244)], 11, amp=6)
    poly = r1 + [(610, 330), (-10, 330)]
    out.append(f'<polygon points="{P(poly)}" fill="#BCAFC0"/>')
    out.append(dab_fill(D, poly, 12, ["#C8BCCB", "#B0A2B6", "#C4B0B8", "#B8A8B0"], 220, (3, 6)))
    out.append(f'<rect x="0" y="236" width="600" height="70" fill="{D.lin([(0, "#F6E8D8", 0), (0.6, "#F6E8D8", 0.75), (1, "#F6E8D8", 0.2)])}"/>')
    # middle ridge, warm and hazy
    r2 = rough([(-10, 290), (110, 272), (220, 286), (330, 270), (450, 284), (610, 268)], 13, amp=6)
    poly = r2 + [(610, 380), (-10, 380)]
    out.append(f'<polygon points="{P(poly)}" fill="#C89A86"/>')
    haze = [(["#B08478"], ["#C9987E"], ["#E2BC98"]), (["#A88A80"], ["#C4A488"], ["#DCC6A2"]), (["#A87A74"], ["#C08A7A"], ["#DDAE92"])]
    rnd = random.Random(14)
    cr = []
    for row, y0 in enumerate((282, 292, 304, 318)):
        for x in range(-10 + row * 6, 620, 16):
            y = (y_on(r2, x) or y0) + 6 + row * 12 + rnd.uniform(-3, 3)
            cr.append(crown(D, x + rnd.uniform(-4, 4), y, rnd.uniform(9, 12), haze[rnd.randrange(3)], x * 7 + row, n=3))
    out.append("".join(cr))
    out.append("".join(conifer(rnd.uniform(0, 600), 302 + rnd.uniform(0, 20), rnd.uniform(14, 24), "#9A8888", rnd.random()) for _ in range(9)))
    out.append(f'<rect x="0" y="282" width="600" height="70" fill="{D.lin([(0, "#F6E8D8", 0), (0.65, "#F6E8D8", 0.8), (1, "#F6E8D8", 0.1)])}"/>')
    # near ridge, peak colour: rows of rounded crowns, larger as they come closer
    r3 = rough([(-10, 336), (90, 322), (200, 340), (300, 330), (410, 338), (520, 322), (610, 332)], 17, amp=5)
    poly3 = r3 + [(610, 620), (-10, 620)]
    out.append(f'<polygon points="{P(poly3)}" fill="#8A3A24"/>')
    hot = ["#D8742E", "#E9A23A", "#C2482A", "#9A3424", "#F2C25A", "#E0862E", "#7E8A3A", "#B4532A"]
    pals = [(["#8E2E20", "#7A2A22"], ["#C2482A", "#B4402A"], ["#EE7A3C", "#F29A4A"]),
            (["#A8641E", "#9A5A1E"], ["#E0862E", "#D87A2A"], ["#F6B24A", "#FBC860"]),
            (["#B07A1E", "#9A6A1A"], ["#E0A62E", "#E9B23A"], ["#F6D266", "#FBE08A"]),
            (["#4E5A26", "#5A6428"], ["#7E8A3A", "#8A9640"], ["#B8B85A", "#C9C060"]),
            (["#6E2232", "#5E2030"], ["#9A3440", "#8E2E3A"], ["#C9566A", "#D0645A"])]
    weights = [0, 0, 1, 1, 1, 2, 2, 3, 4, 0]
    rows = []
    y = 336
    while y < 640:
        r = 9 + (y - 330) * 0.17
        rows.append((y, r))
        y += r * 0.62
    rnd = random.Random(18)
    cr = []
    for i, (yy, r) in enumerate(rows):
        x = -10 - rnd.uniform(0, r)
        while x < 620:
            ty = yy + rnd.uniform(-r * 0.2, r * 0.2)
            if i < 3:
                ty = max(ty, (y_on(r3, x) or 330) + r * 0.6)
            cr.append(crown(D, x, ty, r * rnd.uniform(0.85, 1.1), pals[rnd.choice(weights)], int(x * 13 + yy), n=7 if r > 20 else 4))
            x += r * rnd.uniform(1.15, 1.45)
    out.append("".join(cr))
    rnd = random.Random(19)
    out.append("".join(conifer(x, 360 + rnd.uniform(0, 60), rnd.uniform(26, 50), rnd.choice(["#2E4A34", "#3A5A3A", "#28402E"]), rnd.random(), light="#5E7A4A")
                       for x in (40, 128, 158, 446, 482, 556, 520)))
    # the road winding in from the foreground
    cl = [(232, 342, 8), (254, 360, 22), (300, 384, 44), (360, 418, 80), (386, 470, 132), (350, 534, 200), (284, 612, 300)]
    sm = catmull(cl, 10)
    left, right = [], []
    for i, (x, y, w) in enumerate(sm):
        a = sm[max(0, i - 1)]
        b = sm[min(len(sm) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        left.append((x + nx * w / 2, y + ny * w / 2 * 0.35))
        right.append((x - nx * w / 2, y - ny * w / 2 * 0.35))
    road = left + right[::-1]
    out.append(f'<polygon points="{P(road)}" fill="{D.lin([(0, "#9A8E96"), (0.4, "#6E6270"), (1, "#3E3440")], 0, 340, 0, 600, units="userSpaceOnUse")}"/>')
    out.append(f'<polyline points="{P(left)}" fill="none" stroke="#E8DCC8" stroke-width="2.2" opacity="0.8"/><polyline points="{P(right)}" fill="none" stroke="#E8DCC8" stroke-width="2.2" opacity="0.8"/>')
    dashes = []
    for i in range(0, len(sm) - 1, 2):
        (x1, y1, w1), (x2, y2, w2) = sm[i], sm[i + 1]
        dashes.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke-width="{max(1, w1 * 0.03):.1f}"/>')
    out.append('<g stroke="#F2C25A" stroke-linecap="butt">' + "".join(dashes) + "</g>")
    rnd = random.Random(22)
    out.append("".join(f'<ellipse cx="{x + rnd.uniform(-0.5, 0.5) * w:.1f}" cy="{y + rnd.uniform(-4, 4):.1f}" rx="{max(1, w * 0.02):.1f}" ry="{max(0.7, w * 0.012):.1f}" fill="{rnd.choice(hot)}"/>'
                       for x, y, w in sm[20:] for _ in range(4)))
    # a little teal wagon heading off into the hills, tail lights on in the mist
    cx, cy = 400, 452
    out.append(f'<ellipse cx="{cx}" cy="{cy + 2}" rx="26" ry="5" fill="#241C24" opacity="0.5"/>'
               f'<path d="M {cx - 24} {cy - 2} L {cx - 24} {cy - 18} Q {cx - 22} {cy - 34} {cx - 12} {cy - 36} L {cx + 12} {cy - 36} Q {cx + 22} {cy - 34} {cx + 24} {cy - 18} L {cx + 24} {cy - 2} Z" fill="#3E8A8A"/>'
               f'<path d="M {cx - 16} {cy - 22} L {cx - 13} {cy - 32} L {cx + 13} {cy - 32} L {cx + 16} {cy - 22} Z" fill="#C9D8D8" opacity="0.7"/>'
               f'<rect x="{cx - 24}" y="{cy - 12}" width="48" height="4" fill="#E8E0D0"/>'
               f'<rect x="{cx - 22}" y="{cy - 4}" width="9" height="8" rx="2" fill="#1E1A1E"/><rect x="{cx + 13}" y="{cy - 4}" width="9" height="8" rx="2" fill="#1E1A1E"/>'
               f'<rect x="{cx - 20}" y="{cy - 40}" width="40" height="3" fill="#2A2A2A"/>')
    out.append(mirror(pumpkin(D, cx - 6, cy - 44, 16, 11, PK_ORANGE, cast=0, curl=False, shade=False), cx - 6))
    for sx in (-20, 20):
        out.append(glow(D, cx + sx, cy - 17, 12, "#FF4A3A", 0.8) + f'<rect x="{cx + sx - 3}" y="{cy - 20}" width="6" height="5" rx="1" fill="#FF5A4A"/>')
    # a white birch pair framing the left foreground and a big maple on the right
    for x, top, w in ((78, 330, 16), (108, 360, 12)):
        out.append(f'<path d="M {x - w / 2} 612 L {x - w * 0.35:.1f} {top} L {x + w * 0.35:.1f} {top} L {x + w / 2} 612 Z" fill="{cyl(D, "#FFFFFF", "#E8E2D8", "#A8A098", key="birch")}"/>')
        rnd = random.Random(x)
        out.append("".join(f'<rect x="{x - w * 0.4 + rnd.uniform(0, w * 0.4):.1f}" y="{y:.0f}" width="{rnd.uniform(3, w * 0.5):.1f}" height="2.4" fill="#2A2420"/>' for y in range(top + 10, 600, 17)))
    out.append(foliage(D, 96, 340, 62, 46, (["#B07A1E", "#9A6A1A"], ["#E0A62E", "#D89A2A"], ["#F6D266", "#FBE08A"]), 31, n=180, size=(4, 8), light=(0.7, -0.7), leafy=True))
    out.append(f'<path d="M 532 612 Q 528 520 520 440 L 534 440 Q 546 520 552 612 Z" fill="#4A2E22"/>')
    out.append(foliage(D, 548, 400, 80, 64, (["#7A2420", "#8E2E22"], ["#C2402A", "#B4362A", "#D0542E"], ["#EE7A3C", "#F29A4A"]), 32, n=260, size=(4, 9), light=(0.7, -0.7), leafy=True))
    out.append(f'<rect x="0" y="560" width="600" height="40" fill="{D.lin([(0, "#2A1A14", 0), (1, "#2A1A14", 0.35)])}"/>')
    out.append(birds([(170, 252, 7), (188, 244, 5)], "#5A4A5A", 1.8))
    return D.render(out)


# ================================================================ 12. rainy days & good books (window seat)
@design("rainy-days-good-books")
def rainy_days():
    D = Doc("rd")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#4E6A72"), (1, "#2C3E46")])}"/>']
    out.append(grain(5, "#0E1A1E", 300, op=0.15))
    # the arched window and the rainy afternoon outside
    arch = "M 136 344 L 136 240 A 164 164 0 0 1 464 240 L 464 344 Z"
    out.append(f'<path d="M 116 352 L 116 240 A 184 184 0 0 1 484 240 L 484 352 Z" fill="#1E2C32" opacity="0.5"/>')
    gid = D.clip(f'<path d="{arch}"/>')
    view = [f'<rect x="130" y="60" width="340" height="300" fill="{D.lin([(0, "#7E909E"), (0.6, "#A8B2B6"), (1, "#C2C2BA")])}"/>',
            cloud_puffs(D, 230, 150, 200, 4, col="#93A2AE", shade="#6E7E8C", lit="#B4BEC4"),
            f'<polygon points="{P(rough([(130, 282), (220, 270), (320, 280), (470, 268)], 4, amp=4) + [(470, 360), (130, 360)])}" fill="#8A9294"/>']
    rnd = random.Random(6)
    for x in range(130, 480, 18):
        view.append(foliage(D, x + rnd.uniform(-5, 5), 296 + rnd.uniform(-8, 8), rnd.uniform(16, 24), rnd.uniform(14, 20), (["#7A5A52", "#6E5A56"], ["#A8705A", "#B08A64", "#9A6A58"], ["#C9A274", "#C49A70"]), x, n=30, size=(4, 7), light=(-0.6, -0.8)))
    # neighbour's roof with a warm lit window
    view.append('<polygon points="360,300 404,268 448,300" fill="#5A4048"/><rect x="368" y="300" width="72" height="50" fill="#8A7468"/>'
                '<rect x="392" y="312" width="22" height="20" fill="#FFC870"/>' + glow(D, 403, 322, 40, "#FFC870", 0.5))
    view.append(f'<rect x="130" y="320" width="340" height="40" fill="{D.lin([(0, "#C2C2BA", 0), (1, "#C2C2BA", 0.6)])}"/>')
    view.append('<g stroke="#E8F0F4" stroke-width="1.4" opacity="0.4" stroke-linecap="round">' + "".join(
        f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x - 7:.0f}" y2="{y + 26:.0f}"/>' for x, y in [(rnd.uniform(130, 480), rnd.uniform(60, 350)) for _ in range(120)]) + "</g>")
    drops = []
    for _ in range(46):
        x, y, r = rnd.uniform(140, 460), rnd.uniform(80, 340), rnd.uniform(2, 5.5)
        drops.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#DDE6EA" opacity="0.35"/><circle cx="{x + r * 0.2:.1f}" cy="{y + r * 0.25:.1f}" r="{r * 0.75:.1f}" fill="#5E6E78" opacity="0.35"/>'
                     f'<circle cx="{x - r * 0.35:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.3:.1f}" fill="#FFFFFF" opacity="0.9"/>')
        if r > 4.4:
            drops.append(f'<path d="M {x:.1f} {y - r:.1f} q -2 -14 1 -30" stroke="#E8F0F4" stroke-width="{r * 0.5:.1f}" fill="none" opacity="0.3" stroke-linecap="round"/>')
    view.append("".join(drops))
    out.append(f'<g {gid}>' + "".join(view) + "</g>")
    frame = D.lin([(0, "#F6EDE0"), (1, "#D8C8B0")], 0, 0, 1, 0)
    out.append(f'<path d="M 120 352 L 120 240 A 180 180 0 0 1 480 240 L 480 352 L 464 352 L 464 240 A 164 164 0 0 0 136 240 L 136 352 Z" fill="{frame}"/>')
    out.append('<g stroke="#EADCC6" stroke-width="9"><line x1="300" y1="76" x2="300" y2="344"/><line x1="136" y1="240" x2="464" y2="240"/></g>')
    out.append('<g stroke="#B8A890" stroke-width="2" opacity="0.7"><line x1="304" y1="80" x2="304" y2="344"/><line x1="136" y1="244" x2="464" y2="244"/></g>')
    # curtains with soft folds, tied back
    for sgn in (-1, 1):
        x0 = 0 if sgn < 0 else 600
        pts = [(x0 + sgn * 10, -10), (x0 - sgn * 128, -10), (x0 - sgn * 118, 120), (x0 - sgn * 70, 300), (x0 - sgn * 104, 420), (x0 + sgn * 10, 420)]
        cid = D.clip(f'<polygon points="{P(pts)}"/>')
        folds = "".join(f'<rect x="{x:.0f}" y="-10" width="14" height="440" fill="{D.lin([(0, "#000", 0), (0.5, "#2A1404", 0.32), (1, "#000", 0)], 0, 0, 1, 0, key="fold")}"/>' for x in range(-10 if sgn < 0 else 470, 140 if sgn < 0 else 620, 26))
        out.append(f'<polygon points="{P(pts)}" fill="#D49A3A"/><g {cid}>{folds}<rect x="{0 if sgn < 0 else 460}" y="-10" width="140" height="440" fill="{D.lin([(0, "#FFF0C0", 0.2), (1, "#000", 0.2)])}"/></g>')
        out.append(f'<path d="M {x0 + sgn * 6} 296 Q {x0 - sgn * 40} 286 {x0 - sgn * 76} 304" stroke="#6E2A18" stroke-width="7" fill="none" stroke-linecap="round"/><circle cx="{x0 - sgn * 76}" cy="304" r="6" fill="#E9B54A"/>')
    # sill, cushion, pillow, books and tea
    out.append(f'<rect x="104" y="344" width="392" height="16" rx="3" fill="{D.lin([(0, "#FBF3E6"), (1, "#C9B79C")])}"/>')
    cush = D.lin([(0, "#C2603A"), (0.5, "#A8482A"), (1, "#6E2A16")])
    out.append(f'<path d="M 60 362 L 540 362 Q 552 362 552 380 L 552 408 L 48 408 L 48 380 Q 48 362 60 362 Z" fill="{cush}"/>')
    out.append('<path d="M 52 372 L 548 372" stroke="#F2C08A" stroke-width="2" opacity="0.4"/>')
    # plaid pillow leaning in the corner
    pil = "M 122 380 Q 140 336 126 290 Q 176 304 228 284 Q 214 332 236 378 Q 180 366 122 380 Z"
    pid = D.clip(f'<path d="{pil}"/>')
    plaid = (f'<rect x="120" y="280" width="120" height="110" fill="#5E6B34"/>' + "".join(f'<rect x="{x}" y="280" width="12" height="110" fill="#E9C46A" opacity="0.45"/>' for x in (134, 170, 206))
             + "".join(f'<rect x="120" y="{y}" width="120" height="12" fill="#E9C46A" opacity="0.45"/>' for y in (296, 330, 362))
             + "".join(f'<rect x="{x}" y="280" width="3" height="110" fill="#F6EDE0" opacity="0.6"/>' for x in (152, 188, 224))
             + f'<rect x="120" y="280" width="120" height="110" fill="{D.rad([(0, "#FFF", 0.15), (1, "#000", 0.35)], cx=0.35, cy=0.3, r=0.75)}"/>')
    out.append(f'<g {pid}>{plaid}</g>')
    out.append(f'<g transform="rotate(-4 300 350)">{book(D, 236, 344, 150, 18, "#3E5A6A", "#1E2E38")}</g>')
    out.append(f'<path d="M 244 344 Q 280 330 312 340 Q 344 330 380 344 L 380 348 Q 344 336 312 346 Q 280 336 244 348 Z" fill="#F6EDE0"/>'
               '<path d="M 312 340 L 312 346" stroke="#B8A890" stroke-width="1.5"/>'
               '<g stroke="#B8A890" stroke-width="1" opacity="0.8"><path d="M 256 340 q 24 -8 48 -2"/><path d="M 320 338 q 24 -6 50 2"/></g>')
    out.append(mug(D, 446, 316, 52, 48, glaze=("#F6EDE0", "#E2CBAA", "#9A7E5E"), liquid="#8A5A2E"))
    out.append('<path d="M 452 316 L 456 358" stroke="#6E8A4A" stroke-width="1.4"/><rect x="451" y="352" width="10" height="10" fill="#E9C46A" transform="rotate(8 456 357)"/>')
    out.append(steam(D, 446, 304, 60, "#F6EDE0", n=2, gap=18, sw=4, op=0.6, seed=3))
    out.append(maple(D, 190, 348, 14, L_GOLD, -70, shade=0.15))
    # window-seat panel with the words
    out.append(f'<rect x="-10" y="408" width="620" height="200" fill="{D.lin([(0, "#5A3A2A"), (1, "#3A2418")])}"/>')
    out.append('<rect x="-10" y="408" width="620" height="10" fill="#1E120A" opacity="0.5"/>')
    out.append(word(300, 486, "rainy days", SERIF_IT, 82, "#FBEBD2", max_w=420))
    out.append(word(300, 538, "& GOOD BOOKS", JOS, 32, "#E9B54A", max_w=380, ls=9))
    return D.render(out)


# ================================================================ 13. farmers market stand
def mum(D, cx, cy, r, cols, seed):
    rnd = random.Random(seed)
    out = [f'<ellipse cx="{cx}" cy="{cy + r * 0.25:.1f}" rx="{r * 1.02:.1f}" ry="{r * 0.8:.1f}" fill="#3E4A26"/>']
    heads = []
    for _ in range(int(r * 1.3)):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.random() ** 0.55 * r * 0.92
        heads.append((cx + math.cos(a) * d, cy + math.sin(a) * d * 0.85, math.cos(a) * -0.6 + math.sin(a) * -0.8))
    for x, y, lit in sorted(heads, key=lambda h: h[1]):
        base = cols[2] if lit > 0.3 else (cols[1] if lit > -0.4 else cols[0])
        hr = rnd.uniform(5.5, 8)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{hr:.1f}" fill="{cols[0]}"/>'
                   f'<circle cx="{x:.1f}" cy="{y - 0.6:.1f}" r="{hr * 0.68:.1f}" fill="none" stroke="{base}" stroke-width="{hr * 0.62:.1f}" stroke-dasharray="1.6 1.1"/>'
                   f'<circle cx="{x:.1f}" cy="{y - 0.6:.1f}" r="{hr * 0.28:.1f}" fill="{base}"/><circle cx="{x:.1f}" cy="{y - 0.6:.1f}" r="1.3" fill="#E9C46A"/>')
    return "".join(out)


@design("farmers-market")
def farmers_market():
    D = Doc("fm")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#9EBCC6"), (0.45, "#E9E2CE"), (1, "#F2DEC0")])}"/>']
    out.append(cloud_puffs(D, 110, 70, 140, 8, shade="#9AAABC") + cloud_puffs(D, 500, 52, 120, 9, shade="#9AAABC"))
    # street trees behind the stall
    for x, cy, pal in ((40, 250, 0), (150, 220, 1), (300, 232, 2), (452, 222, 0), (566, 246, 1)):
        p = [(["#9A3424", "#7A2A22"], ["#C9542A", "#D0602E"], ["#F08A3A", "#F2A24A"]),
             (["#A8761E", "#8E6A1E"], ["#D8A23A", "#E0AE40"], ["#F6D066", "#FBE08A"]),
             (["#5E6A2E", "#4E5A28"], ["#8A9640", "#9AA04A"], ["#C9C060", "#D8C66A"])][pal]
        out.append(f'<rect x="{x - 5}" y="{cy}" width="10" height="{460 - cy}" fill="#5A4034"/>')
        out.append(foliage(D, x, cy, 70, 56, p, x + 1, n=170, size=(5, 10), light=(-0.7, -0.7), leafy=True))
    out.append(f'<rect x="0" y="150" width="600" height="320" fill="{D.lin([(0, "#E9E2CE", 0), (1, "#E9E2CE", 0.35)])}"/>')
    # brick pavement
    out.append(f'<rect x="-10" y="462" width="620" height="150" fill="{D.lin([(0, "#C9B39A"), (1, "#9A8270")])}"/>')
    pav = []
    for i, y in enumerate(range(466, 610, 16)):
        off = 18 if i % 2 else 0
        pav.append(f'<line x1="-10" y1="{y}" x2="610" y2="{y}"/>' + "".join(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + 16}"/>' for x in range(-10 + off, 610, 36)))
    out.append('<g stroke="#8A7262" stroke-width="1.5" opacity="0.55">' + "".join(pav) + "</g>")
    # the stall: back wall, shelves with jars, posts
    out.append(f'<rect x="92" y="220" width="416" height="180" fill="{D.lin([(0, "#3A2418"), (1, "#5A3A26")])}"/>')
    out.append(wood_grain(4, (96, 226, 504, 396), "#2A1810", n=16, op=0.5, sw=1.4))
    out.append('<rect x="96" y="300" width="408" height="7" fill="#8A5A34"/>')
    for i, x in enumerate(range(118, 490, 30)):
        if 210 < x < 300:
            continue
        honey = i % 3 != 2
        body = "#E9A23A" if honey else "#9A3A22"
        out.append(f'<rect x="{x}" y="270" width="22" height="30" rx="4" fill="{body}"/><rect x="{x - 1}" y="264" width="24" height="7" rx="2" fill="{"#F2E6D0" if honey else "#E9C46A"}"/>'
                   f'<rect x="{x + 3}" y="276" width="4" height="20" rx="2" fill="#FFF3C8" opacity="0.6"/><rect x="{x + 2}" y="283" width="18" height="9" fill="#F6EDE0" opacity="0.8"/>')
    # dried corn hanging under the awning
    for k, (x, r_) in enumerate(((236, -8), (256, 2), (276, 10))):
        out.append(f'<g transform="rotate({r_} {x} 236)"><line x1="{x}" y1="230" x2="{x}" y2="246" stroke="#C9A060" stroke-width="2"/>'
                   f'<ellipse cx="{x}" cy="276" rx="9" ry="30" fill="{["#9A3A2A", "#C98A2A", "#7A3A4A"][k]}"/>'
                   + "".join(f'<circle cx="{x + dx}" cy="{y}" r="2.2" fill="{["#E9B54A", "#7A2A22", "#F2D27A", "#5A2A3A"][(dx + y) % 4]}"/>' for dx in (-5, 0, 5) for y in range(254, 300, 6)) +
                   f'<path d="M {x} 246 q -18 6 -16 26 q 8 -14 16 -20 q 8 6 14 20 q 2 -20 -14 -26" fill="#E6D49A"/></g>')
    wood = D.lin([(0, "#8A5A34"), (0.3, "#B07A48"), (1, "#5A3A20")], 0, 0, 1, 0)
    for x in (80, 506):
        out.append(f'<rect x="{x}" y="140" width="14" height="330" fill="{wood}"/>')
    # sign board
    out.append(shadow(D, 300, 162, 230, 12, strength=0.4))
    out.append(f'<rect x="70" y="62" width="460" height="98" rx="6" fill="{D.lin([(0, "#4A6A42"), (1, "#2E4A2C")])}"/>')
    out.append(wood_grain(9, (76, 66, 524, 156), "#1E3A1E", n=10, op=0.5, sw=1.2))
    out.append('<g stroke="#1E301C" stroke-width="2" opacity="0.6"><line x1="72" y1="94" x2="528" y2="94"/><line x1="72" y1="128" x2="528" y2="128"/></g>')
    out.append('<rect x="80" y="72" width="440" height="78" rx="4" fill="none" stroke="#F2E6D0" stroke-width="2.5" opacity="0.85"/>')
    out.append("".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#C9B48A"/>' for x in (88, 512) for y in (80, 142)))
    out.append(word(300, 124, "FARMERS MARKET", ANTON, 58, "#F6EDE0", max_w=400, ls=4, sh="#16281A", off=(2, 3)))
    out.append(word(300, 147, "FRESH · LOCAL · SEASONAL", MONO, 18, "#F2C25A", max_w=400, ls=3))
    # striped awning with scalloped edge
    stripes = []
    for i in range(12):
        xt0, xt1 = 70 + i * 460 / 12, 70 + (i + 1) * 460 / 12
        xb0, xb1 = 50 + i * 500 / 12, 50 + (i + 1) * 500 / 12
        col = "#B4532A" if i % 2 == 0 else "#F4E8D4"
        stripes.append(f'<polygon points="{P([(xt0, 160), (xt1, 160), (xb1, 226), (xb0, 226)])}" fill="{col}"/>'
                       f'<path d="M {xb0:.1f} 226 A {(xb1 - xb0) / 2:.1f} {(xb1 - xb0) / 2.2:.1f} 0 0 0 {xb1:.1f} 226 Z" fill="{col}"/>')
    out.append("".join(stripes))
    out.append(f'<polygon points="70,160 530,160 550,226 50,226" fill="{D.lin([(0, "#2A1404", 0.4), (0.4, "#000", 0), (1, "#2A1404", 0.15)])}"/>')
    out.append(f'<rect x="50" y="226" width="500" height="22" fill="{D.lin([(0, "#1A0A04", 0.3), (1, "#1A0A04", 0)])}"/>')
    # counter of crates with produce heaped on top
    def apples_heap(x0, x1, top):
        r = random.Random(3)
        return "".join(apple(D, x0 + 16 + i * (x1 - x0 - 32) / 4 + (row * 10), top - row * 15 + r.uniform(-2, 2), 15 - row, seed=row * 7 + i, leaf=(row == 1 and i == 1), rot_=r.uniform(-25, 25))
                       for row in (0, 1) for i in range(5 - row * 2))
    def pumpkins_heap(x0, x1, top):
        return (pumpkin(D, x0 + 30, top - 8, 54, 40, PK_ORANGE, cast=0, curl=False) + pumpkin(D, x1 - 30, top - 6, 50, 38, PK_CREAM, cast=0, curl=False)
                + pumpkin(D, (x0 + x1) / 2, top - 22, 60, 44, PK_DEEP, cast=0))
    def gourds_heap(x0, x1, top):
        return (squash(D, x0 + 30, top - 16, 34, -60) + pumpkin(D, x1 - 34, top - 8, 44, 32, PK_GREEN, warts=8, seed=2, cast=0, curl=False)
                + pumpkin(D, (x0 + x1) / 2 + 6, top - 4, 40, 30, PK_GOLD, stripes="#7E8A3A", lobes=3, cast=0, curl=False))
    out.append(shadow(D, 300, 470, 230, 14, strength=0.45))
    out.append(crate(D, 100, 384, 130, 84, apples_heap))
    out.append(crate(D, 236, 384, 128, 84, pumpkins_heap))
    out.append(crate(D, 370, 384, 130, 84, gourds_heap))
    for x, price in ((164, "$3"), (300, "$5"), (434, "$4")):
        out.append(f'<g transform="rotate(-6 {x} 400)"><path d="M {x - 22} 390 L {x + 18} 390 L {x + 26} 401 L {x + 18} 412 L {x - 22} 412 Z" fill="#E8D4AE"/><circle cx="{x + 17}" cy="401" r="2.4" fill="#5A3A20"/>'
                   f'<text x="{x - 3}" y="408" text-anchor="middle" {JOS} font-size="18" fill="#3A2418">{price}</text></g>')
    # potted mums at the front corners, a pumpkin pair on the bricks
    for cx, cols, sd in ((106, ["#9A3A22", "#D0602A", "#F29A4A"], 1), (494, ["#5A2440", "#8A3A5E", "#B8648A"], 2)):
        out.append(shadow(D, cx + 6, 560, 56, 8, strength=0.5))
        out.append(f'<path d="M {cx - 40} 500 L {cx + 40} 500 L {cx + 32} 560 L {cx - 32} 560 Z" fill="{cyl(D, "#E0885A", "#C2603A", "#7A3418", key="pot")}"/><rect x="{cx - 44}" y="494" width="88" height="14" rx="3" fill="#B4532A"/>')
        out.append(mum(D, cx, 470, 46, cols, sd))
    out.append(mirror(pumpkin(D, 250, 534, 96, 66, PK_ORANGE, leaf=L_OLIVE), 250) + pumpkin(D, 352, 544, 72, 50, PK_GOLD))
    return D.render(out)


# ================================================================ 14. leaf me alone (sleeping fox)
def leaf_pile(D, cx, cy, w, h, seed, n=60, pals=(L_RED, L_ORANGE, L_GOLD, L_BROWN, L_PLUM, L_OLIVE), size=(14, 24)):
    rnd = random.Random(seed)
    items = []
    for _ in range(n):
        a = rnd.uniform(0, math.pi)
        d = rnd.random() ** 0.6
        x = cx + math.cos(a) * d * w / 2 * (1 if rnd.random() < 0.5 else -1)
        y = cy - math.sin(a) * d * h * 0.7 + rnd.uniform(-4, h * 0.3)
        items.append((y, x, rnd.choice(("maple", "maple", "oak", "slim")), rnd.uniform(*size), rnd.choice(pals), rnd.uniform(-180, 180)))
    return "".join(leaf_any(D, k, x, y, sz, pal, r) for y, x, k, sz, pal, r in sorted(items))


@design("leaf-me-alone")
def leaf_me_alone():
    D = Doc("lma")
    out = [paper(D, "#D4D6B8", "#9EA584", 41, ink="#2E3418", op=0.1, wash=["#E9E2C0", "#7E8A5E"])]
    out.append(word(300, 132, "LEAF ME", JOS, 70, "#3E2A1C", max_w=380, ls=12))
    out.append(word(300, 238, "alone", SERIF_IT, 118, "#B4532A", max_w=360, sh="#7A8460", off=(0, 5), sh_op=0.5))
    out.append('<g transform="translate(300 520) scale(1.13) translate(-300 -520)">')
    out.append(shadow(D, 300, 520, 250, 26, "#2E3418", 0.45))
    out.append(leaf_pile(D, 300, 520, 450, 70, 5, n=70))
    # the fox, curled up asleep
    fur = D.rad([(0, "#F7B061"), (0.5, "#E27A34"), (1, "#A8441A")], cx=0.4, cy=0.25, r=0.8)
    body = "M 206 428 C 206 362 296 336 376 348 C 456 360 474 432 446 466 C 410 502 268 504 228 486 C 210 476 206 452 206 428 Z"
    out.append(f'<path d="{body}" fill="{fur}"/>')
    bid = D.clip(f'<path d="{body}"/>')
    rnd = random.Random(3)
    strokes = "".join(f'<path d="M {x:.0f} {y:.0f} q {rnd.uniform(4, 9):.1f} {rnd.uniform(-2, 3):.1f} {rnd.uniform(10, 16):.1f} {rnd.uniform(-1, 5):.1f}"/>'
                      for x, y in [(rnd.uniform(220, 450), rnd.uniform(350, 490)) for _ in range(70)])
    out.append(f'<g {bid}><g fill="none" stroke="#FFD8A0" stroke-width="2" stroke-linecap="round" opacity="0.45">{strokes}</g>'
               f'<path d="M 380 356 C 440 370 452 430 420 470" stroke="#A8441A" stroke-width="5" fill="none" opacity="0.5"/>'
               f'<rect x="200" y="440" width="260" height="70" fill="{D.lin([(0, "#7A2A0A", 0), (1, "#7A2A0A", 0.45)])}"/></g>')
    out.append('<path d="M 250 360 C 300 342 360 340 400 352" stroke="#FFE2B0" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.6"/>')
    # a little black paw tucked under the chin
    out.append('<ellipse cx="238" cy="480" rx="20" ry="10" fill="#2E1E16"/><ellipse cx="232" cy="477" rx="8" ry="3" fill="#5A4030"/>')
    # bushy tail wrapping round the front, white tip under the nose
    tail = "M 446 452 C 476 482 446 520 382 522 C 300 526 216 516 160 494 C 136 484 138 464 160 462 C 226 474 316 482 380 474 C 420 470 438 462 446 452 Z"
    tid = D.clip(f'<path d="{tail}"/>')
    tg = D.lin([(0, "#F2A050"), (0.55, "#DA6E2C"), (1, "#9A3E16")])
    tip = D.rad([(0, "#FFFBF2"), (0.55, "#F6EDE0"), (1, "#F6EDE0", 0)], cx=0.2, cy=0.5, r=0.6)
    ts = "".join(f'<path d="M {x:.0f} {y:.0f} q {rnd.uniform(6, 12):.1f} {rnd.uniform(-3, 3):.1f} {rnd.uniform(14, 22):.1f} {rnd.uniform(-2, 4):.1f}"/>'
                 for x, y in [(rnd.uniform(150, 450), rnd.uniform(462, 520)) for _ in range(60)])
    out.append(f'<path d="{tail}" fill="{tg}"/><g {tid}><g fill="none" stroke="#FFD8A0" stroke-width="2" stroke-linecap="round" opacity="0.4">{ts}</g>'
               f'<ellipse cx="160" cy="486" rx="74" ry="44" fill="{tip}"/>'
               f'<path d="M 150 492 C 240 512 340 512 440 488" stroke="#7A2A0A" stroke-width="4" fill="none" opacity="0.35"/></g>')
    # head resting on the tail
    head = "M 254 402 C 250 372 222 358 196 362 C 172 366 156 382 148 402 L 120 436 C 114 446 122 454 132 452 L 170 454 C 200 464 240 452 254 424 Z"
    hg = D.rad([(0, "#F8B866"), (0.6, "#E57C36"), (1, "#B0481C")], cx=0.45, cy=0.3, r=0.75)
    ear = D.lin([(0, "#2E1E16"), (0.32, "#2E1E16"), (0.36, "#D86A2C"), (1, "#E57C36")])
    out.append(f'<polygon points="176,374 158,328 206,364" fill="{ear}"/><polygon points="170,366 162,342 188,364" fill="#F6D8B0" opacity="0.8"/>')
    out.append(f'<path d="{head}" fill="{hg}"/>')
    out.append(f'<polygon points="210,368 226,322 244,382" fill="{ear}"/><polygon points="216,364 226,336 236,372" fill="#F6D8B0" opacity="0.8"/>')
    out.append('<path d="M 122 450 L 170 454 C 196 462 222 452 238 436 C 214 440 196 432 180 424 C 160 430 140 436 122 446 Z" fill="#FBF3E6"/>')
    out.append('<path d="M 236 406 C 244 420 252 418 254 412" stroke="#FBF3E6" stroke-width="6" fill="none" stroke-linecap="round" opacity="0.7"/>')
    out.append('<ellipse cx="122" cy="442" rx="7" ry="5.5" fill="#2A1A14"/><ellipse cx="120" cy="440" rx="2.4" ry="1.6" fill="#FFFFFF" opacity="0.6"/>')
    out.append('<path d="M 166 408 Q 180 418 196 410" stroke="#2A1A14" stroke-width="3.4" fill="none" stroke-linecap="round"/>'
               '<path d="M 170 412 l -3 5 M 178 415 l -1 6 M 186 415 l 1 6" stroke="#2A1A14" stroke-width="2" stroke-linecap="round"/>')
    out.append('<path d="M 138 428 q 12 6 26 4" stroke="#B0481C" stroke-width="1.6" fill="none" opacity="0.6"/>')
    # a leaf landed on the sleeper, more scattered on top of the pile
    out.append(maple(D, 340, 352, 26, L_GOLD, 24, spots=2, seed=9))
    out.append(leaf_any(D, "oak", 442, 500, 22, L_RED, -70) + leaf_any(D, "maple", 176, 512, 20, L_PLUM, 140) + leaf_any(D, "slim", 520, 496, 18, L_GOLD, 70))
    out.append(f'<g {SERIF_IT} fill="#4E5636"><text x="128" y="366" font-size="34">z</text><text x="112" y="332" font-size="28">z</text><text x="100" y="302" font-size="22">z</text></g>')
    out.append("</g>")
    out.append(falling(D, [("maple", 498, 314, 18, L_ORANGE, 30), ("slim", 92, 236, 16, L_GOLD, -30), ("oak", 510, 200, 18, L_BROWN, 20)]))
    return D.render(out)


# ================================================================ 15. whooo loves fall? (owl on a branch, harvest moon)
@design("whooo-loves-fall")
def whooo_loves_fall():
    D = Doc("wlf")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#232445"), (0.6, "#43305A"), (1, "#5E3A52")])}"/>']
    rnd = random.Random(2)
    out.append('<g fill="#F6EDE0">' + "".join(f'<circle cx="{rnd.uniform(10, 590):.0f}" cy="{rnd.uniform(10, 420):.0f}" r="{rnd.uniform(0.7, 1.9):.1f}" opacity="{rnd.uniform(0.3, 0.9):.2f}"/>' for _ in range(70)) + "</g>")
    out.append(glow(D, 300, 262, 250, "#F6D68A", 0.4))
    moon = D.rad([(0, "#FFF6D8"), (0.7, "#F8DFA0"), (1, "#E9BE6A")], cx=0.42, cy=0.38, r=0.65)
    out.append(f'<circle cx="300" cy="262" r="136" fill="{moon}"/>')
    out.append('<g fill="#E2B866" opacity="0.45"><circle cx="246" cy="214" r="18"/><circle cx="352" cy="300" r="24"/><circle cx="330" cy="200" r="10"/><circle cx="236" cy="320" r="12"/></g>')
    out.append(word(300, 124, "whooo", SERIF_IT, 92, "#FBEBD2", max_w=320))
    # the owl
    body = "M 300 170 C 372 170 404 246 400 318 C 396 380 352 410 300 410 C 248 410 204 380 200 318 C 196 246 228 170 300 170 Z"
    bg_ = D.rad([(0, "#A8784E"), (0.55, "#7A5232"), (1, "#4A2E1A")], cx=0.42, cy=0.3, r=0.8)
    out.append(f'<path d="{body}" fill="{bg_}"/>')
    # wings with layered feathers
    for sgn in (-1, 1):
        w = (f"M {300 + sgn * 70} 250 C {300 + sgn * 112} 270 {300 + sgn * 116} 350 {300 + sgn * 96} 404 "
             f"L {300 + sgn * 82} 392 L {300 + sgn * 76} 410 L {300 + sgn * 64} 394 C {300 + sgn * 70} 330 {300 + sgn * 66} 290 {300 + sgn * 70} 250 Z")
        out.append(f'<path d="{w}" fill="{D.lin([(0, "#6E4628"), (1, "#3E2614")])}"/>')
        out.append(f'<g fill="none" stroke="#C9A070" stroke-width="2" opacity="0.6">' + "".join(
            f'<path d="M {300 + sgn * 74} {y} q {sgn * 14} 8 {sgn * 28} 2"/>' for y in range(272, 392, 16)) + "</g>")
    # belly with scalloped feathers
    belly = "M 300 262 C 344 262 362 312 356 352 C 350 388 326 404 300 404 C 274 404 250 388 244 352 C 238 312 256 262 300 262 Z"
    bid = D.clip(f'<path d="{belly}"/>')
    sc = []
    for i, y in enumerate(range(274, 404, 13)):
        for x in range(236 + (7 if i % 2 else 0), 366, 14):
            sc.append(f'<path d="M {x - 6} {y} q 6 8 12 0"/>')
    out.append(f'<path d="{belly}" fill="{D.rad([(0, "#F6E2BE"), (1, "#C9A47A")], cx=0.45, cy=0.35, r=0.7)}"/>'
               f'<g {bid}><g fill="none" stroke="#8A5E3A" stroke-width="2.2" stroke-linecap="round" opacity="0.75">{"".join(sc)}</g></g>')
    # ear tufts and facial disc
    for sgn in (-1, 1):
        out.append(f'<path d="M {300 + sgn * 34} 192 L {300 + sgn * 70} 138 L {300 + sgn * 64} 196 Z" fill="#5A3A22"/><path d="M {300 + sgn * 44} 188 L {300 + sgn * 66} 150 L {300 + sgn * 62} 190 Z" fill="#8A6040"/>')
    disc = D.rad([(0, "#F2DDB8"), (0.75, "#D8B488"), (1, "#9A7048")], cx=0.5, cy=0.45, r=0.6)
    for sgn in (-1, 1):
        out.append(f'<circle cx="{300 + sgn * 36}" cy="232" r="44" fill="{disc}"/>')
    out.append('<g fill="none" stroke="#B08A60" stroke-width="1.6" opacity="0.6">' + "".join(
        f'<circle cx="{300 + sgn * 36}" cy="232" r="{r}"/>' for sgn in (-1, 1) for r in (34, 40)) + "</g>")
    iris = D.rad([(0, "#FFE08A"), (0.6, "#F2A630"), (1, "#B86A14")], cx=0.45, cy=0.4, r=0.6)
    for sgn in (-1, 1):
        ex = 300 + sgn * 36
        out.append(f'<circle cx="{ex}" cy="232" r="26" fill="#2A1A10"/><circle cx="{ex}" cy="232" r="21" fill="{iris}"/><circle cx="{ex}" cy="233" r="11" fill="#140A06"/>'
                   f'<circle cx="{ex - 6}" cy="226" r="5" fill="#FFFFFF"/><circle cx="{ex + 6}" cy="240" r="2.2" fill="#FFFFFF" opacity="0.7"/>'
                   f'<path d="M {ex - 26} 218 Q {ex} 204 {ex + 26} 218" stroke="#4A2E1A" stroke-width="4" fill="none" stroke-linecap="round"/>')
    out.append('<path d="M 290 252 L 310 252 L 300 274 Z" fill="#E2A43A"/><path d="M 300 252 L 310 252 L 300 274 Z" fill="#B07818"/>')
    # branch with oak leaves and acorns, talons gripping
    br = D.lin([(0, "#7A5236"), (1, "#3E2616")])
    out.append(f'<path d="M -12 418 C 120 398 220 404 300 404 C 400 404 480 394 612 372 L 612 392 C 480 414 400 424 300 424 C 220 424 120 420 -12 438 Z" fill="{br}"/>')
    out.append('<path d="M 40 414 C 140 400 240 402 300 402 C 400 402 470 394 560 380" stroke="#B08A60" stroke-width="2" fill="none" opacity="0.5"/>')
    for sgn in (-1, 1):
        for dx in (-12, 0, 12):
            out.append(f'<path d="M {300 + sgn * 34 + dx} 400 q 2 10 -2 16" stroke="#C99A3A" stroke-width="5" fill="none" stroke-linecap="round"/>')
    out.append('<path d="M 470 392 q 20 10 40 30" stroke="#4A2E1A" stroke-width="6" fill="none" stroke-linecap="round"/>'
               '<path d="M 120 412 q -20 14 -36 36" stroke="#4A2E1A" stroke-width="6" fill="none" stroke-linecap="round"/>')
    out.append(oak(D, 512, 442, 34, L_RED, 30) + oak(D, 80, 470, 32, L_GOLD, -24) + oak(D, 460, 432, 26, L_ORANGE, -12)
               + maple(D, 150, 444, 24, L_PLUM, 200, spots=2, seed=4))
    out.append(acorn(D, 506, 404, 20, 10) + acorn(D, 98, 428, 18, -14))
    out.append(word(300, 532, "LOVES FALL?", BEBAS, 86, "#F2B94A", max_w=440, ls=8, sh="#1A1530", off=(0, 5)))
    return D.render(out)


# ================================================================ 16. scarf season (a plaid scarf, knotted)
def plaid(D, base, a, b, line, key, rotate=0):
    inner = (f'<rect width="48" height="48" fill="{base}"/>'
             f'<rect x="8" width="14" height="48" fill="{a}" opacity="0.55"/><rect y="8" width="48" height="14" fill="{a}" opacity="0.55"/>'
             f'<rect x="30" width="5" height="48" fill="{b}" opacity="0.6"/><rect y="30" width="48" height="5" fill="{b}" opacity="0.6"/>'
             f'<rect x="40" width="2" height="48" fill="{line}"/><rect y="40" width="48" height="2" fill="{line}"/>')
    return D.pattern(48, 48, inner, key=key, transform=f"rotate({rotate})" if rotate else "")


@design("scarf-season")
def scarf_season():
    D = Doc("ss")
    out = [paper(D, "#FBF3E4", "#EAD6B8", 51, wash=["#E9A86A", "#C9B07A"])]
    out.append(word(300, 150, "SCARF", JOS, 116, "#3E2A1C", max_w=420, ls=16))
    out.append(word(300, 238, "season", SERIF_IT, 88, "#B4322A", max_w=340))
    pl = plaid(D, "#B4322A", "#2E3A4A", "#5E6B34", "#E9C46A", "pl0")
    pl2 = plaid(D, "#B4322A", "#2E3A4A", "#5E6B34", "#E9C46A", "pl1", rotate=-12)
    pl3 = plaid(D, "#B4322A", "#2E3A4A", "#5E6B34", "#E9C46A", "pl2", rotate=18)
    # back of the loop, in shadow
    back = "M 184 330 C 184 244 416 238 418 324 C 400 288 204 290 184 330 Z"
    out.append(f'<path d="{back}" fill="{pl}"/><path d="{back}" fill="#2A0A06" opacity="0.45"/>')
    out.append('<path d="M 208 290 C 260 262 350 258 400 280" stroke="#FFFFFF" stroke-width="3" fill="none" opacity="0.12"/>')
    # tails hanging from the knot
    t1 = "M 316 404 C 310 446 300 490 284 538 L 350 546 C 360 498 368 450 374 408 Z"
    t2 = "M 372 404 C 392 444 416 478 444 516 L 498 490 C 466 452 440 418 414 388 Z"
    for t, pat in ((t2, pl3), (t1, pl2)):
        cid = D.clip(f'<path d="{t}"/>')
        out.append(f'<path d="{t}" fill="{pat}"/><g {cid}><rect x="270" y="370" width="240" height="180" fill="{D.lin([(0, "#2A0A06", 0.35), (0.3, "#2A0A06", 0), (0.8, "#000", 0.05), (1, "#2A0A06", 0.25)], 0, 0, 1, 0, key="tl")}"/>'
                   f'<path d="M 300 390 C 344 430 344 480 330 540" stroke="#2A0A06" stroke-width="4" fill="none" opacity="0.2"/>'
                   f'<path d="M 400 390 C 430 440 460 470 480 500" stroke="#2A0A06" stroke-width="4" fill="none" opacity="0.2"/></g>')
    fr = []
    for i in range(15):
        x = 286 + i * 4.4
        fr.append(f'<path d="M {x:.1f} {537 + i * 0.65:.1f} q {-1 + i % 3:.1f} 12 {1:.1f} 22" />')
    for i in range(12):
        x0, y0 = 446 + i * 4.4, 515 - i * 2.2
        fr.append(f'<path d="M {x0:.1f} {y0:.1f} q 4 10 10 18"/>')
    out.append('<g fill="none" stroke="#9A2A22" stroke-width="3.2" stroke-linecap="round">' + "".join(fr) + "</g>")
    # front of the loop: a thick, soft cowl lit from above
    front = "M 184 330 C 170 404 258 436 314 432 C 382 430 434 392 418 324 C 404 364 360 378 302 380 C 240 382 196 366 184 330 Z"
    fid = D.clip(f'<path d="{front}"/>')
    out.append(f'<path d="{front}" fill="{pl}"/><g {fid}><rect x="100" y="320" width="400" height="110" fill="{D.lin([(0, "#FFFFFF", 0.2), (0.4, "#000", 0), (1, "#2A0A06", 0.45)])}"/>'
               '<g fill="none" stroke="#2A0A06" stroke-width="4" opacity="0.22"><path d="M 194 362 C 230 398 290 406 340 400"/><path d="M 226 404 C 270 422 330 422 380 404"/><path d="M 376 384 C 396 380 410 364 414 350"/></g>'
               '<g fill="none" stroke="#FFFFFF" stroke-width="3" opacity="0.18"><path d="M 196 350 C 240 380 330 388 400 370"/></g></g>')
    # knot
    knot = D.rad([(0, "#D84A3A"), (0.6, "#A8302A"), (1, "#6E1A16")], cx=0.4, cy=0.35, r=0.7)
    out.append(f'<ellipse cx="350" cy="404" rx="46" ry="32" fill="{pl}" transform="rotate(-14 350 404)"/>'
               f'<ellipse cx="350" cy="404" rx="46" ry="32" fill="{knot}" opacity="0.5" transform="rotate(-14 350 404)"/>'
               '<path d="M 310 400 C 332 386 360 388 386 400" stroke="#2A0A06" stroke-width="3.5" fill="none" opacity="0.35"/>'
               '<path d="M 318 392 C 336 382 360 382 378 390" stroke="#FFFFFF" stroke-width="3" fill="none" opacity="0.2"/>')
    # leaves and an acorn around it
    out.append(falling(D, [("maple", 108, 456, 28, L_GOLD, -24), ("oak", 160, 512, 26, L_BROWN, 40), ("maple", 520, 436, 22, L_ORANGE, 30),
                           ("slim", 236, 480, 20, L_OLIVE, -50), ("maple", 84, 252, 18, L_RED, 60), ("maple", 520, 236, 16, L_PLUM, -20)]))
    out.append(acorn(D, 218, 520, 20, 18))
    return D.render(out)


# ================================================================ 17. autumn leaves & pumpkins please (leaf wreath)
@design("autumn-leaves-pumpkins-please")
def autumn_leaves_pumpkins_please():
    D = Doc("alp")
    out = [paper(D, "#566238", "#2E3A1E", 61, ink="#0E1408", op=0.15, wash=["#6E7A44", "#1E2812"])]
    out.append(shadow(D, 300, 306, 200, 200, "#0E1408", 0.5))
    out.append(f'<circle cx="300" cy="300" r="178" fill="{D.rad([(0, "#FBF4E6"), (1, "#EADAC0")], r=0.6)}"/>')
    out.append(grain(62, "#5A3A22", 140, box=(140, 140, 460, 460), op=0.12))
    # twig ring
    out.append('<circle cx="300" cy="300" r="206" fill="none" stroke="#5A3A22" stroke-width="5"/><circle cx="300" cy="300" r="212" fill="none" stroke="#7A5232" stroke-width="2.5" stroke-dasharray="40 18"/>')
    rnd = random.Random(12)
    kinds = ["maple", "oak", "slim", "maple", "slim", "oak"]
    pals = [L_RED, L_GOLD, L_ORANGE, L_OLIVE, L_PLUM, L_BROWN, L_RED, L_GOLD]
    items = []
    for layer, (step, r0, sz) in enumerate(((11, 214, (30, 38)), (13, 200, (24, 32)))):
        for i in range(int(360 / step)):
            a = -90 + i * step + rnd.uniform(-3, 3) + layer * 6
            if 62 < a % 360 < 118:
                continue
            r = r0 + rnd.uniform(-8, 8)
            x, y = 300 + r * math.cos(math.radians(a)), 300 + r * math.sin(math.radians(a))
            items.append(leaf_any(D, kinds[(i + layer) % 6], x, y, rnd.uniform(*sz), pals[(i * 3 + layer) % 8], a + 90 + rnd.choice((-55, 55))))
    out.append("".join(items))
    # berries and acorns tucked between
    for i in range(10):
        a = math.radians(-80 + i * 36 + 14)
        x, y = 300 + 212 * math.cos(a), 300 + 212 * math.sin(a)
        if 250 < y and abs(x - 300) < 80:
            continue
        out.append("".join(f'<circle cx="{x + dx:.1f}" cy="{y + dy:.1f}" r="6" fill="#A8241E"/><circle cx="{x + dx - 2:.1f}" cy="{y + dy - 2:.1f}" r="1.8" fill="#FFFFFF" opacity="0.6"/>' for dx, dy in ((0, 0), (9, 5), (-6, 8))))
    for a in (-150, -30, 200):
        x, y = 300 + 214 * math.cos(math.radians(a)), 300 + 214 * math.sin(math.radians(a))
        out.append(acorn(D, x, y, 22, a + 90))
    # little pumpkins nestled at the bottom of the wreath
    out.append(pumpkin(D, 262, 500, 78, 56, PK_ORANGE, cast=0.35, leaf=L_OLIVE) + pumpkin(D, 340, 506, 64, 46, PK_CREAM, cast=0.35) + pumpkin(D, 300, 520, 48, 36, PK_GOLD, cast=0.3, curl=False))
    # type inside the wreath
    out.append(word(300, 248, "autumn leaves", SERIF_IT, 54, BROWN, max_w=300))
    out.append(word(300, 330, "& PUMPKINS", BEBAS, 82, "#B4532A", max_w=300, ls=6))
    out.append(word(300, 400, "please", SERIF_IT, 60, BROWN, max_w=260))
    return D.render(out)


# ================================================================ 18. give thanks (turkey in full display)
def feather(D, cx, cy, ang, L, w, col, dark, tipc="#F6EDE0", band="#3A2418"):
    g = D.lin([(0, tipc), (0.09, tipc), (0.11, band), (0.17, band), (0.2, col), (0.72, col), (1, dark)], key=("fth", col, dark, tipc))
    d = f"M 0 0 C {-w * 0.32:.1f} {-L * 0.3:.1f} {-w / 2:.1f} {-L * 0.78:.1f} 0 {-L:.1f} C {w / 2:.1f} {-L * 0.78:.1f} {w * 0.32:.1f} {-L * 0.3:.1f} 0 0 Z"
    return (f'<g transform="translate({cx} {cy}) rotate({ang + 90:.1f})"><path d="{d}" fill="{g}"/>'
            f'<path d="M 0 {-L * 0.05:.1f} L 0 {-L * 0.93:.1f}" stroke="{tipc}" stroke-width="1.6" opacity="0.5"/>'
            f'<path d="M {-w * 0.42:.1f} {-L * 0.62:.1f} Q 0 {-L * 0.56:.1f} {w * 0.42:.1f} {-L * 0.62:.1f}" stroke="{band}" stroke-width="2" fill="none" opacity="0.35"/></g>')


@design("give-thanks")
def give_thanks():
    D = Doc("gt")
    out = [paper(D, "#FBF2E2", "#EAD3B0", 71, wash=["#E9A86A", "#C9A06A"])]
    cx, cy = 300, 286
    out.append(glow(D, cx, cy, 250, "#FFE6B0", 0.6))
    out.append('<g transform="translate(300 60) scale(0.94) translate(-300 -60)">')
    cols = [("#B4532A", "#6E2A14"), ("#D9A23B", "#8A5A1A"), ("#8A5232", "#4A2A18")]
    n = 15
    for i in range(n):
        a = -174 + i * 168 / (n - 1)
        c, d = cols[i % 3]
        out.append(feather(D, cx, cy, a, 210, 50, c, d))
    for i in range(12):
        a = -166 + i * 152 / 11
        c, d = [("#C9762E", "#6E3414"), ("#7A3A1E", "#3A1A0E"), ("#E0B04A", "#8A5A1A")][i % 3]
        out.append(feather(D, cx, cy + 6, a, 150, 40, c, d, tipc="#E9C47A"))
    # body with bronze scalloped feathers
    body = f"M {cx} 232 C {cx + 70} 232 {cx + 88} 300 {cx + 82} 352 C {cx + 76} 404 {cx + 40} 424 {cx} 424 C {cx - 40} 424 {cx - 76} 404 {cx - 82} 352 C {cx - 88} 300 {cx - 70} 232 {cx} 232 Z"
    bid = D.clip(f'<path d="{body}"/>')
    sc = []
    for i, y in enumerate(range(250, 430, 14)):
        for x in range(cx - 92 + (8 if i % 2 else 0), cx + 96, 16):
            sc.append(f'<path d="M {x - 8} {y} q 8 11 16 0"/>')
    out.append(f'<path d="{body}" fill="{D.rad([(0, "#A8683E"), (0.6, "#6E3E22"), (1, "#3E2212")], cx=0.42, cy=0.3, r=0.8)}"/>'
               f'<g {bid}><g fill="none" stroke="#D8A060" stroke-width="2.4" stroke-linecap="round" opacity="0.6">{"".join(sc)}</g>'
               f'<rect x="{cx - 90}" y="230" width="180" height="200" fill="{D.lin([(0, "#000", 0), (0.6, "#000", 0), (1, "#1E0E04", 0.45)], 0, 0, 1, 0)}"/></g>')
    for sgn in (-1, 1):
        wing = f"M {cx + sgn * 56} 300 C {cx + sgn * 96} 320 {cx + sgn * 100} 380 {cx + sgn * 78} 412 C {cx + sgn * 66} 380 {cx + sgn * 58} 340 {cx + sgn * 56} 300 Z"
        out.append(f'<path d="{wing}" fill="#3E2416"/>' + "".join(
            f'<path d="M {cx + sgn * (64 + t * 10):.1f} {320 + t * 80:.1f} l {sgn * 18:.1f} {-6:.1f}" stroke="#F6EDE0" stroke-width="3" stroke-linecap="round" opacity="0.8"/>' for t in (0.1, 0.3, 0.5, 0.7)))
    # head and neck
    out.append(f'<path d="M {cx - 16} 250 Q {cx - 18} 228 {cx - 12} 214 L {cx + 12} 214 Q {cx + 18} 228 {cx + 16} 250 Z" fill="#B8C2D6"/>')
    out.append(f'<ellipse cx="{cx}" cy="200" rx="25" ry="28" fill="{D.rad([(0, "#E6ECF4"), (1, "#9AA8C0")], cx=0.4, cy=0.35, r=0.7)}"/>')
    out.append(f'<path d="M {cx - 6} 188 Q {cx - 18} 200 {cx - 14} 226 Q {cx - 8} 232 {cx - 6} 222 Q {cx - 8} 204 {cx + 2} 192 Z" fill="#C2302A"/>')
    out.append(f'<path d="M {cx + 2} 214 Q {cx + 14} 216 {cx + 14} 232 Q {cx + 12} 248 {cx + 2} 244 Q {cx - 4} 232 {cx + 2} 214 Z" fill="#D8403A"/><path d="M {cx + 6} 222 q 4 6 2 14" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.4"/>')
    out.append(f'<path d="M {cx - 6} 204 L {cx + 7} 204 L {cx} 218 Z" fill="#E9B54A"/>')
    for ex in (cx - 11, cx + 11):
        out.append(f'<circle cx="{ex}" cy="192" r="5" fill="#1E1410"/><circle cx="{ex - 1.6}" cy="190.2" r="1.7" fill="#FFFFFF"/>')
    out.append(f'<ellipse cx="{cx - 18}" cy="204" rx="5" ry="3" fill="#F2A6B4" opacity="0.7"/><ellipse cx="{cx + 18}" cy="204" rx="5" ry="3" fill="#F2A6B4" opacity="0.7"/>')
    # feet on a little patch of straw, wheat and a gourd beside
    out.append(shadow(D, cx, 438, 110, 10, strength=0.35))
    for fx in (cx - 18, cx + 18):
        out.append(f'<g stroke="#D88A5A" stroke-width="4" stroke-linecap="round" fill="none"><path d="M {fx} 420 L {fx} 436"/><path d="M {fx} 436 l -8 4 M {fx} 436 l 0 6 M {fx} 436 l 8 4"/></g>')
    out.append(wheat_stalk(D, 160, 440, 120, 372) + wheat_stalk(D, 168, 440, 150, 360) + wheat_stalk(D, 440, 440, 482, 372) + wheat_stalk(D, 432, 440, 452, 362))
    out.append(pumpkin(D, 200, 420, 58, 42, PK_ORANGE, cast=0.3) + pumpkin(D, 404, 424, 46, 34, PK_CREAM, cast=0.3, curl=False))
    out.append("</g>")
    out.append(word(300, 502, "give thanks", SERIF_IT, 80, BROWN, max_w=420))
    out.append(ruled(540, "HAPPY THANKSGIVING", "#B4532A", size=18, ls=4, line_w=30))
    return D.render(out)


# ================================================================ 19. gather together (flat-lay table)
def gingham(D, c, key):
    inner = (f'<rect width="16" height="16" fill="#FBF3E6"/><rect width="8" height="16" fill="{c}" opacity="0.55"/>'
             f'<rect width="16" height="8" fill="{c}" opacity="0.55"/>')
    return D.pattern(16, 16, inner, key=key)


def plate_top(D, cx, cy, r):
    g = D.rad([(0, "#FFFFFF"), (0.7, "#F6EFE4"), (1, "#C9BBA6")], cx=0.42, cy=0.38, r=0.6, key="plate")
    return (shadow(D, cx + 6, cy + 8, r * 1.05, r * 1.0, "#1E0E04", 0.45) + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{g}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * 0.68:.1f}" fill="none" stroke="#D8CCB8" stroke-width="2"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * 0.93:.1f}" fill="none" stroke="#B4532A" stroke-width="2" opacity="0.6"/>')


def pumpkin_top(D, cx, cy, r, pal=PK_ORANGE):
    light, base, dark = pal
    g = D.rad([(0, light), (0.6, base), (1, dark)], cx=0.42, cy=0.4, r=0.6, key=("pkt", pal))
    ribs = "".join(f'<path d="M {cx:.1f} {cy:.1f} Q {cx + r * 0.7 * math.cos(math.radians(a + 12)):.1f} {cy + r * 0.7 * math.sin(math.radians(a + 12)):.1f} {cx + r * math.cos(math.radians(a)):.1f} {cy + r * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 40))
    return (shadow(D, cx + 5, cy + 6, r * 1.05, r, "#1E0E04", 0.45) + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{g}"/>'
            f'<g fill="none" stroke="{dark}" stroke-width="{max(1.5, r * 0.05):.1f}" opacity="0.5">{ribs}</g>'
            f'<circle cx="{cx}" cy="{cy}" r="{r * 0.2:.1f}" fill="{dark}" opacity="0.6"/><circle cx="{cx}" cy="{cy}" r="{r * 0.12:.1f}" fill="#8A7A44"/>'
            f'<path d="M {cx:.1f} {cy:.1f} q {r * 0.3:.1f} {-r * 0.1:.1f} {r * 0.4:.1f} {r * 0.15:.1f}" stroke="#6E7A38" stroke-width="2" fill="none"/>')


@design("gather-together")
def gather_together():
    D = Doc("gth")
    out = []
    for i, x in enumerate(range(-20, 620, 76)):
        c = ["#8A5634", "#7E4C2E", "#94603A", "#80502E"][i % 4]
        out.append(f'<rect x="{x}" y="0" width="76" height="600" fill="{D.lin([(0, c), (1, "#5A3420")], key=("pl", c))}"/>')
        out.append(wood_grain(i * 3 + 1, (x + 6, 0, x + 70, 600), "#4A2A18", n=7, op=0.45, sw=1.5, vertical=True))
        out.append(f'<rect x="{x}" y="0" width="2.5" height="600" fill="#2A160C" opacity="0.7"/>')
    # linen runner with plaid borders
    linen = D.pattern(6, 6, '<rect width="6" height="6" fill="#F2E6D0"/><rect width="6" height="1.2" fill="#D8C8AE" opacity="0.6"/><rect width="1.2" height="6" fill="#E2D2B8" opacity="0.6"/>', key="linen")
    out.append(f'<rect x="-10" y="212" width="620" height="186" fill="#1E0E04" opacity="0.35" transform="translate(0 7)"/>')
    out.append(f'<rect x="-10" y="212" width="620" height="186" fill="{linen}"/>')
    for y0, sgn in ((222, 1), (388, -1)):
        out.append(f'<rect x="-10" y="{y0 - (12 if sgn < 0 else 0)}" width="620" height="12" fill="#B4532A" opacity="0.85"/>'
                   f'<rect x="-10" y="{y0 + sgn * 16 - (3 if sgn < 0 else 0)}" width="620" height="3" fill="#5E6B34"/>')
    out.append(word(300, 316, "gather", SERIF_IT, 104, BROWN, max_w=380))
    out.append(word(300, 366, "TOGETHER", JOS, 36, "#B4532A", max_w=380, ls=16))
    # place setting with a leaf on the plate
    out.append(f'<g transform="rotate(-12 140 128)"><rect x="96" y="70" width="96" height="110" rx="4" fill="#B4532A"/>'
               '<g stroke="#8A3A1A" stroke-width="1.4" opacity="0.6">' + "".join(f'<line x1="96" y1="{y}" x2="192" y2="{y}"/>' for y in range(78, 180, 9)) + "</g></g>")
    out.append(plate_top(D, 140, 126, 60))
    out.append(maple(D, 140, 124, 26, L_ORANGE, -20, spots=2, seed=4))
    steel = D.lin([(0, "#F2F2F2"), (0.5, "#B8BCC4"), (1, "#7E848E")], 0, 0, 1, 0, key="steel")
    out.append(f'<rect x="66" y="78" width="7" height="100" rx="3.5" fill="{steel}"/><path d="M 62 66 L 62 92 Q 69 100 76 92 L 76 66" stroke="{steel}" stroke-width="2.6" fill="none"/>'
               f'<path d="M 69 66 L 69 92" stroke="#B8BCC4" stroke-width="2"/>')
    out.append(f'<path d="M 214 70 Q 224 70 224 100 L 220 120 L 220 182 Q 216 186 212 182 L 212 76 Z" fill="{steel}"/>')
    # a basket of dinner rolls on a gingham cloth
    out.append(shadow(D, 324, 132, 70, 50, "#1E0E04", 0.45))
    out.append(f'<g transform="rotate(10 318 124)"><rect x="262" y="76" width="112" height="100" fill="{gingham(D, "#B4532A", "ghb")}"/></g>')
    out.append(f'<ellipse cx="318" cy="124" rx="62" ry="46" fill="{D.rad([(0, "#E2B276"), (1, "#8A5A2A")], r=0.6)}"/>'
               '<ellipse cx="318" cy="124" rx="62" ry="46" fill="none" stroke="#6E4422" stroke-width="7" stroke-dasharray="6 4"/>'
               '<ellipse cx="318" cy="124" rx="50" ry="35" fill="#5A3416"/>')
    roll = D.rad([(0, "#FBDDA0"), (0.55, "#E0A050"), (1, "#9A5A22")], cx=0.4, cy=0.35, r=0.65)
    for x, y, r_ in ((298, 112, -20), (336, 110, 15), (314, 140, 5), (346, 138, 30), (290, 140, -40)):
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="20" ry="15" transform="rotate({r_} {x} {y})" fill="{roll}"/>'
                   f'<path d="M {x - 8} {y - 4} q 8 -6 16 0" stroke="#FFF0C8" stroke-width="2.4" fill="none" opacity="0.6" transform="rotate({r_} {x} {y})"/>')
    # cranberry sauce in a bowl
    out.append(shadow(D, 474, 132, 56, 54, "#1E0E04", 0.45))
    out.append(f'<circle cx="468" cy="124" r="52" fill="{D.rad([(0, "#FFFBF2"), (1, "#C9B8A0")], cx=0.4, cy=0.35, r=0.65)}"/><circle cx="468" cy="124" r="40" fill="#7A1420"/>')
    rnd = random.Random(5)
    out.append("".join(f'<circle cx="{468 + d * math.cos(a):.1f}" cy="{124 + d * math.sin(a):.1f}" r="5" fill="#B0242C"/><circle cx="{466 + d * math.cos(a):.1f}" cy="{122 + d * math.sin(a):.1f}" r="1.6" fill="#FFD0D0" opacity="0.8"/>'
                       for a, d in [(rnd.uniform(0, 6.3), rnd.uniform(0, 34)) for _ in range(30)]))
    out.append('<path d="M 506 96 L 540 70" stroke="#C9B8A0" stroke-width="8" stroke-linecap="round"/>')
    # pumpkin pie with a slice already gone
    out.append(plate_top(D, 130, 480, 70))
    crust = D.rad([(0, "#F6CE8A"), (1, "#C98A44")], key="crust")
    fill = D.rad([(0, "#F09A48"), (0.7, "#D8742E"), (1, "#B8561E")], cx=0.45, cy=0.4, r=0.6)
    a0, a1 = math.radians(-30), math.radians(25)
    def arc(r, a, b):
        return (f"M 130 480 L {130 + r * math.cos(b):.1f} {480 + r * math.sin(b):.1f} A {r} {r} 0 1 1 {130 + r * math.cos(a):.1f} {480 + r * math.sin(a):.1f} Z")
    out.append(f'<path d="{arc(58, a0, a1)}" fill="{crust}"/><path d="{arc(48, a0, a1)}" fill="{fill}"/>')
    out.append(f'<path d="{arc(56, a0, a1)}" fill="none" stroke="#B8763A" stroke-width="3" stroke-dasharray="4 4"/>')
    out.append(f'<path d="M 130 480 L {130 + 58 * math.cos(a1):.1f} {480 + 58 * math.sin(a1):.1f} M 130 480 L {130 + 58 * math.cos(a0):.1f} {480 + 58 * math.sin(a0):.1f}" stroke="#9A4A1A" stroke-width="3"/>')
    for a in (100, 150, 200, 250, 300):
        x, y = 130 + 32 * math.cos(math.radians(a)), 480 + 32 * math.sin(math.radians(a))
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#FFFBF2"/><path d="M {x - 4:.1f} {y:.1f} a 4 4 0 1 1 4 4" stroke="#E2D6C2" stroke-width="1.6" fill="none"/>')
    out.append('<g fill="#7A4A22" opacity="0.6"><circle cx="186" cy="472" r="1.6"/><circle cx="192" cy="482" r="1.4"/><circle cx="182" cy="488" r="1.6"/></g>')
    # roast turkey on a platter, garnished
    out.append(shadow(D, 324, 490, 116, 78, "#1E0E04", 0.5))
    out.append(f'<ellipse cx="318" cy="480" rx="112" ry="74" fill="{D.rad([(0, "#FFFFFF"), (0.75, "#F2EBDD"), (1, "#C2B49E")], cx=0.42, cy=0.38, r=0.6)}"/>'
               '<ellipse cx="318" cy="480" rx="92" ry="58" fill="none" stroke="#D8CCB8" stroke-width="2"/>')
    for a in range(0, 360, 30):
        x, y = 318 + 82 * math.cos(math.radians(a)), 480 + 52 * math.sin(math.radians(a))
        if a % 60 == 0:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="#F29A3A"/><circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#FFC870"/>'
                       + "".join(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + 8 * math.cos(math.radians(b)):.1f}" y2="{y + 8 * math.sin(math.radians(b)):.1f}" stroke="#F29A3A" stroke-width="1"/>' for b in range(0, 360, 60)))
        else:
            out.append(f'<path d="M {x - 10:.1f} {y:.1f} L {x + 10:.1f} {y:.1f}" stroke="#4E6A3A" stroke-width="2"/>' + "".join(
                f'<path d="M {x + t:.1f} {y:.1f} l -3 -5 M {x + t:.1f} {y:.1f} l -3 5" stroke="#5E7A44" stroke-width="2" stroke-linecap="round"/>' for t in (-8, -3, 2, 7)))
    tk = D.rad([(0, "#FBD28A"), (0.45, "#E09A48"), (1, "#9A4E1E")], cx=0.4, cy=0.35, r=0.65)
    for sgn in (-1, 1):
        out.append(f'<g transform="rotate({sgn * -28} {318 + sgn * 34} 512)"><ellipse cx="{318 + sgn * 34}" cy="512" rx="14" ry="26" fill="{tk}"/>'
                   f'<rect x="{318 + sgn * 34 - 4}" y="532" width="8" height="14" rx="3" fill="#FBF3E6"/><path d="M {318 + sgn * 34 - 7} 546 l 3 6 l 2 -6 l 2 6 l 2 -6 l 3 6" stroke="#FBF3E6" stroke-width="2" fill="none"/></g>')
    out.append(f'<ellipse cx="318" cy="472" rx="58" ry="44" fill="{tk}"/>')
    out.append('<path d="M 318 432 Q 312 472 318 512" stroke="#A8582A" stroke-width="2.4" fill="none" opacity="0.6"/>'
               '<path d="M 296 450 q 6 -10 16 -12" stroke="#FFF2D0" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.6"/>'
               '<ellipse cx="270" cy="460" rx="10" ry="16" fill="#C27A3A" transform="rotate(20 270 460)"/><ellipse cx="366" cy="460" rx="10" ry="16" fill="#B06A2E" transform="rotate(-20 366 460)"/>')
    out.append('<g fill="#7A4A22" opacity="0.5">' + "".join(f'<circle cx="{x}" cy="{y}" r="1.4"/>' for x, y in ((300, 460), (330, 452), (340, 480), (306, 490), (290, 476), (322, 500))) + "</g>")
    # little pumpkins and leaves scattered at the end of the table
    out.append(pumpkin_top(D, 472, 470, 36, PK_ORANGE) + pumpkin_top(D, 516, 530, 24, PK_CREAM) + pumpkin_top(D, 440, 540, 20, PK_GOLD))
    out.append(maple(D, 520, 426, 24, L_RED, 40, spots=2) + oak(D, 230, 190, 22, L_GOLD, 60) + maple(D, 214, 560, 20, L_PLUM, -40) + slim_leaf(D, 404, 196, 20, L_ORANGE, 110))
    return D.render(out)


# ================================================================ 20. save room for pie (cooling on the sill, a squirrel eyeing it)
@design("save-room-for-pie")
def save_room_for_pie():
    D = Doc("pie")
    out = [f'<rect width="600" height="600" fill="{D.rad([(0, "#7E9C98"), (1, "#4E6A68")], cx=0.5, cy=0.4, r=0.8)}"/>']
    out.append('<g>' + "".join(f'<rect x="0" y="{y}" width="600" height="3" fill="#2E4442" opacity="0.4"/><rect x="0" y="{y + 3}" width="600" height="2" fill="#B8D0C8" opacity="0.18"/>' for y in range(18, 600, 24)) + "</g>")
    out.append(grain(81, "#1E2E2C", 260, op=0.1))
    out.append(word(300, 112, "save room", SERIF_IT, 86, "#FBEBD2", max_w=400, sh="#2E4442", off=(0, 4)))
    out.append(word(300, 200, "FOR PIE", BEBAS, 112, "#F2B94A", max_w=420, ls=14, sh="#2E4442", off=(0, 5)))
    # window: warm kitchen inside, gingham curtains
    out.append(f'<rect x="146" y="232" width="308" height="200" fill="{D.rad([(0, "#F2D8A8"), (0.6, "#C9A070"), (1, "#7A5634")], cx=0.5, cy=0.75, r=0.8)}"/>')
    out.append(glow(D, 300, 330, 150, "#FFE2A0", 0.5))
    out.append('<rect x="160" y="300" width="280" height="6" fill="#7A5232"/>' + "".join(
        f'<rect x="{x}" y="{282 if i % 2 else 286}" width="15" height="{18 if i % 2 else 14}" rx="3" fill="{c}"/>' for i, (x, c) in enumerate(((180, "#C9A06A"), (200, "#E9B54A"), (220, "#6E7A3C"), (364, "#A8482A"), (384, "#C9A06A"), (404, "#3E5A6A")))))
    out.append('<path d="M 300 232 L 300 262" stroke="#5A3A22" stroke-width="2"/><path d="M 282 262 L 318 262 L 310 276 L 290 276 Z" fill="#3E5A3A"/>' + glow(D, 300, 280, 40, "#FFF2C0", 0.7))
    gc = gingham(D, "#C2302A", "gh")
    for sgn in (-1, 1):
        x0 = 146 if sgn < 0 else 454
        pts = [(x0, 232), (x0 - sgn * 70, 232), (x0 - sgn * 52, 290), (x0 - sgn * 16, 350), (x0, 372)]
        cid = D.clip(f'<polygon points="{P(pts)}"/>')
        out.append(f'<polygon points="{P(pts)}" fill="{gc}"/><g {cid}><rect x="140" y="230" width="320" height="160" fill="{D.lin([(0, "#000", 0.25), (0.5, "#000", 0), (1, "#000", 0.25)], 0, 0, 1, 0, key="cf")}"/></g>')
    out.append(f'<rect x="146" y="228" width="308" height="18" fill="{gc}"/>' + "".join(f'<path d="M {x} 246 q 9 10 18 0" fill="{gc}"/>' for x in range(146, 454, 18)))
    # the raised upper sash: glass with reflections, then its bottom rail
    out.append('<rect x="146" y="232" width="308" height="100" fill="#DCEAF0" opacity="0.28"/>'
               '<g fill="#FFFFFF" opacity="0.35"><polygon points="170,240 196,240 150,320 146,320 146,282"/><polygon points="330,240 344,240 300,326 286,326"/></g>'
               '<rect x="296" y="232" width="8" height="100" fill="#F2E8D8"/><rect x="146" y="328" width="308" height="14" fill="#F6EEE0"/><rect x="146" y="340" width="308" height="3" fill="#B8A890"/>')
    trim = D.lin([(0, "#FFFBF2"), (1, "#D8CCB8")], 0, 0, 1, 0)
    out.append(f'<path d="M 128 214 L 472 214 L 472 436 L 456 436 L 456 230 L 144 230 L 144 436 L 128 436 Z" fill="{trim}"/><rect x="120" y="204" width="360" height="14" rx="2" fill="#FBF3E6"/>')
    # sill and brackets
    out.append(f'<rect x="104" y="432" width="392" height="20" rx="3" fill="{D.lin([(0, "#FFFBF2"), (1, "#C9BBA6")])}"/>')
    out.append(f'<rect x="104" y="452" width="392" height="14" fill="{D.lin([(0, "#1E2E2C", 0.5), (1, "#1E2E2C", 0)])}"/>')
    for x in (150, 450):
        out.append(f'<path d="M {x - 12} 452 L {x + 12} 452 L {x + 12} 470 Q {x} 490 {x - 12} 470 Z" fill="#E8DCC8"/>')
    # the lattice pie
    out.append(shadow(D, 306, 434, 112, 9, "#1E0E04", 0.5))
    dish = D.lin([(0, "#7FA6C2"), (0.3, "#B8D2E2"), (0.7, "#6E92AE"), (1, "#3E5E7A")], 0, 0, 1, 0)
    out.append(f'<path d="M 202 400 L 398 400 L 384 432 L 216 432 Z" fill="{dish}"/>' + "".join(f'<path d="M {x} 402 L {x + 2 * (300 - x) / 100:.1f} 430" stroke="#3E5E7A" stroke-width="1.4" opacity="0.5"/>' for x in range(212, 392, 12)))
    crust = D.rad([(0, "#FBD898"), (0.6, "#E2A85A"), (1, "#A8682A")], cx=0.45, cy=0.3, r=0.75, key="pcrust")
    out.append(f'<path d="M 204 402 Q 216 352 300 346 Q 384 352 396 402 Z" fill="#9A2E1E"/>')
    lid = D.clip('<path d="M 204 402 Q 216 352 300 346 Q 384 352 396 402 Z"/>')
    strips = []
    for i, x in enumerate(range(214, 400, 26)):
        strips.append(f'<path d="M {x} 404 Q {x + (300 - x) * 0.1:.1f} 360 {x + (300 - x) * 0.18:.1f} 340" stroke="{crust}" stroke-width="13" fill="none"/>')
    for j, y in enumerate((392, 376, 362)):
        strips.append(f'<path d="M 190 {y} Q 300 {y - 14} 410 {y}" stroke="{crust}" stroke-width="12" fill="none"/>')
    out.append(f'<g {lid}><rect x="200" y="340" width="200" height="70" fill="#7A2016"/>{"".join(strips)}'
               '<g fill="#C2402A">' + "".join(f'<circle cx="{x}" cy="{y}" r="3"/>' for x, y in ((236, 386), (288, 370), (330, 384), (260, 368), (350, 368))) + "</g></g>")
    out.append(f'<path d="M 198 404 Q 300 412 402 404" stroke="{crust}" stroke-width="12" fill="none" stroke-linecap="round"/>'
               '<path d="M 198 404 Q 300 412 402 404" stroke="#B8763A" stroke-width="3" fill="none" stroke-dasharray="5 6"/>')
    out.append('<path d="M 230 372 q 30 -14 60 -16" stroke="#FFF2D0" stroke-width="3" fill="none" opacity="0.6" stroke-linecap="round"/>')
    out.append(steam(D, 300, 340, 90, "#FFF2DC", n=3, gap=30, sw=6, op=0.75, seed=8))
    # a squirrel on the end of the sill, acorn in paws, eyeing the pie
    sq = D.rad([(0, "#C98250"), (0.6, "#9A5A32"), (1, "#5E3420")], cx=0.45, cy=0.35, r=0.7)
    out.append(f'<path d="M 132 430 C 92 420 82 360 108 330 C 128 306 104 284 118 270 C 140 300 136 330 128 352 C 120 382 136 410 150 424 Z" fill="{sq}"/>')
    out.append('<path d="M 112 330 C 104 352 108 388 128 414" stroke="#E8B888" stroke-width="3" fill="none" opacity="0.5"/>')
    out.append(f'<path d="M 140 432 C 128 412 136 376 160 370 C 184 368 192 404 186 432 Z" fill="{sq}"/>')
    out.append('<path d="M 160 432 C 154 414 158 394 172 388 C 182 398 182 418 178 432 Z" fill="#F2DCBE"/>')
    out.append(f'<ellipse cx="176" cy="362" rx="20" ry="17" fill="{sq}"/><path d="M 162 352 L 160 336 L 172 348 Z" fill="#8A4A26"/>'
               '<circle cx="183" cy="358" r="3.4" fill="#1E120A"/><circle cx="184.2" cy="356.8" r="1.2" fill="#FFFFFF"/><circle cx="195" cy="366" r="2.2" fill="#2A1A10"/>')
    out.append(acorn(D, 188, 394, 14, 12))
    out.append('<path d="M 176 390 q 8 -4 12 2 M 178 400 q 8 -2 10 4" stroke="#7A4426" stroke-width="4" stroke-linecap="round" fill="none"/>')
    # leaves drifting past the house, a couple of pumpkins on the ground
    out.append(falling(D, [("maple", 512, 300, 24, L_RED, 30), ("maple", 84, 230, 20, L_GOLD, -30), ("oak", 520, 470, 22, L_BROWN, 50),
                           ("slim", 476, 380, 18, L_ORANGE, -60)]))
    out.append(f'<rect x="-10" y="532" width="620" height="80" fill="{D.lin([(0, "#5E5A2E"), (1, "#3E3A1E")])}"/>')
    out.append(leaf_pile(D, 300, 560, 620, 40, 9, n=36, size=(10, 16)))
    out.append(pumpkin(D, 120, 524, 100, 72, PK_ORANGE, leaf=L_OLIVE) + pumpkin(D, 470, 532, 84, 60, PK_CREAM) + pumpkin(D, 538, 548, 54, 40, PK_GOLD, curl=False))
    return D.render(out)


# ================================================================ 21. cider mill (label badge)
@design("cider-mill")
def cider_mill():
    D = Doc("cm")
    out = [paper(D, "#DDBF90", "#B08A58", 91, ink="#4A2E14", op=0.16, wash=["#E9CFA0", "#8A6A3E"])]
    from layout import arc_text
    out.append(shadow(D, 304, 308, 250, 250, "#3A2410", 0.35))
    out.append(f'<circle cx="300" cy="300" r="240" fill="{D.rad([(0, "#6E2A3C"), (1, "#4A1A28")], r=0.5)}"/>')
    out.append('<circle cx="300" cy="300" r="231" fill="none" stroke="#F2E2C4" stroke-width="2.5"/><circle cx="300" cy="300" r="194" fill="none" stroke="#F2E2C4" stroke-width="2.5"/>')
    out.append(arc_text("FRESH PRESSED", 300, 300, 205, CINZEL, 30, "#F6E8CC", ls=8, uid="cm-top"))
    out.append(arc_text("APPLE CIDER", 300, 300, 224, CINZEL, 30, "#F6E8CC", ls=8, uid="cm-bot", top=False))
    from common import star_points
    for x in (82, 518):
        out.append(f'<polygon points="{star_points(x, 300, 12, 5)}" fill="#E9B54A"/>')
    # painted scene inside the label
    cid = D.clip('<circle cx="300" cy="300" r="190"/>')
    sc = [f'<rect x="100" y="100" width="400" height="400" fill="{D.lin([(0, "#86A8BE"), (0.5, "#E9D6B0"), (0.62, "#F6D8A4")])}"/>',
          glow(D, 420, 230, 130, "#FFF0C8", 0.7)]
    sc.append(cloud_puffs(D, 220, 170, 110, 2, shade="#9AA8B8"))
    line = rough([(100, 262), (190, 244), (290, 258), (380, 240), (500, 256)], 4, amp=4)
    sc.append(f'<polygon points="{P(line + [(500, 340), (100, 340)])}" fill="#B8907A"/>')
    rnd = random.Random(7)
    for x in range(100, 510, 15):
        sc.append(crown(D, x + rnd.uniform(-4, 4), (y_on(line, x) or 250) + 10, rnd.uniform(9, 13), [(["#A87A6A"], ["#C99A7E"], ["#E2BC98"]), (["#9A8A6A"], ["#B8A87E"], ["#D8C89A"])][x % 2], x, n=2))
    sc.append(f'<rect x="100" y="282" width="400" height="220" fill="{D.lin([(0, "#9AA25A"), (1, "#5E6E30")])}"/>')
    # apple trees either side
    for x, y, r in ((160, 290, 40), (446, 296, 36), (130, 316, 30)):
        sc.append(f'<rect x="{x - 4}" y="{y}" width="8" height="40" fill="#4A3424"/>')
        sc.append(crown(D, x, y - 4, r, (["#3E5A2A", "#4A6230"], ["#6A8236", "#7A8A3A"], ["#B8B85A", "#C9C060"]), x, n=10))
        sc.append("".join(f'<circle cx="{x + rnd.uniform(-0.8, 0.8) * r:.1f}" cy="{y - 4 + rnd.uniform(-0.7, 0.6) * r:.1f}" r="3.4" fill="#C62E26"/>' for _ in range(9)))
    # the mill: gable end, lit side, roof, and the waterwheel
    side = [(330, 246), (366, 254), (366, 336), (330, 340)]
    sc.append(f'<polygon points="{P(side)}" fill="#B8583A"/>')
    sc.append('<g stroke="#8A3A24" stroke-width="1" opacity="0.6">' + "".join(f'<line x1="{x}" y1="{246 + (x - 330) * 0.22:.1f}" x2="{x}" y2="{340 - (x - 330) * 0.1:.1f}"/>' for x in range(334, 366, 5)) + "</g>")
    sc.append(f'<polygon points="{P([(278, 196), (330, 246), (370, 252), (320, 202)])}" fill="#4A3A3E"/><line x1="320" y1="202" x2="370" y2="252" stroke="#F2C08A" stroke-width="2"/>')
    sc.append(f'<polygon points="{P([(226, 246), (278, 196), (330, 246), (330, 340), (226, 340)])}" fill="#8E3A24"/>')
    sc.append('<g stroke="#6E2A18" stroke-width="1" opacity="0.6">' + "".join(f'<line x1="{x}" y1="{max(246 - (52 - abs(x - 278)), 200)}" x2="{x}" y2="340"/>' for x in range(230, 330, 6)) + "</g>")
    sc.append(f'<polyline points="{P([(222, 248), (278, 194), (334, 248)])}" fill="none" stroke="#F2E6D0" stroke-width="3"/>')
    sc.append('<rect x="262" y="296" width="30" height="44" fill="#4A2416" stroke="#F2E6D0" stroke-width="2.4"/>'
              '<rect x="240" y="262" width="20" height="20" fill="#FFC870" stroke="#F2E6D0" stroke-width="2.4"/><rect x="296" y="262" width="20" height="20" fill="#FFC870" stroke="#F2E6D0" stroke-width="2.4"/>'
              '<rect x="270" y="222" width="16" height="16" fill="#3A1A12" stroke="#F2E6D0" stroke-width="2"/>')
    sc.append(f'<path d="M 340 238 L 420 238 L 420 246 L 340 246 Z" fill="#6E4A2E"/>')
    sc.append(f'<path d="M 410 244 Q 418 270 414 300" stroke="#DCEAF2" stroke-width="7" fill="none" opacity="0.85"/>')
    wx, wy, wr = 404, 300, 44
    sc.append(f'<circle cx="{wx}" cy="{wy}" r="{wr}" fill="none" stroke="#5A3A24" stroke-width="7"/><circle cx="{wx}" cy="{wy}" r="{wr - 14}" fill="none" stroke="#7A5232" stroke-width="3"/>')
    for k in range(12):
        a = math.radians(k * 30)
        sc.append(f'<line x1="{wx}" y1="{wy}" x2="{wx + wr * math.cos(a):.1f}" y2="{wy + wr * math.sin(a):.1f}" stroke="#6E4A2E" stroke-width="3"/>'
                  f'<rect x="{wx + (wr - 2) * math.cos(a) - 5:.1f}" y="{wy + (wr - 2) * math.sin(a) - 5:.1f}" width="10" height="10" transform="rotate({k * 30} {wx + (wr - 2) * math.cos(a):.1f} {wy + (wr - 2) * math.sin(a):.1f})" fill="#8A5A34"/>')
    sc.append(f'<circle cx="{wx}" cy="{wy}" r="7" fill="#3A2416"/>')
    # creek running out under the banner
    sc.append(f'<path d="M 360 346 Q 420 336 470 344 Q 500 350 510 360 L 510 420 Q 380 396 300 410 Q 200 424 100 420 L 100 392 Q 220 392 300 376 Q 340 366 360 346 Z" fill="{D.lin([(0, "#BCD6E2"), (1, "#5E8AA8")])}"/>')
    sc.append('<g stroke="#FFFFFF" stroke-width="2" opacity="0.6" stroke-linecap="round"><path d="M 400 352 q 14 -3 28 0"/><path d="M 330 384 q 16 -3 32 0"/><path d="M 220 404 q 18 -3 36 0"/></g>')
    sc.append(f'<circle cx="{wx}" cy="{wy + wr}" r="10" fill="#FFFFFF" opacity="0.6"/><circle cx="{wx + 12}" cy="{wy + wr - 4}" r="6" fill="#FFFFFF" opacity="0.5"/>')
    sc.append(f'<rect x="100" y="420" width="400" height="90" fill="{D.lin([(0, "#6E7A3A"), (1, "#3E4A22")])}"/>')
    sc.append(birds([(200, 200, 6), (214, 194, 4)], "#5A4A5A", 1.6))
    out.append(f'<g {cid}>' + "".join(sc) + "</g>")
    # jug and apples in the foreground, below the banner
    jug = cyl(D, "#FFF6E6", "#E8D8BC", "#A8946E", key="jug")
    out.append('<g transform="translate(300 486) scale(0.78) translate(-300 -482)">')
    out.append(shadow(D, 300, 482, 96, 10, "#1E1404", 0.5))
    out.append(f'<path d="M 278 420 Q 260 432 262 452 Q 264 478 280 482 L 320 482 Q 336 478 338 452 Q 340 432 322 420 Z" fill="{jug}"/>'
               '<path d="M 278 420 Q 260 432 262 452 L 338 452 Q 340 432 322 420 Z" fill="#7A4A24"/>'
               '<rect x="290" y="410" width="20" height="12" rx="3" fill="#7A4A24"/><ellipse cx="300" cy="410" rx="10" ry="3" fill="#5A3418"/>'
               '<path d="M 322 424 Q 346 428 340 446" stroke="#7A4A24" stroke-width="6" fill="none" stroke-linecap="round"/>'
               '<path d="M 272 436 Q 268 452 276 472" stroke="#FFFFFF" stroke-width="4" fill="none" opacity="0.4" stroke-linecap="round"/>')
    out.append('</g><g transform="translate(0 -12)">')
    out.append(apple(D, 232, 470, 20, seed=1, rot_=-14) + apple(D, 368, 472, 19, pal=("#F2E07A", "#C9B03A", "#7A6A1E"), blush="#E8743A", seed=2, leaf=False, rot_=12)
               + apple(D, 394, 480, 15, seed=3, leaf=False, rot_=30) + apple(D, 212, 482, 14, seed=4, leaf=False, rot_=-30))
    out.append("</g>")
    # banner across the badge
    out.append(ribbon(D, 300, 390, 424, 62, "#C2482A", "#7E2A16", tail=42))
    out.append(word(300, 410, "CIDER MILL", ANTON, 50, "#FBEBD2", max_w=380, ls=6, sh="#5A1A0A", off=(0, 3)))
    return D.render(out)


# ================================================================ 22. pick your own (farm sign)
def plank(D, x0, y0, x1, y1, col, dark, seed, point=0):
    """A painted board; point>0 makes a right-pointing arrow end, point<0 a left one."""
    if point > 0:
        pts = [(x0, y0), (x1, y0), (x1 + point, (y0 + y1) / 2), (x1, y1), (x0, y1)]
    elif point < 0:
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0 + point, (y0 + y1) / 2)]
    else:
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    cid = D.clip(f'<polygon points="{P(pts)}"/>')
    g = D.lin([(0, col), (1, dark)], key=("pk", col))
    rnd = random.Random(seed)
    wear = "".join(f'<ellipse cx="{rnd.uniform(x0, x1):.0f}" cy="{rnd.uniform(y0, y1):.0f}" rx="{rnd.uniform(6, 22):.0f}" ry="{rnd.uniform(2, 4):.0f}" fill="#C9A87A" opacity="{rnd.uniform(0.2, 0.45):.2f}"/>' for _ in range(10))
    return (f'<polygon points="{P(pts)}" fill="#3A2416" transform="translate(4 6)" opacity="0.35"/>'
            f'<polygon points="{P(pts)}" fill="{g}"/><g {cid}>{wood_grain(seed, (x0 - 40, y0, x1 + 40, y1), "#000", n=9, op=0.22, sw=1.4)}{wear}'
            f'<rect x="{x0 - 50}" y="{y0}" width="{x1 - x0 + 100}" height="3" fill="#FFFFFF" opacity="0.25"/><rect x="{x0 - 50}" y="{y1 - 4}" width="{x1 - x0 + 100}" height="4" fill="#000" opacity="0.2"/></g>')


@design("pick-your-own")
def pick_your_own():
    D = Doc("pyo")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#7AA6C8"), (0.45, "#C8DADA"), (0.66, "#F4E4C2"), (1, "#F4E4C2")])}"/>']
    out.append(glow(D, 500, 120, 160, "#FFF6DC", 0.8))
    out.append(cloud_puffs(D, 470, 96, 150, 4, shade="#9AB0C4") + cloud_puffs(D, 120, 300, 110, 6, shade="#9AB0C4", n=10))
    # tree line and the field
    rnd = random.Random(3)
    tl = []
    for x in range(-10, 620, 13):
        p = [(["#9A3424"], ["#C9542A"], ["#F08A3A"]), (["#A8761E"], ["#D8A23A"], ["#F6D066"]), (["#5E6A2E"], ["#8A9640"], ["#C9C060"]), (["#7A2A3A"], ["#A8404A"], ["#D06A5A"])][rnd.randrange(4)]
        tl.append(crown(D, x + rnd.uniform(-5, 5), 384 + rnd.uniform(-5, 4), rnd.uniform(11, 16), p, x, light=(-0.7, -0.7), n=3))
    out.append("".join(tl))
    out.append(f'<rect x="-10" y="360" width="620" height="34" fill="{D.lin([(0, "#F4E4C2", 0), (1, "#F4E4C2", 0.45)])}"/>')
    out.append(f'<rect x="-10" y="392" width="620" height="220" fill="{D.lin([(0, "#C9A85A"), (0.4, "#A8904A"), (1, "#6E6A2E")])}"/>')
    rnd = random.Random(5)
    out.append('<g fill="none" stroke-width="2" stroke-linecap="round">' + "".join(
        f'<path d="M {x:.0f} {y:.0f} q {rnd.uniform(-3, 3):.1f} {-h / 2:.1f} {rnd.uniform(-5, 5):.1f} {-h:.1f}" stroke="{rnd.choice(["#E2C67A", "#8A7A3A", "#B8A05A", "#6E6A2E"])}"/>'
        for x, y, h in [(rnd.uniform(-10, 610), rnd.uniform(400, 600), 0) for _ in range(260)] for h in [6 + (y - 400) * 0.08]) + "</g>")
    # posts
    post = D.lin([(0, "#8A7A6A"), (0.35, "#B8A894"), (1, "#5A4A3E")], 0, 0, 1, 0)
    for x in (148, 434):
        out.append(f'<path d="M {x} 556 L {x} 138 L {x + 9} 128 L {x + 18} 138 L {x + 18} 556 Z" fill="{post}"/>')
        out.append(wood_grain(x, (x + 2, 140, x + 16, 556), "#3A2A20", n=4, op=0.4, sw=1.2, vertical=True))
    out.append(shadow(D, 300, 560, 200, 12, "#3A3010", 0.4))
    # boards
    out.append(plank(D, 84, 150, 516, 248, "#B4382A", "#7E2418", 1))
    out.append('<line x1="84" y1="199" x2="516" y2="199" stroke="#4A160E" stroke-width="2" opacity="0.6"/>')
    out.append(word(300, 222, "PICK YOUR OWN", ANTON, 66, "#FBF0DC", max_w=400, ls=3))
    out.append(plank(D, 112, 266, 462, 334, "#F2E4C8", "#C9B48E", 2, point=48))
    out.append(word(290, 320, "PUMPKINS", ANTON, 50, "#C9561E", max_w=320, ls=6))
    out.append(plank(D, 138, 350, 470, 412, "#5E6B34", "#3E4A22", 3, point=-50))
    out.append(word(310, 400, "APPLES", ANTON, 46, "#FBF0DC", max_w=280, ls=8))
    out.append("".join(f'<circle cx="{x + dx}" cy="{y}" r="3" fill="#4A4A4A"/><circle cx="{x + dx - 0.8}" cy="{y - 0.8}" r="1.2" fill="#C9C9C9"/>'
                       for x in (148, 434) for dx in (6, 12) for y in (172, 228, 290, 312, 372, 392)))
    # a crow keeping watch on the left post
    out.append('<g transform="translate(157 128)">'
               '<path d="M -26 -4 Q -10 -30 14 -24 Q 26 -22 28 -10 L 40 -6 L 28 -2 Q 24 8 8 8 L -6 8 L -30 14 L -22 2 Z" fill="#1E1E28"/>'
               '<path d="M -18 -8 Q 0 -20 16 -14" stroke="#5A6A8A" stroke-width="2.4" fill="none" opacity="0.7"/>'
               '<circle cx="18" cy="-16" r="2.4" fill="#F2D27A"/><path d="M 0 8 L -2 16 M 8 8 L 8 16" stroke="#2A2A2A" stroke-width="2.4" stroke-linecap="round"/></g>')
    # produce at the foot of the sign
    hay = D.lin([(0, "#F6DC96"), (1, "#B8903E")])
    out.append(shadow(D, 104, 552, 70, 10, "#3A3010", 0.5))
    out.append(f'<polygon points="44,488 70,470 176,470 150,488" fill="#F8E6A8"/><polygon points="150,488 176,470 176,532 150,552" fill="#A8803A"/>'
               f'<rect x="44" y="488" width="106" height="64" rx="4" fill="{hay}"/>')
    rnd = random.Random(8)
    out.append('<g stroke="#A8782E" stroke-width="1.6" opacity="0.65" fill="none" stroke-linecap="round">' + "".join(
        f'<path d="M {rnd.uniform(46, 140):.0f} {rnd.uniform(490, 548):.0f} l {rnd.uniform(6, 14):.0f} {rnd.uniform(-2, 2):.0f}"/>' for _ in range(40)) + "</g>")
    out.append('<g stroke="#7A4A20" stroke-width="3"><line x1="74" y1="488" x2="74" y2="552"/><line x1="120" y1="488" x2="120" y2="552"/>'
               '<line x1="74" y1="488" x2="100" y2="470"/><line x1="120" y1="488" x2="146" y2="470"/></g>')
    out.append('<g stroke="#E8C870" stroke-width="2" fill="none"><path d="M 40 490 q -4 -6 2 -10"/><path d="M 150 552 q 8 2 10 -4"/><path d="M 60 552 q -2 6 -8 6"/></g>')
    out.append(pumpkin(D, 498, 520, 104, 76, PK_ORANGE, leaf=L_OLIVE) + pumpkin(D, 404, 540, 70, 50, PK_GOLD) + pumpkin(D, 214, 546, 64, 46, PK_CREAM, curl=False))
    out.append(apple(D, 290, 548, 18, seed=2, cast=0.3) + apple(D, 318, 554, 16, seed=3, cast=0.3, leaf=False, rot_=30))
    out.append(birds([(250, 90, 8), (272, 80, 6)], "#3A3A4A", 2))
    return D.render(out)


# ================================================================ 23. misty mornings (a buck at the forest edge, dawn)
DEER = [(-14, -84), (-10, -90), (-2, -97), (8, -100), (14, -94), (22, -84), (32, -72), (42, -66), (60, -64), (80, -65), (92, -64), (98, -60),
        (100, -52), (97, -42), (93, -34), (90, -24), (92, -16), (91, 0), (86, 0), (85, -14), (82, -26), (77, -34), (66, -37), (50, -36), (38, -37),
        (32, -30), (31, -14), (30, 0), (25, 0), (25, -14), (23, -30), (20, -44), (14, -60), (6, -72), (-2, -78), (-10, -80)]


def deer(D, x, y, s, rim="#FFD9A0", antlers=True):
    """White-tailed buck in profile facing left; (x, y) = front hoof on the ground."""
    g = D.lin([(0, "#B07A4C"), (0.6, "#8A5634"), (1, "#5A3420")], key="deerbody")
    out = [f'<g transform="translate({x} {y}) scale({s})">',
           '<polygon points="36,-36 39,-14 39,0 35,0 34,-14 31,-34" fill="#4A2C1A"/><polygon points="74,-36 80,-22 81,0 77,0 76,-20 68,-34" fill="#4A2C1A"/>',
           f'<polygon points="{P(DEER)}" fill="{g}"/>',
           '<path d="M 38 -40 Q 56 -34 74 -38" stroke="#E8D4B4" stroke-width="3" fill="none" opacity="0.6"/>',
           '<ellipse cx="10" cy="-66" rx="4" ry="7" fill="#F2E6D2" opacity="0.85" transform="rotate(30 10 -66)"/><ellipse cx="-9" cy="-82" rx="4" ry="2.6" fill="#F2E6D2" opacity="0.85"/>',
           '<path d="M 96 -62 Q 104 -58 101 -48" stroke="#F6EEE0" stroke-width="4" fill="none" stroke-linecap="round"/>',
           '<polygon points="8,-99 23,-113 26,-107 15,-95" fill="#7A4A2C"/><polygon points="11,-99 22,-110 23,-107 15,-97" fill="#D8B494"/>',
           '<circle cx="-14" cy="-84" r="2.6" fill="#1E120A"/><circle cx="-2" cy="-90" r="2" fill="#1E120A"/><circle cx="-2.6" cy="-90.6" r="0.6" fill="#FFFFFF"/>',
           '<g fill="#2A1A10"><rect x="24.5" y="-3" width="6" height="3" rx="1"/><rect x="85.5" y="-3" width="6" height="3" rx="1"/></g>']
    if antlers:
        out.append('<g fill="none" stroke="#6E5A44" stroke-width="2.6" stroke-linecap="round"><path d="M 0 -99 C -2 -118 10 -130 26 -136"/><path d="M 4 -116 l -6 -12 M 12 -126 l -2 -15 M 20 -132 l 4 -13"/></g>'
                   '<g fill="none" stroke="#E2D2B4" stroke-width="3" stroke-linecap="round"><path d="M 4 -99 C 6 -116 18 -128 36 -130"/><path d="M 10 -113 l -2 -17 M 20 -122 l 2 -18 M 30 -128 l 8 -14"/></g>')
    rimpts = [(-14, -84), (-10, -90), (-2, -97), (8, -100)]
    chest = [(-2, -78), (6, -72), (14, -60), (20, -44), (23, -30), (25, -14)]
    back = [(14, -94), (22, -84), (32, -72), (42, -66), (60, -64), (80, -65), (92, -64), (98, -60)]
    out.append(f'<polyline points="{P(rimpts)}" fill="none" stroke="{rim}" stroke-width="2.4" stroke-linecap="round"/>'
               f'<polyline points="{P(chest)}" fill="none" stroke="{rim}" stroke-width="2.2" stroke-linecap="round" opacity="0.9"/>'
               f'<polyline points="{P(back)}" fill="none" stroke="{rim}" stroke-width="1.6" stroke-linecap="round" opacity="0.55"/>')
    out.append("</g>")
    return "".join(out)


@design("misty-mornings")
def misty_mornings():
    D = Doc("mmo")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#B4B0CC"), (0.3, "#E2C4BE"), (0.52, "#F6D8B2"), (1, "#F2DCB8")])}"/>']
    out.append(glow(D, 160, 318, 320, "#FFE6B8", 0.9))
    out.append('<circle cx="160" cy="318" r="24" fill="#FFF6DE"/>')
    out.append(word(300, 128, "misty", SERIF_IT, 104, "#5A3A4A", max_w=320))
    out.append(word(300, 196, "MORNINGS", JOS, 54, "#9A4A34", max_w=420, ls=16))
    # far spruce ridge in lavender haze
    line = rough([(-10, 318), (140, 310), (300, 316), (460, 306), (610, 314)], 21, amp=4)
    out.append(f'<polygon points="{P(line + [(610, 420), (-10, 420)])}" fill="#B8A6BC"/>')
    rnd = random.Random(22)
    out.append("".join(conifer(x + rnd.uniform(-5, 5), (y_on(line, x) or 312) + 6, rnd.uniform(14, 44), rnd.choice(["#B4A4BA", "#A898B2", "#BCAEC2"]), rnd.random()) for x in range(-10, 620, 13)))
    out.append(f'<rect x="0" y="290" width="600" height="80" fill="{D.lin([(0, "#F6E6D6", 0), (0.6, "#F6E6D6", 0.85), (1, "#F6E6D6", 0.3)])}"/>')
    # middle woods, hazy autumn colour
    haze = [(["#B08478"], ["#C9987E"], ["#E8C49C"]), (["#A8907E"], ["#C8AE8C"], ["#E2D0A8"]), (["#A87A70"], ["#C2907E"], ["#E2B496"])]
    cr = []
    for row, y0 in enumerate((350, 362, 376)):
        for x in range(-10 + row * 9, 620, 18):
            cr.append(crown(D, x + rnd.uniform(-5, 5), y0 + rnd.uniform(-4, 4), rnd.uniform(12, 16), haze[rnd.randrange(3)], x * 3 + row, light=(-0.8, -0.5), n=3))
    out.append("".join(cr))
    out.append(f'<rect x="0" y="350" width="600" height="60" fill="{D.lin([(0, "#F6E6D6", 0.2), (1, "#F6E6D6", 0.7)])}"/>')
    # god rays from the low sun
    out.append('<g fill="#FFF0D0" opacity="0.18">' + "".join(f'<polygon points="160,318 {x1},620 {x2},620"/>' for x1, x2 in ((260, 330), (400, 470), (540, 600), (680, 740))) + "</g>")
    # the near forest edge on the right, peak colour
    pals = [(["#8E2E20"], ["#C2482A", "#B4402A"], ["#F08A4A", "#F29A5A"]), (["#A8641E"], ["#E0862E", "#D87A2A"], ["#F8B860", "#FBC870"]),
            (["#B07A1E"], ["#E0A62E"], ["#F8D870"]), (["#4E5A26"], ["#7E8A3A"], ["#C2C064"])]
    fp = [(["#8E2E20", "#7A2A22"], ["#C2482A", "#B4402A"], ["#F08A4A", "#F29A5A"]), (["#A8641E", "#9A5A1E"], ["#E0862E", "#D87A2A"], ["#F8B860", "#FBC870"]),
          (["#B07A1E", "#9A6A1A"], ["#E0A62E", "#D8A030"], ["#F8D870", "#FBE08A"]), (["#4E5A26", "#5A6428"], ["#7E8A3A", "#8A9640"], ["#C2C064", "#D0C870"])]
    for k, (x, cy, rx, ry, pi) in enumerate(((400, 330, 46, 62, 1), (590, 300, 70, 96, 0), (470, 300, 58, 84, 2), (536, 336, 50, 70, 3), (430, 372, 40, 46, 0))):
        out.append(f'<path d="M {x - 5} 432 L {x - 3} {cy} L {x + 3} {cy} L {x + 5} 432 Z" fill="#4A3030"/>'
                   f'<path d="M {x} {cy + ry * 0.4:.0f} l {-rx * 0.4:.0f} {-ry * 0.3:.0f} M {x} {cy + ry * 0.2:.0f} l {rx * 0.35:.0f} {-ry * 0.35:.0f}" stroke="#4A3030" stroke-width="3"/>')
        out.append(foliage(D, x, cy, rx, ry, fp[pi], 300 + k, n=int(rx * ry / 14), size=(4, 8), light=(-0.85, -0.45), leafy=True))
    rnd = random.Random(27)
    out.append("".join(conifer(x, 432, rnd.uniform(70, 110), "#4E4A44", rnd.random(), light="#C8A07A") for x in (366, 504, 560)))
    out.append(f'<rect x="330" y="380" width="290" height="60" fill="{D.lin([(0, "#F6E6D6", 0), (1, "#F6E6D6", 0.65)])}"/>')
    # meadow with low mist
    out.append(f'<path d="M -10 420 Q 200 410 400 424 Q 520 432 610 426 L 610 610 L -10 610 Z" fill="{D.lin([(0, "#C8B47A"), (0.4, "#9A8E52"), (1, "#5A5A2E")])}"/>')
    out.append(f'<ellipse cx="260" cy="446" rx="300" ry="26" fill="{D.rad([(0, "#FFF4E2", 0.75), (1, "#FFF4E2", 0)])}"/>')
    out.append(grass(160, 33, (-10, 430, 610, 600), ["#D8C88A", "#A89A5A", "#7A7A3E", "#E8D49A"], h=(8, 22)))
    out.append(shadow(D, 300, 478, 120, 8, "#3A3418", 0.4))
    out.append(deer(D, 222, 476, 1.55))
    out.append(f'<ellipse cx="320" cy="482" rx="220" ry="16" fill="{D.rad([(0, "#FFF4E2", 0.55), (1, "#FFF4E2", 0)])}"/>')
    out.append(grass(120, 34, (-10, 470, 610, 610), ["#6E6A34", "#8A7E44", "#C9B47A", "#4E4E26"], h=(14, 36), sw=2.2))
    # seed heads and goldenrod in the foreground
    for x, h in ((70, 120), (96, 96), (520, 130), (548, 100), (500, 90)):
        out.append(f'<path d="M {x} 610 Q {x + 6} {600 - h / 2} {x + 2} {600 - h}" stroke="#7A6A30" stroke-width="2.4" fill="none"/>')
        out.append("".join(f'<ellipse cx="{x + 2 + (i % 2) * 6 - 3}" cy="{600 - h + i * 6}" rx="4" ry="2.6" fill="{"#F2C24A" if i % 3 else "#D8A030"}"/>' for i in range(7)))
    out.append(falling(D, [("maple", 470, 470, 16, L_RED, 30), ("slim", 120, 380, 14, L_GOLD, -40)]))
    out.append(birds([(250, 254, 7), (268, 246, 5), (232, 262, 5)], "#6A4A5A", 1.8))
    return D.render(out)


# ================================================================ 24. happy fall, y'all (hayride at sunset)
@design("happy-fall-yall")
def happy_fall_yall():
    D = Doc("hfy")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#4A3C6E"), (0.3, "#B8607A"), (0.5, "#EE945A"), (0.6, "#FBC878"), (1, "#FBC878")])}"/>']
    out.append(glow(D, 450, 350, 300, "#FFE09A", 0.9))
    out.append('<circle cx="450" cy="342" r="30" fill="#FFF2C8"/>')
    out.append('<g fill="#F6A88A" opacity="0.5">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="4"/>' for x, y, w in ((110, 290, 80), (520, 270, 70), (360, 300, 50))) + "</g>")
    out.append(word(300, 124, "happy fall,", SERIF_IT, 90, "#FCEBD2", max_w=420, sh="#3A2A4A", off=(0, 4), sh_op=0.6))
    out.append(word(300, 268, "Y'ALL", ANTON, 140, "#FCEBD2", max_w=420, ls=16, sh="#3A2A4A", off=(0, 6), sh_op=0.55))
    # tree line on the horizon, backlit
    rnd = random.Random(4)
    tl = []
    for x in range(-10, 620, 16):
        if 400 < x < 500:
            continue
        tl.append(crown(D, x + rnd.uniform(-4, 4), 344 + rnd.uniform(-6, 4), rnd.uniform(12, 20), (["#5A3448"], ["#7A4458"], ["#C8786A"]), x, light=(0.8, -0.4), n=3))
    out.append("".join(tl))
    out.append(f'<rect x="0" y="320" width="600" height="40" fill="{D.lin([(0, "#FBC878", 0), (1, "#FBC878", 0.5)])}"/>')
    # stubble field with rows running to the sun
    out.append(f'<rect x="-10" y="352" width="620" height="260" fill="{D.lin([(0, "#E8B060"), (0.35, "#C2863E"), (1, "#6E4422")])}"/>')
    out.append('<g stroke="#8A5A2A" stroke-width="2" opacity="0.4">' + "".join(f'<line x1="450" y1="352" x2="{x}" y2="610"/>' for x in range(-600, 1400, 70)) + "</g>")
    for x, y, r in ((120, 372, 9), (170, 368, 7), (560, 376, 10)):
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{r * 1.2}" ry="{r}" fill="#8A5A2A"/><ellipse cx="{x + r * 0.4}" cy="{y - r * 0.2}" rx="{r * 0.6}" ry="{r * 0.6}" fill="#E8B060" opacity="0.6"/>')
    # dirt track
    out.append(f'<path d="M -10 452 Q 300 430 610 438 L 610 460 Q 300 452 -10 474 Z" fill="{D.lin([(0, "#C8925A"), (1, "#E8B880")], 0, 0, 1, 0)}"/>')
    # hay wagon with riders
    out.append(shadow(D, 300, 456, 230, 10, "#3A1E0E", 0.5))
    out.append('<g fill="#5A3A26"><rect x="98" y="398" width="236" height="14"/></g><rect x="98" y="398" width="236" height="3" fill="#FFC88A" opacity="0.8"/>')
    for x in range(104, 334, 26):
        out.append(f'<rect x="{x}" y="376" width="5" height="24" fill="#6E4630"/>')
    out.append('<rect x="98" y="374" width="236" height="5" fill="#6E4630"/><rect x="98" y="374" width="236" height="2" fill="#FFC88A" opacity="0.7"/>')
    hay = D.lin([(0, "#F6D488"), (1, "#B88A3E")], key="hfyhay")
    for x0, y0, w, h in ((110, 360, 70, 38), (186, 360, 70, 38), (262, 360, 66, 38), (146, 326, 66, 34), (220, 326, 66, 34)):
        out.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="3" fill="{hay}"/><rect x="{x0 + w - 6}" y="{y0}" width="6" height="{h}" fill="#FFE2A0" opacity="0.6"/>'
                   f'<line x1="{x0 + w * 0.3:.0f}" y1="{y0}" x2="{x0 + w * 0.3:.0f}" y2="{y0 + h}" stroke="#8A5A24" stroke-width="2"/><line x1="{x0 + w * 0.7:.0f}" y1="{y0}" x2="{x0 + w * 0.7:.0f}" y2="{y0 + h}" stroke="#8A5A24" stroke-width="2"/>')
    riders = [(132, 326, "#3E4A6A", "#B4532A"), (172, 292, "#7A2E3A", None), (214, 292, "#2E5A4A", "#E9B54A"), (254, 292, "#B4532A", None), (300, 326, "#4A3A6A", "#E9B54A")]
    for x, top, coat, hat in riders:
        out.append(f'<path d="M {x - 10} {top + 34} L {x - 11} {top + 12} Q {x} {top + 6} {x + 11} {top + 12} L {x + 10} {top + 34} Z" fill="{coat}"/>'
                   f'<circle cx="{x}" cy="{top}" r="8" fill="#3A2420"/><path d="M {x + 9} {top + 12} L {x + 11} {top + 32}" stroke="#FFC88A" stroke-width="2"/>'
                   f'<path d="M {x + 5} {top - 6} q 4 4 3 10" stroke="#FFC88A" stroke-width="1.8" fill="none"/>')
        if hat:
            out.append(f'<path d="M {x - 9} {top - 3} Q {x} {top - 18} {x + 9} {top - 3} Z" fill="{hat}"/>')
    out.append('<path d="M 214 304 q 14 -18 8 -34" stroke="#2E5A4A" stroke-width="5" stroke-linecap="round" fill="none"/>')
    out.append('<g stroke="#3A2420" stroke-width="4" stroke-linecap="round"><path d="M 126 398 l -4 18 M 138 398 l 2 18"/><path d="M 294 398 l -2 18 M 306 398 l 4 18"/></g>')
    for wx in (138, 300):
        out.append(f'<circle cx="{wx}" cy="436" r="17" fill="#2E1E18"/><circle cx="{wx}" cy="436" r="11" fill="none" stroke="#6E4630" stroke-width="3"/><circle cx="{wx}" cy="436" r="3" fill="#6E4630"/>'
                   f'<path d="M {wx + 6} 420 A 17 17 0 0 1 {wx + 17} 432" stroke="#FFC88A" stroke-width="2.4" fill="none"/>')
    out.append('<line x1="334" y1="406" x2="372" y2="420" stroke="#2E1E18" stroke-width="4"/>')
    # vintage tractor
    red = D.lin([(0, "#D84A34"), (1, "#7A2018")], key="tred")
    out.append(f'<path d="M 404 414 L 404 386 Q 404 380 410 380 L 492 380 Q 500 382 504 392 L 508 414 Z" fill="{red}"/>'
               '<rect x="410" y="380" width="94" height="3" fill="#FFC88A" opacity="0.8"/><path d="M 500 384 L 508 414" stroke="#FFC88A" stroke-width="2.4"/>'
               '<g stroke="#5A1A12" stroke-width="2" opacity="0.7">' + "".join(f'<line x1="{x}" y1="388" x2="{x}" y2="410"/>' for x in range(470, 500, 6)) + "</g>"
               '<rect x="476" y="354" width="7" height="28" fill="#2E2420"/>')
    out.append(f'<path d="M 362 420 A 40 40 0 0 1 438 400 L 438 412 L 362 432 Z" fill="{red}"/>')
    out.append('<circle cx="398" cy="420" r="34" fill="#241814"/><circle cx="398" cy="420" r="20" fill="#C8302A"/><circle cx="398" cy="420" r="7" fill="#E8C870"/>')
    out.append('<g stroke="#3A2A24" stroke-width="5">' + "".join(f'<line x1="{398 + 30 * math.cos(math.radians(a)):.1f}" y1="{420 + 30 * math.sin(math.radians(a)):.1f}" x2="{398 + 36 * math.cos(math.radians(a)):.1f}" y2="{420 + 36 * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 24)) + "</g>")
    out.append('<path d="M 410 388 A 34 34 0 0 1 430 404" stroke="#FFC88A" stroke-width="2.6" fill="none"/>')
    out.append('<circle cx="488" cy="434" r="18" fill="#241814"/><circle cx="488" cy="434" r="9" fill="#C8302A"/><path d="M 496 420 A 18 18 0 0 1 505 430" stroke="#FFC88A" stroke-width="2.2" fill="none"/>')
    out.append('<rect x="392" y="362" width="18" height="6" fill="#2E2420"/><path d="M 420 372 L 432 360" stroke="#2E2420" stroke-width="3"/><ellipse cx="434" cy="358" rx="8" ry="3" fill="#2E2420"/>')
    out.append(person(400, 384, 46, "#3E5A7A", rim="#FFC88A", hat="#C9A060").replace('d="M -8 -46 L 9 -46 L 12 -2 L 6 -2 L 3 -28 L -1 -2 L -7 -2 L -10 -44 Z"', 'd="M -8 -46 L 9 -46 L 30 -40 L 30 -20 L 24 -20 L 22 -34 L -8 -34 Z"'))
    out.append('<g fill="#F2E2C8" opacity="0.55"><circle cx="482" cy="344" r="7"/><circle cx="476" cy="330" r="9"/><circle cx="466" cy="314" r="11"/></g>')
    out.append(f'<ellipse cx="70" cy="440" rx="70" ry="18" fill="{D.rad([(0, "#F6D8A0", 0.6), (1, "#F6D8A0", 0)])}"/>')
    # foreground stubble, pumpkins, a corn shock
    rnd = random.Random(9)
    out.append('<g stroke-width="2" stroke-linecap="round">' + "".join(
        f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x + rnd.uniform(-2, 2):.0f}" y2="{y - 6 - (y - 470) * 0.06:.0f}" stroke="{rnd.choice(["#F2C27A", "#A8703A", "#6E4422"])}"/>' for x, y in [(rnd.uniform(-10, 610), rnd.uniform(476, 600)) for _ in range(220)]) + "</g>")
    for i in range(13):
        t = i / 12
        xb = 476 + 92 * t
        xt = 500 + 44 * t + (t - 0.5) * 30
        out.append(f'<path d="M {xb:.0f} 598 Q {518 + (t - 0.5) * 16:.0f} 512 {xt:.0f} 434" stroke="{["#C8A060", "#A8803E", "#E2C07A", "#8A6A30"][i % 4]}" stroke-width="7" fill="none" stroke-linecap="round"/>')
    out.append('<path d="M 500 506 Q 520 514 540 506" stroke="#6E3A18" stroke-width="5" fill="none"/><path d="M 470 470 q 20 -6 30 -30 M 560 470 q -14 -10 -14 -34" stroke="#C8A060" stroke-width="4" fill="none" stroke-linecap="round"/>')
    out.append(mirror(pumpkin(D, 150, 540, 120, 86, PK_ORANGE, leaf=L_OLIVE, cast=0.3), 150) + mirror(pumpkin(D, 262, 556, 70, 50, PK_CREAM, cast=0.3), 262)
               + mirror(pumpkin(D, 430, 560, 80, 58, PK_GOLD, cast=0.3), 430))
    return D.render(out)


# ================================================================ 25. harvest moon over the cornfield
def cornstalk(x, base, h, col, seed, rim=None, lean=0.0):
    rnd = random.Random(seed)
    tx = x + lean * h
    out = [f'<path d="M {x:.1f} {base:.1f} Q {x + lean * h * 0.3:.1f} {base - h * 0.5:.1f} {tx:.1f} {base - h:.1f}" stroke="{col}" stroke-width="{max(1.2, h * 0.022):.1f}" fill="none"/>']
    for i in range(6):
        t = 0.2 + i * 0.12
        px, py = x + lean * h * t, base - h * t
        sgn = 1 if i % 2 else -1
        L = h * rnd.uniform(0.32, 0.45)
        d = f"M {px:.1f} {py:.1f} Q {px + sgn * L * 0.6:.1f} {py - L * 0.5:.1f} {px + sgn * L:.1f} {py + L * 0.15:.1f} Q {px + sgn * L * 0.5:.1f} {py - L * 0.25:.1f} {px:.1f} {py + h * 0.02:.1f} Z"
        out.append(f'<path d="{d}" fill="{col}"/>')
        if rim and sgn > 0:
            out.append(f'<path d="M {px:.1f} {py:.1f} Q {px + sgn * L * 0.6:.1f} {py - L * 0.5:.1f} {px + sgn * L:.1f} {py + L * 0.15:.1f}" stroke="{rim}" stroke-width="{max(0.8, h * 0.008):.1f}" fill="none" opacity="0.7"/>')
    out.append("".join(f'<line x1="{tx:.1f}" y1="{base - h:.1f}" x2="{tx + dx * h * 0.06:.1f}" y2="{base - h - h * 0.1:.1f}" stroke="{col}" stroke-width="{max(1, h * 0.012):.1f}"/>' for dx in (-1, -0.3, 0.4, 1)))
    if h > 60:
        out.append(f'<ellipse cx="{x + lean * h * 0.5 - h * 0.04:.1f}" cy="{base - h * 0.5:.1f}" rx="{h * 0.03:.1f}" ry="{h * 0.09:.1f}" transform="rotate(-20 {x:.1f} {base - h * 0.5:.1f})" fill="{col}"/>')
    if rim:
        out.append(f'<path d="M {x + 1:.1f} {base:.1f} Q {x + lean * h * 0.3 + 1:.1f} {base - h * 0.5:.1f} {tx + 1:.1f} {base - h:.1f}" stroke="{rim}" stroke-width="{max(0.8, h * 0.008):.1f}" fill="none" opacity="0.6"/>')
    return "".join(out)


@design("harvest-moon")
def harvest_moon():
    D = Doc("hmn")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#161B3C"), (0.45, "#2E2E5A"), (0.68, "#7A4E6A"), (0.76, "#D0805A"), (1, "#D0805A")])}"/>']
    rnd = random.Random(3)
    out.append('<g fill="#F6EDE0">' + "".join(f'<circle cx="{rnd.uniform(0, 600):.0f}" cy="{rnd.uniform(0, 300):.0f}" r="{rnd.uniform(0.6, 1.8):.1f}" opacity="{rnd.uniform(0.3, 0.9):.2f}"/>' for _ in range(80)) + "</g>")
    out.append(glow(D, 300, 336, 300, "#F6B868", 0.55))
    moon = D.rad([(0, "#FFF0C0"), (0.55, "#F8C878"), (1, "#E0904A")], cx=0.42, cy=0.38, r=0.62)
    out.append(f'<circle cx="300" cy="336" r="132" fill="{moon}"/>')
    out.append('<g fill="#D8904A" opacity="0.2"><ellipse cx="256" cy="300" rx="34" ry="24"/><ellipse cx="338" cy="352" rx="40" ry="28"/><ellipse cx="318" cy="276" rx="16" ry="12"/><ellipse cx="262" cy="372" rx="18" ry="12"/></g>')
    out.append(word(300, 112, "HARVEST", JOS, 62, "#F6EDE0", max_w=440, ls=20))
    out.append(word(300, 192, "moon", SERIF_IT, 130, "#F6C462", max_w=360, sh="#0E1028", off=(0, 5)))
    out.append(birds([(232, 286, 10), (256, 270, 8), (280, 292, 7), (214, 306, 6), (300, 260, 6)], "#241A30", 2.6))
    # distant farm on the horizon
    out.append('<path d="M -10 408 Q 150 396 300 404 Q 450 410 610 398 L 610 440 L -10 440 Z" fill="#2E2238"/>')
    out.append('<polygon points="84,404 84,382 102,368 120,382 120,404" fill="#22182C"/><rect x="92" y="388" width="8" height="8" fill="#FFC870"/>' + glow(D, 96, 392, 18, "#FFC870", 0.6))
    out.append('<rect x="128" y="372" width="12" height="34" fill="#22182C"/><path d="M 128 372 Q 134 362 140 372 Z" fill="#22182C"/>')
    # rows of corn, far (moon-lit) to near (silhouette)
    rows = [(420, 34, "#3A2E48", "#F2B868", 7), (446, 56, "#2E2440", "#F2B868", 11), (486, 96, "#241C34", "#F2B868", 18), (540, 150, "#1A1428", "#E8A858", 28), (612, 240, "#120E1E", "#D8985A", 46)]
    for base, h, col, rim, step in rows:
        x = -20 + rnd.uniform(0, step)
        g = []
        while x < 620:
            if not (base > 500 and 150 < x < 450):
                g.append(cornstalk(x, base + rnd.uniform(-3, 3), h * rnd.uniform(0.85, 1.1), col, int(x * 7 + base), rim=rim, lean=rnd.uniform(-0.08, 0.08)))
            x += step * rnd.uniform(0.8, 1.3)
        out.append(f'<rect x="-10" y="{base - 4}" width="620" height="{620 - base}" fill="{col}"/>' + "".join(g))
        if base == 486:
            # scarecrow among the rows
            out.append('<g fill="#1E182C"><rect x="176" y="380" width="6" height="110"/><rect x="140" y="404" width="80" height="6"/>'
                       '<path d="M 164 398 L 196 398 L 202 448 L 158 448 Z"/><circle cx="179" cy="388" r="11"/><path d="M 160 384 L 198 384 L 188 376 Q 179 360 170 376 Z"/>'
                       '<path d="M 140 408 l -8 6 l 6 2 l -6 6 M 220 408 l 8 6 l -6 2 l 6 6" stroke="#1E182C" stroke-width="3" fill="none"/></g>'
                       '<path d="M 196 398 L 202 448 M 188 380 L 198 384 M 220 404 L 220 410" stroke="#F2B868" stroke-width="1.6" fill="none" opacity="0.7"/>')
    # a moonlit pumpkin at the field's edge
    out.append(f'<ellipse cx="300" cy="566" rx="80" ry="10" fill="#08060E" opacity="0.6"/>')
    out.append(pumpkin(D, 300, 534, 120, 84, ("#C88A4A", "#7A4A2A", "#2A1A14"), stem=("#6E6A44", "#3A3420"), cast=0, leaf=("#4E5A3A", "#2A321E")))
    out.append(f'<path d="M 252 504 Q 300 488 348 504" stroke="#F6C462" stroke-width="2.4" fill="none" opacity="0.7"/>')
    return D.render(out)


# ================================================================ 26. sunflower fields (poster)
def sunflower(D, cx, cy, r, tilt=1.0, rot_=0, seed=0):
    petal = D.lin([(0, "#FFE468"), (0.6, "#F8C030"), (1, "#E0901E")], key="sfp")
    out = [f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot_:.1f}) scale({tilt:.2f} 1)">']
    n = 21
    for k, (dist, rx, ry, col, off) in enumerate(((0.6, 0.15, 0.42, "#D8901E", 0.5), (0.62, 0.16, 0.44, petal, 0))):
        for i in range(n):
            a = (i + off) * 360 / n
            out.append(f'<ellipse cx="0" cy="{-dist * r:.1f}" rx="{rx * r:.1f}" ry="{ry * r:.1f}" transform="rotate({a:.1f})" fill="{col}"/>')
    out.append(f'<circle r="{0.52 * r:.1f}" fill="{D.rad([(0, "#9A6A2A"), (0.5, "#5A3414"), (1, "#2A1808")], key="sfd")}"/>')
    m = int(40 + r * 2.2)
    seeds = []
    for i in range(m):
        a = i * 137.508
        d = 0.47 * r * math.sqrt((i + 0.5) / m)
        seeds.append(f'<circle cx="{d * math.cos(math.radians(a)):.1f}" cy="{d * math.sin(math.radians(a)):.1f}" r="{max(0.8, r * 0.022):.1f}"/>')
    out.append(f'<g fill="#C8903A" opacity="0.7">{"".join(seeds[::2])}</g><g fill="#1E1006" opacity="0.8">{"".join(seeds[1::2])}</g>')
    out.append(f'<circle r="{0.5 * r:.1f}" fill="none" stroke="#F2B640" stroke-width="{max(1, r * 0.03):.1f}" opacity="0.6"/>'
               f'<path d="M {-0.3 * r:.1f} {-0.3 * r:.1f} A {0.42 * r:.1f} {0.42 * r:.1f} 0 0 1 {0.2 * r:.1f} {-0.38 * r:.1f}" stroke="#FFF0C0" stroke-width="{max(1, r * 0.03):.1f}" fill="none" opacity="0.5"/></g>')
    return "".join(out)


def sf_leaf(D, x, y, s, rot_):
    g = D.lin([(0, "#6E8A3A"), (1, "#2E4A1E")], key="sfl")
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot_:.1f}) scale({s / 40:.3f})">'
            f'<path d="M 0 0 C -24 -6 -34 -34 -6 -56 C 0 -60 4 -60 8 -56 C 34 -34 24 -6 0 0 Z" fill="{g}"/>'
            '<path d="M 0 0 L 2 -54 M 1 -18 l -14 -10 M 1 -18 l 14 -10 M 1 -34 l -11 -9 M 1 -34 l 11 -9" stroke="#C8D27A" stroke-width="1.4" fill="none" opacity="0.6"/></g>')


def sunflower_fields_art():
    D = Doc("sff")
    C = Cam(f=300, cx=300, vpy=262, eye=1.6)
    out = [f'<rect width="600" height="444" fill="{D.lin([(0, "#7E9CBC"), (0.42, "#E8C49A"), (0.58, "#F8D898"), (1, "#F8D898")])}"/>']
    out.append(glow(D, 470, 248, 260, "#FFE6A8", 0.9) + '<circle cx="470" cy="246" r="20" fill="#FFF6D8"/>')
    out.append('<g fill="#F6C4A0" opacity="0.5">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="4"/>' for x, y, w in ((140, 150, 90), (100, 162, 50), (380, 132, 70))) + "</g>")
    out.append(birds([(250, 170, 7), (268, 162, 5)], "#5A4A5A", 1.8))
    # far trees, a barn and a windmill
    rnd = random.Random(2)
    out.append(f'<rect x="0" y="250" width="600" height="20" fill="#A8907A"/>')
    out.append("".join(crown(D, x + rnd.uniform(-3, 3), 252 + rnd.uniform(-3, 2), rnd.uniform(7, 11), (["#9A7A6E"], ["#B8967E"], ["#E2C098"]), x, light=(0.8, -0.5), n=2) for x in range(-10, 620, 11) if not 440 < x < 500))
    out.append('<polygon points="150,258 150,240 162,232 174,240 174,258" fill="#A8483A"/><polygon points="174,242 192,244 192,258 174,258" fill="#C8604A"/><polygon points="162,232 174,240 192,244 180,236" fill="#6E5458"/>')
    out.append('<g stroke="#5A4A4E" stroke-width="1.6"><line x1="96" y1="258" x2="100" y2="214"/><line x1="108" y1="258" x2="104" y2="214"/><line x1="98" y1="236" x2="106" y2="236"/></g>'
               '<g transform="translate(102 212)" stroke="#5A4A4E" stroke-width="1.4">' + "".join(f'<line x1="0" y1="0" x2="{10 * math.cos(math.radians(a)):.1f}" y2="{10 * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 30)) + '</g><circle cx="102" cy="212" r="2" fill="#5A4A4E"/>')
    out.append(f'<rect x="0" y="236" width="600" height="30" fill="{D.lin([(0, "#F8D898", 0), (1, "#F8D898", 0.5)])}"/>')
    # the field: rows of heads receding to the horizon, foliage below
    out.append(f'<rect x="0" y="262" width="600" height="190" fill="{D.lin([(0, "#7A8A3A"), (1, "#2E3E1A")])}"/>')
    heads = []
    for X in [-14 + i * 0.9 for i in range(32)]:
        Z = 40
        while Z > 1.6:
            heads.append((Z, X + rnd.uniform(-0.2, 0.2)))
            Z *= rnd.uniform(0.8, 0.9)
    for Z, X in sorted(heads, reverse=True):
        x, y = C(X, 1.75, Z)
        r = C.f * 0.16 / Z
        if r < 1 or x < -30 or x > 630:
            continue
        gx, gy = C(X, 0, Z)
        if r < 7:
            out.append(f'<path d="M {x:.1f} {y:.1f} L {x:.1f} {min(gy, 450):.1f}" stroke="#4E6A2A" stroke-width="{max(0.6, r * 0.25):.1f}"/>'
                       f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#F2B42A"/><circle cx="{x + r * 0.1:.1f}" cy="{y:.1f}" r="{r * 0.45:.1f}" fill="#5A3414"/>')
        else:
            out.append(f'<path d="M {x:.1f} {y:.1f} Q {x - r * 0.2:.1f} {(y + 450) / 2:.1f} {x:.1f} 450" stroke="#4E6A2A" stroke-width="{r * 0.14:.1f}" fill="none"/>')
            out.append(sf_leaf(D, x - r * 0.1, y + r * 2.2, r * 0.8, -60) + sf_leaf(D, x + r * 0.1, y + r * 3.0, r * 0.7, 70))
            out.append(sunflower(D, x, y, r, tilt=0.86, rot_=rnd.uniform(-12, 12), seed=int(x)))
    # hero blooms in the foreground
    for x, y, r, t, ro in ((112, 214, 74, 0.9, -10), (512, 256, 60, 0.84, 14), (330, 330, 46, 0.9, 6)):
        out.append(f'<path d="M {x} {y} Q {x + 10} {(y + 450) / 2} {x - 4} 450" stroke="#4E6A2A" stroke-width="{r * 0.16:.1f}" fill="none"/>')
        out.append(sf_leaf(D, x - 10, y + r * 1.6, r * 0.8, -64) + sf_leaf(D, x + 8, y + r * 2.2, r * 0.7, 58))
        out.append(sunflower(D, x, y, r, tilt=t, rot_=ro))
    return D.render(out)


@design("sunflower-fields")
def sunflower_fields():
    return sunflower_fields_art()


# ================================================================ 27. forage (mushrooms and acorns on a mossy log)
def toadstool(D, x, base, h, w, cap=("#F25A3A", "#C22A1E", "#7A140E"), spots=True, stem="#F6EEE0", lean=0, seed=0):
    g = D.rad([(0, cap[0]), (0.55, cap[1]), (1, cap[2])], cx=0.38, cy=0.3, r=0.75, key=("cap", cap))
    sg = D.lin([(0, "#FFFFFF"), (0.5, stem), (1, "#B8A88E")], 0, 0, 1, 0, key=("stm", stem))
    top = base - h
    tx = x + lean
    out = [f'<path d="M {x - w * 0.13:.1f} {base:.1f} Q {x - w * 0.16:.1f} {base - h * 0.5:.1f} {tx - w * 0.1:.1f} {top + h * 0.12:.1f} L {tx + w * 0.1:.1f} {top + h * 0.12:.1f} Q {x + w * 0.16:.1f} {base - h * 0.5:.1f} {x + w * 0.13:.1f} {base:.1f} Z" fill="{sg}"/>',
           f'<ellipse cx="{tx:.1f}" cy="{top + h * 0.14:.1f}" rx="{w * 0.5:.1f}" ry="{w * 0.1:.1f}" fill="#D8C4A0"/>',
           f'<g stroke="#B09A78" stroke-width="1" opacity="0.8">' + "".join(f'<line x1="{tx:.1f}" y1="{top + h * 0.14:.1f}" x2="{tx + w * 0.48 * math.cos(math.radians(a)):.1f}" y2="{top + h * 0.14 + w * 0.09 * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 20)) + "</g>",
           f'<path d="M {tx - w * 0.5:.1f} {top + h * 0.14:.1f} Q {tx - w * 0.5:.1f} {top - h * 0.3:.1f} {tx:.1f} {top - h * 0.32:.1f} Q {tx + w * 0.5:.1f} {top - h * 0.3:.1f} {tx + w * 0.5:.1f} {top + h * 0.14:.1f} Q {tx:.1f} {top + h * 0.22:.1f} {tx - w * 0.5:.1f} {top + h * 0.14:.1f} Z" fill="{g}"/>']
    if spots:
        rnd = random.Random(seed)
        out.append('<g fill="#FBF3E6">' + "".join(f'<ellipse cx="{tx + rnd.uniform(-0.36, 0.36) * w:.1f}" cy="{top + rnd.uniform(-0.22, 0.06) * h:.1f}" rx="{rnd.uniform(0.03, 0.06) * w:.1f}" ry="{rnd.uniform(0.025, 0.045) * w:.1f}"/>' for _ in range(9)) + "</g>")
    out.append(f'<path d="M {tx - w * 0.3:.1f} {top - h * 0.12:.1f} Q {tx - w * 0.2:.1f} {top - h * 0.27:.1f} {tx:.1f} {top - h * 0.28:.1f}" stroke="#FFFFFF" stroke-width="{max(1.5, w * 0.04):.1f}" fill="none" opacity="0.4" stroke-linecap="round"/>')
    return "".join(out)


def fern(x, y, L, ang, col="#5E7A3A", lit="#9AB04A"):
    out = [f'<g transform="translate({x} {y}) rotate({ang})">', f'<path d="M 0 0 Q {L * 0.1:.1f} {-L * 0.5:.1f} {L * 0.35:.1f} {-L:.1f}" stroke="{col}" stroke-width="2.4" fill="none"/>']
    for i in range(1, 14):
        t = i / 14
        px, py = L * 0.35 * t ** 2 + L * 0.1 * t * (1 - t) * 2, -L * t
        ll = L * 0.22 * (1 - t) + 4
        for sgn in (-1, 1):
            out.append(f'<ellipse cx="{px + sgn * ll / 2:.1f}" cy="{py:.1f}" rx="{ll / 2:.1f}" ry="{max(2, ll * 0.18):.1f}" transform="rotate({sgn * -20} {px:.1f} {py:.1f})" fill="{lit if sgn < 0 else col}"/>')
    out.append("</g>")
    return "".join(out)


@design("forage")
def forage():
    D = Doc("fg")
    out = [f'<rect width="600" height="600" fill="{D.rad([(0, "#566E44"), (0.6, "#33452C"), (1, "#1C2618")], cx=0.3, cy=0.25, r=0.9)}"/>']
    out.append('<g fill="#FFF0C0" opacity="0.07"><polygon points="40,-10 150,-10 420,620 250,620"/><polygon points="190,-10 240,-10 520,620 450,620"/></g>')
    rnd = random.Random(4)
    out.append("".join(f'<circle cx="{rnd.uniform(0, 600):.0f}" cy="{rnd.uniform(0, 360):.0f}" r="{rnd.uniform(3, 9):.1f}" fill="#F6E6A8" opacity="{rnd.uniform(0.06, 0.2):.2f}"/>' for _ in range(30)))
    out.append(word(300, 172, "forage", DMS, 150, "#F6ECD6", max_w=420, sh="#141C10", off=(0, 5)))
    out.append(ruled(232, "WANDER · GATHER · SAVOR", "#E9C46A", size=18, ls=4, line_w=30))
    # ferns behind the log
    out.append(fern(70, 470, 200, -30) + fern(110, 470, 160, -12, "#4E6A30", "#8AA048") + fern(520, 470, 190, 24) + fern(480, 470, 150, 8, "#4E6A30", "#8AA048"))
    # the log, with its cut end showing growth rings
    bark = D.lin([(0, "#8A6040"), (0.4, "#6A4428"), (1, "#2E1C10")])
    out.append(shadow(D, 280, 474, 290, 16, "#0A1006", 0.6))
    out.append(f'<path d="M -12 376 Q 220 366 470 380 L 470 470 Q 220 478 -12 468 Z" fill="{bark}"/>')
    lid = D.clip('<path d="M -12 376 Q 220 366 470 380 L 470 470 Q 220 478 -12 468 Z"/>')
    br = "".join(f'<path d="M {x:.0f} {y:.0f} q {rnd.uniform(30, 60):.0f} {rnd.uniform(-3, 3):.0f} {rnd.uniform(70, 130):.0f} {rnd.uniform(-2, 2):.0f}" stroke="{rnd.choice(["#2A1A0E", "#9A7050"])}"/>'
                 for x, y in [(rnd.uniform(-60, 440), rnd.uniform(380, 470)) for _ in range(40)])
    out.append(f'<g {lid}><g fill="none" stroke-width="2" opacity="0.6">{br}</g></g>')
    out.append(f'<ellipse cx="470" cy="425" rx="28" ry="46" fill="{D.rad([(0, "#E8C890"), (0.7, "#C89A60"), (1, "#8A5A30")])}"/>'
               + "".join(f'<ellipse cx="{470 + k * 0.6:.1f}" cy="425" rx="{28 - k * 4.5:.1f}" ry="{46 - k * 7.5:.1f}" fill="none" stroke="#9A6A3A" stroke-width="1.3" opacity="0.8"/>' for k in range(1, 6))
               + '<ellipse cx="470" cy="425" rx="28" ry="46" fill="none" stroke="#4A2E18" stroke-width="5"/><path d="M 470 425 l 18 -22" stroke="#7A4A22" stroke-width="1.4"/>')
    # moss along the top of the log
    moss = []
    for i in range(170):
        x = rnd.uniform(-10, 450)
        y = 374 - (x / 470) * -6 + rnd.uniform(-8, 10)
        moss.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(3, 7):.1f}" fill="{rnd.choice(["#4E6A2A", "#6E8A3A", "#8AA44A", "#A8BC5A"])}"/>')
    out.append("".join(moss))
    # shelf fungi on the side of the log
    for x, y, w in ((70, 430, 46), (112, 446, 38), (60, 452, 30)):
        out.append("".join(f'<path d="M {x - w * f:.1f} {y:.1f} A {w * f:.1f} {w * f * 0.55:.1f} 0 0 1 {x + w * f:.1f} {y:.1f} Z" fill="{c}"/>'
                           for f, c in ((1, "#7A4A2A"), (0.8, "#C9A070"), (0.62, "#6E5A44"), (0.44, "#E8D4B0"), (0.28, "#9A6A3A"))))
    # mushrooms on top: fly agarics, a bolete, a tuft of little ones by the cut end
    out.append(toadstool(D, 170, 382, 96, 104, seed=1) + toadstool(D, 226, 380, 56, 60, seed=2, lean=6))
    out.append(toadstool(D, 330, 384, 70, 96, cap=("#C8925A", "#8A5432", "#4A2A16"), spots=False, stem="#E8D8B8"))
    for i, (x, h) in enumerate(((396, 30), (410, 40), (424, 34), (436, 26), (404, 22))):
        out.append(toadstool(D, x, 386, h, 22, cap=("#F2D29A", "#D8A660", "#9A6A30"), spots=False, lean=(i - 2) * 2))
    # a snail making its way along
    out.append('<path d="M 262 382 q 22 2 40 -2 q 8 -2 10 -8" stroke="#C8B49A" stroke-width="8" fill="none" stroke-linecap="round"/>'
               '<line x1="310" y1="374" x2="316" y2="362" stroke="#C8B49A" stroke-width="2"/><circle cx="316" cy="361" r="2" fill="#4A3A2A"/>'
               f'<circle cx="280" cy="368" r="14" fill="{D.rad([(0, "#F2C890"), (1, "#9A5A2A")], cx=0.4, cy=0.35, r=0.7)}"/>'
               '<path d="M 280 368 m -9 0 a 9 9 0 1 1 9 9 a 6 6 0 1 1 -5 -6 a 3 3 0 1 1 3 3" stroke="#6E3A1A" stroke-width="1.8" fill="none"/>')
    # the forest floor: leaves, acorns, a stray fern
    out.append(f'<rect x="-10" y="466" width="620" height="140" fill="{D.lin([(0, "#3A2A1A"), (1, "#1E140C")])}"/>')
    out.append(leaf_pile(D, 300, 520, 640, 60, 13, n=60, size=(14, 22)))
    for x, y, r_ in ((150, 506, -20), (196, 520, 30), (420, 512, 10), (470, 530, -40), (300, 534, 20)):
        out.append(acorn(D, x, y, 22, r_))
    return D.render(out)


# ================================================================ 28. stick with me (caramel apple)
@design("stick-with-me")
def stick_with_me():
    D = Doc("swm")
    out = [paper(D, "#3E6E70", "#1E3C42", 101, ink="#0A1A1C", op=0.12, wash=["#5E8A86", "#14282C"])]
    rnd = random.Random(5)
    out.append('<g fill="#F2C878">' + "".join(f'<circle cx="{rnd.uniform(20, 580):.0f}" cy="{rnd.uniform(20, 440):.0f}" r="{rnd.uniform(1.2, 2.6):.1f}" opacity="{rnd.uniform(0.2, 0.5):.2f}"/>' for _ in range(40)) + "</g>")
    out.append(glow(D, 300, 300, 220, "#F2C27A", 0.25))
    # parchment square
    out.append(f'<g transform="rotate(-6 300 410)"><rect x="160" y="370" width="290" height="90" fill="#140C08" opacity="0.3" transform="translate(5 6)"/><rect x="160" y="370" width="290" height="90" fill="{D.lin([(0, "#FBF3E2"), (1, "#E2D2B4")])}"/></g>')
    # stick and bow
    out.append(f'<g transform="rotate(4 300 210)"><rect x="293" y="66" width="14" height="150" rx="5" fill="{D.lin([(0, "#F2DCB0"), (0.4, "#D8B47E"), (1, "#9A7444")], 0, 0, 1, 0)}"/>'
               '<g stroke="#B08A54" stroke-width="1" opacity="0.6"><line x1="298" y1="74" x2="298" y2="210"/><line x1="303" y1="90" x2="303" y2="200"/></g></g>')
    cx, cy, r = 300, 300, 118
    out.append(apple(D, cx, cy, r, pal=("#F25A4A", "#C2241E", "#6E0E0E"), leaf=False, seed=3))
    d = (f"M {cx:.1f} {cy - 0.68 * r:.1f} C {cx + 0.3 * r:.1f} {cy - 0.98 * r:.1f} {cx + 1.05 * r:.1f} {cy - 0.92 * r:.1f} {cx + r:.1f} {cy - 0.08 * r:.1f} "
         f"C {cx + 0.96 * r:.1f} {cy + 0.66 * r:.1f} {cx + 0.48 * r:.1f} {cy + 0.98 * r:.1f} {cx:.1f} {cy + 0.86 * r:.1f} "
         f"C {cx - 0.48 * r:.1f} {cy + 0.98 * r:.1f} {cx - 0.96 * r:.1f} {cy + 0.66 * r:.1f} {cx - r:.1f} {cy - 0.08 * r:.1f} "
         f"C {cx - 1.05 * r:.1f} {cy - 0.92 * r:.1f} {cx - 0.3 * r:.1f} {cy - 0.98 * r:.1f} {cx:.1f} {cy - 0.68 * r:.1f} Z")
    cid = D.clip(f'<path d="{d}"/>')
    car = D.rad([(0, "#F6C070"), (0.4, "#D0822E"), (0.8, "#9A4E16"), (1, "#5E2A0A")], cx=0.36, cy=0.28, r=0.8)
    # caramel: a soft wavy edge high on the shoulder, with a few rounded runs
    ye = cy - 0.42 * r
    xs = [cx - 1.2 * r + i * 0.2 * r for i in range(13)]
    d_edge = f"M {xs[0]:.1f} {ye:.1f}"
    for i in range(12):
        x1, x2 = xs[i], xs[i + 1]
        dip = 0.07 * r * (1 if i % 2 else -1) * (1.6 if i in (4, 7) else 1)
        d_edge += f" C {x1 + 0.05 * r:.1f} {ye + dip:.1f} {x2 - 0.05 * r:.1f} {ye + dip:.1f} {x2:.1f} {ye:.1f}"
    cpath = d_edge + f" L {cx + 1.3 * r:.1f} {cy + 1.3 * r:.1f} L {cx - 1.3 * r:.1f} {cy + 1.3 * r:.1f} Z"
    out.append(f'<g {cid}><path d="{cpath}" fill="{car}"/>'
               f'<path d="{d_edge}" stroke="#F8D49A" stroke-width="3" fill="none" opacity="0.55" transform="translate(0 3)"/>'
               f'<path d="M {cx - 0.8 * r:.1f} {cy - 0.12 * r:.1f} Q {cx - 0.92 * r:.1f} {cy + 0.3 * r:.1f} {cx - 0.62 * r:.1f} {cy + 0.6 * r:.1f}" stroke="#FFF0C8" stroke-width="10" fill="none" stroke-linecap="round" opacity="0.5"/>'
               f'<path d="M {cx - 0.42 * r:.1f} {cy - 0.18 * r:.1f} Q {cx - 0.2 * r:.1f} {cy - 0.26 * r:.1f} {cx + 0.1 * r:.1f} {cy - 0.22 * r:.1f}" stroke="#FFF6DC" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.6"/>'
               f'<path d="M {cx + 0.55 * r:.1f} {cy - 0.1 * r:.1f} Q {cx + 0.78 * r:.1f} {cy + 0.2 * r:.1f} {cx + 0.7 * r:.1f} {cy + 0.5 * r:.1f}" stroke="#3A1606" stroke-width="12" fill="none" stroke-linecap="round" opacity="0.25"/></g>')
    # caramel puddle at the foot, chopped nuts round the bottom
    out.append(f'<path d="M {cx - 0.8 * r:.1f} {cy + 0.7 * r:.1f} Q {cx - 1.0 * r:.1f} {cy + 0.9 * r:.1f} {cx - 0.7 * r:.1f} {cy + 0.98 * r:.1f} Q {cx:.1f} {cy + 1.06 * r:.1f} {cx + 0.74 * r:.1f} {cy + 0.98 * r:.1f} Q {cx + 1.14 * r:.1f} {cy + 0.9 * r:.1f} {cx + 0.88 * r:.1f} {cy + 0.64 * r:.1f} Q {cx:.1f} {cy + 1.0 * r:.1f} {cx - 0.86 * r:.1f} {cy + 0.66 * r:.1f} Z" fill="{car}"/>')
    nuts = []
    for _ in range(70):
        a = rnd.uniform(0.15, math.pi - 0.15)
        d = rnd.uniform(0.62, 0.95)
        x, y = cx + math.cos(a) * d * r, cy + math.sin(a) * d * r * 0.95
        k = rnd.uniform(3, 6)
        pts = [(x + k * math.cos(t), y + k * 0.8 * math.sin(t)) for t in (rnd.uniform(0, 1), rnd.uniform(1.6, 2.6), rnd.uniform(3.2, 4.2), rnd.uniform(4.8, 5.8))]
        nuts.append(f'<polygon points="{P(pts)}" fill="{rnd.choice(["#F2D8A4", "#E2BC80", "#C99A5A"])}"/>')
    out.append(f'<g {cid}>' + "".join(nuts) + "</g>")
    # gingham bow on the stick
    gh = gingham(D, "#B4322A", "swmgh")
    out.append(f'<path d="M 304 190 C 268 160 246 186 262 200 C 276 212 296 200 304 192 Z" fill="{gh}" stroke="#8A2018" stroke-width="2"/>'
               f'<path d="M 306 190 C 342 160 364 186 348 200 C 334 212 314 200 306 192 Z" fill="{gh}" stroke="#8A2018" stroke-width="2"/>'
               f'<path d="M 300 196 L 282 236 L 292 234 L 296 244 L 304 198 Z" fill="{gh}" stroke="#8A2018" stroke-width="2"/>'
               f'<path d="M 308 196 L 330 232 L 320 232 L 318 242 L 304 198 Z" fill="{gh}" stroke="#8A2018" stroke-width="2"/>'
               '<ellipse cx="305" cy="194" rx="9" ry="8" fill="#B4322A" stroke="#8A2018" stroke-width="2"/>')
    out.append(maple(D, 432, 420, 22, L_GOLD, 40, spots=2) + maple(D, 170, 430, 18, L_RED, -30))
    # type: one line, two voices
    a_size = fit_size("stick", SERIF_IT, 88, 200)
    b_size = fit_size("WITH ME", BEBAS, 96, 240, 6)
    wa, wb = measure("stick", SERIF_IT, a_size), measure("WITH ME", BEBAS, b_size, 6)
    x0 = 300 - (wa + 20 + wb) / 2
    out.append(text(x0 + 3, 522, "stick", SERIF_IT, a_size, "#0E2024", anchor="start") + text(x0, 518, "stick", SERIF_IT, a_size, "#FBEBD2", anchor="start"))
    out.append(text(x0 + wa + 20, 524, "WITH ME", BEBAS, b_size, "#0E2024", 6, anchor="start") + text(x0 + wa + 20, 518, "WITH ME", BEBAS, b_size, "#F2B94A", 6, anchor="start"))
    return D.render(out)


# ================================================================ 29. boots & blankets (still life)
def boot(D, x, y, s, leather=("#C07A40", "#8A4A24", "#4A2410"), sock=("#F6EDE0", "#B4322A"), dim=0.0):
    light, base, dark = leather
    g = D.lin([(0, light), (0.45, base), (1, dark)], 0, 0, 1, 0.4, key=("lth", leather))
    outline = "M 6 -146 L 46 -146 Q 52 -100 48 -60 Q 50 -30 58 -18 L 58 0 L -70 0 Q -88 -2 -86 -16 Q -84 -34 -60 -40 Q -24 -48 -8 -72 Q 2 -96 6 -146 Z"
    cid = D.clip(f'<path d="{outline}"/>')
    out = [f'<g transform="translate({x} {y}) scale({s})">',
           f'<path d="M 2 -156 Q 26 -170 52 -156 L 50 -140 L 4 -140 Z" fill="{sock[0]}"/>'
           f'<g stroke="{sock[1]}" stroke-width="4"><path d="M 4 -153 Q 26 -164 50 -153"/></g>'
           + "".join(f'<line x1="{x0}" y1="-158" x2="{x0}" y2="-142" stroke="#C8B8A0" stroke-width="1.6"/>' for x0 in range(8, 50, 6)),
           f'<path d="{outline}" fill="{g}"/>',
           f'<g {cid}><path d="M -90 -12 L 70 -12 L 70 4 L -90 4 Z" fill="#2A160A"/><rect x="22" y="-22" width="40" height="24" fill="#3A2010"/>'
           f'<path d="M -84 -16 Q -82 -34 -58 -40 Q -36 -44 -26 -52" stroke="#2A1408" stroke-width="2" fill="none" stroke-dasharray="4 3" opacity="0.7"/>'
           f'<path d="M -84 -14 L 56 -14" stroke="#E8C890" stroke-width="1.6" stroke-dasharray="4 3" opacity="0.6"/>'
           f'<path d="M 30 -146 Q 34 -100 30 -60" stroke="{dark}" stroke-width="2" fill="none" opacity="0.5"/>'
           f'<path d="M -70 -30 Q -60 -40 -40 -40" stroke="#FFF0D0" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.4"/>'
           f'<path d="M 14 -134 Q 18 -110 14 -86" stroke="#FFF0D0" stroke-width="6" fill="none" stroke-linecap="round" opacity="0.3"/></g>']
    eyes = [(-6 + 2 * i, -80 - 14 * i) for i in range(5)]
    lace = []
    for i in range(4):
        (x1, y1), (x2, y2) = eyes[i], eyes[i + 1]
        lace.append(f'<line x1="{x1 + 8:.1f}" y1="{y1:.1f}" x2="{x2 - 4:.1f}" y2="{y2:.1f}"/><line x1="{x1 - 4:.1f}" y1="{y1:.1f}" x2="{x2 + 8:.1f}" y2="{y2:.1f}"/>')
    out.append(f'<g stroke="#F2E2C2" stroke-width="2.6" stroke-linecap="round">{"".join(lace)}</g>')
    out.append("".join(f'<circle cx="{ex - 4:.1f}" cy="{ey:.1f}" r="2.6" fill="#E9C46A"/><circle cx="{ex + 8:.1f}" cy="{ey:.1f}" r="2.6" fill="#E9C46A"/>' for ex, ey in eyes))
    out.append('<path d="M 6 -138 q 16 4 26 26 M 6 -138 q -4 16 -16 26" stroke="#F2E2C2" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
    out.append(f'<path d="M 46 -146 L 52 -162 L 58 -160 L 50 -142" fill="{dark}"/>')
    if dim:
        out.append(f'<path d="{outline}" fill="#1E0E04" opacity="{dim}"/>')
    out.append("</g>")
    return "".join(out)


@design("boots-and-blankets")
def boots_and_blankets():
    D = Doc("bab")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#F2E2C8"), (1, "#DCC2A0")])}"/>']
    out.append('<g fill="#C9A882" opacity="0.18">' + "".join(f'<rect x="{x}" y="0" width="16" height="440"/>' for x in range(10, 600, 46)) + "</g>")
    out.append(grain(111, "#5A3A22", 260, op=0.08))
    out.append(word(300, 152, "BOOTS", ANTON, 128, "#A8432A", max_w=380, ls=12, sh="#E2C6A0", off=(4, 4)))
    out.append(word(300, 232, "& blankets", SERIF_IT, 76, BROWN, max_w=380))
    # wooden floor
    out.append(f'<rect x="-10" y="440" width="620" height="170" fill="{D.lin([(0, "#9A6A42"), (1, "#5A3A22")])}"/>')
    out.append('<g stroke="#3E2414" stroke-width="2" opacity="0.5">' + "".join(f'<line x1="-10" y1="{y}" x2="610" y2="{y}"/>' for y in (470, 506, 548)) + "</g>")
    out.append(wood_grain(5, (-10, 444, 610, 600), "#3E2414", n=16, op=0.3))
    out.append('<rect x="-10" y="436" width="620" height="8" fill="#6E4428"/>')
    # chunky knit blanket, folded, with a mug of cider on top
    knit = knit_pattern(D, "#EADCC4", "#FBF4E6", scale=2.4, key="chunky")
    for k, (x0, y0, w, h) in enumerate(((58, 420, 290, 76), (70, 360, 266, 66))):
        shape = f"M {x0 + 26} {y0} L {x0 + w - 26} {y0} Q {x0 + w + 4} {y0} {x0 + w} {y0 + h / 2} Q {x0 + w - 4} {y0 + h} {x0 + w - 26} {y0 + h} L {x0 + 26} {y0 + h} Q {x0 - 4} {y0 + h} {x0} {y0 + h / 2} Q {x0 + 4} {y0} {x0 + 26} {y0} Z"
        cid = D.clip(f'<path d="{shape}"/>')
        out.append(shadow(D, x0 + w / 2 + 8, y0 + h, w * 0.55, 10, "#2A1406", 0.5))
        out.append(f'<path d="{shape}" fill="#EADCC4"/><g {cid}><rect x="{x0 - 10}" y="{y0 - 10}" width="{w + 20}" height="{h + 20}" fill="{knit}"/>'
                   f'<rect x="{x0 - 10}" y="{y0 - 10}" width="{w + 20}" height="{h + 20}" fill="{D.lin([(0, "#FFFFFF", 0.2), (0.4, "#000", 0), (1, "#3A2410", 0.4)], key="bkshade")}"/>'
                   f'<rect x="{x0 - 10}" y="{y0 - 10}" width="{w + 20}" height="{h + 20}" fill="{D.lin([(0, "#3A2410", 0.3), (0.15, "#000", 0), (0.85, "#000", 0), (1, "#3A2410", 0.35)], 0, 0, 1, 0, key="bkside")}"/></g>')
    out.append('<g stroke="#D8C4A0" stroke-width="3" stroke-linecap="round">' + "".join(f'<line x1="{x}" y1="496" x2="{x + 2}" y2="512"/>' for x in range(84, 330, 9)) + "</g>")
    def mband(l, r, t, b):
        return f'<rect x="{l - 5:.1f}" y="{t + 26}" width="{r - l + 10:.1f}" height="14" fill="#5E6B34"/>'
    out.append(mug(D, 196, 296, 86, 66, glaze=("#E8F0EA", "#B8C8BE", "#6E8478"), liquid="#B8662A", band=mband))
    out.append(cinnamon(D, 214, 300, 246, 254, 9))
    out.append(steam(D, 190, 286, 60, "#FFFFFF", n=2, gap=20, sw=5, op=0.7, seed=3))
    # the boots
    out.append(shadow(D, 440, 490, 130, 10, "#2A1406", 0.55))
    out.append(boot(D, 478, 470, 1.0, dim=0.25))
    out.append(boot(D, 420, 490, 1.06))
    # a small pumpkin and fallen leaves on the floor
    out.append(pumpkin(D, 120, 546, 70, 50, PK_ORANGE, leaf=L_OLIVE))
    out.append(maple(D, 200, 552, 24, L_RED, 160, spots=2) + oak(D, 520, 540, 22, L_GOLD, 60) + maple(D, 250, 556, 18, L_GOLD, -120) + slim_leaf(D, 436, 556, 18, L_ORANGE, 100))
    return D.render(out)


# ================================================================ 30. cat nap season (tabby asleep in a basket by a lantern)
@design("cat-nap-season")
def cat_nap_season():
    D = Doc("cns")
    out = [f'<rect width="600" height="600" fill="{D.rad([(0, "#5A3446"), (0.6, "#341C2A"), (1, "#20101A")], cx=0.65, cy=0.4, r=0.85)}"/>']
    out.append(grain(121, "#F6EDE0", 220, op=0.05))
    # window behind with a crescent moon and falling leaves
    out.append(f'<rect x="70" y="64" width="190" height="170" rx="4" fill="{D.lin([(0, "#1E2448"), (1, "#4A3A6A")])}"/>')
    out.append('<circle cx="206" cy="112" r="24" fill="#F6E2A8"/><circle cx="216" cy="104" r="22" fill="#232A50"/>')
    rnd = random.Random(9)
    out.append('<g fill="#F6EDE0">' + "".join(f'<circle cx="{rnd.uniform(80, 250):.0f}" cy="{rnd.uniform(74, 220):.0f}" r="{rnd.uniform(0.6, 1.6):.1f}"/>' for _ in range(16)) + "</g>")
    out.append(maple(D, 120, 140, 12, L_RED, 40) + maple(D, 170, 190, 10, L_GOLD, -30))
    out.append('<g fill="#EADCC4"><rect x="62" y="56" width="206" height="10"/><rect x="62" y="232" width="206" height="12"/><rect x="62" y="56" width="10" height="186"/><rect x="258" y="56" width="10" height="186"/><rect x="160" y="62" width="8" height="174"/><rect x="66" y="144" width="198" height="7"/></g>')
    # lantern glow
    out.append(glow(D, 470, 240, 300, "#FFB24A", 0.55))
    # rug and floor line
    out.append(f'<rect x="-10" y="372" width="620" height="240" fill="{D.lin([(0, "#4A2A30"), (1, "#24121A")])}"/>')
    out.append(f'<ellipse cx="300" cy="394" rx="290" ry="30" fill="#6E3A30"/><ellipse cx="300" cy="394" rx="270" ry="24" fill="none" stroke="#C88A4A" stroke-width="3" stroke-dasharray="10 6" opacity="0.6"/>')
    # books under the lantern, the lantern itself
    out.append(shadow(D, 470, 384, 80, 9, "#0A0408", 0.6))
    out.append(book(D, 402, 352, 140, 28, "#3E5A6A", "#1E2E38") + book(D, 412, 326, 120, 26, "#B4532A", "#6E2A12"))
    iron = D.lin([(0, "#5A5050"), (0.3, "#8A7E78"), (1, "#2A2424")], 0, 0, 1, 0)
    out.append(f'<rect x="438" y="306" width="64" height="20" rx="4" fill="{iron}"/><ellipse cx="470" cy="306" rx="34" ry="6" fill="#3A3232"/>')
    out.append(glow(D, 470, 252, 90, "#FFE6A0", 0.85))
    out.append(f'<path d="M 446 302 Q 428 252 452 210 L 488 210 Q 512 252 494 302 Z" fill="#FFE6A8" opacity="0.35"/>')
    flame = D.rad([(0, "#FFFFFF"), (0.4, "#FFE9A0"), (1, "#F09A30")], cx=0.5, cy=0.7, r=0.6)
    out.append(f'<path d="M 470 236 C 480 254 480 270 470 280 C 460 270 460 254 470 236 Z" fill="{flame}"/><rect x="466" y="280" width="8" height="10" fill="#6E5A44"/>')
    out.append('<path d="M 446 302 Q 428 252 452 210 L 488 210 Q 512 252 494 302" fill="none" stroke="#FFF6DC" stroke-width="2" opacity="0.6"/>'
               '<path d="M 452 222 Q 440 252 452 290" stroke="#FFFFFF" stroke-width="4" fill="none" opacity="0.5" stroke-linecap="round"/>')
    out.append(f'<rect x="446" y="200" width="48" height="12" rx="3" fill="{iron}"/><path d="M 456 200 L 462 184 L 478 184 L 484 200 Z" fill="{iron}"/>'
               '<path d="M 440 210 Q 470 140 500 210" stroke="#3A3232" stroke-width="3" fill="none"/><g stroke="#3A3232" stroke-width="2.4"><line x1="448" y1="212" x2="440" y2="302"/><line x1="492" y1="212" x2="500" y2="302"/></g>')
    # wicker basket
    seg = D.lin([(0, "#E8BC80"), (0.45, "#C08A4E"), (1, "#6E4420")], key="cseg")
    body = "M 100 300 L 400 300 L 378 384 Q 250 398 122 384 Z"
    cid = D.clip(f'<path d="{body}"/>')
    rows = [f'<rect x="90" y="296" width="320" height="100" fill="#3E2410"/>']
    for x in range(90, 412, 20):
        rows.append(f'<rect x="{x - 2}" y="296" width="4" height="100" fill="#A8743E"/>')
    for i, y in enumerate(range(300, 392, 10)):
        off = 10 if i % 2 else 0
        rows.append("".join(f'<rect x="{x + 3}" y="{y + 1}" width="16" height="8.5" rx="4" fill="{seg}"/>' for x in range(90 - off, 412, 20)))
    out.append(shadow(D, 254, 390, 170, 12, "#0A0408", 0.6))
    out.append(f'<path d="{body}" fill="#5A3416"/><g {cid}>{"".join(rows)}<rect x="90" y="296" width="320" height="100" fill="{cyl(D, "#FFFFFF", "#000000", "#000000", key="cbs")}" opacity="0.25"/></g>')
    # plaid blanket in the basket
    pl = plaid(D, "#5E6B34", "#B4532A", "#E9C46A", "#F6EDE0", "cnspl")
    out.append(f'<path d="M 92 304 Q 110 270 160 268 L 360 266 Q 400 270 410 304 Q 380 316 330 312 Q 300 330 260 314 Q 200 324 160 310 Q 120 322 92 304 Z" fill="{pl}"/>'
               '<path d="M 92 304 Q 120 322 160 310 Q 200 324 260 314 Q 300 330 330 312 Q 380 316 410 304" stroke="#2A1A0A" stroke-width="2" fill="none" opacity="0.4"/>')
    # the cat: grey tabby curled up, head on its paws, tail wrapped round
    fur = D.rad([(0, "#B8B0B4"), (0.55, "#8A8288"), (1, "#4E464E")], cx=0.45, cy=0.25, r=0.8)
    cbody = "M 150 290 C 150 230 220 196 290 198 C 360 200 392 240 384 284 C 360 298 200 300 150 290 Z"
    bid = D.clip(f'<path d="{cbody}"/>')
    stripes = "".join(f'<path d="M {x} {y} q {14 + i % 3 * 3} 18 4 40" />' for i, (x, y) in enumerate(((210, 210), (240, 200), (270, 196), (300, 198), (330, 204), (358, 218), (376, 236))))
    out.append(f'<path d="{cbody}" fill="{fur}"/><g {bid}><g fill="none" stroke="#3E363E" stroke-width="7" stroke-linecap="round" opacity="0.55">{stripes}</g>'
               f'<rect x="140" y="250" width="260" height="50" fill="{D.lin([(0, "#000", 0), (1, "#14101A", 0.4)])}"/></g>')
    out.append('<path d="M 210 206 C 250 192 320 192 360 214" stroke="#FFD8A0" stroke-width="3" fill="none" opacity="0.5" stroke-linecap="round"/>')
    tail = "M 384 270 C 404 300 360 312 300 312 C 240 312 196 308 170 300 C 160 296 162 288 174 288 C 220 296 280 298 330 292 C 360 288 376 282 384 270 Z"
    tid = D.clip(f'<path d="{tail}"/>')
    out.append(f'<path d="{tail}" fill="{fur}"/><g {tid}><g stroke="#3E363E" stroke-width="7" opacity="0.5">' + "".join(f'<line x1="{x}" y1="280" x2="{x - 6}" y2="320"/>' for x in range(190, 390, 22)) + "</g></g>")
    out.append('<ellipse cx="214" cy="296" rx="22" ry="9" fill="#C8C0C4"/><ellipse cx="248" cy="298" rx="20" ry="8" fill="#B8B0B4"/>')
    head = "M 152 286 C 140 260 150 228 186 224 C 222 222 240 248 236 272 C 232 292 206 302 182 300 C 166 298 156 294 152 286 Z"
    hid = D.clip(f'<path d="{head}"/>')
    out.append(f'<polygon points="158,240 158,204 184,228" fill="#7A727A"/><polygon points="162,236 162,214 178,228" fill="#E2A8B0"/>'
               f'<polygon points="206,226 228,198 232,236" fill="#7A727A"/><polygon points="210,226 226,206 228,232" fill="#E2A8B0"/>')
    out.append(f'<path d="{head}" fill="{D.rad([(0, "#C8C0C4"), (0.6, "#948C92"), (1, "#5A5258")], cx=0.45, cy=0.3, r=0.75)}"/>'
               f'<g {hid}><g stroke="#3E363E" stroke-width="4" opacity="0.5" fill="none"><path d="M 186 226 l 0 14"/><path d="M 176 228 l 3 12"/><path d="M 196 227 l -2 12"/></g></g>')
    out.append('<ellipse cx="190" cy="282" rx="22" ry="12" fill="#F2ECE6" opacity="0.9"/>')
    out.append('<path d="M 166 262 q 8 7 16 0 M 196 262 q 8 7 16 0" stroke="#2A2228" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
               '<path d="M 186 274 l 6 0 l -3 4 Z" fill="#D88A94"/><path d="M 189 278 q -4 5 -8 3 M 189 278 q 4 5 8 3" stroke="#2A2228" stroke-width="1.5" fill="none"/>')
    out.append('<g stroke="#F6F0EA" stroke-width="1.6" opacity="0.8" stroke-linecap="round"><path d="M 176 278 l -26 -4 M 176 282 l -26 4"/><path d="M 202 278 l 26 -4 M 202 282 l 26 4"/></g>')
    out.append(f'<g {SERIF_IT} fill="#E9C46A" opacity="0.85"><text x="276" y="196" font-size="32">z</text><text x="298" y="168" font-size="26">z</text><text x="316" y="146" font-size="21">z</text></g>')
    # a ball of yarn rolled away
    yarn = D.rad([(0, "#E07A4A"), (1, "#8A3418")], cx=0.4, cy=0.35, r=0.7)
    out.append(f'<circle cx="548" cy="390" r="22" fill="{yarn}"/>' + "".join(f'<path d="M {548 - 20} {390 + k * 6 - 12} Q 548 {376 + k * 8} {568} {390 + k * 4 - 10}" stroke="#F2A06A" stroke-width="1.6" fill="none" opacity="0.7"/>' for k in range(5))
               + '<path d="M 528 398 Q 480 420 420 404" stroke="#E07A4A" stroke-width="2" fill="none"/>')
    # type
    out.append(word(300, 486, "cat nap", SERIF_IT, 100, "#FBEBD2", max_w=380))
    out.append(word(300, 536, "SEASON", BEBAS, 52, "#E9B54A", max_w=380, ls=18))
    return D.render(out)


# ---------------------------------------------------------------- build
POSTERS = {"apple-picking": ("APPLE PICKING", "FRESH FROM THE ORCHARD", "#3A2418", "#C2482A", "#F6EDE0", "#E9B54A"),
           "sunflower-fields": ("SUNFLOWER FIELDS", "GOLDEN HOUR · EARLY FALL", "#343A1C", "#E9A21E", "#F6EDE0", "#F2C25A")}


def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        if slug in POSTERS:
            name, sub, band, rule, namec, subc = POSTERS[slug]
            poster(COL, slug, name, sub, fn(), band, rule, namec, subc)
        else:
            save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
