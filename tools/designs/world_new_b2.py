"""World Places, painted edition — batch B2: Istanbul, Marrakech, Petra, Dubai, Cape Town, Mykonos.
Same travel-poster idiom as world_painted.py: a real viewpoint, a time of day and light direction, graded skies,
atmospheric depth and small storytelling details."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from world_painted import (defs, Q, mix, lerp, cumulus, streak_cloud, gulls, figure, leaf_canopy, water_lines, camel,
                           camel_shadow)
from places_painted import Cam
from poster import ANTON, poster


def ell_arc(cx, cy, rx, ry, a0, a1, n=24):
    """Points along an ellipse from angle a0 to a1 (degrees, 0 = right, -90 = top)."""
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def dome(cx, base, rx, ry, fill, rim=None, rim_w=1.6, finial=None, rim_side=1):
    """Half-ellipse dome standing on base; rim light along the sun side; optional finial colour."""
    pts = ell_arc(cx, base, rx, ry, 180, 360)
    out = [Q(pts, fill)]
    if rim:
        a0, a1 = (285, 352) if rim_side > 0 else (188, 255)
        out.append(f'<polyline points="{P(ell_arc(cx, base, rx, ry, a0, a1, 12))}" fill="none" stroke="{rim}" stroke-width="{rim_w}" stroke-linecap="round"/>')
    if finial:
        h = max(4, ry * 0.32)
        out.append(f'<line x1="{cx:.1f}" y1="{base - ry:.1f}" x2="{cx:.1f}" y2="{base - ry - h:.1f}" stroke="{finial}" stroke-width="{max(1, rx * 0.05):.1f}"/>'
                   f'<circle cx="{cx:.1f}" cy="{base - ry - h * 0.55:.1f}" r="{max(0.9, rx * 0.06):.1f}" fill="{finial}"/>')
    return "".join(out)


def minaret(x, base, h, w, fill, rim=None, balconies=3, cap=None, rim_side=1):
    """Ottoman pencil minaret: slim shaft, 1-3 serefe balconies, tall conical lead cap, finial."""
    cap = cap or h * 0.17
    shaft_top = base - h + cap
    out = [f'<rect x="{x - w / 2:.1f}" y="{shaft_top:.1f}" width="{w:.1f}" height="{h - cap:.1f}" fill="{fill}"/>',
           f'<rect x="{x - w * 0.75:.1f}" y="{base - h * 0.16:.1f}" width="{w * 1.5:.1f}" height="{h * 0.16:.1f}" fill="{fill}"/>',
           Q([(x - w * 0.62, shaft_top + 0.5), (x, base - h), (x + w * 0.62, shaft_top + 0.5)], fill)]
    for i in range(balconies):
        y = shaft_top + (h - cap) * (0.08 + 0.22 * i)
        out.append(f'<rect x="{x - w * 1.05:.1f}" y="{y:.1f}" width="{w * 2.1:.1f}" height="{max(1.6, w * 0.45):.1f}" fill="{fill}"/>'
                   f'<path d="M {x - w * 1.05:.1f} {y + max(1.6, w * 0.45):.1f} L {x - w / 2:.1f} {y + w * 1.3:.1f} L {x + w / 2:.1f} {y + w * 1.3:.1f} L {x + w * 1.05:.1f} {y + max(1.6, w * 0.45):.1f} Z" fill="{fill}"/>')
    tip = base - h
    out.append(f'<line x1="{x:.1f}" y1="{tip:.1f}" x2="{x:.1f}" y2="{tip - w * 1.4:.1f}" stroke="{rim or fill}" stroke-width="1.2"/>')
    if rim:
        s = rim_side
        out.append(f'<line x1="{x + s * w / 2:.1f}" y1="{shaft_top + 1:.1f}" x2="{x + s * w / 2:.1f}" y2="{base - h * 0.16:.1f}" stroke="{rim}" stroke-width="1.2" opacity="0.85"/>'
                   f'<line x1="{x + s * w * 0.6:.1f}" y1="{shaft_top:.1f}" x2="{x:.1f}" y2="{base - h:.1f}" stroke="{rim}" stroke-width="1.3" opacity="0.9"/>')
    return "".join(out)


def cypress(x, base, h, w, fill, rim=None, seed=0):
    """Mediterranean cypress: a tall flame of foliage with ragged edges."""
    rnd = random.Random(seed)
    L, R = [], []
    n = 10
    for i in range(n + 1):
        t = i / n
        y = base - h * t
        ww = w * (math.sin(math.pi * min(1, 0.15 + t * 0.95)) ** 0.7) * (1 - t * 0.45) * rnd.uniform(0.85, 1.12)
        L.append((x - ww / 2, y))
        R.append((x + ww / 2 * rnd.uniform(0.85, 1.1), y))
    pts = L + [(x + w * 0.04, base - h - 3)] + R[::-1]
    out = Q(pts, fill)
    if rim:
        out += f'<polyline points="{P(R[2:])}" fill="none" stroke="{rim}" stroke-width="1.3" opacity="0.75"/>'
    return out


def gull(x, y, s, flip=False, body="#F6F2EE", under="#E2DCE4", trail="#A8A0B8", tip="#2A2430", rim="#FFD9A0"):
    """Yellow-legged gull gliding with wings raised in a shallow V, seen slightly from below; ~s*150 px span."""
    sx = -s if flip else s
    far = [(-4, -3), (-14, -14), (-30, -23), (-48, -22), (-66, -15), (-50, -13), (-30, -12), (-12, -1)]
    near = [(4, -2), (16, -17), (36, -28), (58, -27), (82, -18), (60, -15), (38, -14), (14, 2)]
    g = [f'<g transform="translate({x:.1f} {y:.1f}) scale({sx:.3f} {s:.3f})">',
         Q(far, trail), Q(far[:6] + [(-30, -15), (-12, -3)], under),
         Q([(-48, -22), (-66, -15), (-50, -13)], tip),
         '<path d="M -20 -2 Q -10 -8 6 -7 Q 20 -6 28 -2 L 36 -5 L 34 2 L 28 2 Q 10 7 -10 5 Q -20 4 -20 -2 Z" fill="' + body + '"/>',
         f'<path d="M -18 2 Q 0 7 28 2 Q 10 7 -10 5 Z" fill="{trail}" opacity="0.6"/>',
         f'<circle cx="-20" cy="-4" r="5.4" fill="{body}"/><path d="M -25 -4 L -33 -2.4 L -25 -1.4 Z" fill="#F2B640"/>',
         f'<circle cx="-21.5" cy="-5.5" r="1.1" fill="{tip}"/>',
         Q(near, trail), Q(near[:6] + [(38, -18), (14, -1)], under),
         Q([(58, -27), (82, -18), (60, -15)], tip), f'<circle cx="70" cy="-19" r="1.4" fill="#FFFFFF"/>',
         f'<polyline points="{P(near[:5])}" fill="none" stroke="{rim}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>',
         f'<polyline points="{P(far[:5])}" fill="none" stroke="{rim}" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round" opacity="0.8"/>',
         f'<path d="M -24 -8 Q -14 -10 0 -7" fill="none" stroke="{rim}" stroke-width="1.4" stroke-linecap="round"/>',
         '<path d="M 22 2 L 30 6 M 24 1 L 31 4" stroke="#E8A0A0" stroke-width="1.3" stroke-linecap="round"/>',
         "</g>"]
    return "".join(g)


def perched_gull(x, base, s, rim="#FFD9A0", flip=False):
    """Gull standing on a rail, facing left (flip faces right)."""
    sx = -s if flip else s
    return (f'<g transform="translate({x:.1f} {base:.1f}) scale({sx:.3f} {s:.3f})">'
            '<path d="M -4 -2 L -6 -14 M 6 -2 L 4 -14" stroke="#E89A8A" stroke-width="2.4" stroke-linecap="round"/>'
            '<path d="M -8 -2 L -1 -2 M 2 -2 L 9 -2" stroke="#E89A8A" stroke-width="2" stroke-linecap="round"/>'
            '<path d="M -16 -26 Q -18 -38 -8 -42 Q 6 -44 18 -36 L 40 -30 L 30 -24 Q 14 -12 -2 -14 Q -14 -16 -16 -26 Z" fill="#F6F2EE"/>'
            '<path d="M -6 -38 Q 10 -42 22 -34 L 42 -29 L 30 -25 Q 16 -22 2 -26 Q -6 -30 -6 -38 Z" fill="#A8A6B4"/>'
            '<path d="M 26 -32 L 44 -28 L 34 -24 Z" fill="#2A2430"/><circle cx="36" cy="-28" r="1.2" fill="#FFFFFF"/>'
            '<path d="M -14 -24 Q -4 -12 10 -16 Q -2 -16 -12 -22 Z" fill="#C8BCC8" opacity="0.8"/>'
            '<path d="M -10 -40 Q -12 -54 -22 -56 Q -32 -56 -34 -48 Q -34 -42 -26 -40 Q -18 -38 -16 -30 Z" fill="#F6F2EE"/>'
            '<path d="M -33 -50 L -46 -48 L -46 -46 L -33 -45 Z" fill="#F2B640"/><circle cx="-41" cy="-46.4" r="1" fill="#D8423A"/>'
            '<circle cx="-27" cy="-50" r="1.6" fill="#2A2430"/><circle cx="-26.5" cy="-50.5" r="0.5" fill="#FFFFFF"/>'
            f'<path d="M -22 -56 Q -10 -54 -10 -40 Q -8 -34 4 -40 Q 18 -42 30 -34" fill="none" stroke="{rim}" stroke-width="2" stroke-linecap="round"/>'
            '</g>')


# ================================================================ ISTANBUL — the old city across the Bosphorus at sunset
def ottoman_mosque(cx, base, k, u, body, dome_c, rim, lit="#FFC86A"):
    """Sultan Ahmed-style imperial mosque seen from the Asian shore, backlit: cascading semi-domes around the
    central dome, corner weight-towers, courtyard arcade of small domes to the left and six minarets."""
    out = []
    # courtyard arcade (left) with a row of small domes
    out.append(f'<rect x="{cx - 160 * k:.1f}" y="{base - 16 * k:.1f}" width="{90 * k:.1f}" height="{16 * k:.1f}" fill="{body}"/>')
    for i in range(7):
        out.append(dome(cx - 152 * k + i * 12 * k, base - 16 * k, 5.2 * k, 5 * k, dome_c, rim, 1.0))
    # main prayer hall
    out.append(f'<rect x="{cx - 74 * k:.1f}" y="{base - 30 * k:.1f}" width="{148 * k:.1f}" height="{30 * k:.1f}" fill="{body}"/>')
    # small outer half-domes, then the big semi-domes on each side
    for sx in (-1, 1):
        out.append(dome(cx + sx * 62 * k, base - 30 * k, 12 * k, 10 * k, dome_c, rim, 1.1, finial=rim))
        out.append(dome(cx + sx * 38 * k, base - 30 * k, 24 * k, 19 * k, dome_c, rim, 1.4, finial=rim))
    # drum with windows, and the central dome
    out.append(f'<rect x="{cx - 30 * k:.1f}" y="{base - 44 * k:.1f}" width="{60 * k:.1f}" height="{14 * k:.1f}" fill="{body}"/>')
    out.append("".join(f'<rect x="{cx - 26 * k + i * 6.2 * k:.1f}" y="{base - 41 * k:.1f}" width="{2.2 * k:.1f}" height="{5 * k:.1f}" rx="{1 * k:.1f}" fill="{lit}" opacity="0.75"/>' for i in range(9)))
    out.append(dome(cx, base - 44 * k, 31 * k, 27 * k, dome_c, rim, 2.0, finial=rim))
    # corner weight-towers with little domes
    for sx in (-1, 1):
        tx = cx + sx * 33 * k
        out.append(f'<rect x="{tx - 4 * k:.1f}" y="{base - 52 * k:.1f}" width="{8 * k:.1f}" height="{22 * k:.1f}" fill="{body}"/>')
        out.append(dome(tx, base - 52 * k, 5 * k, 5 * k, dome_c, rim, 1.0, finial=rim))
    # six minarets: four around the hall (three balconies) and two at the far courtyard corners (two)
    for dx, h, b in ((-80, 118, 3), (80, 118, 3), (-150, 104, 2), (-168, 104, 2)):
        out.append(minaret(cx + dx * k, base - (16 if dx < -100 else 0) * k, h * k, 4.2 * k, body, rim, b))
    # arcade openings with lamps along the base of the hall
    out.append("".join(f'<path d="M {cx - 68 * k + i * 11 * k:.1f} {base:.1f} L {cx - 68 * k + i * 11 * k:.1f} {base - 8 * k:.1f} Q {cx - 65 * k + i * 11 * k:.1f} {base - 12 * k:.1f} {cx - 62 * k + i * 11 * k:.1f} {base - 8 * k:.1f} L {cx - 62 * k + i * 11 * k:.1f} {base:.1f} Z" fill="{lit}" opacity="0.55"/>' for i in range(13)))
    return "".join(out)


def hagia_sophia(cx, base, k, u, body, dome_c, rim, lit="#FFC86A"):
    """The great domed basilica: flatter dome ringed by windows, massive stepped buttresses, four minarets of
    different builds (two slender, two stockier)."""
    out = []
    out.append(Q([(cx - 80 * k, base), (cx - 80 * k, base - 22 * k), (cx - 58 * k, base - 22 * k), (cx - 56 * k, base - 36 * k), (cx - 40 * k, base - 36 * k),
                  (cx - 38 * k, base - 46 * k), (cx + 38 * k, base - 46 * k), (cx + 40 * k, base - 36 * k), (cx + 56 * k, base - 36 * k), (cx + 58 * k, base - 22 * k),
                  (cx + 84 * k, base - 22 * k), (cx + 84 * k, base)], body))
    for sx in (-1, 1):
        out.append(dome(cx + sx * 46 * k, base - 36 * k, 14 * k, 9 * k, dome_c, rim, 1.1))
    out.append(f'<rect x="{cx - 34 * k:.1f}" y="{base - 54 * k:.1f}" width="{68 * k:.1f}" height="{8 * k:.1f}" fill="{body}"/>')
    out.append("".join(f'<rect x="{cx - 31 * k + i * 4.6 * k:.1f}" y="{base - 52.5 * k:.1f}" width="{1.8 * k:.1f}" height="{4.6 * k:.1f}" fill="{lit}" opacity="0.7"/>' for i in range(14)))
    out.append(dome(cx, base - 54 * k, 35 * k, 20 * k, dome_c, rim, 2.0, finial=rim))
    # buttress towers on the near side
    for dx in (-36, 36):
        out.append(f'<rect x="{cx + dx * k - 5 * k:.1f}" y="{base - 60 * k:.1f}" width="{10 * k:.1f}" height="{14 * k:.1f}" fill="{body}"/>')
    for dx, h, w, b in ((-92, 96, 5.6, 2), (-74, 90, 4.6, 1), (96, 100, 4.0, 2), (78, 92, 4.4, 1)):
        out.append(minaret(cx + dx * k, base, h * k, w * k, body, rim, b))
    return "".join(out)


def vapur(x, wl, k, flip=False, hull="#22284A", upper="#F2ECE4", glass="#FFD48A", rim="#FFC890"):
    """Istanbul city ferry in profile: dark hull, white superstructure with a band of saloon windows,
    open upper deck under an awning, a tall funnel with a black top."""
    sx = -k if flip else k
    g = [f'<g transform="translate({x:.1f} {wl:.1f}) scale({sx:.3f} {k:.3f})">',
         '<path d="M -62 -4 Q -64 -12 -58 -15 L 58 -15 Q 64 -12 64 -6 Q 0 3 -62 -4 Z" fill="' + hull + '"/>',
         f'<path d="M -58 -15 L -56 -24 L 56 -24 L 58 -15 Z" fill="{upper}"/>',
         '<g fill="#3A3A5A">' + "".join(f'<circle cx="{-48 + i * 8}" cy="-19.5" r="1.4"/>' for i in range(13)) + "</g>",
         f'<path d="M -50 -24 L -48 -36 L 48 -36 L 50 -24 Z" fill="{upper}"/>',
         f'<rect x="-45" y="-33" width="90" height="6" fill="{glass}"/>',
         '<g stroke="#C8B8A8" stroke-width="1.2">' + "".join(f'<line x1="{-45 + i * 7.5}" y1="-33" x2="{-45 + i * 7.5}" y2="-27"/>' for i in range(1, 12)) + "</g>",
         f'<path d="M -44 -36 L -42 -43 L 42 -43 L 44 -36 Z" fill="{upper}" opacity="0.9"/>',
         '<path d="M -46 -44 L 46 -44 L 44 -47 L -44 -47 Z" fill="#B8463E"/>',
         '<g stroke="#5A5060" stroke-width="1">' + "".join(f'<line x1="{-40 + i * 10}" y1="-43" x2="{-40 + i * 10}" y2="-37"/>' for i in range(9)) + "</g>",
         f'<rect x="6" y="-62" width="9" height="16" fill="{upper}"/><rect x="6" y="-62" width="9" height="5" fill="#1E1A22"/>',
         f'<line x1="-30" y1="-47" x2="-30" y2="-60" stroke="#5A5060" stroke-width="1.2"/><path d="M -30 -60 L -21 -57 L -30 -54 Z" fill="#D8303A"/>',
         f'<path d="M -56 -24 L 56 -24" stroke="{rim}" stroke-width="1.2" opacity="0.8"/>',
         f'<path d="M -62 -4 Q -64 -12 -58 -15" stroke="{rim}" stroke-width="1.4" fill="none"/>',
         "</g>"]
    return "".join(g)


def istanbul():
    u = "ist"
    hz = 300
    sunx, suny = 532, 222
    out = [defs(
        lg(f"{u}-sky", [(0, "#2C2A5E"), (0.24, "#58407C"), (0.46, "#A8507A"), (0.64, "#E2726A"), (0.82, "#F5A45C"), (1, "#FCD488")], 0, 0, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#F9C67E"), (0.07, "#E28A6C"), (0.28, "#8E4C7A"), (0.62, "#4A3268"), (1, "#24204A")], 0, hz, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-sil", [(0, "#5A2E5E"), (1, "#3C2248")], 0, 150, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#F0906E", 0), (1, "#F0906E", 0.55)], 0, 230, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-rail", [(0, "#A8683E"), (0.45, "#6E3E2A"), (1, "#3E2220")]),
        lg(f"{u}-dm", [(0, "#8A5684"), (0.5, "#5E3264"), (1, "#4A2652")]),
        lg(f"{u}-deck", [(0, "#3A2436"), (1, "#20142A")]),
    )]
    out.append(f'<rect width="600" height="{hz + 1}" fill="url(#{u}-sky)"/>')
    out.append(dots(26, 3, (0, 40, 600, 120), "#F6EEE0", r=(0.6, 1.2), opacity=(0.3, 0.8)))
    out.append(glow(sunx, suny, 340, "#FFC27A", f"{u}-g1", 0.8))
    out.append(glow(sunx, suny, 80, "#FFF0C4", f"{u}-g2", 0.95))
    out.append(f'<circle cx="{sunx}" cy="{suny}" r="23" fill="#FFF3CE"/>')
    for x, y, w, c in ((120, 96, 120, "#8E4E86"), (60, 112, 70, "#A85A88"), (300, 120, 110, "#C8648A"), (420, 150, 130, "#F08A7A"), (560, 176, 90, "#F8A070"),
                       (360, 196, 80, "#FAB27A"), (200, 168, 100, "#E07A80"), (540, 120, 60, "#D8708A"), (470, 210, 60, "#FFD09A")):
        out.append(streak_cloud(x, y, w, c, 0.7, 4.2))
        out.append(streak_cloud(x + w * 0.15, y + 3, w * 0.55, "#FFE0B8", 0.55, 1.5))
    # far shore of the Golden Horn beyond the peninsula, hazy
    poly, _ = ridge_poly([(-10, 262), (90, 254), (200, 260), (300, 252), (420, 258), (500, 266)], 4, base=hz + 1, amp=3, fill="#9C5C84")
    out.append(poly)
    out.append(dots(60, 5, (0, 254, 460, 270), "#FFD9A0", r=(0.6, 1.1), opacity=(0.4, 0.9)))
    # the historic peninsula: low hills covered with houses
    hill = rough([(-10, 278), (60, 272), (150, 266), (260, 268), (350, 266), (450, 272), (540, 280), (610, 290)], 8, amp=3, depth=3)
    out.append(Q(hill + [(610, hz + 1), (-10, hz + 1)], f"url(#{u}-sil)"))
    rnd = random.Random(11)
    houses = []
    x = -10
    while x < 610:
        w = rnd.uniform(7, 15)
        yb = y_on(hill, x + w / 2) or 290
        h = rnd.uniform(4, 14)
        houses.append(f'<rect x="{x:.1f}" y="{yb - h:.1f}" width="{w:.1f}" height="{hz + 1 - yb + h:.1f}" fill="{rnd.choice(["#4E285A", "#56305E", "#482652"])}"/>')
        if rnd.random() < 0.5:
            houses.append(f'<path d="M {x - 1:.1f} {yb - h:.1f} L {x + w / 2:.1f} {yb - h - 3:.1f} L {x + w + 1:.1f} {yb - h:.1f} Z" fill="#5E3462"/>')
        x += w + rnd.uniform(-1, 2)
    out.append("".join(houses))
    win = []
    for _ in range(200):
        x = rnd.uniform(0, 600)
        yb = y_on(hill, x) or 290
        y = rnd.uniform(yb - 6, hz - 2)
        win.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="1.6" height="1.8" fill="{rnd.choice(["#FFD48A", "#FFC070", "#FFE2A8"])}" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    out.append("".join(win))
    # Topkapi point: cypress groves and palace roofs
    for i in range(12):
        cx_ = 516 + i * 7 + rnd.uniform(-3, 3)
        out.append(cypress(cx_, (y_on(hill, cx_) or 290) + 6, rnd.uniform(18, 34), rnd.uniform(5, 8), "#3A1E44", "#F8A060", seed=i))
    out.append(f'<rect x="80" y="270" width="34" height="12" fill="#4E285A"/><path d="M 78 270 L 97 262 L 116 270 Z" fill="#5A3060"/>')
    out.append(dome(40, 274, 9, 7, f"url(#{u}-dm)", "#FFB070", 1, finial="#FFB070"))
    out.append(minaret(56, 274, 44, 3, "#4A2652", "#FFB46A", 1))
    # Hagia Sophia (right) and the Blue Mosque (left), rim-lit by the sun behind
    out.append(hagia_sophia(458, 274, 0.78, u, "#4E2A56", f"url(#{u}-dm)", "#FFB46A"))
    out.append(ottoman_mosque(286, 270, 1.3, u, "#4A2652", f"url(#{u}-dm)", "#FFB46A"))
    out.append(f'<rect x="0" y="230" width="600" height="{hz + 1 - 230}" fill="url(#{u}-haze)"/>')
    # the sea, sun path and the reflections of the skyline
    out.append(f'<rect x="0" y="{hz}" width="600" height="{444 - hz}" fill="url(#{u}-sea)"/>')
    rnd = random.Random(14)
    for i in range(30):
        y = hz + 1 + i * 1.4
        out.append(f'<rect x="{-10 + rnd.uniform(-6, 6):.1f}" y="{y:.1f}" width="{500 - i * 3 + rnd.uniform(-10, 10):.1f}" height="1" fill="#3A2048" opacity="{0.55 * (1 - i / 30):.2f}"/>')
    for mx_, top in ((286 - 80 * 1.3, 118), (286 + 80 * 1.3, 118), (286 - 150 * 1.3, 104), (286 - 168 * 1.3, 104), (458 - 92 * 0.78, 96), (458 + 96 * 0.78, 100)):
        for j in range(7):
            yy = hz + 4 + j * 7
            out.append(f'<rect x="{mx_ - 1.6 + rnd.uniform(-1.5, 1.5):.1f}" y="{yy:.1f}" width="3.2" height="4" fill="#3A2048" opacity="{0.5 * (1 - j / 7):.2f}"/>')
    for i in range(170):
        y = hz + 1 + rnd.random() ** 1.5 * 143
        kk = (y - hz) / 143
        x = sunx - 6 + rnd.gauss(0, 14 + kk * 70)
        w = rnd.uniform(5, 22) * (0.4 + kk)
        out.append(f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{0.8 + kk * 1.6:.1f}" rx="1" fill="{rnd.choice(["#FFE6B0", "#FFD08A", "#FFF4D8", "#F8B070"])}" opacity="{(1 - kk * 0.5) * rnd.uniform(0.45, 0.95):.2f}"/>')
    out.append(water_lines(110, 15, (0, hz + 6, 600, 444), ["#B8608A", "#5A3A7A", "#E8907A", "#2E2656"], w=(10, 46), h=(0.8, 2.2), opacity=(0.25, 0.6)))
    # a far ferry heading for Eminonu and the near one crossing to Uskudar, wakes behind them
    out.append(f'<path d="M 120 318 Q 150 316 190 318" stroke="#FFE2C0" stroke-width="1.2" fill="none" opacity="0.5"/>')
    out.append(vapur(96, 318, 0.42, flip=True))
    wx, wl = 250, 352
    out.append(f'<path d="M {wx + 80} {wl - 2} Q {wx + 170} {wl + 2} {wx + 280} {wl + 2}" stroke="#FFE6C8" stroke-width="2.4" fill="none" opacity="0.4"/>'
               f'<path d="M {wx + 78} {wl + 1} Q {wx + 150} {wl + 14} {wx + 240} {wl + 26}" stroke="#FFE6C8" stroke-width="1.8" fill="none" opacity="0.4"/>'
               f'<path d="M {wx + 76} {wl - 3} Q {wx + 140} {wl - 8} {wx + 230} {wl - 10}" stroke="#FFE6C8" stroke-width="1.2" fill="none" opacity="0.35"/>')
    out.append(water_lines(24, 16, (wx + 70, wl - 4, wx + 200, wl + 12), ["#FFE6C8", "#F8C8A8"], w=(6, 20), h=(0.8, 1.6), opacity=(0.3, 0.7)))
    out.append(vapur(wx, wl, 1.08))
    out.append(f'<path d="M {wx - 64} {wl + 1} Q {wx} {wl + 6} {wx + 66} {wl + 1}" stroke="#2A2040" stroke-width="2" fill="none" opacity="0.6"/>')
    # a little fishing boat
    out.append(f'<path d="M 470 330 L 500 330 L 496 336 L 474 336 Z" fill="#2A2448"/><rect x="480" y="324" width="8" height="6" fill="#F2ECE4"/><path d="M 470 330 L 500 330" stroke="#FFC890" stroke-width="1"/>')
    out.append(gulls([(318, 214, 10), (338, 226, 7), (120, 196, 9), (440, 178, 8), (230, 140, 7)], "#3A2448", 1.8))
    # flying gulls following our ferry
    out.append(gull(462, 118, 0.55))
    # on deck: the rail of our ferry, a gull eyeing a simit on the rail
    rail = [(-10, 402), (610, 392)]
    out.append(Q([(-10, 410), (610, 400), (610, 444), (-10, 444)], f"url(#{u}-deck)"))
    out.append(Q([(-10, 444), (610, 444), (610, 430), (-10, 436)], "#1A1020"))
    for x in range(-4, 610, 36):
        y = 402 - (x + 10) / 620 * 10
        out.append(f'<rect x="{x:.1f}" y="{y + 6:.1f}" width="6" height="{444 - y:.1f}" fill="#E8DCD0"/><rect x="{x + 3.6:.1f}" y="{y + 6:.1f}" width="2.4" height="{444 - y:.1f}" fill="#A88EA0"/>')
    for yy in (420, 434):
        out.append(f'<line x1="-10" y1="{yy}" x2="610" y2="{yy - 10}" stroke="#D8CCC4" stroke-width="2.2"/>')
    out.append(Q([(-10, 401), (610, 391), (610, 401), (-10, 411)], f"url(#{u}-rail)"))
    out.append(f'<line x1="-10" y1="401" x2="610" y2="391" stroke="#FFC890" stroke-width="2" opacity="0.9"/>')
    out.append(f'<g stroke="#4A2A22" stroke-width="0.8" opacity="0.5">' + "".join(f'<line x1="{x}" y1="{405 - x / 62:.1f}" x2="{x + 40}" y2="{404.5 - (x + 40) / 62:.1f}"/>' for x in range(0, 600, 70)) + "</g>")
    # simit (sesame bread ring) on the rail
    sx_, sy_ = 236, 392
    out.append(f'<ellipse cx="{sx_}" cy="{sy_ + 3}" rx="17" ry="4" fill="#2A1418" opacity="0.4"/>'
               f'<ellipse cx="{sx_}" cy="{sy_}" rx="17" ry="7.5" fill="#B4602E"/><ellipse cx="{sx_}" cy="{sy_ - 1.4}" rx="15" ry="6" fill="#D88A48"/>'
               f'<ellipse cx="{sx_}" cy="{sy_ - 0.6}" rx="7" ry="2.6" fill="#5A2E22"/>'
               + dots(26, 9, (sx_ - 14, sy_ - 6, sx_ + 14, sy_ + 3), "#FFE8B8", r=(0.5, 0.9), opacity=(0.7, 1))
               + f'<path d="M {sx_ + 6} {sy_ - 6} Q {sx_ + 14} {sy_ - 5} {sx_ + 16} {sy_ - 1}" stroke="#FFD49A" stroke-width="1.4" fill="none"/>')
    out.append(perched_gull(148, 400, 0.9, flip=True))
    return "\n".join(out)


# ================================================================ DUBAI — red dunes at sunset, the city on the horizon
def spline(ctrl, step=6):
    """Catmull-Rom curve through control points, sampled every ~step px of x."""
    pts = [ctrl[0]] + list(ctrl) + [ctrl[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        n = max(2, int(abs(p2[0] - p1[0]) / step))
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    out.append(ctrl[-1])
    return out


def bez(p0, p1, p2, p3, n=16):
    return [tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c + t ** 3 * d for a, b, c, d in zip(p0, p1, p2, p3))
            for t in (i / n for i in range(n + 1))]


def dune(uid, ctrl, lit, shade, bottom, seed, spine=(10, 0.6), rim="#FFD9A0", rip=("#C8583A", "#FFC27A"), rip_shade="#4A1A34",
         n_rip=40, refl=None):
    """A dune range seen from the side with a low sun on the LEFT. Sunlit faces fill the body; from every peak a
    sharp spine sweeps down toward the viewer, and the face to its right (away from the sun) is a shadowed slip
    face reaching to the next trough. Wind ripples follow the slope; the sunlit crest catches a bright rim."""
    line = spline(ctrl)
    body = line + [(line[-1][0], bottom), (line[0][0], bottom)]
    out = [Q(body, lit), f'<clipPath id="{uid}-c"><polygon points="{P(body)}"/></clipPath>']
    g = []
    rnd = random.Random(seed)
    # wind ripples on the lit faces: long shallow S-strokes roughly parallel to the crest
    rp, rh = [], []
    for _ in range(n_rip):
        x0 = rnd.uniform(line[0][0] - 20, line[-1][0])
        y0 = (y_on(line, min(max(x0, line[0][0]), line[-1][0])) or line[0][1]) + rnd.uniform(6, bottom - 300)
        w = rnd.uniform(30, 90)
        d = f'M {x0:.1f} {y0:.1f} q {w * 0.3:.1f} {-rnd.uniform(2, 5):.1f} {w * 0.55:.1f} {-rnd.uniform(0, 2):.1f} t {w * 0.45:.1f} {rnd.uniform(1, 4):.1f}'
        rp.append(f'<path d="{d}"/>')
        rh.append(f'<path d="{d}" transform="translate(0 -1.3)"/>')
    g.append(f'<g fill="none" stroke="{rip[0]}" stroke-width="1.3" stroke-linecap="round" opacity="0.45">{"".join(rp)}</g>'
             f'<g fill="none" stroke="{rip[1]}" stroke-width="1" stroke-linecap="round" opacity="0.5">{"".join(rh)}</g>')
    # peaks and troughs along the crest
    ys = [p[1] for p in line]
    peaks = [i for i in range(1, len(line) - 1) if ys[i] <= ys[i - 1] and ys[i] < ys[i + 1]]
    spines = []
    for pi in peaks:
        j = pi
        while j < len(line) - 1 and ys[j + 1] >= ys[j] - 0.01:
            j += 1
        (xp, yp), (xv, yv) = line[pi], line[j]
        if yv - yp < 4:
            continue
        L = xv - xp
        dx, depth = spine
        xm = xv + dx
        ym = min(bottom + 30, yv + (bottom - yv) * depth + L * 0.25)
        sp = bez((xp, yp), (xp + L * 0.25, yp + (ym - yp) * 0.45), (xm - L * 0.45 - dx * 0.3, ym - (ym - yp) * 0.08), (xm, ym))
        vl = bez((xv, yv), (xv + dx * 0.4, yv + (ym - yv) * 0.4), (xm - dx * 0.1, ym - (ym - yv) * 0.3), (xm, ym))
        poly = line[pi:j + 1] + vl[1:] + sp[::-1]
        g.append(Q(poly, shade))
        if refl:  # warm bounce light low in the slip face
            g.append(Q(poly, refl))
        spines.append(sp)
        # ripples in the shade, darker
        rr = random.Random(seed + pi)
        sh = []
        for _ in range(int((xv - xp) / 8) + 3):
            t = rr.uniform(0.1, 0.9)
            x = xp + (xv - xp) * t + rr.uniform(0, 30)
            y = (y_on(line, min(x, xv)) or yp) + rr.uniform(8, 60)
            w = rr.uniform(16, 40)
            sh.append(f'<path d="M {x:.1f} {y:.1f} q {w * 0.5:.1f} {-rr.uniform(1, 4):.1f} {w:.1f} {rr.uniform(0, 3):.1f}"/>')
        g.append(f'<g fill="none" stroke="{rip_shade}" stroke-width="1.2" stroke-linecap="round" opacity="0.35">{"".join(sh)}</g>')
    out.append(f'<g clip-path="url(#{uid}-c)">' + "".join(g) + "".join(
        f'<polyline points="{P(sp)}" fill="none" stroke="{rim}" stroke-width="1.6" opacity="0.55"/>' for sp in spines) + "</g>")
    # crest: bright on the faces turned to the sun, a fine line along the rest
    for k_ in range(len(line) - 1):
        (x1, y1), (x2, y2) = line[k_], line[k_ + 1]
        up = y2 <= y1 + 0.05
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{rim}" stroke-width="{2.4 if up else 1.2}" stroke-linecap="round" opacity="{0.95 if up else 0.6}"/>')
    return "".join(out), line


def oryx(x, base, k, flip=False, coat="#F6DCCA", shade="#C8939A", dark="#3A2230", rim="#FFE2A8", horn="#2A1A22"):
    """Arabian oryx standing in profile, facing left (toward a low sun): pale coat, dark legs and face mask,
    long straight ringed horns, tufted tail. About 160*k px from hoof to horn tip."""
    sx = -k if flip else k
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({sx:.3f} {k:.3f})">']
    # far legs (darker), far horn
    g.append(f'<path d="M -12 -52 L -12 -28 L -10 -3 M 14 -54 Q 22 -36 17 -18 L 19 -3" fill="none" stroke="{mix(dark, "#000000", 0.25)}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    g.append(f'<path d="M -43 -110 Q -28 -132 -12 -160" fill="none" stroke="{mix(horn, "#000000", 0.2)}" stroke-width="4" stroke-linecap="round"/>')
    # body: deep chest, slight shoulder hump, rounded rump
    g.append(f'<path d="M -36 -74 C -30 -86 -14 -86 6 -84 C 22 -83 34 -84 40 -78 C 48 -70 46 -58 38 -52 C 26 -46 8 -47 -8 -47 '
             f'C -20 -46 -30 -48 -34 -54 C -38 -60 -39 -68 -36 -74 Z" fill="{coat}"/>')
    # shade on the belly and haunch (light from the left, a touch from behind)
    g.append(f'<path d="M -34 -56 C -24 -50 6 -50 22 -52 C 32 -54 40 -60 44 -66 C 46 -58 42 -52 36 -50 C 24 -45 6 -46 -8 -46 C -20 -45 -30 -48 -34 -56 Z" fill="{shade}"/>')
    g.append(f'<path d="M 24 -82 C 36 -82 46 -74 44 -62 C 40 -70 32 -76 22 -78 Z" fill="{shade}" opacity="0.7"/>')
    # dark flank stripe and dark upper legs
    g.append(f'<path d="M -30 -54 C -14 -52 10 -52 32 -55" fill="none" stroke="{dark}" stroke-width="3" stroke-linecap="round" opacity="0.7"/>')
    # neck and head
    g.append(f'<path d="M -38 -68 C -44 -80 -48 -94 -48 -104 L -34 -110 C -32 -98 -26 -88 -16 -82 Z" fill="{coat}"/>')
    g.append(f'<path d="M -40 -110 C -46 -114 -54 -110 -58 -104 L -68 -93 C -71 -89 -68 -85 -63 -86 L -48 -92 C -40 -96 -36 -104 -40 -110 Z" fill="{coat}"/>')
    # face mask: stripe through the eye down the cheek, dark nose band, dark throat patch
    g.append(f'<path d="M -50 -108 L -56 -100 L -63 -90 L -59 -88 L -51 -98 L -46 -106 Z" fill="{dark}"/>')
    g.append(f'<path d="M -66 -95 L -60 -101 L -58 -98 L -64 -91 Z" fill="{dark}"/>')
    g.append(f'<path d="M -44 -96 C -42 -90 -40 -84 -37 -78 L -34 -80 C -37 -86 -39 -92 -40 -98 Z" fill="{shade}" opacity="0.8"/>')
    g.append(f'<circle cx="-50" cy="-103" r="1.6" fill="#120A0E"/><circle cx="-50.6" cy="-103.6" r="0.5" fill="#FFFFFF"/>')
    # ears swept back
    g.append(f'<path d="M -40 -109 L -30 -116 L -32 -110 L -38 -106 Z" fill="{coat}"/><path d="M -38 -108 L -31 -113" stroke="{shade}" stroke-width="1.2"/>')
    # near horn with growth rings
    g.append(f'<path d="M -46 -110 Q -32 -132 -18 -162" fill="none" stroke="{horn}" stroke-width="4.4" stroke-linecap="round"/>')
    g.append(f'<g stroke="{rim}" stroke-width="1" opacity="0.6">' + "".join(
        f'<line x1="{-46 + 14 * t - 2:.1f}" y1="{-110 - 26 * t:.1f}" x2="{-46 + 14 * t + 2:.1f}" y2="{-110 - 26 * t + 1.5:.1f}"/>' for t in (0.1, 0.2, 0.3, 0.4, 0.5)) + "</g>")
    # near legs: muscled shoulder and thigh in the coat, slim dark shanks, white pasterns, small hooves
    g.append(f'<path d="M -36 -66 C -30 -70 -20 -66 -18 -56 L -20 -40 L -21 -24 L -19 -4 L -25 -4 L -27 -24 L -29 -42 C -33 -48 -37 -56 -36 -66 Z" fill="{dark}"/>')
    g.append(f'<path d="M -36 -68 C -28 -72 -18 -66 -18 -56 C -22 -50 -28 -48 -32 -50 C -36 -54 -38 -62 -36 -68 Z" fill="{coat}"/>')
    g.append(f'<path d="M 18 -80 C 34 -84 48 -72 42 -56 C 40 -50 37 -46 35 -40 C 32 -32 30 -26 31 -16 L 34 -4 L 28 -4 L 25 -16 C 24 -26 24 -34 22 -42 C 16 -52 14 -70 18 -80 Z" fill="{dark}"/>')
    g.append(f'<path d="M 18 -80 C 34 -84 48 -72 42 -56 C 38 -50 32 -48 26 -50 C 18 -56 14 -70 18 -80 Z" fill="{coat}"/>')
    g.append(f'<path d="M 30 -54 C 38 -56 42 -60 43 -64 C 44 -56 40 -50 34 -49 Z" fill="{shade}"/>')
    for hx in (-22, 31):
        g.append(f'<path d="M {hx - 3} -11 L {hx + 3} -11 L {hx + 3.4} -4 L {hx - 3.4} -4 Z" fill="{coat}"/>')
        g.append(f'<path d="M {hx - 4} -4 L {hx + 4} -4 L {hx + 4.6} 0 L {hx - 4.6} 0 Z" fill="{horn}"/>')
    # tail with a black tuft
    g.append(f'<path d="M 42 -74 Q 48 -64 46 -50" fill="none" stroke="{coat}" stroke-width="3" stroke-linecap="round"/><path d="M 46 -54 Q 49 -46 45 -40 Q 43 -48 44 -54 Z" fill="{dark}"/>')
    # rim light from the sun ahead: brow, nose, throat, chest, back
    g.append(f'<path d="M -58 -104 C -54 -110 -46 -113 -40 -110" fill="none" stroke="{rim}" stroke-width="2" stroke-linecap="round"/>'
             f'<path d="M -68 -93 C -71 -89 -68 -85 -63 -86" fill="none" stroke="{rim}" stroke-width="1.8" stroke-linecap="round"/>'
             f'<path d="M -46 -104 C -44 -94 -40 -82 -36 -74 C -39 -68 -38 -60 -34 -54" fill="none" stroke="{rim}" stroke-width="2.4" stroke-linecap="round"/>'
             f'<path d="M -30 -84 C -14 -87 10 -84 26 -83" fill="none" stroke="{rim}" stroke-width="2" stroke-linecap="round" opacity="0.85"/>'
             f'<path d="M -47 -111 Q -33 -133 -19 -163" fill="none" stroke="{rim}" stroke-width="1.2" stroke-linecap="round" opacity="0.7"/>')
    g.append("</g>")
    return "".join(g)


def falcon(x, y, s, color="#2A1A30", rim="#FFB070"):
    """Saker falcon soaring: long pointed wings, short fanned tail."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            f'<path d="M -4 -2 Q -18 -10 -34 -6 Q -46 -4 -56 2 Q -40 -1 -26 2 Q -14 4 -4 4 L -3 12 L 0 16 L 3 12 L 4 4 Q 14 4 26 2 Q 40 -1 56 2 Q 46 -4 34 -6 Q 18 -10 4 -2 Q 2 -8 0 -9 Q -2 -8 -4 -2 Z" fill="{color}"/>'
            f'<path d="M -56 2 Q -46 -4 -34 -6 Q -18 -10 -4 -2" stroke="{rim}" stroke-width="1.4" fill="none" opacity="0.8"/></g>')


