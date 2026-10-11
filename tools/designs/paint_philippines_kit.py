"""Gallery-gouache kit for the Pilipinas collection (philippines_painted.py).

What it adds on top of the shared gouache helpers:
  * gouache_finish(): turns a finished art layer into paint. One SVG filter per design (ids prefixed with the slug):
      - fractal-noise displacement so every edge wobbles like a loaded brush (no ruler-straight vector edges),
      - a gentle unsharp pass that pools pigment at the edges of shapes (dark side darker, light side lighter),
      - two crossing bristle-streak textures (soft-light) so flat areas read as brushed paint,
      - pigment granulation and paper tooth (multiply).
    Lettering stays crisp on top (everything after the TXT marker in the design's part list).
  * soft_ink(): a lost-and-found pen line (broken, warm, variable) used instead of the hard full outline.
  * Cam3: a tiny yaw/pitch pinhole camera so objects can be painted in real 3/4 perspective.
  * painterly helpers: brushed skies, wet-road reflections, dry-brush highlights, glazes, rim light.
Plain SVG (filters, gradients, clipPaths, patterns); Chromium renders it for the web and for print.
"""
import math
import random

TXT = "<!--TXT-->"   # put this in a design's part list: art before it gets painted, text after it stays crisp

_FILTER = """<filter id="{fid}" x="0" y="0" width="600" height="600" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="3" seed="{s1}" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="{edge}" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feGaussianBlur in="d" stdDeviation="{pool_r}" result="bl"/>
<feComposite in="d" in2="bl" operator="arithmetic" k1="0" k2="{k2}" k3="{k3}" k4="0" result="p"/>
<feTurbulence type="fractalNoise" baseFrequency="{bf1}" numOctaves="3" seed="{s2}" result="b1"/>
<feColorMatrix in="b1" type="matrix" values="{c} 0 0 0 {o}  {c} 0 0 0 {o}  {c} 0 0 0 {o}  0 0 0 0 {bristle}" result="b1g"/>
<feBlend in="b1g" in2="p" mode="soft-light" result="t1"/>
<feTurbulence type="fractalNoise" baseFrequency="{bf2}" numOctaves="3" seed="{s3}" result="b2"/>
<feColorMatrix in="b2" type="matrix" values="{c} 0 0 0 {o}  {c} 0 0 0 {o}  {c} 0 0 0 {o}  0 0 0 0 {bristle2}" result="b2g"/>
<feBlend in="b2g" in2="t1" mode="soft-light" result="t2"/>
<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="{s4}" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 {gr}  0 0 0 0 {gg}  0 0 0 0 {gb}  -2.4 0 0 0 {ga}" result="gg"/>
<feComposite in="gg" in2="t2" operator="in" result="g2"/>
<feBlend in="g2" in2="t2" mode="multiply" result="t3"/>
<feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="2" seed="{s5}" result="m"/>
<feColorMatrix in="m" type="matrix" values="{mc} 0 0 0 {mo}  {mc} 0 0 0 {mo}  {mc} 0 0 0 {mo}  0 0 0 0 1" result="mg"/>
<feBlend in="mg" in2="t3" mode="multiply"/>
</filter>"""


def gouache_filter(fid, seed=3, edge=2.6, freq=0.05, pool=0.3, pool_r=1.4, bristle=0.11, bristle2=0.06,
                   grain=0.35, mottle=0.3, stroke_dir="h", grain_rgb=(0.24, 0.16, 0.1), gain=1.8):
    """The paint filter itself (returns the <filter> element)."""
    bf1 = "0.022 0.12" if stroke_dir == "h" else "0.12 0.022"
    bf2 = "0.11 0.022" if stroke_dir == "h" else "0.022 0.11"
    return _FILTER.format(fid=fid, s1=seed, s2=seed + 11, s3=seed + 23, s4=seed + 31, s5=seed + 47, edge=edge, freq=freq,
                          pool_r=pool_r, k2=f"{1 + pool:.3f}", k3=f"{-pool:.3f}", bf1=bf1, bf2=bf2, c=f"{gain:.2f}", o=f"{(1 - gain) / 2:.2f}",
                          bristle=bristle, bristle2=bristle2, mc=f"{0.4 * mottle:.3f}", mo=f"{1 - 0.32 * mottle:.3f}", gr=grain_rgb[0], gg=grain_rgb[1], gb=grain_rgb[2],
                          ga=f"{1.2 * grain:.2f}", mottle=mottle)


