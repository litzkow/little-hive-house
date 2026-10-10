"""Building blocks for the travel posters (600 x 444 canvas; the top 40 px are trimmed by the poster layout,
so keep anything important below y = 50)."""
import math
import random


def P(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def sky(bands):
    """bands: [(y_top, color), ...] from the top down; each band runs to the bottom."""
    return "".join(f'<rect x="0" y="{y}" width="600" height="{444 - y}" fill="{c}"/>' for y, c in bands)


def sky_curved(bands):
    """Gently curved horizontal bands, like a screen-printed sky."""
    out = []
    for i, (y, c) in enumerate(bands):
        if i == 0:
            out.append(f'<rect width="600" height="444" fill="{c}"/>')
        else:
            out.append(f'<path d="M 0 {y + 6} Q 300 {y - 10} 600 {y + 6} L 600 444 L 0 444 Z" fill="{c}"/>')
    return "".join(out)


def sun(cx, cy, r, color, halo=None, halo2=None):
    out = []
    if halo2:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 1.32:.1f}" fill="{halo2}"/>')
    if halo:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 1.15:.1f}" fill="{halo}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>')
    return "".join(out)


def cloud(cx, cy, w, color):
    h = w * 0.32
    return (f'<g fill="{color}"><rect x="{cx - w / 2:.1f}" y="{cy - h * 0.35:.1f}" width="{w:.1f}" height="{h * 0.7:.1f}" rx="{h * 0.35:.1f}"/>'
            f'<circle cx="{cx - w * 0.16:.1f}" cy="{cy - h * 0.35:.1f}" r="{h * 0.55:.1f}"/><circle cx="{cx + w * 0.12:.1f}" cy="{cy - h * 0.45:.1f}" r="{h * 0.7:.1f}"/></g>')


def streak(x, y, w, color, h=10):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{color}"/>'


def birds(spec, color, sw=2.4):
    return "".join(f'<path d="M {x} {y} q {s * 0.5} {-s * 0.5} {s} 0 q {s * 0.5} {-s * 0.5} {s} 0" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>'
                   for x, y, s in spec)


def ridge(peaks, base, color):
    """A straight-edged mountain ridge through the given peak/valley points."""
    pts = [(peaks[0][0], base)] + peaks + [(peaks[-1][0], base)]
    return f'<polygon points="{P(pts)}" fill="{color}"/>'


def snowcap(peak, left, right, color, drop=26, teeth=3):
    """Snow on a peak: peak (x, y); left/right are points on the slopes where the snow ends."""
    (px, py), (lx, ly), (rx, ry) = peak, left, right
    pts = [(lx, ly)]
    for i in range(1, teeth * 2):
        t = i / (teeth * 2)
        x = lx + (rx - lx) * t
        y = ly + (ry - ly) * t + (drop if i % 2 else drop * 0.35)
        pts.append((x, y))
    pts += [(rx, ry), (px, py)]
    return f'<polygon points="{P(pts)}" fill="{color}"/>'


def hills(y, amp, color, waves=3, phase=0, bottom=444):
    d = f"M 0 {y + amp * math.sin(phase):.1f}"
    n = 24
    for i in range(1, n + 1):
        x = 600 * i / n
        yy = y + amp * math.sin(phase + waves * 2 * math.pi * i / n)
        d += f" L {x:.1f} {yy:.1f}"
    return f'<path d="{d} L 600 {bottom} L 0 {bottom} Z" fill="{color}"/>'


def water(y, color, ripple=None, spec=(), bottom=444):
    out = [f'<rect x="0" y="{y}" width="600" height="{bottom - y}" fill="{color}"/>']
    if ripple:
        out.append(f'<g stroke="{ripple}" stroke-width="3" stroke-linecap="round">' +
                   "".join(f'<line x1="{x}" y1="{yy}" x2="{x + w}" y2="{yy}"/>' for x, yy, w in spec) + "</g>")
    return "".join(out)


def pine(x, base, h, color, shade=None, trunk="#5A3A2E"):
    w = h * 0.42
    out = [f'<rect x="{x - h * 0.03:.1f}" y="{base - h * 0.14:.1f}" width="{h * 0.06:.1f}" height="{h * 0.14:.1f}" fill="{trunk}"/>']
    for k, (t, s) in enumerate(((0.12, 1.0), (0.38, 0.8), (0.62, 0.58))):
        top = base - h * (t + 0.4 * s + 0.18)
        bot = base - h * t
        out.append(f'<polygon points="{P([(x, top), (x + w * s / 2, bot), (x - w * s / 2, bot)])}" fill="{color}"/>')
        if shade:
            out.append(f'<polygon points="{P([(x, top), (x + w * s / 2, bot), (x + w * s * 0.08, bot)])}" fill="{shade}"/>')
    return "".join(out)


