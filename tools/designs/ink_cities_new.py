"""Ink Cities, new cities: eighteen pen-and-ink illustrations drawn the way an architectural sketcher works:
a believable viewpoint, line-weight hierarchy (bold contours, finer detail, hairline-free texture),
cross-hatching and stippling for tone, scribbled foliage, ink ripples and broken reflections on water, and
small stories in the corners. Black ink on cream paper; a few pieces carry one faded accent wash.

Run from tools/designs:  python3 ink_cities_new.py [slug ...]
"""
import math
import random
import sys

from common import DMS, MONO, CINZEL, esc, fit_size, measure, save, star_points

INK = "#1C1916"
PAPER = "#F4EEE2"
COLL = "city-sketches"


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

    def lobe(self, cx, cy, rx, ry, light=(-1, -1), w=1.5, dense=1.0, shade=1.0):
        """One clump of foliage: paper fill, scalloped outline, little cupped leaf ticks that thicken toward the
        side away from the light into hatched shade, and a heavier contour on that side."""
        rnd = self.rnd
        n = max(9, int((rx + ry) / 3.4))
        ph = rnd.uniform(0, 6.28)
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n + ph
            k = 1 + 0.1 * rnd.uniform(-1, 1)
            pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
        d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
        outline = []
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ox, oy = mx - cx, my - cy
            L = math.hypot(ox, oy) or 1
            ch = math.hypot(b[0] - a[0], b[1] - a[1]) * 0.34 * rnd.uniform(0.6, 1.35)
            d += f" Q {mx + ox / L * ch:.1f} {my + oy / L * ch:.1f} {b[0]:.1f} {b[1]:.1f}"
            outline += [a, (mx + ox / L * ch * 0.5, my + oy / L * ch * 0.5)]
        lx, ly = light
        ll = math.hypot(lx, ly) or 1
        lx, ly = lx / ll, ly / ll
        lr = max(1.8, min(4.0, rx / 8))
        ticks, darks = [], []
        for _ in range(int(rx * ry * 6.2 / (lr * lr) * dense)):
            a = rnd.uniform(0, 2 * math.pi)
            rr = math.sqrt(rnd.random())
            ux, uy = rr * math.cos(a), rr * math.sin(a)
            t = max(0.0, min(1.0, (-(ux * lx + uy * ly) + 0.35) / 1.25)) * shade
            if rnd.random() > t ** 1.4:
                continue
            x, y = cx + ux * rx * 0.95, cy + uy * ry * 0.95
            r = lr * rnd.uniform(0.7, 1.25)
            tl = rnd.uniform(-0.4, 0.4) * r
            ticks.append(f"M{x - r:.1f} {y - tl:.1f}Q{x:.1f} {y + r * 1.25:.1f} {x + r:.1f} {y + tl:.1f}")
            if t > 0.72 and rnd.random() < 0.55:
                darks.append(f"M{x - r * 0.8:.1f} {y + r * 0.2:.1f}Q{x:.1f} {y + r * 1.25:.1f} {x + r * 0.8:.1f} {y + r * 0.2 + tl:.1f}"
                             f"Q{x:.1f} {y + r * 0.7:.1f} {x - r * 0.8:.1f} {y + r * 0.2:.1f}Z")
        cid = self.uid("lb")
        self.defs.append(f'<clipPath id="{cid}"><path d="{d} Z"/></clipPath>')
        inner = f'<path d="{"".join(ticks)}" fill="none" stroke="{INK}" stroke-width="0.95" stroke-linecap="round" opacity="0.9"/>'
        if darks:
            inner += f'<path d="{"".join(darks)}" fill="{INK}" opacity="0.85"/>'
        inner += self.hatch(outline, 100 if lx < 0 else 80, max(1.9, lr * 0.8), 1.0, 0.85,
                            keep=lambda x, y: max(0.0, ((x - cx) / rx * -lx + (y - cy) / ry * -ly) - 0.2) * 1.6)
        out = [f'<path d="{d} Z" fill="{PAPER}"/>', f'<g clip-path="url(#{cid})">{inner}</g>',
               f'<path d="{d} Z" fill="none" stroke="{INK}" stroke-width="{w * 0.75:.2f}" stroke-linejoin="round"/>']
        # heavier contour on the shadow side
        cid2 = self.uid("lc")
        far = 4 * max(rx, ry)
        half = [(cx - ly * far, cy + lx * far), (cx - ly * far - lx * far, cy + lx * far - ly * far),
                (cx + ly * far - lx * far, cy - lx * far - ly * far), (cx + ly * far, cy - lx * far)]
        self.defs.append(f'<clipPath id="{cid2}"><polygon points="{P(half)}"/></clipPath>')
        out.append(f'<path d="{d} Z" fill="none" stroke="{INK}" stroke-width="{w * 1.4:.2f}" clip-path="url(#{cid2})"/>')
        return "".join(out)

    def crown(self, cx, cy, rx, ry, lobes=6, light=(-1, -1), w=1.5, dense=1.0, under=True):
        """A broadleaf tree crown built from overlapping lobes, with a dark underside mass behind them."""
        rnd = self.rnd
        out = []
        if under:
            out.append(self.solid([(cx + rx * 0.92 * math.cos(t), cy + ry * 0.3 + ry * 0.62 * math.sin(t)) for t in [2 * math.pi * k / 24 for k in range(24)]], INK, 0.85))
        spots = [(0, -0.35, 0.55, 0.45)]
        for i in range(lobes - 1):
            a = math.pi * (0.95 + 1.1 * i / max(1, lobes - 2))
            spots.append((math.cos(a) * 0.5 * rnd.uniform(0.85, 1.1), -math.sin(a) * 0.35 + 0.05 + 0.15 * (i % 2),
                          rnd.uniform(0.42, 0.55), rnd.uniform(0.36, 0.46)))
        spots.sort(key=lambda s: s[1])
        for ox, oy, sx, sy in spots:
            out.append(self.lobe(cx + ox * rx, cy + oy * ry, sx * rx, sy * ry, light, w, dense))
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
        """Ink silhouette of a pedestrian standing on (x, y), h tall; larger figures get the fuller walker."""
        if h >= 32:
            return self.walker(x, y, h, "woman" if dress else "man", flip, 0.5 if pose % 2 == 0 else 0.1, bag)
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

    def walker(self, x, y, h, kind="man", flip=False, stride=0.5, bag=False, hat=False, rim=True):
        """A larger figure in silhouette, seen from behind or in three-quarter: rounded shoulders, coat or dress,
        legs in mid-stride with feet, swinging arms, and a paper rim-light down one side."""
        k = h / 100
        sx = -1 if flip else 1
        X = lambda u: x + u * k * sx
        Y = lambda v: y - v * k
        st = stride * 7
        out = []
        legw = 7.5 if kind != "child" else 8
        # legs and feet
        for side, sw in ((-1, -st), (1, st)):
            hip = (X(4 * side), Y(40))
            knee = (X(4.5 * side + sw * 0.5), Y(20))
            foot = (X(5 * side + sw), Y(3))
            out.append(f'<path d="M{hip[0]:.1f} {hip[1]:.1f}Q{knee[0]:.1f} {knee[1]:.1f} {foot[0]:.1f} {foot[1]:.1f}" stroke="{INK}" stroke-width="{legw * k:.1f}" stroke-linecap="round" fill="none"/>')
            out.append(f'<ellipse cx="{foot[0] + 2 * k * sx:.1f}" cy="{Y(1.6):.1f}" rx="{5 * k:.1f}" ry="{2.4 * k:.1f}" fill="{INK}"/>')
        # torso: coat, dress or jacket
        if kind == "woman":
            body = [(-9, 80), (-11, 76), (-11, 62), (-9, 52), (-16, 30), (16, 30), (9, 52), (11, 62), (11, 76), (9, 80)]
        elif kind == "child":
            body = [(-11, 74), (-12, 66), (-12, 46), (-10, 38), (10, 38), (12, 46), (12, 66), (11, 74)]
        else:
            body = [(-10, 82), (-14, 78), (-14, 62), (-13, 44), (-12, 34), (12, 34), (13, 44), (14, 62), (14, 78), (10, 82)]
        pts = [(X(u), Y(v)) for u, v in body]
        out.append(f'<path d="M{pts[0][0]:.1f} {pts[0][1]:.1f}' + "".join(
            f"Q{pts[i][0]:.1f} {pts[i][1]:.1f} {(pts[i][0] + pts[(i + 1) % len(pts)][0]) / 2:.1f} {(pts[i][1] + pts[(i + 1) % len(pts)][1]) / 2:.1f}"
            for i in range(1, len(pts))) + f'Z" fill="{INK}"/>')
        # arms swinging
        top = 76 if kind != "child" else 70
        for side in (-1, 1):
            sw = -side * stride * 5
            sh = (X(12.5 * side), Y(top))
            el = (X(14 * side + sw * 0.5), Y(top - 18))
            hd = (X(14.5 * side + sw), Y(top - 34))
            out.append(f'<path d="M{sh[0]:.1f} {sh[1]:.1f}Q{el[0]:.1f} {el[1]:.1f} {hd[0]:.1f} {hd[1]:.1f}" stroke="{INK}" stroke-width="{5.5 * k:.1f}" stroke-linecap="round" fill="none"/>')
        # head, neck, hair or hat
        hy = 90 if kind != "child" else 82
        out.append(f'<rect x="{X(-3) if not flip else X(3):.1f}" y="{Y(hy - 4):.1f}" width="{6 * k:.1f}" height="{6 * k:.1f}" fill="{INK}"/>')
        out.append(f'<ellipse cx="{X(0):.1f}" cy="{Y(hy):.1f}" rx="{7 * k:.1f}" ry="{8 * k:.1f}" fill="{INK}"/>')
        if kind == "woman":
            out.append(f'<circle cx="{X(-2):.1f}" cy="{Y(hy + 7):.1f}" r="{4 * k:.1f}" fill="{INK}"/>')
        if hat:
            out.append(f'<path d="M{X(-11):.1f} {Y(hy + 4):.1f}H{X(11):.1f}M{X(-6):.1f} {Y(hy + 4):.1f}V{Y(hy + 11):.1f}H{X(6):.1f}V{Y(hy + 4):.1f}" stroke="{INK}" stroke-width="{2.4 * k:.1f}" fill="{INK}"/>')
        if bag:
            out.append(f'<path d="M{X(-12):.1f} {Y(76):.1f}L{X(10):.1f} {Y(48):.1f}" stroke="{INK}" stroke-width="{1.4 * k:.1f}"/>'
                       f'<rect x="{min(X(8), X(18)):.1f}" y="{Y(52):.1f}" width="{10 * k:.1f}" height="{12 * k:.1f}" rx="{1.5 * k:.1f}" fill="{INK}"/>')
        if rim and h > 30:
            rp = [(X(-13.5), Y(76)), (X(-13.6), Y(62)), (X(-12.6), Y(46))] if kind != "woman" else [(X(-10.5), Y(74)), (X(-10.4), Y(62)), (X(-12), Y(44)), (X(-14.5), Y(32))]
            out.append(f'<path d="M{rp[0][0]:.1f} {rp[0][1]:.1f}' + "".join(f"L{a:.1f} {b:.1f}" for a, b in rp[1:]) + f'" stroke="{PAPER}" stroke-width="{max(0.9, 1.4 * k):.1f}" fill="none" opacity="0.8"/>')
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

    def laundry(self, x0, y0, x1, y1, sag=10, items=5, w=1.2, scale=None):
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
            s = max(0.7, min(1.4, s)) if scale is None else scale * rnd.uniform(0.85, 1.15)
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
    o.append(limb([(30, 330), (80, 282), (128, 258), (180, 226), (222, 196), (248, 160), (254, 128), (246, 100)], 32, 5))
    o.append(limb([(50, 400), (84, 330), (118, 300), (132, 262), (156, 238)], 20, 5))
    o.append(limb([(6, 270), (52, 214), (100, 190), (132, 160), (178, 146)], 24, 5))
    o.append(limb([(570, 330), (520, 286), (474, 260), (424, 230), (384, 200), (358, 164), (350, 130), (356, 100)], 30, 5))
    o.append(limb([(552, 400), (516, 330), (484, 302), (468, 266), (446, 244)], 20, 5))
    o.append(limb([(594, 272), (548, 214), (500, 192), (470, 162), (424, 148)], 24, 5))
    for ctrl in (([(200, 214), (210, 232), (226, 246)]), ([(118, 296), (98, 312), (90, 330)]), ([(412, 226), (398, 244), (386, 252)]),
                 ([(484, 300), (504, 318), (510, 334)]), ([(236, 178), (216, 160), (200, 158)]), ([(366, 178), (386, 160), (402, 158)])):
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
    def self_box(c, span):
        r = span * 0.6
        return (p.shape([(c[0] - r, c[1]), (c[0] + r, c[1]), (c[0] + r * 0.9, c[1] + r * 0.35), (c[0] - r * 0.9, c[1] + r * 0.35)], 1.2)
                + p.foliage(c[0], c[1] - r * 0.25, r * 1.05, r * 0.4, w=1.1, shade=0.5, bump=2.5, inner=0.6))

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
            else:
                yy = 1.2
                crs = []
                while yy < H:
                    za = z0 + rnd.uniform(0, w * 0.3)
                    zb = z0 + w - rnd.uniform(0, w * 0.3)
                    if rnd.random() < 0.8:
                        a_, b_ = C(X, yy, za), C(X, yy, zb)
                        crs.append(f"M{a_[0]:.1f} {a_[1]:.1f}L{b_[0]:.1f} {b_[1]:.1f}")
                    yy += 0.42
                out.append(f'<path d="{"".join(crs)}" stroke="{INK}" stroke-width="0.9" opacity="0.6"/>')
                out.append(p.hatch(poly, 100, 5.5 if z0 < 60 else 6.5, 1.0, 0.3))
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
                    bars = []
                    for tt in ((0.33, 0.66) if span > 12 else (0.5,)):
                        m1, m2 = lerp(qi[0], qi[1], tt), lerp(qi[3], qi[2], tt)
                        bars.append(f"M{m1[0]:.1f} {m1[1]:.1f}L{m2[0]:.1f} {m2[1]:.1f}")
                    n1, n2 = lerp(qi[0], qi[3], 0.5), lerp(qi[1], qi[2], 0.5)
                    bars.append(f"M{n1[0]:.1f} {n1[1]:.1f}L{n2[0]:.1f} {n2[1]:.1f}")
                    out.append(f'<path d="{"".join(bars)}" stroke="{PAPER}" stroke-width="{1.2 if span < 14 else 1.8}"/>')
                    # sill and a little lintel shadow
                    s1, s2 = C(X, ya - 0.1, z0 + ua - 0.1), C(X, ya - 0.1, z0 + ua + 1.4)
                    out.append(f'<path d="M{s1[0]:.1f} {s1[1]:.1f}L{s2[0]:.1f} {s2[1]:.1f}" stroke="{INK}" stroke-width="{max(1.2, span / 10):.1f}"/>')

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
    o.append(coord_line(p, 300, 533, coords, 16, 2.0, 16, 9))
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


# ---------------------------------------------------------------------------------- CHARLESTON
HORSE = [(0.1, 1.5), (0.6, 1.45), (1.2, 1.6), (1.5, 1.85), (1.75, 2.15), (1.77, 2.32), (1.83, 2.18), (2.0, 2.05),
         (2.3, 1.7), (2.32, 1.58), (2.18, 1.55), (1.8, 1.72), (1.55, 1.35), (1.62, 1.1), (1.64, 0.9), (1.6, 0.06),
         (1.68, 0), (1.47, 0), (1.47, 0.8), (1.2, 0.95), (0.6, 0.98), (0.47, 0.8), (0.44, 0.06), (0.52, 0), (0.3, 0),
         (0.27, 0.5), (0.18, 0.64), (0.05, 1.0), (0.02, 1.3)]


class YawCam(Cam):
    """Pinhole camera turned by `yaw` degrees toward +X: two-point views of a facade running along Z."""

    def __init__(self, f=300, cx=300, vpy=290, eye=1.6, yaw=0.0):
        super().__init__(f, cx, vpy, eye)
        self.c, self.s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))

    def __call__(self, X, Y, Z):
        xc, zc = X * self.c - Z * self.s, X * self.s + Z * self.c
        return (self.cx + self.f * xc / zc, self.vpy + self.f * (self.eye - Y) / zc)


def fan_palm(p, cx, cy, r, n=11, seed_ang=0.0, w=1.1, back=0.4, droop=1.0, halo=True):
    """Sabal palmetto crown drawn the way a sketcher does it: arching stalks, each ending in a spray of long,
    split leaf segments that fountain outward and droop; back fronds lighter, a few toned with hatching."""
    rnd = p.rnd
    backs, fronts = [], []
    for i in range(n):
        a = seed_ang + 2 * math.pi * i / n + rnd.uniform(-0.15, 0.15)
        dn = max(0.0, math.sin(a))
        up = max(0.0, -math.sin(a))
        L = r * rnd.uniform(0.85, 1.05) * (1 - 0.3 * dn)
        ex = cx + L * 0.5 * math.cos(a)
        ey = cy + L * 0.42 * math.sin(a) + L * 0.08 * dn
        ctrl = (cx + L * 0.25 * math.cos(a), cy + L * 0.25 * math.sin(a) - L * 0.12)
        is_back = rnd.random() < back + 0.4 * dn
        # direction of the leaf spray: continue the stalk, bent down by gravity
        da = math.atan2(ey - ctrl[1], ex - ctrl[0])
        k = rnd.randint(9, 12)
        spread = rnd.uniform(0.7, 1.1)
        strokes, tips = [], []
        for j in range(k):
            t = -spread / 2 + spread * j / (k - 1)
            la = da + t
            ll = L * 0.62 * (1 - 0.35 * abs(t) / spread) * rnd.uniform(0.85, 1.1)
            g = ll * (0.35 + 0.25 * up) * droop
            tx, ty = ex + ll * math.cos(la), ey + ll * math.sin(la) * 0.8 + g
            c1 = (ex + ll * 0.55 * math.cos(la), ey + ll * 0.55 * math.sin(la) * 0.8 - g * 0.1)
            tips.append((tx, ty))
            strokes.append(f"M{ex:.1f} {ey:.1f}Q{c1[0]:.1f} {c1[1]:.1f} {tx:.1f} {ty:.1f}")
            if rnd.random() < 0.6:   # split tip
                strokes.append(f"M{lerp(c1, (tx, ty), 0.7)[0]:.1f} {lerp(c1, (tx, ty), 0.7)[1]:.1f}l{rnd.uniform(-4, 4):.1f} {rnd.uniform(5, 10):.1f}")
        stalk = f'<path d="M{cx:.1f} {cy:.1f}Q{ctrl[0]:.1f} {ctrl[1]:.1f} {ex:.1f} {ey:.1f}" fill="none" stroke="{INK}" stroke-width="{w + 0.7:.1f}" stroke-linecap="round"/>'
        fan = [(ex, ey)] + tips
        if is_back:
            backs.append(stalk + p.hatch(fan, math.degrees(da) + 90, 2.8, 1.0, 0.75)
                         + f'<path d="{"".join(strokes)}" fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round" opacity="0.85"/>')
        else:
            fronts.append(stalk + p.solid(fan, PAPER)
                          + f'<path d="{"".join(strokes)}" fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round"/>')
    pre = ""
    if halo:   # leave the paper white around the crown so it reads against a busy background
        pre = p.solid([(cx + r * 0.85 * math.cos(t) * (1 + 0.08 * math.sin(5 * t)), cy + r * 0.62 * math.sin(t) + r * 0.15)
                       for t in [2 * math.pi * k / 40 for k in range(40)]], PAPER)
    # the boot of the crown: a dark knot of old leaf bases
    knot = p.solid([(cx - r * 0.05, cy + r * 0.2), (cx - r * 0.08, cy + r * 0.02), (cx, cy - r * 0.04), (cx + r * 0.08, cy + r * 0.02), (cx + r * 0.05, cy + r * 0.2)])
    return pre + "".join(backs) + knot + "".join(fronts)


def boot_trunk(p, pts, w0, w1, boots=True):
    """Palmetto trunk: tapering column with the criss-cross 'boots' of old leaf bases, shaded on the right."""
    c = smooth(pts, 6)
    L, R = offset(c, w0, w1)
    poly = L + R[::-1]
    out = [p.shape(poly, 2.0)]
    if boots:
        segs = []
        for i in range(1, len(c) - 1, 2):
            l, r = L[i], R[i]
            for f in (0.15, 0.5):
                a = lerp(l, r, f)
                b = lerp(L[min(len(L) - 1, i + 2)], R[min(len(R) - 1, i + 2)], f + 0.35)
                segs.append(f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}")
                a2 = lerp(l, r, 1 - f)
                b2 = lerp(L[min(len(L) - 1, i + 2)], R[min(len(R) - 1, i + 2)], 0.65 - f)
                segs.append(f"M{a2[0]:.1f} {a2[1]:.1f}L{b2[0]:.1f} {b2[1]:.1f}")
        out.append(f'<path d="{"".join(segs)}" stroke="{INK}" stroke-width="1.2" stroke-linecap="round" fill="none"/>')
    shade = [lerp(l, r, 0.62) for l, r in zip(L, R)] + R[::-1]
    out.append(p.hatch(shade, 100, 2.4, 1.0, 0.9))
    return "".join(out)


@design("charleston", "Charleston", "32.7765° N · 79.9311° W")
def charleston(name, coords):
    """Rainbow Row seen across East Bay Street: Georgian rowhouses stepping away along the street, louvred shutters,
    an iron balcony, carriage lanterns, a mule-drawn carriage tour, and a palmetto in the foreground."""
    p = Pen("charleston", 41)
    rnd = p.rnd
    C = YawCam(f=300, cx=318, vpy=440, eye=1.7, yaw=40)
    CORAL = "#E59A84"
    o = [p.paper(7)]
    X = 10.0                 # facade plane
    CURB = 7.6
    # --- sky: a soft summer haze in long pen strokes, loose clouds, gulls
    o.append(p.hatch([(0, 300), (600, 300), (600, 440), (0, 440)], -3, 6.0, 1.0, 0.45, dash=(10, 50),
                     keep=lambda x, y: max(0, (y - 320) / 160)))
    o.append(p.clouds(110, 250, 0.7) + p.clouds(410, 112, 0.5))
    o.append(p.birds([(190, 230), (206, 222, 0.7), (160, 252, 0.6)], 7))
    # --- the street in front of the row, and the sidewalk
    o.append(p.stipple([(0, 420), (600, 420), (600, 600), (0, 600)], 260, r=(0.5, 1.0),
                       keep=lambda x, y: 0.12 + 0.7 * (y - 420) / 180))
    walk = [C(CURB, 0.15, -3), C(CURB, 0.15, 300), C(X, 0.15, 300), C(X, 0.15, -3)]
    o.append(p.shape(walk, 1.4))
    zz = -2.0
    while zz < 120:
        a, b = C(CURB, 0.15, zz), C(X, 0.15, zz)
        o.append(p.seg(a[0], a[1], b[0], b[1], 1.0, 0.2, op=0.75))
        zz += 1.5 + zz * 0.04
    a, b = C(CURB, 0, -3), C(CURB, 0, 300)
    o.append(p.seg(a[0], a[1], b[0], b[1], 2.2, 0.3))
    o.append(p.hatch([C(CURB, 0, -3), C(CURB, 0, 300), C(CURB, 0.15, 300), C(CURB, 0.15, -3)], 0, 1.8, 1.0, 0.9))
    for z in (-1, 4, 10, 17, 27, 40):                      # dashed centre line
        a, b = C(3.6, 0, z), C(3.6, 0, z + 2.6 + z * 0.05)
        o.append(p.seg(a[0], a[1], b[0], b[1], max(1.1, 24 / max(6, z + 6)), 0.1))
    # --- the rowhouses
    houses = []
    z = -6.0
    kinds = ["hip", "flat", "curve", "balus", "hip", "flat", "curve", "hip", "balus", "flat", "curve", "hip", "flat", "flat", "hip", "flat"]
    tones = [1, 0, 2, 0, 1, 0, 2, 1, 0, 1, 2, 0, 1, 0, 1, 2]
    for i in range(16):
        w = rnd.uniform(6.4, 8.2)
        H = rnd.uniform(10.6, 12.6)
        houses.append((z, w, H, kinds[i], tones[i], i))
        z += w
    for z0, w, H, kind, tone, idx in reversed(houses):
        F = lambda u, v, z0=z0: C(X, v, z0 + u)
        dist = X * C.s + (z0 + w / 2) * C.c
        sc = 300 / dist                                    # px per metre at this house
        lw = 2.2 if sc > 18 else (1.7 if sc > 9 else 1.3)
        body = [F(0, 0.15), F(0, H), F(w, H), F(w, 0.15)]
        if kind == "hip":
            top = [F(0, H), F(0.7, H + 2.6), F(w - 0.7, H + 2.6), F(w, H)]
        elif kind == "curve":
            arc = [F(w / 2 + (w / 2 - 0.9) * math.cos(t), H + 1.3 + 1.3 * math.sin(t) ** 0.7) for t in [math.pi * k / 14 for k in range(15)]]
            top = [F(w, H), F(w, H + 0.9), F(w - 0.5, H + 1.0)] + arc + [F(0.5, H + 1.0), F(0, H + 0.9), F(0, H)]
        elif kind == "balus":
            top = [F(0, H), F(0, H + 1.1), F(w, H + 1.1), F(w, H)]
        else:
            top = [F(0, H), F(0, H + 0.7), F(w, H + 0.7), F(w, H)]
        o.append(p.shape(body, lw))
        o.append(p.shape(top, lw))
        if kind == "hip":
            o.append(p.hatch(top, 15, 2.6 if sc > 9 else 3.2, 1.0, 0.85))
            d = [F(w / 2 - 0.8, H + 0.5), F(w / 2 - 0.8, H + 2.0), F(w / 2, H + 2.8), F(w / 2 + 0.8, H + 2.0), F(w / 2 + 0.8, H + 0.5)]
            o.append(p.shape(d, lw * 0.8))
            o.append(p.solid([F(w / 2 - 0.4, H + 0.8), F(w / 2 - 0.4, H + 1.8), F(w / 2 + 0.4, H + 1.8), F(w / 2 + 0.4, H + 0.8)]))
            ch = [F(w * 0.15, H + 1.6), F(w * 0.15, H + 3.6), F(w * 0.15 + 0.8, H + 3.6), F(w * 0.15 + 0.8, H + 1.6)]
            o.append(p.shape(ch, lw * 0.8) + p.hatch(ch, 0, 2.4, 1.0, 0.7))
        elif kind == "balus":
            bal = []
            for k in range(1, int(w / 0.4)):
                a, b = F(k * 0.4, H + 0.15), F(k * 0.4, H + 0.8)
                bal.append(f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}")
            o.append(f'<path d="{"".join(bal)}" stroke="{INK}" stroke-width="{1.2 if sc > 9 else 0.9}"/>')
            a, b = F(0, H + 0.9), F(w, H + 0.9)
            o.append(p.seg(a[0], a[1], b[0], b[1], lw, 0.2))
        elif kind == "curve":
            c = F(w / 2, H + 1.4)
            o.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{max(1.5, sc * 0.35):.1f}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
        # value of the pastel colour as hatching; the coral houses carry the faded accent wash
        if tone:
            o.append(p.hatch(body, 84, {1: 6.0, 2: 4.0}[tone] * (1 if sc > 9 else 0.8), 1.0, 0.5 if tone == 1 else 0.6))
        if idx in (2, 6, 10):
            o.append(p.wash(body + top[1:-1][::-1] if kind != "hip" else body, CORAL, 0.32))
        # cornice + its shadow; string course over the shop floor
        a, b = F(0, H), F(w, H)
        o.append(p.seg(a[0], a[1], b[0], b[1], lw + 1.0, 0.2))
        o.append(p.hatch([F(0, H), F(w, H), F(w, H - 0.5), F(0, H - 0.5)], 12, 2.2, 1.0, 0.85))
        a, b = F(0, 3.9), F(w, 3.9)
        o.append(p.seg(a[0], a[1], b[0], b[1], lw * 0.8, 0.2))
        # quoins on the corners of near houses
        if sc > 12:
            for v in [0.6 + 0.7 * k for k in range(int((H - 1) / 0.7))]:
                q = [F(0, v), F(0, v + 0.45), F(0.5 if int(v / 0.7) % 2 else 0.8, v + 0.45), F(0.5 if int(v / 0.7) % 2 else 0.8, v)]
                o.append(p.line(q, 1.0, 0.1))
        # windows and louvred shutters
        cols = 3 if w > 7.0 else 2
        for ya, hh in ((4.7, 2.2), (8.0, 2.0)):
            for c in range(cols):
                ua = (w / cols) * (c + 0.5) - 0.55
                q = [F(ua, ya), F(ua, ya + hh), F(ua + 1.1, ya + hh), F(ua + 1.1, ya)]
                span = abs(q[2][0] - q[0][0])
                if span < 4:
                    o.append(p.solid(q))
                    continue
                o.append(p.solid(q))
                m1, m2 = lerp(q[0], q[3], 0.5), lerp(q[1], q[2], 0.5)
                gl = [f"M{m1[0]:.1f} {m1[1]:.1f}L{m2[0]:.1f} {m2[1]:.1f}"]
                for t in ((0.5,) if span < 9 else (0.33, 0.5, 0.67)):
                    a, b = lerp(q[0], q[1], t), lerp(q[3], q[2], t)
                    gl.append(f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}")
                o.append(f'<path d="{"".join(gl)}" stroke="{PAPER}" stroke-width="{max(0.9, min(1.5, span / 12)):.1f}"/>')
                a, b = F(ua - 0.15, ya - 0.05), F(ua + 1.25, ya - 0.05)
                o.append(p.seg(a[0], a[1], b[0], b[1], max(1.2, min(2.4, span / 7)), 0.1))
                a, b = F(ua - 0.1, ya + hh + 0.12), F(ua + 1.2, ya + hh + 0.12)
                o.append(p.seg(a[0], a[1], b[0], b[1], max(1.2, min(2.4, span / 7)), 0.1))
                for su in (ua - 0.58, ua + 1.12):
                    sq = [F(su, ya), F(su, ya + hh), F(su + 0.46, ya + hh), F(su + 0.46, ya)]
                    o.append(p.shape(sq, max(1.0, min(1.5, span / 12))))
                    nl = int(hh / 0.16) if span > 10 else int(hh / 0.3)
                    lv = []
                    for k in range(1, nl):
                        a, b = F(su + 0.05, ya + k * hh / nl), F(su + 0.41, ya + k * hh / nl - 0.04)
                        lv.append(f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}")
                    o.append(f'<path d="{"".join(lv)}" stroke="{INK}" stroke-width="1"/>')
        # ground floor: fanlit door, a shop window under a striped awning
        du = w * 0.1
        door = [F(du, 0.4), F(du, 2.7), F(du + 1.1, 2.7), F(du + 1.1, 0.4)]
        o.append(p.solid(door))
        fan = [F(du + 0.55 + 0.55 * math.cos(math.pi * k / 8), 2.75 + 0.5 * math.sin(math.pi * k / 8)) for k in range(9)]
        o.append(p.shape(fan, max(1.0, lw * 0.7)))
        if sc > 12:
            a = F(du + 0.55, 2.75)
            o.append("".join(p.seg(a[0], a[1], fan[k][0], fan[k][1], 1.0, 0.0) for k in (2, 4, 6)))
            st = [F(du - 0.2, 0.15), F(du - 0.2, 0.4), F(du + 1.3, 0.4), F(du + 1.3, 0.15)]
            o.append(p.shape(st, 1.2))
        sw = [F(w * 0.42, 0.9), F(w * 0.42, 3.0), F(w * 0.88, 3.0), F(w * 0.88, 0.9)]
        o.append(p.solid(sw))
        if sc > 8:
            gl = []
            for t in (0.25, 0.5, 0.75):
                a, b = lerp(sw[0], sw[3], t), lerp(sw[1], sw[2], t)
                gl.append(f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}")
            a, b = lerp(sw[0], sw[1], 0.72), lerp(sw[3], sw[2], 0.72)
            gl.append(f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}")
            o.append(f'<path d="{"".join(gl)}" stroke="{PAPER}" stroke-width="1.1"/>')
            aw = [F(w * 0.4, 3.4), F(w * 0.9, 3.4), C(X - 1.0, 2.8, z0 + w * 0.9), C(X - 1.0, 2.8, z0 + w * 0.4)]
            o.append(p.shape(aw, 1.4))
            stripes = []
            for k in range(1, 12, 2):
                t0, t1 = k / 12, (k + 1) / 12
                stripes.append(p.solid([lerp(aw[0], aw[1], t0), lerp(aw[0], aw[1], t1), lerp(aw[3], aw[2], t1), lerp(aw[3], aw[2], t0)]))
            o.append("".join(stripes))
            sc_e = [lerp(aw[3], aw[2], k / 12) for k in range(13)]
            o.append(p.line(sc_e, 1.3, 0.1))
        # carriage lantern on its bracket by the door
        if sc > 10:
            la = F(du + 1.45, 2.9)
            lb = C(X - 0.4, 2.9, z0 + du + 1.45)
            s = sc * 0.28
            o.append(p.seg(la[0], la[1], lb[0], lb[1], max(1.2, s * 0.2), 0.1))
            o.append(p.shape([(lb[0] - s * 0.45, lb[1]), (lb[0] - s * 0.6, lb[1] + s * 1.2), (lb[0] + s * 0.6, lb[1] + s * 1.2), (lb[0] + s * 0.45, lb[1])], 1.3))
            o.append(p.solid([(lb[0] - s * 0.75, lb[1]), (lb[0], lb[1] - s * 0.55), (lb[0] + s * 0.75, lb[1])]))
            o.append(p.solid([(lb[0] - s * 0.6, lb[1] + s * 1.2), (lb[0] + s * 0.6, lb[1] + s * 1.2), (lb[0], lb[1] + s * 1.6)]))
    # --- a wrought-iron balcony across the second floor of the second house, with potted ferns
    z0, w = houses[1][0], houses[1][1]
    A, B = z0 + 0.5, z0 + w - 0.5
    floor_ = [C(X, 4.45, A), C(X - 1.0, 4.45, A), C(X - 1.0, 4.45, B), C(X, 4.45, B)]
    o.append(p.shape(floor_, 1.5) + p.hatch(floor_, 0, 2.0, 1.0, 0.9))
    bal = []
    for k in range(0, 41):
        zq = A + (B - A) * k / 40
        a, b = C(X - 1.0, 4.5, zq), C(X - 1.0, 5.45, zq)
        bal.append(f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}")
    for zq in (A, B):
        a, b = C(X, 5.45, zq), C(X - 1.0, 5.45, zq)
        bal.append(f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}")
    o.append(f'<path d="{"".join(bal)}" stroke="{INK}" stroke-width="1.1"/>')
    o.append(p.line([C(X - 1.0, 5.45, A), C(X - 1.0, 5.45, B)], 2.0, 0.2))
    for k in range(5):                                       # scroll brackets under it
        zq = A + (B - A) * k / 4
        a, b, c = C(X, 3.9, zq), C(X, 4.4, zq), C(X - 0.9, 4.4, zq)
        o.append(p.line([a, lerp(b, c, 0.3), c], 1.3, 0.1))
    for zq in (A + 0.8, (A + B) / 2, B - 0.8):
        c = C(X - 0.6, 5.9, zq)
        o.append(p.foliage(c[0], c[1], 10, 7, w=1.2, shade=0.5, bump=3, inner=0.5))
    # --- the carriage tour on the street: mule, open wagon with a fringed canopy, passengers
    hx_, hz = 4.4, 9.5
    Hp = lambda u, v: C(hx_, v, hz - u)
    sc = 300 / (hx_ * C.s + hz * C.c)
    o.append(p.hatch([Hp(2.3, 0), Hp(-4.8, 0), Hp(-4.8, -0.6), Hp(2.3, -0.6)], 0, 1.8, 1.0, 0.8))
    o.append(p.shape([Hp(-0.6, 1.0), Hp(-4.6, 1.0), Hp(-4.6, 0.62), Hp(-0.6, 0.62)], 1.5))
    for u, v in ((-1.7, 1.0), (-2.7, 1.0), (-3.7, 1.0)):
        a = Hp(u, v)
        o.append(f'<circle cx="{a[0]:.1f}" cy="{a[1] - sc * 0.95:.1f}" r="{sc * 0.17:.1f}" fill="{INK}"/>'
                 f'<path d="M{a[0] - sc * 0.2:.1f} {a[1]:.1f}L{a[0] - sc * 0.16:.1f} {a[1] - sc * 0.72:.1f}L{a[0] + sc * 0.16:.1f} {a[1] - sc * 0.72:.1f}L{a[0] + sc * 0.2:.1f} {a[1]:.1f}Z" fill="{INK}"/>')
    for u in (-0.9, -2.2, -3.4, -4.5):
        a, b = Hp(u, 1.0), Hp(u, 2.4)
        o.append(p.seg(a[0], a[1], b[0], b[1], 1.3, 0.1))
    can = [Hp(-0.75, 2.62), Hp(-4.7, 2.62), Hp(-4.7, 2.38), Hp(-0.75, 2.38)]
    o.append(p.shape(can, 1.5) + p.hatch(can, 0, 1.6, 1.0, 0.8))
    fr = "".join(f"M{Hp(-0.8 - k * 0.13, 2.38)[0]:.1f} {Hp(-0.8 - k * 0.13, 2.38)[1]:.1f}v{sc * 0.16:.1f}" for k in range(30))
    o.append(f'<path d="{fr}" stroke="{INK}" stroke-width="1"/>')
    for u in (-1.4, -3.9):
        cp = [Hp(u + 0.6 * math.cos(t), 0.6 + 0.6 * math.sin(t)) for t in [2 * math.pi * k / 22 for k in range(22)]]
        hub = Hp(u, 0.6)
        o.append(p.line(cp, 1.7, 0.1, closed=True) + "".join(p.seg(hub[0], hub[1], q[0], q[1], 1.0, 0.0) for q in cp[::2]))
    o.append(p.solid([Hp(u, v) for u, v in HORSE]))
    o.append(p.line([Hp(0.02, 1.3), Hp(-0.22, 0.85), Hp(-0.16, 0.5)], 2.4, 0.1))
    o.append(p.line([Hp(1.55, 1.55), Hp(-0.6, 1.05)], 1.3, 0.1) + p.line([Hp(1.95, 1.8), Hp(1.2, 1.65), Hp(-0.8, 1.5)], 1.1, 0.1))
    o.append(p.line([Hp(1.45, 0.9), Hp(1.3, 0.05)], 2.2, 0.1) + p.line([Hp(0.4, 0.8), Hp(0.55, 0.05)], 2.2, 0.1))
    dv = Hp(-0.85, 1.05)
    o.append(p.person(dv[0], dv[1] + 2, sc * 1.25, 1))
    o.append(f'<path d="M{dv[0] - sc * 0.32:.1f} {dv[1] - sc * 1.12:.1f}h{sc * 0.64:.1f}" stroke="{INK}" stroke-width="2"/>')
    # --- people on the far sidewalk, a bike against a lamp post
    for X_, z_, flip, dress in ((8.7, 15.0, True, True), (9.0, 15.8, True, False), (8.4, 24, False, False), (8.7, 33, True, True)):
        a = C(X_, 0.15, z_)
        sc_ = 300 / (X_ * C.s + z_ * C.c)
        o.append(p.person(a[0], a[1], sc_ * 1.7, pose=int(z_) % 2, flip=flip, dress=dress, bag=dress))
    lp = C(7.9, 0.15, 9.5)
    sc_ = 300 / (7.9 * C.s + 9.5 * C.c)
    o.append(p.lamp(lp[0], lp[1], sc_ * 4.0, w=1.6))
    o.append(p.bike(lp[0] + 2, lp[1], sc_ * 0.075, w=1.6))
    # --- foreground: our own curb in the corner, an old gas lamp, the palmetto's shadow, pigeons, a manhole
    nc = [C(0.6, 0, 3.6), C(0.6, 0, 300)]
    o.append(p.shape([C(0.6, 0, 3.6), C(0.6, 0, 300), C(-3, 0, 300), C(-3, 0, 3.6)], 2.0))
    o.append(p.hatch([C(0.6, 0, 3.6), C(0.6, 0, 300), C(0.6, 0.15, 300), C(0.6, 0.15, 3.6)], 0, 2, 1.0, 0.9))
    zz = 3.6
    while zz < 60:
        a, b = C(0.6, 0.15, zz), C(-3, 0.15, zz)
        o.append(p.seg(a[0], a[1], b[0], b[1], 1.0, 0.2, op=0.7))
        zz += 1.2 + zz * 0.05
    gl = C(0.2, 0.15, 10.0)
    o.append(p.lamp(gl[0], gl[1], 300 / (0.2 * C.s + 10 * C.c) * 3.9, w=2.0, arms=2))
    o.append(p.hatch([C(5.2, 0, 4.2), C(6.2, 0, 6.0), C(3.0, 0, 9.0), C(1.8, 0, 7.2)], 30, 3.0, 1.0, 0.0) if False else "")
    sh = [(470, 600), (520, 600), (560, 548), (590, 520), (560, 515), (520, 540)]
    o.append(p.hatch(sh, 20, 3.0, 1.1, 0.7))
    mh = [C(4.0 + 0.45 * math.cos(t), 0, 6.5 + 0.45 * math.sin(t)) for t in [2 * math.pi * k / 20 for k in range(20)]]
    o.append(p.line(mh, 1.6, 0.1, closed=True) + p.hatch(mh, 0, 2.2, 1.0, 0.7))
    asp = []
    for _ in range(70):
        X_, z_ = rnd.uniform(1.0, 7.4), rnd.uniform(4.5, 40)
        a, b = C(X_, 0, z_), C(X_ + 0.3, 0, z_ + 0.08)
        asp.append(f"M{a[0]:.1f} {a[1]:.1f}L{a[0] + max(3, 90 / z_):.1f} {a[1]:.1f}")
    o.append(f'<path d="{"".join(asp)}" stroke="{INK}" stroke-width="1" opacity="0.55"/>')
    for X_, z_, f in ((2.2, 5.0, 1), (2.5, 5.4, -1), (1.8, 5.7, 1)):
        a = C(X_, 0, z_)
        k = 300 / (X_ * C.s + z_ * C.c) * 0.022
        o.append(f'<path d="M{a[0] - 6 * k * f:.1f} {a[1] - 4 * k:.1f}q{4 * k * f:.1f} {-6 * k:.1f} {11 * k * f:.1f} {-2 * k:.1f}l{3 * k * f:.1f} {-3 * k:.1f}l{2 * k * f:.1f} {2 * k:.1f}l{-2 * k * f:.1f} {2 * k:.1f}q{-1 * k * f:.1f} {5 * k:.1f} {-8 * k * f:.1f} {5 * k:.1f}Z" fill="{INK}"/>'
                 f'<path d="M{a[0]:.1f} {a[1] - 1 * k:.1f}v{1.5 * k:.1f}" stroke="{INK}" stroke-width="1.2"/>')
    # --- the palmetto on the right
    o.append(boot_trunk(p, [(500, 612), (506, 520), (514, 420), (522, 320), (526, 236)], 26, 18))
    o.append(fan_palm(p, 526, 228, 88, n=15, seed_ang=0.25, back=0.45))
    o.append(p.grass(420, 590, 604, 40, (6, 18), 1.4))
    # --- border, title ribbon in the sky
    o.append(p.border(26, 7, 2.6, 1.3))
    o.append(ribbon(p, 232, 104, 300, 60, name, name_size(name, 262, 48), tail=28, drop=12))
    o.append(coord_line(p, 232, 166, coords, 16, 1.8, 16, 9))
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- NEW ORLEANS
def lace_panel(p, x0, x1, y0, y1, w=1.3):
    """Cast-iron gallery railing: top and bottom rails, and a repeating lace motif of back-to-back C-scrolls
    around a rosette, with slim pickets between."""
    out = [p.line([(x0, y0), (x1, y0)], 2.4, 0.2), p.line([(x0, y0 + 4), (x1, y0 + 4)], 1.2, 0.2),
           p.line([(x0, y1), (x1, y1)], 2.4, 0.2), p.line([(x0, y1 - 4), (x1, y1 - 4)], 1.2, 0.2)]
    unit = 24
    n = max(1, int((x1 - x0) / unit))
    unit = (x1 - x0) / n
    h = y1 - y0 - 8
    cy = y0 + 4 + h / 2
    d = []
    for i in range(n):
        ux = x0 + i * unit
        mx = ux + unit / 2
        # pickets at the unit edges
        d.append(f"M{ux:.1f} {y0 + 4:.1f}V{y1 - 4:.1f}")
        # C-scrolls: an S-curve pair making a lyre, curling into small volutes
        r = unit * 0.22
        d.append(f"M{mx:.1f} {y0 + 5:.1f}C{mx - unit * 0.42:.1f} {y0 + 5 + h * 0.15:.1f} {mx - unit * 0.42:.1f} {cy - r:.1f} {mx - r * 0.4:.1f} {cy - r * 0.5:.1f}")
        d.append(f"M{mx:.1f} {y0 + 5:.1f}C{mx + unit * 0.42:.1f} {y0 + 5 + h * 0.15:.1f} {mx + unit * 0.42:.1f} {cy - r:.1f} {mx + r * 0.4:.1f} {cy - r * 0.5:.1f}")
        d.append(f"M{mx:.1f} {y1 - 5:.1f}C{mx - unit * 0.42:.1f} {y1 - 5 - h * 0.15:.1f} {mx - unit * 0.42:.1f} {cy + r:.1f} {mx - r * 0.4:.1f} {cy + r * 0.5:.1f}")
        d.append(f"M{mx:.1f} {y1 - 5:.1f}C{mx + unit * 0.42:.1f} {y1 - 5 - h * 0.15:.1f} {mx + unit * 0.42:.1f} {cy + r:.1f} {mx + r * 0.4:.1f} {cy + r * 0.5:.1f}")
        d.append(f"M{ux + 2:.1f} {y0 + 6:.1f}q{unit * 0.18:.1f} {h * 0.2:.1f} 0 {h * 0.34:.1f}M{ux + unit - 2:.1f} {y0 + 6:.1f}q{-unit * 0.18:.1f} {h * 0.2:.1f} 0 {h * 0.34:.1f}")
        d.append(f"M{ux + 2:.1f} {y1 - 6:.1f}q{unit * 0.18:.1f} {-h * 0.2:.1f} 0 {-h * 0.34:.1f}M{ux + unit - 2:.1f} {y1 - 6:.1f}q{-unit * 0.18:.1f} {-h * 0.2:.1f} 0 {-h * 0.34:.1f}")
        out.append(f'<circle cx="{mx:.1f}" cy="{cy:.1f}" r="{r * 0.7:.1f}" fill="{PAPER}" stroke="{INK}" stroke-width="{w}"/>'
                   f'<circle cx="{mx:.1f}" cy="{cy:.1f}" r="{max(1.2, r * 0.25):.1f}" fill="{INK}"/>')
    d.append(f"M{x1:.1f} {y0 + 4:.1f}V{y1 - 4:.1f}")
    out.insert(4, f'<path d="{"".join(d)}" fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round"/>')
    return "".join(out)


