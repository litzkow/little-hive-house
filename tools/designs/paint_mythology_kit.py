"""Painting kit for the Mythology gallery plates (oil / gouache look in plain SVG, rendered by Chromium).

The idea is the one a digital painter uses: hand-drawn contours for every silhouette, then soft modelling painted
INSIDE each silhouette (blurred glazes clipped to the shape: core shadow, half-tone, light plane, reflected light),
a rim of light on the edge that faces the source, lost-and-found edges (soft blur away from the focal point), real
atmosphere (blurred haze layers, glows blended with `screen`), and a brush finish over the whole art layer
(fractal-noise edge displacement, bristle streaks and pigment grain) while the lettering stays crisp on top.
Texture comes from filters and a few hundred strokes, not from tens of thousands of nodes, so files stay light.

    from paint_mythology_kit import Plate, sp, ...
    P = Plate("myg-owl")
    art = [...]; text = [...]
    body = P.render(art, text, seed=5, edge=2.6, bristle=0.5, grain=0.2)
"""
import math
import random

from fairy_tales_painted import Doc2


def f1(v):
    return f"{v:.1f}"


# ---------------------------------------------------------------- geometry
def sp(pts, closed=True, t=1 / 6):
    """Smooth contour through points (Catmull-Rom -> cubic Bezier). A point given as (x, y, 1) is a sharp corner
    (ear tip, hoof, beak, fingertip); (x, y, 0.5) is a half-sharp turn."""
    P = [(p[0], p[1]) for p in pts]
    C = [(p[2] if len(p) > 2 else 0) for p in pts]
    n = len(P)
    if n < 2:
        return ""

    def tan(i):
        if closed:
            a, b = P[(i - 1) % n], P[(i + 1) % n]
        else:
            a, b = P[max(i - 1, 0)], P[min(i + 1, n - 1)]
        k = t * (1 - C[i])
        return (b[0] - a[0]) * k, (b[1] - a[1]) * k

    d = [f"M {f1(P[0][0])} {f1(P[0][1])}"]
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        j = (i + 1) % n
        t1, t2 = tan(i), tan(j)
        d.append(f"C {f1(P[i][0] + t1[0])} {f1(P[i][1] + t1[1])} {f1(P[j][0] - t2[0])} {f1(P[j][1] - t2[1])} {f1(P[j][0])} {f1(P[j][1])}")
    return " ".join(d) + (" Z" if closed else "")


def lp(pts, closed=True):
    return "M " + " L ".join(f"{f1(x)} {f1(y)}" for x, y, *_ in pts) + (" Z" if closed else "")


def place(pts, ox, oy, s=1.0, flip=False, ang=0.0, sy=None):
    """Local -> page: scale (s, optional separate sy), mirror, rotate (deg), translate. Keeps corner flags."""
    a = math.radians(ang)
    c, si = math.cos(a), math.sin(a)
    sy = s if sy is None else sy
    out = []
    for p in pts:
        x, y = p[0], p[1]
        x = -x if flip else x
        x, y = x * s, y * sy
        q = (ox + x * c - y * si, oy + x * si + y * c)
        out.append(q + tuple(p[2:]))
    return out


def bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp2(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def unit(x, y):
    d = math.hypot(x, y) or 1.0
    return x / d, y / d


def ellipse(cx, cy, rx, ry, n=24, rot=0.0, a0=0, a1=360):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    out = []
    full = (a1 - a0) % 360 == 0
    m = n if full else n + 1
    for i in range(m):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def wobble(pts, seed, amt=1.5):
    rnd = random.Random(seed)
    return [(p[0] + rnd.uniform(-amt, amt), p[1] + rnd.uniform(-amt, amt)) + tuple(p[2:]) for p in pts]


def ribbon(axis, ws, cap=True):
    """Closed outline of a tapered band along an axis polyline (widths per point): limbs, tails, serpents, stalks."""
    n = len(axis)
    L, R = [], []
    for i, (x, y) in enumerate(axis):
        a, b = axis[max(i - 1, 0)], axis[min(i + 1, n - 1)]
        dx, dy = unit(b[0] - a[0], b[1] - a[1])
        w = ws[i] / 2
        L.append((x - dy * w, y + dx * w))
        R.append((x + dy * w, y - dx * w))
    return L + R[::-1]


def resample(pts, step):
    out = [pts[0]]
    acc = 0.0
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L == 0:
            continue
        t = step - acc
        while t <= L:
            out.append(lerp2(a, b, t / L))
            t += step
        acc = L - (t - step)
    if out[-1] != pts[-1]:
        out.append(pts[-1])
    return out


def bez(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out


def catmull(pts, n=8):
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(tuple(pts[-1][:2]))
    return out


# ---------------------------------------------------------------- colour
def hx(c):
    return [int(c[i:i + 2], 16) for i in (1, 3, 5)]


def mix(c1, c2, t):
    a, b = hx(c1), hx(c2)
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


# ---------------------------------------------------------------- the plate (defs, filters, finish)
_FINISH = '''<filter id="{fid}" x="0" y="0" width="600" height="600" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency="{bf}" numOctaves="3" seed="{seed}" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="{edge}" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feTurbulence type="fractalNoise" baseFrequency="{bfx} {bfy}" numOctaves="3" seed="{seed2}" result="b"/>
<feColorMatrix in="b" type="matrix" values="0 0 0 0 0.5 0 0 0 0 0.5 0 0 0 0 0.5 0 0 0 {bristle} 0" result="bs"/>
<feComposite in="bs" in2="d" operator="in" result="bs2"/>
<feBlend in="d" in2="bs2" mode="soft-light" result="t"/>
<feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="{seed3}" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0.25 0 0 0 0 0.2 0 0 0 0 0.15 0 0 0 {grain} 0" result="gg"/>
<feComposite in="gg" in2="t" operator="in" result="g3"/>
<feBlend in="t" in2="g3" mode="multiply"/>
</filter>'''


class Plate(Doc2):
    """Doc2 (lin / rad / clip / pattern / nid) plus cached filters and the finishing pass."""

    def __init__(self, u):
        super().__init__(u)
        self.fcache = {}

    # filters ---------------------------------------------------------
    def _filter(self, key, inner, pad=0.25):
        if key in self.fcache:
            return self.fcache[key]
        i = self.nid()
        self.defs.append(f'<filter id="{i}" x="-{pad}" y="-{pad}" width="{1 + 2 * pad}" height="{1 + 2 * pad}" '
                         f'color-interpolation-filters="sRGB">{inner}</filter>')
        self.fcache[key] = f'filter="url(#{i})"'
        return self.fcache[key]

    def blur(self, sd, pad=0.3):
        """Soft edge (lost edges, haze, glazes)."""
        if isinstance(sd, (tuple, list)):
            sd_s = f"{sd[0]} {sd[1]}"
        else:
            sd_s = f"{sd}"
        return self._filter(("blur", sd_s, pad), f'<feGaussianBlur stdDeviation="{sd_s}"/>', pad)

    def rough(self, scale=4.0, freq=0.035, seed=3, octaves=3):
        """Torn, brushy edge: displaces a shape's outline with fractal noise (dry-brush edge, foam, foliage)."""
        return self._filter(("rough", scale, freq, seed, octaves),
                            f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="{octaves}" seed="{seed}" result="n"/>'
                            f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{scale}" xChannelSelector="R" yChannelSelector="G"/>', 0.1)

    def rough_blur(self, scale=4.0, freq=0.035, sd=1.0, seed=3):
        return self._filter(("rb", scale, freq, sd, seed),
                            f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="3" seed="{seed}" result="n"/>'
                            f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{scale}" xChannelSelector="R" yChannelSelector="G" result="d"/>'
                            f'<feGaussianBlur in="d" stdDeviation="{sd}"/>', 0.2)

    def mottle(self, freq=0.02, op=0.25, seed=4, col=(0, 0, 0)):
        """A filter that paints the shape's own colour with uneven pigment density (canvas / plaster / stone)."""
        r, g, b = col
        return self._filter(("mottle", freq, op, seed, col),
                            f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="4" seed="{seed}" result="n"/>'
                            f'<feColorMatrix in="n" type="matrix" values="0 0 0 0 {r} 0 0 0 0 {g} 0 0 0 0 {b} 0 0 0 {op * 2.2} {-op * 0.9}" result="m"/>'
                            f'<feComposite in="m" in2="SourceGraphic" operator="in" result="mi"/>'
                            f'<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="mi"/></feMerge>', 0.02)

    # finishing -------------------------------------------------------
    def render(self, art, text=(), seed=3, edge=2.6, freq=0.05, bristle=0.5, grain=0.2, streak=(0.035, 0.42)):
        fid = self.nid()
        self.defs.append(_FINISH.format(fid=fid, seed=seed, seed2=seed + 17, seed3=seed + 31, edge=edge, bf=freq,
                                        bfx=streak[0], bfy=streak[1], bristle=bristle, grain=grain))
        return (f'<defs>{"".join(self.defs)}</defs>'
                f'<g filter="url(#{fid})">{"".join(art)}</g>{"".join(text)}')


# ---------------------------------------------------------------- painting primitives
def path(d, fill, op=None, extra=""):
    o = f' opacity="{op:.2f}"' if op is not None and op < 1 else ""
    return f'<path d="{d}" fill="{fill}"{o}{extra}/>'


def g(inner, *attrs):
    a = " ".join(x for x in attrs if x)
    return f"<g {a}>{''.join(inner) if isinstance(inner, (list, tuple)) else inner}</g>"


def screen(inner):
    return f'<g style="mix-blend-mode:screen">{inner}</g>'


def multiply(inner):
    return f'<g style="mix-blend-mode:multiply">{inner}</g>'


def glow(P, x, y, r, col, op=0.7, ry=None, mid=0.42):
    gr = P.rad([(0, col, op), (mid, col, op * 0.45), (1, col, 0)])
    if ry:
        return f'<ellipse cx="{f1(x)}" cy="{f1(y)}" rx="{f1(r)}" ry="{f1(ry)}" fill="{gr}"/>'
    return f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{f1(r)}" fill="{gr}"/>'


def stroke_line(pts, col, w, op=1.0, closed=False, cap="round", smooth=True, extra=""):
    d = sp(pts, closed) if smooth else lp(pts, closed)
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w:.2f}" stroke-linecap="{cap}" stroke-linejoin="round"'
            f' opacity="{op:.2f}"{extra}/>')


def taper(pts, w0, w1, col, op=1.0, mid=None):
    """A brush mark that swells / tapers along a polyline."""
    n = len(pts)
    if mid is None:
        ws = [w0 + (w1 - w0) * i / max(1, n - 1) for i in range(n)]
    else:
        ws = [(w0 + (mid - w0) * (i / ((n - 1) / 2))) if i <= (n - 1) / 2 else (mid + (w1 - mid) * ((i - (n - 1) / 2) / ((n - 1) / 2))) for i in range(n)]
    return path(sp(ribbon(pts, ws)), col, op)


def bstroke(x, y, ang, L, w, col, op, bend=0.0):
    a = math.radians(ang)
    dx, dy = L * math.cos(a), L * math.sin(a)
    nx, ny = -math.sin(a), math.cos(a)
    mx, my = x + dx / 2 + nx * bend * L, y + dy / 2 + ny * bend * L
    return (f'<path d="M {f1(x)} {f1(y)} Q {f1(mx + nx * w)} {f1(my + ny * w)} {f1(x + dx)} {f1(y + dy)} '
            f'Q {f1(mx - nx * w)} {f1(my - ny * w)} {f1(x)} {f1(y)} Z" fill="{col}" opacity="{op:.2f}"/>')


def brush(seed, box, n, flow, cols, length=(6, 16), width=(1, 3), op=(0.2, 0.5), jit=12, bend=0.2, inside=None):
    """Brush strokes in a box; flow = angle in degrees or f(x, y) -> degrees; inside = f(x, y) -> bool filter."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    tries = 0
    while len(out) < n and tries < n * 6:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if inside and not inside(x, y):
            continue
        a = (flow(x, y) if callable(flow) else flow) + rnd.uniform(-jit, jit)
        L = rnd.uniform(*length)
        ar = math.radians(a)
        out.append(bstroke(x - L / 2 * math.cos(ar), y - L / 2 * math.sin(ar), a, L, rnd.uniform(*width) / 2,
                           rnd.choice(cols), rnd.uniform(*op), rnd.uniform(-bend, bend)))
    return "".join(out)


def along(seed, axis, ws, n, cols, length=(5, 12), width=(0.8, 2), op=(0.2, 0.5), spread=0.9, jit=8, back=False, ang_off=0):
    """Strokes laid along a chain (fur down a leg, scales down a serpent, folds down a robe)."""
    rnd = random.Random(seed)
    P = resample(axis, 2.5)
    Wi = []
    # interpolate widths onto resampled points by arc length
    cum = [0]
    for a, b in zip(axis, axis[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    tot = cum[-1] or 1
    cumP = [0]
    for a, b in zip(P, P[1:]):
        cumP.append(cumP[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    for c in cumP:
        t = c / tot * (len(ws) - 1)
        i = min(int(t), len(ws) - 2)
        Wi.append(lerp(ws[i], ws[i + 1], t - i))
    out = []
    for _ in range(int(n)):
        i = rnd.randrange(len(P))
        a_, b_ = P[max(i - 1, 0)], P[min(i + 1, len(P) - 1)]
        tx_, ty_ = unit(b_[0] - a_[0], b_[1] - a_[1])
        u = rnd.uniform(-spread / 2, spread / 2)
        x, y = P[i][0] - ty_ * u * Wi[i], P[i][1] + tx_ * u * Wi[i]
        ang = math.degrees(math.atan2(ty_, tx_)) + (180 if back else 0) + ang_off + rnd.uniform(-jit, jit)
        out.append(bstroke(x, y, ang, rnd.uniform(*length), rnd.uniform(*width) / 2, rnd.choice(cols), rnd.uniform(*op), rnd.uniform(-0.2, 0.2)))
    return "".join(out)


def clip_to(P, d, inner):
    return f'<g {P.clip(f"<path d=\"{d}\"/>")}>{"".join(inner) if isinstance(inner, (list, tuple)) else inner}</g>'


def soft(P, d, col, op, sd):
    """A blurred glaze (soft-brush shading / light) — clip it inside a form with clip_to."""
    return f'<path d="{d}" fill="{col}" opacity="{op:.2f}" {P.blur(sd)}/>'


def soft_line(P, pts, col, w, op, sd, closed=False):
    return f'<path d="{sp(pts, closed)}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" opacity="{op:.2f}" {P.blur(sd)}/>'


def dir_grad(P, stops, L):
    """Gradient across an object's box from the side facing the light (L = vector toward the light)."""
    lx, ly = unit(*L)
    return P.lin(stops, round(0.5 + 0.5 * lx, 3), round(0.5 + 0.5 * ly, 3), round(0.5 - 0.5 * lx, 3), round(0.5 - 0.5 * ly, 3))


def rim(P, ds, L, dist, col, op=0.9, sd=0.6, src=None):
    """Rim light along the edge of a union of shapes that faces the light L (toward-light vector): the band of the
    union that would leave it if shifted toward the light by `dist`. src=(x, y, r) fades it with distance."""
    lx, ly = unit(*L)
    mid = P.nid()
    sh = "".join(f'<path d="{d}"/>' for d in (ds if isinstance(ds, (list, tuple)) else [ds]))
    P.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="-50" y="-50" width="700" height="700">'
                  f'<g fill="#FFFFFF">{sh}</g><g fill="#000000" transform="translate({f1(-lx * dist)} {f1(-ly * dist)})">{sh}</g></mask>')
    fill = col
    if src:
        sx, sy, sr = src
        fill = P.rad([(0, col, 1), (0.5, col, 0.55), (1, col, 0)], cx=sx, cy=sy, r=sr, units="userSpaceOnUse")
    b = P.blur(sd) if sd else ""
    return f'<g mask="url(#{mid})"><g {b}><rect x="-50" y="-50" width="700" height="700" fill="{fill}" opacity="{op}"/></g></g>'


