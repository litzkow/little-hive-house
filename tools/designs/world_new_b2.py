"""World Places, painted edition — batch B2: Istanbul, Marrakech, Petra, Dubai, Cape Town, Mykonos.
Same travel-poster idiom as world_painted.py: a real viewpoint, a time of day and light direction, graded skies,
atmospheric depth and small storytelling details."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from world_painted import (defs, Q, mix, lerp, cumulus, streak_cloud, gulls, figure, leaf_canopy, water_lines, camel,
                           camel_shadow)
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
    out.append(gull(196, 196, 0.62, flip=True))
    out.append(gull(420, 330, 0.5))
    out.append(gull(140, 116, 0.95))
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
def oryx(x, base, k, rim="#FFD08A", body="#F2E4DA", shade="#C89A9A", dark="#3A2630", flip=False):
    """Arabian oryx in profile facing left: white coat, dark legs and face mask, long straight horns."""
    sx = -k if flip else k
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({sx:.3f} {k:.3f})">']
    # far legs
    g.append(f'<path d="M -16 -40 L -14 -2 M 30 -40 L 33 -2" stroke="{mix(dark, "#000000", 0.2)}" stroke-width="4.4" stroke-linecap="round"/>')
    g.append(f'<path d="M -46 -96 L -10 -146" stroke="{dark}" stroke-width="3.4" stroke-linecap="round"/>')
    # body, neck, head
    g.append(f'<path d="M -30 -54 Q -28 -66 -8 -65 L 26 -63 Q 40 -61 38 -47 Q 36 -36 22 -36 L -18 -36 Q -32 -38 -30 -54 Z" fill="{body}"/>')
    g.append(f'<path d="M -18 -36 L 22 -36 Q 36 -36 38 -47 Q 30 -42 18 -42 L -16 -42 Q -26 -42 -30 -50 Q -30 -40 -18 -36 Z" fill="{shade}" opacity="0.8"/>')
    g.append(f'<path d="M -34 -58 L -46 -88 L -36 -92 L -20 -62 Z" fill="{body}"/>')
    g.append(f'<path d="M -40 -94 Q -50 -96 -54 -90 L -62 -78 Q -62 -73 -56 -73 L -42 -80 Q -36 -86 -40 -94 Z" fill="{body}"/>')
    g.append(f'<path d="M -50 -92 L -60 -79 L -55 -76 L -46 -86 Z" fill="{dark}"/><path d="M -42 -82 L -36 -70 L -32 -72 L -38 -84 Z" fill="{dark}" opacity="0.85"/>')
    g.append('<circle cx="-46" cy="-88" r="1.4" fill="#120A0E"/>')
    g.append(f'<path d="M -40 -94 L -36 -100 L -36 -92 Z" fill="{body}"/>')
    g.append(f'<path d="M -44 -97 L -6 -150" stroke="{dark}" stroke-width="3.8" stroke-linecap="round"/>')
    # near legs with dark garters and pale socks
    for lx, dx in ((-22, -2), (24, 3)):
        g.append(f'<path d="M {lx} -42 L {lx + dx * 0.5} -18 L {lx + dx} -2" stroke="{dark}" stroke-width="5" stroke-linecap="round" fill="none"/>')
        g.append(f'<path d="M {lx + dx * 0.7} -10 L {lx + dx} -2" stroke="{body}" stroke-width="4" stroke-linecap="round"/>')
    g.append(f'<path d="M -28 -46 Q -10 -40 10 -44 Q 24 -46 34 -44" stroke="{dark}" stroke-width="3" fill="none" opacity="0.65"/>')
    g.append(f'<path d="M 38 -56 Q 46 -46 42 -32" stroke="{dark}" stroke-width="3.4" stroke-linecap="round" fill="none"/>')
    # rim light from the low sun on the left
    g.append(f'<path d="M -20 -63 Q -10 -66 10 -64 L 26 -63" stroke="{rim}" stroke-width="2.4" stroke-linecap="round" fill="none"/>')
    g.append(f'<path d="M -46 -88 L -34 -58 M -54 -91 Q -50 -96 -40 -95" stroke="{rim}" stroke-width="2" stroke-linecap="round" fill="none"/>')
    g.append(f'<path d="M -44 -97 L -6 -150" stroke="{rim}" stroke-width="1.2" stroke-linecap="round" opacity="0.8"/>')
    g.append("</g>")
    return "".join(g)


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


def dune_range(ctrl, lit, shade, uid, ripple, rip_shade, seed, n_rip=50, rim="#FFD08A", toe=0.35, base=444):
    """A range of dunes: sunlit faces under the ascending crests, and wherever the crest falls away to the
    right (away from a low sun on the left) a shadowed slip face bounded by a curved toe line from the peak."""
    line = spline(ctrl)
    body = line + [(line[-1][0], base), (line[0][0], base)]
    out = [Q(body, lit), f'<clipPath id="{uid}-c"><polygon points="{P(body)}"/></clipPath>']
    rnd = random.Random(seed)
    ys = [y for _, y in line]
    rip = []
    for _ in range(n_rip):
        x0 = rnd.uniform(line[0][0], line[-1][0])
        y0 = (y_on(line, x0) or ys[0]) + rnd.uniform(5, 110)
        w = rnd.uniform(18, 64)
        rip.append(f'<path d="M {x0:.1f} {y0:.1f} q {w * 0.3:.1f} {-rnd.uniform(2, 6):.1f} {w * 0.6:.1f} {-rnd.uniform(0, 3):.1f} q {w * 0.25:.1f} {rnd.uniform(-1, 3):.1f} {w * 0.4:.1f} {rnd.uniform(1, 4):.1f}" stroke="{rnd.choice(ripple)}"/>')
    g = ['<g fill="none" stroke-width="1.3" stroke-linecap="round" opacity="0.6">' + "".join(rip) + "</g>"]
    # find descending runs (peak -> valley)
    runs, i = [], 0
    while i < len(line) - 1:
        if line[i + 1][1] > line[i][1] + 0.05:
            j = i
            while j < len(line) - 1 and line[j + 1][1] >= line[j][1] - 0.05:
                j += 1
            if line[j][1] - line[i][1] > 5:
                runs.append((i, j))
            i = j
        else:
            i += 1
    sh = []
    for i0, i1 in runs:
        (xp, yp), (xv, yv) = line[i0], line[i1]
        L = xv - xp
        ctl = (xp + L * toe, yv + L * 0.5)
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in line[i0:i1 + 1]) + f" Q {ctl[0]:.1f} {ctl[1]:.1f} {xp:.1f} {yp:.1f} Z"
        sh.append(f'<path d="{d}" fill="{shade}"/>')
        sh.append(f'<path d="M {xv:.1f} {yv:.1f} Q {ctl[0]:.1f} {ctl[1]:.1f} {xp:.1f} {yp:.1f}" fill="none" stroke="{rip_shade}" stroke-width="1.4" opacity="0.4"/>')
        rr = random.Random(seed + i0)
        sh.append('<g fill="none" stroke-width="1.1" stroke-linecap="round" opacity="0.45">' + "".join(
            f'<path d="M {x:.1f} {y:.1f} q 10 -2 22 1" stroke="{rip_shade}"/>' for x, y in
            [(rr.uniform(xp + L * 0.2, xv - L * 0.1), 0) for _ in range(8)] for y in [(y_on(line, x) or yp) + rr.uniform(4, 14)]) + "</g>")
    g += sh
    out.append(f'<g clip-path="url(#{uid}-c)">' + "".join(g) + "</g>")
    # crest: bright where it faces the sun, thin elsewhere
    for k_ in range(len(line) - 1):
        (x1, y1), (x2, y2) = line[k_], line[k_ + 1]
        if y2 <= y1 + 0.05:
            out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{rim}" stroke-width="2.2" stroke-linecap="round" opacity="0.9"/>')
    return "".join(out), line


def falcon(x, y, s, color="#2A1A30", rim="#FFB070"):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            f'<path d="M -4 -2 Q -18 -10 -34 -6 Q -46 -4 -56 2 Q -40 -1 -26 2 Q -14 4 -4 4 L -2 14 L 2 18 L 6 14 L 4 4 Q 14 4 26 2 Q 40 -1 56 2 Q 46 -4 34 -6 Q 18 -10 4 -2 Q 2 -8 0 -9 Q -2 -8 -4 -2 Z" fill="{color}"/>'
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
    # drooping fringe
    out.append(f'<g stroke="{mid}" stroke-width="1.4" stroke-linecap="round">' + "".join(
        f'<line x1="{x + d:.1f}" y1="{base - h * 0.58:.1f}" x2="{x + d + 1:.1f}" y2="{base - h * 0.58 + rnd.uniform(4, 10):.1f}"/>' for d in [rnd.uniform(-h * 0.6, h * 0.65) for _ in range(30)]) + "</g>")
    return "".join(out)


def dubai():
    u = "dxb"
    hz = 286
    sunx, suny = 168, 272
    out = [defs(
        lg(f"{u}-sky", [(0, "#221A4E"), (0.22, "#46286A"), (0.45, "#94386E"), (0.64, "#DE4E5A"), (0.82, "#F5864A"), (1, "#FCC26C")], 0, 0, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#E8805A"), (1, "#C25660")], 0, 270, 0, 330, units="userSpaceOnUse"),
        lg(f"{u}-d1", [(0, "#F08A50"), (1, "#C8504A")], 0, 290, 0, 380, units="userSpaceOnUse"),
        lg(f"{u}-d2", [(0, "#F69A56"), (0.5, "#E06A44"), (1, "#B8443E")], 0, 318, 0, 420, units="userSpaceOnUse"),
        lg(f"{u}-d3", [(0, "#FBAE64"), (0.4, "#EE8048"), (1, "#C8503C")], 0, 350, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-sh1", [(0, "#8E3456"), (1, "#6A2650")], 0, 290, 0, 380, units="userSpaceOnUse"),
        lg(f"{u}-sh2", [(0, "#8A2E50"), (1, "#5A2048")], 0, 318, 0, 420, units="userSpaceOnUse"),
        lg(f"{u}-sh3", [(0, "#7E2A4C"), (1, "#4A1A3E")], 0, 350, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#F8A070", 0), (1, "#F8A070", 0.8)], 0, 240, 0, hz + 6, units="userSpaceOnUse"),
        lg(f"{u}-tw", [(0, "#9A4A7A"), (1, "#B85A72")], 0, 180, 0, hz, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="{hz + 40}" fill="url(#{u}-sky)"/>')
    out.append(dots(40, 2, (0, 40, 600, 140), "#F6EEE0", r=(0.6, 1.3), opacity=(0.3, 0.9)))
    out.append(glow(sunx, suny, 360, "#FFB070", f"{u}-g1", 0.75))
    out.append(glow(sunx, suny, 90, "#FFE8B0", f"{u}-g2", 0.95))
    out.append(f'<circle cx="{sunx}" cy="{suny}" r="32" fill="#FFEFC0"/>')
    for x, y, w, c in ((330, 100, 140, "#7A3478"), (480, 124, 100, "#9A3A74"), (250, 150, 120, "#C8466E"), (90, 176, 110, "#E86A62"),
                       (420, 190, 150, "#E0605E"), (560, 208, 80, "#F07A58"), (300, 226, 90, "#F8925A"), (140, 232, 70, "#FFB070")):
        out.append(streak_cloud(x, y, w, c, 0.75, 4))
        out.append(streak_cloud(x - w * 0.25, y + 2.6, w * 0.5, "#FFD0A0", 0.45, 1.4))
    # the city on the horizon, generic towers softened by dust haze
    rnd = random.Random(31)
    x = 318
    towers = []
    while x < 560:
        w = rnd.uniform(7, 16)
        h = rnd.choice([rnd.uniform(14, 40), rnd.uniform(30, 70), rnd.uniform(50, 92)])
        towers.append((x, w, h, rnd.random()))
        x += w + rnd.uniform(1, 6)
    tw = []
    for x, w, h, kind in towers:
        top = hz - h
        col = mix("#9A4A7A", "#C86A7A", rnd.uniform(0, 0.5))
        if kind < 0.2:  # rounded top
            tw.append(f'<path d="M {x:.1f} {hz:.1f} L {x:.1f} {top + w / 2:.1f} Q {x + w / 2:.1f} {top - w * 0.2:.1f} {x + w:.1f} {top + w / 2:.1f} L {x + w:.1f} {hz:.1f} Z" fill="{col}"/>')
        elif kind < 0.38:  # slanted roof
            tw.append(Q([(x, hz), (x, top), (x + w, top + w * 0.8), (x + w, hz)], col))
        elif kind < 0.5:  # setback crown with an antenna
            tw.append(f'<rect x="{x:.1f}" y="{top + 6:.1f}" width="{w:.1f}" height="{h - 6:.1f}" fill="{col}"/><rect x="{x + w * 0.2:.1f}" y="{top:.1f}" width="{w * 0.6:.1f}" height="7" fill="{col}"/>'
                      f'<line x1="{x + w / 2:.1f}" y1="{top:.1f}" x2="{x + w / 2:.1f}" y2="{top - 10:.1f}" stroke="{col}" stroke-width="1.2"/>')
        else:
            tw.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{col}"/>')
        tw.append(f'<rect x="{x:.1f}" y="{top + 3:.1f}" width="{w * 0.3:.1f}" height="{h - 3:.1f}" fill="#FFB890" opacity="0.25"/>')
        for yy in range(int(top) + 5, hz - 2, 5):
            for xx in range(int(x) + 2, int(x + w) - 1, 3):
                if rnd.random() < 0.18:
                    tw.append(f'<rect x="{xx}" y="{yy}" width="1.4" height="1.6" fill="#FFE2A8" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
        if h > 50:
            tw.append(f'<circle cx="{x + w / 2:.1f}" cy="{top - (10 if 0.38 <= kind < 0.5 else 1):.1f}" r="1.4" fill="#FF5050"/>')
    out.append("".join(tw))
    out.append(f'<rect x="0" y="230" width="600" height="{hz + 6 - 230}" fill="url(#{u}-haze)"/>')
    # far dunes, soft in the dust
    poly, _ = ridge_poly([(-10, 290), (80, 282), (200, 288), (300, 280), (420, 290), (520, 284), (610, 290)], 6, base=360, amp=3, fill=f"url(#{u}-far)")
    out.append(poly)
    out.append(mist(sunx, 290, 220, 14, "#FFD8A0", f"{u}-m1", 0.6))
    # a ghaf tree on the far dune
    out.append(ghaf(76, 302, 34, 4, dark="#7A3450", mid="#8E3E58", rim="#FFC890"))
    # three ranges of dunes, each with its shadowed slip faces
    d, c1 = dune_range([(-10, 314), (90, 302), (200, 316), (330, 298), (460, 314), (610, 302)], f"url(#{u}-d1)", f"url(#{u}-sh1)", f"{u}-a",
                       ["#B8483E", "#FFB070"], "#5A2048", 3, n_rip=40, toe=0.4)
    out.append(d)
    d, c2 = dune_range([(-10, 352), (110, 330), (220, 342), (330, 320), (346, 316), (356, 319), (470, 348), (610, 334)], f"url(#{u}-d2)", f"url(#{u}-sh2)", f"{u}-b",
                       ["#B8483E", "#FFC27A", "#C85A44"], "#4A1840", 5, n_rip=60, toe=0.3)
    out.append(d)
    # a pair of oryx on the crest, their long shadows running away from the sun
    ox1, ox2 = 318, 370
    for ox, kk in ((ox1, 0.62), (ox2, 0.46)):
        oy = y_on(c2, ox)
        out.append(f'<ellipse cx="{ox + 70 * kk:.1f}" cy="{oy + 3:.1f}" rx="{90 * kk:.1f}" ry="{6 * kk:.1f}" fill="#5A2048" opacity="0.4"/>')
    out.append(oryx(ox1, y_on(c2, ox1) + 1.5, 0.62))
    out.append(oryx(ox2, y_on(c2, ox2) + 1.5, 0.46))
    # the big dune in front, tyre tracks and footprints
    d, c3 = dune_range([(-10, 414), (110, 390), (226, 360), (246, 354), (262, 358), (420, 394), (610, 416)], f"url(#{u}-d3)", f"url(#{u}-sh3)", f"{u}-c",
                       ["#C85A3E", "#FFC27A", "#D86A44"], "#3E1236", 8, n_rip=80, toe=0.28)
    out.append(d)
    out.append(f'<clipPath id="{u}-c3"><polygon points="{P(c3 + [(610, 444), (-10, 444)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-c3)" fill="none" stroke-linecap="round">'
               '<path d="M -10 436 C 40 424 100 410 160 398 C 200 390 226 380 240 368" stroke="#B8483E" stroke-width="3" opacity="0.5"/>'
               '<path d="M 2 446 C 52 434 112 420 172 408 C 212 400 238 390 252 378" stroke="#B8483E" stroke-width="3" opacity="0.5"/>'
               '<path d="M -10 434 C 40 422 100 408 160 396" stroke="#FFD49A" stroke-width="1" opacity="0.6"/></g>')
    out.append("".join(f'<ellipse cx="{x:.1f}" cy="{y_on(c3, x) + 7 + (i % 2) * 3:.1f}" rx="2.2" ry="1.2" fill="#A8443E" opacity="0.6"/>' for i, x in enumerate(range(96, 226, 9))))
    # sand blowing off the crest
    out.append(f'<g stroke="#FFD8A8" stroke-width="1.2" stroke-linecap="round" opacity="0.5">' + "".join(
        f'<line x1="{x:.1f}" y1="{y_on(c3, x) - 1:.1f}" x2="{x + 26:.1f}" y2="{y_on(c3, x) - 5:.1f}"/>' for x in range(180, 250, 12)) + "</g>")
    out.append(falcon(408, 176, 0.75))
    out.append(gulls([(470, 210, 8), (488, 220, 6)], "#3A1A40", 1.6))
    return "\n".join(out)


BUILD = {
    "istanbul": (istanbul, "ISTANBUL", "TÜRKİYE · BOSPHORUS", "#3A1E3E", "#F2A04E", "#FFF1E4", "#F6B87A"),
    "dubai": (dubai, "DUBAI", "UNITED ARAB EMIRATES", "#2A1A40", "#F28A3A", "#FFF0E0", "#F9B67A"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("world", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
