"""American Places, painted edition (batch C): eight coastal and waterside posters — Niagara Falls, Key West,
Cape Canaveral, the Maine coast, Cape Cod, the Outer Banks, Tybee Island and the Florida Keys. Each one is its
own small gouache painting with a time of day, a light direction, atmospheric depth and truthful details."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from places_painted import Cam, puff_column, palm_tree
from poster import poster
import figures as F


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


# ---------------------------------------------------------------- shared helpers
def cloud_puffs(cx, cy, w, h, seed, body, light, shade=None, n=26, lit_dx=0.25, lit_dy=-0.3, flat=True):
    """Cumulus built from many overlapping puffs: a body colour, a lit cap on the sun side, optional shaded base."""
    rnd = random.Random(seed)
    puffs = []
    for _ in range(n):
        t = rnd.random()
        x = cx + (t - 0.5) * w
        dome = 1 - (2 * (t - 0.5)) ** 2
        r = h * (0.25 + 0.45 * dome) * rnd.uniform(0.7, 1.1)
        y = cy - dome * h * 0.45 * rnd.uniform(0.6, 1.1)
        if flat:
            y = min(y, cy - r * 0.35)
        puffs.append((x, y, r))
    out = [f'<g fill="{body}">' + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>' for x, y, r in puffs) + "</g>"]
    if shade:
        out.append(f'<g fill="{shade}" opacity="0.55">' + "".join(
            f'<circle cx="{x - r * lit_dx * 0.6:.1f}" cy="{y + r * 0.35:.1f}" r="{r * 0.6:.1f}"/>' for x, y, r in puffs) + "</g>")
    out.append(f'<g fill="{light}" opacity="0.8">' + "".join(
        f'<circle cx="{x + r * lit_dx:.1f}" cy="{y + r * lit_dy:.1f}" r="{r * 0.62:.1f}"/>' for x, y, r in puffs) + "</g>")
    if flat:
        out.append(f'<rect x="{cx - w / 2 - h:.1f}" y="{cy:.1f}" width="{w + 2 * h:.1f}" height="{h * 1.2:.1f}" fill="none"/>')
    return "".join(out)


def gulls(spec, color="#2E3A4A", sw=2):
    return (f'<g fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
            + "".join(f'<path d="M {x - s:.1f} {y:.1f} q {s * 0.5:.1f} {-s * 0.55:.1f} {s:.1f} 0 q {s * 0.5:.1f} {-s * 0.55:.1f} {s:.1f} 0"/>' for x, y, s in spec)
            + "</g>")


def ripples(n, seed, box, colors, w=(8, 30), h=1.6, opacity=(0.3, 0.8), persp=True):
    """Horizontal water glints; with persp they get wider and thicker toward the viewer."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        y = rnd.uniform(y0, y1)
        k = 0.35 + 0.65 * (y - y0) / max(1, y1 - y0) if persp else 1
        ww = rnd.uniform(*w) * k
        out.append(f'<rect x="{rnd.uniform(x0, x1) - ww / 2:.1f}" y="{y:.1f}" width="{ww:.1f}" height="{max(0.8, h * k):.1f}" rx="{h * k / 2:.1f}" '
                   f'fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*opacity):.2f}"/>')
    return "".join(out)


def person(x, base, h, coat, legs="#2A2430", head="#2A1E1A", rim=None, hat=None, pose="stand_back", facing=1, light=1, seed=None, pal=None, tint=None):
    """Small painted figure (figures.py); base = feet."""
    p = {"top": coat}
    if hat:
        p.update(hat_kind="cap", hat=hat)
    p.update(pal or {})
    return F.person(x, base, h, pose, facing, p, seed=int(x * 5 + base) if seed is None else seed, rim=rim, light=light, tint=tint)


def gull(x, y, s=1.0, rot=0, body="#FFFFFF", wing="#DCE2E6", under="#B8C4CC", tip="#26262A"):
    """Herring gull gliding, wings in a shallow M, seen slightly from below."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot}) scale({s})">'
            f'<path d="M -6 -1 Q -20 -14 -34 -12 Q -46 -10 -56 -2 Q -40 -4 -30 -2 Q -16 2 -6 5 Z" fill="{wing}"/>'
            f'<path d="M -56 -2 Q -48 -8 -44 -9 L -42 -3 Z" fill="{tip}"/>'
            f'<path d="M -6 5 Q -20 2 -32 -1 Q -18 6 -6 8 Z" fill="{under}"/>'
            f'<path d="M 6 -1 Q 20 -16 36 -15 Q 48 -13 58 -6 Q 42 -6 32 -3 Q 18 2 6 5 Z" fill="{wing}"/>'
            f'<path d="M 58 -6 Q 50 -12 46 -12 L 44 -5 Z" fill="{tip}"/>'
            f'<ellipse cx="0" cy="3" rx="15" ry="5" fill="{body}"/><ellipse cx="-1" cy="5" rx="12" ry="2.6" fill="{under}"/>'
            f'<circle cx="14" cy="0.5" r="4.2" fill="{body}"/><path d="M 17.5 0.2 L 24 1.6 L 17.5 2.8 Z" fill="#F2C040"/><circle cx="15.2" cy="-0.4" r="0.9" fill="#222"/>'
            f'<path d="M -14 2 L -24 0 L -22 6 Z" fill="{body}"/></g>')


# ---------------------------------------------------------------- lighthouse painted as a real tapered cylinder
def lighthouse_tower(uid, x, base, h, w0, w1, pattern="white", light_from=-1, lit=False, body="#F6F2EA", dark="#1E1E26",
                     base_col=None, lantern_glass="#BFD8E8", gallery=None, beam=None, windows=3, door=True):
    """Tapered tower whose rounding is painted with a side-to-side gradient (light_from -1 = lit from left).
    pattern: white | spiral (two black bands spiraling) | tybee (black base, white middle, black top)."""
    top = base - h
    gallery = gallery or dark
    poly = [(x - w0 / 2, base), (x - w1 / 2, top), (x + w1 / 2, top), (x + w0 / 2, base)]
    lo, hi = ("#FFFFFF", "#5A5A70") if light_from < 0 else ("#5A5A70", "#FFFFFF")
    out = [defs(lg(f"{uid}-rnd", [(0, lo, 0.35 if light_from < 0 else 0.45), (0.3, lo, 0.12 if light_from < 0 else 0.25), (0.55, "#888", 0),
                                  (0.8, hi, 0.25 if light_from < 0 else 0.1), (1, hi, 0.5 if light_from < 0 else 0.3)], 0, 0, 1, 0)),
           f'<clipPath id="{uid}-cl"><polygon points="{P(poly)}"/></clipPath>',
           f'<polygon points="{P(poly)}" fill="{body}"/>']
    g = []
    if pattern == "spiral":
        Hs = h / 4.2
        def r_at(y):
            t = (base - y) / h
            return (w0 + (w1 - w0) * t) / 2
        for k in range(-2, 7):
            c = base - k * Hs
            # a black band between edge(c) and edge(c - Hs/2), edges are helix projections
            e1, e2 = [], []
            for j in range(21):
                xn = -1 + 2 * j / 20
                y1 = c - Hs * math.asin(xn) / math.pi
                y2 = y1 - Hs * 0.5
                e1.append((x + xn * r_at(y1), y1))
                e2.append((x + xn * r_at(y2), y2))
            g.append(f'<polygon points="{P(e1 + e2[::-1])}" fill="{dark}"/>')
    elif pattern == "tybee":
        y_a = base - h * 0.34
        y_b = base - h * 0.80
        g.append(f'<rect x="{x - w0:.1f}" y="{y_a:.1f}" width="{w0 * 2:.1f}" height="{base - y_a + 2:.1f}" fill="{dark}"/>')
        g.append(f'<rect x="{x - w0:.1f}" y="{top - 2:.1f}" width="{w0 * 2:.1f}" height="{y_b - top + 2:.1f}" fill="{dark}"/>')
    if base_col:
        g.append(f'<rect x="{x - w0:.1f}" y="{base - h * 0.1:.1f}" width="{w0 * 2:.1f}" height="{h * 0.1 + 2:.1f}" fill="{base_col}"/>')
        g.append('<g stroke="#000" stroke-opacity="0.15" stroke-width="1">' + "".join(
            f'<line x1="{x - w0:.1f}" y1="{base - h * 0.1 + i * 4:.1f}" x2="{x + w0:.1f}" y2="{base - h * 0.1 + i * 4:.1f}"/>' for i in range(int(h * 0.1 / 4) + 1)) + "</g>")
    # windows spiral up the stair
    for i in range(windows):
        t = (i + 1) / (windows + 1)
        wy = base - h * t
        wx = x + (w0 + (w1 - w0) * t) * 0.12 * (1 if i % 2 else -1)
        g.append(f'<rect x="{wx - 2.2:.1f}" y="{wy - 4:.1f}" width="4.4" height="7" rx="2" fill="{"#FFD98E" if lit else "#3A3E4E"}"/>')
    if door:
        g.append(f'<path d="M {x - w0 * 0.1:.1f} {base:.1f} L {x - w0 * 0.1:.1f} {base - h * 0.06:.1f} Q {x:.1f} {base - h * 0.08:.1f} {x + w0 * 0.1:.1f} {base - h * 0.06:.1f} L {x + w0 * 0.1:.1f} {base:.1f} Z" fill="#3A2A2A"/>')
    g.append(f'<rect x="{x - w0:.1f}" y="{top:.1f}" width="{w0 * 2:.1f}" height="{h:.1f}" fill="url(#{uid}-rnd)"/>')
    out.append(f'<g clip-path="url(#{uid}-cl)">' + "".join(g) + "</g>")
    # gallery deck, railing, lantern room, dome, vent ball
    gw = w1 * 1.45
    lw = w1 * 0.78
    lh = w1 * 0.75
    out.append(f'<path d="M {x - gw / 2:.1f} {top:.1f} L {x + gw / 2:.1f} {top:.1f} L {x + w1 / 2:.1f} {top + w1 * 0.25:.1f} L {x - w1 / 2:.1f} {top + w1 * 0.25:.1f} Z" fill="{gallery}"/>')
    out.append(f'<rect x="{x - lw / 2 - 2:.1f}" y="{top - 4:.1f}" width="{lw + 4:.1f}" height="4" fill="{dark}"/>')
    out.append(f'<rect x="{x - lw / 2:.1f}" y="{top - 4 - lh:.1f}" width="{lw:.1f}" height="{lh:.1f}" fill="{"#FFE8A0" if lit else lantern_glass}"/>')
    out.append(f'<g stroke="{dark}" stroke-width="1.6">' + "".join(
        f'<line x1="{x - lw / 2 + i * lw / 3:.1f}" y1="{top - 4 - lh:.1f}" x2="{x - lw / 2 + i * lw / 3:.1f}" y2="{top - 4:.1f}"/>' for i in range(4)) + "</g>")
    if not lit:
        out.append(f'<rect x="{x - lw / 2:.1f}" y="{top - 4 - lh:.1f}" width="{lw * 0.35:.1f}" height="{lh:.1f}" fill="#FFFFFF" opacity="0.35"/>')
    out.append(f'<g stroke="{dark}" stroke-width="1.3" fill="none"><line x1="{x - gw / 2:.1f}" y1="{top - lh * 0.55:.1f}" x2="{x + gw / 2:.1f}" y2="{top - lh * 0.55:.1f}"/>'
               + "".join(f'<line x1="{x - gw / 2 + i * gw / 6:.1f}" y1="{top:.1f}" x2="{x - gw / 2 + i * gw / 6:.1f}" y2="{top - lh * 0.55:.1f}"/>' for i in range(7)) + "</g>")
    out.append(f'<path d="M {x - lw / 2 - 3:.1f} {top - 4 - lh:.1f} Q {x - lw / 2:.1f} {top - 4 - lh - lw * 0.55:.1f} {x:.1f} {top - 4 - lh - lw * 0.62:.1f} Q {x + lw / 2:.1f} {top - 4 - lh - lw * 0.55:.1f} {x + lw / 2 + 3:.1f} {top - 4 - lh:.1f} Z" fill="{dark}"/>')
    out.append(f'<line x1="{x:.1f}" y1="{top - 4 - lh - lw * 0.6:.1f}" x2="{x:.1f}" y2="{top - 4 - lh - lw * 0.95:.1f}" stroke="{dark}" stroke-width="1.6"/>'
               f'<circle cx="{x:.1f}" cy="{top - 4 - lh - lw * 0.75:.1f}" r="{max(1.6, lw * 0.09):.1f}" fill="{dark}"/>')
    if lit:
        out.insert(0, glow(x, top - 4 - lh / 2, lw * 4, "#FFE6A0", f"{uid}-lg", 0.8))
    return "".join(out)


def keeper_house(x, base, w, h, wall="#F6F2EA", roof="#B8423A", trim="#2E3A3A", shade_side=1, chimney=True, lit_win=False, seed=3):
    """1.5-storey keeper's house, side-gabled, seen front-on with a little shaded end wall."""
    rnd = random.Random(seed)
    eave = base - h * 0.62
    ridge = base - h
    end = w * 0.22
    out = []
    # end wall (shaded) with its gable
    if shade_side > 0:
        ex0, ex1 = x + w, x + w + end
    else:
        ex0, ex1 = x - end, x
    out.append(f'<polygon points="{P([(ex0, base), (ex0, eave), ((ex0 + ex1) / 2, ridge + 2), (ex1, eave + 2), (ex1, base)])}" fill="{wall}"/>')
    out.append(f'<polygon points="{P([(ex0, base), (ex0, eave), ((ex0 + ex1) / 2, ridge + 2), (ex1, eave + 2), (ex1, base)])}" fill="#4A4E66" opacity="0.32"/>')
    out.append(f'<rect x="{x:.1f}" y="{eave:.1f}" width="{w:.1f}" height="{base - eave:.1f}" fill="{wall}"/>')
    out.append('<g stroke="#000" stroke-opacity="0.07" stroke-width="1">' + "".join(
        f'<line x1="{x:.1f}" y1="{yy:.1f}" x2="{x + w:.1f}" y2="{yy:.1f}"/>' for yy in [eave + 3 + i * 3 for i in range(int((base - eave - 3) / 3))]) + "</g>")
    # roof plane
    if shade_side > 0:
        rp = [(x - 3, eave + 1), (x + 4, ridge), (ex0 + end / 2, ridge), (ex1 + 2, eave + 2)]
    else:
        rp = [(ex0 - 2, eave + 2), (ex0 + end / 2 - 4, ridge), (x + w - 4, ridge), (x + w + 3, eave + 1)]
    out.append(f'<polygon points="{P(rp)}" fill="{roof}"/>')
    out.append(f'<polygon points="{P([rp[0], rp[1], rp[2], rp[3]])}" fill="#000" opacity="0.0"/>')
    out.append(f'<line x1="{rp[1][0]:.1f}" y1="{ridge:.1f}" x2="{rp[2][0]:.1f}" y2="{ridge:.1f}" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="1.6"/>')
    if chimney:
        cx = x + w * 0.7
        out.append(f'<rect x="{cx:.1f}" y="{ridge - 10:.1f}" width="7" height="14" fill="#8A4A3A"/><rect x="{cx - 1:.1f}" y="{ridge - 12:.1f}" width="9" height="3" fill="#5A3A30"/>')
    # windows and door
    n = 3
    for i in range(n):
        wx = x + w * (i + 0.5) / n
        on = lit_win and rnd.random() < 0.7
        out.append(f'<rect x="{wx - 4.5:.1f}" y="{eave + (base - eave) * 0.18:.1f}" width="9" height="{(base - eave) * 0.42:.1f}" fill="{"#FFD98E" if on else "#3A4656"}" stroke="{trim}" stroke-width="1.2"/>')
    out.append(f'<rect x="{x + w * 0.5 - 4:.1f}" y="{base - (base - eave) * 0.0 - 1:.1f}" width="0" height="0"/>')
    # dormers
    for i in (0.3, 0.7):
        dx = x + w * i
        out.append(f'<path d="M {dx - 6:.1f} {eave - 1:.1f} L {dx - 6:.1f} {eave - 9:.1f} L {dx:.1f} {eave - 15:.1f} L {dx + 6:.1f} {eave - 9:.1f} L {dx + 6:.1f} {eave - 1:.1f} Z" fill="{wall}"/>'
                   f'<path d="M {dx - 7.5:.1f} {eave - 8:.1f} L {dx:.1f} {eave - 16:.1f} L {dx + 7.5:.1f} {eave - 8:.1f}" stroke="{roof}" stroke-width="2.6" fill="none"/>'
                   f'<rect x="{dx - 2.8:.1f}" y="{eave - 9:.1f}" width="5.6" height="7" fill="#3A4656"/>')
    return "".join(out)


