"""World Places, painted edition (batch AO): Cancún, Patagonia, Banff, Québec City, Bora Bora and Milford Sound.

Same painterly approach as world_painted.py: each poster is a small gouache-style painting with its own hour of
the day, a light direction, atmospheric depth, reflections and truthful details of the place.
Run: python3 world_new_ao.py [slug ...]
"""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from places_painted import Cam
from places_new_e import (massif, con, trees_on, forest_fill, inside, leafy, mirror, ripple_lines, birds_v, blob_pts,
                          strokes_h, patches, canopy, forest_mosaic, boulder)
from world_painted import cumulus, streak_cloud, gulls, mix, Q, water_lines, figure
from common import save, esc, measure, fit_size, MONO
from poster import ANTON, ART_H


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


def Pi(pts):
    return " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)


# ================================================================ shared helpers
def qpt(p0, p1, p2, t):
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])


def qtan(p0, p1, p2, t):
    dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
    dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
    n = math.hypot(dx, dy) or 1
    return dx / n, dy / n


def frond(p0, ang, L, droop, leaf, rachis, cols, seed, sw=1.8, lift=0.22, n=20, spread=58, grav=0.9, rw=2.2, op=1.0):
    """Pinnate frond (coconut palm or tree fern): an arching rachis from p0 heading `ang` degrees (0 = right,
    -90 = up), its tip drooping by `droop` px, with paired leaflets that hang under their own weight."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    p2 = (p0[0] + dx * L, p0[1] + dy * L + droop)
    p1 = (p0[0] + dx * L * 0.55, p0[1] + dy * L * 0.55 - L * lift)
    out = [f'<path d="M {p0[0]:.1f} {p0[1]:.1f} Q {p1[0]:.1f} {p1[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}" stroke="{rachis}" stroke-width="{rw:.1f}"/>']
    for i in range(n):
        t = 0.1 + 0.9 * i / n
        x, y = qpt(p0, p1, p2, t)
        tx, ty = qtan(p0, p1, p2, t)
        l = leaf * (math.sin(math.pi * min(0.98, 0.2 + t * 0.85)) ** 0.6) * rnd.uniform(0.8, 1.12)
        for side in (-1, 1):
            s = math.radians(spread) * side
            vx = tx * math.cos(s) - ty * math.sin(s)
            vy = tx * math.sin(s) + ty * math.cos(s) + grav
            nn = math.hypot(vx, vy) or 1
            vx, vy = vx / nn, vy / nn
            ex, ey = x + vx * l, y + vy * l
            mx, my = x + vx * l * 0.5 + tx * l * 0.2, y + vy * l * 0.5 + ty * l * 0.2 - l * 0.12
            out.append(f'<path d="M {x:.1f} {y:.1f} Q {mx:.1f} {my:.1f} {ex:.1f} {ey:.1f}" stroke="{rnd.choice(cols)}"/>')
    return f'<g fill="none" stroke-width="{sw}" stroke-linecap="round" opacity="{op}">' + "".join(out) + "</g>"


def coco_palm(x, base, h, lean, seed, light=1, trunk=("#7A6450", "#B49A78", "#E6D2A8"), dark=("#1A3A2A", "#24503A"),
              mid=("#2E6A3A", "#3A7A40", "#46883E"), lit=("#7AB04A", "#A8CC5A", "#C8E07A"), nuts=True, k=1.0):
    """Coconut palm: a curved ringed trunk, lit on one side, under a crown of arching pinnate fronds.
    light = 1 when the sun is on the right."""
    rnd = random.Random(seed)
    p0 = (x, base)
    p2 = (x + lean * h, base - h)
    p1 = (x + lean * h * 0.15, base - h * 0.55)
    w0, w1 = h * 0.045 * k, h * 0.026 * k
    L, R, C = [], [], []
    N = 30
    for i in range(N + 1):
        t = i / N
        px, py = qpt(p0, p1, p2, t)
        tx, ty = qtan(p0, p1, p2, t)
        w = w0 + (w1 - w0) * t + (h * 0.02 * (1 - t) ** 6)
        L.append((px + ty * w, py - tx * w))
        R.append((px - ty * w, py + tx * w))
        C.append((px, py))
    out = [f'<polygon points="{P(L + R[::-1])}" fill="{trunk[1]}"/>']
    shade, litside = (L, R) if light > 0 else (R, L)
    out.append(f'<polygon points="{P(shade + C[::-1])}" fill="{trunk[0]}" opacity="0.8"/>')
    band = [((a[0] + b[0] * 2) / 3, (a[1] + b[1] * 2) / 3) for a, b in zip(C, litside)]
    out.append(f'<polygon points="{P(band + litside[::-1])}" fill="{trunk[2]}" opacity="0.75"/>')
    rings = []
    for i in range(3, N, 1):
        a, b = L[i], R[i]
        rings.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} Q {(a[0] + b[0]) / 2 + 1:.1f} {(a[1] + b[1]) / 2 + 2.5:.1f} {b[0]:.1f} {b[1]:.1f}"/>')
    out.append(f'<g fill="none" stroke="{trunk[0]}" stroke-width="1.3" opacity="0.6">' + "".join(rings) + "</g>")
    tx, ty = p2
    Lf = h * 0.36
    # back fronds (dark), then the crown, then lit front fronds
    for i, ang in enumerate((-120, -60, -150, -30, 200, -10 + 180)):
        out.append(frond((tx, ty), ang + rnd.uniform(-8, 8), Lf * rnd.uniform(0.75, 0.95), Lf * (0.25 + 0.3 * abs(math.cos(math.radians(ang)))),
                         Lf * 0.3, dark[0], dark, seed * 10 + i, sw=2.0 * k, rw=2.0 * k, n=15, spread=42, grav=1.5))
    if nuts:
        for j in range(5):
            cx_, cy_ = tx + rnd.uniform(-h * 0.03, h * 0.03), ty + h * 0.025 + rnd.uniform(-2, h * 0.02)
            r = h * 0.022 * k
            out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{r:.1f}" fill="#5A6A2E"/><circle cx="{cx_ + light * r * 0.35:.1f}" cy="{cy_ - r * 0.35:.1f}" r="{r * 0.45:.1f}" fill="#A8B04A" opacity="0.8"/>')
    angs = (-100, -140, -45, -170, -5, 25, 155, 60, 120, 95)
    for i, ang in enumerate(angs):
        ang += rnd.uniform(-8, 8)
        sunny = math.cos(math.radians(ang)) * light > -0.3 and math.sin(math.radians(ang)) < 0.5
        cols = lit if sunny else mid
        rach = mid[0] if sunny else dark[1]
        horiz = abs(math.cos(math.radians(ang)))
        out.append(frond((tx, ty), ang, Lf * rnd.uniform(0.85, 1.08), Lf * (0.2 + 0.45 * horiz), Lf * 0.32, rach, cols, seed * 10 + 20 + i,
                         sw=2.2 * k, rw=2.4 * k, n=16, spread=40, grav=1.5))
    return "".join(out)


def sparkle(x, y, r, color="#FFFFFF", op=0.9):
    return (f'<path d="M {x} {y - r} L {x + r * 0.22} {y - r * 0.22} L {x + r} {y} L {x + r * 0.22} {y + r * 0.22} L {x} {y + r} '
            f'L {x - r * 0.22} {y + r * 0.22} L {x - r} {y} L {x - r * 0.22} {y - r * 0.22} Z" fill="{color}" opacity="{op}"/>')


def frigate(x, y, s, col="#1E2436"):
    """Magnificent frigatebird soaring: long angular crooked wings and a deeply forked tail."""
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M 0 0 L -10 -4 L -22 -2 L -34 4 L -22 0 L -10 2 L -2 4 '
            f'L -3 10 L 0 6 L 3 10 L 2 4 L 10 2 L 22 0 L 34 4 L 22 -2 L 10 -4 Z" fill="{col}"/></g>')


# ================================================================ CANCÚN — a palapa on the white sand, the Caribbean at midday
def palapa(cx, apex, eave, rx, post_base, u, light=1):
    """Thatched beach palapa: a single pole under a cone of layered palm thatch with a ragged fringe."""
    ry = rx * 0.16
    rnd = random.Random(7)
    front = [(cx + rx * math.cos(math.radians(a)), eave + ry * math.sin(math.radians(a))) for a in range(0, 181, 6)]
    fringe = []
    for i, (fx, fy) in enumerate(front):
        fringe.append((fx, fy))
        if 0 < i < len(front) - 1:
            fringe.append((fx - 2, fy + rnd.uniform(3, 9)))
    roof = [(cx, apex)] + fringe + [(cx - rx, eave)]
    x1, x2 = (cx - rx, cx + rx) if light > 0 else (cx + rx, cx - rx)
    out = [defs(lg(f"{u}-th", [(0, "#7A5430"), (0.45, "#B88A4E"), (0.8, "#E2BE80"), (1, "#F2D49A")], x1, 0, x2, 0, units="userSpaceOnUse"),
                f'<clipPath id="{u}-rc"><polygon points="{P(roof)}"/></clipPath>')]
    # pole and its shadow on the sand
    shp = []
    for a in range(0, 360, 6):
        k_ = 1.0 if a % 12 else 0.9
        shp.append((cx - light * 26 + rx * 1.05 * k_ * math.cos(math.radians(a)), post_base + 8 + ry * 1.1 * k_ * math.sin(math.radians(a))))
    out.append(f'<polygon points="{P(shp)}" fill="#7E8CC0" opacity="0.3"/>')
    out.append(f'<path d="M {cx - 5} {eave} L {cx - 6.5} {post_base} L {cx + 6.5} {post_base} L {cx + 5} {eave} Z" fill="#8A6444"/>'
               f'<path d="M {cx + 1} {eave} L {cx + 1} {post_base} L {cx + 6.5 * light} {post_base} L {cx + 5 * light} {eave} Z" fill="#D2AA78" opacity="0.8"/>')
    out.append('<g stroke="#5A3E2A" stroke-width="1.2" opacity="0.6">' + "".join(
        f'<line x1="{cx - 5}" y1="{y:.0f}" x2="{cx + 5}" y2="{y + 2:.0f}"/>' for y in range(int(eave) + 12, int(post_base), 14)) + "</g>")
    # underside seen in shadow
    out.append(f'<ellipse cx="{cx}" cy="{eave}" rx="{rx * 0.98:.1f}" ry="{ry:.1f}" fill="#4A3220"/>')
    out.append(f'<polygon points="{P(roof)}" fill="url(#{u}-th)"/>')
    g = []
    # radiating thatch strands
    for i in range(150):
        a = rnd.uniform(0, 180)
        ex = cx + rx * math.cos(math.radians(a)) * rnd.uniform(0.9, 1.02)
        ey = eave + ry * math.sin(math.radians(a)) + rnd.uniform(0, 8)
        sx = cx + (ex - cx) * rnd.uniform(0.0, 0.6)
        sy = apex + (ey - apex) * ((sx - cx) / (ex - cx) if ex != cx else 0)
        col = rnd.choice(["#6A4626", "#8A6036", "#F6DCA2", "#C8985A", "#FFE8B0", "#5A3A20"])
        g.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{col}" stroke-width="{rnd.uniform(0.9, 2):.1f}" opacity="{rnd.uniform(0.3, 0.75):.2f}"/>')
    # tiers of thatch, each with a shadowed lip
    for k, f in enumerate((0.42, 0.68, 0.88)):
        yy = apex + (eave - apex) * f
        rr = rx * f
        arc = [(cx + rr * math.cos(math.radians(a)), yy + ry * f * math.sin(math.radians(a)) + rnd.uniform(-1, 1)) for a in range(0, 181, 8)]
        g.append(f'<polyline points="{P(arc)}" fill="none" stroke="#4A2E18" stroke-width="3" opacity="0.4"/>')
        g.append(f'<polyline points="{P([(px_, py_ - 2.5) for px_, py_ in arc])}" fill="none" stroke="#FFE6B0" stroke-width="1.4" opacity="0.5"/>')
    g.append(f'<polygon points="{P([(cx, apex), (cx - rx, eave), (cx - rx * 0.4, eave + ry)])}" fill="#3A2614" opacity="{0.22 if light > 0 else 0}"/>')
    out.append(f'<g clip-path="url(#{u}-rc)">' + "".join(g) + "</g>")
    # little topknot
    out.append(f'<path d="M {cx - 6} {apex + 6} L {cx} {apex - 8} L {cx + 6} {apex + 6} Z" fill="#7A5430"/><path d="M {cx} {apex - 8} L {cx + 6} {apex + 6} L {cx + 2} {apex + 6} Z" fill="#E2BE80"/>')
    return "".join(out)


def hammock(a, b, sag, u, cols=("#E8443A", "#F6B53A", "#2EB0B8", "#E8609A", "#F4EEE0", "#6A4AA8")):
    """Yucatán-style striped hammock slung between a and b (cord ends): a fan of strings, then the striped bed."""
    ax, ay = a
    bx, by = b
    L = bx - ax
    s0 = (ax + L * 0.2, ay + sag * 0.35)
    s1 = (bx - L * 0.2, by + sag * 0.35)
    mid_top = ((s0[0] + s1[0]) / 2, max(s0[1], s1[1]) + sag * 0.9)
    mid_bot = (mid_top[0], mid_top[1] + sag * 1.05)
    top = [qpt(s0, mid_top, s1, t / 20) for t in range(21)]
    bot = [qpt((s0[0] + 3, s0[1] + 9), mid_bot, (s1[0] - 3, s1[1] + 9), t / 20) for t in range(21)]
    out = [f'<clipPath id="{u}-hm"><polygon points="{P(top + bot[::-1])}"/></clipPath>']
    # strings
    st = []
    for i in range(6):
        f = i / 5
        st.append(f'<line x1="{ax}" y1="{ay}" x2="{s0[0] + f * 3:.1f}" y2="{s0[1] + f * 9:.1f}"/>')
        st.append(f'<line x1="{bx}" y1="{by}" x2="{s1[0] - f * 3:.1f}" y2="{s1[1] + f * 9:.1f}"/>')
    out.append('<g stroke="#8A6A4A" stroke-width="0.9" opacity="0.8">' + "".join(st) + "</g>")
    out.append(f'<path d="M {ax - 3} {ay - 2} l 6 0 l 0 5 l -6 0 Z M {bx - 3} {by - 2} l 6 0 l 0 5 l -6 0 Z" fill="#5A3E2A"/>')
    # bed: lengthwise stripes
    g = [f'<polygon points="{P(top + bot[::-1])}" fill="{cols[4]}"/>']
    nb = 12
    for j in range(nb):
        f0, f1 = j / nb, (j + 1) / nb
        e0 = [(t[0] + (bb[0] - t[0]) * f0, t[1] + (bb[1] - t[1]) * f0) for t, bb in zip(top, bot)]
        e1 = [(t[0] + (bb[0] - t[0]) * f1, t[1] + (bb[1] - t[1]) * f1) for t, bb in zip(top, bot)]
        g.append(f'<polygon points="{P(e0 + e1[::-1])}" fill="{cols[j % len(cols)]}"/>')
    g.append(f'<polygon points="{P(top + bot[::-1])}" fill="#2A1E40" opacity="0.0"/>')
    sh = [(t[0] + (bb[0] - t[0]) * 0.55, t[1] + (bb[1] - t[1]) * 0.55) for t, bb in zip(top, bot)]
    g.append(f'<polygon points="{P(sh + bot[::-1])}" fill="#2A1E40" opacity="0.3"/>')
    g.append(f'<polyline points="{P(top)}" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity="0.6"/>')
    # woven texture
    g.append('<g stroke="#2A1E40" stroke-width="0.8" opacity="0.25">' + "".join(
        f'<line x1="{top[i][0]:.1f}" y1="{top[i][1]:.1f}" x2="{bot[i][0]:.1f}" y2="{bot[i][1]:.1f}"/>' for i in range(1, 20)) + "</g>")
    out.append(f'<g clip-path="url(#{u}-hm)">' + "".join(g) + "</g>")
    # fringe tassels along the bottom edge
    out.append('<g stroke-width="1.4" stroke-linecap="round">' + "".join(
        f'<line x1="{bot[i][0]:.1f}" y1="{bot[i][1]:.1f}" x2="{bot[i][0] - 1:.1f}" y2="{bot[i][1] + 6:.1f}" stroke="{cols[i % 4]}"/>' for i in range(2, 19, 2)) + "</g>")
    return "".join(out)


def sloop(x, wl, s, hull="#F6F4F0", sail="#FFFFFF", sail_sh="#C8D4E4", rim="#FFF6D8", flip=False):
    """Small sloop under sail (mainsail + jib), heading right; (x, wl) = waterline centre."""
    f = -1 if flip else 1
    return (f'<g transform="translate({x} {wl}) scale({s * f} {s})">'
            f'<path d="M -30 2 Q 0 -8 30 -4 L 34 -6" stroke="#FFFFFF" stroke-width="1.6" fill="none" opacity="0.0"/>'
            f'<path d="M -26 -6 L 28 -6 L 20 2 L -22 2 Z" fill="{hull}"/><path d="M -24 -1 L 24 -1 L 20 2 L -22 2 Z" fill="#2A4A7A"/>'
            f'<line x1="-2" y1="-6" x2="-2" y2="-72" stroke="#5A5A6A" stroke-width="1.6"/>'
            f'<path d="M 0 -70 Q 18 -40 22 -9 L 0 -9 Z" fill="{sail}"/><path d="M 10 -46 Q 18 -30 22 -9 L 14 -9 Z" fill="{rim}" opacity="0.8"/>'
            f'<path d="M -4 -68 Q -20 -36 -24 -9 L -4 -9 Z" fill="{sail_sh}"/>'
            f'<line x1="-22" y1="-9" x2="0" y2="-9" stroke="#5A5A6A" stroke-width="1.2"/></g>')


def cancun():
    u = "cun"
    HZ = 228
    out = [defs(
        lg(f"{u}-sky", [(0, "#1D5AB4"), (0.4, "#3E8AD4"), (0.78, "#9ED0EE"), (1, "#DDF2F4")], 0, 40, 0, HZ, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#1C3C8A"), (0.1, "#1E56A4"), (0.3, "#1784BE"), (0.52, "#1EB0C4"), (0.74, "#45D0C8"), (0.9, "#8CE6D6"), (1, "#C4F2E2")], 0, HZ, 0, 352, units="userSpaceOnUse"),
        lg(f"{u}-sand", [(0, "#FFF8EA"), (0.35, "#F8EBD0"), (1, "#EAD2AC")], 0, 340, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-ch", [(0, "#FFFFFF"), (0.5, "#F4F8FC"), (1, "#C4D2E8")]),
        lg(f"{u}-hz", [(0, "#DDF2F4", 0), (1, "#DDF2F4", 0.75)], 0, 200, 0, HZ, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="{HZ + 1}" fill="url(#{u}-sky)"/>')
    out.append(glow(560, 40, 300, "#FFFBE8", f"{u}-sun", 0.7))
    # trade-wind cumulus: a low bank on the horizon, fair-weather puffs above
    out.append(cumulus(f"{u}-c1", 470, HZ - 2, 250, 58, 4, "#FFFFFF", "#F2F6FA", "#AFC2DE", hi="#FFFFFF", hi_op=0.7, light=1))
    out.append(cumulus(f"{u}-c2", 150, HZ - 2, 200, 40, 5, "#FFFFFF", "#EEF4FA", "#B4C6E0", hi="#FFFFFF", hi_op=0.7, light=1))
    out.append(cumulus(f"{u}-c3", 330, 132, 120, 30, 6, "#FFFFFF", "#F0F4FA", "#B8C8E2", hi="#FFFFFF", hi_op=0.7, light=1))
    out.append(cumulus(f"{u}-c4", 470, 98, 70, 18, 7, "#FFFFFF", "#F0F4FA", "#B8C8E2", hi="#FFFFFF", hi_op=0.7, light=1))
    out.append(f'<rect x="0" y="190" width="600" height="{HZ - 189}" fill="url(#{u}-hz)"/>')
    # the hotel zone strung along its sandbar, far to the left, pale in the haze
    rnd = random.Random(3)
    hz = []
    x = -10
    while x < 200:
        w = rnd.uniform(5, 13)
        h = rnd.uniform(3, 14) * (1 - x / 260)
        top = HZ - 2 - h
        col = rnd.choice(["#F2F2F2", "#E8ECF0", "#F6EEE2", "#DCE4EC"])
        if rnd.random() < 0.25:  # stepped, pyramid-like resort
            hz.append(f'<polygon points="{Pi([(x, HZ - 1), (x + w * 0.15, top), (x + w * 0.85, top), (x + w, HZ - 1)])}" fill="{col}"/>')
        else:
            hz.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{w:.1f}" height="{h + 1:.1f}" fill="{col}"/>')
        hz.append(f'<rect x="{x + w * 0.65:.1f}" y="{top:.1f}" width="{w * 0.35:.1f}" height="{h + 1:.1f}" fill="#9AB0C8" opacity="0.5"/>')
        x += w + rnd.uniform(1, 6)
    out.append("".join(hz))
    out.append(f'<path d="M -10 {HZ - 1} L 220 {HZ - 0.5} L 230 {HZ + 1} L -10 {HZ + 1.5} Z" fill="#F4ECD8"/>')
    out.append(dots(26, 4, (-10, HZ - 2, 200, HZ), "#5AA040", r=(0.8, 1.6), opacity=(0.6, 0.9)))
    # the Caribbean: deep blue, cobalt, then bands of turquoise over white sand and dark reef patches
    out.append(f'<rect x="0" y="{HZ}" width="600" height="{444 - HZ}" fill="url(#{u}-sea)"/>')
    out.append(patches(26, 8, (-10, 252, 610, 300), ["#1A5A9C", "#16508E", "#2066A8"], w=(24, 70), h=(2, 5), op=(0.35, 0.6)))
    out.append(patches(16, 9, (-10, 300, 610, 330), ["#7EE2D2", "#A8F0E0"], w=(30, 80), h=(2, 5), op=(0.35, 0.6)))
    out.append(strokes_h(170, 10, (-10, HZ + 2, 610, 334), ["#FFFFFF", "#BFEFF0", "#1A4A90"], w=(4, 20), sw=(0.8, 1.6), op=(0.25, 0.6)))
    out.append(dots(50, 11, (300, HZ + 2, 610, 300), "#FFFFFF", r=(0.6, 1.5), opacity=(0.5, 1)))
    # an offshore swell breaking softly
    wave = rough([(-10, 318), (120, 314), (260, 320), (400, 315), (610, 320)], 12, 2, 3)
    out.append(f'<polyline points="{P(wave)}" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.55" stroke-dasharray="40 14 22 10"/>')
    # sailboat and a parasailer with its tow boat
    sx_, sy_ = 196, 292
    out.append(f'<path d="M {sx_ - 26} {sy_ + 2} Q {sx_ - 70} {sy_ + 6} {sx_ - 110} {sy_ + 4}" stroke="#FFFFFF" stroke-width="1.6" fill="none" opacity="0.6"/>')
    out.append(f'<path d="M {sx_ - 6} {sy_ + 3} L {sx_ + 22} {sy_ + 3} L {sx_ + 16} {sy_ + 40} L {sx_} {sy_ + 34} Z" fill="#FFFFFF" opacity="0.25"/>')
    out.append(sloop(sx_, sy_, 1.2))
    bx, by = 268, 254
    out.append(f'<path d="M {bx + 10} {by + 2} L {bx + 90} {by + 6} M {bx + 10} {by + 3} L {bx + 80} {by - 2}" stroke="#FFFFFF" stroke-width="1.5" opacity="0.7"/>')
    out.append(f'<path d="M {bx - 12} {by - 3} L {bx + 12} {by - 3} L {bx + 8} {by + 2} L {bx - 10} {by + 2} Z" fill="#F4F4F4"/><rect x="{bx - 4}" y="{by - 7}" width="8" height="4" fill="#2A3A5A"/>')
    px_, py_ = 300, 118
    out.append(f'<path d="M {bx + 6} {by - 5} Q {(bx + px_) / 2 + 20} {(by + py_) / 2 + 10} {px_ + 2} {py_ + 26}" stroke="#3A4A6A" stroke-width="1" fill="none" opacity="0.8"/>')
    out.append(f'<g transform="translate({px_} {py_})">'
               '<path d="M -18 4 Q -16 -12 0 -13 Q 16 -12 18 4 Q 0 -2 -18 4 Z" fill="#F24A3A"/>'
               '<path d="M -10 -10 Q -8 -2 -9 2 L -4 0 Q -3 -6 -4 -12 Z M 4 -12 Q 3 -6 4 0 L 9 2 Q 8 -2 10 -10 Z" fill="#FFD24A"/>'
               '<path d="M -18 4 Q 0 -2 18 4" fill="none" stroke="#B8302A" stroke-width="1.4"/>'
               '<path d="M -16 4 L -1 22 M 16 4 L 1 22 M -6 1 L -1 22 M 6 1 L 1 22" stroke="#5A5A6A" stroke-width="0.7"/>'
               '<circle cx="0" cy="22" r="2" fill="#2A2A3A"/><path d="M -1 24 L -2 30 M 1 24 L 2 30" stroke="#2A2A3A" stroke-width="1.4"/></g>')
    # shore: swash, foam lace and the white sand
    shore = rough([(-10, 352), (110, 344), (240, 350), (380, 343), (500, 349), (610, 344)], 13, 3, 4)
    wet = [(x_, y_ + 9) for x_, y_ in shore]
    out.append(f'<polygon points="{P(shore + [(610, 444), (-10, 444)])}" fill="url(#{u}-sand)"/>')
    out.append(f'<polygon points="{P(shore + wet[::-1])}" fill="#E2D2B4" opacity="0.8"/>')
    out.append(f'<polygon points="{P([(x_, y_ - 6) for x_, y_ in shore] + shore[::-1])}" fill="#C8F2E6" opacity="0.8"/>')
    out.append(f'<polyline points="{P([(x_, y_ - 0.5) for x_, y_ in shore])}" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{P([(x_, y_ - 7) for x_, y_ in shore])}" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity="0.8" stroke-dasharray="18 6 30 8"/>')
    out.append(dots(90, 14, (-10, 336, 610, 352), "#FFFFFF", r=(0.8, 2), opacity=(0.6, 1)))
    out.append(strokes_h(40, 15, (-10, 350, 610, 362), ["#FFFFFF", "#D8C8A8"], w=(10, 30), sw=(0.8, 1.4), op=(0.4, 0.8)))
    # sand grain, ripples, footprints, shells
    out.append(dots(260, 16, (-10, 360, 610, 444), "#C8A878", r=(0.5, 1.3), opacity=(0.3, 0.7)))
    out.append(dots(120, 17, (-10, 360, 610, 444), "#FFFFFF", r=(0.5, 1.2), opacity=(0.5, 0.9)))
    out.append(strokes_h(50, 18, (-10, 366, 610, 444), ["#DCC29A", "#FFFDF4"], w=(14, 34), sw=(1, 1.6), op=(0.4, 0.7)))
    # palapa with its pole, the hammock slung to the palm
    out.append(palapa(392, 238, 300, 104, 410, u))
    out.append(coco_palm(578, 452, 312, -0.2, 5, light=1))
    fp = []
    for i in range(9):
        fx, fy = 214 + i * 8 + (i % 2) * 7, 446 - i * 10
        fp.append(f'<ellipse cx="{fx}" cy="{fy}" rx="{3.8 - i * 0.22:.1f}" ry="{2.2 - i * 0.12:.1f}" fill="#C8A878" opacity="0.7"/>'
                  f'<ellipse cx="{fx + 0.6}" cy="{fy - 0.6}" rx="{2.6 - i * 0.15:.1f}" ry="{1.2 - i * 0.07:.1f}" fill="#B89868" opacity="0.6"/>')
    out.append("".join(fp))
    out.append(hammock((398, 330), (561, 320), 30, u))
    # left palm leaning in over the beach
    out.append(coco_palm(26, 470, 340, 0.36, 3, light=1))
    # beach towel, flip-flops, a coconut and a starfish
    out.append(f'<g transform="translate(150 404) rotate(-6)"><rect x="-38" y="-10" width="76" height="22" rx="2" fill="#FFFFFF"/>'
               + "".join(f'<rect x="{-38 + i * 9.5:.1f}" y="-10" width="5" height="22" fill="#F07A3A"/>' for i in range(8))
               + '<rect x="-38" y="6" width="76" height="6" fill="#2A1E40" opacity="0.12"/></g>')
    out.append('<g><ellipse cx="214" cy="420" rx="4" ry="8" transform="rotate(20 214 420)" fill="#2EB0B8"/><ellipse cx="224" cy="424" rx="4" ry="8" transform="rotate(32 224 424)" fill="#2EB0B8"/>'
               '<path d="M 212 414 L 215 420 L 218 415 M 222 418 L 225 424 L 228 420" stroke="#FFFFFF" stroke-width="1.2" fill="none"/></g>')
    out.append('<g><circle cx="480" cy="424" r="9" fill="#7A5A2E"/><circle cx="483" cy="421" r="4.5" fill="#B88A4A" opacity="0.8"/><circle cx="476" cy="428" r="1.4" fill="#3A2A1A"/></g>')
    star = []
    for i in range(10):
        r = 10 if i % 2 == 0 else 4
        a = math.radians(-90 + 36 * i + 10)
        star.append((330 + r * math.cos(a), 430 + r * math.sin(a) * 0.6))
    out.append(f'<polygon points="{P(star)}" fill="#F08A4A"/><circle cx="330" cy="430" r="2" fill="#FFC27A"/>')
    out.append(frigate(240, 112, 0.55) + frigate(268, 128, 0.4))
    return "\n".join(out)


# ================================================================ PATAGONIA — the Fitz Roy massif at first light, guanacos on the steppe
def lens_cloud(cx, cy, w, h, top, under, rim):
    """Lenticular cloud: a smooth lens with a lit underside, as stacked over the Patagonian peaks."""
    return (f'<path d="M {cx - w} {cy} Q {cx} {cy - h * 2} {cx + w} {cy} Q {cx} {cy + h * 0.9} {cx - w} {cy} Z" fill="{top}"/>'
            f'<path d="M {cx - w} {cy} Q {cx} {cy + h * 0.9} {cx + w} {cy} Q {cx} {cy + h * 0.2} {cx - w} {cy} Z" fill="{under}"/>'
            f'<path d="M {cx - w * 0.92} {cy + 0.5} Q {cx} {cy + h * 0.8} {cx + w * 0.92} {cy + 0.5}" fill="none" stroke="{rim}" stroke-width="1.6" opacity="0.9"/>')


def condor(x, y, W, col="#1E1A24", band="#C8C4D0"):
    """Andean condor soaring on flat wings: broad wings fingered at the tips, white ruff, pale secondaries."""
    s = W / 100
    half = [(0, -2), (-14, -5), (-30, -6), (-44, -5), (-49, -6), (-46, -3.6), (-52, -3.5), (-47, -1.6), (-52, -0.5), (-46, 0.6), (-50, 2.2),
            (-43, 2.6), (-30, 6), (-14, 6), (-4, 7)]
    pts = half + [(-a, b) for a, b in half[::-1]]
    pale = [(-12, 4), (-30, 3.6), (-40, 2.4), (-30, 6), (-14, 6)]
    return (f'<g transform="translate({x} {y}) scale({s:.3f})">'
            f'<polygon points="{P(pts)}" fill="{col}"/>'
            f'<polygon points="{P(pale)}" fill="{band}" opacity="0.7"/><polygon points="{P([(-a, b) for a, b in pale])}" fill="{band}" opacity="0.7"/>'
            f'<path d="M -5 6 L 0 12 L 5 6 Z" fill="{col}"/><ellipse cx="0" cy="-3.2" rx="3.4" ry="2" fill="#F4F0EA"/><circle cx="0" cy="-5.6" r="2" fill="#7A4A44"/></g>')


def guanaco(x, base, h, grazing=False, flip=1, rim="#FFD6A0", coat="#BE7840", dark="#8A4E2A", belly="#F4EADC"):
    """Guanaco in profile facing left (flip=-1 faces right): long upright neck, small grey camel head with
    pointed ears, cinnamon back and flanks, a crisp white belly line and inner legs, slim legs, short tail.
    h = height to the ear tips (standing)."""
    s = h / 170
    sw = 2.0 / s
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({s * flip:.3f} {s:.3f})">']
    # far legs (in shade)
    g.append(f'<path d="M 38 -70 C 40 -50 38 -30 40 0 L 45 0 C 45 -30 47 -50 48 -68 Z '
             f'M 104 -72 C 112 -58 111 -44 106 -32 L 108 0 L 113 0 L 113 -32 C 117 -46 118 -60 115 -74 Z" fill="{dark}"/>')
    # body
    g.append(f'<path d="M 22 -86 C 22 -100 34 -105 52 -103 C 70 -101 86 -105 100 -104 C 114 -104 122 -96 120 -84 '
             f'C 118 -72 110 -66 100 -66 C 82 -64 62 -63 46 -64 C 32 -64 22 -72 22 -86 Z" fill="{coat}"/>')
    # belly: the sharp white underside
    g.append(f'<path d="M 26 -74 C 44 -70 76 -69 112 -72 C 108 -67 102 -66 98 -66 C 80 -64 60 -63 46 -64 C 36 -64 30 -68 26 -74 Z" fill="{belly}"/>')
    # near legs: cinnamon outer, white inner stripe, dark pads
    g.append(f'<path d="M 26 -70 C 28 -50 26 -30 28 0 L 33.5 0 C 33.5 -30 36 -50 38 -68 Z '
             f'M 94 -72 C 103 -58 102 -44 97 -32 L 99 0 L 104.5 0 L 104 -32 C 108 -46 110 -60 108 -74 Z" fill="{coat}"/>')
    g.append(f'<path d="M 32 -66 C 33 -48 31 -30 32 -2 M 102 -62 C 104 -50 102 -40 101 -30 L 102 -2" fill="none" stroke="{belly}" stroke-width="2.6" opacity="0.9"/>')
    g.append('<path d="M 27 -1 L 34 -1 M 98 -1 L 105 -1 M 39 -1 L 46 -1 M 107 -1 L 114 -1" stroke="#2A1E1A" stroke-width="3.4"/>')
    # tail
    g.append(f'<path d="M 117 -96 C 126 -94 128 -86 124 -76 C 120 -82 117 -86 114 -88 Z" fill="#5A3424"/>')
    if not grazing:
        # neck rising, white throat, grey head
        g.append(f'<path d="M 24 -82 C 16 -102 6 -124 3 -142 L 20 -148 C 22 -128 30 -110 44 -98 Z" fill="{coat}"/>')
        g.append(f'<path d="M 24 -82 C 16 -102 6 -124 3 -140 L 8 -141 C 11 -124 19 -104 30 -88 Z" fill="{belly}"/>')
        g.append('<path d="M 6 -137 C 0 -144 -8 -147 -15 -145 C -20 -143 -20 -137 -15 -135 C -8 -133 0 -133 8 -133 Z" fill="#6E6468"/>'
                 '<path d="M 2 -138 C 0 -150 7 -158 15 -156 C 23 -154 23 -146 21 -139 Z" fill="#76696C"/>'
                 '<path d="M 7 -153 L 4 -168 L 12 -155 Z M 13 -155 L 15 -170 L 19 -153 Z" fill="#5E5256"/>'
                 '<circle cx="2" cy="-146" r="2.4" fill="#141012"/><path d="M -17 -138 C -14 -136 -10 -135 -7 -136" stroke="#2A2224" stroke-width="2" fill="none"/>')
        g.append(f'<path d="M 20 -148 C 22 -128 30 -110 44 -98 C 60 -103 80 -103 100 -104 C 112 -104 120 -98 121 -88" fill="none" stroke="{rim}" stroke-width="{sw:.1f}" stroke-linecap="round"/>'
                 f'<path d="M 15 -170 L 19 -153 M 15 -156 C 9 -158 3 -152 2 -146" fill="none" stroke="{rim}" stroke-width="{sw * 0.8:.1f}" stroke-linecap="round"/>')
    else:
        # neck down to the grass, cropping
        g.append(f'<path d="M 26 -94 C 10 -90 -2 -70 -8 -34 L 6 -30 C 10 -58 22 -76 42 -98 Z" fill="{coat}"/>')
        g.append(f'<path d="M 24 -80 C 10 -74 0 -56 -6 -34 L -1 -33 C 4 -54 14 -70 30 -78 Z" fill="{belly}"/>')
        g.append('<path d="M -10 -38 C -16 -30 -16 -16 -12 -8 C -8 -4 -2 -6 0 -12 C 4 -20 6 -32 4 -38 Z" fill="#6E6468"/>'
                 '<path d="M -2 -38 L 2 -52 L 4 -38 Z M 3 -38 L 9 -50 L 8 -36 Z" fill="#5E5256"/><circle cx="-3" cy="-26" r="2.2" fill="#141012"/>')
        g.append(f'<path d="M 42 -98 C 60 -103 80 -103 100 -104 C 112 -104 120 -98 121 -88 M 26 -94 C 10 -90 -2 -70 -8 -34" fill="none" stroke="{rim}" stroke-width="{sw:.1f}" stroke-linecap="round"/>')
    g.append("</g>")
    return "".join(g)


def tussock(x, y, k, seed, cols=("#F6CC80", "#D8A050", "#FFE6B0", "#A8743E"), base="#7A4E2C", lean=-0.25):
    """A clump of coirón bunch-grass: a dark crown at the base and a fountain of thin blades, bent by the wind."""
    rnd = random.Random(seed)
    out = [f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{7 * k:.1f}" ry="{2.2 * k:.1f}" fill="{base}" opacity="0.7"/>']
    blades = []
    for i in range(int(10 + 8 * k)):
        a = math.radians(rnd.uniform(-160, -20))
        L = k * rnd.uniform(9, 18) * (0.6 + 0.4 * math.sin(-a))
        sx = x + rnd.uniform(-4, 4) * k
        ex = sx + math.cos(a) * L + lean * L
        ey = y - math.sin(-a) * L
        blades.append(f'<path d="M {sx:.1f} {y:.1f} Q {sx + (ex - sx) * 0.3:.1f} {ey + (y - ey) * 0.1:.1f} {ex:.1f} {ey:.1f}" stroke="{rnd.choice(cols)}"/>')
    out.append(f'<g fill="none" stroke-width="{max(1.0, 1.1 * k ** 0.6):.1f}" stroke-linecap="round">' + "".join(blades) + "</g>")
    return "".join(out)


def patagonia():
    u = "ptg"
    LK = 296  # lake surface
    ST = 352  # steppe edge (approx.)
    out = [defs(
        lg(f"{u}-sky", [(0, "#2A2A68"), (0.3, "#54488A"), (0.58, "#A87AA6"), (0.8, "#EDA8A2"), (1, "#FAD2AA")], 0, 40, 0, 280, units="userSpaceOnUse"),
        lg(f"{u}-gran", [(0, "#FFB066"), (0.2, "#FA8650"), (0.5, "#D25A5A"), (0.8, "#8A3E62"), (1, "#5A3462")], 0, 84, 0, 262, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#E8A8B0"), (0.5, "#B888A8"), (1, "#8E70A0")], 0, 120, 0, 262, units="userSpaceOnUse"),
        lg(f"{u}-ice", [(0, "#F6D8E0"), (0.3, "#C8BEE0"), (1, "#8C88BE")], 0, 204, 0, 292, units="userSpaceOnUse"),
        lg(f"{u}-lake", [(0, "#8AC4CC", 0.35), (0.5, "#4A9AAA", 0.6), (1, "#2A6E88", 0.9)], 0, LK, 0, 370, units="userSpaceOnUse"),
        lg(f"{u}-steppe", [(0, "#F0BC74"), (0.4, "#D2964E"), (1, "#8A5632")], 0, 340, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(-30, 290, 360, "#FFD8A8", f"{u}-dawn", 0.65))
    out.append(dots(30, 2, (280, 42, 600, 112), "#F6EEF6", r=(0.6, 1.3), opacity=(0.3, 0.8)))
    # the setting moon in the west and the stacked lenticulars typical of Patagonian winds
    out.append(glow(526, 84, 30, "#F6EEF6", f"{u}-mg", 0.5) + '<circle cx="526" cy="84" r="8" fill="#F8F2F2"/><circle cx="530" cy="81" r="7.4" fill="#4C4486"/>')
    out.append(lens_cloud(450, 136, 96, 9, "#9A88B8", "#F6B0A0", "#FFE2C8"))
    out.append(lens_cloud(462, 121, 66, 7, "#A894C0", "#F8C0A8", "#FFE8D0"))
    out.append(lens_cloud(456, 108, 38, 5, "#B4A2CA", "#FAD0B8", "#FFF0DC"))
    out.append(lens_cloud(122, 110, 72, 5, "#9C8CBC", "#F4B8AC", "#FFE6D2"))
    # Cerro Torre group: thin needles further off, hazier, on the left
    sv, _ = massif(f"{u}-ct", [(-10, 250), (18, 222), (38, 188), (50, 150), (58, 136), (66, 176), (82, 160), (96, 196), (128, 222), (170, 252)],
                   11, 270, f"url(#{u}-far)", shade="#5A4A86", shade_op=0.45, amp=3, depth=4, light=1, rim="#FFD6C0", rim_w=1.6,
                   tex=("#6A4E80", "#F6C8C0"), tex_op=(0.15, 0.35), tex_n=0.6, spine_k=0.1)
    out.append(sv)
    # the Fitz Roy massif: Saint-Exupéry, Poincenot, the great blocky summit of Fitz Roy, Mermoz, Guillaumet
    ctrl = [(60, 286), (100, 240), (124, 214), (138, 226), (156, 192), (170, 210), (188, 186), (202, 160), (212, 178), (230, 114),
            (244, 160), (256, 150), (264, 112), (274, 92), (290, 82), (310, 80), (324, 88), (334, 110), (342, 150), (352, 196), (366, 178),
            (380, 144), (392, 180), (406, 160), (418, 196), (448, 210), (488, 234), (540, 250), (610, 260)]
    ctrl = [(x, 276 - (276 - y) * 0.94) for x, y in ctrl]  # summit kept inside the print-safe area
    sv, line = massif(f"{u}-fr", ctrl, 21, 276, f"url(#{u}-gran)", shade="#3A2052", shade_op=0.5, amp=2.4, depth=4, decay=0.5, light=1,
                      rim="#FFE6B8", rim_w=2.2, gullies=12, 
                      tex=("#5A2A44", "#FFC08A", "#8A3A50"), tex_op=(0.18, 0.45), tex_n=1.8, spine_k=0.06,
                      haze="#B87A9A", haze_top=196)
    out.append(sv)
    # vertical joints in the granite of the main tower
    rnd = random.Random(5)
    out.append(f'<g clip-path="url(#{u}-fr-c)" stroke="#6A2A48" stroke-linecap="round" fill="none">' + "".join(
        f'<path d="M {x:.0f} {y:.0f} l {rnd.uniform(-2, 2):.1f} {rnd.uniform(14, 40):.0f}" stroke-width="{rnd.uniform(1.2, 2.2):.1f}" opacity="{rnd.uniform(0.25, 0.5):.2f}"/>'
        for x, y in ((rnd.uniform(262, 340), rnd.uniform(96, 190)) for _ in range(26))) + "</g>")
    out.append(f'<path d="M 276 107 Q 286 95 304 93" stroke="#FFF0C8" stroke-width="2.6" fill="none" stroke-linecap="round" opacity="0.9"/>')
    # the Piedras Blancas glacier tucked in the cirque under the towers: a ragged upper edge reaching up the
    # couloirs, a crevassed tongue, the shadow of the east ridge across it
    top = [(176, 252), (196, 240), (214, 236), (226, 222), (234, 230), (252, 226), (262, 210), (272, 222), (288, 216), (300, 200),
           (308, 214), (322, 218), (336, 206), (344, 224), (362, 230), (380, 238), (404, 244), (430, 254)]
    ice = rough(top, 31, 3, 3)
    tongue = rough([(430, 270), (380, 276), (338, 282), (312, 292), (292, 294), (270, 286), (236, 278), (200, 276), (176, 268)], 32, 3, 3)
    gl = ice + tongue
    out.append(f'<polygon points="{P(gl)}" fill="url(#{u}-ice)"/>')
    out.append(f'<clipPath id="{u}-ic"><polygon points="{P(gl)}"/></clipPath>')
    cr = []
    for _ in range(34):
        x0, y0 = rnd.uniform(190, 420), rnd.uniform(236, 276)
        L = rnd.uniform(6, 16)
        cr.append(f'<path d="M {x0:.0f} {y0:.0f} q {L / 2:.1f} {rnd.uniform(-1, 2):.1f} {L:.1f} {rnd.uniform(-1, 1.5):.1f}" stroke="#6A6AA0" stroke-width="{rnd.uniform(1, 1.6):.1f}" fill="none" opacity="0.5"/>')
    out.append(f'<g clip-path="url(#{u}-ic)">' + "".join(cr) + strokes_h(30, 34, (180, 214, 430, 280), ["#F6E4EE", "#A8A0CC"], w=(6, 16), sw=(1, 1.6), op=(0.4, 0.7))
               + f'<polygon points="{P([(334, 200), (440, 240), (440, 282), (350, 282)])}" fill="#6A5A9A" opacity="0.22"/></g>')
    out.append(f'<polyline points="{P(ice)}" fill="none" stroke="#FFE4E0" stroke-width="1.4" opacity="0.8"/>')
    # dark lateral moraines
    # lenga forest in autumn red, still in the blue shadow of dawn, on the moraine above the lake
    fr = rough([(-10, 262), (60, 254), (130, 266), (200, 266), (260, 282), (330, 284), (400, 270), (470, 264), (540, 256), (610, 262)], 41, 5, 4)
    fpoly = fr + [(610, LK + 2), (-10, LK + 2)]
    LENGA = [("#5A2440", "#8A3A48"), ("#6A2A3A", "#A8484A"), ("#7A3436", "#C05E4A"), ("#4A2A44", "#7A4252"), ("#6E3A30", "#B8664A")]
    out.append(forest_mosaic(fpoly, 42, 60, 230, 2.4, 5.5, base="#3E2440", pal=LENGA, cid=f"{u}-fo"))
    out.append(lg_rect(f"{u}-fh", -10, 254, 620, LK - 252, "#8A6A96", 0.0, 0.35))
    out.append(trees_on(fr, 43, ["#3A2440", "#4A2A42"], density=1.2, hmin=4, hmax=8, sink=2))
    # glacial lake: milky turquoise holding the reflection of the towers
    out.append(f'<clipPath id="{u}-lk"><rect x="-10" y="{LK}" width="620" height="90"/></clipPath>')
    out.append(f'<rect x="-10" y="{LK}" width="620" height="90" fill="#5A9EAC"/>')
    refl = (f'<polygon points="{P(line + [(610, 330), (60, 330)])}" fill="#E68A6E"/>'
            f'<polygon points="{P(gl)}" fill="#EEDCE6"/>'
            f'<polygon points="{P(fpoly)}" fill="#5A3048"/>')
    out.append(mirror(LK - 1, refl, f"{u}-lk", 0.5))
    out.append(f'<rect x="-10" y="{LK}" width="620" height="90" fill="url(#{u}-lake)"/>')
    out.append(ripple_lines(34, 44, (-10, LK + 3, 600, LK + 60), "#FFE2D4", op=(0.3, 0.6), w=(20, 70), sw=1.2))
    out.append(ripple_lines(16, 45, (-10, LK + 6, 600, LK + 60), "#2A5A72", op=(0.3, 0.5), w=(20, 60), sw=1.2))
    out.append(f'<rect x="-10" y="{LK - 0.5}" width="620" height="2" fill="#F6C8B8" opacity="0.6"/>')
    # golden steppe in the first sun, rising toward the viewer
    st = rough([(-10, 360), (80, 350), (180, 356), (300, 346), (420, 352), (520, 342), (610, 348)], 45, 5, 4)
    out.append(f'<polygon points="{P(st + [(610, 444), (-10, 444)])}" fill="url(#{u}-steppe)"/>')
    out.append(f'<polyline points="{P([(x, y + 2) for x, y in st])}" fill="none" stroke="#5A3A3A" stroke-width="2" opacity="0.3"/>')
    out.append(f'<polyline points="{P(st)}" fill="none" stroke="#FFDCA4" stroke-width="2.2" opacity="0.8"/>')
    out.append(strokes_h(170, 46, (-10, 354, 610, 444), ["#F6C880", "#B0743E", "#FFE2A8", "#8A5432"], w=(5, 16), sw=(1, 2), op=(0.35, 0.75)))
    items = []
    for _ in range(46):
        x, y = rnd.uniform(-10, 610), rnd.uniform(356, 446)
        k = 0.45 + (y - 350) / 96 * 1.15
        items.append((y, tussock(x, y, k, rnd.randrange(9999))))
    # a few dark mata negra shrubs
    for x, y in ((40, 382), (230, 370), (560, 392), (120, 420)):
        k = 0.6 + (y - 350) / 100
        items.append((y, f'<ellipse cx="{x}" cy="{y}" rx="{14 * k:.1f}" ry="{3 * k:.1f}" fill="#4A2E24" opacity="0.4"/>'
                      + leafy(x, y - 6 * k, 13 * k, 7 * k, int(x), "#2E3A2A", "#46523A", "#8A8A4A", n=7, lx=-0.7, ly=-0.6, dab=0.28, rot=False)))
    # guanacos: a sentinel buck on the rise, a grazing female and her chulengo, two more further off
    items.append((410, f'<ellipse cx="486" cy="412" rx="50" ry="5" fill="#5A3424" opacity="0.35"/>' + guanaco(430, 410, 112)))
    items.append((396, f'<ellipse cx="370" cy="398" rx="34" ry="4" fill="#5A3424" opacity="0.35"/>' + guanaco(330, 396, 80, grazing=True)))
    items.append((402, f'<ellipse cx="240" cy="404" rx="20" ry="3" fill="#5A3424" opacity="0.35"/>' + guanaco(258, 402, 54, flip=-1)))
    items.append((372, guanaco(136, 372, 40, grazing=True) + guanaco(96, 368, 38)))
    out.append("".join(v for _, v in sorted(items, key=lambda t: t[0])))
    out.append("".join(tussock(x, 446, 2.1, int(x)) for x in range(-10, 620, 34)))
    out.append(condor(512, 186, 64) + condor(170, 160, 34))
    return "\n".join(out)


def lg_rect(uid, x, y, w, h, color, op0, op1):
    """A rectangle washed with a vertical transparency gradient (haze, fog banks, darkening)."""
    return (defs(lg(uid, [(0, color, op0), (1, color, op1)], 0, y, 0, y + h, units="userSpaceOnUse"))
            + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{uid})"/>')


# ================================================================ BANFF — a red canoe on a turquoise glacial lake under the ten peaks, early morning
def canoe(x, wl, L, u, hull="#D8352A", hull_dk="#8E1E1E", hull_lt="#F26A4A", paddlers=2, flip=False):
    """Open canoe seen from the side and a little above: a long red hull with upswept ends, a cream gunwale,
    the varnished interior and thwarts, paddlers kneeling with paddles in the water. (x, wl) = waterline centre."""
    f = -1 if flip else 1
    h = L * 0.1
    pts_top = [(-L / 2, -h * 1.15), (-L * 0.42, -h * 0.72), (-L * 0.2, -h * 0.55), (0, -h * 0.52), (L * 0.2, -h * 0.55), (L * 0.42, -h * 0.72), (L / 2, -h * 1.15)]
    pts_bot = [(L / 2, -h * 1.15), (L * 0.46, -h * 0.4), (L * 0.36, 0), (0, h * 0.12), (-L * 0.36, 0), (-L * 0.46, -h * 0.4), (-L / 2, -h * 1.15)]
    inner = [(-L * 0.44, -h * 0.82), (-L * 0.2, -h * 0.75), (0, -h * 0.74), (L * 0.2, -h * 0.75), (L * 0.44, -h * 0.82)]
    g = [f'<g transform="translate({x} {wl}) scale({f} 1)">']
    # interior seen over the far gunwale
    far = [(-L * 0.47, -h * 1.0), (-L * 0.2, -h * 0.95), (0, -h * 0.93), (L * 0.2, -h * 0.95), (L * 0.47, -h * 1.0)]
    g.append(f'<polygon points="{P(far + inner[::-1])}" fill="#C88A4E"/>')
    g.append(f'<polyline points="{P(far)}" fill="none" stroke="#F4E8D0" stroke-width="1.6"/>')
    for t in (-0.28, 0.0, 0.28):
        g.append(f'<line x1="{L * t:.1f}" y1="{-h * 0.95:.1f}" x2="{L * t:.1f}" y2="{-h * 0.74:.1f}" stroke="#8A5A2E" stroke-width="2"/>')
    g.append(f'<polygon points="{P(pts_top + pts_bot[1:])}" fill="{hull}"/>')
    g.append(f'<polygon points="{P([(L * 0.46, -h * 0.4), (L * 0.36, 0), (0, h * 0.12), (-L * 0.36, 0), (-L * 0.46, -h * 0.4), (0, -h * 0.25)])}" fill="{hull_dk}" opacity="0.55"/>')
    g.append(f'<polyline points="{P([(p[0], p[1] + h * 0.18) for p in pts_top[1:-1]])}" fill="none" stroke="{hull_lt}" stroke-width="2.2" opacity="0.8"/>')
    g.append(f'<polyline points="{P(pts_top)}" fill="none" stroke="#F6EEDC" stroke-width="2" stroke-linejoin="round"/>')
    g.append(f'<path d="M {-L / 2:.1f} {-h * 1.15:.1f} l -2 -2 M {L / 2:.1f} {-h * 1.15:.1f} l 2 -2" stroke="#F6EEDC" stroke-width="2" stroke-linecap="round"/>')
    g.append("</g>")
    # paddlers (always facing the bow on the right when not flipped)
    for i, px in enumerate((-L * 0.3, L * 0.22)[:paddlers]):
        X = x + f * px
        Y = wl - h * 0.75
        jacket = ("#F2C230", "#2E6AB0")[i % 2]
        g.append(f'<path d="M {X - 5:.1f} {Y:.1f} Q {X - 6:.1f} {Y - 16:.1f} {X:.1f} {Y - 19:.1f} Q {X + 6:.1f} {Y - 16:.1f} {X + 5:.1f} {Y:.1f} Z" fill="{jacket}"/>'
                 f'<path d="M {X - f * 1:.1f} {Y - 18:.1f} Q {X - f * 5.5:.1f} {Y - 12:.1f} {X - f * 4.5:.1f} {Y - 2:.1f}" stroke="#7A4A1A" stroke-width="2.6" fill="none" opacity="0.45"/>'
                 f'<circle cx="{X:.1f}" cy="{Y - 23:.1f}" r="4.6" fill="#E8B48A"/>'
                 f'<path d="M {X - 5.4:.1f} {Y - 24:.1f} Q {X:.1f} {Y - 31:.1f} {X + 5.4:.1f} {Y - 24:.1f} Z" fill="{("#2A2A34", "#C8303A")[i % 2]}"/>')
        # paddle: shaft across the body, blade in the water on the near side
        a0 = (X + f * 9, Y - 28)
        a1 = (X - f * 10, wl + 9)
        g.append(f'<line x1="{a0[0]:.1f}" y1="{a0[1]:.1f}" x2="{a1[0]:.1f}" y2="{a1[1]:.1f}" stroke="#C89A5A" stroke-width="2.2" stroke-linecap="round"/>'
                 f'<path d="M {X + f * 6:.1f} {Y - 14:.1f} L {X + f * 3:.1f} {Y - 6:.1f}" stroke="#E8B48A" stroke-width="3.4" stroke-linecap="round"/>'
                 f'<path d="M {X - f * 3:.1f} {Y - 13:.1f} L {X - f * 6.5:.1f} {Y - 2:.1f}" stroke="#E8B48A" stroke-width="3.4" stroke-linecap="round"/>'
                 f'<ellipse cx="{a1[0] - f * 1:.1f}" cy="{wl + 3:.1f}" rx="6" ry="1.6" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(g)


def scree(apex, left, right, seed, top="#A2A6B4", bot="#727A8C", u="s"):
    """A talus cone poured from a gully: narrow at the top, spreading in a convex fan, pale grey with fall lines."""
    ax, ay = apex
    by = max(left[1], right[1])
    L = [qpt(apex, (ax - (ax - left[0]) * 0.25, ay + (by - ay) * 0.55), left, t / 10) for t in range(11)]
    R = [qpt(right, (ax + (right[0] - ax) * 0.25, ay + (by - ay) * 0.55), apex, t / 10) for t in range(11)]
    poly = rough(L, seed, 2, 2) + rough(R, seed + 1, 2, 2)
    box = (left[0], ay, right[0], by)
    out = [defs(lg(u, [(0, top), (1, bot)], 0, ay, 0, by, units="userSpaceOnUse"), f'<clipPath id="{u}-c"><polygon points="{P(poly)}"/></clipPath>'),
           f'<polygon points="{P(poly)}" fill="url(#{u})"/>']
    rnd = random.Random(seed)
    lines = []
    for _ in range(12):
        t = rnd.uniform(0.05, 0.95)
        ex = left[0] + (right[0] - left[0]) * t
        lines.append(f'<line x1="{ax + rnd.uniform(-3, 3):.1f}" y1="{ay + 6:.1f}" x2="{ex:.1f}" y2="{by:.1f}" stroke="{rnd.choice(["#5E6676", "#D8DEE6"])}" stroke-width="{rnd.uniform(0.8, 1.4):.1f}" opacity="{rnd.uniform(0.2, 0.4):.2f}"/>')
    shade = [(ax, ay)] + [(ax + (right[0] - ax) * f, ay + (by - ay) * f ** 0.8) for f in (0.5, 1.0)] + [(ax + (right[0] - ax) * 0.3, by)]
    out.append(f'<g clip-path="url(#{u}-c)">' + "".join(lines) + f'<polygon points="{P(shade)}" fill="#3A4466" opacity="0.25"/>'
               + dots(26, seed + 1, box, "#4E5666", r=(0.6, 1.5), opacity=(0.4, 0.8)) + "</g>")
    return "".join(out)


def banff():
    u = "bnf"
    LK = 272
    out = [defs(
        lg(f"{u}-sky", [(0, "#2E6CB8"), (0.45, "#6EA6DA"), (0.8, "#BCDCEE"), (1, "#F2EEE0")], 0, 40, 0, 230, units="userSpaceOnUse"),
        lg(f"{u}-rock", [(0, "#E8A87E"), (0.22, "#B88A84"), (0.5, "#6E7088"), (1, "#3E4A62")], 0, 84, 0, 268, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#C8D2E2"), (1, "#9AAAC2")], 0, 120, 0, 240, units="userSpaceOnUse"),
        lg(f"{u}-lake", [(0, "#4ED0D4"), (0.25, "#22B4C4"), (0.7, "#0E8EA6"), (1, "#0A7290")], 0, LK, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-lakeov", [(0, "#5ED8D8", 0.55), (0.3, "#24B6C6", 0.6), (1, "#0A7A96", 0.85)], 0, LK, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="{LK + 2}" fill="url(#{u}-sky)"/>')
    out.append(glow(20, 50, 260, "#FFF4D8", f"{u}-sun", 0.75))
    out.append(streak_cloud(470, 74, 70, "#FFFFFF", 0.7, 5) + streak_cloud(430, 84, 40, "#FFFFFF", 0.5, 3) + streak_cloud(170, 96, 50, "#FFFFFF", 0.45, 3))
    # far summits peeking between the ten peaks
    poly, fl = ridge_poly([(150, 240), (190, 150), (214, 128), (240, 160), (300, 140), (346, 118), (380, 150), (430, 140), (470, 240)], 3, amp=5, fill=f"url(#{u}-far)")
    out.append(poly)
    # the Valley of the Ten Peaks: a wall of jagged quartzite summits with glaciers in their laps
    ctrl = [(-10, 186), (16, 164), (34, 170), (60, 128), (74, 142), (92, 136), (118, 104), (138, 140), (160, 150), (184, 120), (200, 134),
            (232, 90), (252, 118), (270, 112), (296, 150), (320, 128), (338, 138), (366, 100), (388, 130), (404, 124), (428, 156), (452, 128),
            (474, 140), (500, 106), (522, 138), (546, 132), (574, 160), (610, 150)]
    ctrl = [(x, LK - (LK - y) * 0.95) for x, y in ctrl]
    sv, line = massif(f"{u}-tp", ctrl, 7, LK, f"url(#{u}-rock)", shade="#34405E", shade_op=0.5, amp=5, depth=5, decay=0.55, light=1,
                      snow="#FFF4EA", snow_y=124, snow_amp=26, snow_shade="#5A6A9A", rim="#FFE2B8", rim_w=2.2,
                      strata=("#4A5266", 0.22, 0.16, 16), gullies=14, tex=("#3E4658", "#F0DCCC"), tex_op=(0.15, 0.4), tex_n=1.2,
                      haze="#A8BCD4", haze_top=200, spine_k=0.12)
    out.append(sv)
    # talus fans pouring down to the water
    for i, (ax, ay, lx, rx) in enumerate(((96, 206, 56, 146), (206, 210, 166, 258), (330, 202, 276, 380), (466, 210, 418, 512), (574, 216, 538, 616))):
        out.append(scree((ax, ay), (lx, 262), (rx, 264), 50 + i, u=f"{u}-sc{i}"))
    # dark forest along the shore and up the avalanche strips between the fans
    fr = rough([(-10, 250), (40, 244), (60, 256), (130, 252), (150, 258), (260, 256), (280, 250), (380, 254), (400, 258), (500, 252), (530, 258), (610, 250)], 61, 4, 3)
    fpoly = fr + [(610, LK + 1), (-10, LK + 1)]
    out.append(f'<polygon points="{P(fpoly)}" fill="#1E3A34"/>')
    out.append(forest_fill(fpoly, 62, ["#1A3430", "#1E3A34", "#24443A", "#2A4A3C"], 420, 9, 18, light="#5E8A6A"))
    out.append(forest_fill([(-10, 226), (30, 200), (50, 210), (60, 256), (-10, 256)], 63, ["#1E3A34", "#2A4A3C"], 30, 8, 13, light="#5E8A6A"))
    out.append(forest_fill([(130, 252), (146, 216), (160, 222), (152, 258)], 64, ["#1E3A34", "#2A4A3C"], 12, 7, 11, light="#5E8A6A"))
    out.append(forest_fill([(370, 256), (384, 214), (396, 218), (402, 258)], 65, ["#1E3A34", "#2A4A3C"], 12, 7, 11, light="#5E8A6A"))
    out.append(forest_fill([(506, 254), (518, 212), (530, 216), (530, 258)], 66, ["#1E3A34", "#2A4A3C"], 12, 7, 11, light="#5E8A6A"))
    out.append(mist(300, 262, 320, 10, "#E8F4F8", f"{u}-m1", 0.45))
    # the lake: glacial-flour turquoise with the peaks mirrored in the still morning water
    out.append(f'<clipPath id="{u}-lk"><rect x="-10" y="{LK}" width="620" height="180"/></clipPath>')
    out.append(f'<rect x="-10" y="{LK}" width="620" height="180" fill="url(#{u}-lake)"/>')
    refl = (f'<polygon points="{P(line + [(610, LK + 10), (-10, LK + 10)])}" fill="#8A9AB4"/>'
            + f'<polygon points="{P(fpoly)}" fill="#163A3A"/>')
    out.append(mirror(LK, refl, f"{u}-lk", 0.5))
    out.append(f'<rect x="-10" y="{LK}" width="620" height="180" fill="url(#{u}-lakeov)"/>')
    out.append(water_lines(160, 67, (-10, LK + 4, 610, 440), ["#9AF0EC", "#E8FFFC", "#0E7A92", "#4ED0D4"], w=(10, 50), h=(1, 2), opacity=(0.25, 0.7)))
    out.append(f'<rect x="-10" y="{LK}" width="620" height="2" fill="#D8FAF6" opacity="0.6"/>')
    # floating logs drifting near the outlet
    for lx_, ly_, L in ((120, 312, 70), (196, 324, 46), (470, 300, 54)):
        out.append(f'<g transform="rotate(-4 {lx_} {ly_})"><rect x="{lx_ - L / 2}" y="{ly_ - 3}" width="{L}" height="6" rx="3" fill="#8A6A52"/>'
                   f'<rect x="{lx_ - L / 2}" y="{ly_ - 3}" width="{L}" height="2.2" rx="1.1" fill="#D8C0A0"/>'
                   f'<ellipse cx="{lx_ + L / 2 - 1}" cy="{ly_}" rx="2" ry="3" fill="#E8D4B4"/>'
                   f'<rect x="{lx_ - L / 2}" y="{ly_ + 4}" width="{L}" height="3" fill="#0A6A80" opacity="0.4"/></g>')
    # a second canoe far off near the shore
    out.append(canoe(262, 292, 46, u, hull="#F2B030", hull_dk="#A86A1A", hull_lt="#FFD870", paddlers=0, flip=True))
    out.append(f'<path d="M 286 293 q 20 2 40 1" stroke="#E8FFFC" stroke-width="1" opacity="0.6" fill="none"/>')
    # the red canoe gliding out, its V wake and reflection
    cx_, cw = 344, 384
    wake = []
    wr = random.Random(68)
    for j in range(18):
        t = j / 17
        for sgn in (-1, 1):
            wake.append(f'<path d="M {cx_ - 72 - t * 170:.1f} {cw + 2 + sgn * (1 + t * 16) * (0.5 if sgn < 0 else 1):.1f} q {-6 - t * 6:.1f} {sgn * -1:.1f} {-12 - t * 8:.1f} 0" '
                        f'stroke="#E8FFFC" stroke-width="{1.8 - t:.1f}" fill="none" stroke-linecap="round" opacity="{0.85 - t * 0.6:.2f}"/>')
    out.append("".join(wake))
    out.append(f'<g opacity="0.45"><path d="M {cx_ - 70} {cw + 2} Q {cx_} {cw + 14} {cx_ + 70} {cw + 2} L {cx_ + 64} {cw + 11} Q {cx_} {cw + 22} {cx_ - 64} {cw + 11} Z" fill="#B8302A"/></g>')
    out.append(water_lines(14, 69, (cx_ - 50, cw + 6, cx_ + 50, cw + 20), ["#4ED0D4", "#E8FFFC"], w=(10, 30), h=(1, 1.8), opacity=(0.5, 0.9), grow=False))
    out.append(canoe(cx_, cw, 150, u))
    # left foreground: the rockpile's lichen-spotted quartzite boulders and tall subalpine firs framing the view
    rk = [(-20, 444), (-20, 330), (20, 316), (60, 326), (96, 352), (128, 380), (156, 412), (170, 444)]
    out.append(f'<polygon points="{P(rough(rk, 70, 6, 3))}" fill="#6E6A72"/>')
    for i, (bx, by, rx, ry) in enumerate(((10, 350, 48, 30), (80, 384, 42, 25), (134, 422, 46, 26), (36, 410, 54, 32), (-6, 444, 64, 30))):
        out.append(boulder(bx, by, rx, ry, 71 + i, u, lit="#E8DCD2", mid="#A8A2A6", dark="#5E5A66"))
        out.append(dots(10, 72 + i, (bx - rx * 0.6, by - ry * 0.7, bx + rx * 0.5, by), "#D8C060", r=(1, 2.2), opacity=(0.5, 0.85)))
    out.append(f'<ellipse cx="190" cy="438" rx="40" ry="6" fill="#0A6A80" opacity="0.4"/>')
    # framing firs
    for x, b, h, w, sd in ((20, 340, 300, 0.24, 81), (74, 352, 226, 0.22, 82), (-12, 380, 330, 0.26, 83)):
        out.append(conifer(x, b, h, "#16302C", sd, width=w, light="#3E6A52"))
    for x, b, h, w, sd in ((584, 318, 270, 0.24, 84), (548, 308, 190, 0.22, 85), (612, 330, 320, 0.26, 86)):
        out.append(conifer(x, b, h, "#16302C", sd, width=w, light="#3E6A52"))
    # the right shore under those firs: a strip of rock and grass, and the firs mirrored in the lake
    rs = rough([(500, 306), (530, 300), (570, 302), (620, 298)], 87, 3, 3)
    firs_r = "".join(conifer(x, 312, h, "#0A3A3E", sd, width=w) for x, h, w, sd in ((584, 276, 0.24, 84), (548, 196, 0.22, 85), (612, 318, 0.26, 86)))
    out.append(f'<clipPath id="{u}-rr"><rect x="480" y="312" width="140" height="140"/></clipPath>' + mirror(312, firs_r, f"{u}-rr", 0.28))
    out.append(f'<polygon points="{P(rs + [(620, 314), (500, 312)])}" fill="#5A5E62"/>'
               f'<polyline points="{P(rs)}" fill="none" stroke="#B8C0A0" stroke-width="2"/>')
    out.append(birds_v([(300, 150, 8), (316, 156, 6)], "#2A3A50", 1.6))
    return "\n".join(out)


# ================================================================ QUÉBEC CITY — the copper-roofed castle above the old town, a snowy blue hour
def lit_windows(x0, y0, cols, rows, dx, dy, w, h, seed, p=0.7, lit=("#FFD27A", "#FFC060", "#FFE2A0"), dark="#3A2A40", frame=None, arch=False):
    """A grid of small windows, most of them lit warm."""
    rnd = random.Random(seed)
    out = []
    for r in range(rows):
        for c in range(cols):
            x, y = x0 + c * dx, y0 + r * dy
            col = rnd.choice(lit) if rnd.random() < p else dark
            if frame:
                out.append(f'<rect x="{x - 0.8:.1f}" y="{y - 0.8:.1f}" width="{w + 1.6:.1f}" height="{h + 1.6:.1f}" fill="{frame}"/>')
            if arch:
                out.append(f'<path d="M {x:.1f} {y + h:.1f} L {x:.1f} {y + w / 2:.1f} A {w / 2:.1f} {w / 2:.1f} 0 0 1 {x + w:.1f} {y + w / 2:.1f} L {x + w:.1f} {y + h:.1f} Z" fill="{col}"/>')
            else:
                out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{col}"/>')
    return "".join(out)


def dormer(x, y, w, h, roof="#4E9C84", lit="#FFD27A", snow="#F4F6FC"):
    """Gabled dormer: copper cheeks and pediment, a lit window, snow sitting on its little roof."""
    return (f'<rect x="{x - w / 2:.1f}" y="{y - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{roof}"/>'
            f'<rect x="{x - w * 0.3:.1f}" y="{y - h * 0.85:.1f}" width="{w * 0.6:.1f}" height="{h * 0.75:.1f}" fill="{lit}"/>'
            f'<line x1="{x:.1f}" y1="{y - h * 0.85:.1f}" x2="{x:.1f}" y2="{y - h * 0.1:.1f}" stroke="#7A4A2A" stroke-width="0.8"/>'
            f'<polygon points="{P([(x - w * 0.7, y - h), (x, y - h - w * 0.75), (x + w * 0.7, y - h)])}" fill="{roof}"/>'
            f'<polyline points="{P([(x - w * 0.75, y - h + 0.5), (x, y - h - w * 0.8), (x + w * 0.75, y - h + 0.5)])}" fill="none" stroke="{snow}" stroke-width="1.8" stroke-linejoin="round"/>'
            f'<polygon points="{P([(x, y - h - w * 0.75), (x + w * 0.7, y - h), (x + w * 0.2, y - h)])}" fill="#1E3A40" opacity="0.35"/>')


def copper_roof(pts, u, seams=10, light_x=None):
    """A steep copper roof gone verdigris: gradient, standing seams, darker shade half, snow dusting."""
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    gid = f"{u}-g"
    out = [defs(lg(gid, [(0, "#8ED8BC"), (0.5, "#5AAE94"), (1, "#3A7E70")], x0, 0, x1, 0, units="userSpaceOnUse"),
                f'<clipPath id="{u}-c"><polygon points="{P(pts)}"/></clipPath>'),
           f'<polygon points="{P(pts)}" fill="url(#{gid})"/>']
    g = []
    for i in range(1, seams):
        x = x0 + (x1 - x0) * i / seams
        g.append(f'<line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y1:.1f}" stroke="#2E6A5E" stroke-width="0.9" opacity="0.5"/>')
    g.append(dots(int((x1 - x0) * (y1 - y0) / 60), int(x0 * 7 + y0), (x0, y0, x1, y1), "#F4F6FC", r=(0.6, 1.4), opacity=(0.5, 0.9)))
    g.append(f'<rect x="{x0:.1f}" y="{y1 - 5:.1f}" width="{x1 - x0:.1f}" height="5" fill="#FFC88A" opacity="0.35"/>')
    out.append(f'<g clip-path="url(#{u}-c)">' + "".join(g) + "</g>")
    return "".join(out)


def turret(cx, top, bottom, r, cone_h, u, seed, wall="url(#qc-wall)"):
    """Round corner tower: a cylinder of floodlit brick with slit windows under a tall copper witch-hat cone."""
    out = [defs(lg(f"{u}-cy", [(0, "#F2B47A"), (0.45, "#D88A5A"), (1, "#7A4A44")], cx - r, 0, cx + r, 0, units="userSpaceOnUse"))]
    out.append(f'<rect x="{cx - r:.1f}" y="{top:.1f}" width="{2 * r:.1f}" height="{bottom - top:.1f}" fill="url(#{u}-cy)"/>')
    out.append(f'<rect x="{cx - r:.1f}" y="{top:.1f}" width="{2 * r:.1f}" height="{bottom - top:.1f}" fill="url(#qc-up)"/>')
    out.append(lit_windows(cx - r * 0.25, top + 10, 1, int((bottom - top - 16) / 16), 0, 16, r * 0.5, 8, seed, p=0.8, arch=True))
    out.append(f'<rect x="{cx - r - 1.5:.1f}" y="{top - 2:.1f}" width="{2 * r + 3:.1f}" height="4" fill="#E8C49A"/>')
    cone = [(cx - r - 3, top), (cx, top - cone_h), (cx + r + 3, top)]
    out.append(copper_roof(cone, f"{u}-cn", seams=5))
    out.append(f'<polyline points="{P([(cx - r - 3.5, top + 1), (cx + r + 3.5, top + 1)])}" stroke="#F4F6FC" stroke-width="2.2"/>')
    out.append(f'<line x1="{cx:.1f}" y1="{top - cone_h:.1f}" x2="{cx:.1f}" y2="{top - cone_h - 9:.1f}" stroke="#2E5A52" stroke-width="1.6"/><circle cx="{cx:.1f}" cy="{top - cone_h - 4:.1f}" r="1.6" fill="#E8C060"/>')
    return "".join(out)


def kiosk(x, base, k):
    """A Victorian terrace kiosk: white posts, a green bell roof capped with snow, a lamp glow inside."""
    return (f'<g transform="translate({x} {base}) scale({k})">'
            f'<rect x="-11" y="-16" width="22" height="16" fill="#FFD890" opacity="0.35"/>'
            + "".join(f'<rect x="{px - 1}" y="-17" width="2" height="17" fill="#F4EEE4"/>' for px in (-11, -4, 4, 11))
            + '<path d="M -15 -17 Q -12 -24 0 -32 Q 12 -24 15 -17 Z" fill="#4E9C84"/><path d="M 0 -32 Q 12 -24 15 -17 L 6 -17 Q 6 -24 0 -32 Z" fill="#2E6A5E" opacity="0.6"/>'
            '<path d="M -14 -18 Q -10 -26 0 -32 Q 10 -26 14 -18" fill="none" stroke="#F4F6FC" stroke-width="2"/>'
            '<line x1="0" y1="-32" x2="0" y2="-38" stroke="#2E5A52" stroke-width="1.4"/><rect x="-14" y="-3" width="28" height="3" fill="#F4F6FC"/></g>')


def stone_house(x, base, w, wall_h, roof_h, seed, wall="#8A8494", roof_snow="#EEF2FA", dormers=2, chim=True, shop=False, k=1.0):
    """Old-town stone house: grey rubble walls, warm windows, a steep roof under thick snow with dormers and
    fire-break gables carrying chimney stacks at both ends."""
    rnd = random.Random(seed)
    top = base - wall_h
    out = [f'<rect x="{x:.1f}" y="{top:.1f}" width="{w:.1f}" height="{wall_h:.1f}" fill="{wall}"/>']
    out.append(blobs(int(w * wall_h / 40), seed, (x, top, x + w, base), ["#6E6878", "#A8A2B0", "#7A7488"], r=(1.5, 3.5), opacity=(0.4, 0.8), squash=0.6))
    out.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{w:.1f}" height="{wall_h:.1f}" fill="url(#qc-hs)"/>')
    nw = max(2, int(w / (22 * k)))
    ww = 7 * k
    for i in range(nw):
        wx = x + w * (i + 0.5) / nw - ww / 2
        for j, wy in enumerate((top + 8 * k, top + wall_h * 0.5)):
            if wy + 12 * k > base - 2:
                continue
            lit = rnd.random() < 0.75
            col = rnd.choice(["#FFD27A", "#FFC060", "#FFE2A0"]) if lit else "#3A3450"
            out.append(f'<rect x="{wx - 1.2:.1f}" y="{wy - 1.2:.1f}" width="{ww + 2.4:.1f}" height="{12 * k + 2.4:.1f}" fill="#E8E2D8"/>'
                       f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{ww:.1f}" height="{12 * k:.1f}" fill="{col}"/>'
                       f'<line x1="{wx + ww / 2:.1f}" y1="{wy:.1f}" x2="{wx + ww / 2:.1f}" y2="{wy + 12 * k:.1f}" stroke="#6A4A3A" stroke-width="0.8"/>')
            if lit:
                out.append(f'<rect x="{wx - 2:.1f}" y="{wy + 12 * k + 1:.1f}" width="{ww + 4:.1f}" height="2" fill="#F4F6FC"/>')
    if shop:
        out.append(f'<rect x="{x + w * 0.15:.1f}" y="{base - wall_h * 0.42:.1f}" width="{w * 0.7:.1f}" height="{wall_h * 0.42:.1f}" fill="#FFCE7A"/>'
                   f'<rect x="{x + w * 0.12:.1f}" y="{base - wall_h * 0.48:.1f}" width="{w * 0.76:.1f}" height="{wall_h * 0.07:.1f}" fill="{rnd.choice(["#B8303A", "#2E5A8A", "#2E6A4E"])}"/>')
    # roof under snow
    rf = [(x - 3, top), (x + w * 0.12, top - roof_h), (x + w * 0.88, top - roof_h), (x + w + 3, top)]
    out.append(f'<polygon points="{P(rf)}" fill="{roof_snow}"/>')
    out.append(f'<polygon points="{P([(x + w * 0.5, top - roof_h), (x + w * 0.88, top - roof_h), (x + w + 3, top), (x + w * 0.55, top)])}" fill="#A8B4D8" opacity="0.45"/>')
    out.append(f'<rect x="{x - 3:.1f}" y="{top - 1.5:.1f}" width="{w + 6:.1f}" height="3" fill="#6A7090" opacity="0.6"/>')
    out.append(f'<path d="M {x - 3:.1f} {top + 1:.1f} ' + " ".join(f'L {x - 3 + (w + 6) * i / 10:.1f} {top + 1 + rnd.uniform(1, 5):.1f}' for i in range(11)) + '" stroke="#DCE6F6" stroke-width="1.4" fill="none"/>')
    for i in range(dormers):
        dx = x + w * (i + 1) / (dormers + 1)
        out.append(dormer(dx, top - roof_h * 0.18, 9 * k, 11 * k, roof="#5E6A80", lit=rnd.choice(["#FFD27A", "#FFE2A0", "#3A3450"])))
    if chim:
        for ex in (x - 2, x + w - 8 * k + 2):
            out.append(f'<rect x="{ex:.1f}" y="{top - roof_h - 10 * k:.1f}" width="{8 * k:.1f}" height="{roof_h + 10 * k:.1f}" fill="#7A7488"/>'
                       f'<rect x="{ex - 1:.1f}" y="{top - roof_h - 12 * k:.1f}" width="{8 * k + 2:.1f}" height="{3 * k:.1f}" fill="#F4F6FC"/>')
        out.append(f'<path d="M {x + w - 4 * k:.1f} {top - roof_h - 14 * k:.1f} q -6 -8 -2 -16 q 4 -8 -2 -16" stroke="#C8CCE4" stroke-width="{3 * k:.1f}" fill="none" opacity="0.35" stroke-linecap="round"/>')
    return "".join(out)


def snowy_fir(x, base, h, seed, col="#1E2A40", snow="#EEF2FA"):
    """Small fir loaded with snow: dark spire, white shelves on every tier of branches."""
    rnd = random.Random(seed)
    out = [conifer(x, base, h, col, seed, width=0.42)]
    for i in range(4):
        t = 0.2 + i * 0.19
        y = base - h * t
        w = h * 0.2 * (1 - t) + 1.5
        out.append(f'<path d="M {x - w:.1f} {y + 1:.1f} Q {x:.1f} {y - 3:.1f} {x + w * 0.8:.1f} {y + 0.5:.1f}" stroke="{snow}" stroke-width="{max(1.4, h * 0.07):.1f}" fill="none" stroke-linecap="round"/>')
    out.append(f'<circle cx="{x:.1f}" cy="{base - h + 1.5:.1f}" r="{max(1, h * 0.04):.1f}" fill="{snow}"/>')
    return "".join(out)


def quebec_city():
    u = "qc"
    CT = 262  # top of the cliff in castle coordinates (the castle group is shifted down by DY)
    DY = 14
    out = [defs(
        lg(f"{u}-sky", [(0, "#121A40"), (0.35, "#22306A"), (0.7, "#4A529A"), (1, "#8A80B8")], 0, 40, 0, 270, units="userSpaceOnUse"),
        lg(f"{u}-wall", [(0, "#8A5A50"), (0.55, "#C8784E"), (1, "#F2A868")], 0, 110, 0, CT, units="userSpaceOnUse"),
        lg(f"{u}-up", [(0, "#FFC07A", 0), (1, "#FFC07A", 0.25)], 0, 110, 0, CT, units="userSpaceOnUse"),
        lg(f"{u}-hs", [(0, "#1E2448", 0.1), (1, "#1E2448", 0.45)]),
        lg(f"{u}-cliff", [(0, "#5A5A7E"), (1, "#2E3058")], 0, CT, 0, 360, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(40, 1, (0, 40, 600, 140), "#F4F0FF", r=(0.5, 1.2), opacity=(0.3, 0.8)))
    out.append(glow(300, 260, 300, "#FFB878", f"{u}-cityglow", 0.35))
    # a low cloud bank lit from below by the city
    out.append(streak_cloud(110, 130, 120, "#6A6AA8", 0.5, 8) + streak_cloud(520, 116, 110, "#6A6AA8", 0.45, 7))
    # ---- the castle: floodlit brick walls, verdigris roofs, a central tower and turreted wings
    W = []
    # far left lower wing
    W.append(f'<rect x="96" y="214" width="92" height="{CT - 214}" fill="url(#{u}-wall)"/>')
    W.append(lit_windows(102, 222, 8, 3, 11, 13, 5, 7, 11, p=0.75))
    W.append(copper_roof([(92, 214), (106, 188), (184, 188), (192, 214)], f"{u}-r0", seams=12))
    W.append("".join(dormer(x, 206, 7, 9) for x in (116, 136, 156, 174)))
    W.append(turret(98, 200, CT, 11, 42, f"{u}-t0", 12))
    # left wing
    W.append(f'<rect x="186" y="186" width="118" height="{CT - 186}" fill="url(#{u}-wall)"/>')
    W.append(lit_windows(192, 196, 10, 5, 11.4, 13, 5.4, 7.5, 13, p=0.72))
    W.append(copper_roof([(182, 186), (198, 148), (292, 148), (308, 186)], f"{u}-r1", seams=14))
    W.append("".join(dormer(x, 178, 8, 10) for x in (206, 228, 250, 272, 290)))
    W.append("".join(dormer(x, 162, 6, 8) for x in (220, 245, 270)))
    W.append(turret(186, 172, CT, 14, 56, f"{u}-t1", 14))
    # right wing
    W.append(f'<rect x="368" y="194" width="104" height="{CT - 194}" fill="url(#{u}-wall)"/>')
    W.append(f'<rect x="420" y="194" width="52" height="{CT - 194}" fill="#2A2048" opacity="0.25"/>')
    W.append(lit_windows(374, 204, 9, 4, 11.2, 13, 5.4, 7.5, 15, p=0.72))
    W.append(copper_roof([(364, 194), (378, 158), (462, 158), (476, 194)], f"{u}-r2", seams=12))
    W.append("".join(dormer(x, 186, 8, 10) for x in (388, 410, 432, 454)))
    W.append(turret(470, 178, CT, 13, 52, f"{u}-t2", 16))
    # far right lower block stepping down the cliff
    W.append(f'<rect x="482" y="222" width="70" height="{CT - 222}" fill="url(#{u}-wall)"/>')
    W.append(f'<rect x="482" y="222" width="70" height="{CT - 222}" fill="#2A2048" opacity="0.3"/>')
    W.append(lit_windows(488, 230, 6, 2, 10.5, 13, 5, 7, 17, p=0.7))
    W.append(copper_roof([(478, 222), (490, 202), (546, 202), (556, 222)], f"{u}-r3", seams=8))
    # the central tower
    W.append(f'<rect x="300" y="136" width="72" height="{CT - 136}" fill="url(#{u}-wall)"/>')
    W.append(f'<rect x="338" y="136" width="34" height="{CT - 136}" fill="#2A2048" opacity="0.22"/>')
    W.append(f'<rect x="300" y="136" width="72" height="{CT - 136}" fill="url(#{u}-up)"/>')
    W.append(lit_windows(306, 148, 6, 8, 10.6, 12.6, 5.6, 7.6, 18, p=0.78))
    for yy in (144, 182, 220):
        W.append(f'<rect x="298" y="{yy}" width="76" height="2.2" fill="#F0C898" opacity="0.8"/>')
    W.append(f'<path d="M 325 {CT} L 325 244 A 11 11 0 0 1 347 244 L 347 {CT} Z" fill="#FFCE7A"/>')
    W.append(copper_roof([(296, 136), (312, 92), (360, 92), (376, 136)], f"{u}-r4", seams=10))
    W.append("".join(dormer(x, 129, 8, 11) for x in (314, 336, 358)))
    W.append("".join(dormer(x, 110, 6, 8) for x in (325, 347)))
    W.append(f'<rect x="312" y="90" width="48" height="3" fill="#F4F6FC"/>')
    for fx in (316, 356):
        W.append(f'<line x1="{fx}" y1="92" x2="{fx}" y2="78" stroke="#2E5A52" stroke-width="2"/><circle cx="{fx}" cy="84" r="2.2" fill="#E8C060"/>')
    for tx in (300, 372):
        W.append(turret(tx, 138, 156, 6, 22, f"{u}-tb{tx}", tx))
    out.append(f'<g transform="translate(0 {DY})">{"".join(W)}')
    out.append(mist(336, 92, 30, 12, "#FFE8B8", f"{u}-tg", 0.3))
    # ---- Dufferin-style terrace on the cliff edge: boardwalk, railing, kiosks and lamps
    out.append(f'<rect x="-10" y="{CT - 4}" width="300" height="8" fill="#5A4A5A"/><rect x="-10" y="{CT - 6}" width="300" height="3" fill="#F4F6FC"/>')
    out.append(f'<g stroke="#2A2440" stroke-width="1.2">' + "".join(f'<line x1="{x}" y1="{CT - 6}" x2="{x}" y2="{CT - 14}"/>' for x in range(-6, 290, 7)) + f'<line x1="-10" y1="{CT - 14}" x2="290" y2="{CT - 14}"/></g>')
    out.append(kiosk(44, CT - 6, 1.2) + kiosk(112, CT - 6, 1.1) + kiosk(260, CT - 6, 1.0))
    for lx in (12, 80, 150, 226):
        out.append(glow(lx, CT - 30, 22, "#FFD08A", f"{u}-lg{lx}", 0.7)
                   + f'<line x1="{lx}" y1="{CT - 6}" x2="{lx}" y2="{CT - 28}" stroke="#1E1A30" stroke-width="1.6"/><circle cx="{lx}" cy="{CT - 30}" r="3" fill="#FFF0C0"/>')
    rnd = random.Random(30)
    out.append("".join(f'<g transform="translate({x:.0f} {CT - 6})"><rect x="-2" y="-11" width="4" height="8" rx="1.5" fill="{rnd.choice(["#2A2440", "#8A2A3A", "#2A3A6A"])}"/>'
                       f'<circle cx="0" cy="-13" r="2" fill="#2A2440"/><path d="M -1.6 -3 L -1.6 0 M 1.6 -3 L 1.6 0" stroke="#2A2440" stroke-width="1.4"/></g>' for x in (28, 64, 70, 134, 196, 202)))
    out.append("</g>")
    CT += DY
    # ---- the cliff of Cap Diamant: buttresses of dark slate, snow on every ledge, snowy firs clinging on
    base = rough([(-10, 350), (120, 342), (260, 348), (400, 340), (610, 346)], 32, 4, 3)
    cpoly = [(-10, CT), (610, CT)] + base[::-1]
    out.append(f'<polygon points="{P(cpoly)}" fill="url(#{u}-cliff)"/>')
    out.append(f'<clipPath id="{u}-cc"><polygon points="{P(cpoly)}"/></clipPath>')
    g = []
    for i in range(16):
        bx = -10 + i * 40 + rnd.uniform(-8, 8)
        bw = rnd.uniform(18, 34)
        face = rough([(bx, CT + 2), (bx + bw * 0.2, CT + 30), (bx - 4, 352)], 400 + i, 4, 3)
        g.append(f'<polygon points="{P(face + [(bx + bw, 352), (bx + bw, CT + 2)])}" fill="#6E6E94" opacity="0.55"/>')
        g.append(f'<polyline points="{P(face)}" fill="none" stroke="#9A9AC0" stroke-width="1.1" opacity="0.3"/>')
    g.append(streaks(70, 33, (-10, CT, 610, 350), ["#3A3A60", "#24244A"], w=(1.5, 4), length=(10, 34), opacity=(0.3, 0.6), slant=0.1))
    g.append(patches(46, 34, (-10, CT + 10, 610, 344), ["#E8EEF8", "#C8D2EA", "#F4F6FC"], w=(6, 18), h=(1.5, 3.5), op=(0.75, 1)))
    out.append(f'<g clip-path="url(#{u}-cc)">' + "".join(g) + "</g>")
    out.append(f'<rect x="-10" y="{CT}" width="620" height="5" fill="#E8EEF8"/><rect x="-10" y="{CT + 5}" width="620" height="3" fill="#1E2048" opacity="0.4"/>')
    for _ in range(30):
        x, y = rnd.uniform(-10, 610), rnd.uniform(CT + 22, 350)
        out.append(snowy_fir(x, y, rnd.uniform(16, 30), rnd.randrange(999)))
    # the funicular climbing the cliff in its lit glass cabin
    out.append(f'<polygon points="{P([(176, 352), (186, 352), (240, CT + 4), (232, CT + 4)])}" fill="#1E1A30"/>'
               f'<line x1="181" y1="352" x2="236" y2="{CT + 4}" stroke="#8A88A8" stroke-width="1"/>')
    out.append(glow(206, 306, 30, "#FFD08A", f"{u}-fg", 0.6))
    out.append(f'<g transform="translate(211 314) rotate(-52.6)"><rect x="-15" y="-15" width="30" height="15" rx="2" fill="#B8303A"/>'
               '<rect x="-12" y="-12.5" width="24" height="7" fill="#FFE2A0"/><path d="M -4 -12.5 L -4 -5.5 M 4 -12.5 L 4 -5.5" stroke="#B8303A" stroke-width="1.4"/>'
               '<rect x="-15" y="-16" width="30" height="2.4" fill="#F4F6FC"/></g>')
    # ---- the lower town: snow-laden stone houses with firewall gables and chimneys, warm windows
    out.append(f'<rect x="-10" y="340" width="620" height="104" fill="#3A3A5E"/>')
    back = [(-14, 372, 66, 30, 18, 2), (52, 366, 58, 28, 16, 2), (110, 376, 70, 34, 18, 3), (250, 370, 64, 30, 16, 2), (314, 366, 72, 30, 18, 3), (386, 374, 60, 32, 16, 2), (446, 368, 74, 28, 18, 3), (520, 372, 90, 32, 18, 3)]
    for i, (x, b, w, wh, rh, d) in enumerate(back):
        out.append(stone_house(x, b, w, wh, rh, 40 + i, wall=rnd.choice(["#7A7488", "#8A8090", "#6E6A80"]), dormers=d, k=0.8))
    front = [(-20, 452, 120, 58, 30, 3, True), (96, 452, 88, 50, 26, 2, True), (184, 456, 110, 62, 30, 3, True), (380, 452, 100, 54, 28, 2, True), (478, 456, 140, 62, 32, 3, True)]
    for i, (x, b, w, wh, rh, d, sh) in enumerate(front):
        out.append(stone_house(x, b, w, wh, rh, 60 + i, wall=rnd.choice(["#9A90A0", "#A8A0AE", "#8E8698"]), dormers=d, shop=sh, k=1.15))
    # the snowy lane between, with a lamp and two walkers
    lane = [(294, 444), (300, 392), (372, 392), (380, 444)]
    out.append(f'<polygon points="{P(lane)}" fill="#DCE4F4"/><polygon points="{P([(300, 392), (372, 392), (366, 400), (306, 400)])}" fill="#FFD9A0" opacity="0.5"/>')
    out.append(f'<path d="M 318 444 Q 324 420 326 392 M 356 444 Q 352 420 350 392" stroke="#A8B4D8" stroke-width="2" fill="none" opacity="0.6"/>'
               + lg_rect(f"{u}-ls", 290, 404, 95, 40, "#6A74A8", 0.0, 0.45))
    out.append(glow(338, 380, 46, "#FFC878", f"{u}-lane", 0.6))
    out.append(f'<line x1="300" y1="444" x2="300" y2="372" stroke="#1E1A30" stroke-width="2.2"/><path d="M 300 372 l 8 0 l 0 4" stroke="#1E1A30" stroke-width="1.6" fill="none"/>'
               f'<path d="M 304 376 L 312 376 L 310 384 L 306 384 Z" fill="#FFE8A8"/>' + glow(308, 380, 18, "#FFD890", f"{u}-lamp", 0.9))
    out.append(figure(332, 416, 26, "#8A2A3A", head="#2A2030", legs="#2A2030") + figure(346, 418, 24, "#2A4A7A", head="#E8E0D8", legs="#2A2030"))
    # falling snow, nearer flakes bigger
    out.append(dots(260, 90, (-10, 40, 610, 444), "#FFFFFF", r=(0.7, 1.5), opacity=(0.45, 0.9)))
    out.append(dots(60, 91, (-10, 40, 610, 444), "#FFFFFF", r=(1.6, 2.6), opacity=(0.6, 0.95)))
    return "\n".join(out)


# ================================================================ BORA BORA — overwater bungalows in the lagoon under Mount Otemanu, golden hour
def thatch_fill(poly, seed, cols, n, dirn=(0, 1), sw=(0.8, 1.6), L=(4, 10)):
    """Short strokes of pandanus thatch combed in one direction, to be clipped to a roof face."""
    rnd = random.Random(seed)
    xs = [x for x, _ in poly]
    ys = [y for _, y in poly]
    out = []
    for _ in range(n):
        x, y = rnd.uniform(min(xs), max(xs)), rnd.uniform(min(ys), max(ys))
        l = rnd.uniform(*L)
        out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + dirn[0] * l:.1f}" y2="{y + dirn[1] * l:.1f}" stroke="{rnd.choice(cols)}" stroke-width="{rnd.uniform(*sw):.1f}" opacity="{rnd.uniform(0.4, 0.85):.2f}"/>')
    return "".join(out)


def bungalow(x, deck, k, u, seed, light=-1, lit_p=0.6):
    """Overwater bungalow in 3/4 view: stilts into the lagoon, a timber deck with a ladder, a house with a lit
    front and shaded side, under a steep hipped roof of golden pandanus thatch. (x, deck) = front-left corner
    of the deck; light=-1 when the sun is on the left."""
    rnd = random.Random(seed)
    w, d, hw, rh, st = 62 * k, 30 * k, 22 * k, 30 * k, 16 * k
    dx, dy = d, -d * 0.35  # depth axis goes back to the right
    out = []
    # stilts and their wet shadows
    for px in (x + 2 * k, x + w * 0.5, x + w - 2 * k, x + dx + 2 * k, x + w + dx - 2 * k):
        py = deck + (dy if px > x + w else 0) + 0
        out.append(f'<rect x="{px - 1.2 * k:.1f}" y="{py:.1f}" width="{2.4 * k:.1f}" height="{st:.1f}" fill="#4A3A34"/>')
        out.append(f'<rect x="{px - 1.2 * k:.1f}" y="{py + st:.1f}" width="{2.4 * k:.1f}" height="{st * 0.8:.1f}" fill="#4A3A34" opacity="0.3"/>')
    # deck (top face + front edge)
    dk = [(x - 6 * k, deck), (x + w + 4 * k, deck), (x + w + 4 * k + dx, deck + dy), (x - 6 * k + dx, deck + dy)]
    out.append(f'<polygon points="{P(dk)}" fill="#C89A6A"/>')
    out.append(f'<rect x="{x - 6 * k:.1f}" y="{deck:.1f}" width="{w + 10 * k:.1f}" height="{3 * k:.1f}" fill="#7A5A40"/>')
    out.append(f'<polygon points="{P([(x + w + 4 * k, deck), (x + w + 4 * k + dx, deck + dy), (x + w + 4 * k + dx, deck + dy + 3 * k), (x + w + 4 * k, deck + 3 * k)])}" fill="#5A4030"/>')
    # ladder down to the water
    lx = x + w * 0.2
    out.append(f'<path d="M {lx:.1f} {deck:.1f} l 0 {st:.1f} M {lx + 5 * k:.1f} {deck:.1f} l 0 {st:.1f}" stroke="#E8E0D0" stroke-width="{max(0.9, 1 * k):.1f}"/>')
    out.append("".join(f'<line x1="{lx:.1f}" y1="{deck + st * f:.1f}" x2="{lx + 5 * k:.1f}" y2="{deck + st * f:.1f}" stroke="#E8E0D0" stroke-width="{max(0.8, 0.9 * k):.1f}"/>' for f in (0.3, 0.6, 0.9)))
    # house: front wall (lit), side wall (shaded)
    fx0, fx1 = x + 6 * k, x + w - 6 * k
    fb = deck + dy * 0.25
    out.append(f'<polygon points="{P([(fx1, fb), (fx1 + dx * 0.6, fb + dy * 0.6), (fx1 + dx * 0.6, fb + dy * 0.6 - hw), (fx1, fb - hw)])}" fill="#7A5038"/>')
    out.append(f'<rect x="{fx0:.1f}" y="{fb - hw:.1f}" width="{fx1 - fx0:.1f}" height="{hw:.1f}" fill="#C88A58"/>')
    out.append(f'<g stroke="#8A5A3A" stroke-width="0.8" opacity="0.6">' + "".join(f'<line x1="{fx0:.1f}" y1="{fb - hw * f:.1f}" x2="{fx1:.1f}" y2="{fb - hw * f:.1f}"/>' for f in (0.25, 0.5, 0.75)) + "</g>")
    # big sliding glass doors glowing warm
    gx0, gx1 = fx0 + (fx1 - fx0) * 0.18, fx0 + (fx1 - fx0) * 0.82
    glass = rnd.choice(["#FFD488", "#FFC870"]) if rnd.random() < lit_p else "#5A6A8A"
    out.append(f'<rect x="{gx0:.1f}" y="{fb - hw * 0.85:.1f}" width="{gx1 - gx0:.1f}" height="{hw * 0.85:.1f}" fill="{glass}"/>')
    out.append("".join(f'<line x1="{gx0 + (gx1 - gx0) * f:.1f}" y1="{fb - hw * 0.85:.1f}" x2="{gx0 + (gx1 - gx0) * f:.1f}" y2="{fb:.1f}" stroke="#6A4A34" stroke-width="{max(0.8, k):.1f}"/>' for f in (0.33, 0.66)))
    # deck railing
    out.append(f'<line x1="{x - 6 * k:.1f}" y1="{deck - 6 * k:.1f}" x2="{x + w + 4 * k:.1f}" y2="{deck - 6 * k:.1f}" stroke="#E8D8C0" stroke-width="{max(0.8, 1.1 * k):.1f}"/>'
               + "".join(f'<line x1="{x - 6 * k + (w + 10 * k) * f:.1f}" y1="{deck - 6 * k:.1f}" x2="{x - 6 * k + (w + 10 * k) * f:.1f}" y2="{deck:.1f}" stroke="#E8D8C0" stroke-width="{max(0.7, 0.9 * k):.1f}"/>' for f in (0, 0.2, 0.4, 0.6, 0.8, 1)))
    # hipped thatch roof: front trapezoid (lit), side triangle (shade), deep overhang
    e0, e1 = (x - 4 * k, fb - hw + 3 * k), (x + w + 4 * k, fb - hw + 3 * k)
    r0, r1 = (x + w * 0.36 + dx * 0.3, fb - hw - rh + dy * 0.3), (x + w * 0.64 + dx * 0.3, fb - hw - rh + dy * 0.3)
    e2 = (x + w + 4 * k + dx * 0.75, fb - hw + 3 * k + dy * 0.75)
    front = [e0, r0, r1, e1]
    side = [e1, r1, e2]
    uid = f"{u}-bg{seed}"
    out.append(defs(f'<clipPath id="{uid}f"><polygon points="{P(front)}"/></clipPath><clipPath id="{uid}s"><polygon points="{P(side)}"/></clipPath>'))
    out.append(f'<polygon points="{P(side)}" fill="#8A6034"/><polygon points="{P(front)}" fill="#E0AE62"/>')
    if k > 0.45:
        out.append(f'<g clip-path="url(#{uid}f)">' + thatch_fill(front, seed, ["#F6D08A", "#B8823E", "#FFE6A8", "#9A6A34"], int(70 * k * k + 20), (0.1, 1), L=(4 * k, 10 * k)) + "</g>")
        out.append(f'<g clip-path="url(#{uid}s)">' + thatch_fill(side, seed + 1, ["#6A4626", "#A87A44", "#5A3A20"], int(40 * k * k + 10), (0.3, 1), L=(4 * k, 9 * k)) + "</g>")
    out.append(f'<polyline points="{P([e0, e1])}" stroke="#7A5030" stroke-width="{max(1, 2 * k):.1f}"/>')
    out.append(f'<path d="M {e0[0]:.1f} {e0[1]:.1f} ' + " ".join(f'L {e0[0] + (e1[0] - e0[0]) * i / 16:.1f} {e0[1] + (2 + (i % 2) * 2.5) * k:.1f}' for i in range(17)) + f'" stroke="#B8823E" stroke-width="{max(0.8, 1.2 * k):.1f}" fill="none"/>')
    out.append(f'<polyline points="{P([r0, r1])}" stroke="#FFE6A8" stroke-width="{max(1.2, 2.4 * k):.1f}" stroke-linecap="round"/>')
    out.append(f'<polyline points="{P([e0, r0])}" stroke="#FFE6A8" stroke-width="{max(1, 1.6 * k):.1f}" opacity="0.8"/>')
    return "".join(out)


def vaa(x, wl, L, flip=False):
    """Polynesian outrigger canoe (va'a) with a paddler: slim hull, two booms and the ama float."""
    f = -1 if flip else 1
    return (f'<g transform="translate({x} {wl}) scale({f} 1)">'
            f'<path d="M {-L / 2} -3 Q 0 2 {L / 2} -5 L {L / 2 - 4} 1 Q 0 4 {-L / 2 + 3} 1 Z" fill="#F4EEE4"/>'
            f'<path d="M {-L / 2 + 3} 1 Q 0 4 {L / 2 - 4} 1" stroke="#B8302A" stroke-width="1.6" fill="none"/>'
            f'<path d="M {-L * 0.2} -3 L {-L * 0.22} -14 M {L * 0.18} -3 L {L * 0.16} -14" stroke="#5A4030" stroke-width="1.4"/>'
            f'<path d="M {-L * 0.3} -14 Q 0 -16 {L * 0.25} -14" stroke="#3A2A20" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
            f'<path d="M 0 -4 Q -2 -12 2 -16 Q 6 -12 5 -4 Z" fill="#1E3A6A"/><circle cx="3" cy="-19" r="3" fill="#6A3A2A"/>'
            f'<line x1="9" y1="-22" x2="-4" y2="6" stroke="#5A3A20" stroke-width="1.6"/><ellipse cx="-4" cy="5" rx="3" ry="1.2" fill="#FFFFFF" opacity="0.8"/></g>')


def bora_bora():
    u = "bb"
    HZ = 286  # lagoon horizon at the island's foot
    out = [defs(
        lg(f"{u}-sky", [(0, "#3E4C9C"), (0.35, "#7A6AB0"), (0.62, "#E28EA0"), (0.85, "#FFB884"), (1, "#FFDCA6")], 0, 40, 0, HZ, units="userSpaceOnUse"),
        lg(f"{u}-rock", [(0, "#C8925A"), (0.3, "#7A6A4E"), (0.7, "#3E5A3E"), (1, "#2A4A36")], 0, 92, 0, HZ, units="userSpaceOnUse"),
        lg(f"{u}-lag", [(0, "#4AB6B8"), (0.18, "#3CC8C0"), (0.42, "#6ADCCC"), (0.62, "#36BAC4"), (0.85, "#1E92B0"), (1, "#167C9E")], 0, HZ, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="{HZ + 2}" fill="url(#{u}-sky)"/>')
    out.append(glow(-20, 230, 320, "#FFE2A8", f"{u}-sun", 0.8))
    # pink trade-wind clouds, one capping the peak
    out.append(cumulus(f"{u}-c1", 470, 150, 170, 36, 3, "#FFE0C8", "#F2A8A8", "#9A7AAA", hi="#FFF0DC", hi_op=0.6, light=-1))
    out.append(cumulus(f"{u}-c2", 120, 116, 120, 24, 4, "#FFE0C8", "#F2A8A8", "#9A7AAA", hi="#FFF0DC", hi_op=0.6, light=-1))
    out.append(streak_cloud(300, 78, 120, "#FFD0C0", 0.45, 4) + streak_cloud(520, 92, 70, "#FFD0C0", 0.4, 3))
    # Mount Pahia (left) and Mount Otemanu: a basalt plug with sheer walls, lit gold on its western face
    ctrl = [(-10, 268), (40, 250), (90, 214), (118, 182), (138, 190), (160, 170), (182, 192), (212, 196), (236, 176), (252, 138),
            (262, 106), (282, 96), (306, 100), (322, 112), (334, 150), (346, 186), (380, 206), (430, 226), (500, 246), (560, 262), (610, 270)]
    sv, line = massif(f"{u}-ot", ctrl, 9, HZ + 4, f"url(#{u}-rock)", shade="#2A3050", shade_op=0.5, amp=3, depth=4, decay=0.5, light=-1,
                      rim="#FFE0A0", rim_w=2.2, gullies=10, tex=("#2A3A2A", "#E8B878", "#4A6A3A"), tex_op=(0.2, 0.5), tex_n=1.6, spine_k=0.05,
                      haze="#E8A8A0", haze_top=200)
    out.append(sv)
    # jungle draping the lower slopes: rounded canopy painted in warm-lit greens
    jl = rough([(-10, 262), (60, 236), (120, 220), (200, 226), (250, 214), (300, 210), (350, 218), (420, 236), (500, 250), (610, 262)], 12, 6, 4)
    jpoly = jl + [(610, HZ + 2), (-10, HZ + 2)]
    JUNGLE = [("#24503A", "#5A8A3E"), ("#2E5A36", "#7AA048"), ("#1E4430", "#4A7A3A"), ("#3A6A3A", "#A8B858")]
    out.append(f'<g clip-path="url(#{u}-ot-c)">' + forest_mosaic(jpoly, 13, 50, 220, 3, 7, base="#24443A", pal=JUNGLE, cid=f"{u}-jg") + "</g>")
    # ferns and shrubs clinging to the ledges of the basalt walls
    out.append(f'<g clip-path="url(#{u}-ot-c)">' + patches(70, 14, (90, 110, 420, 222), ["#3E6A3A", "#4E7A3E", "#2E5034", "#6A8A44"], w=(3, 7), h=(1, 2.2), op=(0.5, 0.85)) + "</g>")
    out.append(lg_rect(f"{u}-ih", -10, 220, 620, HZ - 216, "#F0B0A0", 0.0, 0.4))
    # palm fringe along the shore
    shore = rough([(-10, HZ - 2), (200, HZ - 4), (400, HZ - 2), (610, HZ - 4)], 16, 2, 3)
    out.append(f'<polygon points="{P(shore + [(610, HZ + 2), (-10, HZ + 2)])}" fill="#F2E2C0"/>')
    rnd = random.Random(17)
    pf = []
    for _ in range(60):
        x = rnd.uniform(-10, 610)
        y = HZ - 3
        h = rnd.uniform(8, 16)
        lean = rnd.uniform(-0.3, 0.3)
        tx, ty = x + lean * h, y - h
        pf.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="#4A4030" stroke-width="1"/>'
                  + "".join(f'<path d="M {tx:.1f} {ty:.1f} q {math.cos(a) * 3:.1f} {-2:.1f} {math.cos(a) * 6:.1f} {math.sin(a) * 2 + 2:.1f}" stroke="#2E5A36" stroke-width="1.4" fill="none"/>' for a in (0.3, 2.8, 1.4, -0.5, 3.6)))
    out.append("".join(pf))
    # the lagoon: pale turquoise over sand, deepening toward us; the island mirrored in it
    out.append(f'<clipPath id="{u}-lk"><rect x="-10" y="{HZ}" width="620" height="170"/></clipPath>')
    out.append(f'<rect x="-10" y="{HZ}" width="620" height="170" fill="url(#{u}-lag)"/>')
    refl = f'<polygon points="{P(line + [(610, HZ + 4), (-10, HZ + 4)])}" fill="#3A5A4A"/>'
    out.append(mirror(HZ, refl, f"{u}-lk", 0.22))
    out.append(patches(30, 18, (-10, 300, 610, 340), ["#8AE8D8", "#A8F0E0", "#58D4C8"], w=(30, 80), h=(2, 5), op=(0.35, 0.6)))
    out.append(water_lines(150, 19, (-10, HZ + 2, 610, 444), ["#FFE8C8", "#B8F4EC", "#1E86A6", "#FFFFFF"], w=(8, 40), h=(1, 2), opacity=(0.25, 0.7)))
    # the sun's path on the water from the left
    out.append(water_lines(40, 20, (-10, 300, 220, 444), ["#FFE6B0", "#FFD49A"], w=(10, 40), h=(1, 2.2), opacity=(0.5, 0.9)))
    # boardwalk curving out from the motu, bungalows along it, far to near
    bw = [qpt((660, 430), (420, 360), (150, 312), t / 30) for t in range(31)]
    out.append(f'<polyline points="{P(bw)}" fill="none" stroke="#5A4030" stroke-width="4"/>'
               f'<polyline points="{P([(x, y - 1.5) for x, y in bw])}" fill="none" stroke="#D8B080" stroke-width="2.4"/>')
    out.append("".join(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y + 3 + (y - 300) * 0.05:.1f}" stroke="#4A3A30" stroke-width="1"/>' for x, y in bw[::2]))
    spots = [(0.79, 1), (0.64, -1), (0.5, 1), (0.36, -1), (0.22, 1), (0.08, -1)]
    for i, (t, side) in enumerate(spots):
        px, py = qpt((660, 430), (420, 360), (150, 312), t)
        k = 0.28 + (py - 306) / 124 * 1.2
        bx_ = px - 31 * k + side * 10 * k
        by_ = py - 10 * k + (8 * k if side > 0 else -6 * k)
        out.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{bx_ + 31 * k:.1f}" y2="{by_:.1f}" stroke="#C8A070" stroke-width="{max(1.2, 3 * k):.1f}"/>')
        out.append(f'<rect x="{bx_ - 4 * k:.1f}" y="{by_ + 16 * k:.1f}" width="{70 * k:.1f}" height="{10 * k:.1f}" fill="#1E5A70" opacity="0.25"/>')
        out.append(bungalow(bx_, by_, k, u, 30 + i))
    # an outrigger canoe on the golden water
    out.append(f'<path d="M 132 372 q -30 3 -70 1" stroke="#FFF6E0" stroke-width="1.4" fill="none" opacity="0.7"/>')
    out.append(vaa(160, 372, 64))
    # leaning coconut palm from a sand spit at the right edge, framing the scene
    out.append(f'<path d="M 470 444 Q 540 410 620 404 L 620 444 Z" fill="#F2DEB4"/><path d="M 470 444 Q 540 412 620 406" stroke="#FFF6E0" stroke-width="2" fill="none"/>')
    out.append(coco_palm(612, 440, 276, -0.36, 21, light=-1, lit=("#9AB84A", "#C8D46A", "#E8E08A"), mid=("#2E5A36", "#3A6A3A", "#4A7A3E"), trunk=("#6A4A3A", "#A8805E", "#F2C890")))
    out.append(gulls([(380, 120, 9), (398, 128, 6)], "#5A3A5A", 1.6))
    return "\n".join(out)


# ================================================================ MILFORD SOUND — Mitre Peak over the still fjord, morning cloud after rain
def waterfall(pts, w, seed, col="#F4FAFA", op=0.95):
    """A plunging fall drawn as several broken white veils along a path, widening toward the foot."""
    rnd = random.Random(seed)
    out = [f'<polyline points="{P(pts)}" fill="none" stroke="#FFFFFF" stroke-width="{w * 2.6:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="0.14"/>']
    for k in range(4):
        off = (k - 1.5) * w * 0.35
        seg = [(x + off * (0.6 + i / len(pts)) + rnd.uniform(-0.6, 0.6), y) for i, (x, y) in enumerate(pts)]
        i = 0
        while i < len(seg) - 1:
            j = min(len(seg), i + rnd.randint(2, 5))
            out.append(f'<polyline points="{P(seg[i:j])}" fill="none" stroke="{col}" stroke-width="{w * rnd.uniform(0.35, 0.6):.1f}" stroke-linecap="round" opacity="{op * rnd.uniform(0.6, 1):.2f}"/>')
            i = j + (1 if rnd.random() < 0.3 else 0)
    return "".join(out)


def cruise_boat(x, wl, k, flip=False):
    """Small fjord cruise vessel: dark hull, two white decks with window bands, a red stripe and a mast."""
    f = -1 if flip else 1
    return (f'<g transform="translate({x} {wl}) scale({k * f} {k})">'
            '<path d="M -46 -8 L 40 -8 L 52 -14 L 48 0 Q 40 5 30 5 L -44 5 Z" fill="#1E2A3E"/>'
            '<rect x="-46" y="-9" width="96" height="2.4" fill="#C8303A"/>'
            '<path d="M -42 -9 L -42 -20 L 30 -20 L 40 -9 Z" fill="#F4F4F2"/><path d="M -30 -20 L -30 -29 L 16 -29 L 24 -20 Z" fill="#E8ECEE"/>'
            + "".join(f'<rect x="{-38 + i * 6.5}" y="-17" width="4.6" height="4" rx="1" fill="#2A3A52"/>' for i in range(11))
            + '<rect x="-26" y="-27" width="40" height="3.4" fill="#2A3A52"/>'
            '<line x1="-6" y1="-29" x2="-6" y2="-40" stroke="#E8ECEE" stroke-width="1.4"/><line x1="-12" y1="-36" x2="0" y2="-36" stroke="#E8ECEE" stroke-width="1"/>'
            '<path d="M -42 -20 L 30 -20" stroke="#FFFFFF" stroke-width="1"/></g>')


def kayak(x, wl, L, col="#F2B030", flip=False):
    f = -1 if flip else 1
    return (f'<g transform="translate({x} {wl}) scale({f} 1)">'
            f'<path d="M {-L / 2} 0 Q 0 -6 {L / 2} 0 Q 0 4 {-L / 2} 0 Z" fill="{col}"/><path d="M {-L / 2} 0 Q 0 4 {L / 2} 0" stroke="#8A5A1A" stroke-width="1.2" fill="none"/>'
            f'<path d="M -4 -2 Q -4 -12 0 -14 Q 4 -12 4 -2 Z" fill="#C8303A"/><circle cx="0" cy="-17" r="3.2" fill="#2A2A34"/>'
            f'<line x1="-14" y1="-4" x2="14" y2="-14" stroke="#2A2A34" stroke-width="1.4"/><path d="M -16 -3 l -3 1 l 1 2 Z M 14 -14 l 4 -2 l -1 3 Z" fill="#2A2A34"/>'
            f'<ellipse cx="-17" cy="0.5" rx="4" ry="1" fill="#FFFFFF" opacity="0.7"/></g>')


def milford_sound():
    u = "mf"
    WL = 300
    out = [defs(
        lg(f"{u}-sky", [(0, "#5E7EA8"), (0.4, "#9AB4CC"), (0.75, "#D2DEE4"), (1, "#EEF0E8")], 0, 40, 0, WL, units="userSpaceOnUse"),
        lg(f"{u}-mitre", [(0, "#C8CCD0"), (0.18, "#8A9498"), (0.45, "#4E6464"), (0.75, "#24443E"), (1, "#18342E")], 0, 90, 0, WL, units="userSpaceOnUse"),
        lg(f"{u}-wallL", [(0, "#2E4A46"), (0.5, "#1E3A34"), (1, "#14302A")], 0, 40, 0, WL, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#A8B8C8"), (1, "#7E98A8")], 0, 140, 0, WL, units="userSpaceOnUse"),
        lg(f"{u}-mid", [(0, "#6E8A94"), (1, "#4A6A70")], 0, 120, 0, WL, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#9AB4BC"), (0.12, "#4E7A80"), (0.5, "#24525A"), (1, "#163E48")], 0, WL, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-seaov", [(0, "#A8C2C8", 0.35), (0.3, "#2A5A62", 0.45), (1, "#123A44", 0.8)], 0, WL, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="{WL + 2}" fill="url(#{u}-sky)"/>')
    out.append(glow(560, 70, 260, "#FFF6DC", f"{u}-sun", 0.7))
    out.append(streak_cloud(300, 110, 150, "#FFFFFF", 0.4, 5) + streak_cloud(520, 132, 90, "#FFFFFF", 0.35, 4))
    # far walls toward the Tasman Sea, pale with distance
    poly, fl = ridge_poly([(150, 310), (180, 220), (214, 196), (246, 210), (276, 188), (300, 214), (330, 310)], 4, amp=5, fill=f"url(#{u}-far)")
    out.append(poly)
    out.append(mist(250, 250, 120, 24, "#EEF2F4", f"{u}-m0", 0.8))
    # the Lion and the middle walls
    poly, ml = ridge_poly([(130, 310), (160, 250), (196, 226), (222, 240), (250, 258), (290, 300)], 6, amp=5, fill=f"url(#{u}-mid)")
    out.append(poly)
    out.append(f'<clipPath id="{u}-mc"><polygon points="{P(ml + [(290, 310), (130, 310)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-mc)">' + streaks(40, 7, (130, 220, 290, 300), ["#A8C0C4", "#3A5A60"], w=(1, 2.4), length=(8, 26), opacity=(0.3, 0.6), slant=0.2) + "</g>")
    # Mitre Peak: a sheer pyramid of rock from the water to the cloud, rainforest on its lower flanks
    ctrl = [(262, 302), (300, 264), (330, 226), (352, 186), (368, 150), (382, 120), (396, 100), (408, 84), (416, 78), (424, 88), (432, 96),
            (440, 92), (452, 116), (466, 150), (480, 186), (498, 222), (528, 252), (566, 268), (610, 280)]
    ctrl = [(x, 302 - (302 - y) * 0.94) for x, y in ctrl]  # keep the summit inside the print-safe area
    sv, mline = massif(f"{u}-mp", ctrl, 19, WL + 4, f"url(#{u}-mitre)", shade="#1E2E3A", shade_op=0.45, amp=2.4, depth=4, decay=0.5, light=-1,
                       rim="#FFF6DC", rim_w=2, gullies=12, tex=("#24343A", "#C8D4D4", "#3E5E4A"), tex_op=(0.2, 0.5), tex_n=1.6, spine_k=0.05,
                       snow="#F2F4F6", snow_y=104, snow_amp=10)
    out.append(sv)
    # rainforest climbing the flanks in a ragged edge
    fe = rough([(250, 302), (296, 274), (330, 254), (360, 236), (390, 232), (420, 224), (450, 226), (480, 230), (520, 248), (560, 260), (610, 270)], 23, 16, 5)
    fpoly = fe + [(610, WL + 2), (240, WL + 2)]
    BUSH = [("#1E3E30", "#3E6A44"), ("#24483A", "#4E7A4A"), ("#18362C", "#2E5A3E"), ("#2A4E36", "#5E8A4E")]
    out.append(forest_mosaic(fpoly, 24, 40, 260, 2.5, 6, base="#1A3A30", pal=BUSH, cid=f"{u}-fo"))
    out.append(f'<g clip-path="url(#{u}-mp-c)">' + patches(60, 25, (300, 176, 560, 236), ["#1E3E30", "#2E5A3E", "#3E6A44"], w=(3, 8), h=(1.5, 4), op=(0.6, 0.95)) + "</g>")
    # rain-fed falls streaking down the peak after the night's rain
    for k, (x, y0, y1) in enumerate(((396, 134, 210), (446, 150, 214), (480, 196, 250))):
        pts = rough([(x, y0), (x + 4, (y0 + y1) / 2), (x + 2, y1)], 70 + k, 3, 3)
        out.append(waterfall(pts, 2.2, 70 + k, op=0.8))
    # low cloud lying across the mountain's waist
    out.append(mist(480, 176, 140, 12, "#F4F6F6", f"{u}-m1", 0.8) + mist(560, 168, 70, 10, "#FFFFFF", f"{u}-m1b", 0.7)
               + mist(350, 200, 80, 9, "#F4F6F6", f"{u}-m2", 0.7) + mist(420, 186, 50, 7, "#FFFFFF", f"{u}-m2b", 0.6))
    # the near wall on the left: dark, wet, streaked with green, with a big fall plunging into the sound
    lw = rough([(-20, 40), (40, 52), (80, 70), (120, 104), (156, 150), (184, 212), (204, 262), (220, 302)], 31, 8, 4)
    lpoly = lw + [(220, 304), (-20, 304)]
    out.append(f'<polygon points="{P(lpoly)}" fill="url(#{u}-wallL)"/>')
    out.append(f'<clipPath id="{u}-lc"><polygon points="{P(lpoly)}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-lc)">'
               + streaks(130, 32, (-20, 40, 220, 304), ["#0E2420", "#4E6E62", "#2E4E44", "#6E8A7A"], w=(1.2, 3.4), length=(14, 50), opacity=(0.3, 0.7), slant=0.12)
               + blobs(70, 33, (-20, 60, 220, 304), ["#2E5A3E", "#3E6A44", "#24483A"], r=(3, 9), opacity=(0.5, 0.9), squash=0.6)
               + forest_mosaic(rough([(-20, 240), (60, 236), (130, 250), (200, 270), (230, 304), (-20, 304)], 34, 4, 3), 35, 20, 90, 2.5, 5.5, base="#163228", pal=BUSH)
               + "</g>")
    out.append(f'<polyline points="{P(lw[: len(lw) * 2 // 3])}" fill="none" stroke="#A8C8B8" stroke-width="1.6" opacity="0.6"/>')
    fall = rough([(118, 104), (122, 150), (128, 200), (132, 250), (134, 298)], 36, 3, 3)
    out.append(waterfall(fall, 5, 36))
    out.append(waterfall(rough([(60, 70), (62, 140), (66, 200)], 37, 2, 3), 2, 37, op=0.75))
    out.append(mist(60, 74, 110, 16, "#F4F6F6", f"{u}-m3", 0.75) + mist(150, 160, 70, 9, "#F4F6F6", f"{u}-m4", 0.6))
    out.append(mist(132, 296, 54, 14, "#FFFFFF", f"{u}-spray", 0.9) + mist(140, 284, 30, 16, "#FFFFFF", f"{u}-spray2", 0.6))
    # the sound: dark, still, a silver mirror near the far shore
    out.append(f'<clipPath id="{u}-wc"><rect x="-10" y="{WL}" width="620" height="150"/></clipPath>')
    out.append(f'<rect x="-10" y="{WL}" width="620" height="150" fill="url(#{u}-sea)"/>')
    refl = (f'<polygon points="{P(mline + [(610, WL + 6), (250, WL + 6)])}" fill="#4E6A6A"/>'
            f'<polygon points="{P(fpoly)}" fill="#1E3A34"/><polygon points="{P(lpoly)}" fill="#14302A"/>'
            f'<polygon points="{P(fl + [(330, WL + 6), (150, WL + 6)])}" fill="#9AB0BC"/>')
    out.append(mirror(WL, refl, f"{u}-wc", 0.55))
    out.append(f'<polyline points="{P([(132, WL + 2), (134, WL + 40)])}" stroke="#E8F4F4" stroke-width="3" opacity="0.35"/>')
    out.append(f'<rect x="-10" y="{WL}" width="620" height="150" fill="url(#{u}-seaov)"/>')
    out.append(water_lines(150, 38, (-10, WL + 3, 610, 444), ["#C8DCE0", "#5E8A8E", "#E8F2F2", "#1E4A52"], w=(10, 50), h=(1, 2), opacity=(0.25, 0.7)))
    out.append(f'<rect x="-10" y="{WL}" width="620" height="2" fill="#E8F0F0" opacity="0.6"/>')
    # the cruise boat heading for the falls, its wake fanning back across the sound
    bx, by = 262, 330
    wake = []
    wr = random.Random(39)
    for j in range(20):
        t = j / 19
        for sgn in (-1, 1):
            if wr.random() < 0.25:
                continue
            wake.append(f'<path d="M {bx + 48 + t * 160 + wr.uniform(-3, 3):.1f} {by + 4 + sgn * (1 + t * 12) * (0.6 if sgn < 0 else 1):.1f} q {5 + t * 4:.1f} {sgn * -1:.1f} {10 + t * 6:.1f} 0" '
                        f'stroke="#F0F6F6" stroke-width="{1.8 - t:.1f}" fill="none" stroke-linecap="round" opacity="{0.85 - t * 0.6:.2f}"/>')
    out.append("".join(wake))
    out.append(f'<rect x="{bx - 44}" y="{by + 5}" width="96" height="5" fill="#0E2A32" opacity="0.4"/>')
    out.append(cruise_boat(bx, by, 0.9, flip=True))
    # foreground: dark wet boulders on the foreshore, a sea kayak, tree-fern fronds arching in from the corner
    out.append(kayak(430, 402, 54, flip=True))
    out.append(f'<path d="M 456 404 q 30 2 70 0" stroke="#E8F2F2" stroke-width="1.2" fill="none" opacity="0.6"/>')
    rk = rough([(-20, 400), (30, 390), (80, 396), (130, 414), (170, 444)], 40, 5, 3)
    out.append(f'<polygon points="{P(rk + [(-20, 444)])}" fill="#2A3A3E"/>')
    for i, (bx_, by_, rx, ry) in enumerate(((20, 404, 40, 20), (90, 418, 34, 18), (140, 438, 36, 16), (-6, 432, 40, 22))):
        out.append(boulder(bx_, by_, rx, ry, 90 + i, u, lit="#8A9AA0", mid="#4E5E66", dark="#24323A", water=by_ + ry * 0.4))
    tree = []
    for i, (ang, L, dr) in enumerate(((-58, 150, 40), (-30, 170, 60), (-80, 130, 30), (-10, 150, 70), (-100, 100, 26))):
        tree.append(frond((-14, 470), ang, L, dr, 20, "#3A4A2A", ["#2E5A2E", "#3E6E34", "#5A8A3E", "#7AA04A"], 400 + i, sw=2.2, n=22, spread=60, grav=0.7, rw=2.6))
    out.append("".join(tree))
    for i, (ang, L, dr) in enumerate(((-122, 140, 40), (-150, 150, 60), (-100, 120, 30))):
        out.append(frond((626, 460), ang, L, dr, 18, "#3A4A2A", ["#2A5230", "#3A6634", "#4E7E3A"], 420 + i, sw=2.0, n=20, spread=60, grav=0.7, rw=2.4))
    out.append(gulls([(200, 150, 8), (214, 158, 6)], "#2A3A4A", 1.5))
    return "\n".join(out)


def poster(collection, slug, name, sub, art, band, rule, namec, subc, name_max=90):
    """Same layout as poster.poster, but measured on Anton's real outlines (cap 0.867 em, accents up to
    1.1 em) so an accented capital (CANCÚN, QUÉBEC) never touches the rule above the band."""
    accent = any(ch in "ÁÉÍÓÚÂÊÔÀÈÃÕ" for ch in name)
    size = 76 if accent else name_max
    while size > 40 and measure(name, ANTON, size, 0.03 * size) > 500:
        size -= 1
    ssz = fit_size(sub, MONO, 19, 500, 4.2)
    if accent:
        ny = 502.0  # accent tops at ny - 1.1 em stay ~9 px clear of the rule
    else:
        cap = 0.735 * size
        total = cap + 18 + ssz * 0.7
        ny = ART_H + 5 + (556 - ART_H - 5 - total) / 2 + cap
    sy = ny + 18 + ssz * 0.7
    body = (f'<rect width="600" height="600" fill="{band}"/>\n'
            f'<svg x="0" y="0" width="600" height="{ART_H}" viewBox="0 0 600 444" preserveAspectRatio="xMidYMax slice">\n{art.strip()}\n</svg>\n'
            f'<rect x="0" y="{ART_H}" width="600" height="5" fill="{rule}"/>\n'
            f'<text x="{300 + 0.015 * size:.1f}" y="{ny:.1f}" text-anchor="middle" {ANTON} font-size="{size}" letter-spacing="{0.03 * size:.1f}" fill="{namec}">{esc(name)}</text>\n'
            f'<text x="302" y="{sy:.1f}" text-anchor="middle" {MONO} font-size="{ssz}" letter-spacing="4.2" fill="{subc}">{esc(sub)}</text>')
    save(collection, slug, body)


BUILD = {
    "cancun": (cancun, "CANCÚN", "MEXICO · CARIBBEAN", "#0E5266", "#FF8E6E", "#FFF4EC", "#8EE8DC"),
    "patagonia": (patagonia, "PATAGONIA", "ARGENTINA · CHILE", "#2E1E40", "#F2784A", "#FFF1E6", "#F6B49A"),
    "quebec-city": (quebec_city, "QUÉBEC CITY", "CANADA · QUÉBEC", "#141C3C", "#4FB59A", "#FFF6EA", "#F6C77A"),
    "bora-bora": (bora_bora, "BORA BORA", "FRENCH POLYNESIA", "#2A2458", "#FF9A6A", "#FFF2E4", "#8EE6DA"),
    "milford-sound": (milford_sound, "MILFORD SOUND", "NEW ZEALAND · FIORDLAND", "#16302E", "#9ED2C4", "#F2F6F2", "#9ED2C4"),
    "banff": (banff, "BANFF", "CANADA · ALBERTA", "#123A44", "#E0402E", "#F4FBFA", "#7EDCD8"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("world", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
