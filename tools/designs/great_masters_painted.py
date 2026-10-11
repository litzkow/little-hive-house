"""Great Masters, hand-painted edition: 30 magnets of the world's most loved public-domain paintings.

Each magnet is our own painted interpretation of one famous painting (all made before 1931, by painters who died
long ago), rendered in that master's own technique: Van Gogh's impasto as thousands of directional, ridged dashes;
Monet's broken dabs of light; Hokusai and Hiroshige's flat woodblock colour with bokashi gradients and key-block
line; Klimt's gold mosaic; Vermeer's glazed window light; Seurat's dots; and so on. Every painting hangs in its own
painted gallery setting (gilded frames, linen mats, a silk scroll mount, a dark museum wall) with a small museum
label in a refined face. Canvas weave, varnish sheen and the frame's cast shadow make each one read as an object.

Run from tools/designs:  python3 great_masters_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_painted import Doc
from fall_gouache_a import mix as _mix, bbox, shift, painted, pline, taper, letters, label, blooms, dab_crown, cast, soft_glow
from gouache import blob, blob_pts, ink, jitter, smooth_closed, smooth_open, strokes, wash
from paint import rough

COL = "great-masters"
INK = "#3A2418"

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def _full(c):
    c = c.lstrip("#")
    return "#" + ("".join(ch * 2 for ch in c) if len(c) == 3 else c)


def mix(c1, c2, t):
    return _mix(_full(c1), _full(c2), max(0.0, min(1.0, t)))


def lt(c, t):
    return mix(c, "#FFFFFF", t)


def dk(c, t):
    return mix(c, "#000000", t)


def f1(v):
    return f"{v:.1f}"


def pd(pts, close=True):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if close else "")


def ell_pts(cx, cy, rx, ry, a0=0, a1=360, n=24, rot=0):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def inside(pt, poly):
    """Even-odd point in polygon."""
    x, y = pt
    c = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi:
            c = not c
        j = i
    return c


def wpick(rnd, items):
    """items: [(weight, value), ...]"""
    t = rnd.uniform(0, sum(w for w, _ in items))
    for w, v in items:
        t -= w
        if t <= 0:
            return v
    return items[-1][1]


# ================================================================ brush engines
class Brush:
    """Collects painted marks (dashes and dots) and writes them compactly, in painting order."""

    def __init__(self):
        self.marks = []

    def dash(self, pts, col, w, op=1.0):
        """A round-capped brush dash through 2-4 points."""
        if len(pts) == 2:
            d = f"M{pts[0][0]:.0f} {pts[0][1]:.0f}L{pts[1][0]:.0f} {pts[1][1]:.0f}"
        elif len(pts) == 3:
            (x0, y0), (x1, y1), (x2, y2) = pts
            cx, cy = 2 * x1 - (x0 + x2) / 2, 2 * y1 - (y0 + y2) / 2
            d = f"M{x0:.0f} {y0:.0f}Q{cx:.0f} {cy:.0f} {x2:.0f} {y2:.0f}"
        else:
            (x0, y0), (x1, y1), (x2, y2), (x3, y3) = pts[0], pts[len(pts) // 3], pts[2 * len(pts) // 3], pts[-1]
            # cubic through 4 points (approximate: control points from Catmull-Rom style tangents)
            c1 = (x1 + (x1 - x0) * 0.0, y1)
            d = f"M{x0:.0f} {y0:.0f}C{2 * x1 - (x0 + x2) / 2:.0f} {2 * y1 - (y0 + y2) / 2:.0f} {2 * x2 - (x1 + x3) / 2:.0f} {2 * y2 - (y1 + y3) / 2:.0f} {x3:.0f} {y3:.0f}"
        self.marks.append(("d", col, w, op, d))

    def dot(self, x, y, r, col, op=1.0):
        self.marks.append(("o", col, r, op, (x, y)))

    def render(self, cap="round"):
        parts = []
        for kind, col, w, op, d in self.marks:
            o = f' opacity="{op:.2f}"' if op < 1 else ""
            if kind == "o":
                parts.append(f'<circle cx="{d[0]:.1f}" cy="{d[1]:.1f}" r="{w:.1f}" fill="{col}"{o}/>')
            else:
                parts.append(f'<path d="{d}" stroke="{col}" stroke-width="{w:.1f}"{o}/>')
        self.marks = []
        return f'<g fill="none" stroke-linecap="{cap}" stroke-linejoin="round">' + "".join(parts) + "</g>"


def follow(field, x, y, L, steps=3, sign=1):
    """Integrate a direction field from (x, y) for length L -> list of points."""
    pts = [(x, y)]
    h = L / steps
    for _ in range(steps):
        a = field(x, y)
        x, y = x + sign * h * math.cos(a), y + sign * h * math.sin(a)
        pts.append((x, y))
    return pts


def impasto(B, field, region, n, colfn, seed, L=(9, 16), W=(3.2, 5.0), ridge=0.45, light=(-0.7, -0.7), steps=2,
            jit=0.15, op=1.0, center=False):
    """Van Gogh style: n thick dashes laid along `field`, sampled inside `region` (fn(x,y)->bool or poly).
    colfn(x, y, rnd) -> colour. A thinner, lighter ridge on part of the strokes reads as raised paint."""
    rnd = random.Random(seed)
    test = region if callable(region) else (lambda x, y: inside((x, y), region))
    xs = [p[0] for p in region] if not callable(region) else None
    box = bbox(region) if not callable(region) else (0, 0, 600, 600)
    tries = 0
    k = 0
    ridges = []
    while k < n and tries < n * 30:
        tries += 1
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        if not test(x, y):
            continue
        k += 1
        Ls = rnd.uniform(*L)
        fa = lambda xx, yy: field(xx, yy) + rnd.uniform(-jit, jit)
        if center:
            pts = follow(fa, x, y, Ls / 2, max(1, steps // 2), -1)[::-1] + follow(fa, x, y, Ls / 2, max(1, steps // 2))[1:]
        else:
            pts = follow(fa, x, y, Ls, steps)
        w = rnd.uniform(*W)
        col = colfn(x, y, rnd)
        B.dash(pts, col, w, op)
        if ridge and rnd.random() < ridge:
            ox, oy = light[0] * w * 0.22, light[1] * w * 0.22
            rp = [(px + ox, py + oy) for px, py in pts]
            ridges.append((rp[:max(2, len(rp) - 1)], lt(col, 0.42), w * 0.32))
    for rp, c, w in ridges:
        B.dash(rp, c, w, 0.55)


def dabs(B, region, n, colfn, seed, L=(6, 12), W=(3, 6), angle=0, spread=25, op=(0.7, 1.0)):
    """Impressionist dabs: short, broken, mostly straight touches at a dominant angle."""
    rnd = random.Random(seed)
    test = region if callable(region) else (lambda x, y: inside((x, y), region))
    box = bbox(region) if not callable(region) else (0, 0, 600, 600)
    k = tries = 0
    while k < n and tries < n * 30:
        tries += 1
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        if not test(x, y):
            continue
        k += 1
        a = math.radians((angle(x, y) if callable(angle) else angle) + rnd.uniform(-spread, spread))
        Ls = rnd.uniform(*L)
        dx, dy = Ls / 2 * math.cos(a), Ls / 2 * math.sin(a)
        B.dash([(x - dx, y - dy), (x + dx, y + dy)], colfn(x, y, rnd), rnd.uniform(*W), round(rnd.uniform(*op), 2))


def stipple(B, region, n, colfn, seed, r=(1.6, 2.4), op=1.0):
    """Seurat: pure dots of colour laid side by side."""
    rnd = random.Random(seed)
    test = region if callable(region) else (lambda x, y: inside((x, y), region))
    box = bbox(region) if not callable(region) else (0, 0, 600, 600)
    k = tries = 0
    while k < n and tries < n * 30:
        tries += 1
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        if not test(x, y):
            continue
        k += 1
        B.dot(x, y, rnd.uniform(*r), colfn(x, y, rnd), op)


def under(D, box, cols, n, seed, r=(30, 80), op=(0.25, 0.55), squash=0.6):
    """Soft underpainting: big overlapping blobs of the scene's colours, so dabs sit on a living ground."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for i in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        c = cols(x, y, rnd) if callable(cols) else rnd.choice(cols)
        rr = rnd.uniform(*r)
        out.append(f'<path d="{blob(x, y, rr, rr * squash, rnd.randint(0, 9999), 0.18, 12, rnd.uniform(-20, 20))}" fill="{c}" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


# ================================================================ gallery settings
def canvas_weave(D, box, op=0.07, step=4):
    x0, y0, x1, y1 = box
    pat = D.pattern(step, step, f'<path d="M0 0.5H{step}M0.5 0V{step}" stroke="#000" stroke-width="0.7" opacity="0.6"/>'
                                f'<path d="M0 2.3H{step}M2.3 0V{step}" stroke="#FFF" stroke-width="0.6" opacity="0.5"/>')
    return f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{pat}" opacity="{op}"/>'


def varnish(D, box, sheen=0.16, vignette=0.28, lip=10, lipop=0.5):
    """Varnish sheen from the upper left, a darker edge, and the frame's cast shadow on the canvas."""
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    out = [f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.rad([(0, "#FFFFFF", sheen), (1, "#FFFFFF", 0)], 0.22, 0.12, 0.6)}"/>',
           f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.rad([(0, "#000", 0), (0.62, "#000", 0), (1, "#000", vignette)], 0.5, 0.5, 0.75)}"/>']
    if lip:
        out.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{lip}" fill="{D.lin([(0, "#000", lipop), (1, "#000", 0)])}"/>')
        out.append(f'<rect x="{x0}" y="{y0}" width="{lip}" height="{H}" fill="{D.lin([(0, "#000", lipop * 0.8), (1, "#000", 0)], 0, 0, 1, 0)}"/>')
        out.append(f'<rect x="{x0}" y="{y1 - lip * 0.5}" width="{W}" height="{lip * 0.5}" fill="{D.lin([(0, "#000", 0), (1, "#000", lipop * 0.3)])}"/>')
    return "".join(out)


def ring_side(D, box, t0, t1, stops, side_light=(1.0, 0.82, 0.55, 0.68)):
    """One concentric band of a moulding, profile `stops` [(0..1 across band from outside in, colour)], mitred,
    each side tinted for light from the upper left (top, left, bottom, right)."""
    x0, y0, x1, y1 = box
    sides = [
        ([(x0 + t0, y0 + t0), (x1 - t0, y0 + t0), (x1 - t1, y0 + t1), (x0 + t1, y0 + t1)], (0, y0 + t0, 0, y0 + t1)),
        ([(x0 + t0, y0 + t0), (x0 + t1, y0 + t1), (x0 + t1, y1 - t1), (x0 + t0, y1 - t0)], (x0 + t0, 0, x0 + t1, 0)),
        ([(x0 + t0, y1 - t0), (x0 + t1, y1 - t1), (x1 - t1, y1 - t1), (x1 - t0, y1 - t0)], (0, y1 - t0, 0, y1 - t1)),
        ([(x1 - t0, y0 + t0), (x1 - t0, y1 - t0), (x1 - t1, y1 - t1), (x1 - t1, y0 + t1)], (x1 - t0, 0, x1 - t1, 0)),
    ]
    out = []
    for k, (poly, (gx0, gy0, gx1, gy1)) in enumerate(sides):
        f = side_light[k]
        st = [(o, mix(c, "#000000", 1 - f) if f < 1 else mix(c, "#FFFFFF", f - 1)) for o, c in stops]
        g = D.lin(st, gx0, gy0, gx1, gy1, "userSpaceOnUse")
        out.append(f'<path d="{pd(poly)}" fill="{g}"/>')
    return "".join(out)


GOLD = ("#FFF1B8", "#E8C060", "#B98A30", "#7A5418", "#3E2808")


def gilt_frame(D, box, w, seed, style="ornate", gold=GOLD):
    """Gilded frame of width w around box (the sight opening): roll, cove, bead row, flat, sight edge;
    ornate style adds acanthus leaves along the roll and shell cartouches at the corners."""
    x0, y0, x1, y1 = box
    ob = (x0 - w, y0 - w, x1 + w, y1 + w)
    hl, base, mid, dark, deep = gold
    out = []
    # cast shadow of the frame on the wall
    out.append(f'<rect x="{ob[0] + 4}" y="{ob[1] + 8}" width="{ob[2] - ob[0]}" height="{ob[3] - ob[1]}" rx="3" fill="#1A0E04" opacity="0.28"/>')
    out.append(f'<rect x="{ob[0] + 2}" y="{ob[1] + 4}" width="{ob[2] - ob[0]}" height="{ob[3] - ob[1]}" rx="2" fill="#1A0E04" opacity="0.22"/>')
    prof = [
        (0.00, 0.06, [(0, deep), (0.5, dark), (1, mid)]),
        (0.06, 0.42, [(0, mid), (0.25, hl), (0.5, base), (0.8, mid), (1, dark)]),           # outer roll
        (0.42, 0.52, [(0, deep), (0.6, dark), (1, mid)]),                                       # cove
        (0.52, 0.66, [(0, base), (0.4, hl), (1, mid)]),                                         # bead bed
        (0.66, 0.90, [(0, mid), (0.5, base), (1, mid)]),                                        # flat (matte)
        (0.90, 0.96, [(0, hl), (1, base)]),                                                     # sight edge
        (0.96, 1.00, [(0, dark), (1, deep)]),
    ]
    for a, b, st in prof:
        out.append(ring_side(D, ob, a * w, b * w, st))
    rnd = random.Random(seed)
    # bead row
    t = 0.59 * w
    bx0, by0, bx1, by1 = ob[0] + t, ob[1] + t, ob[2] - t, ob[3] - t
    br = max(1.6, w * 0.055)
    beads = []
    step = br * 2.6

    def bead(x, y, f):
        beads.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{br:.1f}" fill="{mix(base, "#000", 1 - f) if f < 1 else base}"/>'
                     f'<circle cx="{x - br * 0.35:.1f}" cy="{y - br * 0.35:.1f}" r="{br * 0.45:.1f}" fill="{hl}" opacity="{0.9 * f:.2f}"/>')
    n = int((bx1 - bx0) / step)
    for i in range(n + 1):
        x = bx0 + (bx1 - bx0) * i / n
        bead(x, by0, 1.0)
        bead(x, by1, 0.6)
    n = int((by1 - by0) / step)
    for i in range(1, n):
        y = by0 + (by1 - by0) * i / n
        bead(bx0, y, 0.85)
        bead(bx1, y, 0.65)
    out.append("".join(beads))
    if style == "ornate":
        # acanthus leaves on the outer roll
        tt = 0.24 * w
        lx0, ly0, lx1, ly1 = ob[0] + tt, ob[1] + tt, ob[2] - tt, ob[3] - tt
        leaves = []
        s = w * 0.17

        def leafm(x, y, ang, f):
            c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            pts = [(-s * 1.3, 0), (-s * 0.4, -s * 0.8), (s * 0.5, -s * 0.55), (s * 1.3, 0), (s * 0.5, s * 0.55), (-s * 0.4, s * 0.8)]
            P = [(x + px * c - py * sn, y + px * sn + py * c) for px, py in pts]
            col = mix(mid, "#000", 1 - f)
            leaves.append(f'<path d="{smooth_closed(P)}" fill="{col}" opacity="0.55"/>')
            leaves.append(f'<path d="M{P[0][0]:.1f} {P[0][1]:.1f}Q{x:.1f} {y:.1f} {P[3][0]:.1f} {P[3][1]:.1f}" stroke="{hl}" stroke-width="{max(1, s * 0.18):.1f}" fill="none" opacity="{0.75 * f:.2f}"/>')
        step2 = s * 3.0
        for side, (ax, ay, bx, by, ang, f) in enumerate([(lx0, ly0, lx1, ly0, 0, 1.0), (lx0, ly1, lx1, ly1, 0, 0.6),
                                                         (lx0, ly0, lx0, ly1, 90, 0.85), (lx1, ly0, lx1, ly1, 90, 0.65)]):
            L = math.hypot(bx - ax, by - ay)
            m = int(L / step2)
            for i in range(1, m):
                tq = i / m
                leafm(ax + (bx - ax) * tq, ay + (by - ay) * tq, ang + (20 if i % 2 else -20), f)
        out.append("".join(leaves))
        # corner shells
        for cx, cy, f in ((ob[0] + w * 0.36, ob[1] + w * 0.36, 1.0), (ob[2] - w * 0.36, ob[1] + w * 0.36, 0.8),
                          (ob[0] + w * 0.36, ob[3] - w * 0.36, 0.75), (ob[2] - w * 0.36, ob[3] - w * 0.36, 0.55)):
            r = w * 0.46
            out.append(f'<path d="{blob(cx, cy, r, r, seed + int(cx), 0.08, 14)}" fill="{D.rad([(0, hl), (0.5, base), (1, dark)], 0.35, 0.3, 0.75)}" opacity="{0.6 + 0.4 * f:.2f}"/>')
            for k in range(7):
                a = math.radians(-90 + (k - 3) * 26) if True else 0
                out.append(f'<path d="M{cx:.1f} {cy + r * 0.45:.1f}L{cx + r * 0.85 * math.cos(a):.1f} {cy + r * 0.85 * math.sin(a) + r * 0.2:.1f}" stroke="{deep}" stroke-width="{max(1.1, w * 0.035):.1f}" opacity="0.45"/>')
            out.append(f'<circle cx="{cx - r * 0.25:.1f}" cy="{cy - r * 0.25:.1f}" r="{r * 0.22:.1f}" fill="#FFFBE0" opacity="{0.55 * f:.2f}"/>')
    # gilding wear: dry-brush specks and rubbed bole showing through
    band = f"M{ob[0]} {ob[1]}H{ob[2]}V{ob[3]}H{ob[0]}Z M{x0} {y0}V{y1}H{x1}V{y0}Z"
    out.append(strokes(D.nid(), band, ob, [hl, "#FFFFFF", deep, "#8A3A1A"], seed + 5, n=int(w * 12), angle=0, length=(6, 22),
                       width=(0.6, 1.6), opacity=(0.12, 0.4), curve=0.1, clip_extra=' clip-rule="evenodd"'))
    return "".join(out)


def simple_frame(D, box, w, cols, seed, light=(1.0, 0.8, 0.5, 0.65)):
    """Plain moulding (black lacquer, walnut, silver...). cols = (hl, base, dark)."""
    hl, base, dark = cols
    ob = (box[0] - w, box[1] - w, box[2] + w, box[3] + w)
    out = [f'<rect x="{ob[0] + 3}" y="{ob[1] + 7}" width="{ob[2] - ob[0]}" height="{ob[3] - ob[1]}" fill="#0A0604" opacity="0.3"/>']
    out.append(ring_side(D, ob, 0, w * 0.55, [(0, dark), (0.35, hl), (1, base)], light))
    out.append(ring_side(D, ob, w * 0.55, w * 0.85, [(0, base), (1, dark)], light))
    out.append(ring_side(D, ob, w * 0.85, w, [(0, hl), (1, dark)], light))
    return "".join(out)


def mat_board(D, box, bevel, col, seed, wall=None):
    """Linen/paper mat filling the whole magnet with a bevelled window cut around box."""
    x0, y0, x1, y1 = box
    out = [f'<rect width="600" height="600" fill="{col}"/>',
           f'<rect width="600" height="600" fill="{D.rad([(0, lt(col, 0.25), 0.7), (1, dk(col, 0.12), 0.0)], 0.4, 0.3, 0.8)}"/>',
           blooms(seed, [dk(col, 0.1), lt(col, 0.3)], 8, (0, 0, 600, 600), (60, 160), (0.04, 0.09))]
    rnd = random.Random(seed)
    fib = "".join(f'<path d="M{rnd.uniform(0, 600):.0f} {rnd.uniform(0, 600):.0f}l{rnd.uniform(-9, 9):.1f} {rnd.uniform(-3, 3):.1f}"/>' for _ in range(160))
    out.append(f'<g stroke="{dk(col, 0.3)}" stroke-width="0.8" opacity="0.18">{fib}</g>')
    ob = (x0 - bevel, y0 - bevel, x1 + bevel, y1 + bevel)
    out.append(ring_side(D, ob, 0, bevel, [(0, "#FFFFFF"), (1, lt(col, 0.4))], (1.02, 0.97, 0.78, 0.86)))
    out.append(f'<path d="M{ob[0]} {ob[1]}H{ob[2]}V{ob[3]}H{ob[0]}Z" fill="none" stroke="{dk(col, 0.25)}" stroke-width="1" opacity="0.5"/>')
    return "".join(out)


def wall(D, col, seed, light=(0.5, 0.25), strength=0.25):
    """A gallery wall: painted plaster with a soft spotlight pool from above."""
    out = [f'<rect width="600" height="600" fill="{col}"/>',
           f'<rect width="600" height="600" fill="{D.rad([(0, lt(col, 0.35), 0.9), (0.55, col, 0.2), (1, dk(col, 0.35), 0.9)], light[0], light[1], 0.85)}"/>',
           blooms(seed, [dk(col, 0.2), lt(col, 0.2)], 9, (0, 0, 600, 600), (60, 170), (0.05, 0.1))]
    out.append(strokes(D.nid(), "M-10 -10H610V610H-10Z", (-40, -10, 600, 610), [dk(col, 0.15), lt(col, 0.12)], seed + 3, n=90,
                       angle=-60, length=(40, 120), width=(4, 12), opacity=(0.04, 0.12), curve=0.2))
    return "".join(out)


def museum_label(D, cy, title, byline, ink_c="#2A1E14", sub_c=None, title_font=SERIF_IT, by_font=CINZEL, ts=27, bs=17,
                 max_w=420, gap=26, ls=2.4, cx=300):
    """Two-line museum label: painting title (refined italic) over ARTIST · YEAR (small caps serif)."""
    sub_c = sub_c or mix(ink_c, "#FFFFFF", 0.25)
    out = [label(cx, cy, title, title_font, ts, ink_c, 0, max_w)]
    out.append(label(cx, cy + gap, byline, by_font, bs, sub_c, ls, max_w))
    return "".join(out)


def plaque(D, cx, cy, w, h, title, byline, seed, gold=GOLD, ink_c="#2A1A08", ts=21, bs=16):
    """A small engraved brass plaque (title + artist/year)."""
    hl, base, mid, dark, deep = gold
    x0, y0 = cx - w / 2, cy - h / 2
    out = [f'<rect x="{x0 + 2}" y="{y0 + 3}" width="{w}" height="{h}" rx="3" fill="#000" opacity="0.35"/>',
           f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="3" fill="{D.lin([(0, hl), (0.45, base), (1, mid)], 0, 0, 0.3, 1)}"/>',
           f'<rect x="{x0 + 3}" y="{y0 + 3}" width="{w - 6}" height="{h - 6}" rx="2" fill="none" stroke="{dark}" stroke-width="1.2" opacity="0.6"/>',
           f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="3" fill="none" stroke="{deep}" stroke-width="1" opacity="0.6"/>']
    for sx in (x0 + 8, x0 + w - 8):
        out.append(f'<circle cx="{sx}" cy="{cy}" r="2.6" fill="{mid}" stroke="{deep}" stroke-width="0.8"/><path d="M{sx - 1.8} {cy}h3.6" stroke="{deep}" stroke-width="0.8"/>')
    if byline:
        out.append(label(cx, cy - 2, title, SERIF_IT, ts, ink_c, 0, w - 34))
        out.append(label(cx, cy + 17, byline, CINZEL, bs, mix(ink_c, "#000", 0.1), 1.6, w - 34))
    else:
        out.append(label(cx, cy + ts * 0.34, title, CINZEL, ts, ink_c, 1.6, w - 34))
    return "".join(out)


def finish(D, out, seed, color="#2A1A10", op=0.8):
    from fall_painted import grain
    out.append(grain(seed, color, 300, op=0.08 * op))
    return D.render(out)


def clip_box(D, box, rx=0):
    x0, y0, x1, y1 = box
    return D.clip(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{rx}"/>')


# ================================================================ 1. The Starry Night — Van Gogh, 1889
def halo(B, cx, cy, rings, seed, L=(6, 10), dens=1.0, ridge=0.35):
    """Concentric rings of tangential dashes (Van Gogh's star and moon halos).
    rings = [(r_in, r_out, colours, width)]."""
    rnd = random.Random(seed)
    rid = []
    for r0, r1, cols, w in rings:
        area = math.pi * (r1 * r1 - r0 * r0)
        n = int(area / (sum(L) / 2 * w) * 1.25 * dens) + 4
        for _ in range(n):
            a = rnd.uniform(0, 2 * math.pi)
            r = rnd.uniform(r0, r1)
            Ls = rnd.uniform(*L)
            da = Ls / max(r, 2) / 2
            pts = [(cx + r * math.cos(a + t * da), cy + r * math.sin(a + t * da)) for t in (-1, 0, 1)] if r > 3 else \
                  [(cx - Ls / 3, cy + rnd.uniform(-2, 2)), (cx + Ls / 3, cy + rnd.uniform(-2, 2))]
            c = rnd.choice(cols)
            ww = w * rnd.uniform(0.85, 1.15)
            B.dash(pts, c, ww)
            if rnd.random() < ridge:
                rid.append(([(x - ww * 0.18, y - ww * 0.18) for x, y in pts], lt(c, 0.45), ww * 0.32))
    for p, c, w in rid:
        B.dash(p, c, w, 0.6)


def tongue_pts(center, widths):
    """Tapered flame tongue polygon around a centreline."""
    left, right = [], []
    n = len(center)
    for i, (x, y) in enumerate(center):
        a = center[max(i - 1, 0)]
        b = center[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = widths[i] / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left + right[::-1]


def along(center):
    """Direction field following a centreline (by nearest segment)."""
    def f(x, y):
        best, ang = 1e9, -math.pi / 2
        for (ax, ay), (bx, by) in zip(center, center[1:]):
            mx, my = (ax + bx) / 2, (ay + by) / 2
            d = (x - mx) ** 2 + (y - my) ** 2
            if d < best:
                best, ang = d, math.atan2(by - ay, bx - ax)
        return ang
    return f


@design("the-starry-night")
def starry_night():
    D = Doc("gmsn")
    box = (68, 66, 532, 436)   # 464 x 370 (the canvas is 92 x 74 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H
    out = [wall(D, "#26323F", 1, (0.5, 0.15), 0.3)]
    out.append(gilt_frame(D, box, 22, 3, "ornate"))
    cp = clip_box(D, box)
    B = Brush()
    paint = []
    moon = (X(0.885), Y(0.15), 19)
    stars = [(X(0.04), Y(0.24), 11), (X(0.16), Y(0.1), 13), (X(0.33), Y(0.07), 10), (X(0.47), Y(0.2), 12),
             (X(0.56), Y(0.05), 9), (X(0.66), Y(0.3), 15), (X(0.76), Y(0.07), 9), (X(0.79), Y(0.27), 12),
             (X(0.43), Y(0.42), 8), (X(0.95), Y(0.4), 9)]
    hills_top = rough([(x0 - 10, Y(0.64)), (X(0.12), Y(0.6)), (X(0.3), Y(0.63)), (X(0.46), Y(0.67)), (X(0.6), Y(0.62)),
                       (X(0.76), Y(0.55)), (X(0.9), Y(0.5)), (x1 + 10, Y(0.53))], 7, 5, 3)

    def hill_y(x):
        for (ax, ay), (bx, by) in zip(hills_top, hills_top[1:]):
            if ax <= x <= bx:
                return ay + (by - ay) * (x - ax) / (bx - ax + 1e-9)
        return Y(0.55)

    # the great current: an S wave through the middle of the sky that curls into two eddies
    wave_y = lambda x: Y(0.33) + H * 0.07 * math.sin((x - x0) / W * 2 * math.pi * 1.1 + 0.6)
    vort = [(X(0.36), Y(0.33), 30, 1), (X(0.53), Y(0.37), 34, -1)]

    def field(x, y):
        # base current: follows the S wave near it, relaxes to gentle horizontal drift elsewhere
        slope = (wave_y(x + 3) - wave_y(x - 3)) / 6
        dv = abs(y - wave_y(x)) / H
        k = max(0.0, 1 - dv / 0.22)
        vx, vy = 1.0, slope * k + 0.25 * math.sin(x / 45 + y / 60) * (1 - k)
        for cx, cy, r, s in vort:
            dx, dy = x - cx, y - cy
            dd = math.hypot(dx, dy)
            if dd < r * 1.7:
                wgt = max(0, 1 - dd / (r * 1.7)) * 3
                vx += -dy / (dd + 1e-6) * wgt * s
                vy += dx / (dd + 1e-6) * wgt * s
        for sx, sy, r in stars + [moon]:
            dx, dy = x - sx, y - sy
            dd = math.hypot(dx, dy)
            if dd < r * 3:
                wgt = max(0, 1 - dd / (r * 3)) * 4
                vx += -dy / (dd + 1e-6) * wgt
                vy += dx / (dd + 1e-6) * wgt
        return math.atan2(vy, vx)

    SKY = ["#102A66", "#183A86", "#21499A", "#2A58A8", "#1A3A80", "#244E9E"]
    MIDB = ["#3A6AB4", "#4A7ABE", "#5A88C4"]
    PALE = ["#7EA6D6", "#9DBEE0", "#B6D0E6", "#6E9AD0", "#C8DCE4"]
    CREAMY = ["#E8EEC8", "#DCE6BC", "#F2F0CE", "#C8DCC0"]

    def sky_col(x, y, rnd):
        for cx, cy, r, s in vort:
            q = math.hypot(x - cx, y - cy) / r
            if q < 1.5:
                if 0.25 < q < 0.6 or 0.9 < q < 1.2:
                    return rnd.choice(PALE + CREAMY)
                return rnd.choice(SKY + MIDB)
        dv = abs(y - wave_y(x))
        if dv < 9:
            return rnd.choice(CREAMY + PALE[1:3])
        if dv < 20:
            return rnd.choice(PALE + MIDB)
        v = (y - y0) / H
        if v > 0.42:
            return rnd.choice(MIDB + PALE[:2] + ["#5E8AC0", "#86A8CC"]) if rnd.random() < 0.55 else rnd.choice(SKY)
        return rnd.choice(SKY) if rnd.random() < 0.72 else rnd.choice(MIDB + PALE[:1])

    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.lin([(0, "#0E2458"), (0.6, "#1A3C80"), (1, "#24508E")])}"/>')
    sky_region = lambda x, y: y < hill_y(x) + 8
    impasto(B, field, sky_region, 4200, sky_col, 11, L=(10, 17), W=(3.0, 4.4), ridge=0.4, steps=3, jit=0.07)
    paint.append(B.render())
    # stars: concentric halos of ringed dashes around a white-hot core
    for i, (sx, sy, r) in enumerate(stars):
        halo(B, sx, sy, [(r * 1.55, r * 2.15, ["#1E4A9A", "#2A5AAA", "#3A6AB4"], 2.8),
                         (r * 1.05, r * 1.55, ["#C8DCB8", "#E4E8B0", "#A8C8C8", "#F2EAA8"], 3.0),
                         (r * 0.62, r * 1.05, ["#F6D648", "#F2E07A", "#E8C030", "#FFE88A"], 3.2),
                         (0, r * 0.62, ["#FFFBE0", "#FFF4B0", "#FFFFFF"], 3.0)], 200 + i, L=(5, 9))
    mx, my, mr = moon
    halo(B, mx, my, [(mr * 1.9, mr * 2.5, ["#2A5AA6", "#3E6EB8", "#C8D8C0"], 3.0),
                     (mr * 1.35, mr * 1.9, ["#F2EAA8", "#E8E4B8", "#D8E4C0", "#FFF2B0"], 3.2),
                     (mr * 1.0, mr * 1.35, ["#FFE070", "#F8D048", "#FFEA98"], 3.4),
                     (0, mr, ["#F6A818", "#F8B828", "#FFC838", "#E89010"], 3.4)], 300, L=(6, 10))
    paint.append(B.render())
    # the crescent: the shadowed disc of the moon painted over, leaving a fat orange crescent
    paint.append(f'<path d="{blob(mx + mr * 0.42, my - mr * 0.18, mr * 0.72, mr * 0.76, 5, 0.04, 14)}" fill="#E8B030"/>')
    halo(B, mx + mr * 0.42, my - mr * 0.18, [(0, mr * 0.7, ["#F2C440", "#FFD860", "#E8B838"], 3.0)], 301, L=(5, 8))
    paint.append(B.render())
    # ---- hills: a pale far range then the main blue range, strokes running along the slopes
    hill_poly = hills_top + [(x1 + 10, y1 + 10), (x0 - 10, y1 + 10)]
    paint.append(f'<path d="{pd(hill_poly)}" fill="#1C3A76"/>')
    hf = lambda x, y: math.atan2((hill_y(x + 5) - hill_y(x - 5)) / 10 * (1 - min(1, (y - hill_y(x)) / 60)), 1) + 0.1 * math.sin(x / 25)
    impasto(B, hf, lambda x, y: hill_y(x) < y < hill_y(x) + 58, 700,
            lambda x, y, r: r.choice(["#2A4E98", "#3E66B0", "#18326E", "#5A80C0", "#294A8A", "#7A9ACC"]) if y < hill_y(x) + 12 else
            r.choice(["#2A4E98", "#1E3E80", "#18326E", "#3A5A9A", "#2C4C86"]), 21, L=(11, 19), W=(2.8, 4.0), ridge=0.3)
    paint.append(B.render())
    paint.append(ink(smooth_open(hills_top), "#0A1840", 2.8, 3, 2, 0.8))
    # light ridge lines on the range (his pale contour strokes)
    for k, off in enumerate((14, 30)):
        ln = [(x, hill_y(x) + off + 4 * math.sin(x / 30 + k)) for x in range(int(x0) + 60, int(x1), 12)]
        paint.append(pline(ln, "#6E90C8", 2.2, 40 + k, 0.6, 1))
    # ---- the sleeping village
    gr_top = lambda x: Y(0.76) - (x - x0) * 0.03
    paint.append(f'<path d="{pd([(x0 - 10, gr_top(x0 - 10)), (x1 + 10, gr_top(x1 + 10)), (x1 + 10, y1 + 10), (x0 - 10, y1 + 10)])}" fill="#1E3A5E"/>')
    impasto(B, lambda x, y: 0.1 * math.sin(x / 40), lambda x, y: y > gr_top(x) - 4, 700,
            lambda x, y, r: r.choice(["#24466A", "#2E5476", "#1A3456", "#3A6070", "#2A4A5A", "#4A6A5A"]), 25, L=(10, 16), W=(2.8, 3.8), ridge=0.2)
    paint.append(B.render())
    rnd = random.Random(31)
    church = (X(0.56), Y(0.88))
    houses = []
    for k in range(34):
        v = rnd.random()
        hx = X(rnd.uniform(0.24, 0.97))
        by = Y(0.8 + v * 0.15) - (hx - X(0.24)) * 0.03
        sc = 0.7 + v * 0.5
        hw, hh = rnd.uniform(13, 21) * sc, rnd.uniform(8, 13) * sc
        if abs(hx + hw / 2 - church[0]) < 22 and by < church[1] + 4:
            continue
        if any(abs(hx - ox) < 9 and abs(by - oy) < 6 for ox, oy, _, _ in houses):
            continue
        houses.append((hx, by, hw, hh))
    trees = [(X(rnd.uniform(0.24, 0.98)), Y(rnd.uniform(0.8, 0.97)), rnd.uniform(8, 14)) for _ in range(14)]
    items = [(by, "h", (hx, by, hw, hh)) for hx, by, hw, hh in houses] + [(ty + 4, "t", (tx, ty, tr)) for tx, ty, tr in trees] + [(church[1], "c", church)]
    for _, kind, it in sorted(items, key=lambda q: q[0]):
        if kind == "h":
            hx, by, hw, hh = it
            wall_c = rnd.choice(["#5A6E96", "#4A5E88", "#6A7EA0", "#3E5280", "#7A8AA8"])
            body = [(hx, by), (hx, by - hh), (hx + hw, by - hh), (hx + hw, by)]
            roof = [(hx - 2.5, by - hh + 1), (hx + hw * rnd.uniform(0.35, 0.65), by - hh - hw * 0.4), (hx + hw + 2.5, by - hh + 1)]
            paint.append(f'<path d="{pd(body)}" fill="{wall_c}"/><path d="{pd(body[:2] + [(hx + 4, by - hh), (hx + 4, by)])}" fill="#9AAAC8" opacity="0.35"/>')
            paint.append(f'<path d="{pd(roof)}" fill="{rnd.choice(["#24345E", "#3A4A7A", "#2E4070", "#4A3E6A"])}"/>')
            paint.append(f'<path d="{pd(body)} {pd(roof)}" fill="none" stroke="#0A1430" stroke-width="1.7" stroke-linejoin="round"/>')
            for k in range(rnd.randint(1, 3)):
                wx = hx + rnd.uniform(2.5, hw - 7)
                wy = by - hh + rnd.uniform(2.5, max(3, hh - 8))
                c = rnd.choice(["#F8D848", "#FFE680", "#F2B830", "#FFD050"])
                paint.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="4.6" height="4.4" fill="{c}"/><rect x="{wx - 1.5:.1f}" y="{wy - 1.5:.1f}" width="7.6" height="7.4" fill="{c}" opacity="0.25"/>')
        elif kind == "t":
            tx, ty, tr = it
            paint.append(dab_crown(D, tx, ty - tr * 0.5, tr, tr * 0.75, [("#3E6672", "#1E3E4A", "#0C2028"), ("#2E5260", "#183440", "#08161C")],
                                   int(tx * 3), n=16, size=(3, 5.5), inkw=1.4, inkc="#06121A", base=True))
        else:
            cx_, cb = it
            nave = [(cx_ - 14, cb), (cx_ - 14, cb - 20), (cx_ + 20, cb - 20), (cx_ + 20, cb)]
            paint.append(f'<path d="{pd(nave)}" fill="#5A6A94"/>')
            paint.append(f'<path d="{pd([(cx_ - 16, cb - 19), (cx_ + 3, cb - 31), (cx_ + 22, cb - 19)])}" fill="#2E3E6E"/>')
            tower = [(cx_ - 8, cb - 20), (cx_ - 8, cb - 42), (cx_ + 2, cb - 42), (cx_ + 2, cb - 20)]
            spire = [(cx_ - 9.5, cb - 41), (cx_ - 3, cb - 96), (cx_ + 3.5, cb - 41)]
            paint.append(f'<path d="{pd(tower)}" fill="#6A7AA0"/><path d="{pd(spire)}" fill="#3E5290"/>')
            paint.append(f'<path d="M{cx_ - 3} {cb - 93}L{cx_ - 6} {cb - 44}" stroke="#8AA0D0" stroke-width="2" opacity="0.7"/>')
            paint.append(f'<path d="{pd(nave)} {pd(tower)} {pd(spire)}" fill="none" stroke="#0A1430" stroke-width="1.8" stroke-linejoin="round"/>')
            paint.append(f'<rect x="{cx_ + 7}" y="{cb - 14}" width="4.5" height="6.5" fill="#F8D848"/>')
    # ---- the cypress: tongues of dark flame licking up into the sky
    base_y = y1 + 12
    tongues = [
        ([(X(0.25), base_y), (X(0.25), Y(0.8)), (X(0.22), Y(0.6)), (X(0.235), Y(0.45)), (X(0.215), Y(0.32))], [44, 40, 30, 18, 3]),
        ([(X(0.08), base_y), (X(0.09), Y(0.78)), (X(0.12), Y(0.6)), (X(0.115), Y(0.44)), (X(0.14), Y(0.3)), (X(0.13), Y(0.2))], [50, 46, 36, 26, 12, 3]),
        ([(X(0.16), base_y), (X(0.16), Y(0.75)), (X(0.17), Y(0.5)), (X(0.185), Y(0.3)), (X(0.18), Y(0.12)), (X(0.2), Y(-0.03))], [66, 58, 46, 32, 16, 4]),
        ([(X(0.2), base_y), (X(0.21), Y(0.85)), (X(0.195), Y(0.68)), (X(0.205), Y(0.55))], [40, 34, 22, 3]),
        ([(X(0.11), base_y), (X(0.115), Y(0.88)), (X(0.13), Y(0.75)), (X(0.12), Y(0.66))], [34, 30, 18, 3]),
    ]
    CY = ["#121C0C", "#1C2A14", "#26381A", "#33281A", "#16220E", "#0A1206", "#2C3E1C", "#222E16"]
    for k, (cl, ws) in enumerate(tongues):
        cl = [(x + random.Random(k).uniform(-2, 2), y) for x, y in cl]
        pts = tongue_pts(cl, ws)
        rj = random.Random(60 + k)
        pts = [(x + 3.5 * math.sin(y / 9 + k) + rj.uniform(-1.5, 1.5), y) for x, y in pts]
        d = smooth_closed(pts)
        paint.append(f'<path d="{d}" fill="#0E1608"/>')
        fine = []
        for a, b in zip(pts, pts[1:] + pts[:1]):
            for t in range(5):
                fine.append((a[0] + (b[0] - a[0]) * t / 5, a[1] + (b[1] - a[1]) * t / 5))
        fld = along(cl[::-1])
        impasto(B, lambda x, y, f=fld, kk=k: f(x, y) + 0.35 * math.sin(y / 14 + kk), fine, int(sum(ws) * 4.2),
                lambda x, y, r, kk=k: r.choice(CY) if (x - (cl[0][0])) < -4 or r.random() < 0.72 else r.choice(["#46502A", "#584628", "#3A5028", "#62582C"]),
                61 + k, L=(12, 22), W=(2.6, 4.0), ridge=0.25, steps=3, jit=0.25)
        paint.append(f'<g {D.clip(f"<path d=\"{d}\"/>")}>{B.render()}</g>')
        paint.append(ink(d, "#050A02", 1.8, 6 + k, 1, 0.6))
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.07)}{varnish(D, box, 0.12, 0.22)}</g>')
    out.append(museum_label(D, 494, "The Starry Night", "VINCENT VAN GOGH · 1889", "#F4E8CA", "#D8C49A", ts=30, bs=18, gap=28))
    return finish(D, out, 7)


# ================================================================ 2. Sunflowers — Van Gogh, 1888
def sunflower_head(D, cx, cy, r, kind, seed, rot=0, squash=1.0, petal_cols=None, disk_cols=None):
    """One impasto sunflower drawn around the origin then placed: kind full / seed / back / droop."""
    rnd = random.Random(seed)
    B = Brush()
    out = []
    pc = petal_cols or ["#F6C21C", "#F2A814", "#FFD84A", "#E88A10", "#F8CC30", "#D87A0E"]
    dc = disk_cols or ["#7A4A14", "#5A3410", "#9A6A1E", "#3E260C", "#B8862A", "#6E7A28"]
    if kind == "back":
        # petals peeking out behind a green calyx
        for i in range(18):
            a = 2 * math.pi * i / 18 + rnd.uniform(-0.1, 0.1)
            L = r * rnd.uniform(0.95, 1.2)
            B.dash([(0.45 * r * math.cos(a), 0.45 * r * math.sin(a)), (L * 0.75 * math.cos(a + 0.05), L * 0.75 * math.sin(a + 0.05)), (L * math.cos(a + 0.1), L * math.sin(a + 0.1))],
                   rnd.choice(pc), r * 0.16)
        out_b = B.render()
        cal = blob(0, 0, r * 0.62, r * 0.62, seed, 0.12, 16)
        out.append(out_b + f'<path d="{cal}" fill="#6A8A2A"/>')
        for i in range(14):
            a = 2 * math.pi * i / 14 + rnd.uniform(-0.12, 0.12)
            B.dash([(0.1 * r * math.cos(a), 0.1 * r * math.sin(a)), (0.68 * r * math.cos(a), 0.68 * r * math.sin(a))],
                   rnd.choice(["#4A6A1A", "#8AA03A", "#5A7A22", "#A8B848"]), r * 0.13)
        out.append(B.render())
        out.append(f'<path d="{cal}" fill="none" stroke="#2A3A0A" stroke-width="1.6" opacity="0.7"/>')
    else:
        disk_r = r * (0.62 if kind == "seed" else 0.5)
        n_p = {"full": 26, "droop": 18, "seed": 9}[kind]
        for layer in range(2 if kind == "full" else 1):
            for i in range(n_p):
                a = 2 * math.pi * (i + layer * 0.5) / n_p + rnd.uniform(-0.08, 0.08)
                L = r * rnd.uniform(0.9, 1.15) * (0.9 if layer else 1)
                bend = rnd.uniform(-0.25, 0.25) + (0.5 if kind == "droop" and math.sin(a) > -0.2 else 0)
                p0 = ((disk_r * 0.85) * math.cos(a), (disk_r * 0.85) * math.sin(a))
                p1 = (L * 0.72 * math.cos(a + bend * 0.3), L * 0.72 * math.sin(a + bend * 0.3) + (r * 0.15 if kind == "droop" else 0))
                p2 = (L * math.cos(a + bend * 0.6), L * math.sin(a + bend * 0.6) + (r * 0.4 if kind == "droop" else 0))
                c = rnd.choice(pc) if kind != "seed" else rnd.choice(["#C88A20", "#A86A18", "#E0A030", "#8A5A1A"])
                w = r * rnd.uniform(0.13, 0.19)
                B.dash([p0, p1, p2], dk(c, 0.18), w * 1.15)
                B.dash([p0, p1, p2], c, w)
                if rnd.random() < 0.6:
                    B.dash([(p0[0] - 0.6, p0[1] - 0.8), (p1[0] - 0.6, p1[1] - 0.8)], lt(c, 0.5), w * 0.3, 0.7)
        out.append(B.render())
        disk = blob(0, 0, disk_r, disk_r, seed + 1, 0.06, 16)
        out.append(f'<path d="{disk}" fill="{dc[1]}"/>')
        # disk: concentric dabs + a thick ring of seeds
        for i in range(int(disk_r * 3.2)):
            a = rnd.uniform(0, 2 * math.pi)
            rr = disk_r * math.sqrt(rnd.random()) * 0.95
            x, y = rr * math.cos(a), rr * math.sin(a)
            ta = a + math.pi / 2
            L = rnd.uniform(3, 6)
            col = rnd.choice(dc) if rr > disk_r * 0.4 or kind == "seed" else rnd.choice(["#8A9A2A", "#6E7A1E", "#B0A030", "#5A6A1A"])
            B.dash([(x - L / 2 * math.cos(ta), y - L / 2 * math.sin(ta)), (x + L / 2 * math.cos(ta), y + L / 2 * math.sin(ta))], col, rnd.uniform(1.8, 3.0))
        for i in range(int(disk_r * 1.6)):
            a = rnd.uniform(0, 2 * math.pi)
            rr = disk_r * rnd.uniform(0.55, 0.95)
            B.dot(rr * math.cos(a), rr * math.sin(a), rnd.uniform(0.9, 1.6), rnd.choice(["#E89A20", "#2A1806", "#F2B840", "#3A2008"]))
        out.append(B.render())
        out.append(f'<path d="{disk}" fill="none" stroke="#2A1606" stroke-width="2" opacity="0.7"/>')
        out.append(f'<path d="{blob(-disk_r * 0.25, -disk_r * 0.3, disk_r * 0.35, disk_r * 0.22, seed, 0.2, 10)}" fill="#F2C840" opacity="0.25"/>')
    return f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot}) scale(1 {squash})">{"".join(out)}</g>'


@design("sunflowers")
def sunflowers():
    D = Doc("gmsf")
    box = (150, 58, 450, 436)   # 300 x 378 (92 x 73 cm, portrait)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    out = [mat_board(D, (x0 - 10, y0 - 10, x1 + 10, y1 + 10), 7, "#2E5A5C", 2)]
    out.append(gilt_frame(D, box, 10, 4, "plain", gold=("#FFF4C0", "#E2BC5A", "#B08A34", "#6E5018", "#3A2808")))
    cp = clip_box(D, box)
    paint = []
    B = Brush()
    table_y = y0 + H * 0.76
    # background: lemon/chrome yellow hatched in short criss-cross strokes
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="#EEC84A"/>')
    impasto(B, lambda x, y: math.radians(-60 if (int(x / 22) + int(y / 22)) % 2 else -20), lambda x, y: y < table_y + 4, 1500,
            lambda x, y, r: r.choice(["#F2D468", "#F0D47A", "#E8C04A", "#F0CC58", "#E6C860", "#E2B840", "#EED070"]), 3,
            L=(8, 14), W=(3.0, 4.4), ridge=0.12, steps=1)
    # table: ochre to orange, long horizontal strokes
    impasto(B, lambda x, y: 0.05 * math.sin(x / 30), lambda x, y: y > table_y - 2, 520,
            lambda x, y, r: r.choice(["#E0A22A", "#D88A1E", "#ECB43A", "#C87818", "#F2C24A"]), 5, L=(14, 26), W=(3.2, 4.6), ridge=0.35, steps=2)
    paint.append(B.render())
    paint.append(pline([(x0 - 5, table_y), (x0 + W * 0.5, table_y + 1.5), (x1 + 5, table_y - 1)], "#4A70C0", 3.4, 6, 0.9, 1))
    paint.append(pline([(x0 - 5, table_y + 3), (x1 + 5, table_y + 2)], "#B06A10", 2, 7, 0.6, 1))
    # vase: squat ochre jug, upper half paler, divided by a blue line
    vx, vb = x0 + W * 0.5, table_y + H * 0.16
    vase = [(vx - 56, vb - 4), (vx - 70, vb - 40), (vx - 64, vb - 74), (vx - 48, vb - 96), (vx - 50, vb - 108), (vx + 50, vb - 108),
            (vx + 48, vb - 96), (vx + 64, vb - 74), (vx + 70, vb - 40), (vx + 56, vb - 4), (vx, vb + 2)]
    vd = smooth_closed(vase)
    paint.append(cast_shadow := f'<ellipse cx="{vx + 18}" cy="{vb + 2}" rx="78" ry="9" fill="#8A4A10" opacity="0.35"/>')
    paint.append(f'<path d="{vd}" fill="#E8A830"/>')
    band_y = vb - 62
    vp = [(x, y) for x, y in ell_pts(vx, vb - 52, 64, 56, 0, 360, 40)]
    impasto(B, lambda x, y: math.radians(-90 + (x - vx) * 0.6), lambda x, y: y < band_y, 260,
            lambda x, y, r: r.choice(["#F6DC7A", "#F2CE5A", "#FBE9A0", "#E8BE48"]), 8, L=(9, 15), W=(3, 4.2), ridge=0.3)
    impasto(B, lambda x, y: math.radians(-90 + (x - vx) * 0.5), lambda x, y: y >= band_y, 380,
            lambda x, y, r: r.choice(["#E8A42A", "#D88E1E", "#F2B840", "#C87A16", "#F6C858"]) if x < vx + 26 else r.choice(["#C07018", "#A85A10", "#D88A20"]),
            9, L=(9, 15), W=(3, 4.2), ridge=0.3)
    paint.append(f'<g {D.clip(f"<path d=\"{vd}\"/>")}>{B.render()}</g>')
    paint.append(pline([(vx - 60, band_y + 2), (vx, band_y + 7), (vx + 60, band_y + 2)], "#3A64B8", 3.4, 10, 0.95, 1))
    paint.append(f'<path d="{blob(vx - 30, vb - 46, 9, 22, 11, 0.1, 10)}" fill="#FFF0B0" opacity="0.45"/>')
    paint.append(ink(vd, "#7A4A10", 2.0, 12, 2, 0.7))
    # stems and leaves rising from the jug
    rnd = random.Random(13)
    heads = [  # (u, v, r, kind, rot, squash)
        (0.42, 0.11, 30, "full", -8, 0.92), (0.68, 0.1, 25, "seed", 15, 0.9), (0.18, 0.2, 27, "droop", -35, 0.85),
        (0.86, 0.22, 26, "full", 20, 0.88), (0.3, 0.32, 36, "full", -10, 0.95), (0.6, 0.28, 41, "full", 5, 1.0),
        (0.84, 0.42, 30, "seed", 25, 0.9), (0.1, 0.44, 25, "droop", -50, 0.8), (0.46, 0.47, 33, "full", 0, 0.9),
        (0.7, 0.53, 28, "back", 35, 0.85), (0.22, 0.54, 29, "full", -20, 0.85), (0.92, 0.63, 22, "droop", 60, 0.8),
        (0.07, 0.66, 21, "droop", -70, 0.75), (0.36, 0.64, 24, "seed", -15, 0.8), (0.58, 0.67, 22, "full", 10, 0.8),
    ]
    stem_out = []
    for u, v, r, kind, rot, sq in heads:
        hx, hy = x0 + u * W, y0 + v * H
        sx = vx + (u - 0.5) * 60
        sy = vb - 104
        mid = ((hx + sx) / 2 + rnd.uniform(-10, 10), (hy + sy) / 2 + 14)
        stem_out.append(taper([(sx, sy), mid, (hx, hy)], 7, 4, "#5A7A22"))
        stem_out.append(pline([(sx - 1, sy), (mid[0] - 2, mid[1]), (hx - 2, hy)], "#A8B840", 1.6, int(hx), 0.6, 1))
        stem_out.append(pline([(sx + 2, sy), (mid[0] + 2, mid[1]), (hx + 2, hy)], "#2A3A0A", 1.4, int(hy), 0.6, 1))
    paint.append("".join(stem_out))
    for k in range(5):
        lx, ly = vx + rnd.uniform(-70, 70), vb - rnd.uniform(110, 170)
        ang = rnd.uniform(-160, -20)
        L = rnd.uniform(34, 48)
        tip = (lx + L * math.cos(math.radians(ang)), ly + L * math.sin(math.radians(ang)) + 12)
        lf = [(lx, ly), ((lx + tip[0]) / 2 - 8, (ly + tip[1]) / 2 - 10), tip, ((lx + tip[0]) / 2 + 8, (ly + tip[1]) / 2 + 8)]
        paint.append(painted(D, lf, ("#A8C04A", "#6A8A2A", "#34500E"), 20 + k, sk=0.12, angle=ang, inkw=1.4, inkc="#2A3A0A", hi=0.4))
    # heads, back to front by size
    for i, (u, v, r, kind, rot, sq) in enumerate(sorted(heads, key=lambda h: h[2])):
        paint.append(sunflower_head(D, x0 + u * W, y0 + v * H, r * 1.18, kind, 100 + i, rot, sq))
    # a fallen petal on the table
    paint.append(taper([(x0 + W * 0.84, table_y + 30), (x0 + W * 0.88, table_y + 26), (x0 + W * 0.92, table_y + 32)], 6, 2, "#E88A10"))
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.07)}{varnish(D, box, 0.14, 0.2, 7, 0.35)}</g>')
    out.append(museum_label(D, 488, "Sunflowers", "VINCENT VAN GOGH · 1888", "#FBF2DC", "#E8D6A6", ts=30, bs=18, gap=28))
    return finish(D, out, 9)


# ================================================================ 3. Café Terrace at Night — Van Gogh, 1888
def flower_star(B, x, y, r, seed):
    """Van Gogh's starry 'flowers': a white core ringed by short radial dabs of lemon and cream."""
    rnd = random.Random(seed)
    for i in range(9):
        a = 2 * math.pi * i / 9 + rnd.uniform(-0.2, 0.2)
        B.dash([(x + r * 0.35 * math.cos(a), y + r * 0.35 * math.sin(a)), (x + r * math.cos(a), y + r * math.sin(a))],
               rnd.choice(["#F8E890", "#FFF6C8", "#F2D860", "#E8F0D0"]), r * 0.42)
    B.dot(x, y, r * 0.42, "#FFFFF0")


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def persp_t(t, k=0.35):
    """Perspective compression along a receding wall: t (0 near .. 1 far) in true depth -> screen fraction."""
    return t / (t + (1 - t) * k) if t < 1 else 1


@design("cafe-terrace-at-night")
def cafe_terrace():
    from figures import person
    D = Doc("gmct")
    box = (150, 54, 450, 426)   # 300 x 372 (81 x 65.5 cm, portrait)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H
    out = [wall(D, "#5A3A2E", 21, (0.5, 0.2), 0.3)]
    out.append(simple_frame(D, box, 16, ("#5A5048", "#1E1814", "#0A0806"), 5))
    out.append(f'<rect x="{x0 - 4}" y="{y0 - 4}" width="{W + 8}" height="{H + 8}" fill="none" stroke="#C8A050" stroke-width="2.2"/>')
    cp = clip_box(D, box)
    paint = []
    B = Brush()
    vp = (X(0.68), Y(0.58))
    # ---- sky
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="#14306E"/>')
    impasto(B, lambda x, y: math.radians(-10 + 30 * math.sin(x / 40)), lambda x, y: True, 900,
            lambda x, y, r: r.choice(["#1A3A86", "#22489A", "#16327A", "#2C56A8", "#10286A", "#3A62AE"]), 3,
            L=(8, 13), W=(2.6, 3.6), ridge=0.3, steps=2)
    paint.append(B.render())
    for i, (u, v, r) in enumerate([(0.56, 0.05, 7), (0.7, 0.1, 8.5), (0.84, 0.04, 6), (0.62, 0.2, 6.5), (0.77, 0.21, 7), (0.92, 0.14, 6),
                                   (0.6, 0.31, 5), (0.69, 0.36, 4.5), (0.98, 0.04, 5), (0.74, 0.3, 4)]):
        flower_star(B, X(u), Y(v), r, 40 + i)
    paint.append(B.render())
    # ---- right-hand houses receding to the vanishing point
    near_top, near_bot = (x1 + 6, Y(0.06)), (x1 + 6, Y(0.84))
    far_top, far_bot = (X(0.71), Y(0.44)), (X(0.71), vp[1] + 1)
    facade = [near_top, far_top, far_bot, near_bot]

    def fpt(t, h):
        tt = persp_t(t, 0.3)
        return lerp(lerp(near_top, far_top, tt), lerp(near_bot, far_bot, tt), h)
    paint.append(f'<path d="{pd(facade)}" fill="#262A52"/>')
    impasto(B, lambda x, y: math.atan2(vp[1] - y, vp[0] - x) * 0.4 + 0.1, facade, 420,
            lambda x, y, r: r.choice(["#2E3462", "#3C3E74", "#1E2448", "#4A4682", "#2A305C", "#5A4A7A"]), 7, L=(9, 15), W=(2.6, 3.6), ridge=0.2)
    paint.append(f'<g {D.clip(f"<path d=\"{pd(facade)}\"/>")}>{B.render()}</g>')
    rnd = random.Random(9)
    for t0 in (0.04, 0.24, 0.44, 0.62, 0.78):
        for h0 in (0.1, 0.32, 0.54):
            t1, h1 = t0 + 0.1, h0 + 0.14
            q = [fpt(t0, h0), fpt(t1, h0), fpt(t1, h1), fpt(t0, h1)]
            lit = rnd.random() < 0.4
            paint.append(f'<path d="{pd(q)}" fill="{"#F2B830" if lit else "#3E6E70"}"/>')
            if lit:
                m0, m1 = lerp(q[0], q[1], 0.5), lerp(q[3], q[2], 0.5)
                paint.append(f'<path d="M{m0[0]:.1f} {m0[1]:.1f}L{m1[0]:.1f} {m1[1]:.1f}" stroke="#7A4A10" stroke-width="1.3"/>')
            paint.append(f'<path d="{pd(q)}" fill="none" stroke="#0C0E26" stroke-width="1.5"/>')
    # dark tree against the houses
    paint.append(taper([(X(0.9), Y(0.88)), (X(0.9), Y(0.62)), (X(0.92), Y(0.44))], 7, 4, "#2A1C14"))
    paint.append(dab_crown(D, X(0.93), Y(0.34), 30, 50, [("#2E6A5A", "#1A4438", "#0A2018"), ("#3A7A4A", "#1E4A2E", "#0E2414")], 11, n=80,
                           size=(4, 8), inkw=1.6, inkc="#06120C"))
    # ---- the café wall, lit orange, receding under the awning
    base_near, base_far = (x0 - 6, Y(0.8)), (X(0.64), vp[1] + 1)
    top_near, top_far = (x0 - 6, Y(0.2)), (X(0.64), Y(0.42))
    cafe_wall = [top_near, top_far, base_far, base_near]

    def wpt(t, h):
        tt = persp_t(t, 0.35)
        return lerp(lerp(top_near, top_far, tt), lerp(base_near, base_far, tt), h)
    paint.append(f'<path d="{pd(cafe_wall)}" fill="#E39A30"/>')
    impasto(B, lambda x, y: -math.pi / 2 + 0.15, cafe_wall, 420,
            lambda x, y, r: r.choice(["#F2B040", "#E89428", "#F6C858", "#D8801E", "#C8701A", "#E8A848"]), 8, L=(9, 15), W=(2.8, 3.8), ridge=0.3)
    paint.append(f'<g {D.clip(f"<path d=\"{pd(cafe_wall)}\"/>")}>{B.render()}</g>')
    for t0, t1, h0 in ((0.02, 0.2, 0.32), (0.3, 0.46, 0.36), (0.56, 0.68, 0.4), (0.76, 0.84, 0.42)):
        q = [wpt(t0, h0), wpt(t1, h0), wpt(t1, 1.0), wpt(t0, 1.0)]
        paint.append(f'<path d="{pd(q)}" fill="#F8D468"/>')
        impasto(B, lambda x, y: -math.pi / 2, q, int(abs(q[1][0] - q[0][0]) * abs(q[3][1] - q[0][1]) / 14) + 6,
                lambda x, y, r: r.choice(["#FFF0A8", "#FFE07A", "#F6C850", "#FFF8D0", "#E8B040"]), int(t0 * 100), L=(6, 11), W=(2.4, 3.2), ridge=0.2)
        paint.append(f'<g {D.clip(f"<path d=\"{pd(q)}\"/>")}>{B.render()}</g>')
        m0, m1 = lerp(q[0], q[1], 0.5), lerp(q[3], q[2], 0.5)
        paint.append(f'<path d="M{m0[0]:.1f} {m0[1]:.1f}L{m1[0]:.1f} {m1[1]:.1f}" stroke="#B86A18" stroke-width="1.6"/>')
        paint.append(f'<path d="{pd(q)}" fill="none" stroke="#7A3A10" stroke-width="2"/>')
    # ---- the great awning, seen from below: chrome yellow, its valance edge receding
    val_near, val_far = (x0 - 6, Y(0.27)), (X(0.62), Y(0.44))
    awning = [(x0 - 6, y0 - 6), (X(0.5), y0 - 6), (X(0.6), Y(0.2)), (X(0.64), Y(0.4)), val_far, val_near]
    paint.append(f'<path d="{pd(awning)}" fill="#F2C838"/>')
    impasto(B, lambda x, y: math.atan2(val_far[1] - val_near[1], val_far[0] - val_near[0]) + 0.1, awning, 640,
            lambda x, y, r: r.choice(["#F6D040", "#FFE060", "#E8B820", "#F2C838", "#FFEA80"]) if r.random() < 0.8 else r.choice(["#B8B848", "#D8A828", "#E8D870"]),
            9, L=(12, 20), W=(3.0, 4.2), ridge=0.35)
    paint.append(f'<g {D.clip(f"<path d=\"{pd(awning)}\"/>")}>{B.render()}</g>')
    valance = [val_near, val_far, lerp(val_far, (val_far[0], val_far[1] + 6), 1), (val_near[0], val_near[1] + 18)]
    paint.append(f'<path d="{pd(valance)}" fill="#E8A020"/>')
    paint.append(pline([val_near, val_far], "#8A5A10", 2.4, 11, 0.85, 1))
    paint.append(pline([(val_near[0], val_near[1] + 18), (val_far[0], val_far[1] + 6)], "#7A4A10", 2.0, 12, 0.8, 1))
    paint.append(ink(pd(awning[1:5], False), "#5A3A0A", 2.0, 10, 1, 0.6))
    # gas lamp hanging from the valance
    lx, ly = X(0.4), Y(0.42)
    paint.append(soft_glow(D, lx, ly, 90, "#FFF4A0", 0.6))
    paint.append(f'<path d="M{lx} {Y(0.36)}V{ly - 6}" stroke="#3A2408" stroke-width="1.6"/>')
    paint.append(f'<path d="{pd([(lx - 7, ly - 7), (lx + 7, ly - 7), (lx + 5, ly + 8), (lx - 5, ly + 8)])}" fill="#FFFDE8" stroke="#5A3A0A" stroke-width="1.5"/>')
    paint.append(f'<path d="M{lx - 9} {ly - 7}H{lx + 9}" stroke="#3A2408" stroke-width="2.2"/>')
    # ---- terrace floor (lit) and the cobbled street
    edge_near, edge_far = (X(0.56), y1 + 6), (X(0.67), vp[1] + 1)
    floor = [base_near, base_far, edge_far, edge_near, (x0 - 6, y1 + 6)]
    paint.append(f'<path d="{pd(floor)}" fill="#E8A83A"/>')
    impasto(B, lambda x, y: math.atan2(vp[1] - y, vp[0] - x) + math.pi / 2 + 0.3, floor, 460,
            lambda x, y, r: r.choice(["#F2BE48", "#E8A030", "#F6D068", "#D88C28", "#E0B050", "#C8A048"]), 12, L=(8, 13), W=(2.8, 3.8), ridge=0.3)
    paint.append(f'<g {D.clip(f"<path d=\"{pd(floor)}\"/>")}>{B.render()}</g>')
    street = [edge_near, edge_far, (X(0.72), vp[1] + 1), near_bot, (x1 + 6, y1 + 6)]
    paint.append(f'<path d="{pd(street)}" fill="#3A4A7A"/>')
    rnd = random.Random(14)
    for i in range(700):
        x, y = rnd.uniform(X(0.5), x1 + 4), rnd.uniform(vp[1], y1 + 6)
        if not inside((x, y), street):
            continue
        t = (y - vp[1]) / (y1 - vp[1])
        rr = 1.0 + 4.4 * t
        near_lamp = x < X(0.8) and rnd.random() < 0.55
        c = rnd.choice(["#E8A85A", "#F2C070", "#C87A5A", "#E89A6A", "#B88AA8"]) if near_lamp else \
            rnd.choice(["#5A6AA8", "#7A7AB8", "#4A5A90", "#9A88B8", "#6A7AB0", "#C89AA8", "#3A4A80"])
        B.dash([(x - rr * 0.7, y), (x + rr * 0.7, y + rr * 0.1)], c, rr * 0.95)
    paint.append(f'<g {D.clip(f"<path d=\"{pd(street)}\"/>")}>{B.render()}</g>')
    # ---- tables in perspective along the wall, with diners and a waiter
    fig = []

    def table(tx, ty, s, i):
        tr = 22 * s
        fig.append(f'<ellipse cx="{tx + 3 * s:.1f}" cy="{ty + 30 * s:.1f}" rx="{tr * 0.9:.1f}" ry="{tr * 0.22:.1f}" fill="#8A5A1A" opacity="0.35"/>')
        fig.append(f'<path d="M{tx:.1f} {ty:.1f}V{ty + 30 * s:.1f}M{tx - 7 * s:.1f} {ty + 30 * s:.1f}H{tx + 7 * s:.1f}" stroke="#4A2A10" stroke-width="{max(1.4, 2.6 * s):.1f}"/>')
        fig.append(f'<ellipse cx="{tx:.1f}" cy="{ty:.1f}" rx="{tr:.1f}" ry="{tr * 0.36:.1f}" fill="#FFF2D0" stroke="#7A5A30" stroke-width="{max(1.2, 1.8 * s):.1f}"/>')
        fig.append(f'<ellipse cx="{tx - tr * 0.25:.1f}" cy="{ty - tr * 0.08:.1f}" rx="{tr * 0.45:.1f}" ry="{tr * 0.12:.1f}" fill="#FFFFFF" opacity="0.85"/>')
        if i % 2 == 0:
            fig.append(f'<rect x="{tx + tr * 0.2:.1f}" y="{ty - 7 * s:.1f}" width="{3 * s:.1f}" height="{7 * s:.1f}" fill="#5A8A6A"/>')
        for sx in (-1, 1):
            cx_ = tx + sx * tr * 1.15
            fig.append(f'<path d="M{cx_:.1f} {ty + 28 * s:.1f}V{ty - 4 * s:.1f}M{cx_ - 6 * s:.1f} {ty + 9 * s:.1f}H{cx_ + 6 * s:.1f}M{cx_ - 5 * s:.1f} {ty + 9 * s:.1f}V{ty + 28 * s:.1f}" '
                       f'stroke="#5A3A1A" stroke-width="{max(1.2, 2.0 * s):.1f}" fill="none" stroke-linecap="round"/>')
    spots = [(0.62, 0.625), (0.55, 0.66), (0.4, 0.69), (0.52, 0.745), (0.24, 0.78), (0.44, 0.86), (0.13, 0.95)]
    for i, (u, v) in enumerate(spots):
        tx, ty = X(u), Y(v)
        s = (ty - vp[1]) / (y1 - vp[1])
        table(tx, ty - 26 * s, s, i)
        if i in (2, 3, 4, 6):
            fig.append(person(tx - 30 * s, ty + 4 * s, 78 * s, "sit_side", 1, {"top": ["#3A4A6A", "#2A2A3A", "#6A3A2A", "#4A5A3A"][i % 4], "hat_kind": "cap" if i == 3 else None,
                                                                                "bottom": "#2A2430", "skin": "#E8B888", "hair": "#3A2A1A", "form": "m"}, seed=50 + i, light=-1, tint=("#F2B040", 0.2), shadow=0))
        if i in (1, 3, 5):
            fig.append(person(tx + 30 * s, ty + 4 * s, 74 * s, "sit_side", -1, {"top": ["#F2E8D8", "#3A3A5A", "#7A2A3A"][i % 3], "hat_kind": None, "form": "f", "hair_style": "bun",
                                                                                 "bottom": "#4A2A3A", "bottom_kind": "skirt", "skin": "#F0C8A0", "hair": "#4A2A1A"}, seed=70 + i, light=-1, tint=("#F2B040", 0.2), shadow=0))
    paint.append("".join(fig))
    paint.append(person(X(0.33), Y(0.8), 50, "stand_34", 1, {"top": "#F6F2E4", "bottom": "#1E1A20", "top_kind": "long", "bottom_kind": "trousers",
                                                              "hair": "#2A1A10", "hat_kind": None, "skin": "#E8B888", "form": "m"}, seed=60, light=-1, tint=("#F2B040", 0.15)))
    for k, (u, v, h, sd, f_) in enumerate([(0.8, 0.66, 30, 61, -1), (0.86, 0.68, 26, 62, 1), (0.76, 0.62, 17, 63, -1)]):
        paint.append(person(X(u), Y(v), h, "walk", f_, "silhouette:#1A1A30", seed=sd, rim="#E8A040", light=-1))
    # carriage far down the street
    cxr, cyr = X(0.73), Y(0.6)
    paint.append(f'<rect x="{cxr - 4:.1f}" y="{cyr - 9:.1f}" width="9" height="7" fill="#1A1424"/><circle cx="{cxr - 2:.1f}" cy="{cyr - 1:.1f}" r="2.4" fill="none" stroke="#1A1424" stroke-width="1.2"/>'
                 f'<path d="M{cxr + 5:.1f} {cyr - 5:.1f}l6 -2v6" stroke="#1A1424" stroke-width="2" fill="none"/>')
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.07)}{varnish(D, box, 0.12, 0.25, 8, 0.4)}</g>')
    out.append(f'<rect x="176" y="458" width="248" height="74" rx="2" fill="#000" opacity="0.25" transform="translate(2 3)"/>')
    out.append(f'<rect x="176" y="458" width="248" height="74" rx="2" fill="#F6EEDC"/>')
    out.append(museum_label(D, 490, "Café Terrace at Night", "VAN GOGH · 1888", "#2A1A10", "#6A4A2A", ts=24, bs=17, gap=26, max_w=226))
    return finish(D, out, 13)


# ================================================================ 4. Almond Blossoms — Van Gogh, 1890
def branch_tree(rnd, x, y, ang, L, w, depth, out, kink=18):
    """Recursive gnarled branch: list of (points, w0, w1) segments."""
    pts = [(x, y)]
    a = ang
    seg = L / 4
    for _ in range(4):
        a += math.radians(rnd.uniform(-kink, kink))
        x, y = x + seg * math.cos(a), y + seg * math.sin(a)
        pts.append((x, y))
    out.append((pts, w, w * 0.62))
    if depth > 0:
        for k in range(rnd.choice([1, 2, 2, 3])):
            t = rnd.uniform(0.35, 0.95)
            i = min(3, int(t * 4))
            bx, by = pts[i + 1]
            side = rnd.choice([-1, 1])
            branch_tree(rnd, bx, by, a + side * math.radians(rnd.uniform(25, 60)), L * rnd.uniform(0.45, 0.7), w * 0.62, depth - 1, out, kink)
    return out


def blossom(B, D, cx, cy, r, seed, rot=0, open_=1.0, pink=0.0):
    """Five-petalled almond flower: white petals with cool blue-grey shadows and a blush at the heart."""
    rnd = random.Random(seed)
    out = []
    for i in range(5):
        a = math.radians(rot + i * 72 + rnd.uniform(-8, 8))
        px, py = cx + r * 0.55 * math.cos(a) * open_, cy + r * 0.55 * math.sin(a) * open_
        pet = blob(px, py, r * 0.52, r * 0.42 * (0.7 + 0.3 * open_), seed + i, 0.12, 12, math.degrees(a))
        base = mix("#FFFFFF", "#F2C8D0", pink * rnd.uniform(0.5, 1))
        out.append(f'<path d="{pet}" fill="{base}"/>')
        out.append(f'<path d="{pet}" fill="#A8C0C8" opacity="{rnd.uniform(0.15, 0.35):.2f}" transform="translate({1.2 * math.cos(a + 1):.1f} {1.2 * math.sin(a + 1):.1f})" clip-path="none"/>')
        # radial brush ridges on the petal
        for k in range(3):
            aa = a + rnd.uniform(-0.4, 0.4)
            B.dash([(cx + r * 0.25 * math.cos(aa), cy + r * 0.25 * math.sin(aa)), (cx + r * 0.85 * math.cos(aa) * open_, cy + r * 0.85 * math.sin(aa) * open_)],
                   rnd.choice(["#FFFFFF", "#F4F2EC", "#E4ECEC", "#F8E8EA"]), r * 0.16, 0.8)
        out.append(B.render())
        out.append(f'<path d="{pet}" fill="none" stroke="#5A6A6A" stroke-width="1.1" opacity="0.55"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.26:.1f}" fill="#B8C870"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.14:.1f}" fill="#8A3A2A"/>')
    for i in range(7):
        a = rnd.uniform(0, 6.28)
        out.append(f'<circle cx="{cx + r * 0.3 * math.cos(a):.1f}" cy="{cy + r * 0.3 * math.sin(a):.1f}" r="1.1" fill="#7A3A2A"/>')
    return "".join(out)


def bud(cx, cy, r, ang, seed, col="#E88A9A"):
    rnd = random.Random(seed)
    a = math.radians(ang)
    tip = (cx + r * 1.4 * math.cos(a), cy + r * 1.4 * math.sin(a))
    d = smooth_closed([(cx - r * 0.6 * math.sin(a), cy + r * 0.6 * math.cos(a)), tip, (cx + r * 0.6 * math.sin(a), cy - r * 0.6 * math.cos(a)),
                       (cx - r * 0.5 * math.cos(a), cy - r * 0.5 * math.sin(a))])
    return (f'<path d="{d}" fill="{col}"/><path d="{d}" fill="none" stroke="#7A2A3A" stroke-width="1.2" opacity="0.6"/>'
            f'<path d="M{cx - r * 0.5 * math.cos(a):.1f} {cy - r * 0.5 * math.sin(a):.1f}l{-r * 0.5 * math.cos(a):.1f} {-r * 0.5 * math.sin(a):.1f}" stroke="#5A3A2A" stroke-width="{r * 0.6:.1f}" stroke-linecap="round"/>'
            f'<path d="M{cx:.1f} {cy:.1f}L{tip[0] - 1:.1f} {tip[1] - 1:.1f}" stroke="#FFFFFF" stroke-width="1.2" opacity="0.6"/>')


@design("almond-blossoms")
def almond_blossoms():
    D = Doc("gmab")
    box = (70, 62, 530, 428)   # 460 x 366 (73 x 92 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    out = [mat_board(D, (x0 - 6, y0 - 6, x1 + 6, y1 + 6), 6, "#EFE6D2", 31)]
    out.append(simple_frame(D, box, 6, ("#F4F0E6", "#C8C0B0", "#7A7266"), 3))
    cp = clip_box(D, box)
    paint = []
    B = Brush()
    # turquoise sky, laid in dense short strokes close in value, paler where the light gathers
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.rad([(0, "#8ED0CE"), (0.6, "#6CBCC2"), (1, "#56AAB4")], 0.5, 0.45, 0.75)}"/>')
    fld = lambda x, y: math.radians(-60 + 50 * math.sin(x / 60 + y / 90))
    impasto(B, fld, lambda x, y: True, 3400,
            lambda x, y, r: (r.choice(["#86CACA", "#94D2D0", "#7AC2C6", "#A2D8D4", "#8CCCCC", "#B2DED8"]) if math.hypot(x - 300, y - 230) < 150 else
                             r.choice(["#6CB8C0", "#78BEC4", "#62B0BA", "#84C6C8", "#5AA8B4"])),
            3, L=(8, 14), W=(3.2, 4.4), ridge=0.15, steps=2, jit=0.2)
    paint.append(B.render())
    # branches: limbs entering from the edges and forking into a lacework of twigs
    rnd = random.Random(8)
    segs = []
    branch_tree(random.Random(8), x0 - 10, y0 + H * 0.86, math.radians(-30), 230, 24, 4, segs, 20)
    branch_tree(random.Random(12), x0 - 10, y0 + H * 0.3, math.radians(-8), 200, 15, 3, segs, 22)
    branch_tree(random.Random(15), x1 + 10, y0 + H * 0.16, math.radians(165), 190, 15, 3, segs, 20)
    branch_tree(random.Random(19), x1 + 10, y0 + H * 0.7, math.radians(-150), 150, 12, 3, segs, 20)
    branch_tree(random.Random(23), x0 + W * 0.3, y1 + 10, math.radians(-80), 140, 11, 3, segs, 22)
    bark = []
    segs.sort(key=lambda q: -q[1])
    for pts, w0, w1 in segs:
        bark.append(taper(pts, w0 + 3, w1 + 2.6, "#1A2622"))
    for pts, w0, w1 in segs:
        bark.append(taper(pts, w0, w1, "#4E4C30"))
        bark.append(taper([(x - w0 * 0.15, y - w0 * 0.2) for x, y in pts], w0 * 0.45, w1 * 0.35, "#7E7A48", 0.85))
        bark.append(taper([(x + w0 * 0.2, y + w0 * 0.22) for x, y in pts], w0 * 0.3, w1 * 0.25, "#26302A", 0.8))
        for k in range(max(1, int(w0 / 2.5))):
            i = rnd.randrange(len(pts) - 1)
            p, q = pts[i], pts[i + 1]
            t = rnd.random()
            bx, by = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
            ang = math.atan2(q[1] - p[1], q[0] - p[0])
            L = rnd.uniform(4, 9)
            B.dash([(bx - L / 2 * math.cos(ang), by - L / 2 * math.sin(ang) + rnd.uniform(-w0 / 4, w0 / 4)),
                    (bx + L / 2 * math.cos(ang), by + L / 2 * math.sin(ang) + rnd.uniform(-w0 / 4, w0 / 4))],
                   rnd.choice(["#8A8858", "#3A4430", "#A89A62", "#2E3A2E", "#6A7A4A"]), max(1.4, min(3, w0 * 0.2)), 0.85)
    paint.append("".join(bark) + B.render())
    # blossoms and buds along the twigs (more toward the tips)
    flowers = []
    for pts, w0, w1 in segs:
        if w0 > 20:
            continue
        for k in range(1 + int(len(pts) * (18 - w0) / 12)):
            i = rnd.randrange(1, len(pts))
            px, py = pts[i]
            side = rnd.choice([-1, 1])
            fx, fy = px + side * rnd.uniform(4, 10), py + rnd.uniform(-8, 6)
            if not (x0 + 8 < fx < x1 - 8 and y0 + 8 < fy < y1 - 8):
                continue
            kind = rnd.random()
            if any(abs(fx - ox) < 21 and abs(fy - oy) < 21 for oy, ox, *_ in flowers):
                continue
            flowers.append((fy, fx, kind, rnd.uniform(13, 19), rnd.uniform(0, 72), rnd.randint(0, 9999)))
    flowers.sort()
    for fy, fx, kind, r, rot, sd in flowers:
        if kind < 0.18:
            paint.append(bud(fx, fy, r * 0.42, rnd.uniform(-150, -30), sd, rnd.choice(["#E8909C", "#F2B0B8", "#D87080"])))
        elif kind < 0.3:
            paint.append(blossom(B, D, fx, fy, r * 0.75, sd, rot, 0.6, 0.8))
        else:
            paint.append(blossom(B, D, fx, fy, r, sd, rot, 1.0, 0.25 if kind < 0.5 else 0.0))
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.06)}{varnish(D, box, 0.12, 0.16, 6, 0.3)}</g>')
    out.append(museum_label(D, 480, "Almond Blossoms", "VINCENT VAN GOGH · 1890", "#3A2E22", "#6A5A44", ts=30, bs=18, gap=30))
    return finish(D, out, 17)


# ================================================================ 5. Wheatfield with Cypresses — Van Gogh, 1889
def swirl_cloud(B, D, cx, cy, rx, ry, seed, cols, shade):
    """A curling cumulus built of concentric swirling strokes (Van Gogh's clouds)."""
    rnd = random.Random(seed)
    out = []
    lobes = [(cx + rx * rnd.uniform(-0.7, 0.7), cy + ry * rnd.uniform(-0.4, 0.3), rx * rnd.uniform(0.35, 0.55)) for _ in range(5)]
    for lx, ly, lr in lobes:
        out.append(f'<path d="{blob(lx, ly, lr, lr * 0.75, rnd.randint(0, 999), 0.12, 14)}" fill="{shade[0]}"/>')
    for lx, ly, lr in lobes:
        n = int(lr * lr * 0.12) + 10
        for _ in range(n):
            a = rnd.uniform(0, 2 * math.pi)
            r = lr * math.sqrt(rnd.random()) * 0.95
            x, y = lx + r * math.cos(a), ly + r * 0.75 * math.sin(a)
            L = rnd.uniform(9, 16)
            da = L / max(r, 4) / 2
            sp = 0.18   # spiral inward
            pts = [(lx + r * (1 - sp * t) * math.cos(a + t * da), ly + r * (1 - sp * t) * 0.75 * math.sin(a + t * da)) for t in (-1, 0, 1)]
            lit = math.sin(a) < 0.3 and r > lr * 0.3
            B.dash(pts, rnd.choice(cols if lit else shade), rnd.uniform(2.8, 4))
    return "".join(out)


@design("wheatfield-with-cypresses")
def wheatfield():
    D = Doc("gmwf")
    box = (70, 70, 530, 432)   # 460 x 362 (72.5 x 91.5 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H
    out = [wall(D, "#E8E0D0", 41, (0.5, 0.2), 0.2)]
    out.append(gilt_frame(D, box, 26, 43, "plain", gold=("#FFF0C0", "#D8B868", "#A88A44", "#6A5222", "#36280E")))
    cp = clip_box(D, box)
    paint = []
    B = Brush()
    # sky: turquoise-blue, with curling paths of wind
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.lin([(0, "#6AA6D0"), (0.5, "#9ACAE0"), (1, "#C8E0E0")])}"/>')
    sky_f = lambda x, y: math.radians(-10 + 40 * math.sin(x / 38 + y / 30))
    impasto(B, sky_f, lambda x, y: y < Y(0.55), 1500,
            lambda x, y, r: r.choice(["#7AB2D8", "#8CC0DE", "#6AA2CE", "#A8D0E4", "#5E96C4", "#B8D8E4"]) if y < Y(0.3) else
            r.choice(["#A8D0E2", "#BCDCE6", "#9AC4DC", "#CCE4E4", "#B0D4D8"]), 3, L=(9, 15), W=(3, 4.2), ridge=0.3, steps=3)
    paint.append(B.render())
    for i, (u, v, rx, ry) in enumerate([(0.22, 0.18, 70, 34), (0.55, 0.12, 54, 26), (0.5, 0.36, 82, 30), (0.88, 0.3, 50, 26), (0.12, 0.42, 46, 18)]):
        paint.append(swirl_cloud(B, D, X(u), Y(v), rx, ry, 50 + i, ["#FFFFFF", "#F2F2EA", "#E8ECEC", "#FFF8E8"], ["#C8D4DC", "#B8C8D4", "#D8DCE0"]))
        paint.append(B.render())
    # violet-blue mountains
    mtn = rough([(x0 - 10, Y(0.56)), (X(0.12), Y(0.5)), (X(0.3), Y(0.47)), (X(0.42), Y(0.52)), (X(0.58), Y(0.46)), (X(0.8), Y(0.5)), (x1 + 10, Y(0.53))], 4, 6, 3)
    mpoly = mtn + [(x1 + 10, Y(0.66)), (x0 - 10, Y(0.66))]
    paint.append(f'<path d="{pd(mpoly)}" fill="#7A82B8"/>')
    impasto(B, lambda x, y: math.radians(-5 + 20 * math.sin(x / 30)), mpoly, 300,
            lambda x, y, r: r.choice(["#8A92C8", "#6A72A8", "#9AA2D0", "#7A7AB0", "#A8A8D0"]), 5, L=(10, 16), W=(3, 4), ridge=0.3)
    paint.append(B.render())
    paint.append(ink(smooth_open(mtn), "#3A3A70", 2.2, 5, 1, 0.7))
    # olive groves and dark bushes in the middle distance
    for i, (u, v, rx, ry) in enumerate([(0.08, 0.62, 40, 18), (0.3, 0.6, 50, 16), (0.52, 0.61, 36, 14), (0.86, 0.6, 50, 18), (0.64, 0.64, 30, 12)]):
        paint.append(dab_crown(D, X(u), Y(v), rx, ry, [("#9AB060", "#5E7A3A", "#2E4420"), ("#7AA070", "#3E6A44", "#1E3A24")], 60 + i, n=int(rx * 1.6),
                               size=(4, 7), inkw=1.6, inkc="#1A2A10"))
    # golden wheat, rolling in waves toward us
    field = [(x0 - 10, Y(0.64)), (X(0.3), Y(0.62)), (X(0.6), Y(0.65)), (x1 + 10, Y(0.63)), (x1 + 10, y1 + 10), (x0 - 10, y1 + 10)]
    paint.append(f'<path d="{pd(field)}" fill="#D8A030"/>')
    wf = lambda x, y: math.radians(-70 + 35 * math.sin(x / 26 + y / 18))
    impasto(B, wf, field, 1500,
            lambda x, y, r: r.choice(["#F2C848", "#E8B030", "#F6D870", "#D89A28", "#C8882A", "#F8E08A", "#B8A040"]) if r.random() < 0.9 else r.choice(["#7A9A3A", "#A8A848"]),
            7, L=(10, 18), W=(3, 4.2), ridge=0.35, steps=3)
    paint.append(B.render())
    rnd = random.Random(9)
    for k in range(26):
        x, y = rnd.uniform(X(0.05), X(0.65)), rnd.uniform(Y(0.68), Y(0.97))
        r = 1.6 + 2.2 * (y - Y(0.68)) / (Y(0.3))
        paint.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{rnd.choice(["#D8301E", "#E84A2A", "#C02018"])}"/>')
    # foreground bush bottom-left
    paint.append(dab_crown(D, X(0.04), Y(0.98), 70, 34, [("#7A9A50", "#3E6A30", "#1A3A18"), ("#5A8A6A", "#2E5A3E", "#12301E")], 70, n=120, size=(4, 8), inkw=1.6, inkc="#0E1E0A"))
    # the cypresses, tall flames on the right
    for k, (cxu, top, wid) in enumerate([(0.79, 0.04, 0.12), (0.69, 0.3, 0.08)]):
        cxp = X(cxu)
        cl = [(cxp, y1 + 30), (cxp - 3, Y(0.75)), (cxp + 4, Y(0.5)), (cxp - 2, Y(0.25 + top * 0.5)), (cxp + 3, Y(top))]
        ws = [W * wid, W * wid * 1.05, W * wid * 0.85, W * wid * 0.55, 3]
        pts = tongue_pts(cl, ws)
        rj = random.Random(80 + k)
        pts = [(x + 4 * math.sin(y / 8 + k) + rj.uniform(-2, 2), y) for x, y in pts]
        d = smooth_closed(pts)
        paint.append(f'<path d="{d}" fill="#0E1E10"/>')
        fine = []
        for a_, b_ in zip(pts, pts[1:] + pts[:1]):
            for t in range(5):
                fine.append((a_[0] + (b_[0] - a_[0]) * t / 5, a_[1] + (b_[1] - a_[1]) * t / 5))
        fld = along(cl[::-1])
        impasto(B, lambda x, y, f=fld, kk=k: f(x, y) + 0.6 * math.sin(y / 10 + kk), fine, int(sum(ws) * 3.2),
                lambda x, y, r: r.choice(["#1A3A20", "#24462A", "#2E5A34", "#163018", "#3A6A3A", "#0E2212"]) if x > cxp - 6 or r.random() < 0.5 else r.choice(["#4A7A40", "#5A8A48", "#3E6A3A"]),
                81 + k, L=(10, 18), W=(2.8, 4.0), ridge=0.25, steps=3, jit=0.3)
        paint.append(f'<g {D.clip(f"<path d=\"{d}\"/>")}>{B.render()}</g>')
        paint.append(ink(d, "#06100A", 1.8, 9 + k, 1, 0.7))
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.07)}{varnish(D, box, 0.12, 0.2)}</g>')
    out.append(plaque(D, 300, 500, 340, 60, "Wheat Field with Cypresses", "VAN GOGH · 1889", 3, ts=23, bs=17))
    return finish(D, out, 19)


# ================================================================ 6. Irises — Van Gogh, 1889
def iris_flower(D, cx, cy, s, seed, pal, rot=0):
    """Bearded iris: three drooping falls and three upright standards, each petal painted with strokes
    that follow its veins, and inked like a Japanese print."""
    rnd = random.Random(seed)
    light, base, dark = pal
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def T(pts):
        return [(cx + (x * c - y * sn) * s, cy + (x * sn + y * c) * s) for x, y in pts]
    out = []
    specs = [
        ([(-0.08, -0.05), (-0.42, -0.4), (-0.36, -0.82), (-0.12, -0.7)], (light, base, dark), -100),
        ([(0.08, -0.05), (0.42, -0.4), (0.36, -0.82), (0.12, -0.7)], (base, dark, dk(dark, 0.3)), -80),
        ([(-0.13, -0.05), (-0.22, -0.55), (-0.02, -1.0), (0.2, -0.58), (0.12, -0.05)], (lt(light, 0.2), light, base), -90),
        ([(-0.05, 0.0), (-0.5, -0.1), (-0.88, 0.25), (-0.66, 0.58), (-0.28, 0.34)], (light, base, dark), 150),
        ([(0.05, 0.0), (0.5, -0.1), (0.88, 0.25), (0.66, 0.58), (0.28, 0.34)], (base, dark, dk(dark, 0.3)), 30),
        ([(-0.2, 0.02), (0.2, 0.02), (0.26, 0.5), (0.02, 0.8), (-0.24, 0.5)], (light, base, dark), 90),
    ]
    for k, (pts, pp, ang) in enumerate(specs):
        P = jitter(T(pts), seed + k, s * 0.02)
        out.append(painted(D, P, pp, seed * 7 + k, sk=0.14, angle=ang + rot, n=int(s * 0.9), slen=(s * 0.12, s * 0.35), sw=(s * 0.03, s * 0.07),
                           inkc="#120E36", inkw=max(1.3, s * 0.05), inkop=0.8, hi=0.35))
    # white throat streaks and the golden beard on the falls
    for k in range(8):
        a = rnd.uniform(-0.7, 0.7)
        p0 = T([(0, 0.08)])[0]
        p1 = T([(0.45 * math.sin(a), 0.08 + 0.38 * math.cos(a))])[0]
        out.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f}L{p1[0]:.1f} {p1[1]:.1f}" stroke="{rnd.choice(["#FFFFFF", lt(light, 0.5)])}" stroke-width="{max(1.2, s * 0.04):.1f}" opacity="0.6" stroke-linecap="round"/>')
    b0, b1 = T([(0, 0.1), (0, 0.38)])
    out.append(f'<path d="M{b0[0]:.1f} {b0[1]:.1f}L{b1[0]:.1f} {b1[1]:.1f}" stroke="#F2C030" stroke-width="{max(2, s * 0.1):.1f}" stroke-linecap="round"/>')
    return "".join(out)


def sword_leaf(x, y, L, ang, w, cols, seed, bend=0.15):
    rnd = random.Random(seed)
    a = math.radians(ang)
    pts = []
    for i in range(6):
        t = i / 5
        aa = a + bend * t * t * 2
        pts.append((x + L * t * math.cos(aa), y + L * t * math.sin(aa)))
    out = [taper(pts, w + 2.2, 1.5, "#0E2A1E"), taper(pts, w, 0.6, cols[1])]
    out.append(taper([(px - w * 0.2, py) for px, py in pts], w * 0.4, 0.4, cols[0], 0.7))
    out.append(taper([(px + w * 0.25, py) for px, py in pts], w * 0.25, 0.3, cols[2], 0.8))
    return "".join(out)


@design("irises")
def irises():
    D = Doc("gmir")
    box = (66, 60, 534, 424)   # 468 x 364 (71 x 93 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H
    out = [wall(D, "#3E4A3A", 51, (0.5, 0.2), 0.25)]
    out.append(simple_frame(D, box, 18, ("#E8DCC4", "#B8A482", "#6A5A40"), 5))
    out.append(f'<rect x="{x0 - 4}" y="{y0 - 4}" width="{W + 8}" height="{H + 8}" fill="none" stroke="#4A3A28" stroke-width="2"/>')
    cp = clip_box(D, box)
    paint = []
    B = Brush()
    rnd = random.Random(5)
    # background: meadow green with a band of yellow and orange flowers at the top
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="#6A9A4A"/>')
    impasto(B, lambda x, y: math.radians(-80 + 20 * math.sin(x / 20)), lambda x, y: True, 1700,
            lambda x, y, r: r.choice(["#7AAA4A", "#5A8A3A", "#8AB858", "#9AC060", "#6A9A40", "#B8C868"]) if y < Y(0.45) else
            r.choice(["#4A7A3A", "#3A6A3A", "#5A8A4A", "#2E5A34", "#6A9A50"]), 3, L=(8, 14), W=(3, 4), ridge=0.25)
    paint.append(B.render())
    for k in range(70):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, Y(0.22))
        col = rnd.choice(["#F2A020", "#E8801A", "#F6C030"]) if x < X(0.35) else rnd.choice(["#F6E060", "#F2D040", "#FFF0A0"])
        B.dot(x, y, rnd.uniform(2.4, 4), col)
        B.dot(x - 0.8, y - 0.8, 1, "#FFF6C8", 0.7)
    paint.append(B.render())
    # red earth in the lower left with marigolds
    earth = [(x0 - 10, Y(0.68)), (X(0.12), Y(0.7)), (X(0.3), Y(0.82)), (X(0.42), y1 + 10), (x0 - 10, y1 + 10)]
    paint.append(f'<path d="{pd(earth)}" fill="#B8602A"/>')
    impasto(B, lambda x, y: math.radians(-20), earth, 260, lambda x, y, r: r.choice(["#C8703A", "#A85020", "#D88A4A", "#984418", "#E09A5A"]), 6, L=(8, 14), W=(3, 4), ridge=0.3)
    paint.append(B.render())
    for k in range(9):
        x, y = rnd.uniform(X(0.0), X(0.24)), rnd.uniform(Y(0.74), Y(0.98))
        if not inside((x, y), earth):
            continue
        for i in range(8):
            a = i * math.pi / 4
            B.dash([(x, y), (x + 5 * math.cos(a), y + 5 * math.sin(a))], rnd.choice(["#F28A1A", "#F6A830", "#E86A10"]), 3)
        B.dot(x, y, 2.2, "#A84A10")
    paint.append(B.render())
    # leaves: a thicket of blue-green swords
    leaf_cols = [("#7ABAA0", "#3E8A6A", "#1E5A44"), ("#8AC08A", "#4A8A5A", "#24563A"), ("#6AA8B0", "#3A7A88", "#1A4A5A")]
    leaves = []
    for k in range(110):
        bx = rnd.uniform(X(0.1), X(1.05))
        by = rnd.uniform(Y(0.55), y1 + 40)
        if inside((bx, by), earth):
            continue
        L = rnd.uniform(70, 120)
        ang = rnd.uniform(-112, -68)
        leaves.append((by, sword_leaf(bx, by, L, ang, rnd.uniform(13, 18), rnd.choice(leaf_cols), k, rnd.uniform(-0.18, 0.18) + (0.25 if ang < -90 else -0.25) * rnd.random())))
    # flowers among the leaves
    flowers = []
    spots = [(0.2, 0.34), (0.33, 0.44), (0.42, 0.27), (0.54, 0.4), (0.66, 0.28), (0.76, 0.44), (0.88, 0.3), (0.98, 0.46),
             (0.6, 0.6), (0.8, 0.64), (0.44, 0.6), (0.7, 0.8), (0.92, 0.82), (0.26, 0.56)]
    for i, (u, v) in enumerate(spots):
        pal = rnd.choice([("#8A7AE0", "#4A3AB0", "#24186A"), ("#7A8AE0", "#3A4AA8", "#1A2268"), ("#A07AD8", "#5A36A0", "#2A1660")])
        if i == 2:
            pal = ("#FFFFFF", "#E8ECF0", "#9AA8B8")
        s = rnd.uniform(32, 38) * (0.85 + 0.3 * v)
        flowers.append((Y(v) + 10, iris_flower(D, X(u) + rnd.uniform(-6, 6), Y(v) + rnd.uniform(-6, 6), s, 100 + i, pal, rnd.uniform(-15, 15))))
    for _, svg in sorted(leaves[:40] + flowers[:9] + leaves[40:] + flowers[9:], key=lambda q: q[0]):
        paint.append(svg)
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.07)}{varnish(D, box, 0.12, 0.2)}</g>')
    out.append(museum_label(D, 480, "Irises", "VINCENT VAN GOGH · 1889", "#F4EEDC", "#D8CCA8", ts=32, bs=18, gap=30))
    return finish(D, out, 23)


# ================================================================ 7. Water Lilies — Monet, 1906
def lily_pad(B, cx, cy, rx, ry, seed, pal):
    """A lily pad seen in perspective: a notched ellipse of short dabs, darker at the back edge."""
    rnd = random.Random(seed)
    light, base, dark = pal
    notch = rnd.uniform(0, 2 * math.pi)
    out = []
    for i in range(int(rx * ry / 6) + 6):
        a = rnd.uniform(0, 2 * math.pi)
        if abs((a - notch + math.pi) % (2 * math.pi) - math.pi) < 0.25:
            continue
        r = math.sqrt(rnd.random()) * 0.9
        x, y = cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)
        col = light if math.sin(a) > 0.2 and rnd.random() < 0.6 else (dark if math.sin(a) < -0.4 and rnd.random() < 0.6 else base)
        L = rx * rnd.uniform(0.2, 0.4)
        B.dash([(x - L / 2, y + rnd.uniform(-0.5, 0.5)), (x + L / 2, y + rnd.uniform(-0.5, 0.5))], rnd.choice([col, col, mix(col, "#C8B8E0", 0.25)]), max(2.4, ry * rnd.uniform(0.4, 0.6)))


def lily_flower(B, cx, cy, s, seed, cols):
    rnd = random.Random(seed)
    for i in range(9):
        a = rnd.uniform(math.pi * 1.05, math.pi * 1.95)
        L = s * rnd.uniform(0.6, 1.0)
        B.dash([(cx + rnd.uniform(-s * 0.3, s * 0.3), cy), (cx + L * math.cos(a) * 0.8, cy + L * math.sin(a) * 0.9)], rnd.choice(cols), s * 0.32)
    B.dash([(cx - s * 0.5, cy + s * 0.1), (cx + s * 0.5, cy + s * 0.1)], cols[-1], s * 0.3)
    B.dot(cx, cy - s * 0.15, s * 0.16, "#F2D048")


@design("water-lilies")
def water_lilies():
    D = Doc("gmwl")
    box = (66, 56, 534, 456)   # 468 x 400
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H
    out = [wall(D, "#B8B0C4", 61, (0.5, 0.2), 0.2)]
    out.append(simple_frame(D, box, 12, ("#FFFDF4", "#E8E0CC", "#A89C84"), 5))
    out.append(f'<rect x="{x0 - 3}" y="{y0 - 3}" width="{W + 6}" height="{H + 6}" fill="none" stroke="#C8A860" stroke-width="2"/>')
    cp = clip_box(D, box)
    paint = []
    B = Brush()
    rnd = random.Random(3)
    # the pond surface: sky reflections in lilac, blue and rose, with willow reflections falling vertically
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.lin([(0, "#4A6A7A"), (0.45, "#7A92B8"), (1, "#9AAAD0")])}"/>')

    def water(x, y, r):
        v = (y - y0) / H
        willow = 0.5 + 0.5 * math.sin(x / 26 + 1.3) * math.sin(x / 61)
        if v < 0.55 and willow > 0.62 and r.random() < 0.75:
            return r.choice(["#2E4A3A", "#3E5A4A", "#4A6A4A", "#24403A", "#5A7A5A"])
        if r.random() < 0.18:
            return r.choice(["#E8C8D8", "#F2D8DC", "#D8B8D0"])
        return r.choice(["#8A9ACB", "#7A8CC0", "#A2AED6", "#6A80B0", "#B8BEDC", "#94A8C8", "#5A7298"]) if v > 0.3 else r.choice(["#5A7488", "#6A8098", "#4A6478", "#7A90A8", "#3E5A64"])
    paint.append(under(D, box, lambda x, y, r: water(x, y, r), 90, 6, (20, 50), (0.3, 0.6), 0.5))
    dabs(B, lambda x, y: True, 5200, water, 5, L=(5, 11), W=(3.4, 6), angle=lambda x, y: 90 if 0.5 + 0.5 * math.sin(x / 26 + 1.3) * math.sin(x / 61) > 0.62 and y < Y(0.55) else 0, spread=14, op=(0.6, 0.95))
    paint.append(B.render())
    # lily pads in drifting islands, smaller and flatter with distance
    pads = []
    for isl, (u, v, n) in enumerate([(0.2, 0.18, 8), (0.66, 0.14, 9), (0.4, 0.4, 10), (0.84, 0.46, 9), (0.14, 0.64, 10), (0.56, 0.72, 11), (0.92, 0.86, 7), (0.3, 0.93, 8)]):
        for k in range(n):
            px = X(u) + rnd.gauss(0, 30 + v * 30)
            py = Y(v) + rnd.gauss(0, 7 + v * 9)
            sc = 0.5 + v * 0.8
            pads.append((py, px, 22 * sc * rnd.uniform(0.8, 1.25), 7 * sc * rnd.uniform(0.8, 1.1), rnd.randint(0, 9999)))
    pads.sort()
    for py, px, rx, ry, sd in pads:
        pal = random.Random(sd).choice([("#9ABA6A", "#5E8A4A", "#2E5A3A"), ("#B8C878", "#7A9A50", "#3E6A3A"), ("#8AAA7A", "#4E7A5A", "#2A4A3A")])
        lily_pad(B, px, py, rx, ry, sd, pal)
    paint.append(B.render())
    for k, (py, px, rx, ry, sd) in enumerate(pads):
        if k % 4 == 0:
            cols = random.Random(sd).choice([["#F2A8B8", "#E87A98", "#FFD0D8", "#FFFFFF"], ["#FFFFFF", "#F6E8EC", "#E8D0E0", "#FFF4F4"], ["#F8C8A8", "#F2A890", "#FFE0C8", "#FFF6E8"]])
            lily_flower(B, px + rnd.uniform(-rx * 0.3, rx * 0.3), py - ry * 0.3, ry * 1.5, sd, cols)
    paint.append(B.render())
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.06)}{varnish(D, box, 0.1, 0.15, 6, 0.3)}</g>')
    out.append(museum_label(D, 498, "Water Lilies", "CLAUDE MONET · 1906", "#2E2840", "#5A5070", ts=30, bs=18, gap=28))
    return finish(D, out, 29)


# ================================================================ 8. Impression, Sunrise — Monet, 1872
def boat_silhouette(x, y, s, col, rower=True, flip=1):
    hull = [(x - 26 * s * flip, y - 2 * s), (x + 22 * s * flip, y - 4 * s), (x + 16 * s * flip, y + 3 * s), (x - 20 * s * flip, y + 3 * s)]
    out = [f'<path d="{smooth_closed(hull)}" fill="{col}"/>']
    if rower:
        out.append(f'<path d="{smooth_closed([(x - 6 * s * flip, y - 3 * s), (x - 4 * s * flip, y - 16 * s), (x + 1 * s * flip, y - 19 * s), (x + 4 * s * flip, y - 14 * s), (x + 3 * s * flip, y - 3 * s)])}" fill="{col}"/>')
        out.append(f'<circle cx="{x - 1 * s * flip:.1f}" cy="{y - 21 * s:.1f}" r="{3.2 * s:.1f}" fill="{col}"/>')
        out.append(f'<path d="M{x - 10 * s * flip:.1f} {y - 12 * s:.1f}L{x + 26 * s * flip:.1f} {y + 6 * s:.1f}" stroke="{col}" stroke-width="{1.8 * s:.1f}"/>')
    return "".join(out)


@design("impression-sunrise")
def impression_sunrise():
    D = Doc("gmis")
    box = (78, 78, 522, 414)   # 444 x 336 (48 x 63 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H
    out = [wall(D, "#2E3436", 71, (0.5, 0.15), 0.3)]
    out.append(gilt_frame(D, box, 34, 73, "ornate"))
    cp = clip_box(D, box)
    paint = []
    B = Brush()
    rnd = random.Random(4)
    sun = (X(0.56), Y(0.37), 15)
    # misty harbour: blue-grey dabs warming toward the sun
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.lin([(0, "#8A9A9C"), (0.4, "#9A9E98"), (0.55, "#7A8C92"), (1, "#3E5A6A")])}"/>')
    paint.append(soft_glow(D, sun[0], sun[1], 150, "#F2A070", 0.45))

    def mist(x, y, r):
        d = math.hypot(x - sun[0], (y - sun[1]) * 1.4)
        v = (y - y0) / H
        if d < 70 and r.random() < 0.7:
            return r.choice(["#E8A080", "#D89A88", "#F0B898", "#C8A0A0"])
        if v < 0.5:
            return r.choice(["#9AA6A6", "#8A9A9E", "#A8AEA8", "#B0A8A0", "#7E9096", "#C0AAA0"])
        return r.choice(["#5A7A88", "#4A6A7A", "#6A8A96", "#3A5A6C", "#7A9AA4", "#5E8090"])
    paint.append(under(D, box, lambda x, y, r: mist(x, y, r), 70, 7, (25, 60), (0.3, 0.6), 0.45))
    dabs(B, lambda x, y: True, 2600, mist, 7, L=(8, 16), W=(3.8, 6.4), angle=lambda x, y: -15 if y < Y(0.52) else 0, spread=14, op=(0.45, 0.9))
    paint.append(B.render())
    # the port behind the mist: cranes, masts, chimneys with smoke
    ghost = []
    for k, (u, h) in enumerate([(0.06, 0.3), (0.1, 0.36), (0.14, 0.26), (0.22, 0.4), (0.28, 0.34), (0.35, 0.3), (0.72, 0.28), (0.8, 0.36), (0.86, 0.3), (0.93, 0.42)]):
        bx = X(u)
        ghost.append(f'<path d="M{bx:.1f} {Y(0.52):.1f}L{bx + rnd.uniform(-2, 2):.1f} {Y(0.52 - h):.1f}" stroke="#6E7A84" stroke-width="{rnd.uniform(1.6, 2.6):.1f}" opacity="0.6"/>')
        if k % 3 == 0:
            ghost.append(f'<path d="M{bx - 10:.1f} {Y(0.52 - h * 0.7):.1f}L{bx + 10:.1f} {Y(0.52 - h * 0.75):.1f}" stroke="#6E7A84" stroke-width="1.6" opacity="0.55"/>')
    ghost.append(f'<path d="{smooth_closed([(x0 - 5, Y(0.54)), (X(0.4), Y(0.5)), (X(0.42), Y(0.53)), (X(0.7), Y(0.52)), (x1 + 5, Y(0.5)), (x1 + 5, Y(0.56)), (x0 - 5, Y(0.57))])}" fill="#6E7E88" opacity="0.6"/>')
    for u in (0.2, 0.84):
        ghost.append(f'<path d="{blob(X(u), Y(0.18), 26, 12, int(u * 99), 0.2, 12)}" fill="#B8A8A0" opacity="0.4"/>')
    paint.append("".join(ghost))
    # the sun and its orange path broken on the water
    sx, sy, sr = sun
    paint.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="#F26A1E"/><circle cx="{sx - 3}" cy="{sy - 3}" r="{sr * 0.6}" fill="#FF8A3A" opacity="0.7"/>')
    for k in range(13):
        yy = Y(0.6) + k * 9.5 + rnd.uniform(-2, 2)
        L = 26 - k * 0.8 + rnd.uniform(-4, 4)
        xx = sx + rnd.uniform(-8, 8) + (k * 0.6)
        B.dash([(xx - L / 2, yy), (xx + L / 2, yy + rnd.uniform(-1, 1))], rnd.choice(["#F26A1E", "#F6852A", "#E85A18", "#FF9A4A"]), rnd.uniform(3.4, 5))
    paint.append(B.render())
    # boats: one near, dark and decisive; two fading behind
    paint.append(boat_silhouette(X(0.33), Y(0.8), 1.25, "#1E2A3A"))
    paint.append(boat_silhouette(X(0.48), Y(0.66), 0.75, "#2E3E4E", True, -1))
    paint.append(boat_silhouette(X(0.7), Y(0.6), 0.5, "#4A5A68", True))
    for x, y, L in ((X(0.33), Y(0.83), 70), (X(0.48), Y(0.675), 40)):
        for k in range(5):
            B.dash([(x - L / 2 + rnd.uniform(-6, 6), y + k * 4), (x + L / 2 + rnd.uniform(-6, 6), y + k * 4)], rnd.choice(["#1E2A3A", "#2E3E4E", "#3A4A5A"]), 2.6, 0.5)
    paint.append(B.render())
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.07)}{varnish(D, box, 0.12, 0.25)}</g>')
    out.append(museum_label(D, 494, "Impression, Sunrise", "CLAUDE MONET · 1872", "#F2E6CC", "#C8B898", ts=29, bs=18, gap=28))
    return finish(D, out, 31)


# ================================================================ 9. Poppy Field — Monet, 1873
def monet_figure(B, x, base, h, seed, dress="#1E2A3A", parasol="#3A6A8A", child=False, hat="#2A2A2A"):
    """A figure in Monet's shorthand: a few decisive dabs for dress, hat, face and parasol."""
    rnd = random.Random(seed)
    out = []
    w = h * 0.32
    dress_pts = [(x - w * 0.55, base), (x - w * 0.22, base - h * 0.62), (x + w * 0.22, base - h * 0.62), (x + w * 0.6, base)]
    out.append(f'<path d="{smooth_closed(dress_pts)}" fill="{dress}"/>')
    for k in range(int(h * 0.6)):
        t = rnd.random()
        yy = base - t * h * 0.6
        hw = w * (0.55 - 0.35 * t)
        xx = x + rnd.uniform(-hw, hw)
        B.dash([(xx, yy), (xx + rnd.uniform(-1, 1), yy - h * 0.12)], rnd.choice([dress, lt(dress, 0.25), dk(dress, 0.3)]), max(1.6, h * 0.07))
    out.append(B.render())
    out.append(f'<path d="{blob(x, base - h * 0.68, w * 0.24, h * 0.06, seed, 0.1, 8)}" fill="{lt(dress, 0.2)}"/>')
    out.append(f'<circle cx="{x:.1f}" cy="{base - h * 0.775:.1f}" r="{h * 0.062:.1f}" fill="#B88A74"/>')
    out.append(f'<path d="{blob(x - h * 0.02, base - h * 0.765, h * 0.03, h * 0.035, seed + 2, 0.1, 8)}" fill="#E0B49A" opacity="0.8"/>')
    out.append(f'<path d="{blob(x, base - h * 0.825, h * 0.13, h * 0.035, seed + 1, 0.1, 8)}" fill="{hat}"/>')
    out.append(f'<path d="{blob(x, base - h * 0.85, h * 0.06, h * 0.035, seed + 3, 0.1, 8)}" fill="{hat}"/>')
    if child:
        out.append(f'<path d="M{x - h * 0.05:.1f} {base - h * 0.86:.1f}l{h * 0.1:.1f} {-h * 0.02:.1f}" stroke="#D8301E" stroke-width="{max(1.6, h * 0.04):.1f}" stroke-linecap="round"/>')
    if parasol:
        px, py = x + h * 0.08, base - h * 1.0
        out.append(f'<path d="M{x + h * 0.06:.1f} {base - h * 0.6:.1f}L{px:.1f} {py:.1f}" stroke="#3A2A1A" stroke-width="1.4"/>')
        out.append(f'<path d="M{px - h * 0.3:.1f} {py + h * 0.08:.1f}Q{px:.1f} {py - h * 0.2:.1f} {px + h * 0.3:.1f} {py + h * 0.08:.1f}Q{px:.1f} {py:.1f} {px - h * 0.3:.1f} {py + h * 0.08:.1f}Z" fill="{parasol}"/>')
        out.append(f'<path d="M{px - h * 0.2:.1f} {py - h * 0.02:.1f}Q{px - h * 0.05:.1f} {py - h * 0.15:.1f} {px + h * 0.12:.1f} {py - h * 0.08:.1f}" stroke="{lt(parasol, 0.4)}" stroke-width="{max(1.2, h * 0.03):.1f}" fill="none"/>')
    return "".join(out)


@design("poppy-field")
def poppy_field():
    D = Doc("gmpf")
    box = (72, 64, 528, 414)   # 456 x 350 (50 x 65 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H
    out = [mat_board(D, (x0 - 8, y0 - 8, x1 + 8, y1 + 8), 8, "#E8E4D8", 81)]
    out.append(gilt_frame(D, box, 10, 83, "plain", gold=("#FFF6D8", "#E6D29A", "#C0A868", "#8A7038", "#4A3A18")))
    cp = clip_box(D, box)
    paint = []
    B = Brush()
    rnd = random.Random(6)
    # summer sky with soft white clouds
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.lin([(0, "#8AB0D8"), (0.5, "#B8D0E4")])}"/>')

    def sky(x, y, r):
        c = 0.5 + 0.5 * math.sin(x / 40 + 1) * math.cos(y / 22)
        if c > 0.55 and r.random() < 0.8:
            return r.choice(["#FFFFFF", "#F4F2EE", "#E8ECF0", "#F8F0E8", "#DCE2EA"])
        return r.choice(["#8AB0D8", "#9ABCDE", "#A8C6E2", "#7AA4D0", "#B8D0E6"])
    paint.append(under(D, (x0, y0, x1, Y(0.5)), lambda x, y, r: sky(x, y, r), 50, 8, (25, 55), (0.4, 0.7), 0.55))
    dabs(B, lambda x, y: y < Y(0.5), 1700, sky, 8, L=(6, 12), W=(4, 6.5), angle=-10, spread=30, op=(0.6, 0.95))
    paint.append(B.render())
    # tree line and a red-roofed house
    tl = rough([(x0 - 10, Y(0.5)), (X(0.15), Y(0.38)), (X(0.3), Y(0.42)), (X(0.45), Y(0.36)), (X(0.6), Y(0.44)), (X(0.75), Y(0.4)), (X(0.85), Y(0.46)), (x1 + 10, Y(0.44))], 3, 10, 4)
    tpoly = tl + [(x1 + 10, Y(0.56)), (x0 - 10, Y(0.56))]
    paint.append(f'<path d="{pd(tpoly)}" fill="#3E5A3A"/>')
    dabs(B, tpoly, 600, lambda x, y, r: r.choice(["#2E4A30", "#4A6A3E", "#5A7A48", "#3A5A40", "#6A8A50", "#24402A"]), 9, L=(5, 10), W=(3.4, 5), angle=-70, spread=50)
    paint.append(B.render())
    hx, hy = X(0.66), Y(0.47)
    paint.append(f'<path d="{pd([(hx - 14, hy), (hx - 14, hy - 12), (hx + 14, hy - 12), (hx + 14, hy)])}" fill="#E8DCC0"/><path d="{pd([(hx - 17, hy - 11), (hx, hy - 22), (hx + 17, hy - 11)])}" fill="#B8503A"/>')
    # the meadow: a green slope, a diagonal river of poppies falling to the lower left
    field = [(x0 - 10, Y(0.52)), (x1 + 10, Y(0.5)), (x1 + 10, y1 + 10), (x0 - 10, y1 + 10)]
    paint.append(f'<path d="{pd(field)}" fill="#7A9A4A"/>')
    diag = lambda x, y: (y - Y(0.5)) / H - (1 - (x - x0) / W) * 0.55

    def meadow(x, y, r):
        dd = diag(x, y)
        if dd > -0.05 and r.random() < 0.55 + min(0.3, dd):
            return r.choice(["#D8301E", "#E84A2A", "#C02818", "#F0603A", "#B82014"])
        v = (y - Y(0.5)) / (H * 0.5)
        return r.choice(["#8AA850", "#6A8A40", "#A8B860", "#5A7A3A", "#B8C070", "#7A9A68", "#C8C890"]) if v < 0.6 else r.choice(["#6A8A3A", "#4E6E30", "#8AA048", "#5E7A3A"])
    paint.append(under(D, (x0, Y(0.5), x1, y1), lambda x, y, r: meadow(x, y, r), 60, 10, (20, 50), (0.4, 0.7), 0.5))
    dabs(B, field, 2800, meadow, 10, L=(4, 9), W=(3.6, 5.8), angle=-80, spread=60)
    paint.append(B.render())
    # mother and child, near and far
    paint.append(monet_figure(B, X(0.78), Y(0.97), 92, 11, "#1E2838", "#2E5A7A", hat="#222"))
    paint.append(monet_figure(B, X(0.86), Y(0.98), 50, 12, "#C8D0E0", None, True, "#E8C878"))
    paint.append(monet_figure(B, X(0.22), Y(0.6), 36, 13, "#2A3040", "#7A3A3A", hat="#2A2A2A"))
    paint.append(monet_figure(B, X(0.27), Y(0.61), 22, 14, "#3A4A5A", None, True, "#E8D8B0"))
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.06)}{varnish(D, box, 0.1, 0.15, 6, 0.3)}</g>')
    out.append(museum_label(D, 474, "Poppy Field", "CLAUDE MONET · 1873", "#3A2E22", "#6A5A44", ts=30, bs=18, gap=30))
    return finish(D, out, 37)


# ================================================================ 10. The Japanese Footbridge — Monet, 1899
@design("the-japanese-footbridge")
def japanese_footbridge():
    D = Doc("gmjf")
    box = (60, 52, 540, 450)   # 480 x 398 (89 x 93 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H
    out = [f'<rect width="600" height="600" fill="#2A3A2A"/>']
    out.append(gilt_frame(D, (x0 - 12, y0 - 12, x1 + 12, y1 + 12), 60, 91, "ornate"))
    out.append(simple_frame(D, box, 12, ("#F4ECD8", "#D8CCB0", "#9A8C70"), 2))
    cp = clip_box(D, box)
    paint = []
    B = Brush()
    rnd = random.Random(8)
    # dense garden foliage: vertical dabs of every green, a few lilac wisteria touches
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="#3E6A3A"/>')

    def foliage(x, y, r):
        if r.random() < 0.08:
            return r.choice(["#C8B8D8", "#E0D0E0", "#F2E8A0"])
        v = (y - y0) / H
        return r.choice(["#6A9A40", "#8AB050", "#4A7A3A", "#A8C060", "#2E5A30", "#5A8A50", "#C8D070", "#3A6A48", "#7AA868"]) if v < 0.5 else \
            r.choice(["#4A7A3A", "#2E5A30", "#5A8A50", "#3A6A48", "#6A9A58", "#24482A"])
    paint.append(under(D, (x0, y0, x1, Y(0.46)), lambda x, y, r: foliage(x, y, r), 60, 11, (20, 50), (0.5, 0.8), 0.7))
    dabs(B, lambda x, y: y < Y(0.46), 3200, foliage, 11, L=(4, 9), W=(4, 6.5), angle=lambda x, y: -90 + 40 * math.sin(x / 30 + y / 20), spread=70)
    paint.append(B.render())
    # pond: reflections of the foliage broken by horizontal light
    pond = [(x0 - 5, Y(0.45)), (x1 + 5, Y(0.45)), (x1 + 5, y1 + 5), (x0 - 5, y1 + 5)]

    def pond_c(x, y, r):
        if r.random() < 0.3:
            return r.choice(["#8AB0A8", "#A8C8B8", "#C8D8C0", "#7A9AA8"])
        return r.choice(["#3E6A48", "#2E5A3A", "#4A7A50", "#5A8A5A", "#24482E", "#6A9A68"])
    paint.append(under(D, (x0, Y(0.45), x1, y1), lambda x, y, r: pond_c(x, y, r), 50, 12, (25, 55), (0.4, 0.7), 0.4))
    dabs(B, pond, 2400, pond_c, 12, L=(6, 13), W=(3.6, 5.6), angle=lambda x, y: 90 if math.sin(x / 18) > 0.3 else 0, spread=12)
    paint.append(B.render())
    # lily pads drifting in horizontal bands
    pads = []
    for band, (v, n, sc) in enumerate([(0.56, 12, 0.6), (0.66, 11, 0.8), (0.78, 10, 1.0), (0.9, 9, 1.25)]):
        for k in range(n):
            px = X(rnd.uniform(-0.02, 1.02))
            py = Y(v + rnd.uniform(-0.03, 0.03))
            pads.append((py, px, 22 * sc * rnd.uniform(0.8, 1.2), 7 * sc, rnd.randint(0, 9999)))
    pads.sort()
    for py, px, rx, ry, sd in pads:
        lily_pad(B, px, py, rx, ry, sd, random.Random(sd).choice([("#B8D078", "#7AA050", "#3E6A3A"), ("#C8D888", "#8AAA58", "#4A7A40")]))
    paint.append(B.render())
    for k, (py, px, rx, ry, sd) in enumerate(pads):
        if k % 3 == 0:
            lily_flower(B, px + rnd.uniform(-5, 5), py - ry * 0.3, ry * 1.5, sd, random.Random(sd).choice([["#F2A8B8", "#E87A98", "#FFD0D8", "#FFFFFF"], ["#FFFFFF", "#F6E8EC", "#E8D0E0"]]))
    paint.append(B.render())
    # the footbridge: a shallow blue-green arch with railings
    def arch(t, lift):
        x = x0 - 20 + (W + 40) * t
        return x, Y(0.47) - lift * math.sin(math.pi * t) * H * 0.14
    deck_top = [arch(t / 30, 1) for t in range(31)]
    deck_bot = [(x, y + 12) for x, y in deck_top]
    rail_top = [(x, y - 36) for x, y in deck_top]
    rail_mid = [(x, y - 19) for x, y in deck_top]
    BR = ["#5E8A7A", "#7AA890", "#4A7A6A", "#9AC0A8", "#3A6A5A"]
    paint.append(f'<path d="{pd(deck_top + deck_bot[::-1])}" fill="#4A7A68"/>')
    for k in range(31):
        x, y = deck_top[k]
        B.dash([(x, y + 1), (x, y - 36)], rnd.choice(BR), 4.4)
    for line in (rail_top, rail_mid):
        for (ax, ay), (bx, by) in zip(line, line[1:]):
            B.dash([(ax, ay), (bx, by)], rnd.choice(BR), 5.4)
    for (ax, ay), (bx, by) in zip(deck_top, deck_top[1:]):
        B.dash([(ax, ay + 3), (bx, by + 3)], rnd.choice(["#3A6A5A", "#2E5A4A", "#5A8A78"]), 7)
        B.dash([(ax, ay + 9), (bx, by + 9)], rnd.choice(["#2E5A4A", "#24483C", "#3A6A5A"]), 6)
    paint.append(B.render())
    for (ax, ay), (bx, by) in zip(rail_top[::2], rail_top[2::2]):
        B.dash([(ax, ay - 1.5), (bx, by - 1.5)], rnd.choice(["#C8E0C0", "#D8E8B8", "#B8D8C8"]), 1.8, 0.8)
    paint.append(B.render())
    # the bridge's reflection
    for k in range(40):
        t = rnd.random()
        x, y = arch(t, 1)
        ry_ = Y(0.52) + (Y(0.47) - y) * 0.6 + rnd.uniform(0, 10)
        B.dash([(x - 6, ry_), (x + 6, ry_)], rnd.choice(["#4A7A68", "#5E8A7A", "#3A6A5A"]), 3, 0.6)
    paint.append(B.render())
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.06)}{varnish(D, box, 0.1, 0.18, 6, 0.3)}</g>')
    out.append(plaque(D, 300, 503, 330, 54, "The Japanese Footbridge", "CLAUDE MONET · 1899", 4, ts=22, bs=16))
    return finish(D, out, 41)


# ================================================================ 11. The Great Wave off Kanagawa — Hokusai, c. 1831
KEY = "#1C1E2C"      # woodblock key-line ink
PRUSSIAN = ("#7AA2C8", "#2E5A8E", "#16305C")


def washi(D, box, base="#EFE3C6", seed=1, fibres=90):
    """Woodblock paper: warm ground, soft mottling and long kozo fibres."""
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{base}"/>',
           blooms(seed, [dk(base, 0.08), lt(base, 0.3)], 6, box, (40, 120), (0.06, 0.12))]
    fib = "".join(f'<path d="M{(x := rnd.uniform(x0, x1)):.0f} {(y := rnd.uniform(y0, y1)):.0f}q{rnd.uniform(-8, 8):.0f} {rnd.uniform(-3, 3):.0f} {rnd.uniform(-18, 18):.0f} {rnd.uniform(-6, 6):.0f}"/>' for _ in range(fibres))
    out.append(f'<g fill="none" stroke="{dk(base, 0.25)}" stroke-width="0.7" opacity="0.25">{fib}</g>')
    return "".join(out)


def woodgrain(D, box, op=0.08, seed=3, col="#5A3A1A"):
    """The faint grain of the printing block showing in a flat area."""
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    lines = []
    y = y0
    while y < y1:
        y += rnd.uniform(3, 7)
        pts = [(x0 + (x1 - x0) * t / 8, y + rnd.uniform(-1.5, 1.5)) for t in range(9)]
        lines.append(f'<path d="{smooth_open(pts)}"/>')
    return f'<g fill="none" stroke="{col}" stroke-width="0.8" opacity="{op}">{"".join(lines)}</g>'


def hanko(x, y, s, col="#C0301E", seed=1):
    """A red seal stamp with worn edges and a carved abstract mark (no lettering)."""
    rnd = random.Random(seed)
    out = [f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="2" fill="{col}"/>',
           f'<rect x="{x + s * 0.12:.1f}" y="{y + s * 0.12:.1f}" width="{s * 0.76:.1f}" height="{s * 0.76:.1f}" fill="none" stroke="#F6E6D0" stroke-width="{s * 0.06:.1f}"/>',
           f'<path d="M{x + s * 0.28:.1f} {y + s * 0.3:.1f}h{s * 0.3:.1f}q{s * 0.12:.1f} 0 {s * 0.12:.1f} {s * 0.14:.1f}t{-s * 0.14:.1f} {s * 0.12:.1f}h{-s * 0.1:.1f}v{s * 0.18:.1f}h{s * 0.26:.1f}M{x + s * 0.34:.1f} {y + s * 0.42:.1f}v{s * 0.3:.1f}" stroke="#F6E6D0" stroke-width="{s * 0.07:.1f}" fill="none" stroke-linecap="round"/>']
    for _ in range(6):
        out.append(f'<circle cx="{x + rnd.uniform(0, s):.1f}" cy="{y + rnd.uniform(0, s):.1f}" r="{rnd.uniform(0.6, 1.4):.1f}" fill="#F6E6D0" opacity="0.7"/>')
    return "".join(out)


def resample(curve, n):
    """Resample an open polyline to n points evenly by length."""
    L = [0]
    for (ax, ay), (bx, by) in zip(curve, curve[1:]):
        L.append(L[-1] + math.hypot(bx - ax, by - ay))
    out = []
    for i in range(n):
        t = L[-1] * i / (n - 1)
        j = max(0, min(len(L) - 2, next((k for k in range(len(L) - 1) if L[k + 1] >= t), len(L) - 2)))
        f = (t - L[j]) / (L[j + 1] - L[j] + 1e-9)
        out.append(lerp(curve[j], curve[j + 1], f))
    return out


def catmull_pts(pts, n=8):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


def claw(x, y, ang, s, seed, depth=2, curl=110):
    """Hokusai's foam fingers: a tapering white talon that curls over at the tip and sprouts smaller talons."""
    rnd = random.Random(seed)
    n = 9
    a = math.radians(ang)
    turn = math.radians(curl * rnd.uniform(0.8, 1.2)) / n
    pts = [(x, y)]
    step = s / n
    for i in range(n):
        a += turn * (0.4 + 1.4 * i / n)
        pts.append((pts[-1][0] + step * math.cos(a), pts[-1][1] + step * math.sin(a)))
    ws = [s * 0.34 * (1 - i / n) ** 0.9 + 0.6 for i in range(n + 1)]
    poly = tongue_pts(pts, ws)
    out = [f'<path d="{smooth_closed(poly)}" fill="#FBF6E8" stroke="{KEY}" stroke-width="{max(0.9, s * 0.05):.1f}" stroke-linejoin="round"/>']
    if depth > 0:
        for k, t in enumerate((0.3, 0.55) if depth > 1 else (0.45,)):
            i = int(t * n)
            (ax, ay), (bx, by) = pts[i], pts[i + 1]
            h = math.degrees(math.atan2(by - ay, bx - ax))
            out.append(claw(ax, ay, h - rnd.uniform(35, 55), s * rnd.uniform(0.42, 0.55), seed * 3 + k, depth - 1, curl))
    return "".join(out)


def oshiokuri(x, y, L, tilt, rowers, seed):
    """A long fast boat with crouching rowers in indigo."""
    rnd = random.Random(seed)
    a = math.radians(tilt)
    c, s_ = math.cos(a), math.sin(a)

    def T(u, v):
        return (x + u * c - v * s_, y + u * s_ + v * c)
    hull = [T(-L / 2, -2), T(L / 2, -5), T(L / 2 + 6, -8), T(L / 2 - 4, 4), T(-L / 2 + 6, 5)]
    out = [f'<path d="{pd(hull)}" fill="#E8D8A8" stroke="{KEY}" stroke-width="1.4" stroke-linejoin="round"/>',
           f'<path d="{pd([T(-L / 2 + 6, 1), T(L / 2 - 4, 0)], False)}" stroke="#B89A60" stroke-width="1.2"/>']
    for i in range(rowers):
        u = -L / 2 + 12 + i * (L - 22) / max(1, rowers - 1)
        bx, by = T(u, -4)
        out.append(f'<path d="{blob(bx, by - 4, 4.2, 3.4, seed + i, 0.08, 8)}" fill="#2E4A7A" stroke="{KEY}" stroke-width="1"/>')
        out.append(f'<circle cx="{bx + 2:.1f}" cy="{by - 7.5:.1f}" r="2.2" fill="#E8D8B8" stroke="{KEY}" stroke-width="0.8"/>')
    return "".join(out)


@design("the-great-wave")
def great_wave():
    D = Doc("gmgw")
    box = (66, 78, 534, 396)   # 468 x 318 (25.7 x 37.9 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [mat_board(D, (x0 - 4, y0 - 4, x1 + 4, y1 + 4), 5, "#F2EADA", 91)]
    out.append(simple_frame(D, (x0 - 18, y0 - 18, x1 + 18, y1 + 18), 0.01, ("#000", "#000", "#000"), 1) if False else "")
    cp = clip_box(D, box)
    paint = [washi(D, box, "#EADCB8", 5)]
    # sky: pale with the dark bokashi band across the top
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H * 0.4}" fill="{D.lin([(0, "#6A6A66", 0.85), (0.35, "#A8A496", 0.35), (1, "#EADCB8", 0)])}"/>')
    paint.append(woodgrain(D, (x0, y0, x1, Y(0.7)), 0.07, 5))
    for k, (u, v, w_) in enumerate([(0.72, 0.18, 0.2), (0.85, 0.3, 0.14), (0.6, 0.36, 0.1)]):
        paint.append(f'<path d="{smooth_closed(UV([(u - w_, v), (u - w_ * 0.4, v - 0.035), (u + w_ * 0.3, v - 0.02), (u + w_, v + 0.005), (u, v + 0.02)]))}" fill="#D8CCAA" opacity="0.8"/>')
    # Fuji, far away, small and calm
    fuji = UV([(0.53, 0.84), (0.65, 0.67), (0.68, 0.62), (0.705, 0.615), (0.73, 0.628), (0.82, 0.72), (0.9, 0.84)])
    paint.append(f'<path d="{pd(fuji)}" fill="#3A4E6E" stroke="{KEY}" stroke-width="1.6" stroke-linejoin="round"/>')
    cap = UV([(0.633, 0.695), (0.65, 0.67), (0.68, 0.62), (0.705, 0.615), (0.73, 0.628), (0.775, 0.68), (0.758, 0.695), (0.742, 0.678),
              (0.725, 0.712), (0.71, 0.684), (0.695, 0.72), (0.68, 0.69), (0.655, 0.712)])
    paint.append(f'<path d="{pd(cap)}" fill="#FBF6E8" stroke="{KEY}" stroke-width="1.2" stroke-linejoin="round"/>')
    rnd = random.Random(7)
    # the sea: swells rising behind the boats, a trough where Fuji shows through
    surf = catmull_pts(UV([(0.3, 0.8), (0.42, 0.66), (0.5, 0.62), (0.57, 0.67), (0.65, 0.76), (0.72, 0.72), (0.8, 0.62), (0.86, 0.58),
                           (0.93, 0.62), (1.04, 0.72)]), 8)
    sea = surf + [(X(1.04), Y(1.04)), (X(0.3), Y(1.04))]
    paint.append(f'<path d="{pd(sea)}" fill="{PRUSSIAN[1]}"/>')
    for k in range(1, 7):
        line = [(x, y + k * 9) for x, y in surf][4:-2]
        paint.append(f'<path d="{smooth_open(line)}" fill="none" stroke="{"#7AA2C8" if k % 2 else PRUSSIAN[2]}" stroke-width="{2.2 if k % 2 else 3}" opacity="0.85"/>')
    paint.append(f'<path d="{smooth_open(surf)}" fill="none" stroke="{KEY}" stroke-width="2"/>')
    # lacy foam on the far swell
    for i in range(30, len(surf) - 10, 3):
        x, y = surf[i]
        if x > X(0.74):
            paint.append(claw(x, y, -80 + rnd.uniform(-20, 20) + (x - X(0.86)) * 0.5, 11, 500 + i, 1))
    # boats riding the swells
    paint.append(oshiokuri(X(0.49), Y(0.67), 120, 24, 7, 3))
    paint.append(oshiokuri(X(0.87), Y(0.62), 100, -18, 6, 4))
    # ---- the great wave as a ribbon between its outer skin and the inner curl
    c_out = catmull_pts(UV([(-0.06, 1.04), (-0.01, 0.66), (0.07, 0.42), (0.17, 0.23), (0.28, 0.11), (0.39, 0.065), (0.49, 0.075), (0.57, 0.13),
                            (0.62, 0.21), (0.625, 0.3), (0.6, 0.36)]), 8)
    c_in = catmull_pts(UV([(0.38, 1.04), (0.36, 0.82), (0.345, 0.62), (0.355, 0.45), (0.38, 0.32), (0.42, 0.245), (0.47, 0.21), (0.52, 0.215),
                           (0.565, 0.245), (0.59, 0.3), (0.6, 0.36)]), 8)
    N = 90
    A, Bc = resample(c_out, N), resample(c_in, N)
    body = A + Bc[::-1]
    paint.append(f'<path d="{pd(body)}" fill="{PRUSSIAN[2]}"/>')
    for f, col, w_ in ((0.12, PRUSSIAN[1], 9), (0.3, "#3E6A9E", 5), (0.45, PRUSSIAN[1], 4), (0.62, "#4A78AA", 3), (0.8, PRUSSIAN[1], 3)):
        line = [lerp(a, b, f) for a, b in zip(A, Bc)][2:-6]
        paint.append(f'<path d="{smooth_open(line)}" fill="none" stroke="{col}" stroke-width="{w_}" stroke-linecap="round"/>')
    for f in (0.22, 0.38, 0.54, 0.7):
        line = [lerp(a, b, f) for a, b in zip(A, Bc)][4:-10]
        paint.append(f'<path d="{smooth_open(line)}" fill="none" stroke="#C8D8E8" stroke-width="1.3" opacity="0.8"/>')
    paint.append(f'<path d="{pd(body)}" fill="none" stroke="{KEY}" stroke-width="2.2" stroke-linejoin="round"/>')
    # foam: a thin white lip, then claws reaching forward and down from the crest, big at the crown
    lip = A[30:]
    lip_in = [lerp(a, b, 0.07) for a, b in zip(A, Bc)][30:]
    paint.append(f'<path d="{pd(lip + lip_in[::-1])}" fill="#FBF6E8" stroke="{KEY}" stroke-width="1.3"/>')
    claws = []
    for i in range(30, N - 3, 3):
        (ax, ay), (bx, by) = A[i - 1], A[i + 1]
        tx, ty = bx - ax, by - ay
        tl = math.hypot(tx, ty) or 1
        nx, ny = A[i][0] - Bc[i][0], A[i][1] - Bc[i][1]
        nl = math.hypot(nx, ny) or 1
        dx, dy = tx / tl * 1.0 + nx / nl * 0.4, ty / tl * 1.0 + ny / nl * 0.4
        ang = math.degrees(math.atan2(dy, dx)) + rnd.uniform(-10, 10)
        t = (i - 30) / (N - 33)
        s_ = 16 + 30 * math.sin(math.pi * min(1, t * 1.15)) ** 0.7
        claws.append((t, claw(A[i][0], A[i][1], ang, s_, 100 + i, 2)))
    claws = [c for _, c in sorted(claws, key=lambda q: -q[0])]
    paint.append("".join(claws))
    # spray falling from the crest like snow
    for k in range(140):
        t = rnd.uniform(0.45, 1.0)
        i = int(t * (N - 1))
        px, py = A[i]
        dx, dy = rnd.uniform(-5, 70), rnd.gauss(30, 40) + 10
        r = rnd.uniform(1.0, 2.8)
        paint.append(f'<circle cx="{px + dx:.1f}" cy="{py + dy:.1f}" r="{r:.1f}" fill="#FBF6E8" stroke="{KEY}" stroke-width="0.5" opacity="0.95"/>')
    # foreground wave, a small Fuji of water with its own crest
    fw_out = catmull_pts(UV([(0.04, 1.04), (0.1, 0.88), (0.17, 0.79), (0.23, 0.76), (0.28, 0.78), (0.31, 0.84)]), 8)
    fw_in = catmull_pts(UV([(0.36, 1.04), (0.33, 0.94), (0.32, 0.88), (0.31, 0.84)]), 8)
    fw = fw_out + fw_in[::-1]
    paint.append(f'<path d="{pd(fw)}" fill="{PRUSSIAN[1]}" stroke="{KEY}" stroke-width="1.8" stroke-linejoin="round"/>')
    fA = resample(fw_out, 30)
    fB = resample(fw_in[::-1] + [fw_in[0]], 30)
    for i in range(12, 29, 2):
        (ax, ay), (bx, by) = fA[i - 1], fA[min(29, i + 1)]
        tang = math.degrees(math.atan2(by - ay, bx - ax))
        paint.append(claw(fA[i][0], fA[i][1], tang - 70, 12, 300 + i, 1))
    paint.append(woodgrain(D, box, 0.05, 9, "#1A1A2A"))
    out.append(f'<g {cp}>{"".join(paint)}</g>')
    out.append(f'<rect x="{x0 - 1}" y="{y0 - 1}" width="{W + 2}" height="{H + 2}" fill="none" stroke="{KEY}" stroke-width="2.4"/>')
    out.append(museum_label(D, 470, "The Great Wave", "KATSUSHIKA HOKUSAI · c. 1831", "#1E2A44", "#5A6478", ts=34, bs=18, gap=32))
    out.append(hanko(466, 432, 24, seed=3))
    return finish(D, out, 43)


# ================================================================ 12. Red Fuji (Fine Wind, Clear Morning) — Hokusai, c. 1831
def scroll_mount(D, box, seed, silk="#2E3A4A", brocade="#B89A5A", paper_c="#E8DCC0"):
    """Hanging-scroll style mount: a silk ground with a brocade border band and a fine ivory slip."""
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    out = [f'<rect width="600" height="600" fill="{silk}"/>']
    # silk weave
    pat = D.pattern(6, 6, f'<path d="M0 1H6M0 4H6" stroke="#FFFFFF" stroke-width="0.5" opacity="0.06"/><path d="M1.5 0V6" stroke="#000" stroke-width="0.6" opacity="0.08"/>')
    out.append(f'<rect width="600" height="600" fill="{pat}"/>')
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFFFFF", 0.12), (1, "#000000", 0.25)], 0.5, 0.35, 0.8)}"/>')
    # brocade band around the picture
    b = 14
    ob = (x0 - b - 4, y0 - b - 4, x1 + b + 4, y1 + b + 4)
    out.append(f'<rect x="{ob[0] + 2}" y="{ob[1] + 5}" width="{ob[2] - ob[0]}" height="{ob[3] - ob[1]}" fill="#000" opacity="0.3"/>')
    out.append(f'<rect x="{ob[0]}" y="{ob[1]}" width="{ob[2] - ob[0]}" height="{ob[3] - ob[1]}" fill="{brocade}"/>')
    motif = (f'<rect width="22" height="22" fill="{brocade}"/>'
             f'<path d="M11 3a8 8 0 0 1 0 16a8 8 0 0 1 0-16M3 11h16M11 3v16" fill="none" stroke="{dk(brocade, 0.3)}" stroke-width="1.1" opacity="0.6"/>'
             f'<circle cx="11" cy="11" r="2.2" fill="{lt(brocade, 0.4)}"/>')
    out.append(f'<rect x="{ob[0]}" y="{ob[1]}" width="{ob[2] - ob[0]}" height="{ob[3] - ob[1]}" fill="{D.pattern(22, 22, motif)}"/>')
    out.append(ring_side(D, ob, 0, 3, [(0, lt(brocade, 0.5)), (1, brocade)]))
    out.append(f'<rect x="{x0 - 4}" y="{y0 - 4}" width="{x1 - x0 + 8}" height="{y1 - y0 + 8}" fill="{paper_c}"/>')
    return "".join(out)


@design("red-fuji")
def red_fuji():
    D = Doc("gmrf")
    box = (70, 70, 530, 382)   # 460 x 312 (25.5 x 37.5 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [scroll_mount(D, box, 3, "#24303E", "#A8884A")]
    cp = clip_box(D, box)
    paint = [washi(D, box, "#F0E4C6", 7)]
    # sky: Prussian blue at the top fading to pale, with rows of mackerel clouds
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.lin([(0, "#1E3A78"), (0.35, "#3E6AAE"), (0.7, "#9ABCD8"), (1, "#E8E4D0")])}"/>')
    paint.append(woodgrain(D, box, 0.06, 3, "#0A1A3A"))
    rnd = random.Random(5)
    for row in range(7):
        v = 0.12 + row * 0.075
        u = rnd.uniform(-0.05, 0.05)
        while u < 1.05:
            w = rnd.uniform(0.025, 0.05) * (1 + row * 0.08)
            cx, cy = X(u), Y(v + 0.015 * math.sin(u * 9 + row))
            d = smooth_closed([(cx - w * W, cy), (cx - w * W * 0.4, cy - 4 - row * 0.4), (cx + w * W * 0.3, cy - 3 - row * 0.3), (cx + w * W, cy + 1), (cx, cy + 3)])
            paint.append(f'<path d="{d}" fill="#FBF8EE" opacity="{0.95 - row * 0.05:.2f}"/>')
            u += w * 2 + rnd.uniform(0.015, 0.04)
    # the mountain: a great red-brown cone, darker toward the summit, snow running down in streaks
    fuji = UV([(-0.12, 1.02), (0.12, 0.8), (0.3, 0.6), (0.42, 0.42), (0.5, 0.24), (0.54, 0.165), (0.57, 0.155), (0.6, 0.16), (0.625, 0.17),
               (0.66, 0.24), (0.76, 0.4), (0.88, 0.56), (1.02, 0.72), (1.02, 1.02)])
    fd = smooth_closed(fuji)
    paint.append(f'<path d="{fd}" fill="{D.lin([(0, "#5A2414"), (0.25, "#9A3A1E"), (0.55, "#C0502A"), (1, "#C8683A")])}"/>')
    paint.append(woodgrain(D, (x0, Y(0.15), x1, y1), 0.1, 7, "#3A1408"))
    # snow tongues from the summit
    snow = []
    sx = X(0.57)
    for k in range(13):
        base_x = X(0.505 + (k / 12) * 0.15) + rnd.uniform(-2, 2)
        top_y = Y(0.16 + abs(k - 6) * 0.006)
        L = rnd.uniform(0.07, 0.22) * (1 - abs(k - 6) / 14)
        tip = (base_x + (base_x - sx) * 0.55, top_y + H * L)
        mid = lerp((base_x, top_y), tip, 0.55)
        w = rnd.uniform(3, 5)
        snow.append(f'<path d="M{base_x - w:.1f} {top_y:.1f}Q{mid[0] - w * 0.8:.1f} {mid[1]:.1f} {tip[0]:.1f} {tip[1]:.1f}Q{mid[0] + w * 0.6:.1f} {mid[1]:.1f} {base_x + w:.1f} {top_y:.1f}Z" fill="#F6F2E8"/>')
    # darker, cooler streaks high on the cone where the rock is bare
    for k in range(26):
        u = rnd.uniform(0.44, 0.72)
        v0 = rnd.uniform(0.2, 0.45)
        snow.append(f'<path d="M{X(u):.1f} {Y(v0):.1f}l{(X(u) - sx) * 0.25:.1f} {rnd.uniform(18, 50):.1f}" stroke="{rnd.choice(["#3A1A1A", "#5A2A20", "#2A1A2A"])}" stroke-width="{rnd.uniform(1.5, 3.2):.1f}" opacity="0.35" stroke-linecap="round"/>')
    cap = UV([(0.5, 0.24), (0.54, 0.165), (0.57, 0.155), (0.6, 0.16), (0.625, 0.17), (0.66, 0.24), (0.6, 0.22), (0.57, 0.25), (0.54, 0.22)])
    paint.append(f'<g {D.clip(f"<path d=\"{fd}\"/>")}>{"".join(snow)}<path d="{smooth_closed(cap)}" fill="#F6F2E8"/></g>')
    # dark green forest at the foot, a field of tiny tree dabs
    forest = UV([(-0.02, 0.86), (0.1, 0.8), (0.2, 0.78), (0.3, 0.82), (0.45, 0.84), (0.6, 0.86), (0.75, 0.84), (0.9, 0.86), (1.02, 0.84), (1.02, 1.02), (-0.02, 1.02)])
    paint.append(f'<path d="{smooth_closed(forest)}" fill="#1E3A2A"/>')
    for k in range(320):
        x, y = rnd.uniform(x0, x1), rnd.uniform(Y(0.78), y1)
        if not inside((x, y), forest):
            continue
        r = 1.6 + 1.8 * (y - Y(0.78)) / (H * 0.22)
        paint.append(f'<path d="M{x - r:.1f} {y + r:.1f}L{x:.1f} {y - r * 1.3:.1f}L{x + r:.1f} {y + r:.1f}Z" fill="{rnd.choice(["#2E5A3A", "#3A6A44", "#14301E", "#4A7A4A"])}"/>')
    paint.append(f'<path d="{fd}" fill="none" stroke="#2A0E06" stroke-width="2" stroke-linejoin="round"/>')
    out.append(f'<g {cp}>{"".join(paint)}</g>')
    out.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="none" stroke="#2A1A10" stroke-width="1.6"/>')
    out.append(museum_label(D, 464, "Red Fuji", "KATSUSHIKA HOKUSAI · c. 1831", "#F2E4C4", "#C8B48C", ts=40, bs=19, gap=38))
    out.append(hanko(287, 516, 26, seed=5))
    return finish(D, out, 47)


# ================================================================ 13. Plum Park in Kameido — Hiroshige, 1857
@design("plum-garden")
def plum_garden():
    D = Doc("gmpg")
    box = (172, 56, 428, 436)   # 256 x 380 (36 x 24 cm, portrait)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [mat_board(D, (x0 - 4, y0 - 4, x1 + 4, y1 + 4), 5, "#E6DCC8", 101)]
    out.append(simple_frame(D, (x0 - 4, y0 - 4, x1 + 4, y1 + 4), 10, ("#5A4A3A", "#2A2018", "#120C08"), 3))
    cp = clip_box(D, box)
    paint = [washi(D, box, "#F2EAD6", 9)]
    # sky: red bokashi at the top melting into pale ivory
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H * 0.62}" fill="{D.lin([(0, "#C8281E"), (0.3, "#E0603A"), (0.65, "#F2C8A0", 0.6), (1, "#F2EAD6", 0)])}"/>')
    paint.append(woodgrain(D, (x0, y0, x1, Y(0.4)), 0.08, 9, "#5A0A06"))
    # ground: soft green field, a fence and strollers among distant plum trees
    ground = UV([(-0.02, 0.62), (0.4, 0.6), (1.02, 0.61), (1.02, 1.02), (-0.02, 1.02)])
    paint.append(f'<path d="{pd(ground)}" fill="{D.lin([(0, "#C8D0A0"), (1, "#8AA070")])}"/>')
    paint.append(f'<path d="{pd(UV([(-0.02, 0.62), (1.02, 0.6), (1.02, 0.64), (-0.02, 0.66)]))}" fill="#6A8A5A" opacity="0.5"/>')
    rnd = random.Random(4)
    # distant plum trees: dark twisted trunks with white blossom dots
    for k, (u, v, s) in enumerate([(0.08, 0.6, 0.6), (0.3, 0.58, 0.5), (0.62, 0.6, 0.55), (0.86, 0.59, 0.6), (0.46, 0.6, 0.4)]):
        bx, by = X(u), Y(v)
        segs = []
        branch_tree(random.Random(40 + k), bx, by, math.radians(-90 + rnd.uniform(-20, 20)), 70 * s, 6 * s, 2, segs, 30)
        for pts, w0, w1 in segs:
            paint.append(taper(pts, w0 + 0.5, w1, "#3A2A2A"))
        for pts, w0, w1 in segs:
            for (px, py) in pts[1::2]:
                paint.append(f'<circle cx="{px + rnd.uniform(-3, 3):.1f}" cy="{py + rnd.uniform(-3, 3):.1f}" r="{rnd.uniform(1.4, 2.4):.1f}" fill="#FFFFFF" stroke="#C8B8B8" stroke-width="0.4"/>')
    # fence
    for k in range(18):
        fx = X(-0.02 + k * 0.06)
        paint.append(f'<path d="M{fx:.1f} {Y(0.66):.1f}V{Y(0.62):.1f}" stroke="#7A6A5A" stroke-width="1.6"/>')
    paint.append(f'<path d="M{x0} {Y(0.635)}H{x1}" stroke="#7A6A5A" stroke-width="1.4"/>')
    # small strollers behind the fence
    from figures import person
    for k, (u, h, pal) in enumerate([(0.2, 26, {"top": "#3A4A6A", "top_kind": "coat", "bottom_kind": "skirt", "bottom": "#3A4A6A", "hat_kind": None, "hair": "#141018", "hair_style": "bun"}),
                                    (0.27, 24, {"top": "#8A3A3A", "top_kind": "coat", "bottom_kind": "skirt", "bottom": "#8A3A3A", "hat_kind": None, "hair": "#141018", "hair_style": "bun"}),
                                    (0.74, 25, {"top": "#4A5A3A", "top_kind": "coat", "bottom_kind": "skirt", "bottom": "#4A5A3A", "hat_kind": None, "hair": "#141018", "hair_style": "short"})]):
        paint.append(person(X(u), Y(0.655), h, "stand_34", 1 if k else -1, {**pal, "skin": "#F2DCC0"}, seed=60 + k, light=1, shadow=0.15))
    # the great foreground plum: a dark gnarled trunk rising through the whole picture
    trunk_c = UV([(0.98, 1.04), (0.92, 0.86), (0.78, 0.74), (0.62, 0.62), (0.5, 0.46), (0.36, 0.36), (0.18, 0.3), (0.02, 0.22), (-0.06, 0.2)])
    ws = [62, 56, 46, 40, 34, 28, 22, 16, 12]
    tpts = tongue_pts(catmull_pts(trunk_c, 4), [ws[min(len(ws) - 1, i // 4)] * (1 - (i % 4) / 16) for i in range((len(trunk_c) - 1) * 4 + 1)])
    tpts = jitter(tpts, 11, 2.5)
    td = smooth_closed(tpts)
    paint.append(f'<path d="{td}" fill="#2A2224"/>')
    # bark: knots, mossy green patches and pale flaking edges, printed in flat layers
    bark = []
    for k in range(60):
        i = rnd.randrange(len(tpts))
        x, y = tpts[i]
        bark.append(f'<path d="{blob(x + rnd.uniform(-10, 10), y + rnd.uniform(-10, 10), rnd.uniform(3, 9), rnd.uniform(2, 5), k, 0.3, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#4A5A3A", "#5A6A4A", "#1A1418", "#6A5A4A", "#3A3A2A"])}"/>')
    for k in range(10):
        t = rnd.uniform(0.1, 0.8)
        x, y = catmull_pts(trunk_c, 4)[int(t * (len(trunk_c) - 1) * 4)]
        bark.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(4, 8):.1f}" ry="{rnd.uniform(3, 5):.1f}" fill="#120C0E" stroke="#5A4A4A" stroke-width="1"/>')
    paint.append(f'<g {D.clip(f"<path d=\"{td}\"/>")}>{"".join(bark)}</g>')
    paint.append(f'<path d="{td}" fill="none" stroke="#0A0608" stroke-width="2"/>')
    # twigs shooting straight up from the limb, as plums do, studded with blossoms
    twigs = []
    for k, (u, v, L, a) in enumerate([(0.26, 0.31, 70, -80), (0.12, 0.27, 50, -95), (0.42, 0.4, 90, -70), (0.55, 0.5, 60, -85), (0.36, 0.34, 40, -120),
                                      (0.04, 0.22, 46, -60), (0.66, 0.6, 50, -60), (0.48, 0.42, 30, -40)]):
        x, y = X(u), Y(v)
        pts = [(x, y)]
        ang = math.radians(a)
        for i in range(4):
            ang += math.radians(rnd.uniform(-12, 12))
            pts.append((pts[-1][0] + L / 4 * math.cos(ang), pts[-1][1] + L / 4 * math.sin(ang)))
        twigs.append(taper(pts, 5, 1.6, "#2A2224"))
        for (px, py) in pts[1:]:
            for j in range(2):
                fx, fy = px + rnd.uniform(-7, 7), py + rnd.uniform(-5, 5)
                r = rnd.uniform(4.5, 6.5)
                petals = "".join(f'<circle cx="{fx + r * 0.6 * math.cos(math.radians(72 * i + 18)):.1f}" cy="{fy + r * 0.6 * math.sin(math.radians(72 * i + 18)):.1f}" r="{r * 0.5:.1f}"/>' for i in range(5))
                twigs.append(f'<g fill="#FFFFFF" stroke="#B8A0A0" stroke-width="0.6">{petals}</g><circle cx="{fx:.1f}" cy="{fy:.1f}" r="{r * 0.25:.1f}" fill="#E85A5A"/>')
            if rnd.random() < 0.5:
                twigs.append(f'<circle cx="{px + 3:.1f}" cy="{py - 3:.1f}" r="2.4" fill="#C8303A"/>')
    paint.append("".join(twigs))
    out.append(f'<g {cp}>{"".join(paint)}</g>')
    # title cartouche printed on the picture, as in the series (here in English)
    out.append(f'<rect x="{x1 - 40}" y="{y0 + 12}" width="28" height="104" fill="#E8D8B0" stroke="#2A1A10" stroke-width="1.2"/>')
    out.append(f'<rect x="{x1 - 37}" y="{y0 + 15}" width="22" height="98" fill="none" stroke="#C8281E" stroke-width="1"/>')
    for k in range(4):
        out.append(f'<path d="M{x1 - 31} {y0 + 26 + k * 22}h10" stroke="#2A1A10" stroke-width="2.4" opacity="0"/>')
    out.append(museum_label(D, 490, "Plum Garden in Kameido", "UTAGAWA HIROSHIGE · 1857", "#3A2A1E", "#6A5440", ts=28, bs=17, gap=28, max_w=440))
    return finish(D, out, 53)


# ================================================================ 14. Sudden Shower over Shin-Ōhashi Bridge — Hiroshige, 1857
def rain_walker(x, y, s, kind, seed, facing=1):
    """A woodblock figure hurrying through rain: straw hat or paper umbrella, a wrapped robe, bare legs."""
    rnd = random.Random(seed)
    f = facing
    out = []
    robe = rnd.choice(["#3A4A6A", "#5A4A3A", "#2E3A4A", "#6A5A40", "#4A3A4A"])
    # legs, mid-stride
    out.append(f'<path d="M{x - 2 * s * f:.1f} {y - 10 * s:.1f}L{x - 6 * s * f:.1f} {y:.1f}M{x + 2 * s * f:.1f} {y - 10 * s:.1f}L{x + 5 * s * f:.1f} {y - 1 * s:.1f}" stroke="#E8C8A0" stroke-width="{2.2 * s:.1f}" stroke-linecap="round"/>')
    out.append(f'<path d="M{x - 2 * s * f:.1f} {y - 10 * s:.1f}L{x - 6 * s * f:.1f} {y:.1f}M{x + 2 * s * f:.1f} {y - 10 * s:.1f}L{x + 5 * s * f:.1f} {y - 1 * s:.1f}" stroke="{KEY}" stroke-width="{0.6 * s:.1f}" stroke-linecap="round" opacity="0.6"/>')
    if kind == "mino":
        body = [(x - 7 * s * f, y - 9 * s), (x - 5 * s * f, y - 26 * s), (x + 5 * s * f, y - 27 * s), (x + 8 * s * f, y - 10 * s)]
        out.append(f'<path d="{pd(body)}" fill="#8A7A4A" stroke="{KEY}" stroke-width="{0.9 * s:.1f}" stroke-linejoin="round"/>')
        for k in range(5):
            xx = x + (-5 + k * 2.6) * s * f
            out.append(f'<path d="M{xx:.1f} {y - 25 * s:.1f}l{rnd.uniform(-1, 1) * s:.1f} {15 * s:.1f}" stroke="#5A4A2A" stroke-width="{0.6 * s:.1f}"/>')
        hat = [(x - 11 * s, y - 26 * s), (x + 1 * s * f, y - 34 * s), (x + 11 * s, y - 26 * s)]
        out.append(f'<path d="{pd(hat)}" fill="#C8A860" stroke="{KEY}" stroke-width="{0.9 * s:.1f}" stroke-linejoin="round"/>')
    else:
        body = [(x - 6 * s * f, y - 9 * s), (x - 4 * s * f, y - 26 * s), (x + 4 * s * f, y - 27 * s), (x + 7 * s * f, y - 10 * s)]
        out.append(f'<path d="{pd(body)}" fill="{robe}" stroke="{KEY}" stroke-width="{0.9 * s:.1f}" stroke-linejoin="round"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y - 29 * s:.1f}" r="{3 * s:.1f}" fill="#1A1418"/>')
        out.append(f'<path d="M{x + 1 * s * f:.1f} {y - 22 * s:.1f}L{x - 2 * s * f:.1f} {y - 40 * s:.1f}" stroke="{KEY}" stroke-width="{0.9 * s:.1f}"/>')
        ux, uy = x - 3 * s * f, y - 40 * s
        top = f"M{ux - 15 * s:.1f} {uy + 4 * s:.1f}Q{ux:.1f} {uy - 7 * s:.1f} {ux + 15 * s:.1f} {uy + 4 * s:.1f}Q{ux:.1f} {uy + 1 * s:.1f} {ux - 15 * s:.1f} {uy + 4 * s:.1f}Z"
        out.append(f'<path d="{top}" fill="{rnd.choice(["#D8C090", "#E8D8B0", "#C8A870"])}" stroke="{KEY}" stroke-width="{0.9 * s:.1f}"/>')
        for k in (-10, -5, 0, 5, 10):
            out.append(f'<path d="M{ux:.1f} {uy - 2.5 * s:.1f}L{ux + k * s:.1f} {uy + 3.4 * s - abs(k) * 0.05 * s:.1f}" stroke="#8A6A3A" stroke-width="{0.5 * s:.1f}"/>')
    return "".join(out)


@design("sudden-shower")
def sudden_shower():
    D = Doc("gmss")
    box = (184, 68, 416, 414)   # 232 x 346 (36 x 24 cm, portrait)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [scroll_mount(D, box, 9, "#3A3428", "#6A7A6A", "#E8DCC0")]
    cp = clip_box(D, box)
    paint = [washi(D, box, "#ECE2C8", 11)]
    rnd = random.Random(7)
    # sky: a black thundercloud pressing down, grey below
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H * 0.42}" fill="{D.lin([(0, "#16161C"), (0.25, "#3A3A40"), (0.6, "#8A8A84", 0.7), (1, "#ECE2C8", 0)])}"/>')
    paint.append(woodgrain(D, (x0, y0, x1, Y(0.3)), 0.12, 5, "#000"))
    # river: blue bokashi bands
    river = UV([(-0.02, 0.36), (1.02, 0.36), (1.02, 1.02), (-0.02, 1.02)])
    paint.append(f'<path d="{pd(river)}" fill="{D.lin([(0, "#8AA4B0"), (0.3, "#5A7A90"), (0.7, "#3E5E7A"), (1, "#2A4A6A")])}"/>')
    paint.append(woodgrain(D, (x0, Y(0.36), x1, y1), 0.08, 7, "#0A1A2A"))
    # far shore under the rain, a soft grey-green line of trees
    shore = rough(UV([(-0.02, 0.4), (0.15, 0.37), (0.3, 0.39), (0.45, 0.36), (0.6, 0.385), (0.8, 0.37), (1.02, 0.39)]), 3, 4, 3)
    paint.append(f'<path d="{pd(shore + UV([(1.02, 0.43), (-0.02, 0.43)]))}" fill="#4A5A4A" opacity="0.85"/>')
    for k in range(40):
        x = X(rnd.uniform(0, 1))
        paint.append(f'<path d="{blob(x, Y(0.385) + rnd.uniform(-3, 3), rnd.uniform(4, 8), rnd.uniform(5, 9), k, 0.2, 8)}" fill="#3A4A3A" opacity="0.7"/>')
    # a raftsman poling his logs downstream
    rx, ry = X(0.35), Y(0.55)
    raft = [(rx - 46, ry), (rx + 40, ry - 10), (rx + 44, ry - 5), (rx - 42, ry + 5)]
    paint.append(f'<path d="{pd(raft)}" fill="#6A4A2A" stroke="{KEY}" stroke-width="1.2"/>')
    for k in range(3):
        paint.append(f'<path d="M{rx - 44:.1f} {ry - 1 + k * 2:.1f}L{rx + 42:.1f} {ry - 9 + k * 2:.1f}" stroke="#3A2414" stroke-width="0.7"/>')
    paint.append(rain_walker(rx + 10, ry - 6, 0.9, "mino", 3, 1))
    paint.append(f'<path d="M{rx + 14:.1f} {ry - 30:.1f}L{rx - 20:.1f} {ry + 18:.1f}" stroke="{KEY}" stroke-width="1.4"/>')
    for k in range(4):
        paint.append(f'<path d="M{rx - 50 + k * 4:.1f} {ry + 6 + k * 3:.1f}q20 -3 40 -6" stroke="#C8D8E0" stroke-width="1" fill="none" opacity="0.6"/>')
    # the bridge: deck on a diagonal, with legs standing in the river
    deck_l, deck_r = (X(-0.05), Y(0.72)), (X(1.05), Y(0.6))
    deck = [deck_l, deck_r, (deck_r[0], deck_r[1] + 10), (deck_l[0], deck_l[1] + 12)]
    for k in range(9):
        t = 0.04 + k * 0.12
        px, py = lerp(deck_l, deck_r, t)
        paint.append(f'<path d="{pd([(px - 3, py + 8), (px + 3, py + 8), (px + 4, y1 + 6), (px - 4, y1 + 6)])}" fill="#5A4A3A" stroke="{KEY}" stroke-width="1"/>')
        paint.append(f'<path d="M{px - 2:.1f} {py + 20:.1f}L{px + 2:.1f} {y1:.1f}" stroke="#8A7A5A" stroke-width="1" opacity="0.6"/>')
        if k % 2 == 0:
            paint.append(f'<path d="M{px:.1f} {py + 30:.1f}L{px + 34:.1f} {py + 68:.1f}" stroke="#4A3A2A" stroke-width="2.4"/>')
    paint.append(f'<path d="{pd(deck)}" fill="#B89A6A" stroke="{KEY}" stroke-width="1.6" stroke-linejoin="round"/>')
    for k in range(30):
        t = k / 30
        px, py = lerp(deck_l, deck_r, t)
        paint.append(f'<path d="M{px:.1f} {py:.1f}l0 10" stroke="#8A6A40" stroke-width="0.7"/>')
    rail_l, rail_r = (deck_l[0], deck_l[1] - 14), (deck_r[0], deck_r[1] - 14)
    for k in range(14):
        px, py = lerp(deck_l, deck_r, k / 13)
        paint.append(f'<path d="M{px:.1f} {py:.1f}V{py - 14:.1f}" stroke="#6A5034" stroke-width="2.2"/>')
    paint.append(f'<path d="M{rail_l[0]:.1f} {rail_l[1]:.1f}L{rail_r[0]:.1f} {rail_r[1]:.1f}" stroke="#6A5034" stroke-width="3.2"/>')
    paint.append(f'<path d="M{rail_l[0]:.1f} {rail_l[1]:.1f}L{rail_r[0]:.1f} {rail_r[1]:.1f}" stroke="{KEY}" stroke-width="0.8"/>')
    # people caught in the shower, hurrying both ways
    walkers = [(0.14, 1, "umb", 1), (0.24, 1.0, "umb", 1), (0.33, 0.95, "mino", 1), (0.62, 0.9, "umb", -1), (0.7, 0.88, "mino", -1), (0.82, 0.85, "umb", -1)]
    for k, (t, sc, kind, fc) in enumerate(walkers):
        px, py = lerp(deck_l, deck_r, t)
        paint.append(rain_walker(px, py + 6, sc * 1.25, kind, 20 + k, fc))
    # the rain: hundreds of fine lines at two angles, as two separate blocks
    rain = []
    for k in range(420):
        x = X(rnd.uniform(-0.15, 1.05))
        y = Y(rnd.uniform(-0.05, 1.0))
        L = rnd.uniform(30, 90)
        a = math.radians(rnd.choice([96, 100]))
        rain.append(f'<path d="M{x:.1f} {y:.1f}l{L * math.cos(a):.1f} {L * math.sin(a):.1f}"/>')
    paint.append(f'<g stroke="#1A1A22" stroke-width="0.8" opacity="0.55">{"".join(rain)}</g>')
    out.append(f'<g {cp}>{"".join(paint)}</g>')
    out.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="none" stroke="#1A140E" stroke-width="1.6"/>')
    out.append(museum_label(D, 484, "Sudden Shower", "UTAGAWA HIROSHIGE · 1857", "#F0E6CC", "#C8BC9C", ts=36, bs=18, gap=34))
    return finish(D, out, 59)


# ================================================================ 15. The Tree of Life — Klimt, 1909
def gold_leaf(D, box, seed, base=("#F6DC8A", "#D8A840", "#9A6A1E"), flecks=900):
    """Gold-leaf ground: warm gradient, the seams between leaves, and crackle of tiny bright flecks."""
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{D.lin([(0, base[0]), (0.5, base[1]), (1, base[2])], 0, 0, 1, 1)}"/>']
    seams = []
    s = 34
    for gy in range(int(y0), int(y1), s):
        seams.append(f'<path d="M{x0} {gy + rnd.uniform(-1, 1):.1f}H{x1}"/>')
        off = rnd.uniform(0, s)
        for gx in range(int(x0 + off), int(x1), s):
            seams.append(f'<path d="M{gx} {gy}v{s}"/>')
    out.append(f'<g stroke="{base[2]}" stroke-width="0.7" opacity="0.35">{"".join(seams)}</g>')
    fl = "".join(f'<circle cx="{rnd.uniform(x0, x1):.0f}" cy="{rnd.uniform(y0, y1):.0f}" r="{rnd.uniform(0.4, 1.2):.1f}" fill="{rnd.choice(["#FFF6C8", "#FFFFFF", base[2], "#B8862A"])}"/>' for _ in range(flecks))
    out.append(f'<g opacity="0.6">{fl}</g>')
    return "".join(out)


def spiral_pts(cx, cy, r0, turns, a0, direction=1, n=60, shrink=0.18):
    """Logarithmic-ish spiral from the outside in."""
    pts = []
    for i in range(n + 1):
        t = i / n
        a = a0 + direction * t * turns * 2 * math.pi
        r = r0 * (shrink + (1 - shrink) * (1 - t) ** 1.25)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def gilded_band(pts, w0, w1, seed, fill="#E8B848", edge="#5A3410", dots="#7A4A14"):
    rnd = random.Random(seed)
    out = [taper(pts, w0 + 3, w1 + 2, edge), taper(pts, w0, w1, fill),
           taper([(x - w0 * 0.12, y - w0 * 0.12) for x, y in pts], w0 * 0.35, w1 * 0.3, "#FFF0B0", 0.55)]
    for i in range(2, len(pts) - 2, 3):
        x, y = pts[i]
        t = i / len(pts)
        r = (w0 + (w1 - w0) * t) * 0.18
        if r > 0.9:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{dots}"/>')
    return "".join(out)


def klimt_eye(cx, cy, s, rot=0):
    """The Egyptian 'eye' motif that dots the Tree of Life."""
    return (f'<g transform="rotate({rot} {cx:.1f} {cy:.1f})">'
            f'<path d="M{cx - s:.1f} {cy:.1f}Q{cx:.1f} {cy - s * 0.7:.1f} {cx + s:.1f} {cy:.1f}Q{cx:.1f} {cy + s * 0.7:.1f} {cx - s:.1f} {cy:.1f}Z" fill="#FFF6DC" stroke="#3A2410" stroke-width="1.4"/>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s * 0.32:.1f}" fill="#2A1A0A"/><circle cx="{cx - s * 0.1:.1f}" cy="{cy - s * 0.1:.1f}" r="{s * 0.1:.1f}" fill="#FFF6DC"/></g>')


@design("tree-of-life")
def tree_of_life():
    D = Doc("gmtl")
    box = (64, 62, 536, 422)   # 472 x 360 (frieze detail)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H
    out = [f'<rect width="600" height="600" fill="#1E1A14"/>', wall(D, "#2A241A", 111, (0.5, 0.2), 0.3)]
    out.append(gilt_frame(D, box, 18, 113, "plain", gold=("#FFF4C8", "#E8C870", "#B8923E", "#7A5A1E", "#3A2A0A")))
    cp = clip_box(D, box)
    paint = [gold_leaf(D, box, 5, ("#F8EAC0", "#EAD69A", "#C8A868"), 1400)]
    rnd = random.Random(6)
    # flowering ground: a band of little coloured flower discs
    for k in range(90):
        x, y = X(rnd.uniform(-0.02, 1.02)), Y(rnd.uniform(0.86, 1.02))
        r = rnd.uniform(4, 9)
        c = rnd.choice(["#C8402A", "#2E5A9A", "#E8E0C8", "#6A8A3A", "#D8783A", "#7A3A6A"])
        paint.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{c}" stroke="#3A2410" stroke-width="1"/>'
                     f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.45:.1f}" fill="{rnd.choice(["#F2D060", "#FFFFFF", "#2A1A0A"])}"/>')
    # trunk
    tx = X(0.5)
    trunk = [(tx - 16, y1 + 8), (tx - 11, Y(0.6)), (tx - 8, Y(0.42)), (tx + 8, Y(0.42)), (tx + 11, Y(0.6)), (tx + 16, y1 + 8)]
    paint.append(f'<path d="{smooth_closed(trunk)}" fill="#8A5A22" stroke="#3A2410" stroke-width="2"/>')
    for k in range(10):
        yy = Y(0.45 + k * 0.055)
        paint.append(f'<path d="M{tx - 9 - k * 0.6:.1f} {yy:.1f}Q{tx:.1f} {yy + 5:.1f} {tx + 9 + k * 0.6:.1f} {yy:.1f}" stroke="#E8B848" stroke-width="1.8" fill="none"/>')
    # branches: great scrolling spirals to either side, smaller curls on top
    bands = []
    specs = [  # (start u, v, center u, v, r0, turns, a0, dir)
        (0.5, 0.44, 0.3, 0.36, 0.2, 1.6, -0.2, -1), (0.5, 0.44, 0.7, 0.36, 0.2, 1.6, math.pi + 0.2, 1),
        (0.5, 0.4, 0.38, 0.14, 0.13, 1.5, 0.9, -1), (0.5, 0.4, 0.62, 0.14, 0.13, 1.5, math.pi - 0.9, 1),
        (0.5, 0.5, 0.13, 0.58, 0.15, 1.4, -0.3, -1), (0.5, 0.5, 0.87, 0.58, 0.15, 1.4, math.pi + 0.3, 1),
        (0.5, 0.36, 0.08, 0.2, 0.1, 1.3, 0.4, -1), (0.5, 0.36, 0.92, 0.2, 0.1, 1.3, math.pi - 0.4, 1),
    ]
    for k, (su, sv, cu, cv, r0, turns, a0, dr) in enumerate(specs):
        cx, cy, R = X(cu), Y(cv), r0 * W
        sp = spiral_pts(cx, cy, R, turns, a0 + math.pi, dr, 70)
        start = (X(su), Y(sv))
        mid = (start[0] + (sp[0][0] - start[0]) * 0.45, min(start[1], sp[0][1]) - 26 - k * 2)
        lead = catmull_pts([start, mid, sp[0]], 6)[:-1]
        pts = lead + sp
        bands.append(gilded_band(pts, 12 - k * 0.6, 3, 20 + k, "#E2A838" if k % 2 else "#EEC050"))
        # small curls budding from the big spirals
        for j in range(3):
            i = int(len(sp) * (0.15 + j * 0.2))
            bx, by = sp[i]
            sub = spiral_pts(bx + rnd.uniform(-14, 14), by - rnd.uniform(10, 18), rnd.uniform(9, 14), 1.2, rnd.uniform(0, 6.28), rnd.choice([-1, 1]), 30)
            bands.append(gilded_band([(bx, by)] + sub, 4, 1.4, 60 + k * 3 + j, "#F2C858"))
    paint.append("".join(bands))
    # eyes and triangles studding the branches
    for k in range(16):
        x, y = X(rnd.uniform(0.06, 0.94)), Y(rnd.uniform(0.08, 0.78))
        if abs(x - tx) < 30:
            continue
        if k % 2:
            paint.append(klimt_eye(x, y, rnd.uniform(6, 9), rnd.uniform(-30, 30)))
        else:
            s_ = rnd.uniform(5, 8)
            paint.append(f'<path d="{pd([(x - s_, y + s_ * 0.6), (x, y - s_), (x + s_, y + s_ * 0.6)])}" fill="#2A1A0A" stroke="#E8C060" stroke-width="1"/>'
                         f'<circle cx="{x:.1f}" cy="{y + s_ * 0.05:.1f}" r="{s_ * 0.25:.1f}" fill="#E8C060"/>')
    # the black bird perched on the left branch
    bx, by = X(0.36), Y(0.52)
    body = [(bx - 22, by + 4), (bx - 6, by - 10), (bx + 10, by - 12), (bx + 18, by - 22), (bx + 26, by - 21), (bx + 22, by - 14), (bx + 16, by - 6),
            (bx + 12, by + 8), (bx - 4, by + 14), (bx - 30, by + 16)]
    paint.append(f'<path d="{smooth_closed(body)}" fill="#14100C" stroke="#E8C060" stroke-width="1"/>')
    paint.append(f'<path d="M{bx + 25} {by - 20}l9 2l-9 3z" fill="#E8B848"/><circle cx="{bx + 20}" cy="{by - 18}" r="1.8" fill="#E8C060"/>')
    for k in range(4):
        paint.append(f'<path d="M{bx - 4 + k * 5} {by - 2}q-10 6 -24 10" stroke="#3A2A1A" stroke-width="1.2" fill="none"/>')
    paint.append(f'<path d="M{bx + 2} {by + 12}l-2 10M{bx + 8} {by + 10}l1 10" stroke="#14100C" stroke-width="2"/>')
    out.append(f'<g {cp}>{"".join(paint)}{varnish(D, box, 0.16, 0.18, 7, 0.35)}</g>')
    out.append(museum_label(D, 474, "The Tree of Life", "GUSTAV KLIMT · 1909", "#F2DC98", "#C8A860", ts=32, bs=18, gap=32))
    return finish(D, out, 61)


# ================================================================ portrait toolkit (faces)
def face(D, cx, cy, h, rot=0, turn=0.0, eyes="open", gaze=(0.0, 0.0), skin=("#FBE3D0", "#E8B898", "#B07A62"), lips="#C8565A",
         iris="#5A4030", brow="#6A4A34", blush=0.35, smile=0.0, lid=0.0, light=(-0.6, -0.7), ink_c="#4A2A1E", nose_w=1.0, line=1.0,
         jaw=1.0, outline=None):
    """A carefully proportioned painted face. h = chin-to-hairline height in px. turn: -1 (looking to our left) .. 1 (to our
    right): features slide toward the turned side and the far half narrows. eyes: open / closed / down.
    Returns SVG; the head shape (for hair placement) is unit-based: forehead top at -h/2, chin at +h/2."""
    k = h / 2.0
    t = turn
    rnd = random.Random(int(cx * 3 + cy * 7))
    lightc, base, shadow = skin

    def sx(x):
        """Squash the far side, push the near side, for a 3/4 turn."""
        if t >= 0:
            return x * (1 - 0.32 * t) if x > 0 else x * (1 + 0.06 * t)
        return x * (1 + 0.32 * t) if x < 0 else x * (1 - 0.06 * t)

    def P(x, y):
        X_ = sx(x) + t * 0.16 * (1 - abs(y) * 0.3)
        return X_ * k, y * k

    outline = [(-0.5, -0.98), (-0.68, -0.68), (-0.75, -0.3), (-0.74, 0.05), (-0.66 * jaw, 0.38), (-0.5 * jaw, 0.68), (-0.28 * jaw, 0.9), (-0.1, 1.0), (0, 1.01),
               (0.1, 1.0), (0.28 * jaw, 0.9), (0.5 * jaw, 0.68), (0.66 * jaw, 0.38), (0.74, 0.05), (0.75, -0.3), (0.68, -0.68), (0.5, -0.98), (0, -1.08)]
    # the outline is shifted less than the features (the skull turns, the features ride on the front)
    O = [((sx(x) + t * 0.06) * k, y * k) for x, y in outline]
    od = smooth_closed(O)
    out = []
    # skin: base, form shading away from the light, warm light on the planes facing it
    out.append(f'<path d="{od}" fill="{base}"/>')
    g1 = D.rad([(0, lightc, 0.95), (0.55, lightc, 0.35), (1, lightc, 0)], 0.42 + light[0] * 0.12 + t * 0.08, 0.38, 0.55)
    out.append(f'<path d="{od}" fill="{g1}"/>')
    sd = 1 if light[0] < 0 else -1
    g2 = D.lin([(0, shadow, 0), (0.62, shadow, 0), (1, shadow, 0.55)], 0.5 - 0.5 * sd, 0, 0.5 + 0.5 * sd, 0)
    out.append(f'<path d="{od}" fill="{g2}"/>')
    g3 = D.lin([(0, shadow, 0), (0.78, shadow, 0), (1, shadow, 0.35)])
    out.append(f'<path d="{od}" fill="{g3}"/>')
    # cheeks and the soft shadow of the eye sockets
    for side in (-1, 1):
        ex, ey = P(side * 0.32, -0.06)
        out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{k * 0.26 * (1 - 0.3 * t * side):.1f}" ry="{k * 0.16:.1f}" fill="{D.rad([(0, shadow, 0.3), (1, shadow, 0)])}"/>')
        bx, by = P(side * 0.42, 0.34)
        out.append(f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="{k * 0.24:.1f}" ry="{k * 0.16:.1f}" fill="{D.rad([(0, "#E8707A", blush), (1, "#E8707A", 0)])}"/>')
    # brows
    for side in (-1, 1):
        pts = [P(side * x, y) for x, y in ((0.12, -0.27), (0.3, -0.34), (0.52, -0.29))]
        out.append(taper(pts if side < 0 else pts, k * 0.07 * line, k * 0.025 * line, brow, 0.85))
    # eyes
    for side in (-1, 1):
        cxe, cye = P(side * 0.31, -0.04)
        w = k * 0.18 * (1 - 0.28 * t * side)
        hh = k * 0.08
        inner, outer = (cxe - side * w, cye + hh * 0.1), (cxe + side * w, cye - hh * 0.15)
        if eyes == "closed":
            lidl = [inner, (cxe, cye + hh * 0.85), outer]
            out.append(f'<path d="M{inner[0]:.1f} {inner[1]:.1f}Q{cxe:.1f} {cye + hh * 1.3:.1f} {outer[0]:.1f} {outer[1]:.1f}" stroke="{ink_c}" stroke-width="{max(1.1, k * 0.03) * line:.1f}" fill="none" stroke-linecap="round"/>')
            for j in range(5):
                tt = 0.3 + j * 0.15
                lx = inner[0] + (outer[0] - inner[0]) * tt
                ly = cye + hh * (0.62 + 0.25 * math.sin(math.pi * tt))
                out.append(f'<path d="M{lx:.1f} {ly:.1f}l{side * k * 0.02:.1f} {k * 0.035:.1f}" stroke="{ink_c}" stroke-width="{max(0.7, k * 0.012):.1f}" stroke-linecap="round"/>')
            out.append(f'<path d="M{inner[0]:.1f} {inner[1] - hh * 0.6:.1f}Q{cxe:.1f} {cye - hh * 0.9:.1f} {outer[0]:.1f} {outer[1] - hh * 0.5:.1f}" stroke="{shadow}" stroke-width="{max(0.8, k * 0.018):.1f}" fill="none" opacity="0.6"/>')
            continue
        op_ = 1.0 if eyes == "open" else 0.55
        top_y = cye - hh * op_ * (1 - lid)
        eye_d = f"M{inner[0]:.1f} {inner[1]:.1f}Q{cxe:.1f} {top_y - hh * 0.8:.1f} {outer[0]:.1f} {outer[1]:.1f}Q{cxe:.1f} {cye + hh * 1.25:.1f} {inner[0]:.1f} {inner[1]:.1f}Z"
        out.append(f'<path d="{eye_d}" fill="#F4ECE4"/>')
        ir = hh * 1.3
        ix, iy = cxe + gaze[0] * w * 0.45, cye + gaze[1] * hh * 0.5 + hh * 0.1
        cid = D.clip(f'<path d="{eye_d}"/>')
        out.append(f'<g {cid}><circle cx="{ix:.1f}" cy="{iy:.1f}" r="{ir:.1f}" fill="{D.rad([(0, lt(iris, 0.25)), (0.7, iris), (1, dk(iris, 0.45))])}"/>'
                   f'<circle cx="{ix:.1f}" cy="{iy:.1f}" r="{ir * 0.42:.1f}" fill="#120A08"/>'
                   f'<path d="M{inner[0]:.1f} {inner[1] - hh * 2:.1f}H{outer[0]:.1f}V{top_y + hh * 0.3:.1f}H{inner[0]:.1f}Z" fill="{shadow}" opacity="0.28"/></g>')
        out.append(f'<circle cx="{ix - ir * 0.32:.1f}" cy="{iy - ir * 0.35:.1f}" r="{max(0.8, ir * 0.22):.1f}" fill="#FFFFFF" opacity="0.95"/>')
        # upper lid line (heavier, with a lash flick), lower lid, crease
        out.append(f'<path d="M{inner[0]:.1f} {inner[1]:.1f}Q{cxe:.1f} {top_y - hh * 0.8:.1f} {outer[0]:.1f} {outer[1]:.1f}l{side * k * 0.04:.1f} {-k * 0.02:.1f}" stroke="{ink_c}" stroke-width="{max(1.2, k * 0.035) * line:.1f}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        out.append(f'<path d="M{inner[0] + side * w * 0.2:.1f} {inner[1] + hh * 0.35:.1f}Q{cxe:.1f} {cye + hh * 1.25:.1f} {outer[0]:.1f} {outer[1]:.1f}" stroke="{shadow}" stroke-width="{max(0.7, k * 0.014):.1f}" fill="none" opacity="0.7"/>')
        out.append(f'<path d="M{inner[0] + side * w * 0.1:.1f} {inner[1] - hh * 1.0:.1f}Q{cxe:.1f} {top_y - hh * 1.9:.1f} {outer[0] - side * w * 0.05:.1f} {outer[1] - hh * 0.9:.1f}" stroke="{shadow}" stroke-width="{max(0.7, k * 0.016):.1f}" fill="none" opacity="0.55"/>')
    # nose: a shadow plane on the side away from the light, nostrils, a lit tip
    nb = P(0.0, 0.38)
    side_n = sd
    ridge = [P(side_n * 0.06, -0.02), P(side_n * 0.09, 0.16), P(side_n * 0.12, 0.32)]
    out.append(taper(ridge, k * 0.015, k * 0.06 * nose_w, shadow, 0.22))
    for side in (-1, 1):
        nx_, ny_ = P(side * 0.1 * nose_w, 0.39)
        out.append(f'<path d="M{nx_ - side * k * 0.04:.1f} {ny_ - k * 0.02:.1f}q{side * k * 0.04:.1f} {k * 0.045:.1f} {side * k * 0.075:.1f} {-k * 0.005:.1f}" stroke="{dk(shadow, 0.15)}" stroke-width="{max(0.8, k * 0.022) * line:.1f}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    tip = P(-side_n * 0.02, 0.33)
    out.append(f'<ellipse cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" rx="{k * 0.05:.1f}" ry="{k * 0.035:.1f}" fill="#FFFFFF" opacity="0.35"/>')
    out.append(f'<ellipse cx="{nb[0]:.1f}" cy="{nb[1] + k * 0.06:.1f}" rx="{k * 0.12:.1f}" ry="{k * 0.03:.1f}" fill="{shadow}" opacity="0.25"/>')
    # mouth
    mx, my = P(0.0, 0.62)
    mw = k * 0.23 * (1 - 0.15 * abs(t))
    up = smile * k * 0.04
    ul = f"M{mx - mw:.1f} {my - up:.1f}Q{mx - mw * 0.5:.1f} {my - k * 0.07:.1f} {mx:.1f} {my - k * 0.035:.1f}Q{mx + mw * 0.5:.1f} {my - k * 0.07:.1f} {mx + mw:.1f} {my - up:.1f}Q{mx:.1f} {my + k * 0.01:.1f} {mx - mw:.1f} {my - up:.1f}Z"
    ll = f"M{mx - mw * 0.92:.1f} {my - up * 0.8:.1f}Q{mx:.1f} {my + k * 0.16:.1f} {mx + mw * 0.92:.1f} {my - up * 0.8:.1f}Q{mx:.1f} {my + k * 0.02:.1f} {mx - mw * 0.92:.1f} {my - up * 0.8:.1f}Z"
    out.append(f'<path d="{ul}" fill="{dk(lips, 0.12)}"/><path d="{ll}" fill="{lips}"/>')
    out.append(f'<ellipse cx="{mx + k * 0.02:.1f}" cy="{my + k * 0.06:.1f}" rx="{mw * 0.35:.1f}" ry="{k * 0.022:.1f}" fill="#FFFFFF" opacity="0.3"/>')
    out.append(f'<path d="M{mx - mw:.1f} {my - up:.1f}Q{mx:.1f} {my + k * 0.015:.1f} {mx + mw:.1f} {my - up:.1f}" stroke="{dk(lips, 0.5)}" stroke-width="{max(0.8, k * 0.02) * line:.1f}" fill="none" stroke-linecap="round"/>')
    if smile:
        for side in (-1, 1):
            out.append(f'<path d="M{mx + side * mw:.1f} {my - up:.1f}q{side * k * 0.04:.1f} {-k * 0.01:.1f} {side * k * 0.05:.1f} {-k * 0.04:.1f}" stroke="{shadow}" stroke-width="{max(0.7, k * 0.014):.1f}" fill="none" opacity="0.5"/>')
    # chin shadow and the faint contour
    out.append(f'<path d="{od}" fill="none" stroke="{outline or shadow}" stroke-width="{(max(1.6, k * 0.035) if outline else max(0.8, k * 0.02) * line):.1f}" opacity="{0.9 if outline else 0.55}"/>')
    return f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot})">{"".join(out)}</g>'


def soft(D, cx, cy, rx, ry, col, op, rot=0, key=None):
    """A soft-edged glaze: an ellipse whose colour fades to nothing at its rim (sfumato building block)."""
    g = D.rad([(0, col, op), (0.5, col, op * 0.6), (1, col, 0)])
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{g}" transform="rotate({rot} {cx:.1f} {cy:.1f})"/>'


# ================================================================ 16. The Kiss — Klimt, 1908
def curls(cx, cy, rx, ry, n, seed, cols, w=2.2):
    """Small hair curls: tight spirals scattered in an ellipse."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        r = math.sqrt(rnd.random())
        x, y = cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)
        s = rnd.uniform(2.5, 4.5)
        out.append(f'<path d="M{x - s:.1f} {y:.1f}a{s:.1f} {s:.1f} 0 1 1 {s:.1f} {s:.1f}" stroke="{rnd.choice(cols)}" stroke-width="{w}" fill="none" stroke-linecap="round"/>')
    return "".join(out)


@design("the-kiss")
def the_kiss():
    D = Doc("gmks")
    box = (110, 62, 490, 442)   # 380 square (180 x 180 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [wall(D, "#1E2A2A", 121, (0.5, 0.15), 0.35)]
    out.append(gilt_frame(D, box, 14, 123, "plain", gold=("#FFF2B8", "#E2BC58", "#B88E30", "#7A5818", "#3A2808")))
    cp = clip_box(D, box)
    rnd = random.Random(5)
    paint = [f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.rad([(0, "#B8964A"), (0.6, "#8A6A2E"), (1, "#5A4218")], 0.5, 0.4, 0.75)}"/>']
    paint.append(f'<g opacity="0.75">{"".join(f"<circle cx=\"{rnd.uniform(x0, x1):.0f}\" cy=\"{rnd.uniform(y0, y1):.0f}\" r=\"{rnd.uniform(0.5, 1.6):.1f}\" fill=\"{rnd.choice(["#E8C860", "#F6E098", "#C8A040", "#5A4018"])}\"/>" for _ in range(1600))}</g>')
    # the flowering meadow at the cliff's edge
    meadow = UV([(-0.02, 0.8), (0.2, 0.79), (0.45, 0.83), (0.62, 0.88), (0.7, 1.02), (-0.02, 1.02)])
    paint.append(f'<path d="{smooth_closed(meadow)}" fill="#2E5A3A"/>')
    for k in range(150):
        x, y = rnd.uniform(X(0), X(0.68)), rnd.uniform(Y(0.79), y1)
        if not inside((x, y), meadow):
            continue
        r = rnd.uniform(2, 4.6)
        c = rnd.choice(["#3A7A5A", "#5A9A4A", "#E8E0C8", "#C8402A", "#4A6AB8", "#E8B840", "#8A5AA8", "#2E6A4A"])
        paint.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{c}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.35:.1f}" fill="{rnd.choice(["#F6E098", "#FFFFFF", "#2A1A0A"])}"/>')
    # ---- the golden cloak that wraps them both
    cloak = UV([(0.43, 0.06), (0.53, 0.07), (0.6, 0.13), (0.66, 0.26), (0.71, 0.42), (0.72, 0.58), (0.68, 0.74), (0.64, 0.86), (0.66, 0.95),
                (0.56, 0.96), (0.44, 0.97), (0.33, 0.9), (0.26, 0.74), (0.22, 0.56), (0.22, 0.38), (0.27, 0.2), (0.34, 0.1)])
    cd = smooth_closed(cloak)
    paint.append(f'<path d="{cd}" fill="{D.lin([(0, "#F6DA78"), (0.5, "#E2B848"), (1, "#B88A2A")], 0, 0, 1, 1)}"/>')
    inner = []
    # gold swirls all over the cloak
    for k in range(70):
        x, y = rnd.uniform(X(0.22), X(0.72)), rnd.uniform(Y(0.06), Y(0.96))
        if not inside((x, y), cloak):
            continue
        r = rnd.uniform(3, 7)
        inner.append(f'<path d="M{x - r:.1f} {y:.1f}a{r:.1f} {r:.1f} 0 1 1 {r:.1f} {r:.1f}a{r * 0.5:.1f} {r * 0.5:.1f} 0 1 1 {-r * 0.4:.1f} {-r * 0.6:.1f}" stroke="#A87A20" stroke-width="1.2" fill="none" opacity="0.7"/>')
    # his robe: upright black, white and silver oblongs
    his = UV([(0.22, 0.2), (0.6, 0.13), (0.62, 0.3), (0.5, 0.5), (0.46, 0.66), (0.4, 0.98), (0.2, 0.98)])
    for k in range(46):
        x, y = rnd.uniform(X(0.22), X(0.6)), rnd.uniform(Y(0.16), Y(0.96))
        if not inside((x, y), his) or not inside((x, y), cloak):
            continue
        w_, h_ = rnd.uniform(6, 11), rnd.uniform(16, 34)
        c = rnd.choice(["#14100C", "#14100C", "#F2EEE4", "#B8B8B0", "#2A2420"])
        inner.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w_:.1f}" height="{h_:.1f}" fill="{c}" stroke="#5A4018" stroke-width="0.8"/>')
        if c == "#14100C" and rnd.random() < 0.6:
            inner.append(f'<rect x="{x + w_ * 0.25:.1f}" y="{y + h_ * 0.15:.1f}" width="{w_ * 0.5:.1f}" height="{h_ * 0.7:.1f}" fill="#E8C060" opacity="0.8"/>')
    # her dress: rounded blooms of red, violet and blue on gold
    hers = UV([(0.5, 0.52), (0.72, 0.44), (0.72, 0.6), (0.66, 0.8), (0.66, 0.97), (0.44, 0.97), (0.46, 0.68)])
    for k in range(70):
        x, y = rnd.uniform(X(0.44), X(0.72)), rnd.uniform(Y(0.44), Y(0.97))
        if not inside((x, y), hers) or not inside((x, y), cloak):
            continue
        r = rnd.uniform(3.5, 8)
        c = rnd.choice(["#C8402A", "#7A3A8A", "#2E4A9A", "#E87A6A", "#F2E8D0", "#3A7A6A"])
        inner.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{c}" stroke="#5A3A10" stroke-width="0.9"/>'
                     f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.5:.1f}" fill="none" stroke="#F6E098" stroke-width="1"/>'
                     f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.18:.1f}" fill="#F6E098"/>')
    paint.append(f'<g {D.clip(f"<path d=\"{cd}\"/>")}>{"".join(inner)}</g>')
    paint.append(f'<path d="{cd}" fill="none" stroke="#6A4A14" stroke-width="2"/>')
    # her bare feet curled over the cliff edge
    for k, (u, v) in enumerate([(0.62, 0.94), (0.66, 0.92)]):
        fx, fy = X(u), Y(v)
        foot = [(fx - 8, fy - 4), (fx + 4, fy - 6), (fx + 12, fy + 4), (fx + 10, fy + 12), (fx - 2, fy + 8)]
        paint.append(f'<path d="{smooth_closed(foot)}" fill="#F2D2BC" stroke="#A87A62" stroke-width="1.2"/>')
    # ---- heads: his bent down over hers; her face upturned, eyes closed
    # her hair: auburn, spreading down to the right behind her head, with little flowers
    hair = UV([(0.53, 0.3), (0.62, 0.27), (0.7, 0.33), (0.73, 0.45), (0.7, 0.56), (0.62, 0.53), (0.56, 0.47)])
    hd = smooth_closed(hair)
    paint.append(f'<path d="{hd}" fill="#7A3214"/>')
    paint.append(f'<g {D.clip(f"<path d=\"{hd}\"/>")}>{curls(X(0.63), Y(0.42), W * 0.1, H * 0.15, 70, 6, ["#B8582A", "#5A2008", "#D8783A", "#8A3A14"], 1.8)}</g>')
    for k in range(9):
        px, py = X(rnd.uniform(0.56, 0.72)), Y(rnd.uniform(0.3, 0.55))
        if inside((px, py), hair):
            paint.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.2" fill="{rnd.choice(["#4A6AC8", "#F2E8D8", "#C8302A"])}" stroke="#3A1A0A" stroke-width="0.7"/><circle cx="{px:.1f}" cy="{py:.1f}" r="1.1" fill="#F6E098"/>')
    # her face, cheek turned up to his kiss
    paint.append(face(D, X(0.555), Y(0.41), H * 0.165, rot=80, turn=-0.1, eyes="closed", skin=("#FFF4EA", "#F4D8C8", "#C8988C"),
                      lips="#C84850", brow="#8A4A2A", blush=0.5, ink_c="#5A2A1A", jaw=0.92, light=(0.5, -0.7)))
    # his head: dark curls wreathed in ivy, bent so that only cheek and ear show
    hx, hy = X(0.465), Y(0.19)
    cheek = UV([(0.48, 0.21), (0.53, 0.235), (0.545, 0.285), (0.525, 0.33), (0.49, 0.3), (0.465, 0.26)])
    paint.append(f'<path d="{smooth_closed(cheek)}" fill="{D.lin([(0, "#C89878"), (1, "#7A4A38")], 0, 0, 1, 1)}" stroke="#5A2A1A" stroke-width="1"/>')
    paint.append(f'<path d="{blob(X(0.49), Y(0.25), 4, 6, 9, 0.1, 10, 20)}" fill="#B87E66" stroke="#6A3A28" stroke-width="0.8"/>')
    paint.append(f'<path d="{blob(hx, hy, W * 0.09, H * 0.08, 3, 0.08, 16, 30)}" fill="#1E140E"/>')
    paint.append(curls(hx, hy, W * 0.08, H * 0.07, 44, 4, ["#3A2A1E", "#5A4030", "#0E0806"], 2))
    for k in range(10):
        a = math.radians(190 + k * 21)
        lx, ly = hx + W * 0.088 * math.cos(a), hy + H * 0.078 * math.sin(a)
        paint.append(leaf_simple_k(lx, ly, 10, math.degrees(a) + 90 + rnd.uniform(-15, 15), ("#9AC85A", "#4A8A2E", "#1E4A14"), k))
    # his hand at her cheek: slim fingers along her jaw
    for j in range(3):
        b0 = UV([(0.47 + j * 0.01, 0.475 + j * 0.012)])[0]
        b1 = UV([(0.53 + j * 0.012, 0.455 + j * 0.016)])[0]
        paint.append(taper([b0, lerp(b0, b1, 0.5), b1], 6.4, 4.2, "#8A5A44"))
        paint.append(taper([b0, lerp(b0, b1, 0.5), b1], 5.2, 3.4, "#E2B498"))
    out.append(f'<g {cp}>{"".join(paint)}{varnish(D, box, 0.14, 0.2, 6, 0.3)}</g>')
    out.append(museum_label(D, 488, "The Kiss", "GUSTAV KLIMT · 1908", "#F2DC98", "#C8A860", ts=36, bs=18, gap=34))
    return finish(D, out, 67)


def leaf_simple_k(x, y, L, ang, pal, seed):
    a = math.radians(ang)
    tip = (x + L * math.cos(a), y + L * math.sin(a))
    nx, ny = -math.sin(a) * L * 0.35, math.cos(a) * L * 0.35
    mid = ((x + tip[0]) / 2, (y + tip[1]) / 2)
    d = f"M{x:.1f} {y:.1f}Q{mid[0] + nx:.1f} {mid[1] + ny:.1f} {tip[0]:.1f} {tip[1]:.1f}Q{mid[0] - nx:.1f} {mid[1] - ny:.1f} {x:.1f} {y:.1f}Z"
    return f'<path d="{d}" fill="{pal[1]}" stroke="{pal[2]}" stroke-width="0.9"/><path d="M{x:.1f} {y:.1f}L{tip[0]:.1f} {tip[1]:.1f}" stroke="{pal[0]}" stroke-width="0.8"/>'


# ================================================================ 17. The Little Street — Vermeer, c. 1658
def ls_bricks(D, poly_d, box, seed, base="#74402F", cols=("#8A4A36", "#7A4030", "#94543E", "#6A382A", "#A0624A", "#7E4634", "#5E3226", "#8E5A48"), course=4.2, brick=11,
              mortar="#B4A48C", mop=0.42, light=None, soot=True):
    """Brickwork clipped to a shape: base colour, staggered bricks of slightly different fired tints, mortar courses."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = [f'<path d="{poly_d}" fill="{base}"/>']
    bricks = []
    rows = int((y1 - y0) / course) + 1
    for r in range(rows):
        y = y0 + r * course
        off = (brick / 2) * (r % 2)
        x = x0 - off
        while x < x1:
            w = brick * rnd.uniform(0.9, 1.1)
            bricks.append(f'<rect x="{x + 0.5:.1f}" y="{y + 0.5:.1f}" width="{w - 1:.1f}" height="{course - 1:.1f}" fill="{rnd.choice(cols)}" opacity="{rnd.uniform(0.55, 1):.2f}"/>')
            x += w
    lines = "".join(f'M{x0:.0f} {y0 + r * course:.1f}H{x1:.0f}' for r in range(rows))
    c = D.clip(f'<path d="{poly_d}"/>')
    grime = ""
    if soot:
        grime = "".join(f'<path d="M{rnd.uniform(x0, x1):.1f} {rnd.uniform(y0, y1):.1f}v{rnd.uniform(10, 40):.1f}" stroke="{rnd.choice(["#3A2018", "#5A3A2E", "#C8A890"])}" stroke-width="{rnd.uniform(2, 6):.1f}" opacity="{rnd.uniform(0.08, 0.2):.2f}" stroke-linecap="round"/>'
                        for _ in range(int((x1 - x0) * (y1 - y0) / 900)))
    out.append(f'<g {c}>{"".join(bricks)}<path d="{lines}" stroke="{mortar}" stroke-width="0.8" opacity="{mop}"/>{grime}{light or ""}</g>')
    return "".join(out)


def ls_window(D, x, y, w, h, seed, frame="#2A2018", glass=("#3A4A44", "#5A6A60", "#22302C"), panes=(3, 4), shutters=None, sh_col="#7A2E20", lit=0.0):
    """A Dutch leaded window: dark frame, small panes of greenish glass catching the sky, optional open shutters."""
    rnd = random.Random(seed)
    out = []
    if shutters:
        sw = w * 0.48
        for sx, side in ((x - sw - 1.5, -1), (x + w + 1.5, 1)):
            out.append(f'<rect x="{sx:.1f}" y="{y:.1f}" width="{sw:.1f}" height="{h:.1f}" fill="{sh_col}"/>')
            for k in range(1, 4):
                out.append(f'<path d="M{sx + sw * k / 4:.1f} {y + 1:.1f}V{y + h - 1:.1f}" stroke="{dk(sh_col, 0.35)}" stroke-width="0.8"/>')
            out.append(f'<rect x="{sx:.1f}" y="{y:.1f}" width="{sw:.1f}" height="{h:.1f}" fill="none" stroke="{dk(sh_col, 0.5)}" stroke-width="1"/>')
            out.append(f'<path d="M{sx + (0 if side < 0 else sw):.1f} {y:.1f}v{h:.1f}" stroke="{lt(sh_col, 0.3)}" stroke-width="1" opacity="0.6"/>')
    out.append(f'<rect x="{x - 1.5:.1f}" y="{y - 1.5:.1f}" width="{w + 3:.1f}" height="{h + 3:.1f}" fill="{frame}"/>')
    nx, ny = panes
    pw, ph = w / nx, h / ny
    for i in range(nx):
        for j in range(ny):
            px, py = x + i * pw, y + j * ph
            c = rnd.choice(glass)
            out.append(f'<rect x="{px + 0.6:.1f}" y="{py + 0.6:.1f}" width="{pw - 1.2:.1f}" height="{ph - 1.2:.1f}" fill="{c}"/>')
            if rnd.random() < 0.35 + lit:
                out.append(f'<rect x="{px + 0.8:.1f}" y="{py + 0.8:.1f}" width="{(pw - 1.6) * rnd.uniform(0.3, 0.8):.1f}" height="{(ph - 1.6) * 0.5:.1f}" fill="#C8D4D0" opacity="{rnd.uniform(0.2, 0.5):.2f}"/>')
    out.append(f'<path d="M{x + w / 2:.1f} {y:.1f}V{y + h:.1f}M{x:.1f} {y + h / 2:.1f}H{x + w:.1f}" stroke="{frame}" stroke-width="1.6"/>')
    out.append(f'<rect x="{x - 2:.1f}" y="{y + h + 1:.1f}" width="{w + 4:.1f}" height="2" fill="#D8CEB8"/>')
    return "".join(out)


def ls_cloud(D, cx, cy, rx, ry, seed):
    rnd = random.Random(seed)
    out = []
    for k in range(16):
        a = rnd.uniform(math.pi, 2 * math.pi)
        r = rnd.uniform(0.2, 0.9)
        px, py = cx + rx * r * math.cos(a), cy + ry * 0.6 * r * math.sin(a)
        rr = rnd.uniform(0.3, 0.55) * rx
        out.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{rr:.1f}" ry="{rr * 0.7:.1f}" fill="{D.rad([(0, "#FFFFFF", 0.95), (0.6, "#F2F2EC", 0.6), (1, "#E8E8E0", 0)], 0.42, 0.38, 0.6)}"/>')
    out.append(f'<ellipse cx="{cx:.1f}" cy="{cy + ry * 0.25:.1f}" rx="{rx * 0.95:.1f}" ry="{ry * 0.3:.1f}" fill="{D.rad([(0, "#B8BCC0", 0.6), (1, "#B8BCC0", 0)])}"/>')
    return "".join(out)


def ls_flakes(rnd, X, Y, u0, u1, n):
    """Patches where the whitewash has flaked and a few bricks show through."""
    out = []
    for k in range(n):
        fx, fy = X(rnd.uniform(u0, u1)), Y(rnd.uniform(0.63, 0.88))
        for j in range(rnd.randint(1, 3)):
            bx, by = fx + rnd.uniform(-4, 4) + (j % 2) * 4, fy + j * 4.2
            out.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{rnd.uniform(5, 9):.1f}" height="3.2" fill="{rnd.choice(["#9A5A44", "#8A4A36", "#A86A50"])}" opacity="{rnd.uniform(0.35, 0.6):.2f}"/>')
    return "".join(out)


@design("the-little-street")
def little_street():
    from figures import person
    D = Doc("gmls")
    box = (153, 62, 447, 424)   # 294 x 362 (54.3 x 44 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [wall(D, "#4A5048", 131, (0.5, 0.15), 0.3)]
    out.append(simple_frame(D, box, 17, ("#4A4038", "#16120E", "#060504"), 3))
    out.append(f'<rect x="{x0 - 5}" y="{y0 - 5}" width="{W + 10}" height="{H + 10}" fill="none" stroke="#C8A050" stroke-width="3"/>')
    cp = clip_box(D, box)
    rnd = random.Random(9)
    P = []
    WASH, WASH_SH = "#ECE8DA", "#C8C2B0"
    # ---- sky over the rooftops, a few fair-weather clouds
    P.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H * 0.45}" fill="{D.lin([(0, "#A8BCCC"), (0.6, "#C8D4D8"), (1, "#E2E6E0")])}"/>')
    P.append(ls_cloud(D, X(0.16), Y(0.11), W * 0.2, H * 0.08, 3))
    P.append(ls_cloud(D, X(0.36), Y(0.05), W * 0.14, H * 0.05, 4))
    P.append(ls_cloud(D, X(0.05), Y(0.22), W * 0.12, H * 0.05, 5))
    # ---- the house beyond, at the left: a red-tiled roof and a chimney against the sky
    roof = UV([(-0.02, 0.33), (0.1, 0.24), (0.3, 0.22), (0.42, 0.3), (0.42, 0.36), (-0.02, 0.36)])
    rd = pd(roof)
    tiles = "".join(f'M{X(-0.02):.0f} {Y(0.22) + k * 3.2:.1f}H{X(0.45):.0f}' for k in range(14))
    P.append(f'<path d="{rd}" fill="#9A4A30"/><g {D.clip(f"<path d=\"{rd}\"/>")}><path d="{tiles}" stroke="#6A2E1C" stroke-width="0.9" opacity="0.7"/>'
             f'<rect x="{X(-0.02)}" y="{Y(0.22)}" width="{W * 0.47}" height="{H * 0.14}" fill="{D.lin([(0, "#C87A52", 0.4), (1, "#3A1A10", 0.4)], 0, 0, 1, 0)}"/></g>')
    P.append(ls_bricks(D, pd(UV([(0.18, 0.24), (0.18, 0.15), (0.24, 0.15), (0.24, 0.235)])), (X(0.17), Y(0.14), X(0.25), Y(0.25)), 30, course=3.4, brick=8))
    P.append(f'<rect x="{X(0.172):.1f}" y="{Y(0.14):.1f}" width="{W * 0.076:.1f}" height="3" fill="#5A2A1A"/>')

    # ---- the left house: brick above, whitewashed below, a gateway into the passage, a closed door
    left = UV([(-0.02, 0.36), (0.42, 0.36), (0.42, 0.93), (-0.02, 0.93)])
    ld = pd(left)
    P.append(ls_bricks(D, ld, (X(-0.02), Y(0.36), X(0.42), Y(0.93)), 31))
    wash_l = UV([(-0.02, 0.6), (0.06, 0.598), (0.14, 0.61), (0.2, 0.6), (0.42, 0.6), (0.42, 0.93), (-0.02, 0.93)])
    P.append(f'<path d="{pd(wash_l)}" fill="{WASH}"/>')
    P.append(strokes(D.nid(), pd(wash_l), (X(-0.02), Y(0.6), X(0.42), Y(0.93)), ["#F6F4EA", "#D8D2C0", "#E0DACA"], 33, n=60, angle=-80,
                     length=(8, 24), width=(2, 5), opacity=(0.25, 0.5), curve=0.1))
    # flakes where the brick shows through the whitewash
    P.append(ls_flakes(rnd, X, Y, 0.0, 0.4, 5))
    # windows of the left house (upper floor)
    P.append(ls_window(D, X(0.05), Y(0.41), W * 0.1, H * 0.1, 50, panes=(3, 4)))
    P.append(ls_window(D, X(0.22), Y(0.41), W * 0.1, H * 0.1, 51, panes=(3, 4)))
    # the closed door at the far left
    P.append(f'<rect x="{X(0.03):.1f}" y="{Y(0.66):.1f}" width="{W * 0.11:.1f}" height="{H * 0.27:.1f}" fill="#3A2E22"/>')
    for k in range(1, 4):
        P.append(f'<path d="M{X(0.03) + W * 0.11 * k / 4:.1f} {Y(0.665):.1f}V{Y(0.93):.1f}" stroke="#241C14" stroke-width="1"/>')
    P.append(f'<rect x="{X(0.03):.1f}" y="{Y(0.66):.1f}" width="{W * 0.11:.1f}" height="{H * 0.27:.1f}" fill="none" stroke="#1A140E" stroke-width="1.4"/>')
    # the gateway: a deep passage, its far end bright, the maid bent over the rain barrel
    gx0, gx1, gy0 = X(0.22), X(0.36), Y(0.64)
    gate = f"M{gx0:.1f} {Y(0.93):.1f}V{gy0 + 10:.1f}Q{gx0:.1f} {gy0:.1f} {gx0 + 10:.1f} {gy0:.1f}H{gx1 - 10:.1f}Q{gx1:.1f} {gy0:.1f} {gx1:.1f} {gy0 + 10:.1f}V{Y(0.93):.1f}Z"
    P.append(f'<path d="{gate}" fill="{D.lin([(0, "#2A241C"), (0.5, "#4A4234"), (1, "#5A5242")], 0, 0, 0, 1)}"/>')
    gc = D.clip(f'<path d="{gate}"/>')
    inner = [f'<rect x="{gx0 + 12:.1f}" y="{gy0 + 6:.1f}" width="{gx1 - gx0 - 24:.1f}" height="{Y(0.86) - gy0 - 6:.1f}" fill="{D.lin([(0, "#D8D4C4"), (1, "#B8B2A0")])}"/>',
             f'<path d="{pd([(gx0, gy0), (gx0 + 12, gy0 + 6), (gx0 + 12, Y(0.86)), (gx0, Y(0.93))])}" fill="#3A3226"/>',
             f'<path d="{pd([(gx1, gy0), (gx1 - 12, gy0 + 6), (gx1 - 12, Y(0.86)), (gx1, Y(0.93))])}" fill="#4A4032"/>',
             f'<path d="{pd([(gx0 + 12, Y(0.86)), (gx1 - 12, Y(0.86)), (gx1, Y(0.93)), (gx0, Y(0.93))])}" fill="#6A6252"/>']
    # rain barrel and the maid stooping over it
    bxr, byr = gx0 + 16, Y(0.858)
    inner.append(f'<path d="M{bxr:.1f} {byr:.1f}v-11q5 -2 10 0v11z" fill="#5A4430"/><path d="M{bxr:.1f} {byr - 4:.1f}h10M{bxr:.1f} {byr - 9:.1f}h10" stroke="#2A2018" stroke-width="0.8"/>')
    mx_, my_ = gx0 + 30, Y(0.858)
    maid = [(mx_ - 5, my_), (mx_ - 6, my_ - 9), (mx_ - 8, my_ - 15), (mx_ - 4, my_ - 19), (mx_ + 2, my_ - 16), (mx_ + 4, my_ - 9), (mx_ + 5, my_)]
    inner.append(f'<path d="{smooth_closed(maid)}" fill="#7A3A2A"/>')
    inner.append(f'<path d="{smooth_closed([(mx_ - 8, my_ - 15), (mx_ - 4, my_ - 19), (mx_ + 1, my_ - 17), (mx_ - 2, my_ - 13)])}" fill="#3A4A5A"/>')
    inner.append(f'<path d="{smooth_closed([(mx_ - 8, my_ - 9), (mx_ - 6, my_), (mx_ + 5, my_), (mx_ + 3, my_ - 8)])}" fill="#2A3A5A"/>')
    inner.append(f'<path d="{blob(mx_ - 10, my_ - 17, 2.6, 2.4, 3, 0.1, 8)}" fill="#F2EEE4"/>')
    inner.append(f'<path d="M{mx_ - 8:.1f} {my_ - 14:.1f}l-4 4" stroke="#E0B898" stroke-width="1.6" stroke-linecap="round"/>')
    P.append(f'<g {gc}>{"".join(inner)}</g>')
    P.append(f'<path d="{gate}" fill="none" stroke="#2A2018" stroke-width="1.2"/>')

    # ---- the main house: a tall brick facade with a crow-stepped gable, whitewashed at the foot
    steps = [(0.42, 0.36), (0.42, 0.3), (0.47, 0.3), (0.47, 0.24), (0.52, 0.24), (0.52, 0.18), (0.57, 0.18), (0.57, 0.12), (0.62, 0.12), (0.62, 0.06),
             (0.67, 0.06), (0.67, 0.0), (0.72, 0.0), (0.72, -0.05)]
    house = UV(steps + [(1.03, -0.05), (1.03, 0.93), (0.42, 0.93)])
    hd = pd(house)
    shade_r = f'<rect x="{X(0.42)}" y="{y0}" width="{W * 0.6}" height="{H}" fill="{D.lin([(0, "#FFE8C8", 0.14), (0.45, "#000", 0), (1, "#140A06", 0.32)], 0, 0, 1, 0.4)}"/>'
    P.append(ls_bricks(D, hd, (X(0.42), y0, X(1.03), Y(0.93)), 61, light=shade_r))
    # stone coping on each step of the gable
    for i in range(0, len(steps) - 2, 2):
        (ua, va), (ub, vb) = steps[i + 1], steps[i + 2]
        P.append(f'<rect x="{X(ua) - 1:.1f}" y="{Y(va) - 2:.1f}" width="{X(ub) - X(ua) + 2:.1f}" height="3" fill="#D8CEB8"/>')
    # whitewashed lower storey
    wash = UV([(0.42, 0.6), (0.6, 0.605), (0.8, 0.598), (1.03, 0.6), (1.03, 0.93), (0.42, 0.93)])
    P.append(f'<path d="{pd(wash)}" fill="{WASH}"/>')
    P.append(strokes(D.nid(), pd(wash), (X(0.42), Y(0.6), X(1.03), Y(0.93)), ["#F8F6EE", "#D6D0BE", "#E4DED0"], 63, n=90, angle=-82,
                     length=(8, 26), width=(2, 5), opacity=(0.25, 0.5), curve=0.1))
    P.append(ls_flakes(rnd, X, Y, 0.44, 1.0, 7))
    # grime rising from the street on the whitewash, a stone ledge where the whitewash stops
    for wd in (pd(wash), pd(wash_l)):
        P.append(f'<path d="{wd}" fill="{D.lin([(0, "#000", 0), (0.7, "#6A5A48", 0), (1, "#6A5A48", 0.35)])}"/>')
    P.append(f'<rect x="{X(-0.02):.1f}" y="{Y(0.597):.1f}" width="{W * 1.05:.1f}" height="3.2" fill="#B8AC94"/><rect x="{X(-0.02):.1f}" y="{Y(0.597):.1f}" width="{W * 1.05:.1f}" height="1.2" fill="#F2EAD8"/>')
    # windows: small ones in the gable, two tall casements above, one with red shutters below
    P.append(ls_window(D, X(0.63), Y(0.14), W * 0.06, H * 0.06, 80, panes=(2, 3)))
    P.append(ls_window(D, X(0.53), Y(0.27), W * 0.07, H * 0.07, 81, panes=(2, 3)))
    P.append(ls_window(D, X(0.78), Y(0.22), W * 0.09, H * 0.08, 82, panes=(3, 3)))
    P.append(ls_window(D, X(0.5), Y(0.4), W * 0.13, H * 0.13, 83, panes=(4, 5)))
    P.append(ls_window(D, X(0.78), Y(0.4), W * 0.13, H * 0.13, 84, panes=(4, 5)))
    P.append(ls_window(D, X(0.84), Y(0.66), W * 0.1, H * 0.11, 85, panes=(3, 4), shutters=True))
    # lintels of pale stone over the windows
    for (u, v, w_) in ((0.5, 0.4, 0.13), (0.78, 0.4, 0.13), (0.78, 0.22, 0.09)):
        P.append(f'<rect x="{X(u) - 3:.1f}" y="{Y(v) - 6:.1f}" width="{W * w_ + 6:.1f}" height="4" fill="#C8B89A"/><rect x="{X(u) - 3:.1f}" y="{Y(v) - 6:.1f}" width="{W * w_ + 6:.1f}" height="1.2" fill="#F2EAD8"/>')
    # the open door, the woman sewing in the doorway
    dx0, dx1, dy0 = X(0.6), X(0.74), Y(0.64)
    P.append(f'<rect x="{dx0 - 3:.1f}" y="{dy0 - 3:.1f}" width="{dx1 - dx0 + 6:.1f}" height="{Y(0.93) - dy0 + 3:.1f}" fill="#2E2418"/>')
    P.append(f'<rect x="{dx0:.1f}" y="{dy0:.1f}" width="{dx1 - dx0:.1f}" height="{Y(0.93) - dy0:.1f}" fill="{D.lin([(0, "#3A3024"), (1, "#1E1810")], 0, 0, 1, 0)}"/>')
    P.append(f'<rect x="{dx0 + 3:.1f}" y="{Y(0.86):.1f}" width="{dx1 - dx0 - 6:.1f}" height="{Y(0.93) - Y(0.86):.1f}" fill="#5A4A38"/>')
    # the open leaf of the door, folded back against the wall, and the upper half-door
    P.append(f'<path d="{pd([(dx1, dy0), (dx1 + 7, dy0 + 3), (dx1 + 7, Y(0.92)), (dx1, Y(0.93))])}" fill="#4A3A26"/>')
    wx, wy = dx0 + (dx1 - dx0) * 0.45, Y(0.9)
    sitter = [(wx - 9, wy), (wx - 10, wy - 8), (wx - 7, wy - 14), (wx - 6, wy - 20), (wx - 2, wy - 26), (wx + 3, wy - 25), (wx + 5, wy - 18), (wx + 6, wy - 12),
              (wx + 11, wy - 8), (wx + 12, wy)]
    P.append(f'<path d="{smooth_closed(sitter)}" fill="#2E3E5A"/>')
    P.append(f'<path d="{smooth_closed([(wx - 6, wy - 20), (wx - 2, wy - 26), (wx + 3, wy - 25), (wx + 5, wy - 18), (wx + 2, wy - 14), (wx - 5, wy - 14)])}" fill="#C8A048"/>')
    P.append(f'<path d="{smooth_closed([(wx - 9, wy - 7), (wx - 1, wy - 11), (wx + 6, wy - 10), (wx + 4, wy - 5), (wx - 6, wy - 4)])}" fill="#E8E2D2"/>')
    P.append(f'<path d="{blob(wx - 1, wy - 29.5, 3.6, 3.8, 5, 0.06, 10)}" fill="#F4F0E6"/><path d="{blob(wx - 2.6, wy - 28.6, 1.8, 2.4, 6, 0.06, 8)}" fill="#E0B496"/>')
    P.append(f'<path d="M{wx - 5:.1f} {wy - 17:.1f}l-3 8" stroke="#C8A048" stroke-width="2.2" stroke-linecap="round"/><circle cx="{wx - 8:.1f}" cy="{wy - 9:.1f}" r="1.3" fill="#E0B496"/>')
    # a bench by the door
    P.append(f'<rect x="{X(0.47):.1f}" y="{Y(0.885):.1f}" width="{W * 0.11:.1f}" height="2.6" fill="#5A4430"/><path d="M{X(0.48):.1f} {Y(0.89):.1f}v{H * 0.04:.1f}M{X(0.57):.1f} {Y(0.89):.1f}v{H * 0.04:.1f}" stroke="#3A2C1E" stroke-width="1.6"/>')
    # the vine climbing the corner of the house
    vine = []
    for k in range(150):
        t = rnd.random()
        spread_ = 6 + t * 16
        vx = X(0.4) + math.sin(t * 9) * 5 + rnd.uniform(-spread_ * 0.6, spread_)
        vy = Y(0.93) - t * H * 0.52 + rnd.uniform(-4, 4)
        vine.append(f'<path d="{blob(vx, vy, rnd.uniform(2.4, 4.2), rnd.uniform(1.8, 3.2), 300 + k, 0.2, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#4A6A30", "#3A5A28", "#6A8A3E", "#2A4020", "#8AA04A"])}"/>')
    P.append(f'<path d="M{X(0.4):.1f} {Y(0.93):.1f}C{X(0.42):.1f} {Y(0.8):.1f} {X(0.38):.1f} {Y(0.65):.1f} {X(0.41):.1f} {Y(0.45):.1f}" stroke="#4A3A28" stroke-width="1.6" fill="none"/>')
    P.append("".join(vine))
    # ---- the street: brick paving, a gutter, two children kneeling at play
    street = UV([(-0.02, 0.93), (1.03, 0.93), (1.03, 1.03), (-0.02, 1.03)])
    sd = pd(street)
    P.append(ls_bricks(D, sd, (X(-0.02), Y(0.93), X(1.03), Y(1.03)), 90, base="#8A7060", cols=("#9A7A66", "#7A6050", "#A88A72", "#6A5446"), course=3.6, brick=7,
                       mortar="#4A3A30", mop=0.5, soot=False))
    P.append(f'<rect x="{X(-0.02):.1f}" y="{Y(0.93):.1f}" width="{W * 1.05:.1f}" height="2.4" fill="#5A4A3E"/>')
    P.append(f'<rect x="{X(-0.02):.1f}" y="{Y(0.965):.1f}" width="{W * 1.05:.1f}" height="2" fill="#4A3C32" opacity="0.7"/>')
    for k, (u, top, skirt) in enumerate(((0.47, "#7A2E22", "#2A3A5A"), (0.535, "#3A4A6A", "#5A3A2A"))):
        cx_, cy_ = X(u), Y(0.985)
        kid = [(cx_ - 5, cy_), (cx_ - 6, cy_ - 5), (cx_ - 4, cy_ - 11), (cx_, cy_ - 13), (cx_ + 4, cy_ - 11), (cx_ + 5, cy_ - 5), (cx_ + 7, cy_)]
        P.append(f'<ellipse cx="{cx_ + 2:.1f}" cy="{cy_ + 0.5:.1f}" rx="8" ry="1.6" fill="#2A1E16" opacity="0.4"/>')
        P.append(f'<path d="{smooth_closed(kid)}" fill="{skirt}"/>')
        P.append(f'<path d="{smooth_closed([(cx_ - 4, cy_ - 6), (cx_ - 4, cy_ - 11), (cx_, cy_ - 13), (cx_ + 4, cy_ - 11), (cx_ + 4, cy_ - 6)])}" fill="{top}"/>')
        P.append(f'<path d="{blob(cx_, cy_ - 15.5, 2.8, 3, 7 + k, 0.06, 10)}" fill="#F2EEE4"/>')
    # Vermeer's daylight: a warm glow over the left, the faint shadow of the eaves across the facade
    P.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.rad([(0, "#FFF4DC", 0.18), (1, "#FFF4DC", 0)], 0.25, 0.5, 0.6)}"/>')
    out.append(f'<g {cp}>{"".join(P)}{canvas_weave(D, box, 0.04)}{varnish(D, box, 0.1, 0.25, 8, 0.4)}</g>')
    out.append(museum_label(D, 486, "The Little Street", "JOHANNES VERMEER · c. 1658", "#F2EADA", "#C8BCA2", ts=30, bs=17, gap=28, max_w=440))
    return finish(D, out, 71)


# ================================================================ 18. View of Delft — Vermeer, c. 1661
def ripple_frame(D, box, w, seed):
    """Dutch ebony 'ripple' frame: black moulding with fine wavy guilloché bands catching the light."""
    out = [simple_frame(D, box, w, ("#4A443E", "#121010", "#040303"), seed)]
    ob = (box[0] - w, box[1] - w, box[2] + w, box[3] + w)
    for t, op in ((0.25, 0.35), (0.6, 0.3)):
        x0, y0, x1, y1 = ob[0] + w * t, ob[1] + w * t, ob[2] - w * t, ob[3] - w * t
        rip = []
        for (ax, ay, bx, by) in ((x0, y0, x1, y0), (x0, y1, x1, y1)):
            n = int((bx - ax) / 3)
            rip.append("M" + " L".join(f"{ax + (bx - ax) * i / n:.1f} {ay + (1.2 if i % 2 else -1.2):.1f}" for i in range(n + 1)))
        for (ax, ay, bx, by) in ((x0, y0, x0, y1), (x1, y0, x1, y1)):
            n = int((by - ay) / 3)
            rip.append("M" + " L".join(f"{ax + (1.2 if i % 2 else -1.2):.1f} {ay + (by - ay) * i / n:.1f}" for i in range(n + 1)))
        out.append(f'<path d="{" ".join(rip)}" stroke="#8A8278" stroke-width="0.9" fill="none" opacity="{op}"/>')
    return "".join(out)


def cumulus(D, cx, cy, rx, ry, seed, lit="#FFFFFF", mid="#D8D4C8", dark="#8A8C90", n=14):
    """A rounded cloud built of soft puffs: bright tops, grey undersides."""
    rnd = random.Random(seed)
    out = []
    puffs = [(cx + rx * rnd.uniform(-0.9, 0.9), cy + ry * rnd.uniform(-0.6, 0.5), rx * rnd.uniform(0.25, 0.45)) for _ in range(n)]
    for px, py, r in sorted(puffs, key=lambda p: -p[1]):
        out.append(soft(D, px, py + r * 0.25, r * 1.1, r * 0.8, dark, 0.55))
    for px, py, r in sorted(puffs, key=lambda p: -p[1]):
        out.append(soft(D, px, py, r, r * 0.8, mid, 0.85))
        out.append(soft(D, px - r * 0.2, py - r * 0.3, r * 0.75, r * 0.5, lit, 0.9))
    return "".join(out)


@design("view-of-delft")
def view_of_delft():
    D = Doc("gmvd")
    box = (66, 70, 534, 454)   # 468 x 384 (96.5 x 117.5 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [wall(D, "#5A6466", 151, (0.5, 0.15), 0.3)]
    out.append(ripple_frame(D, box, 18, 3))
    cp = clip_box(D, box)
    rnd = random.Random(8)
    paint = []
    # sky: a heavy grey cloud bank above, blue breaking through, bright cumulus low over the town
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.lin([(0, "#5A6A7A"), (0.25, "#7A98B8"), (0.5, "#A8C0D4"), (0.6, "#D8DCD8")])}"/>')
    for k in range(9):
        paint.append(soft(D, X(rnd.uniform(-0.1, 1.1)), Y(rnd.uniform(-0.05, 0.12)), W * rnd.uniform(0.2, 0.35), H * rnd.uniform(0.06, 0.1), rnd.choice(["#3A4450", "#4A5460", "#5A646E"]), 0.8))
    for k, (u, v, rx, ry) in enumerate([(0.15, 0.3, 70, 26), (0.45, 0.24, 90, 30), (0.78, 0.3, 80, 26), (0.3, 0.42, 70, 16), (0.65, 0.42, 90, 16), (0.95, 0.4, 40, 14)]):
        paint.append(cumulus(D, X(u), Y(v), rx, ry, 30 + k, "#FFFDF4", "#E8E4D8", "#8A9098"))
    # the town: a long frieze of roofs, gates and towers along the far quay
    sky_line = 0.5
    town = []
    # back row: pale sunlit roofs and the New Church tower catching the sun
    xx = X(-0.02)
    while xx < X(1.02):
        w_ = rnd.uniform(10, 22)
        h_ = rnd.uniform(14, 30)
        top = Y(0.56) - h_
        town.append(f'<path d="{pd([(xx, Y(0.6)), (xx, top + 6), (xx + w_ / 2, top), (xx + w_, top + 6), (xx + w_, Y(0.6))])}" fill="{rnd.choice(["#C8A070", "#D8B888", "#B8906A", "#E0C49A"])}" opacity="0.85"/>')
        xx += w_ * rnd.uniform(0.7, 1.0)
    tx = X(0.7)
    town.append(f'<path d="{pd([(tx - 8, Y(0.58)), (tx - 8, Y(0.44)), (tx - 6, Y(0.42)), (tx - 6, Y(0.38)), (tx - 3, Y(0.36)), (tx, Y(0.3)), (tx + 3, Y(0.36)), (tx + 6, Y(0.38)), (tx + 6, Y(0.42)), (tx + 8, Y(0.44)), (tx + 8, Y(0.58))])}" fill="#F2DC98"/>')
    town.append(f'<path d="{pd([(tx + 2, Y(0.58)), (tx + 2, Y(0.44)), (tx + 8, Y(0.44)), (tx + 8, Y(0.58))])}" fill="#C8A868"/>')
    town.append(f'<path d="M{tx} {Y(0.3)}V{Y(0.27)}" stroke="#8A7A5A" stroke-width="1.2"/>')
    # front row: dark red roofs, then the Schiedam gate (left) and the Rotterdam gate (right)
    xx = X(-0.02)
    while xx < X(1.02):
        w_ = rnd.uniform(14, 26)
        h_ = rnd.uniform(10, 22)
        base = Y(0.66)
        top = Y(0.6) - h_ * 0.5
        roof = rnd.choice(["#8A3A24", "#9A4A2A", "#6A2A1A", "#7A3A2A"])
        town.append(f'<path d="{pd([(xx, base), (xx, top + h_ * 0.4), (xx + w_, top + h_ * 0.4), (xx + w_, base)])}" fill="{rnd.choice(["#5A4A3A", "#6A5644", "#4A3E32"])}"/>')
        town.append(f'<path d="{pd([(xx - 1, top + h_ * 0.42), (xx + w_ / 2, top - h_ * 0.2), (xx + w_ + 1, top + h_ * 0.42)])}" fill="{roof}"/>')
        for _ in range(2):
            town.append(f'<rect x="{xx + rnd.uniform(2, w_ - 5):.1f}" y="{top + h_ * 0.55 + rnd.uniform(0, 6):.1f}" width="2.4" height="3.2" fill="#2A2018"/>')
        xx += w_
    # Schiedam gate with its clock tower and twin turrets
    gx = X(0.3)
    town.append(f'<path d="{pd([(gx - 26, Y(0.66)), (gx - 26, Y(0.5)), (gx + 26, Y(0.5)), (gx + 26, Y(0.66))])}" fill="#7A6A54"/>')
    town.append(f'<path d="{pd([(gx - 28, Y(0.5)), (gx, Y(0.44)), (gx + 28, Y(0.5))])}" fill="#4A3A2E"/>')
    town.append(f'<path d="{pd([(gx - 6, Y(0.45)), (gx - 6, Y(0.38)), (gx, Y(0.33)), (gx + 6, Y(0.38)), (gx + 6, Y(0.45))])}" fill="#5A4A3A"/>')
    town.append(f'<circle cx="{gx}" cy="{Y(0.47):.1f}" r="3.6" fill="#E8C870" stroke="#3A2A1A" stroke-width="0.8"/>')
    for s_ in (-1, 1):
        town.append(f'<path d="{pd([(gx + s_ * 30 - 5, Y(0.66)), (gx + s_ * 30 - 5, Y(0.48)), (gx + s_ * 30, Y(0.43)), (gx + s_ * 30 + 5, Y(0.48)), (gx + s_ * 30 + 5, Y(0.66))])}" fill="#6A5A48"/>')
    town.append(f'<path d="{pd([(gx - 10, Y(0.66)), (gx - 10, Y(0.6)), (gx + 10, Y(0.6)), (gx + 10, Y(0.66))])}" fill="#2A2018"/>')
    # Rotterdam gate: twin dark towers with pointed blue roofs
    rx_ = X(0.82)
    for s_ in (-1, 1):
        cx_ = rx_ + s_ * 16
        town.append(f'<path d="{pd([(cx_ - 9, Y(0.67)), (cx_ - 9, Y(0.48)), (cx_ + 9, Y(0.48)), (cx_ + 9, Y(0.67))])}" fill="#4A3E36"/>')
        town.append(f'<path d="{pd([(cx_ - 11, Y(0.48)), (cx_, Y(0.38)), (cx_ + 11, Y(0.48))])}" fill="#3A4A5A"/>')
    town.append(f'<path d="{pd([(rx_ - 8, Y(0.67)), (rx_ - 8, Y(0.54)), (rx_ + 8, Y(0.54)), (rx_ + 8, Y(0.67))])}" fill="#5A4A3E"/>')
    # sunlight on some roofs: Vermeer's pointillé
    for k in range(120):
        x, y = X(rnd.uniform(0, 1)), Y(rnd.uniform(0.5, 0.66))
        town.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 1.3):.1f}" fill="{rnd.choice(["#FFF0C0", "#F6D890", "#E8A870"])}" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>')
    paint.append("".join(town))
    # quay wall and the bridge
    paint.append(f'<path d="{pd(UV([(-0.02, 0.66), (1.02, 0.665), (1.02, 0.69), (-0.02, 0.69)]))}" fill="#4A3E30"/>')
    paint.append(f'<path d="M{X(0.5):.1f} {Y(0.69):.1f}q20 -10 40 0" stroke="#3A2E24" stroke-width="4" fill="none"/>')
    # water: the still harbour with long vertical reflections
    water = UV([(-0.02, 0.69), (1.02, 0.69), (1.02, 0.9), (-0.02, 0.92)])
    paint.append(f'<path d="{pd(water)}" fill="{D.lin([(0, "#4A4236"), (0.35, "#6A6658"), (0.6, "#9AA8AC"), (1, "#6A787C")])}"/>')
    # reflections: the town's dark mass, the gates and the sunlit tower, softly broken
    for k in range(70):
        x = X(rnd.uniform(0, 1))
        paint.append(soft(D, x, Y(0.73), rnd.uniform(4, 10), H * rnd.uniform(0.03, 0.06), rnd.choice(["#2A2218", "#3A3024", "#5A3A2A"]), 0.5))
    for gx_, col in ((X(0.3), "#5A4A3A"), (X(0.82) - 16, "#3A3028"), (X(0.82) + 16, "#3A3028"), (X(0.7), "#C8B888")):
        paint.append(soft(D, gx_, Y(0.76), 9, H * 0.07, col, 0.7))
    B = Brush()
    for k in range(160):
        y = Y(rnd.uniform(0.7, 0.9))
        x = X(rnd.uniform(0, 1))
        L = rnd.uniform(8, 26)
        B.dash([(x - L / 2, y), (x + L / 2, y)], rnd.choice(["#C8D4D4", "#A8B8BC", "#E0E4DC", "#7A8A8E"]), rnd.uniform(1, 1.8), 0.55)
    paint.append(B.render())
    # two herring busses moored on the right, dark hulls with Vermeer's beads of light
    for k, (u, v, s_) in enumerate([(0.78, 0.8, 1.0), (0.9, 0.78, 0.8)]):
        bx, by = X(u), Y(v)
        hull = [(bx - 40 * s_, by - 8 * s_), (bx + 36 * s_, by - 12 * s_), (bx + 40 * s_, by - 2 * s_), (bx + 30 * s_, by + 6 * s_), (bx - 34 * s_, by + 6 * s_)]
        paint.append(f'<path d="{smooth_closed(hull)}" fill="#1E1A16"/>')
        paint.append(f'<path d="M{bx - 2 * s_:.1f} {by - 10 * s_:.1f}V{by - 60 * s_:.1f}" stroke="#2A2420" stroke-width="{2.4 * s_:.1f}"/>')
        for j in range(8):
            paint.append(f'<circle cx="{bx + rnd.uniform(-34, 34) * s_:.1f}" cy="{by + rnd.uniform(-10, 2) * s_:.1f}" r="{rnd.uniform(0.7, 1.2):.1f}" fill="#F2E8C8"/>')
        paint.append(f'<path d="{smooth_closed([(x, 2 * by - y + 4) for x, y in hull])}" fill="#2A2420" opacity="0.4"/>')
    # sandy foreground quay with a few townsfolk
    quay = UV([(-0.02, 0.9), (0.35, 0.89), (0.62, 0.92), (1.02, 0.96), (1.02, 1.02), (-0.02, 1.02)])
    paint.append(f'<path d="{smooth_closed(quay)}" fill="{D.lin([(0, "#C8A878"), (1, "#8A6A44")])}"/>')
    from figures import person
    for k, (u, h, pal) in enumerate([(0.14, 26, {"top": "#2A2A30", "top_kind": "coat", "bottom_kind": "skirt", "bottom": "#1E1E24", "hat_kind": None, "hair": "#E8E4D8", "hair_style": "bun"}),
                                    (0.18, 25, {"top": "#3A2A20", "top_kind": "coat", "bottom_kind": "skirt", "bottom": "#2A2A6A", "hat_kind": None, "hair": "#F2F0E8", "hair_style": "bun"}),
                                    (0.3, 23, {"top": "#2A2A30", "top_kind": "coat", "bottom_kind": "trousers", "bottom": "#1E1A18", "hat_kind": "cowboy", "hat": "#1A1614"})]):
        paint.append(person(X(u), Y(0.935), h, "stand_34" if k < 2 else "stand_side", 1 if k != 1 else -1, {**pal, "skin": "#E8C4A0"}, seed=80 + k, light=-1, shadow=0.2))
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.05)}{varnish(D, box, 0.1, 0.22, 8, 0.4)}</g>')
    out.append(museum_label(D, 500, "View of Delft", "JOHANNES VERMEER · c. 1661", "#F2EADA", "#C8BCA2", ts=30, bs=17, gap=27))
    return finish(D, out, 73)


# ================================================================ 19. A Sunday on La Grande Jatte — Seurat, 1886
def closed_curve(pts, n=6):
    """Dense polygon along the closed Catmull-Rom curve through pts (for point tests that match smooth_closed)."""
    out = []
    m = len(pts)
    for i in range(m):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % m], pts[(i + 2) % m]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    return out


def dotfill(pts, base, colfn, seed, dens=0.8, r=(1.05, 1.5), smooth=True, base_op=1.0, test=None):
    """Seurat's touch: a flat ground of the local colour, then pure dots of colour laid side by side inside the shape.
    Dots are written compactly as zero-length round-capped strokes, grouped by colour and size."""
    rnd = random.Random(seed)
    poly = closed_curve(pts) if smooth else pts
    d = smooth_closed(pts) if smooth else pd(pts)
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    bx0, by0, bx1, by1 = min(xs), min(ys), max(xs), max(ys)
    area = 0.0
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        area += ax * by - bx * ay
    area = abs(area) / 2
    rm = (r[0] + r[1]) / 2
    n = int(area * dens / (math.pi * rm * rm)) + 2
    groups = {}
    k = tries = 0
    while k < n and tries < n * 8:
        tries += 1
        x, y = rnd.uniform(bx0, bx1), rnd.uniform(by0, by1)
        if not inside((x, y), poly) or (test and not test(x, y)):
            continue
        k += 1
        c = colfn(x, y, rnd)
        rr = round(rnd.uniform(*r) * 4) / 4
        groups.setdefault((c, rr), []).append(f"M{x:.1f} {y:.1f}h0")
    out = [f'<path d="{d}" fill="{base}"{f" opacity={chr(34)}{base_op}{chr(34)}" if base_op < 1 else ""}/>'] if base else []
    for (c, rr), segs in groups.items():
        out.append(f'<path d="{"".join(segs)}" stroke="{c}" stroke-width="{rr * 2:.1f}" stroke-linecap="round" fill="none"/>')
    return "".join(out)


def palette(*items):
    """Weighted colour palette -> colfn."""
    items = [(w, c) for w, c in items]
    return lambda x, y, rnd: wpick(rnd, items)


def lit_pal(dark_items, lit_items, fn):
    """Choose between a shadow and a light palette by fn(x, y) in 0..1 (probability of light)."""
    return lambda x, y, rnd: wpick(rnd, lit_items if rnd.random() < fn(x, y) else dark_items)


@design("sunday-on-la-grande-jatte")
def grande_jatte():
    D = Doc("gmgj")
    box = (60, 84, 540, 407)   # 480 x 323 (207.5 x 308 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [mat_board(D, (x0 - 14, y0 - 14, x1 + 14, y1 + 14), 6, "#EDE6D6", 161)]
    out.append(simple_frame(D, (x0 - 8, y0 - 8, x1 + 8, y1 + 8), 8, ("#FFFFFF", "#EDEAE2", "#B8B2A4"), 3))
    # Seurat's own painted border of dots, complementary to the scene it touches
    border = (x0 - 8, y0 - 8, x1 + 8, y1 + 8)
    bring = [(border[0], border[1]), (border[2], border[1]), (border[2], border[3]), (border[0], border[3])]
    out.append(f'<path d="M{border[0]} {border[1]}H{border[2]}V{border[3]}H{border[0]}Z M{x0} {y0}V{y1}H{x1}V{y0}Z" fill="#34407A" fill-rule="evenodd"/>')
    out.append(dotfill(bring, None, lambda x, y, rnd: rnd.choice(["#E8823A", "#2A3A8A", "#F2C040", "#3A5AB8", "#C8502A", "#1E2A6A"])
                       if (x0 <= x <= x1 and y0 <= y <= y1) is False else "#000", 3, 1.6, (0.9, 1.25), False,
                       test=lambda x, y: not (x0 <= x <= x1 and y0 <= y <= y1)))
    cp = clip_box(D, box)
    P = []   # paint layers in order

    # ---- palettes
    SUN = palette((5, "#D6D65C"), (4, "#B8CC52"), (3, "#E8D070"), (3, "#9ABE48"), (2, "#F2E89A"), (1.2, "#E8A050"), (0.8, "#7AA0C8"), (0.6, "#6AA040"))
    SUN_FAR = palette((5, "#D8DC8A"), (4, "#C8D474"), (3, "#EEE6A8"), (2, "#B8CC88"), (1, "#E8B878"), (1, "#A8C0D0"))
    SHADE = palette((5, "#1E5A44"), (4, "#2A6A48"), (3, "#2E3E86"), (2.4, "#4A3A80"), (2, "#3A7A4A"), (1, "#E8823A"), (0.8, "#8AB040"), (0.6, "#1A2A5A"))
    RIVER = palette((5, "#5A8CCC"), (4, "#7EAEDE"), (3, "#3E68B4"), (2, "#B4D2EA"), (1.4, "#EEE2B8"), (1, "#F2B078"), (0.8, "#2E4E9A"))
    SKY = palette((5, "#EEF0DC"), (3, "#CCDCE4"), (3, "#F4E6BE"), (2, "#B8D0DC"), (1, "#F6D4A8"))
    CANOPY = palette((5, "#21402C"), (4, "#2E5A34"), (3, "#3A6A3A"), (2, "#33407A"), (1.5, "#5A8A3A"), (0.6, "#E8A040"), (0.7, "#1A2A40"))
    BANK = palette((4, "#6A8A62"), (3, "#8AA078"), (2, "#9AA8C0"), (2, "#B8C49A"), (1, "#E8C890"))
    DARK = palette((5, "#1C1C34"), (4, "#28284A"), (3, "#352650"), (2, "#14142A"), (1, "#4A3A6A"), (0.3, "#E8823A"), (0.6, "#2A4A7A"))
    SKIN = palette((5, "#EAB88E"), (3, "#F2CCA0"), (2, "#D89A72"), (1, "#E88A6A"), (0.6, "#A8B8D8"))
    TRUNK = palette((5, "#3E3428"), (3, "#2A2A40"), (3, "#5A4430"), (2, "#7A5A34"), (1, "#3A4A7A"), (0.6, "#E8A050"))

    # ---- sky and the far bank of the Seine, glimpsed at the upper left
    P.append(dotfill(UV([(-0.02, -0.02), (0.6, -0.02), (0.6, 0.12), (-0.02, 0.12)]), "#DCE4D2", SKY, 1, 0.9, smooth=False))
    P.append(dotfill(UV([(-0.02, 0.07), (0.08, 0.06), (0.14, 0.075), (0.22, 0.058), (0.3, 0.07), (0.4, 0.062), (0.5, 0.075), (0.5, 0.14), (-0.02, 0.14)]),
                     "#7E9A72", BANK, 2, 0.9, smooth=False))
    # far houses on the bank
    for k, (u, w_) in enumerate([(0.04, 0.03), (0.17, 0.025), (0.33, 0.035)]):
        P.append(dotfill(UV([(u, 0.09), (u, 0.075), (u + w_, 0.075), (u + w_, 0.09)]), "#E8DCC0",
                         palette((4, "#F2E8D0"), (2, "#E8C8A0"), (1, "#C8A8B8")), 210 + k, 0.9, (0.9, 1.2), False))
    # ---- the river
    river = UV([(-0.02, 0.12), (0.5, 0.12), (0.44, 0.17), (0.36, 0.24), (0.27, 0.32), (0.17, 0.4), (0.08, 0.46), (-0.02, 0.5)])
    P.append(dotfill(river, "#6A98CA", RIVER, 3, 0.95, smooth=False))
    # boats: a sailboat, a steamer trailing smoke, a racing scull and its oarsmen
    sb = [(0.075, 0.26), (0.105, 0.155), (0.13, 0.26)]
    P.append(dotfill(UV(sb), "#F6F2E4", palette((5, "#FFFFFF"), (3, "#F2E8C8"), (1, "#C8D4E8"), (0.5, "#F2C890")), 4, 1.1, (0.8, 1.1), False))
    P.append(dotfill(UV([(0.06, 0.262), (0.145, 0.262), (0.135, 0.275), (0.07, 0.275)]), "#3A2E40", DARK, 5, 1.0, (0.8, 1.1), False))
    P.append(f'<path d="M{X(0.103):.1f} {Y(0.15):.1f}V{Y(0.262):.1f}" stroke="#3A2E2A" stroke-width="1.2"/>')
    st = UV([(0.24, 0.155), (0.33, 0.155), (0.325, 0.167), (0.245, 0.167)])
    P.append(dotfill(st, "#E8DCC8", palette((3, "#F2E8D0"), (2, "#3A3A5A"), (1, "#C8A080")), 6, 1.0, (0.8, 1.1), False))
    P.append(dotfill(UV([(0.265, 0.155), (0.265, 0.13), (0.275, 0.13), (0.275, 0.155)]), "#2A2A3A", DARK, 7, 1.0, (0.7, 1.0), False))
    P.append(dotfill(UV([(0.268, 0.13), (0.29, 0.1), (0.33, 0.09), (0.36, 0.1), (0.32, 0.115), (0.285, 0.128)]), None,
                     palette((3, "#D8D4CC"), (2, "#B8B4BC"), (1, "#F2F0E8")), 8, 0.7, (0.9, 1.3)))
    scull = UV([(0.14, 0.348), (0.3, 0.325), (0.302, 0.332), (0.145, 0.356)])
    P.append(dotfill(scull, "#E8C890", palette((3, "#F2D8A0"), (2, "#C89060"), (1, "#3A3A5A")), 9, 1.1, (0.8, 1.0), False))
    for j in range(6):
        u = 0.165 + j * 0.022
        v = 0.343 - j * 0.0035
        P.append(dotfill(UV([(u - 0.006, v), (u - 0.004, v - 0.032), (u + 0.004, v - 0.032), (u + 0.006, v)]), "#F2EEE4",
                         palette((3, "#FFFFFF"), (1, "#E8823A")), 20 + j, 1.0, (0.7, 0.9), False))
        P.append(f'<circle cx="{X(u):.1f}" cy="{Y(v - 0.038):.1f}" r="2.1" fill="#C8845A"/>')
        P.append(f'<path d="M{X(u - 0.03):.1f} {Y(v + 0.02):.1f}L{X(u + 0.012):.1f} {Y(v - 0.016):.1f}" stroke="#7A5A3A" stroke-width="0.9"/>')

    # ---- the lawn: far sunlit, middle sunlit band, deep shade in front and to the right
    lawn = UV([(0.5, 0.12), (1.02, 0.1), (1.02, 1.02), (-0.02, 1.02), (-0.02, 0.5), (0.08, 0.46), (0.17, 0.4), (0.27, 0.32), (0.36, 0.24), (0.44, 0.17)])
    P.append(dotfill(lawn, "#B4C25A", lambda x, y, rnd: SUN_FAR(x, y, rnd) if y < Y(0.3) and rnd.random() < (Y(0.3) - y) / (H * 0.18) else SUN(x, y, rnd),
                     10, 0.95, smooth=False))
    shade_front = UV([(-0.02, 0.58), (0.12, 0.6), (0.26, 0.64), (0.4, 0.69), (0.52, 0.7), (0.62, 0.64), (0.74, 0.6), (0.86, 0.56), (1.02, 0.52),
                      (1.02, 1.02), (-0.02, 1.02)])
    P.append(dotfill(shade_front, "#2C5A46", SHADE, 11, 1.0))
    shade_right = UV([(0.6, 0.1), (1.02, 0.08), (1.02, 0.56), (0.92, 0.52), (0.8, 0.44), (0.72, 0.34), (0.66, 0.22)])
    P.append(dotfill(shade_right, "#2E5E46", SHADE, 12, 1.0))
    # cast shadows of the trees across the sunlit middle, and sun breaking through into the shade
    for k, (u, v, rx, ry) in enumerate([(0.36, 0.44, 0.07, 0.025), (0.55, 0.38, 0.09, 0.03), (0.47, 0.27, 0.05, 0.018), (0.27, 0.5, 0.06, 0.02)]):
        P.append(dotfill(blob_pts(X(u), Y(v), W * rx, H * ry, 30 + k, 0.1, 14), None, SHADE, 31 + k, 1.6))
    for k, (u, v, rx, ry) in enumerate([(0.2, 0.8, 0.07, 0.022), (0.6, 0.86, 0.06, 0.02), (0.88, 0.66, 0.05, 0.02), (0.4, 0.95, 0.08, 0.02)]):
        P.append(dotfill(blob_pts(X(u), Y(v), W * rx, H * ry, 40 + k, 0.12, 14), None, palette((4, "#B8C850"), (3, "#E8B850"), (2, "#8ABA48"), (1, "#E8823A")), 41 + k, 1.4))

    # ---- trees: tall trunks rising into a dark canopy along the top
    for k, (u, v_, w_) in enumerate([(0.255, 0.5, 0.016), (0.44, 0.36, 0.011), (0.58, 0.4, 0.013), (0.735, 0.38, 0.016), (0.965, 0.6, 0.028), (0.66, 0.3, 0.008)]):
        tw = W * w_
        tr = [(X(u) - tw / 2, Y(v_)), (X(u) - tw * 0.4, y0 - 4), (X(u) + tw * 0.4 + 2, y0 - 4), (X(u) + tw / 2, Y(v_))]
        P.append(dotfill(tr, "#3A3228", TRUNK, 50 + k, 1.05, (0.9, 1.25), False))
        P.append(dotfill([(X(u) - tw / 2, Y(v_)), (X(u) - tw * 0.4, y0 - 4), (X(u) - tw * 0.1, y0 - 4), (X(u) - tw * 0.15, Y(v_))], None,
                         palette((3, "#C8A060"), (2, "#E8C070"), (1, "#8A6A40")), 56 + k, 0.6, (0.8, 1.1), False))
    canopy = UV([(0.22, -0.02), (1.02, -0.02), (1.02, 0.15), (0.94, 0.12), (0.88, 0.16), (0.8, 0.13), (0.74, 0.17), (0.66, 0.11), (0.58, 0.14),
                 (0.5, 0.09), (0.42, 0.075), (0.35, 0.05), (0.28, 0.04)])
    P.append(dotfill(canopy, "#2A4A32", CANOPY, 60, 1.0))
    for k, (u, v, rx, ry) in enumerate([(0.62, 0.16, 0.04, 0.03), (0.86, 0.18, 0.05, 0.03), (0.3, 0.06, 0.04, 0.025), (0.97, 0.2, 0.03, 0.04)]):
        P.append(dotfill(blob_pts(X(u), Y(v), W * rx, H * ry, 620 + k, 0.2, 12), "#2A4A32", CANOPY, 630 + k, 1.0))

    # ---- figure helpers
    def fig(pts, base, colfn, seed, dens=1.05, r=(0.8, 1.15)):
        return dotfill(pts, base, colfn, seed, dens, r)

    def placer(ox, oy, s, flip=1):
        return lambda pts: [(ox + px * s * flip, oy + py * s) for px, py in pts]

    def cast_sh(cx, cy, rx, ry, seed):
        return dotfill(blob_pts(cx, cy, rx, ry, seed, 0.08, 12), None, palette((4, "#2A5A44"), (3, "#2E3E86"), (2, "#4A3A80")), seed, 0.9)

    # background strollers: a couple under a parasol, two soldiers, a nurse, a lady seated under a tree
    def small_person(u, v, h, dress, seed, parasol=None, hat="#1E1E34", flip=1, kind="dress"):
        T = placer(X(u), Y(v), h / 100, flip)
        o = []
        if kind == "dress":
            body = [(-5, 100), (-4, 70), (-3, 40), (-4, 28), (-2, 20), (3, 20), (4, 30), (6, 40), (9, 46), (8, 70), (9, 100)]
        else:
            body = [(-5, 100), (-4.5, 60), (-5, 28), (-3, 20), (3, 20), (5, 28), (4.5, 60), (5, 100)]
        o.append(fig(T(body), dress if isinstance(dress, str) else "#2A2A44", DARK if dress == "#1E1E34" else palette((4, dress), (2, dk(dress, 0.3)), (1, "#3A3A6A"), (1, lt(dress, 0.3))), seed, 1.1, (0.7, 0.95)))
        o.append(fig(T([(-3, 20), (-3.5, 12), (0, 8), (3, 11), (2.5, 20)]), "#E8B890", SKIN, seed + 1, 1.1, (0.6, 0.8)))
        o.append(fig(T([(-5, 10), (-3, 4), (3, 4), (5, 10)]), hat, DARK, seed + 2, 1.1, (0.6, 0.8)))
        if parasol:
            o.append(fig(T([(-16, 0), (-8, -9), (4, -11), (14, -4), (16, 0), (0, -3)]), parasol, palette((4, parasol), (2, lt(parasol, 0.3)), (1, dk(parasol, 0.3))), seed + 3, 1.1, (0.7, 0.95)))
            o.append(f'<path d="{pd(T([(0, -3), (-1, 30)]), False)}" stroke="#2A2030" stroke-width="1"/>')
        return "".join(o)
    P.append(small_person(0.355, 0.36, 34, "#1E1E34", 70, parasol="#E8823A"))
    P.append(small_person(0.385, 0.365, 38, "#1E1E34", 72, hat="#1E1E34", kind="coat"))
    for j, u in enumerate((0.61, 0.632)):
        P.append(small_person(u, 0.345, 30, "#2A3A7A", 74 + j * 3, hat="#C83A2A", kind="coat"))
        P.append(fig(placer(X(u), Y(0.345), 0.3)([(-4.5, 60), (-4.5, 100), (4.5, 100), (4.5, 60)]), "#C83A2A", palette((4, "#D8483A"), (2, "#E8823A"), (1, "#7A2A4A")), 80 + j, 1.1, (0.6, 0.8)))
    # nurse seated, seen from behind: white bonnet, red shawl
    nx_, ny_ = X(0.43), Y(0.56)
    P.append(cast_sh(nx_ + 10, ny_ + 2, 16, 3.5, 82))
    P.append(fig([(nx_ - 12, ny_), (nx_ - 9, ny_ - 12), (nx_ - 6, ny_ - 22), (nx_ + 1, ny_ - 25), (nx_ + 7, ny_ - 20), (nx_ + 10, ny_ - 10), (nx_ + 13, ny_)], "#1E1E34", DARK, 83))
    P.append(fig([(nx_ - 6, ny_ - 20), (nx_ - 2, ny_ - 25), (nx_ + 6, ny_ - 23), (nx_ + 9, ny_ - 14), (nx_ + 1, ny_ - 12)], "#C83A2A", palette((4, "#D8483A"), (2, "#E8823A"), (1, "#8A2A5A")), 84, 1.1, (0.7, 0.9)))
    P.append(fig([(nx_ - 4, ny_ - 25), (nx_ - 3, ny_ - 32), (nx_ + 3, ny_ - 33), (nx_ + 5, ny_ - 26)], "#F6F2EA", palette((4, "#FFFFFF"), (2, "#E8E4F0"), (1, "#F2D8A8")), 85, 1.1, (0.7, 0.9)))
    # lady seated under the tree at the right with an orange parasol
    lx_, ly_ = X(0.665), Y(0.5)
    P.append(fig([(lx_ - 14, ly_), (lx_ - 8, ly_ - 10), (lx_ - 3, ly_ - 22), (lx_ + 3, ly_ - 22), (lx_ + 6, ly_ - 10), (lx_ + 14, ly_)], "#2A2A4A", DARK, 86, 1.05, (0.7, 0.95)))
    P.append(fig([(lx_ - 3, ly_ - 22), (lx_ - 3, ly_ - 29), (lx_ + 3, ly_ - 30), (lx_ + 3, ly_ - 22)], "#E8B890", SKIN, 87, 1.1, (0.6, 0.8)))
    P.append(fig([(lx_ - 20, ly_ - 30), (lx_ - 6, ly_ - 44), (lx_ + 8, ly_ - 40), (lx_ + 14, ly_ - 28), (lx_ - 2, ly_ - 33)], "#E8823A", palette((4, "#F2903A"), (2, "#E8B060"), (1, "#C8502A")), 88, 1.1, (0.7, 0.95)))

    # ---- the girl in white and her mother, walking toward us in the full sun
    gx_, gy_ = X(0.505), Y(0.63)
    P.append(cast_sh(gx_ + 16, gy_ + 1, 22, 4, 90))
    M = placer(X(0.535), Y(0.635), 0.6)
    mother = [(-8, 0), (-7, -22), (-6, -40), (-5, -50), (-6, -62), (-3, -70), (3, -70), (6, -62), (5, -50), (8, -40), (10, -22), (11, 0)]
    P.append(fig(M(mother), "#C8603A", palette((4, "#D86A3A"), (3, "#E8904A"), (2, "#A84A5A"), (1, "#F2C070"), (1, "#5A4A8A")), 91, 1.1, (0.8, 1.05)))
    P.append(fig(M([(-3, -70), (-4, -78), (0, -83), (4, -79), (3, -70)]), "#E8B890", SKIN, 92, 1.1, (0.6, 0.8)))
    P.append(fig(M([(-5, -80), (-3, -86), (3, -86), (6, -81)]), "#1E1E34", DARK, 93, 1.1, (0.6, 0.8)))
    P.append(fig(M([(-26, -86), (-14, -100), (2, -104), (18, -98), (26, -86), (0, -90)]), "#F2E8C8", palette((4, "#FFF6E0"), (3, "#F2D8A8"), (1, "#E8A070"), (1, "#C8C8E8")), 94, 1.1, (0.8, 1.05)))
    P.append(f'<path d="{pd(M([(1, -90), (-1, -55)]), False)}" stroke="#3A2A2A" stroke-width="1.2"/>')
    G = placer(gx_, gy_, 0.42)
    girl = [(-9, 0), (-10, -18), (-8, -38), (-5, -48), (5, -48), (8, -38), (10, -18), (9, 0)]
    P.append(fig(G(girl), "#F6F4EE", lit_pal([(3, "#C8D0EC"), (2, "#B8C0E0"), (1, "#E8D8F0")], [(5, "#FFFFFF"), (3, "#F6EED8"), (1, "#F2D8A8")],
                                              lambda x, y: 0.75 if x < gx_ else 0.35), 95, 1.15, (0.8, 1.05)))
    P.append(fig(G([(-3, -48), (-4, -58), (0, -62), (4, -58), (3, -48)]), "#E8B890", SKIN, 96, 1.1, (0.6, 0.8)))
    P.append(fig(G([(-8, -57), (-5, -64), (5, -64), (8, -57), (0, -59)]), "#F6F2EA", palette((3, "#FFFFFF"), (1, "#E8823A")), 97, 1.1, (0.6, 0.8)))
    P.append(fig(G([(-7, 0), (-5, 6), (-2, 6), (-1, 0)]) + G([(1, 0), (2, 6), (5, 6), (7, 0)]), None, DARK, 98, 0.6, (0.6, 0.8)))

    # a little girl in orange running in the sun, and a woman fishing at the water's edge
    R = placer(X(0.4), Y(0.53), 0.36)
    P.append(fig(R([(-9, 0), (-4, -14), (-8, -30), (-4, -44), (4, -44), (8, -30), (6, -14), (12, -2), (6, 0)]), "#E8703A", palette((4, "#F2803A"), (2, "#E8A050"), (1, "#C8402A")), 99, 1.1, (0.7, 0.9)))
    P.append(fig(R([(-3, -44), (-3, -52), (3, -53), (3, -44)]), "#E8B890", SKIN, 100, 1.1, (0.6, 0.8)))
    F = placer(X(0.19), Y(0.47), 0.5)
    P.append(fig(F([(-6, 0), (-5, -30), (-4, -50), (-6, -60), (-3, -68), (3, -68), (5, -58), (7, -46), (14, -36), (13, -20), (12, 0)]), "#D86A5A",
                 palette((4, "#E07060"), (3, "#C8505A"), (2, "#E8A070"), (1, "#5A4A9A")), 101, 1.1, (0.7, 0.95)))
    P.append(fig(F([(-3, -68), (-4, -76), (0, -80), (3, -76), (3, -68)]), "#E8B890", SKIN, 102, 1.1, (0.6, 0.8)))
    P.append(fig(F([(-6, -76), (-2, -82), (4, -81), (7, -77)]), "#2A2A44", DARK, 103, 1.1, (0.6, 0.8)))
    P.append(f'<path d="{pd(F([(-5, -56), (-40, -100), (-62, -96)]), False)}" stroke="#3A2A20" stroke-width="1" fill="none"/>')

    # ---- the left foreground group in deep shade: a gentleman seated in a top hat, a woman with a fan, the reclining boatman
    S1 = placer(X(0.035), Y(0.66), 0.75)
    P.append(fig(S1([(-2, -14), (14, -16), (30, -10), (46, -5), (48, 0), (30, 0), (10, -2)]), "#4A4A6A", palette((4, "#5A5A7A"), (3, "#3A3A5A"), (1, "#E8823A"), (1, "#8A8AAA")), 103))
    P.append(fig(S1([(-10, 0), (-9, -24), (-10, -42), (-6, -50), (6, -50), (10, -36), (12, -18), (2, -10), (-2, 0)]), "#1E1E34", DARK, 104))
    P.append(fig(S1([(-5, -50), (-5, -60), (0, -64), (5, -61), (6, -50)]), "#E8B890", SKIN, 105, 1.1, (0.7, 0.9)))
    P.append(fig(S1([(-7, -62), (-6, -80), (5, -80), (6, -62), (9, -62), (9, -60), (-10, -60), (-10, -62)]), "#141428", DARK, 106))
    P.append(f'<path d="{pd(S1([(10, -30), (30, 2)]), False)}" stroke="#E8C890" stroke-width="1.5"/>')
    S2 = placer(X(0.135), Y(0.69), 0.78)
    woman_s = [(-18, 0), (-14, -12), (-8, -20), (-6, -36), (-7, -46), (-4, -54), (3, -54), (6, -44), (4, -32), (8, -22), (20, -14), (28, -4), (26, 0)]
    P.append(fig(S2(woman_s), "#3A2A5A", palette((4, "#3A2A60"), (3, "#4A3A80"), (2, "#2A2A4A"), (1, "#C8503A"), (1, "#7A5AA8")), 107))
    P.append(fig(S2([(-4, -54), (-5, -62), (-1, -67), (4, -64), (4, -54)]), "#E8B890", SKIN, 108, 1.1, (0.7, 0.9)))
    P.append(fig(S2([(-8, -62), (-4, -70), (5, -70), (10, -64), (2, -63)]), "#C8402A", palette((3, "#D84A2A"), (2, "#F2C040"), (1, "#2A2A4A")), 109, 1.1, (0.7, 0.9)))
    P.append(fig(S2([(6, -42), (12, -50), (18, -44), (12, -38)]), "#F2C040", palette((3, "#F2C850"), (2, "#E8823A"), (1, "#FFFFFF")), 110, 1.1, (0.6, 0.8)))
    # the boatman lying on his side, propped on an elbow, cap and pipe
    B_ = placer(X(0.12), Y(0.82), 1.0)
    P.append(cast_sh(X(0.22), Y(0.825), 52, 5, 111))
    trousers = [(4, -1), (5, -6), (10, -8), (26, -9), (40, -13), (52, -20), (58, -16), (56, -2), (36, -1), (16, -1)]
    P.append(fig(B_(trousers), "#1E1E3C", DARK, 112))
    knee = [(54, -18), (44, -28), (36, -36), (30, -34), (24, -14), (20, -4), (12, -3), (12, 0), (26, 0), (32, -18), (36, -24), (46, -12), (56, -6)]
    P.append(fig(B_(knee), "#2A2A50", lit_pal([(5, "#232344"), (3, "#2A2A50"), (1, "#E8823A")], [(3, "#3A3A7A"), (2, "#4A4A8A"), (1, "#E8A050")],
                                                lambda x, y: 0.5 if y < B_([(0, -20)])[0][1] else 0.15), 119))
    shirt = [(50, -18), (56, -24), (64, -32), (72, -38), (80, -40), (85, -36), (84, -28), (78, -18), (70, -8), (60, -3), (54, -6)]
    P.append(fig(B_(shirt), "#E8C8A8", lit_pal([(3, "#C89A80"), (2, "#8A86B8"), (1, "#E8823A")], [(4, "#F2D8B8"), (3, "#F6E8D0"), (1, "#F2B078")],
                                                  lambda x, y: 0.6), 113))
    P.append(fig(B_([(77, -32), (83, -37), (88, -20), (90, -8), (100, -6), (102, -1), (84, -1), (80, -12)]), "#D89A78", SKIN, 114))
    P.append(fig(B_([(80, -42), (80, -49), (85, -54), (91, -52), (93, -46), (90, -40)]), "#E0A880", SKIN, 115, 1.1, (0.7, 0.9)))
    P.append(fig(B_([(78, -50), (83, -57), (91, -57), (97, -52), (91, -51)]), "#1E1E34", DARK, 116, 1.1, (0.7, 0.9)))
    P.append(f'<path d="{pd(B_([(92, -45), (100, -42)]), False)}" stroke="#2A1A14" stroke-width="1.6"/><path d="{pd(B_([(100, -44), (100, -40)]), False)}" stroke="#2A1A14" stroke-width="2.6"/>')

    # the black dog nosing through the grass, and a little pug near the couple
    dg = placer(X(0.37), Y(0.875), 1.25, -1)
    dog_b = [(-16, -13), (-10, -16), (0, -16), (8, -15), (12, -13), (16, -10), (19, -6), (22, -3), (20, -1), (16, -4), (12, -7), (11, -1), (13, 0),
             (9, 0), (8, -6), (-5, -8), (-7, -1), (-5, 0), (-9, 0), (-10, -7), (-13, -9), (-17, -18), (-19, -23), (-17, -22), (-15, -15)]
    P.append(fig(dg(dog_b), "#141420", DARK, 117, 1.1, (0.7, 0.95)))
    pg = placer(X(0.555), Y(0.925), 0.55)
    P.append(fig(pg([(-12, -10), (-6, -14), (6, -14), (11, -16), (15, -12), (12, -8), (9, -7), (9, 0), (6, 0), (5, -6), (-6, -6), (-7, 0), (-10, 0), (-10, -6), (-14, -12)]),
                 "#C88A4A", palette((4, "#D8984A"), (2, "#E8B060"), (2, "#8A5A3A"), (1, "#3A3A6A")), 118, 1.1, (0.7, 0.9)))

    # ---- the couple at the right: the lady with her great bustle, parasol and monkey; the gentleman in his top hat
    s_ = H * 0.62 / 100
    MN = placer(X(0.905), Y(0.97), s_)
    P.append(fig(MN([(-6, -34), (-6.5, 3), (-1.5, 3), (0.5, -24), (2.5, 3), (7.5, 3), (7, -34)]), "#14142A", DARK, 120))
    man_coat = [(-6, -74), (-2, -76), (5, -76), (8, -72), (9, -62), (9.5, -45), (11, -32), (2, -33), (-7, -34), (-8, -45), (-8.5, -60), (-8, -68)]
    P.append(fig(MN(man_coat), "#121226", palette((5, "#121226"), (4, "#1C1C34"), (2, "#2A2244"), (1, "#3A2A5A"), (0.25, "#E8823A")), 121))
    P.append(fig(MN([(4, -86), (-4, -86), (-5, -83.5), (-7, -81.5), (-5.2, -80.5), (-5.6, -78.5), (-4.5, -76.5), (-1, -75.5), (4, -76), (5.5, -80)]), "#E0AA80", SKIN, 122, 1.15, (0.6, 0.85)))
    P.append(fig(MN([(-5, -101), (5, -101), (5.5, -88), (8.5, -87.5), (8.5, -86), (-8.5, -86), (-8.5, -87.5), (-5.5, -88)]), "#0E0E1E", DARK, 123, 1.1, (0.7, 0.9)))
    P.append(f'<path d="{pd(MN([(-5, -79.5), (-11, -78.2)]), False)}" stroke="#5A3A2A" stroke-width="1.8"/><circle cx="{MN([(-11.2, -78.2)])[0][0]:.1f}" cy="{MN([(-11.2, -78.2)])[0][1]:.1f}" r="1.1" fill="#E8823A"/>')
    P.append(f'<path d="{pd(MN([(-4, -75.5), (1, -74.5), (5, -75.5)]), False)}" stroke="#F2F0E8" stroke-width="1.8"/>')
    P.append(fig(MN([(-1, -72), (-6, -62), (-10, -50), (-8, -47.5), (-4, -58), (2, -66)]), "#1A1A30", DARK, 124))
    P.append(f'<path d="{pd(MN([(-9.5, -48.5), (-14, 3)]), False)}" stroke="#3A2A3A" stroke-width="1.6"/>')
    WM = placer(X(0.765), Y(0.985), s_)
    dress = [(-2.5, -79), (-6, -75.5), (-7.5, -71), (-6.5, -66), (-5, -62), (-6.5, -50), (-8.5, -30), (-10.5, -10), (-11, 0), (13, 0), (14, -20),
             (15, -34), (17, -40), (23, -44), (27, -48), (26, -52), (20, -56), (10, -60), (4, -62), (4.5, -70), (4, -76), (2, -80)]
    by_ = WM([(0, -50)])[0][1]
    bx_ = WM([(8, 0)])[0][0]
    P.append(fig(WM(dress), "#1E1E40", lit_pal([(5, "#1C1C38"), (4, "#28284E"), (3, "#352656"), (2, "#16162E"), (0.3, "#E8823A")],
                                                [(4, "#4A4A8E"), (3, "#5A4A9E"), (2, "#6A5AAA"), (0.8, "#E8903A"), (1, "#3A6AAA")],
                                                lambda x, y: (0.75 if y < by_ else 0.25) if x > bx_ else 0.1), 125))
    # head in profile, hair up in a bun, a small hat with flowers
    P.append(fig(WM([(4, -79), (2, -83), (-3.5, -84), (-4.5, -86.5), (-6, -88.5), (-4.6, -89.5), (-5, -91), (-3.5, -93.5), (0, -95), (4, -94.5), (6, -90), (5.5, -84)]),
                 "#E4AE84", SKIN, 126, 1.15, (0.6, 0.85)))
    P.append(fig(WM([(1, -93), (4, -96), (8, -94), (9, -89), (6, -86), (4, -89)]), "#2A1E2A", DARK, 127, 1.1, (0.6, 0.8)))
    P.append(fig(WM([(-3, -95), (0, -99), (6, -99.5), (9, -97), (6, -95)]), "#1C1C34", DARK, 128, 1.1, (0.6, 0.8)))
    P.append(fig(WM([(1, -99), (3, -102.5), (6.5, -101.5), (5.5, -99)]), "#D8483A", palette((3, "#E8503A"), (1, "#F2C040")), 129, 1.1, (0.6, 0.8)))
    # her arm, and the dark parasol open over her shoulder
    P.append(fig(WM([(1, -77), (-1, -69), (-6, -64), (-8, -66.5), (-4, -72), (-2, -79)]), "#22224A", DARK, 130))
    P.append(f'<path d="{pd(WM([(-7, -65.5), (5, -119)]), False)}" stroke="#2A2030" stroke-width="1.4"/>')
    para = [(-12, -106), (-4, -116), (8, -120), (20, -116), (26, -108), (15, -109.5), (7, -107.5), (-2, -108.5)]
    pt_ = WM([(0, -114)])[0][1]
    P.append(fig(WM(para), "#1C1C38", lit_pal([(5, "#1C1C38"), (3, "#2A2A50"), (1, "#E8823A")], [(3, "#4A3A8A"), (2, "#E8A050"), (2, "#3A4A9A")],
                                              lambda x, y: 0.45 if y < pt_ else 0.12), 131))
    for rx_ in (-6, 5, 15):
        P.append(f'<path d="{pd(WM([(7, -119), (rx_ + 2, -108)]), False)}" stroke="#4A3A7A" stroke-width="0.9" opacity="0.8"/>')
    # the leash and the monkey, tail curled high
    hand = WM([(-8, -66)])[0]
    mkx, mky = WM([(-27, 0)])[0]
    mk = placer(mkx, mky, 1.35)
    collar = mk([(9, -15)])[0]
    P.append(f'<path d="M{hand[0]:.1f} {hand[1]:.1f}Q{collar[0] + 4:.1f} {collar[1] - 50:.1f} {collar[0]:.1f} {collar[1]:.1f}" stroke="#2A2030" stroke-width="1" fill="none"/>')
    monkey = [(-8, -9), (-4, -13), (3, -14), (8, -13), (10, -16), (13, -19), (17, -18), (18, -14), (15, -11), (13, -8), (13.5, 0), (11, 0), (10, -6),
              (3, -7), (1, -3), (2, 0), (-1, 0), (-2, -4), (-5, -4), (-6, 0), (-9, 0), (-8.5, -5)]
    P.append(fig(mk(monkey), "#1A1420", palette((4, "#1E1820"), (2, "#3A2A30"), (1.4, "#6A4030"), (1, "#2A2A4A")), 132, 1.15, (0.6, 0.85)))
    P.append(fig(mk([(14, -17), (16, -19.5), (18.5, -17.5), (17, -15)]), "#A87A5A", palette((3, "#C89070"), (1, "#E8B890")), 133, 1.1, (0.5, 0.7)))
    tail = mk([(-8, -9), (-15, -12), (-18, -22), (-14, -30), (-8, -29), (-7, -24), (-10, -23)])
    P.append(f'<path d="{smooth_open(tail)}" stroke="#1A1420" stroke-width="2.2" fill="none" stroke-linecap="round"/>')

    out.append(f'<g {cp}>{"".join(P)}{varnish(D, box, 0.08, 0.12, 6, 0.25)}</g>')
    out.append(museum_label(D, 472, "A Sunday on La Grande Jatte", "GEORGES SEURAT · 1886", "#2A2A3A", "#5A5A6A", ts=29, bs=18, gap=30, max_w=450))
    return finish(D, out, 79)


# ================================================================ 20. Still Life with Apples — Cézanne, c. 1893
def hatch(B, region, n, colfn, seed, L=(8, 13), W=(3.4, 5), angle=-40, spread=8):
    """Cézanne's constructive stroke: short parallel patches laid side by side in one direction."""
    dabs(B, region, n, colfn, seed, L=L, W=W, angle=angle, spread=spread, op=(0.75, 1.0))


def cz_apple(D, B, cx, cy, r, seed, pal, light=(-0.6, -0.7)):
    """An apple built of planes of colour: warm where it turns to the light, cool violet in shadow, a blue contour."""
    rnd = random.Random(seed)
    pts = blob_pts(cx, cy, r, r * 0.92, seed, 0.05, 16)
    d = smooth_closed(pts)
    out = [f'<path d="{d}" fill="{pal[1]}"/>']

    def col(x, y, rr):
        t = ((x - cx) * light[0] + (y - cy) * light[1]) / r
        if t > 0.35:
            return rr.choice([pal[0], lt(pal[0], 0.25), "#F6E070"])
        if t < -0.35:
            return rr.choice([pal[2], "#5A3A6A", dk(pal[2], 0.2)])
        return rr.choice([pal[1], pal[0], mix(pal[1], pal[2], 0.4)])
    hatch(B, pts, int(r * r / 9) + 12, col, seed, L=(r * 0.35, r * 0.6), W=(r * 0.18, r * 0.28), angle=-50, spread=14)
    out.append(f'<g {D.clip(f"<path d=\"{d}\"/>")}>{B.render()}</g>')
    out.append(f'<path d="{d}" fill="none" stroke="#2A3A6A" stroke-width="{max(1.4, r * 0.08):.1f}" opacity="0.75"/>')
    out.append(soft(D, cx + light[0] * r * 0.35, cy + light[1] * r * 0.35, r * 0.18, r * 0.14, "#FFFFF0", 0.75))
    out.append(f'<path d="M{cx:.1f} {cy - r * 0.8:.1f}q{r * 0.05:.1f} {-r * 0.25:.1f} {r * 0.2:.1f} {-r * 0.3:.1f}" stroke="#4A3018" stroke-width="{max(1.2, r * 0.07):.1f}" fill="none"/>')
    return "".join(out)


@design("still-life-with-apples")
def cezanne_apples():
    D = Doc("gmcz")
    box = (70, 62, 530, 428)   # 460 x 366
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [wall(D, "#6A5A48", 171, (0.5, 0.15), 0.3)]
    out.append(gilt_frame(D, box, 22, 173, "ornate", gold=("#F6E6B0", "#D0AE60", "#A08040", "#685020", "#33260C")))
    cp = clip_box(D, box)
    B = Brush()
    rnd = random.Random(5)
    paint = []
    # back wall: blue-grey and olive patches laid in diagonal strokes
    wall_r = UV([(-0.02, -0.02), (1.02, -0.02), (1.02, 0.5), (-0.02, 0.56)])
    paint.append(f'<path d="{pd(wall_r)}" fill="#7A8A8A"/>')
    hatch(B, wall_r, 1100, lambda x, y, r: r.choice(["#8A9A98", "#7E8E90", "#98A090", "#748490", "#909888", "#84907C"]), 1, L=(10, 16), W=(4.5, 6.5))
    paint.append(B.render())
    # patterned drapery hanging at the back left: deep blue with a leafy pattern
    drape = UV([(-0.02, -0.02), (0.3, -0.02), (0.36, 0.3), (0.3, 0.62), (0.12, 0.66), (-0.02, 0.7)])
    dd = smooth_closed(drape)
    paint.append(f'<path d="{dd}" fill="#2E3A6A"/>')
    hatch(B, drape, 520, lambda x, y, r: r.choice(["#3A4A8A", "#24305A", "#4A5A9A", "#5A3A5A", "#1E2848"]), 2, L=(9, 14), W=(4, 6), angle=-70)
    paint.append(f'<g {D.clip(f"<path d=\"{dd}\"/>")}>{B.render()}</g>')
    for k in range(16):
        x, y = X(rnd.uniform(0, 0.32)), Y(rnd.uniform(0.02, 0.62))
        if inside((x, y), drape):
            paint.append(f'<path d="{blob(x, y, 7, 3, k, 0.2, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#C89A3A", "#8A3A2A", "#6A8A4A"])}" opacity="0.9"/>')
    paint.append(ink(dd, "#141A34", 1.8, 3, 1, 0.6))
    # table: tilted top in warm brown, front edge darker
    table = UV([(-0.02, 0.52), (1.02, 0.46), (1.02, 1.02), (-0.02, 1.02)])
    paint.append(f'<path d="{pd(table)}" fill="#8A5A30"/>')
    hatch(B, table, 700, lambda x, y, r: r.choice(["#9A6A38", "#7A4A28", "#B07A40", "#6A4020", "#A8703A"]), 3, L=(10, 16), W=(4, 6))
    paint.append(B.render())
    # the white cloth, crumpled into peaks and valleys, cool blue in its folds
    cloth = UV([(0.12, 0.56), (0.3, 0.5), (0.55, 0.54), (0.8, 0.5), (0.98, 0.58), (1.02, 0.8), (0.95, 1.02), (0.2, 1.02), (0.06, 0.86), (0.1, 0.7)])
    cd = smooth_closed(cloth)
    paint.append(f'<path d="{cd}" fill="#E8E8E0"/>')

    def cloth_c(x, y, r):
        f = math.sin((x - y * 0.6) / 30) + 0.35 * math.sin((x + y) / 47)
        if f < -0.75:
            return r.choice(["#9AA4C0", "#8A94B4", "#A8AEC4"])
        if f < -0.1:
            return r.choice(["#C8CCD4", "#D4D4CC", "#BCC4CE"])
        return r.choice(["#FFFFFF", "#F6F4EC", "#F2EEE0", "#FFFBF0"])
    hatch(B, cloth, 1300, cloth_c, 4, L=(10, 16), W=(4, 6), angle=-45, spread=20)
    paint.append(f'<g {D.clip(f"<path d=\"{cd}\"/>")}>{B.render()}</g>')
    paint.append(ink(cd, "#3A4A7A", 1.6, 5, 1, 0.55))
    # the pitcher: white with a flowered band, on the left of the cloth
    jx, jy = X(0.2), Y(0.36)
    jug = [(jx - 36, jy + 98), (jx - 42, jy + 44), (jx - 30, jy), (jx - 20, jy - 26), (jx + 20, jy - 26), (jx + 30, jy), (jx + 42, jy + 44), (jx + 36, jy + 98)]
    jd = smooth_closed(jug)
    paint.append(f'<path d="{jd}" fill="#E8E4D8"/>')
    hatch(B, jug, 220, lambda x, y, r: r.choice(["#FFFFFF", "#F2EEE4", "#D8DCD8"]) if x < jx else r.choice(["#B8C0D0", "#A0A8C0", "#C8CCD0"]), 6, L=(8, 12), W=(3.5, 5))
    paint.append(f'<g {D.clip(f"<path d=\"{jd}\"/>")}>{B.render()}</g>')
    for k in range(7):
        fx, fy = jx - 30 + k * 10, jy + 44 + (k % 2) * 5
        paint.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="4.4" fill="{["#C83A2A", "#3A5AA8", "#E8A030"][k % 3]}"/><path d="M{fx:.1f} {fy + 4:.1f}l-3 7" stroke="#4A7A3A" stroke-width="1.6"/>')
    paint.append(f'<path d="M{jx + 30:.1f} {jy + 4:.1f}q30 8 8 46" stroke="#C8CCD0" stroke-width="8" fill="none"/>')
    paint.append(ink(jd, "#3A4A7A", 1.8, 6, 1, 0.7))
    # a white plate heaped with apples, and more rolling across the cloth
    px, py = X(0.58), Y(0.68)
    paint.append(f'<ellipse cx="{px:.1f}" cy="{py + 6:.1f}" rx="118" ry="32" fill="#6A7AA0" opacity="0.45"/>')
    paint.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="114" ry="30" fill="#F6F4EC" stroke="#3A4A7A" stroke-width="2"/>')
    paint.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="88" ry="20" fill="none" stroke="#C8D0D8" stroke-width="2.4"/>')
    RED = ("#F2803A", "#C8382A", "#6A1E28")
    YEL = ("#F6E070", "#E0A830", "#7A5A28")
    GRN = ("#C8D870", "#7A9A3A", "#3A5A3A")
    ORA = ("#FFB050", "#E87A1E", "#8A3A14")
    apples = [(0.44, 0.62, 30, RED), (0.58, 0.6, 31, YEL), (0.72, 0.62, 29, RED), (0.51, 0.49, 28, GRN), (0.65, 0.48, 29, RED),
              (0.88, 0.8, 27, YEL), (0.3, 0.86, 28, RED), (0.52, 0.9, 26, ORA), (0.72, 0.92, 27, GRN), (0.12, 0.78, 25, YEL)]
    for k, (u, v, r, pal) in enumerate(sorted(apples, key=lambda a: a[1])):
        ax, ay = X(u), Y(v)
        paint.append(f'<ellipse cx="{ax + r * 0.4:.1f}" cy="{ay + r * 0.85:.1f}" rx="{r * 1.0:.1f}" ry="{r * 0.28:.1f}" fill="#3A3A6A" opacity="0.3"/>')
        paint.append(cz_apple(D, B, ax, ay, r, 100 + k, pal))
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.06)}{varnish(D, box, 0.12, 0.2)}</g>')
    out.append(museum_label(D, 494, "Still Life with Apples", "PAUL CÉZANNE · c. 1893", "#F2E8D2", "#D0C0A0", ts=30, bs=18, gap=28))
    return finish(D, out, 83)


# ================================================================ 21. The Fighting Temeraire — Turner, 1839
@design("the-fighting-temeraire")
def fighting_temeraire():
    D = Doc("gmft")
    box = (66, 68, 534, 416)   # 468 x 348 (91 x 122 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [wall(D, "#4A2A22", 181, (0.5, 0.15), 0.35)]
    out.append(gilt_frame(D, box, 28, 183, "ornate"))
    cp = clip_box(D, box)
    rnd = random.Random(6)
    paint = []
    # sky: cool blue-green on the left with a pale moon, flaring to vermilion and gold at the sunset on the right
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.lin([(0, "#7AA0B0"), (0.35, "#C8C8A8"), (0.6, "#F2B060"), (0.8, "#E86A2A"), (1, "#B8401E")], 0, 0, 1, 0.2)}"/>')
    sun = (X(0.78), Y(0.6))
    paint.append(soft(D, sun[0], sun[1], W * 0.45, H * 0.4, "#FFD878", 0.75))
    paint.append(soft(D, sun[0], sun[1] - 10, W * 0.2, H * 0.16, "#FFF2C0", 0.9))
    # clouds: soft scumbles of fire and ash, with only a few dragged streaks
    B = Brush()
    for k in range(120):
        x, y = X(rnd.uniform(0.3, 1.05)), Y(rnd.uniform(0.02, 0.58))
        d_ = math.hypot((x - sun[0]) / W, (y - sun[1]) / H)
        col = rnd.choice(["#F2A040", "#E8702A", "#F6D070", "#C84A1E", "#FFE8A0"]) if d_ < 0.35 else rnd.choice(["#D88A5A", "#B86A50", "#E8B080", "#8A6A70", "#C8A890"])
        paint.append(soft(D, x, y, rnd.uniform(18, 50), rnd.uniform(6, 16), col, rnd.uniform(0.35, 0.7), rnd.uniform(-30, -5)))
    for k in range(40):
        x, y = X(rnd.uniform(-0.05, 0.4)), Y(rnd.uniform(0.0, 0.45))
        paint.append(soft(D, x, y, rnd.uniform(18, 40), rnd.uniform(6, 12), rnd.choice(["#A8C0C8", "#C8D8D0", "#8AAAB8", "#E8E8D8"]), 0.45))
    for k in range(60):
        x, y = X(rnd.uniform(0.45, 1.0)), Y(rnd.uniform(0.15, 0.55))
        a_ = math.radians(rnd.uniform(-30, -12))
        L = rnd.uniform(14, 30)
        B.dash([(x, y), (x + L * math.cos(a_), y + L * math.sin(a_))], rnd.choice(["#FFE098", "#F6B050", "#C84A1E"]), rnd.uniform(1.6, 3), 0.45)
    paint.append(B.render())
    paint.append(f'<path d="M{X(0.17):.1f} {Y(0.17):.1f}a10 10 0 1 0 8 -16a8 8 0 1 1 -8 16z" fill="#F6F2E0" opacity="0.85"/>')
    # water: mirror of the sky, soft horizontal glazes and a broken golden path under the sun
    water = UV([(-0.02, 0.66), (1.02, 0.64), (1.02, 1.02), (-0.02, 1.02)])
    paint.append(f'<path d="{pd(water)}" fill="{D.lin([(0, "#8AA0A0"), (0.4, "#B8B090"), (0.65, "#E89A50"), (1, "#A8401E")], 0, 0, 1, 0)}"/>')
    for k in range(90):
        x, y = X(rnd.uniform(-0.02, 1.02)), Y(rnd.uniform(0.67, 1.0))
        paint.append(soft(D, x, y, rnd.uniform(20, 50), rnd.uniform(2, 5), rnd.choice(["#7A9098", "#A8A890", "#5A6A70", "#C8B898", "#D8885A", "#E8C090"]), 0.5))
    for k in range(70):
        x, y = sun[0] + rnd.gauss(0, 18), Y(rnd.uniform(0.66, 1.0))
        L = rnd.uniform(8, 26)
        B.dash([(x - L / 2, y), (x + L / 2, y)], rnd.choice(["#FFE098", "#F6B050", "#FFF0C0", "#E87A2A"]), rnd.uniform(1.6, 3.2), 0.7)
    paint.append(B.render())
    # far shore at the right horizon, a dark smudge under the sun
    paint.append(soft(D, X(0.92), Y(0.645), W * 0.12, H * 0.02, "#5A2A1A", 0.7))
    # the Temeraire: a pale, ghostly three-decker with tall masts, towed toward the left
    tx, ty = X(0.25), Y(0.69)
    hull = [(tx - 72, ty - 34), (tx + 60, ty - 40), (tx + 80, ty - 20), (tx + 72, ty + 4), (tx - 62, ty + 4), (tx - 78, ty - 14)]
    hd_ = smooth_closed(hull)
    paint.append(f'<path d="{hd_}" fill="{D.lin([(0, "#F2EEDC"), (0.6, "#D0C8B0"), (1, "#9A9080")], 0, 0, 0, 1)}"/>')
    for k in range(3):
        y_ = ty - 28 + k * 9
        paint.append(f'<path d="M{tx - 62:.1f} {y_:.1f}L{tx + 66:.1f} {y_ - 4:.1f}" stroke="#A8A08A" stroke-width="1.6" stroke-dasharray="4 3" opacity="0.8"/>')
    paint.append(soft(D, tx + 50, ty - 18, 40, 20, "#F6C080", 0.35))
    for k, (dx, h) in enumerate(((-38, 190), (6, 215), (46, 150))):
        mx = tx + dx
        paint.append(f'<path d="M{mx:.1f} {ty - 34:.1f}L{mx + 3:.1f} {ty - 34 - h:.1f}" stroke="#E8E2C8" stroke-width="3"/>')
        for j in range(4):
            yy = ty - 52 - j * h * 0.24
            w_ = 32 - j * 6
            paint.append(f'<path d="M{mx - w_:.1f} {yy:.1f}L{mx + w_ + 2:.1f} {yy - 3:.1f}" stroke="#E0DAC0" stroke-width="2"/>')
        paint.append(f'<path d="M{mx + 3:.1f} {ty - 34 - h:.1f}L{mx - 60:.1f} {ty - 34:.1f}M{mx + 3:.1f} {ty - 34 - h:.1f}L{mx + 62:.1f} {ty - 36:.1f}" stroke="#D8D2BC" stroke-width="0.9" opacity="0.7"/>')
    paint.append(soft(D, tx, ty - 110, 90, 140, "#F6F2E0", 0.25))
    paint.append(f'<path d="{smooth_closed([(x, 2 * ty - y + 8) for x, y in hull])}" fill="#E8E0C8" opacity="0.35"/>')
    # the little black tug, its funnel belching red-brown smoke
    gx, gy = X(0.45), Y(0.73)
    tug = [(gx - 34, gy - 6), (gx + 30, gy - 8), (gx + 38, gy + 2), (gx + 28, gy + 8), (gx - 30, gy + 8)]
    paint.append(f'<path d="{smooth_closed(tug)}" fill="#1A1410"/>')
    paint.append(f'<path d="M{gx - 4:.1f} {gy - 6:.1f}V{gy - 40:.1f}" stroke="#1A1410" stroke-width="5"/>')
    paint.append(f'<path d="M{gx - 18:.1f} {gy - 6:.1f}V{gy - 30:.1f}" stroke="#1A1410" stroke-width="2"/>')
    paint.append(f'<ellipse cx="{gx + 16:.1f}" cy="{gy - 4:.1f}" rx="10" ry="6" fill="#2A1E18"/>')
    for k in range(10):
        paint.append(soft(D, gx - 4 - k * 9 + rnd.uniform(-3, 3), gy - 46 - k * 4 + rnd.uniform(-3, 3), 10 + k * 2, 7 + k, rnd.choice(["#6A2A1A", "#8A3A20", "#3A2018", "#C85A2A"]), 0.6))
    paint.append(soft(D, gx - 4, gy - 40, 5, 4, "#F2803A", 0.9))
    paint.append(f'<path d="{smooth_closed([(x, 2 * gy - y + 12) for x, y in tug])}" fill="#1A1410" opacity="0.35"/>')
    # a buoy and a small boat at the right
    paint.append(f'<path d="M{X(0.66):.1f} {Y(0.72):.1f}h22l-4 5h-15z" fill="#2A1A10"/>')
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.06)}{varnish(D, box, 0.14, 0.25)}</g>')
    out.append(museum_label(D, 488, "The Fighting Temeraire", "J. M. W. TURNER · 1839", "#F2E2C4", "#D0B490", ts=30, bs=18, gap=28))
    return finish(D, out, 89)


# ================================================================ 22. Wanderer above the Sea of Fog — Friedrich, 1818
@design("wanderer-above-the-sea-of-fog")
def wanderer():
    D = Doc("gmwa")
    box = (160, 56, 440, 422)   # 280 x 366 (94.8 x 74.8 cm, portrait)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [mat_board(D, (x0 - 14, y0 - 14, x1 + 14, y1 + 14), 7, "#3A4A52", 191)]
    out.append(gilt_frame(D, box, 14, 193, "plain", gold=("#F2E6C0", "#C8AE70", "#9A8048", "#5A4824", "#2A200E")))
    cp = clip_box(D, box)
    rnd = random.Random(4)
    paint = []
    # sky: pale, warm at the horizon, a soft cloud bank rising
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.lin([(0, "#9AB0C0"), (0.35, "#D8DCD8"), (0.55, "#F2E8D8")])}"/>')
    for k in range(18):
        paint.append(soft(D, X(rnd.uniform(-0.1, 1.1)), Y(rnd.uniform(0.05, 0.35)), W * rnd.uniform(0.15, 0.35), H * rnd.uniform(0.03, 0.06), rnd.choice(["#E8E4DC", "#C8CCD0", "#F6F2EA", "#B8C0C8"]), 0.6))
    # far mountains, faint and blue, rising out of the fog
    for k, (pts, col, op) in enumerate([
            ([(-0.05, 0.47), (0.1, 0.42), (0.2, 0.44), (0.3, 0.4), (0.38, 0.43), (0.45, 0.45)], "#8A98A8", 0.7),
            ([(0.55, 0.46), (0.68, 0.36), (0.74, 0.33), (0.8, 0.37), (0.92, 0.42), (1.05, 0.44)], "#7A8A9C", 0.8)]):
        poly = UV(pts) + UV([(pts[-1][0], 0.6), (pts[0][0], 0.6)])
        paint.append(f'<path d="{smooth_closed(poly)}" fill="{col}" opacity="{op}"/>')
    # the sea of fog: rolling banks with grey hollows, rock spurs breaking through
    for k in range(70):
        x, y = X(rnd.uniform(-0.1, 1.1)), Y(rnd.uniform(0.45, 0.95))
        paint.append(soft(D, x, y, W * rnd.uniform(0.1, 0.22), H * rnd.uniform(0.03, 0.06), rnd.choice(["#F2F0EA", "#E0E2E2", "#C8CED4", "#FFFFFF", "#B8C0C8"]), 0.75))
    for k, (u, v, w_, h_) in enumerate([(0.12, 0.62, 0.12, 0.1), (0.32, 0.58, 0.1, 0.08), (0.82, 0.6, 0.14, 0.12), (0.62, 0.66, 0.08, 0.06), (0.05, 0.75, 0.1, 0.12), (0.95, 0.74, 0.1, 0.1)]):
        rock = rough(UV([(u - w_ / 2, v + h_ * 0.3), (u - w_ * 0.25, v - h_ * 0.5), (u - w_ * 0.05, v - h_), (u + w_ * 0.1, v - h_ * 0.75), (u + w_ * 0.3, v - h_ * 0.55), (u + w_ / 2, v + h_ * 0.3)]), 60 + k, 5, 3)
        paint.append(f'<path d="{pd(rock)}" fill="{D.lin([(0, "#9AA098"), (0.5, "#7A8078"), (1, "#5A6058")], 0, 0, 1, 0)}"/>')
        for j in range(7):
            tx_, ty_ = X(u + rnd.uniform(-w_ * 0.35, w_ * 0.35)), Y(v - h_ * rnd.uniform(0.1, 0.7))
            if inside((tx_, ty_), rock):
                paint.append(conifer_dk(tx_, ty_, rnd.uniform(4, 8), "#4A564E", 50 + k * 9 + j))
        paint.append(soft(D, X(u), Y(v + h_ * 0.3), W * w_ * 0.7, H * 0.025, "#F2F0EA", 0.85))
    # foreground crag: dark rocks the wanderer stands on
    crag = rough(UV([(0.08, 1.04), (0.16, 0.9), (0.24, 0.84), (0.3, 0.8), (0.38, 0.78), (0.44, 0.76), (0.52, 0.775), (0.6, 0.78), (0.68, 0.84), (0.78, 0.88), (0.86, 0.95), (0.94, 1.04)]), 7, 6, 3)
    cd = pd(crag)
    paint.append(f'<path d="{cd}" fill="{D.lin([(0, "#4A4640"), (1, "#1A1814")])}"/>')
    paint.append(f'<g {D.clip(f"<path d=\"{cd}\"/>")}>{"".join(f"<path d=\"M{X(rnd.uniform(0.15, 0.85)):.1f} {Y(rnd.uniform(0.78, 1.0)):.1f}l{rnd.uniform(-14, 14):.1f} {rnd.uniform(-8, 8):.1f}\" stroke=\"{rnd.choice(["#6A665E", "#2A2620", "#8A847A"])}\" stroke-width=\"{rnd.uniform(1.2, 2.6):.1f}\" opacity=\"0.6\"/>" for _ in range(60))}</g>')
    paint.append(f'<path d="{cd}" fill="none" stroke="#9A9488" stroke-width="1.2" opacity="0.5"/>')
    # the wanderer, seen from behind: dark green frock coat, windblown hair, walking stick
    cx_, base = X(0.47), Y(0.78)
    s_ = H * 0.0042

    def F(x, y):
        return cx_ + x * s_, base + y * s_
    legs = [F(-10, 0), F(-9, -38), F(-3, -42), F(4, -40), F(9, -2), F(14, 0), F(8, -32), F(2, -36), F(-3, -10), F(-4, 0)]
    paint.append(f'<path d="{smooth_closed(legs)}" fill="#1E1C1A"/>')
    coat = [F(-17, -34), F(-13, -70), F(-12, -86), F(-5, -94), F(6, -94), F(14, -88), F(16, -70), F(20, -36), F(12, -32), F(2, -40), F(-8, -32)]
    cdd = smooth_closed(coat)
    paint.append(f'<path d="{cdd}" fill="{D.lin([(0, "#3A4A38"), (0.5, "#24302A"), (1, "#141A16")], 0, 0, 1, 0)}"/>')
    paint.append(f'<path d="M{F(0, -92)[0]:.1f} {F(0, -92)[1]:.1f}L{F(1, -40)[0]:.1f} {F(1, -40)[1]:.1f}" stroke="#141A16" stroke-width="1.4" opacity="0.8"/>')
    paint.append(f'<path d="{cdd}" fill="none" stroke="#5A6A58" stroke-width="1" opacity="0.5"/>')
    # arm and stick on the right
    paint.append(taper([F(13, -86), F(19, -70), F(22, -58)], 7 * s_, 5 * s_, "#20281F"))
    paint.append(f'<path d="M{F(22, -58)[0]:.1f} {F(22, -58)[1]:.1f}L{F(30, 2)[0]:.1f} {F(30, 2)[1]:.1f}" stroke="#2A1E14" stroke-width="{max(1.4, 1.6 * s_):.1f}"/>')
    # head and windblown hair
    hx, hy = F(1, -103)
    paint.append(f'<path d="{blob(hx, hy, 6.5 * s_, 8 * s_, 7, 0.06, 12)}" fill="#C89A70"/>')
    hair = [F(-6, -110), F(-2, -113), F(6, -112), F(10, -106), F(12, -100), F(16, -97), F(9, -98), F(6, -96), F(-4, -96), F(-7, -102)]
    paint.append(f'<path d="{smooth_closed(hair)}" fill="#6A4A2A"/>')
    for k in range(5):
        a, b = F(rnd.uniform(-4, 8), rnd.uniform(-112, -100)), F(rnd.uniform(10, 20), rnd.uniform(-104, -94))
        paint.append(f'<path d="M{a[0]:.1f} {a[1]:.1f}Q{(a[0] + b[0]) / 2:.1f} {a[1] - 2:.1f} {b[0]:.1f} {b[1]:.1f}" stroke="#8A6A40" stroke-width="1" fill="none"/>')
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.05)}{varnish(D, box, 0.12, 0.22, 7, 0.35)}</g>')
    out.append(museum_label(D, 474, "Wanderer above the Sea of Fog", "CASPAR DAVID FRIEDRICH · 1818", "#F2EEE4", "#C8D0D4", ts=25, bs=16, gap=28, max_w=460))
    return finish(D, out, 97)


def conifer_dk(x, base, h, col, seed):
    rnd = random.Random(seed)
    pts = [(x, base - h)]
    for i in range(1, 6):
        t = i / 5
        w = h * 0.3 * t
        pts += [(x + w, base - h + h * t * 0.9), (x + w * 0.5, base - h + h * t * 0.9 - 1)]
    pts += [(x, base)]
    left = [(2 * x - px, py) for px, py in pts[::-1]]
    return f'<path d="{pd(pts + left)}" fill="{col}"/>'


# ================================================================ 23. Hunters in the Snow — Bruegel, 1565
def hs_tree(x, base, top, w, seed, col="#241D17", lit="#5A4C3E", lean=0.0, branchy=1.0):
    """Bruegel's tall winter tree: a straight tapering trunk with a lit edge, thin upward branches and a fine
    net of twigs; returns (svg, perch points for crows)."""
    rnd = random.Random(seed)
    H = base - top
    n = 9
    trunk = [(x + lean * H * (i / n) ** 1.3 + rnd.uniform(-1.2, 1.2) * (i > 0), base - H * i / n) for i in range(n + 1)]
    out = [taper(trunk, w, 1.2, col)]
    out.append(taper([(px - w * 0.22 * (1 - i / n), py) for i, (px, py) in enumerate(trunk[:-2])], w * 0.28, 0.4, lit, 0.55))
    perches = []
    segs = []
    k = 0
    y = base - H * 0.3
    while y > top + 6:
        t = (base - y) / H
        tx = x + lean * H * t ** 1.3
        side = 1 if k % 2 else -1
        if rnd.random() < 0.25:
            side = -side
        ang = math.radians(-90 + side * rnd.uniform(28, 62))
        L = H * rnd.uniform(0.16, 0.3) * (1.15 - t * 0.6) * branchy
        branch_tree(rnd, tx, y, ang, L, max(1.0, w * 0.42 * (1 - t * 0.7)), 2, segs, 16)
        y -= H * rnd.uniform(0.045, 0.085)
        k += 1
    for pts, w0, w1 in segs:
        out.append(taper(pts, w0, max(0.5, w1), col, 0.95))
        if w0 > 1.4 and rnd.random() < 0.35:
            perches.append(pts[2])
    return "".join(out), perches


def hs_crow(x, y, s, col="#141210", flip=1):
    """A crow perched: rounded body, tail down, beak forward."""
    f = flip
    body = [(x - 4 * s * f, y - 3 * s), (x + 1 * s * f, y - 5.5 * s), (x + 4.2 * s * f, y - 5 * s), (x + 6.5 * s * f, y - 4.4 * s), (x + 4 * s * f, y - 3.6 * s),
            (x + 3 * s * f, y - 1 * s), (x - 1 * s * f, y + 0.5 * s), (x - 5 * s * f, y + 4 * s), (x - 6 * s * f, y + 3.4 * s), (x - 4 * s * f, y - 0.5 * s)]
    return f'<path d="{smooth_closed(body)}" fill="{col}"/>'


def hs_flying_bird(x, y, s, col="#141210"):
    """The great bird gliding over the valley, wings spread wide, tail fanned."""
    d = (f"M{x - 16 * s:.1f} {y - 3 * s:.1f}Q{x - 9 * s:.1f} {y - 7 * s:.1f} {x - 2 * s:.1f} {y - 1 * s:.1f}L{x + 1 * s:.1f} {y - 2.5 * s:.1f}"
         f"L{x + 4 * s:.1f} {y - 2 * s:.1f}Q{x + 10 * s:.1f} {y - 8 * s:.1f} {x + 18 * s:.1f} {y - 5 * s:.1f}Q{x + 10 * s:.1f} {y - 2 * s:.1f} {x + 4 * s:.1f} {y + 1 * s:.1f}"
         f"L{x + 1 * s:.1f} {y + 4.5 * s:.1f}L{x - 1.5 * s:.1f} {y + 1 * s:.1f}Q{x - 9 * s:.1f} {y - 1 * s:.1f} {x - 16 * s:.1f} {y - 3 * s:.1f}Z")
    return f'<path d="{d}" fill="{col}"/>'


def hs_hunter(x, base, h, seed, coat="#2C241E", lit="#5A4A3A", stride=1.0, pike=True, fox=False, bend=0.0):
    """A hunter seen from behind trudging down through the snow: cap, hunched shoulders, belted knee-length coat,
    leggings, boots sunk in snow, a long pike over the shoulder."""
    rnd = random.Random(seed)
    k = h / 100.0

    def P(px, py):
        # lean forward (down the hill, to the right)
        return x + (px + bend * (-py) * 0.12) * k, base + py * k
    out = []
    # cast shadow on the snow (light from the left)
    out.append(f'<ellipse cx="{x + 14 * k:.1f}" cy="{base + 1:.1f}" rx="{20 * k:.1f}" ry="{3.2 * k:.1f}" fill="#4A5A60" opacity="0.28"/>')
    # legs: one planted, one swinging back with the heel lifted
    legs = [([P(-5, -34), P(-6, -18), P(-7, -2)], 8.5, 6.5), ([P(5, -34), P(7 + 3 * stride, -18), P(4 + 7 * stride, -5)], 8, 6)]
    for pts, w0, w1 in legs:
        out.append(taper(pts, w0 * k, w1 * k, "#3A2E26"))
        out.append(taper(pts[:2], w0 * k * 0.35, w1 * k * 0.3, "#6A5848", 0.6))
    # boots (half hidden in snow)
    out.append(f'<path d="{blob(*P(-7, -2), 5.5 * k, 3 * k, seed, 0.1, 10)}" fill="#1A1410"/>')
    out.append(f'<path d="{blob(*P(4 + 7 * stride, -4), 5 * k, 2.8 * k, seed + 1, 0.1, 10, 30)}" fill="#1A1410"/>')
    out.append(f'<path d="{blob(*P(-7, 0), 7 * k, 2.4 * k, seed + 2, 0.15, 10)}" fill="#E8ECEA" opacity="0.9"/>')
    # coat
    coat_pts = [P(-11, -80), P(-15, -70), P(-15, -54), P(-13, -46), P(-16, -36), P(-17, -28), P(-6, -26), P(4, -27), P(16, -29), P(15, -38),
                P(12, -47), P(14, -56), P(14, -70), P(10, -80), P(0, -83)]
    cd = smooth_closed(coat_pts)
    out.append(f'<path d="{cd}" fill="{coat}"/>')
    cid = None
    # folds and the light down the left side of the back
    out.append(taper([P(-12, -76), P(-13, -60), P(-12, -46), P(-14, -30)], 4.5 * k, 3 * k, lit, 0.7))
    out.append(taper([P(-2, -70), P(-1, -55)], 2.2 * k, 1 * k, lit, 0.35))
    out.append(taper([P(2, -44), P(5, -28)], 1.8 * k, 1 * k, "#140E0A", 0.6))
    out.append(taper([P(-7, -44), P(-9, -28)], 1.6 * k, 1 * k, "#140E0A", 0.5))
    # belt
    out.append(taper([P(-14, -47), P(0, -45), P(13, -47)], 3 * k, 3 * k, "#16100C"))
    # pouch on the belt
    out.append(f'<path d="{blob(*P(11, -42), 4 * k, 5 * k, seed + 3, 0.1, 10)}" fill="#5A4030"/>')
    # arm: the near arm reaching up to steady the pike on the shoulder
    if pike:
        out.append(taper([P(10, -74), P(17, -64), P(15, -76)], 6.5 * k, 5 * k, coat))
        out.append(f'<path d="M{P(-30, -128)[0]:.1f} {P(-30, -128)[1]:.1f}L{P(30, -56)[0]:.1f} {P(30, -56)[1]:.1f}" stroke="#3A2C20" stroke-width="{max(1.4, 2.4 * k):.1f}" stroke-linecap="round"/>')
        out.append(f'<path d="M{P(-30, -128)[0]:.1f} {P(-30, -128)[1]:.1f}L{P(-24, -121)[0]:.1f} {P(-24, -121)[1]:.1f}" stroke="#8A8A86" stroke-width="{max(1.4, 2.6 * k):.1f}" stroke-linecap="round"/>')
    else:
        out.append(taper([P(-13, -74), P(-16, -58), P(-15, -46)], 6 * k, 5 * k, coat))
    if fox:
        # the thin fox slung over the back: a long russet body, the brush hanging down
        fx = [P(-6, -84), P(4, -86), P(10, -78), P(9, -64), P(6, -54), P(2, -62), P(-2, -74)]
        out.append(f'<path d="{smooth_closed(fx)}" fill="#8A4A24"/>')
        out.append(taper([P(6, -56), P(9, -46), P(8, -36)], 5 * k, 2 * k, "#9A5A2C"))
        out.append(taper([P(8, -38), P(8, -34)], 2.4 * k, 1 * k, "#E8E0D0"))
        out.append(taper([P(-5, -82), P(3, -84), P(8, -76)], 2 * k, 1.5 * k, "#C07A40", 0.8))
    # head: cap and the back of the hood
    out.append(f'<path d="{blob(*P(-1, -88), 7.5 * k, 8 * k, seed + 4, 0.06, 12)}" fill="#3A2A20"/>')
    out.append(f'<path d="{blob(*P(-1, -93), 7.8 * k, 4.6 * k, seed + 5, 0.08, 12)}" fill="#201812"/>')
    out.append(f'<path d="{blob(*P(-4, -91), 2.5 * k, 3 * k, seed + 6, 0.1, 8)}" fill="#6A5444" opacity="0.6"/>')
    # snow sticking to the shoulders
    out.append(taper([P(-12, -80), P(-4, -84), P(4, -83)], 2.2 * k, 1 * k, "#D8DEDC", 0.55))
    return "".join(out)


def hs_dog(x, base, s, seed, col="#2E241C", belly="#6A5644", flip=1, phase=0.0, head_down=1.0, view="side"):
    """A lean hunting hound trudging: deep chest, tucked waist, angled hocks, tail low, head down at the snow."""
    rnd = random.Random(seed)
    f = flip

    def P(px, py):
        return x + px * s * f, base + py * s
    far = dk(col, 0.3)
    out = [f'<ellipse cx="{x + 3 * s * f:.1f}" cy="{base + 0.5:.1f}" rx="{12 * s:.1f}" ry="{1.6 * s:.1f}" fill="#4A5A60" opacity="0.25"/>']
    a = phase
    # far legs first
    out.append(taper([P(7, -9), P(8.5 - 2 * a, -4.5), P(8 - 3.5 * a, 0)], 2.0 * s, 1.1 * s, far))
    out.append(taper([P(-9, -10), P(-6.5 + 1.5 * a, -5.5), P(-9.5 + 2.5 * a, -2.6), P(-9 + 2.5 * a, 0)], 2.6 * s, 1.1 * s, far))
    # body: deep chest, arched loin, tucked belly, rounded haunch
    body = [P(-12.5, -12.5), P(-11, -15.2), P(-4, -15.6), P(3, -15.4), P(8, -15.8), P(11, -14.5), P(11.5, -11), P(9.5, -8.3), P(5, -8.6),
            P(0, -10.6), P(-5, -11), P(-9, -9.2), P(-12.3, -9.8)]
    out.append(f'<path d="{smooth_closed(body)}" fill="{col}"/>')
    out.append(taper([P(-10, -15), P(-2, -15.4), P(7, -15.6)], 1.3 * s, 0.7 * s, mix(col, "#D8CCB8", 0.4), 0.75))
    out.append(taper([P(9, -9.5), P(4, -9.4), P(0, -10.8)], 1.6 * s, 0.5 * s, belly, 0.7))
    # near legs: foreleg straight, hind leg with the hock angled back
    out.append(taper([P(8.5, -10), P(9 + 2 * a, -4.5), P(10 + 3 * a, 0)], 2.4 * s, 1.2 * s, col))
    out.append(taper([P(-10, -11.5), P(-7.5 - 1.5 * a, -6), P(-11 - 2 * a, -2.6), P(-10.5 - 2 * a, 0)], 3.4 * s, 1.2 * s, col))
    # tail hanging low, a gentle hook at the tip
    out.append(taper([P(-12, -13.5), P(-15, -10.5), P(-16, -6), P(-15, -3.5)], 1.5 * s, 0.6 * s, col))
    # neck reaching forward and down; long narrow head with a drop ear
    hd = head_down
    neck = [P(7, -15.5), P(11, -16.4 + 2 * hd), P(15, -13.5 + 4.5 * hd), P(14, -10.5 + 4 * hd), P(10.5, -10)]
    out.append(f'<path d="{smooth_closed(neck)}" fill="{col}"/>')
    head = [P(13, -15 + 4.5 * hd), P(16.5, -15.6 + 5 * hd), P(19.5, -13.6 + 6 * hd), P(21.5, -11.4 + 6.5 * hd), P(20.6, -10.6 + 6.5 * hd),
            P(16.5, -11.4 + 5 * hd), P(13.4, -11.6 + 4.5 * hd)]
    out.append(f'<path d="{smooth_closed(head)}" fill="{col}"/>')
    out.append(taper([P(15, -15 + 4.8 * hd), P(14.2, -12.8 + 4.6 * hd), P(14.6, -10.6 + 4.4 * hd)], 2.4 * s, 1.1 * s, dk(col, 0.4)))
    out.append(f'<circle cx="{P(21.2, -11 + 6.5 * hd)[0]:.1f}" cy="{P(21.2, -11 + 6.5 * hd)[1]:.1f}" r="{0.7 * s:.1f}" fill="#0E0A08"/>')
    return "".join(out)


def hs_skater(x, y, h, seed, pose="glide", col="#1C1816", accent=None):
    """A tiny skater on the ice (h = height px): a few deliberate strokes, as Bruegel's crowd."""
    rnd = random.Random(seed)
    lean = rnd.uniform(-0.35, 0.35)
    out = [f'<path d="M{x - h * 0.35:.1f} {y + 0.4:.1f}h{h * 0.7:.1f}" stroke="#5E6E6A" stroke-width="{max(0.8, h * 0.12):.1f}" opacity="0.5" stroke-linecap="round"/>']
    if pose == "fallen":
        out.append(taper([(x - h * 0.45, y - h * 0.08), (x + h * 0.4, y - h * 0.14)], h * 0.28, h * 0.22, col))
        out.append(f'<circle cx="{x + h * 0.5:.1f}" cy="{y - h * 0.18:.1f}" r="{h * 0.12:.1f}" fill="{col}"/>')
        out.append(taper([(x - h * 0.3, y - h * 0.1), (x - h * 0.5, y - h * 0.4)], h * 0.1, h * 0.08, col))
        return "".join(out)
    top = (x + lean * h * 0.5, y - h * 0.82)
    out.append(taper([(x + lean * h * 0.1, y - h * 0.42), top], h * 0.3, h * 0.26, accent or col))
    out.append(taper([(x + lean * h * 0.1, y - h * 0.46), (x - h * 0.16, y)], h * 0.13, h * 0.1, col))
    out.append(taper([(x + lean * h * 0.1, y - h * 0.46), (x + h * 0.2 + lean * h * 0.2, y - h * 0.02)], h * 0.13, h * 0.1, col))
    if pose == "arms":
        out.append(taper([(top[0] - h * 0.32, top[1] + h * 0.18), top, (top[0] + h * 0.32, top[1] + h * 0.14)], h * 0.09, h * 0.07, col))
    out.append(f'<circle cx="{top[0] + lean * h * 0.08:.1f}" cy="{top[1] - h * 0.1:.1f}" r="{h * 0.11:.1f}" fill="{col}"/>')
    return "".join(out)


def hs_house(x, base, w, h, seed, wall="#9A6E4E", roof_h=None, side=0.0, chimney=True, lit_side=True):
    """A village house in snow: lit gable wall, shadowed side wall, snow-loaded roof, dark windows and door."""
    rnd = random.Random(seed)
    rh = roof_h or w * 0.55
    out = []
    sw = w * side
    # side wall (in shadow)
    if sw:
        out.append(f'<path d="{pd([(x + w, base), (x + w, base - h), (x + w + sw, base - h - sw * 0.12), (x + w + sw, base - sw * 0.1)])}" fill="{dk(wall, 0.35)}"/>')
        out.append(f'<path d="{pd([(x + w / 2, base - h - rh), (x + w / 2 + sw, base - h - rh - sw * 0.12), (x + w + sw + 1.5, base - h - sw * 0.12 + 1.5), (x + w + 1.5, base - h + 1.5)])}" fill="#EEF2EE"/>')
        out.append(f'<path d="M{x + w + 1.5:.1f} {base - h + 1.5:.1f}L{x + w + sw + 1.5:.1f} {base - h - sw * 0.12 + 1.5:.1f}" stroke="#7A8884" stroke-width="0.9"/>')
    # gable wall
    out.append(f'<path d="{pd([(x, base), (x, base - h), (x + w / 2, base - h - rh), (x + w, base - h), (x + w, base)])}" fill="{wall}"/>')
    out.append(f'<path d="{pd([(x, base), (x, base - h), (x + w * 0.25, base - h - rh * 0.5), (x + w * 0.25, base)])}" fill="{lt(wall, 0.18)}" opacity="0.6"/>')
    # snow on the gable edges
    out.append(f'<path d="{pd([(x - 1.5, base - h + 1), (x + w / 2, base - h - rh - 1.5), (x + w + 1.5, base - h + 1), (x + w, base - h + 2), (x + w / 2, base - h - rh + 2), (x, base - h + 2)])}" fill="#F4F6F2"/>')
    # windows / door
    if w > 7:
        out.append(f'<rect x="{x + w * 0.38:.1f}" y="{base - h * 0.55:.1f}" width="{w * 0.24:.1f}" height="{h * 0.55:.1f}" fill="#2A1E16"/>')
        if w > 11:
            out.append(f'<rect x="{x + w * 0.14:.1f}" y="{base - h * 0.85:.1f}" width="{w * 0.14:.1f}" height="{h * 0.2:.1f}" fill="#2A1E16"/>')
            out.append(f'<rect x="{x + w * 0.72:.1f}" y="{base - h * 0.85:.1f}" width="{w * 0.14:.1f}" height="{h * 0.2:.1f}" fill="#2A1E16"/>')
    if chimney and w > 9:
        cx_ = x + w * 0.5 + sw * 0.6
        cy_ = base - h - rh * 0.6
        out.append(f'<rect x="{cx_:.1f}" y="{cy_ - w * 0.25:.1f}" width="{w * 0.12:.1f}" height="{w * 0.3:.1f}" fill="{dk(wall, 0.2)}"/>')
        out.append(f'<rect x="{cx_ - 0.5:.1f}" y="{cy_ - w * 0.28:.1f}" width="{w * 0.12 + 1:.1f}" height="{max(1.2, w * 0.05):.1f}" fill="#F4F6F2"/>')
    out.append(f'<path d="M{x - 1:.1f} {base + 0.5:.1f}H{x + w + sw + 1:.1f}" stroke="#F4F6F2" stroke-width="{max(1.2, h * 0.12):.1f}"/>')
    return "".join(out)


def hs_small_tree(x, base, h, seed, col="#4A4038"):
    """A small bare tree or pollard in the distance."""
    rnd = random.Random(seed)
    segs = []
    branch_tree(rnd, x, base, math.radians(-90 + rnd.uniform(-6, 6)), h, max(0.9, h * 0.07), 2, segs, 20)
    return "".join(taper(p, w0, max(0.4, w1), col, 0.9) for p, w0, w1 in segs)


@design("hunters-in-the-snow")
def hunters_in_the_snow():
    from figures import person
    D = Doc("gmhs")
    box = (64, 66, 536, 404)   # 472 x 338 (117 x 162 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [wall(D, "#3A3A34", 201, (0.5, 0.15), 0.3)]
    out.append(simple_frame(D, box, 20, ("#7A6A4E", "#3E3222", "#1A140C"), 3))
    out.append(f'<rect x="{x0 - 4}" y="{y0 - 4}" width="{W + 8}" height="{H + 8}" fill="none" stroke="#C8A860" stroke-width="2"/>')
    cp = clip_box(D, box)
    rnd = random.Random(5)
    paint = []
    SNOW, SNOW_SH, ICE = "#EEF1EC", "#B8C4C2", "#86A59C"
    # ---- the cold green-grey sky, darker overhead
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.lin([(0, "#5E7468"), (0.3, "#7E9488"), (0.48, "#A2B2A6"), (0.6, "#B8C4B8")])}"/>')
    paint.append(strokes(D.nid(), pd(UV([(0, 0), (1, 0), (1, 0.48), (0, 0.48)])), (x0 - 30, y0, x1, Y(0.48)), ["#6E8478", "#8EA296", "#A8B8AC", "#58705E"], 31,
                         n=140, angle=-4, length=(30, 90), width=(3, 8), opacity=(0.12, 0.3), curve=0.06))
    # ---- far plain beyond the valley: a pale frozen bay and low hills at the horizon
    far = UV([(0.0, 0.47), (0.2, 0.455), (0.4, 0.45), (0.6, 0.445), (1.0, 0.44), (1.0, 0.6), (0.0, 0.6)])
    paint.append(f'<path d="{pd(far)}" fill="#C4CEC6"/>')
    paint.append(f'<path d="{smooth_closed(UV([(0.18, 0.47), (0.35, 0.462), (0.5, 0.466), (0.52, 0.48), (0.3, 0.485), (0.16, 0.48)]))}" fill="#9EB2AC"/>')
    for k in range(40):
        u, v = rnd.uniform(0.12, 0.62), rnd.uniform(0.452, 0.49)
        paint.append(hs_small_tree(X(u), Y(v), rnd.uniform(3, 6), 900 + k, "#7A8682"))
    # ---- the jagged crags on the right
    crag = UV([(0.5, 0.47), (0.53, 0.42), (0.56, 0.4), (0.585, 0.33), (0.6, 0.355), (0.625, 0.27), (0.645, 0.3), (0.66, 0.24), (0.68, 0.28), (0.7, 0.26),
               (0.725, 0.31), (0.75, 0.21), (0.765, 0.17), (0.785, 0.22), (0.81, 0.19), (0.835, 0.25), (0.86, 0.15), (0.875, 0.12), (0.895, 0.18),
               (0.92, 0.155), (0.95, 0.21), (0.975, 0.17), (1.02, 0.2), (1.02, 0.5), (0.5, 0.5)])
    crd = pd(crag)
    paint.append(f'<path d="{crd}" fill="{D.lin([(0, "#D8DED8"), (1, "#C2CCC6")])}"/>')
    rock = []
    peaks = [p for i, p in enumerate(crag[1:-2], 1) if p[1] < crag[i - 1][1] and p[1] < crag[i + 1][1]]
    for i, (px, py) in enumerate(peaks):
        # the shadowed right face of each pinnacle, rock ribs and gullies down its face
        drop = (Y(0.47) - py)
        face_ = [(px, py), (px + drop * 0.32, py + drop * 0.55), (px + drop * 0.18, Y(0.5)), (px + 2, Y(0.5)), (px - drop * 0.05, py + drop * 0.5)]
        rock.append(f'<path d="{smooth_closed(face_)}" fill="#6E847E" opacity="0.7"/>')
        for j in range(12):
            sx_ = px + rnd.uniform(-drop * 0.18, drop * 0.3)
            sy_ = py + rnd.uniform(4, drop * 0.5)
            rock.append(taper([(sx_, sy_), (sx_ + rnd.uniform(-2, 4), sy_ + rnd.uniform(6, 18))], rnd.uniform(1.2, 2.4), 0.5, rnd.choice(["#5E706C", "#6E807A", "#4A5A58"]), 0.7))
    paint.append(f'<g {D.clip(f"<path d=\"{crd}\"/>")}>{"".join(rock)}</g>')
    paint.append(f'<path d="{smooth_open(crag[1:-2])}" fill="none" stroke="#F2F4F0" stroke-width="1.4" opacity="0.7"/>')
    # haze at the foot of the crags
    paint.append(f'<rect x="{X(0.45)}" y="{Y(0.38)}" width="{W * 0.6}" height="{H * 0.14}" fill="{D.lin([(0, "#C8D2CA", 0), (1, "#C8D2CA", 0.85)])}"/>')
    # ---- the valley floor: snowfields falling away to the ponds
    valley = UV([(0.0, 0.48), (0.5, 0.47), (1.02, 0.47), (1.02, 1.02), (0.0, 1.02)])
    vd = pd(valley)
    paint.append(f'<path d="{vd}" fill="{D.lin([(0, "#DCE2DC"), (0.4, "#E6EAE4"), (1, "#EEF0EA")])}"/>')
    paint.append(strokes(D.nid(), vd, (x0 - 20, Y(0.47), x1, y1), ["#C4CECA", "#F6F8F4", "#B0BEBA"], 33, n=110, angle=6, length=(14, 40), width=(1.5, 4),
                         opacity=(0.2, 0.45), curve=0.1))
    # field boundaries and hedgerows
    for k in range(16):
        u, v = rnd.uniform(0.42, 1.0), rnd.uniform(0.5, 0.64)
        L = rnd.uniform(0.04, 0.12)
        paint.append(f'<path d="M{X(u):.1f} {Y(v):.1f}l{W * L:.1f} {rnd.uniform(-3, 4):.1f}" stroke="#7A8480" stroke-width="{rnd.uniform(0.8, 1.4):.1f}" opacity="0.6"/>')
    # the frozen river winding from the mill and the ponds
    river = UV([(1.02, 0.6), (0.94, 0.605), (0.88, 0.63), (0.82, 0.66), (0.83, 0.69), (0.9, 0.705), (0.98, 0.7), (1.02, 0.7)])
    paint.append(f'<path d="{smooth_closed(river)}" fill="{ICE}"/>')
    ponds = [((0.62, 0.565), 0.13, 0.026, 41), ((0.7, 0.735), 0.24, 0.07, 42), ((0.9, 0.79), 0.12, 0.04, 43), ((0.44, 0.535), 0.07, 0.018, 44)]
    for (u, v), rx, ry, sd_ in ponds:
        pts = blob_pts(X(u), Y(v), W * rx, H * ry, sd_, 0.06, 22)
        d = smooth_closed(pts)
        paint.append(f'<path d="{d}" fill="{D.lin([(0, "#6E8E86"), (0.5, ICE), (1, "#A6BEB4")])}"/>')
        # scratches of skates and the sheen of the ice
        paint.append(strokes(D.nid(), d, (X(u - rx), Y(v - ry), X(u + rx), Y(v + ry)), ["#C8D6D0", "#7A928A", "#DCE6E0"], sd_, n=int(rx * 260),
                             angle=rnd.uniform(-8, 8), length=(8, 26), width=(0.6, 1.6), opacity=(0.3, 0.6), curve=0.15))
        paint.append(f'<path d="{d}" fill="none" stroke="#F4F6F2" stroke-width="2" opacity="0.8"/>')
    # ---- the mill, its wheel frozen fast, by the river at the right
    mx_, my_ = X(0.9), Y(0.62)
    paint.append(hs_house(mx_ - 18, my_, 26, 16, 51, "#8A6448", 12, 0.35))
    wc = (mx_ + 14, my_ - 2)
    paint.append(f'<circle cx="{wc[0]:.1f}" cy="{wc[1]:.1f}" r="9" fill="none" stroke="#3A2E24" stroke-width="2"/>')
    for a in range(0, 180, 30):
        ra = math.radians(a)
        paint.append(f'<path d="M{wc[0] - 9 * math.cos(ra):.1f} {wc[1] - 9 * math.sin(ra):.1f}L{wc[0] + 9 * math.cos(ra):.1f} {wc[1] + 9 * math.sin(ra):.1f}" stroke="#3A2E24" stroke-width="1"/>')
    for j in range(6):
        paint.append(f'<path d="M{wc[0] - 7 + j * 2.8:.1f} {wc[1] + 6:.1f}l0.4 {rnd.uniform(4, 8):.1f}" stroke="#F4F8F6" stroke-width="1.3" stroke-linecap="round"/>')
    paint.append(f'<path d="M{wc[0] - 10:.1f} {wc[1] - 9.5:.1f}a10 10 0 0 1 20 0" fill="none" stroke="#F4F6F2" stroke-width="1.6"/>')
    # ---- the village: houses around the ponds, a church, a bridge
    houses = [(0.47, 0.55, 9, 6, 0.4), (0.52, 0.545, 8, 5, 0.3), (0.56, 0.56, 10, 7, 0.4), (0.68, 0.545, 9, 6, 0.3), (0.74, 0.55, 8, 5, 0.3),
              (0.79, 0.565, 10, 6, 0.35), (0.84, 0.58, 9, 6, 0.3), (0.58, 0.63, 13, 9, 0.4), (0.53, 0.66, 12, 8, 0.4), (0.62, 0.66, 11, 8, 0.4),
              (0.96, 0.66, 14, 9, 0.3), (0.86, 0.69, 12, 8, 0.35), (0.45, 0.6, 11, 7, 0.4), (0.97, 0.88, 18, 12, 0.3), (0.8, 0.86, 15, 10, 0.4),
              (0.72, 0.58, 9, 6, 0.3), (0.64, 0.6, 8, 6, 0.3)]
    for i, (u, v, w_, h_, sd_) in enumerate(houses):
        paint.append(hs_house(X(u), Y(v), w_, h_, 60 + i, rnd.choice(["#9A6E4E", "#A87E5A", "#8A5E42", "#B08A64", "#7E5A44"]), side=sd_))
    # the church with its spire
    chx, chy = X(0.6), Y(0.535)
    paint.append(hs_house(chx, chy, 16, 9, 77, "#B8A486", 6, 0.6, False))
    paint.append(f'<path d="{pd([(chx - 5, chy), (chx - 5, chy - 16), (chx + 1, chy - 16), (chx + 1, chy)])}" fill="#A8947A"/>')
    paint.append(f'<path d="{pd([(chx - 6, chy - 16), (chx - 2, chy - 30), (chx + 2, chy - 16)])}" fill="#5A4A3E"/>')
    paint.append(f'<path d="M{chx - 2:.1f} {chy - 30:.1f}L{chx - 5:.1f} {chy - 17:.1f}" stroke="#F2F4F0" stroke-width="1.2"/>')
    # the stone bridge over the stream
    bx_, by_ = X(0.8), Y(0.665)
    paint.append(f'<path d="M{bx_ - 14:.1f} {by_:.1f}Q{bx_:.1f} {by_ - 9:.1f} {bx_ + 14:.1f} {by_:.1f}L{bx_ + 14:.1f} {by_ + 4:.1f}Q{bx_ + 7:.1f} {by_ + 4:.1f} {bx_ + 6:.1f} {by_ + 1:.1f}Q{bx_:.1f} {by_ - 4:.1f} {bx_ - 6:.1f} {by_ + 1:.1f}Q{bx_ - 7:.1f} {by_ + 4:.1f} {bx_ - 14:.1f} {by_ + 4:.1f}Z" fill="#8A7A66"/>')
    paint.append(f'<path d="M{bx_ - 14:.1f} {by_ - 0.5:.1f}Q{bx_:.1f} {by_ - 10:.1f} {bx_ + 14:.1f} {by_ - 0.5:.1f}" stroke="#F4F6F2" stroke-width="1.6" fill="none"/>')
    paint.append(person(bx_ + 2, by_ - 5, 9, "walk", -1, {"top": "#3A2A22", "bottom": "#2A2420", "skin": "#C8987A"}, seed=88, shadow=0))
    # small bare trees and pollards across the valley
    for k in range(46):
        u, v = rnd.uniform(0.42, 1.0), rnd.uniform(0.5, 0.9)
        if any(abs(u - pu) < rx * 0.9 and abs(v - pv) < ry * 1.2 for (pu, pv), rx, ry, _ in ponds):
            continue
        h_ = 5 + (v - 0.5) * 50
        paint.append(hs_small_tree(X(u), Y(v), h_, 400 + k, mix("#3A322A", "#8A928C", max(0, 0.75 - (v - 0.5) * 2))))
    # skaters, curlers, a fallen boy, children with tops, on every pond
    for i, ((u, v), rx, ry, sd_) in enumerate(ponds):
        n = int(rx * 150)
        for j in range(n):
            a = rnd.uniform(0, 2 * math.pi)
            r = math.sqrt(rnd.random()) * 0.85
            sx_, sy_ = X(u + rx * r * math.cos(a)), Y(v + ry * r * math.sin(a)) + 2
            h_ = 3.2 + (sy_ - Y(0.5)) / H * 22
            pose = wpick(rnd, [(6, "glide"), (3, "arms"), (0.5, "fallen")])
            accent = rnd.choice([None, None, None, "#8A2A1E", "#5A3A2A", "#3A3A4A", "#9A7A5A"])
            paint.append(hs_skater(sx_, sy_, h_, 700 + i * 50 + j, pose, rnd.choice(["#1C1816", "#2A2220", "#3A2A22"]), accent))
    # people on the near bank and a sledge
    paint.append(person(X(0.86), Y(0.9), 15, "walk", -1, {"top": "#4A2A22", "bottom": "#2A2420", "skin": "#C8987A"}, seed=91, shadow=0.1))
    paint.append(f'<path d="M{X(0.86) - 11:.1f} {Y(0.9) - 1:.1f}h-10" stroke="#3A2A20" stroke-width="2.4" stroke-linecap="round"/>')
    paint.append(f'<path d="M{X(0.86) - 21:.1f} {Y(0.9) - 4:.1f}h9l2 3h-12z" fill="#6A4A30"/><path d="M{X(0.86) - 21:.1f} {Y(0.9) - 5:.1f}h9" stroke="#8A6A40" stroke-width="2.5"/>')
    # ---- the hill in the foreground, its crest falling to the right
    hill = UV([(-0.02, 0.38), (0.06, 0.41), (0.16, 0.465), (0.28, 0.54), (0.4, 0.62), (0.5, 0.7), (0.58, 0.79), (0.64, 0.88), (0.68, 0.96), (0.7, 1.03), (-0.02, 1.03)])
    hd_ = smooth_closed(hill)
    paint.append(f'<path d="{hd_}" fill="{D.lin([(0, "#F4F6F2"), (0.6, "#E8ECE8"), (1, "#D8E0DE")], 0, 0, 0.6, 1)}"/>')
    paint.append(strokes(D.nid(), hd_, (x0 - 20, Y(0.38), X(0.72), y1), ["#C8D2D0", "#FFFFFF", "#B4C2C0", "#D8E0DC"], 35, n=130, angle=28, length=(14, 44),
                         width=(1.6, 4.4), opacity=(0.25, 0.55), curve=0.1))
    # cold blue shadow pooling in the hollow at the lower left, and the long shadows of the trees across the snow
    paint.append(f'<path d="{hd_}" fill="{D.lin([(0, "#8EA0A6", 0.0), (0.55, "#8EA0A6", 0.0), (1, "#8EA0A6", 0.45)], 0, 0, 0, 1)}"/>')
    paint.append(f'<path d="{hd_}" fill="{D.rad([(0, "#7A8E96", 0.35), (1, "#7A8E96", 0)], 0.0, 1.0, 0.6)}"/>')
    for (u, v) in ((0.13, 0.46), (0.27, 0.55), (0.42, 0.65)):
        paint.append(taper([(X(u) + 2, Y(v) + 1), (X(u) + 30, Y(v) + 26), (X(u) + 60, Y(v) + 52)], 3.5, 1, "#7E9098", 0.35))
    # the shadowed drop of the crest and the scrub along it
    paint.append(taper(UV([(0.04, 0.405), (0.16, 0.47), (0.28, 0.545), (0.4, 0.625), (0.5, 0.705), (0.58, 0.795), (0.64, 0.885), (0.69, 0.99)]), 3, 4.5, "#7E8C8A", 0.85))
    for k in range(70):
        t = rnd.random()
        crest = hill[1:10]
        i = min(len(crest) - 2, int(t * (len(crest) - 1)))
        ft = t * (len(crest) - 1) - i
        cx_, cy_ = crest[i][0] + (crest[i + 1][0] - crest[i][0]) * ft, crest[i][1] + (crest[i + 1][1] - crest[i][1]) * ft
        paint.append(f'<path d="M{cx_:.1f} {cy_ + 1:.1f}l{rnd.uniform(-2, 3):.1f} {-rnd.uniform(3, 9):.1f}" stroke="#3A322A" stroke-width="{rnd.uniform(0.7, 1.3):.1f}" opacity="0.8"/>')
    # ---- the inn at the left: timbered gable, snow on the roof, the sign hanging askew from its bracket
    ix, iy = X(0.0), Y(0.6)
    inn = []
    inn.append(f'<path d="{pd([(ix - 10, iy), (ix - 10, iy - 70), (ix + 52, iy - 62), (ix + 52, iy - 4)])}" fill="#7A5A42"/>')
    inn.append(f'<path d="{pd([(ix + 52, iy - 4), (ix + 52, iy - 62), (ix + 74, iy - 58), (ix + 74, iy - 8)])}" fill="#5A4030"/>')
    for j in range(5):
        xx = ix + j * 13
        inn.append(f'<path d="M{xx:.1f} {iy - 69 + j * 1.6:.1f}V{iy - 2 - j * 0.8:.1f}" stroke="#3A2A1E" stroke-width="2"/>')
    inn.append(f'<path d="M{ix - 10:.1f} {iy - 38:.1f}L{ix + 52:.1f} {iy - 34:.1f}" stroke="#3A2A1E" stroke-width="2"/>')
    for (wx, wy) in ((ix + 18, iy - 56), (ix + 36, iy - 54), (ix + 18, iy - 26), (ix + 58, iy - 50)):
        inn.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="8" height="9" fill="#1E1610"/><rect x="{wx:.1f}" y="{wy + 8:.1f}" width="8" height="1.6" fill="#F2F4F0"/>')
    inn.append(f'<path d="{pd([(ix + 34, iy - 2), (ix + 34, iy - 22), (ix + 45, iy - 21), (ix + 45, iy - 3)])}" fill="#1E1610"/>')
    roof = [(ix - 14, iy - 68), (ix + 30, iy - 98), (ix + 80, iy - 60), (ix + 74, iy - 57), (ix + 30, iy - 90), (ix - 10, iy - 64)]
    inn.append(f'<path d="{pd(roof)}" fill="#F2F4F0" stroke="#8A9896" stroke-width="1"/>')
    inn.append(f'<path d="{pd([(ix - 14, iy - 68), (ix + 30, iy - 98), (ix + 20, iy - 104), (ix - 20, iy - 76)])}" fill="#E4EAE6"/>')
    inn.append(f'<rect x="{ix + 14}" y="{iy - 112}" width="7" height="14" fill="#6A4A36"/><rect x="{ix + 13}" y="{iy - 114}" width="9" height="3" fill="#F2F4F0"/>')
    # the bracket and the sign hanging from one hinge
    sx0, sy0 = ix + 74, iy - 50
    inn.append(f'<path d="M{sx0:.1f} {sy0:.1f}h22" stroke="#2A1E16" stroke-width="2"/><path d="M{sx0:.1f} {sy0 + 8:.1f}l14 -8" stroke="#2A1E16" stroke-width="1.2"/>')
    inn.append(f'<path d="M{sx0 + 20:.1f} {sy0:.1f}l1 6" stroke="#2A1E16" stroke-width="1"/>')
    sg = [(sx0 + 12, sy0 + 6), (sx0 + 26, sy0 + 5), (sx0 + 28, sy0 + 19), (sx0 + 14, sy0 + 21)]
    inn.append(f'<path d="{pd(sg)}" fill="#D8C8A0" stroke="#3A2A1E" stroke-width="1.2"/>')
    inn.append(f'<path d="M{sx0 + 16:.1f} {sy0 + 16:.1f}l4 -4l4 4M{sx0 + 20:.1f} {sy0 + 12:.1f}v-3m-2 1l2 -2l2 2" stroke="#6A3A22" stroke-width="1" fill="none"/>')
    paint.append("".join(inn))
    # the fire outside the inn where the family singes a pig, smoke drifting
    fx_, fy_ = X(0.2), Y(0.6)
    paint.append(soft(D, fx_, fy_ - 8, 26, 22, "#F2A040", 0.55))
    for j, (dx, hh, c) in enumerate(((-4, 18, "#C83A14"), (1, 24, "#E8601E"), (5, 15, "#E8601E"), (0, 14, "#F6C040"), (-2, 9, "#FFF0A0"))):
        paint.append(taper([(fx_ + dx, fy_), (fx_ + dx + rnd.uniform(-3, 3), fy_ - hh * 0.5), (fx_ + dx + rnd.uniform(-2, 4), fy_ - hh)], 7 - j * 0.6, 0.5, c))
    for j in range(5):
        paint.append(soft(D, fx_ + 6 + j * 7, fy_ - 30 - j * 10, 10 + j * 3, 7 + j * 2, "#8A8E88", 0.35 - j * 0.04))
    paint.append(f'<path d="M{fx_ - 12:.1f} {fy_ + 2:.1f}l24 -1" stroke="#2A1E16" stroke-width="2.4"/>')
    for j, (dx, pose, top) in enumerate(((-14, "stand_34", "#8A2A1E"), (13, "stand_34", "#3A3A44"), (20, "walk", "#5A3A2A"))):
        paint.append(person(fx_ + dx, fy_ + 3, 22 - j * 2, pose, -1 if dx > 0 else 1, {"top": top, "bottom": "#2A2420", "skin": "#E0A888", "hat_kind": None}, seed=230 + j, shadow=0.1))
    # ---- the tall bare trees marching down the crest, crows in their branches
    crows = []
    for k, (u, v, w_, lean, br) in enumerate([(0.13, 0.46, 7, 0.02, 1.0), (0.27, 0.55, 7.5, -0.03, 1.1), (0.42, 0.65, 6.5, 0.03, 1.0), (0.55, 0.76, 6, -0.02, 0.9),
                                              (0.64, 0.89, 5.5, 0.04, 0.8)]):
        svg, perch = hs_tree(X(u), Y(v), y0 - 30 + k * 6, w_, 500 + k, lean=lean, branchy=br)
        paint.append(svg)
        crows += perch[:2]
    for i, (px, py) in enumerate(crows[:7]):
        paint.append(hs_crow(px, py, 1.05, flip=1 if i % 2 else -1))
    paint.append(hs_flying_bird(X(0.6), Y(0.3), 1.2))
    # ---- the hunters and their tired hounds, trudging down toward the village
    hunters = [(0.245, 0.735, 50, 11, True, "#2C241E"), (0.33, 0.79, 56, 12, False, "#2A231E"), (0.425, 0.875, 62, 13, False, "#30271F")]
    # their footprints trailing back up the slope, and the dogs' tracks
    trail = []
    for (u, v, h, sd_, fox, coat) in hunters:
        for j in range(1, 9):
            tx_, ty_ = X(u) - j * 9.5 + (j % 2) * 3, Y(v) - j * 5.2 - (j % 2) * 1.5
            trail.append(f'<ellipse cx="{tx_:.1f}" cy="{ty_:.1f}" rx="{2.6 - j * 0.12:.1f}" ry="1.1" fill="#8E9E9E" opacity="{0.75 - j * 0.05:.2f}"/>')
    for k in range(60):
        u = rnd.uniform(0.04, 0.5)
        v = 0.66 + (u - 0.04) * 0.5 + rnd.uniform(0.0, 0.26)
        trail.append(f'<ellipse cx="{X(u):.1f}" cy="{Y(v):.1f}" rx="{rnd.uniform(0.9, 1.6):.1f}" ry="0.7" fill="#98A6A6" opacity="0.55"/>')
    paint.append("".join(trail))
    # the pack strung out around and behind the men, noses down
    dogs = [(0.135, 0.69, 0.78, 1, 0.2, "#2E241C"), (0.19, 0.745, 0.84, 1, 0.8, "#4A3626"), (0.27, 0.81, 0.9, 1, 0.4, "#2A201A"),
            (0.355, 0.875, 0.98, 1, 0.9, "#3A2A20"), (0.2, 0.83, 0.92, 1, 0.1, "#6A5038"), (0.5, 0.955, 1.06, 1, 0.6, "#2E241C"),
            (0.1, 0.77, 0.86, 1, 0.3, "#5A4430"), (0.29, 0.93, 1.02, 1, 0.55, "#1E1814"), (0.475, 0.86, 0.92, 1, 0.8, "#3A2C22"),
            (0.06, 0.71, 0.76, 1, 0.5, "#3A2C22"), (0.39, 0.975, 1.1, 1, 0.25, "#4A3828"), (0.15, 0.9, 0.98, 1, 0.7, "#2A201A"),
            (0.56, 0.905, 0.96, 1, 0.35, "#2A201A")]
    for i, (u, v, s, f, ph, c) in enumerate(dogs):
        paint.append(hs_dog(X(u), Y(v), s, 240 + i, c, mix(c, "#C8B090", 0.45), f, ph, 1.0 if i % 3 else 0.55))
    for (u, v, h, sd_, fox, coat) in hunters:
        paint.append(hs_hunter(X(u), Y(v), h, sd_, coat=coat, fox=fox, pike=True, bend=0.6 + h * 0.004, stride=0.8 + (h - 50) * 0.02))
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.05)}{varnish(D, box, 0.1, 0.2)}</g>')
    out.append(museum_label(D, 474, "Hunters in the Snow", "PIETER BRUEGEL THE ELDER · 1565", "#F2EEE4", "#C8C4B4", ts=29, bs=16, gap=28, max_w=460))
    return finish(D, out, 101)


# ================================================================ 24. Several Circles — Kandinsky, 1926
def glow_circle(D, cx, cy, r, col, op=0.85, halo=None, edge=None):
    """A translucent disc of colour with a soft halo, as Kandinsky's circles float and overlap."""
    out = []
    if halo:
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 1.35:.1f}" fill="{D.rad([(0, halo, 0), (0.7, halo, 0.55), (1, halo, 0)])}"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{D.rad([(0, lt(col, 0.18)), (0.8, col), (1, dk(col, 0.15))], 0.42, 0.4, 0.62)}" opacity="{op}"/>')
    if edge:
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{edge}" stroke-width="{max(1, r * 0.04):.1f}" opacity="0.8"/>')
    return "".join(out)


@design("several-circles")
def several_circles():
    D = Doc("gmkc")
    box = (94, 54, 506, 466)   # 412 square (140 x 140 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H
    out = [wall(D, "#E6E2DA", 211, (0.5, 0.2), 0.15)]
    out.append(simple_frame(D, box, 9, ("#F4F2EC", "#D8D4CA", "#9A968A"), 3))
    cp = clip_box(D, box)
    rnd = random.Random(3)
    paint = []
    # deep night ground, a little brushy, darker at the corners
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.rad([(0, "#2A2A3A"), (0.6, "#16161E"), (1, "#0A0A10")], 0.5, 0.5, 0.75)}"/>')
    paint.append(strokes(D.nid(), f"M{x0} {y0}H{x1}V{y1}H{x0}Z", box, ["#2E2E44", "#1A1A26", "#3A3448"], 5, n=260, angle=-20, length=(30, 80), width=(4, 10), opacity=(0.08, 0.2), curve=0.2))
    # the great blue circle with its violet corona
    paint.append(glow_circle(D, X(0.42), Y(0.4), W * 0.27, "#1E2A6A", 0.95, "#6A3AA8"))
    paint.append(f'<circle cx="{X(0.42):.1f}" cy="{Y(0.4):.1f}" r="{W * 0.27:.1f}" fill="none" stroke="#8A6AD8" stroke-width="2.4" opacity="0.5"/>')
    # inside and around it, overlapping smaller circles in clear colours
    circles = [(0.48, 0.42, 0.09, "#E8A030", 0.85, None), (0.56, 0.5, 0.05, "#2E2E2E", 0.95, None), (0.32, 0.3, 0.06, "#4AA0D8", 0.8, None),
               (0.42, 0.56, 0.035, "#E84A3A", 0.9, None), (0.66, 0.24, 0.07, "#3A8A5A", 0.8, None), (0.72, 0.62, 0.11, "#C8C83A", 0.75, "#F2F070"),
               (0.78, 0.78, 0.05, "#E8508A", 0.85, None), (0.2, 0.7, 0.065, "#3A5AC8", 0.8, "#6A8AF0"), (0.84, 0.36, 0.035, "#F2F2E8", 0.9, None),
               (0.6, 0.84, 0.03, "#8A3AC8", 0.9, None), (0.14, 0.18, 0.025, "#E87A2A", 0.9, None), (0.9, 0.12, 0.02, "#F2D040", 0.9, None),
               (0.3, 0.86, 0.04, "#2AA0A0", 0.85, None), (0.52, 0.3, 0.025, "#F2F2E8", 0.85, None), (0.7, 0.44, 0.018, "#E84A3A", 0.9, None),
               (0.36, 0.48, 0.05, "#7A3A9A", 0.6, None), (0.88, 0.9, 0.02, "#4AA0D8", 0.9, None), (0.1, 0.48, 0.018, "#F2F2E8", 0.9, None)]
    for u, v, r, col, op, halo in circles:
        paint.append(glow_circle(D, X(u), Y(v), W * r, col, op, halo))
    # a few dry-brush specks of light, like stars in the void
    for k in range(14):
        paint.append(f'<circle cx="{X(rnd.uniform(0, 1)):.1f}" cy="{Y(rnd.uniform(0, 1)):.1f}" r="{rnd.uniform(0.5, 1.0):.1f}" fill="#E8E4F0" opacity="{rnd.uniform(0.15, 0.4):.2f}"/>')
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.06)}{varnish(D, box, 0.08, 0.15, 5, 0.25)}</g>')
    out.append(museum_label(D, 506, "Several Circles", "WASSILY KANDINSKY · 1926", "#2A2620", "#6A645A", ts=29, bs=17, gap=26))
    return finish(D, out, 107)


# ================================================================ 25. Tiger in a Tropical Storm (Surprised!) — Rousseau, 1891
def jungle_leaf(D, x, y, L, w, ang, pal, seed, veins=True):
    """A naive, crisply outlined leaf with a midrib and parallel veins (Rousseau's patient foliage)."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    tip = (x + L * math.cos(a), y + L * math.sin(a))
    nx, ny = -math.sin(a), math.cos(a)
    mid = ((x + tip[0]) / 2, (y + tip[1]) / 2)
    pts = [(x, y), (mid[0] + nx * w + (tip[0] - x) * 0.05, mid[1] + ny * w + (tip[1] - y) * 0.05), tip, (mid[0] - nx * w, mid[1] - ny * w)]
    d = smooth_closed(pts)
    out = [f'<path d="{d}" fill="{D.lin([(0, pal[0]), (0.5, pal[1]), (1, pal[2])], 0, 0, 1, 1)}"/>']
    out.append(f'<path d="M{x:.1f} {y:.1f}L{tip[0]:.1f} {tip[1]:.1f}" stroke="{pal[0]}" stroke-width="1.1" opacity="0.8"/>')
    if veins:
        for i in range(1, 6):
            t = i / 6.5
            px, py = x + (tip[0] - x) * t, y + (tip[1] - y) * t
            ww = w * math.sin(math.pi * t) * 0.85
            for sg in (-1, 1):
                out.append(f'<path d="M{px:.1f} {py:.1f}l{(nx * sg * ww + math.cos(a) * ww * 0.5):.1f} {(ny * sg * ww + math.sin(a) * ww * 0.5):.1f}" stroke="{pal[2]}" stroke-width="0.8" opacity="0.6"/>')
    out.append(f'<path d="{d}" fill="none" stroke="{dk(pal[2], 0.4)}" stroke-width="1" opacity="0.7"/>')
    return "".join(out)


def tiger(D, x, y, s, seed):
    """Rousseau's tiger crouching, mid-leap, head turned toward us — flat naive forms with bold stripes."""
    rnd = random.Random(seed)

    def T(px, py):
        return x + px * s, y + py * s
    out = []
    body = [T(-60, 6), T(-44, -10), T(-20, -16), T(6, -14), T(26, -18), T(40, -14), T(46, 2), T(40, 14), T(20, 16), T(-10, 18), T(-40, 20), T(-58, 18)]
    bd = smooth_closed(body)
    legs = [[T(-50, 14), T(-66, 30), T(-74, 34)], [T(-36, 16), T(-44, 34), T(-50, 38)], [T(28, 12), T(44, 30), T(54, 32)], [T(16, 14), T(24, 34), T(34, 38)]]
    for lg in legs:
        out.append(taper(lg, 15 * s, 10 * s, "#D8701E"))
        out.append(taper(lg, 5 * s, 3 * s, "#1A0E08", 0.85))
    tail = [T(-58, 4), T(-80, -4), T(-92, -20), T(-88, -34)]
    out.append(taper(tail, 9 * s, 5 * s, "#D8701E"))
    out.append(f'<path d="{bd}" fill="{D.lin([(0, "#F2A040"), (0.6, "#D8701E"), (1, "#A84A12")], 0, 0, 0, 1)}"/>')
    belly = [T(-44, 14), T(-10, 16), T(20, 14), T(18, 10), T(-10, 11), T(-40, 10)]
    out.append(f'<path d="{smooth_closed(belly)}" fill="#F6E8C8"/>')
    cid = D.clip(f'<path d="{bd}"/>')
    st = []
    for i in range(14):
        sx_ = -54 + i * 7.4
        st.append(taper([T(sx_ + rnd.uniform(-2, 2), -18), T(sx_ + 3, -6), T(sx_ - 1, 4)], 3.6 * s, 0.8 * s, "#1A0E08"))
    out.append(f'<g {cid}>{"".join(st)}</g>')
    for k in range(4):
        tt = 0.25 + k * 0.2
        p = tail[int(tt * 3)]
        out.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{3.4 * s:.1f}" fill="#1A0E08"/>')
    # head turned toward us, ears back, mouth snarling
    hx, hy = T(54, -14)
    head = [T(42, -26), T(50, -36), T(62, -36), T(72, -28), T(74, -14), T(68, -2), T(56, 2), T(44, -4), T(40, -16)]
    hd = smooth_closed(head)
    out.append(f'<path d="{hd}" fill="{D.rad([(0, "#F6B860"), (0.7, "#E07A24"), (1, "#A84A12")], 0.5, 0.45, 0.6)}"/>')
    for ex in (46, 68):
        out.append(f'<path d="{pd([T(ex - 5, -32), T(ex, -42), T(ex + 5, -32)])}" fill="#E07A24" stroke="#1A0E08" stroke-width="{1.2 * s:.1f}"/>')
        out.append(f'<path d="{pd([T(ex - 2.5, -33), T(ex, -38), T(ex + 2.5, -33)])}" fill="#F6E8C8"/>')
    for sx_, sy_ in ((44, -24), (70, -24), (48, -12), (66, -12)):
        out.append(f'<path d="M{T(sx_, sy_)[0]:.1f} {T(sx_, sy_)[1]:.1f}l{(4 if sx_ < 57 else -4) * s:.1f} {1 * s:.1f}" stroke="#1A0E08" stroke-width="{1.6 * s:.1f}" stroke-linecap="round"/>')
    out.append(f'<path d="{smooth_closed([T(50, -12), T(57, -6), T(64, -12), T(64, 0), T(57, 2), T(50, 0)])}" fill="#F6E8C8"/>')
    for ex, sg in ((51, -1), (63, 1)):
        c_ = T(ex, -21)
        out.append(f'<path d="M{c_[0] - 3.6 * s:.1f} {c_[1] + 0.6 * s:.1f}Q{c_[0]:.1f} {c_[1] - 3.2 * s:.1f} {c_[0] + 3.6 * s:.1f} {c_[1] - 0.4 * s:.1f}Q{c_[0]:.1f} {c_[1] + 2.4 * s:.1f} {c_[0] - 3.6 * s:.1f} {c_[1] + 0.6 * s:.1f}Z" fill="#E8D040" stroke="#1A0E08" stroke-width="{0.9 * s:.1f}"/>'
                   f'<ellipse cx="{c_[0]:.1f}" cy="{c_[1]:.1f}" rx="{0.7 * s:.1f}" ry="{1.4 * s:.1f}" fill="#1A0E08"/>')
    out.append(f'<path d="{pd([T(54, -14), T(60, -14), T(57, -9)])}" fill="#8A3A2A"/>')
    out.append(f'<path d="M{T(52, -4)[0]:.1f} {T(52, -4)[1]:.1f}Q{T(57, 0)[0]:.1f} {T(57, 0)[1]:.1f} {T(62, -4)[0]:.1f} {T(62, -4)[1]:.1f}" fill="#7A1E18" stroke="#1A0E08" stroke-width="{1 * s:.1f}"/>')
    for tx_ in (54, 60):
        out.append(f'<path d="{pd([T(tx_ - 1, -3), T(tx_, 0), T(tx_ + 1, -3)])}" fill="#FFFFFF"/>')
    out.append(f'<path d="{hd}" fill="none" stroke="#1A0E08" stroke-width="{1.2 * s:.1f}" opacity="0.7"/>')
    for k in range(5):
        out.append(f'<path d="M{T(52, -6)[0]:.1f} {T(52, -6)[1] + k * 1.2 * s:.1f}l{-10 * s:.1f} {(-2 + k) * s:.1f}M{T(62, -6)[0]:.1f} {T(62, -6)[1] + k * 1.2 * s:.1f}l{10 * s:.1f} {(-2 + k) * s:.1f}" stroke="#F6F0E0" stroke-width="0.7" opacity="0.8"/>')
    return "".join(out)


@design("tiger-in-a-tropical-storm")
def rousseau_tiger():
    D = Doc("gmrt")
    box = (68, 66, 532, 420)   # 464 x 354 (130 x 162 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H
    out = [wall(D, "#2A3428", 221, (0.5, 0.15), 0.3)]
    out.append(gilt_frame(D, box, 22, 223, "ornate"))
    cp = clip_box(D, box)
    rnd = random.Random(7)
    paint = []
    # storm sky: bruised grey-violet with a flash of lightning
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.lin([(0, "#5A5A6A"), (0.5, "#8A8A88"), (1, "#3A4A3A")])}"/>')
    for k in range(10):
        paint.append(soft(D, X(rnd.uniform(0, 1)), Y(rnd.uniform(0, 0.35)), W * rnd.uniform(0.12, 0.25), H * rnd.uniform(0.05, 0.1), rnd.choice(["#4A4A5A", "#9A9890", "#6A6A78"]), 0.6))
    bolt = [(X(0.62), Y(-0.02)), (X(0.6), Y(0.08)), (X(0.64), Y(0.1)), (X(0.6), Y(0.22)), (X(0.63), Y(0.24)), (X(0.58), Y(0.36))]
    paint.append(f'<path d="{pd(bolt, False)}" stroke="#FFFFF0" stroke-width="2.4" fill="none"/><path d="{pd(bolt, False)}" stroke="#F2F0FF" stroke-width="7" fill="none" opacity="0.25"/>')
    # layers of jungle: dark back, mid greens, bright foreground blades, each leaf outlined
    pals = [("#4A6A3A", "#2E4A2A", "#16261A"), ("#6A8A3A", "#4A6A2A", "#24361A"), ("#8AAA4A", "#5A7A2A", "#2A3A14"), ("#A8B85A", "#6A8A2A", "#34461A"),
            ("#5A8A6A", "#2E5A4A", "#14302A"), ("#C8C86A", "#8A9A3A", "#4A5A1A")]
    for layer in range(4):
        leaves = []
        for k in range(70 if layer < 3 else 40):
            x = X(rnd.uniform(-0.05, 1.05))
            y = Y(rnd.uniform(0.25 + layer * 0.08, 1.05))
            L = rnd.uniform(26, 60) * (0.8 + layer * 0.15)
            ang = rnd.uniform(-160, -20)
            leaves.append(jungle_leaf(D, x, y, L, L * rnd.uniform(0.18, 0.32), ang, pals[(layer + k) % len(pals)] if layer else pals[0], 1000 * layer + k, layer > 0))
        paint.append("".join(leaves))
        if layer == 1:
            # tall grass blades and a tree trunk
            paint.append(taper([(X(0.86), y1 + 10), (X(0.85), Y(0.4)), (X(0.88), Y(0.0))], 22, 12, "#4A3A2A"))
        if layer == 2:
            blades = []
            for k in range(60):
                bx = X(rnd.uniform(-0.05, 1.05))
                by = y1 + 10
                h = rnd.uniform(60, 180)
                bend = rnd.uniform(20, 60)
                blades.append(taper([(bx, by), (bx + bend * 0.2, by - h * 0.5), (bx + bend, by - h)], rnd.uniform(4, 8), 1, rnd.choice(["#6A8A2A", "#8AA03A", "#4A6A2A", "#A8B848"])))
            paint.append("".join(blades))
            paint.append(tiger(D, X(0.36), Y(0.7), 1.9, 9))
    # rain: fine silver slants across everything
    rain = "".join(f'<path d="M{X(rnd.uniform(-0.1, 1.1)):.1f} {Y(rnd.uniform(-0.1, 1)):.1f}l{-14:.1f} {40:.1f}"/>' for _ in range(220))
    paint.append(f'<g stroke="#E8ECF0" stroke-width="0.8" opacity="0.45">{rain}</g>')
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.06)}{varnish(D, box, 0.1, 0.22)}</g>')
    out.append(museum_label(D, 492, "Tiger in a Tropical Storm", "HENRI ROUSSEAU · 1891", "#F2EEDC", "#C8C8A8", ts=29, bs=17, gap=28))
    return finish(D, out, 109)


# ================================================================ 26. Walk on the Beach — Sorolla, 1909
def broad(B, region, n, colfn, seed, L=(10, 22), W=(5, 9), angle=-80, spread=18, op=(0.8, 1.0)):
    """Sorolla's loaded, broad strokes."""
    dabs(B, region, n, colfn, seed, L=L, W=W, angle=angle, spread=spread, op=op)


@design("walk-on-the-beach")
def walk_on_the_beach():
    D = Doc("gmwb")
    box = (92, 54, 508, 458)   # 416 x 404 (205 x 200 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [wall(D, "#E8E0D2", 231, (0.5, 0.2), 0.15)]
    out.append(simple_frame(D, box, 12, ("#FFFDF6", "#E6DCC8", "#A8987C"), 3))
    out.append(f'<rect x="{x0 - 3}" y="{y0 - 3}" width="{W + 6}" height="{H + 6}" fill="none" stroke="#C8A860" stroke-width="1.6"/>')
    cp = clip_box(D, box)
    rnd = random.Random(5)
    B = Brush()
    paint = []
    # the sea: deep turquoise far out, emerald and foam near the shore
    sea = UV([(-0.02, -0.02), (1.02, -0.02), (1.02, 0.5), (-0.02, 0.44)])
    paint.append(f'<path d="{pd(sea)}" fill="{D.lin([(0, "#2E6A8A"), (0.6, "#3E8A9A"), (1, "#7AB8B0")])}"/>')

    def sea_c(x, y, r):
        v = (y - y0) / H
        if r.random() < 0.12 + v * 0.4:
            return r.choice(["#FFFFFF", "#E8F4F0", "#CDE8E4"])
        return r.choice(["#2E6A8A", "#3A7A9A", "#4A9AA8", "#5AAAB0", "#2A5A7A", "#6ABAB8"])
    broad(B, sea, 900, sea_c, 1, L=(10, 24), W=(4, 7), angle=0, spread=8)
    paint.append(B.render())
    # wet sand mirroring the sky, then warm dry sand with violet shadows
    sand = UV([(-0.02, 0.44), (1.02, 0.5), (1.02, 1.02), (-0.02, 1.02)])
    paint.append(f'<path d="{pd(sand)}" fill="{D.lin([(0, "#C8C8C0"), (0.2, "#E8D8C0"), (1, "#E0C8A8")])}"/>')
    broad(B, sand, 900, lambda x, y, r: r.choice(["#F2E2C8", "#E8D0B0", "#D8C8D0", "#F6EAD8", "#C8B8C8", "#E0C8A0"]), 2, L=(12, 24), W=(4, 7), angle=-5, spread=10)
    paint.append(B.render())
    # the two women walking into the wind, white dresses blazing in the sun
    # shadows on the sand first
    paint.append(soft(D, X(0.48), Y(0.97), W * 0.3, H * 0.035, "#8A7AA8", 0.6))
    paint.append(soft(D, X(0.8), Y(0.93), W * 0.22, H * 0.03, "#8A7AA8", 0.5))
    def lady(ox, oy, sc, seed, hat="#F2EEE6", hatband="#C8B8D8", parasol=False, veil=True):
        """An Edwardian woman in white walking left into the wind: fitted bodice, flaring skirt blown back,
        a wide hat over a profile in warm shadow."""
        def Q(x, y):
            return X(ox + x * sc), Y(oy + y * sc)
        g = []
        skirt = [Q(-0.05, 0.0), Q(-0.07, 0.2), Q(-0.12, 0.42), Q(-0.12, 0.52), Q(0.06, 0.54), Q(0.22, 0.52), Q(0.3, 0.46), Q(0.16, 0.3), Q(0.06, 0.12), Q(0.04, 0.0)]
        bodice = [Q(-0.06, -0.2), Q(-0.075, -0.15), Q(-0.065, -0.08), Q(-0.05, 0.02), Q(0.045, 0.02), Q(0.05, -0.1), Q(0.045, -0.2), Q(0.0, -0.22)]
        for poly, n_, sd in ((skirt, 300, 1), (bodice, 90, 2)):
            dd = smooth_closed(poly)
            g.append(f'<path d="{dd}" fill="#ECECF4"/>')
            lit_edge = ox * W + x0
            broad(B, poly, int(n_ * sc / 0.5), lambda x, y, r, le=lit_edge: r.choice(["#FFFFFF", "#FAFAF4", "#FFF8EA", "#F2F2F8"]) if x > X(ox + 0.0 * sc) + (y - Y(oy)) * 0.15 else
                  r.choice(["#B4B4D8", "#A4A4CC", "#C4C4E2", "#9898C4", "#B0C0E0"]), seed + sd, L=(12 * sc / 0.5, 26 * sc / 0.5), W=(4, 7.5), angle=-100, spread=12)
            g.append(f'<g {D.clip(f"<path d=\"{dd}\"/>")}>{B.render()}</g>')
        # neck, profile and hair in the warm shadow of the hat
        g.append(f'<path d="{smooth_closed([Q(-0.02, -0.21), Q(-0.022, -0.26), Q(0.02, -0.26), Q(0.02, -0.21)])}" fill="#A87460"/>')
        face_ = [Q(-0.01, -0.36), Q(-0.035, -0.345), Q(-0.04, -0.325), Q(-0.052, -0.31), Q(-0.04, -0.302), Q(-0.042, -0.29), Q(-0.036, -0.282), Q(-0.034, -0.27),
                 Q(-0.02, -0.258), Q(0.01, -0.262), Q(0.03, -0.3), Q(0.025, -0.35)]
        g.append(f'<path d="{smooth_closed(face_)}" fill="{D.lin([(0, "#D8A088"), (1, "#8A5A48")], 0, 0, 1, 0)}"/>')
        g.append(soft(D, *Q(-0.03, -0.305), 3.5 * sc / 0.5, 3 * sc / 0.5, "#F2C0A0", 0.6))
        g.append(f'<path d="{blob(*Q(0.03, -0.31), 0.03 * W * sc, 0.035 * H * sc, seed + 5, 0.15, 10)}" fill="#4A3020"/>')
        # the hat
        g.append(f'<path d="{blob(*Q(0.0, -0.355), 0.13 * W * sc, 0.028 * H * sc, seed + 6, 0.05, 14, -5)}" fill="{hat}"/>')
        g.append(f'<path d="{blob(*Q(0.01, -0.385), 0.055 * W * sc, 0.035 * H * sc, seed + 7, 0.06, 12)}" fill="{hat}"/>')
        g.append(f'<path d="{blob(*Q(0.01, -0.362), 0.06 * W * sc, 0.012 * H * sc, seed + 8, 0.06, 10)}" fill="{hatband}"/>')
        if veil:
            v_ = [Q(0.02, -0.37), Q(0.12, -0.38), Q(0.24, -0.35), Q(0.3, -0.29), Q(0.2, -0.3), Q(0.1, -0.32)]
            g.append(f'<path d="{smooth_closed(v_)}" fill="#FFFFFF" opacity="0.82"/>')
        return "".join(g)
    # shadows on the sand
    paint.append(soft(D, X(0.5), Y(0.97), W * 0.3, H * 0.035, "#8A7AA8", 0.6))
    paint.append(soft(D, X(0.82), Y(0.92), W * 0.2, H * 0.03, "#8A7AA8", 0.5))
    paint.append(lady(0.8, 0.4, 0.8, 30, "#E8C878", "#C88A5A"))
    # the parasol, then the woman holding it
    pc = UV([(0.2, 0.22), (0.28, 0.1), (0.4, 0.06), (0.52, 0.1), (0.58, 0.2), (0.48, 0.18), (0.38, 0.2), (0.28, 0.2)])
    paint.append(f'<path d="{smooth_closed(pc)}" fill="{D.lin([(0, "#FFFFFF"), (0.6, "#F2F0EA"), (1, "#C8C0D8")], 0, 0, 0, 1)}"/>')
    for k in range(6):
        a_ = UV([(0.39, 0.065)])[0]
        b_ = UV([(0.22 + k * 0.07, 0.205)])[0]
        paint.append(f'<path d="M{a_[0]:.1f} {a_[1]:.1f}L{b_[0]:.1f} {b_[1]:.1f}" stroke="#C8C4D4" stroke-width="1.2" opacity="0.8"/>')
    paint.append(f'<path d="M{X(0.39):.1f} {Y(0.065):.1f}L{X(0.405):.1f} {Y(0.33):.1f}" stroke="#7A6A5A" stroke-width="1.6"/>')
    paint.append(lady(0.47, 0.44, 1.0, 40))
    paint.append(taper(UV([(0.44, 0.25), (0.415, 0.3), (0.405, 0.33)]), 9, 6, "#C8C8DC"))
    paint.append(f'<path d="{blob(X(0.405), Y(0.33), 4.5, 4, 3, 0.1, 8)}" fill="#C89878"/>')
    # sparkle of the sun on the foam and a scatter of loose, bright touches
    for k in range(40):
        x, y = X(rnd.uniform(0, 1)), Y(rnd.uniform(0.25, 0.46))
        B.dash([(x - 4, y), (x + 4, y)], "#FFFFFF", 2.2, 0.85)
    paint.append(B.render())
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.05)}{varnish(D, box, 0.1, 0.12, 6, 0.25)}</g>')
    out.append(museum_label(D, 502, "Walk on the Beach", "JOAQUÍN SOROLLA · 1909", "#3A3228", "#7A6A58", ts=29, bs=17, gap=27))
    return finish(D, out, 113)


# ================================================================ 27. The Scream — Munch, 1893
def band_strokes(B, line_fn, n_lines, t_range, cols, seed, w=(3, 6), jitter_=2.0, op=0.85, steps=24):
    """Long undulating strokes laid along a family of curves line_fn(k, t) -> (x, y), k in 0..1 across, t along."""
    rnd = random.Random(seed)
    for i in range(n_lines):
        k = i / max(1, n_lines - 1)
        t0 = rnd.uniform(t_range[0], t_range[0] + 0.2)
        t1 = rnd.uniform(t_range[1] - 0.2, t_range[1])
        pts = [line_fn(k + rnd.uniform(-0.01, 0.01), t0 + (t1 - t0) * j / steps) for j in range(steps + 1)]
        pts = [(x + rnd.uniform(-jitter_, jitter_) * 0.3, y + rnd.uniform(-jitter_, jitter_) * 0.3) for x, y in pts]
        col = cols(k, rnd) if callable(cols) else rnd.choice(cols)
        ww = rnd.uniform(*w)
        # split into short runs so colour can vary along the band
        for a in range(0, steps, 6):
            seg = pts[a:a + 7]
            if len(seg) >= 2:
                B.dash(seg[::2] if len(seg) > 4 else seg, col if rnd.random() < 0.7 else (cols(k, rnd) if callable(cols) else rnd.choice(cols)), ww, op)


@design("the-scream")
def the_scream():
    D = Doc("gmms")
    box = (150, 56, 450, 428)   # 300 x 372 (91 x 73.5 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [wall(D, "#2A3038", 251, (0.5, 0.15), 0.3)]
    out.append(simple_frame(D, box, 16, ("#6A5E50", "#2E2620", "#120E0A"), 3))
    out.append(f'<rect x="{x0 - 4}" y="{y0 - 4}" width="{W + 8}" height="{H + 8}" fill="none" stroke="#B8985A" stroke-width="2"/>')
    cp = clip_box(D, box)
    rnd = random.Random(5)
    B = Brush()
    paint = []
    # the screaming sky: bands of blood-orange, red and yellow, with streaks of blue-green
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.lin([(0, "#D8602A"), (0.25, "#E88A3A"), (0.45, "#C8402A")])}"/>')

    def sky_line(k, t):
        x = x0 - 20 + t * (W + 40)
        y = Y(0.02 + k * 0.42) + H * 0.035 * math.sin(t * 7 + k * 5) + H * 0.05 * math.sin(t * 2.5 + 1) * (1 - k * 0.5)
        return x, y

    def sky_cols(k, r):
        if 0.35 < k < 0.55 and r.random() < 0.45:
            return r.choice(["#F2D050", "#F6E070", "#E8B830"])
        if k > 0.7 and r.random() < 0.3:
            return r.choice(["#6A9A8A", "#5A8A9A", "#8AB0A0"])
        return r.choice(["#E8602A", "#D8402A", "#F2903A", "#C8301E", "#E87A2A", "#F2A040"])
    band_strokes(B, sky_line, 46, (0, 1), sky_cols, 3, w=(4, 7))
    paint.append(B.render())
    # the land and the fjord below, all swirling: dark blue water curving in from the right, green-black hills
    land = UV([(-0.02, 0.42), (0.2, 0.4), (0.4, 0.44), (0.6, 0.4), (0.8, 0.38), (1.02, 0.42), (1.02, 1.02), (-0.02, 1.02)])
    paint.append(f'<path d="{smooth_closed(land)}" fill="#2A3A4A"/>')

    def fjord_line(k, t):
        cx_, cy_ = X(0.72), Y(0.62)
        a = math.pi * (0.9 + 1.3 * t)
        r = W * (0.12 + 0.45 * k)
        return cx_ + r * math.cos(a) * 1.2, cy_ + r * math.sin(a) * 0.45

    band_strokes(B, fjord_line, 30, (0, 1), lambda k, r: r.choice(["#1E3A6A", "#2A4A8A", "#3A5A9A", "#14284A", "#4A6AA8"]) if k < 0.55 else
                 r.choice(["#2E4A3A", "#3A5A3A", "#1E3A2A", "#4A6A4A", "#5A4A3A", "#E8803A"]), 4, w=(4, 7))
    paint.append(f'<g {D.clip(f"<path d=\"{smooth_closed(land)}\"/>")}>{B.render()}</g>')
    # two boats on the fjord
    for u, v in ((0.66, 0.5), (0.74, 0.54)):
        paint.append(f'<path d="M{X(u) - 6:.1f} {Y(v):.1f}h12l-3 3h-6z" fill="#1A1A1A"/><path d="M{X(u):.1f} {Y(v):.1f}v-9" stroke="#1A1A1A" stroke-width="1"/>')
    # the bridge: its deck rushing diagonally from the near right corner away to the left
    deck = UV([(1.02, 0.86), (1.02, 1.02), (-0.02, 1.02), (-0.02, 0.5)])
    paint.append(f'<path d="{pd(deck)}" fill="#B8783A"/>')

    def deck_line(k, t):
        a = lerp((X(1.05), Y(0.88 + k * 0.16)), (X(-0.05), Y(0.48 + k * 0.18)), t)
        return a
    band_strokes(B, deck_line, 16, (0, 1), ["#C8864A", "#A86A30", "#D89A5A", "#8A5A2A", "#E8A060"], 6, w=(4, 6), steps=12)
    paint.append(f'<g {D.clip(f"<path d=\"{pd(deck)}\"/>")}>{B.render()}</g>')
    # the railing: three long rails converging on the far end, with posts
    for k, (dy0, dy1) in enumerate(((0.72, 0.4), (0.76, 0.43), (0.8, 0.46))):
        a, b = (X(1.04), Y(dy0)), (X(-0.04), Y(dy1))
        paint.append(f'<path d="M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}" stroke="#5A3A20" stroke-width="{4.5 - k:.1f}" stroke-linecap="round"/>')
        paint.append(f'<path d="M{a[0]:.1f} {a[1] - 1.5:.1f}L{b[0]:.1f} {b[1] - 1:.1f}" stroke="#E8A060" stroke-width="1.2" opacity="0.6"/>')
    for k in range(9):
        t = (k / 8) ** 1.6
        a = lerp((X(1.04), Y(0.72)), (X(-0.04), Y(0.4)), t)
        b = lerp((X(1.04), Y(0.9)), (X(-0.04), Y(0.5)), t)
        paint.append(f'<path d="M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}" stroke="#4A2E18" stroke-width="{max(1.2, 3.6 * (1 - t)):.1f}"/>')
    # the two strollers at the far end of the bridge
    for k, u in enumerate((0.1, 0.17)):
        fx, fy = X(u), Y(0.46 + k * 0.012)
        paint.append(f'<path d="{smooth_closed([(fx - 4, fy), (fx - 3, fy - 16), (fx, fy - 20), (fx + 3, fy - 16), (fx + 4, fy)])}" fill="#141418"/>'
                     f'<circle cx="{fx:.1f}" cy="{fy - 22:.1f}" r="3.2" fill="#141418"/><path d="M{fx - 5:.1f} {fy - 24:.1f}h10" stroke="#141418" stroke-width="2"/>')
    # the figure: a sinuous dark body and a pale, skull-like head clasped in its hands
    body = UV([(0.3, 1.04), (0.33, 0.88), (0.38, 0.76), (0.44, 0.69), (0.5, 0.66), (0.58, 0.69), (0.62, 0.78), (0.6, 0.9), (0.66, 1.04)])
    bd = smooth_closed(body)
    paint.append(f'<path d="{bd}" fill="#1E2430"/>')
    band_strokes(B, lambda k, t: (lerp(UV([(0.4 + k * 0.17, 1.04)])[0], UV([(0.46 + k * 0.08, 0.76)])[0], t)[0] + 6 * math.sin(t * 6 + k * 3),
                                  lerp(UV([(0.4 + k * 0.17, 1.04)])[0], UV([(0.46 + k * 0.08, 0.76)])[0], t)[1]), 9, (0, 1),
                 ["#2A3448", "#141820", "#3A4458", "#24283A"], 7, w=(3, 5), steps=12)
    paint.append(f'<g {D.clip(f"<path d=\"{bd}\"/>")}>{B.render()}</g>')
    hx, hy = X(0.5), Y(0.6)
    k_ = 1.35
    head = [(hx + x * k_, hy + y * k_) for x, y in ((-16, -6), (-13, -22), (0, -28), (13, -22), (16, -6), (11, 14), (4, 24), (-4, 24), (-11, 14))]
    hd = smooth_closed(head)
    paint.append(f'<path d="{hd}" fill="{D.rad([(0, "#E8D8A0"), (0.6, "#C8B880"), (1, "#8A8050")], 0.45, 0.4, 0.65)}"/>')
    # hands pressed to the cheeks, arms rising from the body
    for sg in (-1, 1):
        paint.append(taper([(hx + sg * 26, hy + 62), (hx + sg * 30, hy + 34), (hx + sg * 21, hy + 4)], 13, 9, "#232A38"))
        paint.append(f'<path d="{blob(hx + sg * 20, hy + 2, 7, 12, 3 + sg, 0.12, 10, sg * 10)}" fill="#C8B880" stroke="#5A5030" stroke-width="0.9"/>')
    # eyes: dark staring hollows; nostril slits; the open oval mouth
    for sg in (-1, 1):
        paint.append(f'<path d="{blob(hx + sg * 8, hy - 12, 5, 6.5, 7 + sg, 0.12, 10)}" fill="#3A3420"/>')
        paint.append(f'<path d="{blob(hx + sg * 8.5, hy - 11, 2.4, 3.2, 9 + sg, 0.12, 8)}" fill="#E8E0B8" opacity="0.5"/>')
        paint.append(f'<ellipse cx="{hx + sg * 3:.1f}" cy="{hy + 4:.1f}" rx="1.2" ry="2" fill="#3A3420"/>')
    paint.append(f'<path d="{blob(hx, hy + 18, 6, 10, 13, 0.08, 10)}" fill="#2A2418" stroke="#5A5030" stroke-width="0.8"/>')
    paint.append(f'<path d="{hd}" fill="none" stroke="#4A4428" stroke-width="1.3"/>')
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.06)}{varnish(D, box, 0.08, 0.2, 6, 0.3)}</g>')
    out.append(museum_label(D, 486, "The Scream", "EDVARD MUNCH · 1893", "#F2E6D4", "#C8B8A0", ts=34, bs=18, gap=32))
    return finish(D, out, 117)


# ================================================================ 28. Spring (The Seasons) — Mucha, 1896
def lock(pts, w0, w1, fill, line="#4A3420"):
    """One outlined lock of Art Nouveau hair."""
    return taper(pts, w0 + 2.2, w1 + 1.4, line) + taper(pts, w0, w1, fill)


def mu_xf(ox, oy, s, rot):
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return lambda pts: [(ox + (x * c - y * sn) * s, oy + (x * sn + y * c) * s) for x, y in pts]


def mu_line(pts, w, col, op=1.0, closed=False):
    d = smooth_closed(pts) if closed else smooth_open(pts)
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w:.2f}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>'


def mu_flower(x, y, r, rot, petal, line, centre="#E8B848", shade=None):
    """A five-petalled blossom drawn the Art Nouveau way: crisp outline, flat petal colour, a tinted heart."""
    out = []
    for i in range(5):
        a = math.radians(rot + 72 * i)
        px, py = x + r * 0.55 * math.cos(a), y + r * 0.55 * math.sin(a)
        pts = blob_pts(px, py, r * 0.5, r * 0.4, int(x * 7 + y * 3 + i), 0.04, 10, rot + 72 * i)
        out.append(f'<path d="{smooth_closed(pts)}" fill="{petal}" stroke="{line}" stroke-width="0.9"/>')
    if shade:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.5:.1f}" fill="{shade}" opacity="0.55"/>')
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.22:.1f}" fill="{centre}" stroke="{line}" stroke-width="0.6"/>')
    return "".join(out)


def mu_leaf(x, y, L, ang, fill, line, vein=None):
    a = math.radians(ang)
    tip = (x + L * math.cos(a), y + L * math.sin(a))
    nx, ny = -math.sin(a) * L * 0.3, math.cos(a) * L * 0.3
    m = ((x + tip[0]) / 2, (y + tip[1]) / 2)
    d = f"M{x:.1f} {y:.1f}Q{m[0] + nx:.1f} {m[1] + ny:.1f} {tip[0]:.1f} {tip[1]:.1f}Q{m[0] - nx:.1f} {m[1] - ny:.1f} {x:.1f} {y:.1f}Z"
    out = f'<path d="{d}" fill="{fill}" stroke="{line}" stroke-width="0.9"/>'
    if vein:
        out += f'<path d="M{x:.1f} {y:.1f}Q{m[0] + nx * 0.2:.1f} {m[1] + ny * 0.2:.1f} {tip[0]:.1f} {tip[1]:.1f}" stroke="{vein}" stroke-width="0.7" fill="none"/>'
    return out


def mu_bird(x, y, s, flip=1, body="#C8B89A", line="#5A3A28"):
    """A small songbird perched, Art Nouveau outline."""
    f = flip
    pts = [(x - 7 * s * f, y + 1 * s), (x - 3 * s * f, y - 4 * s), (x + 2 * s * f, y - 5 * s), (x + 5 * s * f, y - 8 * s), (x + 8 * s * f, y - 8 * s),
           (x + 10 * s * f, y - 6.5 * s), (x + 12.5 * s * f, y - 6 * s), (x + 10 * s * f, y - 5 * s), (x + 9 * s * f, y - 2 * s), (x + 5 * s * f, y + 2 * s),
           (x - 1 * s * f, y + 3 * s), (x - 9 * s * f, y + 6 * s), (x - 12 * s * f, y + 6 * s)]
    out = [f'<path d="{smooth_closed(pts)}" fill="{body}" stroke="{line}" stroke-width="1"/>']
    out.append(f'<path d="M{x - 4 * s * f:.1f} {y - 1 * s:.1f}Q{x + 2 * s * f:.1f} {y - 3 * s:.1f} {x + 5 * s * f:.1f} {y + 0.5 * s:.1f}" stroke="{line}" stroke-width="0.8" fill="none"/>')
    out.append(f'<path d="M{x + 3 * s * f:.1f} {y - 3.5 * s:.1f}Q{x + 6 * s * f:.1f} {y - 1 * s:.1f} {x + 8 * s * f:.1f} {y - 2 * s:.1f}" stroke="#E8D8B8" stroke-width="1.6" fill="none" opacity="0.8"/>')
    out.append(f'<circle cx="{x + 8.6 * s * f:.1f}" cy="{y - 6.8 * s:.1f}" r="{0.8 * s:.1f}" fill="#2A1A10"/>')
    out.append(f'<path d="M{x + 1 * s * f:.1f} {y + 2.5 * s:.1f}l{0.5 * s * f:.1f} {3 * s:.1f}M{x + 3 * s * f:.1f} {y + 2 * s:.1f}l{0.5 * s * f:.1f} {3.2 * s:.1f}" stroke="{line}" stroke-width="0.8"/>')
    return "".join(out)


@design("spring-mucha")
def mucha_spring():
    D = Doc("gmmu")
    box = (150, 50, 450, 452)   # 300 x 402 decorative panel
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H
    LINE = "#5A3A28"
    out = [wall(D, "#E2D6C0", 271, (0.5, 0.2), 0.15)]
    out.append(simple_frame(D, box, 10, ("#E8D4A0", "#B8964A", "#6A5020"), 3))
    cp = clip_box(D, box)
    rnd = random.Random(7)
    P = [f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="#EFE6D0"/>']
    bx0, by0, bx1, by1 = x0 + 9, y0 + 9, x1 - 9, y1 - 9
    # ---- the pictorial field: a pale spring sky, sage at the foot, arched at the top
    fx0, fy0, fx1, fy1 = bx0 + 7, by0 + 7, bx1 - 7, Y(0.835)
    arch = f"M{fx0} {fy1}V{fy0 + 40}Q{fx0} {fy0} {fx0 + 40} {fy0}H{fx1 - 40}Q{fx1} {fy0} {fx1} {fy0 + 40}V{fy1}Z"
    P.append(f'<path d="{arch}" fill="{D.lin([(0, "#F2EEDA"), (0.55, "#E4E8CC"), (1, "#C8D4A8")])}"/>')
    fcl = D.clip(f'<path d="{arch}"/>')
    bg = []
    # flowering branches reaching in from both sides, a pair of songbirds
    for k, (sx_, sy_, ang, L) in enumerate([(fx0 - 4, Y(0.18), -18, 120), (fx1 + 4, Y(0.12), 200, 120), (fx0 - 4, Y(0.5), -35, 95), (fx1 + 4, Y(0.46), 215, 100)]):
        segs = []
        branch_tree(random.Random(70 + k), sx_, sy_, math.radians(ang), L, 4.2, 2, segs, 14)
        for pts, w0, w1 in segs:
            bg.append(taper(pts, w0 + 1.6, max(1.4, w1 + 1.2), LINE))
            bg.append(taper(pts, w0, max(0.6, w1), "#9A7A58"))
        for pts, w0, w1 in segs:
            for j, (px, py) in enumerate(pts[1:]):
                if rnd.random() < 0.75:
                    bg.append(mu_flower(px + rnd.uniform(-3, 3), py + rnd.uniform(-3, 3), rnd.uniform(5.5, 7.5), rnd.uniform(0, 72),
                                        rnd.choice(["#FFFFFF", "#FBEFF0", "#F6DDE2"]), "#9A7A70", "#E8B848", "#F2B8C4"))
                elif rnd.random() < 0.5:
                    bg.append(mu_leaf(px, py, 9, rnd.uniform(0, 360), "#A8BC88", "#6A7A50"))
    bg.append(mu_bird(fx0 + 34, Y(0.205), 1.25, 1))
    bg.append(mu_bird(fx1 - 30, Y(0.15), 1.15, -1, "#B8C0A8"))
    P.append(f'<g {fcl}>{"".join(bg)}</g>')
    P.append(f'<path d="{arch}" fill="none" stroke="{LINE}" stroke-width="2"/>')

    # ---- the halo: a great disc of rings, beads and a lattice of blossoms
    hx, hy = X(0.5), Y(0.33)
    R = W * 0.37
    halo = [f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{R:.1f}" fill="{D.rad([(0, "#FBF6E6"), (0.7, "#F2E8C8"), (1, "#E2D2A2")])}" stroke="{LINE}" stroke-width="2"/>']
    halo.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{R - 7:.1f}" fill="none" stroke="#C8A860" stroke-width="3.5"/>')
    halo.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{R - 7:.1f}" fill="none" stroke="#F6E8B8" stroke-width="1" />')
    halo.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{R - 12:.1f}" fill="none" stroke="{LINE}" stroke-width="1.2"/>')
    for k in range(36):
        a = 2 * math.pi * k / 36
        px, py = hx + (R - 18) * math.cos(a), hy + (R - 18) * math.sin(a)
        halo.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{3.3 if k % 2 else 2.2}" fill="{"#B8C890" if k % 2 else "#D8B868"}" stroke="{LINE}" stroke-width="0.8"/>')
    halo.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{R - 24:.1f}" fill="none" stroke="{LINE}" stroke-width="1"/>')
    for k in range(12):
        a = 2 * math.pi * (k + 0.5) / 12
        c1 = (hx + (R - 24) * math.cos(a - 0.26), hy + (R - 24) * math.sin(a - 0.26))
        c2 = (hx + (R - 24) * math.cos(a + 0.26), hy + (R - 24) * math.sin(a + 0.26))
        tip = (hx + (R - 52) * math.cos(a), hy + (R - 52) * math.sin(a))
        halo.append(f'<path d="M{c1[0]:.1f} {c1[1]:.1f}Q{tip[0]:.1f} {tip[1]:.1f} {c2[0]:.1f} {c2[1]:.1f}" fill="none" stroke="#C8A860" stroke-width="1.4"/>')
        halo.append(mu_flower(hx + (R - 30) * math.cos(a), hy + (R - 30) * math.sin(a), 4.2, math.degrees(a), "#FFFFFF", "#A88A6A", "#E8B848"))
    P.append("".join(halo))

    # ---- the figure. Head in three-quarter view, inclined to our left, eyes lowered.
    T = mu_xf(hx - 2, hy + 4, 1.0, -9)
    HAIR, HAIR_D, HAIR_L = "#E0A858", "#A86A2E", "#F6D896"
    SKIN, SKIN_SH, BLUSH = "#FCEADC", "#EEC6B2", "#F09A9A"

    def hair_mass(pts, seed, flow):
        """A lobe of hair: honey fill, long strand lines following `flow` (list of curves), a sheen, brown contour."""
        d = smooth_closed(pts)
        c = D.clip(f'<path d="{d}"/>')
        r_ = random.Random(seed)
        inner = []
        for crv in flow:
            pts_ = T(catmull_pts(crv, 6))
            inner.append(f'<path d="{smooth_open(pts_)}" stroke="{r_.choice([HAIR_D, LINE, "#C08440"])}" stroke-width="{r_.uniform(0.7, 1.3):.1f}" fill="none" opacity="0.8"/>')
            if r_.random() < 0.4:
                inner.append(f'<path d="{smooth_open([(x_ + 2.5, y_) for x_, y_ in pts_])}" stroke="{HAIR_L}" stroke-width="{r_.uniform(1.6, 3):.1f}" fill="none" opacity="0.6"/>')
        return f'<path d="{d}" fill="{HAIR}"/><g {c}>{"".join(inner)}</g><path d="{d}" fill="none" stroke="{LINE}" stroke-width="1.9"/>'

    # whiplash ribbons of hair escaping over the halo, each a bundle of fine strands curling at the end
    whips = []
    for k, (sg, st, md, cc, r0, tw) in enumerate([(-1, (-56, 30), (-96, 50), (-102, 90), 8, 1.2), (-1, (-62, 62), (-86, 94), (-66, 120), 6, 1.0),
                                                   (1, (56, 26), (96, 38), (108, 76), 8, 1.25), (1, (66, 64), (94, 98), (82, 126), 6, 1.0),
                                                   ]):
        for j in range(3):
            off = (j - 1) * 3.2
            sp = spiral_pts(*T([(cc[0] + off * sg, cc[1] + off)])[0], r0 + j * 1.5, tw, 1.3 + k, sg, 22)
            pts = catmull_pts(T([(st[0], st[1] + off), (md[0], md[1] + off * 1.4)]) + [sp[0]], 6) + sp[1:]
            whips.append(taper(pts, 4.6, 1.6, LINE))
            whips.append(taper(pts, 3.0, 0.6, [HAIR, HAIR_L, "#D29A4A"][j]))
    P.append("".join(whips))
    # the great mass of hair behind the head
    back = T([(-40, -50), (-34, -72), (-12, -86), (16, -86), (40, -72), (52, -44), (56, -10), (60, 24), (70, 56), (84, 84), (78, 106), (58, 98), (44, 72),
              (36, 46), (-34, 46), (-44, 72), (-60, 98), (-82, 106), (-88, 84), (-68, 56), (-58, 24), (-53, -10), (-48, -32)])
    flow = []
    for k in range(24):
        sg = -1 if k % 2 else 1
        j = k // 2
        flow.append([(sg * (3 + j * 1.6), -84), (sg * (34 + j * 1.6), -58 + j), (sg * (46 + j * 1.0), -10 + j * 1.5), (sg * (52 + j * 1.2), 30 + j * 2), (sg * (58 + j * 2.2), 96 + j)])
    P.append(hair_mass(back, 11, flow))
    # gown, neck and shoulders
    gown = T([(-92, 214), (-96, 150), (-82, 106), (-50, 86), (-16, 80), (12, 90), (36, 82), (64, 90), (90, 116), (100, 170), (98, 214)])
    gd = smooth_closed(gown)
    P.append(f'<path d="{gd}" fill="{D.lin([(0, "#FFFCF4"), (0.6, "#F4ECDC"), (1, "#DCCCB0")], 0, 0, 1, 0.3)}" stroke="{LINE}" stroke-width="2"/>')
    folds = []
    for k in range(12):
        t = k / 11
        a_ = T([(-78 + t * 168, 108 + abs(t - 0.45) * 30)])[0]
        c1 = T([(-82 + t * 172 + (t - 0.5) * 30 + 10, 140)])[0]
        c2 = T([(-88 + t * 182 + (t - 0.5) * 34 - 8, 180)])[0]
        b_ = T([(-92 + t * 190 + (t - 0.5) * 24, 216)])[0]
        folds.append(f'<path d="M{a_[0]:.1f} {a_[1]:.1f}C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {b_[0]:.1f} {b_[1]:.1f}" stroke="#D8CAB0" stroke-width="4" fill="none" opacity="0.8"/>')
        folds.append(f'<path d="M{a_[0] - 2:.1f} {a_[1]:.1f}C{c1[0] - 2:.1f} {c1[1]:.1f} {c2[0] - 2:.1f} {c2[1]:.1f} {b_[0] - 2:.1f} {b_[1]:.1f}" stroke="{LINE}" stroke-width="1" fill="none" opacity="0.55"/>')
    P.append(f'<g {D.clip(f"<path d=\"{gd}\"/>")}>{"".join(folds)}</g>')
    neck = T([(-8, 46), (-10, 66), (-13, 86), (26, 88), (27, 66), (26, 38)])
    nd = smooth_closed(neck)
    P.append(f'<path d="{nd}" fill="{D.lin([(0, SKIN), (0.55, SKIN), (1, SKIN_SH)], 0, 0, 1, 0)}" stroke="{LINE}" stroke-width="1.6"/>')
    P.append(f'<g {D.clip(f"<path d=\"{nd}\"/>")}>{soft(D, *T([(8, 50)])[0], 26, 12, "#D8A898", 0.7)}</g>')
    # embroidered neckline, a little green brooch
    nl = T([(-50, 86), (-22, 96), (6, 101), (36, 95), (64, 89)])
    P.append(taper(nl, 7, 7, LINE))
    P.append(taper(nl, 4.8, 4.8, "#B8C890"))
    for t_ in range(1, 12):
        px, py = catmull_pts(nl, 4)[t_ * 16 // 12]
        P.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.3" fill="#F6EED0"/>')
    bp = T([(6, 104)])[0]
    P.append(f'<ellipse cx="{bp[0]:.1f}" cy="{bp[1]:.1f}" rx="6" ry="7.5" fill="#6A9A7A" stroke="{LINE}" stroke-width="1.4"/><ellipse cx="{bp[0] - 1.6:.1f}" cy="{bp[1] - 2.4:.1f}" rx="1.8" ry="2.2" fill="#E8F2E0"/>')
    P.append(f'<path d="M{bp[0] - 3:.1f} {bp[1] + 7:.1f}q3 9 -2 16M{bp[0] + 3:.1f} {bp[1] + 7:.1f}q-1 10 4 15" stroke="#C8A860" stroke-width="1.6" fill="none"/>')
    garland = T(catmull_pts([(-84, 130), (-50, 150), (-10, 156), (30, 146), (64, 128), (92, 112)], 5))
    P.append(taper(garland, 2.6, 2.6, "#6A8A4A"))
    for i, (gx_, gy_) in enumerate(garland[1:-1]):
        if i % 2:
            P.append(mu_leaf(gx_, gy_, 11, rnd.choice([60, 120, -60, 240]), "#9AB47A", "#5A6A40", "#C8D8A8"))
        else:
            P.append(mu_flower(gx_, gy_ + rnd.uniform(-2, 2), rnd.uniform(6, 8), i * 23, ["#FFFFFF", "#F8DCE2", "#FFF4D8"][i % 3], "#8A6A60", "#E8B848", "#F2C0CC"))
    # ---- the face, modelled with soft glazes under a fine contour
    face = T([(-26, -36), (-30, -20), (-31, -8), (-28.5, 0), (-30.5, 10), (-28, 24), (-22, 36), (-14, 47), (-6, 51), (5, 48.5), (18, 40), (30, 24), (36, 2),
              (37, -20), (30, -38), (2, -46)])
    fd = smooth_closed(face)
    P.append(f'<path d="{fd}" fill="{SKIN}"/>')
    sh = []
    sh.append(soft(D, *T([(33, 8)])[0], 16, 36, SKIN_SH, 0.95))
    sh.append(soft(D, *T([(14, 44)])[0], 18, 9, SKIN_SH, 0.8))
    sh.append(soft(D, *T([(8, 22)])[0], 14, 9, BLUSH, 0.55))
    sh.append(soft(D, *T([(-24, 18)])[0], 6, 8, BLUSH, 0.4))
    sh.append(soft(D, *T([(-12, 45)])[0], 7, 4, BLUSH, 0.3))
    sh.append(soft(D, *T([(-8, -24)])[0], 24, 12, "#FFFFFF", 0.7))
    sh.append(soft(D, *T([(-18, 6)])[0], 5, 14, "#FFFFFF", 0.5))
    sh.append(soft(D, *T([(-14, 9)])[0], 3.5, 9, SKIN_SH, 0.7))
    sh.append(soft(D, *T([(-22, -3)])[0], 8, 5, SKIN_SH, 0.6))
    sh.append(soft(D, *T([(8, -3)])[0], 13, 6, SKIN_SH, 0.6))
    P.append(f'<g {D.clip(f"<path d=\"{fd}\"/>")}>{"".join(sh)}</g>')
    P.append(f'<path d="{fd}" fill="none" stroke="{LINE}" stroke-width="1.7"/>')
    # brows
    P.append(taper(T([(-28, -10.5), (-22, -13), (-15, -12)]), 1.5, 0.5, "#9A6A40"))
    P.append(taper(T([(-6, -12.5), (6, -14.5), (19, -10)]), 1.8, 0.6, "#9A6A40"))
    # eyes lowered: the heavy upper lid, a crescent of iris beneath it, a soft lower lid, the fold above
    for (ex, w, k) in ((-21.5, 5.5, 0.7), (7, 10.5, 1.0)):
        lid = T([(ex - w, 0.8), (ex - w * 0.4, -1.4), (ex + w * 0.35, -1.5), (ex + w, 0.2)])
        low = T([(ex - w * 0.7, 2.0), (ex, 3.2), (ex + w * 0.75, 1.8)])
        ed = smooth_closed(lid + low[::-1])
        P.append(f'<path d="{ed}" fill="#F8F0EA"/>')
        P.append(f'<g {D.clip(f"<path d=\"{ed}\"/>")}><circle cx="{T([(ex + 0.6, 2.9)])[0][0]:.1f}" cy="{T([(ex + 0.6, 2.9)])[0][1]:.1f}" r="{3.6 * k + 0.6:.1f}" fill="#5E7E92"/>'
                 f'<circle cx="{T([(ex + 0.6, 3.2)])[0][0]:.1f}" cy="{T([(ex + 0.6, 3.2)])[0][1]:.1f}" r="{1.5 * k + 0.3:.1f}" fill="#1E1E28"/>'
                 f'<path d="{ed}" fill="none" stroke="#C8A090" stroke-width="2.4" opacity="0.6"/></g>')
        P.append(taper(lid + T([(ex + w + 1.6, -0.8)]), 1.0, 2.2 * k + 0.2, "#3A2418"))
        P.append(mu_line(low[1:], 0.7, "#B88A78", 0.8))
        P.append(mu_line(T([(ex - w * 0.7, -4.6), (ex, -6.2), (ex + w * 0.85, -4.2)]), 0.85, "#C08A70", 0.8))
    # nose: the line of the bridge against the far cheek, the nostril's curl
    P.append(mu_line(T([(-12, -5), (-14.5, 4), (-18, 12), (-20.5, 17), (-19.5, 19.8), (-16.5, 20.2)]), 1.2, LINE, 0.85))
    P.append(mu_line(T([(-12.5, 20.2), (-9.5, 20.6), (-8, 18.6)]), 1.0, LINE, 0.7))
    P.append(soft(D, *T([(-12.5, 22.5)])[0], 6, 1.8, "#C8907A", 0.45))
    # mouth: a small closed rosebud
    up = T([(-21, 30.4), (-16, 28.2), (-12.5, 29.2), (-9, 28.2), (-3.5, 30), (-10, 31.6), (-16, 31.6)])
    lo = T([(-19, 31.2), (-12, 31.8), (-5, 30.8), (-8, 34.8), (-13, 35.6), (-17, 34.2)])
    P.append(f'<path d="{smooth_closed(lo)}" fill="#E48E88"/><path d="{smooth_closed(up)}" fill="#C8625E"/>')
    P.append(mu_line(T([(-21, 30.6), (-12, 31.5), (-3.5, 30.2)]), 1.0, "#7A3A30"))
    P.append(soft(D, *T([(-12, 33.4)])[0], 3, 1.1, "#FFFFFF", 0.75))
    # ---- front hair: parted in the middle, swept low over the temples and down past the cheeks
    lf = [[(-2, -46), (-22, -40), (-34, -22), (-38, 4), (-44, 34)], [(-6, -44), (-26, -34), (-36, -14), (-40, 12), (-46, 36)],
          [(-10, -42), (-30, -28), (-38, -6), (-41, 20)], [(0, -44), (-18, -44), (-32, -30), (-42, -6), (-46, 28)]]
    rf = [[(2, -46), (22, -42), (36, -24), (42, 4), (48, 34)], [(6, -44), (28, -36), (40, -16), (44, 12), (50, 36)],
          [(10, -42), (32, -28), (42, -6), (46, 22)], [(0, -44), (18, -46), (34, -32), (46, -6), (52, 26)]]
    P.append(hair_mass(T([(0, -52), (0, -37), (-10, -38), (-22, -33), (-31, -20), (-35, -2), (-34, 18), (-40, 34), (-48, 40), (-48, 14), (-46, -14), (-38, -38), (-20, -54)]), 21, lf))
    P.append(hair_mass(T([(0, -52), (20, -56), (40, -44), (50, -18), (54, 10), (56, 38), (48, 40), (40, 24), (40, 4), (36, -18), (27, -32), (12, -38), (0, -37)]), 22, rf))
    # wreath of spring blossoms and leaves across the crown
    wreath = []
    for k in range(14):
        t = k / 13
        a = math.radians(192 + t * 156)
        px, py = T([(2 + 52 * math.cos(a), -22 + 38 * math.sin(a))])[0]
        if k % 3 != 1:
            wreath.append(mu_leaf(px, py, 12, math.degrees(a) + rnd.choice([-75, 75]), "#9AB47A", "#5A6A40", "#C8D8A8"))
    for k in range(11):
        t = k / 10
        a = math.radians(196 + t * 148)
        px, py = T([(2 + 50 * math.cos(a), -24 + 36 * math.sin(a))])[0]
        wreath.append(mu_flower(px, py, 7.8 if k % 2 else 6.4, k * 17, "#FFFFFF" if k % 3 else "#F8DCE2", "#8A6A60", "#E8B848", "#F2C0CC"))
    for k, (u_, v_) in enumerate([(-50, -6), (52, -10)]):
        px, py = T([(u_, v_)])[0]
        wreath.append(mu_flower(px, py, 8.5, k * 30, "#FFFFFF", "#8A6A60", "#E8B848", "#F2C0CC"))
        wreath.append(mu_leaf(px, py + 6, 12, 100 if k else 80, "#9AB47A", "#5A6A40", "#C8D8A8"))
    P.append("".join(wreath))
    # ---- lower panel: the cartouche with the season's name, flanked by blossoms
    cy0 = Y(0.86)
    P.append(f'<rect x="{bx0 + 6}" y="{cy0:.1f}" width="{bx1 - bx0 - 12}" height="{by1 - cy0 - 6:.1f}" fill="{D.lin([(0, "#D8C898"), (1, "#C0AC78")])}" stroke="{LINE}" stroke-width="1.6"/>')
    P.append(f'<rect x="{bx0 + 11}" y="{cy0 + 5:.1f}" width="{bx1 - bx0 - 22}" height="{by1 - cy0 - 16:.1f}" fill="none" stroke="#F2E8D0" stroke-width="1"/>')
    P.append(label(X(0.5), cy0 + (by1 - cy0 - 6) / 2 + 9, "PRINTEMPS", CINZEL, 26, LINE, 6, W - 90))
    for sx_ in (bx0 + 24, bx1 - 24):
        P.append(mu_flower(sx_, cy0 + (by1 - cy0 - 6) / 2, 7, 10, "#FFFFFF", "#8A6A60", "#E8B848", "#F2C0CC"))
    # the panel border: double rule with mitred corner rosettes
    P.append(f'<rect x="{bx0}" y="{by0}" width="{bx1 - bx0}" height="{by1 - by0}" fill="none" stroke="{LINE}" stroke-width="2"/>')
    P.append(f'<rect x="{bx0 + 4}" y="{by0 + 4}" width="{bx1 - bx0 - 8}" height="{by1 - by0 - 8}" fill="none" stroke="#A8925A" stroke-width="1.2"/>')
    out.append(f'<g {cp}>{"".join(P)}</g>')
    out.append(museum_label(D, 490, "Spring, from The Seasons", "ALPHONSE MUCHA · 1896", "#3A2E22", "#6A5A44", ts=27, bs=17, gap=27, max_w=440))
    return finish(D, out, 131)


# ================================================================ 29. The Bedroom — Van Gogh, 1888
def flat_impasto(B, poly, n, cols, seed, angle, L=(8, 14), W=(3, 4.4), ridge=0.3, jit=0.12):
    """Van Gogh's flat colour areas: dense parallel impasto in one direction."""
    impasto(B, lambda x, y: math.radians(angle), poly, n, lambda x, y, r: r.choice(cols), seed, L=L, W=W, ridge=ridge, steps=1, jit=jit)


@design("the-bedroom")
def bedroom():
    D = Doc("gmbr")
    box = (66, 64, 534, 430)   # 468 x 366 (72 x 90 cm)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H

    def UV(pts):
        return [(X(u), Y(v)) for u, v in pts]
    out = [wall(D, "#5A4A3E", 291, (0.5, 0.15), 0.3)]
    out.append(simple_frame(D, box, 18, ("#E8D8B8", "#B8A07A", "#6A5838"), 3))
    out.append(f'<rect x="{x0 - 4}" y="{y0 - 4}" width="{W + 8}" height="{H + 8}" fill="none" stroke="#3A2A1A" stroke-width="2"/>')
    cp = clip_box(D, box)
    B = Brush()
    rnd = random.Random(4)
    paint = []

    def area(poly, base, cols, seed, angle, n=None, **kw):
        d = pd(poly)
        A = abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(poly, poly[1:] + poly[:1]))) / 2
        paint.append(f'<path d="{d}" fill="{base}"/>')
        flat_impasto(B, poly, n or int(A / 22) + 10, cols, seed, angle, **kw)
        paint.append(f'<g {D.clip(f"<path d=\"{d}\"/>")}>{B.render()}</g>')
        paint.append(f'<path d="{d}" fill="none" stroke="#2A2A3A" stroke-width="2.2" stroke-linejoin="round"/>')
    # the room in its tilted perspective: back wall violet-blue, side walls paler blue
    back = UV([(0.24, -0.02), (0.78, -0.02), (0.76, 0.56), (0.28, 0.58)])
    left = UV([(-0.02, -0.02), (0.24, -0.02), (0.28, 0.58), (-0.02, 0.78)])
    right = UV([(0.78, -0.02), (1.02, -0.02), (1.02, 0.86), (0.76, 0.56)])
    floor = UV([(-0.02, 0.78), (0.28, 0.58), (0.76, 0.56), (1.02, 0.86), (1.02, 1.02), (-0.02, 1.02)])
    area(back, "#8A9AC8", ["#9AA8D0", "#8A98C8", "#A8B4D8", "#7A8AB8", "#B0B8DC"], 1, -90)
    area(left, "#A8B8D8", ["#B8C4E0", "#A8B8D8", "#C8D2E8", "#98A8CC"], 2, -80)
    area(right, "#98A8D0", ["#A8B4D8", "#98A8D0", "#B8C4E0", "#8898C4"], 3, -100)
    # the floor: reddish boards running toward the window, green-tinged
    paint.append(f'<path d="{pd(floor)}" fill="#C8906A"/>')
    vp = (X(0.52), Y(0.2))
    impasto(B, lambda x, y: math.atan2(vp[1] - y, vp[0] - x), floor, 700,
            lambda x, y, r: r.choice(["#D8A070", "#C88A5A", "#B87A50", "#A8A060", "#E0B080", "#9A8A58"]), 4, L=(10, 18), W=(3, 4.4), ridge=0.3, steps=1, jit=0.05)
    paint.append(f'<g {D.clip(f"<path d=\"{pd(floor)}\"/>")}>{B.render()}</g>')
    # the window on the back wall, green shutters ajar
    win = UV([(0.42, 0.06), (0.6, 0.06), (0.6, 0.38), (0.42, 0.38)])
    area(win, "#7AA868", ["#8AB878", "#6A9A5A", "#A8C890", "#5A8A4A"], 5, -90, 120)
    paint.append(f'<path d="M{X(0.51):.1f} {Y(0.06):.1f}V{Y(0.38):.1f}M{X(0.42):.1f} {Y(0.22):.1f}H{X(0.6):.1f}" stroke="#2A2A3A" stroke-width="1.8"/>')
    for k in range(4):
        paint.append(f'<path d="M{X(0.43 + (k % 2) * 0.09):.1f} {Y(0.08 + (k // 2) * 0.16):.1f}h{W * 0.07:.1f}v{H * 0.12:.1f}h{-W * 0.07:.1f}z" fill="#C8E0B0" opacity="0.6"/>')
    # pictures on the walls: a landscape and two portraits (as small dabbed frames), a mirror and towel
    for (u, v, w_, h_, col) in ((0.3, 0.06, 0.08, 0.12, "#C8B060"), (0.66, 0.08, 0.06, 0.1, "#8A6A3A"), (0.7, 0.2, 0.06, 0.1, "#6A8A5A")):
        r_ = UV([(u, v), (u + w_, v), (u + w_, v + h_), (u, v + h_)])
        paint.append(f'<path d="{pd(r_)}" fill="{col}" stroke="#4A2A10" stroke-width="2.4"/>')
        paint.append(f'<path d="{blob(X(u + w_ / 2), Y(v + h_ / 2), W * w_ * 0.25, H * h_ * 0.3, int(u * 100), 0.2, 8)}" fill="{lt(col, 0.3)}"/>')
    paint.append(f'<path d="{pd(UV([(0.1, 0.12), (0.18, 0.13), (0.18, 0.3), (0.1, 0.32)]))}" fill="#C8B888" stroke="#4A2A10" stroke-width="2"/>')
    paint.append(f'<path d="{pd(UV([(0.05, 0.36), (0.1, 0.35), (0.1, 0.5), (0.05, 0.52)]))}" fill="#7AA868" stroke="#2A2A3A" stroke-width="1.6"/>')
    # pegs with clothes on the right wall
    paint.append(f'<path d="M{X(0.85):.1f} {Y(0.18):.1f}L{X(0.98):.1f} {Y(0.16):.1f}" stroke="#6A4A2A" stroke-width="3"/>')
    paint.append(f'<path d="{blob(X(0.9), Y(0.28), 10, 18, 7, 0.15, 10)}" fill="#3A5AA8" stroke="#1A2A4A" stroke-width="1.4"/>')
    paint.append(f'<path d="{blob(X(0.96), Y(0.27), 8, 16, 8, 0.15, 10)}" fill="#E8C060" stroke="#6A4A10" stroke-width="1.4"/>')
    # the great yellow bed with its scarlet coverlet, filling the right side
    head = UV([(0.6, 0.22), (0.79, 0.2), (0.8, 0.5), (0.58, 0.54)])
    area(head, "#E8B040", ["#F2C050", "#E0A030", "#F6D068", "#D89828"], 7, -90, 160)
    # bed: the left side rail, the scarlet coverlet on top, pillows at the head, the tall footboard at the front
    rail = UV([(0.56, 0.5), (0.46, 0.9), (0.46, 0.97), (0.56, 0.56)])
    area(rail, "#E0A838", ["#F2C050", "#E0A030", "#D89828"], 12, -70, 40)
    cover = UV([(0.56, 0.5), (0.79, 0.46), (0.9, 0.86), (0.46, 0.9)])
    area(cover, "#D8402A", ["#E8502A", "#C8302A", "#F06A3A", "#B8281E", "#E85A3A"], 8, -60, None, L=(10, 16))
    for k, (u, v) in enumerate(((0.6, 0.47), (0.69, 0.455))):
        pl = UV([(u, v), (u + 0.09, v - 0.015), (u + 0.1, v + 0.07), (u + 0.01, v + 0.085)])
        area(pl, "#D8E0A0", ["#E8E8B8", "#C8D890", "#F2F0C8", "#B8C878"], 9 + k, -20, 50)
    foot = UV([(0.42, 0.84), (0.92, 0.79), (0.93, 1.02), (0.42, 1.02)])
    area(foot, "#E0A838", ["#F2C050", "#E0A030", "#D89828", "#F6D068"], 11, -90, 120)
    paint.append(f'<path d="M{X(0.42):.1f} {Y(0.9):.1f}L{X(0.92):.1f} {Y(0.86):.1f}" stroke="#A8701A" stroke-width="2.4"/>')
    # two rush chairs and the little table with jug and basin
    def chair(cx_, cy_, s_, seed):
        seat = [(cx_ - 18 * s_, cy_), (cx_ + 16 * s_, cy_ - 4 * s_), (cx_ + 20 * s_, cy_ + 10 * s_), (cx_ - 14 * s_, cy_ + 14 * s_)]
        legs = f'<path d="M{cx_ - 16 * s_:.1f} {cy_ + 12 * s_:.1f}v{30 * s_:.1f}M{cx_ + 18 * s_:.1f} {cy_ + 9 * s_:.1f}v{30 * s_:.1f}M{cx_ + 14 * s_:.1f} {cy_ - 3 * s_:.1f}v{-36 * s_:.1f}M{cx_ - 16 * s_:.1f} {cy_ + 1 * s_:.1f}v{-36 * s_:.1f}M{cx_ - 16 * s_:.1f} {cy_ - 20 * s_:.1f}L{cx_ + 14 * s_:.1f} {cy_ - 24 * s_:.1f}M{cx_ - 16 * s_:.1f} {cy_ - 30 * s_:.1f}L{cx_ + 14 * s_:.1f} {cy_ - 34 * s_:.1f}" stroke="#C8962A" stroke-width="{4 * s_:.1f}" stroke-linecap="round"/>'
        legs_k = legs.replace('stroke="#C8962A"', 'stroke="#2A2A3A"').replace(f'stroke-width="{4 * s_:.1f}"', f'stroke-width="{6 * s_:.1f}"')
        paint.append(legs_k + legs)
        area(seat, "#C8A848", ["#D8B858", "#B89838", "#E8C868", "#A88A30"], seed, 20, 40)
    chair(X(0.34), Y(0.7), 1.2, 21)
    chair(X(0.12), Y(0.78), 1.35, 22)
    tb = UV([(0.12, 0.54), (0.26, 0.52), (0.28, 0.58), (0.14, 0.6)])
    area(tb, "#C88A3A", ["#D89A48", "#B87A30", "#E8B060"], 23, 0, 30)
    paint.append(f'<path d="M{X(0.14):.1f} {Y(0.6):.1f}v{H * 0.14:.1f}M{X(0.27):.1f} {Y(0.58):.1f}v{H * 0.14:.1f}" stroke="#8A5A2A" stroke-width="3"/>')
    paint.append(f'<ellipse cx="{X(0.19):.1f}" cy="{Y(0.545):.1f}" rx="12" ry="4" fill="#7AA0C8" stroke="#2A2A3A" stroke-width="1.4"/>')
    paint.append(f'<path d="M{X(0.22):.1f} {Y(0.54):.1f}q-4 -16 4 -18q8 2 4 18z" fill="#5A8AB8" stroke="#2A2A3A" stroke-width="1.4"/>')
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.06)}{varnish(D, box, 0.12, 0.18)}</g>')
    out.append(museum_label(D, 488, "The Bedroom", "VINCENT VAN GOGH · 1888", "#F4EEDC", "#D8CCA8", ts=32, bs=18, gap=30))
    return finish(D, out, 139)


# ================================================================ 30. Birch Forest — Klimt, 1903
@design("birch-forest")
def birch_forest():
    D = Doc("gmbf")
    box = (106, 56, 494, 444)   # 388 square (110 x 110 cm, as Klimt's landscapes)
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0

    def X(u):
        return x0 + u * W

    def Y(v):
        return y0 + v * H
    out = [wall(D, "#4A3A2A", 301, (0.5, 0.15), 0.3)]
    out.append(simple_frame(D, box, 14, ("#E8D29A", "#B89048", "#6A4E1A"), 3))
    out.append(f'<rect x="{x0 - 3}" y="{y0 - 3}" width="{W + 6}" height="{H + 6}" fill="none" stroke="#2A1E10" stroke-width="1.6"/>')
    cp = clip_box(D, box)
    rnd = random.Random(8)
    B = Brush()
    paint = []
    # forest floor: a carpet of russet and gold leaves, dotted like a mosaic, rising nearly to the top
    paint.append(f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{D.lin([(0, "#6A5A3A"), (0.15, "#A86A30"), (1, "#7A3A18")])}"/>')
    stipple(B, lambda x, y: True, 6500, lambda x, y, r: r.choice(["#C8782A", "#A85A20", "#E89A3A", "#8A4018", "#D8A050", "#6A3010", "#B86A2A", "#5A6A3A"])
            if y > Y(0.12) else r.choice(["#5A6A4A", "#7A8A5A", "#4A5A3A", "#8A9A6A"]), 3, r=(1.8, 3.2))
    paint.append(B.render())
    # birch trunks: pale columns with dark lenticel marks, cut by the top edge, varying in width and distance
    trunks = []
    for k in range(15):
        u = (k + rnd.uniform(0.1, 0.9)) / 15 * 1.04 - 0.02
        depth = rnd.random()
        w_ = 6 + depth * 20
        base = Y(0.45 + depth * 0.55)
        trunks.append((depth, u, w_, base))
    trunks.sort()
    for depth, u, w_, base in trunks:
        tx = X(u)
        col = mix("#C8C0B0", "#F4F0E6", depth)
        trunk = [(tx - w_ / 2, y0 - 6), (tx + w_ / 2, y0 - 6), (tx + w_ / 2 + 1, base), (tx - w_ / 2 - 1, base)]
        paint.append(f'<path d="{pd(trunk)}" fill="{D.lin([(0, lt(col, 0.2)), (0.6, col), (1, mix(col, "#7A7268", 0.5))], 0, 0, 1, 0)}"/>')
        for j in range(int((base - y0) / 9)):
            yy = y0 + rnd.uniform(0, base - y0)
            L = rnd.uniform(0.3, 0.9) * w_
            xx = tx - w_ / 2 + rnd.uniform(0, w_ - L)
            paint.append(f'<path d="M{xx:.1f} {yy:.1f}h{L:.1f}" stroke="{rnd.choice(["#2A2420", "#4A3A30", "#1A1612"])}" stroke-width="{rnd.uniform(1, 1 + w_ * 0.12):.1f}" stroke-linecap="round"/>')
        paint.append(f'<ellipse cx="{tx:.1f}" cy="{base:.1f}" rx="{w_ * 0.8:.1f}" ry="{w_ * 0.15:.1f}" fill="#3A1A08" opacity="0.4"/>')
    out.append(f'<g {cp}>{"".join(paint)}{canvas_weave(D, box, 0.05)}{varnish(D, box, 0.1, 0.18, 6, 0.3)}</g>')
    out.append(museum_label(D, 486, "Birch Forest", "GUSTAV KLIMT · 1903", "#F2E6CC", "#C8B48C", ts=32, bs=18, gap=30))
    return finish(D, out, 149)


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())
    if not only:
        from common import ROOT
        for f in (ROOT / COL).glob("*.svg"):
            if f.stem not in DESIGNS:
                f.unlink()


if __name__ == "__main__":
    build(sys.argv[1:] or None)