# ---------------------------------------------------------------- Niagara Falls (Horseshoe Falls, afternoon)
def niagara():
    u = "niagara"
    out = [defs(
        lg(f"{u}-sky", [(0, "#3F7DC0"), (0.45, "#77AEDD"), (0.8, "#B8D8EE"), (1, "#DCEBF2")]),
        lg(f"{u}-up", [(0, "#A9CFC6"), (0.5, "#6FAE9E"), (1, "#4E9886")]),
        lg(f"{u}-fall", [(0, "#4FA48A"), (0.18, "#7FC4AC"), (0.5, "#CFEDE2"), (1, "#FFFFFF")]),
        lg(f"{u}-river", [(0, "#BFE3D8"), (0.25, "#4F9C8C"), (0.7, "#24685E"), (1, "#163F3E")]),
        lg(f"{u}-mist", [(0, "#C6D6E6"), (0.5, "#EEF4F8"), (1, "#FFFFFF")], 160, 0, 420, 0, units="userSpaceOnUse"),
        lg(f"{u}-cliffL", [(0, "#6E6458"), (0.5, "#8C7E6C"), (1, "#A69580")], 0, 0, 1, 0),
        lg(f"{u}-cliffR", [(0, "#8A7C6C"), (1, "#5A5048")], 0, 0, 1, 0),
        lg(f"{u}-haze", [(0, "#DCEBF2", 0), (1, "#DCEBF2", 0.9)]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    # fair-weather cumulus, lit from behind the viewer (soft, frontal light)
    out.append(cloud_puffs(110, 96, 170, 44, 3, "#E6EEF6", "#FFFFFF", shade="#B8C8DC"))
    out.append(cloud_puffs(500, 84, 150, 36, 7, "#E6EEF6", "#FFFFFF", shade="#B8C8DC"))
    out.append(cloud_puffs(330, 128, 120, 22, 11, "#DDE8F2", "#FFFFFF", shade="#BCCBDD", n=16))
    # far shore of the upper river: low woods and a hint of town, pale with distance
    poly, far = ridge_poly([(-10, 178), (90, 172), (200, 176), (330, 170), (460, 175), (610, 170)], 4, base=200, amp=3, fill="#9DB7B4")
    out.append(poly)
    rnd = random.Random(5)
    out.append('<g fill="#AFC4C6">' + "".join(f'<rect x="{x:.0f}" y="{170 - h:.0f}" width="{w:.0f}" height="{h + 8:.0f}"/>' for x, w, h in
                                         ((388, 12, 14), (402, 8, 22), (412, 14, 10), (430, 10, 18), (520, 12, 12), (536, 9, 20))) + "</g>")
    out.append(tree_line(far, 8, ["#8AA8A2", "#93AFA9", "#86A39C"], density=1.6, hmin=6, hmax=12))
    out.append(f'<rect x="0" y="150" width="600" height="40" fill="url(#{u}-haze)"/>')
    # upper river rushing to the brink: rapids streaks converging on the horseshoe
    out.append(f'<path d="M -10 186 L 610 184 L 610 262 L -10 262 Z" fill="url(#{u}-up)"/>')
    out.append(ripples(90, 12, (0, 188, 600, 240), ["#E6F4EE", "#FFFFFF", "#CFE6DE"], w=(10, 40), h=1.6, opacity=(0.4, 0.9)))
    # crest of the Horseshoe: far middle higher on screen, near sides lower (we look down on it)
    crest = [(-10, 262), (40, 248), (110, 230), (190, 218), (270, 213), (340, 214), (410, 222), (470, 234), (520, 248), (560, 262)]
    base = [(-10, 330), (60, 318), (140, 300), (220, 286), (290, 282), (350, 284), (420, 294), (480, 306), (540, 322), (560, 330)]
    curtain = crest + base[::-1]
    out.append(f'<clipPath id="{u}-cur"><polygon points="{P(curtain)}"/></clipPath>')
    out.append(f'<polygon points="{P(curtain)}" fill="url(#{u}-fall)"/>')
    # falling-water texture: vertical bands of green and white following the curve
    g = []
    for i in range(170):
        t = rnd.random()
        ci = t * (len(crest) - 1)
        j = int(ci)
        f = ci - j
        cx = crest[j][0] + (crest[j + 1][0] - crest[j][0]) * f
        cy = crest[j][1] + (crest[j + 1][1] - crest[j][1]) * f
        bx = base[j][0] + (base[j + 1][0] - base[j][0]) * f
        by = base[j][1] + (base[j + 1][1] - base[j][1]) * f
        L = (by - cy) * rnd.uniform(0.3, 1.0)
        y0 = cy + rnd.uniform(-2, (by - cy) * 0.5)
        col = rnd.choice(["#FFFFFF", "#F2FBF7", "#3E9478", "#2E7E66", "#BFE6D8"])
        g.append(f'<path d="M {cx + (bx - cx) * (y0 - cy) / (by - cy):.1f} {y0:.1f} l {(bx - cx) * L / (by - cy):.1f} {L:.1f}" stroke="{col}" '
                 f'stroke-width="{rnd.uniform(1.2, 3.4):.1f}" opacity="{rnd.uniform(0.35, 0.85):.2f}"/>')
    out.append(f'<g clip-path="url(#{u}-cur)" stroke-linecap="round">' + "".join(g) + "</g>")
    # the lip: bright white line where the water rolls over
    out.append(f'<polyline points="{P(crest)}" fill="none" stroke="#F4FFFA" stroke-width="3" opacity="0.9"/>')
    out.append(f'<polyline points="{P([(x, y + 4) for x, y in crest])}" fill="none" stroke="#2F7E68" stroke-width="2.5" opacity="0.55"/>')
    # Goat Island: wooded point on the right with its rock face, dividing the falls
    gi = [(560, 262), (548, 248), (556, 230), (580, 222), (610, 220), (610, 346), (560, 346)]
    out.append(f'<polygon points="{P(gi)}" fill="url(#{u}-cliffR)"/>')
    out.append(f'<clipPath id="{u}-gi"><polygon points="{P(gi)}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-gi)">' + streaks(40, 21, (548, 240, 610, 346), ["#4A4038", "#A89884", "#6A5E52"], w=(1, 3), length=(10, 40), opacity=(0.3, 0.7)) + "</g>")
    for k in range(16):
        r2 = random.Random(100 + k)
        x = 548 + k * 4.2 + r2.uniform(-3, 3)
        out.append(f'<circle cx="{x:.1f}" cy="{226 - r2.uniform(0, 10):.1f}" r="{r2.uniform(7, 12):.1f}" fill="{r2.choice(["#3E6A3E", "#4E7A44", "#5A8A4A"])}"/>')
        out.append(f'<circle cx="{x - 2:.1f}" cy="{220 - r2.uniform(0, 10):.1f}" r="{r2.uniform(3, 6):.1f}" fill="#8CB06A" opacity="0.7"/>')
    # the great spray cloud boiling out of the horseshoe: broad, translucent, drifting downstream and up
    rnd2 = random.Random(77)
    out.append(defs(rg(f"{u}-pw", [(0, "#FFFFFF", 0.5), (0.6, "#FFFFFF", 0.22), (1, "#FFFFFF", 0)]),
                    rg(f"{u}-ps", [(0, "#9FB4CC", 0.45), (1, "#9FB4CC", 0)])))
    sh, bo = [], []
    for i in range(80):
        t = rnd2.random()
        y = 296 - t * 190
        spread = 70 + 170 * abs(t - 0.25) ** 0.8
        x = 300 + rnd2.uniform(-1, 1) * spread + 40 * t
        r = 18 + 30 * rnd2.uniform(0.6, 1.2) * (0.6 + t * 0.6)
        bo.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>')
        if rnd2.random() < 0.5:
            sh.append(f'<circle cx="{x - r * 0.3:.1f}" cy="{y + r * 0.35:.1f}" r="{r * 0.8:.1f}"/>')
    out.append(f'<g fill="url(#{u}-ps)">' + "".join(sh) + "</g>")
    out.append(f'<g fill="url(#{u}-pw)">' + "".join(bo) + "</g>")
    out.append(mist(300, 300, 280, 36, "#FFFFFF", f"{u}-m1", 0.9))
    out.append(mist(140, 300, 120, 30, "#FFFFFF", f"{u}-m2", 0.8))
    out.append(mist(470, 306, 110, 28, "#FFFFFF", f"{u}-m3", 0.8))
    out.append(dots(120, 78, (160, 230, 460, 320), "#FFFFFF", r=(0.8, 2.2), opacity=(0.4, 0.9)))
    # rainbow in the spray (sun behind the viewer, afternoon): strongest low in the mist, fading upward and at the feet
    bands = ["#E8504A", "#F29A3C", "#F6D84A", "#6CC06A", "#4A9AD8", "#7A62C8"]
    rb = [lg(f"{u}-rb{i}", [(0, c, 0), (0.25, c, 0.7), (0.5, c, 0.3), (0.75, c, 0.7), (1, c, 0)], 0, 0, 1, 0) for i, c in enumerate(bands)]
    out.append(defs(*rb))
    out.append(f'<g fill="none">' + "".join(
        f'<path d="M {300 - (196 - i * 5.4):.1f} 334 A {196 - i * 5.4:.1f} {176 - i * 5.4:.1f} 0 0 1 {300 + (196 - i * 5.4):.1f} 334" stroke="url(#{u}-rb{i})" stroke-width="6"/>'
        for i in range(len(bands))) + "</g>")
    out.append(f'<path d="M {300 - 166:.1f} 334 A 166 146 0 0 1 {300 + 166:.1f} 334" fill="none" stroke="#FFFFFF" stroke-width="10" opacity="0.12"/>')
    # gorge walls: Canadian side on the left, layered dolostone over shale, wooded top with the railing walk
    lw = [(-10, 252), (30, 246), (70, 252), (96, 268), (118, 300), (126, 340), (140, 400), (150, 444), (-10, 444)]
    out.append(f'<polygon points="{P(lw)}" fill="url(#{u}-cliffL)"/>')
    out.append(f'<clipPath id="{u}-lw"><polygon points="{P(lw)}"/></clipPath>')
    lay = "".join(f'<path d="M -10 {y} Q 60 {y - 6} {150} {y + 10}" stroke="{c}" stroke-width="{w}" fill="none" opacity="0.55"/>' for y, c, w in
                  ((272, "#C9B8A0", 3), (284, "#5A5046", 2), (300, "#B4A28C", 4), (322, "#4E463E", 2.5), (348, "#9C8A76", 3), (372, "#4E463E", 2)))
    out.append(f'<g clip-path="url(#{u}-lw)">{lay}' + streaks(70, 31, (-10, 250, 150, 444), ["#4A4038", "#B8A890", "#6A5E52"], w=(1, 3), length=(10, 50), opacity=(0.25, 0.6)) +
               f'<polygon points="{P([(96, 268), (118, 300), (126, 340), (140, 400), (150, 444), (100, 444), (96, 380), (84, 300)])}" fill="#3E362E" opacity="0.35"/></g>')
    # talus with trees at the foot of the left wall
    for k in range(22):
        r2 = random.Random(200 + k)
        x = r2.uniform(-10, 150)
        y = 380 + (x / 150) * 30 + r2.uniform(0, 40)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r2.uniform(8, 16):.1f}" fill="{r2.choice(["#2E5A3A", "#3A6A40", "#2A4E34"])}"/>')
        out.append(f'<circle cx="{x - 3:.1f}" cy="{y - 5:.1f}" r="{r2.uniform(3, 7):.1f}" fill="#7EA65E" opacity="0.6"/>')
    # top of the left wall: lawn, walk, railing and visitors at the brink
    out.append('<path d="M -10 246 L 30 240 L 70 246 L 96 262 L 96 268 L 70 252 L 30 246 L -10 252 Z" fill="#6E9A4E"/>')
    out.append('<g stroke="#2E3A3A" stroke-width="1.6"><path d="M -10 238 L 30 232 L 70 238 L 92 252" fill="none"/>' +
               "".join(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + 8}"/>' for x, y in ((0, 237), (14, 235), (28, 233), (42, 234), (56, 236), (70, 238), (82, 245))) + "</g>")
    for x, c in ((40, "#C94A4A"), (50, "#3A5A8A"), (66, "#E0B040"), (76, "#4A4A6A")):
        out.append(person(x, 244 - (x / 70) * 2 + (4 if x > 70 else 0), 15, c, pose={40: "stand_back", 50: "photo", 66: "lean_back", 76: "stand_34"}[x], light=1, pal={"season": "summer"}))
    # lower river: churning, foam streaks swirling out of the mist
    out.append(f'<path d="M -10 318 Q 300 300 610 320 L 610 444 L -10 444 Z" fill="url(#{u}-river)"/>')
    out.append(defs(lg(f"{u}-rfl", [(0, "#1E3E34", 0.45), (1, "#1E3E34", 0)], 0, 0, 1, 0), lg(f"{u}-rfr", [(0, "#1E3E34", 0), (1, "#1E3E34", 0.5)], 0, 0, 1, 0)))
    out.append(f'<path d="M -10 330 L 140 320 Q 170 380 176 444 L -10 444 Z" fill="url(#{u}-rfl)"/>')
    out.append(f'<path d="M 610 326 L 540 328 Q 490 390 480 444 L 610 444 Z" fill="url(#{u}-rfr)"/>')
    out.append(ripples(120, 41, (120, 320, 560, 444), ["#E8F6F0", "#FFFFFF", "#A8D6C8"], w=(10, 46), h=2, opacity=(0.3, 0.75)))
    out.append('<g fill="none" stroke="#FFFFFF" stroke-linecap="round" opacity="0.45">' + "".join(
        f'<path d="M {x} {y} q {w / 2} {-6} {w} 0 q {w / 3} 4 {w * 0.6} 0" stroke-width="{sw}"/>' for x, y, w, sw in
        ((160, 344, 50, 2), (380, 340, 60, 2), (220, 372, 70, 2.5), (440, 380, 50, 2.5), (180, 410, 80, 3), (470, 420, 60, 3))) + "</g>")
    # right gorge wall, nearer
    rw = [(610, 300), (560, 312), (530, 340), (510, 390), (500, 444), (610, 444)]
    out.append(f'<polygon points="{P(rw)}" fill="#4E463E"/>')
    out.append(f'<clipPath id="{u}-rw"><polygon points="{P(rw)}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-rw)">' + streaks(40, 51, (500, 300, 610, 444), ["#6E6254", "#3A322C", "#8A7C6A"], w=(1, 3), length=(10, 40), opacity=(0.3, 0.7)) + "</g>")
    for k in range(14):
        r2 = random.Random(300 + k)
        x = r2.uniform(520, 610)
        y = 300 + (610 - x) * 0.3 + r2.uniform(-4, 14)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r2.uniform(8, 15):.1f}" fill="{r2.choice(["#2E5A3A", "#3A6A40", "#2A4E34"])}"/>')
        out.append(f'<circle cx="{x - 3:.1f}" cy="{y - 5:.1f}" r="{r2.uniform(3, 6):.1f}" fill="#7EA65E" opacity="0.55"/>')
    # near left bank: the foot of the Canadian wall, wooded, with boulders at the water
    lb = [(-10, 336), (30, 340), (64, 362), (84, 400), (96, 444), (-10, 444)]
    out.append(f'<polygon points="{P(lb)}" fill="#3E3630"/>')
    out.append(f'<clipPath id="{u}-lb"><polygon points="{P(lb)}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-lb)">' + streaks(30, 63, (-10, 330, 96, 444), ["#6E6254", "#2A241E", "#8A7C6A"], w=(1, 3), length=(10, 40), opacity=(0.3, 0.7)) + "</g>")
    for k in range(16):
        r2 = random.Random(400 + k)
        x = r2.uniform(-10, 60)
        y = 340 + x * 0.3 + r2.uniform(-10, 10)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r2.uniform(9, 16):.1f}" fill="{r2.choice(["#2E5A3A", "#3A6A40", "#2A4E34"])}"/>')
        out.append(f'<circle cx="{x + 3:.1f}" cy="{y - 5:.1f}" r="{r2.uniform(3, 7):.1f}" fill="#8CB06A" opacity="0.6"/>')
    for bx_, by_, r_ in ((70, 426, 20), (96, 440, 18), (40, 440, 24)):
        out.append(f'<ellipse cx="{bx_}" cy="{by_}" rx="{r_}" ry="{r_ * 0.6:.1f}" fill="#3A342E"/><ellipse cx="{bx_ - r_ * 0.25:.1f}" cy="{by_ - r_ * 0.25:.1f}" rx="{r_ * 0.55:.1f}" ry="{r_ * 0.25:.1f}" fill="#7A6E62" opacity="0.7"/>')
    out.append(blobs(20, 64, (50, 410, 130, 444), ["#FFFFFF", "#E8F6F0"], r=(3, 8), opacity=(0.6, 0.95), squash=0.4))
    for bx_, by_, r_ in ((520, 430, 26), (556, 414, 22), (492, 444, 20), (590, 440, 30)):
        out.append(f'<ellipse cx="{bx_}" cy="{by_}" rx="{r_}" ry="{r_ * 0.6:.1f}" fill="#3A342E"/><ellipse cx="{bx_ - r_ * 0.25:.1f}" cy="{by_ - r_ * 0.25:.1f}" rx="{r_ * 0.55:.1f}" ry="{r_ * 0.25:.1f}" fill="#7A6E62" opacity="0.7"/>')
    out.append(blobs(30, 62, (470, 404, 610, 444), ["#FFFFFF", "#E8F6F0"], r=(3, 9), opacity=(0.6, 0.95), squash=0.4))
    # tour boat heading into the mist, passengers in rain ponchos, a V of foam trailing toward us
    bx, by = 250, 356
    rw_ = random.Random(9)
    wk = []
    for sgn in (-1, 1):
        for j in range(6):
            t0 = j / 9
            x0 = bx + sgn * (26 + 100 * t0)
            y0 = by + 8 + 70 * t0
            L = rw_.uniform(10, 22) * (0.6 + t0)
            wk.append(f'<path d="M {x0:.1f} {y0:.1f} q {sgn * L * 0.5:.1f} {L * 0.15:.1f} {sgn * L:.1f} {L * 0.55:.1f}" stroke-width="{1.5 + 2 * t0:.1f}" opacity="{0.8 - 0.4 * t0:.2f}"/>')
    out.append('<g fill="none" stroke="#F4FFFA" stroke-linecap="round">' + "".join(wk) + "</g>")
    out.append(blobs(14, 61, (bx - 22, by + 4, bx + 22, by + 22), ["#FFFFFF", "#E8F6F0"], r=(3, 8), opacity=(0.5, 0.9), squash=0.45))
    out.append(f'<g transform="translate({bx} {by}) scale(0.82)">'
               '<path d="M -44 -6 L 44 -6 L 40 8 Q 0 14 -40 8 Z" fill="#F4F2EC"/><path d="M -44 -6 L 44 -6 L 43 -2 L -43 -2 Z" fill="#2E4E7A"/>'
               '<path d="M 0 -6 L 44 -6 L 40 8 Q 20 12 0 12 Z" fill="#7A8A9A" opacity="0.25"/>'
               '<rect x="-38" y="-22" width="76" height="16" fill="#F4F2EC"/><rect x="-34" y="-19" width="68" height="7" fill="#3E5E7E"/>'
               '<rect x="0" y="-22" width="38" height="16" fill="#7A8A9A" opacity="0.2"/>'
               '<rect x="-40" y="-25" width="80" height="4" rx="1.5" fill="#2E4E7A"/>'
               '<rect x="-30" y="-36" width="60" height="11" fill="#F4F2EC"/><rect x="-32" y="-38" width="64" height="3" fill="#2E4E7A"/>'
               + "".join(F.person(-35.2 + i * 6.5, -25, 15, "tiny", 1, {"top": "#3E86D6", "top_kind": "coat", "hair": "#5A9AE6", "bottom": "#2E4E7A"}, seed=660 + i, shadow=0)
                         for i in range(12))
               + "".join(F.person(-25.2 + i * 6.5, -38, 15, "tiny", 1, {"top": "#3E86D6", "top_kind": "coat", "hair": "#5A9AE6", "bottom": "#2E4E7A"}, seed=680 + i, shadow=0)
                         for i in range(9))
               + '<line x1="22" y1="-38" x2="22" y2="-54" stroke="#2E4E7A" stroke-width="1.8"/><path d="M 22 -54 L 33 -51 L 22 -47 Z" fill="#E8504A"/>'
               "</g>")
    # gulls riding the updraft
    out.append(gull(468, 350, 1.0, -6))
    out.append(gulls([(220, 150, 7), (240, 162, 5), (420, 132, 6), (180, 250, 5), (452, 266, 6)], "#3A4A5A", 1.8))
    return "\n".join(out)


# ---------------------------------------------------------------- Key West (sunset from the harbor pier)
def conch_house(x, base, w, h, body, trim="#FFFDF6", roof="#B8B4B0", shutter="#4E8A7A", shade=0.0, lit=None, seed=1):
    """Two-storey Key West conch house facing us: front gable with tin roof, double porch with gingerbread
    balusters, louvered shutters. shade darkens it (backlit), lit colours the sunny right edge."""
    rnd = random.Random(seed)
    eave = base - h * 0.78
    peak = base - h
    out = [f'<polygon points="{P([(x - 4, eave), (x + w / 2, peak), (x + w + 4, eave)])}" fill="{roof}"/>',
           f'<g stroke="#000" stroke-opacity="0.18" stroke-width="1.2">' + "".join(
               f'<line x1="{x + w / 2 + (i - 3) * w / 8:.1f}" y1="{peak + abs(i - 3) * (eave - peak) / 4 + 2:.1f}" x2="{x + w / 2 + (i - 3) * w / 7.2:.1f}" y2="{eave:.1f}"/>' for i in range(7)) + "</g>",
           f'<rect x="{x:.1f}" y="{eave:.1f}" width="{w:.1f}" height="{base - eave:.1f}" fill="{body}"/>']
    # clapboard lines
    out.append('<g stroke="#000" stroke-opacity="0.08" stroke-width="1">' + "".join(
        f'<line x1="{x:.1f}" y1="{yy:.1f}" x2="{x + w:.1f}" y2="{yy:.1f}"/>' for yy in [eave + 4 + i * 3.2 for i in range(int((base - eave - 4) / 3.2))]) + "</g>")
    # gable vent
    out.append(f'<path d="M {x + w / 2 - 7:.1f} {eave - 4:.1f} L {x + w / 2:.1f} {eave - 14:.1f} L {x + w / 2 + 7:.1f} {eave - 4:.1f} Z" fill="{trim}" opacity="0.8"/>')
    # two porch levels
    mid = base - (base - eave) * 0.5
    for yl, yt in ((mid, eave + 2), (base, mid + 2)):
        out.append(f'<rect x="{x - 3:.1f}" y="{yt:.1f}" width="{w + 6:.1f}" height="3" fill="{trim}"/>')
        n = 4
        for i in range(n + 1):
            px = x + i * w / n
            out.append(f'<rect x="{px - 1.4:.1f}" y="{yt:.1f}" width="2.8" height="{yl - yt:.1f}" fill="{trim}"/>')
        # windows / doors with shutters behind the porch
        for i in range(n):
            cx = x + (i + 0.5) * w / n
            ww, wh = w / n * 0.42, (yl - yt) * 0.62
            on = lit and rnd.random() < 0.5
            out.append(f'<rect x="{cx - ww / 2:.1f}" y="{yl - wh - 4:.1f}" width="{ww:.1f}" height="{wh:.1f}" fill="{"#FFD98E" if on else "#3A3446"}"/>')
            out.append(f'<rect x="{cx - ww / 2 - ww * 0.42:.1f}" y="{yl - wh - 4:.1f}" width="{ww * 0.38:.1f}" height="{wh:.1f}" fill="{shutter}"/>'
                       f'<rect x="{cx + ww / 2 + ww * 0.04:.1f}" y="{yl - wh - 4:.1f}" width="{ww * 0.38:.1f}" height="{wh:.1f}" fill="{shutter}"/>')
        # gingerbread balusters
        rail = yl - (yl - yt) * 0.3
        out.append(f'<rect x="{x - 3:.1f}" y="{rail:.1f}" width="{w + 6:.1f}" height="2.2" fill="{trim}"/>')
        out.append(f'<g fill="{trim}">' + "".join(f'<rect x="{x + j * 3.6:.1f}" y="{rail:.1f}" width="1.6" height="{yl - rail - 1:.1f}"/>' for j in range(int(w / 3.6) + 1)) + "</g>")
        # scalloped bracket trim under each porch roof
        out.append(f'<path d="' + "".join(f'M {x + j * 6:.1f} {yt + 3:.1f} q 3 4 6 0 ' for j in range(int(w / 6))) + f'" fill="none" stroke="{trim}" stroke-width="1.4"/>')
    if shade:
        out.append(f'<polygon points="{P([(x - 4, eave), (x + w / 2, peak), (x + w + 4, eave), (x + w + 4, base), (x - 4, base)])}" fill="#3A2048" opacity="{shade}"/>')
    if lit:
        out.append(f'<path d="M {x + w / 2:.1f} {peak:.1f} L {x + w + 4:.1f} {eave:.1f} M {x + w + 1:.1f} {eave:.1f} L {x + w + 1:.1f} {base:.1f}" stroke="{lit}" stroke-width="2.4" fill="none" opacity="0.9"/>')
    return "".join(out)


def rooster(x, y, s=1.0, flip=False, rim="#FFB060"):
    """Key West street rooster in profile (facing right unless flip), standing on (x, y)."""
    sc = -s if flip else s
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({sc:.2f} {s:.2f})">'
            '<path d="M -8 -24 Q -30 -40 -30 -58 Q -20 -50 -16 -40 Q -22 -56 -12 -66 Q -10 -50 -6 -40 Q -6 -56 4 -60 Q -2 -44 0 -30 Z" fill="#1E3A34"/>'
            '<path d="M -12 -66 Q -10 -50 -6 -40 Q -6 -56 4 -60" fill="none" stroke="#3E7A5A" stroke-width="1.6"/>'
            '<path d="M -10 -14 Q -14 -34 4 -38 Q 22 -40 24 -24 Q 24 -10 8 -8 Q -4 -6 -10 -14 Z" fill="#8A3A22"/>'
            '<path d="M -4 -20 Q 6 -14 18 -20 Q 10 -10 -2 -14 Z" fill="#5A2414"/>'
            '<path d="M 12 -36 Q 14 -50 20 -56 Q 28 -58 30 -52 Q 28 -44 24 -30 Q 18 -24 12 -36 Z" fill="#D8762E"/>'
            '<path d="M 14 -38 Q 18 -46 22 -48 M 16 -34 Q 22 -42 26 -42" stroke="#F2A040" stroke-width="1.4" fill="none"/>'
            '<path d="M 21 -58 q 1 -6 4 -3 q 2 -5 4 0 q 3 -3 3 3 Z" fill="#D8262A"/>'
            '<path d="M 30 -53 L 36 -51 L 30 -49 Z" fill="#E8B040"/><path d="M 28 -48 q 2 6 -1 7 q -2 -2 -1 -7 Z" fill="#D8262A"/>'
            '<circle cx="27" cy="-53" r="1.2" fill="#1A1A1A"/>'
            '<path d="M 4 -9 L 2 0 M 12 -9 L 14 0 M -1 0 L 6 0 M 11 0 L 18 0" stroke="#D89A3A" stroke-width="2" stroke-linecap="round"/>'
            f'<path d="M 24 -30 Q 28 -44 30 -52 M 24 -24 Q 24 -10 8 -8" stroke="{rim}" stroke-width="1.8" fill="none" stroke-linecap="round" opacity="0.9"/>'
            '</g>')


