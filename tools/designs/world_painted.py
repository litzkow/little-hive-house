"""World Places, painted edition: every poster is composed like a small gouache painting with a real viewpoint,
a time of day, light direction, atmospheric depth and small storytelling details (same layout as places_painted)."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from places_painted import Cam, puff_column
from common import MONO
from poster import ANTON, poster


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


def Q(pts, fill, extra=""):
    return f'<polygon points="{P(pts)}" fill="{fill}"{extra}/>'


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def lerp(a, b, t):
    return a + (b - a) * t


def cumulus(uid, cx, base, w, h, seed, lit, mid, shade, hi="#FFFFFF", hi_op=0.55, light=-1):
    """Flat-bottomed cumulus from many puffs, shaded with one gradient (lit side -> shade side) plus highlights.
    light = -1 when the sun is on the left, +1 on the right."""
    rnd = random.Random(seed)
    puffs = []
    n = max(5, int(w / 9))
    for i in range(n):
        t = i / (n - 1)
        prof = math.sin(math.pi * (0.08 + 0.84 * t)) ** 0.8
        r = h * (0.22 + 0.4 * prof) * rnd.uniform(0.75, 1.1)
        x = cx - w / 2 + w * t + rnd.uniform(-4, 4)
        y = base - r * 0.55 - h * 0.42 * prof * rnd.uniform(0.6, 1.05)
        puffs.append((x, y, r))
    for _ in range(int(n / 2)):
        t = rnd.uniform(0.25, 0.75)
        prof = math.sin(math.pi * t)
        r = h * 0.3 * rnd.uniform(0.6, 1)
        puffs.append((cx - w / 2 + w * t, base - h * 0.55 * prof - r * 0.4, r))
    x1, x2 = (cx - w / 2, cx + w / 2) if light < 0 else (cx + w / 2, cx - w / 2)
    out = [defs(lg(uid, [(0, lit), (0.45, mid), (1, shade)], x1, base - h, x2, base, units="userSpaceOnUse"),
                f'<clipPath id="{uid}-c"><rect x="{cx - w}" y="{base - h * 2}" width="{w * 2}" height="{h * 2}"/></clipPath>')]
    body = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>' for x, y, r in puffs)
    his = "".join(f'<circle cx="{x + light * r * 0.25:.1f}" cy="{y - r * 0.3:.1f}" r="{r * 0.62:.1f}"/>' for x, y, r in puffs if y < base - h * 0.3)
    out.append(f'<g clip-path="url(#{uid}-c)"><g fill="url(#{uid})">{body}</g><g fill="{hi}" opacity="{hi_op}">{his}</g>'
               f'<ellipse cx="{cx - light * w * 0.05:.1f}" cy="{base - 2:.1f}" rx="{w * 0.48:.1f}" ry="{h * 0.12:.1f}" fill="{shade}" opacity="0.5"/></g>')
    return "".join(out)


def streak_cloud(x, y, w, color, op=0.6, h=4):
    return f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{h}" fill="{color}" opacity="{op}"/>'


def gulls(spec, color, sw=2):
    return (f'<g fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round">'
            + "".join(f'<path d="M {x} {y} q {s * 0.5} {-s * 0.45} {s} 0 q {s * 0.5} {-s * 0.45} {s} 0"/>' for x, y, s in spec) + "</g>")


def figure(x, base, h, col, head="#2A1E1E", legs="#2A2228", rim=None, rim_side=-1, bag=None):
    """Small standing person silhouette, h px tall."""
    s = h / 100
    g = (f'<g transform="translate({x:.1f} {base:.1f}) scale({s:.3f})">'
         f'<path d="M -9 -48 L 9 -48 L 10 0 L 4 0 L 1 -30 L -2 0 L -8 0 Z" fill="{legs}"/>'
         f'<path d="M -13 -84 Q 0 -92 13 -84 L 12 -44 L -12 -44 Z" fill="{col}"/>'
         f'<circle cx="0" cy="-94" r="9" fill="{head}"/>')
    if bag:
        g += f'<rect x="10" y="-62" width="9" height="12" rx="2" fill="{bag}"/><path d="M 11 -62 L 12 -82" stroke="{bag}" stroke-width="2"/>'
    if rim:
        xx = 13 * (-rim_side) * -1
        g += f'<path d="M {13 * rim_side} -84 L {12 * rim_side} -46" stroke="{rim}" stroke-width="3" stroke-linecap="round"/><path d="M {7 * rim_side} -101 Q {11 * rim_side} -95 {8 * rim_side} -88" stroke="{rim}" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
    return g + "</g>"


def leaf_canopy(uid, cx, cy, rx, ry, seed, dark, mid, lit, gold=None, light=(-1, -1), n=60, holes=None, r=(0.16, 0.32)):
    """Irregular tree canopy built of leaf clumps: shade clumps, body, then sunlit clumps on the light side."""
    rnd = random.Random(seed)
    clumps = []
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(0, 1) ** 0.6
        x = cx + rx * d * math.cos(a)
        y = cy + ry * d * math.sin(a)
        rr = min(rx, ry) * rnd.uniform(*r) * 1.3
        clumps.append((x, y, rr))
    lx, ly = light
    body = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}"/>' for x, y, rr in clumps)
    shade = "".join(f'<circle cx="{x - lx * rr * 0.25:.1f}" cy="{y - ly * rr * 0.3:.1f}" r="{rr * 0.8:.1f}"/>' for x, y, rr in clumps
                    if (x - cx) * lx + (y - cy) * ly < 0)
    sun = "".join(f'<circle cx="{x + lx * rr * 0.28:.1f}" cy="{y + ly * rr * 0.3:.1f}" r="{rr * 0.55:.1f}"/>' for x, y, rr in clumps
                  if (x - cx) * lx / rx + (y - cy) * ly / ry > -0.1)
    out = (f'<g fill="{mid}">{body}</g><g fill="{dark}" opacity="0.75">{shade}</g><g fill="{lit}" opacity="0.85">{sun}</g>')
    if gold:
        tips = "".join(f'<ellipse cx="{x + lx * rr * 0.5:.1f}" cy="{y + ly * rr * 0.5:.1f}" rx="{rr * 0.22:.1f}" ry="{rr * 0.15:.1f}"/>' for x, y, rr in clumps
                       if (x - cx) * lx / rx + (y - cy) * ly / ry > 0.45)
        out += f'<g fill="{gold}" opacity="0.55">{tips}</g>'
    # leaf texture: tiny dark and light flecks
    out += dots(n, seed + 7, (cx - rx * 0.9, cy - ry * 0.8, cx + rx * 0.9, cy + ry * 0.8), dark, r=(0.8, 1.8), opacity=(0.3, 0.6))
    if holes:
        out += dots(int(n / 3), seed + 1, (cx - rx * 0.7, cy - ry * 0.7, cx + rx * 0.7, cy + ry * 0.7), holes, r=(1, 2.4), opacity=(0.6, 1))
    return out


def water_lines(n, seed, box, colors, w=(8, 40), h=(1, 2.4), opacity=(0.3, 0.8), grow=True):
    """Horizontal ripple strokes, larger toward the bottom of the box (perspective)."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        y = rnd.uniform(y0, y1)
        k = 0.35 + 0.65 * (y - y0) / max(1, y1 - y0) if grow else 1
        ww = rnd.uniform(*w) * k
        hh = rnd.uniform(*h) * (0.5 + k * 0.7)
        x = rnd.uniform(x0, x1)
        out.append(f'<rect x="{x - ww / 2:.1f}" y="{y:.1f}" width="{ww:.1f}" height="{hh:.1f}" rx="{hh / 2:.1f}" fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*opacity):.2f}"/>')
    return "".join(out)


# ================================================================ PARIS — the tower from a Seine quay, golden hour
def eiffel(cx, base, top, u, body, shade, lit, rim, lattice):
    """Eiffel Tower seen face-on (between two legs), sunlit from the left."""
    H = base - top
    prof = [(0, 0.205), (0.05, 0.172), (0.1, 0.143), (0.17, 0.112), (0.26, 0.085), (0.35, 0.064), (0.45, 0.049),
            (0.6, 0.034), (0.72, 0.026), (0.84, 0.019)]

    def hw(t):
        for (t1, w1), (t2, w2) in zip(prof, prof[1:]):
            if t1 <= t <= t2:
                return H * lerp(w1, w2, (t - t1) / (t2 - t1))
        return H * prof[-1][1]

    def legw(t):  # width of one leg seen face on
        return H * lerp(0.07, 0.03, min(1, t / 0.35))

    Y = lambda t: base - t * H
    ts = [i / 60 * 0.84 for i in range(61)]
    left = [(cx - hw(t), Y(t)) for t in ts]
    right = [(cx + hw(t), Y(t)) for t in ts]
    outer = left + right[::-1]

    def hole(t0, t1, arch):
        pts = [(cx - hw(t) + legw(t), Y(t)) for t in [t0 + (t1 - t0) * i / 10 for i in range(11)]]
        xl, yl = pts[-1]
        xr = 2 * cx - xl
        n = 14
        top_pts = [(lerp(xl, xr, i / n), yl - arch * H * math.sin(math.pi * i / n)) for i in range(n + 1)]
        rpts = [(2 * cx - x, y) for x, y in pts[::-1]]
        return pts + top_pts[1:-1] + rpts

    hA = hole(0.0, 0.10, 0.045)
    hB = hole(0.19, 0.31, 0.02)
    hC = [(cx - hw(0.37) + legw(0.37) * 0.9, Y(0.37)), (cx, Y(0.56)), (cx + hw(0.37) - legw(0.37) * 0.9, Y(0.37))]

    def path(pts):
        return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z "

    d = path(outer) + path(hA) + path(hB) + path(hC)
    out = [defs(lg(f"{u}-tw", [(0, lit), (0.35, body), (0.7, shade), (1, shade)], cx - hw(0), 0, cx + hw(0), 0, units="userSpaceOnUse"),
                f'<clipPath id="{u}-twc"><path d="{d}" fill-rule="evenodd" clip-rule="evenodd"/></clipPath>')]
    out.append(f'<path d="{d}" fill-rule="evenodd" fill="url(#{u}-tw)"/>')
    # lattice: cross bracing in each leg and in the shaft, as light-through-iron strokes
    g = []
    t = 0.0
    while t < 0.84:
        step = 0.028 if t < 0.35 else 0.035
        t2 = min(0.84, t + step)
        for sgn in (-1, 1):
            if t < 0.35:
                a1, b1 = cx + sgn * hw(t), cx + sgn * (hw(t) - legw(t))
                a2, b2 = cx + sgn * hw(t2), cx + sgn * (hw(t2) - legw(t2))
            else:
                a1, b1, a2, b2 = cx + sgn * hw(t), cx, cx + sgn * hw(t2), cx
            g.append(f'<line x1="{a1:.1f}" y1="{Y(t):.1f}" x2="{b2:.1f}" y2="{Y(t2):.1f}"/><line x1="{b1:.1f}" y1="{Y(t):.1f}" x2="{a2:.1f}" y2="{Y(t2):.1f}"/>')
        g.append(f'<line x1="{cx - hw(t2):.1f}" y1="{Y(t2):.1f}" x2="{cx + hw(t2):.1f}" y2="{Y(t2):.1f}"/>')
        t = t2
    out.append(f'<g clip-path="url(#{u}-twc)"><g stroke="{lattice}" stroke-width="1.1" opacity="0.6">{"".join(g)}</g>'
               f'<polygon points="{P([(cx + hw(0) * 0.15, base), (cx + hw(0) + 2, base), (cx + hw(0.84) + 2, Y(0.84)), (cx + 1, Y(0.84))])}" fill="{shade}" opacity="0.35"/></g>')
    # decorative arch under the first floor
    ax0, ax1 = cx - hw(0.02) + legw(0.02), cx + hw(0.02) - legw(0.02)
    out.append(f'<path d="M {ax0:.1f} {Y(0.02):.1f} Q {cx:.1f} {Y(0.215):.1f} {ax1:.1f} {Y(0.02):.1f}" fill="none" stroke="{body}" stroke-width="{H * 0.012:.1f}"/>')
    out.append(f'<path d="M {ax0:.1f} {Y(0.02):.1f} Q {cx:.1f} {Y(0.215):.1f} {cx:.1f} {Y(0.117):.1f}" fill="none" stroke="{lit}" stroke-width="{H * 0.005:.1f}" opacity="0.7"/>')
    # platforms
    for t, th, ov in ((0.17, 0.026, 0.018), (0.35, 0.018, 0.012)):
        x0, x1 = cx - hw(t) - H * ov, cx + hw(t) + H * ov
        out.append(f'<rect x="{x0:.1f}" y="{Y(t) - H * th / 2:.1f}" width="{x1 - x0:.1f}" height="{H * th:.1f}" fill="{shade}"/>')
        out.append(f'<rect x="{x0:.1f}" y="{Y(t) - H * th / 2:.1f}" width="{x1 - x0:.1f}" height="{H * th * 0.35:.1f}" fill="{lit}" opacity="0.8"/>')
        n = int((x1 - x0) / 4)
        out.append(f'<g fill="{shade}">' + "".join(f'<rect x="{x0 + (i + 0.3) * (x1 - x0) / n:.1f}" y="{Y(t) + H * th * 0.05:.1f}" width="{(x1 - x0) / n * 0.4:.1f}" height="{H * th * 0.35:.1f}" fill="{lit}" opacity="0.35"/>' for i in range(n)) + "</g>")
    # top: third floor cabin, lantern and antenna
    tt = Y(0.84)
    w3 = H * 0.03
    out.append(f'<rect x="{cx - w3:.1f}" y="{tt - H * 0.03:.1f}" width="{2 * w3:.1f}" height="{H * 0.03:.1f}" fill="{shade}"/>')
    out.append(f'<rect x="{cx - w3:.1f}" y="{tt - H * 0.03:.1f}" width="{w3 * 0.8:.1f}" height="{H * 0.03:.1f}" fill="{lit}" opacity="0.7"/>')
    out.append(f'<polygon points="{P([(cx - w3 * 0.6, tt - H * 0.03), (cx - w3 * 0.25, tt - H * 0.08), (cx + w3 * 0.25, tt - H * 0.08), (cx + w3 * 0.6, tt - H * 0.03)])}" fill="{body}"/>')
    out.append(f'<rect x="{cx - 1.2:.1f}" y="{top:.1f}" width="2.4" height="{tt - H * 0.08 - top:.1f}" fill="{shade}"/>')
    out.append(f'<rect x="{cx - 2.2:.1f}" y="{tt - H * 0.11:.1f}" width="4.4" height="{H * 0.035:.1f}" fill="{body}"/>')
    # rim light down the sunlit edge
    out.append(f'<polyline points="{P(left)}" fill="none" stroke="{rim}" stroke-width="1.8" stroke-linejoin="round" opacity="0.9"/>')
    return "".join(out)


