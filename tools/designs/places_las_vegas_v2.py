"""American Places, Las Vegas v2: the Welcome sign at golden hour (daylight, no neon night).

Looking north up the boulevard from the south end of the Strip: the mid-century welcome sign (public-domain
design, never trademarked) on its desert-planted island, the road running to a hazy Strip skyline under a low
golden sun, the Spring Mountains and Red Rock to the west, a Joshua tree framing the left and a Mojave garden
of yucca, barrel cactus, brittlebush and creosote in front. Warm cream / peach sky, pale aqua, sage, terracotta.

Writes the poster to the scratchpad (new-places/las-vegas.svg) for the owners to approve before it goes into
designs/places/.
"""
import math
import pathlib
import random
import sys

from paint import P, dots, glow, lg, mist, rg, ridge_poly, rough, streaks, y_on
from places_painted import Cam
from common import SERIF_IT, MONO, measure, fit_size
import re
import poster as PM
from poster import ANTON
import figures as F

OUT = pathlib.Path("/tmp/claude-0/-home-claude-little-hive-house/126373fb-bcff-5469-8b97-3f0485f13186/scratchpad/new-places")
U = "lv2"

# camera: horizon at art y 310, vanishing point of the boulevard at x 170
C = Cam(f=420, cx=170, vpy=310, eye=2.5)
SUN = (198, 150)


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


def poly(pts, fill, extra=""):
    return f'<polygon points="{P(pts)}" fill="{fill}"{extra}/>'


def smooth(pts, closed=False):
    """Catmull-Rom through points -> cubic bezier path data."""
    if closed:
        pts = pts + pts[:2]
    d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f} "
    n = len(pts)
    for i in range(n - 1 if not closed else n - 2):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f} "
    return d + ("Z" if closed else "")


def qpt(p0, p1, p2, t):
    u = 1 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0], u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