def schooner(x, y, s, hull="#2A1E30", sail="#F6D6B0", sail_sh="#D89A80", rim="#FFE2A0"):
    """Two-masted gaff schooner under sail, heading left; (x, y) waterline centre."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            '<path d="M -62 -10 L 58 -10 Q 52 4 40 6 L -48 6 Q -58 0 -62 -10 Z" fill="' + hull + '"/>'
            '<line x1="-62" y1="-10" x2="-92" y2="-16" stroke="' + hull + '" stroke-width="2.2"/>'
            '<line x1="-18" y1="-10" x2="-20" y2="-122" stroke="' + hull + '" stroke-width="2.6"/><line x1="22" y1="-10" x2="20" y2="-136" stroke="' + hull + '" stroke-width="2.8"/>'
            f'<path d="M -18 -16 L -19 -112 L 12 -100 L 16 -16 Z" fill="{sail}"/><path d="M -2 -16 L -3 -106 L 12 -100 L 16 -16 Z" fill="{sail_sh}" opacity="0.5"/>'
            f'<path d="M 22 -16 L 21 -126 L 56 -110 L 62 -16 Z" fill="{sail}"/><path d="M 40 -16 L 39 -118 L 56 -110 L 62 -16 Z" fill="{sail_sh}" opacity="0.5"/>'
            f'<path d="M -22 -16 L -21 -116 L -86 -16 Z" fill="{sail}"/><path d="M -24 -100 L -66 -18 L -86 -16 Z" fill="{sail_sh}" opacity="0.35"/>'
            '<g stroke="' + hull + '" stroke-width="1.4" opacity="0.6"><line x1="-19" y1="-112" x2="12" y2="-100"/><line x1="21" y1="-126" x2="56" y2="-110"/><line x1="-18" y1="-16" x2="16" y2="-16"/><line x1="22" y1="-16" x2="62" y2="-16"/></g>'
            f'<path d="M 12 -100 L 16 -16 M 56 -110 L 62 -16" stroke="{rim}" stroke-width="2" opacity="0.8"/>'
            '<path d="M 20 -136 L 30 -133 L 20 -130 Z" fill="#D8463A"/>'
            + "".join(f'<circle cx="{-40 + i * 12}" cy="-14" r="2.6" fill="{hull}"/>' for i in range(6))
            + "</g>")


def key_west():
    u = "keywest"
    H = 270
    out = [defs(
        lg(f"{u}-sky", [(0, "#2E2E6E"), (0.3, "#6A3E86"), (0.55, "#C8507E"), (0.75, "#F0784E"), (0.9, "#F9A848"), (1, "#FFD078")], 0, 40, 0, H, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#FFC070"), (0.08, "#E88A5A"), (0.35, "#8A4A7A"), (0.7, "#3E2E62"), (1, "#22204A")], 0, H, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-deck", [(0, "#7A4A3E"), (1, "#3A2230")]),
        lg(f"{u}-cl", [(0, "#FFB878"), (1, "#C85A7A")]),
    )]
    out.append(f'<rect width="600" height="{H + 1}" fill="url(#{u}-sky)"/>')
    sx, sy = 388, H - 14
    out.append(glow(sx, sy, 260, "#FFD27A", f"{u}-g1", 0.75))
    out.append(glow(sx, sy, 70, "#FFF0C0", f"{u}-g2", 0.9))
    out.append(f'<circle cx="{sx}" cy="{sy}" r="26" fill="#FFF2C6"/>')
    # sunset cloud streaks with glowing undersides
    for x, y, w, h_ in ((120, 104, 220, 9), (70, 120, 140, 6), (460, 92, 240, 10), (520, 110, 150, 6), (300, 150, 180, 7), (200, 178, 160, 5), (520, 196, 120, 5), (430, 224, 110, 4)):
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{w / 2}" ry="{h_}" fill="#9A4A82" opacity="0.6"/>')
        out.append(f'<ellipse cx="{x + 6}" cy="{y + h_ * 0.5:.1f}" rx="{w / 2 * 0.85:.1f}" ry="{h_ * 0.5:.1f}" fill="url(#{u}-cl)" opacity="0.85"/>')
    # sea and the sun's glittering road toward us
    out.append(f'<rect x="0" y="{H}" width="600" height="{444 - H}" fill="url(#{u}-sea)"/>')
    rnd = random.Random(4)
    gl = []
    for i in range(170):
        y = H + 2 + (444 - H) * (rnd.random() ** 1.5)
        t = (y - H) / (444 - H)
        x = sx + rnd.gauss(0, 10 + 70 * t)
        w = rnd.uniform(6, 26) * (0.4 + t)
        gl.append(f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{1 + 2.2 * t:.1f}" rx="1" fill="{rnd.choice(["#FFE6A8", "#FFD078", "#FFF4D0"])}" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    out.append("".join(gl))
    out.append(ripples(70, 5, (0, H + 6, 600, 444), ["#C86A8A", "#7A4A86", "#E89A7A"], w=(10, 40), h=1.6, opacity=(0.3, 0.7)))
    # far keys on the horizon
    out.append(f'<path d="M 470 {H} q 20 -6 50 -5 q 30 -2 50 3 l 40 2 Z" fill="#5A3A6A" opacity="0.7"/>')
    out.append(f'<path d="M -10 {H} q 30 -5 70 -4 q 20 0 40 4 Z" fill="#5A3A6A" opacity="0.7"/>')
    # schooner crossing the sun, a little sloop farther out
    out.append(schooner(300, H + 14, 0.86))
    out.append(f'<path d="M 230 {H + 16} q 70 6 140 0" stroke="#FFE6A8" stroke-width="1.6" fill="none" opacity="0.6"/>')
    out.append(f'<g transform="translate(486 {H + 4})"><path d="M -14 -2 L 14 -2 L 10 3 L -10 3 Z" fill="#2A1E30"/><path d="M 0 -3 L 0 -40 L 14 -4 Z" fill="#F6D6B0"/><path d="M -2 -4 L -2 -34 L -14 -4 Z" fill="#E8B8A0"/></g>')
    out.append(f'<g transform="translate(560 {H + 2}) scale(0.6)"><path d="M -14 -2 L 14 -2 L 10 3 L -10 3 Z" fill="#3A2A44"/><path d="M 0 -3 L 0 -40 L 14 -4 Z" fill="#E8B8A0"/><path d="M -2 -4 L -2 -34 L -14 -4 Z" fill="#D8A098"/></g>')
    # waterfront on the left: conch houses with palms, backlit by the sunset
    out.append(f'<path d="M -10 {H + 30} L 250 {H + 30} L 262 {H + 40} L -10 {H + 40} Z" fill="#3A2440"/>')
    out.append(palm_tree(36, H + 32, 150, trunk="#2E1E34", frond="#2A2A3A", rim="#FFB070", seed=3, lean=0.1))
    out.append(conch_house(-6, H + 32, 92, 120, "#9AD0C0", shutter="#4E7AA0", roof="#C8C0C8", shade=0.42, lit="#FFC890", seed=2))
    out.append(conch_house(102, H + 32, 84, 106, "#F4B8C0", shutter="#4E8A7A", roof="#C8C0C8", shade=0.36, lit="#FFD8A0", seed=5))
    out.append(conch_house(194, H + 32, 64, 82, "#F6E2A0", shutter="#6A9AC0", roof="#B8B0BC", shade=0.32, lit="#FFE0A8", seed=8))
    out.append(palm_tree(186, H + 34, 136, trunk="#2E1E34", frond="#2A2A3A", rim="#FFB070", seed=7, lean=0.12))
    out.append(palm_tree(262, H + 36, 92, trunk="#3A2840", frond="#33304A", rim="#FFB070", seed=11, lean=0.14))
    rb_ = random.Random(31)
    out.append('<g>' + "".join(f'<circle cx="{rb_.uniform(-10, 262):.1f}" cy="{H + 30 - rb_.uniform(0, 6):.1f}" r="{rb_.uniform(3.5, 7):.1f}" fill="{rb_.choice(["#2E2A40", "#3A2E48", "#283044", "#34304A"])}"/>' for _ in range(60)) + "</g>")
    out.append('<g>' + "".join(f'<circle cx="{rb_.uniform(-10, 262):.1f}" cy="{H + 26 - rb_.uniform(0, 6):.1f}" r="{rb_.uniform(2, 4):.1f}" fill="#E8906A" opacity="0.55"/>' for _ in range(16)) + "</g>")
    # harbor seawall and its reflection
    out.append(f'<path d="M -10 {H + 38} L 262 {H + 38} Q 272 {H + 41} 276 {H + 46} L -10 {H + 46} Z" fill="#2A1A30"/>')
    out.append(f'<path d="M 262 {H + 38} Q 272 {H + 41} 276 {H + 46}" stroke="#FFB070" stroke-width="1.6" fill="none" opacity="0.8"/>')
    # a little dock off the end of the waterfront with a moored skiff
    out.append(f'<rect x="250" y="{H + 34}" width="56" height="4" fill="#4A2E3A"/>' + "".join(f'<rect x="{x}" y="{H + 30}" width="3" height="18" fill="#3A2232"/>' for x in (254, 276, 300)))
    out.append(f'<path d="M 270 {H + 44} L 306 {H + 44} L 302 {H + 50} L 274 {H + 50} Z" fill="#E8E0D8"/><path d="M 270 {H + 44} L 306 {H + 44} L 305 {H + 46} L 271 {H + 46} Z" fill="#3E8AA0"/>'
               f'<path d="M 272 {H + 44} L 304 {H + 44}" stroke="#FFC890" stroke-width="1.2"/>')
    out.append(f'<g opacity="0.25">' + "".join(f'<rect x="{x}" y="{H + 46 + i * 5}" width="{rnd.uniform(20, 60):.0f}" height="2" fill="{c}"/>'
                                            for i in range(6) for x, c in ((10 + i * 7, "#9AD0C0"), (110 - i * 5, "#F4B8C0"), (200 + i * 3, "#F6E2A0"))) + "</g>")
    # the pier: planked deck in perspective, pilings, rope rail
    vx = sx
    deck = [(-10, 388), (610, 372), (610, 444), (-10, 444)]
    out.append(f'<polygon points="{P(deck)}" fill="url(#{u}-deck)"/>')
    out.append('<g stroke="#2A1626" stroke-width="1.4" opacity="0.6">' + "".join(
        f'<line x1="{x0:.1f}" y1="{388 - (x0 + 10) * 16 / 620:.1f}" x2="{x0 + (x0 - vx) * 0.9:.1f}" y2="444"/>' for x0 in range(-40, 640, 28)) + "</g>")
    out.append('<path d="M -10 388 L 610 372" stroke="#FFB878" stroke-width="2.4" opacity="0.8"/>')
    for x in (30, 150, 270, 390, 510):
        yb = 388 - (x + 10) * 16 / 620
        out.append(f'<rect x="{x - 5}" y="{yb - 34:.1f}" width="10" height="36" fill="#3A2230"/><rect x="{x + 2}" y="{yb - 34:.1f}" width="3" height="36" fill="#FFB070" opacity="0.6"/>'
                   f'<ellipse cx="{x}" cy="{yb - 34:.1f}" rx="5" ry="2" fill="#5A3A40"/>')
    out.append('<path d="M 30 ' + f'{388 - 40 * 16 / 620 - 26:.1f}' + ' Q 90 ' + f'{388 - 90 * 16 / 620 - 14:.1f}' + ' 150 ' + f'{388 - 160 * 16 / 620 - 26:.1f}'
               + ' Q 210 ' + f'{388 - 220 * 16 / 620 - 14:.1f}' + ' 270 ' + f'{388 - 280 * 16 / 620 - 26:.1f}'
               + ' Q 330 ' + f'{388 - 340 * 16 / 620 - 14:.1f}' + ' 390 ' + f'{388 - 400 * 16 / 620 - 26:.1f}'
               + ' Q 450 ' + f'{388 - 460 * 16 / 620 - 14:.1f}' + ' 510 ' + f'{388 - 520 * 16 / 620 - 26:.1f}" fill="none" stroke="#C88A5A" stroke-width="2.6"/>')
    # sunset watchers on the pier, rim-lit
    kw = dict(rim="#FFB878", tint=("#2A1A34", 0.42))
    yb = 392 - 232 * 16 / 620
    out.append(F.couple(222, yb, 43, palette={"top": "#2E2A4A", "season": "summer"}, seed=611, light=1, gap=38, **kw))
    for x, h, c, pose, sd in ((330, 46, "#2A3A4A", "stand_back", 612), (346, 38, "#7A3A4A", "stand_back", 613), (446, 42, "#3A2A3E", "photo", 614)):
        out.append(person(x, 392 - (x + 10) * 16 / 620, h, c, pose=pose, facing=-1, light=1 if x < 388 else -1, seed=sd, pal={"season": "summer", "form": "f" if x == 346 else None}, **kw))
    out.append(person(358, 392 - 368 * 16 / 620, 24, "#E86A5A", pose="child_back", light=-1, seed=615, **dict(kw, rim="#FFD8A0")))
    # a couple strolling across the boards to join the crowd, painted large in the foreground
    out.append('<ellipse cx="138" cy="433" rx="40" ry="4" fill="#1E0E1A" opacity="0.3"/>')
    out.append(F.couple(138, 432, 80, "back", {"season": "summer"}, seed=618, rim="#FFB878", light=1, tint=("#2A1A34", 0.3), gap=32))
    # a Key West rooster on the nearest piling
    yb = 388 - 520 * 16 / 620
    out.append(rooster(510, yb - 34, 0.85, flip=True))
    out.append(gulls([(150, 150, 7), (172, 162, 5), (520, 160, 6)], "#2A1E3A", 1.8))
    return "\n".join(out)


# ---------------------------------------------------------------- Cape Canaveral (dawn launch over the lagoon)
def cabbage_palm(x, base, h, color="#1A1C30", rim=None, seed=1, lean=0.0):
    """Sabal (cabbage) palm silhouette: slim trunk with leaf-boot texture under a dense round crown of
    fan leaves, each fan a spray of stiff pointed segments."""
    rnd = random.Random(seed)
    tx, ty = x + lean * h, base - h
    w0, w1 = h * 0.035, h * 0.028
    out = [f'<path d="M {x - w0:.1f} {base:.1f} Q {x + lean * h * 0.5 - w1:.1f} {base - h * 0.5:.1f} {tx - w1:.1f} {ty + h * 0.06:.1f} L {tx + w1:.1f} {ty + h * 0.06:.1f} Q {x + lean * h * 0.5 + w1:.1f} {base - h * 0.5:.1f} {x + w0:.1f} {base:.1f} Z" fill="{color}"/>']
    # rough bark: short darker ticks along the trunk
    out.append(f'<g stroke="#000" stroke-opacity="0.25" stroke-width="1">' + "".join(
        f'<line x1="{x + lean * h * t - w0 * 0.8:.1f}" y1="{base - h * t:.1f}" x2="{x + lean * h * t + w0 * 0.8:.1f}" y2="{base - h * t + 1.5:.1f}"/>'
        for t in [0.1 + 0.06 * i for i in range(14)]) + "</g>")
    segs = []
    rims = []
    for i in range(15):
        a = math.radians(-200 + i * 220 / 14 + rnd.uniform(-7, 7))
        L = h * rnd.uniform(0.13, 0.19)
        droop = h * 0.06 * max(0, math.cos(a) ** 2) if math.sin(a) > -0.6 else 0
        fx, fy = tx + L * math.cos(a), ty + L * math.sin(a) * 0.75 + droop
        segs.append(f'<path d="M {tx:.1f} {ty:.1f} L {fx:.1f} {fy:.1f}" stroke="{color}" stroke-width="{max(1, h * 0.012):.1f}" fill="none"/>')
        # the fan: stiff segments radiating from the end of the stalk
        fan_a = a + rnd.uniform(-0.2, 0.2)
        n = 9
        spread = 1.5
        R = h * rnd.uniform(0.11, 0.15)
        pts = [(fx, fy)]
        for j in range(n):
            aa = fan_a - spread / 2 + spread * j / (n - 1)
            rr = R * (0.75 + 0.25 * math.sin(math.pi * j / (n - 1)))
            pts.append((fx + rr * math.cos(aa), fy + rr * math.sin(aa) * 0.85 + R * 0.25 * abs(math.cos(aa))))
            aa2 = fan_a - spread / 2 + spread * (j + 0.5) / (n - 1)
            if j < n - 1:
                pts.append((fx + rr * 0.55 * math.cos(aa2), fy + rr * 0.55 * math.sin(aa2) * 0.85))
        segs.append(f'<polygon points="{P(pts)}" fill="{color}"/>')
        if rim and math.cos(fan_a) > 0.2:
            rims.append(f'<polyline points="{P(pts[1:5])}" fill="none" stroke="{rim}" stroke-width="{max(0.8, h * 0.007):.1f}" opacity="0.6"/>')
    out.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="{h * 0.07:.1f}" fill="{color}"/>')
    out += segs + rims
    return "".join(out)


def billow(cx, base, w, h, seed, grad, hi="#FFFFFF", hi_op=0.6, shade="#7A6A9A", n=60, lit_dx=0.3):
    """Low, wide billowing cloud mass (launch ground cloud, surf spray): soft dome of overlapping puffs with
    shaded undersides and lit caps."""
    rnd = random.Random(seed)
    body, sh, li = [], [], []
    for _ in range(n):
        t = rnd.uniform(-1, 1)
        dome = (1 - t * t) ** 0.7
        r = h * (0.18 + 0.32 * dome) * rnd.uniform(0.7, 1.15)
        x = cx + t * w / 2
        y = base - r * 0.6 - rnd.uniform(0, 1) * h * 0.55 * dome
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>')
        sh.append(f'<circle cx="{x - r * 0.2:.1f}" cy="{y + r * 0.35:.1f}" r="{r * 0.62:.1f}"/>')
        li.append(f'<circle cx="{x + r * lit_dx:.1f}" cy="{y - r * 0.32:.1f}" r="{r * 0.55:.1f}"/>')
    return (f'<g fill="url(#{grad})">' + "".join(body) + "</g>"
            + f'<g fill="{shade}" opacity="0.22">' + "".join(sh) + "</g>"
            + f'<g fill="{hi}" opacity="{hi_op}">' + "".join(li) + "</g>")


def egret(x, y, s=1.0, rim="#FFD8B0"):
    """Great egret wading, facing left: white body, S-neck, yellow bill, long black legs."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.2f})">'
            '<path d="M -2 -30 L -6 0 M 4 -30 L 6 0" stroke="#1A1A22" stroke-width="1.8" stroke-linecap="round"/>'
            '<path d="M -14 -40 Q -10 -54 8 -52 Q 24 -48 26 -38 Q 18 -30 4 -30 Q -10 -30 -14 -40 Z" fill="#F6F2EC"/>'
            '<path d="M 26 -38 Q 34 -34 36 -30 Q 28 -32 20 -34 Z" fill="#E8E2DA"/>'
            '<path d="M -10 -46 Q -20 -56 -14 -66 Q -8 -74 -14 -82" stroke="#F6F2EC" stroke-width="4.6" fill="none" stroke-linecap="round"/>'
            '<circle cx="-15" cy="-83" r="3.6" fill="#F6F2EC"/><path d="M -18 -84 L -32 -81 L -18 -81.5 Z" fill="#F2C040"/>'
            f'<path d="M 8 -52 Q 24 -48 26 -38 M -12 -66 Q -8 -74 -13 -82" stroke="{rim}" stroke-width="1.6" fill="none" opacity="0.9"/>'
            '<path d="M -6 -34 Q 4 -38 18 -36" stroke="#C8C0C8" stroke-width="1.2" fill="none"/>'
            '</g>')