def form(P, d, pal, L=(-0.6, -0.8), box=None, core=0.55, lit=0.45, refl=None, refl_op=0.35, sd=None, edge=None, edge_op=0.5,
         rim_col=None, rim_d=2.0, rim_op=0.85, rim_src=None, extra=(), grad=True):
    """Paint one closed form with a full value structure, all inside its silhouette:
    base colour + directional gradient, a soft core shadow on the far side, a soft light plane on the near side,
    reflected light along the far edge, extra painting (strokes, markings) and an optional rim light / dark edge.
    d: path data; pal = (light, base, dark); box = (x0, y0, x1, y1) of the form (for sizing the glazes)."""
    light, base, dark = pal
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    m = min(W, H)
    lx, ly = unit(*L)
    sd = sd if sd is not None else max(1.5, m * 0.12)
    out = [path(d, base)]
    if grad:
        out.append(path(d, dir_grad(P, [(0, light, 0.55), (0.45, base, 0), (0.8, dark, 0.35), (1, dark, 0.6)], L)))
    inner = []
    if core:
        # a shadow shape: the form shifted away from the light, blurred (core shadow + cast-in-self)
        inner.append(f'<path d="{d}" fill="{dark}" stroke="{dark}" stroke-width="{f1(sd * 3)}" opacity="{core:.2f}" '
                     f'transform="translate({f1(-lx * m * 0.22)} {f1(-ly * m * 0.22)})" {P.blur(sd)}/>')
        # punch the lit part back out: a lit copy shifted toward the light
    if lit:
        inner.append(f'<g style="mix-blend-mode:screen"><path d="{d}" fill="{light}" opacity="{lit:.2f}" '
                     f'stroke="{light}" stroke-width="{f1(sd * 2)}" transform="translate({f1(lx * m * 0.32)} {f1(ly * m * 0.32)})" {P.blur(sd * 1.1)}/></g>')
    if refl:
        inner.append(rim(P, d, (-lx, -ly), max(2, m * 0.05), refl, refl_op, sd=max(1, m * 0.03)))
    inner.extend(extra)
    out.append(clip_to(P, d, inner))
    if edge:
        out.append(rim(P, d, (-lx, -ly), 1.6, edge, edge_op, sd=0.5))
    if rim_col:
        out.append(rim(P, d, (lx, ly), rim_d, rim_col, rim_op, sd=0.5, src=rim_src))
    return "".join(out)


