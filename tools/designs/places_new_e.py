"""American Places, painted edition, batch E: mountains, lakes, ridges, vineyards and the Big Sur coast.

Each poster is its own small gouache painting with a time of day, a light direction, atmospheric depth
and truthful details of the place. Run: python3 places_new_e.py [slug ...]
"""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from places_painted import Cam, puff_column
from poster import poster


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


# ================================================================ shared painting helpers
def Pi(pts):
    """Compact points (integer pixels) for small, numerous shapes."""
    return " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)


def con(x, base, h, color, seed, lean=0.0, width=0.30, light=None):
    """Compact spruce silhouette (same drawing as paint.conifer, fewer and rounded points) for big forests."""
    rnd = random.Random(seed)
    levels = max(5, int(h / 6))
    left, right = [], []
    maxw = h * width / 2
    for i in range(levels + 1):
        t = i / levels
        y = base - h * 0.08 - t * h * 0.92
        cx = x + lean * t * h * 0.08
        step = h * 0.92 / levels
        w = maxw * (1 - t) ** 0.85 * rnd.uniform(0.62, 1.05) + 1.2
        left += [(cx - w, y), (cx - w * rnd.uniform(0.5, 0.75), y - step * 0.55)]
        w2 = maxw * (1 - t) ** 0.85 * rnd.uniform(0.62, 1.05) + 1.2
        right += [(cx + w2, y - step * 0.2), (cx + w2 * rnd.uniform(0.5, 0.75), y - step * 0.7)]
    tip = (x + lean * h * 0.08, base - h)
    pts = [(x - 1.5, base)] + left + [tip] + right[::-1] + [(x + 1.5, base)]
    pp = Pi(pts) if h < 40 else P(pts)
    out = f'<polygon points="{pp}" fill="{color}"/>'
    if light:
        out += f'<polygon points="{Pi([(x, base - h * 0.08)] + left + [tip])}" fill="{light}" opacity="0.5"/>'
    return out


def trees_on(line, seed, colors, density=0.5, hmin=10, hmax=22, xmin=-10, xmax=610, sink=2, light=None):
    rnd = random.Random(seed)
    out = []
    xs = sorted(rnd.uniform(xmin, xmax) for _ in range(int((xmax - xmin) * density / 6)))
    for x in xs:
        y = y_on(line, x)
        if y is None:
            continue
        out.append(con(x, y + sink, rnd.uniform(hmin, hmax), rnd.choice(colors), rnd.random(), light=light))
    return "".join(out)


def inside(poly, x, y):
    """Point-in-polygon (even-odd)."""
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def massif(u, ctrl, seed, base, rock, shade="#2E2A55", shade_op=0.5, amp=10, depth=5, decay=0.55, light=1,
           snow=None, snow_y=None, snow_amp=30, snow_shade=None, ledges=None, rim=None, rim_w=2.2, haze=None, haze_top=None,
           tex=("#000000",), tex_op=(0.06, 0.18), tex_n=1.0, gullies=0, strata=None, spine_k=0.18):
    """A mountain mass painted in layers: rock fill, texture streaks, snow fields, a shadow facet on the far
    side of every peak, gullies, rim light on the sunlit ridges, then haze at the foot.
    light = 1 means the sun is on the left (right faces in shadow), -1 the opposite.
    Returns (svg, ridgeline)."""
    line = rough(ctrl, seed, amp, depth, decay)
    poly = line + [(line[-1][0], base), (line[0][0], base)]
    cid = f"{u}-c"
    xs = [x for x, _ in line]
    top = min(y for _, y in line)
    box = (min(xs), top, max(xs), base)
    out = [f'<clipPath id="{cid}"><polygon points="{P(poly)}"/></clipPath>',
           f'<polygon points="{P(poly)}" fill="{rock}"/>']
    g = []
    rnd = random.Random(seed * 7 + 1)
    if strata:
        # tilted sedimentary bands: (colour, opacity, angle_slope, count)
        col, op, slope, n = strata
        for i in range(n):
            y0 = top + (base - top) * i / n + rnd.uniform(-6, 6)
            th = rnd.uniform(2, 7)
            pts_a = rough([(box[0] - 20, y0 + slope * (box[0] - 20 - 300)), (box[2] + 20, y0 + slope * (box[2] + 20 - 300))], seed + i, 5, 4)
            pts_b = [(x, y + th + rnd.uniform(-1.5, 1.5)) for x, y in pts_a]
            g.append(f'<polygon points="{P(pts_a + pts_b[::-1])}" fill="{col}" opacity="{op * rnd.uniform(0.6, 1.2):.2f}"/>')
    if tex_n:
        g.append(streaks(int((box[2] - box[0]) * (base - top) / 300 * tex_n), seed + 3, box, list(tex), w=(1.2, 3.5),
                         length=(12, 60), opacity=tex_op, slant=0.3))
    if snow:
        # snow fields: from the ridgeline down to a ragged snowline with fingers running down the gullies
        sl = []
        for i, (x, y) in enumerate(line):
            d = snow_y + snow_amp * (math.sin(x * 0.09 + seed) * 0.5 + math.sin(x * 0.23 + seed * 2) * 0.35)
            d += rnd.uniform(0, snow_amp) if rnd.random() < 0.35 else 0
            sl.append((x, max(y, d)))
        g.append(f'<polygon points="{P(line + sl[::-1])}" fill="{snow}"/>')
        # stray snow streaks below the line
        g.append(streaks(int((box[2] - box[0]) / 12), seed + 9, (box[0], snow_y - 10, box[2], snow_y + snow_amp * 1.4), [snow],
                         w=(0.8, 2), length=(8, 26), opacity=(0.5, 0.85), slant=0.35))
    if ledges:
        # snow caught on ledges of the tilted strata: (count, slope, y_min, y_max, colour)
        n, slope, ya, yb, col = ledges
        for i in range(n):
            x0 = rnd.uniform(box[0] + 30, box[2] - 60)
            y0 = rnd.uniform(ya, yb)
            L = rnd.uniform(16, 52)
            m = 6
            tpts = rough([(x0, y0), (x0 + L, y0 + slope * L)], seed + 200 + i, 3, 3)
            th = rnd.uniform(1.8, 4.2)
            bpts = [(x, y + th * math.sin(math.pi * k / (len(tpts) - 1)) + 0.3) for k, (x, y) in enumerate(tpts)]
            g.append(f'<polygon points="{P(tpts + bpts[::-1])}" fill="{col}" opacity="{rnd.uniform(0.75, 1):.2f}"/>')
    # shadow facets
    peaks = [i for i in range(1, len(ctrl) - 1) if ctrl[i][1] <= ctrl[i - 1][1] and ctrl[i][1] <= ctrl[i + 1][1]]
    for k, i in enumerate(peaks):
        px, py = ctrl[i]
        j = i + light
        vx = ctrl[j][0]
        h = base - py
        spine = rough([(px, py), (px + light * h * spine_k * 0.6, py + h * 0.4), (px + light * h * spine_k * 0.2, base + 6)], seed + 31 * k, 9, 4)
        seg = [p for p in line if (px < p[0] <= vx if light > 0 else vx <= p[0] < px)]
        if light < 0:
            seg = seg[::-1]
        shadow = spine[::-1] + seg + [(vx, base + 6)]
        g.append(f'<polygon points="{P(shadow)}" fill="{shade}" opacity="{shade_op}"/>')
        if snow_shade:
            g.append(f'<polygon points="{P(shadow)}" fill="{snow_shade}" opacity="0.18"/>')
    # gullies: dark descending clefts with a lit lip
    for k in range(gullies):
        x = rnd.uniform(box[0] + 20, box[2] - 20)
        y = y_on(line, x)
        if y is None:
            continue
        L = (base - y) * rnd.uniform(0.3, 0.75)
        pts = rough([(x, y + 2), (x + rnd.uniform(-14, 14), y + L * 0.5), (x + rnd.uniform(-24, 24), y + L)], seed + 100 + k, 6, 3)
        w = rnd.uniform(1.5, 3.2)
        right = [(px_ + w * (1 - t / len(pts)), py_) for t, (px_, py_) in enumerate(pts)]
        g.append(f'<polygon points="{P(pts + right[::-1])}" fill="{shade}" opacity="{shade_op * 0.9:.2f}"/>')
    if haze:
        hid = f"{u}-hz"
        out.append(defs(lg(hid, [(0, haze, 0), (1, haze, 0.9)], 0, haze_top if haze_top is not None else top + (base - top) * 0.4, 0, base, units="userSpaceOnUse")))
        g.append(f'<rect x="-20" y="{top:.0f}" width="640" height="{base - top + 10:.0f}" fill="url(#{hid})"/>')
    out.append(f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>")
    if rim:
        # light catching the sunlit side of every summit ridge
        segs = []
        for i in peaks:
            px, py = ctrl[i]
            vx = ctrl[i - light][0]
            seg = [p for p in line if (vx <= p[0] <= px if light > 0 else px <= p[0] <= vx)]
            if len(seg) > 1:
                segs.append(f'<polyline points="{P(seg)}"/>')
        out.append(f'<g fill="none" stroke="{rim}" stroke-width="{rim_w}" stroke-linejoin="round" stroke-linecap="round" opacity="0.9">' + "".join(segs) + "</g>")
    return "".join(out), line


def forest_fill(poly, seed, colors, n, hmin, hmax, light=None, ybias=1.0, trunk=None):
    """Scatter conifers inside a polygon, drawn back to front; nearer (lower) trees are taller."""
    rnd = random.Random(seed)
    xs = [x for x, _ in poly]
    ys = [y for _, y in poly]
    pts = []
    tries = 0
    while len(pts) < n and tries < n * 30:
        tries += 1
        x, y = rnd.uniform(min(xs), max(xs)), rnd.uniform(min(ys), max(ys))
        if inside(poly, x, y):
            pts.append((x, y))
    pts.sort(key=lambda p: p[1])
    y0, y1 = min(ys), max(ys)
    out = []
    for x, y in pts:
        t = ((y - y0) / max(1, y1 - y0)) ** ybias
        h = hmin + (hmax - hmin) * t * rnd.uniform(0.7, 1.1)
        out.append(con(x, y, h, rnd.choice(colors), rnd.random(), light=light))
    return "".join(out)


def leafy(cx, cy, rx, ry, seed, dark, mid, light, n=26, lx=-0.45, ly=-0.5, spark=None, dab=0.2, rot=True):
    """A crown of foliage painted with many small leaf dabs: shadow mass, mid tone, then sunlit dabs pushed
    toward the light (lx, ly)."""
    rnd = random.Random(seed)
    out = []
    for col, k, sh, rr in ((dark, int(n * 2.2), -0.1, dab * 1.15), (mid, int(n * 1.8), 0.08, dab), (light, int(n * 1.1), 0.3, dab * 0.8)):
        g = []
        for _ in range(k):
            a = rnd.uniform(0, 2 * math.pi)
            d = math.sqrt(rnd.random()) * 0.85
            x = cx + rx * d * math.cos(a) + rx * sh * lx
            y = cy + ry * d * math.sin(a) + ry * sh * ly
            r = min(rx, ry) * rr * rnd.uniform(0.7, 1.3)
            if rot:
                g.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r * 1.25:.1f}" ry="{r * 0.85:.1f}" transform="rotate({rnd.uniform(-40, 40):.0f} {x:.0f} {y:.0f})"/>')
            else:
                g.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}"/>')
        out.append(f'<g fill="{col}">' + "".join(g) + "</g>")
    if spark:
        out.append(dots(int(n * 0.6), seed + 1, (cx - rx * 0.7, cy - ry * 0.7, cx + rx * 0.3, cy + ry * 0.1), spark, r=(0.8, 1.8), opacity=(0.5, 1)))
    return "".join(out)


def grove(poly, seed, n, rmin, rmax, colors=(("#9A5A1E", "#D8962A", "#F4C84E"),), trunk="#D8D0C4", light=-1, conifers=None, ncon=0):
    """A stand of small deciduous crowns (and optional conifers) filling a slope polygon, back to front."""
    rnd = random.Random(seed)
    xs = [x for x, _ in poly]
    ys = [y for _, y in poly]
    pts = []
    tries = 0
    while len(pts) < n + ncon and tries < (n + ncon) * 40:
        tries += 1
        x, y = rnd.uniform(min(xs), max(xs)), rnd.uniform(min(ys), max(ys))
        if inside(poly, x, y):
            pts.append((x, y, len(pts) < ncon))
    pts.sort(key=lambda p: p[1])
    y0, y1 = min(ys), max(ys)
    out = []
    for x, y, is_con in pts:
        t = (y - y0) / max(1, y1 - y0)
        r = rmin + (rmax - rmin) * t * rnd.uniform(0.7, 1.15)
        if is_con:
            out.append(con(x, y + r * 0.4, r * 3.2, rnd.choice(conifers), rnd.random()))
            continue
        d, m, l_ = rnd.choice(colors)
        out.append(f'<rect x="{x - r * 0.08:.0f}" y="{y - r * 0.6:.0f}" width="{max(0.8, r * 0.16):.1f}" height="{r:.0f}" fill="{trunk}"/>')
        out.append(leafy(x, y - r * 1.15, r * 0.75, r * 1.0, rnd.randrange(10 ** 6), d, m, l_, n=3, lx=light * 0.5, ly=-0.5, dab=0.36, rot=False))
    return "".join(out)


def aspen(x, base, h, seed, gold=("#B8761E", "#E2A12C", "#F7D25A"), lean=0.0, bark="#EDE7DA", light=-1):
    """Quaking aspen: slender pale trunk with dark eyes, a narrow golden crown of leaf clusters."""
    rnd = random.Random(seed)
    w = max(1.6, h * 0.035)
    tx = x + lean * h
    out = [f'<path d="M {x - w:.1f} {base:.1f} Q {x + lean * h * 0.4 - w * 0.6:.1f} {base - h * 0.5:.1f} {tx - w * 0.35:.1f} {base - h * 0.95:.1f} '
           f'L {tx + w * 0.35:.1f} {base - h * 0.95:.1f} Q {x + lean * h * 0.4 + w * 0.6:.1f} {base - h * 0.5:.1f} {x + w:.1f} {base:.1f} Z" fill="{bark}"/>',
           f'<path d="M {x + w * 0.2:.1f} {base:.1f} Q {x + lean * h * 0.4 + w * 0.3:.1f} {base - h * 0.5:.1f} {tx + w * 0.1:.1f} {base - h * 0.95:.1f} '
           f'L {tx + w * 0.35:.1f} {base - h * 0.95:.1f} Q {x + lean * h * 0.4 + w * 0.6:.1f} {base - h * 0.5:.1f} {x + w:.1f} {base:.1f} Z" fill="#9A9488" opacity="0.6"/>']
    for _ in range(int(h / 9)):
        t = rnd.uniform(0.05, 0.6)
        yy = base - h * t
        xx = x + lean * h * t * 0.6
        out.append(f'<path d="M {xx - w * 0.8:.1f} {yy:.1f} q {w * 0.8:.1f} {-w * 0.5:.1f} {w * 1.5:.1f} 0" stroke="#3A3430" stroke-width="{max(0.8, w * 0.35):.1f}" fill="none" stroke-linecap="round"/>')
    # a few twigs, then an irregular crown of three or four lobes with gaps
    for k in range(4):
        t = 0.45 + 0.12 * k
        bx, by = x + lean * h * t, base - h * t
        out.append(f'<path d="M {bx:.1f} {by:.1f} q {(-1) ** k * h * 0.06:.1f} {-h * 0.04:.1f} {(-1) ** k * h * 0.12:.1f} {-h * 0.1:.1f}" stroke="{bark}" stroke-width="{max(1, w * 0.4):.1f}" fill="none" stroke-linecap="round"/>')
    lobes = [(0, 0.78, 0.17, 0.2), (-0.09, 0.62, 0.14, 0.16), (0.1, 0.58, 0.13, 0.15), (0.02, 0.45, 0.12, 0.12)]
    for k, (ox, oy, rx, ry) in enumerate(lobes[: 3 + (seed % 2)]):
        out.append(leafy(x + lean * h * oy + ox * h * rnd.uniform(0.8, 1.2), base - h * oy, h * rx, h * ry, seed + 3 + k, gold[0], gold[1], gold[2],
                         n=max(8, int(h * 0.1)), lx=light * 0.6, ly=-0.5, dab=0.2))
    return "".join(out)


def figure(x, base, h, body="#2A2A34", head="#1E1A1E", pack=None, pole=False, flip=1):
    """Small standing person silhouette (hiker), h = total height."""
    k = h / 100
    out = [f'<g transform="translate({x:.1f} {base:.1f}) scale({k * flip:.3f} {k:.3f})">',
           '<path d="M -9 -44 L -11 0 L -4 0 L 0 -30 L 4 0 L 11 0 L 9 -44 Z" fill="#1E1C24"/>',
           f'<path d="M -12 -82 Q 0 -90 12 -82 L 11 -42 L -11 -42 Z" fill="{body}"/>',
           f'<circle cx="0" cy="-92" r="9" fill="{head}"/>']
    if pack:
        out.append(f'<rect x="8" y="-84" width="12" height="30" rx="4" fill="{pack}"/>')
    if pole:
        out.append('<path d="M -12 -66 L -22 0" stroke="#1E1C24" stroke-width="3" stroke-linecap="round"/>')
    out.append("</g>")
    return "".join(out)


def ripple_lines(n, seed, box, color, op=(0.3, 0.8), w=(8, 40), sw=1.4):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        y = rnd.uniform(y0, y1)
        t = (y - y0) / max(1, y1 - y0)
        ww = rnd.uniform(*w) * (0.5 + t)
        x = rnd.uniform(x0, x1)
        out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + ww:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="{sw * (0.6 + t):.1f}" opacity="{rnd.uniform(*op):.2f}" stroke-linecap="round"/>')
    return "".join(out)


