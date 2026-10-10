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
    out.append(F.couple(132, 409, 44, palette={"top": "#3B4A6B", "season": "any"}, seed=4, gap=30, **vis))
    out.append(F.person(178, 408, 43, "photo", -1, {"top": "#2E3A30", "top_kind": "jacket", "bottom": "#CDBB94", "bottom_kind": "trousers", "hat_kind": "sunhat",
                                                   "hat": "#D8B070", "form": "m"}, seed=7, **vis))
    out.append(F.person(236, 406, 42, "stand_back", 1, {"top": "#5E4A7A", "top_kind": "jacket", "bottom": "#2E3A58", "bottom_kind": "trousers", "form": "f",
                                                      "hair_style": "ponytail"}, seed=11, **vis))
    out.append(F.person(253, 406, 27, "child_back", 1, {"top": "#E0A040", "top_kind": "jacket", "bottom": "#3E5274", "bottom_kind": "trousers"}, seed=12, **vis))
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


# Everything below is built in 3-D with the pinhole Cam (X right = north bank, Y up from the water, Z west up the
# river). The camera stands on the south sidewalk of the Michigan Avenue bridge (X = CH_XC, eye CH_EYE above the
# water), so the Riverwalk and its people come close on the left. Every building is a real volume: an east front in
# cool shade, a river face lit by the low sun (north bank) or by the sky (south bank), each painted in its own
# material (cream limestone with proud piers, red-brown brick with punched windows, glazed white terra cotta,
# curtain-wall glass that mirrors the sunset and the city across the water), set-back tiers, cornices, roofs.
CH_EYE = 12.0
CH_XC = -12.0
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
CH_LIGHT = {"front": ("#3A3C6E", 0.40, 0.66), "xpos": ("#8A82B8", 0.28, 0.86), "xneg": ("#FFBE7A", 0.30, 1.10),
            "top": ("#FFD8A8", 0.25, 1.0), "bottom": ("#2A2A50", 0.5, 0.45)}
# what a glass wall facing each way reflects: (top, middle, bottom)
CH_GLASS = {"front": ("#2E3C68", "#525C92", "#8A7AA6"), "xpos": ("#55609A", "#A889B0", "#E9AE98"),
            "xneg": ("#FBDDA8", "#E8A27A", "#9A6A78"), "top": ("#8A86B0", "#8A86B0", "#8A86B0"),
            "bottom": ("#2A2A40", "#2A2A40", "#2A2A40")}
LIT_WIN = ("#FFD995", "#F9C574", "#FFE6B0", "#F4B866", "#FFCF8A")


class ChiScene:
    def __init__(self):
        self.f = 470.0
        self.cam = Cam(f=self.f, cx=300, vpy=282, eye=CH_EYE)
        self.n = 0
        self.defs = []
        self.refl = []          # (Z, pts3, colour, lit-window flecks) gathered while the city is built

    def C(self, X, Y, Z):
        return self.cam(X - CH_XC, Y, Z)

    def gid(self, pre="g"):
        self.n += 1
        return f"ch-{pre}{self.n}"

    def p(self, pts3):
        return P([self.C(*q) for q in pts3])

    def poly(self, pts3, fill, extra=""):
        return f'<path d="{d_rel([self.C(*q) for q in pts3])}" fill="{fill}"{extra}/>'

    def fog(self, Z):
        return min(0.8, max(0.0, 1 - math.exp(-(Z - 160) / 1250)))

    def lit(self, base, kind, Z, extra_fog=0.0):
        tint, amt, k = CH_LIGHT[kind]
        return cmix(cscale(cmix(base, tint, amt), k), CH_HAZE, min(0.85, self.fog(Z) + extra_fog))

    def px(self, Z):
        """pixels per metre at depth Z"""
        return self.f / Z


def box_faces(X0, X1, Z0, Z1, Y0, Y1):
    """Visible faces of an axis-aligned box: (kind, quad, map(u, v, depth)->3D, u-range)."""
    out = [("front", [(X0, Y0, Z0), (X0, Y1, Z0), (X1, Y1, Z0), (X1, Y0, Z0)], lambda u, v, d=0: (u, v, Z0 + d), (X0, X1))]
    if X1 < CH_XC:
        out.append(("xpos", [(X1, Y0, Z0), (X1, Y1, Z0), (X1, Y1, Z1), (X1, Y0, Z1)], lambda u, v, d=0: (X1 - d, v, u), (Z0, Z1)))
    if X0 > CH_XC:
        out.append(("xneg", [(X0, Y0, Z0), (X0, Y1, Z0), (X0, Y1, Z1), (X0, Y0, Z1)], lambda u, v, d=0: (X0 + d, v, u), (Z0, Z1)))
    if Y1 < CH_EYE:
        out.append(("top", [(X0, Y1, Z0), (X1, Y1, Z0), (X1, Y1, Z1), (X0, Y1, Z1)], None, None))
    if Y0 > CH_EYE:
        out.append(("bottom", [(X0, Y0, Z0), (X1, Y0, Z0), (X1, Y0, Z1), (X0, Y0, Z1)], None, None))
    return out


def fq(fm, a, b, c, d, dep=0.0):
    """Face-local rectangle u a..b, v c..d at depth dep (negative = proud of the wall)."""
    return [fm(a, c, dep), fm(a, d, dep), fm(b, d, dep), fm(b, c, dep)]


def ch_line(S, p, q):
    a, b = S.C(*p), S.C(*q)
    return f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>'


def _num(v):
    t = f"{v:.1f}"
    if t.endswith(".0"):
        t = t[:-2]
    if t.startswith("0."):
        t = t[1:]
    elif t.startswith("-0."):
        t = "-" + t[2:]
    return "0" if t in ("-0", "") else t


def d_rel(pts, close=True):
    """Compact path data: absolute start, then relative steps between the rounded points."""
    r = [(round(x, 1), round(y, 1)) for x, y in pts]
    out = [f"M{_num(r[0][0])} {_num(r[0][1])}l"]
    seq = []
    for (ax, ay), (bx, by) in zip(r, r[1:]):
        seq.append(f"{_num(bx - ax)} {_num(by - ay)}")
    out.append(" ".join(seq).replace(" -", "-"))
    return "".join(out) + ("z" if close else "")


class Bk:
    """Collects many small shapes and writes each (layer, paint) group as ONE path: same picture, far fewer bytes.
    Layers keep the stacking right (glass < room details < blinds < reveals < mullions < ledges)."""
    def __init__(self, S):
        self.S = S
        self.k = {}

    def poly(self, layer, pts3, fill, extra="", min_area=0.35):
        pts = [self.S.C(*q) for q in pts3]
        if min_area and abs(sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts)))) / 2 < min_area:
            return
        d = d_rel(pts)
        self.k.setdefault((layer, "f", fill, extra), []).append(d)

    def line(self, layer, p, q, stroke, w, extra=""):
        a, b = self.S.C(*p), self.S.C(*q)
        self.k.setdefault((layer, "s", stroke, f'{w:.2f}"{extra}'), []).append(d_rel([a, b], False))

    def svg(self):
        out = []
        for key in sorted(self.k, key=lambda k: k[0]):
            ds = "".join(self.k[key])
            if key[1] == "f":
                out.append(f'<path d="{ds}" fill="{key[2]}"{key[3]}/>')
            else:
                out.append(f'<path d="{ds}" fill="none" stroke="{key[2]}" stroke-width="{key[3]}/>')
        return "".join(out)


def ch_vgrad(S, quad, stops):
    ys = [S.C(*q)[1] for q in quad]
    gid = S.gid("v")
    S.defs.append(lg(gid, stops, 0, round(min(ys), 1), 0, round(max(ys), 1), units="userSpaceOnUse"))
    return f"url(#{gid})"


def ch_face_paint(S, kind, quad, col):
    """Golden-hour light on a wall: the sunlit river face glows warm up high and cools toward the street canyon,
    the sky-lit face carries a warm bounce off the river at its foot, the shaded front darkens downward."""
    if kind == "xneg":
        st = [(0, cmix(cscale(col, 1.12), "#FFE4B4", 0.3)), (0.45, col), (1, cmix(cscale(col, 0.8), "#6A4A6A", 0.28))]
    elif kind == "xpos":
        st = [(0, cmix(cscale(col, 1.08), "#B8B0D8", 0.15)), (0.55, col), (1, cmix(cscale(col, 0.86), "#B07A80", 0.25))]
    else:
        st = [(0, cmix(cscale(col, 1.1), "#9A90C0", 0.2)), (0.5, col), (1, cmix(cscale(col, 0.76), "#1E1A36", 0.2))]
    return ch_vgrad(S, quad, st)


def ch_haze_over(S, kind, quad, Zn, Zf):
    """Extra aerial haze toward the far end of a receding face (details are painted with the near end's haze)."""
    if kind == "front":
        return ""
    fa, fb = S.fog(Zn), S.fog(Zf)
    if fb - fa < 0.03:
        return ""
    xa, xb = S.C(*quad[0])[0], S.C(*quad[3])[0]
    gid = S.gid("hz")
    S.defs.append(lg(gid, [(0, CH_HAZE, 0), (1, CH_HAZE, round(min(0.85, fb - fa), 2))], round(xa, 1), 0, round(xb, 1), 0, units="userSpaceOnUse"))
    return S.poly(quad, f"url(#{gid})")


def ch_chunks(S, side, zat, u0, u1, size, min_px, n=6):
    """Split a face along u; in each chunk give the spacing multiplier (1, 2, 4...) that keeps marks >= min_px apart."""
    out = []
    k_ = n if side else 1
    for k in range(k_):
        ua, ub = u0 + (u1 - u0) * k / k_, u0 + (u1 - u0) * (k + 1) / k_
        m = 1
        while S.f / zat(ub) * size * m < min_px and m < 8:
            m *= 2
        if S.f / zat(ub) * size * m >= min_px:
            out.append((ua, ub, m))
    return out


def ch_hjoints(S, fm, side, zat, u0, u1, v0, v1, step, min_px=1.8, phase=0.0):
    out = []
    for ua, ub, m in ch_chunks(S, side, zat, u0, u1, step, min_px):
        s = step * m
        v = v0 + phase + s
        while v < v1 - 0.05:
            out.append(ch_line(S, fm(ua, v), fm(ub, v)))
            v += s
    return "".join(out)


def ch_vjoints(S, fm, side, zat, u0, u1, v0, v1, step, min_px=2.0, dep=0.0):
    out = []
    k = 1
    while u0 + k * step < u1 - 0.1:
        u = u0 + k * step
        mm = 1
        while S.f / zat(u) * step * mm < min_px and mm < 8:
            mm *= 2
        if S.f / zat(u) * step * mm >= min_px and k % mm == 0:
            out.append(ch_line(S, fm(u, v0, dep), fm(u, v1, dep)))
        k += 1
    return "".join(out)


