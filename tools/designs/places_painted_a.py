"""American Places, painted edition A: New York, San Francisco, Grand Canyon, Washington DC, Miami Beach,
Honolulu and Savannah, each repainted as a small gouache scene with its own time of day and light."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from places_painted import Cam, palm_tree, facade_windows
from common import BEBAS, SERIF_IT, MONO, JOS
from poster import ANTON, poster


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


def cumulus(u, cx, cy, w, h, seed, lit="#FFF4E4", body="#F2D6C8", shade="#B9A2B8", n=26, light_dx=0.3, op=1.0):
    """Cumulus: puffs piled on a dome over a flat base; shaded belly, body, then lit crowns toward the light."""
    rnd = random.Random(seed)
    puffs = []
    for i in range(n):
        t = rnd.random()
        dome = math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2))
        r = h * rnd.uniform(0.28, 0.42) * (0.55 + 0.6 * dome)
        x = cx + (t - 0.5) * (w - r)
        y = cy - r * 0.6 - dome * (h - r * 1.2) * rnd.uniform(0.55, 1.0)
        puffs.append((x, y, r))
    puffs.sort(key=lambda p: -p[1])
    sh = "".join(f'<circle cx="{x - r * 0.12:.1f}" cy="{y + r * 0.2:.1f}" r="{r:.1f}"/>' for x, y, r in puffs)
    bd = "".join(f'<circle cx="{x + r * 0.06:.1f}" cy="{y - r * 0.04:.1f}" r="{r * 0.9:.1f}"/>' for x, y, r in puffs)
    li = "".join(f'<circle cx="{x + r * light_dx:.1f}" cy="{y - r * 0.32:.1f}" r="{r * 0.58:.1f}"/>' for x, y, r in puffs if rnd.random() < 0.8)
    base = f'<ellipse cx="{cx:.1f}" cy="{cy - h * 0.06:.1f}" rx="{w * 0.48:.1f}" ry="{h * 0.1:.1f}"/>'
    return (f'<g opacity="{op}"><g fill="{shade}">{base}{sh}</g><g fill="{body}">{bd}</g><g fill="{lit}" opacity="0.85">{li}</g></g>')


def stroll(x, base, h, col, head="#1A1418", flip=1, rim=None):
    """Small standing / walking person silhouette, h = height in px."""
    k = h / 100
    g = (f'<g transform="translate({x:.1f} {base:.1f}) scale({k * flip:.3f} {k:.3f})">'
         '<path d="M -9 -46 L 10 -46 L 13 -2 L 7 -2 L 4 -30 L -1 -2 L -7 -2 L -11 -44 Z" fill="#1A1620"/>'
         f'<path d="M -13 -86 Q 0 -94 13 -86 L 14 -44 L -12 -44 Z" fill="{col}"/>'
         f'<circle cx="0" cy="-95" r="8.5" fill="{head}"/>')
    if rim:
        g += f'<path d="M -13 -86 L -12 -44" stroke="{rim}" stroke-width="3" stroke-linecap="round"/>'
    return g + "</g>"


def reflect_streaks(seed, xs, y0, y1, colors, w=(2, 6), op=(0.3, 0.8), step=(3, 7)):
    """Broken horizontal dashes stacked under light sources -> reflections on rippled water."""
    rnd = random.Random(seed)
    out = []
    for x in xs:
        y = y0 + rnd.uniform(0, 3)
        c = rnd.choice(colors)
        while y < y1:
            ww = rnd.uniform(*w) * (1 + (y - y0) / max(1, y1 - y0))
            out.append(f'<rect x="{x - ww / 2 + rnd.uniform(-1.5, 1.5):.1f}" y="{y:.1f}" width="{ww:.1f}" height="1.6" fill="{c}" opacity="{rnd.uniform(*op) * (1 - 0.6 * (y - y0) / max(1, y1 - y0)):.2f}"/>')
            y += rnd.uniform(*step)
    return "".join(out)


# ---------------------------------------------------------------- New York (blue hour from Brooklyn Bridge Park)
def new_york():
    u = "nyb"
    out = [defs(
        lg(f"{u}-sky", [(0, "#0C1636"), (0.3, "#1C2E62"), (0.55, "#3C548C"), (0.72, "#8A6E9A"), (0.84, "#E28E7A"), (0.92, "#F6B470"), (1, "#F9CC88")], 0, 0, 0, 330, units="userSpaceOnUse"),
        lg(f"{u}-river", [(0, "#F2A672"), (0.08, "#8A6A8A"), (0.35, "#2E3C6A"), (1, "#0E1530")], 0, 318, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#6A6A9A"), (1, "#8A7A9E")]),
        lg(f"{u}-near", [(0, "#232A54"), (1, "#1A1E3E")]),
        lg(f"{u}-wtcL", [(0, "#F0B488"), (0.5, "#9A88B4"), (1, "#3E4A7E")]),
        lg(f"{u}-wtcR", [(0, "#4A5A92"), (1, "#222A56")]),
        lg(f"{u}-stone", [(0, "#8A7484"), (0.6, "#5E5068"), (1, "#3E3450")], 0, 0, 1, 0),
        lg(f"{u}-arch", [(0, "#F2A672"), (0.5, "#8A6E9A"), (1, "#3C548C")]),
        lg(f"{u}-pier", [(0, "#2A2238"), (1, "#120E1C")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(40, 2, (0, 40, 600, 150), "#F6EDE0", r=(0.6, 1.4), opacity=(0.3, 0.9)))
    out.append(glow(170, 318, 260, "#FFC488", f"{u}-dusk", 0.6))
    # long thin clouds lit from below by the set sun
    out.append('<g fill="#F2A08A" opacity="0.45">' + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="3"/>' for x, y, w in ((90, 176, 90), (40, 186, 60), (300, 158, 70), (520, 190, 80), (560, 200, 40))) + "</g>")
    # --- Lower Manhattan, far layer (hazy)
    rnd = random.Random(5)
    x = -10
    while x < 610:
        w = rnd.uniform(14, 30)
        h = rnd.uniform(30, 90)
        out.append(f'<rect x="{x:.1f}" y="{318 - h:.1f}" width="{w + 1:.1f}" height="{h:.1f}" fill="url(#{u}-far)"/>')
        x += w
    # --- near skyline towers (left of the bridge tower); (x, w, top, crown)
    towers = [(-6, 34, 236, "flat"), (26, 26, 214, "flat"), (50, 38, 250, "flat"), (86, 30, 196, "step"), (232, 32, 206, "flat"),
              (262, 26, 230, "flat"), (286, 30, 178, "flat"), (314, 22, 226, "flat"), (334, 30, 160, "gothic"), (362, 34, 214, "wavy"),
              (394, 30, 238, "flat"), (196, 38, 182, "flat"), (164, 30, 240, "flat")]
    for k, (x, w, top, crown) in enumerate(towers):
        out.append(f'<rect x="{x}" y="{top}" width="{w}" height="{320 - top}" fill="url(#{u}-near)"/>')
        out.append(f'<rect x="{x}" y="{top}" width="2.5" height="{320 - top}" fill="#E8A07A" opacity="0.55"/>')
        r2 = random.Random(k * 13)
        for yy in range(int(top) + 6, 314, 6):
            for xx in range(int(x) + 4, int(x + w) - 3, 5):
                if r2.random() < 0.38:
                    out.append(f'<rect x="{xx}" y="{yy}" width="2.4" height="2.6" fill="{r2.choice(["#FFD98E", "#F7C873", "#FFF0C8", "#BFD4F0"])}" opacity="{r2.uniform(0.55, 1):.2f}"/>')
        if crown == "step":
            out.append(f'<polygon points="{P([(x + 4, top), (x + 4, top - 10), (x + 9, top - 10), (x + 9, top - 18), (x + w - 9, top - 18), (x + w - 9, top - 10), (x + w - 4, top - 10), (x + w - 4, top)])}" fill="#232A54"/>')
            out.append(f'<rect x="{x + w / 2 - 1:.1f}" y="{top - 34}" width="2" height="16" fill="#232A54"/>')
        if crown == "gothic":   # the old terracotta Gothic tower with a copper pyramid crown
            out.append(f'<polygon points="{P([(x + 3, top), (x + 3, top - 16), (x + w - 3, top - 16), (x + w - 3, top)])}" fill="#262C56"/>')
            out.append(f'<polygon points="{P([(x + 5, top - 16), (x + w / 2, top - 46), (x + w - 5, top - 16)])}" fill="#3E7A78"/>')
            out.append(f'<polygon points="{P([(x + w / 2, top - 46), (x + w - 5, top - 16), (x + w / 2 + 2, top - 16)])}" fill="#2A5458"/>')
            out.append(f'<line x1="{x + w / 2:.1f}" y1="{top - 46}" x2="{x + w / 2:.1f}" y2="{top - 58}" stroke="#3E7A78" stroke-width="1.6"/>')
            out.append(f'<rect x="{x + 3}" y="{top - 16}" width="{w - 6}" height="16" fill="#FFE2A0" opacity="0.35"/>')
            for t in (0.25, 0.5, 0.75):
                out.append(f'<line x1="{x + w * t:.1f}" y1="{top - 16}" x2="{x + w * t:.1f}" y2="{top - 24}" stroke="#262C56" stroke-width="2"/>')
        if crown == "wavy":     # rippling stainless tower
            out.append(f'<g fill="none" stroke="#7A86B8" stroke-width="1" opacity="0.6">' + "".join(
                f'<path d="M {x + i * 5} {top} q 2 20 0 40 q -2 20 0 40 q 2 20 0 {320 - top - 80}"/>' for i in range(1, 7)) + "</g>")
    # --- the tallest tower: tapering facets, mirror-glass catching the afterglow, spire with beacon
    base_y, top_y = 320, 138
    out.append(f'<polygon points="{P([(118, base_y), (118, 270), (134, top_y), (152, top_y), (152, base_y)])}" fill="url(#{u}-wtcL)"/>')
    out.append(f'<polygon points="{P([(152, base_y), (152, top_y), (170, top_y), (186, 270), (186, base_y)])}" fill="url(#{u}-wtcR)"/>')
    out.append(f'<polygon points="{P([(118, 270), (134, top_y), (152, top_y), (152, 270)])}" fill="#FFE0B0" opacity="0.12"/>')
    out.append(f'<line x1="152" y1="{top_y}" x2="152" y2="{base_y}" stroke="#FFE6C0" stroke-width="1.6" opacity="0.7"/>')
    out.append(f'<rect x="130" y="{top_y - 4}" width="44" height="5" fill="#2A3260"/>')
    out.append(f'<polygon points="{P([(150, top_y - 4), (154, top_y - 4), (152.6, 96), (151.4, 96)])}" fill="#2A3260"/>')
    out.append(glow(152, 97, 12, "#FFFFFF", f"{u}-bc", 0.8) + '<circle cx="152" cy="97" r="1.8" fill="#FFFFFF"/>')
    r3 = random.Random(77)
    for yy in range(top_y + 10, 316, 5):
        for xx in range(122, 184, 5):
            if r3.random() < 0.18 and (xx < 152 or True):
                out.append(f'<rect x="{xx}" y="{yy}" width="2.2" height="2.2" fill="#FFF0C8" opacity="{r3.uniform(0.4, 0.9):.2f}"/>')
    # shoreline: piers and the waterfront
    out.append(f'<rect x="-10" y="314" width="430" height="8" fill="#141834"/>')
    out.append(dots(80, 9, (0, 314, 420, 320), "#FFD98E", r=(0.6, 1.4), opacity=(0.5, 1)))
    # --- river
    out.append(f'<rect x="-10" y="320" width="620" height="124" fill="url(#{u}-river)"/>')
    rx_ = [x for x in range(4, 420, 7)]
    out.append(reflect_streaks(11, rx_, 324, 404, ["#FFD98E", "#F7C873", "#FFF0C8"], w=(2, 5), op=(0.25, 0.75), step=(4, 9)))
    out.append(reflect_streaks(12, [152, 150, 154], 324, 380, ["#F6B480"], w=(5, 10), op=(0.4, 0.8), step=(3, 5)))
    out.append(dots(120, 13, (0, 330, 600, 420), "#8EA0D0", r=(0.5, 1.2), opacity=(0.2, 0.6)))
    # ferry crossing with its wake
    fx, fy = 262, 352
    out.append(f'<path d="M {fx + 34} {fy + 2} Q {fx + 90} {fy + 6} {fx + 160} {fy + 4}" fill="none" stroke="#DCE4F4" stroke-width="2.2" opacity="0.45"/>')
    out.append(f'<path d="M {fx + 34} {fy + 4} Q {fx + 80} {fy + 12} {fx + 140} {fy + 14}" fill="none" stroke="#DCE4F4" stroke-width="1.6" opacity="0.3"/>')
    out.append(f'<g transform="translate({fx} {fy})"><path d="M -34 -4 L 36 -4 L 30 6 L -28 6 Z" fill="#E8E2DA"/><rect x="-34" y="-1" width="70" height="2" fill="#2E4A7A"/>'
               '<rect x="-24" y="-14" width="48" height="10" fill="#F0ECE4"/><rect x="-14" y="-21" width="26" height="7" fill="#F0ECE4"/>'
               + "".join(f'<rect x="{-21 + i * 6}" y="-12" width="3.5" height="4" fill="#FFD98E"/>' for i in range(8))
               + '<rect x="-2" y="-27" width="3" height="6" fill="#2E4A7A"/></g>')
    out.append(reflect_streaks(14, range(fx - 22, fx + 26, 6), fy + 8, fy + 30, ["#FFD98E"], w=(2, 4), op=(0.3, 0.7)))
    # --- the Brooklyn Bridge: Manhattan tower far, Brooklyn tower near, cables and the web of stays
    MT = (196, 222)       # Manhattan tower top centre
    BT = (472, 112)       # Brooklyn tower top centre
    deck_l, deck_r = (150, 292), (610, 300)

    def deck_y(x):
        return deck_l[1] + (deck_r[1] - deck_l[1]) * (x - deck_l[0]) / (deck_r[0] - deck_l[0])

    # Manhattan tower (small, hazy)
    out.append(f'<polygon points="{P([(184, 320), (184, MT[1] + 4), (188, MT[1]), (204, MT[1]), (208, MT[1] + 4), (208, 320)])}" fill="#4A4664"/>')
    for ax in (190, 200):
        out.append(f'<path d="M {ax} 296 L {ax} {MT[1] + 30} Q {ax + 3} {MT[1] + 20} {ax + 6} {MT[1] + 30} L {ax + 6} 296 Z" fill="url(#{u}-arch)" opacity="0.85"/>')
    # main cable spans: catenaries from Brooklyn tower to Manhattan tower
    def catenary(a, b, sag, n=40):
        pts = []
        for i in range(n + 1):
            t = i / n
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + sag * 4 * t * (1 - t)))
        return pts
    cab1 = catenary((BT[0] - 30, BT[1] + 14), (MT[0] - 8, MT[1] + 4), 118)
    cab2 = catenary((BT[0] - 22, BT[1] + 16), (MT[0] + 6, MT[1] + 6), 120)
    # deck
    out.append(f'<polygon points="{P([(deck_l[0], deck_l[1] - 5), (610, deck_r[1] - 10), (610, deck_r[1] + 6), (deck_l[0], deck_l[1] + 2)])}" fill="#262038"/>')
    out.append(f'<polyline points="{P([(deck_l[0], deck_l[1] - 5), (610, deck_r[1] - 10)])}" fill="none" stroke="#F2A672" stroke-width="1.4" opacity="0.6"/>')
    # traffic lights along the deck
    rnd = random.Random(21)
    for i in range(36):
        x = rnd.uniform(160, 600)
        out.append(f'<circle cx="{x:.1f}" cy="{deck_y(x) - 1:.1f}" r="{rnd.uniform(0.8, 1.6):.1f}" fill="{rnd.choice(["#FF5A4A", "#FFF2C8", "#FFD98E"])}"/>')
    # suspenders + stays (thin web)
    web = []
    for cab in (cab1, cab2):
        for (x, y) in cab[2:-2:1]:
            web.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{deck_y(x) - 4:.1f}"/>')
    for i in range(14):
        x = BT[0] - 36 - i * 13
        web.append(f'<line x1="{BT[0] - 28}" y1="{BT[1] + 18}" x2="{x:.1f}" y2="{deck_y(x) - 4:.1f}"/>')
    for i in range(8):
        x = BT[0] + 40 + i * 14
        web.append(f'<line x1="{BT[0] + 28}" y1="{BT[1] + 18}" x2="{x:.1f}" y2="{deck_y(x) - 4:.1f}"/>')
    out.append(f'<g stroke="#2A2440" stroke-width="1" opacity="0.75">' + "".join(web) + "</g>")
    for cab, sw in ((cab1, 3.0), (cab2, 2.6)):
        out.append(f'<polyline points="{P(cab)}" fill="none" stroke="#1E1A30" stroke-width="{sw}"/>')
    out.append(f'<polyline points="{P(cab1)}" fill="none" stroke="#F2B080" stroke-width="0.9" opacity="0.6" transform="translate(0 -1.2)"/>')
    # back-span cables to the Brooklyn anchorage (off frame right)
    for dx, sw in ((22, 3.0), (30, 2.6)):
        bk = catenary((BT[0] + dx, BT[1] + 16), (640, 268), 30)
        out.append(f'<polyline points="{P(bk)}" fill="none" stroke="#1E1A30" stroke-width="{sw}"/>')
        out.append(f'<g stroke="#2A2440" stroke-width="1" opacity="0.7">' + "".join(
            f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{deck_y(x) - 4:.1f}"/>' for x, y in bk[2::3]) + "</g>")
    # Brooklyn tower: granite and limestone, two pointed Gothic arches, backlit with a warm rim on the west face
    tl, tr, tb = BT[0] - 46, BT[0] + 46, 336
    out.append(f'<polygon points="{P([(tl - 4, tb), (tl, BT[1] + 22), (tl - 3, BT[1] + 22), (tl - 3, BT[1] + 8), (tr + 3, BT[1] + 8), (tr + 3, BT[1] + 22), (tr, BT[1] + 22), (tr + 4, tb)])}" fill="url(#{u}-stone)"/>')
    out.append(f'<rect x="{tl - 6}" y="{BT[1]}" width="{tr - tl + 12}" height="9" fill="#4E4260"/>')
    out.append(f'<rect x="{tl - 6}" y="{BT[1]}" width="{tr - tl + 12}" height="2" fill="#F2B080" opacity="0.7"/>')
    # stone courses
    out.append(f'<g stroke="#2E2640" stroke-width="1" opacity="0.35">' + "".join(
        f'<line x1="{tl - 3}" y1="{y}" x2="{tr + 3}" y2="{y}"/>' for y in range(BT[1] + 18, tb, 7)) + "</g>")
    # weathered stone blocks
    rb = random.Random(31)
    blk = []
    for y in range(BT[1] + 18, tb - 4, 7):
        x = tl - 3 + (rb.uniform(0, 8) if (y // 7) % 2 else 0)
        while x < tr + 2:
            w = rb.uniform(9, 18)
            blk.append(f'<rect x="{x:.1f}" y="{y}" width="{min(w, tr + 3 - x):.1f}" height="7" fill="{rb.choice(["#A08A90", "#4A3E58", "#8A7480", "#3A3048"])}" opacity="{rb.uniform(0.08, 0.22):.2f}"/>')
            x += w
    out.append("".join(blk))
    # belt course at deck level, darker base below it
    out.append(f'<rect x="{tl - 4}" y="{deck_y(BT[0]) - 2:.1f}" width="{tr - tl + 8}" height="{tb - deck_y(BT[0]) + 2:.1f}" fill="#2A2238" opacity="0.35"/>')
    out.append(f'<rect x="{tl - 6}" y="{deck_y(BT[0]) - 4:.1f}" width="{tr - tl + 12}" height="4" fill="#4E4260"/>')
    # pilasters
    for px in (tl - 3, BT[0] - 4, tr - 7):
        out.append(f'<rect x="{px}" y="{BT[1] + 9}" width="10" height="{tb - BT[1] - 9}" fill="#3E3450" opacity="0.35"/>')
    # Gothic arches showing the sky through the tower
    for ax in (tl + 9, BT[0] + 8):
        aw = 28
        top = BT[1] + 52
        spring = top + 34
        out.append(f'<path d="M {ax} {deck_y(ax) - 4:.1f} L {ax} {spring} Q {ax} {top + 6} {ax + aw / 2} {top} Q {ax + aw} {top + 6} {ax + aw} {spring} L {ax + aw} {deck_y(ax + aw) - 4:.1f} Z" fill="url(#{u}-arch)"/>')
        # deep reveal on the shadowed inner jamb, voussoirs around the pointed head
        out.append(f'<path d="M {ax + aw} {deck_y(ax + aw) - 4:.1f} L {ax + aw} {spring} Q {ax + aw} {top + 6} {ax + aw / 2} {top} Q {ax + aw - 2} {top + 10} {ax + aw - 5} {spring} L {ax + aw - 5} {deck_y(ax + aw) - 4:.1f} Z" fill="#3A3048" opacity="0.9"/>')
        out.append(f'<path d="M {ax} {spring} Q {ax} {top + 6} {ax + aw / 2} {top} Q {ax + aw} {top + 6} {ax + aw} {spring}" fill="none" stroke="#2A2238" stroke-width="2.4"/>')
        out.append(f'<path d="M {ax - 3} {spring} Q {ax - 3} {top + 3} {ax + aw / 2} {top - 4} Q {ax + aw + 3} {top + 3} {ax + aw + 3} {spring}" fill="none" stroke="#C8A890" stroke-width="1.4" opacity="0.5"/>')
        # cables passing through the arches
        out.append(f'<line x1="{ax}" y1="{spring + 18}" x2="{ax + aw}" y2="{spring + 22}" stroke="#2A2440" stroke-width="1" opacity="0.6"/>')
    # small upper lancet windows
    for ax in (tl + 16, BT[0] + 15):
        out.append(f'<path d="M {ax} {BT[1] + 40} L {ax} {BT[1] + 28} Q {ax + 7} {BT[1] + 20} {ax + 14} {BT[1] + 28} L {ax + 14} {BT[1] + 40} Z" fill="#2A2238"/>')
    out.append(f'<polyline points="{P([(tl - 4, tb), (tl, BT[1] + 22), (tl - 3, BT[1] + 22), (tl - 3, BT[1] + 8)])}" fill="none" stroke="#F6B480" stroke-width="2.2" opacity="0.8"/>')
    # lamps on the tower
    for lx in (tl + 4, tr - 4):
        out.append(glow(lx, 284, 10, "#FFE2A0", f"{u}-tl{lx}", 0.8))
    # tower footing in the water + its reflection
    out.append(f'<rect x="{tl - 10}" y="{tb - 6}" width="{tr - tl + 20}" height="10" fill="#2A2238"/>')
    out.append(f'<rect x="{tl - 4}" y="{tb + 4}" width="{tr - tl + 8}" height="40" fill="#141830" opacity="0.5"/>')
    out.append(reflect_streaks(15, [tl + 22, BT[0] + 22], tb + 6, 400, ["#F2A672"], w=(6, 12), op=(0.3, 0.6)))
    # --- foreground: Brooklyn waterfront promenade with railing, lamps and onlookers
    out.append(f'<path d="M -10 404 L 610 396 L 610 444 L -10 444 Z" fill="url(#{u}-pier)"/>')
    out.append('<g stroke="#0E0A16" stroke-width="2.4">' + "".join(f'<line x1="{x}" y1="{404 - x * 8 / 600 - 22:.1f}" x2="{x}" y2="{404 - x * 8 / 600:.1f}"/>' for x in range(-4, 610, 22)) + "</g>")
    out.append('<path d="M -10 382 L 610 374" stroke="#0E0A16" stroke-width="3.5"/><path d="M -10 381 L 610 373" stroke="#F2A672" stroke-width="1" opacity="0.5"/>')
    out.append('<path d="M -10 392 L 610 384" stroke="#0E0A16" stroke-width="1.6"/>')
    # old pier pilings in the water
    for x, h in ((32, 18), (44, 14), (56, 20), (520, 16), (534, 22), (548, 14), (562, 18)):
        out.append(f'<rect x="{x}" y="{378 - h}" width="5" height="{h + 4}" fill="#1A1626"/><rect x="{x}" y="{378 - h}" width="1.6" height="{h}" fill="#F2A672" opacity="0.5"/>')
    for x, k in ((92, 1.0), (430, 0.95)):
        bx = x
        out.append(f'<rect x="{bx - 1.6}" y="{318}" width="3.2" height="{82}" fill="#0E0A16"/>')
        out.append(f'<path d="M {bx - 7} 322 L {bx + 7} 322 L {bx + 5} 310 L {bx - 5} 310 Z" fill="#0E0A16"/>')
        out.append(glow(bx, 316, 34, "#FFE2A0", f"{u}-lmp{x}", 0.9))
        out.append(f'<rect x="{bx - 4}" y="311" width="8" height="10" fill="#FFF0C8"/>')
    for x in (92, 430):
        out.append(f'<ellipse cx="{x}" cy="{402 - x * 8 / 600:.1f}" rx="46" ry="5" fill="#FFD98E" opacity="0.22"/>')
    out.append(stroll(212, 402, 46, "#3E2E48", rim="#F6B480"))
    out.append(stroll(228, 402, 42, "#6A3048", flip=-1, rim="#F6B480"))
    out.append(stroll(350, 400, 40, "#2A3A5A", rim="#F6B480"))
    # gulls
    out.append('<g fill="none" stroke="#F6E6D8" stroke-width="1.8" stroke-linecap="round" opacity="0.85"><path d="M 300 184 q 6 -5 12 0 q 6 -5 12 0"/><path d="M 326 200 q 4 -4 8 0 q 4 -4 8 0"/></g>')
    return "\n".join(out)


# ---------------------------------------------------------------- San Francisco (golden hour from the Marin headlands)
def fog_bank(u, k, pts, seed, lit="#FFE6C4", body="#E8D4CC", shade="#A898B0", r=(10, 26), n=60, base=None):
    """Rolling fog: puffs strung along a polyline, flat-bottomed by a filled body underneath."""
    rnd = random.Random(seed)
    sh, bd, li = [], [], []
    for i in range(n):
        t = i / (n - 1)
        j = min(int(t * (len(pts) - 1)), len(pts) - 2)
        tt = t * (len(pts) - 1) - j
        x = pts[j][0] + (pts[j + 1][0] - pts[j][0]) * tt + rnd.uniform(-6, 6)
        y = pts[j][1] + (pts[j + 1][1] - pts[j][1]) * tt + rnd.uniform(-4, 6)
        rr = rnd.uniform(*r)
        sh.append(f'<ellipse cx="{x - rr * 0.15:.1f}" cy="{y + rr * 0.3:.1f}" rx="{rr * 1.4:.1f}" ry="{rr:.1f}"/>')
        bd.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rr * 1.3:.1f}" ry="{rr * 0.85:.1f}" opacity="{rnd.uniform(0.55, 0.9):.2f}"/>')
        li.append(f'<ellipse cx="{x + rr * 0.3:.1f}" cy="{y - rr * 0.4:.1f}" rx="{rr * 0.9:.1f}" ry="{rr * 0.4:.1f}" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    base_poly = ""
    if base is not None:
        poly = [(x, y + 8) for x, y in pts] + [(pts[-1][0], base), (pts[0][0], base)]
        base_poly = f'<polygon points="{P(poly)}" fill="url(#{u}-fogb{k})"/>'
    return (defs(lg(f"{u}-fogb{k}", [(0, body), (1, shade, 0.0)])) + base_poly
            + f'<g fill="{shade}" opacity="0.35">{"".join(sh)}</g><g fill="{body}">{"".join(bd)}</g><g fill="{lit}" opacity="0.8">{"".join(li)}</g>')


def gg_tower(cx, top, base, s, u, k, lit="#E2532F", shade="#8E2A22", hi="#F8A066", portal_ys=None):
    """Art Deco suspension tower: two stepped legs joined by portal struts. s = scale (1 -> ~70 px wide)."""
    out = []
    leg_w, gap = 20 * s, 30 * s
    H = base - top
    xl, xr = cx - gap / 2 - leg_w, cx + gap / 2
    portal_ys = portal_ys or [0.0, 0.17, 0.36, 0.57]
    for x0 in (xl, xr):
        # three setbacks: each section a bit narrower going up
        secs = [(0.0, 0.3, 0.0), (0.3, 0.6, 1.2 * s), (0.6, 1.0, 2.4 * s)]
        for a, b, ins in secs:
            ya, yb = top + H * a, top + H * b
            out.append(f'<rect x="{x0 + ins:.1f}" y="{ya:.1f}" width="{leg_w - 2 * ins:.1f}" height="{yb - ya + 0.5:.1f}" fill="{lit}"/>')
            out.append(f'<rect x="{x0 + ins:.1f}" y="{ya:.1f}" width="{(leg_w - 2 * ins) * 0.38:.1f}" height="{yb - ya + 0.5:.1f}" fill="{shade}"/>')
            out.append(f'<rect x="{x0 + ins + (leg_w - 2 * ins) * 0.38:.1f}" y="{ya:.1f}" width="{max(0.8, 1.2 * s):.1f}" height="{yb - ya:.1f}" fill="{hi}" opacity="0.8"/>')
            # vertical recessed fluting on the lit face
            out.append(f'<rect x="{x0 + ins + (leg_w - 2 * ins) * 0.66:.1f}" y="{ya + 2 * s:.1f}" width="{max(0.8, 1.6 * s):.1f}" height="{yb - ya - 4 * s:.1f}" fill="{shade}" opacity="0.55"/>')
    # portal struts with Art Deco stepped panels
    for i, t in enumerate(portal_ys):
        y = top + H * t + (6 * s if i == 0 else 0)
        h = (14 if i == 0 else 10 - i * 1.4) * s
        out.append(f'<rect x="{xl + leg_w * 0.6:.1f}" y="{y:.1f}" width="{gap + leg_w * 0.8:.1f}" height="{h:.1f}" fill="{lit}"/>')
        out.append(f'<rect x="{xl + leg_w * 0.6:.1f}" y="{y + h * 0.7:.1f}" width="{gap + leg_w * 0.8:.1f}" height="{h * 0.3:.1f}" fill="{shade}"/>')
        for j in range(4):
            px = xl + leg_w + gap * (j + 0.5) / 4 - 2 * s
            out.append(f'<rect x="{px:.1f}" y="{y + h * 0.2:.1f}" width="{4 * s:.1f}" height="{h * 0.45:.1f}" fill="{shade}" opacity="0.6"/>')
    # cap
    for x0 in (xl, xr):
        out.append(f'<rect x="{x0 + 2.4 * s:.1f}" y="{top - 6 * s:.1f}" width="{leg_w - 4.8 * s:.1f}" height="{6 * s:.1f}" fill="{lit}"/>')
        out.append(f'<rect x="{x0 + 2.4 * s:.1f}" y="{top - 6 * s:.1f}" width="{(leg_w - 4.8 * s) * 0.4:.1f}" height="{6 * s:.1f}" fill="{shade}"/>')
        out.append(f'<circle cx="{x0 + leg_w / 2:.1f}" cy="{top - 7 * s:.1f}" r="{max(1.2, 1.6 * s):.1f}" fill="#FF4A3A"/>')
    return "".join(out), (xl + leg_w / 2, top - 2 * s), (xr + leg_w / 2, top - 2 * s)


def san_francisco():
    u = "sfg"
    out = [defs(
        lg(f"{u}-sky", [(0, "#5878A8"), (0.3, "#8E9CC2"), (0.55, "#D8B8B8"), (0.78, "#F4CDA4"), (1, "#F9E0B4")], 0, 40, 0, 290, units="userSpaceOnUse"),
        lg(f"{u}-bay", [(0, "#B9B4C4"), (0.15, "#6E88A8"), (0.6, "#2E5478"), (1, "#1A3858")], 0, 270, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-hill", [(0, "#E8B870"), (0.5, "#C88E4E"), (1, "#7A5A34")]),
        lg(f"{u}-city", [(0, "#F6D8BC"), (1, "#D8B4A8")]),
        lg(f"{u}-deck", [(0, "#C8462C"), (1, "#7A2420")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(640, 210, 300, "#FFE2A8", f"{u}-sun", 0.75))
    # high streaks of cloud catching the gold light
    rnd = random.Random(4)
    for cx, cy, w in ((120, 120, 150), (430, 96, 130), (330, 150, 90), (560, 130, 70)):
        for i in range(7):
            out.append(f'<ellipse cx="{cx + rnd.uniform(-w * 0.4, w * 0.4):.1f}" cy="{cy + rnd.uniform(-6, 6):.1f}" rx="{rnd.uniform(0.25, 0.5) * w:.1f}" ry="{rnd.uniform(3, 7):.1f}" fill="{rnd.choice(["#F8DCC4", "#FFF0E0", "#E8C4C0"])}" opacity="{rnd.uniform(0.25, 0.55):.2f}"/>')
        out.append(f'<ellipse cx="{cx + w * 0.1:.1f}" cy="{cy - 2:.1f}" rx="{w * 0.3:.1f}" ry="2" fill="#FFF6E8" opacity="0.6"/>')
    # East Bay hills and the city lit by the low sun
    poly, _ = ridge_poly([(-10, 258), (80, 248), (180, 256), (300, 246), (420, 256), (610, 250)], 3, base=290, amp=4, fill="#A898B8")
    out.append(poly)
    rnd = random.Random(8)
    city = []
    x = 0
    while x < 210:
        w = rnd.uniform(5, 11)
        h = rnd.uniform(8, 34) * (1.4 if 80 < x < 150 else 1)
        city.append((x, w, h))
        x += w + rnd.uniform(0, 2)
    for x, w, h in city:
        out.append(f'<rect x="{x:.1f}" y="{272 - h:.1f}" width="{w:.1f}" height="{h + 2:.1f}" fill="url(#{u}-city)"/>')
        out.append(f'<rect x="{x:.1f}" y="{272 - h:.1f}" width="{w * 0.35:.1f}" height="{h + 2:.1f}" fill="#B89AA8" opacity="0.6"/>')
    out.append(f'<polygon points="{P([(116, 274), (121, 214), (126, 274)])}" fill="#F8E2CC"/><polygon points="{P([(116, 274), (121, 214), (119.5, 274)])}" fill="#C0A4B0"/>')
    out.append(f'<rect x="-10" y="270" width="230" height="4" fill="#C8A8A8"/>')
    # Alcatraz
    out.append(f'<path d="M 20 284 Q 30 276 46 276 L 66 278 Q 74 280 78 284 Z" fill="#8A7A8C"/><rect x="38" y="270" width="18" height="8" fill="#D8C0B8"/><rect x="58" y="264" width="2.4" height="14" fill="#E8D4C8"/>')
    # bay
    out.append(f'<rect x="-10" y="280" width="620" height="164" fill="url(#{u}-bay)"/>')
    rnd = random.Random(12)
    out.append("".join(f'<rect x="{rnd.uniform(-10, 600):.1f}" y="{(yy := rnd.uniform(286, 440)):.1f}" width="{rnd.uniform(4, 16) * (yy - 260) / 80:.1f}" height="1.4" rx="0.7" fill="#9FC0DC" opacity="{rnd.uniform(0.2, 0.55):.2f}"/>' for _ in range(160)))
    # Presidio hills on the south shore, half drowned in fog
    poly, pl = ridge_poly([(330, 282), (420, 268), (500, 272), (610, 262)], 7, base=300, amp=4, fill="#5E7A62")
    out.append(poly)
    out.append(tree_line(pl, 9, ["#3E5A48", "#4A6650"], density=1.4, hmin=5, hmax=10, xmin=340, xmax=610))
    # --- the bridge
    NT_cx, NT_top, NT_base = 236, 104, 360
    ST_cx, ST_top, ST_base = 470, 182, 296
    deck = lambda x: 318 - (x - 0) * (318 - 268) / 470 if x < 470 else 268 - (x - 470) * 0.08
    # south tower first (far), fog wraps its feet later
    st, st_l, st_r = gg_tower(ST_cx, ST_top, ST_base, 0.42, u, 1, lit="#D45A3C", shade="#9A3A30", hi="#F09A70", portal_ys=[0.0, 0.2, 0.42])
    out.append(st)
    # catenary helpers
    def cat(a, b, sag, n=48):
        return [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + sag * 4 * t * (1 - t)) for t in (i / n for i in range(n + 1))]
    nt, nt_l, nt_r = gg_tower(NT_cx, NT_top, NT_base, 1.0, u, 0)
    main_w = cat(nt_r, st_r, 128)
    main_e = cat(nt_l, st_l, 128)
    back = cat(st_r, (640, 232), 14)
    side_w = cat((-40, 330), nt_r, 34)
    side_e = cat((-40, 318), nt_l, 34)
    # suspenders (far span first)
    sus = []
    for cab in (main_w, side_w, back):
        for x, y in cab[1:-1]:
            sus.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{deck(x) - 3:.1f}"/>')
    out.append('<g stroke="#B8402C" stroke-width="1.2">' + "".join(sus) + "</g>")
    # deck with stiffening truss
    dl = [(-10, deck(-10)), (610, deck(610))]
    out.append(f'<polygon points="{P([(-10, deck(-10) - 5), (470, 263), (610, 256), (610, 262), (470, 270), (-10, deck(-10) + 14)])}" fill="url(#{u}-deck)"/>')
    out.append(f'<polyline points="{P([(-10, deck(-10) - 5), (470, 263), (610, 256)])}" fill="none" stroke="#F8A070" stroke-width="1.6"/>')
    tr_ = []
    for i in range(60):
        x = -10 + i * 8
        if x > 470:
            break
        th = 19 - 12 * (x + 10) / 480
        ya = deck(x) - 4
        tr_.append(f'<line x1="{x:.1f}" y1="{ya:.1f}" x2="{x + 4:.1f}" y2="{ya + th:.1f}"/><line x1="{x + 4:.1f}" y1="{ya + th:.1f}" x2="{x + 8:.1f}" y2="{ya - 0.8:.1f}"/>')
    out.append('<g stroke="#5A1A18" stroke-width="1" opacity="0.8">' + "".join(tr_) + "</g>")
    # traffic on the deck
    rnd = random.Random(31)
    for i in range(22):
        x = rnd.uniform(0, 600)
        out.append(f'<rect x="{x:.1f}" y="{deck(x) - 7:.1f}" width="{max(2, 6 - x / 120):.1f}" height="{max(1.5, 3.5 - x / 200):.1f}" rx="1" fill="{rnd.choice(["#F4F0E8", "#2E3A4A", "#E8C060", "#5A7A9A", "#B8B8C0"])}"/>')
    # main cables
    for cab, sw in ((main_e, 3.2), (side_e, 3.6)):
        out.append(f'<polyline points="{P(cab)}" fill="none" stroke="#8E2A22" stroke-width="{sw}"/>')
    for cab, sw in ((main_w, 3.6), (side_w, 4.2), (back, 2.4)):
        out.append(f'<polyline points="{P(cab)}" fill="none" stroke="#C8462C" stroke-width="{sw}"/>')
        out.append(f'<polyline points="{P(cab)}" fill="none" stroke="#FFB27A" stroke-width="1.1" opacity="0.8" transform="translate(0.6 -1)"/>')
    # north tower on top
    out.append(nt)
    # the north pier: concrete fender at the waterline
    out.append(f'<path d="M {NT_cx - 46} {NT_base - 6} L {NT_cx + 46} {NT_base - 6} L {NT_cx + 52} {NT_base + 16} L {NT_cx - 52} {NT_base + 16} Z" fill="#D8C4AC"/>'
               f'<path d="M {NT_cx - 46} {NT_base - 6} L {NT_cx - 18} {NT_base - 6} L {NT_cx - 22} {NT_base + 16} L {NT_cx - 52} {NT_base + 16} Z" fill="#8E7E80"/>'
               f'<rect x="{NT_cx - 50}" y="{NT_base + 8}" width="102" height="8" fill="#5E5260" opacity="0.5"/>')
    out.append(f'<path d="M {NT_cx - 64} {NT_base + 16} Q {NT_cx} {NT_base + 22} {NT_cx + 66} {NT_base + 15}" fill="none" stroke="#E8F0F4" stroke-width="2" opacity="0.6"/>')
    out.append(f'<rect x="{NT_cx - 50}" y="{NT_base + 16}" width="100" height="30" fill="#8E2A22" opacity="0.18"/>')
    # fog rolling in through the Golden Gate, swallowing the south tower's feet and the Presidio
    out.append(fog_bank(u, 0, [(330, 290), (400, 282), (470, 274), (540, 266), (620, 258)], 5, r=(10, 22), n=70, base=310))
    out.append(fog_bank(u, 1, [(380, 300), (450, 296), (520, 290), (620, 284)], 6, r=(8, 18), n=50, base=318))
    out.append(fog_bank(u, 2, [(520, 236), (560, 226), (620, 214)], 7, r=(10, 22), n=24))
    out.append(mist(470, 286, 150, 30, "#F8E4D4", f"{u}-m1", 0.7))
    out.append(mist(560, 252, 90, 34, "#FFEAD4", f"{u}-m2", 0.6))
    out.append(mist(420, 304, 110, 16, "#E8DCE0", f"{u}-m3", 0.6))
    # wisps creeping over the roadway
    rnd = random.Random(55)
    for i in range(14):
        x = rnd.uniform(340, 600)
        out.append(f'<ellipse cx="{x:.1f}" cy="{deck(x) - rnd.uniform(0, 14):.1f}" rx="{rnd.uniform(20, 46):.1f}" ry="{rnd.uniform(3, 6):.1f}" fill="#FFF0E2" opacity="{rnd.uniform(0.25, 0.5):.2f}"/>')
    # reflections of the tower in the bay
    out.append(reflect_streaks(51, [NT_cx - 22, NT_cx - 18, NT_cx + 18, NT_cx + 22], NT_base + 18, 440, ["#D8502E", "#F08A5A"], w=(4, 9), op=(0.35, 0.75), step=(4, 8)))
    # Marin headland in the foreground, golden grass in raking light
    # rocky cliff where the headland drops into the water
    out.append(f'<path d="M 284 444 Q 360 392 440 372 Q 470 366 500 366 L 470 380 Q 400 400 330 444 Z" fill="#6A4A3A"/>')
    out.append(f'<clipPath id="{u}-cl"><path d="M 284 444 Q 360 392 440 372 Q 470 366 500 366 L 470 380 Q 400 400 330 444 Z"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-cl)">' + streaks(40, 61, (280, 360, 500, 444), ["#8E6448", "#4A3028", "#B07A50"], w=(1.5, 4), length=(10, 30), opacity=(0.4, 0.8), slant=0.3) + "</g>")
    out.append('<path d="M 280 442 Q 330 420 360 410" fill="none" stroke="#E8F0F4" stroke-width="2" opacity="0.6"/>')
    out.append(f'<path d="M 300 444 Q 380 380 470 362 Q 540 350 610 332 L 610 444 Z" fill="url(#{u}-hill)"/>')
    # a sandy trail along the crest
    out.append('<path d="M 610 352 Q 540 366 500 372 Q 470 378 452 392" fill="none" stroke="#F4D8A0" stroke-width="5" stroke-linecap="round" opacity="0.7"/>')
    out.append(f'<path d="M 300 444 Q 380 380 470 362 Q 540 350 610 332" fill="none" stroke="#FFD890" stroke-width="2.4" opacity="0.8"/>')
    out.append(grass(140, 41, (360, 360, 610, 444), ["#F2C878", "#E0A85A", "#B8803E", "#FFE0A0"], h=(6, 16)))
    # coastal scrub: clumps of small leaves, shadowed below and lit gold on the sun side
    rnd = random.Random(42)
    for cx, cy, r in ((430, 404, 22), (470, 392, 16), (520, 414, 26), (580, 398, 22), (560, 436, 30), (450, 436, 24), (600, 370, 16), (395, 430, 14)):
        for i in range(26):
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.uniform(0, 1) ** 0.6 * r
            x, y = cx + d * math.cos(a), cy + d * math.sin(a) * 0.5
            rr = rnd.uniform(3, 6.5)
            col = "#3E4A2A" if y > cy + 2 else ("#7A8040" if x > cx + 4 else "#56602E")
            out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rr * 1.3:.1f}" ry="{rr:.1f}" fill="{col}"/>')
        for i in range(6):
            out.append(f'<ellipse cx="{cx + rnd.uniform(0, r * 0.8):.1f}" cy="{cy - rnd.uniform(2, r * 0.45):.1f}" rx="3" ry="2" fill="#C8B866" opacity="0.8"/>')
    # a couple watching the bridge, warm light on their right side
    out.append(stroll(520, 356, 44, "#2E4A6A", rim="#FFD08A"))
    out.append(stroll(538, 354, 40, "#8A3A3A", flip=-1, rim="#FFD08A"))
    # sailboat heeling on the bay with a wake
    out.append('<path d="M 100 382 Q 140 388 196 386" fill="none" stroke="#E8F0F4" stroke-width="2" opacity="0.5"/>')
    out.append('<g transform="translate(96 380) rotate(-6)"><path d="M -18 0 L 18 0 L 13 7 L -14 7 Z" fill="#F4EEE4"/><path d="M 0 -2 L 0 -44 L 16 -4 Z" fill="#FFF6E8"/><path d="M -2 -2 L -2 -38 L -16 -4 Z" fill="#E8D8C8"/><rect x="-0.8" y="-46" width="1.6" height="46" fill="#4A4A4A"/></g>')
    out.append('<g fill="none" stroke="#4A4060" stroke-width="1.8" stroke-linecap="round"><path d="M 330 150 q 6 -5 12 0 q 6 -5 12 0"/><path d="M 356 164 q 4 -4 8 0 q 4 -4 8 0"/></g>')
    return "\n".join(out)


# ---------------------------------------------------------------- Grand Canyon (sunrise from the South Rim)
def temple(cx, w, top, base, seed):
    """Stepped Grand Canyon butte: Kaibab cap, Coconino cliff, Hermit slope, Supai ledges, Redwall cliff, Tonto apron.
    Returns (left profile top->base, right profile top->base)."""
    rnd = random.Random(seed)
    cap = rnd.choice([rnd.uniform(0.04, 0.12), rnd.uniform(0.15, 0.45)])
    H = base - top
    steps = [(0.0, 0.0), (0.03, 0.01), (0.15, 0.025), (0.24, 0.10), (0.30, 0.11), (0.35, 0.15), (0.41, 0.16), (0.46, 0.19),
             (0.60, 0.205), (0.78, 0.36), (1.0, 0.5 - cap / 2)]
    sides = []
    for sgn in (-1, 1):
        j = rnd.uniform(0.7, 1.3)
        pts = []
        acc = 0
        for f, hw in steps:
            acc = max(acc, hw * j * rnd.uniform(0.8, 1.25))
            dx = (cap / 2 + acc) * w
            pts.append((cx + sgn * dx + rnd.uniform(-1.5, 1.5), top + H * f * rnd.uniform(0.95, 1.05) * (f < 1) + H * (f == 1)))
        # sometimes a lower shoulder butte attached on this side
        if rnd.random() < 0.5:
            k = rnd.choice([3, 4, 5])
            x, y = pts[k]
            pts = pts[:k + 1] + [(x + sgn * w * rnd.uniform(0.08, 0.18), y + H * 0.01), (x + sgn * w * rnd.uniform(0.2, 0.28), y + H * 0.12)] + [
                (px + sgn * w * 0.2, py) for px, py in pts[k + 2:]]
        sides.append(pts)
    return sides[0], sides[1]


def canyon_layer(u, k, temples, rim, base, seed, tint, tint_op, body=("#E8A07A", "#B8604A"), shade="#4A2A5A", shade_op=0.42,
                 lit="#FFE4B4", lit_op=0.7, apron="#9A8070", texture=1.0, platform=True):
    """A row of stepped buttes standing on a shared Tonto platform; strata bands, west faces in shadow,
    east faces and rims catching the sunrise, then an atmospheric tint that grows with distance."""
    rnd = random.Random(seed)
    out = [defs(lg(f"{u}-body{k}", [(0, body[0]), (1, body[1])], 0, rim, 0, base, units="userSpaceOnUse"))]
    # shared platform so nothing floats
    if platform:
        plat = rough([(-10, rim + (base - rim) * 0.72), (200, rim + (base - rim) * 0.7), (400, rim + (base - rim) * 0.74), (610, rim + (base - rim) * 0.7)], seed, 3, 3)
        out.append(f'<polygon points="{P(plat + [(610, base), (-10, base)])}" fill="{apron}"/>')
        out.append(f'<polygon points="{P(plat + [(610, base), (-10, base)])}" fill="{shade}" opacity="{shade_op * 0.6:.2f}"/>')
        out.append(dots(int(60 * texture), seed, (-10, rim + (base - rim) * 0.74, 610, base), "#5E6A50", r=(0.8, 1.8), opacity=(0.4, 0.8)))
    for i, (cx, w, top) in enumerate(temples):
        lft, rgt = temple(cx, w, top, base, seed * 10 + i)
        poly = lft[::-1] + rgt
        H = base - top
        cid = f"{u}-t{k}-{i}"
        out.append(f'<clipPath id="{cid}"><polygon points="{P(poly)}"/></clipPath>')
        out.append(f'<polygon points="{P(poly)}" fill="url(#{u}-body{k})"/>')
        g = []
        # strata: Kaibab cream cap, white Coconino, red Supai ledges, deep Redwall, grey-green Tonto apron
        for a, b, c, op in ((0, 0.03, "#F4E2C8", 0.9), (0.03, 0.15, "#F6E8D4", 0.75), (0.15, 0.24, "#D8846A", 0.5), (0.30, 0.31, "#7A3A3A", 0.5),
                            (0.35, 0.36, "#7A3A3A", 0.45), (0.41, 0.42, "#7A3A3A", 0.45), (0.46, 0.60, "#A0403A", 0.55), (0.78, 1.0, apron, 0.75)):
            g.append(f'<rect x="{cx - w:.1f}" y="{top + H * a:.1f}" width="{2 * w:.1f}" height="{H * (b - a) + 0.5:.1f}" fill="{c}" opacity="{op}"/>')
        if texture:
            g.append(streaks(int(w * H / 220 * texture), seed + i, (cx - w / 2, top + H * 0.14, cx + w / 2, base), ["#6A3040", "#F4C8A0", "#8A4A48"], w=(0.8, 2.2), length=(4, H * 0.18), opacity=(0.15, 0.4), slant=0.05))
        # west face in shadow
        shadow = lft + [(cx - w * 0.04, base), (lft[0][0] + (rgt[0][0] - lft[0][0]) * 0.3, top)]
        g.append(f'<polygon points="{P(shadow)}" fill="{shade}" opacity="{shade_op}"/>')
        # east flank in full sun
        sun = rgt + [(cx + w * 0.22, base), (rgt[0][0] - (rgt[0][0] - lft[0][0]) * 0.15, top)]
        g.append(f'<polygon points="{P(sun)}" fill="#FFD0A0" opacity="0.22"/>')
        out.append(f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>")
        out.append(f'<polyline points="{P([(lft[0][0] + 2, top)] + rgt[:9])}" fill="none" stroke="{lit}" stroke-width="{1.4 if texture < 1 else 2}" stroke-linejoin="round" opacity="{lit_op}"/>')
    if tint_op:
        out.append(f'<rect x="-10" y="{min(t for _, _, t in temples) - 4}" width="620" height="{base - min(t for _, _, t in temples) + 4}" fill="{tint}" opacity="{tint_op}"/>')
    return "".join(out)


def juniper(x, base, s, seed, lit="#E8C070"):
    """Gnarled Utah juniper clinging to the rim: twisted silver trunk and clumped blue-green foliage."""
    rnd = random.Random(seed)
    out = [f'<g transform="translate({x} {base}) scale({s})">']
    out.append('<path d="M -6 0 C -10 -20 4 -30 -4 -50 C -10 -64 2 -74 10 -84 L 14 -80 C 8 -70 0 -62 4 -50 C 10 -32 2 -20 6 0 Z" fill="#6A5048"/>'
               '<path d="M 0 -42 C 14 -48 22 -56 34 -60 L 35 -56 C 24 -52 16 -44 3 -36 Z" fill="#6A5048"/>'
               '<path d="M -3 -60 C -16 -66 -24 -74 -34 -76 L -34 -72 C -24 -70 -16 -62 -4 -54 Z" fill="#6A5048"/>'
               '<path d="M 4 -50 C 10 -32 2 -20 6 0 L 2 0 C -1 -18 6 -30 1 -46 Z" fill="#C8B4A0" opacity="0.8"/>'
               '<path d="M 10 -84 L 14 -80 C 8 -70 2 -64 4 -54 L 2 -56 C 1 -66 6 -74 10 -84 Z" fill="#D8C4B0" opacity="0.7"/>')
    for cx, cy, r in ((-34, -82, 16), (-20, -96, 18), (8, -100, 20), (30, -88, 16), (38, -66, 13), (-38, -64, 10), (18, -110, 12)):
        for i in range(16):
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.uniform(0, 1) ** 0.6 * r
            px, py = cx + d * math.cos(a), cy + d * math.sin(a) * 0.7
            rr = rnd.uniform(3, 6)
            col = "#3E5048" if py > cy + 2 else ("#7A8A6A" if px > cx + 3 else "#56685A")
            out.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{rr * 1.2:.1f}" ry="{rr:.1f}" fill="{col}"/>')
        out.append(f'<ellipse cx="{cx + r * 0.4:.1f}" cy="{cy - r * 0.3:.1f}" rx="{r * 0.35:.1f}" ry="{r * 0.2:.1f}" fill="{lit}" opacity="0.55"/>')
    out.append(dots(14, seed, (-40, -112, 40, -60), "#8EA8C8", r=(1, 1.8), opacity=(0.6, 0.9)))
    out.append("</g>")
    return "".join(out)


def grand_canyon():
    u = "gcs"
    out = [defs(
        lg(f"{u}-sky", [(0, "#36457E"), (0.3, "#7A6EA6"), (0.6, "#E89A8E"), (0.82, "#FBC488"), (1, "#FFE2AE")], 0, 40, 0, 200, units="userSpaceOnUse"),
        lg(f"{u}-rim", [(0, "#E8D2B8"), (1, "#A88E7C")]),
        lg(f"{u}-river", [(0, "#FFF0C8"), (1, "#F8B878")], 0, 0, 1, 0),
        lg(f"{u}-gorge", [(0, "#6A3E54"), (1, "#3A2440")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(500, 186, 300, "#FFE6B0", f"{u}-sun", 0.95))
    out.append('<circle cx="500" cy="183" r="16" fill="#FFF6DA"/>')
    rnd = random.Random(3)
    out.append('<g fill="#F8C0A0">' + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{rnd.uniform(2.5, 4.5):.1f}" opacity="{rnd.uniform(0.35, 0.65):.2f}"/>' for x, y, w in ((110, 104, 100), (60, 116, 60), (300, 96, 80), (380, 128, 110), (560, 112, 60), (200, 140, 70))) + "</g>")
    out.append('<g fill="#FFE8C8" opacity="0.7">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="1.5"/>' for x, y, w in ((130, 102, 60), (400, 126, 70), (320, 94, 40))) + "</g>")
    # North Rim: long flat forested plateau, palest and bluest
    poly, nr = ridge_poly([(-10, 190), (140, 187), (300, 190), (420, 185), (610, 189)], 2, base=250, amp=2, fill="#B4A2C4")
    out.append(poly)
    fr = rough([(-10, 189), (200, 186), (400, 186), (610, 188)], 5, 2.5, 5)
    out.append(f'<polygon points="{P(fr + [(610, 194), (-10, 194)])}" fill="#9A88B2" opacity="0.8"/>')
    out.append(f'<rect x="-10" y="193" width="620" height="2" fill="#FFE6C0" opacity="0.55"/>')
    out.append(glow(500, 196, 120, "#FFE8C0", f"{u}-sun2", 0.6))
    # far temples (lavender), middle temples (rose), then warmer and sharper toward us
    out.append(canyon_layer(u, 1, [(20, 150, 208), (110, 170, 200), (200, 140, 214), (290, 160, 204), (380, 170, 210), (470, 150, 204), (560, 170, 208)],
                            200, 262, 11, "#C2A6CA", 0.55, body=("#E8B0A0", "#C88078"), shade_op=0.3, lit_op=0.8, texture=0.4))
    out.append(mist(300, 260, 340, 14, "#E8C4CC", f"{u}-h1", 0.45))
    out.append(canyon_layer(u, 2, [(10, 190, 228), (110, 200, 218), (220, 160, 238), (320, 190, 226), (420, 200, 216), (530, 190, 230), (620, 160, 236)],
                            216, 310, 21, "#E4A6AA", 0.26, body=("#EEA486", "#B8645A"), shade_op=0.36, lit_op=0.85, texture=0.7))
    out.append(mist(300, 306, 340, 12, "#ECC0C0", f"{u}-h2", 0.4))
    # the canyon floor in morning shadow, then the inner gorge with the Colorado River catching the sunrise
    out.append(defs(lg(f"{u}-floor", [(0, "#B87A7A"), (0.4, "#8A5466"), (1, "#5A3450")])))
    fl = rough([(-10, 306), (200, 304), (400, 308), (610, 304)], 9, 3, 3)
    out.append(f'<polygon points="{P(fl + [(610, 444), (-10, 444)])}" fill="url(#{u}-floor)"/>')
    out.append(dots(90, 10, (-10, 310, 610, 440), "#4E5A44", r=(0.8, 1.8), opacity=(0.35, 0.7)))
    out.append(streaks(60, 12, (-10, 310, 610, 440), ["#C88A80", "#4A2A44"], w=(1, 2.5), length=(5, 18), opacity=(0.2, 0.45), slant=0.1))
    gt = rough([(130, 336), (220, 328), (300, 332), (380, 334), (470, 328)], 13, 5, 4)
    gb = rough([(470, 350), (380, 356), (300, 354), (220, 352), (130, 352)], 14, 3, 3)
    out.append(f'<polygon points="{P(gt + gb)}" fill="url(#{u}-gorge)"/>')
    out.append(f'<polyline points="{P(gt)}" fill="none" stroke="#E8A890" stroke-width="1.4" opacity="0.6"/>')
    out.append(streaks(24, 15, (130, 334, 470, 350), ["#2A1A30", "#8A5466"], w=(1, 2), length=(4, 10), opacity=(0.3, 0.6), slant=0.1))
    out.append(f'<path d="M 150 348 Q 230 340 300 345 Q 370 350 460 340" fill="none" stroke="url(#{u}-river)" stroke-width="3.6" stroke-linecap="round"/>')
    out.append('<g fill="#FFF6DA">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="1.1"/>' for x, y, w in ((262, 343, 8), (320, 347, 6), (390, 346, 7))) + "</g>")
    out.append(glow(330, 346, 34, "#FFE6B0", f"{u}-rg", 0.3))
    out.append(canyon_layer(u, 3, [(-10, 200, 262), (90, 180, 252), (190, 120, 292), (440, 120, 290), (520, 200, 250), (620, 180, 262)],
                            250, 380, 31, "#F4B090", 0.06, body=("#F4A070", "#B0503E"), shade_op=0.45, lit_op=1.0, texture=1.0, platform=False))
    out.append(mist(330, 378, 200, 12, "#F0C4B8", f"{u}-h3", 0.4))
    # near spur on the right, fully lit, deep violet shadow
    out.append(canyon_layer(u, 4, [(560, 320, 300), (420, 200, 372), (290, 260, 388)], 300, 444, 41, "#000", 0, body=("#F89A64", "#A84838"), shade_op=0.5, lit_op=1.0, texture=1.2, platform=False))
    # South Rim foreground: a pale Kaibab limestone ledge with a juniper and early hikers
    rim = [(-10, 360), (40, 356), (90, 362), (140, 374), (190, 392), (226, 418), (246, 444), (-10, 444)]
    out.append(f'<polygon points="{P(rim)}" fill="url(#{u}-rim)"/>')
    out.append(f'<clipPath id="{u}-rc"><polygon points="{P(rim)}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-rc)">'
               + '<g stroke="#7A6660" stroke-width="1.6" opacity="0.55" fill="none"><path d="M -10 384 Q 60 376 150 386"/><path d="M -10 408 Q 80 398 190 410"/><path d="M -10 430 Q 100 424 220 434"/></g>'
               + streaks(50, 71, (-10, 360, 246, 444), ["#8A7066", "#FFF0DC", "#6A5A5A"], w=(1, 3), length=(4, 14), opacity=(0.3, 0.6), slant=0.5)
               + f'<polygon points="{P([(140, 374), (190, 392), (226, 418), (246, 444), (170, 444), (130, 400)])}" fill="#5A4050" opacity="0.35"/></g>')
    out.append(f'<polyline points="{P(rim[:7])}" fill="none" stroke="#FFF2D8" stroke-width="2.4" stroke-linejoin="round"/>')
    out.append(grass(40, 72, (-10, 362, 170, 400), ["#B8A070", "#8A8058", "#D8C08A"], h=(4, 10)))
    out.append(juniper(58, 362, 1.0, 5))
    out.append(stroll(150, 378, 30, "#3E5A7A", rim="#FFD8A0"))
    out.append(stroll(167, 383, 27, "#B8504A", flip=-1, rim="#FFD8A0"))
    # ravens riding the morning updraft
    out.append('<g fill="#2A2030"><path d="M 330 150 q 8 -7 14 -1 q 6 -6 14 1 q -7 -1 -14 3 q -7 -4 -14 -3 Z"/><path d="M 372 168 q 6 -5 10 -1 q 4 -4 10 1 q -5 -1 -10 2 q -5 -3 -10 -2 Z"/></g>')
    return "\n".join(out)


# ---------------------------------------------------------------- Washington DC (dawn over the Tidal Basin, cherry blossoms)
def branch_tree(x, y, ang, length, width, depth, seed, bark="#3A2630", tips=None, segs=None, droop=0.0):
    """Recursive branching: returns stroke segments and collects tip points for blossom clusters."""
    rnd = random.Random(seed)
    segs = [] if segs is None else segs
    tips = [] if tips is None else tips
    a = math.radians(ang)
    bend = rnd.uniform(-0.35, 0.35)
    x2 = x + length * math.cos(a)
    y2 = y + length * math.sin(a) + droop * length
    mx = x + length * 0.5 * math.cos(a + bend)
    my = y + length * 0.5 * math.sin(a + bend)
    segs.append((x, y, mx, my, x2, y2, width))
    if depth == 0 or width < 1.2:
        tips.append((x2, y2))
        return segs, tips
    n = 2 if rnd.random() < 0.7 else 3
    for i in range(n):
        na = ang + rnd.uniform(-38, 38) + (i - (n - 1) / 2) * 18
        branch_tree(x2, y2, na, length * rnd.uniform(0.62, 0.8), width * rnd.uniform(0.55, 0.72), depth - 1, rnd.random(), bark, tips, segs, droop)
    if depth <= 2:
        tips.append(((x + x2) / 2, (y + y2) / 2))
    return segs, tips


def blossoms(pts, seed, r=14, n=18, cols=("#F6B8CC", "#F9CCDA", "#EE9CB8", "#FFE6EE"), lit="#FFF2F4", shade="#C8709A", light=(1, -0.6)):
    rnd = random.Random(seed)
    sh, bd, li = [], [], []
    for cx, cy in pts:
        rr = r * rnd.uniform(0.7, 1.2)
        for i in range(n):
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.uniform(0, 1) ** 0.7 * rr
            x, y = cx + d * math.cos(a), cy + d * math.sin(a) * 0.8
            pr = rnd.uniform(2.6, 5.0)
            facing = math.cos(a) * light[0] + math.sin(a) * light[1]
            if facing < -0.4:
                sh.append(f'<circle cx="{x:.1f}" cy="{y + 1:.1f}" r="{pr:.1f}"/>')
            else:
                bd.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{pr:.1f}" fill="{rnd.choice(cols)}"/>')
            if facing > 0.5 and rnd.random() < 0.5:
                li.append(f'<circle cx="{x + 0.6:.1f}" cy="{y - 0.6:.1f}" r="{pr * 0.55:.1f}"/>')
    return f'<g fill="{shade}">{"".join(sh)}</g><g>{"".join(bd)}</g><g fill="{lit}" opacity="0.85">{"".join(li)}</g>'


def draw_segs(segs, bark, rim=None):
    out = []
    for x, y, mx, my, x2, y2, w in segs:
        out.append(f'<path d="M {x:.1f} {y:.1f} Q {mx:.1f} {my:.1f} {x2:.1f} {y2:.1f}" stroke="{bark}" stroke-width="{w:.1f}"/>')
    lit = ""
    if rim:
        lit = f'<g fill="none" stroke="{rim}" stroke-linecap="round" opacity="0.6">' + "".join(
            f'<path d="M {x + w * 0.25:.1f} {y - w * 0.25:.1f} Q {mx + w * 0.25:.1f} {my - w * 0.25:.1f} {x2 + w * 0.2:.1f} {y2 - w * 0.2:.1f}" stroke-width="{max(0.8, w * 0.25):.1f}"/>'
            for x, y, mx, my, x2, y2, w in segs if w > 2.5) + "</g>"
    return '<g fill="none" stroke-linecap="round">' + "".join(out) + "</g>" + lit


def washington_dc():
    u = "dcb"
    out = [defs(
        lg(f"{u}-sky", [(0, "#5E6EA8"), (0.3, "#A898C4"), (0.6, "#F0B4BC"), (0.85, "#FFD4B0"), (1, "#FFE8C8")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-water", [(0, "#F8D0C0"), (0.2, "#D8A8C0"), (0.6, "#8A88B8"), (1, "#5A5E98")], 0, 302, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-monL", [(0, "#B8A6C8"), (1, "#9A8AB4")]),
        lg(f"{u}-monR", [(0, "#FFE8D8"), (1, "#F4C8B8")]),
        lg(f"{u}-wall", [(0, "#C8B8C0"), (1, "#8A7A90")]),
        lg(f"{u}-path", [(0, "#B8A4B0"), (1, "#8A7488")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(300, 292, 300, "#FFE6C0", f"{u}-sun", 0.95))
    out.append('<circle cx="300" cy="290" r="18" fill="#FFF6E4"/>')
    rnd = random.Random(3)
    out.append('<g fill="#FBD0C8">' + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{rnd.uniform(2.5, 4):.1f}" opacity="{rnd.uniform(0.4, 0.7):.2f}"/>' for x, y, w in ((140, 150, 90), (90, 162, 50), (420, 136, 110), (480, 150, 60), (330, 200, 70), (520, 220, 50))) + "</g>")
    out.append('<g fill="#FFF0E4" opacity="0.7">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="1.5"/>' for x, y, w in ((150, 148, 50), (430, 134, 70), (340, 198, 40))) + "</g>")
    # far shore: blue-grey trees, then a long band of blossoming cherries
    poly, fl = ridge_poly([(-10, 292), (60, 284), (140, 290), (260, 286), (400, 288), (520, 282), (610, 288)], 5, base=312, amp=5, fill="#8E86A8")
    out.append(poly)
    # the Washington Monument with the ring of flags at its foot
    cx, base, top = 214, 296, 116
    wb, wt = 12.5, 7.8
    out.append(f'<polygon points="{P([(cx - wb, base), (cx - wt, top), (cx, top), (cx, base)])}" fill="url(#{u}-monL)"/>')
    out.append(f'<polygon points="{P([(cx, base), (cx, top), (cx + wt, top), (cx + wb, base)])}" fill="url(#{u}-monR)"/>')
    out.append(f'<polygon points="{P([(cx - wt, top), (cx, 96), (cx, top)])}" fill="#A898BC"/><polygon points="{P([(cx, top), (cx, 96), (cx + wt, top)])}" fill="#FFF0E4"/>')
    ych = base - (base - top) * 0.27
    out.append(f'<polygon points="{P([(cx - wb + 0.9, ych), (cx + wb - 0.9, ych), (cx + wb - 0.8, ych + 1.2), (cx - wb + 0.8, ych + 1.2)])}" fill="#C8A0A8" opacity="0.5"/>')
    out.append(f'<polygon points="{P([(cx - wb + 0.9, ych), (cx + wb - 0.9, ych), (cx + wb, base), (cx - wb, base)])}" fill="#D8A8A0" opacity="0.12"/>')
    for yy in (top + 6, ):
        out.append(f'<rect x="{cx + 2}" y="{yy}" width="2" height="2.6" fill="#E04A4A"/><rect x="{cx - 4}" y="{yy}" width="2" height="2.6" fill="#B03A50"/>')
    out.append(f'<line x1="{cx}" y1="{top}" x2="{cx}" y2="{base}" stroke="#FFFFFF" stroke-width="0.8" opacity="0.5"/>')
    for i in range(-7, 8):
        fx = cx + i * 4.8
        out.append(f'<line x1="{fx:.1f}" y1="{base + 2}" x2="{fx:.1f}" y2="{base - 12}" stroke="#E8E0E8" stroke-width="0.9"/><rect x="{fx:.1f}" y="{base - 12}" width="3.2" height="2.2" fill="{"#C84A5A" if i % 2 else "#4A5A9A"}"/>')
    # Jefferson Memorial: shallow dome on a drum behind an Ionic portico, lit from the right
    jx, jb = 424, 300
    out.append(f'<g transform="translate({jx} {jb}) scale(1.3) translate({-jx} {-jb})">')
    out.append(f'<path d="M {jx - 46} {jb - 30} Q {jx} {jb - 70} {jx + 46} {jb - 30} Z" fill="#E8DCE4"/>')
    out.append(f'<path d="M {jx - 46} {jb - 30} Q {jx - 30} {jb - 60} {jx} {jb - 62} L {jx - 4} {jb - 30} Z" fill="#A89ABC" opacity="0.7"/>')
    out.append(f'<path d="M {jx - 44} {jb - 32} Q {jx} {jb - 68} {jx + 44} {jb - 32}" fill="none" stroke="#FFF6EE" stroke-width="1.4" opacity="0.8"/>')
    out.append(f'<rect x="{jx - 50}" y="{jb - 30}" width="100" height="10" fill="#D8CCD8"/><rect x="{jx - 50}" y="{jb - 30}" width="40" height="10" fill="#A89ABC" opacity="0.6"/>')
    out.append(f'<rect x="{jx - 64}" y="{jb - 20}" width="128" height="20" fill="#E4D8E0"/><rect x="{jx - 64}" y="{jb - 20}" width="50" height="20" fill="#A89ABC" opacity="0.5"/>')
    # portico
    out.append(f'<polygon points="{P([(jx - 24, jb - 34), (jx, jb - 46), (jx + 24, jb - 34)])}" fill="#F4ECEE"/><polygon points="{P([(jx - 24, jb - 34), (jx, jb - 46), (jx, jb - 34)])}" fill="#B8AAC8"/>')
    out.append(f'<rect x="{jx - 25}" y="{jb - 34}" width="50" height="4" fill="#E8DCE4"/>')
    out.append(f'<rect x="{jx - 23}" y="{jb - 30}" width="46" height="26" fill="#6A5A7A"/>')
    for i in range(8):
        px = jx - 22 + i * 6.1
        out.append(f'<rect x="{px:.1f}" y="{jb - 30}" width="3" height="26" fill="{"#FFF4EE" if i > 3 else "#D8CCDA"}"/>')
    out.append(f'<rect x="{jx - 70}" y="{jb - 4}" width="140" height="6" fill="#D0C2D0"/>')
    out.append('</g>')
    # cherry trees ringing the basin
    rnd = random.Random(9)
    far_bl = [(rnd.uniform(-10, 610), rnd.uniform(294, 306)) for _ in range(70)]
    out.append(blossoms(far_bl, 10, r=10, n=9, cols=("#F4C4D4", "#F8D4E0", "#EAB0C8"), lit="#FFF0F2", shade="#B88AAE"))
    out.append(f'<rect x="-10" y="302" width="620" height="8" fill="#8E7A9A" opacity="0.6"/>')
    out.append(mist(300, 296, 140, 16, "#FFE8D4", f"{u}-gl", 0.6))
    # the basin
    out.append(f'<rect x="-10" y="306" width="620" height="138" fill="url(#{u}-water)"/>')
    out.append(f'<rect x="-10" y="306" width="620" height="16" fill="#E8B8C8" opacity="0.4"/>')
    # reflections: monument, memorial, the sun's path, blossoms
    out.append(reflect_streaks(21, [cx - 3, cx + 3], 310, 420, ["#FFE8DC", "#C8B4D0"], w=(5, 9), op=(0.35, 0.75), step=(3.5, 6)))
    out.append(reflect_streaks(22, [jx - 40, jx - 14, jx + 14, jx + 40], 310, 360, ["#F4E4EC"], w=(12, 20), op=(0.3, 0.6), step=(3, 5)))
    out.append(reflect_streaks(23, [294, 300, 306], 308, 420, ["#FFF0D0", "#FFE0A8"], w=(10, 22), op=(0.4, 0.9), step=(3, 5)))
    rnd = random.Random(24)
    out.append("".join(f'<rect x="{rnd.uniform(-10, 600):.1f}" y="{rnd.uniform(312, 330):.1f}" width="{rnd.uniform(6, 20):.1f}" height="1.5" fill="#F8C8D8" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>' for _ in range(40)))
    out.append(dots(90, 25, (-10, 330, 610, 400), "#FFF0F4", r=(0.6, 1.3), opacity=(0.3, 0.7)))
    out.append(mist(160, 314, 180, 10, "#FFF0F0", f"{u}-wm1", 0.5))
    out.append(mist(470, 316, 160, 9, "#FFF0F0", f"{u}-wm2", 0.45))
    # a paddle boat out early, with its little wake
    for bx, by, s, col in ((250, 352, 1.0, "#3E7AB0"), (360, 336, 0.7, "#E8E2D8")):
        out.append(f'<g transform="translate({bx} {by}) scale({s})"><path d="M -22 4 Q 0 8 22 4" fill="none" stroke="#FFF4F4" stroke-width="1.6" opacity="0.6"/>'
                   f'<path d="M -16 -4 L 16 -4 L 13 4 L -13 4 Z" fill="{col}"/><path d="M -10 -4 L -8 -14 L 9 -14 L 11 -4" fill="none" stroke="#F4F0EC" stroke-width="1.6"/>'
                   '<rect x="-9" y="-16" width="19" height="3" rx="1.2" fill="#F4F0EC"/><circle cx="-3" cy="-7" r="2.6" fill="#2A2238"/><circle cx="4" cy="-7" r="2.6" fill="#7A3A48"/></g>')
    # granite seawall and the walk, petals everywhere
    out.append(f'<polygon points="{P([(-10, 398), (610, 392), (610, 404), (-10, 410)])}" fill="url(#{u}-wall)"/>')
    out.append('<g stroke="#6A5A70" stroke-width="1" opacity="0.6">' + "".join(f'<line x1="{x}" y1="{398 - x * 6 / 620 + 0.5:.1f}" x2="{x}" y2="{410 - x * 6 / 620:.1f}"/>' for x in range(10, 610, 34)) + "</g>")
    out.append(f'<polygon points="{P([(-10, 398), (610, 392), (610, 394), (-10, 400)])}" fill="#FFF0E8" opacity="0.7"/>')
    out.append(f'<polygon points="{P([(-10, 410), (610, 404), (610, 444), (-10, 444)])}" fill="url(#{u}-path)"/>')
    out.append(dots(160, 26, (-10, 404, 610, 444), "#F8C8D8", r=(0.8, 1.8), opacity=(0.5, 0.95)))
    # an early walker and a photographer on the walk
    out.append(stroll(120, 404, 36, "#3E4A7A", rim="#FFD8B8"))
    out.append(stroll(380, 401, 34, "#A84A5A", flip=-1, rim="#FFD8B8"))
    out.append('<g stroke="#2A2238" stroke-width="1.4"><line x1="390" y1="401" x2="396" y2="381"/><line x1="402" y1="401" x2="396" y2="381"/><line x1="396" y1="401" x2="396" y2="381"/></g><rect x="392" y="375" width="9" height="6" rx="1" fill="#2A2238"/>')
    # cherry trees framing the view: a gnarled trunk on the right, branches arching over from both corners
    segs, tips = branch_tree(596, 470, -98, 104, 24, 5, 31, droop=0.02)
    segs2, tips2 = branch_tree(-24, 50, 24, 74, 16, 4, 37, droop=0.16)
    segs2 = [sg for sg in segs2 if max(sg[0], sg[4]) < 196]
    tips2 = [(sg[4], sg[5]) for sg in segs2 if sg[6] < 8]
    segs3, tips3 = branch_tree(624, 40, 168, 70, 14, 3, 33, droop=0.16)
    keep = lambda pts: [(x, y) for x, y in pts if not (150 < x < 400 and y > 80)]
    along = [((x + x2) / 2, (y + y2) / 2) for x, y, mx, my, x2, y2, w in segs + segs2 + segs3 if w < 7]
    out.append(draw_segs(segs, "#3A2632", rim="#F4B8A8"))
    out.append(draw_segs(segs2 + segs3, "#3A2632", rim="#F4B8A8"))
    out.append(blossoms(keep(tips + tips2 + tips3 + along), 34, r=17, n=13))
    # a low limb dipping toward the water, heavy with bloom
    segs4, tips4 = branch_tree(604, 336, 194, 62, 10, 3, 39, droop=0.22)
    out.append(draw_segs(segs4, "#3A2632", rim="#F4B8A8"))
    out.append(blossoms(tips4 + [((a + c) / 2, (b + d) / 2) for a, b, _, _, c, d, w in segs4 if w < 7], 38, r=15, n=12))
    # blossom reflections near the shore
    rnd = random.Random(36)
    out.append("".join(f'<rect x="{rnd.uniform(470, 600):.1f}" y="{rnd.uniform(340, 392):.1f}" width="{rnd.uniform(6, 18):.1f}" height="1.6" fill="#F8C0D4" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>' for _ in range(24)))
    # petals drifting down
    rnd = random.Random(35)
    out.append("".join(f'<ellipse cx="{rnd.uniform(40, 560):.1f}" cy="{rnd.uniform(140, 390):.1f}" rx="2.4" ry="1.4" transform="rotate({rnd.uniform(0, 180):.0f})" fill="#FBD4E0" opacity="0.9"/>'[:0] +
                       f'<ellipse cx="{(px := rnd.uniform(40, 560)):.1f}" cy="{(py := rnd.uniform(140, 390)):.1f}" rx="2.6" ry="1.5" transform="rotate({rnd.uniform(0, 180):.0f} {px:.1f} {py:.1f})" fill="#FBD4E0" opacity="0.9"/>' for _ in range(14)))
    return "\n".join(out)

# ---------------------------------------------------------------- Miami Beach (Ocean Drive at dusk)
def neon_line(pts, col, w=1.6, glow_w=6, op=0.35):
    return (f'<polyline points="{P(pts)}" fill="none" stroke="{col}" stroke-width="{glow_w:.1f}" stroke-linejoin="round" stroke-linecap="round" opacity="{op}"/>'
            f'<polyline points="{P(pts)}" fill="none" stroke="#FFF6FA" stroke-width="{w * 0.5:.1f}" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<polyline points="{P(pts)}" fill="none" stroke="{col}" stroke-width="{w:.1f}" stroke-linejoin="round" stroke-linecap="round" opacity="0.85"/>')


class YawCam(Cam):
    """Pinhole camera at (camX, eye) turned `yaw` degrees to the right of +Z."""
    def __init__(self, f=300, cx=300, vpy=290, eye=1.6, camX=0.0, yaw=0.0):
        super().__init__(f, cx, vpy, eye)
        self.camX, self.c, self.s = camX, math.cos(math.radians(yaw)), math.sin(math.radians(yaw))

    def depth(self, X, Z):
        return (X - self.camX) * self.s + Z * self.c

    def __call__(self, X, Y, Z):
        dx = X - self.camX
        Xr = dx * self.c - Z * self.s
        Zr = max(0.05, dx * self.s + Z * self.c)
        return (self.cx + self.f * Xr / Zr, self.vpy + self.f * (self.eye - Y) / Zr)


def deco_car(x, base, k, body="#F4A0B8", trim="#FFF4F0", flip=1):
    """1950s convertible in profile, tail fins and chrome; (x, base) = middle of the wheels' ground line."""
    return (f'<g transform="translate({x:.1f} {base:.1f}) scale({k * flip:.3f} {k:.3f})">'
            '<ellipse cx="0" cy="1" rx="62" ry="5" fill="#140C20" opacity="0.55"/>'
            f'<path d="M -60 -10 L -62 -22 Q -60 -30 -48 -31 L -24 -33 L -14 -42 L 6 -42 L 4 -34 L 44 -34 L 58 -44 L 60 -34 Q 64 -28 62 -10 Z" fill="{body}"/>'
            f'<path d="M -62 -20 L 62 -20 L 62 -14 L -62 -14 Z" fill="{trim}"/>'
            '<path d="M -60 -26 Q 0 -30 58 -28" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity="0.8"/>'
            '<path d="M -14 -42 L -18 -34 L 2 -34 L 4 -40 Z" fill="#B8E8F0" opacity="0.7"/>'
            '<path d="M 10 -34 Q 22 -40 34 -34 Z" fill="#7A3A4A"/><circle cx="18" cy="-42" r="4.2" fill="#2A1A2A"/><circle cx="30" cy="-41" r="4" fill="#5A2A3A"/>'
            '<rect x="60" y="-30" width="4" height="7" rx="1" fill="#FF3A4A"/>'
            '<circle cx="-62" cy="-24" r="3" fill="#FFF6D8"/>'
            '<circle cx="-38" cy="-8" r="10" fill="#140C18"/><circle cx="-38" cy="-8" r="5" fill="#E8E8F0"/>'
            '<circle cx="38" cy="-8" r="10" fill="#140C18"/><circle cx="38" cy="-8" r="5" fill="#E8E8F0"/>'
            f'<path d="M -50 -10 Q -38 -24 -26 -10 M 26 -10 Q 38 -24 50 -10" fill="{body}" stroke="#2A1A2A" stroke-width="1.4"/>'
            '</g>')