def gouache_finish(slug, rendered, **kw):
    """rendered = D.render(parts) where parts contain the TXT marker. Returns the final SVG body."""
    fid = f"{slug}-gf"
    if TXT in rendered:
        art, txt = rendered.split(TXT, 1)
    else:
        art, txt = rendered, ""
    return (f'<defs>{gouache_filter(fid, **kw)}</defs>'
            f'<g transform="translate(300 300) scale(1.012) translate(-300 -300)"><g filter="url(#{fid})">{art}</g></g>{txt}')


# ---------------------------------------------------------------- lost-and-found pen line
def soft_ink(d, color="#4A2E1E", w=2.0, seed=1, passes=2, opacity=0.6):
    """A painter's line: warm, broken (lost and found), thinner second pass. Same signature as gouache.ink."""
    rnd = random.Random(seed)
    out = []
    for i in range(min(passes, 2)):
        dash = " ".join(f"{rnd.uniform(18, 70):.0f} {rnd.uniform(3, 14):.0f}" for _ in range(4))
        ww = w * (0.85 if i == 0 else rnd.uniform(0.35, 0.55))
        dx, dy = rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5)
        op = opacity * (0.75 if i == 0 else 0.45)
        out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{ww:.2f}" stroke-linecap="round" stroke-linejoin="round" '
                   f'stroke-dasharray="{dash}" stroke-dashoffset="{rnd.uniform(0, 60):.0f}" opacity="{op:.2f}" transform="translate({dx:.2f} {dy:.2f})"/>')
    return "".join(out)


def install_soft_ink(*modules, color=None):
    """Swap the hard full-outline pen (gouache.ink) for the lost-and-found line inside the given helper modules
    (affects only this process)."""
    def _ink(d, c="#3A2418", w=2.4, seed=1, passes=2, opacity=0.85):
        if c in ("#3A2418", "#2A1A12", "#2A1408", "#3A2A2A") and color:
            c = color
        return soft_ink(d, c, w * 0.8, seed, passes, opacity * 0.72)
    for m in modules:
        if hasattr(m, "ink"):
            m.ink = _ink
    return _ink


# ---------------------------------------------------------------- 3/4 perspective camera
class Cam3:
    """Pinhole camera. World: X right, Y up, Z forward (metres). The world is first turned by `yaw` degrees
    around Y (so a box aligned with X can be seen in 3/4), then seen from `eye` height with a little `pitch`."""

    def __init__(self, f=520, cx=300, cy=300, yaw=0.0, pitch=0.0, pos=(0, 1.5, -8)):
        self.f, self.cx, self.cy = f, cx, cy
        self.cy_, self.sy_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        self.cp, self.sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
        self.pos = pos

    def cam(self, X, Y, Z):
        x = X * self.cy_ + Z * self.sy_ - self.pos[0]
        z = -X * self.sy_ + Z * self.cy_ - self.pos[2]
        y = Y - self.pos[1]
        y, z = y * self.cp - z * self.sp, y * self.sp + z * self.cp
        return x, y, z

    def __call__(self, X, Y, Z):
        x, y, z = self.cam(X, Y, Z)
        z = max(z, 0.05)
        return (self.cx + self.f * x / z, self.cy - self.f * y / z)

    def eye_world(self):
        """Camera position in world coordinates."""
        x, y, z = self.pos
        # undo pitch is not needed for the position; undo yaw
        X = x * self.cy_ - z * self.sy_
        Z = x * self.sy_ + z * self.cy_
        return (X, y, Z)

    def depth(self, X, Y, Z):
        return self.cam(X, Y, Z)[2]

    def poly(self, pts3):
        return [self(*p) for p in pts3]


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def lerp3(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def quad_at(q, u0, u1, v0, v1):
    """Sub-rectangle of a projected quad q = [p00, p10, p11, p01] (u along p00->p10, v along p00->p01),
    bilinear (good enough for small spans)."""
    def at(u, v):
        a = lerp(q[0], q[1], u)
        b = lerp(q[3], q[2], u)
        return lerp(a, b, v)
    return [at(u0, v0), at(u1, v0), at(u1, v1), at(u0, v1)]


def bil(q, u, v):
    a = lerp(q[0], q[1], u)
    b = lerp(q[3], q[2], u)
    return lerp(a, b, v)


def pd(pts, close=True):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if close else "")