def canaveral():
    u = "canaveral"
    H = 300
    out = [defs(
        lg(f"{u}-sky", [(0, "#1A2452"), (0.35, "#3A4A86"), (0.6, "#9A7AA8"), (0.82, "#F0A49A"), (0.95, "#FFCE9A"), (1, "#FFE0B0")], 0, 40, 0, H, units="userSpaceOnUse"),
        lg(f"{u}-lag", [(0, "#F8C8A0"), (0.15, "#C89AA8"), (0.5, "#5A5E8E"), (1, "#202A50")], 0, H, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-plume", [(0, "#8A7AA0"), (0.5, "#E8B8B0"), (1, "#FFE8C8")], 120, 0, 420, 0, units="userSpaceOnUse"),
        lg(f"{u}-trail", [(0, "#C8A0B0"), (0.5, "#FFE0B8"), (1, "#FFF4E0")], 200, 0, 280, 0, units="userSpaceOnUse"),
        lg(f"{u}-body", [(0, "#BFC4D4"), (0.35, "#FFFFFF"), (0.7, "#F2EEEA"), (1, "#9A9AB0")], 0, 0, 1, 0),
        lg(f"{u}-shore", [(0, "#2A2A48"), (1, "#14182E")]),
    )]
    out.append(f'<rect width="600" height="{H + 1}" fill="url(#{u}-sky)"/>')
    out.append(dots(40, 3, (0, 40, 600, 130), "#F4EEF8", r=(0.5, 1.3), opacity=(0.3, 0.9)))
    out.append(glow(470, H, 240, "#FFD6A0", f"{u}-dawn", 0.7))
    # thin dawn clouds catching first light from below
    for x, y, w in ((470, 150, 160), (530, 170, 110), (90, 176, 150), (400, 196, 120), (150, 214, 100)):
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{w / 2}" ry="5" fill="#6A5A8A" opacity="0.55"/><ellipse cx="{x + 8}" cy="{y + 3}" rx="{w * 0.4:.0f}" ry="2.5" fill="#FFB89A" opacity="0.8"/>')
    # distant barrier island with the launch complex
    out.append(f'<path d="M -10 {H} L -10 {H - 8} Q 120 {H - 12} 260 {H - 9} Q 420 {H - 6} 610 {H - 10} L 610 {H} Z" fill="#4A4A72"/>')
    rnd = random.Random(8)
    out.append(tree_line([(-10, H - 8), (610, H - 9)], 3, ["#454570", "#4E4E78"], density=0.6, hmin=4, hmax=8))
    # other pads / towers far down the cape
    for x, h in ((470, 22), (520, 14), (90, 16)):
        out.append(f'<rect x="{x}" y="{H - 8 - h}" width="3" height="{h}" fill="#55557E"/>')
    # rocket position
    rx, ry_top, ry_bot = 238, 104, 200   # body
    pad_x, pad_y = 238, H - 8
    # the launch tower (lattice) beside the pad, with lightning mast
    tx = pad_x + 20
    out.append(f'<rect x="{tx}" y="{pad_y - 74}" width="12" height="74" fill="#3A3A5E"/>')
    out.append('<g stroke="#6A6A92" stroke-width="1">' + "".join(f'<line x1="{tx}" y1="{pad_y - 74 + i * 6}" x2="{tx + 12}" y2="{pad_y - 68 + i * 6}"/>' for i in range(12)) + "</g>")
    out.append(f'<line x1="{tx + 6}" y1="{pad_y - 74}" x2="{tx + 6}" y2="{pad_y - 98}" stroke="#3A3A5E" stroke-width="2"/>')
    out.append(f'<rect x="{tx - 8}" y="{pad_y - 60}" width="9" height="3" fill="#3A3A5E"/><rect x="{tx - 8}" y="{pad_y - 40}" width="9" height="3" fill="#3A3A5E"/>')
    for x in (pad_x - 46, pad_x + 54):
        out.append(f'<line x1="{x}" y1="{pad_y}" x2="{x}" y2="{pad_y - 60}" stroke="#4A4A70" stroke-width="1.6"/>')
    # exhaust: column from pad to engine, lit warm by the flame below and the coming sun
    # ground cloud billowing out of the flame trench, lit gold from within and pink from the dawn
    out.append(billow(pad_x + 10, pad_y + 2, 230, 46, 3, f"{u}-plume", hi="#FFE8D0", hi_op=0.55))
    # the exhaust column: puffs swelling as they fall behind the climbing rocket
    rc = random.Random(5)
    col = []
    for i in range(46):
        t = i / 45
        y = ry_bot + 30 + (pad_y - 30 - ry_bot - 30) * t
        r = 5 + 16 * t ** 1.3
        x = rx + rc.uniform(-3, 3) * (0.5 + t) - 6 * t
        col.append((x, y, r))
    out.append(f'<g fill="url(#{u}-trail)">' + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>' for x, y, r in col) + "</g>")
    out.append('<g fill="#9A84A8" opacity="0.25">' + "".join(f'<circle cx="{x - r * 0.35:.1f}" cy="{y + r * 0.1:.1f}" r="{r * 0.6:.1f}"/>' for x, y, r in col) + "</g>")
    out.append('<g fill="#FFF6E0" opacity="0.6">' + "".join(f'<circle cx="{x + r * 0.3:.1f}" cy="{y - r * 0.1:.1f}" r="{r * 0.5:.1f}"/>' for x, y, r in col) + "</g>")
    out.append(glow(pad_x, pad_y - 16, 80, "#FFB060", f"{u}-pg", 0.7))
    # the flame and the rocket
    out.append(glow(rx, ry_bot + 22, 60, "#FFC060", f"{u}-fg", 0.9))
    out.append(f'<path d="M {rx - 9} {ry_bot + 2} Q {rx - 12} {ry_bot + 26} {rx} {ry_bot + 70} Q {rx + 12} {ry_bot + 26} {rx + 9} {ry_bot + 2} Z" fill="#FF9A3A"/>')
    out.append(f'<path d="M {rx - 5} {ry_bot + 2} Q {rx - 6} {ry_bot + 20} {rx} {ry_bot + 48} Q {rx + 8} {ry_bot + 20} {rx + 5} {ry_bot + 2} Z" fill="#FFE07A"/>')
    out.append(f'<path d="M {rx - 3} {ry_bot + 2} Q {rx - 3} {ry_bot + 12} {rx} {ry_bot + 22} Q {rx + 3} {ry_bot + 12} {rx + 3} {ry_bot + 2} Z" fill="#FFFFFF"/>')
    body = f'M {rx - 9} {ry_bot} L {rx - 9} {ry_top + 18} Q {rx - 9} {ry_top + 4} {rx} {ry_top - 6} Q {rx + 9} {ry_top + 4} {rx + 9} {ry_top + 18} L {rx + 9} {ry_bot} Z'
    out.append(f'<path d="{body}" fill="url(#{u}-body)"/>')
    out.append(f'<rect x="{rx - 9}" y="{ry_top + 30}" width="18" height="5" fill="#2A2A3E"/><rect x="{rx - 9}" y="{ry_bot - 12}" width="18" height="3" fill="#2A2A3E" opacity="0.7"/>')
    out.append(f'<path d="M {rx - 9} {ry_bot - 6} L {rx - 16} {ry_bot + 2} L {rx - 9} {ry_bot + 1} Z M {rx + 9} {ry_bot - 6} L {rx + 16} {ry_bot + 2} L {rx + 9} {ry_bot + 1} Z" fill="#3A3A50"/>')
    out.append(f'<line x1="{rx + 8}" y1="{ry_top + 10}" x2="{rx + 8}" y2="{ry_bot}" stroke="#FFC890" stroke-width="1.6" opacity="0.8"/>')
    # shore of the lagoon (distant) and the glassy lagoon
    out.append(f'<rect x="0" y="{H}" width="600" height="{444 - H}" fill="url(#{u}-lag)"/>')
    # reflection of the flame and trail, broken by ripples
    rr = random.Random(12)
    refl = []
    for i in range(60):
        y = H + 3 + i * 2.2
        if y > 444:
            break
        t = (y - H) / 144
        w = rr.uniform(4, 16) * (0.6 + t)
        refl.append(f'<rect x="{rx + rr.gauss(0, 3 + 6 * t) - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{1.2 + 1.2 * t:.1f}" rx="1" fill="{rr.choice(["#FFE8A0", "#FFC070", "#FFFFFF"])}" opacity="{max(0.15, 0.95 - t * 0.9):.2f}"/>')
    out.append("".join(refl))
    out.append(ripples(80, 13, (0, H + 4, 600, 444), ["#F8D0B0", "#B88AA8", "#7A7AAE"], w=(10, 40), h=1.5, opacity=(0.25, 0.6)))
    # the ground cloud mirrored in the still lagoon
    out.append(mist(pad_x + 10, H + 22, 130, 20, "#F8C8A8", f"{u}-cr", 0.55))
    out.append(mist(pad_x, H + 10, 60, 10, "#FFE0A0", f"{u}-cr2", 0.7))
    # brown pelicans gliding low in a line across the water
    for k, (px_, py_) in enumerate(((330, 344), (356, 338), (382, 333), (408, 329))):
        out.append(f'<g transform="translate({px_} {py_}) scale(0.9)"><path d="M -16 0 Q -8 -5 0 -1 Q 8 -5 16 0 Q 8 -2 0 2 Q -8 -2 -16 0 Z" fill="#2A2640"/>'
                   f'<path d="M -2 0 L -10 1 L -2 2 Z" fill="#2A2640"/></g>')
    # near shore: mangroves and cabbage palms on the right, spectators on the left
    shore = rough([(-10, 390), (120, 386), (200, 396), (300, 404), (420, 398), (500, 392), (610, 388)], 6, amp=4, depth=3)
    out.append(f'<polygon points="{P(shore + [(610, 444), (-10, 444)])}" fill="url(#{u}-shore)"/>')
    rm = random.Random(14)
    for k in range(40):
        x = rm.uniform(420, 610)
        y = (y_on(shore, x) or 400) + rm.uniform(-4, 4)
        out.append(f'<circle cx="{x:.1f}" cy="{y - rm.uniform(4, 22):.1f}" r="{rm.uniform(8, 16):.1f}" fill="{rm.choice(["#1A1C30", "#20223A", "#16182A"])}"/>')
    out.append('<g stroke="#16182A" stroke-width="1.6" fill="none">' + "".join(
        f'<path d="M {x} {y_on(shore, x) or 400:.1f} q {rm.uniform(-6, 6):.1f} 10 {rm.uniform(-10, 10):.1f} 16"/>' for x in range(430, 610, 9)) + "</g>")
    for x, h, sd, ln in ((470, 150, 1, 0.04), (512, 186, 2, -0.03), (556, 132, 3, 0.05), (440, 100, 4, 0.02)):
        out.append(cabbage_palm(x, (y_on(shore, x) or 400) - 6, h, rim="#F0A890", seed=sd, lean=ln))
    for x in range(-10, 400, 40):
        out.append(grass(14, x, (x, (y_on(shore, x) or 404) - 4, x + 40, (y_on(shore, x) or 404) + 8), ["#2A2C48", "#3A3A5A", "#5A4A6A"], h=(6, 14)))
    # launch watchers: a family, the kid up on dad's shoulders, someone pointing at the rocket
    for x, h, c in ((262, 34, "#3A3A5E"), (284, 30, "#5A3A5A"), (330, 32, "#2E3A52")):
        out.append(person(x, (y_on(shore, x) or 404) + 2, h, c, rim="#FFB890", pose="stand_back", light=1 if x < 300 else -1, tint=("#1E1E36", 0.32)))
    gy_ = lambda x: (y_on(shore, x) or 400) + 10
    tn = ("#1E1E36", 0.3)
    out.append(F.parent_child(96, gy_(96), 62, 1, {"top": "#3A3E62", "form": "m"}, seed=621, rim="#FFB890", light=1, tint=tn, view="back"))
    out.append(person(124, gy_(124), 56, "#5A3A5A", rim="#FFB890", pose="point", facing=1, light=1, seed=622, tint=tn, pal={"form": "f"}))
    out.append(person(170, gy_(170) - 2, 58, "#2E3A52", rim="#FFB890", hat="#1A1A2A", pose="stand_back", light=1, seed=623, tint=tn, pal={"form": "m"}))
    out.append(person(190, gy_(190) - 2, 38, "#7A4A5A", rim="#FFB890", pose="child_back", light=1, seed=624, tint=tn))
    out.append(egret(398, 422, 0.66))
    out.append(gulls([(420, 210, 7), (440, 220, 6), (462, 214, 6), (484, 226, 5)], "#2A2848", 2))
    return "\n".join(out)


# ---------------------------------------------------------------- Maine coast (morning, surf on granite ledges)
def ledge(uid, pts, top_col, face_col, seed, cracks=10, weed=None, weed_y=None, lit_edge="#FFF0DC", streak_cols=("#5A4A50", "#E8D2C4", "#8A7478")):
    """Granite slab: face colour, lit top facet along the upper edge, streaks + joint cracks clipped inside,
    optional band of golden rockweed at the waterline."""
    rnd = random.Random(seed)
    xs = [p_[0] for p_ in pts]
    ys = [p_[1] for p_ in pts]
    box = (min(xs), min(ys), max(xs), max(ys))
    out = [f'<clipPath id="{uid}"><polygon points="{P(pts)}"/></clipPath>', f'<polygon points="{P(pts)}" fill="{face_col}"/>']
    g = [streaks(int((box[2] - box[0]) * (box[3] - box[1]) / 300), seed, box, list(streak_cols), w=(1.5, 4), length=(8, 40), opacity=(0.2, 0.5), slant=0.4)]
    # lit top facet: offset copy of the upper outline
    upper = [p_ for p_ in pts if p_[1] < box[3] - 2]
    if len(upper) >= 2:
        band = upper + [(x_, y_ + rnd.uniform(8, 16)) for x_, y_ in upper[::-1]]
        g.append(f'<polygon points="{P(band)}" fill="{top_col}"/>')
    for _ in range(cracks):
        x0 = rnd.uniform(box[0], box[2])
        y0 = rnd.uniform(box[1], box[3])
        L = rnd.uniform(14, 40)
        g.append(f'<path d="M {x0:.1f} {y0:.1f} l {rnd.uniform(-6, 6):.1f} {L * 0.5:.1f} l {rnd.uniform(-8, 8):.1f} {L * 0.5:.1f}" stroke="#3A2E36" stroke-width="{rnd.uniform(1.2, 2.2):.1f}" fill="none" opacity="0.6"/>')
    g.append(dots(int((box[2] - box[0]) * 0.6), seed + 1, box, "#FFFFFF", r=(0.5, 1.3), opacity=(0.15, 0.5)))
    g.append(dots(int((box[2] - box[0]) * 0.6), seed + 2, box, "#2A2026", r=(0.5, 1.3), opacity=(0.15, 0.5)))
    if weed and weed_y:
        g.append(f'<rect x="{box[0] - 5:.1f}" y="{weed_y:.1f}" width="{box[2] - box[0] + 10:.1f}" height="{box[3] - weed_y + 5:.1f}" fill="{weed}"/>')
        g.append(blobs(40, seed + 3, (box[0], weed_y - 4, box[2], weed_y + 10), [weed, "#6A5418", "#B8962E"], r=(3, 8), opacity=(0.6, 1), squash=0.6))
    out.append(f'<g clip-path="url(#{uid})">' + "".join(g) + "</g>")
    if upper:
        out.append(f'<polyline points="{P(upper)}" fill="none" stroke="{lit_edge}" stroke-width="2" stroke-linejoin="round" opacity="0.8"/>')
    return "".join(out)


def lobster_boat(x, y, s=1.0, hull="#F4F2EC", trim="#2E4A6A", cabin="#F4F2EC", flip=False):
    """Downeast lobster boat: high flared bow, low working stern, cabin forward, mast and hauler."""
    sc = -s if flip else s
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({sc:.2f} {s:.2f})">'
            '<path d="M -40 -8 L 30 -10 Q 42 -14 48 -18 L 46 -6 Q 40 6 30 8 L -38 8 Q -42 2 -40 -8 Z" fill="' + hull + '"/>'
            '<path d="M -38 4 L 34 4 Q 40 2 44 -2 L 42 2 Q 36 8 30 8 L -38 8 Z" fill="#B8423A"/>'
            '<path d="M -40 -8 L 30 -10 Q 42 -14 48 -18" stroke="' + trim + '" stroke-width="2" fill="none"/>'
            '<path d="M 2 -10 L 4 -26 L 26 -26 L 30 -12 Z" fill="' + cabin + '"/><path d="M 6 -24 L 7 -17 L 25 -17 L 26 -24 Z" fill="#3A4E66"/>'
            '<path d="M 2 -27 L 28 -27" stroke="' + trim + '" stroke-width="2.4"/>'
            '<line x1="14" y1="-27" x2="14" y2="-44" stroke="#3A3A44" stroke-width="1.6"/><line x1="10" y1="-38" x2="18" y2="-38" stroke="#3A3A44" stroke-width="1.4"/>'
            '<rect x="-30" y="-16" width="8" height="6" fill="#E8C04A"/><rect x="-20" y="-15" width="8" height="5" fill="#C84A3A"/>'
            '' + F.person(-4, -9, 13, "stand_side", 1, {"top": "#E89A3A", "top_kind": "jacket", "bottom": "#E89A3A", "bottom_kind": "trousers", "hat_kind": "beanie", "hat": "#2A2A30", "form": "m"}, seed=641, shadow=0)
            + '</g>')


def buoy(x, y, s, a="#E8463A", b="#F4E04A", c="#F4F2EC"):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.2f}) rotate(12)">'
            f'<rect x="-4" y="-14" width="8" height="14" rx="3.5" fill="{a}"/><rect x="-4" y="-9" width="8" height="4" fill="{b}"/><rect x="-4" y="-14" width="8" height="3" fill="{c}"/>'
            '<line x1="0" y1="-14" x2="0" y2="-20" stroke="#4A3A2A" stroke-width="1.5"/><rect x="-2" y="-14" width="2" height="14" fill="#FFFFFF" opacity="0.35"/>'
            '</g>' + f'<ellipse cx="{x:.1f}" cy="{y + 1:.1f}" rx="{7 * s:.1f}" ry="{1.6 * s:.1f}" fill="#FFFFFF" opacity="0.5"/>')