def tube(p0, p1, p2, w0, w1, n=10, off=0.0):
    """Tapered limb along a quadratic curve; off shifts the strip sideways (fraction of width, + = right normal)."""
    L, R = [], []
    for i in range(n + 1):
        t = i / n
        x, y = qpt(p0, p1, p2, t)
        ta = qpt(p0, p1, p2, min(1, t + 0.02))
        tb = qpt(p0, p1, p2, max(0, t - 0.02))
        dx, dy = ta[0] - tb[0], ta[1] - tb[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = (w0 + (w1 - w0) * t) / 2
        cx, cy = x + nx * w * off * 2, y + ny * w * off * 2
        L.append((cx + nx * w, cy + ny * w))
        R.append((cx - nx * w, cy - ny * w))
    return L + R[::-1]


# ---------------------------------------------------------------- sky
def sky():
    out = [defs(
        lg(f"{U}-sky", [(0, "#6FB2C6"), (0.22, "#A9D2D4"), (0.44, "#F2D9B4"), (0.64, "#F4BE86"), (0.84, "#EE9E66"), (1, "#E58C58")], 0, 40, 0, 312, units="userSpaceOnUse"),
        rg(f"{U}-sunh", [(0, "#FFF4D2", 0.95), (0.25, "#FFE2A6", 0.6), (0.6, "#FBD49A", 0.22), (1, "#FBD49A", 0)]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{U}-sky)"/>')
    out.append(f'<circle cx="{SUN[0]}" cy="{SUN[1]}" r="300" fill="url(#{U}-sunh)"/>')
    # long, flat golden-hour clouds: a cream body, a peach underside, a lit upper rim
    rc = random.Random(7)
    for cx, cy, w, k in ((420, 92, 230, 1.0), (88, 112, 170, 0.9), (330, 126, 140, 0.7), (520, 150, 110, 0.6), (40, 168, 90, 0.5)):
        under, body, lit = [], [], []
        for i in range(10):
            x = cx + rc.uniform(-0.5, 0.5) * w * 0.8
            y = cy + rc.uniform(-4, 4) * k
            rx = rc.uniform(0.12, 0.3) * w
            ry = rc.uniform(3.2, 6.5) * k
            under.append(f'<ellipse cx="{x + 4:.1f}" cy="{y + 2.5:.1f}" rx="{rx:.1f}" ry="{ry:.1f}"/>')
            body.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx * 0.92:.1f}" ry="{ry * 0.8:.1f}"/>')
            lit.append(f'<ellipse cx="{x - rx * 0.12:.1f}" cy="{y - ry * 0.35:.1f}" rx="{rx * 0.6:.1f}" ry="{max(1.2, ry * 0.32):.1f}"/>')
        out.append(f'<g fill="#EFAE8A" opacity="{0.55 * k + 0.2:.2f}">' + "".join(under) + "</g>")
        out.append(f'<g fill="#FCE6CC" opacity="0.9">' + "".join(body) + "</g>")
        out.append(f'<g fill="#FFF8EA" opacity="0.85">' + "".join(lit) + "</g>")
    # the low sun
    out.append(glow(SUN[0], SUN[1], 70, "#FFF1C4", f"{U}-sg", 0.9))
    out.append(f'<circle cx="{SUN[0]}" cy="{SUN[1]}" r="23" fill="#FFE3A0"/><circle cx="{SUN[0] - 3}" cy="{SUN[1] - 3}" r="15" fill="#FFEDBA" opacity="0.7"/>')
    # a pair of ravens riding the warm air, top right
    out.append('<g fill="none" stroke="#6A4A3A" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round">'
               '<path d="M 452 122 q 6 -5 12 0 q 6 -5 12 0"/><path d="M 486 108 q 4 -3.4 8 0 q 4 -3.4 8 0"/></g>')
    return "\n".join(out)


# ---------------------------------------------------------------- mountains
def mountains():
    out = [defs(
        lg(f"{U}-spr", [(0, "#9FB8C2"), (0.6, "#BCC6C2"), (1, "#E3CDB6")], 0, 200, 0, 312, units="userSpaceOnUse"),
        lg(f"{U}-rr", [(0, "#E6995F"), (0.5, "#D27A50"), (1, "#E2A27A")], 0, 262, 0, 312, units="userSpaceOnUse"),
        lg(f"{U}-east", [(0, "#D8C4B6"), (1, "#EDD2B8")], 0, 270, 0, 312, units="userSpaceOnUse"),
    )]
    # Spring Mountains to the west (left): Charleston Peak with late snow, hazed blue-grey
    pts = [(-10, 232), (30, 218), (62, 206), (96, 196), (118, 202), (146, 214), (176, 226), (214, 238), (250, 252), (290, 266), (340, 276), (400, 282)]
    line = rough(pts, 11, amp=6, depth=4)
    shape = line + [(400, 312), (-10, 312)]
    out.append(poly(shape, f"url(#{U}-spr)"))
    cid = f"{U}-sprc"
    out.append(f'<clipPath id="{cid}"><polygon points="{P(shape)}"/></clipPath>')
    g = [streaks(70, 12, (-10, 196, 400, 300), ["#8EA6B2", "#A9B9BE", "#CFD6D0"], w=(0.8, 2.2), length=(10, 40), opacity=(0.25, 0.5), slant=0.35)]
    # snowfields on the summit ridge
    for x, y, w in ((84, 202, 26), (102, 199, 18), (60, 211, 16), (128, 208, 14)):
        g.append(f'<path d="M {x - w / 2} {y + 4} q {w * 0.25} -6 {w / 2} -5 q {w * 0.3} 1 {w / 2} 6 q -{w * 0.3} -2 -{w / 2} 1 q -{w * 0.2} -2 -{w / 2} -2 Z" fill="#FBF4EA" opacity="0.85"/>')
    # sun-facing (right) flanks glow warm
    g.append(f'<polygon points="{P([(96, 196), (118, 202), (146, 214), (176, 226), (214, 238), (250, 252), (290, 266), (290, 300), (130, 300)])}" fill="#FFD8AE" opacity="0.28"/>')
    out.append(f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>")
    out.append(f'<polyline points="{P([p for p in line if p[0] > 92])}" fill="none" stroke="#FFE6C2" stroke-width="1.6" opacity="0.75"/>')
    out.append(mist(160, 290, 260, 26, "#F6C79A", f"{U}-mh1", 0.32))
    # low desert ranges to the east, mostly behind the sign
    pl, _ = ridge_poly([(300, 300), (360, 290), (420, 284), (470, 288), (520, 280), (560, 286), (610, 292)], 13, base=312, amp=3, fill=f"url(#{U}-east)")
    out.append(pl)
    # Red Rock: the striped sandstone of the Calico Hills under the grey escarpment
    rr = [(-10, 286), (14, 276), (40, 270), (66, 274), (88, 268), (112, 276), (140, 284), (170, 292), (200, 300)]
    rl = rough(rr, 14, amp=3, depth=3)
    shape = rl + [(200, 312), (-10, 312)]
    out.append(poly(shape, f"url(#{U}-rr)"))
    cid = f"{U}-rrc"
    bands = []
    for i, (y, col, op) in enumerate(((276, "#F6D2AE", 0.7), (283, "#C9663E", 0.45), (289, "#F4CBA2", 0.6), (295, "#C65F37", 0.4), (301, "#F2C29A", 0.5))):
        wav = [(x, y + 2.5 * math.sin(x / 23 + i)) for x in range(-10, 211, 10)]
        bands.append(f'<polyline points="{P(wav)}" fill="none" stroke="{col}" stroke-width="3.2" opacity="{op}"/>')
    out.append(f'<clipPath id="{cid}"><polygon points="{P(shape)}"/></clipPath><g clip-path="url(#{cid})">' + "".join(bands)
               + streaks(30, 15, (-10, 266, 200, 310), ["#B8583A", "#F8D6B4"], w=(0.8, 2), length=(4, 14), opacity=(0.2, 0.45), slant=0.3) + "</g>")
    out.append(f'<polyline points="{P(rl[:12])}" fill="none" stroke="#FFE2BE" stroke-width="1.4" opacity="0.7"/>')
    out.append(mist(260, 308, 360, 10, "#F4C292", f"{U}-mh2", 0.3))
    return "\n".join(out)


# ---------------------------------------------------------------- the Strip on the horizon
def tower_face(x0, x1, top, base, lit, shade, side_w, side_right, bands=None, band_col="#FFFFFF", band_op=0.25, round_top=False):
    """A distant tower: front face + a narrow side face; horizontal floor bands for scale."""
    out = []
    if side_right:
        out.append(poly([(x1, top + 2), (x1 + side_w, top + 4), (x1 + side_w, base), (x1, base)], shade))
    else:
        out.append(poly([(x0 - side_w, top + 4), (x0, top + 2), (x0, base), (x0 - side_w, base)], shade))
    if round_top:
        w = x1 - x0
        out.append(f'<path d="M {x0:.1f} {base} L {x0:.1f} {top + w * 0.35:.1f} Q {x0 + w * 0.5:.1f} {top - w * 0.2:.1f} {x1:.1f} {top + w * 0.35:.1f} L {x1:.1f} {base} Z" fill="{lit}"/>')
    else:
        out.append(f'<rect x="{x0:.1f}" y="{top:.1f}" width="{x1 - x0:.1f}" height="{base - top:.1f}" fill="{lit}"/>')
    if bands:
        y = top + bands
        lines = []
        while y < base - 2:
            lines.append(f'<line x1="{x0 + 0.6:.1f}" y1="{y:.1f}" x2="{x1 - 0.6:.1f}" y2="{y:.1f}"/>')
            y += bands
        out.append(f'<g stroke="{band_col}" stroke-width="0.9" opacity="{band_op}">' + "".join(lines) + "</g>")
    return "".join(out)


def skyline():
    base = 312
    out = [defs(lg(f"{U}-skyhz", [(0, "#F4C292", 0), (0.6, "#F4C292", 0.08), (1, "#F2BE8C", 0.28)], 0, 160, 0, 312, units="userSpaceOnUse"))]
    # far blocks near the vanishing point
    for x0, x1, top, col in ((150, 160, 286, "#E8CDB8"), (160, 168, 292, "#EAD3BE"), (172, 180, 290, "#E6CBB8"), (186, 196, 282, "#ECD4BC")):
        out.append(f'<rect x="{x0}" y="{top}" width="{x1 - x0}" height="{base - top}" fill="{col}"/>')
    # the observation tower at the far north end: needle shaft, saucer pod, mast
    tx = 182
    out.append(poly([(tx - 3.4, base), (tx - 1.6, 196), (tx + 1.6, 196), (tx + 3.4, base)], "#E4D2C2"))
    out.append(poly([(tx - 3.4, base), (tx - 1.6, 196), (tx - 0.2, 196), (tx - 1.0, base)], "#F8E8D4"))
    out.append(f'<path d="M {tx - 9} 194 Q {tx} 186 {tx + 9} 194 L {tx + 6} 199 L {tx - 6} 199 Z" fill="#E9D8C6"/>'
               f'<rect x="{tx - 9}" y="193" width="18" height="1.6" fill="#8FC3CC"/>'
               f'<rect x="{tx - 5.5}" y="199" width="11" height="2.4" fill="#D9C6B4"/>'
               f'<line x1="{tx}" y1="188" x2="{tx}" y2="168" stroke="#D8C6B6" stroke-width="1.6"/>')
    # left of the road: the golden three-winged tower and the glass pyramid beside it
    out.append(tower_face(84, 98, 244, base, "#EDC27A", "#D2A266", 4, False, bands=3.2, band_col="#FFF0C8", band_op=0.35))
    out.append(tower_face(116, 130, 240, base, "#E2B26A", "#C99A5E", 4, True, bands=3.2, band_col="#FFF0C8", band_op=0.3))
    out.append(tower_face(97, 117, 226, base, "#F2CC84", "#D8AA6C", 0, True, bands=3.2, band_col="#FFF4D6", band_op=0.4))
    out.append(f'<rect x="99" y="222" width="16" height="4" fill="#E2B670"/><rect x="104" y="217" width="6" height="5" fill="#D9AC6A"/>')
    out.append(poly([(128, base), (155, 266), (182, base)], "#BFB8B2"))
    out.append(poly([(128, base), (155, 266), (152, base)], "#DCCDBE"))
    out.append('<g stroke="#F6E6D4" stroke-width="0.8" opacity="0.5">' + "".join(
        f'<line x1="{155 - (y - 266) * 27 / 46:.1f}" y1="{y}" x2="{155 + (y - 266) * 27 / 46:.1f}" y2="{y}"/>' for y in range(272, 311, 5)) + "</g>")
    # right of the road: a stepped run of resort towers growing toward us
    for x0, x1, top, lit, shade, bands, rt in (
            (198, 212, 270, "#F1DCC6", "#DCC2AE", 3.0, False),
            (212, 230, 256, "#A9D3D6", "#8EBCC2", 3.0, False),
            (230, 252, 240, "#F6E8D8", "#E0CDBC", 3.4, True),
            (252, 268, 256, "#F2C9A6", "#DDB090", 3.2, False)):
        out.append(tower_face(x0, x1, top, base, lit, shade, 3, False, bands=bands, band_col="#FFFFFF" if lit != "#A9D3D6" else "#E8F6F6", band_op=0.35))
    out.append('<path d="M 212 256 L 230 256 L 230 260 L 212 262 Z" fill="#C9E6E6" opacity="0.8"/>')
    out.append(f'<rect x="0" y="160" width="300" height="152" fill="url(#{U}-skyhz)"/>')
    return '<g transform="translate(170 312) scale(1.22) translate(-170 -312)">' + "\n".join(out) + "</g>"


# ---------------------------------------------------------------- ground, road and long shadows
def ground():
    out = [defs(
        lg(f"{U}-floor", [(0, "#F4D3AA"), (0.25, "#EDC092"), (0.7, "#E2A878"), (1, "#D99A68")], 0, 310, 0, 444, units="userSpaceOnUse"),
        lg(f"{U}-road", [(0, "#C8B2A2"), (0.35, "#A8968C"), (1, "#8C7E78")], 0, 310, 0, 444, units="userSpaceOnUse"),
        lg(f"{U}-glare", [(0, "#FFE6BE", 0.75), (1, "#FFE6BE", 0)], 0, 310, 0, 380, units="userSpaceOnUse"),
    )]
    out.append(f'<rect x="-10" y="310" width="620" height="140" fill="url(#{U}-floor)"/>')
    # sand ripples and wash lines across the flats
    rnd = random.Random(21)
    rip = []
    for _ in range(70):
        y = 314 + (rnd.random() ** 1.6) * 130
        s = (y - 308) / 20
        x = rnd.uniform(-10, 610)
        rip.append(f'<path d="M {x:.1f} {y:.1f} q {6 * s:.1f} {-1.2 * s:.1f} {12 * s:.1f} 0" stroke="{rnd.choice(["#F8DCB6", "#D99A6A", "#FBE4C4"])}" stroke-width="{max(0.8, 0.5 * s):.1f}"/>')
    out.append('<g fill="none" opacity="0.6" stroke-linecap="round">' + "".join(rip) + "</g>")
    # creosote and bursage dotting the flats, smaller with distance
    bush = []
    for _ in range(110):
        Z = math.exp(rnd.uniform(math.log(16), math.log(400)))
        X = rnd.uniform(-60, 80)
        if -4.5 < X < 5.5:
            continue
        x, y = C(X, 0, Z)
        if not (-10 < x < 610) or y > 444:
            continue
        r = max(0.9, 420 * 0.6 / Z)
        bush.append((y, x, r, Z))
    for y, x, r, Z in sorted(bush):
        near = max(0.0, min(1.0, (60 - Z) / 44))      # far shrubs melt into the haze
        op = 0.35 + 0.55 * near
        out.append(f'<g opacity="{op:.2f}"><ellipse cx="{x + (r * 0.9 if x > SUN[0] else -r * 0.9):.1f}" cy="{y + 0.6:.1f}" rx="{r * 1.4:.1f}" ry="{r * 0.28:.1f}" fill="#B86E48" opacity="0.4"/>'
                   f'<ellipse cx="{x:.1f}" cy="{y - r * 0.4:.1f}" rx="{r:.1f}" ry="{r * 0.6:.1f}" fill="{rnd.choice(["#8FA67A", "#9AAE84", "#7C9B74"])}"/>'
                   f'<ellipse cx="{x + r * 0.3:.1f}" cy="{y - r * 0.6:.1f}" rx="{r * 0.5:.1f}" ry="{r * 0.3:.1f}" fill="#D2D8A6" opacity="0.7"/></g>')
    # the boulevard running north to the Strip
    def gq(X0, X1, Z0, Z1, Y=0.0):
        return [C(X0, Y, Z0), C(X1, Y, Z0), C(X1, Y, Z1), C(X0, Y, Z1)]
    out.append(poly(gq(-3.4, 4.4, 6, 4000), "#E8C9A6"))           # pale concrete shoulders / curbs
    out.append(poly(gq(-2.8, 3.8, 6, 4000), f"url(#{U}-road)"))
    out.append(poly([C(-2.8, 0, 60), C(3.8, 0, 60), (C(3.8, 0, 4000)[0], 311), (C(-2.8, 0, 4000)[0], 311)], f"url(#{U}-glare)"))
    for X in (-2.55, 3.55):
        out.append(poly(gq(X - 0.08, X + 0.08, 6, 4000), "#FBF0E0", ' opacity="0.9"'))
    z = 6.5
    while z < 600:
        out.append(poly(gq(0.42, 0.58, z, z * 1.18), "#FBF0E0", ' opacity="0.9"'))
        z *= 1.42
    # tyre-polished sheen down each lane
    for X in (-1.2, 2.2):
        out.append(poly(gq(X - 0.5, X + 0.5, 6, 4000), "#C2AE9E", ' opacity="0.25"'))
    return "\n".join(out)


# ---------------------------------------------------------------- Joshua tree
def joshua_tree(x, base, h, seed, light=1):
    """Yucca brevifolia: shaggy trunk forking into elbowed arms, each ending in a spiky rosette of daggers.
    light = side the sun is on (1 = right)."""
    rnd = random.Random(seed)
    bark, bark_d, bark_l = "#8E7A64", "#6E5C4C", "#E8C9A0"
    skirt_c = ["#A88E6C", "#94785A", "#B89C76"]
    leaf_d, leaf_m, leaf_l, rim = "#5A7444", "#7E9A5A", "#B2C27E", "#F6E4A0"
    limbs, tips = [], []

    def grow(p, ang, L, w, depth):
        ex = p[0] + math.cos(ang) * L
        ey = p[1] + math.sin(ang) * L
        # elbow: arms bend upward toward their ends
        up = -math.pi / 2
        mid_ang = ang + (up - ang) * 0.15
        c = (p[0] + math.cos(mid_ang) * L * 0.55, p[1] + math.sin(mid_ang) * L * 0.55)
        end_ang = ang + (up - ang) * 0.55
        ex = c[0] + math.cos(end_ang) * L * 0.5
        ey = c[1] + math.sin(end_ang) * L * 0.5
        limbs.append((p, c, (ex, ey), w, w * 0.72))
        if depth == 0:
            tips.append((ex, ey, end_ang, w))
            return
        n = 2 if rnd.random() < 0.7 else 3
        spread = rnd.uniform(0.45, 0.7)
        for i in range(n):
            a = end_ang + (i - (n - 1) / 2) * spread * 2 / max(1, n - 1) * rnd.uniform(0.8, 1.2)
            grow((ex, ey), a, L * rnd.uniform(0.55, 0.75), w * 0.72, depth - 1)

    trunk_top = (x + rnd.uniform(-4, 4), base - h * 0.42)
    limbs.append(((x, base), (x - h * 0.02, base - h * 0.2), trunk_top, h * 0.085, h * 0.065))
    for i, a in enumerate((-2.2, -1.25, -0.6)):
        grow(trunk_top, a + rnd.uniform(-0.12, 0.12), h * rnd.uniform(0.24, 0.3), h * 0.06, 1 if i != 1 else 2)
    out = []
    for p0, p1, p2, w0, w1 in limbs:
        out.append(poly(tube(p0, p1, p2, w0, w1), bark))
        out.append(poly(tube(p0, p1, p2, w0 * 0.45, w1 * 0.45, off=-0.55 * light), bark_d, ' opacity="0.55"'))
        out.append(poly(tube(p0, p1, p2, w0 * 0.22, w1 * 0.22, off=0.75 * light), bark_l, ' opacity="0.55"'))
        # shaggy dead-leaf texture: short downward hooks along the limb
        marks = []
        for k in range(int(math.hypot(p2[0] - p0[0], p2[1] - p0[1]) / 3.2)):
            t = rnd.random()
            px, py = qpt(p0, p1, p2, t)
            ww = (w0 + (w1 - w0) * t) / 2
            ox = rnd.uniform(-ww, ww)
            marks.append(f'<path d="M {px + ox:.1f} {py:.1f} l {rnd.uniform(-1.5, 1.5):.1f} {rnd.uniform(2.5, 5):.1f}" stroke="{rnd.choice([bark_d, "#A08A70", "#5E4E40"])}"/>')
        out.append('<g fill="none" stroke-width="1.1" stroke-linecap="round" opacity="0.7">' + "".join(marks) + "</g>")
    for ex, ey, a, w in tips:
        R = h * rnd.uniform(0.062, 0.075)
        # a short skirt of dry leaves folded down under the rosette
        sk = []
        for k in range(12):
            sx = ex + rnd.uniform(-w * 0.8, w * 0.8)
            sk.append(f'<path d="M {sx:.1f} {ey + R * 0.15:.1f} l {rnd.uniform(-1.5, 1.5):.1f} {R * rnd.uniform(0.3, 0.55):.1f}" stroke="{rnd.choice(skirt_c)}"/>')
        out.append(f'<g fill="none" stroke-width="{max(1.2, w * 0.2):.1f}" stroke-linecap="round">' + "".join(sk) + "</g>")
        leaves = []
        cx, cy = ex, ey - R * 0.25
        leaves.append((-9, f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{R * 0.42:.1f}" ry="{R * 0.36:.1f}" fill="{leaf_d}"/>'))
        for k in range(70):
            # a dense pompom of stiff daggers bristling outward, more of them upward
            la = rnd.uniform(-math.pi, math.pi)
            if math.sin(la) > 0.2 and rnd.random() < 0.55:
                la = -la
            r0 = R * 0.28 * rnd.random()
            sx_, sy_ = cx + math.cos(la) * r0, cy + math.sin(la) * r0 * 0.85
            L = R * rnd.uniform(0.5, 0.95) * (0.75 if math.sin(la) > 0.3 else 1.0)
            bw = max(0.75, R * 0.05)
            tx, ty = sx_ + math.cos(la) * L, sy_ + math.sin(la) * L
            nx, ny = -math.sin(la) * bw, math.cos(la) * bw
            lit_side = (math.cos(la) * light > 0.1) or math.sin(la) < -0.6
            z = rnd.random()
            col = (leaf_l if z < 0.55 else leaf_m) if lit_side else (leaf_m if z < 0.5 else leaf_d)
            leaves.append((z + (1 if lit_side else 0), f'<polygon points="{P([(sx_ + nx, sy_ + ny), (tx, ty), (sx_ - nx, sy_ - ny)])}" fill="{col}"/>'))
            if lit_side and rnd.random() < 0.35:
                leaves.append((2.5, f'<line x1="{sx_ + (tx - sx_) * 0.45:.1f}" y1="{sy_ + (ty - sy_) * 0.45:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{rim}" stroke-width="0.8" opacity="0.75"/>'))
        out.append("".join(s for _, s in sorted(leaves, key=lambda t: t[0])))
    return "".join(out)


# ---------------------------------------------------------------- the welcome sign
def face_outline(cx, top, W, H, n=14):
    """Horizontally stretched diamond: shallow pointed top and bottom, rounded ends."""
    hw, mid = W / 2, top + H / 2
    ex, ry = hw * 0.80, H * 0.33
    pts = [(cx, top)]
    for i in range(n + 1):
        a = -math.pi / 2 + math.pi * i / n
        pts.append((cx + ex + hw * 0.2 * math.cos(a), mid + ry * math.sin(a)))
    pts.append((cx, top + H))
    for i in range(n + 1):
        a = math.pi / 2 + math.pi * i / n
        pts.append((cx - ex + hw * 0.2 * math.cos(a), mid + ry * math.sin(a)))
    return pts


def resample(pts, step):
    closed = pts + [pts[0]]
    out = []
    carry = 0.0
    for (x1, y1), (x2, y2) in zip(closed, closed[1:]):
        L = math.hypot(x2 - x1, y2 - y1)
        t = carry
        while t < L:
            out.append((x1 + (x2 - x1) * t / L, y1 + (y2 - y1) * t / L))
            t += step
        carry = t - L
    return out


def star8(cx, cy, R, r, rot=0.0):
    pts = []
    for i in range(16):
        a = rot + math.pi * i / 8 - math.pi / 2
        rr = R if i % 2 == 0 else r
        if i % 4 == 2:
            rr = R * 0.78
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def welcome_sign(cx, ground_y):
    W, H = 268, 152
    top = 150
    out = [defs(
        lg(f"{U}-face", [(0, "#FFFDF6"), (0.55, "#FFF8EC"), (1, "#F1EBE4")], 0, 0, 1, 0.3),
        lg(f"{U}-pole", [(0, "#FBF6EE"), (0.55, "#E6DED4"), (1, "#BDB2A8")], 0, 0, 1, 0),
        lg(f"{U}-edge", [(0, "#E9DED2"), (1, "#C8B9AA")], 0, 0, 0, 1),
    )]
    # cast shadows: the low sun is behind and to the left, so shadows run toward us and to the right
    for px in (cx - 24, cx + 20):
        out.append(poly([(px - 5, ground_y), (px + 5, ground_y), (px + 70, ground_y + 52), (px + 56, ground_y + 52)], "#B0603E", ' opacity="0.28"'))
    out.append(f'<path d="M {cx + 40} {ground_y + 52} Q {cx + 150} {ground_y + 40} {cx + 240} {ground_y + 56} L {cx + 250} {ground_y + 70} L {cx + 20} {ground_y + 70} Z" fill="#B0603E" opacity="0.22"/>')
    # two flat poles (offset front/back), joined by a crosspiece above the face
    for px, w in ((cx - 24, 10), (cx + 20, 10)):
        out.append(f'<rect x="{px - w / 2:.1f}" y="100" width="{w}" height="{ground_y - 100:.1f}" fill="url(#{U}-pole)"/>')
        out.append(f'<rect x="{px - w / 2:.1f}" y="100" width="2.2" height="{ground_y - 100:.1f}" fill="#FFE8C0" opacity="0.8"/>')
    out.append(f'<rect x="{cx - 30}" y="98" width="56" height="7" fill="url(#{U}-pole)"/><rect x="{cx - 30}" y="98" width="56" height="2" fill="#FFF2D8"/>')
    # footings
    for px in (cx - 24, cx + 20):
        out.append(f'<rect x="{px - 9}" y="{ground_y - 8}" width="18" height="9" rx="1.5" fill="#E2D2C2"/><rect x="{px - 9}" y="{ground_y - 8}" width="18" height="2.4" fill="#FFF0DC"/>')
    # the eight-pointed star between the poles, its rays wrapping over the frame
    sc = (cx - 2, 124)
    out.append(glow(sc[0], sc[1], 34, "#FFE9A8", f"{U}-stg", 0.55))
    out.append(poly(star8(sc[0] + 1.5, sc[1] + 1.5, 25, 9), "#7E3B2C", ' opacity="0.35"'))
    out.append(poly(star8(sc[0], sc[1], 25, 9), "#D9402E", ' stroke="#FFD25E" stroke-width="2.6" stroke-linejoin="round"'))
    out.append(poly(star8(sc[0], sc[1], 25, 9)[12:16] + [sc] + star8(sc[0], sc[1], 25, 9)[0:1], "#F06A4A", ' opacity="0.65"'))
    out.append(f'<circle cx="{sc[0]}" cy="{sc[1]}" r="3" fill="#FFD25E"/>')
    # the face: cabinet edge (lit on the sun side), white panel, bulb border, red pinstripe
    fo = face_outline(cx, top, W, H)
    out.append(poly([(x - 3.2, y + 3) for x, y in fo], f"url(#{U}-edge)"))
    out.append(poly(fo, "#C9443A"))
    fi = [(cx + (x - cx) * (W - 10) / W, top + H / 2 + (y - top - H / 2) * (H - 10) / H) for x, y in fo]
    out.append(poly(fi, f"url(#{U}-face)"))
    fb = [(cx + (x - cx) * (W - 22) / W, top + H / 2 + (y - top - H / 2) * (H - 22) / H) for x, y in fo]
    out.append(poly(fb, "none", ' stroke="#D9402E" stroke-width="1.8"'))
    # bulbs along the border band
    fbulb = [(cx + (x - cx) * (W - 16) / W, top + H / 2 + (y - top - H / 2) * (H - 16) / H) for x, y in fo]
    bulbs = resample(fbulb, 7.4)
    out.append('<g>' + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.4" fill="#F6C453"/><circle cx="{x - 0.6:.1f}" cy="{y - 0.7:.1f}" r="1.1" fill="#FFF6D6"/>' for x, y in bulbs) + "</g>")
    # WELCOME on seven silver dollars along a gentle arch
    dol = []
    for i, ch in enumerate("WELCOME"):
        dx = (i - 3) * 27.5
        y = top + 39 + abs(dx) * 0.07
        dol.append(f'<circle cx="{cx + dx + 1:.1f}" cy="{y + 1.2:.1f}" r="12" fill="#B9AFA6" opacity="0.6"/>'
                   f'<circle cx="{cx + dx:.1f}" cy="{y:.1f}" r="12" fill="#FFFFFF" stroke="#D2CCC6" stroke-width="1.6"/>'
                   f'<circle cx="{cx + dx:.1f}" cy="{y:.1f}" r="9.8" fill="none" stroke="#E7E2DC" stroke-width="0.9"/>'
                   f'<text x="{cx + dx:.1f}" y="{y + 6.0:.1f}" text-anchor="middle" {ANTON} font-size="16.5" fill="#D9402E">{ch}</text>')
    out.append("".join(dol))
    # "to Fabulous" in blue script, LAS VEGAS in big red capitals, NEVADA small in blue
    out.append(f'<text x="{cx - 2}" y="{top + 75}" text-anchor="middle" {SERIF_IT} font-size="17" fill="#2E62B0">to Fabulous</text>')
    sz = fit_size("LAS VEGAS", ANTON, 46, 206, 1.0)
    out.append(f'<text x="{cx + 1.4}" y="{top + 118.4}" text-anchor="middle" {ANTON} font-size="{sz}" letter-spacing="1" fill="#7E3B2C" opacity="0.35">LAS VEGAS</text>')
    out.append(f'<text x="{cx}" y="{top + 117}" text-anchor="middle" {ANTON} font-size="{sz}" letter-spacing="1" fill="#D9402E">LAS VEGAS</text>')
    out.append(f'<text x="{cx + 2}" y="{top + 133}" text-anchor="middle" {MONO} font-size="10" letter-spacing="3" fill="#2E62B0">NEVADA</text>')
    # warm light skimming the sun-side of the panel; a cooler sky reflection on the far end
    right = [p for p in fi if p[0] > cx + W * 0.22]
    out.append(poly(right, "#C3E5E6", ' opacity="0.18"'))
    return "\n".join(out)


# ---------------------------------------------------------------- Mojave garden plants
def yucca(x, base, h, seed, bloom=True, light=-1):
    """Mojave yucca: short shaggy trunk, a burst of stiff blue-green blades, a creamy flower spike."""
    rnd = random.Random(seed)
    out = []
    th = h * 0.32
    out.append(poly([(x - h * 0.05, base), (x - h * 0.035, base - th), (x + h * 0.035, base - th), (x + h * 0.05, base)], "#8C7458"))
    out.append(f'<g fill="none" stroke="#A88E6C" stroke-width="1.3" stroke-linecap="round" opacity="0.8">' + "".join(
        f'<path d="M {x + rnd.uniform(-h * 0.04, h * 0.04):.1f} {base - rnd.uniform(0, th):.1f} l {rnd.uniform(-1, 1):.1f} 5"/>' for _ in range(22)) + "</g>")
    cy = base - th
    blades = []
    for k in range(40):
        a = rnd.uniform(-math.pi * 0.98, -math.pi * 0.02)
        L = h * rnd.uniform(0.38, 0.62) * (0.75 + 0.25 * abs(math.sin(a)))
        bw = h * 0.022
        tx, ty = x + math.cos(a) * L, cy + math.sin(a) * L
        nx, ny = -math.sin(a) * bw, math.cos(a) * bw
        lit = math.cos(a) * light > 0.15
        col = rnd.choice(["#9FB89A", "#B7C9A8"]) if lit else rnd.choice(["#6F8E6C", "#5E7E62", "#7C9B74"])
        blades.append((math.sin(a), f'<polygon points="{P([(x + nx, cy + ny), (x + (tx - x) * 0.6 + nx * 0.6, cy + (ty - cy) * 0.6 + ny * 0.6), (tx, ty), (x - nx, cy - ny)])}" fill="{col}"/>'))
    out.append("".join(s for _, s in sorted(blades, key=lambda t: -t[0])))
    if bloom:
        sx, top = x + h * 0.04, cy - h * 0.95
        out.append(f'<path d="M {x:.1f} {cy:.1f} Q {sx - 3:.1f} {(cy + top) / 2:.1f} {sx:.1f} {top:.1f}" stroke="#8A7A4E" stroke-width="2.2" fill="none"/>')
        fl = []
        for k in range(26):
            t = rnd.uniform(0.02, 0.55)
            yy = top + (cy - top) * t
            xx = sx + rnd.uniform(-1, 1) * (3 + 22 * t) * 0.45
            r = rnd.uniform(2.6, 3.6)
            fl.append((yy, f'<ellipse cx="{xx:.1f}" cy="{yy:.1f}" rx="{r:.1f}" ry="{r * 1.2:.1f}" fill="{rnd.choice(["#FFF4DE", "#F7E1B5", "#FBEBCB"])}"/>'
                           f'<ellipse cx="{xx + r * 0.3:.1f}" cy="{yy + r * 0.4:.1f}" rx="{r * 0.6:.1f}" ry="{r * 0.6:.1f}" fill="#E2C08E" opacity="0.6"/>'))
        out.append("".join(s for _, s in sorted(fl)))
    return "".join(out)


def barrel(x, base, r, seed, light=-1):
    """Barrel cactus: ribbed sage dome with red-gold spines and a crown of yellow flowers."""
    rnd = random.Random(seed)
    h = r * 1.25
    cid = f"{U}-bc{seed}"
    body = f'M {x - r:.1f} {base:.1f} C {x - r * 1.05:.1f} {base - h * 0.75:.1f} {x - r * 0.6:.1f} {base - h:.1f} {x:.1f} {base - h:.1f} C {x + r * 0.6:.1f} {base - h:.1f} {x + r * 1.05:.1f} {base - h * 0.75:.1f} {x + r:.1f} {base:.1f} Z'
    out = [f'<clipPath id="{cid}"><path d="{body}"/></clipPath>',
           f'<path d="{body}" fill="#7C9B74"/>',
           f'<g clip-path="url(#{cid})">',
           f'<ellipse cx="{x + light * r * 0.55:.1f}" cy="{base - h * 0.55:.1f}" rx="{r * 0.6:.1f}" ry="{h * 0.7:.1f}" fill="#B7CBA2" opacity="0.6"/>',
           f'<ellipse cx="{x - light * r * 0.7:.1f}" cy="{base - h * 0.4:.1f}" rx="{r * 0.55:.1f}" ry="{h * 0.8:.1f}" fill="#4E6E4A" opacity="0.45"/>']
    ribs = []
    for i in range(-4, 5):
        t = i / 4.6
        ribs.append(f'<path d="M {x + t * r * 0.35:.1f} {base - h:.1f} Q {x + t * r * 1.15:.1f} {base - h * 0.5:.1f} {x + t * r * 0.98:.1f} {base:.1f}" stroke="#4E6E4A" stroke-width="1.2" fill="none" opacity="0.6"/>')
        for k in range(5):
            tt = 0.15 + k * 0.18
            px = x + t * r * (0.35 + 0.8 * math.sin(math.pi * tt * 0.9))
            py = base - h + h * tt
            ribs.append(f'<path d="M {px:.1f} {py:.1f} l {rnd.uniform(-3, 3):.1f} {rnd.uniform(-3, -1):.1f} M {px:.1f} {py:.1f} l {rnd.uniform(-3, 3):.1f} {rnd.uniform(1, 3):.1f}" stroke="{rnd.choice(["#C65F37", "#E6995F", "#F6C453"])}" stroke-width="0.9" fill="none"/>')
    out.append("".join(ribs) + "</g>")
    for k in range(5):
        fx = x + (k - 2) * r * 0.22 + rnd.uniform(-1, 1)
        fy = base - h - 1 + abs(k - 2) * 1.2
        out.append(f'<ellipse cx="{fx:.1f}" cy="{fy:.1f}" rx="3.2" ry="2.4" fill="#F6C453"/><ellipse cx="{fx - 0.5:.1f}" cy="{fy - 0.6:.1f}" rx="1.6" ry="1.1" fill="#FFE9A0"/>')
    return "".join(out)


def brittlebush(x, base, r, seed, light=-1):
    """Silver-sage mound with a cloud of small yellow daisies on wiry stems above it."""
    rnd = random.Random(seed)
    out = [f'<ellipse cx="{x:.1f}" cy="{base - r * 0.45:.1f}" rx="{r:.1f}" ry="{r * 0.55:.1f}" fill="#8EA683"/>']
    for k in range(int(r * 2.2)):
        a = rnd.uniform(0, math.tau)
        rr = r * rnd.random() ** 0.6
        lx, ly = x + math.cos(a) * rr * 0.95, base - r * 0.45 + math.sin(a) * rr * 0.5
        lit = (lx - x) * light > 0 and ly < base - r * 0.4
        out.append(f'<ellipse cx="{lx:.1f}" cy="{ly:.1f}" rx="{r * 0.16:.1f}" ry="{r * 0.09:.1f}" fill="{"#C9D6B4" if lit else rnd.choice(["#A7BC9F", "#7C9B74", "#93AB88"])}" transform="rotate({rnd.uniform(-40, 40):.0f} {lx:.1f} {ly:.1f})"/>')
    stems, heads = [], []
    for k in range(int(r * 0.9)):
        sx = x + rnd.uniform(-r * 0.8, r * 0.8)
        sy = base - r * 0.6 - abs(rnd.gauss(0, 0.12)) * r
        tx, ty = sx + rnd.uniform(-4, 4), sy - r * rnd.uniform(0.35, 0.7)
        stems.append(f'<path d="M {sx:.1f} {sy:.1f} Q {sx:.1f} {(sy + ty) / 2:.1f} {tx:.1f} {ty:.1f}"/>')
        fr = max(2.0, r * 0.11)
        heads.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="{fr:.1f}" fill="{rnd.choice(["#F6C453", "#FFD25E", "#F4B43A"])}"/><circle cx="{tx + 0.3:.1f}" cy="{ty + 0.2:.1f}" r="{fr * 0.4:.1f}" fill="#C27A2A"/>')
    out.append(f'<g fill="none" stroke="#8A9A6A" stroke-width="0.9">' + "".join(stems) + "</g>" + "".join(heads))
    return "".join(out)


def creosote(x, base, r, seed, light=-1):
    rnd = random.Random(seed)
    out = [f'<ellipse cx="{x:.1f}" cy="{base - r * 0.5:.1f}" rx="{r:.1f}" ry="{r * 0.62:.1f}" fill="#5E7A4E"/>']
    tw = []
    for k in range(int(r * 1.6)):
        bx = x + rnd.uniform(-r * 0.4, r * 0.4)
        a = rnd.uniform(-1.2, 1.2)
        L = r * rnd.uniform(0.6, 1.1)
        tw.append(f'<path d="M {bx:.1f} {base:.1f} L {bx + math.sin(a) * L:.1f} {base - math.cos(a) * L * 0.9:.1f}"/>')
    out.append('<g stroke="#5A4A3A" stroke-width="1" opacity="0.6">' + "".join(tw) + "</g>")
    for k in range(int(r * 3)):
        a = rnd.uniform(0, math.tau)
        rr = r * rnd.random() ** 0.5
        lx, ly = x + math.cos(a) * rr, base - r * 0.55 + math.sin(a) * rr * 0.6
        lit = (lx - x) * light > 0 and ly < base - r * 0.5
        out.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="{r * rnd.uniform(0.07, 0.13):.1f}" fill="{"#B9C98E" if lit else rnd.choice(["#6F8A55", "#7C9B66", "#5E7A4E"])}"/>')
    out.append(dots(int(r * 0.5), seed, (x - r * 0.6, base - r * 1.0, x + r * 0.6, base - r * 0.3), "#F6D25E", r=(0.7, 1.3), opacity=(0.7, 1)))
    return "".join(out)


def rock(x, base, w, h, seed, light=-1):
    rnd = random.Random(seed)
    pts = [(x - w / 2, base), (x - w * 0.45, base - h * 0.6), (x - w * 0.2, base - h), (x + w * 0.2, base - h * 0.95), (x + w * 0.45, base - h * 0.5), (x + w / 2, base)]
    pts = [(px + rnd.uniform(-1, 1), py + rnd.uniform(-1, 1)) for px, py in pts]
    out = [f'<path d="{smooth(pts)}Z" fill="#D49270"/>']
    lit = pts[:4] if light < 0 else pts[2:]
    out.append(f'<path d="M {pts[1][0]:.1f} {pts[1][1]:.1f} Q {pts[2][0]:.1f} {pts[2][1] - 1:.1f} {pts[3][0]:.1f} {pts[3][1]:.1f} Q {x:.1f} {base - h * 0.55:.1f} {pts[1][0]:.1f} {pts[1][1]:.1f} Z" fill="#F4C8A4"/>')
    out.append(f'<path d="M {pts[3][0]:.1f} {pts[3][1]:.1f} Q {pts[4][0] + 1:.1f} {pts[4][1]:.1f} {pts[5][0]:.1f} {pts[5][1]:.1f} L {x + w * 0.1:.1f} {base:.1f} Z" fill="#A85E40" opacity="0.55"/>')
    return "".join(out)


def garden(cx, ground_y):
    """The raised planter island around the sign: a cream stone curb around warm decomposed-granite gravel."""
    out = [defs(lg(f"{U}-isle", [(0, "#EDBE92"), (1, "#E0A678")], 0, 0, 0, 1),
                lg(f"{U}-curb", [(0, "#FBE8D2"), (1, "#E2C4A6")], 0, 0, 0, 1))]
    top = [(cx - 168, ground_y + 14), (cx - 130, ground_y - 4), (cx - 40, ground_y - 13), (cx + 80, ground_y - 13), (cx + 175, ground_y - 4), (cx + 230, ground_y + 12)]
    d = smooth(top)
    out.append(f'<path d="{d} L {cx + 236} {ground_y + 20} L {cx - 174} {ground_y + 22} Z" fill="url(#{U}-curb)"/>')
    front = [(px, py + 7) for px, py in top]
    out.append(f'<path d="{d} L {cx + 230} 450 L {cx - 168} 450 Z" fill="url(#{U}-isle)"/>')
    out.append(f'<path d="{smooth(front)} L {cx + 230} {ground_y + 12} L {cx + 236} 450 L {cx - 174} 450 L {cx - 168} {ground_y + 14} Z" fill="url(#{U}-isle)"/>')
    # stone curb: a lit top edge, block joints
    out.append(f'<path d="{d}" fill="none" stroke="#FFF2E2" stroke-width="2.4"/>')
    out.append(f'<path d="{smooth(front)}" fill="none" stroke="#C88A64" stroke-width="1.2" opacity="0.6"/>')
    rnd = random.Random(43)
    out.append('<g stroke="#C9A486" stroke-width="1" opacity="0.6">' + "".join(
        f'<line x1="{x:.1f}" y1="{y_on(top, x) + 1:.1f}" x2="{x:.1f}" y2="{y_on(top, x) + 6.5:.1f}"/>' for x in range(int(cx - 160), int(cx + 228), 17) if y_on(top, x)) + "</g>")
    # gravel texture
    out.append(dots(150, 41, (cx - 160, ground_y, cx + 230, 444), "#B87050", r=(0.6, 1.6), opacity=(0.3, 0.7)))
    out.append(dots(90, 42, (cx - 160, ground_y, cx + 230, 444), "#FFEBD2", r=(0.6, 1.4), opacity=(0.4, 0.8)))
    return "\n".join(out)


def vintage_car(x, base, w):
    """A turquoise late-fifties convertible seen from behind, heading up the boulevard toward the Strip."""
    k = w / 40
    g = [f'<g transform="translate({x:.1f} {base:.1f}) scale({k:.3f})">',
         '<ellipse cx="6" cy="0.5" rx="26" ry="2.6" fill="#8A5A40" opacity="0.35"/>',
         # body, tail fins and trunk lid
         '<path d="M -20 -3 L -20 -12 Q -20 -15 -17 -16 L -15 -21 L -12 -16 L 12 -16 L 15 -21 L 17 -16 Q 20 -15 20 -12 L 20 -3 Z" fill="#5FA8B4"/>',
         '<path d="M -20 -12 L 20 -12 L 20 -9 L -20 -9 Z" fill="#8CC8CE" opacity="0.8"/>',
         '<path d="M -12 -16 L 12 -16 L 11 -13 L -11 -13 Z" fill="#7EBEC6"/>',
         '<path d="M 4 -16 L 20 -15 L 20 -3 L 8 -3 Z" fill="#3E7E8C" opacity="0.35"/>',
         # chrome bumper, plate, red tail lamps in the fins
         '<rect x="-21" y="-5" width="42" height="2.6" rx="1.2" fill="#F4ECE2"/><rect x="-21" y="-5" width="42" height="0.9" fill="#FFFFFF"/>',
         '<rect x="-4" y="-9" width="8" height="3.4" fill="#F7E1B5"/>',
         '<path d="M -19 -14 L -16 -19.5 L -15 -14 Z" fill="#E8463A"/><path d="M 19 -14 L 16 -19.5 L 15 -14 Z" fill="#E8463A"/>',
         # tyres
         '<rect x="-18" y="-3" width="6" height="3.4" rx="1" fill="#4A3A36"/><rect x="12" y="-3" width="6" height="3.4" rx="1" fill="#4A3A36"/>',
         # top down: windscreen frame and two travellers, one in a sun scarf
         '<path d="M -13 -16 L -11 -22 L 11 -22 L 13 -16" fill="none" stroke="#E8E2DA" stroke-width="1.2"/>',
         '<path d="M -11 -22 L 11 -22 L 13 -16 L -13 -16 Z" fill="#C3E5E6" opacity="0.35"/>',
         '<ellipse cx="-6" cy="-21" rx="3.2" ry="3.8" fill="#5A3A2C"/><path d="M -9 -17 Q -6 -20 -3 -17 Z" fill="#F4A15A"/>',
         '<ellipse cx="6" cy="-21.5" rx="3.3" ry="3.9" fill="#3A2A22"/><path d="M 3 -23 Q 6 -27 9 -23 L 10 -22 Q 6 -24 2 -22 Z" fill="#F28CB1"/>',
         '<path d="M 9 -22 q 4 -1 7 1" stroke="#F28CB1" stroke-width="1.2" fill="none"/>',
         "</g>"]
    return "".join(g)


# ---------------------------------------------------------------- assemble
def las_vegas():
    out = [sky(), mountains(), _grade(skyline(), 0.88), ground()]   # the Strip a step stronger out of the haze
    sx, gy = 405, 395
    # the convertible on its way to the Strip
    cx_, cb = C(1.9, 0, 21)
    out.append(vintage_car(cx_, cb, C.f * 2.0 / 21))
    out.append(garden(sx, gy))
    # Joshua tree on the left shoulder, lit from the sun on its right
    jx, jb = 52, 392
    out.append(f'<path d="M {jx - 10} {jb} L {jx + 12} {jb} L {jx - 60} 450 L {jx - 120} 450 Z" fill="#B0603E" opacity="0.22"/>')
    out.append(f'<ellipse cx="{jx}" cy="{jb}" rx="22" ry="4" fill="#B0603E" opacity="0.3"/>')
    out.append(creosote(jx + 28, jb + 3, 12, 3, light=1))
    out.append(joshua_tree(jx, jb, 262, 5, light=1))
    out.append(brittlebush(jx - 8, jb + 8, 16, 8, light=1))
    out.append(welcome_sign(sx, gy))
    # island planting (sun on their left)
    out.append(brittlebush(sx - 92, gy + 4, 22, 32))
    out.append(creosote(sx - 136, gy + 10, 13, 31))
    out.append(barrel(sx + 60, gy + 6, 12, 33))
    out.append(barrel(sx + 80, gy + 10, 9, 34))
    out.append(brittlebush(sx + 132, gy + 6, 18, 35))
    # a couple posing under the sign, their friend taking the picture
    out.append(F.person(sx + 2, gy + 10, 46, "couple_front", 1, {"season": "summer"}, seed=12, rim="#FFE2B0", light=-1))
    out.append(F.person(sx - 70, gy + 30, 48, "photo", 1, {"season": "summer", "top": "#F28CB1", "hat_kind": "sunhat", "hat": "#F7E1B5", "form": "f"}, seed=27, rim="#FFE2B0", light=-1))
    # foreground Mojave garden
    out.append(rock(sx + 28, gy + 40, 34, 15, 36))
    out.append(barrel(470, 446, 15, 39))
    out.append(yucca(550, 446, 124, 38))
    return "\n".join(out)


# ---------------------------------------------------------------- golden-hour grade (owners: "a bit darker, more orange")
_HEX = re.compile(r"#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})(?![\w-])")


def _grade(svg, dark=0.92):
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    from recolor_places import hex_to_oklch, oklch_to_hex
    cache = {}

    def g(m):
        L, C, H = hex_to_oklch(m.group(0))
        if C < 0.012:                       # whites/greys: warm them slightly, keep the sign's white
            return oklch_to_hex(L * 0.97, C + 0.012, 70)
        if 20 <= H <= 110:                  # sand, peach, gold -> deeper orange
            H = H + (55 - H) * 0.35
            C = C * 1.25
        L = L * dark
        return oklch_to_hex(L, C, H)
    return _HEX.sub(lambda m: cache.setdefault(m.group(0).upper(), g(m)), svg)


def _save(collection, slug, body):
    OUT.mkdir(parents=True, exist_ok=True)
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600">\n' + body.strip() + "\n</svg>\n"
    dest = OUT / f"{slug}.svg"
    if len(sys.argv) > 1:
        dest = pathlib.Path(sys.argv[1]) / f"{slug}.svg"
        dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(svg, encoding="utf-8")
    print(dest, len(svg))


def build():
    PM.save = _save
    PM.poster("places", "las-vegas", "LAS VEGAS", "NEVADA · USA", _grade(las_vegas()), "#F1E2C6", "#D9B27E", "#4A3424", "#93673A")


if __name__ == "__main__":
    build()