# ---------------------------------------------------------------- painterly marks
def brush_field(seed, box, cols, n, angle=0.0, length=(20, 60), width=(2, 6), op=(0.15, 0.45), curve=0.15, jitter_a=10):
    """Free brush marks (tapered, slightly curved) — not clipped; use inside a clipped group."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        L = rnd.uniform(*length)
        w = rnd.uniform(*width)
        a = math.radians(angle + rnd.uniform(-jitter_a, jitter_a))
        dx, dy = L * math.cos(a), L * math.sin(a)
        nx, ny = -math.sin(a), math.cos(a)
        b = L * curve * rnd.uniform(-1, 1)
        mx, my = x + dx / 2 + nx * b, y + dy / 2 + ny * b
        out.append(f'<path d="M {x:.1f} {y:.1f} Q {mx + nx * w:.1f} {my + ny * w:.1f} {x + dx:.1f} {y + dy:.1f} '
                   f'Q {mx - nx * w * 0.7:.1f} {my - ny * w * 0.7:.1f} {x:.1f} {y:.1f} Z" fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


def dry_brush(seed, pts, w, color, op=0.7, breaks=5):
    """A dry-brush highlight dragged along a polyline: several thin broken parallel hairs."""
    rnd = random.Random(seed)
    out = []
    n = len(pts)
    for h in range(breaks):
        off = (h - breaks / 2) * w / breaks
        seg = []
        for i, (x, y) in enumerate(pts):
            a = pts[max(i - 1, 0)]
            b = pts[min(i + 1, n - 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1
            seg.append((x - dy / L * off, y + dx / L * off))
        dash = " ".join(f"{rnd.uniform(4, 22):.0f} {rnd.uniform(2, 9):.0f}" for _ in range(3))
        out.append(f'<path d="{pd(seg, False)}" fill="none" stroke="{color}" stroke-width="{rnd.uniform(0.7, 1.6):.1f}" '
                   f'stroke-linecap="round" stroke-dasharray="{dash}" stroke-dashoffset="{rnd.uniform(0, 20):.0f}" opacity="{op * rnd.uniform(0.5, 1):.2f}"/>')
    return "".join(out)


def streak_reflection(seed, x, y0, y1, w, color, op=0.6, n=14, wobble=6):
    """Broken vertical reflection streaks on wet road / water under a light at x."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        yy = rnd.uniform(y0, y1)
        t = (yy - y0) / max(1, (y1 - y0))
        ww = w * (1 - 0.6 * t) * rnd.uniform(0.4, 1)
        xx = x + rnd.uniform(-wobble, wobble) * (0.4 + t)
        hh = rnd.uniform(2, 7)
        out.append(f'<rect x="{xx - ww / 2:.1f}" y="{yy:.1f}" width="{ww:.1f}" height="{hh:.1f}" rx="{hh / 2:.1f}" fill="{color}" opacity="{op * (1 - 0.7 * t) * rnd.uniform(0.4, 1):.2f}"/>')
    return "".join(out)


def _rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _hex(t):
    return "#" + "".join(f"{max(0, min(255, round(v))):02X}" for v in t)


def color_at(stops, t):
    """Colour of a gradient (list of (offset, colour)) at offset t."""
    if t <= stops[0][0]:
        return stops[0][1]
    for (o1, c1, *_), (o2, c2, *_) in zip(stops, stops[1:]):
        if o1 <= t <= o2:
            u = (t - o1) / max(1e-6, o2 - o1)
            a, b = _rgb(c1), _rgb(c2)
            return _hex(tuple(x + (y - x) * u for x, y in zip(a, b)))
    return stops[-1][1]


def tint(c, t, toward="#FFFFFF"):
    a, b = _rgb(c), _rgb(toward)
    return _hex(tuple(x + (y - x) * t for x, y in zip(a, b)))