def umbrella(x, base, h, col, stripe="#FFFFFF"):
    w = h * 0.7
    return (f'<line x1="{x:.1f}" y1="{base:.1f}" x2="{x:.1f}" y2="{base - h:.1f}" stroke="#2A2030" stroke-width="{max(0.8, h * 0.04):.1f}"/>'
            f'<path d="M {x - w:.1f} {base - h * 0.78:.1f} Q {x:.1f} {base - h * 1.12:.1f} {x + w:.1f} {base - h * 0.78:.1f} Z" fill="{col}"/>'
            f'<path d="M {x - w * 0.33:.1f} {base - h * 0.8:.1f} Q {x:.1f} {base - h * 1.1:.1f} {x + w * 0.33:.1f} {base - h * 0.8:.1f} Z" fill="{stripe}" opacity="0.8"/>'
            f'<rect x="{x - w * 0.5:.1f}" y="{base - h * 0.36:.1f}" width="{w:.1f}" height="{max(1, h * 0.05):.1f}" fill="#2A2030"/>')


def miami_beach():
    u = "mbd"
    C = YawCam(f=330, cx=300, vpy=318, eye=1.7, camX=-7, yaw=36)
    out = [defs(
        lg(f"{u}-sky", [(0, "#22225C"), (0.3, "#4A3A88"), (0.55, "#A85AA0"), (0.78, "#F28098"), (1, "#FFB884")], 0, 40, 0, 318, units="userSpaceOnUse"),
        lg(f"{u}-road", [(0, "#6A4A72"), (1, "#2A1E3A")], 0, 318, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-walk", [(0, "#A07898"), (1, "#5A4068")], 0, 318, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-lawn", [(0, "#3A4A5A"), (1, "#1A2230")], 0, 318, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-cafe", [(0, "#FFE4A8"), (1, "#F8A060")]),
        lg(f"{u}-far", [(0, "#8A5A9A"), (1, "#C8789A")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(40, 2, (0, 40, 600, 130), "#F6EDE0", r=(0.6, 1.3), opacity=(0.3, 0.9)))
    out.append(glow(150, 318, 280, "#FFC890", f"{u}-dusk", 0.7))
    rnd = random.Random(3)
    out.append('<g fill="#F8A0B0">' + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{rnd.uniform(2.5, 4.5):.1f}" opacity="{rnd.uniform(0.35, 0.65):.2f}"/>' for x, y, w in ((130, 150, 110), (60, 162, 60), (280, 124, 70), (220, 196, 80), (420, 104, 60))) + "</g>")
    out.append('<g fill="#FFD8B0" opacity="0.7">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="1.6"/>' for x, y, w in ((140, 152, 60), (230, 198, 40))) + "</g>")
    # taller hotels further inland, hazy against the afterglow
    for x, w, h in ((40, 20, 60), (62, 14, 40), (96, 22, 82), (120, 16, 50), (150, 26, 70), (190, 18, 46)):
        out.append(f'<rect x="{x}" y="{318 - h}" width="{w}" height="{h}" fill="url(#{u}-far)" opacity="0.8"/>')
        out.append(dots(int(h / 5), x, (x + 2, 322 - h, x + w - 2, 314), "#FFE0B0", r=(0.7, 1.1), opacity=(0.5, 1)))
    # ground: lawn on the park side, Ocean Drive, the hotel sidewalk
    out.append(f'<rect x="-10" y="316" width="620" height="130" fill="url(#{u}-lawn)"/>')
    road = [C(-1, 0, 3000), C(13.5, 0, 3000), C(13.5, 0, -4), C(-1, 0, -4)]
    out.append(f'<polygon points="{P(road)}" fill="url(#{u}-road)"/>')
    out.append(f'<polygon points="{P([C(13.5, 0, 3000), C(17.5, 0, 3000), C(17.5, 0, -10), C(13.5, 0, -10)])}" fill="url(#{u}-walk)"/>')
    out.append(f'<polygon points="{P([C(13.5, 0.15, 3000), C(13.5, 0.15, -10), C(13.5, 0, -10), C(13.5, 0, 3000)])}" fill="#E8C8D8"/>')
    out.append(f'<polygon points="{P([C(-1, 0.15, 3000), C(-1, 0.15, -4), C(-1, 0, -4), C(-1, 0, 3000)])}" fill="#C8B0C8"/>')
    for z in (-2, 3, 8, 14, 21, 30, 42, 58, 80, 110, 150, 210):
        out.append(f'<polygon points="{P([C(6.1, 0, z), C(6.35, 0, z), C(6.35, 0, z + 2.6 + z * 0.05), C(6.1, 0, z + 2.6 + z * 0.05)])}" fill="#F8D870" opacity="0.8"/>')
    # ---- Art Deco hotel row (far to near): z0, z1, height, wall, trim, neon, sign word
    FAC = 17.5
    hotels = [(250, 600, 12, "#C8A8D8", "#F4E8F4", "#7AF0F0", None), (170, 250, 13, "#F4C0C8", "#FFF2F4", "#FF6FB0", None),
              (118, 170, 11, "#B8E4D8", "#FFF6F0", "#7AF0F0", None), (80, 118, 14, "#F8E0A0", "#FFFFFF", "#FF5FA0", "HOTEL"),
              (52, 80, 12, "#A8D8F0", "#FFFFFF", "#FF8FD0", "CAFE"), (28, 52, 15, "#F6B0C0", "#FFFFFF", "#6AF4F4", "HOTEL"),
              (6, 28, 13, "#C8E8C8", "#FFFFFF", "#FF6FB0", "OCEAN")]
    for k, (z0, z1, h, wall, trim, neon, word) in enumerate(hotels):
        X = FAC
        dz = z1 - z0
        out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, 0, h))}" fill="{wall}"/>')
        # rounded corner tower at the near end with its own neon edge
        out.append(f'<polygon points="{P(C.quad_x(X, z0, z0 + dz * 0.1, 0, h + 1.4))}" fill="{trim}"/>')
        out.append(f'<polygon points="{P(C.quad_x(X, z0 + dz * 0.07, z0 + dz * 0.1, 0, h + 1.4))}" fill="#3A2A6A" opacity="0.22"/>')
        floors = int((h - 4) / 3.2)
        rr = random.Random(k * 7)
        bays = max(3, int(dz / 4.0))
        for f_ in range(floors):
            y0 = 4 + f_ * 3.2
            for i in range(bays):
                za = z0 + dz * (0.14 + 0.82 * (i + 0.15) / bays)
                zb = z0 + dz * (0.14 + 0.82 * (i + 0.85) / bays)
                on = rr.random() < 0.55
                out.append(f'<polygon points="{P(C.quad_x(X, za, zb, y0 + 0.5, y0 + 2.1))}" fill="{rr.choice(["#FFD98E", "#FFE8B0", "#F8B870"]) if on else "#46508A"}"/>')
            out.append(f'<polygon points="{P(C.quad_x(X, z0 + dz * 0.1, z1, y0 + 1.9, y0 + 2.35))}" fill="#2A1A4A" opacity="0.3"/>')
            out.append(f'<polygon points="{P(C.quad_x(X, z0 + dz * 0.1, z1, y0 + 2.35, y0 + 2.65))}" fill="{trim}"/>')
        # stepped ziggurat parapet
        for j, (a, b, hh) in enumerate(((0.3, 0.7, 1.2), (0.38, 0.62, 2.4), (0.45, 0.55, 3.6))):
            out.append(f'<polygon points="{P(C.quad_x(X, z0 + dz * a, z0 + dz * b, h - 0.2, h + hh))}" fill="{trim if j % 2 == 0 else wall}"/>')
        out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, h - 0.6, h))}" fill="{trim}"/>')
        # dusk: walls cool down toward the top
        out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, h * 0.45, h + 3.6))}" fill="#2A2A6A" opacity="0.18"/>')
        zn = max(z0, 6)
        sw = 330 / C.depth(X, zn)
        out.append(neon_line([C(X - 0.05, h + 0.05, z0 + dz * 0.1), C(X - 0.05, h + 0.05, z1)], neon, w=max(1.0, sw * 0.12), glow_w=max(3, sw * 0.5)))
        out.append(neon_line([C(X - 0.05, 0.3, z0 + dz * 0.1), C(X - 0.05, h + 1.4, z0 + dz * 0.1)], neon, w=max(1.0, sw * 0.12), glow_w=max(3, sw * 0.5)))
        # glowing ground-floor cafe with a coloured awning
        out.append(f'<polygon points="{P(C.quad_x(X, z0 + dz * 0.12, z1 - dz * 0.03, 0.2, 3.0))}" fill="url(#{u}-cafe)"/>')
        out.append(f'<polygon points="{P([C(X, 3.3, z0 + dz * 0.12), C(X, 3.3, z1 - dz * 0.03), C(X - 1.6, 2.8, z1 - dz * 0.03), C(X - 1.6, 2.8, z0 + dz * 0.12)])}" fill="{neon}" opacity="0.75"/>')
        out.append(f'<polygon points="{P([C(X, 0, z0 + dz * 0.12), C(X, 0, z1), C(X - 4, 0, z1), C(X - 4, 0, z0 + dz * 0.12)])}" fill="#FFC880" opacity="0.2"/>')
        # vertical fin with a neon blade sign
        if word:
            zf = z0 + dz * 0.5
            fq = [C(X - 1.8, h * 0.35, zf), C(X - 1.8, h + 4.5, zf), C(X, h + 4.5, zf), C(X, h * 0.35, zf)]
            xs = [p[0] for p in fq]
            cx_ = sum(xs) / 4
            y0, y1 = (fq[1][1] + fq[2][1]) / 2, (fq[0][1] + fq[3][1]) / 2
            wd = max(xs) - min(xs)
            out.append(glow(cx_, (y0 + y1) / 2, (y1 - y0) * 0.7, neon, f"{u}-fg{k}", 0.35))
            out.append(f'<polygon points="{P(fq)}" fill="{trim}" stroke="{neon}" stroke-width="{max(1, wd * 0.08):.1f}" stroke-linejoin="round"/>')
            step = (y1 - y0) * 0.86 / len(word)
            fs = min(step * 1.02, wd * 0.75)
            for i, c in enumerate(word):
                yy = y0 + (y1 - y0) * 0.07 + step * (i + 0.5) + fs * 0.36
                out.append(f'<text x="{cx_:.1f}" y="{yy:.1f}" text-anchor="middle" {ANTON} font-size="{fs:.1f}" fill="none" stroke="{neon}" stroke-width="{fs * 0.24:.1f}" opacity="0.4">{c}</text>'
                           f'<text x="{cx_:.1f}" y="{yy:.1f}" text-anchor="middle" {ANTON} font-size="{fs:.1f}" fill="#FFF6FA" stroke="{neon}" stroke-width="{fs * 0.06:.1f}">{c}</text>')
    # porthole windows on the nearest corner tower
    for yy in (6.2, 9.4):
        cx_, cy_ = C(FAC - 0.02, yy, 7.4)
        r_ = 330 * 0.5 / C.depth(FAC, 7.4)
        out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{r_:.1f}" fill="#FFE0A0" stroke="#FFFFFF" stroke-width="{r_ * 0.3:.1f}"/>')
    # cafe umbrellas and diners on the sidewalk
    for Z, col in ((12, "#FF6FB0"), (18, "#7AD8D0"), (34, "#F8C060"), (42, "#FF8FA8"), (60, "#7AD8D0"), (90, "#FF6FB0")):
        x, b = C(15.6, 0, Z)
        hh = 330 * 2.6 / C.depth(15.6, Z)
        out.append(umbrella(x, b, hh, col))
    for X, Z, h, col, rim in ((14.6, 24, 1.7, "#3A3A6A", "#7AF0F0"), (15.0, 50, 1.65, "#A84A7A", "#FF8FD0"), (14.4, 15, 1.75, "#F0E8F0", "#FF8FD0"), (14.9, 72, 1.7, "#2A4A5A", "#7AF0F0")):
        x, b = C(X, 0, Z)
        out.append(stroll(x, b, 330 * h / C.depth(X, Z), col, rim=rim))
    # a pink-and-white convertible parked at the curb
    x, b = C(11.6, 0, 9)
    out.append(deco_car(x, b, 330 / C.depth(11.6, 9) / 22, flip=1))
    # street lamps along the park side
    for Z in (6, 14, 24, 38, 58, 90):
        x0, y0 = C(-0.6, 0, Z)
        x1, y1 = C(-0.6, 5.2, Z)
        d = C.depth(-0.6, Z)
        out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#1E1830" stroke-width="{max(0.8, 330 * 0.13 / d):.1f}"/>')
        out.append(glow(x1, y1, 330 * 1.4 / d, "#FFE8B0", f"{u}-lp{Z}", 0.85))
        out.append(f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="{max(1, 330 * 0.22 / d):.1f}" fill="#FFF6E0"/>')
    # coconut palms in the park, rim-lit by the afterglow (foreground ones framing the view)
    # park walk along the street
    out.append(f'<polygon points="{P([C(-4.5, 0, 3000), C(-1, 0, 3000), C(-1, 0, -1), C(-4.5, 0, -1)])}" fill="#6A5878"/>')
    out.append(grass(120, 5, (-10, 330, 260, 444), ["#3E5A68", "#2A3A48", "#5A7A80"], h=(4, 12)))
    for X, Z, sd, hh in ((-4, 120, 8, 12), (-3, 70, 7, 12), (-6, 44, 6, 11), (-3, 28, 5, 10), (-7, 18, 4, 8), (-6, 8, 3, 6.2)):
        x, b = C(X, 0, Z)
        out.append(palm_tree(x, b, 330 * hh / C.depth(X, Z), trunk="#2E2240", frond="#1C2434", rim="#FF9AB8", seed=sd, lean=0.1 if sd % 2 else -0.08))
    # a couple on a park bench under the palms
    x, b = C(-3.2, 0, 12)
    k = 330 / C.depth(-3.2, 12) / 60
    out.append(f'<g transform="translate({x:.1f} {b:.1f}) scale({k:.3f})"><rect x="-40" y="-26" width="80" height="6" fill="#4A3A5A"/><rect x="-40" y="-44" width="80" height="5" fill="#4A3A5A"/>'
               '<rect x="-36" y="-26" width="4" height="26" fill="#2A2038"/><rect x="32" y="-26" width="4" height="26" fill="#2A2038"/>'
               '<path d="M -22 -26 L -22 -60 Q -14 -68 -6 -60 L -6 -26 Z" fill="#E86A8A"/><circle cx="-14" cy="-72" r="8" fill="#2A1A2A"/><path d="M -22 -26 L -26 0 M -8 -26 L -12 0" stroke="#2A2038" stroke-width="6"/>'
               '<path d="M 4 -26 L 4 -62 Q 12 -70 20 -62 L 20 -26 Z" fill="#3A6A9A"/><circle cx="12" cy="-74" r="8" fill="#3A2A2A"/><path d="M 6 -26 L 2 0 M 18 -26 L 14 0" stroke="#2A2038" stroke-width="6"/>'
               '<path d="M -6 -60 L -6 -26" stroke="#FF9AB8" stroke-width="2"/></g>')
    # sea grape shrubs in the corner, catching pink light
    rnd = random.Random(61)
    for cx, cy, r in ((20, 420, 40), (80, 436, 34), (-4, 380, 30), (150, 444, 30)):
        for i in range(40):
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.uniform(0, 1) ** 0.6 * r
            px, py = cx + d * math.cos(a), cy + d * math.sin(a) * 0.6
            rr = rnd.uniform(4, 8)
            col = "#142028" if py > cy else ("#3A4A58" if px > cx else "#22303C")
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rr:.1f}" fill="{col}"/>')
        for i in range(8):
            out.append(f'<circle cx="{cx + rnd.uniform(0, r * 0.8):.1f}" cy="{cy - rnd.uniform(r * 0.2, r * 0.55):.1f}" r="2.6" fill="#E88AA8" opacity="0.7"/>')
    # pelicans gliding home
    out.append('<g fill="none" stroke="#2A2050" stroke-width="2" stroke-linecap="round"><path d="M 230 118 q 8 -6 16 0 q 8 -6 16 0"/><path d="M 266 132 q 6 -5 11 0 q 6 -5 11 0"/></g>')
    return "\n".join(out)