MAT_FRAME = {"stone": "#F2EADC", "brick": "#EFE8DC", "tc": "#6A5650"}


def ch_sun_shadow(S, t, kind, fm, ur, rnd):
    """The low sun comes across the river from the south-west, so the towers on the south bank throw a ragged
    band of cool shadow over the lower floors of the north-bank river faces; only the upper floors burn gold."""
    if kind != "xneg" or t["Z0"] > 900 or t.get("sun_shadow") is False:
        return ""
    Y0, Y1 = t["Y0"], t["Y1"]
    u0, u1 = ur
    pts = [fm(u0, Y0)]
    u = u0
    h = rnd.uniform(0.35, 0.55)
    while u < u1:
        un = min(u1, u + rnd.uniform(12, 30))
        top = min(Y1, Y0 + (Y1 - Y0) * h + 3)
        pts += [fm(u, top), fm(un, top)]
        h = max(0.2, min(0.7, h + rnd.uniform(-0.18, 0.18)))
        u = un
    pts.append(fm(u1, Y0))
    return S.poly(pts, "#3A2C5A", ' opacity="0.36"')


def ch_masonry_face(S, t, kind, quad, fm, ur, rnd):
    """Limestone / brick / terra-cotta wall: graded light, coursing, proud piers with lit and shaded sides,
    recessed spandrels, punched windows with jamb + soffit/sill reveals, mullions, blinds, lit rooms, a
    rusticated or arcaded base, belt courses, an attic frieze and rain-wash weathering."""
    mat, base = t["mat"], t["base"]
    Z0, Z1, Y0, Y1 = t["Z0"], t["Z1"], t["Y0"], t["Y1"]
    u0, u1 = ur
    side = kind != "front"
    zat = (lambda u: u) if side else (lambda u: Z0)
    ppm = lambda u: S.f / zat(u)
    Zn, Zf = Z0, (Z1 if side else Z0)
    col = S.lit(base, kind, Zn)
    fog = S.fog(Zn)
    soff = S.lit(base, "bottom", Zn)
    sill_c = S.lit(base, "top", Zn)
    shade = cmix(cscale(col, 0.6), "#1E1A36", 0.3)
    hi = cmix(col, "#FFF2DC", 0.4 if kind == "xneg" else 0.22)
    gt, gm, gb = (cmix(cmix(g, "#1C1A30", 0.42), CH_HAZE, fog * 0.8) for g in CH_GLASS[kind])
    glass = ch_vgrad(S, quad, [(0, gt), (0.55, gm), (1, gb)])
    glass_far = cmix(gm, col, 0.25)
    frame = cmix(MAT_FRAME[mat], CH_HAZE, fog) if mat != "tc" else cmix(cmix(MAT_FRAME[mat], col, 0.2), CH_HAZE, fog)
    out = [S.poly(quad, ch_face_paint(S, kind, quad, col))]
    fh, bay = t.get("fh", 4.0), t.get("bay", 3.0)
    winw, winh = t.get("winw", 0.56), t.get("winh", 0.6)
    street = Y0 < 10
    base_h = t.get("base_h", 5.0 if street else 0.8)
    cor_h = t.get("cornice_h", 1.4) if t.get("cornice", True) else 0.0
    attic = t.get("attic", 0.0)
    m = t.get("margin", 1.0)
    nb = max(1, int(round((u1 - u0 - 2 * m) / bay)))
    bw = (u1 - u0 - 2 * m) / nb
    yf0 = Y0 + base_h
    ytop = Y1 - cor_h - attic
    nf = max(0, int((ytop - yf0) / fh + 0.3))
    fh2 = (ytop - yf0) / nf if nf else fh

    def side_kind(a):
        """orientation of a reveal / pier side seen at face-coordinate a"""
        return "front" if side else ("xneg" if a > CH_XC else "xpos")

    # -- texture: coursing, brick bond, glazed blocks
    if mat == "brick":
        out.append(f'<g stroke="{cmix(cscale(col, 0.72), "#3A1E1A", 0.2)}" stroke-width="0.45" opacity="0.42">'
                   + ch_hjoints(S, fm, side, zat, u0, u1, Y0, ytop, 0.33, 1.7) + "</g>")
        for _ in range(int(30 * min(1.0, ppm(u0) / 4)) if ppm(u0) > 1.2 else 0):
            ua = rnd.uniform(u0, u1 - 2)
            va = rnd.uniform(Y0, ytop - 1)
            w, h = rnd.uniform(1.5, 5), rnd.uniform(0.3, 1.4)
            out.append(S.poly(fq(fm, ua, ua + w, va, va + h), rnd.choice([cscale(col, 1.14), cscale(col, 0.84), cmix(col, "#6A2E26", 0.35), cmix(col, "#C89070", 0.3)]),
                              f' opacity="{rnd.uniform(0.18, 0.4):.2f}"'))
    elif mat == "stone":
        out.append(f'<g stroke="{shade}" stroke-width="0.45" opacity="0.16">' + ch_hjoints(S, fm, side, zat, u0, u1, yf0, ytop, 1.0, 3.2) + "</g>")
    else:
        out.append(f'<g stroke="{shade}" stroke-width="0.4" opacity="0.13">' + ch_hjoints(S, fm, side, zat, u0, u1, yf0, ytop, 0.8, 3.0)
                   + ch_vjoints(S, fm, side, zat, u0, u1, yf0, ytop, 1.2, 3.5) + "</g>")
    # -- windows, bay by bay (near bays in full detail, far bays as ribbons of glass)
    lit_p = t.get("lit", 0.22)
    pair = t.get("pair", False)
    dep = 0.42 if mat != "brick" else 0.3
    B = Bk(S)
    jamb_c = {}
    # far bays: one ribbon of glass per floor across all of them, lit windows dotted in
    i_far = nb
    for i in range(nb):
        ba = u0 + m + i * bw
        sw_ = bw * (0.72 if pair else winw)
        if ppm(ba + bw / 2) * sw_ < 2.2 or ppm(ba + bw / 2) * fh2 * winh < 2.4:
            i_far = i
            break
    if i_far < nb:
        ua, ub = u0 + m + i_far * bw + bw * 0.15, u1 - m - bw * 0.15
        for f_ in range(nf):
            c = yf0 + f_ * fh2 + fh2 * (1 - winh) * 0.62
            d = c + fh2 * winh
            B.poly(1, fq(fm, ua, ub, c, d), glass_far)
            for i in range(i_far, nb):
                if rnd.random() < lit_p:
                    a = u0 + m + i * bw + bw * (1 - winw) / 2
                    B.poly(2, fq(fm, a, a + bw * winw, c, d), cmix(rnd.choice(LIT_WIN), CH_HAZE, fog * 0.6))
    for i in range(i_far):
        ba = u0 + m + i * bw
        if pair:
            spans = [(ba + bw * 0.14, ba + bw * 0.47), (ba + bw * 0.53, ba + bw * 0.86)]
        else:
            a = ba + bw * (1 - winw) / 2
            spans = [(a, a + bw * winw)]
        pp = ppm(ba + bw / 2)
        far = pp * (spans[0][1] - spans[0][0]) < 2.2 or pp * fh2 * winh < 2.4
        for f_ in range(nf):
            c = yf0 + f_ * fh2 + fh2 * (1 - winh) * 0.62
            d = c + fh2 * winh
            if far:
                B.poly(1, fq(fm, spans[0][0], spans[-1][1], c, d), glass_far)
                for a, b in spans:
                    if rnd.random() < lit_p:
                        B.poly(2, fq(fm, a, b, c, d), cmix(rnd.choice(LIT_WIN), CH_HAZE, fog * 0.6))
                continue
            # recessed spandrel panel under the window (stone, terra cotta)
            if mat != "brick" and f_ > 0 and pp * 0.8 > 2.4:
                B.poly(0, fq(fm, spans[0][0], spans[-1][1], c - fh2 * (1 - winh) + 0.35, c - 0.3), cscale(col, 0.9), ' opacity="0.7"')
                if mat == "tc" and pp * 0.6 > 3:
                    mu = (spans[0][0] + spans[-1][1]) / 2
                    mv = c - fh2 * (1 - winh) / 2
                    B.poly(1, [fm(mu - 0.32, mv), fm(mu, mv + 0.32), fm(mu + 0.32, mv), fm(mu, mv - 0.32)], hi)
            for a, b in spans:
                on = rnd.random() < lit_p
                w_px = pp * (b - a)
                B.poly(2, fq(fm, a, b, c, d), cmix(rnd.choice(LIT_WIN), CH_HAZE, fog * 0.6) if on else glass)
                if on and w_px > 3.5:
                    # a room: darker furniture line low down, warm ceiling glow
                    B.poly(3, fq(fm, a, b, c, c + (d - c) * 0.3), "#8A5636", ' opacity="0.3"')
                    B.poly(3, fq(fm, a, b, d - (d - c) * 0.18, d), "#FFF4D6", ' opacity="0.5"')
                elif not on and rnd.random() < 0.16 and w_px > 2.5:
                    # blinds half drawn, catching the light
                    B.poly(4, fq(fm, a, b, d - (d - c) * rnd.choice((0.3, 0.45, 0.6)), d), cmix(col, "#F4E6CC", 0.45))
                if pp * dep > 0.8:
                    ju = b if (side or a > CH_XC) else a
                    sk = side_kind(a)
                    if sk not in jamb_c:
                        jamb_c[sk] = S.lit(base, sk, Zn)
                    B.poly(5, [fm(ju, c), fm(ju, d), fm(ju, d, dep), fm(ju, c, dep)], jamb_c[sk])
                    if d > CH_EYE:
                        B.poly(5, [fm(a, d), fm(b, d), fm(b, d, dep), fm(a, d, dep)], soff)
                    if c < CH_EYE:
                        B.poly(5, [fm(a, c), fm(b, c), fm(b, c, dep), fm(a, c, dep)], sill_c)
                if w_px > 6:
                    sw = round(max(0.5, pp * 0.07) * 4) / 4
                    B.line(6, fm((a + b) / 2, c, dep), fm((a + b) / 2, d, dep), frame, sw)
                    B.line(6, fm(a, c + (d - c) * 0.68, dep), fm(b, c + (d - c) * 0.68, dep), frame, sw)
                if mat != "tc" and w_px > 4:
                    # stone sill ledge catching the light; brick walls also get a stone lintel
                    B.poly(7, fq(fm, a - 0.15, b + 0.15, c - 0.22, c, -0.12), hi)
                    if mat == "brick":
                        B.poly(7, fq(fm, a - 0.2, b + 0.2, d, d + 0.38, -0.05), cmix(S.lit("#DCCAA8", kind, Zn), col, 0.1))
                if mat in ("stone", "tc") and rnd.random() < 0.1 and w_px > 3:
                    # rain-wash streak under a sill
                    B.poly(8, fq(fm, a + (b - a) * 0.2, b - (b - a) * 0.2, c - rnd.uniform(1.5, 4.5), c - 0.2), shade, ' opacity="0.09"')
    # -- proud piers running up between the bays, with their lit face and the shaded side we see
    if t.get("piers"):
        pw, pd = t.get("pw", 0.8 if not pair else 0.6), 0.32
        pc = cmix(cscale(col, 1.06), "#FFF0D8", 0.15 if kind == "xneg" else 0.04)
        ptop = ytop + (attic if t.get("piers_full") else 0)
        for i in range(1, nb):
            uc = u0 + m + i * bw
            pa, pb = uc - pw / 2, uc + pw / 2
            if ppm(uc) * pw < 1.0:
                continue
            B.poly(9, fq(fm, pa, pb, yf0, ptop, -pd), pc)
            su = pa if (side or pa > CH_XC) else pb
            sk = side_kind(pa)
            if sk not in jamb_c:
                jamb_c[sk] = S.lit(base, sk, Zn)
            B.poly(9, [fm(su, yf0), fm(su, ptop), fm(su, ptop, -pd), fm(su, yf0, -pd)], jamb_c[sk])
            if kind == "xneg" and ppm(uc) * pw > 2.5:
                B.poly(10, fq(fm, pb - pw * 0.22, pb, yf0, ptop, -pd), "#FFF2D8", ' opacity="0.28"')
    out.append(B.svg())
    # -- attic frieze under the cornice
    if attic > 0:
        out.append(S.poly(fq(fm, u0, u1, ytop - 0.15, ytop + 0.35, -0.2), hi))
        g = []
        for i in range(nb):
            ba = u0 + m + i * bw
            if ppm(ba) * bw < 4:
                continue
            mu = ba + bw / 2
            mv = ytop + attic * 0.55
            r = min(bw, attic) * 0.22
            if mat == "tc":
                g.append(S.poly([fm(mu + r * math.cos(a_ * math.pi / 4), mv + r * math.sin(a_ * math.pi / 4)) for a_ in range(8)], cscale(col, 0.82)))
                g.append(S.poly([fm(mu + r * 0.5 * math.cos(a_ * math.pi / 4), mv + r * 0.5 * math.sin(a_ * math.pi / 4)) for a_ in range(8)], hi))
            else:
                g.append(S.poly(fq(fm, mu - bw * 0.18, mu + bw * 0.18, mv - attic * 0.22, mv + attic * 0.22), glass))
        out.append("".join(g))
    # -- the street storey: rustication and an arcade, or shopfronts with striped awnings
    if street and base_h >= 3:
        out.append(ch_base(S, t, kind, fm, u0, u1, Y0, yf0, nb, bw, m, ppm, col, hi, shade, side, zat, rnd))
    elif base_h > 0.5:
        out.append(S.poly(fq(fm, u0, u1, Y0, yf0), cscale(col, 0.92), ' opacity="0.6"'))
    # -- belt course at the top of the base
    if yf0 - Y0 > 2:
        out.append(S.poly(fq(fm, u0, u1, yf0 - 0.55, yf0, -0.3), hi))
        out.append(S.poly(fq(fm, u0, u1, yf0 - 1.1, yf0 - 0.55), shade, ' opacity="0.35"'))
    out.append(ch_sun_shadow(S, t, kind, fm, ur, rnd))
    # -- the corner: a sunlit arris on the river face, a soft dark seam where the faces meet
    if side:
        out.append(S.poly([fm(u0, Y0), fm(u0, Y1), fm(u0 + 0.5, Y1), fm(u0 + 0.5, Y0)], "#FFF4DC" if kind == "xneg" else "#E8E0F0",
                          f' opacity="{0.55 if kind == "xneg" else 0.25}"'))
    out.append(ch_haze_over(S, kind, quad, Zn, Zf))
    return "".join(out)


