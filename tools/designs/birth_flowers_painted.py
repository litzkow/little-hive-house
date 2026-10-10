"""Birth Flowers, painted edition: watercolour / gouache botanical illustrations on warm paper.

  * 12 monthly specimens (same slugs as before): botanically drawn flower, buds, stems and leaves in layered
    washes with pooled edges, wet-in-wet blooms, granulation and fine sepia pen veins; month in Playfair
    italic, flower name small in Cinzel.
  * 12 birth-month bouquets: a lush wrapped bouquet of that month's flower, each with its own paper, ribbon,
    colour story and hand-lettered month.
  * 6 botanical gifts: grow with love, bloom where you are planted, lavender, sunflowers, peonies, wildflowers.

Run from tools/designs:  python3 birth_flowers_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_painted import Doc
from gouache import blob, blob_pts, grain, ink, jitter, paper, smooth_closed, smooth_open, strokes
from fall_gouache_a import catmull, label, letters, mix, pline, soft_glow, taper

COL = "birth-flowers"
SEPIA = "#4A3428"
PAPER = "#F7F0E2"
FLECK = "#8A6A4A"

GREENS = {
    "sage": ("#C9D4A4", "#83A062", "#3E5A30"),
    "blue": ("#C4D8CC", "#76A092", "#2E5A52"),     # glaucous: carnation, daffodil, poppy
    "leaf": ("#C4DC94", "#62A048", "#285A26"),     # fresh spring green
    "deep": ("#9CBC84", "#3E7448", "#173A24"),     # holly, lily-of-the-valley
    "olive": ("#D4D090", "#8E9C50", "#4A5626"),
    "fern": ("#B4D49C", "#5A9050", "#24502C"),
}

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


# ================================================================ geometry helpers
def bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def rot_pts(pts, ang, ox=0.0, oy=0.0):
    a = math.radians(ang)
    c, s = math.cos(a), math.sin(a)
    return [(ox + x * c - y * s, oy + x * s + y * c) for x, y in pts]


def face(pts, cx, cy, tilt=1.0, rot=0.0):
    """Map points in a flower's own flat plane (centre 0,0) to the page: foreshorten y by `tilt`, rotate."""
    return rot_pts([(x, y * tilt) for x, y in pts], rot, cx, cy)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def poly_d(pts):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def path_open(pts):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def bez(p0, p1, p2, n=12):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (i / n for i in range(n + 1))]


def along(pts, t):
    """Point and unit tangent at fraction t of a polyline."""
    segs = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
    tot = sum(segs) or 1
    goal = t * tot
    for i, L in enumerate(segs):
        if goal <= L or i == len(segs) - 1:
            k = goal / L if L else 0
            p = lerp(pts[i], pts[i + 1], min(1, k))
            dx, dy = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
            n = math.hypot(dx, dy) or 1
            return p, (dx / n, dy / n)
        goal -= L
    return pts[-1], (0, -1)


# ================================================================ watercolour painting
def pen(d, w=1.3, seed=1, op=0.7, color=SEPIA, broken=True):
    """Fine sepia pen line under the paint; broken into long dashes like a real nib lifting off the paper."""
    rnd = random.Random(seed)
    dash = ""
    if broken:
        seq = []
        for _ in range(8):
            seq += [rnd.uniform(40, 160), rnd.uniform(2, 9)]
        dash = f' stroke-dasharray="{" ".join(f"{v:.0f}" for v in seq)}" stroke-dashoffset="{rnd.uniform(0, 80):.0f}"'
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w:.2f}" stroke-linecap="round" stroke-linejoin="round" '
            f'opacity="{op:.2f}"{dash}/>')