def cast_shadow(P, cx, cy, rx, ry, col="#000000", op=0.45, sd=None):
    sd = sd or max(2, ry * 0.5)
    return f'<ellipse cx="{f1(cx)}" cy="{f1(cy)}" rx="{f1(rx)}" ry="{f1(ry)}" fill="{col}" opacity="{op:.2f}" {P.blur(sd)}/>'


# ---------------------------------------------------------------- skies, atmosphere, water
def sky_grad(P, stops, y0=0, y1=600, x0=0, x1=600):
    gr = P.lin(stops, 0, y0, 0, y1, "userSpaceOnUse")
    return f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{gr}"/>'


def sky_wash(P, seed, cols, n=14, box=(-40, -40, 640, 400), r=(60, 160), op=(0.08, 0.2), sd=30, flat=0.45):
    """Large soft colour blooms in the sky (the painter's broken colour), blurred together."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        rr = rnd.uniform(*r)
        out.append(f'<ellipse cx="{f1(rnd.uniform(x0, x1))}" cy="{f1(rnd.uniform(y0, y1))}" rx="{f1(rr)}" ry="{f1(rr * flat)}" '
                   f'fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*op):.2f}"/>')
    return f'<g {P.blur(sd, 0.6)}>{"".join(out)}</g>'


def sky_strokes(P, seed, cols, n=60, box=(-20, -20, 620, 420), length=(60, 180), width=(4, 12), op=(0.05, 0.16), ang=-2, sd=1.2):
    return f'<g {P.blur(sd)}>{brush(seed, box, n, ang, cols, length, width, op, jit=4, bend=0.05)}</g>'


def stars(seed, box, n, cols=("#FFFFFF", "#FFF2C8", "#DCE6FF"), r=(0.5, 1.6), op=(0.4, 1.0), avoid=None):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if avoid and avoid(x, y):
            continue
        out.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{rnd.uniform(*r):.2f}" fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


def twinkle(x, y, r, col="#FFFFFF", op=0.9):
    d = (f"M {f1(x)} {f1(y - r)} Q {f1(x + r * 0.12)} {f1(y - r * 0.12)} {f1(x + r)} {f1(y)} Q {f1(x + r * 0.12)} {f1(y + r * 0.12)} "
         f"{f1(x)} {f1(y + r)} Q {f1(x - r * 0.12)} {f1(y + r * 0.12)} {f1(x - r)} {f1(y)} Q {f1(x - r * 0.12)} {f1(y - r * 0.12)} {f1(x)} {f1(y - r)} Z")
    return f'<path d="{d}" fill="{col}" opacity="{op}"/>'


def cloud(P, seed, cx, cy, w, h, pal, L=(0, -1), n=None, op=1.0, sd=(2.5, 1.2), flat=0.55, edge_sd=0.8, wisps=0.0, rough_=True):
    """A cumulus-type cloud bank: a dark under-body, lit puffs toward the light, soft halo; painted with blur so
    edges are lost on the shadow side and found on the lit side."""
    rnd = random.Random(seed)
    light, base, dark = pal
    lx, ly = unit(*L)
    n = n or max(6, int(w / 14))
    puffs = []
    for i in range(n):
        t = i / max(1, n - 1)
        px = cx - w / 2 + w * t + rnd.uniform(-w * 0.04, w * 0.04)
        hump = math.sin(math.pi * t) ** 0.7
        r = rnd.uniform(0.35, 0.6) * h * (0.55 + 0.6 * hump)
        py = cy - hump * h * 0.35 + rnd.uniform(-h * 0.08, h * 0.08)
        puffs.append((px, py, r))
    body = "".join(f'<ellipse cx="{f1(x)}" cy="{f1(y)}" rx="{f1(r)}" ry="{f1(r * (0.8 + flat * 0.2))}"/>' for x, y, r in puffs)
    base_d = f'<rect x="{f1(cx - w / 2)}" y="{f1(cy - h * 0.1)}" width="{f1(w)}" height="{f1(h * 0.28)}" rx="{f1(h * 0.14)}"/>'
    out = [f'<g fill="{dark}" opacity="{op}" {P.blur(sd[0])}>{body}{base_d}</g>']
    lit = "".join(f'<ellipse cx="{f1(x + lx * r * 0.18)}" cy="{f1(y + ly * r * 0.18)}" rx="{f1(r * 0.86)}" ry="{f1(r * 0.86 * (0.8 + flat * 0.2))}"/>' for x, y, r in puffs)
    out.append(f'<g fill="{base}" opacity="{op}" {P.blur(sd[1])}>{lit}</g>')
    hi = "".join(f'<ellipse cx="{f1(x + lx * r * 0.36)}" cy="{f1(y + ly * r * 0.36)}" rx="{f1(r * 0.6)}" ry="{f1(r * 0.55)}"/>' for x, y, r in puffs)
    out.append(f'<g fill="{light}" opacity="{op * 0.9:.2f}" {P.blur(edge_sd)}>{hi}</g>')
    return "".join(out)


def haze(P, y0, y1, col, op0=0.0, op1=0.6, x0=-20, x1=620):
    gr = P.lin([(0, col, op0), (1, col, op1)], 0, y0, 0, y1, "userSpaceOnUse")
    return f'<rect x="{x0}" y="{f1(y0)}" width="{x1 - x0}" height="{f1(y1 - y0)}" fill="{gr}"/>'


def ridge(seed, x0, x1, base, top, amp, n=14, rough_=0.35, peaks=None, bottom=620):
    """Mountain / hill outline: random midpoint ridge + optional explicit peaks [(x, y), ...]; returns points."""
    rnd = random.Random(seed)
    pts = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        y = top + amp * (0.5 + 0.5 * math.sin(i * 1.7 + seed)) * rnd.uniform(1 - rough_, 1 + rough_)
        if peaks:
            for px, py, pw in peaks:
                k = max(0.0, 1 - abs(x - px) / pw)
                y = min(y, lerp(base, py, k ** 0.9) if k > 0 else y)
        pts.append((x, y))
    return [(x0, bottom)] + pts + [(x1, bottom)]


def water(P, seed, y0, y1, stops, cols, n=140, sun_x=None, glint="#FFF2C8", glint_w=40, length=(10, 40), op=(0.15, 0.45), sd=0.5):
    """Painted water: graded base and horizontal ripple strokes that shorten with distance; a glitter path under
    the light source."""
    rnd = random.Random(seed)
    out = [sky_grad(P, stops, y0, y1)]
    st = []
    for _ in range(n):
        t = rnd.random() ** 1.4
        y = y0 + (y1 - y0) * t
        k = 0.3 + 0.7 * t
        L = rnd.uniform(*length) * k
        x = rnd.uniform(-20, 620)
        w = (0.6 + 2.2 * t) * rnd.uniform(0.6, 1.2)
        st.append(bstroke(x, y, rnd.uniform(-1.5, 1.5), L, w / 2, rnd.choice(cols), rnd.uniform(*op), 0.02))
    out.append(f'<g {P.blur(sd)}>{"".join(st)}</g>')
    if sun_x is not None:
        gl = []
        for _ in range(int(n * 0.5)):
            t = rnd.random() ** 1.2
            y = y0 + (y1 - y0) * t
            spread = glint_w * (0.25 + 1.2 * t)
            x = sun_x + rnd.gauss(0, spread * 0.45)
            L = rnd.uniform(4, 18) * (0.4 + t)
            gl.append(bstroke(x - L / 2, y, 0, L, (0.5 + 1.4 * t) / 2, glint, rnd.uniform(0.35, 0.95), 0))
        out.append(f'<g style="mix-blend-mode:screen">{"".join(gl)}</g>')
    return "".join(out)


def rays(P, ox, oy, angs, length, width, col, op=0.25, sd=6):
    """Light shafts from a point (sun, doorway): list of angles (deg), each a widening wedge, blurred, screened."""
    out = []
    for i, a in enumerate(angs):
        w = width[i % len(width)] if isinstance(width, (list, tuple)) else width
        ar = math.radians(a)
        dx, dy = math.cos(ar), math.sin(ar)
        nx, ny = -dy, dx
        ex, ey = ox + dx * length, oy + dy * length
        out.append(f'<path d="M {f1(ox + nx * w * 0.08)} {f1(oy + ny * w * 0.08)} L {f1(ex + nx * w / 2)} {f1(ey + ny * w / 2)} '
                   f'L {f1(ex - nx * w / 2)} {f1(ey - ny * w / 2)} L {f1(ox - nx * w * 0.08)} {f1(oy - ny * w * 0.08)} Z"/>')
    gr = P.rad([(0, col, op), (0.6, col, op * 0.4), (1, col, 0)], cx=ox, cy=oy, r=length, units="userSpaceOnUse")
    return f'<g style="mix-blend-mode:screen"><g fill="{gr}" {P.blur(sd, 0.5)}>{"".join(out)}</g></g>'


def foliage(P, seed, cx, cy, rx, ry, pal, L=(-0.6, -0.8), n=30, leaf=(4, 9), dabs=120, sd=2.0, edge_cols=None, rnd_shape=0.25):
    """A painted mass of leaves: a dark blurred core mass, mid-tone clumps, lit clumps toward the light, and crisp
    leaf dabs breaking the silhouette (found edges)."""
    rnd = random.Random(seed)
    light, base, dark = pal
    lx, ly = unit(*L)
    out = []
    clumps = []
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.random() ** 0.6
        x, y = cx + math.cos(a) * rx * rr * 0.85, cy + math.sin(a) * ry * rr * 0.85
        r = rnd.uniform(0.22, 0.42) * min(rx, ry) * (1.1 - 0.4 * rr)
        clumps.append((x, y, r))
    out.append(f'<g fill="{dark}" {P.blur(sd)}>' + "".join(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{f1(r)}"/>' for x, y, r in clumps) + "</g>")
    mid = []
    for x, y, r in clumps:
        mid.append(f'<circle cx="{f1(x + lx * r * 0.2)}" cy="{f1(y + ly * r * 0.2)}" r="{f1(r * 0.75)}"/>')
    out.append(f'<g fill="{base}" {P.blur(sd * 0.8)}>{"".join(mid)}</g>')
    lit = []
    for x, y, r in clumps:
        facing = ((x - cx) / rx * lx + (y - cy) / ry * ly)
        if facing > -0.1:
            lit.append(f'<circle cx="{f1(x + lx * r * 0.42)}" cy="{f1(y + ly * r * 0.42)}" r="{f1(r * 0.42)}" opacity="{min(1, 0.35 + facing * 0.6):.2f}"/>')
    out.append(f'<g fill="{light}" {P.blur(sd * 0.6)}>{"".join(lit)}</g>')
    # crisp leaf dabs on the silhouette and in the light
    dd = []
    cols = edge_cols or [light, base, dark, mix(base, light, 0.5)]
    for _ in range(dabs):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0.55, 1.02)
        x, y = cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr
        facing = math.cos(a) * lx + math.sin(a) * ly
        col = cols[0] if facing > 0.35 else (cols[2] if facing < -0.3 else rnd.choice(cols[1:]))
        L_ = rnd.uniform(*leaf)
        dd.append(bstroke(x, y, rnd.uniform(0, 360), L_, L_ * 0.28, col, rnd.uniform(0.55, 0.95), 0.25))
    out.append("".join(dd))
    return "".join(out)


def grass(seed, x0, x1, y0, y1, cols, n=200, h=(6, 16), lean=(-12, 12), w=(0.8, 1.8), op=(0.4, 0.9)):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        hh = rnd.uniform(*h) * (0.5 + 0.5 * (y - y0) / max(1, y1 - y0))
        a = math.radians(-90 + rnd.uniform(*lean))
        ex, ey = x + math.cos(a) * hh, y + math.sin(a) * hh
        mx, my = x + math.cos(a) * hh * 0.5 + rnd.uniform(-2, 2), y + math.sin(a) * hh * 0.5
        ww = rnd.uniform(*w)
        out.append(f'<path d="M {f1(x - ww)} {f1(y)} Q {f1(mx)} {f1(my)} {f1(ex)} {f1(ey)} Q {f1(mx + ww * 0.3)} {f1(my)} {f1(x + ww)} {f1(y)} Z" '
                   f'fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


def flame(P, x, y, h, seed, lean=0.0, pal=("#FFFBE6", "#FFD25A", "#FF8A1E", "#C8380E"), n=7, w=0.4, sd=1.2):
    """Painted fire: several licking tongues in four temperatures, blurred at the edges, white-hot core."""
    rnd = random.Random(seed)
    out = []
    for k, (col, sc, op) in enumerate(((pal[3], 1.0, 0.85), (pal[2], 0.82, 0.9), (pal[1], 0.6, 0.95), (pal[0], 0.36, 1.0))):
        tongues = []
        for i in range(n if k < 2 else max(2, n // 2)):
            hh = h * sc * rnd.uniform(0.55, 1.0) * (1.0 if i == 0 else rnd.uniform(0.5, 0.9))
            ww = h * w * sc * rnd.uniform(0.35, 0.6)
            ox = x + rnd.uniform(-1, 1) * h * w * 0.45 * sc
            tip = (ox + lean * hh + rnd.uniform(-0.18, 0.18) * hh, y - hh)
            pts = [(ox - ww, y), (ox - ww * 0.9, y - hh * 0.3), (ox - ww * 0.35 + lean * hh * 0.4, y - hh * 0.65), (tip[0], tip[1], 1),
                   (ox + ww * 0.3 + lean * hh * 0.5, y - hh * 0.58), (ox + ww * 0.85, y - hh * 0.28), (ox + ww, y)]
            tongues.append(f'<path d="{sp(pts)}"/>')
        out.append(f'<g fill="{col}" opacity="{op}" {P.blur(sd * (1.6 - k * 0.3))}>{"".join(tongues)}</g>')
    return "".join(out)


def embers(seed, x, y, spread, rise, n, cols=("#FFE8A0", "#FFB040", "#FF7A20"), r=(0.6, 1.8)):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        t = rnd.random()
        ex = x + rnd.gauss(0, spread * (0.3 + t))
        ey = y - rise * t
        out.append(f'<circle cx="{f1(ex)}" cy="{f1(ey)}" r="{rnd.uniform(*r) * (1.2 - t * 0.6):.2f}" fill="{rnd.choice(cols)}" opacity="{0.95 - t * 0.6:.2f}"/>')
    return "".join(out)


def vignette(P, col="#000000", op=0.55, r0=0.55, cx=0.5, cy=0.5):
    gr = P.rad([(0, col, 0), (r0, col, 0), (1, col, op)], cx=cx, cy=cy, r=0.75)
    return f'<rect x="-10" y="-10" width="620" height="620" fill="{gr}"/>'


def text_scrim(P, y0, y1, col="#000000", op=0.55, up=True):
    gr = P.lin([(0, col, 0 if up else op), (1, col, op if up else 0)], 0, y0, 0, y1, "userSpaceOnUse")
    return f'<rect x="-10" y="{f1(y0)}" width="620" height="{f1(y1 - y0)}" fill="{gr}"/>'


def strata(P, seed, y, x0, x1, th, pal, L=(0, -1), n=7, op=1.0, sd=1.6, rough_=(10, 0.025)):
    """Long painted cloud bands (stratus / altostratus / mackerel streaks): irregular elongated blobs, a lit edge on
    the light side, a dark belly, torn edges (noise displacement) and soft blur."""
    rnd = random.Random(seed)
    light, base, dark = pal
    lx, ly = unit(*L)
    bands = []
    for i in range(n):
        cx = rnd.uniform(x0, x1)
        w = rnd.uniform(0.18, 0.45) * (x1 - x0)
        h = th * rnd.uniform(0.5, 1.1)
        cy = y + rnd.uniform(-th * 1.2, th * 1.2)
        pts = []
        m = 14
        for k in range(m):
            a = 2 * math.pi * k / m
            r = 1 + rnd.uniform(-0.25, 0.25)
            pts.append((cx + math.cos(a) * w / 2 * r, cy + math.sin(a) * h / 2 * r * (0.7 if math.sin(a) > 0 else 1.0)))
        bands.append(sp(pts))
    f = P.rough_blur(rough_[0], rough_[1], sd, seed)
    out = [f'<g fill="{dark}" opacity="{op}" {f}>' + "".join(f'<path d="{d}"/>' for d in bands) + "</g>"]
    out.append(f'<g fill="{base}" opacity="{op}" {f}>' + "".join(f'<path d="{d}" transform="translate({lx * th * 0.22:.1f} {ly * th * 0.22:.1f}) "/>' for d in bands) + "</g>")
    out.append(f'<g fill="{light}" opacity="{op * 0.85:.2f}" {P.rough_blur(rough_[0] * 0.8, rough_[1] * 1.6, sd * 0.6, seed + 1)}>'
               + "".join(f'<path d="{d}" transform="translate({lx * th * 0.45:.1f} {ly * th * 0.45:.1f}) "/>' for d in bands[: max(1, n * 2 // 3)]) + "</g>")
    return "".join(out)


def scallops(seed, region, n, flow, cols, size=(4, 8), op=(0.3, 0.7), w=(0.7, 1.4), inside=None):
    """Feather / scale edges: short curved marks laid across the flow (like the rounded tip of each feather)."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = region
    out = []
    tries = 0
    while len(out) < n and tries < n * 8:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if inside and not inside(x, y):
            continue
        a = math.radians((flow(x, y) if callable(flow) else flow) + rnd.uniform(-10, 10))
        r = rnd.uniform(*size)
        nx, ny = -math.sin(a), math.cos(a)
        p0 = (x - nx * r, y - ny * r)
        p2 = (x + nx * r, y + ny * r)
        c = (x + math.cos(a) * r * 1.1, y + math.sin(a) * r * 1.1)
        out.append(f'<path d="M {f1(p0[0])} {f1(p0[1])} Q {f1(c[0])} {f1(c[1])} {f1(p2[0])} {f1(p2[1])}" fill="none" stroke="{rnd.choice(cols)}" '
                   f'stroke-width="{rnd.uniform(*w):.2f}" stroke-linecap="round" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


def inside_poly(pts):
    """Point-in-polygon test function for a closed outline."""
    P_ = [(p[0], p[1]) for p in pts]

    def f(x, y):
        c = False
        n = len(P_)
        j = n - 1
        for i in range(n):
            xi, yi = P_[i]
            xj, yj = P_[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi:
                c = not c
            j = i
        return c
    return f


# ---------------------------------------------------------------- bodies (people and beasts) drawn as organic parts
def interp_list(vals, n):
    out = []
    for i in range(len(vals) - 1):
        for k in range(n):
            out.append(vals[i] + (vals[i + 1] - vals[i]) * k / n)
    out.append(vals[-1])
    return out


def limb(axis, wl, wr, n=6):
    """Organic limb outline along a joint chain with separate half-widths on the left / right of the direction of
    travel (so a calf can bulge behind, a thigh in front). Returns closed outline points."""
    A = catmull(axis, n)
    WL, WR = interp_list(wl, n), interp_list(wr, n)
    m = len(A)
    Lp, Rp = [], []
    for i, (x, y) in enumerate(A):
        a, b = A[max(i - 1, 0)], A[min(i + 1, m - 1)]
        dx, dy = unit(b[0] - a[0], b[1] - a[1])
        Lp.append((x - dy * WL[i], y + dx * WL[i]))
        Rp.append((x + dy * WR[i], y - dx * WR[i]))
    # rounded caps
    return Lp + Rp[::-1]


class Body:
    """A figure (or beast) built of overlapping painted parts that read as one mass: each part gets its own form
    modelling, then the union gets rim lights (several sources allowed) and a dark found-edge on the shadow side."""

    def __init__(self, P, L=(-0.6, -0.8)):
        self.P, self.L = P, L
        self.parts = []

    def add(self, pts, pal, core=0.55, lit=0.35, extra=(), smooth=True, sd=None, L=None, edge=True):
        self.parts.append(dict(pts=pts, pal=pal, core=core, lit=lit, extra=list(extra), smooth=smooth, sd=sd, L=L, edge=edge))
        return len(self.parts) - 1

    def d(self, i):
        p = self.parts[i]
        return sp(p["pts"]) if p["smooth"] else lp(p["pts"])

    def render(self, rims=(), edge_col="#000000", edge_op=0.5, edge_d=1.6, over=()):
        P = self.P
        out = []
        ds = []
        for i, p in enumerate(self.parts):
            d = self.d(i)
            ds.append(d)
            out.append(form(P, d, p["pal"], p["L"] or self.L, bbox(p["pts"]), core=p["core"], lit=p["lit"], extra=p["extra"], sd=p["sd"],
                            edge=edge_col if p["edge"] else None, edge_op=edge_op * 0.6))
        if over:
            cl = P.clip("".join(f'<path d="{d}"/>' for d in ds))
            out.append(f'<g {cl}>{"".join(over)}</g>')
        for r in rims:
            # r = dict(L=(x, y), col=..., d=2, op=0.9, src=(x, y, r) or None, parts=None)
            sel = [ds[i] for i in r["parts"]] if r.get("parts") else ds
            out.append(rim(P, sel, r["L"], r.get("d", 2.0), r["col"], r.get("op", 0.9), sd=r.get("sd", 0.6), src=r.get("src")))
        return "".join(out)


def limb_shade(axis, wl, wr, L, t=0.15, n=6):
    """The shadow-side band of a limb for cylinder modelling: from a terminator a little toward the light from the
    axis, out to the far edge. L = toward-light vector."""
    A = catmull(axis, n)
    WL, WR = interp_list(wl, n), interp_list(wr, n)
    lx, ly = unit(*L)
    m = len(A)
    T_, E_ = [], []
    for i, (x, y) in enumerate(A):
        a, b = A[max(i - 1, 0)], A[min(i + 1, m - 1)]
        dx, dy = unit(b[0] - a[0], b[1] - a[1])
        nlx, nly = -dy, dx                      # left normal
        dot = nlx * lx + nly * ly
        if dot >= 0:                            # left side is lit: shadow toward the right
            T_.append((x + nlx * WL[i] * t * 2 * dot, y + nly * WL[i] * t * 2 * dot))
            E_.append((x - nlx * WR[i] * 1.05, y - nly * WR[i] * 1.05))
        else:
            T_.append((x - nlx * WR[i] * t * 2 * -dot, y - nly * WR[i] * t * 2 * -dot))
            E_.append((x + nlx * WL[i] * 1.05, y + nly * WL[i] * 1.05))
    return T_ + E_[::-1]


def falloff(P, cx, cy, r, col="#000000", op=0.85, inner=0.25):
    """Light falling off with distance from a source: transparent near (cx, cy), darkening outward (clip to a body)."""
    gr = P.rad([(0, col, 0), (inner, col, 0), (1, col, op)], cx=cx, cy=cy, r=r, units="userSpaceOnUse")
    return f'<rect x="-50" y="-50" width="700" height="700" fill="{gr}"/>'


def furry(P, pts, pal, L, seed, flow=90, n=None, flen=(4, 10), fw=(0.6, 1.4), fop=(0.25, 0.6), rough=(3.0, 0.12), core=0.5, lit=0.4,
          rim_col=None, rim_d=2.0, rim_src=None, edge="#000000", edge_op=0.45, extra=(), pre=(), cols=None, sd=None):
    """A furred / feathered form: modelled mass, fur strokes following `flow` (deg or f(x, y)), fluffy torn edge."""
    d = sp(pts)
    box = bbox(pts)
    W, H = box[2] - box[0], box[3] - box[1]
    n = n if n is not None else int(min(500, W * H / 40))
    light, base, dark = pal
    cols = cols or [light, base, dark, mix(base, light, 0.5), mix(base, dark, 0.5)]
    fur = brush(seed, box, n, flow, cols, flen, fw, fop, jit=14, bend=0.25, inside=inside_poly(pts))
    body = form(P, d, pal, L, box, core=core, lit=lit, extra=list(pre) + [fur] + list(extra), edge=edge, edge_op=edge_op,
                rim_col=rim_col, rim_d=rim_d, rim_src=rim_src, sd=sd)
    if rough:
        return f'<g {P.rough(rough[0], rough[1], seed)}>{body}</g>'
    return body


def plume(spine, W, prof=(0.3, 0.62, 0.9, 1.0, 0.92, 0.7, 0.42, 0.12)):
    """Outline of a bushy tail / plume along a spine with a width profile (fractions of W)."""
    n = len(spine)
    ws = []
    for i in range(n):
        t = i / max(1, n - 1) * (len(prof) - 1)
        j = min(int(t), len(prof) - 2)
        ws.append(W * lerp(prof[j], prof[j + 1], t - j) / 2)
    return limb(spine, ws, ws, n=4)