def round_tree(x, base, r, color, shade=None, trunk="#5A3A2E"):
    out = [f'<rect x="{x - r * 0.1:.1f}" y="{base - r * 0.9:.1f}" width="{r * 0.2:.1f}" height="{r * 0.9:.1f}" fill="{trunk}"/>',
           f'<circle cx="{x}" cy="{base - r * 1.5:.1f}" r="{r}" fill="{color}"/>']
    if shade:
        out.append(f'<path d="M {x + r * 0.15:.1f} {base - r * 2.48:.1f} A {r} {r} 0 0 1 {x + r * 0.15:.1f} {base - r * 0.52:.1f} Q {x + r * 0.7:.1f} {base - r * 1.5:.1f} {x + r * 0.15:.1f} {base - r * 2.48:.1f} Z" fill="{shade}"/>')
    return "".join(out)


def cypress(x, base, h, color):
    return f'<ellipse cx="{x}" cy="{base - h / 2:.1f}" rx="{h * 0.13:.1f}" ry="{h / 2:.1f}" fill="{color}"/>'


def palm(x, base, h, trunk, frond, lean=1.0, fronds=7):
    tx, ty = x + 26 * lean * h / 200, base - h
    out = [f'<path d="M {x - 5} {base} Q {x + 6 * lean:.1f} {base - h * 0.5:.1f} {tx - 3:.1f} {ty:.1f} L {tx + 4:.1f} {ty + 2:.1f} Q {x + 14 * lean:.1f} {base - h * 0.5:.1f} {x + 6} {base} Z" fill="{trunk}"/>']
    k = h / 200
    for i in range(fronds):
        ang = math.radians(-170 + i * (160 / (fronds - 1)))
        L = (70 + 18 * math.sin(i * 1.7)) * k
        ex, ey = tx + L * math.cos(ang), ty + L * math.sin(ang) + 30 * k
        mx, my = tx + 0.55 * L * math.cos(ang), ty + 0.55 * L * math.sin(ang) - 14 * k
        nx, ny = tx + 0.5 * L * math.cos(ang), ty + 0.5 * L * math.sin(ang) + 6 * k
        out.append(f'<path d="M {tx:.1f} {ty:.1f} Q {mx:.1f} {my:.1f} {ex:.1f} {ey:.1f} Q {nx:.1f} {ny:.1f} {tx:.1f} {ty:.1f} Z" fill="{frond}"/>')
    out.append(f'<circle cx="{tx:.1f}" cy="{ty + 4:.1f}" r="{5 * k + 2:.1f}" fill="{trunk}"/>')
    return "".join(out)


def windows(x, y, w, h, cols, rows, color, ww=None, wh=None, arch=False):
    ww = ww or w / (cols * 2)
    wh = wh or h / (rows * 2)
    gx = (w - cols * ww) / (cols + 1)
    gy = (h - rows * wh) / (rows + 1)
    out = []
    for i in range(cols):
        for j in range(rows):
            xx, yy = x + gx + i * (ww + gx), y + gy + j * (wh + gy)
            if arch:
                out.append(f'<path d="M {xx:.1f} {yy + wh:.1f} L {xx:.1f} {yy + ww / 2:.1f} A {ww / 2:.1f} {ww / 2:.1f} 0 0 1 {xx + ww:.1f} {yy + ww / 2:.1f} L {xx + ww:.1f} {yy + wh:.1f} Z" fill="{color}"/>')
            else:
                out.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="{ww:.1f}" height="{wh:.1f}" fill="{color}"/>')
    return "".join(out)


def sailboat(x, y, s, hull, sail, sail2=None):
    k = s / 60
    return (f'<path d="M {x - 30 * k:.1f} {y} L {x + 30 * k:.1f} {y} L {x + 22 * k:.1f} {y + 10 * k:.1f} L {x - 22 * k:.1f} {y + 10 * k:.1f} Z" fill="{hull}"/>'
            f'<path d="M {x + 2 * k:.1f} {y - 2 * k:.1f} L {x + 2 * k:.1f} {y - 50 * k:.1f} L {x + 26 * k:.1f} {y - 4 * k:.1f} Z" fill="{sail}"/>'
            f'<path d="M {x - 2 * k:.1f} {y - 2 * k:.1f} L {x - 2 * k:.1f} {y - 40 * k:.1f} L {x - 20 * k:.1f} {y - 4 * k:.1f} Z" fill="{sail2 or sail}"/>')