def sky_paint(D, stops, seed, h=600, n=110, angle=-2.0, y0=0, sl=(70, 220), sw=(4, 12), op=(0.18, 0.42), var=0.12):
    """A painted sky: the gradient (stops' offsets are fractions of 600 px, like a full-canvas gradient), then broad
    horizontal brush strokes whose colour is the local sky colour pushed a little lighter/warmer or darker/cooler,
    so the sky reads as worked paint rather than a smooth vector ramp."""
    g = D.lin(stops, 0, 0, 0, 600, "userSpaceOnUse")
    out = [f'<rect x="-10" y="{y0 - 10}" width="620" height="{h - y0 + 20}" fill="{g}"/>']
    rnd = random.Random(seed)
    marks = []
    for _ in range(n):
        y = rnd.uniform(y0 - 5, h)
        x = rnd.uniform(-80, 600)
        c = color_at(stops, y / 600)
        c = tint(c, rnd.uniform(0.04, var), rnd.choice(["#FFFFFF", "#FFE8C8", "#1A1030", "#3A2A5A"]))
        L = rnd.uniform(*sl)
        w = rnd.uniform(*sw)
        a = math.radians(angle + rnd.uniform(-3, 3))
        dx, dy = L * math.cos(a), L * math.sin(a)
        marks.append(f'<path d="M {x:.1f} {y:.1f} Q {x + dx / 2:.1f} {y + dy / 2 - w:.1f} {x + dx:.1f} {y + dy:.1f} Q {x + dx / 2:.1f} {y + dy / 2 + w * 0.6:.1f} {x:.1f} {y:.1f} Z" '
                     f'fill="{c}" opacity="{rnd.uniform(*op):.2f}"/>')
    out.append(f'<g>{"".join(marks)}</g>')
    return "".join(out)


def ripple_filter(fid, seed=5, scale=10, freq="0.004 0.12", blur=0.8):
    """For reflections in wet streets / water: horizontal ripples smear the mirrored image."""
    return (f'<filter id="{fid}" x="-0.1" y="-0.1" width="1.2" height="1.2" color-interpolation-filters="sRGB">'
            f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="2" seed="{seed}" result="n"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{scale}" xChannelSelector="G" yChannelSelector="R" result="d"/>'
            f'<feGaussianBlur in="d" stdDeviation="{blur} {blur * 0.3:.2f}"/></filter>')


def soft_filter(fid, blur=2.0):
    return f'<filter id="{fid}" x="-0.5" y="-0.5" width="2" height="2"><feGaussianBlur stdDeviation="{blur}"/></filter>'