# ---------------------------------------------------------------- Honolulu (Waikiki toward Diamond Head, late golden light)
def outrigger(x, y, s, hull="#C8402E", seed=1):
    """Six-seat outrigger canoe seen side-on with its float (ama) and paddlers mid-stroke."""
    rnd = random.Random(seed)
    out = [f'<g transform="translate({x} {y}) scale({s})">',
           '<path d="M -40 -4 Q -42 -14 -36 -18 M 30 -6 Q 28 -16 34 -20" fill="none" stroke="#5A3A28" stroke-width="2.4"/>',
           '<path d="M -50 -18 Q -6 -22 46 -22" fill="none" stroke="#5A3A28" stroke-width="2"/>',
           '<path d="M -56 -20 Q -6 -26 52 -24 L 50 -20 Q -6 -22 -54 -17 Z" fill="#E8D8B8"/>']
    for i in range(6):
        px = -56 + i * 22
        col = rnd.choice(["#2A2A3A", "#3A2A2A", "#E8504A", "#F0C040", "#2A6A8A"])
        out.append(f'<line x1="{px + 6}" y1="-24" x2="{px - 12}" y2="2" stroke="#7A5638" stroke-width="2.2"/><path d="M {px - 13} -2 L {px - 9} 0 L {px - 13} 8 L {px - 17} 6 Z" fill="#7A5638"/>'
                   f'<path d="M {px - 19} 4 q 4 -4 10 0" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity="0.8"/>'
                   f'<path d="M {px - 5} -8 L {px - 6} -22 Q {px} -27 {px + 6} -22 L {px + 5} -8 Z" fill="{col}"/>'
                   f'<path d="M {px + 2} -22 L {px + 7} -24" stroke="{col}" stroke-width="3" stroke-linecap="round"/>'
                   f'<circle cx="{px}" cy="-30" r="4.2" fill="#3A2420"/><path d="M {px + 3} -33 Q {px + 5} -30 {px + 3} -27" stroke="#FFD08A" stroke-width="1.4" fill="none"/>'
                   f'<path d="M {px + 5} -21 L {px + 5} -9" stroke="#FFD08A" stroke-width="1.6" opacity="0.8"/>')
    out.append(f'<path d="M -78 -10 Q 0 -6 78 -12 L 72 0 Q 0 4 -72 0 Z" fill="{hull}"/>'
               '<path d="M -76 -9 Q 0 -5 76 -11" fill="none" stroke="#FFE8C0" stroke-width="1.6" opacity="0.8"/>'
               '<path d="M -72 -2 Q 0 2 72 -2" fill="none" stroke="#5A1A18" stroke-width="2" opacity="0.5"/>')
    out.append('<path d="M -60 4 Q 0 10 80 4" fill="none" stroke="#FFFFFF" stroke-width="2.2" opacity="0.7"/></g>')
    return "".join(out)


