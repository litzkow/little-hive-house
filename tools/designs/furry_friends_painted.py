"""Furry Friends, hand-painted (gouache / storybook) edition.

Repaints the six original Furry Friends magnets and adds painted breed portraits (dogs and cats) plus a couple
of little scenes. Every piece is gouache on warm paper: organic shapes, washes with pooled edges, fur painted
as short brush strokes that follow the coat, a warm brown pen line under the paint, glossy eyes with
catchlights, painted collars / bandanas / bows, and brush-textured lettering.

Run from tools/designs:  python3 furry_friends_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_b import brush, btext, dabs, form, hand_rule, plaid_fill, plain, wobble_line
from gouache import blob, blob_pts, grain, ink, jitter, paper, smooth_closed, smooth_open
from poster import ANTON

COL = "furry-friends"
INK = "#3A2418"
FLECK = "#8A6A4A"
DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def _f(v):
    return f"{v:.1f}"


class Ids:
    def __init__(self, slug):
        self.p, self.n = "ff-" + slug, 0

    def __call__(self, tag="i"):
        self.n += 1
        return f"{self.p}-{tag}{self.n}"


# ================================================================ geometry
def sym(R, cx=300):
    """Right half (top centre -> bottom centre, inclusive) -> full closed outline, mirrored about x = cx."""
    return R + [(2 * cx - x, y) for x, y in reversed(R[1:-1])]


def mirror(pts, cx=300):
    return [(2 * cx - x, y) for x, y in pts]


def bbox(pts, pad=0):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def rot_pts(pts, cx, cy, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def catmull(pts, n=8):
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out


def closed_curve(pts, n=6):
    """Dense points along the smooth closed curve through pts (for tufts / sampling)."""
    m = len(pts)
    ext = [pts[-1]] + pts + [pts[0], pts[1]]
    out = []
    for i in range(1, m + 1):
        seg = catmull(ext[i - 1:i + 3], n)
        out += seg[n:2 * n]
    return out


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def radial(cx, cy, add=0):
    """Fur-flow field: strokes pointing away from (cx, cy)."""
    return lambda x, y: math.degrees(math.atan2(y - cy, x - cx)) + add


# ================================================================ grounds, light
def glow(u, cx, cy, r, color, op=0.6, ry=None):
    g = u("gl")
    return (f'<defs><radialGradient id="{g}"><stop offset="0" stop-color="{color}" stop-opacity="{op}"/>'
            f'<stop offset="0.55" stop-color="{color}" stop-opacity="{op * 0.4:.2f}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient></defs>'
            f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(r)}" ry="{_f(ry or r)}" fill="url(#{g})"/>')


def shadow(u, cx, cy, rx, ry, op=0.3, color="#2A1608"):
    return glow(u, cx, cy, rx, color, op, ry)


def lgrad(u, stops, x1=0, y1=0, x2=0, y2=1):
    g = u("lg")
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a[0] if a else 1}"/>' for o, c, *a in stops)
    return f'<defs><linearGradient id="{g}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient></defs>', f"url(#{g})"


def bg(u, base, tints, seed, fleck=FLECK, angle=-20, n=260, length=(60, 170), width=(6, 18), op=(0.05, 0.14), mottle=None):
    out = [paper(u("pp"), base, fleck, seed, 1.2), brush((-40, -40, 640, 640), tints, seed + 1, n, angle, length, width, op, 0.15)]
    rnd = random.Random(seed + 2)
    for col in (mottle or tints[:2]):
        for _ in range(3):
            out.append(f'<path d="{blob(rnd.uniform(40, 560), rnd.uniform(40, 560), rnd.uniform(90, 200), rnd.uniform(70, 160), rnd.randint(0, 999), 0.14, 16)}" '
                       f'fill="{col}" opacity="{rnd.uniform(0.04, 0.09):.2f}"/>')
    return "".join(out)


def sky(u, stops, tints, seed, n=120, angle=-4, op=(0.06, 0.16)):
    d, g = lgrad(u, stops)
    return d + f'<rect width="600" height="600" fill="{g}"/>' + brush((-60, -20, 640, 620), tints, seed, n, angle, (80, 220), (6, 16), op, 0.1)


def spot(u, cx, cy, rx, ry, base, tints, seed, edge=None, op=1.0, wob=0.1):
    """A loose painted wash spot (the 'vignette' many storybook portraits sit on)."""
    d = blob(cx, cy, rx, ry, seed, wob, 26)
    cid = u("sp")
    out = [f'<g opacity="{op}"><path d="{d}" fill="{base}"/><clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})">',
           brush((cx - rx, cy - ry, cx + rx, cy + ry), tints, seed, rx * ry / 260, -20, (rx * 0.25, rx * 0.7), (5, 14), (0.12, 0.3), 0.15),
           "</g>"]
    if edge:
        out.append(f'<path d="{d}" fill="none" stroke="{edge}" stroke-width="2.4" opacity="0.35"/>')
    out.append("</g>")
    return "".join(out)


def vignette(u, color, op=0.45, inner=0.6):
    g = u("vg")
    return (f'<defs><radialGradient id="{g}" cx="0.5" cy="0.5" r="0.72"><stop offset="{inner}" stop-color="{color}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="{op}"/></radialGradient></defs><rect width="600" height="600" fill="url(#{g})"/>')


def finish(u, color=INK, op=0.9, seed=9):
    return grain(u("gr"), color, seed, op)


def sparkle(x, y, s, col="#FFF4D6", op=0.9):
    return (f'<path d="M {_f(x)} {_f(y - s)} Q {_f(x + s * 0.15)} {_f(y - s * 0.15)} {_f(x + s)} {_f(y)} Q {_f(x + s * 0.15)} {_f(y + s * 0.15)} '
            f'{_f(x)} {_f(y + s)} Q {_f(x - s * 0.15)} {_f(y + s * 0.15)} {_f(x - s)} {_f(y)} Q {_f(x - s * 0.15)} {_f(y - s * 0.15)} {_f(x)} {_f(y - s)} Z" '
            f'fill="{col}" opacity="{op}"/>')


def heart_d(cx, cy, s):
    k = s / 16
    return (f"M {cx:.1f} {cy + 18 * k:.1f} C {cx - 30 * k:.1f} {cy - 2 * k:.1f} {cx - 24 * k:.1f} {cy - 24 * k:.1f} {cx - 8 * k:.1f} {cy - 20 * k:.1f} "
            f"Q {cx - 2 * k:.1f} {cy - 18 * k:.1f} {cx:.1f} {cy - 12 * k:.1f} Q {cx + 2 * k:.1f} {cy - 18 * k:.1f} {cx + 8 * k:.1f} {cy - 20 * k:.1f} "
            f"C {cx + 24 * k:.1f} {cy - 24 * k:.1f} {cx + 30 * k:.1f} {cy - 2 * k:.1f} {cx:.1f} {cy + 18 * k:.1f} Z")


def p_heart(u, cx, cy, s, pal=("#D2483A", "#8E1E16", "#F2806A"), seed=1, rot=0, ink_w=None):
    d = heart_d(cx, cy, s)
    return (f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">' +
            form(u, d, (cx - s * 1.6, cy - s * 1.4, cx + s * 1.6, cy + s * 1.2), pal[0], pal[1], pal[2], seed, -60, n=max(6, s * 1.5),
                 shade=(s * 0.18, s * 0.14), hi=(cx - s * 0.6, cy - s * 0.6, s * 0.3, s * 0.2), hi_op=0.6,
                 ink_w=ink_w if ink_w is not None else max(1, s * 0.09), ink_col=pal[1]) + "</g>")


def paw_d(cx, cy, s, rot=0):
    """A paw print as separate blobs (pad + 4 toes)."""
    parts = [blob(cx, cy + 0.42 * s, 1.0 * s, 0.82 * s, 3, 0.05, 14)]
    for i, (dx, dy, rx, ry, r) in enumerate(((-1.0, -0.55, 0.34, 0.46, -22), (-0.38, -1.12, 0.36, 0.48, -6), (0.38, -1.12, 0.36, 0.48, 6), (1.0, -0.55, 0.34, 0.46, 22))):
        parts.append(blob(cx + dx * s, cy + dy * s, rx * s, ry * s, 5 + i, 0.05, 12, rot=r))
    d = " ".join(parts)
    return d


def p_paw(u, cx, cy, s, pal, seed, rot=0, ink_w=None, inkc=None):
    d = paw_d(cx, cy, s)
    return (f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">' +
            form(u, d, (cx - 1.5 * s, cy - 1.7 * s, cx + 1.5 * s, cy + 1.3 * s), pal[0], pal[1], pal[2], seed, -60, n=s * 2,
                 shade=(s * 0.12, s * 0.1), ink_w=ink_w if ink_w is not None else max(1, s * 0.06), ink_col=inkc or pal[1],
                 length=(s * 0.2, s * 0.6), width=(max(0.8, s * 0.03), max(1.4, s * 0.07))) + "</g>")


# ================================================================ fur
def fur(u, pts, pal, seed, flow, n=None, shade=(10, 8), shade_op=0.45, hi=None, hi_op=0.35, ink_w=2.2, ink_col=INK, ink_op=0.75,
        length=(6, 18), width=(1.0, 2.6), tints=None, sop=(0.2, 0.5), density=1.0, curve=0.3, extra_in="", d=None):
    """A furry painted form: wash + shading + many short brush strokes following `flow`."""
    base, dark, light = pal
    d = d or smooth_closed(pts)
    box = bbox(pts)
    W, H = box[2] - box[0], box[3] - box[1]
    n = n if n is not None else int(W * H / 34 * density)
    return form(u, d, box, base, dark, light, seed, flow, n=n, length=length, width=width, tints=tints or [light, dark, base, light],
                shade=shade, shade_op=shade_op, hi=hi, hi_op=hi_op, ink_w=ink_w, ink_col=ink_col, ink_op=ink_op, sop=sop, curve=curve,
                extra_in=extra_in)


def tufts(pts, colors, seed, every=2, out_len=(5, 12), w=(1.6, 3.2), lean=0.0, op=(0.75, 1.0), cx=None, cy=None, skip=None):
    """Little tapered fur strokes breaking out over an outline (fluffy edges). pts = dense outline points."""
    rnd = random.Random(seed)
    n = len(pts)
    if cx is None:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        cx, cy = sum(xs) / n, sum(ys) / n
    res = []
    for i in range(0, n, every):
        x, y = pts[i]
        if skip and skip(x, y):
            continue
        a = pts[(i - 1) % n]
        b = pts[(i + 1) % n]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        if (x - cx) * nx + (y - cy) * ny < 0:
            nx, ny = -nx, -ny
        ln = rnd.uniform(*out_len)
        dx, dy = nx + lean * tx / L + rnd.uniform(-0.35, 0.35), ny + lean * ty / L + rnd.uniform(-0.35, 0.35)
        dl = math.hypot(dx, dy) or 1
        dx, dy = dx / dl * ln, dy / dl * ln
        ww = rnd.uniform(*w)
        sx, sy = x - dx * 0.6, y - dy * 0.6
        ex, ey = x + dx, y + dy
        mx, my = (sx + ex) / 2, (sy + ey) / 2
        px, py = -dy / ln * ww, dx / ln * ww
        res.append(f'<path d="M {_f(sx - px * 0.5)} {_f(sy - py * 0.5)} Q {_f(mx + px)} {_f(my + py)} {_f(ex)} {_f(ey)} Q {_f(mx - px * 0.4)} {_f(my - py * 0.4)} '
                   f'{_f(sx + px * 0.5)} {_f(sy + py * 0.5)} Z" fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(res)


def fluffy(pts, amp, seed, n=6, phase_k=1.0):
    """Turn a smooth outline into a scalloped, tufted fur outline (points pushed outward in little locks)."""
    dense = closed_curve(pts, n)
    m = len(dense)
    xs, ys = [p[0] for p in dense], [p[1] for p in dense]
    cx, cy = sum(xs) / m, sum(ys) / m
    rnd = random.Random(seed)
    out = []
    for i, (x, y) in enumerate(dense):
        a, b = dense[(i - 1) % m], dense[(i + 1) % m]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        if (x - cx) * nx + (y - cy) * ny < 0:
            nx, ny = -nx, -ny
        k = amp * (0.5 + 0.5 * math.sin(i * phase_k * 2.1)) * rnd.uniform(0.6, 1.2)
        out.append((x + nx * k, y + ny * k))
    return out


def feather(pts, colors, seed, every=2, L=(8, 18), w=(2, 4), down=0.6, bend=0.35, op=(0.8, 1.0), cx=None, cy=None, skip=None):
    """Soft locks of fur spilling over an outline and falling with gravity (feathered ears, ruffs, chests)."""
    rnd = random.Random(seed)
    n = len(pts)
    if cx is None:
        cx, cy = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    res = []
    for i in range(0, n, every):
        x, y = pts[i]
        if skip and skip(x, y):
            continue
        a, b = pts[(i - 1) % n], pts[(i + 1) % n]
        tx, ty = b[0] - a[0], b[1] - a[1]
        l = math.hypot(tx, ty) or 1
        nx, ny = -ty / l, tx / l
        if (x - cx) * nx + (y - cy) * ny < 0:
            nx, ny = -nx, -ny
        dx, dy = nx * (1 - down) + rnd.uniform(-0.2, 0.2), ny * (1 - down) + down
        dl = math.hypot(dx, dy) or 1
        ln = rnd.uniform(*L)
        dx, dy = dx / dl, dy / dl
        ww = rnd.uniform(*w)
        sx, sy = x - dx * ln * 0.5, y - dy * ln * 0.5
        ex, ey = x + dx * ln, y + dy * ln
        px, py = -dy, dx
        bd = rnd.uniform(-bend, bend) * ln
        mx, my = (sx + ex) / 2 + px * bd, (sy + ey) / 2 + py * bd
        res.append(f'<path d="M {_f(sx - px * ww)} {_f(sy - py * ww)} Q {_f(mx - px * ww * 0.6)} {_f(my - py * ww * 0.6)} {_f(ex)} {_f(ey)} '
                   f'Q {_f(mx + px * ww * 0.6)} {_f(my + py * ww * 0.6)} {_f(sx + px * ww)} {_f(sy + py * ww)} Z" fill="{rnd.choice(colors)}" '
                   f'opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(res)


def taper(pts, w0, w1, color, op=1.0):
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = (w0 + (w1 - w0) * i / max(1, n - 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return f'<path d="{smooth_closed(left + right[::-1])}" fill="{color}" opacity="{op}"/>'


def strands(pts_list, color, w, seed, op=0.7):
    """Hand-inked hair strands (each a short polyline)."""
    return "".join(ink(smooth_open(p), color, w, seed + i, 1, op) for i, p in enumerate(pts_list))


def locks(cx, cy, rx, ry, colors, seed, n=60, size=(5, 10), light=(-0.6, -0.8), ink_c=None):
    """Curly coat (poodle / doodle): overlapping little curl dabs, lighter toward the light."""
    rnd = random.Random(seed)
    items = []
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        r = math.sqrt(rnd.random()) * 0.95
        x, y = cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r
        lt = -(math.cos(a) * light[0] + math.sin(a) * light[1]) * r
        items.append((lt, x, y, rnd.uniform(*size)))
    out = []
    lt_c, base_c, dk_c = colors
    for lt, x, y, s in sorted(items):
        col = lt_c if lt > 0.3 else (dk_c if lt < -0.3 else base_c)
        out.append(f'<path d="{blob(x, y, s, s * 0.85, rnd.randint(0, 9999), 0.2, 9, rnd.uniform(0, 180))}" fill="{col}"/>')
        if ink_c:
            a0 = rnd.uniform(0, 6.28)
            out.append(f'<path d="M {_f(x + s * 0.55 * math.cos(a0))} {_f(y + s * 0.55 * math.sin(a0))} A {_f(s * 0.55)} {_f(s * 0.5)} 0 1 1 '
                       f'{_f(x + s * 0.55 * math.cos(a0 + 4.2))} {_f(y + s * 0.55 * math.sin(a0 + 4.2))}" fill="none" stroke="{ink_c}" '
                       f'stroke-width="{max(1, s * 0.16):.1f}" stroke-linecap="round" opacity="0.45"/>')
    return "".join(out)


# ================================================================ faces
def eye(u, cx, cy, rx, ry, iris=("#6A3A18", "#3A1C0A"), seed=1, look=(0, 0), rot=0, lid="#24140A", lid_w=None, pupil="#140A04",
        slit=False, white=False, hi=True, rim=None, lower_hi=True, pupil_k=0.55):
    """Glossy painted eye: almond outline, iris with a warm lower glow, pupil, two catchlights, inked lid."""
    lid_w = lid_w or max(1.6, rx * 0.2)
    pts = []
    for i in range(20):
        a = 2 * math.pi * i / 20
        k = 1 + 0.08 * math.cos(a) ** 3
        pts.append((cx + rx * math.cos(a) * k, cy + ry * math.sin(a) * (1.06 if math.sin(a) < 0 else 0.94)))
    pts = rot_pts(pts, cx, cy, rot)
    d = smooth_closed(pts)
    cid, gid = u("ec"), u("eg")
    lx, ly = cx + look[0] * rx * 0.25, cy + look[1] * ry * 0.2
    ir = min(rx, ry) * (0.82 if white else 1.02)
    out = []
    if rim:
        out.append(f'<path d="{smooth_closed([(x + (x - cx) * 0.22, y + (y - cy) * 0.28) for x, y in pts])}" fill="{rim}"/>')
    out.append(f'<defs><radialGradient id="{gid}" cx="{_f(lx)}" cy="{_f(ly + ir * 0.35)}" r="{_f(ir * 1.1)}" gradientUnits="userSpaceOnUse">'
               f'<stop offset="0" stop-color="{iris[0]}"/><stop offset="0.75" stop-color="{iris[1]}"/><stop offset="1" stop-color="{mix(iris[1], "#000000", 0.4)}"/></radialGradient>'
               f'<clipPath id="{cid}"><path d="{d}"/></clipPath></defs>')
    out.append(f'<path d="{d}" fill="{"#F6EEE2" if white else iris[1]}"/>')
    out.append(f'<g clip-path="url(#{cid})">')
    out.append(f'<circle cx="{_f(lx)}" cy="{_f(ly)}" r="{_f(ir)}" fill="url(#{gid})"/>')
    if slit:
        out.append(f'<path d="{blob(lx, ly, ir * 0.22, ir * 0.85, seed, 0.03, 12)}" fill="{pupil}"/>')
    else:
        out.append(f'<circle cx="{_f(lx)}" cy="{_f(ly)}" r="{_f(ir * pupil_k)}" fill="{pupil}"/>')
    # top lid shadow
    out.append(f'<path d="{d}" fill="none" stroke="#000000" stroke-width="{_f(ry * 0.5)}" opacity="0.22" transform="translate(0 {-ry * 0.12:.1f})"/>')
    out.append("</g>")
    if hi:
        out.append(f'<path d="{blob(lx - ir * 0.36, ly - ir * 0.36, ir * 0.26, ir * 0.22, seed + 1, 0.08, 10)}" fill="#FFFFFF" opacity="0.95"/>')
        out.append(f'<circle cx="{_f(lx + ir * 0.12)}" cy="{_f(ly - ir * 0.5)}" r="{_f(ir * 0.08)}" fill="#FFFFFF" opacity="0.85"/>')
        if lower_hi:
            out.append(f'<path d="M {_f(lx + ir * 0.05)} {_f(ly + ir * 0.62)} Q {_f(lx + ir * 0.45)} {_f(ly + ir * 0.5)} {_f(lx + ir * 0.6)} {_f(ly + ir * 0.15)}" '
                       f'stroke="#FFFFFF" stroke-width="{_f(max(1, ir * 0.1))}" fill="none" stroke-linecap="round" opacity="0.45"/>')
    out.append(ink(d, lid, lid_w * 0.6, seed + 2, 1, 0.9))
    top = [p for p in pts if p[1] <= cy + ry * 0.15]
    top = sorted(top, key=lambda p: p[0])
    out.append(ink(smooth_open(top), lid, lid_w, seed + 3, 2, 0.95))
    return "".join(out)


def dog_nose(u, cx, cy, w, col=("#2E2018", "#140C08", "#6A5448"), seed=1, h=None):
    h = h or w * 0.68
    pts = [(cx, cy - h * 0.5), (cx + w * 0.36, cy - h * 0.48), (cx + w * 0.5, cy - h * 0.18), (cx + w * 0.4, cy + h * 0.2),
           (cx + w * 0.14, cy + h * 0.42), (cx, cy + h * 0.5), (cx - w * 0.14, cy + h * 0.42), (cx - w * 0.4, cy + h * 0.2),
           (cx - w * 0.5, cy - h * 0.18), (cx - w * 0.36, cy - h * 0.48)]
    d = smooth_closed(pts)
    out = [form(u, d, (cx - w * 0.5, cy - h * 0.5, cx + w * 0.5, cy + h * 0.5), col[0], col[1], col[2], seed, 0, n=w * 0.6,
                shade=(w * 0.04, h * 0.1), shade_op=0.6, ink_w=max(1.2, w * 0.04), ink_col="#0E0806", ink_op=0.8,
                length=(w * 0.1, w * 0.3), width=(max(0.6, w * 0.015), max(1, w * 0.04)))]
    for s in (-1, 1):
        out.append(f'<path d="{blob(cx + s * w * 0.2, cy + h * 0.06, w * 0.1, h * 0.12, seed + s, 0.12, 10, rot=s * 35)}" fill="#080402"/>')
    out.append(ink(f"M {_f(cx)} {_f(cy + h * 0.2)} L {_f(cx)} {_f(cy + h * 0.5)}", "#080402", max(1, w * 0.035), seed, 1, 0.8))
    out.append(f'<path d="{blob(cx - w * 0.08, cy - h * 0.3, w * 0.2, h * 0.1, seed + 4, 0.15, 10, rot=-6)}" fill="#FFFFFF" opacity="0.5"/>')
    out.append(f'<circle cx="{_f(cx - w * 0.16)}" cy="{_f(cy - h * 0.3)}" r="{_f(w * 0.04)}" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


def cat_nose(u, cx, cy, w, col=("#E8A0A0", "#B8606A", "#F8D0CC"), seed=1, inkc="#6A2A2A"):
    h = w * 0.7
    d = smooth_closed([(cx - w * 0.5, cy - h * 0.45), (cx, cy - h * 0.55), (cx + w * 0.5, cy - h * 0.45), (cx + w * 0.12, cy + h * 0.32), (cx, cy + h * 0.45),
                       (cx - w * 0.12, cy + h * 0.32)])
    return (form(u, d, (cx - w * 0.5, cy - h * 0.55, cx + w * 0.5, cy + h * 0.45), col[0], col[1], col[2], seed, 0, n=4, shade=(0, h * 0.12),
                 shade_op=0.5, ink_w=max(1, w * 0.06), ink_col=inkc) +
            f'<path d="{blob(cx - w * 0.1, cy - h * 0.25, w * 0.16, h * 0.1, seed, 0.1, 8)}" fill="#FFFFFF" opacity="0.6"/>')


def cat_mouth(cx, cy, s, col="#4A2A2A", seed=1, w=1.8):
    """'w'-shaped cat mouth below the nose at (cx, cy)."""
    return ink(f"M {_f(cx)} {_f(cy)} L {_f(cx)} {_f(cy + s * 0.35)} M {_f(cx - s)} {_f(cy + s * 0.45)} Q {_f(cx - s * 0.45)} {_f(cy + s * 0.75)} {_f(cx)} {_f(cy + s * 0.35)} "
               f"Q {_f(cx + s * 0.45)} {_f(cy + s * 0.75)} {_f(cx + s)} {_f(cy + s * 0.45)}", col, w, seed, 2, 0.9)


def whiskers(cx, cy, side, spread, length, col="#FFFFFF", w=1.6, seed=1, n=3, droop=0.12, op=0.85):
    """Whiskers fanning from (cx, cy) to one side (side = 1 right / -1 left)."""
    out = []
    for k in range(n):
        a = (k - (n - 1) / 2) * spread
        ex = cx + side * length * math.cos(math.radians(a))
        ey = cy + length * math.sin(math.radians(a)) + length * droop
        mx = cx + side * length * 0.5
        my = cy + length * 0.5 * math.sin(math.radians(a)) - length * 0.04
        out.append(ink(f"M {_f(cx)} {_f(cy + (k - 1) * 3)} Q {_f(mx)} {_f(my)} {_f(ex)} {_f(ey)}", col, w, seed + k, 1, op))
    return "".join(out)


def muzzle_dots(cx, cy, side, col, seed, r=1.3, n=6):
    rnd = random.Random(seed)
    return "".join(f'<circle cx="{_f(cx + side * (rnd.uniform(0, 22)))}" cy="{_f(cy + rnd.uniform(-6, 8))}" r="{r}" fill="{col}" opacity="0.6"/>' for _ in range(n))


def tongue(u, cx, top, w, h, seed, pal=("#E8707A", "#B8404E", "#F8A8AE"), rot=0):
    d = smooth_closed([(cx - w * 0.5, top), (cx + w * 0.5, top), (cx + w * 0.52, top + h * 0.55), (cx + w * 0.3, top + h * 0.95), (cx, top + h),
                       (cx - w * 0.3, top + h * 0.95), (cx - w * 0.52, top + h * 0.55)])
    return (f'<g transform="rotate({rot} {_f(cx)} {_f(top)})">' +
            form(u, d, (cx - w * 0.55, top, cx + w * 0.55, top + h), pal[0], pal[1], pal[2], seed, -90, n=w * 0.8, shade=(w * 0.08, h * 0.1),
                 hi=(cx - w * 0.2, top + h * 0.55, w * 0.12, h * 0.16), hi_op=0.6, ink_w=max(1.2, w * 0.05), ink_col="#7A2030") +
            ink(f"M {_f(cx)} {_f(top + h * 0.12)} L {_f(cx + w * 0.02)} {_f(top + h * 0.62)}", pal[1], max(1, w * 0.05), seed, 1, 0.8) + "</g>")


# ================================================================ accessories
def band(center, w):
    """Ribbon outline (closed pts) of width w along a polyline."""
    pts = catmull(center, 6)
    n = len(pts)
    L, R = [], []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        L.append((x + nx * w / 2, y + ny * w / 2))
        R.append((x - nx * w / 2, y - ny * w / 2))
    return L + R[::-1], pts


def collar(u, center, w, pal, seed, studs=None, stitch="#FFFFFF", tag=None, tag_at=0.5, ring=True):
    """Painted collar along `center` (left -> right) with stitching, optional studs and a hanging tag.
    tag: (kind, pal) where kind in 'round', 'heart', 'bone'."""
    pts, mid = band(center, w)
    d = smooth_closed(pts)
    out = [form(u, d, bbox(pts), pal[0], pal[1], pal[2], seed, 0, n=len(mid) * 3, shade=(0, w * 0.22), shade_op=0.55,
                length=(w * 0.6, w * 1.6), width=(0.8, 1.8), ink_w=2, ink_col=mix(pal[1], "#000000", 0.4))]
    # stitching
    for sgn in (-1, 1):
        sp = []
        n = len(mid)
        for i, (x, y) in enumerate(mid):
            a, b = mid[max(i - 1, 0)], mid[min(i + 1, n - 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            l = math.hypot(dx, dy) or 1
            sp.append((x - dy / l * sgn * w * 0.3, y + dx / l * sgn * w * 0.3))
        out.append(f'<path d="{smooth_open(sp)}" fill="none" stroke="{stitch}" stroke-width="1.4" stroke-dasharray="4 4" opacity="0.6"/>')
    if studs:
        for i in range(2, len(mid) - 2, studs):
            x, y = mid[i]
            out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(w * 0.17)}" fill="#C8C2B8"/><circle cx="{_f(x - w * 0.05)}" cy="{_f(y - w * 0.06)}" r="{_f(w * 0.07)}" fill="#FFFFFF" opacity="0.9"/>')
    if tag:
        kind, tp = tag
        i = int(tag_at * (len(mid) - 1))
        x, y = mid[i]
        y += w * 0.42
        if ring:
            out.append(f'<ellipse cx="{_f(x)}" cy="{_f(y + 3)}" rx="5.5" ry="6.5" fill="none" stroke="#B89A5A" stroke-width="2.6"/>'
                       f'<ellipse cx="{_f(x)}" cy="{_f(y + 3)}" rx="5.5" ry="6.5" fill="none" stroke="#FFF2C8" stroke-width="0.9" opacity="0.8"/>')
        ty = y + 9
        out.append(tag_shape(u, kind, x, ty, tp, seed + 7))
    return "".join(out)


def tag_shape(u, kind, x, top, pal, seed, s=16):
    if kind == "heart":
        return p_heart(u, x, top + s * 0.95, s, pal, seed, ink_w=1.6)
    if kind == "bone":
        return p_bone(u, x, top + s * 0.6, s * 1.5, s * 0.36, seed, 0, pal, pal[1])
    d = blob(x, top + s * 0.85, s * 0.85, s * 0.85, seed, 0.02, 14)
    return form(u, d, (x - s, top, x + s, top + s * 1.8), pal[0], pal[1], pal[2], seed, 0, n=s, shade=(s * 0.12, s * 0.15),
                hi=(x - s * 0.3, top + s * 0.55, s * 0.25, s * 0.18), hi_op=0.7, ink_w=1.4, ink_col=pal[1]) + \
        f'<path d="{blob(x, top + s * 0.85, s * 0.55, s * 0.55, seed + 1, 0.02, 12)}" fill="none" stroke="{pal[1]}" stroke-width="1.1" opacity="0.5"/>'


GOLD_TAG = ("#E8B84A", "#9A6A1A", "#FFE8A0")
SILVER_TAG = ("#C8CCD0", "#7A8088", "#F4F6F8")


def bandana(u, left, right, tip, pal, seed, pattern="dots", pc="#FFFFFF", sag=14, roll=True, knot=None, rot_pat=0):
    """Front triangle of a tied bandana: top edge from `left` to `right` (sagging), point at `tip`."""
    base, dark, light = pal
    lx, ly = left
    rx, ry = right
    mx = (lx + rx) / 2
    top = [left, (lx + (mx - lx) * 0.5, ly + sag * 0.75), (mx, (ly + ry) / 2 + sag), (rx - (rx - mx) * 0.5, ry + sag * 0.75), right]
    tri = top + [(rx - (rx - tip[0]) * 0.35, ry + (tip[1] - ry) * 0.45), (tip[0] + 6, tip[1] - 4), tip, (tip[0] - 6, tip[1] - 4),
                 (lx + (tip[0] - lx) * 0.35, ly + (tip[1] - ly) * 0.45)]
    d = smooth_closed(jitter(tri, seed, 0.6))
    box = bbox(tri, 4)
    cid = u("bd")
    out = [shadow(u, tip[0] + 6, (ly + tip[1]) / 2 + 10, (rx - lx) * 0.42, (tip[1] - ly) * 0.45, 0.22)]
    out.append(form(u, d, box, base, dark, light, seed, lambda x, y: -90 + (x - tip[0]) * 0.25, n=(box[2] - box[0]) * 0.9, shade=(10, 0), shade_op=0.4,
                    ink_w=0, length=(10, 30), width=(1.2, 3)))
    pat = []
    rnd = random.Random(seed)
    if pattern == "dots":
        for gy in range(int(box[1]) - 10, int(box[3]) + 10, 16):
            for gx in range(int(box[0]) - 10 + (8 if (gy // 16) % 2 else 0), int(box[2]) + 10, 16):
                pat.append(f'<circle cx="{gx + rnd.uniform(-1, 1):.1f}" cy="{gy + rnd.uniform(-1, 1):.1f}" r="{rnd.uniform(2.2, 3):.1f}" fill="{pc}" opacity="0.85"/>')
    elif pattern == "paisley":
        for gy in range(int(box[1]) - 10, int(box[3]) + 10, 26):
            for gx in range(int(box[0]) - 10 + (13 if (gy // 26) % 2 else 0), int(box[2]) + 10, 26):
                a = rnd.uniform(0, 360)
                pat.append(f'<g transform="rotate({a:.0f} {gx} {gy})"><path d="M {gx - 6} {gy + 4} C {gx - 8} {gy - 6} {gx + 4} {gy - 8} {gx + 6} {gy - 2} '
                           f'C {gx + 7} {gy + 4} {gx} {gy + 7} {gx - 6} {gy + 4} Z" fill="none" stroke="{pc}" stroke-width="1.8" opacity="0.85"/>'
                           f'<circle cx="{gx}" cy="{gy}" r="1.8" fill="{pc}" opacity="0.85"/></g>')
                pat.append(f'<circle cx="{gx + 13:.0f}" cy="{gy + 2:.0f}" r="1.6" fill="{pc}" opacity="0.8"/>')
    elif pattern == "plaid":
        pat.append(plaid_fill(box, base, [(dark, 7, 26, 4, 0.55), (pc, 2.4, 26, 14, 0.6), (light, 3, 13, 0, 0.3)], seed, rot_pat or 45, mx, (ly + tip[1]) / 2))
    elif pattern == "stripes":
        for k in range(-20, 20):
            x = mx + k * 14
            pat.append(f'<path d="M {x} {box[1] - 20} L {x + 30} {box[3] + 20}" stroke="{pc}" stroke-width="4" opacity="0.7"/>')
    elif pattern == "flowers":
        for gy in range(int(box[1]) - 10, int(box[3]) + 10, 24):
            for gx in range(int(box[0]) - 10 + (12 if (gy // 24) % 2 else 0), int(box[2]) + 10, 24):
                x, y = gx + rnd.uniform(-2, 2), gy + rnd.uniform(-2, 2)
                pat.append("".join(f'<circle cx="{_f(x + 3.4 * math.cos(a))}" cy="{_f(y + 3.4 * math.sin(a))}" r="2.4" fill="{pc}" opacity="0.9"/>'
                                   for a in (0, 1.26, 2.51, 3.77, 5.03)))
                pat.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="1.7" fill="#F2C04A"/>')
    elif pattern == "stars":
        for gy in range(int(box[1]) - 10, int(box[3]) + 10, 22):
            for gx in range(int(box[0]) - 10 + (11 if (gy // 22) % 2 else 0), int(box[2]) + 10, 22):
                pat.append(sparkle(gx, gy, 4.5, pc, 0.85))
    out.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})">{"".join(pat)}')
    # folds and shading over the pattern
    d2, g = lgrad(u, [(0, "#000000", 0.0), (0.6, "#000000", 0.08), (1, "#000000", 0.3)], 0, 0, 1, 1)
    out.append(d2 + f'<rect x="{box[0]}" y="{box[1]}" width="{box[2] - box[0]}" height="{box[3] - box[1]}" fill="{g}"/>')
    for t in (0.3, 0.55):
        out.append(ink(smooth_open([(lx + (mx - lx) * t * 1.4, ly + sag * 0.8), ((lx + tip[0]) / 2 + 10, (ly + tip[1]) / 2 + 4), (tip[0] - 4, tip[1] - 12)]),
                       mix(dark, "#000000", 0.3), 1.6, seed + int(t * 10), 1, 0.35))
    out.append(ink(smooth_open([(mx + 20, (ly + ry) / 2 + sag + 4), (tip[0] + 14, (ly + tip[1]) / 2 + 10), (tip[0] + 4, tip[1] - 10)]), mix(dark, "#000000", 0.3), 1.6, seed + 9, 1, 0.3))
    out.append("</g>")
    out.append(ink(d, mix(dark, "#000000", 0.45), 2.2, seed + 3, 2, 0.8))
    if roll:
        rp, _ = band([(lx - 2, ly - 2), (lx + (mx - lx) * 0.5, ly + sag * 0.75 - 2), (mx, (ly + ry) / 2 + sag - 2), (rx - (rx - mx) * 0.5, ry + sag * 0.75 - 2), (rx + 2, ry - 2)], 12)
        rd = smooth_closed(rp)
        out.append(form(u, rd, bbox(rp), base, dark, light, seed + 5, 0, n=40, shade=(0, 4), shade_op=0.5, length=(10, 24), width=(1, 2.4),
                        hi=(mx - (rx - lx) * 0.2, (ly + ry) / 2 + sag * 0.6, (rx - lx) * 0.18, 2.5), hi_op=0.5, ink_w=2, ink_col=mix(dark, "#000000", 0.45)))
    if knot:
        kx, ky = knot
        out.append(form(u, blob(kx, ky, 13, 10, seed + 6, 0.08, 12), (kx - 14, ky - 11, kx + 14, ky + 11), base, dark, light, seed + 6, 30, n=12,
                        shade=(3, 3), ink_w=2, ink_col=mix(dark, "#000000", 0.45)))
    return "".join(out)


def bow(u, cx, cy, s, pal, seed, rot=0, tails=True, dots=None):
    """A painted bow tie / hair bow centred at (cx, cy)."""
    base, dark, light = pal
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    if tails:
        for sg in (-1, 1):
            tp = [(cx + sg * s * 0.1, cy + s * 0.1), (cx + sg * s * 0.42, cy + s * 0.95), (cx + sg * s * 0.2, cy + s * 0.85), (cx + sg * s * 0.08, cy + s * 1.0),
                  (cx - sg * s * 0.06, cy + s * 0.2)]
            out.append(form(u, smooth_closed(tp), bbox(tp, 2), base, dark, light, seed + sg, -90 + sg * 20, n=10, shade=(sg * 3, 2), ink_w=1.8,
                            ink_col=mix(dark, "#000000", 0.4)))
    for sg in (-1, 1):
        lp = [(cx, cy - s * 0.12), (cx + sg * s * 0.5, cy - s * 0.52), (cx + sg * s * 0.95, cy - s * 0.42), (cx + sg * s * 1.02, cy),
              (cx + sg * s * 0.95, cy + s * 0.42), (cx + sg * s * 0.5, cy + s * 0.5), (cx, cy + s * 0.12)]
        dd = smooth_closed(lp)
        out.append(form(u, dd, bbox(lp, 2), base, dark, light, seed + 3 + sg, sg * 10, n=s * 0.8, shade=(sg * s * 0.1, s * 0.1), shade_op=0.5,
                        hi=(cx + sg * s * 0.55, cy - s * 0.22, s * 0.22, s * 0.1), hi_op=0.5, ink_w=2, ink_col=mix(dark, "#000000", 0.4),
                        extra_in="".join(f'<circle cx="{_f(cx + sg * s * fx)}" cy="{_f(cy + s * fy)}" r="{_f(s * 0.075)}" fill="{dots}" opacity="0.9"/>'
                                         for fx, fy in ((0.35, -0.2), (0.7, -0.25), (0.55, 0.15), (0.85, 0.12), (0.3, 0.25))) if dots else ""))
        out.append(ink(smooth_open([(cx + sg * s * 0.2, cy - s * 0.05), (cx + sg * s * 0.55, cy - s * 0.14), (cx + sg * s * 0.82, cy - s * 0.1)]),
                       mix(dark, "#000000", 0.3), 1.4, seed + 5, 1, 0.45))
    k = blob(cx, cy, s * 0.2, s * 0.26, seed + 9, 0.06, 10)
    out.append(form(u, k, (cx - s * 0.22, cy - s * 0.28, cx + s * 0.22, cy + s * 0.28), base, dark, light, seed + 9, -90, n=6, shade=(2, 2), ink_w=2,
                    ink_col=mix(dark, "#000000", 0.4)))
    out.append("</g>")
    return "".join(out)


# ================================================================ lettering
def title(u, x, y, s, font, size, fill, tints, seed, max_w=470, ls=0, shadow=None, soff=(0.03, 0.04), angle=-75, hi=None, edge=None, edge_w=0, rot=0):
    t, sz, w = btext(u, x, y, s, font, size, fill, tints, seed, max_w=max_w, ls=ls, angle=angle, shadow=shadow, soff=soff, hi=hi,
                     edge=edge, edge_w=edge_w, rot=rot)
    return t


def ruled(u, y, s, font, size, fill, seed, ls=5, line=None, line_w=40, gap=14, w=2.2, max_w=440, cx=300):
    size = fit_size(s, font, size, max_w - 2 * (line_w + gap), ls)
    tw = measure(s, font, size, ls)
    ly = y - size * 0.34
    a, b = cx - tw / 2 - gap, cx + tw / 2 + gap
    return (plain(cx, y, s, font, size, fill, max_w, ls) + hand_rule(a - line_w, a, ly, line or fill, w, seed) +
            hand_rule(b, b + line_w, ly, line or fill, w, seed + 1))


def arc_title(u, s, cx, cy, r, font, size, fill, ls=0, top=True, shadow=None, soff=(1.5, 2), tints=None, seed=1):
    """Text on an arc; optional brush texture (clip by the same text) and offset shadow."""
    pid = u("ap")
    if top:
        d = f"M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"
    else:
        d = f"M {cx - r} {cy} A {r} {r} 0 0 0 {cx + r} {cy}"
    lsa = f' letter-spacing="{ls}"' if ls else ""
    tp = f'<textPath href="#{pid}" startOffset="50%">{esc(s)}</textPath>'
    out = [f'<defs><path id="{pid}" d="{d}" fill="none"/></defs>']
    if shadow:
        out.append(f'<text {font} font-size="{size}"{lsa} fill="{shadow}" text-anchor="middle" transform="translate({soff[0]} {soff[1]})">{tp}</text>')
    out.append(f'<text {font} font-size="{size}"{lsa} fill="{fill}" text-anchor="middle">{tp}</text>')
    if tints:
        cid = u("ac")
        out.append(f'<clipPath id="{cid}"><text {font} font-size="{size}"{lsa} text-anchor="middle">{tp}</text></clipPath><g clip-path="url(#{cid})">')
        out.append(brush((cx - r - size, cy - r - size, cx + r + size, cy + (r if not top else size)), tints, seed, r * 2.2, -75,
                         (size * 0.2, size * 0.6), (size * 0.03, size * 0.07), (0.2, 0.5), 0.2))
        out.append("</g>")
    return "".join(out)


def ribbon(u, cx, cy, w, h, pal, seed, tail=34, bend=8, fold=True, inkc=None):
    """A painted banner ribbon (curved slightly upward in the middle) with forked tails behind."""
    base, dark, light = pal
    inkc = inkc or mix(dark, "#000000", 0.4)
    out = []
    for sg in (-1, 1):
        x0 = cx + sg * (w / 2 - 10)
        tp = [(x0, cy - h / 2 + 10), (x0 + sg * tail, cy - h / 2 + 12), (x0 + sg * (tail - 12), cy + 8), (x0 + sg * tail, cy + h / 2 + 12),
              (x0, cy + h / 2 + 10)]
        out.append(form(u, smooth_closed(jitter(tp, seed + sg, 0.5)), bbox(tp, 2), dark, mix(dark, "#000000", 0.3), base,
                        seed + sg, 0, n=20, shade=None, ink_w=2, ink_col=inkc))
        if fold:
            fp = [(x0, cy - h / 2 + 10), (x0 - sg * 4, cy - h / 2 + 2), (x0 - sg * 14, cy - h / 2 + 2), (x0 - sg * 14, cy - h / 2 + 10)]
            out.append(f'<path d="M {_f(x0)} {_f(cy + h / 2 + 10)} L {_f(x0 - sg * 14)} {_f(cy + h / 2 + 2)} L {_f(x0 - sg * 14)} {_f(cy + h / 2 - 6)} Z" fill="{mix(dark, "#000000", 0.35)}"/>')
    top = [(cx - w / 2 + (k / 8) * w, cy - h / 2 - bend * math.sin(math.pi * k / 8)) for k in range(9)]
    bot = [(x, y + h) for x, y in reversed(top)]
    pts = top + bot
    d = smooth_open(top) + f" L {_f(bot[0][0])} {_f(bot[0][1])} " + smooth_open(bot).replace("M", "L", 1) + " Z"
    out.append(form(u, d, bbox(pts, 2), base, dark, light, seed, 0, n=w * 0.5, shade=(0, h * 0.18), shade_op=0.35, length=(20, 60), width=(1.5, 3.5),
                    hi=(cx, cy - h * 0.25, w * 0.35, h * 0.08), hi_op=0.35, ink_w=2.2, ink_col=inkc))
    return "".join(out)


def ribbon_text(cx, cy, s, font, size, fill, w, bend=8, ls=0, u=None):
    """Text following a ribbon's upward bow."""
    pid = u("rt")
    r = (w * w / 4 + bend * bend) / (2 * bend) if bend else 1e5
    x0, x1 = cx - w / 2, cx + w / 2
    yb = cy + size * 0.34
    d = f"M {_f(x0)} {_f(yb)} A {_f(r)} {_f(r)} 0 0 1 {_f(x1)} {_f(yb)}" if bend else f"M {_f(x0)} {_f(yb)} L {_f(x1)} {_f(yb)}"
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return (f'<defs><path id="{pid}" d="{d}"/></defs><text {font} font-size="{size}"{lsa} fill="{fill}" text-anchor="middle">'
            f'<textPath href="#{pid}" startOffset="50%">{esc(s)}</textPath></text>')


