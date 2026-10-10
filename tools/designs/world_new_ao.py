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
                          strokes_h, patches, canopy)
from world_painted import cumulus, streak_cloud, gulls, mix, Q, water_lines
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
    out.append(f'<ellipse cx="{cx - light * 26:.0f}" cy="{post_base + 8:.0f}" rx="{rx * 1.05:.0f}" ry="{ry * 1.1:.0f}" fill="#8E9AC8" opacity="0.35"/>')
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
    mid_bot = (mid_top[0], mid_top[1] + sag * 0.75)
    top = [qpt(s0, mid_top, s1, t / 20) for t in range(21)]
    bot = [qpt((s0[0] + 2, s0[1] + 6), mid_bot, (s1[0] - 2, s1[1] + 6), t / 20) for t in range(21)]
    out = [f'<clipPath id="{u}-hm"><polygon points="{P(top + bot[::-1])}"/></clipPath>']
    # strings
    st = []
    for i in range(9):
        f = i / 8
        st.append(f'<line x1="{ax}" y1="{ay}" x2="{s0[0] + f * 2:.1f}" y2="{s0[1] + f * 6:.1f}"/>')
        st.append(f'<line x1="{bx}" y1="{by}" x2="{s1[0] - f * 2:.1f}" y2="{s1[1] + f * 6:.1f}"/>')
    out.append('<g stroke="#F4E8D0" stroke-width="1" opacity="0.9">' + "".join(st) + "</g>")
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
    fp = []
    for i in range(9):
        fx, fy = 250 + i * 13 - (i % 2) * 4, 440 - i * 9 + (i % 2) * 3
        fp.append(f'<ellipse cx="{fx}" cy="{fy}" rx="{3.6 - i * 0.2:.1f}" ry="{2 - i * 0.1:.1f}" fill="#C8AE84" opacity="0.6"/>')
    out.append("".join(fp))
    # palapa with its pole, the hammock slung to the palm
    out.append(palapa(392, 238, 300, 104, 410, u))
    out.append(coco_palm(578, 452, 312, -0.2, 5, light=1))
    out.append(hammock((398, 348), (556, 334), 22, u))
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
    out.append(frigate(470, 150, 0.55) + frigate(500, 168, 0.4))
    return "\n".join(out)


# ================================================================ PATAGONIA — the Fitz Roy massif at first light, guanacos on the steppe
def lens_cloud(cx, cy, w, h, top, under, rim):
    """Lenticular cloud: a smooth lens with a lit underside, as stacked over the Patagonian peaks."""
    return (f'<path d="M {cx - w} {cy} Q {cx} {cy - h * 2} {cx + w} {cy} Q {cx} {cy + h * 0.9} {cx - w} {cy} Z" fill="{top}"/>'
            f'<path d="M {cx - w} {cy} Q {cx} {cy + h * 0.9} {cx + w} {cy} Q {cx} {cy + h * 0.2} {cx - w} {cy} Z" fill="{under}"/>'
            f'<path d="M {cx - w * 0.92} {cy + 0.5} Q {cx} {cy + h * 0.8} {cx + w * 0.92} {cy + 0.5}" fill="none" stroke="{rim}" stroke-width="1.6" opacity="0.9"/>')


