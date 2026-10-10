"""Painted and engraved pieces for the photo-magnet frames (tools/frames.py): gouache leaves, holly, pine,
peonies, roses, eucalyptus, monstera, palms, balloons, clouds, laurel, gold work, lace and more.

Everything is plain SVG on the 600-unit magnet canvas. Each piece takes a `U` id factory so clipPath and
gradient ids stay unique inside one frame file."""
import math
import random
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent / "designs"))
from gouache import smooth_closed, smooth_open, blob, blob_pts, wash, strokes, ink, jitter  # noqa: E402,F401


def f1(v):
    return f"{v:.1f}"


class U:
    """Unique id factory: U('holly')('leaf') -> 'holly-leaf-3'."""

    def __init__(self, prefix):
        self.p, self.n = prefix, 0

    def __call__(self, name="x"):
        self.n += 1
        return f"{self.p}-{name}{self.n}"


def rot(x, y, cx, cy, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c


def lgrad(uid, stops, x1=0, y1=0, x2=0, y2=1, user=False):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a[0]}"' if a else "") + "/>" for o, c, *a in stops)
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    return f'<linearGradient id="{uid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>{s}</linearGradient>'


def rgrad(uid, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None, user=False):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a[0]}"' if a else "") + "/>" for o, c, *a in stops)
    f = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
    u = ' gradientUnits="userSpaceOnUse"' if user else ""
    return f'<radialGradient id="{uid}" cx="{cx}" cy="{cy}" r="{r}"{f}{u}>{s}</radialGradient>'


GOLD = [(0, "#7A5418"), (0.18, "#C99A3E"), (0.38, "#F4DC95"), (0.52, "#D9AE55"), (0.7, "#A67A2A"), (0.86, "#E9C979"), (1, "#8A6420")]
GOLD_SOFT = [(0, "#B48A3C"), (0.35, "#EBCF86"), (0.6, "#C9A04E"), (1, "#9C7430")]


# ---------------------------------------------------------------- textures
def paper_tex(uid, fleck="#8A6A4A", seed=5, density=1.0, size=120):
    """Speck + fibre pattern (no base) to lay over a mat."""
    rnd = random.Random(seed)
    specks = "".join(f'<circle cx="{rnd.uniform(0, size):.1f}" cy="{rnd.uniform(0, size):.1f}" r="{rnd.uniform(0.3, 0.9):.2f}" fill="{fleck}" opacity="{rnd.uniform(0.08, 0.22):.2f}"/>' for _ in range(int(36 * density)))
    fibres = "".join(f'<path d="M {rnd.uniform(0, size):.1f} {rnd.uniform(0, size):.1f} q {rnd.uniform(-4, 4):.1f} {rnd.uniform(-2, 2):.1f} {rnd.uniform(-9, 9):.1f} {rnd.uniform(-3, 3):.1f}" stroke="{fleck}" stroke-width="0.5" fill="none" opacity="0.12"/>' for _ in range(int(9 * density)))
    return (f'<defs><pattern id="{uid}" width="{size}" height="{size}" patternUnits="userSpaceOnUse">{specks}{fibres}</pattern></defs>'
            f'<rect width="600" height="600" fill="url(#{uid})"/>')


def mottle(seed, colors, n=14, op=(0.02, 0.05)):
    rnd = random.Random(seed)
    return "".join(f'<ellipse cx="{rnd.uniform(0, 600):.0f}" cy="{rnd.uniform(0, 600):.0f}" rx="{rnd.uniform(60, 190):.0f}" ry="{rnd.uniform(40, 150):.0f}" '
                   f'fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*op):.3f}"/>' for _ in range(n))


def linen_tex(uid, line="#9C8B70", seed=3, op=0.16):
    """Woven linen: irregular fine warp and weft threads."""
    rnd = random.Random(seed)
    out = []
    for i in range(40):
        y = i * 3 + rnd.uniform(-0.6, 0.6)
        out.append(f'<path d="M 0 {y:.1f} H 120" stroke="{line}" stroke-width="{rnd.uniform(0.4, 1.1):.2f}" opacity="{rnd.uniform(op * 0.4, op):.2f}"/>')
        x = i * 3 + rnd.uniform(-0.6, 0.6)
        out.append(f'<path d="M {x:.1f} 0 V 120" stroke="{line}" stroke-width="{rnd.uniform(0.4, 1.0):.2f}" opacity="{rnd.uniform(op * 0.3, op * 0.8):.2f}"/>')
    for _ in range(14):  # slubs
        x, y = rnd.uniform(0, 120), rnd.uniform(0, 120)
        out.append(f'<path d="M {x:.1f} {y:.1f} h {rnd.uniform(4, 12):.1f}" stroke="{line}" stroke-width="1.4" opacity="{op * 0.9:.2f}" stroke-linecap="round"/>')
    return (f'<defs><pattern id="{uid}" width="120" height="120" patternUnits="userSpaceOnUse">{"".join(out)}</pattern></defs>'
            f'<rect width="600" height="600" fill="url(#{uid})"/>')


def grain_tex(uid, color="#3A2418", seed=9, op=1.0):
    rnd = random.Random(seed)
    specks = "".join(f'<circle cx="{rnd.uniform(0, 90):.1f}" cy="{rnd.uniform(0, 90):.1f}" r="{rnd.uniform(0.3, 0.8):.2f}" fill="{rnd.choice([color, "#FFFFFF"])}" opacity="{rnd.uniform(0.05, 0.16):.2f}"/>' for _ in range(50))
    return (f'<defs><pattern id="{uid}" width="90" height="90" patternUnits="userSpaceOnUse">{specks}</pattern></defs>'
            f'<rect width="600" height="600" fill="url(#{uid})" opacity="{op}"/>')