def lace_frieze(p, x0, x1, y0, h, w=1.2):
    """The lace valance under a gallery roof: a run of shallow arches hung with drops and scroll spandrels."""
    out = [p.line([(x0, y0), (x1, y0)], 2.0, 0.2)]
    n = max(1, int((x1 - x0) / 34))
    u = (x1 - x0) / n
    d = []
    for i in range(n):
        a = x0 + i * u
        b = a + u
        d.append(f"M{a:.1f} {y0 + h:.1f}Q{(a + b) / 2:.1f} {y0 + h * 0.15:.1f} {b:.1f} {y0 + h:.1f}")
        d.append(f"M{a + 3:.1f} {y0 + 2:.1f}q{u * 0.2:.1f} {h * 0.55:.1f} {-1:.1f} {h * 0.75:.1f}")
        d.append(f"M{b - 3:.1f} {y0 + 2:.1f}q{-u * 0.2:.1f} {h * 0.55:.1f} {1:.1f} {h * 0.75:.1f}")
        d.append(f"M{(a + b) / 2:.1f} {y0 + h * 0.58:.1f}v{h * 0.35:.1f}")
        out.append(f'<circle cx="{(a + b) / 2:.1f}" cy="{y0 + h * 0.98:.1f}" r="1.8" fill="{INK}"/>'
                   f'<circle cx="{(a + b) / 2:.1f}" cy="{y0 + h * 0.36:.1f}" r="2.6" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    out.append(f'<path d="{"".join(d)}" fill="none" stroke="{INK}" stroke-width="{w}" stroke-linecap="round"/>')
    return "".join(out)


def french_door(p, x, y, w, h, state="open", shutters=True):
    """Tall Creole French door under a transom; louvred shutters open or closed."""
    out = []
    tr = 16
    out.append(p.shape(rect(x - 3, y - 4, w + 6, h + 4), 1.6))
    if state == "closed":
        out.append(p.shape(rect(x, y + tr, w, h - tr), 1.4))
        lv = "".join(f"M{x + 2:.1f} {yy:.1f}h{w / 2 - 3:.1f}M{x + w / 2 + 1:.1f} {yy:.1f}h{w / 2 - 3:.1f}" for yy in [y + tr + 4 + k * 3.4 for k in range(int((h - tr - 6) / 3.4))])
        out.append(f'<path d="{lv}" stroke="{INK}" stroke-width="1.05"/>')
        out.append(p.seg(x + w / 2, y + tr, x + w / 2, y + h, 1.4, 0.1))
        out.append(p.line([(x + 1, y + tr + (h - tr) * 0.5), (x + w - 1, y + tr + (h - tr) * 0.5)], 1.6, 0.1))
    else:
        out.append(p.solid(rect(x, y + tr, w, h - tr)))
        gl = []
        for k in range(1, 5):
            gl.append(f"M{x + 2:.1f} {y + tr + k * (h - tr) / 5:.1f}h{w - 4:.1f}")
        gl.append(f"M{x + w / 2:.1f} {y + tr:.1f}V{y + h:.1f}")
        gl.append(f"M{x + w * 0.25:.1f} {y + tr:.1f}V{y + h:.1f}M{x + w * 0.75:.1f} {y + tr:.1f}V{y + h:.1f}")
        out.append(f'<path d="{"".join(gl)}" stroke="{PAPER}" stroke-width="1.2" opacity="0.85"/>')
        if shutters:
            sw = w * 0.5
            for sx in (x - sw - 3, x + w + 3):
                out.append(p.shape(rect(sx, y + tr, sw, h - tr), 1.4))
                lv = "".join(f"M{sx + 1.5:.1f} {yy:.1f}h{sw - 3:.1f}" for yy in [y + tr + 4 + k * 3.4 for k in range(int((h - tr - 6) / 3.4))])
                out.append(f'<path d="{lv}" stroke="{INK}" stroke-width="1.05"/>')
                out.append(p.line([(sx, y + tr + (h - tr) * 0.5), (sx + sw, y + tr + (h - tr) * 0.5)], 1.6, 0.1))
    # transom: a fanlight of radiating bars
    out.append(p.shape(rect(x, y, w, tr - 2), 1.4))
    fl = "".join(f"M{x + w / 2:.1f} {y + tr - 2:.1f}L{x + w / 2 + (w / 2) * math.cos(math.pi * k / 6):.1f} {y + tr - 2 - (tr - 2) * math.sin(math.pi * k / 6):.1f}" for k in range(1, 6))
    out.append(f'<path d="{fl}" stroke="{INK}" stroke-width="1"/>')
    return "".join(out)


def hanging_fern(p, x, y0, drop, r=20):
    """A Boston fern in a wire basket hung on chains from the gallery ceiling: arching fronds spilling down."""
    rnd = p.rnd
    by = y0 + drop
    out = [p.line([(x, y0), (x - r * 0.6, by)], 1.0, 0.1), p.line([(x, y0), (x + r * 0.6, by)], 1.0, 0.1)]
    fr = []
    for k in range(17):
        a = math.pi * (0.03 + 0.94 * k / 16) + rnd.uniform(-0.08, 0.08)
        L = r * rnd.uniform(1.3, 2.1)
        sx = x + r * 0.7 * math.cos(a)
        ex, ey = x + L * math.cos(a) * 1.15, by + L * 0.75 * abs(math.sin(a)) + L * 0.35
        cx_, cy_ = x + L * 0.8 * math.cos(a) * 1.15, by - r * 0.4
        fr.append(f"M{sx:.1f} {by:.1f}Q{cx_:.1f} {cy_:.1f} {ex:.1f} {ey:.1f}")
        # pinnae: short ticks along the frond
        for t in (0.35, 0.5, 0.65, 0.8):
            px_ = (1 - t) ** 2 * sx + 2 * (1 - t) * t * cx_ + t * t * ex
            py_ = (1 - t) ** 2 * by + 2 * (1 - t) * t * cy_ + t * t * ey
            fr.append(f"M{px_ - 3:.1f} {py_ - 2:.1f}l3 2l3 -2")
    out.append(f'<path d="{"".join(fr)}" fill="none" stroke="{INK}" stroke-width="1.15" stroke-linecap="round"/>')
    out.append(p.shape([(x - r * 0.75, by - 2), (x + r * 0.75, by - 2), (x + r * 0.5, by + r * 0.5), (x - r * 0.5, by + r * 0.5)], 1.6))
    out.append(p.hatch([(x - r * 0.75, by - 2), (x + r * 0.75, by - 2), (x + r * 0.5, by + r * 0.5), (x - r * 0.5, by + r * 0.5)], 45, 2.6, 1.0, 0.8)
               + p.hatch([(x - r * 0.75, by - 2), (x + r * 0.75, by - 2), (x + r * 0.5, by + r * 0.5), (x - r * 0.5, by + r * 0.5)], 135, 2.6, 1.0, 0.8))
    out.append(p.foliage(x, by - 4, r * 0.8, r * 0.38, w=1.2, shade=0.6, bump=3, inner=0.6))
    return "".join(out)


def musician(p, x, y, h, inst="trumpet", flip=False):
    """A street musician in silhouette: hat, jacket, and the instrument picked out in paper highlights."""
    k = h / 60
    s = -1 if flip else 1
    out = [p.person(x, y, h * 0.98, pose=1, flip=flip)]
    out.append(f'<path d="M{x - 5 * k:.1f} {y - h * 0.97:.1f}h{10 * k:.1f}M{x - 3 * k:.1f} {y - h * 0.97:.1f}v{-4 * k:.1f}h{6 * k:.1f}v{4 * k:.1f}" stroke="{INK}" stroke-width="{2 * k:.1f}" fill="{INK}"/>')
    hx, hy = x + 3 * k * s, y - h * 0.86
    if inst == "trumpet":
        out.append(f'<path d="M{hx:.1f} {hy:.1f}l{22 * k * s:.1f} {-8 * k:.1f}" stroke="{INK}" stroke-width="{2.4 * k:.1f}" stroke-linecap="round"/>'
                   f'<path d="M{hx + 20 * k * s:.1f} {hy - 7 * k:.1f}l{6 * k * s:.1f} {-6 * k:.1f}l{3 * k * s:.1f} {9 * k:.1f}Z" fill="{INK}"/>'
                   f'<path d="M{hx + 8 * k * s:.1f} {hy - 3 * k:.1f}l{1 * k * s:.1f} {-4 * k:.1f}m{3 * k * s:.1f} {-1 * k:.1f}l{1 * k * s:.1f} {-4 * k:.1f}" stroke="{INK}" stroke-width="{1.4 * k:.1f}"/>'
                   f'<path d="M{x + 2 * k * s:.1f} {y - h * 0.68:.1f}L{hx + 9 * k * s:.1f} {hy - 1 * k:.1f}" stroke="{INK}" stroke-width="{2.2 * k:.1f}" stroke-linecap="round"/>')
        for i in range(3):      # notes drifting up from the bell
            nx, ny = hx + (30 + i * 10) * k * s, hy - (16 + i * 12) * k
            out.append(f'<ellipse cx="{nx:.1f}" cy="{ny:.1f}" rx="{2.6 * k:.1f}" ry="{2 * k:.1f}" fill="{INK}" transform="rotate(-20 {nx:.1f} {ny:.1f})"/>'
                       f'<path d="M{nx + 2.3 * k:.1f} {ny:.1f}v{-9 * k:.1f}q{3 * k:.1f} {2 * k:.1f} {4 * k:.1f} {5 * k:.1f}" fill="none" stroke="{INK}" stroke-width="{1.3 * k:.1f}"/>')
    elif inst == "tuba":
        cx_, cy_ = x + 2 * k * s, y - h * 0.6
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{9 * k:.1f}" fill="none" stroke="{INK}" stroke-width="{3.2 * k:.1f}"/>'
                   f'<path d="M{cx_ - 4 * k * s:.1f} {cy_ - 8 * k:.1f}l{-4 * k * s:.1f} {-18 * k:.1f}" stroke="{INK}" stroke-width="{4 * k:.1f}"/>'
                   f'<ellipse cx="{cx_ - 9 * k * s:.1f}" cy="{cy_ - 28 * k:.1f}" rx="{10 * k:.1f}" ry="{3.5 * k:.1f}" fill="{PAPER}" stroke="{INK}" stroke-width="{2 * k:.1f}"/>'
                   f'<ellipse cx="{cx_ - 9 * k * s:.1f}" cy="{cy_ - 28 * k:.1f}" rx="{6 * k:.1f}" ry="{1.6 * k:.1f}" fill="{INK}"/>')
    else:     # banjo, held across the body
        cx_, cy_ = x - 2 * k * s, y - h * 0.55
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{7 * k:.1f}" fill="{PAPER}" stroke="{INK}" stroke-width="{2 * k:.1f}"/>'
                   f'<path d="M{cx_ + 5 * k * s:.1f} {cy_ - 4 * k:.1f}l{22 * k * s:.1f} {-14 * k:.1f}" stroke="{INK}" stroke-width="{2.4 * k:.1f}" stroke-linecap="round"/>'
                   f'<path d="M{cx_ - 3 * k:.1f} {cy_ + 2 * k:.1f}l{6 * k:.1f} {-3 * k:.1f}" stroke="{INK}" stroke-width="{1 * k:.1f}"/>')
    return "".join(out)