# ================================================================ small props
def bone_shape(cx, cy, L, r, rot=0):
    pts = []
    k = L / 2
    knob = [(cx - k, cy - r * 0.9), (cx - k, cy + r * 0.9), (cx + k, cy - r * 0.9), (cx + k, cy + r * 0.9)]
    d = " ".join(blob(x, y, r, r, i + 1, 0.04, 12) for i, (x, y) in enumerate(knob))
    d += " " + smooth_closed([(cx - k, cy - r * 0.62), (cx, cy - r * 0.52), (cx + k, cy - r * 0.62), (cx + k, cy + r * 0.62), (cx, cy + r * 0.52), (cx - k, cy + r * 0.62)])
    return d


def p_bone(u, cx, cy, L, r, seed, rot=0, pal=("#F6EAD2", "#C8AE86", "#FFFFFF"), inkc="#8A6A44"):
    d = bone_shape(cx, cy, L, r)
    return (f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">' +
            form(u, d, (cx - L / 2 - r * 1.2, cy - r * 2, cx + L / 2 + r * 1.2, cy + r * 2), pal[0], pal[1], pal[2], seed, 0, n=L * 0.6,
                 shade=(0, r * 0.4), shade_op=0.6, hi=(cx - L * 0.1, cy - r * 0.25, L * 0.35, r * 0.18), hi_op=0.7, ink_w=2.2, ink_col=inkc,
                 length=(L * 0.1, L * 0.3), width=(1, 2.4)) + "</g>")