def mirror(y, content, clip, op=0.8):
    """Reflection of `content` about the horizontal line y, clipped to the water."""
    return (f'<g clip-path="url(#{clip})" opacity="{op}"><g transform="translate(0 {2 * y:.1f}) scale(1 -1)">{content}</g></g>')


def birds_v(spec, color, sw=2):
    return f'<g fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round">' + "".join(
        f'<path d="M {x} {y} q {s * 0.5:.1f} {-s * 0.4:.1f} {s:.1f} 0 q {s * 0.5:.1f} {-s * 0.4:.1f} {s:.1f} 0"/>' for x, y, s in spec) + "</g>"


def falling_leaves(spec, seed):
    rnd = random.Random(seed)
    out = []
    for x, y, s, col in spec:
        a = rnd.uniform(0, 180)
        out.append(f'<g transform="translate({x} {y}) rotate({a:.0f}) scale({s})"><path d="M 0 -6 Q 5 -1 0 6 Q -5 -1 0 -6 Z" fill="{col}"/>'
                   f'<line x1="0" y1="-5" x2="0" y2="5" stroke="#7A4A1A" stroke-width="0.8" opacity="0.6"/></g>')
    return "".join(out)


# ================================================================ Rocky Mountains (Maroon Bells at first light)
def rocky_mountains():
    u = "rkm"
    SH = 318  # lake shoreline
    out = [defs(
        lg(f"{u}-sky", [(0, "#2E4C86"), (0.45, "#6F8CC0"), (0.78, "#E9B9A6"), (1, "#F6D9B0")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-rock", [(0, "#F4946A"), (0.3, "#C85E4E"), (1, "#6A3440")], 0, 90, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-wall", [(0, "#3E4A4E"), (1, "#26302E")]),
        lg(f"{u}-lake", [(0, "#3A5C7A", 0.2), (0.5, "#2A4A66", 0.45), (1, "#1C3248", 0.75)], 0, SH, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-shore", [(0, "#8A7A4A"), (1, "#5A5230")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(140, 250, 260, "#FFE6BE", f"{u}-dawn", 0.55))
    # thin cirrus catching pink
    out.append('<g fill="#F7C6B4" opacity="0.6">' + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="3.2"/>' for x, y, w in ((110, 96, 70), (80, 108, 44), (480, 86, 76), (530, 100, 46), (420, 120, 40))) + "</g>")

    def bells(uu, lite=False):
        s = []
        # far shoulder behind the bells
        sv, _ = massif(f"{uu}-b0", [(150, 250), (200, 196), (238, 176), (300, 186), (380, 168), (430, 200), (480, 250)], 21, 300,
                       "#A0566A", shade="#3A2850", shade_op=0.45, amp=6, snow="#F8EEF0", snow_y=200, snow_amp=14, tex_n=0.6,
                       haze="#C9A0B0")
        s.append(sv)
        # Maroon Peak and North Maroon: two pyramids of banded maroon mudstone, snow caught on the tilted ledges
        sv, _ = massif(f"{uu}-b1", [(170, 300), (210, 220), (246, 150), (276, 100), (300, 132), (318, 146), (340, 128), (356, 114), (392, 170), (430, 236), (470, 300)],
                       7, 310, f"url(#{u}-rock)", shade="#3A2448", shade_op=0.5, amp=7, depth=5, light=1,
                       snow="#FFF4EE", snow_y=146, snow_amp=20, rim="#FFE2C0", rim_w=2.4, gullies=12,
                       strata=("#4A2236", 0.3, -0.22, 22), ledges=(24, -0.22, 150, 262, "#FFF2EC"),
                       tex=("#3A1E2A", "#F2A07A"), tex_op=(0.1, 0.25), haze="#B07A8A", tex_n=0.25 if lite else 1.0)
        s.append(sv)
        return "".join(s)

    def walls(uu, lite=False):
        s = []
        # valley walls: spruce slopes with stands of gold aspen, still in the morning shade
        L = [(-10, 150), (60, 170), (130, 210), (200, 262), (260, 300), (300, 322), (-10, 322)]
        R = [(610, 162), (540, 180), (470, 220), (410, 268), (350, 304), (320, 322), (610, 322)]
        gold = (("#8A5A1E", "#C88A26", "#EDBB44"), ("#9A6420", "#D89A2A", "#F6CE5E"), ("#7A4A1E", "#B8782A", "#E2A63A"))
        for poly, sd, lgt in ((L, 3, 1), (R, 5, -1)):
            line = rough(poly[:-1], sd, 8, 4)
            pp = line + [poly[-1]]
            s.append(f'<polygon points="{P(pp)}" fill="url(#{u}-wall)"/>')
            s.append(f'<clipPath id="{uu}-w{sd}"><polygon points="{P(pp)}"/></clipPath>')
            if lite:
                g = [blobs(110, sd + 40, (min(x for x, _ in pp), 170, max(x for x, _ in pp), 322), ["#C88A26", "#EDBB44", "#9A6420"], r=(2.5, 5), opacity=(0.4, 0.7), squash=1.4),
                     forest_fill(pp, sd + 7, ["#22302C", "#2A3A34"], 70, 8, 22)]
            else:
                g = [grove(pp, sd + 40, 80, 3.5, 9, colors=gold, trunk="#C8C0B0", light=-1, conifers=["#22302C", "#2A3A34", "#1C2826"], ncon=100)]
            s.append(f'<g clip-path="url(#{uu}-w{sd})">' + "".join(g) + "</g>")
            s.append(trees_on(line, sd + 9, ["#22302C", "#2A3A34"], density=1.6, hmin=8, hmax=18))
        return "".join(s)

    out.append(bells(u))
    out.append(walls(u))
    # spruce along the far shore, closing the valley floor
    fl = [(180, 320), (300, 318), (440, 320)]
    floor = trees_on(fl, 17, ["#1E2A28", "#26342F"], density=3, hmin=10, hmax=24, xmin=200, xmax=420, sink=4)
    out.append(floor)
    # lake with the bells mirrored
    out.append(f'<clipPath id="{u}-lk"><rect x="-10" y="{SH}" width="620" height="130"/></clipPath>')
    out.append(f'<rect x="-10" y="{SH}" width="620" height="130" fill="#2A4058"/>')
    out.append(mirror(SH, bells(u + "r", True) + walls(u + "r", True) + floor, f"{u}-lk", 0.85))
    out.append(f'<rect x="-10" y="{SH}" width="620" height="130" fill="url(#{u}-lake)"/>')
    out.append(ripple_lines(26, 6, (-10, SH + 6, 600, 400), "#F2D4C4", op=(0.2, 0.45), w=(30, 90), sw=1.1))
    out.append(ripple_lines(18, 8, (-10, SH + 10, 600, 400), "#1A2A3A", op=(0.2, 0.45), w=(40, 110), sw=1.3))
    out.append(f'<rect x="-10" y="{SH - 1}" width="620" height="2.5" fill="#E9D2C0" opacity="0.6"/>')
    # a pair of ducks leaving a V wake
    for dx, dy in ((372, 352), (392, 358)):
        out.append(f'<path d="M {dx + 6} {dy + 1} L {dx + 54} {dy - 3} M {dx + 6} {dy + 3} L {dx + 54} {dy + 9}" stroke="#F2D8C8" stroke-width="1.3" opacity="0.5"/>'
                   f'<ellipse cx="{dx + 2}" cy="{dy}" rx="6" ry="3" fill="#2A2420"/><circle cx="{dx - 3}" cy="{dy - 3}" r="2.6" fill="#24402E"/>')
    # near shore: grasses, boulders, aspens framing both sides
    shore = [(-10, 404), (80, 396), (180, 404), (300, 410), (420, 402), (520, 394), (610, 398), (610, 444), (-10, 444)]
    out.append(f'<polygon points="{P(rough(shore[:-2], 12, 6, 3) + shore[-2:])}" fill="url(#{u}-shore)"/>')
    for bx, by, r in ((150, 404, 16), (176, 410, 10), (440, 402, 13)):
        out.append(f'<ellipse cx="{bx}" cy="{by}" rx="{r * 1.4}" ry="{r * 0.8}" fill="#6E6A66"/><ellipse cx="{bx - r * 0.4}" cy="{by - r * 0.3}" rx="{r * 0.8}" ry="{r * 0.35}" fill="#A8A29A"/>')
    out.append(grass(170, 13, (-10, 398, 610, 444), ["#C9A24A", "#A88A3A", "#E2C06A", "#7A6A30"], h=(8, 22)))
    # photographer with a tripod waiting for the light
    out.append(figure(250, 412, 26, body="#B8463A", pack="#2E3A4A"))
    out.append('<path d="M 266 384 L 260 412 M 266 384 L 272 412 M 266 384 L 266 412" stroke="#1E1C24" stroke-width="1.6"/><rect x="261" y="378" width="10" height="7" rx="1.5" fill="#1E1C24"/>')
    for x, b, h, sd, ln in ((-6, 444, 190, 1, 0.03), (40, 440, 150, 2, -0.02), (92, 444, 120, 3, 0.04),
                            (510, 444, 160, 4, -0.03), (562, 442, 200, 5, 0.02), (604, 444, 140, 6, -0.04)):
        out.append(aspen(x, b, h, sd, lean=ln))
    out.append(grass(50, 14, (-10, 426, 610, 444), ["#C9A24A", "#E2C06A", "#7A6A30"], h=(8, 18)))
    out.append(falling_leaves([(130, 300, 1.2, "#F2C24A"), (470, 280, 1.0, "#E8A22A"), (210, 360, 0.9, "#F6D25E"), (540, 340, 1.1, "#F2C24A")], 3))
    out.append(birds_v([(420, 150, 12), (442, 160, 9)], "#3A3050"))
    return "\n".join(out)


# ================================================================ Grand Teton (Moulton barn on Mormon Row at dawn)
def sage(n, seed, box, cols=("#4E5644", "#6E7660", "#A8AC98"), r=(3, 8)):
    """Sagebrush flats: low ragged shrubs painted as a dark base and short upright silver-green brush
    ticks, the frosty tips catching the light; nearer shrubs bigger."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    pts = sorted(((rnd.uniform(x0, x1), rnd.uniform(y0, y1)) for _ in range(n)), key=lambda p: p[1])
    out = []
    for x, y in pts:
        t = (y - y0) / max(1, y1 - y0)
        rr = (r[0] + (r[1] - r[0]) * t) * rnd.uniform(0.7, 1.25)
        g = [f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rr * 1.3:.1f}" ry="{rr * 0.45:.1f}" fill="{cols[0]}"/>']
        for k in range(7):
            a = math.radians(rnd.uniform(-150, -30))
            L = rr * rnd.uniform(0.7, 1.2)
            sx = x + rnd.uniform(-rr, rr)
            g.append(f'<path d="M {sx:.1f} {y:.1f} l {L * math.cos(a) * 0.6:.1f} {L * math.sin(a):.1f}" stroke="{cols[1] if k % 3 else cols[2]}" stroke-width="{max(0.8, rr * 0.28):.1f}" stroke-linecap="round"/>')
        out.append("".join(g))
    return '<g fill="none">' + "".join(out) + "</g>"


def patches(n, seed, box, cols, w=(20, 60), h=(3, 8), op=(0.5, 0.9)):
    """Irregular flattened colour patches (ragged ellipses): tundra mosaics, fields, distant foliage."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        y = rnd.uniform(y0, y1)
        t = (y - y0) / max(1, y1 - y0)
        cx = rnd.uniform(x0, x1)
        rx = rnd.uniform(*w) * (0.5 + t)
        ry = rnd.uniform(*h) * (0.5 + t)
        k = 9
        pts = []
        for i in range(k):
            a = 2 * math.pi * i / k
            rr = rnd.uniform(0.65, 1.15)
            pts.append((cx + rx * rr * math.cos(a), y + ry * rr * math.sin(a)))
        out.append(f'<polygon points="{Pi(pts)}" fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


def strokes_h(n, seed, box, cols, w=(4, 16), sw=(1, 2.2), op=(0.3, 0.7)):
    """Short horizontal brush strokes: texture for flats, fields and distant water."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        y = rnd.uniform(y0, y1)
        t = (y - y0) / max(1, y1 - y0)
        x = rnd.uniform(x0, x1)
        L = rnd.uniform(*w) * (0.5 + t)
        out.append(f'<path d="M {x:.0f} {y:.1f} q {L / 2:.1f} {-rnd.uniform(0, 1.2):.1f} {L:.1f} 0" stroke="{rnd.choice(cols)}" stroke-width="{rnd.uniform(*sw) * (0.6 + t * 0.8):.1f}" opacity="{rnd.uniform(*op):.2f}"/>')
    return '<g fill="none" stroke-linecap="round">' + "".join(out) + "</g>"


def pronghorn(x, base, s, flip=1, head_down=False):
    """Pronghorn in profile facing left: tan coat, white belly and rump, black horns."""
    head = ('<path d="M -4 -30 L -16 -20 L -20 -14 L -14 -12 L -4 -20 Z" fill="#C88A52"/>' if head_down else
            '<path d="M -2 -32 L -8 -48 L -16 -50 L -20 -45 L -12 -40 L -8 -30 Z" fill="#C88A52"/>'
            '<path d="M -10 -50 L -11 -60 L -8 -56 M -13 -50 L -15 -60" stroke="#1E1612" stroke-width="2" fill="none" stroke-linecap="round"/>'
            '<path d="M -16 -50 L -20 -45 L -17 -44 Z" fill="#1E1612"/><path d="M -9 -44 L -6 -36 L -9 -34 Z" fill="#F4EEE2"/>')
    return (f'<g transform="translate({x:.1f} {base:.1f}) scale({s * flip:.3f} {s:.3f})">'
            '<path d="M -2 -16 L -4 0 M 4 -16 L 6 0 M 26 -16 L 24 0 M 32 -16 L 34 0" stroke="#5A3A22" stroke-width="2.4" stroke-linecap="round"/>'
            '<path d="M -6 -30 Q 0 -36 16 -34 Q 32 -34 38 -28 Q 40 -20 34 -16 L 0 -16 Q -6 -20 -6 -30 Z" fill="#C88A52"/>'
            '<path d="M 0 -16 Q 16 -21 34 -16 Q 20 -14 0 -16 Z" fill="#F4EEE2"/><ellipse cx="36" cy="-24" rx="4" ry="6" fill="#F4EEE2"/>'
            '<path d="M -6 -30 Q 0 -36 16 -34 Q 32 -34 38 -28" stroke="#FFD2A0" stroke-width="1.4" fill="none"/>'
            + head + "</g>")


def moulton_barn(x, base, k, u):
    """The weathered plank barn on Mormon Row: tall gabled centre with lean-to sheds either side and a
    pitched hay hood, lit warm by the dawn on its east face. Local units: 1 = k px; base at y=0."""
    rnd = random.Random(5)
    lit, mid, dark = "#B98A62", "#8E6446", "#4A3430"
    out = [f'<g transform="translate({x:.1f} {base:.1f}) scale({k:.3f})">']
    # the barn seen a little from the side: roof planes and the shadowed north wall receding to the right
    out.append(f'<polygon points="{P([(0, -138), (46, -82), (82, -90), (36, -146)])}" fill="#2E2426"/>')
    out.append(f'<polygon points="{P([(36, -80), (98, -40), (134, -48), (72, -88)])}" fill="#342828"/>')
    out.append(f'<polygon points="{P([(92, -40), (134, -48), (134, -6), (92, 0)])}" fill="{dark}"/>')
    out.append('<g stroke="#2A1E1E" stroke-width="0.9" opacity="0.6">' + "".join(f'<line x1="{xx}" y1="{-40 - (xx - 92) * 0.19:.1f}" x2="{xx}" y2="{-(xx - 92) * 0.14:.1f}"/>' for xx in range(96, 134, 5)) + "</g>")
    out.append('<path d="M 0 -138 L 36 -146 M 98 -40 L 134 -48" stroke="#E8A888" stroke-width="1.2" opacity="0.5"/>')
    # sheds
    for sgn in (-1, 1):
        wall = [(sgn * 40, 0), (sgn * 92, 0), (sgn * 92, -42), (sgn * 40, -74)]
        out.append(f'<polygon points="{P(wall)}" fill="{mid if sgn > 0 else lit}"/>')
    # central block
    out.append(f'<polygon points="{P([(-40, 0), (40, 0), (40, -86), (0, -132), (-40, -86)])}" fill="{lit}"/>')
    out.append(f'<polygon points="{P([(8, 0), (40, 0), (40, -86), (8, -123)])}" fill="{mid}" opacity="0.35"/>')
    # vertical planks with silver weathering
    planks = []
    for xx in range(-90, 92, 5):
        top = -132 + abs(xx) * 1.15 if abs(xx) <= 40 else -74 + (abs(xx) - 40) * 32 / 52
        planks.append(f'<line x1="{xx}" y1="0" x2="{xx}" y2="{max(top, -132) + 2:.1f}"/>')
    out.append('<g stroke="#5A3E30" stroke-width="0.9" opacity="0.55">' + "".join(planks) + "</g>")
    out.append(streaks(60, 9, (-90, -120, 92, -4), ["#E2CDB0", "#6A4A38"], w=(0.8, 1.8), length=(8, 30), opacity=(0.2, 0.45), slant=0.05))
    # roofs: dark cedar shingles with a warm rim of dawn light
    for sgn in (-1, 1):
        r = [(sgn * 36, -80), (sgn * 98, -40), (sgn * 98, -35), (sgn * 36, -73)]
        out.append(f'<polygon points="{P(r)}" fill="#3A2C2C"/>')
        out.append(f'<line x1="{sgn * 36}" y1="-80" x2="{sgn * 98}" y2="-40" stroke="#F0B890" stroke-width="2" opacity="{0.9 if sgn < 0 else 0.4}"/>')
    out.append(f'<polygon points="{P([(-46, -82), (0, -138), (46, -82), (46, -77), (0, -131), (-46, -77)])}" fill="#3A2C2C"/>')
    out.append('<path d="M -46 -82 L 0 -138" stroke="#FFD0A8" stroke-width="2.4"/><path d="M 0 -138 L 46 -82" stroke="#E8A888" stroke-width="1.6" opacity="0.6"/>')
    # hay hood and doors
    out.append(f'<polygon points="{P([(-14, -100), (14, -100), (14, -82), (-14, -82)])}" fill="#2A1E1E"/>')
    out.append(f'<polygon points="{P([(-18, -100), (0, -116), (18, -100), (18, -97), (0, -112), (-18, -97)])}" fill="#3A2C2C"/>')
    out.append('<rect x="-18" y="-50" width="36" height="50" fill="#2A1E1E"/><path d="M -18 -50 L 18 0 M 18 -50 L -18 0" stroke="#8E6446" stroke-width="2"/>'
               '<rect x="-18" y="-52" width="36" height="3" fill="#C9A07A"/>')
    for sgn in (-1, 1):
        out.append(f'<rect x="{sgn * 66 - 7}" y="-30" width="14" height="12" fill="#2A1E1E"/><rect x="{sgn * 66 - 8}" y="-32" width="16" height="2" fill="#C9A07A"/>')
    out.append(f'<rect x="-92" y="-3" width="222" height="4" fill="#3A2A22" opacity="0.6"/>')
    out.append("</g>")
    return "".join(out)


def grand_teton():
    u = "gtn"
    out = [defs(
        lg(f"{u}-sky", [(0, "#2E3466"), (0.38, "#6A6AA0"), (0.66, "#D8A2B2"), (0.82, "#F2C2B4"), (1, "#C8B4C8")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-rock", [(0, "#FFC4A0"), (0.35, "#E09A92"), (0.7, "#9A7090"), (1, "#4E4A70")], 0, 90, 0, 306, units="userSpaceOnUse"),
        lg(f"{u}-flat", [(0, "#6E7258"), (1, "#3E4234")]),
        lg(f"{u}-near", [(0, "#8A8462"), (1, "#4A4834")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    # a few dawn-lit cloud wisps over the peaks
    out.append('<g fill="#F8CFC0" opacity="0.7">' + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{h}"/>' for x, y, w, h in ((420, 92, 70, 4), (470, 102, 44, 3), (120, 82, 60, 3.5), (330, 74, 50, 3))) + "</g>")
    out.append('<g fill="#9A7AA0" opacity="0.35">' + "".join(
        f'<ellipse cx="{x}" cy="{y + 4}" rx="{w * 0.8}" ry="2"/>' for x, y, w in ((420, 92, 70), (120, 82, 60))) + "</g>")
    # the range: South & Middle Teton, the Grand, Mount Owen and Teewinot, then the long ridge to Mount Moran
    # far ridges first, then the Cathedral Group in front
    sv, _ = massif(f"{u}-f", [(-10, 250), (60, 214), (110, 196), (160, 200), (420, 206), (470, 176), (500, 172), (530, 178), (560, 200), (610, 226)],
                   19, 306, "#9A88A8", shade="#4A4072", shade_op=0.45, amp=5, light=1, snow="#F4E8EE", snow_y=190, snow_amp=14,
                   tex_n=0.5, haze="#8A7A9A")
    out.append(sv)
    ctrl = [(40, 300), (80, 236), (108, 184), (130, 200), (160, 140), (186, 162), (200, 150), (234, 92),
            (252, 128), (264, 118), (286, 148), (302, 136), (330, 190), (370, 240), (400, 300)]
    sv, line = massif(f"{u}-m", ctrl, 11, 306, f"url(#{u}-rock)", shade="#2C2858", shade_op=0.6, amp=6, depth=5, light=1,
                      snow="#FFF2EC", snow_y=150, snow_amp=24, rim="#FFE6CC", rim_w=2.4, gullies=10,
                      tex=("#4A3A60", "#FFD8C0"), tex_op=(0.12, 0.3), haze="#5A5478", haze_top=230, spine_k=0.3)
    out.append(sv)
    # morning mist in the valley and the dark forest along the Snake River
    out.append(mist(300, 300, 360, 18, "#E8D4DC", f"{u}-mist1", 0.7))
    fl = rough([(-10, 312), (150, 308), (300, 312), (450, 306), (610, 310)], 4, 3, 4)
    out.append(f'<polygon points="{P(fl + [(610, 330), (-10, 330)])}" fill="#2E3446"/>')
    out.append(trees_on(fl, 8, ["#2A3042", "#323A4E", "#262C3C"], density=3.4, hmin=8, hmax=20, sink=4))
    out.append(mist(160, 318, 220, 10, "#D8C4D4", f"{u}-mist2", 0.55))
    # sagebrush flat
    out.append(f'<path d="M -10 318 Q 300 312 610 316 L 610 444 L -10 444 Z" fill="url(#{u}-flat)"/>')
    out.append(strokes_h(260, 2, (-10, 318, 610, 404), ["#8A8E74", "#5A604A", "#A8A88C", "#7A6A50"], w=(4, 14), sw=(1, 2)))
    out.append(sage(220, 3, (-10, 322, 610, 400), cols=("#4A5040", "#8A927A", "#C8CCB8"), r=(1.6, 4.5)))
    out.append(mist(260, 330, 300, 16, "#F2B8A8", f"{u}-dawn", 0.35))
    # a pair of pronghorn in the sage
    out.append(pronghorn(118, 356, 0.5))
    out.append(pronghorn(150, 360, 0.45, flip=-1, head_down=True))
    # the barn and its long shadow-side; buck-and-rail fence leading in
    out.append(f'<ellipse cx="452" cy="392" rx="120" ry="8" fill="#2A2C24" opacity="0.4"/>')
    out.append(moulton_barn(430, 392, 1.02, u))
    fence = []
    for i, x in enumerate(range(-10, 360, 30)):
        y = 400 + (360 - x) * 0.05
        fence.append(f'<path d="M {x - 6} {y} L {x + 6} {y - 22} M {x + 6} {y} L {x - 6} {y - 22}" stroke="#4A3828" stroke-width="2.6"/>')
    fence.append('<path d="M -10 398 L 360 380" stroke="#6A5038" stroke-width="2.6"/><path d="M -10 388 L 360 371" stroke="#6A5038" stroke-width="2.2"/>')
    fence.append('<path d="M -10 397 L 360 379" stroke="#E8B890" stroke-width="0.9" opacity="0.6"/>')
    out.append("".join(fence))
    out.append(f'<path d="M -10 404 Q 300 396 610 402 L 610 444 L -10 444 Z" fill="url(#{u}-near)"/>')
    out.append(strokes_h(120, 6, (-10, 404, 610, 444), ["#A89A6A", "#7A6E4A", "#C8B888"], w=(8, 20), sw=(1.4, 2.6)))
    out.append(grass(160, 9, (-10, 400, 610, 444), ["#C8B47A", "#9A8A58", "#E2D0A0", "#7A6A48"], h=(8, 20)))
    out.append(sage(26, 7, (-10, 414, 610, 444), cols=("#4A5244", "#8A9682", "#D0D6C8"), r=(6, 11)))
    out.append(birds_v([(330, 120, 11), (350, 128, 8)], "#3A2E50"))
    return "\n".join(out)


# ================================================================ Denali (the High One over fall tundra, a bull moose)
def cloud_bank(x0, x1, y, h, seed, body, shade, light, n=60, r=(10, 26), flat=None):
    """Horizontal bank of cumulus: shaded underside, body, sunlit tops (light from the upper left).
    flat = clip id to give the cloud a flat base at y + r_max * 0.5."""
    rnd = random.Random(seed)
    pts = []
    for _ in range(n):
        x = rnd.uniform(x0, x1)
        t = abs((x - x0) / (x1 - x0) - 0.5) * 2
        rr = rnd.uniform(*r) * (1 - 0.5 * t)
        pts.append((x, y - rnd.uniform(0, h) * (1 - 0.6 * t), rr))
    out = ['<g fill="' + shade + '">' + "".join(f'<circle cx="{x:.0f}" cy="{yy + rr * 0.35:.0f}" r="{rr:.1f}"/>' for x, yy, rr in pts) + "</g>",
           '<g fill="' + body + '">' + "".join(f'<circle cx="{x - rr * 0.1:.0f}" cy="{yy:.0f}" r="{rr * 0.9:.1f}"/>' for x, yy, rr in pts) + "</g>",
           '<g fill="' + light + '">' + "".join(f'<circle cx="{x - rr * 0.3:.0f}" cy="{yy - rr * 0.35:.0f}" r="{rr * 0.55:.1f}"/>' for x, yy, rr in pts) + "</g>"]
    if flat:
        return (f'<clipPath id="{flat}"><rect x="{x0 - 40}" y="{y - h - r[1] * 2}" width="{x1 - x0 + 80}" height="{h + r[1] * 2.5}"/></clipPath>'
                f'<g clip-path="url(#{flat})">' + "".join(out) + "</g>")
    return "".join(out)


def moose(x, base, s, rim="#FFD9A0", flip=1):
    """Bull moose in profile facing left: humped shoulders, long pale legs, overhanging muzzle, dewlap and
    broad palmate antlers; rim light on the back from the low sun."""
    body = [(150, -96), (122, -104), (92, -110), (66, -124), (48, -130), (34, -120), (18, -112), (2, -110), (-18, -98),
            (-32, -84), (-38, -74), (-34, -67), (-22, -69), (-8, -78), (8, -84), (20, -80), (28, -66), (36, -58),
            (70, -60), (110, -58), (126, -62), (144, -70), (154, -84)]
    legs = [  # far legs first (darker), then near legs
        ([(48, -62), (56, -62), (60, -30), (58, 0), (51, 0), (52, -30)], "#2A1E18", "#6E6458"),
        ([(130, -66), (142, -66), (140, -40), (134, -30), (138, 0), (131, 0), (127, -30), (130, -44)], "#2A1E18", "#6E6458"),
        ([(30, -64), (42, -62), (44, -30), (42, 0), (35, 0), (34, -30)], "#3A2A20", "#A89C8A"),
        ([(112, -64), (128, -64), (126, -40), (118, -28), (124, 0), (116, 0), (110, -28), (112, -44)], "#3A2A20", "#A89C8A"),
    ]
    near_palm = [(4, -112), (-6, -126), (-26, -132), (-46, -142), (-40, -138), (-40, -150), (-30, -144), (-26, -158), (-18, -150),
                 (-10, -162), (-4, -152), (4, -160), (8, -148), (14, -154), (16, -140), (12, -124)]
    far_palm = [(14, -114), (24, -126), (32, -140), (30, -154), (38, -146), (44, -158), (48, -146), (56, -152), (56, -138), (64, -140),
                (58, -128), (44, -122), (24, -112)]
    out = [f'<g transform="translate({x:.1f} {base:.1f}) scale({s * flip:.3f} {s:.3f})">']
    out.append(f'<polygon points="{P(far_palm)}" fill="#8E7A5E"/>')
    for pts, top, low in legs[:2]:
        out.append(f'<polygon points="{P(pts)}" fill="{top}"/>')
        out.append(f'<polygon points="{P([p for p in pts if p[1] > -34] )}" fill="{low}" opacity="0.8"/>')
    out.append(f'<polygon points="{P(body)}" fill="#3E2C22"/>')
    # darker belly and shoulder shading, lighter saddle
    out.append('<path d="M 36 -58 Q 90 -70 144 -70 L 154 -84 Q 150 -64 126 -62 L 110 -58 L 70 -60 Z" fill="#1E140F" opacity="0.6"/>')
    out.append('<path d="M 66 -122 Q 100 -108 140 -100 Q 110 -96 80 -104 Q 66 -110 60 -118 Z" fill="#6A5240" opacity="0.6"/>')
    out.append('<path d="M -8 -78 L 8 -84 L 10 -62 Q 6 -58 4 -64 Z" fill="#2A1E18"/>')
    for pts, top, low in legs[2:]:
        out.append(f'<polygon points="{P(pts)}" fill="{top}"/>')
        lower = [p for p in pts if p[1] > -34]
        out.append(f'<polygon points="{P(lower)}" fill="{low}"/>')
    # head details: muzzle, eye, ear
    out.append('<path d="M -18 -98 Q -30 -88 -38 -74 Q -34 -66 -22 -69 Q -28 -80 -18 -98 Z" fill="#5A4232"/>')
    out.append('<circle cx="-4" cy="-100" r="2.2" fill="#0E0A08"/><circle cx="-4.6" cy="-100.6" r="0.7" fill="#F2E6D2"/>')
    out.append('<path d="M 12 -112 L 24 -124 L 20 -110 Z" fill="#2E2018"/><ellipse cx="-33" cy="-76" rx="2" ry="1.4" fill="#0E0A08"/>')
    out.append(f'<polygon points="{P(near_palm)}" fill="#D2BC94"/>')
    out.append(f'<polygon points="{P([(4, -112), (-6, -126), (-26, -132), (-46, -142), (-40, -138), (-22, -128), (-4, -120), (8, -114)])}" fill="#9A8462"/>')
    out.append(f'<polyline points="{P(near_palm[2:13])}" fill="none" stroke="{rim}" stroke-width="1.6" stroke-linejoin="round" opacity="0.9"/>')
    out.append(f'<polyline points="{P(body[:7])}" fill="none" stroke="{rim}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round" opacity="0.9"/>')
    rnd = random.Random(int(x))
    out.append('<g stroke="#6A5240" stroke-width="1.3" fill="none" opacity="0.6" stroke-linecap="round">' + "".join(
        f'<path d="M {fx:.0f} {fy:.0f} q 3 4 2 {rnd.uniform(5, 9):.1f}"/>' for fx, fy in [(rnd.uniform(40, 140), rnd.uniform(-118, -70)) for _ in range(26)]) + "</g>")
    out.append("</g>")
    return "".join(out)


def denali():
    u = "dnl"
    out = [defs(
        lg(f"{u}-sky", [(0, "#4E7EB8"), (0.5, "#8EB4D8"), (0.85, "#D6E2E6"), (1, "#F2E6CE")], 0, 40, 0, 290, units="userSpaceOnUse"),
        lg(f"{u}-snow", [(0, "#FFF8EC"), (0.45, "#F6F2EE"), (1, "#B8C6DC")], 0, 94, 0, 260, units="userSpaceOnUse"),
        lg(f"{u}-hill", [(0, "#7A6670"), (1, "#4A4250")]),
        lg(f"{u}-tundra", [(0, "#A85A3A"), (0.5, "#8A3A2A"), (1, "#5A2A22")], 0, 290, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-pond", [(0, "#A8C6E2"), (1, "#5E86B0")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(70, 160, 220, "#FFF2D8", f"{u}-sun", 0.6))
    # Denali: one colossal snow massif, South Peak higher on the left, North Peak on the right
    ctrl = [(10, 262), (80, 214), (140, 170), (190, 136), (228, 108), (254, 94), (282, 104), (316, 100), (346, 110),
            (370, 126), (398, 116), (428, 132), (476, 166), (530, 196), (580, 222), (620, 236)]
    sv, line = massif(f"{u}-m", ctrl, 3, 270, f"url(#{u}-snow)", shade="#4E6496", shade_op=0.5, amp=5, depth=5, light=1,
                      rim="#FFF4DC", rim_w=2.2, gullies=12, tex=("#8A9AB8", "#FFFFFF"), tex_op=(0.12, 0.3), tex_n=0.8,
                      haze="#C8D6E4", haze_top=170, spine_k=0.3)
    out.append(sv)
    # dark rock buttresses poking through the ice
    rnd = random.Random(8)
    rock = []
    for _ in range(26):
        x = rnd.uniform(130, 520)
        y0 = y_on(line, x)
        if y0 is None:
            continue
        y = y0 + rnd.uniform(14, 90)
        L = rnd.uniform(8, 26)
        rock.append(f'<path d="M {x:.0f} {y:.0f} l {rnd.uniform(-4, 4):.1f} {L:.1f} l {rnd.uniform(2, 5):.1f} {-L * 0.2:.1f} Z" fill="#4A5068" opacity="{rnd.uniform(0.35, 0.7):.2f}"/>')
    out.append(f'<g clip-path="url(#{u}-m-c)">' + "".join(rock) + mist(150, 150, 220, 110, "#FFE2B8", f"{u}-warm", 0.35) + "</g>")
    # a cloud bank wrapping the mountain's lower slopes
    out.append(mist(330, 246, 330, 26, "#EEF2F4", f"{u}-cm", 0.9))
    # soft layered cloud wrapped around the lower slopes
    for k, (cx, cy, rx, ry, col, op) in enumerate(((260, 240, 170, 18, "#C2CCDC", 0.85), (480, 244, 180, 16, "#C2CCDC", 0.85),
                                                    (300, 232, 130, 13, "#FFFFFF", 1), (510, 236, 130, 12, "#FFFFFF", 1),
                                                    (110, 246, 130, 10, "#F4F4F4", 0.9), (390, 226, 80, 9, "#FFFFFF", 0.95))):
        out.append(mist(cx, cy, rx, ry, col, f"{u}-cl{k}", op))
    # outer range foothills: bare, brown-violet, with early snow on the tops
    sv, fl = massif(f"{u}-h", [(-10, 256), (40, 232), (90, 248), (140, 226), (190, 246), (230, 238), (280, 256), (330, 244), (380, 262), (440, 236), (500, 258), (560, 240), (610, 250)],
                    7, 300, f"url(#{u}-hill)", shade="#2E2840", shade_op=0.45, amp=5, light=1, snow="#F2EEF2", snow_y=250, snow_amp=6,
                    tex=("#3A2E36", "#C8A890"), tex_op=(0.2, 0.4), tex_n=1.2, rim="#E8C8A8", rim_w=1.4)
    out.append(sv)
    # the braided river on its gravel flats
    out.append('<path d="M -10 286 Q 300 278 610 288 L 610 302 Q 300 294 -10 302 Z" fill="#9A9488"/>')
    out.append('<g fill="none" stroke="#C8DCEC" stroke-linecap="round">'
               '<path d="M -10 292 C 80 288 140 296 220 290 S 380 284 460 292 S 560 296 610 292" stroke-width="2.4"/>'
               '<path d="M 60 296 C 120 292 170 298 240 294" stroke-width="1.4"/><path d="M 320 288 C 380 292 420 286 500 290" stroke-width="1.4"/></g>')
    # rolling tundra in full fall colour: crimson dwarf birch and blueberry, gold willow, dark spruce
    out.append(f'<path d="M -10 300 Q 160 292 300 300 Q 440 306 610 296 L 610 444 L -10 444 Z" fill="url(#{u}-tundra)"/>')
    out.append(patches(140, 5, (-10, 300, 610, 444), ["#D88A3A", "#E8B04A", "#B84A2E", "#C86A3A", "#7A2E24", "#8A7A3A"], w=(14, 40), h=(2, 6), op=(0.5, 0.85)))
    out.append(strokes_h(320, 6, (-10, 300, 610, 444), ["#E2A050", "#C84A30", "#F0C060", "#6A2420", "#B86A3A"], w=(4, 14), sw=(0.8, 2), op=(0.4, 0.8)))
    # kettle ponds mirroring the sky
    for cx, cy, rx, ry in ((150, 330, 60, 7), (410, 322, 44, 5), (250, 352, 34, 5)):
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{u}-pond)"/>'
                   f'<ellipse cx="{cx - rx * 0.2:.0f}" cy="{cy - ry * 0.3:.1f}" rx="{rx * 0.5:.0f}" ry="1" fill="#FFFFFF" opacity="0.6"/>'
                   f'<path d="M {cx - rx} {cy} Q {cx} {cy - ry * 1.6} {cx + rx} {cy}" fill="none" stroke="#5A3A22" stroke-width="1.4" opacity="0.6"/>')
    # scattered black spruce, thin and scraggly
    rnd = random.Random(12)
    sp = []
    for _ in range(40):
        x, y = rnd.uniform(-10, 610), rnd.uniform(298, 350)
        h = 6 + (y - 298) * 0.5 + rnd.uniform(0, 8)
        sp.append((y, con(x, y, h, rnd.choice(["#1E2A22", "#26342A", "#2E3A2C"]), rnd.random(), width=0.2)))
    for x, y, h in ((30, 392, 70), (62, 398, 52), (560, 404, 84), (596, 400, 60), (14, 410, 46)):
        sp.append((y, con(x, y, h, "#1A241E", x, width=0.22, light="#4A5A3A")))
    out.append("".join(v for _, v in sorted(sp, key=lambda t: t[0])))
    # foreground willow and blueberry, then the moose browsing in it
    rnd = random.Random(9)
    shrubs = []
    for _ in range(26):
        x, y = rnd.uniform(-10, 610), rnd.uniform(384, 444)
        r = 5 + (y - 384) * 0.2
        pal = rnd.choice((("#8A2A1E", "#C8402A", "#E87A4A"), ("#9A6A1E", "#E2A23A", "#F6D06A"), ("#7A3A1E", "#B8602A", "#E8A04A")))
        shrubs.append((y, leafy(x, y - r * 0.5, r * 1.6, r * 0.8, rnd.randrange(999), *pal, n=5, lx=-0.6, ly=-0.6, dab=0.35, rot=False)))
    out.append("".join(v for _, v in sorted(shrubs, key=lambda t: t[0]) if _ < 420))
    out.append(moose(372, 424, 0.92))
    out.append("".join(v for _, v in sorted(shrubs, key=lambda t: t[0]) if _ >= 420))
    out.append(grass(140, 11, (-10, 404, 610, 444), ["#F2C25A", "#C8402A", "#E8A23A", "#7A2A22"], h=(6, 16), sw=1.8))
    out.append(birds_v([(120, 120, 12), (142, 112, 9), (156, 126, 8)], "#3A4660"))
    return "\n".join(out)


# ================================================================ Great Smoky Mountains (sunrise over the ridges, a log cabin)
def soft_ridge(ctrl, seed, color, base=444, amp=6, bumps=None, bump_r=(1.5, 3.5), density=1.0):
    """Rounded Appalachian ridge; optional canopy bumps (tree crowns) along the crest."""
    line = rough(ctrl, seed, amp, 5, 0.5)
    out = [f'<polygon points="{P(line + [(line[-1][0], base), (line[0][0], base)])}" fill="{color}"/>']
    if bumps:
        rnd = random.Random(seed + 1)
        b = []
        x = line[0][0]
        while x < line[-1][0]:
            y = y_on(line, x)
            if y is not None:
                r = rnd.uniform(*bump_r)
                b.append(f'<circle cx="{x:.0f}" cy="{y + r * 0.4:.1f}" r="{r:.1f}"/>')
            x += rnd.uniform(1.5, 4) / density
        out.append(f'<g fill="{bumps}">' + "".join(b) + "</g>")
    return "".join(out), line


def deer(x, base, s, flip=1, col="#8A5A3A", head_down=False, rim="#FFD6A0"):
    """White-tailed deer in profile facing left: slim legs, long neck, big ears, white throat and tail."""
    if head_down:
        head = (f'<polygon points="-2,-33 -12,-16 -7,-13 4,-28" fill="{col}"/>'
                f'<path d="M -9 -18 L -17 -6 L -14 -3 L -5 -13 Z" fill="{col}"/><path d="M -8 -18 L -5 -26 L -4 -19 Z" fill="{col}"/>'
                '<circle cx="-16" cy="-5" r="1.3" fill="#1A1210"/>')
    else:
        head = (f'<polygon points="-2,-34 -8,-50 -2,-52 5,-36" fill="{col}"/>'
                f'<path d="M -3 -53 L -10 -53 L -19 -47 L -18 -44 L -8 -45 Z" fill="{col}"/>'
                f'<path d="M -4 -52 L 1 -60 L -1 -51 Z M -7 -52 L -8 -61 L -5 -52 Z" fill="{col}"/>'
                '<path d="M -6 -44 L -2 -38 L -5 -37 Z" fill="#F4EEE2"/><circle cx="-18" cy="-46" r="1.2" fill="#1A1210"/>'
                '<circle cx="-9" cy="-50" r="1" fill="#1A1210"/>')
    return (f'<g transform="translate({x:.1f} {base:.1f}) scale({s * flip:.3f} {s:.3f})">'
            '<path d="M 2 -22 L 1 -10 L 2 0 M 8 -22 L 9 -10 L 8 0 M 28 -22 L 31 -12 L 27 0 M 33 -22 L 36 -12 L 33 0" stroke="#4A3022" stroke-width="2.2" stroke-linecap="round" fill="none"/>'
            f'<path d="M -2 -34 Q 4 -40 18 -38 Q 32 -40 37 -32 Q 39 -24 34 -21 L 4 -21 Q -3 -24 -2 -34 Z" fill="{col}"/>'
            '<path d="M 37 -32 Q 44 -36 42 -27 Q 38 -26 37 -30 Z" fill="#F4EEE2"/><path d="M 5 -22 Q 18 -25 32 -22" stroke="#E8DCC8" stroke-width="1.6" fill="none"/>'
            f'<path d="M -2 -34 Q 4 -40 18 -38 Q 32 -40 37 -32" stroke="{rim}" stroke-width="1.4" fill="none" opacity="0.8"/>'
            + head + "</g>")


def log_cabin(x, base, k, u):
    """Single-pen log cabin with a stone chimney on the gable end, shake roof and a lamp in the window.
    Seen in 3/4 view: long front wall facing us (in the shade, the sun is behind), gable end to the left."""
    out = [f'<g transform="translate({x:.1f} {base:.1f}) scale({k:.3f})">']
    logs_dark, logs_mid, chink = "#4A3226", "#6A4632", "#C8B49A"
    # gable end (receding to the left)
    gable = [(0, 0), (-34, -10), (-34, -50), (-17, -84), (0, -40)]
    out.append(f'<polygon points="{P(gable)}" fill="{logs_dark}"/>')
    for i in range(1, 9):
        y0, y1 = -i * 5, -10 - i * 5
        if -40 - 0 < y0:
            out.append(f'<line x1="0" y1="{y0}" x2="-34" y2="{y1}" stroke="{chink}" stroke-width="1" opacity="0.45"/>')
    # front wall: stacked logs with light chinking and notched corners
    out.append('<rect x="0" y="-40" width="120" height="40" fill="' + logs_mid + '"/>')
    for i in range(8):
        y = -40 + i * 5
        out.append(f'<rect x="0" y="{y}" width="120" height="4" rx="2" fill="{"#7A5238" if i % 2 else "#6E4A34"}"/>'
                   f'<rect x="0" y="{y + 4}" width="120" height="1" fill="{chink}" opacity="0.7"/>'
                   f'<rect x="0" y="{y}" width="120" height="1" fill="#F2C890" opacity="0.18"/>')
        for cx in (-2, 122):
            out.append(f'<ellipse cx="{cx}" cy="{y + 2}" rx="3.4" ry="2.4" fill="#8A6244"/>')
    # door, window with a warm lamp, porch posts
    out.append('<rect x="44" y="-32" width="18" height="32" fill="#2A1C16"/><rect x="46" y="-30" width="14" height="30" fill="#3E2A20"/>')
    out.append('<rect x="80" y="-28" width="16" height="13" fill="#FFC870"/><path d="M 88 -28 L 88 -15 M 80 -21.5 L 96 -21.5" stroke="#4A3226" stroke-width="1.6"/>'
               '<rect x="78" y="-30" width="20" height="17" fill="none" stroke="#3A2620" stroke-width="2"/>')
    out.append(glow(88, -21, 26, "#FFC870", f"{u}-lamp", 0.55))
    # shake roof with the ridge catching the sunrise
    roof = [(-6, -38), (126, -38), (108, -88), (-21, -88)]
    out.append(f'<polygon points="{P(roof)}" fill="#4E3A30"/>')
    out.append('<g stroke="#2E221E" stroke-width="1" opacity="0.7">' + "".join(
        f'<line x1="{-6 + t * -15:.1f}" y1="{-38 - t * 50:.1f}" x2="{126 - t * 18:.1f}" y2="{-38 - t * 50:.1f}"/>' for t in (0.2, 0.4, 0.6, 0.8)) + "</g>")
    rnd = random.Random(3)
    out.append('<g stroke="#2E221E" stroke-width="0.8" opacity="0.5">' + "".join(
        f'<line x1="{xx:.0f}" y1="{-38 - j * 10:.0f}" x2="{xx - 3:.0f}" y2="{-48 - j * 10:.0f}"/>' for j in range(5) for xx in [rnd.uniform(-10 - j * 3, 120 - j * 3) for _ in range(9)]) + "</g>")
    out.append('<path d="M -21 -88 L 108 -88" stroke="#FFD6A0" stroke-width="2.4"/><path d="M 108 -88 L 126 -38" stroke="#FFC890" stroke-width="1.8" opacity="0.8"/>')
    out.append(f'<polygon points="{P([(-21, -88), (-6, -38), (-38, -48)])}" fill="#3A2A24"/>')
    # stone chimney on the gable end
    out.append('<polygon points="-30,2 -12,-3 -12,-62 -16,-64 -16,-104 -30,-100 -30,-58 -34,-56 -34,0" fill="#7A746E"/>')
    for (cx, cy, w, h) in [(-30, -8, 8, 5), (-21, -14, 8, 5), (-28, -22, 9, 5), (-20, -30, 7, 5), (-30, -38, 8, 5), (-22, -46, 8, 5),
                           (-29, -54, 7, 5), (-27, -66, 8, 5), (-21, -76, 6, 5), (-28, -86, 8, 5), (-22, -96, 6, 5)]:
        out.append(f'<rect x="{cx}" y="{cy}" width="{w}" height="{h}" rx="1.5" fill="{rnd.choice(["#9A948C", "#8A847C", "#A8A098", "#6E6862"])}"/>')
    out.append('<path d="M -16 -104 L -16 -64 L -12 -62 L -12 -3" stroke="#FFD6A0" stroke-width="1.6" fill="none" opacity="0.8"/>')
    out.append("</g>")
    return "".join(out)


def great_smoky_mountains():
    u = "gsm"
    SX, SY = 420, 186
    out = [defs(
        lg(f"{u}-sky", [(0, "#5A6CA8"), (0.35, "#A2A2C8"), (0.62, "#F2BFA8"), (0.8, "#FBD9A6"), (1, "#FCE8C4")], 0, 40, 0, 250, units="userSpaceOnUse"),
        lg(f"{u}-meadow", [(0, "#4A6248"), (1, "#24342E")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(SX, SY, 300, "#FFE2A8", f"{u}-sun", 0.85))
    out.append(f'<circle cx="{SX}" cy="{SY}" r="17" fill="#FFF6DC"/>')
    # sunbeams through the haze
    out.append('<g fill="#FFF0CC" opacity="0.12">' + "".join(
        f'<polygon points="{SX},{SY} {SX + 500 * math.cos(math.radians(a)):.0f},{SY + 500 * math.sin(math.radians(a)):.0f} {SX + 500 * math.cos(math.radians(a + w)):.0f},{SY + 500 * math.sin(math.radians(a + w)):.0f}"/>'
        for a, w in ((150, 4), (162, 2.5), (172, 3), (14, 3), (26, 2.5), (40, 4))) + "</g>")
    # long thin clouds lit from beneath
    out.append('<g fill="#F7C6A8" opacity="0.65">' + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="3"/>' for x, y, w in ((120, 100, 80), (170, 112, 50), (470, 110, 90), (540, 124, 50), (300, 86, 40))) + "</g>")
    # seven ridges from far to near, a band of mist pooling at the foot of each
    ridges = [
        ([(-10, 222), (80, 206), (170, 214), (260, 198), (360, 212), (460, 202), (540, 214), (610, 206)], "#DDB8BC", "#F8DCCB"),
        ([(-10, 234), (60, 220), (150, 232), (240, 216), (330, 228), (420, 222), (500, 234), (610, 220)], "#C0A6C0", "#F6D6CA"),
        ([(-10, 246), (90, 230), (190, 248), (280, 236), (380, 250), (480, 234), (610, 248)], "#9E96BE", "#EAD0D0"),
        ([(-10, 262), (70, 250), (170, 266), (260, 250), (350, 268), (450, 254), (540, 266), (610, 256)], "#7C82B2", "#DCC8D4"),
        ([(-10, 282), (110, 266), (220, 286), (330, 272), (430, 290), (520, 276), (610, 288)], "#5C68A0", "#C8BCD6"),
        ([(-10, 304), (80, 292), (190, 310), (300, 298), (400, 314), (500, 300), (610, 312)], "#424E88", "#B8B4D4"),
    ]
    for k, (ctrl, col, mcol) in enumerate(ridges):
        sv, line = soft_ridge(ctrl, 30 + k, col, bumps=col if k >= 3 else None, bump_r=(1.2 + k * 0.4, 2.5 + k * 0.6))
        out.append(sv)
        if k >= 2:
            # rim light along the crest facing the sun
            seg = [p for p in line if abs(p[0] - SX) < 200]
            out.append(f'<polyline points="{P(seg)}" fill="none" stroke="#FFE6C0" stroke-width="{1.2 + 0.1 * k:.1f}" opacity="{0.5 - k * 0.05:.2f}"/>')
        top = max(y for _, y in ctrl)
        out.append(defs(lg(f"{u}-m{k}", [(0, mcol, 0), (1, mcol, 0.9)], 0, top - 26, 0, top + 14, units="userSpaceOnUse")))
        out.append(f'<rect x="-10" y="{top - 26}" width="620" height="{444 - top + 26}" fill="url(#{u}-m{k})"/>')
        out.append(mist(SX - 150 + k * 60, top + 4, 180, 10, "#FFF2E2", f"{u}-wisp{k}", 0.6))
    # near hillside meadow: Cades Cove style clearing with the cabin
    hill = rough([(-10, 352), (90, 340), (200, 344), (320, 356), (440, 350), (530, 340), (610, 346)], 41, 4, 4)
    out.append(f'<polygon points="{P(hill + [(610, 444), (-10, 444)])}" fill="url(#{u}-meadow)"/>')
    out.append(f'<polyline points="{P(hill)}" fill="none" stroke="#F6D2A0" stroke-width="2" opacity="0.6"/>')
    out.append(strokes_h(220, 3, (-10, 346, 610, 444), ["#6A7E5A", "#3A4E3E", "#8A9A6A", "#2A3A30"], w=(6, 18), sw=(1, 2.2)))
    # tree line on the meadow's edge, backlit
    trees = []
    rnd = random.Random(44)
    for x in (24, 46, 520, 548, 576, 600):
        y = y_on(hill, x)
        h = rnd.uniform(70, 110)
        trees.append(leafy(x, y - h * 0.62, h * 0.32, h * 0.42, int(x), "#1E2A32", "#2A3A40", "#4A5A50", n=14, lx=0.6, ly=-0.6, dab=0.22))
        trees.append(f'<rect x="{x - 2:.0f}" y="{y - h * 0.3:.0f}" width="4" height="{h * 0.3:.0f}" fill="#1E2420"/>')
    trees.append(con(496, y_on(hill, 496) + 2, 96, "#1E2A2E", 5, light="#5A6A5A"))
    trees.append(con(80, y_on(hill, 80) + 2, 72, "#1E2A2E", 6, light="#5A6A5A"))
    out.append("".join(trees))
    # the cabin with smoke curling from the chimney
    cx, cb = 196, 396
    out.append(f'<ellipse cx="{cx + 60}" cy="{cb + 2}" rx="118" ry="8" fill="#1A2420" opacity="0.5"/>')
    out.append(log_cabin(cx, cb, 1.3, u))
    K = 1.3
    for i in range(9):
        t = i / 8
        out.append(mist(cx - 23 * K + t * 40 + math.sin(t * 5) * 6, cb - 104 * K - 6 - t * 70, 6 + t * 18, 5 + t * 9, "#EEE8EE", f"{u}-smk{i}", 0.75 - t * 0.45))
    # worm fence zig-zagging across the meadow and a pair of deer
    fence = []
    for i in range(12):
        x0 = -10 + i * 30
        y0 = 418 - i * 1.5
        a, b = (x0, y0), (x0 + 30, y0 - 7 if i % 2 == 0 else y0 + 7)
        for j in range(4):
            fence.append(f'<line x1="{a[0]:.0f}" y1="{a[1] - j * 5:.1f}" x2="{b[0]:.0f}" y2="{b[1] - j * 5:.1f}" stroke="{"#5A4232" if j % 2 else "#6E5040"}" stroke-width="2.6" stroke-linecap="round"/>')
        fence.append(f'<line x1="{a[0]:.0f}" y1="{a[1] - 17:.1f}" x2="{b[0]:.0f}" y2="{b[1] - 17:.1f}" stroke="#F2C890" stroke-width="0.9" opacity="0.6"/>')
    out.append("".join(fence))
    out.append(deer(404, 390, 0.95))
    out.append(deer(500, 402, 0.9, flip=-1, head_down=True, col="#7A4E34"))
    out.append(grass(150, 7, (-10, 412, 610, 444), ["#5A6E4A", "#8A9A5A", "#C8B888", "#2E3E32"], h=(6, 16)))
    out.append(dots(50, 9, (-10, 400, 610, 444), "#F2E2B0", r=(0.8, 1.8), opacity=(0.5, 0.9)))
    out.append(birds_v([(250, 160, 10), (268, 152, 8)], "#4A4060"))
    return "\n".join(out)


# ================================================================ Blue Ridge Parkway (autumn afternoon, an overlook)
AUTUMN = [("#A82A24", "#E0604A"), ("#C8462A", "#F08A5A"), ("#E0702A", "#F6AE5A"), ("#E8922E", "#F8C46A"),
          ("#E8B83A", "#FADC7A"), ("#C89A2A", "#F2CC5A"), ("#6A7A34", "#A2AA5A"), ("#3E5A36", "#6E8A4E"), ("#8A3A26", "#C8644A")]


def canopy(poly, seed, n, rmin, rmax, pal=AUTUMN, lx=0.35, ly=-0.35, weights=None, cluster=0.75):
    """Forest canopy seen from a distance: rounded crowns painted back to front, each with a shaded
    underside and a sunlit cap. Colours group into stands (low-frequency noise) like real hardwood forest."""
    rnd = random.Random(seed)
    xs = [x for x, _ in poly]
    ys = [y for _, y in poly]
    y0, y1 = min(ys), max(ys)
    pts = []
    tries = 0
    while len(pts) < n and tries < n * 30:
        tries += 1
        x, y = rnd.uniform(min(xs), max(xs)), rnd.uniform(y0, y1)
        if inside(poly, x, y):
            pts.append((x, y))
    pts.sort(key=lambda p: p[1])
    out = []
    ph = seed * 1.7
    for x, y in pts:
        t = (y - y0) / max(1, y1 - y0)
        r = (rmin + (rmax - rmin) * t) * rnd.uniform(0.75, 1.2)
        if rnd.random() < cluster:
            v = (math.sin(x * 0.021 + ph) + math.sin(y * 0.06 + x * 0.011 + ph * 2) * 0.8 + 1.8) / 3.6
            d, l_ = pal[max(0, min(len(pal) - 1, int(v * len(pal) + rnd.uniform(-0.8, 0.8))))]
        else:
            d, l_ = rnd.choices(pal, weights=weights)[0]
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{d}"/>'
                   f'<circle cx="{x - r * lx * 0.5:.1f}" cy="{y + r * 0.45:.1f}" r="{r * 0.6:.1f}" fill="#2A1420" opacity="0.22"/>'
                   f'<circle cx="{x + r * lx:.1f}" cy="{y + r * ly:.1f}" r="{r * 0.5:.1f}" fill="{l_}" opacity="0.8"/>')
    return "".join(out)


def forest_mosaic(poly, seed, n_patch, n_crown, rmin, rmax, base="#6A3A26", pal=AUTUMN, weights=None, cid=None):
    """Dense autumn hardwood forest: dark base, a mosaic of colour patches, then individual crowns on top."""
    ys = [y for _, y in poly]
    xs = [x for x, _ in poly]
    box = (min(xs), min(ys), max(xs), max(ys))
    out = [f'<polygon points="{P(poly)}" fill="{base}"/>']
    inner = patches(n_patch, seed, box, [d for d, _ in pal], w=(rmin * 2, rmax * 3), h=(rmin, rmax * 1.2), op=(0.7, 1))
    inner += canopy(poly, seed + 1, n_crown, rmin, rmax, pal=pal, weights=weights)
    if cid:
        out.append(f'<clipPath id="{cid}"><polygon points="{P(poly)}"/></clipPath><g clip-path="url(#{cid})">{inner}</g>')
    else:
        out.append(inner)
    return "".join(out)


def catmull(pts, steps=12):
    out = []
    p = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(steps):
            t = k / steps
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out


def offset(line, wfn, side):
    out = []
    for i, (x, y) in enumerate(line):
        a = line[max(0, i - 1)]
        b = line[min(len(line) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = wfn(y) / 2 * side
        out.append((x + nx * w, y + ny * w * 0.35))
    return out


def vintage_car(x, base, k, body="#2E8A8A", flip=1):
    return (f'<g transform="translate({x:.1f} {base:.1f}) scale({k * flip:.3f} {k:.3f})">'
            '<ellipse cx="0" cy="1" rx="54" ry="5" fill="#1A1A1A" opacity="0.35"/>'
            f'<path d="M -50 -10 Q -52 -22 -40 -24 L -26 -26 Q -16 -42 4 -42 Q 22 -42 30 -28 L 46 -24 Q 54 -20 52 -10 Z" fill="{body}"/>'
            '<path d="M -22 -27 Q -14 -38 2 -38 L 2 -27 Z M 6 -38 Q 20 -38 26 -27 L 6 -27 Z" fill="#CFE2EA"/>'
            '<path d="M -50 -14 L 52 -14" stroke="#F4F0E6" stroke-width="2.4"/><path d="M -40 -24 L -26 -26 Q -16 -42 4 -42 Q 22 -42 30 -28" stroke="#FFE2B0" stroke-width="1.6" fill="none"/>'
            '<circle cx="-30" cy="-8" r="9" fill="#1A1A1A"/><circle cx="32" cy="-8" r="9" fill="#1A1A1A"/><circle cx="-30" cy="-8" r="4" fill="#C8C8C8"/><circle cx="32" cy="-8" r="4" fill="#C8C8C8"/>'
            '<rect x="48" y="-20" width="5" height="4" fill="#FF6A4A"/></g>')


def blue_ridge():
    u = "brp"
    out = [defs(
        lg(f"{u}-sky", [(0, "#4C78B4"), (0.5, "#8EB2D6"), (0.82, "#E6D6C2"), (1, "#F6DCB4")], 0, 40, 0, 250, units="userSpaceOnUse"),
        lg(f"{u}-road", [(0, "#6A6470"), (1, "#3E3A40")], 0, 260, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-hz", [(0, "#C8D6E8", 0), (1, "#C8D6E8", 0.7)]),
        lg(f"{u}-shd", [(0, "#2A1A30", 0.35), (0.5, "#2A1A30", 0.05), (1, "#2A1A30", 0)], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(560, 170, 240, "#FFE8B8", f"{u}-sun", 0.7))
    # fair-weather clouds
    for k, (cx, cy, w) in enumerate(((150, 112, 70), (420, 96, 90), (520, 140, 50))):
        out.append(cloud_bank(cx - w, cx + w, cy, 20, 20 + k, "#F6F2EE", "#B8C0D6", "#FFFFFF", n=int(w * 0.9), r=(3, 14), flat=f"{u}-cf{k}"))
    # the blue ridges that give the parkway its name
    for k, (ctrl, col) in enumerate((
        ([(-10, 214), (90, 200), (200, 210), (300, 194), (420, 206), (520, 196), (610, 204)], "#A8BCDC"),
        ([(-10, 228), (110, 214), (240, 226), (360, 212), (470, 224), (610, 214)], "#8AA2CC"),
        ([(-10, 244), (80, 236), (190, 248), (300, 232), (420, 246), (520, 236), (610, 244)], "#6E88BA"),
    )):
        sv, line = soft_ridge(ctrl, 50 + k, col, bumps=col if k == 2 else None, bump_r=(1.2, 2.4))
        out.append(sv)
        out.append(f'<rect x="-10" y="{min(y for _, y in ctrl) + 6}" width="620" height="60" fill="url(#{u}-hz)"/>')
    # far hill the road climbs toward, then the folds of the mountainside it hugs
    W = [3, 3, 4, 5, 4, 5, 2, 2, 3]
    far = rough([(-10, 262), (90, 244), (200, 250), (330, 262), (430, 256), (520, 248), (610, 258)], 61, 4, 4)
    out.append(forest_mosaic(far + [(610, 330), (-10, 330)], 3, 260, 900, 1.8, 3.4, base="#7A4A30", weights=W, cid=f"{u}-f1"))
    out.append(f'<rect x="-10" y="240" width="620" height="90" fill="url(#{u}-hz)" opacity="0.6"/>')
    fold = rough([(-10, 300), (70, 288), (150, 300), (240, 318), (330, 324), (420, 316), (520, 300), (610, 306)], 64, 4, 4)
    out.append(forest_mosaic(fold + [(610, 444), (-10, 444)], 4, 300, 1000, 2.8, 6, base="#6A3A26", weights=W, cid=f"{u}-f2"))
    out.append(f'<polygon points="{P(fold + [(610, 444), (-10, 444)])}" fill="url(#{u}-shd)"/>')
    # broad masses of shade in the hollows and warm light on the slopes facing the afternoon sun
    out.append(f'<g clip-path="url(#{u}-f2)">' + mist(330, 352, 170, 26, "#3A1E2A", f"{u}-hol1", 0.45) + mist(40, 330, 120, 30, "#3A1E2A", f"{u}-hol2", 0.4)
               + mist(470, 330, 160, 30, "#FFD27A", f"{u}-lit1", 0.3) + "</g>")
    out.append(f'<g clip-path="url(#{u}-f1)">' + mist(150, 272, 160, 14, "#3A2A40", f"{u}-hol3", 0.3) + mist(470, 262, 150, 14, "#FFE0A0", f"{u}-lit2", 0.3) + "</g>")
    out.append(f'<polyline points="{P(fold)}" fill="none" stroke="#FFE2A8" stroke-width="1.6" opacity="0.5"/>')
    # the parkway: S-curve along the mountainside with a stone guard wall on the valley side
    cl = catmull([(660, 470), (520, 418), (360, 392), (220, 372), (140, 352), (150, 330), (260, 312), (380, 296), (470, 282), (540, 270), (620, 262)], 10)
    wfn = lambda y: 3 + max(0, y - 255) * 0.3
    L, R = offset(cl, wfn, 1), offset(cl, wfn, -1)
    out.append(f'<polygon points="{P(L + R[::-1])}" fill="url(#{u}-road)"/>')
    out.append(f'<polyline points="{P(L)}" fill="none" stroke="#E8E2D6" stroke-width="1.2" opacity="0.8"/>')
    out.append(f'<polyline points="{P(R)}" fill="none" stroke="#E8E2D6" stroke-width="1.2" opacity="0.8"/>')
    # double yellow centre line, dashed into the distance
    out.append(f'<polyline points="{P(cl)}" fill="none" stroke="#F2C23A" stroke-width="1.6" opacity="0.9"/>')
    # the low stone wall on the downhill edge
    wall = []
    for (x, y), (x2, y2) in zip(R, R[1:]):
        h = max(1, wfn(y) * 0.12)
        wall.append(f'<polygon points="{x:.1f},{y:.1f} {x2:.1f},{y2:.1f} {x2:.1f},{y2 + h:.1f} {x:.1f},{y + h:.1f}" fill="#9A9088"/>')
    out.append("".join(wall))
    # a car taking the bend in the afternoon light
    out.append(vintage_car(268, 314, 0.42, body="#2E8A8A", flip=-1))
    out.append(vintage_car(470, 410, 0.7, body="#C8462A"))
    # trees in front of the lower stretch of road
    out.append(canopy([(-10, 444), (-10, 386), (120, 380), (200, 392), (300, 404), (420, 418), (500, 436), (520, 444)], 8, 90, 7, 14, weights=W))
    # the overlook: stone wall, a couple taking in the view
    ov = rough([(-10, 404), (120, 398), (250, 410), (330, 444)], 63, 3, 3)
    out.append(f'<polygon points="{P(ov + [(-10, 444)])}" fill="#6A6460"/>')
    stones = []
    rnd = random.Random(7)
    for row in range(3):
        x = -10 + row * 7
        while x < 300:
            y = y_on(ov, x)
            if y is None:
                break
            w = rnd.uniform(14, 24)
            yy = y + row * 9 + 2
            stones.append(f'<rect x="{x:.0f}" y="{yy:.0f}" width="{w - 2:.0f}" height="7.5" rx="2.5" fill="{rnd.choice(["#A8A098", "#8E867E", "#B8B0A6", "#9A8C80"])}"/>')
            x += w
    out.append("".join(stones))
    out.append(f'<polyline points="{P(ov)}" fill="none" stroke="#F6E0B8" stroke-width="2.2" opacity="0.8"/>')
    out.append(figure(120, 430, 46, body="#2E4A6A", head="#3A2A20"))
    out.append(figure(140, 431, 42, body="#C8562E", head="#6A4428"))
    out.append('<path d="M 132 392 L 156 374" stroke="#C8562E" stroke-width="3.4" stroke-linecap="round"/>')
    out.append(birds_v([(300, 150, 12), (322, 142, 9)], "#3A4060"))
    return "\n".join(out)


# ================================================================ Lake Tahoe (granite cove on the east shore, midday)
def blob_pts(cx, cy, rx, ry, seed, k=14, jag=0.12, flat_bottom=False):
    rnd = random.Random(seed)
    pts = []
    for i in range(k):
        a = 2 * math.pi * i / k
        rr = 1 + rnd.uniform(-jag, jag)
        y = cy + ry * rr * math.sin(a)
        if flat_bottom and math.sin(a) > 0.3:
            y = cy + ry * 0.45 + ry * 0.1 * math.sin(a)
        pts.append((cx + rx * rr * math.cos(a), y))
    return pts


def boulder(cx, cy, rx, ry, seed, u, lit="#F0DEC0", mid="#CDB494", dark="#7A6A62", water=None):
    """Rounded granite boulder: lit dome, shadow side low right, cracks, salt-and-pepper speckle and,
    if it sits in water, a wet dark band at the waterline."""
    gid = f"{u}-bg{seed}"
    pts = blob_pts(cx, cy, rx, ry, seed, 16, 0.1, flat_bottom=True)
    out = [defs(rg(gid, [(0, lit), (0.55, mid), (1, dark)], cx=0.35, cy=0.3, r=0.85)),
           f'<polygon points="{P(pts)}" fill="url(#{gid})"/>',
           f'<clipPath id="{gid}c"><polygon points="{P(pts)}"/></clipPath><g clip-path="url(#{gid}c)">']
    rnd = random.Random(seed)
    out.append(dots(int(rx * ry / 18), seed, (cx - rx, cy - ry, cx + rx, cy + ry), "#5A4E4A", r=(0.5, 1.3), opacity=(0.3, 0.7)))
    out.append(dots(int(rx * ry / 60), seed + 1, (cx - rx, cy - ry, cx + rx, cy + ry), "#FFF6E8", r=(0.5, 1), opacity=(0.3, 0.6)))
    for _ in range(2 + int(rx / 30)):
        x0 = cx + rnd.uniform(-rx * 0.6, rx * 0.6)
        y0 = cy - ry * rnd.uniform(0.3, 0.9)
        c = rough([(x0, y0), (x0 + rnd.uniform(-10, 10), y0 + ry * 0.5), (x0 + rnd.uniform(-16, 16), y0 + ry * 1.2)], seed + _, 4, 3)
        out.append(f'<polyline points="{P(c)}" fill="none" stroke="#5A4A44" stroke-width="1.5" opacity="0.55"/>')
    out.append(f'<ellipse cx="{cx + rx * 0.45:.1f}" cy="{cy + ry * 0.35:.1f}" rx="{rx * 0.7:.1f}" ry="{ry * 0.6:.1f}" fill="#4A3A40" opacity="0.25"/>')
    if water is not None:
        out.append(f'<rect x="{cx - rx - 5:.0f}" y="{water - 3:.0f}" width="{rx * 2 + 10:.0f}" height="{ry * 2:.0f}" fill="#3A5A60" opacity="0.55"/>')
    out.append("</g>")
    return "".join(out)


def jeffrey_pine(x, base, h, seed, lean=0.0, light=-1):
    """Jeffrey pine: straight cinnamon trunk with dark plates, open crown of needle tufts on upswept branches."""
    rnd = random.Random(seed)
    w = h * 0.035
    tx = x + lean * h
    out = [f'<path d="M {x - w:.1f} {base:.1f} L {tx - w * 0.3:.1f} {base - h:.1f} L {tx + w * 0.3:.1f} {base - h:.1f} L {x + w:.1f} {base:.1f} Z" fill="#9A5A36"/>',
           f'<path d="M {x + w * 0.1:.1f} {base:.1f} L {tx + w * 0.05:.1f} {base - h:.1f} L {tx + w * 0.3:.1f} {base - h:.1f} L {x + w:.1f} {base:.1f} Z" fill="#5A3022" opacity="0.6"/>']
    out.append('<g stroke="#4A2A1E" stroke-width="1" opacity="0.7">' + "".join(
        f'<line x1="{x - w * 0.6 + lean * h * t:.1f}" y1="{base - h * t:.1f}" x2="{x + w * 0.5 + lean * h * t:.1f}" y2="{base - h * t - 3:.1f}"/>' for t in [rnd.uniform(0.02, 0.6) for _ in range(int(h / 8))]) + "</g>")
    tufts = []
    for i in range(13):
        t = 0.3 + i * 0.054
        by = base - h * t
        bx = x + lean * h * t
        side = -1 if i % 2 else 1
        L = h * (0.24 - 0.014 * i) * rnd.uniform(0.8, 1.2)
        ex, ey = bx + side * L, by - L * 0.35
        out.append(f'<path d="M {bx:.1f} {by:.1f} Q {bx + side * L * 0.5:.1f} {by:.1f} {ex:.1f} {ey:.1f}" stroke="#5A3A2A" stroke-width="{max(1, w * 0.4):.1f}" fill="none"/>')
        tufts.append((ex, ey, L * 0.5))
        tufts.append((bx + side * L * 0.5, by - L * 0.15, L * 0.42))
        tufts.append((bx + side * L * 0.15, by - L * 0.05, L * 0.3))
    tufts.append((tx, base - h * 1.02, h * 0.08))
    for k, (cx, cy, r) in enumerate(tufts):
        out.append(leafy(cx, cy, r, r * 0.6, seed * 50 + k, "#1E3A2E", "#2E5A3E", "#6A9A52", n=7, lx=light * 0.5, ly=-0.6, dab=0.3))
    return "".join(out)


def lake_tahoe():
    u = "tah"
    HZ = 236
    out = [defs(
        lg(f"{u}-sky", [(0, "#2A62B4"), (0.6, "#6EA4DA"), (1, "#CDE4F2")], 0, 40, 0, HZ, units="userSpaceOnUse"),
        lg(f"{u}-deep", [(0, "#3A6AA8"), (0.3, "#1E4E96"), (1, "#16407E")], 0, HZ, 0, 340, units="userSpaceOnUse"),
        lg(f"{u}-cove", [(0, "#2AA8B8"), (0.5, "#4CC8C4"), (1, "#8EE2D0")], 0, 300, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-mtn", [(0, "#8A9AC0"), (1, "#5A6E9A")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(cloud_bank(380, 520, 120, 14, 3, "#FAFAFA", "#C8D4E6", "#FFFFFF", n=60, r=(4, 13), flat=f"{u}-cf1"))
    out.append(cloud_bank(80, 180, 96, 8, 4, "#FAFAFA", "#C8D4E6", "#FFFFFF", n=36, r=(3, 9), flat=f"{u}-cf2"))
    # the Sierra crest across the lake, still holding snow
    sv, _ = massif(f"{u}-m", [(-10, 222), (50, 196), (110, 178), (150, 188), (200, 158), (236, 174), (300, 196), (360, 186), (420, 200), (480, 176), (530, 190), (610, 206)],
                   5, HZ, f"url(#{u}-mtn)", shade="#3A4A78", shade_op=0.4, amp=4, light=1, snow="#FFFFFF", snow_y=196, snow_amp=12,
                   tex=("#3A4A70", "#E8EEF8"), tex_op=(0.15, 0.35), tex_n=0.6, rim="#FFFFFF", rim_w=1.2, haze="#B8CCE4")
    out.append(sv)
    fl = rough([(-10, 230), (150, 228), (300, 232), (450, 229), (610, 231)], 6, 2, 3)
    out.append(f'<polygon points="{P(fl + [(610, HZ + 2), (-10, HZ + 2)])}" fill="#3A5A6A"/>')
    out.append(trees_on(fl, 9, ["#2E4A52", "#36545A"], density=2.4, hmin=3, hmax=7, sink=3))
    # open lake: deep cobalt with wind lines and sun glitter
    out.append(f'<rect x="-10" y="{HZ}" width="620" height="210" fill="url(#{u}-deep)"/>')
    out.append(strokes_h(140, 4, (-10, HZ + 2, 610, 330), ["#6A9AD8", "#2A5AA0", "#A8CCF0"], w=(6, 26), sw=(0.8, 1.6), op=(0.3, 0.7)))
    out.append(dots(36, 5, (200, HZ + 4, 440, 290), "#FFFFFF", r=(0.6, 1.4), opacity=(0.4, 0.9)))
    # the shallow cove over pale granite sand: turquoise, with boulders seen through the water
    cove = rough([(-10, 322), (90, 306), (200, 300), (330, 304), (450, 300), (540, 312), (610, 320)], 12, 6, 4)
    out.append(f'<polygon points="{P(cove + [(610, 444), (-10, 444)])}" fill="url(#{u}-cove)"/>')
    out.append(defs(lg(f"{u}-edge", [(0, "#1E4E96", 0.85), (1, "#1E4E96", 0)], 0, 296, 0, 340, units="userSpaceOnUse")))
    out.append(f'<rect x="-10" y="296" width="620" height="44" fill="url(#{u}-edge)"/>')
    out.append(f'<clipPath id="{u}-cv"><polygon points="{P(cove + [(610, 444), (-10, 444)])}"/></clipPath>')
    sub = []
    rnd = random.Random(14)
    rocks = sorted(((rnd.uniform(30, 570), rnd.uniform(320, 430)) for _ in range(16)), key=lambda p: p[1])
    for x, y in rocks:
        t = (y - 310) / 120
        rx = rnd.uniform(14, 34) * (0.6 + t)
        for k_ in range(rnd.choice((1, 2, 2, 3))):
            ox, oy, sc = (0, 0, 1) if k_ == 0 else (rnd.uniform(-1, 1) * rx, rnd.uniform(-0.2, 0.3) * rx, rnd.uniform(0.4, 0.7))
            r_ = rx * sc
            sd = rnd.randrange(999)
            sub.append(f'<polygon points="{Pi(blob_pts(x + ox, y + oy + r_ * 0.06, r_, r_ * 0.5, sd, 12, 0.18))}" fill="#22809A" opacity="0.5"/>'
                       f'<polygon points="{Pi(blob_pts(x + ox - r_ * 0.12, y + oy - r_ * 0.06, r_ * 0.8, r_ * 0.36, sd + 1, 11, 0.18))}" fill="#A8E6D6" opacity="0.5"/>'
                       f'<ellipse cx="{x + ox - r_ * 0.32:.0f}" cy="{y + oy - r_ * 0.18:.0f}" rx="{r_ * 0.3:.1f}" ry="{r_ * 0.1:.1f}" fill="#E8FFF4" opacity="0.4"/>')
    # sunlight caustics rippling over the bottom
    for _ in range(70):
        x, y = rnd.uniform(-10, 600), rnd.uniform(318, 440)
        L = rnd.uniform(8, 22)
        sub.append(f'<path d="M {x:.0f} {y:.0f} q {L / 3:.1f} -3 {L / 2:.1f} 0 t {L / 2:.1f} 0" stroke="#EFFFF8" stroke-width="1.1" fill="none" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    out.append(f'<g clip-path="url(#{u}-cv)">' + "".join(sub) + "</g>")
    # a kayaker gliding over the shallows, a wake behind
    kx, ky = 352, 352
    out.append(f'<path d="M {kx + 30} {ky + 2} L {kx + 90} {ky - 5} M {kx + 30} {ky + 5} L {kx + 90} {ky + 11}" stroke="#EFFFFA" stroke-width="1.4" opacity="0.45"/>')
    out.append(f'<ellipse cx="{kx}" cy="{ky + 6}" rx="38" ry="4" fill="#1E6A7A" opacity="0.4"/>')
    out.append(f'<path d="M {kx - 36} {ky} Q {kx} {ky + 8} {kx + 36} {ky} Q {kx} {ky - 4} {kx - 36} {ky} Z" fill="#F2B52A"/><path d="M {kx - 34} {ky} Q {kx} {ky - 3} {kx + 34} {ky}" stroke="#FFE08A" stroke-width="1.4" fill="none"/>')
    out.append(f'<path d="M {kx - 4} {ky - 2} L {kx - 6} {ky - 18} Q {kx} {ky - 21} {kx + 6} {ky - 18} L {kx + 4} {ky - 2} Z" fill="#D8463A"/><circle cx="{kx}" cy="{ky - 24}" r="5" fill="#3A2A22"/>'
               f'<path d="M {kx - 7} {ky - 30} Q {kx} {ky - 33} {kx + 7} {ky - 30} L {kx + 9} {ky - 27} L {kx - 9} {ky - 27} Z" fill="#F4EEE2"/>')
    out.append(f'<path d="M {kx - 30} {ky - 4} L {kx + 28} {ky - 22}" stroke="#2A2A2A" stroke-width="2"/><path d="M {kx - 36} {ky - 1} l 8 -6 l 2 3 Z M {kx + 26} {ky - 24} l 8 -4 l -1 4 Z" fill="#2A2A2A"/>')
    # granite boulders breaking the surface, foreground and framing
    for args in ((120, 318, 30, 12, 1, 322), (470, 316, 22, 9, 2, 320), (520, 330, 34, 16, 3, 336), (210, 340, 18, 8, 4, 343)):
        cx, cy, rx, ry, sd, wl = args
        out.append(boulder(cx, cy, rx, ry, sd, u, water=wl))
        out.append(f'<path d="M {cx - rx - 4} {wl + 1} Q {cx} {wl + 5} {cx + rx + 4} {wl + 1}" stroke="#EFFFFA" stroke-width="1.6" fill="none" opacity="0.8"/>')
    out.append(boulder(60, 420, 110, 52, 7, u))
    out.append(boulder(170, 446, 70, 30, 8, u))
    out.append(boulder(560, 410, 100, 60, 9, u))
    out.append(boulder(450, 452, 70, 30, 10, u))
    out.append(dots(40, 21, (-10, 400, 610, 444), "#EFFFFA", r=(0.8, 2), opacity=(0.5, 1)))
    # Jeffrey pines rooted in the cracks of the granite
    out.append(jeffrey_pine(548, 370, 290, 4, lean=-0.03))
    out.append(jeffrey_pine(30, 386, 220, 6, lean=0.04))
    out.append(birds_v([(260, 126, 10), (276, 134, 7)], "#2A3A5A"))
    return "\n".join(out)


# ================================================================ Glacier (Lake McDonald's coloured stones at dusk)
PEBBLES = ["#8A3436", "#9E4A3E", "#6A2E34", "#4E7258", "#3E6456", "#3A6874", "#566684", "#B88E52", "#CEC4B0", "#644A62", "#A87452", "#727E62"]


def pebbles(n, seed, box, glaze=None, glaze_op=0.0, scale=(4, 16), light=(-0.3, -0.35)):
    """Rounded argillite pebbles in reds, greens, blues and ochres, smaller with distance; optional water glaze."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    pts = sorted(((rnd.uniform(x0, x1), rnd.uniform(y0, y1)) for _ in range(n)), key=lambda p: p[1])
    out = []
    for x, y in pts:
        t = (y - y0) / max(1, y1 - y0)
        r = (scale[0] + (scale[1] - scale[0]) * t ** 1.3) * rnd.uniform(0.6, 1.3)
        ry = r * rnd.uniform(0.45, 0.62)
        a = rnd.uniform(-20, 20)
        c = rnd.choice(PEBBLES)
        tf = f' transform="rotate({a:.0f} {x:.0f} {y:.0f})"'
        out.append(f'<ellipse cx="{x:.0f}" cy="{y + ry * 0.25:.1f}" rx="{r * 1.02:.1f}" ry="{ry:.1f}" fill="#1E1A22" opacity="0.45"{tf}/>'
                   f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{r:.1f}" ry="{ry:.1f}" fill="{c}"{tf}/>'
                   f'<ellipse cx="{x + r * light[0]:.1f}" cy="{y + ry * light[1]:.1f}" rx="{r * 0.5:.1f}" ry="{ry * 0.35:.1f}" fill="#FFFFFF" opacity="0.2"{tf}/>')
    s = "".join(out)
    if glaze:
        s += f'<rect x="{x0 - 20}" y="{y0 - 20}" width="{x1 - x0 + 40}" height="{y1 - y0 + 40}" fill="{glaze}" opacity="{glaze_op}"/>'
    return s


def glacier():
    u = "glc"
    SH = 274
    out = [defs(
        lg(f"{u}-sky", [(0, "#3A64A4"), (0.4, "#86A8CE"), (0.72, "#EED2A0"), (0.9, "#F6D898"), (1, "#F8E2B0")], 0, 40, 0, SH, units="userSpaceOnUse"),
        lg(f"{u}-rock", [(0, "#F4C88A"), (0.3, "#C89A7E"), (0.65, "#6E7088"), (1, "#3A4660")], 0, 96, 0, 270, units="userSpaceOnUse"),
        lg(f"{u}-lake", [(0, "#D8D0B8"), (0.3, "#86A6C0"), (0.7, "#2E7E8C"), (1, "#1E6A72")], 0, SH, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-glz", [(0, "#2A7A88", 0.9), (0.3, "#2A9AA0", 0.6), (0.6, "#2AA6A8", 0.35), (1, "#4CC0B4", 0.1)], 0, 306, 0, 410, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append('<g fill="#FBE2B4" opacity="0.8">' + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{h}"/>' for x, y, w, h in ((150, 92, 90, 4), (210, 104, 60, 3), (440, 82, 80, 4), (500, 96, 60, 3), (330, 118, 50, 3))) + "</g>")
    out.append('<g fill="#C89A7A" opacity="0.35">' + "".join(
        f'<ellipse cx="{x}" cy="{y + 4}" rx="{w}" ry="2"/>' for x, y, w in ((150, 92, 80), (440, 82, 70))) + "</g>")

    def range_(uu, lite=False):
        s_ = []
        sv, _ = massif(f"{uu}-far", [(-10, 230), (60, 200), (130, 176), (190, 196), (260, 168), (330, 188), (420, 160), (480, 182), (560, 172), (610, 196)],
                       31, 262, "#8E9AB8", shade="#3E4A78", shade_op=0.45, amp=5, light=1, snow="#F6F2EC", snow_y=184, snow_amp=10,
                       tex_n=0 if lite else 0.5, rim="#F8E2C0", rim_w=1.2, haze="#C8C8CC")
        s_.append(sv)
        # glacier-carved horns with flat-lying sedimentary bands
        sv, _ = massif(f"{uu}-pk", [(40, 270), (110, 210), (160, 150), (186, 112), (212, 146), (236, 160), (276, 132), (300, 104), (326, 140),
                                     (360, 170), (410, 150), (446, 120), (478, 160), (530, 200), (590, 250)],
                       17, 272, f"url(#{u}-rock)", shade="#28305A", shade_op=0.55, amp=6, depth=5, light=1,
                       snow="#FFF8EC", snow_y=150, snow_amp=22, rim="#FFE6B8", rim_w=2.2, gullies=0 if lite else 14,
                       strata=("#3A3A5A", 0.3, 0.0, 16), ledges=None,
                       tex=("#3A3A58", "#FFE0B8"), tex_op=(0.1, 0.22), tex_n=0.2 if lite else 0.5, haze="#5E6E80", haze_top=200)
        s_.append(sv)
        # forested shores converging toward the far end of the lake
        for poly, sd in (([(-10, 214), (60, 226), (150, 252), (240, 268), (300, SH), (-10, SH)], 3),
                         ([(610, 222), (540, 236), (440, 258), (360, 270), (320, SH), (610, SH)], 4)):
            line = rough(poly[:-1], sd, 5, 4)
            pp = line + [poly[-1]]
            s_.append(f'<polygon points="{P(pp)}" fill="#1E2C30"/>')
            if not lite:
                s_.append(forest_fill(pp, sd + 10, ["#1A2A2C", "#223634", "#182426"], 130, 8, 26, light="#7A8A5A"))
            s_.append(trees_on(line, sd + 20, ["#1A2A2C", "#223634"], density=1.8, hmin=10, hmax=22))
        return "".join(s_)

    scene = range_(u)
    out.append(scene)
    # the lake: mirror-calm far out, then clear shallows over the famous coloured stones
    out.append(f'<clipPath id="{u}-lk"><rect x="-10" y="{SH}" width="620" height="180"/></clipPath>')
    out.append(f'<rect x="-10" y="{SH}" width="620" height="180" fill="url(#{u}-lake)"/>')
    out.append(mirror(SH, f'<rect x="-10" y="40" width="620" height="{SH - 40}" fill="url(#{u}-sky)"/>' + range_(u + "r", True), f"{u}-lk", 0.7))
    out.append(defs(lg(f"{u}-fade", [(0, "#2A6A7A", 0), (0.6, "#2A6A7A", 0.35), (1, "#1E7A80", 0.8)], 0, SH, 0, 340, units="userSpaceOnUse")))
    out.append(f'<rect x="-10" y="{SH}" width="620" height="180" fill="url(#{u}-fade)"/>')
    out.append(ripple_lines(30, 6, (-10, SH + 4, 600, 340), "#F8E8C8", op=(0.2, 0.5), w=(30, 90), sw=1.1))
    out.append(f'<rect x="-10" y="{SH - 1}" width="620" height="2" fill="#F8E8C8" opacity="0.5"/>')
    # a rowboat drifting out on the still water
    bx, by = 400, 306
    out.append(f'<path d="M {bx - 60} {by + 4} L {bx + 60} {by + 4}" stroke="#F8E8C8" stroke-width="1" opacity="0.5"/>'
               f'<path d="M {bx - 22} {by - 4} L {bx + 22} {by - 4} L {bx + 16} {by + 2} L {bx - 18} {by + 2} Z" fill="#B83A2E"/>'
               f'<path d="M {bx - 22} {by - 4} L {bx + 22} {by - 4}" stroke="#F2C8A8" stroke-width="1.2"/>'
               f'<path d="M {bx - 4} {by - 4} L {bx - 5} {by - 16} Q {bx} {by - 18} {bx + 5} {by - 16} L {bx + 4} {by - 4} Z" fill="#2E3A5A"/><circle cx="{bx}" cy="{by - 20}" r="3.6" fill="#2A2020"/>'
               f'<path d="M {bx - 30} {by + 6} L {bx + 30} {by - 12}" stroke="#4A3022" stroke-width="1.4"/>'
               f'<path d="M {bx - 20} {by + 4} L {bx + 20} {by + 4} L {bx + 14} {by + 9} L {bx - 16} {by + 9} Z" fill="#B83A2E" opacity="0.25"/>')
    # shallows: stones seen through clear water, then the dry stones of the beach
    wl = rough([(-10, 404), (120, 398), (260, 404), (400, 400), (520, 396), (610, 402)], 22, 4, 4)
    out.append(f'<clipPath id="{u}-sw"><polygon points="{P([(-10, 306)] + [(610, 306)] + wl[::-1])}"/></clipPath>')
    caus = []
    rnd = random.Random(31)
    for _ in range(60):
        x, y = rnd.uniform(-10, 600), rnd.uniform(340, 404)
        L = rnd.uniform(10, 26)
        caus.append(f'<path d="M {x:.0f} {y:.0f} q {L / 3:.1f} -3 {L / 2:.1f} 0 t {L / 2:.1f} 0" stroke="#E8FFF8" stroke-width="1.1" fill="none" opacity="{rnd.uniform(0.25, 0.55):.2f}"/>')
    out.append(defs(lg(f"{u}-mk", [(0, "#000000"), (0.4, "#FFFFFF")], 0, 306, 0, 360, units="userSpaceOnUse"),
                    f'<mask id="{u}-msk"><rect x="-10" y="300" width="620" height="120" fill="url(#{u}-mk)"/></mask>'))
    out.append(f'<g clip-path="url(#{u}-sw)"><g mask="url(#{u}-msk)"><rect x="-10" y="306" width="620" height="110" fill="#2A6A70"/>' + pebbles(500, 4, (-10, 316, 610, 410), scale=(3, 14))
               + f'<rect x="-10" y="306" width="620" height="112" fill="url(#{u}-glz)"/>'
               + "".join(caus) + ripple_lines(24, 9, (-10, 330, 600, 404), "#F2F0E0", op=(0.25, 0.5), w=(20, 60), sw=1.1) + "</g></g>")
    out.append(f'<polyline points="{P(wl)}" fill="none" stroke="#F4F0F0" stroke-width="1.8" opacity="0.7"/>')
    out.append(f'<polygon points="{P(wl + [(610, 444), (-10, 444)])}" fill="#4A3A40"/>')
    out.append(f'<clipPath id="{u}-bc"><polygon points="{P(wl + [(610, 444), (-10, 444)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-bc)">' + pebbles(240, 7, (-10, 392, 610, 452), scale=(9, 18)) + "</g>")
    out.append(defs(lg(f"{u}-wet", [(0, "#2A5A6A", 0.35), (1, "#2A5A6A", 0)], 0, 396, 0, 416, units="userSpaceOnUse")))
    out.append(f'<polygon points="{P(wl + [(610, 420), (-10, 420)])}" fill="url(#{u}-wet)"/>')
    out.append(birds_v([(250, 132, 11), (270, 124, 8)], "#2E3A50"))
    return "\n".join(out)


# ================================================================ Napa Valley (vineyard rows at sunrise, hot air balloons)
def balloon(cx, cy, r, colors, u, k, burner=False, light=-1):
    """Hot air balloon: striped gores following the envelope's curve, sphere shading from the low sun,
    load tapes, basket on rigging, optional burner glow."""
    def pt(a, b):
        return f"{cx + a * r:.1f} {cy + b * r:.1f}"
    env = (f"M {pt(0, -1)} C {pt(0.78, -1)} {pt(1.02, -0.55)} {pt(1.0, -0.15)} C {pt(0.98, 0.28)} {pt(0.55, 0.62)} {pt(0.27, 0.9)} "
           f"L {pt(-0.27, 0.9)} C {pt(-0.55, 0.62)} {pt(-0.98, 0.28)} {pt(-1.0, -0.15)} C {pt(-1.02, -0.55)} {pt(-0.78, -1)} {pt(0, -1)} Z")
    cid, gid = f"{u}-bc{k}", f"{u}-bs{k}"
    out = [defs(f'<clipPath id="{cid}"><path d="{env}"/></clipPath>',
                rg(gid, [(0, "#FFFFFF", 0.35), (0.45, "#FFFFFF", 0), (0.8, "#1A1030", 0.25), (1, "#1A1030", 0.5)], cx=0.5 + 0.18 * light, cy=0.32, r=0.75))]
    out.append(f'<path d="{env}" fill="{colors[0]}"/>')
    g = []
    n = 10
    ks = [-1 + 2 * i / n for i in range(n + 1)]
    for i in range(n):
        a, b = ks[i], ks[i + 1]
        if i % len(colors) == 0:
            continue
        g.append(f'<path d="M {pt(0, -1)} C {pt(a * 1.32, -1)} {pt(a * 1.32, 0.3)} {pt(a * 0.27, 0.9)} L {pt(b * 0.27, 0.9)} C {pt(b * 1.32, 0.3)} {pt(b * 1.32, -1)} {pt(0, -1)} Z" fill="{colors[i % len(colors)]}"/>')
    for a in ks[1:-1]:
        g.append(f'<path d="M {pt(0, -1)} C {pt(a * 1.32, -1)} {pt(a * 1.32, 0.3)} {pt(a * 0.27, 0.9)}" fill="none" stroke="#2A1A20" stroke-width="{max(0.5, r * 0.02):.1f}" opacity="0.3"/>')
    g.append(f'<path d="M {pt(-1, 0.42)} Q {pt(0, 0.6)} {pt(1, 0.42)}" fill="none" stroke="#2A1A20" stroke-width="{max(0.8, r * 0.05):.1f}" opacity="0.35"/>')
    g.append(f'<rect x="{cx - r * 1.1:.1f}" y="{cy - r * 1.1:.1f}" width="{r * 2.2:.1f}" height="{r * 2.2:.1f}" fill="url(#{gid})"/>')
    out.append(f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>")
    # rigging and basket
    by = cy + r * 1.22
    sw = max(0.6, r * 0.025)
    out.append(f'<path d="M {pt(-0.27, 0.9)} L {cx - r * 0.16:.1f} {by:.1f} M {pt(0.27, 0.9)} L {cx + r * 0.16:.1f} {by:.1f}" stroke="#3A2A22" stroke-width="{sw:.1f}"/>')
    out.append(f'<rect x="{cx - r * 0.17:.1f}" y="{by:.1f}" width="{r * 0.34:.1f}" height="{r * 0.24:.1f}" rx="{r * 0.03:.1f}" fill="#8A5A32"/>'
               f'<rect x="{cx - r * 0.17:.1f}" y="{by:.1f}" width="{r * 0.34:.1f}" height="{r * 0.05:.1f}" fill="#5A3A22"/>'
               f'<rect x="{cx - r * 0.17:.1f}" y="{by + r * 0.08:.1f}" width="{r * 0.12:.1f}" height="{r * 0.16:.1f}" fill="#C8905A" opacity="0.6"/>')
    if burner:
        out.append(glow(cx, cy + r * 1.02, r * 0.4, "#FFB040", f"{u}-bf{k}", 0.85))
        out.append(f'<path d="M {cx - r * 0.06:.1f} {cy + r * 1.1:.1f} Q {cx:.1f} {cy + r * 0.86:.1f} {cx + r * 0.06:.1f} {cy + r * 1.1:.1f} Z" fill="#FFE07A"/>')
    return "".join(out)


def vine_leaf(x, y, s, rot, col="#6A8A3A", vein="#3E5A24", hi="#B8C060"):
    """Five-lobed grape leaf."""
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">'
            f'<path d="M 0 0 C -6 -2 -14 -2 -18 -8 C -14 -10 -18 -16 -14 -20 C -10 -18 -8 -24 -4 -26 C -2 -22 0 -26 2 -30 C 4 -26 6 -24 10 -26 '
            f'C 10 -22 16 -20 18 -18 C 14 -14 20 -12 18 -8 C 14 -4 8 -2 0 0 Z" fill="{col}"/>'
            f'<path d="M 0 0 L 2 -26 M 0 -4 L -14 -16 M 0 -4 L 14 -16 M 0 -2 L -16 -6 M 0 -2 L 16 -6" stroke="{vein}" stroke-width="1" fill="none"/>'
            f'<path d="M -14 -20 C -10 -18 -8 -24 -4 -26 C -2 -22 0 -26 2 -30" stroke="{hi}" stroke-width="1.4" fill="none" opacity="0.8"/></g>')


def grapes(x, y, s, seed):
    rnd = random.Random(seed)
    rows = [5, 6, 5, 4, 4, 3, 2, 1]
    out = [f'<g transform="translate({x} {y}) scale({s})">', '<path d="M 0 -6 Q 2 -14 8 -18" stroke="#5A3A22" stroke-width="2" fill="none"/>']
    for j, n in enumerate(rows):
        for i in range(n):
            gx = (i - (n - 1) / 2) * 7 + rnd.uniform(-1, 1)
            gy = j * 6
            c = rnd.choice(["#4A2A5A", "#5A3268", "#3E2250", "#6A3A72"])
            out.append(f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="4.2" fill="{c}"/><circle cx="{gx - 1.3:.1f}" cy="{gy - 1.4:.1f}" r="1.3" fill="#E8D0F0" opacity="0.6"/>')
    out.append("</g>")
    return "".join(out)


def napa_valley():
    u = "npa"
    C = Cam(f=320, cx=300, vpy=246, eye=6.5)
    out = [defs(
        lg(f"{u}-sky", [(0, "#5A80BC"), (0.35, "#A8B0CC"), (0.62, "#F2C496"), (0.85, "#F8CF7E"), (1, "#FBDC96")], 0, 40, 0, 240, units="userSpaceOnUse"),
        lg(f"{u}-hill", [(0, "#9A8AA0"), (1, "#B8A098")]),
        lg(f"{u}-soil", [(0, "#C8A060"), (1, "#7A5A30")], 0, 246, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-litrow", [(0, "#C8B048"), (1, "#7A8A2A")], 0, 0, 0, 1),
        lg(f"{u}-shrow", [(0, "#4A5A2A"), (1, "#2E3A1E")], 0, 0, 0, 1),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    SX, SY = 84, 198
    out.append(glow(SX, SY, 320, "#FFE09A", f"{u}-sun", 1))
    out.append(f'<circle cx="{SX}" cy="{SY}" r="17" fill="#FFF8DC"/>')
    # Mayacamas hills across the valley, oak-dotted, in the morning haze
    sv, hl = soft_ridge([(-10, 222), (80, 214), (170, 204), (260, 208), (350, 192), (450, 200), (540, 188), (610, 198)], 71, "#B0A0B8")
    out.append(sv)
    sv, hl2 = soft_ridge([(-10, 236), (120, 224), (230, 232), (340, 220), (440, 230), (540, 222), (610, 228)], 72, "#B49CA8", bumps="#B49CA8", bump_r=(1.5, 3))
    out.append(sv)
    out.append(blobs(40, 73, (20, 226, 600, 240), ["#8A7A88", "#9A8A90"], r=(2, 4), opacity=(0.6, 0.9), squash=0.7))
    out.append(glow(SX, SY + 20, 200, "#FFD890", f"{u}-bloom", 0.55))
    out.append(mist(320, 244, 360, 14, "#FFF0D8", f"{u}-mist", 0.85))
    # valley floor and the vineyard: trellised rows running away from us
    out.append(f'<rect x="-10" y="244" width="620" height="200" fill="url(#{u}-soil)"/>')
    # far blocks of vines in other orientations, and a stone winery among cypress and oaks
    out.append(strokes_h(160, 74, (-10, 246, 610, 258), ["#6A7A3A", "#8A9A4A", "#5A6A30"], w=(10, 30), sw=(1.2, 2), op=(0.6, 0.9)))
    wx, wb = 470, 250
    out.append(f'<rect x="{wx}" y="{wb - 14}" width="44" height="14" fill="#D8C0A0"/><polygon points="{wx - 3},{wb - 14} {wx + 22},{wb - 24} {wx + 47},{wb - 14}" fill="#A8604A"/>'
               f'<rect x="{wx + 46}" y="{wb - 10}" width="20" height="10" fill="#C8B090"/><polygon points="{wx + 44},{wb - 10} {wx + 56},{wb - 16} {wx + 68},{wb - 10}" fill="#9A5440"/>'
               + "".join(f'<rect x="{wx + 6 + i * 9}" y="{wb - 9}" width="3" height="5" fill="#FFD890"/>' for i in range(4)))
    for x in (452, 460, 522, 530):
        out.append(f'<path d="M {x} {wb} Q {x - 3} {wb - 14} {x} {wb - 26} Q {x + 3} {wb - 14} {x} {wb} Z" fill="#3A4A2A"/>')
    out.append(leafy(426, 238, 12, 8, 5, "#3A4A2A", "#5A6A30", "#B8A048", n=8, lx=-0.7, ly=-0.5, dab=0.3))
    rows = []
    for i in range(-26, 27):
        X = i * 2.6 + 0.7
        rows.append(X)
    for X in sorted(rows, key=lambda v: -abs(v)):
        Z0, Z1 = 6, 900
        lit = X > 0   # the low sun on the left lights the faces we see on the right-hand rows
        face = C.quad_x(X - (0.35 if X > 0 else -0.35), Z0, Z1, 0.25, 1.7)
        top = [C(X - 0.4, 1.7, Z0), C(X + 0.4, 1.7, Z0), C(X + 0.4, 1.7, Z1), C(X - 0.4, 1.7, Z1)]
        # long morning shadow cast toward the right
        sh = [C(X, 0, Z0), C(X + 2.0, 0, Z0), C(X + 2.0, 0, Z1), C(X, 0, Z1)]
        out.append(f'<polygon points="{P(sh)}" fill="#4A3020" opacity="0.28"/>')
        out.append(f'<polygon points="{P(face)}" fill="{"#8A9A3A" if lit else "#3E4E26"}"/>')
        out.append(f'<polygon points="{P(top)}" fill="{"#C8C060" if lit else "#9AA24A"}"/>')
    # leaf texture and posts on the nearer rows
    rnd = random.Random(75)
    tex = []
    for X in rows:
        if abs(X) > 40:
            continue
        for _ in range(int(150 / (1 + abs(X) * 0.12))):
            Z = 6 * (1.05 ** rnd.uniform(0, 60))
            if Z > 120:
                continue
            on_top = rnd.random() < 0.45
            if on_top:
                x, y = C(X + rnd.uniform(-0.4, 0.4), 1.7, Z)
            else:
                x, y = C(X - (0.35 if X > 0 else -0.35), rnd.uniform(0.4, 1.7), Z)
            r = C.f * rnd.uniform(0.05, 0.1) / Z
            if r < 0.5:
                continue
            if on_top:
                col = rnd.choice(["#E8D870", "#C8C058", "#F0B850", "#A8B048"])
            else:
                col = rnd.choice(["#D8C85A", "#A8B040", "#E8A040", "#C89A3A"] if X > 0 else ["#2E3E1E", "#5A6A30", "#4A5A28", "#8A7A30"])
            tex.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}" opacity="0.8"/>')
        for Z in (8, 12, 18, 27, 40, 60, 90):
            a_, b_ = C(X, 0, Z), C(X, 1.9, Z)
            tex.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#4A3422" stroke-width="{max(0.5, C.f * 0.08 / Z):.1f}"/>')
    out.append("".join(tex))
    # balloons drifting up the valley at sunrise
    for k, (bx, by, r, cols, burner) in enumerate((
            (420, 106, 9, ("#E8B83A", "#2E6AA8"), False), (222, 112, 11, ("#C83A3A", "#F2E2C8"), False),
            (530, 150, 14, ("#3A8A6A", "#F2C24A", "#E86A3A"), False), (316, 138, 30, ("#D8463A", "#F6C23A", "#F4EEE2", "#2E6AA8"), True),
            (178, 176, 22, ("#7A4AA0", "#F2A23A"), True))):
        out.append(balloon(bx, by, r, cols, u, k, burner=burner))
    # foreground: the nearest vine with leaves and a ripe cluster
    for x, y, sc, rot, col in ((30, 430, 1.6, -20, "#5A7A30"), (70, 440, 1.4, 25, "#6A8A3A"), (580, 438, 1.5, 20, "#7A8A30"), (548, 446, 1.3, -30, "#C8902A")):
        out.append(vine_leaf(x, y, sc, rot, col))
    out.append(grapes(92, 392, 1.25, 4))
    out.append(birds_v([(240, 92, 10), (256, 100, 7)], "#4A3A50"))
    return "\n".join(out)


# ================================================================ Big Sur (Bixby Creek Bridge, late afternoon fog)
def cypress_tree(x, base, h, seed, light=1):
    """Wind-sculpted Monterey cypress: twisted trunk leaning inland, flat-topped tiers of dense foliage."""
    rnd = random.Random(seed)
    out = [f'<path d="M {x - 6:.0f} {base:.0f} Q {x - 2:.0f} {base - h * 0.3:.0f} {x - h * 0.12:.0f} {base - h * 0.55:.0f} L {x - h * 0.1:.0f} {base - h * 0.58:.0f} '
           f'Q {x + 6:.0f} {base - h * 0.3:.0f} {x + 7:.0f} {base:.0f} Z" fill="#3A2A26"/>',
           f'<path d="M {x - 2:.0f} {base - h * 0.32:.0f} Q {x + h * 0.12:.0f} {base - h * 0.45:.0f} {x + h * 0.28:.0f} {base - h * 0.5:.0f}" stroke="#3A2A26" stroke-width="4" fill="none" stroke-linecap="round"/>']
    for cx, cy, rx, ry in ((-0.18, 0.66, 0.36, 0.12), (0.2, 0.56, 0.3, 0.1), (-0.05, 0.8, 0.28, 0.1), (0.3, 0.68, 0.2, 0.08), (-0.38, 0.58, 0.18, 0.07)):
        out.append(leafy(x + cx * h, base - cy * h, rx * h, ry * h, rnd.randrange(999), "#1E3026", "#2E4A34", "#6A8A4A", n=12, lx=light * 0.6, ly=-0.7, dab=0.24))
    return "".join(out)


def big_sur():
    u = "bsr"
    HZ = 172
    out = [defs(
        lg(f"{u}-sky", [(0, "#5A84B8"), (0.5, "#9EB8D4"), (0.85, "#F2D6B4"), (1, "#F8DCAE")], 0, 40, 0, HZ, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#7A9AB8"), (0.15, "#3E6A96"), (0.6, "#24507A"), (1, "#1E5A6E")], 0, HZ, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-hill", [(0, "#C8A45A"), (1, "#8A7A3E")], 0, 150, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-conc", [(0, "#F2EADC"), (1, "#C8C0B2")], 0, 0, 1, 0),
        lg(f"{u}-cliff", [(0, "#A88A5A"), (0.5, "#7A6448"), (1, "#4A3A34")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    SX, SY = 540, 140
    out.append(glow(SX, SY, 220, "#FFE6B0", f"{u}-sun", 0.85))
    out.append(f'<circle cx="{SX}" cy="{SY}" r="15" fill="#FFF4D6"/>')
    # Pacific to the horizon, glitter under the sun
    out.append(f'<rect x="-10" y="{HZ}" width="620" height="280" fill="url(#{u}-sea)"/>')
    rnd = random.Random(3)
    out.append("".join(f'<rect x="{SX - (w := rnd.uniform(4, 30)) / 2 + rnd.uniform(-1, 1) * (y - HZ) * 0.5:.0f}" y="{y:.0f}" width="{w:.0f}" height="1.4" fill="#FFF0C8" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>'
                       for y in [HZ + 2 + i * 2.2 for i in range(60)]))
    out.append(strokes_h(120, 4, (300, HZ + 4, 610, 300), ["#A8C4DC", "#2E5A86", "#6A8AB0"], w=(8, 24), sw=(0.8, 1.4), op=(0.3, 0.6)))
    # the fog bank lying offshore, lit gold on top
    for k, (cx, cy, rx, ry, col, op) in enumerate(((470, HZ - 4, 220, 14, "#F8EEDC", 0.9), (560, HZ - 10, 120, 12, "#FFF4E0", 0.85), (380, HZ, 160, 8, "#F2E6D8", 0.8))):
        out.append(mist(cx, cy, rx, ry, col, f"{u}-fb{k}", op))
    # Santa Lucia range behind, hazy blue, then golden coastal hills
    hill = rough([(-10, 168), (80, 158), (170, 172), (260, 182), (340, 200), (420, 230), (470, 256), (520, 286), (560, 330)], 82, 5, 4)
    rl = rough([(-10, 132), (60, 116), (140, 126), (220, 112), (300, 140), (360, 166), (420, 186), (470, 214), (520, 270), (540, 300)], 81, 6, 5, 0.5)
    out.append(f'<polygon points="{P(rl + [(540, 320), (-10, 320)])}" fill="#8A90B4"/>')
    out.append(f'<polyline points="{P(rl[:-8])}" fill="none" stroke="#E8D8D0" stroke-width="1.2" opacity="0.5"/>')
    out.append(mist(160, 170, 240, 20, "#E8E0E4", f"{u}-hz1", 0.6))
    out.append(mist(470, 200, 90, 24, "#E8E0E4", f"{u}-hz2", 0.5))
    hp = hill + [(560, 420), (-10, 420)]
    out.append(f'<polygon points="{P(hp)}" fill="url(#{u}-hill)"/>')
    out.append(f'<clipPath id="{u}-hl"><polygon points="{P(hp)}"/></clipPath>')
    hg = [patches(70, 83, (-10, 170, 500, 300), ["#5A6A3A", "#4A5A32", "#6E7A44", "#3E4A2E"], w=(10, 30), h=(3, 8), op=(0.6, 0.9)),
          strokes_h(140, 84, (-10, 170, 500, 300), ["#E2C47A", "#B8984E", "#8A7A3E"], w=(4, 12), sw=(0.8, 1.6), op=(0.4, 0.8)),
          mist(120, 200, 200, 40, "#3A3050", f"{u}-hs", 0.25)]
    out.append(f'<g clip-path="url(#{u}-hl)">' + "".join(hg) + "</g>")
    out.append(f'<polyline points="{P(hill)}" fill="none" stroke="#FFE6B0" stroke-width="1.6" opacity="0.6"/>')
    # Highway 1 cut into the far headland, a car on it
    road = [(-10, 214), (90, 218), (190, 226), (280, 238), (360, 252), (440, 268)]
    out.append(f'<polyline points="{P(road)}" fill="none" stroke="#5A5048" stroke-width="5"/><polyline points="{P(road)}" fill="none" stroke="#D8CCB4" stroke-width="1.2" opacity="0.7"/>')
    out.append('<rect x="132" y="215" width="9" height="4.5" rx="1.5" fill="#D8463A"/><rect x="134" y="213" width="5" height="3" rx="1" fill="#8AB0C8"/>')
    # Bixby canyon: slopes plunging to the creek mouth and its little beach
    L = [(-10, 236), (60, 250), (120, 286), (170, 330), (220, 372), (270, 400), (300, 410), (-10, 410)]
    R = [(610, 236), (560, 244), (500, 270), (450, 312), (410, 352), (370, 392), (330, 410), (610, 410)]
    # the canyon's far wall winding inland, in cool shade; the creek mouth and its beach at the bottom
    back = rough([(150, 262), (220, 270), (280, 296), (310, 330), (340, 300), (400, 276), (470, 262)], 84, 5, 4)
    bp = back + [(470, 420), (150, 420)]
    out.append(f'<polygon points="{P(bp)}" fill="#3E4A3A"/>')
    out.append(f'<clipPath id="{u}-bk"><polygon points="{P(bp)}"/></clipPath><g clip-path="url(#{u}-bk)">'
               + patches(50, 841, (150, 262, 470, 400), ["#2E3E30", "#465A3A", "#5A6A40", "#26342A"], w=(8, 20), h=(3, 8), op=(0.7, 1))
               + strokes_h(60, 842, (150, 262, 470, 400), ["#A89A5A", "#7A7A48"], w=(4, 10), sw=(0.8, 1.4), op=(0.3, 0.6))
               + f'<rect x="150" y="250" width="320" height="170" fill="#2A2E48" opacity="0.3"/></g>')
    out.append(f'<polyline points="{P(back)}" fill="none" stroke="#E8D8A8" stroke-width="1.2" opacity="0.4"/>')
    out.append('<path d="M 300 334 Q 318 360 300 384 Q 290 398 300 410" stroke="#8AB0C0" stroke-width="3" fill="none" opacity="0.8"/>')
    out.append(f'<path d="M 200 414 Q 260 398 330 394 Q 400 392 470 400 L 470 420 L 200 420 Z" fill="#D8C6A0"/>')
    out.append(f'<path d="M 180 444 L 200 420 Q 300 404 380 400 Q 430 398 470 398 L 610 400 L 610 444 Z" fill="#2E6A80"/>')
    out.append('<path d="M 210 426 Q 300 410 380 412 Q 440 414 470 420" stroke="#FFFFFF" stroke-width="2.4" fill="none" opacity="0.7"/>'
               '<path d="M 196 438 Q 290 424 380 428 Q 440 430 480 436" stroke="#E8F4F4" stroke-width="2" fill="none" opacity="0.55"/>'
               + dots(40, 97, (220, 400, 470, 416), "#FFFFFF", r=(1, 2.4), opacity=(0.6, 1)) +
               '<path d="M 290 416 Q 380 396 470 400" stroke="#FFFFFF" stroke-width="3" fill="none" opacity="0.9"/>'
               '<path d="M 330 418 Q 400 404 470 406" stroke="#E8F4F4" stroke-width="2" fill="none" opacity="0.7"/>')
    for poly, sd, shade_op in ((L, 85, 0.45), (R, 86, 0.1)):
        line = rough(poly[:-1], sd, 6, 4)
        pp = line + [poly[-1]]
        out.append(f'<polygon points="{P(pp)}" fill="url(#{u}-cliff)"/>')
        cid = f"{u}-sl{sd}"
        xs = [x for x, _ in pp]
        box = (min(xs), 230, max(xs), 412)
        g = [patches(60, sd, box, ["#3E5A34", "#4E6A3A", "#2E4A2E", "#6A7A40"], w=(10, 26), h=(4, 10), op=(0.7, 0.95)),
             strokes_h(160, sd + 1, box, ["#D8B86A", "#C8A050", "#E8CC8A"], w=(4, 12), sw=(0.8, 1.8), op=(0.5, 0.9)),
             streaks(40, sd + 2, box, ["#3A2A26", "#B89A7A"], w=(1, 2.5), length=(10, 30), opacity=(0.2, 0.5), slant=0.3),
             f'<rect x="-10" y="230" width="620" height="190" fill="#1E1A2E" opacity="{shade_op}"/>']
        out.append(f'<clipPath id="{cid}"><polygon points="{P(pp)}"/></clipPath><g clip-path="url(#{cid})">' + "".join(g) + "</g>")
        if sd == 86:
            out.append(f'<polyline points="{P(line[:5])}" fill="none" stroke="#FFE2AA" stroke-width="2" opacity="0.7"/>')
    # fog drifting up the canyon
    out.append(mist(330, 360, 140, 22, "#F2EEF0", f"{u}-cf1", 0.55))
    out.append(mist(250, 330, 90, 14, "#F2EEF0", f"{u}-cf2", 0.4))
    # the bridge: a single open-spandrel concrete arch, tall piers at the springings, columns carrying the deck
    DY, DB = 228, 238
    out.append(f'<rect x="40" y="{DY}" width="540" height="{DB - DY}" fill="url(#{u}-conc)"/>')
    out.append(f'<rect x="40" y="{DB - 3}" width="540" height="3" fill="#8A8478"/>')
    out.append(f'<rect x="40" y="{DY - 5}" width="540" height="2.2" fill="#E8E0D0"/>')
    out.append('<g fill="#D8D0C2">' + "".join(f'<rect x="{x}" y="{DY - 5}" width="1.6" height="5"/>' for x in range(42, 580, 6)) + "</g>")
    ax0, ay0, ax1, ay1, cxr, cyr = 186, 336, 426, 328, 306, 246
    def arch_y(x, top=True):
        t = (x - ax0) / (ax1 - ax0)
        base = ay0 + (ay1 - ay0) * t
        h = (base - cyr) * (1 - (2 * t - 1) ** 2) ** 0.85
        return base - h - (0 if top else 10 + 8 * abs(2 * t - 1))
    xs = [ax0 + (ax1 - ax0) * i / 40 for i in range(41)]
    outer = [(x, arch_y(x)) for x in xs]
    inner = [(x, arch_y(x) + 10 + 8 * abs(2 * ((x - ax0) / (ax1 - ax0)) - 1)) for x in xs]
    # spandrel columns between arch and deck, and approach bents down to the slopes
    cols = []
    for x in range(198, 420, 14):
        y = arch_y(x)
        if y - DB > 6:
            cols.append((x, DB, y))
    for x, yb in ((70, 252), (98, 262), (126, 284), (152, 308), (456, 300), (486, 276), (514, 258), (542, 248)):
        cols.append((x, DB, yb))
    for x, y0, y1 in cols:
        out.append(f'<rect x="{x - 2.6:.1f}" y="{y0}" width="5.2" height="{y1 - y0:.1f}" fill="#D8D0C2"/><rect x="{x + 0.8:.1f}" y="{y0}" width="1.8" height="{y1 - y0:.1f}" fill="#FFF8EC"/>')
        out.append(f'<rect x="{x - 2.6:.1f}" y="{y0}" width="1.6" height="{y1 - y0:.1f}" fill="#9A9488"/>')
    out.append(f'<polygon points="{P(outer + inner[::-1])}" fill="url(#{u}-conc)"/>')
    out.append(f'<polyline points="{P(inner)}" fill="none" stroke="#8A8478" stroke-width="2"/>')
    out.append(f'<polyline points="{P(outer[20:])}" fill="none" stroke="#FFFBF2" stroke-width="1.6"/>')
    # massive piers where the arch springs from the canyon walls
    for x, yb in ((172, 340), (414, 332)):
        out.append(f'<rect x="{x}" y="{DB}" width="26" height="{yb - DB}" fill="#E2DACB"/><rect x="{x + 17}" y="{DB}" width="9" height="{yb - DB}" fill="#FFF8EC"/>'
                   f'<rect x="{x}" y="{DB}" width="6" height="{yb - DB}" fill="#A8A296"/>'
                   + "".join(f'<rect x="{x + 3}" y="{y}" width="20" height="1.2" fill="#B8B0A2"/>' for y in range(DB + 12, yb, 18)))
    out.append(f'<rect x="40" y="{DY}" width="540" height="2" fill="#FFFBF0"/>')
    # a car crossing and gulls riding the updraft
    out.append(f'<rect x="250" y="{DY - 8}" width="16" height="7" rx="2.5" fill="#2E5A8A"/><rect x="253" y="{DY - 11}" width="9" height="4" rx="1.5" fill="#B8D4E8"/>')
    out.append(birds_v([(210, 130, 12), (232, 140, 9), (470, 300, 10)], "#3A3A50"))
    # foreground right: rugged sea cliffs and sea stacks in white surf
    rc = rough([(400, 444), (420, 410), (470, 388), (520, 372), (570, 362), (610, 360)], 87, 8, 4)
    out.append(f'<polygon points="{P(rc + [(610, 444)])}" fill="#4A3A36"/>')
    out.append(f'<clipPath id="{u}-rc"><polygon points="{P(rc + [(610, 444)])}"/></clipPath><g clip-path="url(#{u}-rc)">'
               + streaks(70, 88, (400, 356, 610, 444), ["#8A6A52", "#2A2026", "#B8906A"], w=(2, 5), length=(10, 40), opacity=(0.3, 0.6), slant=0.4)
               + patches(20, 89, (430, 360, 610, 400), ["#4E6A3A", "#6A7A40"], w=(10, 22), h=(3, 6), op=(0.8, 1))
               + f'<rect x="400" y="350" width="210" height="100" fill="#FFD8A0" opacity="0.12"/></g>')
    out.append(f'<polyline points="{P(rc)}" fill="none" stroke="#FFD8A0" stroke-width="1.8" opacity="0.6"/>')
    out.append(grass(50, 96, (440, 366, 610, 400), ["#D8C080", "#A89A5A"], h=(6, 14)))
    # foreground left: our clifftop pullout with magenta ice plant, grasses and a wind-shaped cypress
    lc = rough([(-10, 376), (70, 384), (150, 404), (200, 444)], 91, 5, 3)
    out.append(f'<polygon points="{P(lc + [(-10, 444)])}" fill="#4A5A30"/>')
    out.append(f'<clipPath id="{u}-lc"><polygon points="{P(lc + [(-10, 444)])}"/></clipPath><g clip-path="url(#{u}-lc)">'
               + patches(60, 92, (-10, 380, 200, 444), ["#6A7A3A", "#8A9A4A", "#3E4E2A"], w=(8, 20), h=(3, 7), op=(0.8, 1))
               + dots(160, 93, (-10, 392, 190, 444), "#E0408A", r=(1.4, 3), opacity=(0.8, 1))
               + dots(60, 94, (-10, 392, 190, 444), "#F6A0C8", r=(1, 2), opacity=(0.8, 1)) + "</g>")
    out.append(grass(70, 95, (-10, 380, 180, 444), ["#D8C080", "#A89A5A", "#E8D8A0"], h=(8, 22)))
    out.append(cypress_tree(52, 392, 150, 7, light=1))
    return "\n".join(out)


BUILD = {
    "rocky-mountains": (rocky_mountains, "ROCKY MOUNTAINS", "COLORADO · USA", "#2C1E2C", "#E9B23C", "#FBEBD4", "#F2C46A"),
    "denali": (denali, "DENALI", "ALASKA · NATIONAL PARK", "#1E2A30", "#D8553A", "#FBEBD4", "#F2B05A"),
    "great-smoky-mountains": (great_smoky_mountains, "GREAT SMOKY MOUNTAINS", "TENNESSEE · NORTH CAROLINA", "#1E2448", "#F4B07A", "#FBEBD4", "#F6C9A0"),
    "blue-ridge": (blue_ridge, "BLUE RIDGE PARKWAY", "NORTH CAROLINA · VIRGINIA", "#1E2E4A", "#E8823A", "#FBEBD4", "#F6B46A"),
    "lake-tahoe": (lake_tahoe, "LAKE TAHOE", "CALIFORNIA · NEVADA", "#0E3456", "#3CC8C0", "#FBEBD4", "#7EE0D4"),
    "glacier": (glacier, "GLACIER", "MONTANA · NATIONAL PARK", "#1A2C34", "#D8684A", "#FBEBD4", "#F2BC8A"),
    "napa-valley": (napa_valley, "NAPA VALLEY", "CALIFORNIA · USA", "#3A1A2C", "#E8B04A", "#FBEBD4", "#F2C46A"),
    "big-sur": (big_sur, "BIG SUR", "CALIFORNIA · USA", "#1C2E40", "#F2A65A", "#FBEBD4", "#F6C890"),
    "grand-teton": (grand_teton, "GRAND TETON", "WYOMING · NATIONAL PARK", "#2A2440", "#F2A08E", "#FBEBD4", "#F6C2B0"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("places", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