def wc(D, pts, pal, seed, light=(-0.55, -0.83), grad=None, op=0.94, edge=0.62, edge_w=None, wet=2, gran=8, inkw=0.0,
       inkop=0.6, tex=0, tex_angle=-90, tex_len=None, band=0.16, half=None, d=None, accent=None, slip=0.012, edge_col=None):
    """One watercolour shape: a wash, a light-to-shadow glaze, wet-in-wet blooms, granulation, a darker pooled
    edge, optional dry-brush texture and an optional fine pen line. `grad` = (x0, y0, x1, y1) runs from the
    lit colour at (x0, y0) to the shadow colour at (x1, y1); otherwise it follows `light`."""
    lt, base, dk = pal
    given = d is not None
    d = d or smooth_closed(pts)
    x0, y0, x1, y1 = bbox(pts)
    W, H = x1 - x0, y1 - y0
    m = max(W, H, 1)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rnd = random.Random(seed)
    ew = edge_w or max(1.0, min(2.4, m * 0.02))
    pen_d = d
    if slip and not given:
        # the wash never sits exactly inside the pen line: shift and wobble it a hair
        sp = jitter(pts, seed + 11, m * slip)
        ox, oy = rnd.uniform(-1, 1) * m * slip, rnd.uniform(-1, 1) * m * slip
        d = smooth_closed([(x + ox, y + oy) for x, y in sp])
    out = [f'<path d="{d}" fill="{base}" opacity="{op}"/>']
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    if grad:
        gx0, gy0, gx1, gy1 = grad
    else:
        gx0, gy0, gx1, gy1 = cx + light[0] * m / 2, cy + light[1] * m / 2, cx - light[0] * m / 2, cy - light[1] * m / 2
    g = D.lin([(0, lt, 0.9), (0.45, base, 0), (1, dk, 0.72)], f"{gx0:.1f}", f"{gy0:.1f}", f"{gx1:.1f}", f"{gy1:.1f}", "userSpaceOnUse")
    inner.append(f'<path d="{d}" fill="{g}"/>')
    if half:
        inner.append(f'<path d="{smooth_closed(half)}" fill="{dk}" opacity="0.22"/>')
    if accent:
        bx, by = rnd.uniform(x0 + W * 0.2, x1 - W * 0.2), rnd.uniform(y0 + H * 0.2, y1 - H * 0.2)
        r = m * rnd.uniform(0.2, 0.32)
        bd = blob(bx, by, r, r * 0.7, rnd.randint(0, 9999), 0.22, 12, rnd.uniform(0, 180))
        inner.append(f'<path d="{bd}" fill="{accent}" opacity="0.22"/>')
    for _ in range(wet):
        c = rnd.choice([lt, dk, lt])
        bx, by = rnd.uniform(x0 + W * 0.15, x1 - W * 0.15), rnd.uniform(y0 + H * 0.15, y1 - H * 0.15)
        r = m * rnd.uniform(0.16, 0.3)
        bd = blob(bx, by, r, r * rnd.uniform(0.5, 0.9), rnd.randint(0, 9999), 0.2, 12, rnd.uniform(0, 180))
        o = rnd.uniform(0.16, 0.3)
        inner.append(f'<path d="{bd}" fill="{c}" opacity="{o:.2f}"/><path d="{bd}" fill="none" stroke="{c}" '
                     f'stroke-width="{max(0.7, ew * 0.55):.1f}" opacity="{min(0.6, o * 1.4):.2f}"/>')
    if tex:
        tl = tex_len or (m * 0.15, m * 0.45)
        inner.append(strokes(D.nid(), d, (x0 - 4, y0 - 4, x1 + 4, y1 + 4), [lt, dk, lt, base], seed + 7, n=tex, angle=tex_angle,
                             length=tl, width=(max(0.5, m * 0.008), max(1.0, m * 0.025)), opacity=(0.14, 0.38), curve=0.25))
    if band:
        inner.append(f'<path d="{d}" fill="none" stroke="{dk}" stroke-width="{ew * 3.6:.1f}" opacity="{band}"/>')
    for _ in range(gran):
        inner.append(f'<circle cx="{rnd.uniform(x0, x1):.1f}" cy="{rnd.uniform(y0, y1):.1f}" r="{rnd.uniform(0.4, 1.0):.1f}" '
                     f'fill="{dk}" opacity="{rnd.uniform(0.2, 0.45):.2f}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(f'<path d="{d}" fill="none" stroke="{edge_col or dk}" stroke-width="{ew:.2f}" stroke-opacity="{edge}" stroke-linejoin="round"/>')
    if inkw:
        out.append(pen(pen_d, inkw, seed + 3, inkop))
    return "".join(out)


def veins(lines, color, w=1.0, op=0.45):
    if not lines:
        return ""
    ds = "".join(f'<path d="{smooth_open(v)}"/>' for v in lines if len(v) > 1)
    return f'<g fill="none" stroke="{color}" stroke-width="{w:.2f}" stroke-linecap="round" opacity="{op:.2f}">{ds}</g>'


def wash_pts(cx, cy, rx, ry, seed, rough=1.0, n=64, rot=0):
    """Outline of a hand-laid wash: big lazy lobes plus small nibbles where the paint dried against the tooth."""
    rnd = random.Random(seed)
    p = [rnd.uniform(0, 6.28) for _ in range(4)]
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + rough * (0.1 * math.sin(2 * a + p[0]) + 0.07 * math.sin(3 * a + p[1]) + 0.035 * math.sin(7 * a + p[2])
                         + 0.018 * math.sin(13 * a + p[3]) + rnd.uniform(-0.012, 0.012))
        pts.append((rx * k * math.cos(a), ry * k * math.sin(a)))
    return rot_pts(pts, rot, cx, cy)


def splash(D, cx, cy, rx, ry, col, seed, op=0.22, edge=0.35, rough=1.0, col2=None, rot=0):
    """A loose background wash: two overlapping glazes, back-runs with dried rims, a darker pooled edge."""
    rnd = random.Random(seed)
    d = smooth_closed(wash_pts(cx, cy, rx, ry, seed, rough, rot=rot))
    out = [f'<path d="{d}" fill="{col}" opacity="{op}"/>']
    d2 = smooth_closed(wash_pts(cx + rnd.uniform(-0.15, 0.15) * rx, cy + rnd.uniform(-0.15, 0.15) * ry, rx * 0.7, ry * 0.66, seed + 1, rough * 1.4, rot=rot + 40))
    out.append(f'<path d="{d2}" fill="{col2 or col}" opacity="{op * 0.55:.3f}"/><path d="{d2}" fill="none" stroke="{col2 or col}" stroke-width="1.5" opacity="{op * 0.9:.3f}"/>')
    for i in range(3):
        bd = smooth_closed(wash_pts(cx + rnd.uniform(-0.55, 0.55) * rx, cy + rnd.uniform(-0.55, 0.55) * ry, rx * rnd.uniform(0.18, 0.32),
                                    ry * rnd.uniform(0.18, 0.32), seed * 7 + i, 1.8, 40))
        out.append(f'<path d="{bd}" fill="#FFFFFF" opacity="0.10"/><path d="{bd}" fill="none" stroke="{col}" stroke-width="1.3" opacity="{op * 1.1:.3f}"/>')
    out.append(spatter(seed + 3, (cx - rx, cy - ry, cx + rx, cy + ry), [col], 30, (0.4, 1.2), (op, op * 2.2)))
    out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="2.4" opacity="{edge}"/>')
    return "".join(out)


def spatter(seed, box, cols, n=18, r=(0.8, 3.2), op=(0.25, 0.6)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    return "".join(f'<circle cx="{rnd.uniform(x0, x1):.1f}" cy="{rnd.uniform(y0, y1):.1f}" r="{rnd.uniform(*r):.1f}" '
                   f'fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*op):.2f}"/>' for _ in range(n))


# ================================================================ petals and leaves (local frame: base at 0,0, axis +x)
def _profile(shape, t):
    if shape == "oval":
        return math.sin(math.pi * t) ** 0.7 * (1 + 0.15 * (t - 0.5))
    if shape == "obovate":
        return math.sin(math.pi * t ** 0.75) ** 0.75
    if shape == "spoon":
        return (min(1, t * 2.4) ** 0.6) * (1 - t ** 5) ** 0.5 * (0.45 + 0.55 * t)
    if shape == "strip":
        return min(1, t * 6) ** 0.5 * (1 - t ** 8) ** 0.5
    if shape == "wedge":
        return 0.12 + 0.88 * t ** 0.7
    if shape == "lance":
        return math.sin(math.pi * t ** 1.25) ** 0.9
    if shape == "ovate":
        return math.sin(math.pi * t ** 0.8) ** 0.85
    if shape == "fan":
        return 0.2 + 0.8 * math.sin(math.pi / 2 * min(1.0, t / 0.72)) ** 0.8
    if shape == "linear":
        return min(1, t * 8) ** 0.5 * (1 - t) ** 0.6
    if shape == "round":
        return math.sin(math.pi * t) ** 0.55
    return math.sin(math.pi * t)


def petal(L, W, shape="oval", tip="round", curl=0.0, n=14, teeth=3, depth=0.12, seed=0, wob=0.03, nveins=3, vlen=0.8,
          fringe=0.0, lobes=0, lobe_depth=0.0, lobe_kind="crenate"):
    """Petal or leaf outline in its own frame. Returns (outline, vein polylines, axis polyline).
    lobes: scalloped (crenate) or forward-pointing saw teeth (serrate) along both margins."""
    rnd = random.Random(seed)
    if lobes:
        n = max(n, lobes * 8)
    ts = [i / n for i in range(n + 1)]
    ws = [_profile(shape, t) for t in ts]
    mx = max(ws) or 1
    ws = [w / mx * W / 2 for w in ws]
    if lobes:
        ph = rnd.uniform(0, 0.3)
        for i, t in enumerate(ts):
            if 0.1 < t < 0.97:
                u = (t * lobes + ph) % 1
                if lobe_kind == "crenate":
                    k = 1 - abs(math.sin(math.pi * u)) ** 0.6
                elif lobe_kind == "spiny":
                    k = abs(math.sin(math.pi * u)) ** 0.7
                else:
                    k = u
                ws[i] *= 1 - lobe_depth * k

    def ax(t):
        return (L * t, curl * L * t * t)

    def nrm(t):
        dx, dy = L, 2 * curl * L * t
        k = math.hypot(dx, dy)
        return (-dy / k, dx / k)

    right, left = [], []
    for i, t in enumerate(ts):
        p, nv = ax(t), nrm(t)
        w = ws[i] * (1 + rnd.uniform(-wob, wob))
        if fringe and t > 0.45 and i % 2:
            w *= 1 + fringe
        w2 = w
        if lobes and 0.1 < t < 0.97 and lobe_kind == "serrate":
            # offset the left margin's teeth half a tooth so the two sides are not mirror images
            u = (t * lobes + 0.5) % 1
            w2 = ws[i] / max(0.05, 1 - lobe_depth * ((t * lobes) % 1)) * (1 - lobe_depth * u)
        right.append((p[0] + nv[0] * w, p[1] + nv[1] * w))
        left.append((p[0] - nv[0] * w2, p[1] - nv[1] * w2))
    wtip = ws[-1]
    cap = []
    tp, tn = ax(1), nrm(1)
    tg = (tn[1], -tn[0])
    if wtip > W * 0.06:
        if tip == "teeth" or tip == "fringe":
            k = teeth * 2 + 1
            for j in range(1, k):
                f = 1 - 2 * j / k
                out = (depth * W * (0.5 if j % 2 == 0 else -0.25)) * (1 + rnd.uniform(-0.3, 0.3))
                if tip == "fringe":
                    out = depth * W * (0.6 if j % 2 else -0.2) * (1 + rnd.uniform(-0.4, 0.4))
                bulge = W * 0.12 * (1 - f * f)
                cap.append((tp[0] + tn[0] * f * wtip + tg[0] * (out + bulge), tp[1] + tn[1] * f * wtip + tg[1] * (out + bulge)))
        else:
            for j in range(1, 6):
                a = math.pi / 2 - math.pi * j / 6
                cap.append((tp[0] + tn[0] * math.sin(a) * wtip + tg[0] * math.cos(a) * wtip * 0.75,
                            tp[1] + tn[1] * math.sin(a) * wtip + tg[1] * math.cos(a) * wtip * 0.75))
        outline = right + cap + left[::-1]
    else:
        outline = right[:-1] + [(tp[0] + tg[0] * 0.5, tp[1] + tg[1] * 0.5)] + left[:-1][::-1]
    vs = []
    for k in range(nveins):
        f = 0 if nveins == 1 else -0.6 + 1.2 * k / (nveins - 1)
        v = []
        for i, t in enumerate(ts):
            if 0.06 <= t <= vlen:
                p, nv = ax(t), nrm(t)
                v.append((p[0] + nv[0] * f * ws[i], p[1] + nv[1] * f * ws[i]))
        vs.append(v)
    axis = [ax(t) for t in ts]
    return outline, vs, axis


def place(pts, ang, ox, oy):
    return rot_pts(pts, ang, ox, oy)


def leaf(D, base, ang, L, W, pal, seed, shape="lance", curl=0.0, lobes=0, lobe_depth=0.0, lobe_kind="crenate", inkw=1.0,
         side_veins=4, fold=True, vein_col=None, op=0.95, mid_op=0.5, edge=0.6, accent=None, parallel=0):
    """A watercolour leaf whose stalk end sits at `base`, pointing along `ang` (degrees, 0 = right, -90 = up)."""
    if isinstance(pal, str):
        pal = GREENS[pal]
    lt, bs, dk = pal
    outline, pv, axis = petal(L, W, shape, "round", curl, 18, seed=seed, wob=0.02, nveins=parallel, vlen=0.94, lobes=lobes,
                              lobe_depth=lobe_depth, lobe_kind=lobe_kind)
    pts = place(outline, ang, *base)
    ax = place(axis, ang, *base)
    tipp = ax[-1]
    # one half in shadow (the leaf folds along its midrib)
    halfp = place([p for p in outline[: len(outline) // 2 + 1]] + axis[::-1], ang, *base) if fold else None
    out = [wc(D, pts, pal, seed, grad=(tipp[0], tipp[1], base[0], base[1]), half=halfp, op=op, wet=2, gran=4, inkw=inkw, inkop=0.5,
              edge=edge, band=0.12, accent=accent or ("#E8D86A" if seed % 2 else "#5E9AA0"))]
    vc = vein_col or mix(lt, "#FFFFFF", 0.3)
    if parallel:
        out.append(veins([place(v, ang, *base) for v in pv], dk, max(0.7, W * 0.012), 0.3))
        out.append(veins([place(v, ang, *base) for v in pv], vc, max(0.6, W * 0.01), 0.35))
    out.append(veins([ax[1:-2]], vc, max(0.9, W * 0.035), mid_op))
    if side_veins:
        sv = []
        for k in range(side_veins):
            t = 0.18 + 0.62 * k / max(1, side_veins - 1)
            p, tg = along(ax, t)
            nx, ny = -tg[1], tg[0]
            for sg in (-1, 1):
                L2 = W * 0.42 * math.sin(math.pi * min(0.95, t + 0.1)) ** 0.6
                q = (p[0] + tg[0] * L2 * 0.9 + sg * nx * L2, p[1] + tg[1] * L2 * 0.9 + sg * ny * L2)
                m = (p[0] + tg[0] * L2 * 0.2 + sg * nx * L2 * 0.6, p[1] + tg[1] * L2 * 0.2 + sg * ny * L2 * 0.6)
                sv.append(bez(p, m, q, 6))
        out.append(veins(sv, dk, max(0.7, W * 0.02), 0.35))
    return "".join(out)


def stem(pts, w0, w1, pal="sage", seed=1, inkw=0.9):
    """A painted stem: shadow side, body, a lit stripe and a faint pen line."""
    if isinstance(pal, str):
        pal = GREENS[pal]
    lt, bs, dk = pal
    c = catmull(pts, 8)
    out = [taper(c, w0, w1, dk, 0.95), taper([(x - 0.18 * w0, y) for x, y in c], w0 * 0.72, w1 * 0.72, bs, 0.95),
           taper([(x - 0.3 * w0, y) for x, y in c], max(0.8, w0 * 0.25), max(0.5, w1 * 0.25), lt, 0.7)]
    if inkw:
        out.append(pen(smooth_open([(x + w0 * 0.42, y) for x, y in pts]), inkw, seed, 0.4))
    return "".join(out)


# ================================================================ flower building blocks
def radial(D, cx, cy, R, n, pal, seed, tilt=1.0, rot=0.0, shape="strip", tip="round", W=0.2, r0=0.16, curl=0.0, ja=5,
           Lvar=0.08, nveins=2, vein_w=0.9, vein_op=0.4, inkw=0.8, a0=0.0, teeth=2, depth=0.14, layer_pals=None, edge=0.55,
           base_dark=True, wet=1, cup=0.0, edge_col=None, edge_w=None, band=0.1):
    """A ring of petals in the flower's own plane, foreshortened by `tilt` and turned by `rot`; far petals first."""
    rnd = random.Random(seed)
    items = []
    for i in range(n):
        a = a0 + i * 360 / n + rnd.uniform(-ja, ja)
        L = R * (1 - r0) * (1 + rnd.uniform(-Lvar, Lvar))
        o, vs, axis = petal(L, R * W * (1 + rnd.uniform(-0.1, 0.1)), shape, tip, curl * rnd.uniform(0.6, 1.4) * rnd.choice([-1, 1]),
                            14, teeth, depth, seed + i, 0.04, nveins)
        ra = math.radians(a)
        bx, by = R * r0 * math.cos(ra), R * r0 * math.sin(ra)
        # cupping: petal tips lift toward the viewer (pull them in a little on the far side)
        o = place(o, a, bx, by)
        vs = [place(v, a, bx, by) for v in vs]
        axis = place(axis, a, bx, by)
        if cup:
            o = [(x * (1 - cup * 0.25), y * (1 - cup * 0.25) - cup * R * 0.25 * (math.hypot(x, y) / R) ** 2) for x, y in o]
            vs = [[(x * (1 - cup * 0.25), y * (1 - cup * 0.25) - cup * R * 0.25 * (math.hypot(x, y) / R) ** 2) for x, y in v] for v in vs]
            axis = [(x * (1 - cup * 0.25), y * (1 - cup * 0.25) - cup * R * 0.25 * (math.hypot(x, y) / R) ** 2) for x, y in axis]
        items.append((math.sin(ra), o, vs, axis, i))
    items.sort(key=lambda it: it[0])
    out = []
    for depth_k, o, vs, axis, i in items:
        P = face(o, cx, cy, tilt, rot)
        V = [face(v, cx, cy, tilt, rot) for v in vs]
        A = face(axis, cx, cy, tilt, rot)
        pal_i = layer_pals[i % len(layer_pals)] if layer_pals else pal
        if base_dark == "tip":
            g = (A[0][0], A[0][1], A[-1][0], A[-1][1])
        else:
            g = (A[-1][0], A[-1][1], A[0][0], A[0][1]) if base_dark else None
        out.append(wc(D, P, pal_i, seed * 31 + i, grad=g, wet=wet, gran=3, inkw=inkw, inkop=0.5, edge=edge, band=band, edge_col=edge_col,
                      edge_w=edge_w))
        if nveins:
            out.append(veins(V, pal_i[2], vein_w, vein_op))
    return "".join(out)


def disc(D, cx, cy, r, pal, seed, tilt=1.0, rot=0.0, dots=90, dot_cols=None, dome=True, inkw=0.9, ring=None):
    """Composite-flower centre: a domed disc of florets (phyllotaxis dots), shaded away from the light."""
    pts = face(blob_pts(0, 0, r, r, seed, 0.03, 18), cx, cy, tilt, rot)
    lt, bs, dk = pal
    out = [wc(D, pts, pal, seed, wet=1, gran=6, inkw=inkw, inkop=0.6, band=0.2)]
    golden = math.pi * (3 - math.sqrt(5))
    cols = dot_cols or [dk, mix(dk, "#000000", 0.25), lt]
    ds = []
    for i in range(dots):
        rr = r * 0.92 * math.sqrt((i + 0.5) / dots)
        a = i * golden
        x, y = face([(rr * math.cos(a), rr * math.sin(a))], cx, cy, tilt, rot)[0]
        # dome: dots on the lower-right are in shadow
        shade = (rr * math.cos(a) * 0.55 + rr * math.sin(a) * 0.83) / r
        c = cols[0] if shade > 0.15 else (cols[2] if shade < -0.4 else cols[1 if i % 3 else 0])
        ds.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(0.7, r * 0.065 * (1.1 - 0.4 * rr / r)):.1f}" fill="{c}" opacity="0.8"/>')
    out.append("".join(ds))
    if dome:
        hl = face([(-r * 0.35, -r * 0.4)], cx, cy, tilt, rot)[0]
        out.append(f'<ellipse cx="{hl[0]:.1f}" cy="{hl[1]:.1f}" rx="{r * 0.32:.1f}" ry="{r * 0.2 * tilt:.1f}" fill="#FFFFFF" opacity="0.28" '
                   f'transform="rotate({rot - 30:.0f} {hl[0]:.1f} {hl[1]:.1f})"/>')
    if ring:
        out.append(f'<path d="{smooth_closed(face(blob_pts(0, 0, r * 1.08, r * 1.08, seed + 1, 0.03, 18), cx, cy, tilt, rot))}" fill="none" '
                   f'stroke="{ring}" stroke-width="{max(1, r * 0.12):.1f}" opacity="0.45"/>')
    return "".join(out)


# ================================================================ page furniture
def page(D, seed, base=PAPER, wash_col=None, wash=(300, 270, 230, 210), wash_op=0.2):
    out = [paper(D.nid(), base, FLECK, seed)]
    if wash_col:
        cx, cy, rx, ry = wash
        out.append(splash(D, cx, cy, rx, ry, wash_col, seed, wash_op, wash_op * 1.4))
    return out


def month_type(D, month, flower, ink_col, accent, y=498, size=70, sub_y=536, seed=1):
    """Month in Playfair italic with a soft painted shadow; flower name small in spaced Cinzel between pen dashes."""
    out = []
    fs = fit_size(month, SERIF_IT, size, 420)
    out.append(f'<text x="302" y="{y + 3}" text-anchor="middle" {SERIF_IT} font-size="{fs}" fill="{accent}" opacity="0.35">{esc(month)}</text>')
    out.append(f'<text x="300" y="{y}" text-anchor="middle" {SERIF_IT} font-size="{fs}" fill="{ink_col}">{esc(month)}</text>')
    s = flower.upper()
    ffs = fit_size(s, CINZEL, 19, 320, 5)
    w = measure(s, CINZEL, ffs, 5)
    out.append(label(300, sub_y, s, CINZEL, ffs, ink_col, 5, 320))
    mid = sub_y - ffs * 0.36
    for sg in (-1, 1):
        a = 300 + sg * (w / 2 + 14)
        b = 300 + sg * (w / 2 + 44)
        out.append(pline([(a, mid), ((a + b) / 2, mid + 1), (b, mid - 0.5)], accent, 1.8, seed + sg, 0.9, 1))
        out.append(f'<circle cx="{b + sg * 6:.1f}" cy="{mid:.1f}" r="2.4" fill="{accent}"/>')
    return "".join(out)


def tooth(D, seed, op=1.0):
    """Cold-press paper tooth laid over everything: tiny pale pits and darker grains."""
    rnd = random.Random(seed)
    el = []
    for _ in range(70):
        x, y = rnd.uniform(0, 70), rnd.uniform(0, 70)
        el.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(0.8, 2.6):.1f}" ry="{rnd.uniform(0.5, 1.6):.1f}" '
                  f'transform="rotate({rnd.uniform(0, 180):.0f} {x:.1f} {y:.1f})" fill="#FFFFFF" opacity="{rnd.uniform(0.05, 0.14):.2f}"/>')
    for _ in range(30):
        el.append(f'<circle cx="{rnd.uniform(0, 70):.1f}" cy="{rnd.uniform(0, 70):.1f}" r="{rnd.uniform(0.4, 1.1):.1f}" fill="#5A4030" '
                  f'opacity="{rnd.uniform(0.04, 0.1):.2f}"/>')
    i = D.nid()
    return (f'<defs><pattern id="{i}" width="70" height="70" patternUnits="userSpaceOnUse">{"".join(el)}</pattern></defs>'
            f'<rect width="600" height="600" fill="url(#{i})" opacity="{op}"/>')


def finish(D, out, seed, color=SEPIA, op=0.8):
    out.append(tooth(D, seed))
    out.append(grain(D.nid(), color, seed, op))
    return D.render(out)


# ================================================================ flowers
WHITE_P = ("#FFFFFF", "#FBF8F2", "#A9A6BE")
YELLOW_D = ("#FFE27A", "#F2B42A", "#B0640E")


def daisy_head(D, cx, cy, R, seed, tilt=1.0, rot=0.0, pal=WHITE_P, dpal=YELLOW_D, n=24, inkw=0.8):
    out = [radial(D, cx, cy, R, n, pal, seed, tilt, rot, shape="strip", tip="teeth", W=0.15, r0=0.2, curl=0.05, ja=3, Lvar=0.1,
                  nveins=2, vein_w=0.8, vein_op=0.3, inkw=inkw, teeth=1, depth=0.25, edge=0.7)]
    out.append(disc(D, cx, cy, R * 0.26, dpal, seed + 5, tilt, rot, dots=70))
    return "".join(out)


def daisy_bud(D, cx, cy, s, seed, ang=-90):
    out = []
    # green involucre cup with a white tip of rays peeking out
    cup = place([(-s * 0.5, -s * 0.15), (-s * 0.1, -s * 0.55), (s * 0.5, -s * 0.5), (s * 0.85, 0), (s * 0.5, s * 0.5), (-s * 0.1, s * 0.55), (-s * 0.5, s * 0.15)],
                ang, cx, cy)
    tipw = place([(s * 0.4, -s * 0.38), (s * 0.95, -s * 0.2), (s * 1.08, 0), (s * 0.95, s * 0.2), (s * 0.4, s * 0.38)], ang, cx, cy)
    out.append(wc(D, tipw, WHITE_P, seed, inkw=0.8, wet=0))
    out.append(wc(D, cup, GREENS["leaf"], seed + 1, inkw=0.9, wet=0))
    sep = [place([(-s * 0.2, k * s * 0.15), (s * 0.6, k * s * 0.2)], ang, cx, cy) for k in (-2, 0, 2)]
    out.append(veins(sep, GREENS["leaf"][2], 0.9, 0.5))
    return "".join(out)


# ================================================================ 04 April · Daisy
@design("april-daisy")
def april_daisy():
    D = Doc("bf-apr")
    out = page(D, 4, wash_col="#E8D27A", wash=(300, 260, 220, 200), wash_op=0.18)
    out.append(spatter(41, (90, 80, 510, 440), ["#E8C25A", "#9DBA6A"], 14))
    # three oxeye daisies on wiry stems from one base, with a bud and lobed basal leaves
    out.append(stem([(300, 440), (296, 360), (262, 250), (230, 176)], 6, 4.5, "leaf", 1))
    out.append(stem([(300, 440), (304, 360), (330, 270), (378, 214)], 6, 4.5, "leaf", 2))
    out.append(stem([(300, 440), (302, 380), (306, 300), (318, 150)], 6, 4, "leaf", 3))
    out.append(stem([(300, 440), (290, 380), (250, 330), (196, 300)], 5, 3.5, "leaf", 4))
    for i, (bx, by, a, L, W) in enumerate(((298, 430, -152, 96, 32), (302, 430, -26, 100, 32), (296, 404, -118, 74, 24), (305, 400, -64, 70, 22))):
        out.append(leaf(D, (bx, by), a, L, W, "leaf", 50 + i, "spoon", curl=0.08 * (1 if i % 2 else -1), lobes=6, lobe_depth=0.3, side_veins=3))
    out.append(leaf(D, (316, 300), -24, 50, 12, "leaf", 60, "linear", curl=0.1, lobes=5, lobe_depth=0.25, lobe_kind="serrate", side_veins=0))
    out.append(leaf(D, (280, 290), -164, 46, 11, "leaf", 61, "linear", curl=-0.1, lobes=5, lobe_depth=0.25, lobe_kind="serrate", side_veins=0))
    out.append(daisy_bud(D, 196, 300, 16, 70, -150))
    out.append(daisy_head(D, 378, 214, 64, 7, tilt=0.62, rot=-28))
    out.append(daisy_head(D, 230, 176, 70, 8, tilt=0.8, rot=22))
    out.append(daisy_head(D, 318, 140, 74, 9, tilt=0.95, rot=0))
    out.append(month_type(D, "April", "Daisy", "#3E4A2A", "#C9A62E", seed=4))
    return finish(D, out, 4)


# ================================================================ shared shape helpers
def hull(pts):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def scallop(pts, n, depth, phase=0.0, skip=0.06):
    """Push a closed outline's margin into n rounded scallops (crenate edge); `skip` leaves the stalk end alone."""
    N = len(pts)
    out = []
    for i, (x, y) in enumerate(pts):
        u = i / N
        if u < skip or u > 1 - skip:
            out.append((x, y))
            continue
        a, b = pts[i - 1], pts[(i + 1) % N]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = dy / L, -dx / L
        k = abs(math.sin(math.pi * (u * n + phase))) ** 0.5
        out.append((x + nx * depth * (k - 0.6), y + ny * depth * (k - 0.6)))
    return out


def local(pts, base, ang):
    """Points given in an object's own frame (axis +x) -> page."""
    return rot_pts(pts, ang, base[0], base[1])


def hairs(pts, seed, color, n=30, L=3.0, w=0.8, op=0.6, every=1):
    """Fine bristles along an outline (poppy stems and buds)."""
    rnd = random.Random(seed)
    out = []
    N = len(pts)
    for _ in range(n):
        i = rnd.randrange(N)
        a, b = pts[i], pts[(i + 1) % N]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = dy / l, -dx / l
        ll = L * rnd.uniform(0.6, 1.3)
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} l {nx * ll + dx / l * ll * 0.5:.1f} {ny * ll + dy / l * ll * 0.5:.1f}"/>')
    return f'<g stroke="{color}" stroke-width="{w}" stroke-linecap="round" opacity="{op}">{"".join(out)}</g>'


def node(x, y, r, pal="blue"):
    lt, bs, dk = GREENS[pal] if isinstance(pal, str) else pal
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 1.15:.1f}" ry="{r * 0.8:.1f}" fill="{bs}" stroke="{dk}" stroke-width="1" stroke-opacity="0.6"/>'


