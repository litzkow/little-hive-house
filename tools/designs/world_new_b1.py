"""World Places, painted edition — batch B1: Edinburgh, Dublin, Swiss Alps, Iceland, Norway, Cinque Terre, Provence.
Same travel-poster idiom as world_painted.py: a real viewpoint, a time of day and light direction, graded skies,
atmospheric depth and small storytelling details. Run this file to regenerate all seven posters."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from world_painted import (defs, Q, mix, lerp, cumulus, streak_cloud, gulls, figure, leaf_canopy, water_lines)
from places_painted import Cam
from poster import poster


def win_grid(x0, y0, w, h, cols, rows, seed, lit_p=0.55, lit=("#FFD98E", "#F7C06A", "#FFE6A8"), dark="#2A2340",
             ww=0.42, wh=0.5, sill=None):
    """A grid of windows inside the rectangle (x0, y0, w, h)."""
    rnd = random.Random(seed)
    out = []
    cw, rh = w / cols, h / rows
    for r in range(rows):
        for c in range(cols):
            on = rnd.random() < lit_p
            x = x0 + c * cw + cw * (1 - ww) / 2
            y = y0 + r * rh + rh * (1 - wh) / 2
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cw * ww:.1f}" height="{rh * wh:.1f}" fill="{rnd.choice(lit) if on else dark}"/>')
            if sill:
                out.append(f'<rect x="{x - 0.6:.1f}" y="{y + rh * wh:.1f}" width="{cw * ww + 1.2:.1f}" height="1.2" fill="{sill}"/>')
    return "".join(out)


def chimneys(x0, x1, y, seed, col, pots="#5A4048", h=(7, 12), every=(14, 26), rim=None):
    """Chimney stacks with rows of pots along a roof line (very Edinburgh)."""
    rnd = random.Random(seed)
    out = []
    x = x0 + rnd.uniform(2, 8)
    while x < x1 - 6:
        w = rnd.uniform(7, 13)
        hh = rnd.uniform(*h)
        out.append(f'<rect x="{x:.1f}" y="{y - hh:.1f}" width="{w:.1f}" height="{hh + 1:.1f}" fill="{col}"/>')
        out.append(f'<rect x="{x - 0.8:.1f}" y="{y - hh:.1f}" width="{w + 1.6:.1f}" height="1.6" fill="{col}"/>')
        n = max(1, int(w / 3.2))
        for i in range(n):
            px = x + (i + 0.5) * w / n
            out.append(f'<rect x="{px - 0.9:.1f}" y="{y - hh - rnd.uniform(2, 4):.1f}" width="1.8" height="4" fill="{pots}"/>')
        if rim:
            out.append(f'<rect x="{x + w - 1.4:.1f}" y="{y - hh:.1f}" width="1.4" height="{hh:.1f}" fill="{rim}" opacity="0.6"/>')
        x += w + rnd.uniform(*every)
    return "".join(out)


def lamp_post(x, base, h, u, k, glow_col="#FFD58A", post="#1E1A26", strength=0.85, r=40, s=1.0):
    """Victorian cast-iron lamp standard with a lantern and its pool of light (s scales the lantern)."""
    top = base - h
    a, b, c, d = 4.2 * s, 3.2 * s, 9 * s, 4.6 * s
    return (glow(x, top + c / 2, r, glow_col, f"{u}-lp{k}", strength)
            + f'<path d="M {x - 3 * s:.1f} {base:.1f} L {x - 1.4 * s:.1f} {base - h * 0.15:.1f} L {x - 1.1 * s:.1f} {top + c:.1f} L {x + 1.1 * s:.1f} {top + c:.1f} L {x + 1.4 * s:.1f} {base - h * 0.15:.1f} L {x + 3 * s:.1f} {base:.1f} Z" fill="{post}"/>'
            + f'<rect x="{x - 2.6 * s:.1f}" y="{base - h * 0.16:.1f}" width="{5.2 * s:.1f}" height="{2 * s:.1f}" fill="{post}"/>'
            + f'<path d="M {x - a:.1f} {top + c:.1f} L {x - b:.1f} {top + s:.1f} L {x + b:.1f} {top + s:.1f} L {x + a:.1f} {top + c:.1f} Z" fill="#FFF0C4"/>'
            + f'<path d="M {x - d:.1f} {top + 1.5 * s:.1f} L {x:.1f} {top - 3 * s:.1f} L {x + d:.1f} {top + 1.5 * s:.1f} Z" fill="{post}"/>'
            + f'<rect x="{x - d:.1f}" y="{top + c - 0.5 * s:.1f}" width="{2 * d:.1f}" height="{1.8 * s:.1f}" fill="{post}"/>'
            + f'<line x1="{x:.1f}" y1="{top - 3 * s:.1f}" x2="{x:.1f}" y2="{top - 6 * s:.1f}" stroke="{post}" stroke-width="{1.4 * s:.1f}"/>')


def stepped_gable(x, w, top, h, fill, steps=4):
    """Crow-stepped gable end wall: a triangle whose sloping edges climb in little stone steps."""
    pts = [(x, top)]
    for i in range(steps):
        y0 = top - h * i / steps
        y1 = top - h * (i + 1) / steps
        xx = x + (w / 2) * (i + 0.5) / (steps + 0.5)
        pts += [(xx, y0), (xx, y1)]
    pts += [(x + w / 2 - w * 0.06, top - h), (x + w / 2 + w * 0.06, top - h)]
    right = [(2 * x + w - px, py) for px, py in pts[::-1]]
    return Q(pts + right[1:], fill)


# ================================================================ EDINBURGH — the floodlit castle on its rock, blue hour
def gothic_spire(cx, base, top, w, u, wall, roof, lit, rim):
    """The Hub (Tolbooth Kirk): square tower, crocketed pinnacles, tall octagonal spire."""
    sb = base - (base - top) * 0.42
    out = [f'<rect x="{cx - w / 2:.1f}" y="{sb:.1f}" width="{w:.1f}" height="{base - sb:.1f}" fill="{wall}"/>',
           f'<rect x="{cx + w * 0.12:.1f}" y="{sb:.1f}" width="{w * 0.38:.1f}" height="{base - sb:.1f}" fill="{lit}" opacity="0.55"/>']
    # tall lancet belfry openings
    for d in (-0.22, 0.22):
        x = cx + d * w
        out.append(f'<path d="M {x - 2.2:.1f} {sb + 34:.1f} L {x - 2.2:.1f} {sb + 12:.1f} Q {x:.1f} {sb + 6:.1f} {x + 2.2:.1f} {sb + 12:.1f} L {x + 2.2:.1f} {sb + 34:.1f} Z" fill="#2A2238"/>')
    out.append(f'<rect x="{cx - w / 2 - 1:.1f}" y="{sb - 2:.1f}" width="{w + 2:.1f}" height="3" fill="{rim}" opacity="0.8"/>')
    # spire with lucarnes, flanked by pinnacles
    out.append(f'<path d="M {cx - w * 0.36:.1f} {sb:.1f} L {cx - 0.8:.1f} {top:.1f} L {cx + 0.8:.1f} {top:.1f} L {cx + w * 0.36:.1f} {sb:.1f} Z" fill="{roof}"/>')
    out.append(f'<path d="M {cx + 0.2:.1f} {top + 2:.1f} L {cx + w * 0.36:.1f} {sb:.1f} L {cx + w * 0.1:.1f} {sb:.1f} Z" fill="{lit}" opacity="0.45"/>')
    for i in range(6):
        y = sb - (sb - top) * (0.12 + i * 0.13)
        hw = w * 0.36 * (y - top) / (sb - top)
        out.append(f'<line x1="{cx - hw:.1f}" y1="{y:.1f}" x2="{cx - hw - 2.2:.1f}" y2="{y - 2.4:.1f}" stroke="{roof}" stroke-width="1.5"/>'
                   f'<line x1="{cx + hw:.1f}" y1="{y:.1f}" x2="{cx + hw + 2.2:.1f}" y2="{y - 2.4:.1f}" stroke="{roof}" stroke-width="1.5"/>')
    out.append(f'<path d="M {cx - 3:.1f} {sb - 6:.1f} L {cx:.1f} {sb - 15:.1f} L {cx + 3:.1f} {sb - 6:.1f} Z" fill="{lit}" opacity="0.8"/>')
    for d in (-0.5, 0.5):
        x = cx + d * w
        out.append(f'<path d="M {x - 2.6:.1f} {sb + 1:.1f} L {x:.1f} {sb - 24:.1f} L {x + 2.6:.1f} {sb + 1:.1f} Z" fill="{roof}"/>')
        out.append(f'<line x1="{x:.1f}" y1="{sb - 24:.1f}" x2="{x:.1f}" y2="{sb - 28:.1f}" stroke="{roof}" stroke-width="1.2"/>')
    out.append(f'<line x1="{cx:.1f}" y1="{top:.1f}" x2="{cx:.1f}" y2="{top - 5:.1f}" stroke="{rim}" stroke-width="1.4"/>')
    return "".join(out)


def crown_spire(cx, base, w, u):
    """St Giles' Cathedral: square tower with corner pinnacles and the open stone crown of flying ribs, floodlit."""
    tt = base - 46
    out = [defs(lg(f"{u}-sg", [(0, "#F6D59A"), (1, "#B48A70")], 0, 0, 1, 0))]
    out.append(glow(cx, tt - 12, 46, "#FFD898", f"{u}-sgg", 0.45))
    out.append(f'<rect x="{cx - w / 2:.1f}" y="{tt:.1f}" width="{w:.1f}" height="{base - tt:.1f}" fill="url(#{u}-sg)"/>')
    for d in (-0.2, 0.2):
        out.append(f'<path d="M {cx + d * w - 2:.1f} {tt + 26:.1f} L {cx + d * w - 2:.1f} {tt + 10:.1f} Q {cx + d * w:.1f} {tt + 5:.1f} {cx + d * w + 2:.1f} {tt + 10:.1f} L {cx + d * w + 2:.1f} {tt + 26:.1f} Z" fill="#4A3448"/>')
    out.append(f'<rect x="{cx - w / 2 - 1.5:.1f}" y="{tt - 3:.1f}" width="{w + 3:.1f}" height="3.5" fill="#FBE2AE"/>')
    # crenellated parapet
    out.append("".join(f'<rect x="{cx - w / 2 + i * w / 6:.1f}" y="{tt - 6:.1f}" width="{w / 12:.1f}" height="3.5" fill="#E8C690"/>' for i in range(7)))
    ctop = tt - 26
    # the four (visible: three) flying ribs of the crown, with crockets
    ribs = [(cx - w / 2, tt - 4), (cx + w / 2, tt - 4), (cx - w * 0.18, tt - 4), (cx + w * 0.18, tt - 4)]
    for k, (x, y) in enumerate(ribs):
        sw = 2.4 if k < 2 else 1.8
        out.append(f'<path d="M {x:.1f} {y:.1f} Q {x + (cx - x) * 0.2:.1f} {ctop + 2:.1f} {cx:.1f} {ctop + 8:.1f}" fill="none" stroke="#F2CE90" stroke-width="{sw}"/>')
        for t in (0.35, 0.6, 0.82):
            px = (1 - t) ** 2 * x + 2 * (1 - t) * t * (x + (cx - x) * 0.2) + t * t * cx
            py = (1 - t) ** 2 * y + 2 * (1 - t) * t * (ctop + 2) + t * t * (ctop + 8)
            out.append(f'<circle cx="{px:.1f}" cy="{py - 1.4:.1f}" r="1.2" fill="#FFE6B4"/>')
    for d in (-0.5, 0.5):
        x = cx + d * w
        out.append(f'<path d="M {x - 2.4:.1f} {tt - 4:.1f} L {x:.1f} {tt - 20:.1f} L {x + 2.4:.1f} {tt - 4:.1f} Z" fill="#F2CE90"/>')
    out.append(f'<rect x="{cx - 2.6:.1f}" y="{ctop + 2:.1f}" width="5.2" height="8" fill="#F2CE90"/>')
    out.append(f'<path d="M {cx - 2.2:.1f} {ctop + 3:.1f} L {cx:.1f} {ctop - 14:.1f} L {cx + 2.2:.1f} {ctop + 3:.1f} Z" fill="#FBE2AE"/>')
    out.append(f'<line x1="{cx:.1f}" y1="{ctop - 14:.1f}" x2="{cx:.1f}" y2="{ctop - 19:.1f}" stroke="#FBE2AE" stroke-width="1.3"/>')
    return "".join(out)


