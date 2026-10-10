"""American Places, painted edition (batch F): Los Angeles, San Diego, Portland, Maui, St. Louis, Brooklyn,
Badlands and Annapolis. Same painterly approach as places_painted.py — graded skies, a real light direction,
atmospheric depth, reflections, and small storytelling details — each with its own hour and palette."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from places_painted import Cam, bison, defs, puff_column, facade_windows
from poster import poster
import figures as F


# ---------------------------------------------------------------- shared helpers
def cumulus(cx, cy, w, h, seed, grad, hi="#FFFFFF", hi_op=0.6, shade="#8E86A8", shade_op=0.22, n=None):
    """Flat-bottomed cumulus built from many puffs; one shared gradient, lit tops, shaded bellies."""
    rnd = random.Random(seed)
    n = n or int(w / 4)
    body, lights, shades = [], [], []
    for _ in range(n):
        t = rnd.uniform(-1, 1)
        x = cx + t * w / 2
        top = h * (1 - abs(t) ** 1.6)
        y = cy - rnd.uniform(0.15, 1) * top
        r = rnd.uniform(0.25, 0.5) * (h * 0.4 + top * 0.6)
        r = min(r, cy - y + h * 0.25)
        if r < 2:
            continue
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>')
        lights.append(f'<circle cx="{x - r * 0.2:.1f}" cy="{y - r * 0.28:.1f}" r="{r * 0.62:.1f}"/>')
        shades.append(f'<circle cx="{x + r * 0.1:.1f}" cy="{y + r * 0.35:.1f}" r="{r * 0.6:.1f}"/>')
    clip = f'{grad}-c{seed}'
    return (f'<clipPath id="{clip}"><rect x="{cx - w}" y="{cy - h * 3}" width="{w * 2}" height="{h * 3 + h * 0.18:.1f}"/></clipPath>'
            f'<g clip-path="url(#{clip})"><g fill="url(#{grad})">' + "".join(body) + "</g>"
            + f'<g fill="{shade}" opacity="{shade_op}">' + "".join(shades) + "</g>"
            + f'<g fill="{hi}" opacity="{hi_op}">' + "".join(lights) + "</g></g>")


def walker(x, base, h, col, head="#1E1A22", legs="#1E1A22", rim=None, rim_side=1, bag=None, pose="walk", facing=1, seed=None, pal=None, tint=None):
    """Small painted pedestrian (figures.py), h = full height in px; the rim light sits on rim_side."""
    p = {"top": col}
    if bag:
        p.update(bag=bag)
    p.update(pal or {})
    return F.person(x, base, h, pose, facing, p, seed=int(x * 3 + base) if seed is None else seed, rim=rim, light=rim_side, tint=tint)


def ripples(n, seed, box, colors, w=(6, 30), h=(0.8, 2), opacity=(0.3, 0.8), persp=None):
    """Horizontal water-glint strokes; persp=(y_horizon, y_bottom) widens them toward the viewer."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        y = rnd.uniform(y0, y1)
        k = 1.0
        if persp:
            k = 0.25 + 1.2 * max(0, (y - persp[0]) / (persp[1] - persp[0]))
        ww = rnd.uniform(*w) * k
        out.append(f'<rect x="{rnd.uniform(x0, x1) - ww / 2:.1f}" y="{y:.1f}" width="{ww:.1f}" height="{rnd.uniform(*h) * k:.1f}" rx="1" fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*opacity):.2f}"/>')
    return "".join(out)


def gulls(spec, color, sw=2):
    return f'<g fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round">' + "".join(
        f'<path d="M {x} {y} q {s * 0.5:.1f} {-s * 0.45:.1f} {s} 0 q {s * 0.5:.1f} {-s * 0.45:.1f} {s} 0"/>' for x, y, s in spec) + "</g>"


# ---------------------------------------------------------------- Los Angeles (palm-lined street at sunset)
def fan_palm(x, base, h, seed, trunk="#3A2238", crown="#2E1C30", skirt="#4A2A30", rim="#FF9E6A", lean=0.0):
    """Mexican fan palm: very tall slender trunk, small shaggy crown with a dead-frond skirt, rim light on the sun side (left)."""
    rnd = random.Random(seed)
    tx, ty = x + lean * h, base - h
    w0, w1 = max(0.9, h * 0.014), max(0.6, h * 0.008)
    bend = rnd.uniform(-0.02, 0.02) * h
    out = [f'<path d="M {x - w0:.1f} {base:.1f} Q {x + bend + lean * h * 0.4:.1f} {base - h * 0.5:.1f} {tx - w1:.1f} {ty:.1f} L {tx + w1:.1f} {ty:.1f} '
           f'Q {x + bend + lean * h * 0.4 + w0 * 1.6:.1f} {base - h * 0.5:.1f} {x + w0:.1f} {base:.1f} Z" fill="{trunk}"/>']
    if h > 120:  # rim light along the left of the trunk
        out.append(f'<path d="M {x - w0:.1f} {base:.1f} Q {x + bend + lean * h * 0.4:.1f} {base - h * 0.5:.1f} {tx - w1:.1f} {ty:.1f}" fill="none" stroke="{rim}" stroke-width="{max(0.8, w0 * 0.45):.1f}" opacity="0.55"/>')
    s = h * 0.075  # crown size
    # skirt of old fronds
    out.append(f'<path d="M {tx - s * 0.32:.1f} {ty + s * 0.1:.1f} Q {tx - s * 0.36:.1f} {ty + s * 0.9:.1f} {tx - s * 0.12:.1f} {ty + s * 1.25:.1f} L {tx + s * 0.14:.1f} {ty + s * 1.2:.1f} Q {tx + s * 0.36:.1f} {ty + s * 0.8:.1f} {tx + s * 0.3:.1f} {ty + s * 0.1:.1f} Z" fill="{skirt}"/>')
    # fan fronds
    for i in range(15):
        a = math.radians(-195 + i * 15 + rnd.uniform(-5, 5))
        L = s * rnd.uniform(0.75, 1.05)
        droop = s * 0.35 * max(0, math.cos(a)) ** 2 + s * 0.2
        ex, ey = tx + L * math.cos(a), ty + L * math.sin(a) * 0.7 + droop
        wd = s * 0.2
        perp = (-math.sin(a), math.cos(a))
        out.append(f'<path d="M {tx:.1f} {ty:.1f} L {ex + perp[0] * wd:.1f} {ey + perp[1] * wd:.1f} L {ex - perp[0] * wd:.1f} {ey - perp[1] * wd:.1f} Z" fill="{crown}"/>')
        if h > 90:
            tips = "".join(f'M {ex + perp[0] * wd * t:.1f} {ey + perp[1] * wd * t:.1f} l {math.cos(a) * s * 0.18:.1f} {math.sin(a) * s * 0.14 + s * 0.08:.1f} ' for t in (-0.8, 0, 0.8))
            out.append(f'<path d="{tips}" stroke="{crown}" stroke-width="{max(0.6, s * 0.04):.1f}" fill="none"/>')
        if math.cos(a) < -0.2 and h > 60:
            out.append(f'<path d="M {tx:.1f} {ty:.1f} L {ex + perp[0] * wd:.1f} {ey + perp[1] * wd:.1f}" stroke="{rim}" stroke-width="{max(0.6, s * 0.035):.1f}" opacity="0.6"/>')
    return "".join(out)


def bungalow(C, X, z0, z1, h, wall, roof, seed, side):
    """Low Spanish-revival house facing the street (plane X), tile roof, lit windows."""
    rnd = random.Random(seed)
    out = [f'<polygon points="{P(C.quad_x(X, z0, z1, 0, h))}" fill="{wall}"/>']
    out.append(f'<polygon points="{P([C(X, h, z0), C(X - side * 1.5, h + 1.6, z0 + 1), C(X - side * 1.5, h + 1.6, z1 - 1), C(X, h, z1)])}" fill="{roof}"/>')
    for i in range(3):
        za = z0 + (z1 - z0) * (0.12 + i * 0.3)
        zb = za + (z1 - z0) * 0.16
        on = rnd.random() < 0.7
        out.append(f'<polygon points="{P(C.quad_x(X, za, zb, 0.9, 2.4))}" fill="{"#FFC878" if on else "#3A2A40"}"/>')
    out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, 0, h))}" fill="#3A1A48" opacity="0.38"/>')
    return "".join(out)