def lighthouse(x, base, h, body, stripe, lamp="#FFD25E", cap="#2B2B2B", stripes=4, spiral=False):
    w0, w1 = h * 0.2, h * 0.13
    top = base - h
    cid = f"lh{int(x)}{int(base)}"
    out = [f'<clipPath id="{cid}"><polygon points="{P([(x - w0 / 2, base), (x - w1 / 2, top), (x + w1 / 2, top), (x + w0 / 2, base)])}"/></clipPath>',
           f'<polygon points="{P([(x - w0 / 2, base), (x - w1 / 2, top), (x + w1 / 2, top), (x + w0 / 2, base)])}" fill="{body}"/>']
    band = h / (stripes * 2)
    if spiral:
        g = "".join(f'<polygon points="{P([(x - 40, top + i * band * 2), (x + 40, top + i * band * 2 - band * 1.6), (x + 40, top + i * band * 2 - band * 0.6), (x - 40, top + i * band * 2 + band)])}" fill="{stripe}"/>'
                    for i in range(stripes + 2))
    else:
        g = "".join(f'<rect x="{x - 40}" y="{top + band * (2 * i + 1):.1f}" width="80" height="{band:.1f}" fill="{stripe}"/>' for i in range(stripes))
    out.append(f'<g clip-path="url(#{cid})">{g}<rect x="{x}" y="{top}" width="40" height="{h}" fill="#000000" opacity="0.1"/></g>')
    out.append(f'<rect x="{x - w1 / 2 - 6:.1f}" y="{top - 4:.1f}" width="{w1 + 12:.1f}" height="6" fill="{cap}"/>')
    out.append(f'<rect x="{x - w1 / 2 + 2:.1f}" y="{top - 24:.1f}" width="{w1 - 4:.1f}" height="20" fill="{lamp}"/>')
    out.append(f'<g stroke="{cap}" stroke-width="2">' + "".join(f'<line x1="{x - w1 / 2 + 2 + i * (w1 - 4) / 3:.1f}" y1="{top - 24:.1f}" x2="{x - w1 / 2 + 2 + i * (w1 - 4) / 3:.1f}" y2="{top - 4:.1f}"/>' for i in range(4)) + "</g>")
    out.append(f'<path d="M {x - w1 / 2 - 2:.1f} {top - 24:.1f} Q {x:.1f} {top - 44:.1f} {x + w1 / 2 + 2:.1f} {top - 24:.1f} Z" fill="{cap}"/>')
    out.append(f'<rect x="{x - 1.5:.1f}" y="{top - 52:.1f}" width="3" height="10" fill="{cap}"/>')
    return "".join(out)


def rays(cx, cy, r1, r2, color, n=12, sw=6, start=0, opacity=1):
    return (f'<g stroke="{color}" stroke-width="{sw}" stroke-linecap="round" opacity="{opacity}">' +
            "".join(f'<line x1="{cx + r1 * math.cos(math.radians(start + i * 360 / n)):.1f}" y1="{cy + r1 * math.sin(math.radians(start + i * 360 / n)):.1f}" '
                    f'x2="{cx + r2 * math.cos(math.radians(start + i * 360 / n)):.1f}" y2="{cy + r2 * math.sin(math.radians(start + i * 360 / n)):.1f}"/>' for i in range(n)) + "</g>")


def stars(seed, n, color, box=(0, 0, 600, 260), r=(0.8, 2.2), opacity=0.8):
    rnd = random.Random(seed)
    return f'<g fill="{color}" opacity="{opacity}">' + "".join(
        f'<circle cx="{rnd.uniform(box[0], box[2]):.1f}" cy="{rnd.uniform(box[1], box[3]):.1f}" r="{rnd.uniform(*r):.1f}"/>' for _ in range(n)) + "</g>"


def grass_tufts(spec, color):
    return "".join(f'<path d="M {x} {y} l -6 -16 M {x} {y} l 1 -20 M {x} {y} l 7 -15" stroke="{color}" stroke-width="2.4" stroke-linecap="round" fill="none"/>' for x, y in spec)
