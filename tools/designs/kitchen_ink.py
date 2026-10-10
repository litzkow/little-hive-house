"""Kitchen Words, pen-and-ink edition.

Little kitchen sayings drawn like the plates of a vintage cookbook or a letterpress shop sign: warm black ink
on cream paper, nib lines that swell and thin with direction, hatching and cross-hatching that follow each
form, stippled shading, worn letterpress type with hatched drop shades, ribbons, badges and ruled labels.
Each piece allows ONE restrained accent colour (tomato, mustard, sage...) laid in as a watercolour tint
under the ink.

Run from tools/designs:  python3 kitchen_ink.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from gouache import blob, blob_pts, grain, paper, smooth_closed, smooth_open, strokes, wash
from poster import ANTON

COL = "kitchen-words"
INK = "#1E1A16"          # warm black ink
PAPER = "#F3EADA"        # cream stock
FLECK = "#6E5A44"
TOMATO = ("#E07A62", "#C7402D", "#8E2A1C")
MUSTARD = ("#F0C764", "#D9A22E", "#A5741A")
SAGE = ("#B4C29E", "#82966C", "#566A44")
WINE = ("#C2545C", "#8E2434", "#5A1420")
COFFEE = ("#C69A72", "#8E5E3A", "#5E3A22")

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


class Ids:
    def __init__(self, slug):
        self.slug, self.n = slug, 0

    def __call__(self, tag="u"):
        self.n += 1
        return f"kw-{self.slug}-{tag}{self.n}"


# ================================================================ geometry
def _f(v):
    return f"{v:.1f}"


def lerp(a, b, t):
    return a + (b - a) * t


def ss(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def E(cx, cy, rx, ry, a0=0, a1=360, n=None, rot=0):
    """Points on an ellipse arc (degrees, 0 = right, 90 = down)."""
    n = n or max(8, int(abs(a1 - a0) / 8))
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def cr(pts, closed=False, step=2.5):
    """Dense samples along a uniform Catmull-Rom curve (same curve as gouache.smooth_*)."""
    n = len(pts)
    out = []
    segs = n if closed else n - 1
    for i in range(segs):
        p0 = pts[(i - 1) % n] if closed else pts[max(i - 1, 0)]
        p1, p2 = pts[i % n], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed else pts[min(i + 2, n - 1)]
        k = max(2, int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / step))
        for j in range(k):
            t = j / k
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[q] + (-p0[q] + p2[q]) * t + (2 * p0[q] - 5 * p1[q] + 4 * p2[q] - p3[q]) * t2
                                    + (-p0[q] + 3 * p1[q] - 3 * p2[q] + p3[q]) * t3) for q in (0, 1)))
    if not closed:
        out.append(pts[-1])
    return out


def dense(pts, step=2.5):
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        k = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        out += [(lerp(x0, x1, j / k), lerp(y0, y1, j / k)) for j in range(k)]
    return out + [pts[-1]]


def poly(pts, closed=True):
    return "M " + " L ".join(f"{_f(x)} {_f(y)}" for x, y in pts) + (" Z" if closed else "")


def sm(pts):
    return smooth_closed(pts)


def tr(pts, dx=0, dy=0, sx=1, sy=None, ox=0, oy=0, rot=0):
    sy = sx if sy is None else sy
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for x, y in pts:
        x, y = (x - ox) * sx, (y - oy) * sy
        out.append((ox + x * c - y * s + dx, oy + x * s + y * c + dy))
    return out


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


# ================================================================ pen work
def nib(pts, w=2.6, closed=False, smooth=True, taper=(0.3, 0.3), ramp=0.22, cal=0.45, nib_ang=35, seed=1,
        wob=0.12, color=INK, op=1.0, step=2.2):
    """A pen line drawn as a filled shape: it swells and thins with direction (broad-nib feel), tapers at the
    ends and wavers a little, like a dip pen."""
    P = cr(pts, closed, step) if smooth else (dense(pts + [pts[0]], step) if closed else dense(pts, step))
    if len(P) < 2:
        return ""
    rnd = random.Random(seed)
    ph, fq = rnd.uniform(0, 6.3), rnd.uniform(0.03, 0.07)
    L = [0.0]
    for (x0, y0), (x1, y1) in zip(P, P[1:]):
        L.append(L[-1] + math.hypot(x1 - x0, y1 - y0))
    tot = L[-1] or 1
    left, right = [], []
    na = math.radians(nib_ang)
    n = len(P)
    for i, (x, y) in enumerate(P):
        a = P[(i - 1) % n] if (closed or i > 0) else P[0]
        b = P[(i + 1) % n] if (closed or i < n - 1) else P[-1]
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        t = L[i] / tot
        prof = 1.0 if closed else lerp(taper[0], 1, ss(t / ramp)) * lerp(taper[1], 1, ss((1 - t) / ramp))
        dirf = (1 - cal) + cal * abs(math.sin(ang - na))
        ww = max(0.5, w * prof * dirf * (1 + wob * math.sin(ph + L[i] * fq))) / 2
        nx, ny = -math.sin(ang), math.cos(ang)
        left.append((x + nx * ww, y + ny * ww))
        right.append((x - nx * ww, y - ny * ww))
    if closed:
        d = poly(left) + " " + poly(right[::-1])
        return f'<path d="{d}" fill="{color}" fill-rule="evenodd" opacity="{op:.2f}"/>'
    return f'<path d="{poly(left + right[::-1])}" fill="{color}" opacity="{op:.2f}"/>'


def line(x0, y0, x1, y1, w=2.4, seed=1, bow=0.0, **kw):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0), (x1 - x0)
    k = math.hypot(nx, ny) or 1
    return nib([(x0, y0), (mx + nx / k * bow, my + ny / k * bow), (x1, y1)], w, seed=seed, **kw)


def _clip(uid, clip):
    items = clip if isinstance(clip, (list, tuple)) else [clip]
    inner = "".join(c if c.lstrip().startswith("<") else f'<path d="{c}"/>' for c in items)
    return f'<clipPath id="{uid}">{inner}</clipPath>'


def clipped(uid, clip, inner, clip2=None):
    out = _clip(uid, clip)
    if clip2 is not None:
        out += _clip(uid + "b", clip2)
        return out + f'<g clip-path="url(#{uid})"><g clip-path="url(#{uid}b)">{inner}</g></g>'
    return out + f'<g clip-path="url(#{uid})">{inner}</g>'


def hatch(uid, clip, box, ang=45, gap=(6, 6), w=(1.3, 1.3), color=INK, seed=1, op=1.0, span=(0, 1), wob=0.8,
          dark=None, clip2=None, brk=0.12):
    """Parallel pen hatching clipped to a shape. gap/w run from the light side to the `dark` point side."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    D = math.hypot(x1 - x0, y1 - y0) / 2 + 4
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    if dark is not None and (dark[0] - cx) * nx + (dark[1] - cy) * ny < 0:
        nx, ny = -nx, -ny
    rnd = random.Random(seed)
    d = -D
    out = []
    while d <= D:
        u = (d + D) / (2 * D)
        g = lerp(gap[0], gap[1], u)
        if span[0] <= u <= span[1]:
            px, py = cx + nx * d, cy + ny * d
            ww = lerp(w[0], w[1], u) * rnd.uniform(0.8, 1.15)
            s0, s1 = -D, D
            segs = [(s0, s1)]
            if rnd.random() < brk:
                cut = rnd.uniform(-D * 0.6, D * 0.6)
                segs = [(s0, cut - rnd.uniform(2, 6)), (cut + rnd.uniform(2, 6), s1)]
            for p, q in segs:
                bend = rnd.uniform(-wob, wob)
                ax, ay = px + ux * p, py + uy * p
                bx, by = px + ux * q, py + uy * q
                mx, my = (ax + bx) / 2 + nx * bend, (ay + by) / 2 + ny * bend
                out.append(f'<path d="M {_f(ax)} {_f(ay)} Q {_f(mx)} {_f(my)} {_f(bx)} {_f(by)}" stroke-width="{ww:.2f}"/>')
        d += g * rnd.uniform(0.85, 1.15)
    inner = f'<g fill="none" stroke="{color}" stroke-linecap="round" opacity="{op:.2f}">{"".join(out)}</g>'
    return clipped(uid, clip, inner, clip2)


def xhatch(uid, clip, box, ang=45, gap=(6, 6), w=(1.2, 1.2), seed=1, dark=None, span2=(0.45, 1), **kw):
    """Cross-hatching: a full layer plus a crossing layer over the darker part."""
    return (hatch(uid + "a", clip, box, ang, gap, w, seed=seed, dark=dark, **kw)
            + hatch(uid + "c", clip, box, ang + 75, gap, w, seed=seed + 5, dark=dark, span=span2, **kw))


def contour(uid, clip, cx, top, bot, rx, ry, gap=7, w=1.2, color=INK, seed=1, a0=10, a1=170, op=1.0, clip2=None):
    """Curved hatching that wraps round a cylinder (front ellipse arcs stacked down the body)."""
    rnd = random.Random(seed)
    out = []
    y = top
    while y <= bot:
        pts = E(cx, y, rx, ry, a0 + rnd.uniform(-4, 4), a1 + rnd.uniform(-4, 4), 14)
        out.append(f'<path d="{smooth_open(pts)}" stroke-width="{w * rnd.uniform(0.8, 1.15):.2f}"/>')
        y += gap * rnd.uniform(0.85, 1.15)
    inner = f'<g fill="none" stroke="{color}" stroke-linecap="round" opacity="{op:.2f}">{"".join(out)}</g>'
    return clipped(uid, clip, inner, clip2)


def stipple(uid, clip, box, n, seed, light=None, power=1.6, r=(0.7, 1.5), color=INK, op=0.9, spread=None):
    """Pen dots, denser away from the light point."""
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    lx, ly = light or ((x0 + x1) / 2, (y0 + y1) / 2)
    md = spread or max(math.hypot(x - lx, y - ly) for x in (x0, x1) for y in (y0, y1))
    dots = []
    tries = 0
    while len(dots) < n and tries < n * 30:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if light is not None and rnd.random() > min(1, math.hypot(x - lx, y - ly) / md) ** power:
            continue
        dots.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{rnd.uniform(*r):.2f}"/>')
    return clipped(uid, clip, f'<g fill="{color}" opacity="{op:.2f}">{"".join(dots)}</g>')


def tint(uid, d, pal, seed, op=0.92, ang=-80, n=40, length=(14, 36), width=(2, 5), box=None):
    """Watercolour tint laid under the ink: a wash plus a few brush strokes inside the shape."""
    light, base, dark = pal
    out = [f'<g opacity="{op:.2f}">', wash(d, base, seed, layers=3, spread=1.2, opacity=0.5)]
    if n and box:
        out.append(strokes(uid, d, box, [light, dark, base, light], seed, n=n, angle=ang, length=length, width=width,
                           opacity=(0.18, 0.45)))
    out.append("</g>")
    return "".join(out)


def steam(x, y, h, seed, w=2.6, color=INK, amp=9, curls=2.5, op=0.9):
    rnd = random.Random(seed)
    pts = []
    k = 9
    ph = rnd.uniform(0, 6.28)
    for i in range(k + 1):
        t = i / k
        pts.append((x + amp * math.sin(ph + t * curls * math.pi) * (0.4 + 0.6 * t), y - h * t))
    return nib(pts, w, taper=(0.15, 0.1), ramp=0.45, seed=seed, color=color, op=op)


def leaf_pts(x, y, ang, L, W, bend=0.15):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    pts = []
    for t in (0, 0.18, 0.4, 0.62, 0.82, 1.0):
        wv = W * math.sin(math.pi * t) ** 0.8 * (1 - 0.25 * t)
        b = bend * L * math.sin(math.pi * t)
        pts.append((x + ux * L * t + nx * (b + wv), y + uy * L * t + ny * (b + wv)))
    back = []
    for t in (0.82, 0.62, 0.4, 0.18):
        wv = W * math.sin(math.pi * t) ** 0.8 * (1 - 0.25 * t)
        b = bend * L * math.sin(math.pi * t)
        back.append((x + ux * L * t + nx * (b - wv), y + uy * L * t + ny * (b - wv)))
    return pts + back


def leaf(x, y, ang, L, W, seed, fill=None, bend=0.12, w=1.8, vein=True, color=INK, op=0.95):
    pts = leaf_pts(x, y, ang, L, W, bend)
    out = []
    if fill:
        out.append(f'<path d="{sm(pts)}" fill="{fill}" opacity="{op}"/>')
    out.append(nib(pts, w, closed=True, seed=seed, color=color))
    if vein:
        a = math.radians(ang)
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        mid = [(x + ux * L * t + nx * bend * L * math.sin(math.pi * t), y + uy * L * t + ny * bend * L * math.sin(math.pi * t))
               for t in (0.05, 0.4, 0.8)]
        out.append(nib(mid, w * 0.6, seed=seed + 1, color=color))
    return "".join(out)