def guanaco(x, base, h, grazing=False, flip=1, rim="#FFD6A0", coat="#B8703A", dark="#8A4E2A"):
    """Guanaco in profile facing left: long neck, small grey head with pointed ears, cinnamon back,
    white belly and inner legs, slender legs and a short dark tail. h = height to the ear tips."""
    s = h / 142
    sw = 1.8 / s
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({s * flip:.3f} {s:.3f})">']
    # far legs (darker)
    g.append(f'<path d="M 6 -54 L 5 -26 L 7 0 L 11 0 L 10 -26 L 12 -52 Z M 56 -56 C 62 -42 60 -32 58 -26 L 61 0 L 65 0 L 63 -26 C 66 -34 66 -46 64 -54 Z" fill="{dark}"/>')
    g.append(f'<path d="M 7 -26 L 8 -2 M 60 -24 L 62 -2" stroke="#E8DCCA" stroke-width="2" opacity="0.6"/>')
    # body
    g.append(f'<path d="M -8 -62 C -8 -76 6 -80 22 -78 C 40 -76 58 -82 70 -74 C 80 -68 80 -56 72 -50 C 60 -45 40 -47 20 -47 C 8 -47 -6 -50 -8 -62 Z" fill="{coat}"/>')
    g.append(f'<path d="M 0 -50 C 16 -46 44 -45 70 -51 C 64 -46 44 -44 22 -45 C 10 -45 2 -47 0 -50 Z" fill="#F2E8DA"/>')
    g.append(f'<path d="M 4 -49 C 20 -46 46 -46 68 -50 L 66 -56 C 46 -53 22 -53 6 -56 Z" fill="#F2E8DA" opacity="0.85"/>')
    # near legs: white inner, cinnamon outer
    g.append(f'<path d="M -4 -54 L -5 -26 L -3 0 L 1 0 L 1 -26 L 4 -50 Z M 64 -56 C 70 -42 68 -32 66 -26 L 69 0 L 73 0 L 71 -26 C 74 -34 76 -46 72 -54 Z" fill="{coat}"/>')
    g.append(f'<path d="M -1 -48 L -1 -26 L 0 -2 M 68 -40 L 69 -26 L 70 -2" stroke="#F2E8DA" stroke-width="2.4" opacity="0.8"/>')
    g.append(f'<path d="M -5 0 L 1 0 M 67 0 L 73 0" stroke="#2A1E1A" stroke-width="3"/>')
    # tail
    g.append(f'<path d="M 72 -72 C 82 -72 84 -64 80 -56 C 77 -61 75 -66 70 -66 Z" fill="#4A2E22"/>')
    if not grazing:
        g.append(f'<path d="M -8 -60 C -14 -76 -16 -100 -17 -120 L -6 -122 C -4 -102 4 -82 12 -72 Z" fill="{coat}"/>')
        g.append(f'<path d="M -8 -60 C -14 -76 -16 -100 -17 -118 L -13 -118 C -12 -100 -9 -80 -4 -64 Z" fill="#F2E8DA"/>')
        g.append(f'<path d="M -6 -131 C -16 -133 -28 -129 -36 -122 C -38 -117 -34 -113 -28 -113 C -22 -113 -14 -115 -4 -118 Z" fill="#6E6468"/>')
        g.append(f'<path d="M -34 -118 C -32 -114 -28 -113 -24 -114" stroke="#2A2224" stroke-width="2" fill="none"/>')
        g.append(f'<path d="M -8 -128 L -6 -142 L -2 -128 Z M -13 -129 L -14 -141 L -9 -129 Z" fill="#5A5054"/>')
        g.append(f'<circle cx="-20" cy="-124" r="2" fill="#1A1416"/>')
        g.append(f'<path d="M -6 -122 C -4 -102 4 -82 12 -72 C 22 -78 40 -76 58 -82 C 66 -80 74 -76 78 -68" fill="none" stroke="{rim}" stroke-width="{sw:.1f}" stroke-linecap="round"/>'
                 f'<path d="M -2 -128 L -6 -142 M -6 -131 C -16 -133 -28 -129 -36 -122" fill="none" stroke="{rim}" stroke-width="{sw * 0.8:.1f}" stroke-linecap="round"/>')
    else:
        g.append(f'<path d="M -6 -66 C -22 -64 -32 -46 -38 -22 L -29 -18 C -25 -40 -14 -54 6 -58 Z" fill="{coat}"/>')
        g.append(f'<path d="M -8 -58 C -20 -54 -28 -40 -32 -22 L -29 -20 C -24 -40 -16 -50 -4 -54 Z" fill="#F2E8DA"/>')
        g.append(f'<path d="M -40 -28 C -44 -18 -42 -8 -37 -3 C -33 -3 -30 -8 -29 -14 C -29 -22 -31 -28 -40 -28 Z" fill="#6E6468"/>')
        g.append(f'<path d="M -34 -28 L -27 -38 L -28 -26 Z M -38 -28 L -35 -39 L -33 -28 Z" fill="#5A5054"/>')
        g.append(f'<path d="M 6 -58 C 22 -78 40 -76 58 -82 C 66 -80 74 -76 78 -68 M -6 -66 C -22 -64 -32 -46 -38 -22" fill="none" stroke="{rim}" stroke-width="{sw:.1f}" stroke-linecap="round"/>')
    g.append("</g>")
    return "".join(g)


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


