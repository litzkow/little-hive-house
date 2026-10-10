"""Hand-painted look for SVG: organic (never perfect) shapes, layered washes with darker pooled edges,
visible brush strokes clipped inside shapes, variable-width ink lines, paper grain, and brush-textured
lettering. Plain SVG (clipPaths, patterns, opacity) so it prints exactly as it renders."""
import math
import random

from icons import MAPLE, P


def _f(v):
    return f"{v:.1f}"


def smooth_closed(pts):
    """Catmull-Rom through points -> closed cubic Bezier path."""
    n = len(pts)
    d = [f"M {_f(pts[0][0])} {_f(pts[0][1])}"]
    for i in range(n):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C {_f(c1[0])} {_f(c1[1])} {_f(c2[0])} {_f(c2[1])} {_f(p2[0])} {_f(p2[1])}")
    return " ".join(d) + " Z"


def smooth_open(pts):
    n = len(pts)
    d = [f"M {_f(pts[0][0])} {_f(pts[0][1])}"]
    for i in range(n - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C {_f(c1[0])} {_f(c1[1])} {_f(c2[0])} {_f(c2[1])} {_f(p2[0])} {_f(p2[1])}")
    return " ".join(d)


def jitter(pts, seed, amt=2.0):
    rnd = random.Random(seed)
    return [(x + rnd.uniform(-amt, amt), y + rnd.uniform(-amt, amt)) for x, y in pts]


def blob_pts(cx, cy, rx, ry, seed, wobble=0.06, n=18, rot=0):
    rnd = random.Random(seed)
    out = []
    ph = rnd.uniform(0, 6.28)
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + wobble * (math.sin(3 * a + ph) * 0.6 + rnd.uniform(-1, 1) * 0.5)
        x, y = rx * k * math.cos(a), ry * k * math.sin(a)
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def blob(cx, cy, rx, ry, seed, wobble=0.06, n=18, rot=0):
    return smooth_closed(blob_pts(cx, cy, rx, ry, seed, wobble, n, rot))


def wash(d, color, seed, layers=3, spread=1.6, opacity=0.5, edge=None, edge_w=1.6):
    """Watercolour/gouache wash: a few slightly shifted copies of a shape, plus a darker pooled edge."""
    rnd = random.Random(seed)
    out = [f'<path d="{d}" fill="{color}"/>']
    for _ in range(layers - 1):
        dx, dy = rnd.uniform(-spread, spread), rnd.uniform(-spread, spread)
        out.append(f'<path d="{d}" fill="{color}" opacity="{opacity * rnd.uniform(0.5, 0.9):.2f}" transform="translate({dx:.1f} {dy:.1f})"/>')
    if edge:
        out.append(f'<path d="{d}" fill="none" stroke="{edge}" stroke-width="{edge_w}" stroke-opacity="0.45" stroke-linejoin="round"/>')
    return "".join(out)


def strokes(uid, clip_d, box, colors, seed, n=80, angle=-80, length=(14, 40), width=(2, 6), opacity=(0.18, 0.5),
            curve=0.25, clip_extra=""):
    """Visible brush strokes clipped inside a shape. angle in degrees (0 = right, -90 = up)."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = [f'<clipPath id="{uid}"><path d="{clip_d}"{clip_extra}/></clipPath><g clip-path="url(#{uid})">']
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        L = rnd.uniform(*length)
        w = rnd.uniform(*width)
        a = math.radians(angle + rnd.uniform(-12, 12))
        dx, dy = L * math.cos(a), L * math.sin(a)
        nx, ny = -math.sin(a), math.cos(a)
        bend = L * curve * rnd.uniform(-1, 1)
        mx, my = x + dx / 2 + nx * bend, y + dy / 2 + ny * bend
        # tapered stroke: two curves meeting at the ends
        out.append(f'<path d="M {_f(x)} {_f(y)} Q {_f(mx + nx * w)} {_f(my + ny * w)} {_f(x + dx)} {_f(y + dy)} '
                   f'Q {_f(mx - nx * w)} {_f(my - ny * w)} {_f(x)} {_f(y)} Z" fill="{rnd.choice(colors)}" '
                   f'opacity="{rnd.uniform(*opacity):.2f}"/>')
    out.append("</g>")
    return "".join(out)


def ink(d, color="#3A2418", w=2.4, seed=1, passes=2, opacity=0.85):
    """Variable-weight hand-inked line: a couple of passes with different widths and tiny offsets."""
    rnd = random.Random(seed)
    out = []
    for i in range(passes):
        dx, dy = rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6)
        ww = w * (1 if i == 0 else rnd.uniform(0.45, 0.7))
        out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{ww:.2f}" stroke-linecap="round" '
                   f'stroke-linejoin="round" opacity="{opacity if i == 0 else opacity * 0.6:.2f}" transform="translate({dx:.2f} {dy:.2f})"/>')
    return "".join(out)


def paper(uid, base="#F4ECDD", fleck="#8A6A4A", seed=5, density=1.0):
    """Paper ground: base colour, soft mottling, and a tiled pattern of specks and fibres."""
    rnd = random.Random(seed)
    specks = "".join(f'<circle cx="{rnd.uniform(0, 120):.1f}" cy="{rnd.uniform(0, 120):.1f}" r="{rnd.uniform(0.3, 0.9):.2f}" fill="{fleck}" opacity="{rnd.uniform(0.08, 0.25):.2f}"/>' for _ in range(int(40 * density)))
    fibres = "".join(f'<path d="M {(x := rnd.uniform(0, 120)):.1f} {(y := rnd.uniform(0, 120)):.1f} q {rnd.uniform(-4, 4):.1f} {rnd.uniform(-2, 2):.1f} {rnd.uniform(-9, 9):.1f} {rnd.uniform(-3, 3):.1f}" stroke="{fleck}" stroke-width="0.5" fill="none" opacity="0.12"/>' for _ in range(int(10 * density)))
    mottle = "".join(f'<ellipse cx="{rnd.uniform(0, 600):.0f}" cy="{rnd.uniform(0, 600):.0f}" rx="{rnd.uniform(60, 180):.0f}" ry="{rnd.uniform(40, 140):.0f}" fill="{rnd.choice(["#FFFFFF", fleck])}" opacity="{rnd.uniform(0.012, 0.03):.3f}"/>' for _ in range(14))
    return (f'<defs><pattern id="{uid}" width="120" height="120" patternUnits="userSpaceOnUse">{specks}{fibres}</pattern></defs>'
            f'<rect width="600" height="600" fill="{base}"/>{mottle}<rect width="600" height="600" fill="url(#{uid})"/>')


def grain(uid, color="#3A2418", seed=9, opacity=1.0):
    """Speck pattern to lay over painted areas (adds tooth to flat colour)."""
    rnd = random.Random(seed)
    specks = "".join(f'<circle cx="{rnd.uniform(0, 90):.1f}" cy="{rnd.uniform(0, 90):.1f}" r="{rnd.uniform(0.3, 0.8):.2f}" fill="{rnd.choice([color, "#FFFFFF"])}" opacity="{rnd.uniform(0.06, 0.18):.2f}"/>' for _ in range(60))
    return (f'<defs><pattern id="{uid}" width="90" height="90" patternUnits="userSpaceOnUse">{specks}</pattern></defs>'
            f'<rect width="600" height="600" fill="url(#{uid})" opacity="{opacity}"/>')


def brush_text(uid, x, y, s, font, size, color, colors, seed, ls=0, anchor="middle", angle=-8, n=None, shadow=None):
    """Lettering filled with visible brush strokes (text used as a clipPath), with an optional offset shadow."""
    t = f'<text x="{x}" y="{y}" text-anchor="{anchor}" {font} font-size="{size}" letter-spacing="{ls}">{s}</text>'
    out = []
    if shadow:
        out.append(f'<text x="{x + size * 0.03:.1f}" y="{y + size * 0.035:.1f}" text-anchor="{anchor}" {font} font-size="{size}" letter-spacing="{ls}" fill="{shadow}">{s}</text>')
    out.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" {font} font-size="{size}" letter-spacing="{ls}" fill="{color}">{s}</text>')
    rnd = random.Random(seed)
    w = size * len(s) * 0.7
    x0 = x - w / 2 if anchor == "middle" else x
    n = n or int(len(s) * 26)
    st = []
    for _ in range(n):
        px, py = rnd.uniform(x0 - 10, x0 + w + 10), rnd.uniform(y - size, y + size * 0.2)
        L = rnd.uniform(size * 0.25, size * 0.7)
        ww = rnd.uniform(size * 0.03, size * 0.08)
        a = math.radians(angle + rnd.uniform(-10, 10))
        dx, dy = L * math.cos(a), L * math.sin(a)
        nx, ny = -math.sin(a), math.cos(a)
        mx, my = px + dx / 2, py + dy / 2
        st.append(f'<path d="M {_f(px)} {_f(py)} Q {_f(mx + nx * ww)} {_f(my + ny * ww)} {_f(px + dx)} {_f(py + dy)} Q {_f(mx - nx * ww)} {_f(my - ny * ww)} {_f(px)} {_f(py)} Z" fill="{rnd.choice(colors)}" opacity="{rnd.uniform(0.2, 0.55):.2f}"/>')
    out.append(f'<clipPath id="{uid}">{t}</clipPath><g clip-path="url(#{uid})">{"".join(st)}</g>')
    return "".join(out)


# ---------------------------------------------------------------- painted pieces (shared by magnets and site decor)
def maple_leaf(cx, cy, s, fill, dark, rot=0, seed=1, vein="#FFE9C4"):
    pts = MAPLE + [(-x, y) for x, y in reversed(MAPLE[1:])]
    pts = [(cx + x * s, cy + y * s) for x, y in pts]
    rnd = random.Random(seed)
    pts = [(x + rnd.uniform(-0.6, 0.6), y + rnd.uniform(-0.6, 0.6)) for x, y in pts]
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    half = [(cx, cy - s)] + [(cx + x * s, cy + y * s) for x, y in MAPLE[1:]] + [(cx, cy + 0.46 * s)]
    base = (cx, cy + 0.38 * s)
    veins = "".join(f'<path d="M {base[0]:.1f} {base[1]:.1f} Q {cx + tx * s * 0.45 + 1:.1f} {cy + ty * s * 0.5:.1f} {cx + tx * s:.1f} {cy + ty * s:.1f}"/>'
                    for tx, ty in ((0, -0.86), (0.8, -0.28), (-0.8, -0.28), (0.48, 0.18), (-0.48, 0.18)))
    return (f'<g transform="rotate({rot} {cx} {cy})">'
            f'<path d="{d}" fill="{fill}"/>'
            f'<polygon points="{P(half)}" fill="{dark}" opacity="0.55"/>'
            f'<g fill="none" stroke="{vein}" stroke-width="{max(0.8, s * 0.035):.1f}" stroke-linecap="round" opacity="0.7">{veins}</g>'
            f'<path d="{d}" fill="none" stroke="{dark}" stroke-width="{max(0.8, s * 0.04):.1f}" stroke-linejoin="round" opacity="0.6"/>'
            f'<path d="M {cx:.1f} {cy + 0.4 * s:.1f} q {s * 0.05:.1f} {s * 0.3:.1f} {-s * 0.06:.1f} {s * 0.6:.1f}" stroke="{dark}" stroke-width="{max(1.2, s * 0.07):.1f}" fill="none" stroke-linecap="round"/>'
            "</g>")


def oak(cx, cy, s, fill, dark, rot=0):
    pts = []
    for i in range(0, 360, 8):
        a = math.radians(i)
        wob = 1 + 0.2 * math.sin(a * 6) if 18 < i < 342 else 1
        pts.append((cx + 0.42 * s * math.sin(a) * wob, cy - s * math.cos(a) * 0.9))
    d = smooth_closed(pts)
    return (f'<g transform="rotate({rot} {cx} {cy})"><path d="{d}" fill="{fill}"/>'
            f'<path d="M {cx} {cy - 0.85 * s} L {cx} {cy + 0.9 * s}" stroke="{dark}" stroke-width="{max(0.8, s * 0.05):.1f}" opacity="0.7"/>'
            f'<path d="{d}" fill="none" stroke="{dark}" stroke-width="{max(0.8, s * 0.04):.1f}" opacity="0.5"/>'
            f'<path d="M {cx} {cy + 0.9 * s} l 0 {s * 0.3:.1f}" stroke="{dark}" stroke-width="{max(1.2, s * 0.08):.1f}" stroke-linecap="round"/></g>')


def acorn(cx, cy, s, rot=0):
    return (f'<g transform="rotate({rot} {cx} {cy})">'
            f'<path d="{blob(cx, cy + 0.3 * s, 0.42 * s, 0.55 * s, 3, 0.04)}" fill="#B9773A"/>'
            f'<path d="{blob(cx + 0.1 * s, cy + 0.36 * s, 0.26 * s, 0.42 * s, 4, 0.04)}" fill="#8E5426" opacity="0.6"/>'
            f'<ellipse cx="{cx - 0.15 * s:.1f}" cy="{cy + 0.22 * s:.1f}" rx="{0.08 * s:.1f}" ry="{0.2 * s:.1f}" fill="#FFE2B8" opacity="0.5"/>'
            f'<path d="M {cx - 0.52 * s:.1f} {cy + 0.02 * s:.1f} Q {cx:.1f} {cy - 0.6 * s:.1f} {cx + 0.52 * s:.1f} {cy + 0.02 * s:.1f} Q {cx:.1f} {cy + 0.16 * s:.1f} {cx - 0.52 * s:.1f} {cy + 0.02 * s:.1f} Z" fill="#6E4A2A"/>'
            f'<path d="M {cx - 0.3 * s:.1f} {cy - 0.12 * s:.1f} l {0.6 * s:.1f} 0 M {cx - 0.4 * s:.1f} {cy - 0.02 * s:.1f} l {0.8 * s:.1f} 0" stroke="#4A3018" stroke-width="{max(0.6, s * 0.04):.1f}" opacity="0.6"/>'
            f'<path d="M {cx:.1f} {cy - 0.28 * s:.1f} q {0.04 * s:.1f} {-0.18 * s:.1f} {0.14 * s:.1f} {-0.24 * s:.1f}" stroke="#4A3018" stroke-width="{max(1, s * 0.09):.1f}" fill="none" stroke-linecap="round"/>'
            "</g>")


def painted_pumpkin(uid, cx, cy, w, h, seed, body="#E8792E", dark="#B9531E", light="#F8A85A", stem="#6B5A2E", leaf="#6E8A3E"):
    """Gouache pumpkin: lobes as organic washes, curved rib strokes, dry-brush highlights, inked edges."""
    out = []
    lobes = [(-0.32, 0.25, 0.45, dark), (0.32, 0.25, 0.45, dark), (-0.16, 0.27, 0.5, body), (0.16, 0.27, 0.5, body), (0, 0.24, 0.52, body)]
    outline = blob(cx, cy, 0.56 * w, 0.5 * h, seed, 0.03, 22)
    out.append(f'<ellipse cx="{cx}" cy="{cy + 0.5 * h:.1f}" rx="{0.55 * w:.1f}" ry="{0.07 * h:.1f}" fill="#3A2418" opacity="0.18"/>')
    for k, (dx, rx, ry, col) in enumerate(lobes):
        out.append(wash(blob(cx + dx * w, cy, rx * w, ry * h, seed + k, 0.035, 16), col, seed + k, layers=2, spread=0.8, opacity=0.5))
    out.append(strokes(f"{uid}-st", outline, (cx - 0.6 * w, cy - 0.55 * h, cx + 0.6 * w, cy + 0.55 * h),
                       [light, dark, "#FFD08A", "#A8461A"], seed, n=int(w * 0.9), angle=-90, length=(0.12 * h, 0.4 * h),
                       width=(0.012 * w, 0.03 * w), opacity=(0.18, 0.45), curve=0.15))
    for dx in (-0.27, -0.1, 0.1, 0.27):
        out.append(ink(f"M {cx + dx * w:.1f} {cy - 0.44 * h:.1f} Q {cx + dx * 1.45 * w:.1f} {cy:.1f} {cx + dx * w:.1f} {cy + 0.47 * h:.1f}", dark, max(1.2, 0.02 * w), seed + 7, 1, 0.65))
    out.append(f'<path d="M {cx - 0.2 * w:.1f} {cy - 0.3 * h:.1f} Q {cx - 0.29 * w:.1f} {cy - 0.02 * h:.1f} {cx - 0.21 * w:.1f} {cy + 0.24 * h:.1f}" stroke="#FFE2B8" stroke-width="{max(1.5, 0.035 * w):.1f}" fill="none" stroke-linecap="round" opacity="0.7"/>')
    out.append(ink(outline, "#7A3412", max(1.2, 0.022 * w), seed + 3, 2, 0.55))
    # stem, curling vine and a leaf
    out.append(f'<path d="M {cx - 0.05 * w:.1f} {cy - 0.42 * h:.1f} q {-0.02 * w:.1f} {-0.2 * h:.1f} {0.09 * w:.1f} {-0.3 * h:.1f} l {0.05 * w:.1f} {0.05 * h:.1f} q {-0.07 * w:.1f} {0.09 * h:.1f} {-0.03 * w:.1f} {0.27 * h:.1f} Z" fill="{stem}"/>')
    out.append(ink(f"M {cx + 0.02 * w:.1f} {cy - 0.47 * h:.1f} q {0.2 * w:.1f} {-0.1 * h:.1f} {0.18 * w:.1f} {-0.22 * h:.1f} q {-0.02 * w:.1f} {-0.08 * h:.1f} {-0.08 * w:.1f} {-0.04 * h:.1f}", leaf, max(1, 0.014 * w), seed + 9, 1, 0.9))
    lf = blob(cx + 0.24 * w, cy - 0.5 * h, 0.13 * w, 0.07 * w, seed + 11, 0.12, 12, rot=-20)
    out.append(f'<path d="{lf}" fill="{leaf}"/><path d="M {cx + 0.13 * w:.1f} {cy - 0.47 * h:.1f} L {cx + 0.36 * w:.1f} {cy - 0.55 * h:.1f}" stroke="#4A6228" stroke-width="{max(0.8, 0.01 * w):.1f}"/>')
    return "".join(out)


def hay_bale(uid, x, y, w, h, seed):
    d = smooth_closed([(x, y + 4), (x + w * 0.5, y - 2), (x + w, y + 4), (x + w + 3, y + h * 0.5), (x + w, y + h), (x + w * 0.5, y + h + 2), (x, y + h), (x - 3, y + h * 0.5)])
    out = [f'<ellipse cx="{x + w / 2:.1f}" cy="{y + h + 2:.1f}" rx="{w * 0.56:.1f}" ry="6" fill="#3A2418" opacity="0.18"/>',
           wash(d, "#E2B65A", seed, 2, 1, 0.5),
           f'<path d="M {x} {y + 6} L {x + w} {y + 6} L {x + w} {y + h * 0.35} L {x} {y + h * 0.35} Z" fill="#F2D07A" opacity="0.55"/>',
           strokes(f"{uid}-s", d, (x - 10, y - 10, x + w + 10, y + h + 10), ["#C9933A", "#F6DA8A", "#A8742A", "#FFF0B8"], seed,
                   n=int(w * 1.6), angle=-5, length=(10, 26), width=(0.6, 1.6), opacity=(0.4, 0.85), curve=0.2)]
    for t in (0.3, 0.7):
        out.append(f'<path d="M {x + w * t:.1f} {y} q 2 {h / 2:.1f} 0 {h:.1f}" stroke="#7A4E22" stroke-width="2.4" fill="none"/>')
    rnd = random.Random(seed)
    tufts = "".join(f'<path d="M {x + rnd.uniform(0, w):.1f} {y + rnd.choice([1, h - 1]):.1f} l {rnd.uniform(-8, 8):.1f} {rnd.uniform(-7, 7):.1f}"/>' for _ in range(30))
    out.append(f'<g stroke="#D9A847" stroke-width="1.2" stroke-linecap="round">{tufts}</g>')
    out.append(ink(d, "#8A5A22", 1.6, seed, 1, 0.5))
    return "".join(out)


def corn_stalk(x, base, h, seed, lean=0):
    rnd = random.Random(seed)
    top = (x + lean * h, base - h)
    out = [ink(smooth_open([(x, base), (x + lean * h * 0.4, base - h * 0.5), top]), "#B08A4A", 4, seed, 1, 1)]
    for i in range(7):
        t = 0.2 + i * 0.11
        px, py = x + lean * h * t, base - h * t
        side = 1 if i % 2 else -1
        L = h * rnd.uniform(0.22, 0.34)
        tip = (px + side * L, py + L * rnd.uniform(0.1, 0.5))
        mid = (px + side * L * 0.5, py - L * 0.25)
        d = f"M {px:.1f} {py:.1f} Q {mid[0]:.1f} {mid[1] - 4:.1f} {tip[0]:.1f} {tip[1]:.1f} Q {mid[0]:.1f} {mid[1] + 5:.1f} {px:.1f} {py + 6:.1f} Z"
        out.append(f'<path d="{d}" fill="{rnd.choice(["#D9B46A", "#C9A25A", "#E6C47E"])}"/>')
        out.append(f'<path d="M {px:.1f} {py + 2:.1f} Q {mid[0]:.1f} {mid[1]:.1f} {tip[0]:.1f} {tip[1]:.1f}" stroke="#9A7A3A" stroke-width="0.9" fill="none" opacity="0.8"/>')
    out.append(f'<path d="M {top[0]:.1f} {top[1]:.1f} l -6 -14 M {top[0]:.1f} {top[1]:.1f} l 2 -16 M {top[0]:.1f} {top[1]:.1f} l 8 -12" stroke="#C9A25A" stroke-width="2" stroke-linecap="round"/>')
    return "".join(out)