def maine():
    u = "mainecoast"
    H = 232
    out = [defs(
        lg(f"{u}-sky", [(0, "#5E92C6"), (0.5, "#94BCDE"), (0.85, "#D2E2EA"), (1, "#E8EEEC")], 0, 40, 0, H, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#8AA8BE"), (0.08, "#4E7A9E"), (0.45, "#2A5478"), (1, "#173650")], 0, H, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-cliff", [(0, "#E8C6B4"), (0.5, "#B8968E"), (1, "#7A6270")], 0, 0, 1, 0),
        lg(f"{u}-spray", [(0, "#C8D6E4"), (0.6, "#F4F8FA"), (1, "#FFFFFF")], 220, 0, 360, 0, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#E8EEEC", 0), (1, "#E8EEEC", 0.9)]),
    )]
    out.append(f'<rect width="600" height="{H + 1}" fill="url(#{u}-sky)"/>')
    # morning sun high on the left, out of frame; soft glow and wisps
    out.append(glow(40, 60, 260, "#FFF6E0", f"{u}-sun", 0.75))
    out.append('<g fill="#FFFFFF" opacity="0.55">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{h_}"/>' for x, y, w, h_ in
                                                           ((200, 98, 90, 5), (250, 108, 60, 3.5), (470, 82, 110, 6), (520, 94, 70, 4), (360, 140, 80, 4))) + "</g>")
    out.append(cloud_puffs(140, H - 6, 160, 22, 5, "#E4ECF0", "#FFFFFF", shade="#B8C8D6", n=18, lit_dx=-0.25))
    out.append(f'<rect x="0" y="{H - 30}" width="600" height="32" fill="url(#{u}-haze)"/>')
    # the sea with rows of swell, glare under the sun
    out.append(f'<rect x="0" y="{H}" width="600" height="{444 - H}" fill="url(#{u}-sea)"/>')
    out.append(ripples(110, 7, (0, H + 2, 340, H + 60), ["#FFFFFF", "#E8F2F8"], w=(6, 26), h=1.4, opacity=(0.4, 0.9)))
    out.append(ripples(80, 8, (0, H + 20, 600, 400), ["#7AA2C2", "#A8C4DA", "#1E3E5A"], w=(10, 40), h=1.8, opacity=(0.3, 0.7)))
    rnd = random.Random(9)
    for y in (H + 26, H + 48, H + 76, H + 108):
        k = (y - H) / 140
        pts = [(x, y + 3 * math.sin(x / 40 + y)) for x in range(-10, 620, 20)]
        out.append(f'<polyline points="{P(pts)}" fill="none" stroke="#1A3A56" stroke-width="{2 + 3 * k:.1f}" opacity="0.35"/>')
        for _ in range(int(6 + 8 * k)):
            cx = rnd.uniform(0, 600)
            w = rnd.uniform(14, 40) * (0.6 + k)
            out.append(f'<path d="M {cx - w / 2:.1f} {y:.1f} q {w / 2:.1f} {-4 - 4 * k:.1f} {w:.1f} 0 Z" fill="#F4F8FA" opacity="{rnd.uniform(0.6, 0.95):.2f}"/>')
    # lobster boat working its traps offshore, a few buoys
    out.append(lobster_boat(140, H + 30, 0.9))
    out.append(f'<path d="M 100 {H + 38} q 40 4 84 0" stroke="#FFFFFF" stroke-width="1.6" fill="none" opacity="0.6"/>')
    for bx, by_, sc in ((206, H + 40, 0.6), (232, H + 52, 0.7), (60, H + 70, 0.8)):
        out.append(buoy(bx, by_, sc))
    # the headland: pink granite cliff lit from the left, grass on top, spruce forest behind
    head = [(286, 336), (300, 300), (330, 284), (352, 268), (380, 262), (460, 258), (540, 252), (610, 248), (610, 352), (286, 352)]
    out.append(ledge(f"{u}-hd", head, "#F2D6C2", f"url(#{u}-cliff)", 12, cracks=16))
    rs = random.Random(13)
    # spruces behind the light station
    sp_line = [(330, 270), (380, 262), (460, 258), (540, 252), (610, 248)]
    for k in range(34):
        x = rs.uniform(450, 615)
        y = y_on(sp_line, min(x, 609)) or 252
        out.append(conifer(x, y + 4, rs.uniform(46, 96), rs.choice(["#1E3A30", "#24443A", "#2A4A3A"]), rs.random(), width=0.34, light="#4E7A5A"))
    for k in range(8):
        x = rs.uniform(330, 372)
        y = y_on(sp_line, x) or 266
        out.append(conifer(x, y + 4, rs.uniform(26, 44), rs.choice(["#24443A", "#2A4A3A"]), rs.random(), width=0.34, light="#5A8A64"))
    out.append(f'<path d="M 330 286 Q 340 272 380 266 L 460 262 L 540 256 L 610 252 L 610 262 L 540 266 L 460 270 L 380 274 Q 344 280 330 290 Z" fill="#8A9A4E"/>')
    out.append(grass(70, 15, (330, 256, 610, 272), ["#6A7A3A", "#A8A85A", "#4E5E2E"], h=(4, 10)))
    # keeper's house and the white tower, lit from the left
    out.append(keeper_house(416, 266, 64, 46, roof="#A8403A", shade_side=1, seed=4))
    out.append(f'<rect x="396" y="246" width="22" height="20" fill="#F6F2EA"/><rect x="408" y="246" width="10" height="20" fill="#4A4E66" opacity="0.25"/>'
               f'<path d="M 394 247 L 420 247 L 420 243 L 394 243 Z" fill="#A8403A"/>')
    out.append(lighthouse_tower(f"{u}-lh", 386, 268, 118, 30, 19, pattern="white", light_from=-1))
    out.append('<g stroke="#F6F2EA" stroke-width="1.6"><line x1="340" y1="276" x2="372" y2="270"/><line x1="340" y1="282" x2="372" y2="276"/>'
               + "".join(f'<line x1="{x}" y1="{276 - (x - 340) * 0.18:.1f}" x2="{x}" y2="{284 - (x - 340) * 0.18:.1f}"/>' for x in range(340, 374, 8)) + "</g>")
    # surf rolling in against the headland foot
    out.append(billow(330, 352, 110, 30, 21, f"{u}-spray", hi="#FFFFFF", hi_op=0.7, shade="#8AA4BE", n=30))
    # the inlet between the near ledges: dark green-blue water laced with foam
    out.append(f'<path d="M -10 360 Q 120 352 300 372 Q 420 362 610 356 L 610 444 L -10 444 Z" fill="#1E4A5E"/>')
    rl = random.Random(26)
    lace = []
    for i in range(40):
        y = rl.uniform(360, 440)
        x = rl.uniform(180, 420)
        w = rl.uniform(20, 60)
        lace.append(f'<path d="M {x:.1f} {y:.1f} q {w * 0.25:.1f} {-4:.1f} {w * 0.5:.1f} 0 t {w * 0.5:.1f} 0" stroke-width="{rl.uniform(1.4, 3):.1f}" opacity="{rl.uniform(0.5, 0.95):.2f}"/>')
    out.append('<g fill="none" stroke="#F4F8FA" stroke-linecap="round">' + "".join(lace) + "</g>")
    out.append(blobs(40, 25, (200, 360, 420, 444), ["#FFFFFF", "#DCE8F0"], r=(3, 10), opacity=(0.5, 0.9), squash=0.4))
    # a wave exploding on the near ledge: white base, jets of spray fanning up, drifting droplets
    sx_, sy_ = 236, 372
    out.append(billow(sx_ + 6, sy_ + 6, 120, 54, 22, f"{u}-spray", hi="#FFFFFF", hi_op=0.75, shade="#7A96B2", n=46, lit_dx=-0.3))
    jets = []
    rj = random.Random(27)
    for i in range(18):
        a_ = math.radians(rj.uniform(-145, -45))
        L = rj.uniform(40, 110)
        x0 = sx_ + rj.uniform(-30, 30)
        y0 = sy_ - 20
        x1, y1 = x0 + L * math.cos(a_), y0 + L * math.sin(a_)
        w = rj.uniform(3, 9)
        jets.append(f'<path d="M {x0 - w:.1f} {y0:.1f} Q {(x0 + x1) / 2 - w * 0.9:.1f} {(y0 + y1) / 2:.1f} {x1:.1f} {y1:.1f} Q {(x0 + x1) / 2 + w * 0.9:.1f} {(y0 + y1) / 2:.1f} {x0 + w:.1f} {y0:.1f} Z" opacity="{rj.uniform(0.2, 0.55):.2f}"/>')
    out.append('<g fill="#FFFFFF">' + "".join(jets) + "</g>")
    out.append(mist(sx_, sy_ - 50, 100, 70, "#FFFFFF", f"{u}-sm", 0.7))
    out.append(dots(140, 23, (150, 240, 330, 350), "#FFFFFF", r=(1, 2.8), opacity=(0.5, 1)))
    l1 = [(-10, 352), (40, 340), (110, 336), (170, 348), (214, 366), (240, 392), (262, 444), (-10, 444)]
    out.append(ledge(f"{u}-l1", l1, "#F0CDB8", "#A07E80", 31, cracks=14, weed="#8A6A20", weed_y=None))
    l2 = [(372, 444), (392, 404), (430, 380), (490, 370), (556, 372), (610, 366), (610, 444)]
    out.append(ledge(f"{u}-l2", l2, "#E8C6B4", "#8E6E74", 32, cracks=12))
    out.append(f'<path d="M -10 420 Q 80 412 150 418 Q 200 424 250 440 L 260 444 L -10 444 Z" fill="#5E4A1A"/>')
    out.append(f'<path d="M 380 444 Q 420 424 480 420 Q 560 418 610 412 L 610 444 Z" fill="#5E4A1A"/>')
    rw2 = random.Random(35)
    weed = []
    for _ in range(170):
        x = rw2.uniform(-10, 610)
        if 250 < x < 390:
            continue
        ytop = (418 - 6 * math.sin(x / 50)) if x < 300 else (424 - (x - 380) * 0.05)
        y = rw2.uniform(ytop - 4, 444)
        L = rw2.uniform(6, 16)
        weed.append(f'<path d="M {x:.1f} {y:.1f} q {rw2.uniform(-4, 4):.1f} {L / 2:.1f} {rw2.uniform(-3, 3):.1f} {L:.1f}" stroke="{rw2.choice(["#8A6A20", "#A8862E", "#6A5418", "#C8A040"])}"/>')
    out.append('<g fill="none" stroke-width="2.6" stroke-linecap="round">' + "".join(weed) + "</g>")
    # tide pool on the near ledge reflecting the sky
    out.append('<ellipse cx="96" cy="372" rx="30" ry="6" fill="#8FB4D2"/><ellipse cx="90" cy="371" rx="16" ry="2" fill="#FFFFFF" opacity="0.6"/>')
    out.append(gulls([(250, 150, 8), (272, 162, 6), (520, 300, 6), (110, 300, 5)], "#2E3A4A", 2))
    out.append(gull(470, 330, 0.9, -4))
    return "\n".join(out)


# ---------------------------------------------------------------- Cape Cod (golden hour in the dunes)
def cape_cottage(uid, x, base, w, wall_h, roof_h, seed=2):
    """Weathered grey-shingled half Cape: steep side-gabled roof, big central chimney, white trim,
    6-over-6 windows, a red door, roses climbing the front. Lit from the right."""
    rnd = random.Random(seed)
    eave = base - wall_h
    ridge = eave - roof_h
    end = w * 0.32
    out = []
    # right end wall in sun (gable)
    ex0, ex1 = x + w, x + w + end
    gable = [(ex0, base), (ex0, eave), (ex0 + end * 0.45, ridge + 4), (ex1, eave + 6), (ex1, base + 4)]
    out.append(f'<clipPath id="{uid}-g"><polygon points="{P(gable)}"/></clipPath>')
    out.append(f'<polygon points="{P(gable)}" fill="#C8B49A"/>')
    sh = []
    for yy in range(int(ridge), int(base) + 6, 5):
        sh.append(f'<line x1="{ex0:.1f}" y1="{yy:.1f}" x2="{ex1:.1f}" y2="{yy + 6 * (ex1 - ex0) / end * 0.0 + 2:.1f}"/>')
        for k_ in range(int(end / 6)):
            sh.append(f'<line x1="{ex0 + k_ * 6 + (yy % 10) * 0.3:.1f}" y1="{yy:.1f}" x2="{ex0 + k_ * 6 + (yy % 10) * 0.3:.1f}" y2="{yy + 5:.1f}"/>')
    out.append(f'<g clip-path="url(#{uid}-g)" stroke="#8A7A6A" stroke-width="0.9" opacity="0.7">' + "".join(sh) + "</g>")
    out.append(f'<rect x="{ex0 + end * 0.3:.1f}" y="{eave + wall_h * 0.15:.1f}" width="{end * 0.32:.1f}" height="{wall_h * 0.45:.1f}" fill="#3A4656" stroke="#FFFDF4" stroke-width="2"/>')
    out.append(f'<rect x="{ex0 + end * 0.36:.1f}" y="{eave - roof_h * 0.45:.1f}" width="{end * 0.22:.1f}" height="{roof_h * 0.28:.1f}" fill="#3A4656" stroke="#FFFDF4" stroke-width="1.8"/>')
    out.append(f'<line x1="{ex0:.1f}" y1="{eave:.1f}" x2="{ex0 + end * 0.45:.1f}" y2="{ridge + 4:.1f}" stroke="#FFFDF4" stroke-width="2.4"/><line x1="{ex0 + end * 0.45:.1f}" y1="{ridge + 4:.1f}" x2="{ex1:.1f}" y2="{eave + 6:.1f}" stroke="#FFFDF4" stroke-width="2.4"/>')
    # front wall (in soft shade)
    out.append(f'<clipPath id="{uid}-f"><rect x="{x:.1f}" y="{eave:.1f}" width="{w:.1f}" height="{wall_h:.1f}"/></clipPath>')
    out.append(f'<rect x="{x:.1f}" y="{eave:.1f}" width="{w:.1f}" height="{wall_h:.1f}" fill="#9A8C84"/>')
    sh = []
    for i, yy in enumerate(range(int(eave), int(base), 5)):
        sh.append(f'<line x1="{x:.1f}" y1="{yy:.1f}" x2="{x + w:.1f}" y2="{yy:.1f}" stroke="#6A5E5E" stroke-width="1"/>')
        for k_ in range(int(w / 6) + 1):
            xx = x + k_ * 6 + (3 if i % 2 else 0) + rnd.uniform(-1, 1)
            sh.append(f'<line x1="{xx:.1f}" y1="{yy:.1f}" x2="{xx:.1f}" y2="{yy + 5:.1f}" stroke="#6A5E5E" stroke-width="0.8"/>')
            if rnd.random() < 0.18:
                sh.append(f'<rect x="{xx:.1f}" y="{yy:.1f}" width="6" height="5" fill="{rnd.choice(["#B0A49A", "#7E726C"])}"/>')
    out.append(f'<g clip-path="url(#{uid}-f)" opacity="0.8">' + "".join(sh) + "</g>")
    # corner boards and trim
    out.append(f'<rect x="{x - 1:.1f}" y="{eave:.1f}" width="4" height="{wall_h:.1f}" fill="#F4F0E6"/><rect x="{x + w - 3:.1f}" y="{eave:.1f}" width="4" height="{wall_h:.1f}" fill="#FFFDF4"/>')
    # windows: two each side of the door
    for fx in (0.13, 0.31, 0.69, 0.87):
        wx = x + w * fx
        ww, wh = w * 0.1, wall_h * 0.5
        wy = eave + wall_h * 0.18
        out.append(f'<rect x="{wx - ww / 2 - 2:.1f}" y="{wy - 2:.1f}" width="{ww + 4:.1f}" height="{wh + 4:.1f}" fill="#F4F0E6"/>'
                   f'<rect x="{wx - ww / 2:.1f}" y="{wy:.1f}" width="{ww:.1f}" height="{wh:.1f}" fill="#46566A"/>'
                   f'<path d="M {wx - ww / 2:.1f} {wy + wh / 2:.1f} H {wx + ww / 2:.1f} M {wx - ww / 6:.1f} {wy:.1f} V {wy + wh:.1f} M {wx + ww / 6:.1f} {wy:.1f} V {wy + wh:.1f} M {wx - ww / 2:.1f} {wy + wh / 4:.1f} H {wx + ww / 2:.1f} M {wx - ww / 2:.1f} {wy + wh * 0.75:.1f} H {wx + ww / 2:.1f}" stroke="#F4F0E6" stroke-width="1"/>'
                   f'<rect x="{wx - ww / 2:.1f}" y="{wy:.1f}" width="{ww * 0.4:.1f}" height="{wh:.1f}" fill="#FFE8B0" opacity="0.25"/>')
    dx = x + w * 0.5
    out.append(f'<rect x="{dx - w * 0.07:.1f}" y="{eave + wall_h * 0.1:.1f}" width="{w * 0.14:.1f}" height="{wall_h * 0.9:.1f}" fill="#F4F0E6"/>'
               f'<rect x="{dx - w * 0.05:.1f}" y="{eave + wall_h * 0.22:.1f}" width="{w * 0.1:.1f}" height="{wall_h * 0.78:.1f}" fill="#A8342E"/>'
               f'<circle cx="{dx + w * 0.03:.1f}" cy="{eave + wall_h * 0.62:.1f}" r="1.4" fill="#E8C060"/>'
               f'<rect x="{dx - w * 0.05:.1f}" y="{eave + wall_h * 0.12:.1f}" width="{w * 0.1:.1f}" height="{wall_h * 0.08:.1f}" fill="#46566A"/>')
    # roof: cedar shingles weathered dark, lit edge on the right
    roof = [(x - 5, eave + 2), (x + 6, ridge), (ex0 + end * 0.45, ridge + 4), (ex0 + 2, eave + 2)]
    out.append(f'<clipPath id="{uid}-r"><polygon points="{P(roof)}"/></clipPath>')
    out.append(f'<polygon points="{P(roof)}" fill="#6E645E"/>')
    rr = []
    for i, yy in enumerate(range(int(ridge), int(eave) + 2, 5)):
        rr.append(f'<line x1="{x - 10:.1f}" y1="{yy:.1f}" x2="{ex0 + 20:.1f}" y2="{yy:.1f}" stroke="#4A4240" stroke-width="1"/>')
        for k_ in range(int((w + 30) / 7)):
            xx = x - 8 + k_ * 7 + (3.5 if i % 2 else 0)
            rr.append(f'<line x1="{xx:.1f}" y1="{yy:.1f}" x2="{xx:.1f}" y2="{yy + 5:.1f}" stroke="#4A4240" stroke-width="0.7"/>')
    out.append(f'<g clip-path="url(#{uid}-r)" opacity="0.7">' + "".join(rr) +
               f'<rect x="{x - 10:.1f}" y="{ridge:.1f}" width="{w + 30:.1f}" height="{roof_h:.1f}" fill="url(#{uid}-rg)"/></g>')
    out.insert(0, defs(lg(f"{uid}-rg", [(0, "#FFD89A", 0), (0.7, "#FFD89A", 0.05), (1, "#FFD89A", 0.35)], 0, 0, 1, 0)))
    out.append(f'<line x1="{x + 6:.1f}" y1="{ridge:.1f}" x2="{ex0 + end * 0.45:.1f}" y2="{ridge + 4:.1f}" stroke="#E8C890" stroke-width="2" opacity="0.8"/>')
    # central brick chimney
    cx = x + w * 0.52
    out.append(f'<rect x="{cx - 9:.1f}" y="{ridge - 16:.1f}" width="18" height="20" fill="#9A4A36"/><rect x="{cx + 2:.1f}" y="{ridge - 16:.1f}" width="7" height="20" fill="#C8704E"/>'
               f'<rect x="{cx - 11:.1f}" y="{ridge - 19:.1f}" width="22" height="4" fill="#6A3226"/>'
               + '<g stroke="#6A3226" stroke-width="0.8">' + "".join(f'<line x1="{cx - 9:.1f}" y1="{ridge - 12 + i * 4:.1f}" x2="{cx + 9:.1f}" y2="{ridge - 12 + i * 4:.1f}"/>' for i in range(4)) + "</g>")
    # climbing roses on the front and a rose bush at the corner
    out.append(blobs(40, seed + 5, (x - 6, eave + wall_h * 0.3, x + w * 0.25, base), ["#3E5A34", "#4E6A3A", "#2E4A2A"], r=(3, 7), opacity=(0.9, 1)))
    out.append(dots(26, seed + 6, (x - 4, eave + wall_h * 0.3, x + w * 0.24, base - 2), "#F07A9A", r=(1.4, 2.6), opacity=(0.8, 1)))
    out.append(blobs(30, seed + 7, (x + w * 0.72, eave + wall_h * 0.5, ex0 + 6, base + 2), ["#3E5A34", "#4E6A3A", "#5A7A40"], r=(3, 7), opacity=(0.9, 1)))
    out.append(dots(18, seed + 8, (x + w * 0.72, eave + wall_h * 0.5, ex0 + 4, base), "#F48AAE", r=(1.4, 2.6), opacity=(0.8, 1)))
    return "".join(out)


def dune_fence(pts, color="#8A7A6A", lit="#F4D8A8", slat_h=14, gap=4.2, sw=2.2):
    """Snow fence of wooden slats wired together, following a polyline (in perspective: slats shrink with y)."""
    out = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        L = math.hypot(x2 - x1, y2 - y1)
        n = int(L / gap)
        for i in range(n):
            t = i / n
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            k = 0.4 + 0.6 * (y - 250) / 194
            hh = slat_h * k
            out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + 0.5:.1f}" y2="{y - hh:.1f}" stroke="{color if i % 3 else lit}" stroke-width="{max(1.2, sw * k):.1f}"/>')
    out.append(f'<polyline points="{P([(x, y - slat_h * (0.4 + 0.6 * (y - 250) / 194) * 0.25) for x, y in pts])}" fill="none" stroke="#5A4A3A" stroke-width="1"/>')
    out.append(f'<polyline points="{P([(x, y - slat_h * (0.4 + 0.6 * (y - 250) / 194) * 0.8) for x, y in pts])}" fill="none" stroke="#5A4A3A" stroke-width="1"/>')
    return f'<g stroke-linecap="round">' + "".join(out) + "</g>"