def ghaf(x, base, h, seed, dark="#4A2238", mid="#6A3046", rim="#FFB070"):
    """Ghaf tree: a short crooked trunk and a broad, drooping crown of fine foliage."""
    rnd = random.Random(seed)
    out = [f'<path d="M {x - 3:.1f} {base:.1f} Q {x - 1:.1f} {base - h * 0.3:.1f} {x - 6:.1f} {base - h * 0.55:.1f} L {x - 2:.1f} {base - h * 0.56:.1f} Q {x + 3:.1f} {base - h * 0.32:.1f} {x + 3:.1f} {base:.1f} Z" fill="{dark}"/>',
           f'<path d="M {x - 2:.1f} {base - h * 0.4:.1f} Q {x + h * 0.2:.1f} {base - h * 0.5:.1f} {x + h * 0.32:.1f} {base - h * 0.6:.1f}" stroke="{dark}" stroke-width="2.2" fill="none"/>']
    puffs, lit = [], []
    for _ in range(26):
        px = x + rnd.uniform(-h * 0.55, h * 0.6)
        py = base - h * 0.62 - rnd.uniform(-h * 0.08, h * 0.32) * (1 - abs(px - x) / (h * 0.7))
        r = rnd.uniform(h * 0.08, h * 0.15)
        puffs.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{r * 1.4:.1f}" ry="{r:.1f}"/>')
        if px < x:
            lit.append(f'<ellipse cx="{px - r * 0.4:.1f}" cy="{py - r * 0.3:.1f}" rx="{r * 0.8:.1f}" ry="{r * 0.5:.1f}"/>')
    out.append(f'<g fill="{mid}">' + "".join(puffs) + f'</g><g fill="{rim}" opacity="0.45">' + "".join(lit) + "</g>")
    out.append(f'<g stroke="{mid}" stroke-width="1.4" stroke-linecap="round">' + "".join(
        f'<line x1="{x + d:.1f}" y1="{base - h * 0.58:.1f}" x2="{x + d + 1:.1f}" y2="{base - h * 0.58 + rnd.uniform(4, 10):.1f}"/>' for d in [rnd.uniform(-h * 0.6, h * 0.65) for _ in range(30)]) + "</g>")
    return "".join(out)


def skyline(x0, x1, hz, seed, cols, lit_col="#FFE2A8", rim="#FFC890", hmax=96):
    """A generic modern skyline: slim towers of varied heights and crowns (flat, stepped, slanted, rounded),
    a sun-catching edge on the left of each and scattered lit windows."""
    rnd = random.Random(seed)
    towers, x = [], x0
    while x < x1:
        w = rnd.uniform(7, 15)
        mid = 1 - abs((x - x0) / (x1 - x0) - 0.45) * 1.6
        h = rnd.uniform(10, 26) + max(0, mid) * rnd.uniform(10, hmax)
        towers.append((x, w, h, rnd.random()))
        x += w + rnd.uniform(-1, 5)
    towers.sort(key=lambda t: -t[2] * 0 + rnd.random())
    tw = []
    for x, w, h, kind in towers:
        top = hz - h
        col = mix(cols[0], cols[1], rnd.uniform(0, 1))
        if kind < 0.18:
            tw.append(f'<path d="M {x:.1f} {hz:.1f} L {x:.1f} {top + w / 2:.1f} Q {x + w / 2:.1f} {top - w * 0.15:.1f} {x + w:.1f} {top + w / 2:.1f} L {x + w:.1f} {hz:.1f} Z" fill="{col}"/>')
        elif kind < 0.36:
            tw.append(Q([(x, hz), (x, top), (x + w, top + w * 0.7), (x + w, hz)], col))
        elif kind < 0.52:
            tw.append(f'<rect x="{x:.1f}" y="{top + 8:.1f}" width="{w:.1f}" height="{h - 8:.1f}" fill="{col}"/><rect x="{x + w * 0.18:.1f}" y="{top + 3:.1f}" width="{w * 0.64:.1f}" height="6" fill="{col}"/>'
                      f'<rect x="{x + w * 0.34:.1f}" y="{top:.1f}" width="{w * 0.32:.1f}" height="4" fill="{col}"/>')
        else:
            tw.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{col}"/>')
        tw.append(f'<rect x="{x:.1f}" y="{top + 4:.1f}" width="1.4" height="{h - 4:.1f}" fill="{rim}" opacity="0.55"/>')
        for yy in range(int(top) + 6, int(hz) - 3, 4):
            for xx in range(int(x) + 2, int(x + w) - 1, 3):
                if rnd.random() < 0.12:
                    tw.append(f'<rect x="{xx}" y="{yy}" width="1.3" height="1.5" fill="{lit_col}" opacity="{rnd.uniform(0.45, 0.95):.2f}"/>')
    return "".join(tw)


