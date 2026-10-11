"""Painting kit for the Fairy Tales & Myths gallery plates (owner: fairy_tales_painted.py).

The idea: a painter blocks a figure as a silhouette, feels the volume inside it, then lays strokes whose colour
comes from how the light hits that volume. Here a form is an authored outline (anatomy drawn point by point)
that is rasterised; its distance field is inflated into a height map (plus optional anatomical bumps: a shoulder,
a haunch, a jowl), and the surface normals drive every stroke: colour from key light, warm rim, cool bounce;
direction along the form or along the hair. Edges are lost on the lit side and found on the shadow side.

Only numpy / opencv at build time; the output is plain SVG paths.
"""
import math
import random

import cv2
import numpy as np

from gouache import blob, smooth_closed, smooth_open


# ---------------------------------------------------------------- colour
def hx(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def mix(a, b, t):
    A, B = hx(a), hx(b)
    t = max(0.0, min(1.0, t))
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * t) for x, y in zip(A, B))


def lt(c, t):
    return mix(c, "#FFFFFF", t)


def dk(c, t):
    return mix(c, "#000000", t)


def ramp(cols, t):
    t = max(0.0, min(1.0, t))
    k = t * (len(cols) - 1)
    i = min(int(k), len(cols) - 2)
    return mix(cols[i], cols[i + 1], k - i)


def gstop(stops, t):
    if t <= stops[0][0]:
        return stops[0][1]
    for (o0, c0), (o1, c1) in zip(stops, stops[1:]):
        if t <= o1:
            return mix(c0, c1, (t - o0) / max(1e-6, o1 - o0))
    return stops[-1][1]


def norm3(v):
    L = math.sqrt(sum(a * a for a in v)) or 1.0
    return tuple(a / L for a in v)


# ---------------------------------------------------------------- geometry
def resample(pts, step=4.0, closed=True):
    """Points every ~step px along the Catmull-Rom curve through pts (matches smooth_closed / smooth_open)."""
    P = list(pts) + ([pts[0], pts[1], pts[2]] if closed else [])
    out = []
    n = len(pts) if closed else len(pts) - 1
    for i in range(n):
        p0 = P[i - 1] if (i > 0 or closed) else P[0]
        p1, p2 = P[i], P[i + 1]
        p3 = P[i + 2] if i + 2 < len(P) else P[-1]
        seg = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        m = max(1, int(seg / step))
        for k in range(m):
            t = k / m
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    if not closed:
        out.append(pts[-1])
    return out


def lin_resample(pts, step=3.0, closed=True):
    P = list(pts) + ([pts[0]] if closed else [])
    out = []
    for (x0, y0), (x1, y1) in zip(P, P[1:]):
        m = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        out += [(x0 + (x1 - x0) * k / m, y0 + (y1 - y0) * k / m) for k in range(m)]
    if not closed:
        out.append(P[-1])
    return out