def cape_cod():
    u = "capecod"
    H = 238
    out = [defs(
        lg(f"{u}-sky", [(0, "#7EA6C8"), (0.45, "#B8C8D2"), (0.75, "#F2D2A8"), (1, "#FCE2B0")], 0, 40, 0, H, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#A8C2C8"), (0.3, "#5E8EA2"), (1, "#3A6A82")], 0, H, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-dune", [(0, "#E8C890"), (1, "#C89E6A")]),
        lg(f"{u}-dfar", [(0, "#E8CFA4"), (1, "#D4B286")]),
        lg(f"{u}-dnear", [(0, "#F2D49A"), (0.6, "#D8A86A"), (1, "#B8865A")]),
        lg(f"{u}-sh", [(0, "#8A7AA0", 0.45), (1, "#8A7AA0", 0)], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="{H + 1}" fill="url(#{u}-sky)"/>')
    out.append(glow(610, 170, 330, "#FFE2A8", f"{u}-sun", 0.8))
    # high clouds gilded on their right
    for x, y, w, h_, n in ((140, 104, 210, 40, 34), (440, 126, 170, 30, 26), (290, 176, 130, 22, 20)):
        out.append(cloud_puffs(x, y, w, h_, x, "#E6D6D2", "#FFF0D0", shade="#B0A8C4", n=n, lit_dx=0.35, lit_dy=-0.2))
    # sea with sailboats out on the bay
    out.append(f'<rect x="0" y="{H}" width="600" height="80" fill="url(#{u}-sea)"/>')
    out.append(ripples(60, 3, (0, H + 2, 600, H + 50), ["#FFF0D0", "#E8F0F0"], w=(8, 24), h=1.3, opacity=(0.4, 0.9)))
    for bx, by_, sc, sail in ((300, H + 12, 0.8, "#FFF8EC"), (356, H + 6, 0.55, "#FFF2E0"), (240, H + 8, 0.5, "#F6E8D8")):
        out.append(f'<g transform="translate({bx} {by_}) scale({sc})"><path d="M -16 -2 L 16 -2 L 12 4 L -12 4 Z" fill="#3A4A5A"/>'
                   f'<path d="M 0 -4 L 0 -46 L 16 -6 Z" fill="{sail}"/><path d="M -2 -6 L -2 -40 L -16 -6 Z" fill="#E8D8C8"/><path d="M 0 -46 L 16 -6" stroke="#FFD89A" stroke-width="1.6"/></g>')
    # distant bluff with the lighthouse and its keeper's house
    bl = [(380, H + 2), (420, H - 14), (470, H - 20), (610, H - 24), (610, H + 4)]
    out.append(f'<polygon points="{P(bl)}" fill="#D8A878"/>')
    out.append(f'<polygon points="{P([(380, H + 2), (420, H - 14), (440, H - 12), (412, H + 2)])}" fill="#A87A64" opacity="0.6"/>')
    out.append(f'<path d="M 420 {H - 14} L 470 {H - 20} L 610 {H - 24} L 610 {H - 18} L 470 {H - 15} L 422 {H - 10} Z" fill="#9AA06A"/>')
    out.append(keeper_house(500, H - 18, 30, 22, roof="#5A5A62", shade_side=-1, chimney=False, seed=9))
    out.append(lighthouse_tower(f"{u}-lh", 482, H - 18, 64, 15, 10, pattern="white", light_from=1, windows=2, door=False))
    # rolling dunes, far to near
    poly, d1 = ridge_poly([(-10, 266), (90, 250), (200, 262), (300, 270), (420, 258), (520, 248), (610, 252)], 4, base=444, amp=6, fill=f"url(#{u}-dfar)")
    out.append(poly)
    out.append(grass(160, 5, (-10, 250, 610, 280), ["#8A9A5A", "#A8A86A", "#6A7A4A", "#C8B878"], h=(5, 10), sw=1.3))
    # shaded lee sides
    out.append(f'<path d="M 200 262 Q 160 270 120 290 L 200 290 Z" fill="#9A88A8" opacity="0.25"/>')
    poly, d2 = ridge_poly([(-10, 300), (60, 290), (150, 296), (260, 300), (360, 286), (460, 292), (610, 284)], 6, base=444, amp=5, fill=f"url(#{u}-dune)")
    out.append(poly)
    # the cottage tucked into the dunes
    # long shadow of the cottage cast left across the sand
    out.append(f'<path d="M 74 314 L -10 322 L -10 332 L 74 322 Z" fill="#8A7AA0" opacity="0.3"/>')
    out.append(cape_cottage(f"{u}-ct", 74, 314, 166, 48, 60, seed=3))
    out.append(f'<path d="M 50 316 Q 170 306 320 316 L 320 328 L 50 328 Z" fill="#D8B07A"/>')
    out.append(grass(110, 7, (40, 304, 330, 326), ["#7A8A4A", "#A8A060", "#5A6A3A", "#C8B878"], h=(8, 20), sw=1.6))
    # lavender shade in the hollows between dunes
    out.append(f'<path d="M 330 300 Q 420 296 470 320 Q 420 330 340 326 Z" fill="#9A88B0" opacity="0.25"/>')
    out.append(grass(120, 8, (330, 290, 610, 340), ["#7A8A4A", "#A8A060", "#5A6A3A", "#C8B878"], h=(6, 16), sw=1.5))
    # near dune with a sand path and the snow fence leading up to the cottage
    near = rough([(-10, 352), (80, 340), (180, 330), (280, 344), (380, 360), (480, 350), (610, 340)], 8, amp=6, depth=3)
    out.append(f'<polygon points="{P(near + [(610, 444), (-10, 444)])}" fill="url(#{u}-dnear)"/>')
    out.append(f'<path d="M 290 444 Q 270 400 246 370 Q 226 344 196 326 L 212 326 Q 252 344 276 368 Q 314 404 346 444 Z" fill="#F6DCA8"/>')
    out.append(f'<path d="M 290 444 Q 270 400 246 370 Q 226 344 196 326" fill="none" stroke="#C89A68" stroke-width="2" opacity="0.6"/>')
    out.append(dots(160, 41, (220, 330, 360, 444), "#B88A5A", r=(0.6, 1.6), opacity=(0.3, 0.7)))
    out.append(dune_fence([(372, 446), (338, 406), (306, 374), (272, 350), (238, 332)], color="#6A584A", lit="#E8C48A", slat_h=40, gap=5, sw=2.8))
    # wind-combed beach grass in the foreground, lit gold on the tips
    rg_ = random.Random(51)
    blades = []
    for _ in range(420):
        x = rg_.uniform(-10, 610)
        if 240 < x < 330 and rg_.random() < 0.85:
            continue
        ytop = y_on(near, min(max(x, -9), 609)) or 350
        y = rg_.uniform(ytop + 4, 450)
        k = (y - 330) / 114
        L = rg_.uniform(18, 46) * (0.6 + 0.8 * k)
        bend = rg_.uniform(8, 20) * (0.6 + k)
        col = rg_.choice(["#6A7A3E", "#8A964E", "#A8A45A", "#4E5E30", "#C8B46A"])
        blades.append(f'<path d="M {x:.1f} {y:.1f} q {-bend * 0.2:.1f} {-L * 0.6:.1f} {-bend:.1f} {-L:.1f}" stroke="{col}" stroke-width="{1.4 + 1.2 * k:.1f}"/>')
    out.append('<g fill="none" stroke-linecap="round">' + "".join(blades) + "</g>")
    out.append(grass(80, 52, (-10, 380, 240, 444), ["#F2D890", "#E8C878"], h=(10, 22), sw=1.4))
    out.append(grass(60, 53, (360, 370, 610, 444), ["#F2D890", "#E8C878"], h=(10, 22), sw=1.4))
    # rugosa roses blooming in the near dune
    for cx, cy in ((90, 384), (520, 376), (560, 400)):
        out.append(blobs(18, cx, (cx - 26, cy - 14, cx + 26, cy + 10), ["#3E5A34", "#4E6A3A", "#5E7A40"], r=(4, 8), opacity=(0.9, 1)))
        rr = random.Random(cy)
        for _ in range(6):
            fx, fy = cx + rr.uniform(-20, 20), cy + rr.uniform(-12, 6)
            out.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="3.6" fill="#E8508A"/><circle cx="{fx:.1f}" cy="{fy:.1f}" r="1.3" fill="#F8D860"/>')
    out.append(gulls([(330, 150, 7), (352, 160, 5), (120, 196, 6)], "#4A4458", 1.8))
    return "\n".join(out)


# ---------------------------------------------------------------- Outer Banks (storm clearing, wild horses, the spiral tower)
def horse(x, y, s=1.0, coat="#7A4A2E", dark="#221814", mane="#1A1210", rim="#FFD8A0", head_rot=0, flip=False, blaze=False, socks=()):
    """Banker / Spanish mustang in profile facing left (flip to face right). (x, y) = front hoof on the ground,
    s = 1 -> ~135 px long. head_rot rotates neck+head down (positive = grazing)."""
    sc = -s if flip else s
    legs = [((52, 64), (50, 84), (52, 100), 6.2, 0), ((62, 64), (64, 84), (66, 100), 6.0, 1),
            ((108, 62), (110, 82), (104, 100), 6.4, 2), ((120, 62), (126, 80), (120, 100), 6.6, 3)]
    out = [f'<g transform="translate({x - 50 * sc:.1f} {y - 100 * s:.1f}) scale({sc:.3f} {s:.3f})">']
    # far legs darker, drawn first
    for (a, b, c, w, i) in legs:
        col = "#3A2418" if i in (0, 2) else coat
        if i in (0, 2):
            out.append(f'<path d="M {a[0]} {a[1]} Q {b[0]} {b[1]} {c[0]} {c[1]}" stroke="{col}" stroke-width="{w}" stroke-linecap="round" fill="none"/>'
                       f'<path d="M {b[0]} {b[1] + 4} Q {(b[0] + c[0]) / 2} {(b[1] + c[1]) / 2} {c[0]} {c[1] - 1}" stroke="{dark}" stroke-width="{w * 0.85:.1f}" stroke-linecap="round" fill="none"/>')
    out.append(f'<path d="M 120 48 Q 140 54 138 72 Q 136 84 140 92 Q 130 86 128 72 Q 126 60 120 56 Z" fill="{mane}"/>')
    out.append(f'<path d="M 46 40 C 52 30 72 32 92 34 C 112 34 128 32 132 48 C 134 60 128 70 112 70 C 92 72 72 72 58 70 C 44 68 40 54 46 40 Z" fill="{coat}"/>')
    # belly shade and barrel highlight
    out.append(f'<path d="M 58 70 C 72 72 92 72 112 70 C 120 69 126 66 128 62 C 110 66 80 66 54 62 Z" fill="#000" opacity="0.22"/>')
    out.append(f'<path d="M 70 40 C 90 38 112 38 124 44" stroke="{rim}" stroke-width="2.4" fill="none" opacity="0.55" stroke-linecap="round"/>')
    # near legs
    for (a, b, c, w, i) in legs:
        if i in (1, 3):
            out.append(f'<path d="M {a[0]} {a[1] - 4} Q {b[0]} {b[1]} {c[0]} {c[1]}" stroke="{coat}" stroke-width="{w}" stroke-linecap="round" fill="none"/>'
                       f'<path d="M {b[0]} {b[1] + 4} Q {(b[0] + c[0]) / 2} {(b[1] + c[1]) / 2} {c[0]} {c[1] - 1}" stroke="{"#F2EADC" if i in socks else dark}" stroke-width="{w * 0.85:.1f}" stroke-linecap="round" fill="none"/>')
        out.append(f'<ellipse cx="{c[0] - 1}" cy="{c[1]}" rx="{w * 0.6:.1f}" ry="2" fill="#1A120E"/>')
    out.append(f'<path d="M 108 44 Q 124 46 126 62 Q 118 66 110 64 Q 112 54 108 44 Z" fill="#000" opacity="0.12"/>')
    # neck and head, rotatable about the base of the neck
    out.append(f'<g transform="rotate({head_rot} 58 46)">')
    out.append(f'<path d="M 72 38 C 58 20 46 8 34 6 L 26 24 C 32 38 38 50 42 62 C 52 60 62 52 72 38 Z" fill="{coat}"/>')
    out.append(f'<path d="M 36 6 C 28 6 16 16 8 28 C 4 34 4 40 10 42 C 14 43 18 40 22 36 C 28 34 34 30 32 20 Z" fill="{coat}"/>')
    out.append(f'<path d="M 26 24 C 32 38 38 50 42 62 C 46 60 48 56 50 52 C 42 44 36 34 32 22 Z" fill="#000" opacity="0.18"/>')
    out.append(f'<path d="M 8 30 C 4 34 4 40 10 42 C 13 43 16 41 18 38 Z" fill="{dark}" opacity="0.75"/>')
    out.append(f'<circle cx="8" cy="36" r="1.2" fill="#000"/>')
    out.append(f'<path d="M 29 8 L 29 -3 L 35 7 Z" fill="{coat}"/><path d="M 32 9 L 35 -1 L 38 10 Z" fill="{dark}"/>')
    out.append(f'<circle cx="22" cy="17" r="1.9" fill="#120C0A"/><circle cx="22.5" cy="16.4" r="0.6" fill="#FFFFFF"/>')
    if blaze:
        out.append(f'<path d="M 26 10 Q 16 20 7 32 L 10 34 Q 18 24 29 12 Z" fill="#F2EADC"/>')
    # mane falling along the crest
    rnd = random.Random(int(x * 7 + y))
    out.append(f'<path d="M 34 4 C 48 10 62 24 74 38 L 68 42 C 58 30 46 18 32 10 Z" fill="{mane}"/>')
    out.append(f'<g stroke="{mane}" stroke-width="2.2" stroke-linecap="round" fill="none">' + "".join(
        f'<path d="M {36 + t * 36:.1f} {6 + t * 30:.1f} q {rnd.uniform(2, 6):.1f} {rnd.uniform(4, 8):.1f} {rnd.uniform(0, 4):.1f} {rnd.uniform(8, 14):.1f}"/>' for t in [i / 9 for i in range(10)]) + "</g>")
    out.append(f'<path d="M 30 4 Q 22 2 22 10" stroke="{mane}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    out.append(f'<path d="M 36 5 C 48 10 62 24 74 38" stroke="{rim}" stroke-width="1.8" fill="none" opacity="0.6"/>')
    out.append("</g>")
    out.append("</g>")
    return "".join(out)


def sea_oats(x, base, h, seed, stem="#A88A4A", seed_col="#D8B060", rim=None, lean=-0.15):
    """Sea oats: tall arching stem with a drooping panicle of flat seed spikelets."""
    rnd = random.Random(seed)
    tx, ty = x + lean * h, base - h
    out = [f'<path d="M {x:.1f} {base:.1f} Q {x + lean * h * 0.2:.1f} {base - h * 0.6:.1f} {tx:.1f} {ty:.1f}" stroke="{stem}" stroke-width="{max(1.2, h * 0.018):.1f}" fill="none"/>']
    # leaves at the base
    for i in range(3):
        L = h * rnd.uniform(0.25, 0.45)
        d = rnd.choice((-1, 1))
        out.append(f'<path d="M {x:.1f} {base:.1f} q {d * L * 0.3:.1f} {-L * 0.6:.1f} {d * L * 0.7:.1f} {-L * 0.7:.1f}" stroke="#7A8A4A" stroke-width="{max(1.2, h * 0.016):.1f}" fill="none"/>')
    # panicle: spikelets hanging from the top 30% of the stem
    for i in range(9):
        t = 0.7 + 0.3 * i / 8
        px = x + lean * h * (t ** 2)
        py = base - h * t
        side = -1 if i % 2 else 1
        sx, sy = px + side * h * rnd.uniform(0.04, 0.09), py + h * rnd.uniform(0.03, 0.07)
        out.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{stem}" stroke-width="0.9"/>')
        out.append(f'<ellipse cx="{sx:.1f}" cy="{sy:.1f}" rx="{max(1.6, h * 0.022):.1f}" ry="{max(3, h * 0.05):.1f}" fill="{seed_col}" transform="rotate({side * 25} {sx:.1f} {sy:.1f})"/>')
        if rim:
            out.append(f'<ellipse cx="{sx + 0.8:.1f}" cy="{sy - 0.5:.1f}" rx="{max(0.8, h * 0.01):.1f}" ry="{max(1.6, h * 0.035):.1f}" fill="{rim}" opacity="0.8" transform="rotate({side * 25} {sx:.1f} {sy:.1f})"/>')
    return "".join(out)


def outer_banks():
    u = "outerbanks"
    H = 262
    out = [defs(
        lg(f"{u}-sky", [(0, "#2E3648"), (0.4, "#4E5A6E"), (0.75, "#8A94A0"), (1, "#C8C2B4")], 0, 40, 0, H, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#6E8494"), (0.4, "#3E5A6E"), (1, "#2A4252")], 0, H, 0, 320, units="userSpaceOnUse"),
        lg(f"{u}-dune", [(0, "#E8C890"), (1, "#C8A06A")]),
        lg(f"{u}-dnear", [(0, "#D8B47A"), (0.6, "#B88A58"), (1, "#8A6448")]),
        lg(f"{u}-ray", [(0, "#FFE6B0", 0.4), (1, "#FFE6B0", 0)]),
        lg(f"{u}-storm", [(0, "#232A3A"), (1, "#3A4256")]),
    )]
    out.append(f'<rect width="600" height="{H + 1}" fill="url(#{u}-sky)"/>')
    # break in the storm on the right: bright gap low over the sea
    out.append(glow(470, 170, 260, "#FFE0A8", f"{u}-gap", 0.85))
    # heavy storm clouds rolling off to the left, with ragged, lit edges toward the gap
    out.append(f'<path d="M -10 40 L 610 40 L 610 70 Q 540 96 480 80 Q 440 110 380 96 Q 340 130 280 122 Q 230 160 170 150 Q 120 186 60 176 Q 20 196 -10 190 Z" fill="url(#{u}-storm)"/>')
    sc = random.Random(4)
    puffs = []
    for i in range(60):
        t = i / 59
        x = 610 - t * 640 + sc.uniform(-8, 8)
        y = 70 + t * 112 + sc.uniform(-6, 12)
        r = sc.uniform(18, 34) * (0.7 + 0.5 * t)
        puffs.append((x, y, r))
        if sc.random() < 0.6:
            puffs.append((x + sc.uniform(-20, 20), y - r * sc.uniform(0.6, 1.4), r * sc.uniform(0.8, 1.2)))
    out.append('<g fill="#F2D6A8" opacity="0.85">' + "".join(f'<circle cx="{x + r * 0.16:.1f}" cy="{y + r * 0.2:.1f}" r="{r:.1f}"/>' for x, y, r in puffs) + "</g>")
    out.append('<g fill="#8A8A94">' + "".join(f'<circle cx="{x + r * 0.08:.1f}" cy="{y + r * 0.1:.1f}" r="{r:.1f}"/>' for x, y, r in puffs) + "</g>")
    out.append('<g fill="#3E4658">' + "".join(f'<circle cx="{x - r * 0.04:.1f}" cy="{y - r * 0.04:.1f}" r="{r:.1f}"/>' for x, y, r in puffs) + "</g>")
    out.append('<g fill="#2C3344" opacity="0.7">' + "".join(f'<circle cx="{x - r * 0.3:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.7:.1f}"/>' for x, y, r in puffs) + "</g>")
    # rain veils trailing from the storm on the far left
    out.append('<g stroke="#2E3648" stroke-width="2" opacity="0.25">' + "".join(f'<line x1="{x}" y1="180" x2="{x - 14}" y2="{H}"/>' for x in range(-10, 150, 7)) + "</g>")
    # crepuscular rays through the gap
    for a0, a1 in ((100, 112), (118, 126), (132, 142), (60, 70)):
        r0 = 600
        out.append(f'<polygon points="{P([(520, 110), (520 + r0 * math.cos(math.radians(a0)), 110 + r0 * math.sin(math.radians(a0))), (520 + r0 * math.cos(math.radians(a1)), 110 + r0 * math.sin(math.radians(a1)))])}" fill="url(#{u}-ray)" opacity="0.5"/>')
    # sea and breakers
    out.append(f'<rect x="0" y="{H}" width="600" height="70" fill="url(#{u}-sea)"/>')
    out.append(ripples(60, 5, (250, H + 2, 600, H + 30), ["#FFE6B0", "#F4F0E0"], w=(8, 30), h=1.4, opacity=(0.4, 0.9)))
    for y in (H + 12, H + 24, H + 34):
        rr = random.Random(y)
        for _ in range(10):
            cx = rr.uniform(0, 600)
            w = rr.uniform(30, 90)
            out.append(f'<path d="M {cx - w / 2:.1f} {y:.1f} q {w / 2:.1f} -5 {w:.1f} 0 Z" fill="#F4F2EA" opacity="{rr.uniform(0.6, 0.95):.2f}"/>')
    # far dune line and the light station
    poly, d1 = ridge_poly([(-10, 300), (120, 288), (260, 296), (380, 290), (500, 294), (610, 288)], 3, base=444, amp=4, fill=f"url(#{u}-dune)")
    out.append(poly)
    out.append(grass(140, 6, (-10, 284, 610, 304), ["#8A8A4E", "#A8A060", "#6A6A3E"], h=(5, 11), sw=1.3))
    out.append(keeper_house(452, 300, 56, 34, wall="#F4F0E6", roof="#4A4A52", shade_side=-1, chimney=True, seed=6))
    out.append(lighthouse_tower(f"{u}-lh", 410, 302, 176, 32, 20, pattern="spiral", light_from=1, body="#F6F2EA", dark="#16161E", base_col="#A0503A", windows=4))
    # the near dune crest with sea oats, the horses on top
    near = rough([(-10, 352), (80, 338), (180, 334), (280, 346), (380, 364), (480, 372), (610, 366)], 9, amp=5, depth=3)
    out.append(f'<polygon points="{P(near + [(610, 444), (-10, 444)])}" fill="url(#{u}-dnear)"/>')
    out.append(f'<path d="M -10 346 Q 120 334 240 340 Q 300 344 330 352 Q 200 352 -10 364 Z" fill="#F2D49A" opacity="0.4"/>')
    for hx, hy, w in ((46, 347, 110), (168, 345, 64), (198, 353, 140)):
        out.append(f'<ellipse cx="{hx + w * 0.3:.1f}" cy="{hy + 2:.1f}" rx="{w * 0.7:.1f}" ry="4" fill="#6A4A5A" opacity="0.3"/>')
    out.append(dots(200, 61, (-10, 350, 610, 444), "#7A5A40", r=(0.6, 1.6), opacity=(0.3, 0.7)))
    # wind ripples in the sand
    out.append('<g fill="none" stroke="#8A6448" stroke-width="1.4" opacity="0.45">' + "".join(
        f'<path d="M {x} {y} q 20 -4 40 0 q 20 4 40 0"/>' for x, y in ((320, 392), (360, 404), (420, 396), (300, 416), (380, 426), (460, 414), (520, 400))) + "</g>")
    # the horses: a bay mare and her foal grazing, a chestnut stallion watching
    out.append(horse(88, 346, 0.82, coat="#6E3E26", head_rot=-50, rim="#FFD8A0"))
    out.append(horse(192, 344, 0.56, coat="#8A5634", mane="#3A2618", head_rot=8, rim="#FFE0A8", flip=True, socks=(3,)))
    out.append(horse(256, 352, 0.98, coat="#9A5A2E", mane="#4A2A1A", head_rot=-6, blaze=True, rim="#FFD8A0", socks=(1,)))
    # sea oats on the crest and in the foreground, lit gold on the right
    ro = random.Random(71)
    for _ in range(26):
        x = ro.uniform(-10, 610)
        if 40 < x < 330 and ro.random() < 0.7:
            continue
        yb = (y_on(near, min(max(x, -9), 609)) or 360) + ro.uniform(2, 30)
        out.append(sea_oats(x, yb, ro.uniform(50, 110), ro.randrange(999), rim="#FFE6A8", lean=ro.uniform(-0.25, -0.05)))
    out.append(grass(160, 72, (-10, 344, 610, 444), ["#8A8A4E", "#A8A060", "#6A6A3E", "#C8B070"], h=(8, 20), sw=1.6))
    # hoofprints wandering down the dune
    hp = random.Random(73)
    prints = []
    for i in range(16):
        t = i / 15
        x = 200 + 160 * t + hp.uniform(-6, 6) + (6 if i % 2 else -6)
        y = 362 + 70 * t
        prints.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{2.5 + 2 * t:.1f}" ry="{1.4 + 1 * t:.1f}" fill="#7A5844" opacity="0.5"/>')
    out.append("".join(prints))
    # tall sea oats framing the foreground
    for x, yb, h, sd in ((548, 448, 150, 5), (576, 450, 120, 6), (520, 452, 104, 7), (30, 450, 130, 8), (58, 452, 96, 9)):
        out.append(sea_oats(x, yb, h, sd, stem="#8A7040", seed_col="#C89A48", rim="#FFE6A8", lean=-0.18))
    # terns riding the wind
    out.append(gulls([(300, 200, 7), (318, 212, 5), (560, 230, 6)], "#2A3040", 2))
    return "\n".join(out)


# ---------------------------------------------------------------- Tybee Island (moonrise at dusk, light station and pier)
def ghost_crab(x, y, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.2f})">'
            '<g stroke="#D8C8A8" stroke-width="1.6" stroke-linecap="round" fill="none">'
            '<path d="M -8 0 l -8 -4 l -4 6 M -8 2 l -9 0 l -3 7 M -7 4 l -7 4 l -1 6 M 8 0 l 8 -4 l 4 6 M 8 2 l 9 0 l 3 7 M 7 4 l 7 4 l 1 6"/></g>'
            '<ellipse cx="0" cy="0" rx="10" ry="7" fill="#E8DCC0"/><ellipse cx="2" cy="-2" rx="6" ry="3" fill="#FFF6E0" opacity="0.6"/>'
            '<path d="M -6 -5 l -2 -8 M 6 -5 l 2 -8" stroke="#D8C8A8" stroke-width="1.6"/><circle cx="-8" cy="-13" r="2" fill="#2A2A30"/><circle cx="8" cy="-13" r="2" fill="#2A2A30"/>'
            '<path d="M -10 -2 q -8 -6 -4 -10 q 4 2 6 6 Z M 10 -2 q 9 -7 5 -12 q -5 2 -7 7 Z" fill="#E8DCC0"/>'
            '</g>')


def live_oak(x, base, w, h, seed, trunk="#1E2236", leaf=("#26304A", "#2A3450", "#222A42"), hi="#4A5A80", moss="#7A86A0"):
    """Southern live oak: short thick trunk, long low limbs, broad flattened canopy, Spanish moss hanging."""
    rnd = random.Random(seed)
    out = [f'<path d="M {x - w * 0.045:.1f} {base:.1f} L {x - w * 0.03:.1f} {base - h * 0.4:.1f} L {x + w * 0.03:.1f} {base - h * 0.4:.1f} L {x + w * 0.05:.1f} {base:.1f} Z" fill="{trunk}"/>']
    out.append(f'<g stroke="{trunk}" stroke-linecap="round" fill="none">'
               f'<path d="M {x:.1f} {base - h * 0.36:.1f} Q {x - w * 0.18:.1f} {base - h * 0.42:.1f} {x - w * 0.42:.1f} {base - h * 0.5:.1f}" stroke-width="{w * 0.035:.1f}"/>'
               f'<path d="M {x:.1f} {base - h * 0.36:.1f} Q {x + w * 0.2:.1f} {base - h * 0.44:.1f} {x + w * 0.44:.1f} {base - h * 0.52:.1f}" stroke-width="{w * 0.032:.1f}"/>'
               f'<path d="M {x:.1f} {base - h * 0.38:.1f} Q {x + w * 0.02:.1f} {base - h * 0.6:.1f} {x - w * 0.06:.1f} {base - h * 0.75:.1f}" stroke-width="{w * 0.03:.1f}"/></g>')
    clumps = []
    for _ in range(64):
        t = rnd.uniform(-1, 1)
        cx = x + t * w * 0.5
        cy = base - h * (0.52 + 0.34 * (1 - t * t)) + rnd.uniform(-h * 0.08, h * 0.08)
        r = rnd.uniform(0.08, 0.13) * w
        clumps.append((cx, cy, r))
    out.append("".join(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r:.1f}" ry="{r * 0.62:.1f}" fill="{rnd.choice(leaf)}"/>' for cx, cy, r in clumps))
    out.append(f'<g fill="{hi}" opacity="0.5">' + "".join(f'<ellipse cx="{cx + r * 0.2:.1f}" cy="{cy - r * 0.3:.1f}" rx="{r * 0.5:.1f}" ry="{r * 0.25:.1f}"/>' for cx, cy, r in clumps[::2]) + "</g>")
    ms = []
    for cx, cy, r in clumps:
        if rnd.random() < 0.7:
            L = rnd.uniform(8, 22)
            ms.append(f'<path d="M {cx:.1f} {cy + r * 0.4:.1f} q {rnd.uniform(-3, 3):.1f} {L / 2:.1f} {rnd.uniform(-2, 2):.1f} {L:.1f}"/>')
    out.append(f'<g stroke="{moss}" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.75">' + "".join(ms) + "</g>")
    return "".join(out)


def tybee():
    u = "tybee"
    H = 276
    out = [defs(
        lg(f"{u}-sky", [(0, "#122A48"), (0.35, "#2A4E74"), (0.6, "#6A86A8"), (0.78, "#D8A8B4"), (0.88, "#EDBFB0"), (0.93, "#8A8AB0"), (1, "#6E7AA4")], 0, 40, 0, H, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#7A84AC"), (0.3, "#4A5E86"), (1, "#22344E")], 0, H, 0, 360, units="userSpaceOnUse"),
        lg(f"{u}-sand", [(0, "#8A8098"), (0.5, "#6E6680"), (1, "#4A4460")], 0, 330, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-wet", [(0, "#9AA2C4"), (1, "#5A6A8E")]),
        lg(f"{u}-beam", [(0, "#FFF0C0", 0.35), (1, "#FFF0C0", 0)], 0, 0, 1, 0),
        lg(f"{u}-beamL", [(0, "#FFF0C0", 0), (1, "#FFF0C0", 0.3)], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="{H + 1}" fill="url(#{u}-sky)"/>')
    out.append(dots(70, 5, (0, 40, 600, 150), "#F4F2FF", r=(0.5, 1.4), opacity=(0.3, 1)))
    # full moon rising out of the sea, its path of light toward the beach
    mx, my = 468, 214
    out.append(glow(mx, my, 120, "#FFF2D8", f"{u}-mg", 0.55))
    out.append(f'<circle cx="{mx}" cy="{my}" r="20" fill="#FFF6E2"/>')
    out.append(f'<g fill="#E8DCC4" opacity="0.6"><circle cx="{mx - 6}" cy="{my - 5}" r="5"/><circle cx="{mx + 7}" cy="{my + 4}" r="4"/><circle cx="{mx - 2}" cy="{my + 9}" r="3"/><circle cx="{mx + 8}" cy="{my - 8}" r="2.5"/></g>')
    out.append(f'<ellipse cx="{mx - 90}" cy="{my + 10}" rx="80" ry="4" fill="#C8A0B4" opacity="0.6"/><ellipse cx="{mx + 60}" cy="{my + 24}" rx="70" ry="3" fill="#C8A0B4" opacity="0.6"/>')
    out.append(f'<rect x="0" y="{H}" width="600" height="90" fill="url(#{u}-sea)"/>')
    rnd = random.Random(6)
    gl = []
    for i in range(120):
        y = H + 2 + 80 * (rnd.random() ** 1.4)
        t = (y - H) / 80
        x = mx + rnd.gauss(0, 6 + 40 * t)
        w = rnd.uniform(5, 20) * (0.4 + t)
        gl.append(f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{1 + 1.4 * t:.1f}" rx="0.8" fill="#FFF2D0" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    out.append("".join(gl))
    out.append(ripples(50, 7, (0, H + 4, 600, H + 80), ["#9AA2C8", "#C8B0C4"], w=(10, 40), h=1.4, opacity=(0.3, 0.6)))
    # the pier and pavilion reaching out to sea on the right, lamps strung along it
    near_end, far_end = (612, 330), (372, 286)
    out.append(f'<polygon points="{P([near_end, (far_end[0], far_end[1]), (far_end[0], far_end[1] + 4), (near_end[0], near_end[1] + 10)])}" fill="#2A2C44"/>')
    pil = []
    for i in range(22):
        t = i / 21
        x = near_end[0] + (far_end[0] - near_end[0]) * t
        y = near_end[1] + (far_end[1] - near_end[1]) * t
        h = 40 * (1 - t) + 14 * t
        pil.append(f'<rect x="{x - 1.4:.1f}" y="{y:.1f}" width="{2.8 - 1.4 * t:.1f}" height="{h:.1f}" fill="#22243A"/>')
    out.append("".join(pil))
    out.append(f'<polyline points="{P([(near_end[0], near_end[1] - 7), (far_end[0], far_end[1] - 3)])}" stroke="#3A3C58" stroke-width="2" fill="none"/>')
    # pavilion at the end
    px, py = far_end
    out.append(f'<rect x="{px - 34}" y="{py - 18}" width="56" height="16" fill="#2E3050"/>'
               f'<polygon points="{P([(px - 40, py - 18), (px - 6, py - 32), (px + 28, py - 18)])}" fill="#3A3C5E"/>'
               f'<polygon points="{P([(px - 40, py - 18), (px - 6, py - 32), (px - 6, py - 18)])}" fill="#4A4E74"/>'
               + "".join(f'<rect x="{px - 30 + i * 9}" y="{py - 13}" width="4" height="6" fill="#FFD98E"/>' for i in range(6)))
    for i in range(10):
        t = (i + 0.5) / 10
        x = near_end[0] + (far_end[0] - near_end[0]) * t
        y = near_end[1] + (far_end[1] - near_end[1]) * t
        lh = 16 * (1 - t) + 7 * t
        out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y - lh:.1f}" stroke="#22243A" stroke-width="{1.6 - t:.1f}"/>')
        out.append(glow(x, y - lh, 10 * (1 - t) + 5, "#FFE2A0", f"{u}-pl{i}", 0.9))
        out.append(f'<rect x="{x - 1:.1f}" y="{y + 6:.1f}" width="2" height="{30 * (1 - t) + 10:.1f}" fill="#FFD98E" opacity="0.35"/>')
    # beach: wet sand mirroring the sky, the swash line, dry sand
    out.append(f'<path d="M -10 {H + 66} Q 300 {H + 52} 610 {H + 62} L 610 444 L -10 444 Z" fill="url(#{u}-wet)"/>')
    out.append(f'<path d="M -10 {H + 66} Q 300 {H + 52} 610 {H + 62}" stroke="#F4F2FA" stroke-width="2.4" fill="none" opacity="0.8"/>')
    out.append(f'<path d="M -10 {H + 76} Q 200 {H + 66} 610 {H + 74}" stroke="#E8E4F4" stroke-width="1.4" fill="none" opacity="0.5"/>')
    out.append("".join(f'<rect x="{mx - 14 + rnd.uniform(-10, 10):.1f}" y="{H + 64 + i * 3.2:.1f}" width="{rnd.uniform(8, 30):.1f}" height="1.4" fill="#FFF2D0" opacity="{0.6 - i * 0.03:.2f}"/>' for i in range(16)))
    dry = rough([(-10, 372), (150, 366), (300, 378), (450, 384), (610, 380)], 12, amp=4, depth=3)
    out.append(f'<polygon points="{P(dry + [(610, 444), (-10, 444)])}" fill="url(#{u}-sand)"/>')
    out.append(dots(260, 81, (-10, 372, 610, 444), "#B8B0C8", r=(0.5, 1.3), opacity=(0.3, 0.7)))
    # the light station on the left: keepers' cottages, palms, live oak and the black-white-black tower
    st_base = H + 30
    out.append(f'<path d="M -10 {st_base + 6} Q 120 {st_base - 8} 300 {st_base + 2} Q 330 {st_base + 14} 360 {st_base + 30} L -10 {st_base + 40} Z" fill="#3A3A58"/>')
    out.append(live_oak(34, st_base, 180, 116, 91))
    out.append(keeper_house(206, st_base - 2, 60, 38, wall="#E8E6F0", roof="#3A3C52", trim="#2E3A3A", shade_side=1, chimney=True, lit_win=True, seed=2))
    out.append(keeper_house(280, st_base + 2, 40, 28, wall="#DCDAE8", roof="#3A3C52", shade_side=1, chimney=False, lit_win=True, seed=5))
    # beams sweeping from the lantern
    lx, ly = 150, st_base - 172 - 14
    out.append(f'<polygon points="{P([(lx, ly - 3), (610, ly - 40), (610, ly + 30), (lx, ly + 3)])}" fill="url(#{u}-beam)"/>')
    out.append(f'<polygon points="{P([(lx, ly - 3), (-10, ly - 26), (-10, ly + 14), (lx, ly + 3)])}" fill="url(#{u}-beamL)"/>')
    out.append(lighthouse_tower(f"{u}-lh", 150, st_base, 172, 30, 19, pattern="tybee", light_from=1, lit=True, body="#F2F0F4", dark="#16161E", windows=4))
    for x, h, sd in ((104, 96, 3), (300, 84, 4), (330, 110, 5), (60, 120, 6)):
        out.append(cabbage_palm(x, st_base + 4, h, color="#1A2036", rim="#8A9AC0", seed=sd, lean=0.03))
    out.append(grass(120, 92, (-10, st_base - 4, 360, st_base + 30), ["#3A4460", "#4A5470", "#2A3048", "#6A6A90"], h=(6, 16), sw=1.4))
    # dune in the foreground left with sea oats and a crossover boardwalk
    dn = [(-10, 380), (40, 364), (120, 360), (190, 374), (230, 400), (250, 444), (-10, 444)]
    out.append(f'<polygon points="{P(dn)}" fill="#3E3A58"/>')
    out.append(f'<path d="M 120 360 Q 190 370 230 400 L 250 444 L 200 444 Q 180 400 120 372 Z" fill="#2E2A46" opacity="0.6"/>')
    # dune crossover boardwalk ramping up over the dune toward the beach
    A, B = (-10, 432), (150, 370)
    dw = 14
    deck = [(A[0], A[1]), (B[0], B[1]), (B[0] + 6, B[1] + dw * 0.5), (A[0] + 6, A[1] + dw)]
    out.append(f'<polygon points="{P([(A[0], A[1] + dw), (B[0] + 6, B[1] + dw * 0.5), (B[0] + 6, B[1] + dw * 0.5 + 6), (A[0], A[1] + dw + 8)])}" fill="#2A2438"/>')
    out.append(f'<polygon points="{P(deck)}" fill="#8A7A8E"/>')
    out.append('<g stroke="#5A4E62" stroke-width="1.2">' + "".join(
        f'<line x1="{A[0] + (B[0] - A[0]) * t:.1f}" y1="{A[1] + (B[1] - A[1]) * t:.1f}" x2="{A[0] + 6 + (B[0] - A[0]) * t:.1f}" y2="{A[1] + dw + (B[1] + dw * 0.5 - A[1] - dw) * t:.1f}"/>' for t in [i / 26 for i in range(27)]) + "</g>")
    for side, off in ((0, 0), (1, 1)):
        pts = []
        for t in [i / 6 for i in range(7)]:
            bx_ = A[0] + 6 * off + (B[0] - A[0]) * t
            by_ = A[1] + dw * off + (B[1] + dw * 0.5 * off - A[1] - dw * off) * t
            ph = 20 - 8 * t
            out.append(f'<line x1="{bx_:.1f}" y1="{by_:.1f}" x2="{bx_:.1f}" y2="{by_ - ph:.1f}" stroke="{"#A898AC" if off else "#6A5E74"}" stroke-width="{2.4 - 0.8 * t:.1f}"/>')
            pts.append((bx_, by_ - ph))
        out.append(f'<polyline points="{P(pts)}" fill="none" stroke="{"#B8A8BC" if off else "#6A5E74"}" stroke-width="2.4"/>')
    for x, yb, h, sd in ((20, 446, 110, 1), (150, 380, 70, 2), (176, 392, 80, 3), (210, 420, 100, 4), (130, 368, 56, 5), (232, 446, 120, 6)):
        out.append(sea_oats(x, yb, h, sd, stem="#5A5470", seed_col="#9A8AA8", rim="#E8E0F4", lean=0.12))
    out.append(grass(80, 93, (-10, 366, 240, 444), ["#4A4868", "#5A5478", "#34304C"], h=(8, 18), sw=1.5))
    # footprints toward the water and a ghost crab out for the evening
    fp = random.Random(94)
    out.append("".join(f'<ellipse cx="{300 + 120 * t + (5 if i % 2 else -5):.1f}" cy="{440 - 70 * t:.1f}" rx="{3.4 - 1.6 * t:.1f}" ry="{1.8 - 0.8 * t:.1f}" fill="#3A3452" opacity="0.6"/>'
                       for i, t in enumerate([j / 13 for j in range(14)])))
    out.append(F.couple(306, H + 74, 30, palette={"top": "#3A4A6E", "season": "summer"}, seed=631, rim="#FFF2D0", light=1, tint=("#2A2848", 0.2), gap=40))
    out.append(f'<g opacity="0.3"><rect x="296" y="{H + 76}" width="8" height="14" fill="#3A4A6E"/><rect x="308" y="{H + 76}" width="8" height="12" fill="#8A4A6A"/></g>')
    out.append(ghost_crab(470, 418, 1.0))
    out.append(f'<ellipse cx="470" cy="426" rx="14" ry="2.5" fill="#2A2640" opacity="0.5"/>')
    out.append(gulls([(330, 150, 6), (346, 160, 5)], "#1A2238", 1.8))
    return "\n".join(out)


# ---------------------------------------------------------------- Florida Keys (the old arched railway viaduct over the shallows)
def pelican(x, y, s=1.0, flip=False):
    """Brown pelican perched, facing left: grey-brown body, white head and neck with a yellow crown,
    long bill with the pouch tucked, dark webbed feet. (x, y) = feet."""
    sc = -s if flip else s
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({sc:.2f} {s:.2f})">'
            '<path d="M -6 0 L -10 4 M -6 0 L -2 4 M 6 0 L 2 4 M 6 0 L 10 4" stroke="#2A2420" stroke-width="2.4" stroke-linecap="round"/>'
            '<path d="M -4 -14 L -6 0 M 6 -14 L 6 0" stroke="#3A322C" stroke-width="3"/>'
            # body and folded wing
            '<path d="M -18 -40 Q -26 -60 -8 -66 Q 14 -70 26 -54 Q 40 -36 48 -18 Q 30 -14 14 -12 Q -10 -10 -16 -24 Z" fill="#7A746E"/>'
            '<path d="M -6 -58 Q 14 -66 26 -54 Q 38 -38 48 -18 Q 30 -24 18 -30 Q 2 -40 -6 -58 Z" fill="#5A5048"/>'
            '<g stroke="#B8AEA2" stroke-width="1.4" fill="none" opacity="0.8"><path d="M 2 -52 q 12 8 20 22"/><path d="M 10 -56 q 12 10 18 24"/><path d="M 18 -50 q 10 10 14 22"/></g>'
            '<path d="M 26 -54 Q 40 -36 48 -18" stroke="#2A2420" stroke-width="2" fill="none"/>'
            '<path d="M -16 -24 Q -10 -10 14 -12 Q 4 -18 -6 -18 Z" fill="#4A403A"/>'
            # neck (dark chestnut stripe on the back of the neck in breeding plumage, white front)
            '<path d="M -14 -60 Q -22 -76 -14 -92 Q -8 -102 -2 -98 Q -6 -86 -4 -74 Q -2 -64 -6 -58 Z" fill="#F4EEE4"/>'
            '<path d="M -4 -98 Q -6 -86 -4 -74 Q -2 -64 -6 -58 L -2 -60 Q 2 -70 0 -82 Q 0 -94 -2 -98 Z" fill="#6A3A2A"/>'
            # head, crown, eye, bill and pouch
            '<ellipse cx="-8" cy="-100" rx="9" ry="7" fill="#F4EEE4"/><path d="M -14 -104 Q -8 -110 0 -104 Q -6 -104 -12 -101 Z" fill="#F2D060"/>'
            '<circle cx="-11" cy="-101" r="1.6" fill="#1A1A1A"/><circle cx="-11" cy="-101" r="2.6" fill="none" stroke="#E8A0A0" stroke-width="0.8"/>'
            '<path d="M -14 -102 L -58 -86 L -56 -82 L -14 -96 Z" fill="#B8A890"/>'
            '<path d="M -14 -96 L -56 -82 Q -40 -76 -16 -88 Z" fill="#6A6058"/>'
            '<path d="M -58 -86 Q -62 -84 -58 -80 L -56 -82 Z" fill="#D88A4A"/>'
            '<path d="M -14 -102 L -58 -86" stroke="#E8D8B8" stroke-width="1.2"/>'
            '</g>')


def flats_skiff(x, y, s=1.0):
    """Flats skiff with a guide poling from the platform and an angler casting from the bow."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.2f})">'
            '<path d="M -40 -4 L 42 -6 Q 48 -6 50 -2 L 44 4 L -38 4 Z" fill="#F4F2EC"/><path d="M -38 2 L 44 2 L 42 4 L -38 4 Z" fill="#5A8AA8"/>'
            '<path d="M -36 -4 L -36 -16 M -24 -4 L -24 -16 M -38 -16 L -22 -16" stroke="#C8CCD0" stroke-width="1.8"/>'
            # guide on the poling platform
            '<line x1="-46" y1="10" x2="-14" y2="-62" stroke="#3A3A3A" stroke-width="1.4"/>'
            + F.person(-31, -16, 31, "stand_side", 1, {"top": "#E8E4D8", "top_kind": "long", "bottom": "#4A5A6A", "bottom_kind": "trousers", "hat_kind": "cap", "hat": "#E8E0C8", "form": "m", "skin": "#C88A60"}, seed=651, shadow=0, rim="#FFF4D8", light=1)
            # angler at the bow
            + F.person(28, -4, 30, "point", 1, {"top": "#5A8AC8", "top_kind": "long", "bottom": "#E8E4D8", "bottom_kind": "shorts", "hat_kind": "sunhat", "hat": "#E8E0C8", "form": "m", "skin": "#C88A60"}, seed=652, shadow=0, rim="#FFF4D8", light=1) +
            '<path d="M 35 -30 L 50 -48" stroke="#2A2A2A" stroke-width="1.2"/><path d="M 50 -48 Q 62 -40 68 -5" stroke="#FFFFFF" stroke-width="0.9" fill="none" opacity="0.8"/>'
            '</g>')


def keys():
    u = "flkeys"
    C = Cam(f=380, cx=372, vpy=254, eye=4.0)
    H = 254
    out = [defs(
        lg(f"{u}-sky", [(0, "#2E7CC0"), (0.5, "#5EA8DA"), (0.85, "#A8D6EC"), (1, "#D2ECF2")], 0, 40, 0, H, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#2E7EA8"), (0.12, "#2E9EB8"), (0.35, "#38C2C4"), (0.7, "#7CDCCC"), (1, "#B4ECD8")], 0, H, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-conc", [(0, "#F2E6CE"), (1, "#D8C6A8")]),
        lg(f"{u}-back", [(0, "#A89A88"), (1, "#8A7C6E")]),
        lg(f"{u}-cbase", [(0, "#6ACAC4"), (1, "#E8F4F0")]),
    )]
    out.append(f'<rect width="600" height="{H + 1}" fill="url(#{u}-sky)"/>')
    # towering cumulus over the Gulf, bases tinted turquoise by the shallows below
    for cx, cy, w, h_, sd in ((120, H - 8, 240, 90, 1), (470, H - 6, 220, 70, 2), (300, H - 4, 160, 40, 3)):
        out.append(cloud_puffs(cx, cy - h_ * 0.35, w, h_, sd, "#EEF4F8", "#FFFFFF", shade="#B4C8DC", n=40, lit_dx=0.3, lit_dy=-0.35))
        out.append(f'<ellipse cx="{cx}" cy="{cy - h_ * 0.12:.1f}" rx="{w * 0.48:.1f}" ry="{h_ * 0.12:.1f}" fill="#9ADCD8" opacity="0.55"/>')
    out.append(cloud_puffs(560, 110, 120, 30, 4, "#EEF4F8", "#FFFFFF", shade="#B4C8DC", n=18))
    out.append(cloud_puffs(240, 92, 90, 22, 5, "#EEF4F8", "#FFFFFF", shade="#B4C8DC", n=14))
    out.append(f'<rect x="0" y="{H - 6}" width="600" height="8" fill="#D2ECF2" opacity="0.7"/>')
    # sea: deep channel blue at the horizon to clear turquoise and sand-bottom aqua close in
    out.append(f'<rect x="0" y="{H}" width="600" height="{444 - H}" fill="url(#{u}-sea)"/>')
    # seagrass beds and sandy patches seen through the clear water
    out.append(blobs(30, 11, (0, H + 30, 600, 340), ["#2E8A8A", "#3A9A8A"], r=(14, 40), opacity=(0.25, 0.45), squash=0.2))
    out.append(blobs(26, 12, (0, 330, 600, 444), ["#4AA08A", "#5AA88A", "#3A8A7A"], r=(20, 60), opacity=(0.25, 0.4), squash=0.25))
    out.append(blobs(18, 13, (0, 330, 600, 444), ["#CFF4E4", "#E2F8EC"], r=(16, 50), opacity=(0.3, 0.5), squash=0.25))
    # sunlight caustics in the shallows
    rc = random.Random(14)
    caus = []
    for _ in range(140):
        y = rc.uniform(300, 444)
        k = (y - 300) / 144
        x = rc.uniform(-10, 610)
        w = rc.uniform(8, 22) * (0.5 + k)
        caus.append(f'<path d="M {x:.1f} {y:.1f} q {w / 2:.1f} {-2 - 2 * k:.1f} {w:.1f} 0" stroke-width="{0.9 + 1.2 * k:.1f}" opacity="{rc.uniform(0.3, 0.7):.2f}"/>')
    out.append('<g fill="none" stroke="#F4FFFA" stroke-linecap="round">' + "".join(caus) + "</g>")
    out.append(ripples(70, 15, (0, H + 2, 600, 300), ["#E8F8F8", "#FFFFFF", "#2A7AA0"], w=(8, 30), h=1.2, opacity=(0.3, 0.7)))
    # far mangrove keys on the horizon
    for x0, x1, sd in ((450, 560, 1), (580, 640, 2), (10, 70, 3)):
        line = rough([(x0, H), (x0 + 10, H - 7), ((x0 + x1) / 2, H - 10), (x1 - 10, H - 6), (x1, H)], sd, amp=3, depth=3)
        out.append(f'<polygon points="{P(line)}" fill="#3E7A5E"/>')
    # the viaduct: back face, arch barrels in shadow, then the sunlit front face with arch openings cut out
    X, Xb = -7.0, -10.2
    span, pier, spring, deck0, deck1 = 14.0, 2.4, 1.6, 7.0, 8.2
    z = 3.0
    spans = []
    while z < 520:
        spans.append(z)
        z += span
    def opening(Xp, z0, mirror=1):
        zc = z0 + span / 2
        r = (span - 2 * pier) / 2
        pts = [C(Xp, 0 * mirror, z0 + pier), C(Xp, spring * mirror, z0 + pier)]
        for j in range(1, 16):
            a = math.pi - math.pi * j / 16
            pts.append(C(Xp, (spring + r * math.sin(a)) * mirror, zc + r * math.cos(a)))
        pts += [C(Xp, spring * mirror, z0 + span - pier), C(Xp, 0 * mirror, z0 + span - pier)]
        return pts
    def wall_path(Xp, mirror=1):
        zA, zB = spans[0], spans[-1] + span
        outer = [C(Xp, 0, zA), C(Xp, deck1 * mirror, zA), C(Xp, deck1 * mirror, zB), C(Xp, 0, zB)]
        d = "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in outer) + " Z "
        for z0 in spans:
            d += "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in opening(Xp, z0, mirror)) + " Z "
        return d
    # reflection of the viaduct in the calm water (drawn first, softly)
    out.append(f'<clipPath id="{u}-rc">' + "".join(f'<rect x="0" y="{y:.1f}" width="600" height="{2 + (y - H) * 0.03:.1f}"/>' for y in [H + 2 + i * (3 + i * 0.12) for i in range(48)] if y < 444) + "</clipPath>")
    out.append(f'<path d="{wall_path(X, -1)}" fill="#E8DCC4" fill-rule="evenodd" opacity="0.26" clip-path="url(#{u}-rc)"/>')
    out.append(ripples(60, 16, (0, H + 4, 380, 444), ["#7CDCCC", "#B4ECD8"], w=(20, 60), h=2, opacity=(0.4, 0.8)))
    out.append(f'<path d="{wall_path(Xb)}" fill="url(#{u}-back)" fill-rule="evenodd"/>')
    bar = []
    for z0 in spans:
        f_, b_ = opening(X, z0), opening(Xb, z0)
        for i in range(len(f_) - 1):
            q = [f_[i], f_[i + 1], b_[i + 1], b_[i]]
            area = sum(q[k][0] * q[(k + 1) % 4][1] - q[(k + 1) % 4][0] * q[k][1] for k in range(4))
            if area <= 0:
                continue
            shade = "#9A8A78" if i > len(f_) - 4 else "#8A7A6A"
            bar.append(f'<polygon points="{P(q)}" fill="{shade}" stroke="{shade}" stroke-width="0.6"/>')
    out.append("".join(bar))
    out.append(f'<clipPath id="{u}-fw"><path d="{wall_path(X)}" clip-rule="evenodd"/></clipPath>')
    out.append(f'<path d="{wall_path(X)}" fill="url(#{u}-conc)" fill-rule="evenodd"/>')
    # weathering on the sunlit face: rust streaks, waterline algae, deck shadow
    wz = []
    rw = random.Random(17)
    for z0 in spans[:18]:
        for k in range(3):
            zz = z0 + rw.uniform(0, span)
            top = C(X, deck0, zz)
            bot = C(X, rw.uniform(2, 5), zz)
            wz.append(f'<line x1="{top[0]:.1f}" y1="{top[1]:.1f}" x2="{bot[0]:.1f}" y2="{bot[1]:.1f}" stroke="{rw.choice(["#B89A7A", "#A88A6A", "#C8B090"])}" stroke-width="{max(0.6, 300 / zz * 0.12):.1f}" opacity="0.6"/>')
    wl = [C(X, 0, spans[0]), C(X, 0.9, spans[0]), C(X, 0.9, spans[-1] + span), C(X, 0, spans[-1] + span)]
    dk = [C(X, deck0 - 0.1, spans[0]), C(X, deck0 - 0.6, spans[0]), C(X, deck0 - 0.6, spans[-1] + span), C(X, deck0 - 0.1, spans[-1] + span)]
    out.append(f'<g clip-path="url(#{u}-fw)">' + "".join(wz) + f'<polygon points="{P(wl)}" fill="#5A7A5A" opacity="0.6"/>'
               f'<polygon points="{P(dk)}" fill="#8A7A6A" opacity="0.35"/></g>')
    # deck fascia, railing and posts
    fas = [C(X, deck0, spans[0]), C(X, deck1, spans[0]), C(X, deck1, spans[-1] + span), C(X, deck0, spans[-1] + span)]
    out.append(f'<polygon points="{P(fas)}" fill="#FFF6E2"/>')
    out.append(f'<polyline points="{P([C(X, deck0, spans[0]), C(X, deck0, spans[-1] + span)])}" stroke="#7A6A5A" stroke-width="1.4" fill="none" opacity="0.6"/>')
    rail = [C(X, deck1 + 1.0, spans[0]), C(X, deck1 + 1.0, spans[-1] + span)]
    out.append(f'<polyline points="{P(rail)}" stroke="#E8DCC4" stroke-width="2" fill="none"/>')
    pz = spans[0]
    posts = []
    while pz < spans[-1] + span:
        a_, b_ = C(X, deck1, pz), C(X, deck1 + 1.0, pz)
        posts.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#E8DCC4" stroke-width="{max(0.6, 380 * 0.18 / pz):.1f}"/>')
        pz += 3.5
    out.append("".join(posts))
    # the far bridge continuing to the horizon as a thin line
    a_, b_ = C(X, deck1, spans[-1] + span), C(X, deck1, 4000)
    out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#E8DCC4" stroke-width="1.4"/>')
    # a red mangrove islet in the middle distance with prop roots
    mx0, mx1, my = 452, 560, 284
    mid_ = (mx0 + mx1) / 2
    out.append(f'<g stroke="#4A3A2A" stroke-width="1.6" fill="none">' + "".join(
        f'<path d="M {x} {my - 10} q {(x - mid_) * 0.12:.1f} 2 {(x - mid_) * 0.2:.1f} 12"/>' for x in range(mx0 + 4, mx1 - 2, 6)) + "</g>")
    rm = random.Random(18)
    out.append("".join(f'<circle cx="{rm.uniform(mx0, mx1):.1f}" cy="{my - 10 - rm.uniform(0, 12) * math.sin(math.pi * 0.5):.1f}" r="{rm.uniform(6, 12):.1f}" fill="{rm.choice(["#2E5A3A", "#3A6A42", "#2A4E34"])}"/>' for _ in range(26)))
    out.append("".join(f'<circle cx="{rm.uniform(mx0 + 4, mx1 - 4):.1f}" cy="{my - 18 - rm.uniform(0, 8):.1f}" r="{rm.uniform(3, 6):.1f}" fill="#7AAA5A" opacity="0.7"/>' for _ in range(14)))
    out.append(f'<ellipse cx="{(mx0 + mx1) / 2}" cy="{my + 3}" rx="{(mx1 - mx0) / 2 + 6}" ry="3" fill="#2E6A5A" opacity="0.35"/>')
    # flats skiff poling along the edge of the channel
    out.append(f'<ellipse cx="350" cy="324" rx="70" ry="5" fill="#1E6A7A" opacity="0.25"/>')
    out.append(flats_skiff(350, 318, 1.3))
    out.append(f'<path d="M 294 324 q 50 6 110 0" stroke="#FFFFFF" stroke-width="1.8" fill="none" opacity="0.7"/>'
               f'<path d="M 288 320 q -30 2 -56 8 M 290 326 q -26 6 -48 14" stroke="#FFFFFF" stroke-width="1.3" fill="none" opacity="0.5"/>')
    # the pelican on an old piling in the foreground
    out.append(f'<rect x="488" y="352" width="22" height="100" fill="#7A6450"/><rect x="498" y="352" width="12" height="100" fill="#5A4A3A"/>'
               f'<ellipse cx="499" cy="352" rx="11" ry="3.5" fill="#A88E72"/><rect x="488" y="410" width="22" height="34" fill="#4A6A5A" opacity="0.5"/>')
    out.append('<g stroke="#4A3A2E" stroke-width="1" opacity="0.6">' + "".join(f'<line x1="490" y1="{y}" x2="496" y2="{y + 3}"/>' for y in range(362, 410, 9)) + "</g>")
    out.append(f'<path d="M 470 444 q 30 -6 58 0" stroke="#FFFFFF" stroke-width="1.6" fill="none" opacity="0.6"/>')
    out.append(pelican(504, 352, 0.82))
    # mangrove leaves reaching into the bottom right corner
    for k in range(18):
        r2 = random.Random(300 + k)
        lx_, ly_ = r2.uniform(540, 620), r2.uniform(380, 450)
        a = r2.uniform(-60, 60)
        out.append(f'<ellipse cx="{lx_:.1f}" cy="{ly_:.1f}" rx="14" ry="6" fill="{r2.choice(["#2E5A3A", "#3A6A42", "#4A7A4A"])}" transform="rotate({a:.0f} {lx_:.1f} {ly_:.1f})"/>')
    out.append(gulls([(330, 140, 7), (352, 150, 5), (200, 170, 6)], "#2A3A4A", 1.8))
    return "\n".join(out)


BUILD = {
    "cape-canaveral": (canaveral, "CAPE CANAVERAL", "FLORIDA · SPACE COAST", "#1A2042", "#FFB878", "#FBEBD4", "#F7C49A"),
    "key-west": (key_west, "KEY WEST", "FLORIDA · SOUTHERNMOST CITY", "#24183A", "#F6984E", "#FBEBD4", "#FFC078"),
    "maine-coast": (maine, "MAINE COAST", "MAINE · USA", "#1A2E44", "#E8C6B4", "#FBEBD4", "#A8C8E2"),
    "cape-cod": (cape_cod, "CAPE COD", "MASSACHUSETTS · USA", "#2E3A4E", "#F2C890", "#FBEBD4", "#F2D49A"),
    "outer-banks": (outer_banks, "OUTER BANKS", "NORTH CAROLINA · USA", "#232A38", "#F2D49A", "#FBEBD4", "#E8C890"),
    "tybee-island": (tybee, "TYBEE ISLAND", "GEORGIA · USA", "#141E36", "#E8B0B8", "#FBEBD4", "#C8C8E8"),
    "florida-keys": (keys, "FLORIDA KEYS", "FLORIDA · OVERSEAS HIGHWAY", "#123A4A", "#5CD0C8", "#FBEBD4", "#8EE0D4"),
    "niagara-falls": (niagara, "NIAGARA FALLS", "NEW YORK · USA", "#16323A", "#7FC4AC", "#FBEBD4", "#9FD8C4"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("places", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