def ch_base(S, t, kind, fm, u0, u1, Y0, yf0, nb, bw, m, ppm, col, hi, shade, side, zat, rnd):
    mat = t["mat"]
    fog = S.fog(t["Z0"])
    out = []
    shop = cmix("#FFD48A", CH_HAZE, fog * 0.5)
    shop2 = cmix("#C8703E", CH_HAZE, fog * 0.5)
    quad_b = fq(fm, u0, u1, Y0, yf0)
    inner = ch_vgrad(S, quad_b, [(0, shop), (0.55, cmix(shop, shop2, 0.5)), (1, shop2)])
    if mat in ("stone", "tc"):
        out.append(f'<g stroke="{shade}" stroke-width="0.6" opacity="0.4">' + ch_hjoints(S, fm, side, zat, u0, u1, Y0, yf0 - 0.6, 0.75, 2.2) + "</g>")
    for i in range(nb):
        ba = u0 + m + i * bw
        pp = ppm(ba + bw / 2)
        a, b = ba + bw * 0.13, ba + bw * 0.87
        top = yf0 - 1.0
        if pp * (b - a) < 2:
            out.append(S.poly(fq(fm, a, b, Y0 + 0.2, top), inner, ' opacity="0.85"'))
            continue
        if t.get("arcade"):
            r = (b - a) / 2
            spring = top - r
            pts = [fm(a, Y0 + 0.1), fm(a, spring)] + [fm((a + b) / 2 - r * math.cos(math.pi * k / 12), spring + r * math.sin(math.pi * k / 12)) for k in range(13)] + [fm(b, Y0 + 0.1)]
            ring = [fm((a + b) / 2 - (r + 0.45) * math.cos(math.pi * k / 12), spring + (r + 0.45) * math.sin(math.pi * k / 12)) for k in range(13)]
            out.append(f'<polygon points="{P([S.C(*q) for q in [fm(a - 0.45, spring)] + ring + [fm(b + 0.45, spring)]])}" fill="{hi}"/>')
            out.append(f'<polygon points="{P([S.C(*q) for q in pts])}" fill="{inner}"/>')
            # reveal on the far side of the arch, mullioned fanlight, keystone
            ju = b if (side or a > CH_XC) else a
            out.append(S.poly([fm(ju, Y0 + 0.1), fm(ju, spring), fm(ju, spring, 0.9), fm(ju, Y0 + 0.1, 0.9)], S.lit(t["base"], "front" if side else "xneg", t["Z0"])))
            if pp * r > 3:
                sw = max(0.5, pp * 0.08)
                fan = "".join(ch_line(S, fm((a + b) / 2, spring, 0.5), fm((a + b) / 2 - r * math.cos(math.pi * k / 4), spring + r * math.sin(math.pi * k / 4), 0.5)) for k in (1, 2, 3))
                out.append(f'<g stroke="#5A4038" stroke-width="{sw:.2f}" opacity="0.8">' + fan + ch_line(S, fm(a, spring, 0.5), fm(b, spring, 0.5))
                           + ch_line(S, fm((a + b) / 2, Y0 + 0.1, 0.5), fm((a + b) / 2, spring, 0.5)) + "</g>")
                kx = (a + b) / 2
                out.append(S.poly([fm(kx - 0.35, top + 0.5, -0.1), fm(kx - 0.22, top - 0.25, -0.1), fm(kx + 0.22, top - 0.25, -0.1), fm(kx + 0.35, top + 0.5, -0.1)], cmix(hi, "#FFFFFF", 0.2)))
            # people inside, dark against the glow
            if pp * 1.7 > 7:
                for j in range(rnd.randint(1, 2)):
                    x, y = S.C(*fm(rnd.uniform(a + 0.6, b - 0.6), Y0 + 0.1, 1.5))
                    hh = pp * 1.65
                    out.append(f'<path d="M {x - hh * 0.13:.1f} {y:.1f} L {x - hh * 0.15:.1f} {y - hh * 0.62:.1f} Q {x:.1f} {y - hh * 0.74:.1f} {x + hh * 0.15:.1f} {y - hh * 0.62:.1f} L {x + hh * 0.13:.1f} {y:.1f} Z" fill="#5A3A34" opacity="0.75"/>'
                               f'<circle cx="{x:.1f}" cy="{y - hh * 0.84:.1f}" r="{hh * 0.1:.1f}" fill="#5A3A34" opacity="0.75"/>')
        else:
            out.append(S.poly(fq(fm, a, b, Y0 + 0.2, top), inner))
            if pp * 0.15 > 0.5:
                out.append(f'<g stroke="#3A2A2A" stroke-width="{max(0.5, pp * 0.1):.2f}" opacity="0.7">'
                           + ch_line(S, fm((a + b) / 2, Y0 + 0.2), fm((a + b) / 2, top)) + ch_line(S, fm(a, top - 1.0), fm(b, top - 1.0)) + "</g>")
            if mat == "brick" and pp * 1.0 > 1.6:
                # striped canvas awning, sloping out over the sidewalk
                cols = t.get("awning", ("#2E5A4A", "#EFE6D2"))
                n_ = 6
                for k in range(n_):
                    ua, ub = a - 0.2 + (b - a + 0.4) * k / n_, a - 0.2 + (b - a + 0.4) * (k + 1) / n_
                    out.append(S.poly([fm(ua, top + 0.4), fm(ub, top + 0.4), fm(ub, top - 0.7, -1.4), fm(ua, top - 0.7, -1.4)], cmix(cols[k % 2], CH_HAZE, fog)))
                out.append(S.poly([fm(a - 0.2, top - 0.7, -1.4), fm(b + 0.2, top - 0.7, -1.4), fm(b + 0.2, top - 1.0, -1.4), fm(a - 0.2, top - 1.0, -1.4)], cmix(cols[0], "#1A1A2A", 0.3)))
    return "".join(out)


