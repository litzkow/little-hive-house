"""Painterly kit for the India collection (gallery upgrade).

What it adds on top of the shared gouache helpers:
  * finish_art(): the art is drawn inside an SVG filter that breaks every edge like a loaded brush, lays a bristle /
    paper texture and pigment granulation over the paint, while the lettering stays crisp and unfiltered on top.
  * modelled(): one form painted the way a gouache painter builds it: a warm-to-cool gradient body, a core shadow
    band, reflected light, a dry-brush light side, form-following strokes in 3-4 tints, and a broken ink line that
    is only present on the shadow side ("lost and found" edges).
  * glaze(), vignette(), light_shaft(), haze_band(): atmosphere.
  * Figure silhouettes built on a real 7.5-head skeleton (tapered limbs with muscle, shoulders, neck, hands,
    clothing drapery), used small and backlit, never as toys.
  * Cam3: a tiny perspective camera so vehicles and buildings are drawn in a true three-quarter view.
Nothing here edits a shared module; it only imports from them.
"""
import math
import random

from fall_gouache_a import bbox, mix, shift, taper
from gouache import blob, ink, smooth_closed, smooth_open, strokes, wash

INK = "#3A2418"


# ---------------------------------------------------------------- painterly filter and finish
_F = '''<filter id="{fid}" x="-20" y="-20" width="640" height="640" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
<feTurbulence type="fractalNoise" baseFrequency="{bf}" numOctaves="3" seed="{s1}" result="n"/>
<feDisplacementMap in="SourceGraphic" in2="n" scale="{edge}" xChannelSelector="R" yChannelSelector="G" result="d"/>
<feTurbulence type="fractalNoise" baseFrequency="0.022 0.30" numOctaves="3" seed="{s2}" result="b1"/>
<feTurbulence type="fractalNoise" baseFrequency="0.30 0.025" numOctaves="2" seed="{s4}" result="b2"/>
<feComposite in="b1" in2="b2" operator="arithmetic" k1="0" k2="0.6" k3="0.4" k4="0" result="b"/>
<feColorMatrix in="b" type="matrix" values="0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 0 0.5  0 0 0 {bristle} 0" result="bs"/>
<feComposite in="bs" in2="d" operator="in" result="bs2"/>
<feBlend in="d" in2="bs2" mode="soft-light" result="t"/>
<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="{s3}" result="g"/>
<feColorMatrix in="g" type="matrix" values="0 0 0 0 0.30  0 0 0 0 0.22  0 0 0 0 0.16  0 0 0 {grain} 0" result="gg"/>
<feComposite in="gg" in2="t" operator="in" result="g3"/>
<feBlend in="t" in2="g3" mode="multiply"/>
</filter>'''


def pfilter(fid, seed, edge=3.0, freq=0.045, bristle=0.5, grain=0.2):
    return _F.format(fid=fid, s1=seed, s2=seed + 17, s3=seed + 31, s4=seed + 47, edge=edge, bf=freq, bristle=bristle, grain=grain)


def finish_art(D, art, txt, seed, under="#E8D8C0", edge=3.0, freq=0.045, bristle=0.5, grain=0.2, txt_filter=False):
    """art: list of SVG fragments (the painting); txt: list of fragments drawn crisp on top (lettering).
    Returns the full body with defs."""
    fid = f"{D.u}-pf"
    defs = "<defs>" + "".join(D.defs) + pfilter(fid, seed, edge, freq, bristle, grain)
    tf = ""
    if txt_filter:
        defs += pfilter(fid + "t", seed + 5, 1.2, 0.08, 0.25, 0.12)
        tf = f' filter="url(#{fid}t)"'
    defs += "</defs>\n"
    return (defs + f'<rect x="-10" y="-10" width="620" height="620" fill="{under}"/>\n'
            f'<g filter="url(#{fid})">' + "\n".join(p for p in art if p) + "</g>\n"
            f"<g{tf}>" + "\n".join(p for p in txt if p) + "</g>")


# ---------------------------------------------------------------- light and atmosphere
def glaze(D, stops, x1=0, y1=0, x2=0, y2=1, blend=None):
    """A transparent colour glaze over the whole picture (warm light, cool shadow)."""
    g = D.lin(stops, x1, y1, x2, y2)
    mb = f' style="mix-blend-mode:{blend}"' if blend else ""
    return f'<rect x="-10" y="-10" width="620" height="620" fill="{g}"{mb}/>'


def vignette(D, col="#2A140A", op=0.35, r=0.75, cx=0.5, cy=0.5):
    g = D.rad([(0, col, 0), (0.62, col, 0), (1, col, op)], cx, cy, r)
    return f'<rect x="-10" y="-10" width="620" height="620" fill="{g}"/>'


def light_shaft(D, x0, y0, x1a, x1b, y1, col="#FFF2C8", op=0.25):
    g = D.lin([(0, col, op), (1, col, 0)], x0, y0, (x1a + x1b) / 2, y1, "userSpaceOnUse")
    return f'<path d="M {x0 - 6:.1f} {y0:.1f} L {x0 + 6:.1f} {y0:.1f} L {x1b:.1f} {y1:.1f} L {x1a:.1f} {y1:.1f} Z" fill="{g}"/>'


def haze_band(D, y, h, col, op=0.6, x0=-20, x1=620):
    g = D.lin([(0, col, 0), (0.5, col, op), (1, col, 0)], 0, y - h / 2, 0, y + h / 2, "userSpaceOnUse")
    return f'<rect x="{x0}" y="{y - h / 2:.1f}" width="{x1 - x0}" height="{h:.1f}" fill="{g}"/>'


def scumble(D, d, box, cols, seed, n=60, angle=-20, length=(10, 40), width=(2, 8), op=(0.06, 0.2)):
    """Loose dry-brush scumble over an area (broken colour)."""
    return strokes(D.nid(), d, box, cols, seed, n=n, angle=angle, length=length, width=width, opacity=op, curve=0.35)


def dabs(seed, box, cols, n=60, r=(2, 6), op=(0.3, 0.8), squash=(0.5, 0.9), clip=None):
    """Loose round brush dabs (foliage light, flower dots, impasto touches)."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y, rr = rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(*r)
        out.append(f'<path d="{blob(x, y, rr, rr * rnd.uniform(*squash), rnd.randint(0, 99999), 0.25, 8, rnd.uniform(0, 180))}" '
                   f'fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*op):.2f}"/>')
    g = "".join(out)
    return f'<g {clip}>{g}</g>' if clip else g


def modelled(D, pts, pal, seed, light=(-0.7, -0.7), angle=-90, n=None, inkw=1.6, inkc=INK, refl=None,
             cols=None, hi=0.55, core=0.5, sop=(0.12, 0.4), slen=None, sw=None, curve=0.25, edge=True, lost=True):
    """A form painted with light: gradient body (light side -> shadow side), a core-shadow band, an optional
    reflected-light rim on the shadow side, form-following strokes, a dry-brush highlight, and an ink line that
    fades out on the lit side (lost edge) and is firm on the shadow side (found edge)."""
    lt, base, dk = pal
    d = smooth_closed(pts)
    x0, y0, x1, y1 = bbox(pts)
    W, H = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    L = math.hypot(*light) or 1
    lx, ly = light[0] / L, light[1] / L
    R = 0.5 * math.hypot(W * lx, H * ly) + 1
    ax, ay = cx + lx * R, cy + ly * R            # lit end
    bx, by = cx - lx * R, cy - ly * R            # shadow end
    g = D.lin([(0, mix(lt, "#FFFFFF", 0.1)), (0.35, lt), (0.55, base), (0.8, dk), (1, mix(dk, base, 0.35))], ax, ay, bx, by, "userSpaceOnUse")
    out = [f'<path d="{d}" fill="{base}"/>', f'<path d="{d}" fill="{g}"/>']
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    # core shadow: a soft band just past the terminator
    if core:
        gc = D.lin([(0, dk, 0), (0.58, dk, 0), (0.72, dk, core * 0.55), (0.86, dk, core * 0.25), (1, dk, 0)], ax, ay, bx, by, "userSpaceOnUse")
        inner.append(f'<rect x="{x0 - 5:.1f}" y="{y0 - 5:.1f}" width="{W + 10:.1f}" height="{H + 10:.1f}" fill="{gc}"/>')
    if refl:
        sp = shift(pts, lx * W * 0.06, ly * H * 0.06)
        inner.append(f'<path d="{d} {smooth_closed(sp)}" fill-rule="evenodd" fill="{refl}" opacity="0.35"/>')
    m = min(W, H)
    nn = n or int(max(12, min(260, W * H / 70)))
    slen = slen or (0.1 * max(W, H), 0.38 * max(W, H))
    sw = sw or (max(0.6, m * 0.012), max(1.2, m * 0.035))
    inner.append(strokes(D.nid(), d, (x0 - 4, y0 - 4, x1 + 4, y1 + 4), cols or [lt, dk, base, mix(lt, "#FFFFFF", 0.3)], seed + 1,
                         n=nn, angle=angle, length=slen, width=sw, opacity=sop, curve=curve))
    if hi:
        sp = shift(pts, -lx * W * 0.07, -ly * H * 0.07)
        inner.append(f'<path d="{d} {smooth_closed(sp)}" fill-rule="evenodd" fill="{mix(lt, "#FFFFFF", 0.45)}" opacity="{hi * 0.6:.2f}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    if edge:
        out.append(f'<path d="{d}" fill="none" stroke="{dk}" stroke-width="{max(1.0, m * 0.012):.1f}" opacity="0.35"/>')
    if inkw:
        if lost:
            gi = D.lin([(0, inkc, 0.05), (0.45, inkc, 0.25), (1, inkc, 0.95)], ax, ay, bx, by, "userSpaceOnUse")
            out.append(f'<path d="{d}" fill="none" stroke="{gi}" stroke-width="{inkw:.2f}" stroke-linejoin="round"/>')
        else:
            out.append(ink(d, inkc, inkw, seed + 2, 2, 0.75))
    return "".join(out)


def lit_line(D, d, col, w, light_from, to, op=(0.05, 0.9)):
    """A stroke whose opacity runs from op[0] at `light_from` to op[1] at `to` (lost and found line)."""
    g = D.lin([(0, col, op[0]), (1, col, op[1])], light_from[0], light_from[1], to[0], to[1], "userSpaceOnUse")
    return f'<path d="{d}" fill="none" stroke="{g}" stroke-width="{w:.2f}" stroke-linecap="round" stroke-linejoin="round"/>'


def cast_shadow(D, pts, col="#2A1408", op=0.45, soft=True):
    """A cast shadow polygon that fades out away from the object (pts listed from the contact edge outward)."""
    d = smooth_closed(pts)
    x0, y0, x1, y1 = bbox(pts)
    return f'<path d="{d}" fill="{col}" opacity="{op}"/>'


# ---------------------------------------------------------------- perspective camera
class Cam3:
    """Pinhole camera: eye at `pos`, looking at `target`, focal length f (px), picture centre (cx, cy)."""

    def __init__(self, pos, target, f=700, cx=300, cy=300, roll=0.0):
        self.pos = pos
        fx, fy, fz = (target[i] - pos[i] for i in range(3))
        L = math.sqrt(fx * fx + fy * fy + fz * fz)
        self.fw = (fx / L, fy / L, fz / L)
        up = (0, 0, 1)
        rx = (self.fw[1] * up[2] - self.fw[2] * up[1], self.fw[2] * up[0] - self.fw[0] * up[2], self.fw[0] * up[1] - self.fw[1] * up[0])
        L = math.sqrt(sum(c * c for c in rx))
        self.rt = tuple(c / L for c in rx)
        f_, r_ = self.fw, self.rt
        self.up = (r_[1] * f_[2] - r_[2] * f_[1], r_[2] * f_[0] - r_[0] * f_[2], r_[0] * f_[1] - r_[1] * f_[0])
        self.f, self.cx, self.cy, self.roll = f, cx, cy, math.radians(roll)

    def depth(self, p):
        v = [p[i] - self.pos[i] for i in range(3)]
        return sum(v[i] * self.fw[i] for i in range(3))

    def __call__(self, p):
        v = [p[i] - self.pos[i] for i in range(3)]
        z = sum(v[i] * self.fw[i] for i in range(3))
        x = sum(v[i] * self.rt[i] for i in range(3))
        y = sum(v[i] * self.up[i] for i in range(3))
        sx, sy = self.f * x / z, -self.f * y / z
        c, s = math.cos(self.roll), math.sin(self.roll)
        return (self.cx + sx * c - sy * s, self.cy + sx * s + sy * c)

    def pts(self, ps):
        return [self(p) for p in ps]


# ---------------------------------------------------------------- figure silhouettes (7.5 heads, real anatomy)
def _limb(a, b, w0, w1, bulge=0.0, at=0.35, n=8, back=0.0):
    """Tapered limb from a to b (widths w0 -> w1) with a muscle swell of `bulge`*w0 around `at` (0..1).
    back shifts the swell toward one side (+ = left of the a->b direction)."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        w = w0 + (w1 - w0) * t
        bump = bulge * w0 * math.exp(-((t - at) / 0.24) ** 2)
        wl = w / 2 + bump * (0.5 + back)
        wr = w / 2 + bump * (0.5 - back)
        x, y = ax + dx * t, ay + dy * t
        left.append((x + nx * wl, y + ny * wl))
        right.append((x - nx * wr, y - ny * wr))
    return left + right[::-1]