# ================================================================ 01 January · Carnation
CARN = ("#FFF4F4", "#F9CDD6", "#E27E9A")     # blush pink ...
PICOTEE = "#B8143E"                            # ... with a crimson picotee rim


def carn_petal_fan(D, x, y, ang, s, seed, pal, layers=((7, 75, 0.74, 0.56, 0.0), (6, 58, 0.62, 0.5, 0.04), (5, 42, 0.46, 0.44, 0.1))):
    """Ruffled carnation head in side view: fringed, fan-shaped petals bursting from the calyx mouth at (x, y)."""
    rnd = random.Random(seed)
    out = []
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    for k, (n, spread, Lk, Wk, back) in enumerate(layers):
        for i in range(n):
            off = -spread + 2 * spread * i / max(1, n - 1) + rnd.uniform(-6, 6)
            L = s * Lk * rnd.uniform(0.9, 1.08) * (1 - 0.18 * abs(off) / 90)
            o, vs, axis = petal(L, s * Wk * rnd.uniform(0.85, 1.1), "wedge", "fringe", 0.18 * (1 if off > 0 else -1) * abs(off) / 70,
                                12, 5, 0.2, seed + k * 20 + i, 0.05, 4, 0.7, fringe=0.06)
            ox, oy = x - ux * s * back, y - uy * s * back
            P, V, A = local(o, (ox, oy), ang + off), [local(v, (ox, oy), ang + off) for v in vs], local(axis, (ox, oy), ang + off)
            out.append(wc(D, P, pal, seed * 7 + k * 20 + i, grad=(A[0][0], A[0][1], A[-1][0], A[-1][1]), wet=1, gran=2, inkw=0.6,
                          inkop=0.45, edge=0.95, edge_w=2.0, band=0.3, edge_col=PICOTEE))
            out.append(veins(V, pal[2], 0.7, 0.3))
    return "".join(out)


def carn_calyx(D, x, y, ang, s, seed, tip=None):
    """Calyx tube (top at x, y, pointing along ang) with five teeth and the small scale-like bracts at its foot."""
    cl, cw = s * 0.62, s * 0.13
    teeth = [(cl * 1.0, -cw * 1.0), (cl * 1.12, -cw * 0.8), (cl * 1.0, -cw * 0.45), (cl * 1.13, -cw * 0.1), (cl * 1.0, cw * 0.25),
             (cl * 1.12, cw * 0.62), (cl * 0.99, cw * 1.0)]
    loc = [(0, -cw * 0.62), (cl * 0.5, -cw * 0.84)] + teeth + [(cl * 0.5, cw * 0.84), (0, cw * 0.62)]
    base = (x - math.cos(math.radians(ang)) * cl, y - math.sin(math.radians(ang)) * cl)
    out = []
    if tip:
        tp = [(cl * 0.9, -cw * 0.75), (cl * 1.25, -cw * 0.75), (cl * 1.45, -cw * 0.2), (cl * 1.5, cw * 0.15), (cl * 1.3, cw * 0.7), (cl * 0.9, cw * 0.75)]
        out.append(wc(D, local(tp, base, ang), tip, seed + 5, inkw=0.7, wet=0, edge=0.9))
    out.append(wc(D, local(loc, base, ang), GREENS["blue"], seed, inkw=0.9, wet=1, edge=0.6))
    ribs = [local([(cl * 0.1, f * cw * 0.7), (cl * 0.6, f * cw * 0.8), (cl * 0.97, f * cw * 0.85)], base, ang) for f in (-0.5, 0.05, 0.55)]
    out.append(veins(ribs, GREENS["blue"][2], 0.8, 0.35))
    for sg in (-1, 1):
        br = [(0, sg * cw * 0.2), (cl * 0.1, sg * cw * 0.9), (cl * 0.3, sg * cw * 0.55)]
        out.append(wc(D, local(br + [(cl * 0.05, sg * cw * 0.1)], base, ang), GREENS["sage"], seed + sg, inkw=0.7, wet=0, gran=0))
    return "".join(out), base


def carnation_side(D, x, y, ang, s, seed, pal=CARN):
    """Side view: calyx with its teeth, the ruffled head bursting out of it."""
    cal, base = carn_calyx(D, x, y, ang, s, seed)
    head = carn_petal_fan(D, x, y, ang, s, seed + 3, pal)
    # the front teeth of the calyx overlap the lowest petals
    return cal + head, base


def carnation_front(D, cx, cy, R, seed, tilt=0.75, rot=0.0, pal=CARN):
    """Three-quarter view: four rings of fringed petals, each ring a little higher and more cupped (a ruffled dome)."""
    out = []
    for k, (rr, n, a0, W) in enumerate(((1.0, 11, 0, 0.62), (0.8, 10, 17, 0.6), (0.6, 8, 7, 0.6), (0.38, 6, 33, 0.66))):
        out.append(radial(D, cx, cy - k * R * 0.08, R * rr, n, pal, seed + k * 20, tilt, rot, shape="wedge", tip="fringe", W=W, r0=0.04,
                          curl=0.14, ja=9, Lvar=0.12, nveins=4, vein_w=0.7, vein_op=0.3, inkw=0.6, teeth=5, depth=0.22, edge=0.95,
                          base_dark="tip", cup=0.35 * k, a0=a0, edge_col=PICOTEE, edge_w=2.0, band=0.3))
    return "".join(out)