def vstreaks(seed, x, y0, y1, w, color, op=0.7, n=7, spread=5):
    """Long broken vertical streaks (a light's reflection on wet ground / water)."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        xx = x + rnd.uniform(-spread, spread)
        a = rnd.uniform(y0, y0 + (y1 - y0) * 0.3)
        b = rnd.uniform(a + (y1 - y0) * 0.3, y1)
        ww = w * rnd.uniform(0.3, 1)
        out.append(f'<path d="M {xx:.1f} {a:.1f} Q {xx + ww:.1f} {(a + b) / 2:.1f} {xx + rnd.uniform(-2, 2):.1f} {b:.1f} Q {xx - ww:.1f} {(a + b) / 2:.1f} {xx:.1f} {a:.1f} Z" '
                   f'fill="{color}" opacity="{op * rnd.uniform(0.4, 1):.2f}"/>')
    return "".join(out)


def cloud_bank(D, cx, cy, w, h, seed, lit="#FFF4DC", mid="#F2D8C8", shade="#B8A0B8", light_dir=-1.0, n=26, soft=1.6, op=0.92):
    """A painted cumulus bank: many soft overlapping dabs on a flat-ish base, warm on the sun side, cool underneath,
    with soft (blurred) edges and a few crisp lit strokes on top."""
    rnd = random.Random(seed)
    fid = D.nid()
    D.defs.append(soft_filter(fid, soft))
    from gouache import blob
    dabs = []
    for i in range(n):
        t = rnd.random()
        x = cx + (t - 0.5) * w
        top = math.sin(math.pi * t) ** 0.8
        r = (0.18 + 0.5 * top) * h * rnd.uniform(0.6, 1.0)
        y = cy - top * h * 0.55 * rnd.uniform(0.5, 1.0) + r * 0.3
        dabs.append((x, y, r))
    base = []
    for x, y, r in sorted(dabs, key=lambda d: -d[1]):
        base.append(f'<path d="{blob(x, y, r, r * 0.8, rnd.randint(0, 9999), 0.12, 12)}" fill="{mid}"/>')
    shade_g = D.lin([(0, shade, 0), (0.55, shade, 0.2), (1, shade, 0.85)], 0, cy - h * 0.6, 0, cy + h * 0.25, "userSpaceOnUse")
    lit_g = D.lin([(0, lit, 0.95), (1, lit, 0)], cx + light_dir * w * 0.5, 0, cx - light_dir * w * 0.2, 0, "userSpaceOnUse")
    allp = "".join(base)
    out = [f'<g filter="url(#{fid})" opacity="{op}">{allp}',
           f'<g fill="{shade_g}">' + "".join(f'<path d="{blob(x, y, r, r * 0.8, int(x * 7 + y), 0.12, 12)}"/>' for x, y, r in dabs) + '</g>',
           f'<g fill="{lit_g}">' + "".join(f'<path d="{blob(x + light_dir * r * 0.15, y - r * 0.2, r * 0.75, r * 0.6, int(x * 3 + y), 0.14, 12)}"/>' for x, y, r in dabs) + '</g>',
           '</g>']
    for x, y, r in dabs:
        if rnd.random() < 0.5:
            a0 = math.radians(200 if light_dir < 0 else -20)
            pts = [(x + math.cos(a0 + k * 0.35 * (1 if light_dir < 0 else -1)) * r * 0.85, y + math.sin(a0 + k * 0.35 * (1 if light_dir < 0 else -1)) * r * 0.7) for k in range(4)]
            out.append(f'<path d="M {pts[0][0]:.1f} {pts[0][1]:.1f} Q {pts[1][0]:.1f} {pts[1][1]:.1f} {pts[2][0]:.1f} {pts[2][1]:.1f}" fill="none" stroke="{lit}" '
                       f'stroke-width="{max(1.2, r * 0.12):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.4, 0.8):.2f}"/>')
    return "".join(out)


_STEAM_N = [0]


def soft_steam(cx, y, h, seed, col="#FFFFFF", n=3, gap=24, w=7, op=0.6, uid="st"):
    """Steam painted as it looks: soft, blurred, translucent ribbons that widen and fade as they rise, with a
    brighter thin core near the food. Carries its own blur filter (unique id)."""
    _STEAM_N[0] += 1
    fid = f"{uid}-soft{_STEAM_N[0]}"
    rnd = random.Random(seed)
    out = [f'<defs><filter id="{fid}" x="-1" y="-1" width="3" height="3"><feGaussianBlur stdDeviation="{max(1.5, w * 0.45):.1f}"/></filter>'
           f'<linearGradient id="{fid}g" x1="0" y1="{y:.1f}" x2="0" y2="{y - h:.1f}" gradientUnits="userSpaceOnUse">'
           f'<stop offset="0" stop-color="{col}" stop-opacity="{op}"/><stop offset="0.55" stop-color="{col}" stop-opacity="{op * 0.6:.2f}"/>'
           f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient></defs>']
    paths = []
    for i in range(n):
        x0 = cx + (i - (n - 1) / 2) * gap + rnd.uniform(-4, 4)
        a = rnd.uniform(8, 16) * (1 if i % 2 else -1)
        pts = [(x0, y), (x0 + a * 0.6, y - h * 0.3), (x0 - a * 0.5, y - h * 0.6), (x0 + a * 0.7, y - h)]
        d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f} C {pts[1][0]:.1f} {pts[1][1]:.1f} {pts[2][0]:.1f} {pts[2][1]:.1f} {pts[3][0]:.1f} {pts[3][1]:.1f}"
        paths.append(f'<path d="{d}" fill="none" stroke="url(#{fid}g)" stroke-width="{w * rnd.uniform(1.6, 2.4):.1f}" stroke-linecap="round"/>')
        paths.append(f'<path d="{d}" fill="none" stroke="url(#{fid}g)" stroke-width="{w * 0.5:.1f}" stroke-linecap="round" opacity="0.8"/>')
    out.append(f'<g filter="url(#{fid})">{"".join(paths)}</g>')
    return "".join(out)


def fur(seed, box, cols, n, flow, length=(4, 9), width=(0.6, 1.4), op=(0.35, 0.85), inside=None):
    """Short hair strokes whose direction follows flow(x, y) -> angle in degrees. Use inside a clip group.
    inside(x, y) -> bool optionally rejects points (cheap masking)."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    groups = {}
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if inside and not inside(x, y):
            continue
        a = math.radians(flow(x, y) + rnd.uniform(-14, 14))
        L = rnd.uniform(*length)
        c = rnd.choice(cols)
        w = round(rnd.uniform(*width), 1)
        o = round(rnd.uniform(*op), 1)
        mx, my = x + math.cos(a) * L * 0.5 + rnd.uniform(-0.8, 0.8), y + math.sin(a) * L * 0.5 + rnd.uniform(-0.8, 0.8)
        groups.setdefault((c, w, o), []).append(f"M{x:.1f} {y:.1f}Q{mx:.1f} {my:.1f} {x + math.cos(a) * L:.1f} {y + math.sin(a) * L:.1f}")
    return "".join(f'<path d="{"".join(v)}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" opacity="{o}"/>'
                   for (c, w, o), v in groups.items())


