"""Painterly toolkit for the travel posters: gradients, natural ridgelines, conifers with irregular
branches, erosion streaks, mist and glows. Everything is plain SVG (no filters) so it prints and scrolls well."""
import math
import random


def P(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def lg(uid, stops, x1=0, y1=0, x2=0, y2=1, units="objectBoundingBox"):
    """Linear gradient. stops = [(offset 0..1, color, opacity?), ...]."""
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a[0]}"' if a else "") + "/>" for o, c, *a in stops)
    u = "" if units == "objectBoundingBox" else f' gradientUnits="{units}"'
    return f'<linearGradient id="{uid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>{s}</linearGradient>'


def rg(uid, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a[0]}"' if a else "") + "/>" for o, c, *a in stops)
    f = (f' fx="{fx}" fy="{fy}"' if fx is not None else "")
    return f'<radialGradient id="{uid}" cx="{cx}" cy="{cy}" r="{r}"{f}>{s}</radialGradient>'


def rough(pts, seed, amp=8, depth=4, decay=0.55):
    """Midpoint displacement between control points -> natural ridge / shoreline."""
    rnd = random.Random(seed)
    out = list(pts)
    a = amp
    for _ in range(depth):
        nxt = [out[0]]
        for (x1, y1), (x2, y2) in zip(out, out[1:]):
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            nxt += [(mx + rnd.uniform(-a, a) * 0.3, my + rnd.uniform(-a, a)), (x2, y2)]
        out = nxt
        a *= decay
    return out


def ridge_poly(pts, seed, base=444, amp=8, depth=4, fill="#000", extra=""):
    line = rough(pts, seed, amp, depth)
    poly = line + [(line[-1][0], base), (line[0][0], base)]
    return f'<polygon points="{P(poly)}" fill="{fill}"{extra}/>', line


def conifer(x, base, h, color, seed, lean=0.0, width=0.30, trunk=None, light=None):
    """Spruce / lodgepole silhouette with irregular branch tufts; optional lit edge on the left."""
    rnd = random.Random(seed)
    levels = max(7, int(h / 5))
    left, right = [], []
    maxw = h * width / 2
    for i in range(levels + 1):
        t = i / levels
        y = base - h * 0.08 - t * h * 0.92
        cx = x + lean * t * h * 0.08
        w = maxw * (1 - t) ** 0.85 * rnd.uniform(0.62, 1.05) + 1.2
        step = h * 0.92 / levels
        left += [(cx - w, y), (cx - w * rnd.uniform(0.5, 0.75), y - step * 0.55)]
        w2 = maxw * (1 - t) ** 0.85 * rnd.uniform(0.62, 1.05) + 1.2
        right += [(cx + w2, y - step * 0.2), (cx + w2 * rnd.uniform(0.5, 0.75), y - step * 0.7)]
    tip = (x + lean * h * 0.08, base - h)
    pts = [(x - 1.5, base)] + left + [tip] + right[::-1] + [(x + 1.5, base)]
    out = []
    if trunk:
        out.append(f'<rect x="{x - h * 0.018:.1f}" y="{base - h * 0.2:.1f}" width="{h * 0.036:.1f}" height="{h * 0.2:.1f}" fill="{trunk}"/>')
    out.append(f'<polygon points="{P(pts)}" fill="{color}"/>')
    if light:
        lit = [(x, base - h * 0.08)] + left + [tip]
        out.append(f'<polygon points="{P(lit)}" fill="{light}" opacity="0.55"/>')
    return "".join(out)


def tree_line(line, seed, colors, density=0.5, hmin=10, hmax=22, xmin=-10, xmax=610, sink=2):
    """Many small conifers standing on a ridgeline (list of points)."""
    rnd = random.Random(seed)
    out = []
    xs = sorted(rnd.uniform(xmin, xmax) for _ in range(int((xmax - xmin) * density / 6)))
    for x in xs:
        y = y_on(line, x)
        if y is None:
            continue
        out.append(conifer(x, y + sink, rnd.uniform(hmin, hmax), rnd.choice(colors), rnd.random()))
    return "".join(out)


def y_on(line, x):
    for (x1, y1), (x2, y2) in zip(line, line[1:]):
        if min(x1, x2) <= x <= max(x1, x2) and x1 != x2:
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return None


def streaks(n, seed, box, colors, w=(2, 7), length=(20, 90), opacity=(0.25, 0.6), slant=0.15):
    """Vertical erosion / rain-wash streaks inside box (use inside a clipPath)."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1)
        L = rnd.uniform(*length)
        ww = rnd.uniform(*w)
        dx = slant * L * rnd.uniform(-1, 1)
        out.append(f'<path d="M {x:.1f} {y:.1f} q {dx / 2 + ww:.1f} {L / 2:.1f} {dx:.1f} {L:.1f} l {-ww:.1f} 0 q {dx / 2 - ww * 0.4:.1f} {-L / 2:.1f} {-dx:.1f} {-L:.1f} Z" '
                   f'fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*opacity):.2f}"/>')
    return "".join(out)


def blobs(n, seed, box, colors, r=(4, 14), opacity=(0.3, 0.8), squash=0.6):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    return "".join(f'<ellipse cx="{rnd.uniform(x0, x1):.1f}" cy="{rnd.uniform(y0, y1):.1f}" rx="{(rr := rnd.uniform(*r)):.1f}" ry="{rr * squash:.1f}" '
                   f'fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*opacity):.2f}"/>' for _ in range(n))


def glow(cx, cy, r, color, uid, strength=0.9):
    return (f'<defs>{rg(uid, [(0, color, strength), (0.35, color, strength * 0.45), (1, color, 0)])}</defs>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{uid})"/>')


def mist(cx, cy, rx, ry, color, uid, strength=0.85):
    return (f'<defs>{rg(uid, [(0, color, strength), (0.55, color, strength * 0.5), (1, color, 0)])}</defs>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{uid})"/>')


def grass(n, seed, box, colors, h=(6, 16), sw=1.6):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        hh = rnd.uniform(*h) * (0.6 + 0.6 * (y - y0) / max(1, y1 - y0))
        out.append(f'<path d="M {x:.1f} {y:.1f} q {rnd.uniform(-3, 3):.1f} {-hh / 2:.1f} {rnd.uniform(-5, 5):.1f} {-hh:.1f}" stroke="{rnd.choice(colors)}"/>')
    return f'<g fill="none" stroke-width="{sw}" stroke-linecap="round">' + "".join(out) + "</g>"


def dots(n, seed, box, color, r=(0.6, 1.6), opacity=(0.3, 0.9)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    return "".join(f'<circle cx="{rnd.uniform(x0, x1):.1f}" cy="{rnd.uniform(y0, y1):.1f}" r="{rnd.uniform(*r):.2f}" fill="{color}" opacity="{rnd.uniform(*opacity):.2f}"/>' for _ in range(n))