def haussmann(C, X, z0, z1, ybase, side, wall, glass, roof, seed, ground=None, sun=None, top=22):
    """Haussmann apartment block in the plane X (side -1: left of the camera, facade faces +X)."""
    rnd = random.Random(seed)
    away = side * 2.6
    out = [Q(C.quad_x(X, z0, z1, ybase, ybase + top), wall)]
    # stone courses
    out.append('<g stroke="#000" stroke-opacity="0.07" stroke-width="0.8">' + "".join(
        f'<line x1="{C(X, ybase + y, z0)[0]:.1f}" y1="{C(X, ybase + y, z0)[1]:.1f}" x2="{C(X, ybase + y, z1)[0]:.1f}" y2="{C(X, ybase + y, z1)[1]:.1f}"/>'
        for y in [5.4 + 0.75 * i for i in range(22)] if y < top) + "</g>")
    bays = max(2, int((z1 - z0) / 3.4))
    for f_ in range(5):
        y0 = ybase + 5.6 + f_ * 3.15
        if y0 + 2.4 > ybase + top - 1:
            break
        for i in range(bays):
            za = z0 + (z1 - z0) * (i + 0.3) / bays
            zb = z0 + (z1 - z0) * (i + 0.7) / bays
            refl = rnd.random()
            col = glass[0] if refl < 0.55 else (glass[1] if refl < 0.9 else glass[2])
            out.append(Q(C.quad_x(X, za, zb, y0, y0 + 2.3), col))
            out.append(Q(C.quad_x(X, za - 0.12, zb + 0.12, y0 + 2.3, y0 + 2.6), "#FFFFFF", ' opacity="0.25"'))
        if f_ in (1, 4):  # continuous wrought-iron balconies
            out.append(Q(C.quad_x(X, z0 + 0.3, z1 - 0.3, y0 - 0.1, y0 + 0.9), "#2A2226", ' opacity="0.55"'))
            out.append(Q(C.quad_x(X, z0 + 0.3, z1 - 0.3, y0 - 0.25, y0 - 0.05), "#FFFFFF", ' opacity="0.3"'))
    # ground floor: shopfronts
    gcol = ground or "#3A2A2E"
    out.append(Q(C.quad_x(X, z0, z1, ybase, ybase + 4.6), gcol))
    for i in range(bays):
        za = z0 + (z1 - z0) * (i + 0.12) / bays
        zb = z0 + (z1 - z0) * (i + 0.88) / bays
        out.append(Q(C.quad_x(X, za, zb, ybase + 0.2, ybase + 3.6), "#F2C27A" if rnd.random() < 0.6 else "#5A4A52", ' opacity="0.85"'))
    out.append(Q(C.quad_x(X, z0, z1, ybase + 4.6, ybase + 5.2), "#FFFFFF", ' opacity="0.3"'))
    # cornice and mansard roof with dormers and chimneys
    out.append(Q(C.quad_x(X, z0, z1, ybase + top - 0.8, ybase + top), "#FFFFFF", ' opacity="0.35"'))
    m = [C(X, ybase + top, z0), C(X + away, ybase + top + 4.2, z0), C(X + away, ybase + top + 4.2, z1), C(X, ybase + top, z1)]
    out.append(Q(m, roof))
    for i in range(bays):
        zc = z0 + (z1 - z0) * (i + 0.5) / bays
        dq = [C(X + away * 0.3, ybase + top + 1.0, zc - 0.5), C(X + away * 0.3, ybase + top + 2.8, zc - 0.5),
              C(X + away * 0.3, ybase + top + 3.2, zc), C(X + away * 0.3, ybase + top + 2.8, zc + 0.5), C(X + away * 0.3, ybase + top + 1.0, zc + 0.5)]
        out.append(Q(dq, "#E8DCCB"))
        out.append(Q(C.quad_x(X + away * 0.3, zc - 0.3, zc + 0.3, ybase + top + 1.15, ybase + top + 2.5), glass[0]))
    for i in range(max(1, bays // 2)):
        zc = z0 + (z1 - z0) * (i + 0.5) / max(1, bays // 2) + rnd.uniform(-0.6, 0.6)
        cq = [C(X + away * 1.2, ybase + top + 3.6, zc - 0.8), C(X + away * 1.2, ybase + top + 6.2, zc - 0.8),
              C(X + away * 1.2, ybase + top + 6.2, zc + 0.8), C(X + away * 1.2, ybase + top + 3.6, zc + 0.8)]
        out.append(Q(cq, mix(wall, "#8A5A4A", 0.4)))
        px, py = C(X + away * 1.2, ybase + top + 6.2, zc)
        out.append(f'<rect x="{px - 2:.1f}" y="{py - 3:.1f}" width="4" height="3" fill="#B0603E"/>')
    if sun:
        out.append(f'<polyline points="{P([m[1], m[2]])}" fill="none" stroke="{sun}" stroke-width="1.6" opacity="0.9"/>')
    out.append(Q(C.quad_x(X, z0, z0 + 0.35, ybase, ybase + top), "#000", ' opacity="0.16"'))
    return "".join(out)


def bouquiniste(C, z0, z1, X=-10.6, top=8.0, seed=0, sun="#F8C878"):
    """Green bookseller box on the parapet with its lid propped open, prints pinned inside."""
    rnd = random.Random(seed)
    out = []
    xs = X + 0.62
    out.append(Q([C(xs, top, z0), C(xs, top + 0.7, z0), C(xs, top + 0.7, z1), C(xs, top, z1)], "#2E5A44"))
    out.append(Q([C(X, top + 0.7, z0), C(xs, top + 0.7, z0), C(xs, top + 0.7, z1), C(X, top + 0.7, z1)], "#4A7A5C"))
    out.append(Q([C(xs, top + 0.62, z0), C(xs, top + 0.7, z0), C(xs, top + 0.7, z1), C(xs, top + 0.62, z1)], sun, ' opacity="0.8"'))
    # lid
    lid = [C(X + 0.05, top + 0.7, z0), C(X - 0.25, top + 1.75, z0), C(X - 0.25, top + 1.75, z1), C(X + 0.05, top + 0.7, z1)]
    out.append(Q(lid, "#24483A"))
    inner = [C(X + 0.0, top + 0.78, z0 + 0.1), C(X - 0.22, top + 1.68, z0 + 0.1), C(X - 0.22, top + 1.68, z1 - 0.1), C(X + 0.0, top + 0.78, z1 - 0.1)]
    out.append(Q(inner, "#E8DCC4"))
    cols = ["#C9574A", "#3E6A8A", "#E0B04A", "#6A8A5A", "#F2E6D0", "#8A4A6A", "#2E4A6A"]
    n = max(2, int((z1 - z0) / 0.45))
    for i in range(n):
        za = z0 + 0.15 + (z1 - z0 - 0.3) * i / n
        zb = za + (z1 - z0 - 0.3) / n * 0.8
        for k, (y0, y1) in enumerate(((0.85, 1.2), (1.27, 1.62))):
            if rnd.random() < 0.85:
                xa = X - 0.22 * (y0 - 0.78) / 0.9
                out.append(Q([C(xa, top + y0, za), C(xa - 0.08, top + y1, za), C(xa - 0.08, top + y1, zb), C(xa, top + y0, zb)], rnd.choice(cols)))
    out.append(Q([C(xs, top, z0), C(xs, top + 0.7, z0), C(xs, top + 0.7, z0 + 0.06), C(xs, top, z0 + 0.06)], "#1A3A2C"))
    return "".join(out)


def plane_tree(C, X, Z, ybase, h, seed, light=(-1, -1)):
    """London-plane: mottled trunk, forked limbs, a broad loose canopy."""
    rnd = random.Random(seed)
    x, b = C(X, ybase, Z)
    s = C.f / Z
    tw = 0.55 * s
    th = h * 0.42 * s
    out = [f'<path d="M {x - tw / 2:.1f} {b:.1f} Q {x - tw * 0.3:.1f} {b - th * 0.5:.1f} {x - tw * 0.2:.1f} {b - th:.1f} L {x + tw * 0.3:.1f} {b - th:.1f} Q {x + tw * 0.4:.1f} {b - th * 0.5:.1f} {x + tw / 2:.1f} {b:.1f} Z" fill="#A89878"/>']
    # limbs
    for dx, dy in ((-1.6, -1.2), (1.4, -1.4), (0.2, -1.8)):
        out.append(f'<path d="M {x:.1f} {b - th * 0.95:.1f} Q {x + dx * s * 0.4:.1f} {b - th * 1.15:.1f} {x + dx * s:.1f} {b - th + dy * s * 1.3:.1f}" fill="none" stroke="#8E8066" stroke-width="{tw * 0.45:.1f}" stroke-linecap="round"/>')
    # camouflage bark
    out.append(blobs(int(6 + th / 8), seed, (x - tw * 0.45, b - th, x + tw * 0.45, b), ["#D8CCB0", "#6E6A52", "#C4B894", "#8C8466"], r=(tw * 0.12, tw * 0.28), opacity=(0.7, 1), squash=1.3))
    out.append(Q([(x + tw * 0.05, b), (x + tw / 2, b), (x + tw * 0.3, b - th), (x, b - th)], "#2E2A22", ' opacity="0.3"'))
    cx, cy = x, b - th - h * 0.22 * s
    rx = h * 0.38 * s
    out.append(leaf_canopy(f"pt{seed}", cx, cy, rx, h * 0.24 * s, seed, "#2E4226", "#557336", "#87A04C", gold="#D8C870", light=light, n=int(min(130, 24 + rx * 0.9)), r=(0.09, 0.2)))
    return "".join(out)


def paris():
    u = "pa"
    C = Cam(f=300, cx=300, vpy=286, eye=10)
    out = [defs(
        lg(f"{u}-sky", [(0, "#6C93C6"), (0.28, "#9DB9D9"), (0.52, "#DCD3CA"), (0.6, "#F4D5AC"), (0.645, "#F9E1B6")], 0, 0, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-river", [(0, "#F4D9AE"), (0.1, "#C9C2B8"), (0.35, "#7E9CB8"), (1, "#3E5E80")], 0, 286, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-pave", [(0, "#C9B49A"), (1, "#9A8676")], 0, 286, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-wallL", [(0, "#CDB59C"), (1, "#9E8670")], 0, 286, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#F6DDB6", 0), (1, "#F6DDB6", 0.85)], 0, 220, 0, 290, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(70, 250, 300, "#FFE3A8", f"{u}-sun", 0.75))
    # clouds lit from the low sun on the left
    out.append(cumulus(f"{u}-c1", 470, 150, 170, 62, 3, "#FFF1D8", "#E9D2C4", "#A9A6BE", hi="#FFF8EA", hi_op=0.6))
    out.append(cumulus(f"{u}-c2", 560, 196, 90, 30, 8, "#FFE9CC", "#E6CFC4", "#AFA8BE", hi="#FFF8EA"))
    out.append(cumulus(f"{u}-c3", 300, 120, 90, 26, 5, "#FFF1D8", "#E6D2C8", "#B4AEC4", hi="#FFF8EA"))
    for x, y, w in ((210, 200, 70), (380, 214, 60), (520, 232, 50)):
        out.append(streak_cloud(x, y, w, "#FBE6C8", 0.6, 3))
    # far city: hazy roofs, a gilded dome
    rnd = random.Random(4)
    x = 150
    far = []
    while x < 600:
        w = rnd.uniform(14, 30)
        h = rnd.uniform(6, 14)
        far.append(f'<rect x="{x:.1f}" y="{286 - h:.1f}" width="{w + 1:.1f}" height="{h + 6:.1f}" fill="{rnd.choice(["#C6B6BE", "#BEAFBC", "#CBBCC0"])}"/>')
        x += w
    out.append("".join(far))
    out.append('<g><rect x="236" y="262" width="22" height="14" fill="#C9B9B8"/><path d="M 236 263 Q 247 240 258 263 Z" fill="#E2B85E"/>'
               '<path d="M 247 241 Q 253 248 256 262 L 258 263 Q 252 244 247 241 Z" fill="#B88A4A" opacity="0.6"/><rect x="245.5" y="232" width="3" height="10" fill="#D6A84E"/></g>')
    out.append(f'<rect x="0" y="230" width="600" height="60" fill="url(#{u}-haze)"/>')
    # the tower
    out.append(eiffel(352, 296, 93, u, "#8E6A58", "#5E4A52", "#E8B47A", "#FFE1A6", "#E6CBB4"))
    # far bank: Champ de Mars trees around the tower's feet
    for k, (X, Z, h) in enumerate(((50, 300, 12), (62, 420, 16), (76, 520, 16), (95, 600, 15), (40, 700, 14), (110, 460, 15), (130, 560, 14), (20, 900, 13))):
        x, b = C(X, 6, Z)
        s = C.f / Z
        out.append(leaf_canopy(f"{u}-ft{k}", x, b - h * 0.5 * s, h * 0.7 * s, h * 0.42 * s, 40 + k, "#4E5A44", "#6E7A52", "#B8AE6A", light=(-1, -1), n=30))
    # the bridge across the river, lamps on its parapet
    Zb = 210
    out.append(Q([C(-12, 10.4, Zb), C(62, 10.4, Zb), C(62, 8.6, Zb), C(-12, 8.6, Zb)], "#D8C2A4"))
    out.append(Q([C(-12, 8.6, Zb), C(62, 8.6, Zb), C(62, 0, Zb), C(-12, 0, Zb)], "#C2A88C"))
    for i in range(4):
        X0, X1 = -10 + i * 18 + 2.5, -10 + (i + 1) * 18 - 2.5
        a0, a1 = C(X0, 0, Zb), C(X1, 0, Zb)
        apex = C((X0 + X1) / 2, 6.8, Zb)
        out.append(f'<path d="M {a0[0]:.1f} {a0[1]:.1f} Q {apex[0]:.1f} {apex[1] - (a0[1] - apex[1]):.1f} {a1[0]:.1f} {a1[1]:.1f} Z" fill="#6E6276"/>')
    for i in range(9):
        lx, ly = C(-10 + i * 8.8, 10.4, Zb)
        out.append(f'<line x1="{lx:.1f}" y1="{ly:.1f}" x2="{lx:.1f}" y2="{ly - 6:.1f}" stroke="#4A3E46" stroke-width="1"/><circle cx="{lx:.1f}" cy="{ly - 6.5:.1f}" r="1.4" fill="#4A3E46"/>')
    # right bank: sunlit facades
    for k, (z0, z1) in enumerate(((84, 112), (112, 136), (136, 168), (168, 196), (196, 236), (236, 270))):
        out.append(haussmann(C, 82, z0, z1, 8, 1, ["#F2D3A2", "#E9C79A", "#DCD0D4"][k % 3] if False else ["#F3D6A6", "#EDCB98", "#F6DEB4"][k % 3],
                             ("#7E8AA8", "#F9E2B8", "#4A4A5E"), "#8E96AA", 70 + k, ground="#6A4A42", sun="#FFE6B0"))
    # right quay: trees and wall
    out.append(Q([C(60, 0, 60), C(60, 8, 60), C(60, 8, 3000), C(60, 0, 3000)], "#E8C894"))
    out.append(f'<g stroke="#B8946A" stroke-width="0.8" opacity="0.5">' + "".join(
        f'<line x1="{C(60, y, 60)[0]:.1f}" y1="{C(60, y, 60)[1]:.1f}" x2="{C(60, y, 600)[0]:.1f}" y2="{C(60, y, 600)[1]:.1f}"/>' for y in (2, 4, 6)) + "</g>")
    out.append(Q([C(60, 8, 60), C(82, 8, 60), C(82, 8, 3000), C(60, 8, 3000)], "#D8B88E"))
    for k, Z in enumerate((70, 92, 120, 156, 200, 250)):
        out.append(plane_tree(C, 65, Z, 8, 17, 200 + k))
    # river
    out.append(Q([C(-10, 0, 19), C(60, 0, 19), C(60, 0, 4000), C(-10, 0, 4000)], f"url(#{u}-river)"))
    # reflections: bridge, tower legs, sunlit facades
    out.append(Q([C(-12, 0, Zb), C(62, 0, Zb), C(62, -3.5, Zb), C(-12, -3.5, Zb)], "#A89096", ' opacity="0.45"'))
    rnd = random.Random(11)
    for i in range(26):
        y = 304 + i * 1.6
        w = rnd.uniform(5, 18)
        out.append(f'<rect x="{352 - w / 2 + rnd.uniform(-6, 6):.1f}" y="{y:.1f}" width="{w:.1f}" height="1.2" fill="#6E5A5E" opacity="{0.5 - i * 0.015:.2f}"/>')
    for i in range(70):
        Z = rnd.uniform(70, 260)
        x, y = C(rnd.uniform(48, 60), 0, Z)
        w = C.f * rnd.uniform(2, 6) / Z
        out.append(f'<rect x="{x - w:.1f}" y="{y + rnd.uniform(0, 3000 / Z):.1f}" width="{w:.1f}" height="{max(0.8, 150 / Z):.1f}" fill="#F8D9A4" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    out.append(water_lines(90, 12, (150, 306, 600, 444), ["#DCE6EE", "#F6DDB0", "#2E4A6A", "#93AECA"], w=(6, 46), h=(0.8, 1.8), opacity=(0.2, 0.55)))
    # tour boat heading downriver
    hull = [C(22, 0, 36), C(22, 1.6, 36), C(22, 1.6, 70), C(22, 0, 70)]
    out.append(Q([C(22, -0.6, 36), C(30, -0.6, 36), C(30, -0.6, 72), C(22, -0.6, 72)], "#2A3E5A", ' opacity="0.35"'))
    out.append(Q(hull, "#F4EEE4"))
    out.append(Q([C(22, 0, 36), C(22, 0.5, 36), C(22, 0.5, 70), C(22, 0, 70)], "#2E4A6A"))
    out.append(Q([C(22, 1.6, 44), C(23, 3.6, 44), C(23, 3.6, 70), C(22, 1.6, 70)], "#9EC0D2"))
    out.append(Q([C(23, 3.6, 44), C(29, 3.6, 44), C(29, 3.6, 70), C(23, 3.6, 70)], "#C8DCE4"))
    for z in range(46, 70, 3):
        a_, b_ = C(22.1, 1.7, z), C(23, 3.5, z)
        out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#E8E2D8" stroke-width="1.2"/>')
    for z, c in ((38, "#C9574A"), (39.5, "#2E3A5A"), (41.5, "#E0B04A")):
        x, y = C(23.5, 1.6, z)
        s = C.f / z
        out.append(f'<rect x="{x - 0.25 * s:.1f}" y="{y - 1.4 * s:.1f}" width="{0.5 * s:.1f}" height="{1.4 * s:.1f}" rx="2" fill="{c}"/><circle cx="{x:.1f}" cy="{y - 1.6 * s:.1f}" r="{0.22 * s:.1f}" fill="#3A2A22"/>')
    wk = [C(22, 0, 70), C(19, 0, 90), C(17, 0, 120)]
    out.append(f'<path d="M {P(wk[:1])} Q {P(wk[1:2])} {P(wk[2:])}" fill="none" stroke="#F4EEE4" stroke-width="2" opacity="0.5"/>')
    out.append(f'<path d="M {C(22, 0, 36)[0]:.1f} {C(22, 0, 36)[1] + 2:.1f} L {C(14, 0, 30)[0]:.1f} {C(14, 0, 30)[1]:.1f}" stroke="#F4EEE4" stroke-width="2.2" opacity="0.55"/>')
    # left bank: shaded facades with the cafe at street level
    for k, (z0, z1) in enumerate(((300, 400), (240, 300), (190, 240), (150, 190), (118, 150), (92, 118), (70, 92), (52, 70), (34, 52))):
        out.append(haussmann(C, -32, z0, z1, 7, -1, ["#C9B4A6", "#D2BCA8", "#C4AEA6"][k % 3], ("#5E5E74", "#B8C4D6", "#3A3448"), "#7A7E96", 10 + k,
                             ground="#4A3438", sun="#FFD9A0"))
    # cafe terrace: awning, tables, people
    az0, az1 = 35, 51
    aw = [C(-32, 11.2, az0), C(-29.4, 10.0, az0), C(-29.4, 10.0, az1), C(-32, 11.2, az1)]
    out.append(Q(aw, "#9E2E36"))
    n = 12
    for i in range(n):
        za, zb = az0 + (az1 - az0) * i / n, az0 + (az1 - az0) * (i + 0.5) / n
        out.append(Q([C(-32, 11.2, za), C(-29.4, 10.0, za), C(-29.4, 10.0, zb), C(-32, 11.2, zb)], "#F2E2C8", ' opacity="0.85"'))
    val = [C(-29.4, 10.0, az0), C(-29.4, 9.5, az0), C(-29.4, 9.5, az1), C(-29.4, 10.0, az1)]
    out.append(Q(val, "#7A1E28"))
    for z in (37, 40, 43.5, 47):
        tx, ty = C(-30.4, 7, z)
        s = C.f / z
        out.append(f'<rect x="{tx - 0.35 * s:.1f}" y="{ty - 0.75 * s:.1f}" width="{0.7 * s:.1f}" height="{0.08 * s + 1:.1f}" fill="#E8E0D0"/><line x1="{tx:.1f}" y1="{ty - 0.7 * s:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="#2A2226" stroke-width="1"/>')
    for z, c in ((38.2, "#3E5A7A"), (44.5, "#C98A4A"), (46, "#5A4A6A")):
        px, pb = C(-30.9, 7, z)
        out.append(figure(px, pb, C.f * 1.25 / z, c))
    # left quay: road, sidewalk, plane trees, parapet wall and bouquinistes
    out.append(Q([C(-32, 7, 6), C(-10, 7, 6), C(-10, 7, 4000), C(-32, 7, 4000)], f"url(#{u}-pave)"))
    out.append(Q([C(-28.5, 7.01, 6), C(-16, 7.01, 6), C(-16, 7.01, 4000), C(-28.5, 7.01, 4000)], "#7E7076", ' opacity="0.55"'))
    out.append(Q([C(-10, 0, 5), C(-10, 8, 5), C(-10, 8, 4000), C(-10, 0, 4000)], f"url(#{u}-wallL)"))
    out.append(f'<g stroke="#7A6656" stroke-width="0.9" opacity="0.45">' + "".join(
        f'<line x1="{C(-10, y, 19)[0]:.1f}" y1="{C(-10, y, 19)[1]:.1f}" x2="{C(-10, y, 900)[0]:.1f}" y2="{C(-10, y, 900)[1]:.1f}"/>' for y in (1.2, 2.4, 3.6, 4.8, 6, 7.2)) + "</g>")
    out.append(f'<g stroke="#7A6656" stroke-width="0.9" opacity="0.35">' + "".join(
        f'<line x1="{C(-10, 1.2 * (i % 6), z)[0]:.1f}" y1="{C(-10, 1.2 * (i % 6), z)[1]:.1f}" x2="{C(-10, 1.2 * (i % 6) + 1.2, z)[0]:.1f}" y2="{C(-10, 1.2 * (i % 6) + 1.2, z)[1]:.1f}"/>'
        for i, z in enumerate([6 + j * 1.9 + (j % 2) * 0.9 for j in range(60)])) + "</g>")
    out.append(Q([C(-10, 0, 5), C(-10, 1.5, 5), C(-10, 1.5, 4000), C(-10, 0, 4000)], "#5E6A6A", ' opacity="0.35"'))
    out.append(Q([C(-10, 7.4, 5), C(-10, 8, 5), C(-10, 8, 4000), C(-10, 7.4, 4000)], "#F2DDB8", ' opacity="0.7"'))
    out.append(Q([C(-10.6, 8, 5), C(-10, 8, 5), C(-10, 8, 4000), C(-10.6, 8, 4000)], "#E2CDAE"))
    # weathering on the quay wall, ivy spilling over it, an iron mooring ring
    wall = [C(-10, 0, 5), C(-10, 8, 5), C(-10, 8, 400), C(-10, 0, 400)]
    out.append(f'<clipPath id="{u}-wc"><polygon points="{P(wall)}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-wc)">' + streaks(70, 5, (0, 300, 300, 444), ["#8E7A68", "#B8A08A", "#6E6A5E"], w=(1.5, 4), length=(10, 40), opacity=(0.08, 0.2), slant=0.05) + "</g>")
    rnd = random.Random(31)
    for z0 in (12.5, 17, 27, 36, 58, 80):
        L = rnd.uniform(1.2, 2.6)
        k = 7
        for j in range(k):
            z = z0 + L * j / (k - 1)
            drop = rnd.uniform(0.6, 3.0) * math.sin(math.pi * (j + 0.5) / k) ** 0.5
            steps = max(2, int(drop / 0.22))
            for i in range(steps):
                px, py = C(-10, 8 - drop * i / steps, z + rnd.uniform(-0.15, 0.15))
                rr = max(0.7, C.f / z * 0.16 * (1 - 0.5 * i / steps))
                out.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{rr * 1.2:.1f}" ry="{rr:.1f}" fill="{rnd.choice(["#3E5A30", "#5E7E3A", "#8A9E4A", "#2E4A26"])}"/>')
    rx_, ry_ = C(-10, 3.2, 9)
    out.append(f'<ellipse cx="{rx_:.1f}" cy="{ry_:.1f}" rx="5" ry="8" fill="none" stroke="#3A2E2A" stroke-width="2.2"/>')
    trees = [(-13, Z) for Z in (16, 25, 36, 50, 68, 92, 125, 170, 230)]
    for k, (X, Z) in enumerate(reversed(trees)):
        if Z > 30:
            out.append(plane_tree(C, X, Z, 7, 19, 300 + k))
    for k, (z0, z1) in enumerate(((52, 54), (48, 50.5), (40, 42), (37, 39.5), (30, 32.3), (26.6, 28.9), (19.6, 22.2), (16.5, 19.2), (12.2, 15.2))):
        out.append(bouquiniste(C, z0, z1, seed=k))
    # a peniche houseboat moored against the quay, geraniums along its roof
    hz0, hz1 = 22, 52
    out.append(Q([C(-4.2, 0, hz0), C(-1.8, 0, hz0), C(-1.8, 0, hz1 + 2), C(-4.6, 0, hz1)], "#1E3048", ' opacity="0.35"'))
    hull = [C(-4.2, -0.2, hz0), C(-4.2, 2.4, hz0), C(-4.2, 2.4, hz1 - 4), C(-5.2, 3.0, hz1 + 1.5), C(-4.6, -0.2, hz1 - 1)]
    out.append(Q(hull, "#22322E"))
    out.append(Q([C(-4.2, 1.95, hz0), C(-4.2, 2.4, hz0), C(-4.2, 2.4, hz1 - 4), C(-5.2, 3.0, hz1 + 1.5), C(-5.1, 2.55, hz1 + 1)], "#B8443E"))
    for z in [hz0 + 1.5 + i * 2.2 for i in range(12)]:
        px, py = C(-4.2, 1.15, z)
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{max(1, 0.2 * C.f / z):.1f}" fill="#C8B88A"/>')
    out.append(Q([C(-9.6, 2.4, hz0), C(-4.2, 2.4, hz0), C(-4.2, 2.4, hz1 - 4), C(-5.2, 3.0, hz1 + 1.5), C(-9.6, 3.0, hz1 - 2)], "#9A7656"))
    # stern transom facing us
    out.append(Q(C.quad_z(hz0, -9.6, -4.2, -0.2, 2.4), "#2A3C38"))
    out.append(Q(C.quad_z(hz0, -9.6, -4.2, 1.95, 2.4), "#B8443E"))
    out.append(Q(C.quad_z(hz0, -9.6, -4.2, -0.2, 0.3), "#1A2624"))
    rx0, ry0 = C(-9.6, 2.4, hz0)
    rx1, _ = C(-4.2, 2.4, hz0)
    rh = 0.9 * C.f / hz0
    out.append(f'<g stroke="#E8DCC4" stroke-width="1.4"><line x1="{rx0:.1f}" y1="{ry0 - rh:.1f}" x2="{rx1:.1f}" y2="{ry0 - rh:.1f}"/>' + "".join(
        f'<line x1="{lerp(rx0, rx1, t):.1f}" y1="{ry0 - rh:.1f}" x2="{lerp(rx0, rx1, t):.1f}" y2="{ry0:.1f}"/>' for t in (0.02, 0.33, 0.66, 0.98)) + "</g>")
    lx_, ly_ = C(-6.9, 1.1, hz0)
    out.append(f'<ellipse cx="{lx_:.1f}" cy="{ly_:.1f}" rx="{0.9 * C.f / hz0:.1f}" ry="{0.5 * C.f / hz0:.1f}" fill="none" stroke="#E8DCC4" stroke-width="1.6"/>')
    # long saloon cabin
    cz0, cz1 = hz0 + 5, hz1 - 6
    out.append(Q(C.quad_x(-4.9, cz0, cz1, 2.4, 4.5), "#EFE4CF"))
    out.append(Q(C.quad_z(cz0, -9.2, -4.9, 2.4, 4.5), "#D9CBB2"))
    out.append(Q(C.quad_z(cz0, -7.6, -6.4, 2.4, 4.0), "#7A5A44"))
    out.append(Q([C(-9.2, 4.5, cz0), C(-4.6, 4.5, cz0), C(-4.6, 4.5, cz1), C(-9.2, 4.5, cz1)], "#3E5A4A"))
    out.append(Q([C(-4.6, 4.5, cz0), C(-4.6, 4.75, cz0), C(-4.6, 4.75, cz1), C(-4.6, 4.5, cz1)], "#E8D9B8"))
    for i in range(6):
        za = cz0 + 1.2 + i * (cz1 - cz0 - 2) / 6
        out.append(Q(C.quad_x(-4.9, za, za + 2.2, 3.0, 4.0), "#F7C873" if i in (1, 2, 4) else "#6E8AA6"))
    # wheelhouse at the stern
    out.append(Q(C.quad_x(-5.8, hz0 + 0.8, hz0 + 3.8, 2.4, 5.4), "#EFE4CF"))
    out.append(Q(C.quad_x(-5.8, hz0 + 1.3, hz0 + 3.3, 4.0, 5.0), "#6E8AA6"))
    out.append(Q(C.quad_z(hz0 + 0.8, -8.4, -5.8, 2.4, 5.4), "#D9CBB2"))
    out.append(Q(C.quad_z(hz0 + 0.8, -7.9, -6.3, 4.0, 5.0), "#8EA8C0"))
    out.append(Q([C(-8.6, 5.4, hz0 + 0.6), C(-5.5, 5.4, hz0 + 0.6), C(-5.5, 5.4, hz0 + 4.0), C(-8.6, 5.4, hz0 + 4.0)], "#B8443E"))
    # geraniums in pots along the roof
    for z in [cz0 + 1 + i * 3.2 for i in range(6)]:
        px, py = C(-5.0, 4.75, z)
        s_ = C.f / z
        out.append(f'<rect x="{px - 0.4 * s_:.1f}" y="{py - 0.4 * s_:.1f}" width="{0.8 * s_:.1f}" height="{0.4 * s_:.1f}" fill="#B0603E"/>')
        out.append(blobs(7, int(z * 7), (px - 0.5 * s_, py - 0.95 * s_, px + 0.5 * s_, py - 0.35 * s_), ["#D8343A", "#F0605A", "#3E6A30", "#5E8A3E"], r=(0.13 * s_, 0.24 * s_), opacity=(0.95, 1), squash=1))
    # bow deck: two chairs and a reader
    for z in (hz1 - 3.6, hz1 - 2.2):
        px, pb = C(-6.6, 2.6, z)
        s_ = C.f / z
        out.append(f'<path d="M {px - 0.4 * s_:.1f} {pb:.1f} L {px - 0.3 * s_:.1f} {pb - 0.9 * s_:.1f} L {px + 0.35 * s_:.1f} {pb - 0.5 * s_:.1f} L {px + 0.4 * s_:.1f} {pb:.1f}" fill="#E0B04A" stroke="#6A4A2A" stroke-width="1"/>')
    px, pb = C(-7.6, 2.6, hz1 - 3)
    out.append(figure(px, pb, C.f * 1.2 / (hz1 - 3), "#3E6A8A", head="#4A2E22"))
    out.append(water_lines(50, 77, (C(-4, 0, hz1)[0] - 10, C(-4, 0, hz1)[1], C(-4, 0, hz0)[0] + 50, 444), ["#22322E", "#B8443E", "#EFE4CF"], w=(10, 40), opacity=(0.2, 0.5)))
    # lamp posts on the parapet
    for Z in (22.5, 45, 90):
        x0, y0 = C(-10.3, 8, Z)
        x1, y1 = C(-10.3, 12.5, Z)
        s = C.f / Z
        out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#23332C" stroke-width="{max(1.2, 0.14 * s):.1f}"/>'
                   f'<path d="M {x1 - 0.22 * s:.1f} {y1:.1f} L {x1 - 0.3 * s:.1f} {y1 - 0.6 * s:.1f} L {x1 + 0.3 * s:.1f} {y1 - 0.6 * s:.1f} L {x1 + 0.22 * s:.1f} {y1:.1f} Z" fill="#F2E2B8" stroke="#23332C" stroke-width="{max(0.8, 0.05 * s):.1f}"/>'
                   f'<path d="M {x1 - 0.36 * s:.1f} {y1 - 0.6 * s:.1f} L {x1:.1f} {y1 - 0.85 * s:.1f} L {x1 + 0.36 * s:.1f} {y1 - 0.6 * s:.1f} Z" fill="#23332C"/>')
    # people at the stalls and strolling
    for X, Z, h, c, bag in ((-11.2, 18, 1.7, "#B8574A", None), (-11.4, 28, 1.75, "#3E5A7A", "#E0B04A"), (-13.5, 42, 1.65, "#E8D8C0", None), (-12.2, 60, 1.7, "#4A6A5A", None)):
        px, pb = C(X, 7, Z)
        out.append(figure(px, pb, C.f * h / Z, c, bag=bag, rim="#FFD9A0", rim_side=-1))
    # the nearest plane trees overhang the foreground
    for k, (X, Z) in enumerate(trees[:2]):
        out.append(plane_tree(C, X, Z, 7, 19, 400 + k))
    out.append(gulls([(170, 160, 12), (196, 174, 9), (440, 250, 8)], "#4A4058"))
    return "\n".join(out)


# ================================================================ JAPAN — Mount Fuji, the five-story pagoda, cherry blossom
def blossoms(uid, cx, cy, rx, ry, seed, n=90, base="#F2B3C6", shade="#D98AA6", lit="#FFE3EC", white="#FFF4F7", fleck="#C9577A", light=(-1, -1), florets=True, r=(0.12, 0.26), twigs="#5A3438"):
    """A cloud of cherry blossom: clumps shaded from the light side, twigs peeking through, flower specks on the lit edge."""
    rnd = random.Random(seed)
    clumps = []
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(0, 1) ** 0.55
        x, y = cx + rx * d * math.cos(a), cy + ry * d * math.sin(a)
        clumps.append((x, y, min(rx, ry) * rnd.uniform(*r) * 1.4))
    lx, ly = light
    out = ['<g fill="%s">' % base + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}"/>' for x, y, rr in clumps) + "</g>"]
    out.append(f'<g fill="{shade}" opacity="0.75">' + "".join(f'<circle cx="{x - lx * rr * 0.3:.1f}" cy="{y - ly * rr * 0.35:.1f}" r="{rr * 0.72:.1f}"/>'
                                                          for x, y, rr in clumps if (x - cx) * lx / rx + (y - cy) * ly / ry < 0.15) + "</g>")
    if twigs and florets:
        tw = []
        for _ in range(int(n / 25) + 2):
            x0, y0 = cx + rnd.uniform(-0.6, 0.6) * rx, cy + rnd.uniform(-0.3, 0.5) * ry
            L = rnd.uniform(0.2, 0.45) * rx
            a = rnd.uniform(-2.6, -0.5)
            tw.append(f'<path d="M {x0:.1f} {y0:.1f} q {L * 0.5 * math.cos(a) + 4:.1f} {L * 0.5 * math.sin(a):.1f} {L * math.cos(a):.1f} {L * math.sin(a):.1f}" stroke-width="{rnd.uniform(1.4, 2.6):.1f}"/>')
        out.append(f'<g stroke="{twigs}" fill="none" stroke-linecap="round" opacity="0.8">{"".join(tw)}</g>')
    out.append(f'<g fill="{lit}" opacity="0.9">' + "".join(f'<circle cx="{x + lx * rr * 0.3:.1f}" cy="{y + ly * rr * 0.3:.1f}" r="{rr * 0.55:.1f}"/>'
                                                         for x, y, rr in clumps if (x - cx) * lx / rx + (y - cy) * ly / ry > -0.2) + "</g>")
    if florets:
        fl, sp = [], []
        for x, y, rr in clumps:
            for _ in range(2):
                fx, fy = x + rnd.uniform(-rr, rr) * 0.9, y + rnd.uniform(-rr, rr) * 0.9
                if (fx - cx) * lx / rx + (fy - cy) * ly / ry > -0.3 and rnd.random() < 0.5:
                    fl.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{rnd.uniform(0.9, 1.7):.1f}"/>')
                elif rnd.random() < 0.3:
                    sp.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{rnd.uniform(0.6, 1.1):.1f}"/>')
        out.append(f'<g fill="{white}">{"".join(fl)}</g><g fill="{fleck}" opacity="0.7">{"".join(sp)}</g>')
    return "".join(out)


def branch(pts, w0, w1, color):
    """Tapered branch along a polyline (list of points)."""
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        x2, y2 = pts[min(i + 1, n - 1)]
        x1, y1 = pts[max(i - 1, 0)]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = lerp(w0, w1, i / (n - 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return Q(left + right[::-1], color)


def pagoda(cx, base, k, u):
    """Five-story pagoda, front view from slightly above, morning light from the left."""
    out = [defs(lg(f"{u}-pb", [(0, "#F0643C"), (0.5, "#D8402A"), (1, "#9E2A22")], 0, 0, 1, 0),
                lg(f"{u}-pr", [(0, "#6E6A74"), (0.48, "#4A4652"), (0.52, "#36323C"), (1, "#26222A")], 0, 0, 1, 0))]
    y = base
    # stone plinth and steps
    out.append(f'<rect x="{cx - 52 * k:.1f}" y="{y - 9 * k:.1f}" width="{104 * k:.1f}" height="{9 * k:.1f}" fill="#B9B2AA"/><rect x="{cx - 52 * k:.1f}" y="{y - 9 * k:.1f}" width="{104 * k:.1f}" height="{2.5 * k:.1f}" fill="#E8E2D8"/>')
    out.append(f'<rect x="{cx - 14 * k:.1f}" y="{y - 9 * k:.1f}" width="{28 * k:.1f}" height="{9 * k:.1f}" fill="#A8A098"/>' + "".join(
        f'<rect x="{cx - 14 * k:.1f}" y="{y - (2 + 3 * i) * k:.1f}" width="{28 * k:.1f}" height="{0.8 * k:.1f}" fill="#E8E2D8"/>' for i in range(3)))
    y -= 9 * k
    R = [76, 70, 64, 58, 53]
    for i in range(5):
        Rk = R[i] * k
        B = (40 - 3.2 * i) * k
        hb = (24 if i == 0 else 15) * k
        # body
        out.append(f'<rect x="{cx - B:.1f}" y="{y - hb:.1f}" width="{2 * B:.1f}" height="{hb:.1f}" fill="url(#{u}-pb)"/>')
        if i == 0:
            out.append(f'<rect x="{cx - B * 0.32:.1f}" y="{y - hb * 0.8:.1f}" width="{B * 0.64:.1f}" height="{hb * 0.8:.1f}" fill="#3A2226"/>')
            for sx in (-1, 1):
                out.append(f'<rect x="{cx + sx * B * 0.66 - B * 0.15:.1f}" y="{y - hb * 0.75:.1f}" width="{B * 0.3:.1f}" height="{hb * 0.5:.1f}" fill="#F4E4C8"/>'
                           f'<g stroke="#9E2A22" stroke-width="{0.8 * k:.1f}">' + "".join(
                               f'<line x1="{cx + sx * B * 0.66 - B * 0.15 + j * B * 0.075:.1f}" y1="{y - hb * 0.75:.1f}" x2="{cx + sx * B * 0.66 - B * 0.15 + j * B * 0.075:.1f}" y2="{y - hb * 0.25:.1f}"/>' for j in range(1, 4)) + "</g>")
        else:
            # balcony railing in white with posts
            out.append(f'<rect x="{cx - B - 4 * k:.1f}" y="{y - 5 * k:.1f}" width="{2 * B + 8 * k:.1f}" height="{1.6 * k:.1f}" fill="#F4E8D8"/>')
            out.append(f'<g fill="#F4E8D8">' + "".join(f'<rect x="{cx - B - 4 * k + j * (2 * B + 8 * k) / 8 - 0.6 * k:.1f}" y="{y - 5 * k:.1f}" width="{1.2 * k:.1f}" height="{5 * k:.1f}"/>' for j in range(9)) + "</g>")
            out.append(f'<rect x="{cx - B * 0.25:.1f}" y="{y - hb * 0.9:.1f}" width="{B * 0.5:.1f}" height="{hb * 0.55:.1f}" fill="#4A2A2A"/>')
        # bracket band
        bb = 6 * k
        out.append(f'<rect x="{cx - B - 6 * k:.1f}" y="{y - hb - bb:.1f}" width="{2 * B + 12 * k:.1f}" height="{bb:.1f}" fill="#8E2620"/>')
        out.append(f'<g fill="#F2C49A" opacity="0.7">' + "".join(f'<rect x="{cx - B - 6 * k + j * (2 * B + 12 * k) / 12 + 1:.1f}" y="{y - hb - bb + 1.2 * k:.1f}" width="{1.8 * k:.1f}" height="{bb * 0.45:.1f}"/>' for j in range(12)) + "</g>")
        # roof: upturned eaves, visible top surface
        yc = y - hb - bb + 2.5 * k
        up = 13 * k
        rt = yc - 14 * k
        tw = B * 0.82
        lt, rtp = (cx - Rk, yc - up), (cx + Rk, yc - up)
        d = (f"M {lt[0]:.1f} {lt[1]:.1f} Q {cx - Rk * 0.55:.1f} {yc + 2 * k:.1f} {cx:.1f} {yc:.1f} Q {cx + Rk * 0.55:.1f} {yc + 2 * k:.1f} {rtp[0]:.1f} {rtp[1]:.1f} "
             f"L {cx + tw:.1f} {rt:.1f} L {cx - tw:.1f} {rt:.1f} Z")
        out.append(f'<path d="M {lt[0]:.1f} {lt[1]:.1f} Q {cx - Rk * 0.55:.1f} {yc + 2 * k:.1f} {cx:.1f} {yc:.1f} Q {cx + Rk * 0.55:.1f} {yc + 2 * k:.1f} {rtp[0]:.1f} {rtp[1]:.1f} '
                   f'L {rtp[0]:.1f} {rtp[1] + 3 * k:.1f} Q {cx + Rk * 0.55:.1f} {yc + 5 * k:.1f} {cx:.1f} {yc + 3.2 * k:.1f} Q {cx - Rk * 0.55:.1f} {yc + 5 * k:.1f} {lt[0]:.1f} {lt[1] + 3 * k:.1f} Z" fill="#1E1A20"/>')
        out.append(f'<path d="{d}" fill="url(#{u}-pr)"/>')
        # tile ribs converging up the roof
        ribs = []
        for j in range(1, 22):
            t = j / 22
            # point on eave (approx along the two quadratic curves)
            if t < 0.5:
                tt = t * 2
                ex = (1 - tt) ** 2 * lt[0] + 2 * (1 - tt) * tt * (cx - Rk * 0.55) + tt * tt * cx
                ey = (1 - tt) ** 2 * lt[1] + 2 * (1 - tt) * tt * (yc + 2 * k) + tt * tt * yc
            else:
                tt = (t - 0.5) * 2
                ex = (1 - tt) ** 2 * cx + 2 * (1 - tt) * tt * (cx + Rk * 0.55) + tt * tt * rtp[0]
                ey = (1 - tt) ** 2 * yc + 2 * (1 - tt) * tt * (yc + 2 * k) + tt * tt * rtp[1]
            tx = cx - tw + 2 * tw * t
            ribs.append(f'<line x1="{ex:.1f}" y1="{ey:.1f}" x2="{tx:.1f}" y2="{rt:.1f}"/>')
        out.append(f'<g stroke="#8E8A96" stroke-width="{0.7 * k:.1f}" opacity="0.45">{"".join(ribs)}</g>')
        out.append(f'<path d="M {lt[0]:.1f} {lt[1]:.1f} Q {cx - Rk * 0.55:.1f} {yc + 2 * k:.1f} {cx:.1f} {yc:.1f} Q {cx + Rk * 0.55:.1f} {yc + 2 * k:.1f} {rtp[0]:.1f} {rtp[1]:.1f}" fill="none" stroke="#C8C2CC" stroke-width="{1.6 * k:.1f}" stroke-linecap="round"/>')
        out.append(f'<path d="M {lt[0]:.1f} {lt[1]:.1f} Q {cx - Rk * 0.55:.1f} {yc + 2 * k:.1f} {cx - Rk * 0.1:.1f} {yc + 0.3 * k:.1f}" fill="none" stroke="#FFFFFF" stroke-width="{1.4 * k:.1f}" stroke-linecap="round" opacity="0.8"/>')
        # hip ridges toward the corners
        out.append(f'<g stroke="#2A262E" stroke-width="{1.4 * k:.1f}" stroke-linecap="round"><line x1="{cx - tw:.1f}" y1="{rt:.1f}" x2="{lt[0] + 3 * k:.1f}" y2="{lt[1] + 1 * k:.1f}"/><line x1="{cx + tw:.1f}" y1="{rt:.1f}" x2="{rtp[0] - 3 * k:.1f}" y2="{rtp[1] + 1 * k:.1f}"/></g>')
        y = rt
    # finial: square cap, nine rings, flame
    out.append(f'<rect x="{cx - 8 * k:.1f}" y="{y - 6 * k:.1f}" width="{16 * k:.1f}" height="{6 * k:.1f}" fill="#3A3640"/>')
    out.append(f'<rect x="{cx - 1.6 * k:.1f}" y="{y - 58 * k:.1f}" width="{3.2 * k:.1f}" height="{52 * k:.1f}" fill="#4A3E36"/>')
    for j in range(9):
        yy = y - 12 * k - j * 4.2 * k
        out.append(f'<ellipse cx="{cx:.1f}" cy="{yy:.1f}" rx="{(5.5 - j * 0.25) * k:.1f}" ry="{1.3 * k:.1f}" fill="#6E5A44"/><ellipse cx="{cx - 1.2 * k:.1f}" cy="{yy - 0.4 * k:.1f}" rx="{2.4 * k:.1f}" ry="{0.6 * k:.1f}" fill="#D8B878"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{y - 58 * k:.1f}" r="{3 * k:.1f}" fill="#B89458"/>')
    return "".join(out)


def japan():
    u = "jp"
    out = [defs(
        lg(f"{u}-sky", [(0, "#4C7FC0"), (0.35, "#86AEDA"), (0.62, "#CFE0EE"), (0.75, "#F6E2E6")], 0, 0, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-mt", [(0, "#6A7CB0"), (0.45, "#7F92C0"), (1, "#B6C6E0")], 0, 180, 0, 330, units="userSpaceOnUse"),
        lg(f"{u}-snow", [(0, "#FFFFFF"), (0.42, "#F2F5FA"), (0.56, "#C6D2E8"), (1, "#A9B8D8")], 250, 0, 520, 0, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#EAF0F6", 0), (1, "#EEF2F6", 0.9)], 0, 250, 0, 330, units="userSpaceOnUse"),
        lg(f"{u}-hill", [(0, "#4E6E4A"), (1, "#2E4632")], 0, 300, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(40, 60, 260, "#FFF6E0", f"{u}-sun", 0.6))
    out.append(cumulus(f"{u}-c1", 110, 168, 150, 40, 21, "#FFFFFF", "#F2EEF4", "#C2CCE2", hi="#FFFFFF", hi_op=0.7))
    out.append(cumulus(f"{u}-c2", 560, 150, 110, 30, 22, "#FFFFFF", "#EEF0F6", "#C2CCE2", hi="#FFFFFF", hi_op=0.7))
    for x, y, w in ((220, 120, 60), (520, 106, 70)):
        out.append(streak_cloud(x, y, w, "#FFFFFF", 0.55, 3))
    # Mount Fuji: concave flanks, flat crater rim
    cx, top, H, L = 382, 112, 236, 215

    def fy(x):
        d = max(0.0, abs(x - cx) - 26)
        return top + H * (1 - math.exp(-d / L)) + (2.0 * math.sin(x * 0.7) if abs(x - cx) < 26 else 0)

    xs = [-10 + i * 5 for i in range(125)]
    prof = [(x, fy(x)) for x in xs]
    rim = rough([(cx - 28, top + 2), (cx - 12, top - 2), (cx + 2, top + 1), (cx + 16, top - 2), (cx + 28, top + 2)], 5, amp=2, depth=3)
    prof = [p for p in prof if p[0] < cx - 28] + rim + [p for p in prof if p[0] > cx + 28]
    out.append(Q(prof + [(610, 444), (-10, 444)], f"url(#{u}-mt)"))
    # shadow side (right) and lit side (left)
    out.append(Q([p for p in prof if p[0] >= cx] + [(610, 340), (cx + 40, 340)], "#4E5E94", ' opacity="0.28"'))
    out.append(f'<clipPath id="{u}-mc"><polygon points="{P(prof + [(610, 444), (-10, 444)])}"/></clipPath>')
    g = []
    rnd = random.Random(9)
    for i in range(46):  # ravines fanning down the flanks
        side = -1 if i % 2 else 1
        d0 = rnd.uniform(20, 170)
        x0 = cx + side * d0
        y0 = fy(x0) + rnd.uniform(2, 10)
        L_ = rnd.uniform(40, 120)
        x1 = x0 + side * L_ * rnd.uniform(0.45, 0.8)
        y1 = fy(x1) + L_ * 0.25
        g.append(f'<path d="M {x0:.1f} {y0:.1f} Q {(x0 + x1) / 2 + side * 4:.1f} {(y0 + y1) / 2:.1f} {x1:.1f} {y1:.1f}" stroke="{"#9AAAD2" if side < 0 else "#5A6A9E"}" stroke-width="{rnd.uniform(1, 2.4):.1f}" fill="none" opacity="0.55"/>')
    out.append(f'<g clip-path="url(#{u}-mc)">{"".join(g)}</g>')
    # snow cap with long, irregular fingers down the gullies
    snow_top = [p for p in prof if abs(p[0] - cx) < 178]
    fingers = [(cx + rnd.uniform(-172, 172), rnd.uniform(10, 58), rnd.uniform(1.6, 5)) for _ in range(44)]
    lower = []
    n = 150
    for i in range(n + 1):
        x = cx + 178 - 356 * i / n
        d = abs(x - cx)
        depth = (1 - (d / 178) ** 1.5) * 64 + 3
        depth *= 0.82 + 0.18 * math.sin(x * 0.09) * math.sin(x * 0.031 + 1)
        depth += sum(hgt * math.exp(-((x - fx) / wd) ** 2) for fx, hgt, wd in fingers) * (1 - (d / 178) ** 2)
        lower.append((x, fy(x) + max(3, depth)))
    out.append(Q(snow_top + lower, f"url(#{u}-snow)"))
    # streaks of rock showing through the snow, and blue gully shadows
    sg = []
    for i in range(60):
        side = -1 if i % 2 else 1
        x0 = cx + side * rnd.uniform(6, 130)
        y0 = fy(x0) + rnd.uniform(4, 20)
        L_ = rnd.uniform(18, 70)
        x1 = x0 + side * L_ * 0.55
        sg.append(f'<path d="M {x0:.1f} {y0:.1f} q {side * L_ * 0.2:.1f} {L_ * 0.45:.1f} {x1 - x0:.1f} {L_:.1f}" fill="none" stroke="{"#B8C6E2" if side < 0 else "#93A3CC"}" stroke-width="{rnd.uniform(0.8, 2.2):.1f}" opacity="{rnd.uniform(0.35, 0.7):.2f}"/>')
    out.append(f'<clipPath id="{u}-sc"><polygon points="{P(snow_top + lower)}"/></clipPath><g clip-path="url(#{u}-sc)" stroke-linecap="round">{"".join(sg)}</g>')
    out.append(f'<polyline points="{P([p for p in snow_top if p[0] <= cx + 4])}" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{P([p for p in snow_top if p[0] >= cx - 4])}" fill="none" stroke="#DDE6F4" stroke-width="1.6" stroke-linejoin="round"/>')
    # haze at the mountain's foot and a soft cloud band
    out.append(f'<rect x="0" y="250" width="600" height="82" fill="url(#{u}-haze)"/>')
    out.append(cumulus(f"{u}-c3", 520, 300, 220, 34, 31, "#FFFFFF", "#F2F2F8", "#C8D0E4", hi="#FFFFFF", hi_op=0.6))
    # foothills and the town of Fujiyoshida in the valley
    poly, l1 = ridge_poly([(-10, 300), (120, 292), (260, 306), (400, 298), (520, 290), (610, 296)], 7, amp=6, fill="#93A7B8")
    out.append(poly)
    poly, l2 = ridge_poly([(-10, 318), (90, 306), (220, 320), (340, 314), (470, 304), (610, 312)], 8, amp=5, fill="#6E8A84")
    out.append(poly)
    out.append(tree_line(l2, 12, ["#5E7A70", "#6A867A", "#58746A"], density=1.6, hmin=6, hmax=12))
    out.append(Q([(-10, 330), (610, 322), (610, 444), (-10, 444)], "#8EA08A"))
    rnd = random.Random(15)
    houses = []
    for _ in range(170):
        x = rnd.uniform(200, 610)
        y = rnd.uniform(322, 372)
        k = 0.6 + (y - 322) / 50 * 0.9
        w, h = rnd.uniform(7, 14) * k, rnd.uniform(4, 7) * k
        houses.append((y, x, w, h))
    for y, x, w, h in sorted(houses):
        roof = rnd.choice(["#5E6A86", "#7A8298", "#8E5A4E", "#4E5A72", "#A4A8B4"])
        houses_svg = (f'<rect x="{x:.1f}" y="{y - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{rnd.choice(["#F2EEE6", "#E6E0D6", "#DCD8D2", "#EDE4D2"])}"/>'
                      f'<polygon points="{P([(x - 1, y - h), (x + w * 0.2, y - h - h * 0.6), (x + w * 0.8, y - h - h * 0.6), (x + w + 1, y - h)])}" fill="{roof}"/>'
                      f'<rect x="{x + w * 0.6:.1f}" y="{y - h:.1f}" width="{w * 0.4:.1f}" height="{h:.1f}" fill="#8A90A8" opacity="0.35"/>')
        out.append(houses_svg)
        if rnd.random() < 0.18:
            out.append(blossoms(f"{u}-tb{int(x)}{int(y)}", x + rnd.uniform(-6, 6), y - h, 6 * k, 4 * k, int(x * y), n=10, florets=False))
        elif rnd.random() < 0.2:
            out.append(f'<circle cx="{x:.1f}" cy="{y - h:.1f}" r="{4 * k:.1f}" fill="#6E8A62"/>')
    out.append(mist(420, 330, 260, 16, "#F4F2F6", f"{u}-m1", 0.55))
    # the Chureito hillside: forest and blossom
    poly, hl = ridge_poly([(-10, 300), (60, 312), (150, 330), (250, 352), (330, 384), (420, 444)], 13, amp=6, fill=f"url(#{u}-hill)")
    out.append(poly)
    for k_, (x, y, rx, ry) in enumerate(((40, 316, 50, 22), (110, 330, 48, 20), (250, 362, 44, 22), (310, 392, 46, 24), (20, 350, 60, 26))):
        out.append(leaf_canopy(f"{u}-f{k_}", x, y, rx, ry, 60 + k_, "#22362A", "#3A5A3C", "#6E8E52", light=(-1, -1), n=40))
    out.append(f'<clipPath id="{u}-hc"><polygon points="{P(hl + [(420, 444), (-10, 444)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-hc)">' + grass(260, 14, (100, 330, 430, 444), ["#5E7E4A", "#3E5A3A", "#7E9A5A", "#2A4030"], h=(5, 12), sw=1.4) + "</g>")
    out.append(leaf_canopy(f"{u}-f9", 380, 430, 60, 26, 69, "#22362A", "#3A5A3C", "#6E8E52", light=(-1, -1), n=40))
    for k_, (x, y, rx, ry) in enumerate(((70, 322, 34, 18), (270, 352, 30, 18), (330, 372, 26, 16), (240, 386, 40, 20), (350, 414, 40, 20))):
        out.append(blossoms(f"{u}-hb{k_}", x, y, rx, ry, 70 + k_, n=110, r=(0.08, 0.18)))
    out.append(pagoda(176, 382, 1.0, u))
    # foreground blossom framing the view
    br = "#4A2E30"
    out.append(branch([(-10, 440), (40, 420), (90, 404), (150, 398), (210, 404)], 18, 4, br))
    out.append(branch([(60, 412), (80, 380), (96, 362)], 8, 3, br))
    out.append(blossoms(f"{u}-b1", 70, 412, 110, 46, 81, n=320, r=(0.06, 0.14)))
    out.append(blossoms(f"{u}-b2", 200, 412, 50, 26, 82, n=140, r=(0.06, 0.14)))
    out.append(branch([(610, 380), (560, 390), (510, 404), (460, 424)], 16, 4, br))
    out.append(branch([(560, 390), (540, 360), (528, 340)], 8, 3, br))
    out.append(blossoms(f"{u}-b3", 540, 396, 90, 50, 83, n=300, r=(0.06, 0.14)))
    out.append(blossoms(f"{u}-b4", 462, 424, 50, 24, 84, n=120, r=(0.06, 0.14)))
    out.append(branch([(610, 40), (570, 62), (534, 84), (500, 92)], 12, 3, br))
    out.append(branch([(570, 62), (556, 96)], 6, 2, br))
    out.append(blossoms(f"{u}-b5", 560, 74, 70, 34, 85, n=200, r=(0.06, 0.14)))
    out.append(blossoms(f"{u}-b6", 512, 96, 34, 18, 86, n=70, r=(0.06, 0.14)))
    out.append(branch([(-10, 52), (30, 70), (66, 80)], 10, 3, br))
    out.append(blossoms(f"{u}-b7", 30, 70, 56, 28, 87, n=150, r=(0.06, 0.14)))
    # drifting petals
    rnd = random.Random(88)
    pet = []
    for _ in range(46):
        x, y = rnd.uniform(60, 560), rnd.uniform(90, 400)
        a = rnd.uniform(0, 180)
        pet.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(2, 3.6):.1f}" ry="{rnd.uniform(1.2, 2):.1f}" transform="rotate({a:.0f} {x:.1f} {y:.1f})" fill="{rnd.choice(["#FFE6EE", "#F7C2D2", "#FFFFFF"])}" opacity="{rnd.uniform(0.7, 1):.2f}"/>')
    out.append("".join(pet))
    out.append(gulls([(250, 168, 10), (272, 180, 7)], "#3E4A6E", 1.8))
    return "\n".join(out)


# ================================================================ SANTORINI — Oia cascading to the caldera at sunset
def cyc_house(x, base, w, h, k, rnd, dx=None, dy=None):
    """Cycladic cube house in oblique view: front face in pink shade, sunlit side face on the right, pale roof."""
    dx = 7 * k if dx is None else dx
    dy = 5 * k if dy is None else dy
    tint = rnd.random()
    if tint < 0.12:
        front, side, top = "#E2A86A", "#F8CC86", "#F2C690"
    elif tint < 0.2:
        front, side, top = "#CF7A62", "#F2A27A", "#E8A488"
    elif tint < 0.26:
        front, side, top = "#E0A0A6", "#F8C6B8", "#F2C6C2"
    else:
        front, side, top = "#EBCFD2", "#FFEBD6", "#FBE6DE"
    out = [Q([(x + w, base), (x + w, base - h), (x + w + dx, base - h - dy), (x + w + dx, base - dy)], side),
           f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{front}"/>',
           f'<rect x="{x:.1f}" y="{base - h * 0.45:.1f}" width="{w:.1f}" height="{h * 0.45:.1f}" fill="#9A7AA6" opacity="0.18"/>']
    if rnd.random() < 0.28:  # barrel-vaulted roof
        out.append(f'<path d="M {x:.1f} {base - h:.1f} Q {x + w / 2:.1f} {base - h - w * 0.55:.1f} {x + w:.1f} {base - h:.1f} L {x + w + dx:.1f} {base - h - dy:.1f} Q {x + w / 2 + dx:.1f} {base - h - dy - w * 0.55:.1f} {x + dx:.1f} {base - h - dy:.1f} Z" fill="{top}"/>')
        out.append(f'<path d="M {x:.1f} {base - h:.1f} Q {x + w / 2:.1f} {base - h - w * 0.55:.1f} {x + w:.1f} {base - h:.1f} Z" fill="{front}"/>')
        out.append(f'<path d="M {x + w / 2:.1f} {base - h - w * 0.27:.1f} Q {x + w * 0.8:.1f} {base - h - w * 0.22:.1f} {x + w:.1f} {base - h:.1f}" fill="none" stroke="#FFF2E0" stroke-width="{1.2 * k:.1f}"/>')
    else:
        out.append(Q([(x, base - h), (x + w, base - h), (x + w + dx, base - h - dy), (x + dx, base - h - dy)], top))
        out.append(f'<rect x="{x - 0.5:.1f}" y="{base - h - 1.2 * k:.1f}" width="{w + 1:.1f}" height="{1.6 * k:.1f}" fill="#FFF4EA"/>')
    out.append(f'<line x1="{x + w:.1f}" y1="{base - h:.1f}" x2="{x + w:.1f}" y2="{base:.1f}" stroke="#FFE2B8" stroke-width="{1.2 * k:.1f}" opacity="0.9"/>')
    r_ = rnd.random()
    if r_ < 0.18:  # little cycladic chimney
        cxp = x + w * rnd.uniform(0.3, 0.8) + dx * 0.5
        cy0 = base - h - dy * 0.5
        out.append(f'<rect x="{cxp - 1.6 * k:.1f}" y="{cy0 - 6 * k:.1f}" width="{3.2 * k:.1f}" height="{6 * k:.1f}" fill="{front}"/><rect x="{cxp + 0.4 * k:.1f}" y="{cy0 - 6 * k:.1f}" width="{1.2 * k:.1f}" height="{6 * k:.1f}" fill="{side}"/>'
                   f'<path d="M {cxp - 2.4 * k:.1f} {cy0 - 6 * k:.1f} Q {cxp:.1f} {cy0 - 9 * k:.1f} {cxp + 2.4 * k:.1f} {cy0 - 6 * k:.1f} Z" fill="{top}"/>')
    elif r_ < 0.3 and w > 14 * k:  # whitewashed steps climbing the side
        for j in range(4):
            out.append(f'<rect x="{x + w - (j + 1) * 3 * k:.1f}" y="{base - (j + 1) * h * 0.2:.1f}" width="{3 * k * (j + 1):.1f}" height="{h * 0.2:.1f}" fill="#FFF0E2" opacity="0.9"/>')
            out.append(f'<rect x="{x + w - (j + 1) * 3 * k:.1f}" y="{base - (j + 1) * h * 0.2:.1f}" width="{3 * k * (j + 1):.1f}" height="{0.8 * k:.1f}" fill="#B89AB0" opacity="0.6"/>')
    # door and windows
    dcol = rnd.choice(["#2A5DA8", "#2E7E9A", "#3E6EB8", "#B8443E", "#2A5DA8"])
    if w > 9 * k:
        dw, dh = 4.2 * k, min(h * 0.55, 8 * k)
        dxp = x + rnd.uniform(0.15, 0.6) * (w - dw)
        out.append(f'<path d="M {dxp:.1f} {base:.1f} L {dxp:.1f} {base - dh + dw / 2:.1f} Q {dxp + dw / 2:.1f} {base - dh - dw * 0.15:.1f} {dxp + dw:.1f} {base - dh + dw / 2:.1f} L {dxp + dw:.1f} {base:.1f} Z" fill="{dcol}"/>')
        for _ in range(rnd.choice((0, 1, 1, 2))):
            wx = x + rnd.uniform(0.1, 0.8) * w
            if abs(wx - dxp) < dw + 2:
                continue
            wy = base - h * rnd.uniform(0.45, 0.75)
            out.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{3 * k:.1f}" height="{3.6 * k:.1f}" fill="{dcol}"/><rect x="{wx:.1f}" y="{wy:.1f}" width="{3 * k:.1f}" height="{0.8 * k:.1f}" fill="#FFF4EA"/>')
    return "".join(out)


def blue_dome(cx, base, r, u, cross=True, drum=None):
    drum = drum or r * 0.35
    out = [defs(lg(f"{u}", [(0, "#163A7A"), (0.45, "#2456B0"), (0.82, "#4A86D8"), (1, "#F6B08A")], 0, 0, 1, 0))]
    out.append(f'<rect x="{cx - r * 1.05:.1f}" y="{base - drum:.1f}" width="{r * 2.1:.1f}" height="{drum:.1f}" fill="#EBCFD2"/>')
    out.append(f'<rect x="{cx + r * 0.55:.1f}" y="{base - drum:.1f}" width="{r * 0.5:.1f}" height="{drum:.1f}" fill="#FFEBD6"/>')
    out.append(f'<rect x="{cx - r * 1.12:.1f}" y="{base - drum - r * 0.08:.1f}" width="{r * 2.24:.1f}" height="{r * 0.1:.1f}" fill="#FFF4EA"/>')
    for i in range(5):
        wx = cx - r * 0.8 + i * r * 0.4
        out.append(f'<path d="M {wx - r * 0.07:.1f} {base - drum * 0.2:.1f} L {wx - r * 0.07:.1f} {base - drum * 0.65:.1f} Q {wx:.1f} {base - drum * 0.85:.1f} {wx + r * 0.07:.1f} {base - drum * 0.65:.1f} L {wx + r * 0.07:.1f} {base - drum * 0.2:.1f} Z" fill="#2A5DA8"/>')
    y0 = base - drum - r * 0.08
    out.append(f'<path d="M {cx - r:.1f} {y0:.1f} C {cx - r:.1f} {y0 - r * 0.75:.1f} {cx - r * 0.5:.1f} {y0 - r * 1.1:.1f} {cx:.1f} {y0 - r * 1.12:.1f} C {cx + r * 0.5:.1f} {y0 - r * 1.1:.1f} {cx + r:.1f} {y0 - r * 0.75:.1f} {cx + r:.1f} {y0:.1f} Z" fill="url(#{u})"/>')
    out.append(f'<path d="M {cx + r * 0.25:.1f} {y0 - r * 1.02:.1f} C {cx + r * 0.7:.1f} {y0 - r * 0.9:.1f} {cx + r * 0.92:.1f} {y0 - r * 0.5:.1f} {cx + r * 0.95:.1f} {y0 - r * 0.1:.1f}" fill="none" stroke="#FFD6B0" stroke-width="{max(1.2, r * 0.05):.1f}" stroke-linecap="round" opacity="0.85"/>')
    for t in (-0.55, -0.15, 0.25, 0.62):  # ribs
        out.append(f'<path d="M {cx + t * r:.1f} {y0:.1f} Q {cx + t * r * 0.9:.1f} {y0 - r * 0.8:.1f} {cx:.1f} {y0 - r * 1.1:.1f}" fill="none" stroke="#112E66" stroke-width="{max(0.8, r * 0.025):.1f}" opacity="0.5"/>')
    if cross:
        ty = y0 - r * 1.12
        out.append(f'<rect x="{cx - r * 0.06:.1f}" y="{ty - r * 0.12:.1f}" width="{r * 0.12:.1f}" height="{r * 0.14:.1f}" fill="#EBCFD2"/>'
                   f'<rect x="{cx - r * 0.035:.1f}" y="{ty - r * 0.5:.1f}" width="{r * 0.07:.1f}" height="{r * 0.4:.1f}" fill="#FFF4EA"/>'
                   f'<rect x="{cx - r * 0.15:.1f}" y="{ty - r * 0.4:.1f}" width="{r * 0.3:.1f}" height="{r * 0.07:.1f}" fill="#FFF4EA"/>')
    return "".join(out)


def bell_tower(x, base, w, h):
    """Whitewashed bell gable: two tiers of arches with bronze bells, a cross on top."""
    out = [f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#EBCFD2"/>',
           f'<rect x="{x + w * 0.8:.1f}" y="{base - h:.1f}" width="{w * 0.2:.1f}" height="{h:.1f}" fill="#FFEBD6"/>',
           f'<path d="M {x - 2:.1f} {base - h:.1f} Q {x + w / 2:.1f} {base - h - w * 0.45:.1f} {x + w + 2:.1f} {base - h:.1f} Z" fill="#F4DCD8"/>']
    for row, (yy, n) in enumerate(((base - h * 0.62, 2), (base - h * 0.9, 1))):
        aw = w / (n * 2 + 1) * 1.6
        for i in range(n):
            ax = x + w * (i + 0.5) / n - aw / 2
            ah = h * 0.22
            out.append(f'<path d="M {ax:.1f} {yy + ah:.1f} L {ax:.1f} {yy + aw / 2:.1f} Q {ax + aw / 2:.1f} {yy - aw * 0.15:.1f} {ax + aw:.1f} {yy + aw / 2:.1f} L {ax + aw:.1f} {yy + ah:.1f} Z" fill="#6A4E7A"/>')
            out.append(f'<path d="M {ax + aw * 0.22:.1f} {yy + ah * 0.85:.1f} Q {ax + aw * 0.22:.1f} {yy + aw * 0.45:.1f} {ax + aw / 2:.1f} {yy + aw * 0.42:.1f} Q {ax + aw * 0.78:.1f} {yy + aw * 0.45:.1f} {ax + aw * 0.78:.1f} {yy + ah * 0.85:.1f} Z" fill="#C8963E"/>')
            out.append(f'<path d="M {ax + aw * 0.6:.1f} {yy + aw * 0.5:.1f} Q {ax + aw * 0.72:.1f} {yy + ah * 0.6:.1f} {ax + aw * 0.74:.1f} {yy + ah * 0.82:.1f}" fill="none" stroke="#FFE2A0" stroke-width="1.2"/>')
    cx = x + w / 2
    ty = base - h - w * 0.22
    out.append(f'<rect x="{cx - 1.2:.1f}" y="{ty - 14:.1f}" width="2.4" height="14" fill="#FFF4EA"/><rect x="{cx - 5:.1f}" y="{ty - 11:.1f}" width="10" height="2.4" fill="#FFF4EA"/>')
    return "".join(out)


def windmill(x, base, k, sails_rot=12):
    out = [f'<path d="M {x - 11 * k:.1f} {base:.1f} L {x - 9 * k:.1f} {base - 34 * k:.1f} L {x + 9 * k:.1f} {base - 34 * k:.1f} L {x + 11 * k:.1f} {base:.1f} Z" fill="#EBCFD2"/>',
           f'<path d="M {x + 4 * k:.1f} {base:.1f} L {x + 5 * k:.1f} {base - 34 * k:.1f} L {x + 9 * k:.1f} {base - 34 * k:.1f} L {x + 11 * k:.1f} {base:.1f} Z" fill="#FFE8D0"/>',
           f'<rect x="{x - 3 * k:.1f}" y="{base - 12 * k:.1f}" width="{5 * k:.1f}" height="{12 * k:.1f}" fill="#2A5DA8"/>',
           f'<rect x="{x - 2 * k:.1f}" y="{base - 26 * k:.1f}" width="{3.4 * k:.1f}" height="{4 * k:.1f}" fill="#4A3A4A"/>',
           f'<path d="M {x - 11 * k:.1f} {base - 33 * k:.1f} Q {x - 2 * k:.1f} {base - 52 * k:.1f} {x + 1 * k:.1f} {base - 54 * k:.1f} Q {x + 4 * k:.1f} {base - 52 * k:.1f} {x + 11 * k:.1f} {base - 33 * k:.1f} Z" fill="#9A7448"/>',
           f'<path d="M {x + 1 * k:.1f} {base - 54 * k:.1f} Q {x + 6 * k:.1f} {base - 46 * k:.1f} {x + 11 * k:.1f} {base - 33 * k:.1f} L {x + 4 * k:.1f} {base - 33 * k:.1f} Z" fill="#D8A868"/>']
    hx, hy = x - 9 * k, base - 38 * k
    for i in range(8):
        a = math.radians(sails_rot + i * 45)
        ex, ey = hx + 26 * k * math.cos(a), hy + 26 * k * math.sin(a)
        out.append(f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="#4A3A3A" stroke-width="{1.2 * k:.1f}"/>')
        if i % 2 == 0:
            a2 = a + math.radians(22)
            out.append(Q([(hx + 6 * k * math.cos(a), hy + 6 * k * math.sin(a)), (ex, ey), (hx + 22 * k * math.cos(a2), hy + 22 * k * math.sin(a2))], "#F8E8DC", ' opacity="0.9"'))
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{2 * k:.1f}" fill="#4A3A3A"/>')
    return "".join(out)


def santorini():
    u = "st"
    hz = 300
    out = [defs(
        lg(f"{u}-sky", [(0, "#36397A"), (0.22, "#6A4E8E"), (0.45, "#C0608A"), (0.62, "#EE7E6E"), (0.8, "#F8A862"), (1, "#FBC880")], 0, 0, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#F6B87A"), (0.08, "#C8708A"), (0.3, "#6A4E8E"), (1, "#26306A")], 0, hz, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-cliff", [(0, "#8E4A4E"), (0.5, "#5E3448"), (1, "#3A2440")], 0, 150, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="{hz + 1}" fill="url(#{u}-sky)"/>')
    out.append(glow(460, 284, 300, "#FFC27A", f"{u}-g1", 0.75))
    out.append(glow(460, 284, 70, "#FFF0C0", f"{u}-g2", 0.9))
    out.append(f'<circle cx="460" cy="282" r="21" fill="#FFF2CC"/>')
    for x, y, w, c in ((140, 120, 110, "#E890A0"), (80, 140, 70, "#F2A0A0"), (420, 150, 120, "#FFB490"), (540, 168, 80, "#FFC290"), (330, 206, 90, "#FFC890"),
                       (480, 228, 70, "#FFD8A0"), (240, 94, 80, "#B87AA8"), (560, 110, 60, "#C88AAE")):
        out.append(streak_cloud(x, y, w, c, 0.7, 4))
        out.append(streak_cloud(x - w * 0.2, y + 3, w * 0.6, "#FFE6C8", 0.5, 1.6))
    # sea and the caldera's far islands
    out.append(f'<rect x="0" y="{hz}" width="600" height="{444 - hz}" fill="url(#{u}-sea)"/>')
    poly, _ = ridge_poly([(-10, 266), (60, 258), (140, 268), (230, 262), (300, 280), (330, 298)], 21, base=hz + 1, amp=4, fill="#6E4A7E")
    out.append(poly)
    out.append(dots(60, 22, (0, 252, 260, 266), "#F8D8D0", r=(0.6, 1.4), opacity=(0.5, 0.9)))
    poly, _ = ridge_poly([(500, 298), (540, 288), (580, 284), (610, 288)], 23, base=hz + 1, amp=2, fill="#7E5A86")
    out.append(poly)
    # sun glitter on the water
    rnd = random.Random(5)
    for i in range(140):
        y = hz + 2 + (rnd.random() ** 1.6) * 142
        spread = 10 + (y - hz) * 0.5
        w = rnd.uniform(4, 16) * (0.4 + (y - hz) / 140)
        x = 460 + rnd.gauss(0, spread * 0.45)
        out.append(f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{0.8 + (y - hz) / 90:.1f}" rx="1" fill="{rnd.choice(["#FFE8B8", "#FFD08A", "#FFF4D8"])}" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    out.append(water_lines(80, 6, (300, hz + 4, 610, 444), ["#8A5E9A", "#3E3A7A", "#C8789A"], w=(10, 40), h=(0.8, 1.8), opacity=(0.3, 0.6)))
    # a sailing yacht heading home, sail lit by the sun
    bx, by = 520, 382
    out.append(f'<path d="M {bx - 120:.1f} {by + 9:.1f} Q {bx - 60:.1f} {by + 2:.1f} {bx - 22:.1f} {by + 3:.1f}" fill="none" stroke="#F8D8C8" stroke-width="2" opacity="0.55"/>')
    out.append(f'<path d="M {bx - 26} {by} L {bx + 22} {by} L {bx + 16} {by + 7} L {bx - 20} {by + 7} Z" fill="#F4E6EA"/><path d="M {bx - 20} {by + 5} L {bx + 17} {by + 5} L {bx + 16} {by + 7} L {bx - 20} {by + 7} Z" fill="#3A2E5A"/>')
    out.append(f'<line x1="{bx - 2}" y1="{by}" x2="{bx - 2}" y2="{by - 62}" stroke="#4A3A4A" stroke-width="1.6"/>')
    out.append(f'<path d="M {bx}, {by - 60} Q {bx + 22} {by - 30} {bx + 26} {by - 4} L {bx} {by - 4} Z" fill="#FFE2C8"/><path d="M {bx + 14} {by - 34} Q {bx + 22} {by - 20} {bx + 26} {by - 4} L {bx + 18} {by - 4} Z" fill="#FFC890" opacity="0.8"/>')
    out.append(f'<path d="M {bx - 4} {by - 56} Q {bx - 20} {by - 30} {bx - 24} {by - 6} L {bx - 4} {by - 6} Z" fill="#E8C0C8"/>')
    out.append(f'<path d="M {bx - 22} {by + 9} L {bx + 20} {by + 9}" stroke="#F4E6EA" stroke-width="1" opacity="0.4"/>')
    # the cliff of the caldera rim under the village
    edge = [(-10, 150), (120, 168), (230, 196), (300, 236), (350, 290), (384, 352), (404, 410), (420, 444)]
    cliff = rough([(-10, 220), (170, 250), (300, 300), (380, 370), (430, 444)], 3, amp=10, depth=4)
    out.append(Q([(-10, 150)] + edge[1:] + [(-10, 444)], f"url(#{u}-cliff)"))
    out.append(f'<clipPath id="{u}-cc"><polygon points="{P([(-10, 150)] + edge[1:] + [(-10, 444)])}"/></clipPath>')
    st = []
    for i, col in enumerate(("#B85A4A", "#2E2234", "#D8905E", "#7A3A44", "#E2B48A", "#4A2E3E")):
        off = 18 + i * 22
        line = rough([(x - off * 0.4, y + off) for x, y in edge], 40 + i, amp=6, depth=3)
        st.append(f'<polyline points="{P(line)}" fill="none" stroke="{col}" stroke-width="{rnd.uniform(4, 9):.1f}" opacity="0.55"/>')
    st.append(streaks(90, 7, (0, 180, 440, 444), ["#2A1E30", "#A85A4A", "#E8B08A"], w=(1.5, 4), length=(14, 50), opacity=(0.2, 0.5), slant=0.3))
    out.append(f'<g clip-path="url(#{u}-cc)">{"".join(st)}</g>')
    out.append(f'<polyline points="{P(edge[2:])}" fill="none" stroke="#FFB27A" stroke-width="2.2" opacity="0.8"/>')
    # Oia: rows of cube houses cascading down the rim, far rows small
    rnd = random.Random(42)
    rows = [(160, 0.42, 60), (176, 0.5, 150), (196, 0.58, 190), (218, 0.66, 236), (242, 0.75, 268), (268, 0.84, 296), (296, 0.94, 318), (326, 1.05, 340), (358, 1.16, 358), (392, 1.28, 376), (430, 1.42, 392), (470, 1.56, 404)]
    houses = []
    for yb, k, xmax in rows:
        x = -14 + rnd.uniform(-8, 0)
        while x < xmax - 10 * k:
            w = rnd.uniform(12, 26) * k
            h = rnd.uniform(12, 22) * k
            houses.append((yb + rnd.uniform(-5, 5) * k, x, w, h, k))
            x += w + rnd.uniform(-3, 6) * k
    special = {}
    for i, (yb, x, w, h, k) in enumerate(houses):
        out.append(cyc_house(x, yb, w, h, k, rnd))
        if rnd.random() < 0.16:  # bougainvillea spilling over a wall
            out.append(blobs(int(14 * k), i, (x + w * 0.1, yb - h * 0.9, x + w * 0.7, yb - h * 0.3), ["#D8247A", "#F04A9A", "#B81E6A", "#3E6A30"], r=(1.4 * k, 2.8 * k), opacity=(0.9, 1), squash=0.9))
        if rnd.random() < 0.08 and k > 0.8:  # a turquoise plunge pool on a terrace
            out.append(Q([(x + w * 0.15, yb - h - 1), (x + w * 0.85, yb - h - 1), (x + w * 0.85 + 5 * k, yb - h - 4.5 * k), (x + w * 0.15 + 5 * k, yb - h - 4.5 * k)], "#3EC0D0"))
            out.append(Q([(x + w * 0.2, yb - h - 1.6), (x + w * 0.5, yb - h - 1.6), (x + w * 0.5 + 3 * k, yb - h - 3.6 * k), (x + w * 0.2 + 3 * k, yb - h - 3.6 * k)], "#A8F0F4", ' opacity="0.7"'))
        if i in (40, 85):
            special[i] = (x, yb, w, h, k)
    # windmill on the ridge, the three blue domes and the bell gable
    out.append(windmill(96, 178, 1.0))
    out.append(blue_dome(150, 232, 22, f"{u}-d1"))
    out.append(blue_dome(318, 300, 34, f"{u}-d2"))
    out.append(bell_tower(250, 296, 30, 56))
    out.append(blue_dome(208, 330, 26, f"{u}-d3"))
    out.append(f'<polyline points="{P(rough([(-10, 150), (60, 156), (120, 166)], 9, amp=3, depth=3))}" fill="none" stroke="#FFB27A" stroke-width="2" opacity="0.7"/>')
    # whitewashed terrace wall in the foreground, pots of geraniums, a cat on the wall
    out.append(Q([(-10, 408), (250, 420), (330, 444), (-10, 444)], "#EBCFD2"))
    out.append(Q([(-10, 404), (250, 416), (252, 421), (-10, 410)], "#FFF2E6"))
    out.append(Q([(250, 416), (330, 440), (330, 444), (252, 421)], "#FFE2C8"))
    for x in (40, 118, 196):
        y = 404 + x * 0.046
        out.append(f'<path d="M {x - 9} {y} L {x + 9} {y} L {x + 7} {y - 13} L {x - 7} {y - 13} Z" fill="#C8643E"/><rect x="{x - 9}" y="{y - 15}" width="18" height="3" fill="#E08A5A"/>')
        out.append(blobs(16, x, (x - 12, y - 30, x + 12, y - 14), ["#E83A4A", "#FF6A6A", "#3E6A30", "#5E8A3E"], r=(2, 4), opacity=(0.95, 1), squash=1))
    cx_, cy_ = 150, 411
    out.append(f'<path d="M {cx_ - 10} {cy_} Q {cx_ - 12} {cy_ - 12} {cx_ - 4} {cy_ - 14} L {cx_ - 2} {cy_ - 19} L {cx_ + 1} {cy_ - 15} L {cx_ + 4} {cy_ - 19} L {cx_ + 5} {cy_ - 13} Q {cx_ + 8} {cy_ - 6} {cx_ + 6} {cy_} Z" fill="#3A2A3A"/>'
               f'<path d="M {cx_ + 6} {cy_} Q {cx_ + 16} {cy_ + 2} {cx_ + 18} {cy_ - 8}" fill="none" stroke="#3A2A3A" stroke-width="2.6" stroke-linecap="round"/>'
               f'<path d="M {cx_ + 5} {cy_ - 13} Q {cx_ + 8} {cy_ - 6} {cx_ + 6} {cy_}" fill="none" stroke="#FFB27A" stroke-width="1.4"/>')
    # a couple sitting on the terrace wall, watching the sun go down
    for px, py, c, hd in ((262, 418, "#2E3A6A", "#2A1E22"), (279, 422, "#C8443E", "#5A3420")):
        out.append(f'<g transform="translate({px} {py})">'
                   f'<path d="M -6 0 L -6 -16 Q 0 -21 6 -16 L 7 0 Z" fill="{c}"/>'
                   f'<path d="M 6 -15 L 7 -1" stroke="#FFC890" stroke-width="1.6" stroke-linecap="round"/>'
                   f'<circle cx="0" cy="-24" r="5" fill="{hd}"/><path d="M 3.5 -28 Q 6 -25 4.5 -21" stroke="#FFC890" stroke-width="1.4" fill="none"/>'
                   f'<path d="M -4 0 L 4 0 L 9 4 L 9 12 L 5 12 L 5 6 Z" fill="#2A2234"/></g>')
    out.append(f'<path d="M 268 404 Q 271 401 273 404" stroke="#2E3A6A" stroke-width="2.4" fill="none"/>')
    out.append(gulls([(380, 186, 11), (404, 198, 8), (300, 150, 9)], "#4A2E4E", 1.8))
    return "\n".join(out)


# ================================================================ ROME — the Colosseum in warm evening light
def umbrella_pine(x, base, h, spread, seed, lean=0.0, dark="#24362A", mid="#3A5236", lit="#8A9A4E", gold="#D8B868", trunk="#5A3E34", trunk_lit="#C88A5A"):
    """Stone pine: tall bare curving trunk forking into limbs under a broad flat canopy, sunlit from the left."""
    rnd = random.Random(seed)
    tx, ty = x + lean * h, base - h
    out = [f'<path d="M {x - h * 0.025:.1f} {base:.1f} Q {x + lean * h * 0.3:.1f} {base - h * 0.55:.1f} {tx - h * 0.012:.1f} {ty + h * 0.08:.1f} L {tx + h * 0.012:.1f} {ty + h * 0.08:.1f} Q {x + lean * h * 0.3 + h * 0.03:.1f} {base - h * 0.55:.1f} {x + h * 0.025:.1f} {base:.1f} Z" fill="{trunk}"/>',
           f'<path d="M {x - h * 0.025:.1f} {base:.1f} Q {x + lean * h * 0.3:.1f} {base - h * 0.55:.1f} {tx - h * 0.012:.1f} {ty + h * 0.08:.1f}" fill="none" stroke="{trunk_lit}" stroke-width="{max(1, h * 0.008):.1f}" opacity="0.8"/>']
    for dx, dy in ((-0.35, -0.02), (0.3, 0.0), (-0.12, -0.06), (0.15, -0.05)):
        out.append(f'<path d="M {tx:.1f} {ty + h * 0.09:.1f} Q {tx + dx * spread * 0.4:.1f} {ty + h * 0.04:.1f} {tx + dx * spread:.1f} {ty + dy * h:.1f}" fill="none" stroke="{trunk}" stroke-width="{max(1, h * 0.012):.1f}" stroke-linecap="round"/>')
    clumps = []
    for _ in range(int(spread / 2.2)):
        cx_ = tx + rnd.uniform(-0.5, 0.5) * spread
        t = abs(cx_ - tx) / (spread / 2)
        cy_ = ty - rnd.uniform(0, 1) * h * 0.1 * (1 - t ** 2) + t * h * 0.02
        clumps.append((cx_, cy_, rnd.uniform(0.05, 0.1) * spread))
    out.append(f'<g fill="{mid}">' + "".join(f'<ellipse cx="{a:.1f}" cy="{b:.1f}" rx="{r * 1.3:.1f}" ry="{r * 0.8:.1f}"/>' for a, b, r in clumps) + "</g>")
    out.append(f'<g fill="{dark}" opacity="0.8">' + "".join(f'<ellipse cx="{a + r * 0.2:.1f}" cy="{b + r * 0.35:.1f}" rx="{r * 1.1:.1f}" ry="{r * 0.5:.1f}"/>' for a, b, r in clumps) + "</g>")
    out.append(f'<g fill="{lit}" opacity="0.85">' + "".join(f'<ellipse cx="{a - r * 0.3:.1f}" cy="{b - r * 0.35:.1f}" rx="{r * 0.8:.1f}" ry="{r * 0.4:.1f}"/>' for a, b, r in clumps if a < tx + spread * 0.25) + "</g>")
    out.append(f'<g fill="{gold}" opacity="0.7">' + "".join(f'<ellipse cx="{a - r * 0.5:.1f}" cy="{b - r * 0.5:.1f}" rx="{r * 0.35:.1f}" ry="{r * 0.18:.1f}"/>' for a, b, r in clumps if a < tx) + "</g>")
    return "".join(out)


def vespa(x, base, k, body="#8ED0C0", shade="#4E9A8E", rim="#FFE2A8"):
    """Classic scooter in profile facing left (generic, no badges); (x, base) = rear wheel contact point."""
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({k:.3f})">',
         '<ellipse cx="-40" cy="2" rx="70" ry="5" fill="#3A2A2A" opacity="0.35"/>']
    for wx in (0, -78):
        g.append(f'<circle cx="{wx}" cy="-13" r="13" fill="#1E1A1E"/><circle cx="{wx}" cy="-13" r="8" fill="#E8E0D0"/><circle cx="{wx}" cy="-13" r="5" fill="#B8B0A8"/><circle cx="{wx}" cy="-13" r="2" fill="#5A5050"/>')
    # rear cowl and floorboard
    g.append(f'<path d="M -46 -16 L -20 -16 Q -14 -46 8 -50 Q 26 -50 26 -30 Q 26 -16 12 -14 L -6 -14 Q -10 -24 -22 -24 L -46 -24 Z" fill="{body}"/>')
    g.append(f'<path d="M 8 -50 Q 26 -50 26 -30 Q 26 -16 12 -14 L 4 -14 Q 18 -24 16 -38 Q 14 -48 8 -50 Z" fill="{shade}"/>')
    g.append('<path d="M -46 -16 L -6 -16 L -6 -12 L -46 -12 Z" fill="#2A2A2E"/>')
    # front shield and fork
    g.append(f'<path d="M -46 -24 L -46 -16 L -62 -16 Q -70 -40 -66 -66 L -58 -68 Q -58 -42 -46 -24 Z" fill="{body}"/>')
    g.append(f'<path d="M -66 -66 Q -70 -40 -62 -16" fill="none" stroke="{rim}" stroke-width="2.2" stroke-linecap="round"/>')
    g.append(f'<path d="M -86 -26 Q -84 -40 -72 -40 Q -64 -40 -64 -28 L -72 -24 Z" fill="{body}"/><path d="M -86 -26 Q -84 -40 -72 -40" fill="none" stroke="{rim}" stroke-width="2"/>')
    g.append('<path d="M -64 -66 L -74 -20" stroke="#5A5A62" stroke-width="3"/>')
    # handlebar, headlight, mirror
    g.append(f'<path d="M -70 -70 L -54 -70 L -52 -76 L -66 -78 Z" fill="{body}"/><circle cx="-70" cy="-72" r="5" fill="#F8F0D8" stroke="#C8C0B0" stroke-width="1.5"/>'
             '<path d="M -56 -76 L -46 -80" stroke="#2A2A2E" stroke-width="3" stroke-linecap="round"/><path d="M -60 -78 L -58 -92" stroke="#B8B8C0" stroke-width="1.4"/><circle cx="-58" cy="-93" r="3" fill="#D8D8E0"/>')
    # seat, rear rack, tail light
    g.append('<path d="M -18 -52 Q -12 -60 10 -58 Q 22 -56 22 -50 L -16 -48 Z" fill="#E8D8B8"/><path d="M -18 -52 Q -12 -60 10 -58" fill="none" stroke="#FFF2D8" stroke-width="1.5"/>')
    g.append('<path d="M 12 -56 L 30 -56 L 30 -52 L 12 -52" fill="none" stroke="#B8B8C0" stroke-width="2"/><rect x="24" y="-40" width="4" height="6" rx="1" fill="#C83A3A"/>')
    g.append('<path d="M -30 -12 L -36 0" stroke="#5A5A62" stroke-width="2.2"/>')
    g.append(f'<path d="M -20 -16 Q -14 -46 8 -50" fill="none" stroke="{rim}" stroke-width="2" opacity="0.9"/>')
    g.append("</g>")
    return "".join(g)


def rome():
    u = "ro"
    cx, base, a, b = 300, 336, 228, 34
    out = [defs(
        lg(f"{u}-sky", [(0, "#5C6CA6"), (0.3, "#9C8EB6"), (0.55, "#E8AE96"), (0.72, "#F6CA96"), (0.8, "#FADBA8")], 0, 0, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-ground", [(0, "#C9A27E"), (1, "#7E5A4A")], 0, 300, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(-20, 260, 360, "#FFD69A", f"{u}-sun", 0.85))
    for x, y, w, c in ((420, 126, 110, "#F2B8A8"), (500, 146, 70, "#F8C8A8"), (150, 150, 80, "#FFD8B0"), (360, 186, 60, "#FFDDB4")):
        out.append(streak_cloud(x, y, w, c, 0.65, 4))
    # starling murmuration over the city
    rnd = random.Random(17)
    mm = []
    for i in range(260):
        t = rnd.uniform(0, 2 * math.pi)
        r_ = rnd.gauss(1, 0.18)
        x = 470 + 52 * r_ * math.cos(t) + 26 * math.sin(2 * t)
        y = 112 + 22 * r_ * math.sin(t) * (0.6 + 0.4 * math.cos(t))
        mm.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.7, 1.4):.1f}"/>')
    out.append(f'<g fill="#3A2E46" opacity="0.75">{"".join(mm)}</g>')
    # distant city and the Palatine pines in the haze
    rnd = random.Random(3)
    x = -10
    while x < 610:
        w = rnd.uniform(14, 34)
        h = rnd.uniform(8, 22)
        out.append(f'<rect x="{x:.1f}" y="{300 - h:.1f}" width="{w + 1:.1f}" height="{h + 10:.1f}" fill="{rnd.choice(["#C8A0A0", "#C29AA0", "#D0A8A0"])}"/>')
        x += w
    out.append('<g fill="#C29AA0"><rect x="120" y="262" width="8" height="30"/><path d="M 116 262 L 132 262 L 124 250 Z"/></g>')
    for k_, (px, ph, sp) in enumerate(((560, 70, 70), (520, 58, 56), (40, 60, 60), (590, 84, 64))):
        out.append(umbrella_pine(px, 304, ph, sp, 90 + k_, dark="#6E6A6E", mid="#7E7A78", lit="#B8A890", gold="#E8C8A0", trunk="#8E7A78", trunk_lit="#E8C0A0"))
    out.append(f'<rect x="0" y="250" width="600" height="60" fill="#F6D2A8" opacity="0.3"/>')

    # piazza: travertine paving and sampietrini in perspective
    out.append(Q([(-10, 300), (610, 300), (610, 444), (-10, 444)], f"url(#{u}-ground)"))
    for j in range(16):
        y = base + b + 4 + (j ** 1.55) * 1.7
        if y > 444:
            break
        sw = 0.8 + j * 0.12
        out.append(f'<path d="M -10 {y:.1f} Q 300 {y + 6 + j:.1f} 610 {y:.1f}" fill="none" stroke="#5E4038" stroke-width="{sw:.1f}" opacity="0.35"/>')
        n = 14 + j * 2
        out.append(f'<g stroke="#5E4038" stroke-width="{sw * 0.8:.1f}" opacity="0.25">' + "".join(
            f'<line x1="{-10 + (i + (j % 2) * 0.5) * 620 / n:.1f}" y1="{y:.1f}" x2="{-10 + (i + (j % 2) * 0.5) * 620 / n:.1f}" y2="{y + 3 + j * 0.9:.1f}"/>' for i in range(n + 1)) + "</g>")
    # --- the amphitheatre
    lev = [0, 56, 108, 158, 202]  # heights of storey boundaries (px)
    nb = 40
    sun_t = -0.9
    lit_c, mid_c, shd_c = "#F6CE8E", "#E2A872", "#9E6A5E"

    def X(t, aa=a):
        return cx + aa * math.sin(t)

    def G(t, bb=b):
        return base + bb * math.cos(t)

    def top_h(t):
        d = math.degrees(t)
        if d <= 14:
            return lev[4]
        if d <= 42:
            return lev[4] - (d - 14) / 28 * (lev[4] - lev[2]) + 7 * math.sin(d * 1.7) * math.sin(d * 0.53 + 1)
        return lev[2] + 3 * math.sin(d * 2.3) * math.sin(d * 0.7)

    # interior seen through the collapsed outer ring: far inner face of brick arcades, then the inner ring
    far = []
    for i in range(0, 46):
        t = math.radians(-6 + i * 2.1)
        far.append((X(t, a * 0.93), base - b * 0.93 * math.cos(t) - 136))
    far = rough(far[::3], 44, amp=9, depth=3)
    far_poly = far + [(X(math.radians(90), a * 0.93), base), (X(math.radians(-6), a * 0.93), base)]
    out.append(Q(far_poly, "#B8705A"))
    out.append(f'<clipPath id="{u}-fc"><polygon points="{P(far_poly)}"/></clipPath>')
    for row, hh in enumerate((24, 58, 92)):
        for i in range(2, 44, 2):
            t = math.radians(-6 + i * 2.1)
            xx = X(t, a * 0.93)
            yy = base - b * 0.93 * math.cos(t) - hh - 22
            w = 5.5 * math.cos(t) + 1.5
            out.append(f'<path d="M {xx - w / 2:.1f} {yy + 20:.1f} L {xx - w / 2:.1f} {yy + w / 2:.1f} Q {xx:.1f} {yy - w * 0.2:.1f} {xx + w / 2:.1f} {yy + w / 2:.1f} L {xx + w / 2:.1f} {yy + 20:.1f} Z" fill="#6E3A3A"/>')
    out.append(f'<g clip-path="url(#{u}-fc)">' + streaks(50, 13, (cx, base - 190, cx + a, base - 20), ["#8E4A42", "#D8946E"], w=(1, 3), length=(8, 30), opacity=(0.3, 0.6))
               + f'<polyline points="{P(far)}" fill="none" stroke="#F2B488" stroke-width="2" opacity="0.7"/></g>')
    inner = []
    for i in range(0, 46):
        t = math.radians(4 + i * 1.9)
        inner.append((X(t, a * 0.86), G(t, b * 0.86) - 158 + (i / 45) * 12))
    inner = rough(inner[::3], 45, amp=7, depth=3)
    out.append(Q(inner + [(X(math.radians(91), a * 0.86), base + 10), (X(math.radians(4), a * 0.86), base + 10)], "#C88A66"))
    for row, (h0, h1) in enumerate(((58, 100), (108, 140))):
        for i in range(0, 44, 2):
            t = math.radians(6 + i * 1.95)
            xx = X(t, a * 0.86)
            gy = G(t, b * 0.86)
            if gy - h1 < (y_on(inner, xx) or 0) + 4:
                continue
            w = 9 * math.cos(t) + 1.5
            out.append(f'<path d="M {xx - w / 2:.1f} {gy - h0:.1f} L {xx - w / 2:.1f} {gy - h1 + w / 2:.1f} Q {xx:.1f} {gy - h1 - w * 0.2:.1f} {xx + w / 2:.1f} {gy - h1 + w / 2:.1f} L {xx + w / 2:.1f} {gy - h0:.1f} Z" fill="#7A4440"/>')

    # outer ring: one facet per bay, lit by the low sun from the left
    for i in range(nb):
        t0 = math.radians(-90 + 180 * i / nb)
        t1 = math.radians(-90 + 180 * (i + 1) / nb)
        tm = (t0 + t1) / 2
        L = max(0, math.cos(tm - sun_t))
        col = mix(shd_c, lit_c, L ** 1.3) if L > 0.5 else mix(shd_c, mid_c, L * 2)
        h0, h1 = top_h(t0), top_h(t1)
        out.append(Q([(X(t0), G(t0) + 1), (X(t0), G(t0) - h0), (X(t1), G(t1) - h1), (X(t1), G(t1) + 1)], col))
    # arches per storey
    for k in range(3):
        for i in range(nb):
            tm = math.radians(-90 + 180 * (i + 0.5) / nb)
            if lev[k + 1] > top_h(tm) - 4:
                continue
            hw = math.radians(180 / nb) * 0.31
            xl, xr = X(tm - hw), X(tm + hw)
            if xr - xl < 1.2:
                continue
            gy = G(tm)
            yb = gy - lev[k] - 6
            ys = gy - lev[k] - (lev[k + 1] - lev[k]) * 0.58
            w = xr - xl
            L = max(0, math.cos(tm - sun_t))
            through = (k == 2 and (i % 3 == 1 or math.degrees(tm) > 0)) or (k == 1 and math.degrees(tm) > 26)
            inside = "#F2C6A0" if through else mix("#3E2230", "#7A4A44", L)
            out.append(f'<path d="M {xl:.1f} {yb:.1f} L {xl:.1f} {ys:.1f} Q {xl:.1f} {ys - w * 0.62:.1f} {(xl + xr) / 2:.1f} {ys - w * 0.62:.1f} Q {xr:.1f} {ys - w * 0.62:.1f} {xr:.1f} {ys:.1f} L {xr:.1f} {yb:.1f} Z" fill="{inside}"/>')
            if not through:
                # the sunlit inner reveal on the right side of each opening
                rw = max(0.8, w * 0.22)
                out.append(f'<path d="M {xr - rw:.1f} {yb:.1f} L {xr - rw:.1f} {ys:.1f} Q {xr - rw:.1f} {ys - w * 0.5:.1f} {(xl + xr) / 2:.1f} {ys - w * 0.6:.1f} Q {xr:.1f} {ys - w * 0.62:.1f} {xr:.1f} {ys:.1f} L {xr:.1f} {yb:.1f} Z" fill="{mix("#C8865E", "#F8D29A", L)}" opacity="0.85"/>')
            else:
                out.append(f'<rect x="{xl:.1f}" y="{ys + (yb - ys) * 0.55:.1f}" width="{w:.1f}" height="{(yb - ys) * 0.45:.1f}" fill="#B8786A"/>')
            # engaged half-column on the pier to the left
            xc = X(tm - math.radians(180 / nb) * 0.5)
            cw = max(0.8, 2.2 * math.cos(tm))
            out.append(f'<rect x="{xc - cw / 2:.1f}" y="{gy - lev[k + 1] + 4:.1f}" width="{cw:.1f}" height="{lev[k + 1] - lev[k] - 4:.1f}" fill="{mix(mid_c, "#FFE6B8", L * 0.8)}" opacity="0.7"/>')
            out.append(f'<rect x="{xc + cw / 2:.1f}" y="{gy - lev[k + 1] + 4:.1f}" width="{cw * 0.6:.1f}" height="{lev[k + 1] - lev[k] - 4:.1f}" fill="#6E4040" opacity="0.35"/>')
    # attic: small square windows on alternate bays, corbels under the crown
    for i in range(nb):
        tm = math.radians(-90 + 180 * (i + 0.5) / nb)
        if top_h(tm) < lev[4] - 2 or i % 2:
            continue
        w = 6 * math.cos(tm)
        if w < 1:
            continue
        gy = G(tm)
        out.append(f'<rect x="{X(tm) - w / 2:.1f}" y="{gy - lev[3] - 26:.1f}" width="{w:.1f}" height="9" fill="#4A2A34"/>')
    # cornices along the ellipse (lit top edge, shadow below)
    for k in (1, 2, 3):
        pts_l, pts_d = [], []
        for i in range(91):
            t = math.radians(-90 + i * 2)
            if lev[k] > top_h(t) - 1:
                break
            pts_l.append((X(t), G(t) - lev[k]))
            pts_d.append((X(t), G(t) - lev[k] + 3))
        if len(pts_l) > 1:
            out.append(f'<polyline points="{P(pts_d)}" fill="none" stroke="#6E3E3E" stroke-width="2" opacity="0.5"/>')
            out.append(f'<polyline points="{P(pts_l)}" fill="none" stroke="#FFE2B0" stroke-width="2.6" opacity="0.85"/>')
    crown = [(X(math.radians(-90 + i * 2)), G(math.radians(-90 + i * 2)) - top_h(math.radians(-90 + i * 2))) for i in range(91)]
    out.append(f'<polyline points="{P(crown)}" fill="none" stroke="#FFE8BC" stroke-width="2" opacity="0.8" stroke-linejoin="round"/>')
    out.append(f'<g fill="#7A4A44" opacity="0.6">' + "".join(
        f'<rect x="{X(math.radians(-90 + i * 2)) - 0.8:.1f}" y="{G(math.radians(-90 + i * 2)) - lev[4] + 8:.1f}" width="1.6" height="4"/>' for i in range(0, 52))
        + "</g>")
    # the sloping brick buttress where the outer ring breaks
    tb = math.radians(42)
    bx, bgy = X(tb), G(tb)
    out.append(Q([(bx - 2, bgy), (bx - 2, bgy - lev[2] - 8), (bx + 12, bgy - lev[2] + 14), (bx + 18, bgy)], "#B8664E"))
    out.append(Q([(bx + 8, bgy), (bx + 8, bgy - lev[2] + 8), (bx + 12, bgy - lev[2] + 14), (bx + 18, bgy)], "#8A4A42"))
    out.append(f'<g stroke="#8A4A42" stroke-width="0.8" opacity="0.6">' + "".join(f'<line x1="{bx - 2:.1f}" y1="{bgy - j * 6:.1f}" x2="{bx + 16:.1f}" y2="{bgy - j * 6:.1f}"/>' for j in range(1, 18)) + "</g>")
    # weathering streaks clipped to the ring
    ring = [(X(math.radians(-90 + i * 2)), G(math.radians(-90 + i * 2))) for i in range(91)]
    out.append(f'<clipPath id="{u}-rc"><polygon points="{P(crown + ring[::-1])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-rc)">' + streaks(110, 19, (cx - a, base - 210, cx + a, base + b), ["#8E5A4E", "#5E3A3A", "#FFE6B8"], w=(1, 2.4), length=(8, 36), opacity=(0.08, 0.22), slant=0.05)
               + f'<polygon points="{P([(cx - a, base + b), (cx + a, base + b), (cx + a, base - 24), (cx - a, base - 24)])}" fill="#5E3A40" opacity="0.18"/></g>')

    out.append(Q([(0, 380), (600, 360), (600, 444), (0, 444)], "#FFD8A0", ' opacity="0.08"'))
    # long evening shadows of the pines across the square
    out.append(Q([(60, 432), (360, 418), (380, 426), (70, 444)], "#4A2E3A", ' opacity="0.25"'))
    # visitors, a lamp post
    for px, py, h, c in ((214, 384, 26, "#3E5A7A"), (226, 386, 24, "#C9574A"), (330, 378, 22, "#E0B04A"), (346, 380, 23, "#4A3A5A"), (150, 394, 30, "#6A8A5A"), (414, 374, 21, "#B85A8A")):
        out.append(figure(px, py, h, c, rim="#FFD8A0", rim_side=-1))
    lx = 104
    out.append(f'<rect x="{lx - 2}" y="300" width="4" height="96" fill="#2A2228"/><rect x="{lx - 4}" y="390" width="8" height="8" fill="#2A2228"/>'
               f'<path d="M {lx - 8} 300 L {lx + 8} 300 L {lx + 5} 284 L {lx - 5} 284 Z" fill="#F8E2B0" stroke="#2A2228" stroke-width="2"/><path d="M {lx - 9} 284 L {lx} 276 L {lx + 9} 284 Z" fill="#2A2228"/>')
    # the big umbrella pine framing the left, the scooter on the right
    out.append(umbrella_pine(20, 444, 345, 250, 7, lean=0.1))
    out.append(vespa(520, 432, 1.05))
    out.append(gulls([(250, 76, 10), (276, 88, 7)], "#3A2E46", 1.8))
    return "\n".join(out)


# ================================================================ LONDON — Westminster from the river at blue hour
def clock_tower(cx, base, top, w, u):
    """The Elizabeth Tower, floodlit gold against the dusk, clock faces glowing."""
    H = base - top
    y1, y2, y3, y4 = base - 0.54 * H, base - 0.665 * H, base - 0.745 * H, base - 0.925 * H
    out = [defs(lg(f"{u}-tg", [(0, "#FFE4A0"), (0.45, "#E8B860"), (1, "#8A6040")], 0, 0, 1, 0),
                lg(f"{u}-tr", [(0, "#4A5A7A"), (0.5, "#2E3A5A"), (1, "#1E263E")], 0, 0, 1, 0))]
    out.append(glow(cx, (y1 + y2) / 2, w * 1.6, "#FFE8B0", f"{u}-cg", 0.5))
    # shaft
    out.append(f'<rect x="{cx - w / 2:.1f}" y="{y1:.1f}" width="{w:.1f}" height="{base - y1:.1f}" fill="url(#{u}-tg)"/>')
    out.append(f'<g stroke="#8A6040" stroke-width="0.9" opacity="0.6">' + "".join(
        f'<line x1="{cx + d * w:.1f}" y1="{y1:.1f}" x2="{cx + d * w:.1f}" y2="{base:.1f}"/>' for d in (-0.3, -0.1, 0.1, 0.3)) + "</g>")
    for j in range(9):
        yy = y1 + 6 + j * (base - y1 - 10) / 9
        out.append(f'<rect x="{cx - w / 2:.1f}" y="{yy:.1f}" width="{w:.1f}" height="1.2" fill="#FFF0C8" opacity="0.55"/>')
        for d in (-0.2, 0, 0.2):
            out.append(f'<rect x="{cx + d * w - 1.2:.1f}" y="{yy + 2:.1f}" width="2.4" height="5" fill="{"#FFF2C0" if (j + int(d * 10)) % 3 else "#6A4A3A"}" opacity="0.8"/>')
    # clock stage with its gilded frame and glowing dial
    cw = w * 1.12
    out.append(f'<rect x="{cx - cw / 2:.1f}" y="{y2:.1f}" width="{cw:.1f}" height="{y1 - y2:.1f}" fill="url(#{u}-tg)"/>')
    r = min(cw * 0.4, (y1 - y2) * 0.42)
    ccy = (y1 + y2) / 2
    out.append(f'<rect x="{cx - r * 1.15:.1f}" y="{ccy - r * 1.15:.1f}" width="{r * 2.3:.1f}" height="{r * 2.3:.1f}" fill="#C89A48"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{ccy:.1f}" r="{r * 1.05:.1f}" fill="#5A3E2A"/><circle cx="{cx:.1f}" cy="{ccy:.1f}" r="{r * 0.95:.1f}" fill="#FFF6DC"/>')
    out.append(f'<g stroke="#3A2A22" stroke-width="1" stroke-linecap="round">' + "".join(
        f'<line x1="{cx + r * 0.78 * math.cos(math.radians(i * 30)):.1f}" y1="{ccy + r * 0.78 * math.sin(math.radians(i * 30)):.1f}" x2="{cx + r * 0.92 * math.cos(math.radians(i * 30)):.1f}" y2="{ccy + r * 0.92 * math.sin(math.radians(i * 30)):.1f}"/>' for i in range(12)) + "</g>")
    out.append(f'<line x1="{cx:.1f}" y1="{ccy:.1f}" x2="{cx - r * 0.45:.1f}" y2="{ccy + r * 0.15:.1f}" stroke="#2A1E1A" stroke-width="1.8" stroke-linecap="round"/>'
               f'<line x1="{cx:.1f}" y1="{ccy:.1f}" x2="{cx:.1f}" y2="{ccy - r * 0.75:.1f}" stroke="#2A1E1A" stroke-width="1.3" stroke-linecap="round"/>')
    out.append(f'<path d="M {cx - cw / 2:.1f} {y2:.1f} L {cx:.1f} {y2 - (y2 - y3) * 0.6:.1f} L {cx + cw / 2:.1f} {y2:.1f} Z" fill="#E8B860"/>')
    # belfry
    out.append(f'<rect x="{cx - w * 0.5:.1f}" y="{y3:.1f}" width="{w:.1f}" height="{y2 - y3:.1f}" fill="url(#{u}-tg)"/>')
    for d in (-0.28, 0, 0.28):
        out.append(f'<path d="M {cx + d * w - w * 0.08:.1f} {y2 - 1:.1f} L {cx + d * w - w * 0.08:.1f} {y3 + 4:.1f} L {cx + d * w:.1f} {y3 + 1.5:.1f} L {cx + d * w + w * 0.08:.1f} {y3 + 4:.1f} L {cx + d * w + w * 0.08:.1f} {y2 - 1:.1f} Z" fill="#5A3E3A"/>')
    out.append(f'<rect x="{cx - w * 0.56:.1f}" y="{y3 - 1.5:.1f}" width="{w * 1.12:.1f}" height="3" fill="#FFE8B0"/>')
    # steep iron roof with lucarnes, corner pinnacles, then the spire
    out.append(f'<path d="M {cx - w * 0.5:.1f} {y3:.1f} Q {cx - w * 0.3:.1f} {(y3 + y4) / 2:.1f} {cx - w * 0.1:.1f} {y4:.1f} L {cx + w * 0.1:.1f} {y4:.1f} Q {cx + w * 0.3:.1f} {(y3 + y4) / 2:.1f} {cx + w * 0.5:.1f} {y3:.1f} Z" fill="url(#{u}-tr)"/>')
    out.append(f'<path d="M {cx - w * 0.5:.1f} {y3:.1f} Q {cx - w * 0.3:.1f} {(y3 + y4) / 2:.1f} {cx - w * 0.1:.1f} {y4:.1f}" fill="none" stroke="#E8C070" stroke-width="1.2"/>')
    for t, sc in ((0.3, 1.0), (0.62, 0.7)):
        yy = y3 - (y3 - y4) * t
        hw = w * (0.5 - 0.4 * t) * 0.6
        out.append(f'<path d="M {cx - hw:.1f} {yy + 5 * sc:.1f} L {cx - hw:.1f} {yy:.1f} L {cx:.1f} {yy - 5 * sc:.1f} L {cx + hw:.1f} {yy:.1f} L {cx + hw:.1f} {yy + 5 * sc:.1f} Z" fill="#C89A48"/><rect x="{cx - hw * 0.4:.1f}" y="{yy:.1f}" width="{hw * 0.8:.1f}" height="{4 * sc:.1f}" fill="#FFE8A8"/>')
    for d in (-0.5, 0.5):
        out.append(f'<path d="M {cx + d * w - 2:.1f} {y3:.1f} L {cx + d * w:.1f} {y3 - 12:.1f} L {cx + d * w + 2:.1f} {y3:.1f} Z" fill="#E8B860"/>')
    out.append(f'<path d="M {cx - w * 0.1:.1f} {y4:.1f} L {cx - 1.4:.1f} {top + 4:.1f} L {cx + 1.4:.1f} {top + 4:.1f} L {cx + w * 0.1:.1f} {y4:.1f} Z" fill="#C89A48"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{top + 3:.1f}" r="1.8" fill="#FFE8A8"/><line x1="{cx:.1f}" y1="{top + 2:.1f}" x2="{cx:.1f}" y2="{top - 2:.1f}" stroke="#FFE8A8" stroke-width="1.2"/>')
    out.append(f'<rect x="{cx + w * 0.22:.1f}" y="{y1:.1f}" width="{w * 0.28:.1f}" height="{base - y1:.1f}" fill="#4A3048" opacity="0.25"/>')
    return "".join(out)


def london():
    u = "ld"
    C = Cam(f=640, cx=300, vpy=292, eye=9)
    out = [defs(
        lg(f"{u}-sky", [(0, "#141C44"), (0.3, "#24306A"), (0.55, "#47508E"), (0.7, "#8A6E9E"), (0.8, "#D88E86"), (0.86, "#F2B48A")], 0, 0, 0, 340, units="userSpaceOnUse"),
        lg(f"{u}-river", [(0, "#6A5E8E"), (0.15, "#2E386C"), (1, "#0E1630")], 0, 300, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-pal", [(0, "#F2C878"), (1, "#B8803E")], 0, 236, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-brg", [(0, "#2E5A52"), (1, "#1A3A36")], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(70, 3, (0, 40, 600, 170), "#F6F0E0", r=(0.6, 1.4), opacity=(0.4, 1)))
    out.append(glow(492, 110, 46, "#FFF4D8", f"{u}-moon", 0.35))
    out.append('<path d="M 496 97 A 13 13 0 1 0 496 123 A 16 16 0 0 1 496 97 Z" fill="#FFF4D8"/>')
    out.append(glow(160, 292, 300, "#F6A880", f"{u}-dusk", 0.45))
    for x, y, w_, c in ((120, 210, 120, "#C88AA0"), (60, 228, 80, "#E8A090"), (420, 200, 100, "#9A7AA6"), (520, 222, 70, "#B88AA0")):
        out.append(streak_cloud(x, y, w_, c, 0.5, 3.5))
    # far city to the right, lights twinkling
    rnd = random.Random(7)
    x = 300
    while x < 610:
        w_ = rnd.uniform(10, 26)
        h = rnd.uniform(10, 40)
        out.append(f'<rect x="{x:.1f}" y="{292 - h:.1f}" width="{w_ + 0.5:.1f}" height="{h + 4:.1f}" fill="{rnd.choice(["#3A3E6A", "#343862", "#40446E"])}"/>')
        out.append(dots(int(h / 4), int(x), (x + 2, 292 - h + 3, x + w_ - 2, 292), "#FFD98E", r=(0.6, 1.1), opacity=(0.5, 1)))
        x += w_
    out.append(f'<rect x="0" y="300" width="600" height="144" fill="url(#{u}-river)"/>')
    # Palace of Westminster along the far bank, floodlit
    Z = 300
    out.append(Q([C(-300, 4, Z), C(-300, 28, Z), C(-37, 28, Z), C(-37, 4, Z)], f"url(#{u}-pal)"))
    out.append(Q([C(-300, 28, Z), C(-300, 33, Z + 15), C(-37, 33, Z + 15), C(-37, 28, Z)], "#3A3E5E"))
    rnd = random.Random(12)
    for X in [-40 - 5.2 * i for i in range(52)]:
        xa, ya = C(X, 28, Z)
        xb, yb = C(X, 4, Z)
        tall = rnd.random() < 0.18
        out.append(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" stroke="#FFF0C8" stroke-width="1.2" opacity="0.7"/>')
        top_ = 33 if not tall else 38
        xt, yt = C(X, top_, Z)
        out.append(f'<path d="M {xa - 1.4:.1f} {ya:.1f} L {xt:.1f} {yt:.1f} L {xa + 1.4:.1f} {ya:.1f} Z" fill="#E8B860"/>')
        for row, (y0, y1) in enumerate(((7, 11), (14, 18), (21, 25))):
            on = rnd.random() < 0.7
            q = C.quad_z(Z, X - 4.2, X - 1.2, y0, y1)
            out.append(Q(q, "#FFF0B8" if on else "#7A5A3A", ' opacity="0.9"'))
    for X, h in ((-70, 44), (-122, 40), (-175, 52)):
        q = C.quad_z(Z + 4, X - 8, X + 8, 26, h)
        out.append(Q(q, f"url(#{u}-pal)"))
        xt, yt = C(X, h + 9, Z + 4)
        out.append(Q([q[1], (xt, yt), q[2]], "#3A3E5E"))
        out.append(Q(C.quad_z(Z + 4, X - 5, X - 2, h - 10, h - 3), "#FFF0B8"))
        out.append(Q(C.quad_z(Z + 4, X + 2, X + 5, h - 10, h - 3), "#FFF0B8"))
    out.append(Q([C(-300, 0, Z), C(-300, 4, Z), C(-30, 4, Z), C(-30, 0, Z)], "#C8A070"))
    # buildings north of the bridge: modern block with tall bronze chimneys, then the banded turreted block
    out.append(Q(C.quad_z(Z + 6, -2, 30, 0, 26), "#4A3E44"))
    for X in range(0, 30, 4):
        out.append(Q(C.quad_z(Z + 6, X, X + 1.6, 26, 36), "#5A4A44"))
    for j in range(6):
        for X in range(-1, 29, 3):
            out.append(Q(C.quad_z(Z + 6, X + 0.4, X + 2.2, 3 + j * 3.6, 5.6 + j * 3.6), "#FFD98E" if (X + j) % 4 else "#6E5A5E"))
    out.append(Q(C.quad_z(Z + 10, 32, 72, 0, 24), "#A85A4E"))
    for j in range(7):
        out.append(Q(C.quad_z(Z + 10, 32, 72, 2 + j * 3.2, 2.8 + j * 3.2), "#E8DCC8", ' opacity="0.8"'))
    for X in (34, 70):
        q = C.quad_z(Z + 10, X - 3, X + 3, 0, 30)
        out.append(Q(q, "#B8645A"))
        xt, yt = C(X, 37, Z + 10)
        out.append(Q([q[1], (xt, yt), q[2]], "#3A3E5E"))
    for j in range(5):
        for X in range(36, 68, 4):
            out.append(Q(C.quad_z(Z + 10, X, X + 1.6, 3.6 + j * 4, 5.8 + j * 4), "#FFD98E" if (X + j) % 3 else "#4A2E3A"))
    # embankment trees and lamps
    for k_, X in enumerate(range(78, 220, 14)):
        x_, b_ = C(X, 4, Z - 6)
        out.append(leaf_canopy(f"{u}-et{k_}", x_, b_ - 14, 12, 9, 300 + k_, "#141A2A", "#22283A", "#3A4258", light=(-1, -1), n=24))
    for X in range(76, 230, 10):
        x_, y_ = C(X, 7, Z - 8)
        out.append(glow(x_, y_, 6, "#FFE2A0", f"{u}-el{X}", 0.9))
    out.append(Q([C(-30, 0, Z - 6), C(-30, 4, Z - 6), C(260, 4, Z - 6), C(260, 0, Z - 6)], "#3A3A5A"))
    # the clock tower at the corner of the palace
    tx, tb = C(-31, 4, Z)
    _, tt = C(-31, 100, Z)
    out.append(clock_tower(tx, tb, tt, 31, u))
    # reflections of the floodlit facades
    rnd = random.Random(21)
    for i in range(130):
        y = 301 + rnd.random() ** 1.4 * 110
        k = (y - 300) / 110
        if rnd.random() < 0.65:
            x0, x1 = 0, tx + 12
            xx = rnd.uniform(x0, x1)
            col = rnd.choice(["#F2C878", "#FFE2A0", "#E8A860"])
        else:
            xx = rnd.uniform(300, 600)
            col = rnd.choice(["#FFD98E", "#F2B868"])
        w_ = rnd.uniform(6, 30) * (1 - 0.4 * k)
        out.append(f'<rect x="{xx - w_ / 2:.1f}" y="{y:.1f}" width="{w_:.1f}" height="{1 + k * 1.5:.1f}" rx="1" fill="{col}" opacity="{(1 - k) * rnd.uniform(0.4, 0.9):.2f}"/>')
    # the tower's long golden reflection
    for i in range(40):
        y = 300 + i * 3.2
        w_ = 22 * (1 - i / 50) * rnd.uniform(0.5, 1.2)
        out.append(f'<rect x="{tx - w_ / 2 + rnd.uniform(-3, 3):.1f}" y="{y:.1f}" width="{w_:.1f}" height="1.6" rx="0.8" fill="#FFE2A0" opacity="{0.8 * (1 - i / 42):.2f}"/>')
    out.append(water_lines(120, 22, (0, 300, 600, 444), ["#5A6AA0", "#2A3A70", "#8A8ABA"], w=(8, 50), h=(0.8, 2), opacity=(0.25, 0.6)))

    # Westminster Bridge sweeping from the near bank to the tower's foot
    XR, XL = -12, -36
    piers = [24, 50, 80, 112, 146, 182, 220, 258, 296]
    # water-level shadow and the bridge face
    out.append(Q([C(XR, 9.6, 20), C(XR, 9.6, 296), C(XR, 0, 296), C(XR, 0, 20)], f"url(#{u}-brg)"))
    for z0, z1 in zip(piers, piers[1:]):
        pts = []
        for j in range(17):
            t = j / 16
            Zp = lerp(z0 + 2.5, z1 - 2.5, t)
            pts.append(C(XR, 6.6 * math.sin(math.pi * t) ** 0.45, Zp))
        out.append(Q(pts, "#0E1A2A"))
        # light through the arch: the lit far bank seen underneath
        inner = [(x_, y_ + (C(XR, 0, z0)[1] - y_) * 0.5) for x_, y_ in pts]
        out.append(Q(pts[2:-2], "#F2C878", ' opacity="0.18"'))
        out.append(f'<polyline points="{P(pts)}" fill="none" stroke="#E8C070" stroke-width="{max(0.8, 640 * 0.25 / z0):.1f}" opacity="0.8"/>')
        # cutwater / pier face
        out.append(Q(C.quad_x(XR + 0.2, z1 - 2.5, z1 + 2.5, 0, 7.5), "#3A4A4A"))
    # deck fascia with gilded trim, parapet
    out.append(Q([C(XR, 7.6, 20), C(XR, 9.0, 20), C(XR, 9.0, 296), C(XR, 7.6, 296)], "#24504A"))
    out.append(f'<polyline points="{P([C(XR, 8.3, 20), C(XR, 8.3, 296)])}" fill="none" stroke="#E8C070" stroke-width="1.4" opacity="0.8"/>')
    out.append(Q([C(XR, 9.0, 20), C(XR, 10.1, 20), C(XR, 10.1, 296), C(XR, 9.0, 296)], "#2E5E56"))
    out.append(f'<g stroke="#4E8A7E" stroke-width="1">' + "".join(
        f'<line x1="{C(XR, 9.05, z)[0]:.1f}" y1="{C(XR, 9.05, z)[1]:.1f}" x2="{C(XR, 10.05, z)[0]:.1f}" y2="{C(XR, 10.05, z)[1]:.1f}"/>' for z in [21 + 1.4 * i * (1 + i / 30) for i in range(70)] if z < 296) + "</g>")
    out.append(f'<polyline points="{P([C(XR, 10.1, 20), C(XR, 10.1, 296)])}" fill="none" stroke="#FFE2A8" stroke-width="1.2" opacity="0.8"/>')
    # far-parapet lamps, then people and the bus, then near lamps
    for Z_ in range(40, 300, 22):
        x_, y_ = C(XL, 14.5, Z_)
        out.append(glow(x_, y_, 640 * 1.1 / Z_, "#FFE2A0", f"{u}-fl{Z_}", 0.7))
    for X_, Z_, c in ((-14.5, 44, "#C9574A"), (-14.8, 46.5, "#3E5A7A"), (-14.2, 92, "#E0B04A"), (-33, 60, "#5E4A6A"), (-14.6, 124, "#4A6A5A")):
        x_, b_ = C(X_, 9.4, Z_)
        out.append(figure(x_, b_, 640 * 1.7 / Z_, c, head="#1E1824", legs="#1E1824"))
    # red double-decker heading towards us
    bz0, bz1, bxl, bxr = 64, 75, -22.4, -19.8
    yb, yt = 9.3, 13.7
    side = C.quad_x(bxr, bz0, bz1, yb, yt)
    front = C.quad_z(bz0, bxl, bxr, yb, yt)
    out.append(Q(side, "#B8262A"))
    out.append(Q(front, "#D8323A"))
    for (y0, y1) in ((10.6, 11.7), (12.2, 13.3)):
        out.append(Q(C.quad_x(bxr, bz0 + 0.8, bz1 - 0.4, y0, y1), "#FFD98E"))
        for zz in [bz0 + 0.8 + i * (bz1 - bz0 - 1.2) / 5 for i in range(1, 5)]:
            a_, b_ = C(bxr, y0, zz), C(bxr, y1, zz)
            out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#8E1E22" stroke-width="1.2"/>')
        out.append(Q(C.quad_z(bz0, bxl + 0.2, bxr - 0.2, y0, y1), "#FFE6A8"))
    out.append(Q(C.quad_z(bz0, bxl + 0.4, bxr - 0.4, 13.35, 13.6), "#FFB830"))
    out.append(Q(C.quad_z(bz0, bxl, bxr, 11.85, 12.05), "#F2E6D8", ' opacity="0.7"'))
    out.append(Q(C.quad_x(bxr, bz0, bz1, 11.85, 12.05), "#F2E6D8", ' opacity="0.6"'))
    out.append(Q([C(bxl, yt, bz0), C(bxr, yt, bz0), C(bxr, yt, bz1), C(bxl, yt, bz1)], "#8E1E22"))
    for X_ in (bxl + 0.4, bxr - 0.4):
        hx, hy = C(X_, 9.9, bz0)
        out.append(glow(hx, hy, 16, "#FFF6D8", f"{u}-hl{int(X_ * 10)}", 0.85) + f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="2" fill="#FFFFFF"/>')
    # near-parapet lamp standards: triple lanterns
    for Z_ in range(34, 300, 22):
        x0, y0 = C(XR - 0.3, 10.1, Z_)
        x1, y1 = C(XR - 0.3, 14.2, Z_)
        s_ = 640 / Z_
        out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#1A2A2A" stroke-width="{max(1, s_ * 0.18):.1f}"/>')
        out.append(glow(x1, y1, s_ * 1.3, "#FFE2A0", f"{u}-nl{Z_}", 0.75))
        for dx in (-0.45, 0, 0.45):
            out.append(f'<circle cx="{x1 + dx * s_:.1f}" cy="{y1 - (0.25 if dx == 0 else 0) * s_:.1f}" r="{max(1, s_ * 0.2):.1f}" fill="#FFF2C8"/>')
        # reflection of each lamp
        rx_, ry_ = C(XR - 0.3, -10, Z_)
        out.append(f'<rect x="{x1 - s_ * 0.2:.1f}" y="{C(XR, 0, Z_)[1] + 3:.1f}" width="{max(1.2, s_ * 0.4):.1f}" height="{min(444, ry_) - C(XR, 0, Z_)[1]:.1f}" fill="#FFE2A0" opacity="0.25"/>')
    # a river cruiser gliding past with lit windows
    cz, cx0, cx1 = 118, 8, 38
    a_, b_ = C(cx0, 0, cz), C(cx1, 0, cz)
    s_ = 640 / cz
    out.append(f'<path d="M {a_[0]:.1f} {a_[1] + 1:.1f} Q {a_[0] - 60:.1f} {a_[1] + 5:.1f} {a_[0] - 150:.1f} {a_[1] + 3:.1f}" fill="none" stroke="#C8D2E8" stroke-width="1.8" opacity="0.5"/>')
    out.append(f'<rect x="{a_[0]:.1f}" y="{a_[1] + 2:.1f}" width="{b_[0] - a_[0]:.1f}" height="16" fill="#FFD98E" opacity="0.1"/>')
    out.append(water_lines(34, 23, (a_[0], a_[1] + 3, b_[0], a_[1] + 34), ["#FFD98E", "#FFE8B0"], w=(6, 22), h=(0.8, 1.6), opacity=(0.3, 0.8)))
    hull = [C(cx0, -0.2, cz), C(cx0 - 2.5, 1.9, cz), C(cx1 + 3.5, 1.9, cz), C(cx1 + 0.5, -0.2, cz)]
    out.append(Q(hull, "#1E2A4A"))
    out.append(Q([C(cx0 - 2.5, 1.5, cz), C(cx0 - 2.5, 1.9, cz), C(cx1 + 3.5, 1.9, cz), C(cx1 + 3.2, 1.5, cz)], "#E8E2D8"))
    out.append(Q(C.quad_z(cz, cx0 + 1, cx1 - 2, 1.9, 4.2), "#E8E2D8"))
    out.append(Q(C.quad_z(cz, cx0 + 1.6, cx1 - 2.6, 2.4, 3.7), "#FFE0A0"))
    for X_ in [cx0 + 1.6 + i * (cx1 - cx0 - 4.2) / 12 for i in range(1, 12)]:
        p0, p1 = C(X_, 2.4, cz), C(X_, 3.7, cz)
        out.append(f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" stroke="#B89A70" stroke-width="1"/>')
    out.append(Q(C.quad_z(cz, cx0 + 0.6, cx1 - 1.4, 4.2, 4.5), "#2A3A5A"))
    out.append(Q(C.quad_z(cz, cx1 - 6, cx1 - 2.4, 4.5, 6), "#E8E2D8"))
    out.append(Q(C.quad_z(cz, cx1 - 5.5, cx1 - 2.9, 4.9, 5.7), "#FFE0A0"))
    rl = [C(cx0 + 0.6, 4.5, cz), C(cx1 - 6, 4.5, cz)]
    out.append(f'<line x1="{rl[0][0]:.1f}" y1="{rl[0][1] - 0.9 * s_:.1f}" x2="{rl[1][0]:.1f}" y2="{rl[1][1] - 0.9 * s_:.1f}" stroke="#C8D2E8" stroke-width="1"/>')
    for X_, c in ((cx0 + 4, "#C9574A"), (cx0 + 6, "#E0B04A"), (cx0 + 11, "#5E7AA8")):
        px_, pb_ = C(X_, 4.5, cz)
        out.append(figure(px_, pb_, 1.6 * s_, c, head="#1E1824", legs="#1E1824"))
    fx, fy_ = C(cx1 + 1, 4.2, cz)
    out.append(f'<line x1="{fx:.1f}" y1="{fy_:.1f}" x2="{fx:.1f}" y2="{fy_ - 14:.1f}" stroke="#C8D2E8" stroke-width="1"/><path d="M {fx:.1f} {fy_ - 14:.1f} l 7 2 l -7 2 Z" fill="#C9574A"/>')
    out.append(gulls([(380, 168, 10), (402, 180, 7)], "#0E1430", 1.8))
    return "\n".join(out)


# ================================================================ VENICE — the Grand Canal toward the Salute, late morning
def proj(C, X, pts):
    """Project (Z, Y) points lying in the facade plane X."""
    return [C(X, y, z) for z, y in pts]


def palazzo(C, X, z0, z1, h, wall, seed, lit=True, trim="#F6F0E4"):
    """Venetian Gothic palazzo facade in the plane X: water doors, ogee windows, a central polifora with
    balcony, Istrian-stone string courses and funnel chimneys."""
    rnd = random.Random(seed)
    out = [Q(C.quad_x(X, z0, z1, 0, h), wall)]
    out.append(Q(C.quad_x(X, z0, z1, 0, 0.9), "#5E6A4E", ' opacity="0.6"'))
    out.append(Q(C.quad_x(X, z0, z1, 0.9, 1.6), "#E8E0D0", ' opacity="0.5"'))
    win = "#3A3440" if lit else "#2A2A3A"
    wglass = ("#3A3440", "#5A6A8A", "#2E3A4E")
    W = z1 - z0
    floors = [(4.6, 7.4)] + [(8.4 + i * 3.9, 11.0 + i * 3.9) for i in range(4) if 11.0 + i * 3.9 < h - 1.4]
    # water door
    zc = (z0 + z1) / 2
    dw = min(2.6, W * 0.18)
    out.append(Q(proj(C, X, [(zc - dw / 2, 0.4), (zc - dw / 2, 2.8), (zc, 3.8), (zc + dw / 2, 2.8), (zc + dw / 2, 0.4)]), "#2A2630"))
    out.append(f'<polyline points="{P(proj(C, X, [(zc - dw / 2 - 0.2, 0.4), (zc - dw / 2 - 0.2, 2.9), (zc, 4.0), (zc + dw / 2 + 0.2, 2.9), (zc + dw / 2 + 0.2, 0.4)]))}" fill="none" stroke="{trim}" stroke-width="1.2"/>')
    for fi, (ya, yb) in enumerate(floors):
        out.append(Q(C.quad_x(X, z0, z1, ya - 0.55, ya - 0.25), trim, ' opacity="0.9"'))
        nobile = fi in (1, 2)
        bays = max(3, int(W / 2.6))
        for i in range(bays):
            za = z0 + W * (i + 0.28) / bays
            zb = z0 + W * (i + 0.72) / bays
            central = nobile and abs((i + 0.5) / bays - 0.5) < 0.22
            if central:
                za, zb = z0 + W * (i + 0.08) / bays, z0 + W * (i + 0.92) / bays
            zm = (za + zb) / 2
            peak = (zb - za) * 0.75
            pts = [(za, ya), (za, yb), (zm, yb + peak), (zb, yb), (zb, ya)]
            out.append(Q(proj(C, X, [(za - 0.18, ya - 0.1), (za - 0.18, yb + 0.05), (zm, yb + peak + 0.25), (zb + 0.18, yb + 0.05), (zb + 0.18, ya - 0.1)]), trim))
            out.append(Q(proj(C, X, pts), rnd.choice(wglass)))
            if rnd.random() < 0.3:
                out.append(Q(proj(C, X, [(za, ya), (za, yb - 0.6), (zb, yb - 0.6), (zb, ya)]), "#4E7A5A"))
        if nobile:
            zb0, zb1 = z0 + W * 0.3, z0 + W * 0.7
            out.append(Q(C.quad_x(X, zb0, zb1, ya - 0.3, ya + 1.0), trim))
            out.append(f'<g stroke="#B8B0A8" stroke-width="0.8">' + "".join(
                f'<line x1="{C(X, ya - 0.2, zz)[0]:.1f}" y1="{C(X, ya - 0.2, zz)[1]:.1f}" x2="{C(X, ya + 0.9, zz)[0]:.1f}" y2="{C(X, ya + 0.9, zz)[1]:.1f}"/>'
                for zz in [zb0 + (zb1 - zb0) * j / 10 for j in range(1, 10)]) + "</g>")
    # quoins and cornice
    out.append(Q(C.quad_x(X, z0, z0 + 0.5, 0, h), trim, ' opacity="0.7"'))
    out.append(Q(C.quad_x(X, z0, z1, h - 0.7, h), trim))
    out.append(Q(C.quad_x(X, z0, z1, h - 1.0, h - 0.7), "#000", ' opacity="0.15"'))
    # funnel chimneys and a wooden roof terrace
    for _ in range(rnd.choice((1, 2, 2, 3))):
        zc = rnd.uniform(z0 + 1, z1 - 1)
        Xc = X + (-1.5 if X < 0 else 1.5)
        b0, b1 = C(Xc, h, zc), C(Xc, h + 2.6, zc)
        s_ = C.f / zc
        out.append(f'<rect x="{b0[0] - 0.35 * s_:.1f}" y="{b1[1]:.1f}" width="{0.7 * s_:.1f}" height="{b0[1] - b1[1]:.1f}" fill="{mix(wall, "#6A4A3A", 0.3)}"/>')
        out.append(f'<path d="M {b1[0] - 0.4 * s_:.1f} {b1[1]:.1f} L {b1[0] - 0.85 * s_:.1f} {b1[1] - 1.1 * s_:.1f} L {b1[0] + 0.85 * s_:.1f} {b1[1] - 1.1 * s_:.1f} L {b1[0] + 0.4 * s_:.1f} {b1[1]:.1f} Z" fill="#B8604A"/>')
    if rnd.random() < 0.4:
        za = rnd.uniform(z0 + 1, z1 - 4)
        Xa = X + (-2 if X < 0 else 2)
        out.append(Q(C.quad_x(Xa, za, za + 3, h, h + 1.8), "none", ' stroke="#6A4A3A" stroke-width="1"'))
        out.append(Q(C.quad_x(Xa, za, za + 3, h + 1.6, h + 1.9), "#6A4A3A"))
    if not lit:
        out.append(Q(C.quad_x(X, z0, z1, 0, h), "#3A4A7A", ' opacity="0.28"'))
    out.append(Q(C.quad_x(X, z0, z0 + 0.25, 0, h), "#000", ' opacity="0.25"'))
    return "".join(out)


def palo(C, X, Z, top, cols, gold="#E8C060"):
    """Striped mooring pole with a gilded cap."""
    x0, y0 = C(X, -0.6, Z)
    x1, y1 = C(X, top, Z)
    w = max(1.6, C.f * 0.24 / Z)
    out = [f'<rect x="{x0 - w / 2:.1f}" y="{y1:.1f}" width="{w:.1f}" height="{y0 - y1:.1f}" fill="{cols[0]}"/>']
    n = 7
    for i in range(n):
        ya = y1 + (y0 - y1) * (i + 0.15) / n
        out.append(f'<path d="M {x0 - w / 2:.1f} {ya + w * 0.6:.1f} L {x0 + w / 2:.1f} {ya:.1f} L {x0 + w / 2:.1f} {ya + (y0 - y1) / n * 0.5:.1f} L {x0 - w / 2:.1f} {ya + (y0 - y1) / n * 0.5 + w * 0.6:.1f} Z" fill="{cols[1]}"/>')
    out.append(f'<rect x="{x0 + w * 0.15:.1f}" y="{y1:.1f}" width="{w * 0.3:.1f}" height="{y0 - y1:.1f}" fill="#FFFFFF" opacity="0.3"/>')
    out.append(f'<ellipse cx="{x0:.1f}" cy="{y1:.1f}" rx="{w * 0.75:.1f}" ry="{w * 0.5:.1f}" fill="{gold}"/>')
    # reflection
    out.append(f'<g opacity="0.45">' + "".join(f'<rect x="{x0 - w / 2 + math.sin(i * 1.7) * w * 0.5:.1f}" y="{y0 + i * w * 1.1:.1f}" width="{w:.1f}" height="{w * 0.7:.1f}" fill="{cols[i % 2]}"/>' for i in range(int((y0 - y1) * 0.5 / (w * 1.1)))) + "</g>")
    return "".join(out)


def gondola(x, wl, k, flip=False, passengers=True, tarp=None):
    """Gondola in profile, bow to the left; (x, wl) = mid-hull on the waterline, k = px per metre."""
    sx = -k if flip else k
    g = [f'<g transform="translate({x:.1f} {wl:.1f}) scale({sx:.3f} {k:.3f})">']
    g.append('<path d="M -5.6 -0.1 Q 0 0.7 5.4 -0.1" fill="none" stroke="#FFFFFF" stroke-width="0.12" opacity="0.5"/>')
    g.append('<path d="M -5.8 -0.9 Q -5.9 -1.2 -5.6 -1.5 Q -2 -0.5 2 -0.5 Q 4.6 -0.6 5.6 -1.4 Q 5.8 -1.2 5.6 -0.8 Q 4 0.2 0 0.25 Q -4 0.2 -5.8 -0.9 Z" fill="#141218"/>')
    g.append('<path d="M -5.6 -1.5 Q -2 -0.5 2 -0.5 Q 4.6 -0.6 5.6 -1.4" fill="none" stroke="#8A8AA0" stroke-width="0.09"/>')
    # ferro on the bow
    g.append('<path d="M -5.6 -1.5 L -5.75 -2.5 Q -5.8 -2.75 -5.55 -2.8 L -5.2 -2.8 L -5.3 -1.4 Z" fill="#E8E4E8"/>')
    g.append('<g stroke="#E8E4E8" stroke-width="0.09">' + "".join(f'<line x1="-5.62" y1="{-1.7 - i * 0.18:.2f}" x2="-6.0" y2="{-1.7 - i * 0.18:.2f}"/>' for i in range(5)) + "</g>")
    g.append('<path d="M 5.6 -1.4 Q 5.9 -1.7 5.8 -2.0 L 5.6 -1.95 Z" fill="#E8E4E8"/>')
    if tarp:
        g.append(f'<path d="M -4 -0.55 Q 0 -1.1 4 -0.6 L 4 -0.5 L -4 -0.45 Z" fill="{tarp}"/>')
    if passengers:
        g.append('<rect x="-1.6" y="-0.95" width="1.9" height="0.45" rx="0.1" fill="#B8262E"/>')
        g.append('<path d="M -1.3 -0.9 L -1.2 -1.75 Q -0.9 -1.95 -0.6 -1.75 L -0.5 -0.9 Z" fill="#F2E6D0"/><circle cx="-0.9" cy="-2.0" r="0.22" fill="#4A2E22"/>')
        g.append('<path d="M -0.5 -0.9 L -0.4 -1.8 Q -0.1 -2.0 0.2 -1.8 L 0.3 -0.9 Z" fill="#2E4A7A"/><circle cx="-0.1" cy="-2.05" r="0.22" fill="#2A1E1A"/>')
        # gondolier at the stern, striped shirt and boater, oar in the forcola
        g.append('<path d="M 3.6 -0.62 L 3.75 -1.35 L 4.05 -1.35 L 4.15 -0.62 Z" fill="#1E1A22"/>')
        g.append('<path d="M 3.55 -1.35 L 3.6 -2.2 Q 3.85 -2.35 4.1 -2.2 L 4.15 -1.35 Z" fill="#F4F0E8"/>')
        g.append('<g fill="#1E2A5A">' + "".join(f'<rect x="3.57" y="{-2.15 + i * 0.17:.2f}" width="0.56" height="0.07"/>' for i in range(5)) + "</g>")
        g.append('<circle cx="3.85" cy="-2.45" r="0.17" fill="#C8906A"/><rect x="3.55" y="-2.62" width="0.6" height="0.13" fill="#E8D090"/><rect x="3.66" y="-2.75" width="0.38" height="0.15" fill="#E8D090"/><rect x="3.66" y="-2.66" width="0.38" height="0.05" fill="#B8262E"/>')
        g.append('<path d="M 3.7 -2.0 L 3.0 -1.3" stroke="#C8906A" stroke-width="0.1" stroke-linecap="round"/>')
        g.append('<line x1="2.4" y1="-2.4" x2="4.9" y2="0.5" stroke="#8A6A4A" stroke-width="0.09"/><path d="M 4.75 0.3 L 5.1 0.25 L 5.15 0.7 L 4.85 0.75 Z" fill="#8A6A4A"/>')
        g.append('<path d="M 3.1 -0.6 Q 3.0 -1.05 3.25 -1.15 L 3.35 -0.6 Z" fill="#6A4A2E"/>')
    g.append("</g>")
    return "".join(g)


def salute(cx, base, k, u):
    """Santa Maria della Salute: octagon with great scroll volutes, drum and lead dome, lit from the right."""
    st, sh, dm, dms = "#F6F2EA", "#BDB8C4", "#B8C2CC", "#7E8698"
    out = [defs(lg(f"{u}-dome", [(0, dms), (0.5, dm), (0.85, "#E8EEF2"), (1, "#C8D0D8")], 0, 0, 1, 0),
                lg(f"{u}-oct", [(0, sh), (0.35, "#E2DED8"), (1, st)], 0, 0, 1, 0))]
    # rear dome and bell towers
    for dx in (34, 62):
        out.append(f'<rect x="{cx + dx * k - 3 * k:.1f}" y="{base - 62 * k:.1f}" width="{6 * k:.1f}" height="{40 * k:.1f}" fill="{sh}"/><path d="M {cx + dx * k - 3.4 * k:.1f} {base - 62 * k:.1f} Q {cx + dx * k:.1f} {base - 72 * k:.1f} {cx + dx * k + 3.4 * k:.1f} {base - 62 * k:.1f} Z" fill="{dms}"/>')
    out.append(f'<rect x="{cx + 38 * k:.1f}" y="{base - 46 * k:.1f}" width="{20 * k:.1f}" height="{14 * k:.1f}" fill="{sh}"/><path d="M {cx + 37 * k:.1f} {base - 46 * k:.1f} Q {cx + 48 * k:.1f} {base - 64 * k:.1f} {cx + 59 * k:.1f} {base - 46 * k:.1f} Z" fill="url(#{u}-dome)"/>')
    # octagon body
    out.append(f'<rect x="{cx - 26 * k:.1f}" y="{base - 30 * k:.1f}" width="{52 * k:.1f}" height="{30 * k:.1f}" fill="url(#{u}-oct)"/>')
    out.append(f'<rect x="{cx - 34 * k:.1f}" y="{base - 26 * k:.1f}" width="{8 * k:.1f}" height="{26 * k:.1f}" fill="{sh}"/><rect x="{cx + 26 * k:.1f}" y="{base - 26 * k:.1f}" width="{8 * k:.1f}" height="{26 * k:.1f}" fill="{st}"/>')
    # triumphal-arch portal with columns and pediment
    out.append(f'<path d="M {cx - 7 * k:.1f} {base:.1f} L {cx - 7 * k:.1f} {base - 14 * k:.1f} Q {cx:.1f} {base - 21 * k:.1f} {cx + 7 * k:.1f} {base - 14 * k:.1f} L {cx + 7 * k:.1f} {base:.1f} Z" fill="#5A4E5A"/>')
    for dx in (-18, -11, 11, 18):
        out.append(f'<rect x="{cx + dx * k - 1.4 * k:.1f}" y="{base - 25 * k:.1f}" width="{2.8 * k:.1f}" height="{25 * k:.1f}" fill="{st}"/><rect x="{cx + dx * k + 0.4 * k:.1f}" y="{base - 25 * k:.1f}" width="{1 * k:.1f}" height="{25 * k:.1f}" fill="{sh}" opacity="0.6"/>')
    out.append(f'<path d="M {cx - 21 * k:.1f} {base - 26 * k:.1f} L {cx:.1f} {base - 33 * k:.1f} L {cx + 21 * k:.1f} {base - 26 * k:.1f} Z" fill="{st}"/><path d="M {cx - 21 * k:.1f} {base - 26 * k:.1f} L {cx:.1f} {base - 33 * k:.1f}" stroke="{sh}" stroke-width="{0.8 * k:.1f}"/>')
    for dx in (-30, 30):
        out.append(f'<path d="M {cx + dx * k - 2 * k:.1f} {base - 4 * k:.1f} L {cx + dx * k - 2 * k:.1f} {base - 14 * k:.1f} Q {cx + dx * k:.1f} {base - 17 * k:.1f} {cx + dx * k + 2 * k:.1f} {base - 14 * k:.1f} L {cx + dx * k + 2 * k:.1f} {base - 4 * k:.1f} Z" fill="#6A6070"/>')
    out.append(f'<rect x="{cx - 35 * k:.1f}" y="{base - 31 * k:.1f}" width="{70 * k:.1f}" height="{2.4 * k:.1f}" fill="{st}"/>')
    # statues on the cornice
    for dx in (-32, -21, 0, 21, 32):
        out.append(f'<path d="M {cx + dx * k - 1 * k:.1f} {base - 31 * k:.1f} L {cx + dx * k - 0.8 * k:.1f} {base - 36 * k:.1f} Q {cx + dx * k:.1f} {base - 38 * k:.1f} {cx + dx * k + 0.8 * k:.1f} {base - 36 * k:.1f} L {cx + dx * k + 1 * k:.1f} {base - 31 * k:.1f} Z" fill="#D8D4D0"/>')
    # drum with the great scroll volutes
    out.append(f'<rect x="{cx - 20 * k:.1f}" y="{base - 48 * k:.1f}" width="{40 * k:.1f}" height="{18 * k:.1f}" fill="url(#{u}-oct)"/>')
    for i, dx in enumerate((-22, -13, -4.5, 4.5, 13, 22)):
        sc = 1 - abs(dx) / 60
        vx = cx + dx * k
        vy = base - 33 * k
        out.append(f'<path d="M {vx - 3 * k * sc:.1f} {vy:.1f} Q {vx - 3.4 * k * sc:.1f} {vy - 9 * k:.1f} {vx:.1f} {vy - 11 * k:.1f} Q {vx + 3.4 * k * sc:.1f} {vy - 9 * k:.1f} {vx + 2.4 * k * sc:.1f} {vy - 5 * k:.1f} Q {vx + 0.4 * k:.1f} {vy - 3.5 * k:.1f} {vx + 0.6 * k:.1f} {vy - 6.5 * k:.1f} L {vx + 1.4 * k * sc:.1f} {vy:.1f} Z" fill="{st if dx > 0 else "#E2DED8"}"/>')
        out.append(f'<circle cx="{vx + 0.4 * k:.1f}" cy="{vy - 6 * k:.1f}" r="{1.4 * k * sc:.1f}" fill="none" stroke="{sh}" stroke-width="{0.6 * k:.1f}"/>')
        out.append(f'<path d="M {vx - 0.7 * k:.1f} {vy - 11 * k:.1f} L {vx - 0.5 * k:.1f} {vy - 14.5 * k:.1f} Q {vx:.1f} {vy - 15.5 * k:.1f} {vx + 0.5 * k:.1f} {vy - 14.5 * k:.1f} L {vx + 0.7 * k:.1f} {vy - 11 * k:.1f} Z" fill="#D8D4D0"/>')
    for dx in (-14, -7, 0, 7, 14):
        out.append(f'<path d="M {cx + dx * k - 1.4 * k:.1f} {base - 34 * k:.1f} L {cx + dx * k - 1.4 * k:.1f} {base - 40 * k:.1f} Q {cx + dx * k:.1f} {base - 42 * k:.1f} {cx + dx * k + 1.4 * k:.1f} {base - 40 * k:.1f} L {cx + dx * k + 1.4 * k:.1f} {base - 34 * k:.1f} Z" fill="#6A6878"/>')
    out.append(f'<rect x="{cx - 21 * k:.1f}" y="{base - 49 * k:.1f}" width="{42 * k:.1f}" height="{2 * k:.1f}" fill="{st}"/>')
    # dome, ribs, lantern
    out.append(f'<path d="M {cx - 19 * k:.1f} {base - 48 * k:.1f} C {cx - 19 * k:.1f} {base - 62 * k:.1f} {cx - 10 * k:.1f} {base - 70 * k:.1f} {cx:.1f} {base - 70 * k:.1f} C {cx + 10 * k:.1f} {base - 70 * k:.1f} {cx + 19 * k:.1f} {base - 62 * k:.1f} {cx + 19 * k:.1f} {base - 48 * k:.1f} Z" fill="url(#{u}-dome)"/>')
    for t in (-0.7, -0.35, 0, 0.35, 0.7):
        out.append(f'<path d="M {cx + t * 19 * k:.1f} {base - 48 * k:.1f} Q {cx + t * 15 * k:.1f} {base - 64 * k:.1f} {cx:.1f} {base - 70 * k:.1f}" fill="none" stroke="#6E7688" stroke-width="{0.5 * k:.1f}" opacity="0.6"/>')
    out.append(f'<path d="M {cx + 6 * k:.1f} {base - 68.5 * k:.1f} C {cx + 14 * k:.1f} {base - 66 * k:.1f} {cx + 18 * k:.1f} {base - 58 * k:.1f} {cx + 18.6 * k:.1f} {base - 50 * k:.1f}" fill="none" stroke="#FFFFFF" stroke-width="{0.9 * k:.1f}" opacity="0.8"/>')
    out.append(f'<rect x="{cx - 4 * k:.1f}" y="{base - 77 * k:.1f}" width="{8 * k:.1f}" height="{7 * k:.1f}" fill="url(#{u}-oct)"/><path d="M {cx - 4.4 * k:.1f} {base - 77 * k:.1f} Q {cx:.1f} {base - 83 * k:.1f} {cx + 4.4 * k:.1f} {base - 77 * k:.1f} Z" fill="url(#{u}-dome)"/>')
    out.append(f'<rect x="{cx - 0.5 * k:.1f}" y="{base - 88 * k:.1f}" width="{1 * k:.1f}" height="{6 * k:.1f}" fill="#8A8090"/><circle cx="{cx:.1f}" cy="{base - 88.5 * k:.1f}" r="{1 * k:.1f}" fill="#E8C060"/>')
    # steps down to the water
    for i in range(4):
        out.append(f'<rect x="{cx - (40 + i * 3) * k:.1f}" y="{base + i * 1.2 * k:.1f}" width="{(80 + i * 6) * k:.1f}" height="{1.2 * k:.1f}" fill="{st if i % 2 == 0 else sh}"/>')
    return "".join(out)


def venice():
    u = "vn"
    C = Cam(f=600, cx=300, vpy=250, eye=11)
    out = [defs(
        lg(f"{u}-sky", [(0, "#4E8ED2"), (0.35, "#8EBEE6"), (0.56, "#D6E8F2"), (0.6, "#EEF2EE")], 0, 0, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-water", [(0, "#B8D8D0"), (0.1, "#7EB8B0"), (0.45, "#3E8A88"), (1, "#1E5A62")], 0, 250, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(560, 40, 220, "#FFFBEA", f"{u}-sun", 0.7))
    out.append(cumulus(f"{u}-c1", 160, 120, 150, 40, 4, "#FFFFFF", "#F2F4F8", "#B8C8DE", hi="#FFFFFF", hi_op=0.75, light=1))
    out.append(cumulus(f"{u}-c2", 470, 92, 120, 30, 6, "#FFFFFF", "#F2F4F8", "#B8C8DE", hi="#FFFFFF", hi_op=0.75, light=1))
    out.append(cumulus(f"{u}-c3", 330, 168, 80, 20, 8, "#FFFFFF", "#F2F4F8", "#C2D0E2", hi="#FFFFFF", light=1))
    out.append(f'<rect x="0" y="250" width="600" height="194" fill="url(#{u}-water)"/>')
    # far: Giudecca shore and the island church across the basin
    out.append(Q([(150, 251), (150, 244), (230, 245), (300, 247), (420, 246), (420, 251)], "#B8C4CE"))
    out.append('<g fill="#AAB6C4"><rect x="268" y="214" width="6" height="34"/><path d="M 266 214 L 271 202 L 276 214 Z"/><path d="M 280 246 L 280 236 Q 290 222 300 236 L 300 246 Z"/><rect x="288" y="220" width="3" height="6"/></g>')
    # Salute, rising beyond the right bank
    out.append(salute(404, 274, 2.05, f"{u}-sa"))
    # right bank palazzi (in shade), far to near
    right = [(340, 400, 15, "#E8C8B0"), (280, 340, 17, "#D89A80"), (232, 280, 15, "#F0D6B4"), (190, 232, 19, "#C87868"), (150, 190, 16, "#E8B888"),
             (118, 150, 20, "#D8A0A0"), (92, 118, 15, "#F0D8B8"), (70, 92, 18, "#C86A5A"), (52, 70, 16, "#E8C090")]
    for k_, (z0, z1, h, c) in enumerate(right):
        if z0 >= 200:
            continue
        out.append(palazzo(C, 26, z0, z1, h, c, 50 + k_, lit=False))
    # left bank palazzi in full sun
    left = [(420, 520, 16, "#F0D6B4"), (360, 420, 18, "#D8A090"), (300, 360, 15, "#E8C090"), (250, 300, 20, "#C8786A"), (205, 250, 16, "#F2DCC0"),
            (168, 205, 19, "#E0A878"), (136, 168, 17, "#D88A80"), (108, 136, 21, "#F0D0A8"), (84, 108, 16, "#C86A5A"), (62, 84, 19, "#E8B888"), (44, 62, 17, "#F2D8B8")]
    for k_, (z0, z1, h, c) in enumerate(left):
        out.append(palazzo(C, -26, z0, z1, h, c, 10 + k_, lit=True))
    # reflections of the facades: broken vertical colour in the water
    rnd = random.Random(33)
    for X, blds, lit in ((-26, left, True), (26, [r for r in right if r[0] < 200], False)):
        for z0, z1, h, c in blds:
            for j in range(18):
                Yr = -h * (j + 0.5) / 18
                za, zb = z0 + rnd.uniform(0, 2), z1 - rnd.uniform(0, 2)
                q = C.quad_x(X, za, zb, Yr - h / 36, Yr + h / 36)
                xs_ = [p[0] for p in q]
                ys_ = [p[1] for p in q]
                out.append(f'<rect x="{min(xs_):.1f}" y="{min(ys_):.1f}" width="{max(xs_) - min(xs_):.1f}" height="{max(0.8, (max(ys_) - min(ys_)) * 0.55):.1f}" fill="{c}" opacity="{0.45 * (1 - j / 22):.2f}"/>')
    for z0, z1, h, c in [r for r in right if r[0] < 200]:
        q = C.quad_x(26, z0, z1, -h, 0)
        out.append(Q(q, "#2A5A6A", ' opacity="0.25"'))
    # Salute reflection
    for j in range(16):
        y = 279 + j * 3.2
        w = rnd.uniform(40, 120) * (1 - j / 20)
        out.append(f'<rect x="{404 - w / 2 + rnd.uniform(-8, 8):.1f}" y="{y:.1f}" width="{w:.1f}" height="1.6" rx="0.8" fill="#F2EEE6" opacity="{0.55 * (1 - j / 18):.2f}"/>')
    out.append(water_lines(170, 34, (0, 256, 600, 444), ["#D8F0EA", "#2E6E74", "#9ED0C8", "#FFFFFF"], w=(6, 44), h=(0.8, 2), opacity=(0.25, 0.7)))
    # sun sparkle on the water
    out.append(water_lines(60, 35, (240, 262, 420, 444), ["#FFFFFF", "#FFFBEA"], w=(3, 12), h=(0.8, 1.4), opacity=(0.6, 1)))
    # a vaporetto coming up the canal
    vz = 210
    q = C.quad_z(vz, -6, 4, 0, 2.2)
    out.append(Q(q, "#E8E4DC"))
    out.append(Q(C.quad_z(vz, -6, 4, 0, 0.6), "#2A3A4A"))
    out.append(Q(C.quad_z(vz, -5, 3, 1.0, 1.9), "#5A7A8A"))
    out.append(Q(C.quad_z(vz, -6.3, 4.3, 2.2, 2.6), "#F2C060"))
    out.append(f'<path d="M {C(-6, 0, vz)[0]:.1f} {C(-6, 0, vz)[1] + 1:.1f} L {C(-10, 0, vz - 30)[0]:.1f} {C(-10, 0, vz - 30)[1]:.1f} M {C(4, 0, vz)[0]:.1f} {C(4, 0, vz)[1] + 1:.1f} L {C(8, 0, vz - 30)[0]:.1f} {C(8, 0, vz - 30)[1]:.1f}" stroke="#FFFFFF" stroke-width="1.6" opacity="0.6"/>')
    # moored gondolas under blue covers and the striped poles on the left
    for Z in (50, 56, 63):
        x_, wl = C(-23.5, 0, Z)
        s_ = C.f / Z
        out.append(f'<path d="M {x_ - 0.8 * s_:.1f} {wl:.1f} L {x_ - 0.4 * s_:.1f} {wl - 0.7 * s_:.1f} L {x_ + 0.7 * s_:.1f} {wl - 0.7 * s_:.1f} L {x_ + 0.9 * s_:.1f} {wl:.1f} Z" fill="#141218"/>'
                   f'<path d="M {x_ - 0.45 * s_:.1f} {wl - 0.7 * s_:.1f} Q {x_ + 0.1 * s_:.1f} {wl - 1.1 * s_:.1f} {x_ + 0.65 * s_:.1f} {wl - 0.7 * s_:.1f} Z" fill="#2E5AA8"/>'
                   f'<path d="M {x_ - 0.2 * s_:.1f} {wl - 0.7 * s_:.1f} L {x_ - 0.1 * s_:.1f} {wl - 1.9 * s_:.1f} L {x_ + 0.05 * s_:.1f} {wl - 0.7 * s_:.1f} Z" fill="#E8E4E8"/>')
    for X, Z, cols in ((-22.6, 47, ("#F6F2EA", "#2E5AA8")), (-22.4, 53.5, ("#F6F2EA", "#2E5AA8")), (-22.6, 60, ("#F6F2EA", "#2E5AA8")), (-22.5, 68, ("#F6F2EA", "#C8343A")),
                       (-22.5, 76, ("#F6F2EA", "#C8343A")), (-23, 96, ("#F6F2EA", "#2E7A5A")), (-23, 104, ("#F6F2EA", "#2E7A5A")),
                       (23, 62, ("#F6F2EA", "#B8342E")), (23, 70, ("#F6F2EA", "#B8342E")), (23.4, 100, ("#F6F2EA", "#2E5AA8"))):
        out.append(palo(C, X, Z, 4.2, cols))
    # a gondola crossing in the foreground, its reflection
    gx, gwl = 318, 404
    out.append(f'<g opacity="0.35" transform="translate(0 {2 * gwl + 2}) scale(1 -1)">{gondola(gx, gwl, 15.5, passengers=True)}</g>')
    out.append(f'<rect x="{gx - 96}" y="{gwl + 2}" width="190" height="44" fill="#2E6E74" opacity="0.35"/>')
    out.append(water_lines(30, 41, (gx - 100, gwl + 3, gx + 100, 444), ["#9ED0C8", "#1E4A52"], w=(10, 40), h=(1, 2.2), opacity=(0.4, 0.8)))
    out.append(gondola(gx, gwl, 15.5))
    out.append(f'<path d="M {gx - 92} {gwl + 2} Q {gx - 130} {gwl + 6} {gx - 170} {gwl + 4} M {gx - 92} {gwl + 4} Q {gx - 120} {gwl + 14} {gx - 150} {gwl + 16}" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity="0.55"/>')
    out.append(gulls([(240, 150, 11), (262, 162, 8), (520, 190, 9)], "#3A4A6A", 1.8))
    return "\n".join(out)


# ================================================================ CAIRO — the Giza pyramids at sunrise, a caravan on the dunes
CAMEL_BODY = ("M 88 -70 C 87 -88 74 -103 57 -104 C 45 -104 37 -94 31 -85 C 25 -80 19 -79 14 -81 C 7 -85 0 -96 -5 -104 "
              "L -15 -107 C -23 -107 -29 -101 -27 -96 C -23 -93 -15 -95 -10 -92 C -5 -85 4 -71 10 -63 C 14 -57 19 -53 24 -52 "
              "C 40 -47 58 -46 70 -51 C 80 -53 89 -60 88 -70 Z")


def camel(x, base, k, rider=None, blanket="#B8343A", tassel="#2E5AA8", rim="#FFD08A", body="#5E3E3A", far="#3E2A2E", flip=False, step=0):
    """Dromedary in profile facing left, rim-lit from behind on the right; optional rider."""
    sx = -k if flip else k
    legs_far = [((26, -52), (31, -28 + step * 2), (27 - step * 4, 0)), ((70, -51), (77, -28), (74 + step * 3, 0))]
    legs_near = [((22, -52), (20 - step * 3, -28), (16 - step * 5, 0)), ((64, -50), (66, -27), (63 - step * 2, 0))]
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({sx:.3f} {k:.3f})">']
    for (a_, b_, c_) in legs_far:
        g.append(f'<path d="M {a_[0]} {a_[1]} L {b_[0]} {b_[1]} L {c_[0]} {c_[1]}" fill="none" stroke="{far}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
    g.append(f'<path d="{CAMEL_BODY}" fill="{body}"/>')
    for (a_, b_, c_) in legs_near:
        g.append(f'<path d="M {a_[0]} {a_[1]} L {b_[0]} {b_[1]} L {c_[0]} {c_[1]}" fill="none" stroke="{body}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
        g.append(f'<ellipse cx="{c_[0] - 1}" cy="-1" rx="5" ry="2" fill="{far}"/>')
    g.append('<path d="M 88 -66 Q 94 -56 90 -40" fill="none" stroke="#3E2A2E" stroke-width="3" stroke-linecap="round"/>')
    # rim light along the hump and rump, eye, ear
    g.append(f'<path d="M 31 -85 C 37 -94 45 -104 57 -104 C 74 -103 87 -88 88 -70 C 89 -60 80 -53 70 -51" fill="none" stroke="{rim}" stroke-width="2.6" stroke-linecap="round"/>')
    g.append(f'<path d="M -5 -104 L -15 -107" stroke="{rim}" stroke-width="2" stroke-linecap="round"/>')
    g.append('<circle cx="-14" cy="-100" r="1.6" fill="#1E1416"/><path d="M -6 -104 l 3 -5 l 1 5 Z" fill="#3E2A2E"/>')
    # saddle blanket with tassels
    g.append(f'<path d="M 36 -92 Q 56 -110 78 -92 L 82 -66 Q 58 -60 34 -66 Z" fill="{blanket}"/>')
    g.append(f'<path d="M 34 -66 Q 58 -60 82 -66" fill="none" stroke="#F2D080" stroke-width="2.4"/>')
    g.append(f'<g fill="{tassel}">' + "".join(f'<path d="M {38 + i * 7} {-65 + abs(i - 3) * 0.4} l -1.6 7 l 3.2 0 Z"/>' for i in range(7)) + "</g>")
    g.append('<path d="M 44 -86 L 72 -86" stroke="#F2D080" stroke-width="1.6" stroke-dasharray="3 2"/>')
    g.append('<path d="M -24 -97 Q 0 -86 30 -82" fill="none" stroke="#2A1E1A" stroke-width="1.2"/>')
    if rider:
        robe, scarf = rider
        g.append(f'<path d="M 46 -96 L 50 -126 Q 58 -132 66 -126 L 70 -96 Z" fill="{robe}"/>')
        g.append(f'<path d="M 52 -100 L 46 -78 L 52 -76 L 58 -98 Z" fill="{robe}"/>')
        g.append(f'<circle cx="58" cy="-134" r="7" fill="#5A3A2E"/><path d="M 50 -136 Q 58 -146 66 -136 L 68 -128 Q 58 -132 50 -130 Z" fill="{scarf}"/>')
        g.append(f'<path d="M 66 -126 L 70 -96" stroke="{rim}" stroke-width="2"/><path d="M 64 -140 Q 68 -136 66 -128" stroke="{rim}" stroke-width="1.8" fill="none"/>')
        g.append(f'<path d="M 52 -118 L 30 -104" stroke="{robe}" stroke-width="4" stroke-linecap="round"/>')
    g.append("</g>")
    return "".join(g)


def camel_shadow(x, base, k, color="#6A4A6A", op=0.32, flip=False):
    sx = -k if flip else k
    return (f'<g transform="matrix({sx:.3f} 0 {-1.5 * k:.3f} {-0.22 * k:.3f} {x:.1f} {base:.1f})" opacity="{op}">'
            f'<path d="{CAMEL_BODY}" fill="{color}"/><g stroke="{color}" stroke-width="7" stroke-linecap="round"><line x1="22" y1="-52" x2="18" y2="0"/><line x1="64" y1="-50" x2="64" y2="0"/><line x1="28" y1="-52" x2="27" y2="0"/><line x1="72" y1="-51" x2="74" y2="0"/></g></g>')


def pyramid(apex, left, right, u, near_col, far_col, rim, courses=24, cap=None, seed=0, rim_left=False):
    """Two visible faces split at the front edge; stone courses; rim light on the sunlit right edge."""
    ax, ay = apex
    (lx, ly), (rx, ry) = left, right
    ex = ax + (rx - ax) * 0.22  # front arris foot, toward the right
    ey = max(ly, ry) + 4
    out = [Q([apex, left, (ex, ey)], near_col), Q([apex, (ex, ey), right], far_col)]
    rnd = random.Random(seed)
    g = []
    for i in range(1, courses):
        t = i / courses
        y1 = ay + (ly - ay) * t
        xa = ax + (lx - ax) * t
        xb = ax + (ex - ax) * t
        xc = ax + (rx - ax) * t
        yb = ay + (ey - ay) * t
        yc = ay + (ry - ay) * t
        g.append(f'<path d="M {xa:.1f} {y1:.1f} L {xb:.1f} {yb:.1f} L {xc:.1f} {yc:.1f}" />')
    out.append(f'<g fill="none" stroke="#4A2E3E" stroke-width="0.8" opacity="0.22">{"".join(g)}</g>')
    # erosion: lighter and darker blocks
    cid = f"{u}-pc"
    out.append(f'<clipPath id="{cid}"><polygon points="{P([apex, left, (ex, ey), right])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{cid})">' + blobs(int((rx - lx) / 4), seed, (lx, ay, rx, ey), ["#FFE0B0", "#6A4A5A", "#C89A8A"], r=(1.5, 4), opacity=(0.12, 0.3), squash=0.5))
    if cap:
        ct = cap
        capq = [apex, (ax + (lx - ax) * ct, ay + (ly - ay) * ct), (ax + (ex - ax) * ct, ay + (ey - ay) * ct), (ax + (rx - ax) * ct, ay + (ry - ay) * ct)]
        out.append(Q(capq, "#F2D2B0", ' opacity="0.55"'))
    out.append("</g>")
    out.append(Q([apex, left, (ex, ey), right], f"url(#{u}-v)"))
    out.insert(0, defs(lg(f"{u}-v", [(0, "#FFE8C0", 0.35), (0.5, "#FFE8C0", 0), (1, "#5A3A5A", 0.18)], 0, ay, 0, ey, units="userSpaceOnUse")))
    out.append(f'<polyline points="{P([apex, left if rim_left else right])}" fill="none" stroke="{rim}" stroke-width="2.4" stroke-linecap="round"/>')
    out.append(f'<polyline points="{P([apex, (ex, ey)])}" fill="none" stroke="{rim}" stroke-width="1.2" opacity="0.6"/>')
    return "".join(out)


def cairo():
    u = "cr"
    hz = 292
    out = [defs(
        lg(f"{u}-sky", [(0, "#4E5C96"), (0.3, "#8E7EAE"), (0.55, "#E09A9E"), (0.75, "#F6BC8E"), (0.92, "#FCDCA6"), (1, "#FFEAC0")], 0, 0, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-plat", [(0, "#E8B49A"), (1, "#C88A84")], 0, hz, 0, 340, units="userSpaceOnUse"),
        lg(f"{u}-dune1", [(0, "#F2B88E"), (1, "#C8857E")], 0, 330, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-dune2", [(0, "#D49884"), (0.5, "#B87C7A"), (1, "#9A6670")], 0, 360, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#FCE0C0", 0), (1, "#FCE0C0", 0.9)], 0, 240, 0, hz + 4, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="{hz + 2}" fill="url(#{u}-sky)"/>')
    out.append(glow(424, 222, 330, "#FFD8A0", f"{u}-g1", 0.85))
    out.append(glow(424, 222, 70, "#FFF6D8", f"{u}-g2", 1))
    out.append('<circle cx="424" cy="222" r="19" fill="#FFF4D6"/>')
    for x, y, w, c in ((110, 120, 100, "#F2B0A8"), (60, 140, 60, "#F8C0A8"), (300, 100, 120, "#D89AAE"), (500, 128, 90, "#F6B4A0"), (470, 196, 120, "#FFD0A0"), (210, 214, 80, "#FFD8AE"), (560, 226, 50, "#FFE0B0")):
        out.append(streak_cloud(x, y, w, c, 0.6, 3.5))
        out.append(streak_cloud(x + w * 0.2, y - 2, w * 0.5, "#FFEED0", 0.5, 1.5))
    # Cairo on the horizon: minarets and domes in the dawn haze
    rnd = random.Random(8)
    x = -10
    while x < 610:
        w = rnd.uniform(8, 22)
        h = rnd.uniform(3, 10)
        out.append(f'<rect x="{x:.1f}" y="{hz - h:.1f}" width="{w + 0.5:.1f}" height="{h + 2:.1f}" fill="#D8A8AC"/>')
        x += w
    for mx, mh in ((60, 26), (94, 18), (520, 30), (556, 20), (250, 16)):
        out.append(f'<rect x="{mx - 1.6}" y="{hz - mh}" width="3.2" height="{mh}" fill="#CFA0A6"/><path d="M {mx - 2.4} {hz - mh} L {mx} {hz - mh - 7} L {mx + 2.4} {hz - mh} Z" fill="#CFA0A6"/><rect x="{mx - 2.6}" y="{hz - mh * 0.6}" width="5.2" height="1.6" fill="#CFA0A6"/>')
    out.append('<path d="M 506 290 Q 518 270 530 290 Z" fill="#CFA0A6"/><path d="M 80 290 Q 88 276 96 290 Z" fill="#D2A2A8"/>')
    out.append(f'<rect x="0" y="236" width="600" height="{hz - 236 + 4}" fill="url(#{u}-haze)"/>')
    # the three pyramids, far to near; the queens' pyramids in front
    out.append(pyramid((502, 150), (382, 292), (622, 292), f"{u}-k", "#E2A894", "#C88E92", "#FFE8B8", courses=26, seed=1, rim_left=True))
    out.append(pyramid((322, 112), (186, 298), (462, 298), f"{u}-f", "#B98290", "#E4A48E", "#FFE6B8", courses=30, cap=0.12, seed=2))
    out.append(pyramid((176, 214), (108, 306), (248, 306), f"{u}-m", "#A8768A", "#D89888", "#FFDCA8", courses=14, seed=3))
    for k_, (cx_, h_) in enumerate(((150, 18), (186, 16), (222, 14))):
        out.append(pyramid((cx_, 316 - h_), (cx_ - h_ * 0.85, 316), (cx_ + h_ * 0.85, 316), f"{u}-q{k_}", "#9A6A80", "#C88A84", "#FFD8A0", courses=5, seed=10 + k_))
    out.append(mist(300, 300, 340, 22, "#FCE2C6", f"{u}-m1", 0.65))
    # plateau and dunes
    out.append(Q([(-10, 296), (610, 294), (610, 444), (-10, 444)], f"url(#{u}-plat)"))
    out.append(dots(160, 41, (-10, 300, 610, 340), "#9A6A72", r=(0.6, 1.6), opacity=(0.2, 0.5)))
    poly, mid = ridge_poly([(-10, 336), (120, 322), (260, 330), (400, 318), (520, 326), (610, 316)], 31, amp=4, fill="#D89A8A")
    out.append(poly)
    out.append(f'<polyline points="{P(mid)}" fill="none" stroke="#FFD8A8" stroke-width="1.4" opacity="0.45"/>')
    crest = rough([(-10, 400), (90, 380), (210, 366), (330, 364), (450, 374), (610, 362)], 52, amp=3, depth=3)
    out.append(Q(crest + [(610, 444), (-10, 444)], f"url(#{u}-dune2)"))
    # sunlit lee faces breaking over the crest
    out.append(Q([(330, 364), (450, 374), (610, 362), (610, 376), (470, 388), (360, 380)], "#E8A888", ' opacity="0.7"'))
    out.append(f'<polyline points="{P(crest)}" fill="none" stroke="#FFD8A0" stroke-width="2.6" stroke-linejoin="round"/>')
    # wind ripples following the dune's slope, catching light on their crests
    rnd = random.Random(61)
    rip, hi = [], []
    for i in range(34):
        t = i / 34
        y0 = 388 + t * 54 + rnd.uniform(-2, 2)
        x0 = rnd.uniform(-30, 200)
        w = rnd.uniform(180, 420)
        bow = 6 + t * 8
        d = f'M {x0:.1f} {y0:.1f} Q {x0 + w * 0.5:.1f} {y0 - bow:.1f} {x0 + w:.1f} {y0 + rnd.uniform(-4, 4):.1f}'
        rip.append(f'<path d="{d}"/>')
        hi.append(f'<path d="{d}" transform="translate(0 -1.6)"/>')
    out.append(f'<g fill="none" stroke="#8E5A68" stroke-width="1.2" opacity="0.35">{"".join(rip)}</g>')
    out.append(f'<g fill="none" stroke="#F8CCA4" stroke-width="1" opacity="0.5">{"".join(hi)}</g>')
    out.append(dots(120, 62, (-10, 380, 610, 444), "#F8D0A8", r=(0.5, 1.2), opacity=(0.3, 0.7)))
    # caravan along the crest, long shadows thrown toward us
    cam = [(176, 372, 0.52, ("#2E4A7A", "#F2E6D0"), "#B8343A", "#2E5AA8", 0), (262, 366, 0.56, ("#E8DCC8", "#C8343A"), "#2E6A8A", "#E8B040", 1),
           (348, 367, 0.6, ("#5A3A5A", "#F2C040"), "#C86A2E", "#2E5A3A", 0)]
    for x, b, k, rider, bl, ts, st in cam:
        out.append(camel_shadow(x, b, k))
    # guide on foot leading the caravan
    out.append(f'<g transform="translate(134 376)"><path d="M -7 0 L -4 -34 L 6 -34 L 8 0 Z" fill="#F2E6D0"/><path d="M -4 -34 L -6 -48 Q 0 -54 6 -48 L 6 -34 Z" fill="#F2E6D0"/>'
               '<circle cx="0" cy="-56" r="5.5" fill="#5A3A2E"/><path d="M -6 -58 Q 0 -66 6 -58 L 7 -54 L -6 -54 Z" fill="#E8E0D0"/><path d="M 5 -46 Q 18 -40 34 -46" stroke="#2A1E1A" stroke-width="1.2" fill="none"/>'
               '<path d="M 6 -48 L 7 -2" stroke="#FFD8A0" stroke-width="1.8"/><path d="M 4 -60 Q 8 -56 6 -50" stroke="#FFD8A0" stroke-width="1.6" fill="none"/><rect x="-1" y="-30" width="2" height="30" fill="#E8DCC8" opacity="0"/></g>')
    out.append(camel_shadow(134 + 4, 376, 0.2, op=0.25))
    for x, b, k, rider, bl, ts, st in cam:
        out.append(camel(x, b, k, rider=rider, blanket=bl, tassel=ts, step=st))
    # footprints trailing behind the caravan
    out.append(f'<g fill="#8A5A6E" opacity="0.4">' + "".join(f'<ellipse cx="{x:.1f}" cy="{364 + (x - 400) * 0.02 + (3 if i % 2 else 0):.1f}" rx="2.4" ry="1.1"/>' for i, x in enumerate(range(390, 600, 12))) + "</g>")
    # a desert shrub
    out.append(f'<g stroke="#5A3A3A" stroke-width="1.4" fill="none" stroke-linecap="round">' + "".join(
        f'<path d="M 540 430 q {dx * 0.4:.1f} -10 {dx:.1f} -{h_:.1f}"/>' for dx, h_ in ((-14, 16), (-6, 22), (2, 24), (10, 18), (16, 12))) + "</g>")
    out.append(gulls([(220, 172, 10), (240, 182, 7), (540, 160, 8)], "#4A3450", 1.8))
    return "\n".join(out)


# ================================================================ SYDNEY — the Opera House and the Harbour Bridge at twilight
def shell(x0, x1, apex, base, u, k, glass=True, lean=1):
    """One sail shell: a broad convex back swelling up to the tip, a leading edge curving back down to the
    podium, chevron tile ribs converging on the tip, a glazed mouth glowing inside the leading edge.
    lean = +1 tip toward the right, -1 toward the left."""
    xa, ya = apex
    w = abs(x1 - x0)
    h = base - ya
    sg = 1 if lean > 0 else -1
    back = f"M {x0:.1f} {base:.1f} C {x0 + sg * w * 0.06:.1f} {base - h * 0.62:.1f} {xa - sg * w * 0.62:.1f} {ya + h * 0.04:.1f} {xa:.1f} {ya:.1f}"
    lead = f"C {xa + sg * w * 0.03:.1f} {ya + h * 0.4:.1f} {x1 + sg * w * 0.04:.1f} {base - h * 0.3:.1f} {x1:.1f} {base:.1f}"
    d = back + " " + lead + " Z"
    lo, hi_ = (x0, xa) if sg > 0 else (xa, x0)
    out = [defs(lg(u, [(0, "#B8A4C8"), (0.45, "#E8DCE2"), (0.8, "#FFF2EA"), (1, "#F8CDB4")], lo, 0, hi_ + 1, 0, units="userSpaceOnUse") if sg > 0 else
                lg(u, [(0, "#F8CDB4"), (0.2, "#FFF2EA"), (0.55, "#E8DCE2"), (1, "#B8A4C8")], lo, 0, hi_ + 1, 0, units="userSpaceOnUse"))]
    out.append(f'<path d="{d}" fill="url(#{u})"/>')
    cid = f"{u}-c"
    ribs, chev = [], []
    n = max(5, int(w / 7))
    for i in range(1, n):
        bx = lerp(x0, x1, i / n)
        ribs.append(f'<path d="M {bx:.1f} {base:.1f} Q {lerp(bx, xa, 0.5) - sg * w * 0.12:.1f} {lerp(base, ya, 0.55):.1f} {xa:.1f} {ya:.1f}"/>')
    for j in range(1, 9):
        t = j / 9
        yy = lerp(base, ya, t)
        chev.append(f'<path d="M {lerp(x0, xa, t ** 0.7) - sg * 4:.1f} {yy + 6:.1f} Q {lerp(lerp(x0, x1, 0.5), xa, t):.1f} {yy - 4:.1f} {lerp(x1, xa, t) + sg * 4:.1f} {yy + 8:.1f}"/>')
    glass_svg = ""
    if glass:
        glass_svg = (f'<path d="M {xa:.1f} {ya:.1f} {lead}" fill="none" stroke="#E89A50" stroke-width="{w * 0.12:.1f}" opacity="0.95"/>'
                     f'<path d="M {xa:.1f} {ya:.1f} {lead}" fill="none" stroke="#FFD890" stroke-width="{w * 0.04:.1f}" opacity="0.8" transform="translate({-sg * w * 0.05:.1f} 0)"/>')
    out.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})" fill="none" stroke-width="0.8">'
               f'<g stroke="#A898B8" opacity="0.5">{"".join(ribs)}</g><g stroke="#B8A8C0" opacity="0.4">{"".join(chev)}</g>{glass_svg}</g>')
    out.append(f'<path d="M {xa:.1f} {ya:.1f} {lead}" fill="none" stroke="#FFE4CC" stroke-width="{max(1.2, 1.6 * k):.1f}" stroke-linecap="round"/>')
    out.append(f'<path d="{back}" fill="none" stroke="#F4ECF0" stroke-width="1.2" opacity="0.7"/>')
    return "".join(out)


def harbour_bridge(xs, xn, deck_s, deck_n, top_s, top_n, u):
    """Steel through-arch with granite pylon pairs, seen at an angle (south end nearer, on the left)."""
    out = []
    sil = "#22244A"
    # arch chords: parabola between the pylons
    def chord(t, lift):
        x = lerp(xs, xn, t)
        base = lerp(deck_s, deck_n, t)
        span_top = lerp(top_s, top_n, t)
        y = base - (base - span_top) * (1 - (2 * t - 1) ** 2) * lift
        return x, y
    upper = [chord(i / 60, 1.0) for i in range(61)]
    lower = [chord(i / 60, 0.74) for i in range(61)]
    lower = [(x, y + lerp(10, 7, i / 60)) for i, (x, y) in enumerate(lower)]
    out.append(Q(upper + lower[::-1], sil))
    web = []
    for i in range(0, 60, 2):
        (xa, ya), (xb, yb) = upper[i], lower[i]
        (xc, yc), (xd, yd) = upper[i + 2], lower[i + 2]
        web.append(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xd:.1f}" y2="{yd:.1f}"/><line x1="{xb:.1f}" y1="{yb:.1f}" x2="{xc:.1f}" y2="{yc:.1f}"/>')
    out.append(f'<g stroke="#5A4E7A" stroke-width="0.9" opacity="0.8">{"".join(web)}</g>')
    out.append(f'<polyline points="{P(upper)}" fill="none" stroke="#F6A07E" stroke-width="1.6" opacity="0.9"/>')
    # hangers down to the deck where the arch rises above it
    hang = []
    for i in range(6, 56, 2):
        x, y = lower[i]
        dy = lerp(deck_s, deck_n, i / 60)
        if y < dy - 3:
            hang.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{dy:.1f}"/>')
    out.append(f'<g stroke="{sil}" stroke-width="1.2">{"".join(hang)}</g>')
    # deck with its row of lights, approach spans beyond the pylons
    out.append(Q([(xs - 60, deck_s + 2), (xn + 40, deck_n + 1), (xn + 40, deck_n + 6), (xs - 60, deck_s + 9)], sil))
    out.append(dots(0, 0, (0, 0, 0, 0), "#000"))
    for i in range(46):
        t = i / 45
        x = lerp(xs - 50, xn + 30, t)
        y = lerp(deck_s + 3, deck_n + 2, t)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{lerp(1.4, 1.0, t):.1f}" fill="#FFE2A0"/>')
    for x, y in upper[4:57:4]:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1" fill="#FFD0A0" opacity="0.8"/>')
    # pylon pairs
    for (x, deck, h, w) in ((xs, deck_s, (deck_s - top_s) * 0.52, 24), (xn, deck_n, (deck_n - top_n) * 0.52, 16)):
        ytop = deck - h
        out.append(f'<rect x="{x - w / 2:.1f}" y="{ytop:.1f}" width="{w:.1f}" height="{deck + 30 - ytop:.1f}" fill="#4A3E5A"/>')
        out.append(f'<rect x="{x - w / 2:.1f}" y="{ytop:.1f}" width="{w * 0.35:.1f}" height="{deck + 30 - ytop:.1f}" fill="#E8A888" opacity="0.35"/>')
        out.append(f'<rect x="{x - w / 2 - 1:.1f}" y="{ytop:.1f}" width="{w + 2:.1f}" height="{w * 0.18:.1f}" fill="#5A4E6A"/>')
        out.append(f'<rect x="{x - w * 0.2:.1f}" y="{ytop + h * 0.25:.1f}" width="{w * 0.4:.1f}" height="{h * 0.3:.1f}" fill="#2A2440"/>')
        out.append(f'<g stroke="#2A2440" stroke-width="0.8" opacity="0.6">' + "".join(f'<line x1="{x - w / 2:.1f}" y1="{ytop + j * 5:.1f}" x2="{x + w / 2:.1f}" y2="{ytop + j * 5:.1f}"/>' for j in range(1, int((deck + 30 - ytop) / 5))) + "</g>")
    return "".join(out)


def ferry(x, wl, k, flip=False):
    """Green-and-cream harbour ferry in profile, bow left, windows lit."""
    sx = -k if flip else k
    g = [f'<g transform="translate({x:.1f} {wl:.1f}) scale({sx:.3f} {k:.3f})">',
         '<path d="M -50 -2 Q -52 -9 -46 -12 L 48 -12 Q 52 -9 50 -2 Q 0 3 -50 -2 Z" fill="#1E5A3A"/>',
         '<rect x="-46" y="-12" width="94" height="2.4" fill="#F2C040"/>',
         '<path d="M -40 -12 L -38 -24 L 40 -24 L 42 -12 Z" fill="#F2EAD6"/>',
         '<rect x="-34" y="-21" width="70" height="6" fill="#FFD98E"/>',
         '<g stroke="#B8A880" stroke-width="1">' + "".join(f'<line x1="{-34 + i * 7}" y1="-21" x2="{-34 + i * 7}" y2="-15"/>' for i in range(1, 10)) + "</g>",
         '<path d="M -34 -24 L -30 -31 L 30 -31 L 34 -24 Z" fill="#1E5A3A"/><rect x="-26" y="-30" width="52" height="4" fill="#FFE2A8"/>',
         '<rect x="-6" y="-38" width="12" height="7" fill="#F2EAD6"/><rect x="-4" y="-36.5" width="8" height="3" fill="#FFE2A8"/>',
         '<rect x="10" y="-37" width="4" height="7" fill="#F2C040"/><rect x="9.6" y="-38" width="4.8" height="1.4" fill="#1E1E1E"/>',
         '<path d="M -46 -12 L -40 -24" stroke="#FFE0C8" stroke-width="1.2"/>',
         "</g>"]
    return "".join(g)


def sydney():
    u = "sy"
    hz = 300
    out = [defs(
        lg(f"{u}-sky", [(0, "#24285E"), (0.28, "#4A3E7E"), (0.52, "#9A5288"), (0.7, "#E0707A"), (0.85, "#F6A070"), (1, "#FBCB86")], 0, 0, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#E8968A"), (0.12, "#9A5A8A"), (0.4, "#3E3A76"), (1, "#18204A")], 0, hz, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-pod", [(0, "#C88A72"), (1, "#7A4E52")], 0, 280, 0, 330, units="userSpaceOnUse"),
        lg(f"{u}-rock", [(0, "#C8906A"), (1, "#6A4440")], 0, 380, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="{hz + 1}" fill="url(#{u}-sky)"/>')
    out.append(dots(40, 4, (0, 40, 600, 140), "#F6F0E0", r=(0.6, 1.3), opacity=(0.4, 1)))
    out.append(glow(430, 296, 330, "#FFC08A", f"{u}-g1", 0.75))
    out.append(glow(430, 296, 90, "#FFE8B8", f"{u}-g2", 0.9))
    for x, y, w, c in ((450, 150, 120, "#E8809A"), (540, 172, 70, "#F29A8E"), (380, 206, 90, "#F6A88A"), (500, 232, 110, "#FFC08E"), (120, 120, 90, "#8A5A9A"), (220, 168, 70, "#B8689A")):
        out.append(streak_cloud(x, y, w, c, 0.65, 4))
        out.append(streak_cloud(x - w * 0.15, y + 2.5, w * 0.6, "#FFE0C0", 0.45, 1.4))
    # North Shore beyond the bridge, the city towers behind the Opera House
    poly, _ = ridge_poly([(300, 290), (380, 282), (460, 286), (540, 280), (610, 284)], 5, base=hz + 1, amp=3, fill="#6A4A7E")
    out.append(poly)
    out.append(dots(50, 6, (300, 282, 610, 298), "#FFD98E", r=(0.6, 1.1), opacity=(0.5, 1)))
    rnd = random.Random(9)
    towers = []
    x = -10
    while x < 250:
        w = rnd.uniform(14, 30)
        h = rnd.uniform(40, 150)
        towers.append((x, w, h))
        x += w + rnd.uniform(-2, 4)
    for x, w, h in towers:
        top = hz - h
        out.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{rnd.choice(["#2E2E5E", "#34346A", "#3A3870"])}"/>')
        out.append(f'<rect x="{x + w * 0.7:.1f}" y="{top:.1f}" width="{w * 0.3:.1f}" height="{h:.1f}" fill="#E07A8A" opacity="0.18"/>')
        for yy in range(int(top) + 4, hz - 2, 5):
            for xx in range(int(x) + 2, int(x + w) - 2, 4):
                if rnd.random() < 0.3:
                    out.append(f'<rect x="{xx}" y="{yy}" width="2" height="2.4" fill="#FFD98E" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    out.append('<g><rect x="96" y="150" width="5" height="150" fill="#2E2E5E"/><path d="M 90 150 L 107 150 L 105 132 L 92 132 Z" fill="#C89A5A"/><rect x="90" y="140" width="17" height="2" fill="#FFE2A0"/>'
               '<rect x="91" y="146" width="15" height="1.6" fill="#FFE2A0"/><rect x="97.6" y="104" width="1.8" height="28" fill="#2E2E5E"/><circle cx="98.5" cy="104" r="1.8" fill="#FF6A6A"/></g>')
    out.append(mist(120, 290, 200, 26, "#C87AA0", f"{u}-cm", 0.35))
    # the bridge behind, the sun just gone down beyond it
    out.append(harbour_bridge(300, 528, 244, 252, 150, 178, u))
    # sea
    out.append(f'<rect x="0" y="{hz}" width="600" height="{444 - hz}" fill="url(#{u}-sea)"/>')
    rnd = random.Random(14)
    for i in range(110):
        y = hz + 2 + rnd.random() ** 1.5 * 140
        k = (y - hz) / 140
        x = 430 + rnd.gauss(0, 30 + k * 90)
        w = rnd.uniform(6, 26) * (0.5 + k)
        out.append(f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{0.8 + k * 1.4:.1f}" rx="1" fill="{rnd.choice(["#FFD0A0", "#FFE2B8", "#F6A88A"])}" opacity="{(1 - k * 0.6) * rnd.uniform(0.4, 0.9):.2f}"/>')
    for i in range(46):  # bridge lights reflected
        x = lerp(250, 560, i / 45) + rnd.uniform(-3, 3)
        out.append(f'<rect x="{x - 0.8:.1f}" y="{hz + 4:.1f}" width="1.6" height="{rnd.uniform(10, 40):.1f}" fill="#FFE2A0" opacity="0.3"/>')
    # Opera House: podium, far row of shells (concert hall), near row (theatre), restaurant shells
    out.append(Q([(40, 300), (60, 288), (330, 284), (352, 292), (352, 318), (40, 322)], f"url(#{u}-pod)"))
    out.append(f'<g stroke="#5A3A40" stroke-width="0.8" opacity="0.5">' + "".join(f'<line x1="40" y1="{300 + j * 4}" x2="352" y2="{294 + j * 4}"/>' for j in range(1, 6)) + "</g>")
    for j in range(8):
        out.append(f'<rect x="{38 + j * 2}" y="{291 + j * 3.2:.1f}" width="{70 - j * 2}" height="1.4" fill="#F2C0A0" opacity="0.7"/>')
    out.append(dots(26, 3, (60, 296, 340, 300), "#FFE2A0", r=(0.8, 1.3), opacity=(0.7, 1)))
    # concert hall (far row), restaurant shells, then the theatre (near row); tips lean north, to the right
    out.append(shell(98, 60, (48, 256), 290, f"{u}-r2", 0.7, glass=False, lean=-1))
    out.append(shell(142, 80, (68, 234), 289, f"{u}-fd", 0.8, glass=False, lean=-1))
    out.append(shell(104, 184, (192, 210), 288, f"{u}-fc", 0.9))
    out.append(shell(134, 236, (250, 182), 288, f"{u}-fb", 1.0))
    out.append(shell(178, 300, (316, 156), 288, f"{u}-fa", 1.2))
    out.append(shell(168, 112, (100, 242), 293, f"{u}-nd", 0.8, glass=False, lean=-1))
    out.append(shell(132, 208, (214, 224), 293, f"{u}-nc", 0.9))
    out.append(shell(164, 260, (274, 198), 293, f"{u}-nb", 1.0))
    out.append(shell(210, 332, (344, 172), 293, f"{u}-na", 1.2))
    out.append(f'<rect x="40" y="292" width="312" height="2.2" fill="#F2C8A8" opacity="0.7"/>')
    # reflections of the shells and the podium lights
    for i in range(24):
        y = 324 + i * 2.8
        for x0, x1 in ((96, 200), (180, 330)):
            w = (x1 - x0) * (1 - i / 30) * rnd.uniform(0.6, 1)
            out.append(f'<rect x="{(x0 + x1) / 2 - w / 2 + rnd.uniform(-6, 6):.1f}" y="{y:.1f}" width="{w:.1f}" height="1.4" rx="0.7" fill="#F6E2D8" opacity="{0.4 * (1 - i / 26):.2f}"/>')
    out.append(f'<rect x="40" y="320" width="312" height="5" fill="#FFD98E" opacity="0.25"/>')
    out.append(water_lines(90, 15, (0, 304, 600, 444), ["#6A5A9A", "#2A2E66", "#C87A9A"], w=(10, 44), h=(0.8, 2), opacity=(0.25, 0.6)))
    # ferries crossing, a yacht near the bridge
    out.append(f'<path d="M 520 386 Q 580 392 640 390" fill="none" stroke="#F2EAD6" stroke-width="2" opacity="0.5"/><path d="M 518 388 Q 560 400 610 404" fill="none" stroke="#F2EAD6" stroke-width="1.4" opacity="0.35"/>')
    out.append(water_lines(30, 18, (404, 388, 512, 412), ["#FFD98E", "#F2EAD6"], w=(6, 24), h=(0.8, 1.6), opacity=(0.3, 0.7)))
    out.append(ferry(458, 386, 1.2))
    out.append(ferry(250, 336, 0.55, flip=True))
    out.append(f'<path d="M 278 336 Q 300 338 320 337" fill="none" stroke="#F2EAD6" stroke-width="1.2" opacity="0.5"/>')
    out.append('<path d="M 560 318 L 560 290 L 572 316 Z" fill="#F6E2D8"/><path d="M 558 318 L 556 296 L 548 316 Z" fill="#E8C8C8"/><path d="M 546 318 L 576 318 L 572 322 L 550 322 Z" fill="#2A2440"/>')
    # sandstone rocks of the point in the foreground, a gull on watch
    rk = rough([(-10, 404), (40, 392), (90, 398), (140, 414), (190, 432), (230, 444)], 71, amp=6, depth=3)
    out.append(Q(rk + [(-10, 444)], f"url(#{u}-rock)"))
    out.append(f'<polyline points="{P(rk)}" fill="none" stroke="#FFC898" stroke-width="2" opacity="0.8"/>')
    out.append(f'<clipPath id="{u}-rk"><polygon points="{P(rk + [(-10, 444)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-rk)">' + "".join(
        f'<polyline points="{P([(x + 0, y + 6 + j * 7) for x, y in rk])}" fill="none" stroke="{c}" stroke-width="{w_}" opacity="0.5"/>' for j, (c, w_) in enumerate((("#E8A878", 2.4), ("#7A4A44", 1.4), ("#D8986E", 3), ("#6A3E3E", 1.2), ("#C8885E", 2.6))))
        + blobs(40, 72, (-10, 396, 230, 444), ["#8A5A4A", "#E8B088", "#5A3A3A"], r=(1.5, 4), opacity=(0.3, 0.6), squash=0.5) + "</g>")
    out.append('<g transform="translate(66 394)"><path d="M -10 -6 Q -4 -12 6 -10 L 12 -8 L 6 -4 Q -2 -2 -10 -6 Z" fill="#F2EEEA"/><path d="M -10 -6 Q -14 -6 -16 -4" stroke="#F2EEEA" stroke-width="2.4" stroke-linecap="round"/>'
               '<path d="M -2 -10 Q 4 -12 10 -8 L 4 -6 Z" fill="#8A8A9A"/><circle cx="-12" cy="-9" r="3.4" fill="#F2EEEA"/><path d="M -15 -9 L -19 -8" stroke="#F2B040" stroke-width="1.6"/>'
               '<path d="M -2 -3 L -2 2 M 2 -3 L 2 2" stroke="#E8A040" stroke-width="1.2"/><path d="M -10 -11 Q -8 -12 -6 -10" stroke="#FFC898" stroke-width="1.2" fill="none"/></g>')
    out.append(gulls([(300, 120, 11), (322, 132, 8), (500, 110, 9)], "#2A2450", 1.8))
    return "\n".join(out)


BUILD = {
    "japan": (japan, "JAPAN", "MOUNT FUJI · HONSHU", "#7E2420", "#F4A9BC", "#FFF1EC", "#F7C6D2"),
    "santorini": (santorini, "SANTORINI", "GREECE · CYCLADES", "#1E3E7E", "#F7A46E", "#FFF4EC", "#F9C690"),
    "rome": (rome, "ROME", "ITALIA · EST. 753 BC", "#6E2A22", "#F2A65E", "#FCEBD5", "#F4B874"),
    "london": (london, "LONDON", "ENGLAND · UNITED KINGDOM", "#141C3E", "#D8323A", "#F6EFE0", "#F2C878"),
    "venice": (venice, "VENICE", "ITALIA · LA SERENISSIMA", "#7E2A34", "#F2C46D", "#FDF0E0", "#F2C46D"),
    "cairo": (cairo, "CAIRO", "EGYPT · PYRAMIDS OF GIZA", "#4A2E2A", "#F28C38", "#FCEBD5", "#F9C98A"),
    "sydney": (sydney, "SYDNEY", "AUSTRALIA · HARBOUR CITY", "#1E2450", "#F6A070", "#FFF4EC", "#FBC886"),
    "paris": (paris, "PARIS", "FRANCE · CITY OF LIGHT", "#2E3550", "#F2B872", "#FBEBD4", "#F2C58A"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("world", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