def fuzzy_edge(seed, pts, cols, n_per=1.0, length=(3, 7), width=(0.6, 1.2), op=(0.4, 0.8), outward=1, tilt=0.0):
    """Hairs crossing a silhouette outline (closed point list, clockwise or not): breaks the vector edge."""
    rnd = random.Random(seed)
    groups = {}
    m = len(pts)
    for i in range(m):
        (ax, ay), (bx, by) = pts[i], pts[(i + 1) % m]
        L = math.hypot(bx - ax, by - ay)
        nx, ny = (by - ay) / (L or 1), -(bx - ax) / (L or 1)
        for _ in range(int(L * n_per / 3) + 1):
            t = rnd.random()
            x, y = ax + (bx - ax) * t, ay + (by - ay) * t
            ln = rnd.uniform(*length)
            a = math.atan2(ny * outward, nx * outward) + rnd.uniform(-0.5, 0.5) + tilt
            x0, y0 = x - math.cos(a) * ln * 0.4, y - math.sin(a) * ln * 0.4
            c = rnd.choice(cols)
            w = round(rnd.uniform(*width), 1)
            o = round(rnd.uniform(*op), 1)
            groups.setdefault((c, w, o), []).append(f"M{x0:.1f} {y0:.1f}L{x0 + math.cos(a) * ln:.1f} {y0 + math.sin(a) * ln:.1f}")
    return "".join(f'<path d="{"".join(v)}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" opacity="{o}"/>'
                   for (c, w, o), v in groups.items())


def bokeh(D, seed, box, cols, n=14, r=(6, 22), op=(0.15, 0.4), blur=3):
    """Out-of-focus light discs (blurred) for night / forest backgrounds."""
    rnd = random.Random(seed)
    fid = D.nid()
    D.defs.append(soft_filter(fid, blur))
    x0, y0, x1, y1 = box
    dots = "".join(f'<circle cx="{rnd.uniform(x0, x1):.1f}" cy="{rnd.uniform(y0, y1):.1f}" r="{rnd.uniform(*r):.1f}" fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*op):.2f}"/>' for _ in range(n))
    return f'<g filter="url(#{fid})">{dots}</g>'


def rain_sheets(D, seed, box, col="#DCE6F2", n=220, ang=104, L=(18, 40), op=(0.15, 0.45), blur=0.6, curtains=4):
    """Rain as a painter sees it: soft veils (blurred diagonal curtains) plus thin streaks that read as falling."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    fid = D.nid()
    D.defs.append(soft_filter(fid, 10))
    out = []
    a = math.radians(ang)
    veils = []
    for _ in range(curtains):
        cx = rnd.uniform(x0, x1)
        w = rnd.uniform(40, 110)
        dx = math.cos(a) * (y1 - y0) / max(0.2, math.sin(a))
        veils.append(f'<path d="M {cx:.1f} {y0:.1f} L {cx + w:.1f} {y0:.1f} L {cx + w + dx:.1f} {y1:.1f} L {cx + dx:.1f} {y1:.1f} Z" fill="{col}" opacity="{rnd.uniform(0.1, 0.22):.2f}"/>')
    out.append(f'<g filter="url(#{fid})">{"".join(veils)}</g>')
    groups = {}
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        l = rnd.uniform(*L)
        o = round(rnd.uniform(*op), 1)
        groups.setdefault(o, []).append(f"M{x:.1f} {y:.1f}l{math.cos(a) * l:.1f} {math.sin(a) * l:.1f}")
    fid2 = D.nid()
    D.defs.append(soft_filter(fid2, blur))
    out.append(f'<g filter="url(#{fid2})">' + "".join(f'<path d="{"".join(v)}" stroke="{col}" stroke-width="1.2" stroke-linecap="round" opacity="{o}" fill="none"/>' for o, v in groups.items()) + '</g>')
    return "".join(out)