def sprig(x, y, ang, L, seed, n=6, leafL=22, leafW=7, fill=None, w=1.8, color=INK, spread=50, curve=0.15):
    """A herb sprig: curved stem with paired leaves."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    stem = [(x + ux * L * t + nx * curve * L * math.sin(math.pi * t), y + uy * L * t + ny * curve * L * math.sin(math.pi * t))
            for t in (0, 0.33, 0.66, 1)]
    out = [nib(stem, w * 1.1, seed=seed, color=color, taper=(0.8, 0.3))]
    S = cr(stem)
    for i in range(n):
        t = 0.2 + 0.8 * i / max(1, n - 1)
        px, py = S[min(len(S) - 1, int(t * (len(S) - 1)))]
        k = 1 - 0.4 * t
        for side in (-1, 1):
            if i == n - 1 and side == 1:
                continue
            la = ang + side * spread + rnd.uniform(-8, 8) if i < n - 1 else ang
            out.append(leaf(px, py, la, leafL * k * rnd.uniform(0.85, 1.1), leafW * k, seed + i * 3 + side, fill=fill, w=w, color=color))
    return "".join(out)


def sparkle(x, y, s, color=INK, w=1.8):
    return (line(x - s, y, x + s, y, w, taper=(0.1, 0.1), ramp=0.5, color=color, cal=0)
            + line(x, y - s, x, y + s, w, taper=(0.1, 0.1), ramp=0.5, color=color, cal=0))


def dotrow(x0, x1, y, step, r, color=INK):
    out = []
    x = x0
    while x <= x1 + 0.1:
        out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{r}"/>')
        x += step
    return f'<g fill="{color}">{"".join(out)}</g>'


# ================================================================ lettering
def tx(x, y, s, font, size, fill=INK, ls=0, anchor="middle", extra=""):
    if anchor == "middle" and ls:
        x = x + ls / 2
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}" {font} font-size="{size}"{lsa} fill="{fill}"{extra}>{esc(s)}</text>'


def fit(s, font, size, max_w, ls=0):
    return fit_size(s, font, size, max_w, ls)


def wear_pattern(uid, seed=3, color=PAPER, amt=1.0):
    rnd = random.Random(seed)
    sp = []
    for _ in range(int(34 * amt)):
        x, y = rnd.uniform(0, 70), rnd.uniform(0, 70)
        if rnd.random() < 0.7:
            sp.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{rnd.uniform(0.4, 1.3):.2f}" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
        else:
            sp.append(f'<path d="M {_f(x)} {_f(y)} l {rnd.uniform(2, 6):.1f} {rnd.uniform(-1, 1):.1f}" stroke="{color}" '
                      f'stroke-width="{rnd.uniform(0.5, 1):.1f}" opacity="{rnd.uniform(0.4, 0.8):.2f}"/>')
    return (f'<defs><pattern id="{uid}" width="70" height="70" patternUnits="userSpaceOnUse">'
            f'<g fill="{color}">{"".join(sp)}</g></pattern></defs>')


def worn(uid, x, y, s, font, size, fill=INK, ls=0, anchor="middle", seed=3, wear=PAPER, amt=1.0, extra=""):
    """Solid letterpress type with a little ink wear (paper specks showing through)."""
    t = tx(x, y, s, font, size, fill, ls, anchor, extra)
    return (t + wear_pattern(uid + "p", seed, wear, amt)
            + clipped(uid, tx(x, y, s, font, size, "#000", ls, anchor, extra), f'<rect width="600" height="600" fill="url(#{uid}p)"/>'))


def shade_text(uid, x, y, s, font, size, fill=INK, ls=0, anchor="middle", dx=None, dy=None, gap=3.4, hw=1.3,
               hcolor=INK, halo=PAPER, halo_w=None, seed=3, wear=True, steps=6, hang=-45, extra=""):
    """Letterpress hero type with a hatched drop shade (engraved-sign style)."""
    dx = size * 0.045 if dx is None else dx
    dy = size * 0.045 if dy is None else dy
    halo_w = halo_w or max(2.5, size * 0.035)
    shades = "".join(tx(x + dx * k / steps, y + dy * k / steps, s, font, size, "#000", ls, anchor, extra) for k in range(1, steps + 1))
    box = (0, 0, 600, 600)
    out = [hatch(uid + "h", shades, box, hang, (gap, gap), (hw, hw), color=hcolor, seed=seed, wob=0.3, brk=0)]
    out.append(tx(x, y, s, font, size, halo, ls, anchor, extra + f' stroke="{halo}" stroke-width="{halo_w:.1f}" stroke-linejoin="round"'))
    out.append(worn(uid, x, y, s, font, size, fill, ls, anchor, seed, halo, extra=extra) if wear else tx(x, y, s, font, size, fill, ls, anchor, extra))
    return "".join(out)


def engraved(uid, x, y, s, font, size, color=INK, ls=0, anchor="middle", sw=None, gap=3.0, ang=0, hw=1.1, seed=3,
             fill=PAPER, extra=""):
    """Open letters: an inked outline with fine engraved hatching inside."""
    sw = sw or max(2, size * 0.028)
    t = tx(x, y, s, font, size, "#000", ls, anchor, extra)
    return (tx(x, y, s, font, size, fill, ls, anchor, extra)
            + hatch(uid, t, (0, 0, 600, 600), ang, (gap, gap), (hw, hw), color=color, seed=seed, wob=0.2, brk=0)
            + tx(x, y, s, font, size, "none", ls, anchor, extra + f' stroke="{color}" stroke-width="{sw:.1f}" stroke-linejoin="round"'))


def swash(x0, x1, y, seed, w=3.0, amp=8, color=INK, curl=True):
    """A calligraphic underline flourish."""
    m = (x0 + x1) / 2
    pts = [(x0, y + amp * 0.4), (x0 + (m - x0) * 0.5, y - amp * 0.2), (m, y + amp * 0.3), (m + (x1 - m) * 0.5, y + amp * 0.1),
           (x1, y - amp * 0.8)]
    if curl:
        pts += [(x1 - 6, y - amp * 1.5), (x1 - 12, y - amp * 0.7)]
    return nib(pts, w, taper=(0.1, 0.2), ramp=0.3, seed=seed, color=color, cal=0.6)


def rule_label(uid, cx, y, s, size=18, ls=5, font=MONO, color=INK, gap=14, line_w=48, diamond=True, w=2.2):
    """Small caps label flanked by inked rules with diamond ends."""
    tw = measure(s, font, size, ls)
    xa, xb = cx - tw / 2 - gap, cx + tw / 2 + gap
    my = y - size * 0.35
    out = [tx(cx, y, s, font, size, color, ls),
           line(xa - line_w, my, xa, my, w, seed=7, taper=(0.3, 0.8), cal=0, color=color),
           line(xb, my, xb + line_w, my, w, seed=8, taper=(0.8, 0.3), cal=0, color=color)]
    if diamond:
        for xd in (xa - line_w - 6, xb + line_w + 6):
            out.append(f'<path d="M {_f(xd - 4)} {_f(my)} L {_f(xd)} {_f(my - 4)} L {_f(xd + 4)} {_f(my)} L {_f(xd)} {_f(my + 4)} Z" fill="{color}"/>')
    return "".join(out)


def ribbon(uid, cx, cy, w, h, s, font, size, fill=PAPER, color=INK, ls=0, bend=0, tcolor=None, tail=None, seed=4,
           shade=True, text_dy=None):
    """A banner with swallow-tail ends folded behind; bend > 0 arches it upward. Text follows the arch."""
    tcolor = tcolor or color
    tail = tail or h * 0.9
    x0, x1 = cx - w / 2, cx + w / 2
    top = [(x0, cy - h / 2), (cx, cy - h / 2 - bend), (x1, cy - h / 2)]
    bot = [(x1, cy + h / 2), (cx, cy + h / 2 - bend), (x0, cy + h / 2)]

    def qp(p):
        a, m, b = p
        return f"{_f(a[0])} {_f(a[1])} Q {_f(2 * m[0] - (a[0] + b[0]) / 2)} {_f(2 * m[1] - (a[1] + b[1]) / 2)} {_f(b[0])} {_f(b[1])}"
    band = f"M {qp(top)} L {qp(bot)} Z"
    drop = h * 0.32
    out = []
    for sgn in (-1, 1):
        ex = x0 if sgn < 0 else x1
        ey = cy
        # tail piece behind the band
        tx0 = ex - sgn * h * 0.3
        tx1 = ex + sgn * tail
        pts = [(tx0, ey - h / 2 + drop), (tx1, ey - h / 2 + drop), (tx1 - sgn * h * 0.32, ey + drop), (tx1, ey + h / 2 + drop),
               (tx0, ey + h / 2 + drop)]
        out.append(f'<path d="{poly(pts)}" fill="{fill}"/>')
        if shade:
            out.append(hatch(f"{uid}t{sgn + 1}", poly(pts), (min(tx0, tx1) - 4, ey - h, max(tx0, tx1) + 4, ey + h + drop), 70,
                             (3.6, 3.6), (1.1, 1.1), seed=seed + sgn, wob=0.2, brk=0, color=color))
        out.append(nib(pts, 2.2, closed=True, smooth=False, seed=seed + sgn, color=color))
        # fold triangle
        f = [(ex, ey + h / 2), (tx0, ey + h / 2 + drop), (ex, ey + h / 2 + drop)]
        out.append(f'<path d="{poly(f)}" fill="{color}"/>')
    out.append(f'<path d="{band}" fill="{fill}"/>')
    out.append(nib(cr(top, False, 3) + cr(bot, False, 3), 2.6, closed=True, smooth=False, seed=seed, color=color))
    # text along the arch
    pid = uid + "p"
    ty = text_dy if text_dy is not None else size * 0.34
    mid = [(x0, cy + ty), (cx, cy + ty - bend), (x1, cy + ty)]
    out.append(f'<defs><path id="{pid}" d="M {qp(mid)}"/></defs>')
    lsa = f' letter-spacing="{ls}"' if ls else ""
    out.append(f'<text {font} font-size="{size}"{lsa} fill="{tcolor}" text-anchor="middle"><textPath href="#{pid}" '
               f'startOffset="50%">{esc(s)}</textPath></text>')
    return "".join(out)


def arc_label(uid, s, cx, cy, r, font, size, color=INK, ls=0, top=True):
    if top:
        d = f"M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"
    else:
        d = f"M {cx - r} {cy} A {r} {r} 0 0 0 {cx + r} {cy}"
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return (f'<defs><path id="{uid}" d="{d}" fill="none"/></defs>'
            f'<text {font} font-size="{size}"{lsa} fill="{color}" text-anchor="middle"><textPath href="#{uid}" startOffset="50%">{esc(s)}</textPath></text>')


# ================================================================ ground
def ground(U, seed=5, base=PAPER):
    return paper(U("paper"), base, FLECK, seed, 1.2)


def finish(U, seed=9, op=0.8):
    return grain(U("grain"), INK, seed, op)


def blot(U, cx, cy, rx, ry, pal, seed, op=0.35, rot=0):
    """A soft watercolour blot behind a subject."""
    d = blob(cx, cy, rx, ry, seed, 0.09, 20, rot)
    return (f'<g opacity="{op}">' + wash(d, pal[0], seed, 3, 4, 0.5)
            + strokes(U("bl"), d, (cx - rx, cy - ry, cx + rx, cy + ry), [pal[0], pal[1], pal[0]], seed, n=30, angle=-20,
                      length=(30, 80), width=(4, 10), opacity=(0.15, 0.35)) + "</g>")


def shadow(cx, cy, rx, ry, op=0.12):
    return f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(rx)}" ry="{_f(ry)}" fill="{INK}" opacity="{op}"/>'


def ground_hatch(U, cx, cy, rx, ry, seed, gap=4.2, w=1.1):
    """A little hatched cast shadow under an object."""
    d = blob(cx, cy, rx, ry, seed, 0.05, 16)
    return hatch(U("gh"), d, (cx - rx, cy - ry, cx + rx, cy + ry), 0, (gap, gap), (w, w), seed=seed, wob=0.2)


# ================================================================ drawn objects
def coffee_bean(U, x, y, s, rot, seed, fill=None):
    pts = E(x, y, s, s * 0.68, 0, 360, 20, rot)
    d = sm(pts[:-1])
    a = math.radians(rot)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    crease = [(x - ux * s * 0.85, y - uy * s * 0.85), (x - ux * s * 0.3 + nx * s * 0.18, y - uy * s * 0.3 + ny * s * 0.18),
              (x + ux * s * 0.3 - nx * s * 0.18, y + uy * s * 0.3 - ny * s * 0.18), (x + ux * s * 0.85, y + uy * s * 0.85)]
    out = [f'<path d="{d}" fill="{fill or PAPER}"/>',
           hatch(U("cb"), d, (x - s, y - s, x + s, y + s), rot + 60, (2.6, 2.6), (1, 1), seed=seed, span=(0.5, 1),
                 dark=(x + nx * s, y + ny * s), wob=0.2, brk=0),
           nib(pts[:-1], max(1.8, s * 0.14), closed=True, seed=seed),
           nib(crease, max(1.6, s * 0.12), seed=seed + 1, taper=(0.2, 0.2))]
    return "".join(out)


def mug(U, cx, top, w, h, seed, pal=None, band=None, handle=True, steam_n=3, heart=None, sleeve=None, rimry=None):
    """A straight-sided enamel/ceramic mug in pen and ink, light from the upper left."""
    ry = rimry or w * 0.14
    x0, x1 = cx - w / 2, cx + w / 2
    bot = top + h
    body = [(x0, top)] + [(x0 + 2, top + h * 0.5), (x0 + w * 0.06, bot - ry * 0.4)] + E(cx, bot - ry * 0.4, w / 2 - w * 0.06, ry, 180, 0, 16)[1:-1] + [(x1 - w * 0.06, bot - ry * 0.4), (x1 - 2, top + h * 0.5), (x1, top)] + E(cx, top, w / 2, ry, 0, 180, 16)[1:-1]
    dbody = poly(body)
    out = [shadow(cx + w * 0.12, bot + 4, w * 0.62, ry * 0.7, 0.14)]
    # handle
    if handle:
        hx = x1 - 2
        outer = [(hx, top + h * 0.18), (hx + w * 0.3, top + h * 0.14), (hx + w * 0.4, top + h * 0.45), (hx + w * 0.26, top + h * 0.76), (hx, top + h * 0.8)]
        inner = [(hx, top + h * 0.66), (hx + w * 0.16, top + h * 0.62), (hx + w * 0.22, top + h * 0.44), (hx + w * 0.16, top + h * 0.3), (hx, top + h * 0.3)]
        hd = smooth_open(outer) + " L " + smooth_open(inner[::-1]).replace("M ", "") + " Z"
        hd = poly(cr(outer) + cr(inner[::-1]))
        out.append(f'<path d="{hd}" fill="{pal[1] if pal else PAPER}"/>')
        out.append(hatch(U("mh"), hd, (hx, top, hx + w * 0.45, bot), 80, (3.2, 3.2), (1.1, 1.1), seed=seed + 2, wob=0.2, brk=0))
        out.append(nib(outer, 3.2, seed=seed + 3, taper=(0.6, 0.6)))
        out.append(nib(inner, 2.4, seed=seed + 4, taper=(0.6, 0.6)))
    out.append(f'<path d="{dbody}" fill="{PAPER}"/>')
    if pal:
        out.append(tint(U("mt"), dbody, pal, seed, 0.95, -90, 30, (20, 50), (3, 6), (x0, top, x1, bot)))
    if band:
        by0, by1 = top + h * band[0], top + h * band[1]
        bd = poly(E(cx, by0, w / 2, ry, 0, 180, 16) + E(cx, by1, w / 2, ry, 180, 0, 16))
        out.append(clipped(U("mbc"), dbody, f'<path d="{bd}" fill="{band[2]}"/>'))
    if sleeve:
        out.append(sleeve(dbody))
    # shading: engraved vertical lines toward the right, cross layer at the very edge
    out.append(hatch(U("ms"), dbody, (x0, top - ry, x1, bot + ry), 90, (7, 2.6), (0.9, 1.6), seed=seed, span=(0.52, 1),
                     dark=(x1, top + h / 2), wob=0.4))
    out.append(hatch(U("mx"), dbody, (x0, top - ry, x1, bot + ry), 20, (3.4, 3.4), (1, 1), seed=seed + 1, span=(0.86, 1),
                     dark=(x1, top + h / 2), wob=0.3))
    if heart:
        out.append(heart)
    # rim: opening (dark coffee) + lip
    rim = E(cx, top, w / 2, ry, 0, 360, 36)[:-1]
    inner = E(cx, top + 1.5, w / 2 - 5, ry - 3, 0, 360, 36)[:-1]
    out.append(f'<path d="{sm(rim)}" fill="{PAPER}"/>')
    out.append(f'<path d="{sm(inner)}" fill="{INK}"/>')
    coffee = E(cx, top + ry * 0.35, w / 2 - 9, ry - 5, 0, 360, 30)[:-1]
    out.append(f'<path d="{sm(coffee)}" fill="#5A4636"/>')
    out.append(f'<path d="{smooth_open(E(cx - w * 0.08, top + ry * 0.3, w * 0.22, ry * 0.35, 200, 260, 6))}" stroke="{PAPER}" stroke-width="2" fill="none" opacity="0.6"/>')
    out.append(nib(rim, 2.8, closed=True, seed=seed + 5))
    out.append(nib(body[:1] + body[1:3] + E(cx, bot - ry * 0.4, w / 2 - w * 0.06, ry, 180, 0, 16)[1:-1] + body[-len(E(cx, top, w / 2, ry, 0, 180, 16)[1:-1]) - 3:-len(E(cx, top, w / 2, ry, 0, 180, 16)[1:-1])],
                   3.4, seed=seed + 6, taper=(0.7, 0.7)))
    # highlight
    out.append(nib([(x0 + w * 0.14, top + ry + 8), (x0 + w * 0.13, top + h * 0.5), (x0 + w * 0.15, bot - ry - 6)], 3.2,
                   color=PAPER, seed=seed + 7, op=0.75, cal=0))
    for i in range(steam_n):
        out.append(steam(cx - w * 0.22 + i * w * 0.22, top - ry - 8, h * 0.55 + (i % 2) * 14, seed + 20 + i, 2.6))
    return "".join(out)


# ================================================================ designs (existing twelve, redrawn)
@design("bless-this-mess")
def bless_this_mess(U):
    pal = MUSTARD
    out = [ground(U, 11)]
    out.append(blot(U, 300, 168, 190, 92, pal, 3, 0.22))
    cx, rimY = 300, 150
    rx, ry = 116, 26
    # wooden spoon leaning out the back-left
    out.append('<g transform="translate(0 16)">')
    sp = [(214, 168), (192, 126), (172, 90)]
    out.append(nib(sp, 9, seed=31, taper=(1, 0.8), cal=0.2))
    bowl_sp = E(166, 80, 15, 22, 0, 360, 24, -28)[:-1]
    out.append(f'<path d="{sm(bowl_sp)}" fill="{PAPER}"/>')
    out.append(hatch(U(), sm(bowl_sp), (146, 54, 186, 106), 30, (3, 3), (1, 1), span=(0.5, 1), dark=(176, 94), seed=3))
    out.append(nib(bowl_sp, 2.6, closed=True, seed=32))
    out.append(line(198, 148, 176, 104, 1.6, seed=33, color=PAPER, op=0.7))
    # whisk out the back-right
    hx0, hy0, hx1, hy1 = 352, 140, 422, 70
    for k in range(5):
        off = (k - 2) * 7
        loop = [(hx0 + off * 0.6, hy0 + 30), (hx0 + 18 + off * 1.4, hy0 - 6), (hx1 - 22 + off * 0.5, hy1 + 34 + off * 0.3), (hx1 - 6, hy1 + 12)]
        out.append(nib(loop, 1.8, seed=40 + k, taper=(0.4, 0.6)))
    hd = [(hx1 - 8, hy1 + 14), (hx1 + 2, hy1 - 2), (hx1 + 14, hy1 - 18)]
    out.append(nib(hd, 11, seed=45, taper=(0.9, 1)))
    out.append(line(hx1 - 2, hy1 + 2, hx1 + 9, hy1 - 12, 1.6, seed=46, color=PAPER, op=0.75))
    out.append(f'<circle cx="{hx1 + 16}" cy="{hy1 - 21}" r="4" fill="none" stroke="{INK}" stroke-width="2"/>')
    # flour cloud puffing out of the bowl
    puffs = [(250, 128, 26), (282, 112, 30), (318, 116, 28), (348, 130, 22), (230, 142, 18), (300, 96, 20)]
    for i, (px, py, r) in enumerate(puffs):
        out.append(f'<path d="{blob(px, py, r, r * 0.85, 60 + i, 0.08)}" fill="{PAPER}"/>')
    for i, (px, py, r) in enumerate(puffs):
        pts = blob_pts(px, py, r, r * 0.85, 60 + i, 0.08)
        out.append(nib(pts[8:18], 2.2, seed=70 + i, taper=(0.15, 0.15)))
        out.append(stipple(U(), blob(px, py, r, r * 0.85, 60 + i, 0.08), (px - r, py - r, px + r, py + r), int(r * 2.2), 80 + i,
                           light=(px - r * 0.5, py - r * 0.6), r=(0.5, 1.1), op=0.8))
    rnd = random.Random(5)
    for _ in range(24):
        a = rnd.uniform(200, 340)
        d = rnd.uniform(70, 125)
        out.append(f'<circle cx="{_f(300 + d * math.cos(math.radians(a)) * 1.3)}" cy="{_f(130 + d * math.sin(math.radians(a)) * 0.7)}" r="{rnd.uniform(0.8, 1.8):.1f}" fill="{INK}" opacity="0.7"/>')
    # bowl body (stoneware with mustard bands)
    body = E(cx, rimY, rx, ry, 0, 180, 20) + [(cx - rx + 8, rimY + 50), (cx - 62, rimY + 92), (cx - 40, rimY + 100), (cx + 40, rimY + 100), (cx + 62, rimY + 92), (cx + rx - 8, rimY + 50)]
    bodyfull = [(cx + rx, rimY)] + body[1:20] + [(cx - rx, rimY)] + [(cx - rx + 6, rimY + 48), (cx - 66, rimY + 90), (cx - 40, rimY + 99), (cx + 40, rimY + 99), (cx + 66, rimY + 90), (cx + rx - 6, rimY + 48)]
    bd = sm(bodyfull)
    out.append(shadow(cx + 18, rimY + 104, 128, 12, 0.16))
    out.append(f'<path d="{bd}" fill="{PAPER}"/>')
    for y0, y1 in ((rimY + 38, rimY + 52), (rimY + 60, rimY + 66)):
        band = poly(E(cx, y0, rx, ry * 0.9, 0, 180, 20) + E(cx, y1, rx, ry * 0.9, 180, 0, 20))
        out.append(clipped(U(), bd, tint(U(), band, pal, 7, 1.0, 0, 0)))
    out.append(contour(U(), bd, cx, rimY + 8, rimY + 100, rx - 4, ry * 0.9, 6.5, 1.1, seed=12, a0=8, a1=60))
    out.append(hatch(U(), bd, (cx - rx, rimY, cx + rx, rimY + 104), 90, (16, 3.4), (0.7, 1.4), span=(0.4, 1), dark=(cx + rx, rimY + 50), seed=13))
    out.append(hatch(U(), bd, (cx - rx, rimY, cx + rx, rimY + 104), 30, (4.5, 4), (0.9, 1.0), span=(0.9, 1), dark=(cx + rx * 0.8, rimY + 100), seed=14))
    out.append(nib(bodyfull[19:] + [bodyfull[0]], 3.6, seed=15, taper=(0.6, 0.6)))
    # rim (front lip over the cloud base)
    out.append(nib(E(cx, rimY, rx, ry, 0, 180, 24), 3.2, seed=16, taper=(0.5, 0.5)))
    out.append(nib(E(cx, rimY, rx, ry, 180, 360, 24), 2.0, seed=17, taper=(0.5, 0.5)))
    out.append(nib(E(cx, rimY + 4, rx - 6, ry - 4, 15, 165, 20), 1.4, seed=18, taper=(0.2, 0.2)))
    out.append(nib([(cx - rx + 22, rimY + 34), (cx - rx + 26, rimY + 60), (cx - rx + 48, rimY + 84)], 3.4, color=PAPER, op=0.85, seed=19, cal=0))
    # cracked egg in front right
    ex, ey = 446, 236
    shell = [(ex - 30, ey - 6), (ex - 22, ey - 14), (ex - 14, ey - 4), (ex - 6, ey - 16), (ex + 4, ey - 6), (ex + 12, ey - 15), (ex + 20, ey - 5), (ex + 30, ey - 10)]
    cup = shell + E(ex, ey - 8, 30, 30, 10, 170, 16)[::-1][1:-1]
    cup = [(ex + 30, ey - 10)] + E(ex, ey - 8, 30, 30, 5, 175, 16)[1:-1] + [(ex - 30, ey - 6)] + shell[1:-1]
    out.append(shadow(ex + 6, ey + 24, 34, 6, 0.16))
    out.append(f'<path d="{poly(cup)}" fill="{PAPER}"/>')
    out.append(hatch(U(), poly(cup), (ex - 30, ey - 20, ex + 32, ey + 24), 90, (6, 2.6), (0.8, 1.4), span=(0.5, 1), dark=(ex + 30, ey), seed=21))
    out.append(nib(cup + [cup[0]], 2.6, smooth=False, seed=22))
    yolk = blob(ex - 64, ey + 14, 22, 9, 23, 0.1)
    out.append(f'<path d="{blob(ex - 60, ey + 16, 44, 14, 24, 0.12)}" fill="{PAPER}"/>')
    out.append(nib(blob_pts(ex - 60, ey + 16, 44, 14, 24, 0.12), 2.0, closed=True, seed=25))
    out.append(tint(U(), yolk, pal, 26, 1, 0, 0))
    out.append(hatch(U(), yolk, (ex - 86, ey, ex - 42, ey + 26), 30, (2.6, 2.6), (1, 1), span=(0.6, 1), dark=(ex - 50, ey + 22), seed=27))
    out.append(nib(blob_pts(ex - 64, ey + 14, 22, 9, 23, 0.1), 2.4, closed=True, seed=28))
    out.append(f'<ellipse cx="{ex - 70}" cy="{ey + 10}" rx="5" ry="2.4" fill="{PAPER}" opacity="0.9"/>')
    out.append('</g>')
    # lettering
    out.append(tx(300, 356, "bless", SERIF_IT, 104, INK))
    out.append(rule_label(U(), 300, 400, "THIS", 22, 10, line_w=70))
    out.append(shade_text(U(), 296, 530, "MESS", ANTON, fit("MESS", ANTON, 128, 400, 8), ls=8, seed=4))
    out.append(finish(U))
    return "".join(out)


@design("but-first-coffee")
def but_first_coffee(U):
    pal = TOMATO
    out = [ground(U, 12)]
    # enamel coffee pot on the right
    cx, top, bot = 410, 150, 368
    rt, rb = 52, 82
    body = [(cx - rt, top), (cx - rt - 8, top + 60), (cx - rb + 4, bot - 30), (cx - rb, bot - 6)] + E(cx, bot - 6, rb, 14, 180, 0, 18)[1:-1] + [(cx + rb, bot - 6), (cx + rb - 4, bot - 30), (cx + rt + 8, top + 60), (cx + rt, top)] + E(cx, top, rt, 10, 0, 180, 14)[1:-1]
    bd = poly(cr(body, True))
    out.append(blot(U, 400, 290, 150, 130, pal, 6, 0.18))
    out.append(shadow(cx + 18, bot + 8, 110, 14, 0.18))
    # spout (gooseneck) from lower-left of the body
    sp_o = [(cx - rb + 12, bot - 50), (cx - rb - 26, bot - 72), (cx - rb - 40, top + 30), (cx - rb - 62, top - 6)]
    sp_i = [(cx - rb - 50, top - 14), (cx - rb - 26, top + 34), (cx - rb - 14, bot - 96), (cx - rb + 16, bot - 84)]
    spd = poly(cr(sp_o) + cr(sp_i))
    out.append(f'<path d="{spd}" fill="{PAPER}"/>')
    out.append(tint(U(), spd, pal, 3, 1, -60, 0))
    out.append(hatch(U(), spd, (cx - rb - 70, top - 20, cx - rb + 20, bot - 40), 30, (3.2, 3.2), (1.1, 1.1), span=(0.5, 1), dark=(cx - rb, bot - 50), seed=4))
    out.append(nib(sp_o, 3.2, seed=5, taper=(0.8, 0.5)))
    out.append(nib(sp_i, 2.6, seed=6, taper=(0.5, 0.8)))
    out.append(nib(E(cx - rb - 56, top - 10, 7, 4.5, 0, 360, 16, -40), 2.4, closed=True, seed=7))
    # handle
    ho = [(cx + rt + 4, top + 16), (cx + rb + 40, top + 6), (cx + rb + 44, top + 110), (cx + rb - 4, bot - 46)]
    hi = [(cx + rb - 8, bot - 70), (cx + rb + 24, top + 104), (cx + rb + 22, top + 26), (cx + rt + 8, top + 34)]
    hd = poly(cr(ho) + cr(hi))
    out.append(f'<path d="{hd}" fill="{PAPER}"/>')
    out.append(tint(U(), hd, pal, 8, 1, -80, 0))
    out.append(hatch(U(), hd, (cx + rt, top, cx + rb + 50, bot), 0, (3.4, 3.4), (1.1, 1.1), span=(0.0, 0.6), dark=(cx + rb + 40, bot), seed=9))
    out.append(nib(ho, 3.4, seed=10, taper=(0.6, 0.6)))
    out.append(nib(hi, 2.4, seed=11, taper=(0.6, 0.6)))
    # body
    out.append(f'<path d="{bd}" fill="{PAPER}"/>')
    out.append(tint(U(), bd, pal, 12, 1, -90, 70, (30, 70), (4, 8), (cx - rb, top, cx + rb, bot)))
    out.append(hatch(U(), bd, (cx - rb, top, cx + rb, bot + 10), 90, (16, 3.4), (0.7, 1.4), span=(0.42, 1), dark=(cx + rb, 260), seed=13))
    out.append(hatch(U(), bd, (cx - rb, top, cx + rb, bot + 10), 25, (4, 3.6), (0.9, 1.1), span=(0.84, 1), dark=(cx + rb, 300), seed=14))
    # white enamel band + chips
    band = poly(E(cx, bot - 46, rb - 6, 13, 0, 180, 18) + E(cx, bot - 30, rb - 3, 14, 180, 0, 18))
    out.append(clipped(U(), bd, f'<path d="{band}" fill="{PAPER}"/>' + hatch(U(), band, (cx - rb, bot - 70, cx + rb, bot), 90, (6, 2.4), (0.8, 1.4), span=(0.55, 1), dark=(cx + rb, bot - 40), seed=15)))
    out.append(nib(E(cx, bot - 46, rb - 6, 13, 10, 170, 16), 1.8, seed=16, taper=(0.2, 0.2)))
    out.append(nib(E(cx, bot - 30, rb - 3, 14, 10, 170, 16), 1.8, seed=17, taper=(0.2, 0.2)))
    for (px, py, r, s) in ((cx - 30, top + 96, 6, 1), (cx + 34, top + 140, 4.5, 2), (cx - rb + 14, bot - 14, 5, 3), (cx + 12, top + 40, 3.5, 4)):
        out.append(f'<path d="{blob(px, py, r, r * 0.8, s, 0.25, 9)}" fill="{INK}"/>')
        out.append(f'<path d="{blob(px - 1, py - 1, r * 0.45, r * 0.35, s + 1, 0.2, 8)}" fill="{PAPER}" opacity="0.6"/>')
    out.append(nib(cr(body, True), 3.4, closed=True, smooth=False, seed=18))
    out.append(nib([(cx - rt + 10, top + 22), (cx - rt + 2, top + 80), (cx - rb + 22, bot - 58)], 4, color=PAPER, op=0.85, seed=19, cal=0))
    # lid
    lid = [(cx - rt - 6, top + 2), (cx - rt + 4, top - 16), (cx - 18, top - 28), (cx + 18, top - 28), (cx + rt - 4, top - 16), (cx + rt + 6, top + 2)]
    ld = sm(lid + E(cx, top + 2, rt + 6, 9, 0, 180, 12)[1:-1])
    out.append(f'<path d="{ld}" fill="{PAPER}"/>')
    out.append(tint(U(), ld, pal, 20, 1, 0, 0))
    out.append(hatch(U(), ld, (cx - rt - 8, top - 30, cx + rt + 8, top + 12), 90, (12, 3.4), (0.7, 1.3), span=(0.5, 1), dark=(cx + rt, top), seed=21))
    out.append(nib(lid + E(cx, top + 2, rt + 6, 9, 0, 180, 12)[1:-1], 3, closed=True, seed=22))
    knob = blob(cx, top - 38, 13, 11, 23, 0.06)
    out.append(f'<path d="{knob}" fill="{INK}"/><ellipse cx="{cx - 4}" cy="{top - 42}" rx="4" ry="2.5" fill="{PAPER}" opacity="0.8"/>')
    # steam from the spout
    for i in range(3):
        out.append(steam(cx - rb - 66 + i * 14, top - 26 - i * 3, 50 + i * 8, 30 + i, 2.6))
    # lettering
    out.append(tx(76, 184, "but", SERIF_IT, 92, INK, anchor="start"))
    out.append(tx(96, 272, "first,", SERIF_IT, 92, INK, anchor="start"))
    out.append(swash(100, 230, 300, 3, 3, 7, curl=False))
    fs = fit("COFFEE", ANTON, 170, 470, 6)
    out.append(shade_text(U(), 300, 528, "COFFEE", ANTON, fs, ls=6, seed=6))
    out.append(finish(U))
    return "".join(out)


@design("home-sweet-home")
def home_sweet_home(U):
    pal = SAGE
    out = [ground(U, 13)]
    out.append(blot(U, 300, 300, 200, 110, pal, 8, 0.2))
    gy = 384
    # trees behind
    for (tx_, ty, r, sd) in ((166, 292, 46, 1), (448, 300, 40, 2)):
        crown = blob(tx_, ty, r, r * 1.08, sd, 0.1, 16)
        out.append(nib([(tx_, gy), (tx_ + 2, ty + 20)], 6, seed=sd, taper=(1, 0.6)))
        out.append(f'<path d="{crown}" fill="{PAPER}"/>')
        out.append(tint(U(), crown, pal, sd, 0.85, -60, 26, (10, 26), (2, 5), (tx_ - r, ty - r, tx_ + r, ty + r)))
        out.append(hatch(U(), crown, (tx_ - r, ty - r, tx_ + r, ty + r), 60, (9, 3.2), (0.8, 1.3), span=(0.45, 1), dark=(tx_ + r, ty + r), seed=sd + 3))
        pts = blob_pts(tx_, ty, r, r * 1.08, sd, 0.1, 16)
        out.append(nib(pts, 2.4, closed=True, seed=sd + 4))
        rnd = random.Random(sd)
        for _ in range(9):
            a = rnd.uniform(0, 6.28); d = rnd.uniform(0.2, 0.75) * r
            px, py = tx_ + d * math.cos(a), ty + d * math.sin(a)
            out.append(nib([(px - 5, py + 2), (px, py - 3), (px + 5, py + 2)], 1.6, seed=rnd.randint(0, 99), taper=(0.2, 0.2)))
    # walls
    gl, gr, apex = 214, 318, (266, 214)
    side_r = 428
    front = [(gl, 292), (apex[0], apex[1] + 8), (gr, 292), (gr, gy), (gl, gy)]
    side = [(gr, 296), (side_r, 304), (side_r, gy - 2), (gr, gy)]
    out.append(shadow(320, gy + 4, 150, 10, 0.18))
    out.append(f'<path d="{poly(front)}" fill="{PAPER}"/>')
    out.append(f'<path d="{poly(side)}" fill="{PAPER}"/>')
    # clapboard on the gable front, hatched shadow side
    for i, y in enumerate(range(304, gy, 11)):
        out.append(line(gl + 3, y, gr - 3, y + 0.5, 1.1, seed=100 + i, taper=(0.6, 0.6), cal=0, op=0.8))
    out.append(hatch(U(), poly(side), (gr, 290, side_r, gy), 90, (3.6, 3.6), (1.2, 1.2), seed=5))
    out.append(hatch(U(), poly(side), (gr, 290, side_r, gy), 0, (6, 6), (0.9, 0.9), seed=6, op=0.8))
    # roof: plane over the side wall, plus the gable bargeboards
    roof = [(apex[0], apex[1]), (412, 224), (446, 306), (gr + 6, 298)]
    rd = poly(roof)
    out.append(f'<path d="{rd}" fill="{PAPER}"/>')
    for k in range(8):
        t = (k + 0.6) / 8
        ax, ay = lerp(apex[0], gr + 6, t), lerp(apex[1], 298, t)
        bx, by = lerp(412, 446, t), lerp(224, 306, t)
        out.append(line(ax, ay, bx, by, 1.4, seed=120 + k, cal=0, taper=(0.5, 0.5)))
        for j in range(1, 9):
            u = (j + (k % 2) * 0.5) / 9
            sx, sy = lerp(ax, bx, u), lerp(ay, by, u)
            out.append(line(sx, sy, sx - 2.5, sy - 10, 1.1, seed=130 + j + k * 9, cal=0, taper=(0.6, 0.6)))
    out.append(hatch(U(), rd, (apex[0], apex[1], 446, 306), 20, (9, 4.2), (0.8, 1.1), span=(0.4, 1), dark=(446, 306), seed=7, op=0.85))
    out.append(nib(roof, 2.8, closed=True, smooth=False, seed=8))
    eave = [(gl - 12, 300), (apex[0], apex[1] - 2), (gr + 10, 300)]
    out.append(nib(eave, 6, smooth=False, seed=9, taper=(0.8, 0.8)))
    # chimney + smoke
    ch = [(368, 232), (368, 196), (390, 196), (390, 226)]
    out.append(f'<path d="{poly(ch)}" fill="{PAPER}"/>')
    out.append(hatch(U(), poly(ch), (368, 190, 390, 236), 90, (3.4, 3.4), (1.2, 1.2), span=(0.5, 1), dark=(390, 210), seed=10))
    for i, y in enumerate((204, 214, 224)):
        out.append(line(368, y, 390, y, 1, seed=140 + i, cal=0))
    out.append(nib(ch, 2.6, smooth=False, seed=11, taper=(1, 1)))
    out.append(f'<rect x="365" y="190" width="28" height="7" fill="{INK}"/>')
    for i, (sx, sy, r) in enumerate(((388, 178, 8), (404, 168, 10), (426, 160, 11), (452, 156, 10))):
        out.append(nib(blob_pts(sx, sy, r, r * 0.8, 150 + i, 0.12, 12)[2:12], 2.2, seed=150 + i, taper=(0.2, 0.3)))
    # door + round gable window + side windows with sage shutters
    door = [(254, gy), (254, 344)] + E(268, 344, 14, 14, 180, 360, 10)[1:-1] + [(282, 344), (282, gy)]
    out.append(f'<path d="{poly(door)}" fill="{INK}"/>')
    out.append(f'<circle cx="277" cy="364" r="1.8" fill="{PAPER}"/>')
    out.append(line(268, 334, 268, gy - 2, 1.2, color=PAPER, seed=12, op=0.6))
    out.append(f'<circle cx="266" cy="262" r="13" fill="{PAPER}"/>')
    out.append(f'<circle cx="266" cy="262" r="9" fill="{INK}"/>')
    out.append(line(266, 253, 266, 271, 1.6, color=PAPER, seed=13, cal=0) + line(257, 262, 275, 262, 1.6, color=PAPER, seed=14, cal=0))
    out.append(nib(E(266, 262, 13, 13, 0, 360, 20)[:-1], 2.4, closed=True, seed=15))
    for wx, sd in ((228, 16), (330, 17), (380, 18)):
        ww, wy0, wy1 = (20, 316, 344) if wx == 228 else (28, 322, 352)
        win = [(wx, wy0), (wx + ww, wy0 + (1 if wx > 300 else 0)), (wx + ww, wy1), (wx, wy1)]
        out.append(f'<path d="{poly(win)}" fill="{INK}"/>')
        out.append(f'<path d="{poly(tr(win, sx=0.42, sy=0.38, ox=wx, oy=wy0, dx=3, dy=3))}" fill="{PAPER}" opacity="0.85"/>')
        out.append(line(wx + ww / 2, wy0, wx + ww / 2, wy1, 1.6, color=PAPER, seed=sd, cal=0) + line(wx, (wy0 + wy1) / 2, wx + ww, (wy0 + wy1) / 2, 1.6, color=PAPER, seed=sd + 1, cal=0))
        for sxo in (-9, ww + 1):
            sh = [(wx + sxo, wy0 - 1), (wx + sxo + 8, wy0 - 1), (wx + sxo + 8, wy1 + 1), (wx + sxo, wy1 + 1)]
            out.append(tint(U(), poly(sh), pal, sd, 1, 0, 0))
            out.append(nib(sh, 1.6, closed=True, smooth=False, seed=sd + 2))
        # window box with herbs
        bx = [(wx - 6, wy1 + 2), (wx + ww + 6, wy1 + 2), (wx + ww + 4, wy1 + 10), (wx - 4, wy1 + 10)]
        out.append(f'<path d="{poly(bx)}" fill="{INK}"/>')
        rnd = random.Random(sd)
        for k in range(6):
            px = wx - 3 + k * (ww + 6) / 5
            out.append(f'<path d="{blob(px, wy1 - 1, 4.5, 3.6, sd + k, 0.2, 8)}" fill="{pal[1]}" stroke="{INK}" stroke-width="1.2"/>')
    out.append(nib(front[:3], 1.8, smooth=False, seed=19))
    out.append(nib([(gl, 296), (gl, gy)], 3, seed=20, taper=(1, 1)))
    out.append(nib([(gr, 300), (gr, gy)], 2.6, seed=21, taper=(1, 1)))
    out.append(nib([(side_r, 306), (side_r, gy - 2)], 2.6, seed=22, taper=(1, 1)))
    # ground line, path and fence
    out.append(nib([(110, gy + 2), (300, gy + 1), (490, gy + 3)], 2.8, seed=23, taper=(0.1, 0.1)))
    for i in range(14):
        x = 104 + i * 9 if i < 7 else 434 + (i - 7) * 9
        if x > 220 and x < 420:
            continue
        out.append(nib([(x, gy + 2), (x, gy - 22), (x + 3, gy - 27), (x + 6, gy - 22), (x + 6, gy + 2)], 1.6, smooth=False, seed=160 + i, taper=(1, 1)))
    out.append(line(102, gy - 16, 168, gy - 16, 1.6, seed=170, cal=0) + line(432, gy - 16, 498, gy - 16, 1.6, seed=171, cal=0))
    rnd = random.Random(3)
    for _ in range(26):
        x = rnd.uniform(110, 490)
        if 250 < x < 290:
            continue
        out.append(line(x, gy + 1, x + rnd.uniform(-3, 3), gy - rnd.uniform(5, 11), 1.3, seed=rnd.randint(0, 999), taper=(1, 0.2), cal=0))
    # lettering
    out.append(engraved(U(), 300, 142, "HOME", CINZEL, fit("HOME", CINZEL, 104, 420, 10), ls=10, sw=3, gap=3.2, hw=1.2))
    out.append(ribbon(U(), 300, 404, 260, 48, "sweet", SERIF_IT, 46, PAPER, ls=1, bend=5, seed=6, text_dy=14, tail=34))
    out.append(worn(U(), 300, 532, "HOME", CINZEL, fit("HOME", CINZEL, 96, 420, 10), ls=10, seed=7))
    out.append(finish(U))
    return "".join(out)


def fork(U, x, y0, y1, seed, w=26):
    """A dinner fork, tines up, from y0 (tine tips) to y1 (handle end)."""
    out = []
    tine_len = 0.26 * (y1 - y0)
    neck = y0 + tine_len + 22
    head = [(x - w / 2, y0 + 4), (x - w / 2, y0 + tine_len), (x - w * 0.3, y0 + tine_len + 14), (x - 4, neck), (x - 5, neck + 40),
            (x - 8, y1 - 60), (x - 10, y1 - 10), (x, y1), (x + 10, y1 - 10), (x + 8, y1 - 60), (x + 5, neck + 40), (x + 4, neck),
            (x + w * 0.3, y0 + tine_len + 14), (x + w / 2, y0 + tine_len), (x + w / 2, y0 + 4)]
    d = sm(head)
    out.append(f'<path d="{d}" fill="{PAPER}"/>')
    out.append(hatch(U(), d, (x - w, y0, x + w, y1), 90, (6, 2.8), (0.8, 1.2), span=(0.5, 1), dark=(x + w, y1), seed=seed))
    out.append(nib(head, 2.6, closed=True, seed=seed + 1))
    # slots between tines (paper cut-outs inked)
    for k in (-1, 0, 1):
        sx = x + k * w * 0.25
        slot = [(sx - 2, y0), (sx + 2, y0), (sx + 2.2, y0 + tine_len - 2), (sx, y0 + tine_len + 2), (sx - 2.2, y0 + tine_len - 2)]
        out.append(f'<path d="{poly(slot)}" fill="{PAPER}"/>')
        out.append(nib([(sx - 2.2, y0 + 2), (sx - 2.2, y0 + tine_len - 2), (sx, y0 + tine_len + 2), (sx + 2.2, y0 + tine_len - 2), (sx + 2.2, y0 + 2)], 1.6, seed=seed + 5 + k))
    out.append(nib([(x - 3, neck + 50), (x - 4, y1 - 40)], 2.6, color=PAPER, seed=seed + 9, op=0.9, cal=0))
    return "".join(out)


def knife(U, x, y0, y1, seed, w=24):
    out = []
    blade_end = y0 + 0.5 * (y1 - y0)
    blade = [(x - w / 2 + 2, y0 + 30), (x - w / 2 + 6, y0 + 4), (x + 2, y0), (x + w / 2, y0 + 20), (x + w / 2, blade_end - 6),
             (x + w / 2 - 6, blade_end), (x - w / 2 + 6, blade_end), (x - w / 2 + 2, blade_end - 10)]
    d = poly(cr(blade, True))
    out.append(f'<path d="{d}" fill="{PAPER}"/>')
    out.append(hatch(U(), d, (x - w, y0, x + w, blade_end), 90, (9, 2.8), (0.7, 1.2), span=(0.55, 1), dark=(x + w, blade_end), seed=seed))
    out.append(nib(blade, 2.6, closed=True, seed=seed + 1, smooth=False))
    out.append(line(x - w / 2 + 6, y0 + 40, x - w / 2 + 6, blade_end - 16, 1.2, seed=seed + 2, cal=0, op=0.7))
    hd = [(x - w / 2 + 3, blade_end), (x + w / 2 - 3, blade_end), (x + w / 2 - 1, y1 - 14), (x, y1), (x - w / 2 + 1, y1 - 14)]
    hdd = sm(hd)
    out.append(f'<path d="{hdd}" fill="{INK}"/>')
    for r_y in (blade_end + 22, y1 - 34):
        out.append(f'<circle cx="{x}" cy="{r_y}" r="2.6" fill="{PAPER}"/>')
    out.append(nib([(x - w / 2 + 6, blade_end + 8), (x - w / 2 + 6, y1 - 20)], 2.2, color=PAPER, seed=seed + 3, op=0.7, cal=0))
    return "".join(out)


@design("good-food-good-mood")
def good_food(U):
    pal = MUSTARD
    out = [ground(U, 14)]
    cx, cy = 300, 300
    R, Rw = 196, 148
    # cast shadow of the plate (hatched crescent to the lower right)
    sh = poly(E(cx + 10, cy + 12, R, R, -40, 140, 40) + E(cx, cy, R, R, 140, -40, 40))
    out.append(hatch(U(), sh, (cx - R, cy - R, cx + R + 20, cy + R + 20), 45, (3.6, 3.6), (1.1, 1.1), seed=2, wob=0.3))
    rim = E(cx, cy, R, R, 0, 360, 72)[:-1]
    out.append(f'<path d="{sm(rim)}" fill="{PAPER}"/>')
    # mustard diner band and a pin line
    band = poly(E(cx, cy, R - 12, R - 12, 0, 360, 72)) + " " + poly(E(cx, cy, R - 26, R - 26, 0, 360, 72)[::-1])
    out.append(f'<path d="{band}" fill="{pal[1]}" fill-rule="evenodd"/>')
    out.append(strokes(U(), band, (cx - R, cy - R, cx + R, cy + R), [pal[0], pal[2], pal[0]], 3, n=60, angle=20, length=(20, 50), width=(2, 4), opacity=(0.2, 0.4)))
    out.append(nib(E(cx, cy, R - 12, R - 12, 0, 360, 72)[:-1], 1.4, closed=True, seed=3))
    out.append(nib(E(cx, cy, R - 26, R - 26, 0, 360, 72)[:-1], 1.4, closed=True, seed=4))
    out.append(nib(E(cx, cy, R - 34, R - 34, 0, 360, 72)[:-1], 1.0, closed=True, seed=5, op=0.8))
    # rim shading at lower right
    ring = poly(E(cx, cy, R, R, 0, 360, 72)) + " " + poly(E(cx, cy, Rw, Rw, 0, 360, 72)[::-1])
    out.append(f'<path id="{U("ringdef")}" d="{ring}" fill="none"/>')
    rd = sm(rim)
    out.append(hatch(U(), rd, (cx - R, cy - R, cx + R, cy + R), 45 + 90, (14, 3.6), (0.6, 1.2), span=(0.62, 1), dark=(cx + R, cy + R), seed=6,
                     clip2=f'<path d="{ring}" fill-rule="evenodd" clip-rule="evenodd"/>'))
    # well: inner shadow on the upper-left edge
    well = E(cx, cy, Rw, Rw, 0, 360, 60)[:-1]
    crescent = poly(E(cx, cy, Rw, Rw, 150, 330, 30) + E(cx + 9, cy + 9, Rw, Rw, 330, 150, 30))
    out.append(hatch(U(), crescent, (cx - Rw, cy - Rw, cx + Rw, cy + Rw), 45, (3.2, 3.2), (1, 1), seed=7, wob=0.2))
    out.append(nib(well, 2.2, closed=True, seed=8))
    out.append(nib(rim, 3.4, closed=True, seed=9))
    # gloss arcs
    out.append(nib(E(cx, cy, R - 6, R - 6, 200, 250, 12), 3, color=PAPER, seed=10, op=0.9, cal=0))
    # herb garnish on the rim, upper right
    out.append(sprig(cx + 92, cy - 150, 145, 70, 11, n=5, leafL=16, leafW=6, fill=PAPER, w=1.6))
    # fork + knife
    out.append(fork(U, 76, 112, 488, 20, 26))
    out.append(knife(U, 524, 104, 490, 30, 24))
    # lettering inside the well
    out.append(shade_text(U(), 300, 266, "GOOD", BEBAS, 100, ls=6, seed=11, dx=3.5, dy=3.5))
    out.append(shade_text(U(), 300, 348, "FOOD", BEBAS, 100, ls=6, seed=12, dx=3.5, dy=3.5))
    out.append(tx(300, 396, "good mood", SERIF_IT, fit("good mood", SERIF_IT, 46, 200), INK))
    out.append(nib([(272, 410), (300, 419), (328, 410)], 2.4, seed=13, taper=(0.2, 0.2)))
    out.append(finish(U))
    return "".join(out)


def toque(U, cx, base, w, seed):
    out = []
    band_h = w * 0.3
    bt = base - band_h
    puffs = [(cx - w * 0.36, bt - w * 0.26, w * 0.26), (cx - w * 0.12, bt - w * 0.4, w * 0.3), (cx + w * 0.16, bt - w * 0.42, w * 0.3),
             (cx + w * 0.38, bt - w * 0.24, w * 0.24)]
    # outline of the puffy crown as a union of arcs
    top = [(cx - w * 0.44, bt + 2)]
    top += E(*puffs[0][:2], puffs[0][2], puffs[0][2], 170, 280, 8)
    top += E(*puffs[1][:2], puffs[1][2], puffs[1][2], 200, 300, 8)
    top += E(*puffs[2][:2], puffs[2][2], puffs[2][2], 240, 340, 8)
    top += E(*puffs[3][:2], puffs[3][2], puffs[3][2], 260, 370, 8)
    top += [(cx + w * 0.44, bt + 2)]
    crown = poly(cr(top) + [(cx + w * 0.42, bt + 6), (cx - w * 0.42, bt + 6)])
    out.append(f'<path d="{crown}" fill="{PAPER}"/>')
    out.append(hatch(U(), crown, (cx - w * 0.6, bt - w * 0.8, cx + w * 0.7, bt + 8), 60, (12, 3.2), (0.7, 1.2), span=(0.5, 1), dark=(cx + w * 0.6, bt), seed=seed))
    # pleat folds
    for k, fx in enumerate((-0.28, -0.08, 0.12, 0.3)):
        x0 = cx + fx * w
        out.append(nib([(x0 + 6, bt - w * 0.34), (x0 - 2, bt - w * 0.16), (x0 + 2, bt + 2)], 1.8, seed=seed + k, taper=(0.1, 0.8)))
    out.append(nib(cr(top), 3.2, smooth=False, seed=seed + 5, taper=(0.8, 0.8)))
    # band
    band = [(cx - w * 0.44, bt), (cx + w * 0.44, bt), (cx + w * 0.42, base), (cx - w * 0.42, base)]
    bd = poly(cr([(cx - w * 0.44, bt), (cx, bt + 6), (cx + w * 0.44, bt)]) + cr([(cx + w * 0.42, base), (cx, base + 8), (cx - w * 0.42, base)]))
    out.append(f'<path d="{bd}" fill="{PAPER}"/>')
    for k in range(9):
        x0 = cx - w * 0.38 + k * w * 0.095
        out.append(line(x0, bt + 6, x0 - 1, base + 4, 1.3, seed=seed + 20 + k, cal=0, taper=(0.6, 0.6)))
    out.append(hatch(U(), bd, (cx - w * 0.5, bt, cx + w * 0.5, base + 10), 90, (10, 3.2), (0.7, 1.2), span=(0.55, 1), dark=(cx + w * 0.5, base), seed=seed + 30))
    out.append(nib(cr([(cx - w * 0.44, bt), (cx, bt + 6), (cx + w * 0.44, bt)]) + cr([(cx + w * 0.42, base), (cx, base + 8), (cx - w * 0.42, base)]), 3, closed=True, smooth=False, seed=seed + 31))
    return "".join(out)


def lips(U, cx, cy, s, rot, pal, seed):
    up = [(-1, 0), (-0.6, -0.36), (-0.24, -0.42), (0, -0.26), (0.24, -0.44), (0.62, -0.36), (1, 0), (0.5, -0.02), (0, 0.04), (-0.5, -0.02)]
    lo = [(-0.94, 0.08), (-0.5, 0.1), (0, 0.13), (0.5, 0.1), (0.94, 0.08), (0.6, 0.42), (0, 0.56), (-0.6, 0.42)]
    out = [f'<g transform="rotate({rot} {cx} {cy})">']
    for k, shape in enumerate((up, lo)):
        pts = [(cx + x * s, cy + y * s) for x, y in shape]
        d = sm(pts)
        out.append(f'<path d="{d}" fill="{pal[1]}"/>')
        out.append(strokes(U(), d, (cx - s, cy - s, cx + s, cy + s), [pal[0], pal[2], pal[0]], seed + k, n=30, angle=-90, length=(4, 12), width=(0.8, 2), opacity=(0.3, 0.7)))
        rnd = random.Random(seed + k)
        for j in range(9):
            x = cx + (-0.75 + j * 0.19) * s
            y0 = cy + (-0.3 if k == 0 else 0.15) * s
            out.append(line(x + rnd.uniform(-2, 2), y0, x + rnd.uniform(-3, 3), y0 + 0.22 * s, 1.2, color=PAPER, seed=seed + j, op=0.7, cal=0))
    out.append("</g>")
    return "".join(out)


@design("kiss-the-cook")
def kiss_the_cook(U):
    pal = TOMATO
    out = [ground(U, 15)]
    out.append(blot(U, 300, 160, 150, 90, pal, 4, 0.16))
    for i, (hx_, hy_, r_) in enumerate(((150, 120, 7), (452, 104, 8), (470, 196, 6))):
        out.append(sparkle(hx_, hy_, r_, w=2))
    out.append(toque(U, 300, 252, 210, 20))
    # lettering
    out.append(shade_text(U(), 292, 412, "KISS", DMS, fit("KISS", DMS, 180, 400, 4), ls=4, seed=7))
    out.append(lips(U, 474, 282, 40, -14, pal, 8))
    out.append(tx(300, 494, "the cook", SERIF_IT, 70, INK))
    out.append(swash(110, 182, 486, 9, 2.6, 6, curl=False))
    out.append(nib([(418, 486), (450, 480), (490, 487)], 2.6, seed=10, taper=(0.2, 0.1), cal=0.6))
    out.append(dotrow(232, 368, 524, 17, 2.2))
    out.append(finish(U))
    return "".join(out)


def wine_glass(U, cx, top, h, seed, pal):
    out = []
    bw = h * 0.36
    bowl_b = top + h * 0.48
    bowl = [(cx - bw * 0.82, top), (cx - bw * 0.96, top + h * 0.18), (cx - bw * 0.8, top + h * 0.36), (cx - bw * 0.3, bowl_b), (cx, bowl_b + 4),
            (cx + bw * 0.3, bowl_b), (cx + bw * 0.8, top + h * 0.36), (cx + bw * 0.96, top + h * 0.18), (cx + bw * 0.82, top)]
    bd = sm(bowl + E(cx, top, bw * 0.82, 7, 0, 180, 10)[1:-1])
    wy = top + h * 0.2
    wine = poly(cr([(cx - bw * 0.95, wy), (cx - bw * 0.8, top + h * 0.36), (cx - bw * 0.3, bowl_b), (cx, bowl_b + 4), (cx + bw * 0.3, bowl_b),
                    (cx + bw * 0.8, top + h * 0.36), (cx + bw * 0.95, wy)]) + E(cx, wy, bw * 0.95, 8, 0, 180, 12)[1:-1])
    foot_y = top + h
    out.append(shadow(cx + 10, foot_y + 3, bw * 0.9, 7, 0.16))
    out.append(f'<path d="{bd}" fill="{PAPER}" opacity="0.6"/>')
    out.append(clipped(U(), bd, tint(U(), wine, pal, seed, 1, -20, 30, (16, 40), (3, 6), (cx - bw, wy, cx + bw, bowl_b + 6))))
    out.append(clipped(U(), bd, hatch(U(), wine, (cx - bw, wy - 8, cx + bw, bowl_b + 6), 90, (9, 3), (0.8, 1.3), span=(0.5, 1), dark=(cx + bw, wy + 30), seed=seed)))
    out.append(nib(E(cx, wy, bw * 0.93, 8, 0, 360, 24)[:-1], 1.6, closed=True, seed=seed + 1))
    out.append(nib(bowl, 2.8, seed=seed + 2, taper=(0.6, 0.6)))
    out.append(nib(E(cx, top, bw * 0.82, 7, 0, 360, 24)[:-1], 2, closed=True, seed=seed + 3))
    out.append(nib([(cx - bw * 0.6, top + 12), (cx - bw * 0.72, top + h * 0.2), (cx - bw * 0.56, top + h * 0.34)], 4, color=PAPER, seed=seed + 4, op=0.9, cal=0))
    # stem + foot
    out.append(nib([(cx - 2, bowl_b + 3), (cx - 3, foot_y - 6)], 2.4, seed=seed + 5, taper=(1, 1)))
    out.append(nib([(cx + 3, bowl_b + 3), (cx + 3, foot_y - 6)], 2.4, seed=seed + 6, taper=(1, 1)))
    foot = E(cx, foot_y - 3, bw * 0.72, 8, 0, 360, 24)[:-1]
    out.append(f'<path d="{sm(foot)}" fill="{PAPER}"/>')
    out.append(hatch(U(), sm(foot), (cx - bw, foot_y - 12, cx + bw, foot_y + 6), 90, (6, 3), (0.8, 1.2), span=(0.5, 1), dark=(cx + bw, foot_y), seed=seed + 7))
    out.append(nib(foot, 2.6, closed=True, seed=seed + 8))
    return "".join(out)


@design("wine-oclock")
def wine_oclock(U):
    pal = WINE
    out = [ground(U, 16)]
    cx, cy, R = 262, 192, 128
    out.append(f'<circle cx="{cx + 8}" cy="{cy + 8}" r="{R + 4}" fill="{INK}" opacity="0.12"/>')
    face = E(cx, cy, R, R, 0, 360, 72)[:-1]
    out.append(f'<path d="{sm(face)}" fill="{PAPER}"/>')
    # bezel: dark ring with engraved lines
    ring = poly(E(cx, cy, R, R, 0, 360, 72)) + " " + poly(E(cx, cy, R - 16, R - 16, 0, 360, 72)[::-1])
    out.append(f'<path d="{ring}" fill="{INK}" fill-rule="evenodd"/>')
    out.append(nib(E(cx, cy, R - 7, R - 7, 200, 260, 14), 2.4, color=PAPER, seed=2, op=0.8, cal=0))
    out.append(nib(E(cx, cy, R - 22, R - 22, 0, 360, 72)[:-1], 1.2, closed=True, seed=3))
    # numerals and minute ticks
    nums = ["XII", "I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
    for i in range(60):
        a = math.radians(-90 + i * 6)
        r0 = R - 24
        r1 = r0 - (8 if i % 5 == 0 else 4)
        out.append(line(cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a), 2.2 if i % 5 == 0 else 1.2, cal=0, seed=i))
    for i, nm in enumerate(nums):
        a = math.radians(-90 + i * 30)
        r = R - 52
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        out.append(f'<text x="{_f(x)}" y="{_f(y + 7)}" text-anchor="middle" {CINZEL} font-size="19" fill="{INK}">{nm}</text>')
    out.append(nib(E(cx, cy, 30, 30, 0, 360, 30)[:-1], 1, closed=True, seed=4, op=0.6))
    # hands at five o'clock
    ha = math.radians(-90 + 150)
    hand = [(cx - 12 * math.cos(ha), cy - 12 * math.sin(ha)), (cx + 40 * math.cos(ha), cy + 40 * math.sin(ha)), (cx + 56 * math.cos(ha), cy + 56 * math.sin(ha))]
    out.append(nib(hand, 7, seed=5, taper=(0.8, 0.2), cal=0))
    out.append(f'<circle cx="{_f(cx + 44 * math.cos(ha))}" cy="{_f(cy + 44 * math.sin(ha))}" r="6" fill="none" stroke="{INK}" stroke-width="2.4"/>')
    out.append(nib([(cx, cy + 14), (cx, cy - 60), (cx, cy - 86)], 5, seed=6, taper=(0.8, 0.15), cal=0))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{INK}"/><circle cx="{cx}" cy="{cy}" r="2.4" fill="{PAPER}"/>')
    # glass in front, lower right
    out.append(wine_glass(U, 432, 172, 186, 7, pal))
    # a few drops
    # lettering
    out.append(tx(300, 440, "wine", SERIF_IT, 96, INK))
    out.append(nib([(120, 424), (160, 418), (194, 426)], 2.6, seed=11, taper=(0.1, 0.2), cal=0.6))
    out.append(nib([(400, 426), (436, 418), (476, 424)], 2.6, seed=12, taper=(0.2, 0.1), cal=0.6))
    out.append(shade_text(U(), 300, 530, "O'CLOCK", BEBAS, fit("O'CLOCK", BEBAS, 118, 440, 8), ls=8, seed=13, dx=4, dy=4))
    out.append(finish(U))
    return "".join(out)


def cyl(cx, top, bot, rt, rb, ry, n=18):
    """A body of revolution seen from slightly above: (fill region pts, open outline pts, rim pts)."""
    region = [(cx - rt, top), (cx - rb, bot)] + E(cx, bot, rb, ry, 180, 0, n)[1:-1] + [(cx + rb, bot), (cx + rt, top)] + E(cx, top, rt, ry, 0, 180, n)[1:-1]
    outline = [(cx - rt, top), (cx - rb, bot)] + E(cx, bot, rb, ry, 180, 0, n)[1:-1] + [(cx + rb, bot), (cx + rt, top)]
    rim = E(cx, top, rt, ry, 0, 360, 2 * n)[:-1]
    return region, outline, rim


def mug2(U, cx, top, w, h, seed, pal=None, wrap=None, steam_n=3, handle=True, fillc=None, coffee=True, ry=None):
    ry = ry or w * 0.13
    rt, rb = w / 2, w / 2 - w * 0.03
    bot = top + h
    region, outline, rim = cyl(cx, top, bot, rt, rb, ry)
    rd = poly(region)
    out = [shadow(cx + w * 0.1, bot + ry * 0.5, w * 0.62, ry * 0.75, 0.15)]
    if handle:
        hx = cx + rt - 3
        outer = [(hx, top + h * 0.16), (hx + w * 0.3, top + h * 0.12), (hx + w * 0.42, top + h * 0.42), (hx + w * 0.3, top + h * 0.76), (hx - 2, top + h * 0.82)]
        inner = [(hx - 2, top + h * 0.66), (hx + w * 0.17, top + h * 0.62), (hx + w * 0.25, top + h * 0.42), (hx + w * 0.17, top + h * 0.28), (hx, top + h * 0.3)]
        hd = poly(cr(outer) + cr(inner))
        out.append(f'<path d="{hd}" fill="{fillc or PAPER}"/>')
        if pal and not wrap:
            out.append(tint(U(), hd, pal, seed, 1, 0, 0))
        out.append(hatch(U(), hd, (hx, top, hx + w * 0.45, bot), 70, (3.4, 3.4), (1.1, 1.1), seed=seed + 2, wob=0.2, brk=0, span=(0.35, 1), dark=(hx + w * 0.4, bot)))
        out.append(nib(outer, 3.2, seed=seed + 3, taper=(0.7, 0.7)))
        out.append(nib(inner, 2.4, seed=seed + 4, taper=(0.7, 0.7)))
    out.append(f'<path d="{rd}" fill="{fillc or PAPER}"/>')
    if pal and not wrap:
        out.append(tint(U(), rd, pal, seed, 0.95, -90, 30, (20, 50), (3, 6), (cx - rt, top, cx + rt, bot)))
    if wrap:
        out.append(wrap(rd, region))
    out.append(hatch(U(), rd, (cx - rt, top - ry, cx + rt, bot + ry), 90, (16, 3.2), (0.7, 1.4), span=(0.45, 1), dark=(cx + rt, top + h / 2), seed=seed))
    out.append(hatch(U(), rd, (cx - rt, top - ry, cx + rt, bot + ry), 30, (4.2, 3.8), (0.9, 1.0), span=(0.9, 1), dark=(cx + rt, bot), seed=seed + 1))
    out.append(f'<path d="{sm(rim)}" fill="{fillc or PAPER}"/>')
    inner = E(cx, top + 1, rt - 5, ry - 3.2, 0, 360, 36)[:-1]
    out.append(f'<path d="{sm(inner)}" fill="{INK}"/>')
    if coffee:
        cof = E(cx + 2, top + ry * 0.4, rt - 9, ry - 5, 0, 360, 30)[:-1]
        out.append(f'<path d="{sm(cof)}" fill="#4A3A2E"/>')
        out.append(nib(E(cx - w * 0.06, top + ry * 0.3, w * 0.2, ry * 0.35, 200, 250, 6), 2, color=PAPER, seed=seed + 8, op=0.6, cal=0))
    out.append(nib(rim, 2.8, closed=True, seed=seed + 5))
    out.append(nib(outline, 3.4, seed=seed + 6, taper=(0.8, 0.8)))
    out.append(nib([(cx - rt + w * 0.13, top + ry + 10), (cx - rt + w * 0.12, top + h * 0.5), (cx - rt + w * 0.14, bot - 8)], 4,
                   color=PAPER, seed=seed + 7, op=0.8, cal=0))
    for i in range(steam_n):
        out.append(steam(cx - w * 0.2 + i * w * 0.2, top - ry - 10, h * 0.5 + (i % 2) * 16, seed + 20 + i, 2.8))
    return "".join(out)


@design("life-happens-coffee-helps")
def life_happens(U):
    pal = COFFEE
    out = [ground(U, 17)]
    out.append(tx(300, 126, "life happens,", SERIF_IT, fit("life happens,", SERIF_IT, 70, 430), INK))
    out.append(engraved(U(), 300, 282, "COFFEE", BEBAS, fit("COFFEE", BEBAS, 176, 470, 8), ls=8, sw=3.2, gap=3.0, hw=1.15, ang=-30))
    # coffee ring stains under the mug
    for k, (rx_, ry_, ox) in enumerate(((84, 22, 0), (70, 18, 46))):
        ring = poly(E(196 + ox, 494 - k * 6, rx_, ry_, 0, 360, 48)) + " " + poly(E(196 + ox, 494 - k * 6, rx_ - 6, ry_ - 3, 0, 360, 48)[::-1])
        out.append(f'<path d="{ring}" fill="{pal[1]}" fill-rule="evenodd" opacity="{0.55 - k * 0.2}"/>')
    def camp(rd, region):
        rnd = random.Random(4)
        dots = "".join(f'<circle cx="{rnd.uniform(120, 270):.1f}" cy="{rnd.uniform(380, 500):.1f}" r="{rnd.uniform(0.7, 1.6):.1f}"/>' for _ in range(90))
        return clipped(U(), rd, f'<g fill="{INK}" opacity="0.8">{dots}</g>' + f'<path d="{poly(E(192, 380, 70, 18, 0, 180, 20) + E(192, 392, 70, 18, 180, 0, 20))}" fill="{INK}"/>')
    out.append(mug2(U, 192, 380, 132, 108, 5, pal=None, wrap=camp))
    # beans, a little arrow and "helps"
    for i, (bx, by, r) in enumerate(((356, 506, 30), (392, 494, -20), (500, 500, 60), (528, 482, 10))):
        if i == 3:
            continue
        out.append(coffee_bean(U, bx, by, 14, r, 40 + i))
    out.append(tx(424, 440, "helps", SERIF_IT, 86, INK))
    out.append(swash(352, 492, 462, 11, 2.8, 7, curl=True))
    out.append(finish(U))
    return "".join(out)


def taco(U, cx, cy, R, seed, pal):
    """A hard-shell taco, side view: half-moon shell, ruffled lettuce spilling over, tomato, cheese."""
    out = []
    ry = R * 0.72
    rnd = random.Random(seed)
    # lettuce mass above the shell edge, ruffled outline
    top = []
    n = 13
    for i in range(n + 1):
        t = i / n
        x = cx - R * 1.0 + 2 * R * t
        h = 30 + 30 * math.sin(math.pi * t) + rnd.uniform(-6, 6)
        top.append((x, cy - h))
    ruff = [(cx - R * 1.06, cy + 6), (cx - R * 1.1, cy - 12)]
    for (x0, y0), (x1, y1) in zip(top, top[1:]):
        for k in range(4):
            u = k / 4
            bump = math.sin(math.pi * u) * rnd.uniform(5, 11) + rnd.uniform(-2.5, 2.5)
            ruff.append((lerp(x0, x1, u) + rnd.uniform(-2, 2), lerp(y0, y1, u) - bump))
    ruff += [top[-1], (cx + R * 1.1, cy - 14), (cx + R * 1.06, cy + 6)]
    ld = poly(cr(ruff))
    out.append(f'<path d="{ld}" fill="{PAPER}"/>')
    out.append(hatch(U(), ld, (cx - R, cy - 80, cx + R, cy + 8), 100, (12, 3.6), (0.7, 1.2), span=(0.55, 1), dark=(cx, cy + 8), seed=seed + 1))
    for (x, y) in top[1:-1]:
        out.append(nib([(cx + (x - cx) * 0.55, cy), ((x + cx) / 2 + (x - cx) * 0.25, (y + cy) / 2), (x, y + 6)], 1.6, seed=seed + int(x), taper=(0.6, 0.1)))
    out.append(nib(cr(ruff), 2.6, smooth=False, seed=seed + 2, taper=(0.3, 0.3)))
    # tomato cubes and cheese shreds on top
    for i in range(6):
        t = (i + 0.6) / 6.6
        x = cx - R * 0.85 + 1.7 * R * t + rnd.uniform(-4, 4)
        y = cy - 26 - 26 * math.sin(math.pi * t) + rnd.uniform(-3, 4)
        cube = [(x - 10, y - 8), (x + 9, y - 10), (x + 11, y + 8), (x - 9, y + 9)]
        out.append(f'<path d="{poly(cube)}" fill="{INK}"/>')
        out.append(f'<path d="{poly(tr(cube, sx=0.42, sy=0.4, ox=x - 6, oy=y - 6))}" fill="{PAPER}" opacity="0.85"/>')
    for i in range(14):
        t = rnd.uniform(0.08, 0.92)
        x = cx - R + 2 * R * t
        y = cy - 22 - 30 * math.sin(math.pi * t) + rnd.uniform(-8, 6)
        a = math.radians(rnd.uniform(-70, 70))
        sh = [(x, y), (x + 16 * math.cos(a), y + 16 * math.sin(a))]
        out.append(nib(sh, 6.4, seed=seed + 70 + i, taper=(0.9, 0.9), cal=0, smooth=False))
        out.append(nib(sh, 3.4, seed=seed + 80 + i, taper=(0.9, 0.9), cal=0, color=pal[0], smooth=False))
    # front shell
    shell = [(cx - R, cy)] + E(cx, cy, R, ry, 180, 0, 40)[1:-1] + [(cx + R, cy)]
    sd = poly(cr(shell + [(cx, cy + 2)], True))
    out.append(f'<path d="{sd}" fill="{PAPER}"/>')
    out.append(tint(U(), sd, pal, seed, 1, -30, 70, (10, 30), (2, 5), (cx - R, cy, cx + R, cy + ry)))
    out.append(stipple(U(), sd, (cx - R, cy, cx + R, cy + ry), 380, seed + 3, light=(cx - R * 0.4, cy + 10), r=(0.6, 1.4), op=0.8))
    for i in range(20):
        a = math.radians(rnd.uniform(15, 165)); d = rnd.uniform(0.25, 0.88)
        out.append(f'<path d="{blob(cx + R * d * math.cos(a), cy + ry * d * math.sin(a), rnd.uniform(2, 4.5), rnd.uniform(1.6, 3), seed + i, 0.25, 8)}" fill="{pal[2]}" opacity="0.85"/>')
    out.append(contour(U(), sd, cx, cy + ry * 0.35, cy + ry * 1.05, R, ry * 0.2, 7, 1.1, seed=seed + 4, a0=15, a1=75))
    out.append(nib(shell + [(cx, cy + 1)], 3.4, closed=True, seed=seed + 5))
    # filling crumbs along the edge, then lettuce lobes drooping over it
    for i in range(30):
        x = cx - R * 0.92 + i * R * 0.063 + rnd.uniform(-2, 2)
        y = cy + rnd.uniform(-3, 3)
        out.append(f'<path d="{blob(x, y, rnd.uniform(5, 7.5), rnd.uniform(4, 5.5), seed + i, 0.25, 8)}" fill="{INK}"/>')
    out.append(nib(E(cx, cy, R - 16, ry - 14, 160, 115, 8), 3.6, color=PAPER, op=0.75, seed=seed + 7, cal=0))
    return "".join(out)


def chili(U, x, y, L, rot, seed, fill=None):
    out = [f'<g transform="rotate({rot} {x} {y})">']
    body = [(x, y - 7), (x + L * 0.3, y - 9), (x + L * 0.7, y - 5), (x + L, y + 6), (x + L * 0.7, y + 4), (x + L * 0.3, y + 7), (x, y + 6)]
    d = sm(body)
    out.append(f'<path d="{d}" fill="{fill or PAPER}"/>')
    out.append(hatch(U(), d, (x, y - 12, x + L, y + 10), 0, (5, 2.6), (0.8, 1.2), span=(0.5, 1), dark=(x + L / 2, y + 10), seed=seed))
    out.append(nib(body, 2.2, closed=True, seed=seed + 1))
    out.append(nib([(x + 6, y - 2), (x + L * 0.4, y - 5)], 2, color=PAPER, seed=seed + 2, cal=0, op=0.9))
    out.append(nib([(x + 2, y), (x - 8, y - 2), (x - 14, y - 10)], 3, seed=seed + 3, taper=(1, 0.5)))
    out.append(nib(E(x + 1, y, 6, 8, 0, 360, 12)[:-1], 2, closed=True, seed=seed + 4))
    out.append("</g>")
    return "".join(out)


@design("taco-tuesday")
def taco_tuesday(U):
    pal = MUSTARD
    out = [ground(U, 18)]
    out.append(blot(U, 300, 210, 210, 100, pal, 4, 0.2))
    out.append(shadow(310, 326, 220, 12, 0.15))
    out.append(f'<g transform="rotate(-7 300 220)">{taco(U, 300, 204, 160, 5, pal)}</g>')
    out.append(chili(U, 70, 334, 78, -12, 6))
    # lime wedge
    lx, ly = 500, 326
    lw = E(lx, ly, 40, 40, 200, 340, 16)
    wd = poly([(lx, ly)] + lw)
    out.append(f'<path d="{wd}" fill="{PAPER}"/>')
    for a in (218, 246, 274, 302, 326):
        out.append(line(lx, ly - 3, lx + 32 * math.cos(math.radians(a)), ly + 32 * math.sin(math.radians(a)), 1.5, seed=a, cal=0))
    out.append(nib(E(lx, ly, 33, 33, 200, 340, 14), 1.5, seed=7, taper=(0.3, 0.3)))
    out.append(nib([(lx, ly)] + lw + [(lx, ly)], 2.8, smooth=False, seed=8, taper=(1, 1)))
    out.append(stipple(U(), wd, (lx - 40, ly - 40, lx + 40, ly), 60, 9, light=(lx, ly - 30), r=(0.5, 1)))
    # lettering
    out.append(shade_text(U(), 300, 452, "TACO", ANTON, fit("TACO", ANTON, 136, 400, 12), ls=12, seed=9))
    out.append(ribbon(U(), 300, 494, 300, 50, "TUESDAY", BEBAS, 40, pal[1], ls=8, bend=-6, tcolor=PAPER, seed=10, text_dy=14, tail=36))
    out.append(finish(U))
    return "".join(out)


def cake_stand(U, cx, y, R, seed):
    out = []
    plate = E(cx, y, R, R * 0.17, 0, 360, 48)[:-1]
    # pedestal
    ped = [(cx - 14, y + 6), (cx - 10, y + 30), (cx - 22, y + 52), (cx - R * 0.5, y + 66), (cx + R * 0.5, y + 66), (cx + 22, y + 52), (cx + 10, y + 30), (cx + 14, y + 6)]
    pd = sm(ped)
    out.append(shadow(cx + 12, y + 68, R * 0.62, 8, 0.16))
    out.append(f'<path d="{pd}" fill="{PAPER}"/>')
    out.append(hatch(U(), pd, (cx - R * 0.5, y, cx + R * 0.5, y + 70), 90, (10, 3), (0.7, 1.3), span=(0.5, 1), dark=(cx + R * 0.5, y + 40), seed=seed))
    out.append(nib(ped, 2.6, closed=True, seed=seed + 1))
    out.append(nib(E(cx, y + 52, 24, 4, 10, 170, 10), 1.6, seed=seed + 2))
    pl = poly(cr(plate, True))
    out.append(f'<path d="{pl}" fill="{PAPER}"/>')
    out.append(hatch(U(), pl, (cx - R, y - 20, cx + R, y + 20), 90, (14, 3.4), (0.7, 1.2), span=(0.55, 1), dark=(cx + R, y), seed=seed + 3, clip2=poly(E(cx, y - 2, R + 4, R * 0.12, 0, 180, 30) + [(cx - R - 4, y + 30), (cx + R + 4, y + 30)])))
    out.append(nib(plate, 2.8, closed=True, seed=seed + 4))
    out.append(nib(E(cx, y + 3, R - 2, R * 0.15, 15, 165, 24), 1.6, seed=seed + 5))
    return "".join(out)


@design("eat-cake")
def eat_cake(U):
    pal = TOMATO
    out = [ground(U, 19)]
    out.append(blot(U, 300, 200, 180, 110, pal, 7, 0.16))
    cx = 300
    out.append(cake_stand(U, cx, 300, 150, 3))
    # cake: two-layer drum with frosting drips
    top, bot, rx, ry = 190, 292, 112, 24
    region, outline, rim = cyl(cx, top, bot, rx, rx, ry)
    rd = poly(region)
    out.append(f'<path d="{rd}" fill="{PAPER}"/>')
    out.append(hatch(U(), rd, (cx - rx, top, cx + rx, bot + ry), 90, (16, 3.2), (0.7, 1.4), span=(0.45, 1), dark=(cx + rx, 240), seed=4))
    out.append(contour(U(), rd, cx, top + 40, bot - 4, rx, ry, 9, 0.9, seed=31, a0=95, a1=172, op=0.7))
    # filling seam
    out.append(nib(E(cx, 248, rx, ry, 8, 172, 20), 2, seed=5, taper=(0.4, 0.4)))
    out.append(nib(E(cx, 252, rx, ry, 8, 172, 20), 1.2, seed=6, taper=(0.4, 0.4), op=0.8))
    # drips
    rnd = random.Random(8)
    drip = []
    for i in range(22):
        a = 180 - i * 180 / 21
        x = cx + rx * math.cos(math.radians(a))
        y = top + ry * math.sin(math.radians(a))
        L = rnd.choice([6, 10, 22, 30, 14, 36]) * math.sin(math.radians(a)) ** 0.5 if 0 < i < 21 else 0
        drip.append((x, y + 4 + (L if i % 2 else 2)))
    icing = [(cx - rx, top)] + drip + [(cx + rx, top)] + E(cx, top, rx, ry, 0, 180, 20)[1:-1]
    idd = poly(cr(icing, True))
    out.append(f'<path d="{idd}" fill="{PAPER}"/>')
    out.append(nib(drip, 2.6, seed=9, taper=(0.5, 0.5)))
    out.append(f'<path d="{sm(rim)}" fill="{PAPER}"/>')
    out.append(stipple(U(), sm(rim), (cx - rx, top - ry, cx + rx, top + ry), 80, 10, light=(cx - 30, top - 10), r=(0.5, 1)))
    out.append(nib(rim, 2.6, closed=True, seed=11))
    out.append(nib(outline, 3.2, seed=12, taper=(0.9, 0.9)))
    # piped rosettes and cherries
    for i in range(7):
        a = math.radians(180 + i * 180 / 6)
        px, py = cx + (rx - 16) * math.cos(a), top + (ry - 6) * math.sin(a) + 2
        for j in range(3):
            out.append(nib(E(px, py - j * 4, 10 - j * 3, 5 - j * 1.4, 0, 340, 10), 1.8, seed=20 + i * 3 + j, taper=(0.3, 0.3)))
    for i in range(5):
        a = math.radians(30 + i * 30)
        px, py = cx + (rx - 18) * math.cos(a), top + (ry - 6) * math.sin(a) + 4
        out.append(nib(E(px, py - 3, 13, 6, 0, 360, 14)[:-1], 1.8, closed=True, seed=40 + i))
    for i, (px, py) in enumerate(((cx - 34, top - 18), (cx + 6, top - 26), (cx + 46, top - 14))):
        out.append(nib([(px, py - 6), (px + 6, py - 26), (px + 14, py - 34)], 2, seed=50 + i, taper=(0.8, 0.4)))
        ch = E(px, py, 14, 13, 0, 360, 16)[:-1]
        out.append(f'<path d="{sm(ch)}" fill="{pal[1]}"/>')
        out.append(hatch(U(), sm(ch), (px - 14, py - 14, px + 14, py + 14), 45, (2.6, 2.6), (1, 1), span=(0.5, 1), dark=(px + 10, py + 10), seed=60 + i))
        out.append(nib(ch, 2.2, closed=True, seed=70 + i))
        out.append(f'<ellipse cx="{px - 5}" cy="{py - 5}" rx="4" ry="2.6" fill="{PAPER}" opacity="0.9"/>')
    out.append(nib([(cx - rx + 14, top + ry + 8), (cx - rx + 13, 270), (cx - rx + 18, bot + 10)], 4, color=PAPER, op=0.8, seed=13, cal=0))
    for i in range(19):
        a = math.radians(176 - i * 172 / 18)
        bx_, by_ = cx + rx * math.cos(a), bot + ry * math.sin(a) - 2
        out.append(f'<circle cx="{_f(bx_)}" cy="{_f(by_)}" r="5.6" fill="{PAPER}" stroke="{INK}" stroke-width="1.8"/>')
    rnd2 = random.Random(3)
    for i in range(14):
        a = rnd2.uniform(0, 6.28)
        out.append(f'<circle cx="{_f(cx + 132 * math.cos(a) * rnd2.uniform(0.9, 1.05))}" cy="{_f(300 + 18 * math.sin(a))}" r="{rnd2.uniform(1, 2):.1f}" fill="{INK}"/>')
    # lettering
    out.append(tx(300, 450, "eat", SERIF_IT, 98, INK))
    out.append(swash(116, 230, 430, 14, 2.6, 6, curl=False))
    out.append(nib([(370, 428), (420, 420), (486, 428)], 2.6, seed=15, taper=(0.2, 0.1), cal=0.6))
    out.append(shade_text(U(), 300, 534, "CAKE", DMS, fit("CAKE", DMS, 104, 420, 14), ls=14, seed=16, dx=3.5, dy=3.5))
    out.append(finish(U))
    return "".join(out)


def candlestick(U, cx, base, h, seed, flame=True):
    out = []
    # candle
    ct = base - h
    cand = [(cx - 8, ct), (cx + 8, ct), (cx + 8, base - 40), (cx - 8, base - 40)]
    out.append(f'<path d="{poly(cand)}" fill="{PAPER}"/>')
    out.append(hatch(U(), poly(cand), (cx - 8, ct, cx + 8, base), 90, (4, 2.6), (0.8, 1.1), span=(0.6, 1), dark=(cx + 8, ct), seed=seed))
    out.append(nib(cand, 2.2, closed=True, smooth=False, seed=seed + 1))
    out.append(nib([(cx - 8, ct + 4), (cx - 6, ct + 12), (cx - 7, ct + 18)], 2, seed=seed + 2))
    if flame:
        fl = [(cx, ct - 30), (cx + 7, ct - 14), (cx + 4, ct - 6), (cx, ct - 4), (cx - 4, ct - 6), (cx - 7, ct - 14)]
        out.append(nib(fl, 1.8, closed=True, seed=seed + 3))
        out.append(f'<path d="{sm(tr(fl, sx=0.45, sy=0.5, ox=cx, oy=ct - 6))}" fill="{INK}"/>')
        for k in range(8):
            a = math.radians(-90 + (k - 3.5) * 22)
            out.append(line(cx + 14 * math.cos(a), ct - 16 + 14 * math.sin(a), cx + 22 * math.cos(a), ct - 16 + 22 * math.sin(a), 1.4, seed=seed + 10 + k, cal=0, op=0.8))
    out.append(nib([(cx, ct), (cx, ct - 5)], 1.6, seed=seed + 4, taper=(1, 1)))
    # brass holder
    hold = [(cx - 14, base - 40), (cx + 14, base - 40), (cx + 9, base - 32), (cx + 6, base - 14), (cx + 22, base - 4), (cx + 22, base), (cx - 22, base), (cx - 22, base - 4), (cx - 6, base - 14), (cx - 9, base - 32)]
    out.append(f'<path d="{poly(hold)}" fill="{PAPER}"/>')
    out.append(hatch(U(), poly(hold), (cx - 22, base - 42, cx + 22, base), 90, (6, 2.6), (0.8, 1.2), span=(0.5, 1), dark=(cx + 22, base), seed=seed + 5))
    out.append(nib(hold, 2.2, closed=True, smooth=False, seed=seed + 6))
    return "".join(out)


def loaf(U, cx, cy, w, h, seed, pal=None):
    out = []
    pts = blob_pts(cx, cy, w / 2, h / 2, seed, 0.03, 22)
    pts = [(x, min(y, cy + h * 0.32)) for x, y in pts]
    d = sm(pts)
    out.append(f'<path d="{d}" fill="{PAPER}"/>')
    if pal:
        out.append(tint(U(), d, pal, seed, 0.9, 0, 0))
    out.append(stipple(U(), d, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), int(w * 2.2), seed, light=(cx - w * 0.2, cy - h * 0.4), r=(0.6, 1.3)))
    out.append(nib(pts, 3, closed=True, seed=seed + 1))
    for k in range(3):
        x = cx - w * 0.22 + k * w * 0.22
        sc = [(x - w * 0.1, cy - h * 0.1), (x, cy - h * 0.34), (x + w * 0.08, cy - h * 0.12)]
        out.append(f'<path d="{sm(sc + [(x, cy - h * 0.2)])}" fill="{PAPER}"/>')
        out.append(nib(sc, 2.4, seed=seed + 5 + k, taper=(0.3, 0.3)))
    return "".join(out)


@design("gather")
def gather(U):
    pal = SAGE
    out = [ground(U, 20)]
    # garland arching over the word
    garland = [(92, 160), (180, 92), (300, 70), (420, 92), (508, 160)]
    G = cr(garland, False, 3)
    out.append(nib(garland, 2.4, seed=2, taper=(0.4, 0.4)))
    rnd = random.Random(4)
    for i in range(1, len(G) - 1, 9):
        px, py = G[i]
        qx, qy = G[i + 1]
        ang = math.degrees(math.atan2(qy - py, qx - px))
        for side in (-1, 1):
            out.append(leaf(px, py, ang + side * rnd.uniform(40, 70), rnd.uniform(18, 26), rnd.uniform(6, 8), i + side,
                            fill=pal[1] if (i // 9 + side) % 3 == 0 else PAPER, w=1.7))
    for i, (bx, by) in enumerate(((210, 98), (300, 82), (390, 98))):
        for j in range(3):
            out.append(f'<circle cx="{bx + (j - 1) * 7}" cy="{by + 10 + (j % 2) * 5}" r="4" fill="{INK}"/>')
    out.append(shade_text(U(), 300, 262, "GATHER", DMS, fit("GATHER", DMS, 124, 450, 6), ls=6, seed=5))
    out.append(rule_label(U(), 300, 302, "AROUND", 18, 8, line_w=64))
    out.append(tx(300, 362, "the table", SERIF_IT, 58, INK))
    # the table
    ty = 474
    top_ = [(70, ty), (530, ty), (530, ty + 16), (70, ty + 16)]
    out.append(f'<path d="{poly(top_)}" fill="{PAPER}"/>')
    out.append(hatch(U(), poly(top_), (70, ty, 530, ty + 16), 0, (3.2, 3.2), (1, 1), seed=6, wob=0.3))
    out.append(nib(top_, 2.6, closed=True, smooth=False, seed=7))
    for lx in (96, 504):
        leg = [(lx - 8, ty + 16), (lx + 8, ty + 16), (lx + 6, 540), (lx - 6, 540)]
        out.append(f'<path d="{poly(leg)}" fill="{INK}"/>')
    apron = [(110, ty + 16), (490, ty + 16), (490, ty + 30), (110, ty + 30)]
    out.append(f'<path d="{poly(apron)}" fill="{PAPER}"/>')
    out.append(nib(apron, 2, closed=True, smooth=False, seed=8))
    # table runner in sage
    run = [(250, ty - 1), (350, ty - 1), (346, ty + 40), (300, ty + 52), (254, ty + 40)]
    out.append(tint(U(), poly(run), pal, 9, 1, 0, 0))
    out.append(nib(run, 1.8, closed=True, smooth=False, seed=10))
    out.append(dotrow(262, 338, ty + 32, 9.5, 1.4))
    # things on the table
    out.append(candlestick(U, 132, ty, 92, 11))
    out.append(candlestick(U, 178, ty, 70, 12))
    out.append(shadow(306, ty - 2, 76, 6, 0.18))
    board = [(232, ty - 10), (380, ty - 10), (380, ty - 1), (232, ty - 1)]
    out.append(f'<path d="{poly(board)}" fill="{PAPER}"/>')
    out.append(hatch(U(), poly(board), (232, ty - 12, 380, ty), 0, (3, 3), (1, 1), seed=13))
    out.append(nib(board, 2.2, closed=True, smooth=False, seed=14))
    out.append(nib([(380, ty - 6), (404, ty - 6)], 4, seed=15, taper=(1, 1)))
    out.append(loaf(U, 300, ty - 34, 116, 54, 16))
    # pitcher of herbs
    px, pt = 452, 400
    region, outline, rim = cyl(px, pt, ty - 4, 22, 30, 7)
    belly = [(px - 22, pt), (px - 34, pt + 34), (px - 30, ty - 4)] + E(px, ty - 4, 30, 7, 180, 0, 10)[1:-1] + [(px + 30, ty - 4), (px + 34, pt + 34), (px + 22, pt)] + E(px, pt, 22, 7, 0, 180, 10)[1:-1]
    bd = sm(belly)
    out.append(sprig(px - 4, pt + 2, -112, 46, 17, n=5, leafL=14, leafW=6, fill=pal[1], w=1.6))
    out.append(sprig(px + 6, pt + 2, -48, 48, 18, n=5, leafL=13, leafW=5, fill=PAPER, w=1.6))
    out.append(nib([(px + 30, pt + 10), (px + 52, pt + 14), (px + 46, pt + 44), (px + 30, pt + 52)], 3, seed=19, taper=(0.7, 0.7)))
    out.append(f'<path d="{bd}" fill="{PAPER}"/>')
    out.append(hatch(U(), bd, (px - 34, pt, px + 34, ty), 90, (9, 3), (0.7, 1.3), span=(0.5, 1), dark=(px + 34, pt + 40), seed=20))
    out.append(nib(belly[:len(belly) - 9], 2.8, seed=21, taper=(0.8, 0.8)))
    out.append(nib(E(px, pt, 22, 7, 0, 360, 20)[:-1], 2.2, closed=True, seed=22))
    out.append(nib([(px - 22, pt - 2), (px - 32, pt - 8)], 2.4, seed=23))
    out.append(finish(U))
    return "".join(out)


@design("pizza-love-language")
def pizza(U):
    pal = TOMATO
    out = [ground(U, 21)]
    out.append(blot(U, 300, 190, 170, 120, pal, 2, 0.15))
    g = '<g transform="rotate(-12 300 180)">'
    out.append(g)
    tip = (300, 318)
    cl, crr = (190, 92), (410, 92)
    crust_top = [cl, (300, 66), crr]
    slice_ = [cl, (238, 200), tip, (362, 200), crr]
    body = cr([cl, (238, 200), tip], False, 3) + cr([tip, (362, 200), crr], False, 3)[1:] + cr([crr, (300, 80), cl], False, 3)[1:]
    sd = poly(body)
    out.append(shadow(316, 330, 70, 8, 0.15))
    out.append(f'<path d="{sd}" fill="{PAPER}"/>')
    out.append(stipple(U(), sd, (180, 70, 420, 320), 260, 4, light=(260, 140), r=(0.5, 1.1), op=0.6))
    # cheese bubbles
    rnd = random.Random(6)
    for i in range(10):
        bx, by = rnd.uniform(230, 370), rnd.uniform(110, 230)
        if abs(bx - 300) > (318 - by) * 0.55:
            continue
        out.append(nib(E(bx, by, rnd.uniform(4, 8), rnd.uniform(3, 5), 180, 360, 8), 1.4, seed=i, taper=(0.2, 0.2)))
    # pepperoni
    for i, (px, py, r) in enumerate(((262, 132, 24), (336, 128, 22), (300, 190, 22), (318, 252, 15), (262, 220, 0))):
        if not r:
            continue
        pd = blob(px, py, r, r * 0.92, 10 + i, 0.05)
        out.append(f'<path d="{pd}" fill="{pal[1]}"/>')
        out.append(hatch(U(), pd, (px - r, py - r, px + r, py + r), 45, (5, 2.6), (0.8, 1.1), span=(0.5, 1), dark=(px + r, py + r), seed=20 + i))
        for k in range(4):
            a = rnd.uniform(0, 6.28); d = rnd.uniform(0.2, 0.6) * r
            out.append(f'<circle cx="{_f(px + d * math.cos(a))}" cy="{_f(py + d * math.sin(a))}" r="1.6" fill="{PAPER}" opacity="0.8"/>')
        out.append(nib(blob_pts(px, py, r, r * 0.92, 10 + i, 0.05), 2.2, closed=True, seed=30 + i))
    # basil
    for i, (ox, oy) in enumerate(((272, 172), (338, 196), (292, 238), (246, 108))):
        out.append(f'<ellipse cx="{ox}" cy="{oy}" rx="8.5" ry="7" fill="{INK}"/><ellipse cx="{ox + 0.5}" cy="{oy}" rx="3.4" ry="2.6" fill="{PAPER}"/>')
    out.append(nib([(cl[0], cl[1]), (238, 200), tip, (362, 200), crr], 3.2, seed=42, taper=(0.9, 0.9)))
    # crust
    crust = [cl, (300, 60), crr, (406, 104), (300, 86), (196, 104)]
    cd = sm(crust)
    out.append(f'<path d="{cd}" fill="{PAPER}"/>')
    out.append(stipple(U(), cd, (180, 54, 420, 110), 420, 44, light=(250, 62), r=(0.6, 1.4)))
    out.append(hatch(U(), cd, (180, 54, 420, 110), 80, (9, 3.4), (0.8, 1.2), span=(0.55, 1), dark=(410, 100), seed=47))
    out.append(nib(crust, 3, closed=True, seed=45))
    for i in range(6):
        x = 220 + i * 32
        out.append(nib([(x, 82 - abs(300 - x) * 0.08), (x + 8, 78 - abs(300 - x) * 0.08)], 2, seed=46 + i))
    # cheese drip pulled from the tip
    drip = [(tip[0] - 9, tip[1] - 16), (tip[0] - 6, tip[1] + 6), (tip[0] - 7, tip[1] + 22), (tip[0], tip[1] + 34), (tip[0] + 6, tip[1] + 22), (tip[0] + 4, tip[1] + 6), (tip[0] + 9, tip[1] - 16)]
    out.append(f'<path d="{sm(drip)}" fill="{PAPER}"/>')
    out.append(nib(drip[1:6], 2.4, seed=50, taper=(0.2, 0.2)))
    out.append(f'<ellipse cx="{tip[0] - 2}" cy="{tip[1] + 22}" rx="1.6" ry="4" fill="{INK}" opacity="0.5"/>')
    out.append("</g>")
    out.append(shade_text(U(), 300, 476, "PIZZA", ANTON, fit("PIZZA", ANTON, 140, 430, 10), ls=10, seed=51))
    out.append(tx(300, 528, "is my love language", SERIF_IT, fit("is my love language", SERIF_IT, 44, 420), INK))
    out.append(finish(U))
    return "".join(out)


@design("stay-cozy")
def stay_cozy(U):
    pal = TOMATO
    out = [ground(U, 22)]
    out.append(blot(U, 290, 200, 160, 120, pal, 9, 0.14))

    def knit(rd, region):
        xs = [p[0] for p in region]
        x0, x1 = min(xs), max(xs)
        y0, y1 = 186, 296
        band = poly([(x0 - 4, y0), (x1 + 4, y0), (x1 + 4, y1), (x0 - 4, y1)])
        inner = [tint(U(), band, pal, 3, 1, 0, 0)]
        for r in range(9):
            y = y0 + 8 + r * 12
            for c in range(13):
                x = x0 + 6 + c * 12
                if 4 <= c <= 5:
                    continue
                inner.append(nib([(x - 4, y - 4), (x, y + 4), (x + 4, y - 4)], 1.6, smooth=False, seed=r * 13 + c, taper=(0.5, 0.5), color=pal[2]))
        cx_ = x0 + 6 + 4.5 * 12
        for r in range(5):
            y = y0 + 6 + r * 22
            inner.append(nib([(cx_ - 7, y), (cx_ + 7, y + 11), (cx_ - 7, y + 22)], 2.2, seed=200 + r, color=pal[2]))
            inner.append(nib([(cx_ + 7, y), (cx_ - 7, y + 11), (cx_ + 7, y + 22)], 2.2, seed=210 + r, color=pal[2]))
        for yy in (y0, y1):
            inner.append(nib(E((x0 + x1) / 2, yy, (x1 - x0) / 2, 14, 10, 170, 18), 2.4, seed=yy))
        inner.append(contour(U(), band, (x0 + x1) / 2, y0 + 3, y0 + 9, (x1 - x0) / 2, 14, 3, 1.2, a0=10, a1=170, seed=5))
        inner.append(contour(U(), band, (x0 + x1) / 2, y1 - 9, y1 - 3, (x1 - x0) / 2, 14, 3, 1.2, a0=10, a1=170, seed=6))
        return clipped(U(), rd, "".join(inner))
    out.append(mug2(U, 282, 170, 168, 140, 7, wrap=knit, steam_n=0))
    # heart-shaped steam
    hs = [(282, 132), (262, 112), (252, 92), (262, 76), (278, 80), (282, 92), (288, 80), (304, 76), (314, 92), (304, 112), (282, 132)]
    out.append(nib(hs, 2.8, seed=8, taper=(0.2, 0.2)))
    out.append(steam(244, 140, 54, 9, 2.4))
    out.append(steam(322, 142, 60, 10, 2.4))
    ck = blob_pts(186, 286, 34, 33, 4, 0.04)
    out.append(f'<path d="{sm(ck)}" fill="{PAPER}"/>')
    out.append(stipple(U(), sm(ck), (150, 250, 222, 322), 140, 6, light=(176, 270), r=(0.5, 1.1)))
    out.append(nib(ck, 2.8, closed=True, seed=5))
    for i, (kx, ky) in enumerate(((172, 272), (198, 266), (206, 294), (178, 300), (190, 284), (164, 290))):
        out.append(f'<path d="{blob(kx, ky, 5, 4, i, 0.25, 8)}" fill="{INK}"/>')
    out.append(f'<circle cx="150" cy="322" r="2" fill="{INK}"/><circle cx="140" cy="318" r="1.4" fill="{INK}"/>')
    ck2 = E(118, 298, 30, 30, 0, 360, 30)[:-1]
    out.append(shade_text(U(), 300, 446, "STAY", DMS, fit("STAY", DMS, 120, 380, 12), ls=12, seed=11, dx=3.5, dy=3.5))
    out.append(tx(300, 528, "cozy", SERIF_IT, 104, INK))
    out.append(nib([(124, 508), (166, 500), (200, 510)], 2.6, seed=12, taper=(0.1, 0.2), cal=0.6))
    out.append(nib([(400, 510), (434, 500), (476, 508)], 2.6, seed=13, taper=(0.2, 0.1), cal=0.6))
    out.append(finish(U))
    return "".join(out)


# ================================================================ new sayings
def heart_pts(cx, cy, s, n=40):
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        out.append((cx + x * s / 16, cy + y * s / 16))
    return out


def ink_heart(U, cx, cy, s, pal=None, seed=1, w=2.4, fill=None):
    pts = heart_pts(cx, cy, s)
    d = poly(pts)
    out = [f'<path d="{d}" fill="{fill or PAPER}"/>']
    if pal:
        out.append(tint(U(), d, pal, seed, 1, -60, 14, (6, 14), (1.5, 3), (cx - s, cy - s, cx + s, cy + s)))
    out.append(hatch(U(), d, (cx - s, cy - s, cx + s, cy + s), 45, (3, 3), (1, 1), span=(0.6, 1), dark=(cx + s, cy + s), seed=seed, wob=0.2))
    out.append(nib(pts, w, closed=True, seed=seed + 1, smooth=False))
    out.append(nib([(cx - s * 0.55, cy - s * 0.35), (cx - s * 0.62, cy - s * 0.1)], w * 1.2, color=PAPER, seed=seed + 2, cal=0, op=0.85))
    return "".join(out)


def skillet(U, cx, cy, R, seed, handle_to=None):
    out = []
    ry = R * 0.92
    hx = handle_to or cx + R + 110
    # handle
    hd = [(cx + R - 6, cy - 14), (hx - 20, cy - 12), (hx, cy - 8), (hx + 6, cy), (hx, cy + 8), (hx - 20, cy + 12), (cx + R - 6, cy + 14)]
    hp = sm(hd)
    out.append(shadow(cx + 14, cy + ry + 6, R * 1.05, 12, 0.15))
    out.append(f'<path d="{hp}" fill="{INK}"/>')
    out.append(f'<ellipse cx="{hx - 14}" cy="{cy}" rx="7" ry="4.5" fill="{PAPER}"/>')
    out.append(nib([(cx + R + 6, cy - 6), (hx - 30, cy - 6)], 1.8, color=PAPER, seed=seed, op=0.5, cal=0))
    rim = E(cx, cy, R, ry, 0, 360, 72)[:-1]
    rd = sm(rim)
    out.append(f'<path d="{rd}" fill="{INK}"/>')
    # inner cooking surface: dense cross-hatch over dark ink, lighter toward the light
    inner = E(cx, cy + 4, R - 16, ry - 16, 0, 360, 64)[:-1]
    idd = sm(inner)
    out.append(f'<path d="{idd}" fill="#2E2822"/>')
    out.append(hatch(U(), idd, (cx - R, cy - R, cx + R, cy + R), 30, (3.2, 3.2), (1.0, 1.0), color="#57493C", seed=seed + 1, wob=0.3))
    out.append(hatch(U(), idd, (cx - R, cy - R, cx + R, cy + R), -40, (5, 5), (0.9, 0.9), color="#57493C", seed=seed + 2, wob=0.3, span=(0, 0.5), dark=(cx - R, cy - R)))
    # rim highlight + lip
    out.append(nib(E(cx, cy, R - 7, ry - 7, 195, 300, 20), 3.4, color=PAPER, seed=seed + 3, op=0.55, cal=0))
    out.append(nib(rim, 3, closed=True, seed=seed + 4))
    # pour spouts
    for a in (150, 30):
        x = cx + R * math.cos(math.radians(a)); y = cy + ry * math.sin(math.radians(a))
        out.append(f'<path d="{blob(x, y, 12, 6, seed + a, 0.05, 10, a + 90)}" fill="{INK}"/>')
    return "".join(out)


def fried_egg(U, cx, cy, s, seed, pal):
    out = []
    white = blob_pts(cx, cy, s, s * 0.82, seed, 0.14, 22)
    wd = sm(white)
    out.append(f'<path d="{wd}" fill="{PAPER}"/>')
    out.append(stipple(U(), wd, (cx - s, cy - s, cx + s, cy + s), 90, seed, light=(cx - s * 0.3, cy - s * 0.3), r=(0.5, 1.0), op=0.6))
    out.append(nib(white, 2.6, closed=True, seed=seed + 1))
    # crispy lace edge
    rnd = random.Random(seed)
    for i in range(0, 22, 2):
        x, y = white[i]
        out.append(f'<circle cx="{_f(x + (cx - x) * 0.08)}" cy="{_f(y + (cy - y) * 0.08)}" r="{rnd.uniform(1, 2):.1f}" fill="{INK}" opacity="0.7"/>')
    yk = (cx + s * 0.08, cy - s * 0.05)
    yr = s * 0.4
    yd = blob(yk[0], yk[1], yr, yr * 0.95, seed + 2, 0.03)
    out.append(f'<path d="{yd}" fill="{pal[1]}"/>')
    out.append(tint(U(), yd, pal, seed + 3, 1, -40, 20, (6, 16), (1.5, 3), (yk[0] - yr, yk[1] - yr, yk[0] + yr, yk[1] + yr)))
    out.append(hatch(U(), yd, (yk[0] - yr, yk[1] - yr, yk[0] + yr, yk[1] + yr), 45, (3.6, 2.6), (0.9, 1.1), span=(0.55, 1), dark=(yk[0] + yr, yk[1] + yr), seed=seed + 4))
    out.append(nib(blob_pts(yk[0], yk[1], yr, yr * 0.95, seed + 2, 0.03), 2.6, closed=True, seed=seed + 5))
    out.append(f'<ellipse cx="{_f(yk[0] - yr * 0.35)}" cy="{_f(yk[1] - yr * 0.4)}" rx="{_f(yr * 0.22)}" ry="{_f(yr * 0.13)}" fill="{PAPER}" transform="rotate(-30 {_f(yk[0] - yr * 0.35)} {_f(yk[1] - yr * 0.4)})"/>')
    return "".join(out)


@design("rise-and-shine")
def rise_and_shine(U):
    pal = MUSTARD
    out = [ground(U, 23)]
    cx, cy = 262, 208
    # sunburst behind the pan: tapered rays of alternating length
    rays = []
    for i in range(30):
        a = math.radians(i * 12 + 3)
        L = 176 if i % 2 == 0 else 142
        hw = math.radians(3.6)
        rays.append(poly([(cx + 40 * math.cos(a - hw), cy + 40 * math.sin(a - hw)), (cx + L * math.cos(a - hw * 0.5), cy + L * 0.9 * math.sin(a - hw * 0.5)),
                          (cx + (L + 8) * math.cos(a), cy + (L + 8) * 0.9 * math.sin(a)), (cx + L * math.cos(a + hw * 0.5), cy + L * 0.9 * math.sin(a + hw * 0.5)),
                          (cx + 40 * math.cos(a + hw), cy + 40 * math.sin(a + hw))]))
    for i, r in enumerate(rays):
        out.append(f'<path d="{r}" fill="{pal[1]}" opacity="0.75"/>')
        out.append(f'<path d="{r}" fill="none" stroke="{INK}" stroke-width="1.3" stroke-linejoin="round"/>')
    out.append(skillet(U, cx, cy, 124, 6, handle_to=516))
    out.append(fried_egg(U, cx - 6, cy + 2, 80, 7, pal))
    for i, (sx, sy, r) in enumerate(((92, 120, 9), (470, 92, 11), (486, 300, 7))):
        out.append(sparkle(sx, sy, r, w=2.2))
    out.append(tx(300, 422, "rise &", SERIF_IT, 70, INK))
    out.append(shade_text(U(), 300, 532, "SHINE", ANTON, fit("SHINE", ANTON, 112, 440, 16), ls=16, seed=8))
    out.append(finish(U))
    return "".join(out)


def chain(cx, y0, y1, seed, link=12):
    out = []
    y = y0
    k = 0
    while y < y1 - 2:
        if k % 2 == 0:
            out.append(f'<ellipse cx="{cx}" cy="{_f(y + link / 2)}" rx="4.2" ry="{link / 2 + 1:.1f}" fill="none" stroke="{INK}" stroke-width="2.2"/>')
        else:
            out.append(f'<line x1="{cx}" y1="{_f(y - 1)}" x2="{cx}" y2="{_f(y + link + 1)}" stroke="{INK}" stroke-width="3.4" stroke-linecap="round"/>')
        y += link
        k += 1
    return "".join(out)


def hen(U, cx, cy, s, seed, pal):
    """A plump sitting hen, eyes closed, facing left."""
    out = []
    body = [(cx - 0.62 * s, cy - 0.2 * s), (cx - 0.5 * s, cy - 0.62 * s), (cx - 0.3 * s, cy - 0.72 * s), (cx - 0.12 * s, cy - 0.5 * s),
            (cx + 0.2 * s, cy - 0.32 * s), (cx + 0.52 * s, cy - 0.5 * s), (cx + 0.8 * s, cy - 0.78 * s), (cx + 0.86 * s, cy - 0.36 * s),
            (cx + 0.72 * s, cy + 0.06 * s), (cx + 0.36 * s, cy + 0.3 * s), (cx - 0.2 * s, cy + 0.32 * s), (cx - 0.56 * s, cy + 0.14 * s)]
    bd = sm(body)
    out.append(f'<path d="{bd}" fill="{PAPER}"/>')
    out.append(hatch(U(), bd, (cx - s, cy - s, cx + s, cy + 0.4 * s), 70, (10, 3.2), (0.7, 1.2), span=(0.55, 1), dark=(cx + 0.4 * s, cy + 0.4 * s), seed=seed))
    # tail feathers
    for k, (dx, dy) in enumerate(((0.62, -0.62), (0.74, -0.48), (0.8, -0.3))):
        out.append(nib([(cx + 0.4 * s, cy - 0.2 * s), (cx + (dx - 0.06) * s, cy + (dy + 0.06) * s), (cx + dx * s, cy + dy * s)], 1.8, seed=seed + k, taper=(0.2, 0.2)))
    # wing with scalloped feathers
    wing = [(cx - 0.12 * s, cy - 0.22 * s), (cx + 0.2 * s, cy - 0.26 * s), (cx + 0.5 * s, cy - 0.1 * s), (cx + 0.46 * s, cy + 0.08 * s), (cx + 0.1 * s, cy + 0.14 * s), (cx - 0.16 * s, cy + 0.02 * s)]
    out.append(f'<path d="{sm(wing)}" fill="{PAPER}"/>')
    for r in range(3):
        for c in range(4 - r):
            fx = cx - 0.04 * s + c * 0.12 * s + r * 0.1 * s
            fy = cy - 0.14 * s + r * 0.08 * s
            out.append(nib(E(fx, fy, 0.06 * s, 0.05 * s, 0, 180, 8), 1.5, seed=seed + 10 + r * 5 + c, taper=(0.3, 0.3)))
    out.append(nib(wing, 2.2, closed=True, seed=seed + 20))
    out.append(nib(body, 2.8, closed=True, seed=seed + 21))
    # comb + wattle in the accent
    comb = [(cx - 0.44 * s, cy - 0.66 * s), (cx - 0.46 * s, cy - 0.82 * s), (cx - 0.38 * s, cy - 0.76 * s), (cx - 0.32 * s, cy - 0.9 * s), (cx - 0.26 * s, cy - 0.78 * s), (cx - 0.18 * s, cy - 0.84 * s), (cx - 0.2 * s, cy - 0.66 * s)]
    out.append(f'<path d="{sm(comb)}" fill="{pal[1]}"/>')
    out.append(nib(comb, 1.8, closed=True, seed=seed + 22))
    wat = blob_pts(cx - 0.6 * s, cy - 0.4 * s, 0.05 * s, 0.09 * s, seed, 0.1, 10)
    out.append(f'<path d="{sm(wat)}" fill="{pal[1]}"/>')
    out.append(nib(wat, 1.6, closed=True, seed=seed + 23))
    # beak + sleepy eye
    beak = [(cx - 0.6 * s, cy - 0.56 * s), (cx - 0.76 * s, cy - 0.5 * s), (cx - 0.6 * s, cy - 0.46 * s)]
    out.append(f'<path d="{poly(beak)}" fill="{INK}"/>')
    out.append(nib(E(cx - 0.42 * s, cy - 0.56 * s, 0.06 * s, 0.035 * s, 10, 170, 8), 2, seed=seed + 24, taper=(0.3, 0.3)))
    for k in range(3):
        a = 200 + k * 25
        out.append(line(cx - 0.42 * s + 0.07 * s * math.cos(math.radians(a + 160)), cy - 0.54 * s, cx - 0.42 * s + 0.1 * s * math.cos(math.radians(a + 160)), cy - 0.5 * s + 0.03 * s * k, 1.2, seed=seed + 25 + k, cal=0))
    return "".join(out)


@design("kitchen-closed")
def kitchen_closed(U):
    pal = TOMATO
    out = [ground(U, 24)]
    # wall bracket
    out.append(f'<rect x="64" y="70" width="14" height="96" rx="3" fill="{INK}"/>')
    out.append(nib([(76, 92), (300, 92), (500, 92)], 6, seed=2, taper=(1, 0.8), cal=0))
    out.append(f'<circle cx="504" cy="92" r="6" fill="{INK}"/>')
    scroll = [(78, 154), (120, 130), (170, 106), (220, 96)]
    out.append(nib(scroll, 4.2, seed=3, taper=(1, 0.5), cal=0))
    out.append(nib([(120, 130), (128, 116), (116, 110), (108, 120), (116, 126)], 2.4, seed=4, taper=(0.6, 0.3), cal=0))
    # chains
    out.append(chain(172, 92, 178, 5))
    out.append(chain(428, 92, 178, 6))
    # the sign board
    sx0, sx1, sy0, sy1 = 120, 480, 176, 352
    board = [(sx0, sy0 + 10), (sx0 + 10, sy0), (sx1 - 10, sy0), (sx1, sy0 + 10), (sx1, sy1 - 10), (sx1 - 10, sy1), (sx0 + 10, sy1), (sx0, sy1 - 10)]
    out.append(f'<path d="{poly(board)}" fill="{INK}"/>')
    rnd = random.Random(5)
    for i in range(14):
        y = sy0 + 10 + i * 12 + rnd.uniform(-2, 2)
        out.append(nib([(sx0 + 6, y), (300 + rnd.uniform(-40, 40), y + rnd.uniform(-3, 3)), (sx1 - 6, y + rnd.uniform(-2, 2))], 1.1, color="#4A4038", seed=60 + i, taper=(0.2, 0.2)))
    inner = [(sx0 + 14, sy0 + 14), (sx1 - 14, sy0 + 14), (sx1 - 14, sy1 - 14), (sx0 + 14, sy1 - 14)]
    out.append(nib(inner, 2, closed=True, smooth=False, color=PAPER, seed=7, cal=0))
    for (x, y) in ((sx0 + 14, sy0 + 14), (sx1 - 14, sy0 + 14), (sx1 - 14, sy1 - 14), (sx0 + 14, sy1 - 14)):
        out.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="{PAPER}"/>')
    for x in (172, 428):
        out.append(f'<circle cx="{x}" cy="{sy0 + 1}" r="5" fill="{INK}" stroke="{PAPER}" stroke-width="1.6"/>')
    out.append(rule_label(U(), 300, 226, "KITCHEN", 30, 12, BEBAS, PAPER, line_w=40, gap=12))
    out.append(worn(U(), 300, 322, "CLOSED", ANTON, fit("CLOSED", ANTON, 92, 300, 6), PAPER, ls=6, seed=8, wear=INK))
    # the hen napping on top of the sign
    out.append(hen(U, 292, 148, 92, 9, pal))
    for i, (zx, zy, zs) in enumerate(((214, 128, 34), (190, 98, 44), (222, 70, 28))):
        out.append(tx(zx, zy, "z", SERIF_IT, zs, INK))
    # caption
    out.append(tx(300, 440, "this chick", SERIF_IT, 76, INK))
    out.append(rule_label(U(), 300, 512, "HAS HAD IT", 40, 6, BEBAS, line_w=36, gap=14, w=2.6))
    out.append(finish(U))
    return "".join(out)


def utensil(U, kind, x, top, L, seed, pal=None):
    """Kitchen utensils hanging from a hook at (x, top)."""
    out = []
    # S hook
    out.append(nib([(x + 5, top - 16), (x + 1, top - 22), (x - 4, top - 16), (x, top - 8), (x + 4, top - 2), (x, top + 4), (x - 4, top)], 2, seed=seed, cal=0))
    hole = top + 10
    hw = 8
    hend = top + L * 0.58
    handle = [(x - hw / 2 - 1, top + 2), (x + hw / 2 + 1, top + 2), (x + hw / 2, hend), (x - hw / 2, hend)]
    if kind == "spoon":
        handle = [(x - 6, top + 2), (x + 6, top + 2), (x + 4, hend), (x - 4, hend)]
    hd = sm(handle) if kind == "spoon" else poly(handle)
    fill = pal[1] if (pal and kind in ("whisk",)) else (PAPER if kind == "spoon" else INK)
    out.append(f'<path d="{hd}" fill="{fill}"/>')
    if kind == "spoon":
        for k in range(3):
            out.append(line(x - 2 + k * 2, top + 14, x - 2 + k * 2 + 0.5, hend - 4, 0.9, seed=seed + k, cal=0, op=0.7))
    out.append(nib(handle, 2, closed=True, smooth=kind == "spoon", seed=seed + 1))
    out.append(f'<circle cx="{x}" cy="{hole}" r="3" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>')
    if kind == "whisk":
        out.append(f'<rect x="{x - 5}" y="{hend - 2}" width="10" height="12" fill="{INK}"/>')
        wt = hend + 10
        for k in range(5):
            off = (k - 2) / 2
            loop = [(x + off * 3, wt), (x + off * 16, wt + L * 0.18), (x + off * 18, wt + L * 0.34), (x + off * 8, wt + L * 0.44), (x, wt + L * 0.46)]
            out.append(nib(loop, 1.6, seed=seed + 10 + k, taper=(0.6, 0.6)))
    elif kind == "ladle":
        out.append(nib([(x, hend), (x, hend + 18), (x - 2, hend + 26)], 4, seed=seed + 3, taper=(1, 1), cal=0))
        bowl = E(x - 2, hend + 40, 28, 18, 0, 180, 16) + [(x - 30, hend + 34)]
        bd = poly(cr(bowl, True))
        out.append(f'<path d="{bd}" fill="{PAPER}"/>')
        out.append(hatch(U(), bd, (x - 32, hend + 26, x + 28, hend + 62), 90, (8, 3), (0.8, 1.2), span=(0.5, 1), dark=(x + 26, hend + 50), seed=seed + 4))
        out.append(nib(bowl, 2.4, closed=True, seed=seed + 5, smooth=False))
        out.append(nib(E(x - 2, hend + 40, 28, 6, 0, 360, 20)[:-1], 1.8, closed=True, seed=seed + 6))
    elif kind == "turner":
        blade = [(x - 6, hend), (x + 6, hend), (x + 18, hend + 18), (x + 20, hend + 66), (x - 20, hend + 66), (x - 18, hend + 18)]
        out.append(f'<path d="{poly(blade)}" fill="{PAPER}"/>')
        out.append(hatch(U(), poly(blade), (x - 20, hend, x + 20, hend + 66), 90, (8, 3), (0.8, 1.2), span=(0.55, 1), dark=(x + 20, hend + 40), seed=seed + 4))
        out.append(nib(blade, 2.4, closed=True, smooth=False, seed=seed + 5))
        for k in (-10, 0, 10):
            out.append(f'<rect x="{x + k - 2.5}" y="{hend + 26}" width="5" height="30" rx="2.5" fill="{INK}"/>')
    elif kind == "spoon":
        bowl = E(x, hend + 26, 15, 26, 0, 360, 24)[:-1]
        out.append(f'<path d="{sm(bowl)}" fill="{PAPER}"/>')
        out.append(hatch(U(), sm(bowl), (x - 16, hend, x + 16, hend + 54), 70, (6, 2.8), (0.8, 1.2), span=(0.5, 1), dark=(x + 14, hend + 40), seed=seed + 4))
        out.append(nib(bowl, 2.4, closed=True, seed=seed + 5))
    elif kind == "masher":
        out.append(nib([(x, hend), (x - 18, hend + 46), (x + 18, hend + 46), (x, hend)], 2.6, seed=seed + 3, smooth=False, cal=0))
        grid = [(x - 22, hend + 44), (x + 22, hend + 44), (x + 22, hend + 52), (x - 22, hend + 52)]
        out.append(f'<path d="{poly(grid)}" fill="{INK}"/>')
        for k in range(-2, 3):
            out.append(f'<circle cx="{x + k * 8}" cy="{hend + 48}" r="1.8" fill="{PAPER}"/>')
    return "".join(out)


@design("heart-of-the-home")
def heart_of_the_home(U):
    pal = TOMATO
    out = [ground(U, 25)]
    # rail
    out.append(nib([(80, 92), (300, 91), (520, 92)], 6, seed=2, taper=(1, 1), cal=0))
    for x in (80, 520):
        out.append(f'<circle cx="{x}" cy="92" r="7" fill="{INK}"/>')
        out.append(f'<rect x="{x - 4}" y="70" width="8" height="22" fill="{INK}"/>')
    items = (("ladle", 132, 170), ("whisk", 216, 150), ("turner", 300, 172), ("spoon", 384, 162), ("masher", 466, 150))
    for i, (k, x, L) in enumerate(items):
        out.append(utensil(U, k, x, 112, L, 10 + i * 20, pal))
    out.append(tx(300, 338, "the kitchen is the", SERIF_IT, fit("the kitchen is the", SERIF_IT, 46, 400), INK))
    out.append(shade_text(U(), 300, 460, "HEART", DMS, fit("HEART", DMS, 136, 440, 6), ls=6, seed=4))
    out.append(tx(300, 528, "of the home", SERIF_IT, 52, INK))
    out.append(ink_heart(U, 110, 510, 16, pal, 5, 2))
    out.append(ink_heart(U, 490, 510, 16, pal, 6, 2))
    out.append(finish(U))
    return "".join(out)


def whisk_big(U, seed, pal):
    """A balloon whisk drawn upright in local coordinates (0,0 = top of wires), length ~ 420."""
    out = []
    # wires: nested loops with rounded ends, crossing at the tip
    bulb_h, bulb_w = 230, 120
    fy = bulb_h
    for k, a in enumerate((60, 44, 26, 9)):
        half = [(-a * 0.1 - 3, fy), (-a * 0.78, fy - bulb_h * 0.28), (-a, fy - bulb_h * 0.6), (-a * 0.84, fy - bulb_h * 0.84), (-a * 0.46, fy - bulb_h * 0.97), (0, fy - bulb_h)]
        loop = half + [(-x, y) for x, y in half[::-1][1:]]
        out.append(nib(loop, 2.4 if k == 0 else 2.0, seed=seed + k, taper=(0.8, 0.8), cal=0.2))
    out.append(nib([(0, fy), (0, 0)], 1.8, seed=seed + 6, taper=(0.8, 0.8), cal=0))
    # ferrule
    fer = [(-12, fy), (12, fy), (10, fy + 24), (-10, fy + 24)]
    out.append(f'<path d="{poly(fer)}" fill="{PAPER}"/>')
    out.append(hatch(U(), poly(fer), (-12, fy, 12, fy + 24), 90, (5, 2.4), (0.8, 1.1), span=(0.5, 1), dark=(12, fy + 12), seed=seed + 10))
    out.append(nib(fer, 2.4, closed=True, smooth=False, seed=seed + 11))
    for y in (fy + 6, fy + 18):
        out.append(line(-11, y, 11, y, 1.4, seed=seed + y, cal=0))
    # handle
    hdl = [(-10, fy + 24), (10, fy + 24), (16, fy + 120), (15, fy + 168), (0, fy + 180), (-15, fy + 168), (-16, fy + 120)]
    hd = sm(hdl)
    out.append(f'<path d="{hd}" fill="{PAPER}"/>')
    out.append(tint(U(), hd, pal, seed, 1, -90, 30, (20, 50), (2, 4), (-16, fy + 24, 16, fy + 180)))
    out.append(hatch(U(), hd, (-16, fy + 24, 16, fy + 180), 90, (6, 2.6), (0.8, 1.2), span=(0.55, 1), dark=(16, fy + 100), seed=seed + 12))
    out.append(nib(hdl, 2.8, closed=True, seed=seed + 13))
    out.append(nib([(-8, fy + 36), (-10, fy + 120), (-8, fy + 160)], 3, color=PAPER, seed=seed + 14, op=0.8, cal=0))
    out.append(f'<circle cx="0" cy="{fy + 192}" r="10" fill="none" stroke="{INK}" stroke-width="3"/>')
    return "".join(out)


@design("whisk-taker")
def whisk_taker(U):
    pal = TOMATO
    out = [ground(U, 26)]
    out.append(blot(U, 190, 260, 120, 190, pal, 5, 0.14, rot=20))
    out.append(f'<g transform="translate(166 96) rotate(-16)">{whisk_big(U, 3, pal)}</g>')
    # batter splatters
    rnd = random.Random(4)
    for i in range(10):
        x, y = rnd.uniform(80, 250), rnd.uniform(78, 124)
        out.append(f'<path d="{blob(x, y, rnd.uniform(2, 5), rnd.uniform(2, 4), i, 0.3, 8)}" fill="{INK}"/>')
    out.append(tx(410, 196, "a true", SERIF_IT, 50, INK))
    out.append(shade_text(U(), 414, 330, "WHISK", BEBAS, fit("WHISK", BEBAS, 150, 236, 4), ls=4, seed=5, dx=4, dy=4))
    out.append(shade_text(U(), 414, 466, "TAKER", BEBAS, fit("TAKER", BEBAS, 150, 236, 4), ls=4, seed=6, dx=4, dy=4))
    out.append(rule_label(U(), 430, 520, "BAKE BOLDLY", 18, 4, line_w=16, gap=8))
    out.append(finish(U))
    return "".join(out)


def wreath(U, cx, cy, R, seed, pal, gap_top=40):
    out = []
    rnd = random.Random(seed)
    for side in (-1, 1):
        a0, a1 = 90, 90 - side * (180 - gap_top / 2)
        arc = E(cx, cy, R, R, a0, a1, 40)
        out.append(nib(arc, 2.6, seed=seed + side, taper=(1, 0.3)))
        for i in range(2, len(arc) - 1, 2):
            px, py = arc[i]
            qx, qy = arc[i + 1]
            ang = math.degrees(math.atan2(qy - py, qx - px))
            sz = 1 - 0.4 * i / len(arc)
            for s2 in (-1, 1):
                out.append(leaf(px, py, ang + s2 * rnd.uniform(30, 50), 30 * sz, 9 * sz, seed + i * 3 + s2,
                                fill=pal[1] if (i // 2 + s2) % 3 == 0 else PAPER, w=1.8))
            if i % 6 == 0:
                bx = px + (cx - px) * 0.08
                by = py + (cy - py) * 0.08
                out.append(f'<circle cx="{_f(bx)}" cy="{_f(by)}" r="4.2" fill="{INK}"/><circle cx="{_f(bx - 1.2)}" cy="{_f(by - 1.2)}" r="1.2" fill="{PAPER}"/>')
    return "".join(out)


@design("eat-well-laugh-often-love-much")
def eat_well(U):
    pal = SAGE
    out = [ground(U, 27)]
    out.append(wreath(U, 300, 294, 210, 3, pal, 70))
    # bow at the bottom
    for sgn in (-1, 1):
        loop = [(300, 506), (300 + sgn * 34, 488), (300 + sgn * 44, 506), (300 + sgn * 30, 520), (300, 508)]
        out.append(f'<path d="{sm(loop)}" fill="{PAPER}"/>')
        out.append(nib(loop, 2.4, closed=True, seed=10 + sgn))
        out.append(nib([(300, 510), (300 + sgn * 16, 528), (300 + sgn * 24, 534)], 2.4, seed=12 + sgn))
    out.append(f'<ellipse cx="300" cy="508" rx="7" ry="8" fill="{INK}"/>')
    out.append(ink_heart(U, 300, 92, 14, pal, 9, 2))
    out.append(shade_text(U(), 300, 244, "EAT WELL", BEBAS, fit("EAT WELL", BEBAS, 84, 272, 6), ls=6, seed=4, dx=3, dy=3))
    out.append(dotrow(250, 350, 268, 12.5, 2))
    out.append(tx(300, 330, "laugh often", SERIF_IT, fit("laugh often", SERIF_IT, 60, 320), INK))
    out.append(dotrow(250, 350, 360, 12.5, 2))
    out.append(shade_text(U(), 300, 428, "LOVE MUCH", BEBAS, fit("LOVE MUCH", BEBAS, 84, 250, 6), ls=6, seed=5, dx=3, dy=3))
    out.append(finish(U))
    return "".join(out)


def rolling_pin(U, x0, x1, cy, r, seed):
    out = []
    bx0, bx1 = x0 + 46, x1 - 46
    out.append(shadow((x0 + x1) / 2 + 10, cy + r + 8, (x1 - x0) / 2, 7, 0.14))
    for sgn, hx in ((-1, x0), (1, x1)):
        hd = [(hx, cy - 9), (hx + sgn * -40, cy - 7), (hx + sgn * -46, cy - 4), (hx + sgn * -46, cy + 4), (hx + sgn * -40, cy + 7), (hx, cy + 9)]
        hp = [(hx - sgn * 4, cy - 10)] + [(hx - sgn * 40, cy - 8), (hx - sgn * 46, cy - 5), (hx - sgn * 46, cy + 5), (hx - sgn * 40, cy + 8)] + [(hx - sgn * 4, cy + 10), (hx + sgn * 2, cy)]
        out.append(f'<path d="{sm(hp)}" fill="{PAPER}"/>')
        out.append(hatch(U(), sm(hp), (min(hx, hx - sgn * 46) - 4, cy - 12, max(hx, hx - sgn * 46) + 4, cy + 12), 0, (3, 2.6), (0.9, 1), span=(0.5, 1), dark=(hx, cy + 10), seed=seed + sgn))
        out.append(nib(hp, 2.2, closed=True, seed=seed + 2 + sgn))
    barrel = [(bx0, cy - r), (bx1, cy - r)] + E(bx1, cy, 7, r, -90, 90, 10)[1:-1] + [(bx1, cy + r), (bx0, cy + r)] + E(bx0, cy, 7, r, 90, 270, 10)[1:-1]
    bd = poly(barrel)
    out.append(f'<path d="{bd}" fill="{PAPER}"/>')
    rnd = random.Random(seed)
    for k in range(6):
        y = cy - r * 0.7 + k * r * 0.28
        out.append(nib([(bx0 + 10, y), ((bx0 + bx1) / 2 + rnd.uniform(-40, 40), y + rnd.uniform(-3, 3)), (bx1 - 10, y + rnd.uniform(-2, 2))], 1.0, seed=seed + 10 + k, taper=(0.2, 0.2), op=0.7))
    out.append(hatch(U(), bd, (bx0, cy - r, bx1, cy + r), 0, (14, 3), (0.6, 1.3), span=(0.5, 1), dark=(300, cy + r), seed=seed + 20))
    out.append(nib([(bx0 + 14, cy - r * 0.55), (bx1 - 14, cy - r * 0.55)], 4, color=PAPER, seed=seed + 21, op=0.8, cal=0))
    out.append(nib(barrel, 2.8, closed=True, smooth=False, seed=seed + 22))
    return "".join(out)


@design("made-with-love")
def made_with_love(U):
    pal = TOMATO
    out = [ground(U, 28)]
    # dough sheet with heart cut-outs
    dough = blob_pts(300, 220, 200, 70, 3, 0.07, 26)
    dd = sm(dough)
    out.append(f'<path d="{dd}" fill="{PAPER}"/>')
    out.append(stipple(U(), dd, (100, 150, 500, 290), 260, 4, light=(250, 190), r=(0.5, 1.1), op=0.6))
    out.append(hatch(U(), dd, (100, 150, 500, 290), 10, (12, 3.4), (0.6, 1.1), span=(0.62, 1), dark=(300, 290), seed=5))
    out.append(nib(dough, 2.6, closed=True, seed=6))
    for i, (hx, hy) in enumerate(((210, 228), (290, 244))):
        hp = [(x, y * 0.62 + hy * 0.38) for x, y in heart_pts(hx, hy, 26)]
        hpd = poly(hp)
        out.append(f'<path d="{hpd}" fill="#E4D8C2"/>')
        out.append(hatch(U(), hpd, (hx - 30, hy - 30, hx + 30, hy + 30), 0, (2.8, 2.8), (1, 1), seed=20 + i, wob=0.2, brk=0,
                         clip2=f'<path d="{poly([(x, y + 7) for x, y in hp])} M 0 0 L 600 0 L 600 600 L 0 600 Z" clip-rule="evenodd"/>'))
        out.append(nib(hp, 2.4, closed=True, smooth=False, seed=22 + i))
    # cookie cutter
    cp = [(x, y * 0.62 + 236 * 0.38) for x, y in heart_pts(400, 236, 34)]
    out.append(nib(cp, 4.2, closed=True, seed=7, smooth=False))
    out.append(nib([(x, y - 9) for x, y in cp], 2.4, closed=True, seed=8, smooth=False))
    for k in range(0, 40, 5):
        x, y = cp[k]
        out.append(line(x, y, x, y - 9, 1.6, seed=9 + k, cal=0))
    out.append(rolling_pin(U, 90, 510, 120, 30, 10))
    # flour dust
    rnd = random.Random(6)
    for _ in range(40):
        x, y = rnd.uniform(90, 510), rnd.uniform(150, 310)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 1.5):.1f}" fill="{INK}" opacity="0.55"/>')
    # lettering
    out.append(rule_label(U(), 300, 352, "MADE WITH", 22, 8, line_w=60))
    out.append(tx(286, 488, "love", SERIF_IT, 168, INK))
    out.append(ink_heart(U, 470, 404, 22, pal, 11, 2.4))
    out.append(swash(150, 440, 516, 12, 3, 8, curl=True))
    out.append(finish(U))
    return "".join(out)


def bread_slice_side(U, x0, x1, y, h, seed, top=True):
    """A slice of bread seen edge-on: crust line and stippled crumb."""
    if top:
        pts = [(x0, y + h), (x0 - 4, y + h * 0.4), (x0 + 10, y), ((x0 + x1) / 2, y - h * 0.25), (x1 - 10, y), (x1 + 4, y + h * 0.4), (x1, y + h)]
    else:
        pts = [(x0, y), (x1, y), (x1 + 2, y + h * 0.7), (x1 - 6, y + h), (x0 + 6, y + h), (x0 - 2, y + h * 0.7)]
    d = sm(pts)
    out = [f'<path d="{d}" fill="{PAPER}"/>',
           stipple(U(), d, (x0 - 6, y - h * 0.3, x1 + 6, y + h), int((x1 - x0) * 1.2), seed, light=((x0 + x1) / 2 - 40, y), r=(0.5, 1.2), op=0.7),
           hatch(U(), d, (x0 - 6, y - h * 0.3, x1 + 6, y + h), 0, (9, 3), (0.8, 1.2), span=(0.6, 1), dark=((x0 + x1) / 2, y + h), seed=seed + 1),
           nib(pts, 2.8, closed=True, seed=seed + 2)]
    # crust inner line
    if top:
        inner = [(x0 + 6, y + h - 2), (x0 + 3, y + h * 0.42), (x0 + 15, y + 6), ((x0 + x1) / 2, y - h * 0.25 + 7), (x1 - 15, y + 6), (x1 - 3, y + h * 0.42), (x1 - 6, y + h - 2)]
        out.append(nib(inner, 1.4, seed=seed + 3, taper=(0.3, 0.3)))
    return "".join(out)


@design("sorry-for-what-i-said-when-i-was-hungry")
def sorry_hungry(U):
    pal = MUSTARD
    out = [ground(U, 29)]
    x0, x1 = 128, 472
    sw = []
    sw.append(bread_slice_side(U, x0 + 4, x1 - 4, 214, 30, 3, top=False))
    rnd = random.Random(4)
    # ham: wavy band
    ham = [(x0 - 8, 206)] + [(x0 + i * 27, 206 + (6 if i % 2 else -2)) for i in range(13)] + [(x1 + 8, 208), (x1 + 6, 218)] + [(x1 - i * 27, 218 + (4 if i % 2 else -1)) for i in range(13)] + [(x0 - 6, 218)]
    hd = poly(cr(ham, True))
    sw.append(f'<path d="{hd}" fill="{PAPER}"/>')
    sw.append(hatch(U(), hd, (x0 - 10, 196, x1 + 10, 226), 60, (3, 3), (1, 1), seed=5, wob=0.2))
    sw.append(nib(cr(ham, True), 2, closed=True, smooth=False, seed=6))
    # cheese sheet with its corners drooping over both sides
    ch = [(x0 - 2, 188), (x1 + 2, 188), (x1 + 16, 196), (x1 + 20, 222), (x1 + 6, 214), (x1 - 4, 204), (x0 + 4, 204), (x0 - 6, 216), (x0 - 18, 226), (x0 - 16, 196)]
    cd = poly(ch)
    sw.append(f'<path d="{cd}" fill="{pal[1]}"/>')
    sw.append(tint(U(), cd, pal, 7, 1, 0, 30, (8, 20), (2, 4), (x0 - 20, 186, x1 + 20, 228)))
    for i in range(7):
        sw.append(f'<ellipse cx="{x0 + 24 + i * 48}" cy="{195 + (i % 2) * 2}" rx="4.6" ry="2.6" fill="{PAPER}" opacity="0.85"/>')
    sw.append(nib(ch, 2.2, closed=True, smooth=False, seed=8))
    # tomato slices
    for i, tx_ in enumerate((x0 + 56, x0 + 172, x0 + 288)):
        sl = [(tx_ - 54, 190), (tx_ - 50, 176), (tx_ + 50, 176), (tx_ + 54, 190)]
        sw.append(f'<path d="{sm(sl)}" fill="{INK}"/>')
        for k in range(4):
            sw.append(f'<ellipse cx="{tx_ - 33 + k * 22}" cy="183" rx="5.4" ry="2.2" fill="{PAPER}" opacity="0.85"/>')
    # lettuce ruffle
    let = [(x0 - 16, 180)]
    for i in range(18):
        let.append((x0 - 12 + i * 21, 164 + (0 if i % 2 else 11) + rnd.uniform(-2, 2)))
    let += [(x1 + 16, 180), (x1 + 4, 182)] + [(x1 - i * 32, 180 + (4 if i % 2 else 0)) for i in range(11)] + [(x0 - 4, 182)]
    ld = poly(cr(let, True))
    sw.append(f'<path d="{ld}" fill="{PAPER}"/>')
    sw.append(hatch(U(), ld, (x0 - 18, 156, x1 + 18, 186), 95, (6, 3), (0.9, 1.1), span=(0.4, 1), dark=(300, 186), seed=9))
    sw.append(nib(cr(let, True), 2.2, closed=True, smooth=False, seed=10))
    sw.append(bread_slice_side(U, x0, x1, 112, 52, 11, top=True))
    # a big bite out of the top right corner
    bites = [(458, 112, 30), (488, 150, 28), (440, 92, 22)]
    bite = " ".join(poly(E(bx, by, r, r, 0, 360, 24)) for bx, by, r in bites)
    mid = U("bite")
    out.append(f'<defs><mask id="{mid}"><rect width="600" height="600" fill="#fff"/><path d="{bite}" fill="#000"/></mask></defs>')
    out.append(shadow(300, 248, 190, 9, 0.16))
    out.append(f'<g mask="url(#{mid})">{"".join(sw)}</g>')
    for bx, by, r, a0, a1 in ((458, 112, 30, 100, 196), (488, 150, 28, 120, 215), (440, 92, 22, 40, 150)):
        arc = E(bx, by, r, r, a0, a1, 12)
        out.append(nib(arc, 2.6, seed=bx, taper=(0.3, 0.3)))
        for j in range(1, len(arc) - 1, 3):
            x, y = arc[j]
            out.append(line(x, y, x + (bx - x) * -0.12, y + (by - y) * -0.12, 1.3, seed=bx + j, cal=0))
    # toothpick + olive
    out.append(nib([(250, 62), (254, 210)], 3, seed=12, taper=(0.6, 1), cal=0))
    out.append(f'<ellipse cx="251" cy="92" rx="14" ry="12" fill="{INK}"/><ellipse cx="247" cy="89" rx="5" ry="3.6" fill="{pal[1]}"/>')
    for (cx_, cy_) in ((500, 236), (512, 248), (486, 250), (522, 232)):
        out.append(f'<path d="{blob(cx_, cy_, 3.8, 2.8, cx_, 0.25, 8)}" fill="{INK}"/>')
    # lettering
    out.append(tx(300, 316, "sorry for what I said", SERIF_IT, fit("sorry for what I said", SERIF_IT, 50, 440), INK))
    out.append(rule_label(U(), 300, 364, "WHEN I WAS", 30, 8, BEBAS, line_w=56, w=2.4))
    out.append(shade_text(U(), 300, 518, "HUNGRY", ANTON, fit("HUNGRY", ANTON, 136, 450, 6), ls=6, seed=13))
    out.append(finish(U))
    return "".join(out)


def pancakes(U, cx, base, w, n, seed, pal):
    out = []
    ry = w * 0.2
    th = 16
    out.append(shadow(cx + 8, base + 4, w * 0.62, ry * 0.6, 0.16))
    plate = E(cx, base, w * 0.66, ry * 0.9, 0, 360, 40)[:-1]
    out.append(f'<path d="{sm(plate)}" fill="{PAPER}"/>')
    out.append(nib(plate, 2.4, closed=True, seed=seed))
    for i in range(n):
        y = base - 6 - i * th
        rx = w / 2 - (i % 2) * 3
        side = poly(E(cx, y - th, rx, ry, 180, 0, 20) + E(cx, y, rx, ry, 0, 180, 20))
        sid = poly(E(cx, y - th, rx, ry, 0, 180, 20) + E(cx, y, rx, ry, 180, 0, 20))
        out.append(f'<path d="{sid}" fill="{PAPER}"/>')
        out.append(stipple(U(), sid, (cx - rx, y - th, cx + rx, y + ry), 70, seed + i, light=(cx - rx * 0.4, y - th), r=(0.6, 1.2)))
        out.append(hatch(U(), sid, (cx - rx, y - th, cx + rx, y + ry), 90, (8, 2.6), (0.8, 1.2), span=(0.5, 1), dark=(cx + rx, y), seed=seed + 10 + i))
        out.append(nib(E(cx, y, rx, ry, 0, 180, 20), 2.4, seed=seed + 20 + i, taper=(0.6, 0.6)))
        out.append(nib([(cx - rx, y), (cx - rx, y - th)], 2.2, seed=seed + 30 + i, taper=(1, 1)))
        out.append(nib([(cx + rx, y), (cx + rx, y - th)], 2.2, seed=seed + 40 + i, taper=(1, 1)))
    ytop = base - 6 - (n - 1) * th - th
    topd = sm(E(cx, ytop, w / 2, ry, 0, 360, 30)[:-1])
    out.append(f'<path d="{topd}" fill="{PAPER}"/>')
    # syrup
    syr = blob_pts(cx + 2, ytop + 2, w * 0.38, ry * 0.7, seed, 0.1, 16)
    syr_d = sm(syr)
    out.append(tint(U(), syr_d, pal, seed, 1, 0, 0))
    for dx, L in ((-0.3, 26), (0.05, 38), (0.36, 20)):
        x = cx + dx * w
        dp = [(x - 6, ytop + ry * 0.5), (x - 5, ytop + L), (x, ytop + L + 7), (x + 5, ytop + L), (x + 6, ytop + ry * 0.5)]
        out.append(f'<path d="{sm(dp)}" fill="{pal[1]}"/>')
        out.append(nib(dp[1:4], 1.8, seed=seed + int(L), taper=(0.3, 0.3)))
    out.append(nib(syr, 1.8, closed=True, seed=seed + 50))
    out.append(nib(E(cx, ytop, w / 2, ry, 0, 360, 30)[:-1], 2.4, closed=True, seed=seed + 51))
    # butter pat
    bp = [(cx - 14, ytop - 4), (cx + 6, ytop - 12), (cx + 20, ytop - 4), (cx + 20, ytop + 6), (cx, ytop + 14), (cx - 14, ytop + 6)]
    out.append(f'<path d="{poly(bp)}" fill="{PAPER}"/>')
    out.append(f'<path d="{poly([(cx, ytop + 4), (cx + 20, ytop - 4), (cx + 20, ytop + 6), (cx, ytop + 14)])}" fill="{pal[0]}"/>')
    out.append(nib(bp, 2, closed=True, smooth=False, seed=seed + 52))
    out.append(nib([(cx - 14, ytop - 4), (cx, ytop + 4), (cx + 20, ytop - 4)], 1.6, smooth=False, seed=seed + 53))
    out.append(nib([(cx, ytop + 4), (cx, ytop + 14)], 1.6, smooth=False, seed=seed + 54))
    return "".join(out)


def cup_saucer(U, cx, base, w, seed):
    out = []
    sau = E(cx, base, w * 0.72, w * 0.16, 0, 360, 30)[:-1]
    out.append(shadow(cx + 6, base + 4, w * 0.7, w * 0.12, 0.15))
    out.append(f'<path d="{sm(sau)}" fill="{PAPER}"/>')
    out.append(nib(sau, 2.4, closed=True, seed=seed))
    out.append(nib(E(cx, base - 2, w * 0.4, w * 0.08, 10, 170, 12), 1.4, seed=seed + 1))
    top = base - w * 0.66
    reg = [(cx - w / 2, top), (cx - w * 0.36, base - 8)] + E(cx, base - 8, w * 0.36, w * 0.08, 180, 0, 12)[1:-1] + [(cx + w * 0.36, base - 8), (cx + w / 2, top)] + E(cx, top, w / 2, w * 0.1, 0, 180, 12)[1:-1]
    rd = sm(reg)
    out.append(nib([(cx + w * 0.44, top + 8), (cx + w * 0.72, top + 4), (cx + w * 0.66, top + w * 0.36), (cx + w * 0.36, top + w * 0.44)], 3, seed=seed + 2, taper=(0.7, 0.7)))
    out.append(f'<path d="{rd}" fill="{PAPER}"/>')
    out.append(hatch(U(), rd, (cx - w / 2, top, cx + w / 2, base), 90, (12, 2.8), (0.7, 1.3), span=(0.5, 1), dark=(cx + w / 2, top + 20), seed=seed + 3))
    out.append(nib(reg[:len(reg) - 11], 2.8, seed=seed + 4, taper=(0.8, 0.8)))
    rim = E(cx, top, w / 2, w * 0.1, 0, 360, 24)[:-1]
    out.append(f'<path d="{sm(rim)}" fill="#4A3A2E"/>')
    out.append(nib(rim, 2.4, closed=True, seed=seed + 5))
    for i in range(2):
        out.append(steam(cx - 8 + i * 16, top - 10, 34 + i * 8, seed + 6 + i, 2.2))
    return "".join(out)


def flute(U, cx, base, h, seed, pal):
    out = []
    bw = h * 0.16
    btop, bbot = base - h, base - h * 0.42
    bowl = [(cx - bw, btop), (cx - bw * 0.9, btop + (bbot - btop) * 0.6), (cx - bw * 0.4, bbot - 4), (cx, bbot), (cx + bw * 0.4, bbot - 4), (cx + bw * 0.9, btop + (bbot - btop) * 0.6), (cx + bw, btop)]
    bd = sm(bowl + [(cx, btop - 2)])
    ly = btop + 16
    liq = poly(cr([(cx - bw * 0.99, ly), (cx - bw * 0.9, btop + (bbot - btop) * 0.6), (cx - bw * 0.4, bbot - 4), (cx, bbot), (cx + bw * 0.4, bbot - 4), (cx + bw * 0.9, btop + (bbot - btop) * 0.6), (cx + bw * 0.99, ly)]))
    out.append(shadow(cx + 6, base + 2, bw * 1.2, 5, 0.16))
    out.append(clipped(U(), bd, tint(U(), liq, pal, seed, 1, -90, 20, (10, 30), (2, 3), (cx - bw, ly, cx + bw, bbot))))
    rnd = random.Random(seed)
    for _ in range(9):
        bx, by = cx + rnd.uniform(-bw * 0.6, bw * 0.6), rnd.uniform(ly + 8, bbot - 10)
        out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{rnd.uniform(1.4, 2.6):.1f}" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    out.append(nib([(cx - bw, ly), (cx + bw, ly)], 1.6, seed=seed + 1, taper=(0.5, 0.5)))
    out.append(nib(bowl, 2.6, seed=seed + 2, taper=(0.6, 0.6)))
    out.append(nib(E(cx, btop, bw, 4, 0, 360, 16)[:-1], 1.8, closed=True, seed=seed + 3))
    out.append(nib([(cx - bw * 0.6, btop + 10), (cx - bw * 0.62, bbot - 20)], 3, color=PAPER, seed=seed + 4, op=0.9, cal=0))
    out.append(nib([(cx, bbot), (cx, base - 6)], 3, seed=seed + 5, taper=(1, 1), cal=0))
    foot = E(cx, base - 3, bw * 1.1, 5, 0, 360, 16)[:-1]
    out.append(f'<path d="{sm(foot)}" fill="{PAPER}"/>')
    out.append(nib(foot, 2.4, closed=True, seed=seed + 6))
    # orange slice on the rim
    os_ = E(cx + bw, btop + 2, 14, 14, 180, 360, 12)
    out.append(f'<path d="{poly(os_ + [(cx + bw, btop + 2)])}" fill="{pal[0]}"/>')
    out.append(nib(os_ + [(cx + bw, btop + 2)] + [os_[0]], 2, smooth=False, seed=seed + 7, taper=(1, 1)))
    for a in (210, 250, 290, 330):
        out.append(line(cx + bw, btop + 1, cx + bw + 11 * math.cos(math.radians(a)), btop + 2 + 11 * math.sin(math.radians(a)), 1.2, seed=a, cal=0))
    return "".join(out)


def croissant(U, cx, cy, w, seed, pal):
    out = []
    # segments along a downward-curving arc; outer ones small and pointed toward the tips
    segs = [(-0.44, 0.16, 0.09, 0.07, 50), (-0.3, 0.04, 0.13, 0.13, 30), (-0.15, -0.03, 0.15, 0.18, 14), (0, -0.05, 0.16, 0.21, 0),
            (0.15, -0.03, 0.15, 0.18, -14), (0.3, 0.04, 0.13, 0.13, -30), (0.44, 0.16, 0.09, 0.07, -50)]
    order = [0, 6, 1, 5, 2, 4, 3]
    out.append(shadow(cx + 6, cy + w * 0.2, w * 0.5, 6, 0.16))
    for k in order:
        dx, dy, rx, ry, rot = segs[k]
        pts = blob_pts(cx + dx * w, cy + dy * w, rx * w, ry * w, seed + k, 0.04, 16, rot + 90)
        d = sm(pts)
        out.append(f'<path d="{d}" fill="{PAPER}"/>')
        out.append(tint(U(), d, pal, seed + k, 0.7, 0, 0))
        out.append(hatch(U(), d, (cx + (dx - rx) * w, cy + (dy - ry) * w, cx + (dx + rx) * w, cy + (dy + ry) * w), 80 - rot, (8, 2.8), (0.7, 1.2), span=(0.5, 1),
                         dark=(cx + dx * w, cy + dy * w + ry * w), seed=seed + 10 + k))
        out.append(nib(pts, 2.2, closed=True, seed=seed + 20 + k))
        if abs(dx) < 0.35:
            out.append(nib([(cx + dx * w - rx * w * 0.4, cy + dy * w - ry * w * 0.55), (cx + dx * w + rx * w * 0.1, cy + dy * w - ry * w * 0.7)], 2.6, color=PAPER, seed=seed + 30 + k, op=0.8, cal=0))
    return "".join(out)


@design("brunch-squad")
def brunch_squad(U):
    pal = MUSTARD
    out = [ground(U, 30)]
    shelf = 306
    out.append(cup_saucer(U, 112, shelf - 6, 76, 3))
    out.append(pancakes(U, 252, shelf - 6, 136, 6, 4, pal))
    out.append(croissant(U, 396, shelf - 30, 150, 5, pal))
    out.append(flute(U, 504, shelf - 2, 200, 6, pal))
    out.append(nib([(64, shelf + 4), (300, shelf + 3), (536, shelf + 4)], 2.8, seed=7, taper=(0.2, 0.2)))
    out.append(dotrow(80, 520, shelf + 16, 11, 1.4))
    out.append(shade_text(U(), 300, 456, "BRUNCH", ANTON, fit("BRUNCH", ANTON, 128, 440, 8), ls=8, seed=8))
    out.append(tx(300, 530, "squad", SERIF_IT, 76, INK))
    out.append(nib([(120, 512), (164, 504), (200, 514)], 2.6, seed=9, taper=(0.1, 0.2), cal=0.6))
    out.append(nib([(400, 514), (436, 504), (480, 512)], 2.6, seed=10, taper=(0.2, 0.1), cal=0.6))
    out.append(finish(U))
    return "".join(out)


def romaine(U, cx, base, H, seed, pal):
    """A head of romaine: long ruffled leaves fanning up from the stump, pale ribs down the middle."""
    out = []
    rnd = random.Random(seed)
    leaves = [(-34, 0.78, 0.5), (34, 0.8, 0.55), (-20, 0.95, 0.75), (22, 0.97, 0.8), (-8, 1.0, 0.95), (9, 0.98, 1.0), (0, 0.9, 0.85)]
    for i, (ang, Lk, tone) in enumerate(leaves):
        a = math.radians(-90 + ang)
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        L = H * Lk
        W = H * 0.17
        pts = []
        side_pts = []
        for sgn in (1, -1):
            row = []
            for t in [j / 14 for j in range(15)]:
                wv = W * (0.18 + 0.82 * math.sin(math.pi * min(1, t * 0.95) ** 0.75)) * (1 - 0.25 * t)
                ruff = (2.6 + 3.4 * t) * math.sin(t * 38 + i) if t > 0.25 else 0
                row.append((cx + ux * L * t + nx * sgn * (wv + ruff), base + uy * L * t + ny * sgn * (wv + ruff)))
            side_pts.append(row)
        pts = side_pts[0] + side_pts[1][::-1]
        d = poly(cr(pts, True, 3))
        out.append(f'<path d="{d}" fill="{PAPER}"/>')
        out.append(f'<path d="{d}" fill="{mix(pal[0], pal[1], tone)}" opacity="0.9"/>')
        out.append(strokes(U(), d, (cx - H, base - H, cx + H, base), [pal[0], pal[2], pal[1]], seed + i, n=26, angle=-90 + ang, length=(16, 40), width=(2, 4), opacity=(0.15, 0.35)))
        # rib + veins
        rib = [(cx + ux * L * t, base + uy * L * t) for t in (0.0, 0.4, 0.8)]
        out.append(nib(rib, 7, seed=seed + 40 + i, taper=(1, 0.2), cal=0, color=PAPER, op=0.95))
        out.append(nib(rib, 1.6, seed=seed + 50 + i, taper=(1, 0.2), cal=0, op=0.7))
        veins = []
        for k in range(5):
            t = 0.25 + k * 0.14
            for sgn in (1, -1):
                px, py = cx + ux * L * t, base + uy * L * t
                qx, qy = px + ux * L * 0.12 + nx * sgn * W * 0.75, py + uy * L * 0.12 + ny * sgn * W * 0.75
                veins.append(nib([(px, py), ((px + qx) / 2 + ux * 3, (py + qy) / 2 + uy * 3), (qx, qy)], 1.2, seed=seed + 60 + i * 10 + k, taper=(0.8, 0.1)))
        out.append(clipped(U(), d, "".join(veins)))
        out.append(hatch(U(), d, (cx - H, base - H, cx + H, base), -90 + ang + 12, (9, 3.4), (0.7, 1.1), span=(0.62, 1),
                         dark=(cx + nx * W * (1 if ang >= 0 else -1) * 3, base - L * 0.4), seed=seed + 70 + i))
        out.append(nib(cr(pts, True, 3), 2.2, closed=True, smooth=False, seed=seed + 80 + i))
    stump = [(cx - 26, base - 10), (cx + 26, base - 10), (cx + 20, base + 8), (cx - 20, base + 8)]
    out.append(f'<path d="{sm(stump)}" fill="{PAPER}"/>')
    out.append(hatch(U(), sm(stump), (cx - 26, base - 12, cx + 26, base + 10), 90, (5, 3), (0.9, 1.1), span=(0.5, 1), dark=(cx + 26, base), seed=seed + 90))
    out.append(nib(stump, 2.4, closed=True, seed=seed + 91))
    return "".join(out)


@design("lettuce-eat")
def lettuce_eat(U):
    pal = SAGE
    out = [ground(U, 31)]
    out.append(blot(U, 300, 200, 190, 120, pal, 6, 0.16))
    out.append(shadow(310, 326, 120, 11, 0.16))
    out.append(romaine(U, 300, 318, 262, 3, pal))
    out.append(shade_text(U(), 300, 452, "LETTUCE", BEBAS, fit("LETTUCE", BEBAS, 140, 450, 8), ls=8, seed=4, dx=4, dy=4))
    out.append(tx(300, 530, "eat", SERIF_IT, 84, INK))
    out.append(nib([(150, 508), (196, 500), (236, 510)], 2.6, seed=5, taper=(0.1, 0.2), cal=0.6))
    out.append(nib([(364, 510), (404, 500), (450, 508)], 2.6, seed=6, taper=(0.2, 0.1), cal=0.6))
    out.append(finish(U))
    return "".join(out)


def olive(U, x, y, s, rot, seed, green=None):
    pts = E(x, y, s, s * 0.74, 0, 360, 20, rot)[:-1]
    d = sm(pts)
    out = [f'<path d="{d}" fill="{green or INK}"/>']
    if green:
        out.append(hatch(U(), d, (x - s, y - s, x + s, y + s), rot + 70, (3, 2.6), (1, 1), span=(0.5, 1), dark=(x + s * 0.6, y + s * 0.6), seed=seed))
    out.append(nib(pts, 2.2, closed=True, seed=seed + 1))
    out.append(f'<ellipse cx="{_f(x - s * 0.35)}" cy="{_f(y - s * 0.3)}" rx="{_f(s * 0.26)}" ry="{_f(s * 0.14)}" fill="{PAPER}" opacity="0.9" transform="rotate({rot} {_f(x - s * 0.35)} {_f(y - s * 0.3)})"/>')
    return "".join(out)


@design("olive-you")
def olive_you(U):
    pal = SAGE
    out = [ground(U, 32)]
    out.append(blot(U, 300, 190, 210, 110, pal, 3, 0.18, rot=-12))
    branch = [(84, 300), (170, 232), (280, 172), (390, 124), (496, 100)]
    out.append(nib(branch, 6, seed=4, taper=(1, 0.3), cal=0.2))
    B = cr(branch, False, 3)
    rnd = random.Random(5)
    stems = []
    for i in range(6, len(B) - 4, 7):
        px, py = B[i]
        qx, qy = B[i + 1]
        ang = math.degrees(math.atan2(qy - py, qx - px))
        side = 1 if (i // 7) % 2 else -1
        out.append(leaf(px, py, ang + side * rnd.uniform(35, 55), rnd.uniform(46, 58), rnd.uniform(8, 10), i, fill=pal[1] if (i // 7) % 3 else PAPER, bend=0.05, w=2))
        if (i // 7) % 3 == 1 and i < len(B) - 20:
            stems.append((px, py))
    for k, (px, py) in enumerate(stems):
        ox, oy = px + rnd.uniform(-6, 10), py + 30
        out.append(nib([(px, py), (ox - 2, oy - 18)], 1.8, seed=20 + k, taper=(1, 0.6)))
        out.append(olive(U, ox, oy, 16, 70, 30 + k, green=pal[1] if k % 2 else None))
    out.append(olive(U, 470, 140, 15, 80, 40))
    out.append(nib([(458, 108), (470, 124)], 1.8, seed=41))
    out.append(shade_text(U(), 300, 444, "OLIVE", DMS, fit("OLIVE", DMS, 148, 440, 8), ls=8, seed=6))
    out.append(tx(300, 528, "you", SERIF_IT, 84, INK))
    out.append(ink_heart(U, 404, 502, 16, None, 7, 2.2, fill=INK))
    out.append(nib([(150, 508), (196, 500), (234, 510)], 2.6, seed=8, taper=(0.1, 0.2), cal=0.6))
    out.append(finish(U))
    return "".join(out)


@design("youre-my-butter-half")
def butter_half(U):
    pal = MUSTARD
    out = [ground(U, 33)]
    # dish (a long tray in perspective)
    tray = [(110, 200), (430, 172), (500, 228), (176, 262)]
    td = sm(tray)
    out.append(shadow(316, 262, 200, 18, 0.15))
    out.append(f'<path d="{td}" fill="{PAPER}"/>')
    inner = tr(tray, sx=0.86, sy=0.78, ox=304, oy=216)
    out.append(nib(inner, 1.6, closed=True, seed=3))
    out.append(hatch(U(), td, (100, 160, 510, 270), 20, (12, 3.2), (0.7, 1.2), span=(0.62, 1), dark=(400, 262), seed=4))
    out.append(nib(tray, 3, closed=True, seed=5))
    # butter block: top + front + side faces
    t = [(196, 176), (366, 160), (406, 190), (236, 208)]
    f = [(236, 208), (406, 190), (406, 228), (236, 248)]
    sd = [(196, 176), (236, 208), (236, 248), (196, 214)]
    for face, op in ((t, 0.5), (f, 0.9), (sd, 0.75)):
        d = poly(face)
        out.append(f'<path d="{d}" fill="{PAPER}"/>')
        out.append(f'<path d="{d}" fill="{pal[0]}" opacity="{op}"/>')
    out.append(hatch(U(), poly(f), (236, 186, 406, 250), 90, (5, 3), (0.9, 1.1), seed=6, op=0.8))
    out.append(stipple(U(), poly(t), (196, 158, 406, 210), 80, 7, r=(0.5, 1), op=0.5))
    for face in (t, f, sd):
        out.append(nib(face, 2.4, closed=True, smooth=False, seed=8 + len(face)))
    # knife resting with a butter curl
    kb = [(258, 150), (400, 112), (452, 108), (420, 126), (262, 160)]
    out.append(f'<path d="{poly(kb)}" fill="{PAPER}"/>')
    out.append(hatch(U(), poly(kb), (258, 104, 452, 162), 0, (4, 3), (0.9, 1), span=(0.6, 1), dark=(300, 160), seed=9))
    out.append(nib(kb, 2.4, closed=True, smooth=False, seed=10))
    kh = [(258, 150), (262, 160), (160, 190), (150, 180)]
    out.append(f'<path d="{sm(kh)}" fill="{INK}"/>')
    curl = [(330, 128), (352, 108), (378, 110), (384, 126), (368, 138), (350, 132)]
    out.append(f'<path d="{sm(curl)}" fill="{pal[0]}"/>')
    out.append(nib(curl, 2, closed=True, seed=11))
    out.append(nib([(342, 126), (360, 116), (374, 122)], 1.4, seed=12))
    # lettering
    out.append(tx(300, 338, "you're my", SERIF_IT, 58, INK))
    out.append(shade_text(U(), 300, 462, "BUTTER", ANTON, fit("BUTTER", ANTON, 120, 440, 8), ls=8, seed=13))
    out.append(tx(300, 530, "half", SERIF_IT, 76, INK))
    out.append(ink_heart(U, 130, 504, 14, pal, 14, 2))
    out.append(ink_heart(U, 470, 504, 14, pal, 15, 2))
    out.append(finish(U))
    return "".join(out)


def donut(U, cx, cy, R, seed, pal):
    out = []
    ry = R * 0.62
    rnd = random.Random(seed)
    out.append(shadow(cx + 10, cy + ry + 14, R * 0.95, 12, 0.16))
    body = E(cx, cy + 10, R, ry + 8, 0, 360, 60)[:-1]
    bd = sm(body)
    out.append(f'<path d="{bd}" fill="{PAPER}"/>')
    out.append(stipple(U(), bd, (cx - R, cy - ry, cx + R, cy + ry + 20), 220, seed, light=(cx - R * 0.5, cy), r=(0.6, 1.2)))
    out.append(hatch(U(), bd, (cx - R, cy - ry, cx + R, cy + ry + 20), 90, (12, 3), (0.7, 1.3), span=(0.55, 1), dark=(cx + R, cy + ry), seed=seed + 1))
    out.append(nib(body, 3, closed=True, seed=seed + 2))
    # glaze with drips
    gl = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        k = 0.9 + 0.04 * math.sin(i * 1.7)
        drip = 0
        if math.sin(a) > 0.2 and i % 5 == 0:
            drip = rnd.uniform(10, 22)
        gl.append((cx + R * k * math.cos(a), cy + ry * k * math.sin(a) + drip * math.sin(a)))
    gd = poly(cr(gl, True))
    out.append(f'<path d="{gd}" fill="{mix(pal[0], PAPER, 0.3)}"/>')
    out.append(strokes(U(), gd, (cx - R, cy - ry, cx + R, cy + ry + 20), [pal[0], pal[1], mix(pal[0], PAPER, 0.5)], seed + 3, n=70, angle=10, length=(20, 50), width=(3, 7), opacity=(0.2, 0.5)))
    out.append(hatch(U(), gd, (cx - R, cy - ry, cx + R, cy + ry + 20), 30, (12, 3.2), (0.7, 1.2), span=(0.6, 1), dark=(cx + R, cy + ry), seed=seed + 4))
    out.append(nib(cr(gl, True), 2.6, closed=True, smooth=False, seed=seed + 5))
    # hole
    hole = E(cx, cy - 4, R * 0.3, ry * 0.3, 0, 360, 30)[:-1]
    out.append(f'<path d="{sm(hole)}" fill="{PAPER}"/>')
    out.append(hatch(U(), sm(hole), (cx - R * 0.3, cy - ry * 0.4, cx + R * 0.3, cy + ry * 0.3), 0, (2.8, 2.8), (1, 1), seed=seed + 6,
                     clip2=poly(E(cx, cy - 4, R * 0.3, ry * 0.3, 180, 360, 16))))
    out.append(nib(hole, 2.6, closed=True, seed=seed + 7))
    # sprinkles
    placed = 0
    tries = 0
    while placed < 46 and tries < 500:
        tries += 1
        a = rnd.uniform(0, 6.28)
        d = rnd.uniform(0.42, 0.84)
        x, y = cx + R * d * math.cos(a), cy + ry * d * math.sin(a)
        r_ = math.radians(rnd.uniform(0, 180))
        L = 7
        p0 = (x - L * math.cos(r_), y - L * math.sin(r_))
        p1 = (x + L * math.cos(r_), y + L * math.sin(r_))
        out.append(nib([p0, p1], 5.6, seed=seed + placed, taper=(1, 1), cal=0, smooth=False))
        if placed % 3:
            out.append(nib([p0, p1], 2.4, seed=seed + 100 + placed, taper=(1, 1), cal=0, smooth=False, color=PAPER))
        placed += 1
    out.append(nib(E(cx - R * 0.1, cy - 2, R * 0.72, ry * 0.7, 200, 250, 10), 4, color=PAPER, seed=seed + 8, op=0.8, cal=0))
    return "".join(out)


@design("donut-worry")
def donut_worry(U):
    pal = TOMATO
    out = [ground(U, 34)]
    out.append(donut(U, 300, 190, 168, 3, pal))
    for (sx, sy, r) in ((96, 108, 9), (500, 96, 11), (520, 268, 7), (80, 280, 7)):
        out.append(sparkle(sx, sy, r, w=2.2))
    out.append(shade_text(U(), 300, 446, "DONUT", ANTON, fit("DONUT", ANTON, 128, 440, 12), ls=12, seed=4))
    out.append(tx(300, 530, "worry", SERIF_IT, 84, INK))
    out.append(nib([(120, 506), (160, 498), (196, 508)], 2.6, seed=5, taper=(0.1, 0.2), cal=0.6))
    out.append(nib([(404, 508), (440, 498), (480, 506)], 2.6, seed=6, taper=(0.2, 0.1), cal=0.6))
    out.append(finish(U))
    return "".join(out)


def slice_pts(cx, cy, w, h, rot=0):
    """Classic bread slice outline: a square body with two rounded shoulders on top."""
    p = [(-0.42, 0.5), (0.42, 0.5), (0.46, 0.0), (0.44, -0.18), (0.56, -0.3), (0.5, -0.46), (0.24, -0.52), (0, -0.48), (-0.24, -0.52), (-0.5, -0.46), (-0.56, -0.3), (-0.44, -0.18), (-0.46, 0.0)]
    return tr([(cx + x * w, cy + y * h) for x, y in p], ox=cx, oy=cy, rot=rot)


def bread_slice(U, cx, cy, w, h, rot, seed, pal):
    out = []
    pts = slice_pts(cx, cy, w, h, rot)
    d = sm(pts)
    inner = slice_pts(cx, cy, w * 0.84, h * 0.86, rot)
    idd = sm(inner)
    out.append(f'<path d="{d}" fill="{PAPER}"/>')
    out.append(tint(U(), d, pal, seed, 0.85, 0, 0))
    out.append(f'<path d="{idd}" fill="{PAPER}"/>')
    out.append(stipple(U(), idd, (cx - w, cy - h, cx + w, cy + h), int(w * 1.4), seed, r=(0.5, 1.3), op=0.6))
    rnd = random.Random(seed)
    for _ in range(7):
        x, y = cx + rnd.uniform(-0.3, 0.3) * w, cy + rnd.uniform(-0.3, 0.35) * h
        out.append(nib(E(x, y, rnd.uniform(2, 4), rnd.uniform(1.4, 2.6), 0, 300, 8, rnd.uniform(0, 90)), 1.2, seed=rnd.randint(0, 999), taper=(0.4, 0.4)))
    # crust shading on the shadow side + crumb shading low right
    out.append(hatch(U(), d, (cx - w, cy - h, cx + w, cy + h), 60 + rot, (9, 3), (0.7, 1.2), span=(0.58, 1), dark=(cx + w * 0.6, cy + h * 0.6), seed=seed + 3))
    out.append(nib(inner, 1.6, closed=True, seed=seed + 1, op=0.85))
    out.append(nib(pts, 3, closed=True, seed=seed + 2))
    return "".join(out)


def wheat(x, y, ang, L, seed, w=2):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    out = [nib([(x, y), (x + ux * L, y + uy * L)], w, seed=seed, taper=(1, 0.6), cal=0)]
    for i in range(7):
        t = 0.45 + i * 0.075
        px, py = x + ux * L * t, y + uy * L * t
        for sgn in (-1, 1):
            g = leaf_pts(px, py, ang + sgn * 28, 18, 5, 0)
            out.append(f'<path d="{sm(g)}" fill="{PAPER}"/>')
            out.append(nib(g, 1.6, closed=True, seed=seed + i * 2 + sgn))
            out.append(nib([(px + math.cos(math.radians(ang + sgn * 28)) * 16, py + math.sin(math.radians(ang + sgn * 28)) * 16),
                            (px + math.cos(math.radians(ang + sgn * 18)) * 34, py + math.sin(math.radians(ang + sgn * 18)) * 34)], 0.9, seed=seed + 50 + i, cal=0))
    tip = leaf_pts(x + ux * L * 0.98, y + uy * L * 0.98, ang, 20, 5, 0)
    out.append(f'<path d="{sm(tip)}" fill="{PAPER}"/>' + nib(tip, 1.6, closed=True, seed=seed + 99))
    return "".join(out)


@design("best-thing-since-sliced-bread")
def sliced_bread(U):
    pal = MUSTARD
    out = [ground(U, 35)]
    out.append(wheat(150, 290, -112, 210, 3))
    out.append(wheat(454, 290, -68, 210, 4))
    # loaf behind, slices fanned in front
    # the loaf: a long crusty body seen from the cut end, slices falling forward
    body = [(330, 100), (420, 92), (468, 104), (482, 150), (474, 280), (380, 290), (340, 286)]
    bd = sm(body)
    out.append(shadow(320, 296, 200, 12, 0.18))
    out.append(f'<path d="{bd}" fill="{PAPER}"/>')
    out.append(tint(U(), bd, pal, 4, 0.9, -10, 30, (20, 50), (3, 6), (330, 90, 484, 292)))
    out.append(hatch(U(), bd, (330, 90, 484, 292), 80, (10, 3), (0.8, 1.3), span=(0.4, 1), dark=(484, 290), seed=5))
    for k, x in enumerate((372, 404, 436)):
        out.append(nib([(x, 104 + k * 2), (x + 12, 124), (x + 18, 150)], 2.2, seed=40 + k, taper=(0.3, 0.3)))
    out.append(nib(body, 3, closed=True, seed=6))
    out.append(bread_slice(U, 356, 190, 180, 196, 0, 7, pal))
    out.append(bread_slice(U, 294, 204, 166, 176, -9, 8, pal))
    out.append(bread_slice(U, 234, 218, 148, 156, -18, 9, pal))
    # lettering
    out.append(tx(300, 360, "best thing since", SERIF_IT, fit("best thing since", SERIF_IT, 54, 420), INK))
    out.append(shade_text(U(), 300, 470, "SLICED", ANTON, fit("SLICED", ANTON, 112, 420, 10), ls=10, seed=9))
    out.append(ribbon(U(), 300, 512, 230, 46, "BREAD", BEBAS, 40, pal[1], ls=10, bend=-5, tcolor=INK, seed=10, text_dy=14, tail=30))
    out.append(finish(U))
    return "".join(out)


def dutch_oven(U, cx, cy, w, seed, pal):
    out = []
    h = w * 0.5
    ry = w * 0.14
    top, bot = cy - h / 2, cy + h / 2
    rt, rb = w / 2, w / 2 - 6
    region, outline, rim = cyl(cx, top, bot, rt, rb, ry)
    rd = poly(region)
    out.append(shadow(cx + 10, bot + ry * 0.7, w * 0.6, ry * 0.6, 0.18))
    # side loop handles
    for sgn in (-1, 1):
        hx = cx + sgn * rt
        loop = [(hx, top + 14), (hx + sgn * 24, top + 10), (hx + sgn * 30, top + 26), (hx + sgn * 22, top + 40), (hx, top + 38)]
        out.append(nib(loop, 6, seed=seed + sgn, taper=(0.7, 0.7), cal=0))
    out.append(f'<path d="{rd}" fill="{PAPER}"/>')
    out.append(tint(U(), rd, pal, seed, 1, -90, 40, (20, 50), (3, 7), (cx - rt, top, cx + rt, bot)))
    out.append(hatch(U(), rd, (cx - rt, top - ry, cx + rt, bot + ry), 90, (14, 3.2), (0.7, 1.4), span=(0.45, 1), dark=(cx + rt, cy), seed=seed + 1))
    out.append(hatch(U(), rd, (cx - rt, top - ry, cx + rt, bot + ry), 30, (4.2, 3.8), (0.9, 1), span=(0.88, 1), dark=(cx + rt, bot), seed=seed + 2))
    out.append(nib(outline, 3.4, seed=seed + 3, taper=(0.9, 0.9)))
    out.append(nib(E(cx, top + 10, rt, ry, 10, 170, 20), 1.6, seed=seed + 4))
    out.append(nib([(cx - rt + 16, top + ry + 10), (cx - rt + 16, bot - 8)], 4, color=PAPER, seed=seed + 5, op=0.8, cal=0))
    # lid, slightly ajar
    lid_y = top - 6
    lid = [(cx - rt - 6, lid_y + 4)] + E(cx, lid_y, rt + 6, ry + 30, 190, 350, 24) + [(cx + rt + 6, lid_y + 4)] + E(cx, lid_y + 4, rt + 6, ry * 0.8, 0, 180, 20)[1:-1]
    lidd = poly(cr(lid, True, 3))
    g = f'<g transform="rotate(-5 {cx} {lid_y})">'
    out.append(g)
    out.append(f'<path d="{lidd}" fill="{PAPER}"/>')
    out.append(tint(U(), lidd, pal, seed + 6, 1, 0, 0))
    out.append(hatch(U(), lidd, (cx - rt - 6, lid_y - ry - 30, cx + rt + 6, lid_y + ry), 70, (12, 3.2), (0.7, 1.2), span=(0.5, 1), dark=(cx + rt, lid_y), seed=seed + 7))
    out.append(nib(cr(lid, True, 3), 3, closed=True, smooth=False, seed=seed + 8))
    out.append(nib(E(cx - 20, lid_y - 18, rt * 0.6, 10, 200, 260, 8), 3.4, color=PAPER, seed=seed + 9, op=0.8, cal=0))
    knob = [(cx - 16, lid_y - ry - 26), (cx - 12, lid_y - ry - 40), (cx + 12, lid_y - ry - 40), (cx + 16, lid_y - ry - 26)]
    out.append(f'<path d="{sm(knob)}" fill="{INK}"/>')
    out.append("</g>")
    for i in range(3):
        out.append(steam(cx - rt + 4 + i * 12, lid_y + 2, 50 + i * 8, seed + 20 + i, 2.6))
    return "".join(out)


@design("home-cooking")
def home_cooking(U):
    pal = TOMATO
    out = [ground(U, 36)]
    cx, cy = 300, 300
    out.append(nib(E(cx, cy, 236, 236, 0, 360, 90)[:-1], 4, closed=True, seed=2))
    out.append(nib(E(cx, cy, 226, 226, 0, 360, 90)[:-1], 1.4, closed=True, seed=3))
    out.append(nib(E(cx, cy, 152, 152, 0, 360, 72)[:-1], 1.4, closed=True, seed=4))
    out.append(nib(E(cx, cy, 144, 144, 0, 360, 72)[:-1], 3, closed=True, seed=5))
    # hatched band between the rings
    band = poly(E(cx, cy, 226, 226, 0, 360, 90)) + " " + poly(E(cx, cy, 152, 152, 0, 360, 90)[::-1])
    out.append(f'<path d="{band}" fill="{PAPER}" fill-rule="evenodd" opacity="0"/>')
    out.append(arc_label(U(), "HOME COOKING", cx, cy, 172, BEBAS, 58, INK, 8, top=True))
    out.append(arc_label(U(), "MADE FROM SCRATCH", cx, cy, 200, MONO, 22, INK, 5, top=False))
    for sgn in (-1, 1):
        sx = cx + sgn * 189
        out.append(f'<polygon points="{star_pts(sx, cy, 11, 4.5)}" fill="{INK}"/>')
    out.append(dutch_oven(U, cx, cy + 44, 196, 6, pal))
    out.append(finish(U))
    return "".join(out)


def star_pts(cx, cy, ro, ri, n=5):
    pts = []
    for i in range(n * 2):
        r = ro if i % 2 == 0 else ri
        a = math.radians(-90 + i * 180 / n)
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return " ".join(pts)


def egg(U, cx, cy, s, rot, seed, fill=None):
    pts = [(cx + s * 0.62 * math.sin(math.radians(a)) * (1 - 0.12 * math.cos(math.radians(a))), cy - s * 0.8 * math.cos(math.radians(a))) for a in range(0, 360, 18)]
    pts = tr(pts, ox=cx, oy=cy, rot=rot)
    d = sm(pts)
    return (f'<path d="{d}" fill="{fill or PAPER}"/>'
            + hatch(U(), d, (cx - s, cy - s, cx + s, cy + s), rot + 70, (5, 2.6), (0.8, 1.1), span=(0.55, 1), dark=(cx + s * 0.6, cy + s * 0.6), seed=seed)
            + nib(pts, 2.2, closed=True, seed=seed + 1))


def egg_basket(U, cx, base, w, seed, pal):
    out = []
    h = w * 0.5
    ry = w * 0.14
    top = base - h
    # handle behind
    out.append(nib(E(cx, top, w * 0.46, h * 1.3, 180, 360, 30), 4, seed=seed, taper=(1, 1), cal=0))
    # eggs piled
    for i, (dx, dy, r) in enumerate(((-0.28, -0.04, 10), (-0.08, -0.12, -6), (0.14, -0.1, 14), (0.32, -0.02, -10), (0.02, 0.0, 4), (-0.18, 0.04, 0), (0.22, 0.04, 6))):
        out.append(egg(U, cx + dx * w, top + dy * w, w * 0.12, r, seed + 10 + i))
    # wire body
    body = [(cx - w / 2, top), (cx - w * 0.4, base)] + E(cx, base, w * 0.4, ry, 180, 0, 16)[1:-1] + [(cx + w * 0.4, base), (cx + w / 2, top)] + E(cx, top, w / 2, ry, 0, 180, 16)[1:-1]
    bd = poly(body)
    inner = []
    for k in range(9):
        t = k / 8
        x0_ = cx - w / 2 + w * t
        x1_ = cx - w * 0.4 + w * 0.8 * t
        yb = base + ry * math.sin(math.acos(max(-1, min(1, (x1_ - cx) / (w * 0.4))))) if abs(x1_ - cx) < w * 0.4 else base
        yt = top + ry * math.sin(math.acos(max(-1, min(1, (x0_ - cx) / (w / 2))))) if abs(x0_ - cx) < w / 2 else top
        inner.append(nib([(x0_, yt), (x1_, yb)], 1.6, seed=seed + 30 + k, taper=(1, 1), cal=0))
    for k in range(1, 4):
        y = top + h * k / 4
        rx = w / 2 - w * 0.1 * k / 4
        inner.append(nib(E(cx, y, rx, ry, 0, 180, 20), 1.6, seed=seed + 40 + k, taper=(1, 1)))
    out.append(clipped(U(), bd, "".join(inner)))
    out.append(nib(body[:len(body) - 15], 3, seed=seed + 50, taper=(1, 1)))
    out.append(nib(E(cx, top, w / 2, ry, 0, 180, 20), 3.2, seed=seed + 51, taper=(1, 1)))
    # sage ribbon bow on the handle
    bx, by = cx - w * 0.36, top - h * 0.92
    for sgn in (-1, 1):
        lp = [(bx, by), (bx + sgn * 20, by - 12), (bx + sgn * 24, by + 4), (bx, by)]
        out.append(f'<path d="{sm(lp)}" fill="{pal[1]}"/>' + nib(lp, 1.8, closed=True, seed=seed + 60 + sgn))
        out.append(nib([(bx, by), (bx + sgn * 10, by + 24)], 3, seed=seed + 62 + sgn, color=pal[2], cal=0))
    out.append(f'<circle cx="{bx}" cy="{by}" r="5" fill="{INK}"/>')
    return "".join(out)


def milk_bottle(U, cx, base, h, seed, pal):
    out = []
    w = h * 0.42
    pts = [(cx - w * 0.5, base - 6), (cx - w * 0.52, base - h * 0.52), (cx - w * 0.34, base - h * 0.74), (cx - w * 0.26, base - h * 0.9), (cx - w * 0.26, base - h),
           (cx + w * 0.26, base - h), (cx + w * 0.26, base - h * 0.9), (cx + w * 0.34, base - h * 0.74), (cx + w * 0.52, base - h * 0.52), (cx + w * 0.5, base - 6), (cx + w * 0.4, base), (cx - w * 0.4, base)]
    d = sm(pts)
    out.append(shadow(cx + 6, base + 2, w * 0.6, 5, 0.16))
    out.append(f'<path d="{d}" fill="{PAPER}"/>')
    out.append(hatch(U(), d, (cx - w, base - h, cx + w, base), 90, (14, 3), (0.7, 1.3), span=(0.55, 1), dark=(cx + w * 0.5, base - h * 0.4), seed=seed))
    lab = poly([(cx - w * 0.52, base - h * 0.44), (cx + w * 0.52, base - h * 0.44), (cx + w * 0.5, base - h * 0.2), (cx - w * 0.5, base - h * 0.2)])
    out.append(clipped(U(), d, f'<path d="{lab}" fill="{pal[1]}"/>'))
    out.append(tx(cx, base - h * 0.27, "MILK", BEBAS, 22, PAPER, 2))
    out.append(nib(pts, 2.8, closed=True, seed=seed + 1))
    cap = [(cx - w * 0.3, base - h - 2), (cx + w * 0.3, base - h - 2), (cx + w * 0.28, base - h + 10), (cx - w * 0.28, base - h + 10)]
    out.append(f'<path d="{poly(cap)}" fill="{INK}"/>')
    out.append(nib([(cx - w * 0.3, base - h * 0.66), (cx - w * 0.36, base - h * 0.5), (cx - w * 0.36, base - h * 0.08)], 3.4, color=PAPER, seed=seed + 2, op=0.85, cal=0))
    return "".join(out)


@design("farmhouse-kitchen")
def farmhouse_kitchen(U):
    pal = SAGE
    out = [ground(U, 37)]
    out.append(rule_label(U(), 300, 98, "FRESH EGGS · WARM BREAD", 18, 3, line_w=26, gap=10))
    out.append(shade_text(U(), 300, 182, "FARMHOUSE", CINZEL, fit("FARMHOUSE", CINZEL, 70, 450, 4), ls=4, seed=3, dx=3, dy=3))
    out.append(engraved(U(), 300, 298, "KITCHEN", BEBAS, fit("KITCHEN", BEBAS, 136, 450, 10), ls=10, sw=3.2, gap=3, hw=1.2, ang=-30))
    out.append(blot(U, 300, 450, 220, 80, pal, 4, 0.18))
    out.append(nib([(70, 526), (300, 524), (530, 527)], 2.6, seed=5, taper=(0.2, 0.2)))
    out.append(milk_bottle(U, 148, 524, 150, 6, pal))
    out.append(egg_basket(U, 320, 520, 170, 7, pal))
    out.append(wheat(468, 524, -80, 170, 8))
    out.append(wheat(484, 524, -96, 150, 9))
    out.append(finish(U))
    return "".join(out)


@design("coffee-and-kindness")
def coffee_kindness(U):
    pal = TOMATO
    out = [ground(U, 38)]
    out.append(blot(U, 300, 190, 190, 100, pal, 5, 0.14))
    left = mug2(U, 210, 150, 120, 110, 3, steam_n=0)
    right = mug2(U, 390, 150, 120, 110, 4, steam_n=0)
    out.append(f'<g transform="rotate(14 210 260) translate(420 0) scale(-1 1)">{left}</g>')
    out.append(f'<g transform="rotate(-14 390 260)">{right}</g>')
    # clink splashes
    for (x, y, a) in ((300, 112, -90), (282, 118, -130), (318, 118, -50), (300, 98, -90)):
        out.append(line(x, y, x + 16 * math.cos(math.radians(a)), y + 16 * math.sin(math.radians(a)), 2.2, seed=int(x + y), cal=0, taper=(0.2, 0.9)))
    for (x, y, r) in ((262, 96, 4), (340, 92, 5), (300, 70, 3.5)):
        out.append(f'<path d="M {x} {y - r * 1.8} q {r} {r * 1.6} 0 {r * 2.6} q {-r} {-r} 0 {-r * 2.6} Z" fill="{INK}"/>')
    out.append(ink_heart(U, 300, 288, 22, pal, 6, 2.4))
    out.append(tx(300, 382, "coffee &", SERIF_IT, 76, INK))
    out.append(shade_text(U(), 300, 494, "KINDNESS", BEBAS, fit("KINDNESS", BEBAS, 132, 450, 6), ls=6, seed=7, dx=4, dy=4))
    out.append(rule_label(U(), 300, 534, "POUR GENEROUSLY", 18, 4, line_w=34, gap=10))
    out.append(finish(U))
    return "".join(out)


def cloche(U, cx, base, w, seed, pal, lift=0):
    out = []
    ry = w * 0.12
    # platter
    pl = E(cx, base, w * 0.66, ry * 1.4, 0, 360, 48)[:-1]
    out.append(shadow(cx + 12, base + ry * 1.2, w * 0.66, ry, 0.16))
    out.append(f'<path d="{sm(pl)}" fill="{PAPER}"/>')
    out.append(hatch(U(), sm(pl), (cx - w, base - ry * 2, cx + w, base + ry * 2), 90, (12, 3), (0.7, 1.2), span=(0.5, 1), dark=(cx + w, base), seed=seed))
    out.append(nib(pl, 2.8, closed=True, seed=seed + 1))
    out.append(nib(E(cx, base - 2, w * 0.56, ry * 1.1, 0, 360, 48)[:-1], 1.4, closed=True, seed=seed + 2))
    # dome
    b = base - lift
    dome = [(cx - w / 2, b)] + E(cx, b, w / 2, w * 0.56, 180, 360, 30)[1:-1] + [(cx + w / 2, b)] + E(cx, b, w / 2, ry, 0, 180, 20)[1:-1]
    dd = poly(cr(dome, True, 3))
    out.append(f'<path d="{dd}" fill="{PAPER}"/>')
    out.append(contour(U(), dd, cx, b - w * 0.5, b + 4, w / 2, ry * 1.6, 7, 1.0, seed=seed + 3, a0=8, a1=172, op=0.35))
    out.append(hatch(U(), dd, (cx - w / 2, b - w * 0.6, cx + w / 2, b + ry), 75, (14, 3), (0.7, 1.4), span=(0.45, 1), dark=(cx + w / 2, b - w * 0.2), seed=seed + 4))
    out.append(hatch(U(), dd, (cx - w / 2, b - w * 0.6, cx + w / 2, b + ry), 20, (4, 3.6), (0.9, 1), span=(0.86, 1), dark=(cx + w / 2, b), seed=seed + 5))
    # mirror highlights (a bright window reflection)
    hl = [(cx - w * 0.3, b - w * 0.36), (cx - w * 0.22, b - w * 0.46), (cx - w * 0.14, b - w * 0.42), (cx - w * 0.24, b - w * 0.12), (cx - w * 0.33, b - w * 0.1)]
    out.append(f'<path d="{sm(hl)}" fill="{PAPER}"/>')
    out.append(nib([(cx + w * 0.06, b - w * 0.5), (cx + w * 0.16, b - w * 0.44)], 3.4, color=PAPER, seed=seed + 6, cal=0))
    out.append(nib(cr(dome, True, 3), 3.2, closed=True, smooth=False, seed=seed + 7))
    out.append(nib(E(cx, b - 8, w / 2 - 3, ry, 15, 165, 20), 1.6, seed=seed + 8))
    # knob in brass
    kn = [(cx - 16, b - w * 0.56 + 2), (cx - 12, b - w * 0.56 - 10), (cx - 20, b - w * 0.56 - 22), (cx, b - w * 0.56 - 32), (cx + 20, b - w * 0.56 - 22), (cx + 12, b - w * 0.56 - 10), (cx + 16, b - w * 0.56 + 2)]
    out.append(f'<path d="{sm(kn)}" fill="{pal[1]}"/>')
    out.append(hatch(U(), sm(kn), (cx - 20, b - w * 0.56 - 34, cx + 20, b - w * 0.56 + 4), 90, (5, 2.6), (0.8, 1.1), span=(0.5, 1), dark=(cx + 20, b - w * 0.56), seed=seed + 9))
    out.append(nib(kn, 2.2, closed=True, seed=seed + 10))
    return "".join(out)


@design("dinner-is-served")
def dinner_served(U):
    pal = MUSTARD
    out = [ground(U, 39)]
    out.append(blot(U, 300, 200, 200, 120, pal, 6, 0.16))
    out.append(cloche(U, 300, 268, 290, 3, pal, lift=14))
    # steam escaping from under the lifted lid
    for i, (x, h) in enumerate(((132, 56), (150, 74), (452, 70), (470, 54))):
        out.append(steam(x, 268, h, 20 + i, 2.6))
    for (sx, sy, r) in ((94, 112, 10), (506, 120, 12), (522, 230, 7), (80, 236, 7)):
        out.append(sparkle(sx, sy, r, w=2.2))
    out.append(shade_text(U(), 300, 440, "DINNER", CINZEL, fit("DINNER", CINZEL, 100, 440, 8), ls=8, seed=7, dx=3.5, dy=3.5))
    out.append(tx(300, 520, "is served", SERIF_IT, 70, INK))
    out.append(nib([(96, 500), (136, 492), (156, 502)], 2.6, seed=8, taper=(0.1, 0.2), cal=0.6))
    out.append(nib([(444, 502), (464, 492), (504, 500)], 2.6, seed=9, taper=(0.2, 0.1), cal=0.6))
    out.append(finish(U))
    return "".join(out)


def teapot_cozy(U, cx, base, w, seed, pal):
    out = []
    h = w * 0.78
    top = base - h
    # spout and handle poking out
    sp = [(cx - w * 0.36, base - h * 0.3), (cx - w * 0.6, base - h * 0.44), (cx - w * 0.7, base - h * 0.72), (cx - w * 0.62, base - h * 0.74), (cx - w * 0.54, base - h * 0.56), (cx - w * 0.34, base - h * 0.48)]
    spd = sm(sp)
    out.append(shadow(cx + 10, base + 4, w * 0.62, 10, 0.16))
    out.append(f'<path d="{spd}" fill="{PAPER}"/>')
    out.append(hatch(U(), spd, (cx - w * 0.72, base - h * 0.8, cx - w * 0.3, base - h * 0.28), 20, (4, 3), (1, 1), span=(0.5, 1), dark=(cx - w * 0.4, base - h * 0.3), seed=seed))
    out.append(nib(sp, 2.6, closed=True, seed=seed + 1))
    out.append(nib([(cx + w * 0.4, base - h * 0.64), (cx + w * 0.68, base - h * 0.62), (cx + w * 0.66, base - h * 0.3), (cx + w * 0.4, base - h * 0.24)], 8, seed=seed + 2, taper=(1, 1), cal=0))
    out.append(nib([(cx + w * 0.42, base - h * 0.6), (cx + w * 0.62, base - h * 0.58), (cx + w * 0.6, base - h * 0.32), (cx + w * 0.42, base - h * 0.28)], 3, seed=seed + 3, taper=(1, 1), cal=0, color=PAPER))
    # base of the pot below the cozy
    pb = [(cx - w * 0.44, base - 16), (cx + w * 0.44, base - 16), (cx + w * 0.4, base), (cx - w * 0.4, base)]
    out.append(f'<path d="{sm(pb)}" fill="{PAPER}"/>')
    out.append(hatch(U(), sm(pb), (cx - w / 2, base - 18, cx + w / 2, base + 2), 90, (8, 3), (0.8, 1.2), span=(0.5, 1), dark=(cx + w / 2, base), seed=seed + 4))
    out.append(nib(pb, 2.4, closed=True, seed=seed + 5))
    # knitted cozy dome
    dome = [(cx - w * 0.48, base - 14)] + E(cx, base - 14, w * 0.48, h * 0.86, 180, 360, 30)[1:-1] + [(cx + w * 0.48, base - 14), (cx, base - 6)]
    dd = poly(cr(dome, True, 3))
    out.append(f'<path d="{dd}" fill="{PAPER}"/>')
    knit = [tint(U(), dd, pal, seed + 6, 1, 0, 0)]
    cols = 9
    for c in range(cols):
        x = cx - w * 0.44 + c * w * 0.88 / (cols - 1)
        for r in range(11):
            y = base - 24 - r * h * 0.075
            knit.append(nib([(x - 5, y - 5), (x, y + 4), (x + 5, y - 5)], 1.5, smooth=False, seed=seed + c * 11 + r, taper=(0.5, 0.5), color=pal[2]))
    knit.append(contour(U(), dd, cx, base - 34, base - 18, w * 0.48, 10, 4, 1.4, seed=seed + 7, a0=10, a1=170))
    knit.append(hatch(U(), dd, (cx - w / 2, base - h, cx + w / 2, base), 90, (14, 3.2), (0.7, 1.3), span=(0.55, 1), dark=(cx + w / 2, base - h * 0.4), seed=seed + 8))
    out.append(clipped(U(), dd, "".join(knit)))
    out.append(nib(cr(dome, True, 3), 3, closed=True, smooth=False, seed=seed + 9))
    # pompom
    pp = blob_pts(cx, base - h * 0.88 - 16, 22, 20, seed + 10, 0.18, 18)
    out.append(f'<path d="{sm(pp)}" fill="{pal[0]}"/>')
    for k in range(16):
        a = math.radians(k * 22.5)
        out.append(line(cx + 6 * math.cos(a), base - h * 0.88 - 16 + 6 * math.sin(a), cx + 20 * math.cos(a), base - h * 0.88 - 16 + 18 * math.sin(a), 1.4, seed=seed + 20 + k, cal=0))
    out.append(nib(pp, 1.8, closed=True, seed=seed + 11))
    return "".join(out)


@design("eat-drink-and-be-cozy")
def eat_drink_cozy(U):
    pal = MUSTARD
    out = [ground(U, 40)]
    out.append(blot(U, 290, 200, 210, 120, pal, 7, 0.16))
    out.append(teapot_cozy(U, 238, 306, 206, 3, pal))
    out.append(cup_saucer(U, 448, 306, 100, 4))
    # a plate of biscuits
    out.append(tx(300, 392, "eat, drink", SERIF_IT, 72, INK))
    out.append(shade_text(U(), 300, 506, "& BE COZY", BEBAS, fit("& BE COZY", BEBAS, 124, 450, 6), ls=6, seed=5, dx=4, dy=4))
    out.append(dotrow(220, 380, 532, 16, 2.2))
    out.append(finish(U))
    return "".join(out)


# ================================================================ build
def main(slugs):
    for slug, fn in DESIGNS.items():
        if slugs and slug not in slugs:
            continue
        save(COL, slug, fn(Ids(slug)))
        print("wrote", slug)


if __name__ == "__main__":
    main(sys.argv[1:])