@design("new-orleans", "New Orleans", "29.9511° N · 90.0715° W")
def new_orleans(name, coords):
    """A French Quarter townhouse straight on, its two cast-iron galleries hung with ferns and beads, a brass trio
    playing on the banquette, the cathedral spires over the roof, and the street's name inlaid in the sidewalk tiles."""
    p = Pen("new-orleans", 53)
    rnd = p.rnd
    o = [p.paper(9, vignette=0.12)]
    # --- sky: evening haze strokes and the spires of St. Louis Cathedral rising behind the roof
    o.append(p.hatch([(0, 0), (600, 0), (600, 150), (0, 150)], -2, 6.5, 1.0, 0.4, dash=(12, 50),
                     keep=lambda x, y: max(0, 0.55 - y / 260)))
    sx = 430
    # cathedral facade between the towers, seen over the parapet
    o.append(p.shape([(sx - 60, 150), (sx - 60, 120), (sx - 20, 108), (sx + 20, 108), (sx + 60, 120), (sx + 60, 150)], 1.4))
    o.append(p.hatch([(sx + 20, 108), (sx + 60, 120), (sx + 60, 150), (sx + 20, 150)], 80, 3.0, 1.0, 0.6))
    for tx, top, hw in ((sx - 64, 76, 12), (sx + 64, 76, 12)):
        tw = rect(tx - hw, top + 30, hw * 2, 60)
        o.append(p.shape(tw, 1.6))
        o.append(p.hatch([(tx + 3, top + 30), (tx + hw, top + 30), (tx + hw, top + 90), (tx + 3, top + 90)], 90, 2.4, 1.0, 0.8))
        o.append(p.solid(rect(tx - 4, top + 36, 7, 14)) + p.line([(tx - hw - 2, top + 30), (tx + hw + 2, top + 30)], 2.0, 0.1))
        o.append(p.shape([(tx - hw, top + 30), (tx, top - 6), (tx + hw, top + 30)], 1.6))
        o.append(p.hatch([(tx, top - 6), (tx + hw, top + 30), (tx, top + 30)], 70, 2.2, 1.0, 0.85))
        o.append(p.seg(tx, top - 6, tx, top - 15, 1.4) + p.seg(tx - 3, top - 11, tx + 3, top - 11, 1.3))
    # central tower: clock stage, belfry with arched openings, spire and cross
    ct = rect(sx - 20, 96, 40, 56)
    o.append(p.shape(ct, 2.0))
    o.append(p.hatch([(sx + 4, 96), (sx + 20, 96), (sx + 20, 152), (sx + 4, 152)], 90, 2.4, 1.0, 0.8))
    o.append(f'<circle cx="{sx}" cy="114" r="9" fill="{PAPER}" stroke="{INK}" stroke-width="1.8"/>'
             f'<path d="M{sx} 114v-6M{sx} 114l4 2" stroke="{INK}" stroke-width="1.5" stroke-linecap="round"/>')
    o.append(p.line([(sx - 24, 96), (sx + 24, 96)], 2.6, 0.1))
    o.append(p.shape(rect(sx - 15, 74, 30, 22), 1.8))
    o.append(p.windows(sx - 10, 78, 2, 1, 7, 15, 6, 0, w=1.1, dark=1, arch=True, sill=False))
    o.append(p.line([(sx - 19, 74), (sx + 19, 74)], 2.4, 0.1))
    o.append(p.shape([(sx - 15, 74), (sx, 46), (sx + 15, 74)], 1.8))
    o.append(p.hatch([(sx, 46), (sx + 15, 74), (sx, 74)], 75, 2.2, 1.0, 0.85))
    o.append(p.seg(sx, 46, sx, 36, 1.6) + p.seg(sx - 4, 41, sx + 4, 41, 1.6))
    o.append(p.birds([(250, 70), (266, 62, 0.7), (520, 120, 0.6)], 7))
    # --- the roofline: a flat parapet with a moulded cornice and paired chimneys
    par = [(-10, 150), (-10, 134), (610, 134), (610, 150)]
    o.append(p.shape(par, 2.0))
    o.append(p.line([(-10, 131), (610, 131)], 3.0, 0.2))
    o.append(p.hatch([(-10, 142), (610, 142), (610, 150), (-10, 150)], 0, 2.0, 1.0, 0.85))
    dent = "".join(f"M{x} 142v-5" for x in range(-6, 610, 7))
    o.append(f'<path d="{dent}" stroke="{INK}" stroke-width="1.6"/>')
    for cx_ in (40, 92, 238, 290):
        ch = rect(cx_ - 10, 96, 20, 36)
        o.append(p.shape(ch, 1.8) + p.hatch(ch, 0, 3.2, 1.0, 0.6) + p.line([(cx_ - 13, 96), (cx_ + 13, 96)], 3.0, 0.1))
        o.append(p.shape(rect(cx_ - 5, 88, 10, 8), 1.4))
    o.append(f'<path d="M92 84q-6 -10 2 -18q8 -8 0 -18M98 82q8 -8 2 -16" fill="none" stroke="{INK}" stroke-width="1.2" opacity="0.7"/>')
    # --- the stucco facade, three floors
    wall = [(-10, 150), (610, 150), (610, 472), (-10, 472)]
    o.append(p.shape(wall, 2.0))
    o.append(p.stipple(wall, 260, r=(0.5, 0.9), op=0.6))
    # shadow bands under each gallery roof
    for y0, y1 in ((150, 196), (258, 300), (366, 396)):
        o.append(p.hatch([(-10, y0), (610, y0), (610, y0 + (y1 - y0) * 0.6), (-10, y0 + (y1 - y0) * 0.6)], 4, 2.2, 1.0, 0.8))
        o.append(p.hatch([(-10, y0), (610, y0), (610, y1), (-10, y1)], 4, 4.4, 1.0, 0.6, keep=lambda x, y, y0=y0, y1=y1: 1.0 - (y - y0) / (y1 - y0)))
    # doors: three bays per floor
    bays = (95, 300, 505)
    states = (("open", "closed", "open"), ("closed", "open", "open"), ("open", "open", "closed"))
    for fl, (yd, hd) in enumerate(((172, 72), (282, 70))):
        for b, st in zip(bays, states[fl]):
            o.append(french_door(p, b - 20, yd, 40, hd, st))
    # street floor: arched openings, a shop door with a gas lantern
    for b in bays:
        o.append(p.shape([(b - 26, 472), (b - 26, 412)] + arc_pts(b, 412, 26, 22, 180, 360, 12) + [(b + 26, 472)], 1.8, fill=INK))
        o.append(p.line(arc_pts(b, 412, 32, 28, 180, 360, 12), 1.4, 0.2))
        gl = "".join(f"M{b - 26 + k * 13:.1f} {414:.1f}V472" for k in range(1, 4)) + f"M{b - 26} 436h52"
        o.append(f'<path d="{gl}" stroke="{PAPER}" stroke-width="1.1" opacity="0.8"/>')
    # --- the galleries: posts, lace valances, railings, floors
    posts = [-4, 200, 404, 608]
    for (top, rail_y0, floor_y) in ((150, 214, 246), (258, 322, 354)):
        # gallery roof edge / floor fascia
        o.append(p.shape([(-10, top), (610, top), (610, top + 10), (-10, top + 10)], 2.0))
        o.append(p.hatch([(-10, top + 4), (610, top + 4), (610, top + 10), (-10, top + 10)], 0, 2.0, 1.0, 0.8))
        o.append(lace_frieze(p, -10, 610, top + 10, 20))
        o.append(lace_panel(p, -10, 610, rail_y0, floor_y))
    o.append(p.shape([(-10, 246), (610, 246), (610, 258), (-10, 258)], 2.0))
    o.append(p.hatch([(-10, 251), (610, 251), (610, 258), (-10, 258)], 0, 2.0, 1.0, 0.8))
    o.append(p.shape([(-10, 354), (610, 354), (610, 366), (-10, 366)], 2.0))
    o.append(p.hatch([(-10, 359), (610, 359), (610, 366), (-10, 366)], 0, 2.0, 1.0, 0.8))
    for x in posts:
        for y0, y1 in ((160, 246), (268, 354), (366, 476)):
            o.append(p.shape(rect(x - 4, y0, 8, y1 - y0), 1.6))
            o.append(p.hatch(rect(x, y0, 4, y1 - y0), 90, 1.8, 1.0, 0.9))
            for yy in (y0 + 8, y1 - 10):
                o.append(p.shape(rect(x - 6, yy - 3, 12, 6), 1.3))
        # lace brackets in the corners between post and valance
        for s in (-1, 1):
            for y0 in (180, 288):
                o.append(f'<path d="M{x + 4 * s:.1f} {y0 + 26:.1f}q{14 * s:.1f} -6 {22 * s:.1f} -26M{x + 4 * s:.1f} {y0 + 14:.1f}q{8 * s:.1f} -2 {12 * s:.1f} -14" fill="none" stroke="{INK}" stroke-width="1.3"/>'
                         f'<circle cx="{x + 12 * s:.1f}" cy="{y0 + 12:.1f}" r="2.4" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    # ferns hanging in the upper gallery, Mardi Gras beads draped over the railings
    for fx in (150, 456):
        o.append(hanging_fern(p, fx, 180, 14, 15))
    for fx in (98, 302, 504):
        o.append(hanging_fern(p, fx, 290, 4, 13))
    for x0, x1, y, sag in ((40, 140, 218, 22), (60, 120, 220, 12), (330, 400, 326, 18), (420, 520, 218, 26), (440, 490, 220, 14), (230, 290, 326, 20)):
        pts = [(x0 + (x1 - x0) * t, y + sag * 4 * t * (1 - t)) for t in [k / 30 for k in range(31)]]
        o.append('<g fill="' + INK + '">' + "".join(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="1.6"/>' for a, b in pts[::2]) + "</g>")
    # potted geraniums on the lower gallery railing
    for gx in (64, 262, 548):
        o.append(p.shape([(gx - 10, 322), (gx + 10, 322), (gx + 8, 310), (gx - 8, 310)], 1.4) + p.hatch([(gx - 10, 322), (gx + 10, 322), (gx + 8, 310), (gx - 8, 310)], 90, 2.2, 1.0, 0.8))
        o.append(p.foliage(gx, 302, 14, 9, w=1.2, shade=0.5, bump=3, inner=0.5))
    # a gas lantern on the street-floor post, flickering
    lx, ly = 404, 404
    o.append(p.seg(lx + 4, ly - 6, lx + 22, ly - 6, 1.8) + p.line([(lx + 4, ly + 4), (lx + 14, ly - 6)], 1.3))
    o.append(p.shape([(lx + 16, ly - 2), (lx + 13, ly + 18), (lx + 31, ly + 18), (lx + 28, ly - 2)], 1.6))
    o.append(p.solid([(lx + 12, ly - 2), (lx + 22, ly - 10), (lx + 32, ly - 2)]))
    o.append(f'<path d="M{lx + 22} {ly + 14}q-4 -6 0 -12q4 6 0 12Z" fill="{INK}"/>')
    for k in range(8):
        a = math.pi * 2 * k / 8
        o.append(p.seg(lx + 22 + 14 * math.cos(a), ly + 8 + 14 * math.sin(a), lx + 22 + 19 * math.cos(a), ly + 8 + 19 * math.sin(a), 1.2, 0.0))
    # --- the banquette: flagstones in a running bond, the brass trio, a dog listening
    walk = [(-10, 476), (610, 476), (610, 610), (-10, 610)]
    o.append(p.shape(walk, 2.2))
    y = 476
    k = 0
    fl = []
    while y < 600:
        y += 22
        fl.append(f"M-10 {y:.1f}H610")
        off = 0 if k % 2 else 34
        for x in range(-int(off), 610, 68):
            fl.append(f"M{x:.1f} {y - 22:.1f}v22")
        k += 1
    o.append(f'<path d="{"".join(fl)}" stroke="{INK}" stroke-width="1.0" opacity="0.5"/>')
    o.append(p.stipple(walk, 140, r=(0.5, 1.0), op=0.7))
    o.append(musician(p, 170, 482, 92, "trumpet"))
    o.append(musician(p, 236, 482, 96, "tuba", flip=True))
    o.append(musician(p, 470, 482, 90, "banjo", flip=True))
    o.append(p.shape([(250, 478), (262, 478), (264, 470), (248, 470)], 1.2) + p.hatch([(250, 478), (262, 478), (264, 470), (248, 470)], 45, 2.2, 1.0, 0.8))
    dx, dy = 520, 482
    o.append(f'<path d="M{dx} {dy}l2 -10q-2 -6 4 -8h14q4 0 6 -4l3 -6l4 2l-1 6q4 2 2 6l-4 0q-2 4 -4 6l1 8h-3l-2 -6h-10l-2 6h-3l0 -6q-3 0 -4 6Z" fill="{INK}"/>')
    # --- the street name, inlaid in the sidewalk in tiles
    tx0, tx1, ty0, ty1 = 92, 508, 486, 552
    o.append(p.shape(rect(tx0 - 6, ty0 - 6, tx1 - tx0 + 12, ty1 - ty0 + 12), 2.2))
    border = []
    for x in range(int(tx0), int(tx1), 8):
        for yy in (ty0 - 6, ty1 - 2):
            if (x // 8) % 2 == 0:
                border.append(f'<rect x="{x}" y="{yy}" width="8" height="8"/>')
    for yy in range(int(ty0) + 2, int(ty1) - 2, 8):
        for x in (tx0 - 6, tx1 - 2):
            if (yy // 8) % 2 == 0:
                border.append(f'<rect x="{x}" y="{yy}" width="8" height="8"/>')
    o.append(f'<g fill="{INK}">' + "".join(border) + "</g>")
    o.append(p.shape(rect(tx0 + 4, ty0 + 4, tx1 - tx0 - 8, ty1 - ty0 - 8), 1.4))
    grid = "".join(f"M{x} {ty0 + 4}V{ty1 - 4}" for x in range(int(tx0) + 16, int(tx1) - 4, 12)) + "".join(f"M{tx0 + 4} {y}H{tx1 - 4}" for y in range(int(ty0) + 16, int(ty1) - 4, 12))
    o.append(f'<path d="{grid}" stroke="{INK}" stroke-width="0.8" opacity="0.2"/>')
    sz = name_size(name, tx1 - tx0 - 44, 44)
    o.append(title_text(300, 523, name, sz))
    o.append(title_text(300, 543, coords, fit_size(coords, MONO, 16, 330, 1.6), MONO, ls=1.6))
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- WASHINGTON DC
def blossom_branch(p, ctrl, w0, w1, twigs, wash="#E8A3B4", n_fl=40, spread=26):
    """A cherry branch in ink with clusters of five-petal blossoms along it; a faded pink wash under the clusters."""
    rnd = p.rnd
    out = [p.branch(ctrl, w0, w1, bark=False)]
    c = smooth(ctrl, 8)
    pts = []
    for tw in twigs:
        out.append(p.branch(tw, max(2.0, w1 * 0.8), 1.2, bark=False))
        pts += smooth(tw, 4)[2:]
    pts += c[len(c) // 3:]
    washes, flowers = [], []
    for _ in range(n_fl):
        bx, by = rnd.choice(pts)
        x, y = bx + rnd.uniform(-spread, spread) * 0.6, by + rnd.uniform(-spread, spread) * 0.5
        r = rnd.uniform(3.4, 5.2)
        washes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 2.0:.1f}"/>')
        a0 = rnd.uniform(0, 1.2)
        petals = []
        for k in range(5):
            a = a0 + 2 * math.pi * k / 5
            px_, py_ = x + r * math.cos(a), y + r * math.sin(a)
            petals.append(f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="{r * 0.62:.1f}"/>')
        flowers.append(f'<g fill="{PAPER}" stroke="{INK}" stroke-width="1.1">{"".join(petals)}</g>'
                       f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.55:.1f}" fill="{PAPER}"/>'
                       f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.3" fill="{INK}"/>')
        if rnd.random() < 0.5:   # stamens
            flowers.append("".join(f'<circle cx="{x + 2.2 * math.cos(a0 + k):.1f}" cy="{y + 2.2 * math.sin(a0 + k):.1f}" r="0.7" fill="{INK}"/>' for k in range(3)))
    out.insert(0, f'<g fill="{wash}" opacity="0.5">{"".join(washes)}</g>')
    # buds: little dark ovals at twig tips
    for tw in twigs:
        x, y = tw[-1]
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="2.4" ry="3.4" fill="{INK}"/>')
    out.append("".join(flowers))
    return "".join(out)


@design("washington-dc", "Washington, DC", "38.9072° N · 77.0369° W")
def washington_dc(name, coords):
    """The Capitol dome from the west across the Capitol Reflecting Pool in cherry-blossom season."""
    p = Pen("washington-dc", 61)
    rnd = p.rnd
    o = [p.paper(11)]
    cx = 300
    G = 352                       # the far rim of the pool
    # --- sky: soft morning haze, strokes thicker toward the horizon
    o.append(p.hatch([(0, 150), (600, 150), (600, G), (0, G)], -2, 5.0, 1.0, 0.45, dash=(14, 44),
                     keep=lambda x, y: max(0, (y - 170) / 190) * (0.4 if abs(x - cx) < 110 else 1)))
    o.append(p.clouds(470, 196, 0.62) + p.clouds(118, 236, 0.5))
    o.append(p.birds([(452, 128), (470, 120, 0.7), (488, 132, 0.6)], 7))
    # --- the Capitol: dome profile (half-widths), drum and attic, the west front and the wings
    # wings, running off both edges
    for sgn in (-1, 1):
        x0, x1 = (cx + sgn * 128, cx + sgn * 330)
        a, b = min(x0, x1), max(x0, x1)
        wing = rect(a, 272, b - a, G - 272)
        o.append(p.shape(wing, 1.8))
        o.append(p.line([(a, 272), (b, 272)], 2.6, 0.2))
        bal = "".join(f"M{x:.1f} 268v-6" for x in range(int(a) + 3, int(b), 5))
        o.append(f'<path d="{bal}" stroke="{INK}" stroke-width="1.1"/>' + p.line([(a, 262), (b, 262)], 1.6, 0.2))
        o.append(p.windows(a + 8, 284, int((b - a - 10) / 15), 2, 7, 13, 8, 10, w=1.1, dark=0.75, sill=False))
        o.append(p.hatch(rect(a, 318, b - a, G - 318), 0, 2.6, 1.0, 0.55, dash=(8, 4)))
        for x in range(int(a) + 4, int(b), 15):
            o.append(p.seg(x - 3, 280, x - 3, 316, 1.0, 0.1, op=0.8))
    # central block with the west colonnade
    cb = rect(cx - 132, 256, 264, G - 256)
    o.append(p.shape(cb, 2.2))
    o.append(p.line([(cx - 136, 256), (cx + 136, 256)], 3.0, 0.2))
    bal = "".join(f"M{x:.1f} 252v-7" for x in range(cx - 130, cx + 132, 5))
    o.append(f'<path d="{bal}" stroke="{INK}" stroke-width="1.2"/>' + p.line([(cx - 134, 244), (cx + 134, 244)], 1.8, 0.2))
    # recessed loggia: dark behind the columns
    o.append(p.solid(rect(cx - 96, 270, 192, 50)))
    o.append(p.windows(cx - 90, 278, 12, 2, 6, 12, 9.5, 8, w=0.9, dark=0.0, sill=False).replace(f'fill="{PAPER}" stroke="{INK}"', f'fill="{INK}" stroke="{PAPER}"'))
    for k in range(13):
        x = cx - 96 + k * 16
        col = rect(x - 3.6, 268, 7.2, 52)
        o.append(p.shape(col, 1.3))
        o.append(p.hatch(rect(x + 0.6, 268, 3, 52), 90, 1.6, 1.0, 0.85))
        o.append(p.line([(x - 5.5, 268), (x + 5.5, 268)], 2.0, 0.1))
    o.append(p.line([(cx - 104, 266), (cx + 104, 266)], 2.4, 0.1) + p.line([(cx - 104, 321), (cx + 104, 321)], 2.4, 0.1))
    o.append(p.hatch(rect(cx - 132, 322, 264, G - 322), 0, 2.4, 1.0, 0.7, dash=(10, 4)))
    for sgn in (-1, 1):
        o.append(p.windows(cx + sgn * 116 - 7, 274, 1, 3, 9, 12, 0, 6, w=1.1, dark=0.6))
    # the drum: a peristyle of 36 columns seen as a curved colonnade, shaded on the right
    d0, d1, R = 202, 252, 104
    drum = rect(cx - R, d0, 2 * R, d1 - d0)
    o.append(p.shape(drum, 2.2))
    o.append(p.solid(rect(cx - R + 6, d0 + 10, 2 * R - 12, d1 - d0 - 16)))
    for k in range(19):
        t = math.pi * (k + 0.5) / 19
        x = cx - R * math.cos(t) * 0.97
        wcol = 7.0 * math.sin(t) + 1.2
        o.append(p.shape(rect(x - wcol / 2, d0 + 8, wcol, d1 - d0 - 14), 1.2))
        if x > cx:
            o.append(p.hatch(rect(x - wcol / 2 + wcol * 0.3, d0 + 8, wcol * 0.7, d1 - d0 - 14), 90, 1.6, 1.0, 0.9))
    o.append(p.shape(rect(cx - R - 4, d1 - 8, 2 * R + 8, 8), 1.8))
    o.append(p.shape(rect(cx - R - 6, d0, 2 * R + 12, 9), 2.0))
    o.append(p.hatch(rect(cx - R - 6, d0 + 4, 2 * R + 12, 5), 0, 1.8, 1.0, 0.85))
    o.append(p.tone([(cx + R * 0.55, d1 - 8), (cx + R + 4, d1 - 8), (cx + R + 4, d1), (cx + R * 0.55, d1)], 2, 0))
    # attic with its ring of windows, and the balustrade
    a0, a1, RA = 170, 202, 88
    att = rect(cx - RA, a0, 2 * RA, a1 - a0)
    o.append(p.shape(att, 2.0))
    for k in range(13):
        t = math.pi * (k + 0.5) / 13
        x = cx - RA * math.cos(t) * 0.92
        ww = 6.5 * math.sin(t) + 0.8
        o.append(p.shape([(x - ww / 2, a1 - 6), (x - ww / 2, a0 + 10)] + arc_pts(x, a0 + 10, ww / 2, 3, 180, 360, 4) + [(x + ww / 2, a1 - 6)], 1.0, fill=INK))
        o.append(p.seg(x + ww / 2 + 3.5 * math.sin(t), a0 + 4, x + ww / 2 + 3.5 * math.sin(t), a1 - 3, 1.0, 0.0, op=0.8))
    o.append(p.hatch([(cx + RA * 0.4, a0), (cx + RA, a0), (cx + RA, a1), (cx + RA * 0.4, a1)], 80, 2.6, 1.0, 0.8))
    o.append(p.line([(cx - RA - 4, a0), (cx + RA + 4, a0)], 2.6, 0.1))
    # the cast-iron shell: ribbed, lit from the left, three tiers of small windows
    s0, s1, RS = 170, 90, 80
    shell = [(cx - RS, s0)] + [(cx - RS * math.cos(t) * (1 - 0.06 * math.sin(t)), s0 - (s0 - s1) * math.sin(t) ** 0.9) for t in [math.pi / 2 * k / 20 for k in range(1, 21)]]
    shell = shell + [(2 * cx - x, y) for x, y in shell[::-1]]
    o.append(p.shape(shell, 2.4))
    o.append(p.hatch(shell, 100, 3.0, 1.05, 0.85, keep=lambda x, y: max(0, min(1, (x - cx + 10) / 60))))
    o.append(p.hatch(shell, 60, 3.4, 1.0, 0.75, keep=lambda x, y: max(0, (x - cx - 30) / 40)))
    o.append(p.stipple(shell, 70, r=(0.5, 0.9), keep=lambda x, y: max(0, 0.6 - abs(x - cx + 30) / 70)))
    for k in range(-5, 6):
        f = k / 6
        rib = [(cx + RS * f * (1 - 0.06 * math.sin(t)) * math.cos(t), s0 - (s0 - s1) * math.sin(t) ** 0.9) for t in [math.pi / 2 * j / 12 for j in range(13)]]
        o.append(p.line(rib, 1.4 if abs(k) < 5 else 1.1, 0.2))
    for tier, (yy, hh) in enumerate(((160, 7), (142, 6), (124, 5))):
        rr = RS * math.cos(math.asin(min(1, ((s0 - yy) / (s0 - s1)) ** (1 / 0.9))))
        for k in range(-5, 5):
            f = (k + 0.5) / 6
            x = cx + rr * f
            o.append(p.solid(rect(x - 1.6, yy - hh, 3.2, hh)))
    # lantern (tholos) and the Statue of Freedom
    L0 = 70
    o.append(p.shape(rect(cx - 15, L0, 30, 22), 1.8))
    o.append(p.solid(rect(cx - 11, L0 + 4, 22, 16)))
    for k in range(5):
        x = cx - 11 + k * 5.5
        o.append(p.shape(rect(x - 1.3, L0 + 3, 2.6, 18), 0.9))
    o.append(p.line([(cx - 19, L0), (cx + 19, L0)], 2.6, 0.1) + p.line([(cx - 17, L0 + 22), (cx + 17, L0 + 22)], 2.2, 0.1))
    o.append(p.shape(arc_pts(cx, L0, 15, 8, 180, 360, 10), 1.6) + p.hatch(arc_pts(cx, L0, 15, 8, 270, 360, 6) + [(cx, L0)], 90, 2.0, 1.0, 0.8))
    o.append(p.solid([(cx - 4, L0 - 8), (cx - 3, L0 - 20), (cx - 2, L0 - 24), (cx + 2, L0 - 24), (cx + 3, L0 - 20), (cx + 4, L0 - 8)]) + f'<circle cx="{cx}" cy="{L0 - 27}" r="2.6" fill="{INK}"/>'
             + p.seg(cx, L0 - 28, cx, L0 - 32, 1.6) + p.seg(cx + 4, L0 - 20, cx + 6, L0 - 10, 1.4))
    # flag on the west front
    o.append(p.seg(cx, 244, cx, 222, 1.4) + p.shape([(cx, 222), (cx + 14, 224), (cx + 13, 231), (cx, 230)], 1.1)
             + p.hatch([(cx, 222), (cx + 14, 224), (cx + 13, 231), (cx, 230)], 0, 1.6, 1.0, 0.8))
    # --- trees flanking the lawn, terraces and the steps
    for x, y, rx, ry in ((40, 318, 66, 44), (126, 330, 56, 34), (474, 330, 56, 34), (560, 318, 66, 44), (186, 340, 30, 18), (414, 340, 30, 18)):
        o.append(p.solid(arc_pts(x, y, rx * 1.05, ry * 1.05, 0, 360, 24), PAPER))
        o.append(p.scribble(x, y, rx, ry, sp=4.4, loop=2.6, w=1.05, base=0.6, shade=1.0, dark=0.35, light=(-1, -0.7), cr=(12, 22)))
    o.append(p.line([(0, G), (600, G)], 2.0, 0.4))
    o.append(p.line([(0, G - 4), (600, G - 4)], 1.1, 0.4))
    # --- the reflecting pool: the dome's reflection as broken strokes, ripples, ducks
    W0, W1 = G + 6, 466
    o.append(p.shape([(-10, G + 2), (610, G + 2), (610, G + 6), (-10, G + 6)], 1.4))
    def mirror(poly):
        return [(x, 2 * G + 6 - y) for x, y in poly]
    refl = mirror(shell) + []
    pool = lambda poly: [(x, min(max(y, W0), W1 - 2)) for x, y in poly]
    o.append(p.hatch(pool(mirror(rect(cx - R, d0, 2 * R, d1 - d0))), 0, 2.6, 1.3, 0.9, dash=(8, 6)))
    o.append(p.hatch(pool(mirror(rect(cx - 96, 270, 192, 50))), 0, 2.4, 1.4, 0.95, dash=(10, 4)))
    o.append(p.hatch(pool(mirror(rect(cx - 132, 256, 264, G - 256))), 0, 3.4, 1.2, 0.75, dash=(8, 10)))
    o.append(p.hatch(pool(mirror(rect(-10, 272, 620, G - 272))), 0, 4.0, 1.1, 0.6, dash=(5, 16)))
    for x, rx in ((40, 66), (126, 56), (474, 56), (560, 66)):
        o.append(p.hatch(pool(mirror(arc_pts(x, G - 30, rx, 30, 180, 360, 12))), 0, 2.8, 1.2, 0.9, dash=(6, 6)))
    o.append(p.ripples(0, 600, W0 + 4, W1, 120, hy=W0, lmin=6, lmax=26, wmin=1.0, wmax=1.6))
    for dx, dy, f in ((168, 420, 1), (190, 428, 1), (430, 404, -1)):
        o.append(f'<path d="M{dx - 8 * f} {dy}q{2 * f} 6 {12 * f} 5q{6 * f} 0 {8 * f} -5l{-2 * f} -2q{-2 * f} -5 {2 * f} -8l{3 * f} 1l{-2 * f} 2q{-1 * f} 3 0 5Z" fill="{PAPER}" stroke="{INK}" stroke-width="1.3"/>'
                 f'<path d="M{dx - 10 * f} {dy + 5}q{8 * f} 4 {22 * f} 0" fill="none" stroke="{INK}" stroke-width="1.1"/>'
                 f'<path d="M{dx - 2 * f} {dy + 1}q{4 * f} -3 {8 * f} 0" fill="none" stroke="{INK}" stroke-width="1"/>')
    # the near rim of the pool, granite coping
    o.append(p.shape([(-10, W1), (610, W1), (610, W1 + 10), (-10, W1 + 10)], 2.0))
    o.append(p.grass(-10, 610, 604, 160, (4, 12), 1.2) + p.stipple([(-10, W1 + 10), (610, W1 + 10), (610, 610), (-10, 610)], 120, r=(0.5, 1.0), op=0.6))
    o.append(p.line([(-10, W1 + 18), (610, W1 + 18)], 1.0, 0.4))
    # a jogger and a couple with a stroller along the rim
    o.append(p.person(84, W1, 36, 0, flip=False) + p.person(520, W1, 34, 1, flip=True, dress=True) + p.person(534, W1, 35, 1, flip=True))
    o.append(f'<circle cx="503" cy="{W1 - 4}" r="4" fill="none" stroke="{INK}" stroke-width="1.4"/><circle cx="491" cy="{W1 - 4}" r="4" fill="none" stroke="{INK}" stroke-width="1.4"/>'
             f'<path d="M487 {W1 - 9}h20l3 -12q-12 -6 -22 0Z" fill="{INK}"/><path d="M507 {W1 - 20}l8 -6" stroke="{INK}" stroke-width="1.6"/>')
    # --- cherry branches reaching in from the top corners
    o.append(blossom_branch(p, [(-20, 40), (40, 70), (100, 84), (160, 108), (200, 120)], 20, 4,
                            [[(60, 76), (82, 52), (110, 44)], [(118, 92), (126, 128), (150, 146)], [(30, 64), (40, 110), (30, 150)],
                             [(150, 104), (170, 82), (178, 60)], [(2, 52), (10, 20)]], n_fl=48))
    o.append(blossom_branch(p, [(620, 70), (560, 92), (500, 118), (446, 150), (416, 176)], 20, 4,
                            [[(540, 100), (526, 64), (500, 50)], [(486, 126), (484, 170), (500, 196)], [(590, 82), (590, 130), (606, 160)],
                             [(452, 146), (432, 124), (430, 100)]], n_fl=44))
    # --- title: engraved stone panel with stars
    o.append(cartouche(p, 80, 482, 520, 552, 0.01, 2.4))
    sz = name_size(name, 360, 44)
    o.append(title_text(cx, 519, name, sz))
    o.append(coord_line(p, cx, 542, coords, 16, 1.8, 0, 0))
    for sx_ in (110, 490):
        o.append(f'<polygon points="{star_points(sx_, 512, 9, 3.8)}" fill="{INK}"/>')
        o.append(f'<polygon points="{star_points(sx_ + (14 if sx_ < cx else -14), 528, 5, 2.1)}" fill="{INK}"/>'
                 f'<polygon points="{star_points(sx_ - (8 if sx_ < cx else -8), 530, 5, 2.1)}" fill="{INK}"/>')
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- PHILADELPHIA
def brick_courses(p, poly, sp=3.2, w=0.9, op=0.55, head=10):
    """Flemish-bond brickwork in ink: broken horizontal courses with staggered head joints."""
    x0, y0, x1, y1 = bbox(poly)
    rnd = p.rnd
    d = []
    y = y0 + sp
    row = 0
    while y < y1:
        x = x0 + (head / 2 if row % 2 else 0) - head
        while x < x1:
            L = head * rnd.choice([1, 1, 2])
            if rnd.random() < 0.8:
                d.append(f"M{x + 0.8:.1f} {y:.1f}h{L - 1.6:.1f}")
            if rnd.random() < 0.5:
                d.append(f"M{x + L:.1f} {y - sp:.1f}v{sp:.1f}")
            x += L
        y += sp
        row += 1
    cid = p.uid("br")
    p.defs.append(f'<clipPath id="{cid}"><polygon points="{P(poly)}"/></clipPath>')
    return f'<path d="{"".join(d)}" stroke="{INK}" stroke-width="{w}" opacity="{op}" clip-path="url(#{cid})"/>'


def sash(p, x, y, w, h, panes=(3, 4), w_=1.4, keystone=True):
    """A white-framed sash window with dark glass, glazing bars in paper, a marble lintel with a keystone."""
    out = [p.shape(rect(x - 2, y - 2, w + 4, h + 4), 1.4)]
    out.append(p.solid(rect(x + 1, y + 1, w - 2, h - 2)))
    gl = []
    for k in range(1, panes[0]):
        gl.append(f"M{x + w * k / panes[0]:.1f} {y + 1:.1f}V{y + h - 1:.1f}")
    for k in range(1, panes[1] * 2):
        gl.append(f"M{x + 1:.1f} {y + h * k / (panes[1] * 2):.1f}H{x + w - 1:.1f}")
    out.append(f'<path d="{"".join(gl)}" stroke="{PAPER}" stroke-width="1.1"/>')
    out.append(p.line([(x - 1, y + h / 2), (x + w + 1, y + h / 2)], 1.8, 0.1, color=PAPER))
    if keystone:
        out.append(p.shape([(x - 5, y - 2), (x + w + 5, y - 2), (x + w + 3, y - 9), (x - 3, y - 9)], 1.3))
        out.append(p.shape([(x + w / 2 - 3.5, y - 1), (x + w / 2 + 3.5, y - 1), (x + w / 2 + 4.5, y - 11), (x + w / 2 - 4.5, y - 11)], 1.2))
    out.append(p.line([(x - 4, y + h + 3), (x + w + 4, y + h + 3)], 2.4, 0.1))
    return "".join(out)


@design("philadelphia", "Philadelphia", "39.9526° N · 75.1652° W")
def philadelphia(name, coords):
    """Independence Hall from Independence Square: the brick tower with its Palladian window and the white
    wooden steeple, the main block behind, elms framing the lawn and people strolling the brick paths."""
    p = Pen("philadelphia", 71)
    rnd = p.rnd
    o = [p.paper(13, vignette=0.22)]
    cx = 300
    G = 404
    # --- sky: soft strokes and a few clouds
    o.append(p.hatch([(0, 60), (600, 60), (600, G), (0, G)], -3, 5.2, 1.0, 0.4, dash=(12, 46),
                     keep=lambda x, y: max(0, (y - 100) / 300) * (0.25 if abs(x - cx) < 70 else 1)))
    o.append(p.clouds(150, 120, 0.7) + p.clouds(452, 92, 0.55))
    o.append(p.birds([(398, 150), (414, 142, 0.7), (186, 186, 0.6)], 7))
    # --- the main block: two storeys of Flemish-bond brick, a hipped roof, chimney pairs joined by balustrades
    mx0, mx1 = 66, 534
    top = 300
    roof = [(mx0 - 4, top), (mx0 + 30, top - 38), (mx1 - 30, top - 38), (mx1 + 4, top)]
    o.append(p.shape(roof, 2.0))
    o.append(p.hatch(roof, 6, 3.0, 1.0, 0.7))
    for ex in (mx0 + 40, mx1 - 40):
        for dx in (-22, 22):
            ch = rect(ex + dx - 8, top - 74, 16, 40)
            o.append(p.shape(ch, 1.8) + brick_courses(p, ch, 3.0, 0.9, 0.6, 6) + p.line([(ex + dx - 11, top - 74), (ex + dx + 11, top - 74)], 3.0, 0.1))
        bal = rect(ex - 14, top - 58, 28, 14)
        o.append(p.line([(ex - 14, top - 58), (ex + 14, top - 58)], 1.8, 0.1) + p.line([(ex - 14, top - 46), (ex + 14, top - 46)], 1.4, 0.1))
        o.append(f'<path d="{"".join(f"M{ex - 12 + k * 4:.1f} {top - 57:.1f}v10" for k in range(7))}" stroke="{INK}" stroke-width="1.2"/>')
    main = rect(mx0, top, mx1 - mx0, G - top)
    o.append(p.shape(main, 2.2))
    o.append(brick_courses(p, main, 3.4, 0.9, 0.5, 10))
    o.append(p.line([(mx0 - 6, top), (mx1 + 6, top)], 3.2, 0.2))
    dent = "".join(f"M{x:.1f} {top + 2}v5" for x in range(mx0, mx1, 6))
    o.append(f'<path d="{dent}" stroke="{INK}" stroke-width="1.4"/>')
    o.append(p.hatch(rect(mx0, top + 7, mx1 - mx0, 10), 0, 2.2, 1.0, 0.75))
    # belt course with marble panels between the floors
    o.append(p.shape(rect(mx0, 350, mx1 - mx0, 8), 1.4))
    for x in range(mx0 + 18, mx1 - 20, 44):
        o.append(p.shape(rect(x, 351, 22, 6), 1.0))
    for xw in (86, 132, 178, 386, 432, 478):
        o.append(sash(p, xw, 316, 22, 30, (3, 3)))
        o.append(sash(p, xw, 366, 22, 32, (3, 3)))
    # arcaded piazza wings running off to the sides
    for sgn in (-1, 1):
        x0, x1 = (mx0 - 80, mx0) if sgn < 0 else (mx1, mx1 + 80)
        o.append(p.shape(rect(x0, 352, x1 - x0, G - 352), 1.8))
        o.append(brick_courses(p, rect(x0, 352, x1 - x0, G - 352), 3.4, 0.9, 0.5, 10))
        o.append(p.line([(x0, 352), (x1, 352)], 2.4, 0.1))
        for k in range(3):
            ax = x0 + 14 + k * 26 if sgn > 0 else x1 - 14 - k * 26
            o.append(p.shape([(ax - 9, G), (ax - 9, 376)] + arc_pts(ax, 376, 9, 9, 180, 360, 8) + [(ax + 9, G)], 1.4, fill=INK))
    # --- the tower: three brick stages in front of the main block
    tx0, tx1 = cx - 46, cx + 46
    tb = rect(tx0, 196, tx1 - tx0, G - 196)
    o.append(p.shape(tb, 2.4))
    o.append(brick_courses(p, tb, 3.4, 0.9, 0.55, 10))
    o.append(p.hatch([(cx + 22, 196), (tx1, 196), (tx1, G), (cx + 22, G)], 90, 3.0, 1.0, 0.45))
    for y in (300, 352):
        o.append(p.line([(tx0 - 2, y), (tx1 + 2, y)], 2.4, 0.1))
    # ground floor door with fanlight and steps
    o.append(p.shape([(cx - 16, G - 4), (cx - 16, 372)] + arc_pts(cx, 372, 16, 14, 180, 360, 10) + [(cx + 16, G - 4)], 1.8, fill=INK))
    o.append(p.line(arc_pts(cx, 372, 22, 20, 180, 360, 10), 1.8, 0.1))
    o.append(p.shape([(cx - 4, 352), (cx + 4, 352), (cx + 5, 360), (cx - 5, 360)], 1.2))
    for k in range(3):
        o.append(p.line([(cx - 26 - k * 5, G - 4 + k * 4), (cx + 26 + k * 5, G - 4 + k * 4)], 1.6, 0.1))
    # the Palladian window on the second stage
    o.append(p.shape([(cx - 12, 346), (cx - 12, 316)] + arc_pts(cx, 316, 12, 12, 180, 360, 10) + [(cx + 12, 346)], 1.6, fill=INK))
    o.append(f'<path d="M{cx} 306V346M{cx - 12} 326h24M{cx - 12} 336h24" stroke="{PAPER}" stroke-width="1.1"/>')
    for sgn in (-1, 1):
        o.append(sash(p, cx + sgn * 22 - (8 if sgn > 0 else 8) + (0 if sgn > 0 else 0) - 4 + (4 if sgn > 0 else -4), 318, 8, 28, (1, 3), keystone=False))
    o.append(p.line([(cx - 36, 314), (cx + 36, 314)], 2.0, 0.1))
    o.append(p.line(arc_pts(cx, 316, 17, 17, 180, 360, 10), 2.0, 0.1))
    # third stage: arched window and stone quoins
    o.append(sash(p, cx - 11, 236, 22, 40, (2, 4)))
    o.append(p.shape(arc_pts(cx, 236, 11, 11, 180, 360, 8) + [(cx + 11, 236)], 1.2, fill=INK))
    for y in range(204, G - 4, 14):
        for x, sgn in ((tx0, 1), (tx1, -1)):
            wq = 10 if (y // 14) % 2 else 6
            o.append(p.shape([(x, y), (x + sgn * wq, y), (x + sgn * wq, y + 7), (x, y + 7)], 1.0))
    o.append(p.shape(rect(tx0 - 5, 190, tx1 - tx0 + 10, 8), 2.0))
    o.append(p.hatch(rect(tx0 - 5, 194, tx1 - tx0 + 10, 4), 0, 1.6, 1.0, 0.9))
    # --- the steeple: clock stage, octagonal belfry, lantern, cupola, spire
    s1 = rect(cx - 34, 160, 68, 30)
    o.append(p.shape(s1, 2.0))
    o.append(p.hatch([(cx + 16, 160), (cx + 34, 160), (cx + 34, 190), (cx + 16, 190)], 90, 2.4, 1.0, 0.7))
    o.append(f'<circle cx="{cx}" cy="175" r="11" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>'
             + "".join(f'<path d="M{cx + 8.5 * math.cos(math.pi * k / 6):.1f} {175 + 8.5 * math.sin(math.pi * k / 6):.1f}l{1.8 * math.cos(math.pi * k / 6):.1f} {1.8 * math.sin(math.pi * k / 6):.1f}" stroke="{INK}" stroke-width="1.2"/>' for k in range(12))
             + f'<path d="M{cx} 175v-7M{cx} 175l5 2" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/>')
    o.append(p.line([(cx - 38, 160), (cx + 38, 160)], 2.6, 0.1))
    for sgn in (-1, 1):                                     # balustrade with urns
        o.append(f'<path d="{"".join(f"M{cx + sgn * (6 + k * 4):.1f} 158v-8" for k in range(8))}" stroke="{INK}" stroke-width="1.1"/>')
        ux = cx + sgn * 36
        o.append(p.shape([(ux - 3, 160), (ux - 4, 152), (ux - 2, 149), (ux + 2, 149), (ux + 4, 152), (ux + 3, 160)], 1.2) + p.seg(ux, 149, ux, 145, 1.4))
    o.append(p.line([(cx - 36, 150), (cx + 36, 150)], 1.6, 0.1))
    bel = [(cx - 24, 150), (cx - 24, 108), (cx + 24, 108), (cx + 24, 150)]
    o.append(p.shape(bel, 2.0))
    for x in (cx - 14, cx, cx + 14):                        # arched openings, louvres dark
        o.append(p.shape([(x - 4.5, 146), (x - 4.5, 120)] + arc_pts(x, 120, 4.5, 4.5, 180, 360, 6) + [(x + 4.5, 146)], 1.1, fill=INK))
    for x in (cx - 24, cx - 7, cx + 7, cx + 24):
        o.append(p.seg(x, 110, x, 148, 1.6, 0.1))
    o.append(p.hatch([(cx + 8, 108), (cx + 24, 108), (cx + 24, 150), (cx + 8, 150)], 80, 3.0, 1.0, 0.6))
    o.append(p.line([(cx - 28, 108), (cx + 28, 108)], 2.6, 0.1))
    for sgn in (-1, 1):
        ux = cx + sgn * 26
        o.append(p.shape([(ux - 2.5, 108), (ux - 3.5, 101), (ux, 97), (ux + 3.5, 101), (ux + 2.5, 108)], 1.1))
    lan = [(cx - 15, 106), (cx - 15, 84), (cx + 15, 84), (cx + 15, 106)]
    o.append(p.shape(lan, 1.8))
    for x in (cx - 7, cx + 7):
        o.append(f'<circle cx="{x}" cy="95" r="3.6" fill="{INK}"/>')
    o.append(p.line([(cx - 18, 84), (cx + 18, 84)], 2.2, 0.1))
    cup = arc_pts(cx, 84, 15, 14, 180, 360, 12)
    o.append(p.shape(cup + [(cx + 15, 84)], 1.8) + p.hatch(cup, 75, 2.2, 1.0, 0.85, keep=lambda x, y: (x - cx + 4) / 16))
    o.append(p.shape([(cx - 3, 70), (cx, 52), (cx + 3, 70)], 1.4))
    o.append(p.seg(cx, 52, cx, 44, 1.4) + p.line([(cx - 2, 47), (cx + 9, 46), (cx + 7, 49)], 1.4, 0.0))
    o.append(f'<circle cx="{cx}" cy="70" r="2.4" fill="{INK}"/>')
    # --- the square: lawn, brick paths, elms, lamps, people, pigeons, a squirrel
    lawn = [(-10, G), (610, G), (610, 610), (-10, 610)]
    o.append(p.line([(-10, G), (610, G)], 2.2, 0.4))
    path = [(cx - 28, G + 6), (cx + 28, G + 6), (cx + 120, 610), (cx - 120, 610)]
    o.append(p.shape(path, 1.8))
    hb = []
    y = G + 10
    k = 0
    while y < 600:
        t = (y - G) / (600 - G)
        half = 28 + 92 * t
        step = 8 + 14 * t
        off = 0 if k % 2 else step / 2
        hb.append(f"M{cx - half:.1f} {y:.1f}H{cx + half:.1f}")
        x = cx - half + off
        while x < cx + half:
            hb.append(f"M{x:.1f} {y:.1f}v{-(3 + 6 * t):.1f}")
            x += step
        y += 3 + 6 * t
        k += 1
    cid = p.uid("pth")
    p.defs.append(f'<clipPath id="{cid}"><polygon points="{P(path)}"/></clipPath>')
    o.append(f'<path d="{"".join(hb)}" stroke="{INK}" stroke-width="0.9" opacity="0.5" clip-path="url(#{cid})"/>')
    # the lawn: rows of grass ticks, sparse near the building and fuller toward us
    gt = []
    y = G + 8
    while y < 610:
        t = (y - G) / 200
        for _ in range(int(10 + 26 * t)):
            x = rnd.uniform(-10, 610)
            if abs(x - cx) < 30 + 92 * (y - G) / (600 - G) + 6:
                continue
            if 470 < y < 560 and 120 < x < 480:
                continue
            hh = 2 + 5 * t
            gt.append(f"M{x:.1f} {y:.1f}l{rnd.uniform(-1.5, 1.5):.1f} {-hh:.1f}")
        y += 4 + 8 * t
    o.append(f'<path d="{"".join(gt)}" stroke="{INK}" stroke-width="1.1" stroke-linecap="round" opacity="0.75"/>')
    # elms framing the view: forked trunks rising into clumped crowns cut by the edges
    o.append(p.branch([(30, 640), (36, 520), (40, 420), (52, 330), (80, 250)], 30, 12))
    o.append(p.branch([(42, 400), (20, 330), (-4, 270)], 16, 8))
    o.append(p.branch([(574, 640), (566, 520), (562, 420), (552, 330), (524, 256)], 30, 12))
    o.append(p.branch([(562, 410), (586, 330), (612, 280)], 16, 8))
    o.append(p.crown(40, 170, 110, 150, lobes=7, light=(1, -0.6), dense=1.5))
    o.append(p.crown(566, 182, 104, 146, lobes=7, light=(-1, -0.6), dense=1.5))
    # Franklin lamps along the path
    for lx, h in ((cx - 70, 74), (cx + 70, 74)):
        o.append(p.lamp(lx, G + 34, h, w=1.8))
    for (x, y, h, pose, flip, dress, bag) in ((cx - 54, 470, 44, 0, False, True, True), (cx - 40, 472, 46, 1, False, False, False),
                                             (cx + 50, 452, 34, 0, True, False, True), (cx + 18, 430, 24, 1, True, True, False),
                                             (cx - 14, 426, 22, 0, False, False, False), (cx + 140, 440, 30, 1, True, True, False)):
        o.append(p.person(x, y, h, pose, flip, bag, dress))
    o.append(p.person(cx - 26, 474, 26, 1))           # a child holding a hand
    for bx, by in ((cx + 70, 520), (cx + 84, 526), (cx + 60, 532)):
        o.append(f'<path d="M{bx - 6} {by}q2 -6 9 -5l3 -3l2 2l-2 2q0 5 -6 5Z" fill="{INK}"/>')
    sx_, sy_ = 112, 470                                  # a squirrel on the lawn
    o.append(f'<path d="M{sx_} {sy_}q-2 -10 6 -12q4 -1 6 3l3 -1l1 3q-3 2 -2 5l-2 2h-10Z" fill="{INK}"/>'
             f'<path d="M{sx_} {sy_ - 2}q-14 -4 -10 -18q4 -8 10 -2q-6 4 0 12" fill="{INK}"/>')
    # --- the title on a gentle arc over the lawn, coordinates beneath
    sz = name_size(name, 380, 58)
    r = 520
    o.append(f'<defs><path id="philadelphia-arc" d="M{cx - r} {518 - r} A {r} {r} 0 0 0 {cx + r} {518 - r}" fill="none"/></defs>')
    o.append(f'<text {DMS} font-size="{sz}" fill="{PAPER}" stroke="{PAPER}" stroke-width="10" stroke-linejoin="round" text-anchor="middle"><textPath href="#philadelphia-arc" startOffset="50%">{esc(name)}</textPath></text>')
    o.append(f'<text {DMS} font-size="{sz}" fill="{INK}" text-anchor="middle"><textPath href="#philadelphia-arc" startOffset="50%">{esc(name)}</textPath></text>')
    csz = fit_size(coords, MONO, 16, 360, 2)
    o.append(f'<rect x="{cx - measure(coords, MONO, csz, 2) / 2 - 8:.1f}" y="528" width="{measure(coords, MONO, csz, 2) + 16:.1f}" height="22" fill="{PAPER}"/>')
    o.append(coord_line(p, cx, 545, coords, 16, 2, 22, 10, dots=True))
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- AUSTIN
def bat_swarm(p, spine, n, w0, w1, size=(1.6, 3.4), op=1.0):
    """Mexican free-tailed bats streaming out along a curving ribbon: tiny ink 'm' wings, packed at the core of
    the column and thinning to stragglers at its edges."""
    rnd = p.rnd
    c = smooth(spine, 10)
    L = len(c)
    d = []
    for _ in range(n):
        i = min(L - 2, int(L * rnd.random() ** 0.85))
        t = i / (L - 1)
        (x0, y0), (x1, y1) = c[i], c[i + 1]
        tx, ty = x1 - x0, y1 - y0
        ln = math.hypot(tx, ty) or 1
        nx, ny = -ty / ln, tx / ln
        wdt = w0 + (w1 - w0) * t
        off = rnd.gauss(0, 0.33) * wdt
        f = rnd.random()
        x = x0 + tx * f + nx * off + rnd.uniform(-2, 2)
        y = y0 + ty * f + ny * off + rnd.uniform(-2, 2)
        s = rnd.uniform(*size) * (0.7 + 0.5 * t)
        flap = rnd.uniform(-0.6, 0.9)
        d.append(f"M{x - s:.1f} {y - s * flap:.1f}Q{x - s * 0.5:.1f} {y - s * 0.2:.1f} {x:.1f} {y + s * 0.25:.1f}"
                 f"Q{x + s * 0.5:.1f} {y - s * 0.2:.1f} {x + s:.1f} {y - s * flap:.1f}")
    return f'<path d="{"".join(d)}" fill="none" stroke="{INK}" stroke-width="1.15" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"/>'


def tower_block(p, x0, x1, top, base, cols, rows, shade=0.0, lit=0.15, w=1.6, crown=None):
    """A downtown tower at dusk: hatched glass, a mullion grid, a few lit windows left as paper."""
    rnd = p.rnd
    out = [p.shape(rect(x0, top, x1 - x0, base - top), w)]
    cw = (x1 - x0) / cols
    rh = (base - top) / rows
    g = []
    for c in range(1, cols):
        g.append(f"M{x0 + c * cw:.1f} {top:.1f}V{base:.1f}")
    for r in range(1, rows):
        g.append(f"M{x0:.1f} {top + r * rh:.1f}H{x1:.1f}")
    out.append(p.hatch(rect(x0, top, x1 - x0, base - top), 90, 2.2 if shade > 0.5 else 3.0, 1.0, 0.75))
    out.append(f'<path d="{"".join(g)}" stroke="{INK}" stroke-width="0.9"/>')
    lits = []
    for c in range(cols):
        for r in range(rows):
            if rnd.random() < lit:
                lits.append(f'<rect x="{x0 + c * cw + 0.8:.1f}" y="{top + r * rh + 0.8:.1f}" width="{cw - 1.6:.1f}" height="{rh - 1.6:.1f}"/>')
    out.append(f'<g fill="{PAPER}">' + "".join(lits) + "</g>")
    if shade:
        sx = x0 + (x1 - x0) * (1 - shade * 0.5)
        out.append(p.hatch(rect(sx, top, x1 - sx, base - top), 60, 2.6, 1.0, 0.8))
    return "".join(out)


@design("austin", "Austin", "30.2672° N · 97.7431° W")
def austin(name, coords):
    """Dusk on Lady Bird Lake: the Congress Avenue Bridge, the downtown towers and the Capitol at the end of the
    avenue, and a ribbon of bats pouring out from under the bridge, with kayaks and a tour boat watching."""
    p = Pen("austin", 83)
    rnd = p.rnd
    GLOW = "#E9A25F"
    o = [p.paper(15)]
    WL = 382                      # waterline
    # --- dusk sky: an orange glow low over the city (the accent), ink hatching deepening upward
    g = p.uid("glow")
    p.defs.append(f'<linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GLOW}" stop-opacity="0"/>'
                  f'<stop offset="0.45" stop-color="{GLOW}" stop-opacity="0.18"/><stop offset="1" stop-color="{GLOW}" stop-opacity="0.75"/></linearGradient>')
    o.append(f'<rect x="-10" y="120" width="620" height="{WL - 120}" fill="url(#{g})"/>')
    o.append(p.hatch([(-10, -10), (610, -10), (610, 260), (-10, 260)], -4, 3.4, 1.0, 0.8, dash=(16, 40),
                     keep=lambda x, y: max(0, 1 - y / 240) ** 1.2))
    o.append(p.hatch([(-10, -10), (610, -10), (610, 130), (-10, 130)], -4, 3.4, 1.0, 0.8, dash=(24, 10),
                     keep=lambda x, y: max(0, 1 - y / 120) ** 1.5))
    # a thin crescent moon and the first stars
    o.append(f'<path d="M478 92a18 18 0 1 0 14 -30a14 14 0 1 1 -14 30Z" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>')
    for sx, sy in ((88, 60), (148, 96), (560, 140), (402, 70), (240, 54)):
        o.append(f'<path d="M{sx - 4} {sy}h8M{sx} {sy - 4}v8" stroke="{INK}" stroke-width="1.4"/>'
                 f'<circle cx="{sx}" cy="{sy}" r="2.2" fill="{PAPER}"/>')
    # --- the skyline, back to front
    B = WL - 50                  # tower bases hidden behind the bridge and the trees
    # the Capitol dome at the end of Congress Avenue
    cx = 300
    o.append(p.shape(rect(cx - 36, B - 40, 72, 40), 1.6))
    o.append(p.windows(cx - 30, B - 34, 6, 2, 5, 9, 5.6, 6, w=1.0, dark=0.7, sill=False))
    o.append(p.shape(rect(cx - 22, B - 64, 44, 24), 1.6))
    for k in range(8):
        o.append(p.seg(cx - 19 + k * 5.4, B - 62, cx - 19 + k * 5.4, B - 42, 1.1))
    dome = arc_pts(cx, B - 64, 22, 30, 180, 360, 16)
    o.append(p.shape(dome + [(cx + 22, B - 64)], 1.8))
    o.append(p.hatch(dome, 80, 2.4, 1.0, 0.85, keep=lambda x, y: max(0, (x - cx + 4) / 22)))
    o.append(p.shape(rect(cx - 5, B - 104, 10, 12), 1.4) + p.seg(cx, B - 104, cx, B - 116, 1.4)
             + f'<circle cx="{cx}" cy="{B - 118}" r="2" fill="{INK}"/>')
    # towers: (x0, x1, top, cols, rows, shade, crown)
    T = [(70, 112, 214, 6, 18, 0.4, None), (114, 150, 176, 5, 22, 0.6, "austonian"), (160, 200, 236, 5, 14, 0.3, None),
         (204, 252, 128, 6, 30, 0.5, "frost"), (348, 392, 190, 6, 20, 0.5, "independent"), (396, 436, 160, 5, 24, 0.6, "sail"),
         (440, 486, 222, 6, 14, 0.4, None), (488, 530, 196, 5, 18, 0.6, None)]
    for x0, x1, top, cols, rows, sh, crown in T:
        if crown == "independent":
            # the stacked, cantilevered blocks
            y = top
            k = 0
            blocks = []
            while y < B:
                hh = rnd.uniform(16, 24)
                dx = (6 if k % 3 == 1 else (-5 if k % 3 == 2 else 0))
                blocks.append((x0 + dx, x1 + dx, y, min(B, y + hh)))
                y += hh
                k += 1
            for bx0, bx1, by0, by1 in reversed(blocks):
                o.append(tower_block(p, bx0, bx1, by0, by1, cols, max(2, int((by1 - by0) / 7)), sh, 0.15, 1.5))
                o.append(p.hatch(rect(bx0, by1 - 3, bx1 - bx0, 3), 0, 1.4, 1.0, 0.9))
            continue
        o.append(tower_block(p, x0, x1, top, B, cols, rows, sh))
        mx = (x0 + x1) / 2
        if crown == "frost":
            # stepped, faceted crown rising to a needle
            o.append(p.shape([(x0, top), (x0 + 8, top - 24), (mx - 8, top - 30), (mx, top - 58), (mx + 8, top - 30), (x1 - 8, top - 24), (x1, top)], 1.8))
            o.append(p.hatch([(mx, top - 58), (mx + 8, top - 30), (x1 - 8, top - 24), (x1, top), (mx, top)], 70, 2.2, 1.0, 0.85))
            o.append(p.line([(mx, top - 58), (mx, top)], 1.2, 0.1) + p.line([(x0 + 8, top - 24), (mx, top - 6), (x1 - 8, top - 24)], 1.1, 0.1))
            o.append(p.seg(mx, top - 58, mx, top - 76, 1.4))
        elif crown == "austonian":
            o.append(p.shape(arc_pts(mx, top, (x1 - x0) / 2, 12, 180, 360, 10) + [(x1, top)], 1.6))
            o.append(p.seg(mx, top - 12, mx, top - 26, 1.3))
        elif crown == "sail":
            o.append(p.shape([(x0, top), (x0 + 4, top - 8), (x1, top - 34), (x1, top)], 1.6))
            o.append(p.hatch([(x0, top), (x0 + 4, top - 8), (x1, top - 34), (x1, top)], 60, 2.2, 1.0, 0.8))
        else:
            o.append(p.line([(x0 - 2, top), (x1 + 2, top)], 2.4, 0.1))
            o.append(p.shape(rect(mx - 6, top - 8, 12, 8), 1.3))
    # live oaks along the shore in front of the towers
    for x in range(-20, 640, 44):
        r = rnd.uniform(22, 30)
        o.append(p.foliage(x + rnd.uniform(-8, 8), B + 12, r, r * 0.6, w=1.3, shade=0.0, bump=5, inner=0.0, dark=True))
    o.append(p.solid([(-10, B + 16), (610, B + 16), (610, WL), (-10, WL)]))
    # --- Congress Avenue Bridge: concrete spans on piers, arches dark underneath, lamps along the rail
    deck_y = WL - 44
    o.append(p.shape([(-10, deck_y - 10), (610, deck_y - 10), (610, deck_y + 8), (-10, deck_y + 8)], 2.2))
    o.append(p.hatch([(-10, deck_y - 2), (610, deck_y - 2), (610, deck_y + 8), (-10, deck_y + 8)], 0, 2.0, 1.0, 0.7))
    rail = "".join(f"M{x:.1f} {deck_y - 10:.1f}v-8" for x in range(-8, 610, 7))
    o.append(f'<path d="{rail}" stroke="{INK}" stroke-width="1.1"/>' + p.line([(-10, deck_y - 18), (610, deck_y - 18)], 1.8, 0.2))
    for lx in range(20, 600, 64):
        o.append(p.seg(lx, deck_y - 18, lx, deck_y - 38, 1.6, 0.1) + p.seg(lx, deck_y - 38, lx + 7, deck_y - 38, 1.6, 0.1)
                 + f'<circle cx="{lx + 7}" cy="{deck_y - 36}" r="2.2" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>')
    span = 100
    for k in range(-1, 7):
        a = k * span + 10
        b = a + span
        arch = [(a + 8 + (span - 16) * t, deck_y + 32 - 20 * math.sin(math.pi * t) ** 0.5) for t in [j / 16 for j in range(17)]]
        o.append(p.solid(arch + [(b - 8, WL), (a + 8, WL)], INK))
        o.append(p.line(arch, 1.4, 0.2, color=PAPER, op=0.6))
        # the pier between arches
        pier = [(b - 8, deck_y + 8), (b + 8, deck_y + 8), (b + 10, WL), (b - 10, WL)]
        o.append(p.shape(pier, 1.8))
        o.append(p.hatch([(b + 1, deck_y + 8), (b + 8, deck_y + 8), (b + 10, WL), (b + 1, WL)], 90, 2.0, 1.0, 0.8))
    # cars on the bridge, headlights on
    for x, f in ((96, 1), (232, -1), (414, 1), (520, -1)):
        o.append(p.shape([(x - 14, deck_y - 10), (x - 13, deck_y - 16), (x - 7, deck_y - 22), (x + 7, deck_y - 22), (x + 12, deck_y - 16), (x + 14, deck_y - 10)], 1.4, fill=INK))
        o.append(f'<path d="M{x + 14 * f:.1f} {deck_y - 14:.1f}l{18 * f} -3v6Z" fill="{PAPER}" opacity="0.8"/>')
    # --- the bats: a dark ribbon pouring from beneath the bridge and swinging up across the sky
    o.append(bat_swarm(p, [(250, 352), (236, 300), (238, 250), (270, 200), (330, 160), (410, 136), (480, 128), (560, 112), (630, 92)],
                       2300, 16, 70, (1.5, 3.2)))
    o.append(bat_swarm(p, [(330, 356), (334, 312), (350, 276), (382, 240)], 420, 9, 34, (1.3, 2.6)))
    # --- the lake: reflections of the glow, the arches and the lamps; ripples; kayaks and a tour boat
    W0, W1 = WL, 470
    o.append(p.reflect(-10, 610, WL + 2, 26, density=0.85, sp=2.6, w=1.3, taper=0))
    for lx in range(20, 600, 64):
        o.append(p.reflect(lx + 4, lx + 10, WL + 4, 50, density=1, sp=3.5, w=1.4, taper=0))
    o.append(p.ripples(-10, 610, WL + 26, W1, 170, hy=WL, lmin=6, lmax=30, wmin=1.0, wmax=1.8))
    # tour boat under the bridge watching the bats
    bx, by = 150, 418
    o.append(p.shape([(bx - 54, by - 8), (bx + 52, by - 8), (bx + 60, by - 14), (bx + 46, by + 4), (bx - 48, by + 4)], 1.8))
    o.append(p.hatch([(bx - 54, by - 8), (bx + 52, by - 8), (bx + 46, by + 4), (bx - 48, by + 4)], 0, 2.0, 1.0, 0.8))
    o.append(p.shape(rect(bx - 44, by - 26, 80, 4), 1.5) + "".join(p.seg(x, by - 22, x, by - 8, 1.3) for x in (bx - 42, bx - 14, bx + 14, bx + 34)))
    for k in range(9):
        x = bx - 38 + k * 9
        o.append(p.person(x, by - 8, 13, k % 2, flip=k % 3 == 0))
    o.append(f'<path d="M{bx - 60} {by + 6}q-20 2 -50 -2M{bx - 56} {by + 9}q-26 6 -60 4" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    # kayakers
    for kx, ky, s in ((420, 446, 1.0), (480, 430, 0.8)):
        o.append(p.solid([(kx - 26 * s, ky), (kx - 10 * s, ky - 4 * s), (kx + 14 * s, ky - 4 * s), (kx + 28 * s, ky), (kx + 10 * s, ky + 3 * s), (kx - 10 * s, ky + 3 * s)]))
        o.append(p.person(kx, ky - 3 * s, 15 * s, 1))
        o.append(p.seg(kx - 14 * s, ky + 4 * s, kx + 14 * s, ky - 20 * s, 1.6) + p.solid([(kx - 14 * s, ky + 4 * s), (kx - 18 * s, ky + 10 * s), (kx - 11 * s, ky + 7 * s)]))
        o.append(f'<path d="M{kx - 30 * s} {ky + 2}q-12 2 -24 0" stroke="{INK}" stroke-width="1.2" fill="none"/>')
    # a paddleboarder
    o.append(p.solid([(318, 456), (360, 456), (356, 460), (322, 460)]) + p.person(338, 456, 26, 0) + p.seg(346, 434, 352, 462, 1.6))
    # --- the title in paper on a band of ink at the bottom
    o.append(p.solid([(-10, W1), (610, W1), (610, 610), (-10, 610)]))
    o.append(p.line([(-10, W1 + 1), (610, W1 + 1)], 2.4, 1.0))
    o.append(p.ripples(-10, 610, W1 - 8, W1 - 2, 24, lmin=8, lmax=20, wmin=1.2, wmax=1.4))
    sz = name_size(name, 360, 62, ls=4)
    o.append(title_text(300, 527, name, sz, fill=PAPER, ls=4))
    csz = fit_size(coords, MONO, 16, 360, 2.4)
    o.append(title_text(300, 552, coords, csz, MONO, fill=PAPER, ls=2.4))
    tw = measure(coords, MONO, csz, 2.4)
    for s_ in (-1, 1):
        x = 300 + s_ * (tw / 2 + 14)
        o.append(f'<path d="M{x:.1f} 546.5h{s_ * 30}" stroke="{PAPER}" stroke-width="1.6"/>')
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- DENVER
def ridge_line(rnd, x0, x1, peaks, rough=6.0, step=4.0):
    """A mountain ridge through (x, y) peak/saddle anchors, roughened by recursive midpoint displacement."""
    pts = [(x0, peaks[0][1])] + list(peaks) + [(x1, peaks[-1][1])]
    out = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        seg_ = [(ax, ay), (bx, by)]
        amp = rough
        while True:
            nxt = [seg_[0]]
            for p0, p1 in zip(seg_, seg_[1:]):
                m = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + rnd.uniform(-amp, amp))
                nxt += [m, p1]
            seg_ = nxt
            amp *= 0.55
            if (seg_[1][0] - seg_[0][0]) < step:
                break
        out += seg_[:-1]
    out.append(pts[-1])
    return out


def mountain(p, ridge, base, light=-1, shade_w=1.0, density=1.0, snow=0.0, lw=1.8, op=1.0, fill=PAPER, mult=1):
    """A range in pen: the ridge contour, fall-line strokes on the slopes turned from the light, sparse short
    strokes on the lit slopes, and paper snowfields in the high gullies."""
    rnd = p.rnd
    poly = ridge + [(ridge[-1][0], base), (ridge[0][0], base)]
    out = [p.solid(poly, fill)]
    d = []
    top = min(y for _, y in ridge)
    for i in range(1, len(ridge) - 1):
        (xa, ya), (xb, yb) = ridge[i - 1], ridge[i + 1]
        slope = (yb - ya) / ((xb - xa) or 1)          # +: falling to the right
        x, y = ridge[i]
        shaded = (slope > 0.08) if light < 0 else (slope < -0.08)
        h = base - y
        if shaded and rnd.random() < 0.9 * density:
            for _ in range(mult):
                L = h * rnd.uniform(0.25, 0.85)
                dx = (0.32 if light < 0 else -0.32) * L
                # leave snow paper near the top
                y0 = y + (rnd.uniform(4, 18) if snow and (y - top) < (base - top) * snow else rnd.uniform(0.5, 2))
                xo = rnd.uniform(-1.5, 1.5)
                d.append(f"M{x + xo + (y0 - y) * dx / L:.1f} {y0:.1f}l{dx:.1f} {L:.1f}")
        elif rnd.random() < 0.25 * density:
            L = h * rnd.uniform(0.05, 0.22)
            y0 = y + rnd.uniform(6, 24)
            d.append(f"M{x:.1f} {y0:.1f}l{-0.2 * L * light:.1f} {L:.1f}")
    cid = p.uid("mt")
    p.defs.append(f'<clipPath id="{cid}"><polygon points="{P(poly)}"/></clipPath>')
    out.append(f'<path d="{"".join(d)}" stroke="{INK}" stroke-width="{shade_w}" stroke-linecap="round" opacity="{0.85 * op:.2f}" clip-path="url(#{cid})"/>')
    out.append(p.line(ridge, lw, 0.2, op=op))
    return "".join(out)


def spruce(p, x, base, h, w):
    """Colorado blue spruce: stacked skirts of drooping branches, each tier a scalloped arc with its underside
    inked dark, narrowing to a spire; the shadow side (right) carries denser hatching."""
    rnd = p.rnd
    tiers = max(7, int(h / 22))
    out = []
    for i in range(tiers, -1, -1):
        t = i / tiers
        y = base - h * 0.08 - (h * 0.9) * (1 - t)
        half = w / 2 * (0.1 + 0.9 * t) * rnd.uniform(0.9, 1.08)
        th = h / tiers * 1.6
        # skirt: from the trunk, an arching top line drooping to ragged tips
        top = [(x, y - th)]
        n = 8
        Lp, Rp = [], []
        for k in range(1, n + 1):
            f = k / n
            for sgn, lst in ((-1, Lp), (1, Rp)):
                lst.append((x + sgn * half * f, y - th + th * (f ** 1.6) + rnd.uniform(-1.5, 1.5)))
        tipsL, tipsR = [], []
        for k in range(n, -1, -1):
            f = k / n
            tipsR.append((x + half * f, y + rnd.uniform(-2, 3) - 3 * math.sin(f * 9 + i)))
        for k in range(0, n + 1):
            f = k / n
            tipsL.append((x - half * f, y + rnd.uniform(-2, 3) - 3 * math.sin(f * 7 + i)))
        poly = [top[0]] + Rp + tipsR + tipsL[::-1][::-1][::-1] + Lp[::-1]
        poly = [top[0]] + Rp + tipsR[1:] + [(x - half * k / n, y + rnd.uniform(-2, 3)) for k in range(0, n + 1)][1:] + Lp[::-1]
        out.append(p.shape(poly, 1.4))
        out.append(p.hatch(poly, 75, 2.2, 1.0, 0.9, keep=lambda xx, yy, x=x, y=y, th=th: (0.95 if xx > x else 0.35) * max(0, min(1, (yy - (y - th * 0.6)) / (th * 0.6)))))
        out.append(p.hatch(poly, 115, 2.8, 1.0, 0.8, keep=lambda xx, yy, x=x, half=half: max(0, (xx - x) / half)))
        ticks = "".join(f"M{x + sg * half * f:.1f} {y - 1:.1f}l{sg * 2:.1f} {rnd.uniform(3, 6):.1f}" for f in [k / 7 for k in range(1, 8)] for sg in (-1, 1))
        out.append(f'<path d="{ticks}" stroke="{INK}" stroke-width="1.1"/>')
    out.append(p.seg(x, base - h - 6, x, base - h * 0.9, 1.6))
    out.append(p.solid(rect(x - 4, base - h * 0.08, 8, h * 0.08 + 4)))
    return "".join(out)


@design("denver", "Denver", "39.7392° N · 104.9903° W")
def denver(name, coords):
    """The Front Range rising behind downtown, seen across Ferril Lake in City Park on a clear morning: snow in
    the gullies, the towers catching the sun, the fountain playing, pedal boats and geese, a blue spruce."""
    p = Pen("denver", 97)
    rnd = p.rnd
    o = [p.paper(17)]
    WL = 386
    # --- sky: clean, a few thin strokes near the peaks; title at the top
    o.append(p.hatch([(0, 150), (600, 150), (600, 300), (0, 300)], -2, 6.5, 1.0, 0.35, dash=(10, 50),
                     keep=lambda x, y: max(0, (y - 160) / 140)))
    o.append(p.birds([(120, 168), (136, 160, 0.7), (466, 152, 0.8)], 7))
    # --- the far range (lighter), the main range with snow, and the foothills
    far = ridge_line(rnd, -10, 610, [(30, 268), (120, 246), (190, 262), (270, 236), (330, 256), (420, 238), (520, 258), (590, 250)], 5)
    o.append(mountain(p, far, WL - 40, -1, 1.0, 0.7, 0.0, 1.3, 0.55))
    main = ridge_line(rnd, -10, 610, [(10, 282), (70, 240), (110, 254), (160, 190), (196, 206), (222, 178), (262, 214), (320, 236),
                                      (380, 226), (430, 198), (466, 186), (500, 214), (560, 238), (600, 232)], 8)
    o.append(mountain(p, main, WL - 30, -1, 1.1, 2.2, 0.4, 2.4, mult=3))
    o.append(p.hatch(main + [(610, WL - 30), (-10, WL - 30)], 8, 7.0, 1.0, 0.35, dash=(6, 22), keep=lambda x, y: max(0, (y - 230) / 120)))
    # snowfields: paper tongues outlined down the gullies under the highest peaks
    for sx, sy, L in ((222, 182, 44), (212, 194, 32), (162, 196, 36), (172, 206, 24), (466, 190, 40), (458, 202, 28), (432, 204, 22), (72, 246, 20), (236, 196, 26)):
        tongue = [(sx - 4, sy), (sx + 4, sy), (sx + 7, sy + L * 0.4), (sx + 3, sy + L), (sx - 1, sy + L * 0.6), (sx - 6, sy + L * 0.3)]
        o.append(p.solid(tongue, PAPER) + p.line(tongue[1:4], 1.1, 0.3))
    foot = ridge_line(rnd, -10, 610, [(0, 318), (90, 300), (170, 318), (250, 306), (330, 322), (420, 308), (510, 320), (600, 306)], 4, 5)
    fpoly = foot + [(610, WL), (-10, WL)]
    o.append(p.solid(fpoly, PAPER))
    o.append(p.stipple(fpoly, 700, r=(0.6, 1.1), keep=lambda x, y: 0.5 + 0.5 * math.sin(x / 40)))
    o.append(p.hatch(fpoly, 75, 3.2, 1.0, 0.55))
    o.append(p.line(foot, 1.6, 0.2))
    # --- downtown: towers catching the morning sun from the left, shadow sides hatched
    B = WL - 18
    towers = [(232, 254, 316, "flat"), (256, 280, 282, "slant"), (282, 308, 262, "flat"), (310, 338, 258, "vault"),
              (340, 360, 300, "flat"), (362, 384, 278, "notch"), (386, 404, 312, "flat"), (406, 424, 324, "flat")]
    for x0, x1, top, kind in sorted(towers, key=lambda t: -t[2]):
        pass
    for x0, x1, top, kind in towers:
        body = rect(x0, top, x1 - x0, B - top)
        o.append(p.shape(body, 1.7))
        cols = max(3, int((x1 - x0) / 6))
        g = "".join(f"M{x0 + (x1 - x0) * c / cols:.1f} {top + 4:.1f}V{B:.1f}" for c in range(1, cols))
        rows = int((B - top) / 6)
        g += "".join(f"M{x0:.1f} {top + 4 + r * 6:.1f}H{x1:.1f}" for r in range(1, rows))
        o.append(f'<path d="{g}" stroke="{INK}" stroke-width="0.8" opacity="0.75"/>')
        o.append(p.hatch([(x0 + (x1 - x0) * 0.62, top), (x1, top), (x1, B), (x0 + (x1 - x0) * 0.62, B)], 90, 1.9, 1.0, 0.9))
        mx = (x0 + x1) / 2
        if kind == "vault":        # the rounded crown of the Wells Fargo Center
            v = arc_pts(mx, top, (x1 - x0) / 2, 26, 180, 360, 16)
            o.append(p.shape(v + [(x1, top)], 1.8))
            o.append(f'<path d="{"".join(f"M{mx + (x1 - x0) / 2 * f:.1f} {top:.1f}V{top - 26 * math.sqrt(max(0, 1 - f * f)):.1f}" for f in (-0.7, -0.35, 0, 0.35, 0.7))}" stroke="{INK}" stroke-width="1"/>')
            o.append(p.hatch(v, 90, 2.0, 1.0, 0.8, keep=lambda x, y: max(0, (x - mx) / 14)))
        elif kind == "slant":
            o.append(p.shape([(x0, top), (x1, top - 18), (x1, top)], 1.6) + p.hatch([(x0, top), (x1, top - 18), (x1, top)], 90, 2.0, 1.0, 0.8))
            o.append(p.seg(x1 - 4, top - 18, x1 - 4, top - 32, 1.3))
        elif kind == "notch":
            o.append(p.shape([(x0, top), (x0, top - 10), (mx - 4, top - 10), (mx - 4, top - 18), (x1, top - 18), (x1, top)], 1.6))
        else:
            o.append(p.line([(x0 - 1.5, top), (x1 + 1.5, top)], 2.4, 0.1))
    # lower blocks and park trees along the far shore
    for x0, w, h in ((150, 50, 26), (196, 34, 38), (426, 44, 30), (468, 60, 20)):
        o.append(p.shape(rect(x0, B - h, w, h), 1.4) + p.windows(x0 + 4, B - h + 6, int((w - 4) / 8), int((h - 8) / 9), 4, 5, 4, 4, w=0.9, dark=0.7, sill=False))
    xs = -10
    while xs < 640:
        r = rnd.uniform(14, 30)
        o.append(p.lobe(xs, WL - 8 - r * 0.6 - rnd.uniform(0, 4), r, r * rnd.uniform(0.55, 0.75), light=(-1, -0.4), w=1.3, dense=1.4))
        xs += r * rnd.uniform(1.1, 1.6)
    o.append(p.line([(-10, WL), (610, WL)], 2.0, 0.4))
    # --- Ferril Lake: reflections, the fountain, pedal boats, geese
    W1 = 478
    o.append(p.reflect(170, 430, WL + 3, 60, density=0.7, sp=3.0, w=1.2, taper=0.2))
    o.append(p.reflect(-10, 610, WL + 2, 14, density=0.8, sp=2.6, w=1.2, taper=0.0))
    o.append(p.ripples(-10, 610, WL + 14, W1, 150, hy=WL, lmin=6, lmax=28, wmin=1.0, wmax=1.7))
    fx, fy = 470, 420
    jets = []
    for k in range(-5, 6):
        jets.append(f"M{fx + k * 1.4:.1f} {fy:.1f}q{k * 4:.1f} -50 {k * 9:.1f} -20")
    o.append(f'<path d="{"".join(jets)}" fill="none" stroke="{INK}" stroke-width="1.1" stroke-dasharray="4 3"/>')
    o.append(p.seg(fx, fy, fx, fy - 64, 1.6, 0.2) + f'<path d="M{fx - 10} {fy - 60}q10 -14 20 0" fill="none" stroke="{INK}" stroke-width="1.2" stroke-dasharray="3 3"/>')
    o.append(p.shape(arc_pts(fx, fy + 1, 24, 4, 0, 360, 16), 1.4))
    for bx, by, f in ((112, 428, 1), (224, 446, -1)):
        o.append(p.shape([(bx - 16, by), (bx + 16, by), (bx + 12, by + 7), (bx - 12, by + 7)], 1.6))
        o.append(p.shape([(bx - 12, by), (bx - 10, by - 12), (bx + 10, by - 12), (bx + 12, by)], 1.4))
        o.append(p.hatch([(bx - 12, by), (bx - 10, by - 12), (bx + 10, by - 12), (bx + 12, by)], 0, 2.0, 1.0, 0.8))
        o.append(p.person(bx - 4, by + 1, 13, 1) + p.person(bx + 5, by + 1, 13, 1, dress=True))
        o.append(f'<path d="M{bx - 18} {by + 7}q-10 2 -22 0" stroke="{INK}" stroke-width="1.2" fill="none"/>')
    for gx, gy, f in ((330, 458, 1), (352, 466, 1), (300, 470, -1)):
        o.append(f'<path d="M{gx} {gy}q{6 * f} 5 {16 * f} 1l{2 * f} -4q{-3 * f} -6 {1 * f} -14l{3 * f} -1l{-1 * f} 2q{-2 * f} 6 {1 * f} 12Z" fill="{PAPER}" stroke="{INK}" stroke-width="1.3"/>'
                 f'<path d="M{gx + 13 * f} {gy - 13}l{1 * f} 4" stroke="{INK}" stroke-width="3"/>'
                 f'<path d="M{gx - 3} {gy + 4}q10 3 22 0" stroke="{INK}" stroke-width="1" fill="none"/>')
    # --- the near bank: grass, cattails, a bench with two people, the spruce
    bank = smooth([(-10, W1 + 6), (120, W1 - 2), (260, W1 + 8), (420, W1 + 2), (610, W1 - 4)], 6)
    o.append(p.solid(bank + [(610, 610), (-10, 610)], PAPER))
    o.append(p.line(bank, 2.2, 0.3))
    o.append(p.grass(-10, 610, 600, 120, (5, 14), 1.2))
    o.append(p.grass(-10, 610, 560, 80, (4, 10), 1.1))
    o.append(p.grass(-10, 610, W1 + 18, 70, (3, 8), 1.1))
    for cx_ in (20, 34, 46, 58, 74):
        h = rnd.uniform(46, 70)
        o.append(p.line([(cx_, W1 + 14), (cx_ + 2, W1 + 14 - h)], 1.4, 0.3))
        o.append(f'<rect x="{cx_ - 1.6:.1f}" y="{W1 + 14 - h * 0.86:.1f}" width="4.4" height="{h * 0.22:.1f}" rx="2" fill="{INK}"/>')
        o.append(f'<path d="M{cx_ + 1} {W1 + 10}q{rnd.uniform(-14, 14):.1f} {-h * 0.5:.1f} {rnd.uniform(-18, 18):.1f} {-h * 0.8:.1f}" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    bx = 170
    o.append(p.line([(bx - 26, 520), (bx + 26, 520)], 2.4, 0.2) + p.line([(bx - 26, 506), (bx + 26, 506)], 1.6, 0.2) + p.line([(bx - 26, 500), (bx + 26, 500)], 1.6, 0.2))
    o.append(p.seg(bx - 22, 500, bx - 22, 532, 1.8) + p.seg(bx + 22, 500, bx + 22, 532, 1.8))
    o.append(p.person(bx - 8, 520, 30, 1) + p.person(bx + 8, 520, 28, 1, dress=True))
    o.append(p.lamp(250, 540, 84, w=1.8))
    o.append(p.person(330, 548, 40, 0, flip=True) + p.person(346, 549, 38, 1, flip=True, dress=True) + p.person(360, 550, 24, 0, flip=True))
    o.append(f'<path d="M314 548l2 -9q-2 -5 4 -6h11q3 0 5 -3l2 -5l3 2l0 5q3 2 1 5l-3 0l-3 5l1 6h-2l-2 -5h-9l-2 5h-2l0 -5q-3 0 -5 5Z" fill="{INK}"/>')
    o.append(spruce(p, 538, 604, 300, 150))
    # --- title at the top
    sz = name_size(name, 400, 74, ls=2)
    o.append(title_text(300, 110, name, sz, ls=2))
    o.append(coord_line(p, 300, 142, coords, 17, 2.6, 34, 12, dots=True))
    o.append(p.border(30, 7, 2.6, 1.2))
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- LOS ANGELES
def tall_palm(p, x, base, h, lean=0.0, r=34, w0=9, w1=6, skirt=True):
    """Mexican fan palm: a very tall, thin, slightly curving trunk with ring scars, a shaggy skirt of dead
    fronds under a small round crown."""
    top = (x + lean * h, base - h)
    ctrl = [(x, base), (x + lean * h * 0.2, base - h * 0.4), (x + lean * h * 0.6, base - h * 0.75), top]
    c = smooth(ctrl, 10)
    L, R = offset(c, w0, w1)
    out = [p.shape(L + R[::-1], 1.6)]
    rings = []
    for i in range(2, len(c) - 2, 2):
        a, b = L[i], R[i]
        rings.append(f"M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1] + 0.8:.1f}")
    out.append(f'<path d="{"".join(rings)}" stroke="{INK}" stroke-width="1"/>')
    out.append(p.hatch([lerp(l, rr, 0.55) for l, rr in zip(L, R)] + R[::-1], 90, 1.8, 1.0, 0.9))
    tx, ty = top
    if skirt:
        sk = [(tx - r * 0.32, ty), (tx + r * 0.32, ty), (tx + r * 0.24, ty + r * 0.9), (tx + r * 0.08, ty + r * 1.05), (tx - r * 0.1, ty + r * 1.0), (tx - r * 0.26, ty + r * 0.85)]
        out.append(p.shape(sk, 1.3) + p.hatch(sk, 95, 1.8, 1.0, 0.95) + p.hatch(sk, 80, 2.6, 1.0, 0.7))
    out.append(fan_palm(p, tx, ty, r, n=12, back=0.35, halo=False, droop=1.2))
    return "".join(out)


@design("los-angeles", "Los Angeles", "34.0522° N · 118.2437° W")
def los_angeles(name, coords):
    """Griffith Observatory on its spur of Mount Hollywood in the late afternoon, the street grid of the basin
    running off to downtown's towers behind it, fan palms and a hiking trail in the chaparral below us;
    framed in an astrolabe ring."""
    p = Pen("los-angeles", 103)
    rnd = p.rnd
    CX, CY, RR = 300, 266, 214
    o = [p.paper(19)]
    circ = arc_pts(CX, CY, RR, RR, 0, 360, 90)
    art = []
    a = art.append
    H = 262                                     # horizon of the basin
    # --- sky: the low sun to the right, rays and a warm haze in strokes
    sx, sy = 420, 112
    a(f'<circle cx="{sx}" cy="{sy}" r="22" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>')
    a(p.hatch(arc_pts(sx, sy, 20, 20, 0, 360, 20), 0, 3.0, 1.0, 0.5, keep=lambda x, y: max(0, (y - sy) / 20)))
    rays = []
    for k in range(36):
        ang = 2 * math.pi * k / 36
        r0, r1 = 30, 30 + (18 if k % 2 else 34)
        rays.append(f"M{sx + r0 * math.cos(ang):.1f} {sy + r0 * math.sin(ang):.1f}L{sx + r1 * math.cos(ang):.1f} {sy + r1 * math.sin(ang):.1f}")
    a(f'<path d="{"".join(rays)}" stroke="{INK}" stroke-width="1.3" stroke-linecap="round"/>')
    a(p.hatch([(0, 60), (600, 60), (600, H), (0, H)], -2, 5.0, 1.0, 0.5, dash=(12, 40),
              keep=lambda x, y: max(0, (y - 180) / 140) * (0 if math.hypot(x - sx, y - sy) < 70 else 1)))
    a(p.birds([(170, 140), (186, 132, 0.7), (204, 146, 0.6)], 7))
    # --- the basin: distant hills, the street grid running to the horizon, downtown's towers
    hills = ridge_line(rnd, 60, 560, [(90, H - 6), (200, H - 12), (300, H - 4), (420, H - 10), (540, H - 5)], 3, 5)
    a(p.line(hills, 1.2, 0.2, op=0.6))
    VPX = 470
    g = []
    for k in range(-16, 26):
        xb = VPX + k * 46
        g.append(f"M{VPX + (xb - VPX) * 0.02:.1f} {H + 1:.1f}L{xb:.1f} {H + 140:.1f}")
    for k in range(1, 16):
        y = H + 1.5 * k ** 1.55
        g.append(f"M60 {y:.1f}H560")
    a(f'<path d="{"".join(g)}" stroke="{INK}" stroke-width="0.9" opacity="0.5"/>')
    a(p.stipple([(60, H + 1), (560, H + 1), (560, H + 100), (60, H + 100)], 420, r=(0.5, 1.0), keep=lambda x, y: 0.3 + 0.4 * (y - H) / 100))
    # downtown cluster
    dt = [(450, 464, 196, "crown"), (466, 480, 180, "sail"), (482, 494, 212, None), (438, 450, 222, None), (496, 508, 218, None),
          (426, 438, 236, None), (510, 520, 236, None), (414, 426, 246, None)]
    for x0, x1, top, kind in dt:
        a(p.shape(rect(x0, top, x1 - x0, H - top), 1.3))
        a(p.hatch(rect(x0 + (x1 - x0) * 0.5, top, (x1 - x0) * 0.5, H - top), 90, 1.6, 1.0, 0.9))
        a(f'<path d="{"".join(f"M{x0:.1f} {y:.1f}h{x1 - x0:.1f}" for y in range(int(top) + 4, int(H), 4))}" stroke="{INK}" stroke-width="0.7" opacity="0.7"/>')
        if kind == "crown":
            a(p.shape(arc_pts((x0 + x1) / 2, top, (x1 - x0) / 2, 7, 180, 360, 8) + [(x1, top)], 1.2))
        elif kind == "sail":
            a(p.shape([(x0, top), (x0 + 3, top - 4), (x1 - 2, top - 26), (x1, top)], 1.2) + p.seg(x1 - 2, top - 26, x1 - 2, top - 36, 1.1))
    # palms dotted across the basin
    for px_, py_, h in ((120, H + 60, 30), (148, H + 52, 24), (390, H + 40, 22), (414, H + 44, 26), (530, H + 70, 28), (96, H + 74, 32), (360, H + 30, 16)):
        a(p.seg(px_, py_, px_ + 1, py_ - h, 1.1) + f'<circle cx="{px_ + 1}" cy="{py_ - h}" r="3.4" fill="{INK}"/>')
    # --- Mount Hollywood's spur and the observatory
    spur = smooth([(40, 380), (100, 360), (170, 350), (240, 350), (360, 352), (430, 358), (500, 374), (570, 396)], 6)
    spoly = spur + [(570, 480), (40, 480)]
    a(p.solid(spoly, PAPER))
    a(p.line(spur, 2.0, 0.3))
    a(p.hatch(spoly, 68, 3.6, 1.0, 0.6, keep=lambda x, y: max(0, min(1, (y - 360) / 60))))
    B = 350                                    # terrace level
    # wings and corner towers with their telescope domes
    for tx in (178, 422):
        a(p.shape(rect(tx - 18, B - 46, 36, 46), 1.8))
        a(p.hatch(rect(tx + 4, B - 46, 14, 46), 90, 2.0, 1.0, 0.85))
        a(p.shape(rect(tx - 15, B - 56, 30, 10), 1.6))
        dm = arc_pts(tx, B - 56, 15, 15, 180, 360, 12)
        a(p.shape(dm + [(tx + 15, B - 56)], 1.8))
        a(p.hatch(dm, 75, 2.2, 1.0, 0.85, keep=lambda x, y, tx=tx: max(0, (x - tx + 3) / 14)))
        a(p.seg(tx - 2, B - 70, tx - 2, B - 57, 1.1) + p.seg(tx + 2, B - 70, tx + 2, B - 57, 1.1))
        a(p.seg(tx, B - 71, tx, B - 76, 1.4))
        for k in range(3):
            a(p.seg(tx - 10 + k * 10, B - 40, tx - 10 + k * 10, B - 8, 1.0, 0.1))
    for x0, x1 in ((196, 238), (362, 404)):
        a(p.shape(rect(x0, B - 30, x1 - x0, 30), 1.8))
        for x in range(int(x0) + 5, int(x1), 6):
            a(p.seg(x, B - 26, x, B - 4, 1.0, 0.1))
        a(p.line([(x0, B - 30), (x1, B - 30)], 2.2, 0.1))
    # central building, drum and the planetarium dome
    a(p.shape(rect(236, B - 54, 128, 54), 2.2))
    for x in range(244, 360, 8):
        a(p.seg(x, B - 48, x, B - 6, 1.1, 0.1))
    a(p.hatch(rect(320, B - 54, 44, 54), 90, 2.2, 1.0, 0.7))
    a(p.line([(232, B - 54), (368, B - 54)], 2.8, 0.1))
    a(p.shape(rect(256, B - 72, 88, 18), 2.0))
    a(p.hatch(rect(318, B - 72, 26, 18), 90, 2.0, 1.0, 0.8))
    dome = arc_pts(300, B - 72, 50, 50, 180, 360, 24)
    a(p.shape(dome + [(350, B - 72)], 2.4))
    a(p.hatch(dome, 100, 2.6, 1.05, 0.9, keep=lambda x, y: max(0, min(1, (x - 300 + 6) / 40))))
    a(p.stipple(dome, 60, r=(0.5, 0.9), keep=lambda x, y: max(0, 0.6 - abs(x - 288) / 40)))
    for f in (-0.66, -0.33, 0, 0.33, 0.66):
        rib = [(300 + 50 * f * math.cos(t), B - 72 - 50 * math.sin(t)) for t in [math.pi / 2 * j / 10 for j in range(11)]]
        a(p.line(rib, 1.1, 0.1))
    a(p.seg(300, B - 122, 300, B - 132, 1.6) + f'<circle cx="300" cy="{B - 134}" r="2.2" fill="{INK}"/>')
    # the Astronomers Monument on the lawn, figures round its base
    mxx, mb = 300, B + 26
    a(p.shape([(mxx - 7, mb - 6), (mxx - 4, mb - 62), (mxx, mb - 72), (mxx + 4, mb - 62), (mxx + 7, mb - 6)], 1.6))
    a(p.hatch([(mxx, mb - 72), (mxx + 4, mb - 62), (mxx + 7, mb - 6), (mxx, mb - 6)], 90, 1.8, 1.0, 0.9))
    a(p.shape(rect(mxx - 14, mb - 8, 28, 8), 1.4))
    for k in (-10, -4, 4, 10):
        a(p.solid([(mxx + k - 2, mb - 8), (mxx + k - 1.5, mb - 18), (mxx + k + 1.5, mb - 18), (mxx + k + 2, mb - 8)]) + f'<circle cx="{mxx + k}" cy="{mb - 20}" r="1.8" fill="{INK}"/>')
    # terrace wall, lawn, visitors
    a(p.line([(150, B), (450, B)], 2.4, 0.2))
    a(p.shape([(150, B), (450, B), (470, B + 34), (130, B + 34)], 1.6))
    a(p.line([(300, B + 2), (300, B + 34)], 1.0, 0.1) + p.line([(220, B + 2), (196, B + 34)], 1.0, 0.1) + p.line([(380, B + 2), (404, B + 34)], 1.0, 0.1))
    a(p.hatch([(150, B), (450, B), (470, B + 34), (130, B + 34)], 0, 3.2, 1.0, 0.35))
    for x, h, f in ((248, 12, False), (256, 11, True), (352, 12, True), (412, 11, False), (196, 12, False)):
        a(p.person(x, B + 22, h, int(x) % 2, flip=f))
    # --- our hillside: chaparral, a yucca in bloom, the trail with hikers, and two tall fan palms
    hill = smooth([(40, 420), (160, 404), (300, 420), (420, 410), (560, 426)], 6)
    hpoly = hill + [(560, 500), (40, 500)]
    a(p.solid(hpoly, PAPER))
    a(p.line(hill, 2.2, 0.3))
    bushes = sorted([(rnd.uniform(50, 550), rnd.uniform(420, 490)) for _ in range(30)], key=lambda b: b[1])
    for bx, by in bushes:
        r = rnd.uniform(10, 20)
        a(p.lobe(bx, by, r, r * 0.6, light=(1, -0.8), w=1.2, dense=1.8))
    trail = smooth([(330, 500), (300, 470), (330, 448), (400, 432), (470, 424)], 6)
    a(p.line(trail, 7, 0.2, color=PAPER) + p.line([(x, y - 3) for x, y in trail], 1.2, 0.2) + p.line([(x, y + 3) for x, y in trail], 1.2, 0.2))
    a(p.person(398, 431, 24, 0) + p.person(414, 428, 22, 1, dress=True) + p.seg(392, 422, 389, 432, 1.2))
    yx, yb = 230, 440                          # yucca: rosette of spikes, a tall bloom stalk
    sp = "".join(f"M{yx:.1f} {yb:.1f}l{18 * math.cos(math.radians(a_)):.1f} {-18 * math.sin(math.radians(a_)):.1f}" for a_ in range(15, 170, 12))
    a(f'<path d="{sp}" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/>')
    a(p.seg(yx, yb, yx + 2, yb - 70, 1.8) + p.stipple([(yx - 6, yb - 70), (yx + 8, yb - 70), (yx + 6, yb - 46), (yx - 4, yb - 46)], 40, r=(1.0, 1.8)))
    a(tall_palm(p, 104, 520, 360, lean=0.04, r=36))
    a(tall_palm(p, 150, 520, 300, lean=-0.03, r=30, w0=8, w1=5))
    k = 198 / RR
    o.append(f'<g transform="translate({300 - 300 * k:.2f} {252 - CY * k:.2f}) scale({k:.4f})">'
             + p.clip(f'<circle cx="{CX}" cy="{CY}" r="{RR}"/>', "".join(art)) + "</g>")
    CX, CY, RR = 300, 252, 198
    # --- the astrolabe ring: a heavy circle, a degree scale, a thin outer ring and four stars
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{RR}" fill="none" stroke="{INK}" stroke-width="3.2"/>')
    o.append(f'<circle cx="{CX}" cy="{CY}" r="{RR + 14}" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    tk = []
    for k in range(120):
        ang = 2 * math.pi * k / 120
        r1 = RR + (9 if k % 5 == 0 else 5)
        tk.append(f"M{CX + (RR + 1.5) * math.cos(ang):.1f} {CY + (RR + 1.5) * math.sin(ang):.1f}L{CX + r1 * math.cos(ang):.1f} {CY + r1 * math.sin(ang):.1f}")
    o.append(f'<path d="{"".join(tk)}" stroke="{INK}" stroke-width="1.1"/>')
    for ang in (45, 135, 225, 315):
        x, y = CX + (RR + 30) * math.cos(math.radians(ang)), CY + (RR + 30) * math.sin(math.radians(ang))
        o.append(f'<polygon points="{star_points(x, y, 9, 2.6, 4)}" fill="{INK}"/>')
    # --- title under the ring
    sz = name_size(name, 400, 54)
    o.append(title_text(300, 512, name, sz))
    o.append(coord_line(p, 300, 538, coords, 16, 2.0, 26, 10))
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- BARCELONA
def spindle(p, x, base, top, w, finial="ball", lw=1.6, shade=0.6):
    """A Sagrada Familia bell tower: a parabolic spindle with stacked louvre slots, ending in a pinnacle."""
    pts_l, pts_r = [], []
    n = 18
    for i in range(n + 1):
        t = i / n
        y = base - (base - top) * t
        half = w / 2 * (1 - t ** 2.2) ** 0.8 + 1.2
        pts_l.append((x - half, y))
        pts_r.append((x + half, y))
    body = pts_l + pts_r[::-1]
    out = [p.shape(body, lw)]
    # louvre slots: short slanted bars in vertical columns
    sl = []
    for i in range(2, n - 3):
        t = i / n
        y = base - (base - top) * t
        half = w / 2 * (1 - t ** 2.2) ** 0.8
        for f in (-0.45, 0.0, 0.45):
            xx = x + half * f * 1.4
            if abs(xx - x) < half * 0.8:
                sl.append(f"M{xx - 1.2:.1f} {y:.1f}l2.4 -2.2")
    out.append(f'<path d="{"".join(sl)}" stroke="{INK}" stroke-width="1.3" stroke-linecap="round"/>')
    out.append(p.hatch(body, 90, 2.0, 1.0, 0.85, keep=lambda xx, yy: max(0, (xx - x) / (w / 2) * shade * 1.6)))
    # the pinnacle: a stalk with a crown of balls and a cross-ish finial
    ty = top
    out.append(p.seg(x, ty, x, ty - 16, 1.8))
    if finial == "ball":
        for k in range(5):
            a = math.pi * (0.15 + 0.7 * k / 4)
            out.append(f'<circle cx="{x + 6 * math.cos(a):.1f}" cy="{ty - 8 - 6 * math.sin(a):.1f}" r="2.1" fill="{PAPER}" stroke="{INK}" stroke-width="1.1"/>')
        out.append(f'<path d="M{x - 4} {ty - 20}h8M{x} {ty - 24}v8" stroke="{INK}" stroke-width="1.6"/>')
    elif finial == "star":
        out.append(f'<polygon points="{star_points(x, ty - 22, 8, 3.2, 12)}" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>')
    elif finial == "cross":
        out.append(f'<path d="M{x - 9} {ty - 26}h18M{x} {ty - 36}v20M{x} {ty - 26}m-5 -5l10 10M{x} {ty - 26}m5 -5l-10 10" stroke="{INK}" stroke-width="2"/>'
                   f'<circle cx="{x}" cy="{ty - 26}" r="3.4" fill="{PAPER}" stroke="{INK}" stroke-width="1.4"/>')
    return "".join(out)


def roofscape_block(p, x0, x1, top, base, floors, lw=1.4, tone=0.5, hut=None, tank=None, rail=True):
    """An Eixample block seen from a neighbouring roof: facade with balconied windows and slatted shutters,
    a terrace on top with railing, stair hut, water tank and antenna."""
    rnd = p.rnd
    out = [p.shape(rect(x0, top, x1 - x0, base - top), lw)]
    if tone:
        out.append(p.hatch(rect(x0, top, x1 - x0, base - top), 80, 6.5 - tone * 3, 1.0, 0.45))
    fh = (base - top - 6) / floors
    cols = max(2, int((x1 - x0) / 20))
    cw = (x1 - x0) / cols
    for f in range(floors):
        y = top + 6 + f * fh
        for c in range(cols):
            wx = x0 + c * cw + cw * 0.3
            ww, wh = cw * 0.4, fh * 0.62
            if wh < 4:
                continue
            closed = rnd.random() < 0.72
            out.append(p.shape(rect(wx, y + fh * 0.18, ww, wh), 1.0, fill=PAPER if closed else INK))
            if closed:
                sl = "".join(f"M{wx + 0.6:.1f} {y + fh * 0.18 + k * 2.2:.1f}h{ww - 1.2:.1f}" for k in range(1, int(wh / 2.2)))
                out.append(f'<path d="{sl}" stroke="{INK}" stroke-width="0.8"/>')
            if f > 0 and fh > 9:
                out.append(p.line([(wx - 2, y + fh * 0.8), (wx + ww + 2, y + fh * 0.8)], 1.2, 0.1))
                out.append(f'<path d="{"".join(f"M{wx - 1 + k * 2.6:.1f} {y + fh * 0.8:.1f}v{-fh * 0.22:.1f}" for k in range(int((ww + 2) / 2.6) + 1))}" stroke="{INK}" stroke-width="0.7"/>')
    out.append(p.line([(x0 - 2, top), (x1 + 2, top)], lw + 0.8, 0.1))
    if rail:
        out.append(f'<path d="{"".join(f"M{x:.1f} {top:.1f}v-5" for x in range(int(x0) + 2, int(x1), 4))}" stroke="{INK}" stroke-width="0.9"/>'
                   + p.line([(x0, top - 5), (x1, top - 5)], 1.0, 0.1))
    if hut:
        hx, hw, hh = hut
        out.append(p.shape(rect(hx, top - hh, hw, hh), lw) + p.solid(rect(hx + hw * 0.55, top - hh * 0.75, hw * 0.3, hh * 0.75)))
        out.append(p.hatch(rect(hx, top - hh, hw * 0.4, hh), 90, 2.4, 1.0, 0.6))
    if tank:
        tx, tw = tank
        th = tw * 0.9
        out.append(p.shape(rect(tx, top - th - 3, tw, th), 1.2) + p.shape(arc_pts(tx + tw / 2, top - th - 3, tw / 2, 3, 0, 360, 10), 1.0)
                   + p.hatch(rect(tx + tw * 0.5, top - th - 3, tw * 0.5, th), 90, 1.8, 1.0, 0.85))
        out.append(p.seg(tx + tw + 6, top, tx + tw + 6, top - th - 22, 1.1) + p.seg(tx + tw, top - th - 16, tx + tw + 12, top - th - 16, 1.0)
                   + p.seg(tx + tw + 1, top - th - 10, tx + tw + 11, top - th - 10, 1.0))
    return "".join(out)


@design("barcelona", "Barcelona", "41.3874° N · 2.1686° E")
def barcelona(name, coords):
    """From a terrat in the Eixample: laundry, geraniums and a cat on our roof, the neighbouring blocks with
    their balconies and water tanks, and the spires of the Sagrada Familia rising over everything, cranes and
    all; the name on a marble street plaque set in the parapet."""
    p = Pen("barcelona", 109)
    rnd = p.rnd
    o = [p.paper(21)]
    # --- sky and the far hill of Tibidabo
    o.append(p.hatch([(0, 180), (600, 180), (600, 330), (0, 330)], -3, 6.0, 1.0, 0.4, dash=(12, 50),
                     keep=lambda x, y: max(0, (y - 200) / 140) * (0.3 if x > 320 else 1)))
    o.append(p.clouds(130, 120, 0.9) + p.clouds(250, 176, 0.55))
    tib = smooth([(-10, 262), (40, 250), (90, 236), (140, 232), (200, 246), (260, 262)], 6)
    o.append(p.line(tib, 1.3, 0.3, op=0.7))
    o.append(p.hatch(tib + [(260, 300), (-10, 300)], 70, 4.0, 1.0, 0.4))
    o.append(p.shape([(128, 232), (128, 210), (132, 206), (136, 210), (136, 232)], 1.2) + p.seg(132, 206, 132, 194, 1.2))
    o.append(p.birds([(232, 84), (246, 76, 0.7), (196, 210, 0.6), (300, 112, 0.6), (290, 230, 0.5), (90, 196, 0.6)], 7))
    # --- the Sagrada Familia: Nativity spindles, the evangelists, Mary and Jesus towers, Passion spindles
    base = 318
    o.append(p.shape([(318, base), (318, 262), (566, 262), (566, base)], 1.6))
    o.append(p.hatch([(318, 262), (566, 262), (566, base), (318, base)], 78, 3.2, 1.0, 0.5))
    # a tower crane beside the works
    o.append(f'<path d="M{548} {base}V{86}M{556} {base}V{86}" stroke="{INK}" stroke-width="1.4"/>'
             + "".join(f'<path d="M548 {y}L556 {y - 8}" stroke="{INK}" stroke-width="1"/>' for y in range(base, 94, -10)))
    o.append(p.line([(470, 86), (584, 86)], 1.6, 0.1) + p.line([(470, 92), (584, 92)], 1.0, 0.1)
             + "".join(p.seg(x, 86, x + 6, 92, 0.9, 0.0) for x in range(472, 582, 8)))
    o.append(p.line([(552, 64), (476, 86)], 1.0, 0.1) + p.line([(552, 64), (584, 86)], 1.0, 0.1) + p.seg(552, 64, 552, 86, 1.4))
    o.append(p.solid(rect(574, 88, 10, 10)) + p.seg(492, 92, 492, 140, 0.9) + p.shape(rect(487, 140, 10, 6), 1.0))
    for x, top, w in ((338, 176, 16), (356, 160, 17), (374, 158, 17), (392, 172, 16), (500, 168, 16), (518, 156, 17), (536, 158, 17), (552, 174, 16)):
        o.append(spindle(p, x, base - 40, top, w))
    for x, top, w, fin in ((416, 140, 22, "ball"), (478, 142, 22, "ball")):
        o.append(spindle(p, x, base - 50, top, w, fin))
    o.append(spindle(p, 432, base - 56, 126, 26, "star"))
    o.append(spindle(p, 452, base - 64, 98, 34, "cross", lw=2.0))
    # nave roof between the towers
    o.append(p.shape([(318, 280), (330, 264), (566, 264), (566, 280)], 1.4))
    o.append(p.hatch([(318, 280), (330, 264), (566, 264), (566, 280)], 0, 2.4, 1.0, 0.7))
    # --- the Eixample: rows of blocks stepping toward us
    rows = [
        (262, [(-10, 70, 270, 7, None, (30, 10)), (70, 150, 276, 7, (100, 16, 12), None), (150, 240, 268, 7, None, (200, 12)),
               (240, 330, 282, 7, (270, 18, 12), None)], 0.35),
        (300, [(-10, 96, 318, 6, (20, 18, 14), (60, 14)), (96, 210, 312, 6, None, (170, 14)), (210, 330, 322, 6, (300, 18, 14), None),
               (330, 450, 316, 6, (360, 18, 13), (420, 14)), (450, 610, 320, 6, None, (520, 14))], 0.45),
        (360, [(-10, 140, 372, 5, (90, 22, 16), None), (140, 300, 366, 5, None, (200, 16)), (300, 470, 376, 5, (330, 22, 16), (420, 16)),
               (470, 610, 368, 5, (540, 22, 16), None)], 0.55),
    ]
    for base_y, blocks, tone in rows:
        for x0, x1, top, fl, hut, tank in blocks:
            o.append(roofscape_block(p, x0, x1, top, 452, fl, 1.2 + tone, tone, hut, tank))
    # bits of life on the neighbouring roofs: a little laundry, potted plants, a parasol
    o.append(p.laundry(340, 360, 420, 362, 4, 4, 1.0))
    o.append(p.foliage(160, 360, 10, 7, w=1.1, shade=0.6, bump=3, inner=0.6) + p.foliage(176, 362, 8, 6, w=1.1, shade=0.6, bump=3, inner=0.5))
    o.append(p.shape([(250, 352), (268, 342), (286, 352)], 1.3) + p.hatch([(250, 352), (268, 342), (286, 352)], 60, 2.2, 1.0, 0.8) + p.seg(268, 352, 268, 366, 1.2))
    # --- our own terrace: parapet with clay balusters, pots of geraniums, a cat, and the washing line
    PY = 446
    o.append(p.shape([(-10, PY), (610, PY), (610, 610), (-10, 610)], 2.4))
    o.append(p.shape([(-10, PY - 8), (610, PY - 8), (610, PY + 4), (-10, PY + 4)], 2.2))
    o.append(p.hatch([(-10, PY + 4), (610, PY + 4), (610, PY + 12), (-10, PY + 12)], 0, 1.8, 1.0, 0.85))
    # stucco wall below: rough render in stipple, a crack, and a drainpipe
    o.append(p.stipple([(-10, PY + 12), (610, PY + 12), (610, 610), (-10, 610)], 320, r=(0.5, 1.0), op=0.7))
    for x, h, w in ((52, 34, 30), (500, 30, 28), (546, 40, 34)):
        pot = [(x - w / 2, PY - 8), (x - w / 2 - 3, PY - 8 - h * 0.15), (x + w / 2 + 3, PY - 8 - h * 0.15), (x + w / 2, PY - 8),
               (x + w * 0.38, PY - 8 + 0.1)]
        pot = [(x - w * 0.36, PY - 8), (x - w / 2, PY - 8 - h * 0.55), (x + w / 2, PY - 8 - h * 0.55), (x + w * 0.36, PY - 8)]
        o.append(p.shape(pot, 1.8) + p.hatch(pot, 90, 2.4, 1.0, 0.8, keep=lambda xx, yy, x=x: 1 if xx > x else 0.3))
        o.append(p.line([(x - w / 2 - 2, PY - 8 - h * 0.55), (x + w / 2 + 2, PY - 8 - h * 0.55)], 2.4, 0.1))
        o.append(p.foliage(x, PY - 8 - h * 0.55 - 14, w * 0.75, 16, w=1.3, shade=0.6, bump=4, inner=0.8))
        for k in range(5):
            fx, fy = x + rnd.uniform(-w * 0.5, w * 0.5), PY - 8 - h * 0.55 - rnd.uniform(16, 30)
            o.append("".join(f'<circle cx="{fx + 3 * math.cos(2 * math.pi * j / 5):.1f}" cy="{fy + 3 * math.sin(2 * math.pi * j / 5):.1f}" r="2" fill="{PAPER}" stroke="{INK}" stroke-width="1"/>' for j in range(5))
                     + f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="1.4" fill="{INK}"/>')
    # the cat on the coping, tail hanging
    cx_, cy_ = 432, PY - 8
    o.append(f'<path d="M{cx_ - 14} {cy_}q-2 -16 8 -22q-2 -8 2 -12l4 5h6l4 -5q3 6 0 12q8 6 4 22Z" fill="{INK}"/>'
             f'<path d="M{cx_ + 6} {cy_}q10 4 6 20q-2 8 4 12" fill="none" stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/>')
    # washing line strung from a post on the left to the stair hut on the right
    o.append(p.seg(30, PY - 8, 30, 300, 3.2) + p.seg(18, 304, 42, 304, 2.6))
    o.append(p.laundry(30, 306, 330, 290, 18, 6, 1.5, scale=2.4))
    # --- the marble street plaque on the parapet
    x0, x1, y0, y1 = 112, 488, 470, 552
    o.append(p.shape([(x0 + 4, y0 + 4), (x1 + 4, y0 + 4), (x1 + 4, y1 + 4), (x0 + 4, y1 + 4)], 0.1, fill=INK, op=0.25))
    o.append(p.shape(rect(x0, y0, x1 - x0, y1 - y0), 2.6))
    o.append(p.line(rect(x0 + 7, y0 + 7, x1 - x0 - 14, y1 - y0 - 14), 1.2, 0.2, closed=True))
    o.append(p.line([(x0 + 40, y0 + 18), (x0 + 120, y0 + 30)], 0.9, 0.3, op=0.35) + p.line([(x1 - 60, y1 - 16), (x1 - 20, y1 - 22)], 0.9, 0.3, op=0.35))
    for sx_, sy_ in ((x0 + 14, y0 + 14), (x1 - 14, y0 + 14), (x0 + 14, y1 - 14), (x1 - 14, y1 - 14)):
        o.append(f'<circle cx="{sx_}" cy="{sy_}" r="3" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/><path d="M{sx_ - 2} {sy_}h4" stroke="{INK}" stroke-width="1"/>')
    sz = name_size(name, x1 - x0 - 60, 48)
    o.append(title_text(300, 515, name, sz))
    o.append(title_text(300, 538, coords, fit_size(coords, MONO, 16, 330, 1.6), MONO, ls=1.6))
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- PRAGUE
def saint(p, x, base, h, kind=0, flip=False):
    """A blackened baroque statue on Charles Bridge: a robed figure in silhouette with a raised cross, palm
    or book, a halo of stars, and a few paper highlights picking out the drapery folds."""
    k = h / 100
    s = -1 if flip else 1
    X = lambda u: x + u * k * s
    Y = lambda v: base - v * k
    robe = [(X(-22), Y(0)), (X(-18), Y(30)), (X(-14), Y(62)), (X(-12), Y(74)), (X(-6), Y(82)), (X(6), Y(82)), (X(13), Y(72)),
            (X(16), Y(52)), (X(20), Y(24)), (X(26), Y(0))]
    out = [p.solid(robe)]
    out.append(f'<circle cx="{X(0):.1f}" cy="{Y(90):.1f}" r="{9 * k:.1f}" fill="{INK}"/>')
    folds = [f"M{X(-8):.1f} {Y(64):.1f}Q{X(-12):.1f} {Y(34):.1f} {X(-14):.1f} {Y(6):.1f}",
             f"M{X(4):.1f} {Y(60):.1f}Q{X(8):.1f} {Y(30):.1f} {X(6):.1f} {Y(4):.1f}",
             f"M{X(-2):.1f} {Y(40):.1f}Q{X(4):.1f} {Y(20):.1f} {X(-4):.1f} {Y(2):.1f}"]
    out.append(f'<path d="{"".join(folds)}" fill="none" stroke="{PAPER}" stroke-width="{max(0.8, 1.4 * k):.1f}" opacity="0.7"/>')
    if kind == 0:      # raised cross
        out.append(p.line([(X(10), Y(70)), (X(26), Y(96))], max(2.2, 6 * k), 0.1))
        out.append(p.line([(X(28), Y(80)), (X(30), Y(136))], max(1.6, 3.6 * k), 0.1) + p.line([(X(18), Y(122)), (X(40), Y(122))], max(1.6, 3.4 * k), 0.1))
    elif kind == 1:    # holding a palm frond and a book
        out.append(p.line([(X(12), Y(66)), (X(30), Y(84)), (X(38), Y(118))], max(1.6, 3 * k), 0.1))
        out.append(f'<path d="{"".join(f"M{X(30 + j * 1.2):.1f} {Y(88 + j * 5):.1f}l{8 * k * s:.1f} {-4 * k:.1f}M{X(30 + j * 1.2):.1f} {Y(88 + j * 5):.1f}l{-7 * k * s:.1f} {-5 * k:.1f}" for j in range(6))}" stroke="{INK}" stroke-width="{max(1, 1.6 * k):.1f}"/>')
        out.append(p.solid([(X(-14), Y(56)), (X(-30), Y(60)), (X(-30), Y(70)), (X(-14), Y(66))]))
    elif kind == 2:    # St John of Nepomuk: crucifix cradled, halo of five stars
        out.append(p.line([(X(-14), Y(40)), (X(18), Y(84))], max(1.8, 3.4 * k), 0.1) + p.line([(X(-6), Y(68)), (X(10), Y(56))], max(1.6, 3 * k), 0.1))
        for j in range(5):
            a = math.pi * (0.1 + 0.8 * j / 4)
            out.append(f'<polygon points="{star_points(X(0) + 17 * k * math.cos(a), Y(92) - 17 * k * math.sin(a), max(2.4, 4 * k), max(1, 1.6 * k))}" fill="{INK}"/>')
    else:              # a group: a kneeling figure before the saint
        out.append(p.solid([(X(-48), Y(0)), (X(-46), Y(22)), (X(-40), Y(40)), (X(-30), Y(44)), (X(-22), Y(36)), (X(-20), Y(0))]))
        out.append(f'<circle cx="{X(-34):.1f}" cy="{Y(50):.1f}" r="{7 * k:.1f}" fill="{INK}"/>')
        out.append(p.line([(X(-26), Y(38)), (X(-12), Y(56))], max(1.8, 4 * k), 0.1))
        out.append(p.line([(X(10), Y(74)), (X(24), Y(90))], max(1.8, 4.5 * k), 0.1))
    return "".join(out)


def bridge_lamp(p, x, base, h, w=1.6):
    """Charles Bridge lantern: slim iron post with a scrolled bracket and a six-sided lantern on top."""
    k = h / 80
    out = [p.seg(x, base, x, base - h * 0.82, max(1.3, 2.2 * k), 0.1)]
    out.append(p.shape([(x - 3 * k, base), (x - 2 * k, base - 8 * k), (x + 2 * k, base - 8 * k), (x + 3 * k, base)], max(1.0, w * 0.7), fill=INK))
    lt = base - h * 0.82
    out.append(p.shape([(x - 5 * k, lt), (x - 7 * k, lt - 13 * k), (x + 7 * k, lt - 13 * k), (x + 5 * k, lt)], max(1.0, w * 0.8)))
    out.append(p.seg(x, lt, x, lt - 13 * k, max(0.8, 1.0 * k), 0.0))
    out.append(p.solid([(x - 8 * k, lt - 13 * k), (x, lt - 19 * k), (x + 8 * k, lt - 13 * k)]))
    out.append(f'<circle cx="{x:.1f}" cy="{lt - 20.5 * k:.1f}" r="{max(1.0, 1.4 * k):.1f}" fill="{INK}"/>')
    out.append(f'<path d="M{x:.1f} {lt + 8 * k:.1f}q{6 * k:.1f} -2 {5 * k:.1f} -7M{x:.1f} {lt + 8 * k:.1f}q{-6 * k:.1f} -2 {-5 * k:.1f} -7" fill="none" stroke="{INK}" stroke-width="{max(0.9, 1.2 * k):.1f}"/>')
    return "".join(out)


@design("prague", "Prague", "50.0755° N · 14.4378° E")
def prague(name, coords):
    """Walking across Charles Bridge toward the Lesser Town: the blackened baroque saints on their pedestals,
    lanterns, a painter at his easel and a busker, the Gothic bridge tower at the end with St Nicholas's dome
    beside it and the castle and St Vitus on the hill above."""
    p = Pen("prague", 113)
    rnd = p.rnd
    C = Cam(f=900, cx=300, vpy=332, eye=1.7)
    o = [p.paper(23, vignette=0.28)]
    # --- sky, the castle hill, St Vitus cathedral and the castle's long facade
    o.append(p.hatch([(0, 130), (600, 130), (600, 330), (0, 330)], -3, 5.6, 1.0, 0.4, dash=(12, 46),
                     keep=lambda x, y: max(0, (y - 160) / 170) * (0.3 if 200 < x < 400 else 1)))
    o.append(p.birds([(380, 170), (396, 162, 0.7), (520, 186, 0.6)], 7))
    hill = smooth([(-10, 262), (60, 246), (140, 236), (220, 244), (280, 268), (330, 290)], 6)
    o.append(p.solid(hill + [(330, 336), (-10, 336)], PAPER))
    o.append(p.line(hill, 1.4, 0.3, op=0.8))
    # castle: a long palace facade with rows of windows along the ridge
    o.append(p.shape(rect(20, 222, 170, 26), 1.3))
    o.append(p.windows(26, 228, 20, 2, 3.2, 5, 4.9, 4, w=0.8, dark=0.9, sill=False))
    o.append(p.shape([(16, 222), (40, 212), (170, 212), (194, 222)], 1.2) + p.hatch([(16, 222), (40, 212), (170, 212), (194, 222)], 10, 2.4, 1.0, 0.6))
    # St Vitus: twin west spires and the great south tower with its baroque cap
    for sx in (92, 108):
        o.append(p.shape(rect(sx - 5, 160, 10, 54), 1.3) + p.hatch(rect(sx, 160, 5, 54), 90, 1.6, 1.0, 0.8))
        o.append(p.shape([(sx - 6, 160), (sx, 120), (sx + 6, 160)], 1.3) + p.hatch([(sx, 120), (sx + 6, 160), (sx, 160)], 80, 1.6, 1.0, 0.8))
        o.append(p.seg(sx, 120, sx, 112, 1.1))
    o.append(p.shape([(112, 212), (112, 186), (170, 186), (170, 212)], 1.2) + p.hatch([(112, 212), (112, 186), (170, 186), (170, 212)], 75, 2.6, 1.0, 0.6))
    for k in range(6):
        o.append(p.seg(116 + k * 9, 186, 116 + k * 9, 176, 1.0) + f'<path d="M{114 + k * 9} 176l2 -5l2 5" stroke="{INK}" stroke-width="0.9" fill="none"/>')
    o.append(p.shape(rect(132, 150, 18, 40), 1.4) + p.hatch(rect(141, 150, 9, 40), 90, 1.6, 1.0, 0.85))
    o.append(p.shape([(130, 150), (133, 140), (141, 132), (149, 140), (152, 150)], 1.3) + p.shape([(136, 132), (141, 120), (146, 132)], 1.2) + p.seg(141, 120, 141, 112, 1.1))
    # the hillside below the castle: Lesser Town roofs in tiny strokes and trees
    for x in range(-10, 330, 16):
        y = 252 + (x + 10) * 0.12 + rnd.uniform(-4, 4)
        o.append(p.foliage(x, y + 10, rnd.uniform(9, 14), rnd.uniform(6, 9), w=1.0, shade=0.6, bump=3, inner=0.4))
    # --- St Nicholas: the green dome and its bell tower, right of the bridge tower
    nx = 400
    o.append(p.shape(rect(nx - 30, 236, 60, 60), 1.4) + p.hatch(rect(nx + 6, 236, 24, 60), 80, 2.4, 1.0, 0.6))
    o.append(p.shape(rect(nx - 20, 220, 40, 16), 1.4) + p.windows(nx - 16, 223, 4, 1, 5, 9, 4.6, 0, w=0.8, dark=1, arch=True, sill=False))
    nd = arc_pts(nx, 220, 22, 30, 180, 360, 14)
    o.append(p.shape(nd + [(nx + 22, 220)], 1.8) + p.hatch(nd, 80, 2.2, 1.0, 0.85, keep=lambda x, y: max(0, (x - nx + 4) / 20)))
    o.append(p.shape(rect(nx - 5, 180, 10, 10), 1.2) + p.shape(arc_pts(nx, 180, 6, 6, 180, 360, 8), 1.2) + p.seg(nx, 174, nx, 164, 1.2))
    bt = 452
    o.append(p.shape(rect(bt - 12, 200, 24, 96), 1.5) + p.hatch(rect(bt + 2, 200, 10, 96), 90, 2.0, 1.0, 0.8))
    o.append(p.windows(bt - 6, 210, 2, 3, 4, 10, 4, 14, w=0.9, dark=1, arch=True, sill=False))
    o.append(p.shape([(bt - 14, 200), (bt - 10, 188), (bt - 4, 184), (bt - 3, 172), (bt, 160), (bt + 3, 172), (bt + 4, 184), (bt + 10, 188), (bt + 14, 200)], 1.4))
    o.append(p.hatch([(bt, 160), (bt + 3, 172), (bt + 4, 184), (bt + 10, 188), (bt + 14, 200), (bt, 200)], 80, 2.0, 1.0, 0.8))
    # Lesser Town roofs on the right
    for x0, w, h in ((480, 50, 40), (528, 40, 52), (566, 50, 36), (330, 40, 34)):
        o.append(p.shape([(x0, 300), (x0, 300 - h), (x0 + w / 2, 300 - h - 16), (x0 + w, 300 - h), (x0 + w, 300)], 1.3))
        o.append(p.hatch([(x0, 300 - h), (x0 + w / 2, 300 - h - 16), (x0 + w, 300 - h)], 20, 2.4, 1.0, 0.7))
        o.append(p.windows(x0 + 6, 300 - h + 8, int((w - 8) / 10), 2, 4, 7, 6, 6, w=0.8, dark=0.6, sill=False))
    # --- the Lesser Town Bridge Tower and the smaller Judith tower, with the gateway between them
    Z = 300
    tl, tr = C(-7.5, 0, Z)[0], C(5.5, 0, Z)[0]
    ground = C(0, 0, Z)[1]
    ttop = ground - 900 * 30 / Z
    tw = rect(tl, ttop, tr - tl, ground - ttop)
    o.append(p.shape(tw, 2.0))
    o.append(p.hatch([(tl + (tr - tl) * 0.6, ttop), (tr, ttop), (tr, ground), (tl + (tr - tl) * 0.6, ground)], 90, 2.2, 1.0, 0.85))
    o.append(p.stipple(tw, 80, r=(0.5, 0.9)))
    # gothic gateway arch, the gallery, windows
    gx = (tl + tr) / 2
    o.append(p.shape([(gx - 9, ground), (gx - 9, ground - 22), (gx, ground - 34), (gx + 9, ground - 22), (gx + 9, ground)], 1.6, fill=INK))
    o.append(p.windows(gx - 9, ttop + 26, 2, 2, 5, 10, 8, 16, w=0.9, dark=1, arch=True, sill=False))
    o.append(p.line([(tl - 2, ttop + 14), (tr + 2, ttop + 14)], 1.6, 0.1))
    # steep slate roof with corner turrets
    rf = [(tl - 3, ttop), (gx, ttop - 66), (tr + 3, ttop)]
    o.append(p.shape(rf, 2.0))
    o.append(p.hatch(rf, 70, 2.2, 1.0, 0.85))
    for tx in (tl, tr):
        o.append(p.shape([(tx - 4, ttop + 2), (tx - 4, ttop - 8), (tx, ttop - 26), (tx + 4, ttop - 8), (tx + 4, ttop + 2)], 1.3) + p.seg(tx, ttop - 26, tx, ttop - 32, 1.1))
    o.append(p.shape([(gx - 4, ttop - 40), (gx, ttop - 52), (gx + 4, ttop - 40)], 1.2))
    o.append(p.seg(gx, ttop - 66, gx, ttop - 78, 1.4) + f'<circle cx="{gx}" cy="{ttop - 70}" r="2" fill="{INK}"/>')
    # Judith tower, lower, to the right, and the battlemented gate between
    jx0, jx1 = tr + 18, tr + 44
    jt = ground - 900 * 18 / Z
    o.append(p.shape(rect(tr, ground - 26, jx0 - tr, 26), 1.4))
    o.append(f'<path d="{"".join(f"M{x:.1f} {ground - 26:.1f}v-4h3v4" for x in range(int(tr), int(jx0), 5))}" stroke="{INK}" stroke-width="1" fill="none"/>')
    o.append(p.shape(rect(jx0, jt, jx1 - jx0, ground - jt), 1.6) + p.hatch(rect(jx0 + 12, jt, jx1 - jx0 - 12, ground - jt), 90, 2.2, 1.0, 0.8))
    o.append(p.shape([(jx0 - 2, jt), (jx0 + 13, jt - 20), (jx1 + 2, jt)], 1.6) + p.hatch([(jx0 + 13, jt - 20), (jx1 + 2, jt), (jx0 + 13, jt)], 70, 2.0, 1.0, 0.8))
    # --- the bridge deck: cobbles running away, parapets, pedestals, saints, lanterns
    deck = [C(-5.2, 0, 4), C(-5.2, 0, Z), C(5.2, 0, Z), C(5.2, 0, 4)]
    o.append(p.solid(deck, PAPER))
    cob = []
    z = 4.6
    k = 0
    while z < Z:
        a_, b_ = C(-5.2, 0, z), C(5.2, 0, z)
        cob.append(f"M{a_[0]:.1f} {a_[1]:.1f}L{b_[0]:.1f} {b_[1]:.1f}")
        if z < 70:
            for X in [-5.2 + 0.55 * j + (0.27 if k % 2 else 0) for j in range(20)]:
                if X < 5.2:
                    q1, q2 = C(X, 0, z), C(X, 0, z * 1.045)
                    cob.append(f"M{q1[0]:.1f} {q1[1]:.1f}L{q2[0]:.1f} {q2[1]:.1f}")
        z *= 1.045
        k += 1
    o.append(f'<path d="{"".join(cob)}" stroke="{INK}" stroke-width="0.9" opacity="0.45"/>')
    # tram rails? no: the worn centre path where feet go, in stipple
    o.append(p.stipple([C(-1.6, 0, 6), C(-0.3, 0, Z), C(0.3, 0, Z), C(1.6, 0, 6)], 220, r=(0.5, 1.0)))
    statues = [8, 26, 44, 63, 84, 108, 136, 170, 210, 260]
    kinds = [0, 2, 1, 3, 1, 0, 3, 2, 1, 0]
    # long evening shadows of the left-hand statues and lanterns thrown across the cobbles
    for i, z in enumerate(statues):
        if z > 200:
            continue
        sh = [C(-5.2, 0, z), C(-5.2, 0, z + 1.8), C(-1.0, 0, z * 0.86 + 1.2), C(5.2, 0, z * 0.7 + 1.0), C(5.2, 0, z * 0.7 - 0.3), C(-1.0, 0, z * 0.86 - 0.2)]
        o.append(p.hatch(sh, 0, 2.2 if z < 30 else 1.8, 1.1, 0.85))
        if i < len(statues) - 1:
            zl = (z + statues[i + 1]) / 2
            sh = [C(-5.2, 0, zl), C(-5.2, 0, zl + 0.25), C(2.0, 0, zl - 0.17 * zl), C(2.0, 0, zl - 0.17 * zl - 0.2)]
            o.append(p.hatch(sh, 0, 1.6, 1.0, 0.8))
    for side in (-1, 1):
        X = 5.5 * side
        # parapet: a wall with stone coping running away to the tower
        top_line = [C(X, 1.1, 4), C(X, 1.1, Z)]
        wall = [C(X, 0, 4), C(X, 1.1, 4), C(X, 1.1, Z), C(X, 0, Z)]
        o.append(p.shape(wall, 1.6))
        o.append(p.hatch(wall, 0, 2.6, 1.0, 0.5, dash=(8, 6)))
        o.append(p.line(top_line, 2.4, 0.2))
        for i in range(len(statues) - 1, -1, -1):
            z = statues[i] + (9 if side > 0 else 0)
            if z >= Z - 20:
                continue
            # lantern halfway to the next statue
            if i < len(statues) - 1:
                zl = (z + statues[i + 1] + (9 if side > 0 else 0)) / 2
                if zl < Z - 20:
                    b = C(X * 0.98, 1.1, zl)
                    o.append(bridge_lamp(p, b[0], b[1], 900 * 4.2 / zl))
            # pedestal: base, die with a panel, cornice
            pw, pd = 1.4, 1.6
            front = [C(X - side * pw, 1.1, z), C(X - side * pw, 3.4, z), C(X + side * 0.4, 3.4, z), C(X + side * 0.4, 1.1, z)]
            sidef = [C(X - side * pw, 1.1, z), C(X - side * pw, 3.4, z), C(X - side * pw, 3.4, z + pd), C(X - side * pw, 1.1, z + pd)]
            o.append(p.shape(sidef, max(1.2, 30 / z)))
            o.append(p.hatch(sidef, 90, 2.0, 1.0, 0.8))
            o.append(p.shape(front, max(1.3, 36 / z)))
            if z < 60:
                o.append(p.line([C(X - side * pw * 0.8, 1.6, z), C(X - side * pw * 0.8, 2.9, z), C(X + side * 0.2, 2.9, z), C(X + side * 0.2, 1.6, z)], 1.1, 0.1, closed=True))
            cap = [C(X - side * (pw + 0.15), 3.4, z - 0.1), C(X - side * (pw + 0.15), 3.65, z - 0.1), C(X + side * 0.55, 3.65, z - 0.1), C(X + side * 0.55, 3.4, z - 0.1)]
            o.append(p.shape(cap, max(1.2, 30 / z)))
            # the statue
            sb = C(X - side * 0.5, 3.65, z + 0.4)
            o.append(saint(p, sb[0], sb[1] + 1, 900 * 2.6 / z, kinds[i], flip=side > 0))
    # --- people on the bridge: a painter at an easel, a busker with a double bass, strollers
    def at(X, z, h=1.7):
        q = C(X, 0, z)
        return q, 900 * h / z
    q, h = at(-3.6, 30)
    o.append(p.person(q[0], q[1], h, 1, flip=True))
    o.append(p.line([(q[0] + h * 0.3, q[1]), (q[0] + h * 0.45, q[1] - h * 0.85)], 1.6, 0.1) + p.line([(q[0] + h * 0.6, q[1]), (q[0] + h * 0.45, q[1] - h * 0.85)], 1.6, 0.1))
    o.append(p.shape([(q[0] + h * 0.26, q[1] - h * 0.48), (q[0] + h * 0.62, q[1] - h * 0.48), (q[0] + h * 0.6, q[1] - h * 0.86), (q[0] + h * 0.28, q[1] - h * 0.86)], 1.4))
    o.append(p.hatch([(q[0] + h * 0.3, q[1] - h * 0.52), (q[0] + h * 0.58, q[1] - h * 0.52), (q[0] + h * 0.57, q[1] - h * 0.82), (q[0] + h * 0.31, q[1] - h * 0.82)], 30, 2.6, 1.0, 0.6))
    q, h = at(3.4, 22)
    o.append(p.person(q[0], q[1], h, 1))
    bass = [(q[0] - h * 0.32, q[1] - h * 0.05), (q[0] - h * 0.42, q[1] - h * 0.3), (q[0] - h * 0.34, q[1] - h * 0.5), (q[0] - h * 0.38, q[1] - h * 0.62),
            (q[0] - h * 0.26, q[1] - h * 0.66), (q[0] - h * 0.18, q[1] - h * 0.5), (q[0] - h * 0.12, q[1] - h * 0.3), (q[0] - h * 0.2, q[1] - h * 0.05)]
    o.append(p.shape(bass, 1.6) + p.hatch(bass, 60, 2.4, 1.0, 0.8))
    o.append(p.seg(q[0] - h * 0.3, q[1] - h * 0.66, q[0] - h * 0.24, q[1] - h * 1.05, 2.0))
    o.append(p.shape([(q[0] + h * 0.2, q[1]), (q[0] + h * 0.42, q[1]), (q[0] + h * 0.4, q[1] - h * 0.06), (q[0] + h * 0.22, q[1] - h * 0.06)], 1.2))
    for X, z, f, d in ((-1.2, 46, False, True), (-0.6, 47, False, False), (1.4, 64, True, False), (0.2, 90, True, True), (-2.0, 120, False, False),
                       (2.2, 150, True, True), (-0.8, 180, False, False), (1.0, 200, True, False), (0.0, 34, True, True), (2.4, 40, False, False)):
        q, h = at(X, z)
        o.append(p.person(q[0], q[1], h, int(z) % 2, flip=f, dress=d, bag=d))
    # strollers in the foreground walking toward the tower, a child with a balloon
    q, h = at(-1.9, 13)
    o.append(p.walker(q[0], q[1], h, "woman", stride=0.4, bag=True))
    q, h = at(-1.0, 13.6)
    o.append(p.walker(q[0], q[1], h, "man", flip=True, stride=-0.5, hat=True))
    q, h = at(1.8, 16)
    o.append(p.walker(q[0], q[1], h, "man", stride=0.6))
    q, h = at(-0.35, 13.0, 1.0)
    o.append(p.walker(q[0], q[1], h, "child", stride=0.6))
    o.append(f'<path d="M{q[0] + h * 0.14:.1f} {q[1] - h * 0.42:.1f}q{h * 0.12:.1f} {-h * 0.4:.1f} {h * 0.04:.1f} {-h * 0.68:.1f}" fill="none" stroke="{INK}" stroke-width="1.2"/>'
             f'<ellipse cx="{q[0] + h * 0.04:.1f}" cy="{q[1] - h * 1.3:.1f}" rx="{h * 0.17:.1f}" ry="{h * 0.21:.1f}" fill="{PAPER}" stroke="{INK}" stroke-width="1.8"/>')
    o.append(p.hatch(arc_pts(q[0] + h * 0.04, q[1] - h * 1.3, h * 0.16, h * 0.2, 0, 360, 16), 60, 2.4, 1.0, 0.7, keep=lambda x, y, c=q[0] + h * 0.04: 1 if x > c else 0))
    # a dog trotting ahead
    q, h = at(0.3, 11.5, 0.5)
    o.append(f'<path d="M{q[0]:.1f} {q[1]:.1f}l{h * 0.1:.1f} {-h * 0.5:.1f}q{h * -0.05:.1f} {-h * 0.3:.1f} {h * 0.25:.1f} {-h * 0.32:.1f}h{h * 0.55:.1f}q{h * 0.2:.1f} 0 {h * 0.28:.1f} {-h * 0.22:.1f}l{h * 0.1:.1f} {-h * 0.2:.1f}l{h * 0.14:.1f} {h * 0.08:.1f}v{h * 0.2:.1f}q{h * 0.14:.1f} {h * 0.1:.1f} {h * 0.06:.1f} {h * 0.24:.1f}h{-h * 0.14:.1f}l{-h * 0.1:.1f} {h * 0.22:.1f}l{h * 0.04:.1f} {h * 0.52:.1f}h{-h * 0.08:.1f}l{-h * 0.1:.1f} {-h * 0.4:.1f}h{-h * 0.4:.1f}l{-h * 0.08:.1f} {h * 0.4:.1f}h{-h * 0.08:.1f}l0 {-h * 0.4:.1f}q{-h * 0.12:.1f} {h * 0.05:.1f} {-h * 0.2:.1f} {h * 0.4:.1f}Z" fill="{INK}"/>')
    # a pigeon pair on the near coping
    for bx, by in ((86, 398), (100, 402)):
        o.append(f'<path d="M{bx - 7} {by}q2 -7 10 -6l4 -4l3 2l-2 3q0 6 -8 6Z" fill="{INK}"/>')
    # --- title on a hanging ribbon
    o.append(ribbon(p, 300, 82, 290, 56, name, name_size(name, 250, 48, ls=4), tail=26, drop=10, ls=4))
    o.append(coord_line(p, 300, 140, coords, 16, 2.2, 24, 10))
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- ISTANBUL
def minaret(p, x, base, top, w=8, balconies=2, lw=1.6, tone=0.7):
    """Ottoman pencil minaret: a slender fluted shaft with corbelled serefe balconies and a tall conical cap."""
    cap_h = (base - top) * 0.2
    sh_top = top + cap_h
    out = [p.shape(rect(x - w / 2, sh_top, w, base - sh_top), lw)]
    out.append(p.hatch(rect(x, sh_top, w / 2, base - sh_top), 90, 1.6, 1.0, tone))
    for i in range(balconies):
        by = sh_top + (base - sh_top) * (0.12 + 0.3 * i)
        out.append(p.shape([(x - w / 2, by + 5), (x - w / 2 - 3, by), (x + w / 2 + 3, by), (x + w / 2, by + 5)], 1.2))
        out.append(p.line([(x - w / 2 - 3, by - 2), (x + w / 2 + 3, by - 2)], 1.0, 0.1))
    out.append(p.shape([(x - w / 2 - 0.5, sh_top), (x, top), (x + w / 2 + 0.5, sh_top)], lw))
    out.append(p.hatch([(x, top), (x + w / 2 + 0.5, sh_top), (x, sh_top)], 80, 1.6, 1.0, 0.9))
    out.append(p.seg(x, top, x, top - 6, 1.1) + f'<circle cx="{x:.1f}" cy="{top - 3:.1f}" r="1.3" fill="{INK}"/>')
    return "".join(out)


def dome(p, cx, base, r, h=None, lw=1.8, tone=0.8, ribs=0, finial=True):
    """A lead-covered dome on a short drum pierced with windows, shaded away from the setting sun (left)."""
    h = h or r * 0.95
    dpts = [(cx + r * math.cos(t), base - h * math.sin(t)) for t in [math.pi * k / 20 for k in range(21)]]
    out = [p.shape(dpts, lw)]
    out.append(p.hatch(dpts, 100, 2.2, 1.0, tone, keep=lambda x, y: max(0.15, min(1, (x - cx + r * 0.6) / (r * 1.2)))))
    for k in range(ribs):
        f = -0.8 + 1.6 * k / max(1, ribs - 1)
        out.append(p.line([(cx + r * f * math.cos(t), base - h * math.sin(t)) for t in [math.pi / 2 * j / 8 for j in range(9)]], 0.9, 0.1))
    if finial:
        out.append(p.seg(cx, base - h, cx, base - h - max(6, r * 0.4), 1.2) + f'<circle cx="{cx:.1f}" cy="{base - h - 3:.1f}" r="{max(1.4, r * 0.08):.1f}" fill="{INK}"/>'
                   + f'<path d="M{cx - 3:.1f} {base - h - max(6, r * 0.4) + 3:.1f}a3 3 0 1 0 6 0" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    return "".join(out)


@design("istanbul", "Istanbul", "41.0082° N · 28.9784° E")
def istanbul(name, coords):
    """Sunset from the rail of the Galata Bridge: fishermen's rods leaning over the Golden Horn, a ferry
    crossing, gulls, and the cascading domes and minarets of the New Mosque, with the Suleymaniye on the hill."""
    p = Pen("istanbul", 127)
    rnd = p.rnd
    GOLD = "#E2B45C"
    o = [p.paper(25, vignette=0.2)]
    WL = 352
    # --- sunset sky: the sun banded by thin cloud strokes behind the domes
    sx, sy, sr = 404, 236, 52
    o.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="{GOLD}" opacity="0.4"/>')
    o.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="none" stroke="{INK}" stroke-width="1.6"/>')
    bands = []
    for k in range(6):
        y = sy - 12 + k * 9
        hw = math.sqrt(max(0, sr * sr - (y - sy) ** 2))
        bands.append(f"M{sx - hw - 30 - k * 6:.1f} {y:.1f}H{sx + hw + 40 - k * 4:.1f}")
    o.append(f'<path d="{"".join(bands)}" stroke="{INK}" stroke-width="{1.4}" opacity="0.7"/>')
    o.append(p.hatch([(0, 60), (600, 60), (600, WL), (0, WL)], -2, 4.6, 1.0, 0.45, dash=(14, 40),
                     keep=lambda x, y: max(0, (y - 120) / 230) * (0 if math.hypot(x - sx, y - sy) < sr + 8 else 1)))
    # --- the Suleymaniye on its hill: great dome, cascading half-domes, four minarets (lighter: distance)
    hill = smooth([(-10, 300), (60, 280), (160, 262), (260, 270), (320, 292), (360, 320)], 6)
    o.append(p.solid(hill + [(360, WL), (-10, WL)], PAPER))
    o.append(p.line(hill, 1.2, 0.2, op=0.7))
    o.append(p.hatch(hill + [(360, WL), (-10, WL)], 10, 3.6, 1.0, 0.45))
    sm = 160
    o.append(p.shape(rect(sm - 60, 244, 120, 22), 1.3) + p.hatch(rect(sm - 60, 244, 120, 22), 80, 3.0, 1.0, 0.5))
    for dx in (-34, 34):
        o.append(dome(p, sm + dx, 244, 14, lw=1.2, tone=0.55, finial=False))
    o.append(dome(p, sm, 236, 30, lw=1.5, tone=0.6, ribs=5))
    o.append(p.shape(rect(sm - 30, 236, 60, 8), 1.2))
    for mx, top in ((sm - 70, 150), (sm - 58, 168), (sm + 58, 168), (sm + 70, 150)):
        o.append(minaret(p, mx, 266, top, 5, 2, 1.1, 0.5))
    # --- the New Mosque on the waterfront: courtyard arcade, buttress turrets, half-domes, central dome
    nm = 380
    base = WL - 8
    o.append(p.shape(rect(nm - 120, base - 34, 240, 34), 1.8))
    o.append(p.windows(nm - 112, base - 26, 16, 1, 7, 18, 7.2, 0, w=1.0, dark=1, arch=True, sill=False))
    o.append(p.line([(nm - 124, base - 34), (nm + 124, base - 34)], 2.2, 0.1))
    o.append(p.hatch(rect(nm + 40, base - 34, 80, 34), 80, 2.6, 1.0, 0.55))
    # small domes over the courtyard arcade
    for k in range(-5, 6):
        o.append(dome(p, nm + k * 21, base - 34, 9, lw=1.1, tone=0.6, finial=False))
    # the prayer hall block, kept low so the domes can cascade
    o.append(p.shape(rect(nm - 70, base - 58, 140, 24), 1.8) + p.hatch(rect(nm + 10, base - 58, 60, 24), 80, 2.4, 1.0, 0.6))
    o.append(p.windows(nm - 62, base - 53, 10, 1, 6, 12, 7.3, 0, w=1.0, dark=1, arch=True, sill=False))
    # corner domes, then the four half-domes, buttress turrets, the drum and the great central dome
    for dx in (-56, 56):
        o.append(dome(p, nm + dx, base - 58, 13, lw=1.3, tone=0.7))
    for dx in (-34, 34):
        o.append(dome(p, nm + dx, base - 64, 26, 22, lw=1.7, tone=0.75, finial=False))
    o.append(dome(p, nm, base - 72, 30, 18, lw=1.6, tone=0.7, finial=False))
    for dx in (-44, -24, 24, 44):
        o.append(p.shape(rect(nm + dx - 4, base - 94, 8, 22), 1.2) + dome(p, nm + dx, base - 94, 5, lw=1.0, tone=0.7))
    o.append(p.shape(rect(nm - 34, base - 100, 68, 18), 1.6) + p.windows(nm - 30, base - 96, 8, 1, 4, 10, 4.1, 0, w=0.9, dark=1, arch=True, sill=False))
    o.append(dome(p, nm, base - 100, 38, 34, lw=2.2, tone=0.9, ribs=7))
    for mx, top in ((nm - 104, 160), (nm + 104, 160)):
        o.append(minaret(p, mx, base - 30, top, 8, 3, 1.6, 0.8))
    # the waterfront below: quay, a few tram-stop roofs, people
    o.append(p.shape([(-10, WL - 8), (610, WL - 8), (610, WL), (-10, WL)], 1.6))
    o.append(p.hatch([(-10, WL - 8), (610, WL - 8), (610, WL), (-10, WL)], 0, 2.0, 1.0, 0.8))
    for x in range(30, 600, 26):
        o.append(p.person(x + rnd.uniform(-6, 6), WL - 8, rnd.uniform(9, 11), rnd.randint(0, 1), flip=rnd.random() < 0.5))
    # --- the Golden Horn: sun glitter, a ferry with its wake, small boats, gulls
    o.append(p.line([(-10, WL), (610, WL)], 1.8, 0.3))
    o.append(p.hatch([(sx - 40, WL + 2), (sx + 40, WL + 2), (sx + 70, 440), (sx - 70, 440)], 0, 3.0, 1.6, 0.9, dash=(4, 7)))
    o.append(p.ripples(-10, 610, WL + 4, 440, 150, hy=WL, lmin=6, lmax=28, wmin=1.0, wmax=1.7,
                       avoid=[(sx - 70, WL, sx + 70, 440)]))
    fx, fy = 150, 404
    hull = [(fx - 74, fy - 6), (fx + 70, fy - 6), (fx + 84, fy - 14), (fx + 70, fy + 8), (fx - 66, fy + 8), (fx - 80, fy - 12)]
    o.append(p.shape(hull, 2.0) + p.hatch([(fx - 74, fy + 2), (fx + 74, fy + 2), (fx + 70, fy + 8), (fx - 66, fy + 8)], 0, 1.8, 1.0, 0.9))
    o.append(p.shape(rect(fx - 60, fy - 22, 118, 16), 1.6) + p.windows(fx - 56, fy - 19, 14, 1, 5, 7, 3.4, 0, w=0.8, dark=1, sill=False))
    o.append(p.shape(rect(fx - 40, fy - 34, 72, 12), 1.4) + p.windows(fx - 36, fy - 31, 9, 1, 4, 5, 3.6, 0, w=0.8, dark=1, sill=False))
    o.append(p.shape([(fx - 6, fy - 34), (fx - 4, fy - 52), (fx + 8, fy - 52), (fx + 10, fy - 34)], 1.6) + p.hatch(rect(fx - 5, fy - 52, 14, 8), 0, 1.6, 1.0, 0.9))
    o.append(p.seg(fx + 30, fy - 34, fx + 30, fy - 58, 1.2) + p.seg(fx - 30, fy - 34, fx - 30, fy - 50, 1.0))
    o.append(f'<path d="M{fx + 86} {fy - 10}q20 4 50 2M{fx + 72} {fy + 8}q30 8 76 6M{fx + 60} {fy + 10}q40 14 110 10" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    o.append(p.reflect(fx - 66, fx + 70, fy + 9, 18, density=0.9, sp=2.4, w=1.2, taper=0.2))
    for bx, by in ((520, 380), (292, 392)):
        o.append(p.solid([(bx - 16, by), (bx + 16, by), (bx + 12, by + 5), (bx - 12, by + 5)]) + p.person(bx - 2, by, 12, 1))
    o.append(p.birds([(250, 160), (266, 150, 0.8), (520, 120), (538, 130, 0.7), (90, 200, 0.9), (300, 300, 0.6), (470, 320, 0.7), (560, 220, 0.8)], 8, 1.6))
    # --- the bridge rail in the foreground: fishermen, their rods and lines, a bucket, a gull on the rail
    RY = 444
    o.append(p.shape([(-10, RY), (610, RY), (610, 610), (-10, 610)], 2.2))
    o.append(p.hatch([(-10, RY + 30), (610, RY + 30), (610, 610), (-10, 610)], 0, 4.4, 1.0, 0.35, dash=(30, 12)))
    rods = [(70, 440, 40, 170, 300, 420), (176, 440, 150, 150, 240, 428), (300, 440, 330, 190, 420, 436), (500, 440, 560, 160, 500, 424)]
    for hx, hy, tx, ty, lx, ly in rods:
        o.append(p.line([(hx, hy), (tx, ty)], 2.0, 0.3))
        o.append(f'<path d="M{tx} {ty}Q{(tx + lx) / 2 + 10} {(ty + ly) / 2 - 20} {lx} {ly}" fill="none" stroke="{INK}" stroke-width="0.9"/>')
    for x, kind, flip, stride in ((92, "man", False, 0.1), (196, "man", True, 0.0), (520, "man", False, 0.1)):
        o.append(p.walker(x, RY + 34, 70, kind, flip, stride, hat=(x == 196)))
    o.append(p.walker(452, RY + 34, 64, "woman", False, 0.3, bag=True))
    # the railing in front of them
    o.append(p.line([(-10, RY), (610, RY)], 3.0, 0.2) + p.line([(-10, RY + 4), (610, RY + 4)], 1.2, 0.2))
    o.append(f'<path d="{"".join(f"M{x} {RY + 4}V{RY + 34}" for x in range(-6, 610, 9))}" stroke="{INK}" stroke-width="1.4"/>')
    o.append(p.line([(-10, RY + 34), (610, RY + 34)], 2.6, 0.2))
    o.append(p.shape([(240, RY + 34), (262, RY + 34), (260, RY + 14), (242, RY + 14)], 1.4) + p.hatch([(240, RY + 34), (262, RY + 34), (260, RY + 14), (242, RY + 14)], 90, 2.0, 1.0, 0.8))
    gx_, gy_ = 360, RY
    o.append(f'<path d="M{gx_ - 12} {gy_ - 8}q8 -8 20 -6l6 -6l4 2l-2 6l6 2l-6 2q-8 6 -24 4Z" fill="{PAPER}" stroke="{INK}" stroke-width="1.4"/>'
             f'<path d="M{gx_ - 12} {gy_ - 8}l-6 -2" stroke="{INK}" stroke-width="2"/><path d="M{gx_ - 2} {gy_ - 4}v4M{gx_ + 4} {gy_ - 4}v4" stroke="{INK}" stroke-width="1.2"/>'
             f'<path d="M{gx_ - 8} {gy_ - 10}q8 -2 14 2" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    # --- title in an ogee-arched cartouche below the rail
    cx, y0, y1, hw = 300, 494, 556, 190
    arch = [(cx - hw, y1), (cx - hw, y0 + 4)]
    arch += [(cx - hw + (hw - 18) * t, y0 + 4 - 6 * math.sin(math.pi * t) * 0 - 0) for t in (0.5,)]
    arch = [(cx - hw, y1), (cx - hw, y0 + 2), (cx - 40, y0 + 2), (cx - 16, y0 - 4), (cx, y0 - 16), (cx + 16, y0 - 4), (cx + 40, y0 + 2), (cx + hw, y0 + 2), (cx + hw, y1)]
    o.append(p.shape(arch, 2.4))
    inner = [(cx - hw + 6, y1 - 6), (cx - hw + 6, y0 + 8), (cx - 38, y0 + 8), (cx - 14, y0 + 2), (cx, y0 - 8), (cx + 14, y0 + 2), (cx + 38, y0 + 8), (cx + hw - 6, y0 + 8), (cx + hw - 6, y1 - 6)]
    o.append(p.line(inner, 1.1, 0.2, closed=True))
    o.append(f'<path d="M{cx - 4} {y0 - 4}a5 5 0 1 0 8 0" fill="none" stroke="{INK}" stroke-width="1.3"/>')
    sz = name_size(name, 2 * hw - 50, 44, ls=2)
    o.append(title_text(cx, 528, name, sz, ls=2))
    o.append(title_text(cx, 546, coords, fit_size(coords, MONO, 16, 2 * hw - 40, 1.6), MONO, ls=1.6))
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- KYOTO
def pagoda(p, cx, base, h, w, lw=1.8):
    """The five-storey pagoda of Hokan-ji (Yasaka Pagoda): stacked storeys each under a broad, upswept tiled
    eave with bracketing in shadow beneath, shrinking upward, crowned by the bronze sorin spire with its nine
    rings."""
    out = []
    spire_h = h * 0.27
    body_h = h - spire_h
    fl_h = body_h / 5.4
    y = base
    out.append(p.shape(rect(cx - w * 0.55, base - fl_h * 0.25, w * 1.1, fl_h * 0.25), lw))       # stone podium
    out.append(p.hatch(rect(cx - w * 0.55, base - fl_h * 0.25, w * 1.1, fl_h * 0.25), 0, 2.0, 1.0, 0.6))
    y -= fl_h * 0.25
    for i in range(5):
        k = 1 - 0.09 * i
        bw = w * 0.4 * k
        sh = fl_h * (0.6 if i == 0 else 0.44)
        body = rect(cx - bw, y - sh, 2 * bw, sh)
        out.append(p.shape(body, lw * 0.9))
        out.append(p.hatch(rect(cx + bw * 0.2, y - sh, bw * 0.8, sh), 90, 2.0, 1.0, 0.85))
        # door and latticed panels
        out.append(p.solid(rect(cx - bw * 0.22, y - sh * 0.85, bw * 0.44, sh * 0.85)))
        out.append(f'<path d="{"".join(f"M{cx - bw * 0.22 + j * bw * 0.11:.1f} {y - sh * 0.85:.1f}v{sh * 0.85:.1f}" for j in range(1, 4))}" stroke="{PAPER}" stroke-width="0.8"/>')
        out.append(p.seg(cx - bw * 0.62, y - sh, cx - bw * 0.62, y, 1.0) + p.seg(cx + bw * 0.62, y - sh, cx + bw * 0.62, y, 1.0))
        y -= sh
        # bracket cluster: a dark band under the eave
        ew = w * 1.02 * k
        out.append(p.solid([(cx - bw - 2, y), (cx - ew * 0.86, y - fl_h * 0.16), (cx + ew * 0.86, y - fl_h * 0.16), (cx + bw + 2, y)]))
        # the eave: a thin tiled roof flaring to upturned corners
        t = fl_h * 0.26
        eave = [(cx - ew - 6, y - fl_h * 0.2 - 9), (cx - ew * 0.8, y - fl_h * 0.18), (cx + ew * 0.8, y - fl_h * 0.18), (cx + ew + 6, y - fl_h * 0.2 - 9),
                (cx + ew * 0.85, y - fl_h * 0.2 - t * 0.7), (cx + bw * 0.6, y - fl_h * 0.2 - t * 1.5), (cx - bw * 0.6, y - fl_h * 0.2 - t * 1.5),
                (cx - ew * 0.85, y - fl_h * 0.2 - t * 0.7)]
        out.append(p.shape(eave, lw))
        tiles = "".join(f"M{cx + f * ew * 0.85:.1f} {y - fl_h * 0.19:.1f}L{cx + f * bw * 0.6:.1f} {y - fl_h * 0.2 - t * 1.45:.1f}" for f in [j / 10 - 1 for j in range(0, 21)])
        out.append(f'<path d="{tiles}" stroke="{INK}" stroke-width="0.9"/>')
        out.append(p.hatch(eave, 75, 2.2, 1.0, 0.8, keep=lambda x, y_, cx=cx: 1 if x > cx else 0.25))
        y -= fl_h * 0.2 + t * 1.5
    # sorin: base, nine rings, water-flame and jewel
    out.append(p.shape(rect(cx - w * 0.06, y - spire_h * 0.12, w * 0.12, spire_h * 0.12), 1.4))
    sy = y - spire_h * 0.12
    out.append(p.seg(cx, sy, cx, sy - spire_h * 0.86, 2.0, 0.1))
    for j in range(9):
        ry = sy - spire_h * (0.08 + 0.065 * j)
        rw = w * 0.11 * (1 - 0.03 * j)
        out.append(f'<ellipse cx="{cx:.1f}" cy="{ry:.1f}" rx="{rw:.1f}" ry="{max(1.2, rw * 0.22):.1f}" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>')
    fy = sy - spire_h * 0.7
    out.append(f'<path d="M{cx - 6:.1f} {fy:.1f}q2 -8 6 -12q4 4 6 12Z" fill="{INK}"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{sy - spire_h * 0.86:.1f}" r="2.2" fill="{INK}"/>')
    return "".join(out)


def chochin(p, x, y, s, wash=None):
    """A paper lantern hung from the eave: ribbed barrel, black caps, a tassel."""
    out = [p.seg(x, y - s * 0.9, x, y - s * 0.6, 1.0)]
    body = [(x + s * 0.32 * math.sin(t) * 1.0 + 0, y - s * 0.55 + s * 1.1 * (t / math.pi)) for t in []]
    pts = [(x + s * 0.34 * math.sin(math.pi * k / 12), y - s * 0.55 + s * 1.1 * k / 12) for k in range(13)]
    shp = pts + [(2 * x - a, b) for a, b in pts[::-1]]
    if wash:
        out.append(p.solid(shp, wash, 0.55))
    out.append(p.line(shp, 1.3, 0.1, closed=True))
    out.append(f'<path d="{"".join(f"M{x - s * 0.34 * math.sin(math.pi * k / 12):.1f} {y - s * 0.55 + s * 1.1 * k / 12:.1f}H{x + s * 0.34 * math.sin(math.pi * k / 12):.1f}" for k in range(2, 12, 2))}" stroke="{INK}" stroke-width="0.8"/>')
    out.append(p.solid(rect(x - s * 0.18, y - s * 0.62, s * 0.36, s * 0.1)) + p.solid(rect(x - s * 0.18, y + s * 0.53, s * 0.36, s * 0.1)))
    out.append(p.seg(x, y + s * 0.63, x, y + s * 0.85, 1.2))
    return "".join(out)


@design("kyoto", "Kyoto", "35.0116° N · 135.7681° E")
def kyoto(name, coords):
    """Up the stone-paved slope of Yasaka-dori in Higashiyama: wooden machiya with latticed fronts, hanging
    lanterns and noren, a pair in kimono climbing the steps, and the Yasaka Pagoda at the top of the lane."""
    p = Pen("kyoto", 131)
    rnd = p.rnd
    VERM = "#D9674A"
    o = [p.paper(27)]
    slope = 0.13
    C = Cam(f=520, cx=300, vpy=400, eye=1.6)
    G = lambda X, Z, Y=0.0: C(X, Y + slope * (Z - 4), Z)          # the ground rises as the lane climbs
    ZP = 74
    # --- sky and the wooded hill behind the pagoda
    o.append(p.hatch([(0, 40), (600, 40), (600, 340), (0, 340)], -3, 5.6, 1.0, 0.4, dash=(12, 46),
                     keep=lambda x, y: max(0, (y - 80) / 260) * (0.3 if 220 < x < 380 else 1)))
    hill = smooth([(-10, 250), (80, 226), (170, 220), (260, 236), (340, 232), (430, 214), (520, 226), (610, 240)], 6)
    o.append(p.solid(hill + [(610, 400), (-10, 400)], PAPER))
    o.append(p.line(hill, 1.3, 0.3, op=0.75))
    o.append(p.scribble(0, 0, 1, 1, sp=4.2, loop=2.4, w=1.0, poly=hill + [(610, 300), (-10, 300)], base=0.55, shade=0.9, dark=0.3,
                        light=(-1, -1), cr=(10, 18), op=0.85))
    o.append(p.birds([(470, 120), (486, 112, 0.7), (130, 150, 0.6)], 7))
    # --- the pagoda at the top of the lane
    pb = G(0.6, ZP)
    o.append(pagoda(p, pb[0], pb[1], 520 * 40 / ZP, 520 * 7.6 / ZP))
    # --- the lane: stone paving and steps rising away, gutters at the sides
    o.append(p.solid([G(-3.2, 3), G(-3.2, ZP), G(3.2, ZP), G(3.2, 3)], PAPER))
    z = 3.2
    k = 0
    lines = []
    while z < ZP - 2:
        a_, b_ = G(-3.2, z), G(3.2, z)
        lines.append(f"M{a_[0]:.1f} {a_[1]:.1f}L{b_[0]:.1f} {b_[1]:.1f}")
        for X in [-3.2 + 0.9 * j + (0.45 if k % 2 else 0) for j in range(8)]:
            if -3.2 < X < 3.2:
                q1, q2 = G(X, z), G(X, z * 1.08)
                lines.append(f"M{q1[0]:.1f} {q1[1]:.1f}L{q2[0]:.1f} {q2[1]:.1f}")
        z *= 1.08
        k += 1
    o.append(f'<path d="{"".join(lines)}" stroke="{INK}" stroke-width="1.0" opacity="0.6"/>')
    # a flight of steps in the foreground: risers shaded
    for j in range(5):
        z0 = 4.2 + j * 0.9
        a_, b_ = G(-3.2, z0), G(3.2, z0)
        a2, b2 = C(-3.2, slope * (z0 - 4) - 0.16, z0), C(3.2, slope * (z0 - 4) - 0.16, z0)
        o.append(p.hatch([a_, b_, b2, a2], 0, 1.8, 1.0, 0.85))
        o.append(p.line([a_, b_], 1.8, 0.2))
    # --- machiya down both sides
    def machiya(X, z0, z1, side, two=True, tone=0.5):
        out = []
        F = lambda Y, z: G(X, z, Y)
        H1, H2 = 3.2, 6.0
        wall = [F(0, z0), F(H2 if two else H1, z0), F(H2 if two else H1, z1), F(0, z1)]
        out.append(p.shape(wall, 1.6))
        # ground floor: koshi lattice (vertical slats), a dark doorway with noren
        lat = [F(0.5, z0 + 0.4), F(2.4, z0 + 0.4), F(2.4, z0 + (z1 - z0) * 0.55), F(0.5, z0 + (z1 - z0) * 0.55)]
        out.append(p.shape(lat, 1.2))
        n = int((z1 - z0) * 0.55 * 9)
        sl = []
        for j in range(n):
            zz = z0 + 0.4 + ((z1 - z0) * 0.55 - 0.4) * j / n
            a1, a2_ = F(0.5, zz), F(2.4, zz)
            sl.append(f"M{a1[0]:.1f} {a1[1]:.1f}L{a2_[0]:.1f} {a2_[1]:.1f}")
        out.append(f'<path d="{"".join(sl)}" stroke="{INK}" stroke-width="{max(0.8, min(1.4, 30 / z0)):.1f}"/>')
        door = [F(0, z0 + (z1 - z0) * 0.62), F(2.3, z0 + (z1 - z0) * 0.62), F(2.3, z1 - 0.3), F(0, z1 - 0.3)]
        out.append(p.solid(door))
        nr = [F(1.4, z0 + (z1 - z0) * 0.62), F(2.3, z0 + (z1 - z0) * 0.62), F(2.3, z1 - 0.3), F(1.4, z1 - 0.3)]
        out.append(p.shape(nr, 1.2) + p.hatch(nr, 90, 2.4, 1.0, 0.5))
        for f in (0.33, 0.66):
            zz = z0 + (z1 - z0) * (0.62 + 0.38 * f)
            a1, a2_ = F(1.4, zz), F(2.0, zz)
            out.append(p.seg(a1[0], a1[1], a2_[0], a2_[1], 1.6, 0.0, op=1).replace(INK, PAPER))
        # lower eave: a pent roof of tiles projecting over the street
        ex = X - side * 0.9
        eave = [G(X, z0 - 0.3, H1 + 0.2), G(ex, z0 - 0.3, H1 - 0.2), G(ex, z1 + 0.3, H1 - 0.2), G(X, z1 + 0.3, H1 + 0.2)]
        out.append(p.shape(eave, 1.5))
        out.append(p.hatch(eave, 0 if side < 0 else 0, 2.0 if z0 < 20 else 1.6, 1.0, 0.75))
        if two:
            # upper floor: mushiko-mado (plastered slot windows) and the main roof
            for f in (0.15, 0.55):
                zz0, zz1 = z0 + (z1 - z0) * f, z0 + (z1 - z0) * (f + 0.3)
                win = [F(4.0, zz0), F(5.2, zz0), F(5.2, zz1), F(4.0, zz1)]
                out.append(p.solid(win))
                nn = int((zz1 - zz0) * 7)
                out.append(f'<path d="{"".join(f"M{F(4.0, zz0 + (zz1 - zz0) * j / nn)[0]:.1f} {F(4.0, zz0 + (zz1 - zz0) * j / nn)[1]:.1f}L{F(5.2, zz0 + (zz1 - zz0) * j / nn)[0]:.1f} {F(5.2, zz0 + (zz1 - zz0) * j / nn)[1]:.1f}" for j in range(1, nn))}" stroke="{PAPER}" stroke-width="{max(0.9, min(1.8, 30 / z0)):.1f}"/>')
            ex2 = X - side * 1.0
            roof = [G(X, z0 - 0.4, H2 + 1.4), G(ex2, z0 - 0.4, H2), G(ex2, z1 + 0.4, H2), G(X, z1 + 0.4, H2 + 1.4)]
            out.append(p.shape(roof, 1.8))
            tl = []
            for j in range(int((z1 - z0) * 3)):
                zz = z0 - 0.3 + (z1 - z0 + 0.6) * j / int((z1 - z0) * 3)
                a1, a2_ = G(X, zz, H2 + 1.35), G(ex2, zz, H2 + 0.05)
                tl.append(f"M{a1[0]:.1f} {a1[1]:.1f}L{a2_[0]:.1f} {a2_[1]:.1f}")
            out.append(f'<path d="{"".join(tl)}" stroke="{INK}" stroke-width="{max(0.8, min(1.4, 26 / z0)):.1f}"/>')
            ridge = [G(X + side * 1.5, z0 - 0.4, H2 + 2.2), G(X + side * 1.5, z1 + 0.4, H2 + 2.2)]
            out.append(p.line([roof[0], ridge[0], ridge[1], roof[3]], 1.6, 0.2))
            out.append(p.hatch([roof[0], ridge[0], ridge[1], roof[3]], 0, 2.0, 1.0, 0.8))
        if tone:
            out.append(p.hatch(wall, 90, 5.0, 1.0, 0.35 * tone))
        return out
    for side, X in ((-1, -3.4), (1, 3.4)):
        z = 4.6
        houses = []
        while z < ZP - 6:
            L = rnd.uniform(6, 9)
            houses.append((z, min(z + L, ZP - 6)))
            z += L
        for z0, z1 in reversed(houses):
            o += machiya(X, z0, z1, side, two=rnd.random() < 0.8, tone=rnd.uniform(0.3, 0.9))
            if z0 < 40:
                q = G(X - side * 0.8, z0 + 0.6, 3.0)
                o.append(chochin(p, q[0], q[1], 520 * 0.6 / z0, VERM if z0 < 12 else None))
    # --- people: a pair in kimono climbing, a rickshaw puller resting, a few walkers up the lane
    def kimono(x, y, h, flip=False, umbrella=False):
        k = h / 100
        s = -1 if flip else 1
        X = lambda u: x + u * k * s
        Y = lambda v: y - v * k
        body = [(X(-10), Y(0)), (X(-11), Y(30)), (X(-13), Y(64)), (X(-11), Y(80)), (X(-5), Y(84)), (X(5), Y(84)), (X(11), Y(80)),
                (X(16), Y(64)), (X(12), Y(30)), (X(10), Y(0))]
        out = [p.solid(body)]
        out.append(p.shape([(X(-12), Y(48)), (X(13), Y(48)), (X(14), Y(58)), (X(-13), Y(58))], 1.2))      # obi
        out.append(p.shape([(X(-6), Y(58)), (X(6), Y(58)), (X(9), Y(70)), (X(-9), Y(70))], 0.1, fill=INK))
        out.append(f'<path d="M{X(-8):.1f} {Y(12):.1f}Q{X(0):.1f} {Y(24):.1f} {X(9):.1f} {Y(10):.1f}M{X(-9):.1f} {Y(30):.1f}q{6 * k * s:.1f} {-4 * k:.1f} {12 * k * s:.1f} {2 * k:.1f}" fill="none" stroke="{PAPER}" stroke-width="{max(0.9, 1.5 * k):.1f}"/>')
        out.append(f'<circle cx="{X(0):.1f}" cy="{Y(92):.1f}" r="{7 * k:.1f}" fill="{INK}"/><circle cx="{X(-1):.1f}" cy="{Y(101):.1f}" r="{4.5 * k:.1f}" fill="{INK}"/>')
        out.append(f'<path d="M{X(4):.1f} {Y(100):.1f}l{5 * k * s:.1f} {-3 * k:.1f}" stroke="{INK}" stroke-width="{1.2 * k:.1f}"/>')
        if umbrella:
            out.append(p.seg(X(12), Y(60), X(16), Y(118), max(1.2, 1.8 * k)))
            um = [(X(-24), Y(110)), (X(16), Y(132)), (X(54), Y(110))]
            out.append(p.shape([um[0], um[1], um[2], (X(16), Y(114))], 1.6))
            out.append(f'<path d="{"".join(f"M{X(16):.1f} {Y(130):.1f}L{X(-24 + 13 * j):.1f} {Y(110 + (2 if j % 2 else 0)):.1f}" for j in range(7))}" stroke="{INK}" stroke-width="1"/>')
        return "".join(out)
    q = G(-0.9, 9.4)
    o.append(kimono(q[0], q[1], 520 * 1.6 / 9.4, umbrella=True))
    q = G(0.0, 10.0)
    o.append(kimono(q[0], q[1], 520 * 1.6 / 10.0, flip=True))
    for X, z, f, d in ((1.8, 22, True, False), (-1.6, 30, False, True), (0.4, 42, True, True), (1.2, 54, False, False)):
        q = G(X, z)
        o.append(p.person(q[0], q[1], 520 * 1.65 / z, int(z) % 2, flip=f, dress=d))
    # --- title on a wooden signboard with its own little tiled roof
    cx, y0, y1 = 300, 478, 556
    hw = 170
    roof = [(cx - hw - 18, y0 - 2), (cx - hw + 6, y0 - 18), (cx + hw - 6, y0 - 18), (cx + hw + 18, y0 - 2), (cx + hw, y0 + 2), (cx - hw, y0 + 2)]
    o.append(p.seg(cx - hw + 20, y1, cx - hw + 20, 610, 4.0) + p.seg(cx + hw - 20, y1, cx + hw - 20, 610, 4.0))
    o.append(p.shape(rect(cx - hw, y0, 2 * hw, y1 - y0), 2.6))
    grain = "".join(f"M{cx - hw + 6:.1f} {y0 + 6 + j * 7:.1f}q{hw * 0.6:.1f} {rnd.uniform(-2, 2):.1f} {2 * hw - 12:.1f} {rnd.uniform(-1, 1):.1f}" for j in range(9))
    o.append(f'<path d="{grain}" fill="none" stroke="{INK}" stroke-width="0.8" opacity="0.25"/>')
    o.append(p.shape(roof, 2.2))
    o.append(f'<path d="{"".join(f"M{cx - hw + 2 + j * 10:.1f} {y0 - 3:.1f}l4 -13" for j in range(int(2 * hw / 10)))}" stroke="{INK}" stroke-width="1.2"/>')
    o.append(p.line([(cx - hw - 20, y0 - 2), (cx + hw + 20, y0 - 2)], 2.4, 0.1))
    sz = name_size(name, 2 * hw - 40, 46, ls=6)
    o.append(title_text(cx, 520, name, sz, ls=6))
    o.append(title_text(cx, 545, coords, fit_size(coords, MONO, 16, 2 * hw - 30, 1.4), MONO, ls=1.4))
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- SYDNEY
def sandstone_pylon(p, x0, x1, base, top, lw=2.0):
    """A granite-faced pylon of the Harbour Bridge: battered sides, coursed stonework, a stepped parapet top
    with arched openings, shaded on the right."""
    w = x1 - x0
    body = [(x0, base), (x0 + w * 0.04, top + 22), (x1 - w * 0.04, top + 22), (x1, base)]
    out = [p.shape(body, lw)]
    rows = []
    y = base - 7
    k = 0
    while y > top + 24:
        rows.append(f"M{x0 + 1:.1f} {y:.1f}H{x1 - 1:.1f}")
        off = 0 if k % 2 else 7
        for xx in range(int(x0 + off), int(x1), 14):
            rows.append(f"M{xx:.1f} {y:.1f}v7")
        y -= 7
        k += 1
    cid = p.uid("py")
    p.defs.append(f'<clipPath id="{cid}"><polygon points="{P(body)}"/></clipPath>')
    out.append(f'<path d="{"".join(rows)}" stroke="{INK}" stroke-width="0.8" opacity="0.55" clip-path="url(#{cid})"/>')
    out.append(p.hatch([(x0 + w * 0.62, top + 22), (x1 - w * 0.04, top + 22), (x1, base), (x0 + w * 0.62, base)], 90, 2.2, 1.0, 0.75))
    # upper stage with the lookout arches
    up = rect(x0 + w * 0.08, top, w * 0.84, 22)
    out.append(p.shape(up, lw * 0.9))
    for j in range(3):
        ax = x0 + w * (0.25 + 0.25 * j)
        out.append(p.shape([(ax - w * 0.07, top + 20), (ax - w * 0.07, top + 10)] + arc_pts(ax, top + 10, w * 0.07, w * 0.07, 180, 360, 6) + [(ax + w * 0.07, top + 20)], 1.0, fill=INK))
    out.append(p.line([(x0 + w * 0.04, top), (x1 - w * 0.04, top)], 2.4, 0.1) + p.line([(x0 + w * 0.02, top + 22), (x1 - w * 0.02, top + 22)], 2.0, 0.1))
    return "".join(out)


@design("sydney", "Sydney", "33.8688° S · 151.2093° E")
def sydney(name, coords):
    """The Harbour Bridge's steel arch from the water at Lavender Bay: the southern pylons standing in the
    harbour light, the truss spanning off the frame, a ferry and a yacht crossing, and a Moreton Bay fig
    dropping its aerial roots over the sandstone sea wall where the name is set."""
    p = Pen("sydney", 137)
    rnd = p.rnd
    FERRY = "#8DAE7E"
    o = [p.paper(29)]
    WL = 404
    S = 1.42                     # px per metre
    X0 = 92                      # southern bearing
    def Ylow(s):                 # lower chord height (m) along the span s (0..503)
        u = 2 * s / 503 - 1
        return 116 * (1 - u * u) + 6
    def Yup(s):
        u = 2 * s / 503 - 1
        return Ylow(s) + 18 + 39 * u * u
    sx = lambda s: X0 + s * S
    sy = lambda h: WL - h * S
    # --- sky: harbour light, a few clouds, gulls
    o.append(p.hatch([(0, 40), (600, 40), (600, WL), (0, WL)], -2, 5.8, 1.0, 0.4, dash=(12, 46),
                     keep=lambda x, y: max(0, (y - 120) / 280)))
    o.append(p.clouds(470, 96, 0.8) + p.clouds(330, 140, 0.5))
    o.append(p.birds([(250, 110), (268, 100, 0.7), (520, 170, 0.8), (540, 160, 0.6)], 8))
    # far shore: North Sydney towers behind the arch, low and pale
    for x0, w, h in ((300, 26, 70), (330, 20, 96), (354, 30, 58), (392, 22, 80), (420, 34, 46), (470, 26, 64), (500, 30, 40), (540, 40, 52)):
        o.append(p.shape(rect(x0, WL - 16 - h, w, h), 1.0, op=0.8) + p.hatch(rect(x0 + w * 0.55, WL - 16 - h, w * 0.45, h), 90, 2.4, 1.0, 0.45))
    shore = smooth([(160, WL - 14), (300, WL - 18), (420, WL - 16), (610, WL - 20)], 4)
    o.append(p.solid(shore + [(610, WL), (160, WL)], PAPER) + p.line(shore, 1.2, 0.2))
    o.append(p.stipple(shore + [(610, WL), (160, WL)], 120, r=(0.5, 1.0)))
    # --- the arch: lower and upper chords, the truss between, hangers to the deck
    ss = [k * 503 / 28 for k in range(29)]
    lower = [(sx(s), sy(Ylow(s))) for s in ss]
    upper = [(sx(s), sy(Yup(s))) for s in ss]
    deck_h = 49
    # truss web: verticals and diagonals
    web = []
    for i in range(len(ss) - 1):
        web.append(f"M{lower[i][0]:.1f} {lower[i][1]:.1f}L{upper[i][0]:.1f} {upper[i][1]:.1f}")
        if i % 2 == 0:
            web.append(f"M{lower[i][0]:.1f} {lower[i][1]:.1f}L{upper[i + 1][0]:.1f} {upper[i + 1][1]:.1f}")
        else:
            web.append(f"M{upper[i][0]:.1f} {upper[i][1]:.1f}L{lower[i + 1][0]:.1f} {lower[i + 1][1]:.1f}")
    o.append(f'<path d="{"".join(web)}" stroke="{INK}" stroke-width="1.5" stroke-linecap="round"/>')
    for chord, w in ((lower, 4.2), (upper, 3.4)):
        fine = [(sx(s), sy((Ylow if chord is lower else Yup)(s))) for s in [k * 503 / 120 for k in range(121)]]
        o.append(p.line(fine, w, 0.2))
        o.append(p.line([(x, y + (2.2 if chord is lower else 1.8)) for x, y in fine], 1.0, 0.2, color=PAPER, op=0.8))
    # hangers from the arch down to the deck, posts up from the arch where it dips below
    hg = []
    for s in ss[1:-1]:
        yl = sy(Ylow(s))
        yd = sy(deck_h)
        hg.append(f"M{sx(s):.1f} {yl:.1f}L{sx(s):.1f} {yd:.1f}")
    o.append(f'<path d="{"".join(hg)}" stroke="{INK}" stroke-width="1.3"/>')
    # the deck: road and rail, a train crossing
    dy = sy(deck_h)
    deck = [(-10, dy - 6), (610, dy - 6), (610, dy + 6), (-10, dy + 6)]
    o.append(p.shape(deck, 2.0))
    o.append(p.hatch([(-10, dy), (610, dy), (610, dy + 6), (-10, dy + 6)], 0, 1.8, 1.0, 0.8))
    o.append(f'<path d="{"".join(f"M{x} {dy - 6}v-5" for x in range(-8, 610, 6))}" stroke="{INK}" stroke-width="0.9"/>' + p.line([(-10, dy - 11), (610, dy - 11)], 1.2, 0.1))
    tr = []
    for j in range(5):
        x = 330 + j * 30
        tr.append(p.shape(rect(x, dy - 18, 28, 12), 1.2) + p.windows(x + 3, dy - 15, 4, 1, 4, 4, 2.4, 0, w=0.7, dark=1, sill=False))
    o.append("".join(tr))
    for x in (150, 230, 268):
        o.append(p.shape([(x - 9, dy - 6), (x - 8, dy - 11), (x - 4, dy - 14), (x + 5, dy - 14), (x + 8, dy - 11), (x + 9, dy - 6)], 1.1, fill=INK))
    # climbers on the upper chord (the bridge climb)
    for s in (150, 160, 170):
        x, y = sx(s), sy(Yup(s))
        o.append(p.person(x, y - 1, 9, 1))
    # flags on the summit
    ax_, ay_ = sx(251), sy(Yup(251))
    for dx in (-6, 6):
        o.append(p.seg(ax_ + dx, ay_, ax_ + dx, ay_ - 18, 1.2) + p.shape([(ax_ + dx, ay_ - 18), (ax_ + dx + 12, ay_ - 16), (ax_ + dx + 11, ay_ - 11), (ax_ + dx, ay_ - 12)], 1.0)
                 + p.hatch([(ax_ + dx, ay_ - 18), (ax_ + dx + 12, ay_ - 16), (ax_ + dx + 11, ay_ - 11), (ax_ + dx, ay_ - 12)], 0, 1.6, 1.0, 0.8))
    # --- the southern pylons (one in front of the other) and the approach span
    o.append(sandstone_pylon(p, X0 - 50, X0 + 8, WL, sy(89) + 6))
    o.append(p.line([(X0 - 70, dy - 6), (X0 - 50, dy - 6)], 1.6, 0.1))
    # bearing at the base of the arch
    o.append(p.solid([(X0 - 6, WL - 2), (X0 + 14, WL - 2), (X0 + 8, sy(Ylow(0)) + 2), (X0 + 2, sy(Ylow(0)) + 2)]))
    # --- the water: reflections of the pylons and arch, ripples, ferry and yacht
    o.append(p.line([(-10, WL), (610, WL)], 1.8, 0.3))
    o.append(p.reflect(X0 - 50, X0 + 8, WL + 2, 54, density=0.9, sp=2.8, w=1.3, taper=0.2))
    rf = []
    for s in ss[::2]:
        y0 = WL + (WL - sy(Ylow(s))) * 0.35
        rf.append(f"M{sx(s) - 4:.1f} {y0:.1f}h8")
    o.append(f'<path d="{"".join(rf)}" stroke="{INK}" stroke-width="1.4"/>')
    W1 = 468
    o.append(p.ripples(-10, 610, WL + 4, W1 - 4, 160, hy=WL, lmin=6, lmax=30, wmin=1.0, wmax=1.8))
    # the ferry: double-ended, two decks, wheelhouse each end, a faded green hull
    fx, fy = 360, 446
    hull = [(fx - 92, fy - 10), (fx + 92, fy - 10), (fx + 84, fy + 8), (fx - 84, fy + 8)]
    o.append(p.wash(hull, FERRY, 0.5))
    o.append(p.line(hull, 2.0, 0.2, closed=True))
    o.append(p.hatch([(fx - 88, fy), (fx + 88, fy), (fx + 84, fy + 8), (fx - 84, fy + 8)], 0, 1.8, 1.0, 0.85))
    o.append(p.shape(rect(fx - 84, fy - 28, 168, 18), 1.6) + p.windows(fx - 80, fy - 25, 20, 1, 5, 9, 3.2, 0, w=0.8, dark=1, sill=False))
    o.append(p.shape(rect(fx - 60, fy - 42, 120, 14), 1.4) + p.windows(fx - 56, fy - 39, 14, 1, 5, 7, 3.4, 0, w=0.8, dark=1, sill=False))
    o.append(p.line([(fx - 90, fy - 28), (fx + 90, fy - 28)], 2.2, 0.1) + p.line([(fx - 66, fy - 42), (fx + 66, fy - 42)], 2.0, 0.1))
    for dx in (-52, 52):
        o.append(p.shape(rect(fx + dx - 10, fy - 54, 20, 12), 1.3) + p.solid(rect(fx + dx - 7, fy - 51, 14, 5)))
    o.append(p.shape([(fx - 5, fy - 42), (fx - 4, fy - 62), (fx + 6, fy - 62), (fx + 7, fy - 42)], 1.4) + p.hatch(rect(fx - 4, fy - 62, 10, 6), 0, 1.6, 1.0, 0.9))
    o.append(p.seg(fx + 30, fy - 42, fx + 30, fy - 66, 1.0) + p.shape([(fx + 30, fy - 66), (fx + 42, fy - 64), (fx + 41, fy - 59), (fx + 30, fy - 60)], 0.9))
    for j in range(9):
        o.append(p.person(fx - 70 + j * 17, fy - 28, 9, j % 2))
    o.append(f'<path d="M{fx - 94} {fy - 2}q-30 4 -70 0M{fx - 88} {fy + 8}q-36 10 -96 8M{fx + 92} {fy}q8 2 16 0" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    o.append(p.reflect(fx - 84, fx + 84, fy + 9, 14, density=0.9, sp=2.4, w=1.2, taper=0.1))
    # a yacht heeling in the breeze
    yx, yy = 186, 430
    o.append(p.shape([(yx - 26, yy - 4), (yx + 24, yy - 4), (yx + 18, yy + 4), (yx - 20, yy + 4)], 1.6, fill=INK))
    o.append(p.seg(yx - 2, yy - 4, yx + 6, yy - 74, 1.6))
    o.append(p.shape([(yx + 6, yy - 72), (yx - 1, yy - 8), (yx - 30, yy - 10)], 1.4))
    o.append(p.shape([(yx + 7, yy - 68), (yx + 34, yy - 8), (yx + 2, yy - 8)], 1.4))
    o.append(p.hatch([(yx + 7, yy - 68), (yx + 34, yy - 8), (yx + 2, yy - 8)], 80, 2.8, 1.0, 0.5))
    o.append(p.reflect(yx - 22, yx + 20, yy + 5, 12, density=1, sp=2.4, w=1.2))
    # --- the sandstone sea wall in the foreground, where the name is set
    o.append(p.shape([(-10, W1), (610, W1), (610, 610), (-10, 610)], 2.4))
    o.append(p.line([(-10, W1 + 8), (610, W1 + 8)], 1.4, 0.3))
    blocks = []
    y = W1 + 8
    k = 0
    while y < 600:
        y += 26
        blocks.append(f"M-10 {y:.1f}H610")
        off = 0 if k % 2 else 40
        for x in range(-int(off), 610, 80):
            blocks.append(f"M{x:.1f} {y - 26:.1f}v26")
        k += 1
    o.append(f'<path d="{"".join(blocks)}" stroke="{INK}" stroke-width="1.0" opacity="0.35"/>')
    o.append(p.stipple([(-10, W1 + 8), (610, W1 + 8), (610, 610), (-10, 610)], 220, r=(0.5, 1.0), op=0.5))
    # --- a Moreton Bay fig reaching in from the top left, aerial roots dangling
    o.append(p.branch([(-40, 40), (30, 70), (100, 98), (176, 132), (214, 140)], 34, 8))
    o.append(p.branch([(30, 70), (56, 36), (96, 14)], 16, 6))
    o.append(p.branch([(110, 102), (140, 76), (178, 70)], 12, 4))
    for cx_, cy_, rx, ry in ((10, 20, 100, 56), (120, 40, 70, 40), (190, 104, 56, 32), (60, 96, 50, 28)):
        o.append(p.crown(cx_, cy_, rx, ry, lobes=5, light=(1, -0.6), dense=2.4))
    roots = []
    for x0, y0, L in ((74, 92, 150), (92, 98, 196), (130, 112, 110), (156, 124, 170), (176, 130, 80), (48, 84, 90)):
        sw = rnd.uniform(-8, 8)
        roots.append(f"M{x0} {y0}c{sw:.1f} {L * 0.3:.1f} {-sw:.1f} {L * 0.6:.1f} {sw * 0.5:.1f} {L:.1f}")
    o.append(f'<path d="{"".join(roots)}" fill="none" stroke="{INK}" stroke-width="1.8" stroke-linecap="round"/>')
    # --- title, oversized, straight on the sea wall
    sz = name_size(name, 400, 66, ls=8)
    o.append(f'<rect x="130" y="476" width="340" height="76" fill="{PAPER}"/>')
    o.append(title_text(300, 514, name, sz, ls=8))
    o.append(coord_line(p, 300, 549, coords, 16, 2.2, 30, 12, dots=True))
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- LISBON
def azulejo(p, poly, sp=9.0, op=0.55):
    """Tiled facade: a lattice of diamonds with a dot in each tile, clipped to the wall."""
    x0, y0, x1, y1 = bbox(poly)
    d, dots = [], []
    k = -int((y1 - y0) / sp) - 2
    while k * sp < (x1 - x0) + (y1 - y0):
        a = x0 + k * sp
        d.append(f"M{a:.1f} {y0:.1f}L{a + (y1 - y0):.1f} {y1:.1f}M{a + (y1 - y0):.1f} {y0:.1f}L{a:.1f} {y1:.1f}")
        k += 1
    y = y0 + sp / 2
    r = 0
    while y < y1:
        x = x0 + (sp / 2 if r % 2 else 0)
        while x < x1:
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.1"/>')
            x += sp
        y += sp / 2
        r += 1
    cid = p.uid("az")
    p.defs.append(f'<clipPath id="{cid}"><polygon points="{P(poly)}"/></clipPath>')
    return (f'<g clip-path="url(#{cid})" opacity="{op}"><path d="{"".join(d)}" stroke="{INK}" stroke-width="0.8"/>'
            f'<g fill="{INK}">{"".join(dots)}</g></g>')


@design("lisbon", "Lisbon", "38.7223° N · 9.1393° W")
def lisbon(name, coords):
    """Tram 28 grinding up a steep lane of the Alfama toward us: tiled facades, iron balconies with washing
    strung across, the white dome of Santa Engracia below and the Tagus beyond; drawn as a postage stamp,
    perforations, postmark and all."""
    p = Pen("lisbon", 139)
    rnd = p.rnd
    YEL = "#E9C25A"
    ENV = "#E4D8C2"
    o = [f'<rect width="600" height="600" fill="{ENV}"/>']
    o.append(p.hatch([(0, 0), (600, 0), (600, 600), (0, 600)], 45, 7, 1.0, 0.12))
    # --- the stamp: paper with perforated edges
    S0, S1 = 30, 570
    o.append(f'<rect x="{S0}" y="{S0}" width="{S1 - S0}" height="{S1 - S0}" fill="{PAPER}"/>')
    perf = []
    n = 26
    for i in range(n + 1):
        t = S0 + (S1 - S0) * i / n
        for x, y in ((t, S0), (t, S1), (S0, t), (S1, t)):
            perf.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.4"/>')
    o.append(f'<g fill="{ENV}">' + "".join(perf) + "</g>")
    # --- the art, clipped to the stamp's inner frame
    A0, A1, AB = 52, 548, 462
    art = []
    a = art.append
    a(p.paper(31))
    yF = lambda x: 334 - (x - 300) * 0.32          # far kerb, where the houses stand
    yR = lambda x: yF(x) + 40                      # the rails
    yN = lambda x: yF(x) + 58                      # near kerb
    # --- sky, the Tagus, the far bank and the 25 de Abril bridge
    a(p.hatch([(0, 0), (600, 0), (600, 230), (0, 230)], -2, 6.0, 1.0, 0.35, dash=(12, 46), keep=lambda x, y: max(0, (y - 110) / 120)))
    a(p.clouds(150, 110, 0.7))
    a(p.birds([(240, 140), (256, 132, 0.7), (110, 170, 0.6)], 7))
    bank = smooth([(0, 226), (80, 218), (160, 222), (240, 214), (330, 222)], 4)
    a(p.line(bank, 1.2, 0.3) + p.hatch(bank + [(330, 234), (0, 234)], 10, 2.6, 1.0, 0.5))
    a(p.line([(0, 236), (330, 236)], 1.4, 0.2))
    for tx in (70, 150):
        a(p.seg(tx - 2, 236, tx - 2, 190, 1.6) + p.seg(tx + 2, 236, tx + 2, 190, 1.6) + p.seg(tx - 3, 198, tx + 3, 198, 1.0) + p.seg(tx - 3, 214, tx + 3, 214, 1.0))
    a(f'<path d="M0 214Q35 226 70 191Q110 226 150 191Q185 226 220 212" fill="none" stroke="{INK}" stroke-width="1.2"/>')
    a(p.line([(0, 224), (240, 224)], 1.8, 0.1))
    a(p.ripples(0, 330, 238, 266, 50, hy=236, lmin=4, lmax=12, wmin=1.0, wmax=1.2))
    a(p.shape([(30, 252), (80, 252), (86, 246), (24, 246)], 1.2) + p.shape(rect(46, 238, 20, 8), 1.0))
    # --- the lower Alfama falling to the river, the dome of Santa Engracia
    rnd2 = random.Random(5)
    for i in range(18):
        x0 = rnd2.uniform(-10, 230)
        w = rnd2.uniform(22, 40)
        top = rnd2.uniform(262, 330) + (x0 - 100) * 0.12
        a(p.shape([(x0, 440), (x0, top), (x0 + w / 2, top - 9), (x0 + w, top), (x0 + w, 440)], 1.1))
        a(p.hatch([(x0, top), (x0 + w / 2, top - 9), (x0 + w, top)], 20, 2.0, 1.0, 0.7))
        a(p.windows(x0 + 4, top + 5, max(1, int((w - 6) / 8)), 3, 3.5, 5, 4.5, 6, w=0.8, dark=0.7, sill=False))
    dx = 128
    a(p.shape(rect(dx - 30, 268, 60, 40), 1.4) + p.windows(dx - 24, 276, 5, 2, 5, 8, 5.5, 5, w=0.8, dark=0.8, arch=True, sill=False))
    a(p.shape(rect(dx - 20, 252, 40, 16), 1.3) + "".join(p.seg(dx - 17 + k * 5.7, 254, dx - 17 + k * 5.7, 266, 0.9) for k in range(7)))
    dm = arc_pts(dx, 252, 22, 24, 180, 360, 14)
    a(p.shape(dm + [(dx + 22, 252)], 1.6) + p.hatch(dm, 80, 2.2, 1.0, 0.7, keep=lambda x, y: max(0, (x - dx) / 20)))
    a(p.shape(rect(dx - 4, 220, 8, 8), 1.0) + p.seg(dx, 220, dx, 212, 1.1))
    # --- the houses climbing the hill on the far side of the street
    x = 176
    while x < 620:
        w = rnd.uniform(56, 82)
        x0, x1 = x, x + w
        floors = rnd.randint(3, 4)
        fh = 40
        top = yF(x0) - floors * fh - 16
        wall = [(x0, yF(x0)), (x0, top), (x1, top), (x1, yF(x1))]
        a(p.shape(wall, 1.8))
        if rnd.random() < 0.55:
            a(azulejo(p, wall, sp=8, op=0.45))
        else:
            a(p.stipple(wall, 160, r=(0.5, 0.9), op=0.6))
        a(p.line([(x0 - 3, top), (x1 + 3, top)], 2.4, 0.1))
        eave = [(x0 - 4, top), (x0 + 4, top - 12), (x1 - 4, top - 12), (x1 + 4, top)]
        a(p.shape(eave, 1.4) + p.hatch(eave, 20, 2.2, 1.0, 0.8))
        cols = max(2, int(w / 26))
        for fl in range(floors):
            wy = top + 14 + fl * fh
            for c in range(cols):
                wx = x0 + (c + 0.5) * w / cols - 7
                if fl == floors - 1 and c == 0:
                    # the street door, its sill on the slope
                    a(p.shape([(wx, yF(wx)), (wx, wy - 4), (wx + 14, wy - 4), (wx + 14, yF(wx + 14))], 1.4, fill=INK))
                    continue
                a(p.shape(rect(wx, wy, 14, 24), 1.3, fill=INK))
                a(p.seg(wx + 7, wy + 2, wx + 7, wy + 22, 0.9).replace(INK, PAPER))
                if fl < floors - 1 and rnd.random() < 0.7:
                    a(p.shape(rect(wx - 4, wy + 24, 22, 3), 1.2))
                    a(f'<path d="{"".join(f"M{wx - 3 + k * 3:.1f} {wy + 24:.1f}v-9" for k in range(8))}" stroke="{INK}" stroke-width="0.9"/>'
                      + p.line([(wx - 4, wy + 15), (wx + 18, wy + 15)], 1.3, 0.1))
                    if rnd.random() < 0.35:
                        a(p.foliage(wx + 7, wy + 12, 9, 5, w=1.1, shade=0.6, bump=2.5, inner=0.5))
        if rnd.random() < 0.7:          # washing strung between two windows
            ly = top + 14 + 40 * rnd.randint(0, floors - 2) + 22
            a(p.laundry(x0 + 6, ly, x1 - 6, ly + 2, 3, 3, 1.1, scale=1.1))
        x = x1
    # --- the street: cobbles, rails, kerbs, the overhead wire
    street = [(-10, yF(-10)), (610, yF(610)), (610, yN(610)), (-10, yN(-10))]
    a(p.solid(street, PAPER))
    a(p.stipple(street, 260, r=(0.5, 1.0)))
    a(p.line([(-10, yF(-10)), (610, yF(610))], 2.0, 0.3))
    for off in (34, 46):
        a(p.line([(-10, yF(-10) + off), (610, yF(610) + off)], 1.6, 0.2))
    for x in range(-10, 610, 18):
        a(p.seg(x, yF(x) + 32, x + 3, yF(x + 3) + 48, 1.0, 0.0, op=0.6))
    a(p.line([(-10, yF(-10) - 150), (610, yF(610) - 150)], 1.2, 0.2))
    # --- Tram 28 climbing: yellow wooden body (the accent), white upper band, trolley pole to the wire
    T0, T1 = 236, 452
    bot = lambda x: yR(x) - 6
    TH = 96
    body = [(T0, bot(T0)), (T0 + 6, bot(T0) - TH), (T1 - 6, bot(T1) - TH), (T1, bot(T1))]
    a(p.wash(body, YEL, 0.6))
    a(p.line(body, 2.4, 0.2, closed=True))
    roof = [(T0 + 6, bot(T0) - TH), (T0 + 14, bot(T0) - TH - 8), (T1 - 14, bot(T1) - TH - 8), (T1 - 6, bot(T1) - TH)]
    a(p.shape(roof, 1.8) + p.hatch(roof, -18, 2.0, 1.0, 0.7))
    band = [(T0 + 4, bot(T0) - TH + 4), (T0 + 4, bot(T0) - TH + 14), (T1 - 4, bot(T1) - TH + 14), (T1 - 4, bot(T1) - TH + 4)]
    a(p.solid(band, PAPER) + p.line(band, 1.2, 0.1, closed=True))
    # windows: a row of tilted panes following the slope
    for k in range(8):
        wx = T0 + 22 + k * 23
        wy = bot(wx) - TH + 20
        a(p.solid([(wx, wy), (wx, wy + 32), (wx + 17, wy + 32 - 17 * 0.32), (wx + 17, wy - 17 * 0.32)]))
        if k in (2, 5):
            a(f'<circle cx="{wx + 9:.1f}" cy="{wy + 14:.1f}" r="4.4" fill="{PAPER}"/><path d="M{wx + 2:.1f} {wy + 30:.1f}q7 -10 14 -2" fill="{PAPER}"/>')
    # door, number board, headlamp, fender, skirt
    a(p.line([(T0 + 4, bot(T0) - 40), (T1 - 4, bot(T1) - 40)], 1.6, 0.1))
    dx0 = T1 - 36
    a(p.shape([(dx0, bot(dx0) - 6), (dx0, bot(dx0) - 62), (dx0 + 20, bot(dx0 + 20) - 62), (dx0 + 20, bot(dx0 + 20) - 6)], 1.4))
    a(p.solid([(dx0 + 3, bot(dx0 + 3) - 56), (dx0 + 3, bot(dx0 + 3) - 34), (dx0 + 17, bot(dx0 + 17) - 34), (dx0 + 17, bot(dx0 + 17) - 56)]))
    nb = (T1 - 22, bot(T1 - 22) - TH - 18)
    a(p.shape(rect(nb[0] - 16, nb[1] - 9, 32, 18), 1.4, fill=INK))
    a(f'<text x="{nb[0]:.1f}" y="{nb[1] + 6:.1f}" text-anchor="middle" {MONO} font-size="16" fill="{PAPER}">28</text>')
    a(f'<circle cx="{T1 + 2:.1f}" cy="{bot(T1) - 22:.1f}" r="5" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>')
    a(p.solid([(T0 - 4, bot(T0)), (T1 + 6, bot(T1)), (T1 + 6, bot(T1) + 8), (T0 - 4, bot(T0) + 8)]))
    a(p.hatch([(T0, bot(T0) - 38), (T1, bot(T1) - 38), (T1, bot(T1)), (T0, bot(T0))], 90, 3.2, 1.0, 0.45))
    pole0 = (T0 + 60, bot(T0 + 60) - TH - 8)
    pole1 = (T0 + 170, yF(T0 + 170) - 150)
    a(p.line([pole0, pole1], 2.0, 0.1) + f'<circle cx="{pole1[0]:.1f}" cy="{pole1[1]:.1f}" r="2.6" fill="{INK}"/>')
    # a boy hitching a ride on the back step
    a(p.walker(T0 - 8, bot(T0) + 4, 52, "child", flip=True, stride=0.2))
    # --- the near pavement: calcada in black-and-white waves, a lamp, people walking up
    pav = [(-10, yN(-10)), (610, yN(610)), (610, 470), (-10, 470)]
    a(p.solid(pav, PAPER))
    a(p.line([(-10, yN(-10)), (610, yN(610))], 2.2, 0.3))
    waves = []
    for j in range(16):
        off = 10 + j * 9
        waves.append("M-10 " + f"{yN(-10) + off:.1f}" + "".join(f"Q{x + 15:.1f} {yN(x + 15) + off + (6 if (x // 30) % 2 else -6):.1f} {x + 30:.1f} {yN(x + 30) + off:.1f}" for x in range(-10, 620, 30)))
    cid = p.uid("pv")
    p.defs.append(f'<clipPath id="{cid}"><polygon points="{P(pav)}"/></clipPath>')
    a(f'<path d="{"".join(waves)}" fill="none" stroke="{INK}" stroke-width="3.2" opacity="0.8" clip-path="url(#{cid})"/>')
    a(p.lamp(110, yN(110) + 6, 120, w=2.0))
    a(p.walker(176, yN(176) + 14, 74, "woman", flip=False, stride=0.3, bag=True))
    a(p.walker(520, yN(520) + 16, 80, "man", flip=True, stride=-0.4, hat=True))
    # title band at the bottom of the stamp
    a(p.solid([(0, AB), (600, AB), (600, 600), (0, 600)], PAPER))
    o.append(p.clip(f'<rect x="{A0}" y="{A0}" width="{A1 - A0}" height="{A1 - A0}"/>', "".join(art)))
    o.append(p.line(rect(A0, A0, A1 - A0, A1 - A0), 2.4, 0.2, closed=True))
    o.append(p.line([(A0, AB), (A1, AB)], 2.0, 0.2))
    sz = name_size(name, 380, 52, ls=6)
    o.append(title_text(300, 508, name, sz, ls=6))
    o.append(coord_line(p, 300, 534, coords, 16, 2.0, 26, 10))
    # the postmark: a double ring and wavy cancellation lines across the top-right corner
    pmx, pmy = 470, 112
    o.append(f'<g opacity="0.55"><circle cx="{pmx}" cy="{pmy}" r="40" fill="none" stroke="{INK}" stroke-width="2"/>'
             f'<circle cx="{pmx}" cy="{pmy}" r="32" fill="none" stroke="{INK}" stroke-width="1.2"/>'
             f'<path d="M{pmx - 22} {pmy}h44M{pmx - 18} {pmy - 9}h36M{pmx - 18} {pmy + 9}h36" stroke="{INK}" stroke-width="1.6"/>'
             + "".join(f'<path d="M{pmx - 150} {pmy - 24 + j * 12}q14 -7 28 0t28 0t28 0t28 0t28 0" fill="none" stroke="{INK}" stroke-width="1.6"/>' for j in range(5))
             + "</g>")
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- EDINBURGH
def scott_monument(p, cx, base, h, lw=1.4):
    """The Scott Monument: a soaring Gothic spire of four open arches, stacked galleries bristling with
    pinnacles, tapering to a needle; inked dark (the sandstone is famously sooty)."""
    out = []
    w0 = h * 0.26
    stages = [(0.0, 0.32, 1.0), (0.32, 0.5, 0.78), (0.5, 0.64, 0.6), (0.64, 0.76, 0.45), (0.76, 0.86, 0.32)]
    for a_, b_, k in stages:
        y0, y1 = base - h * a_, base - h * b_
        hw = w0 / 2 * k
        hw2 = w0 / 2 * (k - 0.1)
        poly = [(cx - hw, y0), (cx - hw2, y1), (cx + hw2, y1), (cx + hw, y0)]
        out.append(p.solid(poly))
        # open arch in the middle of the lowest stages
        if a_ < 0.5:
            ah = (y0 - y1) * 0.62
            out.append(p.solid([(cx - hw * 0.4, y0), (cx - hw * 0.4, y0 - ah * 0.7), (cx, y0 - ah), (cx + hw * 0.4, y0 - ah * 0.7), (cx + hw * 0.4, y0)], PAPER))
            out.append(p.line([(cx - hw * 0.4, y0), (cx - hw * 0.4, y0 - ah * 0.7), (cx, y0 - ah), (cx + hw * 0.4, y0 - ah * 0.7), (cx + hw * 0.4, y0)], 1.0, 0.1))
        # pinnacles at the corners of each gallery
        for s in (-1, 1):
            px_ = cx + s * hw2
            out.append(p.solid([(px_ - 2.2, y1 + 2), (px_, y1 - h * 0.06), (px_ + 2.2, y1 + 2)]))
        out.append(p.line([(cx - hw2 - 3, y1), (cx + hw2 + 3, y1)], 1.6, 0.1).replace(INK, INK))
        # paper tracery lines picked out
        out.append(f'<path d="M{cx - hw * 0.75:.1f} {y0:.1f}L{cx - hw2 * 0.75:.1f} {y1 + 3:.1f}M{cx + hw * 0.75:.1f} {y0:.1f}L{cx + hw2 * 0.75:.1f} {y1 + 3:.1f}" stroke="{PAPER}" stroke-width="0.8" opacity="0.7"/>')
    ytop = base - h * 0.86
    out.append(p.solid([(cx - w0 * 0.12, ytop), (cx, base - h), (cx + w0 * 0.12, ytop)]))
    return "".join(out)


@design("edinburgh", "Edinburgh", "55.9533° N · 3.1883° W")
def edinburgh(name, coords):
    """From Calton Hill at the end of the day: the Dugald Stewart Monument's ring of columns in the foreground,
    and over the roofs the Balmoral clock tower, the Scott Monument's spire, the Old Town's crown of spires
    and the Castle on its rock; heather and a couple on the grass."""
    p = Pen("edinburgh", 149)
    rnd = p.rnd
    o = [p.paper(33)]
    H = 330
    # --- big northern sky: banked clouds lit from below, and gulls
    for cx_, cy_, s in ((420, 120, 1.1), (520, 160, 0.8), (150, 190, 0.7)):
        o.append(p.clouds(cx_, cy_, s, 1.6))
    o.append(p.hatch([(0, 200), (600, 200), (600, H), (0, H)], -2, 5.4, 1.0, 0.4, dash=(12, 44), keep=lambda x, y: max(0, (y - 210) / 120)))
    o.append(p.birds([(330, 80), (348, 72, 0.7), (250, 150, 0.6), (70, 160, 0.6)], 7))
    o.append('<g transform="translate(-30 64) scale(1.1)">')
    # --- the Castle on its rock (left, far), Old Town spires along the ridge
    rock = smooth([(-10, 300), (20, 270), (60, 252), (110, 246), (150, 262), (180, 290), (200, 312)], 6)
    o.append(p.solid(rock + [(200, H + 10), (-10, H + 10)], PAPER))
    o.append(p.line(rock, 1.6, 0.3))
    # crags: vertical fall-line strokes, dark in the clefts, trees at the foot
    crag = []
    for _ in range(260):
        xx = rnd.uniform(0, 196)
        top_y = min(y for (x_, y) in rock if abs(x_ - xx) < 6) if any(abs(x_ - xx) < 6 for x_, _ in rock) else 280
        L = rnd.uniform(8, 40)
        y0 = top_y + rnd.uniform(2, 50)
        crag.append(f"M{xx:.1f} {y0:.1f}l{rnd.uniform(-2, 2):.1f} {L:.1f}")
    cid = p.uid("rk")
    p.defs.append(f'<clipPath id="{cid}"><polygon points="{P(rock + [(200, H + 10), (-10, H + 10)])}"/></clipPath>')
    o.append(f'<path d="{"".join(crag)}" stroke="{INK}" stroke-width="1.2" clip-path="url(#{cid})"/>')
    o.append(p.hatch(rock + [(200, H + 10), (-10, H + 10)], 100, 3.4, 1.0, 0.5))
    for x in range(-10, 200, 20):
        o.append(p.lobe(x + rnd.uniform(-5, 5), H + rnd.uniform(-8, 2), rnd.uniform(12, 18), rnd.uniform(8, 11), light=(-1, -0.6), w=1.1, dense=1.8))
    # castle buildings on top
    for x0, w, h in ((30, 40, 22), (68, 30, 34), (98, 46, 26), (142, 24, 16)):
        top = 250 - h + (0 if x0 < 140 else 10)
        o.append(p.shape(rect(x0, top, w, h + 4), 1.3) + p.windows(x0 + 4, top + 5, int((w - 6) / 7), 2, 3, 5, 4, 4, w=0.8, dark=0.8, sill=False))
        o.append(f'<path d="{"".join(f"M{x:.1f} {top:.1f}v-3h3v3" for x in range(int(x0), int(x0 + w), 6))}" stroke="{INK}" stroke-width="1" fill="none"/>')
        o.append(p.hatch(rect(x0 + w * 0.6, top, w * 0.4, h + 4), 90, 2.0, 1.0, 0.6))
    o.append(p.seg(80, 216, 80, 200, 1.1) + p.shape([(80, 200), (92, 202), (91, 207), (80, 206)], 0.9))
    # Old Town ridge: tenements and spires running down from the castle
    ridge_top = lambda x: 286 + (x - 200) * 0.06
    x = 196
    while x < 400:
        w = rnd.uniform(14, 26)
        h = rnd.uniform(14, 34)
        top = ridge_top(x) - h
        o.append(p.shape(rect(x, top, w, H - top), 1.1) + p.hatch(rect(x + w * 0.6, top, w * 0.4, H - top), 90, 2.0, 1.0, 0.6))
        o.append(p.windows(x + 3, top + 4, max(1, int((w - 4) / 6)), 3, 2.5, 4, 3.5, 4, w=0.7, dark=0.8, sill=False))
        x += w
    # the Hub's spire (Tolbooth Kirk) and St Giles' crown
    o.append(p.shape(rect(232, 230, 16, 50), 1.3) + p.shape([(230, 230), (240, 170), (250, 230)], 1.3) + p.hatch([(240, 170), (250, 230), (240, 230)], 80, 1.6, 1.0, 0.85))
    o.append(p.shape(rect(328, 248, 18, 40), 1.3))
    o.append(f'<path d="M326 248q11 -26 22 0M330 248q7 -16 14 0M337 222v-8" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    # --- the New Town: the Balmoral clock tower and the Scott Monument on Princes Street
    o.append(p.shape(rect(400, 262, 70, H - 262), 1.5) + p.windows(406, 270, 6, 4, 5, 7, 5.8, 6, w=0.8, dark=0.7, sill=False))
    bx = 452
    o.append(p.shape(rect(bx - 11, 186, 22, 80), 1.6) + p.hatch(rect(bx + 1, 186, 10, 80), 90, 1.8, 1.0, 0.8))
    o.append(f'<circle cx="{bx}" cy="200" r="7" fill="{PAPER}" stroke="{INK}" stroke-width="1.4"/><path d="M{bx} 200v-4M{bx} 200l3 1" stroke="{INK}" stroke-width="1.1"/>')
    o.append(p.shape([(bx - 13, 186), (bx - 9, 172), (bx, 164), (bx + 9, 172), (bx + 13, 186)], 1.5) + p.hatch([(bx, 164), (bx + 9, 172), (bx + 13, 186), (bx, 186)], 80, 1.8, 1.0, 0.8))
    o.append(p.seg(bx, 164, bx, 150, 1.3) + f'<circle cx="{bx}" cy="160" r="2" fill="{INK}"/>')
    for sgn in (-1, 1):
        o.append(p.solid([(bx + sgn * 11 - 2, 188), (bx + sgn * 11, 176), (bx + sgn * 11 + 2, 188)]))
    o.append(scott_monument(p, 372, 300, 150))
    # trees of Princes Street Gardens along the valley
    for x in range(180, 520, 26):
        o.append(p.lobe(x + rnd.uniform(-6, 6), H - 2 + rnd.uniform(-4, 4), rnd.uniform(14, 20), rnd.uniform(9, 12), light=(-1, -0.6), w=1.2, dense=1.6))
    o.append('</g>')
    # --- Calton Hill's grassy brow in the foreground: gorse, a path, the couple on the grass
    brow = smooth([(-10, 452), (120, 440), (260, 446), (380, 462), (470, 476), (610, 486)], 6)
    bpoly = brow + [(610, 610), (-10, 610)]
    o.append(p.solid(bpoly, PAPER))
    o.append(p.line(brow, 2.2, 0.3))
    o.append(p.grass(-10, 610, 600, 140, (4, 12), 1.2))
    gt = []
    for _ in range(320):
        xx = rnd.uniform(-10, 610)
        yy = rnd.uniform(450, 600)
        if yy < 440 + (xx + 10) * 0.07 + 8:
            continue
        gt.append(f"M{xx:.1f} {yy:.1f}l{rnd.uniform(-1.5, 1.5):.1f} {-rnd.uniform(3, 8):.1f}")
    o.append(f'<path d="{"".join(gt)}" stroke="{INK}" stroke-width="1.1" opacity="0.7"/>')
    for gx, gy, r in ((40, 470, 30), (96, 488, 22), (300, 488, 22)):
        o.append(p.lobe(gx, gy, r, r * 0.55, light=(-1, -0.8), w=1.3, dense=2.0))
        o.append("".join(f'<circle cx="{gx + rnd.uniform(-r, r) * 0.8:.1f}" cy="{gy + rnd.uniform(-r, r) * 0.35:.1f}" r="1.6" fill="{PAPER}" stroke="{INK}" stroke-width="0.9"/>' for _ in range(8)))
    # a gravel path curving up to the monument, a dog walker on it
    pl = smooth([(60, 610), (150, 560), (260, 530), (380, 520)], 8)
    pr = smooth([(150, 610), (220, 572), (300, 548), (396, 540)], 8)
    o.append(p.solid(pl + pr[::-1], PAPER))
    o.append(p.line(pl, 1.6, 0.3) + p.line(pr, 1.6, 0.3))
    o.append(p.stipple(pl + pr[::-1], 160, r=(0.5, 1.1)))
    o.append(p.walker(262, 546, 56, "man", flip=True, stride=0.4, hat=True))
    o.append(f'<path d="M224 548l2 -8q-2 -5 4 -6h10q3 0 5 -3l2 -4l3 2v4q3 2 1 5h-3l-3 4l1 6h-2l-2 -5h-8l-2 5h-2v-5q-3 0 -4 5Z" fill="{INK}"/>'
             f'<path d="M248 518q-8 10 -10 18" fill="none" stroke="{INK}" stroke-width="1"/>')
    # the couple sitting on the grass, looking out
    cx_, cy_ = 170, 478
    o.append(f'<path d="M{cx_ - 10} {cy_}q-2 -16 4 -26q6 -4 10 0q4 10 2 26Z" fill="{INK}"/><circle cx="{cx_ - 1}" cy="{cy_ - 32}" r="5.5" fill="{INK}"/>'
             f'<path d="M{cx_ + 6} {cy_}q-1 -14 4 -22q6 -4 9 0q3 8 2 22Z" fill="{INK}"/><circle cx="{cx_ + 13}" cy="{cy_ - 28}" r="5" fill="{INK}"/>'
             f'<path d="M{cx_ - 14} {cy_}h36" stroke="{INK}" stroke-width="2"/>')
    # --- the Dugald Stewart Monument: podium, nine Corinthian columns, entablature, drum and dome
    mx, mb = 478, 566
    R = 84
    pod = [(mx - R - 14, mb), (mx - R - 14, mb - 34), (mx + R + 14, mb - 34), (mx + R + 14, mb)]
    o.append(p.shape(pod, 2.4))
    o.append(p.hatch([(mx + 20, mb - 34), (mx + R + 14, mb - 34), (mx + R + 14, mb), (mx + 20, mb)], 90, 2.4, 1.0, 0.75))
    o.append(p.line([(mx - R - 18, mb - 34), (mx + R + 18, mb - 34)], 3.0, 0.1) + p.line([(mx - R - 14, mb - 8), (mx + R + 14, mb - 8)], 1.4, 0.1))
    o.append(brick_courses(p, pod, 8, 0.9, 0.4, 26))
    ct, cbm = mb - 168, mb - 36
    # back of the ring: the inner wall in shadow
    o.append(p.solid(rect(mx - R + 10, ct + 8, 2 * R - 20, cbm - ct - 8), INK, 0.85))
    for k in range(9):
        t = math.pi * (k + 0.5) / 9
        x = mx - R * math.cos(t)
        cw = 8 + 6 * math.sin(t)
        col = rect(x - cw / 2, ct + 10, cw, cbm - ct - 10)
        o.append(p.shape(col, 1.6))
        o.append(p.hatch(rect(x + cw * 0.05, ct + 10, cw * 0.45, cbm - ct - 10), 90, 1.6, 1.0, 0.9))
        for j in range(1, 3):
            o.append(p.seg(x - cw / 2 + j * cw / 3, ct + 14, x - cw / 2 + j * cw / 3, cbm - 4, 0.8, 0.0, op=0.8))
        cap = [(x - cw / 2 - 3, ct + 10), (x - cw / 2, ct + 18), (x + cw / 2, ct + 18), (x + cw / 2 + 3, ct + 10)]
        o.append(p.shape(cap, 1.2) + p.stipple(cap, 8, r=(0.6, 1.0)))
        o.append(p.shape(rect(x - cw / 2 - 2, cbm - 4, cw + 4, 4), 1.1))
    ent = [(mx - R - 8, ct + 10), (mx - R - 8, ct - 6), (mx + R + 8, ct - 6), (mx + R + 8, ct + 10)]
    o.append(p.shape(ent, 2.2) + p.line([(mx - R - 10, ct - 6), (mx + R + 10, ct - 6)], 3.0, 0.1))
    o.append(f'<path d="{"".join(f"M{x} {ct - 2}v4" for x in range(int(mx - R - 6), int(mx + R + 8), 5))}" stroke="{INK}" stroke-width="1.2"/>')
    o.append(p.hatch([(mx + 20, ct - 6), (mx + R + 8, ct - 6), (mx + R + 8, ct + 10), (mx + 20, ct + 10)], 90, 2.2, 1.0, 0.7))
    drum = rect(mx - R * 0.62, ct - 34, R * 1.24, 28)
    o.append(p.shape(drum, 2.0) + p.hatch(rect(mx + 10, ct - 34, R * 0.62 - 10, 28), 90, 2.2, 1.0, 0.7))
    dmp = arc_pts(mx, ct - 34, R * 0.62, 26, 180, 360, 16)
    o.append(p.shape(dmp + [(mx + R * 0.62, ct - 34)], 2.0) + p.hatch(dmp, 75, 2.2, 1.0, 0.8, keep=lambda x, y: max(0, (x - mx + 4) / 30)))
    o.append(p.shape([(mx - 6, ct - 60), (mx - 4, ct - 74), (mx, ct - 80), (mx + 4, ct - 74), (mx + 6, ct - 60)], 1.4))
    # --- title in a ruled square cartouche in the sky, top left
    x0, y0, x1, y1 = 62, 66, 314, 152
    o.append(cartouche(p, x0, y0, x1, y1, 10, 2.4))
    sz = name_size(name, x1 - x0 - 34, 44)
    o.append(title_text((x0 + x1) / 2, 112, name, sz))
    o.append(title_text((x0 + x1) / 2, 136, coords, fit_size(coords, MONO, 16, x1 - x0 - 16, 0.4), MONO, ls=0.4))
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- HAVANA
def splash(p, x, y, h, w):
    """A wave bursting over the sea wall: a white plume of spray fanning up and toppling seaward, its edge drawn
    in broken curls, droplets flung wide in stipple."""
    rnd = p.rnd
    d = []
    for k in range(30):
        a = math.radians(rnd.uniform(-60, 30))
        L = h * rnd.uniform(0.4, 1.0)
        sx = x + rnd.uniform(-w * 0.4, w * 0.4)
        ex, ey = sx + L * math.sin(a) * 0.8, y - L * math.cos(a)
        d.append(f"M{sx:.1f} {y:.1f}Q{sx + (ex - sx) * 0.2:.1f} {y - L * 0.7:.1f} {ex:.1f} {ey:.1f}")
        if rnd.random() < 0.5:
            d.append(f"M{ex:.1f} {ey:.1f}q{-4:.1f} {-3:.1f} {-7:.1f} {2:.1f}")
    out = [f'<path d="{"".join(d)}" fill="none" stroke="{INK}" stroke-width="1.0" stroke-linecap="round" stroke-dasharray="6 2"/>']
    dots = []
    for _ in range(220):
        a = rnd.uniform(-1.3, 0.8)
        r = rnd.uniform(0.3, 1.25) * h
        dots.append(f'<circle cx="{x + math.sin(a) * r * 0.8:.1f}" cy="{y - math.cos(a) * r:.1f}" r="{rnd.uniform(0.5, 1.5):.1f}"/>')
    out.append(f'<g fill="{INK}">' + "".join(dots) + "</g>")
    return "".join(out)


def classic_car(p, C, X, Z, Y0=0.0, wash=None):
    """A 1950s American sedan coming toward us: wide chrome grille, round headlamps, wraparound windscreen,
    rounded roof, tail fins just visible, seen in perspective (front face and left flank)."""
    W, L, Hb, Hr = 2.0, 5.2, 0.95, 1.5
    f = lambda x, y, z: C(X + x, Y0 + y, Z + z)
    out = []
    side = [f(-W / 2, 0.25, 0), f(-W / 2, Hb, 0), f(-W / 2, Hb, L), f(-W / 2, 0.25, L)]
    front = [f(-W / 2, 0.25, 0), f(-W / 2, Hb, 0), f(W / 2, Hb, 0), f(W / 2, 0.25, 0)]
    hood = [f(-W / 2, Hb, 0), f(-W / 2, Hb, 1.5), f(W / 2, Hb, 1.5), f(W / 2, Hb, 0)]
    cab = [f(-W / 2 + 0.15, Hb, 1.5), f(-W / 2 + 0.3, Hr, 2.0), f(W / 2 - 0.3, Hr, 2.0), f(W / 2 - 0.15, Hb, 1.5)]
    cabs = [f(-W / 2 + 0.15, Hb, 1.5), f(-W / 2 + 0.3, Hr, 2.0), f(-W / 2 + 0.3, Hr, 3.6), f(-W / 2 + 0.15, Hb, 4.2)]
    roof = [f(-W / 2 + 0.3, Hr, 2.0), f(-W / 2 + 0.3, Hr, 3.6), f(W / 2 - 0.3, Hr, 3.6), f(W / 2 - 0.3, Hr, 2.0)]
    if wash:
        for poly in (side, front, hood, cabs):
            out.append(p.solid(poly, wash, 0.55))
    for poly, w in ((side, 1.8), (cabs, 1.6), (roof, 1.6), (hood, 1.6), (front, 2.0), (cab, 1.6)):
        out.append(p.line(poly, w, 0.2, closed=True))
    out.append(p.solid([lerp(cab[0], cab[1], 0.1), lerp(cab[1], cab[2], 0.05), lerp(cab[2], cab[1], 0.05), lerp(cab[3], cab[2], 0.1)]))
    out.append(p.solid([lerp(cabs[0], cabs[1], 0.2), cabs[1], lerp(cabs[1], cabs[2], 0.45), lerp(cabs[0], cabs[3], 0.45)]))
    out.append(p.solid([lerp(cabs[1], cabs[2], 0.52), cabs[2], lerp(cabs[3], cabs[2], 0.2), lerp(cabs[0], cabs[3], 0.52)]))
    out.append(p.line([f(-W / 2, 0.6, 0.1), f(-W / 2, 0.75, L * 0.9)], 1.2, 0.1))           # chrome side trim
    out.append(p.hatch(side, 0, 2.2, 1.0, 0.5))
    # grille, bumper, headlamps
    g = [f(-0.55, 0.4, -0.02), f(-0.55, 0.75, -0.02), f(0.55, 0.75, -0.02), f(0.55, 0.4, -0.02)]
    out.append(p.solid(g))
    gx = "".join(f"M{lerp(g[0], g[3], t)[0]:.1f} {lerp(g[0], g[3], t)[1]:.1f}L{lerp(g[1], g[2], t)[0]:.1f} {lerp(g[1], g[2], t)[1]:.1f}" for t in [k / 8 for k in range(1, 8)])
    out.append(f'<path d="{gx}" stroke="{PAPER}" stroke-width="1"/>')
    out.append(p.line([f(-W / 2 - 0.05, 0.3, -0.1), f(W / 2 + 0.05, 0.3, -0.1)], 3.0, 0.1))
    for s in (-1, 1):
        c = f(s * 0.75, 0.68, -0.02)
        r = 800 * 0.16 / Z
        out.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{r:.1f}" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>'
                   f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{r * 0.4:.1f}" fill="{INK}"/>')
    # wheels
    for z in (0.9, L - 0.9):
        c = f(-W / 2 - 0.02, 0.33, z)
        out.append(f'<ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="{800 * 0.14 / (Z + z):.1f}" ry="{800 * 0.33 / (Z + z):.1f}" fill="{INK}"/>')
    # the fin
    out.append(p.solid([f(-W / 2, Hb, L - 1.0), f(-W / 2, Hb + 0.28, L - 0.1), f(-W / 2, Hb, L)]))
    return "".join(out)


@design("havana", "Havana", "23.1136° N · 82.3666° W")
def havana(name, coords):
    """From a balcony high over the Malecon: the sea wall curving away toward the harbour mouth and El Morro's
    lighthouse, waves bursting over it, fifties cars cruising the boulevard, friends on the wall, and on our
    own wrought-iron balcony a canary in its cage and a cafecito on the rail."""
    p = Pen("havana", 151)
    rnd = p.rnd
    TEAL = "#7FC1B9"
    C = Cam(f=430, cx=330, vpy=214, eye=26)
    cv = lambda Z: 0.0026 * Z * Z                        # the boulevard bends right as it runs east
    W = lambda X, Y, Z: C(X + cv(Z), Y, Z)
    o = [p.paper(35, vignette=0.4, blotch=6)]
    # --- sky: tall clouds, gulls
    o.append(p.clouds(380, 160, 0.6, 1.4) + p.clouds(104, 176, 0.55))
    o.append(p.birds([(250, 150), (266, 142, 0.7), (420, 120, 0.6), (330, 186, 0.6)], 7))
    # --- across the harbour mouth: La Cabana's walls and El Morro with its lighthouse
    far = smooth([(-10, 210), (60, 204), (130, 200), (200, 202), (250, 206), (280, 214)], 6)
    o.append(p.solid(far + [(280, 216), (-10, 216)], PAPER) + p.line(far, 1.2, 0.2))
    o.append(p.hatch(far + [(280, 216), (-10, 216)], 75, 2.4, 1.0, 0.6))
    o.append(p.shape([(150, 202), (154, 188), (250, 188), (256, 206)], 1.3) + p.hatch([(150, 202), (154, 188), (250, 188), (256, 206)], 80, 2.6, 1.0, 0.5))
    o.append(f'<path d="{"".join(f"M{x} 188v-3h3v3" for x in range(156, 250, 6))}" stroke="{INK}" stroke-width="0.9" fill="none"/>')
    lx = 232
    o.append(p.shape([(lx - 6, 188), (lx - 5, 152), (lx + 5, 152), (lx + 6, 188)], 1.5) + p.hatch([(lx + 1, 152), (lx + 5, 152), (lx + 6, 188), (lx + 1, 188)], 90, 1.6, 1.0, 0.85))
    o.append(p.line([(lx - 8, 152), (lx + 8, 152)], 1.8, 0.1) + p.shape(rect(lx - 4, 143, 8, 9), 1.2) + p.solid(rect(lx - 2.5, 145, 5, 5)))
    o.append(p.shape(arc_pts(lx, 143, 5, 4, 180, 360, 8), 1.1) + p.seg(lx, 139, lx, 135, 1.0))
    for k in range(5):
        a_ = math.radians(-34 + k * 14)
        o.append(p.seg(lx + 9 * math.cos(a_), 147 + 9 * math.sin(a_), lx + 24 * math.cos(a_), 147 + 24 * math.sin(a_), 1.0, 0.0, op=0.6))
    for x0, w, h in ((-10, 40, 10), (30, 26, 14), (60, 34, 8)):
        o.append(p.shape(rect(x0, 204 - h, w, h), 1.0) + p.hatch(rect(x0, 204 - h, w, h), 80, 2.6, 1.0, 0.5))
    # --- inland: the Capitolio dome over a sea of flat roofs, water tanks and a church tower
    cx_ = 520
    o.append(p.shape(rect(cx_ - 40, 196, 80, 18), 1.2) + p.hatch(rect(cx_ + 10, 196, 30, 18), 90, 2.2, 1.0, 0.6))
    o.append(p.shape(rect(cx_ - 16, 176, 32, 20), 1.3) + "".join(p.seg(cx_ - 13 + k * 4.3, 178, cx_ - 13 + k * 4.3, 194, 0.9) for k in range(7)))
    dmc = arc_pts(cx_, 176, 15, 26, 180, 360, 12)
    o.append(p.shape(dmc + [(cx_ + 15, 176)], 1.4) + p.hatch(dmc, 80, 2.0, 1.0, 0.8, keep=lambda x, y: max(0, (x - cx_ + 3) / 14)))
    o.append(p.shape(rect(cx_ - 4, 140, 8, 10), 1.0) + p.seg(cx_, 140, cx_, 132, 1.0))
    rr = random.Random(9)
    roofs = sorted([(rr.uniform(370, 610), rr.uniform(208, 330)) for _ in range(70)], key=lambda r: r[1])
    for x0, y0 in roofs:
        if y0 > 212 + (x0 - 360) * 0.5 + 20:
            pass
        w = rr.uniform(18, 40) * (0.6 + (y0 - 208) / 160)
        o.append(p.shape(rect(x0, y0, w, 440 - y0), 1.0))
        o.append(p.hatch(rect(x0 + w * 0.62, y0 + 1, w * 0.38, 8 + (y0 - 208) * 0.08), 90, 2.0, 1.0, 0.6))
        k_ = 0.5 + (y0 - 208) / 120
        o.append(p.windows(x0 + 3, y0 + 4, max(1, int((w - 4) / (7 * k_))), max(1, int((440 - y0 - 8) / (11 * k_))), 2.8 * k_, 4.4 * k_, 4.2 * k_, 6.6 * k_, w=0.6, dark=0.75, sill=False))
        if rr.random() < 0.3:
            o.append(p.shape(rect(x0 + 3, y0 - 5, 6, 5), 0.9))
    o.append(p.shape(rect(452, 168, 10, 40), 1.2) + p.shape([(450, 168), (457, 154), (464, 168)], 1.1))
    # --- the sea: swell lines thickening toward us, a fishing boat, a freighter heading out
    o.append(p.line([(-10, 216), (360, 216)], 1.4, 0.2))
    wall_pts = [W(-17.8, 1.0, z) for z in [24 + k * 3 for k in range(40)]]
    poly_sea = [(-10, 217), (380, 217)] + [q for q in wall_pts if q[0] < 380][::-1] + [(-10, 610)]
    poly_sea = [(-10, 217), (360, 217)] + sorted([q for q in wall_pts if q[0] < 360], key=lambda q: q[0], reverse=True) + [(-10, 620)]
    cid = p.uid("sea")
    p.defs.append(f'<clipPath id="{cid}"><polygon points="{P(poly_sea)}"/></clipPath>')
    o.append(f'<g clip-path="url(#{cid})">' + p.ripples(-10, 380, 219, 600, 330, hy=216, lmin=5, lmax=40, wmin=1.0, wmax=2.1) + "</g>")
    o.append(p.solid([(96, 262), (132, 262), (128, 268), (100, 268)]) + p.seg(112, 262, 112, 246, 1.1) + p.person(106, 262, 11, 1))
    o.append(f'<path d="M96 266q-14 2 -26 0" fill="none" stroke="{INK}" stroke-width="1.1"/>')
    o.append(p.shape([(26, 236), (88, 236), (84, 244), (30, 244)], 1.3, fill=INK) + p.shape(rect(70, 226, 14, 10), 1.1) + p.seg(42, 236, 42, 222, 1.0) + p.seg(56, 236, 56, 224, 1.0))
    # --- the Malecon: sea wall, wide sidewalk, the boulevard, the far curve
    zs = [24 + k * 2.5 for k in range(70)]
    for X0, X1, fill in ((-17.8, -17.2, PAPER), (-17.2, -14.0, PAPER), (-14.0, -3.0, PAPER)):
        band = [W(X0, 0.2 if X0 > -17.8 else 1.0, z) for z in zs] + [W(X1, 0.2, z) for z in zs[::-1]]
        o.append(p.solid(band, fill))
    o.append(p.line([W(-17.8, 1.0, z) for z in zs], 2.6, 0.2))
    o.append(p.line([W(-17.2, 1.0, z) for z in zs], 1.4, 0.2))
    o.append(p.hatch([W(-17.2, 1.0, z) for z in zs] + [W(-17.2, 0.2, z) for z in zs[::-1]], 0, 1.6, 1.0, 0.8))
    o.append(p.line([W(-14.0, 0.2, z) for z in zs], 1.8, 0.2))
    o.append(p.line([W(-3.0, 0.2, z) for z in zs], 1.8, 0.2))
    o.append(p.stipple([W(-14.0, 0.0, z) for z in zs] + [W(-3.0, 0.0, z) for z in zs[::-1]], 300, r=(0.5, 1.0)))
    for z in zs[::4]:
        a_, b_ = W(-8.6, 0, z), W(-8.6, 0, z + 3)
        o.append(p.seg(a_[0], a_[1], b_[0], b_[1], 1.4, 0.1))
    # waves bursting over the wall at two places
    for z, h, w in ((40, 70, 26), (66, 40, 16)):
        q = W(-18.0, 1.0, z)
        o.append(splash(p, q[0], q[1], h, w))
    # lamps along the wall, friends sitting on it, walkers
    for z in (30, 44, 58, 74, 92):
        q = W(-16.8, 0.2, z)
        o.append(p.lamp(q[0], q[1], 430 * 4.5 / z, w=1.4))
    for z, k in ((33, 1.0), (34, 0.9), (50, 1.0), (62, 1.0), (63.5, 0.9)):
        q = W(-17.5, 1.0, z)
        h = 430 * 1.0 / z * k
        o.append(f'<path d="M{q[0] - h * 0.22:.1f} {q[1]:.1f}q{-h * 0.02:.1f} {-h * 0.62:.1f} {h * 0.22:.1f} {-h * 0.7:.1f}q{h * 0.22:.1f} {h * 0.1:.1f} {h * 0.2:.1f} {h * 0.7:.1f}Z" fill="{INK}"/>'
                 f'<circle cx="{q[0]:.1f}" cy="{q[1] - h * 0.84:.1f}" r="{h * 0.13:.1f}" fill="{INK}"/>')
    for X, z, f, d in ((-15.5, 36, False, True), (-15.0, 46, True, False), (-15.8, 70, False, False)):
        q = W(X, 0.2, z)
        o.append(p.person(q[0], q[1], 430 * 1.7 / z, int(z) % 2, flip=f, dress=d))
    # fifties cars cruising the boulevard
    o.append(classic_car(p, lambda X, Y, Z: W(X, Y, Z), -6.0, 34, wash=TEAL))
    o.append(classic_car(p, lambda X, Y, Z: W(X, Y, Z), -11.0, 52))
    o.append(classic_car(p, lambda X, Y, Z: W(X, Y, Z), -5.5, 78))
    # --- the buildings on our side, receding along the curve: rooftops below us, arcades at street level
    z = 36.0
    blds = []
    while z < 170:
        L = rnd.uniform(10, 16)
        blds.append((z, z + L, rnd.uniform(11, 18)))
        z += L
    for z0, z1, H in reversed(blds):
        X = -2.6
        front = [W(X, 0, z0), W(X, H, z0), W(X, H, z1), W(X, 0, z1)]
        roof = [W(X, H, z0), W(X + 7, H, z0), W(X + 7, H, z1), W(X, H, z1)]
        o.append(p.shape(roof, 1.3))
        o.append(p.hatch(roof, 30, 3.0, 1.0, 0.5))
        o.append(p.line([W(X + 0.4, H + 0.9, z0), W(X + 0.4, H + 0.9, z1)], 1.0, 0.1))
        o.append(p.shape(front, 1.6 if z0 < 60 else 1.1))
        o.append(p.hatch(front, 85, 4.0, 1.0, 0.4))
        n = max(2, int((z1 - z0) / 3.4))
        for j in range(n):
            za = z0 + (z1 - z0) * j / n + 0.4
            zb = z0 + (z1 - z0) * (j + 1) / n - 0.4
            o.append(p.solid([W(X, 0, za), W(X, 3.0, za)] + [W(X, 3.0 + 0.9 * math.sin(math.pi * t), za + (zb - za) * t) for t in [k / 6 for k in range(1, 6)]] + [W(X, 3.0, zb), W(X, 0, zb)]))
            for fl in range(int((H - 4.4) / 3.4)):
                ya = 4.8 + fl * 3.4
                wq = [W(X, ya, za + 0.6), W(X, ya + 2.0, za + 0.6), W(X, ya + 2.0, zb - 0.6), W(X, ya, zb - 0.6)]
                o.append(p.solid(wq) if rnd.random() < 0.6 else p.line(wq, 1.0, 0.1, closed=True))
        o.append(p.line([W(X, H, z0), W(X, H, z1)], 1.8 if z0 < 60 else 1.2, 0.1))
        # rooftop life: water tanks, a pergola, a little laundry
        if rnd.random() < 0.6:
            q = W(X + 3.5, H, (z0 + z1) / 2)
            s_ = 430 / ((z0 + z1) / 2)
            o.append(p.shape(rect(q[0] - s_ * 0.7, q[1] - s_ * 1.4, s_ * 1.4, s_ * 1.4), 1.0) + p.hatch(rect(q[0], q[1] - s_ * 1.4, s_ * 0.7, s_ * 1.4), 90, 1.6, 1.0, 0.8))
    # --- our balcony: wrought-iron railing with scrolls, a canary cage, coffee on the rail, a fern
    RY = 470
    o.append(p.shape([(-10, RY), (610, RY), (610, RY + 10), (-10, RY + 10)], 2.4))
    o.append(p.hatch([(-10, RY + 5), (610, RY + 5), (610, RY + 10), (-10, RY + 10)], 0, 1.6, 1.0, 0.9))
    o.append(p.solid([(-10, 588), (610, 588), (610, 610), (-10, 610)]))
    bars = []
    for x in range(-6, 610, 36):
        bars.append(f"M{x} {RY + 10}V588M{x + 18} {RY + 10}V588")
        cx_, cy_ = x + 9, RY + 60
        bars.append(f"M{x} {RY + 30}c8 0 9 10 9 20c0 -10 1 -20 9 -20M{x} {RY + 90}c8 0 9 -10 9 -20c0 10 1 20 9 20"
                    f"M{cx_ - 5} {cy_}a5 5 0 1 0 10 0a5 5 0 1 0 -10 0")
    o.append(f'<path d="{"".join(bars)}" fill="none" stroke="{INK}" stroke-width="2"/>')
    o.append(p.line([(-10, RY + 30), (610, RY + 30)], 1.6, 0.1) + p.line([(-10, RY + 92), (610, RY + 92)], 1.6, 0.1))
    # the cafecito: cup and saucer on the rail, steam
    cx_ = 470
    o.append(p.shape([(cx_ - 12, RY - 18), (cx_ + 12, RY - 18), (cx_ + 9, RY - 2), (cx_ - 9, RY - 2)], 1.6))
    o.append(f'<path d="M{cx_ + 11} {RY - 15}q9 0 6 7q-2 4 -8 3" fill="none" stroke="{INK}" stroke-width="1.6"/>'
             f'<path d="M{cx_ - 20} {RY - 1}h40" stroke="{INK}" stroke-width="2.4"/>'
             f'<path d="M{cx_ - 4} {RY - 24}q-5 -8 0 -14q5 -6 0 -12M{cx_ + 4} {RY - 24}q-5 -8 0 -14" fill="none" stroke="{INK}" stroke-width="1.2" opacity="0.8"/>')
    o.append(p.hatch([(cx_, RY - 18), (cx_ + 12, RY - 18), (cx_ + 9, RY - 2), (cx_, RY - 2)], 90, 2.0, 1.0, 0.8))
    # the canary cage hanging from above, the bird on its perch
    gx, gy = 96, 330
    o.append(p.seg(gx, 0, gx, gy - 46, 1.4) + f'<circle cx="{gx}" cy="{gy - 50}" r="4" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    cage = [(gx - 34, gy + 40), (gx - 34, gy - 6)] + arc_pts(gx, gy - 6, 34, 40, 180, 360, 14) + [(gx + 34, gy + 40)]
    o.append(p.solid(cage, PAPER, 0.75))
    o.append(f'<path d="{"".join(f"M{gx + 34 * math.cos(math.pi * (1 - k / 10)):.1f} {gy - 6 - 40 * math.sin(math.pi * (1 - k / 10)):.1f}L{gx + 34 * math.cos(math.pi * (1 - k / 10)):.1f} {gy + 40}" for k in range(11))}" stroke="{INK}" stroke-width="1.1"/>')
    o.append(p.line(arc_pts(gx, gy - 6, 34, 40, 180, 360, 14), 1.6, 0.1) + p.line([(gx - 38, gy + 40), (gx + 38, gy + 40)], 3.0, 0.1) + p.line([(gx - 34, gy + 6), (gx + 34, gy + 6)], 1.2, 0.1))
    o.append(p.seg(gx - 20, gy + 18, gx + 20, gy + 18, 1.6))
    o.append(f'<path d="M{gx - 10} {gy + 18}q-2 -12 6 -16q4 -6 10 -2l6 -1l-5 4q2 10 -6 15Z" fill="{INK}"/>'
             f'<path d="M{gx - 10} {gy + 16}l-8 8" stroke="{INK}" stroke-width="2"/><circle cx="{gx + 7}" cy="{gy - 1}" r="1.2" fill="{PAPER}"/>')
    # a fern in a pot on the balcony floor, left
    o.append(p.shape([(150, 588), (186, 588), (192, 552), (144, 552)], 1.8) + p.hatch([(168, 588), (186, 588), (192, 552), (168, 552)], 90, 2.0, 1.0, 0.8))
    fr = []
    for k in range(13):
        a_ = math.pi * (0.05 + 0.9 * k / 12)
        L = rnd.uniform(46, 70)
        ex, ey = 168 + L * math.cos(a_) * 1.2, 552 - L * math.sin(a_) * 0.8 + 18
        fr.append(f"M168 552Q{168 + L * 0.6 * math.cos(a_):.1f} {552 - L * 0.9:.1f} {ex:.1f} {ey:.1f}")
        for t in (0.35, 0.55, 0.75):
            px_ = (1 - t) ** 2 * 168 + 2 * (1 - t) * t * (168 + L * 0.6 * math.cos(a_)) + t * t * ex
            py_ = (1 - t) ** 2 * 552 + 2 * (1 - t) * t * (552 - L * 0.9) + t * t * ey
            fr.append(f"M{px_ - 4:.1f} {py_ - 2:.1f}l4 3l4 -3")
    o.append(f'<path d="{"".join(fr)}" fill="none" stroke="{INK}" stroke-width="1.3" stroke-linecap="round"/>')
    # --- title in the sky
    sz = name_size(name, 400, 72, ls=3)
    o.append(title_text(300, 92, name, sz, ls=3))
    o.append(coord_line(p, 300, 120, coords, 17, 2.6, 34, 12, dots=True))
    return compose(p, "".join(o))


# ---------------------------------------------------------------------------------- build
def build(only=None):
    for slug, (name, coords, fn) in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COLL, slug, fn(name, coords))


if __name__ == "__main__":
    build(sys.argv[1:] or None)