def dubai():
    u = "dxb"
    hz = 292
    sunx, suny = 128, 262
    out = [defs(
        lg(f"{u}-sky", [(0, "#1E3656"), (0.26, "#3E4E76"), (0.5, "#9A6880"), (0.7, "#E28C62"), (0.86, "#F6B25C"), (1, "#FBD68E")], 0, 40, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#EE9A62"), (1, "#D8704C")], 0, 284, 0, 330, units="userSpaceOnUse"),
        lg(f"{u}-d1", [(0, "#F0904E"), (1, "#D2643C")], 0, 300, 0, 380, units="userSpaceOnUse"),
        lg(f"{u}-d2", [(0, "#F7A458"), (0.5, "#E87842"), (1, "#C85434")], 0, 320, 0, 430, units="userSpaceOnUse"),
        lg(f"{u}-d3", [(0, "#FBB664"), (0.35, "#F08A48"), (1, "#C8522E")], 0, 350, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-sh1", [(0, "#A84446"), (1, "#7E3040")], 0, 300, 0, 380, units="userSpaceOnUse"),
        lg(f"{u}-sh2", [(0, "#97363E"), (1, "#5E2234")], 0, 320, 0, 430, units="userSpaceOnUse"),
        lg(f"{u}-sh3", [(0, "#8A2E3A"), (0.6, "#5A1E30"), (1, "#3E1428")], 0, 350, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-rf", [(0, "#E8703E", 0), (0.7, "#E8703E", 0), (1, "#F08848", 0.35)], 0, 0, 0, 1),
        lg(f"{u}-haze", [(0, "#F8B070", 0), (1, "#FAC27E", 0.85)], 0, 220, 0, hz + 4, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="{hz + 40}" fill="url(#{u}-sky)"/>')
    out.append(dots(30, 2, (0, 40, 600, 130), "#F6EEE0", r=(0.6, 1.2), opacity=(0.25, 0.8)))
    out.append(glow(sunx, suny, 380, "#FFB868", f"{u}-g1", 0.7))
    out.append(glow(sunx, suny, 96, "#FFEBB0", f"{u}-g2", 0.95))
    out.append(f'<circle cx="{sunx}" cy="{suny}" r="34" fill="#FFF1C8"/>')
    # dust-thin cloud streaks, lit from below
    for x, y, w, c in ((360, 112, 150, "#7A5A80"), (520, 136, 90, "#9A6080"), (250, 160, 110, "#C87478"), (470, 186, 130, "#E08A6A"),
                       (90, 186, 90, "#E89A6A"), (330, 214, 80, "#F4A866"), (560, 220, 60, "#F8B470")):
        out.append(streak_cloud(x, y, w, c, 0.7, 3.6))
        out.append(streak_cloud(x - w * 0.25, y + 2.4, w * 0.5, "#FFD6A0", 0.45, 1.3))
    # the city on the horizon, softened by dust haze
    out.append(skyline(352, 560, hz + 2, 31, ("#A86A7A", "#C47E7E"), rim="#FFD0A0"))
    out.append(f'<rect x="0" y="210" width="600" height="{hz + 6 - 210}" fill="url(#{u}-haze)"/>')
    # far dunes and a lone ghaf tree
    poly, far = ridge_poly([(-10, 292), (80, 286), (190, 292), (300, 284), (420, 292), (520, 286), (610, 291)], 6, base=360, amp=3, fill=f"url(#{u}-far)")
    out.append(poly)
    out.append(f'<polyline points="{P(far)}" fill="none" stroke="#FFD8A0" stroke-width="1.2" opacity="0.6"/>')
    out.append(mist(sunx, 292, 240, 16, "#FFDCA6", f"{u}-m1", 0.7))
    out.append(ghaf(46, 291, 30, 4, dark="#9A4A52", mid="#A8585C", rim="#FFC890"))
    # ranges of dunes, far to near
    d, c1 = dune(f"{u}-a", [(-10, 318), (80, 306), (190, 320), (300, 302), (420, 318), (530, 304), (610, 312)], f"url(#{u}-d1)", f"url(#{u}-sh1)", 380, 3,
                 spine=(8, 0.7), rip=("#C8583A", "#FFC27A"), rip_shade="#5A2034", n_rip=26)
    out.append(d)
    d, c2 = dune(f"{u}-b", [(-10, 356), (110, 338), (230, 328), (330, 342), (460, 322), (610, 344)], f"url(#{u}-d2)", f"url(#{u}-sh2)", 430, 5,
                 spine=(16, 0.6), rip=("#C8583A", "#FFC27A"), rip_shade="#4A1830", n_rip=44, refl=f"url(#{u}-rf)")
    out.append(d)
    # oryx pair on the crest, hoofprints leading up to them
    ox1, ox2 = 224, 296
    out.append(f'<g fill="#7A2A3A" opacity="0.45">' + "".join(
        f'<ellipse cx="{x:.1f}" cy="{(y_on(c2, x) or 340) + 5 + (i % 2) * 2.5:.1f}" rx="2" ry="1"/>' for i, x in enumerate(range(80, 206, 8))) + "</g>")
    out.append(oryx(ox2, (y_on(c2, ox2) or 330) + 2, 0.58, coat="#F2D2C2", shade="#C08E98"))
    out.append(oryx(ox1, (y_on(c2, ox1) or 340) + 2, 0.92))
    # the big dune in front: a long sunlit flank rising to a sharp crest, its slip face in deep shade
    d, c3 = dune(f"{u}-c", [(-10, 426), (110, 408), (230, 388), (340, 368), (410, 360), (480, 374), (610, 400)], f"url(#{u}-d3)", f"url(#{u}-sh3)", 444, 8,
                 spine=(10, 0.55), rip=("#C85A38", "#FFD08A"), rip_shade="#2E0E22", n_rip=70)
    out.append(d)
    # sand streaming off the crest in the evening breeze
    out.append(f'<g stroke="#FFDCA8" stroke-width="1.2" stroke-linecap="round" opacity="0.55">' + "".join(
        f'<line x1="{x:.1f}" y1="{(y_on(c3, x) or 370) - 1:.1f}" x2="{x + 30:.1f}" y2="{(y_on(c3, x) or 370) - 4:.1f}"/>' for x in range(330, 416, 10)) + "</g>")
    out.append(dots(60, 66, (350, 340, 500, 366), "#FFE2B0", r=(0.5, 1.1), opacity=(0.3, 0.8)))
    # a few desert shrubs on the near flank, their long shadows running away from the sun
    for sx_, sh_ in ((96, 16), (150, 11), (60, 9)):
        sy_ = (y_on(c3, sx_) or 420) + 14
        out.append(f'<path d="M {sx_:.1f} {sy_:.1f} L {sx_ + sh_ * 4:.1f} {sy_ + 2:.1f} L {sx_ + sh_ * 4:.1f} {sy_ + 5:.1f} L {sx_:.1f} {sy_ + 3:.1f} Z" fill="#8A2E3A" opacity="0.4"/>')
        out.append(grass(14, int(sx_), (sx_ - sh_ * 0.5, sy_, sx_ + sh_ * 0.5, sy_ + 2), ["#5A3428", "#7A4A30", "#3E2420"], h=(sh_ * 0.6, sh_), sw=1.6))
        out.append(f'<g stroke="#FFD08A" stroke-width="1" fill="none" opacity="0.8">' + "".join(f'<path d="M {sx_ - sh_ * 0.3 + i * 2:.1f} {sy_:.1f} q -2 {-sh_ * 0.4:.1f} -3 {-sh_ * 0.8:.1f}"/>' for i in range(3)) + "</g>")
    # a desert hyacinth / grass tuft on the near flank
    out.append(falcon(392, 168, 0.72, color="#2A1E36", rim="#FFC27A"))
    out.append(gulls([(470, 222, 8), (488, 230, 6)], "#3A2440", 1.6))
    return "\n".join(out)



# ================================================================ MARRAKECH — a riad arch framing the medina, the Koutoubia and the snowy Atlas
def horseshoe(cx, cy, r, e, jh, floor, n=28):
    """Slightly pointed Moorish horseshoe arch outline: jambs at cx +- jh standing on floor, arcs of radius r whose
    centres sit e px either side of the axis, so they meet in a soft point at the top."""
    a0 = math.degrees(math.acos((-jh - e) / r))
    a1 = 360 - math.degrees(math.acos(-e / r))
    left = [(cx + e + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    right = [(2 * cx - x, y) for x, y in left[::-1]]
    return [(cx - jh, floor)] + left + right[1:] + [(cx + jh, floor)]


def zellige(uid, box, cell, seed, cols=("#1E4E9A", "#2A9A9A", "#2E7A4A", "#F4EEE2", "#D89A3A"), grout="#2A2230"):
    """Zellige tile field: eight-pointed stars (two interlaced squares) with octagon centres and little
    cross-shaped fillers between them, hand-cut colour variation tile to tile."""
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    blue, teal, green, white, ochre = cols
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{white}"/>']
    h = cell / 2
    y = y0
    while y < y1 + cell:
        x = x0
        while x < x1 + cell:
            cx, cy = x + h, y + h
            s1 = [(cx - h * 0.62, cy - h * 0.62), (cx + h * 0.62, cy - h * 0.62), (cx + h * 0.62, cy + h * 0.62), (cx - h * 0.62, cy + h * 0.62)]
            s2 = [(cx, cy - h * 0.88), (cx + h * 0.88, cy), (cx, cy + h * 0.88), (cx - h * 0.88, cy)]
            sc = mix(blue, "#0E2A66", rnd.uniform(0, 0.35))
            out.append(Q(s1, sc) + Q(s2, sc))
            oc = [(cx + h * 0.42 * math.cos(math.radians(22.5 + 45 * i)), cy + h * 0.42 * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
            out.append(Q(oc, mix(teal, "#FFFFFF", rnd.uniform(0, 0.2))))
            out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{h * 0.16:.1f}" fill="{ochre}"/>')
            # corner fillers (between four stars)
            out.append(Q([(x, y - h * 0.3), (x + h * 0.3, y), (x, y + h * 0.3), (x - h * 0.3, y)], mix(green, "#0E3A20", rnd.uniform(0, 0.3))))
            x += cell
        y += cell
    # grout lines
    gl = []
    y = y0
    while y < y1 + cell:
        x = x0
        while x < x1 + cell:
            cx, cy = x + h, y + h
            gl.append(f'<polygon points="{P([(cx, cy - h * 0.88), (cx + h * 0.88, cy), (cx, cy + h * 0.88), (cx - h * 0.88, cy)])}"/>')
            gl.append(f'<rect x="{cx - h * 0.62:.1f}" y="{cy - h * 0.62:.1f}" width="{h * 1.24:.1f}" height="{h * 1.24:.1f}"/>')
            x += cell
        y += cell
    out.append(f'<g fill="none" stroke="{grout}" stroke-width="0.9" opacity="0.55">{"".join(gl)}</g>')
    # glaze sheen
    out.append(dots(int((x1 - x0) * (y1 - y0) / 260), seed + 3, box, "#FFFFFF", r=(0.6, 1.6), opacity=(0.25, 0.7)))
    return f'<clipPath id="{uid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath><g clip-path="url(#{uid})">' + "".join(out) + "</g>"


def lantern(x, top, k, u, glass=("#2AA8A0", "#F2A23A", "#C8343A"), brass="#B8862E", dark="#5A3A1A", glow_r=70, chain=0):
    """Moroccan pierced-brass lantern: onion cap with a finial, a six-sided body of coloured glass panes
    under pierced brass, a tapering foot with a drop. Glows. top = y of the hanging ring."""
    out = []
    if chain:
        out.append(f'<line x1="{x:.1f}" y1="{top - chain:.1f}" x2="{x:.1f}" y2="{top:.1f}" stroke="{dark}" stroke-width="{1.6 * k:.1f}" stroke-dasharray="{3 * k:.1f} {1.4 * k:.1f}"/>')
    by = top + 24 * k
    out.append(glow(x, by + 18 * k, glow_r * k, "#FFC76A", f"{u}-gl", 0.75))
    out.append(f'<circle cx="{x:.1f}" cy="{top + 2 * k:.1f}" r="{2.6 * k:.1f}" fill="none" stroke="{brass}" stroke-width="{1.4 * k:.1f}"/>')
    out.append(f'<path d="M {x:.1f} {top + 4 * k:.1f} L {x:.1f} {top + 9 * k:.1f}" stroke="{brass}" stroke-width="{2 * k:.1f}"/>')
    # onion cap
    out.append(f'<path d="M {x - 15 * k:.1f} {by:.1f} C {x - 15 * k:.1f} {by - 8 * k:.1f} {x - 4 * k:.1f} {by - 10 * k:.1f} {x:.1f} {by - 16 * k:.1f} C {x + 4 * k:.1f} {by - 10 * k:.1f} {x + 15 * k:.1f} {by - 8 * k:.1f} {x + 15 * k:.1f} {by:.1f} Z" fill="{brass}"/>')
    out.append(f'<path d="M {x + 2 * k:.1f} {by - 12 * k:.1f} C {x + 6 * k:.1f} {by - 8 * k:.1f} {x + 13 * k:.1f} {by - 7 * k:.1f} {x + 14 * k:.1f} {by - 1 * k:.1f}" fill="none" stroke="#F8D88A" stroke-width="{1.4 * k:.1f}"/>')
    out.append(dots(10, int(x), (x - 11 * k, by - 7 * k, x + 11 * k, by - 2 * k), "#FFE6A0", r=(0.6 * k, 1.1 * k), opacity=(0.8, 1)))
    out.append(f'<rect x="{x - 17 * k:.1f}" y="{by:.1f}" width="{34 * k:.1f}" height="{3 * k:.1f}" fill="{dark}"/>')
    # body: three visible panes (a hexagon seen side-on) of glass
    bt, bb = by + 3 * k, by + 36 * k
    panes = [(x - 16 * k, x - 7 * k, glass[2]), (x - 7 * k, x + 7 * k, glass[1]), (x + 7 * k, x + 16 * k, glass[0])]
    for i, (a, b, c) in enumerate(panes):
        ia = a + (2 * k if i == 0 else 0)
        ib = b - (2 * k if i == 2 else 0)
        out.append(Q([(ia, bt), (ib, bt), (ib + (2 * k if i == 2 else 0) - (0 if i == 2 else 0), bb - 6 * k), (b - (3 * k if i == 2 else 0), bb), (a + (3 * k if i == 0 else 0), bb), (ia - (0 if i else 0), bb - 6 * k)], c))
        out.append(Q([(ia + 2 * k, bt + 2 * k), (ib - 2 * k, bt + 2 * k), (ib - 2 * k, bt + 12 * k), (ia + 2 * k, bt + 12 * k)], "#FFF2C0", ' opacity="0.55"'))
    out.append(f'<g stroke="{brass}" stroke-width="{2 * k:.1f}">' + "".join(f'<line x1="{xx:.1f}" y1="{bt:.1f}" x2="{xx + (xx - x) * 0.1:.1f}" y2="{bb:.1f}"/>' for xx in (x - 7 * k, x + 7 * k)) + "</g>")
    # pierced brass tracery over the glass: arches and dots
    out.append(f'<g fill="none" stroke="{brass}" stroke-width="{1.2 * k:.1f}">' + "".join(
        f'<path d="M {cx_ - 3.5 * k:.1f} {bb - 4 * k:.1f} L {cx_ - 3.5 * k:.1f} {bt + 14 * k:.1f} Q {cx_:.1f} {bt + 8 * k:.1f} {cx_ + 3.5 * k:.1f} {bt + 14 * k:.1f} L {cx_ + 3.5 * k:.1f} {bb - 4 * k:.1f}"/>' for cx_ in (x - 11.5 * k, x, x + 11.5 * k)) + "</g>")
    out.append(f'<rect x="{x - 16 * k:.1f}" y="{bb:.1f}" width="{32 * k:.1f}" height="{3 * k:.1f}" fill="{dark}"/>')
    out.append(f'<path d="M {x - 14 * k:.1f} {bb + 3 * k:.1f} L {x + 14 * k:.1f} {bb + 3 * k:.1f} L {x + 5 * k:.1f} {bb + 13 * k:.1f} L {x - 5 * k:.1f} {bb + 13 * k:.1f} Z" fill="{brass}"/>')
    out.append(dots(8, int(x) + 1, (x - 10 * k, bb + 5 * k, x + 10 * k, bb + 10 * k), "#FFE6A0", r=(0.6 * k, 1 * k), opacity=(0.8, 1)))
    out.append(f'<path d="M {x:.1f} {bb + 13 * k:.1f} L {x:.1f} {bb + 18 * k:.1f}" stroke="{brass}" stroke-width="{1.6 * k:.1f}"/><circle cx="{x:.1f}" cy="{bb + 20 * k:.1f}" r="{2.4 * k:.1f}" fill="{brass}"/>')
    # light spilling through the pierced holes
    out.append(f'<line x1="{x + 15 * k:.1f}" y1="{bt:.1f}" x2="{x + 13 * k:.1f}" y2="{bb:.1f}" stroke="#FFE6A0" stroke-width="{1.2 * k:.1f}" opacity="0.8"/>')
    return "".join(out)


def koutoubia(cx, base, w, h, u):
    """The Koutoubia minaret: a tall square tower of rose stone, each face with a different blind-arch panel,
    a turquoise ceramic band and stepped merlons at the top, then the small lantern tower with a ribbed dome and
    three golden spheres. The right face takes the late sun."""
    sw = w * 0.24  # visible width of the sunlit side face
    top = base - h
    out = [Q([(cx - w / 2, base), (cx - w / 2, top), (cx + w / 2, top), (cx + w / 2, base)], f"url(#{u}-kf)"),
           Q([(cx + w / 2, base), (cx + w / 2, top), (cx + w / 2 + sw, top - 2), (cx + w / 2 + sw, base - 2)], f"url(#{u}-ks)")]
    # stone courses
    out.append(f'<g stroke="#8A4E46" stroke-width="0.8" opacity="0.25">' + "".join(f'<line x1="{cx - w / 2:.1f}" y1="{y:.1f}" x2="{cx + w / 2 + sw:.1f}" y2="{y - 2 * (1 if False else 0):.1f}"/>' for y in [base - i * 6 for i in range(1, int(h / 6))]) + "</g>")
    # windows on the shaft
    for i, t in enumerate((0.18, 0.36, 0.52)):
        y = base - h * t
        out.append(f'<path d="M {cx - 2.4:.1f} {y:.1f} L {cx - 2.4:.1f} {y - 7:.1f} Q {cx:.1f} {y - 10:.1f} {cx + 2.4:.1f} {y - 7:.1f} L {cx + 2.4:.1f} {y:.1f} Z" fill="#5A2E32"/>')
    # the big blind-arch panels: a polylobed arch over a sebka lattice
    py0, py1 = base - h * 0.88, base - h * 0.62
    out.append(f'<rect x="{cx - w * 0.36:.1f}" y="{py0:.1f}" width="{w * 0.72:.1f}" height="{py1 - py0:.1f}" fill="none" stroke="#8A4E46" stroke-width="1.4" opacity="0.7"/>')
    out.append(f'<path d="M {cx - w * 0.26:.1f} {py1:.1f} L {cx - w * 0.26:.1f} {py0 + 12:.1f} Q {cx - w * 0.26:.1f} {py0 + 4:.1f} {cx:.1f} {py0 + 3:.1f} Q {cx + w * 0.26:.1f} {py0 + 4:.1f} {cx + w * 0.26:.1f} {py0 + 12:.1f} L {cx + w * 0.26:.1f} {py1:.1f}" fill="#9A5A50" opacity="0.55"/>')
    lat = []
    for i in range(4):
        for j in range(3):
            lx, ly = cx - w * 0.2 + j * w * 0.2, py0 + 16 + i * 8
            lat.append(f'<path d="M {lx - 4:.1f} {ly + 4:.1f} L {lx:.1f} {ly:.1f} L {lx + 4:.1f} {ly + 4:.1f} L {lx:.1f} {ly + 8:.1f} Z"/>')
    out.append(f'<g fill="none" stroke="#7A3E3E" stroke-width="1" opacity="0.6">{"".join(lat)}</g>')
    # sebka on the lit side face
    out.append(f'<g fill="none" stroke="#C47A62" stroke-width="1" opacity="0.7">' + "".join(
        f'<path d="M {cx + w / 2 + 1.5:.1f} {py0 + 14 + i * 9:.1f} L {cx + w / 2 + sw / 2:.1f} {py0 + 9 + i * 9:.1f} L {cx + w / 2 + sw - 1.5:.1f} {py0 + 14 + i * 9:.1f}"/>' for i in range(5)) + "</g>")
    # turquoise ceramic band, crown frieze and stepped merlons
    out.append(f'<rect x="{cx - w / 2:.1f}" y="{top + 4:.1f}" width="{w:.1f}" height="4" fill="#2A8A86"/><rect x="{cx + w / 2:.1f}" y="{top + 3:.1f}" width="{sw:.1f}" height="4" fill="#4AB8A8"/>')
    out.append(dots(14, 5, (cx - w / 2, top + 4.5, cx + w / 2, top + 7.5), "#F4EEE2", r=(0.6, 0.9), opacity=(0.8, 1)))
    mer = []
    n = 5
    for i in range(n):
        mx = cx - w / 2 + (i + 0.5) * w / n
        mw = w / n * 0.62
        mer.append(f'<path d="M {mx - mw / 2:.1f} {top:.1f} L {mx - mw / 2:.1f} {top - 4:.1f} L {mx - mw / 4:.1f} {top - 4:.1f} L {mx - mw / 4:.1f} {top - 7:.1f} L {mx + mw / 4:.1f} {top - 7:.1f} L {mx + mw / 4:.1f} {top - 4:.1f} L {mx + mw / 2:.1f} {top - 4:.1f} L {mx + mw / 2:.1f} {top:.1f} Z"/>')
    out.append(f'<g fill="#C98270">{"".join(mer)}</g>')
    out.append(f'<path d="M {cx + w / 2 + 1:.1f} {top - 1:.1f} L {cx + w / 2 + 1:.1f} {top - 6:.1f} L {cx + w / 2 + sw * 0.7:.1f} {top - 7:.1f} L {cx + w / 2 + sw * 0.7:.1f} {top - 2:.1f} Z" fill="#F4BC94"/>')
    # lantern tower
    lw, lh = w * 0.36, h * 0.13
    lt = top - lh
    out.append(f'<rect x="{cx - lw / 2:.1f}" y="{lt:.1f}" width="{lw:.1f}" height="{lh:.1f}" fill="url(#{u}-kf)"/>')
    out.append(f'<rect x="{cx + lw / 2:.1f}" y="{lt - 1:.1f}" width="{lw * 0.24:.1f}" height="{lh:.1f}" fill="#F0B48C"/>')
    out.append(f'<path d="M {cx - 2:.1f} {top - 3:.1f} L {cx - 2:.1f} {lt + lh * 0.45:.1f} Q {cx:.1f} {lt + lh * 0.3:.1f} {cx + 2:.1f} {lt + lh * 0.45:.1f} L {cx + 2:.1f} {top - 3:.1f} Z" fill="#5A2E32"/>')
    out.append(f'<rect x="{cx - lw / 2:.1f}" y="{lt + 2:.1f}" width="{lw:.1f}" height="2.4" fill="#2A8A86"/>')
    out.append(f'<path d="M {cx - lw / 2 - 1:.1f} {lt:.1f} Q {cx:.1f} {lt - lw * 0.75:.1f} {cx + lw / 2 + lw * 0.24 + 1:.1f} {lt:.1f} Z" fill="#B87A5E"/>')
    out.append(f'<path d="M {cx + 1:.1f} {lt - lw * 0.36:.1f} Q {cx + lw * 0.4:.1f} {lt - lw * 0.3:.1f} {cx + lw * 0.68:.1f} {lt - 1:.1f}" fill="none" stroke="#FFD0A0" stroke-width="1.4"/>')
    # finial with three golden spheres, the largest at the bottom
    fy = lt - lw * 0.36
    out.append(f'<line x1="{cx:.1f}" y1="{fy:.1f}" x2="{cx:.1f}" y2="{fy - 24:.1f}" stroke="#B8862E" stroke-width="1.5"/>')
    for r, dy in ((3.6, 6), (2.8, 13), (2.1, 19)):
        out.append(f'<circle cx="{cx:.1f}" cy="{fy - dy:.1f}" r="{r}" fill="#E0AE48"/><circle cx="{cx + r * 0.35:.1f}" cy="{fy - dy - r * 0.35:.1f}" r="{r * 0.4:.1f}" fill="#FFF0B8"/>')
    # sun rim on the lit corner
    out.append(f'<line x1="{cx + w / 2 + sw:.1f}" y1="{top - 2:.1f}" x2="{cx + w / 2 + sw:.1f}" y2="{base - 2:.1f}" stroke="#FFE0B0" stroke-width="1.4" opacity="0.8"/>')
    return "".join(out)


def stork(x, y, s, flip=False, rim="#FFE2B0"):
    """White stork in flight: neck outstretched, red bill and trailing red legs, black flight feathers."""
    sx = -s if flip else s
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({sx:.3f} {s:.3f})">'
            '<path d="M -6 -2 Q -16 -14 -30 -18 Q -40 -20 -50 -16 Q -36 -12 -24 -4 Q -14 2 -6 3 Z" fill="#2A2026"/>'
            '<path d="M -6 -2 Q -16 -12 -28 -15 Q -22 -8 -12 0 Z" fill="#F6F2EC"/>'
            '<path d="M 4 -2 Q 14 -16 30 -22 Q 42 -26 54 -22 Q 40 -16 26 -6 Q 14 2 4 3 Z" fill="#2A2026"/>'
            '<path d="M 4 -2 Q 14 -14 28 -19 Q 22 -10 12 0 Z" fill="#F6F2EC"/>'
            '<path d="M -22 0 Q -10 -6 6 -4 Q 16 -2 20 1 Q 10 5 -6 4 Q -16 3 -22 0 Z" fill="#F6F2EC"/>'
            '<path d="M -22 0 Q -30 -2 -38 -3" stroke="#F6F2EC" stroke-width="3.2" stroke-linecap="round" fill="none"/>'
            '<circle cx="-39" cy="-3.2" r="2.4" fill="#F6F2EC"/><path d="M -41 -4 L -52 -2 L -41 -1.4 Z" fill="#D8402E"/>'
            '<path d="M 18 1 L 38 3 M 18 2 L 37 6" stroke="#D8402E" stroke-width="1.4" stroke-linecap="round"/>'
            f'<path d="M -20 -1 Q -8 -5 8 -3.4" stroke="{rim}" stroke-width="1.2" fill="none"/></g>')


def tea_set(x, base, k, u):
    """Brass tray on a low stand with a silver Moroccan teapot and two painted tea glasses of mint tea."""
    out = []
    # stand: carved wooden legs
    out.append(f'<path d="M {x - 44 * k:.1f} {base:.1f} L {x - 38 * k:.1f} {base - 26 * k:.1f} L {x + 38 * k:.1f} {base - 26 * k:.1f} L {x + 44 * k:.1f} {base:.1f} L {x + 36 * k:.1f} {base:.1f} L {x + 30 * k:.1f} {base - 18 * k:.1f} L {x - 30 * k:.1f} {base - 18 * k:.1f} L {x - 36 * k:.1f} {base:.1f} Z" fill="#4A2A1E"/>')
    out.append(f'<path d="M {x - 26 * k:.1f} {base - 18 * k:.1f} Q {x:.1f} {base - 4 * k:.1f} {x + 26 * k:.1f} {base - 18 * k:.1f}" fill="none" stroke="#6A3E26" stroke-width="{2 * k:.1f}"/>')
    # tray seen from slightly above: brass ellipse, engraved rings, sheen
    ty = base - 28 * k
    out.append(f'<ellipse cx="{x:.1f}" cy="{ty + 2 * k:.1f}" rx="{50 * k:.1f}" ry="{11 * k:.1f}" fill="#8A5A1E"/>')
    out.append(f'<ellipse cx="{x:.1f}" cy="{ty:.1f}" rx="{50 * k:.1f}" ry="{11 * k:.1f}" fill="url(#{u}-brass)"/>')
    out.append(f'<ellipse cx="{x:.1f}" cy="{ty:.1f}" rx="{42 * k:.1f}" ry="{8.6 * k:.1f}" fill="none" stroke="#8A5A1E" stroke-width="{1 * k:.1f}" stroke-dasharray="{2 * k:.1f} {1.6 * k:.1f}"/>')
    out.append(f'<ellipse cx="{x:.1f}" cy="{ty:.1f}" rx="{20 * k:.1f}" ry="{4 * k:.1f}" fill="none" stroke="#8A5A1E" stroke-width="{0.9 * k:.1f}"/>')
    # teapot: bulbous body, conical lid with finial, long curved spout, handle
    px, pb = x - 8 * k, ty + 2 * k
    out.append(f'<path d="M {px + 14 * k:.1f} {pb - 14 * k:.1f} C {px + 24 * k:.1f} {pb - 18 * k:.1f} {px + 30 * k:.1f} {pb - 30 * k:.1f} {px + 34 * k:.1f} {pb - 34 * k:.1f} L {px + 36 * k:.1f} {pb - 32 * k:.1f} C {px + 32 * k:.1f} {pb - 26 * k:.1f} {px + 26 * k:.1f} {pb - 12 * k:.1f} {px + 14 * k:.1f} {pb - 8 * k:.1f} Z" fill="#9AA0AE"/>')
    out.append(f'<path d="M {px - 13 * k:.1f} {pb - 20 * k:.1f} C {px - 26 * k:.1f} {pb - 22 * k:.1f} {px - 26 * k:.1f} {pb - 6 * k:.1f} {px - 13 * k:.1f} {pb - 8 * k:.1f}" fill="none" stroke="#7A808E" stroke-width="{2.6 * k:.1f}"/>')
    out.append(f'<path d="M {px - 10 * k:.1f} {pb:.1f} L {px + 10 * k:.1f} {pb:.1f} L {px + 8 * k:.1f} {pb - 3 * k:.1f} C {px + 18 * k:.1f} {pb - 8 * k:.1f} {px + 18 * k:.1f} {pb - 22 * k:.1f} {px + 6 * k:.1f} {pb - 26 * k:.1f} L {px - 6 * k:.1f} {pb - 26 * k:.1f} C {px - 18 * k:.1f} {pb - 22 * k:.1f} {px - 18 * k:.1f} {pb - 8 * k:.1f} {px - 8 * k:.1f} {pb - 3 * k:.1f} Z" fill="url(#{u}-silver)"/>')
    out.append(f'<path d="M {px - 7 * k:.1f} {pb - 26 * k:.1f} L {px + 7 * k:.1f} {pb - 26 * k:.1f} L {px + 2 * k:.1f} {pb - 38 * k:.1f} L {px - 2 * k:.1f} {pb - 38 * k:.1f} Z" fill="#B8BEC8"/>')
    out.append(f'<circle cx="{px:.1f}" cy="{pb - 40 * k:.1f}" r="{2.6 * k:.1f}" fill="#D8DCE4"/>')
    out.append(f'<path d="M {px - 13 * k:.1f} {pb - 14 * k:.1f} Q {px:.1f} {pb - 10 * k:.1f} {px + 13 * k:.1f} {pb - 14 * k:.1f}" fill="none" stroke="#6A7080" stroke-width="{1 * k:.1f}" stroke-dasharray="{1.6 * k:.1f} {1.2 * k:.1f}"/>')
    out.append(f'<path d="M {px - 9 * k:.1f} {pb - 22 * k:.1f} Q {px - 13 * k:.1f} {pb - 14 * k:.1f} {px - 8 * k:.1f} {pb - 6 * k:.1f}" fill="none" stroke="#FFFFFF" stroke-width="{2 * k:.1f}" opacity="0.8" stroke-linecap="round"/>')
    out.append(f'<path d="M {px + 10 * k:.1f} {pb - 20 * k:.1f} Q {px + 13 * k:.1f} {pb - 14 * k:.1f} {px + 9 * k:.1f} {pb - 6 * k:.1f}" fill="none" stroke="#FFD08A" stroke-width="{1.6 * k:.1f}" opacity="0.8" stroke-linecap="round"/>')
    # steam
    out.append(f'<path d="M {px + 35 * k:.1f} {pb - 36 * k:.1f} q {-4 * k:.1f} {-6 * k:.1f} 0 {-12 * k:.1f} q {4 * k:.1f} {-6 * k:.1f} 0 {-12 * k:.1f}" fill="none" stroke="#FFF6E8" stroke-width="{1.6 * k:.1f}" opacity="0.6" stroke-linecap="round"/>')
    # two tea glasses with gold patterns and green-amber tea, a sprig of mint
    for gx in (x + 24 * k, x + 36 * k):
        gb = ty + 4 * k if gx < x + 30 * k else ty + 1 * k
        out.append(f'<path d="M {gx - 4.4 * k:.1f} {gb - 15 * k:.1f} L {gx + 4.4 * k:.1f} {gb - 15 * k:.1f} L {gx + 3.4 * k:.1f} {gb:.1f} L {gx - 3.4 * k:.1f} {gb:.1f} Z" fill="#E8F0E0" opacity="0.6"/>')
        out.append(f'<path d="M {gx - 4 * k:.1f} {gb - 11 * k:.1f} L {gx + 4 * k:.1f} {gb - 11 * k:.1f} L {gx + 3.4 * k:.1f} {gb:.1f} L {gx - 3.4 * k:.1f} {gb:.1f} Z" fill="#B8862E"/>')
        out.append(f'<path d="M {gx - 3.8 * k:.1f} {gb - 8 * k:.1f} L {gx + 3.8 * k:.1f} {gb - 8 * k:.1f} L {gx + 3.6 * k:.1f} {gb - 4 * k:.1f} L {gx - 3.6 * k:.1f} {gb - 4 * k:.1f} Z" fill="#C8343A" opacity="0.8"/>')
        out.append(f'<path d="M {gx - 3.6 * k:.1f} {gb - 7 * k:.1f} L {gx + 3.6 * k:.1f} {gb - 7 * k:.1f}" stroke="#F2D080" stroke-width="{1 * k:.1f}" stroke-dasharray="{1 * k:.1f} {0.8 * k:.1f}"/>')
        out.append(f'<path d="M {gx - 2.4 * k:.1f} {gb - 14 * k:.1f} L {gx - 1.8 * k:.1f} {gb - 2 * k:.1f}" stroke="#FFFFFF" stroke-width="{1 * k:.1f}" opacity="0.8"/>')
    out.append(f'<path d="M {x + 24 * k:.1f} {ty - 11 * k:.1f} q {2 * k:.1f} {-6 * k:.1f} {6 * k:.1f} {-7 * k:.1f} q {-1 * k:.1f} {4 * k:.1f} {-6 * k:.1f} {7 * k:.1f} Z" fill="#4E9A3E"/>')
    out.append(f'<ellipse cx="{x + 32 * k:.1f}" cy="{ty + 5 * k:.1f}" rx="{4 * k:.1f}" ry="{1.6 * k:.1f}" fill="#3E8A3A"/><ellipse cx="{x + 28 * k:.1f}" cy="{ty + 6 * k:.1f}" rx="{3 * k:.1f}" ry="{1.4 * k:.1f}" fill="#5AAA4A"/>')
    # rim of warm light along the tray
    out.append(f'<path d="M {x - 50 * k:.1f} {ty:.1f} A {50 * k:.1f} {11 * k:.1f} 0 0 0 {x + 50 * k:.1f} {ty:.1f}" fill="none" stroke="#FFE2A0" stroke-width="{1.4 * k:.1f}" opacity="0.8"/>')
    return "".join(out)


def potted_palm(x, base, k, seed, pot="#C0603E", pot_lit="#E8905E"):
    """A terracotta pot with a young date palm: arching pinnate fronds."""
    rnd = random.Random(seed)
    out = [f'<path d="M {x - 16 * k:.1f} {base - 34 * k:.1f} L {x + 16 * k:.1f} {base - 34 * k:.1f} L {x + 11 * k:.1f} {base:.1f} L {x - 11 * k:.1f} {base:.1f} Z" fill="{pot}"/>',
           f'<path d="M {x + 6 * k:.1f} {base - 34 * k:.1f} L {x + 16 * k:.1f} {base - 34 * k:.1f} L {x + 11 * k:.1f} {base:.1f} L {x + 5 * k:.1f} {base:.1f} Z" fill="{pot_lit}" opacity="0.7"/>',
           f'<rect x="{x - 18 * k:.1f}" y="{base - 38 * k:.1f}" width="{36 * k:.1f}" height="{5 * k:.1f}" rx="{1.5 * k:.1f}" fill="{pot_lit}"/>',
           f'<path d="M {x - 13 * k:.1f} {base - 24 * k:.1f} L {x + 13 * k:.1f} {base - 24 * k:.1f}" stroke="#7A3424" stroke-width="{1.4 * k:.1f}" stroke-dasharray="{3 * k:.1f} {2 * k:.1f}"/>']
    fr = []
    for i in range(9):
        a = math.radians(-160 + i * 17 + rnd.uniform(-5, 5))
        L = rnd.uniform(40, 62) * k
        ex, ey = x + L * math.cos(a), base - 38 * k + L * math.sin(a) * 0.9
        mx, my = x + L * 0.5 * math.cos(a), base - 38 * k - L * 0.62 + abs(math.cos(a)) * L * 0.2
        col = rnd.choice(["#2E5A32", "#3E6E3A", "#4E7E3E"])
        fr.append(f'<path d="M {x:.1f} {base - 38 * k:.1f} Q {mx:.1f} {my:.1f} {ex:.1f} {ey:.1f}" stroke="{col}" stroke-width="{1.8 * k:.1f}" fill="none"/>')
        for j in range(1, 9):
            t = j / 9
            qx = (1 - t) ** 2 * x + 2 * (1 - t) * t * mx + t * t * ex
            qy = (1 - t) ** 2 * (base - 38 * k) + 2 * (1 - t) * t * my + t * t * ey
            ll = 9 * k * (1 - t * 0.6)
            fr.append(f'<path d="M {qx:.1f} {qy:.1f} l {-ll * 0.4:.1f} {ll:.1f} M {qx:.1f} {qy:.1f} l {ll * 0.4:.1f} {ll:.1f}" stroke="{col}" stroke-width="{1.4 * k:.1f}"/>')
    out.append(f'<g stroke-linecap="round">{"".join(fr)}</g>')
    return "".join(out)


def marrakech():
    u = "mrk"
    cx, cy, r, e, jh = 300, 268, 176, 12, 150
    floor = 444
    arch = horseshoe(cx, cy, r, e, jh, floor)
    inner = horseshoe(cx + 8, cy + 6, r - 12, e, jh - 10, floor)
    hz = 262
    out = [defs(
        lg(f"{u}-sky", [(0, "#3E7EC0"), (0.35, "#7AB2DA"), (0.62, "#C8D8D8"), (0.82, "#F6D6A8"), (1, "#F8C890")], 0, 90, 0, hz + 10, units="userSpaceOnUse"),
        lg(f"{u}-atl", [(0, "#A8A2CA"), (1, "#C8A8B8")], 0, 200, 0, hz + 10, units="userSpaceOnUse"),
        lg(f"{u}-wall", [(0, "#A8483A"), (0.5, "#B85640"), (1, "#8A3A30")], 0, 0, 1, 0),
        lg(f"{u}-wallr", [(0, "#9A4034"), (1, "#7E3028")], 0, 0, 1, 0),
        lg(f"{u}-sof", [(0, "#F0A070"), (0.5, "#C8684A"), (1, "#7A2E28")], 0, 0, 1, 0),
        lg(f"{u}-kf", [(0, "#C07E68"), (1, "#D49478")], 0, 0, 1, 0),
        lg(f"{u}-ks", [(0, "#F6C098"), (1, "#E8A880")], 0, 0, 1, 0),
        lg(f"{u}-par", [(0, "#D27858"), (1, "#A8503C")]),
        lg(f"{u}-brass", [(0, "#F6D27A"), (0.5, "#D8A440"), (1, "#A8742A")], 0, 0, 1, 0),
        lg(f"{u}-silver", [(0, "#8A90A0"), (0.4, "#E8ECF2"), (0.7, "#B8BECA"), (1, "#7A808E")], 0, 0, 1, 0),
        lg(f"{u}-floor", [(0, "#7A3A2E"), (1, "#4A2220")]),
        lg(f"{u}-wood", [(0, "#5A3420"), (1, "#3A2016")]),
        rg(f"{u}-warm", [(0, "#FFB878", 0.55), (1, "#FFB878", 0)], 0.5, 0.5, 0.5),
    )]
    # ---------------- the view through the arch
    view = []
    view.append(f'<rect x="0" y="0" width="600" height="444" fill="url(#{u}-sky)"/>')
    view.append(glow(560, 250, 260, "#FFD8A0", f"{u}-g1", 0.7))
    view.append(cumulus(f"{u}-c2", 446, 148, 64, 15, 5, "#FFF4E8", "#F8E0D4", "#D8C0CC", hi_op=0.4, light=1))
    # High Atlas: far snowy range with pink alpenglow on the west faces, then hazy foothills
    far = rough([(110, 246), (150, 226), (186, 236), (222, 208), (254, 222), (290, 200), (328, 218), (362, 206), (396, 226), (430, 214), (470, 232), (500, 228)], 7, amp=5, depth=3)
    view.append(Q(far + [(500, 300), (110, 300)], f"url(#{u}-atl)"))
    snow = []
    pk = [(222, 208), (290, 200), (362, 206), (430, 214), (150, 226)]
    for px, py in pk:
        sl = [(px - 30, py + 22), (px - 16, py + 12), (px - 8, py + 16), (px, py), (px + 10, py + 14), (px + 20, py + 10), (px + 34, py + 24), (px + 18, py + 20), (px + 6, py + 26), (px - 8, py + 22)]
        snow.append(Q(sl, "#F6F0F4"))
        snow.append(Q([(px, py), (px + 10, py + 14), (px + 20, py + 10), (px + 34, py + 24), (px + 18, py + 20), (px + 4, py + 10)], "#FFD8C8"))
    view.append(f'<clipPath id="{u}-atc"><polygon points="{P(far + [(500, 300), (110, 300)])}"/></clipPath><g clip-path="url(#{u}-atc)">' + "".join(snow) + "</g>")
    view.append(f'<polyline points="{P(far)}" fill="none" stroke="#FFE6DA" stroke-width="1.2" opacity="0.7"/>')
    poly, fh = ridge_poly([(110, 262), (180, 252), (260, 258), (340, 250), (420, 256), (500, 250)], 9, base=320, amp=3, fill="#C8949A")
    view.append(poly)
    view.append(mist(300, 266, 220, 18, "#F8DCC0", f"{u}-m1", 0.75))
    # the palm grove beyond the walls
    rnd = random.Random(12)
    for i in range(30):
        px = 110 + i * 13 + rnd.uniform(-5, 5)
        view.append(palm_sil(px, 280 + rnd.uniform(-2, 3), rnd.uniform(14, 24), "#8E7A76", seed=i))
    view.append(f'<rect x="100" y="276" width="420" height="12" fill="#D8A890" opacity="0.6"/>')
    # medina roofs: rows of flat-roofed houses, fronts in soft shade, west sides in sun
    rows = [(290, 0.5, "#D89C84", "#F2C09A"), (300, 0.62, "#D4927A", "#F4BC94"), (312, 0.76, "#CE8870", "#F6B88E"), (326, 0.9, "#C8806A", "#F8B48A"), (342, 1.05, "#C07662", "#FAB086"),
            (360, 1.22, "#B86E5C", "#FAAE84"), (380, 1.4, "#B0685A", "#FCAC82")]
    houses = []
    for ri, (yb, k, front, side) in enumerate(rows):
        x = 100 + rnd.uniform(-10, 0)
        while x < 510:
            w = rnd.uniform(18, 44) * k
            h = rnd.uniform(9, 20) * k
            yy = yb + rnd.uniform(-3, 3) * k
            sw = 5 * k
            houses.append(Q([(x + w, yy), (x + w, yy - h), (x + w + sw, yy - h - 2 * k), (x + w + sw, yy - 2 * k)], side))
            houses.append(f'<rect x="{x:.1f}" y="{yy - h:.1f}" width="{w:.1f}" height="{h + 30:.1f}" fill="{mix(front, "#B86A58", rnd.uniform(0, 0.4))}"/>')
            houses.append(f'<rect x="{x - 0.5:.1f}" y="{yy - h - 1.6 * k:.1f}" width="{w + 1:.1f}" height="{1.8 * k:.1f}" fill="{side}"/>')
            if rnd.random() < 0.45:
                dx_ = x + rnd.uniform(0.15, 0.7) * w
                houses.append(f'<path d="M {dx_:.1f} {yy:.1f} L {dx_:.1f} {yy - 5 * k:.1f} Q {dx_ + 1.6 * k:.1f} {yy - 7 * k:.1f} {dx_ + 3.2 * k:.1f} {yy - 5 * k:.1f} L {dx_ + 3.2 * k:.1f} {yy:.1f} Z" fill="#6A3A36"/>')
            if rnd.random() < 0.4:
                wx_ = x + rnd.uniform(0.1, 0.8) * w
                houses.append(f'<rect x="{wx_:.1f}" y="{yy - h * 0.7:.1f}" width="{2.4 * k:.1f}" height="{3 * k:.1f}" fill="#7A4440"/>')
            if rnd.random() < 0.12 and k > 0.7:  # laundry on a line
                lx = x + w * 0.2
                houses.append(f'<path d="M {lx:.1f} {yy - h - 8 * k:.1f} L {lx + w * 0.6:.1f} {yy - h - 7 * k:.1f}" stroke="#6A4040" stroke-width="0.8"/>')
                for j in range(3):
                    houses.append(f'<rect x="{lx + 3 * k + j * w * 0.18:.1f}" y="{yy - h - 8 * k + j * 0.3:.1f}" width="{4 * k:.1f}" height="{6 * k:.1f}" fill="{rnd.choice(["#2E6AB8", "#F2E8D8", "#D8402E", "#E8B83A"])}"/>')
            x += w + sw + rnd.uniform(-2, 3) * k
        if ri == 2:
            view.append("".join(houses))
            houses = []
            view.append(koutoubia(246, 314, 27, 134, u))
            for i, (px, s_) in enumerate(((176, 32), (296, 28), (440, 36), (468, 26))):
                view.append(palm_sil(px, 316, s_, "#4E6A44", seed=40 + i, lit="#9AAA5A"))
    view.append("".join(houses))
    view.append(mist(300, 300, 240, 12, "#F8D8B8", f"{u}-m2", 0.35))
    view.append(stork(318, 132, 0.55, flip=True))
    view.append(stork(292, 150, 0.4, flip=True))
    view.append(gulls([(180, 120, 7), (196, 128, 5)], "#5A4A6A", 1.5))
    # our terrace parapet beyond the arch, with stepped merlons and a cat taking the evening sun
    par_y = 396
    view.append(f'<rect x="100" y="{par_y}" width="420" height="{444 - par_y}" fill="url(#{u}-par)"/>')
    mer = []
    for i in range(14):
        mx = 112 + i * 30 + 0
        mer.append(f'<path d="M {mx - 9} {par_y} L {mx - 9} {par_y - 7} L {mx - 4} {par_y - 7} L {mx - 4} {par_y - 13} L {mx + 4} {par_y - 13} L {mx + 4} {par_y - 7} L {mx + 9} {par_y - 7} L {mx + 9} {par_y} Z"/>')
    view.append(f'<g fill="#C86A4E">{"".join(mer)}</g>')
    view.append(f'<g fill="#F2A878">' + "".join(f'<rect x="{112 + i * 30 + 2}" y="{par_y - 13}" width="2" height="13"/><rect x="{112 + i * 30 + 7}" y="{par_y - 7}" width="2" height="7"/>' for i in range(14)) + "</g>")
    view.append(f'<rect x="100" y="{par_y - 1}" width="420" height="3" fill="#F6B486"/>')
    view.append(streaks(40, 13, (100, par_y + 4, 520, 444), ["#8A3A2E", "#E08A64"], w=(2, 5), length=(10, 30), opacity=(0.15, 0.35), slant=0.1))
    # cat on the parapet, looking out over the roofs
    kx, ky = 368, par_y
    view.append(f'<g transform="translate({kx} {ky})"><path d="M -10 0 Q -14 -14 -8 -20 Q -6 -26 -4 -28 L -3 -34 L 0 -30 L 3 -34 L 4 -28 Q 8 -22 6 -14 Q 10 -6 8 0 Z" fill="#3A2622"/>'
                '<path d="M 8 0 Q 18 2 20 -6 Q 21 -10 18 -12" fill="none" stroke="#3A2622" stroke-width="2.6" stroke-linecap="round"/>'
                '<path d="M 4 -28 Q 8 -22 6 -14 Q 10 -6 8 0" fill="none" stroke="#FFC890" stroke-width="1.4"/><path d="M 3 -34 L 4 -28" stroke="#FFC890" stroke-width="1.2"/></g>')
    out.append(f'<clipPath id="{u}-in"><polygon points="{P(inner)}"/></clipPath>')
    # ---------------- the room: walls, soffit, view
    out.append(f'<rect width="600" height="444" fill="url(#{u}-wall)"/>')
    out.append(Q(arch, f"url(#{u}-sof)"))
    out.append(f'<g clip-path="url(#{u}-in)">' + "".join(view) + "</g>")
    # plaster texture on the walls (outside the arch)
    out.append(f'<clipPath id="{u}-wl"><path d="M 0 0 H 600 V 444 H 0 Z M {P(arch[::-1]).replace(" ", " L ")} Z" clip-rule="evenodd" fill-rule="evenodd"/></clipPath>')
    tex = blobs(70, 21, (0, 40, 600, 444), ["#C86048", "#8A3428", "#D87058"], r=(6, 22), opacity=(0.08, 0.2), squash=0.7)
    tex += streaks(50, 22, (0, 40, 600, 330), ["#7A2E26", "#D8785A"], w=(2, 6), length=(20, 70), opacity=(0.06, 0.16), slant=0.05)
    out.append(f'<g clip-path="url(#{u}-wl)">{tex}</g>')
    # carved stucco archivolt around the arch: a cream band with a scalloped edge and a dotted border
    band = horseshoe(cx, cy, r + 14, e, jh + 14, 330, 40)
    ring = f'M {P(band[1:-1]).replace(" ", " L ")} L {P(arch[-2:0:-1]).replace(" ", " L ")} Z'
    out.append(f'<path d="{ring}" fill="#E8D2B4"/>')
    out.append(f'<polyline points="{P(arch[1:-1])}" fill="none" stroke="#B88A6A" stroke-width="2"/>')
    scal = horseshoe(cx, cy, r + 7, e, jh + 7, 330, 40)
    out.append(f'<g fill="#C8A484">' + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6"/>' for x, y in scal[1:-1]) + "</g>")
    out.append(f'<g fill="#FFF0D8">' + "".join(f'<circle cx="{x - 0.6:.1f}" cy="{y - 0.8:.1f}" r="1.2"/>' for x, y in scal[1:-1]) + "</g>")
    out.append(f'<polyline points="{P(band[1:-1])}" fill="none" stroke="#9A6A4E" stroke-width="1.6"/>')
    # alfiz: the rectangular frame around the arch with an arabesque spandrel and a tile border
    ax0, ax1, ay0 = 96, 504, 74
    spand = f'M {ax0} {ay0} H {ax1} V 330 H {band[-2][0]:.1f} L {P(band[-2:0:-1]).replace(" ", " L ")} L {ax0} 330 Z'
    out.append(f'<path d="{spand}" fill="#D8BC9C"/>')
    out.append(f'<clipPath id="{u}-sp"><path d="{spand}"/></clipPath>')
    arab = []
    for yy in range(ay0 + 6, 330, 16):
        for xx in range(ax0 + 6, ax1, 16):
            arab.append(f'<path d="M {xx} {yy + 8} Q {xx + 4} {yy} {xx + 8} {yy + 8} Q {xx + 12} {yy + 16} {xx + 16} {yy + 8}"/>')
            arab.append(f'<circle cx="{xx + 8}" cy="{yy + 3}" r="1.6"/>')
    out.append(f'<g clip-path="url(#{u}-sp)" fill="none" stroke="#B8946E" stroke-width="1.6">{"".join(arab)}</g>')
    out.append(f'<g clip-path="url(#{u}-sp)"><rect x="{ax0}" y="{ay0}" width="{ax1 - ax0}" height="256" fill="#7A3A2A" opacity="0.18"/></g>')
    for (x0_, y0_, x1_, y1_) in ((ax0 - 10, ay0 - 10, ax1 + 10, ay0), (ax0 - 10, ay0, ax0, 330), (ax1, ay0, ax1 + 10, 330)):
        out.append(zellige(f"{u}-zb{x0_}{y0_}", (x0_, y0_, x1_, y1_), 10, x0_ + y0_))
    out.append(f'<rect x="{ax0 - 10}" y="{ay0 - 10}" width="{ax1 - ax0 + 20}" height="{330 - ay0 + 10}" fill="none" stroke="#3A1E18" stroke-width="1.6"/>')
    out.append(f'<rect x="{ax0}" y="{ay0}" width="{ax1 - ax0}" height="{330 - ay0}" fill="none" stroke="#3A1E18" stroke-width="1.2"/>')
    # carved cedar frieze across the top
    out.append(f'<rect x="0" y="0" width="600" height="58" fill="url(#{u}-wood)"/>')
    out.append(f'<rect x="0" y="54" width="600" height="4" fill="#2A140E"/>')
    out.append(f'<g fill="none" stroke="#8A5A36" stroke-width="1.6">' + "".join(
        f'<path d="M {x} 50 L {x + 8} 42 L {x + 16} 50 M {x + 8} 42 L {x + 8} 34"/><circle cx="{x + 8}" cy="30" r="3"/>' for x in range(-4, 610, 16)) + "</g>")
    out.append(f'<rect x="0" y="52" width="600" height="2" fill="#B8864E" opacity="0.6"/>')
    # zellige dado on both piers, with a chevron border on top
    for x0_, x1_ in ((-10, cx - jh - 14), (cx + jh + 14, 610)):
        out.append(zellige(f"{u}-zd{x0_ + 10}", (x0_, 342, x1_, 444), 30, x0_ + 50))
        out.append(f'<rect x="{x0_}" y="332" width="{x1_ - x0_}" height="10" fill="#F2E8D8"/>')
        out.append(f'<g fill="#1E4E9A">' + "".join(f'<path d="M {x} 342 L {x + 5} 333 L {x + 10} 342 Z"/>' for x in range(x0_, x1_, 10)) + "</g>")
        out.append(f'<rect x="{x0_}" y="330" width="{x1_ - x0_}" height="2.6" fill="#3A1E18"/><rect x="{x0_}" y="342" width="{x1_ - x0_}" height="2" fill="#3A1E18"/>')
    # shade on the inner faces of the piers next to the opening, warm light on the right pier
    out.append(f'<rect x="{cx - jh - 14 - 30}" y="332" width="30" height="112" fill="#3A1A16" opacity="0.25"/>')
    # the loggia floor in front of the arch
    out.append(Q([(-10, 424), (610, 424), (610, 444), (-10, 444)], f"url(#{u}-floor)"))
    out.append(Q([(cx - jh, 424), (cx + jh, 424), (cx + jh + 20, 444), (cx - jh - 30, 444)], "#F2B07A", ' opacity="0.35"'))
    # wall lantern on the left pier, a hanging lantern in the arch
    out.append(f'<path d="M 52 150 L 52 132 Q 52 124 62 124 L 78 124" fill="none" stroke="#3A2416" stroke-width="3"/>')
    out.append(lantern(52, 150, 1.05, f"{u}-l1", glow_r=110))
    out.append(f'<ellipse cx="52" cy="230" rx="70" ry="90" fill="url(#{u}-warm)"/>')
    out.append(lantern(cx + 74, 150, 1.0, f"{u}-l2", chain=60, glow_r=90))
    # foreground: tea on a brass tray, a potted palm on the right
    out.append(potted_palm(536, 436, 1.05, 3))
    out.append(tea_set(118, 440, 1.25, u))
    return "\n".join(out)


def palm_sil(x, base, h, col, seed=0, lit=None):
    """A small date palm: slim curving trunk and a ragged crown of drooping fronds."""
    rnd = random.Random(seed)
    lean = rnd.uniform(-0.12, 0.12)
    tx, ty = x + lean * h, base - h
    out = [f'<path d="M {x - 1.2:.1f} {base:.1f} Q {x + lean * h * 0.3:.1f} {base - h * 0.5:.1f} {tx - 0.8:.1f} {ty:.1f} L {tx + 0.8:.1f} {ty:.1f} Q {x + lean * h * 0.3 + 1.6:.1f} {base - h * 0.5:.1f} {x + 1.2:.1f} {base:.1f} Z" fill="{col}"/>']
    fr = []
    for i in range(9):
        a = math.radians(-180 + i * 22.5 + rnd.uniform(-8, 8))
        L = h * rnd.uniform(0.32, 0.45)
        ex, ey = tx + L * math.cos(a), ty + L * math.sin(a) * 0.5 + L * 0.35
        fr.append(f'<path d="M {tx:.1f} {ty:.1f} Q {tx + L * 0.6 * math.cos(a):.1f} {ty + L * 0.6 * math.sin(a) * 0.6 - L * 0.2:.1f} {ex:.1f} {ey:.1f}"/>')
    out.append(f'<g fill="none" stroke="{col}" stroke-width="{max(1.4, h * 0.07):.1f}" stroke-linecap="round">{"".join(fr)}</g>')
    if lit:
        out.append(f'<g fill="none" stroke="{lit}" stroke-width="{max(0.8, h * 0.03):.1f}" stroke-linecap="round" opacity="0.8">{"".join(fr[4:])}</g>')
    return "".join(out)


# ================================================================ PETRA — the Treasury glowing at the end of the Siq
def treasury(X, B, s, u):
    """Al-Khazneh, front elevation in morning sun from the upper right, drawn in local units (about 210 wide and
    306 tall) and scaled by s: a six-column portico with a pediment, an attic, then the upper order with the
    round tholos (conical roof, capital and urn) between two pavilions crowned by a broken pediment."""
    lit, wall, shade, deep, rim, line = "#F6B694", "#EBA084", "#C47466", "#7A3238", "#FFE0C4", "#9A4A48"
    g = [f'<g transform="translate({X:.1f} {B:.1f}) scale({s:.3f})">']

    def col(x, y0, y1, w, cap=True):
        r = [f'<rect x="{x - w / 2:.1f}" y="{y1:.1f}" width="{w:.1f}" height="{y0 - y1:.1f}" fill="{lit}"/>',
             f'<rect x="{x - w / 2:.1f}" y="{y1:.1f}" width="{w * 0.36:.1f}" height="{y0 - y1:.1f}" fill="{shade}"/>',
             f'<rect x="{x + w * 0.22:.1f}" y="{y1:.1f}" width="{w * 0.14:.1f}" height="{y0 - y1:.1f}" fill="{rim}" opacity="0.7"/>',
             f'<rect x="{x - w * 0.62:.1f}" y="{y0 - 3:.1f}" width="{w * 1.24:.1f}" height="3" fill="{wall}"/>']
        if cap:
            r.append(f'<path d="M {x - w * 0.5:.1f} {y1:.1f} L {x - w * 0.8:.1f} {y1 - 7:.1f} L {x + w * 0.8:.1f} {y1 - 7:.1f} L {x + w * 0.5:.1f} {y1:.1f} Z" fill="{wall}"/>'
                     f'<path d="M {x - w * 0.6:.1f} {y1 - 2:.1f} q {w * 0.3:.1f} -4 {w * 0.6:.1f} 0 q {w * 0.3:.1f} -4 {w * 0.6:.1f} 0" fill="none" stroke="{shade}" stroke-width="1.6"/>')
        return "".join(r)

    def cornice(x0, x1, y, h=6, over=3):
        return (f'<rect x="{x0 - over:.1f}" y="{y - h:.1f}" width="{x1 - x0 + 2 * over:.1f}" height="{h:.1f}" fill="{lit}"/>'
                f'<rect x="{x0 - over:.1f}" y="{y:.1f}" width="{x1 - x0 + 2 * over:.1f}" height="2.6" fill="{deep}" opacity="0.75"/>'
                f'<rect x="{x0 - over:.1f}" y="{y - h:.1f}" width="{x1 - x0 + 2 * over:.1f}" height="1.4" fill="{rim}"/>')

    def statue(x, y, h):
        return (f'<path d="M {x - h * 0.16:.1f} {y:.1f} L {x - h * 0.12:.1f} {y - h * 0.7:.1f} Q {x:.1f} {y - h * 0.8:.1f} {x + h * 0.12:.1f} {y - h * 0.7:.1f} L {x + h * 0.18:.1f} {y:.1f} Z" fill="{shade}"/>'
                f'<circle cx="{x:.1f}" cy="{y - h * 0.82:.1f}" r="{h * 0.1:.1f}" fill="{shade}"/>'
                f'<path d="M {x + h * 0.12:.1f} {y - h * 0.7:.1f} L {x + h * 0.18:.1f} {y:.1f}" stroke="{wall}" stroke-width="1.6"/>')

    # ---- lower storey
    g.append(f'<rect x="-100" y="-160" width="200" height="160" fill="{wall}"/>')
    g.append(f'<rect x="-62" y="-128" width="124" height="120" fill="{deep}"/>')
    g.append(f'<rect x="-62" y="-128" width="124" height="16" fill="#5A2028" opacity="0.7"/>')
    g.append(f'<path d="M -14 -8 L -14 -72 L 14 -72 L 14 -8 Z" fill="#3A161C"/><path d="M -18 -72 L 18 -72 L 18 -78 L -18 -78 Z" fill="{shade}"/><path d="M -20 -80 L 0 -90 L 20 -80 Z" fill="{shade}"/>')
    g.append(f'<rect x="-12" y="-70" width="3" height="62" fill="#6A2A30"/>')
    # Dioscuri reliefs in the outer bays (worn by wind and water)
    for sx in (-1, 1):
        bx = sx * 74
        g.append(f'<rect x="{bx - 10:.1f}" y="-112" width="20" height="58" fill="{shade}" opacity="0.5"/>')
        g.append(f'<path d="M {bx - 8:.1f} -58 Q {bx - 6:.1f} -76 {bx + 2:.1f} -78 Q {bx + 8:.1f} -76 {bx + 9:.1f} -64 L {bx + 6:.1f} -58 Z" fill="{shade}"/>'
                 f'<path d="M {bx - 2:.1f} -78 L {bx - 1:.1f} -100 Q {bx + 1:.1f} -106 {bx + 3:.1f} -100 L {bx + 3:.1f} -78 Z" fill="{shade}"/><circle cx="{bx + 1:.1f}" cy="-104" r="3" fill="{shade}"/>')
    for x in (-16, 16, -44, 44, -88, 88):
        g.append(col(x, -6, -126, 12))
    g.append(f'<rect x="-106" y="-8" width="212" height="8" fill="{wall}"/><rect x="-106" y="-8" width="212" height="1.6" fill="{rim}"/>')
    g.append(f'<rect x="-110" y="-3" width="220" height="3" fill="{shade}"/>')
    # entablature: architrave, frieze with vine scrolls, cornice
    g.append(f'<rect x="-102" y="-142" width="204" height="9" fill="{lit}"/><rect x="-102" y="-134" width="204" height="2.4" fill="{deep}" opacity="0.7"/>')
    g.append(f'<rect x="-102" y="-154" width="204" height="12" fill="{wall}"/>')
    g.append(f'<g fill="none" stroke="{shade}" stroke-width="1.4">' + "".join(f'<path d="M {x} -148 q 4 -5 8 0 q 4 5 8 0"/>' for x in range(-98, 98, 16)) + "</g>")
    g.append(f'<g fill="{shade}">' + "".join(f'<circle cx="{x + 8}" cy="-148" r="1.6"/>' for x in range(-98, 98, 16)) + "</g>")
    g.append(cornice(-102, 102, -154, 6, 4))
    # pediment over the central four columns, with acroteria
    g.append(f'<path d="M -66 -160 L 0 -188 L 66 -160 Z" fill="{wall}"/>')
    g.append(f'<path d="M -58 -162 L 0 -184 L 58 -162 Z" fill="{shade}" opacity="0.45"/>')
    g.append(f'<g fill="none" stroke="{shade}" stroke-width="1.4"><path d="M -20 -168 q 6 -8 12 0 q 6 8 12 0 q 6 -8 12 0"/></g><circle cx="0" cy="-172" r="3.4" fill="{lit}"/>')
    g.append(f'<path d="M -70 -159 L 0 -190 L 70 -159" fill="none" stroke="{lit}" stroke-width="4"/><path d="M 0 -190 L 70 -159" fill="none" stroke="{rim}" stroke-width="1.6"/>')
    g.append(f'<path d="M -66 -158 L 66 -158" stroke="{deep}" stroke-width="2"/>')
    for ax, ay in ((0, -192), (-68, -162), (68, -162)):
        g.append(f'<path d="M {ax - 4} {ay} L {ax - 3} {ay - 10} Q {ax} {ay - 14} {ax + 3} {ay - 10} L {ax + 4} {ay} Z" fill="{lit}"/>')
    # attic band behind the pediment
    g.append(f'<rect x="-104" y="-176" width="38" height="16" fill="{wall}"/><rect x="66" y="-176" width="38" height="16" fill="{wall}"/>')
    g.append(cornice(-104, -66, -176, 4, 2) + cornice(66, 104, -176, 4, 2))
    # ---- upper storey
    U0 = -180  # base of the upper columns
    g.append(f'<rect x="-104" y="-250" width="208" height="{-180 + 250}" fill="{wall}"/>')
    g.append(f'<rect x="-40" y="-246" width="16" height="66" fill="{deep}"/><rect x="24" y="-246" width="16" height="66" fill="{deep}"/>')
    # pavilions: two columns each, statues between them, entablature and the broken pediment rising toward the tholos
    for sx in (-1, 1):
        g.append(f'<rect x="{-96 if sx < 0 else 54}" y="-238" width="42" height="56" fill="{shade}" opacity="0.55"/>')
        g.append(statue(sx * 72, -184, 44))
        for x in (sx * 50, sx * 94):
            g.append(col(x, U0, -238, 10))
        g.append(f'<rect x="{-106 if sx < 0 else 40}" y="-252" width="66" height="8" fill="{lit}"/><rect x="{-106 if sx < 0 else 40}" y="-245" width="66" height="2.4" fill="{deep}" opacity="0.7"/>')
        hp = [(sx * 40, -254), (sx * 40, -284), (sx * 108, -254)]
        g.append(Q(hp, wall))
        g.append(Q([(sx * 44, -256), (sx * 44, -278), (sx * 98, -256)], shade, ' opacity="0.4"'))
        g.append(f'<path d="M {sx * 40} -286 L {sx * 110} -253" stroke="{lit}" stroke-width="4"/>')
        if sx > 0:
            g.append(f'<path d="M 40 -287 L 110 -254" stroke="{rim}" stroke-width="1.6"/>')
        g.append(f'<path d="M {sx * 40} -254 L {sx * 108} -254" stroke="{deep}" stroke-width="2"/>')
        g.append(f'<path d="M {sx * 106 - 4} -254 L {sx * 106 - 3} -264 Q {sx * 106} -268 {sx * 106 + 3} -264 L {sx * 106 + 4} -254 Z" fill="{lit}"/>')
    # tholos: drum, four columns with statues between, round entablature, conical roof, capital and urn
    g.append(f'<rect x="-24" y="-246" width="48" height="66" fill="{wall}"/>')
    g.append(f'<rect x="-24" y="-246" width="16" height="66" fill="{shade}" opacity="0.6"/>')
    g.append(statue(0, -184, 46))
    for x in (-20, -7, 7, 20):
        g.append(col(x, U0, -240, 6 if abs(x) < 10 else 7))
    g.append(f'<path d="M -27 -256 L 27 -256 L 27 -246 Q 0 -240 -27 -246 Z" fill="{lit}"/><path d="M -27 -246 Q 0 -240 27 -246" fill="none" stroke="{deep}" stroke-width="2"/>')
    g.append(f'<path d="M -29 -256 Q 0 -262 29 -256 L 0 -290 Z" fill="{wall}"/><path d="M 0 -290 L 29 -256 Q 14 -259 6 -260 Z" fill="{lit}"/><path d="M 0 -290 L -29 -256 Q -16 -259 -10 -260 Z" fill="{shade}"/>')
    g.append(f'<path d="M 0 -290 L 29 -256" stroke="{rim}" stroke-width="1.4"/>')
    g.append(f'<path d="M -6 -290 L 6 -290 L 8 -298 L -8 -298 Z" fill="{lit}"/>')
    g.append(f'<path d="M -3 -298 L -4 -302 Q -10 -306 -9 -312 Q -7 -320 0 -320 Q 7 -320 9 -312 Q 10 -306 4 -302 L 3 -298 Z" fill="{wall}"/>'
             f'<path d="M 2 -319 Q 8 -316 8 -310" fill="none" stroke="{rim}" stroke-width="1.4"/><rect x="-3" y="-325" width="6" height="5" fill="{lit}"/>')
    g.append(f'<g fill="{deep}" opacity="0.7"><circle cx="-3" cy="-311" r="1"/><circle cx="2" cy="-308" r="0.9"/><circle cx="-1" cy="-315" r="0.8"/></g>')
    # erosion: soft vertical washes and pitting across the whole facade
    g.append(f'<clipPath id="{u}-tc"><rect x="-112" y="-330" width="224" height="330"/></clipPath><g clip-path="url(#{u}-tc)">'
             + streaks(40, 3, (-110, -320, 110, -10), ["#C8786A", "#FFD0B0", "#B86060"], w=(1.5, 4), length=(16, 60), opacity=(0.12, 0.3), slant=0.05)
             + blobs(70, 4, (-110, -320, 110, -10), ["#B86A60", "#FFD8BC"], r=(1, 3), opacity=(0.2, 0.45), squash=0.8) + "</g>")
    g.append("</g>")
    return "".join(g)


def petra():
    u = "ptr"
    X, B, s = 306, 398, 0.92
    out = [defs(
        lg(f"{u}-sky", [(0, "#2E6AB8"), (1, "#8EC2E6")], 0, 40, 0, 200, units="userSpaceOnUse"),
        lg(f"{u}-rock", [(0, "#E89A80"), (0.6, "#D8826E"), (1, "#C06A5E")], 0, 40, 0, 400, units="userSpaceOnUse"),
        lg(f"{u}-wl", [(0, "#4A1E28"), (0.55, "#6A2A30"), (0.85, "#8A3A38"), (1, "#A84E42")], 0, 0, 1, 0),
        lg(f"{u}-wr", [(0, "#A04840"), (0.15, "#7A3034"), (1, "#3E1820")], 0, 0, 1, 0),
        lg(f"{u}-plaza", [(0, "#F2B48E"), (1, "#E09A7A")], 0, 380, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-floor", [(0, "#5A2A2E"), (1, "#2E1418")], 0, 400, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-spill", [(0, "#F8B890", 0.55), (1, "#F8B890", 0)], 0, 400, 0, 444, units="userSpaceOnUse"),
    )]
    # sky and the sunlit cliff the Treasury is carved into
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    cliff = rough([(150, 80), (200, 60), (260, 54), (330, 50), (400, 62), (470, 74)], 2, amp=6, depth=3)
    out.append(Q(cliff + [(470, 444), (150, 444)], f"url(#{u}-rock)"))
    out.append(f'<clipPath id="{u}-cc"><polygon points="{P(cliff + [(470, 444), (150, 444)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-cc)">' + streaks(70, 5, (150, 50, 470, 420), ["#B8605A", "#FFC8A8", "#A8504E", "#F0A884"], w=(2, 7), length=(30, 110), opacity=(0.15, 0.4), slant=0.08)
               + "".join(f'<path d="M 140 {y} Q 220 {y - 14} 300 {y + 4} T 480 {y - 6}" fill="none" stroke="{c}" stroke-width="{w}" opacity="0.25"/>' for y, c, w in
                         ((96, "#C8705E", 5), (120, "#FFD0B0", 3), (150, "#B0585A", 6), (300, "#FFD0B0", 3), (340, "#C0685A", 5)))
               + "</g>")
    # footholds cut up both sides of the facade
    for sx in (-1, 1):
        fx = X + sx * 118
        out.append(f'<g fill="#9A4A48" opacity="0.7">' + "".join(f'<rect x="{fx - 3:.1f}" y="{y}" width="6" height="3.4"/>' for y in range(112, 380, 14)) + "</g>")
    out.append(treasury(X, B, s, u))
    # plaza in sun, figures at the foot of the Treasury for scale
    out.append(Q([(130, B - 4), (480, B - 4), (480, 444), (130, 444)], f"url(#{u}-plaza)"))
    out.append(dots(90, 8, (150, B, 470, 444), "#B8706A", r=(0.6, 1.6), opacity=(0.25, 0.5)))
    out.append(f'<rect x="{X - 106 * s:.1f}" y="{B - 4:.1f}" width="{212 * s:.1f}" height="4" fill="#B86A60" opacity="0.6"/>')
    for fx, fh, c, hd in ((258, 22, "#2E5A8A", "#3A221E"), (270, 21, "#F2E2C8", "#5A3A2A"), (352, 20, "#C83A3A", "#2A1A1A"), (366, 22, "#3E6A4A", "#C8B8A0"), (330, 19, "#E8B030", "#3A221E")):
        out.append(f'<ellipse cx="{fx - 6:.1f}" cy="{B + 6:.1f}" rx="7" ry="1.6" fill="#8A4A48" opacity="0.5"/>')
        out.append(figure(fx, B + 6, fh, c, head=hd, legs="#3A2A2E", rim="#FFE2C8", rim_side=1))
    # the Siq: towering walls of banded sandstone in shade, warm bounce light on the edges facing the gap
    left = [(-10, 40), (262, 40), (252, 64), (260, 92), (244, 120), (232, 160), (240, 196), (220, 232), (206, 270), (212, 306), (192, 344), (176, 384), (160, 420), (150, 444), (-10, 444)]
    right = [(610, 40), (350, 40), (362, 70), (354, 100), (370, 134), (384, 176), (376, 212), (398, 248), (410, 290), (404, 326), (424, 364), (446, 404), (466, 444), (610, 444)]
    for side, poly, grad in (("l", left, f"url(#{u}-wl)"), ("r", right, f"url(#{u}-wr)")):
        out.append(Q(poly, grad))
        out.append(f'<clipPath id="{u}-{side}"><polygon points="{P(poly)}"/></clipPath>')
        bands = []
        rnd = random.Random(30 if side == "l" else 31)
        for i in range(30):
            y0 = 20 + i * 15 + rnd.uniform(-5, 5)
            amp = rnd.uniform(6, 26)
            per = rnd.uniform(45, 120)
            c = rnd.choice(["#8A3A3E", "#5A2230", "#A8504A", "#6A2A40", "#C06A50", "#7A3A5A", "#D88A60", "#4A1A28"])
            sw = rnd.uniform(2, 12)
            ph = rnd.uniform(0, 300)
            slope = rnd.uniform(0.1, 0.3) * (1 if side == "l" else -1)
            pts = [(x, y0 + amp * math.sin((x + ph) / per) + amp * 0.4 * math.sin((x + ph) / (per * 0.37)) + (x - 300) * slope) for x in range(-20, 640, 12)]
            bands.append(f'<polyline points="{P(pts)}" fill="none" stroke="{c}" stroke-width="{sw:.1f}" opacity="{rnd.uniform(0.2, 0.5):.2f}" stroke-linejoin="round"/>')
        # the rounded mass of the wall: lighter where it bulges toward the gap, darker deep inside
        inner = poly[1:-1]
        dirx = 1 if side == "l" else -1
        for off, w, c, op in ((-14, 30, "#C06450", 0.25), (-44, 40, "#5A1E2A", 0.3), (-110, 70, "#2A0E18", 0.35)):
            pts = [(x + dirx * off, y) for x, y in inner]
            bands.append(f'<polyline points="{P(pts)}" fill="none" stroke="{c}" stroke-width="{w}" opacity="{op}" stroke-linejoin="round"/>')
        bands.append(streaks(40, 33 if side == "l" else 34, (-10, 40, 610, 444), ["#2A1018", "#B8604E"], w=(2, 6), length=(30, 90), opacity=(0.12, 0.3), slant=0.05))
        out.append(f'<g clip-path="url(#{u}-{side})">{"".join(bands)}</g>')
        edge = poly[1:-1] if side == "l" else poly[1:-1]
        out.append(f'<polyline points="{P(edge)}" fill="none" stroke="#F09A7A" stroke-width="10" opacity="0.22" stroke-linejoin="round"/>')
        out.append(f'<polyline points="{P(edge)}" fill="none" stroke="#FFC0A0" stroke-width="2.4" opacity="0.7" stroke-linejoin="round"/>')
    # a few tufts of greenery clinging in the cracks, and a swift overhead
    out.append(grass(10, 42, (366, 174, 378, 178), ["#3E4A2E", "#5A6A3A"], h=(5, 10), sw=1.4))
    out.append(gulls([(296, 76, 8), (318, 88, 6)], "#2A2A4A", 1.6))
    # the Siq floor in shade with the light spilling in from the plaza
    floor = [(-10, 424), (150, 420), (466, 420), (610, 426), (610, 444), (-10, 444)]
    out.append(Q(floor, f"url(#{u}-floor)"))
    out.append(Q([(160, 420), (460, 420), (560, 444), (40, 444)], f"url(#{u}-spill)"))
    out.append(dots(60, 51, (0, 424, 600, 444), "#8A4A48", r=(0.6, 1.6), opacity=(0.3, 0.6)))
    # a camel and its Bedouin guide coming back out of the Siq, rim-lit by the plaza behind them
    out.append(f'<ellipse cx="226" cy="441" rx="70" ry="3.4" fill="#1E0A10" opacity="0.5"/>')
    out.append(camel(214, 440, 0.78, blanket="#C8343A", tassel="#E8B040", rim="#FFC8A0", body="#4A2A2A", far="#2E181C", step=1))
    out.append(figure(170, 441, 44, "#2A2430", head="#3A2420", legs="#1E1418", rim="#FFC8A0", rim_side=1))
    out.append(f'<path d="M 164.5 399 Q 164 392 170 391.5 Q 176 392 175.5 399 L 177 410 L 172 404 L 166 404 Z" fill="#E8E0D8"/>'
               f'<g stroke="#C8343A" stroke-width="1.2"><path d="M 165 396 L 175 396"/><path d="M 165 400 L 175 400"/><path d="M 166 394 L 168 404 M 170 392 L 170 404 M 174 394 L 172 404"/></g>'
               f'<rect x="165" y="395" width="10" height="1.8" fill="#1E1418"/>')
    out.append(f'<path d="M 176 418 Q 190 424 198 420" stroke="#2A1E1A" stroke-width="1.2" fill="none"/>')
    return "\n".join(out)


# ================================================================ CAPE TOWN — Table Mountain under its tablecloth, from the harbour
def seal(x, base, k, flip=False, head_up=True, body="#3E2C26", lit="#9A8478", belly="#5A443A"):
    """Cape fur seal hauled out on a pontoon: long tapering body, fore-flippers, a raised pointed head with
    tiny ears and whiskers, a wet sheen along the back."""
    sx = -k if flip else k
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({sx:.3f} {k:.3f})">']
    g.append(f'<ellipse cx="0" cy="1" rx="44" ry="4" fill="#1A2A34" opacity="0.35"/>')
    if head_up:
        g.append(f'<path d="M 40 -2 Q 46 -6 52 -4 L 50 0 Z" fill="{body}"/>'
                 f'<path d="M 44 -2 C 30 -6 10 -10 -6 -16 C -16 -20 -22 -30 -22 -38 C -22 -44 -26 -50 -32 -52 C -38 -53 -42 -50 -44 -46 L -48 -42 L -42 -40 C -40 -34 -36 -26 -34 -18 C -30 -6 -20 0 -4 0 Z" fill="{body}"/>')
        g.append(f'<path d="M -34 -18 C -30 -8 -22 -2 -6 -1 C -18 -6 -26 -12 -30 -22 Z" fill="{belly}"/>')
        g.append(f'<path d="M -26 -16 Q -30 -6 -22 0 L -14 0 Q -22 -6 -20 -14 Z" fill="{mix(body, "#000000", 0.25)}"/>')
        g.append(f'<path d="M -40 -50 Q -32 -54 -26 -46 Q -22 -40 -22 -32 Q -16 -18 6 -12 Q 24 -7 42 -3" fill="none" stroke="{lit}" stroke-width="2.4" stroke-linecap="round"/>')
        g.append(f'<circle cx="-38" cy="-47" r="1.6" fill="#120A08"/><circle cx="-38.5" cy="-47.5" r="0.5" fill="#FFFFFF"/>'
                 f'<path d="M -32 -52 l 1 -4 l 2 3.4" fill="{body}"/>'
                 f'<g stroke="#D8D0C8" stroke-width="0.7" opacity="0.8"><line x1="-45" y1="-42" x2="-54" y2="-44"/><line x1="-45" y1="-41" x2="-54" y2="-40"/></g>')
    else:
        g.append(f'<path d="M 44 -2 Q 48 -6 54 -4 L 52 0 Z" fill="{body}"/><path d="M 44 -2 C 30 -10 10 -16 -10 -16 C -24 -16 -34 -12 -40 -6 L -48 -4 L -46 0 L -4 0 Z" fill="{body}"/>'
                 f'<path d="M -40 -8 C -30 -14 -14 -16 0 -15 C 16 -14 30 -9 42 -3" fill="none" stroke="{lit}" stroke-width="2.2" stroke-linecap="round"/>'
                 f'<circle cx="-38" cy="-8" r="1.4" fill="#120A08"/><path d="M -10 -2 Q -14 4 -4 3 Z" fill="{mix(body, "#000000", 0.25)}"/>')
    g.append("</g>")
    return "".join(g)


def trawler(x, wl, k, hull="#C8342E", flip=False):
    """Small harbour fishing boat: raked bow, red hull with a dark boot-top, white wheelhouse, a mast with
    derrick booms, a tyre fender or two."""
    sx = -k if flip else k
    return (f'<g transform="translate({x:.1f} {wl:.1f}) scale({sx:.3f} {k:.3f})">'
            '<path d="M -60 -26 L 56 -26 L 70 -36 L 66 -20 Q 60 0 40 2 L -48 2 Q -58 -6 -60 -26 Z" fill="' + hull + '"/>'
            '<path d="M -56 -6 Q -50 2 -48 2 L 40 2 Q 54 0 62 -8 Z" fill="#22242E"/>'
            '<path d="M -60 -26 L 56 -26 L 70 -36 L 69 -32 L 56 -23 L -59 -23 Z" fill="#F2ECE4"/>'
            '<rect x="-30" y="-52" width="34" height="26" fill="#F2ECE4"/><rect x="-30" y="-52" width="10" height="26" fill="#C8C6D0"/>'
            '<rect x="-34" y="-56" width="42" height="5" fill="#2E5A8A"/>'
            '<g fill="#2A3A4E"><rect x="-17" y="-47" width="6" height="7"/><rect x="-8" y="-47" width="6" height="7"/><rect x="-26" y="-47" width="5" height="7"/></g>'
            '<line x1="24" y1="-26" x2="24" y2="-86" stroke="#4A4048" stroke-width="2.4"/><line x1="24" y1="-80" x2="56" y2="-34" stroke="#4A4048" stroke-width="1.4"/>'
            '<line x1="24" y1="-72" x2="-4" y2="-56" stroke="#4A4048" stroke-width="1.2"/><path d="M 24 -86 L 34 -82 L 24 -78 Z" fill="#F2C040"/>'
            '<circle cx="-40" cy="-14" r="4" fill="none" stroke="#22242E" stroke-width="2.4"/><circle cx="10" cy="-14" r="4" fill="none" stroke="#22242E" stroke-width="2.4"/>'
            '<g fill="#F2ECE4"><rect x="-44" y="-20" width="2" height="2"/></g>'
            '<path d="M -60 -26 L 56 -26 L 70 -36" fill="none" stroke="#FFF6E0" stroke-width="1.6"/></g>')


def bokaap_house(x, base, w, h, wall, rnd, k=1.0):
    """Bo-Kaap cottage: flat roof behind a moulded parapet (some with a little curved gable), a stoep step,
    a green or brown door, sash windows with white frames; the east side catches the morning sun."""
    out = [f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{wall}"/>',
           f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w * 0.18:.1f}" height="{h:.1f}" fill="#FFFFFF" opacity="0.22"/>',
           f'<rect x="{x + w * 0.82:.1f}" y="{base - h:.1f}" width="{w * 0.18:.1f}" height="{h:.1f}" fill="#000000" opacity="0.12"/>',
           f'<rect x="{x - 0.6:.1f}" y="{base - h - 1.8 * k:.1f}" width="{w + 1.2:.1f}" height="{2.2 * k:.1f}" fill="{mix(wall, "#FFFFFF", 0.45)}"/>']
    if rnd.random() < 0.4:
        out.append(f'<path d="M {x + w * 0.3:.1f} {base - h - 1.6 * k:.1f} Q {x + w * 0.3:.1f} {base - h - 6 * k:.1f} {x + w * 0.5:.1f} {base - h - 6.5 * k:.1f} Q {x + w * 0.7:.1f} {base - h - 6 * k:.1f} {x + w * 0.7:.1f} {base - h - 1.6 * k:.1f} Z" fill="{mix(wall, "#FFFFFF", 0.3)}"/>')
    door = rnd.choice(["#2E5A3A", "#5A3A2A", "#1E3A5A"])
    dw = 3.4 * k
    dx = x + w * rnd.uniform(0.2, 0.6)
    out.append(f'<rect x="{dx:.1f}" y="{base - 7.5 * k:.1f}" width="{dw:.1f}" height="{7.5 * k:.1f}" fill="{door}"/>')
    for wx in (x + w * 0.12, x + w * 0.72):
        if abs(wx - dx) > dw + 1 and wx + 3 * k < x + w:
            out.append(f'<rect x="{wx:.1f}" y="{base - h * 0.62:.1f}" width="{2.8 * k:.1f}" height="{4 * k:.1f}" fill="#F6F2EA"/><rect x="{wx + 0.6 * k:.1f}" y="{base - h * 0.62 + 0.6 * k:.1f}" width="{1.6 * k:.1f}" height="{2.8 * k:.1f}" fill="#3A4A5A"/>')
    out.append(f'<rect x="{x - 1:.1f}" y="{base - 1.2 * k:.1f}" width="{w + 2:.1f}" height="{1.4 * k:.1f}" fill="#8A8A90"/>')
    return "".join(out)


def cape_town():
    u = "cpt"
    wl = 316
    out = [defs(
        lg(f"{u}-sky", [(0, "#2C68B4"), (0.45, "#5E9AD4"), (0.8, "#A8D0EC"), (1, "#D8ECF4")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#7AAAC8"), (0.12, "#3E7EA8"), (0.5, "#245E8A"), (1, "#163E64")], 0, wl, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-face", [(0, "#C8B8A8"), (0.45, "#A89C98"), (1, "#7E7A86")], 0, 0, 1, 0),
        lg(f"{u}-slope", [(0, "#6E8458"), (1, "#4A6248")], 0, 190, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-dev", [(0, "#A0A4AE"), (0.4, "#8A9488"), (1, "#6A7C62")], 0, 140, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-lion", [(0, "#8E8C7A"), (0.5, "#6E7A5A"), (1, "#56704A")], 0, 170, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-tc", [(0, "#FFFFFF", 0.95), (0.4, "#F4F8FC", 0.75), (1, "#EEF2F8", 0)]),
        lg(f"{u}-bank", [(0, "#FFFFFF"), (0.6, "#F2F4F8"), (1, "#D4DCE8")], 0, 0, 1, 0),
        lg(f"{u}-quay", [(0, "#A8A098"), (1, "#6A6460")]),
        lg(f"{u}-pont", [(0, "#6A6A70"), (1, "#3E3E46")]),
    )]
    out.append(f'<rect width="600" height="{wl + 1}" fill="url(#{u}-sky)"/>')
    out.append(glow(40, 70, 260, "#FFF6D8", f"{u}-g1", 0.6))
    out.append(cumulus(f"{u}-c1", 560, 104, 90, 22, 4, "#FFFFFF", "#EEF2F8", "#C8D2E2", light=-1))
    out.append(cumulus(f"{u}-c2", 70, 86, 60, 14, 6, "#FFFFFF", "#EEF2F8", "#C8D2E2", light=-1))
    # Devil's Peak, slightly hazier, on the left
    dev = rough([(-10, 256), (16, 218), (36, 182), (50, 160), (60, 148), (70, 156), (88, 162), (106, 166), (126, 162)], 3, amp=2, depth=2)
    out.append(Q(dev + [(126, 320), (-10, 320)], f"url(#{u}-dev)"))
    out.append(f'<clipPath id="{u}-dv"><polygon points="{P(dev + [(126, 320), (-10, 320)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-dv)">' + streaks(14, 3, (-10, 150, 126, 240), ["#6A7088", "#C8CCD8"], w=(2, 4), length=(14, 40), opacity=(0.15, 0.35), slant=0.3)
               + f'<polygon points="{P([(60, 148), (70, 156), (88, 162), (106, 166), (126, 162), (126, 320), (64, 320)])}" fill="#5E6478" opacity="0.35"/>'
               + blobs(40, 4, (-10, 200, 126, 300), ["#5A7050", "#7A8A60"], r=(3, 7), opacity=(0.3, 0.6)) + "</g>")
    out.append(f'<polyline points="{P(dev[:len(dev) // 2 + 2])}" fill="none" stroke="#FFF2DC" stroke-width="1.6" opacity="0.8"/>')
    # Table Mountain: the level plateau, the sheer sandstone face with buttresses and gullies, Platteklip Gorge
    top = rough([(116, 152), (200, 148), (290, 150), (370, 146), (446, 149)], 5, amp=1.5, depth=3)
    face_bot = rough([(110, 214), (180, 206), (250, 216), (330, 204), (410, 210), (470, 222)], 7, amp=6, depth=3)
    massif = [(100, 160)] + top + [(456, 158), (470, 186), (486, 214), (510, 240), (540, 270), (540, 320), (100, 320)]
    out.append(Q(massif, f"url(#{u}-slope)"))
    face = [(104, 158)] + top + [(456, 158), (468, 184), (474, 222)] + face_bot[::-1]
    out.append(Q(face, f"url(#{u}-face)"))
    out.append(f'<clipPath id="{u}-fc"><polygon points="{P(face)}"/></clipPath>')
    rnd = random.Random(17)
    fc = []
    x = 104
    while x < 476:
        w = rnd.uniform(5, 14)
        yb = (y_on(face_bot, x) or 210) + rnd.uniform(-14, 6)
        fc.append(f'<rect x="{x:.1f}" y="140" width="{w * 0.45:.1f}" height="{yb - 140:.1f}" fill="#6A6878" opacity="{rnd.uniform(0.25, 0.5):.2f}"/>')
        fc.append(f'<rect x="{x + w * 0.45:.1f}" y="140" width="{w * 0.25:.1f}" height="{yb - 140 - rnd.uniform(0, 20):.1f}" fill="#F2E2C8" opacity="{rnd.uniform(0.2, 0.45):.2f}"/>')
        x += w
    for y in (166, 176, 190, 198):
        fc.append(f'<polyline points="{P(rough([(100, y), (300, y - 3), (480, y + 2)], y, amp=2, depth=3))}" fill="none" stroke="#5E5A68" stroke-width="1.2" opacity="0.3"/>')
    fc.append(f'<path d="M 236 150 L 252 150 L 262 214 L 240 216 Z" fill="#4E4E62" opacity="0.6"/>')
    fc.append(f'<path d="M 232 150 L 236 150 L 240 216 L 234 216 Z" fill="#F2E2C8" opacity="0.4"/>')
    fc.append(f'<rect x="440" y="140" width="40" height="90" fill="#4E4E62" opacity="0.3"/>')
    out.append(f'<g clip-path="url(#{u}-fc)">{"".join(fc)}</g>')
    # fynbos and forest on the lower slopes, ravines running down
    out.append(f'<clipPath id="{u}-sl"><polygon points="{P(massif)}"/></clipPath>')
    sl = [blobs(160, 19, (100, 205, 540, 300), ["#3E5A3A", "#7A9050", "#5A7444", "#9AA060"], r=(2.5, 6), opacity=(0.35, 0.7), squash=0.6)]
    for gx in (170, 252, 330, 404):
        sl.append(f'<path d="M {gx} 214 Q {gx + 8} 240 {gx + 2} 262 T {gx - 2} 300" fill="none" stroke="#2E4430" stroke-width="3" opacity="0.25"/>')
    sl.append(f'<polyline points="{P(face_bot)}" fill="none" stroke="#8E8A78" stroke-width="5" opacity="0.5"/>')
    out.append(f'<g clip-path="url(#{u}-sl)">{"".join(sl)}</g>')
    out.append(f'<polyline points="{P(top)}" fill="none" stroke="#FFF2DC" stroke-width="1.6"/>')
    # the tablecloth: a cloud bank resting on the plateau and pouring over the edge, evaporating as it falls
    rnd = random.Random(23)
    bank_top = [(x, 143 - 2 * math.sin(x / 23 + 1) - 1.5 * math.sin(x / 9) - 5 * math.sin(math.pi * (x - 112) / 340)) for x in range(112, 456, 6)]
    bank = bank_top + top[::-1]
    out.append(Q(bank, f"url(#{u}-bank)"))
    bil = []
    x = 116
    while x < 450:
        rx = rnd.uniform(12, 22)
        yb = y_on(bank_top, min(x, 450)) or 140
        bil.append((x, yb + 2, rx, rx * rnd.uniform(0.38, 0.5)))
        x += rx * rnd.uniform(1.1, 1.5)
    out.append(f'<g fill="#D6DEEA">' + "".join(f'<ellipse cx="{x + 2:.1f}" cy="{y + 2:.1f}" rx="{a:.1f}" ry="{b:.1f}"/>' for x, y, a, b in bil) + "</g>")
    out.append(f'<g fill="#FFFFFF">' + "".join(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{a:.1f}" ry="{b:.1f}"/>' for x, y, a, b in bil) + "</g>")
    for layer, (amp, base_l, op) in enumerate(((7, 14, 0.9), (8, 28, 0.4))):
        ph = rnd.uniform(0, 6)
        bot = []
        for x in range(110, 462, 5):
            L = base_l + amp * math.sin(x / 15 + ph) + amp * 0.6 * math.sin(x / 6.3 + ph * 2) + rnd.uniform(-3, 3)
            L *= math.sin(math.pi * min(1, max(0, (x - 110) / 352))) ** 0.5
            bot.append((x, (y_on(top, min(max(x, 117), 445)) or 150) + max(4, L)))
        curtain = [(x, (y_on(top, min(max(x, 117), 445)) or 150) - 2) for x in range(110, 462, 10)] + bot[::-1]
        out.append(f'<polygon points="{P(curtain)}" fill="url(#{u}-tc)" opacity="{op}"/>')
    out.append(f'<g fill="none" stroke="#FFFFFF" stroke-linecap="round" opacity="0.3">' + "".join(
        f'<path d="M {x:.1f} {152 + rnd.uniform(0, 4):.1f} q {rnd.uniform(-3, 3):.1f} {rnd.uniform(10, 20):.1f} {rnd.uniform(-2, 4):.1f} {rnd.uniform(22, 40):.1f}" stroke-width="{rnd.uniform(2, 4):.1f}"/>' for x in [rnd.uniform(130, 430) for _ in range(12)]) + "</g>")
    # Lion's Head and Signal Hill, in front on the right
    lion = rough([(452, 320), (470, 262), (494, 236), (514, 206), (530, 184), (546, 176), (560, 180), (570, 196), (582, 218), (610, 236)], 11, amp=3, depth=3)
    out.append(Q(lion + [(610, 320)], f"url(#{u}-lion)"))
    out.append(f'<path d="M 532 186 C 538 176 556 174 566 190 L 570 206 C 560 204 546 206 536 200 Z" fill="#9A9488"/>')
    out.append(f'<path d="M 532 186 C 538 176 552 174 560 180" fill="none" stroke="#FFF2DC" stroke-width="1.6"/>')
    out.append(f'<clipPath id="{u}-ln"><polygon points="{P(lion + [(610, 320)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-ln)">' + blobs(50, 29, (460, 210, 610, 300), ["#3E5A3A", "#7A9050", "#5A7444"], r=(4, 10), opacity=(0.35, 0.7)) + "</g>")
    out.append(f'<polyline points="{P(lion[:6])}" fill="none" stroke="#E8E2B8" stroke-width="1.4" opacity="0.7"/>')
    signal = rough([(380, 300), (440, 270), (500, 258), (560, 252), (610, 250)], 13, amp=2, depth=3)
    out.append(Q(signal + [(610, 320), (380, 320)], "#6A8452"))
    out.append(f'<polyline points="{P(signal)}" fill="none" stroke="#B8C47A" stroke-width="1.4" opacity="0.7"/>')
    # the city bowl at the foot of the mountain
    rnd = random.Random(37)
    city = []
    x = -10
    while x < 420:
        w = rnd.uniform(8, 22)
        h = rnd.uniform(6, 16) + (rnd.uniform(16, 52) if 120 < x < 330 and rnd.random() < 0.35 else 0)
        c = rnd.choice(["#E8E4DC", "#D8D4D0", "#C8CCD4", "#F2EEE6", "#B8C0CC", "#E0D8CC"])
        city.append(f'<rect x="{x:.1f}" y="{300 - h:.1f}" width="{w:.1f}" height="{h + 20:.1f}" fill="{c}"/><rect x="{x:.1f}" y="{300 - h:.1f}" width="{w * 0.3:.1f}" height="{h + 20:.1f}" fill="#FFFFFF" opacity="0.4"/>')
        if h > 20:
            for yy in range(int(300 - h) + 4, 298, 4):
                city.append(f'<rect x="{x + 1.5:.1f}" y="{yy}" width="{w - 3:.1f}" height="1.4" fill="#7A8AA0" opacity="0.5"/>')
        x += w + rnd.uniform(0, 3)
    out.append("".join(city))
    out.append(blobs(40, 39, (-10, 290, 400, 306), ["#4E6A3E", "#6A8A4A"], r=(4, 9), opacity=(0.7, 1), squash=0.7))
    # Bo-Kaap: rows of brightly painted houses climbing the lower slope of Signal Hill, a minaret among them
    cols = ["#E8467A", "#F2C230", "#5AC8B8", "#8A5AC0", "#F28A3A", "#6AC85A", "#3A8AD8", "#F25A4A", "#F7E04A", "#E86AB8", "#3AB0A0"]
    rnd = random.Random(41)
    for row, (yb, xs, xe, k) in enumerate(((272, 446, 560, 0.75), (284, 420, 590, 0.85), (298, 392, 610, 0.95), (313, 360, 610, 1.05))):
        x = xs + rnd.uniform(-6, 0)
        while x < xe:
            w = rnd.uniform(12, 20) * k
            h = rnd.uniform(11, 16) * k
            out.append(bokaap_house(x, yb + (x - 450) * -0.03 + rnd.uniform(-1.5, 1.5), w, h, rnd.choice(cols), rnd, k))
            x += w + rnd.uniform(0, 1.2)
        if row == 1:
            mx = 566
            out.append(f'<rect x="{mx - 3}" y="{yb - 36}" width="6" height="30" fill="#F6F2EA"/><rect x="{mx - 4.6}" y="{yb - 26}" width="9.2" height="2.4" fill="#F6F2EA"/>'
                       f'<path d="M {mx - 3.6} {yb - 36} Q {mx} {yb - 46} {mx + 3.6} {yb - 36} Z" fill="#3E8A4A"/><line x1="{mx}" y1="{yb - 44}" x2="{mx}" y2="{yb - 50}" stroke="#C8A040" stroke-width="1.2"/>'
                       f'<rect x="{mx + 1.4}" y="{yb - 36}" width="1.6" height="30" fill="#C8C4C0"/>')
    # harbour: quays, water, reflections
    out.append(f'<rect x="-10" y="{wl - 4}" width="620" height="6" fill="#8A8682"/><rect x="-10" y="{wl - 4}" width="620" height="1.6" fill="#E8E2D8"/>')
    out.append(f'<rect x="0" y="{wl + 2}" width="600" height="{444 - wl}" fill="url(#{u}-sea)"/>')
    rnd = random.Random(43)
    ref = []
    for i in range(60):
        y = wl + 4 + i * 1.8
        for x0, x1, c in ((110, 470, "#8E96A4"), (380, 610, "#F2A0A0"), (440, 560, "#F6D070")):
            if rnd.random() < 0.5 and i < 30:
                xx = rnd.uniform(x0, x1)
                ref.append(f'<rect x="{xx:.1f}" y="{y:.1f}" width="{rnd.uniform(8, 30):.1f}" height="1.2" fill="{c}" opacity="{0.4 * (1 - i / 30):.2f}"/>')
    out.append("".join(ref))
    out.append(water_lines(120, 44, (0, wl + 6, 600, 444), ["#9ACBE8", "#1E4A72", "#5A9AC8", "#E8F2F8"], w=(10, 50), h=(0.8, 2.2), opacity=(0.25, 0.65)))
    # boats: a yacht under sail, a red trawler coming in, a small launch
    bx, by = 470, 352
    out.append(f'<path d="M {bx - 22} {by} L {bx + 22} {by} L {bx + 16} {by + 7} L {bx - 18} {by + 7} Z" fill="#F4F0EA"/><path d="M {bx - 18} {by + 5} L {bx + 17} {by + 5} L {bx + 16} {by + 7} L {bx - 18} {by + 7} Z" fill="#1E3A5A"/>'
               f'<line x1="{bx}" y1="{by}" x2="{bx}" y2="{by - 60}" stroke="#5A5A64" stroke-width="1.6"/>'
               f'<path d="M {bx + 2} {by - 58} Q {bx + 24} {by - 30} {bx + 26} {by - 4} L {bx + 2} {by - 4} Z" fill="#FFFFFF"/><path d="M {bx + 2} {by - 58} Q {bx + 10} {by - 30} {bx + 8} {by - 4} L {bx + 2} {by - 4} Z" fill="#DCE4EE"/>'
               f'<path d="M {bx - 2} {by - 50} Q {bx - 18} {by - 26} {bx - 22} {by - 6} L {bx - 2} {by - 6} Z" fill="#F2F4F8"/><path d="M {bx - 2} {by - 50} Q {bx - 18} {by - 26} {bx - 22} {by - 6}" fill="none" stroke="#FFFFFF" stroke-width="1.4"/>'
               f'<path d="M {bx - 40} {by + 9} Q {bx - 10} {by + 6} {bx + 20} {by + 8}" fill="none" stroke="#E8F2F8" stroke-width="1.6" opacity="0.6"/>')
    out.append(f'<path d="M 278 376 Q 250 372 214 374" fill="none" stroke="#E8F2F8" stroke-width="2" opacity="0.5"/><path d="M 280 384 Q 254 390 222 398" fill="none" stroke="#E8F2F8" stroke-width="1.6" opacity="0.45"/>')
    out.append(water_lines(26, 48, (210, 374, 290, 392), ["#FFFFFF", "#CFE6F2"], w=(6, 18), h=(1, 2), opacity=(0.35, 0.75)))
    out.append(trawler(320, 384, 0.72))
    out.append(f'<g opacity="0.18" transform="translate(0 {384 + 0.6 * 386}) scale(1 -0.6)">{trawler(320, 384, 0.72)}</g>')
    out.append(water_lines(20, 45, (270, 386, 380, 398), ["#C8343A", "#F2ECE4"], w=(6, 20), h=(1, 2), opacity=(0.3, 0.6)))
    out.append(f'<path d="M 80 340 L 112 340 L 108 346 L 84 346 Z" fill="#F2ECE4"/><rect x="90" y="334" width="10" height="6" fill="#2E5A8A"/><path d="M 60 344 Q 70 342 80 343" stroke="#E8F2F8" stroke-width="1.2" fill="none" opacity="0.6"/>')
    # stone quay in the foreground with a bollard and rope
    q = [(-10, 400), (170, 410), (196, 444), (-10, 444)]
    out.append(Q(q, f"url(#{u}-quay)"))
    out.append(Q([(-10, 396), (170, 406), (172, 411), (-10, 401)], "#D8D2C8"))
    out.append(f'<g stroke="#5A5450" stroke-width="1.2" opacity="0.5">' + "".join(f'<line x1="{x}" y1="{402 + x * 0.06:.1f}" x2="{x + 14}" y2="444"/>' for x in range(10, 170, 40)) + "</g>")
    out.append(f'<path d="M 92 396 L 92 380 Q 92 372 102 372 Q 112 372 112 380 L 112 396 Z" fill="#2A2A32"/><ellipse cx="102" cy="372" rx="12" ry="4" fill="#3E3E48"/><path d="M 94 382 Q 94 376 100 374" stroke="#9AA4B0" stroke-width="1.6" fill="none"/>')
    out.append(f'<path d="M 112 386 Q 140 400 166 408" fill="none" stroke="#C8B080" stroke-width="3"/><path d="M 92 388 Q 104 392 112 388" fill="none" stroke="#C8B080" stroke-width="3"/>')
    out.append(f'<ellipse cx="54" cy="408" rx="22" ry="6" fill="none" stroke="#C8B080" stroke-width="3"/><ellipse cx="54" cy="406" rx="13" ry="3.4" fill="none" stroke="#B89A68" stroke-width="2.6"/>')
    # Cape fur seals hauled out on a pontoon
    px0, px1, py = 360, 610, 418
    out.append(Q([(px0, py), (px1, py - 6), (px1, py + 8), (px0 + 4, py + 12)], f"url(#{u}-pont)"))
    out.append(Q([(px0, py), (px1, py - 6), (px1, py - 3), (px0, py + 3)], "#9A9AA2"))
    out.append(f'<path d="M {px0 + 4} {py + 12} L {px1} {py + 8} L {px1} {py + 12} L {px0 + 4} {py + 16} Z" fill="#1E3A52" opacity="0.6"/>')
    out.append(seal(560, py - 4.5, 0.62, flip=True, head_up=False))
    out.append(seal(420, py - 0.5, 0.78, head_up=True))
    out.append(seal(490, py - 2.4, 0.6, flip=True, head_up=True, body="#4E3A30"))
    out.append(water_lines(16, 47, (px0 - 10, py + 14, px1, py + 22), ["#E8F2F8"], w=(10, 30), h=(1, 1.8), opacity=(0.3, 0.6)))
    return "\n".join(out)


# ================================================================ MYKONOS — the Kato Mili windmills above Little Venice, afternoon
def mk_windmill(x, base, k, u, g, rot=8, sails=(1, 7), face=0.8):
    """Mykonos windmill: a whitewashed drum, a thatched conical cap, and on the sea side a hub with twelve
    wooden spokes braced by rope at their tips, a few triangular canvas sails set. Sun from the right."""
    w, h, rh = 46 * k, 50 * k, 26 * k
    out = []
    out.append(f'<ellipse cx="{x + 6 * k:.1f}" cy="{base + 1:.1f}" rx="{w * 0.7:.1f}" ry="{3.4 * k:.1f}" fill="#6A5A3A" opacity="0.35"/>')
    body = [(x - w / 2, base), (x - w * 0.46, base - h), (x + w * 0.46, base - h), (x + w / 2, base)]
    out.append(Q(body, f"url(#{g}-drum)"))
    out.append(f'<path d="M {x - w / 2:.1f} {base:.1f} Q {x:.1f} {base + 3 * k:.1f} {x + w / 2:.1f} {base:.1f}" fill="none" stroke="#C8D0DC" stroke-width="{1.4 * k:.1f}"/>')
    # door and windows
    out.append(f'<path d="M {x - 4 * k:.1f} {base:.1f} L {x - 4 * k:.1f} {base - 13 * k:.1f} Q {x:.1f} {base - 16 * k:.1f} {x + 4 * k:.1f} {base - 13 * k:.1f} L {x + 4 * k:.1f} {base:.1f} Z" fill="#2E5A9A"/>')
    out.append(f'<rect x="{x + 9 * k:.1f}" y="{base - 30 * k:.1f}" width="{4 * k:.1f}" height="{5 * k:.1f}" fill="#3A4A5E"/><rect x="{x - 14 * k:.1f}" y="{base - 34 * k:.1f}" width="{3.4 * k:.1f}" height="{4.6 * k:.1f}" fill="#3A4A5E"/>')
    # thatched cap with straw courses and a little peak
    cap = [(x - w * 0.52, base - h + 1), (x - w * 0.2, base - h - rh * 0.8), (x + w * 0.02, base - h - rh), (x + w * 0.24, base - h - rh * 0.78), (x + w * 0.52, base - h + 1)]
    out.append(Q(cap, f"url(#{g}-thatch)"))
    out.append(f'<clipPath id="{u}-cp{int(x)}"><polygon points="{P(cap)}"/></clipPath><g clip-path="url(#{u}-cp{int(x)})" stroke="#6A4A2A" stroke-width="{1 * k:.1f}" opacity="0.5">'
               + "".join(f'<line x1="{x - w * 0.6:.1f}" y1="{base - h - i * 4.5 * k:.1f}" x2="{x + w * 0.6:.1f}" y2="{base - h - i * 4.5 * k + 1.5 * k:.1f}"/>' for i in range(7)) + "</g>")
    out.append(f'<path d="M {x + w * 0.02:.1f} {base - h - rh:.1f} L {x + w * 0.24:.1f} {base - h - rh * 0.78:.1f} L {x + w * 0.52:.1f} {base - h + 1:.1f}" fill="none" stroke="#F8D898" stroke-width="{1.6 * k:.1f}"/>')
    out.append(f'<path d="M {x - w * 0.54:.1f} {base - h + 2:.1f} Q {x:.1f} {base - h + 6 * k:.1f} {x + w * 0.54:.1f} {base - h + 2:.1f}" fill="none" stroke="#5A3E22" stroke-width="{1.8 * k:.1f}"/>')
    # hub and spokes (seen nearly face-on, the wheel tilted slightly)
    hx, hy = x - w * 0.3, base - h - rh * 0.15
    R = 42 * k
    tips = []
    for i in range(12):
        a = math.radians(rot + i * 30)
        tips.append((hx + R * face * math.cos(a), hy + R * math.sin(a)))
    sl = []
    for i in sails:
        a2 = math.radians(rot + i * 30 + 26)
        t = tips[i]
        mid = (hx + R * 0.32 * face * math.cos(math.radians(rot + i * 30)), hy + R * 0.32 * math.sin(math.radians(rot + i * 30)))
        t2 = (hx + R * 0.86 * face * math.cos(a2), hy + R * 0.86 * math.sin(a2))
        sl.append(Q([mid, t, t2], "#FBF8F2", ' opacity="0.95"'))
        sl.append(f'<line x1="{mid[0]:.1f}" y1="{mid[1]:.1f}" x2="{t2[0]:.1f}" y2="{t2[1]:.1f}" stroke="#C8CCD8" stroke-width="{1 * k:.1f}"/>')
    out.append("".join(sl))
    out.append(f'<polygon points="{P(tips)}" fill="none" stroke="#7A6A5A" stroke-width="{0.9 * k + 0.3:.1f}" opacity="0.8"/>')
    out.append(f'<g stroke="#5A4232" stroke-width="{1.3 * k + 0.4:.1f}" stroke-linecap="round">' + "".join(f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{tx:.1f}" y2="{ty:.1f}"/>' for tx, ty in tips) + "</g>")
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{4 * k:.1f}" fill="#4A3426"/><circle cx="{hx + 1 * k:.1f}" cy="{hy - 1 * k:.1f}" r="{1.6 * k:.1f}" fill="#B8946A"/>')
    return "".join(out)


def lv_house(C, X, z0, z1, h, seed, u, end_wall=True):
    """A Little Venice house rising straight out of the sea: whitewashed sea facade (plane X) lit by the
    afternoon sun, coloured shutters and doors, a cantilevered wooden balcony, flat roof with parapet."""
    rnd = random.Random(seed)
    out = []
    col = rnd.choice(["#C8322E", "#2E5AA8", "#2E8A5A", "#E8A62E", "#2E7EB8", "#B83A6A", "#C8322E", "#2E5AA8"])
    fac = C.quad_x(X, z0, z1, 0, h)
    if end_wall:
        out.append(Q([C(X - 6, 0, z0), C(X - 6, h, z0), C(X, h, z0), C(X, 0, z0)], "#D4DEEC"))
        out.append(Q([C(X - 6, 0, z0), C(X - 6, h * 0.4, z0), C(X, h * 0.4, z0), C(X, 0, z0)], "#B8C6DA", ' opacity="0.6"'))
        ec = rnd.choice(["#2E5AA8", "#C8322E", "#2E8A5A"])
        for xa, xb, ya, yb_ in ((X - 2.2, X - 1.0, 0.6, 2.9), (X - 4.8, X - 3.8, 1.6, 2.8), (X - 4.6, X - 3.6, h - 3.0, h - 1.6), (X - 2.2, X - 1.2, h - 3.0, h - 1.6)):
            out.append(Q(C.quad_z(z0, xa, xb, ya, yb_), ec if ya < 1 else "#2A3A4E"))
            if ya >= 1:
                out.append(Q(C.quad_z(z0, xa - 0.3, xa, ya - 0.1, yb_ + 0.1), ec))
                out.append(Q(C.quad_z(z0, xb, xb + 0.3, ya - 0.1, yb_ + 0.1), ec))
        # outside stair climbing the end wall
        for j in range(6):
            yy = 0.4 + j * 0.55
            out.append(Q(C.quad_z(z0 - 0.05, X - 5.8 + j * 0.45, X - 5.8 + j * 0.45 + 0.9, yy, yy + 0.55), "#FBF6EC"))
        out.append(Q(C.quad_z(z0 - 0.05, X - 5.8, X - 2.6, 3.7, 3.95), "#FFFFFF"))
        out.append(Q([C(X - 6, h, z0), C(X - 6, h + 0.5, z0), C(X, h + 0.5, z0), C(X, h, z0)], "#E2EAF4"))
    out.append(Q(fac, "#FBF6EC"))
    out.append(Q(C.quad_x(X, z0, z1, 0, h * 0.35), "#E8E2DA", ' opacity="0.6"'))
    out.append(Q(C.quad_x(X, z0, z1, h, h + 0.5), "#FFFFFF"))
    if rnd.random() < 0.5:  # a little Cycladic chimney on the roof
        zc = z0 + (z1 - z0) * rnd.uniform(0.3, 0.7)
        out.append(Q(C.quad_x(X - 1.5, zc, zc + 0.7, h + 0.4, h + 1.8), "#FBF6EC"))
        out.append(Q(C.quad_x(X - 1.5, zc - 0.15, zc + 0.85, h + 1.8, h + 2.1), "#FFFFFF"))
        out.append(Q(C.quad_x(X - 1.5, zc + 0.15, zc + 0.55, h + 1.0, h + 1.5), "#5A6A7E"))
    out.append(Q([C(X, 0, z0), C(X, h, z0), C(X, h, z0 + 0.35), C(X, 0, z0 + 0.35)], "#C8D4E4"))
    # stone footing streaked by the sea
    out.append(Q(C.quad_x(X, z0, z1, -0.6, 0.9), "#9A8E80"))
    out.append(Q(C.quad_x(X, z0, z1, 0.6, 0.9), "#C8B8A0", ' opacity="0.7"'))
    # openings: doors and shuttered windows on the ground floor, windows with shutters upstairs
    L = z1 - z0
    n = max(1, int(L / 1.9))
    for i in range(n):
        za = z0 + L * (i + 0.25) / n
        zb = za + min(1.0, L / n * 0.42)
        c2 = col if rnd.random() < 0.75 else rnd.choice(["#2E5AA8", "#C8322E", "#2E8A5A"])
        if rnd.random() < 0.5:
            out.append(Q(C.quad_x(X, za, zb, 1.0, 3.0), c2))
            out.append(Q(C.quad_x(X, za, zb, 2.8, 3.0), "#FFFFFF", ' opacity="0.6"'))
        else:
            out.append(Q(C.quad_x(X, za, zb, 1.6, 2.8), "#2A3A4E"))
            out.append(Q(C.quad_x(X, za - 0.3, za, 1.6, 2.8), c2))
            out.append(Q(C.quad_x(X, zb, zb + 0.3, 1.6, 2.8), c2))
        if h > 6:
            out.append(Q(C.quad_x(X, za, zb, h - 3.0, h - 1.6), "#2A3A4E"))
            out.append(Q(C.quad_x(X, za - 0.32, za, h - 3.1, h - 1.5), c2))
            out.append(Q(C.quad_x(X, zb, zb + 0.32, h - 3.1, h - 1.5), c2))
            out.append(Q(C.quad_x(X, za - 0.1, zb + 0.1, h - 1.5, h - 1.3), "#FFFFFF"))
    if rnd.random() < 0.35:  # bougainvillea spilling down the wall
        zc = z0 + L * rnd.uniform(0.2, 0.8)
        pa, pb = C(X + 0.2, h + 0.4, zc - 1.2), C(X + 0.2, h * 0.45, zc + 0.8)
        out.append(blobs(int(500 / z0), seed + 9, (min(pa[0], pb[0]), pa[1], max(pa[0], pb[0]) + 2, pb[1]), ["#D8247A", "#F04A9A", "#B81E6A", "#3E6A30"], r=(150 / z0 * 0.1 + 0.8, 150 / z0 * 0.22 + 1), opacity=(0.9, 1), squash=0.9))
    # balcony: a coloured wooden gallery cantilevered over the water on brackets
    if rnd.random() < 0.85 and h > 5:
        ba, bb = z0 + L * rnd.uniform(0.05, 0.2), z1 - L * rnd.uniform(0.05, 0.25)
        yb = h * rnd.uniform(0.42, 0.52)
        Xb = X + 1.2
        out.append(Q([C(X, yb, ba), C(Xb, yb, ba), C(Xb, yb, bb), C(X, yb, bb)], mix(col, "#000000", 0.35)))
        for zz in [ba + (bb - ba) * t for t in (0.1, 0.5, 0.9)]:
            out.append(f'<line x1="{C(X, yb - 1, zz)[0]:.1f}" y1="{C(X, yb - 1, zz)[1]:.1f}" x2="{C(Xb, yb, zz)[0]:.1f}" y2="{C(Xb, yb, zz)[1]:.1f}" stroke="{mix(col, "#000000", 0.4)}" stroke-width="1.4"/>')
        rail = C.quad_x(Xb, ba, bb, yb, yb + 1.0)
        out.append(Q(rail, col))
        out.append(Q([C(X, yb, ba), C(X, yb + 1.0, ba), C(Xb, yb + 1.0, ba), C(Xb, yb, ba)], mix(col, "#000000", 0.2)))
        bars = []
        nb = int((bb - ba) / 0.3)
        for j in range(1, nb):
            zz = ba + (bb - ba) * j / nb
            p1, p2 = C(Xb, yb + 0.15, zz), C(Xb, yb + 0.85, zz)
            bars.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}"/>')
        out.append(f'<g stroke="#FBF6EC" stroke-width="0.9" opacity="0.7">{"".join(bars)}</g>')
        p1, p2 = C(Xb, yb + 1.0, ba), C(Xb, yb + 1.0, bb)
        out.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="{mix(col, "#FFFFFF", 0.35)}" stroke-width="1.4"/>')
        if rnd.random() < 0.5:  # a pot of red geraniums or bougainvillea on the rail
            px, py = C(Xb, yb + 1.0, ba + (bb - ba) * 0.5)
            s = 300 / ba * 0.05
            out.append(blobs(10, seed, (px - 8 * s, py - 10 * s, px + 8 * s, py), ["#E83A6A", "#C81E5A", "#4E8A3E"], r=(1.4 * s, 3 * s), opacity=(0.9, 1), squash=1))
    return "".join(out)


def pelican(x, base, k, flip=False):
    """Mykonos pelican standing on a rock, facing left: white-pink plumage, black-tipped wings folded, a long
    pale bill with a yellow-orange pouch, shaggy crest."""
    sx = -k if flip else k
    return (f'<g transform="translate({x:.1f} {base:.1f}) scale({sx:.3f} {k:.3f})">'
            '<path d="M -2 0 L 0 -18 M 10 0 L 10 -18" stroke="#E8A070" stroke-width="4.4" stroke-linecap="round"/>'
            '<path d="M -10 0 L 2 0 M 2 0 L 14 0" stroke="#E8A070" stroke-width="3" stroke-linecap="round"/>'
            '<g transform="translate(0 10)">'
            '<path d="M -18 -40 C -20 -60 -6 -72 12 -70 C 30 -68 44 -54 50 -36 C 44 -30 30 -24 14 -24 C -2 -24 -14 -28 -18 -40 Z" fill="#F8EEEE"/>'
            '<path d="M 0 -62 C 16 -66 32 -58 40 -46 C 46 -40 52 -34 56 -30 C 44 -30 34 -32 24 -36 C 12 -40 2 -50 0 -62 Z" fill="#E8DADC"/>'
            '<path d="M 30 -44 C 40 -38 50 -34 58 -30 C 50 -28 40 -30 32 -34 Z" fill="#2A2228"/>'
            '<path d="M 10 -34 C 20 -34 30 -32 40 -32" fill="none" stroke="#C8B4BC" stroke-width="1.6"/>'
            # neck curving up and the head
            '<path d="M -14 -48 C -22 -60 -24 -76 -18 -88 C -14 -96 -4 -98 2 -92 C 6 -86 2 -80 -4 -80 C -10 -76 -8 -62 -2 -54 Z" fill="#F8EEEE"/>'
            '<path d="M -4 -94 C 2 -102 10 -100 10 -94 C 6 -98 0 -98 -4 -94 Z" fill="#F2E2C8"/>'
            '<path d="M 0 -96 Q -6 -104 -2 -106 Q 2 -102 6 -100 Q 4 -106 10 -106 Q 8 -100 6 -96 Z" fill="#F2E8E0"/>'
            # bill and pouch
            '<path d="M -18 -90 L -66 -72 L -68 -68 L -20 -83 Z" fill="#EADAC0"/>'
            '<path d="M -20 -83 L -64 -69 Q -50 -62 -34 -66 Q -22 -70 -15 -76 Z" fill="#F0B050"/>'
            '<path d="M -24 -80 Q -40 -70 -56 -69" fill="none" stroke="#D88A3A" stroke-width="1"/>'
            '<path d="M -20 -82 L -66 -67" stroke="#C88A3A" stroke-width="1"/><path d="M -66 -70 L -70 -66 L -66 -66 Z" fill="#E86A4A"/>'
            '<circle cx="-12" cy="-88" r="2" fill="#2A1E1E"/><circle cx="-12" cy="-88" r="3.4" fill="none" stroke="#F2B8A0" stroke-width="1.4"/>'
            # sun rim along the back and head (sun from the right)
            '<path d="M 12 -70 C 30 -68 44 -54 50 -36" fill="none" stroke="#FFF4D8" stroke-width="2" stroke-linecap="round"/>'
            '<path d="M 2 -92 C 6 -86 2 -80 -4 -80" fill="none" stroke="#FFF4D8" stroke-width="1.6"/>'
            '<path d="M -18 -40 C -14 -30 -2 -24 14 -24 C 30 -24 44 -30 50 -36" fill="none" stroke="#C8B0B8" stroke-width="2"/>'
            '</g></g>')


def mykonos():
    u = "myk"
    hz = 250
    C = Cam(f=330, cx=300, vpy=hz, eye=3.0)
    out = [defs(
        lg(f"{u}-sky", [(0, "#1A58B0"), (0.4, "#3E86D2"), (0.8, "#8CC4EC"), (1, "#C8E6F6")], 0, 40, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#2E78C0"), (0.2, "#1E5EAE"), (0.6, "#14489A"), (1, "#0E3478")], 0, hz, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-hill", [(0, "#D8B878"), (0.5, "#C09A62"), (1, "#9A7A52")], 0, 180, 0, 320, units="userSpaceOnUse"),
        lg(f"{u}-drum", [(0, "#C8D4E6"), (0.35, "#F4F6FA"), (0.7, "#FFFFFF"), (1, "#FFF8EA")], 0, 0, 1, 0),
        lg(f"{u}-thatch", [(0, "#7A5634"), (0.6, "#9E7646"), (1, "#C89E62")], 0, 0, 1, 0),
        lg(f"{u}-rock", [(0, "#A89482"), (1, "#5E5048")]),
        lg(f"{u}-shal", [(0, "#3EC0C8", 0.0), (1, "#3EC0C8", 0.7)]),
    )]
    out.append(f'<rect width="600" height="{hz + 1}" fill="url(#{u}-sky)"/>')
    out.append(glow(560, 90, 240, "#FFF8E0", f"{u}-g1", 0.55))
    out.append(cumulus(f"{u}-c1", 232, 124, 110, 24, 3, "#FFFFFF", "#F2F6FC", "#BCCDE4", light=1))
    out.append(cumulus(f"{u}-c2", 360, 96, 80, 18, 5, "#FFFFFF", "#F2F6FC", "#BCCDE4", light=1))
    out.append(cumulus(f"{u}-c3", 300, 196, 70, 12, 8, "#FFFFFF", "#EEF4FC", "#C8D6EA", light=1))
    # the sea and a far island on the horizon
    out.append(f'<rect x="0" y="{hz}" width="600" height="{444 - hz}" fill="url(#{u}-sea)"/>')
    poly, _ = ridge_poly([(180, hz + 1), (220, hz - 8), (270, hz - 12), (320, hz - 6), (350, hz + 1)], 4, base=hz + 1, amp=2, fill="#8AAED4")
    out.append(poly)
    out.append(water_lines(140, 9, (0, hz + 3, 600, 444), ["#5AA0E0", "#0E3A80", "#8AC4F0", "#FFFFFF"], w=(8, 46), h=(0.8, 2.2), opacity=(0.2, 0.6)))
    # sun glitter (sun high on the right)
    rnd = random.Random(3)
    out.append("".join(f'<rect x="{rnd.uniform(330, 600):.1f}" y="{(y := hz + 4 + rnd.random() ** 1.4 * 120):.1f}" width="{rnd.uniform(3, 12) * (0.5 + (y - hz) / 120):.1f}" height="1.2" rx="0.6" fill="#FFFFFF" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>' for _ in range(70)))
    # the windmill hill: dry golden slopes, stone terrace walls, a few white houses below the mills
    ridge = rough([(330, hz + 2), (370, 238), (420, 214), (470, 196), (520, 190), (570, 194), (610, 200)], 6, amp=2, depth=3)
    shore = [(610, 312), (540, 306), (470, 292), (410, 276), (360, 262), (330, hz + 2)]
    hill = ridge + shore
    out.append(Q(hill, f"url(#{u}-hill)"))
    out.append(f'<clipPath id="{u}-hl"><polygon points="{P(hill)}"/></clipPath>')
    hl = [blobs(70, 7, (330, 190, 610, 310), ["#8A7A4E", "#E8CC8A", "#7A8A52", "#A88A5A"], r=(2, 6), opacity=(0.3, 0.7), squash=0.6)]
    for i, y in enumerate((228, 246, 264, 282)):
        hl.append(f'<polyline points="{P(rough([(330, y + 10), (450, y - 6), (610, y - 20)], 30 + i, amp=2, depth=3))}" fill="none" stroke="#8A7656" stroke-width="2" stroke-dasharray="4 2" opacity="0.6"/>')
    hl.append(Q([(330, hz + 2), (370, 238), (420, 214), (470, 196), (420, 280), (360, 262)], "#7A6A5A", ' opacity="0.18"'))
    out.append(f'<g clip-path="url(#{u}-hl)">{"".join(hl)}</g>')
    out.append(f'<polyline points="{P(ridge)}" fill="none" stroke="#FFF2C8" stroke-width="1.6" opacity="0.8"/>')
    rnd = random.Random(19)
    for i, (hx_, hb, hw, hh) in enumerate(((372, 262, 18, 12), (394, 268, 22, 14), (432, 278, 26, 15), (470, 288, 22, 13), (506, 296, 30, 16), (548, 302, 26, 14), (586, 306, 30, 17))):
        out.append(f'<rect x="{hx_:.1f}" y="{hb - hh:.1f}" width="{hw}" height="{hh}" fill="#FBF6EC"/><rect x="{hx_:.1f}" y="{hb - hh:.1f}" width="{hw * 0.3:.1f}" height="{hh}" fill="#D2DCEA"/>'
                   f'<rect x="{hx_ - 0.5:.1f}" y="{hb - hh - 1.4:.1f}" width="{hw + 1}" height="1.6" fill="#FFFFFF"/>'
                   f'<rect x="{hx_ + hw * 0.55:.1f}" y="{hb - 7:.1f}" width="3" height="7" fill="{rnd.choice(["#2E5AA8", "#C8322E", "#2E8A5A"])}"/>')
    # the windmills along the ridge, far to near
    for x_, k_, rot in ((356, 0.3, 4), (398, 0.42, 14), (446, 0.6, 22), (506, 0.9, 10)):
        out.append(mk_windmill(x_, (y_on(ridge, x_) or 220) + 3 * k_, k_, f"{u}-w{x_}", u, rot=rot))
    # rocks and surf at the foot of the hill
    rk = rough([(330, hz + 3), (400, 274), (470, 294), (540, 308), (610, 314)], 21, amp=3, depth=3)
    out.append(Q(rk + [(610, 322), (540, 318), (470, 304), (400, 284), (330, hz + 5)], "#6A5E58"))
    out.append(water_lines(40, 22, (340, 262, 610, 322), ["#FFFFFF", "#D8F0F8"], w=(6, 22), h=(1, 2.4), opacity=(0.5, 0.95)))
    # Little Venice along the left, houses standing in the sea
    houses = [(-11.0, 15.0, 18.6, 9.6), (-10.6, 18.8, 23.4, 7.6), (-11.3, 23.6, 29.0, 10.4), (-10.8, 29.2, 33.6, 8.2), (-11.6, 33.8, 40.0, 9.8),
              (-11.0, 40.2, 46.0, 8.6), (-11.8, 46.2, 53.0, 10.8), (-11.2, 53.2, 60.0, 8.4), (-12.0, 60.2, 69.0, 10.2), (-11.4, 69.2, 80.0, 9.0), (-12.2, 80.2, 94.0, 10.6)]
    for i, (X, z0, z1, h) in list(enumerate(houses))[::-1]:
        prev = houses[i - 1] if i else None
        out.append(lv_house(C, X, z0, z1, h, 50 + i, u, end_wall=(prev is None or X > prev[0] or h > prev[3])))
    # far town and the Paraportiani-like white chapels at the end of the row
    out.append(f'<path d="M 254 {hz + 2} L 254 {hz - 10} Q 260 {hz - 18} 266 {hz - 10} L 266 {hz + 2} Z" fill="#F6F2EA"/><rect x="266" y="{hz - 6}" width="14" height="8" fill="#E8EEF6"/>')
    # surf breaking against the house footings
    rnd = random.Random(29)
    surf = []
    for i in range(80):
        z = rnd.uniform(15, 94)
        X = -11.0 + rnd.uniform(0, 0.8)
        sx_, sy_ = C(X, rnd.uniform(-0.3, 0.8), z)
        r = 120 / z * rnd.uniform(0.6, 1.5)
        surf.append(f'<ellipse cx="{sx_:.1f}" cy="{sy_:.1f}" rx="{r * 1.8:.1f}" ry="{r * 0.6:.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
    out.append("".join(surf))
    for z, hgt in ((15, 3.2), (20, 2.4), (26, 2.8)):
        sx_, sy_ = C(-10.8, 0.6, z)
        sc = 300 / z
        out.append(f'<g fill="#FFFFFF" opacity="0.85">' + "".join(
            f'<circle cx="{sx_ + rnd.uniform(-0.8, 1.2) * sc * 0.3:.1f}" cy="{sy_ - rnd.uniform(0, hgt) * sc * 0.25:.1f}" r="{rnd.uniform(0.6, 1.6) * sc * 0.06:.1f}"/>' for _ in range(16)) + "</g>")
    # a caique riding at anchor
    bx, by = 0, 0
    out.append('<g transform="translate(250 348) scale(1.35)">')
    out.append(f'<path d="M {bx - 30} {by - 8} Q {bx - 26} {by + 2} {bx - 10} {by + 3} L {bx + 22} {by + 3} Q {bx + 32} {by} {bx + 34} {by - 10} Z" fill="#F6F2EA"/>'
               f'<path d="M {bx - 29} {by - 4} Q {bx - 24} {by + 2} {bx - 10} {by + 3} L {bx + 22} {by + 3} Q {bx + 31} {by} {bx + 33} {by - 5} Z" fill="#2E5AA8"/>'
               f'<path d="M {bx - 30} {by - 8} L {bx + 34} {by - 10}" stroke="#C8322E" stroke-width="2"/>'
               f'<rect x="{bx - 8}" y="{by - 18}" width="16" height="9" fill="#F2E8D8"/><rect x="{bx - 8}" y="{by - 18}" width="16" height="2.4" fill="#2E5AA8"/>'
               f'<line x1="{bx + 14}" y1="{by - 10}" x2="{bx + 14}" y2="{by - 34}" stroke="#5A4A3E" stroke-width="1.4"/>'
               f'<path d="M {bx - 30} {by + 6} Q {bx} {by + 9} {bx + 32} {by + 6}" fill="none" stroke="#FFFFFF" stroke-width="1.2" opacity="0.5"/>')
    out.append(f'<g opacity="0.25"><path d="M {bx - 28} {by + 5} L {bx + 30} {by + 4} L {bx + 22} {by + 12} L {bx - 18} {by + 12} Z" fill="#2E5AA8"/></g>')
    out.append('</g>')
    # foreground: a rock with Petros the pelican, waves breaking around it
    rock = [(340, 444), (352, 410), (378, 392), (420, 384), (470, 388), (520, 398), (566, 412), (610, 418), (610, 444)]
    out.append(Q(rock, f"url(#{u}-rock)"))
    out.append(f'<clipPath id="{u}-rk"><polygon points="{P(rock)}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-rk)">' + streaks(30, 5, (340, 384, 610, 444), ["#3E3430", "#C8B8A4"], w=(2, 6), length=(10, 30), opacity=(0.2, 0.5), slant=0.4)
               + f'<polyline points="{P(rock[1:-1])}" fill="none" stroke="#F8E8CC" stroke-width="3" opacity="0.7"/></g>')
    out.append(f'<path d="M 350 444 Q 344 426 352 412 Q 334 420 322 432 Q 312 426 300 434 Q 290 430 282 440 L 282 444 Z" fill="#FFFFFF" opacity="0.9"/>'
               f'<path d="M 352 412 Q 334 420 322 432" fill="none" stroke="#BFE6F6" stroke-width="2"/>')
    out.append(water_lines(30, 31, (240, 410, 360, 444), ["#FFFFFF", "#BFE6F6"], w=(8, 30), h=(1, 2.6), opacity=(0.5, 0.95)))
    out.append(f'<g fill="#FFFFFF">' + "".join(f'<circle cx="{rnd.uniform(320, 356):.1f}" cy="{rnd.uniform(396, 428):.1f}" r="{rnd.uniform(1, 3):.1f}" opacity="{rnd.uniform(0.6, 1):.2f}"/>' for _ in range(16)) + "</g>")
    out.append(f'<ellipse cx="482" cy="390" rx="30" ry="4" fill="#3E3430" opacity="0.4"/>')
    out.append(pelican(474, 390, 1.0))
    out.append(gulls([(240, 150, 9), (258, 160, 6)], "#2A3A5A", 1.7))
    return "\n".join(out)


BUILD = {
    "istanbul": (istanbul, "ISTANBUL", "TÜRKİYE · BOSPHORUS", "#43183C", "#F2A04E", "#FFF1E4", "#F6B87A"),
    "marrakech": (marrakech, "MARRAKECH", "MOROCCO · AFRICA", "#4A1C18", "#2FA8A0", "#FFF1E2", "#F4B87A"),
    "petra": (petra, "PETRA", "JORDAN · MIDDLE EAST", "#3A1A20", "#F2A07E", "#FFF0E6", "#F4B496"),
    "cape-town": (cape_town, "CAPE TOWN", "SOUTH AFRICA · AFRICA", "#0F3646", "#F07A5A", "#FFF4EA", "#8ED8CC"),
    "mykonos": (mykonos, "MYKONOS", "GREECE · CYCLADES", "#1652A0", "#F6F0E4", "#FFFFFF", "#BFDCFA"),
    "dubai": (dubai, "DUBAI", "UNITED ARAB EMIRATES", "#1C2E44", "#F29A48", "#FFF1E2", "#F8BE78"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("world", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