def ch_glass_face(S, t, kind, quad, fm, ur, rnd):
    """Curtain wall: graded sky reflection, the city across the water mirrored in it (warm sunlit towers on the
    south bank's glass, cool shaded ones on the north bank's), quilted panes, spandrel bands, mullions catching
    the sun, a hot spot of reflected sun, lit offices."""
    mat, base = t["mat"], t["base"]
    Z0, Z1, Y0, Y1 = t["Z0"], t["Z1"], t["Y0"], t["Y1"]
    u0, u1 = ur
    side = kind != "front"
    zat = (lambda u: u) if side else (lambda u: Z0)
    ppm = lambda u: S.f / zat(u)
    Zn, Zf = Z0, (Z1 if side else Z0)
    fog = S.fog(Zn)
    gt, gm, gb = CH_GLASS[kind]
    if mat == "dark":
        gt, gm, gb = (cmix(g, "#16141E", 0.74) for g in (gt, gm, gb))
    ta = t.get("tint_amt", 0.28)
    gt, gm, gb = (cmix(cmix(g, base, ta), CH_HAZE, fog) for g in (gt, gm, gb))
    fill = ch_vgrad(S, quad, [(0, gt), (0.5, gm), (0.85, cmix(gm, gb, 0.7)), (1, gb)])
    cid = S.gid("cp")
    S.defs.append(f'<clipPath id="{cid}"><polygon points="{S.p(quad)}"/></clipPath>')
    out = [S.poly(quad, fill)]
    g = []
    H = Y1 - Y0
    fh = t.get("fh", 4.0)
    mw = t.get("mull", 1.5)
    # 1) the city across the water mirrored in the glass
    if kind == "xpos":
        rcols = ["#F4C892", "#E8A880", "#FFE0B0", "#C88A80"]
    elif kind == "xneg":
        rcols = ["#4A4470", "#5E4E78", "#3A3456", "#7A5E7E"]
    else:
        rcols = ["#24244A", "#2E2C52", "#C89A90", "#3A3660"]
    for _ in range(rnd.randint(4, 7)):
        ua = rnd.uniform(u0 - (u1 - u0) * 0.1, u1)
        ub = min(u1 + 1, ua + rnd.uniform(0.06, 0.24) * (u1 - u0))
        vt = Y0 + H * rnd.uniform(0.12, 0.62)
        rc = cmix(cmix(rnd.choice(rcols), gm, 0.25), CH_HAZE, fog)
        op = rnd.uniform(0.32, 0.55) * (0.6 if mat == "dark" else 1)
        g.append(S.poly([fm(ua, Y0 - 1), fm(ua, vt), fm(ub, vt), fm(ub, Y0 - 1)], rc, f' opacity="{op:.2f}"'))
        if ppm(ua) * 0.6 > 1:
            g.append(S.poly(fq(fm, ua, ub, vt - 0.6, vt), cmix(rc, "#FFF0D8", 0.4), f' opacity="{op:.2f}"'))
    if kind == "front" and mat == "glass":
        # sunlit towers behind the viewer, caught in the shaded east glass: warm bands fading toward the street
        ys_ = [S.C(*q)[1] for q in quad]
        wg = S.gid("wr")
        S.defs.append(lg(wg, [(0, "#FFD8A0", 0.62), (0.45, "#F2B088", 0.32), (0.8, "#C8908A", 0.0)], 0, round(max(min(ys_), 20), 1), 0, round(max(ys_), 1), units="userSpaceOnUse"))
        for _ in range(3):
            ua = rnd.uniform(u0, u1 - (u1 - u0) * 0.15)
            ub = ua + (u1 - u0) * rnd.uniform(0.1, 0.28)
            vt = Y1 - H * rnd.uniform(0.0, 0.25)
            g.append(S.poly([fm(ua, Y0), fm(ua, vt), fm(ub, vt), fm(ub, Y0)], f"url(#{wg})"))
    # 2) quilting: neighbouring panes catch the sky a little differently
    QB = Bk(S)
    for _ in range(70):
        f_ = rnd.randrange(max(1, int(H / fh)))
        i = rnd.randrange(max(1, int((u1 - u0) / mw)))
        ua = u0 + i * mw
        if ppm(ua) * mw < 2.5:
            continue
        va = Y0 + f_ * fh
        n_ = rnd.randint(1, 3)
        QB.poly(0, fq(fm, ua, ua + mw * n_, va, va + fh * rnd.randint(1, 2)), rnd.choice(["#FFFFFF", "#1A1830", gt, gb]), f' opacity="{rnd.choice((0.07, 0.11, 0.15))}"')
    g.append(QB.svg())
    # 3) a diagonal sheen of open sky sliding down the glass
    ua = u0 + (u1 - u0) * rnd.uniform(0.1, 0.5)
    wd = (u1 - u0) * rnd.uniform(0.1, 0.2)
    g.append(S.poly([fm(ua, Y1), fm(ua + wd, Y1), fm(ua + wd * 1.8, Y0), fm(ua + wd * 0.8, Y0)], "#FFF4E0" if kind != "front" else "#B8B0E0", ' opacity="0.12"'))
    # 4) lit offices
    nf = int(H / fh)
    nb = max(1, int((u1 - u0) / mw))
    LB = Bk(S)
    lo_ = round(0.9 - fog, 1)
    for f_ in range(nf):
        for i in range(nb):
            if rnd.random() < t.get("lit", 0.05) * (1 if ppm(u0 + i * mw) * mw > 1.2 else 0.4):
                ua, ub = u0 + i * mw, u0 + (i + rnd.randint(1, 3)) * mw
                va = Y0 + f_ * fh
                LB.poly(0, fq(fm, ua, min(u1, ub), va + 0.25 * fh, va + 0.95 * fh), rnd.choice(LIT_WIN), f' opacity="{lo_}"')
    g.append(LB.svg())
    # 5) spandrel bands at each floor slab and the mullion grid
    sp_col = "#0E0E18" if mat == "dark" else cmix(gm, "#1A1A30", 0.45)
    bands = []
    for ua, ub, mm in ch_chunks(S, side, zat, u0, u1, fh, 2.6):
        v = Y0 + fh * mm
        while v < Y1 - 0.3:
            bands.append(d_rel([S.C(*q) for q in fq(fm, ua, ub, v - fh * 0.22, v)]))
            v += fh * mm
    g.append(f'<path d="{"".join(bands)}" fill="{sp_col}" opacity="{0.55 if mat == "dark" else 0.32}"/>')
    if kind == "xneg":
        lc, lo = ("#FFD8A0", 0.5) if mat == "dark" else ("#FFE6C0", 0.34)
    elif kind == "xpos":
        lc, lo = ("#8A7E9A", 0.5) if mat == "dark" else ("#D8CCE8", 0.28)
    else:
        lc, lo = ("#6A6478", 0.55) if mat == "dark" else ("#141A34", 0.36)
    sw = max(0.45, min(1.2, ppm(u0) * 0.09))
    g.append(f'<g stroke="{cmix(lc, CH_HAZE, fog)}" stroke-width="{sw:.2f}" opacity="{lo * (1 - fog * 0.6):.2f}">' + ch_vjoints(S, fm, side, zat, u0, u1, Y0, Y1, mw, 2.4) + "</g>")
    # 6) a hot spot of reflected sun on the sunlit glass
    if kind == "xneg" and mat != "dark":
        hx, hy = S.C(*fm(u0 + (u1 - u0) * rnd.uniform(0.15, 0.45), Y0 + H * rnd.uniform(0.45, 0.8)))
        g.append(glow(round(hx, 1), round(hy, 1), round(ppm(u0) * min(H, u1 - u0) * 0.35, 1), "#FFF2CC", S.gid("hot"), 0.55))
    g.append(ch_sun_shadow(S, t, kind, fm, ur, rnd))
    out.append(f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>")
    # sunlit arris on the near corner
    if side:
        out.append(S.poly([fm(u0, Y0), fm(u0, Y1), fm(u0 + 0.4, Y1), fm(u0 + 0.4, Y0)], "#FFF2D8" if kind == "xneg" else "#D8D0F0", ' opacity="0.45"'))
    out.append(ch_haze_over(S, kind, quad, Zn, Zf))
    return "".join(out)


def ch_tier(S, t, seed):
    """t: dict(X0, X1, Z0, Z1, Y0, Y1, mat in stone/brick/tc/glass/dark, base colour, fh, bay, lit, piers, pair,
    arcade, attic, cornice, cornice_d, cornice_h, balustrade, tanks, reflect)."""
    X0, X1, Z0, Z1, Y0, Y1 = t["X0"], t["X1"], t["Z0"], t["Z1"], t["Y0"], t["Y1"]
    mat, base = t["mat"], t["base"]
    rnd = random.Random(seed)
    out = []
    for kind, quad, fm, ur in box_faces(X0, X1, Z0, Z1, Y0, Y1):
        if fm is None:
            out.append(S.poly(quad, S.lit(base, kind, Z0)))
            continue
        if mat in ("glass", "dark"):
            out.append(ch_glass_face(S, t, kind, quad, fm, ur, rnd))
        else:
            out.append(ch_masonry_face(S, t, kind, quad, fm, ur, rnd))
        # the river face shows in the water
        if t.get("reflect", True) and kind in ("xpos", "xneg") and Z0 < 1500:
            if mat in ("glass", "dark"):
                rc = CH_GLASS[kind][1] if mat == "glass" else "#2A2634"
                rc = cmix(cmix(rc, base, 0.3), CH_HAZE, S.fog(Z0))
            else:
                rc = cmix(S.lit(base, kind, Z0), "#3A3A60", 0.2)
            S.refl.append((Z0, quad, rc, t.get("lit", 0.1)))
    # cornice: a proud moulded slab with its shadowed soffit, a row of modillions and a soft cast shadow
    if t.get("cornice", mat in ("stone", "brick", "tc")):
        e = t.get("cornice_d", 0.8)
        hgt = t.get("cornice_h", 1.4)
        yb = Y1 - hgt
        for kind, quad, fm, ur in box_faces(X0 - e, X1 + e, Z0 - e, Z1 + e, yb, Y1):
            if kind in ("bottom", "top"):
                continue
            c_ = S.lit(cscale(base, 1.1), kind, Z0)
            out.append(S.poly(quad, c_))
            q = quad
            lerp = lambda a, b, s: tuple(a[i] + (b[i] - a[i]) * s for i in range(3))
            # upper lip catching the light + a darker bed moulding
            out.append(S.poly([q[1], q[2], lerp(q[2], q[3], 0.28), lerp(q[1], q[0], 0.28)], "#FFF2DC", ' opacity="0.35"'))
            out.append(S.poly([lerp(q[1], q[0], 0.62), lerp(q[2], q[3], 0.62), lerp(q[2], q[3], 0.75), lerp(q[1], q[0], 0.75)], cscale(c_, 0.8), ' opacity="0.7"'))
        # cast shadow on the wall below, and the modillions in it
        for kind, quad, fm, ur in box_faces(X0, X1, Z0, Z1, yb - 2.2, yb):
            if fm is None:
                continue
            out.append(S.poly(fq(fm, ur[0], ur[1], yb - 0.9, yb), "#16142A", ' opacity="0.32"'))
            out.append(S.poly(fq(fm, ur[0], ur[1], yb - 2.2, yb - 0.9), "#16142A", ' opacity="0.12"'))
            u0, u1 = ur
            zat = (lambda u: u) if kind != "front" else (lambda u: Z0)
            mods = []
            u = u0 + 0.5
            mc = S.lit(cscale(base, 1.05), kind, Z0)
            while u < u1 - 0.3:
                if S.f / zat(u) * 0.3 > 0.9:
                    mods.append(S.poly(fq(fm, u, u + 0.32, yb - 0.55, yb, -e * 0.7), mc))
                u += 0.95
            out.append("".join(mods))
        if yb > CH_EYE:
            out.append(S.poly([(X0 - e, yb, Z0 - e), (X1 + e, yb, Z0 - e), (X1, yb, Z0), (X0, yb, Z0)], "#1E1A30", ' opacity="0.7"'))
            if X1 < CH_XC:
                out.append(S.poly([(X1 + e, yb, Z0 - e), (X1 + e, yb, Z1 + e), (X1, yb, Z1), (X1, yb, Z0)], "#1E1A30", ' opacity="0.7"'))
            if X0 > CH_XC:
                out.append(S.poly([(X0 - e, yb, Z0 - e), (X0 - e, yb, Z1 + e), (X0, yb, Z1), (X0, yb, Z0)], "#3A2A3A", ' opacity="0.6"'))
    if t.get("balustrade"):
        out.append(ch_balustrade(S, t))
    for (tx, tz) in t.get("tanks", ()):
        out.append(ch_water_tank(S, tx, Y1, tz))
    return "".join(out)


def ch_balustrade(S, t):
    """Stone balustrade along the roof edge facing the river and the front, seen against the sky."""
    e = t.get("cornice_d", 0.8) * 0.6
    X0, X1, Z0, Z1, Y1 = t["X0"] - e, t["X1"] + e, t["Z0"] - e, t["Z1"] + e, t["Y1"]
    col = S.lit(cscale(t["base"], 1.08), "xneg" if X0 > CH_XC else "xpos", Z0)
    edges = [((X0, Z0), (X1, Z0))]
    edges.append(((X0, Z0), (X0, Z1)) if X0 > CH_XC else ((X1, Z0), (X1, Z1)))
    out = []
    for (xa, za), (xb, zb) in edges:
        L = math.hypot(xb - xa, zb - za)
        n = int(L / 0.45)
        posts = []
        for i in range(n + 1):
            s = i / n
            X, Z = xa + (xb - xa) * s, za + (zb - za) * s
            if S.px(Z) * 0.45 < 1.2 and i % 2:
                continue
            posts.append(ch_line(S, (X, Y1 + 0.2, Z), (X, Y1 + 0.95, Z)))
        out.append(f'<g stroke="{col}" stroke-width="{max(0.5, S.px(Z0) * 0.16):.2f}">' + "".join(posts) + "</g>")
        out.append(S.poly([(xa, Y1 + 0.95, za), (xa, Y1 + 1.25, za), (xb, Y1 + 1.25, zb), (xb, Y1 + 0.95, zb)], col))
        out.append(S.poly([(xa, Y1, za), (xa, Y1 + 0.25, za), (xb, Y1 + 0.25, zb), (xb, Y1, zb)], cscale(col, 0.9)))
        # urns on the corner posts
        for X, Z in ((xa, za), (xb, zb)):
            x, y = S.C(X, Y1 + 1.25, Z)
            k = S.px(Z)
            out.append(f'<path d="M {x - k * 0.35:.1f} {y:.1f} L {x - k * 0.45:.1f} {y - k * 0.5:.1f} Q {x:.1f} {y - k * 1.3:.1f} {x + k * 0.45:.1f} {y - k * 0.5:.1f} L {x + k * 0.35:.1f} {y:.1f} Z" fill="{col}"/>')
    return "".join(out)


def ch_water_tank(S, X, Y, Z, R=2.4):
    """Classic rooftop water tower: timber barrel on a steel frame, conical cap, lit on the sunward side."""
    x, yb = S.C(X, Y, Z)
    k = S.px(Z)
    w = R * k
    leg = 3.6 * k
    bh = 4.6 * k
    fog = S.fog(Z)
    wood = cmix("#8A5A3E", CH_HAZE, fog)
    dark = cmix("#3A2630", CH_HAZE, fog)
    lit = cmix("#E8A870", CH_HAZE, fog)
    gid = S.gid("tank")
    S.defs.append(lg(gid, [(0, lit), (0.3, wood), (1, dark)], round(x - w, 1), 0, round(x + w, 1), 0, units="userSpaceOnUse"))
    out = [f'<g stroke="{dark}" stroke-width="{max(0.5, k * 0.18):.2f}">'
           f'<line x1="{x - w * 0.8:.1f}" y1="{yb:.1f}" x2="{x - w * 0.7:.1f}" y2="{yb - leg:.1f}"/><line x1="{x + w * 0.8:.1f}" y1="{yb:.1f}" x2="{x + w * 0.7:.1f}" y2="{yb - leg:.1f}"/>'
           f'<line x1="{x:.1f}" y1="{yb:.1f}" x2="{x:.1f}" y2="{yb - leg:.1f}"/>'
           f'<line x1="{x - w * 0.8:.1f}" y1="{yb:.1f}" x2="{x + w * 0.7:.1f}" y2="{yb - leg:.1f}" stroke-width="{max(0.4, k * 0.1):.2f}"/>'
           f'<line x1="{x + w * 0.8:.1f}" y1="{yb:.1f}" x2="{x - w * 0.7:.1f}" y2="{yb - leg:.1f}" stroke-width="{max(0.4, k * 0.1):.2f}"/></g>']
    yt = yb - leg
    out.append(f'<rect x="{x - w:.1f}" y="{yt - bh:.1f}" width="{2 * w:.1f}" height="{bh:.1f}" fill="url(#{gid})"/>')
    out.append(f'<path d="M {x - w:.1f} {yt:.1f} Q {x:.1f} {yt + w * 0.25:.1f} {x + w:.1f} {yt:.1f}" fill="none" stroke="{dark}" stroke-width="{max(0.4, k * 0.12):.2f}"/>')
    hoops = "".join(f'<path d="M {x - w:.1f} {yt - bh * s:.1f} Q {x:.1f} {yt - bh * s + w * 0.25:.1f} {x + w:.1f} {yt - bh * s:.1f}"/>' for s in (0.22, 0.5, 0.78))
    out.append(f'<g fill="none" stroke="{dark}" stroke-width="{max(0.35, k * 0.1):.2f}" opacity="0.8">{hoops}</g>')
    out.append(f'<path d="M {x - w * 1.08:.1f} {yt - bh:.1f} L {x:.1f} {yt - bh - w * 0.95:.1f} L {x + w * 1.08:.1f} {yt - bh:.1f} Z" fill="url(#{gid})"/>')
    out.append(f'<path d="M {x - w * 1.08:.1f} {yt - bh:.1f} L {x:.1f} {yt - bh - w * 0.95:.1f}" stroke="#FFE0B0" stroke-width="{max(0.4, k * 0.1):.2f}" opacity="0.8"/>')
    out.append(f'<line x1="{x:.1f}" y1="{yt - bh - w * 0.95:.1f}" x2="{x:.1f}" y2="{yt - bh - w * 1.3:.1f}" stroke="{dark}" stroke-width="{max(0.4, k * 0.1):.2f}"/>')
    return "".join(out)


def ch_building(S, tiers, seed):
    """Tiers bottom -> top; drawn top first because the lower, nearer tier hides the foot of the set-back above it."""
    return "".join(ch_tier(S, t, seed + i * 17) for i, t in reversed(list(enumerate(tiers))))


def ch_cylinder_grad(S, Xc, Zc, R, Y, lit_c, mid_c, dark_c, refl_c, fog, uid):
    """Horizontal gradient that shades a vertical cylinder lit from the left-ahead (the setting sun)."""
    C = S.C
    a0 = math.atan2(-(Xc - CH_XC), -Zc)
    D = math.hypot(Xc - CH_XC, Zc)
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


def ch_ring(S, Xc, Zc, Y, rfun, n=40, R=17.0):
    """Projected front half of a horizontal ring with radius rfun(psi) at height Y, left to right."""
    a0 = math.atan2(-(Xc - CH_XC), -Zc)
    D = math.hypot(Xc - CH_XC, Zc)
    lim = math.acos(min(0.999, R / D))
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
    a0 = math.atan2(-(Xc - CH_XC), -Zc)
    lim = math.acos(17.0 / math.hypot(Xc - CH_XC, Zc))
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
    if X1 < CH_XC:
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
    sg = -1 if Xc > CH_XC else 1          # the hull side that faces the camera
    E, tip = Xc + sg * Wd, Xc + sg * 0.8
    side = [(E, 0, Zs), (E, 2.3, Zs), (E, 2.3, bow - 7), (tip, 2.6, bow), (tip, 0.4, bow - 2), (E - sg * 0.6, 0, bow - 8)]
    out.append(S.poly(side, "#D8D4E0"))
    out.append(S.poly([(E, 0, Zs), (E, 0.8, Zs), (E, 0.8, bow - 6), (tip, 1.0, bow - 1.2), (tip, 0.4, bow - 2), (E - sg * 0.6, 0, bow - 8)], "#24385A"))
    out.append(S.poly([(E, 2.0, Zs), (E, 2.3, Zs), (E, 2.3, bow - 7), (tip, 2.6, bow), (tip, 2.3, bow)], "#F6F2EC"))
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
        d = "".join(d_rel([(float(a), float(b)), (float(c), float(e))], False) for a, b, c, e in segs)
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
def ch_flag(x, y, k, seed=0):
    """Small US flag on a rooftop staff, rippling in the evening breeze."""
    w, h = 2.6 * k, 1.5 * k
    out = [f'<g transform="translate({x:.1f} {y:.1f})">']
    for i in range(7):
        y0 = h * i / 7
        out.append(f'<path d="M 0 {y0:.2f} Q {w * 0.3:.2f} {y0 - h * 0.12:.2f} {w * 0.55:.2f} {y0:.2f} T {w:.2f} {y0:.2f} L {w:.2f} {y0 + h / 7:.2f} Q {w * 0.75:.2f} {y0 + h / 7 + h * 0.12:.2f} {w * 0.55:.2f} {y0 + h / 7:.2f} T 0 {y0 + h / 7:.2f} Z" fill="{"#C8303A" if i % 2 == 0 else "#F6F0E6"}"/>')
    out.append(f'<rect x="0" y="0" width="{w * 0.42:.2f}" height="{h * 4 / 7:.2f}" fill="#24345E"/></g>')
    return "".join(out)


def ch_tc_landmark(S, X0, X1, Z0, Z1):
    """Near north-bank landmark: glazed white terra cotta, a two-storey arcade on the river walk, paired windows
    between continuous piers, medallion frieze, deep cornice, balustrade with urns, a flag on the corner."""
    t = dict(X0=X0, X1=X1, Z0=Z0, Z1=Z1, Y0=1.5, Y1=50.0, mat="tc", base="#F4E8D4", fh=3.9, bay=3.8, base_h=9.5,
             arcade=True, piers=True, piers_full=False, pair=True, attic=3.4, cornice_d=1.5, cornice_h=2.1, balustrade=True,
             lit=0.3, margin=1.6)
    out = [ch_building(S, [t], 92)]
    x, y = S.C(X0 + 3, 51.3, Z0 + 16)
    _, yt = S.C(X0 + 3, 57.2, Z0 + 16)
    out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{yt:.1f}" stroke="#3A3040" stroke-width="1.1"/>'
               f'<line x1="{x - 0.4:.1f}" y1="{y:.1f}" x2="{x - 0.4:.1f}" y2="{yt:.1f}" stroke="#FFE2B8" stroke-width="0.5"/>')
    out.append(ch_flag(x, yt + 0.5, S.px(Z0 + 16) * 1.2))
    return "".join(out)