def linear_pair(D, x, y, ang, L, W, pal, seed, spread=38, droop=0.12):
    """A pair of narrow opposite leaves clasping a stem node."""
    return (leaf(D, (x, y), ang - spread, L, W, pal, seed, "linear", curl=-droop, side_veins=0, inkw=0.8, mid_op=0.45)
            + leaf(D, (x, y), ang + spread, L * 0.92, W, pal, seed + 1, "linear", curl=droop, side_veins=0, inkw=0.8, mid_op=0.45))


@design("january-carnation")
def january_carnation():
    D = Doc("bf-jan")
    out = page(D, 1, wash_col="#EBA2B6", wash=(300, 250, 225, 205), wash_op=0.16)
    out.append(spatter(11, (90, 70, 510, 440), ["#E8879F", "#B9CBBE"], 16))
    # stems
    s1 = [(300, 448), (296, 390), (312, 320), (330, 262)]
    s2 = [(300, 448), (292, 400), (258, 336), (220, 290)]
    s3 = [(304, 392), (330, 356), (372, 322), (404, 306)]
    out.append(stem(s1, 7, 5.5, "blue", 1) + stem(s2, 6, 5, "blue", 2) + stem(s3, 4.5, 4, "blue", 3))
    out.append(linear_pair(D, 297, 396, -90, 100, 15, "blue", 20, 52, 0.16))
    out.append(linear_pair(D, 309, 334, -80, 82, 13, "blue", 22, 46, 0.14))
    out.append(linear_pair(D, 268, 350, -124, 70, 12, "blue", 24, 42))
    out.append(linear_pair(D, 352, 336, -38, 54, 10, "blue", 26, 40))
    for x, y in ((297, 396), (309, 334), (268, 350), (352, 336)):
        out.append(node(x, y, 4.6))
    # a bud just showing colour, a side-view bloom and the big ruffled bloom facing us
    cal, _ = carn_calyx(D, 428, 290, -42, 56, 30, tip=CARN)
    out.append(cal)
    sv, _ = carnation_side(D, 206, 262, -114, 108, 40)
    out.append(sv)
    out.append(carn_calyx(D, 330, 250, -88, 74, 50)[0])
    out.append(carnation_front(D, 332, 190, 104, 60, tilt=0.72, rot=-4))
    out.append(month_type(D, "January", "Carnation", "#5A1E32", "#D8708E", seed=1))
    return finish(D, out, 1)


# ================================================================ 02 February · Violet
VIOLET = ("#D6C2F6", "#8A5ACC", "#3C1A7A")


def violet_flower(D, cx, cy, s, seed, tilt=1.0, rot=0.0, pal=VIOLET):
    """Viola odorata: two upper petals behind, two bearded laterals, a broad lower petal with dark guide lines."""
    out = []
    specs = [(-114, 1.0, 1.0, "u"), (-66, 1.0, 1.0, "u"), (-162, 0.86, 0.78, "l"), (-18, 0.86, 0.78, "l"), (90, 0.96, 0.98, "b")]
    for k, (a, L, W, kind) in enumerate(specs):
        o, vs, axis = petal(s * L, s * W, "round", "round", 0.06 * (1 if k % 2 else -1), 14, seed=seed + k, nveins=0)
        P = face(local(o, (0, 0), a), cx, cy, tilt, rot)
        A = face(local(axis, (0, 0), a), cx, cy, tilt, rot)
        out.append(wc(D, P, pal, seed * 5 + k, grad=(A[-1][0], A[-1][1], A[2][0], A[2][1]), wet=1, gran=4, inkw=0.8, inkop=0.5,
                      edge=0.7, band=0.18))
        if kind == "b":
            # pale throat and the dark nectar guides
            th = face(local(blob_pts(s * 0.2, 0, s * 0.2, s * 0.17, seed, 0.1, 12), (0, 0), a), cx, cy, tilt, rot)
            out.append(f'<path d="{smooth_closed(th)}" fill="#FFFFFF" opacity="0.85"/><path d="{smooth_closed(th)}" fill="#F0E66A" opacity="0.25"/>')
            g = [face(local([(s * 0.06, f * s * 0.05), (s * 0.3, f * s * 0.14), (s * 0.55, f * s * 0.2)], (0, 0), a), cx, cy, tilt, rot)
                 for f in (-1.6, -0.8, 0, 0.8, 1.6)]
            out.append(veins(g, "#2A0A5A", 1.0, 0.75))
        elif kind == "l":
            th = face(local(blob_pts(s * 0.14, 0, s * 0.13, s * 0.1, seed + k, 0.1, 10), (0, 0), a), cx, cy, tilt, rot)
            out.append(f'<path d="{smooth_closed(th)}" fill="#FFFFFF" opacity="0.7"/>')
            hb = [face(local([(s * 0.04, f * s * 0.03), (s * 0.2, f * s * 0.07)], (0, 0), a), cx, cy, tilt, rot) for f in (-1, 0, 1)]
            out.append(veins(hb, "#FFFFFF", 1.2, 0.9) + veins([face(local([(s * 0.1, f * s * 0.05), (s * 0.4, f * s * 0.1)], (0, 0), a), cx, cy, tilt, rot)
                                                              for f in (-1, 1)], "#2A0A5A", 0.8, 0.5))
    c = face([(0, s * 0.02)], cx, cy, tilt, rot)[0]
    out.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{s * 0.07:.1f}" fill="#F2C832"/><circle cx="{c[0] - s * 0.02:.1f}" cy="{c[1] - s * 0.02:.1f}" r="{s * 0.025:.1f}" fill="#FFFFFF"/>')
    return "".join(out)


def violet_bud(D, x, y, ang, s, seed, pal=VIOLET):
    """Nodding bud: a twisted violet teardrop hanging from the crook of its stalk, green sepals at the top."""
    bud = local([(0, -s * 0.18), (s * 0.4, -s * 0.3), (s * 0.85, -s * 0.18), (s * 1.05, 0), (s * 0.85, s * 0.16), (s * 0.4, s * 0.28), (0, s * 0.18)], (x, y), ang)
    out = [wc(D, bud, pal, seed, wet=1, inkw=0.8)]
    out.append(veins([local([(s * 0.1, 0), (s * 0.5, s * 0.05), (s * 0.95, -s * 0.02)], (x, y), ang)], pal[2], 0.9, 0.5))
    for sg in (-1, 1):
        sp = local([(-s * 0.05, 0), (s * 0.2, sg * s * 0.22), (s * 0.45, sg * s * 0.14), (s * 0.12, sg * s * 0.02)], (x, y), ang)
        out.append(wc(D, sp, GREENS["leaf"], seed + sg, inkw=0.7, wet=0, gran=0))
    return "".join(out)


def heart_leaf(D, attach, ang, L, W, pal, seed, scallops=11, depth=None, inkw=0.9, accent=None):
    """Cordate leaf with a crenate margin and palmate veins; `attach` is where the petiole meets the blade."""
    if isinstance(pal, str):
        pal = GREENS[pal]
    right = catmull([(0, 0), (-0.12 * L, 0.18 * W), (-0.04 * L, 0.42 * W), (0.25 * L, 0.52 * W), (0.62 * L, 0.38 * W), (0.88 * L, 0.14 * W), (L, 0)], 6)
    left = [(x, -y) for x, y in right[::-1]][1:-1]
    loc = right + left
    loc = scallop(loc, scallops, depth if depth is not None else W * 0.025, 0.0, 0.03)
    P = local(loc, attach, ang)
    tip = local([(L, 0)], attach, ang)[0]
    halfp = local(right + [(L * 0.5, 0)], attach, ang)
    out = [wc(D, P, pal, seed, grad=(tip[0], tip[1], attach[0], attach[1]), half=halfp, wet=2, gran=5, inkw=inkw, inkop=0.5, edge=0.55,
              accent=accent or "#D8D86A")]
    vs = [local([(0, 0), (0.45 * L, 0.01 * W), (0.92 * L, 0)], attach, ang)]
    for sg in (-1, 1):
        for (a1, a2, a3) in (((0.02, 0.1), (0.12, 0.3), (0.32, 0.4)), ((0.06, 0.04), (0.3, 0.2), (0.55, 0.28)), ((0.25, 0.01), (0.5, 0.12), (0.72, 0.18))):
            vs.append(local([(a1[0] * L, sg * a1[1] * W), (a2[0] * L, sg * a2[1] * W), (a3[0] * L, sg * a3[1] * W)], attach, ang))
    out.append(veins(vs[:1], mix(pal[0], "#FFFFFF", 0.3), max(0.9, W * 0.02), 0.6) + veins(vs[1:], pal[2], 0.8, 0.4))
    return "".join(out)


@design("february-violet")
def february_violet():
    D = Doc("bf-feb")
    out = page(D, 2, wash_col="#B49ADC", wash=(300, 255, 228, 205), wash_op=0.17)
    out.append(spatter(21, (90, 70, 510, 440), ["#9A7AD0", "#9DBA6A"], 16))
    root = (300, 446)
    # flower stalks with the characteristic crook just below each flower
    fl = [((200, 200), 48, 0.92, 14), ((300, 142), 54, 0.98, -4), ((402, 196), 50, 0.88, -18), ((338, 268), 42, 0.8, 24)]
    stalks = [[root, (286, 360), (226, 268), (204, 214)], [root, (300, 330), (304, 214), (298, 158)],
              [root, (312, 360), (380, 270), (398, 210)], [root, (306, 380), (336, 320), (342, 280)]]
    buds = [((150, 270), [root, (270, 390), (180, 300), (160, 262)], 100), ((452, 268), [root, (330, 400), (420, 320), (446, 262)], 80)]
    for sp in stalks + [b[1] for b in buds]:
        out.append(stem(sp, 3.4, 2.6, "leaf", len(sp)))
    # heart-shaped leaves on their own petioles, a rosette around the root
    lv = [((222, 400), -160, 80, 72, 1), ((380, 402), -20, 80, 72, 2), ((258, 368), -128, 68, 62, 3), ((344, 364), -52, 70, 62, 4),
          ((300, 380), -92, 60, 54, 5), ((178, 424), 172, 54, 48, 6), ((422, 424), 8, 54, 48, 7)]
    for (ax, ay), a, L, W, k in lv:
        out.append(stem([root, ((root[0] + ax) / 2, (root[1] + ay) / 2 + 6), (ax, ay)], 3, 2.4, "leaf", 40 + k, 0))
    for (ax, ay), a, L, W, k in lv:
        out.append(heart_leaf(D, (ax, ay), a, L, W, "leaf", 40 + k, scallops=13, depth=W * 0.035))
    for (x, y), sp, a in buds:
        out.append(violet_bud(D, x, y + 2, a, 34, len(sp) + x))
    for (x, y), s, t, r in fl:
        out.append(violet_flower(D, x, y, s, int(x), t, r))
    out.append(month_type(D, "February", "Violet", "#3A1E66", "#9A7AD0", seed=2))
    return finish(D, out, 2)


# ================================================================ 03 March · Daffodil
DAFF_T = ("#FFFBD8", "#F9E27A", "#C79A1E")
DAFF_C = ("#FFDC78", "#F5A51E", "#B0520A")


