"""American Places, painted edition: each poster is composed like a small gouache painting — graded skies,
atmospheric depth, light direction, textured rock and water, irregular trees."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from common import BEBAS, SERIF_IT, MONO
from poster import ANTON, poster
import figures as F


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


# ---------------------------------------------------------------- Yellowstone
def spur(pts, u, k, grad, shade, seed, streak_cols, trees=0, light_edge=None):
    """One buttress of canyon wall: filled shape + streaks clipped to it + shadow facet + trees on the crest."""
    cid = f"{u}-sp{k}"
    out = [f'<clipPath id="{cid}"><polygon points="{P(pts)}"/></clipPath>',
           f'<polygon points="{P(pts)}" fill="url(#{grad})"/>']
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]
    box = (min(xs), min(ys) - 10, max(xs), max(ys))
    g = [streaks(int((box[2] - box[0]) * (box[3] - box[1]) / 260), seed, box, streak_cols, w=(1, 3.2),
                 length=(10, 60), opacity=(0.25, 0.65), slant=0.25)]
    if shade:
        g.append(f'<polygon points="{P(shade)}" fill="#6E3E36" opacity="0.28"/>')
    out.append(f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>")
    if light_edge:
        out.append(f'<polyline points="{P(light_edge)}" fill="none" stroke="#FFF4D8" stroke-width="2" stroke-linejoin="round" opacity="0.85"/>')
    rnd = random.Random(seed + 5)
    edge = light_edge or pts[:2]
    for _ in range(trees):
        i = rnd.randrange(len(edge) - 1)
        t = rnd.random()
        x = edge[i][0] + (edge[i + 1][0] - edge[i][0]) * t
        y = edge[i][1] + (edge[i + 1][1] - edge[i][1]) * t
        out.append(conifer(x + rnd.uniform(-4, 4), y + rnd.uniform(2, 10), rnd.uniform(7, 15), rnd.choice(["#3F5E4C", "#4B6B56", "#365443"]), rnd.random()))
    return "".join(out)


def puff_column(u, cx, base, top, seed, r0=10, r1=58, drift=60, n=70, grad=None, hi="#FFF8EE", hi_op=0.55):
    """Billowing steam / cloud column built from clusters of small puffs filled with one shared gradient
    (shadow side to lit side), then soft highlights on the lit puffs for volume."""
    rnd = random.Random(seed)
    body, lights, shades = [], [], []
    for i in range(n):
        t = (i / (n - 1)) ** 0.85
        y = base - (base - top) * t
        r = r0 + (r1 - r0) * t ** 0.9
        x = cx + drift * t ** 1.6
        for _ in range(4):
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.uniform(0.2, 0.75) * r
            rr = r * rnd.uniform(0.32, 0.55)
            px, py = x + d * math.cos(a), y + d * math.sin(a) * 0.8
            body.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rr:.1f}"/>')
            if math.cos(a) < -0.35 or math.sin(a) > 0.6:
                shades.append(f'<circle cx="{px - rr * 0.18:.1f}" cy="{py + rr * 0.22:.1f}" r="{rr * 0.55:.1f}"/>')
            if math.cos(a) > -0.2 and math.sin(a) < 0.4:
                lights.append(f'<circle cx="{px + rr * 0.22:.1f}" cy="{py - rr * 0.25:.1f}" r="{rr * 0.62:.1f}"/>')
    return (f'<g fill="url(#{grad})">' + "".join(body) + "</g>"
            + '<g fill="#8F88B0" opacity="0.18">' + "".join(shades) + "</g>"
            + f'<g fill="{hi}" opacity="{hi_op}">' + "".join(lights) + "</g>")


def bison(x, y, s, body="#33241C", cape="#6A4A34", face="#1E140E", rim="#F6B062", flip=False):
    """American bison in profile facing left; (x, y) = left end at ground level, s = scale (1 -> 150 px long)."""
    pts = [(4, 74), (2, 64), (6, 44), (14, 34), (26, 20), (40, 8), (56, 2), (72, 6), (90, 18), (112, 24), (132, 26), (144, 32),
           (148, 46), (146, 62), (140, 74), (138, 98), (130, 100), (128, 78), (122, 72), (104, 74), (84, 76), (72, 80),
           (70, 98), (60, 100), (58, 86), (48, 90), (40, 84), (32, 90), (24, 92), (18, 86), (10, 82)]
    cape_pts = [(2, 64), (6, 44), (14, 34), (26, 20), (40, 8), (56, 2), (72, 6), (80, 10), (84, 22), (78, 32), (86, 44),
                (80, 56), (88, 68), (84, 76), (72, 80), (70, 98), (60, 100), (58, 86), (48, 90), (40, 84), (32, 90), (24, 92),
                (18, 86), (10, 82), (4, 74)]
    head = [(4, 74), (2, 64), (6, 44), (14, 34), (24, 38), (28, 56), (22, 74), (14, 80)]
    far_legs = ([(80, 76), (84, 98), (76, 99), (72, 80)], [(116, 72), (122, 97), (114, 98), (110, 74)])
    rnd = random.Random(int(x))
    fur = "".join(f'<path d="M {fx:.0f} {fy:.0f} q {rnd.uniform(1, 4):.1f} 4 {rnd.uniform(-1, 2):.1f} {rnd.uniform(6, 11):.1f}"/>'
                  for fx, fy in [(rnd.uniform(26, 82), rnd.uniform(12, 84)) for _ in range(46)])
    tf = f'translate({x} {y - 100 * s}) scale({-s if flip else s} {s})'
    return (f'<g transform="{tf}">'
            + "".join(f'<polygon points="{P(l)}" fill="#1E140E"/>' for l in far_legs)
            + f'<polygon points="{P(pts)}" fill="{body}"/>'
            + f'<polygon points="{P(cape_pts)}" fill="{cape}"/>'
            + f'<g fill="none" stroke="#9A7454" stroke-width="1.5" stroke-linecap="round" opacity="0.75">{fur}</g>'
            + f'<polygon points="{P(head)}" fill="{face}"/>'
            + f'<polyline points="{P(pts[2:14])}" fill="none" stroke="{rim}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round" opacity="0.95"/>'
            + '<path d="M 18 40 q -8 -6 -2 -16" fill="none" stroke="#E8DCC8" stroke-width="3.4" stroke-linecap="round"/>'
            + '<circle cx="13" cy="50" r="1.9" fill="#F2E6D2"/>'
            + '<path d="M 144 32 q 8 12 3 30" fill="none" stroke="#1E140E" stroke-width="3" stroke-linecap="round"/><ellipse cx="147" cy="64" rx="3" ry="5" fill="#1E140E"/>'
            + "</g>")


def yellowstone():
    u = "ys"
    out = [defs(
        lg(f"{u}-sky", [(0, "#3F5D8C"), (0.32, "#8D8DB9"), (0.62, "#E6A88C"), (0.85, "#F7CF9C"), (1, "#FBE3B4")]),
        lg(f"{u}-puff", [(0, "#A9A3C4"), (0.45, "#DCCFDD"), (1, "#FFEBD8")], 200, 0, 380, 0, units="userSpaceOnUse"),
        lg(f"{u}-ground", [(0, "#D9CFC0"), (1, "#F0E7DA")]),
        lg(f"{u}-meadow", [(0, "#8E8A52"), (1, "#5E6638")]),
        lg(f"{u}-col", [(0, "#FFFFFF", 0.95), (1, "#F2ECF4", 0.95)], 0, 0, 1, 0),
        lg(f"{u}-haze", [(0, "#F7CF9C", 0), (1, "#F7CF9C", 0.85)]),
        lg(f"{u}-pool", [(0, "#F4C27A"), (1, "#E07A4A")], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(470, 286, 210, "#FFE2A6", f"{u}-sun", 0.95))
    out.append('<circle cx="470" cy="284" r="22" fill="#FFF1C8"/>')
    # thin high clouds catching the sunset
    out.append('<g fill="#F6B88E" opacity="0.55">' + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="4"/>' for x, y, w in ((120, 110, 90), (90, 124, 60), (520, 96, 80), (560, 112, 50), (420, 150, 70))) + "</g>")
    # distant hills
    poly, far = ridge_poly([(-10, 286), (80, 270), (190, 282), (300, 266), (400, 280), (520, 268), (610, 278)], 3, amp=5, fill="#9A88A8")
    out.append(poly)
    out.append(f'<rect x="0" y="250" width="600" height="60" fill="url(#{u}-haze)"/>')
    # lodgepole forest, backlit
    poly, fl = ridge_poly([(-10, 318), (200, 314), (420, 318), (610, 312)], 9, amp=2, fill="#3A4152")
    out.append(poly)
    out.append(tree_line(fl, 21, ["#3A4152", "#343B4C", "#414860"], density=2.6, hmin=26, hmax=62))
    out.append(tree_line(fl, 22, ["#2F3546", "#2B3142"], density=1.2, hmin=40, hmax=84, xmin=-10, xmax=200))
    out.append(tree_line(fl, 23, ["#2F3546", "#2B3142"], density=1.2, hmin=40, hmax=84, xmin=420, xmax=610))
    # geyser basin
    out.append(f'<path d="M -10 330 Q 300 316 610 326 L 610 444 L -10 444 Z" fill="url(#{u}-ground)"/>')
    out.append(f'<path d="M -10 328 Q 300 316 610 324 L 610 334 Q 300 326 -10 338 Z" fill="#B9AFA6" opacity="0.6"/>')
    out.append(dots(220, 33, (-10, 334, 610, 400), "#B8AC9C", r=(0.6, 1.8), opacity=(0.3, 0.7)))
    out.append('<g fill="none" stroke="#C8BCAC" stroke-width="1.2" opacity="0.8">' + "".join(
        f'<path d="M {x} {y} q 14 -3 28 0 q 10 2 20 -1"/>' for x, y in ((40, 352), (150, 344), (360, 350), (470, 360), (540, 346), (90, 372), (420, 374))) + "</g>")
    # runoff channels with bacterial mats reflecting the sky
    out.append(f'<path d="M 252 352 C 220 364 170 362 120 376 C 80 388 40 386 -10 396 L -10 404 C 50 396 92 398 130 386 C 180 372 226 374 262 356 Z" fill="url(#{u}-pool)" opacity="0.85"/>')
    out.append('<path d="M 254 354 C 222 366 172 365 124 378 C 84 390 44 389 -10 398" fill="none" stroke="#8FB9C8" stroke-width="3" opacity="0.9"/>')
    out.append(f'<path d="M 300 356 C 340 370 380 372 430 380 C 470 386 520 384 610 392 L 610 398 C 520 392 470 394 428 388 C 378 380 336 378 296 362 Z" fill="#E9A15C" opacity="0.7"/>')
    # the cone
    out.append('<path d="M 216 362 Q 240 340 270 338 Q 300 340 324 362 Z" fill="#CFC3B4"/><path d="M 270 338 Q 300 340 324 362 L 284 362 Z" fill="#B8AB9C"/>')
    out.append('<g stroke="#E8A35A" stroke-width="2" opacity="0.7"><line x1="246" y1="352" x2="236" y2="362"/><line x1="292" y1="350" x2="304" y2="362"/></g>')
    # Old Faithful: water column, then billowing steam drifting right
    out.append(f'<path d="M 262 344 Q 266 260 258 200 L 282 200 Q 276 260 280 344 Z" fill="url(#{u}-col)"/>')
    out.append(puff_column(u, 270, 334, 140, 5, r0=10, r1=62, drift=50, n=90, grad=f"{u}-puff"))
    out.append('<g stroke="#FFFFFF" stroke-width="1.6" opacity="0.8" stroke-linecap="round">' + "".join(
        f'<line x1="{x}" y1="{y}" x2="{x + dx}" y2="{y - 30}"/>' for x, y, dx in ((264, 330, -2), (270, 320, 0), (276, 334, 2), (268, 300, 1))) + "</g>")
    # spray falling back
    out.append(dots(60, 31, (226, 250, 316, 340), "#FFFFFF", r=(0.8, 2), opacity=(0.5, 1)))
    # little vents steaming across the basin
    for k, (cx, cy) in enumerate(((96, 340), (520, 338), (410, 344))):
        out.append(mist(cx, cy - 26, 16, 34, "#FFFFFF", f"{u}-v{k}", 0.75))
        out.append(mist(cx + 6, cy - 54, 14, 22, "#FFFFFF", f"{u}-w{k}", 0.4))
    # boardwalk with visitors
    out.append('<path d="M -10 410 C 120 398 260 398 360 404 C 460 410 540 408 610 402 L 610 412 C 540 418 460 420 360 414 C 260 408 120 408 -10 420 Z" fill="#8A6A50"/>')
    out.append('<g stroke="#6A4E3A" stroke-width="2">' + "".join(f'<line x1="{x}" y1="{404 - (x / 600) * 2:.0f}" x2="{x}" y2="{418 - (x / 600) * 4:.0f}"/>' for x in range(10, 600, 26)) + "</g>")
    # visitors on the boardwalk watching the eruption, backlit by the low sun on the right
    vis = dict(rim="#FFD49A", light=1, tint=("#4A3A5E", 0.2))
    out.append(F.couple(156, 402, 23, palette={"top": "#3B4A6B", "season": "any"}, seed=4, **vis))
    out.append(F.person(178, 402, 23, "photo", -1, {"top": "#2E3A30", "bottom": "#CDBB94"}, seed=7, **vis))
    out.append(F.person(330, 402, 22, "stand_back", 1, {"top": "#5E4A7A", "form": "f"}, seed=11, **vis))
    out.append(F.person(342, 402, 15, "child_back", 1, {"top": "#E0A040"}, seed=12, **vis))
    # foreground meadow with a bison, rim-lit by the low sun
    out.append(f'<path d="M -10 424 Q 200 412 380 418 Q 500 420 610 412 L 610 444 L -10 444 Z" fill="url(#{u}-meadow)"/>')
    out.append(grass(160, 51, (-10, 414, 610, 444), ["#C9B26A", "#A8994E", "#6E7240", "#E0C27A"], h=(6, 18)))
    out.append(bison(372, 438, 0.92))
    out.append(grass(40, 52, (370, 430, 520, 444), ["#C9B26A", "#A8994E", "#E0C27A"], h=(6, 14)))
    out.append('<g fill="none" stroke="#3A3046" stroke-width="2" stroke-linecap="round"><path d="M 120 168 q 7 -5 13 0 q 6 -5 13 0"/><path d="M 148 186 q 5 -4 8 0 q 4 -4 8 0"/></g>')
    return "\n".join(out)


# ---------------------------------------------------------------- Nashville (Lower Broadway at night)
class Cam:
    """Simple pinhole camera: X right, Y up (metres), Z forward. Screen centre (cx, vpy)."""
    def __init__(self, f=300, cx=300, vpy=290, eye=1.6):
        self.f, self.cx, self.vpy, self.eye = f, cx, vpy, eye

    def __call__(self, X, Y, Z):
        return (self.cx + self.f * X / Z, self.vpy + self.f * (self.eye - Y) / Z)

    def quad_x(self, X, Z0, Z1, Y0, Y1):
        """Facade rectangle in the plane X = const."""
        return [self(X, Y0, Z0), self(X, Y1, Z0), self(X, Y1, Z1), self(X, Y0, Z1)]

    def quad_z(self, Z, X0, X1, Y0, Y1):
        """Rectangle facing the camera at depth Z."""
        return [self(X0, Y0, Z), self(X0, Y1, Z), self(X1, Y1, Z), self(X1, Y0, Z)]


def neon_text(x, y, s, font, size, color, ls=0):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" {font} font-size="{size:.1f}" letter-spacing="{ls}" fill="none" stroke="{color}" stroke-width="{size * 0.2:.1f}" stroke-linejoin="round" opacity="0.32">{s}</text>'
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" {font} font-size="{size:.1f}" letter-spacing="{ls}" fill="#FFF6E8" stroke="{color}" stroke-width="{size * 0.05:.1f}">{s}</text>')


def nashville():
    u = "nv"
    C = Cam(f=300, vpy=292, eye=1.7)
    out = [defs(
        lg(f"{u}-sky", [(0, "#121836"), (0.5, "#25306A"), (0.8, "#58407E"), (1, "#C25E7E")]),
        lg(f"{u}-street", [(0, "#3A2C40"), (1, "#141018")]),
        lg(f"{u}-walk", [(0, "#4E3C48"), (1, "#2A2028")]),
        lg(f"{u}-tower", [(0, "#34407A"), (1, "#1A1E3C")], 0, 0, 1, 0),
        lg(f"{u}-dark", [(0, "#0E0A18", 0.7), (0.5, "#0E0A18", 0.3), (1, "#0E0A18", 0)], 0, 0, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-store", [(0, "#FFD98E"), (1, "#F09A4A")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(60, 4, (150, 40, 450, 200), "#F6EDE0", r=(0.6, 1.4), opacity=(0.4, 1)))
    # distant skyline and the two-spired tower closing the view
    out.append('<g fill="#2A3262">' + "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{300 - y}"/>' for x, y, w in (
        (228, 214, 26), (252, 196, 22), (360, 206, 26), (384, 224, 22), (270, 230, 18))) + "</g>")
    tw = [(290, 300), (290, 168), (296, 160), (296, 112), (302, 96), (308, 112), (308, 136), (322, 122), (336, 136), (336, 112), (342, 96), (348, 112), (348, 160), (354, 168), (354, 300)]
    out.append(f'<polygon points="{P(tw)}" fill="url(#{u}-tower)"/>')
    out.append(f'<polygon points="{P([(322, 122), (336, 136), (336, 112), (342, 96), (348, 112), (348, 160), (354, 168), (354, 300), (326, 300)])}" fill="#11152E" opacity="0.55"/>')
    rnd = random.Random(8)
    out.append("".join(f'<rect x="{x}" y="{y}" width="2.4" height="2.4" fill="#F7D58A" opacity="{rnd.uniform(0.35, 1):.2f}"/>'
                       for x in range(294, 352, 5) for y in range(166, 296, 6) if rnd.random() < 0.42))
    for x in (302, 342):
        out.append(glow(x, 96, 12, "#FF5A5A", f"{u}-r{x}", 0.8) + f'<circle cx="{x}" cy="96" r="2.4" fill="#FF6A6A"/>')
    # street, curbs, sidewalks
    W, CURB = 15, 10.5
    out.append(f'<polygon points="{P([C(-W, 0, 300), C(W, 0, 300), C(W, 0, 2.5), C(-W, 0, 2.5)])}" fill="url(#{u}-street)"/>')
    for sgn in (-1, 1):
        out.append(f'<polygon points="{P([C(sgn * W, 0, 300), C(sgn * CURB, 0, 300), C(sgn * CURB, 0, 2.5), C(sgn * W, 0, 2.5)])}" fill="url(#{u}-walk)"/>')
        out.append(f'<polygon points="{P([C(sgn * CURB, 0.15, 300), C(sgn * CURB, 0.15, 2.5), C(sgn * CURB, 0, 2.5), C(sgn * CURB, 0, 300)])}" fill="#8A7A80"/>')
    for z in (6, 9, 12.5, 16, 22, 30, 40, 55, 75, 100):
        out.append(f'<polygon points="{P([C(-0.12, 0, z), C(0.12, 0, z), C(0.12, 0, z + z * 0.12), C(-0.12, 0, z + z * 0.12)])}" fill="#E9B949" opacity="0.85"/>')
    # buildings: (Z0, Z1, height m, colour, bays)
    left = [(6, 20, 19, "#8E3B2F", 4), (20, 29, 15, "#D2B48A", 3), (29, 40, 18, "#6E3442", 3), (40, 52, 14, "#A5543A", 3),
            (52, 68, 17, "#4E5E7A", 3), (68, 90, 13, "#86503C", 2), (90, 130, 16, "#5A3A40", 2), (130, 300, 12, "#4A3440", 2)]
    right = [(6, 18, 15, "#3F5A4E", 3), (18, 30, 20, "#9A4632", 4), (30, 40, 13, "#C9A06A", 3), (40, 55, 18, "#5E3A5A", 3),
             (55, 72, 14, "#A04A3A", 3), (72, 95, 17, "#3E4A6A", 2), (95, 140, 13, "#7A4A3A", 2), (140, 300, 15, "#4A3A48", 2)]
    lit = ["#F7C873", "#F4B860", "#FFD98E"]
    for sgn, blds in ((-1, left), (1, right)):
        X = sgn * W
        for k, (z0, z1, h, col, bays) in enumerate(blds):
            out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, 0, h))}" fill="{col}"/>')
            out.append('<g stroke="#000" stroke-opacity="0.13" stroke-width="1">' + "".join(
                f'<line x1="{C(X, y, z0)[0]:.1f}" y1="{C(X, y, z0)[1]:.1f}" x2="{C(X, y, z1)[0]:.1f}" y2="{C(X, y, z1)[1]:.1f}"/>' for y in [4.4 + 0.5 * i for i in range(int((h - 5) / 0.5))]) + "</g>")
            out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, h - 0.9, h))}" fill="#EADCC4" opacity="0.6"/>')
            out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, h - 1.6, h - 0.9))}" fill="#000" opacity="0.18"/>')
            # pilasters between buildings
            out.append(f'<polygon points="{P(C.quad_x(X, z0, z0 + 0.5, 0, h))}" fill="#000" opacity="0.2"/>')
            floors = int((h - 5) / 3.6)
            for f_ in range(floors):
                y0 = 5 + f_ * 3.6
                for i in range(bays):
                    za = z0 + (z1 - z0) * (i + 0.28) / bays
                    zb = z0 + (z1 - z0) * (i + 0.72) / bays
                    on = random.Random(k * 31 + f_ * 7 + i + sgn).random() < 0.62
                    q = C.quad_x(X, za, zb, y0, y0 + 2.3)
                    out.append(f'<polygon points="{P(q)}" fill="{random.Random(k + i + f_).choice(lit) if on else "#221A2A"}"/>')
                    hood = C.quad_x(X, za - 0.15, zb + 0.15, y0 + 2.3, y0 + 2.6)
                    out.append(f'<polygon points="{P(hood)}" fill="#EADCC4" opacity="0.5"/>')
                    if on:
                        mid = C(X, y0 + 1.15, (za + zb) / 2)
                        out.append(f'<line x1="{C(X, y0, (za + zb) / 2)[0]:.1f}" y1="{C(X, y0, (za + zb) / 2)[1]:.1f}" x2="{C(X, y0 + 2.3, (za + zb) / 2)[0]:.1f}" y2="{C(X, y0 + 2.3, (za + zb) / 2)[1]:.1f}" stroke="#7A4A2A" stroke-width="{max(0.5, 30 / za):.1f}" opacity="0.6"/>')
            # glowing storefront with a dark awning
            sq = C.quad_x(X, z0 + (z1 - z0) * 0.08, z1 - (z1 - z0) * 0.08, 0.3, 3.4)
            out.append(f'<polygon points="{P(sq)}" fill="url(#{u}-store)"/>')
            for t in (0.36, 0.64):
                zz = z0 + (z1 - z0) * t
                a_, b_ = C(X, 0.3, zz), C(X, 3.4, zz)
                out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#3A2020" stroke-width="{max(0.6, 60 / zz):.1f}"/>')
            out.append(f'<polygon points="{P(C.quad_x(X, z0 + (z1 - z0) * 0.06, z1 - (z1 - z0) * 0.06, 3.5, 4.1))}" fill="#1E1418"/>')
            # warm light spilling onto the sidewalk
            spill = [C(X, 0, z0 + (z1 - z0) * 0.1), C(X, 0, z1 - (z1 - z0) * 0.1), C(X - sgn * 3, 0, z1 - (z1 - z0) * 0.1), C(X - sgn * 3, 0, z0 + (z1 - z0) * 0.1)]
            out.append(f'<polygon points="{P(spill)}" fill="#F7B860" opacity="0.22"/>')
        # darken the upper floors so the street glow reads
        for z0, z1, h, col, bays in blds:
            out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, 0, h))}" fill="url(#{u}-dark)"/>')
    # neon blade signs (perpendicular to the facades, so they face us)
    specs = [  # side, Z, sign bottom m, height m, depth m, colour, word
        (-1, 19, 4.6, 9.5, 2.0, "#FF5FA2", "HONKY TONK"),
        (-1, 36, 4.5, 7.5, 1.8, "#FFD25E", "BOOTS"),
        (-1, 62, 4.5, 6, 1.8, "#58E6F5", "BAR"),
        (1, 21, 4.8, 8, 2.0, "#FFD25E", "MUSIC"),
        (1, 42, 4.5, 7.5, 1.8, "#FF5FA2", "DANCE"),
        (1, 66, 4.5, 6, 1.8, "#7CF29A", "EATS"),
    ]
    for k, (sgn, z, yb, hh, d, tc, word) in enumerate(sorted(specs, key=lambda t: -t[1])):
        X0 = sgn * W
        X1 = sgn * (W - d)
        q = C.quad_z(z, min(X0, X1), max(X0, X1), yb, yb + hh)
        x0, y0, x1, y1 = q[0][0], q[1][1], q[2][0], q[0][1]
        cx = (x0 + x1) / 2
        out.append(glow(cx, (y0 + y1) / 2, (y1 - y0) * 0.8, tc, f"{u}-g{k}", 0.4))
        out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="{(x1 - x0) * 0.12:.1f}" fill="#1A1420" stroke="{tc}" stroke-width="{max(1, (x1 - x0) * 0.06):.1f}"/>')
        letters = [c for c in word if c != " "]
        step = (y1 - y0) * 0.9 / len(letters)
        fs = min(step * 1.0, (x1 - x0) * 0.78)
        for i, c in enumerate(letters):
            out.append(neon_text(cx, y0 + (y1 - y0) * 0.05 + step * (i + 0.5) + fs * 0.36, c, ANTON, fs, tc))
        # wet-street reflection
        ry = C(X1, 0, z)[1]
        rh = min(444 - ry, (y1 - y0) * 1.1)
        out.append(defs(lg(f"{u}-rf{k}", [(0, tc, 0.4), (1, tc, 0)])))
        for j in range(5):
            yy = ry + 3 + rh * j / 5
            ww = (x1 - x0) * (0.7 - 0.08 * j) * (1 + 0.25 * math.sin(j * 2.3 + k))
            out.append(f'<rect x="{cx - ww / 2:.1f}" y="{yy:.1f}" width="{ww:.1f}" height="{rh / 5 * 0.7:.1f}" rx="{rh / 12:.1f}" fill="{tc}" opacity="{0.22 * (1 - j / 5):.2f}"/>')
    # neon guitar on the near right facade, and a script sign
    gx, gy = C(W - 0.05, 11.5, 30)
    out.append(glow(gx - 22, gy, 60, "#FF9F4A", f"{u}-gg", 0.35))
    out.append(f'<g transform="translate({gx - 22:.1f} {gy:.1f}) rotate(-28) scale(0.62)" fill="none" stroke-linecap="round" stroke-linejoin="round">'
               '<g stroke="#FF9F4A" stroke-width="7" opacity="0.3"><path d="M 0 -60 L 0 -14"/><path d="M 0 -14 C -18 -16 -22 4 -12 12 C -26 22 -24 50 0 50 C 24 50 26 22 12 12 C 22 4 18 -16 0 -14 Z"/></g>'
               '<g stroke="#FFE2B8" stroke-width="2.4"><path d="M 0 -60 L 0 -14"/><path d="M 0 -14 C -18 -16 -22 4 -12 12 C -26 22 -24 50 0 50 C 24 50 26 22 12 12 C 22 4 18 -16 0 -14 Z"/><circle cx="0" cy="18" r="6"/><path d="M -5 -66 L 5 -66 L 5 -58 L -5 -58 Z"/></g></g>')
    # people strolling, a busker with a guitar case
    def person(X, Z, h, col, case=False):
        x, base = C(X, 0, Z)
        hh = C.f * h / Z
        sd = int(abs(X) * 10 + Z)
        pose = "stand" if case else ("stand_back", "stand", "stand_34", "stand_back")[sd % 4]
        g = F.person(x, base, hh, pose, -1 if X > 0 else 1, {"top": col, "season": "any"}, seed=sd,
                     rim="#FFC890", light=-1 if X < 0 else 1, tint=("#2A2040", 0.28))
        if case:
            g = (f'<path d="M {x + hh * 0.04:.1f} {base - hh * 0.98:.1f} q {hh * 0.16:.1f} {hh * 0.04:.1f} {hh * 0.12:.1f} {hh * 0.26:.1f} q {hh * 0.14:.1f} {hh * 0.14:.1f} {hh * 0.04:.1f} {hh * 0.42:.1f} q {-hh * 0.12:.1f} {hh * 0.06:.1f} {-hh * 0.18:.1f} {-hh * 0.08:.1f} Z" fill="#3A2A22"/>') + g
        return g
    for X, Z, h, col, case in ((-12.5, 70, 1.7, "#7A5A9A", False), (12.0, 48, 1.75, "#C9574A", False), (-12.2, 30, 1.8, "#3E6A8A", True),
                               (-13.0, 26, 1.65, "#D9A04A", False), (12.6, 20, 1.7, "#4A7A5A", False), (11.6, 17, 1.6, "#B85A8A", False),
                               (-11.8, 13, 1.75, "#E0C27A", False), (-12.9, 12.4, 1.6, "#5A8AA8", False)):
        out.append(person(X, Z, h, col, case))
    # crosswalk in the foreground
    for i in range(-6, 7):
        X0 = i * 1.9 - 0.6
        out.append(f'<polygon points="{P([C(X0, 0, 3.0), C(X0 + 1.2, 0, 3.0), C(X0 + 1.2, 0, 4.6), C(X0, 0, 4.6)])}" fill="#D8D0D8" opacity="0.2"/>')
    # wet sheen of the storefronts on the asphalt
    for sgn in (-1, 1):
        out.append(f'<polygon points="{P([C(sgn * 10.5, 0, 8), C(sgn * 6, 0, 8), C(sgn * 6, 0, 120), C(sgn * 10.5, 0, 120)])}" fill="#F7B860" opacity="0.08"/>')
    # a couple crossing hand in hand, rim-lit by the neon
    xa, base = C(-3.6, 0, 5.2)
    xb, _ = C(-2.75, 0, 5.2)
    hh = C.f * 1.7 / 5.2
    out.append(F.couple((xa + xb) / 2, base, hh, palette={"top": "#3E4A6A", "bottom": "#1E1A26"}, seed=21, rim="#FF8FB8", light=1,
                        tint=("#2A2040", 0.3), gap=40))
    # vintage pickup cruising toward the tower, tail lights glowing on the wet road
    tz, tX = 26, 3.2
    x, base = C(tX, 0, tz)
    k = C.f / tz / 20
    out.append(f'<g transform="translate({x:.1f} {base:.1f}) scale({k:.3f})">'
               '<path d="M -46 -12 L -46 -40 Q -46 -44 -42 -44 L -30 -44 L -24 -66 Q -22 -70 -18 -70 L 18 -70 Q 22 -70 24 -66 L 30 -44 L 42 -44 Q 46 -44 46 -40 L 46 -12 Z" fill="#2E6A8A"/>'
               '<path d="M -20 -46 L -16 -64 L 16 -64 L 20 -46 Z" fill="#F2C98A" opacity="0.55"/><rect x="-46" y="-24" width="92" height="7" fill="#D6DEE6"/>'
               '<rect x="-44" y="-38" width="11" height="8" rx="2" fill="#FF3A3A"/><rect x="33" y="-38" width="11" height="8" rx="2" fill="#FF3A3A"/>'
               '<rect x="-12" y="-36" width="24" height="10" rx="2" fill="#E9DCC4"/>'
               '<rect x="-42" y="-14" width="18" height="14" rx="4" fill="#0E0C12"/><rect x="24" y="-14" width="18" height="14" rx="4" fill="#0E0C12"/></g>')
    for sx in (-38.5, 38.5):
        out.append(glow(x + sx * k, base - 34 * k, 22 * k, "#FF3A3A", f"{u}-t{int(sx)}", 0.65))
        out.append(f'<rect x="{x + sx * k - 3 * k:.1f}" y="{base + 2:.1f}" width="{6 * k:.1f}" height="{444 - base:.1f}" fill="#FF3A3A" opacity="0.2"/>')
    return "\n".join(out)


# ---------------------------------------------------------------- Las Vegas (the Strip from the Welcome sign)
def palm_tree(x, base, h, trunk="#2A1E2A", frond="#1E2A2A", rim=None, seed=1, lean=0.08):
    """Tall fan of fronds on a slim curved trunk; rim = colour of light catching the right edges."""
    rnd = random.Random(seed)
    tx, ty = x + lean * h, base - h
    w0, w1 = max(1.0, h * 0.02), max(0.7, h * 0.012)
    out = [f'<path d="M {x - w0:.1f} {base:.1f} Q {x + lean * h * 0.2:.1f} {base - h * 0.5:.1f} {tx - w1:.1f} {ty:.1f} L {tx + w1:.1f} {ty:.1f} Q {x + lean * h * 0.2 + w0 * 2:.1f} {base - h * 0.5:.1f} {x + w0:.1f} {base:.1f} Z" fill="{trunk}"/>']
    for i in range(11):
        ang = math.radians(-180 + i * 18 + rnd.uniform(-6, 6))
        L = h * rnd.uniform(0.26, 0.34)
        droop = h * 0.11 * (0.4 + abs(math.cos(ang)))
        ex, ey = tx + L * math.cos(ang), ty + L * math.sin(ang) * 0.55 + droop
        mx, my = tx + L * 0.5 * math.cos(ang), ty + L * 0.5 * math.sin(ang) * 0.55 - h * 0.03
        wd = h * 0.025
        out.append(f'<path d="M {tx:.1f} {ty:.1f} Q {mx:.1f} {my - wd:.1f} {ex:.1f} {ey:.1f} Q {mx:.1f} {my + wd:.1f} {tx:.1f} {ty:.1f} Z" fill="{frond}"/>')
        if rim and math.cos(ang) > -0.2:
            out.append(f'<path d="M {tx:.1f} {ty:.1f} Q {mx:.1f} {my - wd:.1f} {ex:.1f} {ey:.1f}" fill="none" stroke="{rim}" stroke-width="{max(0.6, h * 0.006):.1f}" opacity="0.7"/>')
    return "".join(out)


def welcome_sign(x, base, k, u):
    """The mid-century welcome sign (public domain design, never trademarked), local units then scaled by k."""
    body = [(-56, -110), (-36, -150), (36, -150), (56, -110), (36, -70), (-36, -70)]
    inner = [(-50, -110), (-33, -145), (33, -145), (50, -110), (33, -75), (-33, -75)]
    bulbs = []
    for (x1, y1), (x2, y2) in zip(body, body[1:] + body[:1]):
        n = int(math.hypot(x2 - x1, y2 - y1) / 6)
        for i in range(n):
            t = i / n
            bulbs.append(f'<circle cx="{x1 + (x2 - x1) * t:.1f}" cy="{y1 + (y2 - y1) * t:.1f}" r="1.5"/>')
    circles = "".join(f'<circle cx="{-36 + i * 12}" cy="-132" r="5.6" fill="#FFFFFF" stroke="#C9C2CC" stroke-width="0.6"/>'
                      f'<text x="{-36 + i * 12}" y="-129" text-anchor="middle" {ANTON} font-size="8" fill="#D8263A">{c}</text>' for i, c in enumerate("WELCOME"))
    return (f'<g transform="translate({x:.1f} {base:.1f}) scale({k:.3f})">'
            + glow(0, -112, 90, "#FFF2C8", f"{u}-sg", 0.55)
            + '<rect x="-25" y="-72" width="7" height="72" fill="#CFCBD6"/><rect x="18" y="-72" width="7" height="72" fill="#CFCBD6"/>'
            + '<rect x="-21" y="-72" width="3" height="72" fill="#8E8A9C"/><rect x="22" y="-72" width="3" height="72" fill="#8E8A9C"/>'
            + f'<polygon points="{P(body)}" fill="#FFFDF6"/>'
            + f'<polygon points="{P(inner)}" fill="none" stroke="#D8263A" stroke-width="1.6"/>'
            + f'<g fill="#FFD25E">{"".join(bulbs)}</g>'
            + circles
            + f'<text x="0" y="-116" text-anchor="middle" {SERIF_IT} font-size="9" fill="#2A5DB0">to Fabulous</text>'
            + f'<text x="0" y="-92" text-anchor="middle" {ANTON} font-size="21" letter-spacing="0.5" fill="#D8263A">LAS VEGAS</text>'
            + f'<text x="0" y="-80" text-anchor="middle" {MONO} font-size="6.5" letter-spacing="2" fill="#2A5DB0">NEVADA</text>'
            + f'<polygon points="{P([(0, -172), (4, -160), (16, -158), (6, -151), (9, -139), (0, -146), (-9, -139), (-6, -151), (-16, -158), (-4, -160)])}" fill="#FFD25E" stroke="#D8263A" stroke-width="1.4"/>'
            + "</g>")


def las_vegas():
    u = "lv"
    C = Cam(f=300, vpy=252, eye=5.0)
    out = [defs(
        lg(f"{u}-sky", [(0, "#16163E"), (0.35, "#3A2A72"), (0.65, "#A24A86"), (0.85, "#EE7A6E"), (1, "#F9B868")]),
        lg(f"{u}-mtn", [(0, "#4A2E6A"), (1, "#2A1E46")]),
        lg(f"{u}-road", [(0, "#3A2A44"), (1, "#121018")]),
        lg(f"{u}-desert", [(0, "#5A3A4A"), (1, "#2A1C26")]),
        lg(f"{u}-bld", [(0, "#2A2452"), (1, "#16142E")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(50, 9, (0, 40, 600, 150), "#F6EDE0", r=(0.6, 1.4), opacity=(0.4, 1)))
    out.append(glow(300, 254, 260, "#FFB86A", f"{u}-dusk", 0.55))
    # Spring Mountains, two layers
    poly, _ = ridge_poly([(-10, 236), (70, 214), (150, 228), (240, 206), (330, 226), (420, 210), (520, 230), (610, 216)], 4, base=262, amp=6, fill="#7A4A86")
    out.append(poly)
    poly, _ = ridge_poly([(-10, 246), (110, 232), (210, 244), (330, 236), (450, 246), (610, 234)], 6, base=262, amp=4, fill=f"url(#{u}-mtn)")
    out.append(poly)
    # the Strip: resort towers on both sides, far to near
    rnd = random.Random(14)
    towers = []
    for sgn in (-1, 1):
        z = 150 if sgn < 0 else 170
        while z < 1400:
            X = sgn * rnd.uniform(24, 60)
            w = rnd.uniform(26, 50)
            h = rnd.uniform(60, 150)
            towers.append((z, X, w, h, rnd.random()))
            z *= rnd.uniform(1.1, 1.22)
    neon = ["#FF5FA2", "#58E6F5", "#FFD25E", "#9A7CFF", "#7CF29A"]
    for z, X, w, h, r in sorted(towers, key=lambda t: -t[0]):
        X0, X1 = (X - w, X) if X < 0 else (X, X + w)
        face = C.quad_z(z, X0, X1, 0, h)
        x0, x1, ytop, ybot = face[0][0], face[2][0], face[1][1], face[0][1]
        col = rnd.choice(neon)
        shape = int(r * 4)
        if shape == 0:      # rounded crown
            out.append(f'<path d="M {x0:.1f} {ybot:.1f} L {x0:.1f} {ytop + (x1 - x0) * 0.3:.1f} Q {(x0 + x1) / 2:.1f} {ytop - (x1 - x0) * 0.25:.1f} {x1:.1f} {ytop + (x1 - x0) * 0.3:.1f} L {x1:.1f} {ybot:.1f} Z" fill="url(#{u}-bld)"/>')
        elif shape == 1:    # stepped
            st = (x1 - x0) * 0.2
            out.append(f'<polygon points="{P([(x0, ybot), (x0, ytop + st * 2), (x0 + st, ytop + st * 2), (x0 + st, ytop + st), (x0 + 2 * st, ytop + st), (x0 + 2 * st, ytop), (x1 - 2 * st, ytop), (x1 - 2 * st, ytop + st), (x1 - st, ytop + st), (x1 - st, ytop + st * 2), (x1, ytop + st * 2), (x1, ybot)])}" fill="url(#{u}-bld)"/>')
        elif shape == 2:    # slanted roof
            out.append(f'<polygon points="{P([(x0, ybot), (x0, ytop + (x1 - x0) * 0.4), (x1, ytop), (x1, ybot)])}" fill="url(#{u}-bld)"/>')
        else:               # slab with a spire
            out.append(f'<polygon points="{P([(x0, ybot), (x0, ytop), (x1, ytop), (x1, ybot)])}" fill="url(#{u}-bld)"/>')
            out.append(f'<line x1="{(x0 + x1) / 2:.1f}" y1="{ytop:.1f}" x2="{(x0 + x1) / 2:.1f}" y2="{ytop - (ybot - ytop) * 0.15:.1f}" stroke="#2A2452" stroke-width="{max(0.8, (x1 - x0) * 0.05):.1f}"/>')
        # window grid
        cw = max(1.2, (x1 - x0) / 12)
        rows = int((ybot - ytop) / max(2.2, cw * 1.6))
        for i in range(rows):
            yy = ytop + (x1 - x0) * 0.42 + i * max(2.2, cw * 1.6)
            if yy > ybot - 3:
                break
            for j in range(10):
                if rnd.random() < 0.55:
                    out.append(f'<rect x="{x0 + (j + 1) * (x1 - x0) / 11 - cw * 0.3:.1f}" y="{yy:.1f}" width="{cw * 0.6:.1f}" height="{cw * 0.7:.1f}" fill="#F7D08A" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
        # neon crown band and a vertical light stripe
        out.append(f'<rect x="{x0:.1f}" y="{ytop + (x1 - x0) * 0.32:.1f}" width="{x1 - x0:.1f}" height="{max(1.2, (x1 - x0) * 0.05):.1f}" fill="{col}"/>')
        if r > 0.5:
            out.append(f'<rect x="{x1 - (x1 - x0) * 0.12:.1f}" y="{ytop + (x1 - x0) * 0.4:.1f}" width="{max(1, (x1 - x0) * 0.04):.1f}" height="{(ybot - ytop) * 0.7:.1f}" fill="{col}" opacity="0.8"/>')
        out.append(glow((x0 + x1) / 2, ytop + (x1 - x0) * 0.32, (x1 - x0) * 0.8, col, f"{u}-c{int(z)}{sgn if (sgn := 1 if X > 0 else -1) else 0}", 0.25))
    # the observation tower far up the Strip
    tx, tb = C(10, 0, 950)
    _, tt = C(10, 340, 950)
    out.append(f'<polygon points="{P([(tx - 3, tb), (tx - 1.4, tt + 14), (tx + 1.4, tt + 14), (tx + 3, tb)])}" fill="#2A2452"/>')
    out.append(f'<ellipse cx="{tx:.1f}" cy="{tt + 10:.1f}" rx="6" ry="4" fill="#2A2452"/><rect x="{tx - 6:.1f}" y="{tt + 9:.1f}" width="12" height="1.4" fill="#58E6F5"/>')
    out.append(f'<line x1="{tx:.1f}" y1="{tt + 6:.1f}" x2="{tx:.1f}" y2="{tt - 4:.1f}" stroke="#2A2452" stroke-width="1.2"/><circle cx="{tx:.1f}" cy="{tt - 4:.1f}" r="1.3" fill="#FF6A6A"/>')
    # desert flats and the boulevard
    out.append(f'<polygon points="{P([C(-600, 0, 2000), C(600, 0, 2000), C(600, 0, 3), C(-600, 0, 3)])}" fill="url(#{u}-desert)"/>')
    out.append(f'<polygon points="{P([C(-14, 0, 2000), C(14, 0, 2000), C(14, 0, 3), C(-14, 0, 3)])}" fill="url(#{u}-road)"/>')
    out.append(f'<polygon points="{P([C(-1.6, 0.2, 2000), C(1.6, 0.2, 2000), C(1.6, 0.2, 9), C(-1.6, 0.2, 9)])}" fill="#3A3A3A"/>')
    out.append(f'<polygon points="{P([C(-1.4, 0.21, 2000), C(1.4, 0.21, 2000), C(1.4, 0.21, 9), C(-1.4, 0.21, 9)])}" fill="#2E3E30"/>')
    # glowing casino podiums and marquees at street level
    pods = []
    for sgn in (-1, 1):
        z = 46
        while z < 900:
            pods.append((z, sgn, rnd.uniform(14, 26), rnd.uniform(18, 30)))
            z *= rnd.uniform(1.25, 1.45)
    for z, sgn, h, d in sorted(pods, key=lambda t: -t[0]):
        X0 = sgn * 18
        h *= 0.6
        col = rnd.choice(neon)
        out.append(f'<polygon points="{P(C.quad_x(X0, z, z + d, 0, h))}" fill="#221C3A"/>')
        for t, op in ((0.55, 0.95), (0.7, 0.6), (0.85, 0.95)):
            out.append(f'<polygon points="{P(C.quad_x(X0, z, z + d, h * t, h * t + 0.35))}" fill="{col}" opacity="{op}"/>')
        for i in range(6):
            za, zb = z + d * (i + 0.2) / 6, z + d * (i + 0.8) / 6
            out.append(f'<polygon points="{P(C.quad_x(X0, za, zb, 0.3, h * 0.36))}" fill="#FFC870" opacity="0.8"/>')
        # bulb-lit marquee pylon facing the road
        pz = z + d * 0.15
        q = C.quad_z(pz, sgn * 17.2 - 0.9, sgn * 17.2 + 0.9, 2, h * 1.7)
        x0, y0, x1, y1 = q[0][0], q[1][1], q[2][0], q[0][1]
        out.append(f'<rect x="{min(x0, x1):.1f}" y="{y0:.1f}" width="{abs(x1 - x0):.1f}" height="{y1 - y0:.1f}" fill="#1A1426" stroke="{col}" stroke-width="{max(0.6, abs(x1 - x0) * 0.12):.1f}"/>')
        out.append(glow((x0 + x1) / 2, (y0 + y1) / 2, (y1 - y0) * 0.7, col, f"{u}-p{int(z)}{'l' if sgn < 0 else 'r'}", 0.35))
    # street lamps
    for Z in (20, 28, 40, 58, 85, 125, 180):
        for sgn in (-1, 1):
            x0, y0 = C(sgn * 15, 0, Z)
            x1, y1 = C(sgn * 15, 9, Z)
            x2, _ = C(sgn * 12.5, 9, Z)
            sw = max(0.6, C.f * 0.18 / Z)
            out.append(f'<path d="M {x0:.1f} {y0:.1f} L {x1:.1f} {y1:.1f} L {x2:.1f} {y1:.1f}" fill="none" stroke="#1A1424" stroke-width="{sw:.1f}"/>')
            out.append(glow(x2, y1 + 2, C.f * 2.2 / Z, "#FFE2A0", f"{u}-l{Z}{sgn + 1}", 0.8))
    # long-exposure light trails: tail lights going north on the right, headlights coming south on the left
    for X, col, op in ((3.4, "#FF4A4A", 0.85), (6.4, "#FF6A4A", 0.75), (9.6, "#FF3A5A", 0.6), (12.2, "#FFD0A0", 0.4), (-3.4, "#FFF2C8", 0.9), (-6.4, "#FFE08A", 0.8), (-9.6, "#FFF2C8", 0.6)):
        for dx, w, o in ((0, 0.5, op * 0.35), (0, 0.18, op), (0.6, 0.12, op * 0.7)):
            q = [C(X + dx - w * 0.6, 0.7, 9), C(X + dx + w * 0.6, 0.7, 9), C(X + dx + w, 0.7, 900), C(X + dx - w, 0.7, 900)]
            out.append(f'<polygon points="{P(q)}" fill="{col}" opacity="{o:.2f}"/>')
    # palms along the median and the sidewalks, rim-lit by the neon
    for Z in (22, 30, 42, 60, 85, 120, 170, 240):
        for X, rim in ((0, "#FF8FB8"), (-16, "#FFD25E"), (16, "#58E6F5")):
            if X != 0 and Z < 30:
                continue
            x, b = C(X, 0, Z)
            h = C.f * 12 / Z
            out.append(palm_tree(x, b, h, rim=rim, seed=int(Z * 10 + X), lean=0.06 if X >= 0 else -0.06))
    # foreground: the welcome sign on the median island with its landscaped base
    sx, sb = C(-5.2, 0, 10.5)
    k = C.f / 10.5 / 20
    out.append(f'<ellipse cx="{sx:.1f}" cy="{sb + 4:.1f}" rx="{100 * k:.1f}" ry="{14 * k:.1f}" fill="#2E3A2E"/>')
    out.append(welcome_sign(sx, sb, k, u))
    out.append(grass(60, 81, (sx - 90 * k, sb - 6, sx + 90 * k, sb + 8), ["#3E5A3E", "#5A7A4A", "#2A3A2A"], h=(5, 12)))
    for X, Z, sd in ((-10.5, 12, 3), (14, 13, 5)):
        x, b = C(X, 0, Z)
        out.append(palm_tree(x, b, C.f * 9 / Z, trunk="#24182A", frond="#1A2426", rim="#FFB86A", seed=sd, lean=0.05))
    return "\n".join(out)


# ---------------------------------------------------------------- Chicago (the river at sunset, looking west)
def facade_windows(C, X, z0, z1, y0, y1, fh, bays, col, seed, lit_p=0.35, lit=("#FFD98E", "#F7C873"), mull=None):
    rnd = random.Random(seed)
    out = []
    floors = int((y1 - y0) / fh)
    for f_ in range(floors):
        ya = y0 + f_ * fh + fh * 0.25
        yb = ya + fh * 0.55
        for i in range(bays):
            za = z0 + (z1 - z0) * (i + 0.15) / bays
            zb = z0 + (z1 - z0) * (i + 0.85) / bays
            on = rnd.random() < lit_p
            out.append(f'<polygon points="{P(C.quad_x(X, za, zb, ya, yb))}" fill="{rnd.choice(lit) if on else col}"/>')
    return "".join(out)


# Everything below is built in 3-D with the pinhole Cam (X right = north bank, Y up, Z west up the river) so each
# building is a real box: an east front in cool shade, a river face lit by the low sun (north bank) or by the sky
# (south bank), set-back tiers, cornices, punched windows with reveals, glass curtain walls with sky reflections.
CH_EYE = 16.0
CH_HAZE = "#D9AAA8"


def _chx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def cmix(a, b, t):
    ra, rb = _chx(a), _chx(b)
    return "#" + "".join(f"{max(0, min(255, round(x + (y - x) * t))):02X}" for x, y in zip(ra, rb))


def cscale(c, k):
    return "#" + "".join(f"{max(0, min(255, round(v * k))):02X}" for v in _chx(c))


# light on each kind of face: (tint, amount, brightness)
CH_LIGHT = {"front": ("#3A3C6E", 0.42, 0.62), "xpos": ("#8A82B8", 0.30, 0.84), "xneg": ("#FFBE7A", 0.34, 1.12),
            "top": ("#FFD8A8", 0.25, 1.0), "bottom": ("#2A2A50", 0.5, 0.45)}
# what a glass wall facing each way reflects: (top, middle, bottom)
CH_GLASS = {"front": ("#33426E", "#5A6498", "#9A86AE"), "xpos": ("#55609A", "#A889B0", "#E9AE98"),
            "xneg": ("#FBDDA8", "#F2AE7A", "#B87470"), "top": ("#8A86B0", "#8A86B0", "#8A86B0"),
            "bottom": ("#2A2A40", "#2A2A40", "#2A2A40")}


class ChiScene:
    def __init__(self):
        self.C = Cam(f=470, cx=300, vpy=282, eye=CH_EYE)
        self.n = 0
        self.defs = []

    def gid(self, pre="g"):
        self.n += 1
        return f"ch-{pre}{self.n}"

    def p(self, pts3):
        return P([self.C(*q) for q in pts3])

    def poly(self, pts3, fill, extra=""):
        return f'<polygon points="{self.p(pts3)}" fill="{fill}"{extra}/>'

    def fog(self, Z):
        return min(0.8, max(0.0, 1 - math.exp(-(Z - 140) / 1250)))

    def lit(self, base, kind, Z, extra_fog=0.0):
        tint, amt, k = CH_LIGHT[kind]
        return cmix(cscale(cmix(base, tint, amt), k), CH_HAZE, min(0.85, self.fog(Z) + extra_fog))

    def px(self, Z):
        """pixels per metre at depth Z"""
        return self.C.f / Z


def box_faces(X0, X1, Z0, Z1, Y0, Y1):
    """Visible faces of an axis-aligned box: (kind, quad, map(u, v)->3D, u-range, inward depth vector)."""
    out = [("front", [(X0, Y0, Z0), (X0, Y1, Z0), (X1, Y1, Z0), (X1, Y0, Z0)], lambda u, v, d=0: (u, v, Z0 + d), (X0, X1))]
    if X1 < 0:
        out.append(("xpos", [(X1, Y0, Z0), (X1, Y1, Z0), (X1, Y1, Z1), (X1, Y0, Z1)], lambda u, v, d=0: (X1 - d, v, u), (Z0, Z1)))
    if X0 > 0:
        out.append(("xneg", [(X0, Y0, Z0), (X0, Y1, Z0), (X0, Y1, Z1), (X0, Y0, Z1)], lambda u, v, d=0: (X0 + d, v, u), (Z0, Z1)))
    if Y1 < CH_EYE:
        out.append(("top", [(X0, Y1, Z0), (X1, Y1, Z0), (X1, Y1, Z1), (X0, Y1, Z1)], None, None))
    if Y0 > CH_EYE:
        out.append(("bottom", [(X0, Y0, Z0), (X1, Y0, Z0), (X1, Y0, Z1), (X0, Y0, Z1)], None, None))
    return out


def ch_window(S, kind, fm, a, b, c, d, glass, depth, jamb, soffit, sill, detail):
    """One punched window with depth: opening + the visible jamb, soffit (above eye) or sill (below eye)."""
    out = [S.poly([fm(a, c), fm(a, d), fm(b, d), fm(b, c)], glass)]
    if not detail:
        return "".join(out)
    if kind == "front":
        ju = a if a < 0 else b
    else:
        ju = b
    out.append(S.poly([fm(ju, c), fm(ju, d), fm(ju, d, depth), fm(ju, c, depth)], jamb))
    if d > CH_EYE:
        out.append(S.poly([fm(a, d), fm(b, d), fm(b, d, depth), fm(a, d, depth)], soffit))
    if c < CH_EYE:
        out.append(S.poly([fm(a, c), fm(b, c), fm(b, c, depth), fm(a, c, depth)], sill))
    return "".join(out)


LIT_WIN = ("#FFD995", "#F9C574", "#FFE6B0", "#F4B866")


def ch_tier(S, t, seed):
    """t: dict(X0, X1, Z0, Z1, Y0, Y1, mat, base, fh, bay, lit, cornice, piers)."""
    X0, X1, Z0, Z1, Y0, Y1 = t["X0"], t["X1"], t["Z0"], t["Z1"], t["Y0"], t["Y1"]
    mat, base = t["mat"], t["base"]
    fh, bay = t.get("fh", 4.0), t.get("bay", 3.0)
    rnd = random.Random(seed)
    out = []
    for kind, quad, fm, ur in box_faces(X0, X1, Z0, Z1, Y0, Y1):
        Zm = Z0 if kind == "front" else (Z0 + Z1) / 2
        Zn = Z0                                  # nearest depth of this face (detail level)
        ppm = S.px(Zn)
        col = S.lit(base, kind, Zm)
        if fm is None:
            out.append(S.poly(quad, col))
            continue
        fog = S.fog(Zm)
        if mat in ("glass", "dark"):
            gt, gm, gb = CH_GLASS[kind]
            if mat == "dark":
                gt, gm, gb = (cmix(g, "#151520", 0.72) for g in (gt, gm, gb))
            gt, gm, gb = (cmix(cmix(g, base, 0.25), CH_HAZE, fog) for g in (gt, gm, gb))
            ya = S.C(*quad[1])[1]
            yb = S.C(*quad[0])[1]
            gid = S.gid("gl")
            S.defs.append(lg(gid, [(0, gt), (0.55, gm), (1, gb)], 0, ya, 0, yb, units="userSpaceOnUse"))
            cid = S.gid("cp")
            S.defs.append(f'<clipPath id="{cid}"><polygon points="{S.p(quad)}"/></clipPath>')
            out.append(S.poly(quad, f"url(#{gid})"))
            g = []
            u0, u1 = ur
            # reflections of neighbouring towers: soft vertical slabs in the glass
            for _ in range(rnd.randint(2, 4)):
                ua = rnd.uniform(u0, u1)
                ub = ua + rnd.uniform(0.12, 0.35) * (u1 - u0)
                va = rnd.uniform(Y0, Y0 + (Y1 - Y0) * 0.5)
                rc = cmix(gm, "#1A1E38", 0.45) if rnd.random() < 0.6 else cmix(gm, "#FFE6C0", 0.5)
                g.append(S.poly([fm(ua, Y0), fm(ua, va + (Y1 - Y0) * 0.5), fm(ub, va + (Y1 - Y0) * 0.45), fm(ub, Y0)], rc, f' opacity="{rnd.uniform(0.18, 0.32):.2f}"'))
            # lit panes
            mw = t.get("mull", 3.0)
            nf = int((Y1 - Y0) / fh)
            nb = max(1, int((u1 - u0) / mw))
            for f_ in range(nf):
                for i in range(nb):
                    if rnd.random() < t.get("lit", 0.06):
                        ua, ub = u0 + (u1 - u0) * i / nb, u0 + (u1 - u0) * (i + 1) / nb
                        va = Y0 + f_ * fh
                        g.append(S.poly([fm(ua, va + 0.2 * fh), fm(ua, va + 0.95 * fh), fm(ub, va + 0.95 * fh), fm(ub, va + 0.2 * fh)],
                                        rnd.choice(LIT_WIN), f' opacity="{(0.95 - fog) * rnd.uniform(0.6, 1):.2f}"'))
            # mullions and spandrels
            sw = max(0.45, min(1.3, ppm * 0.16))
            lc = "#141A34" if kind != "xneg" else "#7A4A44"
            if mat == "dark":
                lc = "#B89A7A" if kind == "xneg" else "#6A6478"
            lines = []
            step = mw if ppm * mw > 2.2 else mw * 2 if ppm * mw * 2 > 2.2 else None
            if step:
                k = 1
                u = u0 + step
                while u < u1 - 0.2:
                    a_, b_ = S.C(*fm(u, Y0)), S.C(*fm(u, Y1))
                    lines.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}"/>')
                    u += step
            fstep = fh if ppm * fh > 2.0 else fh * 2 if ppm * fh * 2 > 2.0 else fh * 4
            v = Y0 + fstep
            hl = []
            while v < Y1 - 0.2:
                a_, b_ = S.C(*fm(u0, v)), S.C(*fm(u1, v))
                hl.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}"/>')
                v += fstep
            op = 0.42 * (1 - fog)
            g.append(f'<g stroke="{lc}" stroke-width="{sw:.2f}" opacity="{op:.2f}">' + "".join(lines) + "</g>")
            g.append(f'<g stroke="{lc}" stroke-width="{sw * 1.3:.2f}" opacity="{op * 1.15:.2f}">' + "".join(hl) + "</g>")
            # sun glint / sky sheen running down the glass
            if kind == "xneg":
                g.append(S.poly([fm(u0, Y1), fm(u0 + (u1 - u0) * 0.35, Y1), fm(u0 + (u1 - u0) * 0.12, Y0), fm(u0, Y0)], "#FFF2D0", ' opacity="0.22"'))
            elif kind == "front":
                ua = u0 + (u1 - u0) * rnd.uniform(0.15, 0.6)
                g.append(S.poly([fm(ua, Y1), fm(ua + (u1 - u0) * 0.12, Y1), fm(ua + (u1 - u0) * 0.3, Y0), fm(ua + (u1 - u0) * 0.18, Y0)], "#C8B8E0", ' opacity="0.13"'))
            out.append(f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>")
        else:
            out.append(S.poly(quad, col))
            u0, u1 = ur
            dark = cmix(cscale(col, 0.42), "#1E1E38", 0.3)
            glass_dark = cmix(dark, CH_GLASS[kind][1], 0.35 if kind != "front" else 0.2)
            jamb = cscale(col, 1.12) if kind == "xneg" else cscale(col, 0.82)
            soffit = cscale(col, 0.55)
            sill = cscale(col, 1.18)
            nb = max(1, int(round((u1 - u0 - 1.0) / bay)))
            base_h = t.get("base_h", 5.0)
            nf = int((Y1 - Y0 - base_h - 1.5) / fh)
            winw = t.get("winw", 0.56)
            detail = ppm * bay * winw > 3.2
            depth = 0.45
            piers = t.get("piers")
            if piers and ppm * bay > 2.5:
                # vertical deco piers running between the window bays, a hair proud and catching light
                for i in range(1, nb):
                    u = u0 + 0.5 + (u1 - u0 - 1.0) * i / nb
                    out.append(S.poly([fm(u - 0.25, Y0 + base_h), fm(u - 0.25, Y1 - 1), fm(u + 0.25, Y1 - 1), fm(u + 0.25, Y0 + base_h)],
                                      cscale(col, 1.14 if kind == "xneg" else 1.08)))
            small = ppm * fh * 0.6 < 2.6 or ppm * bay * winw < 2.0
            for f_ in range(nf):
                c = Y0 + base_h + f_ * fh + fh * 0.22
                d = c + fh * 0.6
                if small:
                    # far away: a dark ribbon of glass per floor, lit windows dotted into it
                    out.append(S.poly([fm(u0 + 0.5, c), fm(u0 + 0.5, d), fm(u1 - 0.5, d), fm(u1 - 0.5, c)], glass_dark, ' opacity="0.85"'))
                    for i in range(nb):
                        if rnd.random() < t.get("lit", 0.2):
                            a = u0 + 0.5 + (u1 - u0 - 1.0) * (i + (1 - winw) / 2) / nb
                            b = u0 + 0.5 + (u1 - u0 - 1.0) * (i + (1 + winw) / 2) / nb
                            out.append(S.poly([fm(a, c), fm(a, d), fm(b, d), fm(b, c)], cmix(rnd.choice(LIT_WIN), CH_HAZE, fog * 0.7)))
                    continue
                for i in range(nb):
                    a = u0 + 0.5 + (u1 - u0 - 1.0) * (i + (1 - winw) / 2) / nb
                    b = u0 + 0.5 + (u1 - u0 - 1.0) * (i + (1 + winw) / 2) / nb
                    on = rnd.random() < t.get("lit", 0.2)
                    gcol = rnd.choice(LIT_WIN) if on else glass_dark
                    if on:
                        gcol = cmix(gcol, CH_HAZE, fog * 0.7)
                    out.append(ch_window(S, kind, fm, a, b, c, d, gcol, depth, jamb, soffit, sill, detail))
            # storefront band at the base
            if base_h >= 4 and Y0 < 12:
                out.append(S.poly([fm(u0 + 0.6, Y0 + 0.4), fm(u0 + 0.6, Y0 + base_h * 0.75), fm(u1 - 0.6, Y0 + base_h * 0.75), fm(u1 - 0.6, Y0 + 0.4)],
                                  cmix(dark, "#F7B860", 0.35 if t.get("shop") else 0.05)))
            # weathering: faint vertical wash and a dark foot
            out.append(S.poly([fm(u0, Y0), fm(u0, Y0 + (Y1 - Y0) * 0.25), fm(u1, Y0 + (Y1 - Y0) * 0.25), fm(u1, Y0)], "#1A1830", ' opacity="0.12"'))
        # corner shadow line where two faces meet (gives the edge a crisp turn)
        if kind == "xpos":
            out.append(S.poly([(X1, Y0, Z0), (X1, Y1, Z0), (X1, Y1, Z0 + 0.6), (X1, Y0, Z0 + 0.6)], "#FFE8C8", ' opacity="0.18"'))
        if kind == "xneg":
            out.append(S.poly([(X0, Y0, Z0), (X0, Y1, Z0), (X0, Y1, Z0 + 0.8), (X0, Y0, Z0 + 0.8)], "#FFF4D8", ' opacity="0.45"'))
    # cornice: a proud slab with its shadowed underside
    if t.get("cornice", mat in ("stone", "brick")):
        e = t.get("cornice_d", 0.7)
        hgt = t.get("cornice_h", 1.4)
        ct = dict(X0=X0 - e, X1=X1 + e, Z0=Z0 - e, Z1=Z1 + e, Y0=Y1 - hgt, Y1=Y1)
        for kind, quad, fm, ur in box_faces(ct["X0"], ct["X1"], ct["Z0"], ct["Z1"], ct["Y0"], ct["Y1"]):
            if kind in ("bottom", "top"):
                continue
            out.append(S.poly(quad, S.lit(cscale(base, 1.12), kind, Z0)))
            # a bright lip along the top edge of the moulding
            q = quad
            out.append(S.poly([q[1], q[2], (lambda a, b: tuple(a[i] + (b[i] - a[i]) * 0.3 for i in range(3)))(q[2], q[3]),
                               (lambda a, b: tuple(a[i] + (b[i] - a[i]) * 0.3 for i in range(3)))(q[1], q[0])], "#FFF0D8", ' opacity="0.25"'))
        yb = Y1 - hgt
        if yb > CH_EYE:
            # only the projecting rim of the underside shows, in deep shadow
            out.append(S.poly([(X0 - e, yb, Z0 - e), (X1 + e, yb, Z0 - e), (X1, yb, Z0), (X0, yb, Z0)], "#1E1A30", ' opacity="0.75"'))
            if X1 < 0:
                out.append(S.poly([(X1 + e, yb, Z0 - e), (X1 + e, yb, Z1 + e), (X1, yb, Z1), (X1, yb, Z0)], "#1E1A30", ' opacity="0.75"'))
            if X0 > 0:
                out.append(S.poly([(X0 - e, yb, Z0 - e), (X0 - e, yb, Z1 + e), (X0, yb, Z1), (X0, yb, Z0)], "#3A2A3A", ' opacity="0.6"'))
        # soft cast shadow on the wall just under the cornice
        for kind, quad, fm, ur in box_faces(X0, X1, Z0, Z1, yb - 1.6, yb):
            if fm is not None:
                out.append(S.poly(quad, "#16142A", ' opacity="0.25"'))
    # golden hour: the low sun warms the upper floors more than the street canyon
    return "".join(out)


def ch_building(S, tiers, seed):
    """Tiers bottom -> top; drawn top first because the lower, nearer tier hides the foot of the set-back above it."""
    return "".join(ch_tier(S, t, seed + i * 17) for i, t in reversed(list(enumerate(tiers))))


def ch_cylinder_grad(S, Xc, Zc, R, Y, lit_c, mid_c, dark_c, refl_c, fog, uid):
    """Horizontal gradient that shades a vertical cylinder lit from the left-ahead (the setting sun)."""
    C = S.C
    a0 = math.atan2(-Xc, -Zc)
    D = math.hypot(Xc, Zc)
    lim = math.acos(R / D)
    L = (-math.sin(math.radians(74)), math.cos(math.radians(74)))
    xs, cols = [], []
    for i in range(17):
        th = -lim + 2 * lim * i / 16
        psi = a0 + th
        n = (math.sin(psi), math.cos(psi))
        I = n[0] * L[0] + n[1] * L[1]
        x, _ = C(Xc + R * math.sin(psi), Y, Zc + R * math.cos(psi))
        if I > 0:
            c = cmix(mid_c, lit_c, min(1, I * 1.5) ** 0.6)
        else:
            c = cmix(mid_c, dark_c, min(1, -I * 1.7))
        if th > lim * 0.7:
            c = cmix(c, refl_c, (th - lim * 0.7) / (lim * 0.3) * 0.55)
        xs.append(x)
        cols.append(cmix(c, CH_HAZE, fog))
    x0, x1 = xs[0], xs[-1]
    S.defs.append(lg(uid, [(round((x - x0) / (x1 - x0), 3), c) for x, c in zip(xs, cols)], x0, 0, x1, 0, units="userSpaceOnUse"))
    return x0, x1


def ch_ring(S, Xc, Zc, Y, rfun, n=40):
    """Projected front half of a horizontal ring with radius rfun(psi) at height Y, left to right."""
    a0 = math.atan2(-Xc, -Zc)
    D = math.hypot(Xc, Zc)
    lim = math.acos(17.0 / D)
    pts = []
    for i in range(n + 1):
        th = -lim + 2 * lim * i / n
        psi = a0 + th
        r = rfun(psi)
        pts.append(S.C(Xc + r * math.sin(psi), Y, Zc + r * math.cos(psi)))
    return pts


def ch_corncob(S, Xc, Zc, seed, R=16.5, top=178.0):
    """The twin 'corncob' towers: parking spiral below, scalloped petal balconies above, river marina at the foot."""
    rnd = random.Random(seed)
    fog = S.fog(Zc)
    u = S.gid("cob")
    body = f"{u}b"
    slab = f"{u}s"
    ch_cylinder_grad(S, Xc, Zc, R - 1.2, 100, "#9A7262", "#4A4058", "#242234", "#34304A", fog, body)
    ch_cylinder_grad(S, Xc, Zc, R, 100, "#FFE9C2", "#B9A3AE", "#5C587C", "#7E789E", fog * 0.9, slab)
    out = []
    Ytop = top
    left = ch_ring(S, Xc, Zc, 0, lambda p: R)[0]
    # body silhouette (inner wall)
    ring_b = ch_ring(S, Xc, Zc, 1.0, lambda p: R - 0.6)
    ring_t = ch_ring(S, Xc, Zc, Ytop, lambda p: R - 0.6)
    out.append(f'<polygon points="{P(ring_b + ring_t[::-1])}" fill="url(#{body})"/>')
    # lit windows deep in the apartments
    pet = 16

    def scallop(psi, b=2.4):
        k = pet * psi / (2 * math.pi)
        t = 2 * (k - math.floor(k)) - 1
        return R - 0.6 + b * math.sqrt(max(0.0, 1 - t * t))
    a0 = math.atan2(-Xc, -Zc)
    lim = math.acos(17.0 / math.hypot(Xc, Zc))
    win = []
    for f_ in range(40):
        Y = 62 + f_ * 2.72
        for _ in range(3):
            if rnd.random() < 0.75:
                th = rnd.uniform(-lim * 0.85, lim * 0.85)
                psi = a0 + th
                x, y = S.C(Xc + (R - 0.6) * math.sin(psi), Y + 1.3, Zc + (R - 0.6) * math.cos(psi))
                win.append(f'<rect x="{x - 0.9:.1f}" y="{y - 0.6:.1f}" width="1.8" height="1.3" fill="{rnd.choice(LIT_WIN)}" opacity="{rnd.uniform(0.6, 1):.2f}"/>')
    out.append("".join(win))
    # parking spiral: smooth ramp edges with car fronts peeking out
    cars = []
    bands = []
    for f_ in range(19):
        Y = 4 + f_ * 2.85
        top_e = ch_ring(S, Xc, Zc, Y + 0.75, lambda p: R, n=20)
        bot_e = ch_ring(S, Xc, Zc, Y, lambda p: R - 0.6, n=20)
        bands.append(f'<polygon points="{P(top_e + bot_e[::-1])}"/>')
        for _ in range(4):
            th = rnd.uniform(-lim * 0.9, lim * 0.9)
            psi = a0 + th
            x, y = S.C(Xc + (R - 0.4) * math.sin(psi), Y + 1.6, Zc + (R - 0.4) * math.cos(psi))
            cars.append(f'<rect x="{x - 1.3:.1f}" y="{y - 0.5:.1f}" width="2.6" height="1.3" rx="0.5" fill="{rnd.choice(["#C8473A", "#E8E2D6", "#3E5A7A", "#2A2A30", "#B8B0A0", "#D8A040"])}"/>')
    out.append("".join(cars))
    out.append(f'<g fill="url(#{slab})">' + "".join(bands) + "</g>")
    # mechanical floor: a dark recessed ring with a row of columns
    m = ch_ring(S, Xc, Zc, 58.5, lambda p: R - 2.5)
    m2 = ch_ring(S, Xc, Zc, 61.5, lambda p: R - 2.5)
    out.append(f'<polygon points="{P(m + m2[::-1])}" fill="#26223A" opacity="0.85"/>')
    # 40 floors of petal balconies: each slab edge + its underside seen from below
    slabs = []
    for f_ in range(41):
        Y = 61.5 + f_ * 2.72
        outer = ch_ring(S, Xc, Zc, Y + 0.55, scallop, n=56)
        inner = ch_ring(S, Xc, Zc, Y - 0.15, lambda p: R - 0.6, n=16)
        slabs.append(f'<polygon points="{P(outer + inner[::-1])}"/>')
    out.append(f'<g fill="url(#{slab})">' + "".join(slabs) + "</g>")
    # thin railing line on each balcony (lighter, catches the sun on the left)
    rail = []
    for f_ in range(0, 41):
        Y = 61.5 + f_ * 2.72 + 1.5
        pts = ch_ring(S, Xc, Zc, Y, lambda p: scallop(p, 2.2), n=36)
        rail.append(f'<polyline points="{P(pts)}"/>')
    out.append(f'<g fill="none" stroke="url(#{slab})" stroke-width="0.45" opacity="0.8">' + "".join(rail) + "</g>")
    # roof parapet and the little rooftop house
    rt = ch_ring(S, Xc, Zc, Ytop + 1.6, lambda p: R + 0.3)
    rb = ch_ring(S, Xc, Zc, Ytop - 0.6, lambda p: R + 0.3)
    out.append(f'<polygon points="{P(rt + rb[::-1])}" fill="url(#{slab})"/>')
    # warm rim of sunlight on the left limb
    lt = ch_ring(S, Xc, Zc, Ytop + 1.6, lambda p: R + 0.3)[0]
    lb = ch_ring(S, Xc, Zc, 4, lambda p: R)[0]
    out.append(f'<line x1="{lt[0] + 0.6:.1f}" y1="{lt[1]:.1f}" x2="{lb[0] + 0.6:.1f}" y2="{lb[1]:.1f}" stroke="#FFE2B0" stroke-width="1.1" opacity="0.7"/>')
    # marina at the waterline: dark boat slips under the tower
    mb = ch_ring(S, Xc, Zc, 0.2, lambda p: R + 1)
    mt = ch_ring(S, Xc, Zc, 4.0, lambda p: R + 1)
    out.append(f'<polygon points="{P(mb + mt[::-1])}" fill="#2A2436"/>')
    for i in range(1, 9):
        q = mt[i * 5]
        b = mb[i * 5]
        out.append(f'<line x1="{q[0]:.1f}" y1="{q[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#8A8098" stroke-width="0.8"/>')
    for i in (2, 5, 7):
        b = mb[i * 5 + 2]
        out.append(f'<ellipse cx="{b[0]:.1f}" cy="{b[1] - 0.8:.1f}" rx="2.2" ry="0.9" fill="#F2EEE6"/>')
    return "".join(out)


def ch_willis(S, Zf=1400, Xr=-136):
    """The black bundled-tube tower: 3x3 square tubes stopping at 50/66/90/108 floors, twin antennas on top."""
    w = 22.9
    H = {50: 205, 66: 270, 90: 368, 108: 442}
    grid = [[50, 90, 66], [108, 108, 90], [66, 90, 50]]          # rows north -> south, columns west -> east
    boxes = []
    for r in range(3):
        for c in range(3):
            X1 = Xr - r * w
            Z0 = Zf + (2 - c) * w
            boxes.append((Z0, X1 - w, X1, H[grid[r][c]]))
    out = []
    fog = S.fog(Zf) * 0.75
    for Z0, X0, X1, h in sorted(boxes, key=lambda b: (-b[0], b[2])):
        for kind, quad, fm, ur in box_faces(X0, X1, Z0, Z0 + w, 0, h):
            if kind == "front":
                col = cmix("#23222E", CH_HAZE, fog * 0.8)
            elif kind == "xpos":
                col = cmix("#3A3446", CH_HAZE, fog * 0.85)
            else:
                col = "#000"
            out.append(S.poly(quad, col))
            if fm is not None:
                # black steel mullions and the louvred mechanical bands
                u0, u1 = ur
                ls = []
                for i in range(1, 6):
                    uu = u0 + (u1 - u0) * i / 6
                    a_, b_ = S.C(*fm(uu, 0)), S.C(*fm(uu, h))
                    ls.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}"/>')
                out.append(f'<g stroke="{cmix(col, "#C8A88A", 0.25)}" stroke-width="0.5" opacity="0.6">' + "".join(ls) + "</g>")
                for yb in (118, 262, 362, 434):
                    if yb < h - 2:
                        out.append(S.poly([fm(u0, yb), fm(u0, yb + 6), fm(u1, yb + 6), fm(u1, yb)], cmix(col, "#8A7A8A", 0.35)))
                # warm sunset rim on the sun-side edge
                if kind == "front":
                    a_, b_ = S.C(X0, 0, Z0), S.C(X0, h, Z0)
                    out.append(f'<line x1="{a_[0] + 0.4:.1f}" y1="{a_[1]:.1f}" x2="{b_[0] + 0.4:.1f}" y2="{b_[1]:.1f}" stroke="#FFC890" stroke-width="0.8" opacity="0.65"/>')
        # rooftop edge glint
        a_, b_ = S.C(X0, h, Z0), S.C(X1, h, Z0)
        out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#E8B890" stroke-width="0.7" opacity="0.7"/>')
    # twin antennas on the two tallest tubes
    for X, Z, top in ((Xr - w * 1.25, Zf + w * 0.6, 527), (Xr - w * 1.85, Zf + w * 1.7, 517)):
        a_, b_ = S.C(X, 442, Z), S.C(X, top, Z)
        out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#4A4458" stroke-width="1.7"/>')
        out.append(f'<line x1="{a_[0] - 0.3:.1f}" y1="{a_[1]:.1f}" x2="{b_[0] - 0.3:.1f}" y2="{b_[1]:.1f}" stroke="#F0D8C8" stroke-width="0.6" opacity="0.8"/>')
        out.append(glow(b_[0], b_[1], 6, "#FF5A4A", S.gid("ant"), 0.7) + f'<circle cx="{b_[0]:.1f}" cy="{b_[1]:.1f}" r="1.3" fill="#FF6A5A"/>')
    return "".join(out)


def ch_bridge(S, Zb, col="#4E5C6E", wide=16, houses=True, people=0, seed=0, cars=1):
    """Bascule bridge crossing the river at depth Zb: deck truss with an arched bottom chord, railings, lamps,
    road deck seen from above, and stone bridge-tender houses with hipped roofs on both banks."""
    rnd = random.Random(seed)
    C = S.C
    fog = S.fog(Zb)
    XL, XR = -42.0, 30.0
    Xm = (XL + XR) / 2
    half = (XR - XL) / 2
    out = []
    girder = cmix(cscale(col, 0.78), CH_HAZE, fog)
    lit_edge = cmix("#FFD2A0", CH_HAZE, fog * 0.6)
    # shadow on the water under the bridge
    out.append(S.poly([(XL + 12, 0, Zb), (XR, 0, Zb), (XR, 0, Zb + wide), (XL + 12, 0, Zb + wide)], "#141A2C", ' opacity="0.35"'))
    # road deck (seen from above) with sidewalks and lane dashes
    deck = [(XL, 8.4, Zb), (XR, 8.4, Zb), (XR, 8.4, Zb + wide), (XL, 8.4, Zb + wide)]
    out.append(S.poly(deck, cmix("#6A5E66", CH_HAZE, fog)))
    out.append(S.poly([(XL, 8.45, Zb), (XR, 8.45, Zb), (XR, 8.45, Zb + 2.5), (XL, 8.45, Zb + 2.5)], cmix("#A89290", CH_HAZE, fog)))
    out.append(S.poly([(XL, 8.45, Zb + wide - 2.5), (XR, 8.45, Zb + wide - 2.5), (XR, 8.45, Zb + wide), (XL, 8.45, Zb + wide)], cmix("#A89290", CH_HAZE, fog)))
    # cars on the deck
    for i in range(cars):
        X = rnd.uniform(XL + 8, XR - 8)
        Zc = Zb + rnd.choice((5.5, 9.5))
        cc = rnd.choice(["#C8473A", "#E8E2D6", "#2E4A6A", "#D8A040", "#3A3A44"])
        out.append(S.poly([(X - 2.2, 8.4, Zc), (X + 2.2, 8.4, Zc), (X + 2.2, 9.9, Zc), (X - 2.2, 9.9, Zc)], cmix(cc, "#2A2840", 0.35)))
        out.append(S.poly([(X - 1.5, 9.9, Zc + 0.6), (X + 1.5, 9.9, Zc + 0.6), (X + 1.2, 10.8, Zc + 1.2), (X - 1.2, 10.8, Zc + 1.2)], cmix(cc, "#2A2840", 0.15)))
        for sx in (-1.6, 1.6):
            hx, hy = C(X + sx, 9.2, Zc)
            out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{max(0.6, S.px(Zc) * 0.25):.1f}" fill="#FFF0C8"/>')
    # front girder: Warren truss between a straight top chord and an arched bottom chord
    n = 24
    top = [(XL + (XR - XL) * i / n, 8.4, Zb) for i in range(n + 1)]
    bot = [(x, 4.0 + 2.6 * (1 - ((x - Xm) / half) ** 2), Zb) for x, _, _ in top]
    out.append(S.poly(top + bot[::-1], girder))
    sw = max(0.5, S.px(Zb) * 0.32)
    tr = []
    for i in range(n):
        a = bot[i] if i % 2 == 0 else top[i]
        b = top[i + 1] if i % 2 == 0 else bot[i + 1]
        pa, pb = C(*a), C(*b)
        tr.append(f'<line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}"/>')
    # panels between the diagonals read as dark openings
    out.append(f'<g stroke="{cmix(col, CH_HAZE, fog)}" stroke-width="{sw:.2f}">' + "".join(tr) + "</g>")
    out.append(f'<polyline points="{P([C(*q) for q in bot])}" fill="none" stroke="{cmix(cscale(col, 0.6), CH_HAZE, fog)}" stroke-width="{sw * 1.6:.2f}"/>')
    tp = [C(x, 8.4, Zb) for x, _, _ in top]
    out.append(f'<polyline points="{P(tp)}" fill="none" stroke="{lit_edge}" stroke-width="{sw * 1.2:.2f}"/>')
    # seam where the two leaves meet
    a_, b_ = C(Xm, 8.4, Zb), C(Xm, 6.6, Zb)
    out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#1A1A28" stroke-width="{sw * 0.8:.2f}"/>')
    # railing along the near edge
    rl = [C(x, 9.6, Zb) for x, _, _ in top]
    out.append(f'<polyline points="{P(rl)}" fill="none" stroke="{cmix("#3A3C4E", CH_HAZE, fog)}" stroke-width="{sw * 0.8:.2f}"/>')
    out.append('<g stroke="{}" stroke-width="{:.2f}">'.format(cmix("#3A3C4E", CH_HAZE, fog), sw * 0.45) + "".join(
        f'<line x1="{C(XL + (XR - XL) * i / 48, 8.4, Zb)[0]:.1f}" y1="{C(XL, 8.4, Zb)[1]:.1f}" x2="{C(XL + (XR - XL) * i / 48, 9.6, Zb)[0]:.1f}" y2="{C(XL, 9.6, Zb)[1]:.1f}"/>' for i in range(49)) + "</g>")
    # people strolling across
    pp = []
    for i in range(people):
        X = rnd.uniform(XL + 4, XR - 4)
        x, y = C(X, 8.45, Zb + 1.2)
        pp.append(ch_mini(x, y, S.px(Zb + 1.2) * rnd.uniform(1.6, 1.8), seed * 13 + i))
    out.append("".join(pp))
    # ornamental lamps on the railing
    for X in (XL + 10, Xm, XR - 10):
        a_, b_ = C(X, 9.6, Zb), C(X, 13.2, Zb)
        out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#2A2836" stroke-width="{max(0.5, sw * 0.6):.2f}"/>')
        out.append(glow(b_[0], b_[1], S.px(Zb) * 2.0, "#FFE2A0", S.gid("bl"), 0.8))
        out.append(f'<circle cx="{b_[0]:.1f}" cy="{b_[1]:.1f}" r="{max(0.7, S.px(Zb) * 0.35):.1f}" fill="#FFF2CC"/>')
    # bridge-tender houses
    if houses:
        for X0, X1 in ((-50.0, -42.0), (30.0, 38.0)):
            out.append(ch_bridgehouse(S, X0, X1, Zb - 1, Zb + 7, 2.0 if X0 < 0 else 1.5, 15.5, seed + int(X0)))
    return "".join(out)


def ch_bridgehouse(S, X0, X1, Z0, Z1, Y0, Y1, seed):
    out = [ch_building(S, [dict(X0=X0, X1=X1, Z0=Z0, Z1=Z1, Y0=Y0, Y1=Y1, mat="stone", base="#D9C8AA", fh=3.6, bay=2.6, base_h=2.5,
                                lit=0.6, cornice=True, cornice_d=0.45, cornice_h=0.8)], seed)]
    # hipped roof: four slopes to a ridge, copper gone green
    cx, cz = (X0 + X1) / 2, (Z0 + Z1) / 2
    e = 0.5
    a, b, c, d = (X0 - e, Y1, Z0 - e), (X1 + e, Y1, Z0 - e), (X1 + e, Y1, Z1 + e), (X0 - e, Y1, Z1 + e)
    r1, r2 = (cx, Y1 + 3.6, cz - 1.2), (cx, Y1 + 3.6, cz + 1.2)
    fog = S.fog(Z0)
    roof = "#5E8A7A"
    if X1 < 0:
        out.append(S.poly([b, c, r2, r1], cmix(cscale(roof, 0.95), CH_HAZE, fog)))
    else:
        out.append(S.poly([d, a, r1, r2], cmix(cscale(roof, 1.25), CH_HAZE, fog)))
    out.append(S.poly([a, b, r1], cmix(cscale(roof, 0.7), CH_HAZE, fog)))
    fx, fy = S.C(cx, Y1 + 3.6, cz - 1.2)
    _, fy2 = S.C(cx, Y1 + 5.4, cz - 1.2)
    out.append(f'<line x1="{fx:.1f}" y1="{fy:.1f}" x2="{fx:.1f}" y2="{fy2:.1f}" stroke="#3A4A44" stroke-width="{max(0.6, S.px(Z0) * 0.25):.1f}"/>')
    return "".join(out)


def ch_tree(x, by, h, seed, lit="#C8C070", mid="#6E8A4A", dark="#3A5236"):
    """Riverwalk honey-locust: trunk + canopy of many leaf clumps, lit on the sun side (left)."""
    rnd = random.Random(seed)
    out = [f'<path d="M {x - h * 0.03:.1f} {by:.1f} L {x - h * 0.015:.1f} {by - h * 0.55:.1f} L {x + h * 0.02:.1f} {by - h * 0.55:.1f} L {x + h * 0.03:.1f} {by:.1f} Z" fill="#2E2428"/>']
    cy = by - h * 0.68
    rx, ry = h * 0.36, h * 0.3
    for layer, col, n, dx, dy, sc in ((0, dark, 16, 0.08, 0.06, 1.0), (1, mid, 12, -0.04, -0.05, 0.8), (2, lit, 8, -0.14, -0.14, 0.55)):
        for _ in range(n):
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.uniform(0, 0.75) ** 0.8
            px_ = x + rx * sc * d * math.cos(a) + rx * dx * 2
            py_ = cy + ry * sc * d * math.sin(a) + ry * dy * 2
            r = h * rnd.uniform(0.08, 0.14) * (1.1 - 0.2 * layer)
            out.append(f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="{r:.1f}" fill="{col}"/>')
    return "".join(out)


def ch_boat(S, Xc, Zs, seed):
    """Architecture tour boat heading upriver: stern toward us, starboard side in sky light, open top deck full of
    passengers seen from behind, glass cabin, city flag at the stern."""
    from figures import person
    C = S.C
    rnd = random.Random(seed)
    Wd, Ln = 4.2, 30.0
    X0, X1 = Xc - Wd, Xc + Wd
    out = []
    # wake: pale churned water straight behind the stern, two thin diverging arms, flecks of foam
    wash = [C(Xc - Wd * 0.8, 0, Zs), C(Xc + Wd * 0.8, 0, Zs), C(Xc + Wd * 1.9, 0, Zs - 24), C(Xc - Wd * 1.9, 0, Zs - 24)]
    gid = S.gid("wash")
    S.defs.append(lg(gid, [(0, "#E8E0F0", 0.38), (1, "#B8B4D8", 0.0)], 0, wash[0][1], 0, wash[2][1], units="userSpaceOnUse"))
    out.append(f'<polygon points="{P(wash)}" fill="url(#{gid})"/>')
    for s_ in (-1, 1):
        for j in range(34):
            t = j / 33
            Z = Zs - 0.5 - t * 25
            X = Xc + s_ * (Wd * 0.95 + t * 10.5)
            if rnd.random() < 0.18:
                continue
            x, y = C(X, 0, Z)
            w = S.px(Z) * rnd.uniform(0.7, 1.5)
            out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w:.1f}" ry="{max(0.45, S.px(Z) * 0.09):.2f}" fill="#FFF6E8" opacity="{0.85 - t * 0.55:.2f}"/>')
    for j in range(46):
        t = rnd.random() ** 0.7
        Z = Zs - 0.5 - t * 22
        X = Xc + rnd.uniform(-1, 1) * Wd * (0.7 + t * 1.1)
        x, y = C(X, 0, Z)
        w = S.px(Z) * rnd.uniform(0.3, 1.0)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w:.1f}" ry="{max(0.4, S.px(Z) * 0.07):.2f}" fill="#FFF6E8" opacity="{(0.8 - t * 0.6):.2f}"/>')
    # reflection of the white hull broken on the water
    out.append(ch_reflect(S, [(X0, 0, Zs), (X0, 2.2, Zs), (X1, 2.2, Zs), (X1, 0, Zs)], "#E8E2EE", seed + 3, 0.35))
    # hull: starboard side (catching the sky), stern transom with a navy boot stripe
    bow = Zs + Ln
    side = [(X1, 0, Zs), (X1, 2.3, Zs), (X1, 2.3, bow - 7), (Xc + 0.8, 2.6, bow), (Xc + 0.8, 0.4, bow - 2), (X1 - 0.6, 0, bow - 8)]
    out.append(S.poly(side, "#D8D4E0"))
    out.append(S.poly([(X1, 0, Zs), (X1, 0.8, Zs), (X1, 0.8, bow - 6), (Xc + 0.8, 1.0, bow - 1.2), (Xc + 0.8, 0.4, bow - 2), (X1 - 0.6, 0, bow - 8)], "#24385A"))
    out.append(S.poly([(X1, 2.0, Zs), (X1, 2.3, Zs), (X1, 2.3, bow - 7), (Xc + 0.8, 2.6, bow), (Xc + 0.8, 2.3, bow)], "#F6F2EC"))
    stern = [(X0 + 0.3, 0, Zs), (X0, 2.3, Zs), (X1, 2.3, Zs), (X1 - 0.3, 0, Zs)]
    out.append(S.poly(stern, "#C9C2CC"))
    out.append(S.poly([(X0 + 0.3, 0, Zs), (X0 + 0.15, 0.8, Zs), (X1 - 0.15, 0.8, Zs), (X1 - 0.3, 0, Zs)], "#24385A"))
    out.append(S.poly([(X0 + 0.12, 1.0, Zs), (X0 + 0.1, 1.2, Zs), (X1 - 0.1, 1.2, Zs), (X1 - 0.12, 1.0, Zs)], "#C8473A"))
    # main deck at the stern seen from above, with its rail
    deck = [(X0, 2.3, Zs), (X1, 2.3, Zs), (X1, 2.3, Zs + 3), (X0, 2.3, Zs + 3)]
    out.append(S.poly(deck, "#9A8A88"))
    # enclosed cabin: warm lit windows all along, a door at the back
    cab = dict(X0=X0 + 0.3, X1=X1 - 0.3, Z0=Zs + 2.6, Z1=bow - 7, Y0=2.3, Y1=4.7)
    for kind, quad, fm, ur in box_faces(cab["X0"], cab["X1"], cab["Z0"], cab["Z1"], cab["Y0"], cab["Y1"]):
        if kind == "top":
            continue
        out.append(S.poly(quad, "#ECE8E2" if kind != "front" else "#B8B0B8"))
        u0, u1 = ur
        if kind == "front":
            for a_, b_ in ((u0 + 0.5, u0 + 3.0), (u1 - 3.0, u1 - 0.5)):
                out.append(S.poly([fm(a_, 3.0), fm(a_, 4.3), fm(b_, 4.3), fm(b_, 3.0)], "#F6C47A"))
            out.append(S.poly([fm(Xc - 0.7, 2.3), fm(Xc - 0.7, 4.3), fm(Xc + 0.7, 4.3), fm(Xc + 0.7, 2.3)], "#6A5A66"))
        else:
            n = 9
            for i in range(n):
                a_ = u0 + 0.5 + (u1 - u0 - 1) * i / n
                b_ = a_ + (u1 - u0 - 1) / n * 0.82
                out.append(S.poly([fm(a_, 3.0), fm(a_, 4.3), fm(b_, 4.3), fm(b_, 3.0)], "#F2BE78" if i % 3 else "#8AA0BC"))
    for i in range(7):
        X = X0 + 0.2 + (X1 - X0 - 0.4) * i / 6
        a_, b_ = C(X, 2.3, Zs + 0.2), C(X, 3.3, Zs + 0.2)
        out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#F4EFE6" stroke-width="{S.px(Zs) * 0.07:.2f}"/>')
    rp = [C(X0 + 0.2, 3.3, Zs + 2.6), C(X0 + 0.2, 3.3, Zs + 0.2), C(X1 - 0.2, 3.3, Zs + 0.2), C(X1 - 0.2, 3.3, Zs + 2.6)]
    out.append(f'<polyline points="{P(rp)}" fill="none" stroke="#F4EFE6" stroke-width="{S.px(Zs) * 0.1:.2f}"/>')
    # open top deck: rows of passengers, the pilot house up front, white rail around
    top = [(cab["X0"], 4.7, cab["Z0"]), (cab["X1"], 4.7, cab["Z0"]), (cab["X1"], 4.7, cab["Z1"]), (cab["X0"], 4.7, cab["Z1"])]
    out.append(S.poly(top, "#7E7076"))
    out.append(S.poly([(cab["X0"], 4.7, cab["Z0"]), (cab["X1"], 4.7, cab["Z0"]), (cab["X1"], 4.4, cab["Z0"]), (cab["X0"], 4.4, cab["Z0"])], "#24385A"))
    ph = dict(X0=Xc - 2.4, X1=Xc + 2.4, Z0=cab["Z1"] - 4, Z1=cab["Z1"], Y0=4.7, Y1=6.9)
    for kind, quad, fm, ur in box_faces(ph["X0"], ph["X1"], ph["Z0"], ph["Z1"], ph["Y0"], ph["Y1"]):
        out.append(S.poly(quad, {"front": "#C8C0C6", "top": "#F2EEE8"}.get(kind, "#E8E4DE")))
        if fm is not None and kind == "front":
            out.append(S.poly([fm(ph["X0"] + 0.4, 5.6), fm(ph["X0"] + 0.4, 6.5), fm(ph["X1"] - 0.4, 6.5), fm(ph["X1"] - 0.4, 5.6)], "#3A4A66"))
    pas = []
    rows = []
    Z = ph["Z0"] - 1.0
    while Z > cab["Z0"] + 1.6:
        rows.append(Z)
        Z -= 1.9
    for j, Z in enumerate(rows):
        for i in range(5):
            X = cab["X0"] + 0.9 + i * (cab["X1"] - cab["X0"] - 1.8) / 4 + rnd.uniform(-0.15, 0.15)
            if rnd.random() < 0.15:
                continue
            x, y = C(X, 4.7, Z)
            pas.append(ch_seated(x, y, S.px(Z) * 1.0, seed * 7 + j * 11 + i))
    out.append("".join(pas))
    # a guide at the aft rail of the top deck, a visitor taking it all in
    x, y = C(Xc - 2.0, 4.7, cab["Z0"] + 0.6)
    out.append(person(x, y, S.px(cab["Z0"]) * 1.75, "stand_back", 1, {"top_kind": "jacket", "top": "#2E4A6A"}, 31, rim="#FFD0A0", light=-1, shadow=0))
    x, y = C(Xc + 2.2, 4.7, cab["Z0"] + 0.5)
    out.append(person(x, y, S.px(cab["Z0"]) * 1.66, "stand_back", -1, None, 47, rim="#FFD0A0", light=-1, shadow=0))
    rp = [C(cab["X0"], 5.7, cab["Z1"]), C(cab["X0"], 5.7, cab["Z0"]), C(cab["X1"], 5.7, cab["Z0"]), C(cab["X1"], 5.7, cab["Z1"])]
    out.append(f'<polyline points="{P(rp)}" fill="none" stroke="#F4EFE6" stroke-width="{S.px(Zs) * 0.12:.2f}"/>')
    for X in [cab["X0"] + (cab["X1"] - cab["X0"]) * i / 8 for i in range(9)]:
        a_, b_ = C(X, 4.7, cab["Z0"]), C(X, 5.7, cab["Z0"])
        out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#F4EFE6" stroke-width="{S.px(Zs) * 0.08:.2f}"/>')
    # Chicago city flag on the stern staff: white, two light-blue bars, four red six-pointed stars
    fx, fy = C(X0 + 0.4, 2.3, Zs + 0.3)
    _, ft = C(X0 + 0.4, 6.6, Zs + 0.3)
    k = S.px(Zs)
    out.append(f'<line x1="{fx:.1f}" y1="{fy:.1f}" x2="{fx:.1f}" y2="{ft:.1f}" stroke="#3A3440" stroke-width="{k * 0.1:.2f}"/>')
    fw, fh_ = k * 1.7, k * 1.1
    out.append(f'<g transform="translate({fx:.1f} {ft:.1f}) skewY(8)"><rect width="{fw:.1f}" height="{fh_:.1f}" fill="#FBF6EE"/>'
               f'<rect y="{fh_ * 0.18:.1f}" width="{fw:.1f}" height="{fh_ * 0.14:.1f}" fill="#7EC4E8"/><rect y="{fh_ * 0.68:.1f}" width="{fw:.1f}" height="{fh_ * 0.14:.1f}" fill="#7EC4E8"/>'
               + "".join(f'<circle cx="{fw * (0.2 + 0.2 * i):.1f}" cy="{fh_ * 0.5:.1f}" r="{fh_ * 0.08:.2f}" fill="#D8263A"/>' for i in range(4)) + "</g>")
    return "".join(out)


def ch_reflect(S, pts3, col, seed, op=0.4, yclip=None):
    """Painterly reflection of a face on the water: the mirrored (Y -> -Y) projection broken into horizontal
    brush strokes with ragged ends, fading with depth below the waterline."""
    rnd = random.Random(seed)
    poly = [S.C(X, -Y, Z) for X, Y, Z in pts3]
    ys = [y for _, y in poly]
    y0, y1 = min(ys), min(max(ys), 444)
    out = []
    y = y0
    while y < y1:
        xs = []
        for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
            if (ay <= y < by) or (by <= y < ay):
                xs.append(ax + (bx - ax) * (y - ay) / (by - ay))
        h = rnd.uniform(0.9, 2.2)
        if len(xs) >= 2:
            a, b = min(xs), max(xs)
            w = b - a
            a += rnd.uniform(-0.08, 0.12) * w
            b += rnd.uniform(-0.12, 0.08) * w
            t = (y - y0) / max(1, (y1 - y0))
            if b > a:
                # each row broken into a few dabs with gaps, like light on moving water
                x = a
                o = op * (1 - 0.55 * t)
                while x < b:
                    L_ = min(b - x, rnd.uniform(0.15, 0.6) * w + 2)
                    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{L_:.1f}" height="{h:.1f}" rx="{h / 2:.1f}" fill="{col}" opacity="{o * rnd.uniform(0.55, 1):.2f}"/>')
                    x += L_ + rnd.uniform(0.04, 0.2) * w + 1
        y += h + rnd.uniform(1.0, 2.6)
    return "".join(out)


def ch_mini(x, by, h, seed, rim="#FFD6A0"):
    """Far-off pedestrian a few pixels tall: legs mid-stride, coat, head; rim light on the sun side."""
    rnd = random.Random(seed)
    top = rnd.choice(["#C8573E", "#E3A43E", "#3E6A8A", "#4A7A5A", "#F2E6D0", "#B85A7A", "#2E3A58", "#7A5A9A", "#4E9AA2", "#F0D46A"])
    leg = rnd.choice(["#2E3A58", "#26242C", "#4A4038", "#3E5274"])
    k = h / 10
    st = rnd.uniform(0.6, 1.3)
    return (f'<g transform="translate({x:.1f} {by:.1f}) scale({k:.3f})">'
            f'<path d="M -0.6 -4.8 L {-st:.1f} 0 M 0.6 -4.8 L {st:.1f} 0" stroke="{leg}" stroke-width="1.1" stroke-linecap="round"/>'
            f'<path d="M -1.5 -4.4 L -1.4 -7.9 Q 0 -8.6 1.4 -7.9 L 1.5 -4.4 Z" fill="{top}"/>'
            f'<path d="M -1.5 -4.4 L -1.4 -7.9 L -0.9 -8.2" fill="none" stroke="{rim}" stroke-width="0.5"/>'
            f'<circle cx="0" cy="-9.2" r="0.95" fill="{rnd.choice(["#3A2A22", "#1C1412", "#6E4426", "#C8964E"])}"/></g>')


def ch_compact(svg):
    """Merge groups of plain <line> strokes into one path each (same look, a fraction of the bytes)."""
    import re

    def rep(m):
        segs = re.findall(r'<line x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)"/>', m.group(2))
        d = "".join(f"M{a} {b}L{c} {e}" for a, b, c, e in segs)
        return f'<path d="{d}" fill="none" {m.group(1)}/>'
    return re.sub(r'<g ([^>]*)>((?:<line x1="[^"]+" y1="[^"]+" x2="[^"]+" y2="[^"]+"/>)+)</g>', rep, svg)


def ch_seated(x, y, h, seed):
    """Tiny passenger seen from behind on a bench: shoulders, back, head with hair, rim-lit on the sun side."""
    rnd = random.Random(seed)
    top = rnd.choice(["#C8573E", "#E3A43E", "#3E6A8A", "#4A7A5A", "#F2E6D0", "#B85A7A", "#2E3A58", "#7A5A9A", "#E07A5A", "#4E9AA2", "#F0D46A", "#5A8AC0"])
    hair = rnd.choice(["#1C1412", "#2E1E16", "#4A2E1E", "#6E4426", "#9A6634", "#C8964E", "#B8B0A6"])
    k = h / 10
    sh = cmix(top, "#24183A", 0.35)
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})">'
            '<path d="M -4.6 0 L -4.4 -5.6 Q -4 -7.6 -1.6 -7.9 L 1.6 -7.9 Q 4 -7.6 4.4 -5.6 L 4.6 0 Z" fill="#FFD6A0"/>'
            f'<path d="M -4.2 0.2 L -4.0 -5.4 Q -3.6 -7.3 -1.4 -7.6 L 1.6 -7.6 Q 3.8 -7.3 4.2 -5.4 L 4.4 0.2 Z" fill="{top}"/>'
            f'<path d="M 0.8 -7.6 L 1.6 -7.6 Q 3.8 -7.3 4.2 -5.4 L 4.4 0.2 L 1.2 0.2 Z" fill="{sh}"/>'
            f'<ellipse cx="0" cy="-10.2" rx="2.5" ry="2.8" fill="{hair}"/>'
            '<path d="M -2.5 -10.4 Q -2.4 -12.6 -0.4 -13" fill="none" stroke="#FFD6A0" stroke-width="0.7"/></g>')


def ch_gull(x, y, s, flap=0.0, rim="#FFE6C0"):
    """Herring gull in flight: grey back, white body, dark wing tips, lit underside."""
    k = s / 20
    w = 9 - 6 * flap
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})">'
            f'<path d="M -20 {w - 6:.1f} Q -10 {-w - 4:.1f} -2 -1 L 2 -1 Q 10 {-w - 4:.1f} 20 {w - 6:.1f} Q 10 {-w + 2:.1f} 2 2 L -2 2 Q -10 {-w + 2:.1f} -20 {w - 6:.1f} Z" fill="#B8B4C4"/>'
            f'<path d="M -20 {w - 6:.1f} Q -17 {w - 9:.1f} -14 {w - 9.5:.1f} L -15 {w - 6.5:.1f} Z M 20 {w - 6:.1f} Q 17 {w - 9:.1f} 14 {w - 9.5:.1f} L 15 {w - 6.5:.1f} Z" fill="#2A2630"/>'
            '<ellipse cx="0" cy="1" rx="2.6" ry="5.5" fill="#F4F0EA"/><circle cx="0" cy="-4.5" r="2" fill="#F4F0EA"/>'
            f'<path d="M -2 2 Q 0 4.5 2 2" fill="none" stroke="{rim}" stroke-width="1.2"/></g>')


def chicago():
    from figures import person
    u = "ch"
    S = ChiScene()
    C = S.C
    out = []
    S.defs.append(lg(f"{u}-sky", [(0, "#2A3A70"), (0.22, "#4A5490"), (0.4, "#8A7AAE"), (0.52, "#D296A0"), (0.6, "#F4B58A"),
                                  (0.635, "#FCD69A"), (0.66, "#FDE5B4"), (1, "#FDE5B4")]))
    S.defs.append(lg(f"{u}-river", [(0, "#FBD9A0"), (0.06, "#F0B88C"), (0.25, "#A48AA4"), (0.6, "#4E5A80"), (1, "#25304E")], 0, 282, 0, 444, units="userSpaceOnUse"))
    S.defs.append(lg(f"{u}-haze", [(0, CH_HAZE, 0), (0.7, "#F8CC9C", 0.55), (1, "#FCD8A4", 0.0)], 0, 200, 0, 296, units="userSpaceOnUse"))
    S.defs.append(lg(f"{u}-walk", [(0, "#8A7470"), (1, "#5A4A50")], 0, 300, 0, 444, units="userSpaceOnUse"))
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    # sun low over the river's end, a big soft glow
    sx, sy = 276, 238
    out.append(glow(sx, sy, 260, "#FFE0A0", f"{u}-sun", 0.85))
    out.append(glow(sx, sy, 70, "#FFF4D8", f"{u}-sun2", 0.9))
    out.append(f'<circle cx="{sx}" cy="{sy}" r="15" fill="#FFE7B0"/><circle cx="{sx}" cy="{sy}" r="12.5" fill="#FFF8E6"/>')
    # long sunset clouds: lavender bodies with golden undersides
    rnd = random.Random(5)
    cl = []
    for cx_, cy_, w_ in ((420, 112, 120), (500, 128, 80), (110, 96, 130), (60, 118, 70), (300, 150, 90), (360, 70, 70), (190, 175, 60), (470, 188, 70)):
        for j in range(4):
            dx = rnd.uniform(-w_ * 0.3, w_ * 0.3)
            ww = w_ * rnd.uniform(0.4, 0.8)
            cl.append(f'<ellipse cx="{cx_ + dx:.0f}" cy="{cy_ + j * 2.2:.1f}" rx="{ww:.0f}" ry="{rnd.uniform(2.5, 4.5):.1f}" fill="#9C88B4" opacity="0.55"/>')
            cl.append(f'<ellipse cx="{cx_ + dx - 6:.0f}" cy="{cy_ + j * 2.2 + 2.6:.1f}" rx="{ww * 0.85:.0f}" ry="1.6" fill="#FFC898" opacity="0.75"/>')
    out.append("".join(cl))
    # far west-side skyline in the haze
    far = []
    rnd = random.Random(9)
    for i in range(26):
        X = rnd.uniform(-600, 600)
        Z = rnd.uniform(1900, 2600)
        w = rnd.uniform(25, 60)
        h = rnd.uniform(30, 150)
        if -260 < X < 120:
            h *= 0.35
        far.append((Z, X, w, h))
    for Z, X, w, h in sorted(far, reverse=True):
        out.append(S.poly([(X - w / 2, 0, Z), (X - w / 2, h, Z), (X + w / 2, h, Z), (X + w / 2, 0, Z)], cmix("#A98EAC", CH_HAZE, 0.35)))
    out.append(ch_willis(S))
    # ---- river, banks and the riverwalk
    out.append(S.poly([(-30, 0, 2400), (30, 0, 2400), (30, 0, 30), (-30, 0, 30)], f"url(#{u}-river)"))
    # mirrored reflections of the banks' faces, cobs and bridges, broken into brush strokes
    rf = []
    rf.append(ch_reflect(S, [(34, 1.5, 40), (34, 38, 40), (34, 38, 112), (34, 1.5, 112)], "#F8DDB4", 1, 0.45))
    rf.append(ch_reflect(S, [(36, 1.5, 126), (36, 64, 126), (36, 64, 205), (36, 1.5, 205)], "#F0B88E", 2, 0.4))
    rf.append(ch_reflect(S, [(36, 1.5, 393), (36, 178, 393), (66, 178, 393), (66, 1.5, 393)], "#D8C4C4", 3, 0.45))
    rf.append(ch_reflect(S, [(40, 1.5, 480), (40, 212, 480), (40, 212, 540), (40, 1.5, 540)], "#2E2C3C", 4, 0.45))
    rf.append(ch_reflect(S, [(-62, 2, 56), (-62, 46, 56), (-62, 46, 150), (-62, 2, 150)], "#8E7C9C", 5, 0.4))
    rf.append(ch_reflect(S, [(-92, 2, 175), (-92, 260, 175), (-92, 260, 240), (-92, 2, 240)], "#6E72A4", 6, 0.4))
    rf.append(ch_reflect(S, [(-64, 2, 255), (-64, 92, 255), (-64, 92, 315), (-64, 2, 315)], "#C8A8A0", 7, 0.4))
    for k, Zb in enumerate((150, 300, 470, 680)):
        rf.append(ch_reflect(S, [(-30, 4.4, Zb), (-30, 9.6, Zb), (30, 9.6, Zb), (30, 4.4, Zb)], "#1E2236", 10 + k, 0.55))
    out.append("".join(rf))
    # reflections and glitter go straight on the water (bridges and boats are drawn over them later)
    refl = []
    # warm column under the sun
    rnd = random.Random(3)
    for i in range(170):
        Z = 46 * (1.025 ** i)
        if Z > 2200:
            break
        x, y = C(0, 0, Z)
        X = (sx - 300) * Z / C.f
        x = 300 + C.f * (X + rnd.uniform(-3.5, 3.5) * (Z / 300) ** 0.25) / Z
        w = max(1.4, C.f * rnd.uniform(1.2, 5) / Z)
        refl.append(f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{max(0.7, C.f * 0.12 / Z):.1f}" rx="0.5" fill="#FFF2C8" opacity="{rnd.uniform(0.45, 0.95):.2f}"/>')
    # the lit north-bank facades stretch golden reflections down the right side of the river
    for i in range(140):
        Z = 46 * (1.03 ** i)
        if Z > 900:
            break
        if i % 3 == 0:
            continue
        X = rnd.uniform(14, 29.5)
        x, y = C(X, 0, Z)
        w = C.f * rnd.uniform(2, 6) / Z
        refl.append(f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{max(0.6, C.f * 0.1 / Z):.1f}" fill="{rnd.choice(["#F6C88E", "#F0B07A", "#FFDCA8"])}" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    # cool ripples on the shaded south side
    for i in range(140):
        Z = 46 * (1.03 ** i)
        if Z > 900:
            break
        X = rnd.uniform(-29.5, 8)
        x, y = C(X, 0, Z)
        w = C.f * rnd.uniform(2, 6) / Z
        refl.append(f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{max(0.6, C.f * 0.1 / Z):.1f}" fill="{rnd.choice(["#7E86B0", "#9A92BA", "#2A3254"])}" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>')
    out.append("".join(refl))
    # north bank: narrow dock walk; south bank: the Riverwalk, its granite wall, Wacker Drive above
    out.append(S.poly([(30, 0, 30), (30, 1.5, 30), (30, 1.5, 2400), (30, 0, 2400)], "#5A4A52"))
    out.append(S.poly([(30, 1.5, 30), (34, 1.5, 30), (34, 1.5, 2400), (30, 1.5, 2400)], "#9A8278"))
    out.append(S.poly([(-30, 0, 30), (-30, 2.0, 30), (-30, 2.0, 2400), (-30, 0, 2400)], "#8A7A82"))
    out.append(S.poly([(-30, 2.0, 30), (-42, 2.0, 30), (-42, 2.0, 2400), (-30, 2.0, 2400)], f"url(#{u}-walk)"))
    out.append(S.poly([(-30, 2.0, 30), (-31, 2.0, 30), (-31, 2.0, 2400), (-30, 2.0, 2400)], "#C8B0A0"))
    out.append(S.poly([(-42, 2.0, 30), (-42, 8.0, 30), (-42, 8.0, 2400), (-42, 2.0, 2400)], "#6E6070"))
    out.append(S.poly([(-42, 8.0, 30), (-62, 8.0, 30), (-62, 8.0, 2400), (-42, 8.0, 2400)], "#5E5058"))
    out.append(S.poly([(-42, 7.2, 30), (-42, 8.4, 30), (-42, 8.4, 2400), (-42, 7.2, 2400)], "#A89090"))
    # granite paving joints and the riverwalk 'rooms': arched cafe openings glowing in the wall under Wacker
    pv = []
    for Z in [30 * 1.045 ** i for i in range(60)]:
        if Z > 700:
            break
        a_, b_ = C(-30.5, 2.0, Z), C(-42, 2.0, Z)
        pv.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}"/>')
    out.append('<g stroke="#4A3A44" stroke-width="0.6" opacity="0.35">' + "".join(pv) + "</g>")
    for Z in (34, 44, 56, 70, 86, 104, 126, 175, 215, 255, 340, 400):
        W_ = 4.6
        arch = [(-42, 2.0, Z), (-42, 4.2, Z)] + [(-42, 4.2 + 2.3 * math.sin(math.pi * i / 10), Z + W_ / 2 - W_ / 2 * math.cos(math.pi * i / 10)) for i in range(11)] + [(-42, 2.0, Z + W_)]
        gid = S.gid("cafe")
        y0_, y1_ = C(-42, 6.5, Z)[1], C(-42, 2.0, Z)[1]
        S.defs.append(lg(gid, [(0, "#FFD890"), (0.6, "#F2A458"), (1, "#B8643A")], 0, y0_, 0, y1_, units="userSpaceOnUse"))
        out.append(S.poly(arch, f"url(#{gid})"))
        # deep reveal on the far side of the opening, and a stone voussoir ring
        out.append(S.poly([(-42, 2.0, Z + W_), (-42, 4.2, Z + W_), (-43.2, 4.2, Z + W_), (-43.2, 2.0, Z + W_)], "#8A6A60"))
        ring = [C(*q) for q in arch[1:-1]]
        out.append(f'<polyline points="{P(ring)}" fill="none" stroke="#A89494" stroke-width="{max(0.6, S.px(Z) * 0.35):.1f}"/>')
        # diners inside, dark against the warm light
        if Z < 140:
            for j, dz in enumerate((1.4, 3.0)):
                x, b = C(-42.6, 2.0, Z + dz)
                hh = S.px(Z + dz) * 1.25
                out.append(f'<path d="M {x - hh * 0.22:.1f} {b:.1f} L {x - hh * 0.2:.1f} {b - hh * 0.62:.1f} Q {x:.1f} {b - hh * 0.75:.1f} {x + hh * 0.2:.1f} {b - hh * 0.62:.1f} L {x + hh * 0.22:.1f} {b:.1f} Z" fill="#5A3A34" opacity="0.8"/>'
                           f'<circle cx="{x:.1f}" cy="{b - hh * 0.86:.1f}" r="{hh * 0.13:.1f}" fill="#5A3A34" opacity="0.8"/>')
        gx, gy = C(-38, 2.0, Z + 2.3)
        out.append(glow(gx, gy, S.px(Z) * 5, "#FFC878", S.gid("cg"), 0.4))
    # cafe tables with cream umbrellas out on the riverwalk
    for Z in (50, 64, 82):
        for dz in (0, 3.2):
            x, b = C(-39.5, 2.0, Z + dz)
            k = S.px(Z + dz)
            out.append(f'<line x1="{x:.1f}" y1="{b:.1f}" x2="{x:.1f}" y2="{b - k * 2.4:.1f}" stroke="#3A2E30" stroke-width="{k * 0.08:.2f}"/>'
                       f'<path d="M {x - k * 1.4:.1f} {b - k * 2.0:.1f} Q {x:.1f} {b - k * 2.9:.1f} {x + k * 1.4:.1f} {b - k * 2.0:.1f} Z" fill="#F2E4CC"/>'
                       f'<path d="M {x:.1f} {b - k * 2.55:.1f} Q {x + k * 0.8:.1f} {b - k * 2.3:.1f} {x + k * 1.4:.1f} {b - k * 2.0:.1f} L {x:.1f} {b - k * 2.0:.1f} Z" fill="#B8A090" opacity="0.6"/>'
                       f'<rect x="{x - k * 0.6:.1f}" y="{b - k * 0.8:.1f}" width="{k * 1.2:.1f}" height="{k * 0.15:.1f}" fill="#3A2E30"/>')
    # ---- buildings and bridges, far to near
    items = []
    # south bank (left), Wacker Drive
    L = [
        (1700, [dict(X0=-150, X1=-40, Z0=1600, Z1=1700, Y0=0, Y1=60, mat="stone", base="#B89A8A", lit=0.3)]),
        (1150, [dict(X0=-170, X1=-62, Z0=1100, Z1=1250, Y0=0, Y1=95, mat="glass", base="#6A7090", lit=0.08),
                dict(X0=-160, X1=-72, Z0=1110, Z1=1240, Y0=95, Y1=120, mat="glass", base="#6A7090", lit=0.08)]),
        (880, [dict(X0=-130, X1=-62, Z0=880, Z1=1000, Y0=8, Y1=70, mat="brick", base="#9A5A48", lit=0.3, bay=4)]),
        (700, [dict(X0=-140, X1=-62, Z0=700, Z1=860, Y0=8, Y1=118, mat="stone", base="#CDB8A0", lit=0.25, bay=4, piers=True)]),
        (560, [dict(X0=-120, X1=-64, Z0=560, Z1=680, Y0=8, Y1=62, mat="brick", base="#8E4E40", lit=0.35, bay=3.5, shop=True)]),
        (440, [dict(X0=-120, X1=-64, Z0=440, Z1=540, Y0=8, Y1=84, mat="stone", base="#E2D6C6", lit=0.22, bay=3.2, piers=True),
               dict(X0=-112, X1=-72, Z0=448, Z1=532, Y0=84, Y1=96, mat="stone", base="#E2D6C6", lit=0.1, bay=3.2, base_h=1.5)]),
        (330, [dict(X0=-112, X1=-64, Z0=330, Z1=420, Y0=8, Y1=66, mat="glass", base="#4E6A8E", lit=0.07, mull=3.0),
               dict(X0=-106, X1=-70, Z0=336, Z1=414, Y0=66, Y1=74, mat="dark", base="#30364A", lit=0.0)]),
    ]
    for Zk, tiers in L:
        items.append((Zk, ch_building(S, tiers, int(Zk))))
    # the domed terra-cotta tower on Wacker
    items.append((255, ch_jewelers(S, -104, -64, 255, 315)))
    items.append((175, ch_building(S, [dict(X0=-160, X1=-92, Z0=175, Z1=240, Y0=8, Y1=150, mat="glass", base="#3E5478", lit=0.05, mull=3.0),
                                       dict(X0=-152, X1=-98, Z0=181, Z1=234, Y0=150, Y1=230, mat="glass", base="#3E5478", lit=0.05, mull=3.0),
                                       dict(X0=-144, X1=-106, Z0=187, Z1=228, Y0=230, Y1=260, mat="glass", base="#3E5478", lit=0.03, mull=3.0)], 175)))
    items.append((56, ch_building(S, [dict(X0=-110, X1=-62, Z0=56, Z1=150, Y0=8, Y1=38, mat="stone", base="#C9B08E", lit=0.45, bay=3.4, fh=4.2, piers=True, shop=True),
                                      dict(X0=-104, X1=-68, Z0=62, Z1=144, Y0=38, Y1=46, mat="stone", base="#C9B08E", lit=0.5, bay=3.4, fh=4.0, base_h=1.0)], 56)))
    # north bank (right)
    R = [
        (1300, [dict(X0=34, X1=160, Z0=1300, Z1=1450, Y0=0, Y1=92, mat="brick", base="#B07860", lit=0.3, bay=5)]),
        (1000, [dict(X0=40, X1=110, Z0=1000, Z1=1150, Y0=0, Y1=130, mat="glass", base="#7A8AA0", lit=0.06)]),
        (760, [dict(X0=36, X1=100, Z0=760, Z1=900, Y0=0, Y1=74, mat="stone", base="#D0B494", lit=0.25, bay=4)]),
        (600, [dict(X0=36, X1=90, Z0=600, Z1=720, Y0=0, Y1=105, mat="glass", base="#5E7E80", lit=0.06)]),
        (480, [dict(X0=40, X1=92, Z0=480, Z1=540, Y0=1.5, Y1=212, mat="dark", base="#24242E", lit=0.04, mull=1.6, fh=3.6)]),
    ]
    for Zk, tiers in R:
        items.append((Zk, ch_building(S, tiers, int(Zk) + 3)))
    items.append((443, ch_corncob(S, 86, 460, 7)))
    items.append((393, ch_corncob(S, 51, 410, 8)))
    items.append((230, ch_building(S, [dict(X0=96, X1=150, Z0=230, Z1=300, Y0=1.5, Y1=170, mat="glass", base="#5A7894", lit=0.05),
                                       dict(X0=102, X1=146, Z0=236, Z1=294, Y0=170, Y1=230, mat="glass", base="#5A7894", lit=0.04),
                                       dict(X0=108, X1=140, Z0=242, Z1=288, Y0=230, Y1=270, mat="glass", base="#5A7894", lit=0.03)], 231)))
    items.append((126, ch_building(S, [dict(X0=36, X1=86, Z0=126, Z1=205, Y0=1.5, Y1=58, mat="glass", base="#6A8098", lit=0.08, fh=3.6),
                                       dict(X0=40, X1=82, Z0=132, Z1=199, Y0=58, Y1=64, mat="dark", base="#3A3A4A", lit=0.0)], 126)))
    items.append((40, ch_building(S, [dict(X0=34, X1=80, Z0=40, Z1=112, Y0=1.5, Y1=34, mat="stone", base="#F2E8DA", lit=0.3, bay=2.6, fh=4.0, piers=True, shop=True),
                                      dict(X0=35.2, X1=78, Z0=43, Z1=109, Y0=34, Y1=39, mat="stone", base="#F2E8DA", lit=0.35, bay=2.6, fh=3.0, base_h=1.2, winw=0.4, cornice_d=0.6, cornice_h=0.9, piers=True)], 40)))
    # bridges
    for k, (Zb, ppl) in enumerate(((150, 5), (300, 3), (470, 2), (680, 0), (900, 0), (1180, 0))):
        items.append((Zb - 0.5, ch_bridge(S, Zb, people=ppl, seed=k + 1, cars=2 if Zb < 700 else 0, houses=Zb < 1000)))
    for Zk, svg in sorted(items, key=lambda t: -t[0]):
        out.append(svg)
    # horizon haze over the far city
    out.append(f'<rect x="0" y="200" width="600" height="96" fill="url(#{u}-haze)"/>')
    # ---- the riverwalk life: trees, lamps, people (near)
    near = []
    for Z in (52, 66, 84, 108, 136):
        x, b = C(-40.2, 2.0, Z)
        near.append((Z, ch_tree(x, b, S.px(Z) * 8.5, int(Z))))
        lx, lb = C(-31.6, 2.0, Z + 8)
        lh = S.px(Z + 8) * 4.2
        near.append((Z + 8, f'<line x1="{lx:.1f}" y1="{lb:.1f}" x2="{lx:.1f}" y2="{lb - lh:.1f}" stroke="#221C26" stroke-width="{max(0.7, lh * 0.035):.1f}"/>'
                     + glow(lx, lb - lh, lh * 0.5, "#FFE2A0", S.gid("lamp"), 0.9) + f'<circle cx="{lx:.1f}" cy="{lb - lh:.1f}" r="{lh * 0.06:.1f}" fill="#FFF4D0"/>'))
    rnd = random.Random(21)
    walkers = [(-34.5, 58, "walk", 1), (-36.0, 62, "walk", 1), (-36.9, 62.4, "walk", 1), (-33.0, 74, "walk", -1), (-38.0, 80, "stand_back", 1), (-35.2, 92, "walk", 1),
               (-31.6, 98, "stand_back", 1), (-37.0, 112, "walk", -1), (-34.0, 124, "walk", 1), (-36.5, 140, "walk", 1), (-33.0, 47.5, "stand", 1)]
    for i, (X, Z, pose, fc) in enumerate(walkers):
        x, b = C(X, 2.0, Z)
        hh = S.px(Z) * rnd.uniform(1.62, 1.8)
        near.append((Z, person(x, b, hh, pose, fc, None, 40 + i * 9, rim="#FFD6A0", light=-1) if hh > 8.5 else ch_mini(x, b, hh, 40 + i * 9)))
    # people on the north-bank dock
    for i, (X, Z) in enumerate(((32.5, 70), (31.8, 96), (32.6, 120))):
        x, b = C(X, 1.5, Z)
        near.append((Z, person(x, b, S.px(Z) * 1.72, "walk", -1, None, 90 + i, rim="#FFD6A0", light=-1) if Z < 90 else ch_mini(x, b, S.px(Z) * 1.72, 90 + i)))
    for Z, svg in sorted(near, key=lambda t: -t[0]):
        out.append(svg)
    # ---- architecture tour boat heading upriver
    out.append(ch_boat(S, -12.0, 70, 4))
    # gulls riding the evening air
    out.append(ch_gull(214, 156, 12, 0.2) + ch_gull(236, 176, 8, 0.7) + ch_gull(420, 214, 8, 0.4) + ch_gull(180, 222, 7, 0.9))
    return ch_compact(defs(*S.defs) + "\n" + "\n".join(out))


def ch_jewelers(S, X0, X1, Z0, Z1):
    """Terra-cotta tower on Wacker with a set-back crown, four corner turrets and a domed temple on top."""
    cx, cz = (X0 + X1) / 2, (Z0 + Z1) / 2
    out = []
    tiers = [dict(X0=X0, X1=X1, Z0=Z0, Z1=Z1, Y0=8, Y1=78, mat="stone", base="#E8D2AE", lit=0.25, bay=3.0, fh=3.8, piers=True),
             dict(X0=X0 + 5, X1=X1 - 5, Z0=Z0 + 5, Z1=Z1 - 5, Y0=78, Y1=92, mat="stone", base="#E8D2AE", lit=0.3, bay=3.0, fh=3.8, base_h=1.0)]
    # dome temple (drawn first: the set-back tiers hide its foot)
    R = 7.0
    fog = S.fog(cz)
    u = S.gid("dome")
    ch_cylinder_grad(S, cx, cz, R, 100, "#FFF0D0", "#D8BC9C", "#8E7A86", "#A08EA0", fog, u)
    ring = lambda Y, r: ch_ring(S, cx, cz, Y, lambda p: r, n=24)
    out.append(f'<polygon points="{P(ring(92, R) + ring(104, R)[::-1])}" fill="url(#{u})"/>')
    # colonnade: dark gaps between columns
    a0 = math.atan2(-cx, -cz)
    for i in range(-3, 4):
        psi = a0 + i * 0.42
        p1 = S.C(cx + R * math.sin(psi), 94, cz + R * math.cos(psi))
        p2 = S.C(cx + R * math.sin(psi), 102, cz + R * math.cos(psi))
        out.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="#4A3A44" stroke-width="{S.px(cz) * 1.4:.1f}" opacity="0.65"/>')
    out.append(f'<polygon points="{P(ring(104, R + 0.8) + ring(105.5, R + 0.8)[::-1])}" fill="url(#{u})"/>')
    # dome: stack of shrinking rings
    dome = []
    for j in range(8):
        a = j / 8 * math.pi / 2
        b = (j + 1) / 8 * math.pi / 2
        dome.append(f'<polygon points="{P(ring(105.5 + R * 0.95 * math.sin(a), R * math.cos(a)) + ring(105.5 + R * 0.95 * math.sin(b), R * math.cos(b))[::-1])}"/>')
    out.append(f'<g fill="url(#{u})">' + "".join(dome) + "</g>")
    lx, ly = S.C(cx, 105.5 + R * 0.95, cz)
    _, ly2 = S.C(cx, 105.5 + R * 0.95 + 4, cz)
    out.append(f'<line x1="{lx:.1f}" y1="{ly:.1f}" x2="{lx:.1f}" y2="{ly2:.1f}" stroke="#D8BC9C" stroke-width="{S.px(cz) * 0.8:.1f}"/>')
    out.append(ch_building(S, tiers, 77))
    # corner turrets on the crown tier with little domes
    for tx, tz in ((X0 + 5, Z0 + 5), (X1 - 5, Z0 + 5)):
        ut = S.gid("tur")
        ch_cylinder_grad(S, tx, tz, 2.0, 98, "#FFF0D0", "#D8BC9C", "#8E7A86", "#A08EA0", fog, ut)
        rr = lambda Y, r: ch_ring(S, tx, tz, Y, lambda p: r, n=12)
        out.append(f'<polygon points="{P(rr(92, 2.0) + rr(99, 2.0)[::-1])}" fill="url(#{ut})"/>')
        out.append(f'<polygon points="{P(rr(99, 2.0) + rr(101.5, 1.2)[::-1] )}" fill="url(#{ut})"/>')
        p = S.C(tx, 103, tz)
        q = S.C(tx, 101.5, tz)
        out.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="#D8BC9C" stroke-width="1"/>')
    return "".join(out)


BUILD = {
    "chicago": (chicago, "CHICAGO", "ILLINOIS · EST. 1837", "#1E2A44", "#F8B860", "#FBEBD4", "#F8CC86"),
    "las-vegas": (las_vegas, "LAS VEGAS", "NEVADA · THE STRIP", "#1A1436", "#FF5FA2", "#FBEBD4", "#58E6F5"),
    "nashville": (nashville, "NASHVILLE", "TENNESSEE · MUSIC CITY", "#16122A", "#FF6FA8", "#FBEBD4", "#FFD25E"),
    "yellowstone": (yellowstone, "YELLOWSTONE", "WYOMING · NATIONAL PARK", "#2B2F44", "#F2A65A", "#FBEBD4", "#F7CF9C"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("places", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