def yarn(u, cx, cy, r, pal, seed, tail=None):
    d = blob(cx, cy, r, r * 0.96, seed, 0.03, 16)
    cid = u("yn")
    out = [form(u, d, (cx - r, cy - r, cx + r, cy + r), pal[0], pal[1], pal[2], seed, -30, n=r * 0.8, shade=(r * 0.2, r * 0.2), shade_op=0.55,
                ink_w=2, ink_col=mix(pal[1], "#000000", 0.4))]
    rnd = random.Random(seed)
    lines = []
    for k in range(9):
        a = rnd.uniform(0, 180)
        off = rnd.uniform(-0.6, 0.6) * r
        lines.append(f'<g transform="rotate({a:.0f} {_f(cx)} {_f(cy)})"><path d="M {_f(cx - r * 1.1)} {_f(cy + off)} Q {_f(cx)} {_f(cy + off - r * 0.35)} {_f(cx + r * 1.1)} {_f(cy + off)}" '
                     f'fill="none" stroke="{pal[1] if k % 2 else pal[2]}" stroke-width="{_f(max(1.2, r * 0.07))}" opacity="0.75"/></g>')
    out.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})">{"".join(lines)}</g>')
    if tail:
        out.append(ink(smooth_open(tail), pal[1], max(1.6, r * 0.08), seed, 1, 0.95))
    return "".join(out)


