"""World Places, Asia set (painted edition): nine new travel posters composed like small gouache paintings —
a real viewpoint, a time of day with a light direction, atmospheric depth and small truthful details.
Same layout and helpers as world_painted.py (which stays untouched)."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from places_painted import Cam, palm_tree, puff_column
from world_painted import (Q, blossoms, branch, cumulus, defs, figure, gulls, leaf_canopy, lerp, mix, streak_cloud, water_lines)
from poster import poster


# ---------------------------------------------------------------- shared helpers
def smooth(pts, closed=False, t=0.5):
    """Catmull-Rom spline through pts as an SVG path 'd'."""
    if closed:
        pts = pts + pts[:2]
        seg = [(pts[i - 1], pts[i], pts[i + 1], pts[i + 2]) for i in range(1, len(pts) - 2)]
        d = f"M {pts[1][0]:.1f} {pts[1][1]:.1f} "
    else:
        ext = [pts[0]] + pts + [pts[-1]]
        seg = [(ext[i - 1], ext[i], ext[i + 1], ext[i + 2]) for i in range(1, len(ext) - 2)]
        d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f} "
    for p0, p1, p2, p3 in seg:
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        d += f"C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f} "
    return d + ("Z" if closed else "")


def arch(x0, x1, yb, ys, ya):
    """Pointed (Mughal / Gothic) arch: jambs from yb up to the springing line ys, apex at ya."""
    xc = (x0 + x1) / 2
    h = ys - ya
    w = x1 - x0
    return (f"M {x0:.1f} {yb:.1f} L {x0:.1f} {ys:.1f} C {x0:.1f} {ys - h * 0.62:.1f} {xc - w * 0.2:.1f} {ya + h * 0.18:.1f} {xc:.1f} {ya:.1f} "
            f"C {xc + w * 0.2:.1f} {ya + h * 0.18:.1f} {x1:.1f} {ys - h * 0.62:.1f} {x1:.1f} {ys:.1f} L {x1:.1f} {yb:.1f} Z")


def rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{extra}/>'


def flock(spec, color, sw=1.8):
    return gulls(spec, color, sw)


def ripple_reflection(n, seed, x, y0, y1, w, colors, op=(0.35, 0.9), spread=0.0):
    """Broken horizontal dashes under a light source: a shimmering column reflection."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        yy = rnd.uniform(y0, y1)
        k = (yy - y0) / max(1, y1 - y0)
        ww = rnd.uniform(0.3, 1.0) * w * (1 + spread * k)
        xx = x + rnd.gauss(0, w * 0.25 * (1 + spread * k))
        out.append(f'<rect x="{xx - ww / 2:.1f}" y="{yy:.1f}" width="{ww:.1f}" height="{rnd.uniform(0.8, 2.2):.1f}" rx="0.8" fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


# ================================================================ TAJ MAHAL — from the garden canal at dawn
def onion(cx, base, half_base, bulge, top, steps=None):
    """Right-hand onion-dome profile mirrored into a closed outline."""
    H = base - top
    prof = steps or [(0, 0.86), (0.1, 0.95), (0.22, 1.0), (0.34, 1.0), (0.48, 0.94), (0.6, 0.82), (0.7, 0.66), (0.79, 0.46),
                     (0.86, 0.28), (0.91, 0.15), (0.955, 0.07), (1.0, 0.02)]
    right = [(cx + (half_base if t == 0 else bulge * r), base - H * t) for t, r in prof]
    left = [(2 * cx - x, y) for x, y in right[::-1]]
    return smooth(left + right) + " Z"


def taj_building(u, s, cx, gy, shade, front, lit, deep, inlay):
    """The mausoleum seen face-on from the south, sunrise light from the east (right). s = px per metre,
    gy = y of the plinth base. Returns markup (gradients are defined by the caller)."""
    o = []
    X = lambda m: cx + m * s
    Y = lambda m: gy - m * s
    # --- marble plinth with its blind arcade
    o.append(rect(X(-47.5), Y(6.7), 95 * s, 6.7 * s, f"url(#{u}-plinth)"))
    o.append(rect(X(-47.5), Y(6.7), 95 * s, 0.7 * s, "#FFF6EE"))
    for i in range(23):
        x0 = X(-46.5 + i * 4.05)
        o.append(f'<path d="{arch(x0, x0 + 2.4 * s, Y(0.6), Y(3.6), Y(5.2))}" fill="{deep}" opacity="0.55"/>')
    o.append(rect(X(-47.5), Y(0.6), 95 * s, 0.6 * s, "#B8A0A8"))
    # --- minarets (behind the building edges, at the plinth corners), slight outward lean
    for side in (-1, 1):
        mx = X(side * 44.5)
        b0, top = Y(6.7), Y(6.7 + 40)
        w0, w1 = 2.6 * s, 2.0 * s
        lean = side * 0.9 * s
        shaft = [(mx - w0, b0), (mx - w1 + lean, top), (mx + w1 + lean, top), (mx + w0, b0)]
        o.append(Q(shaft, f"url(#{u}-min)"))
        for f in (0.0, 0.33, 0.66):  # three storeys: balconies with brackets
            yb = lerp(b0, top, f + 0.33) if f < 0.66 else top
            xx = mx + lean * (f + 0.33)
            wb = lerp(w0, w1, f + 0.33) + 1.4 * s
            o.append(rect(xx - wb, yb - 0.7 * s, 2 * wb, 1.1 * s, "#F6E6E0"))
            o.append(rect(xx - wb, yb + 0.4 * s, 2 * wb, 0.5 * s, deep, ' opacity="0.6"'))
            o.append(f'<g fill="{shade}">' + "".join(rect(xx - wb + j * wb / 3, yb + 0.4 * s, 0.35 * s, 1.4 * s, shade) for j in range(7)) + "</g>")
            o.append(rect(xx - wb, yb - 1.8 * s, 2 * wb, 1.1 * s, "none", f' stroke="{inlay}" stroke-width="0.8" opacity="0.6"'))
        for f in (0.12, 0.2, 0.45, 0.53, 0.78, 0.86):  # inlaid rings
            yy = lerp(b0, top, f)
            ww = lerp(w0, w1, f)
            o.append(rect(mx + lean * f - ww, yy, 2 * ww, 0.35 * s, inlay, ' opacity="0.45"'))
        # top chhatri: open pavilion with eight posts, eave, little dome and finial
        tx = mx + lean
        o.append(rect(tx - 2.2 * s, top - 3.4 * s, 4.4 * s, 3.4 * s, deep, ' opacity="0.75"'))
        for j in range(4):
            o.append(rect(tx - 2.2 * s + j * 1.3 * s, top - 3.4 * s, 0.45 * s, 3.4 * s, front))
        o.append(rect(tx - 2.9 * s, top - 3.9 * s, 5.8 * s, 0.6 * s, "#FFF6EE"))
        o.append(f'<path d="{onion(tx, top - 3.9 * s, 2.2 * s, 2.5 * s, top - 7.6 * s)}" fill="url(#{u}-dome)"/>')
        o.append(rect(tx - 0.2 * s, top - 9.4 * s, 0.4 * s, 1.9 * s, "#C8A86A"))
    # --- roof chhatris (behind the facade top)
    for side in (-1, 1):
        hx = X(side * 19)
        b = Y(6.7 + 30)
        o.append(rect(hx - 4.4 * s, b - 6 * s, 8.8 * s, 6 * s, deep, ' opacity="0.7"'))
        for j in range(4):
            o.append(rect(hx - 4.4 * s + j * 2.6 * s, b - 6 * s, 0.9 * s, 6 * s, lit if side > 0 and j > 1 else front))
        o.append(rect(hx - 5.4 * s, b - 6.9 * s, 10.8 * s, 1.0 * s, "#FFF4EC"))
        o.append(rect(hx - 4.6 * s, b - 8.0 * s, 9.2 * s, 1.1 * s, front))
        o.append(f'<path d="{onion(hx, b - 8 * s, 4.0 * s, 4.6 * s, b - 15.5 * s)}" fill="url(#{u}-dome)"/>')
        o.append(rect(hx - 0.25 * s, b - 18 * s, 0.5 * s, 2.6 * s, "#C8A86A"))
        o.append(f'<circle cx="{hx:.1f}" cy="{b - 16.4 * s:.1f}" r="{0.5 * s:.1f}" fill="#D8B878"/>')
    # --- drum and main dome
    db, dt = Y(6.7 + 31), Y(6.7 + 38)
    o.append(rect(X(-11), dt, 22 * s, db - dt, f"url(#{u}-drum)"))
    o.append(rect(X(-11), dt, 22 * s, 0.8 * s, "#FFF6EE"))
    o.append(rect(X(-11), db - 1.4 * s, 22 * s, 0.6 * s, inlay, ' opacity="0.4"'))
    dome = onion(cx, dt + 0.5 * s, 11 * s, 13.2 * s, Y(6.7 + 65))
    o.append(f'<path d="{dome}" fill="url(#{u}-dome)"/>')
    o.append(f'<clipPath id="{u}-dc"><path d="{dome}"/></clipPath>')
    o.append(f'<g clip-path="url(#{u}-dc)">'
             f'<ellipse cx="{X(-9):.1f}" cy="{Y(6.7 + 48):.1f}" rx="{8 * s:.1f}" ry="{16 * s:.1f}" fill="{shade}" opacity="0.45"/>'
             f'<ellipse cx="{X(6.5):.1f}" cy="{Y(6.7 + 50):.1f}" rx="{3.6 * s:.1f}" ry="{9 * s:.1f}" fill="#FFFFFF" opacity="0.55"/>'
             f'<ellipse cx="{X(8):.1f}" cy="{Y(6.7 + 51):.1f}" rx="{1.4 * s:.1f}" ry="{5 * s:.1f}" fill="#FFFFFF" opacity="0.8"/>'
             f'<rect x="{X(-14):.1f}" y="{dt - 1.5 * s:.1f}" width="{28 * s:.1f}" height="{2 * s:.1f}" fill="{shade}" opacity="0.35"/></g>')
    # lotus crest, finial with the crescent
    ly = Y(6.7 + 64.2)
    o.append(f'<g fill="#F2E2DA" stroke="{shade}" stroke-width="0.6">' + "".join(
        f'<path d="M {cx + i * 1.1 * s:.1f} {ly:.1f} q {0.55 * s:.1f} {-1.8 * s:.1f} {1.1 * s:.1f} 0 Z"/>' for i in range(-3, 3)) + "</g>")
    fy0 = ly - 0.4 * s
    o.append(rect(cx - 0.35 * s, fy0 - 9 * s, 0.7 * s, 9 * s, "#B8964E"))
    for j, r in enumerate((1.1, 0.9, 0.75)):
        o.append(f'<circle cx="{cx:.1f}" cy="{fy0 - (1.5 + j * 2.2) * s:.1f}" r="{r * s:.1f}" fill="#C8A458"/><circle cx="{cx + 0.3 * s:.1f}" cy="{fy0 - (1.7 + j * 2.2) * s:.1f}" r="{r * 0.45 * s:.1f}" fill="#F6DEA0"/>')
    o.append(f'<path d="M {cx - 1.2 * s:.1f} {fy0 - 9.6 * s:.1f} q {1.2 * s:.1f} {1.6 * s:.1f} {2.4 * s:.1f} 0" fill="none" stroke="#C8A458" stroke-width="{0.5 * s:.1f}" stroke-linecap="round"/>')
    # --- main block: chamfered corners left (shade) and right (sun), front face between
    fb, ft = Y(6.7), Y(6.7 + 28)
    o.append(rect(X(-28.5), ft, 6.5 * s, fb - ft, shade))
    o.append(rect(X(22), ft, 6.5 * s, fb - ft, lit))
    o.append(rect(X(-22), ft, 44 * s, fb - ft, front))
    # pishtaq (great portal frame) rises higher
    pt = Y(6.7 + 33)
    o.append(rect(X(-10.5), pt, 21 * s, fb - pt, front))
    o.append(rect(X(-10.5), pt, 21 * s, 0.9 * s, "#FFF8F0"))
    o.append(rect(X(-28.5), ft, 57 * s, 0.7 * s, "#FFF8F0"))
    o.append(rect(X(-28.5), ft + 0.7 * s, 57 * s, 0.6 * s, deep, ' opacity="0.45"'))
    o.append(rect(X(-10.5), pt + 0.9 * s, 21 * s, 0.6 * s, deep, ' opacity="0.45"'))
    for m in (-10.5, 10.5):
        o.append(rect(X(m) - (0.5 * s if m < 0 else 0), pt, 0.5 * s, fb - pt, deep if m < 0 else "#FFFFFF", ' opacity="0.35"'))
    # guldasta pinnacles
    for m in (-10.5, 10.5, -22, 22, -28.5, 28.5):
        top = (pt if abs(m) == 10.5 else ft) - 4.5 * s
        base = pt if abs(m) == 10.5 else ft
        o.append(rect(X(m) - 0.45 * s, top, 0.9 * s, base - top + 3 * s, lit if m > 0 else front))
        o.append(f'<path d="M {X(m) - 0.8 * s:.1f} {top:.1f} q {0.8 * s:.1f} {-2.4 * s:.1f} {1.6 * s:.1f} 0 Z" fill="{lit if m > 0 else front}"/>')
    # calligraphy frame around the great arch
    o.append(rect(X(-8.6), pt + 2 * s, 17.2 * s, fb - pt - 2 * s, "none", f' stroke="{inlay}" stroke-width="{0.55 * s:.1f}" opacity="0.65"'))
    # great iwan
    iw = arch(X(-7), X(7), fb, Y(6.7 + 17), Y(6.7 + 29))
    o.append(f'<path d="{iw}" fill="url(#{u}-iwan)"/>')
    o.append(f'<path d="{arch(X(-3.2), X(3.2), fb, Y(6.7 + 7), Y(6.7 + 12))}" fill="{deep}" opacity="0.8"/>')
    o.append(f'<path d="{arch(X(-3.2), X(3.2), Y(6.7 + 13.5), Y(6.7 + 17.5), Y(6.7 + 21))}" fill="{deep}" opacity="0.55"/>')
    o.append(f'<g stroke="{lit}" stroke-width="0.6" opacity="0.6">' + "".join(
        f'<line x1="{X(-3.2 + j * 0.8):.1f}" y1="{Y(6.7 + 13.5):.1f}" x2="{X(-3.2 + j * 0.8):.1f}" y2="{Y(6.7 + 18.5):.1f}"/>' for j in range(1, 8)) + "</g>")
    o.append(f'<path d="{iw}" fill="none" stroke="{inlay}" stroke-width="{0.35 * s:.1f}" opacity="0.5"/>')
    # spandrel flowers (pietra dura)
    for sx in (-1, 1):
        o.append(f'<circle cx="{X(sx * 8):.1f}" cy="{Y(6.7 + 29.6):.1f}" r="{0.7 * s:.1f}" fill="#C88A86" opacity="0.7"/>')
    # side bays: two storeys of arched alcoves on the front, and on each chamfer
    for side in (-1, 1):
        for (a, b, tone) in ((15.8, 4.6, None), (25.5, 2.6, "ch")):
            mx = X(side * a)
            for lo, hi_, ap in ((6.7, 6.7 + 10.5, 6.7 + 14), (6.7 + 15, 6.7 + 23.5, 6.7 + 26.5)):
                path = arch(mx - b * s, mx + b * s, Y(lo), Y(hi_), Y(ap))
                col = deep
                op = 0.9 if (tone and side < 0) else 0.7
                o.append(f'<path d="{path}" fill="{col}" opacity="{op}"/>')
                # sunlit inner jamb on the right side of each recess
                o.append(rect(mx + b * s * 0.55, Y(hi_), b * s * 0.45, Y(lo) - Y(hi_), lit, ' opacity="0.55"'))
                o.append(f'<path d="{path}" fill="none" stroke="{inlay}" stroke-width="0.7" opacity="0.4"/>')
            o.append(rect(mx - (b + 1.4) * s, Y(6.7 + 14.4), (2 * b + 2.8) * s, 0.5 * s, inlay, ' opacity="0.35"'))
    o.append(rect(X(-28.5), Y(6.7 + 1.0), 57 * s, 0.6 * s, inlay, ' opacity="0.35"'))
    # rim light on the right edges
    o.append(rect(X(28.5) - 0.8, ft, 1.6, fb - ft, "#FFE2C6", ' opacity="0.9"'))
    return "".join(o)


def taj_mahal():
    u = "tm"
    hz = 302
    C = Cam(f=900, cx=300, vpy=hz, eye=2.67)
    s = 2.9
    gy = 310
    out = [defs(
        lg(f"{u}-sky", [(0, "#46548A"), (0.3, "#7E80B4"), (0.55, "#C79AB8"), (0.75, "#F2B6A6"), (0.9, "#FBD3AE"), (1, "#FDE3BC")], 0, 0, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-pool", [(0, "#FCE0BC"), (0.15, "#F4BEA8"), (0.45, "#C49ABA"), (1, "#6E74A8")], 0, hz, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-dome", [(0, "#B4ADCB"), (0.35, "#DCD3E2"), (0.68, "#FFF1E8"), (0.86, "#FFE6D6"), (1, "#EAC6BE")], 0, 0, 1, 0),
        lg(f"{u}-drum", [(0, "#BDB5D0"), (0.5, "#EEE2E6"), (1, "#FFEADC")], 0, 0, 1, 0),
        lg(f"{u}-min", [(0, "#B8B0CC"), (0.45, "#E4DAE4"), (0.8, "#FFF0E6"), (1, "#E6CCC8")], 0, 0, 1, 0),
        lg(f"{u}-plinth", [(0, "#D6CCDC"), (0.5, "#F2E6E6"), (1, "#FFEEE2")], 0, 0, 1, 0),
        lg(f"{u}-iwan", [(0, "#8E86A8"), (0.55, "#A89CB6"), (1, "#E8CFCB")], 0, 0, 1, 0),
        lg(f"{u}-red", [(0, "#A86A6E"), (1, "#C9827A")], 0, 0, 1, 0),
        lg(f"{u}-lawn", [(0, "#7E9278"), (1, "#3E5A40")], 0, hz, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-walk", [(0, "#E8B8A6"), (1, "#B87A6E")], 0, hz, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#FBDCC0", 0), (0.6, "#F8D6C2", 0.75), (1, "#F2D2C8", 0.95)], 0, 250, 0, 316, units="userSpaceOnUse"),
        lg(f"{u}-cyp", [(0, "#22362E"), (0.6, "#2E4636"), (1, "#5E6A48")], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="{hz + 2}" fill="url(#{u}-sky)"/>')
    out.append(glow(560, 268, 300, "#FFD6A8", f"{u}-g1", 0.75))
    out.append(glow(560, 272, 70, "#FFF0D0", f"{u}-g2", 0.95))
    out.append('<circle cx="566" cy="276" r="17" fill="#FFF4DC" opacity="0.95"/>')
    # thin dawn clouds catching pink light from below
    for x, y, w, c in ((110, 118, 100, "#E6A6B8"), (70, 132, 60, "#F2BCC0"), (470, 100, 120, "#F0AEB6"), (540, 116, 70, "#F8C4B8"),
                       (200, 196, 70, "#F6C2B8"), (420, 176, 90, "#FAD0BC"), (520, 214, 60, "#FCD8C0")):
        out.append(streak_cloud(x, y, w, c, 0.6, 3.6))
        out.append(streak_cloud(x + w * 0.15, y + 2.4, w * 0.55, "#FFE8D6", 0.55, 1.2))
    # the flanking mosque (west) and guest house (east): red sandstone, white domes, half lost in the haze
    for side in (-1, 1):
        x0 = 300 + side * 262
        out.append(Q([(x0, 312), (x0, 262), (x0 + side * 90, 262), (x0 + side * 90, 312)], f"url(#{u}-red)", ' opacity="0.8"'))
        out.append(f'<path d="{arch(x0 + side * 14 - 8, x0 + side * 14 + 8, 300, 278, 266)}" fill="#7A4A5A" opacity="0.6"/>')
        out.append(f'<path d="{onion(x0 + side * 36, 262, 13, 15, 228)}" fill="url(#{u}-dome)" opacity="0.9"/>')
        out.append(rect(x0 + side * 36 - 0.8, 220, 1.6, 9, "#C8A86A"))
        out.append(rect(x0 - 3, 236, 6, 76, "#B87A78", ' opacity="0.85"'))
        out.append(f'<path d="{onion(x0, 236, 4.5, 5.5, 222)}" fill="url(#{u}-dome)" opacity="0.9"/>')
    # far garden trees and haze
    rnd = random.Random(3)
    for side in (-1, 1):
        for k in range(9):
            x = 300 + side * rnd.uniform(150, 330)
            out.append(leaf_canopy(f"{u}-ft{side}{k}", x, rnd.uniform(286, 300), rnd.uniform(26, 44), rnd.uniform(14, 22), 30 + k + (side > 0) * 20,
                                   "#6E7A8A", "#8A92A0", "#C8B4B0", light=(1, -1), n=26))
    out.append(f'<rect x="0" y="250" width="600" height="70" fill="url(#{u}-haze)"/>')
    # the Taj
    body = taj_building(u, s, 300, gy, "#B4AACC", "#F0DEE0", "#FFF4EA", "#8A7EA4", "#6E6280")
    out.append(body)
    out.append(rect(130, 308, 340, 6, "#C9887E"))  # red sandstone terrace line
    out.append(rect(130, 308, 340, 1.4, "#F6C6AE"))
    out.append(mist(300, 316, 330, 14, "#FCE6D4", f"{u}-m1", 0.8))
    # ground plane: lawns, walks, pool
    out.append(Q([(-10, 316), (610, 316), (610, 444), (-10, 444)], f"url(#{u}-lawn)"))

    def gx(X, y):  # screen x of a ground line at lateral offset X, at screen y
        z = C.f * C.eye / max(0.01, y - hz)
        return 300 + C.f * X / z

    def band(X0, X1, y0=313, y1=446):
        return [(gx(X0, y0), y0), (gx(X1, y0), y0), (gx(X1, y1), y1), (gx(X0, y1), y1)]

    for sg in (-1, 1):
        for j in range(6):
            out.append(Q(band(sg * (9.5 + j * 6), sg * (12.5 + j * 6)), "#9AAE86", ' opacity="0.16"'))
    for sg in (-1, 1):
        out.append(Q(band(sg * 4.0, sg * 7.2), f"url(#{u}-walk)"))
        out.append(Q(band(sg * 12.5, sg * 14.5), f"url(#{u}-walk)", ' opacity="0.8"'))
        # marigold beds along the walks
        rnd = random.Random(40 + sg)
        fl = []
        for _ in range(170):
            y = 318 + (rnd.random() ** 1.7) * 128
            X = sg * rnd.uniform(7.6, 9.4)
            x = gx(X, y)
            r = 0.6 + (y - 316) / 128 * 2.6
            fl.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{rnd.choice(["#F29A2E", "#F7B940", "#E8742A", "#FFD27A"])}"/>')
        out.append("".join(fl))
        out.append(grass(110, 50 + sg, (gx(sg * 8, 444) if sg > 0 else -10, 360, 610 if sg > 0 else gx(sg * 8, 444), 444), ["#5E7A50", "#7E9A60", "#3E5A3E"], h=(4, 9), sw=1.2))
    # pool: sky colours, the reflection, ripples, marble rim
    pool = band(-3.6, 3.6, 311, 446)
    out.append(f'<clipPath id="{u}-pc"><polygon points="{P(pool)}"/></clipPath>')
    out.append(Q(pool, f"url(#{u}-pool)"))
    refl = taj_building(u + "r", s, 300, gy, "#A8A2C4", "#E2D2DA", "#F6E2DA", "#8E86A8", "#7A6E86")
    rdefs = defs(lg(f"{u}r-dome", [(0, "#A8A2C4"), (0.5, "#D6CCDC"), (1, "#F2D8D0")], 0, 0, 1, 0),
                 lg(f"{u}r-drum", [(0, "#A8A2C4"), (1, "#EAD8D8")], 0, 0, 1, 0),
                 lg(f"{u}r-min", [(0, "#A8A2C4"), (1, "#EAD8D8")], 0, 0, 1, 0),
                 lg(f"{u}r-plinth", [(0, "#C2B8CC"), (1, "#E8D8D8")], 0, 0, 1, 0),
                 lg(f"{u}r-iwan", [(0, "#7E7898"), (1, "#C8B0BC")], 0, 0, 1, 0))
    out.append(rdefs)
    out.append(f'<g clip-path="url(#{u}-pc)"><g opacity="0.62" transform="translate(0 {2 * gy + 2}) scale(1 -1)">{refl}</g>'
               + water_lines(140, 5, (150, 314, 450, 444), ["#FCE6D4", "#8E86B0", "#FFFFFF"], w=(6, 34), h=(0.6, 1.6), opacity=(0.25, 0.7))
               + "</g>")
    for sg in (-1, 1):
        out.append(f'<line x1="{gx(sg * 3.6, 311):.1f}" y1="311" x2="{gx(sg * 3.6, 446):.1f}" y2="446" stroke="#FFF0E2" stroke-width="2.6"/>')
        out.append(f'<line x1="{gx(sg * 3.9, 311):.1f}" y1="311" x2="{gx(sg * 3.9, 446):.1f}" y2="446" stroke="#B89AA6" stroke-width="1.6"/>')
    # fountain nozzles down the centre line
    out.append("".join(f'<circle cx="300" cy="{hz + C.f * C.eye / z:.1f}" r="{max(0.6, 30 / z):.1f}" fill="#7E7698"/>' for z in (20, 24, 29, 35, 43, 53, 66, 84, 110, 150)))
    # cypress avenues
    rnd = random.Random(8)
    for sg in (-1, 1):
        for z in (150, 120, 96, 78, 64, 53, 44, 37):
            X = sg * 13.5
            x, base = C(X, 0, z)
            h = C.f * rnd.uniform(8.5, 10) / z
            w = C.f * 1.5 / z
            tip = base - h
            pts = [(x - w * 0.15, base), (x - w * 0.5, base - h * 0.25), (x - w * 0.55, base - h * 0.5), (x - w * 0.38, base - h * 0.75), (x, tip),
                   (x + w * 0.38, base - h * 0.75), (x + w * 0.55, base - h * 0.5), (x + w * 0.5, base - h * 0.25), (x + w * 0.15, base)]
            d = smooth(pts) + " Z"
            sh = [(x - w * 0.4, base), (x - w * 0.1 - h * 0.9, base + w * 0.06 + h * 0.04), (x - h * 0.9, base + w * 0.3 + h * 0.05), (x + w * 0.4, base + w * 0.12)]
            out.append(Q(sh, "#2A3A40", ' opacity="0.28"'))
            out.append(f'<path d="{d}" fill="url(#{u}-cyp)"/>')
            # sunlit right flank and leafy texture
            out.append(f'<clipPath id="{u}-cy{sg}{z}"><path d="{d}"/></clipPath><g clip-path="url(#{u}-cy{sg}{z})">'
                       + f'<ellipse cx="{x + w * 0.5:.1f}" cy="{base - h * 0.5:.1f}" rx="{w * 0.32:.1f}" ry="{h * 0.5:.1f}" fill="#B8A66A" opacity="0.45"/>'
                       + blobs(int(h / 3), int(z * 7 + sg), (x - w * 0.5, tip, x + w * 0.5, base), ["#1A2A24", "#4A5E40", "#8A8A58"], r=(w * 0.06, w * 0.16), opacity=(0.3, 0.7), squash=0.5)
                       + "</g>")
            out.append(f'<ellipse cx="{x - w * 0.3:.1f}" cy="{base:.1f}" rx="{w * 0.9:.1f}" ry="{w * 0.12:.1f}" fill="#24342C" opacity="0.4"/>')
    # visitors: a couple on the left walk, a woman in a saffron sari on the right
    out.append(figure(gx(-5.2, 352), 352, 15, "#2E4A7A", head="#2A1E1E"))
    out.append(figure(gx(-5.8, 350), 350, 13, "#E8E0D6", head="#2A1E1E"))
    xs, ys = gx(5.4, 372), 372
    out.append(figure(xs, ys, 19, "#E8862E", head="#2A1E1E", legs="#E8862E", rim="#FFD8A8", rim_side=1))
    out.append(f'<path d="M {xs - 2:.1f} {ys - 17:.1f} q 4 6 3 17 l 3 0 q 0 -10 -4 -17 Z" fill="#C8402E" opacity="0.9"/>')
    out.append(figure(gx(4.8, 330), 330, 7, "#E8E2D8"))
    # birds over the dome
    out.append(flock([(150, 160, 9), (168, 150, 7), (182, 166, 6), (430, 132, 8), (448, 140, 6)], "#5A4A6E", 1.7))
    return "\n".join(out)



# ================================================================ BALI — rice terraces, a temple's split gate, late morning
def coconut(x, base, h, lean, seed, trunk="#8A7058", trunk_lit="#C8A880", dark="#2A4E2A", mid="#4A7E34", lit="#A8C85A", light=-1, nuts=True):
    """Coconut palm: bowed ringed trunk, crown of pinnate fronds built from leaflet strokes, lit from `light` side."""
    rnd = random.Random(seed)
    tx, ty = x + lean * h, base - h
    cxp, cyp = x + lean * h * 0.15 - light * h * 0.04, base - h * 0.55
    w0, w1 = max(1.4, h * 0.03), max(1.0, h * 0.019)
    o = [f'<path d="M {x - w0:.1f} {base:.1f} Q {cxp - w0:.1f} {cyp:.1f} {tx - w1:.1f} {ty:.1f} L {tx + w1:.1f} {ty:.1f} Q {cxp + w0:.1f} {cyp:.1f} {x + w0:.1f} {base:.1f} Z" fill="{trunk}"/>']
    o.append(f'<path d="M {x + light * w0 * 0.6:.1f} {base:.1f} Q {cxp + light * w0 * 0.6:.1f} {cyp:.1f} {tx + light * w1 * 0.5:.1f} {ty:.1f}" fill="none" stroke="{trunk_lit}" stroke-width="{max(1, w1 * 0.8):.1f}" opacity="0.8"/>')
    rings = []
    for i in range(int(h / 7)):
        t = i / (h / 7)
        px = (1 - t) ** 2 * x + 2 * (1 - t) * t * cxp + t * t * tx
        py = (1 - t) ** 2 * base + 2 * (1 - t) * t * cyp + t * t * ty
        ww = lerp(w0, w1, t)
        rings.append(f'<path d="M {px - ww:.1f} {py:.1f} q {ww:.1f} {ww * 0.5:.1f} {2 * ww:.1f} 0"/>')
    o.append(f'<g fill="none" stroke="#5A4636" stroke-width="{max(0.7, h * 0.005):.1f}" opacity="0.6">{"".join(rings)}</g>')
    fronds_back, fronds_front = [], []
    n = 14
    for i in range(n):
        ang = -math.pi + (i + rnd.uniform(-0.3, 0.3)) * math.pi * 2 / n
        L = h * rnd.uniform(0.27, 0.36)
        up = math.sin(ang) < 0
        ex = tx + L * math.cos(ang) * (1 if abs(math.cos(ang)) > 0.2 else 0.6)
        ey = ty + L * math.sin(ang) * 0.45 + L * (0.42 if not up else 0.22) * (0.6 + 0.4 * abs(math.cos(ang)))
        mx = tx + (ex - tx) * 0.5
        my = ty + (ey - ty) * 0.5 - L * 0.28
        seg = []
        for j in range(1, 19):
            t = j / 19
            px = (1 - t) ** 2 * tx + 2 * (1 - t) * t * mx + t * t * ex
            py = (1 - t) ** 2 * ty + 2 * (1 - t) * t * my + t * t * ey
            dx = 2 * (1 - t) * (mx - tx) + 2 * t * (ex - mx)
            dy = 2 * (1 - t) * (my - ty) + 2 * t * (ey - my)
            dl = math.hypot(dx, dy) or 1
            nx, ny = -dy / dl, dx / dl
            ll = L * 0.2 * (1 - t * 0.65) * rnd.uniform(0.8, 1.1)
            for sgn in (-1, 1):
                lx = px + sgn * nx * ll * 0.7 + dx / dl * ll * 0.35
                ly = py + sgn * ny * ll * 0.7 + ll * 0.55 + dy / dl * ll * 0.35
                facing = (sgn * nx * light) > 0 or ly < py
                seg.append((px, py, lx, ly, facing))
        sw = max(0.8, h * 0.0075)
        strokes = "".join(f'<path d="M {a:.1f} {b:.1f} Q {(a + c) / 2:.1f} {min(b, d) - 1:.1f} {c:.1f} {d:.1f}" stroke="{lit if f and rnd.random() < 0.65 else (mid if rnd.random() < 0.6 else dark)}"/>'
                          for a, b, c, d, f in seg)
        rach = f'<path d="M {tx:.1f} {ty:.1f} Q {mx:.1f} {my:.1f} {ex:.1f} {ey:.1f}" stroke="{mix(lit, "#E8E0A0", 0.4)}" stroke-width="{sw * 1.1:.1f}"/>'
        g = f'<g fill="none" stroke-width="{sw:.1f}" stroke-linecap="round">{strokes}{rach}</g>'
        (fronds_back if up else fronds_front).append(g)
    o += fronds_back
    if nuts:
        o.append("".join(f'<circle cx="{tx + dx * h * 0.012:.1f}" cy="{ty + h * 0.03 + dy * h * 0.01:.1f}" r="{h * 0.017:.1f}" fill="{c}"/>'
                         for dx, dy, c in ((-1.5, 0.5, "#6E7A2E"), (1.2, 0.8, "#8A8A3A"), (0, 1.6, "#5E6A2A"), (-0.4, 0.2, "#A8A040"))))
    o += fronds_front
    return "".join(o)


def candi_half(gx, base, k, side, u, light=-1):
    """One half of a candi bentar (Balinese split gate): brick body with grey carved-stone tiers; the inner face is
    sheer as if the mountain were cut in two. side=-1 is the left half (inner face at gx on its right)."""
    tiers = [(46, 12, "stone"), (42, 30, "brick"), (47, 4, "cap"), (38, 13, "brick"), (42, 4, "cap"), (33, 14, "brick"), (37, 4, "cap"),
             (27, 12, "brick"), (31, 4, "cap"), (21, 11, "brick"), (24, 3.5, "cap"), (15, 10, "brick"), (18, 3, "cap"), (9, 9, "stone"), (4, 7, "stone")]
    o = []
    y = base
    rnd = random.Random(int(gx * 3 + side))
    for i, (w, h, kind) in enumerate(tiers):
        w, h = w * k, h * k
        x0, x1 = (gx - w, gx) if side < 0 else (gx, gx + w)
        if kind == "brick":
            o.append(rect(x0, y - h, w, h, f"url(#{u}-brick)"))
            # brick courses and joints
            rows = max(2, int(h / (3.2 * k)))
            for r_ in range(rows):
                yy = y - h + r_ * h / rows
                o.append(rect(x0, yy, w, 0.5 * k, "#E8B8A0", ' opacity="0.35"'))
                off = (r_ % 2) * 4 * k
                o.append("".join(rect(x0 + off + j * 8 * k, yy, 0.5 * k, h / rows, "#6A2E22", ' opacity="0.35"') for j in range(int(w / (8 * k)) + 1) if x0 + off + j * 8 * k < x1))
            # carved paras panel in the big body
            if h > 20 * k:
                px0 = x0 + w * 0.22
                o.append(rect(px0, y - h * 0.85, w * 0.56, h * 0.7, "#9C988C"))
                o.append(rect(px0 + 1.5 * k, y - h * 0.85 + 1.5 * k, w * 0.56 - 3 * k, h * 0.7 - 3 * k, "#B8B2A2"))
                o.append(f'<g fill="none" stroke="#7A766C" stroke-width="{0.9 * k:.1f}">' + "".join(
                    f'<path d="M {px0 + w * 0.28 + a * w * 0.12:.1f} {y - h * 0.5 + b * h * 0.18:.1f} c {3 * k:.1f} {-4 * k:.1f} {7 * k:.1f} {-1 * k:.1f} {4 * k:.1f} {2 * k:.1f} c {-2 * k:.1f} {2 * k:.1f} {-5 * k:.1f} 0 {-3 * k:.1f} {-2 * k:.1f}"/>'
                    for a, b in ((-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1))) + "</g>")
            # sun on the outer (left) flank, shadow on the right
            if side < 0:
                o.append(rect(x0, y - h, 2.4 * k, h, "#F2A27A", ' opacity="0.7"'))
            else:
                o.append(rect(x1 - 3 * k, y - h, 3 * k, h, "#4A1E1A", ' opacity="0.35"'))
        else:
            col = "#C8C2B0" if kind == "cap" else "#A8A496"
            if kind == "cap":
                # projecting cornice with curling corner ornaments (karang) on the outer side
                o.append(rect(x0, y - h, w, h, col))
                o.append(rect(x0, y - h, w, h * 0.35, "#ECE6D2"))
                o.append(rect(x0, y - 0.6 * k, w, 0.6 * k, "#5A5248", ' opacity="0.5"'))
                ox = x0 if side < 0 else x1
                o.append(f'<path d="M {ox:.1f} {y - h:.1f} q {side * -2 * k:.1f} {-6 * k:.1f} {side * 1.5 * k:.1f} {-8 * k:.1f} q {side * 2 * k:.1f} {2 * k:.1f} {side * 0.5 * k:.1f} {4 * k:.1f} Z" fill="#B8B2A0"/>')
                o.append(f'<path d="M {ox + side * 1 * k:.1f} {y - h - 2 * k:.1f} q {side * -1 * k:.1f} {-3 * k:.1f} {side * 1 * k:.1f} {-5 * k:.1f}" stroke="#ECE6D2" stroke-width="{0.8 * k:.1f}" fill="none"/>')
            else:
                o.append(rect(x0, y - h, w, h, col))
                o.append(f'<g fill="none" stroke="#6E6A60" stroke-width="{0.8 * k:.1f}" opacity="0.7">' + "".join(
                    f'<path d="M {x0 + j * 5 * k:.1f} {y - h * 0.3:.1f} q {2.5 * k:.1f} {-h * 0.5:.1f} {5 * k:.1f} 0"/>' for j in range(int(w / (5 * k)))) + "</g>")
                if side < 0:
                    o.append(rect(x0, y - h, 2 * k, h, "#F6EEDC", ' opacity="0.6"'))
        y -= h
    # moss and weathering
    o.append(blobs(18, int(gx), (gx - 40 * k if side < 0 else gx, base - 60 * k, gx if side < 0 else gx + 40 * k, base), ["#4E6A3A", "#6E8A4A"], r=(1 * k, 3 * k), opacity=(0.3, 0.6), squash=0.6))
    # the sheer inner face, in shade
    o.append(rect(gx - (2.2 * k if side < 0 else 0), y, 2.2 * k, base - y, "#3A1A1A" if side > 0 else "#F0B090", ' opacity="0.45"'))
    return "".join(o)


def meru(cx, base, k, tiers=5, u="m"):
    """Balinese meru shrine: masonry base, wooden body, stacked roofs of black sugar-palm thatch (ijuk)."""
    o = [rect(cx - 15 * k, base - 12 * k, 30 * k, 12 * k, "#B5523A"), rect(cx - 16 * k, base - 13 * k, 32 * k, 2 * k, "#C8C2B0"),
         rect(cx - 9 * k, base - 22 * k, 18 * k, 9 * k, "#7A3E2A"), rect(cx - 3 * k, base - 21 * k, 6 * k, 8 * k, "#C89A3A")]
    y = base - 22 * k
    for i in range(tiers):
        w = (24 - i * 3.6) * k
        h = (8 - i * 0.6) * k
        o.append(f'<path d="M {cx - w:.1f} {y:.1f} Q {cx - w * 0.6:.1f} {y - h * 0.4:.1f} {cx - w * 0.35:.1f} {y - h:.1f} L {cx + w * 0.35:.1f} {y - h:.1f} Q {cx + w * 0.6:.1f} {y - h * 0.4:.1f} {cx + w:.1f} {y:.1f} Z" fill="#2A2422"/>')
        o.append(f'<path d="M {cx - w:.1f} {y:.1f} Q {cx - w * 0.6:.1f} {y - h * 0.4:.1f} {cx - w * 0.35:.1f} {y - h:.1f} L {cx - w * 0.1:.1f} {y - h:.1f} Q {cx - w * 0.4:.1f} {y - h * 0.4:.1f} {cx - w * 0.6:.1f} {y:.1f} Z" fill="#6A5E52" opacity="0.8"/>')
        o.append(f'<path d="M {cx - w:.1f} {y:.1f} L {cx + w:.1f} {y:.1f}" stroke="#4A3E36" stroke-width="{1.2 * k:.1f}"/>')
        y -= h
        if i < tiers - 1:
            o.append(rect(cx - w * 0.3, y - 3 * k, w * 0.6, 3 * k, "#7A3E2A"))
            y -= 3 * k
    o.append(rect(cx - 1.2 * k, y - 8 * k, 2.4 * k, 8 * k, "#C89A3A"))
    o.append(f'<circle cx="{cx:.1f}" cy="{y - 8 * k:.1f}" r="{1.8 * k:.1f}" fill="#E8C060"/>')
    return "".join(o)


def penjor(x, base, h, lean=1, seed=1):
    """Penjor: tall bamboo pole arching over at the top, palm-leaf ornaments and a hanging sampian."""
    tx, ty = x + lean * h * 0.42, base - h * 0.82
    o = [f'<path d="M {x:.1f} {base:.1f} Q {x - lean * 2:.1f} {base - h * 0.95:.1f} {tx:.1f} {ty:.1f}" fill="none" stroke="#C8A860" stroke-width="2.6" stroke-linecap="round"/>',
         f'<path d="M {x + 1:.1f} {base:.1f} Q {x - lean * 1:.1f} {base - h * 0.95:.1f} {tx:.1f} {ty:.1f}" fill="none" stroke="#F2E2A0" stroke-width="0.9" opacity="0.8"/>']
    rnd = random.Random(seed)
    for t in [0.35 + 0.05 * i for i in range(12)]:
        px = (1 - t) ** 2 * x + 2 * (1 - t) * t * (x - lean * 2) + t * t * tx
        py = (1 - t) ** 2 * base + 2 * (1 - t) * t * (base - h * 0.95) + t * t * ty
        o.append(f'<path d="M {px:.1f} {py:.1f} q {rnd.uniform(-5, 5):.1f} 5 {rnd.uniform(-3, 3):.1f} {rnd.uniform(7, 11):.1f}" stroke="#E8D890" stroke-width="1.3" fill="none"/>')
    o.append(f'<path d="M {tx:.1f} {ty:.1f} l 0 10" stroke="#E8D890" stroke-width="1.2"/><path d="M {tx - 4:.1f} {ty + 10:.1f} q 4 -4 8 0 q -1 8 -4 12 q -3 -4 -4 -12 Z" fill="#E8D070"/>'
             f'<path d="M {tx - 2:.1f} {ty + 12:.1f} l 4 0" stroke="#D8504A" stroke-width="1.6"/>')
    o.append(f'<path d="M {x - 3:.1f} {base - h * 0.28:.1f} l 6 0 l -1 8 l -4 0 Z" fill="#E8C860"/>')
    return "".join(o)


def duck(x, y, k, flip=False):
    sx = -k if flip else k
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({sx:.2f} {k:.2f})">'
            '<path d="M -6 -3 Q -6 -8 0 -8 L 4 -8 Q 3 -12 5 -14 Q 8 -15 9 -12 L 11 -11.5 L 9 -10.5 Q 8 -8 7 -6 Q 6 -1 0 -1 Q -5 -1 -6 -3 Z" fill="#FAF6EC"/>'
            '<path d="M -6 -3 Q -1 -2 5 -3 Q 1 0 -4 -1 Z" fill="#C8C2B4"/><circle cx="7.4" cy="-12.2" r="0.7" fill="#2A2A2A"/><path d="M 9 -12 L 11.5 -11.4 L 9 -10.8 Z" fill="#E8A040"/>'
            '<path d="M -1 -1 L -1.5 2 M 2 -1 L 2.5 2" stroke="#E8A040" stroke-width="0.9"/></g>')


def farmer(x, base, k, flip=False):
    """Rice farmer bending to plant, wearing a conical hat (caping)."""
    sx = -k if flip else k
    return (f'<g transform="translate({x:.1f} {base:.1f}) scale({sx:.2f} {k:.2f})">'
            '<path d="M -4 0 L -3 -12 L 1 -12 L 2 0 Z" fill="#3A4A6A"/>'
            '<path d="M -5 -11 Q -2 -22 8 -22 L 10 -17 Q 2 -16 0 -9 Z" fill="#B8603A"/>'
            '<path d="M 6 -18 L 10 -6 M 3 -15 L 6 -5" stroke="#B8603A" stroke-width="2" stroke-linecap="round"/>'
            '<circle cx="11" cy="-21" r="2.6" fill="#6A4232"/>'
            '<path d="M 4 -22 L 11 -30 L 19 -21 Q 11 -19 4 -22 Z" fill="#E8D294"/><path d="M 11 -30 L 19 -21 Q 15 -20 12 -20.5 Z" fill="#B8A060"/>'
            '<path d="M 9 -5 l -1 4 M 11 -5 l 1 4" stroke="#7EA040" stroke-width="1.2"/></g>')


def bali():
    u = "bl"
    hz = 262
    out = [defs(
        lg(f"{u}-sky", [(0, "#2C78BC"), (0.4, "#5EA6DA"), (0.75, "#A8D4EA"), (1, "#E2F0EA")], 0, 0, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-agung", [(0, "#7894C0"), (0.55, "#8EA8CC"), (1, "#B8CCDC")], 0, 130, 0, 290, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#E2F0EA", 0), (1, "#E6F2EA", 0.85)], 0, 220, 0, 290, units="userSpaceOnUse"),
        lg(f"{u}-brick", [(0, "#C8664A"), (0.5, "#B2503A"), (1, "#8E3C2E")], 0, 0, 1, 0),
        lg(f"{u}-flood", [(0, "#CFE8F0"), (1, "#8CC2DC")], 0, 0, 0, 1),
    )]
    out.append(f'<rect width="600" height="{hz + 40}" fill="url(#{u}-sky)"/>')
    out.append(glow(60, 40, 280, "#FFFBE6", f"{u}-sun", 0.55))
    out.append(cumulus(f"{u}-c1", 470, 150, 190, 54, 3, "#FFFFFF", "#F2F6FA", "#B8C8DC", hi="#FFFFFF", hi_op=0.75))
    out.append(cumulus(f"{u}-c2", 560, 118, 110, 34, 4, "#FFFFFF", "#EEF4FA", "#B8C8DC", hi="#FFFFFF", hi_op=0.7))
    out.append(cumulus(f"{u}-c3", 90, 112, 120, 30, 5, "#FFFFFF", "#F2F6FA", "#BCCADE", hi="#FFFFFF", hi_op=0.7))
    out.append(streak_cloud(300, 96, 70, "#FFFFFF", 0.5, 3))
    # Mount Agung: steep concave cone with a ragged summit
    cx, top = 236, 150

    def ay(x):
        d = abs(x - cx)
        return top + 8 + 150 * (1 - math.exp(-max(0, d - 6) / 120)) * (1.03 if x > cx else 1)

    prof = [(x, ay(x)) for x in range(-10, 611, 6)]
    summit = rough([(cx - 16, top + 10), (cx - 8, top + 1), (cx + 1, top + 6), (cx + 8, top), (cx + 17, top + 10)], 3, amp=3, depth=3)
    prof = [p for p in prof if p[0] < cx - 16] + summit + [p for p in prof if p[0] > cx + 17]
    out.append(Q(prof + [(610, 300), (-10, 300)], f"url(#{u}-agung)"))
    out.append(Q([p for p in prof if p[0] >= cx + 4] + [(610, 300), (cx + 30, 300)], "#5E78A8", ' opacity="0.3"'))
    out.append(f'<clipPath id="{u}-ag"><polygon points="{P(prof + [(610, 300), (-10, 300)])}"/></clipPath>')
    rnd = random.Random(6)
    rav = []
    for i in range(40):
        side = -1 if i % 2 else 1
        x0 = cx + side * rnd.uniform(4, 90)
        y0 = ay(x0) + rnd.uniform(1, 8)
        L_ = rnd.uniform(20, 70)
        rav.append(f'<path d="M {x0:.1f} {y0:.1f} q {side * L_ * 0.2:.1f} {L_ * 0.5:.1f} {side * L_ * 0.45:.1f} {L_:.1f}" stroke="{"#A8BCD8" if side < 0 else "#6A82AE"}" stroke-width="{rnd.uniform(0.9, 2):.1f}" fill="none" opacity="0.6"/>')
    out.append(f'<g clip-path="url(#{u}-ag)">{"".join(rav)}</g>')
    out.append(cumulus(f"{u}-c4", 300, 214, 120, 22, 9, "#FFFFFF", "#EEF2F6", "#C2CEDC", hi="#FFFFFF", hi_op=0.6))
    out.append(f'<rect x="0" y="210" width="600" height="80" fill="url(#{u}-haze)"/>')
    # distant forested ridge with tiny palms
    poly, r1 = ridge_poly([(-10, 258), (80, 250), (190, 262), (300, 254), (420, 248), (520, 258), (610, 250)], 4, amp=4, fill="#7EA6A0")
    out.append(poly)
    out.append(blobs(70, 41, (-10, 250, 610, 268), ["#6E9A92", "#8EB4AA"], r=(3, 7), opacity=(0.5, 0.9)))
    for x in (40, 70, 150, 330, 360, 470, 500, 560):
        y = y_on(r1, x) or 256
        out.append(palm_tree(x, y + 2, 20, trunk="#6E928C", frond="#6E928C", seed=x, lean=0.1))
    # mid ridge with jungle
    poly, r2 = ridge_poly([(-10, 284), (100, 276), (220, 286), (340, 280), (460, 272), (610, 278)], 7, amp=4, fill="#4E8460")
    out.append(poly)
    out.append(leaf_canopy(f"{u}-j1", 80, 280, 80, 12, 11, "#2E5E44", "#4E8460", "#8AB870", light=(-1, -1), n=40, r=(0.3, 0.5)))
    out.append(leaf_canopy(f"{u}-j2", 560, 276, 70, 12, 12, "#2E5E44", "#4E8460", "#8AB870", light=(-1, -1), n=36, r=(0.3, 0.5)))
    for x, hh in ((130, 46), (170, 38), (296, 42), (540, 50), (590, 40)):
        out.append(coconut(x, (y_on(r2, x) or 280) + 3, hh, 0.08 if x % 2 else -0.06, x, trunk="#5E6A4E", trunk_lit="#9AA27A", dark="#2E5A3E", mid="#4A7A4A", lit="#8EB06A", nuts=False))
    # the temple on its terrace: wall, meru towers, frangipani, split gate, steps, penjor
    tb = 300
    out.append(Q([(330, tb + 2), (330, 288), (600, 286), (600, tb + 4)], "#5E8A4A"))
    out.append(meru(512, 292, 1.25, 7))
    out.append(meru(364, 292, 0.9, 3))
    out.append(rect(300, 281, 300, 15, "#A84A36"))
    out.append(rect(300, 279, 300, 3.5, "#C8C2B0"))
    out.append("".join(rect(300 + j * 12, 283 + (j % 2) * 4, 0.6, 4, "#6A2E22", ' opacity="0.4"') for j in range(25)))
    out.append(leaf_canopy(f"{u}-fr", 562, 268, 32, 18, 13, "#4E6A3A", "#6E8A4A", "#A8C070", light=(-1, -1), n=26))
    out.append(dots(26, 14, (536, 254, 590, 282), "#FFFFFF", r=(1.4, 2.2), opacity=(0.9, 1)))
    out.append(dots(12, 15, (536, 254, 590, 282), "#F6D060", r=(0.7, 1.0), opacity=(0.9, 1)))
    gk = 1.05
    out.append(candi_half(430, tb, gk, -1, u))
    out.append(candi_half(446, tb, gk, 1, u))
    for j in range(6):
        w = 22 + j * 4
        out.append(rect(438 - w / 2, tb + j * 3.2, w, 3.2, "#B8B0A0" if j % 2 else "#D2CCBC"))
    out.append(f'<g fill="#F2D060">{dots(8, 16, (432, 296, 444, 300), "#E8503A", r=(0.8, 1.3), opacity=(1, 1))}</g>')
    out.append(penjor(398, tb + 4, 150, 1, 3))
    # terraces: contour lips from far to near; surfaces split into fields (flooded / young / ripening)
    N = 17
    lines = []
    for k in range(N):
        t = k / (N - 1)
        base = 300 + 150 * t ** 1.45
        amp = 2 + 16 * t ** 1.4
        per = 220 + 140 * t
        ph = 30 * k
        lines.append([(x, base + amp * math.sin((x + ph) / per * 2 * math.pi) + (x - 300) * 0.035 * (1 - t)) for x in range(-20, 641, 10)])
    rnd = random.Random(21)
    fields = {"flood": ("url(#%s-flood)" % u, "#6EA8C8"), "young": ("#9CCB48", "#C8E070"), "green": ("#5E9E38", "#86BE4A"), "ripe": ("#C2BE58", "#E2D47A")}
    for k in range(N - 1):
        t = k / (N - 1)
        riser = 1.5 + 8 * t ** 1.3
        top_l, bot_l = lines[k], lines[k + 1]
        # riser: the grassy bank dropping from this lip to the terrace below
        surf_top = [(x, y + riser) for x, y in top_l]
        # field segments
        x = -20
        while x < 640:
            w = rnd.uniform(70, 160) * (0.6 + t)
            xa, xb = x, min(640, x + w)
            kind = rnd.choices(list(fields), weights=(3, 3, 3, 1.3))[0]
            fill, line_c = fields[kind]
            seg_top = [(px, py) for px, py in surf_top if xa <= px <= xb]
            seg_bot = [(px, py) for px, py in bot_l if xa <= px <= xb]
            if len(seg_top) >= 2:
                poly = seg_top + seg_bot[::-1]
                out.append(Q(poly, fill))
                # planting rows parallel to the contour
                rows = []
                for r_ in range(1, 4 + int(t * 5)):
                    f = r_ / (4 + int(t * 5))
                    pts = [(a, b + (d - b) * f) for (a, b), (c, d) in zip(seg_top, seg_bot)]
                    rows.append(f'<polyline points="{P(pts)}" stroke-dasharray="{1 + t * 2:.1f} {1.5 + t * 2:.1f}"/>')
                out.append(f'<g fill="none" stroke="{line_c}" stroke-width="{0.6 + t * 1.4:.1f}" opacity="0.75">{"".join(rows)}</g>')
                if kind == "flood":
                    # glints of sky and a cloud reflection
                    mx = (xa + xb) / 2
                    my = y_on(seg_top, mx) or seg_top[0][1]
                    out.append(f'<ellipse cx="{mx:.1f}" cy="{my + 3 + t * 5:.1f}" rx="{w * 0.25:.1f}" ry="{1 + t * 2:.1f}" fill="#FFFFFF" opacity="0.65"/>')
                # little dike between fields
                y0 = y_on(top_l, xb) or 0
                y1 = y_on(bot_l, xb) or 0
                out.append(f'<line x1="{xb:.1f}" y1="{y0 + riser:.1f}" x2="{xb + 6 * t:.1f}" y2="{y1:.1f}" stroke="#4E7A34" stroke-width="{1 + 2 * t:.1f}"/>')
            x = xb
        out.append(Q(top_l + [(x_, y_ + riser) for x_, y_ in top_l][::-1], "#3E6E30"))
        out.append(f'<polyline points="{P([(x_, y_ + riser * 0.5) for x_, y_ in top_l])}" fill="none" stroke="#2E5A26" stroke-width="{riser * 0.4:.1f}" opacity="0.5"/>')
        out.append(f'<polyline points="{P(top_l)}" fill="none" stroke="#D6EC8A" stroke-width="{0.8 + t * 1.6:.1f}" opacity="0.9"/>')
        if t > 0.3:
            out.append(grass(int(40 * t), 300 + k, (-10, top_l[30][1] - 4, 610, top_l[30][1] + riser), ["#4E8A34", "#7EAE48", "#2E5A26"], h=(3, 6 + 6 * t), sw=1.1))
    # life on the terraces: a farmer planting, a line of ducks on a dike
    fy = (y_on(lines[11], 250) or 400) - 2
    out.append(farmer(250, fy + 18, 1.0))
    out.append(f'<ellipse cx="258" cy="{fy + 19:.1f}" rx="12" ry="1.6" fill="#FFFFFF" opacity="0.5"/>')
    ly = lines[8]
    for i in range(7):
        x = 410 + i * 13
        out.append(duck(x, (y_on(ly, x) or 380) + 0.5, 0.8, flip=True))
    # foreground palms framing the left, a young palm on the right
    out.append(coconut(70, 470, 330, 0.16, 31, light=-1))
    out.append(coconut(30, 470, 260, -0.12, 32, light=-1))
    out.append(coconut(560, 460, 150, -0.1, 33, light=-1))
    # a fish kite riding the trade wind
    out.append('<g transform="translate(150 150) rotate(-14)"><path d="M -14 0 Q -4 -9 10 -3 L 18 -8 L 15 0 L 18 8 L 10 3 Q -4 9 -14 0 Z" fill="#E8463A"/>'
               '<path d="M -14 0 Q -4 -9 10 -3 L 10 3 Q -4 9 -14 0 Z" fill="#F2C040" opacity="0.7"/><circle cx="-8" cy="-1" r="1.6" fill="#1E1E1E"/>'
               '<path d="M 0 0 Q 30 30 70 60 Q 100 90 150 110" fill="none" stroke="#FFFFFF" stroke-width="0.9" opacity="0.7"/></g>')
    out.append(flock([(330, 120, 8), (346, 128, 6)], "#2E4A6A", 1.6))
    return "\n".join(out)


# ================================================================ build
BUILD = {
    "taj-mahal": (taj_mahal, "TAJ MAHAL", "INDIA · AGRA", "#1E4A52", "#F4B49A", "#FFF4EC", "#F6C9A8"),
    "bali": (bali, "BALI", "INDONESIA · ASIA", "#1F4A30", "#E8C35A", "#FFF6E0", "#E8D58A"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("world", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
