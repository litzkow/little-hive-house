"""American Places, painted edition: each poster is composed like a small gouache painting — graded skies,
atmospheric depth, light direction, textured rock and water, irregular trees."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from common import BEBAS, SERIF_IT, MONO
from poster import ANTON, poster


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
    people = ""
    for px, h, c in ((150, 22, "#3B4A6B"), (162, 19, "#B8574A"), (176, 23, "#2E3A30"), (330, 21, "#5E4A7A"), (342, 16, "#E0A040")):
        y0 = 402
        people += (f'<rect x="{px - 3}" y="{y0 - h}" width="6" height="{h * 0.6:.0f}" rx="2" fill="{c}"/><circle cx="{px}" cy="{y0 - h - 3}" r="3.2" fill="#3A2A22"/>'
                   f'<rect x="{px - 2.5}" y="{y0 - h * 0.42:.0f}" width="2" height="{h * 0.42:.0f}" fill="#2A2A2A"/><rect x="{px + 0.5}" y="{y0 - h * 0.42:.0f}" width="2" height="{h * 0.42:.0f}" fill="#2A2A2A"/>')
    out.append(people)
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
        g = (f'<path d="M {x - hh * 0.12:.1f} {base - hh * 0.4:.1f} L {x - hh * 0.14:.1f} {base - hh * 0.76:.1f} Q {x:.1f} {base - hh * 0.84:.1f} {x + hh * 0.14:.1f} {base - hh * 0.76:.1f} L {x + hh * 0.12:.1f} {base - hh * 0.4:.1f} Z" fill="{col}"/>'
             f'<circle cx="{x:.1f}" cy="{base - hh * 0.89:.1f}" r="{hh * 0.085:.1f}" fill="#1A1216"/>'
             f'<path d="M {x - hh * 0.1:.1f} {base - hh * 0.42:.1f} L {x - hh * 0.07:.1f} {base:.1f} M {x + hh * 0.1:.1f} {base - hh * 0.42:.1f} L {x + hh * 0.08:.1f} {base:.1f}" stroke="#141016" stroke-width="{hh * 0.075:.1f}" stroke-linecap="round"/>')
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
    def walker(X, Z, h, col, rim, flip=1):
        x, base = C(X, 0, Z)
        k_ = C.f * h / Z / 100
        return (f'<g transform="translate({x:.1f} {base:.1f}) scale({k_ * flip:.3f} {k_:.3f})">'
                '<path d="M -9 -46 L 10 -46 L 13 -6 L 8 -6 L 4 -30 L -1 -6 L -7 -6 L -11 -44 Z" fill="#141018"/>'
                f'<path d="M -13 -86 Q 0 -94 13 -86 L 14 -46 L -12 -46 Z" fill="{col}"/>'
                '<circle cx="0" cy="-95" r="8.5" fill="#1E1418"/>'
                f'<path d="M -12 -82 Q -18 -66 -14 -50 M 12 -82 Q 18 -66 15 -50" stroke="{col}" stroke-width="6" stroke-linecap="round" fill="none"/>'
                f'<path d="M 13 -86 L 14 -46" stroke="{rim}" stroke-width="2.4" stroke-linecap="round"/><path d="M 7 -101 Q 10 -95 8 -88" stroke="{rim}" stroke-width="2" fill="none" stroke-linecap="round"/>'
                '<path d="M -8 -6 L -8 0 L -16 0 M 9 -6 L 9 0 L 16 0" stroke="#141018" stroke-width="4" stroke-linecap="round"/>'
                "</g>")
    out.append(walker(-3.6, 5.2, 1.72, "#3E4A6A", "#FF8FB8"))
    out.append(walker(-2.75, 5.2, 1.62, "#8A3A4A", "#FFD25E", flip=-1))
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


def chicago():
    u = "ch"
    C = Cam(f=560, vpy=252, eye=14)
    out = [defs(
        lg(f"{u}-sky", [(0, "#3C5C94"), (0.4, "#8A86B4"), (0.7, "#EAA88C"), (0.9, "#F8CC86"), (1, "#FBE0A6")]),
        lg(f"{u}-river", [(0, "#F8D290"), (0.12, "#D8A07A"), (0.45, "#5E6A82"), (1, "#1E2E44")], 0, 252, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-lglass", [(0, "#5E7E9E"), (1, "#2A3C54")]),
        lg(f"{u}-dark", [(0, "#0E1424", 0.5), (0.6, "#0E1424", 0.1), (1, "#0E1424", 0)], 0, 0, 0, 260, units="userSpaceOnUse"),
        lg(f"{u}-rim", [(0, "#FFD9A0", 0), (1, "#FFD9A0", 0.35)], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(300, 238, 250, "#FFE6A8", f"{u}-sun", 0.9))
    out.append('<circle cx="300" cy="236" r="16" fill="#FFF3CC"/>')
    out.append('<g fill="#F8D2A8" opacity="0.6">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="3.5"/>' for x, y, w in ((150, 110, 80), (110, 122, 50), (470, 96, 90), (520, 110, 60), (390, 150, 60))) + "</g>")
    # far skyline in the haze around the sun
    for X, Z, w, h, col in ((-150, 1500, 40, 140, "#9A8EAE"), (-90, 1700, 36, 180, "#A296B2"), (-40, 1800, 30, 120, "#A89CB6"),
                            (45, 1800, 30, 160, "#A89CB6"), (95, 1700, 40, 130, "#A296B2"), (150, 1500, 36, 190, "#9A8EAE")):
        out.append(f'<polygon points="{P(C.quad_z(Z, X - w / 2, X + w / 2, 0, h))}" fill="{col}"/>')
    # the black bundled tower with twin antennas, left of the sun
    Z = 1300
    for X0, X1, h in ((-70, -46, 330), (-46, -22, 442), (-70, -58, 400), (-34, -22, 380), (-58, -46, 410)):
        out.append(f'<polygon points="{P(C.quad_z(Z, X0, X1, 0, h))}" fill="#4A4462"/>')
    for X in (-38, -30):
        a_, b_ = C(X, 442, Z), C(X, 520, Z)
        out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#4A4462" stroke-width="1.5"/><circle cx="{b_[0]:.1f}" cy="{b_[1]:.1f}" r="1.5" fill="#FF6A6A"/>')
    # river and riverwalks
    out.append(f'<polygon points="{P([C(-34, 0, 4000), C(34, 0, 4000), C(34, 0, 30), C(-34, 0, 30)])}" fill="url(#{u}-river)"/>')
    for sgn in (-1, 1):
        out.append(f'<polygon points="{P([C(sgn * 34, 0, 4000), C(sgn * 34, 2.6, 4000), C(sgn * 34, 2.6, 30), C(sgn * 34, 0, 30)])}" fill="#4A3E46"/>')
        out.append(f'<polygon points="{P([C(sgn * 34, 2.6, 4000), C(sgn * 46, 2.6, 4000), C(sgn * 46, 2.6, 30), C(sgn * 34, 2.6, 30)])}" fill="#6E5E62"/>')
    # buildings lining the river, near to far: (side, Z0, Z1, height, colour, style)
    L = [(-1, 150, 210, 150, "#C9B79A", "stone"), (-1, 210, 300, 200, "url(#ch-lglass)", "glass"), (-1, 380, 470, 120, "#8E5A48", "brick"),
         (-1, 470, 600, 170, "#B9A88C", "stone"), (-1, 600, 800, 230, "url(#ch-lglass)", "glass"), (-1, 800, 1100, 140, "#9A8A80", "stone")]
    R = [(1, 150, 220, 120, "#7E4E3E", "brick"), (1, 260, 340, 210, "#5E7E7A", "glass"), (1, 340, 430, 140, "#C2AE90", "stone"),
         (1, 430, 560, 190, "#46607A", "glass"), (1, 560, 760, 120, "#9E6A50", "brick"), (1, 760, 1100, 170, "#8A7A70", "stone")]
    for sgn, z0, z1, h, col, style in L + R:
        X = sgn * 46
        out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, 2.6, h))}" fill="{col}"/>')
        if style == "glass":
            out.append(f'<g stroke="#B8D4E6" stroke-opacity="0.3" stroke-width="0.8">' + "".join(
                f'<line x1="{C(X, y, z0)[0]:.1f}" y1="{C(X, y, z0)[1]:.1f}" x2="{C(X, y, z1)[0]:.1f}" y2="{C(X, y, z1)[1]:.1f}"/>' for y in range(8, int(h), 4)) + "</g>")
            out.append(facade_windows(C, X, z0, z1, 6, h - 4, 4, 8, "none", int(z0) + sgn, lit_p=0.18))
        else:
            dark = {"stone": "#7A6E70", "brick": "#4A2E2A"}[style]
            out.append(facade_windows(C, X, z0 + 1, z1 - 1, 6, h - 8, 4, max(5, int((z1 - z0) / 7)), dark, int(z0) * 3 + sgn, lit_p=0.22))
            out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, h - 3, h))}" fill="#FFFFFF" opacity="0.25"/>')
        if h > 160:
            out.append(f'<polygon points="{P(C.quad_x(X + sgn * 8, z0 + (z1 - z0) * 0.2, z1 - (z1 - z0) * 0.2, h, h + 26))}" fill="{col}"/>')
        out.append(f'<polygon points="{P(C.quad_x(X, z0, z0 + 2, 2.6, h))}" fill="#000" opacity="0.2"/>')
        out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, 2.6, h))}" fill="url(#{u}-dark)"/>')
    # low riverfront buildings closer in, so nothing floats
    for sgn, z0, z1, h, col in ((-1, 70, 150, 34, "#6A4A44"), (1, 70, 150, 28, "#5A4E5A")):
        X = sgn * 46
        out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, 2.6, h))}" fill="{col}"/>')
        out.append(facade_windows(C, X, z0 + 1, z1 - 1, 5, h - 3, 4, 10, "#2A2026", int(z0) + sgn * 7, lit_p=0.4))
        out.append(f'<polygon points="{P(C.quad_x(X, z0, z1, h - 1.5, h))}" fill="#FFD9A0" opacity="0.35"/>')
    # the corncob towers on the left bank, between the blocks
    for X, Zc in ((-58, 330), (-60, 362)):
        r = 10
        cx_, base = C(X, 2.6, Zc)
        _, top = C(X, 175, Zc)
        w = C.f * r / Zc
        out.append(f'<rect x="{cx_ - w:.1f}" y="{top:.1f}" width="{2 * w:.1f}" height="{base - top:.1f}" rx="{w * 0.4:.1f}" fill="#ECE4D4"/>')
        out.append(f'<rect x="{cx_ - w:.1f}" y="{top:.1f}" width="{w * 0.6:.1f}" height="{base - top:.1f}" fill="#A8A0A0" opacity="0.5"/>')
        out.append(f'<rect x="{cx_ - w:.1f}" y="{base - (base - top) * 0.3:.1f}" width="{2 * w:.1f}" height="{(base - top) * 0.3:.1f}" fill="#6E6A72" opacity="0.55"/>')
        n = 34
        for i in range(n):
            yy = top + (base - top) * (0.03 + 0.65 * i / n)
            out.append(f'<path d="' + "".join(f'M {cx_ - w + j * w / 3:.1f} {yy:.1f} q {w / 6:.1f} {w * 0.22:.1f} {w / 3:.1f} 0 ' for j in range(6)) + '" fill="none" stroke="#857A74" stroke-width="0.9"/>')
    # bascule bridges
    for Zb, col in ((230, "#C2523E"), (420, "#4A7A66"), (720, "#C2523E")):
        deck = [C(-46, 9, Zb), C(46, 9, Zb), C(46, 7.4, Zb), C(-46, 7.4, Zb)]
        out.append(f'<polygon points="{P(deck)}" fill="#2A2A34"/>')
        sw = max(0.8, C.f * 0.45 / Zb)
        top = [C(-30 + i * 6, 14 if 0 < i < 10 else 9, Zb) for i in range(11)]
        bot = [C(-30 + i * 6, 9, Zb) for i in range(11)]
        out.append(f'<polyline points="{P(top)}" fill="none" stroke="{col}" stroke-width="{sw:.1f}"/>')
        out.append(f'<g stroke="{col}" stroke-width="{sw * 0.7:.1f}">' + "".join(
            f'<line x1="{bot[i][0]:.1f}" y1="{bot[i][1]:.1f}" x2="{top[i + 1][0]:.1f}" y2="{top[i + 1][1]:.1f}"/><line x1="{bot[i + 1][0]:.1f}" y1="{bot[i + 1][1]:.1f}" x2="{top[i + 1][0]:.1f}" y2="{top[i + 1][1]:.1f}"/>' for i in range(10)) + "</g>")
        for X in (-39, 39):
            out.append(f'<polygon points="{P(C.quad_z(Zb, X - 3.2, X + 3.2, 2.6, 17))}" fill="#E2D6C2"/>')
            out.append(f'<polygon points="{P([C(X - 3.8, 17, Zb), C(X + 3.8, 17, Zb), C(X, 21, Zb)])}" fill="#7A4A3A"/>')
            wx, wy = C(X, 13, Zb)
            out.append(f'<rect x="{wx - sw:.1f}" y="{wy:.1f}" width="{sw * 2:.1f}" height="{sw * 2:.1f}" fill="#FFD98E"/>')
        out.append(f'<polygon points="{P([C(-34, 0, Zb - 3), C(34, 0, Zb - 3), C(34, 0, Zb + 6), C(-34, 0, Zb + 6)])}" fill="#1A2230" opacity="0.35"/>')
    # riverwalk: trees and lamps
    rnd2 = random.Random(12)
    for Z in (34, 42, 52, 64, 80, 100, 125, 160, 200):
        for sgn in (-1, 1):
            X = sgn * 40
            x, b = C(X, 2.6, Z)
            hh = C.f * 9 / Z
            out.append(f'<rect x="{x - hh * 0.03:.1f}" y="{b - hh * 0.45:.1f}" width="{hh * 0.06:.1f}" height="{hh * 0.45:.1f}" fill="#2A2026"/>')
            for j in range(5):
                out.append(f'<circle cx="{x + rnd2.uniform(-0.25, 0.25) * hh:.1f}" cy="{b - hh * rnd2.uniform(0.55, 0.9):.1f}" r="{hh * rnd2.uniform(0.16, 0.26):.1f}" fill="{rnd2.choice(["#3E5A3A", "#4A6A40", "#56763E"])}"/>')
            out.append(f'<circle cx="{x + sgn * -hh * 0.12:.1f}" cy="{b - hh * 0.82:.1f}" r="{hh * 0.12:.1f}" fill="#E8B060" opacity="0.5"/>')
            lx, lb = C(sgn * 35, 2.6, Z * 1.1)
            lh = C.f * 4.5 / (Z * 1.1)
            out.append(f'<line x1="{lx:.1f}" y1="{lb:.1f}" x2="{lx:.1f}" y2="{lb - lh:.1f}" stroke="#1E1A22" stroke-width="{max(0.6, lh * 0.04):.1f}"/>')
            out.append(glow(lx, lb - lh, lh * 0.35, "#FFE2A0", f"{u}-lp{Z}{sgn + 1}", 0.85))
    out.append(f'<polygon points="{P([C(-34, 0, 30), C(-34, 2.6, 30), C(-34, 2.6, 4000), C(-34, 0, 4000)])}" fill="#2E2630" opacity="0.6"/>')
    out.append(f'<polygon points="{P([C(34, 0, 30), C(34, 2.6, 30), C(34, 2.6, 4000), C(34, 0, 4000)])}" fill="#2E2630" opacity="0.6"/>')
    # reflections of the facades and the sun's glitter path on the water
    rnd = random.Random(3)
    for i in range(160):
        Z = 32 * (1.03 ** i)
        if Z > 2000:
            break
        x, y = C(rnd.uniform(-5, 5) * (Z / 200) ** 0.3, 0, Z)
        w = max(1.2, C.f * rnd.uniform(1.5, 4.5) / Z)
        out.append(f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{max(0.6, C.f * 0.1 / Z):.1f}" rx="0.5" fill="#FFF0C0" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
    for i in range(90):
        Z = 30 * (1.035 ** i)
        X = rnd.uniform(-33, 33)
        x, y = C(X, 0, Z)
        w = C.f * rnd.uniform(1.5, 4) / Z
        col = "#E8B88A" if abs(X) < 20 else "#8A7A8A"
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{max(0.5, C.f * 0.08 / Z):.1f}" fill="{col}" opacity="0.4"/>')
    # architecture tour boat heading upriver, leaving a wake
    bz = 62
    bx, by = C(-9, 0, bz)
    k = C.f / bz / 22
    out.append(f'<path d="M {bx - 50 * k:.1f} {by + 6 * k:.1f} L {bx - 140 * k:.1f} {by + 70 * k:.1f} M {bx + 50 * k:.1f} {by + 6 * k:.1f} L {bx + 140 * k:.1f} {by + 70 * k:.1f}" fill="none" stroke="#F4E6CC" stroke-width="2.5" opacity="0.55"/>')
    out.append(f'<path d="M {bx - 40 * k:.1f} {by + 8 * k:.1f} Q {bx:.1f} {by + 40 * k:.1f} {bx + 40 * k:.1f} {by + 8 * k:.1f}" fill="#F4E6CC" opacity="0.35"/>')
    out.append(f'<g transform="translate({bx:.1f} {by:.1f}) scale({k:.3f})">'
               '<path d="M -50 -6 L 50 -6 L 46 8 L -46 8 Z" fill="#F4EFE6"/><rect x="-50" y="-8" width="100" height="4" fill="#2E4A6A"/>'
               '<rect x="-42" y="-30" width="84" height="22" fill="#F4EFE6"/><rect x="-38" y="-26" width="76" height="10" fill="#5A7A9A"/>'
               '<rect x="-46" y="-34" width="92" height="5" rx="2" fill="#2E4A6A"/><rect x="-38" y="-26" width="20" height="10" fill="#FFE0A0" opacity="0.6"/>'
               + "".join(f'<circle cx="{-34 + i * 9.5}" cy="-37.5" r="2.8" fill="{c}"/>' for i, c in enumerate(("#C9574A", "#3E6A8A", "#E0C27A", "#5A8A5A", "#B85A8A", "#E8E0D0", "#7A5A9A", "#C9574A")))
               + "</g>")
    # gulls
    out.append('<g fill="none" stroke="#3A3046" stroke-width="2" stroke-linecap="round"><path d="M 214 150 q 7 -5 13 0 q 6 -5 13 0"/><path d="M 246 166 q 5 -4 8 0 q 4 -4 8 0"/><path d="M 380 128 q 5 -4 9 0 q 4 -4 9 0"/></g>')
    return "\n".join(out)


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