def edinburgh():
    u = "ed"
    out = [defs(
        lg(f"{u}-sky", [(0, "#141840"), (0.3, "#262A66"), (0.55, "#4E3C7C"), (0.74, "#9A5578"), (0.88, "#E0826A"), (1, "#F6B67C")], 0, 40, 0, 330, units="userSpaceOnUse"),
        lg(f"{u}-rock", [(0, "#4A3A52"), (0.5, "#3A2E46"), (1, "#241E30")], 0, 230, 0, 380, units="userSpaceOnUse"),
        lg(f"{u}-wall", [(0, "#9C7E86"), (0.55, "#D4AE8A"), (1, "#F2CC8E")], 0, 150, 0, 260, units="userSpaceOnUse"),
        lg(f"{u}-wall2", [(0, "#7E6676"), (1, "#C29C82")], 0, 150, 0, 260, units="userSpaceOnUse"),
        lg(f"{u}-half", [(0, "#A8806E"), (0.35, "#F4D296"), (0.7, "#E2B884"), (1, "#9C7A70")], 0, 0, 1, 0),
        lg(f"{u}-trees", [(0, "#22303A"), (1, "#121A22")]),
        lg(f"{u}-lawn", [(0, "#1E3A2E"), (1, "#0E1C18")]),
        lg(f"{u}-haze", [(0, "#F2A274", 0), (1, "#F2A274", 0.5)]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(500, 300, 250, "#FFB070", f"{u}-sun", 0.75))
    out.append(dots(70, 3, (0, 40, 600, 150), "#F4EEF8", r=(0.5, 1.3), opacity=(0.3, 0.95)))
    # a brighter evening star and long dusk clouds lit from below on the west side
    out.append('<circle cx="146" cy="78" r="1.8" fill="#FFF6E8"/>')
    for x, y, w, op in ((470, 120, 120, 0.5), (420, 134, 70, 0.4), (540, 150, 90, 0.45), (120, 132, 80, 0.25), (330, 104, 60, 0.25)):
        out.append(streak_cloud(x, y, w, "#3A2E62", op, 4.5) + streak_cloud(x + 6, y + 3, w * 0.8, "#F09A7A", op * 0.9, 1.8))
    # distant Pentland hills, faint in the afterglow
    poly, _ = ridge_poly([(330, 300), (400, 286), (470, 292), (540, 280), (610, 290)], 7, amp=4, fill="#7A5478")
    out.append(poly)
    # ---- Old Town on the ridge (east, left): tenements stepping down the Royal Mile
    rnd = random.Random(11)
    x = -12
    tcols = ["#3A3456", "#433A5E", "#3E3050", "#4A3E62", "#362E4C"]
    ten = []
    while x < 214:
        w = rnd.uniform(24, 42)
        top = 214 + (214 - x) * 0.16 + rnd.uniform(-10, 10)
        col = rnd.choice(tcols)
        ten.append((x, w, top, col))
        x += w - 1
    for k, (x, w, top, col) in enumerate(ten):
        gable = rnd.random() < 0.45
        out.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{w:.1f}" height="{340 - top:.1f}" fill="{col}"/>')
        if gable:
            out.append(stepped_gable(x + 1, w - 2, top + 0.5, w * 0.42, col, steps=4))
            out.append(f'<rect x="{x + w / 2 - 1.6:.1f}" y="{top - w * 0.42 - 6:.1f}" width="3.2" height="7" fill="{col}"/>')
        else:
            out.append(Q([(x, top), (x + 4, top - 8), (x + w - 4, top - 8), (x + w, top)], "#2A2440"))
            out.append(chimneys(x + 2, x + w - 2, top - 7, k * 5 + 1, col, h=(6, 11), every=(6, 14)))
        out.append(f'<rect x="{x + w - 3:.1f}" y="{top:.1f}" width="3" height="{340 - top:.1f}" fill="#000" opacity="0.18"/>')
        rows = int((340 - top - 8) / 11)
        out.append(win_grid(x + 3, top + 6, w - 6, rows * 11, max(2, int(w / 9)), rows, 40 + k, lit_p=0.5, dark="#2A2440", ww=0.45, wh=0.55))
    # St Giles' crown spire rising over the tenements
    out.append(crown_spire(98, 240, 30, u))
    # The Hub spire (Tolbooth Kirk) at the head of the Royal Mile
    out.append(gothic_spire(178, 262, 112, 26, u, "#5A4A66", "#3A3050", "#C08E86", "#F2B88A"))
    # Ramsay Garden: cream harled houses with red roofs and turrets, just below the esplanade
    rg_parts = [(196, 220, 34, "#E8D2B0"), (224, 230, 26, "#F0DEC0"), (244, 236, 20, "#E2C8A6")]
    for k, (x, top, w, col) in enumerate(rg_parts):
        out.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{w:.1f}" height="{300 - top:.1f}" fill="{col}"/>')
        out.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{w * 0.3:.1f}" height="{300 - top:.1f}" fill="#7A5A6A" opacity="0.35"/>')
        out.append(Q([(x - 2, top), (x + w / 2, top - w * 0.5), (x + w + 2, top)], "#B4543E"))
        out.append(Q([(x + w / 2, top - w * 0.5), (x + w + 2, top), (x + w / 2 + 2, top)], "#7E3A34", ' opacity="0.6"'))
        out.append(win_grid(x + 3, top + 6, w - 6, 300 - top - 10, max(2, int(w / 9)), int((300 - top - 10) / 12), 70 + k, lit_p=0.6, dark="#5A4A5A", ww=0.45, wh=0.5))
    # conical turrets
    for tx, ty, tw in ((206, 232, 9), (236, 238, 8), (260, 246, 7)):
        out.append(f'<rect x="{tx - tw / 2:.1f}" y="{ty:.1f}" width="{tw:.1f}" height="14" fill="#F2E2C6"/>'
                   + Q([(tx - tw / 2 - 1.5, ty), (tx, ty - tw * 1.8), (tx + tw / 2 + 1.5, ty)], "#A84A38"))
    # ---- Castle Rock: dolerite crag, cliffs on the north face
    rock = [(250, 262), (268, 256), (286, 252), (300, 246), (330, 240), (360, 236), (400, 234), (440, 236), (470, 238),
            (500, 242), (530, 246), (552, 252), (566, 270), (578, 300), (596, 322), (610, 330), (610, 380), (230, 380), (238, 300)]
    out.append(f'<clipPath id="{u}-rk"><polygon points="{P(rock)}"/></clipPath>')
    out.append(Q(rock, f"url(#{u}-rock)"))
    facets = []
    fr = random.Random(5)
    for i in range(16):
        x0 = 238 + i * 23 + fr.uniform(-6, 6)
        y0 = 244 + fr.uniform(0, 30)
        w = fr.uniform(14, 28)
        facets.append(Q([(x0, y0), (x0 + w, y0 + fr.uniform(-6, 6)), (x0 + w * 0.8, 380), (x0 + w * 0.1, 380)],
                        fr.choice(["#5E4A62", "#2A2236", "#4E3E5A", "#1E1A2A"]), f' opacity="{fr.uniform(0.35, 0.7):.2f}"'))
    out.append(f'<g clip-path="url(#{u}-rk)">' + "".join(facets)
               + streaks(110, 21, (236, 236, 610, 380), ["#6E5672", "#1A1626", "#8A6A78", "#2A2234"], w=(1.2, 3.2), length=(14, 50), opacity=(0.3, 0.7), slant=0.1)
               + f'<rect x="230" y="250" width="380" height="130" fill="url(#{u}-haze)" opacity="0.2"/>'
               + blobs(28, 9, (236, 300, 610, 370), ["#2E3A36", "#3A463E", "#24302C"], r=(5, 12), opacity=(0.6, 0.9)) + "</g>")
    ledges = "".join(f'<path d="M {x:.1f} {y:.1f} q {w * 0.5:.1f} {fr.uniform(-4, 4):.1f} {w:.1f} {fr.uniform(-3, 5):.1f}" fill="none" stroke="{c}" stroke-width="{sw}" opacity="0.5"/>'
                     for x, y, w, c, sw in [(fr.uniform(250, 560), fr.uniform(262, 350), fr.uniform(20, 60), fr.choice(["#1A1424", "#1A1424", "#5E4A62"]), fr.choice([1.5, 2.2])) for _ in range(26)])
    scrub = blobs(40, 17, (250, 266, 590, 340), ["#3E4A3A", "#4A5A44", "#2E3A30"], r=(2, 6), opacity=(0.6, 0.9), squash=0.55)
    west = Q([(500, 244), (552, 252), (566, 270), (578, 300), (596, 322), (610, 330), (610, 380), (560, 380), (548, 300), (530, 262)], "#C27A6A", ' opacity="0.28"')
    out.append(f'<g clip-path="url(#{u}-rk)">{ledges}{scrub}{west}</g>')
    # warm floodlight spill on the upper crag
    out.append(f'<g clip-path="url(#{u}-rk)">' + mist(400, 250, 190, 28, "#F4B884", f"{u}-fl", 0.45) + "</g>")
    out.append(f'<polyline points="{P(rock[8:15])}" fill="none" stroke="#F6A274" stroke-width="2" opacity="0.7"/>')
    # ---- The castle (floodlit sandstone): curtain wall, Half Moon Battery, Palace, War Memorial, Hospital, Barracks
    out.append(f'<rect x="456" y="196" width="76" height="52" fill="url(#{u}-wall2)"/>')  # New Barracks behind
    out.append(win_grid(458, 200, 72, 40, 9, 4, 3, lit_p=0.3, lit=("#FFE2A0",), dark="#8A6A78", ww=0.4, wh=0.45))
    out.append(f'<rect x="456" y="194" width="76" height="3" fill="#5A4A62"/>')
    # curtain wall following the crag
    cw = [(282, 254), (300, 248), (330, 242), (360, 238), (400, 236), (440, 238), (470, 240), (500, 244), (530, 248), (548, 254)]
    wall_top = [(x, y - 14) for x, y in cw]
    out.append(Q(wall_top + cw[::-1], f"url(#{u}-wall)"))
    out.append("".join(f'<rect x="{x - 2:.1f}" y="{y - 18:.1f}" width="4.5" height="5" fill="#E6C08C"/>' for x, y in rough(cw, 3, amp=0, depth=2)[1::1] if 290 < x < 545))
    # Hospital / Governor's House with crow-stepped gables
    for k, (x, w, top) in enumerate(((420, 34, 206), (452, 30, 212), (482, 28, 218))):
        out.append(f'<rect x="{x}" y="{top}" width="{w}" height="{240 - top}" fill="url(#{u}-wall)"/>')
        out.append(Q([(x - 6, top + 2), (x + 4, top - 10), (x + w - 4, top - 10), (x + w + 6, top + 2)], "#3A3450"))
        out.append(stepped_gable(x + w * 0.2, w * 0.6, top + 1, 16, "#E2BC8C"))
        out.append(f'<rect x="{x + w / 2 - 1.5:.1f}" y="{top - 8:.1f}" width="3" height="4" fill="#5A3E4A"/>')
        out.append(win_grid(x + 3, top + 4, w - 6, 240 - top - 8, 3, 3, 50 + k, lit_p=0.45, lit=("#FFE6A8", "#FFD98E"), dark="#8C6E70", ww=0.4, wh=0.5))
    # Scottish National War Memorial and the Great Hall at the summit (Crown Square)
    out.append(f'<rect x="350" y="192" width="72" height="46" fill="url(#{u}-wall)"/>')
    out.append(Q([(348, 192), (356, 182), (416, 182), (424, 192)], "#3A3450"))
    out.append(f'<rect x="376" y="176" width="20" height="62" fill="url(#{u}-wall)"/>')
    out.append(Q([(374, 176), (386, 160), (398, 176)], "#3A3450"))
    out.append(f'<path d="M 381 206 L 381 192 Q 386 184 391 192 L 391 206 Z" fill="#5A3E4A"/>')
    for x in (376, 396, 350, 422):
        out.append(f'<path d="M {x - 2:.1f} 194 L {x:.1f} 180 L {x + 2:.1f} 194 Z" fill="#E6C08C"/>' if x in (350, 422) else
                   f'<path d="M {x - 2:.1f} 178 L {x:.1f} 166 L {x + 2:.1f} 178 Z" fill="#E6C08C"/>')
    out.append("".join(f'<path d="M {x} 228 L {x} 210 Q {x + 3} 205 {x + 6} 210 L {x + 6} 228 Z" fill="#6A4A56"/>' for x in (356, 366, 402, 412)))
    # Royal Palace with its square tower, ogee-capped turret and flagpole
    out.append(f'<rect x="300" y="198" width="54" height="44" fill="url(#{u}-wall)"/>')
    out.append(Q([(298, 198), (306, 188), (348, 188), (356, 198)], "#3A3450"))
    out.append(win_grid(304, 204, 46, 30, 5, 2, 7, lit_p=0.7, lit=("#FFE6A8", "#FFD98E"), dark="#8C6E70", ww=0.45, wh=0.55))
    out.append(f'<rect x="318" y="168" width="22" height="30" fill="url(#{u}-wall)"/>')
    out.append(win_grid(320, 174, 18, 18, 2, 2, 9, lit_p=0.8, lit=("#FFE6A8",), dark="#8C6E70"))
    out.append("".join(f'<rect x="{317 + i * 4.8:.1f}" y="164" width="2.8" height="4.5" fill="#E6C08C"/>' for i in range(5)))
    out.append(f'<rect x="334" y="152" width="8" height="16" fill="#E6C08C"/><path d="M 333 152 Q 338 150 338 140 Q 338 150 343 152 Z" fill="#3A3450"/>')
    out.append('<line x1="324" y1="164" x2="324" y2="128" stroke="#2A2438" stroke-width="1.6"/>')
    out.append('<path d="M 325 129 Q 333 126 341 130 L 341 141 Q 333 137 325 140 Z" fill="#2A4E9A"/>'
               '<path d="M 325 129 L 341 141 M 341 130 L 325 140" stroke="#F2EEF2" stroke-width="1.6"/>'
               '<path d="M 333 128 L 333 139 M 325 135 L 341 135" stroke="#C8303A" stroke-width="1.4"/>')
    # Half Moon Battery (curved, east end) with gun embrasures, David's Tower stump above it
    out.append(f'<path d="M 270 258 L 272 222 Q 296 214 320 222 L 322 252 Z" fill="url(#{u}-half)"/>')
    out.append('<path d="M 271 224 Q 296 216 321 224" fill="none" stroke="#FBE2AE" stroke-width="2.2"/>')
    out.append("".join(f'<rect x="{x}" y="226" width="3.4" height="4" fill="#5A3E4A"/>' for x in (278, 288, 298, 308)))
    out.append(dots(30, 13, (274, 230, 318, 254), "#8A6A6A", r=(0.6, 1.4), opacity=(0.3, 0.6)))
    # Argyle / Mills Mount battery on the north ledge, with the One O'Clock Gun
    out.append(Q([(352, 252), (452, 252), (452, 240), (352, 240)], "#D2AA82"))
    out.append(f'<rect x="352" y="238" width="100" height="2.4" fill="#F4D49A"/>')
    out.append('<g fill="#2A2438">' + "".join(f'<rect x="{x}" y="236" width="8" height="2.2"/><circle cx="{x + 1}" cy="238.5" r="1.8"/>' for x in (368, 392, 416, 438)) + "</g>")
    # Western defences and the drop to the west
    out.append(f'<rect x="512" y="226" width="12" height="22" fill="url(#{u}-wall)"/><path d="M 511 226 L 518 216 L 525 226 Z" fill="#3A3450"/>')
    # rim of sunset on the west edges
    out.append('<g stroke="#FFB27A" stroke-width="1.6" opacity="0.8"><line x1="532" y1="196" x2="532" y2="248"/><line x1="354" y1="198" x2="354" y2="242"/><line x1="340" y1="168" x2="340" y2="198"/><line x1="422" y1="192" x2="422" y2="238"/></g>')
    # Castle Esplanade with its lamps
    out.append(Q([(236, 268), (280, 258), (282, 266), (238, 274)], "#B48C7A"))
    out.append(lamp_post(252, 266, 14, u, 1, r=12, strength=0.7, s=0.45) + lamp_post(270, 262, 14, u, 2, r=12, strength=0.7, s=0.45))
    # ---- Princes Street Gardens: wooded slope, the railway in the valley, lawn and lamps
    tl = rough([(-10, 330), (80, 320), (170, 326), (250, 318), (340, 326), (430, 318), (520, 324), (610, 316)], 31, amp=10, depth=4)
    out.append(Q(tl + [(610, 400), (-10, 400)], f"url(#{u}-trees)"))
    trnd = random.Random(33)
    for i in range(34):
        cx = -10 + i * 19 + trnd.uniform(-6, 6)
        cy = y_on(tl, max(-9, min(609, cx))) + trnd.uniform(4, 22)
        out.append(leaf_canopy(f"{u}-t{i}", cx, cy, trnd.uniform(14, 24), trnd.uniform(10, 16), 100 + i,
                               "#0E161E", "#1C2830", "#34464A", gold="#B88A6A" if trnd.random() < 0.4 else None, light=(0.7, -0.7), n=40, r=(0.12, 0.22)))
    # train gliding through the gardens towards Waverley
    out.append('<rect x="-10" y="372" width="620" height="18" fill="#14141E"/>')
    out.append('<rect x="-10" y="388" width="620" height="2" fill="#3A3A4A"/>')
    for k in range(5):
        x0 = 112 + k * 64
        out.append(f'<rect x="{x0}" y="368" width="61" height="18" rx="2.5" fill="#2E3446"/>'
                   f'<rect x="{x0}" y="368" width="61" height="3" rx="1.5" fill="#56607A"/>'
                   + "".join(f'<rect x="{x0 + 4 + j * 10.5:.1f}" y="373" width="7.5" height="6" rx="1" fill="#FFE0A0"/>' for j in range(6))
                   + f'<rect x="{x0}" y="381" width="61" height="1.6" fill="#B8A040"/>')
    out.append(glow(112, 378, 26, "#FFF2C8", f"{u}-hl", 0.7))
    out.append('<path d="M 112 368 Q 102 370 100 378 L 100 386 L 112 386 Z" fill="#2E3446"/><rect x="101" y="372" width="9" height="6" rx="1.5" fill="#9AB0D0"/><circle cx="103" cy="382" r="1.6" fill="#FFF6D8"/>')
    out.append(mist(260, 380, 260, 14, "#F2C8A0", f"{u}-st", 0.25))
    # lawn with a curving path
    out.append(f'<path d="M -10 392 Q 300 384 610 392 L 610 444 L -10 444 Z" fill="url(#{u}-lawn)"/>')
    out.append('<path d="M -10 432 C 120 418 240 408 330 404 C 420 400 500 400 610 404 L 610 410 C 500 406 420 408 330 412 C 240 418 140 430 -10 444 Z" fill="#6A5A62"/>')
    out.append(grass(120, 61, (-10, 396, 610, 444), ["#2E4A3A", "#3E5A44", "#22382E"], h=(4, 10)))
    out.append(lamp_post(76, 432, 64, u, 3, r=60))
    out.append(lamp_post(470, 402, 44, u, 4, r=40))
    out.append(mist(330, 412, 160, 10, "#FFD58A", f"{u}-pg", 0.25))
    out.append(f'<path d="M 360 422 Q 470 414 610 418 L 610 432 Q 470 428 360 434 Z" fill="#1A2A22"/>')
    out.append(dots(90, 77, (366, 416, 610, 430), "#E87A8A", r=(1, 2.2), opacity=(0.5, 0.95)) + dots(60, 78, (366, 416, 610, 430), "#F2D27A", r=(1, 2), opacity=(0.5, 0.9))
               + dots(40, 79, (366, 416, 610, 430), "#F4F0F0", r=(0.8, 1.6), opacity=(0.4, 0.8)))
    out.append('<g fill="#1A1622"><rect x="218" y="404" width="34" height="3" rx="1"/><rect x="218" y="397" width="34" height="2.4" rx="1"/><rect x="218" y="401" width="34" height="1.6"/><rect x="220" y="404" width="2" height="8"/><rect x="248" y="404" width="2" height="8"/></g>')
    # strollers on the path, and a piper heading home
    out.append(figure(300, 408, 20, "#5A3A4A", rim="#FFC890", rim_side=-1) + figure(312, 408, 18, "#2E3A5A", rim="#FFC890", rim_side=-1))
    out.append(figure(420, 404, 15, "#3A4A3A"))
    out.append('<g transform="translate(176 424)">'
               '<path d="M -5 -22 L 5 -22 L 6 -10 L -6 -10 Z" fill="#1E2A3A"/>'
               '<path d="M -6 -10 L 6 -10 L 7 -1 L -7 -1 Z" fill="#9A2A2A"/><path d="M -6 -7 L 7 -7 M -6 -4 L 7 -4 M -2 -10 L -2 -1 M 3 -10 L 3 -1" stroke="#2A3A2A" stroke-width="1"/>'
               '<rect x="-4" y="-1" width="2.4" height="8" fill="#E8E0D0"/><rect x="1.6" y="-1" width="2.4" height="8" fill="#E8E0D0"/>'
               '<circle cx="0" cy="-26" r="4" fill="#E2B49A"/><path d="M -4.5 -27 Q 0 -33 4.5 -27 Z" fill="#1E2A3A"/>'
               '<ellipse cx="-6" cy="-15" rx="5" ry="4" fill="#9A2A2A"/>'
               '<g stroke="#2A2020" stroke-width="1.4" stroke-linecap="round"><line x1="-7" y1="-18" x2="-10" y2="-36"/><line x1="-5" y1="-18" x2="-5" y2="-38"/><line x1="-3" y1="-18" x2="0" y2="-37"/><line x1="-6" y1="-13" x2="-3" y2="-24"/></g></g>')
    out.append(gulls([(250, 152, 9), (270, 162, 7), (560, 176, 8)], "#1E1A36", 1.7))
    return "\n".join(out)


# ================================================================ DUBLIN — the Ha'penny Bridge over the Liffey, looking west at golden hour
def proj(C, X, pts):
    return [C(X, y, z) for z, y in pts]


def quay_house(C, X, z0, z1, yb, h, wall, seed, shop=None, lit_side=True, sash="#2E3448", glow_p=0.25, trim="#F2E8D8"):
    """Georgian / painted quay-front house in the plane X: sash windows in bays, a shopfront with a painted
    fascia, cornice and chimney stack."""
    rnd = random.Random(seed)
    W = z1 - z0
    out = [Q(C.quad_x(X, z0, z1, yb, yb + h), wall)]
    far = z0 > 160
    bays = max(2, int(W / 2.4))
    floors = int((h - 4.2) / 3.0)
    if not far:
        for f_ in range(floors):
            ya = yb + 4.6 + f_ * 3.0
            yt = ya + (2.1 if f_ == 0 else 1.8 - 0.1 * f_)
            for i in range(bays):
                za = z0 + W * (i + 0.3) / bays
                zb = z0 + W * (i + 0.7) / bays
                g = rnd.random() < glow_p
                out.append(Q(C.quad_x(X, za - 0.12, zb + 0.12, ya - 0.18, yt + 0.12), trim, ' opacity="0.75"'))
                out.append(Q(C.quad_x(X, za, zb, ya, yt), "#FFD98E" if g else sash))
                if z0 < 90:
                    m = C(X, (ya + yt) / 2, (za + zb) / 2)
                    m0 = C(X, (ya + yt) / 2, za)
                    m1 = C(X, (ya + yt) / 2, zb)
                    out.append(f'<line x1="{m0[0]:.1f}" y1="{m0[1]:.1f}" x2="{m1[0]:.1f}" y2="{m1[1]:.1f}" stroke="{trim}" stroke-width="0.9" opacity="0.8"/>')
        # shopfront
        sc = shop or rnd.choice(["#2E4E3E", "#7A2A2A", "#1E3456", "#3A2A2A", "#C8963A"])
        out.append(Q(C.quad_x(X, z0 + 0.2, z1 - 0.2, yb, yb + 3.8), sc))
        out.append(Q(C.quad_x(X, z0 + 0.4, z1 - 0.4, yb + 3.0, yb + 3.6), mix(sc, "#F2E2B8", 0.55)))
        out.append(Q(C.quad_x(X, z0 + 0.8, z1 - 0.8, yb + 0.6, yb + 2.7), "#FFCF7E" if rnd.random() < 0.7 else "#3A3A4A", ' opacity="0.9"'))
    else:
        out.append(win_grid(*_bbox(C.quad_x(X, z0, z1, yb + 4, yb + h - 1)), max(2, bays), max(1, floors), seed, lit_p=0.25, dark=sash, ww=0.4, wh=0.45))
    # cornice / parapet and chimney
    out.append(Q(C.quad_x(X, z0, z1, yb + h - 0.6, yb + h), trim, ' opacity="0.85"'))
    if rnd.random() < 0.8:
        zc = rnd.uniform(z0 + 0.6, z1 - 1.6)
        Xc = X + (-0.8 if X < 0 else 0.8)
        out.append(Q(C.quad_x(Xc, zc, zc + 1.2, yb + h, yb + h + 1.6), mix(wall, "#3A2A2A", 0.35)))
        for j in range(3):
            pz = zc + 0.2 + j * 0.4
            a, b = C(Xc, yb + h + 1.6, pz), C(Xc, yb + h + 2.2, pz)
            out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#8A4A3A" stroke-width="{max(0.8, 120 / pz):.1f}"/>')
    # party wall shadow line
    out.append(Q(C.quad_x(X, z0, z0 + 0.3, yb, yb + h), "#000", ' opacity="0.2"'))
    if not lit_side:
        out.append(Q(C.quad_x(X, z0, z1, yb, yb + h), "#2A2E5A", ' opacity="0.22"'))
    return "".join(out)


def _bbox(q):
    xs = [p[0] for p in q]
    ys = [p[1] for p in q]
    return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)


def dublin():
    u = "db"
    C = Cam(f=640, cx=300, vpy=300, eye=2.0)
    ZB = 62.0
    k = C.f / ZB
    out = [defs(
        lg(f"{u}-sky", [(0, "#5476AE"), (0.32, "#94A4CA"), (0.66, "#E2BCA8"), (0.88, "#F6D4A2"), (1, "#FAE2B2")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-water", [(0, "#E8C49A"), (0.12, "#A89CA0"), (0.4, "#5A7484"), (1, "#1E3442")], 0, 300, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-granite", [(0, "#8E8A8E"), (1, "#5A5662")]),
        lg(f"{u}-path", [(0, "#F7D9A0", 0.0), (0.5, "#FFE6B0", 0.8), (1, "#F7D9A0", 0.0)], 0, 0, 1, 0),
        lg(f"{u}-far", [(0, "#B496A8"), (1, "#9A8098")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(250, 190, 240, "#FFE2A0", f"{u}-sun", 0.85))
    out.append('<circle cx="250" cy="190" r="15" fill="#FFF4D2"/>')
    # soft Irish cumulus, lit from the low western sun
    out.append(cumulus(f"{u}-c1", 128, 116, 160, 46, 3, "#FFF0D8", "#E6C6BE", "#9290B0", light=1))
    out.append(cumulus(f"{u}-c2", 470, 100, 190, 56, 8, "#FFF0D8", "#E2C4BE", "#8A88AA", light=-1))
    out.append(cumulus(f"{u}-c3", 316, 150, 96, 24, 12, "#FFF6E6", "#F2D6C4", "#B8AABE", light=-1))
    out.append(streak_cloud(190, 210, 80, "#F8D4B0", 0.6, 3) + streak_cloud(410, 220, 60, "#F8D4B0", 0.5, 2.5))
    # distant city upriver: hazy roofs and the copper dome of the Four Courts on the north quay
    far = rough([(200, 286), (230, 280), (260, 284), (290, 278), (320, 282), (350, 276), (400, 282)], 5, amp=3, depth=3)
    out.append(Q(far + [(400, 300), (200, 300)], f"url(#{u}-far)"))
    out.append(dots(40, 6, (205, 284, 395, 298), "#FFE2A8", r=(0.6, 1.1), opacity=(0.5, 1)))
    fx, fb = C(40, 3.4, 460)
    s_ = C.f / 460
    fc = "#B8A0AE"
    out.append(f'<rect x="{fx - 34 * s_:.1f}" y="{fb - 16 * s_:.1f}" width="{68 * s_:.1f}" height="{16 * s_:.1f}" fill="{fc}"/>')
    out.append(Q([(fx - 11 * s_, fb - 16 * s_), (fx, fb - 21 * s_), (fx + 11 * s_, fb - 16 * s_)], fc))
    out.append(f'<rect x="{fx - 11 * s_:.1f}" y="{fb - 30 * s_:.1f}" width="{22 * s_:.1f}" height="{14 * s_:.1f}" fill="#C4ACB6"/>')
    out.append("".join(f'<rect x="{fx - 10 * s_ + i * 2.6 * s_:.1f}" y="{fb - 29 * s_:.1f}" width="{1.1 * s_:.1f}" height="{11 * s_:.1f}" fill="#9A8296"/>' for i in range(8)))
    out.append(f'<path d="M {fx - 10.5 * s_:.1f} {fb - 30 * s_:.1f} Q {fx - 10 * s_:.1f} {fb - 41 * s_:.1f} {fx:.1f} {fb - 42 * s_:.1f} Q {fx + 10 * s_:.1f} {fb - 41 * s_:.1f} {fx + 10.5 * s_:.1f} {fb - 30 * s_:.1f} Z" fill="#7EA696"/>')
    out.append(f'<path d="M {fx - 10.5 * s_:.1f} {fb - 30 * s_:.1f} Q {fx - 10 * s_:.1f} {fb - 41 * s_:.1f} {fx:.1f} {fb - 42 * s_:.1f} L {fx:.1f} {fb - 30 * s_:.1f} Z" fill="#B8D8C0" opacity="0.5"/>')
    out.append(f'<rect x="{fx - 2 * s_:.1f}" y="{fb - 47 * s_:.1f}" width="{4 * s_:.1f}" height="{5.5 * s_:.1f}" fill="#C4ACB6"/><path d="M {fx - 2.4 * s_:.1f} {fb - 47 * s_:.1f} Q {fx:.1f} {fb - 51 * s_:.1f} {fx + 2.4 * s_:.1f} {fb - 47 * s_:.1f} Z" fill="#7EA696"/>')
    # river surface
    out.append(f'<polygon points="{P([C(-20, 0, 900), C(20, 0, 900), C(20, 0, 3), C(-20, 0, 3)])}" fill="url(#{u}-water)"/>')
    # quay walls (granite) and quay roads, both banks
    for sgn in (-1, 1):
        out.append(Q([C(sgn * 20, 0, 900), C(sgn * 20, 3.4, 900), C(sgn * 20, 3.4, 30), C(sgn * 20, 0, 30)], f"url(#{u}-granite)"))
        out.append(Q([C(sgn * 20, 3.4, 900), C(sgn * 32, 3.4, 900), C(sgn * 32, 3.4, 30), C(sgn * 20, 3.4, 30)], "#6E6A72"))
        out.append(Q([C(sgn * 20, 3.1, 900), C(sgn * 20, 3.4, 900), C(sgn * 20, 3.4, 30), C(sgn * 20, 3.1, 30)], "#D8D0C8"))
        out.append(Q([C(sgn * 20, 0, 900), C(sgn * 20, 0.9, 900), C(sgn * 20, 0.9, 30), C(sgn * 20, 0, 30)], "#3A4A3E", ' opacity="0.7"'))
        for z in (42, 52, 66, 80, 100, 130, 170, 230):
            a_, b_ = C(sgn * 20, 0.9, z), C(sgn * 20, 3.1, z)
            out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#4A4652" stroke-width="{max(0.6, 40 / z):.1f}" opacity="0.5"/>')
    # quay-front houses: south bank (left, in shade) painted Temple Bar fronts; north bank (right, sunlit) Georgian brick
    south = [(60, 68, 16, "#C8B49A", "#3A2A2A"), (68, 75, 15, "#2E4A6E", None), (75, 81, 14, "#E2B44A", None), (81, 89, 17, "#B8433A", None),
             (89, 96, 14, "#E8DCC4", None), (96, 105, 16, "#3E6A52", None), (105, 114, 15, "#A8583E", None), (114, 124, 17, "#E6CFA8", None),
             (124, 136, 14, "#7A3A4A", None), (136, 150, 16, "#C8A070", None), (150, 168, 15, "#4A5A7A", None), (168, 190, 17, "#B86A4A", None),
             (190, 230, 14, "#A89080", None), (230, 300, 16, "#9A8088", None), (300, 420, 15, "#A08A94", None)]
    north = [(60, 68, 17, "#A8583E", "#1E3456"), (68, 76, 16, "#B8664A", "#2E4E3E"), (76, 84, 17, "#94503E", "#7A2A2A"), (84, 91, 14, "#E8D6B0", "#2E4E3E"),
             (91, 100, 17, "#B05A40", None), (100, 109, 16, "#C87A4E", None), (109, 120, 17, "#9A4E3C", None), (120, 132, 15, "#E2C890", None),
             (132, 146, 17, "#A8583E", None), (146, 164, 16, "#BC6E4A", None), (164, 186, 17, "#9E5440", None), (186, 214, 15, "#D8B888", None),
             (214, 260, 17, "#A86A50", None), (260, 300, 15, "#B48070", None), (340, 420, 16, "#B08070", None)]
    for sgn, row, lit in ((-1, south, False), (1, north, True)):
        for i, (z0, z1, h, wall, shop) in reversed(list(enumerate(row))):
            out.append(quay_house(C, sgn * 32, z0, z1, 3.4, h, wall, 100 * (sgn + 2) + i, shop=shop, lit_side=lit, glow_p=0.15 if lit else 0.3))
    out.append(f'<polygon points="{P([C(32, 3.4, 420), C(32, 21, 420), C(32, 21, 60), C(32, 3.4, 60)])}" fill="#FFC870" opacity="0.13"/>')
    # Merchant's Arch at the south end of the bridge
    out.append(Q(C.quad_x(-32, 58.0, 63.5, 3.4, 16), "#B4A898"))
    out.append(Q(proj(C, -32, [(59.6, 3.4), (59.6, 7.2), (60.75, 8.6), (61.9, 7.2), (61.9, 3.4)]), "#2A2430"))
    out.append(Q(C.quad_x(-32, 58.0, 63.5, 15.2, 16), "#E8DCC8"))
    out.append(Q(C.quad_x(-32, 58.0, 63.5, 3.4, 16), "#2A2E5A", ' opacity="0.22"'))
    # quayside railings and lamps
    for sgn in (-1, 1):
        for z in (40, 48, 76, 96, 124, 160, 210):
            a_, b_ = C(sgn * 20.6, 3.4, z), C(sgn * 20.6, 7.4, z)
            s2 = C.f / z
            out.append(glow(b_[0], b_[1], s2 * 1.6, "#FFE0A0", f"{u}-ql{sgn + 1}{z}", 0.55))
            out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#1E2E2A" stroke-width="{max(1, s2 * 0.16):.1f}"/>'
                       f'<circle cx="{b_[0]:.1f}" cy="{b_[1]:.1f}" r="{max(1.2, s2 * 0.28):.1f}" fill="#FFF0C8"/>')
        r0, r1 = C(sgn * 20.4, 4.4, 34), C(sgn * 20.4, 4.4, 300)
        out.append(f'<line x1="{r0[0]:.1f}" y1="{r0[1]:.1f}" x2="{r1[0]:.1f}" y2="{r1[1]:.1f}" stroke="#1E2A28" stroke-width="1.6" opacity="0.8"/>')
    # water: sun path, painterly reflections of the house fronts, ripples
    out.append(f'<rect x="190" y="300" width="150" height="144" fill="url(#{u}-path)" opacity="0.55"/>')
    rnd = random.Random(7)
    refl = []
    for sgn, row in ((-1, south), (1, north)):
        for z0, z1, h, wall, shop in row:
            xa = C(sgn * 20, 0, z0)[0]
            xb = C(sgn * 20, 0, z1)[0]
            y0 = C(sgn * 20, 0, (z0 + z1) / 2)[1]
            L = C.f * (h * 0.9) / ((z0 + z1) / 2)
            refl.append(f'<rect x="{min(xa, xb):.1f}" y="{y0:.1f}" width="{abs(xb - xa):.1f}" height="{L:.1f}" fill="{wall}" opacity="0.32"/>')
    out.append(f'<g>{"".join(refl)}</g>')
    out.append(water_lines(230, 9, (30, 304, 570, 444), ["#F8D8A0", "#FFE8C0", "#7E98A6", "#2E4A5A", "#1E3442"], w=(8, 46), h=(1, 2.4), opacity=(0.35, 0.85)))
    out.append(water_lines(80, 10, (200, 302, 320, 330), ["#FFF0C8", "#FFE0A0"], w=(4, 22), h=(0.8, 1.6), opacity=(0.5, 1), grow=False))
    # ---- the Ha'penny Bridge (cast-iron elliptical arch, 1816) at Z = ZB, lamps lit, sun behind it
    def bx(X):
        return 300 + k * X

    def by(Y):
        return C.vpy + k * (C.eye - Y)

    N = 60
    Xs = [-20.6 + 41.2 * i / N for i in range(N + 1)]
    deck = [(bx(X), by(3.6 + 1.7 * (1 - (X / 20.6) ** 2))) for X in Xs]
    rail = [(x, y - k * 1.15) for x, y in deck]
    arch = [(bx(X), by(1.5 + 2.9 * math.sqrt(max(0, 1 - (X / 20.6) ** 2)))) for X in Xs]
    wy = by(0)
    ref = lambda pts: [(x, 2 * wy - y) for x, y in pts]
    # reflection: the arch and its mirror make the famous ellipse
    out.append(f'<polygon points="{P(ref(rail) + ref(arch)[::-1])}" fill="#7E8298" opacity="0.4"/>')
    out.append(f'<polyline points="{P(ref(arch))}" fill="none" stroke="#F2EEE8" stroke-width="3.2" opacity="0.75"/>')
    out.append(f'<polyline points="{P(ref(deck))}" fill="none" stroke="#F2EEE8" stroke-width="2.4" opacity="0.5"/>')
    for j in range(3):
        X = (-10.3, 0, 10.3)[j]
        i = int((X + 20.6) / 41.2 * N)
        x, y = ref(rail)[i]
        out.append(f'<rect x="{x - 2.5:.1f}" y="{y + k * 2.2:.1f}" width="5" height="5" fill="#FFE6A8" opacity="0.6"/>')
    out.append(water_lines(70, 12, (bx(-20), wy + 3, bx(20), wy + 64), ["#3E5A6A", "#5A7484", "#F8D8A0"], w=(12, 34), h=(1, 2), opacity=(0.5, 0.9), grow=False))
    # stone abutments on the quays
    for sgn in (-1, 1):
        out.append(Q([(bx(sgn * 20.0), by(0)), (bx(sgn * 20.0), by(3.9)), (bx(sgn * 24), by(3.9)), (bx(sgn * 24), by(0))], "#8A8490"))
        out.append(Q([(bx(sgn * 20.0), by(3.6)), (bx(sgn * 20.0), by(3.9)), (bx(sgn * 24), by(3.9)), (bx(sgn * 24), by(3.6))], "#D8D0C8"))
    # spandrel face, rings diminishing towards the crown
    out.append(f'<polygon points="{P(deck + arch[::-1])}" fill="#C6C2D2" opacity="0.32"/>')
    for i in range(-9, 10):
        if i == 0:
            continue
        X = i * 2.05
        yd = by(3.6 + 1.7 * (1 - (X / 20.6) ** 2))
        ya = by(1.5 + 2.9 * math.sqrt(max(0, 1 - (X / 20.6) ** 2)))
        r = (ya - yd) * 0.4
        if r > 1.6:
            out.append(f'<circle cx="{bx(X):.1f}" cy="{(yd + ya) / 2:.1f}" r="{r:.1f}" fill="none" stroke="#F0ECF0" stroke-width="{min(2.4, max(1.5, r * 0.3)):.1f}"/>')
    out.append(f'<polyline points="{P([(x, y + 3) for x, y in arch])}" fill="none" stroke="#8A88A0" stroke-width="2"/>')
    out.append(f'<polyline points="{P(arch)}" fill="none" stroke="#F4F0EA" stroke-width="5"/>')
    out.append(f'<polyline points="{P(deck)}" fill="none" stroke="#F6F2EC" stroke-width="4"/>')
    lat = []
    for i in range(N):
        (x0, y0), (x1, y1) = deck[i], deck[i + 1]
        (u0, v0), (u1, v1) = rail[i], rail[i + 1]
        lat.append(f'M {x0:.1f} {y0:.1f} L {u1:.1f} {v1:.1f} M {u0:.1f} {v0:.1f} L {x1:.1f} {y1:.1f}')
    out.append(f'<path d="{" ".join(lat)}" stroke="#ECE8F0" stroke-width="1.3" fill="none"/>')
    out.append(f'<polyline points="{P(rail)}" fill="none" stroke="#F8F4EE" stroke-width="3"/>')
    out.append(f'<polyline points="{P(rail[6:55])}" fill="none" stroke="#FFD890" stroke-width="1.3"/>')
    # people crossing, silhouetted against the light
    for X, h, c in ((-15.5, 19, "#3A3046"), (-14.2, 17, "#8A3A3A"), (-5, 20, "#2E3A50"), (4.5, 19, "#4A3A2E"), (13.5, 18, "#3A4A3A")):
        i = int((X + 20.6) / 41.2 * N)
        out.append(figure(deck[i][0], deck[i][1] - 1.5, h, c, rim="#FFD9A0", rim_side=-1))
    # the three lamp arches with their lanterns
    for j, X in enumerate((-10.3, 0, 10.3)):
        i = int((X + 20.6) / 41.2 * N)
        x, y = rail[i]
        top = y - k * 2.6
        out.append(glow(x, top + 3, 34, "#FFE6A8", f"{u}-bl{j}", 0.8))
        out.append(f'<path d="M {x - 5:.1f} {deck[i][1]:.1f} L {x - 4.6:.1f} {y:.1f} Q {x - 5:.1f} {top + 5:.1f} {x:.1f} {top + 1:.1f} Q {x + 5:.1f} {top + 5:.1f} {x + 4.6:.1f} {y:.1f} L {x + 5:.1f} {deck[i][1]:.1f}" fill="none" stroke="#F4F0F2" stroke-width="2.2"/>')
        out.append(f'<path d="M {x - 3.4:.1f} {top + 4:.1f} L {x - 2.6:.1f} {top - 3:.1f} L {x + 2.6:.1f} {top - 3:.1f} L {x + 3.4:.1f} {top + 4:.1f} Z" fill="#FFF4D2"/>'
                   f'<path d="M {x - 3.8:.1f} {top - 3:.1f} L {x:.1f} {top - 7:.1f} L {x + 3.8:.1f} {top - 3:.1f} Z" fill="#2A2A3A"/>'
                   f'<rect x="{x - 3.6:.1f}" y="{top + 4:.1f}" width="7.2" height="1.6" fill="#2A2A3A"/>')
    # foreground: the Liffey Boardwalk on the north quay, a green Dublin lamp standard and a gull on watch
    out.append(Q([(440, 444), (474, 404), (610, 398), (610, 444)], "#5A3E30"))
    out.append('<path d="M 474 404 L 610 398" stroke="#D8A070" stroke-width="2.4"/>')
    out.append('<g stroke="#3E2A22" stroke-width="1.4">' + "".join(f'<line x1="{474 - (y - 404) * 0.85:.1f}" y1="{y}" x2="610" y2="{y - 6:.1f}"/>' for y in (414, 424, 434)) + "</g>")
    out.append('<path d="M 476 398 L 610 392" stroke="#2A1E1A" stroke-width="2.4"/><path d="M 476 380 L 610 374" stroke="#2A1E1A" stroke-width="2.8"/>'
               + "".join(f'<line x1="{x}" y1="{398 - (x - 476) * 0.045:.1f}" x2="{x}" y2="{380 - (x - 476) * 0.045:.1f}" stroke="#2A1E1A" stroke-width="1.5"/>' for x in range(484, 610, 9)))
    out.append(lamp_post(524, 402, 116, u, 9, post="#1E3A30", r=46, s=1.6, strength=0.75))
    out.append('<g transform="translate(524 278)"><path d="M -13 -2 Q -4 -11 9 -8 L 16 -4 L 8 -1 Q -4 1 -13 -2 Z" fill="#F4F0EA"/><path d="M -2 -9 Q 7 -11 13 -5 L 5 -3 Z" fill="#8E8E9E"/>'
               '<circle cx="-13" cy="-7" r="4" fill="#F4F0EA"/><path d="M -16.8 -7 L -21.6 -6" stroke="#F2B040" stroke-width="2"/><path d="M -11 -10.5 Q -7 -12.5 -3 -9" stroke="#FFD9A0" stroke-width="1.4" fill="none"/>'
               '<path d="M 16 -4 L 19 -3" stroke="#2A2A2A" stroke-width="2"/><path d="M -2 -1 L -3 3 M 2 -1 L 3 3" stroke="#E8A040" stroke-width="1.3"/></g>')
    out.append(gulls([(110, 186, 12), (136, 198, 9), (420, 170, 11), (446, 182, 8), (352, 232, 6)], "#3A3A56", 1.8))
    return "\n".join(out)

# ================================================================ SWISS ALPS — the Matterhorn above Zermatt, crisp summer morning
def flowers(n, seed, box, cols, r=(1.2, 2.6)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        k = 0.5 + 0.8 * (y - y0) / max(1, y1 - y0)
        rr = rnd.uniform(*r) * k
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="{rnd.choice(cols)}"/>')
    return "".join(out)


def swiss_alps():
    u = "sa"
    out = [defs(
        lg(f"{u}-sky", [(0, "#1A4E9E"), (0.35, "#3E7CC8"), (0.75, "#94C2EC"), (1, "#D4ECF8")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-east", [(0, "#F2D0A8"), (0.45, "#C49A80"), (1, "#8A7078")], 0, 98, 0, 320, units="userSpaceOnUse"),
        lg(f"{u}-north", [(0, "#6A7AA0"), (1, "#3E4A6E")], 0, 98, 0, 320, units="userSpaceOnUse"),
        lg(f"{u}-range", [(0, "#F4F8FC"), (1, "#B8CCE4")]),
        lg(f"{u}-haze", [(0, "#DCEEFA", 0), (1, "#DCEEFA", 0.9)]),
        lg(f"{u}-meadow", [(0, "#8EBE58"), (1, "#4E8A3A")]),
        lg(f"{u}-fore", [(0, "#7AB04A"), (1, "#3E7232")]),
        lg(f"{u}-wood", [(0, "#8A4A2E"), (1, "#5A2E1E")]),
        lg(f"{u}-roof", [(0, "#8A8A94"), (1, "#5E5E6A")]),
        lg(f"{u}-train", [(0, "#E8343A"), (1, "#A81E26")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(40, 60, 200, "#FFF6D8", f"{u}-sun", 0.6))
    out.append(cumulus(f"{u}-c1", 110, 150, 120, 30, 4, "#FFFFFF", "#E8F0F8", "#A8BCD8", light=-1))
    out.append(cumulus(f"{u}-c2", 520, 132, 110, 28, 9, "#FFFFFF", "#E4EEF8", "#A4B8D6", light=-1))
    # distant snowy ranges either side (Breithorn massif left, Dent Blanche side right)
    for pts, seed in (([(-10, 268), (40, 236), (90, 226), (140, 244), (190, 250), (240, 290)], 3),
                      ([(380, 290), (430, 246), (470, 232), (520, 220), (560, 238), (610, 228)], 5)):
        poly, line = ridge_poly(pts, seed, amp=10, depth=4, fill=f"url(#{u}-range)")
        out.append(poly)
        shade = [(x + 6, y + 5) for x, y in line]
        out.append(f'<polyline points="{P(line)}" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.9"/>')
        out.append(streaks(40, seed + 1, (min(p[0] for p in line), min(p[1] for p in line), max(p[0] for p in line), 300), ["#8EA6C8", "#A8BCD8"], w=(1, 3), length=(8, 24), opacity=(0.3, 0.6), slant=0.6))
    # ---- the Matterhorn: east face in morning sun (left), north face in shade (right), hooked summit
    S = (292, 96)
    left = [S, (284, 104), (270, 132), (258, 152), (246, 166), (240, 172), (226, 196), (204, 228), (182, 256), (150, 300), (130, 330)]
    ridge = [S, (294, 120), (295, 150), (298, 182), (302, 214), (306, 248), (314, 290), (318, 330)]
    right = [S, (302, 98), (310, 110), (318, 130), (330, 162), (346, 196), (360, 212), (380, 234), (414, 266), (460, 300), (500, 330)]
    east = left + ridge[::-1][:-1]
    north = ridge + right[::-1][1:-1]
    out.append(f'<clipPath id="{u}-ef"><polygon points="{P(east)}"/></clipPath><clipPath id="{u}-nf"><polygon points="{P(north)}"/></clipPath>')
    out.append(Q(east, f"url(#{u}-east)"))
    out.append(Q(north, f"url(#{u}-north)"))
    rnd = random.Random(21)

    def ledges(n, seed, box, ang, cols, w=(14, 46), th=(1.6, 4.2), op=(0.6, 1)):
        """Snow lying on sloping rock ledges: thin tapered strokes at the strata angle."""
        r_ = random.Random(seed)
        x0, y0, x1, y1 = box
        res = []
        for _ in range(n):
            x, y = r_.uniform(x0, x1), r_.uniform(y0, y1)
            L = r_.uniform(*w)
            t = r_.uniform(*th)
            dx, dy = L * math.cos(math.radians(ang)), L * math.sin(math.radians(ang))
            res.append(f'<path d="M {x:.1f} {y:.1f} q {dx * 0.5:.1f} {dy * 0.5 - t:.1f} {dx:.1f} {dy:.1f} q {-dx * 0.45:.1f} {-dy * 0.45 + t * 1.6:.1f} {-dx:.1f} {-dy:.1f} Z" fill="{r_.choice(cols)}" opacity="{r_.uniform(*op):.2f}"/>')
        return "".join(res)

    def gullies(n, seed, box, cols, op=(0.3, 0.6)):
        r_ = random.Random(seed)
        x0, y0, x1, y1 = box
        res = []
        for _ in range(n):
            x, y = r_.uniform(x0, x1), r_.uniform(y0, y1)
            L = r_.uniform(20, 60)
            res.append(f'<path d="M {x:.1f} {y:.1f} q {r_.uniform(-6, 6):.1f} {L / 2:.1f} {r_.uniform(-14, -4):.1f} {L:.1f}" fill="none" stroke="{r_.choice(cols)}" stroke-width="{r_.uniform(1.5, 3.5):.1f}" stroke-linecap="round" opacity="{r_.uniform(*op):.2f}"/>')
        return "".join(res)

    out.append(f'<g clip-path="url(#{u}-ef)">'
               + gullies(40, 30, (150, 110, 330, 320), ["#6A4E58", "#8A6A6A"])
               + blobs(40, 31, (150, 110, 330, 320), ["#7A5E66", "#D8B498"], r=(6, 16), opacity=(0.15, 0.35), squash=0.5)
               + ledges(110, 32, (140, 104, 336, 320), 160, ["#FFF8F0", "#FCEEE2", "#F8E4D4"], w=(12, 46), th=(2, 5))
               + ledges(30, 37, (230, 100, 310, 180), 160, ["#FFFFFF", "#FFF4E8"], w=(10, 30), th=(2.4, 5))
               + ledges(40, 33, (150, 140, 336, 320), 160, ["#7A5A60"], w=(14, 40), th=(0.8, 1.6), op=(0.4, 0.7))
               + f'<polygon points="{P([(294, 120), (295, 150), (298, 182), (302, 214), (306, 248), (314, 290), (318, 330), (296, 330), (286, 250), (284, 180)])}" fill="#5A4A60" opacity="0.2"/>'
               + "</g>")
    out.append(f'<g clip-path="url(#{u}-nf)">'
               + gullies(30, 34, (300, 110, 500, 330), ["#2A3454", "#36405E"])
               + ledges(110, 36, (290, 104, 490, 330), 25, ["#DCE6F4", "#C8D6EC", "#EEF2FA"], w=(10, 40), th=(2, 4.6))
               + "</g>")
    # Hörnli ridge catching the light, the shoulder, and the summit glowing
    out.append(f'<polyline points="{P(ridge)}" fill="none" stroke="#FFF2DE" stroke-width="2.4" stroke-linejoin="round" opacity="0.9"/>')
    out.append(f'<polyline points="{P(left[:8])}" fill="none" stroke="#FFE8C8" stroke-width="2" stroke-linejoin="round" opacity="0.85"/>')
    out.append('<path d="M 286 104 L 292 96 L 300 98 L 296 108 Z" fill="#FFF8EE"/>')
    # banner cloud streaming off the summit
    out.append(mist(334, 104, 44, 9, "#FFFFFF", f"{u}-ban", 0.8) + mist(372, 110, 34, 6, "#FFFFFF", f"{u}-ban2", 0.55))
    # glacier and haze over the valley at the foot
    gl = rough([(110, 312), (170, 296), (240, 300), (300, 292), (360, 298), (430, 290), (520, 300)], 41, amp=5, depth=3)
    out.append(Q(gl + [(520, 330), (110, 330)], "#E8F2FA"))
    out.append(f'<rect x="0" y="260" width="600" height="80" fill="url(#{u}-haze)"/>')
    # ---- midground: larch and spruce wood on the slope below
    poly, mg = ridge_poly([(-10, 318), (120, 308), (260, 316), (400, 304), (610, 312)], 51, amp=6, fill="#4E7A46")
    out.append(poly)
    out.append(tree_line(mg, 52, ["#2E5A3A", "#3A6A42", "#24502E"], density=2.2, hmin=14, hmax=30, sink=6))
    out.append(tree_line(mg, 53, ["#C8A43A", "#B89436"], density=0.25, hmin=12, hmax=22, sink=6))
    # the meadow the train climbs across
    out.append(f'<path d="M -10 336 C 140 322 300 330 420 322 C 500 318 560 320 610 316 L 610 444 L -10 444 Z" fill="url(#{u}-meadow)"/>')
    out.append(grass(140, 61, (-10, 330, 610, 380), ["#A8D06A", "#6E9E44", "#C8E080"], h=(3, 7), sw=1.3))
    out.append(conifer(60, 352, 50, "#2A5434", 1, light="#7AA65A") + conifer(84, 354, 36, "#24502E", 2, light="#7AA65A") + conifer(560, 336, 44, "#2A5434", 3, light="#7AA65A"))
    # rack railway with catenary, and the red train climbing towards the summit station
    t0, t1 = (-10, 386), (610, 326)
    sl = (t1[1] - t0[1]) / (t1[0] - t0[0])
    ty = lambda x: t0[1] + (x - t0[0]) * sl
    out.append(f'<path d="M {t0[0]} {t0[1] + 4} L {t1[0]} {t1[1] + 4} L {t1[0]} {t1[1] - 1} L {t0[0]} {t0[1] - 1} Z" fill="#8A7A6A"/>')
    out.append(f'<line x1="{t0[0]}" y1="{t0[1]:.1f}" x2="{t1[0]}" y2="{t1[1]:.1f}" stroke="#4A3E3A" stroke-width="1.6"/>')
    out.append('<g stroke="#5A5054" stroke-width="1.2">' + "".join(f'<line x1="{x}" y1="{ty(x) - 1:.1f}" x2="{x - 2}" y2="{ty(x) + 4:.1f}"/>' for x in range(0, 600, 7)) + "</g>")
    for x in (30, 150, 390, 510):
        out.append(f'<line x1="{x}" y1="{ty(x):.1f}" x2="{x}" y2="{ty(x) - 40:.1f}" stroke="#4A4A52" stroke-width="2"/><line x1="{x}" y1="{ty(x) - 36:.1f}" x2="{x + 12}" y2="{ty(x) - 37:.1f}" stroke="#4A4A52" stroke-width="1.6"/>')
    out.append(f'<line x1="-10" y1="{ty(-10) - 36:.1f}" x2="610" y2="{ty(610) - 36:.1f}" stroke="#3A3A44" stroke-width="1.1"/>')
    ang = math.degrees(math.atan(sl))
    tx = 210
    train = [f'<g transform="translate({tx} {ty(tx) - 2:.1f}) rotate({ang:.2f})">']
    for c in range(2):
        x0 = c * 76
        train.append(f'<rect x="{x0}" y="-30" width="73" height="27" rx="4" fill="url(#{u}-train)"/>'
                     f'<rect x="{x0}" y="-30" width="73" height="4" rx="2" fill="#F2F0EC"/>'
                     f'<rect x="{x0 + 2}" y="-24" width="69" height="10" rx="2" fill="#2A3A4E"/>'
                     + "".join(f'<rect x="{x0 + 4 + j * 11:.1f}" y="-23" width="9" height="8" rx="1.5" fill="#BCD8EE"/><rect x="{x0 + 4 + j * 11:.1f}" y="-23" width="4" height="8" rx="1" fill="#E8F4FC" opacity="0.8"/>' for j in range(6))
                     + f'<rect x="{x0}" y="-11" width="73" height="2.4" fill="#F2F0EC"/>'
                     f'<rect x="{x0 + 8}" y="-4" width="14" height="4" rx="2" fill="#2A2A30"/><rect x="{x0 + 51}" y="-4" width="14" height="4" rx="2" fill="#2A2A30"/>'
                     f'<rect x="{x0}" y="-30" width="73" height="27" rx="4" fill="#000" opacity="0" />'
                     f'<rect x="{x0 + 66}" y="-30" width="7" height="27" rx="3" fill="#7A1218" opacity="0.5"/>')
    train.append('<rect x="148" y="-26" width="4" height="18" rx="1.5" fill="#BCD8EE"/><circle cx="150" cy="-6" r="1.8" fill="#FFF6D8"/>'
                 '<path d="M 100 -30 L 108 -38 L 116 -30 M 104 -34 L 112 -34" fill="none" stroke="#2A2A30" stroke-width="1.4"/>'
                 '<path d="M 24 -30 L 32 -38 L 40 -30" fill="none" stroke="#2A2A30" stroke-width="1.4"/>'
                 '<rect x="0" y="-33" width="150" height="3" rx="1.5" fill="#E8E4E0"/></g>')
    out.append("".join(train))
    # ---- the chalet: Valais larch wood darkened by the sun, stone base, slate roof, geraniums
    out.append(f'<path d="M 330 444 C 360 400 420 386 520 384 C 560 384 590 388 610 392 L 610 444 Z" fill="url(#{u}-fore)"/>')
    fx0, fx1, top = 358, 474, 246
    mx = (fx0 + fx1) / 2
    # side wall in shade
    out.append(Q([(fx1, 304), (522, 290), (522, 404), (fx1, 414)], "#4A2A20"))
    out.append(Q([(fx1, 384), (522, 376), (522, 404), (fx1, 414)], "#8A8690"))
    out.append('<g stroke="#2E1A14" stroke-width="1.2" opacity="0.8">' + "".join(f'<line x1="{fx1}" y1="{y}" x2="522" y2="{y - 13:.1f}"/>' for y in range(312, 384, 7)) + "</g>")
    out.append(Q([(486, 322), (498, 318), (498, 340), (486, 343)], "#1E1E2A") + Q([(486, 322), (492, 320), (492, 342), (486, 343)], "#3A4A5E"))
    # front gable facade (lit)
    out.append(Q([(fx0, 414), (fx0, 300), (mx, 262), (fx1, 300), (fx1, 414)], f"url(#{u}-wood)"))
    out.append(Q([(fx0, 380), (fx1, 380), (fx1, 414), (fx0, 414)], "#C8C2BC"))
    out.append(blobs(26, 5, (fx0, 382, fx1, 412), ["#9A949C", "#E2DCD4", "#8A8490"], r=(3, 7), opacity=(0.4, 0.8), squash=0.6))
    out.append('<g stroke="#3A1E14" stroke-width="1.1" opacity="0.75">' + "".join(f'<line x1="{fx0}" y1="{y}" x2="{fx1}" y2="{y}"/>' for y in range(306, 380, 6)) + "</g>")
    out.append('<g stroke="#3A1E14" stroke-width="1.1" opacity="0.75">' + "".join(
        f'<line x1="{mx - (y - 262) * (mx - fx0) / 38:.1f}" y1="{y}" x2="{mx + (y - 262) * (mx - fx0) / 38:.1f}" y2="{y}"/>' for y in range(270, 300, 6)) + "</g>")
    out.append(Q([(fx0, 300), (mx, 262), (mx + 6, 266), (fx0 + 6, 304)], "#FFD9A8", ' opacity="0.25"'))
    # windows with white frames and red-and-white shutters
    for wx, wy in ((374, 352), (438, 352), (406, 284)):
        out.append(f'<rect x="{wx - 2}" y="{wy - 2}" width="24" height="22" fill="#F4EEE4"/><rect x="{wx}" y="{wy}" width="20" height="18" fill="#2A3448"/>'
                   f'<rect x="{wx}" y="{wy}" width="9" height="8" fill="#9AB8D4" opacity="0.7"/><line x1="{wx + 10}" y1="{wy}" x2="{wx + 10}" y2="{wy + 18}" stroke="#F4EEE4" stroke-width="1.6"/>'
                   f'<line x1="{wx}" y1="{wy + 9}" x2="{wx + 20}" y2="{wy + 9}" stroke="#F4EEE4" stroke-width="1.6"/>')
        if wy > 300:
            for sx in (wx - 10, wx + 22):
                out.append(f'<rect x="{sx}" y="{wy - 2}" width="8" height="22" fill="#C8303A"/><path d="M {sx} {wy - 2} L {sx + 8} {wy + 20} M {sx + 8} {wy - 2} L {sx} {wy + 20}" stroke="#F4EEE4" stroke-width="1.6"/>')
    # carved balcony across the gable with geranium boxes
    out.append(f'<rect x="{fx0 - 6}" y="318" width="{fx1 - fx0 + 12}" height="4" fill="#3A1E14"/>')
    out.append(f'<rect x="{fx0 - 6}" y="322" width="{fx1 - fx0 + 12}" height="18" fill="#7A4028"/>')
    out.append("".join(f'<rect x="{x}" y="324" width="5" height="14" fill="#5A2E1E"/><circle cx="{x + 2.5}" cy="330" r="1.4" fill="#2A140C"/>' for x in range(fx0 - 2, fx1 + 4, 8)))
    out.append(f'<rect x="{fx0 - 8}" y="338" width="{fx1 - fx0 + 16}" height="4" fill="#3A1E14"/>')
    out.append(f'<rect x="{fx0 - 4}" y="310" width="{fx1 - fx0 + 8}" height="9" rx="2" fill="#6A3A22"/>')
    out.append(blobs(44, 61, (fx0 - 4, 300, fx1 + 4, 314), ["#3E7A32", "#2E6A2A", "#5A9A3E"], r=(2.4, 4.4), opacity=(0.9, 1)))
    out.append(flowers(70, 62, (fx0 - 4, 298, fx1 + 4, 316), ["#E8283A", "#F0404E", "#C81E30", "#FF6A72"], r=(1.6, 2.6)))
    for wx in (374, 438):
        out.append(f'<rect x="{wx - 4}" y="372" width="28" height="6" rx="1.5" fill="#6A3A22"/>'
                   + blobs(14, wx, (wx - 4, 366, wx + 24, 374), ["#3E7A32", "#5A9A3E"], r=(2, 3.4), opacity=(0.9, 1))
                   + flowers(20, wx + 1, (wx - 4, 364, wx + 24, 373), ["#E8283A", "#F0404E", "#FF6A72"], r=(1.5, 2.4)))
    # stone-slab roof with deep overhang
    out.append(Q([(mx, 244), (506, 230), (538, 296), (fx1 + 18, 312)], f"url(#{u}-roof)"))
    out.append('<g stroke="#4A4A56" stroke-width="1.2" opacity="0.7">' + "".join(f'<line x1="{mx + (fx1 + 18 - mx) * t:.1f}" y1="{244 + 68 * t:.1f}" x2="{506 + 32 * t:.1f}" y2="{230 + 66 * t:.1f}"/>' for t in (0.2, 0.4, 0.6, 0.8)) + "</g>")
    out.append(Q([(fx0 - 18, 312), (mx, 244), (fx1 + 18, 312), (fx1 + 14, 314), (mx, 252), (fx0 - 14, 314)], "#3A2A26"))
    out.append(f'<polyline points="{P([(fx0 - 18, 312), (mx, 244)])}" stroke="#E8E4E8" stroke-width="2.2" fill="none"/>')
    out.append(f'<rect x="{mx + 32}" y="222" width="10" height="20" fill="#B4AEB0"/><rect x="{mx + 30}" y="219" width="14" height="4" fill="#6E6A74"/>')
    out.append(f'<path d="M {mx + 37} 216 q -4 -10 4 -18 q 6 -8 0 -16" fill="none" stroke="#FFFFFF" stroke-width="3" opacity="0.5" stroke-linecap="round"/>')
    # Swiss flag on a pole beside the chalet
    out.append('<line x1="342" y1="418" x2="342" y2="300" stroke="#E8E4E0" stroke-width="2.4"/><rect x="343" y="300" width="26" height="26" fill="#D8202A"/>'
               '<rect x="353" y="305" width="6" height="16" fill="#FFFFFF"/><rect x="348" y="310" width="16" height="6" fill="#FFFFFF"/>')
    # wooden fence and the flowered meadow in front
    out.append(f'<path d="M -10 410 C 120 396 260 404 380 418 L 380 444 L -10 444 Z" fill="url(#{u}-fore)"/>')
    for i, x in enumerate(range(20, 330, 34)):
        y = 402 + (x - 20) * 0.02
        out.append(f'<rect x="{x}" y="{y - 26:.1f}" width="5" height="30" fill="#7A5A3E"/><rect x="{x}" y="{y - 26:.1f}" width="2" height="30" fill="#B48A5E"/>')
    out.append('<path d="M 14 384 L 340 390" stroke="#8A6A48" stroke-width="3.4"/><path d="M 14 396 L 340 402" stroke="#8A6A48" stroke-width="3.4"/>'
               '<path d="M 14 383 L 340 389" stroke="#C89A6A" stroke-width="1"/>')
    out.append(grass(220, 71, (-10, 400, 610, 444), ["#9ACC5A", "#5E9A3E", "#C8E07A", "#3E7A2E"], h=(5, 14)))
    out.append(flowers(150, 72, (-10, 404, 610, 444), ["#FFFFFF", "#F6E04A", "#B07AE0", "#E85A8A", "#FFFFFF", "#7AA8F0"], r=(1.3, 2.8)))
    out.append(gulls([(170, 200, 10), (190, 210, 7)], "#2A3A5A", 1.7))
    return "\n".join(out)


# ================================================================ ICELAND — aurora over the little black church at Búðir, winter night
def aurora(u, k, curve, seed, height=(60, 140), width=2.6, step=2.2, grad=None, op=(0.25, 0.75), edge="#B8FFD8"):
    """Aurora curtain: vertical rays rising from a wavy lower edge, fading upward, with a bright hem."""
    rnd = random.Random(seed)
    rays = []
    x0, x1 = curve[0][0], curve[-1][0]
    x = x0
    while x < x1:
        y = y_on(curve, x)
        if y is None:
            x += step
            continue
        t = (x - x0) / (x1 - x0)
        env = math.sin(math.pi * t) ** 0.6
        h = rnd.uniform(*height) * (0.55 + 0.45 * env) * (0.7 + 0.3 * math.sin(x / 23 + seed))
        rays.append(f'<rect x="{x:.1f}" y="{y - h:.1f}" width="{width * rnd.uniform(0.7, 1.4):.1f}" height="{h + 3:.1f}" opacity="{rnd.uniform(*op) * (0.5 + 0.5 * env):.2f}"/>')
        x += step * rnd.uniform(0.6, 1.3)
    return (f'<g fill="url(#{grad})">' + "".join(rays) + "</g>"
            + f'<polyline points="{P(curve)}" fill="none" stroke="#7CF8B8" stroke-width="7" opacity="0.18" stroke-linecap="round"/>'
            + f'<polyline points="{P(curve)}" fill="none" stroke="{edge}" stroke-width="2" opacity="0.55" stroke-linecap="round"/>')


def iceland():
    u = "is"
    out = [defs(
        lg(f"{u}-sky", [(0, "#060A1E"), (0.4, "#0C1A3A"), (0.75, "#123A52"), (1, "#1E5A62")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-ray", [(0, "#8CFFC4", 0.95), (0.25, "#3EE89A", 0.7), (0.6, "#2AB89A", 0.35), (0.85, "#8A5AC8", 0.25), (1, "#B05AD0", 0)], 0, 1, 0, 0),
        lg(f"{u}-ray2", [(0, "#C8FFE0", 0.9), (0.3, "#52F0A8", 0.6), (0.75, "#3A9AB0", 0.2), (1, "#3A9AB0", 0)], 0, 1, 0, 0),
        lg(f"{u}-mtn", [(0, "#E4F4F2"), (0.6, "#A8C4D0"), (1, "#7A98B0")]),
        lg(f"{u}-mtn2", [(0, "#C8DEE4"), (1, "#8AA6BC")]),
        lg(f"{u}-snow", [(0, "#BCD8DC"), (0.5, "#9AB8C8"), (1, "#6A88A4")], 0, 330, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-lag", [(0, "#2A7A6A"), (1, "#0E2A3A")]),
        lg(f"{u}-wall", [(0, "#1E2230"), (1, "#0C0E16")], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(160, 2, (0, 40, 600, 280), "#F2F6FF", r=(0.5, 1.4), opacity=(0.3, 1)))
    for x, y in ((90, 76), (488, 66), (548, 160), (214, 58), (40, 190)):
        out.append(f'<circle cx="{x}" cy="{y}" r="1.9" fill="#FFFFFF"/><path d="M {x - 5} {y} L {x + 5} {y} M {x} {y - 5} L {x} {y + 5}" stroke="#FFFFFF" stroke-width="0.8" opacity="0.6"/>')
    # aurora: a broad sweeping curtain and a fainter fold behind it
    c1 = rough([(-20, 236), (60, 200), (150, 172), (240, 190), (330, 160), (420, 128), (500, 140), (620, 112)], 4, amp=12, depth=4)
    c2 = rough([(-20, 150), (90, 130), (200, 112), (300, 128), (380, 100), (470, 92), (620, 86)], 8, amp=10, depth=4)
    c3 = rough([(120, 262), (220, 236), (300, 248), (380, 222), (470, 236), (560, 206)], 12, amp=8, depth=3)
    out.append(glow(320, 190, 300, "#2EE89A", f"{u}-ag", 0.22))
    out.append(aurora(u, 2, c2, 21, height=(40, 90), width=2.2, step=3, grad=f"{u}-ray2", op=(0.15, 0.45)))
    out.append(aurora(u, 1, c1, 22, height=(70, 160), width=2.6, step=2, grad=f"{u}-ray", op=(0.25, 0.8)))
    out.append(aurora(u, 3, c3, 23, height=(30, 80), width=2.2, step=2.4, grad=f"{u}-ray2", op=(0.2, 0.6)))
    # snowy mountains behind: the glacier dome far right, craggy ridges left
    poly, gl = ridge_poly([(330, 300), (400, 278), (460, 262), (510, 258), (560, 266), (620, 290)], 31, amp=4, depth=3, fill=f"url(#{u}-mtn2)")
    out.append(poly)
    out.append(f'<polyline points="{P(gl)}" fill="none" stroke="#D8FFF0" stroke-width="1.6" opacity="0.7"/>')
    m1 = [(-20, 300), (20, 262), (54, 246), (80, 226), (104, 214), (128, 230), (150, 222), (176, 240), (200, 236), (236, 262), (270, 276), (320, 300), (360, 316)]
    poly, ml = ridge_poly(m1, 33, amp=8, depth=4, fill=f"url(#{u}-mtn)")
    out.append(f'<clipPath id="{u}-mc"><polygon points="{P(ml + [(360, 340), (-20, 340)])}"/></clipPath>')
    out.append(poly)
    out.append(f'<g clip-path="url(#{u}-mc)">'
               + streaks(150, 34, (-20, 210, 360, 330), ["#3A4E6A", "#5A6E8A", "#4A5E7A"], w=(0.8, 2.2), length=(8, 30), opacity=(0.3, 0.7), slant=0.25)
               + f'<polygon points="{P([(104, 214), (128, 230), (150, 222), (176, 240), (200, 236), (236, 262), (270, 276), (320, 300), (360, 316), (360, 340), (120, 340)])}" fill="#4A6A8A" opacity="0.25"/>'
               + "</g>")
    out.append(f'<polyline points="{P(ml[:len(ml) // 2])}" fill="none" stroke="#C8FFE4" stroke-width="1.8" opacity="0.6"/>')
    # lagoon catching the aurora
    out.append(f'<path d="M -10 322 C 120 316 260 322 420 314 C 500 310 560 314 610 312 L 610 340 C 400 344 200 342 -10 346 Z" fill="url(#{u}-lag)"/>')
    out.append(water_lines(60, 41, (0, 318, 600, 340), ["#8CFFC4", "#3EE89A", "#C8FFE0"], w=(8, 40), h=(0.8, 1.6), opacity=(0.3, 0.8), grow=False))
    # snowfield with mossy lava humps poking through
    out.append(f'<path d="M -10 336 C 140 330 300 338 450 330 C 520 326 570 330 610 328 L 610 444 L -10 444 Z" fill="url(#{u}-snow)"/>')
    rnd = random.Random(51)
    for i in range(26):
        x = rnd.uniform(-10, 610)
        y = rnd.uniform(342, 420)
        w = rnd.uniform(10, 30) * (0.6 + (y - 340) / 120)
        out.append(f'<path d="M {x - w:.1f} {y:.1f} Q {x - w * 0.4:.1f} {y - w * 0.45:.1f} {x:.1f} {y - w * 0.3:.1f} Q {x + w * 0.5:.1f} {y - w * 0.5:.1f} {x + w:.1f} {y:.1f} Z" fill="#3A4A44"/>'
                   f'<path d="M {x - w * 0.8:.1f} {y - w * 0.12:.1f} Q {x - w * 0.3:.1f} {y - w * 0.5:.1f} {x + w * 0.2:.1f} {y - w * 0.36:.1f} Q {x - w * 0.2:.1f} {y - w * 0.2:.1f} {x - w * 0.8:.1f} {y - w * 0.12:.1f} Z" fill="#E4F4F4" opacity="0.85"/>')
    out.append(grass(120, 52, (-10, 350, 610, 444), ["#8A9A6A", "#6A7A5A", "#B4B48A"], h=(4, 12), sw=1.3))
    out.append(mist(330, 352, 320, 26, "#5CF0A8", f"{u}-sg", 0.16))
    # snow sparkle
    out.append(dots(120, 53, (-10, 340, 610, 444), "#FFFFFF", r=(0.5, 1.2), opacity=(0.4, 1)))
    # ---- the black church: tarred timber, white window frames, little belfry
    out.append(mist(318, 380, 170, 30, "#0A1424", f"{u}-sh", 0.35))
    out.append('<g transform="translate(320 396) scale(1.32) translate(-320 -396)">')
    fx0, fx1, base = 250, 286, 376
    out.append(Q([(286, 334), (398, 338), (398, 374), (286, 376)], f"url(#{u}-wall)"))
    out.append('<g stroke="#2A3040" stroke-width="1" opacity="0.8">' + "".join(f'<line x1="{x}" y1="{334 + (x - 286) * 0.036:.1f}" x2="{x}" y2="{376 - (x - 286) * 0.018:.1f}"/>' for x in range(290, 398, 5)) + "</g>")
    for wx in (304, 334, 364):
        wy = 344 + (wx - 286) * 0.03
        out.append(f'<rect x="{wx - 1.6}" y="{wy - 1.6:.1f}" width="15.2" height="19.2" fill="#F2F4F6"/><rect x="{wx}" y="{wy:.1f}" width="12" height="16" fill="#1E2A3A"/>'
                   f'<path d="M {wx + 6} {wy:.1f} L {wx + 6} {wy + 16:.1f} M {wx} {wy + 5.3:.1f} L {wx + 12} {wy + 5.3:.1f} M {wx} {wy + 10.6:.1f} L {wx + 12} {wy + 10.6:.1f}" stroke="#F2F4F6" stroke-width="1.4"/>')
    out.append('<rect x="335.4" y="346.5" width="4.6" height="4.4" fill="#FFC870" opacity="0.85"/><rect x="341.4" y="352" width="4.6" height="4.4" fill="#FFC870" opacity="0.7"/>')
    out.append(glow(340, 352, 24, "#FFC870", f"{u}-wg", 0.35))
    # roof (black) with a dusting of snow on the ridge and eaves
    out.append(Q([(266, 306), (392, 312), (402, 338), (286, 334)], "#0E1018"))
    out.append(f'<path d="M 266 306 L 392 312 L 393 315 L 266 310 Z" fill="#E8F6F4"/>')
    out.append(f'<path d="M 286 334 L 402 338 L 402 340 L 286 336 Z" fill="#C8DEE4" opacity="0.8"/>')
    # front gable with the white door
    out.append(Q([(fx0 - 6, base), (fx0 - 6, 334), (268, 304), (fx1 + 2, 334), (fx1 + 2, base)], "#181C28"))
    out.append(Q([(fx0 - 9, 336), (268, 302), (fx1 + 5, 336), (fx1 + 2, 338), (268, 307), (fx0 - 6, 338)], "#0A0C12"))
    out.append('<g stroke="#2E3446" stroke-width="1" opacity="0.8">' + "".join(f'<line x1="{x}" y1="{max(334 - (min(x, 536 - x) - 244) * 1.18, 306):.1f}" x2="{x}" y2="{base}"/>' for x in range(248, 288, 5)) + "</g>")
    out.append(f'<rect x="259" y="350" width="18" height="26" fill="#F2F4F6"/><rect x="261.5" y="352.5" width="13" height="23.5" fill="#E2E6EA"/><line x1="268" y1="352" x2="268" y2="376" stroke="#B8C0C8" stroke-width="1.2"/>')
    out.append(f'<rect x="262" y="320" width="12" height="14" fill="#F2F4F6"/><rect x="264" y="322" width="8" height="10" fill="#1E2A3A"/><line x1="268" y1="322" x2="268" y2="332" stroke="#F2F4F6" stroke-width="1.2"/>')
    # belfry with pyramid cap and cross
    out.append(Q([(258, 306), (258, 288), (280, 289), (280, 307)], "#181C28"))
    out.append(Q([(280, 289), (288, 290), (288, 309), (280, 307)], "#0A0C12"))
    out.append(f'<rect x="263" y="292" width="10" height="9" fill="#F2F4F6"/><rect x="265" y="294" width="6" height="7" fill="#0E1018"/>')
    out.append(Q([(256, 289), (271, 270), (290, 290)], "#0E1018") + '<path d="M 256 289 L 271 270" stroke="#D8F0EC" stroke-width="1.4"/>')
    out.append('<path d="M 271 270 L 271 258 M 267 263 L 275 263" stroke="#F2F4F6" stroke-width="1.6"/>')
    # aurora rim on the roof edges
    out.append('<path d="M 258 289 L 271 270" stroke="#7CF8B8" stroke-width="1.2" opacity="0.7"/><path d="M 244 334 L 268 304" stroke="#7CF8B8" stroke-width="1.4" opacity="0.6"/>')
    # churchyard: low dry-stone wall with snow, black lychgate, a few crosses
    wall = rough([(200, 392), (260, 386), (330, 390), (400, 386), (440, 392)], 71, amp=2, depth=3)
    out.append(Q(wall + [(440, 400), (200, 400)], "#2A2E3A"))
    out.append(blobs(40, 72, (200, 386, 440, 400), ["#3A4050", "#1A1E28", "#4A5262"], r=(2, 4.5), opacity=(0.7, 1), squash=0.7))
    out.append(f'<polyline points="{P(wall)}" fill="none" stroke="#E8F6F4" stroke-width="3.2" stroke-linecap="round"/>')
    gx = 318
    out.append(f'<rect x="{gx - 14}" y="370" width="4" height="30" fill="#0E1018"/><rect x="{gx + 10}" y="370" width="4" height="30" fill="#0E1018"/>'
               f'<path d="M {gx - 19} 372 L {gx} 360 L {gx + 19} 372 Z" fill="#0E1018"/><path d="M {gx - 19} 372 L {gx} 360 L {gx + 19} 372" fill="none" stroke="#E8F6F4" stroke-width="2"/>'
               f'<g stroke="#2A2E3A" stroke-width="1.6">' + "".join(f'<line x1="{gx - 10 + i * 4}" y1="384" x2="{gx - 10 + i * 4}" y2="398"/>' for i in range(6)) + f'</g><line x1="{gx - 10}" y1="386" x2="{gx + 10}" y2="386" stroke="#2A2E3A" stroke-width="1.6"/>')
    for cx_, cy_ in ((222, 382), (238, 380), (410, 380), (424, 382)):
        out.append(f'<path d="M {cx_} {cy_} L {cx_} {cy_ - 12} M {cx_ - 4} {cy_ - 8} L {cx_ + 4} {cy_ - 8}" stroke="#F2F4F6" stroke-width="2"/>')
    out.append("</g>")
    # footprints in the snow leading to the gate
    fp = []
    for i in range(14):
        t = i / 13
        x = 300 + 18 * math.sin(t * 3) + (1 - t) * 40 + (3 if i % 2 else -3)
        y = 440 - t * 38
        fp.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{2.6 - t:.1f}" ry="{1.4 - t * 0.5:.1f}" fill="#5A7894" opacity="0.8"/>')
    out.append("".join(fp))
    return "\n".join(out)


# ================================================================ NORWAY — a steep fjord on a still summer morning
def cabin(x, base, w, h, depth, k, wall="#B8302A", shade="#7A1E1E", trim="#F4EEE4", turf=True, door=True, side=1):
    """Norwegian timber cabin in 3/4 view: lit gable end, shaded long side, grass (turf) roof, white trim."""
    out = []
    gh = w * 0.42
    # long side (going back to the right)
    sx = x + w
    out.append(Q([(sx, base), (sx, base - h), (sx + depth, base - h - depth * 0.22), (sx + depth, base - depth * 0.22)], shade))
    out.append(f'<g stroke="#4A1010" stroke-width="0.9" opacity="0.6">' + "".join(
        f'<line x1="{sx:.1f}" y1="{base - h * j / 6:.1f}" x2="{sx + depth:.1f}" y2="{base - h * j / 6 - depth * 0.22:.1f}"/>' for j in range(1, 6)) + "</g>")
    # gable end
    out.append(Q([(x, base), (x, base - h), (x + w / 2, base - h - gh), (sx, base - h), (sx, base)], wall))
    out.append(f'<g stroke="#7A1A1A" stroke-width="0.9" opacity="0.55">' + "".join(
        f'<line x1="{x + w * j / 7:.1f}" y1="{base:.1f}" x2="{x + w * j / 7:.1f}" y2="{base - h - gh * (1 - abs(j / 7 - 0.5) * 2):.1f}"/>' for j in range(1, 7)) + "</g>")
    out.append(f'<rect x="{x - 1:.1f}" y="{base - 2.5:.1f}" width="{w + depth + 2:.1f}" height="3" fill="#6A6A6E"/>')
    # windows and door with white frames
    ww = w * 0.22
    out.append(f'<rect x="{x + w * 0.5 - ww / 2 - 1.2:.1f}" y="{base - h - gh * 0.55:.1f}" width="{ww + 2.4:.1f}" height="{ww * 1.1 + 2.4:.1f}" fill="{trim}"/>'
               f'<rect x="{x + w * 0.5 - ww / 2:.1f}" y="{base - h - gh * 0.55 + 1.2:.1f}" width="{ww:.1f}" height="{ww * 1.1:.1f}" fill="#2A3A4A"/>')
    if door:
        out.append(f'<rect x="{x + w * 0.18:.1f}" y="{base - h * 0.78:.1f}" width="{w * 0.22:.1f}" height="{h * 0.78 - 2.5:.1f}" fill="{trim}"/>'
                   f'<rect x="{x + w * 0.2:.1f}" y="{base - h * 0.74:.1f}" width="{w * 0.18:.1f}" height="{h * 0.74 - 2.5:.1f}" fill="#8A2420"/>')
        out.append(f'<rect x="{x + w * 0.56:.1f}" y="{base - h * 0.72:.1f}" width="{w * 0.24:.1f}" height="{w * 0.22:.1f}" fill="{trim}"/>'
                   f'<rect x="{x + w * 0.58:.1f}" y="{base - h * 0.72 + 1.2:.1f}" width="{w * 0.2:.1f}" height="{w * 0.22 - 2.4:.1f}" fill="#2A3A4A"/>')
    for j in range(2):
        wx = sx + depth * (0.25 + j * 0.42)
        wy = base - h * 0.66 - depth * 0.22 * (0.25 + j * 0.42)
        out.append(Q([(wx, wy), (wx + depth * 0.18, wy - depth * 0.04), (wx + depth * 0.18, wy + h * 0.3 - depth * 0.04), (wx, wy + h * 0.3)], trim)
                   + Q([(wx + 1, wy + 1), (wx + depth * 0.18 - 1, wy - depth * 0.04 + 1), (wx + depth * 0.18 - 1, wy + h * 0.3 - depth * 0.04 - 1), (wx + 1, wy + h * 0.3 - 1)], "#2A3A4A"))
    # roof: barge boards, then the turf
    ridge0 = (x + w / 2, base - h - gh)
    ridge1 = (x + w / 2 + depth, base - h - gh - depth * 0.22)
    eave0 = (sx + 3, base - h + 2)
    eave1 = (sx + depth + 3, base - h - depth * 0.22 + 2)
    if turf:
        out.append(Q([ridge0, ridge1, eave1, eave0], "#5E7A34"))
        out.append(blobs(int(depth * 0.9), k, (ridge0[0], ridge1[1], eave1[0], eave0[1]), ["#7A9A3E", "#4E6A2A", "#9AB04E"], r=(1.5, 3.2), opacity=(0.7, 1), squash=0.7))
        out.append(Q([ridge0, ridge1, (ridge1[0], ridge1[1] + 3), (ridge0[0], ridge0[1] + 3)], "#A8C05A", ' opacity="0.7"'))
        rnd = random.Random(k)
        out.append("".join(f'<circle cx="{lerp(ridge0[0], eave1[0], rnd.random()):.1f}" cy="{lerp(ridge1[1], eave0[1], rnd.random()):.1f}" r="1.1" fill="{rnd.choice(["#F6E05A", "#FFFFFF", "#E870A0"])}"/>' for _ in range(int(depth / 3))))
    else:
        out.append(Q([ridge0, ridge1, eave1, eave0], "#3A3A44"))
    out.append(f'<polyline points="{P([(x - 3, base - h + 2), ridge0, (sx + 3, base - h + 2)])}" fill="none" stroke="{trim}" stroke-width="2"/>')
    if turf:
        out.append(f'<path d="M {x - 3:.1f} {base - h + 2:.1f} L {ridge0[0]:.1f} {ridge0[1] - 2.5:.1f}" stroke="#6E8A38" stroke-width="2.4"/>')
    return "".join(out)


def birch(x, base, h, seed, lean=0.0):
    rnd = random.Random(seed)
    out = [f'<path d="M {x - 2.4:.1f} {base:.1f} Q {x + lean * h * 0.3:.1f} {base - h * 0.5:.1f} {x + lean * h:.1f} {base - h:.1f} L {x + lean * h + 1.6:.1f} {base - h:.1f} Q {x + 2 + lean * h * 0.3:.1f} {base - h * 0.5:.1f} {x + 2.4:.1f} {base:.1f} Z" fill="#F2EEE6"/>']
    for _ in range(int(h / 6)):
        t = rnd.uniform(0.05, 0.95)
        out.append(f'<rect x="{x + lean * h * t - 2:.1f}" y="{base - h * t:.1f}" width="{rnd.uniform(2, 4):.1f}" height="1.4" fill="#2A2A2A" opacity="0.8"/>')
    out.append(leaf_canopy(f"bi{seed}", x + lean * h, base - h * 0.75, h * 0.28, h * 0.32, seed, "#2E5A2A", "#4E8A3A", "#9AC85A", gold="#D8E07A", light=(1, -1), n=50, r=(0.1, 0.2)))
    return "".join(out)


def norway():
    u = "no"
    out = [defs(
        lg(f"{u}-sky", [(0, "#4A86C2"), (0.45, "#8EBCE0"), (0.8, "#D4E8F0"), (1, "#F2F2E2")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#C8D8E8"), (1, "#9AB4C8")]),
        lg(f"{u}-wl", [(0, "#8AA65E"), (0.5, "#5E8448"), (1, "#3E6438")], 0, 80, 0, 330, units="userSpaceOnUse"),
        lg(f"{u}-wr", [(0, "#4E6A6E"), (1, "#24403E")], 0, 80, 0, 330, units="userSpaceOnUse"),
        lg(f"{u}-ml", [(0, "#9AB88A"), (1, "#6A8E6A")]),
        lg(f"{u}-mr", [(0, "#6E8A90"), (1, "#4A6670")]),
        lg(f"{u}-water", [(0, "#A8CCD4"), (0.25, "#4E8A8E"), (0.7, "#1E5A62"), (1, "#123E48")], 0, 300, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-shore", [(0, "#7AA84A"), (1, "#3E6E32")]),
        lg(f"{u}-hull", [(0, "#F6F6F4"), (1, "#C8D0D8")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(560, 70, 220, "#FFF4D0", f"{u}-sun", 0.7))
    out.append(cumulus(f"{u}-c1", 330, 132, 140, 34, 6, "#FFFFFF", "#EEF2F6", "#B4C4D6", light=1))
    out.append(cumulus(f"{u}-c2", 140, 112, 90, 22, 11, "#FFFFFF", "#EEF2F6", "#B4C4D6", light=1))
    # far mountains at the head of the fjord, snow in the gullies
    poly, fl = ridge_poly([(200, 300), (240, 230), (280, 212), (316, 222), (350, 206), (390, 232), (420, 300)], 3, amp=6, fill=f"url(#{u}-far)")
    out.append(poly)
    out.append(f'<clipPath id="{u}-fc"><polygon points="{P(fl + [(420, 300), (200, 300)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-fc)">' + streaks(50, 4, (210, 206, 410, 270), ["#FFFFFF", "#EEF4FA"], w=(1, 3), length=(6, 20), opacity=(0.6, 1), slant=0.5) + "</g>")
    # middle walls, paler with distance
    poly, ml = ridge_poly([(110, 320), (150, 210), (190, 176), (230, 182), (270, 220), (300, 300)], 7, amp=8, fill=f"url(#{u}-ml)")
    out.append(poly)
    out.append(f'<clipPath id="{u}-mlc"><polygon points="{P(ml + [(300, 320), (110, 320)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-mlc)">' + streaks(60, 8, (110, 176, 300, 320), ["#C8D8B8", "#5E7E5E"], w=(1, 2.6), length=(10, 36), opacity=(0.3, 0.6), slant=0.2) + "</g>")
    poly, mr = ridge_poly([(320, 300), (350, 222), (392, 190), (430, 186), (470, 214), (500, 320)], 9, amp=8, fill=f"url(#{u}-mr)")
    out.append(poly)
    out.append(f'<clipPath id="{u}-mrc"><polygon points="{P(mr + [(500, 320), (320, 320)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-mrc)">' + streaks(60, 10, (320, 186, 500, 320), ["#8AA4AC", "#3A5660"], w=(1, 2.6), length=(10, 36), opacity=(0.3, 0.6), slant=0.2) + "</g>")
    out.append(mist(300, 296, 220, 26, "#F2F6F8", f"{u}-m1", 0.75))
    # near walls: sunlit cliff on the left with the Seven Sisters falls, shaded wall on the right
    lw = [(-20, 80), (30, 92), (70, 104), (110, 128), (150, 170), (180, 220), (206, 280), (230, 330), (-20, 330)]
    rough_l = rough(lw[:-1], 13, amp=10, depth=4)
    out.append(Q(rough_l + [(-20, 330)], f"url(#{u}-wl)"))
    out.append(f'<clipPath id="{u}-lc"><polygon points="{P(rough_l + [(-20, 330)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-lc)">'
               + streaks(140, 14, (-20, 80, 230, 330), ["#3E5A3A", "#A8B88A", "#6A6A5A", "#C8CEA8"], w=(1.2, 3.4), length=(14, 50), opacity=(0.3, 0.7), slant=0.15)
               + blobs(60, 15, (-20, 90, 220, 330), ["#3E6A34", "#5A8A3E", "#2E5230"], r=(3, 8), opacity=(0.5, 0.9), squash=0.6)
               + "</g>")
    # the Seven Sisters: thin white veils down the sunlit face, broken by ledges, spray at the foot
    for k, (x, y0, y1) in enumerate(((84, 150, 300), (97, 136, 300), (110, 158, 302), (122, 146, 302), (138, 182, 304), (152, 170, 304), (168, 214, 306))):
        rnd = random.Random(80 + k)
        pts = [(x + rnd.uniform(-1.2, 1.2) + (j / 12) * 5, y0 + (y1 - y0) * j / 12) for j in range(13)]
        out.append(f'<polyline points="{P(pts)}" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" opacity="0.18"/>')
        segs = [pts[i:i + rnd.randint(3, 5)] for i in range(0, 12, 4)]
        for sg in segs:
            if len(sg) > 1:
                out.append(f'<polyline points="{P(sg)}" fill="none" stroke="#F6FBFC" stroke-width="{rnd.uniform(1.6, 2.4):.1f}" stroke-linecap="round" opacity="0.95"/>')
        out.append(f'<ellipse cx="{x:.1f}" cy="{y0:.1f}" rx="2.4" ry="1.6" fill="#FFFFFF" opacity="0.8"/>')
    out.append(mist(128, 300, 70, 12, "#FFFFFF", f"{u}-spray", 0.8))
    rw = [(620, 60), (570, 76), (530, 100), (496, 134), (466, 180), (440, 236), (420, 290), (404, 332), (620, 332)]
    rough_r = rough(rw[:-1], 17, amp=10, depth=4)
    out.append(Q(rough_r + [(620, 332)], f"url(#{u}-wr)"))
    out.append(f'<clipPath id="{u}-rc"><polygon points="{P(rough_r + [(620, 332)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-rc)">'
               + streaks(140, 18, (400, 60, 620, 332), ["#1E3634", "#6E8A8A", "#2E4A48"], w=(1.2, 3.4), length=(14, 50), opacity=(0.3, 0.7), slant=0.15)
               + blobs(50, 19, (410, 70, 620, 330), ["#2E4E3E", "#3E5E4A"], r=(3, 8), opacity=(0.5, 0.9), squash=0.6) + "</g>")
    out.append(f'<polyline points="{P(rough_r[:len(rough_r) // 2])}" fill="none" stroke="#FFF2C8" stroke-width="2" opacity="0.75"/>')
    out.append(tree_line(rough_l, 20, ["#2E5230", "#3E6236"], density=0.6, hmin=6, hmax=12, xmin=-20, xmax=200, sink=4))
    # the fjord
    out.append(f'<rect x="-10" y="300" width="620" height="144" fill="url(#{u}-water)"/>')
    # mirrored reflections of the walls and mountains in the still water
    out.append(f'<clipPath id="{u}-wc"><rect x="-10" y="300" width="620" height="144"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-wc)"><g transform="matrix(1 0 0 -1 0 600)" opacity="0.45">'
               + Q(fl + [(420, 300), (200, 300)], "#B8CCD8") + Q(ml + [(300, 320), (110, 320)], "#7A9A7A") + Q(mr + [(500, 320), (320, 320)], "#5A7680")
               + Q(rough_l + [(-20, 330)], "#4E7444") + Q(rough_r + [(620, 332)], "#24403E") + "</g></g>")
    for k, (x, y0, y1) in enumerate(((84, 150, 300), (110, 158, 302), (138, 182, 304), (168, 214, 306))):
        out.append(f'<line x1="{x + 4}" y1="302" x2="{x + 4}" y2="{302 + (y1 - y0) * 0.3:.0f}" stroke="#E8F4F4" stroke-width="1.6" opacity="0.35"/>')
    out.append(water_lines(180, 21, (-10, 304, 610, 444), ["#C8E4EA", "#7AAEB4", "#2E6A70", "#F2FAFA"], w=(8, 50), h=(1, 2.2), opacity=(0.3, 0.8)))
    out.append(mist(260, 312, 200, 10, "#F6FAFA", f"{u}-m2", 0.6))
    # the ferry gliding up the fjord, wake fanning out behind it
    fx, fy = 286, 352
    wake = []
    wr = random.Random(23)
    for j in range(22):
        t = j / 21
        for sgn in (-1, 1):
            if wr.random() < 0.3:
                continue
            wake.append(f'<path d="M {fx - 44 - t * 130 + wr.uniform(-4, 4):.1f} {fy + 5 + sgn * (1 + t * 14) + wr.uniform(-1.5, 1.5):.1f} q {-4 - t * 4:.1f} {sgn * -1.2:.1f} {-8 - t * 6:.1f} {sgn * 0.6:.1f}" stroke="#F4FAFA" stroke-width="{2 - t:.1f}" stroke-linecap="round" fill="none" opacity="{0.9 - t * 0.65:.2f}"/>')
    out.append("".join(wake))
    out.append(water_lines(40, 22, (fx - 150, fy - 6, fx - 30, fy + 18), ["#FFFFFF", "#D8EEF0"], w=(6, 18), h=(0.8, 1.6), opacity=(0.4, 0.9), grow=False))
    out.append(f'<path d="M {fx - 54} {fy - 8} L {fx + 52} {fy - 8} L {fx + 62} {fy - 14} L {fx + 58} {fy} Q {fx + 50} {fy + 7} {fx + 40} {fy + 7} L {fx - 50} {fy + 7} Z" fill="#1E2E4E"/>')
    out.append(f'<rect x="{fx - 54}" y="{fy - 9}" width="110" height="3" fill="#C8303A"/>')
    out.append(f'<path d="M {fx - 48} {fy - 9} L {fx - 48} {fy - 22} L {fx + 36} {fy - 22} L {fx + 46} {fy - 9} Z" fill="url(#{u}-hull)"/>')
    out.append(f'<path d="M {fx - 34} {fy - 22} L {fx - 34} {fy - 32} L {fx + 22} {fy - 32} L {fx + 30} {fy - 22} Z" fill="url(#{u}-hull)"/>')
    out.append("".join(f'<rect x="{fx - 44 + i * 7}" y="{fy - 18}" width="5" height="4" rx="1" fill="#2A3A5A"/>' for i in range(12)))
    out.append(f'<rect x="{fx - 30}" y="{fy - 30}" width="52" height="4" fill="#2A3A5A"/>')
    out.append(f'<rect x="{fx - 22}" y="{fy - 42}" width="10" height="11" fill="#1E2E4E"/><rect x="{fx - 22}" y="{fy - 42}" width="10" height="3" fill="#C8303A"/>')
    out.append(f'<path d="M {fx - 17} {fy - 44} q -10 -8 -24 -6 q -10 2 -20 -2" fill="none" stroke="#F4F6F8" stroke-width="4" stroke-linecap="round" opacity="0.5"/>')
    out.append(f'<path d="M {fx + 62} {fy - 14} L {fx + 58} {fy}" stroke="#FFF2C8" stroke-width="1.6"/><path d="M {fx - 48} {fy - 22} L {fx + 36} {fy - 22}" stroke="#FFFFFF" stroke-width="1"/>')
    out.append(f'<rect x="{fx - 54}" y="{fy + 8}" width="112" height="6" fill="#1E2E4E" opacity="0.25"/>')
    # ---- foreground shore: red cabins with turf roofs, a boathouse on the water, jetty, rowing boat, flag
    shore = rough([(300, 444), (340, 404), (380, 384), (440, 372), (520, 364), (610, 356)], 31, amp=4, depth=3)
    out.append(Q(shore + [(610, 444)], f"url(#{u}-shore)"))
    out.append(f'<polyline points="{P(shore)}" fill="none" stroke="#B8D07A" stroke-width="2" opacity="0.7"/>')
    out.append(Q([(328, 444), (350, 412), (380, 398), (380, 404), (354, 418), (340, 444)], "#6A6A62", ' opacity="0.7"'))
    out.append(grass(120, 32, (360, 380, 610, 444), ["#A8C86A", "#5E8A3E", "#C8DC8A"], h=(4, 10)))
    out.append(cabin(456, 378, 34, 22, 40, 41))
    out.append(cabin(392, 404, 40, 26, 46, 42))
    # boathouse on stilts over the water with the jetty
    out.append('<g fill="#4A3A30">' + "".join(f'<rect x="{x}" y="398" width="3" height="20"/>' for x in (338, 352, 366)) + "</g>")
    out.append(Q([(300, 404), (372, 402), (372, 406), (300, 408)], "#7A5A40"))
    out.append('<g fill="#4A3A30">' + "".join(f'<rect x="{x}" y="406" width="2.4" height="12"/>' for x in (306, 324)) + "</g>")
    out.append(Q([(300, 418), (310, 412), (340, 412), (346, 418), (340, 422), (306, 422)], "#E8E2D4") + Q([(302, 418), (344, 418), (340, 422), (306, 422)], "#2E5A8A"))
    out.append('<line x1="312" y1="410" x2="300" y2="406" stroke="#3A2A20" stroke-width="1.2"/>')
    out.append(water_lines(20, 33, (296, 420, 380, 436), ["#2E6A70", "#C8E4EA"], w=(6, 20), h=(1, 1.6), opacity=(0.4, 0.8), grow=False))
    # Norwegian flag
    out.append('<g transform="translate(-14 2)"><line x1="520" y1="370" x2="520" y2="300" stroke="#F2F2F0" stroke-width="2.2"/>'
               '<rect x="521" y="300" width="27" height="19" fill="#C8202E"/><rect x="528" y="300" width="6" height="19" fill="#FFFFFF"/><rect x="521" y="306.5" width="27" height="6" fill="#FFFFFF"/>'
               '<rect x="529.5" y="300" width="3" height="19" fill="#1E2E6A"/><rect x="521" y="308" width="27" height="3" fill="#1E2E6A"/></g>')
    # birches framing the left foreground on a rocky point
    pt = rough([(-20, 400), (30, 392), (80, 400), (120, 420), (150, 444)], 41, amp=4, depth=3)
    out.append(Q(pt + [(-20, 444)], "#4E6E3A"))
    out.append(blobs(30, 42, (-20, 400, 140, 444), ["#6A6A60", "#8A8A7E", "#4A4A44"], r=(4, 10), opacity=(0.7, 1), squash=0.6))
    out.append(birch(46, 404, 120, 43, lean=-0.06) + birch(76, 408, 92, 44, lean=0.05))
    out.append(grass(60, 45, (-20, 404, 140, 444), ["#9AC060", "#5E8A3E"], h=(4, 10)))
    out.append(gulls([(250, 160, 10), (268, 170, 7), (470, 110, 9)], "#2A3A4A", 1.7))
    return "\n".join(out)


# ================================================================ CINQUE TERRE — Manarola's pastel houses on the cliff at sunset
def gozzo(x, y, L, hull, rim="#F6F0E4", flip=False, inner="#8A5A3A", ref=True, sea="#2A6A8A"):
    """Ligurian gozzo: small wooden boat with raised pointed stem, painted hull, pale gunwale."""
    d = -1 if flip else 1
    h = L * 0.22
    pts = f'M {x - d * L / 2:.1f} {y - h * 0.9:.1f} Q {x - d * L * 0.3:.1f} {y + h * 0.35:.1f} {x:.1f} {y + h * 0.3:.1f} Q {x + d * L * 0.32:.1f} {y + h * 0.3:.1f} {x + d * L / 2:.1f} {y - h * 1.15:.1f} Z'
    out = []
    if ref:
        out.append(f'<ellipse cx="{x:.1f}" cy="{y + h * 0.9:.1f}" rx="{L * 0.46:.1f}" ry="{h * 0.6:.1f}" fill="{hull}" opacity="0.35"/>')
    out.append(f'<path d="{pts}" fill="{hull}"/>')
    out.append(f'<path d="M {x - d * L / 2:.1f} {y - h * 0.9:.1f} Q {x:.1f} {y - h * 0.45:.1f} {x + d * L / 2:.1f} {y - h * 1.15:.1f}" fill="none" stroke="{rim}" stroke-width="{max(1.2, h * 0.28):.1f}"/>')
    out.append(f'<path d="M {x - d * L * 0.36:.1f} {y - h * 0.62:.1f} Q {x:.1f} {y - h * 0.3:.1f} {x + d * L * 0.36:.1f} {y - h * 0.75:.1f}" fill="none" stroke="{inner}" stroke-width="{max(1, h * 0.3):.1f}" opacity="0.8"/>')
    out.append(f'<path d="M {x - d * L / 2:.1f} {y - h * 0.4:.1f} Q {x:.1f} {y + h * 0.15:.1f} {x + d * L / 2:.1f} {y - h * 0.5:.1f}" fill="none" stroke="#000" stroke-width="{max(1, h * 0.2):.1f}" opacity="0.18"/>')
    return "".join(out)


def ligurian_house(x, base, w, h, wall, seed, lit_side=True, shade_w=0.0, roof="#6A6672"):
    """Tall narrow Ligurian tower-house: pastel render, green shutters, slate roof, warm sunset light."""
    rnd = random.Random(seed)
    out = [f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{wall}"/>']
    if shade_w:
        out.append(f'<rect x="{x + w:.1f}" y="{base - h + 2:.1f}" width="{shade_w:.1f}" height="{h - 2:.1f}" fill="{mix(wall, "#5A4A7A", 0.45)}"/>')
    out.append(f'<rect x="{x + w * 0.82:.1f}" y="{base - h:.1f}" width="{w * 0.18:.1f}" height="{h:.1f}" fill="#7A5A8A" opacity="0.18"/>')
    floors = max(2, int((h - 6) / 10.5))
    cols = max(1, int(w / 11))
    shutter = rnd.choice(["#3E7A4A", "#2E6A4E", "#4A8A5A", "#3E7A4A"])
    for f_ in range(floors):
        wy = base - h + 6 + f_ * 10.5
        for c in range(cols):
            wx = x + w * (c + 0.5) / cols
            if rnd.random() < 0.12:
                continue
            lit = rnd.random() < 0.18
            out.append(f'<rect x="{wx - 2:.1f}" y="{wy:.1f}" width="4" height="6" fill="{"#FFD27A" if lit else "#3A2E3A"}"/>')
            if rnd.random() < 0.7:
                out.append(f'<rect x="{wx - 4.4:.1f}" y="{wy:.1f}" width="2.2" height="6" fill="{shutter}"/><rect x="{wx + 2.2:.1f}" y="{wy:.1f}" width="2.2" height="6" fill="{shutter}"/>')
            else:
                out.append(f'<rect x="{wx - 2:.1f}" y="{wy:.1f}" width="4" height="6" fill="{shutter}"/>')
    # slate roof: low pitch, seen from slightly below with an eave shadow
    out.append(f'<path d="M {x - 1.5:.1f} {base - h + 0.5:.1f} L {x + w * 0.5:.1f} {base - h - 4:.1f} L {x + w + 1.5:.1f} {base - h + 0.5:.1f} Z" fill="{roof}"/>')
    out.append(f'<rect x="{x - 1.5:.1f}" y="{base - h:.1f}" width="{w + 3:.1f}" height="1.8" fill="#4A3E4A" opacity="0.6"/>')
    if lit_side:
        out.append(f'<rect x="{x:.1f}" y="{base - h:.1f}" width="1.6" height="{h:.1f}" fill="#FFE2B0" opacity="0.55"/>')
    return "".join(out)


def cinque_terre():
    u = "ct"
    out = [defs(
        lg(f"{u}-sky", [(0, "#4E6EAE"), (0.35, "#9A9AC0"), (0.65, "#E8B0A0"), (0.88, "#F8CC92"), (1, "#FBE0A8")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#E8B8A0"), (0.1, "#7A9ABE"), (0.45, "#2E6A92"), (1, "#14405E")], 0, 296, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-hill", [(0, "#8A9A5A"), (0.6, "#5E7A44"), (1, "#3E5A36")], 0, 100, 0, 360, units="userSpaceOnUse"),
        lg(f"{u}-rock", [(0, "#8A6A62"), (0.5, "#6A4E52"), (1, "#3E2E3A")], 0, 300, 0, 420, units="userSpaceOnUse"),
        lg(f"{u}-sunpath", [(0, "#FFE2A8", 0), (0.5, "#FFE8B0", 0.9), (1, "#FFE2A8", 0)], 0, 0, 1, 0),
        lg(f"{u}-near", [(0, "#5A4A4E"), (1, "#2A2028")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(64, 284, 240, "#FFD89A", f"{u}-sun", 0.95))
    out.append('<circle cx="64" cy="284" r="16" fill="#FFF2CC"/>')
    for x, y, w, op in ((150, 150, 110, 0.6), (110, 170, 70, 0.45), (300, 120, 90, 0.4), (240, 196, 60, 0.5)):
        out.append(streak_cloud(x, y, w, "#F4B8A4", op, 4) + streak_cloud(x - 6, y - 2, w * 0.7, "#FFE0C4", op * 0.8, 1.6))
    # Punta Mesco headland far off on the horizon
    out.append(Q(rough([(-10, 296), (40, 290), (110, 286), (160, 292), (190, 296)], 2, amp=2, depth=3) + [(190, 297), (-10, 297)], "#B496A6"))
    # the sea
    out.append(f'<rect x="-10" y="296" width="620" height="148" fill="url(#{u}-sea)"/>')
    out.append(f'<rect x="10" y="296" width="110" height="148" fill="url(#{u}-sunpath)" opacity="0.6"/>')
    out.append(water_lines(150, 3, (-10, 300, 330, 444), ["#FFE8B8", "#F8C890", "#5A8AB4", "#1E5070"], w=(8, 40), h=(1, 2.4), opacity=(0.35, 0.85)))
    out.append(water_lines(60, 4, (20, 298, 110, 330), ["#FFF2D0", "#FFE0A0"], w=(4, 18), h=(0.8, 1.6), opacity=(0.5, 1), grow=False))
    # terraced hillside rising behind the village, vineyards on dry-stone terraces
    hill = rough([(220, 300), (300, 230), (370, 184), (440, 150), (520, 124), (610, 110)], 7, amp=6, depth=4)
    out.append(Q(hill + [(610, 340), (220, 340)], f"url(#{u}-hill)"))
    out.append(f'<clipPath id="{u}-hc"><polygon points="{P(hill + [(610, 340), (220, 340)])}"/></clipPath>')
    ter = []
    rnd = random.Random(9)
    for j in range(16):
        y0 = 132 + j * 13
        pts = [(x, y0 + 0.08 * (x - 300) * (-1) + 5 * math.sin(x / 40 + j)) for x in range(200, 620, 20)]
        ter.append(f'<polyline points="{P(pts)}" fill="none" stroke="#D8C89A" stroke-width="1.4" opacity="0.55"/>')
        ter.append(f'<polyline points="{P([(x, y + 2) for x, y in pts])}" fill="none" stroke="#3E5230" stroke-width="1.2" opacity="0.5"/>')
    out.append(f'<g clip-path="url(#{u}-hc)">' + "".join(ter)
               + dots(500, 10, (230, 110, 610, 330), "#3E5A2E", r=(0.8, 1.8), opacity=(0.5, 0.9))
               + dots(200, 11, (230, 110, 610, 330), "#C8C27A", r=(0.6, 1.4), opacity=(0.4, 0.8))
               + f'<polygon points="{P(hill + [(610, 340), (220, 340)])}" fill="#FFC890" opacity="0.12"/></g>')
    out.append(f'<polyline points="{P(hill)}" fill="none" stroke="#FFD8A0" stroke-width="2" opacity="0.7"/>')
    for i in range(16):
        bx_ = rnd.uniform(300, 600)
        by_ = y_on(hill, bx_) + rnd.uniform(10, 60)
        out.append(leaf_canopy(f"{u}-sh{i}", bx_, by_, rnd.uniform(6, 12), rnd.uniform(5, 8), 300 + i, "#2E4A2A", "#4A6A36", "#9AA858", light=(-1, -1), n=14))
    # rocky spur the village is built on (its seaward cliff faces the sunset)
    rows = [(374 - r * 31, 214 + r * 30, r) for r in range(8)]
    edge = [(184, 404)] + [(xa - 6, base + 4) for base, xa, r in rows] + [(rows[-1][1] + 60, rows[-1][0] + 10), (620, 330)]
    rock = rough(edge, 21, amp=3, depth=2)
    out.append(Q(rock + [(620, 404)], f"url(#{u}-rock)"))
    out.append(f'<clipPath id="{u}-rc"><polygon points="{P(rock + [(620, 404)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-rc)">'
               + "".join(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(14, 40):.1f} {rnd.uniform(-12, -4):.1f}" stroke="{rnd.choice(["#A8847A", "#3A2A34", "#C89A88"])}" stroke-width="{rnd.uniform(1.2, 2.4):.1f}" opacity="0.55"/>' for x, y in [(rnd.uniform(180, 400), rnd.uniform(200, 404)) for _ in range(50)])
               + "</g>")
    out.append(f'<polyline points="{P(rock[:6])}" fill="none" stroke="#FFC890" stroke-width="2.4" opacity="0.8" stroke-linejoin="round"/>')
    # the campanile of San Lorenzo at the top of the village (drawn among the rows)
    campanile = ('<rect x="462" y="124" width="18" height="80" fill="#F2E8D6"/><rect x="473" y="124" width="7" height="80" fill="#BCAAB4"/>'
                 '<path d="M 460 124 L 471 100 L 482 124 Z" fill="#8A8494"/><path d="M 460 124 L 471 100 L 471 124 Z" fill="#C8BCC0"/>'
                 '<path d="M 466 140 L 466 132 Q 469 127 472 132 L 472 140 Z" fill="#3A2E3A"/><line x1="471" y1="100" x2="471" y2="92" stroke="#4A3E4A" stroke-width="1.6"/>'
                 '<line x1="468" y1="95.5" x2="474" y2="95.5" stroke="#4A3E4A" stroke-width="1.4"/><rect x="460" y="122" width="22" height="2.6" fill="#FFF4E2"/>'
                 '<rect x="460" y="148" width="22" height="2" fill="#FFF4E2" opacity="0.8"/><rect x="462" y="124" width="1.8" height="80" fill="#FFE2B0" opacity="0.7"/>')
    # ---- the houses, rows stacked up the spur (back rows first)
    walls = ["#F2C26A", "#E88A6A", "#F4D8A8", "#D8706A", "#F6E2B8", "#E8A87A", "#C8D0B0", "#F0B48A", "#E6C0C0", "#F8D27A", "#D88A7A", "#EED6C0"]
    fronts = []
    for base, xa, r in reversed(rows):
        if r == 5:
            out.append(campanile)
        x = xa + rnd.uniform(-4, 4)
        xb = 616 - max(0, r - 2) * 30
        while x < xb:
            w = rnd.uniform(24, 38)
            h = rnd.uniform(48, 66) if r < 7 else rnd.uniform(32, 42)
            yb = base + rnd.uniform(-3, 4)
            col = mix(rnd.choice(walls), "#C8B0CC", max(0, r - 3) * 0.07)
            out.append(ligurian_house(x, yb, w, h, col, int(x * 7 + r), shade_w=rnd.choice([0, 0, 3, 5])))
            if r == 0:
                fronts.append((x, w, h, col))
            x += w + rnd.uniform(-2, 1)
    # golden sunset wash on the village, cool shade on the far side
    out.append(glow(250, 330, 150, "#FFD08A", f"{u}-vg", 0.22))
    # the harbour ramp at the foot of the village with boats pulled up
    out.append(Q([(178, 404), (200, 388), (290, 386), (300, 404)], "#B8A08E"))
    out.append(Q([(178, 404), (300, 404), (300, 408), (178, 408)], "#6A4E52"))
    out.append(gozzo(214, 398, 24, "#2E6AB0", flip=True, ref=False) + gozzo(244, 396, 22, "#D8463A", ref=False) + gozzo(272, 397, 20, "#3E8A6A", flip=True, ref=False))
    # the cove in front: reflections of the coloured houses broken by ripples
    out.append(f'<rect x="170" y="404" width="440" height="40" fill="#1E4E6E"/>')
    refl = "".join(f'<rect x="{x:.1f}" y="408" width="{w:.1f}" height="{min(36, h * 0.6):.1f}" fill="{c}" opacity="0.35"/>' for x, w, h, c in fronts)
    out.append(f'<clipPath id="{u}-cv"><rect x="170" y="406" width="440" height="38"/></clipPath><g clip-path="url(#{u}-cv)">{refl}'
               + water_lines(90, 33, (170, 406, 610, 444), ["#1E4E6E", "#3A7AA0", "#FFD8A0", "#14405E"], w=(10, 40), h=(1.2, 2.4), opacity=(0.5, 0.95), grow=False) + "</g>")
    out.append('<rect x="170" y="404" width="440" height="2" fill="#F4E8D8" opacity="0.6"/>')
    # surf on the seaward rocks
    out.append(mist(184, 402, 26, 10, "#FFFFFF", f"{u}-fm", 0.75))
    out.append(water_lines(24, 32, (150, 392, 200, 420), ["#FFFFFF", "#D8EEF4"], w=(6, 18), h=(1, 2), opacity=(0.5, 0.9), grow=False))
    # boats moored in the cove, a swimmer
    out.append(gozzo(100, 370, 36, "#F4F0E8", inner="#2E6AB0") + gozzo(150, 402, 50, "#2E5A9A") + gozzo(88, 428, 60, "#D8463A", flip=True))
    out.append('<g stroke="#F4F0E8" stroke-width="1.2" opacity="0.8"><path d="M 100 362 L 124 340"/><path d="M 150 391 L 172 366"/></g>')
    out.append('<circle cx="56" cy="390" r="2.6" fill="#5A3A2E"/><path d="M 49 393 q 7 -3 14 0" stroke="#FFFFFF" stroke-width="1.4" fill="none" opacity="0.8"/>')
    out.append(gulls([(120, 220, 11), (140, 232, 8), (360, 160, 9)], "#4A3A5A", 1.7))
    return "\n".join(out)


# ================================================================ PROVENCE — lavender rows to a stone mas, Mont Ventoux beyond, July afternoon
def cypress_tree(x, base, h, seed, dark="#1E3A24", mid="#2E4E2E", lit="#6A8A3E", w=0.16):
    """Italian cypress: tall flame of dense foliage, lit edge on the sunny (right) side."""
    rnd = random.Random(seed)
    hw = h * w / 2
    left, right = [], []
    n = 14
    for i in range(n + 1):
        t = i / n
        prof = math.sin(math.pi * min(1, t * 1.08) ** 0.9) ** 0.75 if t < 0.97 else 0.05
        y = base - h * t
        left.append((x - hw * prof * rnd.uniform(0.85, 1.1), y))
        right.append((x + hw * prof * rnd.uniform(0.85, 1.1), y))
    body = left + [(x, base - h - 3)] + right[::-1]
    lit_pts = [(x + hw * 0.1, base)] + [(px - (px - x) * 0.25, py) for px, py in right[:-1]] + [(x, base - h - 3)] + right[::-1]
    out = [f'<rect x="{x - 1.6:.1f}" y="{base - 6:.1f}" width="3.2" height="7" fill="#4A3424"/>',
           Q(body, dark), Q([(px * 0.5 + x * 0.5 + (px - x) * 0.3, py) for px, py in left] + right[::-1], mid),
           Q(lit_pts, lit, ' opacity="0.65"')]
    out.append("".join(f'<path d="M {x + rnd.uniform(-hw, hw) * 0.7:.1f} {base - h * t:.1f} q {rnd.uniform(1, 3):.1f} 2 {rnd.uniform(2, 5):.1f} 1" stroke="{dark}" stroke-width="1.2" fill="none" opacity="0.6"/>'
                       for t in [rnd.uniform(0.08, 0.9) for _ in range(int(h / 4))]))
    return "".join(out)


def honeybee(x, y, s=1.0, flip=False, wing="#FFFFFF"):
    d = -1 if flip else 1
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({d * s:.2f} {s:.2f})">'
            f'<ellipse cx="-1" cy="-5" rx="4" ry="6" transform="rotate(-25)" fill="{wing}" opacity="0.75"/>'
            f'<ellipse cx="3" cy="-5" rx="3.4" ry="5" transform="rotate(20)" fill="{wing}" opacity="0.6"/>'
            f'<ellipse cx="0" cy="0" rx="6" ry="3.8" fill="#E8A830"/>'
            f'<path d="M -1.5 -3.6 L -1.5 3.6 M 1.8 -3.4 L 1.8 3.4" stroke="#2A1E14" stroke-width="1.5"/>'
            f'<path d="M 5.4 -1 L 7.6 0 L 5.4 1 Z" fill="#2A1E14"/><circle cx="-6.6" cy="0" r="2.6" fill="#2A1E14"/>'
            f'<path d="M -8 -2 q -2 -3 -4 -3" stroke="#2A1E14" stroke-width="0.9" fill="none"/></g>')


def provence():
    u = "pv"
    C = Cam(f=420, cx=300, vpy=262, eye=2.4)
    out = [defs(
        lg(f"{u}-sky", [(0, "#3E7EC8"), (0.45, "#7AAEDC"), (0.8, "#C8DCEA"), (1, "#F2E6CC")], 0, 40, 0, 262, units="userSpaceOnUse"),
        lg(f"{u}-vent", [(0, "#E8EEF6"), (0.25, "#C8D2E4"), (1, "#8E9EC0")]),
        lg(f"{u}-lub", [(0, "#8EA0BE"), (1, "#A4B4C8")]),
        lg(f"{u}-vfoot", [(0, "#8296B8", 0), (1, "#7A8EB2", 0.85)]),
        lg(f"{u}-soil", [(0, "#C89A6A"), (1, "#9A6A44")], 0, 262, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-lav", [(0, "#9A86C8"), (0.5, "#7E62B8"), (1, "#6A48A8")], 0, 262, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-wall", [(0, "#F2DEB4"), (1, "#D8BC8E")]),
        lg(f"{u}-roof", [(0, "#D27A4E"), (1, "#A8543A")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(560, 60, 220, "#FFF6DA", f"{u}-sun", 0.7))
    out.append(cumulus(f"{u}-c1", 170, 130, 120, 28, 5, "#FFFFFF", "#F2EEF2", "#B8BCD4", light=1))
    out.append(cumulus(f"{u}-c2", 420, 112, 80, 20, 9, "#FFFFFF", "#F2EEF2", "#B8BCD4", light=1))
    out.append(cumulus(f"{u}-c3", 520, 170, 60, 14, 13, "#FFFFFF", "#F4F0F4", "#C4C6DA", light=1))
    # Mont Ventoux with its bare white limestone summit, and the long blue Luberon ridge
    poly, vl = ridge_poly([(-10, 252), (40, 230), (100, 206), (140, 196), (170, 198), (220, 222), (290, 246), (330, 258)], 3, amp=4, depth=4, fill=f"url(#{u}-vent)")
    out.append(poly)
    out.append(f'<clipPath id="{u}-vc"><polygon points="{P(vl + [(330, 270), (-10, 270)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-vc)">' + streaks(50, 4, (40, 196, 260, 250), ["#FFFFFF", "#B8C4DA", "#DCE2EE"], w=(1, 2.4), length=(6, 18), opacity=(0.4, 0.8), slant=0.6)
               + f'<rect x="-10" y="214" width="340" height="56" fill="url(#{u}-vfoot)"/></g>')
    out.append('<line x1="156" y1="198" x2="156" y2="186" stroke="#E8ECF4" stroke-width="2"/><circle cx="156" cy="186" r="2" fill="#F4F6FA"/>')
    poly, ll = ridge_poly([(240, 262), (320, 244), (400, 240), (480, 236), (560, 242), (610, 248)], 5, amp=4, depth=4, fill=f"url(#{u}-lub)")
    out.append(poly)
    # rolling farmland: patchwork of wheat, sunflowers, vines and olive groves
    hills = rough([(-10, 266), (100, 254), (200, 262), (300, 254), (400, 258), (500, 250), (610, 256)], 7, amp=4, depth=4)
    out.append(Q(hills + [(610, 280), (-10, 280)], "#B8B060"))
    patches = [((-10, 258, 120, 272), "#E8C45A"), ((120, 262, 230, 272), "#8A9A4A"), ((230, 256, 320, 270), "#D8B050"), ((420, 254, 520, 268), "#F2CC40"), ((520, 254, 610, 270), "#7A8A44")]
    rnd = random.Random(11)
    for (x0, y0, x1, y1), c in patches:
        out.append(f'<rect x="{x0}" y="{y0 + 4}" width="{x1 - x0}" height="{y1 - y0 + 6}" fill="{c}" opacity="0.85"/>')
    out.append(dots(160, 12, (-10, 262, 610, 280), "#4E6A34", r=(1, 2.2), opacity=(0.6, 0.9)))
    out.append(dots(60, 13, (420, 258, 520, 270), "#8A5A1A", r=(0.8, 1.4), opacity=(0.6, 0.9)))
    out.append(tree_line(hills, 14, ["#2E4A2E", "#3A5A34"], density=0.35, hmin=8, hmax=16, sink=10))
    # ---- the field: lavender rows running to the farmhouse
    out.append(f'<polygon points="{P([C(-60, 0, 400), C(60, 0, 400), C(60, 0, 3), C(-60, 0, 3)])}" fill="url(#{u}-soil)"/>')
    Z0, Z1 = 3.6, 70.0
    rows = []
    for i in range(-16, 16):
        Xc = (i + 0.5) * 1.75
        rows.append(Xc)
    # far part of each row: a continuous strip; near part: individual domed bushes, drawn back to front
    ZS = 22.0
    strips = []
    for Xc in rows:
        hw, top = 0.5, 0.45
        side = -1 if Xc > 0 else 1
        strips.append(Q([C(Xc - hw, top, Z1), C(Xc + hw, top, Z1), C(Xc + hw, top, ZS), C(Xc - hw, top, ZS)], "#8A70C4"))
        strips.append(Q([C(Xc + side * hw, top, Z1), C(Xc + side * hw * 1.1, 0, Z1), C(Xc + side * hw * 1.1, 0, ZS), C(Xc + side * hw, top, ZS)], "#9C84D4" if Xc < 0 else "#4E3A8E"))
    out.append("".join(strips))
    bushes = []
    for Xc in rows:
        z = ZS
        while z > Z0 * 0.92:
            bushes.append((z, Xc))
            z /= 1.075
    bushes.sort(key=lambda b_: -b_[0])
    bush_svg = []
    for z, Xc in bushes:
        x, y = C(Xc + rnd.uniform(-0.05, 0.05), 0.0, z)
        sc = C.f / z
        rx, ry = 0.56 * sc * rnd.uniform(0.9, 1.08), 0.5 * sc * rnd.uniform(0.85, 1.12)
        cy = y - ry * 0.75
        if x + rx < -20 or x - rx > 620:
            continue
        bush_svg.append(f'<ellipse cx="{x:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#4A3488"/>'
                        f'<ellipse cx="{x + rx * 0.12:.1f}" cy="{cy - ry * 0.14:.1f}" rx="{rx * 0.86:.1f}" ry="{ry * 0.8:.1f}" fill="{rnd.choice(["#7A5CBC", "#7256B6", "#8262C2"])}"/>'
                        f'<ellipse cx="{x + rx * rnd.uniform(0.18, 0.34):.1f}" cy="{cy - ry * rnd.uniform(0.26, 0.4):.1f}" rx="{rx * rnd.uniform(0.4, 0.56):.1f}" ry="{ry * rnd.uniform(0.36, 0.48):.1f}" fill="{rnd.choice(["#A890DE", "#B49CE4", "#9C82D6"])}"/>')
        if sc > 14:
            for _ in range(int(sc / 6)):
                a_ = rnd.uniform(math.pi * 1.05, math.pi * 1.95)
                d_ = rnd.uniform(0.55, 1.0)
                px, py = x + rx * d_ * math.cos(a_), cy + ry * d_ * math.sin(a_)
                L = sc * 0.16
                bush_svg.append(f'<path d="M {px:.1f} {py + L * 0.3:.1f} l {(px - x) / rx * L * 0.25:.1f} {-L:.1f}" stroke="{rnd.choice(["#5A3A9A", "#B49AE6", "#8A68CC"])}" stroke-width="{max(1.2, sc * 0.03):.1f}" stroke-linecap="round"/>')
    out.append("".join(bush_svg))
    # green weeds and ochre soil between the rows
    # ---- the mas: stone farmhouse with a Roman-tile roof, lavender-blue shutters, a lower barn, cypresses, a plane tree
    hx, hz = 3.0, 74.0
    k = C.f / hz
    gx, gy = C(hx, 0, hz)
    W, H = 15 * k, 7.0 * k
    x0 = gx - W / 2
    out.append(leaf_canopy(f"{u}-pl", x0 + W + 18, gy - H - 8, 26, 22, 31, "#2E4A28", "#4E6E34", "#9AAE4E", gold="#D8C860", light=(1, -1), n=60))
    out.append(f'<rect x="{x0 + W + 16:.1f}" y="{gy - H:.1f}" width="4" height="{H:.1f}" fill="#8A7A6A"/>')
    # barn wing to the right, lower
    out.append(f'<rect x="{x0 + W:.1f}" y="{gy - H * 0.7:.1f}" width="{W * 0.45:.1f}" height="{H * 0.7:.1f}" fill="url(#{u}-wall)"/>')
    out.append(Q([(x0 + W - 2, gy - H * 0.7), (x0 + W + W * 0.45 + 3, gy - H * 0.7), (x0 + W + W * 0.45, gy - H * 0.9), (x0 + W, gy - H * 0.92)], f"url(#{u}-roof)"))
    out.append(f'<path d="M {x0 + W * 1.1:.1f} {gy:.1f} L {x0 + W * 1.1:.1f} {gy - H * 0.4:.1f} Q {x0 + W * 1.22:.1f} {gy - H * 0.55:.1f} {x0 + W * 1.34:.1f} {gy - H * 0.4:.1f} L {x0 + W * 1.34:.1f} {gy:.1f} Z" fill="#6A5A7A"/>')
    # main house
    out.append(f'<rect x="{x0:.1f}" y="{gy - H:.1f}" width="{W:.1f}" height="{H:.1f}" fill="url(#{u}-wall)"/>')
    out.append(blobs(40, 32, (x0, gy - H, x0 + W, gy), ["#C8A878", "#F8E8C8", "#B89868"], r=(1.2, 3), opacity=(0.4, 0.8), squash=0.6))
    out.append(Q([(x0 - 3, gy - H), (x0 + W + 3, gy - H), (x0 + W - 4, gy - H - 15), (x0 + 4, gy - H - 15)], f"url(#{u}-roof)"))
    out.append(f'<g stroke="#8A3E2A" stroke-width="1" opacity="0.6">' + "".join(f'<line x1="{x0 + W * t:.1f}" y1="{gy - H:.1f}" x2="{x0 + 4 + (W - 8) * t:.1f}" y2="{gy - H - 15:.1f}"/>' for t in [j / 22 for j in range(1, 22)]) + "</g>")
    out.append(f'<rect x="{x0 - 3:.1f}" y="{gy - H - 1:.1f}" width="{W + 6:.1f}" height="2.6" fill="#7A3A28"/><rect x="{x0 + 4:.1f}" y="{gy - H - 16:.1f}" width="{W - 8:.1f}" height="2.4" fill="#E0905E"/>')
    out.append(f'<rect x="{x0 + W * 0.7:.1f}" y="{gy - H - 22:.1f}" width="6" height="9" fill="#E2CCA4"/><rect x="{x0 + W * 0.7 - 1:.1f}" y="{gy - H - 23:.1f}" width="8" height="2" fill="#B8603E"/>')
    for j in range(4):
        wx = x0 + W * (0.16 + j * 0.23)
        for wy, hh in ((gy - H * 0.82, H * 0.24), (gy - H * 0.42, H * 0.3)):
            if j == 2 and wy > gy - H * 0.5:
                out.append(f'<path d="M {wx - 4:.1f} {gy:.1f} L {wx - 4:.1f} {gy - H * 0.38:.1f} Q {wx:.1f} {gy - H * 0.48:.1f} {wx + 4:.1f} {gy - H * 0.38:.1f} L {wx + 4:.1f} {gy:.1f} Z" fill="#5A4A3A"/>')
                continue
            out.append(f'<rect x="{wx - 2.4:.1f}" y="{wy:.1f}" width="4.8" height="{hh:.1f}" fill="#3A3040"/>'
                       f'<rect x="{wx - 5.2:.1f}" y="{wy:.1f}" width="2.6" height="{hh:.1f}" fill="#7E9AC8"/><rect x="{wx + 2.6:.1f}" y="{wy:.1f}" width="2.6" height="{hh:.1f}" fill="#7E9AC8"/>')
    out.append(f'<rect x="{x0:.1f}" y="{gy - H:.1f}" width="{W:.1f}" height="3" fill="#6A4A3A" opacity="0.3"/>')
    # cypress windbreak beside the house
    for cx_, hh, sd in ((x0 - 14, 92, 41), (x0 - 28, 78, 42), (x0 - 40, 64, 43), (x0 + W + W * 0.45 + 12, 70, 44)):
        out.append(cypress_tree(cx_, gy + 2, hh, sd))
    # warm haze over the far end of the field
    out.append(mist(300, 280, 320, 18, "#F6E2C4", f"{u}-hz", 0.45))
    out.append(honeybee(150, 368, 1.25) + honeybee(470, 388, 1.4, flip=True) + honeybee(392, 330, 0.9, flip=True))
    out.append(gulls([(330, 150, 8), (346, 158, 6)], "#2A2A4A", 1.6))
    return "\n".join(out)


BUILD = {
    "edinburgh": (edinburgh, "EDINBURGH", "SCOTLAND · UNITED KINGDOM", "#2A1E3E", "#F2A65E", "#FFF1E4", "#F6C08A"),
    "swiss-alps": (swiss_alps, "SWISS ALPS", "SWITZERLAND · EUROPE", "#B0262C", "#F6E7D2", "#FFFFFF", "#FFD9C8"),
    "iceland": (iceland, "ICELAND", "LAND OF FIRE & ICE", "#0B1428", "#4FE0A0", "#F2FFF8", "#8EF0C4"),
    "norway": (norway, "NORWAY", "GEIRANGER · WESTERN FJORDS", "#163A56", "#D8453A", "#FFF6EE", "#F2B8A8"),
    "cinque-terre": (cinque_terre, "CINQUE TERRE", "ITALY · LIGURIA", "#1E4E6E", "#F6A86A", "#FFF4E6", "#F9C894"),
    "provence": (provence, "PROVENCE", "FRANCE · LAVENDER FIELDS", "#3B2C68", "#F2C94C", "#FBF4FF", "#E8D2F8"),
    "dublin": (dublin, "DUBLIN", "IRELAND · EUROPE", "#134A3A", "#F2B84A", "#FFF6E4", "#F6D088"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("world", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
