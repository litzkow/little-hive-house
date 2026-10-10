"""Summer, hand-painted (gouache / storybook) edition — "bem coloridona".

Thirty Summer magnets painted as gouache on paper: saturated tropical colour (coral, turquoise, sunshine
yellow, hot pink, mint), organic shapes, layered washes with pooled edges, brush strokes that follow each
form, a warm pen line under the paint, brush-textured lettering, soft light and paper grain. Repaints the
eight original Summer slugs (same words) and adds 22 new pieces.

Run from tools/designs:  python3 summer_gouache.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (leaf, blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ribbon, ridge, ruled, shift, sky, soft_glow, specks, taper, qpts, catmull, steam_wisps)
from fall_painted import Doc
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from poster import ANTON

COL = "summer"
INK = "#3A2418"
SINK = "#2E2440"       # cool plum pen line for night / sea pieces

# (light, base, dark) gouache palettes
CORAL = ("#FFA08A", "#FF6F59", "#C23C2E")
TURQ = ("#8EE6E0", "#1FB5B0", "#0E6E74")
SUN = ("#FFEB8A", "#FFC93C", "#D98E12")
PINK = ("#FFB6D2", "#FF5FA2", "#B82A6A")
MINT = ("#C8F5DA", "#7EDDB0", "#2E9A72")
LEAF = ("#9ADB6A", "#3FA548", "#1E6234")
ORANGE = ("#FFC07A", "#FF8A2A", "#C0520E")
SAND = ("#FFF0CE", "#F6D9A0", "#C9A066")
SKYB = ("#D4F4FF", "#7FD3F0", "#2E8EC0")
NAVY = ("#4A6A9A", "#22406E", "#0E1E3E")
WHITE = ("#FFFFFF", "#F4F0E8", "#B8B0A6")
RED = ("#FF8A7A", "#E8423A", "#9A1A1A")
WOOD = ("#E8B47A", "#C0864A", "#7A4E26")
LIME = ("#E8FF9A", "#B8E04A", "#6E9A1E")
PURP = ("#C8A0F0", "#8A5AD0", "#4A2A8A")

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


# ================================================================ summer toolkit
def rot(pts, cx, cy, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def rect_pts(x0, y0, x1, y1, step=24, seed=0, j=0.8):
    """Rectangle as many slightly jittered points (hand-drawn edges)."""
    pts = []
    for (ax, ay), (bx, by) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        n = max(2, int(math.hypot(bx - ax, by - ay) / step))
        for i in range(n):
            t = i / n
            pts.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    return jitter(pts, seed, j)


def poly_pts(corners, step=20, seed=0, j=0.7):
    pts = []
    n_c = len(corners)
    for k in range(n_c):
        (ax, ay), (bx, by) = corners[k], corners[(k + 1) % n_c]
        n = max(2, int(math.hypot(bx - ax, by - ay) / step))
        for i in range(n):
            t = i / n
            pts.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    return jitter(pts, seed, j)


def frond(cx, cy, ang, L, seed, cols, droop=0.45, blade=0.3, w=None, spine=None, n=16, sw=1.6):
    """One palm frond: a drooping spine with feathery leaflets either side, swept toward the tip."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)

    def P(t):
        return (cx + L * t * ux, cy + L * t * uy + droop * L * t * t)

    out = []
    w = w or max(2.0, L * 0.035)
    for i in range(n):
        t = 0.1 + 0.9 * i / (n - 1)
        x, y = P(t)
        x2, y2 = P(min(1, t + 0.02))
        tx, ty = x2 - x, y2 - y
        tl = math.hypot(tx, ty) or 1
        tx, ty = tx / tl, ty / tl
        nx, ny = -ty, tx
        ln = L * blade * (math.sin(math.pi * min(1, t * 1.05)) ** 0.7 + 0.15) * rnd.uniform(0.85, 1.1)
        for sg in (-1, 1):
            dx = tx * 0.55 + sg * nx * 0.85
            dy = ty * 0.55 + sg * ny * 0.85 + 0.35
            ex, ey = x + dx * ln, y + dy * ln
            mx, my = x + dx * ln * 0.5 + tx * ln * 0.12, y + dy * ln * 0.5 + ty * ln * 0.12
            out.append(taper([(x, y), (mx, my), (ex, ey)], w, 0.6, rnd.choice(cols), rnd.uniform(0.85, 1)))
    sp = [P(t / 8) for t in range(9)]
    out.append(taper(sp, sw * 2.2, 0.8, spine or cols[-1], 0.95))
    return "".join(out)