def patagonia():
    u = "ptg"
    LK = 314  # lake surface
    out = [defs(
        lg(f"{u}-sky", [(0, "#2C2C6C"), (0.32, "#5A4C8E"), (0.6, "#B07AA4"), (0.82, "#EAA6A4"), (1, "#F8CBA8")], 0, 40, 0, 290, units="userSpaceOnUse"),
        lg(f"{u}-gran", [(0, "#FF9A5A"), (0.25, "#F07050"), (0.55, "#B8506A"), (1, "#5A3462")], 0, 90, 0, 270, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#E4A0A8"), (0.5, "#B080A0"), (1, "#8A6A96")], 0, 130, 0, 260, units="userSpaceOnUse"),
        lg(f"{u}-ice", [(0, "#FFF0EA"), (0.5, "#E8DCEA"), (1, "#A8A8CC")], 0, 210, 0, 268, units="userSpaceOnUse"),
        lg(f"{u}-lake", [(0, "#6AA6B4", 0.55), (1, "#2E6A84", 0.9)], 0, LK, 0, 360, units="userSpaceOnUse"),
        lg(f"{u}-steppe", [(0, "#E8B068"), (0.45, "#C88A48"), (1, "#7A4E30")], 0, 330, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(-20, 300, 330, "#FFD2A0", f"{u}-dawn", 0.6))
    out.append(dots(26, 2, (300, 42, 600, 110), "#F6EEF6", r=(0.6, 1.3), opacity=(0.3, 0.8)))
    # setting moon in the west and the classic stacked lenticulars over the massif
    out.append(glow(530, 86, 30, "#F6EEF6", f"{u}-mg", 0.5) + '<circle cx="530" cy="86" r="8" fill="#F8F2F2"/><circle cx="534" cy="83" r="7.4" fill="#4E4486"/>')
    out.append(lens_cloud(452, 128, 92, 9, "#9A88B8", "#F6B0A0", "#FFE2C8"))
    out.append(lens_cloud(464, 114, 64, 7, "#A894C0", "#F8C0A8", "#FFE8D0"))
    out.append(lens_cloud(458, 102, 38, 5, "#B4A2CA", "#FAD0B8", "#FFF0DC"))
    out.append(lens_cloud(130, 112, 70, 5, "#9C8CBC", "#F4B8AC", "#FFE6D2"))
    # Cerro Torre group: thin needles further off, hazier
    sv, _ = massif(f"{u}-ct", [(-10, 250), (20, 220), (40, 186), (52, 148), (60, 136), (68, 176), (84, 162), (98, 196), (130, 220), (170, 250)],
                   11, 280, f"url(#{u}-far)", shade="#5A4A86", shade_op=0.45, amp=3, depth=4, light=1, rim="#FFD6C0", rim_w=1.6,
                   tex=("#6A4E80", "#F6C8C0"), tex_op=(0.15, 0.35), tex_n=0.6, spine_k=0.1)
    out.append(sv)
    # the Fitz Roy massif: Aguja de la S, Saint-Exupéry, Poincenot, Fitz Roy, Mermoz, Guillaumet
    ctrl = [(40, 290), (80, 246), (108, 216), (122, 232), (146, 194), (162, 214), (182, 190), (198, 156), (210, 176), (230, 116),
            (242, 158), (256, 146), (272, 104), (294, 90), (310, 92), (322, 112), (334, 140), (346, 196), (362, 176), (378, 146),
            (392, 184), (410, 198), (428, 168), (448, 206), (488, 232), (540, 250), (610, 262)]
    sv, line = massif(f"{u}-fr", ctrl, 21, 290, f"url(#{u}-gran)", shade="#3A2052", shade_op=0.55, amp=3, depth=4, decay=0.5, light=1,
                      rim="#FFE0B0", rim_w=2.2, gullies=10, ledges=(30, 0.35, 150, 232, "#FFEAE6"),
                      tex=("#5A2A44", "#FFC08A", "#8A3A50"), tex_op=(0.18, 0.45), tex_n=1.6, spine_k=0.08,
                      haze="#B87A9A", haze_top=200)
    out.append(sv)
    # glaciers draped under the towers, crevassed, catching pink light
    ice = rough([(70, 262), (120, 236), (170, 226), (220, 214), (270, 206), (320, 210), (370, 222), (420, 226), (470, 238), (530, 254)], 31, 6, 4)
    ice_low = rough([(530, 262), (450, 262), (380, 250), (320, 246), (250, 250), (180, 258), (110, 270), (70, 272)], 32, 5, 3)
    out.append(f'<polygon points="{P(ice + ice_low)}" fill="url(#{u}-ice)"/>')
    out.append(f'<clipPath id="{u}-ic"><polygon points="{P(ice + ice_low)}"/></clipPath>')
    rnd = random.Random(33)
    cr = []
    for _ in range(46):
        x0, y0 = rnd.uniform(80, 520), rnd.uniform(210, 262)
        L = rnd.uniform(8, 24)
        cr.append(f'<path d="M {x0:.0f} {y0:.0f} q {L / 2:.1f} {rnd.uniform(-2, 2):.1f} {L:.1f} {rnd.uniform(-1, 2):.1f}" stroke="#7A7AAE" stroke-width="{rnd.uniform(0.8, 1.8):.1f}" fill="none" opacity="0.6"/>')
    out.append(f'<g clip-path="url(#{u}-ic)">' + "".join(cr) + f'<polygon points="{P([(300, 200), (540, 230), (540, 270), (330, 260)])}" fill="#6A5A9A" opacity="0.25"/></g>')
    out.append(f'<polyline points="{P(ice[:6])}" fill="none" stroke="#FFF2E8" stroke-width="1.6" opacity="0.8"/>')
    # moraine ridges and lenga forest, still in blue shadow
    sv, ml = massif(f"{u}-mr", [(-10, 262), (60, 250), (130, 268), (200, 262), (280, 274), (360, 266), (440, 270), (520, 258), (610, 266)],
                    41, LK + 2, "#4A3A62", shade="#2A2044", shade_op=0.4, amp=5, light=1, tex=("#2A2040", "#7A5A7A"), tex_op=(0.2, 0.4), tex_n=1.0)
    out.append(sv)
    out.append(f'<g clip-path="url(#{u}-mr-c)">' + patches(70, 42, (-10, 270, 610, LK), ["#6A3A3A", "#8A4A3A", "#3A3A4A", "#5A4A3A", "#A0583E"], w=(6, 18), h=(2, 4), op=(0.5, 0.85)) + "</g>")
    out.append(trees_on(ml, 43, ["#3A2E46", "#46344A", "#5A3A44"], density=2.0, hmin=5, hmax=10, sink=3))
    # glacial lake: milky turquoise holding a faint reflection of the towers
    out.append(f'<clipPath id="{u}-lk"><rect x="-10" y="{LK}" width="620" height="60"/></clipPath>')
    out.append(f'<rect x="-10" y="{LK}" width="620" height="60" fill="#4A8C9C"/>')
    refl = (f'<polygon points="{P(line + [(610, 330), (40, 330)])}" fill="#E07A64"/>'
            f'<polygon points="{P(ice + ice_low)}" fill="#E8D8E4"/>')
    out.append(mirror(LK - 8, refl, f"{u}-lk", 0.35))
    out.append(f'<rect x="-10" y="{LK}" width="620" height="60" fill="url(#{u}-lake)"/>')
    out.append(ripple_lines(24, 44, (-10, LK + 3, 600, LK + 40), "#F6D2C8", op=(0.25, 0.55), w=(20, 70), sw=1.1))
    out.append(f'<rect x="-10" y="{LK - 0.5}" width="620" height="2" fill="#F6C8B8" opacity="0.6"/>')
    # golden steppe in the first sun: coirón tussocks and dark calafate bushes
    st = rough([(-10, 352), (90, 340), (200, 346), (320, 336), (440, 344), (610, 334)], 45, 5, 4)
    out.append(f'<polygon points="{P(st + [(610, 444), (-10, 444)])}" fill="url(#{u}-steppe)"/>')
    out.append(f'<polyline points="{P(st)}" fill="none" stroke="#FFD49A" stroke-width="2" opacity="0.7"/>')
    out.append(strokes_h(160, 46, (-10, 344, 610, 444), ["#F2C27A", "#A86A3A", "#FFE0A0", "#7A4A2A"], w=(4, 14), sw=(1, 2), op=(0.35, 0.75)))
    rnd = random.Random(47)
    tufts = []
    for _ in range(60):
        x, y = rnd.uniform(-10, 610), rnd.uniform(348, 444)
        k = 0.4 + (y - 340) / 104 * 1.2
        tufts.append((y, grass(int(9 * k + 4), rnd.randrange(9999), (x - 6 * k, y - 1, x + 6 * k, y), ["#F6CC80", "#D8A050", "#FFE6B0", "#9A6A3A"], h=(6 * k, 14 * k), sw=1.4 + 0.4 * k)))
    for _ in range(9):
        x, y = rnd.uniform(-10, 610), rnd.uniform(352, 420)
        k = 0.5 + (y - 340) / 104
        tufts.append((y, leafy(x, y - 6 * k, 14 * k, 7 * k, rnd.randrange(999), "#2E2A2A", "#4A3E30", "#7A6A3A", n=6, lx=-0.7, ly=-0.6, dab=0.3, rot=False)
                      + dots(int(8 * k), rnd.randrange(99), (x - 10 * k, y - 12 * k, x + 10 * k, y - 2), "#F6D04A", r=(0.8, 1.6), opacity=(0.8, 1))))
    # guanacos: a sentinel buck on the rise, a grazing female and her chulengo
    tufts.append((404, guanaco(436, 404, 96)))
    tufts.append((398, guanaco(330, 398, 70, grazing=True)))
    tufts.append((402, guanaco(380, 402, 48)))
    tufts.append((372, guanaco(160, 372, 40, grazing=True) + guanaco(118, 368, 38)))
    out.append("".join(v for _, v in sorted(tufts, key=lambda t: t[0])))
    out.append(grass(120, 48, (-10, 420, 610, 444), ["#F6CC80", "#D8A050", "#FFE6B0", "#9A6A3A"], h=(10, 24), sw=1.8))
    out.append(condor(520, 192, 64))
    out.append(birds_v([(170, 150, 9), (186, 158, 7)], "#4A3A6A", 1.6))
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
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("world", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
