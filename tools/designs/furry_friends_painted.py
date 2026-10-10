"""Furry Friends, hand-painted (gouache / storybook) edition.

The whole 30-piece collection: the six original Furry Friends sayings repainted, plus breed portraits and little
storybook scenes for dog and cat people (dachshund, golden, corgi, pit bull, chihuahua, husky, beagle, frenchie,
basset, border collie, pom, tabby, tuxedo, siamese, calico, black, orange and grey cats...). Every piece is gouache on warm paper: organic shapes, washes with pooled edges, fur painted
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
    size = fit_size(s, font, size, w * 0.9, ls)
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


#<<CAT
# ================================================================ a painted cat (front portrait), shared by the cat designs
class Cat:
    """Front-facing cat head with an optional bust. Local units around the point between the eyes (cx, cy), scale s
    (head ~ 220 wide at s=1). coat = (base, dark, light). mouth: 'w' | 'smile' | 'meow' | 'flat'.
    Hooks draw markings clipped inside head / body / ears; patch() paints a fur-textured colour patch."""

    def __init__(self, u, cx, cy, s, coat, seed, ink_c="#3A2418", eyes=("#C8D86A", "#6E8A2A"), eye_r=24, eye_x=42, eye_y=0, look=(0.06, 0.08),
                 slit=False, pupil_k=0.6, blink=False, ear_in=("#E8A8A0", "#B86A6A", "#F8D0C8"), ear_k=1.0, ear_w=1.0, ear_rot=0,
                 nose=("#E8A0A0", "#B8606A", "#F8D0CC"), cheek=1.0, top=-82, chin=80, muzzle="#F4ECE2", muzzle_op=0.92, chin_c=None,
                 long=0.0, body=True, body_w=1.0, body_len=360, tilt=0, whisk="#FFFFFF", rim=None, mouth="w", density=1.6, eye_rot=8,
                 lid=None, brow=True, ear_tuft=False, body_coat=None):
        self.__dict__.update(locals())
        del self.__dict__["self"]
        self.chin_c = chin_c or muzzle
        self.body_coat = body_coat or coat

    def P(self, x, y):
        return (self.cx + x * self.s, self.cy + y * self.s)

    def Ps(self, pts):
        return [self.P(x, y) for x, y in pts]

    def head_local(self):
        c, t = self.cheek, self.top
        R = [(0, t), (34, t + 2), (64, t + 12), (88, t + 32), (102 * c, -12), (110 * c, 18), (104 * c, 44), (84 * c, 66), (52, self.chin - 4), (0, self.chin)]
        return sym(R, 0)

    def ear_local(self, sg):
        k, w, t = self.ear_k, self.ear_w, self.top
        E = [(20, t + 6), (40 + 4 * w, t - 30 * k), (62 + 10 * w, t - 62 * k), (72 + 14 * w, t - 70 * k), (82 + 16 * w, t - 58 * k),
             (98 + 12 * w, t - 10 * k), (104, t + 50), (70, t + 30)]
        E = rot_pts(E, 62, t + 10, self.ear_rot)
        return [(sg * x, y) for x, y in E]

    def ear_inner_local(self, sg):
        k, w, t = self.ear_k, self.ear_w, self.top
        E = [(36, t + 8), (50 + 5 * w, t - 22 * k), (66 + 10 * w, t - 50 * k), (74 + 13 * w, t - 56 * k), (82 + 14 * w, t - 44 * k),
             (90 + 10 * w, t - 6 * k), (88, t + 26)]
        E = rot_pts(E, 62, t + 10, self.ear_rot)
        return [(sg * x, y) for x, y in E]

    def body_local(self):
        w, L = self.body_w, self.body_len
        R = [(0, 40), (70 * w, 52), (104 * w, 96), (124 * w, 160), (138 * w, 240), (146 * w, 320)]
        R = [p for p in R if p[1] < L - 10] + [(R[-1][0] if L > 320 else 130 * w, L), (0, L)]
        return sym(R, 0)

    def patch(self, pts, pal, seed, flow=None, length=None, soft=True, n=None):
        s = self.s
        pp = self.Ps(pts)
        flow = flow if flow is not None else radial(*self.P(0, 30))
        L = length or (5 * s, 13 * s)
        out = [fur(self.u, pp, pal, seed, flow, shade=None, ink_w=0, length=L, width=(1, 2.2), density=1.5, n=n)]
        if soft:
            out.append(feather(closed_curve(pp, 6), [pal[0], pal[2], pal[0]], seed + 1, 3, (2 * s, 5 * s), (1, 1.8), down=0.15, op=(0.35, 0.7)))
        return "".join(out)

    def stripes(self, color, seed, kind="tabby", op=0.85):
        """Forehead 'M', cheek stripes and brow lines (head hook helper)."""
        P = self.P
        s = self.s
        out = []
        out.append(taper([P(-30, -36), P(-26, -54), P(-18, -70)], 8 * s, 3 * s, color, op))
        out.append(taper([P(-18, -68), P(-9, -54), P(0, -44)], 5 * s, 6 * s, color, op))
        out.append(taper([P(0, -44), P(9, -54), P(18, -68)], 6 * s, 5 * s, color, op))
        out.append(taper([P(18, -70), P(26, -54), P(30, -36)], 3 * s, 8 * s, color, op))
        for x in (-10, 0, 10):
            out.append(taper([P(x * 1.1, -56 if x else -50), P(x * 1.3, -70), P(x * 1.5, -84)], 5 * s, 2 * s, color, op * 0.9))
        for sg in (-1, 1):
            out.append(taper([P(sg * 66, -6), P(sg * 86, 0), P(sg * 108, 10)], 6 * s, 2 * s, color, op))
            out.append(taper([P(sg * 62, 18), P(sg * 86, 26), P(sg * 110, 36)], 6 * s, 2 * s, color, op * 0.9))
            out.append(taper([P(sg * 72, 42), P(sg * 90, 50), P(sg * 102, 56)], 4 * s, 1.5 * s, color, op * 0.7))
            out.append(taper([P(sg * 58, -2), P(sg * 70, 6), P(sg * 84, 8)], 3 * s, 1 * s, color, op * 0.7))
        return "".join(out)

    def draw(self, marks_head=None, marks_body=None, marks_ear=None, under_head=None, over_face=None, over_body=None, behind=None, paws=None):
        u, s = self.u, self.s
        base, dark, light = self.coat
        ic = self.ink_c
        o = [f'<g transform="rotate({self.tilt} {_f(self.cx)} {_f(self.cy + 60 * s)})">' if self.tilt else "<g>"]
        if behind:
            o.append(behind(self))
        if self.body:
            bp = self.Ps(self.body_local())
            bc = self.body_coat
            o.append(fur(u, bp, bc, self.seed, lambda x, y: 90 + (x - self.cx) * 0.2, shade=(-14 * s, 0), shade_op=0.38,
                         length=(10 * s * (1 + self.long), 24 * s * (1 + self.long)), width=(1.2, 3), ink_w=2.4, ink_col=ic, ink_op=0.6,
                         hi=(self.cx - 50 * s, self.cy + 220 * s, 34 * s, 80 * s), hi_op=0.22, extra_in=(marks_body(self) if marks_body else "")))
            o.append(feather([p for p in closed_curve(bp, 6) if self.cy + 80 * s < p[1] < self.cy + (self.body_len - 30) * s], [bc[0], bc[2], bc[1]],
                             self.seed + 1, 2, (6 * s * (1 + self.long * 1.5), 13 * s * (1 + self.long * 1.5)), (1.8, 3.2), down=0.6, cx=self.cx,
                             cy=self.cy + 260 * s))
            if self.rim:
                o.append(ink(smooth_open([p for p in closed_curve(bp, 6) if p[0] > self.cx + 60 * s and self.cy + 60 * s < p[1] < self.cy + (self.body_len - 20) * s]),
                             self.rim, 3 * s, self.seed, 1, 0.55))
        if over_body:
            o.append(over_body(self))
        if paws:
            o.append(paws(self))
        if under_head:
            o.append(under_head(self))
        for sg in (-1, 1):
            ep = self.Ps(self.ear_local(sg))
            o.append(fur(u, ep, self.coat, self.seed + 3 + sg, -90 + sg * 20, shade=(sg * 7 * s, 0), length=(6 * s, 14 * s), width=(1, 2.4),
                         ink_w=2.4, ink_col=ic, extra_in=(marks_ear(self, sg) if marks_ear else "")))
            ip = self.Ps(self.ear_inner_local(sg))
            o.append(form(u, smooth_closed(ip), bbox(ip, 2), self.ear_in[0], self.ear_in[1], self.ear_in[2], self.seed + 5 + sg, -90 + sg * 20, n=18,
                          shade=(sg * 5 * s, 6 * s), shade_op=0.5, ink_w=0))
            bx, by = self.P(sg * 62, self.top + 22)
            tx, ty = ip[3]
            o.append("".join(ink(f"M {_f(bx + sg * (k - 1.5) * 6 * s)} {_f(by)} Q {_f(bx + (tx - bx) * 0.4 + sg * (k - 1.5) * 4 * s)} {_f(by + (ty - by) * 0.3)} "
                                 f"{_f(bx + (tx - bx) * (0.55 + 0.06 * k))} {_f(by + (ty - by) * (0.55 + 0.06 * k))}", "#FFF6EA", 1.4 * s, self.seed + k, 1, 0.7)
                             for k in range(4)))
            if self.ear_tuft:
                tx, ty = self.P(sg * (72 + 14 * self.ear_w), self.top - 70 * self.ear_k)
                o.append(taper([(tx, ty + 8 * s), (tx + sg * 3 * s, ty - 8 * s), (tx + sg * 2 * s, ty - 20 * s)], 6 * s, 0.8, dark, 0.95))
        hp = self.Ps(self.head_local())
        o.append(fur(u, hp, self.coat, self.seed + 7, radial(*self.P(0, 30)), shade=(12 * s, 10 * s), shade_op=0.33,
                     hi=(self.P(-30, -50)[0], self.P(0, -50)[1], 34 * s, 18 * s), hi_op=0.3, length=(6 * s, 14 * s), width=(1, 2.4), ink_w=2.4, ink_col=ic,
                     density=self.density, extra_in=(marks_head(self) if marks_head else "")))
        o.append(feather([p for p in closed_curve(hp, 6) if p[1] > self.cy - 14 * s and abs(p[0] - self.cx) > 56 * s],
                         [base, light, dark, base], self.seed + 8, 2 if not self.long else 1, (5 * s * (1 + self.long * 1.6), 11 * s * (1 + self.long * 1.6)),
                         (1.6, 3), down=0.35, cx=self.cx, cy=self.cy))
        o.append(tufts([p for p in closed_curve(hp, 6) if p[1] <= self.cy - 14 * s], [base, light, base], self.seed + 9, 3, (2 * s, 5 * s), (1.1, 2.2),
                       cx=self.cx, cy=self.cy))
        if self.rim:
            o.append(ink(smooth_open([p for p in closed_curve(hp, 6) if p[0] > self.cx + 30 * s and p[1] < self.cy + 50 * s]), self.rim, 2.6 * s, self.seed + 2, 1, 0.6))
        # whisker pads, chin
        mz = self.muzzle
        for sg in (-1, 1):
            o.append(fur(u, blob_pts(*self.P(sg * 16, 46), 21 * s, 15 * s, self.seed + 9 + sg, 0.06, 14), (mz, mix(mz, "#000000", 0.15), mix(mz, "#FFFFFF", 0.4)),
                         self.seed + 9 + sg, radial(*self.P(0, 40)), shade=(0, 4 * s), shade_op=0.22, ink_w=0, length=(3 * s, 8 * s), width=(0.8, 1.6), n=26))
            for k in range(3):
                bx, by = self.P(sg * (14 + k * 8), 44 + (k % 2) * 7)
                o.append(f'<circle cx="{_f(bx)}" cy="{_f(by)}" r="{_f(1.4 * s)}" fill="{mix(dark, "#000000", 0.2)}" opacity="0.55"/>')
        o.append(f'<path d="{blob(*self.P(0, 66), 18 * s, 10 * s, self.seed + 11, 0.08, 12)}" fill="{self.chin_c}" opacity="0.9"/>')
        # eyes
        for sg in (-1, 1):
            ex, ey = self.P(sg * self.eye_x, self.eye_y)
            r = self.eye_r * s
            if self.blink:
                o.append(ink(f"M {_f(ex - r * 0.85)} {_f(ey - 2 * s)} Q {_f(ex)} {_f(ey + r * 0.55)} {_f(ex + r * 0.85)} {_f(ey - 2 * s)}", "#24140A", 3.6 * s, self.seed + sg, 2, 1))
                o.append(ink(f"M {_f(ex + sg * r * 0.85)} {_f(ey - 2 * s)} l {_f(sg * 5 * s)} {_f(-4 * s)}", "#24140A", 2 * s, self.seed, 1, 1))
            else:
                o.append(eye(u, ex, ey, r, r * 0.82, self.eyes, self.seed + 12 + sg, look=self.look, rot=sg * -self.eye_rot, slit=self.slit,
                             pupil_k=self.pupil_k, rim=mix(dark, "#000000", 0.3)))
                if self.lid:
                    lc, lk = self.lid   # heavy-lidded (unimpressed) look: a lid wash over the top of the eye
                    pts = [(ex - r * 1.08, ey - r * 0.05), (ex - r * 0.5, ey - r * (0.95 - lk)), (ex + r * 0.5, ey - r * (0.95 - lk)), (ex + r * 1.08, ey - r * 0.05),
                           (ex + r * 0.5, ey - r * 1.2), (ex - r * 0.5, ey - r * 1.2)]
                    pts = rot_pts(pts, ex, ey, sg * -self.eye_rot)
                    o.append(f'<path d="{smooth_closed(pts)}" fill="{lc}"/>')
                    o.append(ink(smooth_open(pts[:4]), "#24140A", 2.6 * s, self.seed + sg, 2, 0.95))
            if self.brow:
                o.append("".join(ink(f"M {_f(ex - sg * 2 * s + k * sg * 7 * s)} {_f(ey - r * 1.2)} q {_f(sg * 4 * s)} {_f(-10 * s)} {_f(sg * 2 * s + k * sg * 4 * s)} {_f(-22 * s - k * 3 * s)}",
                                     self.whisk, 1.3 * s, self.seed + 30 + k, 1, 0.6) for k in range(2)))
        o.append(cat_nose(u, *self.P(0, 30), 20 * s, self.nose, self.seed + 14))
        mc = "#4A2A2A"
        if self.mouth == "meow":
            mp = self.Ps([(-14, 46), (0, 42), (14, 46), (10, 60), (0, 64), (-10, 60)])
            o.append(f'<path d="{smooth_closed(mp)}" fill="#5A1E22"/>' + f'<path d="{blob(*self.P(0, 58), 7 * s, 4 * s, self.seed, 0.1, 8)}" fill="#E07A84"/>')
            o.append(ink(f"M {_f(self.P(0, 36)[0])} {_f(self.P(0, 36)[1])} L {_f(self.P(0, 42)[0])} {_f(self.P(0, 42)[1])}", mc, 2 * s, self.seed, 2, 0.9))
            o.append(ink(smooth_closed(mp), mc, 1.8 * s, self.seed + 1, 1, 0.9))
        elif self.mouth == "flat":
            o.append(ink(smooth_open(self.Ps([(0, 36), (0, 44)])), mc, 2 * s, self.seed, 2, 0.9))
            o.append(ink(smooth_open(self.Ps([(-13, 50), (-5, 46), (0, 44), (5, 46), (13, 50)])), mc, 2 * s, self.seed + 1, 2, 0.9))
        else:
            w = 15 if self.mouth == "w" else 17
            o.append(cat_mouth(*self.P(0, 36), w * s, mc, self.seed + 15, max(1.6, 2 * s)))
        if over_face:
            o.append(over_face(self))
        for sg in (-1, 1):
            o.append(whiskers(*self.P(sg * 30, 46), sg, 9, 104 * s, self.whisk, 1.6, self.seed + 16 + sg))
        o.append("</g>")
        return "".join(o)
#CAT>>


#<<DOG
# ================================================================ a painted dog (front portrait), shared by the dog designs
class Dog:
    """Front-facing dog head with optional chest. Local units around the point between the eyes (cx, cy), scale s.
    coat = (base, dark, light). ears: 'drop' | 'hound' | 'prick' | 'bat' | 'rose' | 'button' | 'none'.
    mouth: 'smile' | 'open' | 'grin' | 'closed'. kind: 'smooth' | 'medium' | 'fluffy' (edge tufts, stroke length).
    Hooks draw markings clipped inside head / muzzle / chest / ears."""

    def __init__(self, u, cx, cy, s, coat, seed, ink_c="#3A2418", skull=74, cheek=84, top=-86, dome=6, nose_y=58, muzzle_w=36, stop_w=13,
                 jowl=None, chin=None, ears="drop", ear_coat=None, ear_len=1.0, ear_w=1.0, ear_rot=0, ear_in=("#E8A898", "#B86A60", "#F8D0C4"),
                 ear_x=0, ear_y=0, eye_x=38, eye_r=14, eyes=("#B47434", "#4A2208"), look=(0.08, 0.12), eye_rot=6, muzzle=None, mouth="smile",
                 tongue=True, nose=("#2E2018", "#140C08", "#6A5448"), nose_w=None, chest=True, chest_w=1.0, chest_coat=None, brows=None,
                 kind="medium", fluff=0.0, ear_fluff=0.0, density=1.4, tilt=0, wrinkles=0, flews=0.0, puff=1.0,
                 tongue_pal=("#E8707A", "#B8404E", "#F8A8AE"), stroke_len=1.0, blink=False, lid=None, chest_len=330, neck=0.92, mouth_w=1.0,
                 cheek_shade=0.22, eye_patch=None, face_tufts=None, round_top=0.0):
        self.__dict__.update(locals())
        del self.__dict__["self"]
        self.jowl = jowl if jowl is not None else muzzle_w + 18
        self.chin = chin if chin is not None else nose_y + 44
        self.ear_coat = ear_coat or coat
        self.chest_coat = chest_coat or coat
        self.nose_w = nose_w or muzzle_w * 1.0
        self.muzzle = muzzle or (mix(coat[0], coat[2], 0.55), coat[0], mix(coat[2], "#FFFFFF", 0.35))

    def P(self, x, y):
        return (self.cx + x * self.s, self.cy + y * self.s)

    def Ps(self, pts):
        return [self.P(x, y) for x, y in pts]

    # ---- shapes (local units)
    def head_local(self):
        k, c, t, ny, j = self.skull, self.cheek, self.top, self.nose_y, self.jowl
        rt = self.round_top
        R = [(0, t - self.dome), (k * 0.5, t + 1 + 8 * rt), (k * 0.86, t + 15 + 18 * rt), (k * 1.0, t + 42 + 14 * rt), (c, -4), (c * 0.98, 22),
             (c * 0.5 + j * 0.5, ny * 0.7), (j, ny + 8), (j * 0.86, ny + 30), (j * 0.5, self.chin - 4), (0, self.chin)]
        return sym(R, 0)

    def muzzle_local(self):
        m, ny, sw = self.muzzle_w, self.nose_y, self.stop_w
        R = [(0, -14), (sw, -12), (m * 0.66, ny * 0.42), (m * 0.98, ny - 6), (m * 1.04, ny + 14), (m * 0.88, ny + 30), (m * 0.5, self.chin - 3),
             (0, self.chin - 1)]
        return sym(R, 0)

    def ear_local(self, sg):
        k, t, L, W = self.skull, self.top, self.ear_len, self.ear_w
        e = self.ears
        if e == "drop":
            E = [(k * 0.42, t + 6), (k * 0.84 + 6 * W, t + 2), (k + 24 * W, t + 22), (k + 36 * W, t + 66 * L), (k + 36 * W, t + 112 * L),
                 (k + 24 * W, t + 138 * L), (k + 4, t + 134 * L), (k - 8, t + 104 * L), (k - 8, t + 58), (k * 0.68, t + 24)]
        elif e == "hound":
            E = [(k * 0.6, t + 24), (k + 10 * W, t + 20), (k + 32 * W, t + 52), (k + 42 * W, t + 110 * L), (k + 40 * W, t + 160 * L),
                 (k + 24 * W, t + 184 * L), (k + 2, t + 170 * L), (k - 10, t + 122 * L), (k - 12, t + 72), (k * 0.8, t + 42)]
        elif e == "prick":
            E = [(k * 0.16, t + 8), (k * 0.36 + 4 * W, t - 30 * L), (k * 0.58 + 10 * W, t - 66 * L), (k * 0.7 + 13 * W, t - 74 * L),
                 (k * 0.82 + 16 * W, t - 62 * L), (k * 0.98 + 18 * W, t - 26 * L), (k * 1.06 + 10 * W, t + 20), (k * 0.9, t + 46), (k * 0.5, t + 30)]
        elif e == "bat":
            E = [(k * 0.3, t + 16), (k * 0.36, t - 26 * L), (k * 0.52, t - 66 * L), (k * 0.78 + 8 * W, t - 82 * L), (k * 1.02 + 22 * W, t - 74 * L),
                 (k * 1.16 + 28 * W, t - 42 * L), (k * 1.14 + 20 * W, t - 4), (k * 1.0, t + 36)]
        elif e == "rose":
            E = [(k * 0.46, t + 8), (k * 0.68, t - 12 * L), (k * 0.94 + 8 * W, t - 18 * L), (k + 24 * W, t - 4 * L), (k + 34 * W, t + 14 * L),
                 (k + 26 * W, t + 26 * L), (k + 10, t + 22), (k * 0.84, t + 18)]
        elif e == "button":
            E = [(k * 0.34, t + 8), (k * 0.62, t - 14 * L), (k * 0.96 + 8 * W, t - 10 * L), (k + 20 * W, t + 12 * L), (k + 14 * W, t + 42 * L),
                 (k * 0.9, t + 50 * L), (k * 0.76, t + 32), (k * 0.5, t + 18)]
        else:
            return None
        E = rot_pts(E, k * 0.62, t + 14, self.ear_rot)
        return [(sg * (x + self.ear_x), y + self.ear_y) for x, y in E]

    def ear_inner_local(self, sg):
        k, t, L, W = self.skull, self.top, self.ear_len, self.ear_w
        if self.ears == "prick":
            E = [(k * 0.3, t + 10), (k * 0.44 + 5 * W, t - 24 * L), (k * 0.62 + 10 * W, t - 56 * L), (k * 0.71 + 12 * W, t - 63 * L),
                 (k * 0.8 + 14 * W, t - 52 * L), (k * 0.92 + 15 * W, t - 20 * L), (k * 0.96 + 8 * W, t + 14), (k * 0.7, t + 26)]
        elif self.ears == "bat":
            E = [(k * 0.44, t + 8), (k * 0.48, t - 24 * L), (k * 0.6, t - 56 * L), (k * 0.8 + 7 * W, t - 70 * L), (k * 0.98 + 18 * W, t - 64 * L),
                 (k * 1.06 + 22 * W, t - 38 * L), (k * 1.04 + 14 * W, t - 4), (k * 0.9, t + 22)]
        elif self.ears == "rose":
            E = [(k * 0.72, t + 4), (k * 0.86, t - 8 * L), (k + 12 * W, t - 8 * L), (k + 24 * W, t + 6 * L), (k + 16 * W, t + 14 * L), (k * 0.92, t + 12)]
        else:
            return None
        E = rot_pts(E, k * 0.62, t + 14, self.ear_rot)
        return [(sg * (x + self.ear_x), y + self.ear_y) for x, y in E]

    def chest_local(self):
        w, c, ny, L = self.chest_w, self.cheek, self.nose_y, self.chest_len
        R = [(0, 0), (c * 0.8, 0), (c * self.neck, ny * 0.5 + 30), (c * self.neck * 1.04, ny + 46), (c * 1.2 * w, ny + 96), (c * 1.56 * w, ny + 160), (c * 1.82 * w, ny + 240),
             (c * 1.9 * w, ny + L), (0, ny + L)]
        return sym(R, 0)


    # ---- marking helpers (use inside hooks; local coordinates)
    def patch(self, pts, pal, seed, flow=None, soft=True, length=None, n=None):
        """A fur-painted colour patch (blaze, mask, bib) with a soft feathered edge."""
        s = self.s
        pp = self.Ps(pts)
        flow = flow if flow is not None else radial(*self.P(0, self.nose_y * 0.6))
        L = length or (5 * s * self.stroke_len, 13 * s * self.stroke_len)
        out = [fur(self.u, pp, pal, seed, flow, shade=None, ink_w=0, length=L, width=(1, 2.2), density=1.4, n=n)]
        if soft:
            out.append(feather(closed_curve(pp, 6), [pal[0], pal[2], pal[0]], seed + 1, 3, (2 * s, 5 * s), (1, 1.8), down=0.15, op=(0.35, 0.7)))
        return "".join(out)

    def blaze(self, pal, seed, w_top=8, w_mid=14, top_off=14):
        t, ny, m = self.top, self.nose_y, self.muzzle_w
        R = [(0, t + top_off), (w_top, t + top_off + 4), (w_top * 0.8, -30), (w_mid, -14), (m * 0.7, ny * 0.5), (m * 1.02, ny), (m * 1.0, ny + 30),
             (m * 0.5, self.chin), (0, self.chin + 4)]
        return self.patch(sym(R, 0), pal, seed)

    def bib(self, pal, seed, w=0.7, top=None):
        ny = self.nose_y
        top = top if top is not None else ny + 30
        c = self.cheek
        R = [(0, top), (c * 0.5 * w, top + 4), (c * 0.8 * w, top + 60), (c * 0.95 * w, top + 150), (c * 0.7 * w, top + 260), (0, top + 300)]
        return self.patch(sym(R, 0), pal, seed, flow=lambda x, y: 90 + (x - self.cx) * 0.3, length=(10 * self.s, 24 * self.s))

    # ---- drawing
    def _ears(self, marks_ear):
        u, s, ic, sl = self.u, self.s, self.ink_c, self.stroke_len
        out = []
        for sg in (-1, 1):
            el = self.ear_local(sg)
            if not el:
                continue
            ep = self.Ps(el)
            ec = self.ear_coat
            down = self.ears in ("drop", "hound")
            flow = (lambda x, y, sg=sg: 92 + sg * 6) if down else (lambda x, y, sg=sg: -90 + sg * 22)
            hx = self.P(sg * (self.skull + 18 * self.ear_w), 0)[0]
            e_svg = [fur(u, ep, ec, self.seed + 3 + sg, flow, shade=(sg * 9 * s, 0), shade_op=0.45, length=(8 * s * sl, 22 * s * sl), width=(1.2, 2.8),
                         ink_w=2.4, ink_col=ic, curve=0.4 if down else 0.2, density=1.3,
                         hi=(hx, self.P(0, self.top + 52)[1], 9 * s, 26 * s) if down else None, hi_op=0.25,
                         extra_in=(marks_ear(self, sg) if marks_ear else ""))]
            il = self.ear_inner_local(sg)
            if il:
                ip = self.Ps(il)
                e_svg.append(form(u, smooth_closed(ip), bbox(ip, 2), self.ear_in[0], self.ear_in[1], self.ear_in[2], self.seed + 5 + sg, -90 + sg * 20,
                                  n=24, shade=(sg * 6 * s, 7 * s), shade_op=0.5, ink_w=0))
                if self.ears in ("prick", "bat"):
                    # pale furnishings growing from the inner rim of the ear
                    bx, by = self.P(sg * self.skull * 0.95, self.top + 14)
                    tx, ty = ip[len(ip) // 2]
                    e_svg.append("".join(ink(f"M {_f(bx - sg * k2 * 5 * s)} {_f(by + k2 * 3 * s)} Q {_f((bx + tx) / 2 + sg * 4 * s)} {_f((by + ty) / 2 + 8 * s)} "
                                             f"{_f(bx + (tx - bx) * (0.45 + 0.08 * k2))} {_f(by + (ty - by) * (0.45 + 0.08 * k2))}",
                                             mix(self.ear_coat[2], "#FFFFFF", 0.4), 1.6 * s, self.seed + k2, 1, 0.75) for k2 in range(4)))
            if self.ear_fluff and down:
                lower = [p for p in closed_curve(ep, 6) if p[1] > self.P(0, self.top + 50 * self.ear_len)[1]]
                e_svg.append(feather(lower, [ec[0], ec[2], ec[1], ec[0]], self.seed + 7 + sg, 1, (6 * self.ear_fluff * s, 15 * self.ear_fluff * s), (1.8, 3.2),
                                     down=0.85, cx=self.P(-sg * 300, 0)[0], cy=self.P(0, self.top + 60)[1]))
            if down:
                a, b = el[1], el[2]
                e_svg.append(ink(smooth_open(self.Ps([el[0], ((a[0] + b[0]) / 2, a[1] + 5), (b[0], b[1] + 10)])), ic, 1.8, self.seed + sg, 1, 0.4))
            out.append("".join(e_svg))
        return out

    def draw(self, marks_head=None, marks_muzzle=None, marks_chest=None, marks_ear=None, under_head=None, over_face=None, over_chest=None,
             behind=None):
        u, s = self.u, self.s
        base, dark, light = self.coat
        ic, sl = self.ink_c, self.stroke_len
        ny, m = self.nose_y, self.muzzle_w
        tuftc = [base, light, dark, base]
        o = [f'<g transform="rotate({self.tilt} {_f(self.cx)} {_f(self.cy + 60 * s)})">' if self.tilt else "<g>"]
        if behind:
            o.append(behind(self))
        if self.chest:
            cp = self.Ps(self.chest_local())
            cb = self.chest_coat
            o.append(fur(u, cp, cb, self.seed, lambda x, y: 90 + (x - self.cx) * 0.22, shade=(-14 * s, 0), shade_op=0.35,
                         length=(10 * s * sl, 26 * s * sl), width=(1.2, 3), ink_w=2.4, ink_col=ic, ink_op=0.6,
                         hi=(self.cx - 46 * s, self.cy + (ny + 170) * s, 34 * s, 70 * s), hi_op=0.2, curve=0.4,
                         extra_in=(marks_chest(self) if marks_chest else "")))
            if self.kind != "smooth" or self.fluff:
                fl = max(self.fluff, 0.5 if self.kind == "medium" else 1.0)
                o.append(feather([p for p in closed_curve(cp, 6) if p[1] < self.cy + (ny + self.chest_len - 30) * s and p[1] > self.cy + (ny + 30) * s],
                                 [cb[0], cb[2], cb[1]], self.seed + 1, 2, (8 * fl * s, 18 * fl * s), (2, 3.6), down=0.65, cx=self.cx,
                                 cy=self.cy + (ny + 250) * s))
        if over_chest:
            o.append(over_chest(self))
        if under_head:
            o.append(under_head(self))
        back = self.ears in ("prick", "bat", "rose", "button")
        ears = self._ears(marks_ear)
        if back:
            o += ears
        hl = self.head_local()
        hp = self.Ps(hl)
        hc = self.P(0, ny * 0.6)

        def head_in(_):
            r = []
            # cheek shading beside the muzzle, darker eye sockets, soft forehead light
            for sg in (-1, 1):
                r.append(f'<path d="{blob(*self.P(sg * (m + 20), ny * 0.45), 22 * s, 34 * s, self.seed + 60 + sg, 0.1, 12)}" fill="{dark}" opacity="{self.cheek_shade}"/>')
                if self.eye_patch:
                    pc, po = self.eye_patch
                    r.append(f'<path d="{blob(*self.P(sg * self.eye_x, 2), self.eye_r * 1.9 * s, self.eye_r * 1.6 * s, self.seed + 62 + sg, 0.12, 12, rot=sg * 20)}" fill="{pc}" opacity="{po}"/>')
            r.append(f'<path d="{blob(*self.P(-10, self.top + 34), 40 * s, 20 * s, self.seed + 64, 0.1, 12)}" fill="{light}" opacity="0.25"/>')
            return "".join(r) + (marks_head(self) if marks_head else "")

        o.append(fur(u, hp, self.coat, self.seed + 9, radial(*hc), shade=(12 * s, 10 * s), shade_op=0.32,
                     length=(6 * s * sl, 15 * s * sl), width=(1, 2.4), ink_w=2.4, ink_col=ic, density=self.density, extra_in=head_in(self)))
        ft = self.face_tufts if self.face_tufts is not None else self.kind
        if ft != "smooth":
            fl = 1 + (self.fluff if ft == "fluffy" else 0)
            dense = closed_curve(hp, 7)
            o.append(feather([p for p in dense if p[1] > self.cy - 10 * s], tuftc, self.seed + 10, 2 if ft == "medium" else 1,
                             (5 * s * fl, 11 * s * fl), (1.6, 3), down=0.35, cx=hc[0], cy=hc[1]))
            o.append(tufts([p for p in dense if p[1] <= self.cy - 10 * s], tuftc, self.seed + 11, 3, (3 * s, 7 * s * fl), (1.2, 2.4), cx=hc[0], cy=hc[1]))
        # muzzle
        mp = self.Ps(self.muzzle_local())
        mc = self.muzzle
        o.append(f'<path d="{smooth_closed([(hc[0] + (x - hc[0]) * 1.14, hc[1] + (y - hc[1]) * 1.08) for x, y in mp])}" fill="{mc[0]}" opacity="0.35"/>')
        o.append(fur(u, mp, mc, self.seed + 12, radial(*self.P(0, ny)), shade=(7 * s, 9 * s), shade_op=0.28, ink_w=0,
                     length=(4 * s * sl, 11 * s * sl), width=(0.9, 2), density=1.3,
                     hi=(self.P(-5, ny * 0.38)[0], self.P(0, ny * 0.38)[1], 6 * s, 15 * s), hi_op=0.4,
                     extra_in=(marks_muzzle(self) if marks_muzzle else "")))
        for sg in (-1, 1):
            o.append(ink(smooth_open(self.Ps([(sg * self.stop_w * 0.9, -8), (sg * m * 0.7, ny * 0.44), (sg * m * 0.98, ny * 0.86)])), dark, 1.6 * s, self.seed + 13 + sg, 1, 0.28))
        if self.wrinkles:
            for k in range(self.wrinkles):
                y = ny * 0.15 - 6 - k * 11
                o.append(ink(smooth_open(self.Ps([(-24 + k * 4, y + 5), (-9, y - 1), (0, y + 3), (9, y - 1), (24 - k * 4, y + 5)])), dark, 2.2 * s, self.seed + 30 + k, 1, 0.5))
        # mouth, lip puffs, chin
        mw = m * self.mouth_w
        mt = ny + self.nose_w * 0.3
        pd = 15 * self.puff
        if self.mouth in ("open", "grin"):
            depth = 34 if self.mouth == "open" else 20
            wide = 0.92 if self.mouth == "open" else 1.0
            cav = self.Ps([(-mw * wide, mt + pd * 0.7), (-mw * 0.55, mt + pd + depth * 0.7), (0, mt + pd + depth), (mw * 0.55, mt + pd + depth * 0.7),
                           (mw * wide, mt + pd * 0.7), (0, mt + pd * 0.6)])
            o.append(f'<path d="{smooth_closed(cav)}" fill="#3E1412"/>')
            o.append(f'<path d="{blob(*self.P(0, mt + pd + depth * 0.45), mw * 0.6 * s, depth * 0.3 * s, self.seed + 70, 0.1, 12)}" fill="#7A2A2A" opacity="0.6"/>')
            if self.tongue:
                tw = mw * (0.95 if self.mouth == "open" else 0.75)
                th = (depth + 30) if self.mouth == "open" else depth + 4
                o.append(tongue(u, self.cx, self.cy + (mt + pd + depth * 0.35) * s, tw * s, th * s, self.seed + 40, self.tongue_pal))
            o.append(ink(smooth_closed(cav), "#2A0E0A", 2 * s, self.seed + 71, 1, 0.7))
        # lip puffs (upper lip either side of the philtrum)
        for sg in (-1, 1):
            pp = blob_pts(*self.P(sg * mw * 0.48, mt + pd * 0.55), mw * 0.56 * s, pd * 0.95 * s, self.seed + 72 + sg, 0.05, 14, rot=-sg * 8)
            o.append(fur(u, pp, mc, self.seed + 74 + sg, radial(*self.P(0, mt)), shade=(0, 5 * s), shade_op=0.32, ink_w=0, n=int(40 * s),
                         length=(3 * s, 8 * s), width=(0.8, 1.6), hi=None))
            o.append(ink(smooth_open([pp[i] for i in (1, 2, 3, 4, 5, 6, 7, 8)] if sg > 0 else [pp[i] for i in (10, 9, 8, 7, 6, 5, 4, 3)]), mix(dark, "#000000", 0.2),
                         1.4 * s, self.seed + 76 + sg, 1, 0.35))
            o.append(muzzle_dots(*self.P(sg * mw * 0.32, mt + pd * 0.45), sg, mix(dark, "#000000", 0.3), self.seed + 50 + sg, 1.3 * s, 5))
        if self.mouth in ("smile", "closed"):
            up = -4 if self.mouth == "smile" else 3
            for sg in (-1, 1):
                o.append(ink(smooth_open(self.Ps([(0, mt + pd * 0.9), (sg * mw * 0.3, mt + pd * 1.35), (sg * mw * 0.68, mt + pd * 1.3), (sg * mw * 0.98, mt + pd * 0.9 + up)])),
                             "#2A140A", 2.4 * s, self.seed + 43 + sg, 2, 0.9))
            if self.flews:
                for sg in (-1, 1):
                    o.append(ink(smooth_open(self.Ps([(sg * mw * 0.96, mt + pd * 0.9), (sg * mw * 1.08, mt + pd * (1 + 0.8 * self.flews)), (sg * mw * 0.7, mt + pd * (1.3 + 0.9 * self.flews))])),
                                 dark, 2 * s, self.seed + 45 + sg, 1, 0.45))
        elif self.mouth == "howl":
            # a round 'O' - singing / howling
            oc = self.Ps([(-mw * 0.36, mt + pd * 1.0), (0, mt + pd * 0.8), (mw * 0.36, mt + pd * 1.0), (mw * 0.3, mt + pd * 1.0 + 26), (0, mt + pd * 1.0 + 34),
                          (-mw * 0.3, mt + pd * 1.0 + 26)])
            o.append(f'<path d="{smooth_closed(oc)}" fill="#3E1412"/>')
            o.append(f'<path d="{blob(*self.P(0, mt + pd + 22), mw * 0.2 * s, 7 * s, self.seed + 70, 0.1, 10)}" fill="#E8707A"/>')
            o.append(ink(smooth_closed(oc), "#2A0E0A", 2.2 * s, self.seed + 71, 2, 0.85))
        else:
            for sg in (-1, 1):
                o.append(ink(smooth_open(self.Ps([(0, mt + pd * 0.55), (sg * mw * 0.35, mt + pd * 1.05), (sg * mw * 0.75, mt + pd * 0.95), (sg * mw * 1.0, mt + pd * 0.6)])),
                             "#2A140A", 2.2 * s, self.seed + 43 + sg, 2, 0.85))
        o.append(ink(smooth_open(self.Ps([(0, mt - 2), (0, mt + pd * 0.85)])), "#2A140A", 2.2 * s, self.seed + 41, 2, 0.85))
        o.append(dog_nose(u, *self.P(0, ny), self.nose_w * s, self.nose, self.seed + 48))
        # eyes and brows
        for sg in (-1, 1):
            ex, ey = self.P(sg * self.eye_x, 0)
            if self.blink:
                o.append(ink(f"M {_f(ex - self.eye_r * s)} {_f(ey - 2 * s)} Q {_f(ex)} {_f(ey + self.eye_r * 0.8 * s)} {_f(ex + self.eye_r * s)} {_f(ey - 2 * s)}",
                             "#24140A", 3.6 * s, self.seed + sg, 2, 1))
                o.append(ink(f"M {_f(ex + sg * self.eye_r * s)} {_f(ey - 2 * s)} l {_f(sg * 5 * s)} {_f(-4 * s)}", "#24140A", 2 * s, self.seed, 1, 1))
            else:
                o.append(eye(u, ex, ey, self.eye_r * s, self.eye_r * 0.88 * s, self.eyes, self.seed + 14 + sg, look=self.look, rot=sg * self.eye_rot,
                             rim=mix(dark, "#000000", 0.35), pupil_k=0.52))
                if self.lid:
                    o.append(ink(f"M {_f(ex - self.eye_r * 1.05 * s)} {_f(ey - self.eye_r * 0.2 * s)} Q {_f(ex)} {_f(ey - self.eye_r * 1.3 * s)} "
                                 f"{_f(ex + self.eye_r * 1.05 * s)} {_f(ey - self.eye_r * 0.2 * s)}", self.lid, 1.6 * s, self.seed + sg, 1, 0.5))
            if self.brows:
                bc, bo = self.brows
                o.append(f'<path d="{blob(ex - sg * 3 * s, ey - self.eye_r * 1.75 * s, 8.5 * s, 5.5 * s, self.seed + 20 + sg, 0.12, 10, rot=sg * 16)}" fill="{bc}" opacity="{bo}"/>')
            o.append(ink(f"M {_f(ex - sg * 13 * s)} {_f(ey - self.eye_r * 1.5 * s)} Q {_f(ex - sg * 2 * s)} {_f(ey - self.eye_r * 2.05 * s)} {_f(ex + sg * 11 * s)} {_f(ey - self.eye_r * 1.7 * s)}",
                         mix(dark, "#000000", 0.2), 2 * s, self.seed + 22 + sg, 1, 0.4))
        if over_face:
            o.append(over_face(self))
        if not back:
            o += ears
        o.append("</g>")
        return "".join(o)
#DOG>>


# ================================================================ designs
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
                 ink_w=1.8, ink_col=inkc, tints=tints, density=1.5, sop=(0.2, 0.45), hi=(272, 168, 44, 18), hi_op=0.3))
    o.append(ink("M 236 186 Q 262 144 310 136", "#B8C0D8", 4, 661, 1, 0.35) + ink("M 380 200 Q 392 230 392 262", "#E8C890", 3, 662, 1, 0.3))
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
    o.append(yarn(u, 118, 508, 42, ("#D8605A", "#9A2E2A", "#F29A8A"), 101, tail=[(150, 530), (176, 548), (200, 540), (214, 552)]))
    o.append(collar(u, [(212, 452), (254, 466), (300, 470), (346, 466), (388, 452)], 16, ("#E8783A", "#A8461A", "#F8B070"), 98,
                    tag=("round", GOLD_TAG), tag_at=0.5))
    o.append(title(u, 300, 132, "Tabby", DMS, 108, "#4A3020", ["#3A2414", "#6E4A30", "#8A6040"], 99, max_w=330,
                   shadow="#F4EEDC", soff=(0.025, 0.035), angle=-60))
    o.append(ruled(u, 172, "M IS FOR MEOW", JOS, 21, "#5E7A3A", 100, ls=6, line_w=36))
    o.append(finish(u, op=0.8))
    return "".join(o)


#<<NEW
# ================================================================ more painted props
def rosette(u, cx, cy, r, pal, seed, tails=True, center=None, label=None, label_font=None, label_c="#FFFFFF"):
    """Prize rosette: pleated outer ring, inner ring, button centre, two ribbon tails."""
    base, dark, light = pal
    out = []
    if tails:
        for sg in (-1, 1):
            tp = [(cx + sg * r * 0.15, cy + r * 0.4), (cx + sg * r * 0.62, cy + r * 1.9), (cx + sg * r * 0.42, cy + r * 1.7), (cx + sg * r * 0.3, cy + r * 1.98),
                  (cx - sg * r * 0.2, cy + r * 0.5)]
            out.append(form(u, smooth_closed(tp), bbox(tp, 2), base, dark, light, seed + sg, -90 + sg * 14, n=r * 0.8, shade=(sg * 4, 0),
                            ink_w=1.8, ink_col=mix(dark, "#000000", 0.4)))
    pts = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        rr = r * (1.0 if i % 2 == 0 else 0.86)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    out.append(shadow(u, cx + 3, cy + 5, r * 1.05, r * 1.0, 0.25))
    out.append(form(u, smooth_closed(pts), bbox(pts, 2), base, dark, light, seed, radial(cx, cy), n=r * 2.2, shade=(r * 0.08, r * 0.1),
                    length=(r * 0.2, r * 0.4), width=(1, 2.2), ink_w=1.6, ink_col=mix(dark, "#000000", 0.4)))
    for i in range(24):
        a = 2 * math.pi * (i + 0.5) / 24
        out.append(ink(f"M {_f(cx + r * 0.62 * math.cos(a))} {_f(cy + r * 0.62 * math.sin(a))} L {_f(cx + r * 0.95 * math.cos(a))} {_f(cy + r * 0.95 * math.sin(a))}",
                       mix(dark, "#000000", 0.2), 1.2, seed + i, 1, 0.45))
    cpal = center or ("#F6EEDC", "#C8B48E", "#FFFFFF")
    cd = blob(cx, cy, r * 0.6, r * 0.6, seed + 3, 0.02, 16)
    out.append(form(u, cd, (cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6), cpal[0], cpal[1], cpal[2], seed + 3, -30, n=r, shade=(r * 0.06, r * 0.08),
                    hi=(cx - r * 0.2, cy - r * 0.25, r * 0.22, r * 0.12), hi_op=0.6, ink_w=1.6, ink_col=mix(dark, "#000000", 0.4)))
    out.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 0.48)}" fill="none" stroke="{dark}" stroke-width="1.4" stroke-dasharray="3 3" opacity="0.6"/>')
    if label:
        out.append(plain(cx, cy + r * 0.12, label, label_font or JOS, r * 0.34, label_c or dark, r * 0.9, 1))
    return "".join(out)


def tennis_ball(u, cx, cy, r, seed, rot=0):
    d = blob(cx, cy, r, r * 0.97, seed, 0.03, 16)
    out = [shadow(u, cx + r * 0.1, cy + r * 0.92, r * 0.9, r * 0.22, 0.35),
           form(u, d, (cx - r, cy - r, cx + r, cy + r), "#D8E04A", "#98A428", "#F2F49A", seed, radial(cx, cy), n=r * 5, shade=(r * 0.18, r * 0.2), shade_op=0.5,
                length=(r * 0.06, r * 0.16), width=(0.8, 1.6), hi=(cx - r * 0.35, cy - r * 0.4, r * 0.3, r * 0.2), hi_op=0.6, ink_w=1.8, ink_col="#6A7414")]
    cid = u("tb")
    seam = (f"M {_f(cx - r * 1.1)} {_f(cy - r * 0.3)} Q {_f(cx - r * 0.2)} {_f(cy - r * 0.1)} {_f(cx - r * 0.25)} {_f(cy - r * 1.1)} "
            f"M {_f(cx + r * 1.1)} {_f(cy + r * 0.3)} Q {_f(cx + r * 0.2)} {_f(cy + r * 0.1)} {_f(cx + r * 0.25)} {_f(cy + r * 1.1)}")
    out.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})" transform="rotate({rot} {_f(cx)} {_f(cy)})">'
               f'<path d="{seam}" fill="none" stroke="#FBFBEA" stroke-width="{_f(r * 0.13)}" stroke-linecap="round"/>'
               f'<path d="{seam}" fill="none" stroke="#B8C02E" stroke-width="{_f(r * 0.04)}" opacity="0.6" transform="translate(1.2 1.2)"/></g>')
    return "".join(out)


def confetti(n, seed, box, colors, avoid=None, size=(3, 7)):
    rnd = random.Random(seed)
    out = []
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if avoid and avoid(x, y):
            continue
        k = rnd.random()
        c = rnd.choice(colors)
        s = rnd.uniform(*size)
        if k < 0.4:
            out.append(sparkle(x, y, s * 1.3, c, 0.9))
        elif k < 0.7:
            out.append(f'<path d="{blob(x, y, s * 0.6, s * 0.6, rnd.randint(0, 999), 0.15, 8)}" fill="{c}" opacity="0.85"/>')
        else:
            a = rnd.uniform(0, 180)
            out.append(f'<path d="M {_f(x - s * 0.7)} {_f(y)} q {_f(s * 0.35)} {_f(-s * 0.5)} {_f(s * 0.7)} 0 t {_f(s * 0.7)} 0" stroke="{c}" stroke-width="2.4" '
                       f'fill="none" stroke-linecap="round" transform="rotate({a:.0f} {_f(x)} {_f(y)})" opacity="0.85"/>')
    return "".join(out)


ROSE_PINK = ("#EE98A4", "#C25A6E", "#FAD0D4")
ROSE_CORAL = ("#F2A27A", "#C8603E", "#FBD0B4")
ROSE_CREAM = ("#F6E2C4", "#CDAE84", "#FFF6E6")
LEAF_G = ("#7A9A5A", "#4A6A36", "#A8C27E")
LEAF_SAGE = ("#94A88A", "#5E7458", "#C0D0B2")


def rose(u, cx, cy, r, pal, seed, rot=0):
    """Painted cabbage rose: ring of cupped petals, a deeper centre and a spiral of inked petal edges."""
    base, dark, light = pal
    rnd = random.Random(seed)
    inkc = mix(dark, "#000000", 0.25)
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">', shadow(u, cx + r * 0.1, cy + r * 0.2, r * 1.1, r * 0.9, 0.22)]
    for i in range(7):
        a = 2 * math.pi * i / 7 + rnd.uniform(-0.2, 0.2)
        px, py = cx + math.cos(a) * r * 0.48, cy + math.sin(a) * r * 0.42
        d = blob(px, py, r * 0.56, r * 0.44, seed + i, 0.1, 12, rot=math.degrees(a))
        out.append(form(u, d, (px - r * 0.6, py - r * 0.6, px + r * 0.6, py + r * 0.6), base, dark, light, seed + i, math.degrees(a) + 180, n=r * 0.5,
                        shade=(math.cos(a) * -r * 0.1, math.sin(a) * -r * 0.1), shade_op=0.35, length=(r * 0.15, r * 0.35), width=(0.8, 1.6),
                        ink_w=1.2, ink_col=inkc, ink_op=0.6))
    cd = blob(cx, cy - r * 0.02, r * 0.52, r * 0.46, seed + 9, 0.08, 12)
    out.append(form(u, cd, (cx - r * 0.55, cy - r * 0.5, cx + r * 0.55, cy + r * 0.5), mix(base, dark, 0.25), dark, base, seed + 9, 60, n=r * 0.4,
                    shade=(0, -r * 0.08), ink_w=1.2, ink_col=inkc, ink_op=0.6))
    # spiral of petal edges
    for k in range(4):
        rr = r * (0.42 - k * 0.09)
        a0 = rnd.uniform(0, 6.28)
        out.append(ink(f"M {_f(cx + rr * math.cos(a0))} {_f(cy + rr * 0.85 * math.sin(a0))} A {_f(rr)} {_f(rr * 0.85)} 0 0 1 {_f(cx + rr * math.cos(a0 + 2.6))} {_f(cy + rr * 0.85 * math.sin(a0 + 2.6))}",
                       inkc, max(1, r * 0.06), seed + k, 1, 0.7))
        out.append(ink(f"M {_f(cx + rr * math.cos(a0 + 0.3))} {_f(cy - 1.5 + rr * 0.85 * math.sin(a0 + 0.3))} A {_f(rr)} {_f(rr * 0.85)} 0 0 1 {_f(cx + rr * math.cos(a0 + 1.8))} {_f(cy - 1.5 + rr * 0.85 * math.sin(a0 + 1.8))}",
                       light, max(0.8, r * 0.04), seed + k + 5, 1, 0.8))
    out.append("</g>")
    return "".join(out)


def bud(u, cx, cy, r, pal, seed, ang=-90):
    a = math.radians(ang)
    out = [ink(f"M {_f(cx)} {_f(cy)} l {_f(-math.cos(a) * r * 1.4)} {_f(-math.sin(a) * r * 1.4)}", LEAF_G[1], max(1.2, r * 0.18), seed, 1, 0.9)]
    out.append(f'<path d="{blob(cx, cy, r * 0.6, r * 0.85, seed, 0.08, 10, rot=ang + 90)}" fill="{pal[0]}"/>')
    out.append(f'<path d="{blob(cx - math.cos(a) * r * 0.3, cy - math.sin(a) * r * 0.3, r * 0.7, r * 0.45, seed + 1, 0.08, 10, rot=ang + 90)}" fill="{LEAF_G[0]}"/>')
    out.append(ink(blob(cx, cy, r * 0.6, r * 0.85, seed, 0.08, 10, rot=ang + 90), mix(pal[1], "#000000", 0.2), 1, seed, 1, 0.6))
    return "".join(out)


def wreath(u, cx, cy, R, seed, roses=(), leaf_pal=(LEAF_G, LEAF_SAGE), n_leaves=46, buds=10, berry="#C25A6E", gap=None, ry=None):
    """A painted floral wreath: two rings of leaves following the circle, little buds and berries, roses at given (angle, size, pal)."""
    from fall_gouache_b import leaf
    rnd = random.Random(seed)
    ry = ry or R
    out = []
    items = []
    for i in range(n_leaves):
        a = 2 * math.pi * i / n_leaves + rnd.uniform(-0.05, 0.05)
        if gap and gap[0] <= math.degrees(a) % 360 <= gap[1]:
            continue
        side = 1 if i % 2 else -1
        rr = R + side * rnd.uniform(6, 16)
        x, y = cx + rr * math.cos(a), cy + ry / R * rr * math.sin(a)
        rot = math.degrees(a) + 90 + side * 50 + rnd.uniform(-12, 12)
        items.append(("leaf", x, y, rnd.uniform(13, 19), rot, rnd.choice(leaf_pal), seed + i))
    for i in range(buds):
        a = rnd.uniform(0, 2 * math.pi)
        if gap and gap[0] <= math.degrees(a) % 360 <= gap[1]:
            continue
        rr = R + rnd.choice([-1, 1]) * rnd.uniform(14, 24)
        items.append(("berry", cx + rr * math.cos(a), cy + ry / R * rr * math.sin(a), rnd.uniform(3.5, 5), 0, None, seed + 100 + i))
    # vine ring
    out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{R}" ry="{ry}" fill="none" stroke="{LEAF_G[1]}" stroke-width="3" opacity="0.7"/>')
    for kind, x, y, s, rot, pal, sd in items:
        if kind == "leaf":
            out.append(leaf(u, "elm", x, y, s, rot, pal, sd, detail=True, stem=False))
        else:
            out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(s)}" fill="{berry}"/><circle cx="{_f(x - s * 0.3)}" cy="{_f(y - s * 0.3)}" r="{_f(s * 0.3)}" fill="#FFFFFF" opacity="0.7"/>')
    for a_deg, s, pal in roses:
        a = math.radians(a_deg)
        out.append(rose(u, cx + R * math.cos(a), cy + ry * math.sin(a), s, pal, seed + int(a_deg), rot=a_deg))
    return "".join(out)


# ---------------------------------------------------------------- good boy — golden retriever with his prize rosette and a tennis ball
GOLD = ("#D99A48", "#A4622A", "#F4C67C")
GOLD_EAR = ("#C98A3E", "#8E5222", "#E8B46A")


@design("good-boy")
def good_boy():
    u = Ids("good-boy")
    o = [bg(u, "#DCE6EA", ["#C8D8E0", "#EAF0F0", "#BCCFD8"], 141, angle=-30)]
    o.append(glow(u, 300, 400, 260, "#FFF6E0", 0.8))
    o.append(confetti(46, 142, (40, 230, 560, 560), ["#E8B84A", "#5A86B8", "#E8785A", "#FFFFFF"], avoid=lambda x, y: 150 < x < 450))
    d = Dog(u, 300, 352, 1.12, GOLD, 143, ink_c="#6A3812", ears="drop", ear_coat=GOLD_EAR, skull=80, cheek=90, ear_w=1.0, ear_len=1.0, ear_y=12, round_top=0.8,
            kind="fluffy", face_tufts="smooth", fluff=1.1, ear_fluff=1.0, mouth="open", nose_y=62, muzzle_w=36, tilt=-7, chest_w=1.05,
            muzzle=("#F0C890", "#C8904E", "#FCE6C0"))

    def chest_extra(dd):
        return collar(u, [(200, 520), (250, 544), (300, 552), (350, 544), (400, 520)], 18, ("#2E5E9A", "#1A3A68", "#6A96CC"), 144,
                      tag=("round", GOLD_TAG), tag_at=0.5)
    o.append(d.draw(over_chest=chest_extra))
    o.append(rosette(u, 414, 512, 34, ("#3A6EAE", "#1E4278", "#7AA6DA"), 145, label="1st", label_font=SERIF_IT, label_c="#1E4278"))
    o.append(tennis_ball(u, 118, 520, 34, 146, rot=20))
    # lettering
    o.append(title(u, 300, 110, "good", SERIF_IT, 84, "#1E3A62", ["#14284A", "#2E5486", "#3A64A0"], 147, max_w=300, shadow="#FFFFFF", soff=(0.02, 0.03), angle=-40))
    o.append(title(u, 300, 236, "BOY", ANTON, 110, "#C8642A", ["#A8461A", "#E88A4A", "#B8541E"], 148, max_w=300, ls=10, shadow="#1E3A62", soff=(0.025, 0.035),
                   angle=-75, hi="#FFD6A8"))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ---------------------------------------------------------------- dog mom — a Blenheim Cavalier inside a rose wreath, name ribbon below
CHESTNUT = ("#B8602E", "#7A3414", "#E0904E")
WHITE_COAT = ("#F6F0E6", "#D2C6B6", "#FFFFFF")


def cavalier(u, cx, cy, s, seed, tilt=0, mouth="smile", look=(0.05, 0.1)):
    d = Dog(u, cx, cy, s, CHESTNUT, seed, ink_c="#5A2A12", ears="drop", ear_coat=("#A8542A", "#6A2C10", "#D2844A"), ear_len=1.35, ear_w=1.25,
            skull=78, cheek=84, dome=14, nose_y=46, muzzle_w=32, stop_w=12, eye_x=36, eye_r=16, kind="fluffy", face_tufts="smooth", fluff=0.9,
            ear_fluff=1.7, mouth=mouth, muzzle=WHITE_COAT, chest_coat=WHITE_COAT, tilt=tilt, look=look, eyes=("#7A3E18", "#2A1006"), chin=86)

    def head(dd):
        return dd.blaze(WHITE_COAT, seed + 1, 7, 16, 8) + f'<path d="{blob(*dd.P(0, -50), 7 * s, 8 * s, seed, 0.1, 10)}" fill="#B8602E" opacity="0.9"/>'

    def ears(dd, sg):
        # wavy curls in the long ear feathering
        out = []
        x0, y0 = dd.P(sg * (dd.skull + 10), dd.top + 40)
        for k in range(5):
            out.append(ink(smooth_open([(x0 + sg * (6 + k * 7) * s, y0 + (10 + k * 4) * s), (x0 + sg * (2 + k * 7) * s, y0 + (40 + k * 6) * s),
                                        (x0 + sg * (10 + k * 7) * s, y0 + (70 + k * 6) * s), (x0 + sg * (4 + k * 7) * s, y0 + (100 + k * 6) * s)]),
                           "#E8A060", 1.6 * s, seed + k, 1, 0.55))
        return "".join(out)
    return d, dict(marks_head=head, marks_ear=ears)


@design("dog-mom")
def dog_mom():
    u = Ids("dog-mom")
    o = [bg(u, "#F4E2DA", ["#EED2C8", "#F8ECE4", "#E8C8BC"], 151, angle=-25)]
    cx, cy, R = 300, 248, 172
    # inner painted disc
    o.append(spot(u, cx, cy, R - 6, R - 6, "#FBF1E8", ["#FFF8F0", "#F2E2D6"], 152, op=1, wob=0.03))
    o.append(glow(u, cx, cy - 20, 150, "#FFFFFF", 0.6))
    clip = u("wc")
    o.append(f'<clipPath id="{clip}"><circle cx="{cx}" cy="{cy}" r="{R - 4}"/></clipPath><g clip-path="url(#{clip})">')
    d, hooks = cavalier(u, 300, 230, 1.1, 153, tilt=6)
    o.append(d.draw(**hooks))
    o.append("</g>")
    o.append(wreath(u, cx, cy, R, 154, roses=[(-160, 22, ROSE_CREAM), (-138, 30, ROSE_PINK), (-112, 18, ROSE_CORAL), (-48, 17, ROSE_CREAM),
                                             (-24, 28, ROSE_CORAL), (2, 20, ROSE_PINK), (164, 24, ROSE_CREAM), (138, 17, ROSE_PINK)],
                    gap=(70, 110), n_leaves=74, buds=22))
    # ribbon with the name
    o.append(ribbon(u, 300, 452, 404, 84, ("#C8505E", "#8A2A38", "#EE8A94"), 155, tail=40, bend=12))
    o.append(ribbon_text(300, 450, "DOG MOM", JOS, 58, "#FFF6EE", 370, 12, ls=8, u=u))
    tw = measure("est. with love", SERIF_IT, 34)
    o.append(p_heart(u, 300 - tw / 2 - 22, 526, 9, seed=156, rot=-12) + p_heart(u, 300 + tw / 2 + 22, 526, 9, seed=157, rot=12))
    o.append(plain(300, 536, "est. with love", SERIF_IT, 34, "#8A2A38", 300))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ---------------------------------------------------------------- dog dad — a blue pit bull in a bow tie on a vintage badge
PIT = ("#8A909C", "#545A66", "#BAC0CA")


def pitbull(u, cx, cy, s, seed, tilt=0, mouth="open", look=(0.05, 0.12)):
    d = Dog(u, cx, cy, s, PIT, seed, ink_c="#2A2C34", ears="rose", ear_y=10, ear_x=-6, kind="smooth", skull=86, cheek=100, jowl=70, nose_y=58, round_top=0.6,
            muzzle_w=48, mouth=mouth, eyes=("#C08A44", "#5A3214"), stop_w=18, nose=("#5A545A", "#2A2628", "#8A8488"), tilt=tilt, look=look,
            ear_in=("#D8A0A0", "#A06A6A", "#F2C8C4"), chest_w=1.1, muzzle=("#E6E6EA", "#B4B6BE", "#FFFFFF"))

    def head(dd):
        return dd.blaze(WHITE_COAT, seed + 1, 4, 12, 20)

    def chest(dd):
        return dd.bib(WHITE_COAT, seed + 2, 0.95, dd.nose_y + 20)
    return d, dict(marks_head=head, marks_chest=chest)


@design("dog-dad")
def dog_dad():
    u = Ids("dog-dad")
    o = [bg(u, "#24384E", ["#1C2E42", "#2E4660", "#203448"], 161, angle=-20, fleck="#C8D2DC")]
    # sunburst
    for i in range(24):
        a = math.radians(i * 15)
        o.append(f'<path d="M 300 330 L {_f(300 + 520 * math.cos(a - 0.06))} {_f(330 + 520 * math.sin(a - 0.06))} L {_f(300 + 520 * math.cos(a + 0.06))} '
                 f'{_f(330 + 520 * math.sin(a + 0.06))} Z" fill="#3A5272" opacity="0.35"/>')
    # cream badge
    bx, by, br = 300, 362, 184
    o.append(shadow(u, bx + 6, by + 12, br + 14, br + 14, 0.45, "#0A1420"))
    o.append(spot(u, bx, by, br, br, "#F2E6CE", ["#F8EEDC", "#E6D6B8"], 162, op=1, wob=0.015))
    o.append(f'<circle cx="{bx}" cy="{by}" r="{br - 12}" fill="none" stroke="#C8963E" stroke-width="3" stroke-dasharray="2 7" stroke-linecap="round"/>')
    clip = u("bc")
    o.append(f'<clipPath id="{clip}"><circle cx="{bx}" cy="{by}" r="{br - 3}"/></clipPath><g clip-path="url(#{clip})">')
    o.append(glow(u, 300, 380, 160, "#FFFFFF", 0.5))
    d, hooks = pitbull(u, 300, 330, 0.95, 163, tilt=-5, mouth="grin")
    o.append(d.draw(**hooks))
    o.append(bow(u, 300, 462, 36, ("#C8463A", "#82221A", "#F2806A"), 164, rot=-4, tails=False, dots="#FBEBD2"))
    o.append("</g>")
    o.append(f'<circle cx="{bx}" cy="{by}" r="{br}" fill="none" stroke="#14202E" stroke-width="2.4" opacity="0.7"/>')
    o.append(title(u, 300, 150, "DOG DAD", ANTON, 104, "#F2E6CE", ["#E6D6B8", "#FFF8EA", "#D8C6A2"], 165, max_w=440, ls=8, shadow="#C8963E", soff=(0.025, 0.04), angle=-75))
    for sg in (-1, 1):
        o.append(sparkle(300 + sg * 236, 112, 9, "#E8B84A", 0.95))
    # bottom banner
    o.append(ribbon(u, 300, 520, 380, 50, ("#C8963E", "#8A6018", "#F2CC7A"), 166, tail=30, bend=6))
    o.append(ribbon_text(300, 518, "WALKS · TREATS · BELLY RUBS", JOS, 22, "#24384E", 340, 6, ls=2, u=u))
    o.append(finish(u, op=0.8, color="#1A1A1A"))
    return "".join(o)
#NEW>>


#<<MORE
# ================================================================ more shared pieces: limbs, paws, stamps, boxes, mugs
from fall_gouache_b import mug, steam, leaf, scatter_leaves


def rpoly(pts, r=6, seed=None, jit=0.0):
    """Polygon with gently rounded corners (boxes, tables, labels) - straight-ish edges, never balloons."""
    if seed is not None and jit:
        pts = jitter(pts, seed, jit)
    n = len(pts)
    d = []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        l1 = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) or 1
        l2 = math.hypot(p2[0] - p1[0], p2[1] - p1[1]) or 1
        rr = min(r, l1 / 2.2, l2 / 2.2)
        a = (p1[0] + (p0[0] - p1[0]) * rr / l1, p1[1] + (p0[1] - p1[1]) * rr / l1)
        b = (p1[0] + (p2[0] - p1[0]) * rr / l2, p1[1] + (p2[1] - p1[1]) * rr / l2)
        d.append(("M" if i == 0 else "L") + f" {_f(a[0])} {_f(a[1])} Q {_f(p1[0])} {_f(p1[1])} {_f(b[0])} {_f(b[1])}")
    return " ".join(d) + " Z"


def tube(center, w0, w1, n=6):
    """Outline (closed pts) of a tapered tube along a polyline: legs, tails, straps."""
    pts = catmull(center, n)
    m = len(pts)
    L, R = [], []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, m - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        w = (w0 + (w1 - w0) * i / max(1, m - 1)) / 2
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return L + R[::-1]


def mitt(u, cx, cy, w, h, pal, seed, inkc, rot=0, toes=4, flow=-90, line_op=0.7, ink_w=2.0):
    """A soft front paw seen from the front: furry mitt with toe creases at the front edge."""
    pts = blob_pts(cx, cy, w / 2, h / 2, seed, 0.04, 16)
    out = [f'<g transform="rotate({_f(rot)} {_f(cx)} {_f(cy)})">']
    out.append(fur(u, pts, pal, seed, flow, shade=(0, h * 0.14), shade_op=0.38, length=(w * 0.08, w * 0.22), width=(0.8, 1.8), ink_w=ink_w,
                   ink_col=inkc, n=int(w * h / 14), hi=(cx - w * 0.1, cy - h * 0.18, w * 0.22, h * 0.14), hi_op=0.3))
    for k in range(toes - 1):
        x = cx + (k - (toes - 2) / 2) * w * 0.24
        out.append(ink(f"M {_f(x)} {_f(cy + h * 0.47)} Q {_f(x + 1)} {_f(cy + h * 0.28)} {_f(x - 0.5)} {_f(cy + h * 0.1)}", inkc, 1.7, seed + k, 1, line_op))
    out.append("</g>")
    return "".join(out)


def limb(u, center, w0, w1, pal, seed, inkc, flow=None, shade=(6, 0), hi=None, ink_w=2.2, length=(6, 14)):
    pts = tube(center, w0, w1)
    if flow is None:
        (x0, y0), (x1, y1) = center[0], center[-1]
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        flow = lambda x, y, a=ang: a
    return fur(u, pts, pal, seed, flow, shade=shade, shade_op=0.32, length=length, width=(1, 2.2), ink_w=ink_w, ink_col=inkc, hi=hi, hi_op=0.3)


def distress(u, clip_inner, box, color, seed, n=160, r=(0.8, 2.6)):
    """Worn-ink texture: specks of the ground colour clipped to the shape (stamps, painted signs)."""
    cid = u("ds")
    return (f'<clipPath id="{cid}">{clip_inner}</clipPath><g clip-path="url(#{cid})">' +
            dabs(box, [color], seed, n, r, (0.35, 0.8), 0.5) + "</g>")


def stamp(u, x, y, s, font, size, color, seed, ground, rot=0, max_w=300, ls=0, box=True, pad=(18, 12)):
    """A rubber-stamped word with a double-ruled frame, slightly rotated and worn."""
    size = fit_size(s, font, size, max_w, ls)
    w = measure(s, font, size, ls)
    lsa = f' letter-spacing="{ls}"' if ls else ""
    xx = x + ls / 2
    t = f'<text x="{_f(xx)}" y="{_f(y)}" text-anchor="middle" {font} font-size="{size}"{lsa}>{esc(s)}</text>'
    out = [f'<g transform="rotate({rot} {_f(x)} {_f(y - size * 0.35)})" opacity="0.88">']
    inner = t
    if box:
        bx0, by0, bx1, by1 = x - w / 2 - pad[0], y - size * 0.74 - pad[1], x + w / 2 + pad[0], y + pad[1] * 0.8
        fr = (f'<path d="{smooth_closed(jitter([(bx0, by0), ((bx0 + bx1) / 2, by0 - 1), (bx1, by0), (bx1 + 1, (by0 + by1) / 2), (bx1, by1), ((bx0 + bx1) / 2, by1 + 1), (bx0, by1), (bx0 - 1, (by0 + by1) / 2)], seed, 0.4))}" '
              f'fill="none" stroke="{color}" stroke-width="4"/>'
              f'<rect x="{_f(bx0 + 7)}" y="{_f(by0 + 7)}" width="{_f(bx1 - bx0 - 14)}" height="{_f(by1 - by0 - 14)}" fill="none" stroke="{color}" stroke-width="1.6"/>')
        out.append(fr)
        inner += (f'<rect x="{_f(bx0 - 3)}" y="{_f(by0 - 3)}" width="{_f(bx1 - bx0 + 6)}" height="{_f(by1 - by0 + 6)}"/>')
    out.append(t.replace("<text ", f'<text fill="{color}" '))
    bb = (x - w / 2 - 30, y - size - 30, x + w / 2 + 30, y + 30)
    out.append(distress(u, inner, bb, ground, seed, n=int((bb[2] - bb[0]) * (bb[3] - bb[1]) / 45)))
    out.append("</g>")
    return "".join(out)


def floor_boards(u, y_top, seed, pal=("#C8925A", "#94643A", "#E2B07A"), rows=4, inkc="#6A4220", bottom=620):
    out = [form(u, f"M -20 {y_top} L 620 {y_top} L 620 {bottom} L -20 {bottom} Z", (-20, y_top, 620, bottom), pal[0], pal[1], pal[2], seed, 0, n=300,
                length=(40, 140), width=(1.5, 4), shade=None, ink_w=0)]
    rnd = random.Random(seed)
    h = (bottom - y_top) / rows
    for r in range(rows + 1):
        y = y_top + r * h * (0.8 + 0.2 * r / rows)
        out.append(ink(f"M -10 {_f(y)} L 610 {_f(y + rnd.uniform(-1, 1))}", inkc, 1.6, seed + r, 1, 0.4))
        for _ in range(2):
            x = rnd.uniform(20, 580)
            out.append(ink(f"M {_f(x)} {_f(y)} L {_f(x)} {_f(y + h * 0.8)}", inkc, 1.4, seed + r * 7, 1, 0.35))
    return "".join(out)


def stars_field(seed, n, box, col="#FFF4D6", avoid=None, s=(2.5, 6)):
    rnd = random.Random(seed)
    out = []
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if avoid and avoid(x, y):
            continue
        if rnd.random() < 0.55:
            out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{rnd.uniform(0.8, 1.8):.1f}" fill="{col}" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
        else:
            out.append(sparkle(x, y, rnd.uniform(*s), col, rnd.uniform(0.7, 1)))
    return "".join(out)


def crescent(u, cx, cy, r, seed, pal=("#F8E6A8", "#D8B868", "#FFF8DC"), phase=0.42):
    d = (f"M {_f(cx)} {_f(cy - r)} A {_f(r)} {_f(r)} 0 1 0 {_f(cx)} {_f(cy + r)} "
         f"A {_f(r * 0.78)} {_f(r)} 0 1 1 {_f(cx)} {_f(cy - r)} Z")
    return (glow(u, cx - r * 0.3, cy, r * 2.6, pal[2], 0.35) +
            form(u, d, (cx - r, cy - r, cx + r * 0.2, cy + r), pal[0], pal[1], pal[2], seed, 80, n=r * 1.5, shade=(-r * 0.12, 0), shade_op=0.4,
                 length=(r * 0.2, r * 0.6), width=(1, 2.4), ink_w=0))


def zigzag(x, y, s, col, seed, rot=0, w=3.2):
    """A little lightning-bolt 'zap' mark."""
    d = f"M {_f(x)} {_f(y - s)} L {_f(x - s * 0.35)} {_f(y + s * 0.05)} L {_f(x + s * 0.12)} {_f(y)} L {_f(x - s * 0.18)} {_f(y + s)} L {_f(x + s * 0.4)} {_f(y - s * 0.12)} L {_f(x - s * 0.05)} {_f(y - s * 0.06)} Z"
    return f'<g transform="rotate({rot} {_f(x)} {_f(y)})"><path d="{d}" fill="{col}"/>' + ink(d, mix(col, "#000000", 0.4), 1.6, seed, 1, 0.7) + "</g>"


def motion(pts_list, col, seed, w=2.4, op=0.7):
    return "".join(ink(smooth_open(p), col, w, seed + i, 1, op) for i, p in enumerate(pts_list))


COW = ("#F4EEE6", "#C8BEB2", "#FFFFFF")
CAT_BLACK = ("#2E2A30", "#121014", "#5A5462")
CAT_ORANGE = ("#E8954A", "#B05E22", "#F8C080")
CAT_GREY = ("#8A929E", "#565E6A", "#B4BAC4")
SIAM = ("#F2E6D2", "#C8B496", "#FFF8EC")
SIAM_PT = ("#6A5446", "#4A3628", "#8A7060")
CARD = ("#C89A62", "#94683A", "#E6C08A")


# ---------------------------------------------------------------- if i fits, i sits — a cow cat wedged into a cardboard box
@design("if-i-fits-i-sits")
def if_i_fits():
    u = Ids("if-i-fits-i-sits")
    o = [bg(u, "#CFE2DC", ["#BCD6CE", "#E0EEEA", "#B0CCC4"], 201, angle=-20)]
    o.append(glow(u, 300, 300, 260, "#F6FBF4", 0.7))
    # floor
    o.append(form(u, "M -20 500 Q 300 492 620 500 L 620 620 L -20 620 Z", (-20, 490, 620, 620), "#A9C7BE", "#86A89E", "#C4DCD4", 202, 0, n=120,
                  length=(40, 120), width=(2, 5), shade=None, ink_w=0))
    o.append(shadow(u, 304, 548, 200, 18, 0.45, "#1E3A34"))
    cb, cd, cl = CARD
    inkc = "#5A3A1A"
    # back flap (behind the cat) and the dark inside of the box
    back = [(176, 352), (424, 352), (414, 296), (186, 296)]
    o.append(form(u, rpoly(back, 6, 203, 0.6), bbox(back, 2), mix(cb, "#FFFFFF", 0.1), cd, cl, 203, 0, n=60, length=(20, 60), width=(1.5, 3),
                  shade=(0, -8), shade_op=0.3, ink_w=2, ink_col=inkc))
    inside = [(150, 386), (176, 352), (424, 352), (450, 386)]
    o.append(f'<path d="{rpoly(inside, 4)}" fill="#5E3E22"/>')
    # side flaps folded outward
    for sg in (-1, 1):
        fl = [(300 + sg * 150, 386), (300 + sg * 124, 352), (300 + sg * 196, 318), (300 + sg * 222, 350)]
        o.append(form(u, rpoly(fl, 6, 204 + sg, 0.6), bbox(fl, 2), cl, cd, "#F4D8A8", 204 + sg, sg * 20, n=50, length=(16, 40), width=(1.4, 3),
                      shade=(sg * 6, 0), shade_op=0.25, ink_w=2.2, ink_col=inkc))
    # the cat: white with black patches, sitting inside
    pat = CAT_BLACK

    def head_marks(c):
        P = c.P
        out = [c.patch([(-110, -40), (-80, -84), (-30, -92), (-8, -60), (-18, -24), (-42, -10), (-70, -12), (-96, 6)], pat, 205,
                       flow=radial(*P(-60, -40)))]
        out.append(c.patch([(46, -96), (90, -80), (112, -40), (100, -26), (74, -40), (52, -66)], pat, 206, flow=radial(*P(80, -60))))
        return "".join(out)

    def ear_marks(c, sg):
        return c.patch(c.ear_local(sg), pat, 208 + sg, soft=False)

    def body_marks(c):
        P = c.P
        return c.patch([(60, 70), (120, 80), (140, 150), (90, 160), (70, 120)], pat, 209, flow=lambda x, y: 90)

    cat = Cat(u, 300, 272, 1.0, COW, 210, ink_c="#4A3A30", eyes=("#D8D060", "#7A8A20"), look=(0.0, 0.1), muzzle="#FFFFFF",
              whisk="#FFFFFF", body_len=140, ear_rot=-4, ear_in=("#F0B0AA", "#C07A76", "#FAD6D0"), pupil_k=0.66)
    o.append(cat.draw(head_marks, body_marks, ear_marks))
    # front flap folded down over the box face, then the face itself
    face = [(150, 386), (450, 386), (444, 546), (156, 546)]
    o.append(form(u, rpoly(face, 6, 211, 0.5), bbox(face, 2), cb, cd, cl, 211, -90, n=200, length=(20, 70), width=(1.6, 4),
                  shade=(10, 0), shade_op=0.3, ink_w=2.4, ink_col=inkc, hi=(220, 470, 50, 40), hi_op=0.15))
    # cardboard flute edge and corrugation streaks
    for x in range(170, 440, 28):
        o.append(ink(f"M {x} 440 L {x - 1} 540", cd, 1.2, x, 1, 0.18))
    flap = [(150, 386), (450, 386), (466, 432), (134, 432)]
    o.append(form(u, rpoly(flap, 6, 212, 0.5), bbox(flap, 2), cl, cd, "#F6DEB0", 212, 0, n=110, length=(30, 80), width=(1.4, 3),
                  shade=(0, -6), shade_op=0.3, ink_w=2.4, ink_col=inkc))
    o.append(f'<path d="M 140 430 L 460 430" stroke="{cd}" stroke-width="5" opacity="0.35"/>')
    # packing tape strip down the middle
    tp = [(286, 384), (314, 384), (318, 436), (282, 436)]
    o.append(f'<path d="{rpoly(tp, 2)}" fill="#D8B888" opacity="0.65"/><path d="M 288 392 L 312 392 M 287 410 L 313 410" stroke="#FFF2D6" stroke-width="1.6" opacity="0.6"/>')
    # paws hooked over the edge
    for sg in (-1, 1):
        o.append(mitt(u, 300 + sg * 56, 392, 46, 34, COW, 213 + sg, "#4A3A30", rot=sg * -6))
    o.append(f'<path d="{blob(254, 386, 12, 9, 215, 0.15, 10)}" fill="{pat[0]}" opacity="0.9"/>')
    # stamped words and a shipping label
    o.append(stamp(u, 286, 516, "I SITS", BEBAS, 76, "#B8322A", 216, cb, rot=-4, max_w=200, ls=6))
    lab = [(380, 452), (432, 450), (434, 500), (382, 502)]
    o.append(form(u, rpoly(lab, 5), bbox(lab, 1), "#F6EEDC", "#D2C6AE", "#FFFFFF", 217, 0, n=20, shade=None, ink_w=1.4, ink_col="#8A7A5A"))
    for k in range(4):
        o.append(f'<path d="M {388} {462 + k * 9} L {426 - (k % 2) * 10} {462 + k * 9}" stroke="#8A7A5A" stroke-width="1.8" opacity="0.7"/>')
    # 'this side up' arrows
    for x in (184, 206):
        o.append(ink(f"M {x} 500 L {x} 472 M {x - 7} 480 L {x} 470 L {x + 7} 480", "#7A4E26", 2.6, x, 1, 0.75))
    o.append(title(u, 300, 104, "if i fits,", SERIF_IT, 76, "#2A4E4A", ["#1E3E3A", "#3A6660", "#2A5450"], 218, max_w=380,
                   shadow="#F4FAF6", soff=(0.025, 0.035), angle=-30))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ---------------------------------------------------------------- fur real — a deadpan British shorthair with crossed arms
@design("fur-real")
def fur_real():
    u = Ids("fur-real")
    o = [bg(u, "#EDC66E", ["#E2B85A", "#F4D488", "#D8AC4E"], 221, angle=-25)]
    o.append(spot(u, 300, 420, 250, 210, "#F4D894", ["#F8E2A8", "#EAC878"], 222, op=0.9))
    inkc = "#2A2E36"
    coat = ("#8C94A2", "#566070", "#BCC2CE")

    def head_marks(c):
        P = c.P
        return (f'<path d="{blob(*P(-46, -6), 34 * c.s, 26 * c.s, 223, 0.06, 12)}" fill="#A8B0BC" opacity="0.35"/>'
                f'<path d="{blob(*P(46, -6), 34 * c.s, 26 * c.s, 224, 0.06, 12)}" fill="#A8B0BC" opacity="0.35"/>')

    def arms(c):
        s = c.s
        P = c.P
        out = []
        # left arm under, right arm over: forearms folded across the chest
        out.append(limb(u, [P(-112, 132), P(-60, 168), P(10, 186), P(64, 180)], 56 * s, 46 * s, coat, 225, inkc, shade=(0, 8), ink_w=1.6))
        out.append(mitt(u, *P(78, 178), 44 * s, 36 * s, coat, 226, inkc, rot=-70))
        out.append(limb(u, [P(116, 128), P(64, 160), P(-6, 196), P(-58, 206)], 58 * s, 48 * s, coat, 227, inkc, shade=(0, 8), ink_w=1.8,
                        hi=(P(30, 170)[0], P(30, 170)[1], 30 * s, 8 * s)))
        out.append(mitt(u, *P(-74, 206), 46 * s, 36 * s, coat, 228, inkc, rot=70))
        return "".join(out)

    cat = Cat(u, 300, 330, 1.1, coat, 229, ink_c=inkc, eyes=("#F0AA3A", "#B0601A"), cheek=1.2, ear_k=0.58, ear_w=0.8, muzzle="#B4BCC8",
              nose=("#6A6E7A", "#3A3E48", "#9A9EAA"), lid=("#8C94A2", 0.42), mouth="flat", look=(0.35, 0.05), body_w=1.12, body_len=320,
              ear_in=("#C8A0A4", "#946A70", "#E8C4C4"), whisk="#EEF0F4", chin_c="#B4BCC8", eye_rot=4)
    o.append(cat.draw(head_marks, None, None, over_body=arms))
    o.append(title(u, 300, 168, "fur real?", DMS, 120, "#2E3440", ["#20262E", "#3E4654", "#4A5260"], 230, max_w=470,
                   shadow="#FBEBC0", soff=(0.02, 0.03), angle=-60))
    o.append(ruled(u, 76, "ARE YOU", JOS, 22, "#7A5418", 231, ls=8, line_w=40))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ---------------------------------------------------------------- the cat's pajamas — a sleepy siamese in striped PJs
@design("the-cats-pajamas")
def cats_pajamas():
    u = Ids("the-cats-pajamas")
    o = [sky(u, [(0, "#1C2848"), (0.6, "#2C3C66"), (1, "#3E4E7A")], ["#24345A", "#34466E", "#1E2C50"], 241, n=120)]
    o.append(stars_field(242, 70, (20, 20, 580, 600), avoid=lambda x, y: 150 < x < 450 and y > 200))
    o.append(crescent(u, 498, 268, 30, 243))
    o.append(glow(u, 300, 420, 230, "#6A7AB0", 0.45))
    inkc = "#3A2A20"
    PJ = ("#F4EEE2", "#C8C0B2", "#FFFFFF")
    stripe = "#5E86C2"

    def head_marks(c):
        P = c.P
        return (f'<path d="{blob(*P(0, 34), 70 * c.s, 56 * c.s, 243, 0.08, 14)}" fill="#C8AE90" opacity="0.5"/>' +
                c.patch([(0, -46), (24, -34), (50, -16), (74, 8), (78, 40), (60, 68), (30, 84), (0, 88), (-30, 84), (-60, 68), (-78, 40), (-74, 8), (-50, -16), (-24, -34)],
                        ("#7E6656", "#4E3A2C", "#A08470"), 244))

    def ear_marks(c, sg):
        return c.patch(c.ear_local(sg), SIAM_PT, 245 + sg, soft=False)

    def pajamas(c):
        s = c.s
        P = c.P
        out = []
        shirt = c.Ps([(0, 66), (60, 70), (118, 96), (150, 150), (166, 240), (172, 320), (-172, 320), (-166, 240), (-150, 150), (-118, 96), (-60, 70)])
        cid = u("pj")
        stripes = "".join(f'<path d="M {_f(x)} {_f(P(0, 60)[1])} L {_f(x + 10)} {_f(P(0, 330)[1])}" stroke="{stripe}" stroke-width="{_f(9 * s)}" opacity="0.85"/>'
                          for x in range(int(P(-190, 0)[0]), int(P(190, 0)[0]), int(26 * s)))
        out.append(fur(u, shirt, PJ, 246, lambda x, y: 90 + (x - c.cx) * 0.15, shade=(-14 * s, 0), shade_op=0.3, length=(14, 34), width=(1.4, 3),
                       ink_w=2.4, ink_col="#2E3E66", extra_in=stripes + f'<path d="{blob(*P(-70, 200), 40 * s, 90 * s, 247, 0.1, 12)}" fill="#FFFFFF" opacity="0.15"/>'))
        # folds
        for sg in (-1, 1):
            out.append(ink(smooth_open(c.Ps([(sg * 120, 120), (sg * 110, 180), (sg * 128, 250)])), "#2E3E66", 1.6, 248 + sg, 1, 0.35))
        # notched collar lapels with piping
        for sg in (-1, 1):
            lap = c.Ps([(0, 128), (sg * 18, 92), (sg * 44, 70), (sg * 70, 66), (sg * 84, 80), (sg * 66, 96), (sg * 62, 118), (sg * 30, 150)])
            out.append(form(u, smooth_closed(lap), bbox(lap, 2), "#5E86C2", "#3A5E98", "#8EB0E0", 249 + sg, -90 + sg * 30, n=30, shade=(sg * 4, 4),
                            ink_w=2.2, ink_col="#22345E", extra_in=ink(smooth_open(lap[1:6]), "#F4EEE2", 2.4, 250, 1, 0.8)))
        # placket and buttons
        out.append(ink(smooth_open(c.Ps([(2, 130), (4, 220), (2, 320)])), "#2E3E66", 2, 251, 1, 0.6))
        for k, y in enumerate((170, 228, 286)):
            bx, by = P(-10, y)
            out.append(f'<circle cx="{_f(bx)}" cy="{_f(by)}" r="{_f(7 * s)}" fill="#F2C86A"/><circle cx="{_f(bx)}" cy="{_f(by)}" r="{_f(7 * s)}" fill="none" stroke="#8A6A1A" stroke-width="1.4"/>'
                       f'<circle cx="{_f(bx - 2 * s)}" cy="{_f(by - 1)}" r="1.2" fill="#8A6A1A"/><circle cx="{_f(bx + 2 * s)}" cy="{_f(by + 1)}" r="1.2" fill="#8A6A1A"/>')
        # breast pocket
        pk = c.Ps([(56, 182), (110, 180), (112, 230), (58, 232)])
        out.append(f'<path d="{smooth_closed(pk)}" fill="none" stroke="#2E3E66" stroke-width="2" opacity="0.5"/>'
                   f'<path d="M {_f(pk[0][0])} {_f(pk[0][1] + 9 * s)} L {_f(pk[1][0])} {_f(pk[1][1] + 9 * s)}" stroke="#5E86C2" stroke-width="{_f(8 * s)}" opacity="0.9"/>')
        return "".join(out)

    def sleep_mask(c):
        s = c.s
        P = c.P
        out = []
        # elastic strap behind the ears
        out.append(ink(smooth_open(c.Ps([(-104, -40), (-60, -66), (0, -72), (60, -66), (104, -40)])), "#C25A7A", 5 * s, 252, 1, 0.9))
        mk = c.Ps([(0, -58), (24, -76), (62, -84), (92, -70), (96, -48), (70, -34), (34, -38), (0, -48), (-34, -38), (-70, -34), (-96, -48), (-92, -70), (-62, -84), (-24, -76)])
        out.append(form(u, smooth_closed(mk), bbox(mk, 2), "#F2A4BC", "#C25A7A", "#FBD2DE", 253, 0, n=80, shade=(0, 6 * s), shade_op=0.4,
                        hi=(P(-50, -72)[0], P(0, -72)[1], 24 * s, 5 * s), hi_op=0.5, ink_w=2.2, ink_col="#8A2A4E", length=(8, 20)))
        # painted closed eyes with lashes on the mask
        for sg in (-1, 1):
            ex, ey = P(sg * 50, -60)
            out.append(ink(f"M {_f(ex - 20 * s)} {_f(ey - 3 * s)} Q {_f(ex)} {_f(ey + 10 * s)} {_f(ex + 20 * s)} {_f(ey - 3 * s)}", "#5A1A34", 2.8 * s, 254 + sg, 2, 0.95))
            for k in (-1, 0, 1):
                lx = ex + k * 11 * s
                out.append(ink(f"M {_f(lx)} {_f(ey + 4.5 * s - abs(k) * 2.5 * s)} l {_f(k * 3 * s)} {_f(6 * s)}", "#5A1A34", 2 * s, 255, 1, 0.9))
        return "".join(out)

    cat = Cat(u, 300, 372, 1.0, SIAM, 256, ink_c="#4A3626", eyes=("#9AD2F4", "#2E72B8"), ear_in=SIAM_PT, muzzle="#7A6252", chin_c="#7A6252",
              ear_k=1.12, nose=("#5A4436", "#2A1E16", "#8A7060"), look=(0.0, 0.0), lid=("#EDE0CA", 0.3), whisk="#FFF8EE", body_len=300)
    o.append(cat.draw(head_marks, None, ear_marks, over_body=pajamas, over_face=sleep_mask))
    o.append(title(u, 300, 92, "the cat's", SERIF_IT, 52, "#F8E6A8", ["#FFF2C8", "#E8C878", "#F8E0A0"], 257, max_w=300, angle=-30, shadow="#141C34", soff=(0.02, 0.04)))
    o.append(title(u, 300, 168, "PAJAMAS", BEBAS, 100, "#F4EEE2", ["#FFFFFF", "#D8D2C8", "#9AB8E4"], 258, max_w=360, ls=10, shadow="#5E86C2",
                   soff=(0.025, 0.04), angle=-80))
    o.append(finish(u, op=0.7, color="#0A0E1A"))
    return "".join(o)


# ---------------------------------------------------------------- cat dad — a tuxedo cat in reading glasses and a tie, in Dad's armchair
@design("cat-dad")
def cat_dad():
    u = Ids("cat-dad")
    o = [bg(u, "#E8DCC4", ["#DCCCB0", "#F2E8D6"], 261, angle=-80)]
    # den wallpaper stripes
    for i, x in enumerate(range(-20, 640, 44)):
        o.append(f'<path d="M {x} -10 L {x + 2} 610" stroke="#B8A27E" stroke-width="12" opacity="0.28"/><path d="M {x + 22} -10 L {x + 23} 610" stroke="#B8A27E" stroke-width="2" opacity="0.35"/>')
    o.append(vignette(u, "#5A4428", 0.35, 0.55))
    inkc = "#120E10"
    W = ("#F6F0E6", "#D2C8BA", "#FFFFFF")
    leather = ("#3E6A52", "#22402E", "#6E9A7E")
    # wingback armchair behind the cat
    back = [(130, 600), (124, 340), (150, 262), (220, 222), (300, 212), (380, 222), (450, 262), (476, 340), (470, 600)]
    o.append(shadow(u, 300, 420, 230, 200, 0.3, "#2A1A0A"))
    tuft = []
    for r, y in enumerate(range(262, 600, 46)):
        for x in range(160 + (23 if r % 2 else 0), 450, 46):
            tuft.append(f'<circle cx="{x}" cy="{y}" r="3.6" fill="#16281C"/><circle cx="{x - 1}" cy="{y - 1}" r="1.4" fill="#9AC2A8" opacity="0.8"/>')
            tuft.append(f'<path d="M {x} {y} L {x + 23} {y + 23} M {x} {y} L {x - 23} {y + 23}" stroke="#16281C" stroke-width="1.4" opacity="0.4"/>')
    o.append(form(u, smooth_closed(back), bbox(back, 2), leather[0], leather[1], leather[2], 262, -90, n=260, shade=(-16, 0), shade_op=0.35,
                  hi=(250, 280, 70, 30), hi_op=0.25, ink_w=2.6, ink_col="#122218", extra_in="".join(tuft), length=(20, 50)))
    for sg in (-1, 1):
        wing = [(300 + sg * 176, 600), (300 + sg * 174, 380), (300 + sg * 190, 330), (300 + sg * 226, 342), (300 + sg * 236, 420), (300 + sg * 230, 600)]
        o.append(form(u, smooth_closed(wing), bbox(wing, 2), leather[0], leather[1], leather[2], 263 + sg, -90, n=90, shade=(sg * 10, 0), shade_op=0.4,
                      ink_w=2.6, ink_col="#122218", length=(20, 50)))
        o.append("".join(f'<circle cx="{300 + sg * 205}" cy="{y}" r="3.4" fill="#C8A04A"/>' for y in range(372, 600, 16)))

    def head_marks(c):
        P = c.P
        return (c.patch([(0, -40), (8, -36), (12, -10), (26, 10), (44, 36), (46, 66), (30, 82), (0, 86), (-30, 82), (-46, 66), (-44, 36), (-26, 10), (-12, -10), (-8, -36)],
                        W, 264))

    def body_marks(c):
        P = c.P
        return c.patch([(0, 60), (50, 70), (84, 130), (94, 220), (80, 330), (-80, 330), (-94, 220), (-84, 130), (-50, 70)], W, 265,
                       flow=lambda x, y: 90 + (x - c.cx) * 0.2, length=(10, 22))

    def tie(c):
        s = c.s
        P = c.P
        out = []
        # shirt collar points
        for sg in (-1, 1):
            cp = c.Ps([(sg * 6, 92), (sg * 48, 80), (sg * 40, 120), (sg * 14, 112)])
            out.append(form(u, smooth_closed(cp), bbox(cp, 2), "#FFFFFF", "#C8C2BA", "#FFFFFF", 266 + sg, 0, n=12, shade=(0, 3), ink_w=1.8, ink_col="#6A645E"))
        blade = c.Ps([(-14, 118), (14, 118), (26, 230), (0, 262), (-26, 230)])
        cid = u("tie")
        str_ = "".join(f'<path d="M {_f(P(-60, 0)[0])} {_f(P(0, y)[1])} L {_f(P(60, 0)[0])} {_f(P(0, y - 40)[1])}" stroke="#F2C86A" stroke-width="{_f(5 * s)}" opacity="0.9"/>'
                       for y in range(130, 300, 22))
        out.append(form(u, rpoly(blade, 5), bbox(blade, 2), "#B8322A", "#7A1A14", "#E86A50", 267, -90, n=50, shade=(6, 0), shade_op=0.4,
                        ink_w=2.2, ink_col="#4A0E0A", extra_in=str_))
        kn = c.Ps([(-16, 100), (16, 100), (12, 124), (-12, 124)])
        out.append(form(u, rpoly(kn, 5), bbox(kn, 2), "#B8322A", "#7A1A14", "#E86A50", 268, 0, n=12, shade=(3, 3), ink_w=2.2, ink_col="#4A0E0A"))
        return "".join(out)

    def glasses(c):
        s = c.s
        P = c.P
        out = []
        for sg in (-1, 1):
            gx, gy = P(sg * 44, 10)
            out.append(f'<ellipse cx="{_f(gx)}" cy="{_f(gy)}" rx="{_f(31 * s)}" ry="{_f(27 * s)}" fill="#E8F2F4" opacity="0.16"/>')
            out.append(f'<path d="M {_f(gx - 18 * s)} {_f(gy - 10 * s)} L {_f(gx - 4 * s)} {_f(gy - 20 * s)}" stroke="#FFFFFF" stroke-width="{_f(4 * s)}" stroke-linecap="round" opacity="0.55"/>')
            out.append(f'<ellipse cx="{_f(gx)}" cy="{_f(gy)}" rx="{_f(31 * s)}" ry="{_f(27 * s)}" fill="none" stroke="#C8963A" stroke-width="{_f(4 * s)}"/>'
                       f'<ellipse cx="{_f(gx)}" cy="{_f(gy)}" rx="{_f(31 * s)}" ry="{_f(27 * s)}" fill="none" stroke="#FBE2A0" stroke-width="{_f(1.2 * s)}" opacity="0.8" transform="translate(-1 -1)"/>')
            out.append(ink(smooth_open(c.Ps([(sg * 75, 4), (sg * 96, -2), (sg * 108, -8)])), "#C8963A", 3.4 * s, 269, 1, 1))
        out.append(ink(smooth_open(c.Ps([(-14, 6), (0, 0), (14, 6)])), "#C8963A", 3.6 * s, 270, 1, 1))
        return "".join(out)

    cat = Cat(u, 300, 352, 1.0, CAT_BLACK, 271, ink_c=inkc, eyes=("#B8D86A", "#5E8A2A"), muzzle="#FFFFFF", chin_c="#FFFFFF",
              ear_in=("#7A5A5E", "#4A3236", "#9A7A7E"), nose=("#E8A0A8", "#B8606A", "#F8D0D4"), rim="#8A7AA0", look=(0.0, 0.25), lid=("#2E2A30", 0.22),
              body_len=280, whisk="#FFFFFF")
    o.append(cat.draw(head_marks, body_marks, None, over_body=tie, over_face=glasses))
    o.append(title(u, 300, 172, "CAT DAD", ANTON, 108, "#3A2A1E", ["#2A1C12", "#5A4030", "#4A3424"], 272, max_w=440, ls=6, shadow="#C8963A",
                   soff=(0.025, 0.035), angle=-80))
    o.append(ruled(u, 74, "WORLD'S BEST", JOS, 22, "#7A3A20", 273, ls=7, line_w=40))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ---------------------------------------------------------------- orange cat energy — maintaining eye contact while pushing the mug off
@design("orange-cat-energy")
def orange_cat_energy():
    u = Ids("orange-cat-energy")
    o = [bg(u, "#F4E6CE", ["#EEDCBC", "#F8EEDC", "#E8D2AE"], 281, angle=-15)]
    o.append(glow(u, 270, 300, 220, "#FFF6E2", 0.7))
    inkc = "#6A3410"
    tc = "#B05E22"

    def head_marks(c):
        return c.stripes(tc, 282, op=0.65)

    def body_marks(c):
        P = c.P
        out = [f'<path d="{blob(*P(0, 150), 56 * c.s, 100 * c.s, 283, 0.08, 14)}" fill="#FBEAD2" opacity="0.85"/>']
        for sg in (-1, 1):
            for k, x in enumerate((90, 120)):
                out.append(taper([P(sg * x, 100 + k * 16), P(sg * (x + 12), 130 + k * 16), P(sg * (x + 6), 170 + k * 16)], 8, 2, tc, 0.55))
        return "".join(out)

    cx, cy, s = 262, 318, 0.96
    cat = Cat(u, cx, cy, s, CAT_ORANGE, 284, ink_c=inkc, eyes=("#D8E06A", "#6E9A2A"), look=(0.0, 0.05), muzzle="#FBEEDC", chin_c="#FBEEDC",
              body_len=200, ear_rot=6, pupil_k=0.72)
    # the reaching arm comes from behind the chest
    o.append(limb(u, [(cx + 70, 398), (330, 406), (388, 410), (414, 410)], 46, 38, CAT_ORANGE, 289, inkc, shade=(0, 7), hi=(360, 402, 30, 6)))
    o.append(cat.draw(head_marks, body_marks))
    # table top + apron
    top = [(-20, 438), (472, 438), (486, 446), (486, 462), (-20, 462)]
    o.append(form(u, rpoly(top, 8), bbox(top, 2), "#B87444", "#7E4822", "#DCA070", 285, 0, n=160, length=(40, 120), width=(1.2, 3), shade=(0, -6),
                  shade_op=0.3, ink_w=2.4, ink_col="#4A2410", hi=(240, 444, 220, 3), hi_op=0.35))
    apron = [(-20, 462), (470, 462), (470, 520), (-20, 520)]
    o.append(form(u, rpoly(apron, 4), bbox(apron, 2), "#94562C", "#5E3016", "#B87444", 286, 0, n=140, length=(40, 120), width=(1.4, 3.4),
                  shade=(0, 10), shade_op=0.3, ink_w=2.4, ink_col="#3A1A08"))
    o.append(form(u, "M 440 520 L 470 520 L 468 620 L 444 620 Z", (440, 520, 470, 620), "#94562C", "#5E3016", "#B87444", 287, -90, n=30, shade=(6, 0), ink_w=2.2, ink_col="#3A1A08"))
    # left paw resting on the table
    o.append(mitt(u, cx - 62, 432, 48, 30, CAT_ORANGE, 288, inkc))
    # right arm reaching out to the mug
    # the mug, already tipping over the edge, coffee in mid-air
    o.append(f'<g transform="rotate(32 452 410)">{mug(u, 452, 372, 56, 64, 290, glaze=("#5E8EB8", "#3A6890", "#8EB8DC"), band="#F4EAD8", side=1, drink="#5A3016")}</g>')
    o.append(mitt(u, 420, 406, 40, 30, CAT_ORANGE, 291, inkc, rot=-80))
    for (x, y, r) in ((486, 352, 7), (502, 334, 5), (470, 330, 4.5), (514, 362, 3.5), (494, 312, 3)):
        o.append(f'<path d="{blob(x, y, r, r * 1.25, int(x), 0.15, 10, rot=40)}" fill="#6A3A1A"/><circle cx="{x - r * 0.3:.1f}" cy="{y - r * 0.4:.1f}" r="{r * 0.25:.1f}" fill="#FFFFFF" opacity="0.6"/>')
    o.append(ink("M 478 372 Q 496 346 488 318", "#6A3A1A", 5, 292, 1, 0.9))
    o.append(motion([[(520, 400), (536, 420)], [(512, 420), (526, 442)], [(530, 382), (546, 398)]], "#B05E22", 293, 2.6, 0.7))
    # lettering
    o.append(title(u, 300, 104, "orange cat", SERIF_IT, 70, "#B85A1E", ["#C86A2A", "#8E3E10", "#E08A40"], 294, max_w=400, shadow="#FBF2E2",
                   soff=(0.02, 0.035), angle=-30))
    o.append(title(u, 286, 507, "ENERGY", ANTON, 50, "#FBEEDC", ["#FFFFFF", "#F2D8B0", "#E8C090"], 295, max_w=230, ls=10, angle=-80))
    o.append(zigzag(132, 492, 16, "#F2C04A", 296, rot=-12) + zigzag(440, 492, 16, "#F2C04A", 297, rot=12))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ================================================================ full-body cats
def cat_sit(c, coat=None, chest_marks=None, tail_side=1, paw_coat=None, tail_coat=None, tail_marks=None, bottom=310, tail=True, legs=True, bw=1.0):
    """Sitting cat body seen from the front (local units of a Cat `c`): tail from behind, tucked haunches, chest with soft front legs,
    paws, and the tail tip wrapped round the front of the feet. bw scales the body width (kittens < 1)."""
    u, s = c.u, c.s
    coat = coat or c.coat
    ic = c.ink_c
    out = []
    b = bottom
    ts = tail_side
    tc = tail_coat or coat
    L = lambda pts: c.Ps([(x * bw, y) for x, y in pts])
    tail_c = [(ts * 70, b - 30), (ts * 118, b - 14), (ts * 126, b + 4), (ts * 90, b + 16), (0, b + 18), (-ts * 64, b + 10), (-ts * 88, b - 4)]
    if tail:
        tp = tube(L(tail_c), 30 * s, 17 * s)
        out.append(fur(u, tp, tc, c.seed + 50, lambda x, y: 180 if ts > 0 else 0, shade=(0, 6 * s), shade_op=0.35, length=(8 * s, 16 * s), width=(1.2, 2.4),
                       ink_w=2.2, ink_col=ic))
    for sg in (-1, 1):
        hp = blob_pts(*L([(sg * 84, b - 54)])[0], 54 * s * bw, 58 * s, c.seed + 40 + sg, 0.05, 16, rot=sg * 12)
        out.append(fur(u, hp, coat, c.seed + 40 + sg, radial(*L([(sg * 60, b - 80)])[0]), shade=(sg * 10 * s, 6 * s), shade_op=0.32,
                       length=(8 * s, 18 * s), width=(1.2, 2.6), ink_w=2.2, ink_col=ic, hi=(*L([(sg * 80, b - 84)])[0], 16 * s, 12 * s), hi_op=0.25))
        fp = blob_pts(*L([(sg * 104, b - 6)])[0], 30 * s, 13 * s, c.seed + 42 + sg, 0.05, 12)
        out.append(fur(u, fp, paw_coat or coat, c.seed + 42 + sg, 0, shade=(0, 3 * s), length=(4 * s, 9 * s), width=(0.8, 1.6), ink_w=2, ink_col=ic, n=40))
    chest = L(sym([(0, 50), (58, 58), (86, 96), (98, 160), (100, 220), (92, b - 26), (70, b - 8), (0, b)], 0))
    out.append(fur(u, chest, coat, c.seed + 44, lambda x, y: 90 + (x - c.cx) * 0.25, shade=(-12 * s, 0), shade_op=0.3, length=(9 * s, 20 * s),
                   width=(1.2, 2.8), ink_w=2.2, ink_col=ic, hi=(*L([(-40, 150)])[0], 26 * s, 50 * s), hi_op=0.2,
                   extra_in=(chest_marks(c) if chest_marks else "")))
    if legs:
        pc = paw_coat or coat
        # front legs read as soft forms inside the chest: a shadowed gap between them and light pen lines
        out.append(f'<path d="{blob(*c.P(0, (190 + b) / 2), 12 * s * bw, (b - 190) / 2 * s, c.seed + 45, 0.08, 12)}" fill="{coat[1]}" opacity="0.45"/>')
        for sg in (-1, 1):
            out.append(ink(smooth_open(L([(sg * 18, 196), (sg * 20, 250), (sg * 20, b - 22)])), ic, 1.8, c.seed + 46 + sg, 1, 0.45))
            out.append(ink(smooth_open(L([(sg * 72, 186), (sg * 70, 240), (sg * 70, b - 22)])), ic, 1.8, c.seed + 47 + sg, 1, 0.3))
            out.append(f'<path d="{blob(*L([(sg * 44, 230)])[0], 12 * s, 40 * s, c.seed + 49 + sg, 0.1, 10)}" fill="{coat[2]}" opacity="0.18"/>')
            out.append(mitt(u, *L([(sg * 45, b - 10)])[0], 52 * s * bw, 30 * s, pc, c.seed + 48 + sg, ic))
    if tail:
        tp = tube(L(tail_c[2:]), 26 * s, 17 * s)
        out.append(fur(u, tp, tc, c.seed + 51, lambda x, y: 180 if ts > 0 else 0, shade=(0, 6 * s), shade_op=0.35, length=(8 * s, 16 * s), width=(1.2, 2.4),
                       ink_w=2.2, ink_col=ic, extra_in=(tail_marks(c) if tail_marks else "")))
    return "".join(out)


def cat_ground(u, c, b=310, w=190, op=0.3, color="#2A1608"):
    return shadow(u, c.cx, c.P(0, b + 10)[1], w * c.s, 22 * c.s, op, color)


def clover(u, cx, cy, r, seed, rot=0, pal=("#5E9A4A", "#3A6A2E", "#9ACC7A"), stem=True):
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    if stem:
        out.append(ink(f"M {_f(cx)} {_f(cy)} q {_f(r * 0.3)} {_f(r * 1.2)} {_f(r * 0.9)} {_f(r * 1.8)}", pal[1], max(1.4, r * 0.14), seed, 1, 1))
    for k in range(4):
        a = math.radians(k * 90 + 45)
        hx, hy = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55
        out.append(f'<g transform="rotate({k * 90 + 45 + 90} {_f(hx)} {_f(hy)})">{p_heart(u, hx, hy, r * 0.5, pal, seed + k, ink_w=max(0.8, r * 0.06))}</g>')
    out.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 0.12)}" fill="{pal[1]}"/></g>')
    return "".join(out)


def horseshoe(u, cx, cy, r, seed, pal=("#E8B84A", "#9A6A1A", "#FFE8A0")):
    pts = []
    for i in range(25):
        a = math.radians(200 - i * 220 / 24 + 180)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * 1.05))
    d_out = tube(pts, r * 0.36, r * 0.36, 3)
    out = [form(u, smooth_closed(d_out), bbox(d_out, 2), pal[0], pal[1], pal[2], seed, 0, n=r * 3, shade=(r * 0.06, r * 0.08), shade_op=0.5,
                ink_w=2, ink_col="#6A4410", hi=(cx - r * 0.5, cy - r * 0.7, r * 0.3, r * 0.1), hi_op=0.5)]
    for i in range(3, 23, 3):
        x, y = pts[i]
        out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r * 0.06)}" fill="#6A4410"/>')
    return "".join(out)


CALICO = ("#F6F0E6", "#D2C6B6", "#FFFFFF")
CAL_OR = ("#E08A3E", "#A8561C", "#F4B070")
CAL_BK = ("#3A3230", "#1A1412", "#6A5C56")


# ---------------------------------------------------------------- good luck charm — a black cat with golden eyes and a clover tag
@design("good-luck-charm")
def good_luck_charm():
    u = Ids("good-luck-charm")
    o = [bg(u, "#E4E6CC", ["#D8DCBC", "#EEF0DC", "#CCD2AC"], 301, angle=-20)]
    o.append(glow(u, 300, 380, 230, "#FFF2C0", 0.85))
    o.append(stars_field(302, 26, (60, 200, 540, 520), col="#D8A43A", avoid=lambda x, y: 170 < x < 430, s=(4, 9)))
    inkc = "#0A080A"
    c = Cat(u, 300, 312, 0.86, CAT_BLACK, 303, ink_c=inkc, eyes=("#F6D04A", "#C0861A"), ear_in=("#6A4A4E", "#3A2A2E", "#8A6A6E"), muzzle="#3A363C",
            chin_c="#3A363C", nose=("#4A3E44", "#1A1416", "#7A6A70"), rim="#B8A8D0", look=(0.0, 0.05), body=False, whisk="#E8E2EC", pupil_k=0.5)
    o.append(cat_ground(u, c, 256, 220, 0.35))

    def sitbody(cc):
        return cat_sit(cc, bottom=256)

    def collar_tag(cc):
        return collar(u, cc.Ps([(-60, 74), (-30, 86), (0, 90), (30, 86), (60, 74)]), 13, ("#4E8A42", "#2E5A28", "#82B86E"), 304, tag=None)

    o.append(c.draw(behind=sitbody, under_head=collar_tag))
    # rim light on the right side of the body
    o.append(clover(u, 300, 410, 21, 305, rot=0, stem=False))
    o.append(ink("M 300 388 L 300 380", "#B89A5A", 2.6, 306, 1, 1))
    for (x, y, r, rot) in ((118, 520, 15, -20), (480, 514, 13, 25), (150, 470, 10, 40), (446, 470, 9, -30)):
        o.append(clover(u, x, y, r, 307 + x, rot))
    o.append(title(u, 300, 100, "good luck", SERIF_IT, 66, "#2E5A28", ["#3A6E32", "#1E4018", "#4E8A42"], 308, max_w=360, shadow="#FBF6DE",
                   soff=(0.02, 0.035), angle=-30))
    o.append(ruled(u, 146, "CHARM", JOS, 30, "#B07A1E", 309, ls=12, line_w=44))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ---------------------------------------------------------------- cat mom — a calico hugging a tattoo-flash heart
@design("cat-mom")
def cat_mom():
    u = Ids("cat-mom")
    o = [bg(u, "#F2E4D2", ["#EAD6BE", "#F8EEE2", "#E2CAAE"], 311, angle=-25)]
    rnd = random.Random(312)
    for _ in range(9):
        x, y = rnd.choice([rnd.uniform(70, 150), rnd.uniform(450, 530)]), rnd.uniform(80, 520)
        o.append(p_paw(u, x, y, 7, ("#E4C4A8", "#C8A080", "#F2DCC4"), int(x), rot=rnd.uniform(-30, 30), ink_w=0))
    inkc = "#3A2418"
    hx, hy, hs = 300, 392, 7.2   # heart centre and scale

    def head_marks(cc):
        P = cc.P
        out = [cc.patch([(-112, -30), (-86, -80), (-40, -94), (-14, -64), (-22, -26), (-60, -14), (-96, 4)], CAL_OR, 313, flow=radial(*P(-60, -40)))]
        out.append(cc.patch([(30, -94), (80, -84), (110, -40), (96, -10), (60, -30), (36, -64)], CAL_BK, 314, flow=radial(*P(70, -60))))
        out.append(cc.patch([(70, 20), (108, 10), (112, 40), (90, 56)], CAL_OR, 315))
        return "".join(out)

    def ear_marks(cc, sg):
        return cc.patch(cc.ear_local(sg), CAL_OR if sg < 0 else CAL_BK, 316 + sg, soft=False)

    def body_marks(cc):
        return (cc.patch([(-150, 150), (-90, 120), (-60, 180), (-100, 260), (-150, 260)], CAL_BK, 317) +
                cc.patch([(80, 130), (150, 140), (150, 240), (100, 230)], CAL_OR, 318))

    c = Cat(u, 300, 194, 0.84, CALICO, 319, ink_c=inkc, eyes=("#D8C860", "#8A8A20"), muzzle="#FFFFFF", look=(0.0, 0.1), body_len=230, whisk="#FFFFFF",
            ear_in=("#F0B0AA", "#C07A76", "#FAD6D0"), tilt=-6)
    o.append(c.draw(head_marks, body_marks, ear_marks))
    # the heart
    d = heart_d(hx, hy, hs * 16)
    o.append(shadow(u, hx + 8, hy + 30, 210, 180, 0.3))
    k = hs
    o.append(form(u, d, (hx - 28 * k, hy - 25 * k, hx + 28 * k, hy + 19 * k), "#D2483A", "#8E1E16", "#F2806A", 320, -60, n=260, shade=(18, 14), shade_op=0.45,
                  hi=(hx - 13 * k, hy - 15 * k, 26, 14), hi_op=0.55, ink_w=4, ink_col="#3A1410", length=(10, 26), width=(1.4, 3.4), sop=(0.12, 0.32)))
    o.append(ink(f"M {hx - 18 * k:.0f} {hy - 17 * k:.0f} Q {hx - 22 * k:.0f} {hy - 11 * k:.0f} {hx - 19 * k:.0f} {hy - 6 * k:.0f}", "#FFE2D2", 6, 321, 1, 0.75))
    o.append(f'<circle cx="{hx - 17 * k:.0f}" cy="{hy - 20 * k:.0f}" r="5" fill="#FFF2E8" opacity="0.85"/>')
    # paws draped over the heart's lobes
    for sg in (-1, 1):
        o.append(mitt(u, hx + sg * 62, hy - 21 * k, 50, 34, CALICO, 322 + sg, inkc, rot=sg * -12))
    o.append(f'<path d="{blob(hx + 70, hy - 21 * k - 4, 13, 9, 324, 0.2, 10)}" fill="{CAL_OR[0]}" opacity="0.85"/>')
    # banner across the heart
    o.append(ribbon(u, 300, 404, 440, 74, ("#F6ECD6", "#CDB894", "#FFFFFF"), 325, tail=44, bend=14))
    o.append(ribbon_text(300, 402, "CAT MOM", JOS, 56, "#8E1E16", 380, 14, ls=8, u=u))
    for sg in (-1, 1):
        o.append(sparkle(hx + sg * 214, hy + 96, 12, "#E8B84A", 0.95))
    o.append(plain(300, 486, "EST. WITH LOVE", JOS, 19, "#FBEBD8", 220, ls=4))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ---------------------------------------------------------------- bird watcher — a silver tabby on a sunny windowsill, seen from behind
@design("bird-watcher")
def bird_watcher():
    u = Ids("bird-watcher")
    o = [bg(u, "#E8D6BC", ["#DEC8A8", "#F2E4CE"], 331, angle=-80)]
    # window opening with the garden outside
    win = (110, 96, 490, 452)
    x0, y0, x1, y1 = win
    cid = u("win")
    o.append(f'<clipPath id="{cid}"><path d="{rpoly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 4)}"/></clipPath><g clip-path="url(#{cid})">')
    o.append(sky(u, [(0, "#8EC4E4"), (0.7, "#CDE6EE"), (1, "#F4EEDA")], ["#A4D0E8", "#DCEEF4"], 332, n=60))
    o.append(glow(u, 470, 120, 160, "#FFF8D8", 0.9))
    for k, (cx, cy) in enumerate(((180, 160), (390, 196))):
        o.append("".join(f'<path d="{blob(cx + dx, cy + dy, r, r * 0.7, k * 10 + i, 0.1, 12)}" fill="#FFFFFF" opacity="0.85"/>'
                         for i, (dx, dy, r) in enumerate(((0, 0, 30), (26, -8, 24), (-24, 4, 20), (46, 6, 18)))))
    from fall_gouache_b import hill
    o.append(hill(u, [(100, 380), (220, 352), (360, 366), (500, 344)], 470, "#9CC07A", "#6E9A52", "#C4DE9A", 333))
    o.append(hill(u, [(100, 412), (240, 396), (380, 404), (500, 390)], 470, "#7EAA5E", "#547E3E", "#A8CC82", 334))
    # tree branch with two little birds
    o.append(ink("M 500 196 Q 470 204 440 214 Q 410 222 392 220", "#6E4A2A", 9, 335, 1, 1))
    o.append(ink("M 470 204 Q 466 186 452 178", "#6E4A2A", 5, 336, 1, 1))
    for i, (lx, ly, rot) in enumerate(((484, 186, -20), (452, 172, 30), (404, 210, -40), (430, 228, 60), (396, 226, 80), (474, 220, 20))):
        o.append(leaf(u, "elm", lx, ly, 14, rot, ("#7AA85A", "#4A7A36", "#A8D07E"), 337 + i, detail=False))

    def bird(bx, by, s, flip, pal, seed):
        out = []
        body = blob_pts(bx, by, 16 * s, 12 * s, seed, 0.05, 12)
        out.append(fur(u, body, pal, seed, 0, shade=(0, 3), ink_w=1.6, ink_col="#3A2418", n=30, length=(3, 7), width=(0.8, 1.4)))
        out.append(f'<path d="{blob(bx + flip * 12 * s, by - 10 * s, 9 * s, 8 * s, seed + 1, 0.05, 10)}" fill="{pal[0]}"/>'
                   f'<path d="{blob(bx + flip * 12 * s, by - 10 * s, 9 * s, 8 * s, seed + 1, 0.05, 10)}" fill="none" stroke="#3A2418" stroke-width="1.4"/>')
        out.append(f'<path d="{blob(bx - flip * 2 * s, by + 2 * s, 12 * s, 6 * s, seed + 2, 0.08, 10, rot=flip * 15)}" fill="{pal[1]}" opacity="0.8"/>')
        out.append(f'<path d="{blob(bx + flip * 5 * s, by + 3 * s, 8 * s, 6 * s, seed + 3, 0.08, 10)}" fill="#F2A25A" opacity="0.9"/>')
        out.append(f'<circle cx="{_f(bx + flip * 15 * s)}" cy="{_f(by - 12 * s)}" r="{_f(1.8 * s)}" fill="#1A0E08"/>')
        out.append(f'<path d="M {_f(bx + flip * 20 * s)} {_f(by - 11 * s)} l {_f(flip * 6 * s)} {_f(2 * s)} l {_f(-flip * 6 * s)} {_f(2 * s)} Z" fill="#E8A23A"/>')
        out.append(f'<path d="M {_f(bx - flip * 14 * s)} {_f(by - 2 * s)} l {_f(-flip * 12 * s)} {_f(-4 * s)} l {_f(flip * 2 * s)} {_f(8 * s)} Z" fill="{pal[1]}"/>')
        out.append(ink(f"M {_f(bx)} {_f(by + 11 * s)} l 0 {_f(5 * s)} M {_f(bx + 5 * s)} {_f(by + 11 * s)} l 0 {_f(5 * s)}", "#5A3A1A", 1.4, seed, 1, 0.9))
        return "".join(out)
    o.append(bird(456, 196, 1.2, -1, ("#7A9AC8", "#4E6E9E", "#B4CAE8"), 341))
    o.append(bird(418, 206, 1.1, 1, ("#C8A07A", "#8E6A44", "#E8CAA4"), 342))
    o.append(ink("M 430 150 q 5 -7 10 0 q 5 -7 10 0", "#3A5A7A", 2, 343, 1, 0.8))
    o.append("</g>")
    # sun shafts falling into the room
    for k, (a, b) in enumerate(((150, 230), (250, 300), (330, 380))):
        o.append(f'<path d="M {a + 220} 96 L {b + 220} 96 L {b - 60} 600 L {a - 120} 600 Z" fill="#FFF4D2" opacity="0.13"/>')
    # window frame and muntins
    fr = ("#F4EEE2", "#CFC4B2", "#FFFFFF")
    for (fx0, fy0, fx1, fy1) in ((96, 82, 504, 100), (96, 82, 114, 456), (486, 82, 504, 456), (292, 96, 308, 452), (110, 266, 490, 280)):
        pp = [(fx0, fy0), (fx1, fy0), (fx1, fy1), (fx0, fy1)]
        o.append(form(u, rpoly(pp, 3), (fx0, fy0, fx1, fy1), fr[0], fr[1], fr[2], fx0 + fy0, 0 if fx1 - fx0 > fy1 - fy0 else -90, n=30, shade=(3, 3),
                      shade_op=0.4, ink_w=1.8, ink_col="#8A7A62"))
    # glass glare
    o.append(ink("M 140 140 L 200 110 M 140 170 L 230 124", "#FFFFFF", 4, 344, 1, 0.35))
    # sill
    sill = [(70, 446), (530, 446), (540, 468), (530, 486), (70, 486), (60, 468)]
    o.append(shadow(u, 300, 492, 250, 14, 0.3))
    o.append(form(u, rpoly(sill, 6), bbox(sill, 2), "#F4EEE2", "#CFC4B2", "#FFFFFF", 345, 0, n=120, shade=(0, 8), shade_op=0.35, ink_w=2, ink_col="#8A7A62",
                  hi=(300, 452, 220, 3), hi_op=0.5))
    # potted plant on the sill
    pot = [(122, 400), (178, 400), (172, 448), (128, 448)]
    for i, (lx, ly, rot) in enumerate(((150, 360, -10), (128, 372, -50), (174, 368, 40), (140, 340, -20), (166, 344, 20), (116, 388, -75), (186, 390, 70))):
        o.append(leaf(u, "elm", lx, ly, 24, rot, ("#6E9A52", "#466E34", "#9CC27A"), 346 + i, detail=True, stem=False))
    o.append(form(u, rpoly(pot, 5), bbox(pot, 2), "#D27A4E", "#9A4E2A", "#EEA67A", 353, -90, n=40, shade=(8, 0), ink_w=2, ink_col="#5A2A14"))
    o.append(form(u, rpoly([(116, 396), (184, 396), (184, 410), (116, 410)], 4), (116, 396, 184, 410), "#E08A5A", "#A85A32", "#F2B48A", 354, 0, n=14, shade=None,
                  ink_w=2, ink_col="#5A2A14"))
    # the cat, from behind: round head, ear backs, pear body, tail curled along the sill
    coat = ("#9AA0A8", "#5E646E", "#D2D6DC")
    stripe = "#3E444E"
    inkc = "#2A2E36"
    cx = 318
    tail = tube([(cx + 66, 440), (cx + 104, 452), (cx + 132, 448), (cx + 150, 430), (cx + 146, 414)], 26, 14)
    o.append(fur(u, tail, coat, 355, 0, shade=(0, 5), ink_w=2.2, ink_col=inkc, length=(6, 12),
                 extra_in="".join(taper([(cx + x, 432), (cx + x + 4, 446), (cx + x + 2, 462)], 6, 3, stripe, 0.8) for x in (90, 112, 132))))
    body = [(cx, 300), (cx + 40, 308), (cx + 66, 340), (cx + 84, 386), (cx + 92, 426), (cx + 80, 450), (cx, 456), (cx - 80, 450), (cx - 92, 426),
            (cx - 84, 386), (cx - 66, 340), (cx - 40, 308)]

    def back_stripes():
        out = [f'<path d="{blob(cx, 380, 16, 76, 368, 0.1, 12)}" fill="{stripe}" opacity="0.3"/>']
        rnd2 = random.Random(369)
        for sg in (-1, 1):
            y = 318 + (8 if sg > 0 else 0)
            while y < 446:
                w = 30 + (y - 300) * 0.55
                L = rnd2.uniform(0.6, 1.0)
                x0 = cx + sg * rnd2.uniform(6, 14)
                x1 = cx + sg * (w + 16) * L
                out.append(taper([(x0, y - 4), ((x0 + x1) / 2, y + rnd2.uniform(0, 6)), (x1, y + 10 + rnd2.uniform(0, 8))], rnd2.uniform(6, 9), 1.5, stripe, 0.7))
                if rnd2.random() < 0.5:
                    xs = cx + sg * (w * 0.75 + 6)
                    out.append(taper([(xs, y + 12), (xs + sg * 10, y + 18), (xs + sg * 16, y + 26)], 4, 1.2, stripe, 0.5))
                y += rnd2.uniform(18, 26)
        return "".join(out)
    o.append(fur(u, body, coat, 356, lambda x, y: 90 + (x - cx) * 0.3, shade=(-14, 0), shade_op=0.3, length=(10, 22), width=(1.2, 2.8),
                 ink_w=2.4, ink_col=inkc, extra_in=back_stripes() + f'<path d="{blob(cx + 76, 380, 12, 60, 357, 0.1, 12)}" fill="#FFF4D2" opacity="0.18"/>'))
    o.append(feather([p for p in closed_curve(body, 6) if p[1] > 330], [coat[0], coat[2], coat[1]], 358, 2, (5, 11), (1.6, 2.8), down=0.5, cx=cx, cy=390))
    for sg in (-1, 1):
        ear = [(cx + sg * 22, 230), (cx + sg * 40, 186), (cx + sg * 50, 180), (cx + sg * 62, 228)]
        o.append(fur(u, ear, coat, 359 + sg, -90, shade=(sg * 4, 0), ink_w=2.2, ink_col=inkc, length=(5, 10), n=40))
        o.append(ink(smooth_open([(cx + sg * 40, 222), (cx + sg * 46, 196)]), "#E8B0A8", 2, 360, 1, 0.5))
    head = blob_pts(cx, 262, 64, 54, 361, 0.03, 18)
    o.append(fur(u, head, coat, 362, radial(cx, 300), shade=(-10, 6), shade_op=0.3, ink_w=2.4, ink_col=inkc, length=(6, 13),
                 extra_in="".join(taper([(cx + x, 216), (cx + x * 1.1, 240), (cx + x * 1.2, 266)], 7, 2, stripe, 0.8) for x in (-22, 0, 22)) +
                 "".join(taper([(cx + sg * 30, 270 + k * 14), (cx + sg * 50, 268 + k * 16), (cx + sg * 64, 272 + k * 16)], 2, 6, stripe, 0.6) for sg in (-1, 1) for k in (0, 1))))
    o.append(tufts([p for p in closed_curve(head, 6)], [coat[0], coat[2]], 363, 3, (3, 6), (1, 2), cx=cx, cy=262))
    o.append(ink(smooth_open([(cx + 60, 236), (cx + 66, 262), (cx + 58, 290)]), "#FFF4D2", 3, 364, 1, 0.6))
    for sg in (-1, 1):
        o.append(whiskers(cx + sg * 56, 290, sg, 8, 40, "#F4F2EE", 1.4, 365 + sg, n=2, op=0.7))
    o.append(ruled(u, 74, "PROFESSIONAL", JOS, 22, "#7A4E2A", 366, ls=8, line_w=34, line="#A0784E"))
    o.append(title(u, 300, 536, "bird watcher", SERIF_IT, 62, "#3A2A20", ["#2A1C12", "#5A4030", "#4A3424"], 367, max_w=420,
                   shadow="#F8EEDC", soff=(0.02, 0.03), angle=-30))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ---------------------------------------------------------------- nap queen — a fluffy white cat curled up asleep on a velvet cushion, crown askew
def curled_cat(u, cx, cy, s, coat, seed, inkc, flip=1, ear_in=("#F0B0AA", "#C07A76", "#FAD6D0"), nose=("#E8A0A0", "#B8606A", "#F8D0CC"),
               long=1.0, marks=None, head_marks=None, tail_coat=None, tail_marks=None, paw_coat=None, soft_edge=False):
    """A cat curled asleep, seen from the side/front: loaf body, head resting on its paws at the left, tail wrapped along the front."""
    def P(x, y):
        return (cx + flip * x * s, cy + y * s)

    def Ps(pts):
        return [P(x, y) for x, y in pts]
    out = [shadow(u, cx, cy + 74 * s, 190 * s, 22 * s, 0.35)]
    body = Ps([(-40, -70), (40, -84), (110, -72), (160, -34), (172, 10), (156, 52), (100, 74), (0, 78), (-90, 70), (-120, 30), (-110, -20), (-80, -56)])
    out.append(fur(u, body, coat, seed, lambda x, y: 0 if flip > 0 else 180, shade=(0, 16 * s), shade_op=0.3, length=(12 * s, 26 * s), width=(1.2, 3),
                   ink_w=2.4, ink_col=inkc, hi=(P(40, -50)[0], P(0, -50)[1], 70 * s, 16 * s), hi_op=0.3, extra_in=(marks(P) if marks else "")))
    fcol = [coat[0], coat[2], coat[2]] if soft_edge else [coat[0], coat[2], coat[1]]
    out.append(feather(closed_curve(body, 6)[::1], fcol, seed + 1, 2, (5 * s * long, 11 * s * long), (1.6, 3), down=0.3,
                       cx=P(30, 0)[0], cy=P(0, 0)[1]))
    # haunch curve
    out.append(ink(smooth_open(Ps([(70, 60), (120, 30), (130, -16), (100, -50)])), coat[1], 2.2, seed + 2, 1, 0.5))
    # tail wrapped along the front
    tl = tube(Ps([(150, 40), (120, 76), (40, 92), (-50, 90), (-104, 74), (-120, 56)]), 40 * s, 26 * s)
    tc = tail_coat or coat
    out.append(fur(u, tl, tc, seed + 3, lambda x, y: 180 if flip > 0 else 0, shade=(0, 8 * s), shade_op=0.35, length=(8 * s, 18 * s), width=(1.2, 2.6),
                   ink_w=2.2, ink_col=inkc, extra_in=(tail_marks(P) if tail_marks else "")))
    out.append(feather([p for p in closed_curve(tl, 6) if p[1] > P(0, 80)[1]], fcol if soft_edge else [tc[0], tc[2], tc[1]], seed + 4, 2, (4 * s * long, 9 * s * long), (1.4, 2.4), down=0.6,
                       cx=P(0, 70)[0], cy=P(0, 70)[1]))
    # paws tucked under the chin
    pc = paw_coat or coat
    for k, (x, y) in enumerate(((-96, 56), (-56, 62))):
        out.append(mitt(u, *P(x, y), 40 * s, 24 * s, pc, seed + 5 + k, inkc, rot=-flip * 8))
    # head
    hx, hy = P(-100, 4)
    for sg in (-1, 1):
        ear = Ps([(-100 + sg * 20, -38), (-100 + sg * 40, -84), (-100 + sg * 56, -80), (-100 + sg * 66, -30)])
        ear = rot_pts(ear, *P(-100 + sg * 40, -50), sg * 10 * flip)
        out.append(fur(u, ear, coat, seed + 7 + sg, -90 + sg * 20, shade=(sg * 4, 0), ink_w=2.2, ink_col=inkc, length=(5 * s, 11 * s), n=50))
        inner = Ps([(-100 + sg * 28, -44), (-100 + sg * 42, -76), (-100 + sg * 52, -72), (-100 + sg * 58, -38)])
        inner = rot_pts(inner, *P(-100 + sg * 40, -50), sg * 10 * flip)
        out.append(form(u, smooth_closed(inner), bbox(inner, 1), ear_in[0], ear_in[1], ear_in[2], seed + 9 + sg, -90, n=10, shade=(0, 4), ink_w=0))
    head = blob_pts(hx, hy, 74 * s, 62 * s, seed + 11, 0.03, 18)
    out.append(fur(u, head, coat, seed + 12, radial(hx, hy + 20 * s), shade=(10 * s, 8 * s), shade_op=0.3, length=(6 * s, 13 * s), width=(1, 2.2),
                   ink_w=2.4, ink_col=inkc, hi=(hx - 20 * s, hy - 30 * s, 26 * s, 12 * s), hi_op=0.3, extra_in=(head_marks((hx, hy), s) if head_marks else "")))
    out.append(feather([p for p in closed_curve(head, 6) if p[1] > hy], fcol, seed + 13, 2, (4 * s * long, 9 * s * long), (1.4, 2.4), down=0.4, cx=hx, cy=hy))
    # muzzle puffs, closed eyes, nose, smile
    for sg in (-1, 1):
        out.append(f'<path d="{blob(hx + sg * 13 * s, hy + 28 * s, 16 * s, 12 * s, seed + 14 + sg, 0.06, 12)}" fill="#FFFFFF" opacity="0.6"/>')
        ex, ey = hx + sg * 32 * s, hy + 2 * s
        out.append(ink(f"M {_f(ex - 15 * s)} {_f(ey - 2 * s)} Q {_f(ex)} {_f(ey + 10 * s)} {_f(ex + 15 * s)} {_f(ey - 2 * s)}", "#2A140A", 3.4 * s, seed + 16 + sg, 2, 1))
        for k in (-1, 0, 1):
            lx = ex + k * 8 * s + sg * 2 * s
            out.append(ink(f"M {_f(lx)} {_f(ey + 4.5 * s - abs(k) * 2 * s)} l {_f(k * 2 * s + sg * 1.5 * s)} {_f(5 * s)}", "#2A140A", 1.6 * s, seed, 1, 0.9))
        out.append(f'<path d="{blob(hx + sg * 44 * s, hy + 22 * s, 11 * s, 6 * s, seed + 18 + sg, 0.1, 10)}" fill="#F08A8A" opacity="0.35"/>')
        out.append(whiskers(hx + sg * 22 * s, hy + 30 * s, sg, 9, 58 * s, "#FFFFFF" if coat[0] != "#F6F0E6" else "#B8AEA4", 1.4, seed + 20 + sg, op=0.8))
    out.append(cat_nose(u, hx, hy + 20 * s, 15 * s, nose, seed + 22))
    out.append(cat_mouth(hx, hy + 26 * s, 10 * s, "#4A2A2A", seed + 23, max(1.4, 1.8 * s)))
    return "".join(out), (hx, hy)


def crown(u, cx, cy, w, h, seed, rot=0, pal=("#EEC04A", "#A8781A", "#FFE8A0"), jewels=("#D2483A", "#4E8AC8", "#5E9A4A")):
    pts = [(cx - w / 2, cy), (cx - w / 2 - 2, cy - h * 0.8), (cx - w * 0.28, cy - h * 0.38), (cx - w * 0.14, cy - h * 1.0), (cx, cy - h * 0.42),
           (cx + w * 0.14, cy - h * 1.0), (cx + w * 0.28, cy - h * 0.38), (cx + w / 2 + 2, cy - h * 0.8), (cx + w / 2, cy)]
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    out.append(form(u, rpoly(pts, 2), bbox(pts, 2), pal[0], pal[1], pal[2], seed, -90, n=w * 0.8, shade=(w * 0.08, 0), shade_op=0.45, ink_w=2,
                    ink_col="#5A3A0A", hi=(cx - w * 0.2, cy - h * 0.3, w * 0.1, h * 0.2), hi_op=0.5))
    band = [(cx - w / 2, cy - h * 0.2), (cx + w / 2, cy - h * 0.2), (cx + w / 2, cy + 2), (cx - w / 2, cy + 2)]
    out.append(form(u, rpoly(band, 2), bbox(band, 1), pal[1], mix(pal[1], "#000000", 0.3), pal[0], seed + 1, 0, n=10, shade=None, ink_w=1.6, ink_col="#5A3A0A"))
    for k, x in enumerate((-0.3, 0, 0.3)):
        out.append(f'<circle cx="{_f(cx + x * w)}" cy="{_f(cy - h * 0.09)}" r="{_f(h * 0.11)}" fill="{jewels[k % 3]}"/><circle cx="{_f(cx + x * w - 1)}" cy="{_f(cy - h * 0.12)}" r="{_f(h * 0.04)}" fill="#FFFFFF" opacity="0.8"/>')
    for x in (-0.5, -0.14, 0.14, 0.5):
        out.append(f'<circle cx="{_f(cx + x * w * (1.04 if abs(x) == 0.5 else 1))}" cy="{_f(cy - h * (0.82 if abs(x) == 0.5 else 1.02))}" r="{_f(h * 0.1)}" fill="#FFF2C8"/>')
    out.append("</g>")
    return "".join(out)


def cushion(u, cx, cy, w, h, seed, pal=("#C8506A", "#8A2A44", "#EE8AA0"), tassel="#E8B84A", inkc="#4A1222"):
    top = [(cx - w / 2, cy - h * 0.2), (cx - w * 0.25, cy - h * 0.5), (cx + w * 0.25, cy - h * 0.5), (cx + w / 2, cy - h * 0.2), (cx + w / 2 + 6, cy + h * 0.2),
           (cx + w * 0.25, cy + h * 0.5), (cx - w * 0.25, cy + h * 0.5), (cx - w / 2 - 6, cy + h * 0.2)]
    out = [shadow(u, cx, cy + h * 0.5, w * 0.55, h * 0.16, 0.35)]
    tufts_ = "".join(f'<circle cx="{_f(cx + dx * w)}" cy="{_f(cy + dy * h)}" r="3.4" fill="{inkc}" opacity="0.7"/>'
                     f'<path d="M {_f(cx + dx * w - 10)} {_f(cy + dy * h - 6)} Q {_f(cx + dx * w)} {_f(cy + dy * h)} {_f(cx + dx * w + 10)} {_f(cy + dy * h - 6)}" stroke="{inkc}" stroke-width="1.4" fill="none" opacity="0.4"/>'
                     for dx, dy in ((-0.3, 0.12), (0, 0.18), (0.3, 0.12)))
    out.append(form(u, smooth_closed(top), bbox(top, 4), pal[0], pal[1], pal[2], seed, 0, n=w * 1.2, shade=(0, h * 0.18), shade_op=0.4,
                    hi=(cx - w * 0.1, cy - h * 0.2, w * 0.3, h * 0.08), hi_op=0.35, ink_w=2.4, ink_col=inkc, extra_in=tufts_, length=(14, 40)))
    out.append(ink(smooth_open([(cx - w / 2 - 4, cy + h * 0.16), (cx, cy + h * 0.42), (cx + w / 2 + 4, cy + h * 0.16)]), tassel, 4, seed, 1, 0.9))
    for sg in (-1, 1):
        tx, ty = cx + sg * (w / 2 + 2), cy + h * 0.16
        out.append(f'<circle cx="{_f(tx)}" cy="{_f(ty)}" r="6" fill="{tassel}"/>')
        tas = [(tx - 6, ty + 4), (tx + 6, ty + 4), (tx + 10, ty + 30), (tx - 10, ty + 30)]
        out.append(form(u, rpoly(tas, 3), bbox(tas, 1), tassel, "#A8781A", "#FFE8A0", seed + sg, -90, n=20, shade=None, ink_w=1.4, ink_col="#6A4410",
                        length=(8, 20), width=(0.8, 1.6), sop=(0.4, 0.8)))
    return "".join(out)


@design("nap-queen")
def nap_queen():
    u = Ids("nap-queen")
    o = [bg(u, "#EADCEA", ["#E0D0E2", "#F4EAF2", "#D6C4DA"], 371, angle=-20)]
    o.append(glow(u, 300, 400, 260, "#FFF6F4", 0.8))
    rnd = random.Random(372)
    for _ in range(14):
        x, y = rnd.choice([rnd.uniform(60, 150), rnd.uniform(450, 540)]), rnd.uniform(200, 470)
        o.append(sparkle(x, y, rnd.uniform(4, 8), "#E8B84A", 0.9))
    o.append(cushion(u, 300, 470, 400, 120, 373))
    coat = ("#F6F2EE", "#CFC6C8", "#FFFFFF")
    cat_svg, (hx, hy) = curled_cat(u, 322, 386, 1.14, coat, 374, "#6A5A60", long=1.0, soft_edge=True)
    o.append(cat_svg)
    o.append(crown(u, hx + 30, hy - 58, 62, 40, 375, rot=18))
    # z z z
    for k, (x, y, sz) in enumerate(((112, 290, 30), (138, 252, 38), (172, 214, 46))):
        o.append(plain(x + 2, y + 2, "z", SERIF_IT, sz, "#FFFFFF") + plain(x, y, "z", SERIF_IT, sz, "#8A5A8A"))
    o.append(title(u, 300, 120, "nap", SERIF_IT, 76, "#7A3A5A", ["#8E4A6E", "#5A2440", "#A85A80"], 376, max_w=200, shadow="#FBF2F6", soff=(0.02, 0.03), angle=-30))
    o.append(ruled(u, 168, "QUEEN", CINZEL, 40, "#A8781A", 377, ls=10, line_w=40))
    o.append(finish(u, op=0.7))
    return "".join(o)


# ---------------------------------------------------------------- just kitten around — a kitten tangled up in yarn
def yarn_strand(pts, col, hi, seed, w=4.2):
    d = smooth_open(pts)
    return (f'<path d="{d}" fill="none" stroke="{mix(col, "#000000", 0.35)}" stroke-width="{w + 2:.1f}" stroke-linecap="round" opacity="0.55"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{hi}" stroke-width="{w * 0.3:.1f}" stroke-linecap="round" stroke-dasharray="5 7" opacity="0.8"/>')


@design("just-kitten-around")
def just_kitten_around():
    u = Ids("just-kitten-around")
    o = [bg(u, "#DCE8EE", ["#CCDCE6", "#E8F0F4", "#C2D4E0"], 381, angle=-20)]
    o.append(glow(u, 290, 400, 240, "#FFFFFF", 0.7))
    YARN = ("#E8708A", "#B04460", "#F8A8B8")
    coat = ("#F2C890", "#C88A50", "#FCE4C0")
    inkc = "#6A3E1A"
    stripe = "#D29050"

    def head_marks(cc):
        return cc.stripes(stripe, 382, op=0.6)

    c = Cat(u, 262, 330, 0.78, coat, 383, ink_c=inkc, eyes=("#8AC0E0", "#2E6E9E"), eye_r=30, eye_x=46, eye_y=4, ear_k=0.86, look=(0.25, -0.1),
            muzzle="#FFF4E6", chin_c="#FFF4E6", body=False, pupil_k=0.62, mouth="meow", ear_rot=-6)
    o.append(cat_ground(u, c, 230, 200, 0.3))

    def chest_marks(cc):
        return f'<path d="{blob(*cc.P(0, 150), 50 * cc.s, 90 * cc.s, 384, 0.08, 14)}" fill="#FFF4E6" opacity="0.9"/>'

    def sitbody(cc):
        return cat_sit(cc, bottom=226, chest_marks=chest_marks, tail_side=-1, bw=0.82)
    o.append(c.draw(head_marks, behind=sitbody))
    # the yarn ball and the strand that has tangled round the kitten
    o.append(shadow(u, 446, 518, 60, 10, 0.35))
    o.append(yarn(u, 440, 474, 46, YARN, 385))
    strand = [(404, 476), (360, 470), (310, 466), (256, 462), (204, 446), (184, 404), (192, 352), (206, 300), (226, 252), (256, 236), (288, 240),
              (318, 262), (336, 298), (342, 336)]
    o.append(yarn_strand(strand, YARN[0], YARN[2], 386))
    o.append(yarn_strand([(342, 336), (346, 360), (340, 380)], YARN[0], YARN[2], 387, 3.6))
    # one paw batting at the strand
    o.append(mitt(u, 330, 438, 44, 30, coat, 388, inkc, rot=-30))
    o.append(motion([[(372, 404), (386, 392)], [(378, 422), (396, 418)]], "#7A9AB8", 389, 2.4, 0.8))
    o.append(title(u, 300, 104, "just kitten", DMS, 72, "#2E4E66", ["#1E3A50", "#3E6280", "#2A4A62"], 390, max_w=420, shadow="#F4F8FA",
                   soff=(0.02, 0.03), angle=-60))
    o.append(title(u, 380, 160, "around", SERIF_IT, 56, "#B04460", ["#C85A76", "#8E2E48", "#E8708A"], 391, max_w=220, shadow="#F4F8FA",
                   soff=(0.02, 0.03), angle=-30))
    o.append(finish(u, op=0.75))
    return "".join(o)


# ---------------------------------------------------------------- crazy cat lady — four very different cats on the sofa
@design("crazy-cat-lady")
def crazy_cat_lady():
    u = Ids("crazy-cat-lady")
    o = [bg(u, "#D4E6DC", ["#C4DCD0", "#E2EEE8"], 401, angle=-80)]
    rnd = random.Random(402)
    for gy in range(20, 620, 52):
        for gx in range(10 + (26 if (gy // 52) % 2 else 0), 620, 52):
            o.append(flower(u, gx + rnd.uniform(-3, 3), gy + rnd.uniform(-3, 3), 7, ("#F2B8B0", "#C88078", "#FAD8D2"), gx + gy, center="#F2D06A"))
    o.append(vignette(u, "#4A6A5A", 0.3, 0.55))
    sofa = ("#D86A6A", "#9A3A40", "#F29A94")
    sink = "#5A1E22"
    # sofa back
    back = [(30, 600), (30, 350), (60, 312), (300, 300), (540, 312), (570, 350), (570, 600)]
    o.append(shadow(u, 300, 330, 280, 50, 0.3, "#1E3A2E"))
    o.append(form(u, smooth_closed(back), bbox(back, 2), sofa[0], sofa[1], sofa[2], 403, 0, n=320, shade=(0, -14), shade_op=0.3,
                  hi=(300, 320, 220, 8), hi_op=0.35, ink_w=2.6, ink_col=sink, length=(20, 60),
                  extra_in="".join(f'<circle cx="{x}" cy="{y}" r="3.6" fill="{sink}" opacity="0.6"/>' for x in range(90, 540, 60) for y in (362,))))
    W = ("#F6F0E6", "#D2C6B6", "#FFFFFF")
    cats = [
        (128, 388, 0.6, dict(coat=CAT_ORANGE, eyes=("#C8D86A", "#6E8A2A"), ink_c="#6A3410", muzzle="#FBEEDC", chin_c="#FBEEDC", mouth="meow", tilt=-10,
                              look=(-0.1, 0)), lambda c: c.stripes("#B05E22", 404, op=0.6), None),
        (244, 368, 0.62, dict(coat=CAT_BLACK, eyes=("#F6D04A", "#C0861A"), ink_c="#0A080A", ear_in=("#6A4A4E", "#3A2A2E", "#8A6A6E"), muzzle="#3A363C",
                              chin_c="#3A363C", nose=("#4A3E44", "#1A1416", "#7A6A70"), rim="#B8A8D0", tilt=6, pupil_k=0.75), None, None),
        (360, 382, 0.6, dict(coat=SIAM, eyes=("#9AD2F4", "#2E72B8"), ink_c="#4A3626", ear_in=SIAM_PT, muzzle="#7A6252", chin_c="#7A6252",
                              nose=("#5A4436", "#2A1E16", "#8A7060"), blink=True, tilt=-4),
         lambda c: c.patch([(0, -46), (24, -34), (50, -16), (74, 8), (78, 40), (60, 68), (30, 84), (0, 88), (-30, 84), (-60, 68), (-78, 40), (-74, 8), (-50, -16), (-24, -34)],
                           ("#7E6656", "#4E3A2C", "#A08470"), 405),
         lambda c, sg: c.patch(c.ear_local(sg), SIAM_PT, 406 + sg, soft=False)),
        (474, 392, 0.57, dict(coat=CAT_GREY, eyes=("#F0AA3A", "#B0601A"), ink_c="#2A2E36", muzzle="#B4BCC8", chin_c="#B4BCC8", cheek=1.15, ear_k=0.7,
                             lid=("#8A929E", 0.4), mouth="flat", tilt=10, look=(-0.3, 0)), lambda c: c.stripes("#5A626E", 407, op=0.5), None),
    ]
    for i, (x, y, s, kw, hm, em) in enumerate(cats):
        c = Cat(u, x, y, s, seed=410 + i * 10, body_len=240, whisk="#FFFFFF", **kw)
        o.append(c.draw(hm, None, em))
    # seat cushion front hides their bottoms
    seat = [(20, 500), (300, 490), (580, 500), (590, 560), (580, 620), (20, 620), (10, 560)]
    o.append(form(u, smooth_closed(seat), bbox(seat, 2), sofa[0], sofa[1], sofa[2], 450, 0, n=260, shade=(0, 14), shade_op=0.35,
                  hi=(300, 508, 230, 6), hi_op=0.4, ink_w=2.6, ink_col=sink, length=(20, 60)))
    o.append(ink("M 300 494 Q 302 560 300 620", sink, 2, 451, 1, 0.4))
    for sg in (-1, 1):
        o.append(ink(f"M {300 + sg * 150} 496 Q {300 + sg * 148} 560 {300 + sg * 150} 620", sink, 2, 452 + sg, 1, 0.3))
    # a ball of yarn with knitting needles, and a tail curling up at the end of the sofa
    o.append(yarn(u, 490, 530, 26, ("#7AA8D8", "#3E6E9E", "#B4D2F0"), 453))
    o.append(ink("M 462 546 L 520 502 M 468 554 L 528 512", "#C8963A", 3.6, 454, 1, 1))
    o.append(title(u, 300, 100, "crazy", SERIF_IT, 64, "#9A3A40", ["#B84A50", "#7A2228", "#D86A6A"], 455, max_w=260, shadow="#F4FAF6", soff=(0.02, 0.03), angle=-30))
    o.append(title(u, 300, 186, "CAT LADY", BEBAS, 104, "#2E4A3E", ["#1E3A2E", "#3E5E50", "#284438"], 456, max_w=440, ls=8, shadow="#F4FAF6",
                   soff=(0.02, 0.035), angle=-80))
    o.append(finish(u, op=0.75))
    return "".join(o)


# ================================================================ dogs, part A
W_COAT = ("#F6F0E6", "#D2C8BA", "#FFFFFF")


class MixDog(Dog):
    """A dog with mismatched ears (one up, one folded) - both drawn behind the head."""

    def __init__(self, *a, ear_pair=("prick", "button"), **kw):
        super().__init__(*a, **kw)
        self.ear_pair = ear_pair

    def _ears(self, marks_ear):
        res = []
        orig = self.ears
        for i in range(2):
            self.ears = self.ear_pair[i]
            res.append(Dog._ears(self, marks_ear)[i])
        self.ears = orig
        return res


# ---------------------------------------------------------------- adopt, don't shop — a scruffy mutt carrying its own leash
@design("adopt-dont-shop")
def adopt_dont_shop():
    u = Ids("adopt-dont-shop")
    o = [bg(u, "#D6E4EC", ["#C6D8E4", "#E4EEF4", "#BCD0DE"], 501, angle=-20)]
    rnd = random.Random(502)
    for _ in range(16):
        x, y = rnd.uniform(40, 560), rnd.uniform(180, 560)
        if 130 < x < 470:
            continue
        o.append(p_paw(u, x, y, 8, ("#B8CCDA", "#9AB0C2", "#D2E0EA"), int(x * y), rot=rnd.uniform(-40, 40), ink_w=0))
    o.append(spot(u, 300, 430, 220, 190, "#F2EEE4", ["#F8F4EC", "#E8E0D0"], 503, op=0.9))
    coat = ("#B89A72", "#7E6244", "#DCC4A0")
    inkc = "#4A3420"
    d = MixDog(u, 300, 368, 0.92, coat, 504, ink_c=inkc, ears="prick", ear_pair=("prick", "rose"), ear_len=0.95, ear_w=1.2, ear_rot=10,
               skull=78, cheek=86, nose_y=56, muzzle_w=36, kind="fluffy", fluff=0.7, face_tufts="fluffy", mouth="closed", tongue=False,
               eyes=("#9A5A26", "#3A1A08"), look=(0.05, 0.08), muzzle=W_COAT, chest_coat=W_COAT, brows=("#5A4430", 0.55), tilt=-8,
               ear_in=("#D8A898", "#A8746A", "#F2CCC0"))

    def head(dd):
        P = dd.P
        out = [dd.blaze(W_COAT, 505, 5, 12, 24)]
        # wiry scruff: little dark flecks and eyebrow tufts
        for sg in (-1, 1):
            out.append(dd.patch([(sg * 60, -30), (sg * 86, -10), (sg * 90, 30), (sg * 70, 40), (sg * 54, 10)], ("#8E7454", "#5E4A34", "#B49A78"), 506 + sg))
        return "".join(out)

    def muzzle_marks(dd):
        P = dd.P
        return "".join(ink(f"M {_f(P(x, 74)[0])} {_f(P(x, 74)[1])} l {_f(x * 0.12)} {_f(14)}", "#CFC2AE", 2, 507 + i, 1, 0.8)
                       for i, x in enumerate((-30, -20, -10, 10, 20, 30)))

    def leash(dd):
        P = dd.P
        out = []
        red = ("#C8463A", "#82221A", "#F2806A")
        loop = tube([P(-44, 74), P(-40, 98), P(-18, 128), P(10, 132), P(34, 108), P(42, 78)], 11, 11, 6)
        out.append(form(u, smooth_closed(loop), bbox(loop, 2), red[0], red[1], red[2], 508, 0, n=40, shade=(0, 3), ink_w=2, ink_col="#4A0E0A"))
        bite = tube([P(-46, 74), P(-20, 80), P(20, 80), P(46, 74)], 11, 11, 6)
        out.append(form(u, smooth_closed(bite), bbox(bite, 2), red[0], red[1], red[2], 509, 0, n=30, shade=(0, 3), ink_w=2, ink_col="#4A0E0A",
                        hi=(P(0, 76)[0], P(0, 76)[1], 24, 2), hi_op=0.6))
        strap = tube([P(10, 132), P(40, 190), P(110, 240), P(200, 300)], 11, 12, 6)
        out.append(form(u, smooth_closed(strap), bbox(strap, 2), red[0], red[1], red[2], 510, 0, n=60, shade=(0, 3), ink_w=2, ink_col="#4A0E0A"))
        x, y = P(10, 132)
        out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="8" fill="none" stroke="#C8C2B8" stroke-width="4"/><circle cx="{_f(x)}" cy="{_f(y)}" r="8" fill="none" stroke="#5A5650" stroke-width="1.2"/>')
        return "".join(out)

    def chest(dd):
        return collar(u, dd.Ps([(-80, 128), (-40, 142), (0, 146), (40, 142), (80, 128)]), 16, ("#3E7A9A", "#22506A", "#7AB0CC"), 511,
                      tag=("heart", ("#E8B84A", "#9A6A1A", "#FFE8A0")), tag_at=0.3)
    o.append(d.draw(marks_head=head, marks_muzzle=muzzle_marks, over_chest=chest, over_face=leash))
    o.append(title(u, 300, 116, "ADOPT", ANTON, 92, "#2E4E66", ["#1E3A50", "#3E6280", "#2A4A62"], 512, max_w=330, ls=10, shadow="#F4F8FA",
                   soff=(0.02, 0.035), angle=-80))
    o.append(ruled(u, 172, "don't shop", SERIF_IT, 44, "#C8463A", 513, ls=0, line_w=40, line="#C8463A"))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ---------------------------------------------------------------- small but mighty — a chihuahua in a superhero cape
def sunburst(cx, cy, n, col, op, r=600, w=0.07, rot=0):
    out = []
    for i in range(n):
        a = math.radians(rot + i * 360 / n)
        out.append(f'<path d="M {cx} {cy} L {_f(cx + r * math.cos(a - w))} {_f(cy + r * math.sin(a - w))} L {_f(cx + r * math.cos(a + w))} {_f(cy + r * math.sin(a + w))} Z" fill="{col}" opacity="{op}"/>')
    return "".join(out)


@design("small-but-mighty")
def small_but_mighty():
    u = Ids("small-but-mighty")
    o = [bg(u, "#F6D670", ["#F2C850", "#FAE290", "#ECBE48"], 521, angle=-20)]
    o.append(sunburst(300, 380, 28, "#F8E8A8", 0.45))
    o.append(glow(u, 300, 380, 200, "#FFF8E0", 0.6))
    coat = ("#E8BE88", "#B88850", "#FAE0B4")
    inkc = "#6A4220"
    cape = ("#D2483A", "#8E1E16", "#F2806A")

    def behind(dd):
        P = dd.P
        pts = [P(-70, 112), P(-130, 170), P(-172, 280), P(-196, 420), P(0, 440), P(150, 420), P(206, 336), P(262, 304), P(234, 256), P(272, 206), P(222, 172),
               P(150, 146), P(70, 112)]
        out = [form(u, smooth_closed(pts), bbox(pts, 2), cape[0], cape[1], cape[2], 522, lambda x, y: 90 + (x - dd.cx) * 0.4, n=300, shade=(0, -20),
                    shade_op=0.35, ink_w=2.6, ink_col="#4A0E0A", length=(20, 60), width=(1.6, 4),
                    hi=(P(-120, 260)[0], P(0, 260)[1], 30, 80), hi_op=0.25)]
        for x in (-150, -70):
            out.append(ink(smooth_open([P(x * 0.5, 160), P(x * 0.9, 280), P(x, 400)]), "#7A1A12", 2.4, 523 + x, 1, 0.45))
        for k in range(3):
            out.append(ink(smooth_open([P(90 + k * 10, 150), P(170 + k * 20, 200 + k * 30), P(200 + k * 10, 280 + k * 40)]), "#7A1A12", 2.4, 530 + k, 1, 0.4))
        return "".join(out)

    def clasp(dd):
        P = dd.P
        out = []
        # the cape's tie: a cord round the neck
        out.append(ink(smooth_open(dd.Ps([(-66, 112), (-34, 124), (0, 128), (34, 124), (66, 112)])), "#8E1E16", 5, 524, 1, 1))
        cx, cy = P(0, 128)
        badge = [(cx, cy - 20), (cx + 22, cy - 6), (cx + 14, cy + 18), (cx - 14, cy + 18), (cx - 22, cy - 6)]
        out.append(form(u, rpoly(badge, 4), bbox(badge, 2), "#F2C04A", "#A87A1A", "#FFE8A0", 525, -90, n=20, shade=(3, 3), ink_w=2, ink_col="#5A3A0A",
                        hi=(cx - 6, cy - 6, 5, 4), hi_op=0.6))
        out.append(zigzag(cx, cy + 1, 13, "#D2483A", 526))
        return "".join(out)

    d = Dog(u, 290, 352, 0.95, coat, 527, ink_c=inkc, ears="prick", ear_len=1.25, ear_w=2.0, ear_rot=42, ear_x=0, ear_y=30, skull=86, cheek=84, top=-92,
            dome=0, round_top=1.0, nose_y=40, muzzle_w=27, stop_w=12, eye_x=40, eye_r=20, mouth="smile", kind="smooth", nose_w=20, chin=74, jowl=60, cheek_shade=0.12,
            neck=0.95, chest_w=0.85, chest_len=240, look=(0.12, 0.0), eyes=("#7A4418", "#2A1206"), ear_in=("#EAA898", "#B87468", "#F8D2C6"),
            muzzle=("#F4DCB8", "#C8A070", "#FFF2DE"), brows=("#C8965A", 0.5), tilt=-4)

    def head(dd):
        return dd.blaze(("#F8E8CC", "#D8BC94", "#FFF8EC"), 528, 4, 9, 16)

    def chest(dd):
        return dd.bib(("#F8E8CC", "#D8BC94", "#FFF8EC"), 529, 0.8, dd.nose_y + 30)
    o.append(d.draw(marks_head=head, marks_chest=chest, behind=behind, over_chest=clasp))
    o.append(title(u, 300, 98, "small", SERIF_IT, 64, "#8E1E16", ["#B8322A", "#6E1610", "#D2483A"], 530, max_w=260, shadow="#FFF4D0", soff=(0.02, 0.03), angle=-30))
    o.append(title(u, 300, 172, "BUT MIGHTY", ANTON, 64, "#8E1E16", ["#B8322A", "#6E1610", "#D2483A"], 531, max_w=420, ls=6, shadow="#FFF4D0",
                   soff=(0.025, 0.04), angle=-80))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ---------------------------------------------------------------- spoiled rotten — a pomeranian in a quilted handbag, pearls and a bow
@design("spoiled-rotten")
def spoiled_rotten():
    u = Ids("spoiled-rotten")
    o = [bg(u, "#F4DCE0", ["#EED0D6", "#F8E8EC", "#E8C4CC"], 541, angle=-20)]
    o.append(glow(u, 300, 380, 240, "#FFF6F6", 0.8))
    o.append(stars_field(542, 22, (60, 180, 540, 540), col="#D8A43A", avoid=lambda x, y: 140 < x < 460, s=(4, 9)))
    coat = ("#E89A4E", "#B0642A", "#F8C688")
    inkc = "#6A3410"
    d = Dog(u, 300, 292, 0.92, coat, 543, ink_c="#B87038", ears="prick", ear_len=0.55, ear_w=0.7, ear_rot=6, ear_x=-8, ear_y=8, skull=82, cheek=96, top=-84,
            dome=4, round_top=1.0, nose_y=38, muzzle_w=24, stop_w=12, eye_x=40, eye_r=17, mouth="grin", kind="fluffy", fluff=0.8, face_tufts="smooth", nose_w=22,
            chin=70, look=(0.0, 0.1), eyes=("#6A3A18", "#1E0C04"), muzzle=("#F2B070", "#C8844A", "#FCD8A8"), chest_w=0.85, chest_len=200, stroke_len=0.8,
            ear_in=("#E8A890", "#B87060", "#F8D0C0"), tongue_pal=("#F07A8A", "#C04A5E", "#FAB0BA"), mouth_w=0.8)

    def ruff(dd):
        # the big mane of fur framing the face
        P = dd.P
        ring = fluffy(blob_pts(*P(0, 30), 126 * dd.s, 116 * dd.s, 544, 0.03, 24), 12, 544, 5, 0.9)
        out = [fur(u, ring, coat, 545, radial(*P(0, 30)), shade=(0, 12), shade_op=0.25, length=(10, 22), width=(1.4, 3), ink_w=2, ink_col=inkc, ink_op=0.5,
                   density=1.2, hi=(P(-50, -40)[0], P(0, -40)[1], 40, 24), hi_op=0.3)]
        out.append(feather(closed_curve(ring, 2)[::3], [coat[0], coat[2], coat[0]], 546, 1, (4, 8), (3, 5), down=0.3, op=(0.6, 0.95),
                           cx=P(0, 30)[0], cy=P(0, 30)[1]))
        return "".join(out)
    # handbag: back panel first, then the dog, then the front panel
    bag = ("#F2A4BC", "#C25A7A", "#FBD2DE")
    bk = [(150, 380), (450, 380), (440, 410), (160, 410)]
    o.append(form(u, rpoly(bk, 8), bbox(bk, 2), mix(bag[0], bag[1], 0.4), bag[1], bag[0], 547, 0, n=40, shade=None, ink_w=2, ink_col="#7A2A44"))
    o.append(ink("M 196 392 Q 300 190 404 392", "#C8963A", 7, 548, 1, 1) + ink("M 196 392 Q 300 190 404 392", "#FFE8A0", 2, 549, 1, 0.7))
    o.append(d.draw(behind=ruff))
    front = [(130, 396), (470, 396), (486, 556), (114, 556)]
    quilt = "".join(f'<path d="M {x} 380 L {x + 180} 580 M {x + 180} 380 L {x} 580" stroke="#C25A7A" stroke-width="1.6" opacity="0.45"/>' for x in range(20, 600, 40))
    quilt += "".join(f'<circle cx="{x + (20 if ((y - 396) // 20) % 2 else 0)}" cy="{y}" r="1.6" fill="#7A2A44" opacity="0.5"/>' for x in range(110, 500, 40) for y in range(416, 556, 20))
    o.append(shadow(u, 300, 560, 210, 14, 0.35))
    o.append(form(u, rpoly(front, 16), bbox(front, 2), bag[0], bag[1], bag[2], 550, 0, n=200, shade=(0, 16), shade_op=0.3, ink_w=2.6, ink_col="#7A2A44",
                  extra_in=quilt, hi=(220, 420, 70, 10), hi_op=0.4))
    # gold clasp
    o.append(form(u, rpoly([(280, 404), (320, 404), (320, 430), (280, 430)], 6), (280, 404, 320, 430), "#F2C04A", "#A87A1A", "#FFE8A0", 551, 0, n=10,
                  shade=(2, 3), ink_w=2, ink_col="#5A3A0A", hi=(292, 410, 6, 3), hi_op=0.7))
    # pearls round the neck, front paws on the bag rim, bow on the head
    for i in range(13):
        t = i / 12
        x = 236 + 128 * t
        y = 362 + 22 * math.sin(math.pi * t)
        o.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="6.4" fill="#F8F2E8"/><circle cx="{_f(x)}" cy="{_f(y)}" r="6.4" fill="none" stroke="#B8A890" stroke-width="1.2"/>'
                 f'<circle cx="{_f(x - 2)}" cy="{_f(y - 2.2)}" r="2" fill="#FFFFFF"/>')
    for sg in (-1, 1):
        o.append(mitt(u, 300 + sg * 66, 398, 46, 30, coat, 552 + sg, inkc))
    o.append(bow(u, 374, 196, 28, ("#F2A4BC", "#C25A7A", "#FBD2DE"), 553, rot=20, tails=False, dots="#FFFFFF"))
    o.append(title(u, 300, 102, "spoiled", SERIF_IT, 70, "#A83A5E", ["#C25A7A", "#8A2A4E", "#D8708E"], 554, max_w=300, shadow="#FFF4F6", soff=(0.02, 0.03), angle=-30))
    o.append(title(u, 300, 514, "ROTTEN", CINZEL, 50, "#7A2244", ["#8E2E52", "#5A1430", "#A23E62"], 555, max_w=280, ls=8, shadow="#FCE2EA",
                   soff=(0.03, 0.05), angle=-60))
    o.append(finish(u, op=0.75))
    return "".join(o)


# ---------------------------------------------------------------- treat yo self — a beagle licking its nose beside the biscuit jar
@design("treat-yo-self")
def treat_yo_self():
    u = Ids("treat-yo-self")
    o = [bg(u, "#CFE4DE", ["#C0DAD2", "#E0EEEA"], 561, angle=-80)]
    # kitchen tiles
    for gy in range(0, 440, 44):
        for gx in range(0, 620, 44):
            o.append(f'<rect x="{gx + 2}" y="{gy + 2}" width="40" height="40" rx="4" fill="#E6F2EE" opacity="0.5"/>')
    o.append(vignette(u, "#3A6A5E", 0.25, 0.55))
    coat = ("#C8803E", "#8A4E1E", "#E8A866")
    inkc = "#5A2E10"
    d = Dog(u, 246, 290, 0.98, coat, 564, ink_c=inkc, ears="hound", ear_coat=("#B06A2C", "#743A12", "#D48E4E"), ear_len=1.0, nose_y=60, muzzle_w=38,
            mouth="grin", tongue=False, kind="smooth", muzzle=W_COAT, chest_coat=W_COAT, look=(0.55, -0.1), eyes=("#7A3A14", "#2A1206"), tilt=6,
            chest_len=240, brows=("#E8A866", 0.4))

    def head(dd):
        return dd.blaze(W_COAT, 565, 5, 8, 10)

    def chest_marks(dd):
        P = dd.P
        return dd.patch([(90, 120), (150, 140), (170, 260), (110, 280), (96, 200)], ("#2E2420", "#141010", "#5A4C44"), 566) + \
            dd.patch([(-90, 120), (-150, 140), (-170, 260), (-110, 280), (-96, 200)], coat, 567)

    def lick(dd):
        P = dd.P
        cx, cy = P(14, 70)
        return tongue(u, cx, cy, 24, 34, 568, rot=200)
    o.append(d.draw(marks_head=head, marks_chest=chest_marks, over_face=lick))
    # counter in front of the dog
    top = [(-20, 440), (620, 440), (620, 470), (-20, 470)]
    o.append(form(u, rpoly(top, 3), bbox(top, 2), "#F2E6D2", "#C8B494", "#FFFFFF", 562, 0, n=120, length=(40, 120), shade=(0, -5), ink_w=2.2, ink_col="#7A6448"))
    front = [(-20, 470), (620, 470), (620, 620), (-20, 620)]
    o.append(form(u, rpoly(front, 3), bbox(front, 2), "#6E9A8A", "#4A7464", "#9AC2B2", 563, -90, n=160, length=(30, 80), shade=(0, 8), ink_w=2.2, ink_col="#2E4E42"))
    for x in (150, 450):
        o.append(ink(f"M {x} 480 L {x} 620", "#2E4E42", 2, x, 1, 0.4))
    for sg in (-1, 1):
        o.append(mitt(u, 246 + sg * 56, 444, 50, 30, W_COAT, 569 + sg, inkc))
    # glass biscuit jar
    jx, jy, jw, jh = 450, 300, 130, 140
    jar = [(jx - jw / 2, jy), (jx + jw / 2, jy), (jx + jw / 2 + 6, jy + 20), (jx + jw / 2 + 6, jy + jh - 10), (jx + jw / 2 - 6, jy + jh), (jx - jw / 2 + 6, jy + jh),
           (jx - jw / 2 - 6, jy + jh - 10), (jx - jw / 2 - 6, jy + 20)]
    o.append(shadow(u, jx, jy + jh + 2, jw * 0.6, 8, 0.35))
    o.append(f'<path d="{rpoly(jar, 10)}" fill="#E8F4F2" opacity="0.55"/>')
    rnd = random.Random(570)
    for row in range(5):
        for k in range(3):
            bx = jx - 36 + k * 36 + rnd.uniform(-6, 6)
            by = jy + jh - 18 - row * 22 + rnd.uniform(-3, 3)
            if row == 4 and k != 1:
                continue
            o.append(p_bone(u, bx, by, 38, 8, 571 + row * 3 + k, rot=rnd.uniform(-40, 40), pal=("#D8A060", "#9A6430", "#F2C890"), inkc="#6A4018"))
    o.append(f'<path d="{rpoly(jar, 10)}" fill="none" stroke="#7AA6A0" stroke-width="2.6" opacity="0.8"/>')
    o.append(ink(f"M {jx - jw / 2 + 12} {jy + 22} L {jx - jw / 2 + 12} {jy + jh - 24}", "#FFFFFF", 6, 572, 1, 0.6))
    o.append(ink(f"M {jx - jw / 2 + 26} {jy + 30} L {jx - jw / 2 + 26} {jy + 70}", "#FFFFFF", 3, 573, 1, 0.5))
    # label
    lab = [(jx - 44, jy + 48), (jx + 44, jy + 48), (jx + 44, jy + 84), (jx - 44, jy + 84)]
    o.append(form(u, rpoly(lab, 4), bbox(lab, 1), "#F8F0DC", "#D8C8A4", "#FFFFFF", 574, 0, n=14, shade=None, ink_w=1.6, ink_col="#8A7448"))
    o.append(plain(jx, jy + 74, "TREATS", BEBAS, 26, "#B8462A", 80, ls=2))
    # lid, set aside, leaning on the jar
    lid = [(jx - 58, jy - 8), (jx + 58, jy - 8), (jx + 58, jy + 6), (jx - 58, jy + 6)]
    o.append(f'<g transform="rotate(-14 {jx} {jy})">' + form(u, rpoly(lid, 6), bbox(lid, 1), "#D2483A", "#8E1E16", "#F2806A", 575, 0, n=20, shade=(0, 3), ink_w=2,
                                                               ink_col="#4A0E0A") +
             form(u, blob(jx, jy - 16, 12, 9, 576, 0.06, 10), (jx - 12, jy - 25, jx + 12, jy - 7), "#D2483A", "#8E1E16", "#F2806A", 576, 0, n=6, shade=None, ink_w=2,
                  ink_col="#4A0E0A") + "</g>")
    # crumbs and one stolen biscuit
    o.append(p_bone(u, 380, 448, 34, 7, 577, rot=-12, pal=("#D8A060", "#9A6430", "#F2C890"), inkc="#6A4018"))
    for (x, y) in ((356, 452), (408, 456), (420, 446)):
        o.append(f'<circle cx="{x}" cy="{y}" r="2.4" fill="#B8803E"/>')
    o.append(title(u, 300, 104, "treat", SERIF_IT, 74, "#B8462A", ["#D2583A", "#8E2E16", "#E8784A"], 578, max_w=240, shadow="#F4FAF6", soff=(0.02, 0.03), angle=-30))
    o.append(title(u, 300, 534, "YO SELF", BEBAS, 70, "#FBF3E4", ["#FFFFFF", "#E2EEEA", "#CFE4DE"], 579, max_w=300, ls=10, shadow="#2E4E42",
                   soff=(0.025, 0.04), angle=-80))
    o.append(finish(u, op=0.75))
    return "".join(o)


# ---------------------------------------------------------------- home is where the dog is — a corgi pushing through the dog flap
@design("home-is-where-the-dog-is")
def home_dog():
    u = Ids("home-is-where-the-dog-is")
    o = [bg(u, "#EADCC6", ["#E0CEB2", "#F2E6D4"], 581, angle=-80)]
    # painted brick wall around the door
    rnd = random.Random(582)
    for r, y in enumerate(range(0, 620, 26)):
        for x in range(-40 + (30 if r % 2 else 0), 640, 60):
            o.append(f'<path d="{rpoly([(x + 2, y + 2), (x + 57, y + 2), (x + 57, y + 23), (x + 2, y + 23)], 3)}" fill="{rnd.choice(["#D88A6A", "#C87A5A", "#E09A7A", "#CC8262"])}" opacity="0.55"/>')
    o.append(vignette(u, "#6A3A2A", 0.3, 0.55))
    # door frame, door, panels
    df = [(150, 600), (150, 196), (450, 196), (450, 600)]
    o.append(shadow(u, 304, 400, 170, 230, 0.35))
    o.append(form(u, rpoly(df, 4), bbox(df, 2), "#F4EEE2", "#CFC4B2", "#FFFFFF", 583, -90, n=80, shade=(6, 0), ink_w=2.4, ink_col="#7A6A52"))
    door = [(170, 600), (170, 214), (430, 214), (430, 600)]
    o.append(form(u, rpoly(door, 3), bbox(door, 2), "#3E7A9A", "#22506A", "#7AB0CC", 584, -90, n=300, shade=(14, 0), shade_op=0.35, ink_w=2.4, ink_col="#14324A",
                  length=(30, 80)))
    # window panes in the top of the door
    for (x0, y0) in ((196, 236), (306, 236)):
        pane = [(x0, y0), (x0 + 98, y0), (x0 + 98, y0 + 80), (x0, y0 + 80)]
        o.append(form(u, rpoly(pane, 4), bbox(pane, 1), "#F6E6B0", "#D8B868", "#FFF8DC", 585 + x0, -90, n=30, shade=None, ink_w=2.4, ink_col="#14324A"))
        o.append(ink(f"M {x0 + 49} {y0} L {x0 + 49} {y0 + 80} M {x0} {y0 + 40} L {x0 + 98} {y0 + 40}", "#14324A", 3, 586, 1, 0.8))
        o.append(ink(f"M {x0 + 10} {y0 + 30} L {x0 + 30} {y0 + 10}", "#FFFFFF", 3, 587, 1, 0.6))
    # raised panels
    for (x0, y0, w, h) in ((196, 338, 98, 70), (306, 338, 98, 70)):
        o.append(f'<path d="{rpoly([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)], 4)}" fill="none" stroke="#14324A" stroke-width="2.4" opacity="0.6"/>'
                 f'<path d="M {x0 + 3} {y0 + h - 2} L {x0 + w - 2} {y0 + h - 2} L {x0 + w - 2} {y0 + 3}" stroke="#7AB0CC" stroke-width="2" fill="none" opacity="0.6"/>')
    # brass knob and a heart-shaped name plate
    o.append(form(u, blob(408, 420, 10, 10, 588, 0.03, 12), (398, 410, 418, 430), "#E8B84A", "#9A6A1A", "#FFE8A0", 588, 0, n=8, shade=(2, 2),
                  hi=(405, 416, 3, 2), hi_op=0.9, ink_w=1.8, ink_col="#5A3A0A"))
    # the dog flap with the corgi coming through
    fx0, fy0, fx1, fy1 = 222, 430, 378, 560
    o.append(form(u, rpoly([(fx0 - 10, fy0 - 10), (fx1 + 10, fy0 - 10), (fx1 + 10, fy1 + 10), (fx0 - 10, fy1 + 10)], 10), (fx0 - 10, fy0 - 10, fx1 + 10, fy1 + 10),
                  "#C8C2B8", "#8A847A", "#F2EEE6", 589, 0, n=30, shade=(4, 4), ink_w=2.2, ink_col="#3A3632"))
    o.append(f'<path d="{rpoly([(fx0, fy0), (fx1, fy0), (fx1, fy1), (fx0, fy1)], 8)}" fill="#2A1E18"/>')
    # the flap itself pushed up and back
    flap = [(fx0 + 2, fy0), (fx1 - 2, fy0), (fx1 - 8, fy0 - 40), (fx0 + 8, fy0 - 40)]
    o.append(form(u, rpoly(flap, 6), bbox(flap, 1), "#9AA0A8", "#5E646E", "#D2D6DC", 590, 0, n=20, shade=(0, -4), ink_w=2, ink_col="#2A2E36"))
    coat = ("#D88A40", "#A45A1E", "#F2B470")
    inkc = "#6A3410"
    clip = u("flap")
    o.append(f'<clipPath id="{clip}"><path d="M 0 0 L 600 0 L 600 {fy1} L 0 {fy1} Z"/></clipPath><g clip-path="url(#{clip})">')
    d = Dog(u, 300, 452, 0.62, coat, 591, ink_c=inkc, ears="prick", ear_len=1.05, ear_w=1.5, ear_rot=16, mouth="open", nose_y=54, muzzle_w=34, kind="medium",
            muzzle=W_COAT, cheek=90, chest_coat=W_COAT, chest_len=200, look=(0.0, 0.0), eyes=("#7A3A14", "#2A1206"))

    def head(dd):
        return dd.blaze(W_COAT, 592, 5, 4, 16)
    o.append(d.draw(marks_head=head))
    o.append("</g>")
    for sg in (-1, 1):
        o.append(mitt(u, 300 + sg * 46, 556, 44, 28, W_COAT, 593 + sg, inkc))
    # door mat
    mat = [(170, 566), (430, 566), (440, 600), (160, 600)]
    o.append(form(u, rpoly(mat, 4), (160, 566, 440, 620), "#B88A4A", "#8A5E2A", "#D8AE6E", 595, -90, n=120, length=(4, 10), width=(0.8, 1.6), shade=None,
                  ink_w=2, ink_col="#5A3A14", sop=(0.4, 0.8)))
    # potted plant at the side
    for i, (lx, ly, rot) in enumerate(((506, 404, -10), (488, 420, -50), (526, 418, 40), (498, 380, -20), (518, 384, 20), (480, 448, -75), (532, 446, 70))):
        o.append(leaf(u, "elm", lx, ly, 28, rot, ("#6E9A52", "#466E34", "#9CC27A"), 596 + i, detail=True, stem=False))
    pot = [(472, 466), (540, 466), (532, 540), (480, 540)]
    o.append(form(u, rpoly(pot, 5), bbox(pot, 2), "#D27A4E", "#9A4E2A", "#EEA67A", 603, -90, n=40, shade=(8, 0), ink_w=2, ink_col="#5A2A14"))
    o.append(title(u, 300, 94, "home is where", SERIF_IT, 56, "#3A2418", ["#2A1608", "#5A3420", "#4A2A18"], 604, max_w=420, shadow="#F8EEDC", soff=(0.02, 0.03), angle=-30))
    o.append(title(u, 300, 170, "THE DOG IS", BEBAS, 74, "#22405A", ["#2E5272", "#14304A", "#3E6280"], 605, max_w=420, ls=8, shadow="#FBF3E4", soff=(0.025, 0.04), angle=-80))
    o.append(finish(u, op=0.75))
    return "".join(o)


# ================================================================ dogs, part B
def full_moon(u, cx, cy, r, seed):
    out = [glow(u, cx, cy, r * 1.9, "#FFF6D8", 0.4), glow(u, cx, cy, r * 1.25, "#FFF8E4", 0.5)]
    out.append(form(u, blob(cx, cy, r, r, seed, 0.01, 24), (cx - r, cy - r, cx + r, cy + r), "#F6EED4", "#D8CCA4", "#FFFDF0", seed, -30, n=r * 3,
                    shade=(r * 0.08, r * 0.08), shade_op=0.35, length=(r * 0.1, r * 0.35), width=(1.2, 3), ink_w=0))
    rnd = random.Random(seed)
    for _ in range(9):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, r * 0.75)
        cr = rnd.uniform(r * 0.05, r * 0.14)
        out.append(f'<path d="{blob(cx + rr * math.cos(a), cy + rr * math.sin(a), cr, cr * 0.85, rnd.randint(0, 999), 0.1, 10)}" fill="#D8CCA4" opacity="0.45"/>')
    return "".join(out)


def snow(seed, n, box, avoid=None, col="#FFFFFF"):
    rnd = random.Random(seed)
    out = []
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if avoid and avoid(x, y):
            continue
        r = rnd.uniform(1.4, 3.6)
        out.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r)}" fill="{col}" opacity="{rnd.uniform(0.6, 0.95):.2f}"/>')
    return "".join(out)


def pine(u, x, base, h, seed, pal=("#2E4A4E", "#1A2E34", "#4E6E70"), snowcap=True):
    """Painted fir: stacked drooping tiers, snow on the tiers."""
    rnd = random.Random(seed)
    out = [f'<path d="M {_f(x - 3)} {_f(base)} L {_f(x + 3)} {_f(base)} L {_f(x + 2)} {_f(base - h * 0.2)} L {_f(x - 2)} {_f(base - h * 0.2)} Z" fill="#3A2A20"/>']
    tiers = 5
    for i in range(tiers):
        t = i / tiers
        w = h * (0.42 - t * 0.3)
        yb = base - h * (0.12 + t * 0.72)
        yt = yb - h * 0.28
        pts = [(x, yt), (x + w * 0.4, yb - h * 0.1), (x + w, yb + 2), (x + w * 0.5, yb - 4), (x, yb + 3), (x - w * 0.5, yb - 4), (x - w, yb + 2), (x - w * 0.4, yb - h * 0.1)]
        out.append(form(u, smooth_closed(jitter(pts, seed + i, 1)), bbox(pts, 2), pal[0], pal[1], pal[2], seed + i, -90, n=w * 0.8, shade=(w * 0.15, 0),
                        shade_op=0.4, ink_w=0, length=(4, 10), width=(0.8, 1.8)))
        if snowcap:
            out.append(f'<path d="{smooth_open([(x - w * 0.8, yb - 1), (x - w * 0.4, yb - h * 0.08), (x, yt + h * 0.12), (x + w * 0.4, yb - h * 0.09), (x + w * 0.85, yb)])}" '
                       f'fill="none" stroke="#F4F8FC" stroke-width="{_f(max(2, h * 0.035))}" stroke-linecap="round" opacity="0.9"/>')
    return "".join(out)


def notes(x, y, s, col, seed, rot=0):
    """A pair of beamed music notes."""
    return (f'<g transform="rotate({rot} {_f(x)} {_f(y)})">'
            f'<ellipse cx="{_f(x)}" cy="{_f(y)}" rx="{_f(s * 0.32)}" ry="{_f(s * 0.24)}" fill="{col}" transform="rotate(-20 {_f(x)} {_f(y)})"/>'
            f'<ellipse cx="{_f(x + s * 0.7)}" cy="{_f(y - s * 0.12)}" rx="{_f(s * 0.32)}" ry="{_f(s * 0.24)}" fill="{col}" transform="rotate(-20 {_f(x + s * 0.7)} {_f(y - s * 0.12)})"/>'
            f'<path d="M {_f(x + s * 0.28)} {_f(y)} L {_f(x + s * 0.28)} {_f(y - s)} L {_f(x + s * 0.98)} {_f(y - s * 1.12)} L {_f(x + s * 0.98)} {_f(y - s * 0.12)}" '
            f'stroke="{col}" stroke-width="{_f(s * 0.1)}" fill="none"/><path d="M {_f(x + s * 0.28)} {_f(y - s)} L {_f(x + s * 0.98)} {_f(y - s * 1.12)}" stroke="{col}" stroke-width="{_f(s * 0.22)}"/></g>')


# ---------------------------------------------------------------- fluent in husky — a husky singing to the full moon in the snow
@design("fluent-in-husky")
def fluent_in_husky():
    u = Ids("fluent-in-husky")
    o = [sky(u, [(0, "#16243E"), (0.55, "#24385E"), (1, "#3E5682")], ["#1E2E4E", "#2C4068", "#1A2846"], 601, n=120)]
    o.append(stars_field(602, 60, (20, 20, 580, 420), avoid=lambda x, y: (x - 300) ** 2 + (y - 330) ** 2 < 170 ** 2))
    o.append(full_moon(u, 300, 322, 128, 603))
    # distant snowy hills and firs
    from fall_gouache_b import hill
    o.append(hill(u, [(-20, 470), (140, 440), (320, 462), (480, 436), (620, 456)], 620, "#B4C4DA", "#8A9CB8", "#D8E2F0", 604))
    for i, (x, b, h) in enumerate(((70, 480, 150), (120, 470, 110), (520, 476, 160), (474, 470, 104), (34, 476, 90))):
        o.append(pine(u, x, b, h, 605 + i * 7))
    coat = ("#6E7480", "#3E424C", "#9EA6B0")
    inkc = "#22242A"
    W = ("#F6F4F2", "#C8CCD4", "#FFFFFF")
    d = Dog(u, 300, 334, 0.92, coat, 620, ink_c=inkc, ears="prick", ear_len=0.85, ear_w=0.95, ear_rot=6, nose_y=58, muzzle_w=36, mouth="howl",
            kind="fluffy", fluff=0.6, face_tufts="smooth", muzzle=W, chest_coat=W, blink=True, tilt=-10, chest_len=240, round_top=0.6, cheek=90,
            ear_in=("#E8B0A8", "#B47A74", "#F8D4CC"))

    def head(dd):
        return dd.patch([(0, -30), (12, -24), (18, -4), (34, 16), (66, 18), (86, 36), (80, 70), (50, 104), (0, 110), (-50, 104), (-80, 70), (-86, 36), (-66, 18),
                         (-34, 16), (-18, -4), (-12, -24)], W, 621) + dd.patch([(-8, -86), (8, -86), (10, -46), (0, -36), (-10, -46)], ("#4A4E58", "#2A2C34", "#6E7480"), 622) + \
            "".join(f'<path d="{blob(*dd.P(sg * 36, -26), 13 * dd.s, 6 * dd.s, 623 + sg, 0.1, 10, rot=sg * 12)}" fill="#FFFFFF" opacity="0.9"/>' for sg in (-1, 1))
    o.append(d.draw(marks_head=head))
    # snow bank in front
    bank = [(-20, 520), (120, 500), (300, 512), (470, 498), (620, 516), (620, 620), (-20, 620)]
    o.append(form(u, smooth_closed(bank), bbox(bank, 2), "#E8EEF6", "#B8C6DA", "#FFFFFF", 624, 0, n=200, length=(30, 90), shade=(0, -10), shade_op=0.25,
                  ink_w=2, ink_col="#7A8AA8"))
    o.append(snow(625, 90, (20, 20, 580, 560), avoid=lambda x, y: (x - 300) ** 2 / 140 ** 2 + (y - 360) ** 2 / 200 ** 2 < 1))
    # song
    o.append(notes(430, 250, 26, "#F8E6A8", 626, rot=10) + notes(470, 200, 20, "#F8E6A8", 627, rot=-8))
    o.append(title(u, 300, 88, "fluent in", SERIF_IT, 50, "#F8E6A8", ["#FFF2C8", "#E8C878", "#F8E0A0"], 628, max_w=280, angle=-30, shadow="#0E1628", soff=(0.02, 0.04)))
    o.append(title(u, 300, 168, "HUSKY", BEBAS, 96, "#F4F6FA", ["#FFFFFF", "#D8E0EC", "#B4C4DA"], 629, max_w=300, ls=14, shadow="#3E5682", soff=(0.025, 0.04), angle=-80))
    o.append(title(u, 300, 534, "awoo!", SERIF_IT, 40, "#2E3E5E", ["#3E5682", "#1E2E4E"], 630, max_w=200, angle=-30))
    o.append(finish(u, op=0.6, color="#0A0E1A"))
    return "".join(o)


# ---------------------------------------------------------------- windows down — a border collie with its head out of the car window
@design("windows-down")
def windows_down():
    u = Ids("windows-down")
    o = [sky(u, [(0, "#7EC0E2"), (0.6, "#BEE0EE"), (1, "#F2EAD0")], ["#94CCE6", "#D2EAF2"], 641, n=80)]
    o.append(glow(u, 520, 110, 150, "#FFF6D0", 0.9))
    from fall_gouache_b import hill
    o.append(hill(u, [(-20, 300), (160, 270), (360, 292), (620, 262)], 620, "#A8C88A", "#7EA066", "#CCE2AE", 642))
    o.append(hill(u, [(-20, 330), (200, 314), (420, 330), (620, 318)], 620, "#8AB46E", "#5E8A4C", "#B4D494", 643))
    # speed streaks over the landscape
    rnd = random.Random(644)
    for _ in range(18):
        x, y = rnd.uniform(-40, 560), rnd.uniform(220, 330)
        o.append(f'<path d="M {_f(x)} {_f(y)} l {_f(rnd.uniform(60, 140))} 0" stroke="#FFFFFF" stroke-width="{rnd.uniform(1.5, 3.5):.1f}" stroke-linecap="round" opacity="0.45"/>')
    car = ("#E8806A", "#B04E3C", "#F8B49E")
    cink = "#5A1E14"
    # car body: roof, windshield sloping down to the hood, door below the belt line
    body = [(-20, 620), (-20, 236), (40, 222), (380, 214), (420, 226), (510, 330), (590, 352), (630, 372), (630, 620)]
    o.append(form(u, smooth_closed(body), bbox(body, 2), car[0], car[1], car[2], 645, 0, n=300, shade=(0, -10), shade_op=0.3, ink_w=2.6, ink_col=cink,
                  hi=(200, 224, 170, 5), hi_op=0.5, length=(30, 80)))
    o.append(ink("M 420 228 Q 470 280 508 330", "#FFFFFF", 4, 646, 1, 0.5))
    win = [(96, 384), (102, 256), (124, 240), (366, 236), (402, 248), (478, 376), (474, 384)]
    o.append(f'<path d="{rpoly(win, 12)}" fill="#2E3E4A"/>')
    o.append(f'<path d="{blob(150, 330, 40, 70, 647, 0.05, 12)}" fill="#C8A46A" opacity="0.5"/>')
    o.append(f'<path d="{rpoly(win, 12)}" fill="none" stroke="#D8DCE0" stroke-width="7"/><path d="{rpoly(win, 12)}" fill="none" stroke="#7A8088" stroke-width="1.6"/>')
    coat = ("#2C282C", "#100E10", "#5E5864")
    W = ("#F6F2EC", "#D0C8BE", "#FFFFFF")
    d = Dog(u, 300, 304, 0.98, coat, 648, ink_c="#0A080A", ears="drop", ear_len=0.85, ear_w=1.0, ear_rot=-82, nose_y=56, muzzle_w=34, mouth="open",
            kind="medium", fluff=0.6, face_tufts="medium", muzzle=W, chest_coat=W, look=(0.3, -0.1), tilt=12, chest_len=150, eyes=("#9A5A26", "#3A1A08"),
            ear_coat=("#2C282C", "#100E10", "#5E5864"), round_top=0.5)

    def head(dd):
        return dd.blaze(W, 649, 6, 12, 16)
    o.append(d.draw(marks_head=head))
    # door panel below the belt line hides the chest
    door = [(-20, 388), (630, 388), (630, 620), (-20, 620)]
    o.append(form(u, rpoly(door, 4), bbox(door, 2), car[0], car[1], car[2], 650, 0, n=300, shade=(0, 14), shade_op=0.3, ink_w=0, length=(30, 90)))
    o.append(ink("M -20 388 L 630 388", cink, 2.6, 651, 1, 0.8))
    o.append(form(u, rpoly([(-20, 384), (630, 384), (630, 398), (-20, 398)], 4), (-20, 384, 630, 398), "#E8ECEE", "#9AA0A8", "#FFFFFF", 652, 0, n=60, shade=(0, 3),
                  ink_w=1.8, ink_col="#5A6068", hi=(300, 388, 260, 2), hi_op=0.8))
    o.append(ink("M 486 400 L 486 620", cink, 2, 653, 1, 0.45))
    o.append(form(u, rpoly([(100, 422), (150, 422), (150, 434), (100, 434)], 6), (100, 422, 150, 434), "#E8ECEE", "#9AA0A8", "#FFFFFF", 654, 0, n=8, shade=None,
                  ink_w=1.6, ink_col="#5A6068"))
    # front wheel arch and tyre, headlight
    o.append(f'<path d="M 440 620 A 92 92 0 0 1 624 620 Z" fill="#3A1A14"/>')
    o.append(form(u, blob(532, 640, 76, 76, 655, 0.01, 20), (456, 564, 608, 716), "#2A2A2E", "#121214", "#5A5A60", 655, radial(532, 640), n=60, shade=None, ink_w=2,
                  ink_col="#000000"))
    o.append(form(u, blob(532, 640, 40, 40, 656, 0.01, 18), (492, 600, 572, 680), "#D8DCE0", "#8A9098", "#FFFFFF", 656, 0, n=20, shade=(3, 3), ink_w=1.8,
                  ink_col="#4A5058", hi=(518, 618, 10, 6), hi_op=0.8))
    o.append(form(u, blob(606, 420, 22, 26, 657, 0.03, 14), (584, 394, 628, 446), "#FFF4C8", "#D8C078", "#FFFFFF", 657, 0, n=10, shade=(3, 3), ink_w=2.2,
                  ink_col="#5A6068"))
    # paws over the door edge
    for x in (264, 348):
        o.append(mitt(u, x, 390, 46, 30, W, 658 + x, "#0A080A"))
    # side mirror at the bottom of the windscreen pillar
    o.append(ink("M 470 372 L 492 352", cink, 5, 659, 1, 1))
    o.append(form(u, blob(504, 340, 26, 17, 660, 0.06, 12), (478, 322, 530, 358), car[0], car[1], car[2], 660, 0, n=20, shade=(3, 3), ink_w=2.2, ink_col=cink))
    o.append(motion([[(150, 180), (90, 176)], [(166, 160), (110, 150)], [(150, 200), (104, 204)]], "#FFFFFF", 661, 3, 0.85))
    o.append(title(u, 300, 96, "windows down", SERIF_IT, 64, "#B04E3C", ["#C85A44", "#8E3A2A", "#E8806A"], 656, max_w=440, shadow="#FFFFFF", soff=(0.02, 0.03), angle=-30))
    o.append(title(u, 250, 528, "EARS UP", BEBAS, 76, "#FBF3E4", ["#FFFFFF", "#F8E2D6", "#F2C8B8"], 657, max_w=330, ls=12, shadow="#5A1E14", soff=(0.025, 0.04), angle=-80))
    o.append(finish(u, op=0.7))
    return "".join(o)


# ---------------------------------------------------------------- paws & relax — a frenchie in sunglasses on a pool float
@design("paws-and-relax")
def paws_and_relax():
    u = Ids("paws-and-relax")
    o = [sky(u, [(0, "#5EC4D2"), (1, "#2E9AB4")], ["#72D0DC", "#3EA8C0", "#8ADCE4"], 661, n=160, angle=-20)]
    # caustic light net on the water
    rnd = random.Random(662)
    for gy in range(-20, 640, 46):
        for gx in range(-20, 640, 52):
            x, y = gx + rnd.uniform(-10, 10), gy + rnd.uniform(-8, 8)
            cell = [(x + 26 * math.cos(a) + rnd.uniform(-6, 6), y + 22 * math.sin(a) + rnd.uniform(-5, 5)) for a in [k * 1.047 for k in range(6)]]
            o.append(f'<path d="{smooth_closed(cell)}" stroke="#E8FAFC" stroke-width="{rnd.uniform(1.2, 2.6):.1f}" fill="none" opacity="{rnd.uniform(0.12, 0.3):.2f}"/>')
    cx, cy = 300, 432
    # ripples round the float
    for k, (rx, ry) in enumerate(((236, 140), (262, 160))):
        o.append(f'<ellipse cx="{cx}" cy="{cy + 6}" rx="{rx}" ry="{ry}" fill="none" stroke="#FFFFFF" stroke-width="2.4" opacity="{0.4 - k * 0.15}"/>')
    o.append(f'<ellipse cx="{cx + 10}" cy="{cy + 26}" rx="210" ry="110" fill="#1E6E86" opacity="0.35"/>')
    stripes = ["#F28AA4", "#FFFFFF"]

    def ring_part(front):
        out = []
        n = 12
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            mid = (a0 + a1) / 2
            if (math.sin(mid) > 0) != front:
                continue
            pts = []
            for k in range(7):
                a = a0 + (a1 - a0) * k / 6
                pts.append((cx + 204 * math.cos(a), cy + 108 * math.sin(a)))
            for k in range(7):
                a = a1 - (a1 - a0) * k / 6
                pts.append((cx + 112 * math.cos(a), cy + 54 * math.sin(a)))
            col = stripes[i % 2]
            shade = 0.25 + 0.25 * (1 - math.sin(mid)) / 2 if front else 0.45
            d = "M " + " L ".join(f"{_f(x)} {_f(y)}" for x, y in pts) + " Z"
            out.append(f'<path d="{d}" fill="{col}"/><path d="{d}" fill="#7A1E3A" opacity="{0.12 if col == "#FFFFFF" else 0.0}"/>')
        # tube volume: highlight along the top and a shadow along the inner/outer bottom
        g = u("rg")
        out.append(f'<defs><radialGradient id="{g}" cx="{cx}" cy="{cy - 30}" r="230" gradientUnits="userSpaceOnUse"><stop offset="0.45" stop-color="#7A1E3A" stop-opacity="0.35"/>'
                   f'<stop offset="0.62" stop-color="#FFFFFF" stop-opacity="0"/><stop offset="0.85" stop-color="#FFFFFF" stop-opacity="0.15"/><stop offset="1" stop-color="#7A1E3A" stop-opacity="0.35"/></radialGradient></defs>')
        return "".join(out), g
    back, g1 = ring_part(False)
    cid = u("rc")
    ring_d = (f"M {cx - 204} {cy} A 204 108 0 1 0 {cx + 204} {cy} A 204 108 0 1 0 {cx - 204} {cy} Z "
              f"M {cx - 112} {cy} A 112 54 0 1 1 {cx + 112} {cy} A 112 54 0 1 1 {cx - 112} {cy} Z")
    o.append(back + f'<path d="{ring_d}" fill="url(#{g1})" fill-rule="evenodd" clip-path="none"/>')
    # the frenchie sitting in the ring
    coat = ("#DCBC8C", "#A8845A", "#F4E0BC")
    inkc = "#5A3A1A"
    d = Dog(u, 300, 318, 0.92, coat, 663, ink_c=inkc, ears="bat", ear_w=0.85, ear_len=0.66, ear_rot=10, ear_x=4, ear_y=6, kind="smooth", skull=86, cheek=100,
            jowl=78, nose_y=36, muzzle_w=48, stop_w=16, wrinkles=2, mouth="smile", flews=1.0, eye_x=48, eye_r=16, chin=84, puff=1.5, nose_w=44,
            muzzle=("#DCBC8C", "#A8845A", "#F4E0BC"), ear_in=("#D8A49A", "#9A6A60", "#F0C8BC"), chest_len=150, chest_w=1.0, round_top=0.8, dome=2)

    def muzzle_marks(dd):
        return dd.patch([(0, 6), (22, 10), (40, 30), (50, 60), (44, 90), (0, 100), (-44, 90), (-50, 60), (-40, 30), (-22, 10)], ("#5A4434", "#3A2A20", "#7A6250"), 664)

    def shades(dd):
        P = dd.P
        s_ = dd.s
        out = []
        for sg in (-1, 1):
            gx, gy = P(sg * 46, 2)
            lens = blob_pts(gx, gy, 34 * s_, 26 * s_, 665 + sg, 0.03, 16)
            out.append(form(u, smooth_closed(lens), bbox(lens, 2), "#2A2A3A", "#0E0E18", "#5A5A7A", 666 + sg, -30, n=20, shade=(0, 4), ink_w=4.4, ink_col="#F28AA4",
                            hi=(gx - 12 * s_, gy - 10 * s_, 10 * s_, 4 * s_), hi_op=0.7))
            out.append(ink(f"M {_f(gx - 18 * s_)} {_f(gy + 10 * s_)} L {_f(gx - 4 * s_)} {_f(gy - 8 * s_)}", "#FFFFFF", 3 * s_, 667, 1, 0.45))
        out.append(ink(smooth_open([P(-14, -4), P(0, -10), P(14, -4)]), "#F28AA4", 4.4, 668, 1, 1))
        return "".join(out)
    dclip = u("dc")
    o.append(f'<clipPath id="{dclip}"><rect x="0" y="0" width="600" height="{cy}"/><ellipse cx="{cx}" cy="{cy}" rx="112" ry="54"/></clipPath>'
             f'<g clip-path="url(#{dclip})">{d.draw(marks_muzzle=muzzle_marks, over_face=shades)}</g>')
    front, g2 = ring_part(True)
    cid2 = u("fc")
    o.append(f'<clipPath id="{cid2}"><rect x="0" y="{cy}" width="600" height="300"/></clipPath><g clip-path="url(#{cid2})">{front}'
             f'<path d="{ring_d}" fill="url(#{g2})" fill-rule="evenodd"/></g>')
    o.append(f'<path d="{ring_d}" fill="none" stroke="#8A2A44" stroke-width="2.2" opacity="0.7"/>')
    o.append(ink(f"M {cx - 170} {cy + 50} Q {cx} {cy + 98} {cx + 170} {cy + 50}", "#FFFFFF", 6, 669, 1, 0.5))
    # paws draped over the ring
    for x in (252, 348):
        o.append(mitt(u, x, cy + 52, 48, 30, coat, 670 + x, inkc))
    # a little drink with a straw and umbrella floating beside
    gx, gy = 486, 520
    glass = [(gx - 18, gy - 40), (gx + 18, gy - 40), (gx + 13, gy), (gx - 13, gy)]
    o.append(shadow(u, gx, gy + 2, 26, 6, 0.35, "#0E4A5A"))
    o.append(f'<path d="{rpoly(glass, 4)}" fill="#F8D06A" opacity="0.85"/>' + f'<path d="{rpoly(glass, 4)}" fill="none" stroke="#FFFFFF" stroke-width="2.4" opacity="0.9"/>')
    o.append(ink(f"M {gx + 6} {gy - 36} L {gx + 22} {gy - 70}", "#E85A6A", 3, 671, 1, 1))
    o.append(f'<path d="M {gx - 6} {gy - 40} L {gx - 30} {gy - 66} M {gx - 50} {gy - 60} Q {gx - 30} {gy - 86} {gx - 10} {gy - 64} Z" stroke="#5A3A1A" stroke-width="1.6" fill="#7AC8A8"/>')
    o.append(f'<circle cx="{gx + 12}" cy="{gy - 40}" r="7" fill="#F2E86A"/><path d="M {gx + 6} {gy - 40} L {gx + 18} {gy - 40}" stroke="#C8B02A" stroke-width="1.4"/>')
    o.append(title(u, 300, 102, "paws &", SERIF_IT, 66, "#FBF3E4", ["#FFFFFF", "#E2F6F8"], 672, max_w=300, shadow="#1E6E86", soff=(0.02, 0.04), angle=-30))
    o.append(title(u, 300, 176, "RELAX", BEBAS, 92, "#F28AA4", ["#F6A2B6", "#D25A7A", "#FFC2D0"], 673, max_w=300, ls=14, shadow="#1E5E76", soff=(0.025, 0.04), angle=-80))
    o.append(finish(u, op=0.6, color="#0E3A4A"))
    return "".join(o)


# ---------------------------------------------------------------- life is ruff — a basset hound flat on the rug, ears everywhere
@design("life-is-ruff")
def life_is_ruff():
    u = Ids("life-is-ruff")
    o = [bg(u, "#EEDCC0", ["#E4CEAC", "#F6EAD6"], 681, angle=-15)]
    o.append(floor_boards(u, 400, 682, rows=4))
    # a striped rug
    rug = [(40, 430), (560, 430), (580, 560), (20, 560)]
    rcid = u("rug")
    rstr = "".join(f'<rect x="0" y="{y}" width="600" height="12" fill="{c}" opacity="0.9"/>' for y, c in zip(range(430, 570, 24), ["#C8563A", "#E8B84A", "#4E7A8A", "#C8563A", "#E8B84A", "#4E7A8A"]))
    o.append(shadow(u, 300, 560, 280, 14, 0.3))
    o.append(form(u, rpoly(rug, 6), bbox(rug, 2), "#F2E6CE", "#C8B494", "#FFFFFF", 683, 0, n=200, length=(20, 60), shade=None, ink_w=2.2, ink_col="#7A5A3A",
                  extra_in=rstr + brush((20, 430, 580, 560), ["#FFFFFF", "#5A3A1A"], 684, 200, 0, (6, 20), (1, 2), (0.1, 0.3))))
    for x in range(36, 580, 14):
        o.append(f'<path d="M {x} 560 l {x % 3 - 1} 12" stroke="#E8D8B8" stroke-width="2.4" stroke-linecap="round"/>')
    coat = ("#B8783A", "#7A4818", "#DCA060")
    blackc = ("#3A302C", "#1A1412", "#6A5C56")
    inkc = "#4A2410"
    # the long body lying behind, black saddle
    body = [(120, 470), (130, 400), (190, 350), (300, 336), (420, 344), (490, 380), (510, 440), (480, 474)]
    o.append(fur(u, body, coat, 685, 0, shade=(0, 14), shade_op=0.3, length=(12, 26), width=(1.2, 2.8), ink_w=2.4, ink_col=inkc,
                 extra_in=f'<path d="{blob(330, 362, 150, 34, 686, 0.08, 16)}" fill="{blackc[0]}" opacity="0.95"/>' +
                 brush((180, 330, 480, 400), [blackc[2], blackc[1]], 687, 120, 0, (10, 24), (1, 2.2), (0.2, 0.5))))
    o.append(ink(smooth_open([(470, 380), (520, 344), (540, 318), (536, 300)]), blackc[0], 9, 688, 1, 1))
    o.append(ink(smooth_open([(536, 312), (540, 300), (534, 290)]), "#F6F0E6", 7, 689, 1, 1))
    W = ("#F6F0E6", "#D2C8BA", "#FFFFFF")
    d = Dog(u, 300, 374, 0.96, coat, 690, ink_c=inkc, ears="hound", ear_len=1.45, ear_w=1.3, ear_rot=-22, nose_y=70, muzzle_w=40, mouth="closed", tongue=False,
            flews=1.8, kind="smooth", muzzle=W, chest=False, look=(0.0, 0.25), eyes=("#7A3A14", "#2A1206"), brows=("#E8A866", 0.4), jowl=64, chin=124, skull=72, cheek=80,
            ear_coat=("#8E5222", "#5A2E0E", "#B87440"), wrinkles=2)

    def head(dd):
        return dd.blaze(W, 691, 5, 9, 10)

    def droopy(dd):
        P = dd.P
        out = []
        for sg in (-1, 1):
            ex, ey = P(sg * dd.eye_x, 0)
            r = dd.eye_r * dd.s
            lid = rot_pts([(ex - r * 1.15, ey - r * 0.05), (ex - r * 0.5, ey - r * 0.25), (ex + r * 0.5, ey - r * 0.25), (ex + r * 1.15, ey - r * 0.05),
                           (ex + r * 0.6, ey - r * 1.3), (ex - r * 0.6, ey - r * 1.3)], ex, ey, sg * 10)
            out.append(f'<path d="{smooth_closed(lid)}" fill="{coat[0]}"/>')
            out.append(ink(smooth_open(lid[:4]), "#24140A", 2.6, 692 + sg, 2, 0.95))
            out.append(ink(f"M {_f(ex - r * 0.9)} {_f(ey + r * 0.8)} Q {_f(ex)} {_f(ey + r * 1.25)} {_f(ex + r * 0.9)} {_f(ey + r * 0.8)}", "#C25A5A", 2.4, 693 + sg, 1, 0.7))
        return "".join(out)
    o.append(d.draw(marks_head=head, over_face=droopy))
    # front paws stretched out in front, chin almost on them
    for sg in (-1, 1):
        o.append(limb(u, [(300 + sg * 66, 474), (300 + sg * 72, 504), (300 + sg * 76, 520)], 48, 46, W, 694 + sg, inkc, flow=lambda x, y: 90))
        o.append(mitt(u, 300 + sg * 76, 524, 60, 30, W, 696 + sg, inkc))
    o.append(title(u, 300, 106, "life is", SERIF_IT, 64, "#7A4818", ["#8E5A22", "#5A300E", "#A86A30"], 698, max_w=260, shadow="#FBF2E2", soff=(0.02, 0.03), angle=-30))
    o.append(title(u, 300, 196, "RUFF", ANTON, 100, "#C8563A", ["#D86A4A", "#A43E26", "#E88A60"], 699, max_w=260, ls=14, shadow="#4A2410", soff=(0.025, 0.04),
                   angle=-80, hi="#FFD6B8"))
    o.append(plain(470, 306, "sigh...", SERIF_IT, 26, "#7A5A3A", 120))
    o.append(finish(u, op=0.75))
    return "".join(o)


# ================================================================ dogs, part C
def dog_sit(d, coat=None, chest_marks=None, b=330, leg_coat=None, tail=None, bw=1.0, haunch_marks=None):
    """Sitting dog body seen from the front, in a Dog's local units: haunches, deep chest with the front legs painted into it, paws.
    `tail(d)` is drawn after the haunch it rises from."""
    u, s = d.u, d.s
    coat = coat or d.chest_coat
    ic = d.ink_c
    L = lambda pts: d.Ps([(x * bw, y) for x, y in pts])
    out = []
    for sg in (-1, 1):
        hp = blob_pts(*L([(sg * 84, b - 58)])[0], 58 * s * bw, 64 * s, d.seed + 80 + sg, 0.05, 16, rot=sg * 10)
        out.append(fur(u, hp, coat, d.seed + 80 + sg, radial(*L([(sg * 60, b - 80)])[0]), shade=(sg * 12 * s, 8 * s), shade_op=0.35,
                       length=(8 * s, 16 * s), width=(1.2, 2.6), ink_w=2.2, ink_col=ic, extra_in=(haunch_marks(d, sg) if haunch_marks else "")))
        fp = blob_pts(*L([(sg * 110, b - 6)])[0], 34 * s, 14 * s, d.seed + 82 + sg, 0.05, 12)
        out.append(fur(u, fp, leg_coat or coat, d.seed + 82 + sg, 0, shade=(0, 3 * s), length=(4 * s, 9 * s), width=(0.8, 1.6), ink_w=2, ink_col=ic, n=40))
    if tail:
        out.append(tail(d))
    chest = L(sym([(0, 80), (62, 88), (90, 130), (98, 200), (92, b - 70), (74, b - 20), (0, b - 10)], 0))
    out.append(fur(u, chest, coat, d.seed + 84, lambda x, y: 90 + (x - d.cx) * 0.25, shade=(-14 * s, 0), shade_op=0.32, length=(9 * s, 20 * s),
                   width=(1.2, 2.8), ink_w=2.2, ink_col=ic, hi=(*L([(-36, 170)])[0], 22 * s, 40 * s), hi_op=0.25,
                   extra_in=(chest_marks(d) if chest_marks else "")))
    lc = leg_coat or coat
    out.append(f'<path d="{blob(*L([(0, (220 + b) / 2)])[0], 12 * s * bw, (b - 220) / 2 * s, d.seed + 85, 0.08, 12)}" fill="{coat[1]}" opacity="0.5"/>')
    for sg in (-1, 1):
        out.append(ink(smooth_open(L([(sg * 20, 214), (sg * 22, 270), (sg * 22, b - 20)])), ic, 1.8, d.seed + 86 + sg, 1, 0.5))
        out.append(ink(smooth_open(L([(sg * 74, 200), (sg * 72, 260), (sg * 70, b - 20)])), ic, 1.8, d.seed + 87 + sg, 1, 0.35))
        out.append(mitt(u, *L([(sg * 46, b - 8)])[0], 56 * s * bw, 30 * s, lc, d.seed + 88 + sg, ic))
    return "".join(out)


# ---------------------------------------------------------------- bark less, wag more — a jack russell grinning, tail going like mad
@design("bark-less-wag-more")
def bark_less_wag_more():
    u = Ids("bark-less-wag-more")
    o = [sky(u, [(0, "#A8D8EE"), (0.7, "#D8EEF4"), (1, "#F4F2DC")], ["#B8E0F0", "#E2F2F6"], 701, n=70)]
    for k, (cx, cy) in enumerate(((110, 250), (500, 220))):
        o.append("".join(f'<path d="{blob(cx + dx, cy + dy, r, r * 0.7, k * 10 + i, 0.1, 12)}" fill="#FFFFFF" opacity="0.85"/>'
                         for i, (dx, dy, r) in enumerate(((0, 0, 30), (26, -8, 24), (-24, 4, 20), (46, 6, 18)))))
    from fall_gouache_b import hill
    o.append(hill(u, [(-20, 470), (160, 452), (360, 462), (620, 446)], 620, "#9CC47A", "#6E9A52", "#C4DE9A", 702))
    rnd = random.Random(703)
    for _ in range(40):
        x, y = rnd.uniform(20, 580), rnd.uniform(500, 590)
        if 170 < x < 430 and y < 560:
            continue
        o.append(f'<g>{"".join(f"<circle cx=\"{x + 3.6 * math.cos(a):.1f}\" cy=\"{y + 3.6 * math.sin(a):.1f}\" r=\"2.6\" fill=\"#FFFFFF\"/>" for a in (0, 1.26, 2.51, 3.77, 5.03))}'
                 f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.9" fill="#F2C04A"/></g>')
    W = ("#F8F4EC", "#D2C8BA", "#FFFFFF")
    tan = ("#C8803E", "#8A4E1E", "#E8A866")
    inkc = "#4A2A14"
    d = Dog(u, 300, 282, 0.84, W, 704, ink_c=inkc, ears="rose", ear_coat=tan, ear_len=1.1, ear_w=1.3, ear_y=8, nose_y=52, muzzle_w=32, mouth="open",
            kind="smooth", look=(0.0, 0.05), eyes=("#7A3A14", "#2A1206"), chest=False, ear_in=("#D8A08A", "#A86E5C", "#F2C8B8"), round_top=0.6, tilt=-8,
            muzzle=W)

    def head(dd):
        P = dd.P
        return dd.patch([(-86, -20), (-70, -70), (-30, -90), (-6, -60), (-14, -24), (-40, -6), (-70, 4)], tan, 705, flow=radial(*P(-50, -40))) + \
            dd.patch([(40, -90), (80, -72), (90, -40), (60, -40)], tan, 706)

    def wag(dd):
        P = dd.P
        out = []
        for k, (ang, op) in enumerate(((-14, 0.25), (8, 0.45), (30, 1.0))):
            a = math.radians(ang)
            base = P(92, 250)
            tip = (base[0] + 120 * dd.s * math.sin(a), base[1] - 120 * dd.s * math.cos(a))
            mid = ((base[0] + tip[0]) / 2 + 14, (base[1] + tip[1]) / 2)
            tp = tube([base, mid, tip], 22 * dd.s, 9 * dd.s)
            if op < 1:
                out.append(f'<path d="{smooth_closed(tp)}" fill="{W[1]}" opacity="{op}"/>')
            else:
                out.append(fur(u, tp, W, 707, -60, shade=(4, 0), ink_w=2, ink_col=inkc, length=(5, 10), n=60))
        for k in range(3):
            r = 140 * dd.s + k * 14
            bx, by = P(92, 250)
            out.append(ink(f"M {_f(bx + r * 0.1)} {_f(by - r)} A {_f(r)} {_f(r)} 0 0 1 {_f(bx + r * 0.95)} {_f(by - r * 0.3)}", "#5A8AA8", 2.6, 708 + k, 1, 0.6))
        return "".join(out)

    def chest_marks(dd):
        return ""
    o.append(shadow(u, 300, 570, 150, 14, 0.3, "#2A4A1E"))
    def haunch(dd, sg):
        return dd.patch([(sg * 40, 250), (sg * 110, 240), (sg * 130, 300), (sg * 70, 300)], tan, 714 + sg) if sg > 0 else ""
    o.append(dog_sit(d, coat=W, b=330, tail=wag, haunch_marks=haunch))
    o.append(d.draw(marks_head=head))
    o.append(collar(u, d.Ps([(-62, 104), (-32, 116), (0, 120), (32, 116), (62, 104)]), 14, ("#D2483A", "#8E1E16", "#F2806A"), 709, tag=("bone", GOLD_TAG), tag_at=0.5))
    # a red ball waiting
    o.append(shadow(u, 470, 560, 30, 7, 0.35, "#2A4A1E"))
    o.append(form(u, blob(468, 534, 26, 26, 710, 0.02, 16), (442, 508, 494, 560), "#D2483A", "#8E1E16", "#F2806A", 710, radial(468, 534), n=40, shade=(5, 5),
                  hi=(460, 524, 7, 5), hi_op=0.8, ink_w=2, ink_col="#4A0E0A"))
    o.append(ink("M 446 532 Q 468 520 490 536", "#FFFFFF", 3, 711, 1, 0.8))
    o.append(title(u, 300, 98, "bark less", SERIF_IT, 64, "#2E5A7A", ["#3E6E92", "#1E4060", "#4E82A8"], 712, max_w=320, shadow="#FFFFFF", soff=(0.02, 0.03), angle=-30))
    o.append(title(u, 300, 172, "WAG MORE", BEBAS, 82, "#D2483A", ["#E2604A", "#A8301E", "#F2806A"], 713, max_w=380, ls=10, shadow="#FFFFFF", soff=(0.025, 0.04),
                   angle=-80, hi="#FFD6C8"))
    o.append(finish(u, op=0.7))
    return "".join(o)


# ---------------------------------------------------------------- best friends fur-ever — a lab puppy and a tabby kitten, cheek to cheek
@design("best-friends-fur-ever")
def best_friends():
    u = Ids("best-friends-fur-ever")
    o = [bg(u, "#F6E2D2", ["#F0D4C0", "#FAEEE4", "#EACAB2"], 721, angle=-25)]
    o.append(spot(u, 300, 410, 250, 200, "#FBEEE2", ["#FFF6EE", "#F2DED0"], 722, op=0.9))
    rnd = random.Random(723)
    for _ in range(12):
        x, y = rnd.choice([rnd.uniform(60, 140), rnd.uniform(460, 540)]), rnd.uniform(200, 520)
        o.append(p_heart(u, x, y, rnd.uniform(5, 9), ("#EE98A4", "#C25A6E", "#FAD0D4"), int(x * 7 + y), rot=rnd.uniform(-25, 25), ink_w=0))
    coat = ("#EED2A0", "#C8A06A", "#FBEAC8")
    inkc = "#7A5228"
    d = Dog(u, 236, 330, 0.88, coat, 724, ink_c=inkc, ears="drop", ear_len=0.8, ear_w=1.0, mouth="smile", kind="smooth", nose_y=54, muzzle_w=36, skull=80,
            cheek=90, eyes=("#7A3A14", "#2A1206"), look=(0.35, 0.05), tilt=5, chest_len=320, round_top=0.8, eye_r=15, chest_w=0.82,
            ear_coat=("#E2BE88", "#B88E58", "#F4DCAE"), muzzle=("#F6E2BC", "#D2B080", "#FFF4DE"))
    o.append(d.draw())
    stripe = "#4E5660"
    kc = ("#A8AEB8", "#6E7480", "#D2D6DE")

    def k_head(c):
        return c.stripes(stripe, 725, op=0.75)

    def k_body(c):
        P = c.P
        out = [f'<path d="{blob(*P(0, 170), 60 * c.s, 120 * c.s, 726, 0.08, 14)}" fill="#F4F2EE" opacity="0.9"/>']
        for sg in (-1, 1):
            for k, x in enumerate((90, 118)):
                out.append(taper([P(sg * x, 100 + k * 18), P(sg * (x + 12), 140 + k * 18), P(sg * (x + 6), 180 + k * 18)], 7, 2, stripe, 0.6))
        return "".join(out)
    k = Cat(u, 400, 392, 0.6, kc, 727, ink_c="#2A2E36", eyes=("#B8D86A", "#5E8A2A"), eye_r=28, eye_x=44, ear_k=0.85, muzzle="#F4F2EE", chin_c="#F4F2EE",
            look=(-0.3, 0.0), tilt=-12, body_len=420, pupil_k=0.66, mouth="smile")
    o.append(k.draw(k_head, k_body))
    # little paw on the puppy's chest
    o.append(mitt(u, 326, 520, 40, 26, ("#F4F2EE", "#C8CCD4", "#FFFFFF"), 728, "#2A2E36", rot=-20))
    o.append(p_heart(u, 318, 214, 20, ("#E86A7A", "#B03A4E", "#F8A8B4"), 729, rot=-8))
    o.append(title(u, 300, 96, "best friends", SERIF_IT, 64, "#B03A4E", ["#C84A60", "#8E2A3C", "#E86A7A"], 730, max_w=420, shadow="#FFF6EE", soff=(0.02, 0.03), angle=-30))
    o.append(ruled(u, 152, "FUR-EVER", JOS, 30, "#7A5228", 731, ls=10, line_w=40))
    o.append(finish(u, op=0.75))
    return "".join(o)


# ---------------------------------------------------------------- wipe your paws — muddy paws about to step onto the doormat
@design("wipe-your-paws")
def wipe_your_paws():
    u = Ids("wipe-your-paws")
    o = [bg(u, "#D8C8B0", ["#CDBA9E", "#E4D6C2"], 741, angle=0)]
    # tiled hallway floor in perspective-free checks
    for r, y in enumerate(range(-30, 640, 70)):
        for c_, x in enumerate(range(-30, 640, 70)):
            if (r + c_) % 2 == 0:
                o.append(f'<rect x="{x}" y="{y}" width="70" height="70" fill="#BCA88A" opacity="0.35"/>')
    o.append(vignette(u, "#5A4428", 0.3, 0.55))
    # the coir mat
    mx0, my0, mx1, my1 = 80, 236, 520, 500
    mat = [(mx0, my0), (mx1, my0), (mx1, my1), (mx0, my1)]
    o.append(shadow(u, 304, 508, 240, 16, 0.4))
    o.append(form(u, rpoly(mat, 14), bbox(mat, 2), "#C8955A", "#94643A", "#E2B47A", 742, -90, n=900, length=(4, 10), width=(0.8, 1.8), shade=(0, 10),
                  shade_op=0.25, ink_w=2.4, ink_col="#5A3A18", sop=(0.35, 0.75)))
    inner = [(mx0 + 18, my0 + 18), (mx1 - 18, my0 + 18), (mx1 - 18, my1 - 18), (mx0 + 18, my1 - 18)]
    o.append(f'<path d="{rpoly(inner, 8)}" fill="none" stroke="#6A4420" stroke-width="5" opacity="0.6" stroke-dasharray="2 3"/>')
    # stencilled words on the mat
    for (y, txt, font, size, ls) in ((318, "WIPE YOUR", JOS, 46, 10), (436, "PAWS", BEBAS, 116, 18)):
        sz = fit_size(txt, font, size, 380, ls)
        t = f'<text x="{300 + ls / 2}" y="{y}" text-anchor="middle" {font} font-size="{sz}" letter-spacing="{ls}">{txt}</text>'
        o.append(t.replace("<text ", '<text fill="#4A2A12" opacity="0.88" '))
        o.append(distress(u, t, (100, y - sz, 500, y + 10), "#C8955A", 743 + y, n=420, r=(0.6, 1.8)))
    o.append(ink(f"M 170 350 L 430 350", "#4A2A12", 3, 744, 1, 0.6))
    # muddy footprints crossing the mat and floor
    rnd = random.Random(745)
    trail = [(472, 600), (424, 560), (470, 500), (420, 452), (468, 392), (414, 340), (462, 286)]
    for i, (x, y) in enumerate(trail):
        o.append(p_paw(u, x, y, 9, ("#6A4A2E", "#3E2A18", "#8A6A4A"), 746 + i, rot=rnd.uniform(-20, 20), ink_w=0))
    for _ in range(26):
        x, y = rnd.uniform(380, 520), rnd.uniform(240, 600)
        o.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{rnd.uniform(1, 3):.1f}" fill="#5A3E26" opacity="0.7"/>')
    # two muddy front legs stepping in from the top, curly doodle fur
    coat = ("#F2DEB8", "#C8A878", "#FFF2DA")
    mud = ("#7A5434", "#4A3018", "#9A7450")
    inkc = "#6A4A28"
    for sg, x in ((-1, 252), (1, 352)):
        leg = tube([(x, -30), (x + sg * 2, 80), (x, 170)], 80, 70)
        lid = u("lg")
        gid = u("mg")
        mud_svg = (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{mud[0]}" stop-opacity="0"/>'
                   f'<stop offset="0.45" stop-color="{mud[0]}" stop-opacity="0.75"/><stop offset="1" stop-color="{mud[1]}" stop-opacity="1"/></linearGradient></defs>'
                   f'<rect x="{x - 50}" y="80" width="100" height="120" fill="url(#{gid})"/>' +
                   "".join(f'<path d="{blob(x + rnd.uniform(-34, 34), rnd.uniform(60, 130), rnd.uniform(4, 9), rnd.uniform(3, 7), 900 + x + k, 0.25, 9)}" fill="{mud[0]}" opacity="0.85"/>'
                           for k in range(9)) +
                   brush((x - 40, 100, x + 40, 200), [mud[1], mud[2], mud[0]], 754 + x, 40, 90, (6, 14), (1, 2.4), (0.3, 0.7)))
        for k in range(3):
            dxk = x - 22 + k * 20 + rnd.uniform(-4, 4)
            mud_svg += f'<path d="M {dxk:.1f} 126 q 3 {rnd.uniform(10, 22):.1f} 0 {rnd.uniform(16, 30):.1f} q -4 4 -6 0 Z" fill="{mud[0]}"/>'
        o.append(fur(u, leg, coat, 750 + x, lambda xx, yy: 90 + rnd.uniform(-30, 30), shade=(sg * 10, 0), shade_op=0.3, ink_w=2.4, ink_col=inkc, length=(6, 12),
                     curve=0.9, width=(1.4, 3), density=1.3, extra_in=mud_svg))
        o.append(feather([p for p in closed_curve(leg, 6) if 0 < p[1] < 120], [coat[0], coat[2], coat[1]], 752 + x, 2, (4, 9), (1.8, 3), down=0.2, cx=x, cy=60))
        o.append(mitt(u, x, 180, 80, 40, mud, 758 + x, "#2A1808", line_op=0.0, ink_w=2.4))
        for k, tx in enumerate((-27, -9, 9, 27)):
            ty = 196 + (4 if k in (1, 2) else 0)
            tdp = blob(x + tx, ty, 12, 11, 770 + x + k, 0.06, 12)
            o.append(form(u, tdp, (x + tx - 12, ty - 11, x + tx + 12, ty + 11), mud[0], mud[1], mud[2], 771 + x + k, -90, n=10, shade=(0, 3), shade_op=0.4,
                          hi=(x + tx - 3, ty - 4, 4, 3), hi_op=0.6, ink_w=2, ink_col="#2A1808"))
        for k in range(3):
            o.append(f'<path d="{blob(x + rnd.uniform(-24, 24), 216 + rnd.uniform(0, 12), rnd.uniform(3, 6), rnd.uniform(3, 6), 760 + k + x, 0.2, 8)}" fill="#5A3E26" opacity="0.8"/>')
    o.append(f'<path d="{blob(300, 222, 70, 12, 762, 0.15, 14)}" fill="#5A3E26" opacity="0.35"/>')
    o.append(plain(300, 536, "THANK YOU KINDLY", JOS, 19, "#5A3A18", 300, ls=4))
    o.append(finish(u, op=0.8))
    return "".join(o)


# ---------------------------------------------------------------- who rescued who — a woman and her dog on a hill at sunset, seen from behind
@design("who-rescued-who")
def who_rescued_who():
    u = Ids("who-rescued-who")
    o = [sky(u, [(0, "#E8B4C0"), (0.45, "#F6C8A4"), (0.75, "#FBDCA0"), (1, "#F6E6C0")], ["#F2C0B4", "#F8D4AE", "#EEB8BC"], 781, n=110)]
    o.append(glow(u, 360, 420, 200, "#FFF2C8", 0.9))
    o.append(form(u, blob(360, 410, 46, 46, 782, 0.01, 18), (314, 364, 406, 456), "#FBE6A8", "#F2C878", "#FFF8DC", 782, 0, n=20, shade=None, ink_w=0))
    for k, (cx, cy) in enumerate(((140, 250), (470, 290))):
        o.append("".join(f'<path d="{blob(cx + dx, cy + dy, r, r * 0.5, k * 10 + i, 0.1, 12)}" fill="#FBEAE0" opacity="0.7"/>'
                         for i, (dx, dy, r) in enumerate(((0, 0, 34), (30, -4, 26), (-28, 4, 22)))))
    o.append(motion([[(420, 200), (430, 194), (440, 200)], [(446, 214), (454, 209), (462, 214)]], "#7A4A5A", 783, 2, 0.8))
    from fall_gouache_b import hill
    o.append(hill(u, [(-20, 440), (140, 420), (330, 436), (620, 414)], 620, "#C89AA8", "#A87888", "#E2BCC4", 784))
    o.append(hill(u, [(-20, 468), (200, 452), (420, 466), (620, 450)], 620, "#A88AA0", "#866478", "#C8AABC", 785))
    # the near hilltop they sit on
    o.append(hill(u, [(-20, 520), (150, 496), (300, 488), (450, 494), (620, 512)], 620, "#7E8A5A", "#5A6A3E", "#A8B47E", 786, n=260))
    rnd = random.Random(787)
    for _ in range(70):
        x, y = rnd.uniform(-10, 610), rnd.uniform(500, 600)
        o.append(f'<path d="M {_f(x)} {_f(y)} q {rnd.uniform(-3, 3):.1f} -6 {rnd.uniform(-5, 5):.1f} -{rnd.uniform(8, 16):.1f}" stroke="{rnd.choice(["#5A6A3E", "#A8B47E", "#8A9A62"])}" stroke-width="2" fill="none" stroke-linecap="round"/>')
    for _ in range(14):
        x, y = rnd.choice([rnd.uniform(40, 170), rnd.uniform(440, 570)]), rnd.uniform(520, 580)
        o.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="3" fill="{rnd.choice(["#F2D06A", "#FFFFFF", "#E88A8A"])}"/>')
    inkc = "#3A2418"
    # --- the woman, from behind
    px = 236
    hair = ("#6A3E26", "#3E2214", "#9A6440")
    sweater = ("#5E8AA8", "#3E6480", "#8EB4CE")
    back = [(px, 372), (px + 44, 380), (px + 70, 410), (px + 82, 470), (px + 88, 512), (px - 88, 512), (px - 82, 470), (px - 70, 410), (px - 44, 380)]
    o.append(fur(u, back, sweater, 788, lambda x, y: 90 + (x - px) * 0.3, shade=(-14, 0), shade_op=0.3, length=(12, 26), width=(1.4, 3), ink_w=2.4, ink_col=inkc,
                 extra_in="".join(f'<path d="M {x} 380 L {x} 520" stroke="#2E4E66" stroke-width="2.4" opacity="0.3"/>' for x in range(px - 80, px + 90, 12))))
    o.append(form(u, blob(px, 370, 26, 14, 789, 0.06, 12), (px - 26, 356, px + 26, 384), "#F0C4A0", "#C8946E", "#F8DCC0", 789, 0, n=8, shade=None, ink_w=1.8, ink_col=inkc))
    head = blob_pts(px - 2, 330, 40, 46, 790, 0.03, 16)
    o.append(fur(u, head, hair, 791, lambda x, y: 90 + (x - px) * 1.2, shade=(-6, 0), shade_op=0.35, length=(14, 30), width=(1, 2.2), ink_w=2.4, ink_col=inkc,
                 hi=(px + 12, 312, 12, 16), hi_op=0.35))
    bun = blob_pts(px - 4, 280, 22, 18, 792, 0.05, 12)
    o.append(fur(u, bun, hair, 793, 30, shade=(-3, 3), ink_w=2.2, ink_col=inkc, length=(6, 14), n=40))
    o.append(ink(f"M {px - 20} 290 Q {px - 4} 298 {px + 16} 290", "#C8463A", 4, 794, 1, 1))
    for k in range(4):
        o.append(ink(f"M {px - 30 + k * 18} 296 Q {px - 34 + k * 20} 330 {px - 26 + k * 18} 368", hair[0 if k % 2 else 1], 2, 795 + k, 1, 0.5))
    # her arm round the dog
    arm = tube([(px + 60, 404), (px + 100, 420), (px + 150, 426), (px + 186, 430)], 30, 26)
    # --- the dog, sitting beside her, head leaning on her shoulder
    dx = 368
    coat = ("#D8A858", "#A47A34", "#F2CC88")
    dbody = [(dx, 384), (dx + 40, 392), (dx + 62, 428), (dx + 74, 476), (dx + 76, 514), (dx - 70, 514), (dx - 68, 470), (dx - 56, 426), (dx - 36, 392)]
    o.append(ink(smooth_open([(dx + 66, 510), (dx + 110, 516), (dx + 136, 504), (dx + 146, 486)]), coat[1], 16, 796, 1, 1))
    o.append(ink(smooth_open([(dx + 66, 510), (dx + 110, 516), (dx + 136, 504), (dx + 146, 486)]), coat[0], 11, 797, 1, 1))
    o.append(fur(u, dbody, coat, 798, lambda x, y: 90 + (x - dx) * 0.3, shade=(-12, 0), shade_op=0.3, length=(10, 22), width=(1.2, 2.8), ink_w=2.4, ink_col=inkc))
    o.append(feather([p for p in closed_curve(dbody, 6) if p[1] > 420], [coat[0], coat[2], coat[1]], 799, 2, (5, 11), (1.6, 2.8), down=0.6, cx=dx, cy=460))
    dhead = blob_pts(dx - 22, 352, 44, 40, 800, 0.03, 16, rot=-14)
    for sg, ex in ((-1, dx - 62), (1, dx + 16)):
        ear = [(ex - 12, 330), (ex + 12, 326), (ex + 16 * sg + 4, 370), (ex + 4, 392), (ex - 10 + sg * 6, 372)]
        o.append(fur(u, ear, ("#B88A44", "#7A5420", "#D8A858"), 801 + sg, 95, shade=(sg * 4, 0), ink_w=2.2, ink_col=inkc, length=(8, 16), n=50))
    snout = [(dx - 50, 346), (dx - 78, 352), (dx - 90, 362), (dx - 84, 374), (dx - 56, 378)]
    o.append(fur(u, snout, coat, 809, 180, shade=(0, 4), ink_w=2.2, ink_col=inkc, length=(5, 10), n=40))
    o.append(f'<path d="{blob(dx - 88, 360, 6, 5, 810, 0.1, 10)}" fill="#2A1A12"/>')
    o.append(fur(u, dhead, coat, 803, lambda x, y: 90 + (x - dx) * 0.6, shade=(-8, 4), shade_op=0.3, length=(8, 16), width=(1.2, 2.4), ink_w=2.4, ink_col=inkc,
                 hi=(dx - 4, 336, 14, 10), hi_op=0.3))
    o.append(fur(u, arm, sweater, 804, 0, shade=(0, 6), ink_w=2.4, ink_col=inkc, length=(10, 20)))
    o.append(form(u, blob(px + 192, 432, 15, 12, 805, 0.08, 12), (px + 177, 420, px + 207, 444), "#F0C4A0", "#C8946E", "#F8DCC0", 805, 0, n=8, shade=None,
                  ink_w=1.8, ink_col=inkc))
    o.append(p_heart(u, 300, 250, 16, ("#E86A7A", "#B03A4E", "#F8A8B4"), 806, rot=-6))
    o.append(title(u, 300, 96, "who rescued", SERIF_IT, 60, "#7A3A4E", ["#8E4A60", "#5A2438", "#A85A74"], 807, max_w=400, shadow="#FBEAE0", soff=(0.02, 0.03), angle=-30))
    o.append(title(u, 300, 186, "WHO?", BEBAS, 100, "#C8463A", ["#D85A4A", "#A8301E", "#E8785A"], 808, max_w=260, ls=14, shadow="#FBEAE0", soff=(0.025, 0.04), angle=-80))
    o.append(finish(u, op=0.7))
    return "".join(o)


# ---------------------------------------------------------------- dachshund — long story short: a red doxie in a striped sweater, turning to say hi
@design("dachshund")
def dachshund():
    u = Ids("dachshund")
    o = [bg(u, "#D2E6E2", ["#C2DCD6", "#E2F0EC", "#B6D2CC"], 801, angle=-15)]
    o.append(glow(u, 300, 330, 260, "#F4FBF8", 0.7))
    o.append(floor_boards(u, 462, 802, pal=("#E2BE8A", "#B8905E", "#F2D6AA"), rows=3, inkc="#8A6A42"))
    coat = ("#B8582A", "#7A3014", "#E8925A")
    far = ("#8E3E1A", "#5A2208", "#B8582A")
    inkc = "#4A1A08"
    tints = ["#E8925A", "#7A3014", "#C8683A", "#F2A870"]
    ox = -22
    X = lambda pts: [(x + ox, y) for x, y in pts]
    o.append(shadow(u, 290, 466, 230, 16, 0.4))
    o.append(shadow(u, 452, 530, 50, 8, 0.3))
    o.append(p_bone(u, 450, 520, 70, 13, 818, rot=-14, pal=("#7AB0D8", "#3E6E9E", "#B4D2F0"), inkc="#2E4E72"))
    o.append('<g transform="translate(-12 -18) scale(1.04)">')
    # tail, wagging
    o.append(motion([[(104 + ox, 246), (106 + ox, 224)], [(124 + ox, 258), (136 + ox, 240)]], "#5A8A84", 803, 2.6, 0.7))
    tl = tube(X([(128, 336), (106, 312), (92, 284), (90, 258)]), 20, 6)
    o.append(fur(u, tl, coat, 804, -100, shade=(4, 0), ink_w=2.2, ink_col=inkc, length=(6, 12), tints=tints, n=50))
    # far legs in shadow
    for x in (176, 426):
        o.append(limb(u, X([(x, 366), (x + 4, 406), (x, 438)]), 32, 28, far, 805 + x, inkc, flow=lambda a, b: 90, shade=None, ink_w=1.8))
        o.append(f'<path d="{blob(x + ox + 8, 442, 18, 8, 806 + x, 0.08, 10)}" fill="{far[0]}"/>' + ink(blob(x + ox + 8, 442, 18, 8, 806 + x, 0.08, 10), inkc, 1.6, x, 1, 0.6))
    # near legs
    for x in (148, 398):
        o.append(limb(u, X([(x, 360), (x + 4, 404), (x, 436)]), 38, 32, coat, 811 + x, inkc, flow=lambda a, b: 90, shade=(5, 0), ink_w=2.2))
        pw = blob(x + ox + 10, 442, 21, 9, 812 + x, 0.08, 10)
        o.append(f'<path d="{pw}" fill="{coat[0]}"/>' + ink(pw, inkc, 2, x, 1, 0.8) +
                 ink(f"M {x + ox + 20} 446 l 0 -6 M {x + ox + 26} 446 l -1 -5", inkc, 1.4, x, 1, 0.7))
    # body
    body = X([(120, 352), (128, 318), (166, 300), (256, 296), (346, 298), (410, 292), (446, 300), (466, 330), (458, 370), (430, 394), (360, 398), (262, 394),
              (182, 398), (134, 386)])
    o.append(fur(u, body, coat, 807, lambda x, y: 0 + (y - 340) * 0.05, shade=(0, 16), shade_op=0.4, length=(14, 30), width=(1.4, 3), ink_w=2.4, ink_col=inkc,
                 tints=tints, hi=(260 + ox, 306, 130, 8), hi_op=0.35))
    # striped sweater over the middle of the body
    cid = u("sw")
    sweater_box = (196 + ox, 280, 404 + ox, 410)
    stripes = []
    for k, x in enumerate(range(int(sweater_box[0]), int(sweater_box[2]) + 16, 16)):
        col = ["#3E7A8A", "#F4EEE2", "#D2584A", "#F4EEE2"][k % 4]
        stripes.append(f'<path d="M {x} 270 Q {x + 7} 340 {x} 420 L {x + 16} 420 Q {x + 23} 340 {x + 16} 270 Z" fill="{col}"/>')
    knit = "".join(f'<path d="M {x} {y} l 4 6 l 4 -6" stroke="#000000" stroke-width="1" fill="none" opacity="0.12"/>'
                   for x in range(int(sweater_box[0]), int(sweater_box[2]), 8) for y in range(282, 410, 8))
    gid = u("swg")
    o.append(f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.3"/>'
             f'<stop offset="0.35" stop-color="#FFFFFF" stop-opacity="0"/><stop offset="0.7" stop-color="#1E3A40" stop-opacity="0.15"/>'
             f'<stop offset="1" stop-color="#1E3A40" stop-opacity="0.45"/></linearGradient></defs>')
    o.append(f'<clipPath id="{cid}"><path d="{smooth_closed(body)}"/></clipPath><g clip-path="url(#{cid})">'
             + "".join(stripes) + knit +
             brush(sweater_box, ["#FFFFFF", "#2E5A66"], 808, 120, 90, (6, 14), (1, 2), (0.15, 0.35)) +
             f'<rect x="{sweater_box[0]}" y="270" width="{sweater_box[2] - sweater_box[0] + 16}" height="150" fill="url(#{gid})"/>'
             "</g>")
    for x in (sweater_box[0], sweater_box[2] + 16):
        cuff = [(x - 8, 290), (x + 8, 290), (x + 8, 402), (x - 8, 402)]
        o.append(f'<clipPath id="{cid}c{int(x)}"><path d="{smooth_closed(body)}"/></clipPath><g clip-path="url(#{cid}c{int(x)})">' +
                 form(u, rpoly(cuff, 3), bbox(cuff, 1), "#3E7A8A", "#22505E", "#7AB0BC", 809 + int(x), -90, n=16, shade=None, ink_w=1.8, ink_col="#1E3A40") +
                 "".join(f'<path d="M {x - 4 + k * 4} 292 L {x - 4 + k * 4} 400" stroke="#22505E" stroke-width="1.2" opacity="0.6"/>' for k in range(3)) + "</g>")
    o.append(ink(smooth_closed(body), inkc, 2.4, 810, 1, 0.8))
    # neck and the head turned to the viewer
    neck = tube(X([(430, 336), (452, 300), (470, 268)]), 66, 54)
    o.append(fur(u, neck, coat, 813, -60, shade=(8, 0), ink_w=2.2, ink_col=inkc, tints=tints, length=(8, 16)))
    o.append(collar(u, X([(428, 296), (452, 310), (478, 306)]), 13, ("#D2584A", "#8E2A1E", "#F2907A"), 814, tag=("heart", GOLD_TAG), tag_at=0.5))
    d = Dog(u, 474 + ox, 236, 0.56, coat, 815, ink_c=inkc, ears="drop", ear_len=1.25, ear_w=1.05, nose_y=66, muzzle_w=32, mouth="open", kind="smooth",
            chest=False, look=(-0.1, 0.05), eyes=("#6A3010", "#200C04"), tilt=12, round_top=0.8, skull=74, cheek=80, eye_r=16,
            ear_coat=("#9A4620", "#5E2408", "#C8683A"), muzzle=("#C8683A", "#8E3E1A", "#E8925A"))
    o.append(d.draw())
    o.append("</g>")
    o.append(title(u, 300, 118, "Dachshund", DMS, 100, "#7A2E14", ["#5A1E0A", "#9A4422", "#B8582A"], 816, max_w=440, shadow="#F6FBF8", soff=(0.025, 0.035), angle=-60))
    o.append(ruled(u, 166, "LONG STORY SHORT", JOS, 21, "#2E6A64", 817, ls=6, line_w=34))
    o.append(finish(u, op=0.75))
    return "".join(o)
#MORE>>


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