def palm(D, base, top, seed, fronds=None, trunk=WOOD, leaf_cols=None, L=110, rings=True, inkc=INK, nuts=True, width=18, sil=None, rim=None):
    """Palm tree: a curved, ringed trunk from `base` to `top` and a crown of drooping fronds."""
    bx, by = base
    tx, ty = top
    mx, my = (bx + tx) / 2 + (ty - by) * 0.12, (by + ty) / 2
    path = qpts((bx, by), (mx, my), (tx, ty), 14)
    out = []
    if sil:
        out.append(taper(path, width, width * 0.55, sil))
        if rim:
            out.append(taper([(x - width * 0.22, y) for x, y in path], width * 0.18, width * 0.1, rim, 0.6))
    else:
        left, right = [], []
        n = len(path)
        for i, (x, y) in enumerate(path):
            a = path[max(i - 1, 0)]
            b = path[min(i + 1, n - 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            l = math.hypot(dx, dy) or 1
            nx, ny = -dy / l, dx / l
            ww = (width + (width * 0.55 - width) * i / (n - 1)) / 2
            left.append((x + nx * ww, y + ny * ww))
            right.append((x - nx * ww, y - ny * ww))
        pts = left + right[::-1]
        out.append(painted(D, pts, trunk, seed, sdir=(1, 0), sk=0.2, angle=-90, n=30, slen=(6, 18), sw=(1, 2.2), inkw=1.8, hi=0.35, hik=0.2))
        if rings:
            for i in range(1, n - 1):
                x, y = path[i]
                ww = (width + (width * 0.55 - width) * i / (n - 1)) / 2
                out.append(pline([(x - ww, y - 1), (x, y + 2.5), (x + ww, y - 1)], trunk[2], 1.6, seed + i, 0.7, 1))
    fr = fronds or [(-170, 1.0), (-140, 0.9), (-110, 0.8), (-75, 0.85), (-40, 0.95), (-10, 1.0), (-195, 0.85), (15, 0.8)]
    cols = leaf_cols or [LEAF[0], LEAF[1], LEAF[1], LEAF[2]]
    rnd = random.Random(seed)
    for k, (ang, s) in enumerate(fr):
        out.append(frond(tx, ty, ang + rnd.uniform(-6, 6), L * s, seed * 7 + k, cols, droop=0.5 if abs(ang + 90) > 40 else 0.25))
    if nuts and not sil:
        for k, (dx, dy) in enumerate(((-7, 8), (6, 9), (0, 14))):
            out.append(painted(D, blob_pts(tx + dx, ty + dy, 7, 7, seed + 40 + k, 0.05, 10), ("#B08050", "#6E4A28", "#3A2414"), seed + 40 + k,
                               sk=0.25, angle=-60, n=4, inkw=1.2, hi=0.4))
    return "".join(out)


def puff_cloud(D, cx, cy, w, seed, pal=("#FFFFFF", "#FFF6F0", "#E6C8D8"), inkw=0, op=1.0, inkc=INK, rows=2):
    """Gouache cumulus: overlapping painted puffs (big in the middle), flat base, shaded underside, dry-brush
    highlights; optional pen line drawn only around the outer silhouette."""
    rnd = random.Random(seed)
    puffs = []
    n = 7
    for i in range(n):
        t = i / (n - 1)
        x = cx - w * 0.42 + w * 0.84 * t + rnd.uniform(-w, w) * 0.02
        r = w * (0.09 + 0.12 * math.sin(math.pi * t) ** 1.2) * rnd.uniform(0.85, 1.15)
        y = cy - r * 0.6
        puffs.append((x, y, r))
    if rows > 1:
        for i in range(3):
            t = 0.28 + 0.22 * i + rnd.uniform(-0.05, 0.05)
            x = cx - w * 0.42 + w * 0.84 * t
            r = w * rnd.uniform(0.13, 0.19)
            puffs.append((x, cy - w * 0.16 - r * 0.6, r))
    shapes = [blob(x, y, r, r * 0.88, seed + i, 0.06, 14) for i, (x, y, r) in enumerate(puffs)]
    base = smooth_closed([(cx - w * 0.5, cy), (cx - w * 0.3, cy + w * 0.03), (cx + w * 0.3, cy + w * 0.03), (cx + w * 0.5, cy), (cx + w * 0.3, cy - w * 0.08), (cx - w * 0.3, cy - w * 0.08)])
    allp = " ".join(shapes) + " " + base
    out = [f'<g opacity="{op}">']
    if inkw:
        out.append(f'<path d="{allp}" fill="{inkc}" stroke="{inkc}" stroke-width="{inkw * 2:.1f}" stroke-linejoin="round" opacity="0.35"/>')
    out.append(f'<path d="{allp}" fill="{pal[1]}"/>')
    cid = D.clip(f'<path d="{allp}"/>')
    inner = [f'<path d="{blob(cx, cy + w * 0.02, w * 0.62, w * 0.11, seed + 31, 0.1, 16)}" fill="{pal[2]}" opacity="0.6"/>']
    for i, (x, y, r) in enumerate(puffs):
        inner.append(f'<path d="{blob(x + r * 0.15, y + r * 0.35, r * 0.85, r * 0.45, seed + 70 + i, 0.1, 10)}" fill="{pal[2]}" opacity="0.28"/>')
    for i, (x, y, r) in enumerate(puffs):
        inner.append(f'<path d="{blob(x - r * 0.22, y - r * 0.3, r * 0.6, r * 0.45, seed + 50 + i, 0.12, 10)}" fill="{pal[0]}" opacity="0.85"/>')
        inner.append(taper([(x - r * 0.75, y - r * 0.05), (x - r * 0.5, y - r * 0.6), (x, y - r * 0.85)], 1, max(2, r * 0.12), pal[0], 0.9))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(strokes(D.nid(), allp, (cx - w * 0.6, cy - w * 0.5, cx + w * 0.6, cy + w * 0.1), [pal[0], pal[2], pal[1]], seed, n=int(w * 0.25), angle=-20,
                       length=(w * 0.05, w * 0.15), width=(1, 3), opacity=(0.15, 0.4), curve=0.5))
    out.append("</g>")
    return "".join(out)


def sparkle(cx, cy, r, color, op=1.0):
    k = r * 0.22
    return (f'<path d="M {cx:.1f} {cy - r:.1f} Q {cx + k:.1f} {cy - k:.1f} {cx + r:.1f} {cy:.1f} Q {cx + k:.1f} {cy + k:.1f} {cx:.1f} {cy + r:.1f} '
            f'Q {cx - k:.1f} {cy + k:.1f} {cx - r:.1f} {cy:.1f} Q {cx - k:.1f} {cy - k:.1f} {cx:.1f} {cy - r:.1f} Z" fill="{color}" opacity="{op}"/>')


def wave_lines(seed, box, cols, n=40, L=(20, 50), w=2.0, amp=3, op=(0.4, 0.85)):
    """Little painted wave ticks on water: short bowed strokes."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        l = rnd.uniform(*L) * (0.5 + 0.5 * (y - y0) / max(1, y1 - y0))
        out.append(taper([(x - l / 2, y), (x, y - amp * rnd.uniform(0.5, 1.2)), (x + l / 2, y)], 0.6, w * rnd.uniform(0.7, 1.3), rnd.choice(cols), rnd.uniform(*op)))
    return "".join(out)


def scallop(D, cx, cy, s, pal, seed, rot_=0):
    """Scallop shell (fan with ribs and a hinge)."""
    pts = []
    for i in range(25):
        t = i / 24
        a = math.radians(-160 + 140 * t)
        r = s * (1 + 0.05 * abs(math.sin(t * math.pi * 8)))
        pts.append((cx + r * math.cos(a), cy + 0.25 * s + r * math.sin(a)))
    pts += [(cx + 0.18 * s, cy + 0.3 * s), (cx + 0.3 * s, cy + 0.42 * s), (cx - 0.3 * s, cy + 0.42 * s), (cx - 0.18 * s, cy + 0.3 * s)]
    pts = rot(pts, cx, cy, rot_)
    out = [painted(D, pts, pal, seed, sdir=(0.5, 0.8), sk=0.15, angle=-90 + rot_, n=10, inkw=max(1, s * 0.05), hi=0.4)]
    for k in range(-3, 4):
        a = math.radians(-90 + k * 17)
        p = rot([(cx, cy + 0.28 * s), (cx + 0.9 * s * math.cos(a), cy + 0.25 * s + 0.9 * s * math.sin(a))], cx, cy, rot_)
        out.append(pline(p, pal[2], max(0.9, s * 0.045), seed + k, 0.6, 1))
    return "".join(out)


def starfish(D, cx, cy, s, pal, seed, rot_=0):
    pts = []
    for i in range(10):
        a = math.radians(-90 + rot_ + i * 36)
        r = s if i % 2 == 0 else s * 0.42
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pts = jitter(pts, seed, s * 0.03)
    # rounded arms: add midpoints
    out = [painted(D, pts, pal, seed, sdir=(0.5, 0.7), sk=0.15, angle=-60, n=12, inkw=max(1, s * 0.05), hi=0.35)]
    rnd = random.Random(seed)
    for i in range(5):
        a = math.radians(-90 + rot_ + i * 72)
        for k in range(1, 4):
            r = s * 0.2 * k
            out.append(f'<circle cx="{cx + r * math.cos(a):.1f}" cy="{cy + r * math.sin(a):.1f}" r="{max(0.9, s * 0.05):.1f}" fill="{pal[0]}" opacity="0.9"/>')
    return "".join(out)


def sunglasses(D, cx, cy, s, frame, lens=("#5AD0E0", "#1F6E9A", "#0E2E4E"), seed=1, rot_=0, round_=False):
    out = [f'<g transform="rotate({rot_} {cx} {cy})">']
    for sg in (-1, 1):
        lx = cx + sg * s * 0.52
        if round_:
            pts = blob_pts(lx, cy, s * 0.42, s * 0.4, seed + sg, 0.02, 16)
        else:
            pts = [(lx - s * 0.44, cy - s * 0.3), (lx + s * 0.44, cy - s * 0.32), (lx + s * 0.4, cy + 0.1 * s), (lx + s * 0.2, cy + s * 0.34),
                   (lx - s * 0.2, cy + s * 0.34), (lx - s * 0.42, cy + 0.1 * s)]
        out.append(painted(D, pts, frame, seed + sg, sdir=(0.4, 0.8), sk=0.1, angle=-30, n=6, inkw=1.6, hi=0.3))
        inner = [(lx + (x - lx) * 0.8, cy + (y - cy) * 0.8) for x, y in pts]
        g = D.lin([(0, lens[0]), (0.5, lens[1]), (1, lens[2])])
        out.append(f'<path d="{smooth_closed(inner)}" fill="{g}"/>')
        out.append(taper([(lx - s * 0.25, cy - s * 0.12), (lx - s * 0.05, cy - s * 0.2)], max(2, s * 0.07), 1, "#FFFFFF", 0.7))
        out.append(taper([(lx - s * 0.28, cy + s * 0.02), (lx - s * 0.22, cy - s * 0.01)], max(1.5, s * 0.05), 1, "#FFFFFF", 0.5))
    out.append(pline([(cx - s * 0.12, cy - s * 0.12), (cx, cy - s * 0.2), (cx + s * 0.12, cy - s * 0.12)], frame[2], max(2.5, s * 0.08), seed, 1, 1))
    out.append("</g>")
    return "".join(out)


def sun_disc(D, cx, cy, r, pal=SUN, seed=1, glow_col="#FFF2A0", glow_r=2.2, inkw=0, strokes_n=40):
    out = [soft_glow(D, cx, cy, r * glow_r, glow_col, 0.7)]
    pts = blob_pts(cx, cy, r, r, seed, 0.015, 24)
    out.append(painted(D, pts, pal, seed, sdir=(0.6, 0.6), sk=0.08, angle=-30, n=strokes_n, slen=(r * 0.2, r * 0.6), sw=(r * 0.02, r * 0.06),
                       inkw=inkw, hi=0.45, hik=0.06, curve=0.5, edge=False))
    return "".join(out)


def daisy(D, cx, cy, r, seed, petal=("#FFFFFF", "#FFF8EE", "#D8C8B8"), center=SUN, n=12, rot_=0, inkw=1.2):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        a = math.radians(rot_ + i * 360 / n + rnd.uniform(-5, 5))
        px, py = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55
        pts = blob_pts(px, py, r * 0.5, r * 0.17, seed + i, 0.05, 12, math.degrees(a))
        out.append(painted(D, pts, petal, seed + i, sdir=(0.5, 0.6), sk=0.15, angle=math.degrees(a), n=3, inkw=inkw, inkop=0.5, hi=0.3, edge=False))
    out.append(painted(D, blob_pts(cx, cy, r * 0.28, r * 0.28, seed + 99, 0.05, 12), center, seed + 99, sk=0.25, angle=-45, n=6, inkw=inkw, hi=0.5))
    out.append(specks(seed, (cx - r * 0.18, cy - r * 0.18, cx + r * 0.18, cy + r * 0.18), [center[2]], 8, (0.6, 1.2)))
    return "".join(out)


def hibiscus(D, cx, cy, r, pal, seed, rot_=0, inkw=1.4, stamen="#FFE07A"):
    rnd = random.Random(seed)
    out = []
    for i in range(5):
        a = math.radians(rot_ + i * 72 + rnd.uniform(-6, 6))
        px, py = cx + math.cos(a) * r * 0.5, cy + math.sin(a) * r * 0.5
        pts = blob_pts(px, py, r * 0.55, r * 0.42, seed + i, 0.12, 14, math.degrees(a))
        out.append(painted(D, pts, pal, seed + i, sdir=(math.cos(a), math.sin(a)), sk=0.18, angle=math.degrees(a), n=10, inkw=inkw, inkop=0.6, hi=0.35))
        out.append(pline([(cx + math.cos(a) * r * 0.15, cy + math.sin(a) * r * 0.15), (cx + math.cos(a) * r * 0.6, cy + math.sin(a) * r * 0.6)], pal[2], max(1, r * 0.03), seed + i, 0.5, 1))
    out.append(f'<path d="{blob(cx, cy, r * 0.2, r * 0.2, seed, 0.1, 10)}" fill="{pal[2]}" opacity="0.8"/>')
    a = math.radians(rot_ - 50)
    ex, ey = cx + math.cos(a) * r * 0.85, cy + math.sin(a) * r * 0.85
    out.append(pline([(cx, cy), ((cx + ex) / 2 + 3, (cy + ey) / 2), (ex, ey)], "#FFF2C0", max(2, r * 0.06), seed, 1, 1))
    for k in range(6):
        b = a + rnd.uniform(-0.6, 0.6)
        out.append(f'<circle cx="{ex + math.cos(b) * r * 0.08:.1f}" cy="{ey + math.sin(b) * r * 0.08:.1f}" r="{max(1.4, r * 0.035):.1f}" fill="{stamen}"/>')
    return "".join(out)


def monstera(D, cx, cy, s, rot_, seed, pal=LEAF, holes=True):
    """A broad split tropical leaf: heart shape with slits and a midrib."""
    pts = []
    for i in range(40):
        t = i / 40 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * s / 17, cy - y * s / 17))
    pts = rot(pts, cx, cy, rot_ + 180)
    out = [painted(D, pts, pal, seed, sdir=(0.5, 0.6), sk=0.14, angle=rot_ - 90, n=int(s * 0.8), inkw=max(1.2, s * 0.02), hi=0.3)]
    rnd = random.Random(seed)
    if holes:
        for k, yy in enumerate((-0.45, -0.1, 0.25)):
            for sg in (-1, 1):
                p = rot([(cx + sg * s * 0.95, cy + yy * s - 0.05 * s), (cx + sg * s * 0.55, cy + yy * s + 0.05 * s), (cx + sg * s * 0.25, cy + yy * s + 0.12 * s)], cx, cy, rot_)
                out.append(pline(p, pal[0] if False else "#FFFFFF", max(2, s * 0.06), seed + k, 0.0, 1))
    mid = rot([(cx, cy + 0.85 * s), (cx, cy), (cx, cy - 0.75 * s)], cx, cy, rot_)
    out.append(pline(mid, pal[0], max(1.4, s * 0.035), seed, 0.7, 1))
    for yy in (-0.4, -0.05, 0.3):
        for sg in (-1, 1):
            p = rot([(cx, cy + yy * s + 0.15 * s), (cx + sg * s * 0.45, cy + yy * s), (cx + sg * s * 0.85, cy + yy * s - 0.08 * s)], cx, cy, rot_)
            out.append(pline(p, pal[0], max(1, s * 0.022), seed + 3, 0.5, 1))
    return "".join(out)


def stripes_in(D, d, box, angle, widths, colors, seed, op=1.0):
    """Hand-painted stripes inside a shape (clip), slightly wobbly edges."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0)
    rnd = random.Random(seed)
    cid = D.clip(f'<path d="{d}"/>')
    out = [f'<g {cid}><g transform="rotate({angle} {cx:.1f} {cy:.1f})">']
    x = cx - R
    k = 0
    while x < cx + R:
        w = widths[k % len(widths)]
        c = colors[k % len(colors)]
        if c:
            pts = [(x + rnd.uniform(-1.5, 1.5), cy - R + i * R / 6) for i in range(13)] + [(x + w + rnd.uniform(-1.5, 1.5), cy + R - i * R / 6) for i in range(13)]
            out.append(f'<path d="{smooth_closed(pts)}" fill="{c}" opacity="{op}"/>')
        x += w
        k += 1
    out.append("</g></g>")
    return "".join(out)


def seagull(x, y, s, col="#3A3048", op=0.9, flap=0):
    return (pline([(x - s, y + flap), (x - s * 0.5, y - s * 0.5), (x, y)], col, max(1.6, s * 0.2), int(x), op, 1) +
            pline([(x, y), (x + s * 0.5, y - s * 0.55), (x + s, y - flap)], col, max(1.6, s * 0.2), int(y), op, 1))


def sea(D, y0, y1, stops, seed, cols, n=80, ticks=None):
    g = D.lin(stops, 0, y0, 0, y1, "userSpaceOnUse")
    out = [f'<rect x="0" y="{y0}" width="600" height="{y1 - y0}" fill="{g}"/>']
    d = f"M -10 {y0} L 610 {y0} L 610 {y1 + 10} L -10 {y1 + 10} Z"
    out.append(strokes(D.nid(), d, (-60, y0, 610, y1), cols, seed, n=n, angle=0, length=(40, 140), width=(2, 6), opacity=(0.12, 0.35), curve=0.08))
    if ticks:
        out.append(wave_lines(seed + 1, (0, y0 + 6, 600, y1), ticks, int(n * 0.6)))
    return "".join(out)


def sand_ground(D, line, bottom, seed, pal=SAND, dots=True):
    out = [hill(D, line, bottom, pal, seed, angle=-3, inkw=0, sop=(0.15, 0.4))]
    if dots:
        ys = [p[1] for p in line]
        out.append(specks(seed, (0, min(ys) + 6, 600, bottom), [pal[2], "#FFFFFF", "#B08A5A"], 120, (0.6, 1.6), (0.25, 0.6)))
    return "".join(out)


def beach_ball(D, cx, cy, r, seed, cols=(PINK, SUN, TURQ, WHITE, CORAL, MINT), pole=(-0.35, -0.45)):
    """Beach ball: coloured gores meeting at a pole, shading on the far side, a glossy highlight."""
    px, py = cx + pole[0] * r, cy + pole[1] * r
    out = [cast(D, cx + r * 0.2, cy + r * 0.92, r * 1.0, r * 0.22, strength=0.35, seed=seed)]
    d = blob(cx, cy, r, r, seed, 0.01, 24)
    out.append(f'<path d="{d}" fill="#FFFFFF"/>')
    cid = D.clip(f'<path d="{d}"/>')
    g = []
    for k in range(6):
        a0 = math.radians(k * 60 + 10)
        a1 = math.radians(k * 60 + 70)
        pal = cols[k % len(cols)]
        pts = [(px, py)]
        for j in range(9):
            a = a0 + (a1 - a0) * j / 8
            pts.append((px + 2.4 * r * math.cos(a), py + 2.4 * r * math.sin(a)))
        g.append(f'<path d="M {px:.1f} {py:.1f} ' + " ".join(f"L {x:.1f} {y:.1f}" for x, y in pts[1:]) + f' Z" fill="{pal[1]}"/>')
    g.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r * 0.16:.1f}" fill="#FFFFFF"/>')
    shade = D.rad([(0, "#000000", 0), (0.6, "#000000", 0.05), (1, "#1A0A20", 0.42)], 0.38, 0.32, 0.75)
    g.append(f'<rect x="{cx - r:.1f}" y="{cy - r:.1f}" width="{2 * r:.1f}" height="{2 * r:.1f}" fill="{shade}"/>')
    out.append(f'<g {cid}>{"".join(g)}</g>')
    out.append(strokes(D.nid(), d, (cx - r, cy - r, cx + r, cy + r), ["#FFFFFF", "#000000"], seed, n=int(r * 0.8), angle=-40, length=(r * 0.2, r * 0.5), width=(1, r * 0.05), opacity=(0.08, 0.2), curve=0.5))
    out.append(taper([(cx - r * 0.62, cy - r * 0.05), (cx - r * 0.55, cy - r * 0.4), (cx - r * 0.3, cy - r * 0.62)], max(2, r * 0.07), 1, "#FFFFFF", 0.75))
    out.append(ink(d, INK, max(1.6, r * 0.04), seed, 2, 0.75))
    return "".join(out)


def bite_out(pts, bx, by, br, n=10):
    """Take a round bite out of a closed outline: the run of points inside the circle is replaced by the
    circle's arc that runs through the shape's interior."""
    m = len(pts)
    inside = [math.hypot(x - bx, y - by) < br for x, y in pts]
    if not any(inside) or all(inside):
        return pts
    k = next(i for i in range(m) if not inside[i] and inside[(i + 1) % m])
    seq = [pts[(k + j) % m] for j in range(m)]
    ins = [inside[(k + j) % m] for j in range(m)]
    j1 = next(j for j in range(1, m) if not ins[j])
    a0 = math.atan2(seq[0][1] - by, seq[0][0] - bx)
    a1 = math.atan2(seq[j1][1] - by, seq[j1][0] - bx)
    gx = sum(x for x, _ in pts) / m
    gy = sum(y for _, y in pts) / m
    best = None
    for da in ((a1 - a0) % (2 * math.pi), (a1 - a0) % (2 * math.pi) - 2 * math.pi):
        mid = a0 + da / 2
        dist = math.hypot(bx + br * math.cos(mid) - gx, by + br * math.sin(mid) - gy)
        if best is None or dist < best[0]:
            best = (dist, da)
    da = best[1]
    arc = [(bx + br * math.cos(a0 + da * t / n), by + br * math.sin(a0 + da * t / n)) for t in range(1, n)]
    return [seq[0]] + arc + seq[j1:]


def banana_leaf(D, bx, by, ang, L, W, seed, pal=LEAF, bg=None, splits=3):
    """Long tropical leaf from a base point: elliptic blade, pale midrib, parallel side veins, a few wind tears."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    rnd = random.Random(seed)
    right, left, spine = [], [], []
    for i in range(21):
        t = i / 20
        bend = 0.12 * L * t * t
        px, py = bx + ux * L * t + nx * bend, by + uy * L * t + ny * bend
        w = W * math.sin(math.pi * min(1, t * 1.05)) ** 0.7 * (1 - 0.25 * t)
        spine.append((px, py))
        right.append((px + nx * w, py + ny * w))
        left.append((px - nx * w, py - ny * w))
    pts = right + left[::-1]
    out = [painted(D, pts, pal, seed, sdir=(nx, ny), sk=0.12, angle=ang + 70, n=int(L * W / 120) + 10, slen=(W * 0.3, W * 0.9), sw=(1.5, 3.5), inkw=1.8, hi=0.3, hik=0.06)]
    for i in range(2, 19, 1):
        for side, edge in ((1, right), (-1, left)):
            sx, sy = spine[i]
            ex, ey = edge[min(20, i + 2)]
            out.append(pline([(sx, sy), ((sx + ex) / 2 + ux * 3, (sy + ey) / 2 + uy * 3), (ex, ey)], pal[2] if side > 0 else pal[0], 1.2, seed + i, 0.35, 1))
    if bg:
        for k in range(splits):
            i = rnd.randint(4, 17)
            side = rnd.choice((right, left))
            sx, sy = spine[i]
            ex, ey = side[min(20, i + 2)]
            out.append(taper([(ex + (ex - sx) * 0.1, ey + (ey - sy) * 0.1), ((sx + ex) / 2, (sy + ey) / 2), (sx + (ex - sx) * 0.15, sy + (ey - sy) * 0.15)], 7, 0.8, bg))
    out.append(taper(spine, 5, 1.2, pal[0], 0.85))
    out.append(taper([(bx - ux * 30, by - uy * 30), (bx, by)], 7, 5, pal[2]))
    return "".join(out)


def finish_s(D, out, seed, color=INK, op=1.0):
    return finish(D, out, seed, color, op)


# ================================================================ 1. endless summer — sunset palms over a glowing sea
@design("endless-summer")
def endless_summer():
    D = Doc("es")
    out = [sky(D, [(0, "#5A2A86"), (0.28, "#C2378E"), (0.48, "#FF5F7A"), (0.62, "#FF8A4A"), (0.7, "#FFC24A")], 3, 400,
               ["#FF8AB0", "#B83A8E", "#FFB060", "#7A3AA0"], 70, angle=-2)]
    out.append(soft_glow(D, 300, 352, 300, "#FFD27A", 0.75))
    # striped retro sun sinking into the sea
    clip_bars = "".join(f'<rect x="150" y="{y:.1f}" width="300" height="{h:.1f}"/>' for y, h in
                        ((180, 120), (304, 12), (321, 9), (335, 6)))
    cid = D.clip(clip_bars)
    out.append(f'<g {cid}>' + sun_disc(D, 300, 352, 128, ("#FFF4A0", "#FFD23A", "#FF7A2A"), 5, glow_r=0.01, strokes_n=60) + '</g>')
    # clouds catching the light
    out.append(puff_cloud(D, 150, 250, 170, 7, ("#FFC8A0", "#F2789A", "#A83A86"), op=0.95))
    out.append(puff_cloud(D, 470, 212, 190, 8, ("#FFD0A8", "#F2809E", "#A83A86"), op=0.95))
    # sea
    out.append(sea(D, 344, 600, [(0, "#FF9A6A"), (0.08, "#E8608A"), (0.35, "#3A9AC0"), (1, "#163A6E")], 11,
                   ["#FFB08A", "#2E7AAE", "#5AC0D8", "#1E4E86"], 110))
    # sun's path: broken strokes of gold and pink on the water
    rnd = random.Random(12)
    for i in range(46):
        t = i / 45
        y = 352 + t * 200
        hw = 120 * (1 - t * 0.55) * rnd.uniform(0.35, 1)
        x = 300 + rnd.uniform(-1, 1) * 40 * (1 - t)
        c = rnd.choice(["#FFE27A", "#FFC24A", "#FFF4B8", "#FF9A7A"])
        out.append(taper([(x - hw, y), (x, y - 1.5), (x + hw, y)], 1, 3 + 4 * t, c, 0.75 - 0.35 * t))
    out.append(wave_lines(14, (0, 380, 600, 600), ["#8EE6F0", "#FFFFFF", "#5AC8E0"], 50, (24, 60), 2.6, 3, (0.35, 0.7)))
    # far sailboat
    out.append(f'<path d="M 470 346 L 470 312 L 488 344 Z" fill="#4A1E5A"/><path d="M 462 347 L 492 347 L 488 352 L 466 352 Z" fill="#4A1E5A"/>')
    # birds
    out.append(seagull(400, 262, 11, "#5A1E5A") + seagull(424, 246, 8, "#5A1E5A") + seagull(380, 244, 6, "#5A1E5A"))
    # palms in silhouette with rim light, framing
    pl = [(-150, 0.9), (-120, 0.85), (-90, 0.7), (-55, 0.85), (-20, 1.0), (5, 0.95), (-185, 0.8), (25, 0.75)]
    out.append(palm(D, (14, 640), (84, 300), 21, pl, L=124, sil="#2A0E36", rim="#FF8A7A", leaf_cols=["#2A0E36", "#3A1446", "#2A0E36"], width=24))
    pr = [(-160, 1.0), (-185, 0.95), (-130, 0.8), (-95, 0.75), (-60, 0.85), (-25, 0.9), (-210, 0.75)]
    out.append(palm(D, (604, 640), (530, 336), 22, pr, L=106, sil="#2A0E36", rim="#FF8A7A", leaf_cols=["#2A0E36", "#3A1446", "#2A0E36"], width=20))
    # lettering
    out.append(letters(D, 300, 154, "endless", SERIF_IT, 120, "#FFF6E8", ["#FFFFFF", "#FFE2D0", "#FFD0E0"], 31, max_w=400,
                       shadow="#7A1E5A", soff=(0.025, 0.04), angle=-35))
    out.append(letters(D, 300, 520, "SUMMER", BEBAS, 150, "#FFD23A", ["#FFE88A", "#FFB020", "#FFF2B0", "#FF9A2A"], 32, ls=14, max_w=400,
                       shadow="#7A1E5A", angle=-78, hi="#FFFFFF", inkc="#8A3A10", inkw=1.6))
    return finish(D, out, 41, "#3A1446", 0.8)


# ================================================================ 2. beach, please — flat-lay on the sand: towel, sunhat, shades
def straw_hat(D, cx, cy, R, seed, band=PINK, rot_=0):
    straw = ("#FCE6A8", "#EBC772", "#B88A3A")
    out = [cast(D, cx + R * 0.12, cy + R * 0.14, R * 1.02, R * 0.95, strength=0.3, seed=seed)]
    brim = blob_pts(cx, cy, R, R * 0.96, seed, 0.03, 26)
    out.append(painted(D, brim, straw, seed, sdir=(0.6, 0.7), sk=0.08, angle=0, n=10, inkw=2, hi=0.3))
    # woven rings on the brim
    cid = D.clip(f'<path d="{smooth_closed(brim)}"/>')
    rings = []
    rnd = random.Random(seed)
    for k in range(6, 20):
        r = R * k / 20
        for j in range(int(r / 3)):
            a = 2 * math.pi * j / int(r / 3) + k * 0.3
            x, y = cx + r * math.cos(a), cy + r * 0.96 * math.sin(a)
            rings.append(f'<path d="M {x - 3 * math.sin(a):.1f} {y + 3 * math.cos(a):.1f} l {6 * math.sin(a):.1f} {-6 * math.cos(a):.1f}" stroke="{rnd.choice([straw[2], straw[0], "#D8AE5A"])}" stroke-width="2" stroke-linecap="round" opacity="0.6"/>')
    out.append(f'<g {cid}>{"".join(rings)}</g>')
    crown = blob_pts(cx - R * 0.04, cy - R * 0.04, R * 0.5, R * 0.48, seed + 1, 0.03, 18)
    out.append(cast(D, cx + R * 0.06, cy + R * 0.06, R * 0.56, R * 0.54, strength=0.35, seed=seed + 2))
    out.append(painted(D, crown, straw, seed + 1, sdir=(0.6, 0.7), sk=0.22, angle=-40, n=8, inkw=2, hi=0.55, hik=0.12))
    cid2 = D.clip(f'<path d="{smooth_closed(crown)}"/>')
    sp = "".join(f'<path d="{smooth_open([(cx - R * 0.04 + r * math.cos(a) * R * 0.48, cy - R * 0.04 + r * math.sin(a) * R * 0.46) for a in [b * 0.3 for b in range(22)]])}" fill="none" stroke="{straw[2]}" stroke-width="1.6" opacity="0.5"/>'
                 for r in (0.25, 0.5, 0.75))
    out.append(f'<g {cid2}>{sp}</g>')
    # ribbon band + bow
    band_o = blob(cx - R * 0.04, cy - R * 0.04, R * 0.56, R * 0.54, seed + 3, 0.02, 18)
    band_i = blob(cx - R * 0.04, cy - R * 0.04, R * 0.47, R * 0.45, seed + 3, 0.02, 18)
    out.append(f'<path d="{band_o} {band_i}" fill-rule="evenodd" fill="{band[1]}"/>')
    out.append(ink(band_o, band[2], 1.6, seed, 1, 0.7))
    bx, by = cx + R * 0.36, cy + R * 0.32
    for sg in (-1, 1):
        lp = rot([(bx, by), (bx + sg * R * 0.22, by - R * 0.12), (bx + sg * R * 0.26, by + R * 0.06)], bx, by, 30)
        out.append(painted(D, lp, band, seed + 5 + sg, sk=0.2, angle=0, n=4, inkw=1.6, hi=0.4))
        tl = rot([(bx, by), (bx + sg * R * 0.1, by + R * 0.4), (bx + sg * R * 0.02, by + R * 0.42)], bx, by, 30)
        out.append(painted(D, tl, band, seed + 8 + sg, sk=0.2, angle=80, n=3, inkw=1.4, hi=0.3))
    out.append(painted(D, blob_pts(bx, by, R * 0.06, R * 0.06, seed + 9, 0.05, 8), band, seed + 9, sk=0.2, n=2, inkw=1.4, hi=0.4))
    return "".join(out)


@design("beach-please")
def beach_please():
    D = Doc("bp")
    out = [f'<rect width="600" height="600" fill="#F8DFA8"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, 0, 600, 600), ["#FFF0C8", "#E8C27E", "#F2D090", "#FFF8E0"], 3,
                       n=200, angle=-8, length=(40, 120), width=(3, 9), opacity=(0.15, 0.4), curve=0.15))
    out.append(specks(4, (0, 0, 600, 600), ["#C49A5A", "#FFFFFF", "#A87A44", "#E8A890"], 420, (0.6, 1.8), (0.3, 0.7)))
    # the sea lapping in at the top corner
    sea_pts = [(-20, -20), (620, -20), (620, 40), (540, 58), (470, 48), (400, 66), (320, 54), (240, 70), (160, 58), (80, 74), (-20, 62)]
    sd = smooth_closed(sea_pts)
    out.append(f'<path d="{smooth_closed(shift(sea_pts, 0, 14))}" fill="#E2C48A" opacity="0.7"/>')
    out.append(f'<path d="{sd}" fill="{D.lin([(0, "#1E9AB0"), (0.6, "#3FD0D0"), (1, "#8EF0E0")])}"/>')
    out.append(strokes(D.nid(), sd, (-40, -20, 620, 80), ["#8EF0E0", "#1E8AA0", "#FFFFFF"], 5, n=50, angle=-2, length=(40, 100), width=(2, 5), opacity=(0.2, 0.5)))
    foam = [(x, y + 2) for x, y in sea_pts[2:]]
    out.append(taper(foam[::-1], 3, 8, "#FFFFFF", 0.9))
    rnd = random.Random(6)
    for i in range(40):
        x = rnd.uniform(-10, 610)
        out.append(f'<circle cx="{x:.1f}" cy="{58 + 10 * math.sin(x / 50) + rnd.uniform(-4, 12):.1f}" r="{rnd.uniform(1.2, 3):.1f}" fill="#FFFFFF" opacity="0.85"/>')
    # striped towel, laid at an angle
    tw = rot(rect_pts(40, 300, 420, 620, 26, 7, 1.2), 230, 460, -14)
    td = smooth_closed(tw)
    out.append(cast(D, 236, 470, 230, 190, strength=0.18, seed=8))
    out.append(f'<path d="{td}" fill="#FFFFFF"/>')
    out.append(stripes_in(D, td, (0, 260, 480, 640), -14, [34, 14, 34, 14, 34, 14], [PINK[1], None, TURQ[1], None, SUN[1], None], 9))
    out.append(strokes(D.nid(), td, (0, 260, 480, 640), ["#FFFFFF", "#000000", "#FFE0F0"], 10, n=120, angle=-14, length=(30, 80), width=(1, 3), opacity=(0.08, 0.22)))
    # fringe along the top short edge of the towel
    top_edge = rot([(40 + i * 12, 300) for i in range(32)], 230, 460, -14)
    for i, (x, y) in enumerate(top_edge):
        out.append(pline([(x, y), (x - 3 + 2 * math.sin(i), y - 12)], "#F6F0E6", 2.2, i, 1, 1))
    out.append(ink(td, "#8A5A3A", 1.6, 11, 1, 0.4))
    # sunglasses resting on the towel, a cool drink, shells
    out.append(sunglasses(D, 190, 470, 70, ("#FF8AB8", "#F23A8A", "#9A1A5A"), seed=12, rot_=-18))
    # sunscreen tube lying on the towel
    tube = rot([(60, 360), (150, 352), (158, 356), (160, 384), (152, 390), (60, 384), (54, 372)], 106, 372, -24)
    out.append(cast(D, 112, 384, 60, 18, strength=0.3, seed=13))
    out.append(painted(D, tube, ("#FFE9A0", "#FFC93C", "#D08A12"), 14, sdir=(0.2, 1), sk=0.15, angle=-24, n=14, inkw=1.8, hi=0.5))
    cap = rot([(34, 362), (56, 360), (58, 386), (34, 384), (30, 373)], 106, 372, -24)
    out.append(painted(D, cap, TURQ, 15, sdir=(0.2, 1), sk=0.15, angle=-24, n=4, inkw=1.8, hi=0.4))
    out.append(f'<g transform="rotate(-24 106 372)"><text x="110" y="380" text-anchor="middle" {MONO} font-size="17" fill="#C23C2E">SPF 50</text></g>')
    out.append(starfish(D, 530, 556, 24, CORAL, 19, 12))
    out.append(scallop(D, 478, 568, 20, ("#FFE8E0", "#F6B8A8", "#C0705A"), 20, -20))
    # the straw hat, half on the sand
    out.append(straw_hat(D, 448, 410, 112, 21))
    # lettering on the sand
    out.append(letters(D, 300, 196, "beach,", SERIF_IT, 140, "#E8337E", ["#FF6FAA", "#C21E66", "#FF8AB8"], 22, max_w=400,
                       shadow="#FFF4DC", soff=(-0.02, -0.025), angle=-35))
    out.append(letters(D, 300, 286, "PLEASE", BEBAS, 110, "#0E7E8A", ["#1FB5B0", "#0E5E6E", "#3FD0C8"], 23, ls=16, max_w=380,
                       shadow="#0A3E4E", angle=-78, hi="#B8FFF4"))
    return finish(D, out, 42, "#8A5A3A", 0.7)


# ================================================================ 3. vitamin sea — an orange-slice sun over a curling wave
def citrus_slice(D, cx, cy, r, seed, pal=ORANGE, pith="#FFF4D8", rind=("#FFB050", "#F07A1A", "#B04A0A")):
    out = [painted(D, blob_pts(cx, cy, r, r, seed, 0.01, 26), rind, seed, sk=0.1, n=10, inkw=2, hi=0.3)]
    out.append(f'<path d="{blob(cx, cy, r * 0.9, r * 0.9, seed + 1, 0.01, 24)}" fill="{pith}"/>')
    for k in range(10):
        a0 = 2 * math.pi * k / 10 + 0.06
        a1 = 2 * math.pi * (k + 1) / 10 - 0.06
        pts = [(cx + r * 0.08 * math.cos((a0 + a1) / 2), cy + r * 0.08 * math.sin((a0 + a1) / 2))]
        for j in range(7):
            a = a0 + (a1 - a0) * j / 6
            pts.append((cx + r * 0.8 * math.cos(a), cy + r * 0.8 * math.sin(a)))
        out.append(painted(D, pts, pal, seed + 10 + k, sdir=(0.5, 0.6), sk=0.1, angle=math.degrees((a0 + a1) / 2), n=6,
                           slen=(r * 0.15, r * 0.4), sw=(1, 2.5), inkw=0, hi=0.4, edge=False))
    return "".join(out)


@design("vitamin-sea")
def vitamin_sea():
    D = Doc("vs")
    out = [sky(D, [(0, "#FFF2B0"), (0.4, "#FFE6A0"), (0.75, "#B8F0E8")], 3, 600, ["#FFF8D8", "#FFE08A", "#C8F4EC"], 60)]
    out.append(soft_glow(D, 452, 152, 200, "#FFD27A", 0.6))
    # citrus sun with painted rays
    rnd = random.Random(4)
    for k in range(16):
        a = math.radians(k * 22.5 + 6)
        r0, r1 = 92, 92 + rnd.uniform(22, 36)
        out.append(taper([(452 + r0 * math.cos(a), 152 + r0 * math.sin(a)), (452 + r1 * math.cos(a), 152 + r1 * math.sin(a))], 9, 2, rnd.choice(["#FFB43A", "#FF8A2A"]), 0.9))
    out.append(citrus_slice(D, 452, 152, 80, 5))
    out.append(seagull(330, 236, 12, "#2E5A6A") + seagull(358, 220, 8, "#2E5A6A"))
    # far sea line
    out.append(sea(D, 330, 600, [(0, "#3FC8C8"), (1, "#0E6E8A")], 6, ["#8EF0E0", "#0E7E8E"], 30))
    # the big curling wave, breaking to the left
    body = [(640, 620), (-40, 620), (-40, 470), (60, 466), (150, 455), (230, 432), (292, 398), (330, 350), (346, 300), (338, 262), (316, 246),
            (290, 252), (270, 272), (262, 296), (244, 290), (236, 262), (248, 226), (282, 196), (332, 182), (392, 190), (450, 222), (510, 270),
            (570, 318), (640, 352)]
    bd = smooth_closed(body)
    # the hollow of the tube (seen through the curl)
    tube = smooth_closed([(258, 300), (266, 272), (290, 252), (318, 250), (338, 270), (342, 306), (326, 340), (292, 352), (266, 330)])
    out.append(f'<path d="{tube}" fill="{D.rad([(0, "#0A6A86"), (0.7, "#1E9AB0"), (1, "#3FC0C8")], 0.62, 0.5, 0.6)}"/>')
    out.append(strokes(D.nid(), tube, (240, 240, 350, 380), ["#1E8AA0", "#04283A", "#3FB0C0"], 81, n=30, angle=-60, length=(10, 30), width=(1.5, 4), opacity=(0.2, 0.5), curve=0.6))
    g = D.lin([(0, "#7AEAE0"), (0.35, "#1FB5B8"), (0.75, "#0E6E8E"), (1, "#0A4466")], 0, 180, 0, 600, "userSpaceOnUse")
    out.append(f'<path d="{bd}" fill="{g}"/>')
    cid = D.clip(f'<path d="{bd}"/>')
    # barrel shadow under the lip and swirling face strokes
    barrel = blob(300, 330, 46, 70, 7, 0.08, 14, 20)
    sw = []
    for i in range(18):
        r = 40 + i * 14
        pts = [(300 + r * math.cos(a) * 1.1, 300 + r * math.sin(a) * 0.9) for a in [math.radians(d) for d in range(150, 330, 15)]]
        sw.append(taper(pts, 2, 6, rnd.choice(["#8EF0E0", "#0E6E8E", "#3FD0D0", "#B8FFF4"]), rnd.uniform(0.25, 0.5)))
    out.append(f'<g {cid}><path d="{barrel}" fill="#0A4A66" opacity="0.55"/>{"".join(sw)}</g>')
    out.append(strokes(D.nid(), bd, (-40, 180, 640, 620), ["#8EF0E0", "#0A5A7A", "#3FD0D0", "#FFFFFF"], 8, n=160, angle=-25, length=(20, 70), width=(2, 6), opacity=(0.12, 0.35), curve=0.4))
    out.append(ink(smooth_open(body[3:]), "#0A3A56", 2.2, 9, 2, 0.6))
    # foam along the lip and crest
    crest = body[13:24]
    out.append(taper([(262, 300), (240, 284), (234, 254), (252, 220), (290, 194), (334, 182), (392, 188), (450, 218), (510, 266)], 6, 22, "#FFFFFF", 0.95))
    out.append(taper([(258, 296), (248, 284), (252, 270), (266, 266)], 6, 3, "#FFFFFF", 0.9))
    for i in range(70):
        t = rnd.random()
        k = min(len(crest) - 2, int(t * (len(crest) - 1)))
        x = crest[k][0] + (crest[k + 1][0] - crest[k][0]) * rnd.random()
        y = crest[k][1] + (crest[k + 1][1] - crest[k][1]) * rnd.random()
        out.append(f'<path d="{blob(x + rnd.uniform(-6, 6), y + rnd.uniform(-10, 4), rnd.uniform(3, 9), rnd.uniform(3, 7), i, 0.2, 8)}" fill="#FFFFFF" opacity="{rnd.uniform(0.6, 1):.2f}"/>')
    for i in range(36):
        a = rnd.uniform(math.pi * 0.9, math.pi * 1.6)
        r = rnd.uniform(10, 60)
        out.append(f'<circle cx="{250 + r * math.cos(a):.1f}" cy="{240 + r * math.sin(a):.1f}" r="{rnd.uniform(1.5, 4):.1f}" fill="#FFFFFF" opacity="0.85"/>')
    # foam lace on the water in front
    for y in (500, 540, 584):
        pts = [(x, y + 8 * math.sin(x / 40 + y)) for x in range(-20, 640, 30)]
        out.append(taper(pts, 2, 4, "#C8FFF4", 0.6))
    # lettering, top left
    out.append(letters(D, 206, 150, "vitamin", SERIF_IT, 104, "#FF6A3A", ["#FF8A5A", "#E8461E", "#FFA070"], 21, max_w=288,
                       shadow="#FFFFFF", soff=(-0.02, -0.025), angle=-35))
    out.append(letters(D, 300, 560 - 26, "SEA", BEBAS, 200, "#FFFFFF", ["#FFFFFF", "#D8FFF8", "#B8F4F0"], 22, ls=18, max_w=380,
                       shadow="#0A3A56", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 43, "#0A3A56", 0.7)


# ================================================================ 4. good vibes only — a 70s painted rainbow with daisies
@design("good-vibes-only")
def good_vibes_only():
    D = Doc("gv")
    out = [paper(D.nid(), "#FFF1DC", "#C08A5A", 11)]
    out.append(blooms(3, ["#FFB0C8", "#FFE08A", "#A8F0D8"], 7, (40, 120, 560, 540), (90, 160), (0.08, 0.14)))
    cx, cy = 300, 430
    bands = [PINK, CORAL, ORANGE, SUN, MINT, TURQ]
    R0, bw = 236, 26
    for k, pal in enumerate(bands):
        ro, ri = R0 - k * bw, R0 - (k + 1) * bw + 2
        outer = [(cx + ro * math.cos(math.radians(a)), cy + ro * math.sin(math.radians(a))) for a in range(180, 361, 6)]
        inner = [(cx + ri * math.cos(math.radians(a)), cy + ri * math.sin(math.radians(a))) for a in range(360, 179, -6)]
        pts = jitter(outer + inner, k, 0.8)
        out.append(painted(D, pts, pal, 10 + k, sdir=(0, 1), sk=0.04, angle=0, n=60, slen=(14, 40), sw=(1.5, 3.5), inkw=1.6, inkop=0.5, hi=0.25, hik=0.02, curve=0.6))
    # a smiling sun rising inside the arch
    out.append(sun_disc(D, 300, 430, 70, SUN, 15, glow_col="#FFE07A", glow_r=1.6))
    out.append(pline([(276, 420), (282, 413), (288, 420)], "#8A4A10", 3.2, 1, 1, 1) + pline([(312, 420), (318, 413), (324, 420)], "#8A4A10", 3.2, 2, 1, 1))
    out.append(pline([(284, 440), (300, 452), (316, 440)], "#8A4A10", 3.2, 3, 1, 1))
    out.append(f'<ellipse cx="268" cy="440" rx="9" ry="5" fill="#FF7A6A" opacity="0.5"/><ellipse cx="332" cy="440" rx="9" ry="5" fill="#FF7A6A" opacity="0.5"/>')
    # clouds at the feet of the rainbow
    out.append(puff_cloud(D, 112, 452, 180, 16, ("#FFFFFF", "#FFFFFF", "#F0C8D8"), inkw=1.4, inkc="#8A5A7A"))
    out.append(puff_cloud(D, 488, 452, 180, 17, ("#FFFFFF", "#FFFFFF", "#F0C8D8"), inkw=1.4, inkc="#8A5A7A"))
    # ground band to anchor the sun
    gd = smooth_closed([(-20, 452), (150, 444), (300, 450), (450, 442), (620, 452), (620, 620), (-20, 620)])
    out.append(f'<path d="{gd}" fill="#FFF1DC"/>')
    # daisies & sparkles
    for i, (x, y, r) in enumerate(((84, 516, 26), (124, 548, 18), (516, 520, 24), (474, 552, 16), (70, 160, 18), (532, 178, 20))):
        out.append(daisy(D, x, y, r, 30 + i))
    for x, y, r, c in ((96, 236, 12, PINK[1]), (506, 240, 10, TURQ[1]), (520, 300, 9, SUN[2]), (80, 300, 10, CORAL[1]), (300, 30 + 70, 0, "#000")):
        if r:
            out.append(sparkle(x, y, r, c))
    # lettering
    out.append(letters(D, 300, 150, "good vibes", SERIF_IT, 110, "#3A2A6A", ["#5A3A9A", "#2A1A4A", "#7A5AB0"], 41, max_w=420,
                       shadow="#FFC8D8", soff=(0.02, 0.035), angle=-35))
    out.append(letters(D, 300, 540, "ONLY", BEBAS, 110, "#FF5FA2", ["#FF8AC0", "#D83A80", "#FFB0D0"], 42, ls=22, max_w=280,
                       shadow="#3A2A6A", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 44)


# ================================================================ 5. life's a beach — a hammock between palms, aqua bay
def hammock(D, x0, y0, x1, y1, sag, seed, colors):
    """Striped fabric hammock slung between two points, with ropes."""
    out = []
    n = 16
    top, bot = [], []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t + sag * math.sin(math.pi * t) ** 1.3
        dep = 46 * math.sin(math.pi * t) ** 0.8 + 4
        top.append((x, y - dep * 0.25))
        bot.append((x, y + dep * 0.75))
    pts = top + bot[::-1]
    d = smooth_closed(pts)
    out.append(cast(D, (x0 + x1) / 2, y0 + sag + 110, (x1 - x0) * 0.42, 14, strength=0.3, seed=seed))
    out.append(f'<path d="{d}" fill="{colors[0]}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    st = []
    for i in range(n):
        if i % 2:
            continue
        quad = [top[i], top[i + 1], bot[i + 1], bot[i]]
        st.append(f'<path d="M {quad[0][0]:.1f} {quad[0][1]:.1f} L {quad[1][0]:.1f} {quad[1][1]:.1f} L {quad[2][0]:.1f} {quad[2][1]:.1f} L {quad[3][0]:.1f} {quad[3][1]:.1f} Z" fill="{colors[1 + (i // 2) % (len(colors) - 1)]}"/>')
    shade = D.lin([(0, "#000000", 0), (0.5, "#000000", 0.05), (1, "#000000", 0.3)])
    st.append(f'<path d="{d}" fill="{shade}"/>')
    out.append(f'<g {cid}>{"".join(st)}</g>')
    out.append(strokes(D.nid(), d, (x0, y0 - 20, x1, y0 + sag + 60), ["#FFFFFF", "#000000"], seed, n=60, angle=0, length=(10, 30), width=(1, 2.5), opacity=(0.08, 0.2)))
    out.append(ink(d, INK, 2, seed, 2, 0.7))
    out.append(taper(top, 2, 2, "#FFFFFF", 0.5))
    # ropes fanning to each tree
    for (ax, ay), side in (((x0, y0), 1), ((x1, y1), -1)):
        for k in range(4):
            px, py = top[1 if side > 0 else -2] if k < 2 else bot[1 if side > 0 else -2]
            out.append(pline([(ax, ay), (px + side * k * 2, py)], "#E8D8B8", 1.6, k, 0.9, 1))
        out.append(pline([(ax - 6 * side, ay - 2), (ax + 2 * side, ay + 4)], "#8A6A3A", 6, 3, 1, 1))
    return "".join(out)


@design("lifes-a-beach")
def lifes_a_beach():
    D = Doc("lb")
    out = [sky(D, [(0, "#4AC8F0"), (0.5, "#9AE8F8"), (0.66, "#E0FAFF")], 3, 400, ["#FFFFFF", "#6AD0F0", "#C8F4FF"], 50)]
    out.append(puff_cloud(D, 470, 288, 130, 4, ("#FFFFFF", "#FFFFFF", "#B8DFF0")))
    out.append(puff_cloud(D, 110, 300, 100, 5, ("#FFFFFF", "#FFFFFF", "#B8DFF0")))
    out.append(sea(D, 318, 420, [(0, "#1FA6C8"), (0.5, "#2ED0C8"), (1, "#8EF0DC")], 6, ["#8EF0E0", "#0E7EA0", "#FFFFFF"], 50,
                   ticks=["#FFFFFF", "#C8FFF8"]))
    out.append(f'<path d="M 120 318 L 120 300 L 132 316 Z" fill="#FFFFFF" stroke="#2E5A6A" stroke-width="1.2"/><path d="M 112 318 L 138 318 L 134 322 L 116 322 Z" fill="#E8423A"/>')
    # sand with a foam edge
    line = ridge([(-20, 410), (150, 400), (320, 408), (470, 398), (620, 404)], 7, 6)
    out.append(taper([(x, y - 4) for x, y in line], 6, 6, "#FFFFFF", 0.9))
    out.append(sand_ground(D, line, 620, 8, ("#FFF6DE", "#FBE6B8", "#D8B47A")))
    out.append(taper([(x, y + 6) for x, y in line[::3]], 3, 3, "#8EE0D8", 0.4))
    # palms, hammock between them
    out.append(palm(D, (80, 600), (118, 268), 11, [(-170, 1.0), (-140, 0.9), (-105, 0.75), (-70, 0.85), (-30, 1.0), (0, 1.0), (-200, 0.8), (25, 0.85)], L=120, width=22))
    out.append(palm(D, (520, 600), (480, 286), 12, [(-150, 1.0), (-180, 0.95), (-115, 0.75), (-75, 0.8), (-40, 0.95), (-5, 1.0), (-205, 0.8)], L=112, width=20))
    out.append(hammock(D, 104, 410, 496, 418, 70, 13, ["#FFFFFF", PINK[1], TURQ[1], SUN[1], CORAL[1]]))
    # a beach ball, a starfish and a shell in the sand
    out.append(beach_ball(D, 404, 528, 34, 16))
    out.append(starfish(D, 190, 540, 20, ("#FFC08A", "#FF8A4A", "#C04A1A"), 14, 8))
    out.append(scallop(D, 248, 556, 15, ("#FFF0F4", "#FFC0D0", "#C0708A"), 15, 10))
    rnd = random.Random(17)
    for i in range(5):
        x, y = 560 - i * 34, 590 - i * 10 + (8 if i % 2 else -8)
        out.append(f'<path d="{blob(x, y, 7, 4, 20 + i, 0.15, 8, -15)}" fill="#D8B47A" opacity="0.6"/>')
    # lettering
    out.append(letters(D, 300, 134, "life's a", SERIF_IT, 96, "#0E5E7E", ["#1E7EA0", "#0A3A5A", "#2E9AC0"], 21, max_w=340,
                       shadow="#FFFFFF", soff=(-0.02, -0.025), angle=-35))
    out.append(letters(D, 300, 252, "BEACH", BEBAS, 150, "#FF5F6A", ["#FF8A7A", "#E83A4A", "#FFB0A0"], 22, ls=16, max_w=360,
                       shadow="#0E3E5E", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 45)


# ================================================================ 6. sunshine state of mind — an orange branch over a sunburst
def citrus(D, cx, cy, r, seed, pal=ORANGE, light=(-0.6, -0.7)):
    pts = blob_pts(cx, cy, r, r * 0.96, seed, 0.03, 20)
    out = [painted(D, pts, pal, seed, sdir=(-light[0], -light[1]), sk=0.2, angle=-50, n=int(r * 0.9), slen=(r * 0.2, r * 0.6), sw=(r * 0.03, r * 0.08),
                   cols=[pal[0], pal[2], "#FFD27A", pal[0]], inkw=max(1.4, r * 0.05), hi=0.4, curve=0.5)]
    rnd = random.Random(seed)
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    pores = "".join(f'<circle cx="{cx + rnd.uniform(-r, r):.1f}" cy="{cy + rnd.uniform(-r, r):.1f}" r="{rnd.uniform(0.6, 1.3):.1f}" fill="{rnd.choice([pal[2], pal[0]])}" opacity="0.5"/>' for _ in range(int(r * 2)))
    out.append(f'<g {cid}>{pores}</g>')
    out.append(taper([(cx - r * 0.55, cy - r * 0.1), (cx - r * 0.5, cy - r * 0.45), (cx - r * 0.2, cy - r * 0.62)], max(2, r * 0.1), 1, "#FFF6E0", 0.7))
    out.append(f'<path d="{blob(cx + r * 0.05, cy - r * 0.86, r * 0.12, r * 0.07, seed, 0.1, 8)}" fill="#5A6A1E"/>')
    return "".join(out)


DLEAF = ("#7ACB5A", "#2E8A3E", "#14502A")


@design("sunshine-state-of-mind")
def sunshine_state_of_mind():
    D = Doc("ss")
    out = [f'<rect width="600" height="600" fill="#FFD84A"/>']
    # painted sunburst wedges
    cx, cy = 300, 360
    rnd = random.Random(3)
    for k in range(24):
        a0 = math.radians(k * 15 - 3.5)
        a1 = math.radians(k * 15 + 3.5)
        pts = [(cx, cy), (cx + 700 * math.cos(a0), cy + 700 * math.sin(a0)), (cx + 700 * math.cos(a1), cy + 700 * math.sin(a1))]
        out.append(f'<path d="M {cx} {cy} L {pts[1][0]:.1f} {pts[1][1]:.1f} L {pts[2][0]:.1f} {pts[2][1]:.1f} Z" fill="{"#FFC23A" if k % 2 else "#FFE27A"}" opacity="0.8"/>')
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, 0, 600, 600), ["#FFF2A0", "#FFB020", "#FFE070"], 4, n=160,
                       angle=-30, length=(40, 120), width=(3, 9), opacity=(0.12, 0.3), curve=0.2))
    out.append(soft_glow(D, cx, cy, 260, "#FFF6C8", 0.9))
    # a painted sun disc behind the type
    out.append(sun_disc(D, cx, cy, 150, ("#FFF0A0", "#FFD23A", "#FF9A2A"), 5, glow_r=0.01, strokes_n=60))
    out.append(ink(blob(cx, cy, 150, 150, 5, 0.015, 24), "#E07A1A", 2, 6, 1, 0.5))
    # orange branch across the top
    br = [(-20, 70), (80, 92), (180, 84), (290, 100), (400, 86), (500, 96), (620, 76)]
    out.append(taper(br, 12, 6, "#6A4A2A"))
    out.append(taper([(x, y - 2) for x, y in br], 4, 2, "#A07A50", 0.6))
    out.append(pline(br, INK, 2, 3, 0.6))
    leaves = [(40, 80, 30, -110), (120, 96, 34, 150), (160, 76, 30, -60), (238, 100, 34, 170), (262, 86, 30, -130), (336, 98, 32, 200),
              (372, 82, 30, -70), (446, 94, 34, 160), (480, 82, 30, -120), (560, 84, 34, 190), (20, 92, 30, 150), (590, 72, 28, -40)]
    for i, (x, y, s_, r_) in enumerate(leaves):
        out.append(leaf(D, "slim", x + 0.9 * s_ * math.sin(math.radians(r_)), y - 0.9 * s_ * math.cos(math.radians(r_)), s_, DLEAF, r_, 20 + i, vein="#C8F0A0"))
    for i, (x, y, r) in enumerate(((150, 150, 40), (300, 160, 46), (452, 148, 40))):
        out.append(pline([(x, y - r - 30), (x + 2, y - r - 6)], "#5A4A2A", 3.2, i, 1, 1))
        out.append(citrus(D, x, y, r, 30 + i))
    for i, (x, y) in enumerate(((84, 120), (224, 122), (378, 124), (520, 120))):
        out.append(daisy(D, x, y, 15, 40 + i, n=5, center=("#FFF2A0", "#FFD23A", "#C88A12")))
    out.append(leaf(D, "slim", 340, 210, 22, DLEAF, 40, 60, vein="#C8F0A0"))
    # lettering
    out.append(letters(D, 300, 382, "SUNSHINE", BEBAS, 140, "#FF5A2A", ["#FF7A3A", "#E8361A", "#FF9A5A", "#FF5A2A"], 51, ls=10, max_w=440,
                       shadow="#9A2A0A", angle=-78, hi="#FFE0B0", inkc="#7A1A06", inkw=1.6))
    out.append(letters(D, 300, 452, "state of mind", SERIF_IT, 76, "#0E7E7A", ["#1FA6A0", "#0A5A56", "#2EC0B8"], 52, max_w=380,
                       shadow="#FFF4C8", soff=(-0.02, -0.025), angle=-35))
    out.append(ribbon(D, 300, 512, 340, 40, TURQ, 53, tail=30))
    out.append(label(300, 519, "FLORIDA · GEORGIA · EVERYWHERE", MONO, 18, "#FFFFFF", ls=2, max_w=320))
    return finish(D, out, 46)


# ================================================================ 7. chill out — a melting triple-scoop cone
def scoop(D, cx, cy, r, pal, seed, drips=3, chips=None):
    rnd = random.Random(seed)
    pts = []
    for i in range(28):
        a = math.pi + math.pi * i / 27
        k = 1 + 0.04 * math.sin(a * 5 + seed)
        pts.append((cx + r * math.cos(a) * k, cy + r * 0.92 * math.sin(a) * k))
    # wavy melting rim with drips
    rim = []
    for i in range(29):
        t = i / 28
        x = cx + r * 1.08 - 2.16 * r * t
        y = cy + 0.14 * r + 0.06 * r * math.sin(t * 22 + seed)
        rim.append((x, y))
    for d in range(drips):
        j = 3 + int((d + 0.5) / drips * 22) + rnd.randint(-1, 1)
        L = r * rnd.uniform(0.25, 0.55)
        x, y = rim[j]
        rim[j] = (x, y + L)
        rim[j - 1] = (rim[j - 1][0], rim[j - 1][1] + L * 0.45)
        rim[j + 1] = (rim[j + 1][0], rim[j + 1][1] + L * 0.45)
    full = pts + rim
    out = [painted(D, full, pal, seed, sdir=(0.6, 0.7), sk=0.14, angle=-30, n=int(r * 1.2), slen=(r * 0.2, r * 0.5), sw=(r * 0.03, r * 0.07),
                   inkw=max(1.6, r * 0.03), hi=0.45, hik=0.08, curve=0.5)]
    out.append(taper([(cx - r * 0.7, cy - r * 0.1), (cx - r * 0.55, cy - r * 0.55), (cx - r * 0.15, cy - r * 0.78)], max(3, r * 0.1), 1, "#FFFFFF", 0.6))
    if chips:
        for i in range(int(r * 0.25)):
            a = rnd.uniform(math.pi * 1.05, math.pi * 1.95)
            rr = rnd.uniform(0.2, 0.85) * r
            x, y = cx + rr * math.cos(a), cy + rr * 0.85 * math.sin(a) + r * 0.05
            out.append(f'<path d="{blob(x, y, r * 0.05, r * 0.035, seed + i, 0.25, 6, rnd.uniform(0, 180))}" fill="{chips}"/>')
    return "".join(out)


def sprinkles(seed, box, cols, n=30, L=8, w=3.2):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        a = rnd.uniform(0, math.pi)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {L * math.cos(a):.1f} {L * math.sin(a):.1f}" stroke="{rnd.choice(cols)}" stroke-width="{w}" stroke-linecap="round"/>')
    return "".join(out)


def waffle_cone(D, cx, top, w, h, seed):
    pal = ("#F6CE84", "#E0A050", "#9A6024")
    pts = poly_pts([(cx - w / 2, top), (cx + w / 2, top), (cx + 4, top + h), (cx - 4, top + h)], 18, seed, 0.8)
    out = [painted(D, pts, pal, seed, sdir=(0.7, 0.3), sk=0.15, angle=-80, n=40, inkw=2.2, hi=0.4)]
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    lines = []
    for k in range(-8, 10):
        x = cx + k * 22
        lines.append(f'<path d="M {x:.1f} {top - 10:.1f} l {h * 0.55:.1f} {h * 1.0:.1f}"/><path d="M {x:.1f} {top - 10:.1f} l {-h * 0.55:.1f} {h * 1.0:.1f}"/>')
    out.append(f'<g {cid}><g stroke="{pal[2]}" stroke-width="3" opacity="0.55" fill="none">{"".join(lines)}</g>'
               f'<path d="M {cx - w:.1f} {top:.1f} L {cx:.1f} {top:.1f} L {cx:.1f} {top + h:.1f} Z" fill="#FFF0C8" opacity="0.18"/>'
               f'<path d="M {cx + w:.1f} {top:.1f} L {cx + w * 0.15:.1f} {top:.1f} L {cx:.1f} {top + h:.1f} Z" fill="#6A3A10" opacity="0.2"/></g>')
    return "".join(out)


@design("chill-out")
def chill_out():
    D = Doc("co")
    out = [f'<rect width="600" height="600" fill="#9AF0E0"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, 0, 600, 600), ["#C8FFF4", "#6ADCC8", "#B8F8EC"], 4, n=180,
                       angle=-12, length=(40, 120), width=(3, 9), opacity=(0.15, 0.4), curve=0.2))
    rnd = random.Random(5)
    # painted polka dots
    for y in range(20, 620, 70):
        for x in range(20 + (35 if (y // 70) % 2 else 0), 640, 70):
            out.append(f'<path d="{blob(x + rnd.uniform(-3, 3), y + rnd.uniform(-3, 3), 9, 8.5, x * 7 + y, 0.1, 10)}" fill="#FFFFFF" opacity="0.55"/>')
    out.append(soft_glow(D, 300, 330, 230, "#FFFFFF", 0.6))
    # puddle & drips on the "table" line
    out.append(cast(D, 306, 548, 110, 14, color="#0E6E6A", strength=0.25))
    out.append(f'<path d="{blob(330, 540, 46, 9, 9, 0.15, 14)}" fill="#FF8AB8"/>')
    out.append(waffle_cone(D, 300, 352, 170, 196, 10))
    out.append(scoop(D, 300, 352, 96, ("#FFF6D8", "#FBE6B0", "#C8A060"), 11, drips=4, chips="#6A3A1E"))
    out.append(scoop(D, 300, 268, 88, MINT, 12, drips=3, chips="#4A2A1A"))
    out.append(scoop(D, 300, 192, 80, PINK, 13, drips=3))
    out.append(sprinkles(14, (240, 128, 360, 176), ["#FFE04A", "#1FB5B0", "#FFFFFF", "#8A5AD0", "#FF8A2A"], 26))
    # cherry on top
    out.append(pline([(306, 112), (312, 86), (326, 70)], "#5A3A1A", 3, 15, 1, 1))
    out.append(painted(D, blob_pts(302, 118, 18, 17, 16, 0.03, 14), RED, 16, sk=0.2, angle=-40, n=8, inkw=1.8, hi=0.5))
    out.append(taper([(294, 112), (298, 106)], 4, 1, "#FFFFFF", 0.8))
    # little drips falling
    out.append(f'<path d="{blob(232, 486, 5, 7, 20, 0.1, 8)}" fill="#FF8AB8"/><path d="{blob(370, 474, 4, 6, 21, 0.1, 8)}" fill="#7EDDB0"/>')
    for x, y, r_ in ((470, 170, 12), (130, 230, 9), (500, 320, 8)):
        out.append(sparkle(x, y, r_, "#FFFFFF"))
    # lettering
    out.append(letters(D, 160, 520, "chill", SERIF_IT, 120, "#E8337E", ["#FF6FAA", "#C21E66", "#FF8AB8"], 22, max_w=188,
                       shadow="#FFFFFF", soff=(0.025, 0.035), angle=-35))
    out.append(letters(D, 454, 520, "OUT", BEBAS, 120, "#0E6E74", ["#1FB5B0", "#0A4E56", "#3FD0C8"], 23, ls=8, max_w=136,
                       shadow="#FFFFFF", soff=(0.03, 0.04), angle=-78, hi="#C8FFF4"))
    return finish(D, out, 47, "#0E5E5A", 0.7)


# ================================================================ 8. salty air, sandy hair — a gull on a dock piling
def gull(D, x, y, s, seed, flip=1):
    """Herring gull standing, facing left (flip=-1 faces right). (x, y) = feet on the perch."""
    def P(px, py):
        return (x + flip * px * s, y + py * s)
    out = [f'<g>']
    # legs
    for dx in (-0.08, 0.1):
        out.append(pline([P(dx, -0.36), P(dx - 0.02, -0.12), P(dx, 0)], "#E8806A", max(2, s * 0.035), seed, 1, 1))
        out.append(pline([P(dx - 0.1, 0.0), P(dx + 0.08, 0.0)], "#E8806A", max(2, s * 0.03), seed + 1, 1, 1))
    tail = [P(0.48, -0.62), P(0.86, -0.72), P(0.9, -0.62), P(0.5, -0.46)]
    out.append(painted(D, tail, ("#FFFFFF", "#E8ECF0", "#9AA4B0"), seed + 2, sk=0.2, angle=0, n=4, inkw=1.6, hi=0.3))
    body = [P(-0.42, -0.86), P(-0.2, -0.98), P(0.2, -0.9), P(0.56, -0.72), P(0.6, -0.6), P(0.3, -0.42), P(0, -0.34), P(-0.3, -0.44), P(-0.46, -0.62)]
    out.append(painted(D, body, ("#FFFFFF", "#F2F4F6", "#A8B4C0"), seed + 3, sdir=(0.2 * flip, 1), sk=0.2, angle=0, n=14, inkw=1.8, hi=0.4))
    head = blob_pts(*P(-0.46, -1.06), 0.22 * s, 0.2 * s, seed + 4, 0.03, 14)
    neck = [P(-0.58, -1.0), P(-0.34, -1.12), P(-0.16, -0.94), P(-0.32, -0.76), P(-0.5, -0.8)]
    out.append(painted(D, neck, ("#FFFFFF", "#F4F6F8", "#B8C0C8"), seed + 5, sk=0.15, angle=-90, n=4, inkw=0, hi=0.3, edge=False))
    out.append(painted(D, head, ("#FFFFFF", "#F6F8FA", "#B8C2CC"), seed + 6, sdir=(0.3 * flip, 1), sk=0.15, angle=-30, n=6, inkw=1.8, hi=0.4))
    beak = [P(-0.64, -1.08), P(-0.98, -1.04), P(-1.02, -1.0), P(-0.9, -0.98), P(-0.64, -1.0)]
    out.append(painted(D, beak, ("#FFF07A", "#FFC83A", "#C88A12"), seed + 7, sk=0.2, angle=0, n=3, inkw=1.6, hi=0.4))
    rx, ry = P(-0.9, -1.0)
    out.append(f'<circle cx="{rx:.1f}" cy="{ry:.1f}" r="{s * 0.028:.1f}" fill="#E8423A"/>')
    ex, ey = P(-0.52, -1.12)
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{s * 0.034:.1f}" fill="#1A1A22"/><circle cx="{ex - flip * s * 0.01:.1f}" cy="{ey - s * 0.012:.1f}" r="{s * 0.012:.1f}" fill="#FFFFFF"/>')
    wing = [P(-0.28, -0.84), P(0.0, -0.9), P(0.4, -0.84), P(0.78, -0.72), P(0.98, -0.66), P(0.78, -0.6), P(0.4, -0.56), P(0.04, -0.6), P(-0.24, -0.7)]
    out.append(painted(D, wing, ("#C8D2DC", "#94A4B4", "#56667A"), seed + 8, sdir=(0, 1), sk=0.2, angle=8 if flip > 0 else 172, n=16, inkw=1.8, hi=0.4))
    tip = [P(0.62, -0.74), P(0.78, -0.72), P(0.98, -0.66), P(0.78, -0.6), P(0.6, -0.6)]
    out.append(painted(D, tip, ("#4A4A56", "#26262E", "#0A0A10"), seed + 9, sk=0.1, angle=0, n=3, inkw=1.4, hi=0.2))
    for k, (px, py) in enumerate(((0.8, -0.67), (0.9, -0.655))):
        cx_, cy_ = P(px, py)
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{s * 0.016:.1f}" fill="#FFFFFF"/>')
    for k in range(3):
        a, b = P(0.0 + k * 0.16, -0.78 + k * 0.02), P(0.14 + k * 0.16, -0.7 + k * 0.02)
        out.append(pline([a, b], "#FFFFFF", max(1.2, s * 0.012), seed + k, 0.6, 1))
    out.append("</g>")
    return "".join(out)


def piling(D, x0, x1, top, bottom, seed, pal=("#C8A27A", "#8E6A48", "#4A3220")):
    pts = poly_pts([(x0, top + 6), (x0 + (x1 - x0) * 0.5, top - 2), (x1, top + 6), (x1 + 2, bottom), (x0 - 2, bottom)], 22, seed, 0.8)
    out = [painted(D, pts, pal, seed, sdir=(1, 0), sk=0.22, angle=-90, n=60, slen=(20, 60), sw=(1, 2.6), inkw=2, hi=0.35, hik=0.12)]
    out.append(f'<path d="{blob((x0 + x1) / 2, top + 4, (x1 - x0) / 2, 9, seed, 0.04, 14)}" fill="{pal[0]}" stroke="{pal[2]}" stroke-width="1.6"/>')
    for k, r in enumerate((0.3, 0.6, 0.85)):
        out.append(f'<ellipse cx="{(x0 + x1) / 2:.1f}" cy="{top + 4:.1f}" rx="{(x1 - x0) / 2 * r:.1f}" ry="{9 * r:.1f}" fill="none" stroke="{pal[1]}" stroke-width="1.2" opacity="0.7"/>')
    for k in range(6):
        y = top + 30 + k * 34
        x = x0 + (k * 13 % (x1 - x0 - 10)) + 5
        out.append(pline([(x, y), (x + 1, y + 18)], pal[2], 1.4, k, 0.5, 1))
    return "".join(out)


def rope_wrap(D, x0, x1, y, turns, seed, col=("#FFF0D0", "#E2C48A", "#9A7A44")):
    out = []
    for k in range(turns):
        yy = y + k * 13
        pts = [(x0 - 4, yy + 4), ((x0 + x1) / 2, yy + 8), (x1 + 4, yy + 4), (x1 + 4, yy + 15), ((x0 + x1) / 2, yy + 19), (x0 - 4, yy + 15)]
        out.append(painted(D, pts, col, seed + k, sk=0.2, angle=-10, n=6, inkw=1.4, hi=0.4))
        for j in range(6):
            xx = x0 + (x1 - x0) * (j + 0.5) / 6
            out.append(pline([(xx - 3, yy + 6), (xx + 3, yy + 16)], col[2], 1.2, j, 0.7, 1))
    # trailing rope end
    out.append(taper([(x0 - 2, y + turns * 13 + 4), (x0 - 18, y + turns * 13 + 40), (x0 - 4, y + turns * 13 + 80), (x0 - 30, y + turns * 13 + 130)], 9, 7, col[1]))
    out.append(pline([(x0 - 2, y + turns * 13 + 4), (x0 - 18, y + turns * 13 + 40), (x0 - 4, y + turns * 13 + 80), (x0 - 30, y + turns * 13 + 130)], col[2], 1.4, seed, 0.6, 1))
    return "".join(out)


@design("salty-air-sandy-hair")
def salty_air_sandy_hair():
    D = Doc("sa")
    out = [sky(D, [(0, "#7ECBF0"), (0.3, "#B8E4F4"), (0.48, "#FFE0C8"), (0.52, "#FFD0B8")], 3, 320, ["#FFFFFF", "#9AD4F0", "#FFE8D8"], 50)]
    out.append(puff_cloud(D, 470, 262, 150, 5, ("#FFFFFF", "#FFF8F4", "#E8C8D0")))
    out.append(puff_cloud(D, 120, 284, 110, 6, ("#FFFFFF", "#FFF8F4", "#E8C8D0")))
    out.append(sea(D, 300, 600, [(0, "#2E9AC8"), (0.5, "#1E6EA8"), (1, "#163E7A")], 7, ["#8ED8F0", "#0E4E8A", "#FFFFFF"], 90, ticks=["#FFFFFF", "#9AE0F4"]))
    # little sailboat on the horizon
    out.append(painted(D, [(214, 298), (214, 262), (236, 296)], ("#FFFFFF", "#FFFFFF", "#C8C0B8"), 8, sk=0, n=2, inkw=1.2, hi=0))
    out.append(painted(D, [(208, 298), (244, 298), (238, 306), (214, 306)], CORAL, 9, sk=0, n=2, inkw=1.2, hi=0))
    out.append(seagull(196, 252, 10, "#3A4A6A") + seagull(220, 240, 7, "#3A4A6A"))
    # dune corner with grass
    dd = smooth_closed([(-20, 470), (50, 446), (130, 462), (210, 520), (280, 620), (-20, 620)])
    out.append(f'<path d="{dd}" fill="#F6D9A0"/>')
    out.append(strokes(D.nid(), dd, (-20, 440, 290, 620), ["#FFF0CE", "#C9A066", "#E8C48A"], 10, n=60, angle=-8, length=(20, 60), width=(2, 5), opacity=(0.2, 0.5)))
    out.append(ink(smooth_open([(-20, 470), (50, 446), (130, 462), (210, 520), (280, 620)]), INK, 2, 11, 1, 0.6))
    rnd = random.Random(12)
    for i in range(26):
        x = rnd.uniform(0, 170)
        base = 470 + (x / 170) * 30
        h = rnd.uniform(40, 90)
        lean = rnd.uniform(-0.3, 0.5)
        out.append(taper([(x, base + 6), (x + lean * h * 0.4, base - h * 0.5), (x + lean * h, base - h)], 4, 0.6, rnd.choice(["#8AA040", "#B8C060", "#6A8030", "#D8D080"]), 0.95))
    out.append(starfish(D, 150, 556, 18, CORAL, 13, 10))
    # the piling with rope, and the gull on top
    out.append(piling(D, 392, 476, 396, 620, 14))
    out.append(rope_wrap(D, 392, 476, 432, 3, 15))
    out.append(gull(D, 440, 400, 140, 16))
    # lettering
    out.append(letters(D, 300, 138, "salty air", SERIF_IT, 100, "#1E3E7A", ["#2E5A9A", "#0E2A5A", "#3E6AB0"], 21, max_w=420,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-35))
    out.append(letters(D, 300, 228, "SANDY HAIR", BEBAS, 100, "#FF6F59", ["#FF8A6A", "#E8463A", "#FFA890"], 22, ls=10, max_w=400,
                       shadow="#1E3E7A", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 48)


# ================================================================ 9. one in a melon — a big painted watermelon slice
@design("one-in-a-melon")
def one_in_a_melon():
    D = Doc("om")
    out = [f'<rect width="600" height="600" fill="#C8F4DA"/>']
    out.append(stripes_in(D, "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (0, 0, 600, 600), 0, [30, 30], ["#B4ECCA", None], 3, 0.8))
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, 0, 600, 600), ["#E8FFF0", "#9ADCB8", "#D8FFE8"], 4, n=160,
                       angle=-80, length=(40, 120), width=(3, 9), opacity=(0.12, 0.3), curve=0.2))
    cx, cy, rx, ry = 300, 300, 250, 236
    def arc(rx_, ry_, a0=0, a1=180, n=40):
        return [(cx + rx_ * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry_ * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    out.append(cast(D, 310, 548, 240, 20, color="#1E6234", strength=0.3))
    rind = jitter(arc(rx, ry), 1, 1)
    out.append(painted(D, rind, ("#7ACB5A", "#2E8A3E", "#14502A"), 5, sdir=(0, 1), sk=0.06, angle=60, n=40, inkw=2.6, hi=0.2))
    # rind stripes
    cid = D.clip(f'<path d="{smooth_closed(rind)}"/>')
    st = "".join(taper([(cx + rx * 1.1 * math.cos(math.radians(a)), cy + ry * 1.1 * math.sin(math.radians(a))), (cx + rx * 0.9 * math.cos(math.radians(a + 4)), cy + ry * 0.9 * math.sin(math.radians(a + 4)))], 10, 4, "#14502A", 0.5)
                 for a in range(6, 180, 12))
    out.append(f'<g {cid}>{st}</g>')
    pale = arc(rx - 20, ry - 20)
    out.append(painted(D, pale, ("#F4FFE0", "#D8F4B0", "#9AC870"), 6, sdir=(0, 1), sk=0.05, angle=0, n=10, inkw=0, hi=0.4, edge=False))
    flesh = arc(rx - 34, ry - 34)
    # bites out of the top right
    bites = [(470, 300, 34), (520, 300, 30)]
    out.append(painted(D, flesh, ("#FF8AA0", "#F23A5A", "#A8122E"), 7, sdir=(0, 1), sk=0.06, angle=90, n=10, inkw=0, hi=0.35, hik=0.04, edge=False))
    fcid = D.clip(f'<path d="{smooth_closed(flesh)}"/>')
    rnd = random.Random(8)
    rad = []
    for i in range(220):
        a = math.radians(rnd.uniform(4, 176))
        r0 = rnd.uniform(0.1, 0.95)
        L = rnd.uniform(0.08, 0.22)
        p0 = (cx + (rx - 34) * r0 * math.cos(a), cy + (ry - 34) * r0 * math.sin(a))
        p1 = (cx + (rx - 34) * min(1, r0 + L) * math.cos(a), cy + (ry - 34) * min(1, r0 + L) * math.sin(a))
        rad.append(taper([p0, p1], rnd.uniform(1.5, 4), 0.6, rnd.choice(["#FF9AB0", "#D81E44", "#FF6A80", "#FFC0CC"]), rnd.uniform(0.3, 0.6)))
    out.append(f'<g {fcid}>{"".join(rad)}</g>')
    # seeds in two arcs
    for ring, n_ in ((0.62, 9), (0.82, 12)):
        for k in range(n_):
            a = math.radians(14 + (152) * (k + 0.5) / n_ + rnd.uniform(-3, 3))
            x, y = cx + (rx - 34) * ring * math.cos(a), cy + (ry - 34) * ring * math.sin(a)
            if any(math.hypot(x - bx, y - by) < br + 10 for bx, by, br in bites):
                continue
            ang = math.degrees(a) - 90
            sp = rot([(x, y - 9), (x + 5, y), (x, y + 9), (x - 5, y)], x, y, ang)
            out.append(painted(D, sp, ("#6A4A3A", "#2A1A14", "#0A0604"), k, sk=0.1, n=1, inkw=0, hi=0, edge=False))
            out.append(f'<circle cx="{x - 1.5:.1f}" cy="{y - 3:.1f}" r="1.6" fill="#FFFFFF" opacity="0.75"/>')
    # top cut face: a slightly lighter, wet edge
    out.append(taper([(cx - rx + 4, cy), (cx, cy + 3), (cx + rx - 4, cy)], 7, 7, "#FF9AB0", 0.8))
    out.append(ink(smooth_closed(rind), INK, 2.4, 9, 2, 0.75))
    bite_d = " ".join(blob(bx, by, br, br * 0.9, int(bx), 0.06, 14) for bx, by, br in bites)
    rcid = D.clip(f'<path d="{smooth_closed(rind)}"/>')
    out.append(f'<g {rcid}><path d="{bite_d}" fill="#C8F4DA"/>' + stripes_in(D, bite_d, (0, 0, 600, 600), 0, [30, 30], ["#B4ECCA", None], 3, 0.8) + '</g>')
    out.append(f'<g {rcid}>' + "".join(ink(blob(bx, by, br, br * 0.9, int(bx), 0.06, 14), "#7A0A1E", 2.2, 3, 1, 0.7) for bx, by, br in bites) + "</g>")
    # juice drops
    for x, y, r_ in ((420, 360, 6), (250, 540, 5), (460, 336, 4)):
        out.append(f'<path d="M {x} {y - r_ * 2.2} Q {x + r_} {y - r_ * 0.4} {x} {y + r_} Q {x - r_} {y - r_ * 0.4} {x} {y - r_ * 2.2} Z" fill="#FF6A80" opacity="0.85"/>')
    out.append(sparkle(90, 330, 12, "#FFFFFF") + sparkle(522, 370, 10, "#FFFFFF"))
    # lettering
    out.append(letters(D, 300, 128, "one in a", SERIF_IT, 96, "#1E6234", ["#2E8A3E", "#14502A", "#4AA05A"], 31, max_w=330,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-35))
    out.append(letters(D, 300, 276, "MELON", BEBAS, 170, "#F23A5A", ["#FF6A80", "#C8163A", "#FF8AA0"], 32, ls=16, max_w=420,
                       shadow="#1E6234", angle=-78, hi="#FFE0E8"))
    return finish(D, out, 49, "#1E6234", 0.7)


# ================================================================ 10. stay cool — three popsicles on a cabana stripe
def popsicle(D, cx, top, w, h, seed, kind, rot_=0):
    stick = [(cx - w * 0.15, top + h - 10), (cx + w * 0.15, top + h - 10), (cx + w * 0.15, top + h + h * 0.34), (cx, top + h + h * 0.38), (cx - w * 0.15, top + h + h * 0.34)]
    body = []
    r = w / 2
    for i in range(13):
        a = math.pi + math.pi * i / 12
        body.append((cx + r * math.cos(a), top + r + r * 0.9 * math.sin(a)))
    body += [(cx + r, top + h * 0.55), (cx + r * 0.98, top + h), (cx - r * 0.98, top + h), (cx - r, top + h * 0.55)]
    if kind == "cherry":
        dome = []
        for i in range(37):
            a_ = math.pi + math.pi * i / 36
            dome.append((cx + r * math.cos(a_), top + r + r * 0.9 * math.sin(a_)))
        body = dome + [(cx + r, top + r + 10), (cx + r, top + h * 0.55), (cx + r * 0.98, top + h), (cx - r * 0.98, top + h), (cx - r, top + h * 0.55)]
        body = bite_out(body, cx + r * 0.9, top + r * 0.3, r * 0.36)
        body = bite_out(body, cx + r * 0.42, top + r * 0.0, r * 0.3)
    out = [f'<g transform="rotate({rot_} {cx} {top + h})">']
    out.append(painted(D, stick, WOOD, seed, sdir=(1, 0), sk=0.2, angle=-90, n=8, inkw=1.8, hi=0.35))
    out.append(pline([(cx - w * 0.05, top + h + 6), (cx - w * 0.04, top + h + h * 0.3)], WOOD[2], 1.2, seed, 0.5, 1))
    pal = {"cherry": RED, "rainbow": PINK, "mint": MINT}[kind]
    out.append(painted(D, body, pal, seed + 1, sdir=(0.6, 0.4), sk=0.14, angle=-90, n=40, slen=(h * 0.08, h * 0.25), sw=(1.5, 4), inkw=2.2, hi=0.4, hik=0.08))
    bd = smooth_closed(body)
    cid = D.clip(f'<path d="{bd}"/>')
    inner = []
    if kind == "rainbow":
        for k, (c, y0) in enumerate(((SUN, 0.36), (TURQ, 0.66))):
            band = [(cx - r - 4, top + h * y0 + 5 * math.sin(i)) for i in range(1)] 
            pts = [(cx - r - 6, top + h * y0)] + [(cx - r + 2 * r * i / 8, top + h * y0 + 4 * math.sin(i * 1.3 + k)) for i in range(9)] + [(cx + r + 6, top + h * y0), (cx + r + 6, top + h + 10), (cx - r - 6, top + h + 10)]
            inner.append(painted(D, pts, c, seed + 10 + k, sdir=(0.6, 0.4), sk=0.1, angle=-90, n=20, inkw=1.4, inkop=0.5, hi=0.3, edge=False))
    if kind == "mint":
        dip = [(cx - r - 6, top + h * 0.42)] + [(cx - r + 2 * r * i / 8, top + h * 0.42 + (6 if i % 2 else -2) + (14 if i in (3,) else 0)) for i in range(9)] + [(cx + r + 6, top + h * 0.42), (cx + r + 6, top + h + 10), (cx - r - 6, top + h + 10)]
        inner.append(painted(D, dip, ("#9A6A4A", "#5A321E", "#2A140A"), seed + 12, sdir=(0.6, 0.4), sk=0.12, angle=-90, n=20, inkw=1.4, inkop=0.6, hi=0.3, edge=False))
        inner.append(sprinkles(seed, (cx - r, top + h * 0.5, cx + r, top + h * 0.95), ["#FFE04A", "#FF5FA2", "#FFFFFF", "#1FB5B0", "#FF8A2A"], 18, 7, 3))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(taper([(cx - r * 0.55, top + h * 0.85), (cx - r * 0.6, top + h * 0.4), (cx - r * 0.4, top + r * 0.4)], max(4, w * 0.08), 1.5, "#FFFFFF", 0.6))
    out.append(taper([(cx - r * 0.25, top + h * 0.8), (cx - r * 0.28, top + h * 0.6)], 3, 1, "#FFFFFF", 0.45))
    out.append(ink(bd, INK, 2.2, seed + 2, 2, 0.75))
    # a drip
    out.append(f'<path d="M {cx + r * 0.3:.1f} {top + h - 4:.1f} q 4 14 0 22 q -6 4 -8 -2 q -1 -10 2 -20 Z" fill="{pal[1]}" stroke="{INK}" stroke-width="1.4" stroke-opacity="0.6"/>' if kind != "mint" else "")
    out.append("</g>")
    return "".join(out)


@design("stay-cool")
def stay_cool():
    D = Doc("sc")
    out = [f'<rect width="600" height="600" fill="#FF5FA2"/>']
    out.append(stripes_in(D, "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (0, 0, 600, 600), 0, [50, 50], ["#FF7AB4", None], 3))
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, 0, 600, 600), ["#FF9AC8", "#E8337E", "#FFB0D0"], 4, n=180,
                       angle=-84, length=(40, 140), width=(3, 9), opacity=(0.12, 0.3), curve=0.15))
    out.append(soft_glow(D, 300, 330, 260, "#FFE0EE", 0.5))
    out.append(cast(D, 300, 452, 200, 16, color="#8A0A44", strength=0.3))
    out.append(popsicle(D, 182, 184, 100, 192, 10, "mint", -16))
    out.append(popsicle(D, 418, 184, 100, 192, 20, "rainbow", 16))
    out.append(popsicle(D, 300, 160, 108, 204, 30, "cherry", 0))
    # ice crystals & sparkles
    for x, y, r_ in ((80, 170, 14), (520, 160, 12), (90, 430, 10), (514, 430, 12), (300, 140, 0)):
        if r_:
            out.append(sparkle(x, y, r_, "#FFFFFF"))
    out.append(letters(D, 300, 128, "stay", SERIF_IT, 110, "#FFFFFF", ["#FFFFFF", "#FFE0EE", "#FFF0F6"], 31, max_w=240,
                       shadow="#8A0A44", soff=(0.025, 0.04), angle=-35))
    out.append(letters(D, 300, 540, "COOL", BEBAS, 140, "#22D0D8", ["#5AE8E8", "#0E9AA8", "#8EF0F0"], 32, ls=22, max_w=330,
                       shadow="#5A0A30", angle=-78, hi="#FFFFFF", inkc="#0A4E56", inkw=1.6))
    return finish(D, out, 50, "#5A0A30", 0.6)


# ================================================================ 11. aloha — a pineapple in sunglasses among hibiscus
def tropical_leaf(D, cx, cy, s, rot_, seed, pal=LEAF, slit_col=None):
    """Split-leaf (monstera-like) tropical leaf; slits painted in the background colour."""
    pts = []
    for i in range(44):
        t = i / 44 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * s / 17, cy + y * s / 17))
    pts = rot(pts, cx, cy, rot_)
    out = [painted(D, pts, pal, seed, sdir=(0.5, 0.6), sk=0.14, angle=rot_ - 90, n=int(s * 0.7), inkw=max(1.2, s * 0.02), hi=0.3)]
    if slit_col:
        for k, yy in enumerate((-0.5, -0.15, 0.2)):
            for sg in (-1, 1):
                wpts = rot([(cx + sg * s * 1.02, cy - yy * s - 0.06 * s), (cx + sg * s * 0.5, cy - yy * s + 0.02 * s), (cx + sg * s * 0.2, cy - yy * s + 0.08 * s)], cx, cy, rot_)
                out.append(taper(wpts, max(4, s * 0.12), 1, slit_col))
    mid = rot([(cx, cy - 0.85 * s), (cx, cy), (cx, cy + 0.75 * s)], cx, cy, rot_)
    out.append(pline(mid, pal[0], max(1.4, s * 0.035), seed, 0.8, 1))
    for yy in (-0.32, 0.02, 0.36):
        for sg in (-1, 1):
            p = rot([(cx, cy - yy * s - 0.12 * s), (cx + sg * s * 0.4, cy - yy * s), (cx + sg * s * 0.75, cy - yy * s + 0.08 * s)], cx, cy, rot_)
            out.append(pline(p, pal[0], max(1, s * 0.02), seed + 3, 0.45, 1))
    return "".join(out)


def pineapple(D, cx, cy, w, h, seed):
    body = blob_pts(cx, cy, w / 2, h / 2, seed, 0.02, 24)
    pal = ("#FFE27A", "#F6B42A", "#B8700E")
    out = [cast(D, cx + 10, cy + h / 2 + 4, w * 0.6, 14, strength=0.35, seed=seed)]
    # crown (behind the body)
    rnd = random.Random(seed)
    crown = []
    for k in range(13):
        t = k / 12
        ang = -90 + (t - 0.5) * 150
        L = h * (0.55 - 0.3 * abs(t - 0.5) * 2) * rnd.uniform(0.85, 1.1)
        a = math.radians(ang)
        bx, by = cx + (t - 0.5) * w * 0.4, cy - h / 2 + 10
        tip = (bx + L * math.cos(a), by + L * math.sin(a))
        mid = (bx + L * 0.5 * math.cos(a) + 6 * math.sin(a), by + L * 0.5 * math.sin(a))
        crown.append((abs(t - 0.5), [(bx, by), mid, tip]))
    for depth, pts in sorted(crown, key=lambda c: -c[0]):
        col = rnd.choice([LEAF, ("#7AD07A", "#2E9A5A", "#145A34"), ("#A8E07A", "#4AAA3A", "#1E6224")])
        out.append(taper(pts, w * 0.13, 1.5, col[2]))
        out.append(taper(pts, w * 0.11, 1, col[1]))
        out.append(taper(pts[:2] + [pts[2]], w * 0.04, 0.5, col[0], 0.7))
    out.append(painted(D, body, pal, seed, sdir=(0.6, 0.5), sk=0.18, angle=-90, n=60, inkw=2.4, hi=0.35))
    # diamond scales
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    sc = []
    step = w / 5.2
    for i in range(-6, 7):
        for j in range(-8, 9):
            x = cx + (i + (0.5 if j % 2 else 0)) * step
            y = cy + j * step * 0.62
            d = f"M {x:.1f} {y - step * 0.6:.1f} Q {x + step * 0.55:.1f} {y - step * 0.1:.1f} {x + step * 0.5:.1f} {y:.1f} Q {x + step * 0.4:.1f} {y + step * 0.4:.1f} {x:.1f} {y + step * 0.62:.1f} Q {x - step * 0.4:.1f} {y + step * 0.4:.1f} {x - step * 0.5:.1f} {y:.1f} Q {x - step * 0.55:.1f} {y - step * 0.1:.1f} {x:.1f} {y - step * 0.6:.1f} Z"
            sc.append(f'<path d="{d}" fill="none" stroke="#B8700E" stroke-width="2" opacity="0.7"/>')
            sc.append(f'<path d="M {x - step * 0.2:.1f} {y + step * 0.15:.1f} q {step * 0.2:.1f} {-step * 0.25:.1f} {step * 0.4:.1f} 0" stroke="#FFF2B0" stroke-width="2" fill="none" opacity="0.6"/>')
            sc.append(f'<circle cx="{x:.1f}" cy="{y + step * 0.38:.1f}" r="{step * 0.07:.1f}" fill="#8A4A0A" opacity="0.7"/>')
    shade = D.lin([(0, "#FFFFFF", 0.2), (0.45, "#FFFFFF", 0), (1, "#7A3A00", 0.35)], 0, 0, 1, 0.3)
    sc.append(f'<path d="{smooth_closed(body)}" fill="{shade}"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(ink(smooth_closed(body), "#6A3A0A", 2.4, seed + 1, 2, 0.75))
    out.append(taper([(cx - w * 0.36, cy + h * 0.1), (cx - w * 0.38, cy - h * 0.15), (cx - w * 0.26, cy - h * 0.36)], 6, 1, "#FFF6D0", 0.6))
    return "".join(out)


@design("aloha")
def aloha():
    D = Doc("al")
    bg = "#2EC8C0"
    out = [f'<rect width="600" height="600" fill="{bg}"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, 0, 600, 600), ["#6AE8E0", "#1EA8A8", "#8EF4EC"], 4, n=180,
                       angle=-30, length=(40, 120), width=(3, 9), opacity=(0.15, 0.35), curve=0.2))
    out.append(soft_glow(D, 300, 300, 240, "#FFF6C8", 0.55))
    # tropical leaves reaching in from the corners
    G2 = ("#7AD07A", "#2E9A5A", "#145A34")
    G3 = ("#A8E07A", "#4AAA3A", "#1E6224")
    for i, (x, y, ang, L, W, pal) in enumerate(((-30, -20, 40, 230, 46, LEAF), (-40, 120, 5, 190, 40, G2), (630, -10, 140, 230, 46, G2), (640, 130, 172, 180, 38, G3),
                                                 (-30, 620, -40, 230, 46, G2), (-40, 470, -8, 170, 36, G3), (630, 620, -140, 230, 46, LEAF), (640, 480, -172, 170, 38, G2))):
        out.append(banana_leaf(D, x, y, ang, L, W, 10 + i, pal, bg))
    for i, (x, y, r_, pal, ro) in enumerate(((106, 156, 46, PINK, 10), (500, 150, 40, CORAL, -20), (108, 418, 40, CORAL, 40), (500, 410, 46, PINK, 0),
                                              (70, 286, 26, SUN, 15), (536, 286, 26, ("#FFFFFF", "#FFE8F0", "#E8A0B8"), 30))):
        out.append(hibiscus(D, x, y, r_, pal, 20 + i, ro))
    # the pineapple, wearing shades
    out.append(pineapple(D, 300, 346, 190, 228, 30))
    out.append(sunglasses(D, 300, 306, 100, ("#FF8AC0", "#FF3A8A", "#9A0E4A"), ("#7AE8F0", "#1E7AB0", "#0A2A5A"), 31, -4, round_=False))
    out.append(pline([(274, 368), (300, 384), (326, 368)], "#6A2A00", 3.4, 32, 1, 1))
    out.append(f'<ellipse cx="248" cy="358" rx="12" ry="7" fill="#FF6A6A" opacity="0.5"/><ellipse cx="352" cy="358" rx="12" ry="7" fill="#FF6A6A" opacity="0.5"/>')
    out.append(letters(D, 300, 540, "aloha", SERIF_IT, 130, "#FFFFFF", ["#FFFFFF", "#FFE8F2", "#FFF4D0"], 33, max_w=330,
                       shadow="#D81E7A", soff=(0.03, 0.045), angle=-35))
    out.append(sparkle(440, 230, 12, "#FFFFFF") + sparkle(160, 240, 9, "#FFFFFF"))
    return finish(D, out, 51, "#0A4E4E", 0.6)


# ================================================================ 12. sandy toes, sun-kissed nose — flip-flops at the tide line
def flipflop(D, cx, cy, L, seed, sole=CORAL, strap=TURQ, flip=1, rot_=0, flower=None):
    """Top-down flip-flop, toe at the top. flip mirrors left/right foot."""
    N = [(0.15, -0.5), (0.66, -0.46), (0.98, -0.34), (1.04, -0.18), (0.9, -0.02), (0.64, 0.12), (0.66, 0.3), (0.6, 0.43), (0.36, 0.5),
         (0.0, 0.52), (-0.36, 0.48), (-0.58, 0.36), (-0.62, 0.18), (-0.58, 0.02), (-0.74, -0.18), (-0.74, -0.36), (-0.45, -0.47)]
    outline = [(cx + flip * x * L * 0.21, cy + y * L) for x, y in N]
    out = [f'<g transform="rotate({rot_} {cx} {cy})">']
    out.append(cast(D, cx + 8, cy + 10, L * 0.24, L * 0.52, strength=0.3, seed=seed))
    out.append(painted(D, outline, sole, seed, sdir=(0.5, 0.6), sk=0.08, angle=-90, n=30, inkw=2.2, hi=0.3))
    inner = [(cx + (x - cx) * 0.82, cy + (y - cy) * 0.94) for x, y in outline]
    out.append(painted(D, inner, (mix(sole[0], "#FFFFFF", 0.4), sole[0], sole[1]), seed + 1, sdir=(0.5, 0.6), sk=0.1, angle=-90, n=30, inkw=0, hi=0.2, edge=False))
    # straps
    post = (cx + flip * L * 0.02, cy - L * 0.3)
    for sg in (-1, 1):
        end = (cx + sg * L * 0.16 + flip * L * 0.01, cy + L * 0.04)
        mid = ((post[0] + end[0]) / 2 + sg * L * 0.05, (post[1] + end[1]) / 2 - L * 0.04)
        out.append(taper([end, mid, post], L * 0.075, L * 0.05, strap[2]))
        out.append(taper([end, mid, post], L * 0.06, L * 0.04, strap[1]))
        out.append(taper([end, mid], L * 0.02, L * 0.015, strap[0], 0.8))
    if flower:
        out.append(daisy(D, post[0], post[1], L * 0.09, seed + 5, petal=flower, n=6))
    else:
        out.append(f'<circle cx="{post[0]:.1f}" cy="{post[1]:.1f}" r="{L * 0.035:.1f}" fill="{strap[2]}"/>')
    out.append("</g>")
    return "".join(out)


@design("sandy-toes-sun-kissed-nose")
def sandy_toes():
    D = Doc("st")
    out = [f'<rect width="600" height="600" fill="#F8DCA8"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, 0, 600, 600), ["#FFF0C8", "#E2B87A", "#F6D090", "#FFF8E0"], 3,
                       n=200, angle=-12, length=(40, 120), width=(3, 9), opacity=(0.15, 0.4), curve=0.15))
    out.append(specks(4, (0, 0, 600, 600), ["#C49A5A", "#FFFFFF", "#A87A44", "#E8A890"], 420, (0.6, 1.8), (0.3, 0.7)))
    # wet sand & the tide sweeping in from the bottom right
    tide = [(-20, 620), (-20, 470), (90, 474), (200, 462), (310, 446), (410, 420), (490, 392), (560, 366), (620, 350), (620, 620)]
    out.append(f'<path d="{smooth_closed(shift(tide, 0, -26))}" fill="#E2BC80" opacity="0.7"/>')
    td = smooth_closed(tide)
    out.append(f'<path d="{td}" fill="{D.lin([(0, "#8EF0E0"), (0.4, "#3FD0D0"), (1, "#1E9AB8")], 0.4, 0, 0.8, 1)}" opacity="0.92"/>')
    out.append(strokes(D.nid(), td, (-20, 360, 620, 620), ["#C8FFF4", "#1E8AA0", "#FFFFFF"], 5, n=60, angle=-18, length=(30, 80), width=(2, 5), opacity=(0.2, 0.5)))
    edge = tide[1:-1]
    out.append(taper(edge, 10, 4, "#FFFFFF", 0.95))
    out.append(taper([(x + 10, y + 26) for x, y in edge], 4, 3, "#FFFFFF", 0.6))
    rnd = random.Random(6)
    for i in range(50):
        k = rnd.randint(0, len(edge) - 2)
        t = rnd.random()
        x = edge[k][0] + (edge[k + 1][0] - edge[k][0]) * t
        y = edge[k][1] + (edge[k + 1][1] - edge[k][1]) * t
        out.append(f'<circle cx="{x + rnd.uniform(-4, 4):.1f}" cy="{y + rnd.uniform(-4, 10):.1f}" r="{rnd.uniform(1.2, 3.2):.1f}" fill="#FFFFFF" opacity="0.9"/>')
    # flip-flops
    out.append(flipflop(D, 236, 300, 190, 10, ("#FF9ACD", "#FF4F9E", "#B81E62"), ("#FFF07A", "#FFC93C", "#C8880E"), flip=1, rot_=-14, flower=("#FFFFFF", "#FFFFFF", "#E8C0D0")))
    out.append(flipflop(D, 372, 318, 190, 11, ("#FF9ACD", "#FF4F9E", "#B81E62"), ("#FFF07A", "#FFC93C", "#C8880E"), flip=-1, rot_=10, flower=("#FFFFFF", "#FFFFFF", "#E8C0D0")))
    # shells & a starfish
    out.append(starfish(D, 506, 300, 26, ("#FFC08A", "#FF8A4A", "#C04A1A"), 12, 14))
    out.append(scallop(D, 100, 330, 22, ("#FFF0F4", "#FFC0D0", "#C0708A"), 13, -15))
    out.append(scallop(D, 520, 214, 15, ("#FFF6E0", "#F8D8A0", "#B8905A"), 14, 25))
    out.append(sunglasses(D, 104, 230, 52, ("#7AE8F0", "#1FB5B0", "#0A5A5E"), ("#FFB07A", "#E8501E", "#7A1A0A"), 15, 18, round_=True))
    # lettering
    out.append(letters(D, 300, 128, "sandy toes", SERIF_IT, 104, "#E8337E", ["#FF6FAA", "#C21E66", "#FF8AB8"], 21, max_w=420,
                       shadow="#FFF4DC", soff=(-0.02, -0.025), angle=-35))
    out.append(letters(D, 300, 540, "SUN-KISSED NOSE", BEBAS, 80, "#FFFFFF", ["#FFFFFF", "#E8FFFA", "#C8F4F0"], 22, ls=6, max_w=440,
                       shadow="#0E5E7E", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 52, "#8A5A3A", 0.7)


# ================================================================ 13. fresh lemonade — a little backyard stand
def lemon(D, cx, cy, r, seed, rot_=0):
    pts = []
    for i in range(24):
        a = 2 * math.pi * i / 24
        k = 1 + 0.18 * abs(math.cos(a)) ** 8
        pts.append((cx + r * 1.25 * math.cos(a) * k, cy + r * math.sin(a)))
    pts = rot(pts, cx, cy, rot_)
    out = [painted(D, pts, ("#FFF4A0", "#FFE03A", "#C8A010"), seed, sdir=(0.5, 0.7), sk=0.2, angle=-30 + rot_, n=int(r), inkw=max(1.4, r * 0.06), hi=0.45)]
    out.append(taper(rot([(cx - r * 0.7, cy - r * 0.2), (cx - r * 0.3, cy - r * 0.6)], cx, cy, rot_), max(2, r * 0.14), 1, "#FFFFFF", 0.7))
    return "".join(out)


def lemon_wheel(D, cx, cy, r, seed):
    return citrus_slice(D, cx, cy, r, seed, ("#FFF6B0", "#FFE24A", "#D8B010"), "#FFFCE8", ("#FFF07A", "#FFD21A", "#C89A0A"))


@design("fresh-lemonade")
def fresh_lemonade():
    D = Doc("fl")
    out = [sky(D, [(0, "#6AD4F4"), (0.6, "#B8EEFA"), (0.8, "#E8FAFF")], 3, 470, ["#FFFFFF", "#8ADCF4", "#D8F6FF"], 50)]
    out.append(puff_cloud(D, 80, 150, 110, 4, ("#FFFFFF", "#FFFFFF", "#B8DFF0")))
    out.append(puff_cloud(D, 540, 120, 120, 5, ("#FFFFFF", "#FFFFFF", "#B8DFF0")))
    # lawn
    gl = ridge([(-20, 440), (200, 432), (420, 440), (620, 430)], 6, 4)
    out.append(hill(D, gl, 620, ("#A8E07A", "#5AB84A", "#2E7A34"), 6, angle=-4, inkw=1.6))
    out.append(grass(7, (-10, 440, 610, 600), ["#2E7A34", "#7ACB5A", "#A8E07A", "#4AA040"], 200, (8, 20)))
    for i, (x, y) in enumerate(((54, 520), (556, 530), (120, 566), (500, 572))):
        out.append(daisy(D, x, y, 12, 60 + i, n=8))
    # stand: posts, counter, front panel
    out.append(cast(D, 300, 540, 220, 16, strength=0.35))
    for x in (122, 478):
        out.append(painted(D, rect_pts(x - 9, 206, x + 9, 400, 20, x, 0.6), ("#FFFFFF", "#F4ECE0", "#B8A890"), x, sdir=(1, 0), sk=0.25, angle=-90, n=10, inkw=1.8, hi=0.3))
    front = rect_pts(110, 400, 490, 534, 24, 8, 1)
    out.append(painted(D, front, ("#FFC8DC", "#FF8AB8", "#C8406E"), 8, sdir=(0.5, 1), sk=0.12, angle=-90, n=50, inkw=2.2, hi=0.3))
    for x in range(134, 480, 36):
        out.append(pline([(x, 404), (x + 1, 530)], "#C8406E", 1.6, x, 0.5, 1))
    counter = rect_pts(96, 384, 504, 404, 24, 9, 0.6)
    out.append(painted(D, counter, ("#FFFFFF", "#F4ECE0", "#B8A890"), 9, sdir=(0, 1), sk=0.25, angle=0, n=14, inkw=2, hi=0.4))
    # awning with scalloped edge
    aw_top, aw_bot = 196, 250
    aw = poly_pts([(92, aw_bot), (100, aw_top), (500, aw_top), (508, aw_bot)], 30, 10, 0.6)
    ad = smooth_closed(aw)
    out.append(f'<path d="{ad}" fill="#FFFFFF"/>')
    out.append(stripes_in(D, ad, (60, 180, 540, 270), 0, [40, 40], ["#FFD23A", None], 11))
    out.append(ink(ad, INK, 2, 12, 1, 0.7))
    for k in range(10):
        x0 = 92 + k * 41.6
        col = "#FFD23A" if k % 2 == 0 else "#FFFFFF"
        sc = [(x0, aw_bot - 2), (x0 + 20.8, aw_bot + 20), (x0 + 41.6, aw_bot - 2)]
        out.append(painted(D, [(x0, aw_bot - 2)] + [(x0 + 20.8 + 20.8 * math.cos(math.radians(a)), aw_bot - 2 + 20 * math.sin(math.radians(a))) for a in range(0, 181, 30)][::-1][::-1] + [(x0 + 41.6, aw_bot - 2)],
                           ("#FFF6C0", col, "#C8A010") if col != "#FFFFFF" else WHITE, 13 + k, sk=0.2, angle=0, n=3, inkw=1.6, inkop=0.6, hi=0.3))
    # sign board on top of the awning
    board = rect_pts(118, 64, 482, 186, 26, 14, 1)
    out.append(cast(D, 306, 190, 180, 8, strength=0.25))
    out.append(painted(D, board, ("#FFFFFF", "#FFF6E4", "#C8B898"), 14, sdir=(0.5, 1), sk=0.1, angle=-2, n=40, inkw=2.4, hi=0.3))
    out.append(ink(smooth_closed(rect_pts(128, 74, 472, 176, 26, 15, 0.8)), "#FF5FA2", 2.4, 15, 1, 0.8))
    for x in (176, 424):
        out.append(painted(D, rect_pts(x - 6, 186, x + 6, 200, 6, x, 0.4), WOOD, x, sk=0.2, n=2, inkw=1.4, hi=0.3))
    # pitcher, glasses, lemons on the counter
    pit = [(232, 384), (226, 330), (236, 300), (230, 284), (290, 282), (300, 292), (292, 312), (300, 340), (296, 384)]
    out.append(cast(D, 264, 386, 40, 6, strength=0.3))
    out.append(painted(D, pit, ("#FFFCE0", "#FFF29A", "#D8C060"), 20, sdir=(0.6, 0.3), sk=0.15, angle=-90, n=16, inkw=2, hi=0.5))
    out.append(f'<path d="M 296 304 Q 330 306 324 334 Q 318 358 296 356" fill="none" stroke="{INK}" stroke-width="6" opacity="0.75"/><path d="M 296 304 Q 326 308 320 334 Q 316 354 296 352" fill="none" stroke="#FFFCE8" stroke-width="3"/>')
    out.append(lemon_wheel(D, 252, 340, 15, 21) + lemon_wheel(D, 278, 360, 13, 22))
    for k in range(4):
        out.append(f'<path d="{blob(242 + k * 12, 310 + (k % 2) * 8, 6, 5, 30 + k, 0.1, 8, 20)}" fill="#FFFFFF" opacity="0.6"/>')
    out.append(taper([(240, 372), (238, 304)], 4, 2, "#FFFFFF", 0.7))
    for i, x in enumerate((340, 384)):
        g = [(x - 18, 314), (x + 18, 314), (x + 14, 384), (x - 14, 384)]
        out.append(cast(D, x, 386, 20, 5, strength=0.3))
        out.append(painted(D, g, ("#FFFCE8", "#FFF4A8", "#D8C060"), 23 + i, sdir=(0.6, 0.3), sk=0.15, angle=-90, n=6, inkw=1.8, hi=0.5))
        out.append(f'<path d="M {x - 17} 314 L {x + 17} 314 L {x + 16} 326 L {x - 16} 326 Z" fill="#FFFFFF" opacity="0.5"/>')
        out.append(taper([(x + 4, 330), (x + 18, 288)], 5, 5, "#FF5FA2") + taper([(x + 4, 330), (x + 18, 288)], 2, 2, "#FFFFFF", 0.7))
        out.append(lemon_wheel(D, x - 16, 316, 11, 25 + i))
    out.append(lemon(D, 432, 370, 15, 27, -10) + lemon(D, 460, 374, 13, 28, 15) + lemon(D, 446, 352, 13, 29, 5))
    out.append(lemon(D, 168, 372, 14, 31, 10))
    # price tag hanging on the front
    out.append(pline([(300, 404), (276, 424)], "#7A5A3A", 1.6, 40, 0.9, 1) + pline([(300, 404), (324, 424)], "#7A5A3A", 1.6, 41, 0.9, 1))
    tag = rect_pts(246, 424, 354, 500, 16, 42, 0.8)
    out.append(painted(D, rot(tag, 300, 462, -4), ("#FFFFFF", "#FFFCE8", "#C8B898"), 42, sk=0.1, angle=0, n=10, inkw=2, hi=0.2))
    out.append(f'<g transform="rotate(-4 300 462)"><circle cx="300" cy="412" r="4" fill="#7A5A3A"/>' + label(300, 488, "25¢", BEBAS, 66, "#E8337E", ls=2, max_w=90) + "</g>")
    # lettering on the board
    out.append(letters(D, 300, 120, "fresh", SERIF_IT, 66, "#E8337E", ["#FF6FAA", "#C21E66", "#FF8AB8"], 45, max_w=200, angle=-35))
    out.append(letters(D, 300, 170, "LEMONADE", BEBAS, 62, "#F2A800", ["#FFD23A", "#D88A00", "#FFE27A"], 46, ls=8, max_w=300,
                       shadow="#7A4A0A", soff=(0.03, 0.04), angle=-78, hi="#FFF6C0"))
    return finish(D, out, 53)


# ================================================================ 14. beach days — the beach from above: umbrellas, towels, surf
def umbrella_top(D, cx, cy, r, cols, seed, n=8, shadow=(26, 30)):
    out = [f'<path d="{blob(cx + shadow[0], cy + shadow[1], r * 1.02, r * 0.92, seed + 1, 0.03, 16)}" fill="#8A5A2A" opacity="0.28"/>']
    pts = []
    for i in range(n):
        for j in range(4):
            a = 2 * math.pi * (i + j / 4) / n
            k = 1 - 0.05 * math.sin(math.pi * j / 4)
            pts.append((cx + r * k * math.cos(a), cy + r * k * math.sin(a)))
    d = smooth_closed(pts)
    out.append(f'<path d="{d}" fill="{cols[0][1]}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    w = []
    for i in range(n):
        pal = cols[i % len(cols)]
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        w.append(f'<path d="M {cx:.1f} {cy:.1f} L {cx + 1.3 * r * math.cos(a0):.1f} {cy + 1.3 * r * math.sin(a0):.1f} L {cx + 1.3 * r * math.cos(a1):.1f} {cy + 1.3 * r * math.sin(a1):.1f} Z" fill="{pal[1]}"/>')
        mid = (a0 + a1) / 2
        w.append(f'<path d="M {cx:.1f} {cy:.1f} L {cx + 1.3 * r * math.cos(a0):.1f} {cy + 1.3 * r * math.sin(a0):.1f} L {cx + 1.3 * r * math.cos(mid):.1f} {cy + 1.3 * r * math.sin(mid):.1f} Z" fill="#000000" opacity="0.08"/>')
    shade = D.rad([(0, "#FFFFFF", 0.25), (0.5, "#FFFFFF", 0), (1, "#000000", 0.25)], 0.38, 0.35, 0.7)
    w.append(f'<rect x="{cx - r:.1f}" y="{cy - r:.1f}" width="{2 * r:.1f}" height="{2 * r:.1f}" fill="{shade}"/>')
    out.append(f'<g {cid}>{"".join(w)}</g>')
    out.append(strokes(D.nid(), d, (cx - r, cy - r, cx + r, cy + r), ["#FFFFFF", "#000000"], seed, n=int(r), angle=-40, length=(r * 0.2, r * 0.5), width=(1, 2.5), opacity=(0.06, 0.18)))
    for i in range(n):
        a = 2 * math.pi * i / n
        out.append(pline([(cx, cy), (cx + r * 0.95 * math.cos(a), cy + r * 0.95 * math.sin(a))], "#000000", 1.2, seed + i, 0.18, 1))
    out.append(ink(d, INK, 2, seed, 2, 0.7))
    out.append(painted(D, blob_pts(cx, cy, r * 0.09, r * 0.09, seed + 3, 0.05, 8), WOOD, seed + 3, sk=0.2, n=2, inkw=1.4, hi=0.5))
    return "".join(out)


def towel_top(D, cx, cy, w, h, ang, cols, seed):
    pts = rot(rect_pts(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 16, seed, 0.8), cx, cy, ang)
    d = smooth_closed(pts)
    out = [f'<path d="{smooth_closed(shift(pts, 4, 5))}" fill="#8A5A2A" opacity="0.18"/>', f'<path d="{d}" fill="{cols[0]}"/>']
    out.append(stripes_in(D, d, (cx - w, cy - h, cx + w, cy + h), ang + 90, [h * 0.12, h * 0.12], [cols[1], None], seed))
    out.append(ink(d, "#8A5A3A", 1.4, seed, 1, 0.5))
    return "".join(out)


def swim_ring(D, cx, cy, r, pal, seed, stripes=WHITE):
    out = [f'<path d="{blob(cx + 6, cy + 10, r, r * 0.9, seed, 0.03, 14)}" fill="#0A4A6A" opacity="0.25"/>']
    ring_o = blob(cx, cy, r, r * 0.92, seed + 1, 0.02, 18)
    ring_i = blob(cx, cy, r * 0.48, r * 0.44, seed + 2, 0.02, 14)
    d = f"{ring_o} {ring_i}"
    out.append(f'<path d="{d}" fill-rule="evenodd" fill="{pal[1]}"/>')
    cid = D.clip(f'<path d="{d}" clip-rule="evenodd" fill-rule="evenodd"/>')
    seg = []
    for k in range(0, 8, 2):
        a0, a1 = math.radians(k * 45 + 10), math.radians(k * 45 + 55)
        seg.append(f'<path d="M {cx:.1f} {cy:.1f} L {cx + 2 * r * math.cos(a0):.1f} {cy + 2 * r * math.sin(a0):.1f} L {cx + 2 * r * math.cos(a1):.1f} {cy + 2 * r * math.sin(a1):.1f} Z" fill="{stripes[1]}"/>')
    sh = D.rad([(0.45, "#000000", 0.25), (0.62, "#FFFFFF", 0.3), (0.8, "#FFFFFF", 0), (1, "#000000", 0.3)], 0.5, 0.5, 0.5)
    seg.append(f'<rect x="{cx - r:.1f}" y="{cy - r:.1f}" width="{2 * r:.1f}" height="{2 * r:.1f}" fill="{sh}"/>')
    out.append(f'<g {cid}>{"".join(seg)}</g>')
    out.append(ink(ring_o, INK, 1.8, seed, 1, 0.7) + ink(ring_i, INK, 1.6, seed + 1, 1, 0.6))
    out.append(taper([(cx - r * 0.75, cy - r * 0.1), (cx - r * 0.6, cy - r * 0.55), (cx - r * 0.2, cy - r * 0.75)], max(2, r * 0.1), 1, "#FFFFFF", 0.7))
    return "".join(out)


@design("beach-days")
def beach_days():
    D = Doc("bd")
    out = [f'<rect width="600" height="600" fill="#F8DCA8"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, 0, 600, 600), ["#FFF0C8", "#E2B87A", "#F6D090", "#FFF8E0"], 3,
                       n=200, angle=-6, length=(40, 120), width=(3, 9), opacity=(0.15, 0.4), curve=0.15))
    out.append(specks(4, (0, 260, 600, 600), ["#C49A5A", "#FFFFFF", "#A87A44"], 300, (0.6, 1.6), (0.3, 0.7)))
    shore = [(-20, 262), (60, 276), (140, 266), (230, 284), (320, 272), (410, 290), (500, 278), (620, 292)]
    wet = shift(shore, 0, 26)
    out.append(f'<path d="{smooth_open(wet)} L 620 -20 L -20 -20 Z" fill="#E0B87A" opacity="0.6"/>')
    sd = smooth_open(shore) + " L 620 -20 L -20 -20 Z"
    out.append(f'<path d="{sd}" fill="{D.lin([(0, "#0E5E9A"), (0.45, "#1E9AC8"), (0.8, "#3FD0D0"), (1, "#9AF0E0")], 0, 0, 0, 300, "userSpaceOnUse")}"/>')
    out.append(strokes(D.nid(), sd, (-40, -20, 620, 300), ["#8EF0E0", "#0E5E8A", "#3FC8D8", "#FFFFFF"], 5, n=140, angle=-4, length=(40, 120), width=(2, 6), opacity=(0.12, 0.35)))
    # rolling lines of surf, the last one breaking on the sand
    for k, (dy, w, op) in enumerate(((-120, 3, 0.5), (-84, 3.5, 0.6), (-48, 4.5, 0.7), (-18, 6, 0.85))):
        line = [(x, y + dy + 6 * math.sin(x / 50 + k)) for x, y in catmull(shore, 4)]
        out.append(taper(line, w * 0.6, w, "#FFFFFF", op))
    out.append(taper([(x, y - 2) for x, y in catmull(shore, 4)], 9, 9, "#FFFFFF", 0.95))
    rnd = random.Random(6)
    for i in range(70):
        x = rnd.uniform(-10, 610)
        out.append(f'<circle cx="{x:.1f}" cy="{276 + 12 * math.sin(x / 70) + rnd.uniform(-14, 4):.1f}" r="{rnd.uniform(1.2, 3.2):.1f}" fill="#FFFFFF" opacity="0.85"/>')
    # a float and a swimmer's ring in the water
    out.append(swim_ring(D, 96, 222, 26, PINK, 7))
    out.append(swim_ring(D, 520, 236, 22, SUN, 8, CORAL))
    # towels & umbrellas on the sand
    out.append(towel_top(D, 150, 420, 70, 130, 18, ("#FFFFFF", TURQ[1]), 9))
    out.append(towel_top(D, 430, 470, 70, 130, -12, ("#FFFFFF", PINK[1]), 10))
    out.append(towel_top(D, 300, 520, 64, 120, 80, ("#FFFFFF", SUN[1]), 11))
    out.append(umbrella_top(D, 208, 378, 70, [CORAL, WHITE], 12))
    out.append(umbrella_top(D, 470, 400, 64, [TURQ, SUN], 13))
    out.append(umbrella_top(D, 330, 470, 52, [PINK, ("#FFF0F6", "#FFE0EE", "#C8A0B0")], 14, 6))
    out.append(beach_ball(D, 108, 520, 20, 15))
    out.append(starfish(D, 548, 538, 14, CORAL, 16, 20))
    # lettering over the sea
    out.append(letters(D, 300, 152, "beach", SERIF_IT, 124, "#FFFFFF", ["#FFFFFF", "#E0FFFA", "#C8F4F0"], 21, max_w=330,
                       shadow="#0A3A66", soff=(0.025, 0.04), angle=-35))
    out.append(letters(D, 300, 232, "DAYS", BEBAS, 96, "#FFD23A", ["#FFE27A", "#F2A800", "#FFF0B0"], 22, ls=24, max_w=280,
                       shadow="#0A3A66", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 54, "#8A5A3A", 0.6)


# ================================================================ 15. sea you soon — a sailboat seen through a brass porthole
def sailboat(D, cx, wl, s, seed, sail=WHITE, stripe=RED, hull=NAVY, heel=-6):
    """Sloop on the water line `wl`, sails filling from the left, heeling a little."""
    out = [f'<g transform="rotate({heel} {cx} {wl})">']
    mast_top = (cx, wl - s * 1.25)
    out.append(pline([(cx, wl - 6), mast_top], "#4A3A2A", max(2, s * 0.025), seed, 1, 1))
    main = [(cx + 4, wl - s * 1.2), (cx + 4 + s * 0.12, wl - s * 0.9), (cx + 4 + s * 0.42, wl - s * 0.3), (cx + 4 + s * 0.55, wl - s * 0.14), (cx + 4, wl - s * 0.14)]
    jib = [(cx - 4, wl - s * 1.12), (cx - 4, wl - s * 0.16), (cx - s * 0.6, wl - s * 0.16), (cx - s * 0.36, wl - s * 0.55)]
    out.append(painted(D, main, sail, seed + 1, sdir=(1, 0.2), sk=0.18, angle=-70, n=12, inkw=1.8, hi=0.4))
    out.append(painted(D, jib, sail, seed + 2, sdir=(-1, 0.2), sk=0.18, angle=-110, n=10, inkw=1.8, hi=0.3))
    cid = D.clip(f'<path d="{smooth_closed(main)}"/>')
    out.append(f'<g {cid}><path d="M {cx - 10} {wl - s * 0.48} L {cx + s * 0.6} {wl - s * 0.48} L {cx + s * 0.6} {wl - s * 0.36} L {cx - 10} {wl - s * 0.36} Z" fill="{stripe[1]}"/>'
               f'<path d="M {cx - 10} {wl - s * 0.3} L {cx + s * 0.6} {wl - s * 0.3} L {cx + s * 0.6} {wl - s * 0.24} L {cx - 10} {wl - s * 0.24} Z" fill="{stripe[1]}"/></g>')
    for k in range(3):
        y = wl - s * (0.5 + k * 0.2)
        out.append(pline([(cx + 6, y), (cx + s * 0.1 + (2 - k) * s * 0.08, y - s * 0.02)], sail[2], 1.2, seed + k, 0.5, 1))
    flag = [(cx, wl - s * 1.25), (cx - s * 0.16, wl - s * 1.21), (cx, wl - s * 1.17)]
    out.append(painted(D, flag, stripe, seed + 3, sk=0.1, n=2, inkw=1.2, hi=0.3))
    hullp = [(cx - s * 0.66, wl - s * 0.14), (cx + s * 0.7, wl - s * 0.14), (cx + s * 0.5, wl + s * 0.04), (cx - s * 0.5, wl + s * 0.04)]
    out.append(painted(D, hullp, hull, seed + 4, sdir=(0, 1), sk=0.15, angle=0, n=12, inkw=1.8, hi=0.3))
    out.append(taper([(cx - s * 0.62, wl - s * 0.1), (cx + s * 0.66, wl - s * 0.1)], 3, 3, "#FFFFFF", 0.85))
    out.append("</g>")
    # bow spray and wake
    out.append(taper([(cx - s * 0.62, wl + 2), (cx - s * 0.75, wl - s * 0.05), (cx - s * 0.8, wl - s * 0.02)], 5, 1, "#FFFFFF", 0.8))
    out.append(taper([(cx + s * 0.5, wl + 4), (cx + s * 0.9, wl + 6), (cx + s * 1.3, wl + 4)], 4, 1, "#FFFFFF", 0.7))
    out.append(taper([(cx + s * 0.3, wl + 8), (cx + s * 0.8, wl + 14), (cx + s * 1.2, wl + 12)], 3, 1, "#FFFFFF", 0.5))
    return "".join(out)


@design("sea-you-soon")
def sea_you_soon():
    D = Doc("sy")
    bg = "#1E4A9A"
    out = [f'<rect width="600" height="600" fill="{bg}"/>']
    out.append(stripes_in(D, "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (0, 0, 600, 600), 0, [44, 44], ["#2A5AAE", None], 3))
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, 0, 600, 600), ["#3A6AC0", "#14347A", "#4A7AD0"], 4, n=180,
                       angle=-86, length=(40, 140), width=(3, 9), opacity=(0.15, 0.35), curve=0.1))
    cx, cy, R, r = 300, 304, 160, 126
    out.append(soft_glow(D, cx, cy, 260, "#8EC8FF", 0.35))
    out.append(cast(D, cx + 12, cy + 16, R + 4, R + 4, color="#0A1A4A", strength=0.45))
    # the view: sky, sun, sea, a sloop
    win = blob(cx, cy, r, r, 3, 0.005, 30)
    cid = D.clip(f'<path d="{win}"/>')
    v = [f'<rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" fill="{D.lin([(0, "#7ED4F8"), (0.5, "#C8F0FF"), (0.62, "#FFF0C8")])}"/>']
    v.append(sun_disc(D, cx + 70, cy - 40, 30, SUN, 4, glow_col="#FFF6C0", glow_r=2.4))
    v.append(puff_cloud(D, cx - 70, cy - 54, 90, 5, ("#FFFFFF", "#FFFFFF", "#C8E0F0")))
    v.append(sea(D, cy + 14, cy + r + 10, [(0, "#2EB0D0"), (0.5, "#1E7AB8"), (1, "#14468A")], 6, ["#8EE8F4", "#0E3E7A", "#FFFFFF"], 50, ticks=["#FFFFFF", "#9AE8F4"]))
    v.append(sailboat(D, cx - 10, cy + 54, 120, 7, WHITE, RED, NAVY, -7))
    v.append(seagull(cx + 40, cy - 80, 9, "#2A3A5A") + seagull(cx + 62, cy - 92, 6, "#2A3A5A"))
    v.append(f'<path d="{blob(cx - 110, cy + 30, 28, 6, 8, 0.2, 10)}" fill="#3A8A5A" opacity="0.8"/>')
    out.append(f'<g {cid}>{"".join(v)}</g>')
    # glass glare
    out.append(f'<g {cid}>' + taper([(cx - r * 0.7, cy - r * 0.1), (cx - r * 0.45, cy - r * 0.55), (cx - r * 0.05, cy - r * 0.8)], 16, 3, "#FFFFFF", 0.35)
               + taper([(cx - r * 0.55, cy + r * 0.1), (cx - r * 0.38, cy - r * 0.2)], 8, 2, "#FFFFFF", 0.3) + '</g>')
    # brass ring with bolts
    ring = f'{blob(cx, cy, R, R, 9, 0.006, 30)} {win}'
    out.append(f'<path d="{ring}" fill-rule="evenodd" fill="{D.lin([(0, "#FFE9A0"), (0.4, "#E8B848"), (0.7, "#B8801E"), (1, "#7A4E0E")], 0, 0, 1, 1)}"/>')
    rcid = D.clip(f'<path d="{ring}" clip-rule="evenodd"/>')
    out.append(f'<g {rcid}>' + strokes(D.nid(), ring, (cx - R, cy - R, cx + R, cy + R), ["#FFF2C0", "#8A5A12", "#E8C060"], 10, n=120, angle=-45, length=(10, 30), width=(1, 3), opacity=(0.2, 0.5), curve=0.6) + '</g>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{(R + r) / 2 + 3}" fill="none" stroke="#FFF2C0" stroke-width="2" opacity="0.5"/>')
    out.append(ink(blob(cx, cy, R, R, 9, 0.006, 30), "#4A2E08", 2.6, 11, 2, 0.8) + ink(win, "#4A2E08", 2.2, 12, 2, 0.8))
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        bx, by = cx + (R + r) / 2 * math.cos(a), cy + (R + r) / 2 * math.sin(a)
        out.append(painted(D, blob_pts(bx, by, 7, 7, 20 + k, 0.03, 10), ("#FFF2C0", "#D8A838", "#6A4208"), 20 + k, sk=0.3, n=2, inkw=1.4, hi=0.6))
    # a rope looped around the porthole
    rp = [(cx + (R + 9) * math.cos(math.radians(a)), cy + (R + 9) * math.sin(math.radians(a))) for a in range(0, 361, 6)]
    out.append(taper(rp, 10, 10, "#E8D2A0"))
    rnd = random.Random(30)
    for i in range(0, len(rp) - 1):
        x, y = rp[i]
        out.append(pline([(x - 3, y - 3), (x + 3, y + 3)], "#9A7A44", 1.4, i, 0.7, 1))
    # lettering
    out.append(letters(D, 300, 110, "sea you", SERIF_IT, 92, "#FFFFFF", ["#FFFFFF", "#E0F0FF", "#C8E4FF"], 31, max_w=330,
                       shadow="#0A1A4A", soff=(0.025, 0.04), angle=-35))
    out.append(letters(D, 300, 546, "SOON", BEBAS, 84, "#FF6F59", ["#FF8A6A", "#E8463A", "#FFA890"], 32, ls=20, max_w=260,
                       shadow="#0A1A4A", angle=-78, hi="#FFE0D8"))
    return finish(D, out, 55, "#0A1A4A", 0.6)


# ================================================================ 16. coastal living — a striped lighthouse above the dunes
def lighthouse(D, cx, base, top, seed, w0=74, w1=44, bands=RED):
    out = []
    # tower
    tower = [(cx - w0 / 2, base), (cx - w1 / 2, top + 40), (cx + w1 / 2, top + 40), (cx + w0 / 2, base)]
    tp = poly_pts(tower, 20, seed, 0.6)
    td = smooth_closed(tp)
    out.append(f'<path d="{td}" fill="#FFFFFF"/>')
    cid = D.clip(f'<path d="{td}"/>')
    st = []
    H = base - (top + 40)
    for k in range(5):
        if k % 2 == 0:
            y0 = top + 40 + H * k / 5
            y1 = top + 40 + H * (k + 1) / 5
            st.append(f'<path d="M {cx - 60} {y0 + 6:.1f} Q {cx} {y0 + 14:.1f} {cx + 60} {y0 + 6:.1f} L {cx + 60} {y1 + 6:.1f} Q {cx} {y1 + 14:.1f} {cx - 60} {y1 + 6:.1f} Z" fill="{bands[1]}"/>')
    st.append(f'<path d="{td}" fill="{D.lin([(0, "#FFFFFF", 0.3), (0.35, "#FFFFFF", 0), (0.7, "#3A1A2A", 0.12), (1, "#3A1A2A", 0.4)], 0, 0, 1, 0)}"/>')
    out.append(f'<g {cid}>{"".join(st)}</g>')
    out.append(strokes(D.nid(), td, (cx - w0, top, cx + w0, base), ["#FFFFFF", "#000000", bands[0]], seed, n=60, angle=-90, length=(10, 30), width=(1, 3), opacity=(0.08, 0.2)))
    out.append(ink(td, INK, 2.2, seed, 2, 0.8))
    # door & window
    out.append(painted(D, [(cx - 9, base), (cx - 9, base - 26), (cx, base - 32), (cx + 9, base - 26), (cx + 9, base)], NAVY, seed + 1, sk=0.2, n=3, inkw=1.4, hi=0.3))
    out.append(painted(D, rect_pts(cx - 5, top + 110, cx + 5, top + 126, 6, seed, 0.3), ("#FFF6C0", "#FFD23A", "#C88A12"), seed + 2, sk=0.1, n=2, inkw=1.2, hi=0.3))
    # gallery, lantern room, dome
    gal = rect_pts(cx - w1 / 2 - 12, top + 32, cx + w1 / 2 + 12, top + 42, 10, seed, 0.4)
    out.append(painted(D, gal, NAVY, seed + 3, sk=0.2, n=3, inkw=1.6, hi=0.3))
    for k in range(7):
        x = cx - w1 / 2 - 8 + k * (w1 + 16) / 6
        out.append(pline([(x, top + 32), (x, top + 18)], NAVY[2], 1.6, k, 0.9, 1))
    out.append(pline([(cx - w1 / 2 - 10, top + 18), (cx + w1 / 2 + 10, top + 18)], NAVY[2], 2, seed, 0.9, 1))
    out.append(soft_glow(D, cx, top + 6, 90, "#FFF2A0", 0.85))
    lr = rect_pts(cx - w1 / 2 + 4, top - 6, cx + w1 / 2 - 4, top + 32, 8, seed, 0.3)
    out.append(painted(D, lr, ("#FFFCE0", "#FFE27A", "#E8A020"), seed + 4, sk=0.2, n=4, inkw=1.6, hi=0.5))
    out.append(pline([(cx - 4, top - 6), (cx - 4, top + 32)], NAVY[2], 1.6, seed, 0.8, 1) + pline([(cx + 8, top - 6), (cx + 8, top + 32)], NAVY[2], 1.6, seed + 1, 0.8, 1))
    dome = [(cx - w1 / 2, top - 4), (cx - w1 / 2 + 6, top - 18), (cx, top - 30), (cx + w1 / 2 - 6, top - 18), (cx + w1 / 2, top - 4)]
    out.append(painted(D, dome, bands, seed + 5, sdir=(1, 0.3), sk=0.2, angle=-30, n=4, inkw=1.8, hi=0.4))
    out.append(pline([(cx, top - 30), (cx, top - 42)], INK, 2.4, seed, 1, 1) + f'<circle cx="{cx}" cy="{top - 44}" r="3" fill="{INK}"/>')
    return "".join(out)


@design("coastal-living")
def coastal_living():
    D = Doc("cl")
    out = [sky(D, [(0, "#7ED8F4"), (0.4, "#BDEEF8"), (0.62, "#F2FAF0")], 3, 600, ["#FFFFFF", "#9AE0F4", "#D8F6FF"], 50)]
    # light beams from the lantern
    lx, ly = 452, 132
    for a0, a1 in ((-196, -184), (-172, -164)):
        out.append(f'<path d="M {lx} {ly} L {lx + 520 * math.cos(math.radians(a0)):.1f} {ly + 520 * math.sin(math.radians(a0)):.1f} L {lx + 520 * math.cos(math.radians(a1)):.1f} {ly + 520 * math.sin(math.radians(a1)):.1f} Z" fill="#FFF6C0" opacity="0.35"/>')
    out.append(puff_cloud(D, 140, 300, 110, 4, ("#FFFFFF", "#FFFFFF", "#C0E4F0")))
    out.append(seagull(270, 290, 12, "#3A4A6A") + seagull(296, 276, 8, "#3A4A6A") + seagull(546, 236, 9, "#3A4A6A"))
    out.append(sea(D, 352, 600, [(0, "#3FC8D0"), (0.4, "#1E9AC0"), (1, "#14609A")], 5, ["#9AF0EC", "#0E5E8A", "#FFFFFF"], 50, ticks=["#FFFFFF", "#B8F4F0"]))
    out.append(sailboat(D, 120, 366, 46, 6, WHITE, CORAL, CORAL, -4))
    # dunes
    d2 = ridge([(-20, 452), (120, 430), (240, 446), (360, 410), (470, 396), (620, 410)], 7, 8)
    out.append(hill(D, d2 + [(640, 420)], 620, ("#FFF4D8", "#F2D8A4", "#C8A070"), 7, angle=-6, inkw=1.6))
    out.append(lighthouse(D, 452, 420, 132, 8, 76, 46, CORAL))
    # keeper's cottage
    cot = rect_pts(492, 384, 566, 430, 14, 9, 0.6)
    out.append(painted(D, cot, ("#FFFFFF", "#F4F0E8", "#B8B0A6"), 9, sdir=(1, 0.3), sk=0.2, angle=-90, n=10, inkw=1.8, hi=0.3))
    out.append(painted(D, [(486, 388), (529, 356), (572, 388)], NAVY, 10, sdir=(1, 0.3), sk=0.15, angle=-20, n=8, inkw=1.8, hi=0.3))
    out.append(painted(D, rect_pts(504, 398, 520, 414, 6, 11, 0.3), ("#FFF6C0", "#FFD23A", "#C88A12"), 11, sk=0.1, n=2, inkw=1.2, hi=0.3))
    d1 = ridge([(-20, 500), (100, 476), (220, 492), (330, 520), (460, 500), (620, 476)], 12, 8)
    out.append(hill(D, d1, 620, ("#FFF6E0", "#F8E2B4", "#D0A878"), 12, angle=-4, inkw=1.8))
    rnd = random.Random(13)
    for i in range(70):
        x = rnd.uniform(-10, 610)
        base = 492 + 14 * math.sin(x / 90) + rnd.uniform(0, 60)
        h = rnd.uniform(26, 70)
        lean = rnd.uniform(-0.2, 0.6)
        out.append(taper([(x, base + 4), (x + lean * h * 0.4, base - h * 0.5), (x + lean * h, base - h)], 4, 0.6, rnd.choice(["#8AA040", "#B8C060", "#6A8030", "#D8D080", "#9AB050"]), 0.95))
    # weathered picket fence running through the dune
    for k in range(9):
        x = 60 + k * 30
        yb = 556 - k * 6
        hgt = 52 - k * 2.4
        pk = [(x - 6, yb), (x - 6.5, yb - hgt * 0.5), (x - 6, yb - hgt), (x - 3, yb - hgt - 4), (x, yb - hgt - 9), (x + 3, yb - hgt - 4), (x + 6, yb - hgt), (x + 6.5, yb - hgt * 0.5), (x + 6, yb)]
        out.append(f'<path d="M ' + " L ".join(f"{a:.1f} {b:.1f}" for a, b in jitter(pk, k, 0.5)) + f' Z" fill="#F6F0E6" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round" stroke-opacity="0.7"/>')
        out.append(pline([(x + 3, yb - 2), (x + 3, yb - hgt + 2)], "#A89A8A", 2.2, k, 0.6, 1) + pline([(x - 3, yb - 4), (x - 3, yb - hgt)], "#FFFFFF", 1.4, k, 0.8, 1))
    out.append(pline([(50, 532), (320, 486)], "#A89A8A", 3, 30, 0.9, 1) + pline([(50, 548), (320, 502)], "#A89A8A", 2.4, 31, 0.6, 1))
    out.append(starfish(D, 470, 560, 16, CORAL, 32, 10))
    # lettering, upper left
    out.append(letters(D, 210, 134, "coastal", SERIF_IT, 100, "#0E5E8A", ["#1E7EA0", "#0A3A5A", "#2E9AC0"], 41, max_w=290,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-35))
    out.append(letters(D, 206, 216, "LIVING", BEBAS, 104, "#FF6F59", ["#FF8A6A", "#E8463A", "#FFA890"], 42, ls=16, max_w=280,
                       shadow="#0E3E5E", angle=-78, hi="#FFE0D8"))
    return finish(D, out, 56)


# ================================================================ 17. float on — a flamingo float drifting in the pool
def caustics(D, d, box, seed, col="#FFFFFF", step=46, op=0.35, w=2.2):
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    cells = []
    y = y0 - step
    row = 0
    while y < y1 + step:
        x = x0 - step + (step / 2 if row % 2 else 0)
        while x < x1 + step:
            cells.append(f'<path d="{blob(x + rnd.uniform(-8, 8), y + rnd.uniform(-8, 8), step * 0.46, step * 0.36, rnd.randint(0, 9999), 0.22, 9, rnd.uniform(-30, 30))}"/>')
            x += step
        y += step * 0.78
        row += 1
    cid = D.clip(f'<path d="{d}"/>')
    return f'<g {cid}><g fill="none" stroke="{col}" stroke-width="{w}" opacity="{op}" stroke-linejoin="round">{"".join(cells)}</g></g>'


def flamingo_float(D, cx, cy, rx, ry, seed):
    pk = ("#FFB8D8", "#FF6FAE", "#C8306E")
    out = [f'<path d="{blob(cx + 30, cy + 46, rx, ry, seed, 0.03, 18)}" fill="#0A5A7A" opacity="0.3"/>']
    # ring (torus seen at an angle): outer blob minus inner hole
    outer = blob(cx, cy, rx, ry, seed + 1, 0.02, 22)
    hole = blob(cx + 6, cy - ry * 0.12, rx * 0.5, ry * 0.42, seed + 2, 0.03, 16)
    # water seen through the hole
    out.append(f'<path d="{outer} {hole}" fill-rule="evenodd" fill="{pk[1]}"/>')
    cid = D.clip(f'<path d="{outer} {hole}" clip-rule="evenodd"/>')
    sh = D.rad([(0.42, "#5A0A2A", 0.35), (0.55, "#FFFFFF", 0.3), (0.75, "#FFFFFF", 0), (1, "#5A0A2A", 0.4)], 0.5, 0.47, 0.55)
    out.append(f'<g {cid}><rect x="{cx - rx * 1.2:.1f}" y="{cy - ry * 1.4:.1f}" width="{rx * 2.4:.1f}" height="{ry * 2.8:.1f}" fill="{sh}"/>'
               + strokes(D.nid(), outer, (cx - rx, cy - ry, cx + rx, cy + ry), [pk[0], pk[2], "#FFFFFF"], seed, n=90, angle=0, length=(16, 46), width=(2, 5), opacity=(0.12, 0.35), curve=0.6)
               + "</g>")
    out.append(ink(outer, "#7A1240", 2.4, seed, 2, 0.75) + ink(hole, "#7A1240", 2, seed + 1, 1, 0.65))
    out.append(taper([(cx - rx * 0.8, cy + ry * 0.05), (cx - rx * 0.6, cy - ry * 0.6), (cx - rx * 0.2, cy - ry * 0.86)], 10, 2, "#FFFFFF", 0.65))
    # tail feathers at the back right
    tail = [(cx + rx * 0.7, cy - ry * 0.55), (cx + rx * 1.05, cy - ry * 1.05), (cx + rx * 1.12, cy - ry * 0.7), (cx + rx * 0.96, cy - ry * 0.35)]
    out.append(painted(D, tail, pk, seed + 3, sk=0.2, angle=-50, n=8, inkw=2, hi=0.4))
    # neck rising from the front left, curving back, head with a black-tipped beak
    neck = [(cx - rx * 0.62, cy + ry * 0.1), (cx - rx * 0.72, cy - ry * 0.7), (cx - rx * 0.5, cy - ry * 1.5), (cx - rx * 0.62, cy - ry * 2.05), (cx - rx * 0.86, cy - ry * 2.2)]
    path = catmull(neck, 6)
    out.append(taper(path, rx * 0.26, rx * 0.15, pk[2]))
    out.append(taper(path, rx * 0.22, rx * 0.12, pk[1]))
    out.append(taper([(x - rx * 0.04, y) for x, y in path], rx * 0.07, rx * 0.03, pk[0], 0.8))
    hx, hy = cx - rx * 0.76, cy - ry * 2.18
    out.append(painted(D, blob_pts(hx, hy, rx * 0.16, rx * 0.13, seed + 4, 0.04, 14), pk, seed + 4, sk=0.2, angle=-30, n=6, inkw=2, hi=0.5))
    beak = [(hx - rx * 0.12, hy - rx * 0.04), (hx - rx * 0.34, hy + rx * 0.04), (hx - rx * 0.38, hy + rx * 0.14), (hx - rx * 0.3, hy + rx * 0.1), (hx - rx * 0.12, hy + rx * 0.08)]
    out.append(painted(D, beak, ("#FFFFFF", "#FFF0E0", "#C8B8A8"), seed + 5, sk=0.2, n=3, inkw=1.8, hi=0.3))
    tipb = [(hx - rx * 0.27, hy + rx * 0.04), (hx - rx * 0.34, hy + rx * 0.04), (hx - rx * 0.38, hy + rx * 0.14), (hx - rx * 0.3, hy + rx * 0.1), (hx - rx * 0.26, hy + rx * 0.09)]
    out.append(f'<path d="{smooth_closed(tipb)}" fill="#1A1A22"/>')
    out.append(f'<circle cx="{hx - rx * 0.02:.1f}" cy="{hy - rx * 0.03:.1f}" r="{rx * 0.03:.1f}" fill="#1A1A22"/><circle cx="{hx - rx * 0.03:.1f}" cy="{hy - rx * 0.04:.1f}" r="{rx * 0.01:.1f}" fill="#FFFFFF"/>')
    # a wing on the side of the ring
    wing = [(cx + rx * 0.05, cy + ry * 0.62), (cx + rx * 0.35, cy + ry * 0.45), (cx + rx * 0.72, cy + ry * 0.4), (cx + rx * 0.62, cy + ry * 0.68), (cx + rx * 0.3, cy + ry * 0.8)]
    out.append(painted(D, wing, ("#FFD0E4", "#FF8AC0", "#C8306E"), seed + 6, sk=0.2, angle=-10, n=6, inkw=1.8, hi=0.4))
    for k in range(3):
        out.append(pline([(cx + rx * (0.2 + k * 0.15), cy + ry * (0.7 - k * 0.04)), (cx + rx * (0.32 + k * 0.15), cy + ry * (0.55 - k * 0.04))], pk[2], 1.4, k, 0.6, 1))
    return "".join(out)


@design("float-on")
def float_on():
    D = Doc("fo")
    pool = "M -10 120 L 610 120 L 610 610 L -10 610 Z"
    out = [f'<rect width="600" height="600" fill="#2EC8D8"/>']
    out.append(f'<path d="{pool}" fill="{D.lin([(0, "#1EA8C8"), (0.5, "#3FD4DC"), (1, "#7AE8E4")], 0.2, 0, 0.8, 1)}"/>')
    out.append(strokes(D.nid(), pool, (-60, 100, 600, 620), ["#8EF0EC", "#1E8AB0", "#B8FFF8"], 4, n=140, angle=-10, length=(40, 120), width=(3, 9), opacity=(0.12, 0.3), curve=0.3))
    out.append(caustics(D, pool, (0, 120, 600, 600), 5))
    out.append(caustics(D, pool, (10, 130, 600, 600), 6, "#E8FFFC", 64, 0.25, 1.6))
    # pool edge: blue tile band and stone coping across the top
    tile = "M -10 96 L 610 96 L 610 126 L -10 126 Z"
    out.append(f'<path d="{tile}" fill="#1E6EB8"/>')
    for x in range(-10, 610, 20):
        out.append(f'<path d="M {x} 96 L {x} 126" stroke="#8EC8F0" stroke-width="1.4" opacity="0.6"/>')
    out.append(f'<path d="M -10 111 L 610 111" stroke="#8EC8F0" stroke-width="1.4" opacity="0.6"/>')
    cop = poly_pts([(-10, -10), (610, -10), (610, 96), (-10, 96)], 30, 7, 0.6)
    out.append(painted(D, cop, ("#FFFCF4", "#F2E8D8", "#C0B098"), 7, sdir=(0, 1), sk=0.12, angle=0, n=60, inkw=0, hi=0.2, edge=False))
    for x in range(-10, 610, 74):
        out.append(pline([(x, -10), (x + 2, 96)], "#C0B098", 1.6, x, 0.6, 1))
    out.append(taper([(-10, 94), (300, 96), (610, 94)], 5, 5, "#8A7A66", 0.4))
    # ladder rails dipping into the pool
    for x in (520, 556):
        out.append(taper([(x, 60), (x, 110), (x - 2, 150), (x - 8, 170)], 9, 8, "#B8C8D0") + taper([(x - 2, 60), (x - 2, 110), (x - 4, 150)], 3, 2, "#FFFFFF", 0.8))
    for y in (140, 166):
        out.append(f'<path d="M 516 {y} L 552 {y}" stroke="#B8C8D0" stroke-width="5" stroke-linecap="round" opacity="0.7"/>')
    # floating lemon and a little beach ball
    out.append(f'<path d="{blob(110, 520, 26, 8, 8, 0.2, 10)}" fill="#0A5A7A" opacity="0.25"/>')
    out.append(beach_ball(D, 470, 520, 24, 9))
    out.append(flamingo_float(D, 300, 420, 150, 92, 10))
    out.append(swim_ring(D, 96, 470, 28, ("#FFF4A0", "#FFD23A", "#C88A12"), 11, ("#FFFFFF", "#FFFFFF", "#C8C0B8")))
    # ripples around the float
    for k, (rx_, ry_) in enumerate(((180, 110), (205, 128))):
        pts = [(300 + rx_ * math.cos(math.radians(a)), 430 + ry_ * math.sin(math.radians(a))) for a in range(-10, 200, 10)]
        out.append(taper(pts, 1, 3, "#FFFFFF", 0.45 - k * 0.15))
    # lettering
    out.append(letters(D, 420, 250, "float", SERIF_IT, 116, "#FFFFFF", ["#FFFFFF", "#E8FFFC", "#FFE8F2"], 31, max_w=260,
                       shadow="#0A4A7A", soff=(0.025, 0.04), angle=-35))
    out.append(letters(D, 420, 330, "ON", BEBAS, 96, "#FFD23A", ["#FFE27A", "#F2A800", "#FFF0B0"], 32, ls=22, max_w=160,
                       shadow="#0A4A7A", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 57, "#0A4A7A", 0.5)


# ================================================================ 18. golden hour — a beach cruiser on the boardwalk at sunset
def wheel_side(D, cx, cy, r, seed, tire="#2A2230", rim="#E8E4F0", spokes=18):
    out = []
    ring = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(0, 361, 10)]
    out.append(taper(ring, 10, 10, tire))
    out.append(taper([(cx + (r - 6) * math.cos(math.radians(a)), cy + (r - 6) * math.sin(math.radians(a))) for a in range(0, 361, 10)], 3, 3, rim))
    for k in range(spokes):
        a = math.radians(k * 360 / spokes)
        out.append(f'<path d="M {cx + 5 * math.cos(a):.1f} {cy + 5 * math.sin(a):.1f} L {cx + (r - 7) * math.cos(a + 0.2):.1f} {cy + (r - 7) * math.sin(a + 0.2):.1f}" stroke="{rim}" stroke-width="1.4" opacity="0.85"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{rim}" stroke="{INK}" stroke-width="1.6"/>')
    out.append(taper([(cx - r * 0.7, cy - r * 0.72), (cx - r * 0.2, cy - r * 0.98)], 3, 1, "#FFE0A0", 0.7))
    return "".join(out)


def tube(a, b, w, pal, bend=0.0):
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = b[0] - a[0], b[1] - a[1]
    m = (mx - dy * bend, my + dx * bend)
    pts = qpts(a, m, b, 8)
    return taper(pts, w + 3, w + 3, INK, 0.8) + taper(pts, w, w, pal[1]) + taper([(x, y - w * 0.25) for x, y in pts], w * 0.3, w * 0.3, pal[0], 0.8)


@design("golden-hour")
def golden_hour():
    D = Doc("gh")
    out = [sky(D, [(0, "#FF8A5A"), (0.3, "#FFB45A"), (0.55, "#FFD86A"), (0.66, "#FFF0B0")], 3, 410, ["#FFE0A0", "#FF9A6A", "#FFF4C8", "#FF7A6A"], 70)]
    out.append(soft_glow(D, 300, 392, 300, "#FFF4C0", 0.9))
    out.append(sun_disc(D, 300, 392, 80, ("#FFFCE0", "#FFE87A", "#FFB43A"), 4, glow_r=0.01, strokes_n=20))
    out.append(puff_cloud(D, 120, 300, 150, 5, ("#FFE0B8", "#FF9A7A", "#C85A6A"), op=0.9))
    out.append(puff_cloud(D, 500, 270, 140, 6, ("#FFE0B8", "#FF9A7A", "#C85A6A"), op=0.9))
    out.append(seagull(400, 300, 10, "#7A3A4A") + seagull(424, 288, 7, "#7A3A4A"))
    out.append(sea(D, 392, 440, [(0, "#FFB47A"), (0.4, "#4AB8C8"), (1, "#1E7AA8")], 5, ["#FFE0A0", "#1E7AA8", "#FFFFFF"], 40))
    rnd = random.Random(6)
    for i in range(16):
        t = i / 15
        y = 396 + t * 40
        hw = 70 * (1 - t * 0.4) * rnd.uniform(0.4, 1)
        out.append(taper([(300 - hw, y), (300, y - 1), (300 + hw, y)], 1, 3, rnd.choice(["#FFF4B0", "#FFD86A"]), 0.8))
    # boardwalk planks
    bw = "M -10 440 L 610 440 L 610 610 L -10 610 Z"
    out.append(f'<path d="{bw}" fill="#C88A54"/>')
    out.append(f'<path d="{bw}" fill="{D.lin([(0, "#FFC88A", 0.6), (1, "#7A4A2A", 0.4)], 0, 440, 0, 610, "userSpaceOnUse")}"/>')
    y = 446
    k = 0
    while y < 610:
        hgt = 10 + k * 4
        out.append(pline([(-10, y), (300, y + 1), (610, y)], "#6A3E1E", 1.6 + k * 0.3, k, 0.6, 1))
        for x in range(-10 + (k % 2) * 40, 610, 120 + k * 10):
            out.append(pline([(x, y), (x, y + hgt)], "#6A3E1E", 1.2, x, 0.5, 1))
        y += hgt
        k += 1
    out.append(strokes(D.nid(), bw, (-60, 440, 610, 610), ["#FFD8A0", "#8A5A2A", "#E8A870"], 7, n=120, angle=0, length=(30, 90), width=(1.5, 4), opacity=(0.15, 0.35)))
    # railing posts and rope
    for x in (40, 560):
        out.append(painted(D, rect_pts(x - 8, 360, x + 8, 470, 14, x, 0.5), WOOD, x, sdir=(1, 0), sk=0.2, angle=-90, n=8, inkw=1.8, hi=0.3))
    out.append(taper(catmull([(40, 374), (300, 398), (560, 374)], 10), 5, 5, "#E8D2A0") + pline(catmull([(40, 374), (300, 398), (560, 374)], 10), INK, 1.2, 8, 0.4, 1))
    # sea oats at the sides
    for i in range(18):
        x = rnd.choice([rnd.uniform(0, 70), rnd.uniform(530, 600)])
        h = rnd.uniform(50, 110)
        lean = rnd.uniform(-0.3, 0.3)
        tip = (x + lean * h, 440 - h)
        out.append(taper([(x, 444), (x + lean * h * 0.4, 440 - h * 0.5), tip], 3, 0.8, rnd.choice(["#8A7A3A", "#B8A050", "#6A5A2A"])))
        if i % 3 == 0:
            for j in range(5):
                out.append(f'<path d="{blob(tip[0] + j * 2 * lean, tip[1] + j * 7, 2.6, 5, i * 9 + j, 0.1, 8, 20)}" fill="#C8A050"/>')
    # long evening shadow of the bike
    out.append(f'<path d="{blob(220, 534, 200, 12, 9, 0.08, 16)}" fill="#5A2A1A" opacity="0.3"/>')
    mint = ("#B8FFF0", "#3FD0B8", "#1E7A6E")
    R, F, r = (196, 470), (414, 470), 62
    out.append(wheel_side(D, *R, r, 10) + wheel_side(D, *F, r, 11))
    B = (292, 478)
    S = (262, 372)
    Hb, Ht = (392, 392), (382, 352)
    out.append(tube(B, R, 7, mint) + tube((262, 380), R, 6, mint))
    out.append(tube(B, S, 9, mint))
    out.append(tube(B, Hb, 10, mint, -0.12) + tube((270, 404), (388, 380), 8, mint, -0.1))
    out.append(tube(Ht, Hb, 11, mint))
    out.append(tube(Hb, F, 7, mint, 0.04))
    # fenders
    for (cx_, cy_), a0, a1 in ((R, 190, 330), (F, 205, 345)):
        pts = [(cx_ + (r + 9) * math.cos(math.radians(a)), cy_ + (r + 9) * math.sin(math.radians(a))) for a in range(a0, a1 + 1, 8)]
        out.append(taper(pts, 12, 12, INK, 0.8) + taper(pts, 9, 9, mint[1]) + taper([(x, y - 2) for x, y in pts], 3, 3, mint[0], 0.8))
    # chainring, pedal, chain
    out.append(f'<circle cx="{B[0]}" cy="{B[1]}" r="16" fill="#D8D4E0" stroke="{INK}" stroke-width="2"/><circle cx="{B[0]}" cy="{B[1]}" r="6" fill="#8A8494"/>')
    out.append(pline([(B[0], B[1] - 16), (R[0], R[1] - 8)], "#5A5464", 2.4, 3, 0.8, 1) + pline([(B[0], B[1] + 16), (R[0], R[1] + 8)], "#5A5464", 2.4, 4, 0.8, 1))
    out.append(pline([B, (B[0] + 18, B[1] + 22)], "#5A5464", 4, 5, 1, 1) + f'<path d="M {B[0] + 8} {B[1] + 24} L {B[0] + 30} {B[1] + 21}" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>')
    # saddle
    sad = [(236, 360), (250, 350), (284, 352), (292, 360), (276, 368), (246, 368)]
    out.append(painted(D, sad, ("#C88A5A", "#8A4A2A", "#4A2410"), 12, sk=0.2, n=4, inkw=1.8, hi=0.4))
    # handlebar & basket with flowers
    out.append(pline([Ht, (378, 332), (352, 324), (338, 330)], "#C8C4D0", 5, 13, 1, 1) + pline([Ht, (378, 332), (352, 324), (338, 330)], INK, 1.2, 14, 0.5, 1))
    out.append(taper([(338, 330), (326, 334)], 8, 8, "#8A4A2A"))
    bk = [(392, 318), (468, 316), (462, 376), (400, 378)]
    out.append(painted(D, poly_pts(bk, 14, 15, 0.6), ("#F6D08A", "#D8A050", "#8A5A22"), 15, sk=0.15, angle=0, n=10, inkw=2, hi=0.3))
    cid = D.clip(f'<path d="{smooth_closed(poly_pts(bk, 14, 15, 0.6))}"/>')
    weave = "".join(f'<path d="M 390 {y} Q 430 {y + 3} 470 {y}" stroke="#8A5A22" stroke-width="1.6" fill="none" opacity="0.7"/>' for y in range(324, 378, 9))
    weave += "".join(f'<path d="M {x} 314 L {x - 2} 380" stroke="#FFF0C0" stroke-width="1.4" opacity="0.6"/>' for x in range(398, 470, 11))
    out.append(f'<g {cid}>{weave}</g>')
    out.append(leaf(D, "slim", 400, 306, 16, LEAF, -60, 16, vein="#C8F0A0") + leaf(D, "slim", 466, 304, 16, LEAF, 60, 17, vein="#C8F0A0"))
    for i, (x, y, r_, pal) in enumerate(((412, 300, 16, PINK), (440, 292, 18, ("#FFFFFF", "#FFFFFF", "#D8C8C8")), (464, 306, 14, CORAL), (426, 316, 12, SUN))):
        if pal[0] == "#FFFFFF":
            out.append(daisy(D, x, y, r_, 20 + i, n=10))
        else:
            out.append(hibiscus(D, x, y, r_, pal, 20 + i, i * 30, inkw=1.2))
    out.append(pline([(392, 318), (384, 340)], INK, 2, 18, 0.8, 1))
    # lettering
    out.append(letters(D, 300, 146, "golden", SERIF_IT, 108, "#8A1E3A", ["#A82E4A", "#6A0E2A", "#C84A5A"], 31, max_w=380,
                       shadow="#FFF0C8", soff=(-0.02, -0.025), angle=-35))
    out.append(letters(D, 300, 228, "HOUR", BEBAS, 100, "#FFFFFF", ["#FFFFFF", "#FFF4D8", "#FFE8C0"], 32, ls=30, max_w=300,
                       shadow="#B84A3A", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 58, "#5A2A1A", 0.6)


# ================================================================ 19. shell yeah! — a sand pail brimming with shells
def conch(D, cx, cy, s, seed, rot_=0, pal=("#FFE8D8", "#F6C0A0", "#C07A5A"), lip=("#FFD0D8", "#FF9AB0", "#C0506A")):
    """Spiral shell: stacked whorls narrowing to a point, a flared pink lip."""
    out = [f'<g transform="rotate({rot_} {cx} {cy})">']
    body = [(cx - 0.5 * s, cy - 0.05 * s), (cx - 0.1 * s, cy - 0.5 * s), (cx + 0.55 * s, cy - 0.32 * s), (cx + 1.0 * s, cy - 0.02 * s),
            (cx + 0.55 * s, cy + 0.32 * s), (cx - 0.1 * s, cy + 0.42 * s)]
    out.append(painted(D, body, pal, seed, sdir=(0.3, 1), sk=0.2, angle=0, n=12, inkw=1.8, hi=0.45))
    for k in range(4):
        x = cx + 0.3 * s + k * 0.17 * s
        h = 0.3 * s * (1 - k * 0.2)
        out.append(pline([(x, cy - h), (x + 0.06 * s, cy), (x, cy + h)], pal[2], max(1.2, s * 0.04), seed + k, 0.7, 1))
    lp = [(cx - 0.62 * s, cy - 0.02 * s), (cx - 0.3 * s, cy - 0.42 * s), (cx + 0.1 * s, cy - 0.3 * s), (cx + 0.1 * s, cy + 0.25 * s), (cx - 0.3 * s, cy + 0.4 * s)]
    out.append(painted(D, lp, lip, seed + 5, sdir=(0.3, 1), sk=0.2, angle=-20, n=8, inkw=1.8, hi=0.5))
    out.append(f'<path d="{blob(cx - 0.22 * s, cy, 0.18 * s, 0.24 * s, seed, 0.1, 10)}" fill="{lip[2]}" opacity="0.55"/>')
    for k in range(3):
        a = -0.4 + k * 0.4
        out.append(f'<path d="M {cx - 0.05 * s:.1f} {cy - 0.4 * s + k * 0.08 * s:.1f} l {0.05 * s:.1f} {-0.1 * s:.1f}" stroke="{pal[2]}" stroke-width="{max(1.4, s * 0.05):.1f}" stroke-linecap="round"/>')
    out.append("</g>")
    return "".join(out)


def sand_dollar(D, cx, cy, r, seed):
    out = [painted(D, blob_pts(cx, cy, r, r * 0.97, seed, 0.02, 18), ("#FFFCF0", "#F2E6CC", "#B8A27A"), seed, sk=0.15, n=8, inkw=1.6, hi=0.4)]
    for k in range(5):
        a = math.radians(-90 + k * 72)
        px, py = cx + r * 0.38 * math.cos(a), cy + r * 0.38 * math.sin(a)
        out.append(f'<path d="{blob(px, py, r * 0.08, r * 0.24, seed + k, 0.05, 10, math.degrees(a) + 90)}" fill="none" stroke="#B8A27A" stroke-width="{max(1.2, r * 0.06):.1f}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.06:.1f}" fill="#B8A27A"/>')
    return "".join(out)


@design("shell-yeah")
def shell_yeah():
    D = Doc("sh")
    out = [paper(D.nid(), "#FFE4D2", "#C08060", 11)]
    out.append(blooms(3, ["#FFB8A0", "#FFD8B8", "#FF9AB0"], 7, (0, 0, 600, 600), (90, 160), (0.1, 0.18)))
    # a scatter of tiny painted shells as a pattern
    rnd = random.Random(4)
    for i in range(18):
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 580)
        if 120 < x < 480 and 150 < y < 560:
            continue
        out.append(f'<g opacity="0.35">{scallop(D, x, y, rnd.uniform(9, 13), ("#FFFFFF", "#FFC8B8", "#E08A7A"), 100 + i, rnd.uniform(-40, 40))}</g>')
    # sand mound
    md = smooth_closed([(-20, 620), (-20, 520), (120, 486), (300, 470), (480, 486), (620, 520), (620, 620)])
    out.append(f'<path d="{md}" fill="#F6D9A0"/>')
    out.append(strokes(D.nid(), md, (-20, 460, 620, 620), ["#FFF0CE", "#C9A066", "#E8C48A"], 5, n=90, angle=-5, length=(20, 70), width=(2, 6), opacity=(0.2, 0.5)))
    out.append(specks(6, (0, 480, 600, 600), ["#C49A5A", "#FFFFFF", "#A87A44"], 120, (0.6, 1.6), (0.3, 0.7)))
    out.append(ink(smooth_open([(-20, 520), (120, 486), (300, 470), (480, 486), (620, 520)]), INK, 2, 7, 1, 0.5))
    # the pail
    cx, top, bot = 290, 280, 504
    out.append(cast(D, cx + 30, bot + 4, 150, 16, strength=0.35))
    pail = [(cx - 120, top), (cx + 120, top), (cx + 92, bot - 8), (cx + 60, bot + 4), (cx - 60, bot + 4), (cx - 92, bot - 8)]
    pp = poly_pts(pail, 20, 8, 0.7)
    out.append(painted(D, pp, TURQ, 8, sdir=(0.7, 0.3), sk=0.16, angle=-90, n=80, slen=(20, 60), sw=(2, 5), inkw=2.4, hi=0.4))
    # a band of painted waves around the pail and a starfish decal
    cid = D.clip(f'<path d="{smooth_closed(pp)}"/>')
    wv = taper([(x, 400 + 10 * math.sin(x / 18)) for x in range(cx - 130, cx + 140, 10)], 8, 8, "#FFFFFF", 0.9)
    wv += taper([(x, 424 + 8 * math.sin(x / 18 + 2)) for x in range(cx - 130, cx + 140, 10)], 5, 5, SUN[1], 0.95)
    out.append(f'<g {cid}>{wv}</g>')
    out.append(starfish(D, cx + 10, 360, 26, CORAL, 9, 6))
    # rim
    rim = [(cx - 126, top - 6), (cx + 126, top - 6), (cx + 128, top + 12), (cx - 128, top + 12)]
    out.append(painted(D, poly_pts(rim, 16, 10, 0.5), ("#B8FFF4", "#5AE0D8", "#1E8A8A"), 10, sk=0.2, angle=0, n=20, inkw=2.2, hi=0.5))
    # shells heaped over the top
    heap = [((cx - 70, top - 10), "scallop", 34, ("#FFFFFF", "#FFC8B8", "#D07A6A"), -20), ((cx + 70, top - 12), "scallop", 30, ("#FFF6E0", "#FFD890", "#C8904A"), 25),
            ((cx - 10, top - 28), "conch", 52, None, -18), ((cx + 30, top - 6), "dollar", 26, None, 0), ((cx - 100, top + 4), "scallop", 24, ("#F0E8FF", "#C8B0F0", "#7A5AB0"), -50)]
    for i, ((x, y), kind, s_, pal, r_) in enumerate(heap):
        if kind == "scallop":
            out.append(scallop(D, x, y, s_, pal, 20 + i, r_))
        elif kind == "conch":
            out.append(conch(D, x, y, s_, 20 + i, r_))
        else:
            out.append(sand_dollar(D, x, y, s_, 20 + i))
    # handle
    hp = [(cx - 118, top + 18), (cx - 146, top - 28), (cx, top - 50), (cx + 146, top - 28), (cx + 118, top + 18)]
    out.append(taper(catmull(hp, 8), 9, 9, INK, 0.8) + taper(catmull(hp, 8), 6, 6, SUN[1]) + taper(catmull(hp[1:4], 8), 2, 2, SUN[0], 0.9))
    for sg in (-1, 1):
        out.append(painted(D, blob_pts(cx + sg * 118, top + 20, 9, 9, 30 + sg, 0.05, 10), SUN, 30 + sg, sk=0.2, n=2, inkw=1.6, hi=0.5))
    # shovel stuck in the sand
    sh = [(452, 506), (470, 446), (496, 432), (514, 446), (506, 476), (478, 516)]
    out.append(f'<g transform="rotate(14 480 480)">')
    out.append(painted(D, rect_pts(486, 300, 498, 450, 14, 31, 0.4), CORAL, 31, sdir=(1, 0), sk=0.25, angle=-90, n=6, inkw=1.8, hi=0.4))
    out.append(painted(D, blob_pts(492, 296, 16, 10, 32, 0.05, 12), CORAL, 32, sk=0.2, n=3, inkw=1.8, hi=0.4))
    blade = [(462, 450), (522, 450), (520, 500), (492, 526), (464, 500)]
    out.append(painted(D, blade, CORAL, 33, sdir=(0.6, 0.6), sk=0.15, angle=-80, n=10, inkw=2, hi=0.5))
    out.append("</g>")
    out.append(f'<path d="{blob(486, 520, 50, 10, 34, 0.1, 12)}" fill="#F6D9A0"/>')
    out.append(scallop(D, 110, 520, 20, ("#FFFFFF", "#FFC8D8", "#D07A8A"), 35, 18) + starfish(D, 190, 548, 15, SUN, 36, 20))
    # lettering
    out.append(letters(D, 300, 140, "shell", SERIF_IT, 100, "#E8337E", ["#FF6FAA", "#C21E66", "#FF8AB8"], 41, max_w=260,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-35, rot=-4))
    out.append(letters(D, 300, 214, "YEAH!", BEBAS, 92, "#1FB5B0", ["#3FD0C8", "#0E7E7A", "#8EF0E8"], 42, ls=18, max_w=260,
                       shadow="#0A4E4E", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 59)


# ================================================================ 20. ice cream social — a pastel ice cream truck
@design("ice-cream-social")
def ice_cream_social():
    D = Doc("ic")
    out = [sky(D, [(0, "#C8A8F0"), (0.4, "#F2B8DC"), (0.75, "#FFE0C8")], 3, 600, ["#E8C8FF", "#FFC8E0", "#FFF0E0"], 60)]
    out.append(puff_cloud(D, 90, 260, 120, 4, ("#FFFFFF", "#FFF4FA", "#E0B8E0")))
    out.append(puff_cloud(D, 520, 240, 130, 5, ("#FFFFFF", "#FFF4FA", "#E0B8E0")))
    # park: hedge and lawn, string of bunting
    gl = ridge([(-20, 452), (200, 446), (420, 452), (620, 444)], 6, 4)
    out.append(hill(D, gl, 620, ("#C8F0A0", "#7ACB6A", "#3A8A4A"), 6, angle=-4, inkw=1.4))
    for i, x in enumerate(range(-20, 640, 46)):
        out.append(dab_crown(D, x, 446, 30, 22, [("#9ADB6A", "#4AAA4A", "#1E6A34"), ("#B8E07A", "#6ABA4A", "#2E7A34")], 70 + i, 26, (5, 9), inkw=0))
    out.append(f'<rect x="-10" y="470" width="620" height="140" fill="#9AA0B0"/>')
    out.append(strokes(D.nid(), "M -10 470 L 610 470 L 610 610 L -10 610 Z", (-60, 470, 610, 610), ["#B8BEC8", "#7A8090", "#C8CCD8"], 7, n=80, angle=0, length=(30, 90), width=(2, 5), opacity=(0.2, 0.4)))
    out.append(taper([(-10, 472), (610, 472)], 6, 6, "#E8ECF0"))
    out.append(cast(D, 300, 512, 250, 16, color="#3A2A4A", strength=0.4))
    # truck body (faces right)
    body = poly_pts([(78, 250), (420, 250), (430, 262), (430, 492), (78, 492), (70, 480), (70, 262)], 24, 8, 0.7)
    mint = ("#D8FFF4", "#9AEFD8", "#3AA890")
    out.append(painted(D, body, mint, 8, sdir=(0.4, 1), sk=0.1, angle=-90, n=80, inkw=2.4, hi=0.35))
    cab = poly_pts([(424, 300), (484, 300), (520, 360), (532, 372), (532, 492), (424, 492)], 20, 9, 0.6)
    out.append(painted(D, cab, mint, 9, sdir=(0.4, 1), sk=0.1, angle=-90, n=30, inkw=2.4, hi=0.35))
    out.append(painted(D, poly_pts([(434, 312), (480, 312), (510, 362), (434, 362)], 14, 10, 0.4), ("#FFFFFF", "#C8ECF8", "#6AA8C8"), 10, sdir=(1, 0.5), sk=0.2, angle=-50, n=8, inkw=2, hi=0.5))
    out.append(taper([(446, 354), (466, 318)], 6, 3, "#FFFFFF", 0.7))
    # pink skirt stripe & scallops along the bottom of the body
    sk_ = poly_pts([(70, 430), (532, 430), (532, 462), (70, 462)], 24, 11, 0.4)
    out.append(painted(D, sk_, PINK, 11, sk=0.1, angle=0, n=30, inkw=1.6, hi=0.3))
    for x in range(78, 420, 34):
        out.append(f'<circle cx="{x + 17}" cy="446" r="5" fill="#FFFFFF" opacity="0.85"/>')
    # serving window with an awning
    win = poly_pts([(118, 300), (330, 300), (330, 398), (118, 398)], 20, 12, 0.5)
    out.append(painted(D, win, ("#FFF4FA", "#FFE0EE", "#C8A0B8"), 12, sk=0.12, angle=0, n=10, inkw=2.2, hi=0.3))
    # menu & treats inside the window
    for i, (x, pal) in enumerate(((150, PINK), (196, SUN), (242, MINT))):
        out.append(painted(D, [(x - 12, 390), (x + 12, 390), (x + 4, 330), (x - 4, 330)], ("#F6CE84", "#E0A050", "#9A6024"), 13 + i, sk=0.15, n=3, inkw=1.4, hi=0.3))
        out.append(painted(D, blob_pts(x, 330, 16, 14, 16 + i, 0.06, 12), pal, 16 + i, sk=0.2, n=4, inkw=1.4, hi=0.5))
    out.append(painted(D, poly_pts([(270, 314), (318, 314), (318, 386), (270, 386)], 12, 19, 0.4), ("#4A4A5A", "#2A2A36", "#0A0A10"), 19, sk=0.1, n=4, inkw=1.6, hi=0.2))
    for k in range(4):
        out.append(pline([(278, 330 + k * 15), (310, 330 + k * 15)], "#FFFFFF", 1.6, k, 0.7, 1))
    out.append(painted(D, poly_pts([(110, 398), (338, 398), (338, 410), (110, 410)], 16, 20, 0.4), ("#FFFFFF", "#F4ECF0", "#B8A8B0"), 20, sk=0.2, n=4, inkw=1.6, hi=0.3))
    aw_top, aw_bot = 276, 300
    awd = smooth_closed(poly_pts([(104, aw_bot), (112, aw_top), (336, aw_top), (344, aw_bot)], 20, 21, 0.4))
    out.append(f'<path d="{awd}" fill="#FFFFFF"/>' + stripes_in(D, awd, (90, 260, 360, 320), 0, [28, 28], [PINK[1], None], 22) + ink(awd, INK, 1.8, 22, 1, 0.7))
    for k in range(8):
        x0 = 104 + k * 30
        col = PINK if k % 2 == 0 else WHITE
        out.append(painted(D, [(x0, aw_bot - 2)] + [(x0 + 15 + 15 * math.cos(math.radians(a)), aw_bot - 2 + 13 * math.sin(math.radians(a))) for a in range(0, 181, 30)] + [(x0 + 30, aw_bot - 2)],
                           col, 23 + k, sk=0.2, n=2, inkw=1.4, inkop=0.6, hi=0.3))
    # a giant cone sign on the roof
    out.append(painted(D, poly_pts([(98, 252), (122, 252), (122, 238), (98, 238)], 8, 30, 0.3), ("#E8E4F0", "#B8B4C8", "#6A667A"), 30, sk=0.2, n=2, inkw=1.6, hi=0.3))
    out.append(painted(D, [(88, 214), (132, 214), (110, 250)], ("#F6CE84", "#E0A050", "#9A6024"), 31, sk=0.15, angle=-80, n=6, inkw=2, hi=0.3))
    out.append(scoop(D, 110, 212, 26, PINK, 32, drips=2))
    out.append(f'<circle cx="110" cy="182" r="6" fill="{RED[1]}" stroke="{INK}" stroke-width="1.4"/>')
    # wheels
    for x in (156, 452):
        out.append(painted(D, blob_pts(x, 492, 40, 40, x, 0.01, 18), ("#5A5466", "#2A2430", "#0A080E"), x, sk=0.15, n=8, inkw=2, hi=0.2))
        out.append(painted(D, blob_pts(x, 492, 20, 20, x + 1, 0.02, 14), ("#FFFFFF", "#E8E4F0", "#A8A4B8"), x + 1, sk=0.2, n=3, inkw=1.6, hi=0.5))
        out.append(f'<circle cx="{x}" cy="492" r="6" fill="{PINK[1]}"/>')
    # headlight, bumper, door line
    out.append(f'<circle cx="526" cy="404" r="9" fill="#FFF6C0" stroke="{INK}" stroke-width="1.8"/>' + soft_glow(D, 530, 404, 26, "#FFF6C0", 0.6))
    out.append(taper([(420, 482), (540, 482)], 10, 10, "#E8E4F0") + pline([(420, 482), (540, 482)], INK, 1.4, 40, 0.5, 1))
    out.append(pline([(440, 372), (440, 470)], mint[2], 1.8, 41, 0.6, 1) + pline([(452, 392), (466, 392)], INK, 3, 42, 0.8, 1))
    # bunting across the top of the body
    pts = catmull([(78, 256), (250, 270), (420, 256)], 10)
    for k in range(1, len(pts) - 1, 2):
        x, y = pts[k]
        c = [PINK, SUN, TURQ, CORAL][(k // 2) % 4]
        out.append(painted(D, [(x - 8, y), (x + 8, y), (x, y + 16)], c, 50 + k, sk=0.1, n=1, inkw=1.2, hi=0.3))
    out.append(pline(pts, INK, 1.2, 51, 0.6, 1))
    # lettering
    out.append(letters(D, 300, 128, "ice cream", SERIF_IT, 98, "#7A2A8A", ["#9A3AAA", "#5A1A6A", "#B85AC0"], 61, max_w=420,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-35))
    out.append(letters(D, 300, 200, "SOCIAL", BEBAS, 84, "#FF5FA2", ["#FF8AC0", "#D83A80", "#FFB0D0"], 62, ls=16, max_w=280,
                       shadow="#5A1A6A", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 60, "#3A2A4A", 0.6)


# ================================================================ 21. happy camper — a glowing tent under the stars
def pine_sil(x, base, h, col, seed, w=0.36):
    rnd = random.Random(seed)
    pts = [(x, base - h)]
    tiers = 7
    for i in range(1, tiers + 1):
        t = i / tiers
        y = base - h + h * t * 0.92
        ww = h * w * t * rnd.uniform(0.85, 1.1) / 2
        pts.append((x + ww, y))
        if i < tiers:
            pts.append((x + ww * 0.45, y - h * 0.02))
    left = [(2 * x - px, py) for px, py in pts[1:][::-1]]
    poly = pts + [(x + h * 0.03, base), (x - h * 0.03, base)] + left
    return f'<path d="M ' + " L ".join(f"{a:.1f} {b:.1f}" for a, b in jitter(poly, seed, 1.2)) + f' Z" fill="{col}"/>'


def flame(D, cx, base, h, seed):
    out = [soft_glow(D, cx, base - h * 0.3, h * 2.6, "#FFB84A", 0.75)]
    for k, (sc, col) in enumerate(((1.0, "#FF5A2A"), (0.75, "#FF9A2A"), (0.5, "#FFD84A"), (0.28, "#FFF6C0"))):
        hh = h * sc
        ww = h * 0.42 * sc
        pts = [(cx - ww, base), (cx - ww * 0.9, base - hh * 0.4), (cx - ww * 0.3, base - hh * 0.75), (cx + ww * 0.1, base - hh * 1.0), (cx + ww * 0.15, base - hh * 0.7),
               (cx + ww * 0.6, base - hh * 0.85), (cx + ww * 0.9, base - hh * 0.4), (cx + ww, base)]
        out.append(f'<path d="{smooth_closed(jitter(pts, seed + k, 1))}" fill="{col}"/>')
    return "".join(out)


@design("happy-camper")
def happy_camper():
    D = Doc("hc")
    out = [sky(D, [(0, "#14164A"), (0.45, "#3A2A7A"), (0.72, "#8A3A8A"), (0.82, "#E86A7A")], 3, 470, ["#2A2A6A", "#5A3A9A", "#1A1A5A"], 70)]
    # milky way and stars
    out.append(f'<path d="{blob(330, 170, 320, 50, 4, 0.2, 18, -24)}" fill="#C8A8FF" opacity="0.12"/>')
    out.append(specks(5, (0, 0, 600, 380), ["#FFFFFF", "#FFF4C0", "#C8D8FF"], 160, (0.6, 1.8), (0.4, 1)))
    for x, y, r_ in ((90, 230, 9), (520, 220, 11), (440, 300, 7), (150, 330, 6), (560, 330, 6), (60, 120, 7)):
        out.append(sparkle(x, y, r_, "#FFF6C0"))
    out.append(soft_glow(D, 500, 260, 60, "#FFF6D8", 0.4) + f'<path d="M 498 238 A 24 24 0 1 0 520 276 A 19 19 0 1 1 498 238 Z" fill="#FFF6D8"/>')
    # mountains and pines
    l1 = ridge([(-20, 400), (100, 330), (190, 380), (300, 320), (420, 386), (520, 340), (620, 390)], 3, 14)
    out.append(hill(D, l1, 620, ("#6A4A9A", "#4A3A7A", "#2A1E4A"), 3, angle=-30, inkw=0))
    for i, x in enumerate(range(-20, 640, 26)):
        out.append(pine_sil(x, 470 + (i % 3) * 4, 60 + (i * 37 % 40), "#1E2A4A", 10 + i))
    for i, (x, h) in enumerate(((30, 230), (86, 170), (560, 240), (510, 160))):
        out.append(pine_sil(x, 560, h, "#14203A", 30 + i, 0.4))
    # ground
    gd = smooth_closed([(-20, 470), (200, 462), (400, 468), (620, 460), (620, 620), (-20, 620)])
    out.append(f'<path d="{gd}" fill="#2A3A3A"/>')
    out.append(f'<path d="{gd}" fill="{D.rad([(0, "#E8964A", 0.6), (0.4, "#A85A3A", 0.3), (1, "#2A3A3A", 0)], 0.62, 0.3, 0.6)}"/>')
    out.append(grass(8, (-10, 470, 610, 600), ["#3A5A4A", "#5A7A4A", "#2A4A3A", "#8A7A4A"], 160, (8, 20)))
    # tent glowing from inside
    out.append(cast(D, 250, 500, 150, 14, color="#0A0A1A", strength=0.5))
    out.append(soft_glow(D, 240, 430, 200, "#FFB84A", 0.4))
    out.append(painted(D, [(240, 300), (270, 300), (390, 500), (300, 504), (176, 500)], ("#FFB86A", "#F28A2A", "#B8501A"), 11, sdir=(1, 0.3), sk=0.12, angle=-60, n=40, inkw=2.4, hi=0.3))
    out.append(painted(D, [(110, 500), (240, 300), (210, 400), (176, 500)], ("#FFE08A", "#FFC23A", "#C8800E"), 12, sdir=(-1, 0.3), sk=0.1, angle=-120, n=30, inkw=2.4, hi=0.3))
    out.append(f'<path d="M 242 306 L 186 498 L 288 498 Z" fill="{D.lin([(0, "#FFF6C0"), (0.6, "#FFD86A"), (1, "#FF9A3A")])}"/>')
    out.append(painted(D, [(242, 306), (186 + 10, 498), (214, 498), (246, 330)], ("#FFE08A", "#F2A43A", "#B8641A"), 13, sk=0.1, n=6, inkw=1.6, hi=0.2))
    out.append(ink("M 242 306 L 186 498 M 242 306 L 288 498", INK, 2, 14, 1, 0.8))
    # little silhouettes of two campers inside & bunting
    out.append(f'<path d="{blob(250, 470, 14, 26, 15, 0.1, 10)}" fill="#C8641A" opacity="0.5"/><circle cx="250" cy="438" r="10" fill="#C8641A" opacity="0.5"/>')
    out.append(pline([(240, 300), (250, 284)], INK, 3, 15, 1, 1))
    out.append(painted(D, [(250, 284), (274, 290), (250, 296)], CORAL, 16, sk=0.1, n=1, inkw=1.2, hi=0.3))
    # guy ropes
    out.append(pline([(390, 500), (430, 506)], "#E8D2A0", 1.4, 17, 0.8, 1) + pline([(110, 500), (80, 506)], "#E8D2A0", 1.4, 18, 0.8, 1))
    # campfire with logs, sparks
    fx, fb = 450, 506
    for k, (a, col) in enumerate(((-18, "#7A4A2A"), (18, "#8A5A32"), (90, "#6A3E22"))):
        p = rot([(fx - 34, fb), (fx + 34, fb)], fx, fb, a * 0.3)
        out.append(taper(p, 12, 12, col) + pline(p, INK, 1.4, k, 0.5, 1))
    for k in range(6):
        a = math.pi + math.pi * k / 5
        out.append(painted(D, blob_pts(fx + 46 * math.cos(a), fb + 10 + 4 * math.sin(a), 10, 7, 40 + k, 0.1, 10), ("#A8A0B0", "#6A6474", "#3A3444"), 40 + k, sk=0.2, n=2, inkw=1.2, hi=0.3))
    out.append(flame(D, fx, fb, 64, 50))
    rnd = random.Random(51)
    for i in range(14):
        out.append(f'<circle cx="{fx + rnd.uniform(-40, 40):.1f}" cy="{fb - rnd.uniform(70, 170):.1f}" r="{rnd.uniform(1.2, 2.6):.1f}" fill="#FFD86A" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    # marshmallow stick
    out.append(pline([(560, 556), (476, 452)], "#8A5A32", 3.4, 52, 1, 1) + f'<path d="{blob(472, 446, 9, 7, 53, 0.1, 10, -50)}" fill="#FFF6E8" stroke="{INK}" stroke-width="1.4"/>')
    # lettering
    out.append(letters(D, 300, 142, "happy", SERIF_IT, 110, "#FFFFFF", ["#FFFFFF", "#FFF0D8", "#E8E0FF"], 61, max_w=320,
                       shadow="#0A0A2A", soff=(0.025, 0.04), angle=-35))
    out.append(letters(D, 300, 232, "CAMPER", BEBAS, 104, "#FFB43A", ["#FFD27A", "#F28A1A", "#FFE6A8"], 62, ls=16, max_w=380,
                       shadow="#0A0A2A", angle=-78, hi="#FFF6D8"))
    return finish(D, out, 61, "#0A0A2A", 0.6)


# ================================================================ 22. lake life — a dock, a red canoe and still water
def canoe(D, x0, x1, y, depth, seed, pal=RED):
    L = x1 - x0
    top = [(x0 + L * t, y - depth * 0.15 * (abs(t - 0.5) * 2) ** 3 * 2.4 - (depth * 0.1 if t in (0, 1) else 0)) for t in [i / 16 for i in range(17)]]
    top[0] = (x0 - 6, y - depth * 0.6)
    top[-1] = (x1 + 6, y - depth * 0.6)
    bot = [(x0 + L * t, y + depth * math.sin(math.pi * t) ** 0.6) for t in [i / 16 for i in range(16, -1, -1)]]
    hull = top + bot[1:-1]
    out = [painted(D, hull, pal, seed, sdir=(0.3, 1), sk=0.15, angle=0, n=40, inkw=2.2, hi=0.35)]
    out.append(taper(top, 4, 4, "#FFF0E0", 0.85))
    for t in (0.33, 0.5, 0.67):
        x = x0 + L * t
        out.append(pline([(x, y - 2), (x, y + depth * 0.4)], pal[2], 2, int(x), 0.5, 1))
    return "".join(out)


def adirondack(D, x, base, s, pal, seed, flip=1):
    """Adirondack chair from the side-front: slatted back, broad arms."""
    def P(px, py):
        return (x + flip * px * s, base + py * s)
    out = []
    for k in range(5):
        bx = -0.32 + k * 0.12
        sl = [P(bx, -0.45), P(bx - 0.05, -1.1 - 0.06 * (2 - abs(k - 2))), P(bx + 0.07, -1.12 - 0.06 * (2 - abs(k - 2))), P(bx + 0.1, -0.45)]
        out.append(painted(D, sl, pal, seed + k, sdir=(flip, 0.2), sk=0.2, angle=-100, n=3, inkw=1.4, hi=0.3))
    seat = [P(-0.38, -0.45), P(0.45, -0.38), P(0.5, -0.28), P(-0.36, -0.32)]
    out.append(painted(D, seat, pal, seed + 6, sk=0.2, n=3, inkw=1.4, hi=0.3))
    for lx in (-0.3, 0.4):
        out.append(painted(D, [P(lx - 0.04, -0.6), P(lx + 0.04, -0.6), P(lx + 0.04, 0), P(lx - 0.04, 0)], pal, seed + 7, sk=0.25, n=2, inkw=1.3, hi=0.2))
    arm = [P(-0.42, -0.66), P(0.55, -0.62), P(0.55, -0.56), P(-0.42, -0.6)]
    out.append(painted(D, arm, pal, seed + 8, sk=0.2, n=2, inkw=1.4, hi=0.4))
    return "".join(out)


@design("lake-life")
def lake_life():
    D = Doc("ll")
    out = [sky(D, [(0, "#5AC8F0"), (0.3, "#A8E4F4"), (0.45, "#FFF0D0")], 3, 300, ["#FFFFFF", "#7AD0F0", "#FFF6E0"], 40)]
    out.append(sun_disc(D, 470, 212, 36, ("#FFFCE0", "#FFE87A", "#FFB43A"), 3, glow_col="#FFF6C0", glow_r=3.4))
    out.append(puff_cloud(D, 150, 190, 120, 4, ("#FFFFFF", "#FFFFFF", "#C8E0F0")))
    # mountains
    m1 = ridge([(-20, 260), (90, 190), (180, 236), (290, 176), (390, 230), (480, 196), (620, 250)], 5, 12)
    out.append(hill(D, m1, 330, ("#B8D0E8", "#8AA8D0", "#5A78A8"), 5, angle=-40, inkw=1.2, inkop=0.3))
    for (px, py) in ((290, 176), (90, 190), (480, 196)):
        out.append(f'<path d="M {px - 22} {py + 22} L {px} {py} L {px + 22} {py + 20} L {px + 10} {py + 16} L {px} {py + 24} L {px - 10} {py + 16} Z" fill="#FFFFFF" opacity="0.85"/>')
    # far forest band
    for i, x in enumerate(range(-20, 640, 15)):
        h = 40 + (i * 53 % 34)
        out.append(pine_sil(x, 300, h, rnd_col(i), 70 + i, 0.42))
    # lake with reflections
    lake = "M -10 298 L 610 298 L 610 610 L -10 610 Z"
    out.append(f'<path d="{lake}" fill="{D.lin([(0, "#2E8A8A"), (0.4, "#3AB0B0"), (1, "#1E6E80")], 0, 298, 0, 610, "userSpaceOnUse")}"/>')
    refl = []
    for i, x in enumerate(range(-20, 640, 15)):
        h = 40 + (i * 53 % 34)
        refl.append(f'<g transform="translate(0 600) scale(1 -1)">{pine_sil(x, 302, h * 0.8, "#1E5A54", 70 + i, 0.42)}</g>')
    out.append(f'<g opacity="0.45">{"".join(refl)}</g>')
    out.append(strokes(D.nid(), lake, (-60, 298, 610, 610), ["#8EE0D8", "#1E5E6E", "#FFFFFF", "#5AC8C8"], 6, n=120, angle=0, length=(30, 120), width=(1.5, 4), opacity=(0.15, 0.4)))
    out.append(wave_lines(7, (0, 310, 600, 600), ["#C8FFF4", "#FFFFFF"], 40, (20, 50), 2, 2, (0.3, 0.6)))
    rnd = random.Random(8)
    for i in range(10):
        t = i / 9
        y = 310 + t * 40
        hw = 26 * (1 - t * 0.4)
        out.append(taper([(470 - hw, y), (470, y - 1), (470 + hw, y)], 1, 2.5, "#FFF6C0", 0.8))
    # dock receding from the bottom left
    dock_l = [(40, 610), (230, 400), (306, 400), (330, 610)]
    dd = smooth_closed(poly_pts(dock_l, 24, 9, 0.5))
    out.append(f'<path d="{dd}" fill="#B8865A"/>')
    cid = D.clip(f'<path d="{dd}"/>')
    pl = []
    y = 400
    k = 0
    while y < 610:
        hgt = 6 + k * 2.2
        t0 = (y - 400) / 210
        xl, xr = 230 - 190 * t0, 306 + 24 * t0
        pl.append(f'<path d="M {xl - 10:.1f} {y:.1f} L {xr + 10:.1f} {y:.1f}" stroke="#6A4224" stroke-width="{1 + k * 0.25:.1f}" opacity="0.7"/>')
        pl.append(f'<path d="M {xl - 10:.1f} {y + 1.5:.1f} L {xr + 10:.1f} {y + 1.5:.1f}" stroke="#E8B884" stroke-width="{0.6 + k * 0.15:.1f}" opacity="0.5"/>')
        y += hgt
        k += 1
    out.append(f'<g {cid}>{"".join(pl)}</g>')
    out.append(strokes(D.nid(), dd, (30, 390, 340, 610), ["#E8B884", "#7A4E2A", "#D8A070"], 10, n=70, angle=-60, length=(10, 40), width=(1, 3), opacity=(0.2, 0.4)))
    out.append(ink(dd, INK, 2, 11, 1, 0.6))
    # posts
    for x, y0, y1 in ((228, 396, 430), (306, 396, 434), (150, 486, 560)):
        out.append(painted(D, rect_pts(x - 6, y0, x + 6, y1, 10, x, 0.4), WOOD, x, sdir=(1, 0), sk=0.25, angle=-90, n=4, inkw=1.6, hi=0.3))
    # canoe tied alongside, with a paddle
    out.append(f'<path d="{blob(436, 470, 120, 10, 12, 0.1, 14)}" fill="#0E4E5A" opacity="0.3"/>')
    out.append(canoe(D, 330, 540, 446, 26, 13, ("#FF8A6A", "#E8402E", "#9A1A10")))
    out.append(pline([(306, 420), (334, 438)], "#E8D2A0", 2, 14, 0.9, 1))
    out.append(taper([(390, 424), (500, 412)], 5, 5, "#C8925A") + painted(D, blob_pts(512, 410, 16, 6, 15, 0.1, 10), WOOD, 15, sk=0.2, n=2, inkw=1.4, hi=0.3))
    # two chairs at the end of the dock
    out.append(adirondack(D, 246, 410, 46, ("#7AE0F0", "#1FB5C8", "#0E6A78"), 16, 1))
    out.append(adirondack(D, 290, 406, 42, ("#FFE27A", "#FFC23A", "#C8880E"), 20, 1))
    # a loon and lily pads
    out.append(f'<path d="{blob(100, 360, 16, 6, 21, 0.1, 10)}" fill="#1A1A22"/><circle cx="88" cy="352" r="5" fill="#1A1A22"/><path d="M 84 352 l -8 2" stroke="#1A1A22" stroke-width="2"/>')
    out.append(taper([(80, 368), (120, 368)], 2, 2, "#FFFFFF", 0.6))
    for i, (x, y, r_) in enumerate(((470, 540, 18), (510, 520, 12), (430, 566, 14))):
        out.append(f'<path d="M {x} {y} L {x + r_} {y - 3} A {r_} {r_ * 0.45} 0 1 0 {x + r_} {y + 3} Z" fill="#4AA05A" stroke="#1E6234" stroke-width="1.4"/>')
    out.append(daisy(D, 480, 534, 8, 30, petal=("#FFFFFF", "#FFE0F0", "#E8A0C0"), n=8))
    # lettering
    out.append(letters(D, 160, 138, "lake", SERIF_IT, 100, "#0E4E5A", ["#1E6E7A", "#0A2E3A", "#2E8A90"], 41, max_w=220,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-35))
    out.append(letters(D, 360, 138, "LIFE", BEBAS, 100, "#E8402E", ["#FF6A4A", "#B8281A", "#FF8A6A"], 42, ls=12, max_w=200,
                       shadow="#0E3E4A", angle=-78, hi="#FFE0D8"))
    return finish(D, out, 62)


def rnd_col(i):
    return ["#1E5A4A", "#2A6A50", "#174A3E", "#24604A"][i % 4]


# ================================================================ 23. summer nights — fireflies in a jar at dusk
def jar(D, cx, top, w, h, seed):
    pts = [(cx - w * 0.36, top), (cx + w * 0.36, top), (cx + w * 0.38, top + h * 0.06), (cx + w * 0.5, top + h * 0.16), (cx + w * 0.5, top + h * 0.94),
           (cx + w * 0.44, top + h), (cx - w * 0.44, top + h), (cx - w * 0.5, top + h * 0.94), (cx - w * 0.5, top + h * 0.16), (cx - w * 0.38, top + h * 0.06)]
    d = smooth_closed(pts)
    return pts, d


@design("summer-nights")
def summer_nights():
    D = Doc("sn")
    out = [sky(D, [(0, "#1A1650"), (0.4, "#4A2A80"), (0.66, "#A84A8A"), (0.8, "#F28A7A")], 3, 600, ["#2A2A6A", "#6A3A9A", "#C85A8A"], 70)]
    out.append(specks(5, (0, 0, 600, 300), ["#FFFFFF", "#FFF4C0"], 90, (0.6, 1.6), (0.4, 1)))
    for x, y, r_ in ((80, 250, 7), (530, 230, 8), (470, 300, 5)):
        out.append(sparkle(x, y, r_, "#FFF6C0"))
    # distant tree line & field
    for i, x in enumerate(range(-20, 640, 40)):
        out.append(dab_crown(D, x, 430 - (i * 17 % 20), 34, 30, [("#3A2A5A", "#2A1E4A", "#1A1236")], 80 + i, 20, (6, 10), inkw=0))
    gd = smooth_closed([(-20, 450), (200, 440), (400, 448), (620, 438), (620, 620), (-20, 620)])
    out.append(f'<path d="{gd}" fill="#1E2A3A"/>')
    out.append(grass(8, (-10, 450, 610, 610), ["#2A4A3A", "#3A5A4A", "#4A6A3A", "#1A3A2A"], 220, (14, 40)))
    # fireflies drifting outside the jar
    rnd = random.Random(9)
    def bug(x, y, r):
        return soft_glow(D, x, y, r * 6, "#E8FF7A", 0.75) + f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#F8FFC0"/>'
    for i in range(16):
        x, y = rnd.uniform(60, 540), rnd.uniform(250, 540)
        if 190 < x < 410 and 230 < y < 540:
            continue
        out.append(bug(x, y, rnd.uniform(2, 3.6)))
    # the jar on the grass, glowing
    cx, top, w, h = 300, 262, 200, 262
    out.append(soft_glow(D, cx, top + h * 0.55, 230, "#D8FF7A", 0.55))
    out.append(cast(D, cx + 10, top + h + 2, 120, 12, color="#0A0A1A", strength=0.5))
    pts, d = jar(D, cx, top, w, h, 10)
    g = D.rad([(0, "#F4FFC0", 0.85), (0.5, "#C8F06A", 0.45), (1, "#6A8AA0", 0.35)], 0.5, 0.6, 0.6)
    out.append(f'<path d="{d}" fill="{g}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for i in range(12):
        x, y = cx + rnd.uniform(-0.38, 0.38) * w, top + rnd.uniform(0.25, 0.9) * h
        inner.append(bug(x, y, rnd.uniform(2.4, 4)))
    # a grass sprig inside
    inner.append(taper([(cx - 30, top + h), (cx - 40, top + h * 0.6), (cx - 26, top + h * 0.4)], 5, 1, "#4A8A3A", 0.8))
    inner.append(taper([(cx + 20, top + h), (cx + 36, top + h * 0.7), (cx + 30, top + h * 0.5)], 4, 1, "#5A9A3A", 0.8))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # glass: rim highlights and reflections
    out.append(taper([(cx - w * 0.4, top + h * 0.85), (cx - w * 0.42, top + h * 0.5), (cx - w * 0.36, top + h * 0.22)], 12, 4, "#FFFFFF", 0.45))
    out.append(taper([(cx + w * 0.38, top + h * 0.3), (cx + w * 0.4, top + h * 0.5)], 5, 2, "#FFFFFF", 0.4))
    out.append(ink(d, "#E8F4FF", 2.6, 11, 1, 0.75))
    for k in range(2):
        out.append(pline([(cx - w * 0.36, top + 18 + k * 9), (cx, top + 21 + k * 9), (cx + w * 0.36, top + 18 + k * 9)], "#E8F4FF", 2, k, 0.5, 1))
    # cloth cover tied with twine (with air holes)
    cloth = [(cx - w * 0.5, top + 30), (cx - w * 0.44, top + 6), (cx - w * 0.3, top - 16), (cx, top - 22), (cx + w * 0.3, top - 16), (cx + w * 0.44, top + 6), (cx + w * 0.5, top + 30),
             (cx + w * 0.4, top + 22), (cx + w * 0.3, top + 34), (cx + w * 0.14, top + 22), (cx, top + 36), (cx - w * 0.14, top + 22), (cx - w * 0.3, top + 34), (cx - w * 0.4, top + 22)]
    out.append(painted(D, cloth, ("#FFC8DC", "#FF8AB8", "#C8406E"), 12, sdir=(0.4, 1), sk=0.15, angle=-20, n=20, inkw=2, hi=0.4))
    ccid = D.clip(f'<path d="{smooth_closed(cloth)}"/>')
    out.append(f'<g {ccid}>' + "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#FFFFFF" opacity="0.8"/>' for x in range(int(cx - w * 0.4), int(cx + w * 0.42), 18) for y in (top - 6, top + 10)) + '</g>')
    out.append(taper([(cx - w * 0.42, top + 12), (cx, top + 16), (cx + w * 0.42, top + 12)], 5, 5, "#E8D2A0") + pline([(cx - w * 0.42, top + 12), (cx, top + 16), (cx + w * 0.42, top + 12)], INK, 1.2, 13, 0.6, 1))
    out.append(pline([(cx + w * 0.3, top + 14), (cx + w * 0.4, top + 40), (cx + w * 0.34, top + 56)], "#E8D2A0", 3, 14, 1, 1) + pline([(cx + w * 0.3, top + 14), (cx + w * 0.22, top + 44)], "#E8D2A0", 3, 15, 1, 1))
    # clover & dandelion puff at the jar's foot
    for i, x in enumerate((176, 420, 446)):
        out.append(daisy(D, x, 540 - i * 6, 10, 40 + i, n=8))
    # lettering
    out.append(letters(D, 300, 116, "summer", SERIF_IT, 118, "#FFFFFF", ["#FFFFFF", "#FFF0D8", "#F0E8FF"], 51, max_w=380,
                       shadow="#0A0A2A", soff=(0.025, 0.04), angle=-35))
    out.append(letters(D, 300, 204, "NIGHTS", BEBAS, 92, "#E0FF6A", ["#F0FFA0", "#B8E030", "#FFFFFF"], 52, ls=22, max_w=330,
                       shadow="#0A0A2A", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 63, "#0A0A2A", 0.5)


# ================================================================ 24. stay sunny — a sunflower and a honeybee
def sunflower(D, cx, cy, r, seed):
    rnd = random.Random(seed)
    out = []
    petal_pals = [("#FFEA7A", "#FFC21A", "#D8860A"), ("#FFE060", "#FFB000", "#C8740A")]
    for layer, (n, rr, off) in enumerate(((22, 1.0, 0), (20, 0.86, 8))):
        for i in range(n):
            a = math.radians(i * 360 / n + off + rnd.uniform(-4, 4))
            L = r * rr * rnd.uniform(0.9, 1.05)
            px, py = cx + math.cos(a) * (r * 0.42 + L * 0.3), cy + math.sin(a) * (r * 0.42 + L * 0.3)
            pts = []
            for j in range(12):
                t = j / 11
                w = L * 0.13 * math.sin(math.pi * t) ** 0.8
                d = r * 0.36 + L * 0.62 * t
                for sg in (1,):
                    pass
                pts.append((d, w))
            outline = [(cx + math.cos(a) * d - math.sin(a) * w, cy + math.sin(a) * d + math.cos(a) * w) for d, w in pts] + \
                      [(cx + math.cos(a) * d + math.sin(a) * w, cy + math.sin(a) * d - math.cos(a) * w) for d, w in pts[::-1]]
            pal = petal_pals[layer]
            out.append(painted(D, jitter(outline, seed + i, 0.8), pal if layer else (mix(pal[0], "#C8740A", 0.15), mix(pal[1], "#C8740A", 0.2), pal[2]), seed + layer * 50 + i,
                               sdir=(math.cos(a), math.sin(a)), sk=0.12, angle=math.degrees(a), n=5, slen=(L * 0.2, L * 0.5), sw=(1, 2.4), inkw=1.4, inkop=0.6, hi=0.35))
    disc = blob_pts(cx, cy, r * 0.42, r * 0.42, seed, 0.02, 20)
    out.append(painted(D, disc, ("#A8682A", "#6A3A16", "#2E1608"), seed + 99, sk=0.15, n=12, inkw=2, hi=0.2))
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(260):
        rr = r * 0.4 * math.sqrt(i / 260)
        a = i * golden
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        col = "#E8A040" if rr < r * 0.12 else ("#3A1E0A" if i % 3 else "#8A5A2A")
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(1.2, 2.6 * (0.5 + rr / (r * 0.8))):.1f}" fill="{col}" opacity="0.85"/>')
    out.append(f'<path d="{smooth_closed(disc)}" fill="{D.rad([(0.5, "#000000", 0), (1, "#000000", 0.3)], 0.42, 0.4, 0.6)}"/>')
    out.append(taper([(cx - r * 0.3, cy - r * 0.08), (cx - r * 0.22, cy - r * 0.26), (cx - r * 0.06, cy - r * 0.34)], 4, 1, "#FFE0A0", 0.6))
    return "".join(out)


def honeybee(D, cx, cy, s, seed, rot_=0):
    out = [f'<g transform="rotate({rot_} {cx} {cy})">']
    for k, (dx, dy, a) in enumerate(((-0.1, -0.6, -20), (0.25, -0.62, 20))):
        out.append(f'<path d="{blob(cx + dx * s, cy + dy * s, 0.34 * s, 0.5 * s, seed + k, 0.05, 12, a)}" fill="#FFFFFF" opacity="0.75" stroke="{INK}" stroke-width="1.6"/>')
    body = blob_pts(cx, cy, 0.62 * s, 0.42 * s, seed + 3, 0.03, 16)
    out.append(painted(D, body, ("#FFE27A", "#FFC21A", "#C8860A"), seed + 3, sk=0.2, angle=-90, n=8, inkw=2, hi=0.5))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    out.append(f'<g {cid}>' + "".join(f'<path d="M {cx + dx * s:.1f} {cy - s:.1f} q {0.08 * s:.1f} {s:.1f} 0 {2 * s:.1f}" stroke="#2A1A10" stroke-width="{0.16 * s:.1f}" fill="none"/>' for dx in (-0.08, 0.26)) + '</g>')
    out.append(f'<path d="M {cx + 0.6 * s:.1f} {cy - 0.05 * s:.1f} l {0.22 * s:.1f} {0.06 * s:.1f} l {-0.2 * s:.1f} {0.08 * s:.1f} Z" fill="#2A1A10"/>')
    out.append(painted(D, blob_pts(cx - 0.62 * s, cy - 0.04 * s, 0.28 * s, 0.27 * s, seed + 4, 0.03, 12), ("#4A3A2A", "#2A1A10", "#0A0604"), seed + 4, sk=0.1, n=3, inkw=1.6, hi=0.3))
    out.append(f'<circle cx="{cx - 0.72 * s:.1f}" cy="{cy - 0.1 * s:.1f}" r="{0.06 * s:.1f}" fill="#FFFFFF"/>')
    out.append(pline([(cx - 0.7 * s, cy - 0.28 * s), (cx - 0.86 * s, cy - 0.6 * s), (cx - 1.0 * s, cy - 0.64 * s)], "#2A1A10", max(1.4, s * 0.05), seed, 1, 1))
    out.append(pline([(cx - 0.56 * s, cy - 0.3 * s), (cx - 0.56 * s, cy - 0.66 * s), (cx - 0.44 * s, cy - 0.74 * s)], "#2A1A10", max(1.4, s * 0.05), seed + 1, 1, 1))
    out.append("</g>")
    return "".join(out)


@design("stay-sunny")
def stay_sunny():
    D = Doc("ssy")
    out = [sky(D, [(0, "#3AB8F0"), (0.55, "#8ADCF8"), (1, "#D8F6FF")], 3, 600, ["#FFFFFF", "#5AC8F0", "#C8F0FF"], 60)]
    out.append(soft_glow(D, 300, 400, 300, "#FFF6C8", 0.65))
    out.append(puff_cloud(D, 90, 290, 120, 4, ("#FFFFFF", "#FFFFFF", "#B8DCF0")))
    out.append(puff_cloud(D, 520, 330, 110, 5, ("#FFFFFF", "#FFFFFF", "#B8DCF0")))
    # stem and leaves
    stem = catmull([(296, 640), (306, 560), (300, 470)], 8)
    out.append(taper(stem, 22, 16, LEAF[2]) + taper(stem, 16, 12, LEAF[1]) + taper([(x - 4, y) for x, y in stem], 4, 3, LEAF[0], 0.8))
    for i, (bx, by, ang, L, W) in enumerate(((300, 560, -150, 130, 40), (304, 590, -30, 130, 40), (300, 520, -20, 100, 30))):
        out.append(banana_leaf(D, bx, by, ang, L, W, 10 + i, LEAF))
    out.append(sunflower(D, 300, 396, 156, 20))
    out.append(honeybee(D, 496, 236, 30, 21, -12))
    for k, (x, y) in enumerate(((470, 254), (452, 262), (434, 258), (418, 266))):
        out.append(f'<circle cx="{x}" cy="{y}" r="1.8" fill="#3A2418" opacity="0.6"/>')
    out.append(letters(D, 300, 124, "stay", SERIF_IT, 96, "#FFFFFF", ["#FFFFFF", "#FFF6D8", "#E8F8FF"], 31, max_w=260,
                       shadow="#1E6A9A", soff=(0.025, 0.04), angle=-35))
    out.append(letters(D, 300, 222, "SUNNY", BEBAS, 108, "#FFD21A", ["#FFE27A", "#F2A800", "#FFF0B0"], 32, ls=22, max_w=360,
                       shadow="#1E4E7A", angle=-78, hi="#FFFFFF", inkc="#8A4A00", inkw=1.4))
    return finish(D, out, 64)


# ================================================================ 25. pinch me, I'm on vacation — a crab in shades on a beach towel
def crab(D, cx, cy, s, seed, pal=CORAL):
    out = [cast(D, cx + 10, cy + s * 0.5, s * 1.1, s * 0.2, strength=0.3, seed=seed)]
    # legs
    for sg in (-1, 1):
        for k in range(3):
            a0 = (cx + sg * s * (0.55 + k * 0.05), cy + s * (0.05 + k * 0.12))
            a1 = (cx + sg * s * (0.95 + k * 0.06), cy + s * (0.05 + k * 0.14))
            a2 = (cx + sg * s * (1.12 + k * 0.04), cy + s * (0.4 + k * 0.12))
            out.append(taper([a0, a1, a2], s * 0.1, s * 0.04, pal[2]) + taper([a0, a1, a2], s * 0.075, s * 0.03, pal[1]))
    # arms + claws raised
    for sg in (-1, 1):
        arm = [(cx + sg * s * 0.55, cy - s * 0.1), (cx + sg * s * 0.9, cy - s * 0.35), (cx + sg * s * 0.92, cy - s * 0.7)]
        out.append(taper(arm, s * 0.16, s * 0.12, pal[2]) + taper(arm, s * 0.12, s * 0.09, pal[1]))
        clx, cly = cx + sg * s * 0.92, cy - s * 0.92
        claw = [(clx - s * 0.2, cly + s * 0.2), (clx - s * 0.26, cly - s * 0.08), (clx - s * 0.1, cly - s * 0.3), (clx + s * 0.06, cly - s * 0.32), (clx + s * 0.02, cly - s * 0.12),
                (clx + s * 0.08, cly - s * 0.0), (clx + s * 0.24, cly - s * 0.1), (clx + s * 0.24, cly + s * 0.12), (clx + s * 0.06, cly + s * 0.28)]
        if sg > 0:
            claw = [(2 * clx - x, y) for x, y in claw]
        out.append(painted(D, claw, pal, seed + sg, sdir=(0.5, 0.8), sk=0.15, angle=-60, n=10, inkw=2, hi=0.45))
    body = blob_pts(cx, cy, s * 0.72, s * 0.46, seed + 3, 0.04, 22)
    body = [(x, y - (s * 0.05 if y < cy else 0)) for x, y in body]
    out.append(painted(D, body, pal, seed + 3, sdir=(0.5, 0.8), sk=0.14, angle=-30, n=40, inkw=2.4, hi=0.4))
    rnd = random.Random(seed)
    for i in range(10):
        out.append(f'<circle cx="{cx + rnd.uniform(-0.5, 0.5) * s:.1f}" cy="{cy + rnd.uniform(-0.3, 0.2) * s:.1f}" r="{s * rnd.uniform(0.02, 0.04):.1f}" fill="{pal[0]}" opacity="0.7"/>')
    # eye stalks with sunglasses
    for sg in (-1, 1):
        out.append(taper([(cx + sg * s * 0.18, cy - s * 0.38), (cx + sg * s * 0.22, cy - s * 0.62)], s * 0.08, s * 0.06, pal[2]))
    out.append(sunglasses(D, cx, cy - s * 0.66, s * 0.56, ("#FFF07A", "#FFC93C", "#B8800E"), ("#7AE8F0", "#1E7AB0", "#0A2A5A"), seed + 5, 0, round_=True))
    out.append(pline([(cx - s * 0.2, cy - s * 0.08), (cx, cy + s * 0.06), (cx + s * 0.2, cy - s * 0.08)], "#5A0A0A", max(2.4, s * 0.04), seed, 1, 1))
    out.append(f'<ellipse cx="{cx - s * 0.36:.1f}" cy="{cy - s * 0.06:.1f}" rx="{s * 0.08:.1f}" ry="{s * 0.05:.1f}" fill="#FF8AA0" opacity="0.6"/><ellipse cx="{cx + s * 0.36:.1f}" cy="{cy - s * 0.06:.1f}" rx="{s * 0.08:.1f}" ry="{s * 0.05:.1f}" fill="#FF8AA0" opacity="0.6"/>')
    return "".join(out)


@design("pinch-me-im-on-vacation")
def pinch_me():
    D = Doc("pm")
    full = "M -10 -10 L 610 -10 L 610 610 L -10 610 Z"
    out = [f'<rect width="600" height="600" fill="#FFFFFF"/>']
    out.append(stripes_in(D, full, (0, 0, 600, 600), 24, [46, 14, 46, 14], [MINT[1], None, "#7ADCE8", None], 3))
    out.append(strokes(D.nid(), full, (-60, 0, 600, 600), ["#FFFFFF", "#2E9A72", "#C8F5DA"], 4, n=200, angle=24 + 90, length=(30, 90), width=(2, 6), opacity=(0.1, 0.25)))
    out.append(soft_glow(D, 300, 330, 260, "#FFFFFF", 0.55))
    # a tiny drink with an umbrella and a scatter of shells
    out.append(cast(D, 510, 446, 30, 10, strength=0.3))
    out.append(painted(D, [(486, 380), (534, 380), (522, 446), (498, 446)], ("#FFF6F0", "#FFE0C8", "#C8A890"), 5, sk=0.15, n=4, inkw=1.8, hi=0.5))
    out.append(painted(D, [(490, 392), (530, 392), (521, 440), (499, 440)], ORANGE, 6, sk=0.15, n=4, inkw=0, hi=0.4, edge=False))
    out.append(pline([(516, 384), (540, 340)], "#8A5A32", 2, 7, 1, 1))
    out.append(painted(D, [(520, 340), (544, 326), (566, 338), (546, 346)], PINK, 8, sk=0.1, n=2, inkw=1.6, hi=0.4))
    out.append(lemon_wheel(D, 488, 384, 12, 9))
    out.append(scallop(D, 96, 446, 20, ("#FFFFFF", "#FFC8B8", "#D07A6A"), 10, -20) + starfish(D, 512, 520, 18, SUN, 11, 10))
    out.append(crab(D, 300, 372, 150, 12, ("#FF8A6A", "#F24A32", "#9A1A10")))
    out.append(letters(D, 300, 132, "pinch me", SERIF_IT, 116, "#E83A5A", ["#FF6A80", "#B8163A", "#FF8AA0"], 21, max_w=400,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-35))
    out.append(ribbon(D, 300, 520, 400, 58, TURQ, 22, tail=34))
    out.append(label(300, 535, "I'M ON VACATION", BEBAS, 46, "#FFFFFF", ls=4, max_w=360))
    return finish(D, out, 65)


# ================================================================ 26. whale hello there — a spouting whale on a sunny sea
def whale(D, cx, cy, s, seed, pal=("#6AA8E8", "#2E6AC0", "#14347A"), belly=("#FFFFFF", "#E8F4FF", "#A8C8E8")):
    """Friendly whale at the surface, facing left; tail flukes up at the right."""
    def P(x, y):
        return (cx + x * s, cy + y * s)
    out = []
    tail = [P(0.8, 0.0), P(0.98, -0.3), P(1.02, -0.56), P(0.88, -0.64), P(0.72, -0.82), P(0.92, -0.8), P(1.06, -0.68), P(1.2, -0.82), P(1.4, -0.82),
            P(1.26, -0.64), P(1.12, -0.54), P(1.1, -0.3), P(0.98, 0.04)]
    out.append(painted(D, tail, pal, seed, sdir=(0.5, 0.8), sk=0.15, angle=-70, n=10, inkw=2.2, hi=0.4))
    body = [P(-1.0, 0.0), P(-0.96, -0.32), P(-0.7, -0.52), P(-0.2, -0.56), P(0.4, -0.38), P(0.86, -0.14), P(1.0, 0.04), P(0.7, 0.2), P(0.0, 0.32), P(-0.6, 0.3), P(-0.92, 0.18)]
    out.append(painted(D, body, pal, seed + 1, sdir=(0.4, 1), sk=0.12, angle=-10, n=40, inkw=2.6, hi=0.4))
    bel = [P(-0.94, 0.06), P(-0.6, 0.12), P(0.0, 0.14), P(0.6, 0.08), P(0.7, 0.2), P(0.0, 0.32), P(-0.6, 0.3), P(-0.9, 0.18)]
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    out.append(f'<g {cid}>' + painted(D, bel, belly, seed + 2, sk=0.1, angle=0, n=10, inkw=0, hi=0.3, edge=False))
    for k in range(5):
        out.append(pline([P(-0.86 + k * 0.08, 0.14 + k * 0.012), P(-0.2 + k * 0.08, 0.2 + k * 0.016)], belly[2], 1.6, k, 0.7, 1))
    out.append("</g>")
    # fin, eye, smile, cheek
    fin = [P(-0.3, 0.12), P(-0.06, 0.2), P(0.08, 0.42), P(-0.14, 0.34)]
    out.append(painted(D, fin, pal, seed + 3, sk=0.15, angle=40, n=4, inkw=2, hi=0.3))
    ex, ey = P(-0.62, -0.12)
    out.append(f'<path d="M {ex - s * 0.06:.1f} {ey:.1f} Q {ex:.1f} {ey - s * 0.08:.1f} {ex + s * 0.06:.1f} {ey:.1f}" stroke="#0A1A3A" stroke-width="{max(2.4, s * 0.025):.1f}" fill="none" stroke-linecap="round"/>')
    out.append(pline([P(-0.98, 0.02), P(-0.8, 0.08), P(-0.6, 0.04)], "#0A1A3A", max(2.4, s * 0.022), seed, 1, 1))
    cx2, cy2 = P(-0.66, 0.0)
    out.append(f'<ellipse cx="{cx2:.1f}" cy="{cy2 + s * 0.04:.1f}" rx="{s * 0.07:.1f}" ry="{s * 0.04:.1f}" fill="#FF8AB0" opacity="0.6"/>')
    out.append(taper([P(-0.6, -0.4), P(-0.2, -0.48), P(0.2, -0.42)], max(3, s * 0.04), 1, "#FFFFFF", 0.55))
    return "".join(out)


@design("whale-hello-there")
def whale_hello_there():
    D = Doc("wh")
    out = [sky(D, [(0, "#FFC8B8"), (0.45, "#FFE0C8"), (0.62, "#FFF2D8")], 3, 420, ["#FFFFFF", "#FFB8A8", "#FFE8D0"], 50)]
    out.append(sun_disc(D, 512, 206, 38, ("#FFF6C0", "#FFC93C", "#FF8A2A"), 3, glow_col="#FFE8A0", glow_r=2.6))
    out.append(puff_cloud(D, 110, 250, 130, 4, ("#FFFFFF", "#FFF8F4", "#F0C0C0")))
    out.append(puff_cloud(D, 450, 300, 100, 5, ("#FFFFFF", "#FFF8F4", "#F0C0C0")))
    out.append(sea(D, 380, 600, [(0, "#3FD0D0"), (0.5, "#1E9AC0"), (1, "#14609A")], 6, ["#9AF0EC", "#0E5E8A", "#FFFFFF"], 80, ticks=["#FFFFFF", "#B8F4F0"]))
    # spout: a fountain that splits and falls in drops
    rnd = random.Random(7)
    sx, sy = 240, 340
    out.append(taper([(sx, sy), (sx - 2, sy - 50), (sx, sy - 90)], 16, 8, "#FFFFFF", 0.95))
    for sg in (-1, 1):
        arc = [(sx, sy - 88), (sx + sg * 30, sy - 112), (sx + sg * 62, sy - 100), (sx + sg * 78, sy - 70)]
        out.append(taper(catmull(arc, 6), 12, 3, "#FFFFFF", 0.95) + taper(catmull(arc, 6), 4, 1, "#9AE8F4", 0.8))
        for k in range(3):
            x, y = sx + sg * (78 + k * 6), sy - 54 + k * 16
            out.append(f'<path d="M {x:.1f} {y - 9:.1f} Q {x + 6:.1f} {y:.1f} {x:.1f} {y + 5:.1f} Q {x - 6:.1f} {y:.1f} {x:.1f} {y - 9:.1f} Z" fill="#FFFFFF" stroke="#5AC8E0" stroke-width="1.4"/>')
    out.append(taper([(sx - 8, sy - 80), (sx - 6, sy - 30)], 4, 1, "#9AE8F4", 0.8))
    out.append(f'<path d="{blob(330, 446, 190, 20, 8, 0.1, 16)}" fill="#0E4E7A" opacity="0.25"/>')
    out.append(whale(D, 310, 420, 170, 9))
    # water line lapping across the whale's belly
    wl = [(x, 448 + 6 * math.sin(x / 26)) for x in range(110, 540, 12)]
    out.append(taper(wl, 6, 6, "#FFFFFF", 0.9))
    for x in range(130, 520, 34):
        out.append(f'<path d="{blob(x, 456 + 4 * math.sin(x), 10, 4, x, 0.2, 8)}" fill="#FFFFFF" opacity="0.8"/>')
    out.append(seagull(400, 260, 10, "#7A4A5A") + seagull(424, 248, 7, "#7A4A5A"))
    out.append(letters(D, 300, 142, "whale", SERIF_IT, 104, "#1E4E9A", ["#2E6AC0", "#14347A", "#4A8AD8"], 21, max_w=300,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-35))
    out.append(letters(D, 300, 544, "HELLO THERE", BEBAS, 82, "#FFFFFF", ["#FFFFFF", "#E8FFFA", "#C8F4F0"], 22, ls=8, max_w=420,
                       shadow="#0A3A66", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 66, "#0A3A66", 0.5)


# ================================================================ 27. dog days of summer — a dachshund in a swim ring
def dachshund(D, cx, cy, s, seed, ring=PINK):
    """Side view, facing left; (cx, cy) = middle of the back. Wears a swim ring around the middle."""
    coat = ("#E8A86A", "#C07A3A", "#7A4418")
    def P(x, y):
        return (cx + x * s, cy + y * s)
    out = [cast(D, cx, cy + s * 0.62, s * 1.3, s * 0.08, strength=0.35, seed=seed)]
    # far legs
    for x in (-0.5, 0.82):
        out.append(painted(D, [P(x - 0.08, 0.2), P(x + 0.08, 0.2), P(x + 0.1, 0.52), P(x - 0.1, 0.54)], (coat[1], coat[2], "#3A1E08"), seed + int(x * 10), sk=0.1, n=3, inkw=1.6, hi=0.2))
    # ring back half
    rx_, ry_ = 0.22 * s, 0.56 * s
    rcx, rcy = P(0.06, 0.1)
    back = [(rcx + rx_ * math.cos(math.radians(a)), rcy + ry_ * math.sin(math.radians(a))) for a in range(-90, 91, 10)]
    out.append(taper(back, s * 0.2, s * 0.2, ring[2]))
    # tail
    out.append(taper(catmull([P(0.96, -0.02), P(1.16, -0.16), P(1.26, -0.42)], 6), s * 0.11, s * 0.03, coat[1]))
    # body: deep chest at the front, tucked belly at the back
    body = [P(-0.9, -0.08), P(-0.6, -0.16), P(0.0, -0.13), P(0.6, -0.16), P(0.95, -0.08), P(1.04, 0.1), P(0.9, 0.28), P(0.5, 0.28), P(0.0, 0.32),
            P(-0.5, 0.42), P(-0.86, 0.38), P(-1.0, 0.16)]
    out.append(painted(D, body, coat, seed + 1, sdir=(0.3, 1), sk=0.15, angle=-5, n=50, inkw=2.4, hi=0.4))
    out.append(taper([P(-0.7, -0.08), P(0.0, -0.06), P(0.7, -0.08)], s * 0.05, s * 0.03, coat[0], 0.6))
    # near legs: short, a little angled, with paws
    for x, lean in ((-0.66, -0.04), (0.7, 0.06)):
        out.append(painted(D, [P(x - 0.1, 0.24), P(x + 0.1, 0.24), P(x + 0.09 + lean, 0.52), P(x - 0.11 + lean, 0.54)], coat, seed + 3 + int(x * 10), sk=0.15, n=3, inkw=1.8, hi=0.3))
        px_, py_ = P(x - 0.04 + lean, 0.55)
        out.append(painted(D, blob_pts(px_, py_, s * 0.13, s * 0.06, seed + int(x * 7), 0.06, 10), coat, seed + 9, sk=0.2, n=2, inkw=1.6, hi=0.3))
    # head with a long snout
    head = [P(-0.82, -0.06), P(-0.86, -0.38), P(-1.04, -0.56), P(-1.26, -0.56), P(-1.44, -0.46), P(-1.66, -0.36), P(-1.7, -0.26), P(-1.52, -0.18), P(-1.24, -0.12), P(-1.02, 0.04)]
    out.append(painted(D, head, coat, seed + 5, sdir=(0.3, 1), sk=0.15, angle=-20, n=20, inkw=2.4, hi=0.45))
    nx, ny = P(-1.66, -0.32)
    out.append(painted(D, blob_pts(nx, ny, s * 0.07, s * 0.06, seed + 6, 0.05, 10), ("#5A4A4A", "#2A1A1A", "#0A0404"), seed + 6, sk=0.1, n=1, inkw=1.2, hi=0.5))
    # tongue
    out.append(painted(D, [P(-1.46, -0.2), P(-1.36, -0.18), P(-1.38, -0.02), P(-1.44, 0.0), P(-1.48, -0.06)], ("#FFB8C8", "#FF6F8A", "#C83A5A"), seed + 7, sk=0.1, n=2, inkw=1.4, hi=0.4))
    out.append(pline([P(-1.6, -0.22), P(-1.44, -0.19), P(-1.3, -0.2)], "#3A1A08", max(2, s * 0.025), seed, 1, 1))
    # ear
    ear = [P(-1.02, -0.56), P(-0.86, -0.5), P(-0.78, -0.24), P(-0.82, -0.06), P(-0.94, -0.08), P(-1.0, -0.3)]
    out.append(painted(D, ear, ("#C88A4A", "#9A5A26", "#5A3010"), seed + 8, sdir=(1, 0.6), sk=0.15, angle=-80, n=8, inkw=2.2, hi=0.3))
    # sunglasses
    gx, gy = P(-1.26, -0.42)
    out.append(sunglasses(D, gx, gy, s * 0.3, ("#FF8AC0", "#FF3A8A", "#9A0E4A"), ("#7AE8F0", "#1E7AB0", "#0A2A5A"), seed + 9, -8, round_=True))
    # ring front half (over the body)
    front = [(rcx + rx_ * math.cos(math.radians(a)), rcy + ry_ * math.sin(math.radians(a))) for a in range(90, 271, 10)]
    out.append(taper(front, s * 0.24, s * 0.24, ring[2]) + taper(front, s * 0.2, s * 0.2, ring[1]))
    for a in (120, 180, 240):
        x, y = rcx + rx_ * math.cos(math.radians(a)), rcy + ry_ * math.sin(math.radians(a))
        out.append(f'<path d="{blob(x, y, s * 0.1, s * 0.05, a, 0.05, 10, a - 90)}" fill="#FFFFFF" opacity="0.9"/>')
    out.append(taper([(x - s * 0.05, y) for x, y in front[2:8]], s * 0.05, s * 0.02, "#FFFFFF", 0.6))
    out.append(pline(front, ring[2], 1.6, seed, 0.5, 1))
    return "".join(out)


@design("dog-days-of-summer")
def dog_days():
    D = Doc("dd")
    out = [sky(D, [(0, "#FFD86A"), (0.4, "#FFE89A"), (0.6, "#FFF6D0")], 3, 360, ["#FFF6C8", "#FFC84A", "#FFFFFF"], 60)]
    out.append(soft_glow(D, 470, 140, 220, "#FFFFFF", 0.5))
    out.append(sea(D, 330, 410, [(0, "#3FC8D8"), (1, "#1E8AB8")], 5, ["#9AF0EC", "#0E5E8A", "#FFFFFF"], 40, ticks=["#FFFFFF"]))
    sl = ridge([(-20, 404), (200, 396), (420, 404), (620, 398)], 6, 4)
    out.append(taper([(x, y - 3) for x, y in sl], 6, 6, "#FFFFFF", 0.9))
    out.append(sand_ground(D, sl, 620, 7))
    out.append(puff_cloud(D, 120, 240, 120, 8, ("#FFFFFF", "#FFFFFF", "#F0D8A8")))
    # an umbrella planted at the back right
    out.append(pline([(500, 470), (470, 250)], "#8A5A32", 5, 9, 1, 1))
    can = [(380, 270), (420, 222), (480, 200), (540, 214), (570, 250), (540, 262), (510, 258), (476, 266), (444, 262), (412, 272)]
    out.append(painted(D, can, ("#FFB0D0", "#FF5FA2", "#B82A6A"), 10, sdir=(0.3, 1), sk=0.15, angle=-20, n=20, inkw=2.2, hi=0.4))
    cid = D.clip(f'<path d="{smooth_closed(can)}"/>')
    out.append(f'<g {cid}>' + "".join(f'<path d="M 470 196 L {380 + k * 40} 290 L {400 + k * 40} 290 Z" fill="#FFFFFF" opacity="0.9"/>' for k in range(0, 5, 2)) + '</g>')
    # beach ball, bone, paw prints
    out.append(beach_ball(D, 506, 516, 28, 11))
    for i, (x, y) in enumerate(((90, 548), (124, 530), (150, 556), (184, 538))):
        out.append(f'<path d="{blob(x, y, 6, 5, 20 + i, 0.1, 8)}" fill="#C8A060" opacity="0.6"/>' + "".join(f'<circle cx="{x - 6 + k * 4}" cy="{y - 8 + abs(k - 1.5) * 1.5}" r="2" fill="#C8A060" opacity="0.6"/>' for k in range(4)))
    out.append(dachshund(D, 330, 410, 122, 12))
    out.append(letters(D, 300, 138, "dog days", SERIF_IT, 106, "#B8401A", ["#D85A2A", "#8A2A0A", "#E87A4A"], 21, max_w=400,
                       shadow="#FFFFFF", soff=(0.02, 0.03), angle=-35))
    out.append(ruled(300, 208, "OF SUMMER", "#1E7A9A", BEBAS, 46, 10, 50, 16, line="#1E7A9A", max_w=260))
    return finish(D, out, 67)


# ================================================================ 28. sip sip hooray! — a coconut cocktail with a paper umbrella
def coconut(D, cx, cy, r, seed):
    shell = ("#A8724A", "#6E4426", "#3A200E")
    out = [cast(D, cx + 12, cy + r * 0.92, r * 1.05, r * 0.16, color="#6A1A0A", strength=0.35, seed=seed)]
    body = blob_pts(cx, cy, r, r * 0.92, seed, 0.03, 24)
    out.append(painted(D, body, shell, seed, sdir=(0.6, 0.6), sk=0.18, angle=-60, n=int(r * 1.2), slen=(r * 0.1, r * 0.3), sw=(1, 2.4),
                       cols=["#C8925A", "#3A200E", "#8A5A32", "#D8A86A"], inkw=2.4, hi=0.35, curve=0.6))
    rnd = random.Random(seed)
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    fib = []
    for _ in range(int(r * 1.4)):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0.2, 1) * r
        x, y = cx + rr * math.cos(a), cy + rr * 0.92 * math.sin(a)
        L = rnd.uniform(6, 14)
        b = a + math.pi / 2 + rnd.uniform(-0.4, 0.4)
        fib.append(f'<path d="M {x:.1f} {y:.1f} l {L * math.cos(b):.1f} {L * math.sin(b):.1f}" stroke="{rnd.choice(["#3A200E", "#C8925A", "#8A5A32"])}" stroke-width="1.3" opacity="0.6"/>')
    out.append(f'<g {cid}>{"".join(fib)}</g>')
    # cut top: white flesh ring and the drink
    top_y = cy - r * 0.55
    rim_o = blob(cx, top_y, r * 0.78, r * 0.2, seed + 1, 0.02, 20)
    rim_i = blob(cx, top_y + 2, r * 0.64, r * 0.14, seed + 2, 0.02, 20)
    out.append(f'<path d="{rim_o}" fill="#FFFCF0" stroke="{INK}" stroke-width="2"/>')
    out.append(f'<path d="{rim_i}" fill="{D.lin([(0, "#FFE8A0"), (1, "#FFB84A")])}"/>')
    out.append(f'<path d="{rim_o}" fill="none" stroke="#6E4426" stroke-width="5" opacity="0.5"/>')
    out.append(taper([(cx - r * 0.5, top_y + 2), (cx - r * 0.1, top_y - r * 0.06)], 3, 1, "#FFFFFF", 0.8))
    return "".join(out), top_y


def paper_umbrella(D, x, y, ang, L, seed, cols=(SUN, PINK)):
    a = math.radians(ang)
    tip = (x + L * math.cos(a), y + L * math.sin(a))
    out = [pline([(x, y), tip], "#C8A06A", 3, seed, 1, 1)]
    cx, cy = tip
    can_r = L * 0.55
    nx, ny = -math.sin(a), math.cos(a)
    pts = []
    for k in range(9):
        t = -1 + 2 * k / 8
        pts.append((cx - math.cos(a) * can_r * 0.25 + nx * can_r * t + math.cos(a) * (0 if k % 2 else -can_r * 0.06), cy - math.sin(a) * can_r * 0.25 + ny * can_r * t + math.sin(a) * (0 if k % 2 else -can_r * 0.06)))
    apex = (cx + math.cos(a) * can_r * 0.35, cy + math.sin(a) * can_r * 0.35)
    for k in range(8):
        seg = [apex, pts[k], pts[k + 1]]
        out.append(painted(D, seg, cols[k % 2], seed + k, sk=0.1, n=2, inkw=1.4, inkop=0.6, hi=0.3))
    out.append(f'<circle cx="{apex[0]:.1f}" cy="{apex[1]:.1f}" r="3" fill="#C8A06A"/>')
    return "".join(out)


@design("sip-sip-hooray")
def sip_sip_hooray():
    D = Doc("sp")
    out = [f'<rect width="600" height="600" fill="#FF7A5A"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, 0, 600, 600), ["#FF9A7A", "#E85A3A", "#FFB090"], 4, n=180,
                       angle=-30, length=(40, 120), width=(3, 9), opacity=(0.15, 0.35), curve=0.2))
    # palm-leaf shadows falling across the wall
    for i, (bx, by, ang, L) in enumerate(((-20, 40, 30, 260), (620, 80, 150, 240), (-30, 420, -25, 220), (630, 470, -160, 230))):
        out.append(f'<g opacity="0.22">{frond(bx, by, ang, L, 70 + i, ["#9A2A1A"], droop=0.2, blade=0.32, spine="#9A2A1A")}</g>')
    out.append(soft_glow(D, 300, 380, 230, "#FFE0B0", 0.55))
    # table edge
    tb = "M -10 520 L 610 520 L 610 610 L -10 610 Z"
    out.append(f'<path d="{tb}" fill="#FFE0A8"/>' + stripes_in(D, tb, (0, 500, 600, 620), 90, [14, 14], [SUN[1], None], 5) + taper([(-10, 520), (610, 520)], 4, 4, "#C8804A", 0.6))
    shell, top_y = coconut(D, 300, 412, 132, 6)
    # straw & umbrella behind the rim
    out.append(taper([(330, top_y), (358, 258), (392, 240)], 12, 12, INK, 0.8) + taper([(330, top_y), (358, 258), (392, 240)], 9, 9, "#FFFFFF"))
    out.append(stripes_in(D, smooth_closed([(326, top_y), (334, top_y), (362, 262), (394, 246), (388, 234), (354, 254)]), (300, 150, 420, 340), 30, [10, 10], [PINK[1], None], 7))
    out.append(shell)
    out.append(paper_umbrella(D, 276, top_y + 4, -142, 112, 8))
    # pineapple wedge on the rim
    wedge = [(380, top_y - 4), (430, top_y - 62), (452, top_y - 52), (408, top_y + 6)]
    out.append(painted(D, wedge, ("#FFF4A0", "#FFE04A", "#C8A010"), 9, sk=0.15, angle=-50, n=6, inkw=1.8, hi=0.4))
    out.append(taper([(430, top_y - 62), (452, top_y - 52)], 8, 8, "#C8860A"))
    for k in range(3):
        out.append(leaf(D, "slim", 446 + k * 6, top_y - 74 - k * 4, 16, LEAF, 20 + k * 25, 10 + k, vein="#C8F0A0"))
    out.append(hibiscus(D, 214, 400, 46, PINK, 11, 20))
    out.append(leaf(D, "slim", 176, 438, 26, LEAF, -120, 12, vein="#C8F0A0"))
    out.append(lemon_wheel(D, 488, 506, 24, 13))
    out.append(f'<path d="{blob(118, 512, 34, 10, 14, 0.1, 12)}" fill="#C8804A" opacity="0.35"/>')
    out.append(sparkle(500, 300, 12, "#FFFFFF") + sparkle(96, 300, 10, "#FFFFFF"))
    out.append(letters(D, 300, 142, "sip sip", SERIF_IT, 108, "#FFFFFF", ["#FFFFFF", "#FFF0E0", "#FFE0D0"], 21, max_w=360,
                       shadow="#9A2A1A", soff=(0.025, 0.04), angle=-35))
    out.append(letters(D, 300, 228, "HOORAY!", BEBAS, 100, "#FFE04A", ["#FFF07A", "#F2B800", "#FFF6C0"], 22, ls=14, max_w=330,
                       shadow="#9A2A1A", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 68, "#6A1A0A", 0.6)


# ================================================================ 29. surf's up — a two-tone camper van with boards on the roof
def surfboard(D, x0, x1, y, w, pal, stripe, seed, rot_=0):
    L = x1 - x0
    pts = []
    for i in range(21):
        t = i / 20
        ww = w / 2 * (math.sin(math.pi * t) ** 0.55) * (1 - 0.15 * t)
        pts.append((x0 + L * t, y - ww))
    for i in range(20, -1, -1):
        t = i / 20
        ww = w / 2 * (math.sin(math.pi * t) ** 0.55) * (1 - 0.15 * t)
        pts.append((x0 + L * t, y + ww))
    pts = rot(pts, (x0 + x1) / 2, y, rot_)
    out = [painted(D, pts, pal, seed, sdir=(0.2, 1), sk=0.15, angle=rot_, n=20, inkw=2, hi=0.4)]
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    st = rot([(x0, y - w * 0.12), (x1, y - w * 0.12), (x1, y + w * 0.12), (x0, y + w * 0.12)], (x0 + x1) / 2, y, rot_)
    out.append(f'<g {cid}><path d="M ' + " L ".join(f"{a:.1f} {b:.1f}" for a, b in st) + f' Z" fill="{stripe}"/></g>')
    out.append(pline(rot([(x0 + 10, y), (x1 - 10, y)], (x0 + x1) / 2, y, rot_), pal[2], 1.2, seed, 0.5, 1))
    return "".join(out)


@design("surfs-up")
def surfs_up():
    D = Doc("su")
    out = [sky(D, [(0, "#2EB8F0"), (0.4, "#7ED8F8"), (0.6, "#D8F6FF")], 3, 400, ["#FFFFFF", "#5AC8F0", "#C8F0FF"], 50)]
    out.append(sun_disc(D, 510, 300, 34, ("#FFFCE0", "#FFE87A", "#FFB43A"), 3, glow_col="#FFF6C0", glow_r=3))
    out.append(sea(D, 350, 440, [(0, "#1EA8D0"), (1, "#3FD0D0")], 4, ["#9AF0EC", "#0E6E9A", "#FFFFFF"], 40, ticks=["#FFFFFF"]))
    out.append(palm(D, (60, 470), (88, 290), 5, [(-160, 0.9), (-130, 0.8), (-95, 0.7), (-60, 0.8), (-25, 0.9), (0, 0.85), (-195, 0.75)], L=96, width=16))
    out.append(palm(D, (540, 470), (520, 316), 6, [(-170, 0.85), (-135, 0.8), (-100, 0.7), (-65, 0.8), (-30, 0.9), (-5, 0.85), (20, 0.7)], L=86, width=14))
    rd = smooth_closed([(-20, 430), (620, 430), (620, 620), (-20, 620)])
    out.append(f'<path d="{rd}" fill="#F6D9A0"/>' + strokes(D.nid(), rd, (-20, 420, 620, 620), ["#FFF0CE", "#C9A066"], 7, n=60, angle=-3, length=(30, 80), width=(2, 5), opacity=(0.2, 0.45)))
    out.append(f'<path d="M -10 468 L 610 468 L 610 610 L -10 610 Z" fill="#6A6474"/>')
    out.append(strokes(D.nid(), "M -10 468 L 610 468 L 610 610 L -10 610 Z", (-60, 468, 610, 610), ["#8A8494", "#4A4454"], 8, n=60, angle=0, length=(30, 90), width=(2, 4), opacity=(0.2, 0.4)))
    for x in range(-10, 620, 80):
        out.append(taper([(x, 540), (x + 44, 540)], 5, 5, "#FFFFFF", 0.85))
    out.append(cast(D, 300, 512, 230, 14, color="#1A1424", strength=0.45))
    # van body (faces left)
    teal = ("#7AE8E0", "#1FB5B0", "#0E6E74")
    cream = ("#FFFFFF", "#FFF4DC", "#C8B898")
    body = poly_pts([(110, 300), (128, 262), (170, 248), (490, 248), (512, 262), (516, 300), (516, 470), (104, 470), (96, 430)], 22, 8, 0.6)
    bd = smooth_closed(body)
    out.append(painted(D, body, cream, 8, sdir=(0.4, 1), sk=0.08, angle=-90, n=40, inkw=0, hi=0.3, edge=False))
    cid = D.clip(f'<path d="{bd}"/>')
    lower = [(60, 520), (60, 380), (120, 380), (180, 330), (240, 380), (560, 380), (560, 520)]
    out.append(f'<g {cid}>' + painted(D, lower, teal, 9, sdir=(0.4, 1), sk=0.1, angle=0, n=50, inkw=1.8, inkop=0.6, hi=0.3) +
               f'<path d="{bd}" fill="{D.lin([(0, "#FFFFFF", 0.2), (0.5, "#FFFFFF", 0), (1, "#000000", 0.2)])}"/></g>')
    out.append(ink(bd, INK, 2.4, 10, 2, 0.8))
    # windows
    for i, (x0, x1) in enumerate(((132, 196), (226, 300), (316, 390), (406, 480))):
        wp = poly_pts([(x0, 266), (x1, 266), (x1, 324), (x0, 324)], 14, 11 + i, 0.4)
        out.append(painted(D, wp, ("#E8FAFF", "#9AD8F0", "#3A88B0"), 11 + i, sdir=(1, 0.5), sk=0.2, angle=-50, n=6, inkw=2, hi=0.5))
        out.append(taper([(x0 + 10, 316), (x0 + 28, 274)], 5, 2, "#FFFFFF", 0.7))
    # windshield side, door seam, handle, bumper, light
    out.append(pline([(214, 334), (214, 462)], teal[2], 1.8, 20, 0.6, 1) + pline([(306, 334), (306, 462)], teal[2], 1.8, 21, 0.6, 1))
    out.append(taper([(282, 346), (298, 346)], 5, 5, "#E8E4F0") + taper([(96, 456), (130, 456)], 10, 10, "#E8E4F0") + taper([(486, 456), (522, 456)], 10, 10, "#E8E4F0"))
    out.append(f'<circle cx="112" cy="388" r="11" fill="#FFF6C0" stroke="{INK}" stroke-width="2"/>' + soft_glow(D, 110, 388, 28, "#FFF6C0", 0.5))
    # little daisy decal
    out.append(daisy(D, 440, 410, 18, 22, n=8, petal=("#FFFFFF", "#FFFFFF", "#D8C8C8"), center=SUN))
    out.append(daisy(D, 470, 432, 11, 23, n=7, petal=("#FFE0F0", "#FFB0D0", "#C8507A"), center=SUN))
    # wheels
    for x in (180, 430):
        out.append(f'<path d="{blob(x, 462, 54, 40, x, 0.02, 14)}" fill="#3A3444"/>')
        out.append(painted(D, blob_pts(x, 470, 42, 42, x, 0.01, 18), ("#5A5466", "#2A2430", "#0A080E"), x, sk=0.15, n=8, inkw=2, hi=0.2))
        out.append(painted(D, blob_pts(x, 470, 22, 22, x + 1, 0.02, 14), ("#FFFFFF", "#F4ECE0", "#B8A890"), x + 1, sk=0.2, n=3, inkw=1.6, hi=0.5))
        out.append(f'<circle cx="{x}" cy="470" r="6" fill="{teal[1]}"/>')
    # roof rack & boards
    for x in (190, 420):
        out.append(pline([(x, 248), (x, 232)], "#4A4454", 4, x, 1, 1))
    out.append(taper([(150, 232), (470, 232)], 6, 6, "#4A4454"))
    out.append(surfboard(D, 96, 470, 216, 36, ("#FFE27A", "#FFC21A", "#C8860A"), CORAL[1], 24, -2))
    out.append(surfboard(D, 150, 540, 196, 34, ("#FFB0D0", "#FF5FA2", "#B82A6A"), "#FFFFFF", 25, 1))
    out.append(pline([(250, 200), (252, 240)], "#4A4454", 2, 26, 0.9, 1) + pline([(380, 196), (382, 238)], "#4A4454", 2, 27, 0.9, 1))
    out.append(letters(D, 250, 148, "surf's", SERIF_IT, 112, "#FFFFFF", ["#FFFFFF", "#E8FAFF", "#FFF4D8"], 31, max_w=310,
                       shadow="#0E4E7A", soff=(0.025, 0.04), angle=-35))
    out.append(letters(D, 474, 150, "UP", BEBAS, 124, "#FFE04A", ["#FFF07A", "#F2B800", "#FFF6C0"], 32, ls=6, max_w=120,
                       shadow="#0E4E7A", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 69)


# ================================================================ 30. go with the flow — a sea turtle over the reef
def turtle(D, cx, cy, s, seed, rot_=-20):
    shell = ("#B8C85A", "#6E8A3A", "#34481A")
    skin = ("#C8E0B0", "#8AB07A", "#4A6A3A")
    def P(x, y):
        return (cx + x * s, cy + y * s)
    out = [f'<g transform="rotate({rot_} {cx} {cy})">']
    flips = [([P(-0.3, -0.42), P(-0.6, -0.95), P(-0.34, -1.02), P(0.0, -0.5)], -60), ([P(-0.3, 0.42), P(-0.66, 0.92), P(-0.38, 0.98), P(0.0, 0.5)], 60),
             ([P(0.5, -0.32), P(0.82, -0.56), P(0.86, -0.38), P(0.62, -0.18)], -20), ([P(0.5, 0.32), P(0.82, 0.56), P(0.86, 0.38), P(0.62, 0.18)], 20)]
    for i, (pts, a) in enumerate(flips):
        out.append(painted(D, pts, skin, seed + i, sk=0.15, angle=a, n=8, inkw=2, hi=0.35))
    head = blob_pts(*P(-0.92, 0), 0.24 * s, 0.19 * s, seed + 5, 0.04, 14)
    out.append(painted(D, head, skin, seed + 5, sk=0.15, angle=0, n=6, inkw=2, hi=0.4))
    hx, hy = P(-1.0, -0.06)
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{s * 0.035:.1f}" fill="#1A1A22"/><circle cx="{hx - 1:.1f}" cy="{hy - 1.5:.1f}" r="{s * 0.012:.1f}" fill="#FFFFFF"/>')
    out.append(pline([P(-1.12, 0.04), P(-1.02, 0.08), P(-0.94, 0.06)], "#2A3A1A", 2, seed, 0.9, 1))
    body = blob_pts(cx, cy, 0.72 * s, 0.56 * s, seed + 6, 0.03, 24)
    out.append(painted(D, body, shell, seed + 6, sdir=(0.4, 0.8), sk=0.15, angle=0, n=20, inkw=2.6, hi=0.35))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    sc = []
    cells = [(0, 0, 0.2), (-0.36, 0, 0.17), (0.36, 0, 0.17), (-0.18, -0.3, 0.16), (0.18, -0.3, 0.16), (-0.18, 0.3, 0.16), (0.18, 0.3, 0.16)]
    rnd = random.Random(seed)
    for k, (x, y, r_) in enumerate(cells):
        pts = [(P(x, y)[0] + r_ * s * math.cos(math.radians(a + 30)), P(x, y)[1] + r_ * s * 0.9 * math.sin(math.radians(a + 30))) for a in range(0, 360, 60)]
        sc.append(f'<path d="{smooth_closed(jitter(pts, seed + k, 1.5))}" fill="{rnd.choice(["#C8A85A", "#A8B84A", "#D8B860"])}" stroke="#34481A" stroke-width="2.2" opacity="0.9"/>')
        sc.append(f'<path d="{blob(P(x, y)[0] - r_ * s * 0.25, P(x, y)[1] - r_ * s * 0.25, r_ * s * 0.35, r_ * s * 0.25, seed + k, 0.1, 8)}" fill="#FFF6C0" opacity="0.4"/>')
    for k in range(18):
        a = math.radians(k * 20)
        x, y = cx + 0.66 * s * math.cos(a), cy + 0.5 * s * math.sin(a)
        sc.append(f'<path d="M {x:.1f} {y:.1f} L {cx + 0.78 * s * math.cos(a):.1f} {cy + 0.62 * s * math.sin(a):.1f}" stroke="#34481A" stroke-width="1.6" opacity="0.6"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append("</g>")
    return "".join(out)


def coral(D, x, base, h, seed, pal, branches=5):
    rnd = random.Random(seed)
    out = []
    def br(x0, y0, ang, L, w, depth):
        a = math.radians(ang)
        x1, y1 = x0 + L * math.cos(a), y0 + L * math.sin(a)
        mx, my = (x0 + x1) / 2 + rnd.uniform(-4, 4), (y0 + y1) / 2
        out.append(taper([(x0, y0), (mx, my), (x1, y1)], w, w * 0.7, pal[1]))
        out.append(taper([(x0 - w * 0.2, y0), (mx - w * 0.2, my), (x1 - w * 0.2, y1)], w * 0.3, w * 0.2, pal[0], 0.7))
        if depth > 0:
            for d in (-1, 1):
                br(x1, y1, ang + d * rnd.uniform(18, 34), L * rnd.uniform(0.6, 0.8), w * 0.75, depth - 1)
        else:
            out.append(f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="{w * 0.55:.1f}" fill="{pal[0]}"/>')
    br(x, base, -90 + rnd.uniform(-10, 10), h * 0.4, max(8, h * 0.1), 3)
    return "".join(out)


@design("go-with-the-flow")
def go_with_the_flow():
    D = Doc("gf")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#7AE8E8"), (0.35, "#2EB8D0"), (0.75, "#1A78B0"), (1, "#14508A")])}"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, 0, 600, 600), ["#9AF0F0", "#1A6AA0", "#5AD0E0"], 4, n=160,
                       angle=-6, length=(40, 140), width=(3, 9), opacity=(0.12, 0.3), curve=0.3))
    # sun rays from the surface
    for k, (x0, w) in enumerate(((120, 40), (230, 60), (360, 40), (470, 70))):
        out.append(f'<path d="M {x0} -10 L {x0 + w} -10 L {x0 + w + 120} 620 L {x0 + 60} 620 Z" fill="#FFFFFF" opacity="0.08"/>')
    out.append(caustics(D, "M -10 -10 L 610 -10 L 610 70 L -10 70 Z", (0, 0, 600, 70), 5, "#FFFFFF", 40, 0.3, 1.6))
    # sandy floor with reef
    fl = ridge([(-20, 520), (150, 506), (330, 520), (480, 508), (620, 516)], 6, 6)
    out.append(hill(D, fl, 620, ("#FFE8B8", "#E8C88A", "#B8945A"), 6, angle=-3, inkw=1.4))
    out.append(coral(D, 80, 540, 150, 7, ("#FF9AC0", "#FF5FA2", "#B82A6A")))
    out.append(coral(D, 520, 534, 160, 8, ("#FFC08A", "#FF8A3A", "#C0520E")))
    out.append(coral(D, 150, 548, 90, 9, ("#C8A0F0", "#8A5AD0", "#4A2A8A")))
    for i, x in enumerate((230, 380, 446)):
        pts = [(x + 10 * math.sin(t * 2 + i), 540 - t * 30) for t in range(5)]
        out.append(taper(pts, 10, 2, LEAF[1]) + taper([(px + 12, py + 6) for px, py in pts[:4]], 8, 2, LEAF[2], 0.8))
    for i, (x, y, r_) in enumerate(((300, 556, 22), (440, 560, 16))):
        out.append(f'<path d="{blob(x, y, r_, r_ * 0.6, i, 0.1, 12)}" fill="{["#FFE04A", "#FF6F59"][i]}"/>' + specks(i, (x - r_, y - r_ * 0.5, x + r_, y + r_ * 0.4), ["#FFFFFF"], 8, (1, 2)))
    out.append(starfish(D, 360, 566, 14, SUN, 10, 10))
    # bubbles
    rnd = random.Random(11)
    for i in range(22):
        x, y, r_ = rnd.uniform(60, 560), rnd.uniform(230, 470), rnd.uniform(3, 9)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r_:.1f}" fill="#FFFFFF" fill-opacity="0.15" stroke="#FFFFFF" stroke-width="1.6" opacity="0.8"/><circle cx="{x - r_ * 0.35:.1f}" cy="{y - r_ * 0.35:.1f}" r="{r_ * 0.25:.1f}" fill="#FFFFFF"/>')
    # a school of little fish
    for i, (x, y) in enumerate(((470, 250), (500, 268), (482, 290), (520, 246), (450, 278))):
        out.append(painted(D, [(x - 14, y), (x - 4, y - 8), (x + 10, y - 4), (x + 18, y - 9), (x + 18, y + 9), (x + 10, y + 4), (x - 4, y + 8)], SUN, 40 + i, sk=0.15, n=2, inkw=1.4, hi=0.4)
                   + f'<circle cx="{x - 8}" cy="{y - 2}" r="1.6" fill="#1A1A22"/>')
    out.append(turtle(D, 290, 360, 150, 12, -18))
    out.append(letters(D, 300, 126, "go with the", SERIF_IT, 92, "#FFFFFF", ["#FFFFFF", "#E0FFFA", "#C8F4F0"], 21, max_w=420,
                       shadow="#0A4A6A", soff=(0.025, 0.04), angle=-35))
    out.append(letters(D, 300, 216, "FLOW", BEBAS, 100, "#FFE04A", ["#FFF07A", "#F2B800", "#FFF6C0"], 22, ls=26, max_w=300,
                       shadow="#0A3A5A", angle=-78, hi="#FFFFFF"))
    return finish(D, out, 70, "#0A3A5A", 0.5)


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
