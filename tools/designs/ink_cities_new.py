"""Ink Cities, new cities: eighteen pen-and-ink illustrations drawn the way an architectural sketcher works:
a believable viewpoint, line-weight hierarchy (bold contours, finer detail, hairline-free texture),
cross-hatching and stippling for tone, scribbled foliage, ink ripples and broken reflections on water, and
small stories in the corners. Black ink on cream paper; a few pieces carry one faded accent wash.

Run from tools/designs:  python3 ink_cities_new.py [slug ...]
"""
import math
import random
import sys

from common import DMS, MONO, CINZEL, esc, fit_size, measure, save

INK = "#1C1916"
PAPER = "#F4EEE2"
COLL = "ink-cities"


# ====================================================================== geometry helpers
def P(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def arc_pts(cx, cy, rx, ry, a0, a1, n=24):
    """Points on an ellipse from angle a0 to a1 (degrees, 0 = right, 90 = down)."""
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def smooth(pts, n=6):
    """Catmull-Rom through the points: hand-like curves from a few control points."""
    if len(pts) < 3:
        return list(pts)
    ext = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out


def offset(pts, w0, w1):
    """Left/right offset curves of a centreline, width tapering w0 -> w1: limbs, trunks, palm stems."""
    L, R = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        Ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / Ln, dx / Ln
        ww = (w0 + (w1 - w0) * i / max(1, n - 1)) / 2
        L.append((x + nx * ww, y + ny * ww))
        R.append((x - nx * ww, y - ny * ww))
    return L, R


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def inside(pt, poly):
    x, y = pt
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
            c = not c
    return c


def bbox(poly):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


def rect(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


class Cam:
    """Pinhole camera: X right, Y up, Z forward (metres). Screen centre (cx, vpy)."""

    def __init__(self, f=300, cx=300, vpy=290, eye=1.6):
        self.f, self.cx, self.vpy, self.eye = f, cx, vpy, eye

    def __call__(self, X, Y, Z):
        return (self.cx + self.f * X / Z, self.vpy + self.f * (self.eye - Y) / Z)

    def qx(self, X, Z0, Z1, Y0, Y1):
        return [self(X, Y0, Z0), self(X, Y1, Z0), self(X, Y1, Z1), self(X, Y0, Z1)]

    def qz(self, Z, X0, X1, Y0, Y1):
        return [self(X0, Y0, Z), self(X0, Y1, Z), self(X1, Y1, Z), self(X1, Y0, Z)]


# ====================================================================== the pen
class Pen:
    """Drawing context for one design: unique ids, a seeded hand, and ink primitives that return SVG."""

    def __init__(self, slug, seed=1):
        self.slug = slug
        self.n = 0
        self.defs = []
        self.rnd = random.Random(seed)

    def uid(self, k="x"):
        self.n += 1
        return f"{self.slug}-{k}{self.n}"

    # ---------------------------------------------------------------- lines
    def wob(self, pts, amp=0.7, step=9, closed=False):
        """Subdivide a polyline and nudge it sideways with smooth noise: the tremor of a real pen."""
        if closed:
            pts = list(pts) + [pts[0]]
        out = [pts[0]]
        j = 0.0
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            L = math.hypot(x2 - x1, y2 - y1)
            if L < 1e-6:
                continue
            n = max(1, int(L / step))
            nx, ny = -(y2 - y1) / L, (x2 - x1) / L
            for i in range(1, n + 1):
                t = i / n
                j = 0.55 * j + 0.45 * self.rnd.uniform(-amp, amp)
                jj = j if i < n else j * 0.3
                out.append((x1 + (x2 - x1) * t + nx * jj, y1 + (y2 - y1) * t + ny * jj))
        return out

    def path_d(self, pts, closed=False):
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        return d + (" Z" if closed else "")

    def line(self, pts, w=2.0, amp=0.7, closed=False, fill="none", op=None, cap="round", step=9, color=INK):
        pts = self.wob(pts, amp, step, closed)
        o = f' opacity="{op}"' if op is not None else ""
        return (f'<path d="{self.path_d(pts, closed)}" fill="{fill}" stroke="{color}" stroke-width="{w}" '
                f'stroke-linecap="{cap}" stroke-linejoin="round"{o}/>')

    def seg(self, x1, y1, x2, y2, w=1.6, amp=0.5, op=None):
        return self.line([(x1, y1), (x2, y2)], w, amp, op=op)

    def shape(self, pts, w=2.0, fill=PAPER, amp=0.6, op=None):
        """Closed outline with a paper (or ink) fill: knocks out whatever is behind."""
        return self.line(pts, w, amp, closed=True, fill=fill, op=op)

    def solid(self, pts, fill=INK, op=None):
        o = f' opacity="{op}"' if op is not None else ""
        return f'<polygon points="{P(pts)}" fill="{fill}"{o}/>'

    # ---------------------------------------------------------------- tone
    def hatch(self, poly, ang=45, sp=4.0, w=1.1, op=0.9, trim=2.5, keep=None, amp=0.35, jit=0.18, color=INK, dash=None):
        """Parallel pen strokes filling a polygon, each stroke cut to the outline and trimmed a little at random,
        spacing and angle slightly uneven. keep(x, y) -> 0..1 thins strokes (tone gradients)."""
        a = math.radians(ang)
        dx, dy = math.cos(a), math.sin(a)
        nx, ny = -dy, dx
        x0, y0, x1, y1 = bbox(poly)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        R = math.hypot(x1 - x0, y1 - y0) / 2 + 4
        out = []
        o = -R
        n = len(poly)
        while o <= R:
            oo = o + self.rnd.uniform(-jit, jit) * sp
            px, py = cx + nx * oo, cy + ny * oo
            # intersections of line p + t*d with polygon edges
            ts = []
            for i in range(n):
                ax, ay = poly[i]
                bx, by = poly[(i + 1) % n]
                ex, ey = bx - ax, by - ay
                den = dx * ey - dy * ex
                if abs(den) < 1e-9:
                    continue
                t = ((ax - px) * ey - (ay - py) * ex) / den
                s = ((ax - px) * dy - (ay - py) * dx) / den
                if 0 <= s < 1:
                    ts.append(t)
            ts.sort()
            for t0, t1 in zip(ts[0::2], ts[1::2]):
                t0 += self.rnd.uniform(0, trim)
                t1 -= self.rnd.uniform(0, trim)
                if t1 - t0 < 1.5:
                    continue
                mx, my = px + dx * (t0 + t1) / 2, py + dy * (t0 + t1) / 2
                if keep is not None and not dash and self.rnd.random() > keep(mx, my):
                    continue
                tilt = self.rnd.uniform(-0.6, 0.6)
                if dash:
                    t = t0
                    while t < t1:
                        L = self.rnd.uniform(*dash)
                        te = min(t1, t + L)
                        mx, my = px + dx * (t + te) / 2, py + dy * (t + te) / 2
                        if keep is None or self.rnd.random() < keep(mx, my):
                            out.append(f"M{px + dx * t:.1f} {py + dy * t:.1f}L{px + dx * te:.1f} {py + dy * te + self.rnd.uniform(-0.5, 0.5):.1f}")
                        t = te + self.rnd.uniform(3, 12)
                    continue
                ax_, ay_ = px + dx * t0, py + dy * t0
                bx_, by_ = px + dx * t1 + nx * tilt, py + dy * t1 + ny * tilt
                out.append(f"M{ax_:.1f} {ay_:.1f}L{bx_:.1f} {by_:.1f}")
            o += sp
        if not out:
            return ""
        return (f'<path d="{"".join(out)}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" '
                f'opacity="{op}"/>')

    def tone(self, poly, level=2, ang=45, sp=None, w=1.1, op=0.9, keep=None):
        """Tonal value by layered hatching: 1 light, 2 mid, 3 cross-hatch, 4 dense cross-hatch."""
        sp = sp or {1: 6.5, 2: 4.2, 3: 4.2, 4: 3.2}[level]
        out = [self.hatch(poly, ang, sp, w, op, keep=keep)]
        if level >= 3:
            out.append(self.hatch(poly, ang + 90 if level == 3 else ang - 70, sp * 1.15, w, op * 0.9, keep=keep))
        if level >= 4:
            out.append(self.hatch(poly, ang + 35, sp * 1.3, w, op * 0.8, keep=keep))
        return "".join(out)

    def stipple(self, poly, n, r=(0.7, 1.3), keep=None, op=0.95):
        """Ink dots scattered inside a polygon; keep(x, y) -> 0..1 for density gradients."""
        x0, y0, x1, y1 = bbox(poly)
        dots = []
        tries = 0
        while len(dots) < n and tries < n * 30:
            tries += 1
            x, y = self.rnd.uniform(x0, x1), self.rnd.uniform(y0, y1)
            if not inside((x, y), poly):
                continue
            if keep is not None and self.rnd.random() > keep(x, y):
                continue
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{self.rnd.uniform(*r):.2f}"/>')
        return f'<g fill="{INK}" opacity="{op}">' + "".join(dots) + "</g>"

    # ---------------------------------------------------------------- nature
    def foliage(self, cx, cy, rx, ry, w=1.6, shade=0.55, bump=7.0, fill=PAPER, inner=1.0, light=(-1, -1), dark=False):
        """Scribbled tree crown: a scalloped outline, little 'u' leaf-clump marks inside, and hatched shade on
        the side away from the light."""
        rnd = self.rnd
        per = math.pi * (3 * (rx + ry) - math.sqrt((3 * rx + ry) * (rx + 3 * ry)))
        N = max(7, int(per / (bump * 2.1)))
        pts = []
        for i in range(N):
            a = 2 * math.pi * (i + rnd.uniform(-0.25, 0.25)) / N
            k = rnd.uniform(0.86, 1.06)
            pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
        d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
        poly = []
        for i in range(N):
            p, q = pts[i], pts[(i + 1) % N]
            mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            ox, oy = mx - cx, my - cy
            L = math.hypot(ox, oy) or 1
            b = bump * rnd.uniform(0.6, 1.25)
            c = (mx + ox / L * b, my + oy / L * b)
            d += f" Q {c[0]:.1f} {c[1]:.1f} {q[0]:.1f} {q[1]:.1f}"
            poly += [p, (mx + ox / L * b * 0.5, my + oy / L * b * 0.5)]
        lx, ly = light
        Ll = math.hypot(lx, ly)
        lx, ly = lx / Ll, ly / Ll
        out = [f'<path d="{d} Z" fill="{fill}" stroke="{INK}" stroke-width="{w}" stroke-linejoin="round"/>']
        if dark:
            out.append(self.tone(poly, 3, ang=rnd.uniform(30, 60), sp=3.4, w=1.1))
        elif shade:
            def kp(x, y):
                t = ((x - cx) / rx * -lx + (y - cy) / ry * -ly)
                return max(0.0, min(1.0, (t + 0.25) * 1.4)) * shade * 1.6
            out.append(self.hatch(poly, ang=rnd.choice([40, 50, 130]), sp=3.3, w=1.05, op=0.85, keep=kp))
        # leaf clumps
        marks = []
        m = int(rx * ry / 55 * inner)
        for _ in range(m):
            a = rnd.uniform(0, 2 * math.pi)
            rr = math.sqrt(rnd.random()) * 0.85
            x, y = cx + rx * rr * math.cos(a), cy + ry * rr * math.sin(a)
            s = rnd.uniform(2.5, 4.5)
            marks.append(f"M{x - s:.1f} {y - s * 0.3:.1f}q{s:.1f} {s * 1.3:.1f} {2 * s:.1f} 0")
        out.append(f'<path d="{"".join(marks)}" fill="none" stroke="{INK}" stroke-width="1.2" stroke-linecap="round" opacity="0.8"/>')
        return "".join(out)

    def scribble(self, cx, cy, rx, ry, sp=5.0, loop=3.0, w=1.1, light=(-0.6, -1), shade=1.0, base=0.55,
                 poly=None, dark=0.0, op=1.0, clumps=None, cr=(14, 30), edges=True):
        """Scribbled foliage. The crown is split into leaf clumps; each clump is filled with rows of small
        looping pen curls, sparse on its lit top and packed on its shaded underside, so the mass reads as
        many round tufts. Lit edges of the clumps get a scalloped contour."""
        rnd = self.rnd
        lx, ly = light
        Ll = math.hypot(lx, ly)
        lx, ly = lx / Ll, ly / Ll
        if poly is None:
            poly = []
            for i in range(36):
                a = 2 * math.pi * i / 36
                k = 1 + 0.07 * math.sin(3 * a + cx) + 0.05 * math.sin(5 * a + cy)
                poly.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
        x0, y0, x1, y1 = bbox(poly)
        if clumps is None:
            area = (x1 - x0) * (y1 - y0)
            clumps = []
            tries = 0
            while tries < 4000 and len(clumps) < area / (cr[0] * cr[1] * 1.6) + 2:
                tries += 1
                x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
                if inside((x, y), poly):
                    clumps.append((x, y, rnd.uniform(*cr)))
        clumps.sort(key=lambda c: c[1])

        def val(x, y):
            best = None
            for (ccx, ccy, r) in clumps:
                d = math.hypot((x - ccx) / r, (y - ccy) / (r * 0.8))
                if d < 1:
                    best = (ccx, ccy, r, d)
            if best is None or not inside((x, y), poly):
                return -1
            ccx, ccy, r, d = best
            t = -((x - ccx) / r * lx + (y - ccy) / (r * 0.8) * ly)
            return max(0.0, min(1.0, 0.45 + 0.55 * t + 0.25 * d))
        paths = []
        for pass_ in range(2 + (1 if dark else 0)):
            row = 0
            y = y0 + rnd.uniform(0, sp)
            while y <= y1 + 2:
                row += 1
                x = x0 - 4
                run, runs = [], []
                ph = rnd.uniform(0, 6.28)
                while x <= x1 + 4:
                    yy = y + 1.6 * math.sin(x / 13 + row * 1.7)
                    v = val(x, yy)
                    if pass_ == 0:
                        need = base * (0.35 + 0.9 * v)
                    elif pass_ == 1:
                        need = (v - 0.55) * 2.0 * shade
                    else:
                        need = (v - 0.7) * 3 * dark
                    if v >= 0 and rnd.random() < need:
                        r = loop * rnd.uniform(0.6, 1.3)
                        for k in range(8):
                            ph += rnd.uniform(0.62, 0.9)
                            run.append((x + r * math.cos(ph) + k * 0.45, yy + r * 0.8 * math.sin(ph)))
                    elif run:
                        runs.append(run)
                        run = []
                    x += loop * rnd.uniform(0.9, 1.4)
                if run:
                    runs.append(run)
                for rr in runs:
                    if len(rr) > 3:
                        paths.append("M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in rr))
                y += sp * (1.0 if pass_ == 0 else 1.35) * rnd.uniform(0.8, 1.2)
        o = f' opacity="{op}"' if op != 1 else ""
        out = [f'<path d="{"".join(paths)}" fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"{o}/>']
        if edges:
            arcs = []
            for (ccx, ccy, r) in clumps:
                a0 = math.degrees(math.atan2(ly, lx)) + rnd.uniform(-30, 30)
                pts = arc_pts(ccx, ccy, r * 0.95, r * 0.75, a0 - 38, a0 + 38, 6)
                pts = [q for q in pts if inside(q, poly)]
                if len(pts) > 3:
                    arcs.append("M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in pts))
            out.append(f'<path d="{"".join(arcs)}" fill="none" stroke="{INK}" stroke-width="{w:.2f}" stroke-linecap="round" opacity="{0.75 * op:.2f}"/>')
        return "".join(out)

    def branch(self, ctrl, w0, w1, n=8, bark=True):
        """A limb or trunk in silhouette: solid ink tapering shape with broken paper bark lines along it."""
        c = smooth(ctrl, n)
        L, R = offset(c, w0, w1)
        out = [f'<polygon points="{P(L + R[::-1])}" fill="{INK}" stroke="{INK}" stroke-width="1.2" stroke-linejoin="round"/>']
        if bark and w0 > 9:
            segs = []
            for f in (0.22, 0.45, 0.7):
                pts = [lerp(l, r, f + 0.08 * math.sin(i * 0.7 + f * 9)) for i, (l, r) in enumerate(zip(L, R))]
                i = self.rnd.randint(0, 3)
                while i < len(pts) - 2:
                    j = min(len(pts) - 1, i + self.rnd.randint(2, 4))
                    if self.rnd.random() < 0.5:
                        segs.append("M" + "L".join(f"{a:.1f} {b:.1f}" for a, b in pts[i:j + 1]))
                    i = j + self.rnd.randint(1, 4)
            out.append(f'<path d="{"".join(segs)}" fill="none" stroke="{PAPER}" stroke-width="0.9" stroke-linecap="round" opacity="0.75"/>')
        return "".join(out)

    def ripples(self, x0, x1, y0, y1, n, hy=None, lmin=6, lmax=26, wmin=1.1, wmax=1.9, avoid=None, keep=None, amp=None):
        """Ink ripples on water: short wavy strokes, smaller and denser toward the horizon line hy."""
        hy = y0 if hy is None else hy
        rnd = self.rnd
        out = []
        for _ in range(n * 4):
            if len(out) >= n:
                break
            t = rnd.random() ** 1.6
            y = y0 + (y1 - y0) * t
            x = rnd.uniform(x0, x1)
            if avoid and any(a[0] < x < a[2] and a[1] < y < a[3] for a in avoid):
                continue
            if keep is not None and rnd.random() > keep(x, y):
                continue
            k = (y - hy) / max(1, (y1 - hy))
            L = lmin + (lmax - lmin) * k * rnd.uniform(0.6, 1.2)
            a = (amp or (0.8 + 1.6 * k)) * rnd.choice([1, -1])
            out.append(f'<path d="M{x:.1f} {y:.1f}q{L / 4:.1f} {-a:.1f} {L / 2:.1f} 0t{L / 2:.1f} 0" stroke-width="{wmin + (wmax - wmin) * k:.2f}"/>')
        return f'<g fill="none" stroke="{INK}" stroke-linecap="round">' + "".join(out) + "</g>"

    def reflect(self, x0, x1, y0, depth, density=0.85, sp=3.2, w=1.3, taper=0.35):
        """Broken horizontal strokes under an object: its reflection in moving water."""
        rnd = self.rnd
        out = []
        y = y0 + 1.5
        while y < y0 + depth:
            t = (y - y0) / depth
            span = (x1 - x0) * (1 - taper * t)
            cx = (x0 + x1) / 2 + rnd.uniform(-2, 2)
            xa = cx - span / 2
            while xa < cx + span / 2:
                L = rnd.uniform(5, 18)
                if rnd.random() < density * (1 - 0.6 * t):
                    out.append(f"M{xa:.1f} {y:.1f}l{min(L, cx + span / 2 - xa):.1f} {rnd.uniform(-0.4, 0.4):.1f}")
                xa += L + rnd.uniform(2, 6)
            y += sp * rnd.uniform(0.85, 1.25)
        return f'<path d="{"".join(out)}" stroke="{INK}" stroke-width="{w}" stroke-linecap="round" fill="none"/>'

    def birds(self, pts, s=6, w=1.5):
        out = []
        for x, y, *k in pts:
            ss = s * (k[0] if k else 1)
            out.append(f"M{x - ss:.1f} {y - ss * 0.2:.1f}q{ss * 0.5:.1f} {-ss * 0.55:.1f} {ss:.1f} {ss * 0.2:.1f}"
                       f"q{ss * 0.5:.1f} {-ss * 0.75:.1f} {ss:.1f} {-ss * 0.2:.1f}")
        return f'<path d="{"".join(out)}" fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'

    def grass(self, x0, x1, y, n, h=(3, 8), w=1.2):
        out = []
        for _ in range(n):
            x = self.rnd.uniform(x0, x1)
            hh = self.rnd.uniform(*h)
            out.append(f"M{x:.1f} {y:.1f}q{self.rnd.uniform(-1.5, 1.5):.1f} {-hh / 2:.1f} {self.rnd.uniform(-3, 3):.1f} {-hh:.1f}")
        return f'<path d="{"".join(out)}" fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round"/>'

    def clouds(self, cx, cy, s=1.0, w=1.5):
        """A loose hand-drawn cumulus: a few overlapping arcs and a flat base, with base hatching."""
        rnd = self.rnd
        bumps = [(-34, 0, 14), (-16, -10, 17), (6, -14, 19), (28, -6, 15), (44, 2, 10)]
        d = f"M {cx - 50 * s:.1f} {cy + 8 * s:.1f}"
        for bx, by, r in bumps:
            x = cx + bx * s
            d += f" Q {x - r * s * 0.9:.1f} {cy + (by - r * 1.3) * s:.1f} {x + r * s * 0.6:.1f} {cy + (by - r * 0.2) * s:.1f}"
        d += f" Q {cx + 62 * s:.1f} {cy + 6 * s:.1f} {cx + 52 * s:.1f} {cy + 8 * s:.1f} Z"
        hatch = "".join(f"M{cx - 40 * s + i * 9 * s:.1f} {cy + 7 * s:.1f}l{8 * s:.1f} 0" for i in range(9) if rnd.random() < 0.7)
        return (f'<path d="{d}" fill="{PAPER}" stroke="{INK}" stroke-width="{w}" stroke-linejoin="round"/>'
                f'<path d="{hatch}" stroke="{INK}" stroke-width="1.1" opacity="0.7"/>')

    # ---------------------------------------------------------------- people and things
    def person(self, x, y, h, pose=0, flip=False, bag=False, dress=False):
        """Ink silhouette of a pedestrian standing on (x, y), h tall."""
        k = h / 20
        sx = -1 if flip else 1
        r = 1.8 * k
        legs = {0: f"M{x - 1.2 * k * sx:.1f} {y - 9 * k:.1f}l{-2.2 * k * sx:.1f} {9 * k:.1f}M{x + 1.2 * k * sx:.1f} {y - 9 * k:.1f}l{2.4 * k * sx:.1f} {9 * k:.1f}",
                1: f"M{x - 1 * k:.1f} {y - 9 * k:.1f}l{-0.3 * k:.1f} {9 * k:.1f}M{x + 1 * k:.1f} {y - 9 * k:.1f}l{0.3 * k:.1f} {9 * k:.1f}"}[pose % 2]
        if dress:
            body = f'<path d="M{x - 2.3 * k:.1f} {y - 15.5 * k:.1f}L{x + 2.3 * k:.1f} {y - 15.5 * k:.1f}L{x + 4 * k:.1f} {y - 6 * k:.1f}L{x - 4 * k:.1f} {y - 6 * k:.1f}Z" fill="{INK}"/>'
        else:
            body = f'<path d="M{x - 2.4 * k:.1f} {y - 15.5 * k:.1f}L{x + 2.4 * k:.1f} {y - 15.5 * k:.1f}L{x + 2 * k:.1f} {y - 8.5 * k:.1f}L{x - 2 * k:.1f} {y - 8.5 * k:.1f}Z" fill="{INK}"/>'
        arm = f"M{x + 2.2 * k * sx:.1f} {y - 15 * k:.1f}l{1.6 * k * sx:.1f} {6 * k:.1f}"
        out = [f'<circle cx="{x:.1f}" cy="{y - 17.6 * k:.1f}" r="{r:.1f}" fill="{INK}"/>', body,
               f'<path d="{legs}{arm}" stroke="{INK}" stroke-width="{max(1.3, 1.5 * k):.1f}" stroke-linecap="round" fill="none"/>']
        if bag:
            out.append(f'<rect x="{x + 3 * k * sx - (2.6 * k if flip else 0):.1f}" y="{y - 10 * k:.1f}" width="{2.6 * k:.1f}" height="{3 * k:.1f}" fill="{INK}"/>')
        return "".join(out)

    def bike(self, x, y, s=1.0, flip=False, w=1.5):
        """Upright city bike leaning on its stand, wheels touching y."""
        r = 7.5 * s
        f = -1 if flip else 1
        b = x + 21 * s * f
        hb = (b - 3 * s * f, y - r - 13 * s)
        seat = (x + 6 * s * f, y - r - 11 * s)
        crank = (x + 10 * s * f, y - r + 1 * s)
        d = (f"M{x:.1f} {y - r:.1f}L{crank[0]:.1f} {crank[1]:.1f}L{b - 3 * s * f:.1f} {y - r - 9 * s:.1f}"
             f"L{x + 6 * s * f:.1f} {y - r - 9 * s:.1f}L{x:.1f} {y - r:.1f}M{crank[0]:.1f} {crank[1]:.1f}L{seat[0]:.1f} {seat[1]:.1f}"
             f"M{b:.1f} {y - r:.1f}L{hb[0]:.1f} {hb[1]:.1f}l{-4 * s * f:.1f} {-1 * s:.1f}"
             f"M{seat[0] - 3 * s:.1f} {seat[1]:.1f}l{6 * s:.1f} 0")
        basket = f'<rect x="{b + (1 if flip else -1) * 0 - (7 * s if not flip else 0) + 3 * s * f:.1f}" y="{y - r - 14 * s:.1f}" width="{7 * s:.1f}" height="{5 * s:.1f}" fill="none" stroke="{INK}" stroke-width="1.2"/>'
        return (f'<g fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round">'
                f'<circle cx="{x:.1f}" cy="{y - r:.1f}" r="{r:.1f}"/><circle cx="{b:.1f}" cy="{y - r:.1f}" r="{r:.1f}"/>'
                f'<path d="{d}"/></g>' + (basket if s > 0.8 else ""))

    def lamp(self, x, y, h, style=0, w=1.8, arms=1):
        """Cast-iron street lamp: post with base and a lantern head."""
        k = h / 60
        out = [f'<path d="M{x - 3 * k:.1f} {y:.1f}L{x - 2 * k:.1f} {y - 8 * k:.1f}L{x - 1.1 * k:.1f} {y - 10 * k:.1f}L{x - 0.9 * k:.1f} {y - h + 10 * k:.1f}'
               f'L{x + 0.9 * k:.1f} {y - h + 10 * k:.1f}L{x + 1.1 * k:.1f} {y - 10 * k:.1f}L{x + 2 * k:.1f} {y - 8 * k:.1f}L{x + 3 * k:.1f} {y:.1f}Z" fill="{INK}"/>']
        heads = []
        if arms == 1:
            heads.append((x, y - h + 10 * k))
        else:
            out.append(f'<path d="M{x - 9 * k:.1f} {y - h + 14 * k:.1f}Q{x:.1f} {y - h + 4 * k:.1f} {x + 9 * k:.1f} {y - h + 14 * k:.1f}" stroke="{INK}" stroke-width="{w}" fill="none"/>')
            heads += [(x - 9 * k, y - h + 14 * k), (x + 9 * k, y - h + 14 * k)]
        for hx, hy in heads:
            lw, lh = 4.5 * k, 9 * k
            out.append(f'<path d="M{hx - lw / 2:.1f} {hy:.1f}L{hx - lw * 0.8:.1f} {hy - lh:.1f}L{hx + lw * 0.8:.1f} {hy - lh:.1f}L{hx + lw / 2:.1f} {hy:.1f}Z" fill="{PAPER}" stroke="{INK}" stroke-width="{w * 0.8:.1f}"/>'
                       f'<path d="M{hx - lw:.1f} {hy - lh:.1f}L{hx:.1f} {hy - lh - 3.5 * k:.1f}L{hx + lw:.1f} {hy - lh:.1f}Z" fill="{INK}"/>'
                       f'<circle cx="{hx:.1f}" cy="{hy - lh - 4.5 * k:.1f}" r="{1 * k:.1f}" fill="{INK}"/>')
        return "".join(out)

    def windows(self, x0, y0, cols, rows, ww, wh, gx, gy, w=1.3, dark=0.5, shutters=False, arch=False, sill=True):
        """A grid of sash windows on an elevation, some panes inked dark (curtains / shadow)."""
        out = []
        for r in range(rows):
            for c in range(cols):
                x, y = x0 + c * (ww + gx), y0 + r * (wh + gy)
                fill = INK if self.rnd.random() < dark else PAPER
                if arch:
                    d = f"M{x:.1f} {y + wh:.1f}L{x:.1f} {y + ww / 2:.1f}A{ww / 2:.1f} {ww / 2:.1f} 0 0 1 {x + ww:.1f} {y + ww / 2:.1f}L{x + ww:.1f} {y + wh:.1f}Z"
                    out.append(f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="{w}"/>')
                else:
                    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{ww:.1f}" height="{wh:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{w}"/>')
                if fill == PAPER:
                    out.append(f'<path d="M{x + ww / 2:.1f} {y:.1f}v{wh:.1f}M{x:.1f} {y + wh / 2:.1f}h{ww:.1f}" stroke="{INK}" stroke-width="0.9"/>')
                else:
                    out.append(f'<path d="M{x + ww / 2:.1f} {y + 1:.1f}v{wh - 2:.1f}" stroke="{PAPER}" stroke-width="0.9" opacity="0.8"/>')
                if sill:
                    out.append(f'<path d="M{x - 1.5:.1f} {y + wh + 1:.1f}h{ww + 3:.1f}" stroke="{INK}" stroke-width="{w + 0.4}"/>')
                if shutters:
                    sw_ = ww * 0.45
                    for sx in (x - sw_ - 1, x + ww + 1):
                        out.append(f'<rect x="{sx:.1f}" y="{y:.1f}" width="{sw_:.1f}" height="{wh:.1f}" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>')
                        out.append("".join(f'<path d="M{sx + 0.8:.1f} {y + i * 2.6:.1f}h{sw_ - 1.6:.1f}" stroke="{INK}" stroke-width="0.8"/>' for i in range(1, int(wh / 2.6))))
        return "".join(out)

    def laundry(self, x0, y0, x1, y1, sag=10, items=5, w=1.2):
        """A washing line between two points with shirts, towels and socks pegged on it."""
        rnd = self.rnd
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
        out = [f'<path d="M{x0:.1f} {y0:.1f}Q{mx:.1f} {my + sag:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{INK}" stroke-width="{w}"/>']

        def on(t):
            a = (1 - t) ** 2
            b = 2 * (1 - t) * t
            c = t * t
            return (a * x0 + b * mx + c * x1, a * y0 + b * (my + sag) + c * y1)
        for i in range(items):
            t = (i + 0.6 + rnd.uniform(-0.15, 0.15)) / (items + 0.2)
            x, y = on(t)
            kind = rnd.choice(["shirt", "towel", "sock", "towel", "shirt"])
            s = rnd.uniform(0.9, 1.15) * abs(x1 - x0) / (items * 9)
            s = max(0.7, min(1.4, s))
            if kind == "shirt":
                d = (f"M{x - 5 * s:.1f} {y:.1f}l-3 {3 * s:.1f}l2 {2 * s:.1f}l1.5 -1v{8 * s:.1f}h{9 * s:.1f}v{-8 * s:.1f}l1.5 1l2 {-2 * s:.1f}l-3 {-3 * s:.1f}Z")
            elif kind == "towel":
                d = f"M{x - 4 * s:.1f} {y:.1f}h{8 * s:.1f}l{0.5 * s:.1f} {11 * s:.1f}h{-9 * s:.1f}Z"
            else:
                d = f"M{x - 1.5 * s:.1f} {y:.1f}h{3 * s:.1f}v{6 * s:.1f}l{2 * s:.1f} {1.5 * s:.1f}l-1 {2 * s:.1f}l{-4 * s:.1f} -2Z"
            dark = rnd.random() < 0.3
            out.append(f'<path d="{d}" fill="{INK if dark else PAPER}" stroke="{INK}" stroke-width="1.1" stroke-linejoin="round"/>')
            if not dark and kind == "towel":
                out.append(f'<path d="M{x - 4 * s:.1f} {y + 8 * s:.1f}h{8.5 * s:.1f}" stroke="{INK}" stroke-width="1"/>')
        return "".join(out)

    # ---------------------------------------------------------------- paper and frames
    def paper(self, seed=0, tooth=260, vignette=0.0, blotch=0):
        rnd = random.Random(seed)
        out = [f'<rect width="600" height="600" fill="{PAPER}"/>']
        out.append('<g fill="#8A7A60" opacity="0.18">' + "".join(
            f'<circle cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(0, 600):.1f}" r="{rnd.uniform(0.4, 1.0):.2f}"/>' for _ in range(tooth)) + "</g>")
        if vignette:
            g = self.uid("vig")
            self.defs.append(f'<radialGradient id="{g}" cx="0.5" cy="0.5" r="0.72"><stop offset="0.55" stop-color="{INK}" stop-opacity="0"/>'
                             f'<stop offset="0.85" stop-color="{INK}" stop-opacity="{vignette * 0.5:.2f}"/><stop offset="1" stop-color="{INK}" stop-opacity="{vignette:.2f}"/></radialGradient>')
            out.append(f'<rect width="600" height="600" fill="url(#{g})"/>')
        for _ in range(blotch):
            side = rnd.choice("tblr")
            t = rnd.uniform(0, 600)
            x, y = {"t": (t, rnd.uniform(-20, 30)), "b": (t, rnd.uniform(570, 620)), "l": (rnd.uniform(-20, 30), t), "r": (rnd.uniform(570, 620), t)}[side]
            out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(20, 70):.1f}" ry="{rnd.uniform(15, 50):.1f}" fill="{INK}" opacity="{rnd.uniform(0.03, 0.07):.2f}"/>')
        return "".join(out)

    def border(self, inset=46, gap=7, w1=2.6, w2=1.3, corners="cross"):
        """Hand-ruled double border; the pen overshoots at the corners like a quick sketch."""
        a, b = inset, 600 - inset
        out = []
        for k, (ins, w) in enumerate(((a, w1), (a + gap, w2))):
            lo, hi = ins, 600 - ins
            ov = 5 if corners == "cross" and k == 0 else 0
            for p, q in (((lo - ov, lo), (hi + ov, lo)), ((hi, lo - ov), (hi, hi + ov)),
                         ((hi + ov, hi), (lo - ov, hi)), ((lo, hi + ov), (lo, lo - ov))):
                out.append(self.line([p, q], w, amp=0.6, step=14))
        return "".join(out)

    def wash(self, pts, color, op=0.32, seed=None):
        """A faded watercolour accent: two slightly offset translucent layers with a pooled edge."""
        rnd = self.rnd
        a = [(x + rnd.uniform(-1.5, 1.5), y + rnd.uniform(-1.5, 1.5)) for x, y in pts]
        return (f'<polygon points="{P(pts)}" fill="{color}" opacity="{op:.2f}"/>'
                f'<polygon points="{P(a)}" fill="{color}" opacity="{op * 0.45:.2f}" stroke="{color}" stroke-width="2" stroke-opacity="{op * 0.6:.2f}"/>')

    def clip(self, inner, body):
        cid = self.uid("cl")
        self.defs.append(f'<clipPath id="{cid}">{inner}</clipPath>')
        return f'<g clip-path="url(#{cid})">{body}</g>'


# ====================================================================== typography
def name_size(name, max_w, size, font=DMS, ls=0):
    return fit_size(name, font, size, max_w, ls)


def title_text(x, y, s, size, font=DMS, fill=INK, ls=0, anchor="middle", extra=""):
    if anchor == "middle" and ls:
        x += ls / 2
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" {font} font-size="{size}"{lsa} fill="{fill}"{extra}>{esc(s)}</text>'


def coord_line(pen, cx, y, coords, size=17, ls=2.5, rule=34, gap=12, w=1.6, max_w=400, dots=False):
    """Coordinates in DM Mono flanked by two short pen rules."""
    sz = fit_size(coords, MONO, size, max_w, ls)
    tw = measure(coords, MONO, sz, ls)
    out = [title_text(cx, y, coords, sz, MONO, ls=ls)]
    if rule:
        my = y - sz * 0.33
        out.append(pen.seg(cx - tw / 2 - gap - rule, my, cx - tw / 2 - gap, my, w, 0.3))
        out.append(pen.seg(cx + tw / 2 + gap, my, cx + tw / 2 + gap + rule, my, w, 0.3))
        if dots:
            out.append(f'<circle cx="{cx - tw / 2 - gap - rule - 5:.1f}" cy="{my:.1f}" r="2" fill="{INK}"/>'
                       f'<circle cx="{cx + tw / 2 + gap + rule + 5:.1f}" cy="{my:.1f}" r="2" fill="{INK}"/>')
    return "".join(out)


def ribbon(pen, cx, cy, wdt, h, text, size, tail=26, drop=10, ls=0, w=2.2, curve=0.0):
    """Banner ribbon with folded swallow-tail ends; the folds are hatched in shadow."""
    l, r = cx - wdt / 2, cx + wdt / 2
    t, b = cy - h / 2, cy + h / 2
    c = curve
    out = []
    for s in (-1, 1):
        x0 = l if s < 0 else r
        xo = x0 - s * tail * 1.4
        tailp = [(x0 - s * tail * 0.2, t + drop), (xo, t + drop), (xo + s * tail * 0.45, (t + b) / 2 + drop),
                 (xo, b + drop), (x0 + s * 6, b + drop)]
        out.append(pen.shape(tailp, w))
        out.append(pen.hatch(tailp, 60 if s < 0 else 120, 3.2, 1.0, 0.8))
        fold = [(x0, b), (x0 + s * 6, b + drop), (x0 - s * tail * 0.2, b + drop * 0.2)]
        fold = [(x0, b), (x0 + s * 6, b + drop), (x0, b + drop * 0.1)]
        out.append(pen.solid([(x0, b), (x0 + s * 6, b + drop), (x0 + s * 6, b)]))
    body = [(l, t + c), (cx, t), (r, t + c), (r, b + c), (cx, b), (l, b + c)]
    body = [(l, t), (r, t), (r, b), (l, b)]
    out.append(pen.shape(body, w))
    out.append(pen.line([(l + 6, t + 4), (r - 6, t + 4)], 1.0, 0.3))
    out.append(pen.line([(l + 6, b - 4), (r - 6, b - 4)], 1.0, 0.3))
    out.append(title_text(cx, cy + size * 0.34, text, size, DMS, ls=ls))
    return "".join(out)


def cartouche(pen, x0, y0, x1, y1, notch=10, w=2.4, fill=PAPER, inner=True):
    """Ruled cartouche with notched corners and an inner hairline rule."""
    n = notch
    pts = [(x0 + n, y0), (x1 - n, y0), (x1 - n, y0 + n), (x1, y0 + n), (x1, y1 - n), (x1 - n, y1 - n), (x1 - n, y1),
           (x0 + n, y1), (x0 + n, y1 - n), (x0, y1 - n), (x0, y0 + n), (x0 + n, y0 + n)]
    out = [pen.shape(pts, w, fill=fill)]
    if inner:
        out.append(pen.line(rect(x0 + 6, y0 + 6, x1 - x0 - 12, y1 - y0 - 12), 1.1, 0.3, closed=True))
    return "".join(out)


# ====================================================================== designs
DESIGNS = {}


def design(slug, name, coords):
    def deco(fn):
        DESIGNS[slug] = (name, coords, fn)
        return fn
    return deco


def compose(pen, body):
    return (f"<defs>{''.join(pen.defs)}</defs>\n" if pen.defs else "") + body


# ---------------------------------------------------------------------------------- SAVANNAH
@design("savannah", "Savannah", "32.0809° N · 81.0912° W")
def savannah(name, coords):
    """Forsyth Park: the cast-iron fountain seen down the path, under live oaks dripping with Spanish moss."""
    p = Pen("savannah", 11)
    o = [p.paper(1, vignette=0.0)]
    rnd = p.rnd
    gy = 392                                     # ground line at the fountain
    # --- far trees across the park: lighter, sparser scribble (distance)
    for x, y, rx, ry in ((110, 318, 70, 46), (200, 330, 46, 32), (410, 326, 52, 34), (498, 316, 72, 48)):
        o.append(p.scribble(x, y, rx, ry, sp=6.0, loop=2.4, w=1.0, base=0.4, shade=0.7, op=0.6, cr=(10, 18)))
    o.append(p.line([(60, gy - 8), (540, gy - 8)], 1.2, 0.5))
    # clipped azalea hedges behind the fountain
    for x0 in range(60, 545, 30):
        o.append(p.foliage(x0 + 15, gy - 17, 17, 11, w=1.3, shade=0.5, bump=4, inner=0.4))
    # --- the path, in perspective toward the fountain
    vx = 300
    path = [(vx - 70, gy + 4), (vx + 70, gy + 4), (vx + 190, 600), (vx - 190, 600)]
    o.append(p.line([(vx - 74, gy + 4), (vx - 210, 600)], 1.8, 0.8))
    o.append(p.line([(vx + 74, gy + 4), (vx + 210, 600)], 1.8, 0.8))
    o.append(p.stipple(path, 260, r=(0.6, 1.1), keep=lambda x, y: 0.25 + 0.5 * (y - gy) / 200))
    # lawn hatching both sides
    for poly, ang in (([(0, gy + 2), (vx - 74, gy + 4), (vx - 210, 600), (0, 600)], 8), ([(vx + 74, gy + 4), (600, gy + 2), (600, 600), (vx + 210, 600)], 172)):
        o.append(p.hatch(poly, ang, 5.5, 1.0, 0.55, keep=lambda x, y: 0.3 + (y - gy) / 300))
    o.append(p.grass(60, 230, gy + 30, 40, (3, 7)) + p.grass(370, 540, gy + 30, 40, (3, 7)))
    # --- the fountain
    cx = 300
    # basin and railing
    bw, bh = 132, 16
    basin_top = arc_pts(cx, gy - 4, bw, bh, 180, 360, 30)
    basin = arc_pts(cx, gy - 4, bw, bh, 180, 360, 30) + arc_pts(cx, gy + 10, bw, bh, 0, 180, 30)
    o.append(p.shape(basin, 2.2))
    o.append(p.hatch(arc_pts(cx, gy - 4, bw - 6, bh - 4, 0, 180, 20) + arc_pts(cx, gy + 9, bw - 6, bh - 2, 180, 0, 20), 0, 3.0, 1.0, 0.75))
    # water surface ripples inside the basin
    o.append(p.ripples(cx - 110, cx + 90, gy - 12, gy - 1, 22, lmin=6, lmax=12, wmin=1.0, wmax=1.2, amp=0.8))
    # railing posts in front of basin
    for i in range(-12, 13):
        x = cx + i * 10.8
        yb = gy + 10 + bh * math.sqrt(max(0, 1 - ((x - cx) / bw) ** 2))
        o.append(p.seg(x, yb + 2, x, yb - 12, 1.3, 0.2))
    o.append(p.line(arc_pts(cx, gy + 12, bw, bh, 0, 180, 30), 1.4, 0.3))
    o.append(p.line(arc_pts(cx, gy + 4, bw, bh, 0, 180, 30), 1.4, 0.3))
    # tritons spouting from the basin
    for tx, s in ((cx - 82, -1), (cx + 82, 1)):
        o.append(p.solid([(tx - 6, gy + 2), (tx - 4, gy - 14), (tx, gy - 20), (tx + 4, gy - 14), (tx + 6, gy + 2)]))
        o.append(f'<circle cx="{tx:.1f}" cy="{gy - 23:.1f}" r="3.6" fill="{INK}"/>')
        o.append(p.line([(tx + 2 * s, gy - 24), (tx + 6 * s, gy - 30), (tx + 10 * s, gy - 30)], 2, 0.2))
        o.append(f'<path d="M{tx + 10 * s:.1f} {gy - 30:.1f}q{18 * s:.1f} -14 {34 * s:.1f} 20" fill="none" stroke="{INK}" stroke-width="1.3" stroke-dasharray="4 3"/>')
    # pedestal
    ped = [(cx - 16, gy - 4), (cx - 10, gy - 30), (cx - 6, gy - 62), (cx + 6, gy - 62), (cx + 10, gy - 30), (cx + 16, gy - 4)]
    o.append(p.shape(ped, 2.2))
    o.append(p.hatch(ped, 90, 2.6, 1.0, 0.9, keep=lambda x, y: 0.15 + (x - cx + 16) / 32))
    # big lower bowl
    by = gy - 64
    bowl = arc_pts(cx, by, 74, 9, 180, 360, 24) + [(cx + 74, by), (cx + 50, by + 14), (cx + 16, by + 20), (cx - 16, by + 20), (cx - 50, by + 14), (cx - 74, by)]
    # falling water curtain from the lower bowl
    for i in range(26):
        x = cx - 72 + i * 5.8
        if abs(x - cx) < 10:
            continue
        o.append(f'<path d="M{x:.1f} {by + 4:.1f}q{(x - cx) * 0.08:.1f} 14 {(x - cx) * 0.14:.1f} {gy - by - 14:.1f}" fill="none" stroke="{INK}" stroke-width="1" opacity="0.7" stroke-dasharray="{rnd.uniform(4, 9):.0f} {rnd.uniform(2, 4):.0f}"/>')
    o.append(p.shape(bowl, 2.4))
    o.append(p.hatch([(cx + 10, by + 3), (cx + 74, by), (cx + 50, by + 14), (cx + 16, by + 20)], 125, 2.8, 1.0, 0.9))
    o.append(p.line([(cx - 76, by), (cx + 76, by)], 2.6, 0.3))
    for i in range(-6, 7):                  # gadrooning on the bowl
        x = cx + i * 10
        o.append(p.seg(x * 0.98 + cx * 0.02, by + 2, x * 0.7 + cx * 0.3, by + 17, 1.0, 0.2))
    # stem and upper bowl
    st = [(cx - 6, by - 6), (cx - 4, by - 44), (cx + 4, by - 44), (cx + 6, by - 6)]
    o.append(p.shape(st, 2.0))
    o.append(p.hatch(st, 90, 2.2, 1, 0.9, keep=lambda x, y: (x - cx + 6) / 12))
    uy = by - 46
    ub = arc_pts(cx, uy, 34, 5, 180, 360, 16) + [(cx + 34, uy), (cx + 12, uy + 10), (cx - 12, uy + 10), (cx - 34, uy)]
    for i in range(14):
        x = cx - 32 + i * 4.9
        o.append(f'<path d="M{x:.1f} {uy + 3:.1f}q{(x - cx) * 0.25:.1f} 12 {(x - cx) * 0.45:.1f} {40:.1f}" fill="none" stroke="{INK}" stroke-width="1" opacity="0.65" stroke-dasharray="5 3"/>')
    o.append(p.shape(ub, 2.2))
    o.append(p.hatch([(cx + 5, uy + 2), (cx + 34, uy), (cx + 12, uy + 10)], 125, 2.6, 1, 0.9))
    # crowning figure on a small plinth
    fy = uy - 4
    o.append(p.shape(rect(cx - 5, fy - 10, 10, 10), 1.6))
    fig = [(cx - 5, fy - 10), (cx - 4, fy - 26), (cx - 6, fy - 34), (cx - 2, fy - 38), (cx + 2, fy - 38), (cx + 5, fy - 33), (cx + 4, fy - 26), (cx + 6, fy - 10)]
    o.append(p.solid(fig))
    o.append(f'<circle cx="{cx:.1f}" cy="{fy - 42:.1f}" r="3.6" fill="{INK}"/>')
    o.append(p.seg(cx + 6, fy - 46, cx + 7, fy - 12, 1.6, 0.2))    # staff
    o.append(p.seg(cx - 5, fy - 32, cx - 13, fy - 38, 1.8, 0.2))
    # fountain jet spray
    o.append(f'<path d="M{cx - 10:.1f} {fy - 44:.1f}q-10 -8 -16 4M{cx + 10:.1f} {fy - 46:.1f}q10 -10 18 2" fill="none" stroke="{INK}" stroke-width="1.1" stroke-dasharray="3 3"/>')
    # --- benches and lamps along the path
    for bx, s in ((176, -1), (424, 1)):
        o.append(p.line([(bx - 22, 470), (bx + 22, 470)], 2.4, 0.3))
        o.append(p.line([(bx - 22, 458), (bx + 22, 458)], 1.6, 0.3))
        o.append(p.line([(bx - 22, 452), (bx + 22, 452)], 1.6, 0.3))
        for lx in (bx - 18, bx + 18):
            o.append(p.seg(lx, 452, lx, 482, 1.6, 0.2))
    o.append(p.lamp(214, 436, 66, arms=2))
    o.append(p.lamp(386, 436, 66, arms=2))
    # walkers on the path: a woman with a dog, and a pair
    o.append(p.person(330, 470, 30, pose=0, flip=True, dress=True))
    o.append(f'<path d="M{334:.1f} {458:.1f}q8 6 14 6" stroke="{INK}" stroke-width="1.1" fill="none"/>'
             f'<path d="M346 462h10l2 -3l2 3v6h-2v-3h-8v3h-2Z" fill="{INK}"/>')
    o.append(p.person(262, 448, 19, pose=1) + p.person(270, 449, 20, pose=0, dress=True))
    # --- the live oaks: one on each side, limbs sweeping up and over the path, dripping Spanish moss
    def limb(ctrl, w0, w1, lvl=3):
        return p.branch(ctrl, w0, w1)

    crownL = [(-10, -10), (330, -10), (330, 40), (300, 70), (262, 96), (226, 118), (190, 150), (150, 178), (110, 214),
              (78, 240), (40, 262), (-10, 270)]
    crownR = [(300, -10), (610, -10), (610, 268), (570, 258), (530, 236), (494, 206), (452, 178), (410, 150), (372, 118),
              (340, 92), (316, 62), (300, 40)]
    for cp in (crownL, crownR):
        cp = smooth(cp, 4)
        o.append(p.scribble(0, 0, 1, 1, sp=4.4, loop=2.8, w=1.1, poly=cp, base=0.75, shade=1.0, dark=0.6,
                            light=(0.2, -1), cr=(16, 30)))
    # trunks: dark silhouettes framing the view, bark picked out in broken paper lines
    o.append(p.branch([(10, 620), (30, 520), (36, 420), (30, 330), (6, 260), (-30, 220)], 74, 50))
    o.append(p.branch([(590, 620), (570, 520), (564, 420), (570, 330), (594, 262), (630, 224)], 74, 50))
    # gnarled limbs sweeping up and over the path
    o.append(limb([(30, 330), (80, 282), (120, 262), (170, 228), (214, 206), (262, 186), (318, 172)], 32, 6))
    o.append(limb([(50, 400), (84, 330), (118, 300), (132, 262), (156, 238)], 20, 5))
    o.append(limb([(6, 270), (52, 214), (100, 190), (132, 160), (178, 146)], 24, 5))
    o.append(limb([(570, 330), (520, 286), (482, 262), (430, 232), (386, 214), (346, 204), (310, 204)], 30, 6))
    o.append(limb([(552, 400), (516, 330), (484, 302), (468, 266), (446, 244)], 20, 5))
    o.append(limb([(594, 272), (548, 214), (500, 192), (470, 162), (424, 148)], 24, 5))
    for ctrl in (([(200, 214), (210, 232), (226, 246)]), ([(118, 296), (98, 312), (90, 330)]), ([(412, 226), (398, 244), (386, 252)]),
                 ([(484, 300), (504, 318), (510, 334)]), ([(256, 190), (270, 170), (286, 160)]), ([(350, 194), (334, 174), (318, 166)])):
        o.append(limb(ctrl, 6, 2))
    # Spanish moss: tapering beards of wavy strands, stippled where they bunch
    def moss(x, y, L, wdt=14):
        L *= 1.25
        strands = []
        for k in range(rnd.randint(9, 13)):
            sx = x + rnd.uniform(-wdt / 2, wdt / 2)
            ll = L * rnd.uniform(0.45, 1.0) * (1 - abs(sx - x) / wdt)
            sway = rnd.uniform(-4, 4)
            strands.append(f"M{sx:.1f} {y + rnd.uniform(-2, 2):.1f}c{sway:.1f} {ll * 0.3:.1f} {-sway:.1f} {ll * 0.6:.1f} {sway * 0.5 + (x - sx) * 0.3:.1f} {ll:.1f}")
        return (f'<path d="{"".join(strands)}" fill="none" stroke="{INK}" stroke-width="1.1" stroke-linecap="round"/>'
                + p.stipple([(x - wdt / 2, y), (x + wdt / 2, y), (x + 2, y + L * 0.45), (x - 2, y + L * 0.45)], int(L * 0.35), r=(0.5, 0.9)))
    for x, y, L in ((112, 244, 56), (148, 226, 66), (186, 206, 50), (226, 194, 70), (264, 182, 40), (340, 186, 46), (378, 194, 72),
                    (416, 210, 52), (452, 228, 64), (490, 250, 58), (80, 230, 40), (128, 178, 48), (172, 158, 40), (226, 126, 46),
                    (270, 98, 36), (338, 96, 38), (382, 128, 50), (440, 166, 44), (488, 190, 50), (528, 242, 40), (300, 52, 30)):
        o.append(moss(x, y, L))
    o.append(p.birds([(286, 250, 0.7), (300, 244, 0.55), (318, 252, 0.6)], 7))
    # --- title cartouche
    o.append(cartouche(p, 112, 466, 488, 540, 10, 2.4))
    sz = name_size(name, 320, 50)
    o.append(title_text(300, 506, name, sz))
    o.append(coord_line(p, 300, 528, coords, 16, 2.2, 20, 10))
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- VENICE
@design("venice", "Venice", "45.4408° N · 12.3155° E")
def venice(name, coords):
    """Santa Maria della Salute across the mouth of the Grand Canal, from the gondola moorings on the Molo."""
    p = Pen("venice", 23)
    rnd = p.rnd
    o = [p.paper(3, vignette=0.3)]
    WL = 402
    SX = 350
    # --- sky: light horizontal pen strokes behind the domes, fading upward (a summer haze)
    sky = [(0, 190), (600, 190), (600, WL - 4), (0, WL - 4)]
    o.append(p.hatch(sky, -4, 4.6, 1.0, 0.7, dash=(14, 46), keep=lambda x, y: max(0, (y - 200) / (WL - 200)) ** 1.3))
    o.append(p.birds([(150, 232), (168, 222, 0.7), (486, 206, 0.8), (504, 216, 0.6)], 7))
    # --- Giudecca far shore, very light
    o.append(p.line([(440, WL - 16), (560, WL - 16)], 1.1, 0.4))
    o.append(p.line([(440, WL - 16), (446, WL - 26), (470, WL - 26), (474, WL - 34), (480, WL - 26), (560, WL - 24)], 1.1, 0.5, op=0.7))
    # --- palazzi on the right of the basilica
    for x0, w, h in ((452, 42, 46), (494, 36, 54), (530, 80, 40)):
        o.append(p.shape(rect(x0, WL - h, w, h), 1.6))
        o.append(p.windows(x0 + 5, WL - h + 8, max(1, int((w - 6) / 10)), 3, 4.5, 7, 5.5, 6, w=1.0, dark=0.6, sill=False))
        o.append(p.hatch(rect(x0, WL - h, w, h), 60, 5, 1.0, 0.45))
    # --- the bell towers and the second dome behind
    for tx in (432, 486):
        o.append(p.shape(rect(tx - 6, WL - 140, 12, 110), 1.8))
        o.append(p.hatch(rect(tx, WL - 140, 6, 80), 90, 2.2, 1.0, 0.9))
        o.append(f'<path d="M{tx - 3:.1f} {WL - 126:.1f}v10M{tx + 3:.1f} {WL - 126:.1f}v10" stroke="{INK}" stroke-width="2"/>')
        o.append(p.shape(arc_pts(tx, WL - 140, 8, 9, 180, 360, 10), 1.6))
        o.append(p.seg(tx, WL - 149, tx, WL - 162, 1.6, 0.2) + f'<circle cx="{tx}" cy="{WL - 152}" r="2.2" fill="{INK}"/>')
    o.append(p.shape(rect(440, WL - 108, 40, 20), 1.6))
    d2 = arc_pts(460, WL - 108, 24, 24, 180, 360, 16)
    o.append(p.shape(d2, 1.8))
    o.append(p.hatch(d2 + [(460, WL - 108)], 70, 2.8, 1.0, 0.8, keep=lambda x, y: (x - 452) / 30))
    o.append(p.shape(rect(455, WL - 140, 10, 9), 1.3) + p.shape(arc_pts(460, WL - 140, 6, 6, 180, 360, 8), 1.3) + p.seg(460, WL - 146, 460, WL - 156, 1.4))
    # --- Punta della Dogana: low customs house and its tower with the golden globe
    o.append(p.shape(rect(92, WL - 40, 170, 40), 2.0))
    o.append(p.windows(140, WL - 32, 10, 2, 5, 8, 6.5, 6, w=1.0, dark=0.7, arch=True, sill=False))
    o.append(p.hatch(rect(92, WL - 12, 170, 12), 0, 2.6, 1.0, 0.7))
    o.append(p.line([(90, WL - 41), (264, WL - 41)], 2.4, 0.3))
    tw = rect(96, WL - 76, 36, 76)
    o.append(p.shape(tw, 2.0))
    o.append(p.hatch([(118, WL - 76), (132, WL - 76), (132, WL), (118, WL)], 90, 2.4, 1.0, 0.85))
    o.append(p.windows(106, WL - 66, 1, 2, 8, 12, 0, 8, w=1.1, dark=1.0, arch=True))
    o.append(p.line([(92, WL - 77), (136, WL - 77)], 2.6, 0.2))
    o.append(p.person(106, WL - 78, 13, 1) + p.person(122, WL - 78, 13, 1, flip=True))
    o.append(f'<circle cx="114" cy="{WL - 99}" r="11" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>')
    o.append(p.hatch(arc_pts(114, WL - 99, 10, 10, 0, 360, 16), 120, 2.4, 1.0, 0.8, keep=lambda x, y: (x - 108) / 14))
    o.append(p.solid([(112, WL - 110), (116, WL - 110), (117, WL - 126), (111, WL - 126)]) + f'<circle cx="114" cy="{WL - 129}" r="2.4" fill="{INK}"/>'
             + p.line([(116, WL - 124), (128, WL - 130), (126, WL - 118)], 1.6, 0.2))
    # the Seminario wing between
    o.append(p.shape(rect(236, WL - 52, 40, 52), 1.6))
    o.append(p.windows(242, WL - 44, 3, 3, 5, 8, 5, 6, w=1.0, dark=0.5, sill=False))
    # --- the basilica: steps, octagon, scroll buttresses, drum, dome, lantern
    o.append(p.shape([(258, WL), (262, WL - 16), (444, WL - 16), (448, WL)], 2.0))
    for i in range(1, 4):
        o.append(p.line([(259 + i, WL - i * 4), (447 - i, WL - i * 4)], 1.2, 0.2))
    body_y = WL - 72
    o.append(p.shape([(262, WL - 16), (262, body_y), (296, body_y - 4), (404, body_y - 4), (440, body_y), (440, WL - 16)], 2.4))
    o.append(p.line([(296, body_y - 4), (296, WL - 16)], 1.8) + p.line([(404, body_y - 4), (404, WL - 16)], 1.8))
    # shaded oblique face on the right
    o.append(p.tone([(404, body_y - 4), (440, body_y), (440, WL - 16), (404, WL - 16)], 3, 70, 3.4))
    o.append(p.hatch([(262, body_y), (296, body_y - 4), (296, WL - 16), (262, WL - 16)], 80, 5.5, 1.0, 0.6))
    # cornice
    o.append(p.line([(258, body_y + 1), (296, body_y - 3), (408, body_y - 3), (444, body_y + 1)], 3.0, 0.2))
    o.append(p.line([(262, body_y + 7), (296, body_y + 3), (404, body_y + 3), (440, body_y + 7)], 1.3, 0.2))
    # triumphal-arch facade: portal, paired columns, niches with statues, pediment
    o.append(p.shape([(SX - 20, WL - 16), (SX - 20, WL - 50)] + arc_pts(SX, WL - 50, 20, 20, 180, 360, 12) + [(SX + 20, WL - 16)], 2.0, fill=INK))
    for cxl in (SX - 44, SX - 34, SX + 34, SX + 44):
        o.append(p.shape(rect(cxl - 3, body_y + 6, 6, WL - 16 - body_y - 6), 1.5))
        o.append(p.seg(cxl + 1.2, body_y + 9, cxl + 1.2, WL - 19, 1.0))
    for nx in (SX - 39, SX + 39):
        o.append(p.shape([(nx - 5, WL - 40), (nx - 5, WL - 52)] + arc_pts(nx, WL - 52, 5, 5, 180, 360, 6) + [(nx + 5, WL - 40)], 1.3, fill=INK))
    for cxl in (275, 285, 418, 428):
        o.append(p.seg(cxl, body_y + 8, cxl, WL - 18, 1.4))
    o.append(p.windows(276, body_y + 18, 1, 1, 8, 14, 0, 0, w=1.2, dark=1, arch=True))
    o.append(p.windows(417, body_y + 18, 1, 1, 8, 14, 0, 0, w=1.2, dark=1, arch=True))
    ped = [(SX - 52, body_y - 3), (SX, body_y - 26), (SX + 52, body_y - 3)]
    o.append(p.shape(ped, 2.2))
    o.append(p.line([(SX - 40, body_y - 6), (SX, body_y - 20), (SX + 40, body_y - 6)], 1.1, 0.2))
    o.append(f'<circle cx="{SX}" cy="{body_y - 11}" r="3" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    for sx_, h in ((SX - 52, 12), (SX, 14), (SX + 52, 12), (262, 10), (440, 10)):
        y0 = body_y - (26 if sx_ == SX else 4)
        o.append(p.solid([(sx_ - 2.5, y0), (sx_ - 2, y0 - h + 4), (sx_ + 2, y0 - h + 4), (sx_ + 2.5, y0)]) + f'<circle cx="{sx_}" cy="{y0 - h + 2}" r="2.2" fill="{INK}"/>')
    # drum
    dy0, dy1 = WL - 136, WL - 94
    o.append(p.shape(rect(SX - 54, dy0, 108, dy1 - dy0), 2.2))
    o.append(p.tone(rect(SX + 26, dy0, 28, dy1 - dy0), 2, 75, 3.4))
    for i in range(5):
        wx = SX - 42 + i * 21
        o.append(p.shape([(wx - 4, dy1 - 8), (wx - 4, dy0 + 14)] + arc_pts(wx, dy0 + 14, 4, 4, 180, 360, 6) + [(wx + 4, dy1 - 8)], 1.2, fill=INK))
        o.append(p.seg(wx + 10.5, dy0 + 4, wx + 10.5, dy1 - 2, 1.1))
    o.append(p.line([(SX - 58, dy0), (SX + 58, dy0)], 3.0, 0.2) + p.line([(SX - 56, dy1), (SX + 56, dy1)], 2.0, 0.2))
    # volutes (the great scrolls) bridging the octagon to the drum, with statues on top
    for i, vx in enumerate((272, 300, 330, 370, 400, 428)):
        s = -1 if vx < SX else 1
        top = (vx - s * 6, dy1 - 4)
        o.append(p.line([(vx + s * 8, body_y - 4), (vx + s * 2, body_y - 14), (top[0], top[1] + 4)], 2.0, 0.3))
        o.append(f'<circle cx="{vx + s * 6:.1f}" cy="{body_y - 10:.1f}" r="5.5" fill="{PAPER}" stroke="{INK}" stroke-width="1.8"/>'
                 f'<path d="M{vx + s * 6:.1f} {body_y - 10:.1f}m-2 0a2 2 0 1 1 2.5 1.5" fill="none" stroke="{INK}" stroke-width="1.3"/>')
        o.append(p.solid([(top[0] - 2.4, top[1] + 2), (top[0] - 2, top[1] - 8), (top[0] + 2, top[1] - 8), (top[0] + 2.4, top[1] + 2)])
                 + f'<circle cx="{top[0]:.1f}" cy="{top[1] - 10:.1f}" r="2.1" fill="{INK}"/>')
    # dome: lit from the left, ribbed, shaded with hatching and stipple
    dome = arc_pts(SX, dy0, 62, 60, 180, 360, 30)
    o.append(p.shape(dome + [(SX + 62, dy0)], 2.6))
    o.append(p.hatch(dome, 105, 3.0, 1.05, 0.9, keep=lambda x, y: max(0, (x - SX + 8) / 50)))
    o.append(p.hatch(dome, 60, 3.4, 1.0, 0.8, keep=lambda x, y: max(0, (x - SX - 22) / 36)))
    o.append(p.stipple(dome, 90, r=(0.5, 0.9), keep=lambda x, y: max(0, 0.6 - abs(x - SX + 6) / 60)))
    for k in (-0.75, -0.4, 0.0, 0.4, 0.75):
        rib = [(SX + 62 * k * math.cos(math.radians(a)) if False else SX + 62 * k * math.sin(math.radians(90 - a)) * 1, 0) for a in (0,)]
        pts = [(SX + 62 * k * math.cos(math.radians(t)), dy0 - 60 * math.sin(math.radians(t))) for t in range(0, 91, 10)]
        o.append(p.line(pts, 1.2, 0.2))
    # lantern
    o.append(p.shape(rect(SX - 11, dy0 - 76, 22, 18), 1.8))
    o.append(p.windows(SX - 7, dy0 - 72, 2, 1, 4, 9, 6, 0, w=1.0, dark=1, arch=True, sill=False))
    o.append(p.shape(arc_pts(SX, dy0 - 76, 12, 10, 180, 360, 10), 1.8))
    o.append(p.seg(SX, dy0 - 86, SX, dy0 - 104, 1.8) + f'<circle cx="{SX}" cy="{dy0 - 92}" r="2.5" fill="{INK}"/>')
    o.append(p.seg(SX - 5, dy0 - 99, SX + 5, dy0 - 99, 1.6))
    # --- reflections and water
    o.append(p.reflect(258, 448, WL + 2, 110, density=0.75, sp=3.4, w=1.25))
    o.append(p.reflect(92, 264, WL + 2, 46, density=0.6, sp=3.6, w=1.2))
    o.append(p.reflect(450, 600, WL + 2, 40, density=0.5, sp=3.8, w=1.1))
    o.append(p.line([(40, WL), (560, WL)], 2.0, 0.4))
    o.append(p.ripples(40, 560, WL + 4, 560, 260, hy=WL, lmin=5, lmax=30, wmin=1.0, wmax=1.9))
    # a water taxi crossing midstream, with its wake
    o.append(p.shape([(178, 432), (182, 440), (242, 440), (252, 431)], 1.8))
    o.append(p.shape(rect(196, 423, 30, 9), 1.4, fill=INK) + p.windows(199, 425, 4, 1, 4, 4, 3, 0, w=0.8, dark=0, sill=False))
    o.append(f'<path d="M176 440q-20 2 -46 -1M178 437q-24 6 -60 6" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    # --- mooring poles (paline) with spiral bands, a gull on one
    for px, top, wdt in ((512, 330, 11), (536, 346, 10), (88, 404, 9)):
        pole = rect(px - wdt / 2, top, wdt, 600 - top)
        o.append(p.shape(pole, 2.0))
        y = top + 16
        while y < 590:
            band = [(px - wdt / 2, y), (px + wdt / 2, y - 5), (px + wdt / 2, y + 7), (px - wdt / 2, y + 12)]
            o.append(p.solid(band))
            y += 26
        o.append(p.hatch([(px + 1, top), (px + wdt / 2, top), (px + wdt / 2, 600), (px + 1, 600)], 90, 2.0, 1.0, 0.8))
        o.append(p.shape([(px - wdt / 2 - 1, top), (px, top - 10), (px + wdt / 2 + 1, top)], 1.6, fill=INK))
    o.append(p.solid([(503, 324), (520, 324), (524, 318), (516, 314), (507, 316)]) + f'<circle cx="519" cy="312" r="3" fill="{INK}"/>'
             + f'<path d="M521 312l5 1" stroke="{INK}" stroke-width="1.4"/>' + p.line([(506, 318), (494, 312)], 1.6))
    # --- the gondola, moored in the foreground with its tarp on
    top = smooth([(52, 444), (90, 476), (170, 494), (300, 498), (420, 490), (474, 470), (494, 452)], 8)
    bot = smooth([(494, 452), (480, 480), (420, 508), (300, 517), (170, 512), (96, 494), (52, 444)], 8)
    hull = top + bot
    o.append(p.reflect(80, 480, 519, 30, density=0.95, sp=3, w=1.5, taper=0.5))
    o.append(p.solid(hull))
    o.append(p.line(top[3:-3], 1.2, 0.2, color=PAPER, op=0.85))
    o.append(p.line([lerp(a, b, 0.5) for a, b in zip(top[6:-6], bot[::-1][6:-6])], 0.9, 0.2, color=PAPER, op=0.5))
    # tarp hump and the forcola
    tarp = smooth([(180, 495), (210, 476), (300, 470), (380, 476), (410, 492)], 6)
    o.append(p.shape(tarp, 2.0))
    o.append(p.hatch(tarp + [(300, 498)], 0, 3.0, 1.0, 0.75, keep=lambda x, y: (y - 466) / 30))
    for tx in (230, 270, 320, 360):
        o.append(p.seg(tx, 484, tx + 3, 496, 1.2))
    o.append(p.line([(140, 490), (138, 470), (146, 464), (150, 472), (148, 490)], 2.0, 0.2))
    # the ferro on the prow: S-blade with six teeth
    fx, fy = 494, 438
    o.append(p.shape([(fx - 3, fy + 4), (fx - 1, fy - 14), (fx + 4, fy - 26), (fx + 12, fy - 30), (fx + 10, fy - 22), (fx + 6, fy - 14), (fx + 5, fy + 2)], 1.6, fill=INK))
    for i in range(6):
        o.append(p.seg(fx + 4, fy - 12 + i * 3, fx + 13, fy - 13 + i * 3, 1.8, 0.1))
    o.append(p.line([(fx + 4, fy - 20), (fx + 12, fy - 20)], 1.8))
    # stern curl
    o.append(p.line([(52, 444), (46, 434), (50, 428)], 2.4, 0.2))
    # --- title in the sky
    sz = name_size(name, 380, 76)
    o.append(title_text(300, 120, name, sz))
    o.append(coord_line(p, 300, 150, coords, 17, 2.6, 30, 12))
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- AMSTERDAM
def gable_uv(kind, w, H, G):
    """Outline of a canal-house top in facade coordinates (u across 0..w, v up), from left eave to right eave."""
    if kind == "step":
        s = w / 7
        return [(0, H), (0, H + G * 0.3), (s, H + G * 0.3), (s, H + G * 0.55), (2 * s, H + G * 0.55), (2 * s, H + G * 0.8),
                (3 * s, H + G * 0.8), (3 * s, H + G), (4 * s, H + G), (4 * s, H + G * 0.8), (5 * s, H + G * 0.8),
                (5 * s, H + G * 0.55), (6 * s, H + G * 0.55), (6 * s, H + G * 0.3), (w, H + G * 0.3), (w, H)]
    if kind == "neck":
        a, b = w * 0.27, w * 0.73
        return [(0, H), (0, H + 0.4), (a - 0.5, H + 0.6), (a, H + G * 0.35), (a, H + G * 0.85), (w / 2, H + G * 1.05),
                (b, H + G * 0.85), (b, H + G * 0.35), (b + 0.5, H + 0.6), (w, H + 0.4), (w, H)]
    if kind == "bell":
        pts = [(0, H)]
        for i in range(9):
            t = i / 8
            pts.append((w * 0.32 * math.sin(t * math.pi / 2) ** 0.7, H + G * 0.75 * t))
        pts += [(w * 0.38, H + G * 0.9), (w / 2, H + G * 1.05), (w * 0.62, H + G * 0.9)]
        for i in range(8, -1, -1):
            t = i / 8
            pts.append((w - w * 0.32 * math.sin(t * math.pi / 2) ** 0.7, H + G * 0.75 * t))
        return pts + [(w, H)]
    if kind == "spout":
        return [(0, H), (w * 0.4, H + G * 0.85), (w * 0.4, H + G), (w * 0.6, H + G), (w * 0.6, H + G * 0.85), (w, H)]
    return [(0, H), (0, H + 0.9), (w, H + 0.9), (w, H)]       # straight cornice


@design("amsterdam", "Amsterdam", "52.3676° N · 4.9041° E")
def amsterdam(name, coords):
    """Looking down a canal from a bridge: gabled houses leaning over the water, elms, a houseboat, a sloop,
    and bikes chained to the parapet whose stone plaque carries the name."""
    p = Pen("amsterdam", 31)
    rnd = p.rnd
    C = Cam(f=270, cx=300, vpy=236, eye=3.4)
    o = [p.paper(5)]
    QX, FX = 5.6, 10.5
    ZFAR = 112
    # --- the far end: a row of houses facing us, behind an arched bridge
    xs = -FX
    far = []
    while xs < FX:
        w = rnd.uniform(5, 7)
        H = rnd.uniform(11, 15)
        kind = rnd.choice(["step", "neck", "bell", "spout"])
        poly = [C(xs, 0, ZFAR + 6)] + [C(xs + u, v, ZFAR + 6) for u, v in gable_uv(kind, w, H, 4)] + [C(xs + w, 0, ZFAR + 6)]
        far.append(p.shape(poly, 1.3))
        far.append(p.hatch(poly, 70, 3.6, 1.0, 0.45))
        xs += w
    o += far
    # --- facades down both sides
    def side(X, sgn):
        out = []
        z = 5.0
        houses = []
        while z < ZFAR:
            w = rnd.uniform(5.5, 8.5)
            houses.append((z, w, rnd.uniform(10.5, 14), rnd.choice(["step", "neck", "bell", "spout", "neck", "flat"]), rnd.random()))
            z += w
        for z0, w, H, kind, tint in reversed(houses):
            G = 4.6 if kind != "flat" else 1
            uv = gable_uv(kind, w, H, G)
            poly = [C(X, 0.8, z0)] + [C(X, v, z0 + u) for u, v in uv] + [C(X, 0.8, z0 + w)]
            out.append(p.shape(poly, 1.9 if z0 < 50 else 1.4))
            # tone: shaded right bank hatched; on the sunlit left, brick courses running to the vanishing point
            if sgn > 0:
                out.append(p.hatch(poly, 80, 3.6 if z0 < 60 else 4.6, 1.0, 0.7))
            elif tint < 0.6:
                yy = 1.2
                crs = []
                while yy < H:
                    za = z0 + rnd.uniform(0, w * 0.3)
                    zb = z0 + w - rnd.uniform(0, w * 0.3)
                    if rnd.random() < 0.45:
                        a_, b_ = C(X, yy, za), C(X, yy, zb)
                        crs.append(f"M{a_[0]:.1f} {a_[1]:.1f}L{b_[0]:.1f} {b_[1]:.1f}")
                    yy += 0.55
                out.append(f'<path d="{"".join(crs)}" stroke="{INK}" stroke-width="0.9" opacity="0.55"/>')
            # cornice line under the gable
            if kind != "flat":
                a_, b_ = C(X, H, z0), C(X, H, z0 + w)
                out.append(p.seg(a_[0], a_[1], b_[0], b_[1], 1.8 if z0 < 50 else 1.2, 0.1))
            # windows: tall sashes with white frames and dark glass, floor by floor
            floors = int((H - 2) / 3.0)
            cols = 3 if w > 6.8 else 2
            for f in range(floors):
                ya = 2.4 + f * 3.0
                for c in range(cols):
                    ua = (w / cols) * (c + 0.5) - 0.65
                    q = [C(X, ya, z0 + ua), C(X, ya + 2.0, z0 + ua), C(X, ya + 2.0, z0 + ua + 1.3), C(X, ya, z0 + ua + 1.3)]
                    span = abs(q[2][0] - q[0][0])
                    if span < 1.6:
                        continue
                    if span < 5:
                        out.append(f'<polygon points="{P(q)}" fill="{INK}"/>')
                        continue
                    out.append(f'<polygon points="{P(q)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>')
                    qi = [C(X, ya + 0.15, z0 + ua + 0.15), C(X, ya + 1.85, z0 + ua + 0.15), C(X, ya + 1.85, z0 + ua + 1.15), C(X, ya + 0.15, z0 + ua + 1.15)]
                    out.append(f'<polygon points="{P(qi)}" fill="{INK}"/>')
                    m1, m2 = lerp(qi[0], qi[1], 0.45), lerp(qi[3], qi[2], 0.45)
                    n1, n2 = lerp(qi[0], qi[3], 0.5), lerp(qi[1], qi[2], 0.5)
                    out.append(f'<path d="M{m1[0]:.1f} {m1[1]:.1f}L{m2[0]:.1f} {m2[1]:.1f}M{n1[0]:.1f} {n1[1]:.1f}L{n2[0]:.1f} {n2[1]:.1f}" stroke="{PAPER}" stroke-width="1.2"/>')
            # door at street level and the hoist beam under the gable top
            dq = [C(X, 0.8, z0 + w * 0.2), C(X, 2.4, z0 + w * 0.2), C(X, 2.4, z0 + w * 0.2 + 1.1), C(X, 0.8, z0 + w * 0.2 + 1.1)]
            out.append(f'<polygon points="{P(dq)}" fill="{INK}"/>')
            if kind != "flat":
                hb = C(X, H + G * 0.62, z0 + w / 2)
                hb2 = C(X - sgn * 1.0, H + G * 0.62, z0 + w / 2)
                out.append(p.seg(hb[0], hb[1], hb2[0], hb2[1], 2.0 if z0 < 40 else 1.4, 0.1))
        return out

    o += side(-FX, -1)
    o += side(FX, 1)
    # --- the far bridge: arch over the water, lamps on the parapet
    deck = [C(-FX, 1.2, ZFAR - 2), C(-FX, 3.6, ZFAR - 2), C(FX, 3.6, ZFAR - 2), C(FX, 1.2, ZFAR - 2)]
    o.append(p.shape(deck, 1.6))
    arch = [C(-4.5 + 9 * i / 16, 0.2 + 2.4 * math.sin(math.pi * i / 16) ** 0.6, ZFAR - 2) for i in range(17)]
    o.append(p.shape(arch + [C(4.5, 0.2, ZFAR - 2)], 1.3, fill=INK))
    for lx in (-6, 6):
        a, b = C(lx, 3.6, ZFAR - 2), C(lx, 6, ZFAR - 2)
        o.append(p.seg(a[0], a[1], b[0], b[1], 1.3) + f'<circle cx="{b[0]:.1f}" cy="{b[1]:.1f}" r="1.6" fill="{INK}"/>')
    # --- quays: brick walls along the water, the cobbled street above them
    for X in (-QX, QX):
        top = [C(X, 1.2, 5), C(X, 1.2, ZFAR - 2)]
        bot = [C(X, 0, ZFAR - 2), C(X, 0, 5)]
        wall = top + bot
        o.append(p.shape(wall, 1.8))
        o.append(p.hatch(wall, 0, 2.6, 1.0, 0.8 if X > 0 else 0.55, dash=(6, 20)))
        street = [C(X, 1.2, 5), C(X, 1.2, ZFAR - 2), C(FX * (1 if X > 0 else -1), 1.2, ZFAR - 2), C(FX * (1 if X > 0 else -1), 1.2, 5)]
        o.append(p.stipple(street, 120, r=(0.5, 1.0)))
        # bollards and bikes along the quay edge
        for z in (9, 13, 19, 27, 38, 52):
            a, b = C(X * 1.03, 1.6, z), C(X * 1.03, 2.5, z)
            o.append(p.seg(a[0], a[1], b[0], b[1], max(1.4, 30 / z), 0.1))
        for z in (16, 24):
            q = C(X * 1.06, 1.6, z)
            o.append(p.bike(q[0], q[1], 8.5 / z, flip=X > 0, w=1.3))
    # --- elms along both quays
    trees = []
    for X, zs in ((-8.2, (64, 84)), (8.2, (10, 20, 31, 43, 57, 73, 92))):
        for z in zs:
            trees.append((X, z + rnd.uniform(-1.5, 1.5)))
    for X, z in sorted(trees, key=lambda t: -t[1]):
        base = C(X, 1.6, z)
        top = C(X, 6.0, z)
        ctr = C(X, 8.6, z)
        r = 270 * 3.4 / z
        o.append(p.line([base, top], max(1.6, 270 * 0.3 / z), 0.3))
        o.append(p.solid(arc_pts(ctr[0], ctr[1], r * 1.02, r * 0.86, 0, 360, 24), PAPER))
        o.append(p.scribble(ctr[0], ctr[1], r, r * 0.84, sp=max(3.6, 5.5 - 40 / z), loop=max(1.8, min(3.2, 48 / z)), w=1.05,
                            base=0.55, shade=1.0, dark=0.3 if X > 0 else 0.0, light=(-1, -0.6), cr=(max(6, r * 0.35), max(9, r * 0.6))))
    # --- water: reflections of the walls and trees, ripples
    water = [C(-QX, 0, 5), C(-QX, 0, ZFAR - 2), C(QX, 0, ZFAR - 2), C(QX, 0, 5)]
    for X in (-QX, QX):
        a, b = C(X, 0, 5), C(X, 0, ZFAR - 2)
        refl = [a, b, C(X * 0.7, -5, ZFAR - 2), C(X * 0.7, -5, 5)]
        refl = [(x, max(y, a[1] if False else y)) for x, y in refl]
        o.append(p.hatch([(x, min(y, 452)) for x, y in refl], 0, 3.0, 1.15, 0.8, dash=(4, 16),
                         keep=lambda x, y: 0.65 if X > 0 else 0.4))
    o.append(p.ripples(60, 540, C(0, 0, ZFAR)[1] + 2, 452, 170, hy=C(0, 0, ZFAR)[1], lmin=4, lmax=24, wmin=1.0, wmax=1.8,
                       keep=lambda x, y: 1.0 if abs(x - 300) < (y - 236) * 1.85 * 0.98 else 0))
    # houseboat moored on the left
    hb = [C(-4.6, 0.2, 30), C(-4.6, 1.3, 30), C(-4.6, 1.3, 44), C(-4.6, 0.2, 44)]
    cab = [C(-4.4, 1.3, 32), C(-4.4, 3.1, 32), C(-4.4, 3.1, 42), C(-4.4, 1.3, 42)]
    o.append(p.shape(hb, 1.6, fill=INK))
    o.append(p.shape(cab, 1.6))
    o.append(p.hatch(cab, 90, 3.0, 1.0, 0.5))
    for z in (33.5, 36.5, 39.5):
        q = [C(-4.4, 1.8, z), C(-4.4, 2.7, z), C(-4.4, 2.7, z + 1.6), C(-4.4, 1.8, z + 1.6)]
        o.append(f'<polygon points="{P(q)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.1"/>')
    for z in (33, 36, 39, 42):
        c = C(-4.4, 3.4, z)
        o.append(p.foliage(c[0], c[1], 4.5, 3.2, w=1.1, shade=0.4, bump=2, inner=0.2))
    # little open boats moored along both quays, bows pointing away
    def sloep(X, z0, L, hw=1.0, tarp=False):
        gun, wl = [], []
        for i in range(13):
            s = i / 12
            k = (1 - s ** 2.4) ** 0.6
            gun.append((X - hw * k, 0.75 + 0.15 * s, z0 + L * s))
            wl.append((X - hw * 0.85 * k, 0.0, z0 + L * s * 0.97))
        gun += [(X + hw * (1 - (i / 12) ** 2.4) ** 0.6, 0.75 + 0.15 * i / 12, z0 + L * i / 12) for i in range(12, -1, -1)]
        wl += [(X + hw * 0.85 * (1 - (i / 12) ** 2.4) ** 0.6, 0.0, z0 + L * i / 12 * 0.97) for i in range(12, -1, -1)]
        G = [C(*q) for q in gun]
        W = [C(*q) for q in wl]
        out = [p.solid(W + G[::-1]), p.solid(G, INK)]
        out.append(p.line(G, max(1.2, 16 / z0), 0.2, closed=True))
        inner = [C(x * 0.0 + X + (x - X) * 0.8, y, z0 + (z - z0) * 0.92 + 0.2) for x, y, z in gun]
        out.append(p.shape(inner, max(1.0, 10 / z0)))
        out.append(p.hatch(inner, 75, 2.6, 1.0, 0.7))
        if tarp:
            out.append(p.shape(inner, max(1.0, 10 / z0), fill=PAPER))
            out.append(p.hatch(inner, 0, 3.2, 1.0, 0.6))
        for s in (0.25, 0.5):
            a_, b_ = C(X - hw * 0.8, 0.8, z0 + L * s), C(X + hw * 0.8, 0.8, z0 + L * s)
            out.append(p.seg(a_[0], a_[1], b_[0], b_[1], max(1.2, 14 / z0), 0.1))
        return "".join(out)
    for X, z, L, t in ((-4.6, 9, 5.5, True), (-4.6, 16.5, 6, False), (4.6, 8, 5.5, False), (4.6, 15, 6, True), (4.6, 23, 5, False),
                       (-4.6, 52, 5, True), (4.6, 34, 5, True), (4.6, 46, 5, False)):
        o.append(sloep(X, z, L, tarp=t))
    # the shadow of our bridge on the water just below the parapet
    o.append(p.hatch([(0, 432), (600, 432), (600, 454), (0, 454)], 0, 2.4, 1.1, 0.85, dash=(10, 40)))
    # an open sloop with three on board, motoring toward us
    bz = 20
    sl = [C(-1.5, 0.1, bz), C(-1.9, 0.6, bz + 0.5), C(-1.4, 0.7, bz + 6), C(0, 0.8, bz + 7.4), C(1.4, 0.7, bz + 6), C(1.9, 0.6, bz + 0.5), C(1.5, 0.1, bz)]
    o.append(p.reflect(C(-1.9, 0, bz)[0], C(1.9, 0, bz)[0], C(0, 0, bz)[1] + 2, 14, density=1, sp=2.6, w=1.3))
    o.append(p.shape(sl, 1.7))
    o.append(p.hatch(sl, 0, 2.4, 1.0, 0.8, keep=lambda x, y: 1 if y > C(0, 0.4, bz)[1] else 0.0))
    for X, z in ((-0.7, bz + 1.4), (0.6, bz + 2.6), (0, bz + 4.4)):
        q = C(X, 0.6, z)
        o.append(p.person(q[0], q[1], 270 * 1.0 / z, 1))
    o.append(f'<path d="M{C(-1.6, 0, bz)[0]:.1f} {C(-1.6, 0, bz)[1]:.1f}q-10 6 -26 10M{C(1.6, 0, bz)[0]:.1f} {C(1.6, 0, bz)[1]:.1f}q10 6 26 10" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    # gulls
    o.append(p.birds([(250, 90), (268, 82, 0.7), (360, 104, 0.8)], 7))
    # --- the bridge parapet in the foreground: brick, stone coping, a carved plaque
    py0 = 452
    o.append(p.shape([(-6, py0 + 12), (606, py0 + 12), (606, 606), (-6, 606)], 2.2))
    y = py0 + 20
    row = 0
    br = []
    while y < 600:
        br.append(f"M0 {y:.1f}H600")
        off = 0 if row % 2 else 13
        for x in range(-int(off), 600, 26):
            br.append(f"M{x:.1f} {y - 8:.1f}v8")
        y += 8
        row += 1
    o.append(f'<path d="{"".join(br)}" stroke="{INK}" stroke-width="1" opacity="0.42" fill="none"/>')
    o.append(p.hatch([(0, py0 + 12), (600, py0 + 12), (600, py0 + 26), (0, py0 + 26)], 0, 2.6, 1.0, 0.8))
    o.append(p.shape([(-6, py0), (606, py0), (606, py0 + 12), (-6, py0 + 12)], 2.4))
    o.append(p.line([(-6, py0 + 4), (606, py0 + 4)], 1.0, 0.3))
    o.append(cartouche(p, 142, 474, 458, 544, 9, 2.4))
    sz = name_size(name, 290, 50)
    o.append(title_text(300, 512, name, sz))
    o.append(coord_line(p, 300, 533, coords, 15.5, 2.0, 16, 9))
    # bikes chained to the parapet, and a heron on the coping
    o.append(p.bike(72, 540, 2.0, w=2.0) + p.bike(102, 542, 2.0, w=2.0, flip=True))
    o.append(p.bike(476, 541, 2.0, w=2.0))
    hx, hy = 506, py0
    o.append(p.line([(hx - 2, hy), (hx - 1, hy - 18)], 1.6) + p.line([(hx + 4, hy), (hx + 3, hy - 18)], 1.6))
    o.append(p.shape(smooth([(hx - 10, hy - 18), (hx + 2, hy - 30), (hx + 16, hy - 24), (hx + 8, hy - 16), (hx - 10, hy - 18)], 4), 1.6))
    o.append(p.hatch(smooth([(hx - 10, hy - 18), (hx + 2, hy - 30), (hx + 16, hy - 24), (hx + 8, hy - 16)], 4), 30, 2.6, 1.0, 0.8))
    o.append(p.line(smooth([(hx + 12, hy - 26), (hx + 9, hy - 36), (hx + 14, hy - 44), (hx + 18, hy - 46)], 4), 2.2))
    o.append(f'<circle cx="{hx + 18}" cy="{hy - 46}" r="2.6" fill="{PAPER}" stroke="{INK}" stroke-width="1.4"/>'
             f'<path d="M{hx + 20} {hy - 46}l11 2" stroke="{INK}" stroke-width="1.8"/><path d="M{hx + 16} {hy - 47}l-7 1" stroke="{INK}" stroke-width="1.2"/>')
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- build
def build(only=None):
    for slug, (name, coords, fn) in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COLL, slug, fn(name, coords))


if __name__ == "__main__":
    build(sys.argv[1:] or None)
