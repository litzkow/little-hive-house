"""World Places, Latin America: six painted travel posters (Rio, Machu Picchu, Havana, Chichén Itzá, Cartagena,
Buenos Aires) in the same painterly travel-poster idiom as world_painted.py: a real viewpoint, a time of day,
light direction, atmospheric depth and small storytelling details."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from places_painted import Cam, puff_column
from world_painted import cumulus, streak_cloud, gulls, figure, leaf_canopy, water_lines, mix, Q, defs
from poster import poster


def clip(uid, pts):
    return f'<clipPath id="{uid}"><polygon points="{P(pts)}"/></clipPath>'


def smooth(pts, closed=True):
    """Catmull-Rom through points -> cubic path d."""
    n = len(pts)
    if closed:
        p = [pts[-1]] + pts + pts[:2]
    else:
        p = [pts[0]] + pts + [pts[-1]]
    d = f"M {p[1][0]:.1f} {p[1][1]:.1f} "
    rng = range(1, n + 1) if closed else range(1, n)
    for i in rng:
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f} "
    return d + ("Z" if closed else "")


def frigatebird(x, y, s, color, tilt=0):
    """Magnificent frigatebird soaring: long angled wings, deeply forked tail."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({tilt}) scale({s:.2f})" fill="{color}">'
            '<path d="M 0 0 C -6 -3 -12 -9 -22 -8 C -16 -5 -10 -1 -3 2 Z M 0 0 C 6 -3 12 -9 22 -8 C 16 -5 10 -1 3 2 Z"/>'
            '<path d="M -1.6 -2 L 1.6 -2 L 1.2 5 L 3 11 L 0.6 6.5 L 0 7 L -0.6 6.5 L -3 11 L -1.2 5 Z"/>'
            '<path d="M -1 -2 L 0 -6 L 1 -2 Z"/></g>')


def person(x, base, h, top, bottom=None, skin="#B07A5A", hair="#2A1A14", dress=False, back=False, flip=1, rim=None,
           long_hair=False, hat=None, arms="down", shoes="#2A2226", lean=0):
    """Small painted person (h px tall), unit body 100 high. dress=True gives a flared skirt; back=True shows the
    back of the head; arms: 'down', 'up' (raised hand), 'out' (reaching forward), 'none'. rim = rim-light colour
    on the right side (flip=-1 mirrors everything)."""
    s = h / 100
    bottom = bottom or top
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({s * flip:.3f} {s:.3f}) skewX({lean})">']
    # legs
    g.append(f'<path d="M -7 -48 L -6.5 -3 L -2 -3 L -0.6 -40 L 0.6 -40 L 2 -3 L 6.5 -3 L 7 -48 Z" fill="{bottom if not dress else skin}"/>')
    g.append(f'<path d="M -8 -4 L -1.6 -4 L -1.4 0 L -9.5 0 Z M 1.6 -4 L 8 -4 L 9.5 0 L 1.4 0 Z" fill="{shoes}"/>')
    if dress:
        g.append(f'<path d="M -9 -58 L 9 -58 L 15 -22 Q 0 -17 -15 -22 Z" fill="{bottom}"/>'
                 f'<path d="M 4 -58 L 9 -58 L 15 -22 Q 11 -20.6 7 -20 Z" fill="#000" opacity="0.14"/>')
    # torso
    g.append(f'<path d="M -11 -80 Q -12.5 -78 -11.5 -66 L -8.5 -46 L 8.5 -46 L 11.5 -66 Q 12.5 -78 11 -80 Q 0 -84 -11 -80 Z" fill="{top}"/>'
             f'<path d="M 5 -82 Q 11 -80.5 11.5 -78 Q 12.5 -70 11.5 -66 L 8.5 -46 L 4 -46 Z" fill="#000" opacity="0.12"/>')
    # arms
    if arms == "down":
        g.append(f'<path d="M -11 -78 Q -15 -66 -14 -50 M 11 -78 Q 15 -66 14 -50" fill="none" stroke="{top}" stroke-width="5.4" stroke-linecap="round"/>'
                 f'<circle cx="-14" cy="-48" r="2.8" fill="{skin}"/><circle cx="14" cy="-48" r="2.8" fill="{skin}"/>')
    elif arms == "up":
        g.append(f'<path d="M -11 -78 Q -15 -66 -14 -50" fill="none" stroke="{top}" stroke-width="5.4" stroke-linecap="round"/><circle cx="-14" cy="-48" r="2.8" fill="{skin}"/>'
                 f'<path d="M 10 -78 Q 20 -86 19 -102" fill="none" stroke="{top}" stroke-width="5.4" stroke-linecap="round"/><circle cx="19" cy="-105" r="3" fill="{skin}"/>')
    elif arms == "out":
        g.append(f'<path d="M -11 -78 Q -15 -66 -14 -50" fill="none" stroke="{top}" stroke-width="5.4" stroke-linecap="round"/><circle cx="-14" cy="-48" r="2.8" fill="{skin}"/>'
                 f'<path d="M 10 -77 Q 16 -64 26 -62" fill="none" stroke="{top}" stroke-width="5.4" stroke-linecap="round"/><circle cx="28" cy="-62" r="2.9" fill="{skin}"/>')
    # neck and head
    g.append(f'<rect x="-2.6" y="-86" width="5.2" height="6" fill="{skin}"/><ellipse cx="0" cy="-92" rx="7" ry="8" fill="{skin}"/>')
    if back:
        g.append(f'<ellipse cx="0" cy="-93" rx="7.6" ry="8.6" fill="{hair}"/>')
    else:
        g.append(f'<path d="M -7.4 -91 Q -8 -101 0 -101.5 Q 8 -101 7.6 -92 Q 3 -97 -2 -96 Q -6 -94 -7.4 -91 Z" fill="{hair}"/>')
    if long_hair:
        g.append(f'<path d="M -7.6 -94 Q -10 -80 -8 -70 L 8 -70 Q 10 -80 7.6 -94 Z" fill="{hair}"/>')
    if hat:
        g.append(f'<ellipse cx="0" cy="-97" rx="13" ry="3" fill="{hat}"/><path d="M -7 -97 Q -7 -107 0 -107 Q 7 -107 7 -97 Z" fill="{hat}"/>'
                 f'<rect x="-7" y="-100" width="14" height="2" fill="#000" opacity="0.25"/>')
    if rim:
        g.append(f'<path d="M 11.5 -78 Q 12.5 -70 11.5 -64 L 8.6 -47" fill="none" stroke="{rim}" stroke-width="2.2" stroke-linecap="round" opacity="0.9"/>'
                 f'<path d="M 4 -99 Q 8 -96 7.4 -88" fill="none" stroke="{rim}" stroke-width="2" stroke-linecap="round" opacity="0.9"/>')
    g.append("</g>")
    return "".join(g)


def pipa(x, y, s, sail="#E8303A", cross="#FFD23A", tail="#2E6AB8", string_to=None, seed=0):
    """A paper kite (pipa) - Rio's skies are full of them on breezy afternoons."""
    rnd = random.Random(seed)
    out = []
    if string_to:
        out.append(f'<path d="M {x:.1f} {y + 6 * s:.1f} Q {(x + string_to[0]) / 2 + 20:.1f} {(y + string_to[1]) / 2 + 20:.1f} {string_to[0]:.1f} {string_to[1]:.1f}" fill="none" stroke="#3A3040" stroke-width="0.8" opacity="0.6"/>')
    tp = [(x - 1 * s, y + 9 * s)]
    for i in range(1, 9):
        tp.append((x - 1 * s - i * 3.2 * s + math.sin(i * 0.9) * 3 * s, y + 9 * s + i * 3.6 * s))
    out.append(f'<polyline points="{P(tp)}" fill="none" stroke="{tail}" stroke-width="{0.9 * s:.1f}"/>')
    out.append("".join(f'<path d="M {px - 1.6 * s:.1f} {py - 1 * s:.1f} L {px + 1.6 * s:.1f} {py + 1 * s:.1f} M {px - 1.6 * s:.1f} {py + 1 * s:.1f} L {px + 1.6 * s:.1f} {py - 1 * s:.1f}" stroke="{tail if i % 2 else sail}" stroke-width="{1.2 * s:.1f}"/>' for i, (px, py) in enumerate(tp[2::2])))
    out.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate(-14) scale({s:.2f})"><path d="M 0 -10 L 7 0 L 0 10 L -7 0 Z" fill="{sail}"/>'
               f'<path d="M 0 -10 L 7 0 L 0 0 Z" fill="#FFFFFF" opacity="0.25"/><path d="M -7 0 L 7 0 M 0 -10 L 0 10" stroke="{cross}" stroke-width="1.6"/></g>')
    return "".join(out)


# ================================================================ RIO — Sugarloaf over Botafogo cove at golden hour
def granite_dome(u, outline, light_x0, light_x1, lit, mid, shade, streak_cols, seed, veg=None):
    """Bare granite monolith with exfoliation streaks, shade side to lit side gradient, vegetation in gullies."""
    out = [defs(lg(f"{u}-g", [(0, shade), (0.45, mid), (1, lit)], light_x0, 0, light_x1, 0, units="userSpaceOnUse"),
                clip(f"{u}-c", outline))]
    out.append(Q(outline, f"url(#{u}-g)"))
    xs = [x for x, _ in outline]
    ys = [y for _, y in outline]
    box = (min(xs), min(ys), max(xs), max(ys))
    g = [streaks(int((box[2] - box[0]) * (box[3] - box[1]) / 90), seed, box, streak_cols, w=(1.2, 3.6), length=(20, 90), opacity=(0.2, 0.55), slant=0.12)]
    if veg:
        g.append(veg)
    out.append(f'<g clip-path="url(#{u}-c)">' + "".join(g) + "</g>")
    return "".join(out)


def forest_hill(u, outline, seed, dark, mid, lit, light=(1, -1), n=None, gold=None):
    """Hill covered in Atlantic forest: base fill then many canopy clumps, lit on the light side."""
    xs = [x for x, _ in outline]
    ys = [y for _, y in outline]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    rnd = random.Random(seed)
    out = [clip(f"{u}-c", outline), Q(outline, mid)]
    cl = []
    n = n or int((x1 - x0) * (y1 - y0) / 55)
    for _ in range(n):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0 - 4, y1)
        cl.append((x, y, rnd.uniform(3, 7.5) * (0.6 + 0.6 * (y - y0) / max(1, y1 - y0))))
    lx, ly = light
    body = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>' for x, y, r in cl)
    sh = "".join(f'<circle cx="{x - lx * r * 0.35:.1f}" cy="{y - ly * r * 0.35:.1f}" r="{r * 0.75:.1f}"/>' for x, y, r in cl)
    li = "".join(f'<circle cx="{x + lx * r * 0.35:.1f}" cy="{y + ly * r * 0.4:.1f}" r="{r * 0.5:.1f}"/>' for x, y, r in cl)
    out.append(f'<g clip-path="url(#{u}-c)"><g fill="{dark}" opacity="0.8">{sh}</g><g fill="{mid}">{body}</g>'
               f'<g fill="{dark}" opacity="0.45">{sh}</g><g fill="{lit}" opacity="0.8">{li}</g>')
    if gold:
        out.append(f'<g fill="{gold}" opacity="0.55">' + "".join(f'<circle cx="{x + lx * r * 0.5:.1f}" cy="{y + ly * r * 0.55:.1f}" r="{r * 0.22:.1f}"/>' for x, y, r in cl if rnd.random() < 0.5) + "</g>")
    out.append("</g>")
    # silhouette edge clumps so the skyline is bumpy, not a clean polygon
    top = [(x, y) for x, y in outline if y < y1 - 2]
    edge = []
    for (xa, ya), (xb, yb) in zip(top, top[1:]):
        L = math.hypot(xb - xa, yb - ya)
        for j in range(int(L / 5)):
            t = j / max(1, int(L / 5))
            r = rnd.uniform(2.5, 5.5)
            edge.append((xa + (xb - xa) * t, ya + (yb - ya) * t + r * 0.4, r))
    out.append(f'<g fill="{mid}">' + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>' for x, y, r in edge) + "</g>")
    out.append(f'<g fill="{lit}" opacity="0.75">' + "".join(f'<circle cx="{x + lx * r * 0.3:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.5:.1f}"/>' for x, y, r in edge) + "</g>")
    return "".join(out)


def apartment(x, base, w, h, d, wall, side, roof, rnd, lit_win="#FFE2A0"):
    """Rio apartment block seen from above-left: front face, sunlit right face, flat roof with water tank."""
    out = [Q([(x + w, base), (x + w, base - h), (x + w + d, base - h - d * 0.45), (x + w + d, base - d * 0.45)], side),
           f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{wall}"/>',
           Q([(x, base - h), (x + w, base - h), (x + w + d, base - h - d * 0.45), (x + d, base - h - d * 0.45)], roof)]
    fl = max(2, int(h / 4.2))
    cols = max(2, int(w / 4))
    win = []
    for i in range(fl):
        yy = base - h + 2 + i * (h - 3) / fl
        win.append(f'<rect x="{x + 1:.1f}" y="{yy:.1f}" width="{w - 2:.1f}" height="1.1" fill="#3A3E5A" opacity="0.35"/>')
        for j in range(cols):
            if rnd.random() < 0.08:
                win.append(f'<rect x="{x + 1 + j * (w - 2) / cols:.1f}" y="{yy - 0.4:.1f}" width="1.6" height="1.6" fill="{lit_win}"/>')
        win.append(f'<path d="M {x + w + 0.6:.1f} {yy - 0.2:.1f} l {d - 1:.1f} {-(d - 1) * 0.45:.1f}" stroke="#FFFFFF" stroke-width="0.9" opacity="0.45"/>')
    out.append("".join(win))
    if rnd.random() < 0.5:
        tx = x + rnd.uniform(0.2, 0.6) * w
        out.append(f'<rect x="{tx:.1f}" y="{base - h - d * 0.3 - 3:.1f}" width="3.2" height="3" fill="{side}"/>')
    return "".join(out)


def sailboat_moored(x, y, s, rnd, hull="#FFFFFF"):
    m = rnd.uniform(9, 14) * s
    return (f'<path d="M {x - 4 * s:.1f} {y:.1f} L {x + 4 * s:.1f} {y:.1f} L {x + 3 * s:.1f} {y + 1.6 * s:.1f} L {x - 3 * s:.1f} {y + 1.6 * s:.1f} Z" fill="{hull}"/>'
            f'<line x1="{x - 0.3 * s:.1f}" y1="{y:.1f}" x2="{x - 0.3 * s:.1f}" y2="{y - m:.1f}" stroke="#F4EEE4" stroke-width="{max(0.9, 0.7 * s):.1f}"/>'
            f'<rect x="{x - 3.6 * s:.1f}" y="{y + 1.8 * s:.1f}" width="{7.2 * s:.1f}" height="{1.0 * s:.1f}" fill="{hull}" opacity="0.35"/>')


def ipe_tree(x, base, h, seed, spread=(-55, 55), bloom="#F6C431", bloom_lit="#FFE27A", bloom_shade="#C8901E", trunk="#4A3A30"):
    """Yellow ipê in full flower: dark crooked trunk and limbs carrying clouds of golden blossom."""
    rnd = random.Random(seed)
    out = []
    limbs = []
    for k in range(6):
        a = math.radians(-90 + spread[0] + (spread[1] - spread[0]) * (k + rnd.uniform(0.1, 0.9)) / 6)
        L = h * rnd.uniform(0.45, 0.7)
        sx, sy = x + rnd.uniform(-3, 3), base - h * rnd.uniform(0.25, 0.45)
        ex, ey = sx + L * math.cos(a), sy + L * math.sin(a) * 0.9
        limbs.append((sx, sy, ex, ey))
    out.append(f'<path d="M {x - 5:.1f} {base:.1f} Q {x - 2:.1f} {base - h * 0.3:.1f} {x:.1f} {base - h * 0.42:.1f} L {x + 3:.1f} {base - h * 0.42:.1f} Q {x + 4:.1f} {base - h * 0.3:.1f} {x + 6:.1f} {base:.1f} Z" fill="{trunk}"/>')
    for sx, sy, ex, ey in limbs:
        out.append(f'<path d="M {sx:.1f} {sy:.1f} Q {(sx + ex) / 2 + rnd.uniform(-8, 8):.1f} {(sy + ey) / 2:.1f} {ex:.1f} {ey:.1f}" fill="none" stroke="{trunk}" stroke-width="{rnd.uniform(2, 3.4):.1f}" stroke-linecap="round"/>')
    cl = []
    for sx, sy, ex, ey in limbs:
        for _ in range(16):
            t = rnd.uniform(0.4, 1.15)
            cx_, cy_ = sx + (ex - sx) * t + rnd.uniform(-16, 16), sy + (ey - sy) * t + rnd.uniform(-12, 10)
            R = rnd.uniform(6, 11)
            cl.append((cx_, cy_, R))
    sh, bd, li = [], [], []
    for cx_, cy_, R in cl:
        for _ in range(int(R * 1.6)):
            a_ = rnd.uniform(0, 2 * math.pi)
            d_ = R * rnd.random() ** 0.6
            x_, y_ = cx_ + d_ * math.cos(a_), cy_ + d_ * math.sin(a_) * 0.8
            r_ = rnd.uniform(1.8, 3.4)
            up = -math.sin(a_) * d_ / R + math.cos(a_) * d_ / R * 0.5
            (li if up > 0.3 else sh if up < -0.35 else bd).append(f'<circle cx="{x_:.1f}" cy="{y_:.1f}" r="{r_:.1f}"/>')
    out.append(f'<g fill="{bloom_shade}">' + "".join(f'<circle cx="{a - 1:.1f}" cy="{b + 2:.1f}" r="{r * 0.6:.1f}"/>' for a, b, r in cl) + "</g>")
    out.append(f'<g fill="{bloom_shade}">{"".join(sh)}</g><g fill="{bloom}">{"".join(bd)}</g><g fill="{bloom_lit}">{"".join(li)}</g>')
    xs = [c[0] for c in cl]
    ys = [c[1] for c in cl]
    out.append(dots(90, seed + 3, (min(xs) - 8, min(ys) - 8, max(xs) + 8, max(ys) + 8), "#FFF4C0", r=(0.8, 1.6), opacity=(0.6, 1)))
    out.append(dots(50, seed + 4, (min(xs), min(ys), max(xs), max(ys)), "#8E5A1A", r=(0.6, 1.2), opacity=(0.4, 0.8)))
    return "".join(out)


def palm_frond(x, y, L, ang, color, lit=None, droop=0.35, n=18, w=1.0):
    """Coconut / royal-palm frond: curved rachis with leaflets hanging off both sides."""
    a = math.radians(ang)
    pts = []
    for i in range(n + 1):
        t = i / n
        px = x + L * t * math.cos(a)
        py = y + L * t * math.sin(a) + droop * L * t * t
        pts.append((px, py))
    out = [f'<polyline points="{P(pts)}" fill="none" stroke="{color}" stroke-width="{2.2 * w:.1f}" stroke-linecap="round"/>']
    leaf = []
    for i in range(1, n + 1):
        (px, py), (qx, qy) = pts[i - 1], pts[i]
        dx, dy = qx - px, qy - py
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        ll = L * 0.28 * math.sin(math.pi * (0.15 + 0.85 * i / n)) * w
        for sgn in (1, -1):
            ex = px + sgn * nx * ll + dx * 0.8 + 0
            ey = py + sgn * ny * ll + ll * 0.55
            leaf.append(f'<path d="M {px:.1f} {py:.1f} Q {px + sgn * nx * ll * 0.5:.1f} {py + sgn * ny * ll * 0.5:.1f} {ex:.1f} {ey:.1f}"/>')
    out.append(f'<g fill="none" stroke="{color}" stroke-width="{2.0 * w:.1f}" stroke-linecap="round">{"".join(leaf)}</g>')
    if lit:
        out.append(f'<polyline points="{P(pts[: n // 2 + 3])}" fill="none" stroke="{lit}" stroke-width="{1.0 * w:.1f}" stroke-linecap="round" opacity="0.8"/>')
    return "".join(out)


def coco_palm(x, base, h, seed, lean=0.15, L=None, trunk="#8A7058", trunk_dark="#4E3E34", trunk_lit="#E8C898",
              dark="#183424", mid="#2C5634", lit="#86AC5A", nuts=True, fronds=None, sw=1.0):
    """Coconut / royal palm with a curved ringed trunk and a crown of feathery fronds (leaflets hang off each rachis)."""
    rnd = random.Random(seed)
    tx, ty = x + lean * h, base - h
    cx_, cy_ = x + lean * h * 0.15, base - h * 0.55
    w0, w1 = max(2.0, h * 0.032), max(1.5, h * 0.02)
    out = [f'<path d="M {x - w0:.1f} {base:.1f} Q {cx_ - w0 * 0.8:.1f} {cy_:.1f} {tx - w1:.1f} {ty:.1f} L {tx + w1:.1f} {ty:.1f} Q {cx_ + w0 * 0.8:.1f} {cy_:.1f} {x + w0:.1f} {base:.1f} Z" fill="{trunk}"/>',
           f'<path d="M {x + w0 * 0.4:.1f} {base:.1f} Q {cx_ + w0 * 0.5:.1f} {cy_:.1f} {tx + w1 * 0.5:.1f} {ty:.1f} L {tx + w1:.1f} {ty:.1f} Q {cx_ + w0 * 0.8:.1f} {cy_:.1f} {x + w0:.1f} {base:.1f} Z" fill="{trunk_lit}" opacity="0.7"/>']
    rings = []
    n = int(h / 5)
    for i in range(1, n):
        t = i / n
        px = (1 - t) ** 2 * x + 2 * (1 - t) * t * cx_ + t * t * tx
        py = (1 - t) ** 2 * base + 2 * (1 - t) * t * cy_ + t * t * ty
        w = w0 + (w1 - w0) * t
        rings.append(f'<path d="M {px - w:.1f} {py:.1f} q {w:.1f} {1.6:.1f} {2 * w:.1f} 0"/>')
    out.append(f'<g fill="none" stroke="{trunk_dark}" stroke-width="1" opacity="0.55">{"".join(rings)}</g>')
    L = L or h * 0.42
    fronds = fronds or [-172, -150, -128, -108, -88, -66, -44, -22, -6, 14, 160, 176]
    back, front = [], []
    for k, a_ in enumerate(fronds):
        a = math.radians(a_ + rnd.uniform(-5, 5))
        Lf = L * rnd.uniform(0.78, 1.05) * (0.8 if -120 < a_ < -60 else 1)
        droop = 0.55 if (a_ > 0 or a_ < -160) else 0.42
        pts = []
        for i in range(17):
            t = i / 16
            pts.append((tx + Lf * t * math.cos(a), ty + Lf * t * math.sin(a) * 0.7 + droop * Lf * t * t))
        lf = []
        for i in range(2, 17):
            (px, py), (qx, qy) = pts[i - 1], pts[i]
            dx, dy = qx - px, qy - py
            ln = math.hypot(dx, dy) or 1
            ux, uy = dx / ln, dy / ln
            ll = Lf * 0.26 * math.sin(math.pi * min(1, 0.12 + i / 16)) + 2
            for sgn in (1, -1):
                nx, ny = -uy * sgn, ux * sgn
                ex = px + ll * (nx * 0.55 + ux * 0.55)
                ey = py + ll * (ny * 0.55 + uy * 0.55 + 0.75)
                lf.append(f'<path d="M {px:.1f} {py:.1f} Q {px + (ex - px) * 0.5 + nx * 2:.1f} {py + (ey - py) * 0.3:.1f} {ex:.1f} {ey:.1f}"/>')
        group = back if k % 2 == 0 else front
        group.append((pts, lf))
    for layer, col, hi in ((back, dark, mid), (front, mid, lit)):
        for pts, lf in layer:
            out.append(f'<g fill="none" stroke="{col}" stroke-width="{2.4 * sw:.1f}" stroke-linecap="round">{"".join(lf)}</g>')
            out.append(f'<polyline points="{P(pts)}" fill="none" stroke="{col}" stroke-width="{2.6 * sw:.1f}" stroke-linecap="round"/>')
            out.append(f'<g fill="none" stroke="{hi}" stroke-width="{1.1 * sw:.1f}" stroke-linecap="round" opacity="0.75">{"".join(lf[::3])}</g>')
            out.append(f'<polyline points="{P(pts[:9])}" fill="none" stroke="{hi}" stroke-width="{1.1 * sw:.1f}" stroke-linecap="round" opacity="0.8"/>')
    if nuts:
        out.append("".join(f'<circle cx="{tx + dx:.1f}" cy="{ty + dy:.1f}" r="{max(2, h * 0.016):.1f}" fill="{c}"/>' for dx, dy, c in
                           ((-4, 4, "#6A5A2E"), (3, 5, "#7E6E34"), (0, 8, "#5A4A28"), (6, 2, "#8E7A3A"))))
    return "".join(out)


def marmoset(x, y, s, flip=False, body="#7E7064", dark="#2E2622", tuft="#F6F2EA", rim="#FFD89A"):
    """Common marmoset (sagui) sitting hunched, head turned to us: white ear tufts, white forehead blaze,
    banded back and a long ringed tail hanging down."""
    sx = -s if flip else s
    g = [f'<g transform="translate({x:.1f} {y:.1f}) scale({sx:.2f} {s:.2f})">']
    tail = [(11, -3), (15, 6), (16, 16), (13, 26), (11, 36), (13, 44), (18, 48)]
    for i, ((ax, ay), (bx, by)) in enumerate(zip(tail, tail[1:])):
        for j in range(2):
            t0, t1 = j / 2, (j + 1) / 2
            g.append(f'<line x1="{ax + (bx - ax) * t0:.1f}" y1="{ay + (by - ay) * t0:.1f}" x2="{ax + (bx - ax) * t1:.1f}" y2="{ay + (by - ay) * t1:.1f}" '
                     f'stroke="{dark if j == 0 else "#A89C8E"}" stroke-width="{4.6 - i * 0.35:.1f}" stroke-linecap="round"/>')
    g.append(f'<ellipse cx="2" cy="0.6" rx="15" ry="2.4" fill="#000" opacity="0.22"/>')
    g.append(f'<path d="M -9 0 C -15 -7 -12 -24 0 -26 C 12 -28 19 -13 15 0 Z" fill="{body}"/>')
    g.append(f'<path d="M 4 -26 C 13 -25 19 -13 15 0 L 9 0 C 12 -10 10 -20 4 -26 Z" fill="#4E4440" opacity="0.4"/>')
    g.append('<g fill="none" stroke="#2E2622" stroke-width="1.6" opacity="0.55" stroke-linecap="round">'
             + "".join(f'<path d="M {-3 + i * 3.4:.1f} {-25 + i * 0.8:.1f} q 3 6 {1 + i * 0.6:.1f} {13 + i:.1f}"/>' for i in range(5)) + "</g>")
    g.append('<g fill="none" stroke="#D8CCBE" stroke-width="0.9" opacity="0.6" stroke-linecap="round">'
             + "".join(f'<path d="M {-1.4 + i * 3.4:.1f} {-25 + i * 0.8:.1f} q 3 6 {1 + i * 0.6:.1f} {12 + i:.1f}"/>' for i in range(5)) + "</g>")
    g.append(f'<ellipse cx="8" cy="-4" rx="7" ry="5" fill="#5E544C"/>')
    g.append(f'<path d="M -5 -15 Q -10 -8 -9 -1" fill="none" stroke="#4E443E" stroke-width="3.4" stroke-linecap="round"/>'
             f'<path d="M -9.8 0 l -2 0.6 M -9 0.4 l -0.6 1.4" stroke="{dark}" stroke-width="1.2" stroke-linecap="round"/>')
    # head with the famous white ear tufts
    g.append(f'<path d="M -15 -33 C -24 -42 -29 -27 -21 -23 C -19 -26 -17 -29 -14.5 -30 Z" fill="{tuft}"/>'
             f'<path d="M -1 -33 C 8 -42 13 -27 5 -23 C 3 -26 1 -29 -1.5 -30 Z" fill="{tuft}"/>')
    g.append('<g stroke="#C8C0B4" stroke-width="0.7" fill="none">'
             '<path d="M -16 -31 L -24 -34 M -16 -30 L -25 -29 M -16 -29 L -23 -25 M 0 -31 L 8 -34 M 0 -30 L 9 -29 M 0 -29 L 7 -25"/></g>')
    g.append(f'<circle cx="-8" cy="-30" r="8.2" fill="{dark}"/>'
             f'<ellipse cx="-8" cy="-27.5" rx="4.6" ry="4.4" fill="#B8A48E"/>'
             f'<ellipse cx="-8" cy="-37.4" rx="2.2" ry="1.3" fill="{tuft}"/>'
             '<circle cx="-10.4" cy="-30.6" r="1.5" fill="#1A1412"/><circle cx="-5.6" cy="-30.6" r="1.5" fill="#1A1412"/>'
             '<circle cx="-10" cy="-31" r="0.5" fill="#FFFFFF"/><circle cx="-5.2" cy="-31" r="0.5" fill="#FFFFFF"/>'
             '<path d="M -9 -26.4 Q -8 -25.6 -7 -26.4" stroke="#3A2A24" stroke-width="0.8" fill="none"/>')
    g.append(f'<path d="M 4 -26 C 12 -25 18 -14 15.5 -3" fill="none" stroke="{rim}" stroke-width="1.8" stroke-linecap="round" opacity="0.9"/>'
             f'<path d="M -2 -36 Q 0 -32 -0.6 -27" fill="none" stroke="{rim}" stroke-width="1.3" opacity="0.8"/>')
    g.append("</g>")
    return "".join(g)


def bemtevi(x, y, s, flip=False):
    """Great kiskadee (bem-te-vi): lemon-yellow belly, black-and-white striped head, rufous wings."""
    sx = -s if flip else s
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({sx:.2f} {s:.2f})">'
            '<path d="M 6 -6 L 14 -2 L 13 0 L 5 -3 Z" fill="#5A4430"/>'
            '<path d="M -6 -7 Q -7 0 0 0 Q 7 -1 7 -6 Q 4 -12 -2 -12 Q -6 -11 -6 -7 Z" fill="#F6D020"/>'
            '<path d="M -1 -11 Q 6 -11 8 -5 Q 4 -3 0 -5 Z" fill="#7A5634"/><path d="M 1 -9 Q 5 -8 7 -5" stroke="#C88A4A" stroke-width="1" fill="none"/>'
            '<circle cx="-4" cy="-14" r="4.6" fill="#1E1A1A"/><path d="M -8.4 -14.6 Q -4 -13 0.2 -14.8 L 0.4 -13.2 Q -4 -11.6 -8.6 -13.2 Z" fill="#FFFFFF"/>'
            '<path d="M -7.6 -12 Q -6 -9 -4 -9.6 L -2.6 -11.6 Z" fill="#FFFFFF"/><path d="M -8.6 -14.6 L -12.4 -14 L -8.6 -13 Z" fill="#1E1A1A"/>'
            '<circle cx="-5.6" cy="-13.4" r="0.7" fill="#FFFFFF" opacity="0"/><path d="M -2 0 L -2.6 2 M 1.4 0 L 1 2" stroke="#3A2A24" stroke-width="0.9"/></g>')