# ---------------------------------------------------------------- generic painted leaf
def leaf_outline(bx, by, L, W, ang, seed, bend=0.0, n=9, tip=1.0, base_round=0.35, wob=0.04):
    """Lanceolate leaf from base (bx,by) toward angle `ang` (deg, 0 = right, -90 = up). Returns (path, tip_xy, mid_path)."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    right, left = [], []
    for i in range(1, n):
        t = i / n
        hw = W / 2 * (math.sin(math.pi * min(1, t ** base_round * 1.0)) ** 0.9) * (1 - 0.25 * t) * (1 + rnd.uniform(-wob, wob))
        off = bend * L * math.sin(math.pi * t) * 0.18
        cx, cy = bx + ux * L * t + nx * off, by + uy * L * t + ny * off
        right.append((cx + nx * hw, cy + ny * hw))
        left.append((cx - nx * hw * (1 + rnd.uniform(-wob, wob)), cy - ny * hw))
    tipx, tipy = bx + ux * L * tip, by + uy * L * tip
    pts = [(bx, by)] + right + [(tipx, tipy)] + list(reversed(left))
    mid = [(bx, by)]
    for i in range(1, 6):
        t = i / 6
        off = bend * L * math.sin(math.pi * t) * 0.18
        mid.append((bx + ux * L * t + nx * off, by + uy * L * t + ny * off))
    mid.append((tipx, tipy))
    return smooth_closed(pts), (tipx, tipy), smooth_open(mid)


def painted_leaf(u, bx, by, L, W, ang, fill, dark, light, seed, bend=0.0, vein=None, inkc=None, texture=True, veins=True, n_str=None):
    d, tip, mid = leaf_outline(bx, by, L, W, ang, seed, bend)
    out = [wash_use(u, d, fill, seed, dark, 1.4)]
    # darker half (shadow side)
    a = math.radians(ang)
    nx, ny = -math.sin(a), math.cos(a)
    sh = smooth_closed([(bx, by)] + [(bx + math.cos(a) * L * t + nx * W * 0.42 * math.sin(math.pi * t) * (1 - .25 * t), by + math.sin(a) * L * t + ny * W * 0.42 * math.sin(math.pi * t) * (1 - .25 * t)) for t in (0.2, 0.4, 0.6, 0.8)] + [tip]
                       + [(bx + math.cos(a) * L * t, by + math.sin(a) * L * t) for t in (0.75, 0.5, 0.25)])
    out.append(f'<path d="{sh}" fill="{dark}" opacity="0.32"/>')
    if texture:
        out.append(strokes(u("ls"), d, (min(bx, tip[0]) - W, min(by, tip[1]) - W, max(bx, tip[0]) + W, max(by, tip[1]) + W),
                           [light, dark, fill], seed + 1, n=n_str or max(8, int(L * 0.45)), angle=ang, length=(L * 0.15, L * 0.4),
                           width=(W * 0.04, W * 0.11), opacity=(0.18, 0.45), curve=0.2))
    if veins:
        vc = vein or light
        out.append(f'<path d="{mid}" fill="none" stroke="{vc}" stroke-width="{max(1.0, W * 0.05):.1f}" stroke-linecap="round" opacity="0.75"/>')
        for t in (0.3, 0.5, 0.7):
            px, py = bx + math.cos(a) * L * t, by + math.sin(a) * L * t
            for s in (1, -1):
                ex, ey = px + math.cos(a) * L * 0.14 + s * nx * W * 0.32, py + math.sin(a) * L * 0.14 + s * ny * W * 0.32
                out.append(f'<path d="M {f1(px)} {f1(py)} Q {f1(px + s * nx * W * 0.2)} {f1(py + s * ny * W * 0.2)} {f1(ex)} {f1(ey)}" stroke="{vc}" stroke-width="{max(0.7, W * 0.025):.1f}" fill="none" opacity="0.5"/>')
    if inkc:
        out.append(ink(d, inkc, max(1.0, W * 0.035), seed, 1, 0.55))
    return "".join(out)


def wash_use(u, d, color, seed, edge=None, edge_w=1.4, spread=0.7):
    """Compact wash: the shape once (fill + soft pooled edge) and one offset translucent copy via <use>."""
    rnd = random.Random(seed)
    pid = u("w")
    e = f' stroke="{edge}" stroke-width="{edge_w}" stroke-opacity="0.45" stroke-linejoin="round"' if edge else ""
    return (f'<path id="{pid}" d="{d}" fill="{color}"{e}/>'
            f'<use href="#{pid}" opacity="{rnd.uniform(0.25, 0.45):.2f}" transform="translate({rnd.uniform(-spread, spread):.1f} {rnd.uniform(-spread, spread):.1f})"/>')


def stem(pts, color, w=2.4, seed=1):
    return ink(smooth_open(pts), color, w, seed, 2, 0.9)


# ---------------------------------------------------------------- holly, pine, berries
def holly_leaf(u, bx, by, L, ang, seed, fill="#2F6E45", dark="#1D4A2E", light="#6FA86E"):
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    W = L * 0.42
    ts = [0.0, 0.17, 0.36, 0.56, 0.76, 1.0]

    def pt(t, side, k):
        hw = W / 2 * math.sin(math.pi * min(t, 0.98) ** 0.85) * k
        return bx + ux * L * t + side * nx * hw, by + uy * L * t + side * ny * hw

    d = [f"M {f1(bx)} {f1(by)}"]
    for side in (1, -1):
        seq = ts[1:-1] if side == 1 else list(reversed(ts[1:-1]))
        prev = (bx, by) if side == 1 else (bx + ux * L, by + uy * L)
        for t in seq:
            sp = pt(t, side, 1.25 + rnd.uniform(-0.06, 0.06))
            mx, my = (prev[0] + sp[0]) / 2, (prev[1] + sp[1]) / 2
            cx, cy = 0.55 * mx + 0.45 * (bx + ux * L * t), 0.55 * my + 0.45 * (by + uy * L * t)
            d.append(f"Q {f1(cx)} {f1(cy)} {f1(sp[0])} {f1(sp[1])}")
            prev = sp
        end = (bx + ux * L * 1.04, by + uy * L * 1.04) if side == 1 else (bx, by)
        mx, my = (prev[0] + end[0]) / 2, (prev[1] + end[1]) / 2
        tt = 0.9 if side == 1 else 0.08
        d.append(f"Q {f1(0.55 * mx + 0.45 * (bx + ux * L * tt))} {f1(0.55 * my + 0.45 * (by + uy * L * tt))} {f1(end[0])} {f1(end[1])}")
    d = " ".join(d) + " Z"
    out = [wash(d, fill, seed, 2, 0.6, 0.5, edge=dark, edge_w=1.6)]
    half = (f"M {f1(bx)} {f1(by)} " + " ".join(f"L {f1(p[0])} {f1(p[1])}" for p in [pt(t, -1, 1.0) for t in (0.2, 0.4, 0.6, 0.8)])
            + f" L {f1(bx + ux * L)} {f1(by + uy * L)} Z")
    out.append(f'<path d="{half}" fill="{dark}" opacity="0.35"/>')
    out.append(strokes(u("hl"), d, (min(bx, bx + ux * L) - W, min(by, by + uy * L) - W, max(bx, bx + ux * L) + W, max(by, by + uy * L) + W),
                       [light, dark, "#A8CF8E"], seed + 3, n=int(L * 0.5), angle=ang + 25, length=(L * 0.12, L * 0.3), width=(1, 2.6), opacity=(0.15, 0.4)))
    # glossy highlight along the upper half
    hp = smooth_open([pt(t, 1, 0.45) for t in (0.18, 0.4, 0.62)])
    out.append(f'<path d="{hp}" stroke="#E8F4D8" stroke-width="{max(1.6, L * 0.035):.1f}" fill="none" stroke-linecap="round" opacity="0.5"/>')
    out.append(f'<path d="M {f1(bx)} {f1(by)} L {f1(bx + ux * L * 0.95)} {f1(by + uy * L * 0.95)}" stroke="#C9E0B0" stroke-width="{max(1, L * 0.022):.1f}" opacity="0.7"/>')
    out.append(ink(d, "#173A24", 1.4, seed, 1, 0.55))
    return "".join(out)


def berry(u, cx, cy, r, col="#C8323A", dark="#7E1520", light="#F26A6A"):
    g = u("bg")
    return ("<defs>" + rgrad(g, [(0, light), (0.55, col), (1, dark)], 0.38, 0.35, 0.7) + "</defs>" +
            f'<circle cx="{f1(cx + r * 0.12)}" cy="{f1(cy + r * 0.18)}" r="{f1(r)}" fill="#3A1418" opacity="0.18"/>'
            f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="url(#{g})"/>'
            f'<circle cx="{f1(cx - r * 0.35)}" cy="{f1(cy - r * 0.38)}" r="{f1(r * 0.24)}" fill="#FFF4EE" opacity="0.85"/>'
            f'<circle cx="{f1(cx + r * 0.3)}" cy="{f1(cy + r * 0.3)}" r="{f1(max(0.9, r * 0.12))}" fill="#3A1418" opacity="0.6"/>')


def pine_sprig(u, bx, by, L, ang, seed, needle="#2E5A4C", dark="#1E3E34", light="#5E8C76", twig="#6B4A2E", density=1.0):
    rnd = random.Random(seed)
    a = math.radians(ang)
    pts = []
    for i in range(7):
        t = i / 6
        bendv = math.sin(t * math.pi) * L * 0.06
        pts.append((bx + math.cos(a) * L * t - math.sin(a) * bendv, by + math.sin(a) * L * t + math.cos(a) * bendv))
    out = []
    needles = []
    for k in range(int(70 * density * L / 120)):
        t = rnd.uniform(0.04, 1.0)
        i = min(5, int(t * 6))
        p0, p1 = pts[i], pts[i + 1]
        f = t * 6 - i
        px, py = p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f
        side = rnd.choice((1, -1))
        na = ang + side * rnd.uniform(35, 62)
        nl = rnd.uniform(0.13, 0.2) * L * (1 - 0.35 * t)
        ex, ey = px + math.cos(math.radians(na)) * nl, py + math.sin(math.radians(na)) * nl
        col = rnd.choice([needle, needle, dark, light])
        needles.append(f'<path d="M {f1(px)} {f1(py)} Q {f1((px + ex) / 2 + rnd.uniform(-1.5, 1.5))} {f1((py + ey) / 2 + rnd.uniform(-1.5, 1.5))} {f1(ex)} {f1(ey)}" stroke="{col}" stroke-width="{rnd.uniform(1.4, 2.4):.1f}" stroke-linecap="round" fill="none"/>')
    out.append(stem(pts, twig, 2.6, seed))
    out.append("".join(needles))
    return "".join(out)


def pinecone(u, cx, cy, s, ang, seed):
    rnd = random.Random(seed)
    out = [f'<g transform="rotate({ang} {f1(cx)} {f1(cy)})">']
    out.append(f'<ellipse cx="{f1(cx + 2)}" cy="{f1(cy + 3)}" rx="{f1(s * 0.42)}" ry="{f1(s * 0.62)}" fill="#2A1A10" opacity="0.2"/>')
    out.append(f'<path d="{blob(cx, cy, s * 0.4, s * 0.6, seed, 0.04)}" fill="#5A3A22"/>')
    for row in range(7):
        yy = cy - s * 0.5 + row * s * 0.16
        wrow = s * 0.38 * math.sin(math.pi * (0.15 + row / 8))
        for k in range(-2, 3):
            xx = cx + k * wrow * 0.45 + (row % 2) * wrow * 0.22
            if abs(xx - cx) > wrow:
                continue
            sc = s * 0.13
            out.append(f'<path d="M {f1(xx - sc)} {f1(yy)} Q {f1(xx)} {f1(yy + sc * 1.6)} {f1(xx + sc)} {f1(yy)} Q {f1(xx)} {f1(yy + sc * 0.6)} {f1(xx - sc)} {f1(yy)} Z" fill="{rnd.choice(["#8A5A32", "#9C6A3C", "#7A4A28"])}" stroke="#3A2414" stroke-width="0.8"/>')
            out.append(f'<path d="M {f1(xx - sc * 0.6)} {f1(yy + sc * 0.5)} q {f1(sc * 0.6)} {f1(sc * 0.5)} {f1(sc * 1.2)} 0" stroke="#D9A86A" stroke-width="1" fill="none" opacity="0.6"/>')
    out.append("</g>")
    return "".join(out)


# ---------------------------------------------------------------- flowers
def petal(u, cx, cy, r_in, r_out, ang, width, fill, dark, light, seed, cup=0.0):
    """One painted petal from radius r_in to r_out along angle ang (deg)."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    bx, by = cx + ux * r_in, cy + uy * r_in
    L = r_out - r_in
    pts = [(bx - nx * width * 0.18, by - ny * width * 0.18)]
    for t, k in ((0.3, 0.42), (0.6, 0.5), (0.85, 0.44)):
        pts.append((bx + ux * L * t - nx * width * k, by + uy * L * t - ny * width * k))
    # ruffled outer edge
    for j in range(5):
        s = -0.36 + j * 0.18
        dip = (0.92 if j % 2 else 1.0) + rnd.uniform(-0.03, 0.03)
        pts.append((bx + ux * L * dip + nx * width * s, by + uy * L * dip + ny * width * s))
    for t, k in ((0.85, 0.44), (0.6, 0.5), (0.3, 0.42)):
        pts.append((bx + ux * L * t + nx * width * k, by + uy * L * t + ny * width * k))
    pts.append((bx + nx * width * 0.18, by + ny * width * 0.18))
    d = smooth_closed(pts)
    out = [wash(d, fill, seed, 2, 0.6, 0.55, edge=dark, edge_w=1.1)]
    # base shadow (petals are darker toward the centre)
    g = u("pg")
    out.append(f'<defs>{lgrad(g, [(0, dark, 0.55), (0.55, dark, 0.0)], bx, by, bx + ux * L, by + uy * L, user=True)}</defs><path d="{d}" fill="url(#{g})"/>')
    out.append(strokes(u("ps"), d, (min(bx, bx + ux * L) - width, min(by, by + uy * L) - width, max(bx, bx + ux * L) + width, max(by, by + uy * L) + width),
                       [light, dark, fill], seed + 2, n=max(6, int(L * 0.4)), angle=ang, length=(L * 0.3, L * 0.7), width=(0.8, 2.2), opacity=(0.15, 0.4), curve=0.25))
    # light rim on the outer edge
    rim = smooth_open(pts[4:9])
    out.append(f'<path d="{rim}" stroke="{light}" stroke-width="1.6" fill="none" opacity="0.7" stroke-linecap="round"/>')
    return "".join(out)


