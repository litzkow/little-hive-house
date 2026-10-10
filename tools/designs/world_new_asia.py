"""World Places, Asia set (painted edition): nine travel posters composed like small gouache paintings —
Taj Mahal, Bali, Bangkok, Hong Kong, Kyoto, Tokyo, Seoul, Great Wall, Ha Long Bay — each with a real viewpoint,
its own time of day and palette, atmospheric depth and small truthful details. Run this file to regenerate all
nine (or pass slugs to rebuild only those). Same layout and helpers as world_painted.py (left untouched)."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from places_painted import Cam, palm_tree, puff_column
from world_painted import (Q, blossoms, branch, cumulus, defs, figure, gulls, leaf_canopy, lerp, mix, streak_cloud, water_lines)
from poster import poster
from world_new_b1 import win_grid


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
    u = "taj"
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
    # far garden trees and haze
    rnd = random.Random(3)
    for side in (-1, 1):
        for k in range(9):
            x = 300 + side * rnd.uniform(150, 330)
            out.append(leaf_canopy(f"{u}-ft{side}{k}", x, rnd.uniform(286, 300), rnd.uniform(26, 44), rnd.uniform(14, 22), 30 + k + (side > 0) * 20,
                                   "#6E7A8A", "#8A92A0", "#C8B4B0", light=(1, -1), n=26))
    out.append(f'<rect x="0" y="250" width="600" height="70" fill="url(#{u}-haze)"/>')
    # the Taj
    body = taj_building(u, s, 300, gy, "#C2B2CC", "#F8E6DE", "#FFF6EC", "#A08EB0", "#7A6888")
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
            out.append(Q(sh, "#5A4A6A", ' opacity="0.14"'))
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
    """Morning on the terraces: a candi bentar at the top of a stone stair frames Mount Agung in its cleft;
    the rice terraces step up toward it, coconut palms frame the view. Sun from the upper left."""
    u = "bali"
    out = [defs(
        lg(f"{u}-sky", [(0, "#2A72B8"), (0.35, "#4E98D2"), (0.7, "#96C8E6"), (1, "#D8ECEC")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-agung", [(0, "#6A84B6"), (0.5, "#8AA2C8"), (1, "#B6CADC")], 0, 120, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#DCEEEA", 0), (1, "#E2F2EC", 0.9)], 0, 215, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-brick", [(0, "#D2724E"), (0.55, "#B8563C"), (1, "#8E3E2E")], 0, 0, 1, 0),
        lg(f"{u}-flood", [(0, "#BEE0EE"), (0.6, "#9CCDE4"), (1, "#7EB6D6")], 0, 0, 0, 1),
        lg(f"{u}-young", [(0, "#B6DA5A"), (1, "#86BC3E")], 0, 0, 0, 1),
        lg(f"{u}-green", [(0, "#7EB844"), (1, "#4E9232")], 0, 0, 0, 1),
        lg(f"{u}-ripe", [(0, "#D8D468"), (1, "#B4B44A")], 0, 0, 0, 1),
        lg(f"{u}-stair", [(0, "#BCAE96"), (1, "#8E7E68")], 0, 296, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="310" fill="url(#{u}-sky)"/>')
    out.append(glow(70, 50, 300, "#FFFBE2", f"{u}-sun", 0.6))
    out.append(cumulus(f"{u}-c1", 500, 128, 170, 46, 3, "#FFFFFF", "#F2F6FA", "#B6C6DC", hi="#FFFFFF", hi_op=0.75))
    out.append(cumulus(f"{u}-c3", 96, 104, 130, 32, 5, "#FFFFFF", "#F2F6FA", "#BCCADE", hi="#FFFFFF", hi_op=0.7))
    out.append(streak_cloud(300, 84, 80, "#FFFFFF", 0.45, 3))
    out.append(streak_cloud(420, 72, 50, "#FFFFFF", 0.4, 2.4))
    # Mount Agung: steep concave cone, ragged summit, centred so the gate's cleft frames it
    cx, top = 300, 128

    def ay(x):
        d = abs(x - cx)
        return top + 6 + 168 * (1 - math.exp(-max(0, d - 8) / 150)) * (1.04 if x > cx else 1)

    prof = [(x, ay(x)) for x in range(-10, 611, 6)]
    summit = rough([(cx - 14, top + 7), (cx - 6, top + 1), (cx + 2, top + 5), (cx + 8, top), (cx + 15, top + 8)], 3, amp=3, depth=3)
    prof = [p for p in prof if p[0] < cx - 14] + summit + [p for p in prof if p[0] > cx + 15]
    agp = prof + [(610, 310), (-10, 310)]
    out.append(Q(agp, f"url(#{u}-agung)"))
    out.append(Q([p for p in prof if p[0] >= cx + 4] + [(610, 310), (cx + 40, 310)], "#4E68A0", ' opacity="0.28"'))
    out.append(f'<clipPath id="{u}-ag"><polygon points="{P(agp)}"/></clipPath>')
    rnd = random.Random(6)
    rav = []
    for i in range(56):
        side = -1 if i % 2 else 1
        x0 = cx + side * rnd.uniform(3, 110)
        y0 = ay(x0) + rnd.uniform(1, 8)
        L_ = rnd.uniform(18, 80)
        rav.append(f'<path d="M {x0:.1f} {y0:.1f} q {side * L_ * 0.18:.1f} {L_ * 0.5:.1f} {side * L_ * 0.42:.1f} {L_:.1f}" stroke="{"#AFC2DC" if side < 0 else "#6680B0"}" stroke-width="{rnd.uniform(0.9, 2.2):.1f}" fill="none" opacity="0.6"/>')
    out.append(f'<g clip-path="url(#{u}-ag)">{"".join(rav)}'
               f'<path d="M {cx - 10:.1f} {top + 4:.1f} q -3 5 -1 10 M {cx + 6:.1f} {top + 3:.1f} q 2 6 0 11" stroke="#5A6E9A" stroke-width="1.6" fill="none"/></g>')
    # a thin plume of steam from the crater (Agung is an active volcano)
    out.append(streak_cloud(cx + 26, top - 6, 26, "#FFFFFF", 0.5, 4))
    out.append(streak_cloud(cx + 52, top - 10, 22, "#FFFFFF", 0.35, 3))
    out.append(cumulus(f"{u}-c4", 150, 236, 190, 34, 9, "#FFFFFF", "#EEF2F6", "#C2CEDC", hi="#FFFFFF", hi_op=0.6))
    out.append(cumulus(f"{u}-c5", 470, 232, 210, 36, 10, "#FFFFFF", "#EEF2F6", "#C2CEDC", hi="#FFFFFF", hi_op=0.6, light=-1))
    out.append(f'<rect x="0" y="215" width="600" height="95" fill="url(#{u}-haze)"/>')
    # far jungle ridge with small palms
    poly, r1 = ridge_poly([(-10, 266), (90, 258), (200, 268), (300, 262), (420, 254), (520, 264), (610, 256)], 4, amp=4, fill="#88AEA4")
    out.append(poly)
    out.append(blobs(80, 41, (-10, 256, 610, 274), ["#7AA49A", "#9ABEB2"], r=(3, 7), opacity=(0.5, 0.9)))
    for x in (30, 64, 118, 486, 522, 580):
        out.append(palm_tree(x, (y_on(r1, x) or 262) + 2, 22, trunk="#78A098", frond="#78A098", seed=x, lean=0.1))
    poly, r2 = ridge_poly([(-10, 290), (100, 282), (220, 290), (380, 286), (470, 278), (610, 284)], 7, amp=4, fill="#4E8460")
    out.append(poly)
    out.append(leaf_canopy(f"{u}-j1", 70, 286, 90, 14, 11, "#2E5E44", "#4E8460", "#8AB870", light=(-1, -1), n=44, r=(0.3, 0.5)))
    out.append(leaf_canopy(f"{u}-j2", 540, 282, 90, 14, 12, "#2E5E44", "#4E8460", "#8AB870", light=(-1, -1), n=44, r=(0.3, 0.5)))
    for x, hh in ((112, 64), (150, 50), (470, 58), (508, 70), (580, 52)):
        out.append(coconut(x, (y_on(r2, x) or 286) + 4, hh, 0.08 if x % 2 else -0.06, x, trunk="#5E6A4E", trunk_lit="#9AA27A", dark="#2E5A3E", mid="#4A7A4A", lit="#8EB06A", nuts=False))
    # the pura: courtyard wall, meru towers and a frangipani behind, split gate in front
    tb = 300
    out.append(meru(452, 290, 1.05, 7))
    out.append(meru(156, 290, 0.8, 3))
    out.append(leaf_canopy(f"{u}-fr", 524, 270, 34, 20, 13, "#4E6A3A", "#6E8A4A", "#A8C070", light=(-1, -1), n=28))
    out.append(dots(30, 14, (494, 254, 556, 284), "#FFFFFF", r=(1.5, 2.3), opacity=(0.9, 1)))
    out.append(dots(16, 15, (494, 254, 556, 284), "#F6D060", r=(0.7, 1.0), opacity=(0.9, 1)))
    out.append(rect(60, 280, 480, 18, f"url(#{u}-brick)"))
    out.append(rect(56, 277, 488, 4, "#D8D2C0"))
    out.append(rect(56, 280.5, 488, 1.2, "#7A7464", ' opacity="0.5"'))
    out.append("".join(rect(62 + j * 11 + (r_ % 2) * 5.5, 284 + r_ * 4, 0.7, 4, "#6A2E22", ' opacity="0.45"') for r_ in range(3) for j in range(43)))
    out.append("".join(rect(60, 283.6 + r_ * 4, 480, 0.6, "#E8B8A0", ' opacity="0.35"') for r_ in range(4)))
    gk = 1.28
    out.append(candi_half(272, tb, gk, -1, u))
    out.append(candi_half(328, tb, gk, 1, u))
    # guardian statues wearing black-and-white poleng cloth beside the stair
    for sx in (-1, 1):
        x = 300 + sx * 58
        out.append(rect(x - 7, tb - 6, 14, 7, "#A8A292") + rect(x - 7, tb - 6, 14, 1.6, "#D8D2C0"))
        out.append(f'<path d="M {x - 5:.1f} {tb - 6:.1f} L {x - 4:.1f} {tb - 22:.1f} Q {x:.1f} {tb - 28:.1f} {x + 4:.1f} {tb - 22:.1f} L {x + 5:.1f} {tb - 6:.1f} Z" fill="#8A8676"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{tb - 29:.1f}" r="4.2" fill="#7A7666"/><circle cx="{x - 1.4:.1f}" cy="{tb - 30:.1f}" r="1.8" fill="#A8A292"/>')
        chk = "".join(rect(x - 5 + i * 2.5, tb - 18 + j * 2.5, 2.5, 2.5, "#1E1E1E" if (i + j) % 2 else "#F4F2EA") for i in range(4) for j in range(4))
        out.append(chk)
        out.append(f'<path d="M {x - 6:.1f} {tb - 34:.1f} q 6 -9 12 0 Z" fill="#F2E8C0"/>')  # payung umbrella hint
    # stone stair descending toward us through the terraces
    st = [(274, tb), (326, tb), (348, 446), (252, 446)]
    out.append(Q(st, f"url(#{u}-stair)"))
    sl = []
    for j in range(16):
        f = (j / 16) ** 1.35
        y = tb + (446 - tb) * f
        hw = 26 + 22 * f
        sl.append(rect(300 - hw, y, 2 * hw, 1.2 + 2.6 * f, "#EEE2C8"))
        sl.append(rect(300 - hw, y + 1.2 + 2.6 * f, 2 * hw, 0.8 + 1.4 * f, "#6E6858", ' opacity="0.45"'))
    out.append("".join(sl))
    out.append(Q([(300, tb), (326, tb), (348, 446), (300, 446)], "#5A4A3A", ' opacity="0.16"'))
    out.append(blobs(26, 72, (262, tb + 30, 338, 444), ["#7E9A4A", "#9AAE5A"], r=(1.2, 3), opacity=(0.4, 0.8), squash=0.5))
    for ox, oy in ((288, 303), (306, 306), (296, 312)):  # canang sari: palm-leaf trays of flowers on the steps
        out.append(rect(ox - 4, oy - 2, 8, 3, "#9CC24A") + rect(ox - 4, oy - 2, 8, 0.8, "#D8EC8A"))
        out.append("".join(f'<circle cx="{ox + dx:.1f}" cy="{oy - 2.5:.1f}" r="1.3" fill="{c}"/>' for dx, c in ((-2.4, "#E8443A"), (0, "#FFFFFF"), (2.4, "#F6C030"), (-1.2, "#E880B0"))))
    out.append(penjor(214, tb - 2, 168, -1, 3))
    out.append(penjor(386, tb - 2, 168, 1, 4))
    # terraces: contour lips from far to near, each band = sunlit riser wall + planted surface
    N = 11
    lines = []
    for k in range(N + 1):
        t = k / N
        base = 302 + 146 * t ** 1.25
        amp = 3 + 12 * t
        lines.append([(x, base + amp * math.sin((x + 40 * k) / (230 + 120 * t) * 2 * math.pi) + 26 * (1 - t) * ((x - 300) / 300) ** 2) for x in range(-20, 641, 8)])
    rnd = random.Random(21)
    kinds = {"flood": (f"url(#{u}-flood)", "#6EA8C8"), "young": (f"url(#{u}-young)", "#D2EA80"), "green": (f"url(#{u}-green)", "#9ACE58"),
             "ripe": (f"url(#{u}-ripe)", "#EEE48A")}
    stair_clip = f'<clipPath id="{u}-ns"><path d="M -20 290 L 274 290 L 252 450 L -20 450 Z M 326 290 L 620 290 L 620 450 L 348 450 Z"/></clipPath>'
    terr = [stair_clip]
    for k in range(N):
        t = k / N
        riser = 2 + 9 * t ** 1.2
        top_l, bot_l = lines[k], lines[k + 1]
        surf_top = [(x, y + riser) for x, y in top_l]
        x = -20
        while x < 640:
            w = rnd.uniform(110, 230) * (0.7 + 0.6 * t)
            xa, xb = x, min(640, x + w)
            kind = rnd.choices(list(kinds), weights=(2.2, 3, 3, 1.2))[0]
            fill, line_c = kinds[kind]
            seg_top = [(px, py) for px, py in surf_top if xa <= px <= xb]
            seg_bot = [(px, py) for px, py in bot_l if xa <= px <= xb]
            if len(seg_top) >= 2:
                terr.append(Q(seg_top + seg_bot[::-1], fill))
                if kind == "flood":
                    mx = (xa + xb) / 2
                    my = (y_on(seg_top, mx) or seg_top[0][1]) + 2 + 4 * t
                    terr.append(f'<ellipse cx="{mx:.1f}" cy="{my:.1f}" rx="{w * 0.28:.1f}" ry="{0.8 + 1.6 * t:.1f}" fill="#FFFFFF" opacity="0.7"/>')
                    terr.append(f'<ellipse cx="{mx - w * 0.2:.1f}" cy="{my + 2 + 3 * t:.1f}" rx="{w * 0.12:.1f}" ry="{0.5 + 0.8 * t:.1f}" fill="#FFFFFF" opacity="0.5"/>')
                    # seedlings in rows on the water
                    terr.append(dots(int(w * (0.3 + t)), int(xa * 7 + k), (xa + 4, my + 3, xb - 4, (y_on(seg_bot, mx) or my + 8) - 2), "#5E9A3A", r=(0.5 + t * 0.5, 1 + t), opacity=(0.7, 1)))
                else:
                    rows = []
                    nr = 2 + int(t * 6)
                    for r_ in range(1, nr):
                        f = r_ / nr
                        pts = [(a, b + (d - b) * f) for (a, b), (c, d) in zip(seg_top, seg_bot)]
                        rows.append(f'<polyline points="{P(pts)}" stroke-dasharray="{1.5 + t * 3:.1f} {2 + t * 2.5:.1f}"/>')
                    terr.append(f'<g fill="none" stroke="{line_c}" stroke-width="{0.7 + t * 1.3:.1f}" opacity="0.55">{"".join(rows)}</g>')
                # bund between fields
                y0, y1 = y_on(surf_top, xb), y_on(bot_l, xb)
                if y0 and y1:
                    terr.append(f'<path d="M {xb:.1f} {y0:.1f} Q {xb + 4 * t:.1f} {(y0 + y1) / 2:.1f} {xb + 2 + 6 * t:.1f} {y1:.1f}" stroke="#5E8A3A" stroke-width="{1 + 1.6 * t:.1f}" fill="none"/>')
            x = xb
        # riser wall: grassy bank in morning light, darker toward its foot
        terr.append(Q(top_l + surf_top[::-1], "#5E9A3E"))
        terr.append(f'<polyline points="{P([(x_, y_ + riser * 0.7) for x_, y_ in top_l])}" fill="none" stroke="#3E7230" stroke-width="{riser * 0.6:.1f}" opacity="0.7"/>')
        terr.append(f'<polyline points="{P(top_l)}" fill="none" stroke="#E2F29A" stroke-width="{0.9 + t * 1.6:.1f}"/>')
        if t > 0.25:
            terr.append(grass(int(40 * t), 300 + k, (-10, min(p[1] for p in top_l) - 2, 610, max(p[1] for p in top_l) + riser), ["#5E9A3A", "#7EAE48", "#A8CC5A"], h=(3, 4 + 5 * t), sw=1.0 + t * 0.3))
    out.append(f'<g clip-path="url(#{u}-ns)">' + "".join(terr) + "</g>")
    # edging of the stair: low stone walls with moss
    for sx in (-1, 1):
        out.append(f'<path d="M {300 + sx * 26:.1f} {tb:.1f} L {300 + sx * 48:.1f} 446" stroke="#6E6450" stroke-width="5" fill="none"/>'
                   f'<path d="M {300 + sx * 26:.1f} {tb:.1f} L {300 + sx * 48:.1f} 446" stroke="#DCCFB4" stroke-width="1.8" fill="none" transform="translate({-1.5 * sx} -1)"/>')
        out.append(blobs(14, 70 + sx, (300 + sx * 30 - 6, tb + 20, 300 + sx * 46 + 6, 440), ["#5E8A3A", "#7EA64A"], r=(1.5, 3.5), opacity=(0.5, 0.9)))
    # life: a farmer planting in a flooded field, ducks along a bund, an egret
    fy = (y_on(lines[7], 150) or 400)
    out.append(f'<ellipse cx="152" cy="{fy + 13:.1f}" rx="16" ry="2" fill="#FFFFFF" opacity="0.45"/>')
    out.append(farmer(146, fy + 13, 1.15))
    ly = lines[6]
    for i in range(6):
        x = 404 + i * 14
        out.append(duck(x, (y_on(ly, x) or 380) + 1, 0.85, flip=True))
    ex, ey = 214, (y_on(lines[4], 214) or 340) + 6
    out.append(f'<g transform="translate({ex} {ey}) scale(0.9)"><path d="M -6 0 Q -8 -8 -2 -10 L 4 -10 Q 8 -16 6 -22 Q 7 -26 10 -25 L 14 -24 L 10 -23 Q 9 -18 9 -12 Q 8 -4 0 -2 Z" fill="#FFFFFF"/>'
               '<path d="M -6 -1 Q -2 -2 4 -6" stroke="#C8D0D8" stroke-width="1.2" fill="none"/><path d="M -1 -2 L -2 6 M 2 -2 L 3 6" stroke="#2E2E2E" stroke-width="0.9"/></g>')
    # foreground coconut palms framing the view
    out.append(coconut(84, 470, 312, -0.13, 31, light=-1))
    out.append(coconut(36, 470, 230, 0.05, 32, light=-1))
    out.append(coconut(538, 470, 262, 0.1, 33, light=-1))
    out.append(flock([(380, 92, 8), (396, 100, 6), (186, 160, 6)], "#2E4A6A", 1.6))
    return "\n".join(out)


# ================================================================ BANGKOK — a riverside wat on the Chao Phraya, golden hour
def chofa_gable(cx, base, half, h, u, k, face="#A8282E", board="url(#bkk-gold)", horn=True, tiers=2):
    """Thai gable end seen face-on: nested gables, gold bargeboards with bai raka teeth, hang hong curls at the
    foot, chofa horn at the apex. base = y of the gable foot, half = half-width, h = height."""
    o = []
    ax, ay = cx, base - h
    # rear (higher) gables of the nested set, each peeking above the next
    for j in range(tiers, 0, -1):
        dy = j * 9 * k
        o.append(Q([(cx - half + j * 5 * k, base - dy * 0.4), (ax, ay - dy), (cx + half - j * 5 * k, base - dy * 0.4)], "#C46A2E"))
        o.append(f'<path d="M {cx - half + j * 5 * k:.1f} {base - dy * 0.4:.1f} L {ax:.1f} {ay - dy:.1f} L {cx + half - j * 5 * k:.1f} {base - dy * 0.4:.1f}" fill="none" stroke="#E8B848" stroke-width="{2.4 * k:.1f}"/>')
    o.append(Q([(cx - half, base), (ax, ay), (cx + half, base)], face))
    # na ban: the gilded gable panel — a deity medallion inside scrolling flame ornament
    o.append(Q([(cx - half * 0.78, base - 3 * k), (ax, ay + h * 0.16), (cx + half * 0.78, base - 3 * k)], "#7E1A24", ' opacity="0.5"'))
    o.append(f'<circle cx="{cx:.1f}" cy="{base - h * 0.36:.1f}" r="{h * 0.13:.1f}" fill="#E8B848"/><circle cx="{cx:.1f}" cy="{base - h * 0.36:.1f}" r="{h * 0.085:.1f}" fill="#B87A22"/>'
             f'<circle cx="{cx - h * 0.03:.1f}" cy="{base - h * 0.39:.1f}" r="{h * 0.04:.1f}" fill="#FFE6A0"/>')
    sc = []
    for sx in (-1, 1):
        for i in range(5):
            yy = base - h * (0.1 + i * 0.12)
            xx = cx + sx * (half * (0.3 + 0.15 * (3 - i) / 3) * (1 - i * 0.18))
            sc.append(f'<path d="M {cx + sx * h * 0.1:.1f} {yy:.1f} q {sx * 6 * k:.1f} {-5 * k:.1f} {xx - cx - sx * h * 0.1:.1f} {-1 * k:.1f} q {sx * 3 * k:.1f} {3 * k:.1f} {-sx * 1 * k:.1f} {5 * k:.1f}"/>')
    o.append(f'<g fill="none" stroke="#E8B848" stroke-width="{1.5 * k:.1f}" stroke-linecap="round">{"".join(sc)}</g>')
    # bargeboards with teeth (bai raka) and the hang hong curl at each foot
    for sx in (-1, 1):
        x0, y0 = cx + sx * half, base
        o.append(f'<path d="M {x0:.1f} {y0:.1f} L {ax:.1f} {ay:.1f}" stroke="{board}" stroke-width="{4.6 * k:.1f}" stroke-linecap="round"/>')
        L = math.hypot(ax - x0, ay - y0)
        nx, ny = (ay - y0) / L * -sx, (x0 - ax) / L * -sx
        nx, ny = -abs(nx) * sx * -1, ny
        teeth = []
        for i in range(1, int(L / (5 * k))):
            t = i * 5 * k / L
            px, py = x0 + (ax - x0) * t, y0 + (ay - y0) * t
            teeth.append(f'<path d="M {px:.1f} {py:.1f} l {sx * 3.4 * k:.1f} {-0.6 * k:.1f} l {-sx * 1.2 * k:.1f} {-2.6 * k:.1f} Z"/>')
        o.append(f'<g fill="#E8B848">{"".join(teeth)}</g>')
        o.append(f'<path d="M {x0:.1f} {y0:.1f} q {sx * 7 * k:.1f} {-1 * k:.1f} {sx * 8 * k:.1f} {-8 * k:.1f} q {-sx * 3 * k:.1f} {1 * k:.1f} {-sx * 3 * k:.1f} {4 * k:.1f}" fill="none" stroke="#F2C858" stroke-width="{2.4 * k:.1f}" stroke-linecap="round"/>')
    if horn:  # chofa: slender bird-head finial curling outward
        o.append(f'<path d="M {ax - 2 * k:.1f} {ay + 2 * k:.1f} Q {ax - 2 * k:.1f} {ay - 12 * k:.1f} {ax + 4 * k:.1f} {ay - 20 * k:.1f} Q {ax + 9 * k:.1f} {ay - 24 * k:.1f} {ax + 7 * k:.1f} {ay - 18 * k:.1f} '
                 f'Q {ax + 3 * k:.1f} {ay - 14 * k:.1f} {ax + 2 * k:.1f} {ay + 2 * k:.1f} Z" fill="#F2C858"/>')
        o.append(f'<path d="M {ax - 1 * k:.1f} {ay:.1f} Q {ax - 1 * k:.1f} {ay - 11 * k:.1f} {ax + 4 * k:.1f} {ay - 18 * k:.1f}" stroke="#FFF2C0" stroke-width="{0.9 * k:.1f}" fill="none"/>')
    return "".join(o)


def roof_skirt(cx, top_y, bot_y, x_in, x_out, side, k, u, chofa=True, th=14):
    """One sloping lower roof tier seen end-on: a band of orange glazed tile rows with a green border, gold edge
    board and a small upturned finial at its outer corner. side = -1 left, +1 right; th = tier thickness."""
    xi, xo = cx + side * x_in, cx + side * x_out
    T = th * k
    o = [Q([(xi, top_y), (xo, bot_y), (xo, bot_y + T), (xi, top_y + T * 1.1)], f"url(#{u}-tile)")]
    rows = "".join(f'<line x1="{xi:.1f}" y1="{top_y + T * f:.1f}" x2="{xo:.1f}" y2="{bot_y + T * f:.1f}"/>' for f in (0.25, 0.5))
    o.append(f'<g stroke="#A8481E" stroke-width="{0.9 * k:.1f}" opacity="0.55">{rows}</g>')
    o.append(Q([(xi, top_y + T * 0.72), (xo, bot_y + T * 0.68), (xo, bot_y + T), (xi, top_y + T * 1.1)], "#2E7A4E"))
    o.append(f'<line x1="{xi:.1f}" y1="{top_y + T * 0.72:.1f}" x2="{xo:.1f}" y2="{bot_y + T * 0.68:.1f}" stroke="#7EC08A" stroke-width="{0.8 * k:.1f}"/>')
    o.append(f'<line x1="{xi:.1f}" y1="{top_y:.1f}" x2="{xo:.1f}" y2="{bot_y:.1f}" stroke="#F2C858" stroke-width="{2.6 * k:.1f}"/>')
    # shadow cast on the tier below
    o.append(Q([(xi, top_y + T * 1.1), (xo, bot_y + T), (xo, bot_y + T + 3 * k), (xi, top_y + T * 1.1 + 4 * k)], "#3A1A10", ' opacity="0.25"'))
    if chofa:
        o.append(f'<path d="M {xo:.1f} {bot_y + 1 * k:.1f} q {side * 5 * k:.1f} {-1 * k:.1f} {side * 6 * k:.1f} {-10 * k:.1f} q {-side * 2 * k:.1f} {1 * k:.1f} {-side * 3 * k:.1f} {5 * k:.1f}" fill="none" stroke="#F2C858" stroke-width="{2.2 * k:.1f}" stroke-linecap="round"/>')
    return "".join(o)


def thai_hall(cx, base, k, u, seed=0):
    """Ubosot seen from its gable end: white platform, colonnade with lotus capitals, two lower roof tiers on each
    side and the nested main gable. Sun from the left."""
    o = []
    # platform and steps
    o.append(rect(cx - 122 * k, base - 12 * k, 244 * k, 12 * k, "#EDE2D0") + rect(cx - 122 * k, base - 12 * k, 244 * k, 2 * k, "#FFF6E4")
             + rect(cx + 60 * k, base - 12 * k, 62 * k, 12 * k, "#B8A8A0", ' opacity="0.35"'))
    o.append("".join(rect(cx - 22 * k, base - (3 + 3 * i) * k, 44 * k, 1.2 * k, "#C8B8A8") for i in range(3)))
    # walls behind the colonnade
    o.append(rect(cx - 100 * k, base - 66 * k, 200 * k, 54 * k, "#F4E6D0"))
    o.append(rect(cx + 20 * k, base - 66 * k, 80 * k, 54 * k, "#C8A8A0", ' opacity="0.35"'))
    for j in range(-2, 3):  # doorways / windows with gilded frames and pointed tops
        x = cx + j * 38 * k
        o.append(f'<path d="M {x - 8 * k:.1f} {base - 14 * k:.1f} L {x - 8 * k:.1f} {base - 44 * k:.1f} L {x:.1f} {base - 56 * k:.1f} L {x + 8 * k:.1f} {base - 44 * k:.1f} L {x + 8 * k:.1f} {base - 14 * k:.1f} Z" fill="#E8B848"/>')
        o.append(rect(x - 5.5 * k, base - 44 * k, 11 * k, 30 * k, "#5A1E22" if j else "#3A1418"))
        o.append(rect(x - 0.5 * k, base - 44 * k, 1 * k, 30 * k, "#B87A22"))
    # colonnade: square white pillars with gold lotus capitals, shade on their right faces
    for j in range(8):
        x = cx - 104 * k + j * 29.7 * k
        o.append(rect(x - 3.4 * k, base - 66 * k, 6.8 * k, 54 * k, "#FFF6E8") + rect(x + 1 * k, base - 66 * k, 2.4 * k, 54 * k, "#C8B0A8", ' opacity="0.6"'))
        o.append(f'<path d="M {x - 4.6 * k:.1f} {base - 66 * k:.1f} q {4.6 * k:.1f} {6 * k:.1f} {9.2 * k:.1f} 0 Z" fill="#E8B848"/>')
    o.append(rect(cx - 108 * k, base - 70 * k, 216 * k, 5 * k, "#C89838"))
    o.append(rect(cx - 108 * k, base - 70 * k, 216 * k, 1.4 * k, "#FFE6A0"))
    # roof: veranda tier over the colonnade, two upper tiers, then the nested main gable
    for side in (-1, 1):
        o.append(roof_skirt(cx, base - 104 * k, base - 76 * k, 60 * k, 128 * k, side, k, u, th=13))
    for side in (-1, 1):
        o.append(roof_skirt(cx, base - 126 * k, base - 98 * k, 50 * k, 104 * k, side, k, u, th=13))
    for side in (-1, 1):
        o.append(roof_skirt(cx, base - 146 * k, base - 120 * k, 40 * k, 80 * k, side, k, u, th=12))
    o.append(chofa_gable(cx, base - 112 * k, 50 * k, 98 * k, u, k))
    # sunlight raking the left half of the gable
    o.append(Q([(cx - 50 * k, base - 112 * k), (cx, base - 210 * k), (cx, base - 112 * k)], "#FFD890", ' opacity="0.14"'))
    return "".join(o)


def bell_chedi(cx, base, k, u):
    """Gilded bell-shaped chedi (Sri Lankan style, as at the Grand Palace) catching the low sun on its left."""
    o = []
    y = base
    for w, h in ((60, 9), (52, 8), (46, 8), (40, 7)):
        o.append(rect(cx - w * k, y - h * k, 2 * w * k, h * k, f"url(#{u}-gold)"))
        o.append(rect(cx - w * k, y - h * k, 2 * w * k, 1.4 * k, "#FFF0B0"))
        o.append(rect(cx - w * k, y - 1.4 * k, 2 * w * k, 1.4 * k, "#8A5A1E", ' opacity="0.5"'))
        y -= h * k
    # the bell
    bt = y - 74 * k
    bell = smooth([(cx - 44 * k, y), (cx - 42 * k, y - 22 * k), (cx - 34 * k, y - 48 * k), (cx - 20 * k, y - 66 * k), (cx - 10 * k, bt + 2 * k), (cx, bt)]
                  + [(cx + 10 * k, bt + 2 * k), (cx + 20 * k, y - 66 * k), (cx + 34 * k, y - 48 * k), (cx + 42 * k, y - 22 * k), (cx + 44 * k, y)]) + " Z"
    o.append(f'<path d="{bell}" fill="url(#{u}-gold)"/>')
    o.append(f'<clipPath id="{u}-bc"><path d="{bell}"/></clipPath><g clip-path="url(#{u}-bc)">'
             f'<ellipse cx="{cx - 22 * k:.1f}" cy="{y - 34 * k:.1f}" rx="{8 * k:.1f}" ry="{30 * k:.1f}" fill="#FFF6C8" opacity="0.7"/>'
             f'<ellipse cx="{cx - 24 * k:.1f}" cy="{y - 36 * k:.1f}" rx="{3 * k:.1f}" ry="{20 * k:.1f}" fill="#FFFFFF" opacity="0.7"/>'
             + "".join(f'<path d="M {cx - 46 * k:.1f} {y - i * 7 * k:.1f} Q {cx:.1f} {y - i * 7 * k + 5 * k:.1f} {cx + 46 * k:.1f} {y - i * 7 * k:.1f}" stroke="#A8701E" stroke-width="{0.6 * k:.1f}" fill="none" opacity="0.45"/>' for i in range(1, 10))
             + dots(int(70 * k), 77, (cx - 40 * k, bt, cx + 40 * k, y), "#FFF6C8", r=(0.5 * k, 1.1 * k), opacity=(0.4, 0.9)) + "</g>")
    o.append(f'<path d="M {cx - 44 * k:.1f} {y:.1f} Q {cx:.1f} {y + 4 * k:.1f} {cx + 44 * k:.1f} {y:.1f}" stroke="#FFE7A0" stroke-width="{2 * k:.1f}" fill="none"/>')
    # harmika with its little colonnade
    y = bt
    o.append(rect(cx - 13 * k, y - 12 * k, 26 * k, 12 * k, f"url(#{u}-gold)"))
    o.append("".join(rect(cx - 11 * k + j * 5.5 * k, y - 10 * k, 1.6 * k, 9 * k, "#8A5A1E", ' opacity="0.6"') for j in range(5)))
    o.append(rect(cx - 15 * k, y - 14 * k, 30 * k, 3 * k, "#F2C858"))
    y -= 14 * k
    # ringed spire, then a long plain pinnacle
    rings = 11
    for j in range(rings):
        w = (10 - j * 0.75) * k
        o.append(f'<ellipse cx="{cx:.1f}" cy="{y - j * 5 * k:.1f}" rx="{w:.1f}" ry="{2.6 * k:.1f}" fill="url(#{u}-gold)"/>'
                 f'<ellipse cx="{cx - w * 0.4:.1f}" cy="{y - j * 5 * k - 0.6 * k:.1f}" rx="{w * 0.3:.1f}" ry="{0.9 * k:.1f}" fill="#FFF2C0"/>')
    y -= rings * 5 * k
    o.append(Q([(cx - 2.4 * k, y + 2 * k), (cx, y - 40 * k), (cx + 2.4 * k, y + 2 * k)], f"url(#{u}-gold)"))
    o.append(f'<circle cx="{cx:.1f}" cy="{y - 14 * k:.1f}" r="{2.4 * k:.1f}" fill="#F2C858"/>')
    return "".join(o)


def longtail(x, wl, k, u):
    """Long-tail boat racing to the right: needle hull, flower garlands and ribbons on the raised bow,
    a boatman at the stern steering the long propeller shaft that throws a rooster tail of spray."""
    o = []
    L = 120 * k
    bow, stern = x + L, x - L
    # wake and spray
    o.append(f'<path d="M {stern - 60 * k:.1f} {wl + 2 * k:.1f} Q {x:.1f} {wl + 14 * k:.1f} {bow + 10 * k:.1f} {wl + 1 * k:.1f}" stroke="#FFF2D8" stroke-width="{2 * k:.1f}" fill="none" opacity="0.6"/>')
    o.append(water_lines(26, 401, (stern - 120 * k, wl + 2, x, wl + 16 * k), ["#FFF2D8", "#FFFFFF"], w=(10, 40), h=(1, 2), opacity=(0.4, 0.8)))
    hull = (f"M {stern:.1f} {wl - 9 * k:.1f} L {x + 40 * k:.1f} {wl - 8 * k:.1f} Q {bow - 10 * k:.1f} {wl - 10 * k:.1f} {bow + 8 * k:.1f} {wl - 36 * k:.1f} "
            f"L {bow + 10 * k:.1f} {wl - 33 * k:.1f} Q {bow - 2 * k:.1f} {wl - 2 * k:.1f} {x + 30 * k:.1f} {wl + 2 * k:.1f} L {stern + 4 * k:.1f} {wl + 1 * k:.1f} Z")
    o.append(f'<path d="{hull}" fill="#5A2E22"/>')
    o.append(f'<path d="M {stern:.1f} {wl - 9 * k:.1f} L {x + 40 * k:.1f} {wl - 8 * k:.1f} Q {bow - 10 * k:.1f} {wl - 10 * k:.1f} {bow + 8 * k:.1f} {wl - 36 * k:.1f}" stroke="#E8A048" stroke-width="{2.4 * k:.1f}" fill="none"/>')
    o.append(f'<path d="M {stern + 2 * k:.1f} {wl - 4 * k:.1f} L {x + 40 * k:.1f} {wl - 3 * k:.1f} Q {bow - 14 * k:.1f} {wl - 4 * k:.1f} {bow + 2 * k:.1f} {wl - 24 * k:.1f}" stroke="#2E7AA8" stroke-width="{2.2 * k:.1f}" fill="none"/>')
    o.append(f'<path d="M {stern + 4 * k:.1f} {wl:.1f} L {x + 34 * k:.1f} {wl + 1 * k:.1f}" stroke="#2A140E" stroke-width="{1.6 * k:.1f}" opacity="0.6"/>')
    # garlands and coloured ribbons tied to the bow post
    bx, by = bow + 9 * k, wl - 35 * k
    for j, c in enumerate(("#F2386A", "#F6C030", "#38A85A", "#F6F0E0", "#E8463A")):
        o.append(f'<path d="M {bx:.1f} {by:.1f} q {-6 * k - j * 2 * k:.1f} {6 * k:.1f} {-10 * k - j * 3 * k:.1f} {14 * k + j * 1.5 * k:.1f}" stroke="{c}" stroke-width="{1.8 * k:.1f}" fill="none" stroke-linecap="round"/>')
    o.append(dots(14, 403, (bx - 6 * k, by - 2 * k, bx + 2 * k, by + 8 * k), "#FFF2C0", r=(1 * k, 1.8 * k), opacity=(0.9, 1)))
    o.append(f'<circle cx="{bx - 2 * k:.1f}" cy="{by + 3 * k:.1f}" r="{3 * k:.1f}" fill="#F6C030"/><circle cx="{bx - 3 * k:.1f}" cy="{by + 2 * k:.1f}" r="{1.4 * k:.1f}" fill="#FFF2C0"/>')
    # canopy over the passenger benches
    o.append(f'<path d="M {x - 40 * k:.1f} {wl - 30 * k:.1f} L {x + 50 * k:.1f} {wl - 30 * k:.1f} L {x + 54 * k:.1f} {wl - 26 * k:.1f} L {x - 44 * k:.1f} {wl - 26 * k:.1f} Z" fill="#2E6AA0"/>'
             f'<rect x="{x - 40 * k:.1f}" y="{wl - 30 * k:.1f}" width="{90 * k:.1f}" height="{1.2 * k:.1f}" fill="#8ED0F0"/>')
    for px in (-36, 46):
        o.append(rect(x + px * k, wl - 26 * k, 1.4 * k, 18 * k, "#3A2018"))
    for px, col in ((-22, "#F6F0E0"), (-6, "#E8463A"), (12, "#F6C030"), (28, "#2E4A7A")):  # passengers
        o.append(f'<path d="M {x + px * k - 4 * k:.1f} {wl - 8 * k:.1f} Q {x + px * k:.1f} {wl - 20 * k:.1f} {x + px * k + 4 * k:.1f} {wl - 8 * k:.1f} Z" fill="{col}"/>'
                 f'<circle cx="{x + px * k:.1f}" cy="{wl - 21 * k:.1f}" r="{2.8 * k:.1f}" fill="#3A2420"/>')
    # boatman at the stern, engine on its pivot, the long shaft into the water
    sx = stern + 14 * k
    o.append(f'<path d="M {sx - 4 * k:.1f} {wl - 8 * k:.1f} L {sx - 3 * k:.1f} {wl - 28 * k:.1f} L {sx + 3 * k:.1f} {wl - 28 * k:.1f} L {sx + 4 * k:.1f} {wl - 8 * k:.1f} Z" fill="#2A2A3A"/>'
             f'<path d="M {sx - 4 * k:.1f} {wl - 28 * k:.1f} Q {sx:.1f} {wl - 32 * k:.1f} {sx + 4 * k:.1f} {wl - 28 * k:.1f} L {sx + 4 * k:.1f} {wl - 42 * k:.1f} L {sx - 4 * k:.1f} {wl - 42 * k:.1f} Z" fill="#E86A2A"/>'
             f'<circle cx="{sx:.1f}" cy="{wl - 46 * k:.1f}" r="{3.6 * k:.1f}" fill="#3A2420"/>'
             f'<path d="M {sx - 7 * k:.1f} {wl - 47 * k:.1f} L {sx + 7 * k:.1f} {wl - 47 * k:.1f} L {sx:.1f} {wl - 53 * k:.1f} Z" fill="#E8D294"/>'
             f'<path d="M {sx + 3 * k:.1f} {wl - 36 * k:.1f} L {sx - 10 * k:.1f} {wl - 22 * k:.1f}" stroke="#E86A2A" stroke-width="{2.4 * k:.1f}" stroke-linecap="round"/>')
    ex, ey = stern + 2 * k, wl - 16 * k
    o.append(rect(ex - 9 * k, ey - 7 * k, 16 * k, 10 * k, "#8A8E96") + rect(ex - 9 * k, ey - 7 * k, 16 * k, 2 * k, "#D8DCE2"))
    o.append(f'<line x1="{ex - 12 * k:.1f}" y1="{ey - 4 * k:.1f}" x2="{stern - 70 * k:.1f}" y2="{wl + 6 * k:.1f}" stroke="#4A4E56" stroke-width="{2.2 * k:.1f}" stroke-linecap="round"/>')
    # rooster tail: a fan of spray thrown up and back by the propeller
    rx, ry = stern - 70 * k, wl + 5 * k
    rnd = random.Random(407)
    fan = []
    for i in range(16):
        a = math.radians(rnd.uniform(118, 160))
        L = rnd.uniform(20, 46) * k
        ex, ey = rx + L * math.cos(a), ry - L * math.sin(a)
        fan.append(f'<path d="M {rx:.1f} {ry:.1f} Q {rx + L * 0.5 * math.cos(a) + 4 * k:.1f} {ry - L * 0.7 * math.sin(a) - 6 * k:.1f} {ex:.1f} {ey + 6 * k:.1f}" stroke-width="{rnd.uniform(1.2, 3.2) * k:.1f}" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    o.append(f'<g fill="none" stroke="#FFFFFF" stroke-linecap="round">{"".join(fan)}</g>')
    o.append(dots(60, 406, (rx - 52 * k, ry - 44 * k, rx + 4 * k, ry), "#FFFFFF", r=(0.8, 2.2), opacity=(0.5, 1)))
    o.append(f'<ellipse cx="{rx - 6 * k:.1f}" cy="{ry:.1f}" rx="{20 * k:.1f}" ry="{3 * k:.1f}" fill="#FFFFFF" opacity="0.7"/>')
    return "".join(o)


def bangkok():
    u = "bkk"
    hz = 300
    out = [defs(
        lg(f"{u}-sky", [(0, "#2E5E8E"), (0.35, "#6A90AE"), (0.62, "#E0B48A"), (0.85, "#F6CC8A"), (1, "#FBE2A8")], 0, 40, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-river", [(0, "#F2C88A"), (0.25, "#C89A6E"), (0.6, "#6E7A7A"), (1, "#3E5458")], 0, hz, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-gold", [(0, "#FFE9A0"), (0.3, "#F2C050"), (0.65, "#C8902E"), (1, "#7A4A18")], 0, 0, 1, 0),
        lg(f"{u}-tile", [(0, "#F08A3A"), (1, "#C8582A")], 0, 0, 0, 1),
        lg(f"{u}-haze", [(0, "#FBE2A8", 0), (1, "#F6D6A0", 0.85)], 0, 220, 0, 300, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="{hz + 4}" fill="url(#{u}-sky)"/>')
    out.append(glow(70, 238, 300, "#FFE2A0", f"{u}-g1", 0.8))
    out.append(glow(70, 240, 60, "#FFF6DC", f"{u}-g2", 0.95))
    out.append('<circle cx="70" cy="242" r="16" fill="#FFF6E0"/>')
    for x, y, w, c in ((150, 120, 110, "#F2C0A0"), (110, 134, 60, "#F8D2B0"), (470, 98, 110, "#E8B0A0"), (540, 112, 60, "#F2C2AE"), (300, 170, 80, "#FAD8B4"), (480, 196, 70, "#FCE0BC")):
        out.append(streak_cloud(x, y, w, c, 0.6, 4))
        out.append(streak_cloud(x - w * 0.2, y + 2.6, w * 0.5, "#FFF0D8", 0.6, 1.4))
    # the far city: pale towers in the haze, downstream
    rnd = random.Random(5)
    for x in (360, 384, 404, 500, 522, 548, 572, 596):
        h = rnd.uniform(40, 110)
        w = rnd.uniform(12, 22)
        out.append(rect(x, hz - h, w, h, "#D8B8A8", ' opacity="0.7"'))
        out.append(rect(x + w * 0.65, hz - h, w * 0.35, h, "#C0A0A0", ' opacity="0.5"'))
    out.append(f'<rect x="0" y="220" width="600" height="84" fill="url(#{u}-haze)"/>')
    # trees of the temple grounds
    for i, (x, y, rx, ry) in enumerate(((40, 276, 50, 24), (360, 282, 40, 18), (560, 272, 56, 28), (500, 286, 40, 16))):
        out.append(leaf_canopy(f"{u}-t{i}", x, y, rx, ry, 30 + i, "#3E4E36", "#5E6E44", "#C8B060", light=(-1, -1), n=40))
    for x, h in ((348, 90), (528, 110), (16, 80)):
        out.append(coconut(x, 300, h, 0.06 if x > 300 else -0.05, x, trunk="#6A5A44", trunk_lit="#E8B878", dark="#2E4030", mid="#4E6A3E", lit="#C8B860", light=-1, nuts=False))
    # a small prang and the golden chedi, then the ordination hall
    out.append(bell_chedi(456, 298, 0.93, u))
    out.append(thai_hall(206, 300, 0.92, u))
    # riverside: white wall with the boundary-stone sema niches, a sala pavilion on the landing
    out.append(rect(-10, 296, 620, 14, "#F2E4CE"))
    out.append(rect(-10, 296, 620, 2, "#FFF6E6"))
    out.append(rect(-10, 306, 620, 4, "#B89A88", ' opacity="0.6"'))
    out.append("".join(f'<path d="M {x:.1f} 296 l 3 -6 l 3 6 Z" fill="#F2E4CE"/>' for x in range(-6, 610, 14)))
    sx = 394
    out.append(rect(sx - 26, 284, 52, 3, "#C89838") + rect(sx - 22, 287, 3, 20, "#F4E6D0") + rect(sx + 19, 287, 3, 20, "#F4E6D0"))
    out.append(Q([(sx - 34, 286), (sx - 14, 268), (sx + 14, 268), (sx + 34, 286)], f"url(#{u}-tile)"))
    out.append(Q([(sx - 34, 284), (sx + 34, 284), (sx + 34, 287), (sx - 34, 287)], "#2E7A4E"))
    out.append(Q([(sx - 12, 270), (sx, 254), (sx + 12, 270)], "#A8282E") + f'<path d="M {sx - 12} 270 L {sx} 254 L {sx + 12} 270" stroke="#F2C858" stroke-width="2" fill="none"/>')
    out.append(f'<path d="M {sx - 1} 256 q 0 -6 4 -9" stroke="#F2C858" stroke-width="1.8" fill="none"/>')
    out.append(rect(sx - 40, 306, 80, 6, "#8A6A54"))
    for j in range(5):
        out.append(rect(sx - 38 + j * 19, 306, 2, 14, "#5A4234"))
    # the river: sky colours, golden column under the sun, reflections of the gilded temple
    out.append(rect(-10, 310, 620, 140, f"url(#{u}-river)"))
    out.append(f'<g opacity="0.5">{ripple_reflection(90, 51, 452, 312, 400, 60, ["#FFE08A", "#F2C050", "#FFF2C0"], op=(0.4, 0.9), spread=0.6)}'
               f'{ripple_reflection(110, 52, 212, 312, 390, 150, ["#F2C050", "#F08A3A", "#FFE6A0", "#F4E6D0"], op=(0.3, 0.8), spread=0.3)}</g>')
    out.append(ripple_reflection(80, 53, 76, 312, 440, 50, ["#FFF6DC", "#FFE2A0"], op=(0.5, 1), spread=1.2))
    out.append(water_lines(160, 54, (-10, 314, 610, 444), ["#FFE2B0", "#4A5E62", "#F2C88A", "#2E4246"], w=(10, 50), h=(1, 2.2), opacity=(0.2, 0.6)))
    # clumps of water hyacinth drifting downstream
    for i, (x, y, r) in enumerate(((520, 330, 12), (556, 338, 8), (90, 350, 10), (470, 420, 16), (30, 412, 14))):
        out.append(f'<ellipse cx="{x}" cy="{y + r * 0.2:.1f}" rx="{r * 1.6:.1f}" ry="{r * 0.35:.1f}" fill="#2E4632"/>')
        out.append(leaf_canopy(f"{u}-hy{i}", x, y - r * 0.1, r * 1.4, r * 0.45, 60 + i, "#2E5A36", "#4E8A44", "#9AC060", light=(-1, -1), n=14, r=(0.3, 0.5)))
        out.append(dots(3, 70 + i, (x - r, y - r * 0.5, x + r, y), "#C8A8E8", r=(1.2, 2), opacity=(0.9, 1)))
    out.append(longtail(318, 394, 1.24, u))
    out.append(flock([(250, 110, 9), (268, 120, 7), (530, 150, 7)], "#4A3A4E", 1.8))
    return "\n".join(out)


# ================================================================ HONG KONG — Victoria Harbour at night, a red-sailed junk
def junk_sail(mx, foot, top, fw, aw, k, u, fill, batten="#5A1414", rake=0.0):
    """Chinese battened lug sail on mast mx: luff a little forward (fw) of the mast, leech aft (aw), scalloped
    between full-length battens that fan slightly upward toward the yard. foot/top = y of boom and yard at the mast."""
    n = 7
    pts_l, pts_r = [], []
    for i in range(n + 1):
        t = i / n
        y = lerp(foot, top, t)
        yr = y - t * aw * 0.22 - (1 - t) * 2 * k   # battens rise toward the leech, the yard most
        xl = mx - fw * (0.7 + 0.3 * t) + rake * (foot - y)
        xr = mx + aw * (1 - 0.18 * t * t) + rake * (foot - y)
        pts_l.append((xl, y))
        pts_r.append((xr, yr))
    # scalloped leech: bulge outward between battens
    leech = f"M {pts_l[0][0]:.1f} {pts_l[0][1]:.1f} L {pts_r[0][0]:.1f} {pts_r[0][1]:.1f} "
    for (x1, y1), (x2, y2) in zip(pts_r, pts_r[1:]):
        leech += f"Q {max(x1, x2) + 7 * k:.1f} {(y1 + y2) / 2:.1f} {x2:.1f} {y2:.1f} "
    d = leech + " ".join(f"L {x:.1f} {y:.1f}" for x, y in pts_l[::-1]) + " Z"
    o = [f'<path d="{d}" fill="{fill}"/>']
    o.append(f'<clipPath id="{u}"><path d="{d}"/></clipPath><g clip-path="url(#{u})">'
             f'<rect x="{mx - fw - 10:.1f}" y="{top - 30:.1f}" width="{(fw + aw) * 0.32:.1f}" height="{foot - top + 40:.1f}" fill="#FF9A6A" opacity="0.25"/>'
             f'<ellipse cx="{mx + aw * 0.3:.1f}" cy="{foot:.1f}" rx="{aw * 0.9:.1f}" ry="{(foot - top) * 0.45:.1f}" fill="#FFB070" opacity="0.4"/></g>')
    o.append(f'<g stroke="{batten}" stroke-width="{1.6 * k:.1f}" stroke-linecap="round">' + "".join(
        f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>' for a, b in zip(pts_l, pts_r)) + "</g>")
    # sheets: fan of lines from the batten ends down to the stern
    return "".join(o), pts_r


def junk(x, wl, k, u, sail="url(#hkg-sail)"):
    """Three-masted junk under sail, broadside, bow to the right; deck lanterns glowing."""
    o = []
    L = 92 * k
    # reflection of the sails, broken by the swell
    o.append(f'<g opacity="0.35">' + ripple_reflection(60, 801, x, wl + 4, wl + 70 * k, 70 * k, ["#E8463A", "#FF8A5A", "#B8282A"], op=(0.4, 0.9), spread=0.2) + "</g>")
    o.append(ripple_reflection(24, 802, x, wl + 4, wl + 40 * k, 30 * k, ["#FFD08A", "#FFE6B0"], op=(0.5, 1), spread=0.6))
    # masts
    masts = ((x - 10 * k, 120 * k, 50 * k, 40 * k, 0.02), (x + 40 * k, 96 * k, 34 * k, 28 * k, -0.08), (x - 66 * k, 64 * k, 22 * k, 18 * k, 0.04))
    sails = []
    for i, (mx, H, aw, fw, rake) in enumerate(masts):
        foot = wl - 24 * k
        top = wl - H
        o.append(f'<line x1="{mx:.1f}" y1="{wl - 10 * k:.1f}" x2="{mx + rake * H:.1f}" y2="{top - 8 * k:.1f}" stroke="#2A1612" stroke-width="{2 * k:.1f}"/>')
        s_, pr = junk_sail(mx, foot, top, fw if i != 1 else aw * 0.8, aw if i != 1 else fw, k, f"{u}-js{i}", sail, rake=rake)
        sails.append(s_)
        # pennant
        o.append(f'<path d="M {mx + rake * H:.1f} {top - 8 * k:.1f} l {9 * k:.1f} {2 * k:.1f} l {-9 * k:.1f} {2 * k:.1f} Z" fill="#F2C040"/>')
    o += sails
    # hull: low sheer rising to a tall transom stern on the left
    hull = (f"M {x - L:.1f} {wl - 30 * k:.1f} L {x - L + 14 * k:.1f} {wl - 30 * k:.1f} Q {x - L + 22 * k:.1f} {wl - 16 * k:.1f} {x - 40 * k:.1f} {wl - 16 * k:.1f} "
            f"L {x + L - 20 * k:.1f} {wl - 18 * k:.1f} Q {x + L - 4 * k:.1f} {wl - 20 * k:.1f} {x + L + 6 * k:.1f} {wl - 26 * k:.1f} L {x + L:.1f} {wl - 12 * k:.1f} "
            f"Q {x + L - 20 * k:.1f} {wl + 2 * k:.1f} {x:.1f} {wl + 2 * k:.1f} Q {x - L + 10 * k:.1f} {wl + 2 * k:.1f} {x - L - 2 * k:.1f} {wl - 10 * k:.1f} Z")
    o.append(f'<path d="{hull}" fill="#3A1E18"/>')
    o.append(f'<path d="M {x - L + 6 * k:.1f} {wl - 9 * k:.1f} Q {x:.1f} {wl - 4 * k:.1f} {x + L - 4 * k:.1f} {wl - 10 * k:.1f}" stroke="#8A3A22" stroke-width="{2.4 * k:.1f}" fill="none"/>')
    o.append(f'<path d="M {x - L + 14 * k:.1f} {wl - 30 * k:.1f} Q {x - L + 22 * k:.1f} {wl - 16 * k:.1f} {x - 40 * k:.1f} {wl - 16 * k:.1f} L {x + L - 20 * k:.1f} {wl - 18 * k:.1f} Q {x + L - 4 * k:.1f} {wl - 20 * k:.1f} {x + L + 6 * k:.1f} {wl - 26 * k:.1f}" stroke="#E8A060" stroke-width="{1.4 * k:.1f}" fill="none"/>')
    # stern windows and a painted eye on the bow
    o.append("".join(rect(x - L + 3 * k + j * 5 * k, wl - 26 * k, 3 * k, 4 * k, "#FFD08A") for j in range(3)))
    o.append(f'<circle cx="{x + L - 10 * k:.1f}" cy="{wl - 12 * k:.1f}" r="{2.6 * k:.1f}" fill="#F4F0E6"/><circle cx="{x + L - 9.4 * k:.1f}" cy="{wl - 12 * k:.1f}" r="{1.2 * k:.1f}" fill="#1E1E1E"/>')
    # deck lanterns and their glow
    for j, lx in enumerate((-50, -20, 10, 40, 64)):
        gx_ = x + lx * k
        o.append(glow(gx_, wl - 21 * k, 12 * k, "#FFC070", f"{u}-jl{j}", 0.9))
        o.append(f'<ellipse cx="{gx_:.1f}" cy="{wl - 21 * k:.1f}" rx="{2.2 * k:.1f}" ry="{2.8 * k:.1f}" fill="#FF6A3A"/><ellipse cx="{gx_ - 0.6 * k:.1f}" cy="{wl - 21.6 * k:.1f}" rx="{0.9 * k:.1f}" ry="{1.4 * k:.1f}" fill="#FFE6A0"/>')
    # bow wave
    o.append(f'<ellipse cx="{x + L - 6 * k:.1f}" cy="{wl - 1 * k:.1f}" rx="{14 * k:.1f}" ry="{1.6 * k:.1f}" fill="#E8E6F6" opacity="0.55"/>')
    return "".join(o)


def hk_tower(x, base, w, h, style, seed, body, edge=None, lit_p=0.55, u="hk"):
    """Generic Hong Kong high-rise at night: body shade, window grid, crown variants, optional LED edge strip."""
    rnd = random.Random(seed)
    top = base - h
    o = []
    if style == "spire":
        o.append(f'<line x1="{x + w / 2:.1f}" y1="{top:.1f}" x2="{x + w / 2:.1f}" y2="{top - h * 0.18:.1f}" stroke="{body}" stroke-width="2"/>'
                 f'<circle cx="{x + w / 2:.1f}" cy="{top - h * 0.18:.1f}" r="1.8" fill="#FF4A4A"/>')
    if style == "stepped":
        o.append(rect(x + w * 0.18, top - h * 0.08, w * 0.64, h * 0.08, body) + rect(x + w * 0.34, top - h * 0.14, w * 0.32, h * 0.06, body))
    if style == "slant":
        o.append(Q([(x, top), (x + w, top - h * 0.12), (x + w, top)], body))
    if style == "round":
        o.append(f'<path d="M {x:.1f} {top:.1f} Q {x + w / 2:.1f} {top - w * 0.7:.1f} {x + w:.1f} {top:.1f} Z" fill="{body}"/>')
    o.append(rect(x, top, w, h, body))
    o.append(rect(x + w * 0.62, top, w * 0.38, h, "#000010", ' opacity="0.25"'))
    cols = max(2, int(w / 4.2))
    rows = max(3, int(h / 4.6))
    o.append(win_grid(x + 1, top + 3, w - 2, h - 3, cols, rows, seed, lit_p=lit_p, lit=("#FFE6B0", "#FFF4D8", "#CDE8FF", "#FFD08A"), dark=mix(body, "#000000", 0.25), ww=0.55, wh=0.45))
    if edge:
        o.append(rect(x, top, 1.4, h, edge, ' opacity="0.9"') + rect(x, top, w, 1.4, edge, ' opacity="0.9"'))
    return "".join(o)


def hong_kong():
    u = "hkg"
    hz = 318
    out = [defs(
        lg(f"{u}-sky", [(0, "#0A0E2A"), (0.45, "#1E1E52"), (0.75, "#4A2A6A"), (0.92, "#8A3A72"), (1, "#C25A7A")], 0, 40, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#2A1E4A"), (0.4, "#141A3A"), (1, "#080C20")], 0, hz, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-peak", [(0, "#1A2440"), (1, "#2A2A52")], 0, 120, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-sail", [(0, "#A81E22"), (0.6, "#D8382E"), (1, "#F2683A")], 0, 0, 0, 1),
    )]
    out.append(f'<rect width="600" height="{hz + 4}" fill="url(#{u}-sky)"/>')
    out.append(dots(80, 3, (0, 40, 600, 170), "#FFFFFF", r=(0.5, 1.3), opacity=(0.4, 1)))
    # a crescent moon over the Peak
    out.append(glow(470, 88, 60, "#E8E0FF", f"{u}-mg", 0.4))
    out.append('<path d="M 476 76 A 13 13 0 1 0 482 98 A 11 11 0 1 1 476 76 Z" fill="#FFF6E2"/>')
    # Victoria Peak and its ridges, with lit roads and homes climbing the Mid-Levels
    poly, pk = ridge_poly([(-10, 196), (60, 170), (150, 146), (230, 128), (300, 136), (380, 154), (470, 176), (540, 168), (610, 186)], 31, amp=7, fill=f"url(#{u}-peak)")
    out.append(poly)
    out.append(f'<polyline points="{P(pk)}" fill="none" stroke="#5A4A8A" stroke-width="1.4" opacity="0.7"/>')
    rnd = random.Random(32)
    lights = []
    for _ in range(170):
        x = rnd.uniform(0, 600)
        y0 = y_on(pk, x) or 200
        y = rnd.uniform(y0 + 8, 300)
        lights.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 1.3):.1f}" fill="{rnd.choice(["#FFE6B0", "#FFD08A", "#FFFFFF"])}" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    out.append("".join(lights))
    # the tram station on the summit: a small lit lantern-shaped building
    out.append(rect(214, 124, 22, 7, "#2A2A52") + rect(216, 125, 18, 2.4, "#FFD08A") + Q([(210, 125), (225, 118), (240, 125)], "#2A2A52"))
    out.append(mist(300, 290, 420, 50, "#C25A9A", f"{u}-cg", 0.55))
    # back row of towers (paler, hazier)
    rnd = random.Random(40)
    x = -10
    while x < 610:
        w = rnd.uniform(14, 26)
        h = rnd.uniform(40, 86)
        out.append(hk_tower(x, hz, w, h, rnd.choice(["flat", "flat", "stepped", "slant"]), int(x * 3 + 1), "#3A3466", lit_p=0.3))
        x += w + rnd.uniform(-2, 4)
    out.append(f'<rect x="0" y="230" width="600" height="90" fill="#6A3A7A" opacity="0.18"/>')
    # front row: the waterfront towers, the tallest just right of centre
    front = [(-6, 30, 120, "flat", None), (28, 24, 150, "stepped", None), (56, 30, 104, "slant", "#4AD8F0"), (92, 22, 132, "round", None),
             (118, 34, 92, "flat", None), (156, 26, 166, "spire", None), (186, 30, 118, "stepped", "#FF5AA8"), (220, 22, 98, "flat", None),
             (246, 36, 200, "stepped", None), (286, 26, 140, "slant", None), (316, 30, 112, "flat", "#4AD8F0"), (350, 24, 176, "spire", None),
             (378, 32, 124, "round", None), (414, 26, 150, "stepped", "#FFC04A"), (444, 30, 104, "flat", None), (478, 24, 138, "slant", "#FF5AA8"),
             (506, 34, 116, "flat", None), (544, 28, 160, "stepped", None), (576, 34, 108, "flat", None)]
    cols = ["#26285A", "#2E2A62", "#22305E", "#30285A", "#1E2650"]
    front = [(x, w, h * 0.78, st, edge) for x, w, h, st, edge in front]
    for i, (x, w, h, st, edge) in enumerate(front):
        out.append(hk_tower(x, hz, w, h, st, 100 + i, cols[i % len(cols)], edge=edge, lit_p=0.42))
    # the tallest tower: tiered, with crown lighting
    T = hz - 156
    out.append(rect(252, T - 14, 24, 14, "#2A2C66") + rect(258, T - 25, 12, 11, "#2A2C66") + rect(263, T - 42, 2, 17, "#2A2C66"))
    out.append(rect(252, T - 14, 24, 2, "#9AE8FF") + rect(258, T - 25, 12, 1.6, "#9AE8FF") + f'<circle cx="264" cy="{T - 42}" r="2" fill="#FF4A4A"/>')
    # the nightly light show: a few beams from the rooftops
    for x0, y0, x1, c in ((264, T - 14, 150, "#7AE0FF"), (264, T - 14, 330, "#C88AFF"), (414, hz - 117, 380, "#7AE0FF"), (160, hz - 130, 60, "#FF8AD8")):
        out.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="40" stroke="{c}" stroke-width="1.6" opacity="0.3"/>')
    # waterfront promenade and its lights
    out.append(rect(-10, hz, 620, 6, "#1A1838"))
    out.append(dots(60, 41, (-10, hz + 1, 610, hz + 4), "#FFE6B0", r=(0.8, 1.5), opacity=(0.7, 1)))
    # harbour: long broken reflections of every lit tower
    out.append(rect(-10, hz + 6, 620, 130, f"url(#{u}-sea)"))
    refl = []
    for i, (x, w, h, st, edge) in enumerate(front):
        cs = ["#FFE6B0", "#FFD08A", "#CDE8FF"] + ([edge] * 2 if edge else [])
        refl.append(ripple_reflection(int(h / 3.5), 300 + i, x + w / 2, hz + 7, hz + 7 + h * 0.62, w * 0.9, cs, op=(0.25, 0.8), spread=0.25))
    out.append("".join(refl))
    out.append(water_lines(130, 42, (-10, hz + 8, 610, 444), ["#3A3A7A", "#6A4A9A", "#1E2050"], w=(14, 60), h=(1, 2.2), opacity=(0.3, 0.7)))
    # a harbour ferry crossing, mid-distance
    fx, fw = 470, 64
    out.append(f'<path d="M {fx:.1f} {hz + 30:.1f} L {fx + fw:.1f} {hz + 30:.1f} L {fx + fw - 6:.1f} {hz + 38:.1f} L {fx + 4:.1f} {hz + 38:.1f} Z" fill="#E8EEF2"/>'
               f'<rect x="{fx:.1f}" y="{hz + 34:.1f}" width="{fw:.1f}" height="4" fill="#2E7A4E"/>'
               f'<rect x="{fx + 8:.1f}" y="{hz + 22:.1f}" width="{fw - 16:.1f}" height="8" fill="#E8EEF2"/><rect x="{fx + 8:.1f}" y="{hz + 28:.1f}" width="{fw - 16:.1f}" height="2" fill="#2E7A4E"/>')
    out.append("".join(rect(fx + 10 + j * 6, hz + 24, 3.6, 3, "#FFE6A0") for j in range(8)))
    out.append(ripple_reflection(20, 43, fx + fw / 2, hz + 40, hz + 62, fw * 0.8, ["#FFE6A0", "#E8EEF2"], op=(0.3, 0.8)))
    out.append(junk(206, 400, 1.32, u))
    return "\n".join(out)


# ================================================================ KYOTO — the tunnel of vermilion torii at Fushimi Inari, late afternoon
def kitsune(x, base, k, flip=False):
    """Stone fox messenger of Inari seated on its plinth, a red votive bib round its neck, a jewel in its mouth."""
    sx = -k if flip else k
    return (f'<g transform="translate({x:.1f} {base:.1f}) scale({sx:.3f} {k:.3f})">'
            # plinth
            '<rect x="-34" y="-46" width="68" height="46" fill="#8E8A80"/><rect x="-34" y="-46" width="68" height="5" fill="#C8C2B4"/>'
            '<rect x="10" y="-41" width="24" height="41" fill="#5E5A52" opacity="0.5"/><rect x="-38" y="-54" width="76" height="9" fill="#A8A296"/><rect x="-38" y="-54" width="76" height="3" fill="#D8D2C4"/>'
            '<path d="M -30 -20 q 6 -4 12 0 M 4 -30 q 8 -3 14 1" stroke="#6E8A4A" stroke-width="3" fill="none" opacity="0.6"/>'
            # tail curling up behind
            '<path d="M 14 -60 Q 34 -80 26 -118 Q 22 -134 12 -138 Q 20 -116 12 -92 Q 8 -78 4 -66 Z" fill="#9A968A"/>'
            '<path d="M 26 -118 Q 22 -134 12 -138 Q 18 -124 18 -112 Z" fill="#C8C2B4"/>'
            # body seated
            '<path d="M -20 -54 Q -24 -86 -14 -112 Q -6 -128 6 -124 Q 16 -118 18 -96 Q 22 -74 20 -54 Z" fill="#A8A498"/>'
            '<path d="M 6 -124 Q 16 -118 18 -96 Q 22 -74 20 -54 L 10 -54 Q 12 -90 6 -124 Z" fill="#6E6A60" opacity="0.6"/>'
            '<path d="M -16 -54 L -14 -84 L -8 -84 L -8 -54 Z" fill="#B8B4A8"/>'
            # head, ears, snout with the jewel
            '<path d="M -12 -122 Q -16 -140 -6 -146 L -2 -160 L 4 -144 Q 8 -146 10 -144 L 16 -158 L 16 -140 Q 20 -132 14 -124 Q 4 -116 -12 -122 Z" fill="#B0AC9E"/>'
            '<path d="M -12 -132 L -28 -128 Q -30 -124 -26 -122 L -10 -122 Z" fill="#A8A498"/>'
            '<circle cx="-28" cy="-125" r="4" fill="#C8B888"/><circle cx="-29" cy="-126.5" r="1.4" fill="#F2E6C0"/>'
            '<path d="M -4 -154 L -2 -146 L 1 -150 Z M 14 -152 L 13 -144 L 10 -147 Z" fill="#6E6A60"/>'
            '<path d="M -10 -134 q 3 -2 6 0" stroke="#3E3A34" stroke-width="1.6" fill="none"/>'
            # red bib
            '<path d="M -18 -116 Q 0 -110 16 -118 L 12 -96 Q -2 -88 -16 -96 Z" fill="#D8301E"/>'
            '<path d="M -18 -116 Q 0 -110 16 -118 L 15 -113 Q 0 -106 -17 -111 Z" fill="#F26A4A"/>'
            # moss and lichen
            '<circle cx="-4" cy="-150" r="2" fill="#7E9A4E" opacity="0.7"/><circle cx="-18" cy="-70" r="3" fill="#7E9A4E" opacity="0.5"/><circle cx="12" cy="-64" r="2.4" fill="#C8C060" opacity="0.5"/>'
            # warm sunlight on its right flank
            '<path d="M 10 -150 L 16 -158 L 16 -140 Q 20 -132 14 -124 Q 16 -118 18 -96 Q 22 -74 20 -54 L 22 -54 Q 24 -76 20 -98 Q 22 -120 18 -132 Z" fill="#F2D49A" opacity="0.8"/>'
            '</g>')


def stone_lantern(x, base, k, lit=True):
    """Kasuga-style stone lantern: base, round post, platform, light box with a glowing window, curled roof, jewel finial."""
    s = k
    o = [rect(x - 22 * s, base - 10 * s, 44 * s, 10 * s, "#8A867C"), rect(x - 22 * s, base - 10 * s, 44 * s, 2.4 * s, "#C2BCB0"),
         rect(x - 7 * s, base - 62 * s, 14 * s, 52 * s, "#9A968A"), rect(x + 2 * s, base - 62 * s, 5 * s, 52 * s, "#F2D49A", ' opacity="0.6"'),
         rect(x - 20 * s, base - 72 * s, 40 * s, 10 * s, "#A29E92"), rect(x - 20 * s, base - 72 * s, 40 * s, 2.4 * s, "#D2CCC0"),
         rect(x - 15 * s, base - 98 * s, 30 * s, 26 * s, "#8E8A80")]
    if lit:
        o.append(glow(x, base - 85 * s, 26 * s, "#FFC870", "kyoto-lg", 0.7))
    o.append(rect(x - 8 * s, base - 94 * s, 16 * s, 16 * s, "#FFD890" if lit else "#3A3630"))
    o.append(f'<circle cx="{x:.1f}" cy="{base - 86 * s:.1f}" r="{4.5 * s:.1f}" fill="#8E8A80"/>')
    o.append(f'<path d="M {x - 30 * s:.1f} {base - 100 * s:.1f} Q {x - 22 * s:.1f} {base - 104 * s:.1f} {x - 8 * s:.1f} {base - 116 * s:.1f} L {x + 8 * s:.1f} {base - 116 * s:.1f} Q {x + 22 * s:.1f} {base - 104 * s:.1f} {x + 30 * s:.1f} {base - 100 * s:.1f} '
             f'Q {x + 33 * s:.1f} {base - 104 * s:.1f} {x + 32 * s:.1f} {base - 98 * s:.1f} L {x - 32 * s:.1f} {base - 98 * s:.1f} Q {x - 33 * s:.1f} {base - 104 * s:.1f} {x - 30 * s:.1f} {base - 100 * s:.1f} Z" fill="#9A968A"/>')
    o.append(f'<path d="M {x + 8 * s:.1f} {base - 116 * s:.1f} Q {x + 22 * s:.1f} {base - 104 * s:.1f} {x + 30 * s:.1f} {base - 100 * s:.1f} L {x + 32 * s:.1f} {base - 98 * s:.1f} L {x + 6 * s:.1f} {base - 98 * s:.1f} Z" fill="#F2D49A" opacity="0.55"/>')
    o.append(f'<circle cx="{x:.1f}" cy="{base - 121 * s:.1f}" r="{5.5 * s:.1f}" fill="#A29E92"/><path d="M {x:.1f} {base - 132 * s:.1f} q {4 * s:.1f} {5 * s:.1f} 0 {7 * s:.1f} q {-4 * s:.1f} {-2 * s:.1f} 0 {-7 * s:.1f} Z" fill="#A29E92"/>')
    o.append(blobs(10, int(x), (x - 20 * s, base - 100 * s, x + 20 * s, base - 4 * s), ["#6E8A4A", "#9AAA5A"], r=(1 * s, 3 * s), opacity=(0.4, 0.8)))
    return "".join(o)


def yukata_visitor(x, base, h, u, light=1, rim="#FFD8A0", seed=5, robe="#2E4A8A", obi="#F2B83A", tint=None):
    """A woman in a summer yukata walking away from us (back view), built on the figures.py skeleton: bun with a
    hairpin, wide hanging sleeves, an ankle-length robe with a morning-glory print, a folded obi bow on her back,
    white tabi socks on wooden geta, a small drawstring bag swinging from one hand."""
    from figures import Painter, _palette, _render, mix as fmix, pose_joints, tube_side
    k = h / 100.0
    pal = _palette({"form": "f", "top_kind": "long", "bottom_kind": "trousers", "hair_style": "bun", "skin": "#EDBE98",
                    "hair": "#1C1412", "top": robe, "bottom": robe, "shoes": "#F6F1E8"}, seed)
    J = pose_joints("stand_back", "f", random.Random(seed))
    # mid-stride, seen from behind: the trailing foot lifts its heel, arms swing a little
    J["legs"] = [([(-4.4, -49), (-4.0, -27), (-3.4, -8.0)], None, "front"), ([(4.4, -49), (4.3, -26), (3.9, -3.6)], None, "front")]
    J["arms"] = [("L", [(-7.6, -79.2), (-11.0, -64.5), (-9.0, -51.5)], "front"), ("R", [(7.6, -79.2), (11.4, -64), (12.6, -51)], "front")]
    sh, dk_, lt_ = robe, fmix(robe, "#14102A", 0.38), fmix(robe, "#FFE8C8", 0.3)
    B = Painter(k, light, rim, tint, 2)
    # geta under the feet, drawn first so the robe hem and socks sit on them
    for fx, fy in ((-3.4, -4.6), (3.9, 0.0)):
        B.shape([(fx - 3.2, fy), (fx + 3.2, fy), (fx + 3.2, fy + 1.6), (fx - 3.2, fy + 1.6)], "#B8865A", smooth=False)
        B.shape([(fx - 3.2, fy + 1.6), (fx + 3.2, fy + 1.6), (fx + 3.0, fy + 2.6), (fx - 3.0, fy + 2.6)], "#5A3A24", smooth=False)
    _render(B, dict(J, arms=[]), pal, False, "stand_back")
    # the robe: straight and narrow, falling from the shoulders to the ankles
    robe_pts = [(-9.6, -79), (9.6, -79), (10.4, -64), (10.2, -50), (9.6, -26), (8.8, -7.2), (0.5, -6.4), (-8.8, -7.8), (-9.4, -26), (-10.0, -50), (-10.2, -64)]
    B.fill(robe_pts, robe, smooth=False)
    B.shape(tube_side([(0, -79), (0, -7)], [19.6, 17.8], B.L, 0.36, cap1=False), dk_)
    B.shape(tube_side([(0, -79), (0, -7)], [19.6, 17.8], B.L, 0.1, lit=True, cap1=False), lt_, op=0.7)
    # morning-glory print, clipped to the robe
    rnd = random.Random(seed * 3 + 1)
    clip = f'{u}-yk{seed}'
    motifs = []
    for j in range(34):
        mx, my = rnd.uniform(-10, 10) if j < 26 else rnd.choice((-1, 1)) * rnd.uniform(9, 15), rnd.uniform(-78, -8) if j < 26 else rnd.uniform(-78, -56)
        r = rnd.uniform(1.3, 2.1)
        motifs.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{r:.2f}" fill="#F4F0FA" opacity="0.85"/>'
                      f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{r * 0.42:.2f}" fill="#8EB4E8"/>'
                      f'<path d="M {mx + r:.1f} {my + r * 0.4:.1f} q {r:.1f} {r * 0.2:.1f} {r * 1.4:.1f} {r * 1.3:.1f}" stroke="#8EB4E8" stroke-width="0.6" fill="none"/>')
    B.add(f'<clipPath id="{clip}"><polygon points="{P(robe_pts)}"/></clipPath><g clip-path="url(#{clip})">{"".join(motifs)}</g>')
    # centre-back seam and the hem's turned edge
    B.add(f'<path d="M 0 -78 L 0.4 -7" stroke="{dk_}" stroke-width="0.7" opacity="0.6"/><path d="M -8.8 -7.8 L 0.5 -6.4 L 8.8 -7.2" stroke="{lt_}" stroke-width="0.8" fill="none" opacity="0.8"/>')
    # obi with a folded bunko bow
    o_dk, o_lt = fmix(obi, "#5A2A14", 0.35), fmix(obi, "#FFF6DC", 0.4)
    B.fill([(-10.4, -67.5), (10.4, -67.5), (10.3, -57.5), (-10.3, -57.5)], obi, smooth=False)
    B.shape([(-10.4, -60.5), (10.3, -60.5), (10.3, -57.5), (-10.3, -57.5)], o_dk, smooth=False)
    B.shape([(-10.4, -67.5), (10.4, -67.5), (10.4, -66.6), (-10.4, -66.6)], "#D8302A", smooth=False)
    # the bunko bow: two broad pleated wings, a cinched knot and two short folded loops hanging below
    for s in (-1, 1):
        wing = [(s * 1.8, -70.5), (s * 6.4, -72.2), (s * 11.6, -71.6), (s * 12.4, -66.4), (s * 11.6, -61.4), (s * 6.4, -61.0), (s * 1.8, -63.0)]
        B.fill(wing, obi)
        B.shape([(s * 1.8, -64.6), (s * 6.4, -63.6), (s * 12.1, -63.8), (s * 11.6, -61.4), (s * 6.4, -61.0), (s * 1.8, -63.0)], o_dk, op=0.85)
        B.add(f'<path d="M {s * 3:.1f} -68.2 Q {s * 7:.1f} -69.6 {s * 11.2:.1f} -68.6 M {s * 3:.1f} -66.0 Q {s * 7:.1f} -66.6 {s * 11.8:.1f} -66.2" stroke="{o_dk}" stroke-width="0.6" fill="none" opacity="0.8"/>')
        B.add(f'<path d="M {s * 2:.1f} -70.3 Q {s * 6.4:.1f} -71.9 {s * 11.4:.1f} -71.3" stroke="{o_lt}" stroke-width="0.8" fill="none" opacity="0.9"/>')
    for s in (-1, 1):
        loop = [(s * 0.6, -62.5), (s * 5.6, -61.5), (s * 6.4, -51.5), (s * 3.4, -50.2), (s * 0.4, -51.8)]
        B.fill(loop, obi)
        B.shape([(s * 3.6, -61.8), (s * 5.6, -61.5), (s * 6.4, -51.5), (s * 3.4, -50.2)], o_dk if s * light < 0 else o_lt, op=0.7)
    B.fill([(-2.6, -71.2), (2.6, -71.2), (2.2, -61.6), (-2.2, -61.6)], obi)
    B.shape([(-2.6, -71.2), (-0.6, -71.2), (-0.6, -61.6), (-2.2, -61.6)], o_dk, op=0.8)
    B.add(f'<path d="M -1.8 -69 L 1.8 -69 M -1.6 -66.4 L 1.6 -66.4 M -1.6 -63.8 L 1.6 -63.8" stroke="{o_dk}" stroke-width="0.5"/>')
    # arms, then the wide hanging sleeves over the upper arms
    A = Painter(k, light, rim, tint, 2)
    _render(A, dict(J, legs=[]), pal, False, "stand_back", parts="arms")
    for s in (-1, 1):
        # a straight tamoto hanging from the arm, a little longer at the back, the forearm emerging at its mouth
        sl = [(s * 7.4, -80.6), (s * 11.8, -79.8), (s * 15.0, -72), (s * 15.4, -58.5), (s * 14.2, -55.2), (s * 10.4, -55.0), (s * 8.8, -58), (s * 8.6, -72)]
        A.fill(sl, robe)
        A.shape([(s * 12.6, -74), (s * 15.0, -72), (s * 15.4, -58.5), (s * 14.2, -55.2), (s * 12.4, -55.1)], dk_ if s * light < 0 else lt_, op=0.65)
        A.add(f'<path d="M {s * 9.4:.1f} -71 Q {s * 9.2:.1f} -64 {s * 9.8:.1f} -57" stroke="{dk_}" stroke-width="0.7" fill="none" opacity="0.8"/>')
        A.add(f'<clipPath id="{clip}s{s + 1}"><polygon points="{P(sl)}"/></clipPath><g clip-path="url(#{clip}s{s + 1})">'
              + "".join(motifs[22:]) + "</g>")
    # drawstring bag swinging from the left hand
    A.fill([(-12.2, -49.2), (-7.2, -49.4), (-6.6, -42.5), (-9.6, -41.6), (-12.8, -42.8)], "#C8302A")
    A.shape([(-12.2, -49.2), (-10.6, -49.2), (-11.2, -42), (-12.8, -42.8)], "#8A1E1A")
    A.add('<path d="M -11.8 -47.8 L -7.6 -48" stroke="#F2C24A" stroke-width="0.7"/>')
    # a hairpin with a small flower in the bun
    hx, hy = J["head"]
    A.add(f'<path d="M {hx - 2:.1f} {hy - 10.5:.1f} L {hx + 6:.1f} {hy - 6:.1f}" stroke="#E8D29A" stroke-width="0.9"/>'
          f'<circle cx="{hx + 5.5:.1f}" cy="{hy - 6.5:.1f}" r="1.7" fill="#F26A8A"/><circle cx="{hx + 5.5:.1f}" cy="{hy - 6.5:.1f}" r="0.6" fill="#FFF0C8"/>')
    shadow = f'<ellipse cx="{-light * 3:.1f}" cy="0.8" rx="15" ry="2.6" fill="#140C1A" opacity="0.3"/>'
    return (f'<g transform="translate({x:.1f} {base:.1f}) scale({k:.4f})">' + shadow + "".join(B.out) + "".join(A.out) + "</g>")


def kyoto():
    u = "kyoto"
    C = Cam(f=360, cx=300, vpy=312, eye=1.5)
    Z0, Z1, dz = 2.6, 26.0, 0.56
    HW, PW, TOP = 0.78, 0.13, 2.9   # half path width to pillar centre, pillar half-thickness, kasagi height

    def axis(Z):  # the path curves gently right and climbs
        t = Z - Z0
        return 0.0045 * t * t, 0.075 * t

    out = [defs(
        lg(f"{u}-sky", [(0, "#F6E6A8"), (1, "#C8D88A")], 0, 0, 0, 1),
        lg(f"{u}-for", [(0, "#2E4A2A"), (0.6, "#1E3420"), (1, "#14241A")], 0, 40, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-pil", [(0, "#A8301E"), (0.35, "#E8542C"), (0.7, "#F27A3E"), (1, "#C23C22")], 0, 0, 1, 0),
        lg(f"{u}-pilL", [(0, "#C23C22"), (0.4, "#F27A3E"), (0.75, "#E8542C"), (1, "#A8301E")], 0, 0, 1, 0),
        lg(f"{u}-path", [(0, "#C8A878"), (0.5, "#8E7458"), (1, "#5A4A3A")], 0, 300, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-shaft", [(0, "#FFF0B0", 0.0), (0.5, "#FFE6A0", 0.45), (1, "#FFF0B0", 0.0)], 0, 0, 1, 0),
    )]
    # the forest behind: dark cedar wood, sun pouring in from the upper right
    out.append(f'<rect width="600" height="444" fill="url(#{u}-for)"/>')
    out.append(glow(520, 60, 340, "#F6D27A", f"{u}-sun", 0.75))
    rnd = random.Random(3)
    for i in range(22):  # cedar trunks
        x = rnd.uniform(-10, 610)
        w = rnd.uniform(5, 16)
        c = rnd.choice(["#2A2018", "#3A2A1E", "#4A3424"])
        out.append(rect(x, 40, w, 300, c, f' opacity="{rnd.uniform(0.5, 0.9):.2f}"'))
        out.append(rect(x + w * 0.7, 40, w * 0.3, 300, "#E8B870", ' opacity="0.25"'))
    for i, (x, y, rx, ry, cols) in enumerate(((80, 80, 130, 60, ("#2E4A26", "#4E6E34", "#A8B85A")), (520, 90, 140, 70, ("#3A5228", "#6A8A3A", "#D8D27A")),
                                              (300, 60, 160, 40, ("#2E4A26", "#4E6E34", "#B8C060")), (40, 220, 80, 60, ("#22361E", "#3A5228", "#8EA050")),
                                              (570, 230, 70, 60, ("#22361E", "#3A5228", "#C8C060")))):
        out.append(leaf_canopy(f"{u}-c{i}", x, y, rx, ry, 10 + i, *cols, light=(1, -1), n=220, r=(0.06, 0.13)))
    # a red maple branch catching the light at the top left
    out.append(branch([(-10, 50), (60, 62), (130, 70), (190, 66)], 7, 2, "#3A2420"))
    out.append(leaf_canopy(f"{u}-mp", 110, 66, 96, 30, 31, "#8A2A1E", "#C8462A", "#F28A4A", gold="#FFC070", light=(1, -1), n=160, r=(0.07, 0.15)))
    out.append(f'<polygon points="{P([(560, 40), (610, 40), (380, 330), (330, 330)])}" fill="url(#{u}-shaft)" opacity="0.6"/>')
    out.append(f'<polygon points="{P([(470, 40), (500, 40), (250, 300), (226, 300)])}" fill="url(#{u}-shaft)" opacity="0.4"/>')
    # the path: bright opening at the far end, stone steps climbing toward us
    xa, ya = axis(Z1)
    ex, ey = C(xa, ya + 1.0, Z1)
    out.append(glow(ex, ey, 90, "#FFF2C0", f"{u}-end", 0.95))
    path_l = [C(axis(Z)[0] - HW, axis(Z)[1], Z) for Z in [Z0 - 1.2 + i * 0.5 for i in range(52)]]
    path_r = [C(axis(Z)[0] + HW, axis(Z)[1], Z) for Z in [Z0 - 1.2 + i * 0.5 for i in range(52)]]
    out.append(Q(path_l + path_r[::-1], f"url(#{u}-path)"))
    steps = []
    for j in range(46):
        Z = Z0 - 1.0 + j * 0.52
        X, Y = axis(Z)
        a, b = C(X - HW, Y, Z), C(X + HW, Y, Z)
        steps.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#E8D2A8" stroke-width="{max(0.6, 7 / Z):.1f}" opacity="0.7"/>')
        steps.append(f'<line x1="{a[0]:.1f}" y1="{a[1] + 4 / Z:.1f}" x2="{b[0]:.1f}" y2="{b[1] + 4 / Z:.1f}" stroke="#3A2A20" stroke-width="{max(0.5, 5 / Z):.1f}" opacity="0.4"/>')
    out.append("".join(steps))
    # sun flecks on the steps, filtered through the slats
    rnd = random.Random(9)
    for _ in range(40):
        Z = rnd.uniform(Z0, Z1 * 0.7)
        X, Y = axis(Z)
        px, py = C(X + rnd.uniform(-HW * 0.8, HW * 0.8), Y, Z)
        out.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{90 / Z:.1f}" ry="{18 / Z:.1f}" fill="#FFE6A0" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    # a visitor in a summer yukata walking up the tunnel, slotted in among the gates at her own depth
    ZV = 5.3
    vx, vy = C(axis(ZV)[0] - 0.12, axis(ZV)[1], ZV)
    visitor = yukata_visitor(vx, vy, 1.58 * C.f / ZV, u, light=1, rim="#FFD49A")
    # the gates, far to near
    gates = [Z1 - i * dz for i in range(int((Z1 - Z0) / dz) + 1)]
    for Z in gates:
        if visitor and Z < ZV:
            out.append(visitor)
            visitor = None
        X, Y = axis(Z)
        Zb = Z + 0.26
        Xb, Yb = axis(Zb)
        g = []
        near = Z < 4
        for side in (-1, 1):
            px = X + side * HW
            # inner side face of the pillar (toward the path) receding to the back face
            a = C(px - side * PW, Y, Z)
            b = C(px - side * PW, Y + TOP - 0.25, Z)
            c = C(Xb + side * HW - side * PW, Yb + TOP - 0.25, Zb)
            d = C(Xb + side * HW - side * PW, Yb, Zb)
            g.append(Q([a, b, c, d], "#B83820" if side < 0 else "#C8482A"))
            # front face (cylinder shading: lit from the right)
            fl, fr = C(px - PW, Y, Z), C(px + PW, Y + TOP - 0.25, Z)
            g.append(rect(fl[0], fr[1], fr[0] - fl[0], fl[1] - fr[1], f"url(#{u}-pil)"))
            # black nemaki foot
            fb = C(px - PW * 1.15, Y + 0.32, Z)
            g.append(rect(fb[0], fb[1], (fr[0] - fl[0]) * 1.15, fl[1] - fb[1], "#1E1614"))
            # donors' inscriptions as abstract brush strokes on the near side faces
            if Z < 9 and side < 0:
                ins = C(px - side * PW, Y + TOP * 0.75, Z + 0.13)
                h = 0.9 * C.f / Z
                g.append("".join(f'<rect x="{ins[0] + j * 2.4 * 3 / Z - 1.5:.1f}" y="{ins[1] + h * (0.1 + 0.12 * (j % 3)):.1f}" width="{max(0.8, 2.6 / Z):.1f}" height="{h * (0.25 + 0.1 * j):.1f}" fill="#1E1614" opacity="0.75"/>' for j in range(3)))
        # nuki tie beam
        n0, n1 = C(X - HW - 0.24, Y + TOP - 0.55, Z), C(X + HW + 0.24, Y + TOP - 0.4, Z)
        g.append(rect(n0[0], n1[1], n1[0] - n0[0], n0[1] - n1[1], "#D8482A"))
        g.append(rect(n0[0], n1[1], n1[0] - n0[0], (n0[1] - n1[1]) * 0.3, "#F2884A"))
        # kasagi lintel: a vermilion shimaki under the black-capped kasagi whose ends sweep upward
        s0, s1 = C(X - HW - 0.32, Y + TOP - 0.3, Z), C(X + HW + 0.32, Y + TOP - 0.15, Z)
        g.append(rect(s0[0], s1[1], s1[0] - s0[0], s0[1] - s1[1], "#E8542C"))
        g.append(rect(s0[0], s0[1] - (s0[1] - s1[1]) * 0.25, s1[0] - s0[0], (s0[1] - s1[1]) * 0.25, "#9A2A18", ' opacity="0.5"'))
        k0, k1 = C(X - HW - 0.48, Y + TOP - 0.15, Z), C(X + HW + 0.48, Y + TOP, Z)
        kw, kh = k1[0] - k0[0], k0[1] - k1[1]
        yb, yt = k0[1], k1[1]
        lift = kh * 1.1
        g.append(f'<path d="M {k0[0]:.1f} {yb - lift:.1f} Q {k0[0] + kw * 0.22:.1f} {yb:.1f} {k0[0] + kw * 0.5:.1f} {yb:.1f} Q {k0[0] + kw * 0.78:.1f} {yb:.1f} {k1[0]:.1f} {yb - lift:.1f} '
                 f'L {k1[0] + kw * 0.01:.1f} {yt - lift * 1.1:.1f} Q {k0[0] + kw * 0.78:.1f} {yt:.1f} {k0[0] + kw * 0.5:.1f} {yt:.1f} Q {k0[0] + kw * 0.22:.1f} {yt:.1f} {k0[0] - kw * 0.01:.1f} {yt - lift * 1.1:.1f} Z" fill="#1E1614"/>')
        if near:
            g.append(f'<path d="M {k0[0] + kw * 0.5:.1f} {yt + 0.8:.1f} Q {k0[0] + kw * 0.78:.1f} {yt + 0.8:.1f} {k1[0]:.1f} {yt - lift * 1.05:.1f}" stroke="#F2B07A" stroke-width="1.4" fill="none" opacity="0.7"/>')
        k1 = (k1[0], yb - kh * 0.2)
        kh = 0.0
        # gakuzuka strut between nuki and kasagi
        sx0, sx1 = C(X - 0.06, Y, Z)[0], C(X + 0.06, Y, Z)[0]
        g.append(rect(sx0, s0[1], sx1 - sx0, n1[1] - s0[1], "#C8402A"))
        # depth: far gates dissolve into the warm light
        fade = min(0.75, max(0.0, (Z - 6) / 26))
        out.append(f'<g>{"".join(g)}</g>')
        if fade > 0.02:
            out.append(f'<g opacity="{fade:.2f}">' + "".join(
                Q([C(X + side * HW - PW * 1.2, Y, Z), C(X + side * HW - PW * 1.2, Y + TOP, Z), C(X + side * HW + PW * 1.2, Y + TOP, Z), C(X + side * HW + PW * 1.2, Y, Z)], "#F6D49A") for side in (-1, 1)) + "</g>")
    # the stone fox and a lantern guarding the entrance
    out.append(kitsune(96, 452, 1.05))
    out.append(stone_lantern(522, 446, 1.15))
    for i, (x0, x1) in enumerate(((-10, 200), (420, 610))):
        out.append(leaf_canopy(f"{u}-fern{i}", (x0 + x1) / 2, 436, (x1 - x0) / 2, 18, 40 + i, "#1E3018", "#2E4A24", "#6E8A3A", light=(1, -1), n=50, r=(0.2, 0.4)))
        out.append(grass(60, 13 + i, (x0, 410, x1, 444), ["#2E4A24", "#4E6E30", "#8EA048"], h=(6, 14), sw=1.8))
    # maple leaves drifting down
    rnd = random.Random(15)
    lv = []
    for _ in range(14):
        x, y = rnd.uniform(70, 540), rnd.uniform(110, 380)
        r = rnd.uniform(3, 5)
        lv.append(f'<path d="M {x:.1f} {y - r:.1f} l {r * 0.3:.1f} {r * 0.6:.1f} l {r * 0.7:.1f} {-r * 0.2:.1f} l {-r * 0.4:.1f} {r * 0.6:.1f} l {r * 0.3:.1f} {r * 0.5:.1f} l {-r * 0.9:.1f} {-r * 0.1:.1f} l 0 {r * 0.6:.1f} l {-r * 0.4:.1f} {-r * 0.6:.1f} l {-r * 0.9:.1f} {r * 0.1:.1f} l {r * 0.3:.1f} {-r * 0.5:.1f} l {-r * 0.4:.1f} {-r * 0.6:.1f} l {r * 0.7:.1f} {r * 0.2:.1f} Z" '
                  f'fill="{rnd.choice(["#E8542C", "#F28A3A", "#C8302A"])}" transform="rotate({rnd.uniform(0, 360):.0f} {x:.1f} {y:.1f})"/>')
    out.append("".join(lv))
    return "\n".join(out)


# ================================================================ TOKYO — a lantern-lit side street after rain
def chochin(x, y, r, u, k, col="#F23A2A", glow_r=None, strength=0.75, ribs=True):
    """Red paper lantern: glowing ribbed body with black caps, hanging cord."""
    o = []
    if glow_r:
        o.append(glow(x, y, glow_r, "#FF7A4A", f"{u}-cg{k}", strength))
    o.append(f'<line x1="{x:.1f}" y1="{y - r * 1.9:.1f}" x2="{x:.1f}" y2="{y - r * 1.25:.1f}" stroke="#1A1018" stroke-width="{max(0.6, r * 0.12):.1f}"/>')
    o.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 1.25:.1f}" fill="{col}"/>')
    o.append(f'<ellipse cx="{x - r * 0.15:.1f}" cy="{y - r * 0.1:.1f}" rx="{r * 0.55:.1f}" ry="{r * 0.95:.1f}" fill="#FFB070" opacity="0.75"/>')
    o.append(f'<ellipse cx="{x - r * 0.2:.1f}" cy="{y - r * 0.15:.1f}" rx="{r * 0.22:.1f}" ry="{r * 0.6:.1f}" fill="#FFF0C8" opacity="0.8"/>')
    if ribs and r > 4:
        o.append(f'<g stroke="#A81E1A" stroke-width="{max(0.5, r * 0.07):.1f}" opacity="0.6" fill="none">' + "".join(
            f'<path d="M {x - r * math.sqrt(max(0, 1 - t * t)):.1f} {y + t * r * 1.25:.1f} Q {x:.1f} {y + t * r * 1.25 + r * 0.12:.1f} {x + r * math.sqrt(max(0, 1 - t * t)):.1f} {y + t * r * 1.25:.1f}"/>' for t in (-0.6, -0.3, 0, 0.3, 0.6)) + "</g>")
        # a family-crest style ring, no lettering
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.36:.1f}" fill="none" stroke="#2A1214" stroke-width="{r * 0.12:.1f}" opacity="0.7"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.12:.1f}" fill="#2A1214" opacity="0.7"/>')
    o.append(rect(x - r * 0.6, y - r * 1.3, r * 1.2, r * 0.22, "#1A1018") + rect(x - r * 0.6, y + r * 1.1, r * 1.2, r * 0.22, "#1A1018"))
    return "".join(o)


def pictogram(cx, cy, s, kind, ink):
    """Little picture signs for the alley (no letters): skewers, a noodle bowl, a sake flask, a fish, a cup, a ring crest."""
    if kind == "skewer":
        return (f'<line x1="{cx:.1f}" y1="{cy - s * 0.5:.1f}" x2="{cx:.1f}" y2="{cy + s * 0.5:.1f}" stroke="{ink}" stroke-width="{max(0.7, s * 0.07):.1f}"/>'
                + "".join(f'<circle cx="{cx:.1f}" cy="{cy - s * 0.3 + i * s * 0.22:.1f}" r="{s * 0.13:.1f}" fill="{ink}"/>' for i in range(3)))
    if kind == "bowl":
        return (f'<path d="M {cx - s * 0.45:.1f} {cy:.1f} Q {cx:.1f} {cy + s * 0.6:.1f} {cx + s * 0.45:.1f} {cy:.1f} Z" fill="{ink}"/>'
                f'<path d="M {cx - s * 0.15:.1f} {cy - s * 0.1:.1f} q {s * 0.1:.1f} {-s * 0.2:.1f} 0 {-s * 0.4:.1f} M {cx + s * 0.12:.1f} {cy - s * 0.1:.1f} q {s * 0.1:.1f} {-s * 0.2:.1f} 0 {-s * 0.4:.1f}" stroke="{ink}" stroke-width="{max(0.6, s * 0.06):.1f}" fill="none"/>')
    if kind == "sake":
        return (f'<path d="M {cx - s * 0.08:.1f} {cy - s * 0.5:.1f} L {cx + s * 0.08:.1f} {cy - s * 0.5:.1f} L {cx + s * 0.08:.1f} {cy - s * 0.25:.1f} Q {cx + s * 0.34:.1f} {cy:.1f} {cx + s * 0.28:.1f} {cy + s * 0.45:.1f} '
                f'L {cx - s * 0.28:.1f} {cy + s * 0.45:.1f} Q {cx - s * 0.34:.1f} {cy:.1f} {cx - s * 0.08:.1f} {cy - s * 0.25:.1f} Z" fill="{ink}"/>')
    if kind == "fish":
        return (f'<path d="M {cx - s * 0.45:.1f} {cy:.1f} Q {cx - s * 0.05:.1f} {cy - s * 0.35:.1f} {cx + s * 0.25:.1f} {cy:.1f} L {cx + s * 0.45:.1f} {cy - s * 0.18:.1f} L {cx + s * 0.45:.1f} {cy + s * 0.18:.1f} '
                f'L {cx + s * 0.25:.1f} {cy:.1f} Q {cx - s * 0.05:.1f} {cy + s * 0.35:.1f} {cx - s * 0.45:.1f} {cy:.1f} Z" fill="{ink}"/>')
    if kind == "cup":
        return (f'<path d="M {cx - s * 0.3:.1f} {cy - s * 0.25:.1f} L {cx + s * 0.3:.1f} {cy - s * 0.25:.1f} L {cx + s * 0.22:.1f} {cy + s * 0.35:.1f} L {cx - s * 0.22:.1f} {cy + s * 0.35:.1f} Z" fill="{ink}"/>'
                f'<circle cx="{cx - s * 0.1:.1f}" cy="{cy - s * 0.4:.1f}" r="{s * 0.06:.1f}" fill="{ink}"/><circle cx="{cx + s * 0.08:.1f}" cy="{cy - s * 0.48:.1f}" r="{s * 0.05:.1f}" fill="{ink}"/>')
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s * 0.36:.1f}" fill="none" stroke="{ink}" stroke-width="{max(0.8, s * 0.1):.1f}"/>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{s * 0.14:.1f}" fill="{ink}"/>')


def glyph_panel(x0, y0, w, h, seed, ink):
    """A tall sign panel filled with pictograms and dot rules — reads as a shop sign, spells nothing."""
    rnd = random.Random(seed)
    n = max(1, int(h / (w * 1.15)))
    kinds = rnd.sample(["skewer", "bowl", "sake", "fish", "cup", "crest"], k=min(n, 6))
    o = []
    for i in range(n):
        cy = y0 + h * (i + 0.5) / n
        o.append(pictogram(x0 + w / 2, cy, min(w, h / n) * 0.8, kinds[i % len(kinds)], ink))
        if i < n - 1 and w > 8:
            o.append(rect(x0 + w * 0.2, y0 + h * (i + 1) / n - 0.5, w * 0.6, 1, ink, ' opacity="0.5"'))
    return "".join(o)


def akachochin(x, y, r, u, k, glow_r=None, strength=0.6, body="#E2341E"):
    """Red paper lantern of an izakaya, lit from inside: a hot core fading to a deep red rim, bamboo ribs,
    black lacquer caps and a short cord. No lettering."""
    o = []
    if glow_r:
        o.append(glow(x, y, glow_r, "#FF6A3A", f"{u}-lg{k}", strength))
    o.append(f'<line x1="{x:.1f}" y1="{y - r * 1.75:.1f}" x2="{x:.1f}" y2="{y - r * 1.2:.1f}" stroke="#140C12" stroke-width="{max(0.7, r * 0.1):.1f}"/>')
    o.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 1.22:.1f}" fill="url(#{u}-lan)"/>')
    if r > 3.2:
        o.append(f'<g stroke="#8A160E" stroke-width="{max(0.5, r * 0.06):.1f}" opacity="0.45" fill="none">' + "".join(
            f'<path d="M {x - r * math.sqrt(max(0, 1 - t * t)):.1f} {y + t * r * 1.22:.1f} Q {x:.1f} {y + t * r * 1.22 + r * 0.14:.1f} {x + r * math.sqrt(max(0, 1 - t * t)):.1f} {y + t * r * 1.22:.1f}"/>'
            for t in (-0.7, -0.45, -0.2, 0.05, 0.3, 0.55, 0.78)) + "</g>")
        o.append(f'<ellipse cx="{x - r * 0.38:.1f}" cy="{y - r * 0.25:.1f}" rx="{r * 0.16:.1f}" ry="{r * 0.55:.1f}" fill="#FFE8B0" opacity="0.55"/>')
    o.append(f'<rect x="{x - r * 0.58:.1f}" y="{y - r * 1.34:.1f}" width="{r * 1.16:.1f}" height="{max(0.8, r * 0.2):.1f}" rx="{r * 0.05:.1f}" fill="#140C12"/>'
             f'<rect x="{x - r * 0.58:.1f}" y="{y + r * 1.14:.1f}" width="{r * 1.16:.1f}" height="{max(0.8, r * 0.2):.1f}" rx="{r * 0.05:.1f}" fill="#140C12"/>')
    return "".join(o)


def umbrella_couple(x, base, h, u, light=1, rim="#FFB27A", tint=None, umb="#C8342A"):
    """A couple walking away from us under one oiled-paper umbrella: he holds it (tilted toward her), she has
    her arm through his. Built from two figures.py skeletons seen from behind."""
    from figures import Painter, _palette, _render, mix as fmix, pose_joints
    k = h / 100.0
    g = 25.0                      # distance between the two spines, in figure units
    him = _palette({"form": "m", "top_kind": "jacket", "bottom_kind": "trousers", "top": "#3A4A6E", "bottom": "#24222C", "hair_style": "short",
                    "hair": "#1C1412", "skin": "#E8B48E", "shoes": "#2A2228", "inner": "#E8E2D8"}, 3)
    her = _palette({"form": "f", "top_kind": "coat", "bottom_kind": "skirt", "top": "#C89A64", "bottom": "#4A2434", "hair_style": "long",
                    "hair": "#2A1A14", "skin": "#F0C8A4", "shoes": "#2A2228"}, 4)
    Jm = pose_joints("stand_back", "m", random.Random(1))
    Jf = pose_joints("stand_back", "f", random.Random(2))
    # in step: his left heel and her right heel lifting
    Jm["legs"] = [([(-4.6, -49), (-4.4, -27), (-4.0, -8.0)], None, "front"), ([(4.6, -49), (4.8, -26), (4.6, -3.8)], None, "front")]
    Jf["legs"] = [([(-4.4, -49), (-4.2, -26), (-3.8, -3.8)], None, "front"), ([(4.4, -49), (4.0, -27), (3.6, -8.0)], None, "front")]
    # his inner (right) arm bent up to the shaft in front of his chest; his outer arm swings
    Jm["arms"] = [("L", [(-8.8, -79.2), (-12.6, -64.5), (-12.0, -51)], "front"), ("R", [(8.8, -79.2), (12.0, -67.0), (3.0, -70.0)], "back")]
    # her inner (left) arm hooked through his elbow
    Jf["arms"] = [("L", [(-7.6, -79.2), (-11.2, -67), (-15.0, -66.0)], "front"), ("R", [(7.6, -79.2), (11.0, -64.5), (11.2, -51)], "front")]
    o = []
    for dx in (-g / 2, g / 2):
        o.append(f'<ellipse cx="{dx - light * 3:.1f}" cy="0.8" rx="15" ry="2.6" fill="#0A0610" opacity="0.4"/>')
    # the umbrella: tilted toward her, shaft down to his hand
    tilt = 10.0
    cx_, top_, rim_y, R = 1.5, -128.0, -112.0, 36.0
    a = math.radians(tilt)
    def rot(px, py):    # rotate about the hand
        hx_, hy_ = -g / 2 + 4.0, -70.0
        dx, dy = px - hx_, py - hy_
        return (hx_ + dx * math.cos(a) - dy * math.sin(a), hy_ + dx * math.sin(a) + dy * math.cos(a))
    sh0, sh1 = rot(-g / 2 + 4.0, -70.0), rot(-g / 2 + 4.0, top_ - 4)
    o.append(f'<line x1="{sh0[0]:.1f}" y1="{sh0[1]:.1f}" x2="{sh1[0]:.1f}" y2="{sh1[1]:.1f}" stroke="#5A3A24" stroke-width="1.6"/>')
    for (J, pal, dx, sc) in ((Jm, him, -g / 2, 1.0), (Jf, her, g / 2, 0.95)):
        B = Painter(k * sc, light, rim, tint, 2)
        _render(B, J, pal, False, "stand_back")
        o.append(f'<g transform="translate({dx:.1f} 0) scale({sc})">' + "".join(B.out) + "</g>")
    # canopy: the underside ellipse we glimpse from below, ribs, then the dome
    ccx = -g / 2 + 4.0     # canopy centre x before tilt (on the shaft)
    def C2(px, py):
        return rot(ccx + px, py)
    dk, mid, lt = fmix(umb, "#140812", 0.45), umb, fmix(umb, "#FFD8A0", 0.35)
    under = [C2(R * math.cos(t), rim_y + 6.5 * math.sin(t)) for t in [i * math.pi / 24 for i in range(49)]]
    o.append(f'<polygon points="{P(under)}" fill="{fmix(umb, "#2A0A10", 0.55)}"/>')
    hub = C2(0, rim_y + 2.0)
    for i in range(24):
        t = i * 2 * math.pi / 24
        e = C2(R * math.cos(t) * 0.98, rim_y + 6.3 * math.sin(t))
        if math.sin(t) > -0.2:
            o.append(f'<line x1="{hub[0]:.1f}" y1="{hub[1]:.1f}" x2="{e[0]:.1f}" y2="{e[1]:.1f}" stroke="#E8C88A" stroke-width="0.5" opacity="0.6"/>')
    dome = [C2(R * math.cos(t), rim_y - (rim_y - top_) * max(0.0, math.sin(t)) ** 0.75) for t in [i * math.pi / 30 for i in range(31)]]
    o.append(f'<polygon points="{P(dome)}" fill="{mid}"/>')
    # gores: alternating panels catching the lantern light from the right
    for i in range(8):
        t0, t1 = i * math.pi / 8, (i + 1) * math.pi / 8
        pts = [C2(0, top_ + 1.5)] + [C2(R * math.cos(t), rim_y - (rim_y - top_) * 0.04 * math.sin(t)) for t in (t0, (t0 + t1) / 2, t1)]
        shade = lt if i < 3 else dk if i > 5 else None
        if shade:
            o.append(f'<polygon points="{P(pts)}" fill="{shade}" opacity="{0.55 if i < 3 else 0.5}"/>')
    for i in range(1, 8):
        t = i * math.pi / 8
        e = C2(R * math.cos(t), rim_y - 0.4)
        top = C2(0, top_ + 1.5)
        o.append(f'<line x1="{top[0]:.1f}" y1="{top[1]:.1f}" x2="{e[0]:.1f}" y2="{e[1]:.1f}" stroke="{dk}" stroke-width="0.6" opacity="0.7"/>')
    # the scalloped rim, a lit ring at the top and a little finial
    rim_pts = [C2(R * math.cos(t), rim_y + 1.2 * abs(math.sin(t * 8))) for t in [i * math.pi / 64 for i in range(65)]]
    o.append(f'<polyline points="{P(rim_pts)}" fill="none" stroke="{lt}" stroke-width="1.2" opacity="0.9"/>')
    ring = [C2(R * 0.28 * math.cos(t), top_ + 6 - 1.5 * math.sin(t)) for t in [i * math.pi / 12 for i in range(13)]]
    o.append(f'<polyline points="{P(ring)}" fill="none" stroke="#F6E2B0" stroke-width="0.9" opacity="0.7"/>')
    fin = C2(0, top_ - 3)
    o.append(f'<circle cx="{fin[0]:.1f}" cy="{fin[1]:.1f}" r="1.6" fill="#2A1A14"/>')
    # wet sheen and drops falling from the rim
    sheen = [C2(R * 0.55 * math.cos(t) + 6, rim_y - (rim_y - top_) * 0.72 * max(0.0, math.sin(t)) ** 0.8) for t in [i * math.pi / 16 for i in range(4, 10)]]
    o.append(f'<polyline points="{P(sheen)}" fill="none" stroke="#FFF2DA" stroke-width="1.2" opacity="0.55" stroke-linecap="round"/>')
    for px in (-R * 0.98, -R * 0.6, R * 0.35, R * 0.97):
        d = C2(px, rim_y + 4)
        o.append(f'<ellipse cx="{d[0]:.1f}" cy="{d[1] + random.Random(int(px)).uniform(2, 9):.1f}" rx="0.7" ry="1.4" fill="#FFE2C0" opacity="0.8"/>')
    return f'<g transform="translate({x:.1f} {base:.1f}) scale({k:.4f})">' + "".join(o) + "</g>"


def tokyo():
    u = "tokyo"
    C = Cam(f=440, cx=300, vpy=256, eye=1.6)
    W = 1.75
    out = [defs(
        lg(f"{u}-sky", [(0, "#0C0A24"), (0.55, "#241A4A"), (0.85, "#4A2A5E"), (1, "#8A4A6A")], 0, 40, 0, 250, units="userSpaceOnUse"),
        lg(f"{u}-road", [(0, "#4A3048"), (0.25, "#2A1E34"), (1, "#120E1C")], 0, 262, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-shop", [(0, "#FFE6B0"), (0.6, "#FFC27A"), (1, "#E88A4A")], 0, 0, 0, 1),
        lg(f"{u}-wood", [(0, "#4A2E26"), (1, "#2A1A1C")], 0, 0, 0, 1),
        lg(f"{u}-twr", [(0, "#2E2A54"), (1, "#1A1834")], 0, 0, 1, 0),
        lg(f"{u}-vg", [(0, "#06040C", 0.62), (0.3, "#06040C", 0.18), (0.5, "#06040C", 0.0), (0.7, "#06040C", 0.18), (1, "#06040C", 0.62)], 0, 0, 1, 0),
        lg(f"{u}-rf", [(0, "#FF7A3A", 0.0), (0.25, "#FF7A3A", 0.5), (0.7, "#E8442A", 0.35), (1, "#E8442A", 0.0)], 0, 0, 0, 1),
        rg(f"{u}-lan", [(0, "#FFE29A"), (0.35, "#FF8A3A"), (0.75, "#E2341E"), (1, "#9A1A12")], 0.42, 0.42, 0.62),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    # clouds clearing after the rain, lit from below by the city
    for x, y, w, op in ((140, 92, 120, 0.45), (420, 70, 150, 0.4), (330, 128, 90, 0.35), (520, 140, 80, 0.3), (60, 150, 70, 0.3)):
        out.append(streak_cloud(x, y, w, "#6A4A7A", op, 7))
        out.append(streak_cloud(x + 10, y + 5, w * 0.7, "#B86A8A", op * 0.6, 2.2))
    out.append(dots(26, 2, (180, 44, 420, 110), "#FFFFFF", r=(0.5, 1.1), opacity=(0.3, 0.8)))
    # the city beyond the end of the alley: towers with lit window grids, warning lights on top
    fx, fy = C(0.0, 1.6, 48)
    out.append(glow(fx, fy - 20, 220, "#FF9A6A", f"{u}-city", 0.55))
    rnd = random.Random(31)
    towers = [(-120, 118, 26, 1), (-84, 150, 22, 0), (-46, 104, 30, 1), (-10, 140, 20, 0), (26, 96, 24, 1), (60, 132, 30, 0), (98, 112, 22, 1), (134, 150, 26, 0)]
    for dx, ty, tw, lit_side in towers:
        x0 = 300 + dx
        out.append(rect(x0, ty, tw, 262 - ty, f"url(#{u}-twr)"))
        out.append(rect(x0 + (tw * 0.7 if lit_side else 0), ty, tw * 0.3, 262 - ty, "#3E3A6A", ' opacity="0.6"'))
        cells = []
        for yy in range(int(ty) + 6, 250, 6):
            for xx in range(int(x0) + 3, int(x0 + tw) - 3, 5):
                if rnd.random() < 0.38:
                    cells.append(f'<rect x="{xx}" y="{yy}" width="2.6" height="2.4" fill="{rnd.choice(["#FFD89A", "#FFE8C0", "#BFD8FF"])}" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
        out.append("".join(cells))
        out.append(f'<circle cx="{x0 + tw / 2:.1f}" cy="{ty - 2:.1f}" r="1.8" fill="#FF4A3A"/>' + glow(x0 + tw / 2, ty - 2, 7, "#FF4A3A", f"{u}-wl{dx}", 0.7))
    # the bright cross street at the far end
    out.append(glow(fx, fy + 8, 90, "#FFE2B0", f"{u}-end", 0.9))
    # ---------------------------------------------------------------- the two rows of izakaya, far to near
    segs = []
    for side in (-1, 1):
        rs = random.Random(40 + side)
        z = 1.2 if side < 0 else 1.0
        while z < 48:
            d = rs.uniform(2.8, 4.4)
            segs.append((z, z + d, side, rs.uniform(5.8, 8.6), rs.random()))
            z += d
    segs.sort(key=lambda s_: -s_[0])
    lanterns, refl, spill, signs = [], [], [], []
    walls = ["#3A2626", "#2E2232", "#3A2A30", "#2A2030", "#442A2A"]
    norens = ["#26305E", "#8A1E26", "#F2E8D8", "#26305E", "#3A2A4A"]
    for z0, z1, side, h, rv in segs:
        rs = random.Random(int(z0 * 100) + side)
        X = side * W
        th = lambda zz, base=6.0: max(0.6, base / zz)
        g = []
        # upper storeys: wooden boards or old plaster
        wood = rv < 0.55
        g.append(Q(C.quad_x(X, z0, z1, 2.55, h), f"url(#{u}-wood)" if wood else rs.choice(walls)))
        if wood:
            for j in range(1, int((z1 - z0) / 0.3)):
                zz = z0 + j * 0.3
                a, b = C(X, 2.6, zz), C(X, h, zz)
                g.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#1A1014" stroke-width="{th(zz, 1.6):.1f}" opacity="0.5"/>')
        # roof edge catching the city glow
        a, b = C(X, h, z0), C(X, h, z1)
        g.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#9A6A9A" stroke-width="{th(z0, 7):.1f}"/>')
        # upper windows: warm shoji glow or dark glass
        for fl in (3.3, 5.6):
            if fl + 1.3 > h - 0.3:
                continue
            za, zb = z0 + (z1 - z0) * 0.22, z0 + (z1 - z0) * 0.78
            lit = rs.random() < 0.62
            g.append(Q(C.quad_x(X, za, zb, fl, fl + 1.3), rs.choice(["#FFD49A", "#FFC27A", "#FFE2B4"]) if lit else "#1C1628"))
            if lit:
                for j in range(1, 5):
                    zz = za + (zb - za) * j / 5
                    p, q_ = C(X, fl, zz), C(X, fl + 1.3, zz)
                    g.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q_[0]:.1f}" y2="{q_[1]:.1f}" stroke="#7A4A2E" stroke-width="{th(zz, 2.4):.1f}" opacity="0.7"/>')
                p, q_ = C(X, fl + 0.65, za), C(X, fl + 0.65, zb)
                g.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q_[0]:.1f}" y2="{q_[1]:.1f}" stroke="#7A4A2E" stroke-width="{th(za, 2.4):.1f}" opacity="0.7"/>')
            else:
                g.append(Q(C.quad_x(X, za, za + (zb - za) * 0.3, fl, fl + 1.3), "#4A3A5A", ' opacity="0.7"'))
            g.append(Q(C.quad_x(X, za - 0.05, zb + 0.05, fl - 0.12, fl), "#5A4048"))
            if rs.random() < 0.35:   # an air-conditioner box under the window
                g.append(Q(C.quad_x(X - side * 0.02, zb + 0.15, zb + 0.75, fl - 0.1, fl + 0.45), "#8A8698"))
                g.append(Q(C.quad_x(X - side * 0.02, zb + 0.15, zb + 0.75, fl + 0.35, fl + 0.45), "#B8B4C4"))
        # ground floor: posts, a low dark plinth, warm frosted glass with a slat lattice
        sa, sb = z0 + 0.22, z1 - 0.22
        g.append(Q(C.quad_x(X, z0, z1, 0, 2.55), "#24161A"))
        g.append(Q(C.quad_x(X, sa, sb, 0.45, 2.1), f"url(#{u}-shop)"))
        # patrons on stools, seen as soft shapes through the glass
        for j in range(3):
            zz = sa + (sb - sa) * (0.2 + 0.3 * j)
            if rs.random() < 0.7:
                hx, hy = C(X, 1.42, zz)
                rr = 0.12 * C.f / zz
                g.append(f'<g opacity="0.35"><ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="{rr:.1f}" ry="{rr * 1.2:.1f}" fill="#6A3424"/>'
                         + Q(C.quad_x(X, zz - 0.2, zz + 0.2, 0.75, 1.3), "#6A3424") + "</g>")
        for j in range(1, 9):
            zz = sa + (sb - sa) * j / 9
            p, q_ = C(X, 0.45, zz), C(X, 2.1, zz)
            g.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q_[0]:.1f}" y2="{q_[1]:.1f}" stroke="#5A321E" stroke-width="{th(zz, 3.2 if j % 3 else 6):.1f}" opacity="0.8"/>')
        p, q_ = C(X, 1.25, sa), C(X, 1.25, sb)
        g.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q_[0]:.1f}" y2="{q_[1]:.1f}" stroke="#5A321E" stroke-width="{th(sa, 3):.1f}" opacity="0.7"/>')
        for zz in (z0 + 0.1, z1 - 0.1):
            p, q_ = C(X, 0, zz), C(X, 2.55, zz)
            g.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q_[0]:.1f}" y2="{q_[1]:.1f}" stroke="#140C10" stroke-width="{th(zz, 16):.1f}"/>')
        # noren over the doorway: split panels with a white crest
        nz0, nz1 = sa + (sb - sa) * 0.12, sa + (sb - sa) * (0.62 if rs.random() < 0.5 else 0.88)
        ncol = rs.choice(norens)
        ink = "#F6EEE0" if ncol != "#F2E8D8" else "#26305E"
        npan = 4
        for j in range(npan):
            pa = nz0 + (nz1 - nz0) * j / npan
            pb = nz0 + (nz1 - nz0) * (j + 1) / npan - 0.04
            g.append(Q(C.quad_x(X - side * 0.03, pa, pb, 1.45, 2.15), ncol))
            g.append(Q(C.quad_x(X - side * 0.03, pa, pb, 2.05, 2.15), mix(ncol, "#000000", 0.25)))
        cz = (nz0 + nz1) / 2
        ccx, ccy = C(X - side * 0.03, 1.86, cz)
        cr = 0.1 * C.f / cz
        crx = cr * 0.3 * (1 + 0.9 * abs((ccx - 300) / 300))
        g.append(f'<ellipse cx="{ccx:.1f}" cy="{ccy:.1f}" rx="{crx:.1f}" ry="{cr:.1f}" fill="none" stroke="{ink}" stroke-width="{max(0.6, cr * 0.22):.1f}" opacity="0.85"/>')
        # a pale band along the hem of the noren
        g.append(Q(C.quad_x(X - side * 0.035, nz0, nz1 - 0.04, 1.45, 1.53), ink, ' opacity="0.5"'))
        # the eave: dark tiles, its underside warmed by the shop light, a lit lip
        eo = 0.62
        g.append(Q([C(X, 2.62, z0), C(X, 2.62, z1), C(X - side * eo, 2.36, z1), C(X - side * eo, 2.36, z0)], "#4A2A24"))
        g.append(Q([C(X - side * eo, 2.36, z0), C(X - side * eo, 2.36, z1), C(X - side * eo, 2.48, z1), C(X - side * eo, 2.48, z0)], "#2A2228"))
        a, b = C(X - side * eo, 2.36, z0), C(X - side * eo, 2.36, z1)
        g.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#FF9A5A" stroke-width="{th(z0, 2.2):.1f}" opacity="0.7"/>')
        g.append(Q([C(X, 2.62, z0), C(X - side * eo, 2.36, z0), C(X - side * eo, 2.48, z0), C(X, 2.8, z0)], "#1A1418"))
        # light spilling out on the wet stones
        spill.append(Q([C(X, 0, sa), C(X - side * 1.3, 0, sa + 0.5), C(X - side * 1.3, 0, sb - 0.2), C(X, 0, sb)], "#FFB060", ' opacity="0.16"'))
        refl.append(Q(C.quad_x(X, sa, sb, -1.4, 0), "#FFB878", ' opacity="0.13"'))
        # lanterns under the eave
        nl = 2 if rs.random() < 0.6 else 3
        for j in range(nl):
            zz = z0 + 0.45 + (z1 - z0 - 0.9) * j / max(1, nl - 1)
            lx, ly = C(X - side * 0.4, 1.98, zz)
            lanterns.append((zz, lx, ly, 0.16 * C.f / zz, X - side * 0.4))
        # a projecting picture sign above the eave, face toward us
        if rs.random() < 0.8 and z0 > 6.5:
            zz = z0 + 0.15
            y1_ = min(rs.uniform(4.4, 5.4), 1.6 + 0.4 * zz)
            y0_ = min(rs.uniform(3.0, 3.3), y1_ - 1.2)
            signs.append((zz, X, side, y0_, y1_, rs.choice(["#F6EEDC", "#FFD45A", "#F26A4A", "#7EE8F0", "#F6EEDC"]), int(zz * 100) + side))
        out.append("<g>" + "".join(g) + "</g>")
    # wet road between the walls
    road = [C(-W, 0, 1.0), C(-W, 0, 60), C(W, 0, 60), C(W, 0, 1.0)]
    out.append(f'<clipPath id="{u}-rd"><polygon points="{P(road)}"/></clipPath>')
    out.append(Q(road, f"url(#{u}-road)"))
    stones = []
    for j in range(1, 70):
        zz = 1.0 + j * 0.42 * (1 + j * 0.03)
        a, b = C(-W, 0, zz), C(W, 0, zz)
        stones.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#0E0A14" stroke-width="{max(0.4, 2.4 / zz):.1f}" opacity="0.5"/>')
    for xx in (-1.2, -0.6, 0, 0.6, 1.2):
        a, b = C(xx, 0, 1.0), C(xx, 0, 60)
        stones.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#0E0A14" stroke-width="1" opacity="0.3"/>')
    # gutter channels along each wall
    for side in (-1, 1):
        a, b = C(side * (W - 0.25), 0, 1.0), C(side * (W - 0.25), 0, 60)
        stones.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#08060C" stroke-width="3" opacity="0.6"/>')
    lan_refl = []
    for zz, lx, ly, r, LX in lanterns:
        gx, gy = C(LX, 0, zz)
        my = C(LX, -1.98, zz)[1]
        lan_refl.append(f'<rect x="{gx - r * 0.7:.1f}" y="{gy:.1f}" width="{r * 1.4:.1f}" height="{max(1, my + r - gy):.1f}" fill="url(#{u}-rf)"/>')
        lan_refl.append(ripple_reflection(int(4 + 16 / zz), int(lx * 7 + zz * 13), gx, gy + 1, my + r, r * 1.6, ["#FF5A2A", "#FF9A4A", "#FFD08A"], op=(0.2, 0.6)))
    out.append(f'<g clip-path="url(#{u}-rd)">' + "".join(stones) + "".join(spill) + "".join(refl) + "".join(lan_refl)
               + ripple_reflection(40, 5, fx, fy + 12, 380, 26, ["#FFE2B0", "#FF9A6A", "#FFFFFF"], op=(0.15, 0.5), spread=1.6)
               + water_lines(24, 6, (0, 300, 600, 444), ["#6A4A7A", "#9A5A7A"], w=(10, 40), h=(1, 2), opacity=(0.12, 0.3)) + "</g>")
    # projecting signs (pictograms only), far to near
    for zz, X, side, y0_, y1_, col, seed in sorted(signs, reverse=True):
        a = C(X - side * 0.08, y1_, zz)
        b = C(X - side * 0.6, y0_, zz)
        x0, x1 = min(a[0], b[0]), max(a[0], b[0])
        w, hh = x1 - x0, b[1] - a[1]
        out.append(glow((x0 + x1) / 2, (a[1] + b[1]) / 2, max(w, hh) * 0.8, col, f"{u}-sg{seed}", 0.35))
        out.append(rect(x0 - w * 0.06, a[1] - w * 0.06, w * 1.12, hh + w * 0.12, "#140C18"))
        out.append(rect(x0, a[1], w, hh, col))
        out.append(glyph_panel(x0 + w * 0.1, a[1] + w * 0.12, w * 0.8, hh - w * 0.24, seed, "#2A1218" if col in ("#F6EEDC", "#FFD45A", "#7EE8F0") else "#FFF6EC"))
        # bracket to the wall
        p, q_ = C(X, y1_ - 0.2, zz), C(X - side * 0.1, y1_ - 0.2, zz)
        out.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q_[0]:.1f}" y2="{q_[1]:.1f}" stroke="#140C18" stroke-width="{max(0.8, 6 / zz):.1f}"/>')
    # overhead wires, sagging across the alley
    for zz, y, sag in ((5.5, 6.2, 0.6), (9, 6.6, 0.5), (14, 6.0, 0.4), (22, 6.4, 0.35), (7, 7.0, 0.9)):
        a, b = C(-W, y, zz), C(W, y + 0.3, zz + 1.2)
        mid_ = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + sag * C.f / zz)
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} Q {mid_[0]:.1f} {mid_[1]:.1f} {b[0]:.1f} {b[1]:.1f}" stroke="#08060E" stroke-width="{max(0.7, 6 / zz):.1f}" fill="none"/>')
    # the couple under one umbrella, walking away toward the light
    ZC = 6.0
    px, py = C(-0.12, 0, ZC)
    cpl = umbrella_couple(px, py, 1.72 * C.f / ZC, u, light=1, rim="#FFB27A")
    # lanterns: farther ones before the couple, near ones after
    lan_sorted = sorted(lanterns, reverse=True)
    for i, (zz, lx, ly, r, LX) in enumerate(lan_sorted):
        if cpl and zz < ZC:
            out.append(f'<ellipse cx="{px:.1f}" cy="{py + 2:.1f}" rx="58" ry="5" fill="#FFB060" opacity="0.08"/>')
            out.append(cpl)
            out.append(ripple_reflection(30, 77, px, py + 4, py + 40, 34, ["#C8342A", "#8A3A5A", "#3A4A6E"], op=(0.2, 0.5)))
            cpl = None
        out.append(akachochin(lx, ly, r, u, i, glow_r=r * 3.6 if zz < 16 else None, strength=0.5))
    # the near walls fall into shadow, framing the lit alley
    out.append(f'<rect width="600" height="444" fill="url(#{u}-vg)"/>')
    # drizzle caught in the lantern light
    rnd = random.Random(88)
    drops = []
    for _ in range(70):
        x, y = rnd.uniform(40, 560), rnd.uniform(60, 400)
        L = rnd.uniform(4, 9)
        drops.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x - L * 0.12:.1f}" y2="{y + L:.1f}"/>')
    out.append(f'<g stroke="#FFE2C8" stroke-width="0.9" opacity="0.35" stroke-linecap="round">{"".join(drops)}</g>')
    return "\n".join(out)


# ================================================================ SEOUL — palace eaves in autumn, Namsan and its tower beyond
def korean_roof(cx, eave_y, half, h, k, u, tile="#3A3C44", tile_lit="#6A6C78", under="#2E6A5A", ridge_h=None):
    """Hip-and-gable (paljak) roof in elevation: concave tiled slope whose eave sweeps up at both corners,
    dancheong under the eave, white mortared ridges ending in upturned ornaments."""
    o = []
    lift = 19 * k
    top = eave_y - h
    # underside (painted rafters) between the sweeping eave and the straight bracket band
    def ev(t):  # point on the eave curve, t in -1..1
        return cx + half * t, eave_y + 2 * k - (2 * k + lift) * abs(t) ** 2.6
    curve = [ev(i / 20 - 1) for i in range(41)]
    o.append(Q(curve + [(cx + half * 0.8, eave_y + 9 * k), (cx - half * 0.8, eave_y + 9 * k)], under))
    o.append(Q([(x, y + 1.5 * k) for x, y in curve] + [(cx + half * 0.8, eave_y + 9 * k), (cx - half * 0.8, eave_y + 9 * k)], "#1A3A32", ' opacity="0.35"'))
    o.append("".join(f'<rect x="{x - 0.8 * k:.1f}" y="{y + 1.0 * k:.1f}" width="{1.6 * k:.1f}" height="{1.6 * k:.1f}" fill="#F2C040"/>' for x, y in curve[1:-1:2]))
    o.append("".join(f'<circle cx="{x:.1f}" cy="{y + 4.2 * k:.1f}" r="{1.4 * k:.1f}" fill="#F2E8D0"/><circle cx="{x:.1f}" cy="{y + 4.2 * k:.1f}" r="{0.65 * k:.1f}" fill="#C83A2A"/>' for x, y in curve[2:-2:2]))
    for sx in (-1, 1):  # sharp upswept corner tips
        x0, y0 = ev(sx)
        o.append(f'<path d="M {x0 - sx * 8 * k:.1f} {y0 + 3 * k:.1f} Q {x0:.1f} {y0 + 1 * k:.1f} {x0 + sx * 5 * k:.1f} {y0 - 6 * k:.1f} L {x0 + sx * 2 * k:.1f} {y0 - 1 * k:.1f} Q {x0 - sx * 4 * k:.1f} {y0 - 2 * k:.1f} {x0 - sx * 10 * k:.1f} {y0 - 1 * k:.1f} Z" fill="{tile}"/>')
    # tiled slope: concave, from the eave up to the hip line
    hip_y = top + h * 0.42
    slope = ("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in curve)
             + f" Q {cx + half * 0.8:.1f} {eave_y - lift * 0.6:.1f} {cx + half * 0.5:.1f} {hip_y:.1f} L {cx - half * 0.5:.1f} {hip_y:.1f} Q {cx - half * 0.8:.1f} {eave_y - lift * 0.6:.1f} {cx - half:.1f} {eave_y - lift:.1f} Z")
    o.append(f'<path d="{slope}" fill="{tile}"/>')
    o.append(f'<clipPath id="{u}"><path d="{slope}"/></clipPath><g clip-path="url(#{u})" stroke="{tile_lit}" stroke-width="{max(0.8, 1.2 * k):.1f}" opacity="0.7">'
             + "".join(f'<line x1="{cx + t * half * 1.05:.1f}" y1="{eave_y + 4:.1f}" x2="{cx + t * half * 0.55:.1f}" y2="{hip_y:.1f}"/>' for t in [i / 22 - 1 for i in range(45)]) + "</g>")
    o.append(f'<g clip-path="url(#{u})"><rect x="{cx:.1f}" y="{hip_y:.1f}" width="{half * 1.2:.1f}" height="{eave_y - hip_y + 10:.1f}" fill="#F6C890" opacity="0.18"/></g>')
    # tile-end discs along the eave
    pts = curve
    o.append("".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{1.4 * k:.1f}" fill="#8A8C98"/>' for x, y in pts))
    o.append(f'<polyline points="{P(pts)}" fill="none" stroke="#B8BAC8" stroke-width="{0.8 * k:.1f}" opacity="0.7"/>')
    # gable (hapgak) and main ridge
    gx = half * 0.42
    up = [(cx - half * 0.5, hip_y), (cx - gx, top + 4 * k), (cx + gx, top + 4 * k), (cx + half * 0.5, hip_y)]
    o.append(Q(up, tile))
    o.append(f'<clipPath id="{u}-up"><polygon points="{P(up)}"/></clipPath><g clip-path="url(#{u}-up)" stroke="{tile_lit}" stroke-width="{max(0.8, 1.2 * k):.1f}" opacity="0.6">'
             + "".join(f'<line x1="{cx + t * half * 0.52:.1f}" y1="{hip_y:.1f}" x2="{cx + t * gx:.1f}" y2="{top:.1f}"/>' for t in [i / 14 - 1 for i in range(29)])
             + f'</g><g clip-path="url(#{u}-up)"><rect x="{cx:.1f}" y="{top:.1f}" width="{half:.1f}" height="{hip_y - top:.1f}" fill="#F6C890" opacity="0.15"/></g>')
    o.append(Q([(cx + gx * 0.9, top + 6 * k), (cx + gx, top + 4 * k), (cx + half * 0.5, hip_y), (cx + half * 0.44, hip_y)], "#8A3A2A"))
    o.append(rect(cx - gx - 2 * k, top, 2 * gx + 4 * k, 4.5 * k, "#4A4C56"))
    o.append(rect(cx - gx - 2 * k, top + 1 * k, 2 * gx + 4 * k, 1.6 * k, "#F2EEE6"))
    for sx in (-1, 1):  # upturned ridge ends (chwidu)
        ex = cx + sx * (gx + 2 * k)
        o.append(f'<path d="M {ex:.1f} {top + 4.5 * k:.1f} q {sx * 2 * k:.1f} {-7 * k:.1f} {sx * 6 * k:.1f} {-9 * k:.1f} q {-sx * 1 * k:.1f} {5 * k:.1f} {-sx * 2 * k:.1f} {9 * k:.1f} Z" fill="#4A4C56"/>')
        # hip ridges with white mortar
        o.append(f'<path d="M {cx + sx * half * 0.5:.1f} {hip_y:.1f} Q {cx + sx * half * 0.8:.1f} {eave_y - lift * 0.6:.1f} {cx + sx * half:.1f} {eave_y - lift:.1f}" stroke="#4A4C56" stroke-width="{3 * k:.1f}" fill="none"/>'
                 f'<path d="M {cx + sx * half * 0.5:.1f} {hip_y - 1 * k:.1f} Q {cx + sx * half * 0.8:.1f} {eave_y - lift * 0.6 - 1 * k:.1f} {cx + sx * half:.1f} {eave_y - lift - 1 * k:.1f}" stroke="#F2EEE6" stroke-width="{1.1 * k:.1f}" fill="none"/>')
        # japsang guardian figures in a row on the hip ridge
        for j in range(4):
            t = 0.25 + j * 0.15
            fx = lerp(cx + sx * half * 0.55, cx + sx * half * 0.95, t)
            fy = lerp(hip_y + 1 * k, eave_y - lift + 2 * k, t ** 1.4) - 2 * k
            o.append(f'<path d="M {fx - 1.2 * k:.1f} {fy:.1f} L {fx - 1 * k:.1f} {fy - 3.6 * k:.1f} Q {fx:.1f} {fy - 5 * k:.1f} {fx + 1 * k:.1f} {fy - 3.6 * k:.1f} L {fx + 1.2 * k:.1f} {fy:.1f} Z" fill="#4A4C56"/>')
    return "".join(o)


def palace_hall(cx, base, k, u):
    """Two-storey palace hall (like Geunjeongjeon) on a granite terrace: red columns, green lattice, two tiled roofs."""
    o = []
    # granite terrace (woldae) with balustrade
    o.append(rect(cx - 150 * k, base - 16 * k, 300 * k, 16 * k, "#D8CCB8") + rect(cx - 150 * k, base - 16 * k, 300 * k, 2.4 * k, "#F6ECDA")
             + rect(cx - 150 * k, base - 16 * k, 300 * k, 16 * k, "#8A7A6A", ' opacity="0.0"'))
    o.append("".join(rect(cx - 148 * k + j * 12 * k, base - 24 * k, 2 * k, 8 * k, "#E8DECA") for j in range(25)))
    o.append(rect(cx - 150 * k, base - 25 * k, 300 * k, 2 * k, "#E8DECA"))
    o.append("".join(rect(cx - 20 * k + j * 0, base - 16 * k + i * 3.2 * k, 40 * k, 1.2 * k, "#B8AC98") for i in range(5) for j in range(1)))
    # ground storey: red columns, green lattice doors with paper glowing warm
    gb = base - 25 * k
    o.append(rect(cx - 112 * k, gb - 46 * k, 224 * k, 46 * k, "#3E6A58"))
    for j in range(9):
        x = cx - 112 * k + j * 28 * k
        if j < 8:
            o.append(rect(x + 3 * k, gb - 40 * k, 22 * k, 38 * k, "#F2DCB0"))
            o.append(f'<g stroke="#3E6A58" stroke-width="{0.8 * k:.1f}">' + "".join(f'<line x1="{x + 3 * k + i * 22 * k / 6:.1f}" y1="{gb - 40 * k:.1f}" x2="{x + 3 * k + i * 22 * k / 6:.1f}" y2="{gb - 2 * k:.1f}"/>' for i in range(1, 6))
                     + "".join(f'<line x1="{x + 3 * k:.1f}" y1="{gb - 40 * k + i * 38 * k / 7:.1f}" x2="{x + 25 * k:.1f}" y2="{gb - 40 * k + i * 38 * k / 7:.1f}"/>' for i in range(1, 7)) + "</g>")
        o.append(rect(x - 2.4 * k, gb - 48 * k, 4.8 * k, 48 * k, "#9A2E22") + rect(x + 0.8 * k, gb - 48 * k, 1.6 * k, 48 * k, "#E8784A", ' opacity="0.7"'))
    # bracket band (gongpo) painted in dancheong
    o.append(rect(cx - 118 * k, gb - 56 * k, 236 * k, 9 * k, "#2E6A5A"))
    o.append("".join(f'<rect x="{cx - 116 * k + j * 9.8 * k:.1f}" y="{gb - 55 * k:.1f}" width="{5 * k:.1f}" height="{7 * k:.1f}" fill="{c}"/>' for j, c in
                     ((j, ("#C83A2A", "#2E8AA8", "#F2C040")[j % 3]) for j in range(24))))
    o.append(korean_roof(cx, gb - 57 * k, 150 * k, 40 * k, k, f"{u}-r1"))
    # upper storey
    ub = gb - 74 * k
    o.append(rect(cx - 80 * k, ub - 34 * k, 160 * k, 34 * k, "#3E6A58"))
    for j in range(7):
        x = cx - 80 * k + j * 26.6 * k
        if j < 6:
            o.append(rect(x + 3 * k, ub - 28 * k, 20 * k, 26 * k, "#E8D0A0"))
        o.append(rect(x - 2 * k, ub - 36 * k, 4 * k, 36 * k, "#9A2E22") + rect(x + 0.6 * k, ub - 36 * k, 1.4 * k, 36 * k, "#E8784A", ' opacity="0.7"'))
    o.append(rect(cx - 86 * k, ub - 44 * k, 172 * k, 8 * k, "#2E6A5A"))
    o.append("".join(f'<rect x="{cx - 84 * k + j * 9.6 * k:.1f}" y="{ub - 43 * k:.1f}" width="{5 * k:.1f}" height="{6 * k:.1f}" fill="{("#C83A2A", "#2E8AA8", "#F2C040")[j % 3]}"/>' for j in range(18)))
    o.append(korean_roof(cx, ub - 45 * k, 118 * k, 64 * k, k, f"{u}-r2"))
    return "".join(o)


def n_tower(cx, base, k):
    """Generic slim broadcast tower on the summit: tapering white shaft, a two-ring observation pod, antenna mast."""
    o = [Q([(cx - 4 * k, base), (cx - 2.4 * k, base - 72 * k), (cx + 2.4 * k, base - 72 * k), (cx + 4 * k, base)], "#ECE6E2"),
         Q([(cx + 1 * k, base), (cx + 0.8 * k, base - 72 * k), (cx + 2.4 * k, base - 72 * k), (cx + 4 * k, base)], "#B8A8B0")]
    for y, w, h, c in ((base - 72 * k, 9 * k, 5 * k, "#E2DCD8"), (base - 80 * k, 10 * k, 8 * k, "#F2ECE6"), (base - 84 * k, 8 * k, 4 * k, "#D8D0CC")):
        o.append(rect(cx - w, y - h, 2 * w, h, c) + rect(cx + w * 0.3, y - h, w * 0.7, h, "#A898A8", ' opacity="0.5"'))
    o.append(rect(cx - 10 * k, base - 80 * k, 20 * k, 2.4 * k, "#FFD890"))
    o.append(rect(cx - 1.4 * k, base - 120 * k, 2.8 * k, 36 * k, "#ECE6E2"))
    o.append("".join(rect(cx - 1.4 * k, base - 120 * k + j * 7 * k, 2.8 * k, 3.5 * k, "#D8483A") for j in range(5)))
    o.append(f'<line x1="{cx:.1f}" y1="{base - 120 * k:.1f}" x2="{cx:.1f}" y2="{base - 132 * k:.1f}" stroke="#ECE6E2" stroke-width="{1 * k:.1f}"/>')
    # sun on the right side
    o.append(rect(cx + 1.2 * k, base - 120 * k, 1.2 * k, 36 * k, "#FFE0B0", ' opacity="0.8"'))
    return "".join(o)


def seoul():
    u = "seoul"
    out = [defs(
        lg(f"{u}-sky", [(0, "#3E78BA"), (0.45, "#86B2D8"), (0.8, "#E8D8C0"), (1, "#F6D8A8")], 0, 40, 0, 320, units="userSpaceOnUse"),
        lg(f"{u}-nam", [(0, "#8A8AA0"), (1, "#A89EA8")], 0, 210, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#F2DCC0", 0), (1, "#F2D8B8", 0.85)], 0, 240, 0, 310, units="userSpaceOnUse"),
        lg(f"{u}-yard", [(0, "#E2CCAA"), (1, "#B89A78")], 0, 320, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-tile", [(0, "#2E3038"), (0.6, "#3E404A"), (1, "#5A5C68")], 0, 0, 1, 1),
        lg(f"{u}-under", [(0, "#1E4A40"), (1, "#2E6A5A")], 0, 0, 0, 1),
    )]
    out.append(f'<rect width="600" height="330" fill="url(#{u}-sky)"/>')
    out.append(glow(600, 240, 300, "#FFE2B0", f"{u}-sun", 0.75))
    for x, y, w in ((380, 96, 90), (520, 140, 70), (200, 180, 60)):
        out.append(streak_cloud(x, y, w, "#FFFFFF", 0.55, 3.4))
        out.append(streak_cloud(x + 10, y + 2, w * 0.5, "#FFF0E0", 0.6, 1.4))
    # Namsan: a rounded wooded mountain in autumn haze, the tower on its crown
    poly, nm = ridge_poly([(300, 300), (360, 272), (420, 250), (470, 240), (520, 250), (580, 272), (620, 286)], 61, amp=4, fill=f"url(#{u}-nam)")
    out.append(poly)
    out.append(f'<clipPath id="{u}-nc"><polygon points="{P(nm + [(620, 320), (300, 320)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-nc)">' + blobs(120, 62, (300, 236, 620, 310), ["#B07A70", "#9A8A80", "#C89A78", "#8A8A88"], r=(3, 7), opacity=(0.4, 0.8)) + "</g>")
    out.append(n_tower(470, 244, 1.05))
    # the city in the haze between
    rnd = random.Random(63)
    x = 260
    while x < 610:
        w, h = rnd.uniform(10, 24), rnd.uniform(10, 40)
        out.append(rect(x, 300 - h, w, h, rnd.choice(["#C8B8B0", "#D2C2B8", "#BEB0B0"])))
        x += w + rnd.uniform(0, 6)
    out.append(f'<rect x="0" y="240" width="600" height="80" fill="url(#{u}-haze)"/>')
    # Bugaksan-like ridge on the far left, behind the hall
    poly, bk = ridge_poly([(-10, 260), (60, 240), (140, 250), (220, 270), (300, 290)], 64, amp=5, fill="#A8A0A8")
    out.append(poly)
    # autumn trees behind the hall
    for i, (x, y, rx, ry, cols) in enumerate(((60, 300, 70, 30, ("#B8641E", "#E8A030", "#FFD860")), (520, 306, 80, 28, ("#9A3A22", "#D8582A", "#F6A050")),
                                              (420, 312, 50, 22, ("#B8641E", "#E8A030", "#FFD860")))):
        out.append(leaf_canopy(f"{u}-bt{i}", x, y, rx, ry, 70 + i, *cols, light=(1, -1), n=90, r=(0.1, 0.2)))
    out.append(palace_hall(250, 338, 0.95, u))
    # the courtyard: granite paving with long late shadows to the left
    out.append(Q([(-10, 336), (610, 336), (610, 444), (-10, 444)], f"url(#{u}-yard)"))
    rnd = random.Random(65)
    pav = []
    for r_ in range(9):
        y = 338 + r_ * (6 + r_ * 1.5)
        x = -10 + rnd.uniform(0, 20)
        while x < 610:
            w = rnd.uniform(26, 50) * (0.6 + r_ * 0.12)
            pav.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w - 1.6:.1f}" height="{5 + r_ * 1.5:.1f}" fill="{rnd.choice(["#E8D4B4", "#D8C2A0", "#EEDCBE", "#CDB494"])}" opacity="0.8"/>')
            x += w
    out.append("".join(pav))
    out.append(Q([(110, 338), (390, 338), (420, 444), (80, 444)], "#D8C4A8", ' opacity="0.35"'))
    out.append(Q([(-10, 352), (130, 340), (60, 444), (-10, 444)], "#6A5A6A", ' opacity="0.18"'))
    # ginkgo and maple in full colour at the courtyard edges, leaves on the paving
    out.append(rect(574, 300, 7, 92, "#4A3428") + rect(578, 300, 3, 92, "#C8885A"))
    out.append(branch([(577, 330), (556, 300), (548, 270)], 5, 2, "#4A3428") + branch([(578, 316), (596, 290)], 4, 2, "#4A3428"))
    for i, (x, y, rx, ry) in enumerate(((572, 300, 48, 34), (566, 256, 40, 34), (574, 214, 30, 30), (544, 286, 26, 22))):
        out.append(leaf_canopy(f"{u}-gk{i}", x, y, rx, ry, 81 + i, "#C8781E", "#F2B42E", "#FFE070", gold="#FFF2A0", light=(1, -1), n=90, r=(0.08, 0.16)))
    out.append(dots(80, 82, (380, 360, 610, 444), "#F2C030", r=(1.2, 2.6), opacity=(0.7, 1)))
    out.append(dots(30, 83, (60, 380, 300, 444), "#D8482A", r=(1.2, 2.4), opacity=(0.6, 1)))
    # visitors in hanbok
    for x, y, h, top, skirt in ((330, 392, 34, "#F6E6C8", "#E86A8A"), (350, 394, 36, "#2E4A7A", "#2E4A7A"), (180, 372, 22, "#F2E2C0", "#6AA8C8")):
        out.append(f'<ellipse cx="{x - h * 0.4:.1f}" cy="{y:.1f}" rx="{h * 0.5:.1f}" ry="{h * 0.06:.1f}" fill="#5A4A5A" opacity="0.3"/>')
        out.append(f'<path d="M {x - h * 0.2:.1f} {y:.1f} Q {x - h * 0.22:.1f} {y - h * 0.5:.1f} {x - h * 0.08:.1f} {y - h * 0.62:.1f} L {x + h * 0.08:.1f} {y - h * 0.62:.1f} Q {x + h * 0.22:.1f} {y - h * 0.5:.1f} {x + h * 0.2:.1f} {y:.1f} Z" fill="{skirt}"/>')
        out.append(rect(x - h * 0.11, y - h * 0.8, h * 0.22, h * 0.2, top))
        out.append(f'<circle cx="{x:.1f}" cy="{y - h * 0.88:.1f}" r="{h * 0.09:.1f}" fill="#2A1E1A"/>')
        out.append(rect(x + h * 0.06, y - h * 0.62, h * 0.12, h * 0.6, "#FFE0B0", ' opacity="0.35"'))
    # the near palace eave framing the top left: hip ridge with guardian figures, tiles, painted rafters
    tipx, tipy = 330, 122
    ridge = [(70, 34), (160, 58), (240, 84), (296, 104), (tipx + 8, tipy - 14)]
    eave = [(tipx, tipy), (270, 132), (180, 150), (80, 168), (-14, 182)]
    roof_poly = [(-14, 30)] + ridge + eave
    out.append(Q(roof_poly, "#2A2C34"))
    # tile rows on the roof face
    out.append(f'<clipPath id="{u}-rc"><polygon points="{P(roof_poly)}"/></clipPath><g clip-path="url(#{u}-rc)" stroke="#5A5C68" stroke-width="2.2">'
               + "".join(f'<line x1="{lerp(-14, tipx, t):.1f}" y1="{(y_on(eave[::-1], lerp(-14, tipx, t)) or 150) - 30:.1f}" x2="{lerp(-14, tipx, t) - 60:.1f}" y2="{(y_on(eave[::-1], lerp(-14, tipx, t)) or 150) - 120:.1f}"/>' for t in [i / 30 for i in range(31)]) + "</g>")
    under = [(tipx, tipy), (270, 132), (180, 150), (80, 168), (-14, 182), (-14, 132), (90, 118), (190, 104), (262, 104)]
    out.append(f'<path d="{smooth(under, closed=True)}" fill="url(#{u}-under)"/>')
    # radiating rafters with painted round ends (green, white, red rings)
    out.append(f'<clipPath id="{u}-uc"><path d="{smooth(under, closed=True)}"/></clipPath>')
    raf = []
    for j in range(26):
        t = j / 25
        ex = lerp(-10, tipx - 6, t ** 0.9)
        ey = (y_on(eave[::-1], ex) or tipy) - 4 - 6 * t
        ox, oy = -160, -40
        raf.append(f'<line x1="{ox:.1f}" y1="{oy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="#3E8A6A" stroke-width="{3.6 + 2 * (1 - t):.1f}"/>')
        raf.append(f'<line x1="{lerp(ox, ex, 0.82):.1f}" y1="{lerp(oy, ey, 0.82):.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="#C83A2A" stroke-width="{1.2 + 0.6 * (1 - t):.1f}"/>')
        raf.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{3.4 + 1.2 * (1 - t):.1f}" fill="#2E7A5E"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.2 + 0.8 * (1 - t):.1f}" fill="#F2E8D0"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.0 + 0.4 * (1 - t):.1f}" fill="#C83A2A"/>')
    out.append(f'<g clip-path="url(#{u}-uc)">{"".join(raf)}</g>')
    disc = []
    for j in range(22):
        t = j / 21
        ex = lerp(-6, tipx - 2, t)
        ey = (y_on(eave[::-1], ex) or tipy) - 1
        disc.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{4.6 - t:.1f}" fill="#4A4C58"/><circle cx="{ex + 0.8:.1f}" cy="{ey - 0.8:.1f}" r="{2.2 - t * 0.5:.1f}" fill="#8A8C9A"/>')
    out.append("".join(disc))
    out.append(f'<polyline points="{P(ridge)}" fill="none" stroke="#3A3C46" stroke-width="9" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{P([(x, y - 2) for x, y in ridge])}" fill="none" stroke="#F2EEE6" stroke-width="2.6" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{P([(x + 1, y + 4) for x, y in ridge])}" fill="none" stroke="#FFD8A0" stroke-width="1.4" opacity="0.6"/>')
    # japsang: a little procession of guardian figures on the hip ridge, the monk in front
    for j, t in enumerate((0.32, 0.45, 0.57, 0.68, 0.78, 0.88)):
        fx = lerp(70, tipx + 8, t)
        fy = (y_on(ridge, fx) or 100) - 4
        hh = 13 - j * 0.6
        out.append(f'<path d="M {fx - 3.6:.1f} {fy:.1f} L {fx - 3:.1f} {fy - hh * 0.6:.1f} Q {fx - 2:.1f} {fy - hh:.1f} {fx + 0.6:.1f} {fy - hh:.1f} Q {fx + 3:.1f} {fy - hh * 0.9:.1f} {fx + 3:.1f} {fy - hh * 0.6:.1f} L {fx + 3.6:.1f} {fy:.1f} Z" fill="#3A3C46"/>'
                   f'<path d="M {fx + 1.6:.1f} {fy - hh * 0.95:.1f} Q {fx + 3.2:.1f} {fy - hh * 0.8:.1f} {fx + 3:.1f} {fy - 1:.1f}" stroke="#FFD8A0" stroke-width="1.1" fill="none" opacity="0.7"/>')
    # upturned corner tip and a bronze wind-bell with its fish-shaped clapper
    out.append(f'<path d="M {tipx - 6:.1f} {tipy + 2:.1f} Q {tipx + 6:.1f} {tipy:.1f} {tipx + 14:.1f} {tipy - 18:.1f} L {tipx + 8:.1f} {tipy - 12:.1f} Q {tipx + 2:.1f} {tipy - 6:.1f} {tipx - 8:.1f} {tipy - 4:.1f} Z" fill="#3A3C46"/>')
    bx, by = tipx - 4, tipy + 26
    out.append(f'<line x1="{tipx - 4:.1f}" y1="{tipy + 2:.1f}" x2="{bx:.1f}" y2="{by - 8:.1f}" stroke="#2A2420" stroke-width="1.2"/>')
    out.append(f'<path d="M {bx - 5:.1f} {by:.1f} Q {bx - 5:.1f} {by - 9:.1f} {bx:.1f} {by - 9:.1f} Q {bx + 5:.1f} {by - 9:.1f} {bx + 5:.1f} {by:.1f} Z" fill="#6A7A5A"/><path d="M {bx + 2:.1f} {by - 8:.1f} Q {bx + 4.4:.1f} {by - 6:.1f} {bx + 4.6:.1f} {by:.1f}" stroke="#E8C890" stroke-width="1" fill="none"/>')
    out.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx:.1f}" y2="{by + 6:.1f}" stroke="#2A2420" stroke-width="1"/><path d="M {bx - 3:.1f} {by + 6:.1f} L {bx + 3:.1f} {by + 9:.1f} L {bx - 3:.1f} {by + 12:.1f} L {bx - 1:.1f} {by + 9:.1f} Z" fill="#7A8A6A"/>')
    # a maple branch reaching in from the right foreground
    out.append(branch([(612, 70), (580, 82), (546, 96), (520, 100)], 8, 2.5, "#4A2E26"))
    out.append(leaf_canopy(f"{u}-mpl", 570, 88, 60, 26, 91, "#8A2218", "#D8402A", "#F68A48", light=(1, -1), n=80, r=(0.1, 0.2)))
    out.append(leaf_canopy(f"{u}-mp2", 528, 104, 26, 14, 92, "#8A2218", "#D8402A", "#F68A48", light=(1, -1), n=30, r=(0.12, 0.24)))
    out.append(flock([(380, 150, 8), (396, 160, 6), (408, 146, 5)], "#4A4A6A", 1.6))
    return "\n".join(out)


# ================================================================ GREAT WALL — snaking over green ridges in morning mist
def far_wall(line, x0, x1, s, towers, col, lit, seed):
    """A distant run of wall riding a ridge crest: body under the crest line, tiny merlons, square towers."""
    pts = [(x, y_on(line, x)) for x in range(int(x0), int(x1) + 1, 2) if y_on(line, x) is not None]
    if len(pts) < 2:
        return ""
    h = 5 * s
    o = [Q([(x, y - h * 0.3) for x, y in pts] + [(x, y + h * 0.7) for x, y in pts[::-1]], col)]
    o.append(f'<polyline points="{P([(x, y - h * 0.3) for x, y in pts])}" fill="none" stroke="{lit}" stroke-width="{max(0.8, s * 1.2):.1f}"/>')
    o.append("".join(rect(x - s * 0.5, y - h * 0.3 - s * 1.4, s, s * 1.4, col) for x, y in pts[::max(1, int(3 / max(0.5, s)))]))
    for tx in towers:
        ty = y_on(line, tx)
        if ty is None:
            continue
        w, th = 9 * s, 10 * s
        o.append(rect(tx - w / 2, ty - th, w, th + h * 0.5, col) + rect(tx - w / 2, ty - th, w * 0.35, th + h * 0.5, lit, ' opacity="0.55"'))
        o.append("".join(rect(tx - w / 2 + j * w / 4.5, ty - th - s * 1.6, w / 9, s * 1.6, col) for j in range(5)))
        if s > 1.2:
            o.append("".join(f'<path d="{arch(tx - w * 0.3 + j * w * 0.22 - s * 0.7, tx - w * 0.3 + j * w * 0.22 + s * 0.7, ty - th * 0.35, ty - th * 0.55, ty - th * 0.65)}" fill="#3A3A3A" opacity="0.5"/>' for j in range(3)))
    return "".join(o)


def resample(pts, step):
    """Even spacing along a smooth Catmull-Rom curve through pts."""
    dense = []
    ext = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for j in range(20):
            t = j / 20
            t2, t3 = t * t, t * t * t
            dense.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in range(len(p1))))
    dense.append(pts[-1])
    out = [dense[0]]
    acc = 0.0
    for a, b in zip(dense, dense[1:]):
        acc += math.hypot(b[0] - a[0], b[1] - a[1])
        if acc >= step:
            out.append(b)
            acc = 0.0
    out.append(dense[-1])
    return out


def ribbon_wall(path, u, body="#B89878", body_dk="#8A6E58", lit="#F6DCB4", floor="#C8AE8C", mortar="#6A5444", depth=4.6, height=6.5, par=1.6):
    """The wall as a ribbon along a screen-space path of (x, y, s) points (s = px per metre, from far to near).
    Seen from a little above: walkway band, far parapet, crenellated near parapet with loopholes, brick side face."""
    pts = resample(path, 2.0)
    far = [(x, y - depth * s * 0.42) for x, y, s in pts]
    near = [(x, y) for x, y, s in pts]
    base = [(x, y + height * s) for x, y, s in pts]
    o = []
    # far parapet
    o.append(Q([(x, y - par * s * 0.8) for (x, y), (_, _, s) in zip(far, pts)] + far[::-1], body_dk))
    o.append(f'<polyline points="{P([(x, y - par * s * 0.8) for (x, y), (_, _, s) in zip(far, pts)])}" fill="none" stroke="{lit}" stroke-width="1.2" opacity="0.8"/>')
    # walkway with step lines across it
    o.append(Q(far + near[::-1], floor))
    steps = []
    for i in range(0, len(pts) - 1, 1):
        x, y, s = pts[i]
        x2, y2, _ = pts[i + 1]
        if abs(y2 - y) > 0.35 * abs(x2 - x) and i % max(1, int(3 / max(0.4, s * 0.4))) == 0:
            steps.append(f'<line x1="{far[i][0]:.1f}" y1="{far[i][1]:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="{mortar}" stroke-width="{max(0.6, s * 0.18):.1f}" opacity="0.5"/>')
    o.append("".join(steps))
    # side face, brick courses, the morning light raking it
    o.append(Q(near + base[::-1], f"url(#{u})"))
    courses = []
    for f in (0.12, 0.24, 0.36, 0.48, 0.6, 0.72, 0.84):
        courses.append(f'<polyline points="{P([(x, y + height * s * f) for x, y, s in pts])}" fill="none"/>')
    o.append(f'<g stroke="{mortar}" stroke-width="0.7" opacity="0.35">{"".join(courses)}</g>')
    # near parapet: continuous lower wall, then merlons with loopholes
    o.append(Q([(x, y - par * s * 0.55) for x, y, s in pts] + near[::-1], body))
    mer = []
    i = 0
    while i < len(pts) - 1:
        x, y, s = pts[i]
        L = 1.4 * s
        j = i
        acc = 0.0
        while j < len(pts) - 1 and acc < L:
            acc += math.hypot(pts[j + 1][0] - pts[j][0], pts[j + 1][1] - pts[j][1])
            j += 1
        seg = pts[i:j + 1]
        top = [(px, py - par * s * 1.1) for px, py, _ in seg]
        bot = [(px, py - par * s * 0.5) for px, py, _ in seg]
        mer.append(Q(top + bot[::-1], body))
        mer.append(f'<polyline points="{P(top)}" fill="none" stroke="{lit}" stroke-width="{max(0.8, s * 0.22):.1f}"/>')
        mx, my, ms = seg[len(seg) // 2]
        if ms > 2.2:
            mer.append(rect(mx - ms * 0.12, my - par * ms * 0.92, ms * 0.24, ms * 0.32, "#3A2C26"))
        # skip a crenel gap
        acc = 0.0
        k = j
        while k < len(pts) - 1 and acc < 0.8 * s:
            acc += math.hypot(pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1])
            k += 1
        i = max(k, i + 1)
    o.append("".join(mer))
    o.append(f'<polyline points="{P([(x, y - par * s * 0.55) for x, y, s in pts])}" fill="none" stroke="{lit}" stroke-width="1" opacity="0.6"/>')
    return "".join(o)


def watchtower(x, base, s, u, lit="#F6DCB4", body="#C8AA88", shade="#8A6E5A", roof=False):
    """Square brick watchtower: lit front, shaded side, arched windows, crenellated top; base = walkway level."""
    w, h, d = 10 * s, 11 * s, 4 * s
    o = [rect(x - w / 2, base - h, w, h + 4 * s, f"url(#{u})")]
    o.append(Q([(x + w / 2, base - h), (x + w / 2 + d, base - h - d * 0.45), (x + w / 2 + d, base + 4 * s - d * 0.45), (x + w / 2, base + 4 * s)], shade))
    o.append(rect(x - w / 2, base - h, w, max(1.2, s * 0.6), lit))
    o.append(f'<g stroke="#6A5444" stroke-width="0.7" opacity="0.35">' + "".join(f'<line x1="{x - w / 2:.1f}" y1="{base - h + j * h / 10:.1f}" x2="{x + w / 2:.1f}" y2="{base - h + j * h / 10:.1f}"/>' for j in range(1, 14)) + "</g>")
    for j in range(3):
        cxw = x - w * 0.28 + j * w * 0.28
        o.append(f'<path d="{arch(cxw - w * 0.065, cxw + w * 0.065, base - h * 0.42, base - h * 0.62, base - h * 0.72)}" fill="#2E2420"/>')
    o.append(f'<path d="{arch(x - w * 0.1, x + w * 0.1, base, base - h * 0.16, base - h * 0.28)}" fill="#2E2420"/>')
    mw = w / 11
    o.append("".join(rect(x - w / 2 + j * 2 * mw, base - h - mw * 1.4, mw, mw * 1.4, body) for j in range(6)))
    o.append("".join(Q([(x + w / 2 + d * t, base - h - d * 0.45 * t), (x + w / 2 + d * t, base - h - d * 0.45 * t - mw * 1.4), (x + w / 2 + d * t + mw * 0.6, base - h - d * 0.45 * (t + 0.15) - mw * 1.4), (x + w / 2 + d * t + mw * 0.6, base - h - d * 0.45 * (t + 0.15))], shade) for t in (0.1, 0.55)))
    if roof:  # a small hip-roofed watch pavilion on top
        rx, ry = x, base - h - mw * 1.4
        o.append(rect(rx - w * 0.22, ry - w * 0.2, w * 0.44, w * 0.2, "#8A3A2A"))
        o.append(f'<path d="M {rx - w * 0.34:.1f} {ry - w * 0.18:.1f} Q {rx:.1f} {ry - w * 0.24:.1f} {rx + w * 0.34:.1f} {ry - w * 0.18:.1f} L {rx + w * 0.16:.1f} {ry - w * 0.38:.1f} L {rx - w * 0.16:.1f} {ry - w * 0.38:.1f} Z" fill="#3A3A40"/>')
    return "".join(o)


def gw_spline(ctrl, ds_near=0.45, k=0.028):
    """Catmull-Rom through 3D control points, re-sampled by arc length with a step that grows with depth."""
    dense = []
    ext = [ctrl[0]] + ctrl + [ctrl[-1]]
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for j in range(60):
            t = j / 60
            t2, t3 = t * t, t * t * t
            dense.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2
                                      + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in range(3)))
    dense.append(ctrl[-1])
    out, acc, s = [dense[0]], 0.0, 0.0
    arcs = [0.0]
    for a, b in zip(dense, dense[1:]):
        d = math.dist(a, b)
        acc += d
        s += d
        if acc >= max(ds_near, k * b[2]):
            out.append(b)
            arcs.append(s)
            acc = 0.0
    if out[-1] != dense[-1]:
        out.append(dense[-1])
        arcs.append(s)
    return out, arcs


def gw_frames(pts):
    """Horizontal unit tangent and left normal at each sample."""
    fr = []
    for i in range(len(pts)):
        a, b = pts[max(0, i - 1)], pts[min(len(pts) - 1, i + 1)]
        tx, tz = b[0] - a[0], b[2] - a[2]
        d = math.hypot(tx, tz) or 1
        tx, tz = tx / d, tz / d
        fr.append(((tx, tz), (-tz, tx)))
    return fr


def gw_wall(C, ctrl, u, cam=(0.0, 0.0, 0.0), hw=2.6, body=7.5, par_out=1.75, par_mer=1.0, par_in=0.9, towers=(), skip=(), seed=1,
            haze=None, light=-1, near_detail=40.0):
    """The Great Wall as a real 3D ribbon along ctrl (metres, Y = walkway floor): the brick body on its ridge, the walkway with
    its steps, a crenellated parapet on the left (outer) side and a low parapet on the right, painted segment by segment far to
    near so it occludes itself and the hills correctly. Returns a list of (depth, svg) items so towers / people can be merged
    in by depth. haze(Z) -> (colour, amount) pushes far colours toward the air."""
    pts, arcs = gw_spline(ctrl)
    fr = gw_frames(pts)
    rnd = random.Random(seed)
    ex, ey, ez = cam[0], C.eye, 0.0
    items = []

    def hz(col, Z):
        if not haze:
            return col
        hc, amt = haze(Z)
        return mix(col, hc, amt)

    def proj(p):
        return C(p[0], p[1], p[2])

    def off(p, n, d, dy=0.0):
        return (p[0] + n[0] * d, p[1] + dy, p[2] + n[1] * d)

    # crenel pattern along the arc length: merlon 1.7 m, gap 0.75 m
    def merlon_at(s):
        return (s % 2.45) < 1.7

    for i in range(len(pts) - 1):
        p, q = pts[i], pts[i + 1]
        (ta, na), (tb, nb) = fr[i], fr[i + 1]
        Zm = (p[2] + q[2]) / 2
        sm = (arcs[i] + arcs[i + 1]) / 2
        if any(a <= sm <= b for a, b in skip):
            continue
        g = []
        Lp, Lq = off(p, na, hw), off(q, nb, hw)
        Rp, Rq = off(p, na, -hw), off(q, nb, -hw)
        # hill flanks falling away from the wall foot, wooded in autumn colours
        D, DROP = 120.0, 92.0
        def flank(A, n_, sgn, frac=1.0):
            # out and down the slope, but never toward / behind the camera
            dz = n_[1] * sgn * D * frac
            k_ = 1.0 if A[2] + dz > 0.55 * A[2] else (0.45 * A[2]) / max(1e-6, -dz)
            return off(A, n_, sgn * D * frac * k_, -body - DROP * frac * max(k_, 0.3))
        areas = []
        for sgn, (Ap, Aq) in ((1, (Lp, Lq)), (-1, (Rp, Rq))):
            bp, bq = (Ap[0], Ap[1] - body, Ap[2]), (Aq[0], Aq[1] - body, Aq[2])
            fp, fq = flank(Ap, na, sgn), flank(Aq, nb, sgn)
            poly = [proj(bp), proj(bq), proj(fq), proj(fp)]
            g.append(Q(poly, hz("#9A6A3A" if sgn * light > 0 else "#6E4A34", Zm)))
            ar = 0.5 * abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1])))
            areas.append(min(ar, 160000))
        # trees on the flanks, placed in 3D so they shrink with distance and stand in front of what lies behind
        cols = [("#6A2418", "#A8402A", "#E8804A"), ("#7A4218", "#C8722A", "#F2B05A"), ("#6E5E1C", "#BE9632", "#F2D47A"),
                ("#2E3A22", "#4A5E30", "#8EA05A"), ("#5E2424", "#983830", "#E07048"), ("#7A5A22", "#B08A3A", "#E8C878")]
        trees = []
        for sgn, ar in zip((1, -1), areas):
            rm = 1.0 * C.f / max(Zm, 1)
            rpx = max(2.4, rm)
            nt = int(min(220, ar / (math.pi * rpx * rpx) * 0.9))
            for _ in range(nt):
                tt = rnd.random()
                fr_ = rnd.random() ** 1.15
                base = (p[0] + (q[0] - p[0]) * tt, p[1] + (q[1] - p[1]) * tt, p[2] + (q[2] - p[2]) * tt)
                n = (na[0] + (nb[0] - na[0]) * tt, na[1] + (nb[1] - na[1]) * tt)
                A = off(base, n, sgn * hw)
                tp = flank(A, n, sgn, fr_)
                tp = (tp[0], tp[1] + (body * (1 - fr_) if fr_ < 0.05 else 0) + rnd.uniform(1.0, 3.0), tp[2])
                if tp[2] < 12.0:
                    continue
                x, y = proj(tp)
                if not (-30 < x < 630 and -10 < y < 470):
                    continue
                r = max(2.2, rnd.uniform(0.7, 1.3) * C.f / tp[2])
                trees.append((y, x, r, rnd.choice(cols), tp[2]))
        trees.sort()
        for y, x, r, (dk, md, lt), tz in trees:
            dk, md, lt = hz(dk, tz), hz(md, tz), hz(lt, tz)
            if r > 7:
                g.append(f'<circle cx="{x:.1f}" cy="{y + r * 0.3:.1f}" r="{r:.1f}" fill="{dk}"/><circle cx="{x - r * 0.38:.1f}" cy="{y + r * 0.05:.1f}" r="{r * 0.6:.1f}" fill="{md}"/>'
                         f'<circle cx="{x + r * 0.34:.1f}" cy="{y + r * 0.1:.1f}" r="{r * 0.58:.1f}" fill="{mix(md, dk, 0.25)}"/><circle cx="{x:.1f}" cy="{y - r * 0.3:.1f}" r="{r * 0.6:.1f}" fill="{md}"/>'
                         f'<circle cx="{x + light * r * 0.3:.1f}" cy="{y - r * 0.5:.1f}" r="{r * 0.34:.1f}" fill="{lt}" opacity="0.85"/><circle cx="{x + light * r * 0.62:.1f}" cy="{y - r * 0.05:.1f}" r="{r * 0.22:.1f}" fill="{lt}" opacity="0.7"/>')
            else:
                g.append(f'<circle cx="{x:.1f}" cy="{y + r * 0.25:.1f}" r="{r:.1f}" fill="{dk}"/><circle cx="{x + light * r * 0.1:.1f}" cy="{y:.1f}" r="{r * 0.82:.1f}" fill="{md}"/>'
                         f'<circle cx="{x + light * r * 0.32:.1f}" cy="{y - r * 0.32:.1f}" r="{r * 0.44:.1f}" fill="{lt}" opacity="0.85"/>')
        # brick body: the face(s) we can see
        def vis(n, pt):
            return n[0] * (ex - pt[0]) + n[1] * (ez - pt[2]) > 0
        faces = []
        for sgn, (Ap, Aq, n) in ((1, (Lp, Lq, na)), (-1, (Rp, Rq, na))):
            nn = (n[0] * sgn, n[1] * sgn)
            if vis(nn, Ap):
                top = par_out if sgn > 0 else par_in
                lit = (nn[0] * light) > 0
                col = "#C8A47E" if lit else "#8E7462"
                faces.append((sgn, Ap, Aq, top, col))
        for sgn, Ap, Aq, top, col in faces:
            bp, bq = (Ap[0], Ap[1] - body, Ap[2]), (Aq[0], Aq[1] - body, Aq[2])
            g.append(Q([proj(bp), proj(bq), proj(Aq), proj(Ap)], hz(col, Zm)))
            # granite footing, brick courses above it
            sp, sq = (Ap[0], Ap[1] - body * 0.62, Ap[2]), (Aq[0], Aq[1] - body * 0.62, Aq[2])
            g.append(Q([proj(bp), proj(bq), proj(sq), proj(sp)], hz(mix(col, "#7A7A70", 0.35), Zm)))
            if Zm < near_detail:
                for f_ in (0.15, 0.3, 0.45, 0.72, 0.84, 0.95):
                    a = proj((Ap[0], Ap[1] - body * f_, Ap[2]))
                    b = proj((Aq[0], Aq[1] - body * f_, Aq[2]))
                    g.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{hz("#5A4436", Zm)}" stroke-width="{max(0.4, 3 / Zm):.1f}" opacity="0.45"/>')
        # parapets and walkway
        def parapet(sgn, Ap, Aq, n_, inner_vis):
            o = []
            hgt = par_mer if sgn > 0 else par_in
            lit_col = "#D8B892" if (n_[0] * sgn * light > 0) else "#9A7E68"
            face_col = ("#B89474" if inner_vis else lit_col)
            o.append(Q([proj(Ap), proj(Aq), proj((Aq[0], Aq[1] + hgt, Aq[2])), proj((Ap[0], Ap[1] + hgt, Ap[2]))], hz(face_col, Zm)))
            # coping on top
            ins = -sgn * 0.5
            o.append(Q([proj((Ap[0], Ap[1] + hgt, Ap[2])), proj((Aq[0], Aq[1] + hgt, Aq[2])), proj(off((Aq[0], Aq[1] + hgt, Aq[2]), nb, ins)), proj(off((Ap[0], Ap[1] + hgt, Ap[2]), na, ins))],
                       hz("#E8D0AC", Zm)))
            if sgn > 0 and merlon_at(sm):
                mh = par_out
                o.append(Q([proj((Ap[0], Ap[1] + hgt, Ap[2])), proj((Aq[0], Aq[1] + hgt, Aq[2])), proj((Aq[0], Aq[1] + mh, Aq[2])), proj((Ap[0], Ap[1] + mh, Ap[2]))], hz(face_col, Zm)))
                o.append(Q([proj((Ap[0], Ap[1] + mh, Ap[2])), proj((Aq[0], Aq[1] + mh, Aq[2])), proj(off((Aq[0], Aq[1] + mh, Aq[2]), nb, ins)), proj(off((Ap[0], Ap[1] + mh, Ap[2]), na, ins))],
                           hz("#F2DCB6", Zm)))
                # the merlon's end faces (toward / away from us) give it thickness
                if not merlon_at(arcs[i + 1] + 0.01) or not merlon_at(arcs[i] - 0.01):
                    e = Aq if not merlon_at(arcs[i + 1] + 0.01) else Ap
                    nn_ = nb if e is Aq else na
                    o.append(Q([proj((e[0], e[1] + hgt, e[2])), proj((e[0], e[1] + mh, e[2])), proj(off((e[0], e[1] + mh, e[2]), nn_, ins)), proj(off((e[0], e[1] + hgt, e[2]), nn_, ins))],
                               hz("#7E6656", Zm)))
            return o
        cam_side_L = (ex - Lp[0]) * na[0] + (ez - Lp[2]) * na[1] < 0     # camera is inside (walkway side) of the left parapet
        cam_side_R = (ex - Rp[0]) * (-na[0]) + (ez - Rp[2]) * (-na[1]) < 0
        dL, dR = math.dist((ex, ey, ez), Lp), math.dist((ex, ey, ez), Rp)
        floor_vis = ey > (p[1] + q[1]) / 2
        far_first = [("L", 1, Lp, Lq, cam_side_L), ("R", -1, Rp, Rq, cam_side_R)]
        far_first.sort(key=lambda t_: -(dL if t_[0] == "L" else dR))
        g += parapet(far_first[0][1], far_first[0][2], far_first[0][3], na, far_first[0][4])
        # walkway: bricks, and steps where it climbs
        rise = (q[1] - p[1]) / max(0.01, math.hypot(q[0] - p[0], q[2] - p[2]))
        if floor_vis or True:
            fl = "#C2A688" if (i % 2 == 0 or abs(rise) < 0.12) else "#A68A70"
            if abs(rise) >= 0.12 and not floor_vis:
                fl = "#9A7E66"
            g.append(Q([proj(Lp), proj(Lq), proj(Rq), proj(Rp)], hz(fl, Zm)))
            if Zm < near_detail:
                a, b = proj(Lp), proj(Rp)
                g.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{hz("#6E5646", Zm)}" stroke-width="{max(0.4, 3.2 / Zm):.1f}" opacity="0.5"/>')
                if Zm < 14:
                    for f_ in (-0.66, -0.33, 0.0, 0.33, 0.66):
                        a, b = proj(off(p, na, hw * f_)), proj(off(q, nb, hw * f_))
                        g.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#7E6452" stroke-width="{max(0.4, 2 / Zm):.1f}" opacity="0.35"/>')
        g += parapet(far_first[1][1], far_first[1][2], far_first[1][3], na, far_first[1][4])
        items.append((Zm, "".join(g)))
    return items, pts, arcs, fr


def gw_tower(C, c, t, n, u, w=11.0, d=10.0, h=9.5, below=7.5, light=-1, haze=None, roof=False, seed=0):
    """A square two-storey watchtower astride the wall at centre c (floor level), axes t (along) and n (across)."""
    Z = c[2]
    def hz(col):
        if not haze:
            return col
        hc, amt = haze(Z)
        return mix(col, hc, amt)
    def at(a, b, y):          # a along, b across, y up from the floor
        return C(c[0] + t[0] * a + n[0] * b, c[1] + y, c[2] + t[1] * a + n[1] * b)
    faces = []
    for (a0, b0, a1, b1, nx, nz) in ((-w / 2, d / 2, w / 2, d / 2, n[0], n[1]), (w / 2, -d / 2, -w / 2, -d / 2, -n[0], -n[1]),
                                     (-w / 2, -d / 2, -w / 2, d / 2, -t[0], -t[1]), (w / 2, d / 2, w / 2, -d / 2, t[0], t[1])):
        cxw = c[0] + t[0] * (a0 + a1) / 2 + n[0] * (b0 + b1) / 2
        czw = c[2] + t[1] * (a0 + a1) / 2 + n[1] * (b0 + b1) / 2
        if nx * (0 - cxw) + nz * (0 - czw) > 0:
            faces.append((math.hypot(cxw, czw), a0, b0, a1, b1, nx))
    faces.sort(reverse=True)
    o = []
    for dist, a0, b0, a1, b1, nx in faces:
        lit = nx * light > 0
        col = "#D8B48A" if lit else "#9A7C66"
        o.append(Q([at(a0, b0, -below), at(a1, b1, -below), at(a1, b1, h), at(a0, b0, h)], hz(col)))
        o.append(Q([at(a0, b0, -below), at(a1, b1, -below), at(a1, b1, -below * 0.4), at(a0, b0, -below * 0.4)], hz(mix(col, "#7A7A70", 0.35))))
        for f_ in (0.12, 0.25, 0.38, 0.5, 0.62, 0.75, 0.88):
            yy = -below * 0.4 + (h + below * 0.4) * f_
            p_, q_ = at(a0, b0, yy), at(a1, b1, yy)
            o.append(f'<line x1="{p_[0]:.1f}" y1="{p_[1]:.1f}" x2="{q_[0]:.1f}" y2="{q_[1]:.1f}" stroke="#5A4436" stroke-width="{max(0.4, 2.5 / Z):.1f}" opacity="0.35"/>')
        # arched windows on the upper storey and the doorway at walkway level
        for j, fx in enumerate((0.22, 0.5, 0.78)):
            ca, cb = a0 + (a1 - a0) * fx, b0 + (b1 - b0) * fx
            hwid = 0.075
            pa, pb = a0 + (a1 - a0) * (fx - hwid), b0 + (b1 - b0) * (fx - hwid)
            qa, qb = a0 + (a1 - a0) * (fx + hwid), b0 + (b1 - b0) * (fx + hwid)
            y0, y1 = h * 0.42, h * 0.68
            arc = [at(pa, pb, y0), at(pa, pb, y1)]
            for k in range(1, 8):
                th = math.pi * k / 8
                aa = ca + (pa - ca) * math.cos(th)
                bb = cb + (pb - cb) * math.cos(th)
                arc.append(at(aa, bb, y1 + (qa - pa if abs(qa - pa) > 1e-6 else qb - pb) * 0 + abs(hwid * (w if abs(a1 - a0) > 1 else d)) * math.sin(th)))
            arc += [at(qa, qb, y1), at(qa, qb, y0)]
            o.append(Q(arc, "#2E2420"))
        da, db = (a0 + a1) / 2, (b0 + b1) / 2
        pa, pb = da - (a1 - a0) * 0.08, db - (b1 - b0) * 0.08
        qa, qb = da + (a1 - a0) * 0.08, db + (b1 - b0) * 0.08
        o.append(Q([at(pa, pb, 0), at(pa, pb, h * 0.22), at(da, db, h * 0.3), at(qa, qb, h * 0.22), at(qa, qb, 0)], "#2A201C"))
        # crenellated top
        for k in range(7):
            f0, f1 = k / 6.5, k / 6.5 + 0.08
            ma, mb = a0 + (a1 - a0) * f0, b0 + (b1 - b0) * f0
            na_, nb_ = a0 + (a1 - a0) * f1, b0 + (b1 - b0) * f1
            o.append(Q([at(ma, mb, h), at(na_, nb_, h), at(na_, nb_, h + 1.0), at(ma, mb, h + 1.0)], hz(col)))
        p_, q_ = at(a0, b0, h), at(a1, b1, h)
        o.append(f'<line x1="{p_[0]:.1f}" y1="{p_[1]:.1f}" x2="{q_[0]:.1f}" y2="{q_[1]:.1f}" stroke="{hz("#F2DCB6")}" stroke-width="{max(0.6, 5 / Z):.1f}"/>')
    if roof:   # a small hip-roofed pavilion on the platform
        rw, rd, rh = w * 0.42, d * 0.42, 2.6
        for dist, a0, b0, a1, b1, nx in faces:
            s0, s1 = rw / (w / 2), rd / (d / 2)
            o.append(Q([at(a0 * s0, b0 * s1, h), at(a1 * s0, b1 * s1, h), at(a1 * s0, b1 * s1, h + rh), at(a0 * s0, b0 * s1, h + rh)], "#8A3A2A" if nx * light > 0 else "#5A2A22"))
        for dist, a0, b0, a1, b1, nx in faces:
            s0, s1 = rw / (w / 2) * 1.35, rd / (d / 2) * 1.35
            o.append(Q([at(a0 * s0, b0 * s1, h + rh), at(a1 * s0, b1 * s1, h + rh), at(0, 0, h + rh + 2.4)], "#4A4A52" if nx * light > 0 else "#2E2E36"))
        tp = at(0, 0, h + rh + 2.4)
        o.append(f'<circle cx="{tp[0]:.1f}" cy="{tp[1]:.1f}" r="{max(1, 4 / Z):.1f}" fill="#2E2E36"/>')
    return "".join(o)


def great_wall():
    from figures import person
    u = "gwall"
    C = Cam(f=330, cx=300, vpy=214, eye=4.6)
    L = -1   # morning sun low on the left
    out = [defs(
        lg(f"{u}-sky", [(0, "#7EA6CE"), (0.45, "#B8CCDC"), (0.75, "#F2D6BC"), (1, "#FCE6C8")], 0, 40, 0, 240, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#9AAAC0"), (1, "#C8CCD4")], 0, 140, 0, 250, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(70, 168, 320, "#FFE2BC", f"{u}-sun", 0.85))
    out.append(glow(70, 168, 46, "#FFF6E4", f"{u}-sun2", 1.0))
    out.append('<circle cx="70" cy="168" r="13" fill="#FFF8EC"/>')
    for x, y, w in ((230, 104, 120), (480, 86, 150), (540, 128, 70), (170, 132, 60)):
        out.append(streak_cloud(x, y, w, "#FFF2E2", 0.55, 3.4))
        out.append(streak_cloud(x - 20, y + 3, w * 0.5, "#FFE0CC", 0.5, 1.4))

    def haze(Z):
        return "#E2E0E2", max(0.0, min(0.55, (Z - 50) / 260))

    # far ridges, palest and bluest, with the wall as a thread along their crests and mist pooled between them
    far_layers = [([(-10, 196), (70, 184), (150, 194), (230, 172), (310, 186), (400, 166), (480, 180), (560, 170), (610, 178)], "#B4BCCC", 0.6, (380, 610), [430, 520, 590]),
                  ([(-10, 214), (90, 200), (170, 214), (260, 198), (350, 212), (440, 194), (530, 206), (610, 200)], "#A0A8B4", 0.9, (-10, 230), [30, 120, 200])]
    for i, (pts, col, s, (xa, xb), tw) in enumerate(far_layers):
        poly, line = ridge_poly(pts, 300 + i, amp=6, fill=col)
        out.append(poly)
        out.append(f'<clipPath id="{u}-l{i}"><polygon points="{P(line + [(610, 444), (-10, 444)])}"/></clipPath>')
        out.append(f'<g clip-path="url(#{u}-l{i})">' + blobs(90, 310 + i, (-10, min(p[1] for p in line), 610, max(p[1] for p in line) + 30),
                                                           [mix(col, "#B87A5A", 0.25), mix(col, "#FFE6C0", 0.3), mix(col, "#6E6A5A", 0.2)], r=(2, 5), opacity=(0.4, 0.8)) + "</g>")
        out.append(far_wall(line, xa, xb, s, tw, mix(col, "#C8A884", 0.55), mix(col, "#FFF0D8", 0.75), 320 + i))
        out.append(mist(300 + (i * 2 - 1) * 140, max(p[1] for p in line) + 8, 420, 22, "#FFF6EA", f"{u}-fm{i}", 0.9))
    # the wall itself: from our feet down into a saddle, up a steep ridge to a tower, on along the crest to another
    ctrl = [(0.6, -0.2, 0.8), (1.2, -0.6, 4.0), (1.4, -1.6, 9.0), (0.6, -3.2, 15.0), (-1.8, -5.0, 22.0), (-5.0, -6.0, 30.0), (-7.6, -5.0, 38.0),
            (-9.0, -1.0, 47.0), (-8.6, 4.0, 57.0), (-5.6, 8.6, 68.0), (-1.0, 11.0, 80.0), (6.0, 10.6, 94.0), (14.0, 8.0, 110.0), (24.0, 9.0, 128.0),
            (34.0, 14.0, 146.0), (44.0, 20.0, 166.0), (52.0, 22.0, 184.0), (62.0, 21.0, 204.0)]
    pts, arcs = gw_spline(ctrl)
    fr = gw_frames(pts)
    def at_arc(target):
        for i in range(len(arcs) - 1):
            if arcs[i] <= target <= arcs[i + 1]:
                return i
        return len(arcs) - 2
    # towers on the two crests (by arc length of the nearest sample to the control point)
    def nearest_arc(cp):
        j = min(range(len(pts)), key=lambda k_: math.dist(pts[k_], cp))
        return arcs[j], j
    s1, j1 = nearest_arc((-1.0, 11.0, 80.0))
    s2, j2 = nearest_arc((52.0, 22.0, 184.0))
    items, pts, arcs, fr = gw_wall(C, ctrl, u, hw=2.6, towers=(), skip=((s1 - 5.5, s1 + 5.5), (s2 - 5, s2 + 5)), seed=7, haze=haze, light=L)
    for j, roof in ((j1, True), (j2, False)):
        t, n = fr[j]
        items.append((pts[j][2], gw_tower(C, pts[j], t, n, u, haze=haze, light=L, roof=roof)))
    # mist drifting through the saddle behind the near ridge
    items.append((40.5, mist(150, 300, 220, 26, "#FFF6EA", f"{u}-sm1", 0.75)))
    items.append((90, mist(470, 250, 220, 20, "#FFF6EA", f"{u}-sm2", 0.85)))
    # two hikers on the walkway coming down toward the saddle
    for Zh, dx, pal, sd, fac in ((9.2, -0.5, {"form": "f", "top_kind": "jacket", "top": "#C8443A", "bottom_kind": "trousers", "bottom": "#2E3A58", "hair_style": "ponytail", "pack": True}, 3, -1),
                                 (11.0, 0.7, {"form": "m", "top_kind": "jacket", "top": "#2E6A8A", "bottom_kind": "trousers", "bottom": "#4A4038", "hair_style": "short", "hat_kind": "cap", "hat": "#E8B040", "pack": True}, 5, -1)):
        j = min(range(len(pts)), key=lambda k_: abs(pts[k_][2] - Zh))
        t, n = fr[j]
        base = (pts[j][0] + n[0] * dx, pts[j][1], pts[j][2] + n[1] * dx)
        x, y = C(*base)
        items.append((base[2] - 0.01, person(x, y, 1.72 * C.f / base[2], "hiker", fac, pal, seed=sd, light=L, rim="#FFE2B8")))
    for Z, svg in sorted(items, key=lambda it: -it[0]):
        out.append(svg)
    # a few swallows in the clear morning air
    out.append(flock([(360, 130, 8), (378, 140, 6), (346, 146, 5)], "#4A4A5A", 1.6))
    return "\n".join(out)


def tree_crowns(n, seed, box, r, dark, mid, lit, light=-1, grow=True):
    """A hillside of broadleaf tree crowns: each a dark base, a body and a sunlit cap, bigger toward the viewer."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    items = sorted(((rnd.uniform(y0, y1), rnd.uniform(x0, x1)) for _ in range(n)))
    o = []
    for y, x in items:
        k = (0.45 + 0.55 * (y - y0) / max(1, y1 - y0)) if grow else 1
        rr = rnd.uniform(*r) * k
        t = rnd.uniform(-0.18, 0.18)
        m = mix(mid, "#C8C060", t) if t > 0 else mix(mid, dark, -t)
        o.append(f'<circle cx="{x:.1f}" cy="{y + rr * 0.3:.1f}" r="{rr:.1f}" fill="{dark}"/>'
                 f'<circle cx="{x - light * rr * 0.08:.1f}" cy="{y:.1f}" r="{rr * 0.88:.1f}" fill="{m}"/>'
                 f'<circle cx="{x + light * rr * 0.3:.1f}" cy="{y - rr * 0.34:.1f}" r="{rr * 0.48:.1f}" fill="{lit}" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>')
    return "".join(o)