def surfer(x, y, s, board="#F4E8D0", suit="#2A2A3A", flip=1):
    return (f'<g transform="translate({x} {y}) scale({s * flip} {s})">'
            f'<path d="M -26 0 Q 0 -6 28 -2 Q 0 4 -26 0 Z" fill="{board}"/><path d="M -24 0 Q 0 -4 26 -2" stroke="#E8504A" stroke-width="1.4" fill="none"/>'
            f'<path d="M -8 -2 L -2 -16 L 6 -2" fill="none" stroke="{suit}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M -2 -16 L 2 -30" stroke="{suit}" stroke-width="6" stroke-linecap="round"/>'
            f'<path d="M 0 -26 L -12 -24 M 2 -27 L 14 -31" stroke="{suit}" stroke-width="3" stroke-linecap="round"/>'
            '<circle cx="3" cy="-36" r="4.4" fill="#3A2420"/></g>')


def honolulu():
    u = "hnw"
    out = [defs(
        lg(f"{u}-sky", [(0, "#3A6AB0"), (0.4, "#7EA8D6"), (0.72, "#E8CCC4"), (1, "#FCD6A6")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#2E6A9E"), (0.35, "#2A8AAE"), (0.7, "#3EB8BC"), (1, "#7AD8C8")], 0, 300, 0, 390, units="userSpaceOnUse"),
        lg(f"{u}-dh", [(0, "#C8A060"), (0.5, "#9A8A50"), (1, "#5E6A40")]),
        lg(f"{u}-sand", [(0, "#F0D2A0"), (1, "#E2B880")]),
        lg(f"{u}-wet", [(0, "#C8B8A8"), (1, "#D8C4A8")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    # trade-wind cumulus, lit warm from the west (right)
    out.append(cumulus(u, 170, 168, 190, 62, 11, lit="#FFE6C4", body="#F6DCD4", shade="#A8A8C8", n=22, light_dx=0.4))
    out.append(cumulus(u, 360, 130, 130, 44, 12, lit="#FFE6C4", body="#F6DCD4", shade="#A8A8C8", n=16, light_dx=0.4))
    out.append(cumulus(u, 530, 160, 110, 34, 13, lit="#FFE6C4", body="#F6DCD4", shade="#A8A8C8", n=14, light_dx=0.4))
    out.append(cumulus(u, 60, 250, 130, 26, 14, lit="#FFE4C4", body="#F2D2CC", shade="#B8B0CC", n=14, light_dx=0.4, op=0.85))
    out.append(cumulus(u, 270, 262, 100, 20, 15, lit="#FFE4C4", body="#F2D2CC", shade="#B8B0CC", n=12, light_dx=0.4, op=0.8))
    out.append(mist(300, 296, 340, 30, "#FFE8CC", f"{u}-hz", 0.6))
    out.append(glow(640, 230, 330, "#FFD49A", f"{u}-warm", 0.45))
    # Diamond Head: long slope from Waikiki up to Leahi summit, steep seaward drop, eroded ribs
    prof = rough([(220, 304), (290, 292), (350, 274), (410, 252), (460, 232), (500, 216), (536, 204), (552, 206), (574, 226), (596, 262), (614, 296)], 4, 5, 4)
    poly = prof + [(614, 310), (220, 310)]
    out.append(f'<clipPath id="{u}-dc"><polygon points="{P(poly)}"/></clipPath>')
    out.append(f'<polygon points="{P(poly)}" fill="url(#{u}-dh)"/>')
    g = []
    rnd = random.Random(7)
    x = 232
    while x < 600:
        ytop = y_on(prof, x) or 300
        L = (312 - ytop) * rnd.uniform(0.75, 1.0)
        w = rnd.uniform(4, 11)
        lean = (x - 545) * 0.12 + rnd.uniform(-4, 4)
        g.append(f'<path d="M {x:.1f} {ytop + 1:.1f} q {lean * 0.4 - w * 0.5:.1f} {L * 0.5:.1f} {lean - w * 0.2:.1f} {L:.1f} l {w * 1.4:.1f} 0 q {-lean * 0.5:.1f} {-L * 0.5:.1f} {-lean + w * 0.2:.1f} {-L:.1f} Z" fill="#4A4C34" opacity="{rnd.uniform(0.28, 0.5):.2f}"/>')
        g.append(f'<path d="M {x + w * 1.2:.1f} {ytop + 2:.1f} q {lean * 0.4:.1f} {L * 0.5:.1f} {lean + w * 0.5:.1f} {L * 0.92:.1f}" fill="none" stroke="#F8D894" stroke-width="{rnd.uniform(1.4, 2.6):.1f}" opacity="{rnd.uniform(0.45, 0.8):.2f}"/>')
        x += w * 1.4 + rnd.uniform(5, 14)
    g.append(streaks(70, 77, (240, 210, 610, 300), ["#6A6A40", "#E8C880"], w=(0.8, 2), length=(4, 12), opacity=(0.2, 0.45), slant=0.2))
    g.append(f'<polygon points="{P([(552, 206), (574, 226), (596, 262), (614, 296), (614, 310), (560, 310)])}" fill="#3E4A3A" opacity="0.45"/>')
    g.append(f'<rect x="200" y="286" width="420" height="30" fill="#4A6A40" opacity="0.6"/>')
    out.append(f'<g clip-path="url(#{u}-dc)">' + "".join(g) + "</g>")
    out.append(f'<polyline points="{P(prof[:-12])}" fill="none" stroke="#FFE2A0" stroke-width="2" opacity="0.8"/>')
    out.append(f'<rect x="547" y="203" width="6" height="3" fill="#E8E0D0"/>')
    # Kapiolani shoreline: trees and low buildings at its foot, the whole left bay curving away
    rnd = random.Random(8)
    trees = []
    for i in range(70):
        x = rnd.uniform(-10, 610)
        y = rnd.uniform(298, 306)
        r = rnd.uniform(4, 9)
        trees.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 1.3:.1f}" ry="{r:.1f}" fill="{rnd.choice(["#3E6A48", "#4A7A50", "#2E5A40"])}"/>')
        trees.append(f'<ellipse cx="{x + r * 0.4:.1f}" cy="{y - r * 0.4:.1f}" rx="{r * 0.6:.1f}" ry="{r * 0.4:.1f}" fill="#A8C070" opacity="0.6"/>')
    for x, w, h in ((40, 16, 26), (58, 12, 18), (130, 18, 22), (190, 14, 16), (330, 12, 10)):
        out.append(f'<rect x="{x}" y="{300 - h}" width="{w}" height="{h}" fill="#E8E0DA"/><rect x="{x + w * 0.6:.1f}" y="{300 - h}" width="{w * 0.4:.1f}" height="{h}" fill="#F8F0E0"/>'
                   + "".join(f'<rect x="{x + 1}" y="{yy}" width="{w - 2}" height="1.2" fill="#9AA8B8"/>' for yy in range(302 - h, 298, 4)))
    out.append("".join(trees))
    for x in (90, 150, 230, 280, 360, 420):
        out.append(palm_tree(x, 304, 30, trunk="#4A4030", frond="#3A5A40", seed=x, lean=0.1))
    # the sea: reef shallows, swell lines, breaking surf
    out.append(f'<rect x="-10" y="304" width="620" height="90" fill="url(#{u}-sea)"/>')
    rnd = random.Random(9)
    out.append('<g fill="#BFF0F0">' + "".join(f'<rect x="{rnd.uniform(-10, 600):.1f}" y="{(yy := rnd.uniform(308, 386)):.1f}" width="{rnd.uniform(6, 26) * (yy - 290) / 40:.1f}" height="1.4" rx="0.7" opacity="{rnd.uniform(0.25, 0.6):.2f}"/>' for _ in range(110)) + "</g>")
    out.append(blobs(18, 10, (0, 340, 600, 380), ["#2E8A8A", "#3E7A70"], r=(14, 34), opacity=(0.25, 0.4), squash=0.2))
    # a breaking wave with two surfers riding it
    for y0, x0, x1, sd in ((326, 150, 330, 1), (346, -10, 200, 2), (338, 380, 560, 3)):
        out.append(f'<path d="M {x0} {y0 + 4} Q {(x0 + x1) / 2} {y0 - 8} {x1} {y0 + 2} L {x1} {y0 + 6} Q {(x0 + x1) / 2} {y0 - 2} {x0} {y0 + 8} Z" fill="#1E6A8A" opacity="0.6"/>')
        out.append(f'<path d="M {x0} {y0 + 6} Q {(x0 + x1) / 2} {y0 - 2} {x1} {y0 + 4}" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.9"/>')
        out.append(dots(26, sd, (x0, y0 - 6, x1, y0 + 6), "#FFFFFF", r=(0.8, 2), opacity=(0.5, 1)))
    out.append(surfer(250, 328, 0.62, board="#F8E8C8", suit="#2A2A3A"))
    out.append(surfer(300, 324, 0.5, board="#F0B040", suit="#3A2A2A", flip=-1))
    out.append('<g transform="translate(470 352)"><path d="M -14 0 Q 0 -3 14 -1 Q 0 2 -14 0 Z" fill="#7AD0E0"/><circle cx="0" cy="-5" r="3.2" fill="#3A2420"/><path d="M -3 -2 Q 0 -4 4 -2" stroke="#3A2A2A" stroke-width="3"/></g>')
    # outrigger canoe surfing in, its float and booms catching the light
    out.append('<path d="M 300 380 Q 400 386 520 378" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.5"/>')
    out.append('<path d="M 330 368 Q 410 366 490 362 L 488 365 Q 410 370 332 371 Z" fill="#E8D8B8"/>')
    out.append(outrigger(420, 376, 0.9))
    out.append(glow(620, 360, 220, "#FFE0A8", f"{u}-sheen", 0.35))
    # beach: wet sand reflections, foam lace, dry sand
    out.append(f'<path d="M -10 392 Q 200 384 400 390 Q 520 394 610 388 L 610 444 L -10 444 Z" fill="url(#{u}-wet)"/>')
    out.append(f'<path d="M -10 404 Q 200 396 400 404 Q 520 408 610 400 L 610 444 L -10 444 Z" fill="url(#{u}-sand)"/>')
    out.append('<path d="M -10 392 Q 60 396 120 390 Q 200 386 260 392 Q 330 398 400 390 Q 480 384 540 392 Q 580 396 610 388" fill="none" stroke="#FFFFFF" stroke-width="2.6" opacity="0.9"/>')
    out.append('<path d="M -10 396 Q 80 400 160 394 M 300 398 Q 400 400 470 394" fill="none" stroke="#FFFFFF" stroke-width="1.4" opacity="0.6"/>')
    out.append(reflect_streaks(11, [440, 450], 394, 404, ["#E84A3A"], w=(6, 10), op=(0.2, 0.4), step=(2, 3)))
    out.append(dots(160, 12, (-10, 406, 610, 444), "#C89A68", r=(0.6, 1.4), opacity=(0.4, 0.8)))
    # surfboards planted in the sand, a leaning palm framing the left
    for x, col, st in ((540, "#F27A5A", "#FFF4E0"), (560, "#5AB8D8", "#FFF4E0"), (578, "#F8D070", "#E8504A")):
        out.append(f'<g transform="rotate({(x - 560) * 0.3:.1f} {x} 430)"><path d="M {x - 7} 430 Q {x - 8} 380 {x} 362 Q {x + 8} 380 {x + 7} 430 Z" fill="{col}"/>'
                   f'<path d="M {x} 364 L {x} 430" stroke="{st}" stroke-width="2"/><path d="M {x + 3} 368 Q {x + 6} 390 {x + 6} 428" fill="none" stroke="#FFFFFF" stroke-width="1.4" opacity="0.6"/></g>')
    out.append('<ellipse cx="540" cy="434" rx="50" ry="5" fill="#B88A58" opacity="0.5"/>')
    out.append(palm_tree(30, 460, 300, trunk="#5A4434", frond="#244A30", rim="#FFD890", seed=24, lean=0.462))
    out.append(palm_tree(30, 460, 330, trunk="#5A4434", frond="#2E5A3A", rim="#FFD890", seed=21, lean=0.42))
    tx, ty = 30 + 0.42 * 330, 130
    out.append("".join(f'<circle cx="{tx + dx}" cy="{ty + dy}" r="5" fill="#6A5A2A"/><circle cx="{tx + dx + 1.5}" cy="{ty + dy - 1.5}" r="2" fill="#C8B060" opacity="0.7"/>' for dx, dy in ((-4, 8), (4, 9), (0, 14), (-8, 13))))
    for i in range(1, 26):
        t = i / 26
        bx = 30 + (0.42 * 330 * 0.2) * 2 * t * (1 - t) + 0.42 * 330 * t * t
        by = 460 - 330 * t
        out.append(f'<path d="M {bx - 5 + 2 * t:.1f} {by:.1f} q 5 2 {10 - 4 * t:.1f} 0" fill="none" stroke="#3A2A20" stroke-width="1.4" opacity="0.6"/>')
    out.append('<path d="M 30 460 L -120 452" stroke="#A88058" stroke-width="18" opacity="0.25"/>')
    # frigatebirds
    out.append('<g fill="none" stroke="#2A2A3A" stroke-width="2" stroke-linecap="round"><path d="M 400 190 q 8 -6 15 0 q 7 -6 15 0"/><path d="M 432 206 q 5 -4 9 0 q 5 -4 9 0"/></g>')
    return "\n".join(out)

# ---------------------------------------------------------------- Savannah (a moss-hung square on a spring morning)
def moss(x, y, L, seed, cols=("#A8B094", "#C8CCB0", "#8A947A", "#B8BCA0"), sw=(1.4, 2.6)):
    """A drape of Spanish moss: several wavy strands of varying length hanging from (x, y)."""
    rnd = random.Random(seed)
    out = []
    for i in range(rnd.randint(5, 9)):
        x0 = x + rnd.uniform(-6, 6)
        l = L * rnd.uniform(0.45, 1.0)
        d = f"M {x0:.1f} {y:.1f}"
        yy = y
        xx = x0
        while yy < y + l:
            step = rnd.uniform(5, 9)
            d += f" q {rnd.uniform(-4, 4):.1f} {step / 2:.1f} {rnd.uniform(-2, 2):.1f} {step:.1f}"
            yy += step
        out.append(f'<path d="{d}" stroke="{rnd.choice(cols)}" stroke-width="{rnd.uniform(*sw):.1f}" opacity="{rnd.uniform(0.7, 0.95):.2f}"/>')
    return '<g fill="none" stroke-linecap="round">' + "".join(out) + "</g>"


def leaf_mass(cx, cy, rx, ry, seed, n=60, cols=("#2E4A30", "#3A5634", "#26402A"), lit="#8A9A58", light=(-1, -0.7)):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.uniform(0, 1) ** 0.6
        x, y = cx + rx * d * math.cos(a), cy + ry * d * math.sin(a)
        r = rnd.uniform(5, 11)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 1.3:.1f}" ry="{r:.1f}" fill="{rnd.choice(cols)}"/>')
        if math.cos(a) * light[0] + math.sin(a) * light[1] > 0.4 and d > 0.5:
            out.append(f'<ellipse cx="{x - 1.5:.1f}" cy="{y - 2:.1f}" rx="{r * 0.6:.1f}" ry="{r * 0.4:.1f}" fill="{lit}" opacity="0.7"/>')
    return "".join(out)


def rowhouse(x, w, top, base, wall, trim, shutter, seed, floors=3, stoop=True, balcony=False):
    rnd = random.Random(seed)
    out = [f'<rect x="{x}" y="{top}" width="{w}" height="{base - top}" fill="{wall}"/>',
           f'<rect x="{x}" y="{top}" width="{w * 0.14:.1f}" height="{base - top}" fill="#FFFFFF" opacity="0.12"/>',
           f'<rect x="{x - 2}" y="{top - 5}" width="{w + 4}" height="6" fill="{trim}"/><rect x="{x - 2}" y="{top + 1}" width="{w + 4}" height="2" fill="#000" opacity="0.15"/>']
    if wall in ("#A8503E", "#9A4A3A", "#B8604A"):
        out.append('<g stroke="#6A2A22" stroke-width="0.8" opacity="0.35">' + "".join(f'<line x1="{x}" y1="{yy}" x2="{x + w}" y2="{yy}"/>' for yy in range(int(top) + 4, int(base), 4)) + "</g>")
    fh = (base - top - 16) / floors
    bays = max(2, int(w / 22))
    for f_ in range(floors):
        y0 = top + 8 + f_ * fh
        for i in range(bays):
            wx = x + w * (i + 0.5) / bays
            ww, wh = min(9, w / bays * 0.42), fh * 0.62
            if f_ == floors - 1 and i == 0 and stoop:
                continue
            out.append(f'<rect x="{wx - ww / 2 - 4.5:.1f}" y="{y0:.1f}" width="4" height="{wh:.1f}" fill="{shutter}"/><rect x="{wx + ww / 2 + 0.5:.1f}" y="{y0:.1f}" width="4" height="{wh:.1f}" fill="{shutter}"/>')
            on = rnd.random() < 0.3
            out.append(f'<rect x="{wx - ww / 2:.1f}" y="{y0:.1f}" width="{ww:.1f}" height="{wh:.1f}" fill="{"#F8E0A8" if on else "#3A4A50"}"/>')
            out.append(f'<line x1="{wx:.1f}" y1="{y0:.1f}" x2="{wx:.1f}" y2="{y0 + wh:.1f}" stroke="{trim}" stroke-width="1"/><line x1="{wx - ww / 2:.1f}" y1="{y0 + wh / 2:.1f}" x2="{wx + ww / 2:.1f}" y2="{y0 + wh / 2:.1f}" stroke="{trim}" stroke-width="1"/>')
            out.append(f'<rect x="{wx - ww / 2 - 1:.1f}" y="{y0 - 2.5:.1f}" width="{ww + 2:.1f}" height="2.5" fill="{trim}"/>')
        if balcony and f_ == 1:
            out.append(f'<rect x="{x + 3}" y="{y0 + fh * 0.62:.1f}" width="{w - 6}" height="2" fill="#1E2420"/>'
                       + "".join(f'<line x1="{bx}" y1="{y0 + fh * 0.62 - 7:.1f}" x2="{bx}" y2="{y0 + fh * 0.62:.1f}" stroke="#1E2420" stroke-width="1"/>' for bx in range(int(x) + 4, int(x + w) - 3, 3))
                       + f'<rect x="{x + 3}" y="{y0 + fh * 0.62 - 8:.1f}" width="{w - 6}" height="1.6" fill="#1E2420"/>')
    if stoop:
        dx = x + w * 0.5 / bays
        out.append(f'<rect x="{dx - 6:.1f}" y="{base - fh * 0.8:.1f}" width="12" height="{fh * 0.8 - 8:.1f}" fill="#3A2A26"/>'
                   f'<path d="M {dx - 7:.1f} {base - fh * 0.8:.1f} a 7 6 0 0 1 14 0 Z" fill="{trim}"/>'
                   f'<polygon points="{P([(dx - 8, base - 8), (dx + 8, base - 8), (dx + 16, base), (dx - 16, base)])}" fill="#C8B8A0"/>'
                   + "".join(f'<line x1="{dx - 8 - k * 2:.1f}" y1="{base - 8 + k * 2:.1f}" x2="{dx + 8 + k * 2:.1f}" y2="{base - 8 + k * 2:.1f}" stroke="#8A7A6A" stroke-width="0.8"/>' for k in range(1, 4))
                   + f'<path d="M {dx - 9:.1f} {base - 14:.1f} L {dx - 17:.1f} {base - 4:.1f} M {dx + 9:.1f} {base - 14:.1f} L {dx + 17:.1f} {base - 4:.1f}" stroke="#1E2420" stroke-width="1.4"/>')
    return "".join(out)


def savannah():
    u = "svm"
    out = [defs(
        lg(f"{u}-sky", [(0, "#A8C8D8"), (0.6, "#E4E4D4"), (1, "#F8ECCC")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-lawn", [(0, "#7A9A50"), (1, "#3E5A32")], 0, 330, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-path", [(0, "#E8D4B0"), (1, "#C8A880")], 0, 330, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-iron", [(0, "#FFFFFF"), (0.55, "#E4E0D8"), (1, "#9A9A9A")], 0, 0, 1, 0),
        lg(f"{u}-pool", [(0, "#A8C8C8"), (1, "#5A8088")]),
        lg(f"{u}-ray", [(0, "#FFF4D0", 0.5), (1, "#FFF4D0", 0)]),
        lg(f"{u}-spire", [(0, "#F4EEE4"), (0.6, "#D8D0C8"), (1, "#A8A0A8")], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(120, 150, 260, "#FFF2D0", f"{u}-sun", 0.8))
    # the cathedral's twin Gothic spires rising behind the houses
    for sx in (372, 432):
        out.append(f'<rect x="{sx - 13}" y="176" width="26" height="130" fill="url(#{u}-spire)"/>')
        out.append(f'<polygon points="{P([(sx - 12, 178), (sx, 104), (sx + 12, 178)])}" fill="url(#{u}-spire)"/>')
        out.append(f'<polygon points="{P([(sx, 104), (sx + 12, 178), (sx + 2, 178)])}" fill="#8A8494" opacity="0.4"/>')
        out.append('<g stroke="#A8A0A8" stroke-width="1" opacity="0.7">' + "".join(f'<line x1="{sx - 12 + (178 - yy) * 12 / 74:.1f}" y1="{yy}" x2="{sx + 12 - (178 - yy) * 12 / 74:.1f}" y2="{yy}"/>' for yy in range(124, 178, 12)) + "</g>")
        for px in (sx - 13, sx + 13):
            out.append(f'<polygon points="{P([(px - 3, 180), (px, 162), (px + 3, 180)])}" fill="#E8E2DA"/>')
        out.append(f'<rect x="{sx - 15}" y="176" width="30" height="5" fill="#C8C0C0"/>')
        out.append(f'<path d="M {sx - 5} 214 L {sx - 5} 198 Q {sx} 188 {sx + 5} 198 L {sx + 5} 214 Z" fill="#5A5A6A"/>')
        out.append(f'<circle cx="{sx}" cy="232" r="6" fill="#5A5A6A"/><circle cx="{sx}" cy="232" r="4" fill="#E8E2D8"/>')
        out.append(f'<line x1="{sx}" y1="104" x2="{sx}" y2="92" stroke="#8A8494" stroke-width="1.6"/><line x1="{sx - 4}" y1="97" x2="{sx + 4}" y2="97" stroke="#8A8494" stroke-width="1.6"/>')
    # far oaks of the next square, hazy
    out.append('<g opacity="0.75">' + leaf_mass(100, 240, 120, 34, 3, n=90, cols=("#9AAE98", "#A8BAA4", "#8EA48E"), lit="#D4DCC0")
               + leaf_mass(520, 236, 110, 34, 4, n=90, cols=("#9AAE98", "#A8BAA4", "#8EA48E"), lit="#D4DCC0") + "</g>")
    # historic houses across the square: brick, stucco, a balcony, stoops
    houses = [(40, 62, 222, "#A8503E", "#F2E8D8", "#2E4A3A", True, False), (102, 58, 232, "#E8C8A0", "#FFF6E8", "#3A5A4A", True, True),
              (160, 64, 214, "#C8D4C8", "#FFFFFF", "#2E4A3A", True, False), (224, 58, 228, "#9A4A3A", "#F2E8D8", "#1E3A2E", True, True),
              (282, 64, 220, "#F0DCC0", "#FFFFFF", "#2E4A3A", False, False), (466, 64, 224, "#B8604A", "#F2E8D8", "#2E4A3A", True, True),
              (530, 62, 234, "#E8D0D8", "#FFFFFF", "#3A5A4A", True, False), (346, 120, 262, "#D8CCB8", "#F4ECE0", "#2E4A3A", False, False)]
    for x, w, top, wall, trim, sh, st, bal in houses:
        out.append(rowhouse(x, w, top, 330, wall, trim, sh, x, floors=3 if top < 250 else 2, stoop=st, balcony=bal))
    out.append(f'<rect x="-10" y="300" width="620" height="30" fill="#E8E0C8" opacity="0.25"/>')
    # the street and a carriage tour clip-clopping past
    out.append(f'<rect x="-10" y="328" width="620" height="14" fill="#B8A88E"/><rect x="-10" y="328" width="620" height="2" fill="#8A7A66"/>')
    cx_, cy_ = 150, 338
    out.append(f'<g transform="translate({cx_} {cy_})">'
               '<path d="M 36 -18 Q 44 -26 52 -24 L 56 -30 L 58 -22 Q 62 -18 60 -14 L 54 -14 L 50 -8 L 50 0 L 46 0 L 46 -6 L 30 -6 L 28 0 L 24 0 L 24 -10 Q 22 -18 30 -20 Z" fill="#6A4430"/>'
               '<path d="M 50 -8 L 48 0 M 28 -6 L 26 0" stroke="#4A2E20" stroke-width="2"/>'
               '<path d="M 54 -28 Q 50 -20 46 -18" stroke="#3A2418" stroke-width="2" fill="none"/>'
               '<rect x="-30" y="-24" width="50" height="16" rx="3" fill="#1E2A26"/><rect x="-26" y="-36" width="40" height="3" fill="#7A2A2A"/>'
               '<line x1="-26" y1="-33" x2="-26" y2="-24" stroke="#1E2A26" stroke-width="1.6"/><line x1="14" y1="-33" x2="14" y2="-24" stroke="#1E2A26" stroke-width="1.6"/>'
               '<circle cx="-22" cy="-2" r="8" fill="none" stroke="#2A1E18" stroke-width="2"/><circle cx="10" cy="-4" r="6" fill="none" stroke="#2A1E18" stroke-width="2"/>'
               '<path d="M 20 -16 L 30 -16" stroke="#2A1E18" stroke-width="1.6"/>'
               '<circle cx="-14" cy="-30" r="3.4" fill="#3A2A22"/><rect x="-17" y="-28" width="6" height="6" fill="#E8C060"/><circle cx="-2" cy="-30" r="3.4" fill="#5A3A2A"/><rect x="-5" y="-28" width="6" height="6" fill="#4A7AA8"/>'
               '<circle cx="12" cy="-32" r="3.4" fill="#2A1E1A"/><rect x="9" y="-30" width="6" height="7" fill="#2A2A2A"/><path d="M 8 -35 L 16 -35 L 14 -38 L 10 -38 Z" fill="#2A2A2A"/></g>')
    # the square: lawn, azaleas in bloom, sand-and-brick paths radiating to the fountain
    out.append(f'<rect x="-10" y="342" width="620" height="102" fill="url(#{u}-lawn)"/>')
    out.append(f'<path d="M 230 342 L 370 342 L 520 444 L 80 444 Z" fill="url(#{u}-path)"/>')
    out.append(f'<path d="M -10 380 Q 120 360 220 372 L 220 382 Q 120 372 -10 394 Z" fill="url(#{u}-path)"/>')
    out.append(f'<path d="M 610 382 Q 480 360 380 372 L 380 382 Q 480 372 610 396 Z" fill="url(#{u}-path)"/>')
    rnd = random.Random(12)
    for cx, cy, r in ((40, 352, 30), (110, 348, 26), (190, 350, 22), (420, 350, 22), (500, 348, 28), (570, 352, 30)):
        for i in range(34):
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.uniform(0, 1) ** 0.6 * r
            x, y = cx + d * math.cos(a), cy + d * math.sin(a) * 0.45
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(2.5, 4.5):.1f}" fill="{"#3A5A30" if y > cy + 2 else rnd.choice(["#E8509A", "#F07AB0", "#D8407A", "#F8A8C8"])}"/>')
    out.append(grass(160, 13, (-10, 360, 610, 444), ["#5A7A3E", "#8AA858", "#3E5A30"], h=(4, 10)))
    # the tiered cast-iron fountain
    fx = 300
    out.append(f'<ellipse cx="{fx}" cy="384" rx="118" ry="18" fill="#B8B0A0"/>')
    out.append(f'<ellipse cx="{fx}" cy="380" rx="112" ry="15" fill="url(#{u}-pool)"/>')
    out.append(reflect_streaks(14, [fx - 60, fx - 20, fx + 20, fx + 60], 372, 392, ["#FFFFFF"], w=(8, 16), op=(0.3, 0.6), step=(2.5, 4)))
    out.append(f'<path d="M {fx - 118} 384 Q {fx} 408 {fx + 118} 384 L {fx + 118} 390 Q {fx} 414 {fx - 118} 390 Z" fill="#E8E0D0"/>')
    out.append(f'<path d="M {fx + 40} 401 Q {fx + 90} 396 {fx + 118} 388 L {fx + 118} 390 Q {fx + 90} 400 {fx + 40} 406 Z" fill="#8A8478" opacity="0.5"/>')
    # pedestal, lower bowl, column, upper bowl, crowning figure
    out.append(f'<path d="M {fx - 16} 380 L {fx - 10} 330 L {fx + 10} 330 L {fx + 16} 380 Z" fill="url(#{u}-iron)"/>')
    out.append(f'<path d="M {fx - 62} 318 Q {fx} 352 {fx + 62} 318 Z" fill="url(#{u}-iron)"/><ellipse cx="{fx}" cy="318" rx="62" ry="6" fill="#F4F2EC"/>')
    out.append(f'<path d="M {fx - 6} 318 L {fx - 5} 278 L {fx + 5} 278 L {fx + 6} 318 Z" fill="url(#{u}-iron)"/>')
    out.append(f'<path d="M {fx - 30} 276 Q {fx} 296 {fx + 30} 276 Z" fill="url(#{u}-iron)"/><ellipse cx="{fx}" cy="276" rx="30" ry="4" fill="#F4F2EC"/>')
    out.append(f'<path d="M {fx - 4} 276 L {fx - 3} 256 L {fx + 3} 256 L {fx + 4} 276 Z" fill="url(#{u}-iron)"/>')
    out.append(f'<path d="M {fx - 5} 256 Q {fx - 7} 244 {fx - 2} 236 L {fx - 1} 226 Q {fx + 2} 222 {fx + 3} 228 L {fx + 3} 238 Q {fx + 8} 244 {fx + 6} 256 Z" fill="url(#{u}-iron)"/>')
    out.append(f'<path d="M {fx + 3} 236 L {fx + 10} 228" stroke="#E8E4DC" stroke-width="2.4" stroke-linecap="round"/>')
    # water: arcs from the top jet, curtains falling off both bowls, splashes
    out.append('<g fill="none" stroke="#FFFFFF" stroke-linecap="round">'
               + "".join(f'<path d="M {fx + 9} 228 Q {fx + 9 + dx * 0.5} {218 - dx * 0.1} {fx + 9 + dx} {262 + dx * 0.05}" stroke-width="1.6" opacity="0.8"/>' for dx in (6, 12, 18))
               + "".join(f'<path d="M {fx + s * 28} 278 Q {fx + s * 34} 284 {fx + s * (40 + k * 4)} 316" stroke-width="{2.2 - k * 0.4:.1f}" opacity="{0.85 - k * 0.15:.2f}"/>' for s in (-1, 1) for k in range(3))
               + "".join(f'<path d="M {fx + s * 60} 320 Q {fx + s * 70} 330 {fx + s * (78 + k * 6)} 376" stroke-width="{2.4 - k * 0.4:.1f}" opacity="{0.85 - k * 0.15:.2f}"/>' for s in (-1, 1) for k in range(3))
               + "</g>")
    out.append(dots(50, 15, (fx - 100, 360, fx + 100, 384), "#FFFFFF", r=(0.8, 2), opacity=(0.5, 1)))
    out.append(dots(20, 16, (fx - 50, 300, fx + 50, 318), "#FFFFFF", r=(0.8, 1.6), opacity=(0.5, 1)))
    out.append(f'<path d="M {fx - 5} 330 L {fx - 5} 378" stroke="#FFFFFF" stroke-width="1.6" opacity="0.6"/>')
    # gas lamps on the paths
    for lx, base, h in ((196, 392, 62), (410, 396, 64)):
        out.append(f'<rect x="{lx - 1.8}" y="{base - h}" width="3.6" height="{h}" fill="#1E2420"/><rect x="{lx - 4}" y="{base - 6}" width="8" height="6" fill="#1E2420"/>')
        out.append(glow(lx, base - h - 6, 16, "#FFE8B0", f"{u}-gl{lx}", 0.7))
        out.append(f'<path d="M {lx - 6} {base - h - 1} L {lx - 4} {base - h - 13} L {lx + 4} {base - h - 13} L {lx + 6} {base - h - 1} Z" fill="#FFF0C8" stroke="#1E2420" stroke-width="1.6"/>'
                   f'<path d="M {lx - 6} {base - h - 13} L {lx} {base - h - 19} L {lx + 6} {base - h - 13} Z" fill="#1E2420"/>')
    # a woman walking her dog along the path, a reader on a bench
    out.append(stroll(470, 424, 50, "#E8A0B0", rim="#FFF0C8"))
    out.append('<g transform="translate(500 424)"><path d="M -12 -4 Q -10 -12 0 -12 L 8 -12 L 10 -18 L 14 -16 L 13 -10 Q 14 -6 10 -4 L 10 0 L 7 0 L 7 -4 L -6 -4 L -8 0 L -11 0 Z" fill="#8A5A3A"/><path d="M -12 -8 L -18 -14" stroke="#8A5A3A" stroke-width="2.4" stroke-linecap="round"/></g>')
    out.append('<path d="M 476 400 Q 488 410 504 410" fill="none" stroke="#2A2A2A" stroke-width="1"/>')
    out.append('<g transform="translate(110 414)"><rect x="-30" y="-14" width="60" height="4" fill="#2A3A2E"/><rect x="-30" y="-30" width="60" height="3" fill="#2A3A2E"/><rect x="-30" y="-24" width="60" height="3" fill="#2A3A2E"/>'
               '<rect x="-26" y="-14" width="3" height="14" fill="#1E2420"/><rect x="23" y="-14" width="3" height="14" fill="#1E2420"/>'
               '<path d="M -6 -14 L -6 -40 Q 2 -46 10 -40 L 10 -14 Z" fill="#4A6A8A"/><circle cx="2" cy="-50" r="6.4" fill="#3A2A22"/><rect x="4" y="-36" width="10" height="7" fill="#F4ECDC"/>'
               '<path d="M -4 -14 L 14 -12 L 14 0 M 8 -14 L 20 -12 L 20 0" stroke="#2A2A3A" stroke-width="4" fill="none"/></g>')
    # dappled morning light on the ground
    rnd = random.Random(17)
    out.append("".join(f'<ellipse cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(350, 440):.1f}" rx="{rnd.uniform(8, 26):.1f}" ry="{rnd.uniform(2, 5):.1f}" fill="#FFF4C8" opacity="{rnd.uniform(0.15, 0.35):.2f}"/>' for _ in range(30)))
    # sunbeams slanting through the canopy from the upper left
    for x0, w in ((60, 40), (140, 26), (210, 50), (300, 22)):
        out.append(f'<polygon points="{P([(x0, 40), (x0 + w, 40), (x0 + w + 200, 420), (x0 + 200, 420)])}" fill="url(#{u}-ray)" opacity="0.5"/>')
    # the live oaks: massive trunks, long arching limbs, dark canopy, Spanish moss everywhere
    out.append('<g fill="none" stroke-linecap="round">'
               '<path d="M -20 444 Q 10 300 30 220 Q 40 170 20 110" stroke="#3A3028" stroke-width="46"/>'
               '<path d="M 26 230 Q 120 170 230 150 Q 300 140 340 110" stroke="#3A3028" stroke-width="20"/>'
               '<path d="M 30 170 Q 70 100 160 70 Q 220 50 280 52" stroke="#3A3028" stroke-width="16"/>'
               '<path d="M 620 444 Q 590 300 580 230 Q 572 160 600 100" stroke="#3A3028" stroke-width="44"/>'
               '<path d="M 584 240 Q 500 180 400 160 Q 340 150 300 120" stroke="#3A3028" stroke-width="18"/>'
               '<path d="M 580 170 Q 540 100 440 70 Q 380 54 320 60" stroke="#3A3028" stroke-width="14"/>'
               '</g>')
    out.append('<g fill="none" stroke-linecap="round" stroke="#8A7A60" opacity="0.6">'
               '<path d="M -4 440 Q 24 300 44 220 Q 52 170 36 120" stroke-width="5"/><path d="M 40 222 Q 120 166 230 146" stroke-width="3"/>'
               '<path d="M 600 440 Q 574 300 566 230" stroke-width="3"/><path d="M 570 232 Q 500 176 400 156" stroke-width="2.6"/></g>')
    out.append(streaks(40, 18, (-20, 220, 60, 444), ["#5A4A3A", "#2A2018"], w=(1.5, 3), length=(10, 30), opacity=(0.4, 0.7), slant=0.05))
    out.append(streaks(40, 19, (560, 220, 620, 444), ["#5A4A3A", "#2A2018"], w=(1.5, 3), length=(10, 30), opacity=(0.4, 0.7), slant=0.05))
    # resurrection fern on the limbs
    out.append(dots(60, 20, (40, 140, 300, 170), "#6A8A40", r=(1, 2.2), opacity=(0.6, 1)))
    out.append(leaf_mass(80, 70, 160, 60, 21, n=150))
    out.append(leaf_mass(520, 70, 160, 60, 22, n=150))
    out.append(leaf_mass(300, 26, 220, 36, 23, n=110))
    out.append(leaf_mass(240, 120, 70, 24, 24, n=40))
    out.append(leaf_mass(470, 116, 60, 22, 25, n=36))
    for i, (x, y, L) in enumerate(((70, 120, 70), (120, 160, 90), (160, 110, 60), (210, 150, 80), (250, 140, 54), (300, 112, 46), (340, 124, 50), (476, 150, 70),
                                   (450, 120, 66), (500, 168, 90), (540, 130, 64), (30, 210, 80), (580, 220, 70), (190, 74, 50), (470, 80, 50), (260, 60, 40))):
        out.append(moss(x, y, L, 40 + i))
    return "\n".join(out)


BUILD = {
    "san-francisco": (san_francisco, "SAN FRANCISCO", "CALIFORNIA · USA", "#24304A", "#E2532F", "#FBEBD4", "#F8C890"),
    "grand-canyon": (grand_canyon, "GRAND CANYON", "ARIZONA · USA", "#2E2240", "#F8A070", "#FBEBD4", "#FBC488"),
    "washington-dc": (washington_dc, "WASHINGTON, DC", "DISTRICT OF COLUMBIA", "#2E2C54", "#F4A8C0", "#FBEBD4", "#F8C4D4"),
    "miami-beach": (miami_beach, "MIAMI BEACH", "FLORIDA · USA", "#1E1A48", "#FF6FB0", "#FFF2F6", "#7AF0F0"),
    "honolulu": (honolulu, "HONOLULU", "HAWAII · USA", "#173A54", "#F8C060", "#FFF4E2", "#7AD8C8"),
    "savannah": (savannah, "SAVANNAH", "GEORGIA · EST. 1733", "#22382A", "#E8A0B0", "#FAF2E4", "#F2C890"),
    "new-york": (new_york, "NEW YORK", "NEW YORK · USA", "#141A38", "#F6A66E", "#FBEBD4", "#F6B480"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("places", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