def xform(pts, ox=0.0, oy=0.0, s=1.0, ang=0.0, flip=False, sy=None):
    """Mirror (x -> -x), scale, rotate (deg, screen coords), translate."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    sy = s if sy is None else sy
    out = []
    for x, y in pts:
        if flip:
            x = -x
        x, y = x * s, y * sy
        out.append((ox + x * ca - y * sa, oy + x * sa + y * ca))
    return out


def bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def limb_outline(joints, cap=0.55, top_cap=0.4):
    """Closed outline for a limb / tapering tube from a chain [(x, y, width), ...]."""
    n = len(joints)
    left, right = [], []
    for i, (x, y, w) in enumerate(joints):
        a = joints[max(0, i - 1)]
        b = joints[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        left.append((x + nx * w / 2, y + ny * w / 2))
        right.append((x - nx * w / 2, y - ny * w / 2))
    x, y, w = joints[-1]
    px, py, _ = joints[-2]
    dx, dy = x - px, y - py
    L = math.hypot(dx, dy) or 1
    tip = (x + dx / L * w * cap, y + dy / L * w * cap)
    x, y, w = joints[0]
    px, py, _ = joints[1]
    dx, dy = x - px, y - py
    L = math.hypot(dx, dy) or 1
    top = (x + dx / L * w * top_cap, y + dy / L * w * top_cap)
    return left + [tip] + right[::-1] + [top]


def path_d(pts, closed=True):
    return smooth_closed(pts) if closed else smooth_open(pts)


def poly_d(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"


# ---------------------------------------------------------------- light
class Look:
    """How light falls on a form.
    cols: ramp from core shadow to highlight. key: direction the key light comes FROM (x, y, z) in screen
    coords (y down, z toward the viewer). rim: (colour, (x, y), strength): back light catching the edges that
    face (x, y). bounce: (colour, strength): reflected light into shadows that face down. spec: (colour, from, k).
    """

    def __init__(self, cols, key=(-0.6, -0.7, 0.55), amb=0.1, wrap=0.3, rim=None, bounce=None, spec=None, jit=0.05,
                 gamma=1.0, tint=None):
        self.cols, self.key, self.amb, self.wrap = cols, norm3(key), amb, wrap
        self.rim, self.bounce, self.spec, self.jit, self.gamma, self.tint = rim, bounce, spec, jit, gamma, tint

    def value(self, n):
        d = n[0] * self.key[0] + n[1] * self.key[1] + n[2] * self.key[2]
        v = (d + self.wrap) / (1 + self.wrap)
        v = self.amb + (1 - self.amb) * max(0.0, v)
        return v ** self.gamma

    def color(self, n, rnd, extra=0.0):
        v = self.value(n) + extra + rnd.uniform(-self.jit, self.jit)
        c = ramp(self.cols, v)
        if self.bounce and n[1] > 0.1 and v < 0.6:
            c = mix(c, self.bounce[0], self.bounce[1] * min(1.0, (n[1] - 0.1) * 1.8) * (0.6 - v) / 0.6)
        if self.rim:
            col, (rx, ry), s = self.rim
            rr = math.hypot(rx, ry) or 1
            f = max(0.0, (n[0] * rx + n[1] * ry) / rr) * max(0.0, 1 - n[2]) ** 1.5
            if f > 0.04:
                c = mix(c, col, min(1.0, f * s))
        if self.spec and v > self.spec[1]:
            c = mix(c, self.spec[0], min(1.0, (v - self.spec[1]) / max(0.01, 1 - self.spec[1])) * self.spec[2])
        if self.tint:
            c = mix(c, self.tint[0], self.tint[1])
        return c

    def darker(self, t, **kw):
        a = dict(key=self.key, amb=self.amb, wrap=self.wrap, rim=self.rim, bounce=self.bounce, spec=self.spec, jit=self.jit,
                 gamma=self.gamma, tint=self.tint)
        a.update(kw)
        return Look([dk(c, t) if t > 0 else lt(c, -t) for c in self.cols], **a)

    def toward(self, col, t, **kw):
        a = dict(key=self.key, amb=self.amb, wrap=self.wrap, rim=self.rim, bounce=self.bounce, spec=self.spec, jit=self.jit,
                 gamma=self.gamma, tint=self.tint)
        a.update(kw)
        return Look([mix(c, col, t) for c in self.cols], **a)


# ---------------------------------------------------------------- marks
def stroke(x, y, ang, L, w, col, op, bend=0.0):
    """One tapered, slightly bowed brush stroke centred on (x, y)."""
    a = math.radians(ang)
    dx, dy = L * math.cos(a) / 2, L * math.sin(a) / 2
    nx, ny = -math.sin(a), math.cos(a)
    x0, y0, x1, y1 = x - dx, y - dy, x + dx, y + dy
    mx, my = x + nx * bend, y + ny * bend
    return (f'<path d="M{x0:.1f} {y0:.1f}Q{mx + nx * w:.1f} {my + ny * w:.1f} {x1:.1f} {y1:.1f}'
            f'Q{mx - nx * w:.1f} {my - ny * w:.1f} {x0:.1f} {y0:.1f}Z" fill="{col}" opacity="{op:.2f}"/>')


def dab(x, y, r, col, op, rnd, squash=0.75, rot=None):
    """A loaded-brush dab: a soft irregular blot."""
    rot = math.radians(rnd.uniform(0, 180) if rot is None else rot)
    ca, sa = math.cos(rot), math.sin(rot)
    ry = r * squash
    k = [rnd.uniform(0.85, 1.25) for _ in range(4)]
    P0 = (r * ca, r * sa)
    P1 = (-ry * sa, ry * ca)
    pts = [P0, P1, (-P0[0], -P0[1]), (-P1[0], -P1[1])]
    s = f'M{x + pts[0][0]:.1f} {y + pts[0][1]:.1f}'
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        cx_, cy_ = (a[0] + b[0]) * k[i], (a[1] + b[1]) * k[i]
        s += f'q{cx_ - a[0]:.1f} {cy_ - a[1]:.1f} {b[0] - a[0]:.1f} {b[1] - a[1]:.1f}'
    return f'<path d="{s}" fill="{col}" opacity="{op:.2f}"/>'


def taper(pts, w0, w1, col, op=1.0, mid=None):
    """Tapered brush line along pts (width w0 -> w1, optional swell `mid` in the middle)."""
    n = len(pts)
    if n < 2:
        return ""
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        t = i / max(1, n - 1)
        w = w0 + (w1 - w0) * t
        if mid is not None:
            w += (mid - (w0 + w1) / 2) * math.sin(math.pi * t)
        w /= 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return f'<path d="{smooth_closed(left + right[::-1])}" fill="{col}" opacity="{op:.2f}"/>'


def vline(pts, widths, col, op):
    n = len(pts)
    if n < 2:
        return ""
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = widths[i] / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return f'<path d="M{" L".join(f"{x:.1f} {y:.1f}" for x, y in left + right[::-1])}Z" fill="{col}" opacity="{op:.2f}"/>'


def outline_normals(pts):
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sgn = 1 if area > 0 else -1
    out = []
    for i in range(n):
        ax, ay = pts[i - 1]
        bx, by = pts[(i + 1) % n]
        tx, ty = bx - ax, by - ay
        L = math.hypot(tx, ty) or 1
        out.append((sgn * ty / L, -sgn * tx / L))
    return out


def edges(pts, light, seed, dark="#2A1A12", lit=None, w=2.2, dark_op=0.7, lit_op=0.7, lit_w=None, thresh=0.0, mask=None,
          lit_thresh=0.25):
    """Lost-and-found contour: a dark line that swells where the outline turns away from `light` (direction the light
    comes FROM) and disappears where it faces it; optional `lit` rim line on the lit side."""
    rnd = random.Random(seed)
    ns = outline_normals(pts)
    lx, ly = light
    L = math.hypot(lx, ly) or 1
    lx, ly = lx / L, ly / L
    n = len(pts)
    fac = [ns[i][0] * lx + ns[i][1] * ly for i in range(n)]
    ph1, ph2 = rnd.uniform(0, 6.28), rnd.uniform(0, 6.28)
    mod = [0.75 + 0.35 * math.sin(i * 0.21 + ph1) * math.sin(i * 0.053 + ph2) for i in range(n)]
    out = []

    def runs(test):
        cur = []
        for i in range(n):
            if test(i) and (mask is None or mask(*pts[i])):
                cur.append(i)
            elif cur:
                yield cur
                cur = []
        if cur:
            yield cur
    if dark:
        for r in runs(lambda i: fac[i] < thresh):
            if len(r) < 3:
                continue
            m = len(r)
            ws = [max(0.15, w * (0.35 + 0.85 * min(1.0, (thresh - fac[i]) * 1.4)) * mod[i] * min(1.0, j / 4, (m - 1 - j) / 4))
                  for j, i in enumerate(r)]
            out.append(vline([pts[i] for i in r], ws, dark, dark_op))
    if lit:
        for r in runs(lambda i: fac[i] > lit_thresh):
            if len(r) < 3:
                continue
            m = len(r)
            ws = [max(0.1, (lit_w or w) * (0.3 + 0.9 * min(1.0, (fac[i] - lit_thresh) * 1.6)) * mod[i] * min(1.0, j / 4, (m - 1 - j) / 4))
                  for j, i in enumerate(r)]
            out.append(vline([pts[i] for i in r], ws, lit, lit_op))
    return "".join(out)


# ---------------------------------------------------------------- volume from a silhouette
class Vol:
    """Height field of one form, built from its outline.

    round_r: the distance (px) over which the edge rolls from vertical to flat (about half the form's width for a
    fully round form). bumps: [(cx, cy, rx, ry, rot_deg, amp)] smooth domes (muscles, bones) added to the height,
    negative amp for hollows. blur: smoothing of the field (px)."""

    def __init__(self, pts, round_r=30.0, bumps=(), blur=None, pad=6, res=1.0, extra=None):
        self.pts = pts
        x0, y0, x1, y1 = bbox(pts)
        self.ox, self.oy = math.floor(x0) - pad, math.floor(y0) - pad
        self.res = res
        W = int((x1 - self.ox + pad) / res) + 2
        H = int((y1 - self.oy + pad) / res) + 2
        m = np.zeros((H, W), np.uint8)
        poly = np.array([[(x - self.ox) / res, (y - self.oy) / res] for x, y in pts], np.float32)
        cv2.fillPoly(m, [np.round(poly * 4).astype(np.int32)], 1, lineType=cv2.LINE_8, shift=2)
        self.mask = m.astype(bool)
        d = cv2.distanceTransform(m, cv2.DIST_L2, 5) * res
        R = max(1.0, round_r)
        dd = np.minimum(d, R)
        h = np.sqrt(np.maximum(0.0, dd * (2 * R - dd)))
        if bumps:
            yy, xx = np.mgrid[0:H, 0:W]
            X = xx * res + self.ox
            Y = yy * res + self.oy
            for (cx, cy, rx, ry, rot, amp) in bumps:
                a = math.radians(rot)
                ca, sa = math.cos(a), math.sin(a)
                u = ((X - cx) * ca + (Y - cy) * sa) / rx
                v = (-(X - cx) * sa + (Y - cy) * ca) / ry
                q = u * u + v * v
                h = h + amp * np.where(q < 1, (1 - q) ** 1.5, 0.0)
        if extra is not None:
            h = h + extra(self.ox, self.oy, res, H, W)
        h = h * self.mask
        if blur is None:
            blur = max(2.0, R * 0.22)
        if blur:
            h = cv2.GaussianBlur(h.astype(np.float32), (0, 0), blur / res)
        gy, gx = np.gradient(h, res)
        nz = np.ones_like(h)
        L = np.sqrt(gx * gx + gy * gy + nz)
        self.nx, self.ny, self.nz = -gx / L, -gy / L, nz / L
        self.h = h
        self.W, self.H = W, H

    def inside(self, x, y):
        i, j = int((y - self.oy) / self.res), int((x - self.ox) / self.res)
        return 0 <= i < self.H and 0 <= j < self.W and self.mask[i, j]

    def normal(self, x, y):
        i, j = int((y - self.oy) / self.res), int((x - self.ox) / self.res)
        i = min(max(i, 0), self.H - 1)
        j = min(max(j, 0), self.W - 1)
        return (float(self.nx[i, j]), float(self.ny[i, j]), float(self.nz[i, j]))

    def contour_angle(self, x, y):
        """Direction along the isophote (around the form)."""
        n = self.normal(x, y)
        return math.degrees(math.atan2(n[1], n[0])) + 90


class Doc:
    """Defs collector with unique ids (prefix per design)."""

    def __init__(self, u):
        self.u, self.n, self.defs = u, 0, []

    def nid(self):
        self.n += 1
        return f"{self.u}{self.n}"

    def lin(self, stops, x1=0, y1=0, x2=0, y2=1, units="objectBoundingBox"):
        i = self.nid()
        u = "" if units == "objectBoundingBox" else f' gradientUnits="{units}"'
        s = "".join(f'<stop offset="{st[0]}" stop-color="{st[1]}"' + (f' stop-opacity="{st[2]}"' if len(st) > 2 else "") + "/>" for st in stops)
        self.defs.append(f'<linearGradient id="{i}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{u}>{s}</linearGradient>')
        return f"url(#{i})"

    def rad(self, stops, cx=0.5, cy=0.5, r=0.5, units=None, fx=None, fy=None):
        i = self.nid()
        u = f' gradientUnits="{units}"' if units else ""
        f = (f' fx="{fx}" fy="{fy}"' if fx is not None else "")
        s = "".join(f'<stop offset="{st[0]}" stop-color="{st[1]}"' + (f' stop-opacity="{st[2]}"' if len(st) > 2 else "") + "/>" for st in stops)
        self.defs.append(f'<radialGradient id="{i}" cx="{cx}" cy="{cy}" r="{r}"{f}{u}>{s}</radialGradient>')
        return f"url(#{i})"

    def clip(self, d):
        i = self.nid()
        self.defs.append(f'<clipPath id="{i}"><path d="{d}"/></clipPath>')
        return f'clip-path="url(#{i})"'

    def blur(self, sd):
        i = self.nid()
        self.defs.append(f'<filter id="{i}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{sd}"/></filter>')
        return f'filter="url(#{i})"'

    def render(self, parts):
        return "<defs>" + "".join(self.defs) + "</defs>\n" + "\n".join(p for p in parts if p)


PASSES = ((40, (16, 32), (4, 8), (0.3, 0.55)),
          (190, (8, 18), (1.8, 3.6), (0.35, 0.7)),
          (110, (4, 9), (1.0, 2.2), (0.45, 0.85)))


def paint(D, pts, look, seed, vol=None, round_r=30, bumps=(), flow="contour", flow_jit=12, passes=PASSES, density=1.0,
          under=True, base=None, edge_col="#2A1A12", edge_w=2.0, edge_op=0.65, rim_col=None, rim_w=None, rim_op=0.7,
          edge_light=None, edge_mask=None, edge_thresh=0.0, value_fn=None, color_fn=None, blur=None, lit_thresh=0.25,
          accents=None, smooth=True):
    """A painted solid: underpaint (gradient along the light), strokes modelled by the volume and clipped to the
    outline, then lost-and-found edges. flow: 'contour' (around the form), 'axis' (down the gradient), a fixed
    angle, or callable(x, y, n) -> deg. value_fn(x, y) -> brightness offset (cast shadows, local darkening).
    color_fn(x, y, col, n) -> col (local colour changes: dapples, socks). Returns svg."""
    rnd = random.Random(seed)
    v = vol or Vol(pts, round_r, bumps, blur)
    d = smooth_closed(pts) if smooth else poly_d(pts)
    fine = resample(pts, 3.0) if smooth else lin_resample(pts, 3.0)
    x0, y0, x1, y1 = bbox(fine)
    kx, ky = look.key[0], look.key[1]
    out = []
    if under:
        g = base or D.lin([(0, ramp(look.cols, 0.7)), (0.5, ramp(look.cols, 0.5)), (1, ramp(look.cols, 0.3))],
                          round(0.5 + kx * 0.5, 2), round(0.5 + ky * 0.5, 2), round(0.5 - kx * 0.5, 2), round(0.5 - ky * 0.5, 2))
        out.append(f'<path d="{d}" fill="{g}"/>')
    st = []
    area = (x1 - x0) * (y1 - y0)
    for cnt, Lr, Wr, Or in passes:
        n = int(cnt * area / 10000 * density)
        for _ in range(n):
            x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            if not v.inside(x, y):
                continue
            nrm = v.normal(x, y)
            ex = value_fn(x, y) if value_fn else 0.0
            col = look.color(nrm, rnd, ex)
            if color_fn:
                col = color_fn(x, y, col, nrm) or col
            if callable(flow):
                ang = flow(x, y, nrm)
            elif flow == "contour":
                ang = math.degrees(math.atan2(nrm[1], nrm[0])) + 90
            elif flow == "axis":
                ang = math.degrees(math.atan2(nrm[1], nrm[0]))
            else:
                ang = flow
            ang += rnd.uniform(-flow_jit, flow_jit)
            # strokes get shorter where the form turns sharply (near the edge)
            L = rnd.uniform(*Lr) * (0.55 + 0.45 * nrm[2])
            st.append(stroke(x, y, ang, L, rnd.uniform(*Wr), col, rnd.uniform(*Or), rnd.uniform(-1.5, 1.5)))
    if accents:
        st.append(accents)
    cid = D.clip(d)
    out.append(f'<g {cid}>{"".join(st)}</g>')
    el = edge_light or (look.key[0], look.key[1])
    out.append(edges(fine, el, seed + 5, edge_col, rim_col, edge_w, dark_op=edge_op, lit_op=rim_op, lit_w=rim_w, thresh=edge_thresh,
                     mask=edge_mask, lit_thresh=lit_thresh))
    return "".join(out)


def hair(guide, n, spread, seed, cols, w=(0.8, 2.2), op=(0.35, 0.85), taper_end=0.2, start=(0, 0.3), end=(0.7, 1.0), wave=0.25):
    """Flowing strands (manes, tails, hair, smoke): many tapered curves following a guide, fanned by `spread`
    (number or f(t))."""
    rnd = random.Random(seed)
    g = resample(guide, 5, closed=False)
    ns = []
    for i in range(len(g)):
        a, b = g[max(0, i - 1)], g[min(len(g) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        ns.append((-dy / L, dx / L))
    m = len(g)
    out = []
    for _ in range(n):
        off = rnd.uniform(-1, 1)
        ph = rnd.uniform(0, 6.28)
        fr = rnd.uniform(0.6, 3.0)
        amp = rnd.uniform(0, wave)
        i0 = int(rnd.uniform(*start) * (m - 1))
        i1 = max(i0 + 2, int(rnd.uniform(*end) * (m - 1)))
        line = []
        for i in range(i0, min(i1 + 1, m)):
            t = i / max(1, m - 1)
            s_ = spread(t) if callable(spread) else spread
            o = (off + amp * math.sin(ph + fr * t * 6.28)) * s_
            line.append((g[i][0] + ns[i][0] * o, g[i][1] + ns[i][1] * o))
        if len(line) < 2:
            continue
        ww = rnd.uniform(*w)
        out.append(taper(line, ww, ww * taper_end, rnd.choice(cols), rnd.uniform(*op)))
    return "".join(out)


# ---------------------------------------------------------------- atmosphere
def halo(D, cx, cy, r, col, s=0.8, ry=None, mid=0.4):
    g = D.rad([(0, col, s), (mid, col, round(s * 0.42, 3)), (1, col, 0)])
    if ry:
        return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r:.1f}" ry="{ry:.1f}" fill="{g}"/>'
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{g}"/>'


def sky(D, stops, seed, y0=0, y1=600, n=260, L=(60, 200), W=(4, 12), op=(0.08, 0.28), angle=0, jit=0.06, x0=-20, x1=620):
    """Graded sky + broad brushwork whose colour is sampled from the same gradient."""
    rnd = random.Random(seed)
    g = D.lin([(o, c) for o, c in stops], 0, y0, 0, y1, "userSpaceOnUse")
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{g}"/>']
    for _ in range(n):
        y = rnd.uniform(y0 - 10, y1 + 10)
        t = (y - y0) / max(1, y1 - y0) + rnd.uniform(-jit, jit)
        c = gstop(stops, max(0, min(1, t)))
        c = lt(c, rnd.uniform(0, 0.1)) if rnd.random() < 0.5 else dk(c, rnd.uniform(0, 0.07))
        out.append(stroke(rnd.uniform(x0, x1), y, angle + rnd.uniform(-3, 3), rnd.uniform(*L), rnd.uniform(*W), c, rnd.uniform(*op), rnd.uniform(-3, 3)))
    return "".join(out)


def cloud(D, puffs, look, seed, density=1.0, size=(4, 11), op=(0.4, 0.85), flat_y=None, under_dark=0.25, base_op=0.6,
          wisp=0, wisp_cols=None):
    """A cloud mass from overlapping puffs [(cx, cy, r), ...]: soft body plus dabs coloured by the light on the
    puff surfaces; a flat, shaded underside at flat_y."""
    rnd = random.Random(seed)
    from gouache import blob
    xs = [p[0] - p[2] for p in puffs] + [p[0] + p[2] for p in puffs]
    ys = [p[1] - p[2] for p in puffs]
    bottom = flat_y if flat_y is not None else max(p[1] + p[2] for p in puffs)
    box = (min(xs), min(ys), max(xs), bottom)
    out = []
    for (cx, cy, r) in puffs:
        ry = min(r * 0.92, max(4, (bottom - cy + r * 0.25)))
        out.append(f'<path d="{blob(cx, min(cy, bottom - ry * 0.5), r * 0.95, ry, rnd.randint(0, 9999), 0.1, 14)}" fill="{ramp(look.cols, 0.42)}" opacity="{base_op}"/>')

    def surf(x, y):
        best = None
        for (cx, cy, r) in puffs:
            dx, dy = (x - cx) / r, (y - cy) / r
            q = dx * dx + dy * dy
            if q < 1:
                z = math.sqrt(1 - q) * r
                if best is None or z > best[0]:
                    best = (z, (dx, dy, math.sqrt(1 - q)))
        return best
    area = (box[2] - box[0]) * (box[3] - box[1])
    for _ in range(int(area / 30 * density)):
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        if y > bottom:
            continue
        s = surf(x, y)
        if s is None:
            continue
        ex = -under_dark * max(0.0, (y - (bottom - 18)) / 18)
        c = look.color(norm3(s[1]), rnd, ex)
        edge = s[1][2]
        out.append(dab(x, y, rnd.uniform(*size) * (0.5 + 0.5 * edge), c, rnd.uniform(*op) * min(1, 0.25 + edge * 1.2), rnd, 0.7))
    if wisp:
        for _ in range(wisp):
            x, y = rnd.uniform(box[0], box[2]), rnd.uniform(bottom - 10, bottom + 6)
            out.append(stroke(x, y, rnd.uniform(-4, 4), rnd.uniform(30, 90), rnd.uniform(1.5, 3.5),
                              rnd.choice(wisp_cols or [ramp(look.cols, 0.5)]), rnd.uniform(0.2, 0.5)))
    return "".join(out)


def water(D, y0, y1, stops, seed, n=420, refl_x=None, refl_w=80, refl_col="#FFF2C8", glints=120, x0=-20, x1=620, dark_ticks=0.0):
    """Sea / lake: graded base, long horizontal strokes that get shorter and thinner toward the horizon, a broken
    light path under the sun or moon, glints."""
    rnd = random.Random(seed)
    g = D.lin([(o, c) for o, c in stops], 0, y0, 0, y1, "userSpaceOnUse")
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{g}"/>']
    for _ in range(n):
        y = y0 + (rnd.random() ** 1.4) * (y1 - y0)
        t = (y - y0) / max(1, y1 - y0)
        c = gstop(stops, t)
        c = lt(c, rnd.uniform(0.05, 0.2)) if rnd.random() < 0.45 else dk(c, rnd.uniform(0.05, 0.22 + dark_ticks))
        L = 12 + 80 * t * rnd.uniform(0.5, 1.2)
        out.append(stroke(rnd.uniform(x0, x1), y, rnd.uniform(-1.5, 1.5), L, 0.6 + 2.6 * t, c, rnd.uniform(0.25, 0.6), rnd.uniform(-1, 1)))
    if refl_x is not None:
        for _ in range(glints):
            y = y0 + 2 + (rnd.random() ** 1.3) * (y1 - y0)
            t = (y - y0) / max(1, y1 - y0)
            w = refl_w * (0.35 + 1.4 * t)
            x = refl_x + rnd.gauss(0, w * 0.45)
            out.append(stroke(x, y, rnd.uniform(-1, 1), (5 + 38 * t) * rnd.uniform(0.5, 1.3), 0.5 + 1.8 * t, refl_col,
                              rnd.uniform(0.45, 0.95) * max(0.2, 1 - abs(x - refl_x) / (w * 1.4))))
    return "".join(out)


def mist(D, y, h, col, op=0.6, x0=-40, x1=640, seed=1, n=10, r=(90, 200)):
    rnd = random.Random(seed)
    return "".join(halo(D, rnd.uniform(x0, x1), y + rnd.uniform(-h * 0.3, h * 0.3), rnd.uniform(*r), col, op * rnd.uniform(0.5, 1),
                        ry=h * rnd.uniform(0.5, 1), mid=0.5) for _ in range(n))


def shafts(D, src, spans, col, op=0.22):
    """God-rays: translucent wedges from a source to spans [(x0, x1, y), ...]."""
    out = []
    for (x0, x1, y) in spans:
        g = D.lin([(0, col, op), (0.6, col, round(op * 0.5, 3)), (1, col, 0)], src[0], src[1], (x0 + x1) / 2, y, "userSpaceOnUse")
        out.append(f'<path d="M{src[0] - 3:.1f} {src[1]:.1f}L{src[0] + 3:.1f} {src[1]:.1f}L{x1:.1f} {y:.1f}L{x0:.1f} {y:.1f}Z" fill="{g}"/>')
    return "".join(out)


def brushwork(seed, box, cols, n, L=(10, 30), W=(1, 3), op=(0.2, 0.5), angle=0, jit=10, inside=None):
    """Loose strokes in a box (ground, rock streaks, grass beds); inside(x, y) restricts them."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if inside is not None and not inside(x, y):
            continue
        a = angle(x, y) if callable(angle) else angle
        c = cols(x, y, rnd) if callable(cols) else rnd.choice(cols)
        out.append(stroke(x, y, a + rnd.uniform(-jit, jit), rnd.uniform(*L), rnd.uniform(*W), c, rnd.uniform(*op), rnd.uniform(-2, 2)))
    return "".join(out)