def los_angeles():
    u = "la"
    C = Cam(f=320, cx=300, vpy=296, eye=1.5)
    out = [defs(
        lg(f"{u}-sky", [(0, "#2C2152"), (0.28, "#5E3A7E"), (0.52, "#C2507E"), (0.72, "#F2805E"), (0.88, "#FFB66E"), (1, "#FFD892")], 0, 40, 0, 296, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#A86A9A"), (1, "#E2988E")], 0, 170, 0, 296, units="userSpaceOnUse"),
        lg(f"{u}-hill", [(0, "#6E4080"), (1, "#4A2E62")], 0, 240, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-road", [(0, "#C08088"), (0.06, "#7A5272"), (0.4, "#4A3450"), (1, "#2A1E32")], 0, 296, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-walk", [(0, "#B08488"), (1, "#6A4A5C")], 0, 296, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-lawn", [(0, "#5E5A5A"), (1, "#2E3A2E")], 0, 296, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#FFC28A", 0), (1, "#FFC28A", 0.75)]),
        lg(f"{u}-cl", [(0, "#FFD3A0"), (0.5, "#F59A8A"), (1, "#9A5A8E")]),
        lg(f"{u}-car", [(0, "#6ACACA"), (1, "#2A7A86")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(26, 7, (40, 44, 560, 110), "#FBE8E0", r=(0.6, 1.3), opacity=(0.3, 0.8)))
    # the sun sinking in the west (left), its glow flooding the haze
    out.append(glow(196, 262, 280, "#FFD48A", f"{u}-sun", 0.95))
    out.append('<circle cx="196" cy="258" r="22" fill="#FFF0C4"/>')
    # long sunset cloud streaks lit from below
    for x, y, w, h_ in ((120, 112, 150, 10), (470, 98, 170, 12), (330, 146, 120, 8), (540, 160, 90, 7), (64, 168, 90, 7)):
        out.append(f'<path d="M {x - w / 2} {y} q {w * 0.25} {-h_ * 1.4} {w * 0.5} {-h_ * 0.6} q {w * 0.2} {-h_ * 1.2} {w * 0.5} {h_ * 0.4} q {-w * 0.5} {h_ * 0.9} {-w} {h_ * 0.2} Z" fill="url(#{u}-cl)" opacity="0.85"/>')
        out.append(f'<path d="M {x - w / 2 + 8} {y + 1} q {w * 0.45} {h_ * 0.7} {w - 16} 0" stroke="#FFE2A8" stroke-width="1.6" fill="none" opacity="0.8"/>')
    # San Gabriel Mountains: big hazy range rising behind the end of the street, lit faces toward the sun
    poly, far = ridge_poly([(-10, 232), (50, 218), (110, 226), (170, 204), (230, 196), (290, 176), (330, 184), (380, 170), (440, 190), (500, 182), (560, 200), (610, 196)], 11, base=300, amp=8, fill=f"url(#{u}-far)")
    out.append(poly)
    out.append(f'<polyline points="{P(far)}" fill="none" stroke="#FFD6B0" stroke-width="1.6" opacity="0.55"/>')
    poly, mid = ridge_poly([(-10, 248), (60, 236), (140, 244), (210, 226), (270, 234), (330, 214), (400, 232), (470, 220), (540, 238), (610, 230)], 17, base=300, amp=6, fill="#B47496")
    out.append(poly)
    out.append(f'<polyline points="{P(mid)}" fill="none" stroke="#FFC8A0" stroke-width="1.4" opacity="0.5"/>')
    out.append(f'<rect x="0" y="220" width="600" height="80" fill="url(#{u}-haze)"/>')
    # nearer hills dotted with houses whose windows are coming on
    poly, hl = ridge_poly([(-10, 262), (70, 250), (150, 258), (220, 246), (300, 250), (360, 242), (440, 254), (520, 244), (610, 256)], 21, base=300, amp=5, fill=f"url(#{u}-hill)")
    out.append(poly)
    rnd = random.Random(31)
    for _ in range(90):
        x = rnd.uniform(0, 600)
        top = y_on(hl, x) or 250
        y = rnd.uniform(top + 3, 298)
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="2.4" height="1.7" fill="{rnd.choice(["#FFD48A", "#FFE6B0", "#FFC070"])}" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    out.append(tree_line(hl, 23, ["#4E2E5E", "#442858"], density=0.6, hmin=4, hmax=9))
    # tiny palms on the hill crest, the classic LA silhouette
    for x in (96, 112, 404, 418, 470):
        y = y_on(hl, x) or 250
        out.append(fan_palm(x, y + 2, 26, x, trunk="#4A2A5A", crown="#4A2A5A", skirt="#4A2A5A"))
    # ground planes: lawns, sidewalks, the road
    out.append(f'<polygon points="{P([C(-200, 0, 800), C(200, 0, 800), C(200, 0, 2), C(-200, 0, 2)])}" fill="url(#{u}-lawn)"/>')
    for sgn in (-1, 1):
        out.append(f'<polygon points="{P([C(sgn * 8.2, 0, 800), C(sgn * 11, 0, 800), C(sgn * 11, 0, 2), C(sgn * 8.2, 0, 2)])}" fill="url(#{u}-walk)"/>')
    out.append(f'<polygon points="{P([C(-6.2, 0, 800), C(6.2, 0, 800), C(6.2, 0, 2), C(-6.2, 0, 2)])}" fill="url(#{u}-road)"/>')
    for sgn in (-1, 1):
        out.append(f'<polygon points="{P([C(sgn * 6.2, 0.15, 800), C(sgn * 6.2, 0.15, 2), C(sgn * 6.2, 0, 2), C(sgn * 6.2, 0, 800)])}" fill="#D8A8A0"/>')
    # sunset sheen running down the asphalt
    out.append(f'<polygon points="{P([C(-2.6, 0, 800), C(0.6, 0, 800), C(1.6, 0, 3), C(-5.0, 0, 3)])}" fill="#FFC28A" opacity="0.13"/>')
    for dx in (-0.12, 0.12):
        out.append(f'<polygon points="{P([C(dx - 0.06, 0, 800), C(dx + 0.06, 0, 800), C(dx + 0.06, 0, 3), C(dx - 0.06, 0, 3)])}" fill="#F2C24A" opacity="0.9"/>')
    for z in [4 * 1.25 ** i for i in range(22)]:
        for X in (-3.1, 3.1):
            out.append(f'<polygon points="{P([C(X - 0.08, 0, z), C(X + 0.08, 0, z), C(X + 0.08, 0, z * 1.1), C(X - 0.08, 0, z * 1.1)])}" fill="#F4E6E0" opacity="0.6"/>')
    # Spanish-revival houses set back behind hedges
    rnd = random.Random(5)
    walls = ["#E8C2A8", "#F2D6BC", "#D9A88E", "#EBCFB8", "#CFA0A0"]
    for sgn in (-1, 1):
        z = 24
        while z < 500:
            d = rnd.uniform(10, 16)
            out.append(bungalow(C, sgn * 19, z, z + d, rnd.uniform(3.6, 5.0), rnd.choice(walls), "#A4524A", int(z * 10) + sgn, sgn))
            z += d + rnd.uniform(4, 8)
        for z in [10 * 1.07 ** i for i in range(60)]:
            x, b = C(sgn * 13.5, 0, z)
            r = C.f * 1.0 / z
            out.append(f'<ellipse cx="{x:.1f}" cy="{b - r * 0.7:.1f}" rx="{r * 1.4:.1f}" ry="{r:.1f}" fill="{rnd.choice(["#3A4A36", "#33422F", "#405238"])}"/>')
            if sgn < 0 and rnd.random() < 0.5:
                out.append(f'<ellipse cx="{x - r * 0.3:.1f}" cy="{b - r * 1.2:.1f}" rx="{r * 0.7:.1f}" ry="{r * 0.35:.1f}" fill="#8A8A5A" opacity="0.5"/>')
    # long palm shadows raking across the road toward the viewer (sun ahead-left)
    zs = [15 * 1.2 ** i for i in range(20)]
    sh = []
    for sgn in (-1, 1):
        for z in zs:
            X = sgn * 9.6
            if z - 5 > 3:
                sh.append(f'<polygon points="{P([C(X - 0.25, 0, z), C(X + 0.25, 0, z), C(X + 13, 0, z - 5), C(X + 12.6, 0, z - 5)])}"/>')
    out.append(f'<clipPath id="{u}-gc"><rect x="0" y="297" width="600" height="147"/></clipPath><g clip-path="url(#{u}-gc)" fill="#1A0E22" opacity="0.26">{"".join(sh)}</g>')
    # street lamps between the palms
    for z in [18 * 1.28 ** i for i in range(12)]:
        for sgn in (-1, 1):
            x0, y0 = C(sgn * 7.4, 0, z)
            x1, y1 = C(sgn * 7.4, 5.5, z)
            sw = max(0.6, C.f * 0.14 / z)
            out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#2A1A2E" stroke-width="{sw:.1f}"/>')
            out.append(glow(x1, y1, C.f * 1.3 / z, "#FFE2A0", f"{u}-l{int(z)}{sgn + 1}", 0.85))
            out.append(f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="{max(0.8, C.f * 0.2 / z):.1f}" fill="#FFF2CC"/>')
    # the palms: two long rows marching to the mountains
    for z in reversed(zs):
        for sgn in (-1, 1):
            x, b = C(sgn * 9.6, 0, z)
            hh = C.f * rnd.uniform(21, 26) / z
            out.append(fan_palm(x, b, hh, int(z * 13) + sgn, lean=sgn * rnd.uniform(-0.005, 0.02)))
    # cars: an oncoming car with headlights far off, a vintage convertible cruising toward the hills
    def car(X, Z, away=True):
        x, b = C(X, 0, Z)
        k = C.f / Z / 22
        if not away:
            return (f'<g transform="translate({x:.1f} {b:.1f}) scale({k:.3f})"><path d="M -40 -6 L -42 -22 Q -40 -28 -30 -29 L 30 -29 Q 40 -28 42 -22 L 40 -6 Z" fill="#D9C6B8"/>'
                    '<path d="M -26 -29 L -20 -40 L 20 -40 L 26 -29 Z" fill="#3A2A40"/><circle cx="-30" cy="-20" r="5" fill="#FFF6D8"/><circle cx="30" cy="-20" r="5" fill="#FFF6D8"/></g>'
                    + glow(x, b - 20 * k, 60 * k, "#FFF2C8", f"{u}-h{int(Z)}", 0.6))
        g = (f'<g transform="translate({x:.1f} {b:.1f}) scale({k:.3f})">'
             '<ellipse cx="0" cy="0" rx="48" ry="4" fill="#120C16" opacity="0.5"/>'
             f'<path d="M -44 -6 L -46 -22 Q -45 -28 -36 -29 L -24 -29 L -20 -33 L 20 -33 L 24 -29 L 36 -29 Q 45 -28 46 -22 L 44 -6 Z" fill="url(#{u}-car)"/>'
             '<path d="M -18 -33 L -15 -42 L 15 -42 L 18 -33" fill="none" stroke="#E8E0E8" stroke-width="2"/>'
             '<circle cx="-8" cy="-38" r="5" fill="#2A1A22"/><path d="M -13 -36 q -8 2 -14 -1" stroke="#FF6A8A" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
             '<circle cx="9" cy="-38" r="5.2" fill="#2A1A22"/>'
             '<rect x="-46" y="-15" width="92" height="4" fill="#ECE2EA"/><rect x="-14" y="-24" width="28" height="7" rx="1" fill="#F2E6D0"/>'
             '<path d="M -46 -29 q 6 -6 12 -2 M 46 -29 q -6 -6 -12 -2" stroke="#6ACACA" stroke-width="3" fill="none"/>'
             '<rect x="-43" y="-26" width="9" height="8" rx="2" fill="#FF3A3A"/><rect x="34" y="-26" width="9" height="8" rx="2" fill="#FF3A3A"/>'
             '<rect x="-40" y="-8" width="15" height="10" rx="3" fill="#120C16"/><rect x="25" y="-8" width="15" height="10" rx="3" fill="#120C16"/>'
             '<path d="M -44 -22 L -20 -31 M 44 -22 L 20 -31" stroke="#FFE6C0" stroke-width="1.2" opacity="0.5"/></g>')
        for sx in (-38.5, 38.5):
            g += glow(x + sx * k, b - 22 * k, 16 * k, "#FF4A4A", f"{u}-t{int(Z)}{int(sx)}", 0.6)
        g += f'<polygon points="{P([(x - 36 * k, b + 1), (x - 32 * k, b + 1), (x - 26 * k, 444), (x - 44 * k, 444)])}" fill="#FF4A4A" opacity="0.07"/>'
        return g
    out.append(car(-3.2, 90, away=False))
    out.append(car(3.0, 15))
    # a dog walker on the left sidewalk, a skateboarder on the right
    x, b = C(-9.6, 0, 13)
    hh = C.f * 1.7 / 13
    out.append(walker(x, b, hh, "#E07A5A", rim="#FFC27A", rim_side=-1, pose="dog_walker", facing=1, seed=11, pal={"dog": "#2A1A2E", "form": "f"}, tint=("#3A2448", 0.15)))
    x, b = C(9.5, 0, 26)
    hh = C.f * 1.7 / 26
    out.append(walker(x, b, hh, "#4A7AB0", rim="#FFC27A", rim_side=-1, pose="skate", facing=-1, seed=12, pal={"board": "#2A1A2E", "bottom_kind": "shorts", "hat_kind": "cap", "form": "m"},
                      tint=("#3A2448", 0.15)))
    out.append(gulls([(262, 120, 10), (280, 130, 7)], "#3A2244"))
    return "\n".join(out)


# ---------------------------------------------------------------- St. Louis (the Gateway Arch from the Illinois bank)
def arch_edges(cx, base, H):
    """Weighted catenary of the Gateway Arch: centroid y = 757.7 - 127.7 cosh(x / 127.7) ft (h = 625 ft at the
    centroid, 630 ft overall). Returns outer / inner outlines and the central ridge in screen space."""
    s = H / 630.0
    pts = []
    for i in range(121):
        X = -299.2 + 598.4 * i / 120
        Y = 757.7 - 127.7 * math.cosh(X / 127.7)
        dy = -math.sinh(X / 127.7)  # slope
        n = math.hypot(1, dy)
        nx, ny = -dy / n, 1 / n  # unit normal pointing up/out
        w = 17 + (54 - 17) * (1 - Y / 625.1)  # triangle side, 54 ft at base, 17 ft at top
        pts.append((X, Y, nx, ny, w))

    def scr(X, Y):
        return (cx + X * s, base - Y * s)
    outer = [scr(X + nx * w / 2, Y + ny * w / 2) for X, Y, nx, ny, w in pts]
    inner = [scr(X - nx * w / 2, Y - ny * w / 2) for X, Y, nx, ny, w in pts]
    ridge = [scr(X + nx * w * 0.08, Y + ny * w * 0.08) for X, Y, nx, ny, w in pts]
    return outer, inner, ridge


def gateway_arch(u, cx, base, H):
    outer, inner, ridge = arch_edges(cx, base, H)
    body = outer + inner[::-1]
    out = [defs(
        lg(f"{u}-ao", [(0, "#FFE9C4"), (0.35, "#F8C08A"), (0.7, "#D88A7A"), (1, "#9A6A7A")], 0, base - H, 0, base, units="userSpaceOnUse"),
        lg(f"{u}-ai", [(0, "#C8A0A6"), (0.5, "#8A7088"), (1, "#5A4A64")], 0, base - H, 0, base, units="userSpaceOnUse"),
    )]
    # outer (west/sunlit-reflecting) face and inner (shaded) face meet at the ridge
    out.append(f'<polygon points="{P(outer + ridge[::-1])}" fill="url(#{u}-ao)"/>')
    out.append(f'<polygon points="{P(ridge + inner[::-1])}" fill="url(#{u}-ai)"/>')
    # the right leg's outer face catches the sun directly: brighter
    half = len(outer) // 2
    out.append(f'<polygon points="{P(outer[half:] + ridge[half:][::-1])}" fill="#FFE6B8" opacity="0.35"/>')
    out.append(f'<polyline points="{P(ridge)}" fill="none" stroke="#FFF6E2" stroke-width="1.6" opacity="0.9"/>')
    out.append(f'<polyline points="{P(outer)}" fill="none" stroke="#FFD9A0" stroke-width="1.2" opacity="0.8"/>')
    # faint horizontal panel seams on the stainless skin
    cid = f"{u}-aclip"
    seams = "".join(f'<line x1="{cx - H}" y1="{base - H * t:.1f}" x2="{cx + H}" y2="{base - H * t:.1f}"/>' for t in [i / 24 for i in range(1, 24)])
    out.append(f'<clipPath id="{cid}"><polygon points="{P(body)}"/></clipPath><g clip-path="url(#{cid})" stroke="#6A5060" stroke-width="0.6" opacity="0.25">{seams}</g>')
    return "".join(out), body


def riverboat(x, y, k, u):
    """Mississippi sternwheeler, bow to the left, (x, y) = waterline centre."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})">'
            '<path d="M -70 -10 L 60 -10 L 64 0 L -60 0 Q -70 -2 -74 -8 Z" fill="#F4ECE0"/><rect x="-70" y="-12" width="132" height="3" fill="#B8323A"/>'
            '<rect x="-56" y="-26" width="108" height="14" fill="#F4ECE0"/><rect x="-46" y="-38" width="84" height="12" fill="#F4ECE0"/><rect x="-24" y="-48" width="30" height="10" fill="#F4ECE0"/><rect x="-20" y="-46" width="22" height="4" fill="#5A6A8A"/>'
            '<line x1="0" y1="-49" x2="0" y2="-62" stroke="#1E1A24" stroke-width="1.5"/><path d="M 0 -62 l 9 2.5 l -9 2.5 Z" fill="#B8323A"/>'
            + "".join(f'<rect x="{-52 + i * 9}" y="-23" width="5" height="7" fill="#FFD88A"/>' for i in range(11))
            + "".join(f'<rect x="{-42 + i * 9}" y="-35" width="5" height="6" fill="#FFD88A"/>' for i in range(9))
            + '<rect x="-58" y="-27" width="112" height="2" fill="#2A2A3A"/><rect x="-48" y="-39" width="88" height="2" fill="#2A2A3A"/><rect x="-26" y="-49" width="34" height="2" fill="#2A2A3A"/>'
            '<rect x="-40" y="-70" width="5" height="32" fill="#1E1A24"/><rect x="-28" y="-70" width="5" height="32" fill="#1E1A24"/>'
            '<path d="M -42 -72 l 2 -4 l 2 3 l 2 -3 l 2 4 Z M -30 -72 l 2 -4 l 2 3 l 2 -3 l 2 4 Z" fill="#1E1A24"/>'
            '<rect x="54" y="-30" width="22" height="30" rx="3" fill="#B8323A"/>'
            + "".join(f'<line x1="{54 + i * 4.4}" y1="-30" x2="{54 + i * 4.4}" y2="0" stroke="#7A1E26" stroke-width="1.4"/>' for i in range(1, 5))
            + "".join(f'<circle cx="{-37 + i * 9 + (i % 2) * 3}" cy="{-78 - i * 6}" r="{3.5 + i * 1.3:.1f}" fill="#E8D8DC" opacity="{0.5 - i * 0.08:.2f}"/>' for i in range(5))
            + "</g>")


def st_louis():
    u = "sl"
    out = [defs(
        lg(f"{u}-sky", [(0, "#2E3A6E"), (0.3, "#6A5A92"), (0.55, "#D2789A"), (0.75, "#F49A6A"), (0.9, "#FFC478"), (1, "#FFDE9A")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-river", [(0, "#F2B486"), (0.15, "#B47A84"), (0.5, "#4A4A6E"), (1, "#1E2440")], 0, 300, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-city", [(0, "#7A6890"), (1, "#5A4A72")]),
        lg(f"{u}-near", [(0, "#4A3E62"), (1, "#2E2A44")]),
        lg(f"{u}-park", [(0, "#3E4A4A"), (1, "#26303A")]),
        lg(f"{u}-cl", [(0, "#FFD8A8"), (0.6, "#F29A92"), (1, "#8A6A9E")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    # sun setting behind downtown, slightly right of the arch
    out.append(glow(384, 262, 280, "#FFD890", f"{u}-sun", 0.95))
    out.append('<circle cx="384" cy="258" r="20" fill="#FFF2C8"/>')
    for x, y, w, h_ in ((110, 118, 160, 9), (480, 128, 170, 10), (210, 166, 110, 7), (540, 182, 80, 6), (70, 196, 90, 6)):
        out.append(f'<path d="M {x - w / 2} {y} q {w * 0.25} {-h_ * 1.4} {w * 0.5} {-h_ * 0.6} q {w * 0.2} {-h_ * 1.2} {w * 0.5} {h_ * 0.4} q {-w * 0.5} {h_ * 0.9} {-w} {h_ * 0.2} Z" fill="url(#{u}-cl)" opacity="0.8"/>')
        out.append(f'<path d="M {x - w / 2 + 8} {y + 1} q {w * 0.45} {h_ * 0.7} {w - 16} 0" stroke="#FFE6B0" stroke-width="1.5" fill="none" opacity="0.8"/>')
    # downtown skyline in the haze, backlit
    rnd = random.Random(9)
    far = [(20, 244, 30), (52, 228, 24), (80, 250, 36), (122, 236, 26), (152, 214, 30), (186, 246, 24), (432, 230, 30), (466, 206, 26), (496, 238, 34), (536, 222, 28), (566, 246, 40)]
    for x, y, w in far:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{300 - y}" fill="url(#{u}-city)"/>')
    # the tallest tower with its pyramid crown (left of the arch), and a slim tower right
    out.append(f'<polygon points="{P([(96, 300), (96, 196), (104, 186), (114, 160), (124, 186), (132, 196), (132, 300)])}" fill="#6A5A84"/>')
    out.append('<line x1="114" y1="160" x2="114" y2="146" stroke="#6A5A84" stroke-width="2"/><circle cx="114" cy="146" r="1.6" fill="#FF6A6A"/>')
    out.append(f'<rect x="508" y="186" width="22" height="114" fill="#6A5A84"/><rect x="512" y="178" width="14" height="8" fill="#6A5A84"/>')
    # closer blocks with lit windows
    near = [(0, 262, 44), (40, 252, 40), (136, 258, 50), (184, 270, 40), (412, 262, 40), (450, 250, 50), (498, 266, 46), (544, 256, 60)]
    for x, y, w in near:
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{304 - y}" fill="url(#{u}-near)"/>')
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="2" fill="#FFB87A" opacity="0.7"/>')
        out.append("".join(f'<rect x="{xx}" y="{yy}" width="2.4" height="2.6" fill="{rnd.choice(["#FFD88A", "#FFC070"])}" opacity="{rnd.uniform(0.5, 1):.2f}"/>'
                           for xx in range(x + 4, x + w - 3, 6) for yy in range(y + 6, 298, 7) if rnd.random() < 0.35))
    # the Old Courthouse dome, framed under the arch
    cx = 300
    out.append(f'<rect x="{cx - 46}" y="268" width="92" height="36" fill="#7A6478"/><polygon points="{P([(cx - 50, 268), (cx, 256), (cx + 50, 268)])}" fill="#8A7088"/>')
    out.append(f'<rect x="{cx - 16}" y="232" width="32" height="30" fill="#8A7088"/><rect x="{cx - 18}" y="230" width="36" height="4" fill="#A88EA0"/>')
    out.append("".join(f'<rect x="{cx - 14 + i * 5}" y="238" width="2" height="18" fill="#5A4A60"/>' for i in range(6)))
    out.append(f'<path d="M {cx - 18} 232 Q {cx - 17} 206 {cx} 200 Q {cx + 17} 206 {cx + 18} 232 Z" fill="#6E8A84"/>')
    out.append(f'<path d="M {cx + 2} 200 Q {cx + 17} 206 {cx + 18} 232 L {cx + 8} 232 Q {cx + 9} 210 {cx + 2} 200 Z" fill="#4E6662"/>')
    out.append(f'<path d="M {cx - 18} 232 Q {cx - 17} 206 {cx} 200" stroke="#FFD8A0" stroke-width="1.4" fill="none" opacity="0.6"/>')
    out.append(f'<rect x="{cx - 4}" y="190" width="8" height="11" fill="#6E8A84"/><path d="M {cx - 5} 190 Q {cx} 182 {cx + 5} 190 Z" fill="#4E6662"/><line x1="{cx}" y1="183" x2="{cx}" y2="176" stroke="#4E6662" stroke-width="1.5"/>')
    # Arch grounds: dark park with trees on the bluff above the levee
    poly, gl = ridge_poly([(-10, 300), (120, 298), (300, 302), (480, 298), (610, 300)], 41, base=320, amp=2, fill=f"url(#{u}-park)")
    out.append(poly)
    for x in range(-6, 610, 9):
        if 176 <= x <= 424 and random.Random(x).random() < 0.6:
            continue
        r = random.Random(x * 3).uniform(4, 8)
        out.append(f'<circle cx="{x + random.Random(x).uniform(-3, 3):.1f}" cy="{300 - r * 0.5:.1f}" r="{r:.1f}" fill="{random.Random(x + 1).choice(["#2E3A3E", "#344244", "#283236"])}"/>')
    # the arch: legs land on the grounds (630 ft tall and wide)
    arch, body = gateway_arch(u, 300, 304, 208)
    out.append(arch)
    out.append(glow(300, 304, 30, "#FFC890", f"{u}-legs", 0.0))
    # levee: sloping cobbled riverbank with steps
    out.append(f'<path d="M -10 308 L 610 306 L 610 322 L -10 324 Z" fill="#6E5A6A"/>')
    out.append(f'<path d="M -10 308 L 610 306 L 610 309 L -10 311 Z" fill="#E8B08A" opacity="0.7"/>')
    out.append(dots(160, 44, (-10, 311, 610, 322), "#4A3A4E", r=(0.6, 1.4), opacity=(0.4, 0.8)))
    # Eads Bridge to the north (right): steel arches on stone piers
    piers = [(452, 324), (512, 324), (572, 324)]
    out.append('<rect x="420" y="296" width="200" height="5" fill="#3A3048"/>')
    for (px, py) in piers:
        out.append(f'<rect x="{px - 5}" y="300" width="10" height="{py - 300 + 2}" fill="#7A6A78"/><rect x="{px - 5}" y="300" width="4" height="{py - 300 + 2}" fill="#A88E92"/>')
    for x0, x1 in ((420, 452), (452, 512), (512, 572), (572, 632)):
        out.append(f'<path d="M {x0 + 5} 316 Q {(x0 + x1) / 2} 300 {x1 - 5} 316" stroke="#3A3048" stroke-width="2.5" fill="none"/>')
        out.append("".join(f'<line x1="{x0 + 5 + (x1 - x0 - 10) * t:.1f}" y1="301" x2="{x0 + 5 + (x1 - x0 - 10) * t:.1f}" y2="{316 - 16 * (1 - (2 * t - 1) ** 2) * 1:.1f}" stroke="#3A3048" stroke-width="1"/>' for t in (0.2, 0.35, 0.5, 0.65, 0.8)))
    # the river: sky colors, the arch's mirrored reflection broken by ripples
    out.append(f'<rect x="0" y="322" width="600" height="122" fill="url(#{u}-river)"/>')
    out.append(f'<g transform="translate(0 {2 * 322}) scale(1 -1)" opacity="0.32">{arch}</g>'.replace(f'id="{u}-a', f'id="{u}-r-a').replace(f'url(#{u}-a', f'url(#{u}-r-a'))
    out.append(mist(384, 384, 34, 70, "#FFE2A8", f"{u}-path", 0.3))
    out.append(ripples(260, 51, (0, 324, 600, 444), ["#2A2E50", "#3A3A62", "#5A5076"], w=(10, 50), h=(1, 2.2), opacity=(0.35, 0.8), persp=(322, 444)))
    out.append(ripples(120, 52, (330, 324, 440, 444), ["#FFE6B0", "#FFD08A", "#FFF2D0"], w=(4, 22), h=(0.8, 1.8), opacity=(0.5, 0.95), persp=(322, 444)))
    out.append(ripples(60, 53, (200, 324, 400, 400), ["#F8C8A0", "#E8A890"], w=(4, 14), h=(0.8, 1.6), opacity=(0.4, 0.8), persp=(322, 444)))
    # barge tow working upriver, right
    out.append('<g><rect x="420" y="352" width="44" height="7" fill="#3A2E3A"/><rect x="466" y="352" width="44" height="7" fill="#3A2E3A"/><rect x="420" y="349" width="90" height="3" fill="#6A4A4A"/>'
               '<rect x="420" y="355" width="90" height="4" fill="#1E1A28"/><rect x="420" y="352" width="90" height="1.2" fill="#FFB87A" opacity="0.7"/>'
               '<rect x="512" y="346" width="20" height="13" fill="#E8DCC8"/><rect x="516" y="338" width="12" height="8" fill="#E8DCC8"/><rect x="518" y="341" width="8" height="3" fill="#FFD88A"/>'
               '<path d="M 532 358 q 20 3 40 0" stroke="#F8D8B0" stroke-width="1.5" fill="none" opacity="0.7"/></g>')
    # sternwheeler heading downriver in the foreground, with its wake and reflection
    bx, by = 178, 404
    out.append(f'<g transform="translate(0 {2 * by}) scale(1 -1)" opacity="0.2">{riverboat(bx, by, 1.0, u)}</g>')
    out.append(ripples(40, 61, (bx - 80, by + 2, bx + 80, by + 40), ["#2A2E50", "#3A3A62"], w=(16, 40), h=(1.2, 2.2), opacity=(0.5, 0.9)))
    # foamy V wake spreading behind the paddle wheel
    rnd = random.Random(62)
    for side in (-1, 1):
        for i in range(14):
            t = i / 13
            x = bx + 78 + t * 150
            y = by - 2 + side * t * 18 + (6 if side > 0 else 2)
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{rnd.uniform(10, 20) * (1 - t * 0.4):.1f}" height="2.2" rx="1" fill="#FBE6C8" opacity="{0.9 * (1 - t) + 0.1:.2f}"/>')
    out.append(f'<ellipse cx="{bx + 82}" cy="{by + 1}" rx="12" ry="3" fill="#FBE6C8" opacity="0.6"/>')
    out.append(riverboat(bx, by, 1.0, u))
    # evening strollers on the levee
    for x, h, c in ((70, 13, "#3E3550"), (80, 12, "#5A3A52"), (240, 12, "#3E3550"), (396, 13, "#4A3A5A"), (560, 12, "#3E3550")):
        out.append(walker(x, 314, h, c, rim="#FFC890", rim_side=1, facing=-1 if x in (80, 396) else 1, tint=("#2A2236", 0.3)))
    out.append(gulls([(234, 150, 10), (252, 160, 7), (520, 140, 9)], "#3A2E50"))
    return "\n".join(out)


# ---------------------------------------------------------------- San Diego (Ocean Beach pier at golden hour)
def surfer(x, base, h, board="#F2E2C0", body="#2A2030", pose="ride", flip=1):
    """Painted surfer; pose 'ride' (on a wave), 'sit' (waiting on the board), 'walk' (board under the arm)."""
    p, k = {"ride": ("surf_ride", 1.25), "sit": ("surf_sit", 1.25), "walk": ("surfer", 1.2)}[pose]
    return F.person(x, base, h * k, p, flip, {"top": body, "top_kind": "swim", "bottom": body, "bottom_kind": "trousers", "board": board, "form": "m",
                                              "skin": "#B87A52", "hair_style": "short"}, seed=int(x + base), rim="#FFE2A8", light=-1, tint=("#4A3A50", 0.1))


def san_diego():
    u = "sd"
    C = Cam(f=360, cx=300, vpy=262, eye=4.0)
    out = [defs(
        lg(f"{u}-sky", [(0, "#5E86B8"), (0.35, "#A8A8C4"), (0.6, "#F0BE9C"), (0.85, "#FFD898"), (1, "#FFE8B4")], 0, 40, 0, 262, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#F6D6A0"), (0.12, "#8CB4B8"), (0.45, "#3E7E8E"), (1, "#2A5E70")], 0, 262, 0, 330, units="userSpaceOnUse"),
        lg(f"{u}-wave", [(0, "#2E6A7A"), (0.7, "#5EA4A6"), (1, "#9ED0C4")]),
        lg(f"{u}-wet", [(0, "#F6DCB4"), (0.5, "#E2BCA0"), (1, "#C8A086")], 0, 318, 0, 384, units="userSpaceOnUse"),
        lg(f"{u}-sand", [(0, "#E8C49A"), (1, "#D2A478")], 0, 380, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-deck", [(0, "#8A6A62"), (1, "#5A4250")]),
        lg(f"{u}-cl", [(0, "#FFF0D4"), (0.6, "#F6BCA0"), (1, "#B48EAE")]),
        lg(f"{u}-point", [(0, "#B49AB0"), (1, "#C8A8B0")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    sx, sy = 248, 214
    out.append(glow(sx, sy, 300, "#FFE2A0", f"{u}-sun", 0.95))
    out.append(f'<circle cx="{sx}" cy="{sy}" r="20" fill="#FFF6D8"/>')
    for x, y, w, h_ in ((110, 112, 150, 10), (450, 100, 180, 12), (520, 146, 100, 7), (150, 160, 90, 6), (380, 170, 70, 5)):
        out.append(f'<path d="M {x - w / 2} {y} q {w * 0.25} {-h_ * 1.4} {w * 0.5} {-h_ * 0.6} q {w * 0.2} {-h_ * 1.2} {w * 0.5} {h_ * 0.4} q {-w * 0.5} {h_ * 0.9} {-w} {h_ * 0.2} Z" fill="url(#{u}-cl)" opacity="0.85"/>')
        out.append(f'<path d="M {x - w / 2 + 8} {y + 1} q {w * 0.45} {h_ * 0.7} {w - 16} 0" stroke="#FFF2D0" stroke-width="1.5" fill="none" opacity="0.8"/>')
    # Point Loma, low and hazy to the south (left)
    out.append(f'<path d="M -10 262 L -10 246 Q 20 240 60 244 Q 110 250 150 258 Q 170 262 180 262 Z" fill="url(#{u}-point)"/>')
    out.append(f'<rect x="20" y="243" width="2" height="5" fill="#9A7E98"/>')
    # sea out to the horizon, sun glitter path
    out.append(f'<rect x="0" y="262" width="600" height="80" fill="url(#{u}-sea)"/>')
    out.append(ripples(200, 3, (sx - 70, 263, sx + 70, 330), ["#FFF2C8", "#FFE2A0", "#FFFFFF"], w=(3, 18), h=(0.6, 1.6), opacity=(0.5, 1), persp=(262, 340)))
    out.append(ripples(140, 4, (0, 264, 600, 320), ["#2A5E70", "#6AA4AE"], w=(8, 30), h=(0.6, 1.4), opacity=(0.3, 0.7), persp=(262, 340)))
    # sailboats far out
    for x, y, h in ((404, 262, 14), (430, 263, 10), (120, 263, 11)):
        out.append(f'<path d="M {x} {y - h} L {x} {y - 1} L {x + h * 0.55:.1f} {y - 2} Z" fill="#FFF6E2"/><path d="M {x - 1} {y - h * 0.8:.1f} L {x - 1} {y - 1} L {x - h * 0.4:.1f} {y - 2} Z" fill="#F2E2CC"/>'
                   f'<rect x="{x - h * 0.4:.1f}" y="{y - 1}" width="{h * 0.95:.1f}" height="1.6" fill="#5A5A70"/>')
    # rolling waves: (Z, height m, breaking stretch), far to near
    rnd = random.Random(8)
    waves = [(52, 0.9, (330, 610)), (36, 1.5, (-10, 210)), (26, 2.3, (-10, 250))]
    for i, (Z, hgt, brk) in enumerate(waves):
        y0 = C(0, 0, Z)[1]
        top = y0 - C.f * hgt / Z
        hh = y0 - top
        crest = [(x, top + hh * 0.18 * math.sin(x / 47 + i * 2) + hh * 0.08 * math.sin(x / 17 + i)) for x in range(-10, 611, 8)]
        gid = f"{u}-wf{i}"
        out.append(defs(lg(gid, [(0, "#8CCAC0"), (0.35, "#4E9AA0"), (1, "#2A6274")], 0, top, 0, y0, units="userSpaceOnUse")))
        out.append(f'<polygon points="{P(crest + [(610, y0 + 2), (-10, y0 + 2)])}" fill="url(#{gid})"/>')
        # light glowing through the thin lip
        out.append(f'<polyline points="{P(crest)}" fill="none" stroke="#C8F0E0" stroke-width="{1.2 + i:.1f}" opacity="0.7"/>')
        out.append(ripples(int(30 + i * 30), 20 + i, (0, top + hh * 0.3, 600, y0 - 1), ["#2A6274", "#86C4BC"], w=(6, 22), h=(0.8, 1.4), opacity=(0.4, 0.8)))
        out.append(ripples(24 + i * 10, 30 + i, (sx - 60, top + hh * 0.2, sx + 60, y0), ["#FFF2C8", "#FFFFFF"], w=(4, 14), h=(0.8, 1.6), opacity=(0.6, 1)))
        # the breaking section: tumbling white water over the crest with spray
        x0b, x1b = brk
        foam = []
        x = x0b
        while x < x1b:
            w = rnd.uniform(10, 26) * (1 + i * 0.4)
            yc = y_on(crest, min(max(x, -10), 600)) or top
            foam.append(f'<ellipse cx="{x:.1f}" cy="{yc + hh * 0.15:.1f}" rx="{w * 0.6:.1f}" ry="{hh * rnd.uniform(0.25, 0.45):.1f}"/>')
            x += w * 0.7
        out.append(f'<g fill="#FFF8EE" opacity="0.95">{"".join(foam)}</g>')
        out.append(dots(int(40 * (i + 1)), 40 + i, (x0b, top - hh * 0.5, x1b, top + hh * 0.2), "#FFFFFF", r=(0.6, 1.4 + i * 0.4), opacity=(0.5, 1)))
        # whitewater sheet rolling in ahead of the wave, irregular lace
        lace = [(x, y0 + 1 + rnd.uniform(1, 4) * (1 + i * 0.5)) for x in range(-10, 611, 14)]
        out.append(f'<polygon points="{P([(-10, y0 - 1)] + lace + [(610, y0 - 1)])}" fill="#F2FAF4" opacity="0.8"/>')
        out.append(blobs(int(12 + i * 8), 50 + i, (-10, y0 + 2, 610, y0 + 6 + i * 4), ["#F2FAF4"], r=(4, 14), opacity=(0.4, 0.8), squash=0.3))
        if i == 0:
            out.append(surfer(*C(-34, 0, Z), 9, pose="sit"))
            out.append(surfer(*C(-27, 0, Z * 1.04), 8, pose="sit", flip=-1))
        if i == 2:
            # rider on the green shoulder just ahead of the breaking curl
            x = 278
            yc = y_on(crest, x)
            out.append(f'<path d="M {x - 30} {yc + hh * 0.55:.1f} q -16 2 -32 -2" stroke="#FFF8EE" stroke-width="2" fill="none" opacity="0.9"/>')
            out.append(surfer(x, yc + hh * 0.5, 24, pose="ride"))
    # wet sand mirroring the sky and sun
    y_wet = C(0, 0, 22)[1]
    out.append(f'<rect x="0" y="{y_wet - 1:.1f}" width="600" height="{444 - y_wet + 1:.1f}" fill="url(#{u}-wet)"/>')
    out.append(f'<path d="M -10 {y_wet + 4:.1f} ' + "".join(f'Q {x + 30} {y_wet + 10 + 5 * math.sin(x):.1f} {x + 60} {y_wet + 5:.1f} ' for x in range(-10, 600, 60)) + f'L 610 {y_wet - 1:.1f} L -10 {y_wet - 1:.1f} Z" fill="#FFF4E2" opacity="0.7"/>')
    out.append(mist(sx, y_wet + 34, 50, 40, "#FFE6B0", f"{u}-wg", 0.7))
    out.append(ripples(70, 9, (sx - 40, y_wet + 6, sx + 40, 380), ["#FFF2C8", "#FFFFFF"], w=(6, 26), h=(1, 2), opacity=(0.5, 0.9)))
    # the pier: deck on concrete pilings marching out to sea (right side)
    X0, X1 = 15, 23
    piles = []
    for Z in [12 + 7 * i for i in range(60)]:
        for X in (X0 + 0.6, X1 - 0.6):
            piles.append((Z, X))
    for Z, X in sorted(piles, key=lambda p: -p[0]):
        x0, y0 = C(X - 0.45, 0, Z)
        x1, y1 = C(X + 0.45, 7.0, Z)
        out.append(f'<rect x="{x0:.1f}" y="{y1:.1f}" width="{max(0.8, x1 - x0):.1f}" height="{y0 - y1:.1f}" fill="#4A3A4A"/>')
        out.append(f'<rect x="{x0:.1f}" y="{y1:.1f}" width="{max(0.5, (x1 - x0) * 0.35):.1f}" height="{y0 - y1:.1f}" fill="#E8B08A" opacity="0.55"/>')
        # crossbracing under the deck
        if X < X1 - 1:
            xb, yb = C(X1 - 0.6, 5.0, Z)
            xa, ya = C(X, 6.4, Z)
            out.append(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" stroke="#3A2E3E" stroke-width="{max(0.5, C.f * 0.2 / Z):.1f}"/>')
        # foam ringing the pile at the waterline
        if Z > 22:
            out.append(f'<ellipse cx="{(x0 + x1) / 2:.1f}" cy="{y0:.1f}" rx="{max(1, (x1 - x0) * 1.4):.1f}" ry="{max(0.6, (x1 - x0) * 0.4):.1f}" fill="#FFF6E6" opacity="0.8"/>')
        else:  # reflection in the wet sand
            out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{max(0.8, x1 - x0):.1f}" height="{(y0 - y1) * 0.5:.1f}" fill="#4A3A4A" opacity="0.25"/>')
    # deck underside, fascia, railing
    out.append(f'<polygon points="{P([C(X0, 7, 10), C(X0, 7, 480), C(X1, 7, 480), C(X1, 7, 10)])}" fill="#3A2E3E"/>')
    out.append(f'<polygon points="{P(C.quad_x(X0, 10, 480, 7, 8.2))}" fill="url(#{u}-deck)"/>')
    out.append(f'<polygon points="{P(C.quad_x(X0, 10, 480, 7.9, 8.2))}" fill="#FFD8A8" opacity="0.7"/>')
    rail = C.quad_x(X0 + 0.2, 10, 480, 9.2, 9.35)
    out.append(f'<polygon points="{P(rail)}" fill="#E8D0C0"/>')
    for Z in [10 * 1.06 ** i for i in range(70)]:
        if Z > 480:
            break
        a_, b_ = C(X0 + 0.2, 8.2, Z), C(X0 + 0.2, 9.3, Z)
        out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#E8D0C0" stroke-width="{max(0.5, C.f * 0.08 / Z):.1f}"/>')
    # lamp posts and anglers on the pier
    for Z in (18, 30, 46, 70, 105, 160, 240, 360):
        a_, b_ = C(X0 + 0.5, 8.2, Z), C(X0 + 0.5, 12.5, Z)
        out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#3A2E3E" stroke-width="{max(0.6, C.f * 0.15 / Z):.1f}"/>')
        out.append(f'<circle cx="{b_[0]:.1f}" cy="{b_[1]:.1f}" r="{max(1, C.f * 0.35 / Z):.1f}" fill="#FFF0C8"/>')
    for Z, h, col in ((26, 1.75, "#3E4A6A"), (38, 1.7, "#B8574A"), (56, 1.7, "#2E3A4E"), (90, 1.7, "#5A3A52")):
        x, b = C(X0 + 0.8, 8.2, Z)
        hh = C.f * h / Z
        out.append(walker(x, b, hh, col, rim="#FFD8A0", rim_side=-1, pose="stand_side", facing=-1, tint=("#4A3A50", 0.2)))
        rx, ry = x - hh * 1.6, b - hh * 1.3
        out.append(f'<path d="M {x - hh * 0.1:.1f} {b - hh * 0.6:.1f} L {rx:.1f} {ry:.1f}" stroke="#2A2030" stroke-width="{max(0.7, hh * 0.04):.1f}"/>'
                   f'<path d="M {rx:.1f} {ry:.1f} Q {rx - hh * 0.3:.1f} {b:.1f} {rx - hh * 0.2:.1f} {C(0, 0, Z)[1] + 4:.1f}" stroke="#FFF6E6" stroke-width="0.6" fill="none" opacity="0.35"/>')
    # cafe at the end of the pier
    q = C.quad_x(X0 + 1, 400, 470, 8.2, 12)
    out.append(f'<polygon points="{P(q)}" fill="#E8D8C8"/>')
    # dry sand foreground: texture, kelp, footprints, a surfer heading in
    y_dry = C(0, 0, 13)[1]
    out.append(f'<path d="M -10 {y_dry:.1f} Q 200 {y_dry - 6:.1f} 380 {y_dry + 2:.1f} T 610 {y_dry - 2:.1f} L 610 444 L -10 444 Z" fill="url(#{u}-sand)"/>')
    out.append(dots(500, 71, (-10, y_dry, 610, 444), "#B88A68", r=(0.5, 1.4), opacity=(0.3, 0.7)))
    out.append(dots(200, 72, (-10, y_dry, 610, 444), "#FFF0D8", r=(0.5, 1.2), opacity=(0.4, 0.8)))
    out.append('<g fill="none" stroke="#5A4A3A" stroke-width="1.8" stroke-linecap="round" opacity="0.7"><path d="M 60 396 q 10 -4 20 0 q 8 4 18 -2"/><path d="M 420 388 q 12 3 24 -1"/><path d="M 92 426 q 8 -3 16 0"/></g>')
    for i in range(9):
        fx, fy = 210 + i * 9 + (i % 2) * 5, 440 - i * 7
        out.append(f'<ellipse cx="{fx}" cy="{fy}" rx="2.6" ry="1.6" fill="#B88A68" opacity="0.7"/>')
    out.append(f'<ellipse cx="300" cy="392" rx="16" ry="3" fill="#8A6A58" opacity="0.4"/>')
    out.append(surfer(302, 392, 58, board="#F6E8C8", body="#3A2A36", pose="walk"))
    out.append('<path d="M 297 336 L 297 340" stroke="#000" stroke-width="0"/>')
    # a board planted in the sand, left foreground
    out.append('<path d="M 112 430 L 106 352 Q 112 336 120 352 L 122 430 Z" fill="#E86A4A"/><path d="M 113 430 L 112 350 L 114 344" stroke="#FFF4E0" stroke-width="2" fill="none"/>'
               '<path d="M 106 352 Q 112 336 113 344 L 109 430 L 106 430 Z" fill="#FFB88A" opacity="0.5"/><ellipse cx="128" cy="432" rx="18" ry="3" fill="#8A6A58" opacity="0.4"/>')
    out.append(gulls([(330, 150, 11), (350, 160, 8), (180, 130, 9)], "#4A3A50"))
    return "\n".join(out)


# ---------------------------------------------------------------- Portland (Hawthorne Bridge and Mount Hood at alpenglow)
def portland():
    u = "pd"
    C = Cam(f=420, cx=300, vpy=286, eye=10.0)
    out = [defs(
        # east-facing dusk: blue earth shadow at the horizon, the pink Belt of Venus above it
        lg(f"{u}-sky", [(0, "#3A4A86"), (0.35, "#7484B8"), (0.6, "#C8A0BE"), (0.75, "#F2B6B0"), (0.86, "#E0A8B4"), (1, "#8E8EBE")], 0, 40, 0, 286, units="userSpaceOnUse"),
        lg(f"{u}-snow", [(0, "#FFE0D0"), (0.5, "#F8B8B0"), (1, "#C8A0C0")]),
        lg(f"{u}-rock", [(0, "#8A7A9E"), (1, "#6E6A96")]),
        lg(f"{u}-hills", [(0, "#4A5A84"), (1, "#3A4870")]),
        lg(f"{u}-river", [(0, "#E8B4B8"), (0.3, "#9A9AC4"), (1, "#3A4A78")], 0, 286, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-steel", [(0, "#3E8A6E"), (1, "#2A6A54")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(16, 3, (60, 44, 560, 100), "#FFFFFF", r=(0.6, 1.2), opacity=(0.4, 0.9)))
    # Mount Hood: asymmetric cone, summit a little left, glaciers glowing pink on the west face
    mx, my = 352, 118
    cone = rough([(120, 262), (200, 222), (270, 176), (318, 140), (mx, my), (372, 132), (410, 168), (470, 208), (560, 252), (600, 262)], 5, amp=5, depth=4)
    out.append(f'<polygon points="{P(cone + [(600, 290), (120, 290)])}" fill="url(#{u}-rock)"/>')
    snow = rough([(150, 250), (210, 214), (272, 176), (318, 140), (mx, my), (372, 132), (410, 168), (468, 206), (540, 246),
                  (500, 236), (470, 250), (440, 232), (410, 252), (382, 226), (360, 256), (338, 224), (310, 252), (284, 226), (258, 248), (228, 232), (196, 254)], 15, amp=5, depth=3)
    out.append(f'<polygon points="{P(snow)}" fill="url(#{u}-snow)"/>')
    cid = f"{u}-sn"
    g = [f'<polygon points="{P([(mx, my), (372, 132), (410, 168), (470, 208), (540, 246), (500, 250), (420, 240), (380, 200)])}" fill="#9A86B4" opacity="0.45"/>']
    rnd = random.Random(4)
    for _ in range(26):  # ridges and crevasse lines raking down from the summit
        x = rnd.uniform(200, 520)
        g.append(f'<path d="M {mx + (x - mx) * 0.15:.1f} {my + 14 + rnd.uniform(0, 14):.1f} Q {(mx + x) / 2 + rnd.uniform(-10, 10):.1f} {my + 60:.1f} {x:.1f} {rnd.uniform(220, 260):.1f}" stroke="{rnd.choice(["#B48AA8", "#FFF0E6"])}" stroke-width="{rnd.uniform(1, 2.4):.1f}" fill="none" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>')
    out.append(f'<clipPath id="{cid}"><polygon points="{P(snow)}"/></clipPath><g clip-path="url(#{cid})">{"".join(g)}</g>')
    out.append(f'<polyline points="{P([p for p in cone if p[0] <= mx + 1])}" fill="none" stroke="#FFE8DC" stroke-width="1.8" opacity="0.8"/>')
    # wisp of cloud on the shoulder
    out.append(f'<path d="M 420 186 q 30 -8 70 -2 q 20 4 40 0 q -40 10 -110 2 Z" fill="#F8D0C8" opacity="0.6"/>')
    # forested foothills of the Cascades
    poly, h1 = ridge_poly([(-10, 252), (90, 244), (180, 256), (260, 246), (360, 258), (460, 248), (610, 256)], 7, base=292, amp=4, fill=f"url(#{u}-hills)")
    out.append(poly)
    out.append(tree_line(h1, 8, ["#3E4C76", "#46557E"], density=1.6, hmin=4, hmax=9))
    # east-side city: warehouses, the two glass spires of the convention center, lit windows
    rnd = random.Random(21)
    x = -10
    while x < 610:
        w = rnd.uniform(18, 44)
        h = rnd.uniform(8, 26)
        col = rnd.choice(["#5A5A86", "#525280", "#625E8C"])
        out.append(f'<rect x="{x:.1f}" y="{284 - h:.1f}" width="{w:.1f}" height="{h + 4:.1f}" fill="{col}"/>')
        for yy in range(int(284 - h + 4), 284, 5):
            for xx in range(int(x + 3), int(x + w - 3), 5):
                if rnd.random() < 0.3:
                    out.append(f'<rect x="{xx}" y="{yy}" width="2.2" height="2" fill="#FFD89A" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
        x += w + rnd.uniform(0, 6)
    for sx_ in (468, 486):
        out.append(f'<polygon points="{P([(sx_ - 5, 266), (sx_, 214), (sx_ + 5, 266)])}" fill="#7A8EB4"/><polygon points="{P([(sx_, 214), (sx_ + 5, 266), (sx_ + 1, 266)])}" fill="#5A6A98"/>')
    out.append(f'<rect x="452" y="262" width="52" height="24" fill="#4E5480"/>')
    # river
    out.append(f'<rect x="0" y="286" width="600" height="158" fill="url(#{u}-river)"/>')
    out.append(mist(350, 300, 140, 26, "#FFC8C0", f"{u}-hr", 0.45))
    out.append(ripples(240, 33, (0, 288, 600, 444), ["#5A6A9E", "#7A84B4", "#4A5A8A"], w=(10, 50), h=(1, 2.2), opacity=(0.4, 0.8), persp=(286, 444)))
    out.append(ripples(90, 34, (0, 288, 600, 380), ["#FFD8D0", "#F8C0C0"], w=(6, 24), h=(0.8, 1.6), opacity=(0.4, 0.8), persp=(286, 444)))
    # the Hawthorne Bridge receding toward the east bank: green Pratt trusses and the two lift towers
    ang = math.radians(152)
    dx, dz = math.cos(ang), math.sin(ang)
    nx, nz = -dz, dx
    X0, Z0 = 120, 84
    NEAR, FAR = (7, -7) if nz < 0 else (-7, 7)

    def W(s, off, Y):  # point along the bridge axis s (m), lateral offset, height
        return C(X0 + s * dx + off * nx, Y, Z0 + s * dz + off * nz)
    deck, tp = 14.0, 24.0
    spans = [(0, 64), (64, 128), (128, 186), (186, 236), (236, 300), (300, 364), (364, 430)]
    lift = 3
    for side, op in ((FAR, 0.55), (NEAR, 1.0)):  # far truss first (dimmer), near truss on top
        for k, (s0, s1) in enumerate(spans):
            hh = tp if k != lift else deck + 7
            sw = lambda s: max(0.7, C.f * 0.45 / (Z0 + s * dz))
            bot = [W(s0 + (s1 - s0) * i / 8, side, deck) for i in range(9)]
            top = [W(s0 + (s1 - s0) * i / 8, side, hh if 0 < i < 8 else deck + 3) for i in range(9)]
            col = "#2E6E58" if op < 1 else "#3E9474"
            out.append(f'<g stroke="{col}" fill="none" opacity="{op}" stroke-linecap="round">'
                       f'<polyline points="{P(top)}" stroke-width="{sw(s0) * 1.4:.1f}"/>'
                       + "".join(f'<line x1="{bot[i][0]:.1f}" y1="{bot[i][1]:.1f}" x2="{top[i][0]:.1f}" y2="{top[i][1]:.1f}" stroke-width="{sw(s0) * 0.8:.1f}"/>' for i in range(1, 8))
                       + "".join(f'<line x1="{top[i][0]:.1f}" y1="{top[i][1]:.1f}" x2="{bot[i + 1][0]:.1f}" y2="{bot[i + 1][1]:.1f}" stroke-width="{sw(s0) * 0.7:.1f}"/>' for i in range(0, 4))
                       + "".join(f'<line x1="{top[i + 1][0]:.1f}" y1="{top[i + 1][1]:.1f}" x2="{bot[i][0]:.1f}" y2="{bot[i][1]:.1f}" stroke-width="{sw(s0) * 0.7:.1f}"/>' for i in range(4, 8))
                       + "</g>")
        if side == FAR:
            # deck slab between the trusses
            out.append(f'<polygon points="{P([W(0, NEAR, deck), W(430, NEAR, deck), W(430, NEAR, deck - 1.6), W(0, NEAR, deck - 1.6)])}" fill="#2A3050"/>')
            out.append(f'<polygon points="{P([W(0, NEAR, deck), W(430, NEAR, deck), W(430, NEAR, deck - 0.4), W(0, NEAR, deck - 0.4)])}" fill="#C8384A"/>')
    # concrete piers with cutwaters, and the lift towers with their counterweights
    for s in (0, 64, 128, 186, 236, 300, 364, 430):
        a_, b_ = W(s, -8, 0), W(s, -8, deck - 1.6)
        c_ = W(s, 8, 0)
        w_ = max(2, C.f * 4 / (Z0 + s * dz))
        out.append(f'<rect x="{b_[0] - w_ / 2:.1f}" y="{b_[1]:.1f}" width="{w_:.1f}" height="{a_[1] - b_[1]:.1f}" fill="#B8A8BE"/><rect x="{b_[0]:.1f}" y="{b_[1]:.1f}" width="{w_ / 2:.1f}" height="{a_[1] - b_[1]:.1f}" fill="#7A6E92"/>')
        out.append(f'<ellipse cx="{a_[0]:.1f}" cy="{a_[1]:.1f}" rx="{w_ * 0.9:.1f}" ry="{w_ * 0.18:.1f}" fill="#E8D8E8" opacity="0.5"/>')
    for s in (186, 236):
        for side in (FAR, NEAR):
            b_, t_ = W(s, side, deck - 1), W(s, side, 52)
            w_ = max(2.4, C.f * 2.6 / (Z0 + s * dz))
            col, lit = ("#2A6450", "#2A6450") if side == FAR else ("#3E9474", "#7ED0A8")
            body = [(b_[0] - w_, b_[1]), (t_[0] - w_ * 0.75, t_[1]), (t_[0] + w_ * 0.75, t_[1]), (b_[0] + w_, b_[1])]
            out.append(f'<polygon points="{P(body)}" fill="none" stroke="{col}" stroke-width="{max(1.4, w_ * 0.4):.1f}" stroke-linejoin="round"/>')
            n = 8
            xl = lambda t: b_[0] + (t_[0] - b_[0]) * t
            hw = lambda t: w_ * (1 - 0.25 * t)
            for i in range(n):
                ta, tb = i / n, (i + 1) / n
                ya = b_[1] + (t_[1] - b_[1]) * ta
                yb = b_[1] + (t_[1] - b_[1]) * tb
                out.append(f'<path d="M {xl(ta) - hw(ta):.1f} {ya:.1f} L {xl(tb) + hw(tb):.1f} {yb:.1f} M {xl(ta) + hw(ta):.1f} {ya:.1f} L {xl(tb) - hw(tb):.1f} {yb:.1f} M {xl(tb) - hw(tb):.1f} {yb:.1f} L {xl(tb) + hw(tb):.1f} {yb:.1f}" stroke="{col}" stroke-width="{max(0.8, w_ * 0.22):.1f}"/>')
            out.append(f'<line x1="{b_[0] - w_:.1f}" y1="{b_[1]:.1f}" x2="{t_[0] - w_ * 0.75:.1f}" y2="{t_[1]:.1f}" stroke="{lit}" stroke-width="{max(0.8, w_ * 0.18):.1f}" opacity="0.8"/>')
            cw = W(s, side, 45)
            out.append(f'<rect x="{cw[0] - w_ * 1.2:.1f}" y="{cw[1]:.1f}" width="{w_ * 2.4:.1f}" height="{w_ * 2.4:.1f}" fill="#4E5A66"/><rect x="{cw[0] - w_ * 1.2:.1f}" y="{cw[1]:.1f}" width="{w_ * 0.6:.1f}" height="{w_ * 2.4:.1f}" fill="#8A96A6"/>')
            out.append(f'<rect x="{t_[0] - w_ * 1.1:.1f}" y="{t_[1] - w_ * 0.7:.1f}" width="{w_ * 2.2:.1f}" height="{w_ * 0.7:.1f}" fill="#C8384A"/>')
        # sheaves and the overhead tie between the two towers
        a1, a2 = W(s, FAR, 52), W(s, NEAR, 52)
        out.append(f'<line x1="{a1[0]:.1f}" y1="{a1[1]:.1f}" x2="{a2[0]:.1f}" y2="{a2[1]:.1f}" stroke="#2A6450" stroke-width="2"/>')
        lt = W(s, NEAR, 52)
        out.append(glow(lt[0], lt[1] - 4, 8, "#FF6A6A", f"{u}-tl{s}", 0.8) + f'<circle cx="{lt[0]:.1f}" cy="{lt[1] - 4:.1f}" r="1.5" fill="#FF8080"/>')
    for s_ in (186, 236):
        for side in (FAR, NEAR):
            b_ = W(s_, side, 0)
            out.append(ripples(16, int(s_) + side, (b_[0] - 3, b_[1] + 4, b_[0] + 3, b_[1] + 50), ["#3E9474", "#2A6450"], w=(3, 8), h=(1, 1.6), opacity=(0.4, 0.8)))
    # lamps along the deck
    for s in range(10, 430, 26):
        p_ = W(s, NEAR * 1.07, deck + 4)
        out.append(f'<circle cx="{p_[0]:.1f}" cy="{p_[1]:.1f}" r="{max(0.9, C.f * 0.4 / (Z0 + s * dz)):.1f}" fill="#FFE8B0"/>')
        out.append(glow(p_[0], p_[1], max(4, C.f * 3 / (Z0 + s * dz)), "#FFE0A0", f"{u}-dl{s}", 0.5))
        r_ = W(s, NEAR * 1.07, 0)
        out.append(f'<rect x="{r_[0] - 0.8:.1f}" y="{r_[1] + 2:.1f}" width="1.6" height="{max(4, C.f * 8 / (Z0 + s * dz)):.1f}" fill="#FFE0A0" opacity="0.35"/>')
    # a rowing eight sliding upstream
    rx, ry = 262, 352
    out.append(f'<path d="M {rx - 70} {ry} L {rx + 74} {ry - 1} L {rx + 70} {ry + 2} L {rx - 66} {ry + 2} Z" fill="#F0E6D8"/>')
    for i in range(8):
        x_ = rx - 52 + i * 14
        out.append(f'<line x1="{x_ - 2}" y1="{ry - 3}" x2="{x_ - 14}" y2="{ry + 9}" stroke="#2A2E48" stroke-width="1.2"/><rect x="{x_ - 17}" y="{ry + 8}" width="5" height="2.2" fill="#C8384A"/>'
                   + F.person(x_, ry - 0.5, 21, "paddle", 1, {"top": ["#C8384A", "#2A2E48"][i % 2], "top_kind": "tank", "bottom": "#2A2E48", "no_legs": True, "form": "fm"[i % 2]},
                              seed=60 + i, rim="#FFE8D8", light=-1, shadow=0))
    out.append(F.person(rx + 62, ry - 0.5, 18, "sit", -1, {"top": "#2A2E48", "no_legs": True, "hat_kind": "cap", "hat": "#C8384A"}, seed=69, rim="#FFE8D8", light=-1, shadow=0))
    out.append(f'<path d="M {rx - 70} {ry + 3} q -40 3 -90 1" stroke="#E8E0F0" stroke-width="1.6" fill="none" opacity="0.6"/>')
    out.append(f'<g opacity="0.25"><rect x="{rx - 66}" y="{ry + 3}" width="136" height="3" fill="#F0E6D8"/></g>')
    # west-bank waterfront: seawall, railing, path, a cyclist, and the rose garden in bloom
    out.append(f'<path d="M -10 400 L 610 392 L 610 444 L -10 444 Z" fill="#5A5A6E"/>')
    out.append(f'<path d="M -10 400 L 610 392 L 610 397 L -10 405 Z" fill="#B8A8B8"/>')
    out.append(f'<path d="M -10 410 L 610 403 L 610 444 L -10 444 Z" fill="#7A7486"/>')
    out.append(dots(160, 91, (-10, 404, 610, 420), "#5E586E", r=(0.6, 1.4), opacity=(0.4, 0.8)))
    out.append('<g stroke="#2A2A3E" stroke-width="2">' + "".join(f'<line x1="{x}" y1="{400 - x * 8 / 620 - 1:.1f}" x2="{x}" y2="{400 - x * 8 / 620 - 16:.1f}"/>' for x in range(0, 610, 22)) + "</g>")
    out.append('<path d="M -10 384 L 610 376" stroke="#2A2A3E" stroke-width="2.6"/>')
    for lx in (80, 380):
        ly = 400 - lx * 8 / 620
        out.append(f'<rect x="{lx - 1.5}" y="{ly - 70:.1f}" width="3" height="70" fill="#20243A"/><path d="M {lx - 7} {ly - 70:.1f} L {lx + 7} {ly - 70:.1f} L {lx + 4} {ly - 80:.1f} L {lx - 4} {ly - 80:.1f} Z" fill="#20243A"/>')
        out.append(glow(lx, ly - 66, 26, "#FFE2A0", f"{u}-wl{lx}", 0.8) + f'<rect x="{lx - 4}" y="{ly - 70:.1f}" width="8" height="6" fill="#FFF0C8"/>')
    # cyclist
    cx_, cy_ = 470, 404
    out.append(F.person(cx_, cy_ + 8, 44, "cyclist", 1, {"top": "#E8A040", "bottom": "#20243A", "bottom_kind": "trousers", "accent": "#20243A",
                                                     "hat_kind": "helmet", "hat": "#C8384A"}, seed=21, rim="#FFE2A0", light=-1))
    # roses: dense bushes across the foreground with pink and red blooms
    rnd = random.Random(77)
    leaves = []
    for _ in range(200):
        x = rnd.uniform(-20, 620)
        y = rnd.uniform(416, 452) - max(0, 120 - x) * 0.12 + max(0, x - 330) * 0.03
        r = rnd.uniform(6, 13)
        leaves.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 0.7:.1f}" fill="{rnd.choice(["#2E4A3A", "#365A42", "#284034", "#3E6248"])}"/>')
    out.append("".join(leaves))
    for _ in range(66):
        x = rnd.uniform(-10, 610)
        y = rnd.uniform(412, 446) - max(0, 120 - x) * 0.12 + max(0, x - 330) * 0.03
        r = rnd.uniform(3.4, 6)
        c1, c2 = rnd.choice([("#E8607A", "#FFB0BC"), ("#C8384A", "#F2808A"), ("#F49AA8", "#FFE0E4"), ("#E87A5A", "#FFC0A0")])
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{c1}"/><path d="M {x - r * 0.6:.1f} {y:.1f} q {r * 0.6:.1f} {-r * 0.9:.1f} {r * 1.2:.1f} 0" stroke="{c2}" stroke-width="{r * 0.35:.1f}" fill="none"/>'
                   f'<circle cx="{x + r * 0.1:.1f}" cy="{y + r * 0.15:.1f}" r="{r * 0.3:.1f}" fill="{c2}" opacity="0.8"/>')
    out.append(gulls([(150, 130, 10), (168, 140, 7)], "#3A3E66"))
    return "\n".join(out)


# ---------------------------------------------------------------- Maui (sunrise above the clouds on Haleakala)
def silversword(x, base, r, seed, bloom=0.0, rim="#FFC890"):
    """Haleakala silversword: a globe of silvery curved sword leaves; bloom > 0 adds the tall flowering stalk."""
    rnd = random.Random(seed)
    out = []
    if bloom:
        H = r * bloom
        out.append(f'<path d="M {x - r * 0.22:.1f} {base - r * 0.9:.1f} Q {x - r * 0.3:.1f} {base - H * 0.6:.1f} {x:.1f} {base - H:.1f} Q {x + r * 0.3:.1f} {base - H * 0.6:.1f} {x + r * 0.22:.1f} {base - r * 0.9:.1f} Z" fill="#7A6A5A"/>')
        for i in range(36):
            t = i / 35
            yy = base - r * 0.9 - (H - r * 0.9) * t
            w = r * 0.32 * (1 - t) ** 0.6 + 1
            side = -1 if i % 2 else 1
            out.append(f'<ellipse cx="{x + side * w * rnd.uniform(0.3, 1):.1f}" cy="{yy:.1f}" rx="{max(1.2, r * 0.07):.1f}" ry="{max(1, r * 0.055):.1f}" fill="{rnd.choice(["#8A2E4E", "#A63E5E", "#6E2440", "#C8668A"])}"/>')
    leaves = []
    for i in range(46):
        a = math.radians(rnd.uniform(-180, 0) if i % 4 else rnd.uniform(-200, 20))
        L = r * rnd.uniform(0.75, 1.05)
        ex, ey = x + L * math.cos(a), base - r * 0.55 + L * math.sin(a) * 0.9
        cxp, cyp = x + L * 0.6 * math.cos(a) - math.sin(a) * r * 0.12, base - r * 0.55 + L * 0.6 * math.sin(a) * 0.9 - r * 0.15
        lit = math.cos(a) > 0.1
        col = rnd.choice(["#D8DCE2", "#C2C8D2", "#E8ECF0"]) if lit else rnd.choice(["#9AA2B4", "#8A90A6", "#AEB4C4"])
        leaves.append((math.sin(a), f'<path d="M {x:.1f} {base - r * 0.45:.1f} Q {cxp:.1f} {cyp:.1f} {ex:.1f} {ey:.1f}" stroke="{col}" stroke-width="{max(1.2, r * 0.09):.1f}" fill="none" stroke-linecap="round"/>'))
        if lit and rnd.random() < 0.5:
            leaves.append((math.sin(a) + 0.01, f'<path d="M {cxp:.1f} {cyp:.1f} Q {(cxp + ex) / 2:.1f} {(cyp + ey) / 2 - 1:.1f} {ex:.1f} {ey:.1f}" stroke="{rim}" stroke-width="{max(0.8, r * 0.035):.1f}" fill="none" opacity="0.8"/>'))
    out.append(f'<ellipse cx="{x:.1f}" cy="{base - r * 0.45:.1f}" rx="{r * 0.7:.1f}" ry="{r * 0.5:.1f}" fill="#6A6E86"/>')
    out += [p for _, p in sorted(leaves, key=lambda t: -t[0])]
    return "".join(out)


def cinder_cone(u, k, cx, base, w, h, c_lit, c_shade, seed):
    """Rounded cinder cone with a summit crater dimple; lit on the east (right, toward sunrise), erosion gullies."""
    a, b = cx - w / 2, cx + w / 2
    d = (f'M {a:.1f} {base:.1f} C {cx - w * 0.3:.1f} {base - h * 0.25:.1f} {cx - w * 0.22:.1f} {base - h:.1f} {cx - w * 0.1:.1f} {base - h:.1f} '
         f'Q {cx:.1f} {base - h * 0.9:.1f} {cx + w * 0.1:.1f} {base - h:.1f} C {cx + w * 0.22:.1f} {base - h:.1f} {cx + w * 0.3:.1f} {base - h * 0.25:.1f} {b:.1f} {base:.1f} Z')
    cid = f"{u}-cc{k}"
    out = [defs(lg(f"{u}-ccg{k}", [(0, c_shade), (0.45, c_shade), (0.7, c_lit), (1, c_lit)], 0, 0, 1, 0))]
    out.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
    out.append(f'<path d="{d}" fill="url(#{u}-ccg{k})"/>')
    rnd = random.Random(seed)
    gul = "".join(f'<path d="M {cx + t * w * 0.12:.1f} {base - h * 0.9:.1f} Q {cx + t * w * 0.3:.1f} {base - h * 0.5:.1f} {cx + t * w * 0.5:.1f} {base:.1f}" stroke="{rnd.choice(["#3A1E26", "#5A2E2E"]) if t < 0.2 else "#FFC890"}" stroke-width="{rnd.uniform(0.8, 1.8):.1f}" fill="none" opacity="{rnd.uniform(0.25, 0.5):.2f}"/>'
                  for t in [rnd.uniform(-1, 1) for _ in range(int(w / 6))])
    out.append(f'<g clip-path="url(#{cid})">{gul}' + dots(int(w * h / 30), seed, (a, base - h, b, base), "#2A1A20", r=(0.5, 1.2), opacity=(0.2, 0.5)) + "</g>")
    out.append(f'<ellipse cx="{cx:.1f}" cy="{base - h * 0.94:.1f}" rx="{w * 0.08:.1f}" ry="{max(1.2, h * 0.05):.1f}" fill="{c_shade}" opacity="0.8"/>')
    out.append(f'<path d="M {cx + w * 0.1:.1f} {base - h:.1f} C {cx + w * 0.22:.1f} {base - h:.1f} {cx + w * 0.3:.1f} {base - h * 0.25:.1f} {b:.1f} {base:.1f}" fill="none" stroke="#FFC890" stroke-width="1.4" opacity="0.7"/>')
    out.append(f'<ellipse cx="{cx + w * 0.1:.1f}" cy="{base:.1f}" rx="{w * 0.6:.1f}" ry="{h * 0.08:.1f}" fill="#2A1A22" opacity="0.25"/>')
    return "".join(out)


def lava_rocks(n, seed, box):
    """Angular chunks of lava rock with a lit top facet (sun ahead-right) and a dark base."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(5, 16) * (0.6 + 0.6 * (y - y0) / (y1 - y0))
        pts = [(x + r * math.cos(a) * rnd.uniform(0.7, 1.1), y + r * 0.6 * math.sin(a) * rnd.uniform(0.7, 1.1) - (r * 0.4 if math.sin(a) < 0 else 0))
               for a in [math.radians(d + rnd.uniform(-15, 15)) for d in range(0, 360, 50)]]
        out.append(f'<polygon points="{P(pts)}" fill="{rnd.choice(["#3A2228", "#4A2A2E", "#2E1C22"])}"/>')
        top = [p for p in pts if p[1] < y - r * 0.1]
        if len(top) >= 2:
            top = sorted(top)
            out.append(f'<polyline points="{P(top)}" fill="none" stroke="#C87A5A" stroke-width="1.4" opacity="0.7"/>')
    return "".join(out)


def maui():
    u = "mu"
    out = [defs(
        lg(f"{u}-sky", [(0, "#1E1E4E"), (0.3, "#3E3478"), (0.55, "#9A4A86"), (0.75, "#E8786A"), (0.9, "#FFB45E"), (1, "#FFE08A")], 0, 40, 0, 214, units="userSpaceOnUse"),
        lg(f"{u}-cl", [(0, "#8A6A9E"), (0.5, "#D892A2"), (1, "#FFD2A0")], 120, 0, 460, 0, units="userSpaceOnUse"),
        lg(f"{u}-cl2", [(0, "#6A5A8E"), (0.5, "#B87A9A"), (1, "#F8B896")], 0, 0, 600, 0, units="userSpaceOnUse"),
        lg(f"{u}-rim", [(0, "#5A2E3E"), (1, "#3A2232")]),
        lg(f"{u}-floor", [(0, "#6A4050"), (1, "#3A2434")]),
        lg(f"{u}-fg", [(0, "#4A2A2E"), (1, "#24161C")]),
        lg(f"{u}-kea", [(0, "#7A5A8E"), (1, "#B87A9A")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(50, 2, (0, 42, 600, 120), "#FFFFFF", r=(0.5, 1.3), opacity=(0.3, 0.9)))
    # the sun just breaking the cloud horizon
    sx, sy = 372, 214
    out.append(glow(sx, sy, 320, "#FFD68A", f"{u}-sun", 0.95))
    out.append(f'<clipPath id="{u}-sc"><rect x="0" y="0" width="600" height="{sy}"/></clipPath><circle cx="{sx}" cy="{sy + 6}" r="24" fill="#FFF4D0" clip-path="url(#{u}-sc)"/>')
    out.append(f'<g fill="#FFE6A8" opacity="0.06">' + "".join(
        f'<polygon points="{P([(sx, sy), (sx + 260 * math.cos(math.radians(a - 2.5)), sy + 260 * math.sin(math.radians(a - 2.5))), (sx + 260 * math.cos(math.radians(a + 2.5)), sy + 260 * math.sin(math.radians(a + 2.5)))])}"/>' for a in (200, 222, 246, 270, 291, 318, 340)) + "</g>")
    # thin high cloud bands catching first light
    for x, y, w in ((150, 128, 180), (470, 116, 160), (300, 160, 120), (90, 176, 90)):
        out.append(f'<path d="M {x - w / 2} {y} q {w / 2} -10 {w} 0 q {-w / 2} 5 {-w} 0 Z" fill="#F8A88A" opacity="0.55"/>')
    # Mauna Kea and Mauna Loa on the Big Island, floating above the cloud sea far to the southeast
    out.append(f'<path d="M 470 216 Q 500 196 520 194 Q 540 196 572 214 Z" fill="url(#{u}-kea)" opacity="0.8"/><path d="M 540 216 Q 580 202 620 206 L 620 216 Z" fill="url(#{u}-kea)" opacity="0.7"/>')
    # the sea of clouds: overlapping rows of billows, each row lit on top and violet underneath
    out.append(f'<rect x="0" y="212" width="600" height="80" fill="#B88AA6"/>')
    rnd = random.Random(5)
    rows = ((214, 16, 3.2), (218, 20, 4.2), (223, 26, 5.5), (229, 32, 7), (237, 40, 9), (247, 50, 11), (259, 62, 14), (274, 76, 17))
    for row, (y, rx_, ry_) in enumerate(rows):
        t = row / (len(rows) - 1)
        gid = f"{u}-row{row}"
        top_c = "#FFE4C0" if row < 4 else "#F8C8B4"
        out.append(defs(lg(gid, [(0, top_c), (0.45, "#E8A8A8"), (1, "#8A6A9E")], 0, y - ry_ * 1.3, 0, y + ry_ * 1.2, units="userSpaceOnUse")))
        body, hl = [], []
        x = -30 - rnd.uniform(0, rx_)
        while x < 640:
            rx = rx_ * rnd.uniform(0.6, 1.1)
            ry = ry_ * rnd.uniform(0.8, 1.3)
            yy = y + rnd.uniform(-1, 1) * ry_ * 0.3
            body.append(f'<ellipse cx="{x:.1f}" cy="{yy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}"/>')
            near = max(0, 1 - abs(x - sx) / 300)
            if near > 0.2:
                hl.append(f'<ellipse cx="{x + (rx * 0.2 if x < sx else -rx * 0.2):.1f}" cy="{yy - ry * 0.55:.1f}" rx="{rx * 0.45:.1f}" ry="{ry * 0.3:.1f}" opacity="{0.5 * near:.2f}"/>')
            x += rx * rnd.uniform(0.55, 0.85)
        out.append(f'<g fill="url(#{gid})">{"".join(body)}</g><g fill="#FFF2D8">{"".join(hl)}</g>')
    out.append(mist(sx, 222, 240, 22, "#FFE2B0", f"{u}-cm", 0.55))
    out.append(ripples(40, 9, (sx - 110, 214, sx + 110, 228), ["#FFF2C8"], w=(8, 24), h=(0.8, 1.4), opacity=(0.4, 0.9)))
    # far crater rim walls, left and right
    poly, rl = ridge_poly([(-10, 236), (40, 232), (100, 246), (160, 262), (200, 274), (240, 290), (270, 300)], 3, base=300, amp=4, fill=f"url(#{u}-rim)")
    out.append(poly)
    poly, rr_ = ridge_poly([(360, 300), (400, 286), (440, 270), (480, 256), (530, 246), (610, 240)], 4, base=300, amp=4, fill=f"url(#{u}-rim)")
    out.append(poly)
    out.append(f'<polyline points="{P(rr_)}" fill="none" stroke="#FFB07A" stroke-width="1.6" opacity="0.8"/>')
    # cloud spilling through the gap into the crater
    out.append(mist(300, 268, 120, 12, "#F2C2C0", f"{u}-spill", 0.85))
    out.append(mist(330, 276, 70, 8, "#E8B0B8", f"{u}-spill2", 0.6))
    # crater floor: multicolored cinder desert
    out.append(f'<path d="M -10 300 Q 120 280 300 278 Q 470 280 610 296 L 610 444 L -10 444 Z" fill="url(#{u}-floor)"/>')
    out.append(f'<clipPath id="{u}-fl"><path d="M -10 300 Q 120 280 300 278 Q 470 280 610 296 L 610 444 L -10 444 Z"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-fl)">' + "".join(f'<path d="M {x:.1f} {y:.1f} q {w * 0.5:.1f} {-3:.1f} {w:.1f} {1:.1f} q {-w * 0.5:.1f} {4:.1f} {-w:.1f} 0 Z" fill="{c}" opacity="{o:.2f}"/>' for x, y, w, c, o in
                    [(random.Random(i).uniform(-60, 600), random.Random(i + 99).uniform(282, 350), random.Random(i + 7).uniform(40, 160), random.Random(i + 3).choice(["#8A4A44", "#9A6A4E", "#4A2A3A", "#2E1E2A", "#A87A5A"]), random.Random(i + 5).uniform(0.25, 0.55)) for i in range(40)]) + "</g>")
    # cinder cones, far to near
    for k, (cx, base, w, h, cl, cs) in enumerate(((150, 298, 70, 20, "#C8744A", "#5A3040"), (430, 300, 90, 26, "#B85A3E", "#4E2A3A"),
                                                  (250, 318, 130, 38, "#D0844E", "#5E3240"), (528, 324, 84, 24, "#A0503A", "#44263A"))):
        out.append(cinder_cone(u, k, cx, base, w, h, cl, cs, 30 + k))
    # Sliding Sands trail switchbacking down
    out.append('<path d="M 96 352 Q 140 340 120 326 Q 104 314 150 306 Q 196 298 200 290" stroke="#E8C8A0" stroke-width="1.6" fill="none" opacity="0.7" stroke-dasharray="3 2"/>')
    # foreground summit ridge of dark cinder, rim-lit
    poly, fg = ridge_poly([(-10, 350), (60, 340), (140, 348), (220, 362), (300, 370), (400, 360), (480, 344), (540, 336), (610, 340)], 6, base=444, amp=6, fill=f"url(#{u}-fg)")
    out.append(poly)
    out.append(f'<polyline points="{P(fg)}" fill="none" stroke="#FFB07A" stroke-width="2" opacity="0.75"/>')
    out.append(f'<clipPath id="{u}-fgc"><polygon points="{P(fg + [(610, 444), (-10, 444)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-fgc)">' + dots(400, 12, (-10, 336, 610, 444), "#8A5A4E", r=(0.6, 2.2), opacity=(0.3, 0.8))
               + lava_rocks(26, 13, (-10, 366, 610, 444)) + "</g>")
    # silverswords on the cinder
    out.append(silversword(472, 392, 26, 3, bloom=3.4))
    out.append(silversword(526, 400, 18, 4))
    out.append(silversword(110, 412, 22, 5))
    out.append(silversword(150, 420, 14, 6))
    # sunrise watchers: a couple under a blanket and a photographer at his tripod
    def blanket_pair(x, base, s):
        sil = dict(rim="#FFB07A", light=1, shadow=0)
        return (F.person(x - 8.5 * s, base, 84 * s, "sit_back", 1, "silhouette:#24161C", seed=31, **sil)
                + F.person(x + 9 * s, base, 80 * s, "sit_back", 1, "silhouette:#24161C", seed=32, **sil)
                + f'<g transform="translate({x} {base}) scale({s})">'
                '<path d="M -26 0 Q -28 -22 -18 -30 Q -8 -36 0 -32 Q 8 -37 18 -30 Q 28 -22 26 0 Z" fill="#B8323A"/>'
                '<path d="M -26 0 Q -28 -22 -18 -30 Q -8 -36 0 -32 L 0 0 Z" fill="#8A2430"/>'
                '<path d="M -22 -12 L 22 -12 M -24 -6 L 24 -6" stroke="#F2C24A" stroke-width="2" opacity="0.8"/>'
                '<path d="M 18 -30 Q 28 -22 26 0" stroke="#FFB07A" stroke-width="2" fill="none" opacity="0.8"/></g>')
    out.append(blanket_pair(300, 372, 1.0))
    out.append('<g fill="#24161C"><rect x="224" y="300" width="12" height="9" rx="2"/>'
               '<path d="M 230 309 L 222 362 M 230 309 L 232 362 M 230 309 L 240 360" stroke="#24161C" stroke-width="2"/></g>')
    out.append(F.person(209, 366, 80, "lean", 1, "silhouette:#24161C", seed=33, rim="#FFB07A", light=1))
    out.append(gulls([(120, 150, 9), (136, 158, 6)], "#2A1E3E", sw=1.8))
    return "\n".join(out)


# ---------------------------------------------------------------- Brooklyn (the Bridge from a cobbled DUMBO street, morning)
def brooklyn():
    u = "bk"
    C = Cam(f=380, cx=300, vpy=300, eye=1.6)
    out = [defs(
        lg(f"{u}-sky", [(0, "#6E98C8"), (0.45, "#A8C2DC"), (0.8, "#EED8C8"), (1, "#F8E6CC")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-river", [(0, "#D8DEE4"), (0.4, "#8EA6BE"), (1, "#5A7694")], 0, 284, 0, 304, units="userSpaceOnUse"),
        lg(f"{u}-stone", [(0, "#F6E0BC"), (0.6, "#E2C49E"), (1, "#B89A7E")]),
        lg(f"{u}-arch", [(0, "#B8CCE0"), (1, "#E6DED2")]),
        lg(f"{u}-cob", [(0, "#7A6E72"), (1, "#3E343C")], 0, 300, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-sun", [(0, "#FFD8A0", 0.0), (1, "#FFD8A0", 0.25)], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    for x, y, w in ((150, 110, 150), (470, 92, 170), (360, 150, 100)):
        out.append(f'<path d="M {x - w / 2} {y} q {w * 0.25} -14 {w * 0.5} -6 q {w * 0.2} -12 {w * 0.5} 4 q {-w * 0.5} 9 {-w} 2 Z" fill="#FFFFFF" opacity="0.75"/>'
                   f'<path d="M {x - w / 2 + 6} {y + 1} q {w * 0.45} 5 {w - 12} 0" stroke="#C8B8C8" stroke-width="1.5" fill="none" opacity="0.6"/>')
    # Lower Manhattan across the river, its east faces glowing in the morning sun
    rnd = random.Random(3)
    yr = C(0, 0, 1500)[1]
    sky_ = [(-520, 1700, 60, 150), (-440, 1600, 50, 230), (-370, 1700, 60, 180), (-300, 1500, 46, 260), (-230, 1600, 60, 200),
            (-160, 1500, 50, 150), (-90, 1600, 70, 240), (-20, 1700, 50, 280), (50, 1500, 60, 170), (120, 1600, 50, 220),
            (190, 1700, 70, 260), (260, 1500, 46, 160), (330, 1600, 70, 210), (400, 1500, 50, 140), (470, 1700, 60, 190), (-600, 1800, 70, 150)]
    for X, Z, w, h in sorted(sky_, key=lambda t: -t[1]):
        q = C.quad_z(Z, X - w / 2, X + w / 2, 0, h)
        x0, x1, yt, yb = q[0][0], q[2][0], q[1][1], q[0][1]
        out.append(f'<rect x="{x0:.1f}" y="{yt:.1f}" width="{x1 - x0:.1f}" height="{yb - yt:.1f}" fill="{rnd.choice(["#D2C4C2", "#C8BCC0", "#DCCCC4", "#BEB6C0"])}"/>')
        out.append(f'<rect x="{x0:.1f}" y="{yt:.1f}" width="{(x1 - x0) * 0.4:.1f}" height="{yb - yt:.1f}" fill="#FFE8C8" opacity="0.5"/>')
        out.append("".join(f'<rect x="{x0 + 0.6:.1f}" y="{yy:.1f}" width="{x1 - x0 - 1.2:.1f}" height="0.7" fill="#8A8CA6" opacity="0.35"/>' for yy in [yt + 2.5 + i * 2.6 for i in range(int((yb - yt - 3) / 2.6))]))
    # the tall tapering tower with its spire, right of the bridge
    X, Z = 260, 2000
    mid = C(X, 60, Z)[1]
    b0, b1 = C(X - 32, 0, Z), C(X + 32, 0, Z)
    t0, t1 = C(X - 16, 417, Z), C(X + 16, 417, Z)
    sp = C(X, 541, Z)
    out.append(f'<polygon points="{P([b0, (b0[0], mid), t0, t1, (b1[0], mid), b1])}" fill="#B4C2D4"/>')
    out.append(f'<polygon points="{P([((b0[0] + b1[0]) / 2, mid), t1, (b1[0], mid)])}" fill="#8A9CB6"/>')
    out.append(f'<polygon points="{P([(b0[0], mid), t0, ((t0[0] + t1[0]) / 2, t0[1]), ((b0[0] + b1[0]) / 2, mid)])}" fill="#EEF2F6"/>')
    out.append(f'<line x1="{sp[0]:.1f}" y1="{t0[1]:.1f}" x2="{sp[0]:.1f}" y2="{sp[1]:.1f}" stroke="#8A9CB6" stroke-width="1.4"/>')
    out.append(f'<rect x="0" y="{yr - 10:.1f}" width="600" height="10" fill="#EADCCE" opacity="0.6"/>')
    # East River with a ferry and a tug
    out.append(f'<rect x="0" y="{yr:.1f}" width="600" height="{306 - yr:.1f}" fill="url(#{u}-river)"/>')
    out.append(ripples(60, 4, (0, yr, 600, 306), ["#F2F4F6", "#5E7A98"], w=(4, 18), h=(0.5, 1.0), opacity=(0.4, 0.8)))
    fx, fy = 214, yr + 6
    out.append(f'<path d="M {fx - 12} {fy} L {fx + 11} {fy} L {fx + 9} {fy + 2.5} L {fx - 10} {fy + 2.5} Z" fill="#F4F0E8"/><rect x="{fx - 7}" y="{fy - 3}" width="14" height="3" fill="#2E5A8A"/>'
               f'<path d="M {fx + 11} {fy + 2} q 16 1 32 0" stroke="#FFFFFF" stroke-width="1.2" fill="none" opacity="0.8"/>')
    # ---- the Brooklyn tower in the river, seen straight down the street; cables fan out to both sides
    TZ, DECK, TOP = 175, 39.0, 84.0
    face = C.quad_z(TZ, -20, 20, 0, TOP)
    # cables: main span leaving to the right toward Manhattan, side span to the left toward the anchorage
    def cable(X0, Z0, X1, Z1, Y0, Y1, sag, n=40):
        return [C(X0 + (X1 - X0) * t, Y0 + (Y1 - Y0) * t - sag * 4 * t * (1 - t), Z0 + (Z1 - Z0) * t) for t in [i / n for i in range(n + 1)]]
    for side_x in (-14, 14):
        main = cable(side_x, TZ, side_x + 240, TZ + 420, TOP - 4, 46, 6)
        back = cable(side_x, TZ, side_x - 160, TZ - 260, TOP - 4, 34, 6)
        for line in (main, back):
            out.append(f'<polyline points="{P(line)}" fill="none" stroke="#3E3E54" stroke-width="1.8"/>')
            out.append('<g stroke="#4A4A62" stroke-width="0.7" opacity="0.8">' + "".join(
                f'<line x1="{line[i][0]:.1f}" y1="{line[i][1]:.1f}" x2="{line[i][0]:.1f}" y2="{line[i][1] + C.f * (C.eye - DECK) / -1 * 0 + (C(0, DECK, 1)[1] - C(0, line[i][1], 1)[1]) * 0:.1f}"/>' for i in range(0)) + "</g>")
        # diagonal stays radiating from the tower top: the bridge's signature web
        top = C(side_x, TOP - 6, TZ)
        stays = []
        for t in [0.08 * i for i in range(1, 9)]:
            for X1, Z1 in ((side_x + 240 * t, TZ + 420 * t), (side_x - 160 * t, TZ - 260 * t)):
                p_ = C(X1, DECK, Z1)
                stays.append(f'<line x1="{top[0]:.1f}" y1="{top[1]:.1f}" x2="{p_[0]:.1f}" y2="{p_[1]:.1f}"/>')
        out.append(f'<g stroke="#4A4A62" stroke-width="0.8" opacity="0.75">{"".join(stays)}</g>')
        # vertical suspenders from the main cables to the deck
        sus = []
        for line, (X1, Z1, Y1) in ((main, (side_x + 240, TZ + 420, 46)), (back, (side_x - 160, TZ - 260, 34))):
            for i in range(2, 40, 2):
                t = i / 40
                d_ = C(side_x + (X1 - side_x) * t, DECK + (Y1 - 6 - DECK) * t * 0.2, TZ + (Z1 - TZ) * t)
                sus.append(f'<line x1="{line[i][0]:.1f}" y1="{line[i][1]:.1f}" x2="{line[i][0]:.1f}" y2="{d_[1]:.1f}"/>')
        out.append(f'<g stroke="#5A5A72" stroke-width="0.6" opacity="0.6">{"".join(sus)}</g>')
    # decks leaving the tower both ways
    for X1, Z1, Y1 in ((240, TZ + 420, DECK - 1), (-160, TZ - 260, DECK - 8)):
        dk = [C(-15, DECK, TZ), C(-15 + X1, Y1, Z1), C(-15 + X1, Y1 - 3, Z1), C(-15, DECK - 3, TZ)]
        dk2 = [C(15, DECK, TZ), C(15 + X1, Y1, Z1), C(15 + X1, Y1 - 3, Z1), C(15, DECK - 3, TZ)]
        out.append(f'<polygon points="{P(dk)}" fill="#4A4458"/><polygon points="{P(dk2)}" fill="#4A4458"/>')
    # the tower: warm limestone face, shaded north side, coursed stone, cornice, twin pointed arches
    side = [C(20, 0, TZ), C(20, TOP, TZ), C(20, TOP, TZ + 16), C(20, 0, TZ + 16)]
    out.append(f'<polygon points="{P(side)}" fill="#9A8472"/>')
    out.append(f'<polygon points="{P(face)}" fill="url(#{u}-stone)"/>')
    cid = f"{u}-tw"
    x0, x1 = face[0][0], face[2][0]
    ytop, ybot = face[1][1], face[0][1]
    g = [streaks(90, 9, (x0, ytop, x1, ybot), ["#B8A08A", "#FFF2DA", "#9A8670"], w=(0.6, 1.6), length=(4, 22), opacity=(0.2, 0.45), slant=0.05)]
    for Yc in [3 + 2.6 * i for i in range(32)]:
        a_ = C(-20, Yc, TZ)
        g.append(f'<line x1="{x0:.1f}" y1="{a_[1]:.1f}" x2="{x1:.1f}" y2="{a_[1]:.1f}" stroke="#A8927A" stroke-width="0.6" opacity="0.55"/>')
    # buttress pilasters
    for Xp in (-20, -3.2, 16.8):
        q = C.quad_z(TZ - 0.5, Xp, Xp + 3.2, 0, TOP - 8)
        g.append(f'<polygon points="{P(q)}" fill="#FFF0D6" opacity="0.35"/><line x1="{q[2][0]:.1f}" y1="{q[1][1]:.1f}" x2="{q[2][0]:.1f}" y2="{q[0][1]:.1f}" stroke="#9A8470" stroke-width="1" opacity="0.6"/>')
    out.append(f'<clipPath id="{cid}"><polygon points="{P(face)}"/></clipPath><g clip-path="url(#{cid})">{"".join(g)}</g>')
    for Yc, hgt, col in ((TOP - 7, 3.5, "#FFF4E0"), (TOP - 8.2, 1.2, "#8A7462")):
        q = C.quad_z(TZ - 1, -21, 21, Yc, Yc + hgt)
        out.append(f'<polygon points="{P(q)}" fill="{col}"/>')
    for Xc in (-10.5, 10.5):
        a0, a1 = C(Xc - 5.2, DECK - 3, TZ), C(Xc + 5.2, DECK - 3, TZ)
        spr = C(Xc, DECK + 27, TZ)[1]
        ap = C(Xc, DECK + 39, TZ)
        k_ = ap[1] + (spr - ap[1]) * 0.25
        d = f'M {a0[0]:.1f} {a0[1]:.1f} L {a0[0]:.1f} {spr:.1f} Q {a0[0]:.1f} {k_:.1f} {ap[0]:.1f} {ap[1]:.1f} Q {a1[0]:.1f} {k_:.1f} {a1[0]:.1f} {spr:.1f} L {a1[0]:.1f} {a1[1]:.1f} Z'
        out.append(f'<path d="{d}" fill="url(#{u}-arch)"/>')
        # roadway and its railing seen through the arch
        out.append(f'<rect x="{a0[0]:.1f}" y="{a0[1] - 4:.1f}" width="{a1[0] - a0[0]:.1f}" height="4" fill="#5A5468"/><rect x="{a0[0]:.1f}" y="{a0[1] - 9:.1f}" width="{a1[0] - a0[0]:.1f}" height="1.2" fill="#5A5468"/>')
        out.append(f'<path d="{d}" fill="none" stroke="#6E5A4A" stroke-width="2.2"/>')
        out.append(f'<path d="M {a0[0] + 2.5:.1f} {a0[1]:.1f} L {a0[0] + 2.5:.1f} {spr:.1f} Q {a0[0] + 2.5:.1f} {k_ + 3:.1f} {ap[0]:.1f} {ap[1] + 4:.1f}" stroke="#7A6656" stroke-width="3" fill="none" opacity="0.45"/>')
    # cable saddles on top
    for side_x in (-14, 14):
        sd = C(side_x, TOP - 3, TZ - 1)
        out.append(f'<rect x="{sd[0] - 4:.1f}" y="{sd[1] - 2:.1f}" width="8" height="4" rx="1" fill="#3E3E54"/>')
    # waterfront at the end of the street: railing, park trees, a few people at the rail
    out.append(f'<polygon points="{P([C(-200, 0, 150), C(200, 0, 150), C(200, 0, 60), C(-200, 0, 60)])}" fill="#8A9A78"/>')
    out.append(f'<polygon points="{P([C(-200, 0.01, 150), C(200, 0.01, 150), C(200, 1.1, 150), C(-200, 1.1, 150)])}" fill="#4A4A5A" opacity="0.6"/>')
    for X in range(-40, 41, 5):
        if abs(X) < 9:
            continue
        x, b = C(X + random.Random(X).uniform(-2, 2), 0, 120)
        r = C.f * random.Random(X + 1).uniform(2.6, 4) / 120
        out.append(f'<rect x="{x - 0.8:.1f}" y="{b - r:.1f}" width="1.6" height="{r:.1f}" fill="#4A3A3A"/><circle cx="{x:.1f}" cy="{b - r * 1.6:.1f}" r="{r:.1f}" fill="{random.Random(X + 2).choice(["#5A7A4E", "#6A8A52", "#4E6E48"])}"/>'
                   f'<circle cx="{x + r * 0.3:.1f}" cy="{b - r * 1.9:.1f}" r="{r * 0.5:.1f}" fill="#B8CC80" opacity="0.6"/>')
    for X, col in ((-3.5, "#C8573E"), (-2.6, "#2E4A6A"), (3.2, "#E8A040")):
        x, b = C(X, 0, 140)
        out.append(walker(x, b, C.f * 1.7 / 140, col, facing=1 if X < 0 else -1))
    # cobbled street with old freight rails
    out.append(f'<polygon points="{P([C(-6.5, 0, 150), C(6.5, 0, 150), C(6.5, 0, 3), C(-6.5, 0, 3)])}" fill="url(#{u}-cob)"/>')
    rnd = random.Random(17)
    cobs = []
    Z, row = 3.4, 0
    while Z < 150:
        dZ = 0.24 * (1 + Z * 0.03)
        y0 = C(0, 0, Z)[1]
        y1 = C(0, 0, Z + dZ)[1]
        if y0 - y1 < 0.8:
            break
        X = -6.5 + (row % 2) * 0.22
        while X < 6.5:
            a_, b_ = C(X, 0, Z), C(X + 0.42, 0, Z)
            cobs.append(f'<rect x="{a_[0] + 0.4:.1f}" y="{y1 + 0.3:.1f}" width="{max(0.5, b_[0] - a_[0] - 0.8):.1f}" height="{max(0.4, y0 - y1 - 0.6):.1f}" rx="{min(2.4, (y0 - y1) * 0.35):.1f}" fill="{rnd.choice(["#9A8A86", "#8A7A7A", "#A89488", "#7A6A70", "#B4A094"])}" opacity="{rnd.uniform(0.55, 0.95):.2f}"/>')
            X += 0.46
        Z += dZ
        row += 1
    out.append("".join(cobs))
    for X in (-2.2, -0.9):
        for dx_, col, w_ in ((0, "#3A3238", 0.09), (0.03, "#E8D8C8", 0.03)):
            out.append(f'<polygon points="{P([C(X + dx_ - w_, 0, 150), C(X + dx_ + w_, 0, 150), C(X + dx_ + w_, 0, 3), C(X + dx_ - w_, 0, 3)])}" fill="{col}"/>')
    # low morning sun from behind-left: the left buildings' shadow covers part of the street
    out.append(f'<polygon points="{P([C(-6.5, 0, 150), C(-1.5, 0, 150), C(1.5, 0, 3), C(-6.5, 0, 3)])}" fill="#2A2034" opacity="0.3"/>')
    out.append(f'<polygon points="{P([C(-1.5, 0, 150), C(6.5, 0, 150), C(6.5, 0, 3), C(1.5, 0, 3)])}" fill="#FFD8A0" opacity="0.16"/>')
    for sgn in (-1, 1):
        out.append(f'<polygon points="{P([C(sgn * 6.5, 0.15, 150), C(sgn * 9, 0.15, 150), C(sgn * 9, 0.15, 2), C(sgn * 6.5, 0.15, 2)])}" fill="{"#6E6268" if sgn < 0 else "#D2BCA4"}"/>')
        out.append(f'<polygon points="{P([C(sgn * 6.5, 0, 150), C(sgn * 6.5, 0.15, 150), C(sgn * 6.5, 0.15, 2), C(sgn * 6.5, 0, 2)])}" fill="#E8DCD0"/>')
    # ---- left: brick warehouses in shade (arched windows, fire escapes, painted wall)
    for z0, z1, h, col in ((3, 22, 22, "#7A3A30"), (22, 40, 26, "#864634"), (40, 58, 20, "#6E4038")):
        X = -9
        out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, 0, h))}" fill="{col}"/>')
        out.append('<g stroke="#2A1A1A" stroke-opacity="0.13" stroke-width="0.8">' + "".join(
            f'<line x1="{C(X, y, z0)[0]:.1f}" y1="{C(X, y, z0)[1]:.1f}" x2="{C(X, y, z1)[0]:.1f}" y2="{C(X, y, z1)[1]:.1f}"/>' for y in [0.5 + 0.45 * i for i in range(int(h / 0.45))]) + "</g>")
        floors = int((h - 4) / 3.4)
        bays = max(3, int((z1 - z0) / 4))
        rnd2 = random.Random(z0 * 7)
        for f_ in range(floors):
            y0 = 4 + f_ * 3.4
            for i in range(bays):
                za = z0 + (z1 - z0) * (i + 0.25) / bays
                zb = z0 + (z1 - z0) * (i + 0.75) / bays
                glass = rnd2.choice(["#2A2A3E", "#34364E", "#4A5A72", "#3A3048"])
                out.append(f'<polygon points="{P(C.quad_x(X, za, zb, y0, y0 + 2.2))}" fill="{glass}"/>')
                ta, tb, tm = C(X, y0 + 2.2, za), C(X, y0 + 2.2, zb), C(X, y0 + 2.8, (za + zb) / 2)
                out.append(f'<path d="M {ta[0]:.1f} {ta[1]:.1f} Q {tm[0]:.1f} {tm[1] - (ta[1] - tm[1]) * 0.3:.1f} {tb[0]:.1f} {tb[1]:.1f} Z" fill="{glass}"/>')
                out.append(f'<polygon points="{P(C.quad_x(X, za - 0.1, zb + 0.1, y0 - 0.25, y0))}" fill="#D8C0A8" opacity="0.6"/>')
        out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, h - 1.0, h))}" fill="#C8A890" opacity="0.5"/>')
        out.append(f'<polygon points="{P(C.quad_x(X, z0, z0 + 0.4, 0, h))}" fill="#000" opacity="0.25"/>')
        out.append(f'<polygon points="{P(C.quad_x(X, z0 + 1, z1 - 1, 0.2, 3.4))}" fill="#22181E" opacity="0.7"/>')
        out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, 0, h))}" fill="#1E1628" opacity="0.28"/>')
        if z0 >= 22:
            zf0, zf1 = z0 + (z1 - z0) * 0.3, z0 + (z1 - z0) * 0.6
            fe = []
            for f_ in range(1, floors):
                y = 4 + f_ * 3.4 - 0.4
                for yy in (y, y + 0.9):
                    p1, p2 = C(X + 0.8, yy, zf0), C(X + 0.8, yy, zf1)
                    fe.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}"/>')
                l1 = C(X + 0.8, y, zf0 + 0.6 if f_ % 2 else zf1 - 0.6)
                l2 = C(X + 0.8, y + 3.4, zf1 - 0.6 if f_ % 2 else zf0 + 0.6)
                fe.append(f'<line x1="{l1[0]:.1f}" y1="{l1[1]:.1f}" x2="{l2[0]:.1f}" y2="{l2[1]:.1f}"/>')
            out.append(f'<g stroke="#1A1218" stroke-width="{max(0.8, C.f * 0.07 / ((zf0 + zf1) / 2)):.1f}">{"".join(fe)}</g>')
    # rooftop water tower on the far warehouse
    wt = C(-14, 26, 34)
    k = C.f / 34 / 10
    out.append(f'<g transform="translate({wt[0]:.1f} {wt[1]:.1f}) scale({k:.3f})">'
               '<path d="M -18 0 L -14 -30 M 18 0 L 14 -30 M -16 -10 L 16 -20 M 16 -10 L -16 -20" stroke="#2A2028" stroke-width="2.4"/>'
               '<rect x="-20" y="-62" width="40" height="34" fill="#7A5A48"/><rect x="4" y="-62" width="16" height="34" fill="#C8A07A"/>'
               '<path d="M -20 -48 L 20 -48 M -20 -38 L 20 -38" stroke="#3A2A28" stroke-width="1.6"/>'
               '<path d="M -24 -62 L 0 -82 L 24 -62 Z" fill="#4A3430"/><path d="M 24 -62 L 0 -82 L 4 -62 Z" fill="#9A7A62"/></g>')
    # ---- right: sunlit brownstones with stoops, cornices and bay windows
    rnd3 = random.Random(41)
    z = 5.6
    while z < 58:
        w_ = 6.2
        h = rnd3.uniform(13, 15)
        X = 9
        col = rnd3.choice(["#8A5442", "#7E4A3C", "#94604C"])
        out.append(f'<polygon points="{P(C.quad_x(X, z, z + w_, 0, h))}" fill="{col}"/>')
        out.append(f'<polygon points="{P(C.quad_x(X, z, z + w_, 0, h))}" fill="url(#{u}-sun)"/>')
        out.append(f'<polygon points="{P(C.quad_x(X - 0.5, z - 0.1, z + w_ + 0.1, h - 0.8, h))}" fill="#3E2A28"/>')
        out.append(f'<polygon points="{P(C.quad_x(X - 0.5, z - 0.1, z + w_ + 0.1, h - 0.9, h - 0.7))}" fill="#E8C8A0" opacity="0.6"/>')
        for f_ in range(3):
            y0 = 3.6 + f_ * 3.2
            for za in (z + 0.9, z + 2.6, z + 4.3):
                out.append(f'<polygon points="{P(C.quad_x(X, za, za + 1.0, y0, y0 + 2.2))}" fill="{rnd3.choice(["#3A3448", "#4E5A72", "#2E2A3A", "#6A7A92"])}"/>')
                out.append(f'<polygon points="{P(C.quad_x(X - 0.05, za - 0.15, za + 1.15, y0 + 2.2, y0 + 2.5))}" fill="#E8C8A0" opacity="0.8"/>')
        # stoop: stairs rising to the parlor door, with an iron rail
        door = C.quad_x(X, z + 0.6, z + 1.8, 1.8, 4.2)
        out.append(f'<polygon points="{P(door)}" fill="#3A2420"/>')
        st = [C(X, 1.8, z + 0.5), C(X - 2.6, 0, z + 0.5), C(X - 2.6, 0, z + 1.9), C(X, 1.8, z + 1.9)]
        out.append(f'<polygon points="{P(st)}" fill="#6E4438"/>')
        out.append(f'<polygon points="{P([C(X, 1.8, z + 1.9), C(X - 2.6, 0, z + 1.9), C(X - 2.6, 0.12, z + 1.9), C(X, 1.92, z + 1.9)])}" fill="#D8B090"/>')
        r1, r2 = C(X, 2.8, z + 0.5), C(X - 2.6, 1.0, z + 0.5)
        out.append(f'<line x1="{r1[0]:.1f}" y1="{r1[1]:.1f}" x2="{r2[0]:.1f}" y2="{r2[1]:.1f}" stroke="#1E1618" stroke-width="{max(0.7, C.f * 0.06 / z):.1f}"/>')
        out.append(f'<polygon points="{P(C.quad_x(X, z, z + 0.25, 0, h))}" fill="#000" opacity="0.18"/>')
        z += w_
    # street trees on the brownstone side, dappled with sun
    for Z in (24, 42):
        x, b = C(7.6, 0, Z)
        hh = C.f * 9 / Z
        out.append(f'<path d="M {x - hh * 0.02:.1f} {b:.1f} L {x - hh * 0.012:.1f} {b - hh * 0.5:.1f} L {x + hh * 0.012:.1f} {b - hh * 0.5:.1f} L {x + hh * 0.02:.1f} {b:.1f} Z" fill="#5A4A3E"/>')
        rnd4 = random.Random(Z)
        for _ in range(16):
            cx_, cy_ = x + rnd4.uniform(-0.28, 0.28) * hh, b - hh * rnd4.uniform(0.55, 0.95)
            r = hh * rnd4.uniform(0.08, 0.15)
            out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{r:.1f}" fill="{rnd4.choice(["#4E6E3E", "#5E7E44", "#3E5A36"])}"/><circle cx="{cx_ - r * 0.3:.1f}" cy="{cy_ - r * 0.3:.1f}" r="{r * 0.5:.1f}" fill="#B8CC70" opacity="0.55"/>')
    # cast-iron lamp posts
    for Z in (14, 30, 52):
        for sgn in (-1,):
            x0, y0 = C(sgn * 7.2, 0, Z)
            x1, y1 = C(sgn * 7.2, 4.4, Z)
            sw = max(0.8, C.f * 0.12 / Z)
            out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#1E1A22" stroke-width="{sw:.1f}"/>'
                       f'<path d="M {x1 - sw * 1.8:.1f} {y1:.1f} L {x1 + sw * 1.8:.1f} {y1:.1f} L {x1 + sw * 1.2:.1f} {y1 - sw * 4:.1f} L {x1 - sw * 1.2:.1f} {y1 - sw * 4:.1f} Z" fill="#1E1A22"/>'
                       f'<rect x="{x1 - sw:.1f}" y="{y1 - sw * 3.4:.1f}" width="{sw * 2:.1f}" height="{sw * 2.6:.1f}" fill="#FFE8B8" opacity="0.8"/>')
    # a dog walker heading for the river, a cyclist, a couple photographing the bridge
    x, b = C(-2.4, 0, 11)
    hh = C.f * 1.7 / 11
    out.append(walker(x, b, hh, "#C8573E", rim="#FFD8A0", rim_side=-1, pose="dog_walker", facing=1, seed=41, pal={"dog": "#E8C080", "top_kind": "jacket", "form": "m"}))
    for X, Z, col in ((1.3, 26, "#2E4A6A"), (2.0, 26, "#E8A040")):
        x, b = C(X, 0, Z)
        out.append(walker(x, b, C.f * 1.7 / Z, col, rim="#FFD8A0", rim_side=-1, pose="photo" if X < 1.5 else "stand_back", facing=-1, seed=int(X * 10)))
    out.append(gulls([(200, 150, 9), (216, 160, 6), (420, 128, 8)], "#4A4A62", sw=1.8))
    return "\n".join(out)


# ---------------------------------------------------------------- Badlands (banded spires at sunset, a bighorn ram on the ledge)
def poly(pts, fill, extra=""):
    return f'<polygon points="{P(pts)}" fill="{fill}"{extra}/>'


def spire_line(x0, x1, base, peaks, seed, step=3, amp=1.5, plinth=0.0, teeth=1.0):
    """Badlands skyline: broad eroded masses with concave, flaring skirts, crowned by a saw-tooth of small
    pinnacles; peaks = [(cx, top, half_width, sharpness)]."""
    rnd = random.Random(seed)
    tops = []                               # small pinnacles riding on the masses
    x = x0
    while x < x1:
        tops.append((x, rnd.uniform(4, 13), rnd.uniform(0.25, 1.0)))
        x += rnd.uniform(6, 15)

    def mass(x):
        h = plinth * min(1.0, (x - x0) / 36, (x1 - x) / 36) ** 0.6 if x0 < x < x1 else 0.0
        for cx, top, hw, sh in peaks:
            d = abs(x - cx) / hw
            if d < 1:
                h = max(h, (base - top) * (1 - d) ** sh)
        return h

    hmax = max(base - t for _, t, _, _ in peaks)
    pts = []
    x = x0
    while x <= x1 + 0.1:
        h = mass(x)
        k = (h / hmax) ** 0.7
        t = 0.0
        for tx, tw, th in tops:
            d = abs(x - tx) / tw
            if d < 1:
                t = max(t, th * 26 * teeth * k * (1 - d) ** 1.3)
        pts.append((x, base - h - t + (rnd.uniform(-amp, amp) if h > 3 else 0)))
        x += step
    for cx, top, hw, sh in peaks:           # keep each crest as a true pinnacle so the shadow facets meet it
        i = min(range(len(pts)), key=lambda j: abs(pts[j][0] - cx))
        pts[i] = (cx, min(pts[i][1], top - 10 * teeth))
    return pts


def formation(u, k, line, base, peaks, bands, seed, shade="#5E3E6E", shade_op=0.42, lit="#FFE2B0", lit_op=0.8,
              streak_cols=("#9A6A6A", "#FFF0DC", "#B88070"), n_streaks=None, haze=None):
    """One banded badlands formation: horizontal strata (same absolute heights across a layer), erosion rills,
    a violet shadow facet on the right of every pinnacle and a warm lit rim on the sun-facing slopes."""
    rnd = random.Random(seed)
    shape = line + [(line[-1][0], base + 2), (line[0][0], base + 2)]
    cid = f"{u}-f{k}"
    x0, x1 = line[0][0], line[-1][0]
    top = min(y for _, y in line)
    g = [f'<rect x="{x0}" y="{top - 2:.0f}" width="{x1 - x0}" height="{base - top + 4:.0f}" fill="{bands[0][1]}"/>']
    for by, col in bands[1:]:
        ph = rnd.uniform(0, 6)
        wav = [(x, by + 1.6 * math.sin(x / 19 + ph) + 1.0 * math.sin(x / 7 + ph * 2)) for x in range(int(x0) - 2, int(x1) + 4, 4)]
        g.append(poly(wav + [(x1 + 4, base + 4), (x0 - 2, base + 4)], col))
        # a thin pale parting line at the top of each stratum
        g.append(f'<polyline points="{P(wav)}" fill="none" stroke="#FFF2E2" stroke-width="1" opacity="0.35"/>')
    n = n_streaks or int((x1 - x0) * (base - top) / 320)
    g.append(streaks(n, seed + 1, (x0, top, x1, base), list(streak_cols), w=(0.8, 2.2), length=(8, 40), opacity=(0.12, 0.34), slant=0.06))
    # corrugated rills: a dark gully with a sunlit rib beside it, running down from the crest line
    rills = []
    for _ in range(int((x1 - x0) / 3)):
        rx = rnd.uniform(x0, x1)
        ry = (y_on(line, rx) or base) + rnd.uniform(1, 6)
        L = (base - ry) * rnd.uniform(0.3, 0.8)
        if L < 6:
            continue
        wob = rnd.uniform(-3, 3)
        rills.append(f'<path d="M {rx:.1f} {ry:.1f} q {wob:.1f} {L / 2:.1f} {wob * 0.4:.1f} {L:.1f}" stroke="{shade}" stroke-width="{rnd.uniform(0.9, 1.8):.1f}" opacity="{rnd.uniform(0.18, 0.4):.2f}"/>'
                     f'<path d="M {rx - 1.6:.1f} {ry + 2:.1f} q {wob:.1f} {L * 0.4:.1f} {wob * 0.4:.1f} {L * 0.7:.1f}" stroke="{lit}" stroke-width="1" opacity="{rnd.uniform(0.15, 0.35):.2f}"/>')
    g.append('<g fill="none" stroke-linecap="round">' + "".join(rills) + "</g>")
    # shadow facets: from each crest, down the right-hand flank to the next valley, then down a gully to the base
    for cx, ptop, hw, sh in peaks:
        i = min(range(len(line)), key=lambda j: abs(line[j][0] - cx))
        j = i + 1
        while j < len(line) - 1 and line[j + 1][1] >= line[j][1] - 0.5:
            j += 1
        right = line[i:j + 1]
        gx = right[-1][0]
        mid = [(cx + (base - ptop) * 0.05 * t + rnd.uniform(-2, 2), ptop + (base - ptop) * t) for t in (0.15, 0.35, 0.55, 0.8, 1.0)]
        g.append(poly(right + [(gx + rnd.uniform(-3, 3), base + 2)] + mid[::-1], shade, f' opacity="{shade_op}"'))
    if haze:
        g.append(f'<rect x="{x0}" y="{top - 2:.0f}" width="{x1 - x0}" height="{base - top + 4:.0f}" fill="url(#{haze})"/>')
    out = [f'<clipPath id="{cid}"><polygon points="{P(shape)}"/></clipPath>', poly(shape, bands[0][1]), f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>"]
    # lit rim on slopes that face the low sun (rising to the right)
    seg = []
    for (ax, ay), (bx, by) in zip(line, line[1:]):
        if by < ay - 0.3:
            seg.append(f'M {ax:.1f} {ay:.1f} L {bx:.1f} {by:.1f}')
    out.append(f'<path d="{" ".join(seg)}" stroke="{lit}" stroke-width="1.8" stroke-linecap="round" fill="none" opacity="{lit_op}"/>')
    return "".join(out)


def bighorn(x, base, s, coat="#7A5640", dark="#3E2A22", rim="#FFC27A", horn="#CDB088", horn_dk="#8A6E52"):
    """Bighorn ram in profile facing left (toward the low sun), heavy curled horns, pale muzzle and rump patch."""
    g = []
    # far legs
    g.append(f'<path d="M -10 -20 L -9 -1 L -6 -1 L -5 -20 Z M 20 -20 L 22 -1 L 25 -1 L 24 -20 Z" fill="{dark}"/>')
    # body
    g.append(f'<path d="M -20 -30 Q -19 -41 -6 -42 L 16 -41 Q 29 -41 31 -31 Q 32 -22 26 -18 L 10 -17 Q -2 -16 -14 -18 Q -21 -22 -20 -30 Z" fill="url(#bl-ram)"/>')
    rnd = random.Random(5)
    g.append(f'<g stroke="{dark}" stroke-width="1" stroke-linecap="round" fill="none" opacity="0.35">' + "".join(
        f'<path d="M {fx:.1f} {fy:.1f} q 1.5 2.5 0.5 {rnd.uniform(4, 7):.1f}"/>' for fx, fy in [(rnd.uniform(-14, 26), rnd.uniform(-38, -24)) for _ in range(16)]) + "</g>")
    g.append(f'<path d="M -14 -18 Q -2 -15 10 -17 L 26 -18 Q 28 -22 27 -24 Q 10 -21 -16 -23 Z" fill="{dark}" opacity="0.55"/>')
    g.append(f'<path d="M 26 -38 Q 33 -32 31 -22 Q 27 -20 24 -22 Q 27 -30 24 -37 Z" fill="#EDE2D0"/>')        # rump patch
    # near legs with pale stockings
    g.append(f'<path d="M -16 -24 Q -12 -16 -14.4 -8 L -14 0 L -10.5 0 L -10 -8 Q -8 -16 -8 -24 Z M 14 -23 Q 19 -16 16 -8 L 16 0 L 19.5 0 L 20 -8 Q 23 -16 22 -23 Z" fill="{coat}"/>')
    g.append(f'<path d="M -14.4 -8 L -14 0 L -10.5 0 L -10.2 -8 Z M 15.6 -8 L 16 0 L 19.5 0 L 19.8 -8 Z" fill="#E6DAC8"/>')
    g.append(f'<path d="M -14.5 0 h 4.6 M 15.6 0 h 4.4" stroke="#1E1612" stroke-width="2"/>')
    # thick neck and head, muzzle pointing forward-down
    g.append(f'<path d="M -10 -40 Q -18 -48 -24 -54 L -34 -54 Q -38 -46 -30 -38 Q -24 -30 -20 -26 Z" fill="{coat}"/>')
    g.append(f'<path d="M -24 -56 Q -32 -60 -38 -55 L -44 -48 Q -45 -43 -40 -42 L -33 -44 Q -26 -47 -24 -56 Z" fill="{coat}"/>')
    g.append(f'<path d="M -44 -48 Q -45 -43 -40 -42 L -35 -43.5 Q -38 -47 -41 -50 Z" fill="#E8DCCA"/>')        # pale muzzle
    g.append(f'<circle cx="-33" cy="-53" r="1.3" fill="#1A120E"/>')
    # the great curled horn: a tapering spiral back and down around the ear
    g.append(f'<path d="M -28 -57 Q -24 -66 -14 -64 Q -4 -61 -4 -50 Q -5 -40 -14 -40 Q -22 -41 -22 -48 Q -21 -53 -16 -53" stroke="{horn}" stroke-width="7" fill="none" stroke-linecap="round"/>')
    g.append(f'<path d="M -27 -59 Q -23 -66 -14 -64 Q -4 -61 -4 -50 Q -5 -40 -14 -40" stroke="#F4E2C0" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.8"/>')
    g.append(f'<g stroke="{horn_dk}" stroke-width="1.1" opacity="0.8">' + "".join(
        f'<line x1="{-14 + 9 * math.cos(a):.1f}" y1="{-52 + 10 * math.sin(a):.1f}" x2="{-14 + 13 * math.cos(a):.1f}" y2="{-52 + 14 * math.sin(a):.1f}"/>'
        for a in [math.radians(d) for d in range(-150, 100, 22)]) + "</g>")
    # warm sunset rim on the chest, face and back
    g.append(f'<path d="M -33 -51 Q -36.5 -46 -29.5 -38.5 Q -24 -31 -20.5 -27 M -38 -55 L -43.5 -48.5 M -19 -36 Q -16 -42 -6 -42 L 16 -41" stroke="{rim}" stroke-width="1.8" fill="none" stroke-linecap="round"/>')
    g.append(f'<path d="M -15 -22 L -14 -2" stroke="{rim}" stroke-width="1.2" opacity="0.8"/>')
    d = lg("bl-ram", [(0, "#9A6E4E"), (0.5, coat), (1, "#5A3E30")], 0, 0, 1, 0)
    return f'<defs>{d}</defs><g transform="translate({x} {base}) scale({s})">' + "".join(g) + "</g>"


def yucca(x, base, h, seed, col="#6E7A4A", lit="#D8C878"):
    rnd = random.Random(seed)
    out = []
    for _ in range(16):
        a = math.radians(rnd.uniform(-75, 75))
        L = h * rnd.uniform(0.6, 1.0)
        ex, ey = x + L * math.sin(a), base - L * math.cos(a) * 0.9
        out.append(f'<path d="M {x:.1f} {base:.1f} L {ex:.1f} {ey:.1f}" stroke="{rnd.choice([col, lit, col])}" stroke-width="{rnd.uniform(1.6, 2.6):.1f}" stroke-linecap="round"/>')
    out.append(f'<path d="M {x:.1f} {base - h * 0.4:.1f} Q {x + 4:.1f} {base - h * 1.4:.1f} {x + 2:.1f} {base - h * 1.9:.1f}" stroke="#8A6A3A" stroke-width="1.8" fill="none"/>')
    out.append("".join(f'<ellipse cx="{x + 3 + (i % 2) * 3 - 1.5:.1f}" cy="{base - h * (1.25 + i * 0.12):.1f}" rx="2.4" ry="1.6" fill="#F4E6C0"/>' for i in range(5)))
    return "".join(out)


def badlands():
    u = "bl"
    out = [defs(
        lg(f"{u}-sky", [(0, "#2C2A5C"), (0.3, "#5C4684"), (0.58, "#B8688E"), (0.8, "#F09A6C"), (1, "#FFD088")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-hzF", [(0, "#E8A0A0", 0.55), (1, "#F8C090", 0.25)]),
        lg(f"{u}-hzL", [(0, "#F0A890", 0.1), (1, "#F6B890", 0.45)]),
        lg(f"{u}-prairie", [(0, "#C8A458"), (0.4, "#A88A44"), (1, "#6E5A30")], 0, 330, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-ledge", [(0, "#F2D2B0"), (1, "#C89884")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(22, 3, (300, 40, 600, 120), "#FFF0E0", r=(0.6, 1.2), opacity=(0.3, 0.8)))
    # the sun setting into the far wall, and a wide warm glow
    out.append(glow(214, 272, 300, "#FFD898", f"{u}-sunG", 0.8))
    out.append('<circle cx="214" cy="270" r="20" fill="#FFF2CC"/>')
    # thin sunset clouds lit from beneath
    out.append('<g fill="#F4A08A" opacity="0.6">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{h}"/>' for x, y, w, h in (
        (140, 196, 110, 4), (90, 208, 60, 3), (330, 178, 80, 3.5), (520, 150, 90, 4), (560, 164, 50, 3), (240, 228, 50, 2.5))) + "</g>")
    out.append('<g fill="#FFE0B8" opacity="0.6">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="1.6"/>' for x, y, w in ((150, 199, 70), (330, 180, 40), (240, 230, 30))) + "</g>")
    # pale crescent moon rising in the east
    out.append(glow(520, 104, 26, "#FFF0E0", f"{u}-moonG", 0.35))
    out.append('<path d="M 516 94 A 10 10 0 1 0 530 108 A 8.6 8.6 0 1 1 516 94 Z" fill="#FFF4E4"/>')

    # --- far wall of the Badlands, hazy pink-lavender
    pk = [(10, 244, 70, 1.1), (110, 252, 60, 1.0), (300, 250, 70, 1.1), (400, 240, 60, 1.2), (500, 248, 70, 1.0), (590, 238, 60, 1.1)]
    line = spire_line(-10, 610, 302, pk, 3, step=3, amp=1, plinth=24, teeth=0.45)
    out.append(formation(u, 0, line, 302, pk, [(0, "#E6B4B4"), (256, "#DEA8AE"), (270, "#E8BCB2"), (286, "#D6A0A8")], 4,
                         shade="#8A6A9E", shade_op=0.3, lit="#FFE4C4", lit_op=0.55, streak_cols=("#B88898", "#FFE8DC"), haze=f"{u}-hzF"))

    out.append(f'<rect x="-10" y="298" width="620" height="60" fill="#E2B49A"/><rect x="-10" y="298" width="620" height="3" fill="#FFE2B8" opacity="0.7"/>')
    # --- left formation, nearer, in the sun's glare
    pk = [(10, 196, 80, 1.2), (96, 226, 64, 1.1), (160, 256, 44, 1.0)]
    line = spire_line(-12, 250, 336, pk, 5, step=3, amp=1.5, plinth=30, teeth=0.8)
    out.append(formation(u, 1, line, 336, pk, [(0, "#F2D8C0"), (214, "#EBB8A6"), (234, "#F2D6BC"), (254, "#CF8A72"), (258, "#EBB49E"), (282, "#ECC090"), (306, "#F0D6B8"), (322, "#DDB49C")], 6,
                         shade="#6A4A7A", shade_op=0.38, streak_cols=("#A8706E", "#FFF0DC", "#C08A78"), haze=f"{u}-hzL"))

    # --- the hero wall of spires: broad fluted masses with flaring skirts, crowned by saw-tooth pinnacles,
    #     the same strata running level through every one
    pk = [(268, 222, 60, 1.1), (330, 160, 80, 1.25), (414, 132, 90, 1.35), (500, 162, 70, 1.2), (566, 140, 80, 1.3), (624, 176, 50, 1.1)]
    line = spire_line(222, 612, 344, pk, 9, step=2.5, amp=1.2, plinth=40, teeth=1.0)
    bands = [(0, "#F6E4CC"), (150, "#F0C4AE"), (170, "#F4DABE"), (192, "#EAB09C"), (208, "#CC7E68"), (212, "#ECB49E"), (234, "#F3D3B2"),
             (254, "#E8B678"), (268, "#F1D6B4"), (292, "#DCB0A8"), (314, "#E6B878"), (332, "#CDA290")]
    out.append(formation(u, 2, line, 344, pk, bands, 10, shade="#643C6A", shade_op=0.34, streak_cols=("#9A6266", "#FFF2E0", "#B8806E", "#7A5262")))

    # --- the Yellow Mounds: soft rounded ochre and rose hills in front of the wall
    for k, (pts, col, band) in enumerate((
            ([(40, 352), (80, 326), (130, 316), (180, 322), (230, 334), (270, 352)], "#E2B060", "#D88A6E"),
            ([(200, 356), (250, 334), (300, 326), (360, 330), (420, 346), (450, 358)], "#E8BC6E", "#E0987E"))):
        ln = rough(pts, 50 + k, amp=3, depth=3)
        shape = ln + [(ln[-1][0], 364), (ln[0][0], 364)]
        cid = f"{u}-ym{k}"
        out.append(f'<clipPath id="{cid}"><polygon points="{P(shape)}"/></clipPath>' + poly(shape, col)
                   + f'<g clip-path="url(#{cid})">'
                   + poly([(x, y + 10 + 2 * math.sin(x / 15)) for x, y in ln] + [(ln[-1][0], 364), (ln[0][0], 364)], band, ' opacity="0.8"')
                   + poly([(x, y + 18 + 2 * math.sin(x / 11)) for x, y in ln] + [(ln[-1][0], 364), (ln[0][0], 364)], "#F2D49A", ' opacity="0.7"')
                   + streaks(60, 60 + k, (pts[0][0], 316, pts[-1][0], 364), ["#B8805A", "#FFF0D0"], w=(0.8, 2), length=(6, 20), opacity=(0.2, 0.45), slant=0.1)
                   + poly([(pts[2][0], pts[2][1] - 2)] + [p for p in ln if p[0] > pts[2][0]] + [(ln[-1][0], 364), (pts[2][0] + 10, 364)], "#6A4A6E", ' opacity="0.3"')
                   + "</g>")
        out.append(f'<polyline points="{P([p for p in ln if p[0] < pts[2][0]])}" fill="none" stroke="#FFE6B0" stroke-width="1.6" opacity="0.8"/>')

    # --- the prairie floor with grazing bison far off
    pl, pr = ridge_poly([(-10, 350), (120, 346), (260, 354), (420, 356), (610, 350)], 61, base=444, amp=2, fill=f"url(#{u}-prairie)")
    out.append(pl)
    out.append(grass(260, 62, (-10, 350, 610, 380), ["#D8BC6A", "#B89A4E", "#E8D08A", "#8E7A3E"], h=(3, 7), sw=1.2))
    for bx, by, bs, fl in ((104, 370, 0.17, False), (140, 374, 0.19, False), (200, 367, 0.15, True)):
        out.append(f'<ellipse cx="{bx + 150 * bs * 0.5 + 18:.1f}" cy="{by:.1f}" rx="{150 * bs * 0.7:.1f}" ry="1.6" fill="#4A3A2A" opacity="0.4"/>')
        out.append(bison(bx if not fl else bx + 150 * bs, by, bs, rim="#FFC27A", flip=fl))
    out.append(grass(420, 63, (-10, 372, 610, 444), ["#D8BC6A", "#C8A454", "#E8D08A", "#9A843E", "#F2DC98"], h=(8, 20), sw=1.6))

    # --- foreground ledge of banded rock on the right, a bighorn ram watching the sun go down
    ledge = rough([(300, 444), (318, 404), (346, 392), (392, 384), (450, 382), (510, 384), (560, 378), (610, 380)], 71, amp=3, depth=3)
    shape = ledge + [(610, 446), (300, 446)]
    cid = f"{u}-ld"
    out.append(f'<clipPath id="{cid}"><polygon points="{P(shape)}"/></clipPath>' + poly(shape, f"url(#{u}-ledge)"))
    lb = [(392, "#F2D8BC"), (402, "#E2A28E"), (414, "#F0CCA8"), (422, "#C87A62"), (428, "#E8B488"), (440, "#E0A066")]
    g = []
    for by, col in lb:
        g.append(poly([(x, by + 1.5 * math.sin(x / 13 + by)) for x in range(296, 616, 6)] + [(612, 446), (296, 446)], col))
    g.append(streaks(70, 72, (300, 380, 610, 444), ["#9A6266", "#FFF2E0", "#B8806E"], w=(1, 2.4), length=(8, 26), opacity=(0.15, 0.4), slant=0.05))
    # cracks and a few loose blocks on the ledge face
    g.append('<g stroke="#7A4A5A" stroke-width="1.4" fill="none" opacity="0.5"><path d="M 360 396 l 4 14 l -3 12"/><path d="M 432 392 l -3 16 l 5 10 l -2 14"/><path d="M 528 390 l 2 20 l 6 8"/></g>')
    # flat lit top of the ledge, and its shaded right-hand face
    g.append(poly(ledge[1:] + [(x, y + 7) for x, y in ledge[1:]][::-1], "#FBE6C8", ' opacity="0.8"'))
    g.append(poly([(560, 378), (610, 380), (610, 446), (574, 446)], "#5A3A6E", ' opacity="0.35"'))
    out.append(f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>")
    out.append(f'<polyline points="{P(ledge[:len(ledge) - 2])}" fill="none" stroke="#FFE6B8" stroke-width="2" opacity="0.9"/>')
    # the ram's long shadow stretching away from the sun across the ledge
    rx_, rb = 470, 384
    out.append(f'<path d="M {rx_ - 12} {rb} L {rx_ + 30} {rb - 1} L {rx_ + 124} {rb + 3} Q {rx_ + 136} {rb + 5} {rx_ + 126} {rb + 7} L {rx_ + 26} {rb + 4} Z" fill="#6A3E5E" opacity="0.38"/>')
    out.append(bighorn(rx_, rb, 1.3))
    # sage and yucca in the foreground grass, lit seed heads
    out.append('<g fill="#5A3E4E" opacity="0.28">' + "".join(f'<path d="M {x - 10} {y} L {x + L} {y + 2} L {x + L - 6} {y + 5} L {x - 8} {y + 4} Z"/>'
               for x, y, L in ((96, 436, 70), (250, 440, 56), (40, 414, 60), (150, 424, 60), (200, 410, 54), (286, 430, 50))) + "</g>")
    out.append(yucca(96, 436, 26, 81))
    out.append(yucca(250, 440, 20, 82))
    for k, (cx, cy) in enumerate(((40, 414), (150, 424), (200, 410), (286, 430))):     # sagebrush clumps, lit on top
        out.append(blobs(18, 83 + k, (cx - 14, cy - 8, cx + 14, cy + 4), ["#8A8C66", "#9A9A72", "#74785A"], r=(2.5, 5), opacity=(0.9, 1), squash=0.8))
        out.append(blobs(10, 90 + k, (cx - 12, cy - 10, cx + 8, cy - 2), ["#C8CCA0", "#E0D8A8"], r=(1.6, 3), opacity=(0.7, 1), squash=0.8))
    out.append(grass(120, 84, (-10, 410, 300, 446), ["#F2DC98", "#E8C878", "#C8A454"], h=(10, 24), sw=1.8))
    # a hawk riding the last thermals
    out.append('<path d="M 112 132 q 10 -8 20 -2 q 4 -1 6 2 q 2 -3 6 -2 q 10 -6 20 2 q -12 0 -20 3 q -2 3 -6 0 q -8 -3 -26 -3 Z" fill="#3A2A44"/>')
    out.append(gulls([(70, 162, 7), (84, 156, 5)], "#3A2A44", sw=1.6))
    return "\n".join(out)


# ---------------------------------------------------------------- Annapolis (City Dock full of sailboats, State House on the hill)
def state_house(cx, base, s, u):
    """Maryland State House: Georgian brick block, portico, and the tall white timber dome (octagonal drum, bell dome,
    two-stage lantern with balustrades, acorn and lightning-rod spire). Local units, scaled by s."""
    out = [defs(lg(f"{u}-dome", [(0, "#FFFFFF"), (0.6, "#E8ECF0"), (1, "#A8B4C4")], 0, 0, 1, 0))]
    g = []
    # main block
    g.append('<rect x="-80" y="-44" width="160" height="44" fill="#B4553E"/><rect x="-80" y="-44" width="160" height="44" fill="url(#' + u + '-brk)"/>')
    g.append('<polygon points="-84,-44 0,-62 84,-44" fill="#5A4A50"/><polygon points="-84,-44 0,-62 0,-44" fill="#7A6A6E"/>')
    g.append("".join(f'<rect x="{x}" y="-36" width="7" height="12" fill="#2E3446"/><rect x="{x - 1}" y="-37" width="9" height="1.6" fill="#F4EEE6"/>'
                     f'<rect x="{x}" y="-18" width="7" height="12" fill="#2E3446"/><rect x="{x - 1}" y="-19" width="9" height="1.6" fill="#F4EEE6"/>' for x in (-72, -58, -44, 38, 52, 66)))
    # portico with pediment
    g.append('<rect x="-24" y="-46" width="48" height="46" fill="#F2ECE2"/><polygon points="-28,-46 0,-60 28,-46" fill="#FFFFFF"/><polygon points="-22,-48 0,-57 22,-48" fill="#D8D0C8"/>')
    g.append("".join(f'<rect x="{x}" y="-44" width="4" height="44" fill="#FFFFFF"/><rect x="{x + 3}" y="-44" width="1.4" height="44" fill="#B8B0AE"/>' for x in (-20, -10, 0, 10, 18)))
    g.append('<rect x="-6" y="-16" width="12" height="16" fill="#3A2A2A"/>')
    # dome: square base, octagonal drum, bell dome, lantern stages, acorn, spire
    g.append('<rect x="-22" y="-80" width="44" height="20" fill="#F2ECE2"/><rect x="-22" y="-80" width="44" height="3" fill="#FFFFFF"/><rect x="4" y="-77" width="18" height="17" fill="#C8C0BC" opacity="0.6"/>')
    g.append(f'<rect x="-18" y="-110" width="36" height="30" fill="url(#{u}-dome)"/>')
    g.append("".join(f'<path d="M {x} -84 L {x} -100 Q {x + 3} -105 {x + 6} -100 L {x + 6} -84 Z" fill="#3A4258"/>' for x in (-13, -3, 7)))
    g.append('<rect x="-20" y="-112" width="40" height="3" fill="#FFFFFF"/><rect x="-20" y="-84" width="40" height="2" fill="#D8D0C8"/>')
    g.append(f'<path d="M -19 -112 Q -18 -134 0 -140 Q 18 -134 19 -112 Z" fill="url(#{u}-dome)"/>')
    g.append('<path d="M 2 -140 Q 18 -134 19 -112 L 8 -112 Q 9 -130 2 -140 Z" fill="#9AA6B8" opacity="0.6"/>')
    g.append('<path d="M -10 -113 Q -9 -130 0 -138 M 10 -113 Q 9 -130 0 -138" stroke="#C8D0DA" stroke-width="1" fill="none"/>')
    g.append('<rect x="-12" y="-146" width="24" height="6" fill="#FFFFFF"/>' + "".join(f'<rect x="{x}" y="-149" width="1.4" height="3" fill="#FFFFFF"/>' for x in range(-12, 13, 3)) + '<rect x="-12" y="-150" width="25" height="1.2" fill="#FFFFFF"/>')
    g.append('<rect x="-8" y="-166" width="16" height="16" fill="url(#' + u + '-dome)"/>' + "".join(f'<path d="M {x} -152 L {x} -161 Q {x + 1.5} -164 {x + 3} -161 L {x + 3} -152 Z" fill="#3A4258"/>' for x in (-6, -1.5, 3)))
    g.append('<rect x="-9" y="-168" width="18" height="2.4" fill="#FFFFFF"/>' + "".join(f'<rect x="{x}" y="-171" width="1.2" height="3" fill="#FFFFFF"/>' for x in range(-8, 9, 3)) + '<rect x="-9" y="-172" width="18.5" height="1.2" fill="#FFFFFF"/>')
    g.append('<path d="M -6 -172 Q -5 -182 0 -184 Q 5 -182 6 -172 Z" fill="url(#' + u + '-dome)"/><ellipse cx="0" cy="-187" rx="2.6" ry="3.4" fill="#E8D8A8"/>')
    g.append('<line x1="0" y1="-190" x2="0" y2="-206" stroke="#6A6A7A" stroke-width="1.4"/>')
    return f'<g transform="translate({cx} {base}) scale({s})">' + "".join(out) + "".join(g) + "</g>"


def annapolis():
    u = "an"
    C = Cam(f=380, cx=300, vpy=300, eye=2.4)
    out = [defs(
        lg(f"{u}-sky", [(0, "#2E6EB4"), (0.5, "#6EA4D8"), (0.85, "#B8D6EC"), (1, "#E6F0F4")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-cl", [(0, "#FFFFFF"), (1, "#E4ECF4")]),
        lg(f"{u}-water", [(0, "#8EB8CC"), (0.3, "#3E7EA0"), (1, "#1E4E72")], 0, 300, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-hill", [(0, "#5A8A4E"), (1, "#3E6A3E")]),
        f'<pattern id="{u}-brk" width="6" height="3" patternUnits="userSpaceOnUse"><rect width="6" height="3" fill="none"/><path d="M 0 2.6 L 6 2.6 M 3 0 L 3 1.3 M 0 1.3 L 6 1.3" stroke="#7A3A2A" stroke-width="0.4" opacity="0.5"/></pattern>',
        lg(f"{u}-sail", [(0, "#FFFFFF"), (1, "#D8E0EA")], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    for x, y, w in ((110, 116, 130), (480, 98, 150), (560, 168, 80), (40, 186, 70)):
        out.append(cumulus(x, y, w, w * 0.34, x, f"{u}-cl", hi="#FFFFFF", hi_op=0.8, shade="#9AAAC4", shade_op=0.35, n=int(w / 3)))
    # the hill of the old town, trees, St. Anne's steeple and the State House dome
    out.append(f'<path d="M -10 300 L -10 252 Q 80 236 180 232 Q 300 222 420 232 Q 520 240 610 252 L 610 300 Z" fill="url(#{u}-hill)"/>')
    rnd = random.Random(4)
    for _ in range(70):
        x = rnd.uniform(-10, 610)
        y = 236 + abs(x - 300) * 0.06 + rnd.uniform(-4, 30)
        r = rnd.uniform(8, 16)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{rnd.choice(["#3E6A3E", "#4E7A44", "#36603A", "#5A8A4A"])}"/><circle cx="{x - r * 0.3:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.5:.1f}" fill="#9ABE6A" opacity="0.5"/>')
    # St. Anne's church: brick tower with white belfry and spire
    sx_ = 110
    out.append(f'<rect x="{sx_ - 26}" y="214" width="40" height="40" fill="#A84E3A"/><polygon points="{P([(sx_ - 28, 214), (sx_ - 6, 202), (sx_ + 16, 214)])}" fill="#5A4A50"/>'
               f'<rect x="{sx_ - 11}" y="172" width="22" height="70" fill="#B05440"/><rect x="{sx_ + 4}" y="172" width="7" height="70" fill="#7A3A2E"/>'
               f'<rect x="{sx_ - 12}" y="170" width="24" height="3" fill="#F4EEE4"/>'
               f'<circle cx="{sx_}" cy="186" r="5.5" fill="#F4EEE4"/><path d="M {sx_} 186 L {sx_} 182.5 M {sx_} 186 L {sx_ + 2.5} 187" stroke="#2A2A3A" stroke-width="1"/>'
               f'<rect x="{sx_ - 4}" y="198" width="8" height="12" fill="#2E3446"/><path d="M {sx_ - 4} 198 Q {sx_} 193 {sx_ + 4} 198 Z" fill="#2E3446"/>'
               f'<rect x="{sx_ - 9}" y="150" width="18" height="20" fill="#F4F0EA"/><path d="M {sx_ - 5} 168 L {sx_ - 5} 156 Q {sx_ - 3} 153 {sx_ - 1} 156 L {sx_ - 1} 168 Z M {sx_ + 1} 168 L {sx_ + 1} 156 Q {sx_ + 3} 153 {sx_ + 5} 156 L {sx_ + 5} 168 Z" fill="#3A4258"/>'
               f'<rect x="{sx_ + 4}" y="150" width="5" height="20" fill="#C8D0DA" opacity="0.7"/><rect x="{sx_ - 10}" y="148" width="20" height="2.6" fill="#FFFFFF"/>'
               f'<rect x="{sx_ - 6}" y="136" width="12" height="12" fill="#F4F0EA"/><path d="M {sx_ - 7} 136 L {sx_} 110 L {sx_ + 7} 136 Z" fill="#F4F0EA"/><path d="M {sx_} 110 L {sx_ + 7} 136 L {sx_ + 1} 136 Z" fill="#B8C0CC"/>'
               f'<line x1="{sx_}" y1="110" x2="{sx_}" y2="100" stroke="#C8A040" stroke-width="1.6"/><path d="M {sx_ - 3} 104 L {sx_ + 3} 104" stroke="#C8A040" stroke-width="1.4"/>')
    out.append(state_house(300, 270, 0.86, u))
    # waterfront: colonial brick row around the head of the dock, the Market House in the middle
    rnd = random.Random(9)
    x = -10
    cols = ["#A84E3A", "#B85E44", "#8E4434", "#C8B8A0", "#E8DCC8", "#6E8A9E", "#C86A4A"]
    while x < 610:
        w = rnd.uniform(26, 40)
        h = rnd.uniform(30, 44)
        if 236 < x + w / 2 < 364:
            x += w
            continue
        col = rnd.choice(cols)
        top = 300 - h
        out.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{col}"/>')
        out.append(f'<polygon points="{P([(x - 1, top), (x + w / 2, top - 9), (x + w + 1, top)])}" fill="#4A4048"/>')
        out.append(f'<rect x="{x + w / 2 - 3:.1f}" y="{top - 6:.1f}" width="6" height="5" fill="#F4EEE6"/>')
        for wx in (x + w * 0.2, x + w * 0.45, x + w * 0.7):
            for wy in (top + 6, top + 18):
                if wy + 8 < 296:
                    out.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="5" height="8" fill="#2E3446"/><rect x="{wx - 1:.1f}" y="{wy - 1:.1f}" width="7" height="1.4" fill="#F4EEE6"/>')
        out.append(f'<rect x="{x + w - 4:.1f}" y="{top:.1f}" width="4" height="{h:.1f}" fill="#000" opacity="0.15"/>')
        x += w + rnd.uniform(0, 2)
    out.append('<rect x="244" y="276" width="112" height="24" fill="#C8B8A0"/><polygon points="240,276 300,262 360,276" fill="#5A5058"/>'
               + "".join(f'<path d="M {x} 298 L {x} 284 Q {x + 4} 279 {x + 8} 284 L {x + 8} 298 Z" fill="#3A4258"/>' for x in range(252, 350, 14))
               + '<rect x="296" y="256" width="8" height="8" fill="#F4EEE6"/><path d="M 296 256 L 300 250 L 304 256 Z" fill="#5A5058"/>')
    # bulkheads with pilings along both sides of the dock
    out.append(f'<rect x="0" y="298" width="600" height="6" fill="#8A7A6A"/>')
    # the water
    out.append(f'<rect x="0" y="303" width="600" height="141" fill="url(#{u}-water)"/>')
    out.append(f'<rect x="250" y="303" width="100" height="40" fill="#F4EEE6" opacity="0.12"/>')
    out.append(ripples(260, 5, (0, 304, 600, 444), ["#2A5E84", "#5E9AB8", "#1E4A6E"], w=(8, 36), h=(1, 2.4), opacity=(0.4, 0.8), persp=(300, 444)))
    out.append(ripples(120, 6, (0, 304, 600, 444), ["#FFFFFF", "#DDEEF6"], w=(3, 12), h=(0.8, 1.6), opacity=(0.5, 1), persp=(300, 444)))
    # moored sailboats along both sides, receding up the dock; reflections of hulls and masts
    boats = []
    for sgn in (-1, 1):
        for i, Z in enumerate([19 * 1.27 ** k for k in range(10)]):
            if Z > 160:
                break
            boats.append((Z, sgn * random.Random(i + sgn).uniform(9, 13), sgn, i))
    hulls = ["#FFFFFF", "#F4F0E8", "#1E3A5E", "#FFFFFF", "#8A2E2E", "#F4F0E8", "#2E5A4A"]
    for Z, X, sgn, i in sorted(boats, key=lambda b: -b[0]):
        x, y = C(X, 0, Z)
        k = C.f / Z / 10  # px per m / 10
        L = 10 * k * 10 * 0.42
        hc = hulls[(i * 3 + (sgn > 0)) % len(hulls)]
        mh = C.f * random.Random(i * 7 + sgn).uniform(11, 15) / Z
        # reflection
        out.append(f'<rect x="{x - L / 2:.1f}" y="{y + 1:.1f}" width="{L:.1f}" height="{L * 0.18:.1f}" fill="{hc}" opacity="0.25"/>')
        out.append(f'<path d="M {x:.1f} {y + 2:.1f} ' + "".join(f'l {(-1) ** j * max(0.8, k * 1.2):.1f} {mh * 0.12:.1f} ' for j in range(5)) + f'" stroke="#E8EEF4" stroke-width="{max(0.6, k * 0.25):.1f}" fill="none" opacity="0.5"/>')
        # hull (stern toward us), cabin, boom, furled sail, mast and stays
        out.append(f'<path d="M {x - L / 2:.1f} {y - L * 0.18:.1f} L {x + L / 2:.1f} {y - L * 0.18:.1f} Q {x + L * 0.48:.1f} {y - L * 0.02:.1f} {x + L * 0.3:.1f} {y:.1f} L {x - L * 0.3:.1f} {y:.1f} Q {x - L * 0.48:.1f} {y - L * 0.02:.1f} {x - L / 2:.1f} {y - L * 0.18:.1f} Z" fill="{hc}"/>')
        out.append(f'<path d="M {x + L * 0.1:.1f} {y - L * 0.18:.1f} L {x + L / 2:.1f} {y - L * 0.18:.1f} Q {x + L * 0.48:.1f} {y - L * 0.02:.1f} {x + L * 0.3:.1f} {y:.1f} L {x + L * 0.05:.1f} {y:.1f} Z" fill="#000" opacity="0.1"/>')
        out.append(f'<rect x="{x - L * 0.36:.1f}" y="{y - L * 0.035:.1f}" width="{L * 0.72:.1f}" height="{max(0.6, L * 0.025):.1f}" fill="{"#C8573E" if i % 2 else "#2E5A8A"}"/>')
        out.append(f'<path d="M {x - L * 0.5:.1f} {y - L * 0.18:.1f} L {x - L * 0.5:.1f} {y - L * 0.26:.1f} L {x + L * 0.5:.1f} {y - L * 0.26:.1f} L {x + L * 0.5:.1f} {y - L * 0.18:.1f}" stroke="#C8CCD4" stroke-width="{max(0.5, L * 0.012):.1f}" fill="none"/>')
        out.append(f'<rect x="{x - L / 2:.1f}" y="{y - L * 0.16:.1f}" width="{L:.1f}" height="{max(0.8, L * 0.03):.1f}" fill="{"#1E3A5E" if hc in ("#FFFFFF", "#F4F0E8") else "#F4F0E8"}"/>')
        out.append(f'<rect x="{x - L * 0.22:.1f}" y="{y - L * 0.3:.1f}" width="{L * 0.44:.1f}" height="{L * 0.14:.1f}" rx="{L * 0.04:.1f}" fill="#F4F0E8"/><rect x="{x - L * 0.18:.1f}" y="{y - L * 0.27:.1f}" width="{L * 0.36:.1f}" height="{L * 0.05:.1f}" fill="#3A4258"/>')
        mx = x + random.Random(i).uniform(-0.1, 0.1) * L
        out.append(f'<line x1="{mx:.1f}" y1="{y - L * 0.3:.1f}" x2="{mx:.1f}" y2="{y - mh:.1f}" stroke="#E8E4DC" stroke-width="{max(0.9, k * 0.5):.1f}"/>')
        out.append(f'<line x1="{mx:.1f}" y1="{y - mh:.1f}" x2="{x - L * 0.45:.1f}" y2="{y - L * 0.16:.1f}" stroke="#8A8A9A" stroke-width="0.6" opacity="0.7"/><line x1="{mx:.1f}" y1="{y - mh:.1f}" x2="{x + L * 0.45:.1f}" y2="{y - L * 0.16:.1f}" stroke="#8A8A9A" stroke-width="0.6" opacity="0.7"/>')
        out.append(f'<rect x="{mx - L * 0.05:.1f}" y="{y - L * 0.44:.1f}" width="{L * 0.1:.1f}" height="{L * 0.12:.1f}" rx="{L * 0.04:.1f}" fill="{random.Random(i + 3).choice(["#2E4A7A", "#C8573E", "#F4F0E8", "#3E6A8A"])}"/>')
        out.append(f'<rect x="{x - L / 2:.1f}" y="{y - L * 0.16:.1f}" width="{L * 0.18:.1f}" height="{L * 0.16:.1f}" fill="#000" opacity="{0.08 if sgn < 0 else 0}"/>')
    # a Chesapeake skipjack under full sail coming in, raked mast and big white mainsail
    kx, ky = 160, 352
    out.append(f'<path d="M {kx - 50} {ky + 4} q 40 6 100 0" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.6"/>')
    out.append(f'<path d="M {kx - 46} {ky - 10} L {kx + 52} {ky - 12} Q {kx + 44} {ky + 2} {kx + 30} {ky + 4} L {kx - 36} {ky + 4} Z" fill="#F8F4EC"/><path d="M {kx - 46} {ky - 10} L {kx + 52} {ky - 12} L {kx + 50} {ky - 9} L {kx - 45} {ky - 7} Z" fill="#2E4A7A"/>')
    out.append(f'<path d="M {kx - 8} {ky - 12} L {kx + 10} {ky - 120}" stroke="#C8A878" stroke-width="2.4"/>')
    out.append(f'<path d="M {kx + 8} {ky - 112} L {kx - 50} {ky - 18} L {kx + 2} {ky - 16} Z" fill="url(#{u}-sail)"/><path d="M {kx + 8} {ky - 112} L {kx - 50} {ky - 18}" stroke="#C8D0DA" stroke-width="1.2"/>')
    out.append(f'<path d="M {kx + 12} {ky - 100} L {kx + 64} {ky - 14} L {kx + 14} {ky - 16} Z" fill="#EEF2F6"/><path d="M {kx + 12} {ky - 100} L {kx + 64} {ky - 14}" stroke="#B8C4D0" stroke-width="1"/>')
    out.append(f'<path d="M {kx - 50} {ky - 18} L {kx + 2} {ky - 16}" stroke="#8A6A4A" stroke-width="2"/>')
    out.append(f'<path d="M {kx + 52} {ky - 12} L {kx + 74} {ky - 16}" stroke="#8A6A4A" stroke-width="1.6"/>')
    out.append(walker(kx - 24, ky - 10, 14, "#C8573E", pose="stand_side", facing=1, seed=51, pal={"hat_kind": "cap", "hat": "#F4F2EC"}))
    out.append(f'<g opacity="0.22" transform="translate(0 {2 * ky + 6}) scale(1 -1)"><path d="M {kx + 8} {ky - 112} L {kx - 50} {ky - 18} L {kx + 2} {ky - 16} Z" fill="#FFFFFF"/></g>')
    # a paddler in a red kayak crossing the foreground
    kx2, ky2 = 112, 412
    out.append(f'<path d="M {kx2 - 60} {ky2 + 4} q 30 4 56 1" stroke="#FFFFFF" stroke-width="1.6" fill="none" opacity="0.6"/>'
               f'<path d="M {kx2 - 34} {ky2} Q {kx2} {ky2 - 8} {kx2 + 36} {ky2 - 1} Q {kx2} {ky2 + 6} {kx2 - 34} {ky2} Z" fill="#D8463A"/><path d="M {kx2 - 30} {ky2 - 1} Q {kx2} {ky2 - 7} {kx2 + 32} {ky2 - 1.5}" stroke="#FF9A7A" stroke-width="1.4" fill="none"/>'
               f'<ellipse cx="{kx2}" cy="{ky2 - 3}" rx="7" ry="2" fill="#2A2228"/>'
               + F.person(kx2, ky2 - 3, 42, "paddle", 1, {"top": "#F2C24A", "top_kind": "tank", "no_legs": True, "hat_kind": "cap", "hat": "#2A2228", "season": "summer"},
                          seed=52, rim="#FFF6E0", light=-1, shadow=0)
               + f'<path d="M {kx2 - 22} {ky2 - 2} L {kx2 + 20} {ky2 - 24}" stroke="#2A2228" stroke-width="1.8"/>'
               f'<ellipse cx="{kx2 - 23}" cy="{ky2 - 1}" rx="4" ry="1.8" fill="#2A2228" transform="rotate(-28 {kx2 - 23} {ky2 - 1})"/><ellipse cx="{kx2 + 21}" cy="{ky2 - 25}" rx="4" ry="1.8" fill="#2A2228" transform="rotate(-28 {kx2 + 21} {ky2 - 25})"/>'
               f'<path d="M {kx2 - 26} {ky2 + 3} Q {kx2} {ky2 + 9} {kx2 + 28} {ky2 + 3}" stroke="#D8463A" stroke-width="3" fill="none" opacity="0.25"/>')
    # foreground: a weathered dock corner with pilings, a coiled line, and a gull on a post
    out.append('<path d="M 430 444 L 470 400 L 610 400 L 610 444 Z" fill="#9A8064"/><path d="M 470 400 L 610 400 L 610 406 L 466 406 Z" fill="#C8AE8A"/>'
               + "".join(f'<line x1="{x}" y1="{400 + (x - 470) * 0.0:.0f}" x2="{x - 40}" y2="444" stroke="#7A6450" stroke-width="1.4"/>' for x in range(490, 620, 18)))
    for px, top in ((478, 370), (560, 360)):
        out.append(f'<rect x="{px - 7}" y="{top}" width="14" height="{444 - top}" fill="#6E5644"/><rect x="{px - 7}" y="{top}" width="5" height="{444 - top}" fill="#A88A6A"/><ellipse cx="{px}" cy="{top}" rx="7" ry="2.6" fill="#C8AE8A"/>')
    out.append('<g fill="none" stroke="#E8DCC0" stroke-width="2.4"><ellipse cx="520" cy="416" rx="16" ry="5"/><ellipse cx="520" cy="414" rx="11" ry="3.6"/><ellipse cx="520" cy="412" rx="6" ry="2"/></g>')
    out.append('<g transform="translate(560 360)"><path d="M -6 0 Q -10 -10 -2 -14 Q 6 -16 10 -10 L 16 -12 L 10 -6 Q 8 0 -6 0 Z" fill="#FFFFFF"/><path d="M -6 -4 Q 2 -8 10 -6 L 2 -2 Z" fill="#9AA4B4"/>'
               '<circle cx="-3" cy="-16" r="4.4" fill="#FFFFFF"/><path d="M 1 -16 L 6 -15 L 1 -14 Z" fill="#E8B030"/><circle cx="-2" cy="-17" r="0.9" fill="#1E1E2A"/>'
               '<path d="M -2 0 L -2 4 M 2 0 L 2 4" stroke="#E8A040" stroke-width="1.4"/></g>')
    out.append(gulls([(380, 150, 10), (398, 160, 7), (200, 130, 9)], "#2A3A5A"))
    return "\n".join(out)


BUILD = {
    "los-angeles": (los_angeles, "LOS ANGELES", "CALIFORNIA · USA", "#24173A", "#FF8A5C", "#FBEBD4", "#FFB66E"),
    "san-diego": (san_diego, "SAN DIEGO", "CALIFORNIA · USA", "#163A4A", "#FFC27A", "#FBEBD4", "#FFD898"),
    "portland": (portland, "PORTLAND", "OREGON · USA", "#1E2E4A", "#F08AA0", "#FBEBD4", "#F6B6B8"),
    "maui": (maui, "MAUI", "HAWAII · USA", "#22183A", "#FF9A52", "#FBEBD4", "#FFB45E"),
    "brooklyn": (brooklyn, "BROOKLYN", "NEW YORK · USA", "#2A2030", "#D8704A", "#FBEBD4", "#F2C49A"),
    "badlands": (badlands, "BADLANDS", "SOUTH DAKOTA · NATIONAL PARK", "#2E2240", "#F09A6C", "#FBEBD4", "#F6C49A"),
    "annapolis": (annapolis, "ANNAPOLIS", "MARYLAND · USA", "#14284A", "#E8B04A", "#FBEBD4", "#F2C878"),
    "st-louis": (st_louis, "ST. LOUIS", "MISSOURI · USA", "#1C2238", "#F5A04A", "#FBEBD4", "#FFC478"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("places", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