def peony(u, cx, cy, r, seed, fill="#F2A7B5", dark="#C9667E", light="#FFE3E8", heart="#F7D36B"):
    rnd = random.Random(seed)
    out = [f'<ellipse cx="{f1(cx + r * 0.08)}" cy="{f1(cy + r * 0.12)}" rx="{f1(r * 1.0)}" ry="{f1(r * 0.92)}" fill="#5A2A30" opacity="0.12"/>']
    n = 9
    for i in range(n):  # outer ring
        ang = i * 360 / n + rnd.uniform(-8, 8)
        out.append(petal(u, cx, cy, r * 0.1, r * rnd.uniform(0.92, 1.02), ang, r * 0.62, fill, dark, light, seed + i))
    for i in range(7):  # middle ring, lighter
        ang = i * 360 / 7 + 20 + rnd.uniform(-8, 8)
        out.append(petal(u, cx, cy, r * 0.05, r * rnd.uniform(0.66, 0.74), ang, r * 0.5, light if i % 2 else fill, dark, "#FFFFFF", seed + 20 + i))
    for i in range(5):  # cupped centre petals
        ang = i * 72 + 40
        out.append(petal(u, cx, cy, 0, r * 0.42, ang, r * 0.36, "#F7C2CC", dark, "#FFFFFF", seed + 40 + i))
    out.append(f'<path d="{blob(cx, cy, r * 0.14, r * 0.12, seed, 0.12)}" fill="{heart}" opacity="0.9"/>')
    for k in range(9):
        a = rnd.uniform(0, 6.28)
        rr_ = rnd.uniform(0, r * 0.12)
        out.append(f'<circle cx="{f1(cx + math.cos(a) * rr_)}" cy="{f1(cy + math.sin(a) * rr_)}" r="{rnd.uniform(1.2, 2.2):.1f}" fill="#D9932E"/>')
    return "".join(out)


def rose(u, cx, cy, r, seed, fill="#E5788A", dark="#A8384E", light="#FFC6CF"):
    rnd = random.Random(seed)
    out = [f'<ellipse cx="{f1(cx + r * 0.1)}" cy="{f1(cy + r * 0.14)}" rx="{f1(r)}" ry="{f1(r * 0.9)}" fill="#4A1A24" opacity="0.14"/>']
    for i in range(6):
        ang = i * 60 + rnd.uniform(-10, 10)
        out.append(petal(u, cx, cy, r * 0.2, r * rnd.uniform(0.95, 1.05), ang, r * 0.75, fill, dark, light, seed + i))
    base = blob(cx, cy, r * 0.62, r * 0.56, seed + 9, 0.05)
    out.append(wash(base, fill, seed + 9, 2, 0.6, 0.5))
    g = u("rg")
    out.append(f'<defs>{rgrad(g, [(0, dark, 0.75), (0.6, dark, 0.15), (1, fill, 0)], cx, cy - r * 0.05, r * 0.6, user=True)}</defs><path d="{base}" fill="url(#{g})"/>')
    # spiralling petal edges
    for k in range(5):
        rr_ = r * (0.52 - k * 0.1)
        a0 = rnd.uniform(0, 360) + k * 70
        a1 = a0 + 200
        p0 = (cx + rr_ * math.cos(math.radians(a0)), cy + rr_ * 0.9 * math.sin(math.radians(a0)))
        p1 = (cx + rr_ * math.cos(math.radians(a1)), cy + rr_ * 0.9 * math.sin(math.radians(a1)))
        out.append(f'<path d="M {f1(p0[0])} {f1(p0[1])} A {f1(rr_)} {f1(rr_ * 0.9)} 0 1 1 {f1(p1[0])} {f1(p1[1])}" fill="none" stroke="{light}" stroke-width="{max(1.4, r * 0.06):.1f}" stroke-linecap="round" opacity="0.9"/>')
        out.append(f'<path d="M {f1(p0[0])} {f1(p0[1] + 1.5)} A {f1(rr_)} {f1(rr_ * 0.9)} 0 1 1 {f1(p1[0])} {f1(p1[1] + 1.5)}" fill="none" stroke="{dark}" stroke-width="{max(0.9, r * 0.025):.1f}" stroke-linecap="round" opacity="0.6"/>')
    out.append(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r * 0.07)}" fill="{dark}"/>')
    return "".join(out)


def bud(u, cx, cy, r, ang, seed, fill="#E5788A", dark="#A8384E", leaf="#7A9A6E"):
    out = [f'<g transform="rotate({ang} {f1(cx)} {f1(cy)})">']
    d = smooth_closed([(cx, cy - r), (cx + r * 0.7, cy - r * 0.1), (cx + r * 0.5, cy + r * 0.6), (cx, cy + r * 0.75), (cx - r * 0.5, cy + r * 0.6), (cx - r * 0.7, cy - r * 0.1)])
    out.append(wash(d, fill, seed, 2, 0.5, 0.5, edge=dark))
    out.append(f'<path d="M {f1(cx - r * 0.1)} {f1(cy - r * 0.8)} Q {f1(cx + r * 0.4)} {f1(cy)} {f1(cx)} {f1(cy + r * 0.6)}" stroke="{dark}" stroke-width="1.4" fill="none" opacity="0.6"/>')
    for s in (-1, 1):
        sd = smooth_closed([(cx, cy + r * 0.85), (cx + s * r * 0.65, cy + r * 0.2), (cx + s * r * 0.45, cy - r * 0.35), (cx + s * r * 0.2, cy + r * 0.4)])
        out.append(f'<path d="{sd}" fill="{leaf}"/>')
    out.append("</g>")
    return "".join(out)


def filler_sprig(u, bx, by, L, ang, seed, col="#F7F0E6", dot="#E8D8B8", stemc="#7A8A62"):
    """Baby's-breath style sprig: thin stems with tiny flower dots."""
    rnd = random.Random(seed)
    out = []
    a = math.radians(ang)
    tip = (bx + math.cos(a) * L, by + math.sin(a) * L)
    out.append(f'<path d="M {f1(bx)} {f1(by)} Q {f1((bx + tip[0]) / 2 + 4)} {f1((by + tip[1]) / 2 - 4)} {f1(tip[0])} {f1(tip[1])}" stroke="{stemc}" stroke-width="1.6" fill="none"/>')
    for k in range(7):
        t = 0.35 + k * 0.1
        px, py = bx + math.cos(a) * L * t, by + math.sin(a) * L * t
        ba = ang + rnd.choice((-1, 1)) * rnd.uniform(25, 50)
        l2 = L * rnd.uniform(0.12, 0.25)
        ex, ey = px + math.cos(math.radians(ba)) * l2, py + math.sin(math.radians(ba)) * l2
        out.append(f'<path d="M {f1(px)} {f1(py)} L {f1(ex)} {f1(ey)}" stroke="{stemc}" stroke-width="1.1"/>')
        out.append(f'<circle cx="{f1(ex)}" cy="{f1(ey)}" r="{rnd.uniform(2.6, 3.8):.1f}" fill="{col}" stroke="{dot}" stroke-width="0.8"/>')
    out.append(f'<circle cx="{f1(tip[0])}" cy="{f1(tip[1])}" r="3.4" fill="{col}" stroke="{dot}" stroke-width="0.8"/>')
    return "".join(out)