def flowers_on(n, seed, box):
    return dots(n, seed, box, "#F2E2A0", r=(1.2, 2.2), opacity=(0.8, 1)) + dots(n // 2, seed + 1, box, "#E88AA8", r=(1.2, 2.0), opacity=(0.8, 1))


# ================================================================ HA LONG BAY — limestone karsts and a junk at sunset
def karst_path(cx, base, w, h, seed, lean=0.0):
    """Outline of a limestone tower: sheer flanks that bulge and undercut at random, tapering to a lumpy crown."""
    rnd = random.Random(seed)
    L, R = [], []
    n = 11
    taper_l, taper_r = rnd.uniform(0.08, 0.26), rnd.uniform(0.08, 0.26)
    for i in range(n + 1):
        t = i / n
        y = base - h * t * 0.84
        sway = lean * h * t * 0.12
        bl = (math.sin(t * math.pi * rnd.uniform(0.8, 1.6) + rnd.uniform(0, 3)) * 0.07 + rnd.uniform(-0.035, 0.035)) * w
        br = (math.sin(t * math.pi * rnd.uniform(0.8, 1.6) + rnd.uniform(0, 3)) * 0.07 + rnd.uniform(-0.035, 0.035)) * w
        L.append((cx - w / 2 + w * taper_l * t ** 1.5 - bl + sway, y))
        R.append((cx + w / 2 - w * taper_r * t ** 1.5 + br + sway, y))
    top = []
    m = 6
    for j in range(1, m):
        t = j / m
        x = lerp(L[-1][0], R[-1][0], t)
        top.append((x, base - h * (0.86 + 0.14 * math.sin(t * math.pi) ** 0.7) + rnd.uniform(-0.035, 0.035) * h))
    pts = [(cx - w / 2 - w * 0.04, base + 2)] + L + top + R[::-1] + [(cx + w / 2 + w * 0.04, base + 2)]
    return smooth(pts) + " Z"


def karst(cx, base, w, h, seed, u, fill, rim=None, veg=None, streak_cols=None, lean=0.0, rim_w=2.0):
    d = karst_path(cx, base, w, h, seed, lean)
    o = [f'<path d="{d}" fill="{fill}"/>']
    if rim or veg or streak_cols:
        o.append(f'<clipPath id="{u}"><path d="{d}"/></clipPath><g clip-path="url(#{u})">')
        if streak_cols:
            o.append(streaks(int(w / 3), seed + 1, (cx - w / 2, base - h, cx + w / 2, base), streak_cols, w=(1.5, 4), length=(h * 0.2, h * 0.6), opacity=(0.25, 0.6), slant=0.05))
        if veg:
            # shrubs clinging to the crown and to ledges
            o.append(blobs(int(w * 1.6), seed + 2, (cx - w / 2, base - h * 1.02, cx + w / 2, base - h * 0.74), veg, r=(w * 0.025, w * 0.06), opacity=(0.8, 1), squash=0.75))
            o.append(blobs(int(w * 0.5), seed + 3, (cx - w / 2, base - h * 0.72, cx + w / 2, base - h * 0.15), veg, r=(w * 0.015, w * 0.04), opacity=(0.5, 0.9), squash=0.45))
        if rim:
            o.append(f'<path d="{d}" fill="none" stroke="{rim}" stroke-width="{rim_w * 2:.1f}" opacity="0.85" transform="translate({rim_w:.1f} 0)"/>')
        o.append("</g>")
    return "".join(o)


def halong_junk(x, wl, k, u):
    """Ha Long cruise junk silhouetted against the sun: dark hull with lit cabin windows, rust-red battened sails."""
    o = []
    L = 70 * k
    o.append(f'<g opacity="0.45">' + ripple_reflection(40, 901, x, wl + 3, wl + 40 * k, 60 * k, ["#2A1A30", "#4A2A3A"], op=(0.5, 0.9)) + "</g>")
    o.append(ripple_reflection(18, 902, x - 10 * k, wl + 3, wl + 24 * k, 40 * k, ["#FFC070", "#FFE0A0"], op=(0.4, 0.9)))
    for mx, H, aw, fw in ((x - 8 * k, 96 * k, 34 * k, 12 * k), (x + 30 * k, 78 * k, 26 * k, 9 * k), (x - 46 * k, 54 * k, 18 * k, 7 * k)):
        o.append(f'<line x1="{mx:.1f}" y1="{wl - 14 * k:.1f}" x2="{mx:.1f}" y2="{wl - H - 6 * k:.1f}" stroke="#1E1218" stroke-width="{1.6 * k:.1f}"/>')
        s_, _ = junk_sail(mx, wl - 24 * k, wl - H, fw, aw, k, f"{u}-s{int(mx)}", f"url(#{u}-sail)", batten="#3A1410")
        o.append(s_)
    # hull and two decks of cabins with warm windows
    o.append(f'<path d="M {x - L:.1f} {wl - 22 * k:.1f} L {x + L - 10 * k:.1f} {wl - 20 * k:.1f} Q {x + L + 4 * k:.1f} {wl - 22 * k:.1f} {x + L + 8 * k:.1f} {wl - 28 * k:.1f} '
             f'L {x + L:.1f} {wl - 6 * k:.1f} Q {x:.1f} {wl + 3 * k:.1f} {x - L + 4 * k:.1f} {wl - 2 * k:.1f} Z" fill="#24141C"/>')
    o.append(rect(x - L + 6 * k, wl - 32 * k, (2 * L - 22 * k), 11 * k, "#2E1A22"))
    o.append("".join(rect(x - L + 10 * k + j * 9 * k, wl - 29 * k, 5 * k, 4.5 * k, "#FFC878") for j in range(int((2 * L - 30 * k) / (9 * k)))))
    o.append("".join(rect(x - L + 10 * k + j * 9 * k, wl - 15 * k, 4 * k, 3 * k, "#F2A860", ' opacity="0.8"') for j in range(int((2 * L - 30 * k) / (9 * k)))))
    o.append(f'<path d="M {x - L:.1f} {wl - 22 * k:.1f} L {x + L - 10 * k:.1f} {wl - 20 * k:.1f}" stroke="#F2A060" stroke-width="{0.9 * k:.1f}" opacity="0.8"/>')
    return "".join(o)


def sampan(x, wl, k):
    """Small bamboo-and-plank rowing boat; a rower in a conical hat stands at the stern working one long oar."""
    o = [f'<path d="M {x - 34 * k:.1f} {wl - 6 * k:.1f} Q {x:.1f} {wl + 4 * k:.1f} {x + 36 * k:.1f} {wl - 8 * k:.1f} L {x + 30 * k:.1f} {wl - 2 * k:.1f} Q {x:.1f} {wl + 6 * k:.1f} {x - 30 * k:.1f} {wl - 1 * k:.1f} Z" fill="#1E1418"/>',
         f'<path d="M {x - 34 * k:.1f} {wl - 6 * k:.1f} Q {x:.1f} {wl + 4 * k:.1f} {x + 36 * k:.1f} {wl - 8 * k:.1f}" stroke="#F2A060" stroke-width="{1.2 * k:.1f}" fill="none" opacity="0.8"/>']
    # baskets of the catch and a hooped canopy
    o.append(f'<path d="M {x - 6 * k:.1f} {wl - 4 * k:.1f} Q {x + 4 * k:.1f} {wl - 20 * k:.1f} {x + 16 * k:.1f} {wl - 5 * k:.1f} Z" fill="#2A1C20"/>')
    o.append(f'<circle cx="{x - 14 * k:.1f}" cy="{wl - 6 * k:.1f}" r="{3.6 * k:.1f}" fill="#2A1C20"/>')
    rx = x - 26 * k
    o.append(f'<path d="M {rx - 3 * k:.1f} {wl - 4 * k:.1f} L {rx - 2 * k:.1f} {wl - 20 * k:.1f} L {rx + 3 * k:.1f} {wl - 20 * k:.1f} L {rx + 3 * k:.1f} {wl - 4 * k:.1f} Z" fill="#1E1418"/>'
             f'<path d="M {rx - 3 * k:.1f} {wl - 20 * k:.1f} Q {rx:.1f} {wl - 28 * k:.1f} {rx + 3 * k:.1f} {wl - 20 * k:.1f} Z" fill="#1E1418"/>'
             f'<circle cx="{rx:.1f}" cy="{wl - 28 * k:.1f}" r="{2.6 * k:.1f}" fill="#1E1418"/>'
             f'<path d="M {rx - 8 * k:.1f} {wl - 28 * k:.1f} L {rx:.1f} {wl - 35 * k:.1f} L {rx + 8 * k:.1f} {wl - 28 * k:.1f} Z" fill="#2A1C20"/>'
             f'<path d="M {rx:.1f} {wl - 35 * k:.1f} L {rx + 8 * k:.1f} {wl - 28 * k:.1f}" stroke="#FFB070" stroke-width="{1.1 * k:.1f}"/>'
             f'<line x1="{rx + 2 * k:.1f}" y1="{wl - 18 * k:.1f}" x2="{rx - 24 * k:.1f}" y2="{wl + 8 * k:.1f}" stroke="#1E1418" stroke-width="{1.4 * k:.1f}"/>')
    o.append(f'<path d="M {rx - 30 * k:.1f} {wl + 7 * k:.1f} q 6 -2 12 0" stroke="#FFD0A0" stroke-width="{1 * k:.1f}" fill="none" opacity="0.7"/>')
    return "".join(o)


def ha_long_bay():
    u = "halong"
    wl = 300
    out = [defs(
        lg(f"{u}-sky", [(0, "#2E1E52"), (0.3, "#6A2E6A"), (0.55, "#C8466A"), (0.78, "#F2864A"), (0.92, "#F8B85A"), (1, "#FCD48A")], 0, 40, 0, wl, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#F6B060"), (0.12, "#D86A5A"), (0.45, "#6A2E5A"), (1, "#24183A")], 0, wl, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#B8607E"), (1, "#D88A88")], 0, 0, 0, 1),
        lg(f"{u}-mid", [(0, "#6A3062"), (1, "#8A4A6E")], 0, 0, 0, 1),
        lg(f"{u}-near", [(0, "#2E1A36"), (1, "#3E2440")], 0, 0, 0, 1),
        lg(f"{u}-sail", [(0, "#7A2A1E"), (0.6, "#B84A2A"), (1, "#E8823A")], 0, 0, 0, 1),
    )]
    out.append(f'<rect width="600" height="{wl + 2}" fill="url(#{u}-sky)"/>')
    sx, sy = 236, 262
    out.append(glow(sx, sy, 300, "#FFB060", f"{u}-g1", 0.75))
    out.append(glow(sx, sy, 70, "#FFF0C0", f"{u}-g2", 0.95))
    out.append(f'<circle cx="{sx}" cy="{sy}" r="22" fill="#FFF4D0"/>')
    for x, y, w, c in ((120, 120, 120, "#E86A7A"), (460, 100, 140, "#D85A7A"), (520, 140, 90, "#F2867A"), (330, 180, 110, "#F8A070"), (90, 196, 70, "#FAB27A"), (480, 210, 60, "#FAC080")):
        out.append(streak_cloud(x, y, w, c, 0.7, 4))
        out.append(streak_cloud(x - w * 0.2, y + 3, w * 0.55, "#FFD8A8", 0.6, 1.4))
    # far karsts, pale in the haze
    for i, (cx, w, h) in enumerate(((40, 60, 70), (110, 46, 52), (330, 50, 64), (380, 34, 40), (520, 70, 80), (590, 40, 50), (440, 30, 30))):
        out.append(karst(cx, wl, w, h, 10 + i, f"{u}-f{i}", f"url(#{u}-far)"))
    out.append(mist(300, wl - 4, 360, 14, "#FFC8A0", f"{u}-m1", 0.7))
    # middle group
    for i, (cx, w, h, lean) in enumerate(((150, 70, 130, 0.1), (196, 44, 96, -0.1), (470, 90, 150, 0.05), (540, 60, 112, -0.05), (290, 36, 60, 0))):
        out.append(karst(cx, wl, w, h, 30 + i, f"{u}-md{i}", f"url(#{u}-mid)", rim="#FF9A6A", veg=["#4A2A4A", "#5A3A50"], streak_cols=["#4A2050", "#9A5A7A"], lean=lean, rim_w=1.4))
    # near giants framing left and right, rim-lit toward the sun
    out.append(karst(36, wl + 2, 150, 250, 51, f"{u}-n1", f"url(#{u}-near)", rim="#F2864A", veg=["#1A2420", "#22302A", "#2E3E30"], streak_cols=["#1A1024", "#5A3A50"], lean=0.1, rim_w=2.2))
    out.append(karst(560, wl + 2, 130, 222, 52, f"{u}-n2", f"url(#{u}-near)", rim=None, veg=["#1A2420", "#22302A", "#2E3E30"], streak_cols=["#1A1024", "#5A3A50"], lean=-0.1))
    out.append(f'<path d="{karst_path(560, wl + 2, 130, 222, 52, -0.1)}" fill="none" stroke="#F2864A" stroke-width="3" opacity="0.5" clip-path="url(#{u}-n2)" transform="translate(-1.5 0)"/>')
    # the bay: sky colours, a gold path under the sun, mirrored karsts broken by ripples
    out.append(rect(-10, wl, 620, 150, f"url(#{u}-sea)"))
    refl = []
    for cx, w, h, f, op in ((36, 150, 250, "#24142C", 0.7), (560, 130, 222, "#24142C", 0.7), (150, 70, 130, "#4A2050", 0.55), (470, 90, 150, "#4A2050", 0.55), (540, 60, 112, "#4A2050", 0.5)):
        refl.append(f'<path d="{karst_path(cx, wl, w, h, 0 if False else {36: 51, 560: 52, 150: 30, 470: 32, 540: 33}[cx], 0)}" fill="{f}" opacity="{op}" transform="translate(0 {2 * wl}) scale(1 -1)"/>')
    out.append(f'<clipPath id="{u}-sc"><rect x="-10" y="{wl}" width="620" height="150"/></clipPath><g clip-path="url(#{u}-sc)">{"".join(refl)}</g>')
    out.append(ripple_reflection(140, 903, sx, wl + 2, 444, 70, ["#FFE6A0", "#FFC070", "#FFF4D0", "#F2864A"], op=(0.4, 1), spread=1.2))
    out.append(water_lines(160, 904, (-10, wl + 2, 610, 444), ["#F2A070", "#2A1A3A", "#FFD0A0", "#4A2A4A"], w=(10, 50), h=(1, 2.2), opacity=(0.25, 0.7)))
    out.append(halong_junk(408, 336, 1.25, u))
    out.append(sampan(176, 404, 1.25))
    out.append(ripple_reflection(16, 905, 170, 408, 430, 50, ["#FFD0A0", "#1E1418"], op=(0.3, 0.7)))
    out.append(flock([(300, 150, 9), (318, 160, 7), (334, 148, 6), (420, 186, 6)], "#3A1A3A", 1.7))
    return "\n".join(out)


# ================================================================ build
BUILD = {
    "taj-mahal": (taj_mahal, "TAJ MAHAL", "INDIA · AGRA", "#2A2A52", "#F4B49A", "#FFF4EC", "#F6C9A8"),
    "bali": (bali, "BALI", "INDONESIA · ASIA", "#1F4A30", "#E8C35A", "#FFF6E0", "#E8D58A"),
    "hong-kong": (hong_kong, "HONG KONG", "CHINA · ASIA", "#12183A", "#E8463A", "#FFF2EC", "#8ED8F0"),
    "kyoto": (kyoto, "KYOTO", "JAPAN · KYOTO", "#26201C", "#E8502E", "#FFF2E6", "#F28A5A"),
    "tokyo": (tokyo, "TOKYO", "JAPAN · TOKYO", "#1A1230", "#FF4A8A", "#FFF2F6", "#7EE8F0"),
    "seoul": (seoul, "SEOUL", "SOUTH KOREA · ASIA", "#5A1E24", "#F2C04A", "#FFF4E6", "#F2C890"),
    "great-wall": (great_wall, "GREAT WALL", "CHINA · ASIA", "#2A3A4E", "#E8C08A", "#FFF4E6", "#C8D8C0"),
    "ha-long-bay": (ha_long_bay, "HA LONG BAY", "VIETNAM · ASIA", "#3A1E2A", "#F29A4A", "#FFF0E6", "#F6B88A"),
    "bangkok": (bangkok, "BANGKOK", "THAILAND · ASIA", "#0E3A3A", "#E8B04A", "#FFF4DC", "#E8C878"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("world", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
