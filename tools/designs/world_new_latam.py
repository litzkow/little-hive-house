"""World Places, Latin America: six painted travel posters (Rio, Machu Picchu, Havana, Chichén Itzá, Cartagena,
Buenos Aires) in the same painterly travel-poster idiom as world_painted.py: a real viewpoint, a time of day,
light direction, atmospheric depth and small storytelling details."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from places_painted import Cam
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


def marmoset(x, y, s, flip=False, body="#6E6258", dark="#2E2622", tuft="#F2ECE0", rim="#FFD89A"):
    """Common marmoset (sagui) perched on a branch: striped ringed tail, white ear tufts."""
    sx = -s if flip else s
    g = [f'<g transform="translate({x:.1f} {y:.1f}) scale({sx:.2f} {s:.2f})">']
    # ringed tail hanging down
    tail = [(6, -2), (10, 6), (11, 16), (9, 26), (6, 34)]
    for i, ((ax, ay), (bx, by)) in enumerate(zip(tail, tail[1:])):
        g.append(f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="{dark if i % 2 == 0 else "#8E8276"}" stroke-width="4" stroke-linecap="round"/>')
    g.append(f'<path d="M -8 0 Q -10 -10 -4 -14 Q 4 -16 8 -8 Q 10 -2 6 2 Z" fill="{body}"/>')
    g.append('<g stroke="#2E2622" stroke-width="1" opacity="0.6">' + "".join(f'<line x1="{-6 + i * 3}" y1="-12" x2="{-5 + i * 3}" y2="-4"/>' for i in range(5)) + "</g>")
    g.append(f'<path d="M -6 1 L -7 4 M 4 1 L 5 4" stroke="{dark}" stroke-width="2.2" stroke-linecap="round"/>')
    g.append(f'<circle cx="-9" cy="-16" r="5.2" fill="{dark}"/><ellipse cx="-11.5" cy="-15" rx="2.2" ry="2.6" fill="#C8B49C"/>')
    g.append(f'<path d="M -7 -20 Q -2 -24 -1 -18 Q -4 -17 -6 -16 Z" fill="{tuft}"/><path d="M -12 -21 Q -16 -26 -17 -19 Q -14 -18 -12 -18 Z" fill="{tuft}"/>')
    g.append('<circle cx="-11" cy="-17" r="0.9" fill="#FFFFFF"/><circle cx="-8.6" cy="-17" r="0.9" fill="#FFFFFF"/>')
    g.append(f'<path d="M -4 -14 Q 4 -16 8 -8" fill="none" stroke="{rim}" stroke-width="1.4" opacity="0.9"/>')
    g.append("</g>")
    return "".join(g)


def rio():
    u = "rj"
    hz = 246
    out = [defs(
        lg(f"{u}-sky", [(0, "#3F78B4"), (0.28, "#78A6CE"), (0.55, "#BCCFD8"), (0.78, "#F2D6AE"), (1, "#FBE2B6")], 0, 0, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#9FB8C8"), (0.12, "#5E8EAE"), (0.5, "#2F6A90"), (1, "#1F4F72")], 0, hz, 0, 360, units="userSpaceOnUse"),
        lg(f"{u}-cove", [(0, "#4C86A8"), (1, "#2A5E7E")], 0, 300, 0, 360, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#F8E2C0", 0), (1, "#F8E2C0", 0.75)], 0, 190, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-city", [(0, "#E8D2BC"), (1, "#B89E9A")], 0, 330, 0, 420, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="{hz + 2}" fill="url(#{u}-sky)"/>')
    out.append(glow(640, 170, 360, "#FFD592", f"{u}-sun", 0.8))
    # golden-hour cumulus over the ocean, lit from the right (west)
    out.append(cumulus(f"{u}-c1", 150, 128, 170, 46, 3, "#FFF2DA", "#F4DCC6", "#B6A6C0", hi="#FFF8E8", hi_op=0.7, light=1))
    out.append(cumulus(f"{u}-c2", 548, 92, 120, 34, 5, "#FFF0D2", "#F6D8BC", "#C0A8BC", hi="#FFF8E8", hi_op=0.7, light=1))
    out.append(cumulus(f"{u}-c3", 250, 186, 90, 18, 9, "#FFE8C8", "#F2D2BC", "#C4AEC0", hi="#FFF4E0", light=1))
    for x, y, w in ((60, 168, 70), (470, 196, 80), (330, 150, 50)):
        out.append(streak_cloud(x, y, w, "#FFE2C2", 0.6, 3))
    # open Atlantic at the bay mouth
    out.append(f'<rect x="0" y="{hz}" width="600" height="{444 - hz}" fill="url(#{u}-sea)"/>')
    # Niterói across the bay: layered hazy hills, the Santa Cruz fortress at the point
    poly, _ = ridge_poly([(-10, 196), (30, 186), (70, 200), (110, 192), (150, 210), (196, 222), (232, 240), (250, 247)], 11, base=hz + 2, amp=6, fill="#A4A6C2")
    out.append(poly)
    poly, nl = ridge_poly([(-10, 222), (40, 214), (90, 226), (140, 220), (180, 236), (214, 246)], 12, base=hz + 3, amp=4, fill="#8E92B4")
    out.append(poly)
    out.append(f'<rect x="0" y="180" width="300" height="{hz - 178}" fill="url(#{u}-haze)"/>')
    rnd = random.Random(14)
    out.append("".join(f'<rect x="{rnd.uniform(-5, 200):.1f}" y="{hz - rnd.uniform(1, 6):.1f}" width="{rnd.uniform(2, 5):.1f}" height="{rnd.uniform(2, 5):.1f}" fill="{rnd.choice(["#F4E6DC", "#E2D2D6", "#FFF2E2"])}"/>' for _ in range(50)))
    out.append('<g fill="#D8C8C8"><rect x="214" y="241" width="16" height="5"/><rect x="218" y="238" width="6" height="3"/></g>')
    # sun glitter on the bay
    rnd = random.Random(21)
    for _ in range(70):
        y = hz + 3 + rnd.random() ** 1.4 * 50
        x = rnd.uniform(0, 600)
        w = rnd.uniform(4, 14)
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="1.1" rx="0.5" fill="#FFE8B8" opacity="{rnd.uniform(0.35, 0.8):.2f}"/>')
    out.append(water_lines(60, 22, (0, hz + 6, 600, 300), ["#8EB4C8", "#24557A"], w=(8, 26), h=(0.8, 1.4), opacity=(0.3, 0.6)))
    # Morro da Babilônia / Leme on the right, forested
    bab = [(470, 300), (500, 270), (530, 246), (556, 236), (580, 238), (610, 246), (610, 302)]
    out.append(forest_hill(f"{u}-bb", bab, 31, "#2C4A3A", "#41654A", "#8EA86A", light=(1, -1), gold="#F2D088"))
    # Sugarloaf: the granite dome, sunlit on its west (right) flank
    sl = [(340, 262), (346, 236), (352, 206), (360, 176), (370, 150), (382, 130), (396, 116), (410, 108), (424, 106), (438, 110), (451, 120),
          (462, 136), (472, 160), (481, 190), (490, 224), (500, 258), (512, 292), (520, 306), (334, 306)]
    sl = [sl[0]] + rough(sl[1:-2], 41, amp=2.5, depth=2) + sl[-2:]
    rnd = random.Random(44)
    # Atlantic forest clinging to the lower slopes, a tongue up the western gully, a thin cap on the summit
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
           + f'<g fill="#2A4430">' + "".join(f'<circle cx="{x - 1:.1f}" cy="{y + 1.5:.1f}" r="{r:.1f}"/>' for x, y, r in cl) + "</g>"
           + f'<g fill="#4E6E46">' + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.78:.1f}"/>' for x, y, r in cl) + "</g>"
           + f'<g fill="#B0B874" opacity="0.8">' + "".join(f'<circle cx="{x + r * 0.35:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.4:.1f}"/>' for x, y, r in cl if x > 400 or rnd.random() < 0.4) + "</g>")
    out.append(granite_dome(f"{u}-sl", sl, 350, 505, "#FFCF9A", "#D8A48E", "#8A7896", ["#6A5E7E", "#A88A8E", "#FFE6BE", "#7E6A84"], 7, veg=veg))
    out.append(f'<polyline points="{P(sl[8:17])}" fill="none" stroke="#FFEAC4" stroke-width="2.6" stroke-linejoin="round" opacity="0.95"/>')
    # Morro da Urca, lower and forested, with the cable-car station on top
    urca = [(232, 304), (250, 280), (270, 252), (292, 236), (316, 230), (338, 234), (352, 246), (366, 266), (378, 304)]
    out.append(forest_hill(f"{u}-ur", urca, 33, "#2E4C3C", "#46694C", "#9AB070", light=(1, -1), gold="#F2D088"))
    out.append('<g><rect x="318" y="224" width="20" height="8" fill="#F2E8DC"/><rect x="331" y="224" width="7" height="8" fill="#FFF4E6"/><rect x="316" y="222" width="24" height="2.4" fill="#C8B8B0"/></g>')
    # cable-car wires and the little car in mid-air
    out.append('<path d="M 336 224 Q 380 182 414 110" fill="none" stroke="#2E2E3E" stroke-width="1.3"/><path d="M 338 226 Q 382 184 416 112" fill="none" stroke="#2E2E3E" stroke-width="0.9" opacity="0.7"/>')
    cx_, cy_ = 372, 182
    out.append(f'<line x1="{cx_}" y1="{cy_ - 6}" x2="{cx_}" y2="{cy_}" stroke="#2E2E3E" stroke-width="1.2"/><rect x="{cx_ - 5}" y="{cy_}" width="10" height="7" rx="1.6" fill="#E8F0F2"/><rect x="{cx_ - 4}" y="{cy_ + 1.5}" width="8" height="3" fill="#5A86A8"/><rect x="{cx_ + 1}" y="{cy_}" width="4" height="7" rx="1" fill="#FFFFFF" opacity="0.6"/>')
    # Urca neighbourhood strip at the water, low houses and a seawall
    rnd = random.Random(5)
    x = 226
    while x < 500:
        w = rnd.uniform(5, 11)
        h = rnd.uniform(4, 9)
        out.append(f'<rect x="{x:.1f}" y="{304 - h:.1f}" width="{w:.1f}" height="{h + 2:.1f}" fill="{rnd.choice(["#F4E2CC", "#EED0B8", "#F8EEE0", "#E8C8B0", "#DCC4C0"])}"/>'
                   f'<rect x="{x + w * 0.7:.1f}" y="{304 - h:.1f}" width="{w * 0.3:.1f}" height="{h + 2:.1f}" fill="#FFF4E2" opacity="0.7"/>')
        x += w + rnd.uniform(0, 2)
    out.append('<rect x="222" y="305" width="290" height="3" fill="#C8B4A4"/>')
    # Botafogo cove: calmer water with anchored yachts
    cove = [(-10, 322), (60, 312), (160, 307), (240, 308), (330, 309), (420, 309), (520, 310), (610, 318), (610, 372), (-10, 372)]
    out.append(Q(cove, f"url(#{u}-cove)"))
    # Morro da Viúva headland on the left closing the cove
    viu = [(-10, 330), (-10, 300), (16, 288), (44, 284), (72, 292), (96, 306), (110, 318)]
    out.append(forest_hill(f"{u}-vi", viu, 35, "#284436", "#3E5E46", "#86A066", light=(1, -1), gold="#F2D088"))
    rnd = random.Random(8)
    for _ in range(60):
        out.append(sailboat_moored(rnd.uniform(130, 520), rnd.uniform(316, 352), rnd.uniform(0.7, 1.1), rnd))
    out.append(water_lines(80, 23, (40, 312, 600, 362), ["#86B2C8", "#1E4E6E", "#FFE2B0"], w=(6, 22), h=(0.8, 1.4), opacity=(0.25, 0.6)))
    # the reflection of Sugarloaf's golden flank in the cove
    # Botafogo beach: sand crescent, the promenade and the avenue lined with trees
    beach = [(-10, 372), (60, 362), (160, 356), (280, 354), (400, 356), (520, 360), (610, 368), (610, 380), (-10, 384)]
    out.append(Q(beach, "#F2DCB4"))
    out.append(f'<polyline points="{P(beach[:7])}" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity="0.8"/>')
    out.append('<path d="M -10 380 Q 300 362 610 376 L 610 386 Q 300 370 -10 390 Z" fill="#E4E0D8"/>')
    out.append('<g fill="none" stroke="#2A2A30" stroke-width="1.1" opacity="0.6">' + "".join(
        f'<path d="M {x} {381 - 0.03 * (300 - abs(300 - x)):.1f} q 3 -2 6 0 t 6 0"/>' for x in range(-6, 606, 12)) + "</g>")
    rnd = random.Random(19)
    out.append("".join(f'<circle cx="{x:.1f}" cy="{388 - 0.035 * (300 - abs(300 - x)) + rnd.uniform(-2, 1):.1f}" r="{rnd.uniform(3, 5):.1f}" fill="{rnd.choice(["#3E6A40", "#4E7A48", "#2E5236"])}"/>' for x in range(-4, 606, 9)))
    out.append(dots(30, 20, (60, 356, 560, 370), "#2A2A3A", r=(0.8, 1.4), opacity=(0.6, 1)))
    out.append(dots(16, 21, (60, 356, 560, 370), "#E8543E", r=(1, 1.6), opacity=(0.7, 1)))
    # Botafogo apartment blocks below the overlook, lit gold on their west faces
    rnd = random.Random(27)
    walls = [("#E8DCD0", "#FFE6C2", "#C8B8B0"), ("#D8CCC8", "#F8DCB8", "#B8A8A8"), ("#F0E2D4", "#FFEACC", "#D0C0B4"), ("#C8B8B8", "#F2D0B0", "#A89898"),
             ("#E0C8B4", "#FFD8AC", "#C0A894")]
    for row, (yb, k) in enumerate(((398, 0.75), (410, 0.9))):
        x = -20 + rnd.uniform(-10, 0)
        while x < 620:
            w = rnd.uniform(16, 30) * k
            h = rnd.uniform(14, 30) * k
            wall, side, roof = rnd.choice(walls)
            out.append(apartment(x, yb + rnd.uniform(-3, 3), w, h, 6 * k, wall, side, roof, rnd))
            x += w + 6 * k + rnd.uniform(-2, 8)
    out.append(f'<rect x="0" y="372" width="600" height="40" fill="#C8A8B0" opacity="0.12"/>')
    # treetops of the hillside between the city and the overlook
    hs = [(-10, 444), (-10, 392), (60, 396), (140, 402), (240, 404), (340, 402), (440, 398), (540, 394), (610, 390), (610, 444)]
    out.append(forest_hill(f"{u}-hs", hs, 51, "#1E3A28", "#2E5038", "#6E9450", light=(1, -1), gold="#E8C870"))
    # the overlook: a whitewashed parapet and the wavy black-and-white pedra portuguesa
    out.append(f'<defs>{lg(f"{u}-pave", [(0, "#EFE6D8"), (1, "#FFF6E8")], 0, 412, 0, 444, units="userSpaceOnUse")}</defs>')
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
    # a couple leaning on the wall, watching the light go gold on the Sugarloaf
    for px, h_, c, hair in ((150, 46, "#E8543E", "#2A1A14"), (172, 50, "#2E5A7E", "#3A2418")):
        out.append(f'<g transform="translate({px} 416)">'
                   f'<path d="M -9 -{h_ * 0.5:.0f} L -7 0 L 7 0 L 9 -{h_ * 0.5:.0f} Z" fill="#2A2A3A"/>'
                   f'<path d="M -11 -{h_ * 0.5:.0f} Q -12 -{h_ * 0.85:.0f} 0 -{h_ * 0.88:.0f} Q 12 -{h_ * 0.85:.0f} 11 -{h_ * 0.5:.0f} Z" fill="{c}"/>'
                   f'<path d="M 9 -{h_ * 0.84:.0f} Q 12 -{h_ * 0.7:.0f} 11 -{h_ * 0.5:.0f}" fill="none" stroke="#FFD8A0" stroke-width="2"/>'
                   f'<circle cx="0" cy="-{h_ * 0.97:.0f}" r="{h_ * 0.13:.1f}" fill="{hair}"/>'
                   f'<path d="M {h_ * 0.09:.1f} -{h_ * 1.07:.0f} Q {h_ * 0.15:.1f} -{h_ * 0.98:.0f} {h_ * 0.1:.1f} -{h_ * 0.88:.0f}" fill="none" stroke="#FFD8A0" stroke-width="1.6"/></g>')
    out.append('<path d="M 156 382 Q 162 388 166 384" fill="none" stroke="#E8543E" stroke-width="3" stroke-linecap="round"/>')
    out.append('<path d="M 136 398 L 140 404 L 164 404 L 160 398 Z M 186 398 L 182 404 L 162 404 L 166 398 Z" fill="#2A2A3A" opacity="0.25"/>')
    out.append(coco_palm(58, 404, 250, 81, lean=0.12, L=110))
    # a marmoset on the parapet, tail hanging over the edge
    out.append(marmoset(270, 398, 1.25, flip=True))
    # a yellow ipê in full bloom arching in from the right, petals fallen on the pavement
    out.append(ipe_tree(574, 444, 190, 61, spread=(-80, 25)))
    out.append(dots(30, 72, (380, 418, 610, 444), "#F6C431", r=(1.2, 2.4), opacity=(0.8, 1)))
    out.append(dots(12, 73, (280, 400, 460, 410), "#F6C431", r=(1, 2), opacity=(0.8, 1)))
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


def llama(x, base, k, flip=False, wool="#F4ECDC", shade="#C8B8A0", patch="#8A5E3E", rim="#FFF4D8", tassel=("#E83A6A", "#F6B42E", "#3AA0C8")):
    """Llama standing in three-quarter profile facing left, ear tassels of coloured yarn."""
    sx = -k if flip else k
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({sx:.3f} {k:.3f})">',
         '<ellipse cx="2" cy="1" rx="34" ry="4" fill="#2A3A22" opacity="0.35"/>']
    # far legs
    g.append(f'<path d="M -16 -34 L -14 -2 L -10 -2 L -10 -32 Z M 22 -34 L 24 -2 L 28 -2 L 27 -32 Z" fill="{shade}"/>')
    # body
    g.append(f'<path d="M -26 -38 Q -28 -58 -12 -60 L 22 -60 Q 36 -58 34 -42 Q 33 -30 22 -28 L -16 -28 Q -26 -30 -26 -38 Z" fill="{wool}"/>')
    g.append(f'<path d="M -26 -38 Q -24 -30 -16 -28 L 22 -28 Q 33 -30 34 -42 Q 30 -34 18 -33 L -14 -33 Q -22 -34 -26 -38 Z" fill="{shade}"/>')
    g.append(f'<path d="M 4 -60 Q 18 -62 26 -56 Q 30 -48 22 -44 Q 10 -46 4 -52 Z" fill="{patch}" opacity="0.85"/>')
    # tail
    g.append(f'<path d="M 33 -48 Q 40 -46 38 -38 Q 35 -40 33 -44 Z" fill="{wool}"/>')
    # near legs
    g.append(f'<path d="M -20 -32 L -19 -1 L -14 -1 L -13 -30 Z M 16 -32 L 17 -1 L 22 -1 L 22 -30 Z" fill="{wool}"/>'
             '<path d="M -20 -2 L -13 -2 L -13 1 L -21 1 Z M 16 -2 L 23 -2 L 23 1 L 15 1 Z" fill="#3A2E28"/>')
    # neck and head
    g.append(f'<path d="M -26 -40 Q -30 -60 -28 -82 L -16 -84 Q -14 -62 -12 -52 Z" fill="{wool}"/>')
    g.append(f'<path d="M -16 -84 Q -14 -62 -12 -52 L -18 -50 Q -20 -66 -21 -84 Z" fill="{shade}" opacity="0.7"/>')
    g.append(f'<path d="M -30 -84 Q -32 -94 -24 -96 Q -16 -96 -15 -88 Q -15 -82 -20 -80 L -36 -78 Q -42 -79 -41 -83 Q -38 -86 -30 -84 Z" fill="{wool}"/>')
    g.append('<ellipse cx="-39" cy="-81" rx="3" ry="2.2" fill="#5A4A44"/><circle cx="-27" cy="-89" r="1.6" fill="#1E1A1A"/><circle cx="-26.5" cy="-89.5" r="0.5" fill="#FFFFFF"/>')
    # banana ears with tassels
    g.append(f'<path d="M -26 -95 Q -30 -104 -27 -110 Q -24 -104 -23 -96 Z M -19 -95 Q -18 -105 -14 -109 Q -14 -102 -16 -95 Z" fill="{wool}"/>')
    for i, (ex, ey) in enumerate(((-27, -104), (-15, -104))):
        g.append("".join(f'<path d="M {ex + j * 1.4 - 1.4:.1f} {ey} q {-1 + j:.1f} 5 {-1.6 + j * 0.8:.1f} 9" stroke="{tassel[j]}" stroke-width="1.8" fill="none" stroke-linecap="round"/>' for j in range(3)))
    # rim light from the right/back
    g.append(f'<path d="M -12 -60 L 22 -60 Q 36 -58 34 -42" fill="none" stroke="{rim}" stroke-width="1.8" stroke-linecap="round"/>'
             f'<path d="M -15 -88 Q -14 -62 -12 -54" fill="none" stroke="{rim}" stroke-width="1.5"/>')
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
    g.append(dots(int(area / 30), seed + 1, box, dots_col, r=(0.8, 2.2), opacity=(0.15, 0.4)))
    g.append(dots(int(area / 60), seed + 2, box, ribs[1], r=(0.8, 2), opacity=(0.2, 0.5)))
    out.append(f'<g clip-path="url(#{u}-c)">{"".join(g)}</g>')
    if rim:
        i0, i1 = rim_range
        out.append(f'<polyline points="{P(outline[i0:i1])}" fill="none" stroke="{rim}" stroke-width="2" stroke-linejoin="round" opacity="0.85"/>')
    return "".join(out)


def machu_picchu():
    u = "mp"
    out = [defs(
        lg(f"{u}-sky", [(0, "#6E9CC8"), (0.4, "#A8C6DC"), (0.75, "#E2E8E2"), (1, "#F4EAD6")], 0, 0, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#94AEC2"), (1, "#C4D2DA")], 0, 140, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#F2F0EA", 0), (1, "#F2F0EA", 0.8)], 0, 170, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-lawn", [(0, "#9CC266"), (1, "#7AA84C")], 0, 300, 0, 340, units="userSpaceOnUse"),
        lg(f"{u}-sad", [(0, "#78A250"), (1, "#5E8A42")], 0, 290, 0, 370, units="userSpaceOnUse"),
        lg(f"{u}-slope", [(0, "#7EAA50"), (1, "#4E7A3A")], 0, 300, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="330" fill="url(#{u}-sky)"/>')
    out.append(glow(610, 40, 320, "#FFF2D0", f"{u}-sun", 0.75))
    out.append(cumulus(f"{u}-c1", 150, 112, 170, 42, 12, "#FFFFFF", "#EEF2F4", "#B4C4D2", hi="#FFFFFF", hi_op=0.7, light=1))
    out.append(cumulus(f"{u}-c2", 540, 138, 100, 24, 14, "#FFFFFF", "#F2F2EE", "#BCC8D4", hi="#FFFFFF", light=1))
    # far Andean ranges, pale and blue, a haze settling over them
    poly, _ = ridge_poly([(-10, 200), (40, 172), (90, 190), (150, 156), (210, 186), (260, 176), (300, 206), (350, 198), (410, 168), (470, 182), (530, 152), (610, 176)], 51, base=330, amp=10, fill=f"url(#{u}-far)")
    out.append(poly)
    poly, _ = ridge_poly([(-10, 236), (60, 220), (130, 238), (200, 230), (280, 252), (330, 262)], 57, base=330, amp=6, fill="#A6BAC4")
    out.append(poly)
    out.append(f'<rect x="0" y="170" width="600" height="130" fill="url(#{u}-haze)"/>')
    # mid ridges framing the gorge, in blue-green aerial perspective
    left_r = [(-10, 222), (30, 214), (80, 226), (130, 240), (180, 256), (230, 276), (270, 296), (290, 330), (-10, 330)]
    out.append(jungle_peak(f"{u}-lr", left_r, 52, "#5A8076", "#78988C", "#A8C2A8", 0, 300, ribs=("#4E7268", "#9CB8A4"), rib_op=(0.12, 0.3), n_ribs=50))
    right_r = [(470, 330), (482, 270), (506, 226), (536, 200), (572, 188), (610, 192), (610, 330)]
    out.append(jungle_peak(f"{u}-rr", right_r, 53, "#5A8076", "#7E9E90", "#BCD2B4", 470, 610, ribs=("#4E7268", "#A8C4A8"), rib_op=(0.12, 0.3), n_ribs=40))
    out.append(mist(120, 262, 170, 18, "#FFFFFF", f"{u}-m0", 0.75))
    # Huayna Picchu: the steep peak behind the citadel, cliffs on its west face, sunlit from the right
    hp = [(286, 320), (306, 290), (324, 254), (340, 214), (354, 178), (366, 146), (377, 122), (387, 106), (396, 98), (404, 97), (412, 104),
          (420, 120), (429, 146), (440, 176), (453, 204), (470, 230), (490, 252), (514, 272), (540, 290), (566, 320)]
    hp = [hp[0]] + rough(hp[1:-1], 61, amp=3, depth=2) + [hp[-1]]
    rnd = random.Random(62)
    cl = "".join(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-4, 2):.1f} {rnd.uniform(12, 30):.1f} l {rnd.uniform(3, 7):.1f} {rnd.uniform(-4, 4):.1f} Z" fill="{rnd.choice(["#8E9890", "#AEB4A8", "#6E7A74"])}" opacity="0.7"/>'
                 for x, y in [(rnd.uniform(360, 420), rnd.uniform(110, 200)) for _ in range(26)])
    out.append(jungle_peak(f"{u}-hp", hp, 54, "#2A4A3C", "#4E7A5C", "#A6C482", 340, 470, ribs=("#1E3A30", "#B8D08E"), cliffs=cl, rim="#FFF2CC", rim_range=(9, 16)))
    out.append('<g stroke="#D8D4C2" stroke-width="1.4" opacity="0.9"><path d="M 394 110 L 408 110"/><path d="M 390 116 L 412 117"/><path d="M 397 104 L 405 104"/></g>')
    hc = [(262, 330), (274, 300), (288, 280), (302, 270), (318, 272), (332, 288), (346, 330)]
    out.append(jungle_peak(f"{u}-hc", hc, 55, "#2A4C3E", "#467058", "#90B47E", 262, 346, ribs=("#1E3A30", "#A8C88A")))
    # morning cloud drifting across the flank of the peak and along the gorge
    out.append(cumulus(f"{u}-c3", 486, 262, 130, 24, 16, "#FFFFFF", "#F2F4F2", "#C4D0D6", hi="#FFFFFF", light=1))
    out.append(mist(470, 268, 120, 14, "#FFFFFF", f"{u}-m1", 0.8))
    out.append(mist(230, 296, 130, 12, "#FFFFFF", f"{u}-m2", 0.75))
    # the saddle the citadel sits on
    sad = [(90, 380), (120, 300), (200, 294), (300, 296), (380, 294), (460, 298), (540, 304), (610, 310), (610, 380)]
    out.append(Q(sad, f"url(#{u}-sad)"))
    out.append(mist(330, 296, 260, 8, "#FFFFFF", f"{u}-m3", 0.6))
    rnd = random.Random(64)
    # far row of houses at the foot of Huayna Picchu (Sacred Rock sector)
    for x in range(300, 590, 13):
        out.append(inca_house(x + rnd.uniform(-2, 2), 306 + rnd.uniform(-2, 1) + (x - 300) * 0.02, rnd.uniform(8, 11), rnd.uniform(5, 7), 4, 0.7, rnd, gable=rnd.random() < 0.6))
    # the main plaza lawn
    out.append(Q([(232, 336), (262, 312), (440, 314), (468, 338)], f"url(#{u}-lawn)"))
    out.append('<g stroke="#B8D886" stroke-width="1.2" opacity="0.6">' + "".join(f'<line x1="{250 + i * 22}" y1="{334}" x2="{266 + i * 20}" y2="{314}"/>' for i in range(10)) + "</g>")
    # Intihuatana hill on the left: stepped platforms with the carved stone on top
    for i in range(6):
        w = 104 - i * 15
        y = 330 - i * 6
        out.append(f'<rect x="{186 - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="6" fill="#A4A094"/>'
                   f'<rect x="{186 - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="2" fill="#94BC5E"/>'
                   f'<rect x="{186 + w / 2 - 6:.1f}" y="{y + 2:.1f}" width="6" height="4" fill="#D8D4C6"/>')
    out.append('<rect x="182" y="289" width="8" height="5" fill="#C8C4B8"/><rect x="187" y="289" width="3" height="5" fill="#ECE8DC"/><rect x="180" y="293" width="12" height="2" fill="#8E8A80"/>')
    for x in (126, 146, 228):
        out.append(inca_house(x, 334 + rnd.uniform(-1, 1), rnd.uniform(13, 16), rnd.uniform(7, 9), 5, 0.9, rnd))
    # right sector: tight blocks of houses stepping down
    for row, (yb, k) in enumerate(((328, 0.85), (342, 1.0))):
        x = 448 + row * 6
        while x < 600:
            w = rnd.uniform(11, 16) * k
            out.append(inca_house(x, yb + rnd.uniform(-1.5, 1.5), w, rnd.uniform(7, 9) * k, 5 * k, k, rnd, gable=rnd.random() < 0.7))
            x += w + 5 * k + rnd.uniform(1, 4)
    # near row below the plaza, the largest, one with a reconstructed thatched roof
    x = 214
    while x < 450:
        w = rnd.uniform(15, 20)
        out.append(inca_house(x, 356 + rnd.uniform(-2, 2), w, rnd.uniform(9, 12), 6.5, 1.2, rnd, thatch=abs(x - 320) < 12))
        x += w + 8 + rnd.uniform(0, 6)
    # terraces wrapping the citadel below
    for i in range(6):
        y = 362 + i * 9
        pts = rough([(150 + i * 10, y), (330, y + 2), (450, y + 3), (610, y + 4)], 70 + i, amp=1.2, depth=2)
        out.append(Q(pts + [(610, y + 11), (150 + i * 10, y + 11)], "#86B054" if i % 2 else "#7EA84E"))
        out.append(terrace_band(pts, 3 + i * 0.7, "#B4D27A", "#A8A498", "#605A52", 80 + i))
    # foreground: the great agricultural terraces stepping down from the Guardhouse
    out.append(Q([(-10, 444), (-10, 290), (60, 300), (130, 320), (170, 340), (200, 380), (230, 420), (240, 444)], f"url(#{u}-slope)"))
    for i in range(8):
        t = i / 7
        y0 = 296 + i * 16 + t * t * 16
        x1 = 150 + i * 18
        pts = rough([(-10, y0), (x1 * 0.55, y0 + 8 + i * 1.5), (x1, y0 + 20 + i * 3)], 90 + i, amp=1.0, depth=2)
        h_ = 4 + i * 1.4
        out.append(Q([(x, y - 2) for x, y in pts] + [(x1 + 8, y0 + 40), (-10, y0 + 30)], "#80AC52" if i % 2 else "#78A44C"))
        out.append(f'<polyline points="{P([(x, y - 6 - i) for x, y in pts])}" fill="none" stroke="#A4C86E" stroke-width="{2 + i * 0.6:.1f}" opacity="0.6"/>')
        out.append(terrace_band(pts, h_, "#C4DC88", "#ACA89A", "#5E5850", 100 + i))
    # right foreground: a grassy terrace where the llamas graze
    rs = [(250, 444), (290, 412), (360, 396), (450, 388), (530, 384), (610, 382), (610, 444)]
    out.append(Q(rs, "#6E9A48"))
    out.append(terrace_band(rough([(250, 444), (290, 412), (360, 396), (450, 388), (530, 384), (610, 382)], 130, amp=1, depth=2)[::1], 0.1, "#C4DC88", "#ACA89A", "#5E5850", 131, blocks=False))
    out.append(grass(140, 120, (290, 392, 610, 444), ["#A8C86A", "#5E8A3E", "#C8DC8E"], h=(4, 11), sw=1.4))
    out.append(llama(560, 398, 0.45, flip=True, patch="#5A3E2E"))
    out.append(llama(440, 432, 1.15))
    out.append(grass(40, 121, (390, 424, 500, 440), ["#A8C86A", "#5E8A3E", "#C8DC8E"], h=(4, 9), sw=1.4))
    # an Andean condor gliding high over the gorge
    out.append('<g transform="translate(236 150) rotate(-4) scale(0.9)" fill="#2E3440"><path d="M 0 0 C -10 -4 -24 -6 -40 -2 L -44 1 L -38 0 L -40 3 L -34 2 L -30 4 C -18 3 -8 2 0 3 Z"/>'
               '<path d="M 0 0 C 10 -4 24 -6 40 -2 L 44 1 L 38 0 L 40 3 L 34 2 L 30 4 C 18 3 8 2 0 3 Z"/><path d="M -3 -1 L 3 -1 L 2 8 L -2 8 Z"/>'
               '<path d="M -12 -0.5 L 12 -0.5 L 9 1.5 L -9 1.5 Z" fill="#F2EEE6"/><circle cx="0" cy="-3" r="2" fill="#C88A7A"/></g>')
    return "\n".join(out)


BUILD = {
    "machu-picchu": (machu_picchu, "MACHU PICCHU", "PERU · SOUTH AMERICA", "#2C4A3C", "#E8B04A", "#FBF4E4", "#E8C878"),
    "rio-de-janeiro": (rio, "RIO DE JANEIRO", "BRASIL · CIDADE MARAVILHOSA", "#14503A", "#F2C443", "#FFF6E2", "#F6D27A"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("world", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