def _pt(o, ang, L):
    return (o[0] + math.cos(math.radians(ang)) * L, o[1] + math.sin(math.radians(ang)) * L)


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _circ(c, r, n=10):
    return [(c[0] + r * math.cos(2 * math.pi * i / n), c[1] + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def figure_shapes(H, pose, cloth=None, hair="short", build=1.0, female=False):
    """Skeleton -> list of closed outlines (local coords, feet at y=0, facing +x).  Angles in degrees, 0 = +x,
    90 = down.  Keys: torso (pelvis->neck, -90 upright), head (tilt), ua_/fa_/hand_ (upper arm, forearm, hand)
    and th_/sh_/ft_ (thigh, shin, foot) for the near (l) and far (r) side, crouch (0..0.4 lowers the pelvis)."""
    u = H / 7.5
    p = dict(torso=-90, head=0, ua_l=96, fa_l=92, ua_r=84, fa_r=88, th_l=92, sh_l=90, th_r=88, sh_r=90, crouch=0.0)
    p.update(pose)
    thigh, shin, foot = 1.9 * u, 1.85 * u, 0.95 * u
    upper, fore, hand = 1.4 * u, 1.2 * u, 0.7 * u
    torso_len = 2.5 * u
    bw = build * (0.88 if female else 1.0)
    pel = (0.0, -(thigh + shin + 0.12 * u) * (1 - p["crouch"]))
    shapes, joints = [], {}
    tang = math.radians(p["torso"] + 90)
    c, s = math.cos(tang), math.sin(tang)

    def tf(lx, ly):            # torso frame: lx across (+ = toward viewer side l), ly up the spine from the pelvis
        return (pel[0] + lx * c + ly * s, pel[1] + lx * s - ly * c)
    hips = {"l": tf(0.32 * u, 0.0), "r": tf(-0.32 * u, 0.0)}
    for k in ("r", "l"):
        h = hips[k]
        kn = _pt(h, p["th_" + k], thigh)
        an = _pt(kn, p["sh_" + k], shin)
        shapes.append(_limb(h, kn, 0.82 * u * bw, 0.42 * u * bw, 0.18, 0.25, back=0.1))
        shapes.append(_circ(kn, 0.22 * u * bw))
        shapes.append(_limb(kn, an, 0.42 * u * bw, 0.21 * u * bw, 0.28, 0.3, back=-0.35))
        fa = p.get("ft_" + k, 0.0)
        heel = _pt(an, fa + 180, 0.2 * u)
        toe = _pt(an, fa, foot * 0.85)
        sole = 0.13 * u
        foot_pts = [_pt(heel, fa - 90, 0.05 * u), _pt(an, fa - 90, 0.2 * u), _pt(_lerp(an, toe, 0.55), fa - 90, 0.12 * u),
                    _pt(toe, fa - 90, 0.05 * u), _pt(toe, fa + 90, sole), _pt(heel, fa + 90, sole)]
        shapes.append(foot_pts)
        joints[k] = (h, kn, an)
    # torso outline in its own frame (male/female differ at chest, waist and hip)
    sw = (0.98 if not female else 0.86) * u * bw     # half shoulder width
    ww = (0.5 if not female else 0.42) * u * bw     # half waist
    hw = (0.62 if not female else 0.7) * u * bw     # half hip
    tor = [(-hw * 0.9, -0.15 * u), (0, -0.32 * u), (hw * 0.9, -0.15 * u), (hw, 0.25 * u), (ww, 0.95 * u), (ww * 1.12, 1.4 * u),
           (sw * 0.86, 2.0 * u), (sw * 0.97, 2.22 * u), (sw * 0.7, 2.42 * u), (0.22 * u, 2.6 * u), (-0.22 * u, 2.6 * u),
           (-sw * 0.7, 2.42 * u), (-sw * 0.97, 2.22 * u), (-sw * 0.86, 2.0 * u), (-ww * 1.12, 1.4 * u), (-ww, 0.95 * u), (-hw, 0.25 * u)]
    if female:
        tor[6:7] = [(sw * 0.9, 1.75 * u), (sw * 0.86, 2.0 * u)]
    shapes.append([tf(*q) for q in tor])
    shoulders = {"l": tf(sw * 0.78, 2.28 * u), "r": tf(-sw * 0.78, 2.28 * u)}
    for k in ("r", "l"):
        sh = shoulders[k]
        el = _pt(sh, p["ua_" + k], upper)
        wr = _pt(el, p["fa_" + k], fore)
        shapes.append(_circ(sh, 0.27 * u * bw))
        shapes.append(_limb(sh, el, 0.48 * u * bw, 0.3 * u * bw, 0.22, 0.32))
        shapes.append(_circ(el, 0.16 * u * bw))
        shapes.append(_limb(el, wr, 0.34 * u * bw, 0.2 * u * bw, 0.25, 0.22, back=0.2))
        ha = p.get("hand_" + k)
        ha = p["fa_" + k] if ha is None else ha
        tip = _pt(wr, ha, hand)
        hp = [_pt(wr, ha - 90, 0.11 * u), _pt(_lerp(wr, tip, 0.45), ha - 90, 0.17 * u), _pt(tip, ha - 90, 0.07 * u), tip,
              _pt(tip, ha + 90, 0.06 * u), _pt(_lerp(wr, tip, 0.5), ha + 90, 0.16 * u), _pt(wr, ha + 90, 0.11 * u)]
        if p.get("fist_" + k):
            hp = _circ(_lerp(wr, tip, 0.35), 0.17 * u)
        shapes.append(hp)
        joints["arm_" + k] = (sh, el, wr, tip)
    # neck and head
    nb = tf(0, 2.5 * u)
    ha_ = p["torso"] + p["head"]
    nt = _pt(nb, ha_, 0.42 * u)
    shapes.append(_limb(tf(0, 2.3 * u), nt, 0.42 * u, 0.32 * u))
    hc = _pt(nt, ha_, 0.42 * u)
    hc = _pt(hc, ha_ + 90, -0.06 * u)
    r_ = math.radians(ha_ + 90)
    head = []
    prof = [(0.0, -0.52), (0.26, -0.47), (0.4, -0.28), (0.44, -0.05), (0.52, 0.06), (0.44, 0.16), (0.42, 0.3), (0.3, 0.48),
            (0.1, 0.52), (-0.18, 0.4), (-0.3, 0.2), (-0.42, 0.0), (-0.4, -0.25), (-0.26, -0.45)]
    for hx, hy in prof:
        hx, hy = hx * u, hy * u
        head.append((hc[0] + hx * math.cos(r_) - hy * math.sin(r_), hc[1] + hx * math.sin(r_) + hy * math.cos(r_)))
    shapes.append(head)
    if hair in ("bun", "long", "plait"):
        bc = (hc[0] + (-0.42 * u) * math.cos(r_) - (0.1 * u) * math.sin(r_), hc[1] + (-0.42 * u) * math.sin(r_) + (0.1 * u) * math.cos(r_))
        shapes.append(_circ(bc, 0.2 * u))
        if hair in ("long", "plait"):
            shapes.append(_limb(bc, (bc[0] - 0.15 * u, bc[1] + 1.8 * u), 0.28 * u, 0.1 * u))
    if hair == "turban":
        shapes.append(_circ(_pt(hc, ha_, 0.22 * u), 0.5 * u, 14))
    # clothing drapery (one colour, it only changes the outline)
    jl, jr = joints["l"], joints["r"]
    if cloth in ("kurta", "frock", "sari"):
        hem_t = {"kurta": 0.08, "frock": 0.0, "sari": 0.97}[cloth]
        hl, hr = _lerp(jl[1], jl[2], hem_t), _lerp(jr[1], jr[2], hem_t)
        if cloth == "frock":
            hl, hr = _lerp(jl[0], jl[1], 0.85), _lerp(jr[0], jr[1], 0.85)
        fl = {"kurta": 0.16, "frock": 0.38, "sari": 0.14}[cloth] * u
        lo_x, hi_x = min(hl[0], hr[0]) - fl, max(hl[0], hr[0]) + fl
        hy = max(hl[1], hr[1])
        mid = (hi_x + lo_x) / 2
        top_y = 1.9 if cloth != "sari" else 1.2
        sk = [tf(sw * 0.84, top_y * u), tf(hw * 1.06, 0.5 * u), (hi_x, hy - 0.08 * u), (hi_x - 0.12 * u, hy + 0.02 * u), (mid + 0.15 * u, hy + 0.05 * u),
              (mid - 0.1 * u, hy - 0.02 * u), (lo_x + 0.1 * u, hy + 0.04 * u), (lo_x, hy - 0.06 * u), tf(-hw * 1.06, 0.5 * u), tf(-sw * 0.84, top_y * u)]
        shapes.append(sk)
        if cloth == "sari":
            shp = shoulders["l"]
            shapes.append(_limb(_pt(shp, -90, 0.12 * u), tf(-hw * 1.25, -0.7 * u), 0.42 * u, 0.62 * u, 0.1, 0.5))
        if cloth == "kurta":
            for k in ("l", "r"):
                h_, kn_, an_ = joints[k]
                shapes.append(_limb(kn_, _lerp(kn_, an_, 1.0), 0.5 * u, 0.36 * u))
    if cloth in ("dhoti", "lungi", "pyjama"):
        hem_t = {"dhoti": 0.75, "lungi": 0.92, "pyjama": 1.0}[cloth]
        for k in ("l", "r"):
            h_, kn_, an_ = joints[k]
            shapes.append(_limb(h_, _lerp(kn_, an_, hem_t), 0.95 * u, (0.62 if cloth != "pyjama" else 0.36) * u, 0.1, 0.4))
        if cloth == "lungi":
            a, b = _lerp(jl[1], jl[2], 0.92), _lerp(jr[1], jr[2], 0.92)
            shapes.append([tf(hw * 1.05, 0.2 * u), (max(a[0], b[0]) + 0.15 * u, max(a[1], b[1])), (min(a[0], b[0]) - 0.15 * u, max(a[1], b[1])), tf(-hw * 1.05, 0.2 * u)])
    if cloth == "shorts":
        for k in ("l", "r"):
            h_, kn_, an_ = joints[k]
            shapes.append(_limb(h_, _lerp(h_, kn_, 0.75), 0.98 * u, 0.62 * u))
    return shapes, joints


def figure(x, base, H, pose, col, rim=None, rim_side=-1, facing=1, cloth=None, hair="short", build=1.0, female=False,
           rim_w=None, extra=None, op=1.0):
    """A human silhouette (one colour, believable anatomy) with an optional rim of light on rim_side (-1 left)."""
    shapes, joints = figure_shapes(H, pose, cloth, hair, build, female)
    if extra:
        shapes += extra(joints, H / 7.5)
    tr = f'transform="translate({x:.1f} {base:.1f}) scale({facing} 1)"'
    paths = "".join(f'<path d="{smooth_closed(q)}"/>' for q in shapes)
    out = []
    if rim:
        rw = rim_w or max(0.8, H / 7.5 * 0.1)
        out.append(f'<g {tr}><g fill="{rim}" transform="translate({rim_side * facing * rw:.2f} {-rw * 0.5:.2f})">{paths}</g></g>')
    out.append(f'<g {tr} opacity="{op}"><g fill="{col}">{paths}</g></g>')
    return "".join(out), joints


# ---------------------------------------------------------------- the peacock (Pavo cristatus), displaying
def _rotp(x, y, cx, cy, a):
    c, s = math.cos(a), math.sin(a)
    return (cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c)


def peacock_eye(cx, cy, L, W, ang, seed, light=1.0):
    """One ocellus, long axis along the feather shaft (ang, radians, pointing to the tip).  Rings from outside in:
    a fringe of loose golden-bronze barbs, olive-gold, copper-bronze, turquoise, and the deep blue-violet heart
    (notched toward the tip), with a wet highlight."""
    rnd = random.Random(seed)
    out = []
    a = math.degrees(ang)
    g = f'transform="rotate({a:.1f} {cx:.1f} {cy:.1f})"'
    rings = [(1.0, 1.0, "#8E9A36", 0.0), (0.8, 0.82, "#3E7A2E", 0.03), (0.64, 0.66, "#9A5E26", 0.07), (0.5, 0.54, "#22A2B4", 0.1)]
    for k, (fl, fw, col, off) in enumerate(rings):
        out.append(f'<path d="{blob(cx + L * off, cy, L * fl / 2, W * fw / 2, seed + k, 0.05, 14)}" fill="{col}"/>')
    # heart: a rounded shape with a notch on the tip side
    hx = cx + L * 0.12
    hl, hw = L * 0.36, W * 0.4
    heart = [(hx - hl / 2, cy), (hx - hl * 0.3, cy - hw * 0.45), (hx + hl * 0.15, cy - hw * 0.5), (hx + hl * 0.45, cy - hw * 0.28),
             (hx + hl * 0.3, cy), (hx + hl * 0.45, cy + hw * 0.28), (hx + hl * 0.15, cy + hw * 0.5), (hx - hl * 0.3, cy + hw * 0.45)]
    out.append(f'<path d="{smooth_closed(heart)}" fill="#142060"/>')
    out.append(f'<path d="{blob(hx - hl * 0.05, cy - hw * 0.1, hl * 0.28, hw * 0.25, seed + 9, 0.1, 10)}" fill="#2A3A9A" opacity="0.7"/>')
    out.append(f'<path d="{blob(hx - hl * 0.18, cy - hw * 0.18, hl * 0.1, hw * 0.1, seed + 8, 0.1, 8)}" fill="#C8F0FF" opacity="{0.55 * light:.2f}"/>')
    return f'<g {g}>' + "".join(out) + "</g>"


def peacock_train(D, cx, cy, R, seed, a0=-188, a1=8, rows=5, squash=1.0, light=(-0.6, -0.8)):
    """The displayed train: hundreds of loose barbs radiating from the rump, eyes in staggered rows, the shortest
    feathers in front.  Returns (svg, fan outline points)."""
    rnd = random.Random(seed)
    out = []

    def P(a, r):
        return (cx + math.cos(math.radians(a)) * r, cy + math.sin(math.radians(a)) * r * squash)
    # outline: scalloped by the outermost eyes, with fishtail feathers at the two ends
    outline = []
    for i in range(80):
        a = a0 + (a1 - a0) * i / 79
        rr = R * (1 + 0.025 * math.sin(i * 1.7)) * (0.92 + 0.08 * math.sin(math.pi * i / 79))
        outline.append(P(a, rr))
    outline += [P(a1 + 4, R * 0.15), P(-90, -R * 0.06), P(a0 - 4, R * 0.15)]
    d = smooth_closed(outline)
    # body of the train: radial gradient, deep bronze-green at the root to brighter green-gold at the rim
    g = D.rad([(0, "#0A2418"), (0.45, "#14422A"), (0.8, "#2E6A2E"), (1, "#6A8A2A")], 0.5, 1.0, 1.0)
    out.append(f'<path d="{d}" fill="#1A4A2A"/><path d="{d}" fill="{g}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    # loose barbs: long thin radial strokes in greens, bronze and gold
    cols = ["#2E7A3A", "#4A9A3A", "#8AAA3A", "#C8B24A", "#1E5A3A", "#6AB04A", "#A88A2A"]
    for _ in range(int(R * 3.6)):
        a = rnd.uniform(a0 - 2, a1 + 2)
        r0 = rnd.uniform(0.12, 1.0) * R
        L = rnd.uniform(0.05, 0.16) * R
        p0, p1 = P(a, r0), P(a + rnd.uniform(-1.5, 1.5), r0 + L)
        inner.append(f'<path d="M {p0[0]:.1f} {p0[1]:.1f} L {p1[0]:.1f} {p1[1]:.1f}" stroke="{rnd.choice(cols)}" '
                     f'stroke-width="{rnd.uniform(0.6, 1.6):.1f}" opacity="{rnd.uniform(0.35, 0.85):.2f}" stroke-linecap="round"/>')
    # rows of feathers: shafts and eyes; outer (back) rows first
    radii = [0.91, 0.76, 0.61, 0.47, 0.34][:rows]
    for row, rf in enumerate(radii):
        n = int(10 + rf * 24)
        size = R * (0.07 + rf * 0.035)
        for i in range(n):
            t = (i + (0.5 if row % 2 else 0.0) + rnd.uniform(-0.15, 0.15)) / (n - (0.5 if row % 2 else 1.0))
            a = a0 + 4 + (a1 - a0 - 8) * t
            r = rf * R * rnd.uniform(0.97, 1.03)
            ex, ey = P(a, r)
            ang = math.atan2((ey - cy) / squash if squash else ey - cy, ex - cx)
            # the shaft, pale, from root toward the eye
            s0 = P(a, r * 0.2)
            inner.append(f'<path d="M {s0[0]:.1f} {s0[1]:.1f} L {ex:.1f} {ey:.1f}" stroke="#D8D49A" stroke-width="{max(0.6, size * 0.035):.2f}" opacity="0.45"/>')
            # loose barbs fringing the eye (fan out from the shaft)
            for k in range(8):
                ba = ang + rnd.uniform(-1.0, 1.0)
                bl = size * rnd.uniform(0.7, 1.3)
                q0 = (ex - math.cos(ang) * size * 0.15, ey - math.sin(ang) * size * 0.15)
                inner.append(f'<path d="M {q0[0]:.1f} {q0[1]:.1f} l {math.cos(ba) * bl:.1f} {math.sin(ba) * bl:.1f}" stroke="{rnd.choice(["#9AB040", "#C8B84A", "#5A9A3A"])}" '
                             f'stroke-width="0.9" opacity="0.6"/>')
            # lit side of the fan is a little brighter
            lit = 0.7 + 0.3 * max(0, -(math.cos(ang) * light[0] + math.sin(ang) * light[1]))
            inner.append(peacock_eye(ex, ey, size * 1.3, size * 1.0, ang, seed + row * 100 + i, lit))
    # sheen and shade: light from the upper left, the root in shadow behind the body
    gl = D.lin([(0, "#FFF6C0", 0.22), (0.5, "#FFF6C0", 0), (1, "#0A1A10", 0.3)], cx - R, cy - R, cx + R, cy, "userSpaceOnUse")
    inner.append(f'<rect x="{cx - R - 10:.1f}" y="{cy - R - 10:.1f}" width="{2 * R + 20:.1f}" height="{R * 1.3 + 20:.1f}" fill="{gl}"/>')
    gr = D.rad([(0, "#06140C", 0.75), (0.35, "#06140C", 0.25), (1, "#06140C", 0)], cx, cy, R * 0.55, None, None, "userSpaceOnUse")
    inner.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R * 0.55:.1f}" fill="{gr}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # a wispy fringe of loose barbs breaking the outer edge, catching the light
    fr = []
    for _ in range(int(R * 1.1)):
        a = rnd.uniform(a0 + 2, a1 - 2)
        r0 = R * rnd.uniform(0.86, 0.97)
        L = R * rnd.uniform(0.04, 0.1)
        p0, p1 = P(a, r0), P(a + rnd.uniform(-2, 2), r0 + L)
        fr.append(f'<path d="M {p0[0]:.1f} {p0[1]:.1f} L {p1[0]:.1f} {p1[1]:.1f}" stroke="{rnd.choice(["#8AA040", "#B8B04A", "#5A8A3A", "#D8C860"])}" stroke-width="{rnd.uniform(0.6, 1.2):.1f}" opacity="{rnd.uniform(0.4, 0.8):.2f}"/>')
    out.append("".join(fr))
    return "".join(out), outline


def peacock_body(D, bx, by, k, seed, light=(-0.7, -0.6)):
    """The bird in front of its train, head turned to profile (facing left).  bx, by = between the feet on the
    ground; k = px per cm.  Drooped wings with chestnut primaries, a teardrop of iridescent blue breast running
    up into a slim S-curved neck, small head with white face bars and the fan crest."""
    rnd = random.Random(seed)

    def P(x, y):
        if y < -20:
            y += 5.0                     # a lower-slung body: the legs mostly hidden by the drooped wings
        return (bx + x * k, by + y * k)

    def PH(x, y, cxh=-2.6, cyh=-99.5, sc=1.25):   # the head drawn a touch larger for legibility at 2 inches
        return P(cxh + (x - cxh) * sc, cyh + (y - cyh) * sc)

    def PL(pts):
        return [P(x, y) for x, y in pts]
    out = []
    # shadow of the bird on the wet grass
    out.append(f'<path d="{blob(bx + 6 * k, by + 1.2 * k, 22 * k, 3 * k, seed, 0.1, 14)}" fill="#0E2010" opacity="0.4"/>')
    # legs and feet: long grey-brown tarsi, toes spread, a spur
    for sx in (-1, 1):
        hip = P(sx * 4.0, -24)
        ank = P(sx * 5.5, -1.5)
        out.append(taper([hip, P(sx * 4.8, -14), ank], 2.4 * k, 1.5 * k, "#8A7A66"))
        out.append(taper([P(sx * 4.4 - 0.5, -25), P(sx * 5.3 - 0.5, -4)], 0.6 * k, 0.4 * k, "#C8BAA4", 0.75))
        out.append(taper([P(sx * 5.0, -9), P(sx * 7.0, -9.8)], 0.8 * k, 0.25 * k, "#5A4A3A"))
        for ta in (-25, 0, 25):
            tip = P(sx * 5.5 + math.sin(math.radians(ta)) * 6 + sx * 1.0, -1.5 + 2.0)
            tip = (tip[0], tip[1] + abs(ta) * 0.02 * k)
            out.append(taper([ank, tip], 1.2 * k, 0.5 * k, "#6E5E4C"))
    # drooped wings: barred coverts above, chestnut primaries fanned down and out
    for sx in (-1, 1):
        for j in range(8):
            t = j / 7
            spread = 1.15 if sx < 0 else 0.95
            top = P(sx * (8 + t * 4), -46 + t * 3)
            bot = P(sx * (11 + t * 13) * spread, (-12 + t * 4) * (0.82 if sx < 0 else 1.0) + rnd.uniform(-1, 1))
            ax_, ay_ = bot[0] - top[0], bot[1] - top[1]
            L = math.hypot(ax_, ay_)
            nx, ny = -ay_ / L, ax_ / L
            w = 3.0 * k
            fp = [top, (top[0] + nx * w * 0.5, top[1] + ny * w * 0.5), (bot[0] + nx * w * 0.3, bot[1] + ny * w * 0.3), bot,
                  (bot[0] - nx * w * 0.3, bot[1] - ny * w * 0.3), (top[0] - nx * w * 0.5, top[1] - ny * w * 0.5)]
            out.append(modelled(D, fp, ("#F0A060", "#BC6428", "#5A2A10"), rnd.randint(0, 9999), light=light, angle=math.degrees(math.atan2(ay_, ax_)),
                                n=7, inkw=0.8, hi=0.3, core=0.3))
        cov = PL([(sx * 6, -58), (sx * 11, -57), (sx * 15.5, -48), (sx * 16.5, -36), (sx * 13, -31), (sx * 8, -38)])
        out.append(modelled(D, cov, ("#E8DCB8", "#A89470", "#3A3020"), seed + 3 + sx, light=light, angle=90, n=12, inkw=0.9, hi=0.25, core=0.4))
        cid = D.clip(f'<path d="{smooth_closed(cov)}"/>')
        sc_ = []
        for j in range(9):
            for i in range(5):
                x = sx * (6 + i * 2.4 + (1.2 if j % 2 else 0))
                y = -58 + j * 3.2
                p = P(x, y)
                sc_.append(f'<path d="M {p[0] - 1.3 * k:.1f} {p[1]:.1f} q {1.3 * k:.1f} {1.6 * k:.1f} {2.6 * k:.1f} 0" stroke="#1E1810" stroke-width="{0.55 * k:.2f}" fill="none" opacity="0.75"/>')
                sc_.append(f'<path d="M {p[0] - 0.9 * k:.1f} {p[1] + 0.9 * k:.1f} q {0.9 * k:.1f} {0.9 * k:.1f} {1.8 * k:.1f} 0" stroke="#4A3E2A" stroke-width="{0.35 * k:.2f}" fill="none" opacity="0.6"/>')
        out.append(f'<g {cid}>{"".join(sc_)}</g>')
    # belly between the wings (bronze-black), feathered thighs
    belly = PL([(-7, -42), (-7.5, -34), (-5, -29), (0, -27.5), (5, -29), (7.5, -34), (7, -42)])
    out.append(modelled(D, belly, ("#3E4E40", "#1A2420", "#060A08"), seed + 5, light=light, angle=90, n=12, inkw=0.8, hi=0.2))
    # breast and neck as one teardrop: broad breast, slim S-neck, turning into the head
    cl = [(-1.4, -96.5), (0.2, -91), (1.0, -85), (0.4, -78), (-0.2, -71), (0.4, -64), (0.6, -57), (0.3, -50), (0.0, -43), (0.0, -37)]
    wd = [4.4, 4.3, 4.3, 4.8, 6.0, 8.6, 13.0, 16.5, 18.0, 13.5]
    left, right = [], []
    for i, ((x, y), w) in enumerate(zip(cl, wd)):
        left.append((x - w / 2, y))
        right.append((x + w / 2, y))
    neck = PL([(-1.6, -98.2)] + left + [(0, -34.5)] + right[::-1])
    out.append(modelled(D, neck, ("#64AAFF", "#1C4CD0", "#0A1660"), seed + 6, light=light, angle=-95, n=70, inkw=1.0, hi=0.6, core=0.5,
                        cols=["#7AC0FF", "#2A60E0", "#0E2A9A", "#3AC8E8"], refl="#28A6A0", sop=(0.15, 0.45)))
    cid = D.clip(f'<path d="{smooth_closed(neck)}"/>')
    sc = []
    for _ in range(180):
        x, y = rnd.uniform(-12, 12), rnd.uniform(-92, -38)
        p = P(x, y)
        sc.append(f'<path d="M {p[0] - 1.2 * k:.1f} {p[1]:.1f} q {1.2 * k:.1f} {0.9 * k:.1f} {2.4 * k:.1f} 0" stroke="{rnd.choice(["#9AE0FF", "#3A7AF0", "#0A1A6A", "#3ACAB8"])}" '
                  f'stroke-width="{0.3 * k:.2f}" fill="none" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    g = D.lin([(0, "#2AB08A", 0), (0.72, "#2AB08A", 0), (1, "#3AC08A", 0.6)], 0, P(0, -97)[1], 0, P(0, -36)[1], "userSpaceOnUse")
    sc.append(f'<rect x="{P(-14, 0)[0]:.1f}" y="{P(0, -98)[1]:.1f}" width="{28 * k:.1f}" height="{64 * k:.1f}" fill="{g}"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    # head in profile, facing left
    head = [PH(*q) for q in [(-3.8, -97.0), (-6.4, -98.4), (-6.6, -100.6), (-4.6, -102.6), (-1.4, -103.0), (1.2, -101.6), (1.6, -99.0), (0.2, -96.6)]]
    out.append(modelled(D, head, ("#78BCFF", "#2050D8", "#0A1660"), seed + 7, light=light, angle=180, n=10, inkw=0.9, hi=0.55))
    bk = [PH(*q) for q in [(-6.2, -100.0), (-10.4, -98.6), (-6.2, -97.4)]]
    out.append(f'<path d="{smooth_closed(bk)}" fill="#C8B8A0"/>' + ink(smooth_closed(bk), INK, 0.8, seed, 1, 0.6))
    out.append(taper([PH(-6.2, -98.7), PH(-10.0, -98.6)], 0.25 * k, 0.1 * k, "#5A4A3A", 0.8))
    out.append(taper([PH(-5.6, -100.9), PH(-3.4, -101.8), PH(0.4, -101.2)], 0.9 * k, 0.45 * k, "#FFFFFF", 0.95))
    out.append(taper([PH(-5.4, -98.6), PH(-3.2, -98.0), PH(-0.6, -98.8)], 0.95 * k, 0.55 * k, "#FFFFFF", 0.95))
    e = PH(-3.6, -99.9)
    out.append(f'<circle cx="{e[0]:.1f}" cy="{e[1]:.1f}" r="{0.75 * k:.1f}" fill="#1A120C"/><circle cx="{e[0] - 0.25 * k:.1f}" cy="{e[1] - 0.25 * k:.1f}" r="{0.22 * k:.1f}" fill="#FFFFFF"/>')
    base = PH(-1.0, -102.6)
    for j in range(21):
        a = math.radians(-122 + j * 4.6 + rnd.uniform(-1.5, 1.5))
        L = (10.5 + 1.8 * math.sin(j / 20 * math.pi)) * k
        tip = (base[0] + math.cos(a) * L, base[1] + math.sin(a) * L)
        out.append(f'<path d="M {base[0]:.1f} {base[1]:.1f} L {tip[0]:.1f} {tip[1]:.1f}" stroke="#2A2E3A" stroke-width="{0.22 * k:.2f}" opacity="0.85"/>')
        out.append(f'<path d="{blob(tip[0], tip[1], 0.95 * k, 0.6 * k, seed + j, 0.15, 8, math.degrees(a))}" fill="{rnd.choice(["#1E60C8", "#2A8AC8", "#1E4AA0", "#2AA0A0"])}"/>')
    return "".join(out)


def storm_cloud(D, cx, cy, w, h, seed, dark="#262E48", mid="#3E4866", lit="#C8B890", rim="#E8D49A", light=(-0.8, 0.6)):
    """A heavy monsoon cloud bank: a cluster of rounded masses painted dark, with broken mid-tone strokes,
    undersides warmed by the low light and a few gold-lit lips (the miniature painters' cloud edge)."""
    rnd = random.Random(seed)
    puffs = []
    for i in range(14):
        t = rnd.random()
        x = cx - w / 2 + w * t
        y = cy + rnd.uniform(-h * 0.3, h * 0.25) - math.sin(math.pi * t) * h * 0.25
        r = rnd.uniform(0.16, 0.26) * w * (0.7 + 0.3 * math.sin(math.pi * t))
        puffs.append((x, y, r))
    shapes = " ".join(blob(x, y, r, r * 0.78, rnd.randint(0, 9999), 0.07, 16) for x, y, r in puffs)
    out = [f'<path d="{shapes}" fill="{dark}"/>']
    cid = D.clip(f'<path d="{shapes}"/>')
    inner = [strokes(D.nid(), f"M {cx - w} {cy - h} L {cx + w} {cy - h} L {cx + w} {cy + h} L {cx - w} {cy + h} Z", (cx - w * 0.7, cy - h, cx + w * 0.7, cy + h),
                     [mid, dark, "#4E5878", "#1A2036"], seed, n=int(w * h / 120), angle=-12, length=(20, 60), width=(3, 9), opacity=(0.2, 0.55), curve=0.4)]
    for x, y, r in sorted(puffs, key=lambda q: q[1]):
        inner.append(f'<path d="{blob(x - r * 0.1, y - r * 0.25, r * 0.8, r * 0.55, rnd.randint(0, 9999), 0.1, 12)}" fill="{mid}" opacity="0.5"/>')
        lip = [(x - r * 0.95, y + r * 0.05), (x - r * 0.55, y + r * 0.62), (x + r * 0.2, y + r * 0.74), (x + r * 0.7, y + r * 0.45)]
        inner.append(taper(lip, r * 0.04, r * 0.14, lit, 0.16))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    for x, y, r in puffs:
        if rnd.random() < 0.3:
            lip = [(x - r * 0.9, y + r * 0.25), (x - r * 0.45, y + r * 0.72), (x + r * 0.25, y + r * 0.76)]
            out.append(f'<path d="{smooth_open(lip)}" fill="none" stroke="{rim}" stroke-width="{max(1.0, r * 0.025):.1f}" opacity="0.4" stroke-linecap="round"/>')
    return "".join(out)


def sky_brush(D, seed, bands, angle=-8, box=(-40, -40, 640, 640)):
    """An oil-sketch sky: passes of broad, curved brush strokes.  bands = [(y0, y1, colours, n, (wmin, wmax),
    (lmin, lmax), (omin, omax))], painted in order (dark masses first, light last)."""
    rnd = random.Random(seed)
    out = []
    x0, _, x1, _ = box
    for k, (ya, yb, cols, n, wr, lr, opr) in enumerate(bands):
        d = f"M {x0} {ya} L {x1} {ya} L {x1} {yb} L {x0} {yb} Z"
        out.append(strokes(D.nid(), d, (x0 - 60, ya, x1, yb), cols, seed + k * 7, n=n, angle=angle, length=lr, width=wr, opacity=opr, curve=0.35))
    return "".join(out)


# ---------------------------------------------------------------- three-wheeler (auto-rickshaw) in true perspective
def _face_light(cam, pts3, light):
    """Lambert-ish brightness 0..1 of a planar face (pts3 in order) for a directional light (unit vector)."""
    a, b, c = pts3[0], pts3[1], pts3[2]
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    L = math.sqrt(sum(q * q for q in n)) or 1
    n = [q / L for q in n]
    to_cam = [cam.pos[i] - a[i] for i in range(3)]
    if sum(n[i] * to_cam[i] for i in range(3)) < 0:
        n = [-q for q in n]
    return max(0.0, sum(n[i] * light[i] for i in range(3)))


def wheel3(D, cam, c, r, axis, seed, tire="#1A1A1E", rim="#C8CCD2", hub="#6E747C", w=12, light=(-0.5, 0.6, 0.6)):
    """A wheel (centre c, radius r) whose axle runs along `axis` ('y' usually); drawn as two projected tyre
    outlines joined, a rim and hub."""
    def ring(rr, off):
        pts = []
        for i in range(36):
            a = 2 * math.pi * i / 36
            if axis == "y":
                p = (c[0] + math.cos(a) * rr, c[1] + off, c[2] + math.sin(a) * rr)
            else:
                p = (c[0] + off, c[1] + math.cos(a) * rr, c[2] + math.sin(a) * rr)
            pts.append(cam(p))
        return pts
    outer_o, outer_i = ring(r, w / 2), ring(r, -w / 2)
    hull = outer_o + outer_i
    # the tread: convex hull of both outlines
    hp = _hull(hull)
    out = [f'<path d="{smooth_closed(hp)}" fill="{mix(tire, "#000000", 0.3)}"/>']
    out.append(f'<path d="{smooth_closed(outer_o)}" fill="{tire}"/>')
    out.append(f'<path d="{smooth_closed(ring(r * 0.98, w / 2 + 0.1))}" fill="none" stroke="#4A4A50" stroke-width="1.6" opacity="0.7"/>')
    rimp = ring(r * 0.6, w / 2 + 0.5)
    out.append(f'<path d="{smooth_closed(rimp)}" fill="{rim}"/>')
    g = D.lin([(0, "#FFFFFF", 0.8), (0.5, rim, 0), (1, "#3A3E44", 0.6)])
    out.append(f'<path d="{smooth_closed(rimp)}" fill="{g}"/>')
    out.append(f'<path d="{smooth_closed(ring(r * 0.42, w / 2 + 0.8))}" fill="{hub}"/>')
    hc = ring(r * 0.16, w / 2 + 1.5)
    out.append(f'<path d="{smooth_closed(hc)}" fill="#2A2A2E"/>')
    for i in range(5):
        a = 2 * math.pi * i / 5 + 0.3
        if axis == "y":
            p = cam((c[0] + math.cos(a) * r * 0.3, c[1] + w / 2 + 1, c[2] + math.sin(a) * r * 0.3))
        else:
            p = cam((c[0] + w / 2 + 1, c[1] + math.cos(a) * r * 0.3, c[2] + math.sin(a) * r * 0.3))
        out.append(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="1.3" fill="#E8ECF0"/>')
    return "".join(out)


def _hull(pts):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def poly3(cam, pts3):
    return [cam(p) for p in pts3]


def dens3(pts3, step=8.0, closed=True):
    """Insert points along 3D polyline edges so projected outlines curve correctly."""
    out = []
    n = len(pts3)
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        a, b = pts3[i], pts3[(i + 1) % n]
        L = math.sqrt(sum((b[k] - a[k]) ** 2 for k in range(3)))
        m = max(1, int(L / step))
        for j in range(m):
            t = j / m
            out.append(tuple(a[k] + (b[k] - a[k]) * t for k in range(3)))
    if not closed:
        out.append(pts3[-1])
    return out


def pdl(pts):
    """Straight-edged path (keeps hard corners of manufactured parts)."""
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def _interp(prof, x):
    for (x1, z1), (x2, z2) in zip(prof, prof[1:]):
        if min(x1, x2) <= x <= max(x1, x2):
            t = (x - x1) / (x2 - x1) if x2 != x1 else 0
            return z1 + (z2 - z1) * t
    return prof[0][1] if x > prof[0][0] else prof[-1][1]


def auto_rickshaw(D, cam, seed, light=(0.35, 0.75, 0.55), body=("#2E323C", "#15171C", "#050608"),
                  canopy=("#FFEA8A", "#F6BE1A", "#A86A06"), sky_ref="#C8DCEA"):
    """A three-wheeler in true perspective (cm; x forward, y to the vehicle's left, z up; ground z = 0).
    Returns svg.  Painted as faces lit by `light` (unit vector toward the light)."""
    rnd = random.Random(seed)
    P = cam
    out = []

    def face(pts3, pal, sd, n=None, angle=None, inkw=1.2, extra="", tex=True, op=1.0, curve=0.25, grad=True):
        pts = poly3(cam, dens3(pts3, 10))
        b = 0.18 + 0.82 * _face_light(cam, pts3, light)
        col = mix(pal[2], pal[1], b / 0.55) if b < 0.55 else mix(pal[1], pal[0], min(1, (b - 0.55) / 0.45))
        d = smooth_closed(pts)
        o = [f'<path d="{d}" fill="{col}" opacity="{op}"{extra}/>']
        x0, y0, x1, y1 = bbox(pts)
        if grad:
            g = D.lin([(0, pal[0], 0.35), (0.45, col, 0), (1, pal[2], 0.45)], x0, y0, x1, y1, "userSpaceOnUse")
            o.append(f'<path d="{d}" fill="{g}" opacity="{op}"/>')
        if tex:
            ang = angle if angle is not None else -90
            o.append(strokes(D.nid(), d, (x0 - 4, y0 - 4, x1 + 4, y1 + 4), [mix(col, pal[0], 0.45), mix(col, pal[2], 0.4), col, mix(col, "#FFFFFF", 0.25)], sd,
                             n=n or int(max(8, (x1 - x0) * (y1 - y0) / 110)), angle=ang, length=(8, max(12, (x1 - x0) * 0.45)),
                             width=(1, 3.5), opacity=(0.15, 0.42), curve=curve))
        if inkw:
            o.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{inkw}" stroke-linejoin="round" opacity="0.5"/>')
        return "".join(o), d, pts

    # ---- canopy profile (top line along x) and the skirt bottoms
    top = [(97, 156), (88, 167), (40, 173), (-40, 175), (-100, 171), (-124, 160), (-138, 136), (-146, 104), (-148, 80)]
    xs = [97, 92, 80, 60, 40, 20, 0, -20, -40, -60, -80, -96, -100, -106, -112, -124, -132, -138, -143, -146, -148]

    def zt(x):
        return _interp(top, x)

    def zb(x):          # skirt bottom: a short valance over the open sides, down to the body behind the passenger
        if x > -96:
            return 147
        if x > -112:
            return 147 - (x + 96) / -16 * 70
        return 77
    HW = 66
    # ---- 1. far rear wheel
    out.append(wheel3(D, cam, (-92, -60, 23), 23, "y", seed + 1, w=13))
    # ---- 2. interior seen through the open side: far opening (street light), cabin gloom, seats, driver
    far_open = [(85, -64, 78), (85, -64, 146), (-96, -64, 146), (-96, -64, 78)]
    out.append(f'<path d="{smooth_closed(poly3(cam, dens3(far_open, 10)))}" fill="#E8C890"/>')
    cab = [(-100, 64, 76), (-100, -64, 76), (-100, -64, 165), (-100, 64, 165)]
    out.append(f'<path d="{smooth_closed(poly3(cam, dens3(cab, 10)))}" fill="#2A2018"/>')
    # canopy underside
    under = [(94, 64, 150), (94, -64, 150), (-100, -64, 165), (-100, 64, 165)]
    out.append(f'<path d="{smooth_closed(poly3(cam, dens3(under, 10)))}" fill="#3A2A14"/>')
    # rear bench: back rest and cushion (maroon rexine)
    seat = ("#9A3A36", "#6A1A1C", "#2A0808")
    s1, _, _ = face([(-92, 58, 72), (-92, -58, 72), (-98, -58, 130), (-98, 58, 130)], seat, seed + 3, angle=-90)
    s2, _, _ = face([(-92, 58, 72), (-52, 58, 70), (-52, -58, 70), (-92, -58, 72)], seat, seed + 4, angle=0)
    s3, _, _ = face([(-52, 58, 70), (-52, -58, 70), (-50, -58, 56), (-50, 58, 56)], seat, seed + 5, angle=0)
    out += [s1, s2, s3]
    # driver's seat and the handlebar
    ds, _, _ = face([(28, 22, 82), (52, 22, 82), (52, -22, 82), (28, -22, 82)], seat, seed + 6)
    out.append(ds)
    db, _, _ = face([(26, 20, 82), (26, -20, 82), (24, -20, 112), (24, 20, 112)], seat, seed + 7)
    out.append(db)
    hb = poly3(cam, [(72, 34, 104), (78, 18, 108), (80, 0, 108), (78, -18, 108), (72, -34, 104)])
    out.append(f'<path d="{smooth_open(hb)}" fill="none" stroke="#1A1A1E" stroke-width="4" stroke-linecap="round"/>')
    for yy in (34, -34):
        g0, g1 = P((72, yy, 104)), P((66, yy * 1.15, 103))
        out.append(f'<path d="M {g0[0]:.1f} {g0[1]:.1f} L {g1[0]:.1f} {g1[1]:.1f}" stroke="#2A2A2A" stroke-width="7" stroke-linecap="round"/>')
    # floor seen at the doorway
    fl, _, _ = face([(85, 64, 40), (-50, 64, 40), (-50, -64, 40), (85, -64, 40)], ("#5A5048", "#2A2420", "#100C0A"), seed + 8, inkw=0)
    out.append(fl)
    # ---- 3. near-side body: lower panel with the wheel arch, rear enclosure
    arch = [(-92 + math.cos(math.radians(a)) * 30, 62, 26 + math.sin(math.radians(a)) * 30) for a in range(0, 181, 15)]
    lower = [(60, 62, 30), (60, 62, 78), (-50, 62, 80), (-146, 62, 80), (-150, 62, 60), (-146, 62, 30)] + [(x, y, z) for x, y, z in arch[::-1]][::-1]
    lower = [(60, 62, 30), (60, 62, 78), (-148, 62, 80), (-152, 62, 56), (-146, 62, 30)] + [(-92 - 30, 62, 30)] + \
        [(-92 - math.cos(math.radians(a)) * 30, 62, 26 + math.sin(math.radians(a)) * 30) for a in range(0, 181, 12)] + [(-92 + 30, 62, 30)]
    lp, ld, lpts = face(lower, body, seed + 9, angle=0, n=40)
    out.append(lp)
    # rear enclosure of the canopy, down the near side behind the passenger
    rear_side = [(x, HW, zt(x) - 10) for x in xs if x <= -96] + [(x, HW - 2, zb(x)) for x in xs[::-1] if x <= -96]
    rs, rsd, _ = face(rear_side, canopy, seed + 10, angle=-90, n=30)
    out.append(rs)
    # a little rear-quarter window in the enclosure and the trim line at the belt
    win = [(-116, HW + 0.5, 138), (-130, HW + 0.5, 136), (-134, HW + 0.5, 112), (-116, HW + 0.5, 112)]
    out.append(f'<path d="{smooth_closed(poly3(cam, dens3(win, 6)))}" fill="#2A2420"/>')
    belt = poly3(cam, [(60, 62.5, 78), (-148, 62.5, 80)])
    out.append(f'<path d="M {belt[0][0]:.1f} {belt[0][1]:.1f} L {belt[1][0]:.1f} {belt[1][1]:.1f}" stroke="#F2C21A" stroke-width="3.2"/>')
    # sky reflection running along the black panel
    refl = [(58, 62.6, 70), (-140, 62.6, 72), (-140, 62.6, 62), (58, 62.6, 61)]
    out.append(f'<path d="{smooth_closed(poly3(cam, dens3(refl, 10)))}" fill="{sky_ref}" opacity="0.38"/>')
    refl2 = [(58, 62.6, 74), (-140, 62.6, 76.5), (-140, 62.6, 74.5), (58, 62.6, 72.5)]
    out.append(f'<path d="{smooth_closed(poly3(cam, dens3(refl2, 10)))}" fill="#FFFFFF" opacity="0.5"/>')
    bounce = [(58, 62.6, 40), (-150, 62.6, 40), (-150, 62.6, 30), (58, 62.6, 30)]
    out.append(f'<path d="{smooth_closed(poly3(cam, dens3(bounce, 10)))}" fill="#C89A6A" opacity="0.3"/>')
    # ---- 4. near rear wheel and mudguard shadow
    out.append(wheel3(D, cam, (-92, 64, 23), 23, "y", seed + 11, w=13))
    # ---- 5. front cowl: near side, front face, windscreen
    cowl_side = [(60, 62, 30), (60, 60, 118), (95, 47, 118), (103, 32, 70), (101, 22, 42), (86, 40, 34)]
    cs, csd, _ = face(cowl_side, body, seed + 12, angle=-60, n=30)
    out.append(cs)
    front = [(95, 47, 118), (95, -47, 118), (103, -32, 70), (101, -22, 42), (101, 22, 42), (103, 32, 70)]
    fr, frd, _ = face(front, body, seed + 13, angle=-90, n=30)
    out.append(fr)
    # the yellow band across the top of the nose
    band = [(95, 47, 118), (95, -47, 118), (98.5, -41, 100), (98.5, 41, 100)]
    bnd, _, _ = face(band, canopy, seed + 14, angle=0, n=12)
    out.append(bnd)
    bands = [(60, 61, 118), (95, 47.5, 118), (98.5, 41.5, 100), (60, 61.5, 100)]
    b2, _, _ = face(bands, canopy, seed + 15, angle=0, n=12)
    out.append(b2)
    # headlight with a chrome bezel, indicators
    hc = (103.2, 0, 84)
    ring = [P((hc[0] + 0.3, math.cos(2 * math.pi * i / 24) * 10, hc[2] + math.sin(2 * math.pi * i / 24) * 10)) for i in range(24)]
    out.append(f'<path d="{smooth_closed(ring)}" fill="#D8DCE0"/>')
    ring2 = [P((hc[0] + 0.8, math.cos(2 * math.pi * i / 24) * 7.5, hc[2] + math.sin(2 * math.pi * i / 24) * 7.5)) for i in range(24)]
    out.append(f'<path d="{smooth_closed(ring2)}" fill="#FFF6D0"/>')
    c0 = P((hc[0] + 1, 2, hc[2] + 3))
    out.append(f'<circle cx="{c0[0]:.1f}" cy="{c0[1]:.1f}" r="2.4" fill="#FFFFFF"/>')
    for yy in (30, -30):
        ind = [P((100.5, yy + math.cos(2 * math.pi * i / 12) * 4, 104 + math.sin(2 * math.pi * i / 12) * 3)) for i in range(12)]
        out.append(f'<path d="{smooth_closed(ind)}" fill="#F28A1E"/>')
    # front wheel, mudguard and fork
    out.append(wheel3(D, cam, (114, 0, 22), 22, "y", seed + 16, w=11))
    mg = [(114 + math.cos(math.radians(a)) * 27, 7, 22 + math.sin(math.radians(a)) * 27) for a in range(10, 171, 10)]
    mg2 = [(x, -7, z) for x, y, z in mg[::-1]]
    mgp, _, _ = face(mg + mg2, body, seed + 17, angle=0, n=10, inkw=1)
    out.append(mgp)
    for yy in (8, -8):
        f0, f1 = P((106, yy, 46)), P((114, yy, 22))
        out.append(f'<path d="M {f0[0]:.1f} {f0[1]:.1f} L {f1[0]:.1f} {f1[1]:.1f}" stroke="#8A9098" stroke-width="3.4" stroke-linecap="round"/>')
    # windscreen glass with sky and a streak of light, black frame and pillars
    glass = [(95.5, 45, 119), (95.5, -45, 119), (89, -54, 150), (89, 54, 150)]
    gp = poly3(cam, dens3(glass, 8))
    gg = D.lin([(0, "#E8F0F0", 0.85), (0.4, "#8AA8B8", 0.55), (1, "#3A4A58", 0.75)], 0, 0, 0, 1)
    out.append(f'<path d="{smooth_closed(gp)}" fill="{gg}"/>')
    s0, s1_ = P((93, 30, 124)), P((90, 10, 146))
    out.append(f'<path d="M {s0[0]:.1f} {s0[1]:.1f} L {s1_[0]:.1f} {s1_[1]:.1f}" stroke="#FFFFFF" stroke-width="5" opacity="0.45" stroke-linecap="round"/>')
    for yy in (1, -1):
        p0, p1 = P((95.5, yy * 46, 118)), P((89, yy * 56, 152))
        out.append(f'<path d="M {p0[0]:.1f} {p0[1]:.1f} L {p1[0]:.1f} {p1[1]:.1f}" stroke="#141418" stroke-width="4" stroke-linecap="round"/>')
    tb0, tb1 = P((89, 56, 150)), P((89, -56, 150))
    out.append(f'<path d="M {tb0[0]:.1f} {tb0[1]:.1f} L {tb1[0]:.1f} {tb1[1]:.1f}" stroke="#141418" stroke-width="3"/>')
    # ---- 6. canopy: near valance, top, front lip
    sk = [(x, HW, zt(x) - 10) for x in xs if x >= -100] + [(x, HW, zb(x)) for x in xs[::-1] if x >= -100]
    skp, _, _ = face(sk, canopy, seed + 18, angle=0, n=30)
    out.append(skp)
    xt = [x for x in xs if x >= -126]
    topf = [(x, HW - 6, zt(x)) for x in xt] + [(x, -(HW - 6), zt(x)) for x in xt[::-1]]
    tpp, tpd, tpts = face(topf, canopy, seed + 19, angle=-4, n=60, curve=0.1)
    out.append(tpp)
    shoulder = [(x, HW - 6, zt(x)) for x in xs] + [(x, HW, zt(x) - 10) for x in xs[::-1]]
    shp, _, _ = face(shoulder, canopy, seed + 20, angle=0, n=30)
    out.append(shp)
    lip = [(97, HW, 147), (97, -HW, 147), (97, -(HW - 6), 157), (97, HW - 6, 157)]
    lpp, _, _ = face(lip, canopy, seed + 21, angle=0, n=10)
    out.append(lpp)
    # canvas seams on the hood, a sun-bleached highlight
    for x in (40, -10, -60, -105):
        sm = poly3(cam, [(x, HW, zt(x) - 10), (x, HW - 6, zt(x)), (x, 0, zt(x) + 0.5), (x, -(HW - 6), zt(x))])
        out.append(f'<path d="{smooth_open(sm)}" fill="none" stroke="{canopy[2]}" stroke-width="1.4" opacity="0.5"/>')
    hl = poly3(cam, [(80, 30, zt(80) + 0.6), (-90, 30, zt(-90) + 0.6)])
    out.append(f'<path d="M {hl[0][0]:.1f} {hl[0][1]:.1f} L {hl[1][0]:.1f} {hl[1][1]:.1f}" stroke="#FFF6C8" stroke-width="6" opacity="0.35" stroke-linecap="round"/>')
    # mirror on its stalk
    m0, m1 = P((94, 50, 128)), P((98, 72, 140))
    out.append(f'<path d="M {m0[0]:.1f} {m0[1]:.1f} L {m1[0]:.1f} {m1[1]:.1f}" stroke="#2A2A2E" stroke-width="2.2"/>')
    mr = [P((98, 72 + math.cos(2 * math.pi * i / 14) * 6, 144 + math.sin(2 * math.pi * i / 14) * 5)) for i in range(14)]
    out.append(f'<path d="{smooth_closed(mr)}" fill="#C8D8E0" stroke="#1A1A1E" stroke-width="1.6"/>')
    return "".join(out), {"top": tpd, "lower": ld}


def dens2(pts, step=8.0):
    """Densify a closed 2D polygon with points along straight edges (keeps corners crisp under smooth_closed)."""
    out = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        m = max(2, int(L / step))
        for j in range(m):
            t = j / m
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


# ---------------------------------------------------------------- the Taj Mahal, front elevation, in metres
def _onion(cx, z0, w0, wmax, zmax_at, ztip, n=28):
    """Onion dome profile (metres): from the drum width w0 at z0 swelling to wmax at zmax_at, closing in an
    ogee to the tip at ztip.  Returns the closed outline (x, z)."""
    right = []
    for i in range(n + 1):
        t = i / n
        z = z0 + (ztip - z0) * t
        if z <= zmax_at:
            u = (z - z0) / (zmax_at - z0)
            r = w0 / 2 + (wmax - w0) / 2 * math.sin(u * math.pi / 2) ** 0.8
        else:
            u = (z - zmax_at) / (ztip - zmax_at)
            r = wmax / 2 * (math.cos(u * math.pi / 2) ** 0.9) * (1 - 0.35 * u ** 2)
            if u > 0.82:
                r *= 0.6 + 0.4 * (1 - u) / 0.18
        right.append((cx + r, z))
    left = [(2 * cx - x, z) for x, z in right[::-1]]
    return right + left[1:]


def _arch(cx, z0, w, h, n=8, a=0.12):
    """Mughal pointed arch opening (x, z): straight jambs, then two circular arcs struck from centres just inside
    the opposite jamb, meeting in a point.  h = total height."""
    R = w * (0.5 + a)
    off = a * w
    rise = math.sqrt(R * R - off * off)
    sp = z0 + max(0.0, h - rise)
    th_apex = math.degrees(math.acos(-off / R))
    left = [(cx + off + R * math.cos(math.radians(180 - (180 - th_apex) * i / n)), sp + R * math.sin(math.radians(180 - (180 - th_apex) * i / n))) for i in range(n + 1)]
    right = [(2 * cx - x, z) for x, z in left[::-1]][1:]
    return [(cx - w / 2, z0)] + left + right + [(cx + w / 2, z0)]


def taj_mahal_painting(D, cx, ground_y, s, seed, haze=0.0, haze_c="#F6E0E0", lit="#FFF2E6", mid="#F0DCD6", shade="#BFAFC8",
                       deep="#8E7EA0", line="#8A7898", light_from=-1):
    """The Taj Mahal in front elevation (truthful massing), painted in dawn light from the left.  s = px per metre."""
    def H(c):
        return mix(c, haze_c, haze) if haze else c
    L_, M_, S_, DP, LN = H(lit), H(mid), H(shade), H(deep), H(line)

    def P(x, z):
        return (cx + x * s, ground_y - z * s)

    def PL(pts):
        return [P(x, z) for x, z in pts]
    out = []
    rnd = random.Random(seed)

    def marble(pts, sd, cyl=False, dense=1.0):
        d = pdl(PL(pts)) if not cyl else smooth_closed(PL(pts))
        x0, y0, x1, y1 = bbox(PL(pts))
        if cyl:
            g = D.lin([(0, L_), (0.35, M_), (0.75, S_), (1, mix(S_, M_, 0.4))], x0, 0, x1, 0, "userSpaceOnUse")
        else:
            g = D.lin([(0, L_), (0.55, M_), (1, mix(M_, S_, 0.35))], x0, y0, x1, y1, "userSpaceOnUse")
        o = [f'<path d="{d}" fill="{g}"/>']
        o.append(strokes(D.nid(), d, (x0 - 2, y0 - 2, x1 + 2, y1 + 2), [L_, S_, "#FFFFFF", M_], sd, n=int(max(4, (x1 - x0) * (y1 - y0) / 120 * dense)),
                         angle=-90 if cyl else -80, length=(4, max(6, (y1 - y0) * 0.4)), width=(0.6, 2.2), opacity=(0.12, 0.35)))
        return "".join(o), d

    def recess(pts, sd, depth_col=None):
        d = smooth_closed(PL(pts))
        x0, y0, x1, y1 = bbox(PL(pts))
        g = D.lin([(0, depth_col or DP), (0.6, S_), (1, mix(S_, "#F2C8A8", 0.3))], x0, y0, x1, y1, "userSpaceOnUse")
        return f'<path d="{d}" fill="{g}"/><path d="{d}" fill="none" stroke="{LN}" stroke-width="{max(0.6, s * 0.18):.2f}" opacity="0.7"/>'

    def frame(x0, z0, x1, z1, w=None):
        w = w or max(0.6, s * 0.14)
        p = PL([(x0, z0), (x1, z0), (x1, z1), (x0, z1)])
        return f'<path d="{pdl(p)}" fill="none" stroke="{LN}" stroke-width="{w:.2f}" opacity="0.6"/>'

    def minaret(mx, base_z, sc, sd):
        o = []
        wb, wt, top = 5.6 * sc, 4.4 * sc, base_z + 40 * sc
        shaft = [(mx - wb / 2, base_z), (mx + wb / 2, base_z), (mx + wt / 2, top), (mx - wt / 2, top)]
        f, _ = marble(shaft, sd, cyl=True, dense=0.6)
        o.append(f)
        for bz in (0.32, 0.62, 0.9):
            z = base_z + 40 * sc * bz
            ww = (wb + (wt - wb) * bz) * 1.45
            bal = [(mx - ww / 2, z - 0.9 * sc), (mx + ww / 2, z - 0.9 * sc), (mx + ww / 2, z + 0.5 * sc), (mx - ww / 2, z + 0.5 * sc)]
            f, _ = marble(bal, sd + int(bz * 10), cyl=True, dense=0.4)
            o.append(f)
            br = PL([(mx - ww * 0.42, z - 0.9 * sc), (mx, z - 2.6 * sc), (mx + ww * 0.42, z - 0.9 * sc)])
            o.append(f'<path d="{smooth_open(br)}" fill="none" stroke="{S_}" stroke-width="{max(0.6, s * 0.4 * sc):.2f}" opacity="0.8"/>')
        # rings of black inlay between storeys
        for bz in (0.16, 0.47, 0.77):
            z = base_z + 40 * sc * bz
            ww = wb + (wt - wb) * bz
            a_, b_ = P(mx - ww / 2, z), P(mx + ww / 2, z)
            o.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="{LN}" stroke-width="{max(0.5, s * 0.12):.2f}" opacity="0.5"/>')
        # the chhatri on top
        cw = wt * 1.5
        plat = [(mx - cw / 2, top), (mx + cw / 2, top), (mx + cw / 2, top + 0.8 * sc), (mx - cw / 2, top + 0.8 * sc)]
        f, _ = marble(plat, sd + 5, cyl=True, dense=0.3)
        o.append(f)
        o.append(recess([(mx - cw * 0.32, top + 0.8 * sc), (mx + cw * 0.32, top + 0.8 * sc), (mx + cw * 0.32, top + 3.4 * sc), (mx - cw * 0.32, top + 3.4 * sc)], sd))
        for px in (-0.42, 0, 0.42):
            col = [(mx + px * cw - 0.25 * sc, top + 0.8 * sc), (mx + px * cw + 0.25 * sc, top + 0.8 * sc), (mx + px * cw + 0.25 * sc, top + 3.6 * sc), (mx + px * cw - 0.25 * sc, top + 3.6 * sc)]
            f, _ = marble(col, sd + 6, dense=0.2)
            o.append(f)
        roof = [(mx - cw * 0.6, top + 3.6 * sc), (mx + cw * 0.6, top + 3.6 * sc), (mx + cw * 0.5, top + 4.3 * sc), (mx - cw * 0.5, top + 4.3 * sc)]
        f, _ = marble(roof, sd + 7, cyl=True, dense=0.3)
        o.append(f)
        dm = _onion(mx, top + 4.3 * sc, cw * 0.62, cw * 0.78, top + 5.6 * sc, top + 8.0 * sc, 16)
        f, _ = marble(dm, sd + 8, cyl=True, dense=0.4)
        o.append(f)
        a_, b_ = P(mx, top + 8.0 * sc), P(mx, top + 9.6 * sc)
        o.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="#C8A050" stroke-width="{max(0.7, s * 0.25):.2f}"/>')
        return "".join(o)

    # rear minarets (farther: a little inward, smaller), then the plinth and front minarets
    out.append(minaret(-36.5, 7.6, 0.86, seed + 1))
    out.append(minaret(36.5, 7.6, 0.86, seed + 2))
    # the drum, the great dome, its lotus and finial
    drum = [(-13.2, 36), (13.2, 36), (13.2, 47.5), (-13.2, 47.5)]
    f, _ = marble(drum, seed + 3, cyl=True)
    out.append(f)
    a_, b_ = P(-13.2, 46.6), P(13.2, 46.6)
    out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="{LN}" stroke-width="{max(0.6, s * 0.2):.2f}" opacity="0.5"/>')
    dome = _onion(0, 47.5, 26.4, 30.2, 55.5, 70.5, 30)
    f, dd = marble(dome, seed + 4, cyl=True, dense=1.4)
    out.append(f)
    # the dome's own light: a warm lit crescent on the left, a cool core shadow, reflected light at the right rim
    cid = D.clip(f'<path d="{dd}"/>')
    x0, y0, x1, y1 = bbox(PL(dome))
    gl = D.lin([(0, "#FFE8D0", 0.75), (0.3, "#FFE8D0", 0.15), (0.62, DP, 0.25), (0.84, DP, 0.12), (1, "#F2C8B8", 0.3)], x0, 0, x1, 0, "userSpaceOnUse")
    out.append(f'<g {cid}><rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{gl}"/></g>')
    out.append(f'<path d="{dd}" fill="none" stroke="{LN}" stroke-width="{max(0.6, s * 0.16):.2f}" opacity="0.45"/>')
    lot = _onion(0, 69.6, 3.2, 4.4, 70.6, 72.0, 10)
    f, _ = marble(lot, seed + 5, cyl=True, dense=0.2)
    out.append(f)
    a_, b_ = P(0, 71.6), P(0, 75.6)
    out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="{H("#D8A848")}" stroke-width="{max(0.9, s * 0.38):.2f}" stroke-linecap="round"/>')
    for zz in (72.6, 73.8):
        c_ = P(0, zz)
        out.append(f'<circle cx="{c_[0]:.1f}" cy="{c_[1]:.1f}" r="{max(0.8, s * 0.42):.2f}" fill="{H("#E8B850")}"/>')
    # the four chhatris on the roof (front pair full, rear pair peeping between them and the drum)
    def chhatri(hx, sc, sd):
        o = []
        w = 7.6 * sc
        z0 = 36.0
        base = [(hx - w / 2, z0), (hx + w / 2, z0), (hx + w / 2, z0 + 1.4 * sc), (hx - w / 2, z0 + 1.4 * sc)]
        f, _ = marble(base, sd, cyl=True, dense=0.3)
        o.append(f)
        o.append(recess([(hx - w * 0.36, z0 + 1.4 * sc), (hx + w * 0.36, z0 + 1.4 * sc), (hx + w * 0.36, z0 + 5.2 * sc), (hx - w * 0.36, z0 + 5.2 * sc)], sd + 1))
        for px in (-0.44, -0.15, 0.15, 0.44):
            col = [(hx + px * w - 0.35 * sc, z0 + 1.4 * sc), (hx + px * w + 0.35 * sc, z0 + 1.4 * sc), (hx + px * w + 0.35 * sc, z0 + 5.4 * sc), (hx + px * w - 0.35 * sc, z0 + 5.4 * sc)]
            f, _ = marble(col, sd + 2, dense=0.2)
            o.append(f)
        eave = [(hx - w * 0.6, z0 + 5.4 * sc), (hx + w * 0.6, z0 + 5.4 * sc), (hx + w * 0.5, z0 + 6.4 * sc), (hx - w * 0.5, z0 + 6.4 * sc)]
        f, _ = marble(eave, sd + 3, cyl=True, dense=0.3)
        o.append(f)
        dm = _onion(hx, z0 + 6.4 * sc, w * 0.58, w * 0.72, z0 + 8.2 * sc, z0 + 11.6 * sc, 16)
        f, _ = marble(dm, sd + 4, cyl=True, dense=0.4)
        o.append(f)
        a_, b_ = P(hx, z0 + 11.6 * sc), P(hx, z0 + 13.4 * sc)
        o.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="{H("#C8A050")}" stroke-width="{max(0.7, s * 0.25):.2f}"/>')
        return "".join(o)
    out.insert(0, chhatri(-11.2, 0.8, seed + 20))
    out.insert(0, chhatri(11.2, 0.8, seed + 21))
    out.append(chhatri(-19.6, 1.0, seed + 22))
    out.append(chhatri(19.6, 1.0, seed + 23))
    # the main hall: chamfered corner bays, side bays, the great pishtaq
    for sg in (-1, 1):
        cb = [(sg * 21.2, 6.7), (sg * 28.4, 6.7), (sg * 28.4, 36.0), (sg * 21.2, 36.0)]
        f, _ = marble(cb, seed + 30 + sg)
        out.append(f)
        if sg < 0:
            out.append(f'<path d="{pdl(PL(cb))}" fill="{S_}" opacity="0.18"/>')
        else:
            out.append(f'<path d="{pdl(PL(cb))}" fill="{S_}" opacity="0.45"/>')
        for z0, z1 in ((8.2, 21.0), (22.4, 34.6)):
            out.append(frame(sg * 21.8 if sg > 0 else -27.8, z0, sg * 27.8 if sg > 0 else -21.8, z1))
            out.append(recess(_arch(sg * 24.8, z0 + 0.6, 4.4, (z1 - z0) - 2.0), seed + 31))
        sb = [(sg * 10.6, 6.7), (sg * 21.2, 6.7), (sg * 21.2, 36.0), (sg * 10.6, 36.0)]
        f, _ = marble(sb, seed + 33 + sg)
        out.append(f)
        for z0, z1 in ((8.2, 21.0), (22.4, 34.6)):
            out.append(frame(sg * 11.4 if sg > 0 else -20.4, z0, sg * 20.4 if sg > 0 else -11.4, z1))
            out.append(recess(_arch(sg * 15.9, z0 + 0.6, 6.6, (z1 - z0) - 2.0), seed + 35))
            # the lattice screen glimpsed inside the lower niche
            if z0 < 10:
                c_ = P(sg * 15.9, z0 + 4.5)
                out.append(f'<rect x="{c_[0] - s * 1.6:.1f}" y="{c_[1] - s * 3:.1f}" width="{s * 3.2:.1f}" height="{s * 4.5:.1f}" fill="{S_}" opacity="0.6"/>')
        # parapet with little merlon pinnacles
        for k in range(6):
            px = sg * (11 + k * 3.2)
            a_ = P(px, 36.0)
            out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} l 0 {-s * 1.3:.1f}" stroke="{M_}" stroke-width="{max(0.8, s * 0.45):.2f}" stroke-linecap="round"/>')
    pq = [(-10.6, 6.7), (10.6, 6.7), (10.6, 40.0), (-10.6, 40.0)]
    f, _ = marble(pq, seed + 40)
    out.append(f)
    out.append(frame(-9.6, 7.4, 9.6, 39.2, max(0.8, s * 0.3)))
    out.append(frame(-8.6, 7.4, 8.6, 38.2, max(0.5, s * 0.12)))
    big = _arch(0, 6.7, 14.4, 27.4, 12)
    out.append(recess(big, seed + 41, depth_col=H("#7A6A90")))
    # inside the great iwan: the doorway arch and the lattice window above
    out.append(recess(_arch(0, 6.7, 5.0, 9.6, 8), seed + 42, depth_col=H("#5A4A6A")))
    c_ = P(0, 21.0)
    out.append(f'<rect x="{c_[0] - s * 2.6:.1f}" y="{c_[1] - s * 3.8:.1f}" width="{s * 5.2:.1f}" height="{s * 6.0:.1f}" fill="{H("#A898B8")}" opacity="0.8"/>')
    for k in range(-2, 3):
        a_, b_ = P(k * 1.0, 17.2), P(k * 1.0, 23.2)
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="{LN}" stroke-width="0.6" opacity="0.6"/>')
    # pishtaq pinnacles (guldastas) and the corner ones
    for px in (-10.6, 10.6, -28.4, 28.4):
        top = 44.0 if abs(px) < 11 else 40.0
        a_, b_ = P(px, 6.7), P(px, top)
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="{M_}" stroke-width="{max(1.0, s * 0.7):.2f}"/>')
        out.append(f'<path d="M {a_[0] + s * 0.25:.1f} {a_[1]:.1f} L {b_[0] + s * 0.25:.1f} {b_[1]:.1f}" stroke="{S_}" stroke-width="{max(0.5, s * 0.25):.2f}" opacity="0.7"/>')
        c_ = P(px, top + 0.8)
        out.append(f'<path d="{blob(c_[0], c_[1], s * 0.6, s * 1.0, seed + int(px), 0.05, 8)}" fill="{M_}"/>')
    # the plinth: a long arcade of blind arches, its edge catching the sun
    pl = [(-47.6, 0), (47.6, 0), (47.6, 6.7), (-47.6, 6.7)]
    f, _ = marble(pl, seed + 50)
    out.append(f)
    for k in range(-11, 12):
        if abs(k) < 2:
            continue
        out.append(recess(_arch(k * 4.0, 0.8, 2.4, 4.6, 6), seed + 51))
    a_, b_ = P(-47.6, 6.7), P(47.6, 6.7)
    out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}" stroke="{L_}" stroke-width="{max(1.0, s * 0.35):.2f}"/>')
    # steps up the front of the plinth
    st = [(-5, 0), (5, 0), (4, 6.7), (-4, 6.7)]
    f, _ = marble(st, seed + 52)
    out.append(f)
    out.append(minaret(-44.6, 6.7, 1.0, seed + 60))
    out.append(minaret(44.6, 6.7, 1.0, seed + 61))
    # a calligraphy band framing the great arch (fine dark brushwork)
    band = PL([(-8.9, 7.4), (-8.9, 38.6), (8.9, 38.6), (8.9, 7.4)])
    out.append(f'<path d="M {band[0][0]:.1f} {band[0][1]:.1f} L {band[1][0]:.1f} {band[1][1]:.1f} L {band[2][0]:.1f} {band[2][1]:.1f} L {band[3][0]:.1f} {band[3][1]:.1f}" fill="none" stroke="{H("#7A6A84")}" stroke-width="{max(0.6, s * 0.5):.2f}" opacity="0.4"/>')
    return "".join(out)


# ---------------------------------------------------------------- coconut palm, backlit
def coco_palm(D, x, base, h, bend, seed, col="#1E2A1E", lit="#C8A050", trunk_c="#3A2E24", n_fronds=13, scale=1.0, rim=0.7):
    """A coconut palm against low sun: a slender curving ringed trunk and a crown of drooping pinnate fronds,
    each a curved rachis with leaflets hanging in V's, catching a rim of gold."""
    rnd = random.Random(seed)
    # trunk: a bent curve
    pts = [(x, base), (x + bend * h * 0.15, base - h * 0.35), (x + bend * h * 0.45, base - h * 0.72), (x + bend * h * 0.62, base - h)]
    cp = []
    for i in range(24):
        t = i / 23
        # cubic bezier
        a, b, c, d = pts
        px = (1 - t) ** 3 * a[0] + 3 * (1 - t) ** 2 * t * b[0] + 3 * (1 - t) * t * t * c[0] + t ** 3 * d[0]
        py = (1 - t) ** 3 * a[1] + 3 * (1 - t) ** 2 * t * b[1] + 3 * (1 - t) * t * t * c[1] + t ** 3 * d[1]
        cp.append((px, py))
    w0, w1 = h * 0.045 * scale, h * 0.028 * scale
    out = [taper(cp, w0, w1, trunk_c)]
    out.append(taper([(px - w0 * 0.25, py) for px, py in cp], w0 * 0.35, w1 * 0.3, lit, 0.35 * rim))
    for i in range(2, 23, 2):
        px, py = cp[i]
        ww = (w0 + (w1 - w0) * i / 23) * 0.5
        out.append(f'<path d="M {px - ww:.1f} {py:.1f} q {ww:.1f} {ww * 0.4:.1f} {ww * 2:.1f} 0" stroke="#1A120C" stroke-width="0.8" fill="none" opacity="0.5"/>')
    top = cp[-1]
    # coconuts
    for k in range(4):
        out.append(f'<circle cx="{top[0] + rnd.uniform(-6, 6) * scale:.1f}" cy="{top[1] + rnd.uniform(3, 9) * scale:.1f}" r="{4.2 * scale:.1f}" fill="#4A4020"/>')
    # fronds
    fr = []
    for k in range(n_fronds):
        a = -180 + 360 * (k + rnd.uniform(-0.3, 0.3)) / n_fronds
        L = h * rnd.uniform(0.32, 0.44) * scale
        if -60 < a < -120:
            L *= 0.8
        ar = math.radians(a)
        droop = 0.55 + 0.35 * max(0, math.sin(ar))
        p1 = (top[0] + math.cos(ar) * L * 0.45, top[1] + math.sin(ar) * L * 0.45 * 0.7 - L * 0.12)
        p2 = (top[0] + math.cos(ar) * L, top[1] + math.sin(ar) * L * 0.5 + L * droop * 0.5)
        fr.append((math.sin(ar), p1, p2, L, k))
    for sn, p1, p2, L, k in sorted(fr):
        rach = []
        for i in range(14):
            t = i / 13
            px = (1 - t) ** 2 * top[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
            py = (1 - t) ** 2 * top[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
            rach.append((px, py))
        o = [taper(rach, 3.0 * scale, 0.8, col)]
        for i in range(1, 14):
            px, py = rach[i]
            qx, qy = rach[i - 1]
            dx, dy = px - qx, py - qy
            dl = math.hypot(dx, dy) or 1
            ux, uy = dx / dl, dy / dl
            ll = L * 0.3 * math.sin(math.pi * (i / 13) ** 0.7) + 4
            for sgn in (-1, 1):
                nx, ny = -uy * sgn, ux * sgn
                tip = (px + nx * ll * 0.45 + ux * ll * 0.3, py + ny * ll * 0.45 + uy * ll * 0.3 + ll * 0.75)
                lw = max(1.2, 3.2 * scale * (1 - 0.5 * i / 13))
                o.append(f'<path d="M {px:.1f} {py:.1f} Q {px + nx * ll * 0.35:.1f} {py + ny * ll * 0.35:.1f} {tip[0]:.1f} {tip[1]:.1f}" stroke="{col}" stroke-width="{lw:.1f}" fill="none" stroke-linecap="round"/>')
                if sgn < 0 and rim and rnd.random() < 0.6:
                    o.append(f'<path d="M {px:.1f} {py:.1f} Q {px + nx * ll * 0.4:.1f} {py + ny * ll * 0.4:.1f} {tip[0]:.1f} {tip[1]:.1f}" stroke="{lit}" stroke-width="0.7" fill="none" opacity="{0.45 * rim:.2f}"/>')
        out.append("".join(o))
    return "".join(out)


# ---------------------------------------------------------------- painted metal (stainless steel / aluminium / brass)
def metal_cyl(D, cx, y_top, y_bot, rx, ry, seed, pal=("#FFFFFF", "#B8C0C8", "#4E5660"), env=("#C8D8E8", "#E8B070"),
              light=-1, bulge=0.0, taper_=0.0, gloss=1.0, inkw=1.3, strokes_n=None):
    """A painted metal cylinder seen from slightly above: body between two ellipses (top at y_top, bottom at
    y_bot), banded with soft light and dark bands like real polished metal, a cool sky reflection on the lit side,
    a warm bounce from below, vertical brush strokes, two crisp highlight streaks and a lost-and-found ink edge.
    rx/ry = top ellipse radii; taper_ narrows the bottom (fraction); bulge swells the lower body."""
    hi, base, dk_ = pal
    rb = rx * (1 - taper_)
    n = 18
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        y = y_top + (y_bot - y_top) * t
        r = rx + (rb - rx) * t + bulge * rx * math.sin(math.pi * t) ** 2 * (t > 0.4)
        left.append((cx - r, y))
        right.append((cx + r, y))
    bottom = [(cx + rb * math.cos(math.radians(a)), y_bot + ry * (rb / rx) * math.sin(math.radians(a))) for a in range(0, 181, 15)]
    outline = [(cx - rx, y_top)] + left[1:] + bottom[::-1][1:-1][::-1] + right[::-1][:-1]
    outline = left + bottom[1:-1][::-1][::-1] + right[::-1]
    pts = left + [p for p in reversed(bottom)][1:-1][::-1]
    # build: down the left side, along the front of the bottom ellipse, up the right side
    body = left + [(cx + rb * math.cos(math.radians(a)), y_bot + ry * (rb / rx) * math.sin(math.radians(a))) for a in range(170, 9, -10)] + right[::-1]
    d = smooth_closed(body)
    x0, x1 = cx - rx * (1 + bulge), cx + rx * (1 + bulge)
    s = -light
    stops = [(0, mix(dk_, base, 0.3)), (0.08, hi), (0.16, mix(hi, env[0], 0.4)), (0.3, base), (0.45, mix(dk_, base, 0.2)), (0.55, base),
             (0.68, mix(base, hi, 0.5)), (0.8, mix(dk_, base, 0.5)), (0.92, dk_), (1, mix(dk_, env[1], 0.4))]
    if light > 0:
        stops = [(1 - o, c) for o, c in stops[::-1]]
    g = D.lin(stops, x0, 0, x1, 0, "userSpaceOnUse")
    out = [f'<path d="{d}" fill="{base}"/>', f'<path d="{d}" fill="{g}"/>']
    cid = D.clip(f'<path d="{d}"/>')
    inner = [strokes(D.nid(), d, (x0, y_top - 4, x1, y_bot + ry + 4), [hi, mix(dk_, base, 0.5), base, env[0]], seed, n=strokes_n or int((x1 - x0) * (y_bot - y_top) / 160),
                     angle=-90, length=((y_bot - y_top) * 0.2, (y_bot - y_top) * 0.7), width=(0.8, 2.2), opacity=(0.06, 0.18), curve=0.02)]
    # warm bounce along the bottom, cool sky in the top band
    gb = D.lin([(0, env[1], 0), (0.75, env[1], 0), (1, env[1], 0.4)], 0, y_top, 0, y_bot + ry, "userSpaceOnUse")
    inner.append(f'<rect x="{x0:.1f}" y="{y_top - ry:.1f}" width="{x1 - x0:.1f}" height="{y_bot - y_top + 2 * ry:.1f}" fill="{gb}"/>')
    # crisp highlight streaks (gloss)
    if gloss:
        hx = cx + light * rx * 0.62
        inner.append(taper([(hx, y_top + (y_bot - y_top) * 0.06), (hx + light * 1.5, y_top + (y_bot - y_top) * 0.5), (hx + light * rx * 0.05, y_bot - (y_bot - y_top) * 0.05)],
                           max(1.5, rx * 0.06), max(0.8, rx * 0.02), "#FFFFFF", 0.85 * gloss))
        hx2 = cx - light * rx * 0.35
        inner.append(taper([(hx2, y_top + (y_bot - y_top) * 0.1), (hx2, y_bot - (y_bot - y_top) * 0.12)], max(1, rx * 0.03), max(0.6, rx * 0.012), "#FFFFFF", 0.45 * gloss))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    if inkw:
        gi = D.lin([(0, INK, 0.25), (0.5, INK, 0.15), (1, INK, 0.85)] if light < 0 else [(0, INK, 0.85), (0.5, INK, 0.15), (1, INK, 0.25)], x0, 0, x1, 0, "userSpaceOnUse")
        out.append(f'<path d="{d}" fill="none" stroke="{gi}" stroke-width="{inkw}"/>')
    return "".join(out), d


def metal_ellipse(D, cx, cy, rx, ry, seed, pal=("#FFFFFF", "#B8C0C8", "#4E5660"), inner_pal=None, rim_w=None, light=-1, inkw=1.2):
    """A rolled metal rim seen from above (the mouth of a pot or tumbler): a bright lip with a dark inner wall."""
    hi, base, dk_ = pal
    rw = rim_w or max(2.0, rx * 0.06)
    out = [f'<path d="{blob(cx, cy, rx, ry, seed, 0.004, 30)}" fill="{base}"/>']
    g = D.lin([(0, hi), (0.4, base), (1, dk_)] if light < 0 else [(0, dk_), (0.6, base), (1, hi)], 0, 0, 1, 1)
    out.append(f'<path d="{blob(cx, cy, rx, ry, seed, 0.004, 30)}" fill="{g}"/>')
    ip = inner_pal or (mix(base, dk_, 0.3), dk_, mix(dk_, "#000000", 0.3))
    gi = D.lin([(0, ip[2]), (0.55, ip[1]), (1, mix(ip[0], hi, 0.3))], 0, 0, 0.2, 1)
    out.append(f'<path d="{blob(cx, cy + rw * 0.2, rx - rw, ry - rw * ry / rx, seed + 1, 0.004, 30)}" fill="{gi}"/>')
    out.append(f'<path d="M {cx - rx * 0.85:.1f} {cy - ry * 0.35:.1f} Q {cx - rx * 0.4:.1f} {cy - ry * 1.02:.1f} {cx + rx * 0.3:.1f} {cy - ry * 0.98:.1f}" stroke="#FFFFFF" stroke-width="{max(1, rw * 0.5):.1f}" fill="none" opacity="0.85" stroke-linecap="round"/>')
    if inkw:
        out.append(f'<path d="{blob(cx, cy, rx, ry, seed, 0.004, 30)}" fill="none" stroke="{INK}" stroke-width="{inkw}" opacity="0.5"/>')
    return "".join(out)


def steam_plume(D, pts, w0, w1, seed, col="#FFFFFF", op=0.85, puffs=True):
    """A rising column of steam: a soft tapered body along a curve, billowing puffs breaking off, wisps."""
    rnd = random.Random(seed)
    out = []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        t = i / max(1, n - 1)
        r = w0 + (w1 - w0) * t
        g = D.rad([(0, col, op * (1 - t * 0.5)), (0.6, col, op * 0.35 * (1 - t * 0.6)), (1, col, 0)])
        out.append(f'<path d="{blob(x, y, r, r * 0.8, rnd.randint(0, 9999), 0.18, 12)}" fill="{g}"/>')
        if puffs and rnd.random() < 0.6:
            a = rnd.uniform(0, 6.28)
            out.append(f'<path d="{blob(x + math.cos(a) * r * 0.6, y + math.sin(a) * r * 0.5, r * 0.45, r * 0.38, rnd.randint(0, 9999), 0.2, 10)}" fill="{col}" opacity="{op * 0.3 * (1 - t * 0.5):.2f}"/>')
    for k in range(5):
        i = rnd.randint(n // 3, n - 1)
        x, y = pts[i]
        out.append(f'<path d="M {x:.1f} {y:.1f} q {rnd.uniform(-20, 20):.1f} {rnd.uniform(-20, -40):.1f} {rnd.uniform(-10, 30):.1f} {rnd.uniform(-40, -70):.1f}" stroke="{col}" stroke-width="{rnd.uniform(1.5, 3.5):.1f}" fill="none" opacity="{op * 0.35:.2f}" stroke-linecap="round"/>')
    return "".join(out)


def box3(D, cam, c, size, seed, pal, light=(-0.5, 0.6, 0.65), yaw=0.0, round_=0.0, inkw=1.2, tex=True, faces_out=None, angle_map=None):
    """An axis box (size = (sx, sy, sz), centred on c at its bottom face) rotated by yaw, its three visible faces
    painted with light.  Returns svg; if faces_out is a dict, fills it with {name: (d, pts)} for decoration."""
    sx, sy, sz = size
    cy_, sy_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))

    def T(p):
        x, y, z = p
        return (c[0] + x * cy_ - y * sy_, c[1] + x * sy_ + y * cy_, c[2] + z)
    hx, hy = sx / 2, sy / 2
    F = {"front": [(-hx, hy, 0), (hx, hy, 0), (hx, hy, sz), (-hx, hy, sz)],
         "back": [(-hx, -hy, 0), (hx, -hy, 0), (hx, -hy, sz), (-hx, -hy, sz)],
         "left": [(-hx, -hy, 0), (-hx, hy, 0), (-hx, hy, sz), (-hx, -hy, sz)],
         "right": [(hx, -hy, 0), (hx, hy, 0), (hx, hy, sz), (hx, -hy, sz)],
         "top": [(-hx, -hy, sz), (hx, -hy, sz), (hx, hy, sz), (-hx, hy, sz)]}
    N = {"front": (0, 1, 0), "back": (0, -1, 0), "left": (-1, 0, 0), "right": (1, 0, 0), "top": (0, 0, 1)}
    out = []
    vis = []
    for k, pts in F.items():
        nx, ny, nz = N[k]
        n = (nx * cy_ - ny * sy_, nx * sy_ + ny * cy_, nz)
        P3 = [T(p) for p in pts]
        ctr = [sum(p[i] for p in P3) / 4 for i in range(3)]
        to_cam = [cam.pos[i] - ctr[i] for i in range(3)]
        if sum(n[i] * to_cam[i] for i in range(3)) <= 0:
            continue
        br = max(0, sum(n[i] * light[i] for i in range(3)))
        vis.append((cam.depth(ctr), k, P3, br))
    for _, k, P3, br in sorted(vis, reverse=True):
        pts = [cam(p) for p in dens3(P3, 6)]
        lt_, base, dk_ = pal
        b = 0.2 + 0.8 * br
        col = mix(dk_, base, b / 0.55) if b < 0.55 else mix(base, lt_, min(1, (b - 0.55) / 0.45))
        d = smooth_closed(pts) if round_ else pdl(pts)
        out.append(f'<path d="{d}" fill="{col}"/>')
        x0, y0, x1, y1 = bbox(pts)
        g = D.lin([(0, lt_, 0.3), (0.5, col, 0), (1, dk_, 0.35)], x0, y0, x1, y1, "userSpaceOnUse")
        out.append(f'<path d="{d}" fill="{g}"/>')
        if tex:
            ang = (angle_map or {}).get(k, -90)
            out.append(strokes(D.nid(), d, (x0 - 3, y0 - 3, x1 + 3, y1 + 3), [mix(col, lt_, 0.3), mix(col, dk_, 0.3), col], seed, n=int(max(6, (x1 - x0) * (y1 - y0) / 160)),
                               angle=ang, length=(6, max(8, (y1 - y0) * 0.5)), width=(1, 3), opacity=(0.1, 0.28), curve=0.08))
        if inkw:
            out.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{inkw}" stroke-linejoin="round" opacity="0.5"/>')
        if faces_out is not None:
            faces_out[k] = (d, pts, P3)
        seed += 7
    return "".join(out)