def ch_jewelers(S, X0, X1, Z0, Z1):
    """Terra-cotta tower on Wacker with a set-back crown, four corner turrets and a domed temple on top."""
    cx, cz = (X0 + X1) / 2, (Z0 + Z1) / 2
    out = []
    tiers = [dict(X0=X0, X1=X1, Z0=Z0, Z1=Z1, Y0=8, Y1=80, mat="tc", base="#E9D3AE", lit=0.28, bay=3.0, fh=3.8, piers=True, base_h=6, cornice_d=0.9),
             dict(X0=X0 + 5, X1=X1 - 5, Z0=Z0 + 5, Z1=Z1 - 5, Y0=80, Y1=93, mat="tc", base="#E9D3AE", lit=0.3, bay=3.0, fh=3.8, base_h=1.0, cornice_d=0.6)]
    R = 7.0
    fog = S.fog(cz)
    u = S.gid("dome")
    ch_cylinder_grad(S, cx, cz, R, 100, "#FFF0D0", "#D8BC9C", "#8E7A86", "#A08EA0", fog, u)
    ring = lambda Y, r: ch_ring(S, cx, cz, Y, lambda p: r, n=24, R=r)
    out.append(f'<polygon points="{P(ring(93, R) + ring(105, R)[::-1])}" fill="url(#{u})"/>')
    a0 = math.atan2(-(cx - CH_XC), -cz)
    for i in range(-3, 4):
        psi = a0 + i * 0.42
        p1 = S.C(cx + R * math.sin(psi), 95, cz + R * math.cos(psi))
        p2 = S.C(cx + R * math.sin(psi), 103, cz + R * math.cos(psi))
        out.append(f'<line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}" stroke="#4A3A44" stroke-width="{S.px(cz) * 1.4:.1f}" opacity="0.65"/>')
    out.append(f'<polygon points="{P(ring(105, R + 0.8) + ring(106.5, R + 0.8)[::-1])}" fill="url(#{u})"/>')
    dome = []
    for j in range(8):
        a = j / 8 * math.pi / 2
        b = (j + 1) / 8 * math.pi / 2
        dome.append(f'<polygon points="{P(ring(106.5 + R * 0.95 * math.sin(a), R * math.cos(a) + 0.01) + ring(106.5 + R * 0.95 * math.sin(b), R * math.cos(b) + 0.01)[::-1])}"/>')
    out.append(f'<g fill="url(#{u})">' + "".join(dome) + "</g>")
    lx, ly = S.C(cx, 106.5 + R * 0.95, cz)
    _, ly2 = S.C(cx, 106.5 + R * 0.95 + 4, cz)
    out.append(f'<line x1="{lx:.1f}" y1="{ly:.1f}" x2="{lx:.1f}" y2="{ly2:.1f}" stroke="#D8BC9C" stroke-width="{S.px(cz) * 0.8:.1f}"/>')
    out.append(ch_building(S, tiers, 77))
    for tx, tz in ((X0 + 5, Z0 + 5), (X1 - 5, Z0 + 5)):
        ut = S.gid("tur")
        ch_cylinder_grad(S, tx, tz, 2.0, 98, "#FFF0D0", "#D8BC9C", "#8E7A86", "#A08EA0", fog, ut)
        rr = lambda Y, r: ch_ring(S, tx, tz, Y, lambda p: r, n=12, R=r)
        out.append(f'<polygon points="{P(rr(93, 2.0) + rr(100, 2.0)[::-1])}" fill="url(#{ut})"/>')
        out.append(f'<polygon points="{P(rr(100, 2.0) + rr(102.5, 1.2)[::-1])}" fill="url(#{ut})"/>')
        p = S.C(tx, 104, tz)
        q = S.C(tx, 102.5, tz)
        out.append(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" stroke="#D8BC9C" stroke-width="1"/>')
    return "".join(out)


def ch_water_reflections(S, water):
    """Each river face mirrored in the water (Y -> -Y), fading with depth, flecked with its lit windows."""
    out = []
    for Z0, quad, col, litp in sorted(S.refl, key=lambda r: -r[0]):
        mq = [(X, -Y, Z) for X, Y, Z in quad]
        pts = [S.C(*q) for q in mq]
        ys = [p[1] for p in pts]
        if min(ys) > 444:
            continue
        gid = S.gid("rf")
        S.defs.append(lg(gid, [(0, col, 0.7), (0.5, col, 0.42), (1, col, 0.08)], 0, round(min(ys), 1), 0, round(min(max(ys), 520), 1), units="userSpaceOnUse"))
        out.append(f'<polygon points="{P(pts)}" fill="url(#{gid})"/>')
        rnd = random.Random(int(Z0 * 7 + quad[0][0]))
        X = quad[0][0]
        Y0, Y1 = quad[0][1], quad[1][1]
        Za, Zb = quad[0][2], quad[3][2]
        for _ in range(int(30 * litp * min(1.0, 400 / Z0) + 2)):
            Z = rnd.uniform(Za, Zb)
            Y = rnd.uniform(Y0 + 2, Y1)
            x, y = S.C(X, -Y, Z)
            k = S.px(Z)
            out.append(f'<rect x="{x - k * 0.5:.1f}" y="{y:.1f}" width="{k * 1.1:.1f}" height="{max(0.6, k * 0.35):.1f}" fill="{rnd.choice(LIT_WIN)}" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>')
    # the mirror image is broken into horizontal ripples: a shared clip of ragged strokes, finer toward the horizon
    rnd = random.Random(77)
    rows = ([], [])
    y = 283.0
    k = 0
    while y < 444:
        h = 0.45 + (y - 282) * 0.013
        x = rnd.uniform(-20, 0)
        sc = 0.35 + (y - 282) / 200
        while x < 600:
            L_ = rnd.uniform(8, 70) * sc
            rows[k % 2].append(f"M{x:.0f} {y:.1f}h{L_:.0f}v{h * rnd.uniform(0.6, 1.2):.1f}h{-L_:.0f}z")
            x += L_ + rnd.uniform(1, 5) * sc
        y += h * rnd.uniform(1.15, 1.9)
        k += 1
    body = "".join(out)
    cid = S.gid("water")
    S.defs.append(f'<clipPath id="{cid}"><polygon points="{S.p(water)}"/></clipPath>')
    res = [f'<g clip-path="url(#{cid})"><g opacity="0.35">{body}</g>']
    # two interleaved sets of ripples, nudged apart sideways, so mirrored edges wobble like real water
    for j, dx in enumerate((-1.3, 1.3)):
        rid = S.gid("rip")
        S.defs.append(f'<clipPath id="{rid}"><path d="{"".join(rows[j])}"/></clipPath>')
        res.append(f'<g clip-path="url(#{rid})"><g transform="translate({dx} 0)">{body}</g></g>')
    return "".join(res) + "</g>"


def chicago():
    from figures import person
    u = "ch"
    S = ChiScene()
    C = S.C
    out = []
    S.defs.append(lg(f"{u}-sky", [(0, "#2A3A70"), (0.22, "#4A5490"), (0.4, "#8A7AAE"), (0.52, "#D296A0"), (0.6, "#F4B58A"),
                                  (0.635, "#FCD69A"), (0.66, "#FDE5B4"), (1, "#FDE5B4")]))
    S.defs.append(lg(f"{u}-river", [(0, "#FBD9A0"), (0.06, "#F0B88C"), (0.25, "#A48AA4"), (0.6, "#4E5A80"), (1, "#25304E")], 0, 282, 0, 444, units="userSpaceOnUse"))
    S.defs.append(lg(f"{u}-haze", [(0, CH_HAZE, 0), (0.7, "#F8CC9C", 0.5), (1, "#FCD8A4", 0.0)], 0, 220, 0, 296, units="userSpaceOnUse"))
    S.defs.append(lg(f"{u}-walk", [(0, "#9A8478"), (1, "#5E4C50")], 0, 300, 0, 444, units="userSpaceOnUse"))
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    sx, sy = 276, 240
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
    rnd = random.Random(9)
    far = []
    for i in range(30):
        X = rnd.uniform(-600, 600)
        Z = rnd.uniform(1900, 2600)
        w = rnd.uniform(25, 60)
        h = rnd.uniform(30, 150)
        if -260 < X < 120:
            h *= 0.35
        far.append((Z, X + CH_XC, w, h))
    for Z, X, w, h in sorted(far, reverse=True):
        out.append(S.poly([(X - w / 2, 0, Z), (X - w / 2, h, Z), (X + w / 2, h, Z), (X + w / 2, 0, Z)], cmix("#A98EAC", CH_HAZE, 0.35)))
        if rnd.random() < 0.5:
            out.append(S.poly([(X - w / 2, h, Z), (X - w / 2, h + 0.6 * h / 10, Z), (X - w / 2 + w * 0.15, h + 0.6 * h / 10, Z), (X - w / 2 + w * 0.15, h, Z)], cmix("#FFD8B0", CH_HAZE, 0.3), ' opacity="0.6"'))
    out.append(ch_willis(S))

    # ---- the city, far to near (built first: its river faces are mirrored in the water)
    items = []
    Lb = [  # south bank, above Wacker Drive
        (1700, [dict(X0=-150, X1=-46, Z0=1600, Z1=1700, Y0=0, Y1=60, mat="stone", base="#B89A8A", lit=0.3)]),
        (1200, [dict(X0=-170, X1=-62, Z0=1200, Z1=1400, Y0=0, Y1=96, mat="glass", base="#6A7090", lit=0.08),
                dict(X0=-160, X1=-72, Z0=1210, Z1=1390, Y0=96, Y1=122, mat="glass", base="#6A7090", lit=0.08)]),
        (920, [dict(X0=-130, X1=-62, Z0=920, Z1=1160, Y0=8, Y1=70, mat="brick", base="#9A5A48", lit=0.3, bay=4)]),
        (700, [dict(X0=-140, X1=-62, Z0=700, Z1=880, Y0=8, Y1=62, mat="brick", base="#8E4E40", lit=0.35, bay=3.5)]),
        (492, [dict(X0=-140, X1=-62, Z0=492, Z1=660, Y0=8, Y1=118, mat="stone", base="#CDB8A0", lit=0.25, bay=4, piers=True),
               dict(X0=-130, X1=-72, Z0=500, Z1=650, Y0=118, Y1=128, mat="stone", base="#CDB8A0", lit=0.2, bay=4, base_h=1.0)]),
        (385, [dict(X0=-120, X1=-62, Z0=385, Z1=452, Y0=8, Y1=62, mat="brick", base="#9C5844", lit=0.32, bay=3.2, fh=3.6, tanks=[(-78, 420)])]),
    ]
    for Zk, tiers in Lb:
        items.append((Zk, ch_building(S, tiers, int(Zk))))
    items.append((318, ch_jewelers(S, -104, -62, 318, 372)))
    # tall glass tower on Wacker: its shaded east wall mirrors the sunlit north bank
    items.append((172, ch_building(S, [dict(X0=-150, X1=-66, Z0=172, Z1=232, Y0=8, Y1=196, mat="glass", base="#3E5A7A", lit=0.05, mull=1.6),
                                       dict(X0=-144, X1=-72, Z0=178, Z1=226, Y0=196, Y1=232, mat="glass", base="#3E5A7A", lit=0.05, mull=1.6),
                                       dict(X0=-136, X1=-80, Z0=184, Z1=220, Y0=232, Y1=244, mat="dark", base="#30364A", lit=0.0)], 175)))
    items.append((244, ch_building(S, [dict(X0=-130, X1=-64, Z0=244, Z1=292, Y0=8, Y1=40, mat="brick", base="#8E5446", lit=0.3, bay=3.2, fh=3.7, tanks=[(-70, 270)])], 244)))
    # the near limestone block: shops on Wacker, proud piers, a heavy cornice under a balustrade
    items.append((90, ch_building(S, [dict(X0=-118, X1=-60, Z0=90, Z1=146, Y0=8, Y1=50, mat="stone", base="#DDAE80", lit=0.34, bay=3.4, fh=3.9,
                                            piers=True, base_h=6.5, attic=2.6, cornice_d=1.2, cornice_h=1.9, balustrade=True, margin=1.4)], 90)))
    Rb = [  # north bank
        (1300, [dict(X0=36, X1=160, Z0=1300, Z1=1450, Y0=0, Y1=92, mat="brick", base="#B07860", lit=0.3, bay=5)]),
        (1000, [dict(X0=40, X1=110, Z0=920, Z1=1150, Y0=0, Y1=74, mat="stone", base="#D0B494", lit=0.25, bay=4)]),
        (700, [dict(X0=38, X1=96, Z0=700, Z1=860, Y0=0, Y1=105, mat="glass", base="#5E7E80", lit=0.06)]),
        (492, [dict(X0=40, X1=92, Z0=492, Z1=552, Y0=1.5, Y1=212, mat="dark", base="#24242E", lit=0.04, mull=1.6, fh=3.6)]),
        (320, [dict(X0=36, X1=72, Z0=320, Z1=380, Y0=1.5, Y1=22, mat="stone", base="#D8C8B0", lit=0.3, bay=3.5)]),
    ]
    for Zk, tiers in Rb:
        items.append((Zk, ch_building(S, tiers, int(Zk) + 3)))
    items.append((440, ch_corncob(S, 86, 440, 7)))
    items.append((410, ch_corncob(S, 51, 410, 8)))
    # glass tower behind the landmark (fills the top right with sunset glass)
    items.append((200, ch_building(S, [dict(X0=100, X1=170, Z0=200, Z1=300, Y0=1.5, Y1=260, mat="glass", base="#5A7894", lit=0.05, mull=1.6)], 231)))
    # brick loft block with shopfronts on the river and water tanks on the roof
    items.append((170, ch_building(S, [dict(X0=36, X1=96, Z0=170, Z1=296, Y0=1.5, Y1=44, mat="brick", base="#A65E48", lit=0.32, bay=3.2, fh=3.8,
                                            base_h=5.5, cornice_d=0.9, tanks=[(41, 214), (43, 268)], awning=("#2E5A4A", "#EFE6D2"))], 171)))
    items.append((92, ch_tc_landmark(S, 36, 104, 92, 146)))
    for k, (Zb, ppl) in enumerate(((150, 6), (300, 3), (470, 2), (680, 0), (900, 0), (1180, 0))):
        items.append((Zb - 0.5, ch_bridge(S, Zb, people=ppl, seed=k + 1, cars=2 if Zb < 700 else 0, houses=Zb < 1000)))

    # ---- river, mirrored city, glitter
    water = [(-30, 0, 2400), (30, 0, 2400), (30, 0, 30), (-30, 0, 30)]
    out.append(S.poly(water, f"url(#{u}-river)"))
    # hand-placed mirrors for the round towers, the black tower, the bridges and the Wacker wall
    S.refl.append((393, [(36, 4, 410), (36, 178, 410), (66, 178, 410), (66, 4, 410)], "#C8B4BC", 0.4))
    S.refl.append((1400, [(-160, 0, 1400), (-160, 440, 1400), (-150, 440, 1400), (-150, 0, 1400)], "#4A3E50", 0.0))
    S.refl.append((30, [(-42, 2, 47), (-42, 8, 47), (-42, 8, 700), (-42, 2, 700)], "#7A6878", 0.3))
    out.append(ch_water_reflections(S, water))
    rf = []
    for k, Zb in enumerate((150, 300, 470, 680)):
        rf.append(ch_reflect(S, [(-30, 4.4, Zb), (-30, 9.6, Zb), (30, 9.6, Zb), (30, 4.4, Zb)], "#1E2236", 10 + k, 0.55))
    out.append("".join(rf))
    refl = []
    rnd = random.Random(3)
    # warm column of sun-glitter
    for i in range(190):
        Z = 46 * (1.022 ** i)
        if Z > 2200:
            break
        _, y = C(0, 0, Z)
        Xs = (sx - 300) * Z / S.f + CH_XC
        x = C(Xs + rnd.uniform(-3.5, 3.5) * (Z / 300) ** 0.25, 0, Z)[0]
        w = max(1.4, S.f * rnd.uniform(1.2, 5) / Z)
        refl.append(f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{max(0.7, S.f * 0.12 / Z):.1f}" rx="0.5" fill="#FFF2C8" opacity="{rnd.uniform(0.45, 0.95):.2f}"/>')
    # ripples breaking the mirrored city: warm on the sunlit side, cool and dark elsewhere
    for i in range(260):
        Z = 46 * (1.018 ** i)
        if Z > 1000:
            break
        for _ in range(2):
            X = rnd.uniform(-29.5, 29.5)
            x, y = C(X, 0, Z)
            w = S.f * rnd.uniform(1.5, 6) / Z
            if X > 10:
                cc = rnd.choice(["#F6C88E", "#F0B07A", "#FFDCA8", "#3A3A5E"])
            else:
                cc = rnd.choice(["#7E86B0", "#9A92BA", "#2A3254", "#3A4268"])
            refl.append(f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{max(0.6, S.f * 0.09 / Z):.1f}" fill="{cc}" opacity="{rnd.uniform(0.3, 0.65):.2f}"/>')
    out.append("".join(refl))

    # ---- banks. North: dock walk at the water, the street level behind. South: the Riverwalk, its granite wall
    # with cafe arches, Wacker Drive above
    out.append(S.poly([(30, 0, 30), (30, 1.5, 30), (30, 1.5, 2400), (30, 0, 2400)], "#5A4A52"))
    out.append(S.poly([(30, 1.5, 30), (400, 1.5, 30), (400, 1.5, 2400), (30, 1.5, 2400)], "#4E4048"))
    out.append(S.poly([(30, 1.5, 30), (34, 1.5, 30), (34, 1.5, 2400), (30, 1.5, 2400)], "#9A8278"))
    out.append(S.poly([(-30, 0, 30), (-30, 2.0, 30), (-30, 2.0, 2400), (-30, 0, 2400)], "#8A7A82"))
    out.append(S.poly([(-30, 2.0, 30), (-42, 2.0, 30), (-42, 2.0, 2400), (-30, 2.0, 2400)], f"url(#{u}-walk)"))
    out.append(S.poly([(-30, 2.0, 30), (-31, 2.0, 30), (-31, 2.0, 2400), (-30, 2.0, 2400)], "#C8B0A0"))
    wall = [(-42, 2.0, 30), (-42, 8.0, 30), (-42, 8.0, 2400), (-42, 2.0, 2400)]
    out.append(S.poly(wall, ch_vgrad(S, wall, [(0, "#8A7684"), (1, "#5E5062")])))
    out.append(S.poly([(-42, 8.0, 30), (-400, 8.0, 30), (-400, 8.0, 2400), (-42, 8.0, 2400)], "#5E5058"))
    out.append(S.poly([(-42, 7.2, 30), (-42, 8.4, 30), (-42, 8.4, 2400), (-42, 7.2, 2400)], "#B89C98"))
    # granite blocks in the wall and paving joints on the walk
    pv = []
    for Z in [30 * 1.04 ** i for i in range(80)]:
        if Z > 700:
            break
        pv.append(ch_line(S, (-30.5, 2.0, Z), (-42, 2.0, Z)))
        if S.px(Z) * 1.2 > 2:
            pv.append(ch_line(S, (-42, 2.0, Z), (-42, 7.2, Z)))
    out.append('<g stroke="#3E303A" stroke-width="0.6" opacity="0.3">' + "".join(pv) + "</g>")
    courses = [(2.0, 2.6, "#4E4050", 0.5), (2.6, 3.9, "#9A8494", 0.22), (3.9, 5.2, "#7A6878", 0.18), (5.2, 6.5, "#A08A98", 0.2), (6.5, 7.2, "#6A5868", 0.25)]
    for v0, v1, cc, op in courses:
        out.append(S.poly([(-42, v0, 47), (-42, v1, 47), (-42, v1, 900), (-42, v0, 900)], cc, f' opacity="{op}"'))
    jt = Bk(S)
    for v0, v1, cc, op in courses[1:]:
        jt.line(0, (-42, v1, 47), (-42, v1, 500), "#3A2C38", 0.6, ' opacity="0.45"')
        Z = 47 + (v0 * 0.7) % 1.8
        while Z < 140:
            jt.line(0, (-42, v0, Z), (-42, v1, Z), "#3A2C38", 0.6, ' opacity="0.35"')
            Z += 1.8
    out.append(jt.svg())
    # Wacker balustrade along the top of the wall
    bal = []
    for Z in [40 * 1.012 ** i for i in range(200)]:
        if Z > 600:
            break
        if S.px(Z) * 0.6 > 1.2:
            bal.append(ch_line(S, (-42.3, 8.4, Z), (-42.3, 9.3, Z)))
    out.append(f'<g stroke="#C8AEA4" stroke-width="1">' + "".join(bal) + "</g>")
    out.append(S.poly([(-42.3, 9.3, 40), (-42.3, 9.7, 40), (-42.3, 9.7, 900), (-42.3, 9.3, 900)], "#D8BCAE"))
    # the Riverwalk 'rooms': arched cafe openings glowing in the wall under Wacker
    for Z in (49, 56.5, 64, 71.5, 79, 86.5, 94, 102, 110, 118, 126, 134, 176, 190, 212, 230, 252, 340, 400):
        W_ = 4.6
        arch = [(-42, 2.0, Z), (-42, 4.2, Z)] + [(-42, 4.2 + 2.3 * math.sin(math.pi * i / 10), Z + W_ / 2 - W_ / 2 * math.cos(math.pi * i / 10)) for i in range(11)] + [(-42, 2.0, Z + W_)]
        gid = S.gid("cafe")
        y0_, y1_ = C(-42, 6.5, Z)[1], C(-42, 2.0, Z)[1]
        S.defs.append(lg(gid, [(0, "#FFD890"), (0.6, "#F2A458"), (1, "#B8643A")], 0, round(y0_, 1), 0, round(y1_, 1), units="userSpaceOnUse"))
        out.append(S.poly(arch, f"url(#{gid})"))
        out.append(S.poly([(-42, 2.0, Z + W_), (-42, 4.2, Z + W_), (-43.2, 4.2, Z + W_), (-43.2, 2.0, Z + W_)], "#8A6A60"))
        ring = [C(*q) for q in arch[1:-1]]
        out.append(f'<polyline points="{P(ring)}" fill="none" stroke="#B8A0A0" stroke-width="{max(0.6, S.px(Z) * 0.35):.1f}"/>')
        if Z < 140 and int(Z) % 3 != 1:
            for j, dz in enumerate((1.4, 3.0)):
                x, b = C(-42.6, 2.0, Z + dz)
                hh = S.px(Z + dz) * 1.25
                out.append(f'<path d="M {x - hh * 0.22:.1f} {b:.1f} L {x - hh * 0.2:.1f} {b - hh * 0.62:.1f} Q {x:.1f} {b - hh * 0.75:.1f} {x + hh * 0.2:.1f} {b - hh * 0.62:.1f} L {x + hh * 0.22:.1f} {b:.1f} Z" fill="#5A3A34" opacity="0.8"/>'
                           f'<circle cx="{x:.1f}" cy="{b - hh * 0.86:.1f}" r="{hh * 0.13:.1f}" fill="#5A3A34" opacity="0.8"/>')
        gx, gy = C(-39, 2.0, Z + 2.3)
        out.append(glow(round(gx, 1), round(gy, 1), round(S.px(Z) * 5, 1), "#FFC878", S.gid("cg"), 0.4))

    for Zk, svg in sorted(items, key=lambda t: -t[0]):
        out.append(svg)
    out.append(f'<rect x="0" y="220" width="600" height="76" fill="url(#{u}-haze)"/>')

    # ---- near life: riverwalk railing, trees, lamps, cafe tables, people; the north-bank plaza
    near = []
    rail = []
    for Z in [36 * 1.03 ** i for i in range(120)]:
        if Z > 420:
            break
        rail.append(ch_line(S, (-30.4, 2.0, Z), (-30.4, 3.1, Z)))
    near.append((1000, f'<g stroke="#2A2230" stroke-width="0.9">' + "".join(rail) + "</g>"
                 + f'<polyline points="{P([C(-30.4, 3.1, Z) for Z in (34, 40, 60, 100, 200, 420)])}" fill="none" stroke="#2A2230" stroke-width="1.4"/>'
                 + f'<polyline points="{P([C(-30.4, 3.1, Z) for Z in (34, 40, 60, 100, 200, 420)])}" fill="none" stroke="#FFD6A8" stroke-width="0.5" opacity="0.6" transform="translate(0.6 -0.6)"/>'))
    for Z in (56, 74, 96, 122, 152):
        x, b = C(-40.4, 2.0, Z)
        near.append((Z, ch_tree(x, b, S.px(Z) * 8.5, int(Z), lit="#D8C878")))
    # festoon lights zig-zagging over the walk between the lamp posts and the wall
    fest = []
    bulbs = []
    anchors = []
    for Z in (46, 66, 88, 116, 148):
        anchors.append((-31.2, 6.1, Z))
        anchors.append((-41.8, 7.0, Z + 10))
    for (a, b) in zip(anchors[:-2], anchors[1:-1]):
        pts = []
        for i in range(13):
            s_ = i / 12
            P3 = (a[0] + (b[0] - a[0]) * s_, a[1] + (b[1] - a[1]) * s_ - 1.1 * 4 * s_ * (1 - s_), a[2] + (b[2] - a[2]) * s_)
            pts.append(C(*P3))
            if 0 < i < 12 and i % 2 == 0:
                bulbs.append((P3[2], pts[-1]))
        fest.append(f'<polyline points="{P(pts)}"/>')
    near.append((200, '<g fill="none" stroke="#2A2030" stroke-width="0.6" opacity="0.8">' + "".join(fest) + "</g>"
                 + "".join(f'<circle cx="{x:.1f}" cy="{y + 0.6:.1f}" r="{max(0.6, S.px(Z) * 0.16):.1f}" fill="#FFE6A8"/>'
                           f'<circle cx="{x:.1f}" cy="{y + 0.6:.1f}" r="{max(1.6, S.px(Z) * 0.5):.1f}" fill="#FFD890" opacity="0.3"/>' for Z, (x, y) in bulbs)))
    # ivy spilling over the Wacker balustrade
    rnd = random.Random(14)
    ivy = []
    for _ in range(90):
        Z = 47 * (1 + rnd.random() * 1.6)
        Y = 8.3 - rnd.random() ** 1.6 * 2.2
        x, y = C(-41.8, Y, Z)
        r = S.px(Z) * rnd.uniform(0.3, 0.6)
        ivy.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 0.7:.1f}" ry="{r:.1f}" fill="{rnd.choice(["#3E5A3A", "#4E6E40", "#2E4630", "#6A8A4A"])}"/>')
    near.append((210, "".join(ivy)))
    for Z in (46, 66, 88, 116, 148):
        lx, lb = C(-31.2, 2.0, Z)
        lh = S.px(Z) * 4.2
        near.append((Z, f'<line x1="{lx:.1f}" y1="{lb:.1f}" x2="{lx:.1f}" y2="{lb - lh:.1f}" stroke="#221C26" stroke-width="{max(0.7, lh * 0.035):.1f}"/>'
                     + glow(round(lx, 1), round(lb - lh, 1), round(lh * 0.5, 1), "#FFE2A0", S.gid("lamp"), 0.9)
                     + f'<circle cx="{lx:.1f}" cy="{lb - lh:.1f}" r="{lh * 0.06:.1f}" fill="#FFF4D0"/>'))
    for Z in (60, 70, 84):
        x, b = C(-39.5, 2.0, Z)
        k = S.px(Z)
        near.append((Z + 0.1, f'<line x1="{x:.1f}" y1="{b:.1f}" x2="{x:.1f}" y2="{b - k * 2.4:.1f}" stroke="#3A2E30" stroke-width="{k * 0.08:.2f}"/>'
                     f'<path d="M {x - k * 1.4:.1f} {b - k * 2.0:.1f} Q {x:.1f} {b - k * 2.9:.1f} {x + k * 1.4:.1f} {b - k * 2.0:.1f} Z" fill="#F2E4CC"/>'
                     f'<path d="M {x:.1f} {b - k * 2.55:.1f} Q {x + k * 0.8:.1f} {b - k * 2.3:.1f} {x + k * 1.4:.1f} {b - k * 2.0:.1f} L {x:.1f} {b - k * 2.0:.1f} Z" fill="#B8A090" opacity="0.6"/>'
                     f'<rect x="{x - k * 0.6:.1f}" y="{b - k * 0.8:.1f}" width="{k * 1.2:.1f}" height="{k * 0.15:.1f}" fill="#3A2E30"/>'))
    tint = ("#5A3E6A", 0.18)
    walkers = [(-31.4, 34.5, "couple", 1), (-32.4, 39, "walk", -1), (-31.0, 44, "sit", 1), (-34.0, 47, "dog_walker", -1),
               (-36.5, 52, "walk", 1), (-31.6, 55, "photo", 1), (-38.2, 60, "stand", 1), (-33.2, 66, "jog", -1),
               (-35.6, 72, "walk", 1), (-37.4, 80, "walk", -1), (-32.4, 88, "stand_back", 1), (-35.0, 98, "walk", 1),
               (-37.0, 110, "walk", -1), (-33.6, 124, "walk", 1), (-36.0, 140, "walk", -1), (-34.0, 160, "walk", 1)]
    rnd = random.Random(21)
    for i, (X, Z, pose, fc) in enumerate(walkers):
        x, b = C(X, 2.0, Z)
        hh = S.px(Z) * rnd.uniform(1.66, 1.8)
        if pose == "sit":
            x, b = C(X, 2.45, Z)
        near.append((Z, person(x, b, hh, pose, fc, None, 40 + i * 9, rim="#FFD6A0", light=1, tint=tint) if hh > 12.5 else ch_mini(x, b, hh, 40 + i * 9)))
    # north-bank plaza by the landmark: honey locusts, a lamp, people on the dock
    for X, Z in ((37.0, 84), (36.5, 72)):
        x, b = C(X, 1.5, Z)
        near.append((Z, ch_tree(x, b, S.px(Z) * 8.0, int(Z) + 5, lit="#E0CC78")))
    for i, (X, Z, pose) in enumerate(((32.2, 76, "walk"), (33.0, 88, "stand"), (31.8, 102, "walk"), (32.6, 118, "walk"), (33.2, 134, "walk"))):
        x, b = C(X, 1.5, Z)
        hh = S.px(Z) * 1.72
        near.append((Z, ch_mini(x, b, hh, 90 + i)))
    for Z, svg in sorted(near, key=lambda t: -t[0]):
        out.append(svg)
    # ---- architecture tour boat heading upriver
    out.append(ch_boat(S, -5.0, 70, 4))
    out.append(ch_gull(304, 150, 11, 0.2) + ch_gull(326, 170, 7, 0.7) + ch_gull(290, 196, 6, 0.4) + ch_gull(232, 232, 6, 0.9))
    return ch_compact(defs(*S.defs) + "\n" + "\n".join(out))


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