def hibiscus(u, cx, cy, r, ang, seed, fill="#F0645A", dark="#B8323A", light="#FFB4A0"):
    rnd = random.Random(seed)
    out = [f'<ellipse cx="{f1(cx + 4)}" cy="{f1(cy + 6)}" rx="{f1(r)}" ry="{f1(r * 0.9)}" fill="#3A1410" opacity="0.15"/>']
    for i in range(5):
        out.append(petal(u, cx, cy, r * 0.05, r * rnd.uniform(0.95, 1.05), ang + i * 72, r * 0.95, fill, dark, light, seed + i))
    g = u("hb")
    out.append(f'<defs>{rgrad(g, [(0, "#8A1430", 0.95), (0.35, "#B8233A", 0.6), (1, fill, 0)], cx, cy, r * 0.55, user=True)}</defs>'
               f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r * 0.55)}" fill="url(#{g})"/>')
    a = math.radians(ang - 50)
    ex, ey = cx + math.cos(a) * r * 0.85, cy + math.sin(a) * r * 0.85
    out.append(f'<path d="M {f1(cx)} {f1(cy)} Q {f1((cx + ex) / 2 + 6)} {f1((cy + ey) / 2)} {f1(ex)} {f1(ey)}" stroke="#F6E2C0" stroke-width="3" fill="none" stroke-linecap="round"/>')
    for k in range(7):
        out.append(f'<circle cx="{f1(ex + rnd.uniform(-7, 7))}" cy="{f1(ey + rnd.uniform(-7, 7))}" r="2.4" fill="#F7C53A" stroke="#C98A1A" stroke-width="0.6"/>')
    return "".join(out)


# ---------------------------------------------------------------- foliage
def euca_leaf(u, cx, cy, r, ang, seed, fill="#8FAE9C", dark="#5E7E6E", light="#C8DACB"):
    d = blob(cx, cy, r, r * 0.86, seed, 0.05, 10 if r < 14 else 12, rot=ang)
    out = [wash_use(u, d, fill, seed, dark, 1.2, 0.5)]
    if r >= 14:
        out.append(strokes(u("eu"), d, (cx - r, cy - r, cx + r, cy + r), [light, dark, "#B4CBBA"], seed, n=4, angle=ang - 60, length=(r * 0.6, r * 1.2), width=(1.2, 2.6), opacity=(0.2, 0.45)))
    out.append(f'<ellipse cx="{f1(cx - r * 0.25)}" cy="{f1(cy - r * 0.25)}" rx="{f1(r * 0.4)}" ry="{f1(r * 0.28)}" transform="rotate({ang:.0f} {f1(cx - r * 0.25)} {f1(cy - r * 0.25)})" fill="#FFFFFF" opacity="0.18"/>')
    a = math.radians(ang + 90)
    out.append(f'<path d="M {f1(cx - math.cos(a) * r * 0.75)} {f1(cy - math.sin(a) * r * 0.75)} Q {f1(cx + 1)} {f1(cy + 1)} {f1(cx + math.cos(a) * r * 0.6)} {f1(cy + math.sin(a) * r * 0.6)}" stroke="{dark}" stroke-width="1" fill="none" opacity="0.5"/>')
    return "".join(out)


def euca_stem(u, pts, seed, leaf_r=(9, 14), every=0.11, fill="#8FAE9C", dark="#5E7E6E", light="#C8DACB", stemc="#8A6A5A"):
    """Silver-dollar eucalyptus: a curving stem with pairs of round leaves that get smaller toward the tip."""
    rnd = random.Random(seed)
    out = [stem(pts, stemc, 2.2, seed)]
    n = len(pts)
    leaves = []
    t = 0.06
    while t < 1.0:
        f = t * (n - 1)
        i = min(n - 2, int(f))
        fr = f - i
        px = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * fr
        py = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * fr
        tang = math.degrees(math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0]))
        r = leaf_r[1] - (leaf_r[1] - leaf_r[0]) * t
        for s in (1, -1):
            a = math.radians(tang + s * rnd.uniform(60, 85))
            lx, ly = px + math.cos(a) * r * 0.95, py + math.sin(a) * r * 0.95
            shade = rnd.choice([fill, fill, "#9FBBA8", "#7E9E8C"])
            leaves.append(euca_leaf(u, lx, ly, r, tang + s * 70, seed + int(t * 100) + s, shade, dark, light))
        t += every * rnd.uniform(0.85, 1.15)
    return out[0] + "".join(leaves)