def stars(seed, box, n, cols=("#FFFFFF", "#FFF2C8", "#DCE6FF"), r=(0.5, 1.6), op=(0.4, 1.0)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    return "".join(f'<circle cx="{rnd.uniform(x0, x1):.1f}" cy="{rnd.uniform(y0, y1):.1f}" r="{rnd.uniform(*r):.2f}" fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*op):.2f}"/>'
                   for _ in range(n))


def sparkle(cx, cy, r, col, op=1.0):
    k = r * 0.2
    return (f'<path d="M{cx:.1f} {cy - r:.1f}Q{cx + k:.1f} {cy - k:.1f} {cx + r:.1f} {cy:.1f}Q{cx + k:.1f} {cy + k:.1f} {cx:.1f} {cy + r:.1f}'
            f'Q{cx - k:.1f} {cy + k:.1f} {cx - r:.1f} {cy:.1f}Q{cx - k:.1f} {cy - k:.1f} {cx:.1f} {cy - r:.1f}Z" fill="{col}" opacity="{op}"/>')


def foliage(D, blobs, look, seed, density=1.0, size=(3, 8), op=(0.55, 0.95), squash=0.55, holes=None, hole_n=0, base=True):
    """Leaf masses: clumps [(cx, cy, rx, ry)] modelled as domes, painted with leaf-shaped dabs lit by `look`."""
    rnd = random.Random(seed)
    from gouache import blob
    out = []
    if base:
        for (cx, cy, rx, ry) in blobs:
            out.append(f'<path d="{blob(cx, cy, rx * 0.92, ry * 0.92, rnd.randint(0, 9999), 0.14, 16)}" fill="{ramp(look.cols, 0.3)}"/>')

    def surf(x, y):
        best = None
        for (cx, cy, rx, ry) in blobs:
            dx, dy = (x - cx) / rx, (y - cy) / ry
            q = dx * dx + dy * dy
            if q < 1:
                z = math.sqrt(1 - q) * min(rx, ry)
                if best is None or z > best[0]:
                    best = (z, norm3((dx / rx * min(rx, ry), dy / ry * min(rx, ry), math.sqrt(1 - q))))
        return best
    xs = [b[0] - b[2] for b in blobs] + [b[0] + b[2] for b in blobs]
    ys = [b[1] - b[3] for b in blobs] + [b[1] + b[3] for b in blobs]
    box = (min(xs), min(ys), max(xs), max(ys))
    area = (box[2] - box[0]) * (box[3] - box[1])
    for _ in range(int(area / 26 * density)):
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        s = surf(x, y)
        if s is None:
            continue
        c = look.color(s[1], rnd)
        out.append(dab(x, y, rnd.uniform(*size), c, rnd.uniform(*op), rnd, squash))
    if holes and hole_n:
        for _ in range(hole_n):
            x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
            s = surf(x, y)
            if s is None or s[1][2] < 0.4:
                continue
            out.append(dab(x, y, rnd.uniform(1.5, 4), holes, rnd.uniform(0.5, 0.9), rnd, 0.7))
    return "".join(out)


def grass(seed, box, cols, n=60, h=(10, 26), w=(1.2, 2.6), lean=(-0.4, 0.4), op=(0.5, 0.95)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        hh = rnd.uniform(*h)
        l = rnd.uniform(*lean)
        c = cols(x, y, rnd) if callable(cols) else rnd.choice(cols)
        out.append(taper([(x, y), (x + l * hh * 0.4, y - hh * 0.5), (x + l * hh, y - hh)], rnd.uniform(*w), 0.2, c, rnd.uniform(*op)))
    return "".join(out)


def rough(pts, seed, amt=4.0, step=8.0):
    """Roughen a polyline (ridges, rock edges): resample, then displace by low-frequency noise."""
    rnd = random.Random(seed)
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        m = max(1, int(L / step))
        for k in range(m):
            t = k / m
            out.append((x0 + (x1 - x0) * t + rnd.uniform(-amt, amt) * 0.4, y0 + (y1 - y0) * t + rnd.uniform(-amt, amt)))
    out.append(pts[-1])
    return out


# ---------------------------------------------------------------- text
def text(x, y, s, font, size, fill, ls=0, anchor="middle", op=None, extra=""):
    from common import esc
    lsa = f' letter-spacing="{ls}"' if ls else ""
    o = f' opacity="{op}"' if op is not None else ""
    xx = x + ls / 2 if (ls and anchor == "middle") else x
    return f'<text x="{xx:.1f}" y="{y:.1f}" text-anchor="{anchor}" {font} font-size="{size}"{lsa} fill="{fill}"{o}{extra}>{esc(s)}</text>'


def fitted(s, font, size, max_w, ls=0):
    from common import fit_size
    return fit_size(s, font, size, max_w, ls)


def title(D, x, y, s, font, size, max_w=460, ls=0, face=("#FFF4C8", "#E8B850", "#9A6418"), shadow="#100808", sop=0.6,
          glow=None, glow_op=0.5, anchor="middle", outline=None):
    """Hero lettering: soft dark halo behind (legibility), offset deboss shadow, metallic/painted gradient face,
    bright top edge. Returns svg."""
    from common import measure
    fs = fitted(s, font, size, max_w, ls)
    W = measure(s, font, fs, ls)
    out = []
    if glow:
        cx = x if anchor == "middle" else (x + W / 2 if anchor == "start" else x - W / 2)
        out.append(halo(D, cx, y - fs * 0.33, W * 0.62 + 20, glow, glow_op, ry=fs * 0.95, mid=0.55))
    g = D.lin([(0, face[0]), (0.45, face[1]), (0.55, face[1]), (1, face[2])], 0, y - fs * 0.78, 0, y + fs * 0.05, "userSpaceOnUse")
    out.append(text(x + fs * 0.03, y + fs * 0.045, s, font, fs, shadow, ls, anchor, sop))
    if outline:
        out.append(text(x, y, s, font, fs, "none", ls, anchor, extra=f' stroke="{outline[0]}" stroke-width="{outline[1]}" stroke-linejoin="round" stroke-opacity="{outline[2] if len(outline) > 2 else 1}"'))
    out.append(text(x - fs * 0.01, y - fs * 0.016, s, font, fs, lt(face[0], 0.5), ls, anchor, 0.5))
    out.append(text(x, y, s, font, fs, g, ls, anchor))
    return "".join(out)


def subtitle(x, y, s, font, size, fill, max_w=440, ls=0, anchor="middle", sh="#000000", sop=0.5, op=None):
    fs = fitted(s, font, size, max_w, ls)
    return text(x + 1.1, y + 1.6, s, font, fs, sh, ls, anchor, sop) + text(x, y, s, font, fs, fill, ls, anchor, op)


# ---------------------------------------------------------------- varnish
_FILTER = '''<filter id="{fid}" x="0" y="0" width="600" height="600" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency="{bf}" numOctaves="3" seed="{seed}" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="{edge}" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feTurbulence type="fractalNoise" baseFrequency="0.035 0.42" numOctaves="3" seed="{seed2}" result="b"/>
<feColorMatrix in="b" type="matrix" values="0 0 0 0 0.5 0 0 0 0 0.5 0 0 0 0 0.5 0 0 0 {bristle} 0" result="bs"/>
<feComposite in="bs" in2="d" operator="in" result="bs2"/>
<feBlend in="d" in2="bs2" mode="soft-light" result="t"/>
<feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="{seed3}" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0.25 0 0 0 0 0.2 0 0 0 0 0.15 0 0 0 {grain} 0" result="gg"/>
<feComposite in="gg" in2="t" operator="in" result="g3"/>
<feBlend in="t" in2="g3" mode="multiply"/>
</filter>'''


def varnished(art, lettering, fid, seed=3, edge=2.4, freq=0.05, bristle=0.45, grain=0.2):
    """Art goes under a painterly filter (soft brush edges, bristle streaks, pigment grain); lettering stays crisp
    on top. Both are plain svg strings; `art` may contain its own <defs>."""
    f = _FILTER.format(fid=fid, seed=seed, seed2=seed + 17, seed3=seed + 31, edge=edge, bf=freq, bristle=bristle, grain=grain)
    return f'<defs>{f}</defs><g filter="url(#{fid})">{art}</g>{lettering}'


# ---------------------------------------------------------------- feathers and wings
def _lerp(a, b, t):
    return a + (b - a) * t


def _lerp2(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def feather(D, base, ang, L, w, cols, seed, curve=0.06, asym=0.3, tip=0.82, barbs=7, shaft=True, shadow=None, op=1.0,
            lit_side=1, notch=0.0, rim=None, rim_op=0.6, soft=False):
    """One painted feather. cols = (base/shadow, mid, tip/light). curve bends the shaft (fraction of L, + = toward
    the left of the direction of travel); asym narrows the leading vane; tip = where the rounded tip starts.
    shadow = (dx, dy, colour, opacity): a soft cast shadow on what lies below. notch: emargination of outer
    primaries (vane narrows toward the tip)."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    bx, by = base
    m = 9
    axis, Lft, Rgt = [], [], []
    for i in range(m + 1):
        t = i / m
        bend = curve * L * math.sin(t * math.pi * 0.85)
        cx, cy = bx + ux * L * t + nx * bend, by + uy * L * t + ny * bend
        axis.append((cx, cy))
        if t < 0.12:
            k = 0.4 + 0.6 * t / 0.12
        elif t <= tip:
            k = 1.0 - notch * max(0.0, (t - 0.45) / max(0.01, tip - 0.45))
        else:
            k = (1.0 - notch) * math.sqrt(max(0.0, 1 - ((t - tip) / (1 - tip)) ** 2))
        Lft.append((cx + nx * w * k * (1 - asym), cy + ny * w * k * (1 - asym)))
        Rgt.append((cx - nx * w * k * (1 + asym * 0.3), cy - ny * w * k * (1 + asym * 0.3)))
    tipp = (bx + ux * L * 1.01 + nx * curve * L * 0.4, by + uy * L * 1.01 + ny * curve * L * 0.4)
    pts = Lft[1:-1] + [tipp] + Rgt[::-1][1:-1] + [base]
    d = smooth_closed(pts)
    out = []
    if shadow:
        sx, sy, sc, so = shadow
        out.append(f'<path d="{d}" fill="{sc}" opacity="{so}" transform="translate({sx:.1f} {sy:.1f})"/>')
    g = D.lin([(0, cols[0]), (0.5, cols[1]), (1, cols[2])], round(bx, 1), round(by, 1), round(tipp[0], 1), round(tipp[1], 1), "userSpaceOnUse")
    o = f' opacity="{op}"' if op < 1 else ""
    out.append(f'<g{o}><path d="{d}" fill="{g}"/>')
    # barbs: fine strokes angled from the shaft toward the tip, on both vanes
    segs_l, segs_d = [], []
    for k in range(barbs):
        t = rnd.uniform(0.15, 0.9)
        i = int(t * m)
        cx, cy = axis[i]
        side = 1 if rnd.random() < 0.45 else -1
        ww = w * (1 - asym if side > 0 else 1 + asym * 0.3) * rnd.uniform(0.7, 0.95)
        seg = f'M{cx:.1f} {cy:.1f}l{(nx * side * 0.9 + ux * 0.55) * ww:.1f} {(ny * side * 0.9 + uy * 0.55) * ww:.1f}'
        (segs_l if rnd.random() < 0.5 else segs_d).append(seg)
    sw = max(0.5, w * 0.12)
    if segs_l:
        out.append(f'<path d="{"".join(segs_l)}" stroke="{lt(cols[2], 0.25)}" stroke-width="{sw:.1f}" stroke-linecap="round" opacity="0.45"/>')
    if segs_d:
        out.append(f'<path d="{"".join(segs_d)}" stroke="{dk(cols[0], 0.05)}" stroke-width="{sw:.1f}" stroke-linecap="round" opacity="0.3"/>')
    # the edge facing the light catches it; the other side is a soft darker line
    lit_edge = Lft if lit_side > 0 else Rgt
    dark_edge = Rgt if lit_side > 0 else Lft
    if rim_op > 0:
        out.append(f'<path d="{smooth_open(lit_edge[4:] + [tipp])}" fill="none" stroke="{rim or lt(cols[2], 0.35)}" stroke-width="{max(0.6, w * (0.09 if soft else 0.14)):.1f}" stroke-linecap="round" opacity="{rim_op:.2f}"/>')
    out.append(f'<path d="{smooth_open(dark_edge[2:])}" fill="none" stroke="{dk(cols[0], 0.15)}" stroke-width="{max(0.5, w * (0.07 if soft else 0.1)):.1f}" opacity="{0.22 if soft else 0.35}"/>')
    if shaft:
        mx, my = axis[m // 2]
        ex, ey = axis[-2]
        out.append(f'<path d="M{bx:.1f} {by:.1f}Q{mx:.1f} {my:.1f} {ex:.1f} {ey:.1f}" stroke="{lt(cols[1], 0.4)}" stroke-width="{max(0.6, w * 0.1):.1f}" fill="none" opacity="0.55"/>')
    out.append("</g>")
    return "".join(out)


def wing(D, S, E, Wr, T, cols, seed, trail=1, light=(0.6, -0.6), n_prim=11, n_sec=14, n_ter=3, prim_len=(150, 205),
         sec_len=(118, 130), ter_len=(90, 70), feather_w=0.12, dark=0.0, shade_amt=0.22, cover=1.0, shadow_col="#202040",
         lit_rim=None, curl=0.0, fan=1.0, emarg=3, glaze=0.4, rim_op=0.5,
         rows=((0.42, 2.4, 0.02, 0.14, 0.92), (0.24, 2.9, 0.06, 0.42, 0.96))):
    """A bird / angel wing seen from above, painted the way a painter builds it: flight feathers laid back to
    front with soft gradients (base in shadow, tips catching light), rows of coverts, the soft lesser-covert
    shoulder, then a unifying glaze (shadow toward the root, light along the leading edge).
    S shoulder, E elbow, Wr wrist, T hand tip (canvas coords). trail = +1 / -1 picks the side of the forearm the
    flight feathers hang from. cols = ramp dark->light. light = direction the light comes from."""
    rnd = random.Random(seed)
    lx, ly = light
    ll = math.hypot(lx, ly) or 1
    lx, ly = lx / ll, ly / ll

    def ang_of(p, q):
        return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
    fa = ang_of(E, Wr)
    perp = fa + 90 * trail
    hand = ang_of(Wr, T)
    cxw = (S[0] + E[0] + Wr[0] + T[0]) / 4
    cyw = (S[1] + E[1] + Wr[1] + T[1]) / 4
    span = max(60.0, math.hypot(T[0] - S[0], T[1] - S[1]))

    def tone(p, ang, L, base_dark, contrast=1.0):
        a = math.radians(ang)
        tx_, ty_ = p[0] + math.cos(a) * L * 0.6, p[1] + math.sin(a) * L * 0.6
        s = ((tx_ - cxw) * lx + (ty_ - cyw) * ly) / (span * 0.6)
        v = 0.55 + shade_amt * max(-1.2, min(1.2, s)) - dark - base_dark + rnd.uniform(-0.035, 0.035)
        return (ramp(cols, v - 0.2 * contrast), ramp(cols, v), ramp(cols, v + 0.16 * contrast))
    sh = (-lx * 1.6, -ly * 1.6, shadow_col, 0.14)
    out = []
    flights, tips = [], []
    for j in range(n_prim - 1, -1, -1):
        t = j / max(1, n_prim - 1)
        b = _lerp2(Wr, T, 0.04 + 0.92 * t ** 0.9)
        da = ((hand - perp + 540) % 360) - 180
        ang = perp + da * (0.1 + 0.88 * t ** 1.25) * fan + rnd.uniform(-1.5, 1.5) + curl * t * 20
        L = _lerp(prim_len[0], prim_len[1], math.sin(t * math.pi * 0.62) / math.sin(math.pi * 0.62)) * rnd.uniform(0.98, 1.02)
        w = L * feather_w * (0.8 if j >= n_prim - emarg else 1.0)
        flights.append(("p", j, b, ang, L, w))
    for j in range(n_sec):
        t = j / max(1, n_sec - 1)
        b = _lerp2(Wr, E, 0.02 + 0.96 * t)
        ang = perp + rnd.uniform(-2, 2) - 12 * trail * (1 - t) + 4 * trail * t
        L = _lerp(sec_len[0], sec_len[1], t) * rnd.uniform(0.97, 1.03)
        flights.append(("s", j, b, ang, L, L * feather_w * 1.3))
    for j in range(n_ter):
        t = j / max(1, n_ter - 1)
        b = _lerp2(E, S, 0.08 + 0.55 * t)
        ang = perp + 16 * trail * (t + 0.6) + rnd.uniform(-3, 3)
        L = _lerp(ter_len[0], ter_len[1], t)
        flights.append(("t", j, b, ang, L, L * feather_w * 1.5))
    # silhouette of the whole wing (for the glaze): leading edge then the feather tips back to the root
    for kind, j, b, ang, L, w in flights:
        a = math.radians(ang)
        tips.append((b[0] + math.cos(a) * L, b[1] + math.sin(a) * L))
    lead = resample([S, _lerp2(S, Wr, 0.5), Wr, T], 5, closed=False)
    sil = lead + [tips[0]] + tips[1:][:] + [S]
    for kind, j, b, ang, L, w in flights:
        c = tone(b, ang, L, {"p": 0.0, "s": 0.04, "t": 0.07}[kind])
        out.append(feather(D, b, ang, L, w, c, seed + 10 + j + {"p": 0, "s": 30, "t": 60}[kind], curve=(-0.05 if kind == "p" else 0.04) * trail,
                           asym=0.36 if kind == "p" else 0.14, tip=0.8 if kind == "p" else 0.72,
                           notch=0.22 if (kind == "p" and j >= n_prim - emarg) else 0.0, shadow=sh, barbs=9, lit_side=-trail,
                           rim=lit_rim, rim_op=rim_op * 0.5, soft=True))
    # coverts: greater, median (each one a soft, short, broad feather), nearer the leading edge each row
    seq = sorted(flights, key=lambda f: -math.hypot(f[2][0] - S[0], f[2][1] - S[1]))
    for r_i, (lf, wf, dd, push, op) in enumerate(rows):
        for k, (kind, j, b, ang, L, w) in enumerate(seq):
            if r_i >= 1 and k % 2:
                continue
            a = math.radians(ang)
            bb = (b[0] - math.cos(a) * L * push * 0.3, b[1] - math.sin(a) * L * push * 0.3)
            LL = min(L * lf, 64) * cover * rnd.uniform(0.92, 1.06)
            c = tone(bb, ang, LL, dd, 0.8)
            out.append(feather(D, bb, ang + rnd.uniform(-3, 3), LL, LL * 0.13 * wf, c, seed + 100 + r_i * 60 + k, curve=0.02, asym=0.05,
                               tip=0.5, shadow=(sh[0] * 0.8, sh[1] * 0.8, shadow_col, 0.16), barbs=3, shaft=r_i == 0, lit_side=-trail,
                               rim=lit_rim, rim_op=rim_op * 0.35, soft=True, op=op))
    # lesser coverts: the soft rounded shoulder of the wing along the leading edge
    a1 = math.radians(perp)
    off = 24 * cover
    lead2 = resample([S, _lerp2(S, Wr, 0.5), Wr, _lerp2(Wr, T, 0.22)], 6, closed=False)
    n2 = len(lead2)
    back = [(p[0] + math.cos(a1) * off * (1.0 - 0.5 * i / n2), p[1] + math.sin(a1) * off * (1.0 - 0.5 * i / n2)) for i, p in enumerate(lead2)]
    mass = lead2 + back[::-1]
    mlook = Look(cols, key=(lx, ly, 0.75), amb=0.3, wrap=0.6, jit=0.02)
    out.append(paint(D, mass, mlook.darker(dark * 0.8), seed + 300, round_r=12, flow="contour", flow_jit=8,
                     passes=((80, (6, 12), (2, 3.5), (0.35, 0.6)), (240, (3, 6), (1, 2), (0.45, 0.8))), edge_col=ramp(cols, 0.25),
                     edge_w=1.0, edge_op=0.15, rim_col=lit_rim, rim_w=1.2, rim_op=rim_op * 0.4, under=True))
    for i in range(1, n2 - 1):
        p, q = lead2[i], back[i]
        for k in (0.4, 0.78):
            x_, y_ = _lerp2(p, q, k + rnd.uniform(-0.06, 0.06))
            r_ = 4 + 3 * k
            c = ramp(cols, 0.38 - dark + rnd.uniform(-0.05, 0.05))
            out.append(f'<path d="M{x_ - math.sin(a1) * r_:.1f} {y_ + math.cos(a1) * r_:.1f}Q{x_ + math.cos(a1) * r_ * 1.5:.1f} {y_ + math.sin(a1) * r_ * 1.5:.1f} {x_ + math.sin(a1) * r_:.1f} {y_ - math.cos(a1) * r_:.1f}" '
                       f'stroke="{c}" stroke-width="1.1" fill="none" opacity="0.32"/>')
    # unifying glaze: shadow pooled toward the root and the trailing side, light along the leading edge
    if glaze:
        cid = D.clip(smooth_closed(sil) if False else poly_d(sil))
        g1 = D.rad([(0, shadow_col, glaze), (0.5, shadow_col, round(glaze * 0.4, 3)), (1, shadow_col, 0)], S[0], S[1], span * 0.75, "userSpaceOnUse")
        g2 = D.lin([(0, cols[-1], round(glaze * 0.5, 3)), (0.35, cols[-1], 0)], Wr[0] + lx * 30, Wr[1] + ly * 30,
                   Wr[0] + math.cos(a1) * span * 0.6, Wr[1] + math.sin(a1) * span * 0.6, "userSpaceOnUse")
        out.append(f'<g {cid}><rect x="{min(p[0] for p in sil) - 5:.0f}" y="{min(p[1] for p in sil) - 5:.0f}" width="{max(p[0] for p in sil) - min(p[0] for p in sil) + 10:.0f}" height="{max(p[1] for p in sil) - min(p[1] for p in sil) + 10:.0f}" fill="{g1}"/>'
                   f'<rect x="{min(p[0] for p in sil) - 5:.0f}" y="{min(p[1] for p in sil) - 5:.0f}" width="{max(p[0] for p in sil) - min(p[0] for p in sil) + 10:.0f}" height="{max(p[1] for p in sil) - min(p[1] for p in sil) + 10:.0f}" fill="{g2}"/></g>')
    # the leading edge catches the light
    out.append(taper(resample([_lerp2(S, Wr, 0.2), _lerp2(S, Wr, 0.55), Wr, _lerp2(Wr, T, 0.5)], 5, closed=False), 1.2, 3.0, lit_rim or cols[-1], rim_op * 0.6, mid=3.4))
    return "".join(out)


# ---------------------------------------------------------------- the horse (true anatomy, flying / leaping pose)
def horse_head(P, th, k=1.0):
    """Canonical horse head (pointing right, poll at origin, length 64*k), rotated th degrees nose-down."""
    a = math.radians(th)
    c, s = math.cos(a), math.sin(a)
    can = [(14, 1), (30, 4), (50, 7), (56, 9), (62, 13), (64, 19), (63, 24), (60, 26), (56, 29), (50, 28), (40, 30), (30, 34),
           (20, 39), (10, 38), (3, 30)]
    return [(P[0] + (c * x - s * y) * k, P[1] + (s * x + c * y) * k) for x, y in can]


def head_pt(P, th, x, y, k=1.0):
    a = math.radians(th)
    c, s = math.cos(a), math.sin(a)
    return (P[0] + (c * x - s * y) * k, P[1] + (s * x + c * y) * k)


HORSE_POSE = dict(
    poll=(72, -70), head_th=50, head_k=1.06,
    crest=[(0, -3), (10, -14), (22, -34), (38, -52), (54, -66), (66, -73)],
    top=[(-100, 12), (-88, 0), (-74, -2), (-58, 4), (-40, 8), (-24, 7), (-10, 2)],
    front=[(48, -22), (50, -4), (53, 16), (56, 32), (59, 44), (57, 56), (48, 66), (34, 72), (18, 76), (4, 78), (-20, 80),
           (-40, 76), (-54, 66), (-70, 74), (-88, 70), (-104, 52), (-108, 32)],
    fore_near=[(14, 64, 30), (38, 66, 24), (62, 66, 19), (72, 70, 17), (70, 84, 13.5), (64, 100, 12.5), (60, 108, 15.5), (51, 115, 11.5), (43, 119, 12.5)],
    fore_far=[(20, 60, 28), (44, 54, 22), (66, 46, 18), (76, 50, 17), (80, 64, 13.5), (82, 80, 12.5), (82, 88, 15.5), (78, 98, 11.5), (73, 105, 12.5)],
    thigh=[(-70, 18), (-54, 44), (-52, 64), (-60, 80), (-78, 92), (-98, 100), (-116, 104), (-130, 104), (-136, 96), (-128, 84), (-120, 72),
           (-114, 56), (-110, 40), (-100, 24), (-84, 14)],
    hind_near=[(-124, 100, 17), (-146, 105, 12.5), (-160, 108, 12), (-166, 110, 15.5), (-178, 113, 11), (-186, 115, 12.5)],
    hind_far=[(-70, 80, 32), (-88, 94, 24), (-104, 104, 17), (-114, 110, 17), (-134, 120, 12.5), (-146, 126, 12), (-152, 129, 15.5),
              (-163, 134, 11), (-171, 137, 12.5)],
)


def horse(D, ox, oy, s, ang, look, seed, pose=None, far_dark=0.22, edge_col="#2A2440", hoof_cols=("#8A8296", "#3E384E", "#16141E"),
          mane_cols=None, eye_col="#120E18", wind=(-1.0, 0.35), mane_len=(40, 64), tail=True, tail_cols=None, tail_guide=None,
          rim_col=None, bumps_k=1.0, color_fn=None, coat_jit=10, value_fn=None):
    """Paint a horse. Local frame: withers at (0, 0), facing right, head length ~68, body length ~160; then
    scaled by s, rotated by ang (deg, screen) and moved to (ox, oy). Returns dict of svg layers:
    far (far legs), tail, body (body, thigh, near legs, head detail), mane; paint far -> tail -> body -> mane
    (put a far wing before `far` and a near wing after `mane`). Also returns 'pt' (local -> canvas function)."""
    P = dict(HORSE_POSE)
    P.update(pose or {})

    def T(pts):
        return xform(pts, ox, oy, s, ang)

    def T1(p):
        return T([p])[0]
    lx, ly = look.key[0], look.key[1]
    far_look = look.darker(far_dark)

    def bump(cx, cy, rx, ry, rot, amp):
        c = T1((cx, cy))
        return (c[0], c[1], rx * s, ry * s, rot + ang, amp * s * bumps_k)

    def hoof(joints, lk, sd):
        (x2, y2, w2), (x1, y1, w1) = joints[-1], joints[-2]
        a = math.atan2(y2 - y1, x2 - x1)
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        hw = w2 * 0.52

        def q(u, v):
            return (x2 + ux * u * w2 + nx * v * hw, y2 + uy * u * w2 + ny * v * hw)
        hp = T([q(-0.15, 1.0), q(0.55, 1.12), q(0.95, 0.75), q(1.0, -0.3), q(0.7, -1.0), q(-0.15, -1.0)])
        g = D.lin([(0, hoof_cols[0]), (0.5, hoof_cols[1]), (1, hoof_cols[2])], 0, 0, 0.5, 1)
        o = f'<path d="{smooth_closed(hp)}" fill="{g}"/>'
        o += edges(resample(hp, 2), (lx, ly), sd, hoof_cols[2], None, 1.2 * s, dark_op=0.7)
        o += taper([hp[0], _lerp2(hp[0], hp[5], 0.5), hp[5]], 2.6 * s, 2.0 * s, ramp(lk.cols, 0.7), 0.7)
        o += taper([_lerp2(hp[1], hp[2], 0.3), _lerp2(hp[1], hp[2], 0.8)], 1.2 * s, 0.4 * s, hoof_cols[0], 0.6)
        return o

    def limb(joints, lk, sd, bmp=(), hide=1):
        pts = T(limb_outline(joints))
        b = [bump(*q) for q in bmp]
        r = max(j[2] for j in joints) * s * 0.5
        top = T1(joints[0][:2])
        hid = math.hypot(*(a - b_ for a, b_ in zip(T1(joints[hide][:2]), top)))

        def mask(x, y):
            return math.hypot(x - top[0], y - top[1]) > hid * 0.9
        o = paint(D, pts, lk, sd, round_r=r * 0.9, bumps=b, flow="contour", flow_jit=8, edge_col=edge_col, edge_w=1.7 * s,
                  edge_op=0.6, edge_mask=mask, rim_col=rim_col, rim_w=1.4 * s, rim_op=0.55, color_fn=color_fn, value_fn=value_fn,
                  passes=((60, (10, 20), (2.5, 5), (0.3, 0.55)), (230, (5, 12), (1.2, 2.6), (0.4, 0.8)), (90, (3, 6), (0.8, 1.6), (0.5, 0.85))))
        return o + hoof(joints, lk, sd)
    out = {}
    out["far"] = (limb(P["hind_far"], far_look, seed + 1, ((-80, 88, 16, 10, 40, 6),), hide=1) +
                  limb(P["fore_far"], far_look, seed + 2, ((40, 56, 18, 9, -15, 5),), hide=1))
    # body: topline, crest, head, throat, chest, belly
    head = horse_head(P["poll"], P["head_th"], P["head_k"])
    body_local = P["top"] + P["crest"] + head + P["front"]
    body = T(body_local)
    hk = P["head_k"]
    hp = lambda x, y: head_pt(P["poll"], P["head_th"], x, y, hk)
    jowl = hp(18, 26)
    bmp = [bump(30, 30, 30, 40, 50, 9), bump(-16, 44, 52, 34, 0, 7), bump(-84, 40, 30, 36, 10, 12), bump(30, -32, 44, 16, -48, 7),
           bump(jowl[0], jowl[1], 15, 13, P["head_th"], 7), bump(*hp(38, 14), 26, 9, P["head_th"], 4), bump(*hp(58, 18), 9, 8, 0, 4),
           bump(4, 4, 18, 14, 0, 4)]
    o = []
    o.append(paint(D, body, look, seed + 3, round_r=34 * s, bumps=bmp, flow="contour", flow_jit=coat_jit, edge_col=edge_col,
                   edge_w=2.0 * s, edge_op=0.6, rim_col=rim_col, rim_w=1.8 * s, rim_op=0.6, color_fn=color_fn, value_fn=value_fn,
                   passes=((40, (20, 40), (5, 10), (0.25, 0.42)), (200, (10, 22), (2, 4), (0.28, 0.55)), (90, (5, 10), (1, 2.2), (0.35, 0.65)))))
    # thigh / gaskin mass of the near hind, then its lower leg; near foreleg
    o.append(paint(D, T(P["thigh"]), look, seed + 4, round_r=26 * s, bumps=[bump(-92, 52, 24, 34, 15, 8), bump(-96, 92, 26, 9, 20, 4)],
                   flow="contour", flow_jit=coat_jit, edge_col=edge_col, edge_w=1.9 * s, edge_op=0.55, rim_col=rim_col, rim_w=1.6 * s,
                   rim_op=0.55, color_fn=color_fn, value_fn=value_fn, edge_mask=None, edge_thresh=-0.15,
                   passes=((30, (16, 30), (4, 8), (0.25, 0.45)), (220, (7, 16), (1.6, 3.2), (0.3, 0.62)), (110, (4, 8), (1, 2), (0.4, 0.75)))))
    o.append(limb(P["hind_near"], look, seed + 5, hide=0))
    o.append(limb(P["fore_near"], look, seed + 6, ((38, 68, 22, 11, 0, 6),), hide=1))
    # anatomy accents (drawn in local then transformed): shoulder blade spine, elbow, rib hints, stifle, gaskin
    acc = ramp(look.cols, 0.22)
    hl = ramp(look.cols, 1.0)
    for pts, w, op, col in (([(6, 6), (22, 26), (40, 46)], 2.2, 0.18, acc), ([(44, 50), (40, 60), (30, 66)], 1.8, 0.2, acc),
                            ([(-12, 50), (-10, 64), (-12, 74)], 1.4, 0.1, acc), ([(-28, 48), (-27, 62), (-28, 72)], 1.4, 0.09, acc),
                            ([(-62, 48), (-60, 62), (-64, 74)], 2.0, 0.2, acc), ([(-96, 66), (-108, 84), (-120, 96)], 1.6, 0.18, acc),
                            ([(12, -16), (26, -36), (42, -54), (58, -67)], 2.4, 0.35, hl), ([(-96, 2), (-80, -3), (-62, 2)], 2.2, 0.3, hl)):
        o.append(taper(resample(T(pts), 4, closed=False), w * s, w * s * 0.3, col, op))
    # head detail: eye under a bony brow, nostril, mouth, chin groove, cheek
    ex, ey = hp(19, 11)
    a = P["head_th"] + ang
    def rp(dx, dy):
        r = math.radians(a)
        return (ex + (dx * math.cos(r) - dy * math.sin(r)) * s * hk * 1.25, ey + (dx * math.sin(r) + dy * math.cos(r)) * s * hk * 1.25)
    o.append(f'<path d="{smooth_closed([rp(-7, 2), rp(-1, -4), rp(7, -3), rp(8, 3), rp(0, 5)])}" fill="{ramp(look.cols, 0.25)}" opacity="0.5"/>')
    o.append(f'<path d="{smooth_open([rp(-8, -4), rp(0, -7.5), rp(8, -5)])}" stroke="{hl}" stroke-width="{2.2 * s:.1f}" fill="none" opacity="0.7"/>')
    o.append(f'<path d="{smooth_closed([rp(-5, 1), rp(-1, -2.4), rp(4.5, -1.5), rp(5.5, 1), rp(0.5, 2.6)])}" fill="{eye_col}"/>')
    o.append(f'<circle cx="{rp(1.5, -0.8)[0]:.1f}" cy="{rp(1.5, -0.8)[1]:.1f}" r="{0.9 * s:.1f}" fill="#FFFFFF" opacity="0.85"/>')
    nx_, ny_ = hp(57, 15)
    r = math.radians(a)
    def rp2(dx, dy, c=(nx_, ny_)):
        return (c[0] + (dx * math.cos(r) - dy * math.sin(r)) * s * hk, c[1] + (dx * math.sin(r) + dy * math.cos(r)) * s * hk)
    o.append(f'<path d="{smooth_open([rp2(-3, -2), rp2(1, -3), rp2(3, 0), rp2(0, 2.5)])}" stroke="{ramp(look.cols, 0.12)}" stroke-width="{2.0 * s:.1f}" fill="none" stroke-linecap="round" opacity="0.65"/>')
    o.append(f'<path d="{smooth_open([rp2(-2, 8), rp2(3, 9), rp2(6, 8)])}" stroke="{ramp(look.cols, 0.15)}" stroke-width="{1.1 * s:.1f}" fill="none" opacity="0.5"/>')
    o.append(taper(T([hp(8, 33), hp(20, 36), hp(32, 31), hp(40, 28)]), 1.8 * s, 0.6 * s, acc, 0.3))
    o.append(taper(T([hp(16, 8), hp(28, 14), hp(36, 24)]), 1.4 * s, 0.4 * s, acc, 0.18))
    # ears: far ear first, near ear pricked forward
    for (bx_, by_, tx_, ty_, dkk, sd) in ((-3, -1, 0, -22, 0.2, 31), (4, -3, 11, -24, 0.0, 32)):
        base = hp(bx_, by_)
        ep_local = [(bx_ - 6, by_ + 3), (bx_ - 6.5, by_ - 7), (tx_ - 1.5, ty_ + 4), (tx_, ty_), (tx_ + 3, ty_ + 5), (bx_ + 6, by_ - 6), (bx_ + 6, by_ + 3)]
        ep = T([head_pt(P["poll"], 0, x, y, hk) for x, y in ep_local])
        # ears stand up from the poll regardless of head angle: build them unrotated around the poll
        lk2 = look.darker(dkk)
        o.append(paint(D, ep, lk2, seed + sd, round_r=5 * s, flow="contour", edge_col=edge_col, edge_w=1.0 * s, edge_op=0.45,
                       passes=((400, (4, 8), (1, 2), (0.5, 0.85)),)))
        inner = T([head_pt(P["poll"], 0, x, y, hk) for x, y in ((bx_ + 0.5, by_ - 3), (tx_ - 0.5, ty_ + 7), (bx_ + 3, by_ - 6))])
        o.append(taper(inner, 3.2 * s, 0.6 * s, ramp(look.cols, 0.35), 0.45))
    out["body"] = "".join(o)
    # mane: locks rooted along the crest streaming back with the wind
    mc = mane_cols or [ramp(look.cols, 1.0), ramp(look.cols, 0.86), ramp(look.cols, 0.72), ramp(look.cols, 0.5)]
    crest = T([(64, -74), (54, -67), (40, -55), (26, -40), (14, -22), (4, -8)])
    m = []
    rnd = random.Random(seed + 40)
    wx, wy = wind
    wl = math.hypot(wx, wy) or 1
    wx, wy = wx / wl, wy / wl
    g = resample(crest, 4, closed=False)
    def mane_guide(r, t, Ln):
        return (r[0] + wx * Ln * t, r[1] + wy * Ln * t - Ln * 0.22 * math.sin(t * math.pi * 0.9))
    m.append(locks(crest, mane_guide, seed + 41, mc, n=16, L=(mane_len[0] * s, mane_len[1] * s), W=(8 * s, 13 * s), sway=(0.08, 0.18),
                   light=(lx, ly), strands=5))
    # forelock between the ears
    m.append(hair(T([hp(2, -2), hp(10, 2), hp(17, 8)]), 10, 3 * s, seed + 70, [mc[0], mc[1], mc[2]], w=(0.8 * s, 1.8 * s), op=(0.5, 0.9)))
    out["mane"] = "".join(m)
    # tail: from the dock, a painted mass then strands, streaming back with the wind
    if tail:
        tg = tail_guide or [(-100, 14), (-122, 22), (-146, 38), (-170, 50), (-198, 54), (-226, 50)]
        tg = T(tg)
        tc = tail_cols or [ramp(look.cols, 0.95), ramp(look.cols, 0.7), ramp(look.cols, 0.5), ramp(look.cols, 0.28), lt(ramp(look.cols, 1.0), 0.3)]
        tgr = resample(tg, 4, closed=False)
        tl = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(tgr, tgr[1:]))

        def tail_guide_fn(r, t, Ln):
            k = min(len(tgr) - 1, int(t * Ln / tl * (len(tgr) - 1)))
            p = tgr[k]
            return (p[0] + (r[0] - tgr[0][0]) * (1 - t * 0.3), p[1] + (r[1] - tgr[0][1]) * (1 - t * 0.3))
        rts = [(tgr[0][0] + rnd.uniform(-5, 5) * s, tgr[0][1] + rnd.uniform(-5, 5) * s) for _ in range(16)]
        t_out = [taper(tgr[:int(len(tgr) * 0.85)], 12 * s, 10 * s, tc[2], 0.75, mid=24 * s)]
        t_out.append(locks(rts, tail_guide_fn, seed + 82, [tc[4], tc[0], tc[1], tc[2]], L=(tl * 0.7, tl * 1.0), W=(9 * s, 15 * s),
                           sway=(0.05, 0.11), light=(lx, ly), strands=7, spread=0.035))
        out["tail"] = "".join(t_out)
    else:
        out["tail"] = ""
    out["pt"] = T1
    return out


def wing2(D, S, E, Wr, T, cols, seed, trail=1, light=(0.6, -0.6), n_prim=10, n_sec=13, prim_len=(150, 205), sec_len=(118, 130),
          ter_len=(90, 70), dark=0.0, shadow_col="#202040", lit_rim=None, fan=1.0, depth_r=26, notch=(0.25, 0.08),
          covert_rows=4, glaze=0.35, sep_op=0.45, edge_col=None):
    """A wing painted as one form with the feathers suggested, like a painter would: the silhouette (leading
    edge + the scalloped run of feather tips) is modelled as a volume lit by `light`, strokes run along the
    feathers, then feather separations, covert scallops, a glaze and the lit leading edge. Coordinates as wing()."""
    rnd = random.Random(seed)
    lx, ly = light
    ll = math.hypot(lx, ly) or 1
    lx, ly = lx / ll, ly / ll

    def ang_of(p, q):
        return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
    fa = ang_of(E, Wr)
    perp = fa + 90 * trail
    hand = ang_of(Wr, T)
    span = max(60.0, math.hypot(T[0] - S[0], T[1] - S[1]))
    feathers = []           # (base, angle, length, width, kind)
    for j in range(n_prim - 1, -1, -1):          # outermost first (tip of the wing)
        t = j / max(1, n_prim - 1)
        b = _lerp2(Wr, T, 0.04 + 0.92 * t ** 0.9)
        da = ((hand - perp + 540) % 360) - 180
        ang = perp + da * (0.1 + 0.88 * t ** 1.25) * fan + rnd.uniform(-1.5, 1.5)
        L = _lerp(prim_len[0], prim_len[1], math.sin(t * math.pi * 0.62) / math.sin(math.pi * 0.62)) * rnd.uniform(0.98, 1.02)
        feathers.append((b, ang, L, L * 0.12, "p", t))
    for j in range(n_sec):
        t = j / max(1, n_sec - 1)
        b = _lerp2(Wr, E, 0.03 + 0.95 * t)
        ang = perp + rnd.uniform(-2, 2) - 12 * trail * (1 - t) + 4 * trail * t
        L = _lerp(sec_len[0], sec_len[1], t) * rnd.uniform(0.96, 1.04)
        feathers.append((b, ang, L, L * 0.16, "s", t))
    for j in range(3):
        t = j / 2
        b = _lerp2(E, S, 0.1 + 0.55 * t)
        ang = perp + 16 * trail * (t + 0.6) + rnd.uniform(-3, 3)
        L = _lerp(ter_len[0], ter_len[1], t)
        feathers.append((b, ang, L, L * 0.2, "t", t))

    def tip(f, k=1.0):
        b, ang, L = f[0], f[1], f[2]
        a = math.radians(ang)
        return (b[0] + math.cos(a) * L * k, b[1] + math.sin(a) * L * k)

    def side(f, k, sgn):
        b, ang, L, w = f[0], f[1], f[2], f[3]
        a = math.radians(ang)
        c = (b[0] + math.cos(a) * L * k, b[1] + math.sin(a) * L * k)
        return (c[0] - math.sin(a) * w * sgn, c[1] + math.cos(a) * w * sgn)
    # silhouette: leading edge S -> Wr -> T, then each feather's rounded tip with a notch toward the next
    lead = resample([S, _lerp2(S, Wr, 0.5), Wr, T], 6, closed=False)
    sil = list(lead)
    prev = T
    for i, f in enumerate(feathers):
        nk = notch[0] if f[4] == "p" else notch[1]
        a_, b_ = side(f, 0.93, 0.55), side(f, 0.93, -0.55)
        if math.hypot(a_[0] - prev[0], a_[1] - prev[1]) > math.hypot(b_[0] - prev[0], b_[1] - prev[1]):
            a_, b_ = b_, a_
        sil += [a_, tip(f, 1.0), b_]
        if i + 1 < len(feathers):
            g = feathers[i + 1]
            sil.append(_lerp2(tip(f, 1.0 - nk), tip(g, 1.0 - nk), 0.5))
        prev = b_
    sil.append(_lerp2(S, tip(feathers[-1], 0.3), 0.5))
    # feather direction field
    segs = [(f[0], tip(f), f[1]) for f in feathers]

    def flow(x, y, n):
        best, bd = 0.0, 1e9
        for (b, t_, a) in segs:
            vx, vy = t_[0] - b[0], t_[1] - b[1]
            L2 = vx * vx + vy * vy or 1
            u = max(0.0, min(1.0, ((x - b[0]) * vx + (y - b[1]) * vy) / L2))
            d = math.hypot(x - b[0] - vx * u, y - b[1] - vy * u)
            if d < bd:
                bd, best = d, a
        return best
    look = Look(cols, key=(lx, ly, 0.7), amb=0.2, wrap=0.5, jit=0.025, rim=(lit_rim, (lx, ly), 0.6) if lit_rim else None)
    if dark:
        look = look.darker(dark)
    vol = Vol(sil, round_r=depth_r, bumps=[(S[0], S[1], span * 0.35, span * 0.25, fa, depth_r * 0.5)])
    out = [paint(D, sil, look, seed + 1, vol=vol, flow=flow, flow_jit=5, smooth=False,
                 passes=((50, (18, 34), (3, 6), (0.3, 0.5)), (220, (10, 22), (1.2, 2.6), (0.35, 0.65)), (120, (5, 10), (0.8, 1.6), (0.4, 0.75))),
                 edge_col=edge_col or ramp(cols, 0.15), edge_w=1.4, edge_op=0.5, rim_col=lit_rim, rim_w=1.4, rim_op=0.55)]
    cid = D.clip(poly_d(sil))
    acc = []
    sep = ramp(look.cols, 0.12)
    lite = ramp(look.cols, 1.0)
    # flight feather separations: a shadowed line on the covered side, a lit edge on the other (outer half only)
    for i, f in enumerate(feathers):
        b, ang, L, w, kind, t = f
        k0 = 0.42 if kind == "p" else 0.5
        line = [side(f, k, -trail * 0.85) for k in (k0, k0 + 0.2, 0.75, 0.93)]
        acc.append(taper(line, 1.6, 0.5, sep, sep_op * rnd.uniform(0.7, 1.0)))
        line = [side(f, k, trail * 0.7) for k in (k0 + 0.1, 0.7, 0.92)]
        acc.append(taper(line, 1.1, 0.3, lite, 0.35 * rnd.uniform(0.6, 1.0)))
        # shaft
        acc.append(taper([tip(f, k0), tip(f, 0.7), tip(f, 0.93)], 1.0, 0.3, lite, 0.3))
        # barbs: a few slanted strokes
        for _ in range(4):
            k = rnd.uniform(k0, 0.92)
            p0 = tip(f, k)
            q0 = side(f, k + 0.08, rnd.choice((-1, 1)) * 0.9)
            acc.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f}L{q0[0]:.1f} {q0[1]:.1f}" stroke="{rnd.choice((sep, lite))}" stroke-width="0.7" opacity="0.25"/>')
    # covert scallops: rows of soft U-marks, smaller toward the leading edge
    for r_i in range(covert_rows):
        k = 0.36 - r_i * 0.085
        for i, f in enumerate(feathers):
            if r_i >= 2 and i % 2:
                continue
            b, ang, L, w, kind, t = f
            L2 = min(L, 150)
            a = math.radians(ang)
            c = (b[0] + math.cos(a) * L2 * k, b[1] + math.sin(a) * L2 * k)
            r = max(3.0, w * (1.05 - r_i * 0.18))
            nx, ny = -math.sin(a), math.cos(a)
            p1 = (c[0] + nx * r - math.cos(a) * r * 0.4, c[1] + ny * r - math.sin(a) * r * 0.4)
            p2 = (c[0] - nx * r - math.cos(a) * r * 0.4, c[1] - ny * r - math.sin(a) * r * 0.4)
            q = (c[0] + math.cos(a) * r * 1.3, c[1] + math.sin(a) * r * 1.3)
            acc.append(f'<path d="M{p1[0]:.1f} {p1[1]:.1f}Q{q[0]:.1f} {q[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}" stroke="{sep}" stroke-width="{1.4 - r_i * 0.2:.1f}" fill="none" opacity="{0.3 - r_i * 0.04:.2f}"/>')
            q2 = (c[0] + math.cos(a) * r * 0.9 - lx * 1.5, c[1] + math.sin(a) * r * 0.9 - ly * 1.5)
            acc.append(f'<path d="M{p1[0]:.1f} {p1[1]:.1f}Q{q2[0]:.1f} {q2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}" stroke="{lite}" stroke-width="0.9" fill="none" opacity="0.22"/>')
    if glaze:
        g1 = D.rad([(0, shadow_col, glaze), (0.55, shadow_col, round(glaze * 0.35, 3)), (1, shadow_col, 0)], S[0], S[1], span * 0.7, "userSpaceOnUse")
        x0, y0, x1, y1 = bbox(sil)
        acc.append(f'<rect x="{x0 - 4:.0f}" y="{y0 - 4:.0f}" width="{x1 - x0 + 8:.0f}" height="{y1 - y0 + 8:.0f}" fill="{g1}"/>')
    out.append(f'<g {cid}>{"".join(acc)}</g>')
    out.append(taper(resample([S, _lerp2(S, Wr, 0.5), Wr, _lerp2(Wr, T, 0.6)], 5, closed=False), 4.5, 1.0, lit_rim or cols[-1], 0.5))
    return "".join(out)


def locks(roots, guide_fn, seed, cols, n=None, L=(40, 60), W=(8, 13), sway=(0.08, 0.2), light=(0.6, -0.6), strands=6,
          wisp=1.15, op=1.0, spread=0.0):
    """Flowing locks of hair (mane, tail, a girl's hair): each lock is a painted ribbon with a shadowed underside,
    a body tone, a sheen toward the light and fine strands running off its tip.
    roots: list of root points (one lock each, or n locks spread along them). guide_fn(root, t, L) -> point at
    fraction t of a lock of length L (the lock's main path); sway adds a travelling S-curve. cols = (sheen, light,
    mid, shadow)."""
    rnd = random.Random(seed)
    lx, ly = light
    ll = math.hypot(lx, ly) or 1
    lx, ly = lx / ll, ly / ll
    if n is not None:
        g = resample(roots, 3, closed=False) if len(roots) > 1 else roots
        rts = [g[min(len(g) - 1, int((i + rnd.uniform(-0.3, 0.3)) / max(1, n - 1) * (len(g) - 1)))] for i in range(n)]
    else:
        rts = roots
    out = []
    order = list(range(len(rts)))
    for i in order:
        r = rts[i]
        Ln = rnd.uniform(*L)
        Wd = rnd.uniform(*W)
        ph = rnd.uniform(0, 6.28)
        am = rnd.uniform(*sway)
        lat = rnd.uniform(-1, 1) * spread
        pts = []
        for k in range(12):
            t = k / 11
            p = guide_fn(r, t, Ln)
            q = guide_fn(r, min(1, t + 0.05), Ln)
            dx, dy = q[0] - p[0], q[1] - p[1]
            dl = math.hypot(dx, dy) or 1
            nx, ny = -dy / dl, dx / dl
            o = math.sin(ph + t * 2 * math.pi * 1.1) * Ln * am * t + lat * Ln * t
            pts.append((p[0] + nx * o, p[1] + ny * o))
        line = resample(pts, 3, closed=False)
        out.append(taper(line, Wd, 0.8, cols[3], 0.62 * op, mid=Wd * 0.95))
        sh = [(x - lx * Wd * 0.2, y - ly * Wd * 0.2) for x, y in line]
        out.append(taper(sh, Wd * 0.72, 0.6, cols[2] if i % 3 else cols[1], 0.85 * op, mid=Wd * 0.7))
        hl = [(x - lx * Wd * 0.33, y - ly * Wd * 0.33) for x, y in line[int(len(line) * 0.1): int(len(line) * 0.7)]]
        if len(hl) > 2:
            out.append(taper(hl, Wd * 0.22, 0.3, cols[0], 0.75 * op, mid=Wd * 0.3))
        # wisps off the end, and a few strands down the lock
        ext = [guide_fn(r, t, Ln) for t in (0.55, 0.8, 1.0, wisp)]
        out.append(hair(pts[5:] + [(ext[-1][0] + (pts[-1][0] - ext[2][0]), ext[-1][1] + (pts[-1][1] - ext[2][1]))], strands, Wd * 0.35,
                        seed + 7 * i, [cols[0], cols[1], cols[3]], w=(0.4, 1.0), op=(0.3 * op, 0.75 * op), start=(0, 0.3), end=(0.85, 1.0)))
    return "".join(out)


# ---------------------------------------------------------------- outlines from blobs (clouds, foliage, rocks)
def union_outline(circles=(), polys=(), step=3.0, smooth_px=2.0, all_parts=False):
    """Outline of the union of circles / ellipses [(cx, cy, rx[, ry[, rot]])] and polygons, traced on a grid.
    Returns the largest outline (or every outline with all_parts) as point lists."""
    xs, ys = [], []
    for c in circles:
        r = max(c[2], c[3] if len(c) > 3 else c[2])
        xs += [c[0] - r, c[0] + r]
        ys += [c[1] - r, c[1] + r]
    for p in polys:
        xs += [q[0] for q in p]
        ys += [q[1] for q in p]
    ox, oy = min(xs) - 6, min(ys) - 6
    W, H = int(max(xs) - ox + 8), int(max(ys) - oy + 8)
    m = np.zeros((H, W), np.uint8)
    for c in circles:
        rx = c[2]
        ry = c[3] if len(c) > 3 else rx
        rot = c[4] if len(c) > 4 else 0
        cv2.ellipse(m, (int(round((c[0] - ox) * 4)), int(round((c[1] - oy) * 4))), (int(rx * 4), int(ry * 4)), rot, 0, 360, 255, -1, cv2.LINE_8, 2)
    for p in polys:
        cv2.fillPoly(m, [np.round(np.array([[(x - ox) * 4, (y - oy) * 4] for x, y in p])).astype(np.int32)], 255, cv2.LINE_8, 2)
    if smooth_px:
        m = cv2.GaussianBlur(m, (0, 0), smooth_px)
        m = (m > 127).astype(np.uint8) * 255
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cs = sorted(cs, key=lambda c: -cv2.contourArea(c))
    res = []
    for c in (cs if all_parts else cs[:1]):
        pts = [(float(q[0][0]) + ox, float(q[0][1]) + oy) for q in c]
        out, acc = [pts[0]], 0.0
        for a, b in zip(pts, pts[1:]):
            acc += math.hypot(b[0] - a[0], b[1] - a[1])
            if acc >= step:
                out.append(b)
                acc = 0.0
        if len(out) >= 4:
            res.append(out)
    return res if all_parts else (res[0] if res else [])


def cumulus(D, puffs, look, seed, flat_y=None, density=1.0, round_r=None, rim=None, dab_r=(3, 9), edge_soft=True, base_op=1.0,
            shade_under=0.25, bumps=True, dab_op=(0.3, 0.7), rim_w=2.4):
    """A cumulus mass modelled as one lit volume: union of puffs [(cx, cy, r)], each puff a dome (so the cloud has
    sunlit tops and shadowed creases), flat shaded base at flat_y; painted with soft dabs, edges dissolving."""
    rnd = random.Random(seed)
    circ = [(x, y, r) for x, y, r in puffs]
    polys = []
    if flat_y is not None:
        circ = []
        for x, y, r in puffs:
            circ.append((x, y, r))
        x0 = min(x - r for x, y, r in puffs)
        x1 = max(x + r for x, y, r in puffs)
        polys = [[(x0 - 50, flat_y), (x1 + 50, flat_y), (x1 + 50, flat_y + 400), (x0 - 50, flat_y + 400)]]
    o = union_outline(circ, step=3.0, smooth_px=3.0)
    if flat_y is not None:
        o = [(x, min(y, flat_y)) for x, y in o]
    R = round_r or max(r for _, _, r in puffs) * 0.8
    bm = [(x, y, r, r, 0, r * 0.45) for x, y, r in puffs] if bumps else []
    vol = Vol(o, round_r=R, bumps=bm, blur=R * 0.18)
    fy = flat_y if flat_y is not None else max(y + r for x, y, r in puffs)

    def vf(x, y):
        return -shade_under * max(0.0, 1 - (fy - y) / 22.0)
    g = D.lin([(0, ramp(look.cols, 0.75)), (0.6, ramp(look.cols, 0.45)), (1, ramp(look.cols, 0.25))], 0.5 + look.key[0] * 0.5, 0.5 + look.key[1] * 0.5, 0.5 - look.key[0] * 0.5, 0.5 - look.key[1] * 0.5)
    out = [f'<path d="{smooth_closed(o)}" fill="{g}" opacity="{base_op}"/>']
    x0, y0, x1, y1 = bbox(o)
    st = []
    for _ in range(int((x1 - x0) * (y1 - y0) / 22 * density)):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if not vol.inside(x, y):
            continue
        n = vol.normal(x, y)
        c = look.color(n, rnd, vf(x, y))
        st.append(dab(x, y, rnd.uniform(*dab_r) * (0.6 + 0.4 * n[2]), c, rnd.uniform(*dab_op), rnd, 0.7))
    cid = D.clip(smooth_closed(o))
    out.append(f'<g {cid}>{"".join(st)}</g>')
    if rim:
        out.append(edges(resample(o, 3), (look.key[0], look.key[1]), seed + 3, None, rim, rim_w, lit_op=0.7, lit_thresh=0.2))
    return "".join(out)


# standing horse legs drawn as outlines (forearm, knee, cannon, fetlock, sloping pastern, hoof) -- local frame as horse()
def stand_fore(dx=0.0, dy=0.0):
    f = [(40, 60), (38, 80), (36, 100), (37, 116), (36, 124), (35, 135), (35, 152), (37, 160), (40, 168), (43, 174), (47, 184)]
    b = [(33, 184), (32, 178), (30, 170), (25, 162), (27, 152), (27, 135), (26, 124), (24, 117), (24, 104), (20, 86), (14, 70), (16, 60)]
    return [(x + dx, y + dy) for x, y in f + b]


def stand_hind(dx=0.0, dy=0.0):
    f = [(-70, 18), (-56, 44), (-52, 66), (-54, 86), (-62, 100), (-72, 112), (-80, 124), (-80, 136), (-80, 156), (-78, 164), (-75, 172),
         (-72, 177), (-68, 184)]
    b = [(-84, 184), (-86, 180), (-90, 172), (-95, 166), (-94, 156), (-95, 138), (-98, 128), (-102, 120), (-100, 112), (-104, 100),
         (-110, 84), (-113, 62), (-110, 40), (-100, 24), (-84, 14)]
    return [(x + dx, y + dy) for x, y in f + b]


STAND_POSE = dict(poll=(62, -82), head_th=56, head_k=1.16,
                  crest=[(0, -3), (8, -18), (18, -40), (30, -60), (44, -78), (56, -90)],
                  front=[(50, -36), (54, -14), (58, 8), (62, 30), (64, 44), (60, 56), (50, 66), (36, 72), (18, 76), (4, 78), (-20, 80),
                         (-40, 76), (-56, 70), (-72, 74), (-90, 70), (-104, 52), (-108, 32)])


def horse_body_outline(P):
    head = horse_head(P["poll"], P["head_th"], P["head_k"])
    return P["top"] + P["crest"] + head + P["front"]


# ---------------------------------------------------------------- small human figures (silhouettes with real proportions)
FIG_STAND = dict(lean=0, head=0, ua_n=8, fa_n=14, ua_f=-6, fa_f=-2, th_n=4, sh_n=-2, th_f=-6, sh_f=-8, foot=1, robe=0.0, hood=False,
                 cloak=0.0, hair=0.0, staff=None)


def figure_parts(x, base, h, pose=None, flip=False):
    """A person seen from the side, about 7.3 heads tall, as limb outlines: returns (far_parts, near_parts, head)
    point lists in canvas coords. pose: lean (torso, deg from vertical, + = forward), head tilt, ua/fa (upper arm,
    forearm: deg from hanging straight down, + = forward), th/sh (thigh, shin), suffix _n near side / _f far side;
    robe: 0..1 a tunic or gown flaring to the knee (0.5) or the ankle (1); hood; cloak (0..1 cape flare)."""
    P = dict(FIG_STAND)
    P.update(pose or {})
    u = h / 7.3
    fl = -1 if flip else 1

    def at(p, ang, L):
        a = math.radians(ang)
        return (p[0] + math.sin(a) * L * fl, p[1] + math.cos(a) * L)
    hip = (x, base - (1.85 + 1.85 + 0.15) * u)
    # torso: hip -> neck base, leaning
    lean = P["lean"]
    neck = at(hip, 180 - lean, 2.65 * u)
    shoulder = at(hip, 180 - lean, 2.35 * u)
    headc = at(neck, 180 - lean * 0.6 - P["head"], 0.75 * u)

    def leg(th, sh, foot):
        knee = at(hip, th, 1.85 * u)
        ank = at(knee, sh, 1.8 * u)
        toe = at(ank, sh + 90 * foot, 0.85 * u) if foot else at(ank, sh + 30, 0.6 * u)
        return limb_outline([(hip[0], hip[1], 0.72 * u), (knee[0], knee[1], 0.46 * u), (ank[0], ank[1], 0.3 * u)], cap=0.3) + \
            [], (ank, toe)

    def foot_poly(ank, toe):
        a = math.atan2(toe[1] - ank[1], toe[0] - ank[0])
        nx, ny = -math.sin(a), math.cos(a)
        w = 0.17 * u
        return [(ank[0] - nx * w * 1.6 - math.cos(a) * w, ank[1] - ny * w * 1.6 - math.sin(a) * w), (toe[0] - nx * w * 0.5, toe[1] - ny * w * 0.5),
                (toe[0] + nx * w * 0.7, toe[1] + ny * w * 0.7), (ank[0] + nx * w * 1.2, ank[1] + ny * w * 1.2)]

    def arm(ua, fa):
        el = at(shoulder, ua, 1.35 * u)
        wr = at(el, fa, 1.2 * u)
        hand = at(wr, fa, 0.55 * u)
        return limb_outline([(shoulder[0], shoulder[1], 0.42 * u), (el[0], el[1], 0.32 * u), (wr[0], wr[1], 0.24 * u), (hand[0], hand[1], 0.2 * u)], cap=0.5), hand
    far, near = [], []
    lf, (ank_f, toe_f) = leg(P["th_f"], P["sh_f"], P["foot"])
    ln, (ank_n, toe_n) = leg(P["th_n"], P["sh_n"], P["foot"])
    far += [lf, foot_poly(ank_f, toe_f)]
    near += [ln, foot_poly(ank_n, toe_n)]
    af, hand_f = arm(P["ua_f"], P["fa_f"])
    an, hand_n = arm(P["ua_n"], P["fa_n"])
    far.append(af)
    # torso: chest deeper than the waist, a slight S
    a = math.radians(lean)
    ux, uy = math.sin(a) * fl, -math.cos(a)      # up the spine
    nx, ny = -uy * fl, ux * fl                   # toward the front
    nx, ny = (math.cos(a) * fl, math.sin(a))

    def tp(t, f):
        # t along spine (0 hip .. 1 neck), f across (+ front, - back), in units
        return (hip[0] + ux * t * 2.65 * u + nx * f * u, hip[1] + uy * t * 2.65 * u + ny * f * u)
    torso = [tp(0, 0.62), tp(0.3, 0.5), tp(0.55, 0.62), tp(0.8, 0.6), tp(0.95, 0.34), tp(1.02, 0.12), tp(1.02, -0.2), tp(0.92, -0.5),
             tp(0.7, -0.52), tp(0.4, -0.42), tp(0.15, -0.6), tp(-0.05, -0.55)]
    near.insert(0, torso)
    nk = [tp(0.9, 0.2), tp(1.25, 0.22), tp(1.25, -0.18), tp(0.9, -0.24)]
    near.insert(1, nk)
    if P["robe"]:
        r = P["robe"]
        low = base - (1.0 - r) * 3.4 * u
        flare = 0.9 + 0.6 * r
        robe = [tp(0.85, 0.6), tp(0.85, -0.55), (hip[0] - nx * flare * u * 1.05 + ux * 0, low), (hip[0] + nx * flare * u * 1.1 + (P["th_n"] / 90) * u * fl, low)]
        near.insert(0, robe)
    if P["cloak"]:
        c = P["cloak"]
        low = base - 1.2 * u
        cl = [tp(1.0, -0.1), tp(0.95, -0.6), (hip[0] - nx * (1.2 + c * 1.6) * u, low + u * 0.3), (hip[0] - nx * 0.2 * u, low)]
        far.insert(0, cl)
    near.append(an)
    head = (headc, 0.46 * u, 0.56 * u, lean * 0.6 + P["head"])
    return far, near, head, dict(hand_n=hand_n, hand_f=hand_f, shoulder=shoulder, hip=hip, headc=headc, u=u)


def figure_silhouette(x, base, h, pose=None, flip=False, extra=()):
    """One clean silhouette outline (union of all parts) of figure_parts()."""
    far, near, head, J = figure_parts(x, base, h, pose, flip)
    polys = far + near + list(extra)
    c = head[0]
    o = union_outline([(c[0], c[1], head[1], head[2], head[3])], polys, step=1.0, smooth_px=0.6 * max(1.0, h / 60))
    return o, J


def y_on(line, x):
    """y of a polyline (sorted by x) at x."""
    for (x0, y0), (x1, y1) in zip(line, line[1:]):
        if x0 <= x <= x1 or x1 <= x <= x0:
            return y0 + (y1 - y0) * ((x - x0) / ((x1 - x0) or 1))
    return line[0][1] if x < line[0][0] else line[-1][1]


def cloud_bank(D, y0, y1, cols, seed, n=60, r=(30, 80), x0=-60, x1=660, op=(0.25, 0.55), squash=0.55, lit_under=None, streaks=40):
    """A soft band of storm / sunset cloud: many translucent irregular masses (no hard outline), coloured from
    cols[0] at the top of the band to cols[-1] at its bottom; lit_under = (colour, opacity) adds the bright
    underside lip; streaks add wind-torn wisps."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1)
        t = (y - y0) / max(1, y1 - y0)
        c = ramp(cols, t + rnd.uniform(-0.12, 0.12))
        rr = rnd.uniform(*r)
        out.append(f'<path d="{blob(x, y, rr, rr * squash, rnd.randint(0, 99999), 0.2, 16)}" fill="{c}" opacity="{rnd.uniform(*op):.2f}"/>')
    if lit_under:
        col, o = lit_under
        for _ in range(n // 3):
            x = rnd.uniform(x0, x1)
            y = y1 - rnd.uniform(0, (y1 - y0) * 0.25)
            out.append(stroke(x, y, rnd.uniform(-4, 4), rnd.uniform(40, 120), rnd.uniform(2, 6), col, rnd.uniform(0.3, 1) * o, rnd.uniform(-4, 4)))
    for _ in range(streaks):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1)
        t = (y - y0) / max(1, y1 - y0)
        out.append(stroke(x, y, rnd.uniform(-6, 2), rnd.uniform(40, 140), rnd.uniform(1.5, 5), ramp(cols, t + 0.15), rnd.uniform(0.15, 0.35), rnd.uniform(-5, 5)))
    return "".join(out)


def _inpoly(pts, x, y):
    inside = False
    n = len(pts)
    j = n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
            inside = not inside
        j = i
    return inside


def trunk(D, spine, widths, look, seed, roots=0, root_spread=1.8, crevices=30, knots=2, edge_col="#0A0806", rim=None, flow_jit=6,
          moss=None):
    """An old tree trunk (Rackham): a wavering tapering spine [(x, y)...] (bottom first) with widths per point,
    flared buttress roots, bark crevices running with the grain, knot holes, optional moss on the shadow side."""
    rnd = random.Random(seed)
    n = len(spine)
    left, right = [], []
    for i, (x, y) in enumerate(spine):
        a, b = spine[max(0, i - 1)], spine[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = widths[i] / 2 * rnd.uniform(0.94, 1.06)
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    base = spine[0]
    w0 = widths[0]
    out_l = []
    if roots:
        rl = [(base[0] - w0 * root_spread * 0.5, base[1] + 4), (base[0] - w0 * 0.75, base[1] - w0 * 0.2)]
        rr = [(base[0] + w0 * 0.75, base[1] - w0 * 0.2), (base[0] + w0 * root_spread * 0.5, base[1] + 4)]
        outline = rl + left[1:] + right[::-1][:-1] + rr
    else:
        outline = left + right[::-1]
    ang_at = []
    for i in range(n - 1):
        ang_at.append(math.degrees(math.atan2(spine[i + 1][1] - spine[i][1], spine[i + 1][0] - spine[i][0])))
    ang_at.append(ang_at[-1])

    def flow(x, y, nrm):
        i = min(range(n), key=lambda k: (spine[k][0] - x) ** 2 + (spine[k][1] - y) ** 2)
        return ang_at[i]
    out = [paint(D, outline, look, seed, round_r=max(widths) * 0.45, flow=flow, flow_jit=flow_jit, edge_col=edge_col, edge_w=1.8, edge_op=0.7,
                 rim_col=rim, rim_w=1.4, rim_op=0.5, passes=((50, (16, 34), (3, 6), (0.3, 0.55)), (200, (8, 20), (1.2, 2.6), (0.35, 0.7))))]
    cid = D.clip(smooth_closed(outline))
    cr = []
    dkc = ramp(look.cols, 0.0)
    ltc = ramp(look.cols, 0.8)
    for _ in range(crevices):
        t0 = rnd.uniform(0, 0.85)
        Lc = rnd.uniform(0.08, 0.3)
        u = rnd.uniform(-0.42, 0.42)
        line = []
        for k in range(6):
            t = min(0.999, t0 + Lc * k / 5)
            fi = t * (n - 1)
            i0 = min(n - 2, int(fi))
            fr = fi - i0
            cx = spine[i0][0] + (spine[i0 + 1][0] - spine[i0][0]) * fr
            cy = spine[i0][1] + (spine[i0 + 1][1] - spine[i0][1]) * fr
            w = widths[i0] + (widths[i0 + 1] - widths[i0]) * fr
            line.append((cx + u * w + math.sin(k + u * 9) * 1.4, cy))
        ww = rnd.uniform(1.0, 3.0) * (1 - abs(u))
        cr.append(taper(line, ww, 0.4, dkc, rnd.uniform(0.35, 0.7)))
        cr.append(taper([(px + 1.4, py) for px, py in line], ww * 0.5, 0.3, ltc, rnd.uniform(0.1, 0.25)))
    for _ in range(knots):
        i = rnd.randint(int(n * 0.25), int(n * 0.75))
        cx, cy = spine[i]
        w = widths[i]
        kx = cx + rnd.uniform(-0.2, 0.2) * w
        r = w * rnd.uniform(0.07, 0.12)
        cr.append(f'<path d="{blob(kx, cy, r * 1.5, r * 2.2, rnd.randint(0, 999), 0.2)}" fill="{ramp(look.cols, 0.55)}" opacity="0.6"/>')
        cr.append(f'<path d="{blob(kx, cy, r * 0.8, r * 1.3, rnd.randint(0, 999), 0.2)}" fill="{dkc}" opacity="0.85"/>')
    if moss:
        for _ in range(int(n * 12)):
            i = rnd.randint(0, n - 1)
            cx, cy = spine[i]
            w = widths[i]
            side = -1 if look.key[0] > 0 else 1
            x = cx + side * w * rnd.uniform(0.15, 0.5)
            cr.append(dab(x, cy + rnd.uniform(-6, 6), rnd.uniform(2, 5), rnd.choice(moss), rnd.uniform(0.4, 0.8), rnd))
    out.append(f'<g {cid}>{"".join(cr)}</g>')
    return "".join(out)