def daffodil(D, cx, cy, s, seed, tilt=0.6, rot=0.0, trumpet=0.5, pal=DAFF_T, cpal=DAFF_C, neck=True):
    """Narcissus: six pointed tepals in the flower's plane and a frilled trumpet along its axis (toward the viewer)."""
    out = []
    face_up = math.sqrt(max(0.0, 1 - tilt * tilt))
    r = math.radians(rot)
    ux, uy = -math.sin(r), math.cos(r)            # plane's local +y on the page
    tl = s * trumpet * face_up
    mx, my = cx + ux * tl, cy + uy * tl           # trumpet mouth centre
    if neck:
        # green ovary and the papery spathe behind the flower
        bx, by = cx - ux * s * 0.42, cy - uy * s * 0.42
        ov = blob_pts(bx, by, s * 0.1, s * 0.16, seed, 0.05, 12, math.degrees(math.atan2(uy, ux)) + 90)
        out.append(wc(D, ov, GREENS["leaf"], seed + 1, inkw=0.8, wet=0))
    out.append(radial(D, cx, cy, s, 6, pal, seed, tilt, rot, shape="ovate", tip="round", W=0.46, r0=0.06, curl=0.04, ja=5, Lvar=0.06,
                      nveins=3, vein_w=0.8, vein_op=0.28, inkw=0.8, a0=-90 + 30 * (seed % 2), edge=0.6))
    rb, rr = s * 0.15, s * 0.25
    base_e = face(blob_pts(0, 0, rb, rb, seed, 0.02, 24), cx, cy, tilt, rot)
    rnd = random.Random(seed)
    mouth_l = []
    for i in range(60):
        a = 2 * math.pi * i / 60
        k = 1 + 0.07 * math.sin(14 * a + rnd.uniform(-0.2, 0.2)) + 0.03 * math.sin(5 * a)
        mouth_l.append((rr * k * math.cos(a), rr * k * math.sin(a)))
    mouth = face(mouth_l, mx, my, tilt, rot)
    body = hull(base_e + mouth)
    out.append(wc(D, body, cpal, seed + 2, light=(-0.8, -0.5), wet=1, gran=4, inkw=0.9, inkop=0.5, edge=0.6))
    # ribs along the trumpet
    rib = []
    for k in range(7):
        a = math.pi * (0.15 + 0.7 * k / 6)
        p0 = face([(rb * math.cos(a), rb * math.sin(a))], cx, cy, tilt, rot)[0]
        p1 = face([(rr * math.cos(a), rr * math.sin(a))], mx, my, tilt, rot)[0]
        rib.append([p0, lerp(p0, p1, 0.5), p1])
    out.append(veins(rib, cpal[2], 0.8, 0.3))
    # the open mouth: frilled rim, a shadowed throat, stamens
    out.append(wc(D, mouth, (cpal[0], mix(cpal[0], cpal[1], 0.5), cpal[2]), seed + 3, wet=1, gran=2, inkw=1.0, inkop=0.6, edge=0.8, band=0.25))
    if face_up > 0.2:
        throat = face(blob_pts(0, 0, rr * 0.66, rr * 0.62, seed + 4, 0.05, 16), mx - ux * tl * 0.25, my - uy * tl * 0.25, tilt, rot)
        out.append(f'<path d="{smooth_closed(throat)}" fill="{cpal[2]}" opacity="0.55"/>')
        for k in range(3):
            p = face([((k - 1) * rr * 0.18, -rr * 0.1)], mx - ux * tl * 0.1, my - uy * tl * 0.1, tilt, rot)[0]
            out.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{s * 0.025:.1f}" fill="#FFF2A0"/>')
    return "".join(out), (cx - ux * s * 0.42, cy - uy * s * 0.42)


def spathe(D, x, y, ang, s, seed):
    """Papery, parchment-coloured bract where the daffodil neck meets the stem."""
    pts = local([(0, -s * 0.12), (s * 0.5, -s * 0.18), (s * 1.0, -s * 0.05), (s * 1.15, s * 0.04), (s * 0.5, s * 0.16), (0, s * 0.12)], (x, y), ang)
    return wc(D, pts, ("#F6ECD0", "#D8C08A", "#8A6A3A"), seed, inkw=0.8, wet=1, tex=10, tex_angle=ang, edge=0.7)