def flower(u, cx, cy, r, pal, seed, center="#F2C04A", petals=5, rot=0):
    out = []
    for i in range(petals):
        a = math.radians(rot + i * 360 / petals)
        px, py = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55
        out.append(f'<path d="{blob(px, py, r * 0.5, r * 0.36, seed + i, 0.08, 10, rot=math.degrees(a))}" fill="{pal[0] if i % 2 else pal[2]}"/>')
        out.append(f'<path d="{blob(px, py, r * 0.5, r * 0.36, seed + i, 0.08, 10, rot=math.degrees(a))}" fill="none" stroke="{pal[1]}" stroke-width="1.2" opacity="0.6"/>')
    out.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 0.24)}" fill="{center}"/><circle cx="{_f(cx - r * 0.06)}" cy="{_f(cy - r * 0.06)}" r="{_f(r * 0.09)}" fill="#FFF6D0"/>')
    return "".join(out)


def sprig(u, x, y, L, ang, col, seed, n=5, leaf_s=6):
    """Simple painted leafy sprig."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ex, ey = x + L * math.cos(a), y + L * math.sin(a)
    out = [ink(f"M {_f(x)} {_f(y)} Q {_f((x + ex) / 2 + 6)} {_f((y + ey) / 2 - 6)} {_f(ex)} {_f(ey)}", col[1], 1.8, seed, 1, 0.9)]
    for i in range(n):
        t = (i + 1) / (n + 1)
        px, py = x + (ex - x) * t, y + (ey - y) * t
        sg = 1 if i % 2 else -1
        la = ang + sg * 50
        out.append(f'<path d="{blob(px + math.cos(math.radians(la)) * leaf_s, py + math.sin(math.radians(la)) * leaf_s, leaf_s, leaf_s * 0.5, seed + i, 0.1, 10, rot=la)}" '
                   f'fill="{rnd.choice(col[::2])}"/>')
    return "".join(out)


# ================================================================ a painted cat (front portrait), shared by the cat designs
class Cat:
    """Front-facing cat bust. Geometry in local units (head ~ 230 wide at s=1) around the face centre (cx, cy).
    coat = (base, dark, light). Hooks draw markings clipped inside head / body / ears."""

    def __init__(self, u, cx, cy, s, coat, seed, ink_c="#3A2418", eyes=("#C8D86A", "#6E8A2A"), ear_in=("#E8A8A0", "#B86A6A", "#F8D0C8"),
                 nose=("#E8A0A0", "#B8606A", "#F8D0CC"), long=0.0, tufts_ear=False, body=True, cheek=1.0, ear_k=1.0, chin="#F4ECE2",
                 muzzle="#F4ECE2", muzzle_op=0.9, body_w=1.0, flow_k=1.0, look=(0.1, 0.1), slit=False, blink=False, pupil_k=0.62, whisk="#FFFFFF"):
        self.__dict__.update(locals())
        del self.__dict__["self"]

    def P(self, x, y):
        return (self.cx + x * self.s, self.cy + y * self.s)

    def Ps(self, pts):
        return [self.P(x, y) for x, y in pts]

    def head_pts(self):
        c = self.cheek
        R = [(0, -96), (36, -94), (66, -82), (92, -56), (108 * c, -22), (116 * c, 12), (110 * c, 40), (90 * c, 64), (60, 82), (30, 92), (0, 95)]
        return self.Ps(sym(R, 0))

    def ear_pts(self, sg):
        k = self.ear_k
        E = [(18, -88), (52, -104 - 20 * k), (80, -128 - 36 * k), (90, -134 - 38 * k), (96, -118 - 30 * k), (104, -60), (78, -80)]
        return self.Ps([(sg * x, y) for x, y in E])

    def body_pts(self):
        w = self.body_w
        R = [(0, 70), (70 * w, 76), (118 * w, 112), (150 * w, 170), (172 * w, 250), (184 * w, 340), (190 * w, 420), (0, 420)]
        return self.Ps(sym(R, 0)[:-1] if False else sym(R, 0))

    def draw(self, marks_head=None, marks_body=None, marks_ear=None, under_head=None, over_face=None, extra_body=None):
        u, s = self.u, self.s
        base, dark, light = self.coat
        o = []
        flow = radial(*self.P(0, 30))
        if self.body:
            bp = self.body_pts()
            o.append(fur(u, bp, self.coat, self.seed, lambda x, y: 90 + (x - self.cx) * 0.18, shade=(-16 * s, 0), shade_op=0.4,
                         length=(10 * s, 26 * s), width=(1.2, 3), ink_w=2.4, ink_col=self.ink_c, ink_op=0.65, hi=(self.cx - 70 * s, self.cy + 200 * s, 40 * s, 80 * s),
                         hi_op=0.25, extra_in=(marks_body(self) if marks_body else ""), density=1.0))
            if self.long:
                o.append(feather([p for p in closed_curve(bp, 6) if p[1] < self.cy + 380 * s], [base, light, dark], self.seed + 1, 2,
                                 (8 * self.long, 18 * self.long), (2, 3.6), down=0.6, cx=self.cx, cy=self.cy + 300 * s))
            if extra_body:
                o.append(extra_body(self))
        if under_head:
            o.append(under_head(self))
        for sg in (-1, 1):
            ep = self.ear_pts(sg)
            o.append(fur(u, ep, self.coat, self.seed + 3 + sg, -90 + sg * 20, shade=(sg * 6 * s, 0), length=(6 * s, 14 * s), width=(1, 2.4),
                         ink_w=2.4, ink_col=self.ink_c, extra_in=(marks_ear(self, sg) if marks_ear else "")))
            inner = self.Ps([(sg * x, y) for x, y in [(30, -86), (58, -104 - 18 * self.ear_k), (84, -124 - 32 * self.ear_k), (90, -100 - 20 * self.ear_k), (92, -66)]])
            o.append(form(u, smooth_closed(inner), bbox(inner, 2), self.ear_in[0], self.ear_in[1], self.ear_in[2], self.seed + 5 + sg, -90 + sg * 20, n=12,
                          shade=(sg * 4 * s, 4 * s), ink_w=0))
            # ear furnishings: pale hairs sweeping out of the ear
            ex, ey = self.P(sg * 60, -86)
            o.append("".join(ink(f"M {_f(ex + sg * k * 4 * s)} {_f(ey + k * 2 * s)} q {_f(sg * 6 * s)} {_f(-14 * s)} {_f(sg * (2 + k) * 4 * s)} {_f(-26 * s - k * 4 * s)}",
                                 "#FFF6EA", 1.4, self.seed + k, 1, 0.75) for k in range(3)))
            if self.tufts_ear:
                tx, ty = self.P(sg * 92, -134 - 38 * self.ear_k)
                o.append(taper([(tx, ty + 8 * s), (tx + sg * 3 * s, ty - 8 * s), (tx + sg * 2 * s, ty - 22 * s)], 7 * s, 0.8, dark, 0.95))
        hp = self.head_pts()
        o.append(fur(u, hp, self.coat, self.seed + 7, flow, shade=(12 * s, 10 * s), shade_op=0.35, hi=(self.cx - 40 * s, self.cy - 60 * s, 34 * s, 20 * s),
                     hi_op=0.3, length=(6 * s, 15 * s), width=(1, 2.4), ink_w=2.4, ink_col=self.ink_c, density=1.6 * self.flow_k,
                     extra_in=(marks_head(self) if marks_head else "")))
        # cheek fluff
        o.append(feather([p for p in closed_curve(hp, 6) if p[1] > self.cy - 10 * s and abs(p[0] - self.cx) > 60 * s],
                         [base, light, dark] if not self.long else [base, light, base, dark], self.seed + 8, 2 if not self.long else 1,
                         (5 * s * (1 + self.long), 11 * s * (1 + self.long)), (1.6, 3), down=0.35, cx=self.cx, cy=self.cy))
        # muzzle pads, chin
        for sg in (-1, 1):
            o.append(fur(u, blob_pts(*self.P(sg * 17, 46), 22 * s, 16 * s, self.seed + 9 + sg, 0.06, 14), (self.muzzle, mix(self.muzzle, "#000000", 0.15), "#FFFFFF"),
                         self.seed + 9 + sg, radial(*self.P(0, 40)), shade=(0, 4 * s), shade_op=0.2, ink_w=0, length=(3 * s, 8 * s), width=(0.8, 1.6),
                         n=24, hi=None))
        o.append(f'<path d="{blob(*self.P(0, 70), 22 * s, 13 * s, self.seed + 11, 0.08, 12)}" fill="{self.chin}" opacity="0.9"/>')
        # eyes
        for sg in (-1, 1):
            ex, ey = self.P(sg * 44, -14)
            if self.blink:
                o.append(ink(f"M {_f(ex - 18 * s)} {_f(ey - 2 * s)} Q {_f(ex)} {_f(ey + 12 * s)} {_f(ex + 18 * s)} {_f(ey - 2 * s)}", "#24140A", 4 * s, self.seed + sg, 2, 1))
                o.append(ink(f"M {_f(ex + sg * 18 * s)} {_f(ey - 2 * s)} l {_f(sg * 6 * s)} {_f(-4 * s)}", "#24140A", 2.2 * s, self.seed, 1, 1))
            else:
                o.append(eye(u, ex, ey, 22 * s, 17 * s, self.eyes, self.seed + 12 + sg, look=self.look, rot=sg * -10, slit=self.slit,
                             pupil_k=self.pupil_k, rim=mix(dark, "#000000", 0.3)))
        o.append(cat_nose(u, *self.P(0, 30), 22 * s, self.nose, self.seed + 14))
        o.append(cat_mouth(*self.P(0, 38), 15 * s, "#4A2A2A", self.seed + 15, max(1.6, 2 * s)))
        if over_face:
            o.append(over_face(self))
        for sg in (-1, 1):
            o.append(whiskers(*self.P(sg * 30, 46), sg, 9, 100 * s, self.whisk, 1.6, self.seed + 16 + sg))
            for k in range(3):
                bx, by = self.P(sg * (16 + k * 9), 44 + (k % 2) * 7)
                o.append(f'<circle cx="{_f(bx)}" cy="{_f(by)}" r="{_f(1.4 * s)}" fill="{mix(dark, "#000000", 0.2)}" opacity="0.6"/>')
        return "".join(o)


# ================================================================ designs
# ---------------------------------------------------------------- golden retriever — golden hour portrait
@design("golden-retriever")
def golden_retriever():
    u = Ids("golden-retriever")
    o = [sky(u, [(0, "#F4C489"), (0.45, "#F8DDA9"), (1, "#F2B47A")], ["#FBE6C0", "#F0B37A", "#F8D29A"], 11, n=140)]
    o.append(glow(u, 300, 330, 300, "#FFF2C8", 0.75))
    o.append(glow(u, 300, 330, 120, "#FFFBEA", 0.6))
    # sun rays
    for i in range(14):
        a = math.radians(-180 + i * 360 / 14 + 6)
        o.append(f'<path d="M 300 330 L {_f(300 + 520 * math.cos(a - 0.05))} {_f(330 + 520 * math.sin(a - 0.05))} L {_f(300 + 520 * math.cos(a + 0.05))} {_f(330 + 520 * math.sin(a + 0.05))} Z" fill="#FFF6DA" opacity="0.18"/>')
    # meadow at the bottom
    o.append(form(u, smooth_open([(-20, 500), (120, 486), (300, 494), (480, 482), (620, 496)]) + " L 620 620 L -20 620 Z", (-20, 480, 620, 620),
                  "#C8A050", "#94702E", "#E8C878", 12, -90, n=300, length=(8, 24), width=(1, 2.6), shade=None, ink_w=0))
    rnd = random.Random(3)
    for i in range(18):
        x = rnd.choice([rnd.uniform(40, 150), rnd.uniform(450, 560)])
        y = rnd.uniform(500, 570)
        o.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{rnd.uniform(2.5, 4):.1f}" fill="{rnd.choice(["#FFF4DA", "#F2D06A", "#E88A5A"])}"/>')
    gold = ("#D99A48", "#A4622A", "#F4C67C")
    inkc = "#6A3812"
    # chest (bleeds off the bottom), feathered
    chest = [(226, 420), (188, 452), (160, 500), (140, 560), (128, 640), (472, 640), (460, 560), (440, 500), (412, 452), (374, 420)]
    o.append(fur(u, chest, gold, 20, lambda x, y: 90 + (x - 300) * 0.3, shade=(-16, 0), length=(14, 34), width=(1.4, 3.4), ink_w=2.2, ink_col=inkc,
                 ink_op=0.5, hi=(300, 560, 80, 60), hi_op=0.3, curve=0.5))
    o.append(feather([p for p in closed_curve(chest, 6) if p[1] < 600], [gold[0], gold[2], "#C88A40"], 21, 2, (10, 22), (2, 3.6), down=0.7, cx=300, cy=560))
    # bandana
    o.append(bandana(u, (212, 446), (388, 446), (300, 542), ("#2E6E78", "#1A4650", "#5E9EA4"), 22, "dots", "#FBEFD8", sag=14))
    # head
    R = [(300, 196), (340, 199), (374, 212), (398, 236), (410, 268), (410, 300), (400, 330), (382, 352), (368, 374), (362, 400), (348, 422), (326, 436), (300, 440)]
    head = sym(R)
    o.append(fur(u, head, gold, 23, radial(300, 372), shade=(14, 10), shade_op=0.35, hi=(266, 236, 50, 24), hi_op=0.35,
                 length=(8, 20), width=(1.2, 2.8), ink_w=2.4, ink_col=inkc, density=1.4))
    o.append(feather([p for p in closed_curve(head, 6) if 290 < p[1] < 380], [gold[0], gold[2], gold[1]], 24, 2, (8, 16), (1.8, 3.2), down=0.5, cx=300, cy=320))
    # muzzle: long and deep, lighter, with a soft stop between the eyes
    mz = [(300, 300), (318, 304), (334, 326), (352, 352), (362, 384), (356, 414), (336, 432), (300, 438), (264, 432), (244, 414), (238, 384), (248, 352), (266, 326), (282, 304)]
    o.append(f'<path d="{smooth_closed([(300 + (x - 300) * 1.12, 372 + (y - 372) * 1.08) for x, y in mz])}" fill="#EDC48A" opacity="0.45"/>')
    o.append(fur(u, mz, ("#EDC48A", "#C8904E", "#FBE2B4"), 27, radial(300, 372), shade=(8, 10), shade_op=0.3, ink_w=0, length=(5, 14), width=(1, 2.2),
                 density=1.3, hi=(286, 330, 10, 22), hi_op=0.4))
    o.append(ink("M 282 300 Q 270 330 252 352 M 318 300 Q 330 330 348 352", gold[1], 2, 25, 1, 0.35))
    # forehead furrow and brows
    o.append(ink("M 300 232 Q 302 256 300 282", gold[1], 2.2, 25, 1, 0.45))
    for sg in (-1, 1):
        o.append(ink(f"M {300 + sg * 24} 268 Q {300 + sg * 42} 256 {300 + sg * 62} 266", inkc, 2.2, 26 + sg, 1, 0.5))
    # ears: set at brow level, folded over at the top, feathered
    for sg, seed in ((1, 30), (-1, 34)):
        E = [(368, 216), (404, 210), (434, 228), (454, 270), (462, 322), (456, 372), (440, 406), (420, 418), (404, 404), (400, 366), (404, 324), (406, 286), (398, 250), (384, 228)]
        if sg < 0:
            E = mirror(E)
        o.append(fur(u, E, ("#C98A3E", "#8E5222", "#E8B46A"), seed, lambda x, y: 95 + sg * 8, shade=(sg * 10, 0), shade_op=0.45,
                     hi=(300 + sg * 128, 270, 14, 30), hi_op=0.3, length=(14, 34), width=(1.4, 3.2), curve=0.5, ink_w=2.4, ink_col=inkc))
        o.append(ink(smooth_open([(300 + sg * 84, 230), (300 + sg * 108, 226), (300 + sg * 132, 236), (300 + sg * 146, 256)]), inkc, 2, seed, 1, 0.45))
        lower = [p for p in closed_curve(E, 6) if p[1] > 330]
        o.append(feather(lower, ["#C98A3E", "#D9A050", "#A86A2E", "#E8B46A"], seed + 1, 1, (8, 18), (1.8, 3.2), down=0.8, cx=300 + sg * 430, cy=330))
    # eyes
    o.append(eye(u, 258, 290, 15, 12, ("#8A4A1C", "#3A1A08"), 40, look=(0.15, 0.1), rot=-8, rim="#5A2E12"))
    o.append(eye(u, 342, 290, 15, 12, ("#8A4A1C", "#3A1A08"), 41, look=(0.15, 0.1), rot=8, rim="#5A2E12"))
    # open smile and tongue
    o.append(f'<path d="{smooth_closed([(258, 398), (280, 404), (300, 402), (320, 404), (342, 398), (332, 420), (300, 432), (268, 420)])}" fill="#4A1E14"/>')
    o.append(tongue(u, 300, 408, 34, 46, 42))
    o.append(ink("M 300 388 L 300 402 M 300 402 Q 280 410 258 396 M 300 402 Q 320 410 342 396", "#2A140A", 2.6, 43, 2, 0.95))
    o.append(muzzle_dots(270, 388, -1, "#8A5A2A", 44) + muzzle_dots(330, 388, 1, "#8A5A2A", 45))
    o.append(dog_nose(u, 300, 372, 46, seed=46))
    # cheek blush of light from the sun
    o.append(glow(u, 246, 330, 30, "#FFE2A8", 0.3))
    # lettering
    o.append(title(u, 300, 112, "Golden Retriever", SERIF_IT, 70, "#6A2E10", ["#4A1E08", "#8A4420", "#A85A2A"], 50, max_w=480,
                   shadow="#FBE8C4", soff=(0.025, 0.04), angle=-35))
    o.append(ruled(u, 152, "GOLDEN HOUR, EVERY HOUR", JOS, 19, "#8A4A1E", 51, ls=4, line_w=30))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ---------------------------------------------------------------- labrador — black lab in a gilt oval portrait frame
def gilt_oval(u, cx, cy, rx, ry, w, seed):
    d = f"M {cx - rx} {cy} A {rx} {ry} 0 1 0 {cx + rx} {cy} A {rx} {ry} 0 1 0 {cx - rx} {cy} Z"
    dg, g = lgrad(u, [(0, "#FBE6A0"), (0.35, "#D8A84A"), (0.65, "#B8862E"), (1, "#7A5218")], 0, 0, 1, 1)
    out = [dg, f'<ellipse cx="{cx}" cy="{cy + 6}" rx="{rx + w * 0.6}" ry="{ry + w * 0.6}" fill="none" stroke="#2A1A0A" stroke-width="{w}" opacity="0.25"/>',
           f'<path d="{d}" fill="none" stroke="{g}" stroke-width="{w}"/>']
    rnd = random.Random(seed)
    for k in range(70):
        a = 2 * math.pi * k / 70
        x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
        out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{w * 0.16:.1f}" fill="{"#FFF0B8" if math.sin(a) < 0.2 else "#C8963A"}" opacity="0.8"/>')
    for sgn, op in ((-0.36, 0.8), (0.36, 0.8)):
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx + sgn * w}" ry="{ry + sgn * w}" fill="none" stroke="#5A3A10" stroke-width="2" opacity="{op}"/>')
    out.append(f'<path d="M {cx - rx * 0.9:.1f} {cy - ry * 0.45:.1f} A {rx} {ry} 0 0 1 {cx - rx * 0.2:.1f} {cy - ry * 0.98:.1f}" fill="none" stroke="#FFF6D0" stroke-width="{w * 0.18:.1f}" stroke-linecap="round" opacity="0.6"/>')
    out.append(brush((cx - rx - w, cy - ry - w, cx + rx + w, cy + ry + w), ["#FFF0B8", "#8A5A18"], seed, 60, 0, (8, 18), (1, 2), (0.15, 0.3), 0.3))
    return "".join(out)


@design("labrador")
def labrador():
    u = Ids("labrador")
    o = [bg(u, "#A8B496", ["#98A684", "#B8C2A6", "#8E9C7A"], 61, angle=-80)]
    # painted damask wallpaper
    rnd = random.Random(62)
    for gy in range(0, 640, 60):
        for gx in range(0 + (30 if (gy // 60) % 2 else 0), 640, 60):
            x, y = gx + rnd.uniform(-2, 2), gy + rnd.uniform(-2, 2)
            o.append(f'<g opacity="0.5" fill="#7E8E6A"><path d="M {x} {y - 14} Q {x + 8} {y - 4} {x} {y + 14} Q {x - 8} {y - 4} {x} {y - 14} Z"/>'
                     f'<path d="M {x - 14} {y} Q {x - 4} {y - 6} {x} {y} Q {x - 4} {y + 6} {x - 14} {y} Z M {x + 14} {y} Q {x + 4} {y - 6} {x} {y} Q {x + 4} {y + 6} {x + 14} {y} Z"/>'
                     f'<circle cx="{x}" cy="{y - 20}" r="2.2"/><circle cx="{x}" cy="{y + 20}" r="2.2"/></g>')
    o.append(vignette(u, "#3A4A30", 0.4, 0.5))
    cx, cy, rx, ry = 300, 252, 150, 184
    o.append(shadow(u, cx + 8, cy + 12, rx + 24, ry + 24, 0.35))
    clip = u("ov")
    o.append(f'<clipPath id="{clip}"><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/></clipPath><g clip-path="url(#{clip})">')
    o.append(sky(u, [(0, "#E8BE70"), (0.6, "#D49A50"), (1, "#A86A30")], ["#F2CC86", "#C8884A", "#E0A860"], 63, n=90, angle=-70))
    o.append(glow(u, 260, 170, 140, "#FFF0C0", 0.55))
    coat = ("#2E2A2A", "#121010", "#6E6C76")
    inkc = "#0A0606"
    tints = ["#4A4852", "#0E0C0C", "#2A2626", "#3A3638", "#1A1818", "#56545E"]
    chest = [(238, 330), (204, 362), (176, 420), (160, 480), (150, 560), (450, 560), (440, 480), (424, 420), (396, 362), (362, 330)]
    o.append(fur(u, chest, coat, 64, lambda x, y: 90 + (x - 300) * 0.3, shade=(-14, 0), length=(12, 30), width=(1.4, 3.2), ink_w=1.6, ink_col=inkc, tints=tints, sop=(0.2, 0.45)))
    o.append(collar(u, [(208, 356), (250, 372), (300, 378), (350, 372), (392, 356)], 20, ("#C8382A", "#7A1A12", "#F07A5A"), 65, studs=None,
                    tag=("bone", GOLD_TAG), tag_at=0.5))
    R = [(300, 126), (338, 128), (370, 140), (392, 164), (402, 196), (402, 230), (394, 258), (380, 282), (368, 306), (360, 328), (346, 346), (324, 356), (300, 358)]
    head = sym(R)
    o.append(fur(u, head, coat, 66, radial(300, 292), shade=(14, 10), shade_op=0.4, length=(6, 16), width=(1.1, 2.6),
                 ink_w=1.8, ink_col=inkc, tints=tints, density=1.5, sop=(0.2, 0.45)))
    for (hx, hy, hrx, hry, hr) in ((270, 160, 34, 12, -14), (332, 160, 26, 9, 12), (300, 250, 7, 26, 0), (230, 250, 10, 24, 20), (372, 250, 8, 20, -20)):
        o.append(f'<path d="{blob(hx, hy, hrx, hry, hx, 0.15, 12, rot=hr)}" fill="#8A8C9C" opacity="0.14"/>')
    mz = [(300, 220), (318, 226), (334, 250), (350, 278), (356, 306), (348, 332), (328, 348), (300, 354), (272, 348), (252, 332), (244, 306), (250, 278), (266, 250), (282, 226)]
    o.append(fur(u, mz, ("#38343A", "#141212", "#7A7884"), 67, radial(300, 292), shade=(8, 10), shade_op=0.35, ink_w=0, length=(4, 11), width=(1, 2),
                 tints=tints, density=1.4))
    o.append(ink("M 284 222 Q 268 252 250 280 M 316 222 Q 332 252 350 280", "#7A7884", 1.8, 68, 1, 0.4))
    for sg in (-1, 1):
        o.append(ink(f"M {300 + sg * 22} 196 Q {300 + sg * 40} 184 {300 + sg * 60} 194", "#8A8A96", 2.2, 69 + sg, 1, 0.45))
    for sg, seed in ((1, 70), (-1, 72)):
        E = [(376, 146), (404, 148), (422, 170), (428, 212), (420, 252), (404, 282), (386, 290), (380, 262), (386, 222), (388, 182)]
        if sg < 0:
            E = mirror(E)
        o.append(fur(u, E, ("#242022", "#0A0808", "#5A5862"), seed, lambda x, y: 95 + sg * 10, shade=(sg * 8, 0), shade_op=0.45, length=(10, 22),
                     width=(1.2, 2.6), ink_w=1.8, ink_col=inkc, tints=tints))
    o.append(eye(u, 262, 218, 13, 11, ("#B8702E", "#5A2C10"), 74, look=(0.1, 0.1), rot=-8, rim="#0A0606"))
    o.append(eye(u, 338, 218, 13, 11, ("#B8702E", "#5A2C10"), 75, look=(0.1, 0.1), rot=8, rim="#0A0606"))
    o.append(ink("M 300 306 L 300 320 M 300 320 Q 284 330 266 320 M 300 320 Q 316 330 334 320", "#050303", 2.6, 76, 2, 0.95))
    o.append(ink("M 270 326 Q 300 344 330 326", "#6E6C76", 1.6, 77, 1, 0.5))
    o.append(muzzle_dots(272, 308, -1, "#8A8A96", 78) + muzzle_dots(328, 308, 1, "#8A8A96", 79))
    o.append(dog_nose(u, 300, 292, 44, ("#1E1A1A", "#050404", "#5A5660"), seed=80))
    o.append("</g>")
    o.append(gilt_oval(u, cx, cy, rx, ry, 18, 81))
    # name ribbon over the bottom of the frame, and the motto
    o.append(ribbon(u, 300, 452, 330, 58, ("#F6ECD6", "#CDB894", "#FFFFFF"), 82, tail=40, bend=10))
    o.append(ribbon_text(300, 446, "LABRADOR", JOS, 44, "#7A1E14", 300, 10, ls=6, u=u))
    o.append(ruled(u, 528, "LOYAL TO THE BONE", MONO, 19, "#FBF3E4", 83, ls=5, line_w=36, line="#F6E6C0"))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ---------------------------------------------------------------- tabby cat — the M on the forehead
@design("tabby-cat")
def tabby_cat():
    u = Ids("tabby-cat")
    o = [bg(u, "#CDD6BE", ["#BCC8AA", "#DCE2CE", "#B4C0A0"], 91, angle=-15)]
    o.append(spot(u, 300, 380, 230, 200, "#E8E0C8", ["#F2ECDA", "#DCD2B8"], 92, op=0.85))
    coat = ("#A88A6A", "#5A4432", "#E2CFB2")
    stripe = "#3A2A1E"

    def head_marks(c):
        P = c.P
        out = []
        # the "M"
        out.append(taper([P(-36, -40), P(-30, -60), P(-22, -78)], 9, 3, stripe, 0.9))
        out.append(taper([P(-22, -76), P(-12, -60), P(0, -48)], 6, 7, stripe, 0.9))
        out.append(taper([P(0, -48), P(12, -60), P(22, -76)], 7, 6, stripe, 0.9))
        out.append(taper([P(22, -78), P(30, -60), P(36, -40)], 3, 9, stripe, 0.9))
        for x in (-12, 0, 12):
            out.append(taper([P(x * 1.1, -60 if x else -54), P(x * 1.3, -80), P(x * 1.5, -100)], 6, 3, stripe, 0.85))
        for x in (-34, 34):
            out.append(taper([P(x, -84), P(x * 1.15, -96)], 5, 2, stripe, 0.7))
        for sg in (-1, 1):
            out.append(taper([P(sg * 64, -10), P(sg * 86, -4), P(sg * 112, 8)], 6, 2, stripe, 0.85))
            out.append(taper([P(sg * 60, 14), P(sg * 86, 22), P(sg * 114, 34)], 6, 2, stripe, 0.8))
            out.append(taper([P(sg * 70, 40), P(sg * 92, 48), P(sg * 108, 56)], 4, 1.5, stripe, 0.6))
            # pale rims round the eyes
            out.append(f'<path d="{blob(*P(sg * 44, -12), 30 * c.s, 24 * c.s, 95 + sg, 0.06, 14)}" fill="#F2E6D0" opacity="0.55"/>')
        return "".join(out)

    def body_marks(c):
        P = c.P
        out = [f'<path d="{blob(*P(0, 210), 70 * c.s, 150 * c.s, 96, 0.08, 16)}" fill="#F4ECE0" opacity="0.92"/>']
        for sg in (-1, 1):
            for k, x in enumerate((84, 114, 142, 168)):
                y0 = 92 + k * 14
                out.append(taper([P(sg * x, y0), P(sg * (x + 12), y0 + 34), P(sg * (x + 4), y0 + 70)], 9, 3, stripe, 0.75))
                out.append(taper([P(sg * (x + 2), y0 + 92), P(sg * (x + 16), y0 + 130), P(sg * (x + 8), y0 + 170)], 8, 2, stripe, 0.7))
            out.append(taper([P(sg * 40, 110), P(sg * 60, 150), P(sg * 70, 200)], 6, 2, stripe, 0.4))
        return "".join(out)

    def ear_marks(c, sg):
        return ""

    cat = Cat(u, 300, 372, 1.0, coat, 97, eyes=("#E2D86A", "#7A9A2A"), look=(0.05, 0.05), muzzle="#F6EEE2")
    o.append(cat.draw(head_marks, body_marks, ear_marks))
    o.append(shadow(u, 120, 548, 70, 12, 0.3))
    o.append(yarn(u, 118, 508, 42, ("#D8605A", "#9A2E2A", "#F29A8A"), 101, tail=[(150, 530), (190, 552), (230, 540), (270, 560), (320, 548)]))
    o.append(collar(u, [(212, 452), (254, 466), (300, 470), (346, 466), (388, 452)], 16, ("#E8783A", "#A8461A", "#F8B070"), 98,
                    tag=("round", GOLD_TAG), tag_at=0.5))
    o.append(title(u, 300, 126, "Tabby", DMS, 112, "#4A3020", ["#3A2414", "#6E4A30", "#8A6040"], 99, max_w=330,
                   shadow="#F4EEDC", soff=(0.025, 0.035), angle=-60))
    o.append(ruled(u, 168, "M IS FOR MEOW", JOS, 21, "#5E7A3A", 100, ls=6, line_w=36))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ---------------------------------------------------------------- dachshund — the long and short of it, in a striped sweater
@design("dachshund")
def dachshund():
    u = Ids("dachshund")
    o = [bg(u, "#CFE3E0", ["#BED8D4", "#E2EEEA", "#B2CEC8"], 111, angle=-10)]
    # painted floor
    o.append(form(u, smooth_open([(-20, 420), (300, 414), (620, 420)]) + " L 620 620 L -20 620 Z", (-20, 410, 620, 620), "#E8C89A", "#C09868", "#F6E2C0", 112, 0,
                  n=260, length=(40, 120), width=(2, 5), shade=None, ink_w=0))
    for y in (448, 488, 534, 588):
        o.append(ink(f"M -10 {y} Q 300 {y - 3} 610 {y}", "#B88A5A", 1.6, y, 1, 0.45))
    o.append(shadow(u, 296, 432, 210, 14, 0.4))
    coat = ("#B8582A", "#7A3014", "#E8925A")
    inkc = "#4A1A08"
    tints = ["#E8925A", "#7A3014", "#C8683A", "#F2A870"]
    # tail
    tl = catmull([(138, 324), (116, 308), (100, 286), (94, 262)], 6)
    o.append(taper(tl, 18, 4, coat[0]) + taper([(x - 2, y) for x, y in tl], 6, 1.5, coat[2], 0.6))
    o.append(ink(smooth_open([(136, 318), (112, 300), (98, 278), (94, 262)]), inkc, 1.6, 113, 1, 0.5))
    far = ("#8A3C18", "#5A2208", "#B8582A")
    # far legs (in shadow)
    o.append(fur(u, [(400, 370), (424, 372), (426, 404), (420, 422), (436, 430), (432, 438), (404, 438), (404, 420), (400, 396)], far, 131, 90, shade=None,
                 length=(6, 12), ink_w=1.6, ink_col=inkc, n=24, tints=tints))
    o.append(fur(u, [(176, 356), (204, 364), (206, 392), (200, 420), (214, 430), (208, 438), (180, 438), (182, 418), (178, 390)], far, 132, 90, shade=None,
                 length=(6, 12), ink_w=1.6, ink_col=inkc, n=24, tints=tints))
    # one continuous body: rump, long back, neck, deep keel chest, tucked belly
    body = [(126, 352), (132, 322), (156, 304), (200, 298), (260, 300), (330, 300), (390, 296), (420, 286), (440, 266), (458, 250), (478, 262), (484, 300),
            (478, 330), (472, 354), (460, 380), (438, 396), (400, 400), (360, 396), (300, 386), (250, 380), (210, 380), (176, 386), (146, 382), (128, 370)]
    o.append(fur(u, body, coat, 114, lambda x, y: (0 if x < 420 else -40) + (8 if y > 360 else 0), shade=(0, 14), shade_op=0.4, length=(14, 30), width=(1.4, 3),
                 hi=(260, 310, 140, 9), hi_op=0.35, ink_w=2.4, ink_col=inkc, tints=tints))
    # near legs: round thigh + short crooked front leg with turned-out paw
    hind = [(130, 346), (168, 336), (196, 356), (192, 388), (180, 416), (196, 428), (190, 438), (154, 438), (154, 418), (142, 396), (128, 372)]
    o.append(fur(u, hind, coat, 115, lambda x, y: 100 if y > 390 else 60, shade=(6, 8), shade_op=0.35, length=(8, 18), ink_w=2.2, ink_col=inkc, tints=tints,
                 hi=(156, 356, 14, 8), hi_op=0.35))
    front = [(430, 358), (458, 362), (462, 392), (452, 418), (470, 428), (466, 438), (432, 438), (432, 418), (428, 392)]
    o.append(fur(u, front, coat, 116, 90, shade=(4, 0), length=(6, 14), ink_w=2.2, ink_col=inkc, n=40, tints=tints))
    for x in (160, 438):
        o.append(ink(f"M {x + 10} 438 l 0 -6 M {x + 18} 438 l 0 -5", inkc, 1.4, x, 1, 0.7))
    # glossy short coat: a long sheen along the back, darker belly
    o.append(f'<path d="{blob(290, 312, 130, 7, 133, 0.12, 16)}" fill="#F8B888" opacity="0.4"/>')
    o.append(f'<path d="{blob(420, 300, 24, 6, 134, 0.12, 12, rot=-40)}" fill="#F8B888" opacity="0.35"/>')
    o.append(ink(smooth_open([(214, 380), (300, 386), (380, 396)]), "#5A2208", 2, 135, 1, 0.35))
    # collar with a little heart tag
    o.append(collar(u, [(424, 274), (438, 304), (456, 336)], 13, ("#2E6E78", "#1A4650", "#5E9EA4"), 136, tag=("heart", ("#E8B84A", "#9A6A1A", "#FFE8A0")), tag_at=0.92))
    # head (facing right): long muzzle, gentle stop, low-set ear
    head = [(440, 252), (458, 226), (488, 220), (508, 234), (522, 256), (538, 274), (546, 288), (540, 300), (518, 306), (492, 304), (466, 298), (448, 282)]
    o.append(fur(u, head, coat, 121, 200, shade=(0, 8), shade_op=0.35, hi=(486, 232, 22, 8), hi_op=0.4, length=(6, 14), width=(1, 2.4),
                 ink_w=2.4, ink_col=inkc, tints=tints, density=1.5))
    o.append(ink("M 498 302 Q 518 306 540 300", inkc, 1.6, 122, 1, 0.6))
    o.append(f'<path d="{blob(541, 285, 7.5, 6.5, 123, 0.08, 10)}" fill="#1E1210"/><circle cx="539" cy="282" r="2" fill="#FFFFFF" opacity="0.7"/>')
    o.append(eye(u, 494, 250, 8.5, 7.5, ("#7A3A14", "#2A1206"), 124, look=(0.4, 0), rot=10, rim="#5A1E08"))
    o.append(ink("M 484 242 Q 494 236 506 240", inkc, 1.6, 125, 1, 0.6))
    ear = [(456, 238), (478, 242), (486, 270), (482, 304), (470, 330), (450, 334), (444, 302), (448, 262)]
    o.append(fur(u, ear, ("#8E3E18", "#5A2208", "#C8683A"), 126, 95, shade=(-6, 0), length=(8, 18), ink_w=2.2, ink_col=inkc, tints=tints, hi=(468, 270, 6, 18), hi_op=0.3))
    o.append(muzzle_dots(518, 292, 1, "#5A2208", 127, n=4))
    # lettering
    o.append(title(u, 300, 140, "Dachshund", DMS, 116, "#7A2E14", ["#5A1E0A", "#9A4422", "#B8582A"], 128, max_w=460,
                   shadow="#F6FBF8", soff=(0.025, 0.035), angle=-60))
    o.append(ruled(u, 186, "THE ORIGINAL", JOS, 18, "#3E6A64", 129, ls=7, line_w=40))
    o.append(title(u, 300, 520, "WIENER DOG", BEBAS, 76, "#C8382A", ["#A8261A", "#E8584A", "#8E1E14"], 130, max_w=400, ls=8,
                   shadow="#7A3014", soff=(0.02, 0.035), angle=-80, hi="#FFD0B8"))
    o.append(finish(u, op=0.8))
    return "".join(o)


# @@DESIGNS@@


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