def monstera(u, bx, by, L, ang, seed, fill="#2F7A55", dark="#1B5038", light="#6BB08A", hole_bg=None):
    """Split-leaf monstera from its stalk base, pointing along ang. Slits are real gaps (path has notches)."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    stalk = L * 0.28
    ox, oy = bx + ux * stalk, by + uy * stalk  # leaf base (sinus)
    W = L * 0.9

    def P(t, s, k=1.0):
        hw = W / 2 * math.sin(math.pi * (0.08 + 0.92 * t) ** 0.9) * k
        return ox + ux * L * t + s * nx * hw, oy + uy * L * t + s * ny * hw

    pts = []
    slits = [0.22, 0.4, 0.58, 0.74]
    for s in (1, -1):
        seq = [0.02, 0.1] + [x for t in slits for x in (t - 0.035, t, t + 0.035)] + [0.88, 0.97]
        side = []
        for t in seq:
            if any(abs(t - st) < 1e-6 for st in slits):
                depth = rnd.uniform(0.38, 0.52)
                side.append(P(t + 0.02, s, depth))
            else:
                side.append(P(t, s, 1.0 + rnd.uniform(-0.03, 0.03)))
        pts.append(side if s == 1 else list(reversed(side)))
    tip = (ox + ux * L * 1.02, oy + uy * L * 1.02)
    base_notch = (ox + ux * L * 0.08, oy + uy * L * 0.08)
    outline = [base_notch] + pts[0] + [tip] + pts[1]
    d = "M " + " L ".join(f"{f1(x)} {f1(y)}" for x, y in outline) + " Z"
    # rounded lobes: smooth only the lobe tips, keep slits sharp -> use smooth_closed on a jittered copy
    d = smooth_closed(outline)
    holes = ""
    for t in (0.33, 0.5, 0.66):
        for s in (1, -1):
            hx, hy = ox + ux * L * t + s * nx * W * 0.13, oy + uy * L * t + s * ny * W * 0.13
            holes += " " + blob(hx, hy, W * 0.035, W * 0.06, seed + int(t * 50) + s, 0.1, 10, rot=ang)
    full = d + holes
    out = [f'<path d="M {f1(bx)} {f1(by)} Q {f1(bx + ux * stalk * 0.5 + nx * 6)} {f1(by + uy * stalk * 0.5 + ny * 6)} {f1(ox)} {f1(oy)}" stroke="{dark}" stroke-width="{max(3, L * 0.03):.1f}" fill="none" stroke-linecap="round"/>']
    out.append(f'<path d="{full}" fill="#0E2A1E" opacity="0.18" fill-rule="evenodd" transform="translate(4 6)"/>')
    out.append(f'<path d="{full}" fill="{fill}" fill-rule="evenodd"/>')
    cid = u("mo")
    out.append(f'<clipPath id="{cid}"><path d="{full}" clip-rule="evenodd"/></clipPath><g clip-path="url(#{cid})">')
    out.append(f'<path d="M {f1(ox)} {f1(oy)} ' + " ".join(f"L {f1(p[0])} {f1(p[1])}" for p in [P(t, -1, 1.1) for t in (0.2, 0.5, 0.8)]) + f' L {f1(tip[0])} {f1(tip[1])} Z" fill="{dark}" opacity="0.35"/>')
    st = strokes(u("ms"), full, (min(ox, tip[0]) - W, min(oy, tip[1]) - W, max(ox, tip[0]) + W, max(oy, tip[1]) + W), [light, dark, "#4E9A70"], seed + 2,
                 n=int(L * 0.4), angle=ang + 70, length=(W * 0.14, W * 0.36), width=(1.2, 3.2), opacity=(0.15, 0.4))
    out.append(st)
    # veins
    for t in slits + [0.88]:
        for s in (1, -1):
            p0 = (ox + ux * L * (t - 0.08), oy + uy * L * (t - 0.08))
            p1 = P(t - 0.01, s, 0.9)
            out.append(f'<path d="M {f1(p0[0])} {f1(p0[1])} Q {f1((p0[0] + p1[0]) / 2 + ux * 6)} {f1((p0[1] + p1[1]) / 2 + uy * 6)} {f1(p1[0])} {f1(p1[1])}" stroke="{light}" stroke-width="1.3" fill="none" opacity="0.55"/>')
    out.append(f'<path d="M {f1(ox)} {f1(oy)} L {f1(tip[0])} {f1(tip[1])}" stroke="#A8D8B4" stroke-width="{max(1.6, L * 0.014):.1f}" opacity="0.8"/>')
    out.append("</g>")
    out.append(ink(d, "#123A28", 1.3, seed, 1, 0.5))
    return "".join(out)


def palm_frond(u, bx, by, L, ang, seed, fill="#3E8A5A", dark="#22603C", light="#8CC48E", curl=0.25, n=14):
    rnd = random.Random(seed)
    a = math.radians(ang)
    pts = []
    for i in range(9):
        t = i / 8
        bend = curl * L * t * t
        pts.append((bx + math.cos(a) * L * t - math.sin(a) * bend, by + math.sin(a) * L * t + math.cos(a) * bend))
    out = []
    lfs = []
    for k in range(n):
        t = 0.12 + 0.86 * k / n
        i = min(7, int(t * 8))
        fr = t * 8 - i
        px = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * fr
        py = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * fr
        tang = math.degrees(math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0]))
        ll = L * 0.42 * math.sin(math.pi * (0.25 + 0.7 * t))
        for s in (1, -1):
            la = tang + s * rnd.uniform(38, 52)
            lfs.append(painted_leaf(u, px, py, ll, ll * 0.2, la, rnd.choice([fill, fill, dark, "#4C9A66"]), dark, light, seed + k * 3 + s,
                                    bend=s * 0.6, texture=False, veins=False))
            ex, ey = px + math.cos(math.radians(la)) * ll * 0.9, py + math.sin(math.radians(la)) * ll * 0.9
            lfs.append(f'<path d="M {f1(px)} {f1(py)} L {f1(ex)} {f1(ey)}" stroke="{light}" stroke-width="1" opacity="0.6"/>')
    out.append("".join(lfs))
    out.append(stem(pts, "#5C7A3A", max(2, L * 0.02), seed))
    return "".join(out)


def laurel(u, pts, seed, side=1, leaf_l=26, fill=None, dark="#8A6420", berries=True, gold_id=None):
    """Laurel branch along pts; leaves alternate with gold gradient fill (gold_id) or a flat fill."""
    rnd = random.Random(seed)
    out = [ink(smooth_open(pts), dark, 2.4, seed, 1, 0.9)]
    n = len(pts)
    t = 0.04
    k = 0
    while t < 0.98:
        f = t * (n - 1)
        i = min(n - 2, int(f))
        fr = f - i
        px = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * fr
        py = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * fr
        tang = math.degrees(math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0]))
        ll = leaf_l * (1.0 - 0.35 * t)
        for s in (1, -1):
            la = tang + s * 38 + rnd.uniform(-6, 6)
            d, tip, mid = leaf_outline(px, py, ll, ll * 0.38, la, seed + k, bend=s * 0.3, base_round=0.5)
            fl = f"url(#{gold_id})" if gold_id else fill
            out.append(f'<path d="{d}" fill="{fl}"/><path d="{d}" fill="none" stroke="{dark}" stroke-width="1" opacity="0.7"/>'
                       f'<path d="{mid}" stroke="{dark}" stroke-width="0.9" fill="none" opacity="0.6"/>')
            k += 1
        if berries and rnd.random() < 0.35:
            a = math.radians(tang - 90 * side)
            out.append(f'<circle cx="{f1(px + math.cos(a) * 9)}" cy="{f1(py + math.sin(a) * 9)}" r="3.6" fill="{f"url(#{gold_id})" if gold_id else dark}" stroke="{dark}" stroke-width="0.8"/>')
        t += 0.105
    tip = pts[-1]
    tang = math.degrees(math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0]))
    d, _, mid = leaf_outline(tip[0], tip[1], leaf_l * 0.7, leaf_l * 0.26, tang, seed + 99, base_round=0.5)
    out.append(f'<path d="{d}" fill="{f"url(#{gold_id})" if gold_id else fill}" stroke="{dark}" stroke-width="1"/>')
    return "".join(out)


# ---------------------------------------------------------------- fun pieces
def balloon(u, cx, cy, r, color, dark, light, seed, string_to=None, string_col="#7A6A5A"):
    rnd = random.Random(seed)
    g = u("ba")
    h = r * 1.18
    d = smooth_closed([(cx, cy - h), (cx + r * 0.82, cy - h * 0.62), (cx + r, cy - h * 0.05), (cx + r * 0.72, cy + h * 0.6),
                       (cx + r * 0.12, cy + h * 0.98), (cx - r * 0.12, cy + h * 0.98), (cx - r * 0.72, cy + h * 0.6), (cx - r, cy - h * 0.05), (cx - r * 0.82, cy - h * 0.62)])
    out = []
    if string_to:
        sx, sy = cx, cy + h + 6
        ex, ey = string_to
        mx = (sx + ex) / 2
        out.append(f'<path d="M {f1(sx)} {f1(sy)} C {f1(sx + 16)} {f1(sy + (ey - sy) * 0.3)} {f1(mx - 18)} {f1(sy + (ey - sy) * 0.6)} {f1(ex)} {f1(ey)}" stroke="{string_col}" stroke-width="1.8" fill="none"/>')
    out.append(f'<defs>{rgrad(g, [(0, light), (0.45, color), (1, dark)], 0.35, 0.3, 0.8, 0.32, 0.25)}</defs>')
    out.append(f'<path d="{d}" fill="url(#{g})"/>')
    out.append(strokes(u("bs"), d, (cx - r, cy - h, cx + r, cy + h), [light, dark, color], seed, n=int(r * 0.9), angle=-70, length=(r * 0.3, r * 0.8), width=(1, 2.6), opacity=(0.08, 0.22)))
    out.append(f'<path d="M {f1(cx - r * 0.55)} {f1(cy - h * 0.3)} Q {f1(cx - r * 0.5)} {f1(cy - h * 0.7)} {f1(cx - r * 0.1)} {f1(cy - h * 0.82)}" stroke="#FFFFFF" stroke-width="{f1(r * 0.12)}" stroke-linecap="round" fill="none" opacity="0.75"/>')
    out.append(f'<circle cx="{f1(cx - r * 0.62)}" cy="{f1(cy - h * 0.08)}" r="{f1(r * 0.06)}" fill="#FFFFFF" opacity="0.7"/>')
    out.append(f'<path d="M {f1(cx - r * 0.13)} {f1(cy + h + 6)} L {f1(cx)} {f1(cy + h - 2)} L {f1(cx + r * 0.13)} {f1(cy + h + 6)} Z" fill="{dark}"/>')
    out.append(ink(d, dark, 1.2, seed, 1, 0.45))
    return "".join(out)


def cloud(u, cx, cy, w, seed, fill="#FFFFFF", shade="#D7E3F2", light="#FFFFFF"):
    rnd = random.Random(seed)
    puffs = [(-0.36, 0.08, 0.2), (-0.15, -0.12, 0.27), (0.12, -0.18, 0.3), (0.36, 0.0, 0.22), (0.0, 0.12, 0.3)]
    out = []
    shapes = [blob(cx + dx * w, cy + dy * w, r * w, r * w * 0.82, seed + i, 0.05) for i, (dx, dy, r) in enumerate(puffs)]
    full = " ".join(shapes)
    out.append(f'<path d="{full}" fill="#6A7FA0" opacity="0.12" transform="translate(3 5)"/>')
    out.append(f'<path d="{full}" fill="{fill}"/>')
    cid = u("cl")
    out.append(f'<clipPath id="{cid}"><path d="{full}"/></clipPath><g clip-path="url(#{cid})">'
               f'<ellipse cx="{f1(cx)}" cy="{f1(cy + w * 0.32)}" rx="{f1(w * 0.6)}" ry="{f1(w * 0.18)}" fill="{shade}" opacity="0.9"/>'
               + strokes(u("cs"), full, (cx - w * 0.6, cy - w * 0.5, cx + w * 0.6, cy + w * 0.4), [shade, light, "#EAF0F8"], seed, n=int(w * 0.4), angle=-10, length=(w * 0.08, w * 0.22), width=(1, 3), opacity=(0.2, 0.5)) + "</g>")
    out.append(ink(full, "#9AAAC8", 1.0, seed, 1, 0.35))
    return "".join(out)


def soft_star(cx, cy, r, fill, rot=-90, stroke=None):
    pts = []
    for i in range(10):
        rr_ = r if i % 2 == 0 else r * 0.48
        a = math.radians(rot + i * 36)
        pts.append(f"{cx + rr_ * math.cos(a):.1f},{cy + rr_ * math.sin(a):.1f}")
    sw = max(1.5, r * 0.22)
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{stroke or fill}" stroke-width="{sw:.1f}" stroke-linejoin="round"/>'


def painted_star(u, cx, cy, r, seed, fill="#F6D27A", dark="#D9A43A", light="#FFF2C4", rot=-90):
    pts = []
    rnd = random.Random(seed)
    for i in range(10):
        rr_ = r * rnd.uniform(0.96, 1.04) if i % 2 == 0 else r * 0.5
        a = math.radians(rot + i * 36)
        pts.append((cx + rr_ * math.cos(a), cy + rr_ * math.sin(a)))
    d = "M " + " L ".join(f"{f1(x)} {f1(y)}" for x, y in pts) + " Z"
    out = [f'<path d="{d}" fill="{fill}" stroke="{fill}" stroke-width="{max(1.5, r * 0.25):.1f}" stroke-linejoin="round"/>']
    half = "M " + f"{f1(cx)} {f1(cy)} " + " ".join(f"L {f1(x)} {f1(y)}" for x, y in pts[4:8]) + " Z"
    out.append(f'<path d="{half}" fill="{dark}" opacity="0.35"/>')
    out.append(f'<circle cx="{f1(cx - r * 0.2)}" cy="{f1(cy - r * 0.2)}" r="{f1(r * 0.18)}" fill="{light}" opacity="0.8"/>')
    return "".join(out)


def sparkle(cx, cy, r, fill, op=1.0):
    return (f'<path d="M {f1(cx)} {f1(cy - r)} Q {f1(cx + r * 0.12)} {f1(cy - r * 0.12)} {f1(cx + r)} {f1(cy)} Q {f1(cx + r * 0.12)} {f1(cy + r * 0.12)} {f1(cx)} {f1(cy + r)} '
            f'Q {f1(cx - r * 0.12)} {f1(cy + r * 0.12)} {f1(cx - r)} {f1(cy)} Q {f1(cx - r * 0.12)} {f1(cy - r * 0.12)} {f1(cx)} {f1(cy - r)} Z" fill="{fill}" opacity="{op}"/>')


def painted_heart(u, cx, cy, s, seed, fill="#E2546A", dark="#A8283E", light="#FFB0BC", rot=0):
    k = s / 16
    d = (f"M {f1(cx)} {f1(cy + 18 * k)} C {f1(cx - 30 * k)} {f1(cy - 2 * k)} {f1(cx - 24 * k)} {f1(cy - 24 * k)} {f1(cx - 8 * k)} {f1(cy - 20 * k)} "
         f"Q {f1(cx - 2 * k)} {f1(cy - 18 * k)} {f1(cx)} {f1(cy - 12 * k)} Q {f1(cx + 2 * k)} {f1(cy - 18 * k)} {f1(cx + 8 * k)} {f1(cy - 20 * k)} "
         f"C {f1(cx + 24 * k)} {f1(cy - 24 * k)} {f1(cx + 30 * k)} {f1(cy - 2 * k)} {f1(cx)} {f1(cy + 18 * k)} Z")
    out = [f'<g transform="rotate({rot} {f1(cx)} {f1(cy)})">']
    out.append(f'<path d="{d}" fill="#4A1020" opacity="0.15" transform="translate({f1(s * 0.08)} {f1(s * 0.12)})"/>')
    out.append(wash(d, fill, seed, 2, 0.5, 0.55, edge=dark, edge_w=1.2))
    out.append(f'<path d="M {f1(cx + 4 * k)} {f1(cy + 12 * k)} C {f1(cx + 20 * k)} {f1(cy)} {f1(cx + 24 * k)} {f1(cy - 10 * k)} {f1(cx + 18 * k)} {f1(cy - 17 * k)} '
               f'C {f1(cx + 26 * k)} {f1(cy - 10 * k)} {f1(cx + 22 * k)} {f1(cy + 4 * k)} {f1(cx)} {f1(cy + 18 * k)} Z" fill="{dark}" opacity="0.35"/>')
    out.append(strokes(u("hs"), d, (cx - 2 * s, cy - 2 * s, cx + 2 * s, cy + 2 * s), [light, dark, fill], seed, n=max(6, int(s * 0.8)), angle=-60, length=(s * 0.3, s * 0.8), width=(0.8, max(1.2, s * 0.1)), opacity=(0.15, 0.4)))
    out.append(f'<path d="M {f1(cx - 17 * k)} {f1(cy - 8 * k)} Q {f1(cx - 17 * k)} {f1(cy - 17 * k)} {f1(cx - 9 * k)} {f1(cy - 17 * k)}" stroke="#FFFFFF" stroke-width="{f1(max(1.4, 2.6 * k))}" stroke-linecap="round" fill="none" opacity="0.75"/>')
    out.append("</g>")
    return "".join(out)


def confetti(seed, box, n, colors, avoid=None, size=(4, 9)):
    rnd = random.Random(seed)
    out = []
    x0, y0, x1, y1 = box
    tries = 0
    while len(out) < n and tries < n * 30:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if avoid and avoid(x, y):
            continue
        c = rnd.choice(colors)
        s = rnd.uniform(*size)
        kind = rnd.random()
        if kind < 0.45:
            out.append(f'<rect x="{f1(x - s / 2)}" y="{f1(y - s * 0.22)}" width="{f1(s)}" height="{f1(s * 0.44)}" rx="{f1(s * 0.15)}" fill="{c}" transform="rotate({rnd.uniform(0, 180):.0f} {f1(x)} {f1(y)})"/>')
        elif kind < 0.8:
            out.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{f1(s * 0.32)}" fill="{c}"/>')
        else:
            out.append(f'<path d="M {f1(x - s * 0.6)} {f1(y)} q {f1(s * 0.3)} {f1(-s * 0.5)} {f1(s * 0.6)} 0 t {f1(s * 0.6)} 0" stroke="{c}" stroke-width="{f1(max(1.6, s * 0.22))}" fill="none" stroke-linecap="round" transform="rotate({rnd.uniform(0, 180):.0f} {f1(x)} {f1(y)})"/>')
    return "".join(out)


def snowflake(cx, cy, r, color="#FFFFFF", shadow="#6E8EC8", sw=None, rot=0, kind=0):
    sw = sw or max(1.6, r * 0.09)
    arms = []
    for i in range(6):
        a = math.radians(rot + i * 60)
        ux, uy = math.cos(a), math.sin(a)
        ex, ey = cx + ux * r, cy + uy * r
        arms.append(f"M {f1(cx)} {f1(cy)} L {f1(ex)} {f1(ey)}")
        for t, bl in ((0.45, 0.32), (0.72, 0.22)) if kind == 0 else ((0.35, 0.22), (0.6, 0.3), (0.82, 0.16)):
            px, py = cx + ux * r * t, cy + uy * r * t
            for s in (1, -1):
                b = a + s * math.radians(55)
                arms.append(f"M {f1(px)} {f1(py)} L {f1(px + math.cos(b) * r * bl)} {f1(py + math.sin(b) * r * bl)}")
    d = " ".join(arms)
    tip = "".join(f'<circle cx="{f1(cx + math.cos(math.radians(rot + i * 60)) * r)}" cy="{f1(cy + math.sin(math.radians(rot + i * 60)) * r)}" r="{f1(sw * 0.75)}" fill="{color}"/>' for i in range(6))
    hexp = " ".join(f"{f1(cx + math.cos(math.radians(rot + 30 + i * 60)) * r * 0.16)},{f1(cy + math.sin(math.radians(rot + 30 + i * 60)) * r * 0.16)}" for i in range(6))
    return (f'<path d="{d}" stroke="{shadow}" stroke-width="{f1(sw)}" stroke-linecap="round" fill="none" opacity="0.35" transform="translate(1.5 2)"/>'
            f'<path d="{d}" stroke="{color}" stroke-width="{f1(sw)}" stroke-linecap="round" fill="none"/>{tip}'
            f'<polygon points="{hexp}" fill="{color}"/>')


def moon(u, cx, cy, r, seed, fill="#F8DC8A", dark="#E2B44E", light="#FFF4CC", rot=-20):
    cut = (cx + r * 0.55, cy - r * 0.25)
    # crescent: outer circle minus offset circle, as an explicit path of two arcs
    d = f"M {f1(cx)} {f1(cy - r)} A {f1(r)} {f1(r)} 0 1 0 {f1(cx + r * 0.86)} {f1(cy + r * 0.5)} A {f1(r * 0.82)} {f1(r * 0.82)} 0 1 1 {f1(cx)} {f1(cy - r)} Z"
    g = u("mn")
    out = [f'<defs>{rgrad(g, [(0, "#FFF6D8", 0.85), (1, "#FFF6D8", 0)], cx, cy, r * 1.9, user=True)}</defs>'
           f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r * 1.9)}" fill="url(#{g})"/>']
    out.append(f'<g transform="rotate({rot} {f1(cx)} {f1(cy)})">')
    out.append(wash(d, fill, seed, 2, 0.6, 0.55, edge=dark, edge_w=1.4))
    out.append(strokes(u("ms"), d, (cx - r, cy - r, cx + r, cy + r), [light, dark, fill], seed, n=int(r * 0.9), angle=-75, length=(r * 0.2, r * 0.5), width=(1, 2.6), opacity=(0.18, 0.45)))
    for dx, dy, rr_ in ((-0.55, 0.1, 0.1), (-0.35, 0.5, 0.07), (-0.62, -0.35, 0.06)):
        out.append(f'<circle cx="{f1(cx + dx * r)}" cy="{f1(cy + dy * r)}" r="{f1(rr_ * r)}" fill="{dark}" opacity="0.4"/>')
    out.append("</g>")
    return "".join(out)


def bunting(u, x0, x1, y, sag, n, colors, seed, flag_h=34, flag_w=None, string="#8A6A5A"):
    rnd = random.Random(seed)
    out = []
    mid = (x0 + x1) / 2

    def yat(x):
        t = (x - x0) / (x1 - x0)
        return y + sag * 4 * t * (1 - t)
    out.append(f'<path d="M {f1(x0)} {f1(y)} Q {f1(mid)} {f1(y + sag * 2)} {f1(x1)} {f1(y)}" stroke="{string}" stroke-width="2" fill="none"/>')
    fw = flag_w or (x1 - x0) / n * 0.82
    for i in range(n):
        cx = x0 + (x1 - x0) * (i + 0.5) / n
        lx, rx = cx - fw / 2, cx + fw / 2
        ly, ry = yat(lx), yat(rx)
        ang = math.degrees(math.atan2(ry - ly, rx - lx))
        tipy = (ly + ry) / 2 + flag_h
        c = colors[i % len(colors)]
        d = f"M {f1(lx)} {f1(ly)} L {f1(rx)} {f1(ry)} L {f1(cx + (ry - ly) * -0.4)} {f1(tipy)} Z"
        out.append(f'<path d="{d}" fill="#3A2418" opacity="0.15" transform="translate(2 3)"/>')
        out.append(wash(d, c[0], seed + i, 2, 0.5, 0.55, edge=c[1], edge_w=1.2))
        pat = i % 3
        cid = u("bt")
        if pat == 0:
            dots = "".join(f'<circle cx="{f1(lx + fw * fx)}" cy="{f1((ly + ry) / 2 + flag_h * fy)}" r="2.2" fill="#FFFFFF" opacity="0.8"/>' for fx, fy in ((0.25, 0.18), (0.5, 0.18), (0.75, 0.18), (0.38, 0.42), (0.62, 0.42), (0.5, 0.66)))
            out.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})">{dots}</g>')
        elif pat == 1:
            st = "".join(f'<path d="M {f1(lx - 20)} {f1((ly + ry) / 2 + k * 9)} L {f1(rx + 20)} {f1((ly + ry) / 2 + k * 9 - 14)}" stroke="#FFFFFF" stroke-width="2.6" opacity="0.55"/>' for k in range(1, 6))
            out.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})">{st}</g>')
        else:
            out.append(strokes(cid, d, (lx, min(ly, ry), rx, tipy), [c[1], "#FFFFFF"], seed + i, n=10, angle=80, length=(8, 18), width=(1, 2.2), opacity=(0.2, 0.45)))
        out.append(f'<path d="M {f1(lx)} {f1(ly)} L {f1(rx)} {f1(ry)}" stroke="{c[1]}" stroke-width="2.4" opacity="0.6"/>')
    return "".join(out)


def mortarboard(u, cx, cy, s, rot, seed, top="#20263A", top_l="#3A4466", band="#151A2A", tassel="#E2B04A", tassel_d="#A87A22"):
    out = [f'<g transform="rotate({rot} {f1(cx)} {f1(cy)})">']
    # skull cap
    cap = f"M {f1(cx - s * 0.5)} {f1(cy + s * 0.05)} L {f1(cx - s * 0.46)} {f1(cy + s * 0.42)} Q {f1(cx)} {f1(cy + s * 0.58)} {f1(cx + s * 0.46)} {f1(cy + s * 0.42)} L {f1(cx + s * 0.5)} {f1(cy + s * 0.05)} Z"
    out.append(f'<path d="{cap}" fill="#2A1A10" opacity="0.2" transform="translate(4 6)"/>')
    out.append(f'<path d="{cap}" fill="{band}"/>')
    out.append(f'<path d="M {f1(cx - s * 0.36)} {f1(cy + s * 0.12)} L {f1(cx - s * 0.33)} {f1(cy + s * 0.4)}" stroke="#4A5478" stroke-width="{f1(s * 0.05)}" stroke-linecap="round" opacity="0.6"/>')
    # board (rhombus seen at an angle)
    board = f"M {f1(cx)} {f1(cy - s * 0.42)} L {f1(cx + s * 1.0)} {f1(cy - s * 0.05)} L {f1(cx)} {f1(cy + s * 0.3)} L {f1(cx - s * 1.0)} {f1(cy - s * 0.05)} Z"
    g = u("mb")
    out.append(f'<defs>{lgrad(g, [(0, top_l), (0.5, top), (1, "#11151F")], 0, 0, 1, 1)}</defs>')
    out.append(f'<path d="{board}" fill="url(#{g})"/>')
    out.append(f'<path d="M {f1(cx - s * 1.0)} {f1(cy - s * 0.05)} L {f1(cx)} {f1(cy + s * 0.3)} L {f1(cx + s * 1.0)} {f1(cy - s * 0.05)} L {f1(cx + s * 1.0)} {f1(cy + s * 0.02)} L {f1(cx)} {f1(cy + s * 0.37)} L {f1(cx - s * 1.0)} {f1(cy + s * 0.02)} Z" fill="#0B0E16"/>')
    out.append(f'<path d="M {f1(cx - s * 0.9)} {f1(cy - s * 0.06)} L {f1(cx)} {f1(cy - s * 0.38)}" stroke="#7A86AA" stroke-width="{f1(max(1.4, s * 0.03))}" opacity="0.7" stroke-linecap="round"/>')
    # button + tassel cord falling over the right corner
    out.append(f'<ellipse cx="{f1(cx)}" cy="{f1(cy - s * 0.06)}" rx="{f1(s * 0.07)}" ry="{f1(s * 0.045)}" fill="{tassel}" stroke="{tassel_d}" stroke-width="1"/>')
    tx, ty = cx + s * 0.86, cy + s * 0.02
    out.append(f'<path d="M {f1(cx)} {f1(cy - s * 0.06)} Q {f1(cx + s * 0.5)} {f1(cy - s * 0.12)} {f1(tx)} {f1(ty)} L {f1(tx + s * 0.02)} {f1(ty + s * 0.42)}" stroke="{tassel}" stroke-width="{f1(max(2, s * 0.045))}" fill="none" stroke-linecap="round"/>')
    tb = ty + s * 0.42
    out.append(f'<rect x="{f1(tx - s * 0.05)}" y="{f1(tb - s * 0.02)}" width="{f1(s * 0.14)}" height="{f1(s * 0.07)}" rx="{f1(s * 0.02)}" fill="{tassel_d}"/>')
    for k in range(7):
        x = tx - s * 0.05 + k * s * 0.023
        out.append(f'<path d="M {f1(x)} {f1(tb + s * 0.04)} q {f1(s * 0.01 * (k - 3))} {f1(s * 0.14)} {f1(s * 0.015 * (k - 3))} {f1(s * 0.26)}" stroke="{tassel if k % 2 else "#F6D27A"}" stroke-width="{f1(max(1.2, s * 0.022))}" fill="none" stroke-linecap="round"/>')
    out.append("</g>")
    return "".join(out)


def gold_flake(u, cx, cy, s, seed, gid):
    rnd = random.Random(seed)
    n = rnd.randint(5, 8)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.25, 0.25)
        rr_ = s * rnd.uniform(0.45, 1.0)
        pts.append((cx + rr_ * math.cos(a), cy + rr_ * math.sin(a) * rnd.uniform(0.6, 1.0)))
    d = "M " + " L ".join(f"{f1(x)} {f1(y)}" for x, y in pts) + " Z"
    return (f'<path d="{d}" fill="url(#{gid})" stroke="#9C7430" stroke-width="{0.5 if s < 6 else 0.8}" stroke-opacity="0.6"/>'
            + (f'<path d="M {f1(pts[0][0])} {f1(pts[0][1])} L {f1(cx)} {f1(cy)}" stroke="#FFF2C4" stroke-width="0.8" opacity="0.6"/>' if s > 6 else ""))


def gold_leaf_patch(u, cx, cy, rx, ry, seed, gid, rot=0, flecks=14):
    """A torn sheet of gold leaf: ragged edge, fine crackle lines, a soft sheen and loose flecks around it."""
    rnd = random.Random(seed)
    n = 46
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + 0.18 * math.sin(3 * a + seed) + 0.1 * math.sin(7 * a + seed * 2) + rnd.uniform(-0.12, 0.12)
        if rnd.random() < 0.15:
            k *= rnd.uniform(0.7, 0.85)  # torn bites
        x, y = rx * k * math.cos(a), ry * k * math.sin(a)
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    d = "M " + " L ".join(f"{f1(x)} {f1(y)}" for x, y in pts) + " Z"
    cid = u("gp")
    out = [f'<path d="{d}" fill="#6A4A14" opacity="0.18" transform="translate(1.5 2)"/>', f'<path d="{d}" fill="url(#{gid})"/>']
    cr = []
    for _ in range(9):  # crackle: the wrinkles of beaten leaf
        x0, y0 = cx + rnd.uniform(-rx, rx), cy + rnd.uniform(-ry, ry)
        seg = [f"M {f1(x0)} {f1(y0)}"]
        for _ in range(4):
            x0 += rnd.uniform(-14, 14)
            y0 += rnd.uniform(-10, 10)
            seg.append(f"L {f1(x0)} {f1(y0)}")
        cr.append(f'<path d="{" ".join(seg)}" stroke="{rnd.choice(["#8A6420", "#FFF4CC"])}" stroke-width="0.8" fill="none" opacity="0.55"/>')
    out.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})">{"".join(cr)}'
               f'<ellipse cx="{f1(cx - rx * 0.3)}" cy="{f1(cy - ry * 0.35)}" rx="{f1(rx * 0.5)}" ry="{f1(ry * 0.22)}" fill="#FFF8DC" opacity="0.4" transform="rotate(-25 {f1(cx)} {f1(cy)})"/></g>')
    out.append(f'<path d="{d}" fill="none" stroke="#9C7430" stroke-width="0.7" opacity="0.6"/>')
    for i in range(flecks):
        a = rnd.uniform(0, 6.28)
        dist = rnd.uniform(1.0, 1.7)
        px, py = cx + math.cos(a) * rx * dist, cy + math.sin(a) * ry * dist
        out.append(gold_flake(u, px, py, rnd.uniform(1.6, 4.5), seed * 10 + i, gid))
    return "".join(out)


# ---------------------------------------------------------------- watercolour flowers (soft, translucent, layered)
def soft_petal(u, cx, cy, ang, r_in, r_out, width, base, tip, seed, op=0.92, edge=None, bumps=3):
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    L = r_out - r_in
    bx, by = cx + ux * r_in, cy + uy * r_in
    pts = [(bx - nx * width * 0.12, by - ny * width * 0.12)]
    for t, k in ((0.35, 0.36), (0.68, 0.5)):
        pts.append((bx + ux * L * t - nx * width * k, by + uy * L * t - ny * width * k))
    m = 2 * bumps + 1
    for j in range(m):  # rounded top with gentle scallops
        s = -0.46 + 0.92 * j / (m - 1)
        reach = math.sqrt(max(0.0, 1 - (s / 0.52) ** 2))
        dip = 1.0 if j % 2 == 0 else 0.955
        rr_ = L * (0.7 + 0.3 * reach) * dip * rnd.uniform(0.98, 1.02)
        pts.append((bx + ux * rr_ + nx * width * s, by + uy * rr_ + ny * width * s))
    for t, k in ((0.68, 0.5), (0.35, 0.36)):
        pts.append((bx + ux * L * t + nx * width * k, by + uy * L * t + ny * width * k))
    pts.append((bx + nx * width * 0.12, by + ny * width * 0.12))
    d = smooth_closed(pts)
    g = u("sp")
    out = [f'<defs>{lgrad(g, [(0, base), (1, tip)], bx, by, bx + ux * L, by + uy * L, user=True)}</defs>',
           f'<path d="{d}" fill="url(#{g})" opacity="{op}"/>']
    if edge:
        out.append(f'<path d="{d}" fill="none" stroke="{edge}" stroke-width="0.9" opacity="0.45"/>')
    # a few fine veins from the base
    for s in (-0.18, 0.0, 0.2):
        ex, ey = bx + ux * L * 0.75 + nx * width * s, by + uy * L * 0.75 + ny * width * s
        out.append(f'<path d="M {f1(bx)} {f1(by)} Q {f1(bx + ux * L * 0.4 + nx * width * s * 0.6)} {f1(by + uy * L * 0.4 + ny * width * s * 0.6)} {f1(ex)} {f1(ey)}" stroke="{base}" stroke-width="0.8" fill="none" opacity="0.35"/>')
    return "".join(out)


def crescent(cx, cy, R, a0, a1, thick, fill, line=None, op=1.0, sy=1.0):
    outer, inner = [], []
    for i in range(13):
        t = i / 12
        a = math.radians(a0 + (a1 - a0) * t)
        outer.append((cx + R * math.cos(a), cy + R * sy * math.sin(a)))
        ri = R - thick * math.sin(math.pi * t)
        inner.append((cx + ri * math.cos(a), cy + ri * sy * math.sin(a) + thick * 0.25 * math.sin(math.pi * t)))
    d = "M " + " L ".join(f"{f1(x)} {f1(y)}" for x, y in outer + list(reversed(inner))) + " Z"
    out = f'<path d="{d}" fill="{fill}" opacity="{op}"/>'
    if line:
        out += f'<path d="{smooth_open(outer)}" fill="none" stroke="{line}" stroke-width="1" opacity="0.55"/>'
    return out


def splash(u, cx, cy, r, color, seed, op=0.22):
    """Loose watercolour bloom behind a flower, with a few splatter dots."""
    rnd = random.Random(seed)
    out = [f'<path d="{blob(cx, cy, r, r * 0.85, seed, 0.16, 16)}" fill="{color}" opacity="{op}"/>',
           f'<path d="{blob(cx + r * 0.1, cy + r * 0.05, r * 0.8, r * 0.7, seed + 1, 0.2, 14)}" fill="{color}" opacity="{op * 0.7:.2f}"/>']
    for _ in range(9):
        a = rnd.uniform(0, 6.28)
        d = r * rnd.uniform(1.05, 1.5)
        out.append(f'<circle cx="{f1(cx + math.cos(a) * d)}" cy="{f1(cy + math.sin(a) * d)}" r="{rnd.uniform(1, 3):.1f}" fill="{color}" opacity="{op * 1.6:.2f}"/>')
    return "".join(out)


def peony2(u, cx, cy, r, seed, pal=("#C9567A", "#EE9AB0", "#FBD9E2", "#FFF4F6"), heart="#F2C14E"):
    dk, md, lt, wh = pal
    rnd = random.Random(seed)
    out = [splash(u, cx + 4, cy + 4, r * 1.15, md, seed)]
    for i in range(8):  # back ring
        a = i * 45 + rnd.uniform(-10, 10)
        out.append(soft_petal(u, cx, cy, a, r * 0.05, r * rnd.uniform(0.92, 1.04), r * 0.95, dk, md, seed + i, 0.9, dk))
    for i in range(7):  # middle ring, lighter
        a = i * 51 + 22 + rnd.uniform(-8, 8)
        out.append(soft_petal(u, cx, cy, a, r * 0.04, r * rnd.uniform(0.7, 0.8), r * 0.8, md, lt, seed + 10 + i, 0.88, dk))
    for i in range(6):  # inner ring
        a = i * 60 + 8 + rnd.uniform(-8, 8)
        out.append(soft_petal(u, cx, cy, a, r * 0.02, r * rnd.uniform(0.46, 0.54), r * 0.56, md, wh, seed + 20 + i, 0.9, dk, bumps=2))
    # cupped, crumpled centre petals
    for k, (rr_, a0, a1) in enumerate(((0.36, 200, 340), (0.32, 20, 160), (0.24, 240, 400), (0.2, 60, 200))):
        out.append(crescent(cx, cy + r * 0.03, r * rr_, a0, a1, r * 0.11, lt if k % 2 else wh, dk, 0.95))
    out.append(f'<path d="{blob(cx, cy, r * 0.13, r * 0.11, seed, 0.15)}" fill="{heart}"/>')
    for k in range(12):
        a = rnd.uniform(0, 6.28)
        d = rnd.uniform(r * 0.04, r * 0.16)
        out.append(f'<circle cx="{f1(cx + math.cos(a) * d)}" cy="{f1(cy + math.sin(a) * d)}" r="{rnd.uniform(1.1, 2):.1f}" fill="{rnd.choice(["#D9932E", "#B8741A", "#F6D27A"])}"/>')
    return "".join(out)


def rose2(u, cx, cy, r, seed, pal=("#B8405E", "#E27A92", "#F7C4CF", "#FFEFF2")):
    dk, md, lt, wh = pal
    rnd = random.Random(seed)
    out = [splash(u, cx + 3, cy + 3, r * 1.1, md, seed, 0.18)]
    for i in range(6):  # outer petals
        a = i * 60 + rnd.uniform(-12, 12)
        out.append(soft_petal(u, cx, cy, a, r * 0.2, r * rnd.uniform(0.95, 1.05), r * 1.05, dk, lt, seed + i, 0.92, dk, bumps=1))
    g = u("rc")
    out.append(f'<defs>{rgrad(g, [(0, dk), (0.7, md), (1, lt)], cx, cy - r * 0.1, r * 0.66, user=True)}</defs>'
               f'<path d="{blob(cx, cy, r * 0.62, r * 0.56, seed + 9, 0.05)}" fill="url(#{g})"/>')
    # the spiralling bud: nested crescents, alternating sides
    for k in range(5):
        rr_ = r * (0.56 - k * 0.1)
        a0 = (k * 150 + 190) % 360
        out.append(crescent(cx + (k % 2 - 0.5) * r * 0.04, cy + r * 0.02 * k, rr_, a0, a0 + 170, rr_ * 0.36, lt if k % 2 else wh, dk, 0.95, sy=0.88))
    out.append(f'<path d="{blob(cx, cy - r * 0.02, r * 0.08, r * 0.06, seed, 0.2)}" fill="{dk}"/>')
    # front lip curling toward us
    out.append(crescent(cx, cy + r * 0.05, r * 0.66, 20, 160, r * 0.2, lt, dk, 0.95, sy=0.85))
    return "".join(out)