def rio():
    u = "rj"
    hz = 246
    out = [defs(
        lg(f"{u}-sky", [(0, "#3A70B0"), (0.3, "#7AA4CC"), (0.56, "#C6CCCC"), (0.78, "#F6CFA0"), (1, "#FFD49A")], 0, 0, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#B4BCC4"), (0.1, "#6C94AE"), (0.5, "#2F6A90"), (1, "#1F4F72")], 0, hz, 0, 330, units="userSpaceOnUse"),
        lg(f"{u}-cove", [(0, "#4C88AA"), (0.6, "#2E6688"), (1, "#245676")], 0, 306, 0, 362, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#FADDB6", 0), (1, "#FADDB6", 0.8)], 0, 180, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-ref", [(0, "#FFD89A", 0.85), (1, "#FFD89A", 0)], 0, 308, 0, 356, units="userSpaceOnUse"),
        lg(f"{u}-pave", [(0, "#EFE4D2"), (1, "#FFF4E2")], 0, 412, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="{hz + 2}" fill="url(#{u}-sky)"/>')
    out.append(glow(650, 190, 380, "#FFC870", f"{u}-sun", 0.85))
    # golden-hour cumulus over the Atlantic, lit from the low sun on the right (west)
    out.append(cumulus(f"{u}-c1", 150, 126, 176, 46, 3, "#FFEAD0", "#F6D2C0", "#B4A0BE", hi="#FFF4DC", hi_op=0.75, light=1))
    out.append(cumulus(f"{u}-c2", 548, 90, 124, 34, 5, "#FFE8C4", "#F8D0B4", "#BEA2BA", hi="#FFF4DC", hi_op=0.75, light=1))
    out.append(cumulus(f"{u}-c3", 248, 186, 92, 18, 9, "#FFE2BC", "#F4CCB8", "#C4A8BE", hi="#FFF0D8", light=1))
    for x, y, w in ((60, 168, 70), (470, 200, 80), (330, 150, 50), (520, 156, 40)):
        out.append(streak_cloud(x, y, w, "#FFDCB8", 0.6, 3))
    # open Atlantic at the mouth of the bay
    out.append(f'<rect x="0" y="{hz}" width="600" height="{444 - hz}" fill="url(#{u}-sea)"/>')
    # Niterói across Guanabara Bay: two hazy ridges, the city along the shore, Santa Cruz fortress at the point
    poly, _ = ridge_poly([(-10, 196), (30, 186), (70, 200), (110, 192), (150, 210), (196, 222), (232, 240), (250, 247)], 11, base=hz + 2, amp=6, fill="#ACA4C0")
    out.append(poly)
    poly, nl = ridge_poly([(-10, 222), (40, 214), (90, 226), (140, 220), (180, 236), (214, 246)], 12, base=hz + 3, amp=4, fill="#9890B2")
    out.append(poly)
    out.append(f'<rect x="0" y="178" width="300" height="{hz - 176}" fill="url(#{u}-haze)"/>')
    rnd = random.Random(14)
    out.append("".join(f'<rect x="{rnd.uniform(-5, 205):.1f}" y="{hz - rnd.uniform(1, 6):.1f}" width="{rnd.uniform(2, 5):.1f}" height="{rnd.uniform(2, 5):.1f}" fill="{rnd.choice(["#F6E2D2", "#E4D0D4", "#FFF0DC"])}"/>' for _ in range(54)))
    out.append('<g fill="#D8C4C4"><rect x="214" y="241" width="16" height="5"/><rect x="218" y="238" width="6" height="3"/></g>')
    # sun glitter on the open bay
    rnd = random.Random(21)
    for _ in range(70):
        y = hz + 3 + rnd.random() ** 1.4 * 50
        w = rnd.uniform(4, 14)
        out.append(f'<rect x="{rnd.uniform(0, 600):.1f}" y="{y:.1f}" width="{w:.1f}" height="1.1" rx="0.5" fill="#FFE2A8" opacity="{rnd.uniform(0.35, 0.8):.2f}"/>')
    out.append(water_lines(60, 22, (0, hz + 6, 600, 300), ["#8EB4C8", "#24557A"], w=(8, 26), h=(0.8, 1.4), opacity=(0.3, 0.6)))
    # a ferry crossing to Niterói, its wake catching the light
    out.append('<g><path d="M 120 268 L 150 268 L 147 273 L 123 273 Z" fill="#F4ECE2"/><rect x="128" y="263" width="16" height="5" fill="#FFFFFF"/>'
               '<rect x="130" y="264.5" width="12" height="1.6" fill="#3A5A7A"/><path d="M 150 270 L 200 272 L 150 273 Z" fill="#FFFFFF" opacity="0.55"/></g>')
    # Morro da Babilônia / Leme on the right, forested
    bab = [(470, 300), (500, 270), (530, 246), (556, 236), (580, 238), (610, 246), (610, 302)]
    out.append(forest_hill(f"{u}-bb", bab, 31, "#2C4A3A", "#41654A", "#94AA6A", light=(1, -1), gold="#F6CE80"))
    # Sugarloaf: the bare granite dome, its western flank glowing gold in the late sun
    sl = [(340, 262), (346, 236), (352, 206), (360, 176), (370, 150), (382, 130), (396, 116), (410, 108), (424, 106), (438, 110), (451, 120),
          (462, 136), (472, 160), (481, 190), (490, 224), (500, 258), (512, 292), (520, 306), (334, 306)]
    sl = [sl[0]] + rough(sl[1:-2], 41, amp=2.5, depth=2) + sl[-2:]
    rnd = random.Random(44)
    band = [(326, 310), (330, 272), (342, 262), (356, 256), (368, 260), (378, 246), (390, 256), (404, 264), (418, 258), (430, 264), (440, 250),
            (446, 228), (454, 222), (458, 240), (466, 258), (478, 256), (490, 268), (502, 266), (514, 290), (528, 310)]
    cl = []
    for (xa, ya), (xb, yb) in zip(band, band[1:]):
        L = math.hypot(xb - xa, yb - ya)
        for j in range(max(1, int(L / 4))):
            t = j / max(1, int(L / 4))
            cl.append((xa + (xb - xa) * t + rnd.uniform(-1.5, 1.5), ya + (yb - ya) * t + rnd.uniform(0, 3), rnd.uniform(2.6, 5)))
    for _ in range(120):
        x = rnd.uniform(330, 524)
        yt = y_on(band, x) or 280
        cl.append((x, rnd.uniform(yt + 4, 308), rnd.uniform(2.6, 5.5)))
    for _ in range(26):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.random() ** 0.5
        cl.append((422 + 14 * d * math.cos(a), 112 + 4 * d * math.sin(a), rnd.uniform(2, 3.6)))
    veg = (f'<polygon points="{P([(x, y + 3) for x, y in band])}" fill="#36543A"/>'
           + '<g fill="#2A4430">' + "".join(f'<circle cx="{x - 1:.1f}" cy="{y + 1.5:.1f}" r="{r:.1f}"/>' for x, y, r in cl) + "</g>"
           + '<g fill="#4E6E46">' + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.78:.1f}"/>' for x, y, r in cl) + "</g>"
           + '<g fill="#BCB870" opacity="0.8">' + "".join(f'<circle cx="{x + r * 0.35:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.4:.1f}"/>' for x, y, r in cl if x > 400 or rnd.random() < 0.4) + "</g>")
    out.append(granite_dome(f"{u}-sl", sl, 350, 505, "#FFC680", "#D69C88", "#7E7096", ["#6A5E7E", "#A88A8E", "#FFE2B0", "#7E6A84"], 7, veg=veg))
    out.append(f'<polyline points="{P(sl[8:17])}" fill="none" stroke="#FFE6B4" stroke-width="2.6" stroke-linejoin="round" opacity="0.95"/>')
    # Morro da Urca, lower and forested, with the cable-car station on top
    urca = [(232, 304), (250, 280), (270, 252), (292, 236), (316, 230), (338, 234), (352, 246), (366, 266), (378, 304)]
    out.append(forest_hill(f"{u}-ur", urca, 33, "#2E4C3C", "#46694C", "#A0B070", light=(1, -1), gold="#F6CE80"))
    out.append('<g><rect x="318" y="224" width="20" height="8" fill="#F2E8DC"/><rect x="331" y="224" width="7" height="8" fill="#FFF0DC"/><rect x="316" y="222" width="24" height="2.4" fill="#C8B8B0"/></g>')
    out.append('<path d="M 336 224 Q 380 182 414 110" fill="none" stroke="#2E2E3E" stroke-width="1.3"/><path d="M 338 226 Q 382 184 416 112" fill="none" stroke="#2E2E3E" stroke-width="0.9" opacity="0.7"/>')
    cx_, cy_ = 372, 182
    out.append(f'<line x1="{cx_}" y1="{cy_ - 6}" x2="{cx_}" y2="{cy_}" stroke="#2E2E3E" stroke-width="1.2"/><rect x="{cx_ - 5}" y="{cy_}" width="10" height="7" rx="1.6" fill="#E8F0F2"/><rect x="{cx_ - 4}" y="{cy_ + 1.5}" width="8" height="3" fill="#5A86A8"/><rect x="{cx_ + 1}" y="{cy_}" width="4" height="7" rx="1" fill="#FFF4DC" opacity="0.7"/>')
    # Urca neighbourhood along the water, low houses and a seawall
    rnd = random.Random(5)
    x = 226
    while x < 500:
        w = rnd.uniform(5, 11)
        h = rnd.uniform(4, 9)
        out.append(f'<rect x="{x:.1f}" y="{304 - h:.1f}" width="{w:.1f}" height="{h + 2:.1f}" fill="{rnd.choice(["#F4E2CC", "#EED0B8", "#F8EEE0", "#E8C8B0", "#DCC4C0"])}"/>'
                   f'<rect x="{x + w * 0.7:.1f}" y="{304 - h:.1f}" width="{w * 0.3:.1f}" height="{h + 2:.1f}" fill="#FFF0D8" opacity="0.7"/>')
        x += w + rnd.uniform(0, 2)
    out.append('<rect x="222" y="305" width="290" height="3" fill="#C8B4A4"/>')
    # Botafogo cove: still water mirroring the golden dome, yachts at anchor
    cove = [(-10, 322), (60, 312), (160, 307), (240, 308), (330, 309), (420, 309), (520, 310), (610, 318), (610, 372), (-10, 372)]
    out.append(Q(cove, f"url(#{u}-cove)"))
    rnd = random.Random(9)
    for i in range(26):
        y = 310 + i * 1.8
        w = (64 - i * 1.6) * rnd.uniform(0.7, 1.1)
        cx = 462 + rnd.uniform(-6, 6) + i * 0.6
        out.append(f'<rect x="{cx - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="1.4" rx="0.7" fill="#FFCC8A" opacity="{0.75 - i * 0.025:.2f}"/>')
    for i in range(16):
        y = 310 + i * 2.2
        w = (38 - i * 1.8) * rnd.uniform(0.7, 1.1)
        out.append(f'<rect x="{300 - w / 2 + rnd.uniform(-4, 4):.1f}" y="{y:.1f}" width="{w:.1f}" height="1.4" rx="0.7" fill="#3E6A50" opacity="0.5"/>')
    viu = [(-10, 330), (-10, 300), (16, 288), (44, 284), (72, 292), (96, 306), (110, 318)]
    out.append(forest_hill(f"{u}-vi", viu, 35, "#284436", "#3E5E46", "#8EA066", light=(1, -1), gold="#F6CE80"))
    rnd = random.Random(8)
    for _ in range(34):
        out.append(sailboat_moored(rnd.uniform(120, 530), rnd.uniform(316, 350), rnd.uniform(0.7, 1.15), rnd))
    out.append(water_lines(70, 23, (40, 312, 600, 360), ["#86B2C8", "#1E4E6E", "#FFE0AA"], w=(6, 22), h=(0.8, 1.4), opacity=(0.25, 0.6)))
    # Botafogo beach: the sand crescent with people strolling at the water's edge
    beach = [(-10, 370), (60, 362), (160, 357), (280, 355), (400, 357), (520, 361), (610, 368), (610, 384), (-10, 386)]
    out.append(Q(beach, "#F4DAB0"))
    out.append(f'<polyline points="{P(beach[:7])}" fill="none" stroke="#FFFFFF" stroke-width="1.8" opacity="0.85"/>')
    rnd = random.Random(16)
    for _ in range(18):
        bx = rnd.uniform(40, 560)
        by = (y_on(beach[:7], bx) or 360) + rnd.uniform(2, 7)
        c = rnd.choice(["#E8543E", "#2E5A7E", "#F6C431", "#2A2A3A", "#1E8A6A"])
        out.append(f'<rect x="{bx:.1f}" y="{by - 4:.1f}" width="1.6" height="4" fill="{c}"/><circle cx="{bx + 0.8:.1f}" cy="{by - 5:.1f}" r="0.9" fill="#5A3A2A"/>')
    for bx in (96, 230, 410, 488):
        by = (y_on(beach[:7], bx) or 360) + 8
        c = rnd.choice(["#E8543E", "#F6C431", "#2E8AB8"])
        out.append(f'<path d="M {bx - 5} {by - 5} Q {bx} {by - 9} {bx + 5} {by - 5} Z" fill="{c}"/><line x1="{bx}" y1="{by - 6}" x2="{bx}" y2="{by}" stroke="#4A3A30" stroke-width="0.8"/>')
    # Avenida with the almond trees, then Botafogo's apartment towers below the overlook, west faces lit gold
    out.append('<path d="M -10 384 Q 300 368 610 382 L 610 392 Q 300 376 -10 396 Z" fill="#8A8A90"/>')
    rnd = random.Random(19)
    out.append("".join(f'<circle cx="{x:.1f}" cy="{390 - 0.035 * (300 - abs(300 - x)) + rnd.uniform(-2, 1):.1f}" r="{rnd.uniform(3.5, 5.5):.1f}" fill="{rnd.choice(["#3E6A40", "#4E7A48", "#2E5236"])}"/>' for x in range(-4, 606, 8)))
    rnd = random.Random(27)
    walls = [("#ECDCCC", "#FFE0B4", "#C8B4A8"), ("#DCCCC6", "#FAD4AC", "#B8A4A4"), ("#F2E2D0", "#FFE6C0", "#D0BCAE"), ("#CDBAB6", "#F4CCA6", "#A89494"),
             ("#E4C8B2", "#FFD2A0", "#C0A48E"), ("#F0D2C0", "#FFD8B0", "#D0B0A0")]
    for yb, k, hr in ((404, 0.85, (26, 46)), (414, 1.0, (18, 34))):
        x = -24 + rnd.uniform(-10, 0)
        while x < 620:
            w = rnd.uniform(16, 28) * k
            h = rnd.uniform(*hr) * k
            wall, side, roof = rnd.choice(walls)
            out.append(apartment(x, yb + rnd.uniform(-3, 3), w, h, 7 * k, wall, side, roof, rnd))
            x += w + 7 * k + rnd.uniform(-3, 5)
    out.append('<rect x="0" y="372" width="600" height="44" fill="#C89A9E" opacity="0.1"/>')
    # the overlook: a whitewashed parapet over the city, the wavy black-and-white pedra portuguesa underfoot
    out.append(Q([(-10, 416), (610, 414), (610, 444), (-10, 444)], f"url(#{u}-pave)"))
    for j in range(5):
        y = 418 + j * 5.5 + j * j * 0.5
        A = 1.6 + j * 0.9
        L = 22 + j * 6
        d = f"M -20 {y:.1f} " + " ".join(f"q {L / 4:.1f} {-A * 2:.1f} {L / 2:.1f} 0 t {L / 2:.1f} 0" for _ in range(int(640 / L) + 2))
        out.append(f'<path d="{d}" fill="none" stroke="#2A2626" stroke-width="{2.2 + j * 0.7:.1f}"/>')
    out.append('<rect x="-10" y="400" width="620" height="16" fill="#EADCC8"/><rect x="-10" y="398" width="620" height="4" fill="#FFF2DC"/>'
               '<rect x="-10" y="412" width="620" height="4" fill="#B8A49A"/>')
    out.append(dots(80, 71, (-10, 402, 610, 412), "#C8B4A4", r=(0.6, 1.4), opacity=(0.4, 0.8)))
    # a couple leaning together on the wall, watching the light go gold on the Sugarloaf
    out.append('<ellipse cx="166" cy="417" rx="30" ry="2.6" fill="#5A4A48" opacity="0.3"/>')
    out.append(person(178, 418, 56, "#2E5A7E", "#2A2A3A", skin="#9A6A4E", hair="#2A1A12", back=True, rim="#FFD49A", arms="none"))
    out.append(person(156, 418, 50, "#F0E4D2", "#E8543E", skin="#B07A5A", hair="#3A2016", back=True, long_hair=True, dress=True, rim="#FFD49A", arms="down"))
    out.append('<path d="M 173 374.5 Q 162 371 152.5 377.5" fill="none" stroke="#2E5A7E" stroke-width="3" stroke-linecap="round"/>'
               '<circle cx="152" cy="378" r="1.6" fill="#9A6A4E"/><path d="M 184 375 Q 187 386 186 394" fill="none" stroke="#2E5A7E" stroke-width="3" stroke-linecap="round"/>'
               '<circle cx="186" cy="395" r="1.6" fill="#9A6A4E"/>')
    out.append(coco_palm(58, 404, 250, 81, lean=0.12, L=110))
    # a bem-te-vi perched on the parapet
    out.append(bemtevi(262, 398, 0.62))
    # kites over Botafogo
    out.append(pipa(232, 214, 0.9, seed=1, string_to=(196, 370)))
    out.append(pipa(116, 236, 0.6, sail="#2E8A5A", cross="#FFFFFF", tail="#E8A030", seed=2))
    # a yellow ipê in full bloom arching in from the right, petals fallen on the pavement
    out.append(ipe_tree(574, 444, 190, 61, spread=(-80, 25)))
    out.append(dots(30, 72, (380, 418, 610, 444), "#F6C431", r=(1.2, 2.4), opacity=(0.8, 1)))
    out.append(dots(12, 73, (300, 400, 460, 410), "#F6C431", r=(1, 2), opacity=(0.8, 1)))
    # frigatebirds riding the updraft around the peak
    out.append(frigatebird(300, 132, 1.1, "#2E2E46", tilt=-8) + frigatebird(262, 160, 0.75, "#3E3E56", tilt=6) + frigatebird(512, 146, 0.85, "#2E2E46", tilt=4))
    return "\n".join(out)


# ================================================================ MACHU PICCHU — the citadel from the Guardhouse terraces, early morning
def inca_house(x, base, w, h, d, k, rnd, stone=None, side=None, dark="#34302E", gable=True, thatch=False):
    """Roofless Inca stone house seen from above-left: front wall with trapezoid openings, sunlit right gable,
    dark interior visible over the walls."""
    stone = stone or rnd.choice(["#8E8A82", "#9A958C", "#85817C", "#A09A90"])
    side = side or rnd.choice(["#D2CAB6", "#DCD4C0", "#C8C0AE"])
    out = []
    # interior floor seen over the walls (dark)
    out.append(Q([(x, base - h), (x + w, base - h), (x + w + d, base - h - d * 0.55), (x + d, base - h - d * 0.55)], dark, ' opacity="0.85"'))
    # back wall top lit
    out.append(Q([(x + d, base - h - d * 0.55), (x + w + d, base - h - d * 0.55), (x + w + d, base - h - d * 0.55 - 1.4 * k), (x + d, base - h - d * 0.55 - 1.4 * k)], side))
    # side (right) wall, sunlit, with a gable
    sp = [(x + w, base), (x + w, base - h), (x + w + d, base - h - d * 0.55), (x + w + d, base - d * 0.55)]
    out.append(Q(sp, side))
    if gable:
        gx = x + w + d / 2
        gy = base - h - d * 0.275
        out.append(Q([(x + w, base - h), (gx, gy - h * 0.55), (x + w + d, base - h - d * 0.55)], side))
        out.append(Q([(x + w, base - h + 0.1), (gx, gy - h * 0.55), (gx + 0.8 * k, gy - h * 0.55 + 0.6 * k), (x + w + 0.8 * k, base - h + 0.4 * k)], "#FFF6E2", ' opacity="0.6"'))
        if thatch:
            out.append(Q([(x - 1.5 * k, base - h + 1 * k), (gx - w - 1 * k, gy - h * 0.6 - 0.5 * k), (gx + 1 * k, gy - h * 0.6 - 0.5 * k), (x + w + d + 1.5 * k, base - h - d * 0.55 + 1 * k), (x + w + 1.5 * k, base - h + 1.5 * k)], "#B8904E"))
            out.append(Q([(gx - w - 1 * k, gy - h * 0.6 - 0.5 * k), (gx + 1 * k, gy - h * 0.6 - 0.5 * k), (x + w + d + 1.5 * k, base - h - d * 0.55 + 1 * k), (x + w + 1.5 * k, base - h + 1.5 * k)], "#E2BE72"))
            out.append(f'<g stroke="#8A6A3A" stroke-width="{0.5 * k:.1f}" opacity="0.6">' + "".join(
                f'<line x1="{x + w + 1.5 * k + j * d / 5:.1f}" y1="{base - h + 1.5 * k - j * d * 0.11:.1f}" x2="{gx + 1 * k - w * 0.02 + j * d / 10:.1f}" y2="{gy - h * 0.6:.1f}"/>' for j in range(5)) + "</g>")
    # front wall
    out.append(f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{stone}"/>')
    # stone courses
    rows = max(2, int(h / (1.6 * k)))
    out.append(f'<g stroke="#5E5A58" stroke-width="{max(0.4, 0.35 * k):.2f}" opacity="0.45">' + "".join(
        f'<line x1="{x:.1f}" y1="{base - h + (i + 1) * h / rows:.1f}" x2="{x + w:.1f}" y2="{base - h + (i + 1) * h / rows:.1f}"/>' for i in range(rows - 1)) + "</g>")
    # trapezoid openings
    nd = max(1, int(w / (7 * k)))
    for i in range(nd):
        cx_ = x + w * (i + 0.5) / nd
        top = base - h * 0.78
        bot = base if (i == nd // 2 and rnd.random() < 0.5) else base - h * 0.3
        out.append(Q([(cx_ - 1.6 * k, bot), (cx_ - 1.1 * k, top), (cx_ + 1.1 * k, top), (cx_ + 1.6 * k, bot)], dark))
    out.append(f'<line x1="{x + w:.1f}" y1="{base - h:.1f}" x2="{x + w:.1f}" y2="{base:.1f}" stroke="#FFF6E2" stroke-width="{0.7 * k:.1f}" opacity="0.8"/>')
    out.append(f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{0.9 * k:.1f}" fill="#E8E2D2"/>')
    return "".join(out)


def terrace_band(pts, h, grass_top, wall, wall_dark, seed, blocks=True):
    """One agricultural terrace: a stone retaining wall of height h under a curved grassy lip."""
    rnd = random.Random(seed)
    top = pts
    bot = [(x, y + h) for x, y in pts]
    out = [Q(top + bot[::-1], wall)]
    if blocks and h > 3:
        rows = max(1, int(h / 3.2))
        lines = []
        for r in range(1, rows + 1):
            yy = [(x, y + h * r / (rows + 1)) for x, y in pts]
            lines.append(f'<polyline points="{P(yy)}" fill="none"/>')
        out.append(f'<g stroke="{wall_dark}" stroke-width="0.7" opacity="0.5">{"".join(lines)}</g>')
        vs = []
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            L = math.hypot(xb - xa, yb - ya)
            for _ in range(int(L / 5)):
                t = rnd.random()
                vx, vy = xa + (xb - xa) * t, ya + (yb - ya) * t
                r = rnd.randrange(rows + 1)
                vs.append(f'<line x1="{vx:.1f}" y1="{vy + h * r / (rows + 1):.1f}" x2="{vx:.1f}" y2="{vy + h * (r + 1) / (rows + 1):.1f}"/>')
        out.append(f'<g stroke="{wall_dark}" stroke-width="0.7" opacity="0.45">{"".join(vs)}</g>')
    out.append(Q(bot + [(x, y + h + 2.2) for x, y in pts][::-1], wall_dark, ' opacity="0.35"'))
    out.append(f'<polyline points="{P(top)}" fill="none" stroke="{grass_top}" stroke-width="2.2" stroke-linejoin="round"/>')
    return "".join(out)


def llama(x, base, k, flip=False, wool="#F6EEE0", shade="#CDBEA6", deep="#A8967E", patch="#8A5A38", patch_shade="#5E3C26",
          face=None, rim="#FFF6DC", tassel="#E2384E", light=1):
    """Llama standing in profile facing left (flip=True faces right): long upright neck, banana ears with
    red yarn tassels, woolly scalloped belly, caramel saddle patch. light=+1 rim light on the right."""
    sx = -k if flip else k
    face = face or wool
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({sx:.3f} {k:.3f})">',
         '<ellipse cx="4" cy="0.5" rx="36" ry="3.6" fill="#24361E" opacity="0.32"/>']
    # far legs (in shade)
    g.append(f'<path d="M -13 -36 Q -12 -20 -12.4 -2 L -8.6 -2 Q -8 -20 -7 -34 Z" fill="{deep}"/>'
             f'<path d="M 19 -38 Q 23 -26 21 -14 Q 20 -8 21 -2 L 24.6 -2 Q 24 -10 25 -16 Q 27 -28 25 -38 Z" fill="{deep}"/>'
             '<path d="M -13 -2.6 L -8 -2.6 L -7.6 0.4 L -13.6 0.4 Z M 20.6 -2.6 L 25 -2.6 L 25.6 0.4 L 20 0.4 Z" fill="#3A2E28"/>')
    # body + neck as one woolly mass
    body = [(-21, -42), (-24, -58), (-26, -74), (-27, -86), (-21, -91), (-16, -84), (-14, -70), (-11, -61), (2, -62), (18, -62),
            (29, -59), (35, -51), (34, -41), (28, -34), (14, -31), (0, -31), (-13, -33)]
    g.append(f'<path d="{smooth(body)}" fill="{wool}"/>')
    # caramel saddle patch over the back
    g.append(f'<path d="{smooth([(-6, -61), (6, -63), (20, -63), (30, -59), (34, -50), (26, -46), (14, -48), (2, -50), (-6, -54)])}" fill="{patch}"/>')
    g.append(f'<path d="{smooth([(14, -48), (26, -46), (34, -50), (33, -44), (24, -42), (12, -44)])}" fill="{patch_shade}" opacity="0.6"/>')
    # belly shade with scalloped wool fringe
    g.append(f'<path d="M -20 -40 Q -6 -36 10 -37 Q 26 -38 34 -44 Q 33 -36 28 -34 L 14 -31 L 0 -31 L -13 -33 Z" fill="{shade}"/>')
    g.append('<g fill="' + shade + '">' + "".join(f'<circle cx="{-14 + i * 4.2:.1f}" cy="{-32.4 + abs(i - 5) * 0.12:.1f}" r="2.3"/>' for i in range(11)) + "</g>")
    # neck front shade
    g.append(f'<path d="M -21 -42 Q -24 -58 -26 -74 Q -27 -82 -26 -86 Q -22 -70 -19 -58 Q -17 -48 -14 -40 Z" fill="{shade}" opacity="0.8"/>')
    # wool curls
    g.append(f'<g fill="none" stroke="{deep}" stroke-width="0.9" opacity="0.7" stroke-linecap="round">'
             + "".join(f'<path d="M {cx:.1f} {cy:.1f} q 1.6 -1.6 3 0"/>' for cx, cy in
                       ((-20, -60), (-18, -70), (-22, -76), (-6, -44), (4, -40), (16, -40), (-12, -46), (-20, -50), (24, -40))) + "</g>")
    # near legs, a woolly thigh top
    g.append(f'<path d="M -19 -38 Q -18 -20 -18.4 -2 L -14 -2 Q -13.6 -20 -12 -36 Z" fill="{wool}"/>'
             f'<path d="M 22 -40 Q 28 -28 26 -16 Q 25 -9 26 -2 L 30 -2 Q 29.4 -10 30.6 -17 Q 33 -30 30 -40 Z" fill="{wool}"/>'
             f'<path d="M -16 -38 Q -15.6 -20 -15.6 -2 L -14 -2 Q -13.6 -20 -12 -36 Z" fill="{shade}" opacity="0.7"/>'
             '<path d="M -19 -2.6 L -13.6 -2.6 L -13 0.6 L -19.8 0.6 Z M 25.6 -2.6 L 30.4 -2.6 L 31 0.6 L 25 0.6 Z" fill="#3A2E28"/>')
    # short tail flicked up
    g.append(f'<path d="M 33 -55 Q 40 -60 40 -52 Q 39 -47 35 -48 Z" fill="{patch}"/>')
    # head
    head = [(-21, -88), (-23, -96), (-30, -98.5), (-38, -96), (-45, -92.5), (-48, -89), (-46, -85.5), (-38, -84.5), (-30, -85), (-25, -84)]
    g.append(f'<path d="{smooth(head)}" fill="{face}"/>')
    g.append(f'<path d="M -48 -89 Q -46 -85.5 -38 -84.5 Q -30 -85 -25 -84 Q -32 -87 -40 -87.4 Q -45 -87.6 -48 -89 Z" fill="{shade}"/>')
    g.append('<ellipse cx="-46" cy="-90.6" rx="1.4" ry="1" fill="#3A2A26"/><path d="M -47.4 -87.6 Q -44 -86.8 -41 -87.6" stroke="#3A2A26" stroke-width="0.8" fill="none"/>'
             '<ellipse cx="-31.5" cy="-93" rx="2.1" ry="1.9" fill="#1E1A1A"/><circle cx="-32.1" cy="-93.6" r="0.7" fill="#FFFFFF"/>'
             '<path d="M -34.6 -95 Q -31.6 -96.6 -28.8 -95" stroke="#3A2A26" stroke-width="0.7" fill="none"/>')
    # banana ears curving in, with red yarn tassels
    g.append(f'<path d="M -23 -96 C -21 -103 -19 -108 -21.5 -113 C -25 -108 -26.6 -102 -26.4 -97 Z" fill="{wool}"/>'
             f'<path d="M -27.4 -97.4 C -28.6 -104 -30.6 -109 -34 -112 C -34 -106 -32.8 -101 -31 -97 Z" fill="{shade}"/>'
             '<path d="M -23.4 -99 C -22.6 -104 -22 -107 -22.6 -110" stroke="#C8A898" stroke-width="1" fill="none"/>')
    for ex, ey in ((-21.6, -107), (-31.6, -107)):
        g.append(f'<g fill="{tassel}"><circle cx="{ex - 1:.1f}" cy="{ey + 1:.1f}" r="2.2"/><path d="M {ex - 2.6:.1f} {ey + 2:.1f} l -0.8 6 l 1.6 0.2 Z M {ex - 0.6:.1f} {ey + 2.4:.1f} l 0.6 5.6 l 1.4 -0.4 Z"/></g>')
    # rim light from the sun behind-right
    if light:
        g.append(f'<path d="M -11 -61.6 L 18 -62.6 Q 29 -60 35 -51 Q 35.6 -45 34 -41" fill="none" stroke="{rim}" stroke-width="1.8" stroke-linecap="round" opacity="0.85"/>'
                 f'<path d="M -16 -84 Q -14 -70 -11.6 -62" fill="none" stroke="{rim}" stroke-width="1.5" opacity="0.85"/>'
                 f'<path d="M -21 -113 Q -19 -107 -22.6 -97" fill="none" stroke="{rim}" stroke-width="1" opacity="0.8"/>')
    g.append("</g>")
    return "".join(g)


def jungle_peak(u, outline, seed, shade, mid, lit, lx0, lx1, ribs=("#24463A", "#8EB27A"), n_ribs=None, dots_col="#1E3A2E", rim=None, rim_range=None, cliffs=None, rib_op=(0.25, 0.55)):
    """Steep forested mountain painted with a lit-side gradient, ribs running down the slope and fine canopy texture."""
    xs = [x for x, _ in outline]
    ys = [y for _, y in outline]
    box = (min(xs), min(ys), max(xs), max(ys))
    out = [defs(lg(f"{u}-g", [(0, shade), (0.5, mid), (1, lit)], lx0, 0, lx1, 0, units="userSpaceOnUse"), clip(f"{u}-c", outline)),
           Q(outline, f"url(#{u}-g)")]
    area = (box[2] - box[0]) * (box[3] - box[1])
    g = [streaks(n_ribs or int(area / 120), seed, (box[0], box[1] - 20, box[2], box[3]), list(ribs), w=(1.2, 4), length=(30, 110), opacity=rib_op, slant=0.35)]
    if cliffs:
        g.append(cliffs)
    g.append(dots(int(area / 55), seed + 1, box, dots_col, r=(0.9, 2.4), opacity=(0.15, 0.4)))
    g.append(dots(int(area / 110), seed + 2, box, ribs[1], r=(0.9, 2.2), opacity=(0.2, 0.5)))
    out.append(f'<g clip-path="url(#{u}-c)">{"".join(g)}</g>')
    if rim:
        i0, i1 = rim_range
        out.append(f'<polyline points="{P(outline[i0:i1])}" fill="none" stroke="{rim}" stroke-width="2" stroke-linejoin="round" opacity="0.85"/>')
    return "".join(out)


STONE = dict(front="#A09A8E", lit="#D4CCB8", cap="#E6DFCC", inner="#8E897E", floor="#5E6A4C", floor_dark="#465238", dark="#36322E", line="#625C54")


def room_row(x0, x1, base, h, d, k, seed, gables=0.5, doors=0.5, st=STONE, ruin=0.0):
    """A row of roofless Inca rooms sharing walls, in oblique projection (depth runs up-right by (d, -0.55 d)).
    Draws the grassy floors, the inner face of the back wall, the sunlit east faces of the partition walls with
    their steep gables, then the front wall with its trapezoidal doorways and niches."""
    rnd = random.Random(seed)
    dy = 0.55 * d
    xs = [x0]
    while xs[-1] < x1 - 6 * k:
        xs.append(min(x1, xs[-1] + rnd.uniform(9, 17) * k))
    if xs[-1] < x1:
        xs[-1] = x1
    out = []
    # floors (we look down into the rooms) and the inner face of the back wall
    out.append(Q([(x0, base), (x1, base), (x1 + d, base - dy), (x0 + d, base - dy)], st["floor"]))
    out.append(Q([(x0, base), (x1, base), (x1 + d * 0.5, base - dy * 0.5), (x0 + d * 0.5, base - dy * 0.5)], st["floor_dark"], ' opacity="0.5"'))
    out.append(Q([(x0 + d, base - dy), (x1 + d, base - dy), (x1 + d, base - dy - h), (x0 + d, base - dy - h)], st["inner"]))
    out.append(f'<g stroke="{st["line"]}" stroke-width="{max(0.4, 0.4 * k):.2f}" opacity="0.45">' + "".join(
        f'<line x1="{x0 + d:.1f}" y1="{base - dy - h * j / 4:.1f}" x2="{x1 + d:.1f}" y2="{base - dy - h * j / 4:.1f}"/>' for j in (1, 2, 3)) + "</g>")
    out.append(Q([(x0 + d, base - dy - h), (x1 + d, base - dy - h), (x1 + d + 1.2 * k, base - dy - h - 0.7 * k), (x0 + d + 1.2 * k, base - dy - h - 0.7 * k)], st["cap"]))
    # niches in the back wall
    for xa, xb in zip(xs, xs[1:]):
        for j in range(max(1, int((xb - xa) / (5 * k)))):
            cx_ = xa + d + (j + 0.6) * 5 * k
            if cx_ < xb + d - 2 * k and rnd.random() < 0.7:
                out.append(Q([(cx_ - 1.1 * k, base - dy - h * 0.25), (cx_ - 0.8 * k, base - dy - h * 0.72), (cx_ + 0.8 * k, base - dy - h * 0.72), (cx_ + 1.1 * k, base - dy - h * 0.25)], st["dark"], ' opacity="0.7"'))
    # partition walls, east faces in morning sun, many with a gable
    for i, xs_ in enumerate(xs):
        gh = 0
        if 0 < i < len(xs) - 1 and rnd.random() < gables:
            gh = h * rnd.uniform(0.8, 1.2)
        face = [(xs_, base), (xs_, base - h), (xs_ + d * 0.5, base - dy * 0.5 - h - gh), (xs_ + d, base - dy - h), (xs_ + d, base - dy)]
        out.append(Q(face, st["lit"]))
        out.append(f'<polyline points="{P(face[1:4])}" fill="none" stroke="{st["cap"]}" stroke-width="{max(0.8, 0.9 * k):.1f}" stroke-linejoin="round"/>')
        out.append(f'<line x1="{xs_:.1f}" y1="{base:.1f}" x2="{xs_:.1f}" y2="{base - h:.1f}" stroke="{st["line"]}" stroke-width="{max(0.5, 0.5 * k):.1f}" opacity="0.6"/>')
        if gh and rnd.random() < 0.5:
            wx, wy = xs_ + d * 0.5, base - dy * 0.5 - h * 0.85
            out.append(Q([(wx - 0.6 * k, wy + 1.2 * k), (wx - 0.4 * k, wy - 1.0 * k), (wx + 0.4 * k, wy - 1.2 * k), (wx + 0.6 * k, wy + 0.9 * k)], st["dark"], ' opacity="0.7"'))
    # front wall (south face, half lit) with trapezoid doorways and windows
    out.append(f'<rect x="{x0:.1f}" y="{base - h:.1f}" width="{x1 - x0:.1f}" height="{h:.1f}" fill="{st["front"]}"/>')
    rows = max(2, int(h / (1.8 * k)))
    out.append(f'<g stroke="{st["line"]}" stroke-width="{max(0.4, 0.38 * k):.2f}" opacity="0.5">' + "".join(
        f'<line x1="{x0:.1f}" y1="{base - h + (j + 1) * h / rows:.1f}" x2="{x1:.1f}" y2="{base - h + (j + 1) * h / rows:.1f}"/>' for j in range(rows - 1)) + "</g>")
    for xa, xb in zip(xs, xs[1:]):
        cx_ = (xa + xb) / 2 + rnd.uniform(-1, 1) * k
        if rnd.random() < doors:
            out.append(Q([(cx_ - 1.9 * k, base), (cx_ - 1.3 * k, base - h * 0.8), (cx_ + 1.3 * k, base - h * 0.8), (cx_ + 1.9 * k, base)], st["dark"]))
            out.append(Q([(cx_ - 1.3 * k, base - h * 0.8), (cx_ + 1.3 * k, base - h * 0.8), (cx_ + 1.5 * k, base - h * 0.8 + 0.8 * k), (cx_ - 1.5 * k, base - h * 0.8 + 0.8 * k)], st["cap"], ' opacity="0.8"'))
        else:
            out.append(Q([(cx_ - 1.2 * k, base - h * 0.2), (cx_ - 0.9 * k, base - h * 0.68), (cx_ + 0.9 * k, base - h * 0.68), (cx_ + 1.2 * k, base - h * 0.2)], st["dark"]))
    out.append(f'<rect x="{x0:.1f}" y="{base - h - 0.6 * k:.1f}" width="{x1 - x0:.1f}" height="{1.0 * k:.1f}" fill="{st["cap"]}"/>')
    # the end wall on the right, fully sunlit
    out.append(Q([(x1, base), (x1, base - h), (x1 + d, base - dy - h), (x1 + d, base - dy)], st["lit"]))
    out.append(f'<line x1="{x1:.1f}" y1="{base:.1f}" x2="{x1:.1f}" y2="{base - h:.1f}" stroke="#FFFFFF" stroke-width="{max(0.6, 0.6 * k):.1f}" opacity="0.7"/>')
    if ruin:
        out.append(dots(int((x1 - x0) * ruin), seed + 5, (x0, base - h - dy, x1 + d, base), "#7E9A5A", r=(0.6, 1.4), opacity=(0.5, 0.9)))
    return "".join(out)


def platform(x0, x1, top, h, seed, k=1.0, wall="#A8A294", dark="#6A645A", lit="#D8D0BE", grass_top="#8EB45A", grass_lip="#B8D47A", slope=0.0):
    """A terrace platform's retaining wall: fitted granite courses, a grassy lip and a shadow at its foot."""
    rnd = random.Random(seed)
    y0, y1 = top, top + slope
    out = [Q([(x0, y0), (x1, y1), (x1, y1 + h), (x0, y0 + h)], wall)]
    rows = max(1, int(h / (2.4 * k)))
    for r in range(1, rows + 1):
        t = r / (rows + 1)
        out.append(f'<line x1="{x0:.1f}" y1="{y0 + h * t:.1f}" x2="{x1:.1f}" y2="{y1 + h * t:.1f}" stroke="{dark}" stroke-width="{max(0.4, 0.45 * k):.2f}" opacity="0.5"/>')
    vs = []
    for r in range(rows + 1):
        x = x0 + rnd.uniform(0, 5 * k)
        while x < x1:
            ta, tb = r / (rows + 1), (r + 1) / (rows + 1)
            yy = y0 + (y1 - y0) * (x - x0) / max(1, x1 - x0)
            vs.append(f'<line x1="{x:.1f}" y1="{yy + h * ta:.1f}" x2="{x:.1f}" y2="{yy + h * tb:.1f}"/>')
            x += rnd.uniform(3.5, 7) * k
    out.append(f'<g stroke="{dark}" stroke-width="{max(0.4, 0.4 * k):.2f}" opacity="0.4">{"".join(vs)}</g>')
    out.append(Q([(x0, y0), (x1, y1), (x1, y1 + h * 0.3), (x0, y0 + h * 0.3)], lit, ' opacity="0.35"'))
    out.append(Q([(x0, y0 + h), (x1, y1 + h), (x1, y1 + h + 1.6 * k), (x0, y0 + h + 1.6 * k)], "#2E3A26", ' opacity="0.3"'))
    out.append(f'<line x1="{x0:.1f}" y1="{y0 - 0.6 * k:.1f}" x2="{x1:.1f}" y2="{y1 - 0.6 * k:.1f}" stroke="{grass_lip}" stroke-width="{1.6 * k:.1f}"/>')
    return "".join(out)


def sector(x0, x1, y0, y1, k, seed, gap=0.2, grow=0.0, skip=None):
    """Fill a sector of the citadel with stepped rows of room compounds on platforms, back to front.
    Rows get bigger toward the front by `grow`; gaps between compounds are alleys and stairways."""
    rnd = random.Random(seed)
    out = []
    y = y0
    while y <= y1:
        t = (y - y0) / max(1, y1 - y0)
        kk = k * (1 + grow * t)
        h, d = 4.6 * kk, 11 * kk
        out.append(platform(x0 - 4, x1 + 4, y, 3.4 * kk, seed + int(y), k=kk))
        x = x0 + rnd.uniform(0, 8) * kk
        while x < x1 - 14 * kk:
            L = rnd.uniform(26, 60) * kk
            xb = min(x1 - d * 0.6, x + L)
            if not (skip and skip[0] - d < xb and x < skip[1]):
                out.append(room_row(x, xb, y, h * rnd.uniform(0.85, 1.15), d, kk, seed + int(x * 7 + y), gables=0.55, doors=0.45))
            x = xb + (rnd.uniform(4, 9) * kk if rnd.random() < gap * 3 else d + 1 * kk)
        y += h + 0.55 * d + 3.4 * kk + 0.5
    return "".join(out)


def machu_picchu():
    u = "mp"
    out = [defs(
        lg(f"{u}-sky", [(0, "#6496C4"), (0.4, "#A4C4DA"), (0.75, "#E0E8E2"), (1, "#F6ECD6")], 0, 0, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#90AAC0"), (1, "#C4D2DA")], 0, 140, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#F2F0EA", 0), (1, "#F2F0EA", 0.85)], 0, 170, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-lawn", [(0, "#A8CA6E"), (1, "#86B252")], 0, 300, 0, 336, units="userSpaceOnUse"),
        lg(f"{u}-sad", [(0, "#7EA654"), (1, "#5E8A42")], 0, 290, 0, 380, units="userSpaceOnUse"),
        lg(f"{u}-slope", [(0, "#86AE52"), (1, "#4E7A3A")], 0, 290, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-tread", [(0, "#9CC260"), (1, "#7AA44C")], 0, 0, 0, 1),
    )]
    out.append(f'<rect width="600" height="330" fill="url(#{u}-sky)"/>')
    out.append(glow(612, 30, 330, "#FFF0C8", f"{u}-sun", 0.8))
    out.append(cumulus(f"{u}-c1", 150, 112, 170, 42, 12, "#FFFFFF", "#EEF2F4", "#B4C4D2", hi="#FFFFFF", hi_op=0.7, light=1))
    out.append(cumulus(f"{u}-c2", 540, 138, 100, 24, 14, "#FFFFFF", "#F2F2EE", "#BCC8D4", hi="#FFFFFF", light=1))
    # far Andean ranges, pale and blue; the snowy shoulder of Salkantay's range far off on the left
    poly, _ = ridge_poly([(-10, 200), (40, 172), (90, 190), (150, 156), (210, 186), (260, 176), (300, 206), (350, 198), (410, 168), (470, 182), (530, 152), (610, 176)], 51, base=330, amp=10, fill=f"url(#{u}-far)")
    out.append(poly)
    out.append(Q([(130, 164), (150, 156), (166, 166), (158, 168), (150, 162), (140, 170)], "#EEF2F4", ' opacity="0.9"'))
    poly, _ = ridge_poly([(-10, 236), (60, 220), (130, 238), (200, 230), (280, 252), (330, 262)], 57, base=330, amp=6, fill="#A6BAC4")
    out.append(poly)
    out.append(f'<rect x="0" y="170" width="600" height="130" fill="url(#{u}-haze)"/>')
    # mid ridges framing the Urubamba gorge, blue-green with distance
    left_r = [(-10, 222), (30, 214), (80, 226), (130, 240), (180, 256), (230, 276), (270, 296), (290, 330), (-10, 330)]
    out.append(jungle_peak(f"{u}-lr", left_r, 52, "#5A8076", "#78988C", "#A8C2A8", 0, 300, ribs=("#4E7268", "#9CB8A4"), rib_op=(0.12, 0.3), n_ribs=50))
    right_r = [(470, 330), (482, 270), (506, 226), (536, 200), (572, 188), (610, 192), (610, 330)]
    out.append(jungle_peak(f"{u}-rr", right_r, 53, "#5A8076", "#7E9E90", "#BCD2B4", 470, 610, ribs=("#4E7268", "#A8C4A8"), rib_op=(0.12, 0.3), n_ribs=40))
    out.append(mist(120, 262, 170, 18, "#FFFFFF", f"{u}-m0", 0.75))
    # Huayna Picchu, sunlit from the east (right), with the zig-zag terraces near its summit
    hp = [(286, 320), (306, 290), (324, 254), (340, 214), (354, 178), (366, 146), (377, 122), (387, 106), (396, 98), (404, 97), (412, 104),
          (420, 120), (429, 146), (440, 176), (453, 204), (470, 230), (490, 252), (514, 272), (540, 290), (566, 320)]
    hp = [hp[0]] + rough(hp[1:-1], 61, amp=3, depth=2) + [hp[-1]]
    rnd = random.Random(62)
    cl = "".join(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-4, 2):.1f} {rnd.uniform(12, 30):.1f} l {rnd.uniform(3, 7):.1f} {rnd.uniform(-4, 4):.1f} Z" fill="{rnd.choice(["#8E9890", "#AEB4A8", "#6E7A74"])}" opacity="0.7"/>'
                 for x, y in [(rnd.uniform(360, 420), rnd.uniform(110, 200)) for _ in range(26)])
    out.append(jungle_peak(f"{u}-hp", hp, 54, "#2A4A3C", "#4E7A5C", "#A6C482", 340, 470, ribs=("#1E3A30", "#B8D08E"), cliffs=cl, rim="#FFF2CC", rim_range=(9, 16)))
    out.append('<g stroke="#DCD8C6" stroke-width="1.5" opacity="0.9" stroke-linecap="round"><path d="M 394 110 L 408 110"/><path d="M 390 116 L 412 117"/><path d="M 397 104 L 405 104"/><path d="M 388 123 L 410 124"/></g>')
    hc = [(262, 330), (274, 300), (288, 280), (302, 270), (318, 272), (332, 288), (346, 330)]
    out.append(jungle_peak(f"{u}-hc", hc, 55, "#2A4C3E", "#467058", "#90B47E", 262, 346, ribs=("#1E3A30", "#A8C88A")))
    # morning cloud drifting through the gorge and across the flank of the peak
    out.append(cumulus(f"{u}-c3", 486, 262, 130, 24, 16, "#FFFFFF", "#F2F4F2", "#C4D0D6", hi="#FFFFFF", light=1))
    out.append(mist(470, 268, 120, 14, "#FFFFFF", f"{u}-m1", 0.8))
    out.append(mist(230, 296, 130, 12, "#FFFFFF", f"{u}-m2", 0.75))
    # the saddle the citadel sits on
    sad = [(90, 380), (120, 302), (200, 296), (300, 297), (380, 295), (460, 298), (540, 303), (610, 308), (610, 380)]
    out.append(Q(sad, f"url(#{u}-sad)"))
    out.append(mist(330, 297, 260, 7, "#FFFFFF", f"{u}-m3", 0.55))
    # --- the citadel, back to front ---
    # Sacred Rock sector at the foot of Huayna Picchu
    out.append(platform(300, 600, 304, 3, 70, k=0.55))
    out.append(sector(306, 596, 296, 306, 0.5, 71, gap=0.25))
    # Intihuatana hill on the left: stepped platforms with the carved stone on top
    for i in range(6):
        w = 112 - i * 16
        y = 334 - i * 7
        out.append(platform(178 - w / 2, 178 + w / 2, y, 6, 73 + i, k=0.8, slope=0))
        out.append(Q([(178 - w / 2, y), (178 + w / 2, y), (178 + w / 2 - 6, y - 1.6), (178 - w / 2 + 6, y - 1.6)], "#94BC5E"))
    out.append(room_row(160, 190, 293, 2.6, 5, 0.6, 79, gables=0, doors=0))
    out.append('<path d="M 175 285 L 183 285 L 184 290 L 174 290 Z" fill="#D8D2C4"/><path d="M 180 280 L 183 280 L 183 285 L 180 285 Z" fill="#EEE8DA"/><rect x="172" y="289" width="14" height="2" fill="#8E8A80"/>')
    # the main plaza: two mown lawns stepping down between the two halves of the city
    out.append(Q([(246, 342), (270, 314), (418, 316), (436, 342)], f"url(#{u}-lawn)"))
    out.append(platform(258, 428, 327, 2.4, 81, k=0.6, slope=0.4))
    out.append('<g stroke="#C4DE8E" stroke-width="2" opacity="0.4">' + "".join(f'<line x1="{252 + i * 20}" y1="{340}" x2="{272 + i * 16.6}" y2="{316}"/>' for i in range(9)) + "</g>")
    rnd = random.Random(82)
    for _ in range(8):
        px, py = rnd.uniform(280, 420), rnd.uniform(320, 338)
        c = rnd.choice(["#E8543E", "#2E5A8E", "#F2C230", "#2A2A3A", "#C83A6A"])
        out.append(f'<rect x="{px:.1f}" y="{py - 3.4:.1f}" width="1.6" height="3.4" fill="{c}"/><circle cx="{px + 0.8:.1f}" cy="{py - 4.2:.1f}" r="0.8" fill="#4A3020"/>')
    # western (royal / temple) sector below the Intihuatana
    out.append(sector(108, 250, 330, 352, 0.85, 85, gap=0.2))
    # eastern urban sector: tight compounds stepping down to the right
    out.append(sector(424, 610, 312, 366, 0.72, 86, gap=0.18, grow=0.45))
    # near row below the plaza, one house with a reconstructed thatched roof
    out.append(sector(196, 452, 348, 352, 1.05, 95, gap=0.12, skip=(300, 340)))
    out.append(platform(196, 300, 368, 3.6, 97, k=1.05) + platform(344, 456, 368, 3.6, 98, k=1.05))
    out.append(room_row(200, 296, 368, 5, 11.5, 1.05, 99, gables=0.6) + room_row(346, 440, 368, 5, 11.5, 1.05, 100, gables=0.6))
    tx, tb = 306, 368
    out.append(Q([(tx, tb), (tx + 24, tb), (tx + 24, tb - 8), (tx, tb - 8)], STONE["front"]))
    out.append(Q([(tx + 24, tb), (tx + 24, tb - 8), (tx + 31, tb - 12), (tx + 31, tb - 4)], STONE["lit"]))
    out.append(Q([(tx - 2, tb - 7), (tx + 3.5, tb - 21), (tx + 30, tb - 24), (tx + 26, tb - 7)], "#B08A4C"))
    out.append(Q([(tx + 26, tb - 7), (tx + 30, tb - 24), (tx + 33.5, tb - 10)], "#E4C27A"))
    out.append('<g stroke="#7E6034" stroke-width="0.8" opacity="0.6">' + "".join(f'<line x1="{tx + i * 4:.1f}" y1="{tb - 7:.1f}" x2="{tx + 4 + i * 3.8:.1f}" y2="{tb - 21 - i * 0.4:.1f}"/>' for i in range(7)) + "</g>")
    out.append(Q([(tx + 10, tb), (tx + 11, tb - 6), (tx + 14, tb - 6), (tx + 15, tb)], STONE["dark"]))
    # morning sun breaking through onto the citadel
    out.append(glow(400, 330, 210, "#FFF0C8", f"{u}-lit", 0.35))
    # terraces wrapping the citadel below
    out.append(Q([(140, 373), (610, 373), (610, 444), (140, 444)], "#76A24C"))
    for i in range(5):
        y = 372 + i * 9
        pts = rough([(150 + i * 12, y), (330, y + 2), (450, y + 3), (610, y + 4)], 70 + i, amp=1.0, depth=2)
        out.append(Q(pts + [(610, y + 11), (150 + i * 12, y + 11)], "#86B054" if i % 2 else "#7EA84E"))
        out.append(terrace_band(pts, 3 + i * 0.7, "#B4D27A", "#A8A498", "#605A52", 80 + i))
    # foreground: the great agricultural terraces curving down from the Guardhouse
    out.append(Q([(-10, 444), (-10, 288), (60, 298), (130, 318), (172, 340), (204, 380), (232, 420), (244, 444)], f"url(#{u}-slope)"))
    for i in range(8):
        y0 = 292 + i * 17 + i * i * 0.9
        x1 = 160 + i * 14
        pts = [(-10, y0)]
        for j in range(1, 9):
            t = j / 8
            pts.append((-10 + (x1 + 10) * t, y0 + (6 + i * 2.4) * t * t + 6 * t))
        h_ = 4 + i * 1.5
        nxt = 292 + (i + 1) * 17 + (i + 1) ** 2 * 0.9
        tread = [(x, y + h_) for x, y in pts] + [(x1 + 20, nxt + 20), (-10, nxt)]
        out.append(Q(tread, "#86B056" if i % 2 else "#7EA84C"))
        out.append(f'<polyline points="{P([(x, y + h_ + 2.4 + i * 0.3) for x, y in pts])}" fill="none" stroke="#3E5E2E" stroke-width="{1.6 + i * 0.3:.1f}" opacity="0.35"/>')
        out.append(f'<polyline points="{P([(x, y - 1) for x, y in pts])}" fill="none" stroke="#B8D480" stroke-width="{2 + i * 0.5:.1f}" opacity="0.7"/>')
        out.append(terrace_band(pts, h_, "#CDE290", "#B2AC9C", "#5E5850", 100 + i))
        out.append(grass(int(10 + i * 3), 140 + i, (-10, y0 + h_ + 3, x1 * 0.8, y0 + h_ + 10 + i), ["#A8C86A", "#5E8A3E", "#C8DC8E"], h=(2, 4 + i * 0.6), sw=1.0))
    out.append(f'<defs>{lg(f"{u}-cs", [(0, "#1E3A2A", 0), (1, "#1E3A2A", 0.32)], 0, 330, 0, 444, units="userSpaceOnUse")}</defs>')
    out.append(Q([(-10, 444), (-10, 300), (60, 310), (130, 330), (172, 350), (204, 390), (232, 430), (244, 444)], f"url(#{u}-cs)"))
    # a hiker pausing on the terraces with the view
    out.append(person(118, 349, 15, "#D8402E", "#2E3A4A", skin="#B0805E", hair="#2A1E18", hat="#E8D8B8", rim="#FFF2D0"))
    # right foreground: a grassy terrace where the llamas graze
    rs = [(226, 444), (286, 412), (360, 396), (450, 388), (530, 384), (610, 382), (610, 444)]
    out.append(Q(rs, "#6E9A48"))
    out.append(f'<polyline points="{P(rs[1:6])}" fill="none" stroke="#B8D480" stroke-width="2.4" opacity="0.8"/>')
    out.append(grass(140, 120, (290, 392, 610, 444), ["#A8C86A", "#5E8A3E", "#C8DC8E"], h=(4, 11), sw=1.4))
    out.append(llama(566, 400, 0.42, flip=True, wool="#8A5A3A", shade="#6A4430", deep="#4E3222", patch="#5E3A26", patch_shade="#3E2618", face="#8A5A3A", rim="#F2C890"))
    out.append(llama(446, 432, 1.08))
    out.append(grass(40, 121, (380, 426, 520, 440), ["#A8C86A", "#5E8A3E", "#C8DC8E"], h=(4, 9), sw=1.4))
    # an Andean condor gliding high over the gorge
    out.append('<g transform="translate(236 150) rotate(-4) scale(0.9)" fill="#2E3440"><path d="M 0 0 C -10 -4 -24 -6 -40 -2 L -44 1 L -38 0 L -40 3 L -34 2 L -30 4 C -18 3 -8 2 0 3 Z"/>'
               '<path d="M 0 0 C 10 -4 24 -6 40 -2 L 44 1 L 38 0 L 40 3 L 34 2 L 30 4 C 18 3 8 2 0 3 Z"/><path d="M -3 -1 L 3 -1 L 2 8 L -2 8 Z"/>'
               '<path d="M -12 -0.5 L 12 -0.5 L 9 1.5 L -9 1.5 Z" fill="#F2EEE6"/><circle cx="0" cy="-3" r="2" fill="#C88A7A"/></g>')
    return "\n".join(out)


# ================================================================ HAVANA — a pastel street running down to the Malecón, late afternoon
def hv_ground(Z):
    """Street level (m): flat near the corner, then dropping gently toward the sea."""
    return -0.11 * (min(max(Z, 14), 50) - 14)


def vintage_car(x, base, L, body="#2EB5AE", body_dark="#16706E", upper="#F6EEDC", seat="#C8343A", rim="#FFE6B0", flip=False,
                driver=True, uid="car"):
    """Generic late-1950s convertible in profile (facing right): long body with tail fins, a chrome spear with a
    cream insert on the rear flank, skirted rear wheel, whitewall tyres, wrap-around windscreen, red leather seats."""
    k = L / 100
    sx = -k if flip else k
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({sx:.3f} {k:.3f})">']
    g.append(f'<defs>{lg(uid + "-b", [(0, mix(body, "#FFFFFF", 0.45)), (0.25, body), (0.75, body), (1, body_dark)], 0, 0, 0, 1)}'
             f'{lg(uid + "-ch", [(0, "#FFFFFF"), (0.45, "#C4CED6"), (0.55, "#7A8692"), (1, "#E8EEF2")], 0, 0, 0, 1)}</defs>')
    g.append('<ellipse cx="50" cy="0.4" rx="54" ry="2.6" fill="#1E1A28" opacity="0.45"/>')
    # seats, folded top, people (behind the body)
    g.append(f'<path d="M 30 -20 L 31 -26 Q 38 -28.4 45 -26 L 46 -20 Z M 50 -20 L 51 -27 Q 57 -29.4 63 -27 L 63 -20 Z" fill="{seat}"/>'
             '<path d="M 31 -26 Q 38 -28.4 45 -26 M 51 -27 Q 57 -29.4 63 -27" fill="none" stroke="#F07070" stroke-width="0.8"/>'
             f'<path d="M 16 -20.6 Q 17 -25.4 22 -25.6 L 30 -25 L 30 -20.6 Z" fill="{upper}"/><path d="M 17 -23 L 30 -22.8" stroke="#C8BCA8" stroke-width="0.6"/>')
    if driver:
        g.append('<path d="M 53 -20 L 53 -30 Q 57.6 -33.4 62 -30 L 62.6 -20 Z" fill="#F4F2EC"/><path d="M 57.6 -33 L 57.6 -26" stroke="#D8D4CA" stroke-width="0.6"/>'
                 '<rect x="56.2" y="-35.4" width="2.8" height="3" fill="#7A4A32"/><circle cx="57.6" cy="-37.2" r="3.4" fill="#7A4A32"/>'
                 '<ellipse cx="57.6" cy="-39.6" rx="6" ry="1.3" fill="#E8D49A"/><path d="M 54.4 -39.6 Q 54.4 -44 57.6 -44 Q 60.8 -44 60.8 -39.6 Z" fill="#E8D49A"/>'
                 '<rect x="54.4" y="-41" width="6.4" height="1.1" fill="#2A2A3A"/>'
                 '<path d="M 61 -29 Q 66 -27 68 -24" stroke="#F4F2EC" stroke-width="2.4" fill="none" stroke-linecap="round"/><circle cx="68.6" cy="-23.6" r="1.4" fill="#7A4A32"/>'
                 '<ellipse cx="67.6" cy="-24" rx="1" ry="3.4" fill="none" stroke="#2A2A30" stroke-width="1"/>')
    g.append('<path d="M 65 -20.6 L 62.6 -32 L 66 -32.6 L 69.6 -20.6 Z" fill="#CFEAF2" opacity="0.5"/>'
             '<path d="M 65 -20.6 L 62.6 -32 L 66.2 -32.6 L 69.8 -20.6" fill="none" stroke="#EEF2F4" stroke-width="1"/>'
             '<rect x="63.4" y="-33.4" width="3" height="1.2" fill="#C4CED6"/>')
    # body: rear fin on the left, long hood to the right, wheel arches cut out below
    outline = ("M 1 -5 L 0 -12 Q 0 -18 3 -20.6 L 11 -23.2 L 15 -20.8 L 64 -20.8 Q 82 -21 91 -19.6 Q 98 -18 99.6 -13 L 100 -5 "
               "L 87.6 -5 A 8.8 8.8 0 0 0 70 -5 L 31 -5 A 8.8 8.8 0 0 0 13.4 -5 Z")
    g.append(f'<path d="{outline}" fill="url(#{uid}-b)"/>')
    # sculpted side: shadowed lower flank, sky reflection along the top
    g.append(f'<path d="M 1 -9 L 100 -9.4 L 100 -5 L 87.6 -5 A 8.8 8.8 0 0 0 70 -5 L 31 -5 A 8.8 8.8 0 0 0 13.4 -5 L 1 -5 Z" fill="{body_dark}" opacity="0.35"/>')
    g.append('<path d="M 15 -20.4 L 64 -20.4 Q 82 -20.6 91 -19.2 Q 96.6 -18 98.6 -15.4" fill="none" stroke="#FFFFFF" stroke-width="1" opacity="0.75"/>')
    # cream insert in the chrome spear on the rear flank
    g.append(f'<path d="M 3.6 -17.4 L 12 -18.6 Q 34 -17.6 56 -15.2 Q 34 -13.4 12 -12 L 3 -12.4 Z" fill="{upper}"/>')
    g.append(f'<path d="M 3.6 -17.4 L 12 -18.6 Q 34 -17.6 56 -15.2 L 96 -15.6 M 3 -12.4 L 12 -12 Q 34 -13.4 56 -15.2" fill="none" stroke="url(#{uid}-ch)" stroke-width="1" stroke-linejoin="round"/>')
    # door seam, handle, front-fender vents
    g.append(f'<path d="M 48 -20.4 L 48.6 -6 M 66 -20.4 Q 67 -13 66.4 -6" stroke="{body_dark}" stroke-width="0.6" fill="none" opacity="0.8"/>'
             '<rect x="60" y="-18.6" width="4.4" height="1" rx="0.5" fill="#EEF2F4"/>'
             '<g stroke="#E8EEF2" stroke-width="0.7"><path d="M 74 -12.4 l 5 0 M 74 -11 l 5 0 M 74 -9.6 l 5 0"/></g>')
    g.append(f'<path d="M 11 -23 L 3 -20.4 Q 0.6 -18 0.4 -12" fill="none" stroke="{rim}" stroke-width="1.2" opacity="0.9"/>')
    # wheels: rear one half-hidden by its fender skirt
    for cx in (22.2, 78.8):
        g.append(f'<circle cx="{cx}" cy="-4.8" r="7.8" fill="#1E1C22"/><circle cx="{cx}" cy="-4.8" r="5.6" fill="#F4F2EC"/>'
                 f'<circle cx="{cx}" cy="-4.8" r="3.8" fill="url(#{uid}-ch)"/><circle cx="{cx}" cy="-4.8" r="1.2" fill="#6E7A84"/>'
                 f'<path d="M {cx - 2.4} -7 A 3.4 3.4 0 0 1 {cx + 2} -7.4" stroke="#FFFFFF" stroke-width="0.7" fill="none"/>')
    g.append(f'<path d="M 13.6 -5 A 8.8 8.8 0 0 1 30.8 -5 L 30.8 -2.6 L 13.6 -2.6 Z" fill="url(#{uid}-b)"/>'
             '<path d="M 13.6 -3 L 30.8 -3" stroke="#EEF2F4" stroke-width="0.9"/>')
    # chrome bumpers, tail lights in the fin, hooded headlight, grille tip
    g.append(f'<path d="M -2 -10.6 L 5 -10.6 L 5 -4 L -1.4 -4 Q -3 -7.4 -2 -10.6 Z" fill="url(#{uid}-ch)"/>'
             f'<path d="M 94 -10.6 L 102 -10.2 Q 103.4 -7.4 102 -4 L 94 -4 Z" fill="url(#{uid}-ch)"/>'
             '<path d="M 0.4 -17.8 L 4.4 -20 L 4.8 -16 L 0.8 -14.8 Z" fill="#E8303A"/><path d="M 1 -17.4 L 4 -19 L 4.2 -18 L 1.2 -16.8 Z" fill="#FF8A8A"/>'
             '<circle cx="98.4" cy="-15" r="2.2" fill="#FFF6D8"/><path d="M 95.4 -17.4 Q 99 -19.6 100.4 -15.6" stroke="#EEF2F4" stroke-width="1.1" fill="none"/>'
             '<path d="M 99.2 -11.4 L 100.8 -11.4 L 101 -10.6 L 99.2 -10.6 Z" fill="#9AA4AC"/>'
             '<path d="M 88 -20.6 L 93 -21.6 L 93.6 -20.4 Z" fill="#E8EEF2"/>')
    g.append("</g>")
    return "".join(g)


def hv_facade(C, X, z0, z1, h, wall, seed, lit, shutter="#2E8A9A", portal=False, uid="hf", floors=None, glow_p=0.0):
    """A Havana colonial facade in the street plane X: tall shuttered French windows on every floor, wrought-iron
    balconies, cornices, a balustraded parapet, peeling paint; an arcade (portal) at street level if portal=True."""
    rnd = random.Random(seed)
    sgn = 1 if X < 0 else -1          # direction toward the street centre
    F = lambda z, y, dx=0: C(X + sgn * dx, hv_ground(z) + y, z)
    poly = lambda pts, dx=0: [F(z, y, dx) for z, y in pts]
    out = [f'<clipPath id="{uid}"><polygon points="{P(poly([(z0, 0), (z0, h), (z1, h), (z1, 0)]))}"/></clipPath>']
    out.append(Q(poly([(z0, 0), (z0, h), (z1, h), (z1, 0)]), wall))
    W = z1 - z0
    bays = max(2, round(W / 3.4))
    dark = mix(wall, "#2A2030", 0.7)
    trim = mix(wall, "#FFFFFF", 0.55)
    g = []
    # peeling paint and damp streaks
    zs = [z0 + W * rnd.random() for _ in range(int(W * 1.6))]
    for z in zs:
        y = rnd.uniform(0.5, h - 1)
        r = rnd.uniform(0.3, 0.9)
        g.append(Q(poly([(z - r, y - r * 0.6), (z, y - r), (z + r * 0.8, y - r * 0.2), (z + r * 0.4, y + r * 0.7), (z - r * 0.6, y + r * 0.5)]),
                   rnd.choice([mix(wall, "#FFFFFF", 0.3), mix(wall, "#7A5A50", 0.25), mix(wall, "#C8B8A0", 0.5)]), f' opacity="{rnd.uniform(0.35, 0.7):.2f}"'))
    out.append(f'<g clip-path="url(#{uid})">{"".join(g)}</g>')
    # ground floor
    if portal:
        out.append(Q(poly([(z0, 0), (z0, 4.2), (z1, 4.2), (z1, 0)]), mix(wall, "#3A2A3A", 0.55)))
        out.append(Q(poly([(z0, 0), (z0, 4.2), (z1, 4.2), (z1, 0)], 1.4), mix(wall, "#4A3A48", 0.6), ' opacity="0"'))
        cols = max(3, round(W / 3.0))
        for i in range(cols + 1):
            z = z0 + W * i / cols
            out.append(Q(poly([(z - 0.3, 0), (z - 0.3, 4.2), (z + 0.3, 4.2), (z + 0.3, 0)]), trim))
            if i < cols:
                za, zb = z + 0.3, z0 + W * (i + 1) / cols - 0.3
                zm = (za + zb) / 2
                out.append(Q(poly([(za, 4.2), (za, 3.3), (zm - (zb - za) * 0.3, 3.8), (zm, 3.9), (zm + (zb - za) * 0.3, 3.8), (zb, 3.3), (zb, 4.2)]), wall))
                if rnd.random() < 0.6:
                    out.append(Q(poly([(zm - 0.5, 0), (zm - 0.5, 2.4), (zm + 0.5, 2.4), (zm + 0.5, 0)]), rnd.choice(["#3A5A7A", "#7A3A3A", "#2E6A5A"]), ' opacity="0.8"'))
    else:
        for i in range(bays):
            za = z0 + W * (i + 0.25) / bays
            zb = z0 + W * (i + 0.75) / bays
            zm = (za + zb) / 2
            out.append(Q(poly([(za - 0.15, 0), (za - 0.15, 3.3), (zm, 3.9), (zb + 0.15, 3.3), (zb + 0.15, 0)]), trim))
            out.append(Q(poly([(za, 0), (za, 3.2), (zm, 3.7), (zb, 3.2), (zb, 0)]), rnd.choice([shutter, "#5A3A2A", dark])))
            out.append(f'<polyline points="{P(poly([(zm, 0.1), (zm, 3.6)]))}" stroke="{dark}" stroke-width="0.8" fill="none"/>')
    floors = floors or [y for y in (4.6, 8.4, 12.0) if y + 3.4 < h - 0.6]
    for fi, y0 in enumerate(floors):
        out.append(Q(poly([(z0, y0 - 0.4), (z0, y0), (z1, y0), (z1, y0 - 0.4)]), trim, ' opacity="0.85"'))
        for i in range(bays):
            za = z0 + W * (i + 0.28) / bays
            zb = z0 + W * (i + 0.72) / bays
            zm = (za + zb) / 2
            yt = y0 + 2.9
            out.append(Q(poly([(za - 0.2, y0), (za - 0.2, yt + 0.3), (zb + 0.2, yt + 0.3), (zb + 0.2, y0)]), trim))
            out.append(Q(poly([(za - 0.25, yt + 0.3), (zm, yt + 0.9), (zb + 0.25, yt + 0.3)]), trim))
            openw = rnd.random()
            if openw < 0.35:
                # one shutter swung open: dark room, a glimpse of warm lamp light
                out.append(Q(poly([(za, y0), (za, yt), (zb, yt), (zb, y0)]), "#FFCF84" if rnd.random() < glow_p else "#2A2230"))
                out.append(Q(poly([(zb, y0), (zb, yt), (zb + (zb - za) * 0.45, yt), (zb + (zb - za) * 0.45, y0)], 0.3), shutter))
            else:
                out.append(Q(poly([(za, y0), (za, yt), (zb, yt), (zb, y0)]), shutter))
                lines = "".join(f'<polyline points="{P(poly([(za, y0 + j * 0.28), (zb, y0 + j * 0.28)]))}"/>' for j in range(1, 10))
                out.append(f'<g stroke="{mix(shutter, "#000000", 0.35)}" stroke-width="0.6" opacity="0.6" fill="none">{lines}'
                           f'<polyline points="{P(poly([(zm, y0), (zm, yt)]))}"/></g>')
            # wrought-iron balcony on its stone slab
            if rnd.random() < 0.8:
                bd = 0.7
                out.append(Q(poly([(za - 0.5, y0), (zb + 0.5, y0)]) + poly([(zb + 0.5, y0), (za - 0.5, y0)], bd), mix(trim, "#000000", 0.2)))
                rail = poly([(za - 0.5, y0 + 1.0), (zb + 0.5, y0 + 1.0)], bd)
                bal = "".join(f'<polyline points="{P(poly([(za - 0.5 + (zb - za + 1) * j / 8, y0), (za - 0.5 + (zb - za + 1) * j / 8, y0 + 1.0)], bd))}"/>' for j in range(9))
                out.append(f'<g stroke="#2A2228" fill="none" stroke-width="0.7">{bal}</g><polyline points="{P(rail)}" stroke="#2A2228" stroke-width="1.1" fill="none"/>')
                if rnd.random() < 0.3:
                    pz = rnd.uniform(za, zb)
                    p_ = F(pz, y0 + 1.1, bd)
                    s_ = C.f / pz
                    out.append(f'<circle cx="{p_[0]:.1f}" cy="{p_[1] - 0.3 * s_:.1f}" r="{0.45 * s_:.1f}" fill="#3E7A3A"/><circle cx="{p_[0] + 0.3 * s_:.1f}" cy="{p_[1] - 0.5 * s_:.1f}" r="{0.18 * s_:.1f}" fill="#E8406A"/>')
    # cornice and balustraded parapet
    out.append(Q(poly([(z0, h - 1.4), (z0, h - 0.9), (z1, h - 0.9), (z1, h - 1.4)]), trim))
    out.append(Q(poly([(z0, h - 1.6), (z0, h - 1.4), (z1, h - 1.4), (z1, h - 1.6)]), "#000000", ' opacity="0.18"'))
    n = int(W / 0.5)
    out.append(f'<g stroke="{dark}" stroke-width="0.8" opacity="0.6" fill="none">' + "".join(
        f'<polyline points="{P(poly([(z0 + W * (j + 0.5) / n, h - 0.8), (z0 + W * (j + 0.5) / n, h - 0.2)]))}"/>' for j in range(n) if j % 6) + "</g>")
    out.append(Q(poly([(z0, h - 0.2), (z0, h), (z1, h), (z1, h - 0.2)]), trim))
    for i in range(bays + 1):
        z = z0 + W * i / bays
        out.append(Q(poly([(z - 0.12, 0.2), (z - 0.12, h - 1.4), (z + 0.12, h - 1.4), (z + 0.12, 0.2)]), trim, ' opacity="0.45"'))
    if not lit:
        out.append(Q(poly([(z0, 0), (z0, h), (z1, h), (z1, 0)]), "#3A3A7E", ' opacity="0.3"'))
    else:
        out.append(Q(poly([(z0, 0), (z0, h), (z1, h), (z1, 0)]), "#FFB860", ' opacity="0.12"'))
    out.append(f'<polyline points="{P(poly([(z0, 0), (z0, h)]))}" stroke="#000" stroke-width="1" opacity="0.18" fill="none"/>')
    return "".join(out)


def hv_front(C, Z, x0, x1, h, wall, seed, shutter="#2E7A9A", uid="hfr", lit=0.0):
    """The corner building's face toward us (plane Z): tall shuttered door-windows, balconies with ironwork,
    a big cornice. Drawn at near scale, so with more detail."""
    rnd = random.Random(seed)
    g0 = hv_ground(Z)
    F = lambda x, y, dz=0: C(x, g0 + y, Z - dz)
    poly = lambda pts, dz=0: [F(x, y, dz) for x, y in pts]
    trim = mix(wall, "#FFFFFF", 0.55)
    dark = mix(wall, "#2A2030", 0.7)
    out = [f'<clipPath id="{uid}"><polygon points="{P(poly([(x0, 0), (x0, h), (x1, h), (x1, 0)]))}"/></clipPath>',
           Q(poly([(x0, 0), (x0, h), (x1, h), (x1, 0)]), wall)]
    g = []
    W = x1 - x0
    for _ in range(int(W * 3)):
        x, y, r = x0 + W * rnd.random(), rnd.uniform(0.3, h), rnd.uniform(0.15, 0.6)
        g.append(Q(poly([(x - r, y), (x - r * 0.3, y + r * 0.7), (x + r, y + r * 0.3), (x + r * 0.6, y - r * 0.6)]),
                   rnd.choice([mix(wall, "#FFFFFF", 0.3), mix(wall, "#7A5A50", 0.25), "#D8C8B0"]), f' opacity="{rnd.uniform(0.3, 0.65):.2f}"'))
    g.append(streaks(int(W * 4), seed + 3, (min(F(x0, h)[0], F(x1, h)[0]), F(x0, h)[1], max(F(x0, 0)[0], F(x1, 0)[0]), F(x0, 0)[1]),
                     [mix(wall, "#5A4A4A", 0.3)], w=(1, 3), length=(20, 70), opacity=(0.08, 0.2), slant=0.02))
    out.append(f'<g clip-path="url(#{uid})">{"".join(g)}</g>')
    bays = max(1, round(W / 3.2))
    for y0 in (0.3, 4.6, 8.4, 12.0):
        if y0 + 3 > h - 1:
            continue
        out.append(Q(poly([(x0, y0 - 0.4), (x0, y0), (x1, y0), (x1, y0 - 0.4)]), trim, ' opacity="0.85"'))
        for i in range(bays):
            xa = x0 + W * (i + 0.27) / bays
            xb = x0 + W * (i + 0.73) / bays
            xm = (xa + xb) / 2
            yt = y0 + (3.1 if y0 < 1 else 2.9)
            out.append(Q(poly([(xa - 0.25, y0), (xa - 0.25, yt + 0.3), (xb + 0.25, yt + 0.3), (xb + 0.25, y0)]), trim))
            out.append(Q(poly([(xa - 0.35, yt + 0.3), (xm, yt + 0.95), (xb + 0.35, yt + 0.3)]), trim))
            out.append(Q(poly([(xa, y0), (xa, yt), (xb, yt), (xb, y0)]), shutter))
            lines = "".join(f'<polyline points="{P(poly([(xa, y0 + j * 0.25), (xb, y0 + j * 0.25)]))}"/>' for j in range(1, int((yt - y0) / 0.25)))
            out.append(f'<g stroke="{mix(shutter, "#000000", 0.4)}" stroke-width="0.8" opacity="0.6" fill="none">{lines}'
                       f'<polyline points="{P(poly([(xm, y0), (xm, yt)]))}"/></g>')
            out.append(Q(poly([(xa, yt - 0.9), (xa, yt), (xb, yt), (xb, yt - 0.9)]), mix(shutter, "#FFFFFF", 0.3), ' opacity="0.5"'))
            if y0 > 1:
                bd = 0.8
                slab = poly([(xa - 0.6, y0), (xb + 0.6, y0)]) + poly([(xb + 0.6, y0), (xa - 0.6, y0)], bd)
                out.append(Q(slab, mix(trim, "#000000", 0.25)))
                out.append(Q(poly([(xa - 0.6, y0 - 0.25), (xa - 0.6, y0), (xb + 0.6, y0), (xb + 0.6, y0 - 0.25)], bd), trim))
                bal = "".join(f'<polyline points="{P(poly([(xa - 0.6 + (xb - xa + 1.2) * j / 10, y0), (xa - 0.6 + (xb - xa + 1.2) * j / 10, y0 + 1.0)], bd))}"/>' for j in range(11))
                curls = "".join(f'<circle cx="{F(xa - 0.6 + (xb - xa + 1.2) * (j + 0.5) / 10, y0 + 0.5, bd)[0]:.1f}" cy="{F(0, y0 + 0.5, bd)[1]:.1f}" r="{0.16 * C.f / Z:.1f}"/>' for j in range(10))
                out.append(f'<g stroke="#2A2228" fill="none" stroke-width="1">{bal}{curls}</g>'
                           f'<polyline points="{P(poly([(xa - 0.6, y0 + 1.0), (xb + 0.6, y0 + 1.0)], bd))}" stroke="#2A2228" stroke-width="1.6" fill="none"/>')
    out.append(Q(poly([(x0, h - 1.4), (x0, h - 0.8), (x1, h - 0.8), (x1, h - 1.4)]), trim))
    out.append(Q(poly([(x0, h - 1.7), (x0, h - 1.4), (x1, h - 1.4), (x1, h - 1.7)]), "#000000", ' opacity="0.2"'))
    out.append(Q(poly([(x0, h - 0.25), (x0, h), (x1, h), (x1, h - 0.25)]), trim))
    if lit:
        out.append(Q(poly([(x0, 0), (x0, h), (x1, h), (x1, 0)]), "#FFB860", f' opacity="{lit}"'))
    else:
        out.append(Q(poly([(x0, 0), (x0, h), (x1, h), (x1, 0)]), "#3A3A7E", ' opacity="0.18"'))
    return "".join(out)


def street_cat(x, base, s, fur="#E8A050", dark="#B8662A", lit="#FFD8A0"):
    """Ginger tabby sitting with its back to us, head turned toward the pigeons, tail curled round."""
    return (f'<g transform="translate({x:.1f} {base:.1f}) scale({s:.2f})">'
            '<ellipse cx="2" cy="0" rx="16" ry="2.6" fill="#2A2A5A" opacity="0.25"/>'
            f'<path d="M 12 -2 Q 22 -2 20 -8 Q 18 -12 22 -14" fill="none" stroke="{fur}" stroke-width="4" stroke-linecap="round"/>'
            f'<path d="M -10 0 Q -13 -14 -6 -24 Q 0 -30 6 -24 Q 13 -14 10 0 Z" fill="{fur}"/>'
            f'<path d="M 2 -27 Q 11 -16 10 0 L 4 0 Q 6 -14 2 -27 Z" fill="{lit}" opacity="0.6"/>'
            f'<g stroke="{dark}" stroke-width="1.6" fill="none" stroke-linecap="round"><path d="M -8 -12 q 4 -1 6 1"/><path d="M -9 -6 q 5 -1 7 1"/><path d="M -6 -18 q 3 -1 5 1"/></g>'
            f'<circle cx="1" cy="-31" r="7" fill="{fur}"/><path d="M -5 -34 L -5 -42 L 0 -37 Z M 5 -36 L 9 -42 L 8 -33 Z" fill="{fur}"/>'
            f'<path d="M 6 -37 L 8.4 -40.6 L 8 -35 Z" fill="#F4B8A0"/><path d="M 5 -27 q 3 -2 6 -1" stroke="{dark}" stroke-width="1" fill="none"/>'
            f'<path d="M 3 -36 Q 8 -33 7.6 -27" fill="none" stroke="{lit}" stroke-width="1.4"/>'
            f'<g stroke="{dark}" stroke-width="1.2"><path d="M -3 -36 l 1 3 M 0 -37 l 0 3"/></g></g>')


def havana():
    u = "hv"
    C = Cam(f=310, cx=372, vpy=262, eye=1.6)
    out = [defs(
        lg(f"{u}-sky", [(0, "#4C9ED2"), (0.45, "#8CC4E2"), (0.8, "#F2E2C4"), (1, "#FFD8A4")], 0, 0, 0, 262, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#7EC4D2"), (1, "#1E7A9A")], 0, 262, 0, 290, units="userSpaceOnUse"),
        lg(f"{u}-road", [(0, "#B8A698"), (1, "#8A7A78")], 0, 280, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="300" fill="url(#{u}-sky)"/>')
    out.append(glow(150, 200, 300, "#FFE2A8", f"{u}-sun", 0.75))
    out.append(cumulus(f"{u}-c1", 386, 120, 150, 40, 21, "#FFF8EC", "#F6E6DC", "#B6B4CE", hi="#FFFFFF", hi_op=0.75, light=-1))
    out.append(cumulus(f"{u}-c2", 520, 168, 110, 26, 22, "#FFF4E2", "#F4E2D6", "#BAB6CE", hi="#FFFFFF", light=-1))
    out.append(cumulus(f"{u}-c3", 300, 214, 90, 18, 23, "#FFF0DA", "#F2DCCE", "#C0B8CC", hi="#FFFFFF", light=-1))
    # the sea at the end of the street, glittering, and a freighter on the horizon
    out.append(f'<rect x="0" y="262" width="600" height="40" fill="url(#{u}-sea)"/>')
    out.append(water_lines(40, 31, (300, 263, 460, 290), ["#FFFFFF", "#CFEFF2", "#16627E"], w=(3, 12), h=(0.6, 1.2), opacity=(0.4, 0.9)))
    out.append('<g fill="#5A6A7A"><rect x="404" y="258.6" width="18" height="2.6"/><rect x="417" y="255.4" width="4" height="3.4"/></g>')
    # the Malecón: the long seawall with a wave bursting over it, people sitting on the wall
    wall_top, wall_bot = C(0, hv_ground(60) + 0.9, 60)[1], C(0, hv_ground(60), 60)[1]
    out.append(f'<rect x="0" y="{wall_top:.1f}" width="600" height="{wall_bot - wall_top + 0.5:.1f}" fill="#E8E2D6"/>'
               f'<rect x="0" y="{wall_top:.1f}" width="600" height="1.2" fill="#FFFFFF"/>')
    road_y = C(0, hv_ground(50), 50)[1]
    out.append(f'<rect x="0" y="{wall_bot:.1f}" width="600" height="{road_y - wall_bot + 2:.1f}" fill="#9A8C90"/>')
    out.append(puff_column(f"{u}-sp", 404, wall_top + 1, wall_top - 16, 33, r0=3, r1=9, drift=6, n=18, grad=None, hi="#FFFFFF", hi_op=0.9).replace('fill="url(#None)"', 'fill="#F4FAFC"'))
    rnd = random.Random(34)
    for px in (330, 338, 360, 372, 430, 444):
        c = rnd.choice(["#E8543E", "#2E5A8E", "#F2C230", "#2A2A3A", "#FFFFFF"])
        out.append(f'<rect x="{px:.1f}" y="{wall_top - 3:.1f}" width="2" height="3.2" fill="{c}"/><circle cx="{px + 1:.1f}" cy="{wall_top - 4:.1f}" r="1" fill="#4A3020"/>')
    # a car passing on the Malecón
    out.append(vintage_car(342, road_y - 0.6, 22, body="#E8506A", body_dark="#A8304A", upper="#FFF0E4", driver=False, uid=f"{u}-car2"))
    # the street running down to the sea
    road = [C(-6.3, hv_ground(z), z) for z in (8, 14, 20, 30, 40, 50)] + [C(6.3, hv_ground(z), z) for z in (50, 40, 30, 20, 14, 8)]
    out.append(Q(road, f"url(#{u}-road)"))
    for X, sgn in ((-8, 1), (8, -1)):
        walk = [C(X, hv_ground(z), z) for z in (8, 14, 20, 30, 40, 50)] + [C(X + sgn * 1.7, hv_ground(z), z) for z in (50, 40, 30, 20, 14, 8)]
        out.append(Q(walk, "#D8C6B4"))
        out.append(f'<polyline points="{P([C(X + sgn * 1.7, hv_ground(z), z) for z in (8, 14, 20, 30, 40, 50)])}" stroke="#F6EADA" stroke-width="1.4" fill="none"/>')
    # patched asphalt
    rnd = random.Random(35)
    for _ in range(26):
        z = rnd.uniform(12, 48)
        X = rnd.uniform(-5.5, 5)
        q = [C(X, hv_ground(z), z), C(X + rnd.uniform(0.6, 2), hv_ground(z), z), C(X + rnd.uniform(0.6, 2), hv_ground(z + 1.2), z + 1.2), C(X, hv_ground(z + 1.2), z + 1.2)]
        out.append(Q(q, rnd.choice(["#A89488", "#7E7070", "#C4B4A4"]), ' opacity="0.6"'))
    # street facades: the left (east-facing) side in cool shade, the right side warm in the low sun
    left = [(11, 19, 12.8, "#F4B8C4", "#3E9AA8", False), (19, 26, 11.6, "#F6E4A0", "#2E7A5A", False), (26, 33, 13.4, "#A8DCD2", "#E8E4D8", True),
            (33, 39, 11.2, "#F6C4A0", "#3A6E9A", False), (39, 45, 12.4, "#C8C0E8", "#2E8A7A", False), (45, 50, 10.4, "#F8E8D0", "#4A86A8", False)]
    right = [(11, 18, 13.4, "#A8E0D8", "#E86A6A", True), (18, 25, 11.8, "#F8D488", "#2E6A9A", True), (25, 31, 12.8, "#F4A8B4", "#2E8A8A", True),
             (31, 37, 11.0, "#C4E4A8", "#8A4A6A", True), (37, 43, 12.6, "#F8F0E0", "#3A7AAA", True), (43, 50, 11.4, "#F6BC94", "#2E7A6A", True)]
    for i, (z0, z1, h, wall, sh, portal) in reversed(list(enumerate(left))):
        out.append(hv_facade(C, -8, z0, z1, h, wall, 40 + i, False, shutter=sh, portal=portal, uid=f"{u}-l{i}"))
    for i, (z0, z1, h, wall, sh, portal) in reversed(list(enumerate(right))):
        out.append(hv_facade(C, 8, z0, z1, h, wall, 50 + i, True, shutter=sh, portal=portal, uid=f"{u}-r{i}"))
    # long shadows of the left-hand roofs thrown across the street toward the right
    sh_pts = [C(-6.3, hv_ground(z), z) for z in (8, 50)] + [C(-1.5, hv_ground(50), 50), C(-0.4, hv_ground(42), 42), C(-2.2, hv_ground(36), 36), C(-0.8, hv_ground(28), 28), C(-2.6, hv_ground(19), 19), C(-1.6, hv_ground(8), 8)]
    out.append(Q(sh_pts, "#3A3A7E", ' opacity="0.22"'))
    # overhead wires and laundry strung across
    w1, w2 = C(-8, hv_ground(22) + 9.6, 22), C(8, hv_ground(24) + 9.2, 24)
    out.append(f'<path d="M {w1[0]:.1f} {w1[1]:.1f} Q {(w1[0] + w2[0]) / 2:.1f} {max(w1[1], w2[1]) + 14:.1f} {w2[0]:.1f} {w2[1]:.1f}" stroke="#2A2230" stroke-width="0.9" fill="none"/>')
    w3, w4 = C(-8, hv_ground(31) + 8, 31), C(8, hv_ground(34) + 9, 34)
    out.append(f'<path d="M {w3[0]:.1f} {w3[1]:.1f} Q {(w3[0] + w4[0]) / 2:.1f} {max(w3[1], w4[1]) + 8:.1f} {w4[0]:.1f} {w4[1]:.1f}" stroke="#2A2230" stroke-width="0.7" fill="none"/>')
    l1, l2 = C(-8, hv_ground(16) + 6.4, 16), C(-8, hv_ground(19.5) + 6.4, 19.5)
    out.append(f'<path d="M {l1[0]:.1f} {l1[1]:.1f} Q {(l1[0] + l2[0]) / 2 + 6:.1f} {(l1[1] + l2[1]) / 2 + 10:.1f} {l2[0]:.1f} {l2[1]:.1f}" stroke="#3A3040" stroke-width="0.8" fill="none"/>')
    rnd = random.Random(36)
    for j in range(5):
        t = (j + 0.6) / 5.4
        px = l1[0] + (l2[0] - l1[0]) * t + 6 * 4 * t * (1 - t)
        py = l1[1] + (l2[1] - l1[1]) * t + 10 * 4 * t * (1 - t)
        s_ = 1 - t * 0.4
        out.append(f'<rect x="{px - 3 * s_:.1f}" y="{py:.1f}" width="{6 * s_:.1f}" height="{rnd.uniform(6, 10) * s_:.1f}" fill="{rnd.choice(["#FFFFFF", "#F2C230", "#E8543E", "#4E8ACA", "#F4A8C4"])}"/>')
    # the corner buildings facing us, framing the view
    out.append(hv_front(C, 11, -30, -8, 14.6, "#E89A6A", 60, shutter="#2E6E8A", uid=f"{u}-fl", lit=0.0))
    out.append(hv_front(C, 11, 8, 26, 13.8, "#7EC8C0", 61, shutter="#F4F0E4", uid=f"{u}-fr", lit=0.1))
    # sunlit corner edge on the right building
    a, b = C(8, hv_ground(11), 11), C(8, hv_ground(11) + 13.8, 11)
    out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#FFE6B8" stroke-width="2.4" opacity="0.8"/>')
    # wall lamp on the right corner, a woman watering her plants on the left balcony
    lp = C(8.2, 3.6, 11)
    out.append(f'<path d="M {lp[0]:.1f} {lp[1]:.1f} l 10 -2 l 0 6" stroke="#2A2228" stroke-width="1.6" fill="none"/><path d="M {lp[0] + 6:.1f} {lp[1] + 4:.1f} l 8 0 l -1.6 8 l -4.8 0 Z" fill="#2A2228"/><rect x="{lp[0] + 7.6:.1f}" y="{lp[1] + 5:.1f}" width="4.8" height="5" fill="#FFE8B0"/>')
    # the near cross street with our corner kerb
    kz = 3.7
    ky = C(0, 0, kz)[1]
    cross = [(-10, C(0, 0, 11)[1]), (610, C(0, 0, 11)[1]), (610, ky), (-10, ky)]
    out.append(Q(cross, f"url(#{u}-road)"))
    out.append(Q([(-10, C(0, 0, 11)[1]), (610, C(0, 0, 11)[1]), (610, C(0, 0, 8)[1]), (-10, C(0, 0, 8)[1])], "#3A3A7E", ' opacity="0.14"'))
    rnd = random.Random(37)
    for _ in range(14):
        zz = rnd.uniform(kz + 0.4, 10.5)
        xx = rnd.uniform(-12, 12)
        y_ = C(0, 0, zz)[1]
        s_ = C.f / zz
        out.append(f'<ellipse cx="{C(xx, 0, zz)[0]:.1f}" cy="{y_:.1f}" rx="{s_ * rnd.uniform(0.3, 0.9):.1f}" ry="{s_ * 0.06:.1f}" fill="{rnd.choice(["#A89488", "#7E7070", "#C4B4A4"])}" opacity="0.6"/>')
    out.append(Q([(-10, ky), (610, ky), (610, 444), (-10, 444)], "#DCCAB6"))
    out.append(f'<rect x="-10" y="{ky - 1:.1f}" width="620" height="4" fill="#F4E8D8"/><rect x="-10" y="{ky + 3:.1f}" width="620" height="3" fill="#A8968A"/>')
    for j in range(1, 6):
        yy = C(0, 0, kz - j * 0.5)[1]
        if yy < 444:
            out.append(f'<line x1="-10" y1="{yy:.1f}" x2="610" y2="{yy:.1f}" stroke="#BCA898" stroke-width="1" opacity="0.6"/>')
    for xx in range(-10, 11, 2):
        out.append(f'<line x1="{C(xx, 0, kz)[0]:.1f}" y1="{ky + 6:.1f}" x2="{C(xx, 0, 2.6)[0]:.1f}" y2="444" stroke="#BCA898" stroke-width="1" opacity="0.5"/>')
    # the long shadow of an unseen building on our corner, falling across the pavement
    out.append(Q([(-10, ky + 6), (150, ky + 6), (90, 444), (-10, 444)], "#3A3A7E", ' opacity="0.18"'))
    # a woman with a parasol strolling on the sunny pavement, a man in a guayabera at the corner
    out.append(person(C(7.2, 0, 13)[0], C(7.2, hv_ground(13), 13)[1], 40, "#F2C230", "#F2C230", skin="#8A5A3E", hair="#2A1A12", dress=True, flip=-1, rim="#FFE6B8"))
    pp = C(7.2, 0, 13)
    out.append(f'<path d="M {pp[0] - 12:.1f} {pp[1] - 48:.1f} Q {pp[0] - 1:.1f} {pp[1] - 62:.1f} {pp[0] + 10:.1f} {pp[1] - 48:.1f} Z" fill="#F4F0E8"/>'
               f'<path d="M {pp[0] - 12:.1f} {pp[1] - 48:.1f} Q {pp[0] - 1:.1f} {pp[1] - 62:.1f} {pp[0] + 10:.1f} {pp[1] - 48:.1f}" fill="none" stroke="#E8543E" stroke-width="1.4"/>'
               f'<line x1="{pp[0] - 1:.1f}" y1="{pp[1] - 55:.1f}" x2="{pp[0] - 3:.1f}" y2="{pp[1] - 30:.1f}" stroke="#4A3A30" stroke-width="1"/>')
    out.append(person(C(7.0, 0, 24)[0], C(7.0, hv_ground(24), 24)[1], 24, "#F6F2E8", "#3A3A48", skin="#6A4430", hair="#D8D2C8", hat="#E8D49A", arms="down", rim="#FFE6B8"))
    # the convertible rolling past the corner, its shadow stretching right
    cz = 4.6
    cy = C(0, 0, cz)[1]
    out.append(f'<ellipse cx="{240:.1f}" cy="{cy + 3:.1f}" rx="176" ry="8" fill="#2A2A5A" opacity="0.28"/>')
    out.append(vintage_car(62, cy, 300, uid=f"{u}-car"))
    # a ginger cat on the kerb, eyeing the pigeons
    out.append(street_cat(440, 436, 1.0))
    # pigeons on the pavement
    for px, py, fl in ((486, 430, False), (512, 438, True), (530, 424, False)):
        sx = -1 if fl else 1
        out.append(f'<g transform="translate({px} {py}) scale({sx * 1.3} 1.3)"><ellipse cx="0" cy="-4" rx="6" ry="3.6" fill="#8A8EA0"/><path d="M 4 -5 L 10 -3 L 4 -2 Z" fill="#6A6E80"/>'
                   '<circle cx="-5" cy="-7" r="2.6" fill="#7A7E92"/><path d="M -7.4 -7 L -9.4 -6.4 L -7.4 -6 Z" fill="#3A2A2A"/><path d="M -3 -6 Q -1 -3 -4 -2" stroke="#6AA88A" stroke-width="1.2" fill="none"/>'
                   '<path d="M -1 -1 L -1 1 M 1.4 -1 L 1.4 1" stroke="#E8604A" stroke-width="0.9"/><path d="M -2 -5 Q 2 -6.6 5 -5" stroke="#B8BCCA" stroke-width="0.8" fill="none"/></g>')
    # bougainvillea petals blown onto the pavement
    out.append(dots(26, 38, (300, ky + 8, 600, 444), "#E8407A", r=(1, 2), opacity=(0.7, 1)))
    return "\n".join(out)


# ================================================================ CHICHÉN ITZÁ — El Castillo at sunset, the serpent of light on the north stair
def motmot(x, y, s, flip=False):
    """Turquoise-browed motmot (the Yucatán's 'toh') perched on a twig: green-and-rufous body, turquoise brow,
    black throat patch, and the long tail with two bare-shafted rackets."""
    sx = -s if flip else s
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({sx:.2f} {s:.2f})">'
            # tail: blue-green shaft, bare wires, then the rackets
            '<path d="M 4 4 Q 7 18 9 26" stroke="#3E8A8E" stroke-width="3.4" fill="none" stroke-linecap="round"/>'
            '<path d="M 9 26 L 11 40" stroke="#2A4A4E" stroke-width="1.1"/><path d="M 7.6 26 L 8.4 40" stroke="#2A4A4E" stroke-width="1.1"/>'
            '<path d="M 11 40 Q 14 44 12.6 50 Q 9.6 46 10.2 41 Z" fill="#2E8AB8"/><path d="M 8.4 40 Q 6 44 7 50 Q 10 46 9.2 41 Z" fill="#2A6AA0"/>'
            '<path d="M 11.6 45 Q 12.6 48 12.2 50" stroke="#1E2A3A" stroke-width="1.4" fill="none"/><path d="M 7.6 45 Q 7 48 7.2 50" stroke="#1E2A3A" stroke-width="1.4" fill="none"/>'
            # body
            '<path d="M -8 -6 Q -10 4 -2 8 Q 6 10 8 2 Q 8 -8 0 -11 Q -6 -12 -8 -6 Z" fill="#7E9A3A"/>'
            '<path d="M -1 -10 Q 8 -8 8 2 Q 6 8 2 8 Q 6 -2 -1 -10 Z" fill="#C86A2E"/>'
            '<path d="M -8 -4 Q -9 4 -3 7 Q -4 0 -2 -4 Z" fill="#E8984A"/>'
            '<path d="M 1 -8 Q 7 -6 7.4 0 Q 4 -4 1 -8 Z" fill="#3E8A8E"/>'
            # head with turquoise brow and black mask
            '<circle cx="-6" cy="-13" r="6" fill="#8AAA44"/><path d="M -11.4 -12 Q -9 -10 -4 -11.4 L -2 -13.4 Q -8 -14.6 -11.6 -13.6 Z" fill="#1E1E24"/>'
            '<path d="M -11.6 -15 Q -7 -18.6 -1.6 -15.6 L -2.2 -14.2 Q -7 -16.8 -11 -13.8 Z" fill="#5AD8E0"/>'
            '<circle cx="-7" cy="-12.8" r="1.4" fill="#C8401E"/><circle cx="-7.2" cy="-13" r="0.5" fill="#FFFFFF"/>'
            '<path d="M -11.4 -12.6 L -19 -10.4 L -11 -10.4 Z" fill="#1E1E24"/>'
            '<path d="M -10.6 -8 L -7.4 -5 L -5 -8.4 Z" fill="#1E1E24"/><path d="M -10.8 -7.6 L -7.4 -4.6 L -4.6 -8.2" stroke="#5AD8E0" stroke-width="0.9" fill="none"/>'
            '<path d="M -1.6 -16 Q 2 -13 1 -9" stroke="#FFD08A" stroke-width="1.2" fill="none" opacity="0.9"/>'
            '<path d="M -3 8 L -3.6 11 M 1 8.6 L 0.8 11" stroke="#3A2A24" stroke-width="1"/></g>')


def castillo(C, u):
    """El Castillo (Temple of Kukulcán) seen from the north-west at sunset: nine stepped terraces with recessed
    panels, the north stair with its serpent-head balustrades and, on its western balustrade, the equinox
    'serpent of light' - seven sunlit triangles cast by the terrace corners. West face lit, north face in shade."""
    th = math.radians(32)
    Zc = 70

    def p(a, b, y):
        X = a * math.cos(th) - b * math.sin(th)
        Z = Zc - (a * math.sin(th) + b * math.cos(th))
        return C(X - 6, y, Z)

    H, N = 24.0, 9
    hk = H / N
    B, Wt = 27.7, 9.8
    out = [defs(lg(f"{u}-lit", [(0, "#FFCB84"), (1, "#E89A5E")], 0, 0, 0, 1), lg(f"{u}-sh", [(0, "#A48098"), (1, "#7A5E7E")], 0, 0, 0, 1))]
    lit_c, lit_d, lit_hi = "#F6B47A", "#C47A56", "#FFE2B0"
    sh_c, sh_d, sh_hi = "#94768E", "#6A5272", "#C4A0A8"
    sw, st = 5.4, 4.4                  # stair + balustrade half-widths
    for face in ("west", "north"):
        col, dark, hi = (lit_c, lit_d, lit_hi) if face == "west" else (sh_c, sh_d, sh_hi)
        for k in range(N):
            w0 = B - k * (B - Wt) / N
            w1 = w0 - 0.9
            y0, y1 = k * hk, (k + 1) * hk
            for side in (-1, 1):
                if face == "north":
                    q = [p(side * sw, w0, y0), p(side * w0, w0, y0), p(side * w1, w1, y1), p(side * sw, w1, y1)]
                else:
                    q = [p(w0, side * sw, y0), p(w0, side * w0, y0), p(w1, side * w1, y1), p(w1, side * sw, y1)]
                out.append(Q(q, col))
                # recessed panels and the cornice of each terrace
                n = max(3, int((w0 - sw) / 2.6))
                for j in range(n):
                    a0 = sw + (w0 - sw) * (j + 0.22) / n
                    a1 = sw + (w0 - sw) * (j + 0.78) / n
                    ya, yb = y0 + hk * 0.18, y0 + hk * 0.7
                    tw = lambda a, y: (w0 - (w0 - w1) * (y - y0) / hk)
                    if face == "north":
                        pq = [p(side * a0, tw(a0, ya), ya), p(side * a1, tw(a1, ya), ya), p(side * a1, tw(a1, yb), yb), p(side * a0, tw(a0, yb), yb)]
                    else:
                        pq = [p(tw(a0, ya), side * a0, ya), p(tw(a1, ya), side * a1, ya), p(tw(a1, yb), side * a1, yb), p(tw(a0, yb), side * a0, yb)]
                    out.append(Q(pq, dark, ' opacity="0.55"'))
                if face == "north":
                    cq = [p(side * sw, w1 + 0.1, y1 - 0.45), p(side * w1, w1 + 0.1, y1 - 0.45), p(side * w1, w1, y1), p(side * sw, w1, y1)]
                    bq = [p(side * sw, w0, y0), p(side * w0, w0, y0), p(side * w0, w0, y0 + 0.25), p(side * sw, w0, y0 + 0.25)]
                else:
                    cq = [p(w1 + 0.1, side * sw, y1 - 0.45), p(w1 + 0.1, side * w1, y1 - 0.45), p(w1, side * w1, y1), p(w1, side * sw, y1)]
                    bq = [p(w0, side * sw, y0), p(w0, side * w0, y0), p(w0, side * w0, y0 + 0.25), p(w0, side * sw, y0 + 0.25)]
                out.append(Q(cq, hi, ' opacity="0.8"'))
                out.append(Q(bq, "#000000", ' opacity="0.12"'))
    # weathering: blotches of grey-black lichen on the stone
    rnd = random.Random(5)
    for _ in range(140):
        k = rnd.randrange(N)
        w0 = B - k * (B - Wt) / N
        a = rnd.uniform(sw, w0) * rnd.choice((-1, 1))
        y = rnd.uniform(k * hk, (k + 1) * hk)
        face = rnd.choice(("west", "north"))
        x_, y_ = p(a, w0 - 0.4 * (y - k * hk) / hk, y) if face == "north" else p(w0 - 0.4 * (y - k * hk) / hk, a, y)
        out.append(f'<ellipse cx="{x_:.1f}" cy="{y_:.1f}" rx="{rnd.uniform(1.5, 4):.1f}" ry="{rnd.uniform(0.8, 1.6):.1f}" fill="{rnd.choice(["#5A4A5E", "#3A3040", "#8A6A5A"])}" opacity="{rnd.uniform(0.15, 0.35):.2f}"/>')
    # the stairs: 91 steps up each side; west stair glowing in the sun, north stair in shade
    for face in ("west", "north"):
        lit = face == "west"
        foot, top = B + 2.6, Wt

        def sp(a, t, dy=0.0, f=face):
            v = foot + (top - foot) * t
            y = H * t + dy
            return p(v, a, y) if f == "west" else p(a, v, y)
        out.append(Q([sp(-st, 0), sp(st, 0), sp(st, 1), sp(-st, 1)], "#F2B276" if lit else "#86687E"))
        for j in range(46):
            t0 = j / 46
            out.append(Q([sp(-st, t0), sp(st, t0), sp(st, t0 + 0.5 / 46), sp(-st, t0 + 0.5 / 46)], "#FFD8A0" if lit else "#A68496", ' opacity="0.85"'))
        # balustrades: sloped top, outer side faces
        for side in (-1, 1):
            a0, a1 = side * st, side * sw
            out.append(Q([sp(a0, 0, 1.2), sp(a1, 0, 1.2), sp(a1, 1, 1.2), sp(a0, 1, 1.2)], "#FFE0B0" if lit else "#B898A8"))
            out.append(Q([sp(a0, 0, 0), sp(a0, 0, 1.2), sp(a0, 1, 1.2), sp(a0, 1, 0)], "#C88A60" if lit else "#6E5672"))
            if face == "north" and side == 1:
                # the western balustrade of the north stair: in shade but for the seven triangles of light
                outer = [sp(a1, 0, 1.2), sp(a1, 1, 1.2), sp(a1, 1, -2.4), sp(a1, 0, -1.2)]
                out.append(Q(outer, "#7A5A72"))
                for j in range(7):
                    t0, t1 = 0.06 + j * 0.13, 0.06 + j * 0.13 + 0.11
                    tri = [sp(a1, t0, -1.0 - 1.2 * t0), sp(a1, t1, -1.0 - 1.2 * t1), sp(a1, (t0 + t1) / 2, 1.1)]
                    out.append(Q(tri, "#FFD08A"))
                    out.append(Q([sp(a1, t0 + 0.02, -0.9 - 1.2 * t0), sp(a1, t1 - 0.02, -0.9 - 1.2 * t1), sp(a1, (t0 + t1) / 2, 0.6)], "#FFF0C8", ' opacity="0.7"'))
            if face == "west" and side == -1:
                outer = [sp(a1, 0, 1.2), sp(a1, 1, 1.2), sp(a1, 1, -2.4), sp(a1, 0, -1.2)]
                out.append(Q(outer, "#E09A68"))
        # serpent heads at the foot of the north stair
        if face == "north":
            for side in (-1, 1):
                hx, hy = sp(side * (st + 0.5), -0.03)
                s_ = C.f / (Zc - foot * math.cos(th) - side * 5 * math.sin(th)) * 0.9
                col = "#FFC88A" if side == 1 else "#9A7A8E"
                out.append(f'<g transform="translate({hx:.1f} {hy:.1f}) scale({s_ / 10:.2f})">'
                           f'<path d="M -10 0 L -11 -7 Q -11 -13 -6 -14 L 7 -14 Q 12 -13 12 -7 L 11 0 Z" fill="{col}"/>'
                           f'<path d="M -11 -7 Q -11 -13 -6 -14 L 7 -14 Q 12 -13 12 -7 Q 6 -10 0 -10 Q -6 -10 -11 -7 Z" fill="{mix(col, "#FFFFFF", 0.2)}"/>'
                           '<path d="M -9 -5 Q 0 -7 10 -5 L 9.4 -1.4 Q 0 -2.6 -8.4 -1.4 Z" fill="#3A2434"/>'
                           '<g fill="#E8D8C4"><path d="M -6 -5.6 l 1 2.4 l 1 -2.6 Z M 5 -5.6 l 1 2.4 l 1 -2.6 Z"/></g>'
                           '<path d="M -7 -11 q 2 -1.4 4 0 M 4 -11 q 2 -1.4 4 0" stroke="#3A2434" stroke-width="1.2" fill="none"/>'
                           '<path d="M -1.4 -14 Q 0 -17 1.6 -14" stroke="#3A2434" stroke-width="1" fill="none" opacity="0.7"/></g>')
    # the temple on top: north facade with serpent-column doorway, west wall in the sun
    tw_, ty0, ty1 = 6.6, H, H + 6.2
    out.append(Q([p(tw_, -tw_, ty0), p(tw_, tw_, ty0), p(tw_, tw_, ty1), p(tw_, -tw_, ty1)], "#F8BC80"))
    out.append(Q([p(-tw_, tw_, ty0), p(tw_, tw_, ty0), p(tw_, tw_, ty1), p(-tw_, tw_, ty1)], "#9C7C92"))
    # doorways
    for a in (-3.4, 0, 3.4):
        out.append(Q([p(a - 1.0, tw_, ty0), p(a + 1.0, tw_, ty0), p(a + 1.0, tw_, ty0 + 3.0), p(a - 1.0, tw_, ty0 + 3.0)], "#3A2434"))
    for a in (-1.7, 1.7):
        out.append(Q([p(a - 0.4, tw_ + 0.05, ty0), p(a + 0.4, tw_ + 0.05, ty0), p(a + 0.4, tw_ + 0.05, ty0 + 3.2), p(a - 0.4, tw_ + 0.05, ty0 + 3.2)], "#B4949E"))
    out.append(Q([p(tw_, -1.2, ty0), p(tw_, 1.2, ty0), p(tw_, 1.2, ty0 + 3.0), p(tw_, -1.2, ty0 + 3.0)], "#4A2A34"))
    # frieze and cornice
    for face in ("west", "north"):
        if face == "north":
            band = [p(-tw_, tw_ + 0.2, ty0 + 3.8), p(tw_, tw_ + 0.2, ty0 + 3.8), p(tw_, tw_ + 0.2, ty0 + 5.2), p(-tw_, tw_ + 0.2, ty0 + 5.2)]
            cor = [p(-tw_ - 0.3, tw_ + 0.3, ty1 - 0.4), p(tw_ + 0.3, tw_ + 0.3, ty1 - 0.4), p(tw_ + 0.3, tw_ + 0.3, ty1), p(-tw_ - 0.3, tw_ + 0.3, ty1)]
            out.append(Q(band, "#7A5E78") + Q(cor, "#C4A4B0"))
            out.append("".join(Q([p(a, tw_ + 0.25, ty0 + 4.0), p(a + 0.7, tw_ + 0.25, ty0 + 4.0), p(a + 0.7, tw_ + 0.25, ty0 + 5.0), p(a, tw_ + 0.25, ty0 + 5.0)], "#5A4060") for a in [-6 + i * 1.6 for i in range(8)]))
        else:
            band = [p(tw_ + 0.2, -tw_, ty0 + 3.8), p(tw_ + 0.2, tw_, ty0 + 3.8), p(tw_ + 0.2, tw_, ty0 + 5.2), p(tw_ + 0.2, -tw_, ty0 + 5.2)]
            cor = [p(tw_ + 0.3, -tw_ - 0.3, ty1 - 0.4), p(tw_ + 0.3, tw_ + 0.3, ty1 - 0.4), p(tw_ + 0.3, tw_ + 0.3, ty1), p(tw_ + 0.3, -tw_ - 0.3, ty1)]
            out.append(Q(band, "#E0A070") + Q(cor, "#FFE2B4"))
            out.append("".join(Q([p(tw_ + 0.25, a, ty0 + 4.0), p(tw_ + 0.25, a + 0.7, ty0 + 4.0), p(tw_ + 0.25, a + 0.7, ty0 + 5.0), p(tw_ + 0.25, a, ty0 + 5.0)], "#C47A56") for a in [-6 + i * 1.6 for i in range(8)]))
    # sunlit corner edges
    for a in range(N):
        w0 = B - a * (B - Wt) / N
        x0_, y0_ = p(w0, w0, a * hk)
        x1_, y1_ = p(w0 - 0.9, w0 - 0.9, (a + 1) * hk)
        out.append(f'<line x1="{x0_:.1f}" y1="{y0_:.1f}" x2="{x1_:.1f}" y2="{y1_:.1f}" stroke="#FFE8C0" stroke-width="1.2" opacity="0.7"/>')
    a_, b_ = p(tw_, tw_, ty0), p(tw_, tw_, ty1)
    out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#FFE8C0" stroke-width="1.4" opacity="0.8"/>')
    return "".join(out), p


def chichen_itza():
    u = "ci"
    C = Cam(f=380, cx=329, vpy=318, eye=1.6)
    out = [defs(
        lg(f"{u}-sky", [(0, "#3A3474"), (0.32, "#7A4A86"), (0.6, "#D4687A"), (0.82, "#F6A060"), (1, "#FFD488")], 0, 40, 0, 314, units="userSpaceOnUse"),
        lg(f"{u}-lawn", [(0, "#C0A456"), (0.35, "#80803C"), (1, "#4A4A2C")], 0, 312, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="320" fill="url(#{u}-sky)"/>')
    out.append(glow(560, 300, 340, "#FFC060", f"{u}-sun", 0.95))
    out.append(f'<circle cx="566" cy="300" r="20" fill="#FFE6A8"/><circle cx="566" cy="300" r="15" fill="#FFF4D4"/>')
    # streaks of altocumulus lit from below by the setting sun
    rnd = random.Random(3)
    for i in range(16):
        y = rnd.uniform(70, 230)
        x = rnd.uniform(-40, 600)
        w = rnd.uniform(40, 130)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w:.1f}" ry="{rnd.uniform(3, 7):.1f}" fill="{mix("#7A4A7E", "#F2A48A", (y - 70) / 160)}" opacity="0.75"/>'
                   f'<ellipse cx="{x + 6:.1f}" cy="{y + 2.4:.1f}" rx="{w * 0.85:.1f}" ry="{rnd.uniform(1.4, 2.6):.1f}" fill="#FFC27A" opacity="{0.4 + 0.5 * (y - 70) / 160:.2f}"/>')
    # the flat Yucatán forest on the horizon
    rnd = random.Random(4)
    tl = []
    x = -10
    while x < 610:
        r = rnd.uniform(4, 11)
        tl.append(f'<circle cx="{x:.1f}" cy="{312 - r * rnd.uniform(0.3, 0.9):.1f}" r="{r:.1f}"/>')
        x += r * rnd.uniform(0.8, 1.4)
    out.append(f'<g fill="#6A4E6E">{"".join(tl)}</g><rect x="0" y="306" width="600" height="10" fill="#6A4E6E"/>')
    rnd = random.Random(6)
    tl = []
    x = -10
    while x < 610:
        r = rnd.uniform(3, 8)
        tl.append(f'<circle cx="{x:.1f}" cy="{316 - r * rnd.uniform(0.2, 0.7):.1f}" r="{r:.1f}"/>')
        x += r * rnd.uniform(0.8, 1.4)
    out.append(f'<g fill="#4E3A56">{"".join(tl)}</g>')
    out.append(f'<rect x="0" y="316" width="600" height="130" fill="url(#{u}-lawn)"/>')
    body, p = castillo(C, u)
    # a pale limestone walkway curving across the lawn toward the pyramid
    zs = [4.4, 6, 8, 11, 15, 20, 26, 33, 41]
    cxz = lambda z: 1.2 - 0.004 * (z - 20) ** 2 + 0.05 * z
    path = [C(cxz(z) - 1.1, 0, z) for z in zs] + [C(cxz(z) + 1.1, 0, z) for z in zs[::-1]]
    out.append(Q(path, "#D8C096"))
    out.append(f'<polyline points="{P([C(cxz(z) + 1.1, 0, z) for z in zs])}" stroke="#FFE2B0" stroke-width="1.6" fill="none" opacity="0.8"/>')
    out.append(f'<polyline points="{P([C(cxz(z) - 1.1, 0, z) for z in zs])}" stroke="#5E5A30" stroke-width="1.2" fill="none" opacity="0.5"/>')
    out.append(dots(80, 9, (min(q[0] for q in path), min(q[1] for q in path), max(q[0] for q in path), 444), "#A88E6A", r=(0.6, 1.6), opacity=(0.2, 0.5)))
    # the pyramid's long shadow lying across the plaza toward the east
    sh = [p(27.7, 27.7, 0), p(-27.7, 27.7, 0), p(-27.7, -27.7, 0)]
    out.append(Q([sh[0], sh[1], (sh[1][0] - 260, sh[1][1] + 26), (sh[0][0] - 220, sh[0][1] + 34)], "#2A2440", ' opacity="0.35"'))
    out.append(body)
    # warm glow of the sun grazing the lawn, long-shadowed visitors
    out.append(glow(470, 340, 200, "#FFB860", f"{u}-g2", 0.35))
    rnd = random.Random(8)
    for px, py, h, c in ((150, 352, 15, "#F2F0EA"), (162, 354, 13, "#E8543E"), (420, 348, 14, "#2E8AB8"), (434, 350, 12, "#F2C230"), (360, 372, 20, "#F2F0EA"), (372, 374, 17, "#C83A6A")):
        out.append(f'<path d="M {px:.1f} {py:.1f} L {px - h * 4:.1f} {py + h * 0.35:.1f} L {px - h * 4 + 3:.1f} {py + h * 0.35 + 2:.1f} L {px + 2:.1f} {py + 1:.1f} Z" fill="#2A2440" opacity="0.35"/>')
        out.append(person(px, py, h, c, "#3A3040", skin="#7A4A3A", hair="#2A1E1A", rim="#FFD08A"))
    # mown lawn of the Great Plaza: soft mowing stripes, a few longer tufts at the edges
    for i in range(7):
        y0 = 330 + i * 16 + i * i * 1.2
        out.append(f'<path d="M -10 {y0:.1f} Q 300 {y0 - 4:.1f} 610 {y0 + 2:.1f} L 610 {y0 + 7 + i * 1.6:.1f} Q 300 {y0 + 3 + i * 1.6:.1f} -10 {y0 + 7 + i * 1.6:.1f} Z" fill="#E8C478" opacity="0.1"/>')
    out.append(grass(70, 10, (-10, 330, 610, 444), ["#C8A85A", "#6E6A34", "#E8C478"], h=(2, 5), sw=1.2))
    out.append(grass(50, 11, (-10, 410, 200, 444), ["#C8A85A", "#5E5A2E", "#E8C478"], h=(8, 18), sw=1.5))
    out.append(grass(40, 13, (430, 400, 610, 444), ["#C8A85A", "#5E5A2E", "#E8C478"], h=(8, 18), sw=1.5))
    # an agave on the right, rim-lit
    ax, ay = 528, 444
    for a, L, c in ((-150, 52, "#4E6A5A"), (-130, 64, "#5E7E6A"), (-110, 70, "#6E8E78"), (-90, 76, "#5E7E6A"), (-70, 70, "#4E6E5E"), (-50, 64, "#6E8E78"), (-30, 52, "#5E7E6A")):
        r = math.radians(a)
        ex, ey = ax + L * math.cos(r), ay + L * math.sin(r)
        nx, ny = -math.sin(r) * 6, math.cos(r) * 6
        out.append(f'<path d="M {ax + nx:.1f} {ay + ny:.1f} Q {(ax + ex) / 2 + nx:.1f} {(ay + ey) / 2 + ny:.1f} {ex:.1f} {ey:.1f} Q {(ax + ex) / 2 - nx:.1f} {(ay + ey) / 2 - ny:.1f} {ax - nx:.1f} {ay - ny:.1f} Z" fill="{c}"/>'
                   f'<path d="M {ax:.1f} {ay:.1f} Q {(ax + ex) / 2 + nx * 0.6:.1f} {(ay + ey) / 2 + ny * 0.6:.1f} {ex:.1f} {ey:.1f}" stroke="#FFC888" stroke-width="1.2" fill="none" opacity="0.8"/>')
    # a branch reaching in from the right, backlit, with a motmot watching the sunset
    out.append('<path d="M 610 112 Q 570 118 540 128 Q 510 138 470 140" stroke="#2A1A26" stroke-width="6" fill="none" stroke-linecap="round"/>'
               '<path d="M 560 122 Q 556 104 562 88 M 520 134 Q 508 124 506 110 M 590 116 Q 600 98 612 92" stroke="#2A1A26" stroke-width="3" fill="none" stroke-linecap="round"/>'
               '<path d="M 610 115 Q 570 121 540 131 Q 510 141 470 143" stroke="#FFB070" stroke-width="1.4" fill="none" opacity="0.8"/>')
    rnd = random.Random(12)
    leaves = []
    for _ in range(44):
        lx, ly = rnd.uniform(470, 620), rnd.uniform(60, 150)
        if lx < 520 and ly > 120:
            continue
        a = rnd.uniform(0, 360)
        rx = rnd.uniform(6, 11)
        leaves.append(f'<ellipse cx="{lx:.1f}" cy="{ly:.1f}" rx="{rx:.1f}" ry="{rx * 0.36:.1f}" transform="rotate({a:.0f} {lx:.1f} {ly:.1f})" fill="{rnd.choice(["#2A2030", "#34283A", "#1E1824"])}"/>')
        if rnd.random() < 0.5:
            leaves.append(f'<ellipse cx="{lx + 1:.1f}" cy="{ly + 0.6:.1f}" rx="{rx * 0.8:.1f}" ry="{rx * 0.1:.1f}" transform="rotate({a:.0f} {lx:.1f} {ly:.1f})" fill="#FF9A60" opacity="0.6"/>')
    out.append(f'<g>{"".join(leaves[:30])}</g>')
    out.append(motmot(500, 132, 1.7))
    out.append(f'<g>{"".join(leaves[30:])}</g>')
    out.append(gulls([(120, 112, 9), (146, 124, 7), (102, 132, 6)], "#2A2040", sw=1.8))
    return "\n".join(out)


# ================================================================ CARTAGENA — the walled city at late morning: balconies, bougainvillea, a palenquera
def bougainvillea(n, seed, box, cols=("#E8287A", "#C81E6A", "#FF5AA0", "#A8185A"), leaf=("#2E6A2E", "#3E8A3A"), r=(1.6, 3.4), droop=0.0, sun=(1, -1)):
    """Clusters of papery magenta bracts with a few leaves: each bloom is three overlapping petals, lit on the sun side."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    lv, fl = [], []
    for _ in range(n):
        x = rnd.uniform(x0, x1)
        y = rnd.uniform(y0, y1) + droop * (x - x0)
        rr = rnd.uniform(*r)
        if rnd.random() < 0.3:
            a = rnd.uniform(0, 360)
            lv.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rr * 1.3:.1f}" ry="{rr * 0.6:.1f}" transform="rotate({a:.0f} {x:.1f} {y:.1f})" fill="{rnd.choice(leaf)}"/>')
        c = rnd.choice(cols)
        for k in range(3):
            a = math.radians(k * 120 + rnd.uniform(0, 40))
            fl.append(f'<circle cx="{x + rr * 0.55 * math.cos(a):.1f}" cy="{y + rr * 0.55 * math.sin(a):.1f}" r="{rr * 0.62:.1f}" fill="{c}"/>')
        fl.append(f'<circle cx="{x + sun[0] * rr * 0.35:.1f}" cy="{y + sun[1] * rr * 0.35:.1f}" r="{rr * 0.38:.1f}" fill="#FF9AC8" opacity="0.7"/>')
        if rnd.random() < 0.4:
            fl.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{max(0.5, rr * 0.16):.1f}" fill="#FFF4D0"/>')
    return "".join(lv) + "".join(fl)


def palenquera(x, base, h, flip=False):
    """Palenquera fruit seller in a ruffled dress in the flag's yellow, blue and red, balancing a basin of tropical
    fruit on her head, one hand steadying it. Unit body 100 tall (feet to crown), basin above."""
    s = h / 100
    sx = -s if flip else s
    skin, skin_d, skin_l = "#6A3E26", "#4A2A1A", "#9A6440"
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({sx:.3f} {s:.3f})">']
    g.append('<ellipse cx="6" cy="0.5" rx="30" ry="3.4" fill="#2A2040" opacity="0.3"/>')
    # legs and sandals
    g.append(f'<path d="M -6 -20 L -6.5 -2 L -2.4 -2 L -1.6 -20 Z M 3 -20 L 4 -2 L 8 -2 L 7.4 -20 Z" fill="{skin}"/>'
             '<path d="M -8 -2.4 L -1.6 -2.4 L -1 0.6 L -8.6 0.6 Z M 3 -2.4 L 9.4 -2.4 L 10 0.6 L 2.4 0.6 Z" fill="#E8C060"/>')
    # ruffled skirt: tiers of yellow, blue and red with white piping
    tiers = [(-50, -38, 12, 17, "#F6C51E"), (-39, -28, 16, 21, "#1E4EA8"), (-29, -17, 20, 25, "#D8282E")]
    for y0, y1, w0, w1, c in tiers:
        d = f"M {-w0} {y0} L {w0} {y0} L {w1} {y1} "
        n = 7
        for i in range(n):
            xa = w1 - 2 * w1 * i / n
            xb = w1 - 2 * w1 * (i + 1) / n
            d += f"Q {(xa + xb) / 2:.1f} {y1 + 3.4:.1f} {xb:.1f} {y1} "
        d += "Z"
        g.append(f'<path d="{d}" fill="{c}"/>')
        g.append(f'<path d="M {-w1 * 0.1:.1f} {y0} L {w1 * 0.25:.1f} {y1} L {w1:.1f} {y1} L {w0:.1f} {y0} Z" fill="#000" opacity="0.13"/>')
        g.append(f'<path d="M {-w0} {y0 + 0.6} L {w0} {y0 + 0.6}" stroke="#FFFFFF" stroke-width="1" opacity="0.85"/>')
        g.append(f'<g fill="none" stroke="#000" stroke-width="0.6" opacity="0.25">' + "".join(
            f'<path d="M {-w0 + (2 * w0) * (i + 0.5) / 6:.1f} {y0 + 1} L {-w1 + (2 * w1) * (i + 0.5) / 6:.1f} {y1}"/>' for i in range(6)) + "</g>")
    # bodice: off-shoulder ruffle top in white with a yellow trim
    g.append('<path d="M -11 -73 Q -12 -60 -12 -50 L 12 -50 Q 12 -60 11 -73 Q 0 -76 -11 -73 Z" fill="#F6C51E"/>'
             '<path d="M 4 -75 Q 11 -73 11 -66 L 12 -50 L 6 -50 Z" fill="#000" opacity="0.12"/>'
             '<path d="M -14 -75 Q -8 -70 0 -72 Q 8 -70 14 -75 Q 16 -70 13 -66 Q 6 -64 0 -66 Q -6 -64 -13 -66 Q -16 -70 -14 -75 Z" fill="#FFFFFF"/>'
             '<path d="M -13 -66.4 Q -6 -64.4 0 -66.4 Q 6 -64.4 13 -66.4" stroke="#1E4EA8" stroke-width="1.4" fill="none"/>'
             '<path d="M -12 -51 L 12 -51" stroke="#D8282E" stroke-width="2.4"/>')
    # neck, shoulders, the lowered arm with a little cloth bag
    g.append(f'<path d="M -3.4 -80 L 3.4 -80 L 4 -74 L -4 -74 Z" fill="{skin}"/>'
             f'<path d="M -13 -74 Q -18 -62 -17 -48 L -13 -48 Q -13.6 -60 -10 -70 Z" fill="{skin}"/>'
             f'<circle cx="-15" cy="-46.6" r="2.6" fill="{skin}"/>'
             '<path d="M -18 -44 L -12 -44 L -11 -34 L -19 -34 Z" fill="#F2EEE2"/><path d="M -18 -44 Q -15 -48 -12 -44" stroke="#C8A060" stroke-width="0.9" fill="none"/>')
    # raised arm steadying the basin
    g.append(f'<path d="M 12 -73 Q 20 -82 19 -96 L 15.6 -96 Q 16 -84 9.6 -76 Z" fill="{skin}"/>'
             f'<path d="M 13.4 -96 Q 17 -100 21 -97 L 20 -94 L 14.6 -94 Z" fill="{skin}"/>'
             f'<path d="M 18.6 -82 Q 19.6 -88 19 -95" stroke="{skin_l}" stroke-width="1" fill="none" opacity="0.8"/>')
    # head with headscarf and big hoop earrings, smiling
    g.append(f'<ellipse cx="0" cy="-87" rx="7.4" ry="8.4" fill="{skin}"/>'
             f'<path d="M 4 -94 Q 8 -90 7 -82 Q 4 -79 2 -79.6 Q 6 -86 4 -94 Z" fill="{skin_d}" opacity="0.5"/>'
             '<path d="M -7.8 -88 Q -9 -98 0 -98.6 Q 9 -98 7.8 -88 Q 4 -93 0 -93 Q -4 -93 -7.8 -88 Z" fill="#D8282E"/>'
             '<path d="M -7.8 -90 Q 0 -93.6 7.8 -90" stroke="#F6C51E" stroke-width="1.2" fill="none"/>'
             '<path d="M 6 -92 Q 10 -94 11 -90 Q 9 -91 7 -89 Z" fill="#D8282E"/>'
             '<circle cx="-7.4" cy="-83.6" r="2" fill="none" stroke="#F2C230" stroke-width="0.9"/>'
             '<path d="M -4.6 -87.4 q 1.2 -1 2.4 0 M 1.6 -87.4 q 1.2 -1 2.4 0" stroke="#1E120E" stroke-width="0.9" fill="none"/>'
             '<path d="M -2.6 -82.6 Q 0 -80.4 2.6 -82.6" stroke="#F4E8E0" stroke-width="1.1" fill="none"/>'
             '<path d="M -2.8 -82.8 Q 0 -80 2.8 -82.8" stroke="#3A1810" stroke-width="0.5" fill="none"/>'
             f'<circle cx="-3.6" cy="-84.4" r="1.2" fill="{skin_l}" opacity="0.5"/>')
    # aluminium basin piled with fruit
    g.append('<ellipse cx="2" cy="-99" rx="5" ry="1.6" fill="#E8E0D0"/>'
             '<path d="M -20 -104 L 24 -104 L 19 -98 Q 2 -95.4 -15 -98 Z" fill="#C4CCD4"/><path d="M -20 -104 L 24 -104 L 23 -102 L -19 -102 Z" fill="#EEF2F4"/>'
             '<path d="M 10 -104 L 24 -104 L 19 -98 Q 14 -97 10 -96.8 Z" fill="#8A949E" opacity="0.6"/>')
    # pineapple, papaya halves, mangos, bananas, watermelon wedge, limes
    g.append('<path d="M -2 -104 Q -4 -116 1 -120 Q 6 -116 5 -104 Z" fill="#D8A02E"/>'
             '<g stroke="#8A5A1A" stroke-width="0.6" opacity="0.7"><path d="M -2.4 -110 L 4.8 -116 M -2.6 -106 L 5 -112 M 4.6 -108 L -1 -116 M 4.8 -105 L -2.6 -112"/></g>'
             '<path d="M 1.4 -120 L -3 -129 L 0.4 -122 L 1 -131 L 2.4 -122 L 6 -129 L 3 -120 Z" fill="#3E8A3A"/>'
             '<ellipse cx="-12" cy="-106" rx="7" ry="4.4" fill="#F28A2E"/><ellipse cx="-12" cy="-106.4" rx="5" ry="2.8" fill="#FF7A3A"/>'
             '<g fill="#1E1A1A"><circle cx="-13.4" cy="-106.6" r="0.6"/><circle cx="-11.6" cy="-106" r="0.6"/><circle cx="-12.4" cy="-107.4" r="0.6"/><circle cx="-10.6" cy="-107" r="0.6"/></g>'
             '<path d="M 7 -105 Q 12 -112 20 -110 Q 16 -108 9 -104 Z" fill="#F6D23A"/><path d="M 8 -104.6 Q 13 -110 21 -107.6 Q 16 -106 9 -103.6 Z" fill="#F2C21E"/>'
             '<ellipse cx="17" cy="-106" rx="4" ry="3.4" fill="#F6A02E"/><ellipse cx="18" cy="-107" rx="1.6" ry="1" fill="#FFE070" opacity="0.8"/>'
             '<path d="M -20 -105 L -14 -112 L -8 -105 Z" fill="#2E8A3A"/><path d="M -18.6 -105.6 L -14 -110.6 L -9.4 -105.6 Z" fill="#E8303A"/>'
             '<g fill="#1E1A1A"><circle cx="-14" cy="-107.6" r="0.5"/><circle cx="-15.4" cy="-106.4" r="0.5"/><circle cx="-12.6" cy="-106.4" r="0.5"/></g>'
             '<circle cx="-4" cy="-104" r="2.4" fill="#7AB83A"/><circle cx="12" cy="-103.6" r="2.2" fill="#8AC83A"/><circle cx="-7" cy="-103.4" r="2" fill="#E8303A"/>')
    # sunlight rim on her right side
    g.append(f'<path d="M 7.4 -90 Q 8 -84 5 -80 M 11 -66 Q 12 -58 12 -51 M 19.4 -84 Q 20.4 -90 19.6 -96" stroke="#FFD8A8" stroke-width="1.3" fill="none" opacity="0.8"/>')
    g.append("</g>")
    return "".join(g)


def wood_balcony(C, X, z0, z1, y0, depth, wood="#2E6A3E", wood_l="#5EA05A", roof="#B8503A", uid="wb"):
    """Cartagena's covered timber balcony projecting from the facade in plane X: carved corbels, a floor beam,
    turned balusters, slender posts and a small tiled eave on top."""
    sgn = 1 if X < 0 else -1
    Xo = X + sgn * depth
    F = lambda x, y, z: C(x, y, z)
    out = []
    # shadow thrown on the wall below (sun high on the right)
    out.append(Q([F(X, y0, z0 + 0.4), F(X, y0, z1 + 0.6), F(X, y0 - 1.8, z1 + 1.2), F(X, y0 - 1.8, z0 + 1.0)], "#2A1E3A", ' opacity="0.28"'))
    # corbels
    n = max(3, int((z1 - z0) / 1.1))
    for i in range(n + 1):
        z = z0 + (z1 - z0) * i / n
        out.append(Q([F(X, y0 - 0.9, z), F(X, y0, z), F(Xo, y0, z), F(Xo, y0 - 0.15, z)], mix(wood, "#000000", 0.25)))
    # floor beam: underside and front edge
    out.append(Q([F(X, y0, z0), F(X, y0, z1), F(Xo, y0, z1), F(Xo, y0, z0)], mix(wood, "#000000", 0.35)))
    out.append(Q([F(Xo, y0, z0), F(Xo, y0, z1), F(Xo, y0 + 0.3, z1), F(Xo, y0 + 0.3, z0)], wood))
    # back wall of the balcony: a tall door, shuttered
    out.append(Q([F(X, y0 + 0.3, z0 + 0.4), F(X, y0 + 0.3, z1 - 0.4), F(X, y0 + 2.6, z1 - 0.4), F(X, y0 + 2.6, z0 + 0.4)], "#2A1E28", ' opacity="0.75"'))
    # balusters
    m = max(8, int((z1 - z0) / 0.22))
    bal = []
    for i in range(m + 1):
        z = z0 + (z1 - z0) * i / m
        a, b = F(Xo, y0 + 0.3, z), F(Xo, y0 + 1.1, z)
        bal.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
    sc = C.f / z1
    out.append(f'<g stroke="{wood_l}" stroke-width="{max(0.9, 0.09 * sc):.1f}">{"".join(bal)}</g>')
    out.append(f'<polyline points="{P([F(Xo, y0 + 1.1, z0), F(Xo, y0 + 1.1, z1)])}" stroke="{wood}" stroke-width="{max(1.4, 0.14 * sc):.1f}" fill="none"/>')
    out.append(f'<polyline points="{P([F(Xo, y0 + 0.55, z0), F(Xo, y0 + 0.55, z1)])}" stroke="{wood}" stroke-width="{max(0.8, 0.06 * sc):.1f}" fill="none"/>')
    # posts and the eave
    for i in range(0, n + 1, 2):
        z = z0 + (z1 - z0) * i / n
        a, b = F(Xo, y0 + 1.1, z), F(Xo, y0 + 2.7, z)
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{wood}" stroke-width="{max(1, 0.1 * C.f / z):.1f}"/>')
    # the eave seen from below: timber soffit with rafters, a terracotta tile edge
    Xe = Xo + sgn * 0.35
    out.append(Q([F(X, y0 + 3.0, z0 - 0.2), F(X, y0 + 3.0, z1 + 0.2), F(Xe, y0 + 2.85, z1 + 0.2), F(Xe, y0 + 2.85, z0 - 0.2)], mix(wood, "#2A1A1A", 0.55)))
    k = max(4, int((z1 - z0) / 0.45))
    out.append(f'<g stroke="{mix(wood, "#000000", 0.7)}" stroke-width="{max(0.7, 0.05 * C.f / z1):.1f}" opacity="0.8">' + "".join(
        f'<line x1="{F(X, y0 + 3.0, z0 + (z1 - z0) * j / k)[0]:.1f}" y1="{F(X, y0 + 3.0, z0 + (z1 - z0) * j / k)[1]:.1f}" x2="{F(Xe, y0 + 2.85, z0 + (z1 - z0) * j / k)[0]:.1f}" y2="{F(Xe, y0 + 2.85, z0 + (z1 - z0) * j / k)[1]:.1f}"/>'
        for j in range(k + 1)) + "</g>")
    out.append(Q([F(Xe, y0 + 2.85, z0 - 0.2), F(Xe, y0 + 2.85, z1 + 0.2), F(Xe, y0 + 3.15, z1 + 0.2), F(Xe, y0 + 3.15, z0 - 0.2)], roof))
    out.append(Q([F(Xe, y0 + 2.85, z0 - 0.2), F(Xe, y0 + 2.85, z1 + 0.2), F(Xe, y0 + 2.95, z1 + 0.2), F(Xe, y0 + 2.95, z0 - 0.2)], mix(roof, "#000000", 0.35)))
    return "".join(out)


def ct_facade(C, X, z0, z1, h, wall, seed, lit, uid, door=None, grille="#2E5A8A", knocker=False):
    """Colonial house front in plane X: a big wooden double door with studs, barred window grilles (rejas) on the
    ground floor, white plinth and cornice, painted render with sun-faded patches."""
    rnd = random.Random(seed)
    F = lambda z, y, dx=0: C(X + (dx if X < 0 else -dx), y, z)
    poly = lambda pts, dx=0: [F(z, y, dx) for z, y in pts]
    out = [f'<clipPath id="{uid}"><polygon points="{P(poly([(z0, 0), (z0, h), (z1, h), (z1, 0)]))}"/></clipPath>',
           Q(poly([(z0, 0), (z0, h), (z1, h), (z1, 0)]), wall)]
    g = []
    W = z1 - z0
    for _ in range(int(W * 5)):
        z, y, r = z0 + W * rnd.random(), rnd.uniform(0.3, h), rnd.uniform(0.2, 0.7)
        pts = [(z + r * math.cos(t) * rnd.uniform(0.5, 1.2), y + r * 0.7 * math.sin(t) * rnd.uniform(0.5, 1.2)) for t in [i * math.pi / 4 for i in range(8)]]
        g.append(Q(poly(pts), rnd.choice([mix(wall, "#FFFFFF", 0.2), mix(wall, "#8A4A2A", 0.12)]), f' opacity="{rnd.uniform(0.2, 0.45):.2f}"'))
    out.append(f'<g clip-path="url(#{uid})">{"".join(g)}</g>')
    out.append(Q(poly([(z0, 0), (z0, 0.7), (z1, 0.7), (z1, 0)]), "#F4F0E6"))
    out.append(Q(poly([(z0, h - 0.6), (z0, h), (z1, h), (z1, h - 0.6)]), "#F8F4EA"))
    out.append(Q(poly([(z0, h - 0.8), (z0, h - 0.6), (z1, h - 0.6), (z1, h - 0.8)]), "#000000", ' opacity="0.15"'))
    out.append(Q(poly([(z0, 4.2), (z0, 4.5), (z1, 4.2 + 0.3), (z1, 4.2)]), "#F8F4EA", ' opacity="0.9"'))
    if door:
        za, zb = door
        zm = (za + zb) / 2
        out.append(Q(poly([(za - 0.35, 0), (za - 0.35, 3.75), (zb + 0.35, 3.75), (zb + 0.35, 0)]), "#F8F4EA"))
        out.append(Q(poly([(za, 0), (za, 3.4), (zb, 3.4), (zb, 0)]), "#6A3A24"))
        out.append(Q(poly([(zm, 0), (zm, 3.4), (zb, 3.4), (zb, 0)]), "#5A2E1C"))
        for j in range(3):
            for zz in (za + (zm - za) * 0.15, zm + (zb - zm) * 0.15):
                ya, yb = 0.3 + j * 1.05, 1.15 + j * 1.05
                out.append(Q(poly([(zz, ya), (zz, yb), (zz + (zm - za) * 0.7, yb), (zz + (zm - za) * 0.7, ya)]), "#7E4A2E"))
                out.append(f'<polyline points="{P(poly([(zz, yb), (zz + (zm - za) * 0.7, yb)]))}" stroke="#3A1E14" stroke-width="0.9" fill="none"/>')
        studs = "".join(f'<circle cx="{F(z_, y_)[0]:.1f}" cy="{F(z_, y_)[1]:.1f}" r="{0.05 * C.f / z_:.1f}"/>'
                        for z_ in [za + (zb - za) * (i + 0.5) / 10 for i in range(10)] for y_ in (0.2, 1.25, 2.3, 3.3))
        out.append(f'<g fill="#E8C060">{studs}</g>')
        if knocker:
            kx, ky_ = F(za + (zm - za) * 0.5, 1.9)
            sk = 0.11 * C.f / zm
            # a brass iguana knocker, as on the old doors of the walled city
            out.append(f'<g transform="translate({kx:.1f} {ky_:.1f}) scale({sk / 6:.2f})" fill="#F2C24A" stroke="#8A6A1E" stroke-width="0.6">'
                       '<path d="M 0 -10 Q 3 -8 2 -4 Q 4 0 2 4 Q 3 8 0 12 Q -3 8 -2 4 Q -4 0 -2 -4 Q -3 -8 0 -10 Z"/>'
                       '<path d="M -2 -2 L -6 -4 M 2 -2 L 6 -4 M -2 5 L -6 7 M 2 5 L 6 7 M 0 12 Q 2 16 -1 19" fill="none" stroke-width="1.4" stroke="#C8962E"/>'
                       '<circle cx="0" cy="2" r="5.6" fill="none" stroke-width="1.4"/></g>')
    return "".join(out)


def iguana(x, y, s, body="#6E9A4A", dark="#3E5E2E", lit="#B8D07A", flip=False):
    """Green iguana basking: long banded tail, dorsal crest of spines, dewlap, splayed legs."""
    sx = -s if flip else s
    tail = [(14, -3), (26, -1), (40, 1), (54, 0), (66, -3)]
    t = "".join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{body if i % 2 == 0 else dark}" stroke-width="{5 - i * 1.1:.1f}" stroke-linecap="round"/>' for i, (a, b) in enumerate(zip(tail, tail[1:])))
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({sx:.2f} {s:.2f})">'
            '<ellipse cx="10" cy="1" rx="34" ry="2.4" fill="#2A2050" opacity="0.25"/>' + t +
            f'<path d="M -16 -6 Q -18 -11 -12 -12 L 0 -11 Q 12 -11 16 -6 Q 14 -1 2 -1 L -10 -2 Q -16 -2 -16 -6 Z" fill="{body}"/>'
            f'<path d="M -10 -2 L 2 -1 Q 14 -1 16 -6 Q 10 -4 -2 -4 Q -8 -4 -10 -2 Z" fill="{dark}" opacity="0.6"/>'
            f'<path d="M -22 -9 Q -24 -14 -18 -14 L -12 -12 Q -12 -7 -16 -6 L -22 -6 Z" fill="{body}"/>'
            f'<path d="M -17 -6 Q -17 -1 -13 -1 L -12 -6 Z" fill="#E8B060"/>'
            '<circle cx="-18.4" cy="-11" r="1" fill="#1E1A1A"/><circle cx="-14" cy="-9" r="1.6" fill="#D8C890"/>'
            f'<g fill="{dark}">' + "".join(f'<path d="M {-14 + i * 3:.1f} {-11.6 - (0.4 if i < 6 else 0):.1f} l 1.2 -2.6 l 1.2 2.6 Z"/>' for i in range(9)) + '</g>'
            f'<path d="M -8 -3 L -11 2 L -14 2 M 8 -3 L 11 2 L 14 2" stroke="{body}" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
            f'<path d="M -12 -12 L 0 -11 Q 12 -11 16 -6" stroke="{lit}" stroke-width="1.2" fill="none"/>'
            '<g stroke="#3E5E2E" stroke-width="0.8" opacity="0.6"><path d="M -4 -10 l -1 6 M 2 -10 l -1 7 M 8 -9 l -1 6"/></g></g>')


def cartagena():
    u = "cg"
    C = Cam(f=300, cx=372, vpy=300, eye=1.6)
    out = [defs(
        lg(f"{u}-sky", [(0, "#1468B8"), (0.55, "#4CA6DE"), (1, "#A8DCF0")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-road", [(0, "#A89C94"), (1, "#7E7272")], 0, 300, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="320" fill="url(#{u}-sky)"/>')
    out.append(glow(560, 40, 260, "#FFFFFF", f"{u}-sun", 0.55))
    out.append(cumulus(f"{u}-c1", 390, 96, 130, 34, 41, "#FFFFFF", "#F2F6FA", "#B4C8DE", hi="#FFFFFF", hi_op=0.8, light=1))
    out.append(cumulus(f"{u}-c2", 520, 150, 90, 22, 42, "#FFFFFF", "#F2F6FA", "#B8CCE0", hi="#FFFFFF", light=1))
    # the cathedral's bell tower closing the street, cupola glowing ochre in the sun
    tx, tb = C(0.6, 0, 92)[0], C(0, 0, 92)[1]
    s_ = C.f / 92
    tw = 7 * s_
    out.append(f'<rect x="{tx - tw / 2:.1f}" y="{tb - 30 * s_:.1f}" width="{tw:.1f}" height="{30 * s_:.1f}" fill="#E8B04A"/>'
               f'<rect x="{tx + tw * 0.15:.1f}" y="{tb - 30 * s_:.1f}" width="{tw * 0.35:.1f}" height="{30 * s_:.1f}" fill="#FFD27A" opacity="0.6"/>')
    for yy in (24, 18):
        out.append(f'<rect x="{tx - tw / 2 - 0.6 * s_:.1f}" y="{tb - yy * s_:.1f}" width="{tw + 1.2 * s_:.1f}" height="{0.8 * s_:.1f}" fill="#FFF4DC"/>')
    out.append(f'<path d="M {tx - tw * 0.32:.1f} {tb - 29 * s_:.1f} L {tx - tw * 0.32:.1f} {tb - 25.6 * s_:.1f} L {tx + tw * 0.32:.1f} {tb - 25.6 * s_:.1f} L {tx + tw * 0.32:.1f} {tb - 29 * s_:.1f} Q {tx:.1f} {tb - 31 * s_:.1f} {tx - tw * 0.32:.1f} {tb - 29 * s_:.1f} Z" fill="#3A2A30"/>'
               f'<rect x="{tx - tw / 2 - 0.6 * s_:.1f}" y="{tb - 31 * s_:.1f}" width="{tw + 1.2 * s_:.1f}" height="{1.2 * s_:.1f}" fill="#FFF4DC"/>'
               f'<path d="M {tx - tw * 0.48:.1f} {tb - 31 * s_:.1f} Q {tx - tw * 0.48:.1f} {tb - 38 * s_:.1f} {tx:.1f} {tb - 39 * s_:.1f} Q {tx + tw * 0.48:.1f} {tb - 38 * s_:.1f} {tx + tw * 0.48:.1f} {tb - 31 * s_:.1f} Z" fill="#E87A3A"/>'
               f'<path d="M {tx:.1f} {tb - 39 * s_:.1f} Q {tx + tw * 0.48:.1f} {tb - 38 * s_:.1f} {tx + tw * 0.48:.1f} {tb - 31 * s_:.1f} L {tx + tw * 0.1:.1f} {tb - 31 * s_:.1f} Z" fill="#FFA05A" opacity="0.7"/>'
               f'<g stroke="#FFF4DC" stroke-width="1"><path d="M {tx - tw * 0.24:.1f} {tb - 31 * s_:.1f} Q {tx - tw * 0.22:.1f} {tb - 37 * s_:.1f} {tx:.1f} {tb - 39 * s_:.1f} M {tx + tw * 0.24:.1f} {tb - 31 * s_:.1f} Q {tx + tw * 0.22:.1f} {tb - 37 * s_:.1f} {tx:.1f} {tb - 39 * s_:.1f}"/></g>'
               f'<rect x="{tx - 0.9 * s_:.1f}" y="{tb - 42.6 * s_:.1f}" width="{1.8 * s_:.1f}" height="{3.6 * s_:.1f}" fill="#FFF4DC"/>'
               f'<path d="M {tx:.1f} {tb - 47 * s_:.1f} L {tx:.1f} {tb - 42.6 * s_:.1f} M {tx - 1.2 * s_:.1f} {tb - 45.6 * s_:.1f} L {tx + 1.2 * s_:.1f} {tb - 45.6 * s_:.1f}" stroke="#3A2A30" stroke-width="1.2"/>')
    # street and its stone paving
    road = [C(-3.6, 0, 2), C(3.6, 0, 2), C(3.6, 0, 92), C(-3.6, 0, 92)]
    out.append(Q(road, f"url(#{u}-road)"))
    for X, sgn in ((-5, 1), (5, -1)):
        walk = [C(X, 0, 2), C(X, 0, 92), C(X + sgn * 1.4, 0, 92), C(X + sgn * 1.4, 0, 2)]
        out.append(Q(walk, "#C8BCB0"))
        out.append(f'<polyline points="{P([C(X + sgn * 1.4, 0, 2), C(X + sgn * 1.4, 0, 92)])}" stroke="#F2EADE" stroke-width="1.6" fill="none"/>')
    rnd = random.Random(43)
    st = []
    for i in range(70):
        z = 2.2 * 1.05 ** i
        if z > 90:
            break
        y_ = C(0, 0, z)[1]
        st.append(f'<line x1="{C(-3.6, 0, z)[0]:.1f}" y1="{y_:.1f}" x2="{C(3.6, 0, z)[0]:.1f}" y2="{y_:.1f}"/>')
        for j in range(5):
            xx = -3.6 + 7.2 * (j + rnd.random()) / 5
            a, b = C(xx, 0, z), C(xx, 0, z * 1.05)
            st.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
    out.append(f'<g stroke="#5E5458" stroke-width="0.8" opacity="0.45">{"".join(st)}</g>')
    # shadow of the right-hand houses across the street
    out.append(Q([C(3.6, 0, 2), C(3.6, 0, 92), C(0.8, 0, 92), C(1.4, 0, 30), C(0.4, 0, 12), C(0.6, 0, 2)], "#2A2050", ' opacity="0.25"'))
    # far houses on both sides
    left = [(40, 92, 8.8, "#2E9AC4"), (26, 40, 9.6, "#F2B33A"), (15, 26, 8.6, "#E8654A"), (2.5, 15, 10.4, "#F4D04A")]
    right = [(42, 92, 9.2, "#E8873A"), (28, 42, 8.4, "#5EB88A"), (16, 28, 10.2, "#4A6ED0"), (3, 16, 9.0, "#E85A6E")]
    for i, (z0, z1, h, wall) in enumerate(right):
        out.append(ct_facade(C, 5, z0, z1, h, wall, 60 + i, False, f"{u}-r{i}", door=(z0 + (z1 - z0) * 0.4, z0 + (z1 - z0) * 0.4 + 1.8)))
        out.append(Q([C(5, 0, z0), C(5, h, z0), C(5, h, z1), C(5, 0, z1)], "#2A2050", ' opacity="0.22"'))
        out.append(wood_balcony(C, 5, z0 + 0.6, z1 - 0.6, 4.6, 0.9, wood=["#6A3A24", "#2E5A8A", "#2E6A3E", "#F4F0E6"][i], wood_l=["#A8683E", "#5A8AC4", "#5EA05A", "#FFFFFF"][i], uid=f"{u}-rb{i}"))
        out.append(bougainvillea(int(18 + 160 / z0), 70 + i, (C(5, 7.5, z1 - 1)[0], C(5, 7.6, z0 + 1)[1], C(5, 4, z0 + 0.6)[0], C(5, 4.4, z0 + 1)[1]), r=(0.9 + 6 / z0, 1.6 + 10 / z0)))
    for i, (z0, z1, h, wall) in enumerate(left):
        out.append(ct_facade(C, -5, z0, z1, h, wall, 50 + i, True, f"{u}-l{i}", door=(z0 + (z1 - z0) * 0.5, z0 + (z1 - z0) * 0.5 + 1.9) if i < 3 else (4.4, 6.4), knocker=i == 3))
    # wooden balconies on the sunlit side, each spilling bougainvillea
    for i, (z0, z1, y0, wood, wl) in enumerate(((42, 70, 4.6, "#6A3A24", "#A8683E"), (27, 39, 4.6, "#2E6A3E", "#6EB06A"), (16, 25, 4.6, "#F4F0E6", "#FFFFFF"), (3.2, 14, 4.8, "#2E4E8A", "#6A8EC8"))):
        out.append(wood_balcony(C, -5, z0, z1, y0, 0.9 + (0.2 if i == 3 else 0), wood=wood, wood_l=wl, uid=f"{u}-lb{i}"))
    # bougainvillea cascading from the near balcony and arching over the corner
    out.append(bougainvillea(150, 81, (-10, 30, 150, 120), r=(4, 7.5)))
    out.append(bougainvillea(110, 82, (40, 100, 120, 200), r=(3.4, 6.4), droop=0.6))
    out.append(bougainvillea(60, 83, (100, 170, 140, 250), r=(3, 5.6)))
    out.append(bougainvillea(40, 84, (C(-5, 0, 22)[0] - 6, C(-5, 8, 22)[1], C(-5, 0, 16)[0], C(-5, 5.4, 16)[1]), r=(1.6, 3)))
    out.append(bougainvillea(30, 85, (C(-5, 0, 38)[0] - 4, C(-5, 8, 38)[1], C(-5, 0, 28)[0], C(-5, 5.6, 28)[1]), r=(1.2, 2.4)))
    # a barred window (reja) of turned wood projecting from the near house
    za, zb = 8.6, 11.2
    Xr = -4.65
    out.append(Q([C(-5, 1.0, za), C(-5, 3.2, za), C(-5, 3.2, zb), C(-5, 1.0, zb)], "#2A1E28"))
    out.append(Q([C(-5, 0.9, za - 0.2), C(-5, 0.9, zb + 0.2), C(Xr, 0.9, zb + 0.2), C(Xr, 0.9, za - 0.2)], "#F4F0E6"))
    out.append(Q([C(-5, 3.3, za - 0.2), C(-5, 3.3, zb + 0.2), C(Xr, 3.3, zb + 0.2), C(Xr, 3.3, za - 0.2)], "#5A3420"))
    bars = "".join(f'<line x1="{C(Xr, 0.95, z)[0]:.1f}" y1="{C(Xr, 0.95, z)[1]:.1f}" x2="{C(Xr, 3.3, z)[0]:.1f}" y2="{C(Xr, 3.3, z)[1]:.1f}"/>' for z in [za + (zb - za) * j / 9 for j in range(10)])
    out.append(f'<g stroke="#7A4A2A" stroke-width="2.6">{bars}</g><g stroke="#B8784A" stroke-width="0.9">{bars}</g>')
    out.append(f'<polyline points="{P([C(Xr, 3.3, za), C(Xr, 3.3, zb)])}" stroke="#5A3420" stroke-width="3" fill="none"/>')
    out.append(f'<polyline points="{P([C(Xr, 0.95, za), C(Xr, 0.95, zb)])}" stroke="#5A3420" stroke-width="3" fill="none"/>')
    out.append(Q([C(-5, 1.0, za), C(-5, 0.0, za + 0.6), C(-5, 0.0, zb + 1.4), C(-5, 1.0, zb + 0.6)], "#2A2050", ' opacity="0.15"'))
    # a wall lantern and hanging plant on the near house
    lp = C(-5, 3.8, 15.5)
    out.append(f'<path d="M {lp[0]:.1f} {lp[1]:.1f} l 8 -3 l 0 4" stroke="#1E1A22" stroke-width="1.4" fill="none"/>'
               f'<path d="M {lp[0] + 4:.1f} {lp[1] + 1:.1f} l 8 0 l -1.4 9 l -5.2 0 Z" fill="#1E1A22"/><rect x="{lp[0] + 5.6:.1f}" y="{lp[1] + 2.4:.1f}" width="4.6" height="5.6" fill="#F6F0DA"/>')
    # people in the street: a couple strolling in the distance, a man with a straw sombrero vueltiao in the shade
    for X, Z, h, c, b in ((-1.5, 34, 20, "#F2F0EA", "#2E4E8A"), (-0.9, 36, 18, "#E8303A", "#F2F0EA"), (2.8, 18, 30, "#F4F2EA", "#3A3A48")):
        x_, y_ = C(X, 0, Z)
        out.append(person(x_, y_, C.f * 1.7 / Z * (h / 30) * 0.95, c, b, skin="#7A4A30", hair="#1E1410", hat="#F4ECD8" if Z < 20 else None, rim="#FFE8C0"))
    # an iguana basking on the warm kerb
    out.append(iguana(176, 378, 1.0))
    # the palenquera with her basin of fruit, sunlit, walking toward us
    out.append(palenquera(452, 438, 150))
    out.append(dots(24, 86, (300, 400, 600, 444), "#E8287A", r=(1.2, 2.2), opacity=(0.7, 1)))
    out.append(dots(14, 87, (60, 330, 250, 444), "#E8287A", r=(1.2, 2.4), opacity=(0.7, 1)))
    return "\n".join(out)


# ================================================================ BUENOS AIRES — Caminito, La Boca, at blue hour: tango on the cobbles
def chapa(x0, y0, x1, y1, color, uid, step=3.4, light=0.0):
    """A wall of painted corrugated iron sheet: vertical ridges catching light and shadow, sheet seams, rust spots."""
    rnd = random.Random(int(x0 * 13 + y0))
    out = [f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{color}"/>']
    hi, lo = mix(color, "#FFFFFF", 0.22), mix(color, "#000000", 0.22)
    x = x0 + step * 0.25
    r1, r2 = [], []
    while x < x1:
        r1.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{step * 0.28:.1f}" height="{y1 - y0:.1f}"/>')
        r2.append(f'<rect x="{x + step * 0.5:.1f}" y="{y0:.1f}" width="{step * 0.22:.1f}" height="{y1 - y0:.1f}"/>')
        x += step
    out.append(f'<g fill="{hi}" opacity="0.55">{"".join(r1)}</g><g fill="{lo}" opacity="0.5">{"".join(r2)}</g>')
    # horizontal seams between sheets
    yy = y0 + rnd.uniform(18, 30)
    while yy < y1 - 6:
        out.append(f'<rect x="{x0:.1f}" y="{yy:.1f}" width="{x1 - x0:.1f}" height="1.2" fill="{lo}" opacity="0.6"/>')
        yy += rnd.uniform(26, 36)
    out.append(dots(int((x1 - x0) * (y1 - y0) / 500), int(x0 + y1), (x0, y0, x1, y1), "#8A4A2A", r=(0.5, 1.3), opacity=(0.2, 0.45)))
    if light:
        out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="#FFB860" opacity="{light}"/>')
    return "".join(out)


def window(x, y, w, h, frame, shutter=None, lit=False, open_=False, sill=True):
    """Tall sash window with a painted frame; shutters (persianas) closed, or open on a warm lamp-lit room."""
    out = [f'<rect x="{x - 2:.1f}" y="{y - 2:.1f}" width="{w + 4:.1f}" height="{h + 4:.1f}" fill="{frame}"/>']
    if lit:
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#FFC870"/>'
                   f'<rect x="{x:.1f}" y="{y + h * 0.55:.1f}" width="{w:.1f}" height="{h * 0.45:.1f}" fill="#FFA850"/>'
                   f'<line x1="{x + w / 2:.1f}" y1="{y:.1f}" x2="{x + w / 2:.1f}" y2="{y + h:.1f}" stroke="{frame}" stroke-width="1.6"/>'
                   f'<line x1="{x:.1f}" y1="{y + h * 0.42:.1f}" x2="{x + w:.1f}" y2="{y + h * 0.42:.1f}" stroke="{frame}" stroke-width="1.4"/>')
    else:
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#22264A"/>')
    if shutter and not lit:
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{shutter}"/>'
                   f'<line x1="{x + w / 2:.1f}" y1="{y:.1f}" x2="{x + w / 2:.1f}" y2="{y + h:.1f}" stroke="{mix(shutter, "#000000", 0.4)}" stroke-width="1"/>'
                   f'<g stroke="{mix(shutter, "#000000", 0.35)}" stroke-width="0.8">' + "".join(
                       f'<line x1="{x:.1f}" y1="{y + j * 2.6:.1f}" x2="{x + w:.1f}" y2="{y + j * 2.6:.1f}"/>' for j in range(1, int(h / 2.6))) + "</g>")
    if shutter and lit:
        out.append(f'<rect x="{x - w * 0.5:.1f}" y="{y:.1f}" width="{w * 0.48:.1f}" height="{h:.1f}" fill="{shutter}"/>'
                   f'<rect x="{x + w + 0.2:.1f}" y="{y:.1f}" width="{w * 0.48:.1f}" height="{h:.1f}" fill="{shutter}"/>')
    if sill:
        out.append(f'<rect x="{x - 4:.1f}" y="{y + h + 1.6:.1f}" width="{w + 8:.1f}" height="2.6" fill="{frame}"/>')
    return "".join(out)


def iron_rail(x0, x1, y, h, color="#1E1E2A", k=1.0):
    bars = "".join(f'<line x1="{x:.1f}" y1="{y - h:.1f}" x2="{x:.1f}" y2="{y:.1f}"/>' for x in [x0 + (x1 - x0) * i / max(1, int((x1 - x0) / (3.4 * k))) for i in range(int((x1 - x0) / (3.4 * k)) + 1)])
    return (f'<g stroke="{color}" stroke-width="{1.1 * k:.1f}">{bars}</g>'
            f'<rect x="{x0 - 1:.1f}" y="{y - h - 1.4:.1f}" width="{x1 - x0 + 2:.1f}" height="2.4" fill="{color}"/>'
            f'<rect x="{x0 - 2:.1f}" y="{y:.1f}" width="{x1 - x0 + 4:.1f}" height="3" fill="{color}"/>')


def tango_couple(x, base, h, rim="#FFD08A"):
    """Tango couple in close embrace, joined hands raised to the left, her back leg stretched out in a long line.
    Man (left) in a dark suit and fedora, woman (right) in a red dress with a slit, a red flower in her hair.
    Unit height 100 (his crown)."""
    s = h / 100
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({s:.3f})">']
    g.append('<ellipse cx="4" cy="1" rx="44" ry="4" fill="#0E0E22" opacity="0.45"/>')
    suit, suit_l, skin = "#1E1E30", "#3A3A58", "#C8906A"
    red, red_d, red_l = "#D8203A", "#9A1028", "#FF6070"
    # her extended back leg (behind him? no - to the right, behind her)
    g.append(f'<path d="M 14 -40 Q 30 -26 44 -10 L 52 -3 L 50 0 L 41 -6 Q 28 -20 10 -32 Z" fill="{skin}"/>'
             '<path d="M 48 -4 L 54 -2 L 53 1 L 47 -1 Z" fill="#1E1416"/><path d="M 51 -0.4 L 51.6 3" stroke="#1E1416" stroke-width="1"/>')
    # his legs: front leg stepping toward her, back leg stretched
    g.append(f'<path d="M -12 -50 Q -18 -26 -26 -2 L -19 -2 Q -10 -24 -4 -46 Z" fill="{suit}"/>'
             f'<path d="M -4 -50 Q 2 -26 6 -2 L 12 -2 Q 8 -28 4 -50 Z" fill="{suit}"/>'
             '<path d="M -28 -2.6 L -17 -2.6 L -17 0.6 L -29 0.6 Z M 4 -2.6 L 15 -2.6 L 15 0.6 L 4 0.6 Z" fill="#0A0A12"/>'
             '<path d="M -28 -2.4 L -21 -2.4" stroke="#C8C8D8" stroke-width="0.8"/>')
    # her standing leg and the slit skirt
    g.append(f'<path d="M 14 -36 L 15 -2 L 19 -2 L 20 -36 Z" fill="{skin}"/><path d="M 13 -2.6 L 21 -2.6 L 21 0.6 L 13 0.6 Z" fill="#1E1416"/>')
    g.append(f'<path d="M 6 -60 Q 2 -46 4 -30 Q 8 -22 20 -20 Q 26 -30 22 -42 Q 28 -36 30 -30 Q 26 -46 20 -62 Z" fill="{red}"/>'
             f'<path d="M 20 -62 Q 26 -46 30 -30 Q 26 -32 22 -42 Q 22 -52 18 -62 Z" fill="{red_d}"/>'
             f'<path d="M 4 -30 Q 8 -22 20 -20" stroke="{red_l}" stroke-width="1" fill="none" opacity="0.7"/>')
    # her torso, leaning into him, arm over his shoulder
    g.append(f'<path d="M 3 -82 Q -2 -72 4 -60 L 20 -62 Q 22 -74 14 -84 Z" fill="{red}"/>'
             f'<path d="M 14 -84 Q 22 -74 20 -62 L 15 -62 Q 18 -72 11 -82 Z" fill="{red_d}"/>'
             f'<path d="M 8 -79 L -12 -80 Q -24 -84 -32 -93" stroke="{skin}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    # his torso and jacket
    g.append(f'<path d="M -16 -84 Q -20 -70 -14 -48 L 4 -48 Q 8 -66 4 -84 Q -6 -88 -16 -84 Z" fill="{suit}"/>'
             f'<path d="M -6 -84 L -4 -70 L -2 -84 Z" fill="#F2F0EA"/><path d="M -5 -82 L -3 -78 L -4 -74" stroke="#D8203A" stroke-width="1.4" fill="none"/>')
    # his right arm round her back
    g.append(f'<path d="M 2 -80 Q 12 -76 16 -68" stroke="{suit}" stroke-width="5" fill="none" stroke-linecap="round"/>'
             f'<circle cx="16.6" cy="-67" r="2.4" fill="{skin}"/>')
    # joined hands raised out to the left
    g.append(f'<path d="M -14 -80 Q -26 -82 -34 -92" stroke="{suit}" stroke-width="5" fill="none" stroke-linecap="round"/>'
             f'<circle cx="-34.6" cy="-94" r="3" fill="{skin}"/><path d="M -36 -92 Q -33 -97 -30 -95" stroke="{skin}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    # heads in profile, cheek to cheek: his fedora, her bun with a red carnation
    g.append(f'<path d="{smooth([(-12, -93), (-10.6, -98), (-5, -99.6), (-0.6, -97), (0.6, -93.4), (2.4, -91.2), (0.8, -90.2), (1.2, -87.4), (-1, -85), (-6, -84), (-11, -87)])}" fill="{skin}"/>'
             '<path d="M -12.6 -96 Q -13 -90 -10 -87 L -9 -92 Z" fill="#1A1010"/>'
             f'<ellipse cx="-7.6" cy="-91" rx="1.5" ry="2.3" fill="#A86E4E"/>'
             '<path d="M -2.6 -93.6 l 2 0.2" stroke="#2A1A14" stroke-width="0.9"/><path d="M -0.4 -88.2 l 1.2 0" stroke="#7A3A2E" stroke-width="0.8"/>'
             f'<ellipse cx="-6" cy="-97.6" rx="11.6" ry="2.2" fill="{suit}" transform="rotate(-6 -6 -97.6)"/><path d="M -13.4 -98 Q -13 -108 -5.6 -108.4 Q 1 -108 0.6 -99 Z" fill="{suit}"/>'
             f'<path d="M -13.2 -101.4 Q -6 -102.6 0.8 -101.6 L 0.7 -99.6 Q -6 -100.6 -13.2 -99.4 Z" fill="{red}"/>')
    g.append(f'<path d="{smooth([(14, -91), (12, -95.6), (7, -96.6), (3.6, -94.4), (2.8, -91.4), (1.2, -89.4), (2.6, -88.6), (2.4, -86), (4, -83.6), (8, -82.4), (12, -84.4), (14.4, -88)])}" fill="{skin}"/>'
             f'<path d="M 3.6 -94.4 Q 7 -98.6 12 -96.6 Q 16 -94 14.4 -88 Q 13 -84 11 -84.6 Q 12 -90 9 -93 Q 6 -94.4 3.6 -94.4 Z" fill="#1A0E0E"/>'
             '<path d="M 3.8 -90.4 q 1.2 0.8 2.4 0" stroke="#1A0E0E" stroke-width="0.8" fill="none"/><path d="M 2.4 -86.2 l 1.4 0" stroke="#B8182A" stroke-width="1.2"/>'
             f'<circle cx="15.4" cy="-93" r="3.8" fill="#1A0E0E"/><circle cx="14" cy="-97.4" r="2.6" fill="{red}"/><circle cx="13.4" cy="-98" r="1.1" fill="{red_l}"/>'
             '<circle cx="11.6" cy="-87" r="0.9" fill="#F2C230"/>')
    # rim light from the lamp on the left
    g.append(f'<path d="M -16 -84 Q -20 -70 -14 -48 M -12 -48 Q -18 -26 -26 -3 M -12 -99 Q -13 -106 -7 -107.6 M -12.4 -91 Q -12 -86 -9 -85" stroke="{rim}" stroke-width="1.4" fill="none" opacity="0.85"/>'
             f'<path d="M 2.6 -88 Q 2 -84 4 -82 M 3 -82 Q -2 -72 4 -60" stroke="{rim}" stroke-width="1.2" fill="none" opacity="0.7"/>')
    g.append("</g>")
    return "".join(g)


def bandoneon_player(x, base, h, rim="#FFD08A"):
    """An old musician on a wooden chair playing the bandoneón, flat cap, bellows open across his knees."""
    s = h / 100
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({s:.3f})">',
         '<ellipse cx="0" cy="1" rx="26" ry="3" fill="#0E0E22" opacity="0.4"/>',
         # chair
         '<path d="M -16 -44 L -16 0 M 14 -44 L 14 0 M 18 -44 L 18 -96" stroke="#6A3E24" stroke-width="3" stroke-linecap="round"/>'
         '<rect x="-18" y="-46" width="38" height="4" fill="#8A5230"/><path d="M 16 -90 L 20 -90 M 16 -74 L 20 -74" stroke="#6A3E24" stroke-width="2.4"/>',
         # legs
         '<path d="M -13 -50 L -1 -50 L -2.4 -2 L -11 -2 Z M 1 -50 L 13 -50 L 12 -2 L 3.4 -2 Z" fill="#3A3448"/>'
         '<path d="M -13 -50 L 13 -50 L 12 -44 L -12 -44 Z" fill="#4A4458"/>'
         '<path d="M -13 -2.6 L -1 -2.6 L -1 0.8 L -14 0.8 Z M 2 -2.6 L 14 -2.6 L 15 0.8 L 2 0.8 Z" fill="#141018"/>',
         # torso, waistcoat
         '<path d="M -8 -84 Q -14 -70 -10 -44 L 12 -44 Q 14 -66 10 -84 Q 0 -88 -8 -84 Z" fill="#F0ECE0"/>'
         '<path d="M -6 -80 L 8 -80 L 10 -46 L -8 -46 Z" fill="#4A3A2E"/><path d="M 1 -80 L 1 -46" stroke="#E8C060" stroke-width="0.8" stroke-dasharray="1 4"/>',
         # bandoneón: two square ends and the pleated bellows between them
         '<rect x="-30" y="-64" width="10" height="16" rx="1.4" fill="#141018"/><rect x="18" y="-64" width="10" height="16" rx="1.4" fill="#141018"/>'
         '<g fill="#E8E2D2">' + "".join(f'<circle cx="{-27 + (i % 2) * 4}" cy="{-61 + (i // 2) * 3.4}" r="0.8"/>' for i in range(8)) + "</g>"
         '<path d="M -20 -63 L 18 -63 L 18 -49 L -20 -49 Z" fill="#1E1A26"/>'
         '<g stroke="#C8303A" stroke-width="1">' + "".join(f'<line x1="{-19 + i * 3.6:.1f}" y1="-63" x2="{-17.4 + i * 3.6:.1f}" y2="-49"/>' for i in range(11)) + "</g>"
         '<g stroke="#E8E2D2" stroke-width="0.6" opacity="0.7">' + "".join(f'<line x1="{-17.6 + i * 3.6:.1f}" y1="-63" x2="{-16 + i * 3.6:.1f}" y2="-49"/>' for i in range(10)) + "</g>",
         # arms to the ends
         '<path d="M -8 -80 Q -22 -74 -24 -62" stroke="#F0ECE0" stroke-width="5" fill="none" stroke-linecap="round"/>'
         '<path d="M 10 -80 Q 22 -74 22 -62" stroke="#F0ECE0" stroke-width="5" fill="none" stroke-linecap="round"/>'
         '<circle cx="-24" cy="-60" r="2.6" fill="#C8906A"/><circle cx="22" cy="-60" r="2.6" fill="#C8906A"/>',
         # head bowed over the music, flat cap, white moustache
         '<ellipse cx="1" cy="-91" rx="6.6" ry="7.4" fill="#C8906A"/>'
         '<path d="M -7 -94 Q -6 -102 2 -102 Q 10 -101 9 -94 L 12 -93 Q 2 -91 -7 -94 Z" fill="#4A4A5E"/>'
         '<path d="M -2 -87 Q 1 -85 4 -87" stroke="#E8E4DA" stroke-width="2" fill="none" stroke-linecap="round"/>'
         '<path d="M -3 -90 q 1.4 0.8 2.6 0 M 2.6 -90 q 1.4 0.8 2.6 0" stroke="#3A2418" stroke-width="0.8" fill="none"/>',
         f'<path d="M -8 -84 Q -14 -70 -10 -46 M -7 -95 Q -7 -100 -2 -102" stroke="{rim}" stroke-width="1.4" fill="none" opacity="0.85"/>',
         "</g>"]
    return "".join(g)


def buenos_aires():
    u = "ba"
    base = 344
    out = [defs(
        lg(f"{u}-sky", [(0, "#1A1E44"), (0.4, "#3A3A78"), (0.72, "#8A5A90"), (0.9, "#E08A7A"), (1, "#F6B488")], 0, 40, 0, 260, units="userSpaceOnUse"),
        lg(f"{u}-dusk", [(0, "#22265A", 0.3), (0.6, "#22265A", 0.08), (1, "#22265A", 0)], 0, 140, 0, base, units="userSpaceOnUse"),
        lg(f"{u}-cob", [(0, "#4A4258"), (1, "#2A2438")], 0, base, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="{base}" fill="url(#{u}-sky)"/>')
    out.append(dots(40, 91, (0, 40, 600, 140), "#FFFFFF", r=(0.5, 1.2), opacity=(0.4, 0.9)))
    out.append(f'<path d="M 132 86 a 12 12 0 1 0 12 15 a 9.4 9.4 0 1 1 -12 -15 Z" fill="#FFF2D0"/>')
    out.append(glow(138, 94, 40, "#FFF2D0", f"{u}-moon", 0.35))
    out.append(streak_cloud(470, 120, 90, "#B07A9A", 0.5, 3) + streak_cloud(90, 176, 80, "#C88A9A", 0.45, 3))
    # the old transporter bridge over the Riachuelo, silhouetted against the last light
    bx0, bx1, top = 400, 610, 112
    out.append(f'<g fill="#2A2850">'
               f'<rect x="{bx0}" y="{top}" width="{bx1 - bx0}" height="7"/>'
               f'<path d="M {bx0 + 14} {top} L {bx0 + 6} 240 L {bx0 + 12} 240 L {bx0 + 20} {top + 6} L {bx0 + 28} 240 L {bx0 + 34} 240 L {bx0 + 26} {top} Z"/>'
               f'<path d="M {bx1 - 34} {top} L {bx1 - 42} 240 L {bx1 - 36} 240 L {bx1 - 28} {top + 6} L {bx1 - 20} 240 L {bx1 - 14} 240 L {bx1 - 22} {top} Z"/>'
               f'<rect x="{bx0 + 6}" y="{top - 20}" width="22" height="20"/><rect x="{bx1 - 42}" y="{top - 20}" width="22" height="20"/></g>')
    out.append(f'<g stroke="#2A2850" stroke-width="1.2">' + "".join(f'<line x1="{bx0 + 20 + i * 14}" y1="{top}" x2="{bx0 + 27 + i * 14}" y2="{top + 7}"/><line x1="{bx0 + 27 + i * 14}" y1="{top}" x2="{bx0 + 20 + i * 14}" y2="{top + 7}"/>' for i in range(12)) + "</g>")
    out.append(f'<path d="M 500 {top + 7} L 500 150 M 510 {top + 7} L 510 150" stroke="#2A2850" stroke-width="1"/><rect x="490" y="150" width="30" height="8" fill="#2A2850"/>'
               f'<rect x="494" y="152" width="4" height="3" fill="#FFC870"/><rect x="502" y="152" width="4" height="3" fill="#FFC870"/>'
               f'<circle cx="{bx0 + 17}" cy="{top - 22}" r="1.6" fill="#FF6A5A"/><circle cx="{bx1 - 31}" cy="{top - 22}" r="1.6" fill="#FF6A5A"/>')
    # the houses of Caminito: patchwork corrugated iron in every colour
    H = []
    # house 1 (left): blue ground floor, yellow upper floor, red roof
    H.append(chapa(-10, 272, 128, base, "#2E6AC8", f"{u}h1"))
    H.append(chapa(-10, 196, 128, 272, "#F6C430", f"{u}h2"))
    H.append(f'<path d="M -16 196 L 134 196 L 128 180 L -10 180 Z" fill="#C8382E"/><rect x="-16" y="194" width="150" height="4" fill="#8A2420"/>')
    H.append(window(16, 212, 20, 40, "#2E9A5A", shutter="#2E9A5A") + window(74, 212, 20, 40, "#2E9A5A", lit=True, shutter="#2E9A5A"))
    H.append(f'<rect x="8" y="254" width="96" height="3" fill="#1E1E2A"/>' + iron_rail(10, 102, 254, 14))
    H.append(f'<rect x="20" y="288" width="22" height="56" fill="#D8302E"/><rect x="23" y="291" width="16" height="22" fill="#FFC870"/><rect x="23" y="317" width="16" height="24" fill="#A82020"/>'
             f'<rect x="18" y="285" width="26" height="4" fill="#F6C430"/>' + window(70, 290, 22, 34, "#F6C430", shutter="#D8302E"))
    # house 2 (centre): a conventillo - green below, red above, an attic room, the outside stair and gallery
    H.append(chapa(128, 266, 300, base, "#2E9A5A", f"{u}h3"))
    H.append(chapa(128, 190, 300, 266, "#D8402E", f"{u}h4"))
    H.append(chapa(208, 140, 300, 190, "#7AC8E8", f"{u}h5"))
    H.append(f'<path d="M 202 140 L 306 140 L 300 126 L 208 126 Z" fill="#E8A030"/><rect x="202" y="138" width="104" height="3" fill="#A86A1E"/>')
    H.append(f'<path d="M 122 190 L 210 190 L 210 186 L 128 182 Z" fill="#E8A030"/>')
    H.append(window(240, 152, 18, 26, "#F6C430", lit=True))
    H.append(window(146, 206, 18, 36, "#F6F0E0", shutter="#2E6AC8") + window(250, 204, 18, 36, "#F6F0E0", lit=True))
    # the gallery along the upper floor and the stair rising to it
    H.append(f'<rect x="132" y="264" width="166" height="4" fill="#3A2A2A"/>' + iron_rail(196, 296, 264, 15, "#2A6ACA"))
    H.append(f'<rect x="214" y="216" width="20" height="48" fill="#3A2A3A"/><rect x="216" y="218" width="16" height="44" fill="#FFB860" opacity="0.85"/>')
    H.append(f'<path d="M 134 {base} L 196 264 L 204 264 L 142 {base} Z" fill="#6A4A3A"/>')
    H.append("".join(f'<rect x="{134 + i * 6.2:.1f}" y="{base - (i + 1) * 8:.1f}" width="10" height="2" fill="#8A6A52"/>' for i in range(10)))
    H.append(f'<path d="M 134 {base - 18} L 196 {264 - 18}" stroke="#2A6ACA" stroke-width="2"/>' + "".join(f'<line x1="{140 + i * 6.2:.1f}" y1="{base - 18 - (i + 0.6) * 8 + 4:.1f}" x2="{140 + i * 6.2:.1f}" y2="{base - (i + 0.6) * 8 - 4:.1f}" stroke="#2A6ACA" stroke-width="1.1"/>' for i in range(9)))
    H.append(f'<rect x="250" y="294" width="22" height="50" fill="#F6C430"/><rect x="253" y="297" width="16" height="44" fill="#3A2A3A"/>')
    # laundry on a line across the gallery
    H.append('<path d="M 196 236 Q 222 246 300 238" stroke="#E8E2D2" stroke-width="0.8" fill="none"/>'
             '<rect x="232" y="240" width="9" height="12" fill="#F6F0E0"/><rect x="262" y="241" width="8" height="10" fill="#F2C230"/><path d="M 276 240 l 10 0 l -1 12 l -3 0 l -1 -6 l -1 6 l -3 0 Z" fill="#4A7ACA"/>')
    # house 3: orange below, sky-blue above with a balcony and a painted figure leaning out
    H.append(chapa(300, 270, 434, base, "#F2873A", f"{u}h6"))
    H.append(chapa(300, 186, 434, 270, "#4AB0E0", f"{u}h7"))
    H.append(f'<path d="M 294 186 L 440 186 L 434 168 L 300 168 Z" fill="#2E9A5A"/><rect x="294" y="184" width="146" height="4" fill="#1E6A3E"/>')
    H.append(window(318, 200, 20, 40, "#F6F0E0", lit=True, shutter="#D8402E") + window(390, 200, 20, 40, "#F6F0E0", shutter="#D8402E"))
    H.append(f'<rect x="306" y="252" width="122" height="4" fill="#3A2A2A"/>')
    H.append(person(358, 252, 30, "#E8303A", "#2A2A3A", skin="#E8B890", hair="#3A2A1A", arms="up", rim="#FFD08A"))
    H.append(iron_rail(308, 426, 252, 14, "#F6F0E0"))
    H.append(f'<rect x="322" y="288" width="22" height="56" fill="#2E6AC8"/><rect x="325" y="291" width="16" height="50" fill="#1E4A9A"/>' + window(376, 290, 26, 32, "#2E6AC8", lit=True))
    # house 4 (right): magenta below, lime above
    H.append(chapa(434, 262, 610, base, "#C8306A", f"{u}h8"))
    H.append(chapa(434, 192, 610, 262, "#B8D040", f"{u}h9"))
    H.append(f'<path d="M 428 192 L 616 192 L 610 176 L 434 176 Z" fill="#2E6AC8"/><rect x="428" y="190" width="188" height="4" fill="#1E4A9A"/>')
    H.append(window(456, 206, 18, 38, "#F6F0E0", shutter="#2E6AC8") + window(506, 206, 18, 38, "#F6F0E0", lit=True) + window(556, 206, 18, 38, "#F6F0E0", shutter="#2E6AC8"))
    H.append(f'<rect x="446" y="244" width="140" height="3" fill="#1E1E2A"/>' + iron_rail(448, 584, 244, 12))
    H.append(window(470, 284, 24, 34, "#F6C430", lit=True) + f'<rect x="530" y="282" width="24" height="62" fill="#F6C430"/><rect x="533" y="285" width="18" height="56" fill="#2A2A3A"/>')
    # potted geraniums on the balconies
    for px, py in ((24, 252), (88, 252), (446, 242), (576, 242), (312, 250)):
        H.append(f'<rect x="{px - 4}" y="{py - 6}" width="8" height="6" fill="#B8603A"/>' + bougainvillea(6, px, (px - 5, py - 12, px + 5, py - 6), cols=("#E8303A", "#FF5A5A"), r=(1.2, 2)))
    out.append("".join(H))
    # blue-hour cool over the upper walls
    out.append(f'<rect x="0" y="120" width="600" height="{base - 120}" fill="url(#{u}-dusk)"/>')
    # cobbles of the little plaza, wet-looking, catching the lamp
    out.append(f'<rect x="0" y="{base}" width="600" height="{444 - base}" fill="url(#{u}-cob)"/>')
    out.append(f'<rect x="0" y="{base}" width="600" height="5" fill="#6A6070"/>')
    rnd = random.Random(92)
    cb = []
    y = base + 7
    row = 0
    while y < 446:
        sz = 5 + (y - base) * 0.09
        x = -10 + (row % 2) * sz * 0.6
        while x < 610:
            cb.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{sz * rnd.uniform(1.0, 1.3):.1f}" height="{sz * 0.48:.1f}" rx="{sz * 0.2:.1f}" fill="{rnd.choice(["#5A5268", "#4E4860", "#625A70", "#463E56"])}"/>')
            x += sz * 1.35
        y += sz * 0.6
        row += 1
    out.append("".join(cb))
    # the street lamp and its warm pool of light
    out.append(glow(96, 252, 150, "#FFC870", f"{u}-lamp", 0.55))
    out.append(f'<defs>{rg(f"{u}-pool", [(0, "#FFC870", 0.5), (1, "#FFC870", 0)])}</defs><ellipse cx="190" cy="392" rx="210" ry="42" fill="url(#{u}-pool)"/>')
    out.append('<path d="M 92 412 L 94 266 L 98 266 L 100 412 Z" fill="#14121E"/><rect x="88" y="404" width="16" height="8" fill="#14121E"/>'
               '<path d="M 86 266 L 106 266 L 102 244 L 90 244 Z" fill="#FFE6A8"/><path d="M 84 246 L 96 236 L 108 246 Z" fill="#14121E"/><rect x="86" y="264" width="20" height="3" fill="#14121E"/>'
               '<path d="M 94 300 Q 80 296 76 286 M 98 300 Q 112 296 116 286" stroke="#14121E" stroke-width="2" fill="none"/>')
    # festoon lights strung across the plaza
    for (x0, y0), (x1, y1), sag, seed in (((-10, 206), (330, 200), 38, 1), ((300, 196), (610, 210), 30, 2)):
        pts = []
        for i in range(41):
            t = i / 40
            pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t + sag * 4 * t * (1 - t)))
        out.append(f'<polyline points="{P(pts)}" stroke="#14121E" stroke-width="1" fill="none"/>')
        for i in range(2, 40, 3):
            bx, by = pts[i]
            out.append(f'<circle cx="{bx:.1f}" cy="{by + 3:.1f}" r="6" fill="#FFD890" opacity="0.25"/><circle cx="{bx:.1f}" cy="{by + 3:.1f}" r="2" fill="#FFF2C8"/>')
    # the dancers in the lamplight, the bandoneón player on his chair
    out.append(tango_couple(258, 418, 132))
    out.append(bandoneon_player(470, 404, 96))
    # a dog listening at the musician's feet
    out.append('<g transform="translate(414 404)"><ellipse cx="0" cy="0" rx="14" ry="2" fill="#0E0E22" opacity="0.4"/>'
               '<path d="M -12 -1 Q -14 -10 -4 -11 L 8 -11 Q 12 -12 12 -6 L 12 -1 Z" fill="#C89A6A"/><circle cx="-10" cy="-13" r="5" fill="#C89A6A"/>'
               '<path d="M -14 -15 Q -17 -10 -14 -8 Z M -7 -17 Q -4 -13 -6 -10 Z" fill="#8A5E3E"/><circle cx="-14.4" cy="-12" r="1.2" fill="#1E1416"/>'
               '<path d="M 12 -7 Q 17 -9 16 -14" stroke="#C89A6A" stroke-width="2.4" fill="none" stroke-linecap="round"/><path d="M -12 -10 Q -10 -6 -6 -11" stroke="#FFD08A" stroke-width="1" fill="none"/></g>')
    # reflections of the lamp in the cobbles
    out.append(water_lines(30, 93, (60, 380, 160, 444), ["#FFD890", "#FFC870"], w=(4, 12), h=(1, 1.8), opacity=(0.3, 0.7)))
    return "\n".join(out)


BUILD = {
    "buenos-aires": (buenos_aires, "BUENOS AIRES", "ARGENTINA · SOUTH AMERICA", "#1E1E40", "#4AB0E0", "#FFF4E2", "#F6C430"),
    "machu-picchu": (machu_picchu, "MACHU PICCHU", "PERU · SOUTH AMERICA", "#6A2E2A", "#E8B04A", "#FFF4E4", "#F2C27A"),
    "cartagena": (cartagena, "CARTAGENA", "COLOMBIA · CARIBBEAN", "#A81E5A", "#F6C51E", "#FFF2F6", "#FFD27A"),
    "chichen-itza": (chichen_itza, "CHICHÉN ITZÁ", "MEXICO · YUCATÁN", "#2E1E46", "#F6A060", "#FFF2E4", "#F6B894"),
    "havana": (havana, "HAVANA", "CUBA · CARIBBEAN", "#1E5A78", "#F4A6B4", "#FFF4E8", "#9EE0E0"),
    "rio-de-janeiro": (rio, "RIO DE JANEIRO", "BRASIL · CIDADE MARAVILHOSA", "#14503A", "#F2C443", "#FFF6E2", "#F6D27A"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("world", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