def strap(D, base, pts, w, pal, seed, twist=None):
    """Long flat strap leaf (daffodil, tulip): a tapered ribbon along `pts` with a pale midline."""
    if isinstance(pal, str):
        pal = GREENS[pal]
    c = catmull([base] + pts, 8)
    n = len(c)
    left, right = [], []
    for i, (x, y) in enumerate(c):
        a, b = c[max(0, i - 1)], c[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        t = i / (n - 1)
        ww = w * (1 - t ** 3) * (0.8 + 0.2 * math.sin(math.pi * t)) / 2
        left.append((x + nx * ww, y + ny * ww))
        right.append((x - nx * ww, y - ny * ww))
    outline = left + right[::-1]
    half = left + c[::-1]
    out = [wc(D, outline, pal, seed, grad=(c[-1][0], c[-1][1], c[0][0], c[0][1]), half=half, wet=2, gran=6, inkw=0.9, inkop=0.5,
              accent="#D8E08A", slip=0.004)]
    out.append(veins([c[2:-3]], mix(pal[0], "#FFFFFF", 0.3), max(0.8, w * 0.06), 0.45))
    return "".join(out)


@design("march-daffodil")
def march_daffodil():
    D = Doc("bf-mar")
    out = page(D, 3, wash_col="#F2D25A", wash=(300, 250, 228, 205), wash_op=0.17)
    out.append(spatter(31, (90, 70, 510, 440), ["#E8B82A", "#9DBA6A"], 16))
    # leaves behind
    out.append(strap(D, (288, 450), [(272, 380), (240, 300), (200, 262)], 24, "blue", 1))
    out.append(strap(D, (314, 450), [(328, 380), (372, 310), (430, 284)], 23, "blue", 2))
    # flowers first (to learn where their necks are), then stems that arch over and dip into each neck
    fa, na = daffodil(D, 200, 240, 96, 10, tilt=0.66, rot=56)
    fb, nb = daffodil(D, 408, 200, 90, 11, tilt=0.6, rot=-42)
    out.append(stem([(298, 450), (292, 360), (262, 240), (na[0] + 10, na[1] - 22), na], 8, 6.5, "blue", 3))
    out.append(stem([(306, 450), (316, 350), (346, 220), (nb[0] - 12, nb[1] - 24), nb], 8, 6.5, "blue", 4))
    out.append(stem([(302, 450), (302, 340), (304, 230), (306, 150)], 7, 5.5, "blue", 5))
    out.append(spathe(D, na[0] + 8, na[1] - 20, -130, 38, 6) + spathe(D, nb[0] - 10, nb[1] - 22, -64, 36, 7))
    # a closed bud in its papery sheath
    bud = local([(0, -9), (26, -12), (54, -6), (70, 0), (54, 6), (26, 11), (0, 9)], (306, 150), -92)
    out.append(wc(D, bud, ("#FFF4A8", "#E8D45A", "#9A8A2A"), 8, inkw=0.9, wet=1))
    out.append(veins([local([(6, 0), (36, 1), (64, 0)], (306, 150), -92)], "#9A8A2A", 0.8, 0.5))
    out.append(spathe(D, 306, 160, -90, 44, 9))
    out.append(fa + fb)
    out.append(strap(D, (300, 450), [(302, 390), (276, 330), (246, 318)], 20, "blue", 12))
    out.append(strap(D, (304, 450), [(304, 396), (340, 344), (378, 336)], 19, "blue", 13))
    out.append(month_type(D, "March", "Daffodil", "#5A4210", "#E2A92A", seed=3))
    return finish(D, out, 3)


# ================================================================ 05 May · Lily of the Valley
BELL = ("#FFFFFF", "#FAFBF4", "#9DB2A2")


def bell(D, x, y, ang, s, seed, pal=BELL, bud=False):
    """A hanging lily-of-the-valley bell attached at (x, y), mouth along `ang`, with six little recurved lobes."""
    if bud:
        pts = local([(0, -0.1 * s), (0.25 * s, -0.42 * s), (0.7 * s, -0.42 * s), (0.95 * s, -0.1 * s), (0.95 * s, 0.1 * s), (0.7 * s, 0.42 * s),
                     (0.25 * s, 0.42 * s), (0, 0.1 * s)], (x, y), ang)
        return wc(D, pts, ("#F4FAE8", "#D8E8C0", "#7E9A6A"), seed, inkw=0.8, wet=0, gran=2, edge=0.7)
    loc = [(0, 0.12 * s), (0.12 * s, 0.36 * s), (0.36 * s, 0.5 * s), (0.66 * s, 0.5 * s), (0.86 * s, 0.46 * s), (0.9 * s, 0.66 * s),
           (0.98 * s, 0.38 * s), (1.07 * s, 0.17 * s), (1.0 * s, -0.03 * s), (1.07 * s, -0.24 * s), (0.98 * s, -0.43 * s), (0.9 * s, -0.66 * s),
           (0.86 * s, -0.46 * s), (0.66 * s, -0.5 * s), (0.36 * s, -0.5 * s), (0.12 * s, -0.36 * s), (0, -0.12 * s)]
    pts = local(jitter(loc, seed, s * 0.015), (x, y), ang)
    out = [wc(D, pts, pal, seed, light=(-0.8, -0.4), wet=1, gran=2, inkw=0.9, inkop=0.6, edge=0.8, band=0.22)]
    out.append(veins([local([(0.15 * s, f * s * 0.2), (0.5 * s, f * s * 0.36), (0.84 * s, f * s * 0.38)], (x, y), ang) for f in (-1, 0.2, 1.2)],
                     pal[2], 0.7, 0.3))
    # the shadowed opening under the rim
    out.append(f'<path d="{smooth_closed(local([(0.9 * s, -0.36 * s), (1.0 * s, 0), (0.9 * s, 0.36 * s), (0.86 * s, 0)], (x, y), ang))}" '
               f'fill="{pal[2]}" opacity="0.35"/>')
    return "".join(out)


def raceme(D, pts, n, s0, s1, seed, side=1, nbuds=3, pal=BELL, gst="leaf"):
    """One-sided arching raceme: bells on short curved pedicels hanging from the outer side of the stem."""
    rnd = random.Random(seed)
    c = catmull(pts, 10)
    out = [stem(pts, 3.4, 1.6, gst, seed)]
    items = []
    tot = n + nbuds
    for k in range(tot):
        t = 0.5 + 0.48 * k / max(1, tot - 1)
        p, tg = along(c, t)
        nx, ny = -tg[1] * side, tg[0] * side
        if ny < 0:
            nx, ny = -nx, -ny
        L = 20 * (1 - 0.4 * t) * rnd.uniform(0.85, 1.15)
        tip = (p[0] + nx * L * 0.6 + tg[0] * L * 0.4, p[1] + ny * L * 0.6 + tg[1] * L * 0.4 + L * 0.4)
        mid = (p[0] + nx * L * 0.6, p[1] + ny * L * 0.3 - 2)
        sz = s0 + (s1 - s0) * k / max(1, tot - 1)
        items.append((p, mid, tip, sz, k >= n, rnd.uniform(-14, 14)))
    for p, mid, tip, sz, isbud, wob in items:
        out.append(pline(bez(p, mid, tip, 6), GREENS[gst][2], 1.6, int(tip[0]), 0.9, 1))
    for p, mid, tip, sz, isbud, wob in items[::-1]:
        out.append(bell(D, tip[0], tip[1] - 1, 90 + wob, sz, seed + int(tip[0] * 3), pal, bud=isbud))
    return "".join(out)


@design("may-lily-of-the-valley")
def may_lily():
    D = Doc("bf-may")
    out = page(D, 5, wash_col="#9CC29A", wash=(300, 255, 228, 205), wash_op=0.17)
    out.append(spatter(51, (90, 70, 510, 440), ["#7AA878", "#D8E0C0"], 16))
    # two broad sheathing leaves with parallel veins
    out.append(leaf(D, (292, 452), -112, 330, 116, "deep", 5, "lance", curl=-0.1, side_veins=0, parallel=7, inkw=1.0))
    out.append(leaf(D, (306, 452), -66, 300, 104, "deep", 6, "lance", curl=0.12, side_veins=0, parallel=7, inkw=1.0))
    # the sheath wrapping the base
    sh = [(290, 452), (289, 424), (296, 408), (304, 408), (311, 424), (312, 452)]
    out.append(wc(D, sh, ("#E8E2C8", "#C8B88A", "#7A6A42"), 7, inkw=0.9, wet=1))
    out.append(raceme(D, [(302, 452), (306, 330), (330, 200), (400, 124), (470, 136)], 7, 36, 20, 8, side=1))
    out.append(raceme(D, [(298, 452), (292, 370), (262, 270), (196, 214), (138, 236)], 5, 30, 18, 9, side=-1, nbuds=3))
    out.append(month_type(D, "May", "Lily of the Valley", "#1E4A30", "#7AA878", seed=5))
    return finish(D, out, 5)


# ================================================================ 06 June · Rose
ROSE = ("#FFD6D8", "#EE8A98", "#A8344E")
ROSE_IN = ("#F8A8B4", "#D8566E", "#8A1A36")


def rose(D, cx, cy, R, seed, tilt=0.78, rot=0.0, pal=ROSE, inner=ROSE_IN):
    """Garden rose, three-quarter view: two rings of broad cupped petals with rolled rims, a deep spiralled heart."""
    out = []
    rnd = random.Random(seed)
    out.append(radial(D, cx, cy, R, 5, pal, seed, tilt, rot, shape="round", tip="round", W=1.05, r0=0.04, curl=0.0, ja=8, Lvar=0.06,
                      nveins=3, vein_w=0.8, vein_op=0.22, inkw=0.9, a0=rnd.uniform(0, 72), edge=0.6, band=0.18))
    out.append(radial(D, cx, cy - R * 0.06, R * 0.8, 5, pal, seed + 1, tilt, rot, shape="round", tip="round", W=1.0, r0=0.04, ja=8,
                      nveins=3, vein_w=0.8, vein_op=0.22, inkw=0.9, a0=rnd.uniform(0, 72), edge=0.65, cup=0.5, band=0.2))
    # the cup: crescent petals wrapping the heart, each with a lit rolled lip
    for k in range(5):
        r = R * (0.56 - k * 0.09)
        a0 = rnd.uniform(0, 360) + k * 137
        span = 200 - k * 12
        outer = [(r * math.cos(math.radians(a0 + span * i / 16)), r * math.sin(math.radians(a0 + span * i / 16))) for i in range(17)]
        lift = r * 0.32
        inner_arc = [(x * 0.62, y * 0.62 - lift) for x, y in outer[::-1]]
        P = face(outer + inner_arc, cx, cy - R * 0.1 - k * R * 0.04, tilt, rot)
        pk = inner if k else pal
        out.append(wc(D, P, pk, seed + 10 + k, light=(-0.4, -0.9), wet=1, gran=2, inkw=0.9, inkop=0.6, edge=0.7, band=0.25))
        lip = face([(x * 0.98, y * 0.98) for x, y in outer[2:-2]], cx, cy - R * 0.1 - k * R * 0.04, tilt, rot)
        out.append(veins([lip], mix(pal[0], "#FFFFFF", 0.4), max(1.2, R * 0.025), 0.55))
    hc = face([(0, -R * 0.06)], cx, cy - R * 0.3, tilt, rot)[0]
    sp = [(hc[0] + R * 0.12 * (1 - i / 14) * math.cos(i * 0.9), hc[1] + R * 0.09 * (1 - i / 14) * math.sin(i * 0.9)) for i in range(15)]
    out.append(f'<path d="{blob(hc[0], hc[1], R * 0.13, R * 0.09, seed, 0.1, 10)}" fill="{inner[2]}" opacity="0.6"/>')
    out.append(pen(smooth_open(sp), 1.2, seed, 0.6, mix(inner[2], "#000000", 0.3), False))
    return "".join(out)


def rose_bud(D, x, y, ang, s, seed, pal=ROSE_IN):
    """Pointed bud with the outer petal unfurling, five feathery sepals peeling back, a round green hip."""
    out = []
    for k, sa in enumerate((-150, 150, -105, 105, 180)):
        sep = petal(s * 0.95, s * 0.2, "lance", "round", 0.25 * (1 if sa > 0 else -1), 12, seed=seed + k, nveins=0, lobes=3, lobe_depth=0.4,
                    lobe_kind="serrate")[0]
        out.append(wc(D, local(sep, (x, y), ang + sa * 0.55 + (180 if abs(sa) == 180 else 0)), GREENS["leaf"], seed + k, inkw=0.7, wet=0, gran=2))
    bud = local([(0, -0.3 * s), (0.35 * s, -0.38 * s), (0.8 * s, -0.22 * s), (1.15 * s, 0), (0.8 * s, 0.2 * s), (0.35 * s, 0.36 * s), (0, 0.28 * s)], (x, y), ang)
    out.append(wc(D, bud, pal, seed + 9, wet=1, inkw=0.9, inkop=0.6, band=0.25))
    out.append(veins([local([(0.1 * s, 0.25 * s), (0.6 * s, 0.1 * s), (1.1 * s, 0.0)], (x, y), ang),
                      local([(0.2 * s, -0.3 * s), (0.6 * s, -0.12 * s), (0.9 * s, -0.12 * s)], (x, y), ang)], pal[2], 1.0, 0.55))
    for k, sa in enumerate((-40, 40, 0)):
        sep = petal(s * 0.7, s * 0.16, "lance", "round", -0.1, 10, seed=seed + 20 + k, nveins=0)[0]
        out.append(wc(D, local(sep, (x, y), ang + sa), GREENS["leaf"], seed + 20 + k, inkw=0.7, wet=0, gran=0, op=0.9))
    hip = local(blob_pts(-0.12 * s, 0, 0.16 * s, 0.14 * s, seed, 0.03, 12), (x, y), ang)
    out.append(wc(D, hip, GREENS["leaf"], seed + 30, inkw=0.8, wet=0))
    return "".join(out)


def compound_leaf(D, base, ang, L, seed, pal="leaf", pairs=2, size=1.0, accent="#C8605A", stalk=True):
    """Rose leaf: a rachis with paired, toothed, ovate leaflets and a terminal one."""
    out = []
    tip = local([(L, 0)], base, ang)[0]
    mid = local([(L * 0.5, L * 0.05)], base, ang)[0]
    rach = bez(base, mid, tip, 10)
    if stalk:
        out.append(stem([base, mid, tip], 2.6, 1.6, pal, seed, 0))
    for k in range(pairs):
        t = 0.3 + 0.55 * k / max(1, pairs)
        p, tg = along(rach, t)
        a = math.degrees(math.atan2(tg[1], tg[0]))
        for sg in (-1, 1):
            ll = L * 0.5 * size * (0.85 + 0.15 * k)
            out.append(leaf(D, p, a + sg * 55, ll, ll * 0.56, pal, seed + k * 3 + sg, "ovate", curl=0.06 * sg, lobes=8, lobe_depth=0.12,
                            lobe_kind="serrate", side_veins=4, inkw=0.8, accent=accent))
    out.append(leaf(D, tip, ang + 4, L * 0.58 * size, L * 0.34 * size, pal, seed + 9, "ovate", lobes=9, lobe_depth=0.12, lobe_kind="serrate",
                    side_veins=4, inkw=0.8, accent=accent))
    return "".join(out)


def thorns(pts, seed, n, col="#9A3A2A", s=7):
    c = catmull(pts, 8)
    rnd = random.Random(seed)
    out = []
    for k in range(n):
        p, tg = along(c, 0.1 + 0.8 * (k + rnd.uniform(-0.2, 0.2)) / n)
        sg = 1 if k % 2 else -1
        nx, ny = -tg[1] * sg, tg[0] * sg
        b1 = (p[0] - tg[0] * s * 0.5 + nx * 2, p[1] - tg[1] * s * 0.5 + ny * 2)
        b2 = (p[0] + tg[0] * s * 0.5 + nx * 2, p[1] + tg[1] * s * 0.5 + ny * 2)
        tp = (p[0] - tg[0] * s * 0.4 + nx * s, p[1] - tg[1] * s * 0.4 + ny * s)
        out.append(f'<path d="M {b1[0]:.1f} {b1[1]:.1f} Q {p[0] + nx * s * 0.5:.1f} {p[1] + ny * s * 0.5:.1f} {tp[0]:.1f} {tp[1]:.1f} '
                   f'Q {p[0] + nx * s * 0.3 + tg[0] * 2:.1f} {p[1] + ny * s * 0.3 + tg[1] * 2:.1f} {b2[0]:.1f} {b2[1]:.1f} Z" fill="{col}" opacity="0.9"/>')
    return "".join(out)


@design("june-rose")
def june_rose():
    D = Doc("bf-jun")
    out = page(D, 6, wash_col="#EBA0A8", wash=(300, 250, 228, 205), wash_op=0.16)
    out.append(spatter(61, (90, 70, 510, 440), ["#E07A8A", "#9DBA6A"], 16))
    s1 = [(296, 452), (300, 380), (296, 300), (300, 240)]
    s2 = [(300, 372), (338, 300), (390, 220), (418, 168)]
    out.append(stem(s1, 8, 6.5, "leaf", 1) + stem(s2, 5, 4, "leaf", 2))
    out.append(thorns(s1, 3, 5) + thorns(s2, 4, 3, s=5))
    out.append(compound_leaf(D, (298, 400), -160, 120, 10, size=1.0))
    out.append(compound_leaf(D, (300, 340), -18, 110, 12, size=0.95))
    out.append(compound_leaf(D, (360, 268), -150, 70, 14, pairs=1, size=0.9))
    out.append(rose_bud(D, 418, 168, -62, 54, 20))
    out.append(rose(D, 284, 186, 108, 30, tilt=0.76, rot=-6))
    out.append(month_type(D, "June", "Rose", "#6A1A30", "#E07A8A", seed=6))
    return finish(D, out, 6)


# ================================================================ 07 July · Larkspur
LARK = ("#C6D0F8", "#6E7EDC", "#2C2E8E")
LARK_PINK = ("#F6D2EE", "#D69ACE", "#8A447E")


def lark_floret(D, cx, cy, s, seed, tilt=0.9, rot=0.0, pal=LARK, spur=(-0.2, -1.0)):
    out = []
    # the spur: a slender tapering horn behind the flower
    sx, sy = spur
    sp = [(cx, cy), (cx + sx * s * 0.8 + s * 0.12, cy + sy * s * 0.8), (cx + sx * s * 1.5, cy + sy * s * 1.55), (cx + sx * s * 1.9, cy + sy * s * 1.7)]
    out.append(taper(sp, s * 0.36, s * 0.08, pal[2], 0.95))
    out.append(taper([(x - 1.2, y) for x, y in sp], s * 0.22, s * 0.05, pal[1], 0.95))
    out.append(taper([(x - 2.2, y) for x, y in sp[:3]], s * 0.07, s * 0.03, pal[0], 0.8))
    out.append(radial(D, cx, cy, s, 5, pal, seed, tilt, rot, shape="oval", tip="round", W=0.72, r0=0.08, ja=8, Lvar=0.1, nveins=3,
                      vein_w=0.7, vein_op=0.3, inkw=0.7, a0=-90 + (seed % 5) * 6, edge=0.6))
    # the small inner petals ("the bee") and the dark eye
    c = face([(0, 0)], cx, cy, tilt, rot)[0]
    for k, (dx, dy) in enumerate(((-0.12, -0.12), (0.12, -0.12), (0, 0.06))):
        out.append(f'<path d="{blob(c[0] + dx * s, c[1] + dy * s, s * 0.16, s * 0.13, seed + k, 0.1, 10)}" fill="{mix(pal[0], "#FFFFFF", 0.4)}" '
                   f'stroke="{pal[2]}" stroke-width="0.8" stroke-opacity="0.6"/>')
    out.append(f'<circle cx="{c[0]:.1f}" cy="{c[1] - s * 0.04:.1f}" r="{s * 0.07:.1f}" fill="#1E1A4A"/>')
    return "".join(out)


def lark_bud(D, x, y, s, seed, pal=LARK, lean=0.3):
    pts = blob_pts(x, y, s * 0.36, s * 0.5, seed, 0.05, 12, lean * 30)
    out = [taper([(x, y - s * 0.2), (x + lean * s * 0.4, y - s * 0.7), (x + lean * s * 0.2, y - s * 0.95)], s * 0.18, s * 0.04, pal[2], 0.9)]
    out.append(wc(D, pts, (pal[0], mix(pal[1], "#6A9A7A", 0.25), pal[2]), seed, wet=0, gran=2, inkw=0.7, edge=0.7))
    return "".join(out)


def spike(D, pts, n_open, n_bud, s0, s1, seed, pal=LARK):
    """A larkspur raceme: open florets low on alternating short pedicels, tightening into buds at the tip."""
    rnd = random.Random(seed)
    c = catmull(pts, 12)
    out = []
    items = []
    tot = n_open + n_bud
    for k in range(tot):
        t = 0.28 + 0.7 * k / (tot - 1)
        p, tg = along(c, t)
        sg = 1 if k % 2 else -1
        nx, ny = -tg[1] * sg, tg[0] * sg
        isbud = k >= n_open
        sz = s0 + (s1 - s0) * k / (tot - 1)
        off = sz * (0.7 if not isbud else 0.4)
        q = (p[0] + nx * off + tg[0] * sz * 0.2, p[1] + ny * off + tg[1] * sz * 0.2)
        items.append((p, q, sz, isbud, sg))
    for p, q, sz, isbud, sg in items:
        out.append(pline([p, lerp(p, q, 0.6), q], GREENS["leaf"][2], 1.6, int(q[1]), 0.85, 1))
    for i, (p, q, sz, isbud, sg) in enumerate(items):
        if isbud:
            out.append(lark_bud(D, q[0], q[1], sz, seed + i, pal, lean=sg * 0.3))
        else:
            out.append(lark_floret(D, q[0], q[1], sz, seed + i * 7, rnd.uniform(0.75, 0.98), rnd.uniform(-25, 25), pal,
                                   spur=(sg * 0.35, -0.9)))
    return "".join(out)


def feathery(D, base, ang, L, seed, pal="leaf", w=3.0, fork=2):
    """Finely divided leaf (larkspur, cosmos): a rachis with thread-like segments that fork again."""
    if isinstance(pal, str):
        pal = GREENS[pal]
    rnd = random.Random(seed)
    out = []

    def seg(p, a, l, wd, depth):
        tip = (p[0] + l * math.cos(math.radians(a)), p[1] + l * math.sin(math.radians(a)))
        bend = rnd.uniform(-0.18, 0.18) * l
        mid = (lerp(p, tip, 0.5)[0] - math.sin(math.radians(a)) * bend, lerp(p, tip, 0.5)[1] + math.cos(math.radians(a)) * bend)
        c = bez(p, mid, tip, 8)
        out.append(taper(c, wd, 0.6, pal[2], 0.9))
        out.append(taper([(x - 0.4, y - 0.4) for x, y in c], wd * 0.6, 0.4, pal[1], 0.9))
        if depth > 0:
            for t, da in ((0.35, -38), (0.5, 34), (0.68, -30), (0.8, 28)):
                if rnd.random() < 0.85:
                    q, _ = along(c, t)
                    seg(q, a + da + rnd.uniform(-10, 10), l * rnd.uniform(0.35, 0.5), wd * 0.7, depth - 1)
    seg(base, ang, L, w, fork)
    return "".join(out)


@design("july-larkspur")
def july_larkspur():
    D = Doc("bf-jul")
    out = page(D, 7, wash_col="#9AAEE8", wash=(300, 250, 228, 205), wash_op=0.17)
    out.append(spatter(71, (90, 70, 510, 440), ["#6E7EDC", "#9DBA6A"], 16))
    main = [(300, 452), (302, 360), (308, 240), (316, 74)]
    side = [(298, 452), (284, 380), (238, 280), (196, 150)]
    out.append(stem(side, 5, 2.5, "leaf", 2) + stem(main, 6.5, 2.5, "leaf", 1))
    for k, (b, a, L) in enumerate((((300, 430), -150, 100), ((302, 420), -30, 104), ((300, 392), -120, 80), ((304, 384), -60, 84), ((290, 400), -165, 70))):
        out.append(feathery(D, b, a, L, 40 + k))
    out.append(spike(D, side, 5, 5, 32, 12, 3, LARK_PINK))
    out.append(spike(D, main, 9, 7, 42, 13, 4, LARK))
    out.append(month_type(D, "July", "Larkspur", "#22265E", "#6E7EDC", seed=7))
    return finish(D, out, 7)


# ================================================================ 08 August · Poppy
POPPY = ("#FFA486", "#EE4A30", "#9A1612")


def poppy(D, cx, cy, s, seed, pal=POPPY):
    """Corn poppy, a shallow cup seen from slightly above: two inner petals behind with black basal blotches, the
    seed pod with its rayed crown in a ring of dark stamens, two crinkled outer petals in front."""
    out = []
    rnd = random.Random(seed)

    def pet(px, py, rx, ry, k, rot):
        pts = wash_pts(px, py, rx, ry, seed + k, 0.8, 40, rot)
        return pts

    back = [pet(cx - 0.42 * s, cy - 0.38 * s, 0.6 * s, 0.52 * s, 1, -20), pet(cx + 0.44 * s, cy - 0.4 * s, 0.6 * s, 0.52 * s, 2, 25)]
    for k, b in enumerate(back):
        out.append(wc(D, b, (mix(pal[0], pal[1], 0.3), pal[1], pal[2]), seed + k, grad=(b[len(b) // 4 * (1 + 2 * k)][0], cy - s, cx, cy),
                      wet=2, gran=6, inkw=0.9, inkop=0.5, edge=0.55))
        cid = D.clip(f'<path d="{smooth_closed(b)}"/>')
        bl = blob(cx + (-0.22 if k == 0 else 0.22) * s, cy - 0.12 * s, 0.24 * s, 0.18 * s, seed + 5 + k, 0.15, 12)
        cr = "".join(f'<path d="{smooth_open([(cx + (-0.1 if k == 0 else 0.1) * s, cy - 0.05 * s), (cx + (j - 3) * 0.12 * s, cy - 0.5 * s), (cx + (j - 3) * 0.24 * s * (1 if k else -1) + (-0.5 if k == 0 else 0.5) * s, cy - 0.85 * s)])}"/>' for j in range(7))
        out.append(f'<g {cid}><g fill="none" stroke="{pal[2]}" stroke-width="1" opacity="0.3">{cr}</g>'
                   f'<path d="{bl}" fill="#1C0808" opacity="0.88"/><path d="{bl}" fill="none" stroke="#F6E2C8" stroke-width="1.2" opacity="0.5"/></g>')
    # seed pod, stigma crown and stamens
    rnd2 = random.Random(seed + 9)
    st = []
    for i in range(46):
        a = rnd2.uniform(math.pi * 1.0, math.pi * 2.0)
        r1 = 0.14 * s
        r2 = rnd2.uniform(0.24, 0.34) * s
        x1, y1 = cx + r1 * math.cos(a), cy - 0.12 * s + r1 * 0.5 * math.sin(a)
        x2, y2 = cx + r2 * math.cos(a), cy - 0.12 * s + r2 * 0.55 * math.sin(a) - rnd2.uniform(0, 0.06) * s
        st.append(f'<path d="M {x1:.1f} {y1:.1f} L {x2:.1f} {y2:.1f}" stroke="#2A1010" stroke-width="0.9" opacity="0.7"/>'
                  f'<ellipse cx="{x2:.1f}" cy="{y2:.1f}" rx="2.2" ry="1.5" fill="#1A0A10"/>')
    out.append("".join(st))
    pod = blob_pts(cx, cy - 0.1 * s, 0.15 * s, 0.13 * s, seed, 0.03, 14)
    out.append(wc(D, pod, ("#D8E2B0", "#9AAE72", "#4E6038"), seed + 3, inkw=0.9, wet=0, gran=3))
    crown = blob_pts(cx, cy - 0.2 * s, 0.13 * s, 0.05 * s, seed + 1, 0.03, 16)
    out.append(wc(D, crown, ("#B88AA8", "#6A3A5A", "#2A1028"), seed + 4, inkw=0.8, wet=0, gran=0))
    rays = [[(cx, cy - 0.2 * s), (cx + 0.12 * s * math.cos(math.radians(a)), cy - 0.2 * s + 0.045 * s * math.sin(math.radians(a)))] for a in range(0, 360, 40)]
    out.append(veins(rays, "#E8D0E0", 1.0, 0.7))
    # front petals: crinkled outer faces with a wavy rim
    front = [pet(cx - 0.38 * s, cy + 0.32 * s, 0.6 * s, 0.4 * s, 3, 14), pet(cx + 0.4 * s, cy + 0.3 * s, 0.6 * s, 0.42 * s, 4, -16)]
    for k, f in enumerate(front):
        out.append(wc(D, f, pal, seed + 20 + k, grad=(cx + (-0.6 if k == 0 else 0.6) * s, cy - 0.1 * s, cx, cy + 0.6 * s), wet=2, gran=8,
                      inkw=1.0, inkop=0.55, edge=0.6, accent="#FF7A3A"))
        cid = D.clip(f'<path d="{smooth_closed(f)}"/>')
        cr = []
        for j in range(9):
            ex = cx + (-0.95 if k == 0 else 0.95) * s * (0.2 + 0.8 * j / 8) * (1 if j % 2 else 0.92)
            ey = cy - 0.12 * s + 0.1 * s * math.sin(j)
            cr.append(f'<path d="{smooth_open([(cx + (-0.05 if k == 0 else 0.05) * s, cy + 0.55 * s), ((cx + ex) / 2 + rnd.uniform(-6, 6), cy + 0.2 * s), (ex, ey)])}"/>')
        out.append(f'<g {cid}><g fill="none" stroke="{pal[2]}" stroke-width="1.1" opacity="0.32">{"".join(cr)}</g></g>')
        rim = f[len(f) * 5 // 8: len(f) * 7 // 8 + 1]
        out.append(veins([rim], mix(pal[0], "#FFFFFF", 0.3), 1.6, 0.6))
    return "".join(out)


def poppy_bud(D, x, y, s, seed, ang=100):
    """Nodding hairy bud hanging from the crook of its stem."""
    pts = local(blob_pts(0.5 * s, 0, 0.5 * s, 0.33 * s, seed, 0.03, 16), (x, y), ang)
    out = [wc(D, pts, GREENS["blue"], seed, wet=1, gran=4, inkw=0.9)]
    out.append(veins([local([(0.05 * s, 0), (0.5 * s, 0.04 * s), (0.98 * s, 0)], (x, y), ang)], GREENS["blue"][2], 1.0, 0.5))
    out.append(hairs(pts, seed, "#6A8A7A", 40, 4, 0.8, 0.7))
    # a sliver of red where the sepals part
    sl = local([(0.3 * s, 0.02 * s), (0.6 * s, 0.07 * s), (0.9 * s, 0.03 * s), (0.6 * s, 0.1 * s)], (x, y), ang)
    out.append(f'<path d="{smooth_closed(sl)}" fill="{POPPY[1]}" opacity="0.85"/>')
    return "".join(out)


def poppy_pod(D, x, y, s, seed):
    body = [(x - 0.12 * s, y), (x - 0.36 * s, y - 0.2 * s), (x - 0.4 * s, y - 0.55 * s), (x - 0.3 * s, y - 0.8 * s), (x + 0.3 * s, y - 0.8 * s),
            (x + 0.4 * s, y - 0.55 * s), (x + 0.36 * s, y - 0.2 * s), (x + 0.12 * s, y)]
    out = [wc(D, body, ("#D8E2B8", "#9AB07A", "#4A5E36"), seed, wet=1, gran=5, inkw=1.0)]
    out.append(veins([[(x + f * 0.3 * s, y - 0.78 * s), (x + f * 0.36 * s, y - 0.45 * s), (x + f * 0.1 * s, y - 0.05 * s)] for f in (-0.6, 0, 0.6)],
                     "#4A5E36", 0.8, 0.35))
    cr = blob_pts(x, y - 0.84 * s, 0.38 * s, 0.1 * s, seed, 0.05, 16)
    out.append(wc(D, cr, ("#C8A8B8", "#7A5068", "#3A1A2E"), seed + 1, wet=0, gran=0, inkw=0.9))
    out.append(veins([[(x, y - 0.84 * s), (x + 0.36 * s * math.cos(math.radians(a)), y - 0.84 * s + 0.09 * s * math.sin(math.radians(a)))]
                      for a in range(0, 360, 36)], "#F0DCE6", 1.0, 0.7))
    return "".join(out)


@design("august-poppy")
def august_poppy():
    D = Doc("bf-aug")
    out = page(D, 8, wash_col="#F09A7A", wash=(300, 250, 228, 205), wash_op=0.16)
    out.append(spatter(81, (90, 70, 510, 440), ["#E8603A", "#9DBA6A"], 16))
    s_main = [(300, 452), (296, 380), (306, 300), (300, 230)]
    s_bud = [(300, 452), (280, 390), (196, 330), (150, 268), (146, 236), (156, 246)]
    s_pod = [(304, 452), (322, 380), (410, 320), (448, 270)]
    for k, sp in enumerate((s_bud, s_pod, s_main)):
        out.append(stem(sp, 5.5, 4, "blue", k))
        c = catmull(sp, 8)
        out.append(hairs(c, 30 + k, "#6A8A7A", 50, 4, 0.8, 0.6))
    for k, (b, a, L, W) in enumerate((((298, 440), -160, 112, 40), ((302, 438), -24, 116, 40), ((296, 400), -128, 84, 30), ((306, 396), -54, 84, 30))):
        out.append(leaf(D, b, a, L, W, "blue", 50 + k, "lance", curl=0.1 * (1 if k % 2 else -1), lobes=5, lobe_depth=0.55, lobe_kind="serrate",
                        side_veins=0, inkw=0.9))
    out.append(poppy_pod(D, 448, 270, 66, 60))
    out.append(poppy_bud(D, 156, 246, 68, 61, 96))
    out.append(poppy(D, 300, 170, 116, 62))
    out.append(month_type(D, "August", "Poppy", "#6A1410", "#E8603A", seed=8))
    return finish(D, out, 8)


# ================================================================ 09 September · Aster
ASTER = ("#E2D4FA", "#A284DC", "#563496")
ASTER_D = ("#FFE27A", "#EDAA22", "#A0560E")
ASTER_OLD = ("#F2A27A", "#C8582E", "#6E2410")      # older discs blush rust as they age


def aster_head(D, cx, cy, R, seed, tilt=1.0, rot=0.0, pal=ASTER, dpal=ASTER_D, n=30):
    out = [radial(D, cx, cy, R, n, pal, seed, tilt, rot, shape="strip", tip="round", W=0.11, r0=0.26, curl=0.06, ja=4, Lvar=0.14,
                  nveins=1, vein_w=0.7, vein_op=0.35, inkw=0.6, edge=0.6)]
    out.append(radial(D, cx, cy, R * 0.85, n - 6, (pal[0], mix(pal[1], pal[0], 0.3), pal[2]), seed + 1, tilt, rot, shape="strip",
                      tip="round", W=0.12, r0=0.3, curl=0.05, ja=5, Lvar=0.1, nveins=1, vein_w=0.7, vein_op=0.3, inkw=0.6, a0=6, edge=0.55))
    out.append(disc(D, cx, cy, R * 0.3, dpal, seed + 5, tilt, rot, dots=50))
    return "".join(out)


def aster_bud(D, x, y, s, seed):
    pts = blob_pts(x, y, s * 0.45, s * 0.42, seed, 0.04, 12)
    out = [wc(D, pts, GREENS["leaf"], seed, wet=0, gran=2, inkw=0.8)]
    out.append(f'<path d="{blob(x, y - s * 0.3, s * 0.22, s * 0.14, seed, 0.1, 10)}" fill="{ASTER[1]}" opacity="0.85"/>')
    scales = [[(x + f * s * 0.35, y + s * 0.3), (x + f * s * 0.4, y), (x + f * s * 0.2, y - s * 0.25)] for f in (-1, -0.3, 0.4, 1)]
    out.append(veins(scales, GREENS["leaf"][2], 0.8, 0.5))
    return "".join(out)


@design("september-aster")
def september_aster():
    D = Doc("bf-sep")
    out = page(D, 9, wash_col="#B49AE0", wash=(300, 250, 228, 205), wash_op=0.16)
    out.append(spatter(91, (90, 70, 510, 440), ["#9A7AD0", "#E8B82A"], 16))
    # a branching spray: one main stem, side branches each ending in a flower or bud
    main = [(300, 452), (298, 380), (292, 290), (288, 210)]
    br = [[(298, 390), (330, 340), (380, 290), (420, 252)], [(296, 340), (262, 300), (214, 262), (178, 236)],
          [(294, 300), (320, 250), (352, 190), (372, 150)], [(292, 260), (262, 220), (230, 168), (214, 138)],
          [(296, 360), (340, 340), (420, 340), (448, 330)], [(298, 410), (250, 380), (196, 350), (160, 340)]]
    out.append(stem(main, 6, 4, "sage", 1))
    for k, b in enumerate(br):
        out.append(stem(b, 3.8, 2.6, "sage", 10 + k, 0.7))
    # narrow, clasping leaves along the stems
    lv = [((298, 420), -150, 70, 15), ((299, 405), -32, 72, 15), ((340, 334), -70, 44, 10), ((240, 286), -130, 46, 10), ((322, 254), -10, 44, 10),
          ((256, 214), -160, 40, 9), ((380, 340), 30, 46, 10), ((220, 368), 160, 46, 10)]
    for k, (b, a, L, W) in enumerate(lv):
        out.append(leaf(D, b, a, L, W, "sage", 30 + k, "lance", curl=0.1 * (1 if k % 2 else -1), side_veins=0, inkw=0.8))
    out.append(aster_bud(D, 448, 330, 20, 40) + aster_bud(D, 160, 340, 18, 41))
    heads = [((420, 248), 50, 0.8, -22, ASTER_D), ((178, 232), 52, 0.85, 18, ASTER_OLD), ((372, 146), 54, 0.9, -8, ASTER_D),
             ((214, 136), 46, 0.75, 24, ASTER_D), ((288, 196), 62, 0.95, 4, ASTER_D)]
    for k, ((x, y), R, t, r, dp) in enumerate(heads):
        out.append(aster_head(D, x, y, R, 50 + k * 7, t, r, dpal=dp))
    out.append(month_type(D, "September", "Aster", "#3E2470", "#9A7AD0", seed=9))
    return finish(D, out, 9)


# ================================================================ 10 October · Cosmos
COSMOS = ("#FFE0EE", "#F29AC2", "#B23A7A")
COSMOS_DEEP = ("#F8A8CE", "#D8488E", "#8A1452")


def cosmos_head(D, cx, cy, R, seed, tilt=1.0, rot=0.0, pal=COSMOS):
    out = [radial(D, cx, cy, R, 8, pal, seed, tilt, rot, shape="fan", tip="teeth", W=0.6, r0=0.12, curl=0.03, ja=4, Lvar=0.06,
                  nveins=5, vein_w=0.8, vein_op=0.38, inkw=0.8, teeth=2, depth=0.16, a0=(seed % 7) * 5, edge=0.6, band=0.14)]
    # the darker flush at the base of each petal (a ring around the eye)
    ring = face(blob_pts(0, 0, R * 0.3, R * 0.3, seed, 0.06, 18), cx, cy, tilt, rot)
    out.append(f'<path d="{smooth_closed(ring)}" fill="{pal[2]}" opacity="0.28"/>')
    out.append(disc(D, cx, cy, R * 0.18, YELLOW_D, seed + 5, tilt, rot, dots=40, dot_cols=["#6A3A10", "#9A5A10", "#FFE27A"]))
    return "".join(out)


def cosmos_bud(D, x, y, s, seed, pal=COSMOS_DEEP):
    pts = blob_pts(x, y, s * 0.4, s * 0.48, seed, 0.04, 12)
    out = [wc(D, pts, (pal[0], mix(pal[1], "#6A9A4A", 0.55), pal[2]), seed, wet=0, gran=2, inkw=0.8)]
    for k in range(7):
        a = math.radians(60 + k * 10)
        out.append(taper([(x, y + s * 0.2), (x + math.cos(a) * s * 0.5 * (1 if k % 2 else -1), y + s * 0.1), (x + math.cos(a) * s * 0.75 * (1 if k % 2 else -1), y - s * 0.1)],
                         2.6, 0.5, GREENS["leaf"][1], 0.9))
    return "".join(out)


@design("october-cosmos")
def october_cosmos():
    D = Doc("bf-oct")
    out = page(D, 10, wash_col="#EE9ABE", wash=(300, 250, 228, 205), wash_op=0.16)
    out.append(spatter(101, (90, 70, 510, 440), ["#D8488E", "#9DBA6A"], 16))
    s1 = [(300, 452), (296, 360), (270, 250), (226, 176)]
    s2 = [(300, 452), (306, 370), (346, 290), (398, 236)]
    s3 = [(298, 452), (300, 360), (314, 220), (330, 120)]
    s4 = [(302, 420), (360, 380), (430, 330), (452, 300)]
    for k, sp in enumerate((s1, s2, s3, s4)):
        out.append(stem(sp, 4, 2.6, "leaf", k, 0.7))
    for k, (b, a, L) in enumerate((((299, 430), -150, 96), ((301, 420), -26, 100), ((298, 370), -122, 76), ((304, 352), -50, 70),
                                   ((276, 270), -150, 60), ((334, 300), -20, 56))):
        out.append(feathery(D, b, a, L, 60 + k, "leaf", 2.6))
    out.append(cosmos_bud(D, 452, 296, 26, 70))
    out.append(cosmos_head(D, 330, 118, 70, 71, 0.72, 6, COSMOS_DEEP))
    out.append(cosmos_head(D, 398, 236, 66, 72, 0.9, -12, COSMOS))
    out.append(cosmos_head(D, 222, 186, 84, 73, 0.96, 4, COSMOS))
    out.append(month_type(D, "October", "Cosmos", "#6A1446", "#D8488E", seed=10))
    return finish(D, out, 10)


# ================================================================ 11 November · Chrysanthemum
MUM = ("#FFD09A", "#E8863A", "#963812")
MUM_IN = ("#FFE8B0", "#F4B456", "#B0661A")


def mum(D, cx, cy, R, seed, tilt=0.78, rot=0.0, pal=MUM, inner=MUM_IN):
    """Decorative chrysanthemum: reflexed outer rings of spoon petals, then tighter incurved rings building a dome."""
    out = []
    rings = [(1.0, 22, 0.2, 0.0, pal), (0.86, 20, 0.22, 0.25, pal), (0.7, 18, 0.24, 0.55, pal), (0.54, 15, 0.27, 0.85, inner),
             (0.4, 12, 0.3, 1.1, inner), (0.27, 9, 0.34, 1.3, inner)]
    for k, (rr, n, W, cup, pk) in enumerate(rings):
        out.append(radial(D, cx, cy - k * R * 0.07, R * rr, n, pk, seed + k * 11, tilt, rot, shape="spoon", tip="round", W=W, r0=0.1,
                          curl=0.08, ja=6, Lvar=0.1, nveins=1, vein_w=0.7, vein_op=0.3, inkw=0.6, a0=k * 9, edge=0.6, cup=cup, band=0.16))
    return "".join(out)


def mum_leaf(D, base, ang, L, seed, pal=("#A8BC88", "#5E7E4A", "#28401E")):
    """Deeply lobed chrysanthemum leaf (five rounded lobes)."""
    return leaf(D, base, ang, L, L * 0.7, pal, seed, "ovate", curl=0.05, lobes=3, lobe_depth=0.42, lobe_kind="spiny", side_veins=3, inkw=0.9,
                accent="#9AA86A")


@design("november-chrysanthemum")
def november_chrysanthemum():
    D = Doc("bf-nov")
    out = page(D, 11, wash_col="#E8A060", wash=(300, 250, 228, 205), wash_op=0.17)
    out.append(spatter(111, (90, 70, 510, 440), ["#D8782E", "#9DBA6A"], 16))
    s1 = [(300, 452), (300, 360), (290, 270), (280, 220)]
    s2 = [(300, 410), (340, 360), (390, 300), (418, 262)]
    s3 = [(300, 380), (262, 330), (214, 290), (186, 274)]
    for k, sp in enumerate((s1, s2, s3)):
        out.append(stem(sp, 6 - k, 4, "sage", k))
    for k, (b, a, L) in enumerate((((300, 430), -150, 96), ((300, 418), -30, 100), ((298, 352), -165, 80), ((302, 330), -14, 76),
                                   ((350, 348), 30, 56), ((240, 312), 150, 54))):
        out.append(mum_leaf(D, b, a, L, 70 + k))
    out.append(mum(D, 186, 266, 48, 80, 0.7, 14, ("#FFE4A8", "#F2B24A", "#A86414"), ("#FFF0C8", "#F8CC70", "#B88020")))
    out.append(mum(D, 418, 254, 56, 81, 0.72, -12, ("#F2A08A", "#C8503A", "#7A1E14"), ("#FFC09A", "#E07A50", "#962E1A")))
    out.append(mum(D, 282, 176, 106, 82, 0.74, 0))
    out.append(month_type(D, "November", "Chrysanthemum", "#5A240E", "#D8782E", seed=11))
    return finish(D, out, 11)


# ================================================================ 12 December · Holly
HOLLY = ("#86B07A", "#2E6A3E", "#0E321E")
BERRY = ("#FF8A70", "#D42A26", "#7A0A10")


def holly_leaf(D, base, ang, L, seed, pal=HOLLY, W=None):
    W = W or L * 0.5
    outline, _, axis = petal(L, W, "ovate", "round", 0.06 * (1 if seed % 2 else -1), 24, seed=seed, wob=0.01, nveins=0, lobes=4,
                             lobe_depth=0.42, lobe_kind="spiny")
    pts = place(outline, ang, *base)
    ax = place(axis, ang, *base)
    tipp = ax[-1]
    halfp = place(outline[: len(outline) // 2 + 1] + axis[::-1], ang, *base)
    out = [wc(D, pts, pal, seed, grad=(tipp[0], tipp[1], base[0], base[1]), half=halfp, wet=2, gran=4, inkw=1.0, inkop=0.6, edge=0.6,
              accent="#5A9A6A")]
    out.append(veins([ax[1:-1]], "#C8E0B0", max(1.0, W * 0.04), 0.6))
    # glossy highlight: a dry-brush stripe of near-white along one side of the midrib
    hl = [lerp(ax[i], pts[i], 0.45) for i in range(3, len(ax) - 4, 2)]
    out.append(taper(hl, max(2.5, W * 0.1), 0.6, "#EAF6E0", 0.55))
    return "".join(out)


def berries(D, cx, cy, r, n, seed, pal=BERRY):
    rnd = random.Random(seed)
    out = []
    pos = [(cx, cy)] + [(cx + math.cos(a) * r * 1.6, cy + math.sin(a) * r * 1.4) for a in (rnd.uniform(0, 6.28) + k * 2 * math.pi / (n - 1) for k in range(n - 1))]
    for x, y in sorted(pos, key=lambda p: p[1]):
        pts = blob_pts(x, y, r, r * 0.96, rnd.randint(0, 999), 0.03, 14)
        out.append(wc(D, pts, pal, rnd.randint(0, 999), light=(-0.6, -0.8), wet=0, gran=2, inkw=0.9, inkop=0.6, edge=0.7, band=0.25))
        out.append(f'<path d="{blob(x - r * 0.35, y - r * 0.38, r * 0.26, r * 0.18, rnd.randint(0, 99), 0.1, 8, -30)}" fill="#FFFFFF" opacity="0.8"/>')
        out.append(f'<circle cx="{x + r * 0.12:.1f}" cy="{y + r * 0.2:.1f}" r="{max(1.2, r * 0.12):.1f}" fill="#2A0A0A" opacity="0.7"/>')
    return "".join(out)


@design("december-holly")
def december_holly():
    D = Doc("bf-dec")
    out = page(D, 12, wash_col="#C85A5A", wash=(300, 250, 228, 205), wash_op=0.13)
    out.append(spatter(121, (90, 70, 510, 440), ["#D42A26", "#2E6A3E"], 16))
    twig = [(170, 446), (220, 380), (270, 300), (330, 220), (400, 150)]
    out.append(stem(twig, 7, 4, ("#B89A72", "#7A5A3A", "#3E2A18"), 1))
    side = [(256, 320), (210, 270), (180, 200)]
    out.append(stem(side, 4.5, 3, ("#B89A72", "#7A5A3A", "#3E2A18"), 2, 0.7))
    lv = [((250, 330), -170, 108, 1), ((262, 318), -20, 104, 2), ((310, 246), -150, 100, 3), ((322, 236), 8, 102, 4), ((376, 172), -110, 92, 5),
          ((394, 156), -20, 96, 6), ((206, 264), -170, 84, 7), ((194, 226), -60, 80, 8), ((214, 384), 160, 90, 9), ((226, 372), 20, 86, 10)]
    for b, a, L, k in lv:
        out.append(holly_leaf(D, b, a, L, 20 + k))
    out.append(berries(D, 266, 304, 13, 5, 31) + berries(D, 330, 228, 12, 4, 32) + berries(D, 196, 238, 11, 3, 33) + berries(D, 402, 150, 11, 3, 34))
    out.append(month_type(D, "December", "Holly", "#1E3A26", "#C8342E", seed=12))
    return finish(D, out, 12)


# ================================================================ build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
