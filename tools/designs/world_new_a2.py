"""World Places, painted edition (batch A2): Athens, Dubrovnik, Prague, Budapest, Vienna, Berlin.
Each poster is composed like a small painting / vintage travel poster with its own time of day, light direction
and palette, using the same layout and painterly toolkit as world_painted.py."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from places_painted import Cam
from world_painted import (Q, cumulus, defs, figure, gulls, leaf_canopy, lerp, mix, streak_cloud, umbrella_pine, water_lines)
from poster import poster


def poly(pts, fill, extra=""):
    return f'<polygon points="{P(pts)}" fill="{fill}"{extra}/>'


def line(a, b, color, w, extra=""):
    return f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{color}" stroke-width="{w}"{extra}/>'


def cypress_tree(x, base, h, w, seed, dark="#2E3A26", mid="#45532E", lit="#8A8A48"):
    """Mediterranean cypress: a tall narrow flame of foliage, lit on the left."""
    rnd = random.Random(seed)
    n = 14
    L, R = [], []
    for i in range(n + 1):
        t = i / n
        y = base - t * h
        ww = w / 2 * math.sin(math.pi * min(1, 0.12 + t * 0.95)) ** 0.7 * (1 - t * 0.35) * rnd.uniform(0.8, 1.1)
        L.append((x - ww, y))
        R.append((x + ww * rnd.uniform(0.85, 1.1), y))
    pts = L + [(x, base - h * 1.03)] + R[::-1]
    lit_pts = [(x, base)] + L + [(x, base - h * 1.03)]
    return poly(pts, mid) + poly(lit_pts, lit, ' opacity="0.55"') + poly([(x + 1, base)] + R + [(x, base - h)], dark, ' opacity="0.6"')


def olive_leaf(x, y, ang, L, top, under, rim=None):
    """Narrow lanceolate olive leaf from (x, y) pointing at angle ang (deg)."""
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    nx, ny = -dy, dx
    w = L * 0.16
    tip = (x + dx * L, y + dy * L)
    m1 = (x + dx * L * 0.45 + nx * w, y + dy * L * 0.45 + ny * w)
    m2 = (x + dx * L * 0.45 - nx * w, y + dy * L * 0.45 - ny * w)
    d = (f'M {x:.1f} {y:.1f} Q {m1[0]:.1f} {m1[1]:.1f} {tip[0]:.1f} {tip[1]:.1f} Q {m2[0]:.1f} {m2[1]:.1f} {x:.1f} {y:.1f} Z')
    d2 = (f'M {x:.1f} {y:.1f} Q {m1[0]:.1f} {m1[1]:.1f} {tip[0]:.1f} {tip[1]:.1f} Q {(x + tip[0]) / 2:.1f} {(y + tip[1]) / 2:.1f} {x:.1f} {y:.1f} Z')
    out = f'<path d="{d}" fill="{under}"/><path d="{d2}" fill="{top}"/>'
    if rim:
        out += f'<path d="M {x:.1f} {y:.1f} Q {m1[0]:.1f} {m1[1]:.1f} {tip[0]:.1f} {tip[1]:.1f}" fill="none" stroke="{rim}" stroke-width="1.3" opacity="0.8"/>'
    return out


def olive_branch(pts, seed, wood="#4A3A2E", top="#5E6A44", under="#B4BC98", rim="#F2D08A", olives=6, leaf=(18, 30), density=1.0):
    """A twig following pts with alternate silver-backed leaves and a few olives."""
    rnd = random.Random(seed)
    out = [f'<polyline points="{P(pts)}" fill="none" stroke="{wood}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>']
    leaves, fruit = [], []
    segs = list(zip(pts, pts[1:]))
    for k, ((x1, y1), (x2, y2)) in enumerate(segs):
        base_ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
        n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 9 * density))
        for i in range(n):
            t = (i + rnd.random() * 0.5) / n
            x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            side = 1 if (i + k) % 2 else -1
            ang = base_ang + side * rnd.uniform(28, 55)
            leaves.append(olive_leaf(x, y, ang, rnd.uniform(*leaf), top if rnd.random() < 0.6 else mix(top, "#2E3A26", 0.3), under,
                                     rim if rnd.random() < 0.45 else None))
    ex, ey = pts[-1]
    a = math.degrees(math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0]))
    leaves.append(olive_leaf(ex, ey, a, leaf[1], top, under, rim))
    for _ in range(olives):
        (x1, y1), (x2, y2) = rnd.choice(segs)
        t = rnd.random()
        x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        ox, oy = x + rnd.uniform(-3, 3), y + rnd.uniform(6, 10)
        c = rnd.choice(["#3A2440", "#4A2E46", "#6A7A3A", "#2E1E2E"])
        fruit.append(f'<path d="M {x:.1f} {y:.1f} L {ox:.1f} {oy - 4:.1f}" stroke="{wood}" stroke-width="1.2"/>'
                     f'<ellipse cx="{ox:.1f}" cy="{oy:.1f}" rx="4" ry="5.2" fill="{c}"/><ellipse cx="{ox - 1.3:.1f}" cy="{oy - 1.8:.1f}" rx="1.3" ry="1.6" fill="#FFF0D0" opacity="0.7"/>')
    return "".join(out + leaves + fruit)


# ================================================================ ATHENS — the Parthenon from Filopappou Hill, golden hour
class Axo:
    """Near-axonometric projection of the Parthenon: x runs along the west front (SW corner -> NW corner),
    z along the south flank (SW -> SE), y up, all in metres."""
    def __init__(self, x0, y0, ex, ez, s):
        self.x0, self.y0, self.ex, self.ez, self.s = x0, y0, ex, ez, s

    def __call__(self, x, y, z):
        return (self.x0 + x * self.ex[0] + z * self.ez[0], self.y0 + x * self.ex[1] + z * self.ez[1] - y * self.s)


def doric_column(A, x, z, u, h=10.4, d=1.9, drums=None, dark=False, face=1.0):
    """Fluted Doric column standing at (x, z); lit from the left. drums -> broken stump of that height."""
    s = A.s
    b = A(x, 0, z)
    hh = h if drums is None else drums
    t = A(x, hh, z)
    w0 = d * s * 0.5 * face
    w1 = w0 * (0.78 if drums is None else 1 - 0.22 * hh / h)
    grad = f"{u}-colD" if dark else f"{u}-col"
    out = [f'<path d="M {b[0] - w0:.1f} {b[1]:.1f} Q {b[0] - w0 * 1.04:.1f} {(b[1] + t[1]) / 2:.1f} {t[0] - w1:.1f} {t[1]:.1f} L {t[0] + w1:.1f} {t[1]:.1f} '
           f'Q {b[0] + w0 * 1.04:.1f} {(b[1] + t[1]) / 2:.1f} {b[0] + w0:.1f} {b[1]:.1f} Z" fill="url(#{grad})"/>']
    fl = "#6A4A4A" if not dark else "#4A3438"
    for f in (-0.45, 0.05, 0.5):
        out.append(f'<line x1="{b[0] + f * w0:.1f}" y1="{b[1]:.1f}" x2="{t[0] + f * w1:.1f}" y2="{t[1]:.1f}" stroke="{fl}" stroke-width="0.8" opacity="0.35"/>')
    if drums is None:
        # echinus and abacus
        e = A(x, h + 0.55, z)
        a2 = A(x, h + 0.95, z)
        out.append(f'<path d="M {t[0] - w1:.1f} {t[1]:.1f} Q {t[0] - w1 * 1.5:.1f} {e[1] + 0.5:.1f} {e[0] - w0 * 1.25:.1f} {e[1]:.1f} L {e[0] + w0 * 1.25:.1f} {e[1]:.1f} '
                   f'Q {t[0] + w1 * 1.5:.1f} {e[1] + 0.5:.1f} {t[0] + w1:.1f} {t[1]:.1f} Z" fill="{"#C88E62" if dark else "#E8B478"}"/>')
        out.append(f'<rect x="{e[0] - w0 * 1.3:.1f}" y="{a2[1]:.1f}" width="{w0 * 2.6:.1f}" height="{e[1] - a2[1]:.1f}" fill="{"#B07A5A" if dark else "#F6D29A"}"/>')
    else:
        # broken top of the stump with drum joints
        out.append(f'<ellipse cx="{t[0]:.1f}" cy="{t[1]:.1f}" rx="{w1:.1f}" ry="{w1 * 0.3:.1f}" fill="#F8DCA8"/>')
        for k in range(1, int(hh / 1.4) + 1):
            j = A(x, k * 1.4, z)
            out.append(f'<line x1="{j[0] - w0:.1f}" y1="{j[1]:.1f}" x2="{j[0] + w0:.1f}" y2="{j[1]:.1f}" stroke="#8E6450" stroke-width="0.8" opacity="0.5"/>')
    return "".join(out)


def entablature(A, plane, a0, a1, u, tone, gap=None, triglyphs=True):
    """Architrave + frieze + cornice along the x=const (plane=('x', v)) or z=const (plane=('z', v)) face from a0 to a1."""
    kind, v = plane

    def p(a, y):
        return A(v, y, a) if kind == "x" else A(a, y, v)
    lit, mid, shd = tone
    out = []
    H0, H1, H2, H3 = 10.4 + 0.95, 12.75, 14.1, 14.75
    out.append(poly([p(a0, H0), p(a0, H1), p(a1, H1), p(a1, H0)], mid))
    out.append(poly([p(a0, H0 + 0.95), p(a0, H1), p(a1, H1), p(a1, H0 + 0.95)], lit, ' opacity="0.35"'))
    out.append(poly([p(a0, H1), p(a0, H2), p(a1, H2), p(a1, H1)], lit))
    out.append(f'<polyline points="{P([p(a0, H1 - 0.15), p(a1, H1 - 0.15)])}" fill="none" stroke="{shd}" stroke-width="1.2" opacity="0.6"/>')
    if triglyphs:
        n = int(abs(a1 - a0) / 2.15)
        for i in range(n + 1):
            a = a0 + (a1 - a0) * i / max(1, n)
            q = [p(a - 0.42, H1 + 0.08), p(a - 0.42, H2 - 0.05), p(a + 0.42, H2 - 0.05), p(a + 0.42, H1 + 0.08)]
            out.append(poly(q, shd, ' opacity="0.55"'))
    out.append(poly([p(a0, H2), p(a0, H3), p(a1, H3), p(a1, H2)], lit))
    out.append(f'<polyline points="{P([p(a0, H3), p(a1, H3)])}" fill="none" stroke="#FFF2D2" stroke-width="1.4" opacity="0.9"/>')
    out.append(f'<polyline points="{P([p(a0, H2 - 0.1), p(a1, H2 - 0.1)])}" fill="none" stroke="{shd}" stroke-width="1.6" opacity="0.75"/>')
    return "".join(out)


def parthenon(A, u):
    out = [defs(lg(f"{u}-col", [(0, "#FBE0AE"), (0.35, "#F2C688"), (0.75, "#D49A6A"), (1, "#9E6E62")], 0, 0, 1, 0),
                lg(f"{u}-colD", [(0, "#E2B080"), (0.5, "#C08A66"), (1, "#7E5A5A")], 0, 0, 1, 0))]
    W, L = 30.9, 69.5
    xs = [0.95 + i * (W - 1.9) / 7 for i in range(8)]
    zs = [0.95 + j * (L - 1.9) / 16 for j in range(17)]
    gap = range(6, 11)           # the south colonnade's missing middle (1687 explosion)
    # far: east front and north colonnade (seen from inside), darker
    out.append(entablature(A, ("z", L - 0.95), W, 0, u, ("#E0A878", "#C08A68", "#7E5450"), triglyphs=False))
    for x in xs[::-1]:
        out.append(doric_column(A, x, zs[-1], u, dark=True))
    for z in zs[::-1]:
        out.append(doric_column(A, xs[-1], z, u, dark=True))
    out.append(entablature(A, ("x", xs[-1]), L, 0, u, ("#E6AE7C", "#C48E6A", "#7E5450"), triglyphs=False))
    # the standing west wall of the cella with its great doorway, and the inner porch
    q = [A(4.5, 0, 9.5), A(4.5, 12.6, 9.5), A(26.4, 12.6, 9.5), A(26.4, 0, 9.5)]
    out.append(poly(q, "#D29C6E"))
    out.append(poly([A(13.3, 0, 9.5), A(13.3, 10, 9.5), A(17.6, 10, 9.5), A(17.6, 0, 9.5)], "#5E3A3E"))
    out.append(poly([A(13.3, 10, 9.5), A(13.3, 10.6, 9.5), A(17.6, 10.6, 9.5), A(17.6, 10, 9.5)], "#F2CC94"))
    out.append(f'<g stroke="#9E6E5A" stroke-width="0.8" opacity="0.5">' + "".join(
        line(A(4.5, y, 9.5), A(26.4, y, 9.5), "#9E6E5A", 0.8) for y in (2.4, 4.8, 7.2, 9.6, 12)) + "</g>")
    for x in [5.5 + i * 3.95 for i in range(6)]:
        out.append(doric_column(A, x, 6.4, u, h=10.4, d=1.6, dark=True))
    # broken stumps and fallen drums in the gap
    for j in gap:
        if j in (7, 10):
            out.append(doric_column(A, 0.95, zs[j], u, drums=1.6 + (j % 3) * 1.1))
    # south colonnade, far to near, then the west front, far to near
    for j in range(16, -1, -1):
        if j in gap:
            continue
        out.append(doric_column(A, 0.95, zs[j], u, face=0.95))
    for x in xs[:0:-1]:
        out.append(doric_column(A, x, 0.95, u))
    out.append(doric_column(A, 0.95, 0.95, u))
    # entablatures: south flank (broken over the gap), then the sunlit west front and its pediment
    zg0, zg1 = zs[gap[0] - 1] + 1.9, zs[gap[-1] + 1] - 1.9
    out.append(entablature(A, ("x", 0), L, zg1, u, ("#F2C48A", "#D8A070", "#8A5E56")))
    out.append(entablature(A, ("x", 0), zg0, 0, u, ("#F2C48A", "#D8A070", "#8A5E56")))
    # ragged broken ends
    for zz, sgn in ((zg0, 1), (zg1, -1)):
        out.append(poly([A(0, 11.3, zz), A(0, 14.8, zz), A(0, 13.6, zz + sgn * 1.4), A(0, 12.2, zz + sgn * 0.6)], "#D8A070"))
    out.append(entablature(A, ("z", 0), 0, W, u, ("#FFE2AE", "#F2C48A", "#A06E5A")))
    # pediment: recessed tympanum, raking cornices, the surviving corner figures
    a, b, c = A(0, 14.75, 0), A(W / 2, 18.3, 0), A(W, 14.75, 0)
    out.append(poly([a, b, c], "#D8A274"))
    out.append(poly([a, b, A(W / 2, 14.75, 0)], "#E8B888", ' opacity="0.5"'))
    for (px, py, rx, ry) in ((3.2, 15.5, 1.6, 0.8), (5.2, 15.9, 1.2, 1.1), (27.4, 15.5, 1.7, 0.8), (25.3, 15.8, 1.1, 1.0), (24, 16.2, 0.9, 1.0)):
        cx_, cy_ = A(px, py, 0)
        out.append(f'<ellipse cx="{cx_:.1f}" cy="{cy_:.1f}" rx="{rx * A.s:.1f}" ry="{ry * A.s:.1f}" fill="#F6D2A0"/>')
    for e0, e1 in ((a, b), (b, c)):
        out.append(f'<polyline points="{P([e0, e1])}" fill="none" stroke="#FFEFC8" stroke-width="3.2" stroke-linecap="round"/>')
        out.append(f'<polyline points="{P([(e0[0], e0[1] + 3), (e1[0], e1[1] + 3)])}" fill="none" stroke="#9E6E5A" stroke-width="1.2" opacity="0.6"/>')
    # crepidoma: three steps, hidden partly behind the wall later
    for k in range(3):
        y0, y1 = -0.5 * (k + 1), -0.5 * k
        out.append(poly([A(-0.5 * k, y1, -0.5 * k), A(-0.5 * k, y0, -0.5 * k), A(W + 0.5 * k, y0, -0.5 * k), A(W + 0.5 * k, y1, -0.5 * k)], "#F6D29A"))
        out.append(poly([A(-0.5 * k, y1, -0.5 * k), A(-0.5 * k, y0, -0.5 * k), A(-0.5 * k, y0, L + 0.5 * k), A(-0.5 * k, y1, L + 0.5 * k)], "#D8A072"))
    # scaffold-free but scarred: patina streaks over the west front
    return "".join(out)


def athens():
    u = "athens"
    out = [defs(
        lg(f"{u}-sky", [(0, "#5A78B4"), (0.3, "#8EA2CA"), (0.55, "#D6B8C0"), (0.72, "#F4CDA6"), (0.82, "#F8DEB0")], 0, 0, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-lyc", [(0, "#B8A2B8"), (1, "#D8BCB8")]),
        lg(f"{u}-rock", [(0, "#D8A878"), (0.5, "#B88466"), (1, "#7E6458")]),
        lg(f"{u}-wall", [(0, "#F4C98E"), (1, "#C89068")]),
        lg(f"{u}-haze", [(0, "#F8DEB0", 0), (1, "#F8DEB0", 0.8)]),
        lg(f"{u}-fg", [(0, "#6E6A3E"), (1, "#3A3A26")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(-60, 300, 420, "#FFD9A0", f"{u}-sun", 0.75))
    for x, y, w, c, o in ((170, 110, 120, "#F8D0B8", 0.7), (90, 124, 70, "#FAD8C0", 0.6), (430, 92, 100, "#E8C0C8", 0.55), (520, 112, 60, "#F0C8C0", 0.5), (330, 140, 60, "#FAE0C8", 0.6)):
        out.append(streak_cloud(x, y, w, c, o, 4.5))
        out.append(streak_cloud(x - 10, y - 3, w * 0.6, "#FFF0DC", o * 0.8, 2))
    # Hymettus far to the right, Lycabettus rising just behind the rock with its white chapel
    p_, _ = ridge_poly([(260, 240), (340, 226), (420, 218), (500, 222), (560, 214), (610, 220)], 5, amp=5, base=300, fill="#C8B0C0")
    out.append(p_)
    lyc = rough([(20, 262), (70, 236), (110, 196), (132, 172), (146, 168), (166, 186), (200, 222), (250, 252)], 9, amp=4, depth=3)
    out.append(poly(lyc + [(250, 300), (20, 300)], f"url(#{u}-lyc)"))
    out.append(poly([(146, 168), (166, 186), (200, 222), (250, 252), (250, 300), (160, 300)], "#A890A8", ' opacity="0.35"'))
    rnd = random.Random(14)
    for _ in range(26):
        x = rnd.uniform(96, 226)
        yb = (y_on(lyc, x) or 250) + rnd.uniform(4, 30)
        out.append(conifer(x, yb, rnd.uniform(5, 9), "#9A8AA0", rnd.random(), width=0.5))
    out.append('<g><rect x="139" y="160" width="12" height="9" fill="#FFF8EE"/><path d="M 138 160 L 145 154 L 152 160 Z" fill="#E8DCD8"/><rect x="149" y="152" width="3" height="10" fill="#FFF8EE"/></g>')
    # the city spreading over the plain, dissolving into haze
    rnd = random.Random(31)
    city = []
    for _ in range(420):
        x = rnd.uniform(-10, 610)
        y = rnd.uniform(244, 300) + (0 if 250 < x < 560 else 0)
        w = rnd.uniform(4, 10)
        c = rnd.choice(["#F6E8DC", "#EED8CC", "#E2C8C0", "#F8EEE4", "#D8B8B0"])
        city.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{w * 0.6:.1f}" fill="{c}"/>')
    out.append("".join(city))
    out.append(f'<rect x="0" y="230" width="600" height="72" fill="url(#{u}-haze)"/>')

    # ---- the Acropolis rock
    A = Axo(282, 247, (-3.62, -0.34), (2.55, -0.26), 5.3)
    top = rough([(52, 262), (90, 252), (150, 246), (300, 250), (450, 238), (540, 246), (575, 262)], 3, amp=3, depth=3)
    rock = [(10, 330)] + rough([(10, 330), (40, 290), (52, 262)], 4, amp=6, depth=3)[1:] + top[1:] + rough([(575, 262), (600, 300), (610, 334)], 5, amp=6, depth=3)[1:]
    rock += [(610, 360), (10, 360)]
    out.append(poly(rock, f"url(#{u}-rock)"))
    out.append(f'<clipPath id="{u}-rc"><polygon points="{P(rock)}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-rc)">'
               + streaks(170, 11, (10, 250, 610, 350), ["#8E6458", "#F2C890", "#6A5050", "#E0B080"], w=(1.5, 4), length=(10, 40), opacity=(0.25, 0.6), slant=0.2)
               + blobs(60, 12, (20, 290, 600, 350), ["#5E6A3A", "#4A5634", "#7A7A44"], r=(4, 12), opacity=(0.7, 0.95), squash=0.55)
               + "</g>")
    # Propylaea and the little Nike temple on its bastion (west end, left)
    out.append(poly([(92, 262), (92, 226), (150, 220), (150, 258)], "#D8A272"))
    out.append(poly([(150, 220), (196, 224), (196, 258), (150, 258)], "#F4C88C"))
    out.append(poly([(150, 220), (173, 210), (196, 224)], "#E8B47C"))
    out.append(f'<polyline points="150,220 173,210 196,224" fill="none" stroke="#FFF0C8" stroke-width="2"/>')
    for i in range(6):
        x = 154 + i * 7.6
        out.append(f'<rect x="{x:.1f}" y="225" width="4.2" height="30" fill="#FBE2B0"/><rect x="{x + 2.6:.1f}" y="225" width="1.6" height="30" fill="#B07E62"/>')
    out.append(f'<rect x="150" y="221" width="46" height="5" fill="#F8D8A0"/>')
    out.append(poly([(60, 286), (64, 252), (110, 248), (114, 284)], "#E8B47C"))
    out.append(poly([(110, 248), (124, 252), (122, 286), (114, 284)], "#B88060"))
    out.append(poly([(70, 252), (70, 236), (104, 233), (104, 249)], "#F4CC92"))
    out.append(poly([(70, 236), (87, 228), (104, 233)], "#F8D8A0"))
    for i in range(4):
        out.append(f'<rect x="{73 + i * 8:.1f}" y="238" width="3" height="12" fill="#FFF0CE"/>')
    out.append(f'<g stroke="#A8785E" stroke-width="0.8" opacity="0.5">' + "".join(f'<line x1="62" y1="{y}" x2="112" y2="{y - 2}"/>' for y in (258, 266, 274, 282)) + "</g>")
    # the Parthenon
    out.append(parthenon(A, u))
    # the south (Cimonian) wall along the crest, hiding the temple's feet
    wall_top = rough([(150, 250), (282, 252), (460, 236), (540, 238), (568, 252)], 21, amp=1.5, depth=3)
    wall = wall_top + [(572, 292), (460, 284), (300, 300), (150, 298)]
    out.append(poly(wall, f"url(#{u}-wall)"))
    out.append(f'<clipPath id="{u}-wc"><polygon points="{P(wall)}"/></clipPath>')
    rnd = random.Random(8)
    course = []
    for k in range(1, 12):
        yy = k * 4.2
        course.append(f'<polyline points="{P([(x, y + yy) for x, y in wall_top])}" fill="none" stroke="#A8745A" stroke-width="0.9" opacity="0.45"/>')
    for _ in range(140):
        x = rnd.uniform(150, 570)
        y = (y_on(wall_top, x) or 250) + rnd.uniform(2, 46)
        course.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{y + 4:.1f}" stroke="#A8745A" stroke-width="0.8" opacity="0.4"/>')
    out.append(f'<g clip-path="url(#{u}-wc)">' + "".join(course)
               + streaks(50, 22, (150, 250, 570, 300), ["#8A5E50", "#FFE0A8"], w=(1, 3), length=(8, 30), opacity=(0.2, 0.45))
               + poly([(500, 240), (575, 240), (575, 300), (520, 300)], "#8A5A56", ' opacity="0.25"') + "</g>")
    out.append(f'<polyline points="{P(wall_top)}" fill="none" stroke="#FFF0C8" stroke-width="2" opacity="0.85"/>')
    # buttress and the Odeon of Herodes Atticus at the foot of the slope
    ox0, oy0 = 64, 336
    out.append(poly([(ox0, oy0), (ox0, oy0 - 46), (ox0 + 124, oy0 - 50), (ox0 + 124, oy0)], "#E2A878"))
    out.append(poly([(ox0 + 124, oy0 - 50), (ox0 + 150, oy0 - 40), (ox0 + 150, oy0), (ox0 + 124, oy0)], "#A87660"))
    for row, (y0, h) in enumerate(((oy0 - 10, 16), (oy0 - 28, 13), (oy0 - 43, 9))):
        for i in range(9 if row < 2 else 12):
            n = 9 if row < 2 else 12
            x = ox0 + 8 + i * (110 / n)
            w = 110 / n * 0.5
            out.append(f'<path d="M {x:.1f} {y0:.1f} L {x:.1f} {y0 - h + w / 2:.1f} Q {x + w / 2:.1f} {y0 - h - w * 0.3:.1f} {x + w:.1f} {y0 - h + w / 2:.1f} L {x + w:.1f} {y0:.1f} Z" fill="#6E4446"/>')
            out.append(f'<path d="M {x + w * 0.7:.1f} {y0:.1f} L {x + w * 0.7:.1f} {y0 - h + w / 2:.1f} Q {x + w:.1f} {y0 - h:.1f} {x + w:.1f} {y0 - h + w / 2:.1f} L {x + w:.1f} {y0:.1f} Z" fill="#E8B080" opacity="0.6"/>')
    out.append(f'<polyline points="{ox0},{oy0 - 46} {ox0 + 124},{oy0 - 50}" fill="none" stroke="#FFE6B8" stroke-width="2"/>')
    # Plaka and Koukaki below: white houses, terracotta roofs, cypresses and pines
    out.append(f'<rect x="-10" y="320" width="620" height="124" fill="#9A8A5E"/>')
    out.append(blobs(70, 81, (-10, 320, 610, 420), ["#5E6A3A", "#6E7A44", "#4A5634"], r=(6, 16), opacity=(0.7, 0.95), squash=0.6))
    rnd = random.Random(52)
    houses = []
    for row in range(7):
        y = 340 + row * 9
        x = -10 + rnd.uniform(0, 14)
        while x < 610:
            w = rnd.uniform(14, 30) * (1 + row * 0.08)
            h = rnd.uniform(10, 20) * (1 + row * 0.06)
            wall_c = rnd.choice(["#FBF2E6", "#F6E6D2", "#FFF6EC", "#EED8C4", "#F2DCC8", "#E8C8B0"])
            houses.append(poly([(x, y), (x, y - h), (x + w, y - h), (x + w, y)], wall_c))
            houses.append(poly([(x + w * 0.62, y), (x + w * 0.62, y - h), (x + w, y - h), (x + w, y)], "#B89090", ' opacity="0.3"'))
            if rnd.random() < 0.45:
                houses.append(poly([(x - 1, y - h), (x + w * 0.5, y - h - 7), (x + w + 1, y - h)], rnd.choice(["#C8664A", "#B8584A", "#D8805A"])))
            else:
                houses.append(f'<rect x="{x:.1f}" y="{y - h - 1.5:.1f}" width="{w:.1f}" height="1.5" fill="#C8B0A0"/>')
            for wx in range(int(w / 6)):
                houses.append(f'<rect x="{x + 2.5 + wx * 6:.1f}" y="{y - h * 0.62:.1f}" width="2.4" height="3.4" fill="#5A6A8A" opacity="0.75"/>')
            if rnd.random() < 0.35:
                houses.append(f'<rect x="{x:.1f}" y="{y - h * 0.38:.1f}" width="{w * 0.7:.1f}" height="1.4" fill="#8A6A5A"/>')
            x += w + rnd.uniform(-2, 3)
        for _ in range(6):
            tx = rnd.uniform(0, 600)
            if rnd.random() < 0.5:
                houses.append(cypress_tree(tx, y + 2, rnd.uniform(22, 36), rnd.uniform(6, 9), rnd.random() * 100))
            else:
                houses.append(leaf_canopy(f"{u}-pt{row}{_}", tx, y - 10, rnd.uniform(10, 16), rnd.uniform(6, 9), rnd.randrange(999),
                                          "#2E3A26", "#4A5A34", "#8E9A4E", gold="#E8C878", n=18))
    out.append("".join(houses))
    out.append(defs(lg(f"{u}-ch", [(0, "#F8DEB0", 0.45), (1, "#F8DEB0", 0)])) + f'<rect x="-10" y="318" width="620" height="60" fill="url(#{u}-ch)"/>')
    # foreground: Filopappou rock, an olive tree, two people watching the view
    fg = rough([(-10, 404), (80, 398), (180, 410), (260, 420), (340, 430), (420, 432), (610, 418)], 33, amp=6, depth=3)
    out.append(poly(fg + [(610, 444), (-10, 444)], f"url(#{u}-fg)"))
    out.append(grass(120, 61, (-10, 404, 610, 444), ["#B8A458", "#8E8A44", "#E0C27A", "#6A6A3A"], h=(5, 14)))
    rk = rough([(-10, 420), (10, 400), (50, 392), (110, 394), (150, 410), (170, 444)], 71, amp=3, depth=2)
    out.append(poly(rk + [(-10, 444)], "#A88C78"))
    out.append(f'<clipPath id="{u}-fr"><polygon points="{P(rk + [(-10, 444)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-fr)">' + streaks(40, 72, (-10, 396, 170, 444), ["#6A5050", "#D8B898"], w=(1.5, 4), length=(6, 20), opacity=(0.3, 0.6), slant=0.6)
               + poly([(110, 394), (150, 410), (170, 444), (100, 444), (96, 400)], "#5E4A4E", ' opacity="0.45"') + "</g>")
    out.append(f'<polyline points="{P([p for p in rk if p[0] < 112])}" fill="none" stroke="#FFE0B0" stroke-width="2.4" opacity="0.85"/>')
    # two people sitting on the rock, backs to us, lit from the left; she points at the temple
    for px, c, hc, hair in ((52, "#2E4A6E", "#3A2A22", None), (84, "#C2564A", "#5A3A26", True)):
        out.append(f'<path d="M {px - 13} 398 Q {px - 15} 368 {px} 362 Q {px + 15} 368 {px + 13} 398 Z" fill="{c}"/>'
                   f'<path d="M {px + 2} 362 Q {px + 15} 368 {px + 13} 398 L {px + 5} 398 Q {px + 8} 372 {px + 2} 362 Z" fill="#1E2030" opacity="0.3"/>'
                   f'<circle cx="{px}" cy="353" r="9" fill="{hc}"/>'
                   f'<path d="M {px - 13} 396 Q {px - 15} 372 {px - 3} 363" fill="none" stroke="#FFD8A0" stroke-width="2.4" stroke-linecap="round" opacity="0.9"/>'
                   f'<path d="M {px - 7} 346 Q {px - 10} 352 {px - 8} 358" fill="none" stroke="#E8A070" stroke-width="2" stroke-linecap="round" opacity="0.8"/>')
        if hair:
            out.append(f'<path d="M {px - 8} 350 Q {px} 340 {px + 8} 350 Q {px + 10} 362 {px + 6} 368 L {px - 6} 368 Q {px - 10} 360 {px - 8} 350 Z" fill="{hc}"/>')
    out.append('<path d="M 92 368 Q 104 364 108 352 L 113 340" fill="none" stroke="#C2564A" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="114" cy="337" r="3.2" fill="#D8A07A"/>')
    out.append('<path d="M 64 380 Q 70 384 76 380" fill="none" stroke="#2E4A6E" stroke-width="5" stroke-linecap="round"/>')
    # the olive tree: gnarled trunk at the right, branches arching across the top-right corner
    out.append('<path d="M 556 444 C 552 410 566 392 548 360 C 538 340 552 316 572 300 L 584 306 C 568 324 566 342 576 362 C 590 392 582 420 590 444 Z" fill="#4A3A30"/>')
    out.append('<path d="M 556 444 C 552 410 566 392 548 360 C 538 340 552 316 572 300" fill="none" stroke="#C8A070" stroke-width="2" opacity="0.6"/>')
    out.append('<path d="M 574 302 C 590 250 600 200 612 170 L 616 180 C 606 214 600 254 584 306 Z" fill="#4A3A30"/>')
    out.append('<path d="M 612 50 C 590 60 560 70 530 86" fill="none" stroke="#4A3A30" stroke-width="7" stroke-linecap="round"/>')
    out.append(olive_branch([(612, 36), (572, 42), (536, 36), (494, 48)], 5, olives=2, leaf=(24, 36)))
    out.append(olive_branch([(560, 72), (512, 94), (472, 108), (444, 110)], 3, olives=5, leaf=(24, 38)))
    out.append(olive_branch([(612, 120), (582, 132), (556, 152), (540, 178)], 4, olives=3, leaf=(24, 36)))
    out.append(olive_branch([(600, 300), (590, 270), (596, 240)], 6, olives=2, leaf=(20, 30)))
    out.append(gulls([(250, 130, 10), (272, 140, 7), (380, 156, 8)], "#5A4A5E", 1.8))
    return "\n".join(out)



# ================================================================ DUBROVNIK — the walled town from the hill, bright afternoon
class PCam:
    """Pinhole camera at (cam_x, H, 0) pitched down by phi degrees. X right, Y up, Z forward (metres)."""
    def __init__(self, f, H, phi, cx=300, cy=300, cam_x=0.0, cam_z=0.0):
        self.f, self.H, self.cx, self.cy, self.camx, self.camz = f, H, cx, cy, cam_x, cam_z
        self.s, self.c = math.sin(math.radians(phi)), math.cos(math.radians(phi))

    def __call__(self, X, Y, Z):
        dy = Y - self.H
        Z = Z - self.camz
        zc = -dy * self.s + Z * self.c
        yc = dy * self.c + Z * self.s
        return (self.cx + self.f * (X - self.camx) / zc, self.cy - self.f * yc / zc)

    def depth(self, X, Y, Z):
        return -(Y - self.H) * self.s + (Z - self.camz) * self.c


SUN_DB = (0.55, 0.72, 0.42)          # afternoon sun from the south-west: right, high, beyond


def lit(base, n, lo="#6E5A7A", hi="#FFF6E2", amb=0.25):
    """Colour a face by its normal against the Dubrovnik sun: shade toward lo, light toward hi."""
    L = SUN_DB
    d = sum(a * b for a, b in zip(n, L)) / math.sqrt(sum(a * a for a in L))
    if d < 0.15:
        return mix(base, lo, 0.42 - d * 0.4)
    return mix(base, hi, min(0.55, (d - 0.15) * 0.75))


def inside(pt, polyg):
    x, y = pt
    c = False
    for (x1, y1), (x2, y2) in zip(polyg, polyg[1:] + polyg[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def db_ground(X, Z):
    """Old town terrain: flat around the Stradun and to the south, climbing steeply to the north walls."""
    return 5 + max(0.0, (676 - Z) / 150) ** 1.15 * 30 + max(0.0, (X - 60) / 160) * 6 * max(0.0, (676 - Z) / 150)


def db_house(C, x0, x1, z0, z1, g, h, rh, roof, wall, ridge_x, rnd, shutters=True):
    """A stone house with a terracotta gable roof, faces lit by the afternoon sun."""
    out = []
    xm, zm = (x0 + x1) / 2, (z0 + z1) / 2
    yt = g + h
    F = lambda X, Y, Z: C(X, Y, Z)
    if x1 < C.camx:
        out.append(poly([F(x1, g, z0), F(x1, yt, z0), F(x1, yt, z1), F(x1, g, z1)], lit(wall, (1, 0, 0))))
    elif x0 > C.camx:
        out.append(poly([F(x0, g, z0), F(x0, yt, z0), F(x0, yt, z1), F(x0, g, z1)], lit(wall, (-1, 0, 0))))
    front = [F(x0, g, z0), F(x0, yt, z0), F(x1, yt, z0), F(x1, g, z0)]
    fc = lit(wall, (0, 0, -1))
    out.append(poly(front, fc))
    # windows with green shutters on the near face
    fw = front[2][0] - front[1][0]
    fh = front[0][1] - front[1][1]
    if shutters and fw > 9 and fh > 7:
        floors = max(1, int(h / 3.4))
        cols = max(1, int((x1 - x0) / 5.5))
        for i in range(floors):
            for j in range(cols):
                if rnd.random() < 0.25:
                    continue
                X = x0 + (j + 0.5) * (x1 - x0) / cols
                Y = g + 2.2 + i * 3.3
                a, b = F(X - 0.7, Y + 1.6, z0), F(X + 0.7, Y, z0)
                col = "#3E6A4E" if rnd.random() < 0.55 else "#4A3A3E"
                out.append(f'<rect x="{a[0]:.1f}" y="{a[1]:.1f}" width="{max(1, b[0] - a[0]):.1f}" height="{max(1.2, b[1] - a[1]):.1f}" fill="{col}" opacity="0.85"/>')
    rlo, rhi = "#7A2E2E", "#FFC888"
    if ridge_x:
        far = [F(x0, yt, z1), F(x1, yt, z1), F(x1, yt + rh, zm), F(x0, yt + rh, zm)]
        out.append(poly(far, lit(roof, (0, 0.87, 0.5), rlo, rhi)))
        near = [F(x0, yt, z0), F(x1, yt, z0), F(x1, yt + rh, zm), F(x0, yt + rh, zm)]
        nc = lit(roof, (0, 0.87, -0.5), rlo, rhi)
        if x1 < C.camx:
            out.append(poly([F(x1, yt, z0), F(x1, yt + rh, zm), F(x1, yt, z1)], lit(wall, (1, 0, 0))))
        elif x0 > C.camx:
            out.append(poly([F(x0, yt, z0), F(x0, yt + rh, zm), F(x0, yt, z1)], lit(wall, (-1, 0, 0))))
        out.append(poly(near, nc))
        for t in (0.33, 0.66):
            a = F(x0, yt + rh * t, z0 + (zm - z0) * t)
            b = F(x1, yt + rh * t, z0 + (zm - z0) * t)
            out.append(line(a, b, mix(nc, "#5A2420", 0.35), 0.8, ' opacity="0.6"'))
        out.append(line(F(x0, yt + rh, zm), F(x1, yt + rh, zm), mix(roof, "#FFE0B0", 0.5), 1.1))
    else:
        L_ = [F(x0, yt, z0), F(xm, yt + rh, z0), F(xm, yt + rh, z1), F(x0, yt, z1)]
        R_ = [F(x1, yt, z0), F(xm, yt + rh, z0), F(xm, yt + rh, z1), F(x1, yt, z1)]
        cl, cr = lit(roof, (-0.5, 0.87, 0), rlo, rhi), lit(roof, (0.5, 0.87, 0), rlo, rhi)
        for q, c in ((L_, cl), (R_, cr)) if xm > C.camx else ((R_, cr), (L_, cl)):
            out.append(poly(q, c))
        out.append(poly([F(x0, yt, z0), F(xm, yt + rh, z0), F(x1, yt, z0)], fc))
        out.append(line(F(xm, yt + rh, z0), F(xm, yt + rh, z1), mix(roof, "#FFE0B0", 0.5), 1.1))
    out.append(line(F(x0, yt, z0), F(x1, yt, z0), "#5A3A3A", 0.8, ' opacity="0.45"'))
    return "".join(out)


def db_tower(C, cx, cz, r, y0, y1, u, k, crown=None, stone="#E8D8BC"):
    """Round fortress tower (cylinder) lit from the right, crenellated top, optional narrower crown turret."""
    gid = f"{u}-tw{k}"
    out = [defs(lg(gid, [(0, mix(stone, "#6E5A7A", 0.5)), (0.45, mix(stone, "#8A7A8A", 0.15)), (0.8, mix(stone, "#FFF6E2", 0.4)), (1, mix(stone, "#C8A890", 0.2))], 0, 0, 1, 0))]
    ring = lambda y: [C(cx + r * math.cos(a), y, cz + r * math.sin(a)) for a in [math.pi * i / 18 for i in range(37)]]
    bot, top = ring(y0), ring(y1)
    front = [p for p, a in zip(bot, range(37)) if 18 <= a <= 36]
    body = [bot[18]] + [top[i] for i in range(18, 37)] + [bot[i] for i in range(36, 17, -1)]
    xs = [p[0] for p in body]
    out.append(poly(body, f"url(#{gid})"))
    out.append(poly(top, mix(stone, "#C8B8A8", 0.3)))
    out.append(poly(ring(y1 - 0.5)[18:], "#5A4A5A", ' opacity="0.3"'))
    # merlons along the near rim
    for i in range(18, 37, 2):
        a = C(cx + r * math.cos(math.pi * i / 18), y1, cz + r * math.sin(math.pi * i / 18))
        b = C(cx + r * math.cos(math.pi * i / 18), y1 + 1.8, cz + r * math.sin(math.pi * i / 18))
        out.append(line(a, b, mix(stone, "#FFF6E2", 0.3), max(1.4, (a[1] - b[1]) * 0.9)))
    # stone courses
    for t in (0.25, 0.5, 0.75):
        y = y0 + (y1 - y0) * t
        out.append(f'<polyline points="{P(ring(y)[18:])}" fill="none" stroke="#8A7A80" stroke-width="0.7" opacity="0.4"/>')
    if crown:
        r2, h2 = crown
        out.append(db_tower(C, cx, cz, r2, y1, y1 + h2, u, k + 50, None, stone))
    return "".join(out)


def db_campanile(C, x, z, w, g, h, cap, u, stone="#EFE2C8", dome=None):
    """Square bell tower with belfry openings and a pyramidal or domed cap."""
    out = []
    x0, x1, z0, z1 = x - w / 2, x + w / 2, z - w / 2, z + w / 2
    side_x = x0 if x0 > C.camx else x1
    out.append(poly([C(side_x, g, z0), C(side_x, g + h, z0), C(side_x, g + h, z1), C(side_x, g, z1)], lit(stone, (1 if side_x == x1 else -1, 0, 0))))
    fr = [C(x0, g, z0), C(x0, g + h, z0), C(x1, g + h, z0), C(x1, g, z0)]
    out.append(poly(fr, lit(stone, (0, 0, -1))))
    for yy in (h - 6, h - 2.4):
        a, b = C(x - w * 0.18, g + yy + 2.2, z0), C(x + w * 0.18, g + yy, z0)
        out.append(f'<rect x="{a[0]:.1f}" y="{a[1]:.1f}" width="{b[0] - a[0]:.1f}" height="{b[1] - a[1]:.1f}" fill="#3A2E3A"/>')
    for yy in (h * 0.4, h * 0.7, h - 7):
        out.append(line(C(x0, g + yy, z0), C(x1, g + yy, z0), "#FFF6E2", 1, ' opacity="0.7"'))
    tip = C(x, g + h + cap, z)
    if dome:
        out.append(f'<path d="M {fr[1][0]:.1f} {fr[1][1]:.1f} Q {fr[1][0]:.1f} {tip[1] + 2:.1f} {tip[0]:.1f} {tip[1]:.1f} Q {fr[2][0]:.1f} {tip[1] + 2:.1f} {fr[2][0]:.1f} {fr[2][1]:.1f} Z" fill="{dome}"/>')
        out.append(f'<path d="M {tip[0] + 1:.1f} {tip[1]:.1f} Q {fr[2][0]:.1f} {tip[1] + 2:.1f} {fr[2][0]:.1f} {fr[2][1]:.1f}" fill="none" stroke="#FFF2D2" stroke-width="1.4" opacity="0.8"/>')
    else:
        out.append(poly([fr[1], tip, fr[2]], "#C2643E"))
        out.append(poly([tip, fr[2], C(x1, g + h, z1)], "#E8925A"))
    out.append(line(tip, (tip[0], tip[1] - 4), "#5A4A4A", 1))
    return "".join(out)


def db_dome(C, x, z, r, y0, h, u, k, col="#C8B8A8"):
    """Church dome on a drum (lead/stone grey), lit on the right."""
    gid = f"{u}-dm{k}"
    a, b = C(x - r, y0, z), C(x + r, y0, z)
    t = C(x, y0 + h, z)
    d = C(x, y0 - h * 0.45, z)
    out = [defs(lg(gid, [(0, mix(col, "#5A4A6A", 0.45)), (0.6, col), (1, mix(col, "#FFF6E2", 0.6))], 0, 0, 1, 0))]
    out.append(f'<rect x="{a[0]:.1f}" y="{a[1]:.1f}" width="{b[0] - a[0]:.1f}" height="{d[1] - a[1]:.1f}" fill="url(#{gid})"/>')
    for i in range(1, 6):
        xx = a[0] + (b[0] - a[0]) * i / 6
        out.append(f'<rect x="{xx - 0.7:.1f}" y="{a[1] + 2:.1f}" width="1.4" height="{max(1, d[1] - a[1] - 4):.1f}" fill="#3A2E3A" opacity="0.6"/>')
    out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} Q {a[0]:.1f} {t[1]:.1f} {t[0]:.1f} {t[1]:.1f} Q {b[0]:.1f} {t[1]:.1f} {b[0]:.1f} {b[1]:.1f} Z" fill="url(#{gid})"/>')
    out.append(f'<path d="M {t[0] + 2:.1f} {t[1] + 1:.1f} Q {b[0] - 1:.1f} {t[1] + 1:.1f} {b[0] - 1:.1f} {b[1] - 2:.1f}" fill="none" stroke="#FFFFFF" stroke-width="1.3" opacity="0.6"/>')
    out.append(f'<rect x="{t[0] - 1.5:.1f}" y="{t[1] - 5:.1f}" width="3" height="5" fill="{col}"/><line x1="{t[0]:.1f}" y1="{t[1] - 5:.1f}" x2="{t[0]:.1f}" y2="{t[1] - 9:.1f}" stroke="#5A4A4A" stroke-width="1"/>')
    return "".join(out)


def sail_boat(x, wl, k, sail="#FFFFFF", sail_sh="#C8D4E0", hull="#FFFFFF", flip=False):
    """Small sloop under sail, heeling a touch, with a white wake."""
    sx = -k if flip else k
    return (f'<g transform="translate({x:.1f} {wl:.1f}) scale({sx:.3f} {k:.3f})">'
            '<path d="M -40 2 Q -16 6 -6 3" fill="none" stroke="#FFFFFF" stroke-width="2.2" opacity="0.8"/>'
            '<path d="M -44 5 Q -20 10 -4 6" fill="none" stroke="#FFFFFF" stroke-width="1.4" opacity="0.5"/>'
            f'<path d="M -12 -1 L 14 -1 L 9 4 L -9 4 Z" fill="{hull}"/><path d="M -10 2.5 L 10 2.5 L 9 4 L -9 4 Z" fill="#2E4A6A"/>'
            '<line x1="0" y1="-1" x2="1.5" y2="-34" stroke="#4A4A5A" stroke-width="1.1"/>'
            f'<path d="M 2.5 -33 Q 14 -18 13 -2 L 2.5 -2 Z" fill="{sail}"/><path d="M 9 -16 Q 13 -10 13 -2 L 8 -2 Z" fill="{sail_sh}"/>'
            f'<path d="M 0 -31 Q -10 -16 -10 -3 L 0 -3 Z" fill="{sail_sh}"/>'
            '</g>')


def motorboat(x, wl, k, flip=False, col="#FFFFFF"):
    sx = -k if flip else k
    return (f'<g transform="translate({x:.1f} {wl:.1f}) scale({sx:.3f} {k:.3f})">'
            '<path d="M -8 1 Q -26 3 -46 7 M -8 2 Q -22 7 -38 12" fill="none" stroke="#FFFFFF" stroke-width="1.8" opacity="0.7"/>'
            f'<path d="M -8 -2 L 10 -2 L 6 2 L -8 2 Z" fill="{col}"/><rect x="-4" y="-5" width="7" height="3" fill="#2E4A6A"/></g>')


def dubrovnik():
    u = "dubrovnik"
    C = PCam(f=340, H=170, phi=25, cx=300, cy=300, cam_x=10, cam_z=300)
    hz = C.cy - C.f * C.s / C.c
    out = [defs(
        lg(f"{u}-sky", [(0, "#2E7AC8"), (0.55, "#7CB8E6"), (1, "#D8ECF4")], 0, 40, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#2A6EA8"), (0.3, "#1E5E9E"), (0.75, "#1E78A8"), (1, "#2A9AB0")], 0, hz, 0, 330, units="userSpaceOnUse"),
        lg(f"{u}-hill", [(0, "#6E8A4A"), (1, "#3A5434")], 0, 300, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="{hz + 2:.0f}" fill="url(#{u}-sky)"/>')
    out.append(cumulus(f"{u}-c1", 120, hz - 12, 160, 34, 3, "#FFFFFF", "#F4F8FC", "#B8CCE0", hi="#FFFFFF", hi_op=0.8, light=1))
    out.append(cumulus(f"{u}-c2", 470, hz - 18, 120, 26, 8, "#FFFFFF", "#F4F8FC", "#B8CCE0", hi="#FFFFFF", hi_op=0.8, light=1))
    out.append(cumulus(f"{u}-c3", 300, hz - 6, 90, 14, 5, "#FFFFFF", "#F4F8FC", "#C8D8E8", hi="#FFFFFF", light=1))
    out.append(f'<rect x="0" y="{hz:.1f}" width="600" height="{444 - hz:.1f}" fill="url(#{u}-sea)"/>')
    # far coast to the south-east, the Cavtat headlands in the haze
    out.append(poly(rough([(-10, hz - 8), (40, hz - 14), (90, hz - 6), (140, hz - 3), (180, hz + 0.5)], 7, amp=2, depth=3) + [(-10, hz + 1)], "#9AB4C8"))
    # sun glitter toward the south-west
    rnd = random.Random(5)
    for i in range(170):
        y = hz + 2 + rnd.random() ** 1.3 * 140
        spread = 30 + (y - hz) * 0.9
        w = rnd.uniform(3, 12) * (0.5 + (y - hz) / 120)
        x = 470 + rnd.gauss(0, spread * 0.5)
        out.append(f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{0.8 + (y - hz) / 110:.1f}" rx="0.8" fill="{rnd.choice(["#FFFFFF", "#F2FAFF", "#CFE8F6"])}" opacity="{rnd.uniform(0.35, 0.95):.2f}"/>')
    out.append(water_lines(150, 6, (0, hz + 3, 600, 330), ["#5AA8D0", "#174E86", "#8ACBE0"], w=(6, 30), h=(0.6, 1.6), opacity=(0.25, 0.6)))
    # Lokrum island: pine-dark, rocky white rim, the fort on its crest
    isl = [C(X, 0, Z) for X, Z in ((-230, 1260), (-410, 1180), (-670, 1210), (-950, 1380), (-1050, 1560), (-750, 1700), (-450, 1560))]
    xs_ = sorted(p[0] for p in isl)
    wl = xs_[-1] - xs_[0]
    by = max(p[1] for p in isl)
    top_ = rough([(xs_[0], by), (xs_[0] + wl * 0.12, by - 9), (xs_[0] + wl * 0.4, by - 15), (xs_[0] + wl * 0.62, by - 19), (xs_[0] + wl * 0.85, by - 10), (xs_[-1], by - 1)], 21, amp=3, depth=3)
    out.append(poly(top_ + [(xs_[-1], by + 2), (xs_[0], by + 2)], "#2E5A3E"))
    out.append(poly([(x, y) for x, y in top_ if x > xs_[0] + wl * 0.55] + [(xs_[-1], by + 2), (xs_[0] + wl * 0.55, by + 2)], "#1E3E2E", ' opacity="0.5"'))
    out.append(tree_line(top_, 22, ["#2A4E36", "#355E40", "#3E6A44"], density=4, hmin=4, hmax=8, xmin=xs_[0] + 4, xmax=xs_[-1] - 4, sink=3))
    out.append(f'<polyline points="{P([(xs_[0], by + 1), (xs_[-1], by + 1)])}" fill="none" stroke="#E8E4D8" stroke-width="1.6"/>')
    fx = xs_[0] + wl * 0.62
    out.append(f'<rect x="{fx - 5:.1f}" y="{by - 25:.1f}" width="10" height="7" fill="#D8D0C0"/><rect x="{fx + 1:.1f}" y="{by - 25:.1f}" width="4" height="7" fill="#9A8E86"/>')
    # Fort Lovrijenac on its cliff, beyond the Pile inlet (west, right of the town)
    lx, ly = C(285, 0, 690)
    out.append(poly(rough([(lx - 40, ly + 4), (lx - 30, ly - 22), (lx + 10, ly - 30), (lx + 50, ly - 22), (lx + 66, ly + 4)], 31, amp=3, depth=2), "#B8AC98"))
    out.append(streaks(14, 32, (lx - 30, ly - 22, lx + 56, ly), ["#8A7E70", "#E8DCC8"], w=(1, 2.5), length=(5, 14), opacity=(0.3, 0.6)))
    out.append(poly([(lx - 24, ly - 22), (lx - 20, ly - 50), (lx + 30, ly - 54), (lx + 38, ly - 26)], lit("#E8DCC4", (0, 0, -1))))
    out.append(poly([(lx + 30, ly - 54), (lx + 48, ly - 48), (lx + 52, ly - 22), (lx + 38, ly - 26)], lit("#E8DCC4", (1, 0, 0))))
    out.append(f'<path d="M {lx - 20} {ly - 50} L {lx + 30} {ly - 54} L {lx + 48} {ly - 48}" fill="none" stroke="#5A4A5A" stroke-width="1.8" stroke-dasharray="2 2"/>')
    for k in range(3):
        out.append(f'<rect x="{lx - 12 + k * 12:.1f}" y="{ly - 42:.1f}" width="2.4" height="4" fill="#4A3A4A"/>')
    out.append(f'<polyline points="{lx - 40},{ly + 4} {lx + 66},{ly + 4}" fill="none" stroke="#FFFFFF" stroke-width="2"/>')
    # the land north of the walls: the slope of Srd falling to the town, the Ploce and Pile suburbs
    shore = [(-900, 640), (-520, 630), (-330, 612), (-262, 590), (-222, 600), (0, 600), (205, 590), (238, 640), (262, 676), (330, 664), (420, 700), (900, 720)]
    land = [C(X, 0, Z) for X, Z in shore] + [C(900, db_ground(900, 330), 330), C(-900, db_ground(-900, 330), 330)]
    out.append(f'<defs>{lg(f"{u}-land", [(0, "#8E9A62"), (0.5, "#6E8448"), (1, "#4E683A")], 0, 0, 0, 1)}</defs>')
    out.append(poly(land, f"url(#{u}-land)"))
    out.append(f'<clipPath id="{u}-lc"><polygon points="{P(land)}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-lc)">' + blobs(260, 47, (-10, 230, 610, 444), ["#3E5E30", "#4E6E36", "#2E4A28", "#6E8A44"], r=(3, 9), opacity=(0.6, 0.95), squash=0.6)
               + streaks(40, 48, (-10, 260, 610, 400), ["#C8BC98", "#8E8A60"], w=(1, 3), length=(6, 18), opacity=(0.3, 0.6), slant=0.8) + "</g>")
    sh = [C(X, 0, Z) for X, Z in shore]
    out.append(f'<polyline points="{P(sh)}" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.8"/>')
    # ---- the walled town, painter-sorted
    outline = [(150, 518), (60, 524), (-60, 536), (-150, 552), (-205, 570), (-228, 612), (-238, 660), (-232, 712), (-246, 790),
               (-176, 812), (-80, 826), (20, 832), (110, 822), (170, 800), (216, 762), (232, 700), (222, 630), (196, 566)]
    rnd = random.Random(11)
    items = []
    roofs = ["#D2643A", "#C8553A", "#E07A48", "#B84E36", "#D8703E", "#CC5E3E", "#E48A50"]
    walls_c = ["#EFE2C8", "#E8D8BC", "#F2E6D0", "#E2D2B8", "#EADCC6"]
    shrunk = [(x * 0.94 + 0, 680 + (z - 680) * 0.93) for x, z in outline]
    reserved = [(-200, -168, 676, 712), (-178, -120, 744, 800), (-80, -30, 772, 812), (176, 214, 650, 690)]
    z = 528
    while z < 830:
        dz = rnd.uniform(15, 19)
        x = -240
        while x < 240:
            w = rnd.uniform(15, 25)
            xc, zc = x + w / 2, z + dz / 2
            x += w
            if not inside((xc, zc), shrunk) or abs(zc - 682) < 9.5:
                continue
            if any(a <= xc <= b and c <= zc <= d for a, b, c, d in reserved):
                continue
            g = db_ground(xc, zc)
            h = rnd.uniform(10, 17)
            gap = 3.2 if zc < 676 else 1.8
            ridge_x = rnd.random() < (0.35 if zc < 676 else 0.6)
            span = (dz - 2) if ridge_x else (w - gap)
            items.append((C.depth(xc, g, zc), db_house(C, xc - w / 2 + gap / 2, xc + w / 2 - gap / 2, zc - dz / 2 + 1, zc + dz / 2 - 1, g, h, span * 0.28,
                                                        rnd.choice(roofs), rnd.choice(walls_c), ridge_x, rnd)))
        z += dz
    # houses and gardens on the slope outside the walls
    rnd2 = random.Random(19)
    for _ in range(700):
        X = rnd2.uniform(-560, 560)
        Z = rnd2.uniform(420, 700)
        if inside((X, Z), [(x * 1.06, 676 + (z - 676) * 1.08) for x, z in outline]):
            continue
        if Z > (y_on(shore, X) or 600) - 14 or (240 < X < 340 and Z > 620):
            continue
        g = db_ground(X, Z) * 0.9
        if rnd2.random() < 0.35:
            continue
        w = rnd2.uniform(8, 13)
        d = rnd2.uniform(7, 10)
        items.append((C.depth(X, g, Z), db_house(C, X - w / 2, X + w / 2, Z - d / 2, Z + d / 2, g, rnd2.uniform(4, 6.5), (d if rnd2.random() < 0.5 else w) * 0.42,
                                                 rnd2.choice(roofs), rnd2.choice(walls_c), rnd2.random() < 0.5, rnd2, shutters=False)))
        if rnd2.random() < 0.3:
            tx, ty = C(X + rnd2.choice((-1, 1)) * (w / 2 + 4), g, Z - d / 2 - 2)
            items.append((C.depth(X, g, Z - d) , cypress_tree(tx, ty, rnd2.uniform(14, 24), rnd2.uniform(4, 6), rnd2.random() * 99, "#22361E", "#33502A", "#7E9A4A")))
    # landmarks: bell tower and St Blaise at the Stradun's east end, the cathedral, the Jesuit church, the Franciscan tower
    items.append((C.depth(-184, 5, 690), db_campanile(C, -184, 690, 7, 5, 30, 5, u, dome="#B8B0A0")))
    items.append((C.depth(-160, 5, 700) + 1, db_house(C, -176, -146, 696, 714, 5, 14, 5, "#B8B0A8", "#F2E6D0", False, rnd, shutters=False)
                   + db_dome(C, -161, 704, 5, 22, 7, u, 1)))
    items.append((C.depth(-150, 6, 772), db_house(C, -176, -124, 752, 796, 6, 18, 7, "#C8553A", "#F2E6D0", True, rnd, shutters=False)
                   + db_dome(C, -150, 772, 8, 26, 11, u, 2)))
    items.append((C.depth(-55, 14, 792), db_house(C, -80, -32, 776, 808, 14, 20, 8, "#D2643A", "#F4E8D2", True, rnd, shutters=False)))
    items.append((C.depth(195, 5, 670), db_campanile(C, 195, 670, 7, 5, 26, 8, u)))
    # the Stradun: a pale limestone strip catching the light
    sx0, sx1 = -186, 210
    items.append((C.depth(0, 5, 682) + 0.5, poly([C(sx0, 5, 675), C(sx1, 5, 675), C(sx1, 5, 689), C(sx0, 5, 689)], "#FFF4DC")))
    # city walls: short prisms around the outline, then the round towers
    cyc = outline + outline[:1]
    for (ax, az), (bx, bz) in zip(cyc, cyc[1:]):
        L = math.hypot(bx - ax, bz - az)
        n = max(1, int(L / 12))
        nx, nz = -(bz - az) / L, (bx - ax) / L          # outward normal
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            px0, pz0 = ax + (bx - ax) * t0, az + (bz - az) * t0
            px1, pz1 = ax + (bx - ax) * t1, az + (bz - az) * t1
            g0 = db_ground(px0, pz0)
            g1 = db_ground(px1, pz1)
            sea = pz0 > 700 or px0 > 205 or px0 < -228
            top0 = (g0 + 11) if not sea else 22
            top1 = (g1 + 11) if not sea else 22
            b0, b1 = (g0 - 7, g1 - 7) if not sea else (0, 0)
            T = 5.0
            o0, o1 = (px0 + nx * T, pz0 + nz * T), (px1 + nx * T, pz1 + nz * T)
            face = []
            camv = (C.camx - (px0 + px1) / 2, C.camz - (pz0 + pz1) / 2)
            if nx * camv[0] + nz * camv[1] > 0:          # outer face toward us
                q = [C(o0[0], b0, o0[1]), C(o0[0], top0, o0[1]), C(o1[0], top1, o1[1]), C(o1[0], b1, o1[1])]
                fc = lit("#E2D2B6", (nx, 0, nz))
                face.append(poly(q, fc))
                face.append(line(q[1], q[2], mix(fc, "#FFFFFF", 0.4), 2.2, ' stroke-dasharray="1.6 1.6"'))
                face.append(poly([q[0], (q[0][0], q[0][1] - (q[0][1] - q[1][1]) * 0.18), (q[3][0], q[3][1] - (q[3][1] - q[2][1]) * 0.18), q[3]], "#6E5A6A", ' opacity="0.2"'))
                for t_ in (0.3, 0.5, 0.7):
                    face.append(line((q[0][0], q[0][1] + (q[1][1] - q[0][1]) * t_), (q[3][0], q[3][1] + (q[2][1] - q[3][1]) * t_), "#9A8A80", 0.7, ' opacity="0.45"'))
                face.append(line(q[0], q[1], mix(fc, "#6E5A6A", 0.3), 0.8, ' opacity="0.5"'))
            else:
                q = [C(px0, top0 - 6, pz0), C(px0, top0, pz0), C(px1, top1, pz1), C(px1, top1 - 6, pz1)]
                face.append(poly(q, lit("#E2D2B6", (-nx, 0, -nz))))
            face.append(poly([C(px0, top0, pz0), C(o0[0], top0, o0[1]), C(o1[0], top1, o1[1]), C(px1, top1, pz1)], "#F6EAD2"))
            items.append((C.depth((px0 + px1) / 2, top0, (pz0 + pz1) / 2) - (2 if nz < 0 else 0), "".join(face)))
    g_m = db_ground(150, 518)
    items.append((C.depth(152, g_m, 512) - 6, db_tower(C, 152, 512, 15, g_m - 14, g_m + 26, u, 1, crown=(8, 8))))
    items.append((C.depth(-252, 0, 620), db_tower(C, -252, 620, 18, 0, 18, u, 2)))
    items.append((C.depth(-252, 0, 792), db_tower(C, -252, 792, 16, 0, 24, u, 3)))
    items.append((C.depth(228, 0, 744), db_tower(C, 228, 744, 11, 0, 26, u, 4)))
    items.append((C.depth(-200, 20, 566) - 3, db_tower(C, -204, 566, 8, 12, 40, u, 5)))
    for _, s in sorted(items, key=lambda t: -t[0]):
        out.append(s)
    # the old port: breakwater, moored boats, a tour boat
    pts = [C(-300, 0, 760), C(-290, 3, 820), C(-280, 3, 822), C(-290, 0, 760)]
    out.append(poly(pts, "#D8CCB4"))
    for X, Z, c in ((-275, 735, "#FFFFFF"), (-282, 745, "#F2E6D0"), (-276, 756, "#FFFFFF"), (-270, 726, "#C8E0F0")):
        bx, by_ = C(X, 0, Z)
        out.append(f'<path d="M {bx - 5:.1f} {by_:.1f} L {bx + 5:.1f} {by_:.1f} L {bx + 3:.1f} {by_ + 2.5:.1f} L {bx - 4:.1f} {by_ + 2.5:.1f} Z" fill="{c}"/>')
    # boats on the open sea: a sloop, a couple of launches with wakes
    out.append(sail_boat(*C(70, 0, 1350), 1.0))
    out.append(sail_boat(*C(-300, 0, 2600), 0.55, flip=True))
    out.append(motorboat(*C(-120, 0, 1000), 0.9))
    out.append(motorboat(*C(180, 0, 1700), 0.6, flip=True))
    # foreground: the scrubby slope of Srd below us, a terrace wall with bougainvillea, an umbrella pine framing the right
    hill = rough([(-10, 372), (60, 380), (130, 392), (220, 402), (300, 406), (380, 402), (460, 392), (540, 380), (610, 370)], 41, amp=4, depth=3)
    out.append(poly(hill + [(610, 444), (-10, 444)], f"url(#{u}-hill)"))
    out.append(f'<polyline points="{P(hill)}" fill="none" stroke="#C8C080" stroke-width="2" opacity="0.6"/>')
    out.append(f'<clipPath id="{u}-hc"><polygon points="{P(hill + [(610, 444), (-10, 444)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-hc)">'
               + blobs(50, 42, (-10, 372, 610, 444), ["#4E6E3A", "#5E7E44", "#3A5634", "#7E944E"], r=(6, 16), opacity=(0.6, 0.95), squash=0.55)
               + blobs(26, 44, (-10, 380, 610, 444), ["#C8BCA0", "#B0A488", "#D8CCB0"], r=(3, 8), opacity=(0.7, 0.95), squash=0.5)
               + grass(160, 45, (-10, 376, 610, 444), ["#C8B86A", "#8E9A50", "#E0D08A", "#5E7A3A"], h=(5, 13))
               + "</g>")
    rnd = random.Random(43)
    for x in (128, 150, 468, 486, 506):
        out.append(cypress_tree(x, (y_on(hill, x) or 400) + 8, rnd.uniform(50, 76), rnd.uniform(10, 13), rnd.random() * 99, "#1E321C", "#2E4A28", "#8AA250"))
    # terrace wall with bougainvillea in the bottom-left corner
    out.append(poly([(-10, 414), (200, 406), (212, 444), (-10, 444)], "#E2D2B0"))
    out.append(poly([(200, 406), (212, 444), (196, 444), (188, 410)], "#B8A688"))
    out.append(f'<g stroke="#A8987E" stroke-width="1" opacity="0.7">' + "".join(
        f'<line x1="-10" y1="{414 + k * 6}" x2="{200 + k * 1.6:.0f}" y2="{406 + k * 6}"/>' for k in range(1, 6)) + "</g>")
    out.append(f'<g stroke="#A8987E" stroke-width="1" opacity="0.6">' + "".join(
        f'<line x1="{x + (k % 2) * 12}" y1="{412 - x * 0.04 + k * 6}" x2="{x + (k % 2) * 12}" y2="{418 - x * 0.04 + k * 6}"/>' for k in range(5) for x in range(10, 190, 26)) + "</g>")
    out.append(f'<polyline points="-10,414 200,406" fill="none" stroke="#FFF6E0" stroke-width="2.4"/>')
    out.append(leaf_canopy(f"{u}-bg", 60, 404, 76, 20, 77, "#6A1844", "#C2307A", "#F06AAE", gold="#FFC0E0", n=80, r=(0.2, 0.4)))
    out.append(leaf_canopy(f"{u}-bl", 30, 428, 40, 18, 79, "#2E4A26", "#3E6A2E", "#7EA048", n=30, r=(0.2, 0.4)))
    out.append(dots(50, 78, (0, 390, 140, 424), "#FFD8EC", r=(1, 2), opacity=(0.6, 0.95)))
    out.append(umbrella_pine(588, 444, 300, 190, 61, lean=-0.16, dark="#1E3222", mid="#2E4A2C", lit="#7E9A4A", gold="#C8D070", trunk="#4A3A30", trunk_lit="#C89A6A"))
    out.append(gulls([(330, 118, 10), (350, 128, 7), (200, 100, 8)], "#2A4A6A", 1.8))
    return "\n".join(out)


# ================================================================ PRAGUE — on Charles Bridge at dawn, looking west to the Lesser Town towers
def baroque_saint(x, base, h, seed, body="#2E2A38", rim="#F6B8A8", rim_side=-1, kind=0, halo=False):
    """Blackened sandstone baroque statue on a tall pedestal, seen in silhouette with a dawn rim light.
    x, base: foot of the pedestal (on the parapet top); h: total height in px. kind picks the pose."""
    rnd = random.Random(seed)
    s = h / 100.0
    rs = rim_side
    out = [f'<g transform="translate({x:.1f} {base:.1f}) scale({s:.3f})">']
    # pedestal: plinth, die with a carved panel, cornice
    out.append(f'<path d="M -15 0 L -15 -6 L -12 -8 L -12 -38 L -15 -40 L -15 -44 L 15 -44 L 15 -40 L 12 -38 L 12 -8 L 15 -6 L 15 0 Z" fill="{body}"/>')
    out.append(f'<rect x="-8" y="-33" width="16" height="20" rx="1.5" fill="none" stroke="{mix(body, rim, 0.35)}" stroke-width="1.2" opacity="0.8"/>')
    out.append(f'<path d="M {15 * rs} -44 L {15 * rs} -40 L {12 * rs} -38 L {12 * rs} -8 L {15 * rs} -6 L {15 * rs} 0" fill="none" stroke="{rim}" stroke-width="2" opacity="0.85"/>')
    out.append(f'<path d="M -15 -44 L 15 -44" stroke="{rim}" stroke-width="1.6" opacity="0.6"/>')
    # the figure: a robed saint, contrapposto, cloak swinging
    sway = rnd.uniform(-2.5, 2.5)
    robe = (f'M -13 -44 Q -15 -56 {-10 + sway} -66 Q {-12 + sway} -78 {-9 + sway} -88 Q {-4 + sway} -92 {sway} -92 Q {4 + sway} -92 {9 + sway} -88 '
            f'Q {12 + sway} -78 {10 + sway} -66 Q {16 + sway * 0.5} -56 14 -44 Z')
    out.append(f'<path d="{robe}" fill="{body}"/>')
    out.append(f'<path d="M {sway - 2.6:.1f} -92 L {sway - 2.2:.1f} -95 L {sway + 2.2:.1f} -95 L {sway + 2.6:.1f} -92 Z" fill="{body}"/>')
    out.append(f'<ellipse cx="{sway:.1f}" cy="-99" rx="4" ry="4.8" fill="{body}"/>')
    # a sash / cloak hem across the body
    out.append(f'<path d="M {-10 + sway} -70 Q {sway} -62 {12 + sway * 0.6} -52" fill="none" stroke="{mix(body, rim, 0.3)}" stroke-width="1.6" opacity="0.8"/>')
    # cloak flare on one side
    fl = rnd.choice((-1, 1))
    out.append(f'<path d="M {fl * 9} -78 Q {fl * 20} -64 {fl * 16} -46 L {fl * 10} -46 Q {fl * 14} -62 {fl * 6} -76 Z" fill="{body}"/>')
    if kind == 0:      # holding a tall cross
        out.append(f'<path d="M {sway + 9} -76 L {sway + 14} -84" stroke="{body}" stroke-width="3.4" stroke-linecap="round"/>'
                   f'<rect x="{sway + 13:.1f}" y="-112" width="2.6" height="44" fill="{body}"/><rect x="{sway + 8:.1f}" y="-104" width="12.6" height="2.6" fill="{body}"/>')
        if rs > 0:
            out.append(f'<rect x="{sway + 15:.1f}" y="-112" width="1" height="44" fill="{rim}" opacity="0.8"/>')
    elif kind == 1:    # arm raised in blessing, gaze up
        out.append(f'<path d="M {sway - 7} -84 L {sway - 15} -92 L {sway - 13} -106" fill="none" stroke="{body}" stroke-width="3.8" stroke-linecap="round" stroke-linejoin="round"/>'
                   f'<ellipse cx="{sway - 13.2:.1f}" cy="-108" rx="2.2" ry="3" fill="{body}"/>'
                   f'<path d="M {sway - 15} -92 L {sway - 13} -106" stroke="{rim}" stroke-width="1.2" opacity="0.8" transform="translate(-1.6 0)"/>')
    elif kind == 2:    # carrying a child / book against the chest, with a putto at the foot
        out.append(f'<ellipse cx="{sway + 4:.1f}" cy="-74" rx="7" ry="5.5" fill="{body}"/>'
                   f'<circle cx="{sway + 7:.1f}" cy="-81" r="3.4" fill="{body}"/>'
                   f'<path d="M 4 -44 Q 2 -52 8 -56 Q 14 -54 13 -44 Z" fill="{body}"/><circle cx="9" cy="-59" r="3" fill="{body}"/>')
    else:              # a bishop with crozier and mitre
        out.append(f'<path d="M {sway - 3.4} -102 L {sway} -111 L {sway + 3.4} -102 Z" fill="{body}"/>'
                   f'<rect x="{sway - 14:.1f}" y="-104" width="2.4" height="58" fill="{body}"/>'
                   f'<path d="M {sway - 12.8} -104 Q {sway - 13} -112 {sway - 7} -111 Q {sway - 4} -108 {sway - 7} -105" fill="none" stroke="{body}" stroke-width="2.4"/>')
    # rim light on the figure's lit edge
    if rs < 0:
        out.append(f'<path d="M -13 -44 Q -15 -56 {-10 + sway} -66 Q {-12 + sway} -78 {-9 + sway} -88" fill="none" stroke="{rim}" stroke-width="2" opacity="0.85" stroke-linecap="round"/>'
                   f'<path d="M {sway - 3.6} -103 Q {sway - 4.6} -99 {sway - 3} -95" fill="none" stroke="{rim}" stroke-width="1.6" opacity="0.85"/>')
    else:
        out.append(f'<path d="M 14 -44 Q {16 + sway * 0.5} -56 {10 + sway} -66 Q {12 + sway} -78 {9 + sway} -88" fill="none" stroke="{rim}" stroke-width="2" opacity="0.85" stroke-linecap="round"/>'
                   f'<path d="M {sway + 3.6} -103 Q {sway + 4.6} -99 {sway + 3} -95" fill="none" stroke="{rim}" stroke-width="1.6" opacity="0.85"/>')
    # drapery folds
    for k in range(3):
        xx = -6 + k * 6 + sway * 0.5
        out.append(f'<path d="M {xx:.1f} -48 Q {xx + 2:.1f} -60 {xx + sway * 0.4:.1f} -72" fill="none" stroke="{mix(body, rim, 0.25)}" stroke-width="1" opacity="0.6"/>')
    if halo:          # St John of Nepomuk: the halo of five gilded stars
        for i in range(5):
            a = math.radians(-160 + i * 35)
            sx_, sy_ = sway + 11 * math.cos(a), -100 + 11 * math.sin(a)
            pts = []
            for j in range(10):
                rr = 3.6 if j % 2 == 0 else 1.5
                aa = math.radians(-90 + j * 36)
                pts.append((sx_ + rr * math.cos(aa), sy_ + rr * math.sin(aa)))
            out.append(poly(pts, "#FFD86A"))
        out.append(f'<path d="M {sway - 11} -100 A 11 11 0 0 1 {sway + 11} -100" fill="none" stroke="#E8B84A" stroke-width="0.9" opacity="0.8"/>')
    out.append("</g>")
    return "".join(out)


def bridge_lamp(x, base, h, u, k, glow_col="#FFD9A0"):
    """Baroque lamp on the parapet: slim post, scrolled bracket, a hexagonal lantern still lit at dawn."""
    s = h / 100.0
    return (glow(f"{x:.1f}", f"{base - h * 0.86:.1f}", f"{h * 0.32:.1f}", glow_col, f"{u}-lg{k}", 0.75)
            + f'<g transform="translate({x:.1f} {base:.1f}) scale({s:.3f})">'
            '<path d="M -4 0 L 4 0 L 3 -8 L 1.6 -10 L 1.6 -70 L 3 -73 L -3 -73 L -1.6 -70 L -1.6 -10 L -3 -8 Z" fill="#2A2632"/>'
            '<path d="M 0 -60 Q 7 -64 5 -72 M 0 -60 Q -7 -64 -5 -72" fill="none" stroke="#2A2632" stroke-width="1.6"/>'
            '<path d="M -7 -76 L 7 -76 L 9 -92 L -9 -92 Z" fill="#FFE2A8"/><path d="M -2 -76 L 2 -76 L 2.6 -92 L -2.6 -92 Z" fill="#FFF6DA"/>'
            '<path d="M -7 -76 L 7 -76 L 9 -92 L -9 -92 Z M -2.5 -76 L -3.2 -92 M 2.5 -76 L 3.2 -92" fill="none" stroke="#2A2632" stroke-width="1.4"/>'
            '<path d="M -11 -92 L 11 -92 L 0 -101 Z" fill="#2A2632"/><circle cx="0" cy="-103" r="2" fill="#2A2632"/>'
            '</g>')


def prague():
    u = "prague"
    C = Cam(f=560, cx=300, vpy=332, eye=1.6)
    out = [defs(
        lg(f"{u}-sky", [(0, "#6C7AB0"), (0.28, "#A496C0"), (0.5, "#E2AEBA"), (0.68, "#F6C6AE"), (0.8, "#FADCC0")], 0, 40, 0, 340, units="userSpaceOnUse"),
        lg(f"{u}-deck", [(0, "#B49AA0"), (0.3, "#9A7E8A"), (1, "#5E4A5A")], 0, 332, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-par", [(0, "#8A6E7A"), (1, "#4A3A4A")]),
        lg(f"{u}-twr", [(0, "#E8C0A8"), (0.5, "#C89C98"), (1, "#8A7084")]),
        lg(f"{u}-roof", [(0, "#6A6E8E"), (1, "#3E405E")], 0, 0, 1, 0),
        lg(f"{u}-hz", [(0, "#FBE2CE", 0), (0.5, "#FBE2CE", 0.85), (1, "#F2D2C8", 0)]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    # the sun has just risen behind us: pink light on the undersides of the clouds
    for x, y, w, c, o in ((120, 96, 130, "#F6C2B8", 0.75), (60, 110, 80, "#FAD6C4", 0.6), (440, 84, 150, "#F0B4BC", 0.7), (540, 104, 70, "#F8CCC0", 0.6),
                          (300, 132, 90, "#FBDCCB", 0.55), (230, 116, 60, "#F6C8C0", 0.5)):
        out.append(streak_cloud(x, y, w, c, o, 5))
        out.append(streak_cloud(x - 14, y - 4, w * 0.55, "#FFEEE4", o * 0.8, 2.2))
        out.append(streak_cloud(x + 8, y + 4, w * 0.7, "#B89ABC", o * 0.5, 1.8))
    # Petrin hill on the left with its lattice lookout tower, wooded, in haze
    pet = rough([(-10, 238), (40, 200), (90, 176), (140, 182), (200, 210), (250, 236)], 61, amp=4, depth=3)
    out.append(poly(pet + [(250, 300), (-10, 300)], "#B49AB4"))
    out.append(tree_line(pet, 62, ["#A28AA8", "#9A84A2", "#AC94B0"], density=3, hmin=6, hmax=11, xmin=0, xmax=240, sink=4))
    tx, ty = 96, 178
    out.append(f'<g fill="none" stroke="#8E7A9E" stroke-width="1.6"><path d="M {tx - 7} {ty} L {tx} {ty - 52} L {tx + 7} {ty}"/>'
               f'<path d="M {tx - 5} {ty - 14} L {tx + 5} {ty - 14} M {tx - 3} {ty - 30} L {tx + 3} {ty - 30}"/>'
               f'<path d="M {tx - 7} {ty} L {tx + 5} {ty - 14} M {tx + 7} {ty} L {tx - 5} {ty - 14}"/></g>'
               f'<rect x="{tx - 3.5}" y="{ty - 50}" width="7" height="4" fill="#8E7A9E"/><line x1="{tx}" y1="{ty - 52}" x2="{tx}" y2="{ty - 60}" stroke="#8E7A9E" stroke-width="1.4"/>')
    # Prague Castle on its ridge to the right: the long palace and St Vitus Cathedral rising out of it
    ridge = rough([(330, 252), (380, 214), (430, 196), (520, 190), (610, 192)], 63, amp=3, depth=3)
    out.append(poly(ridge + [(610, 300), (330, 300)], "#A890AC"))
    # the palace front: long and pale, rows of windows catching the dawn
    pal_y0, pal_y1 = 192, 166
    out.append(poly([(392, 212), (392, pal_y1 + 6), (610, pal_y1), (610, 196)], "#F2D2C8"))
    out.append(poly([(392, pal_y1 + 6), (398, pal_y1 - 2), (610, pal_y1 - 8), (610, pal_y1)], "#B08A9E"))
    rows = [(pal_y1 + 10, pal_y1 + 4), (pal_y1 + 17, pal_y1 + 11), (pal_y1 + 24, pal_y1 + 18)]
    win = []
    for r_, (ya, yb) in enumerate(rows):
        for i in range(36):
            xx = 398 + i * 6
            dy_ = (xx - 392) / 218 * -6
            win.append(f'<rect x="{xx:.1f}" y="{ya + dy_:.1f}" width="2.4" height="3.4" fill="#8E7090"/>')
    out.append("".join(win))
    # St Vitus: nave roof, twin west spires and the great south tower with its green copper helmet
    vx = 448
    out.append(poly([(vx - 34, 170), (vx - 30, 150), (vx + 46, 148), (vx + 52, 168)], "#7E7298"))
    out.append(poly([(vx - 30, 150), (vx + 8, 128), (vx + 46, 148)], "#5E5880"))
    out.append(f'<polyline points="{vx - 30},150 {vx + 8},128 {vx + 46},148" fill="none" stroke="#F6C8C0" stroke-width="1.4" opacity="0.7"/>')
    for fx in (vx - 22, vx - 4):             # the two neo-gothic west spires
        out.append(poly([(fx - 7, 170), (fx - 7, 124), (fx + 7, 124), (fx + 7, 170)], "#857AA0"))
        out.append(poly([(fx - 7, 124), (fx, 88), (fx + 7, 124)], "#5E5880"))
        out.append(poly([(fx - 7, 124), (fx, 88), (fx - 1, 124)], "#F2C2BE", ' opacity="0.55"'))
        out.append(f'<line x1="{fx - 7}" y1="170" x2="{fx - 7}" y2="124" stroke="#F6C8C0" stroke-width="1.4" opacity="0.8"/>')
        for k in (132, 146, 158):
            out.append(f'<rect x="{fx - 2}" y="{k}" width="4" height="8" rx="2" fill="#4A4268"/>')
        for px_ in (fx - 7, fx + 7):
            out.append(f'<path d="M {px_ - 1.5} 124 L {px_} 114 L {px_ + 1.5} 124 Z" fill="#5E5880"/>')
    gx = vx + 30                              # the great south tower
    out.append(poly([(gx - 9, 172), (gx - 9, 124), (gx + 9, 124), (gx + 9, 172)], "#8A7EA2"))
    out.append(f'<line x1="{gx - 9}" y1="172" x2="{gx - 9}" y2="124" stroke="#F6C8C0" stroke-width="1.6" opacity="0.8"/>')
    out.append(f'<rect x="{gx - 3}" y="132" width="6" height="12" rx="3" fill="#4A4268"/><circle cx="{gx}" cy="154" r="4" fill="#E8C070"/>')
    out.append(f'<path d="M {gx - 10} 124 Q {gx - 12} 116 {gx - 6} 112 Q {gx - 9} 106 {gx - 4} 102 Q {gx - 5} 98 {gx} 94 Q {gx + 5} 98 {gx + 4} 102 '
               f'Q {gx + 9} 106 {gx + 6} 112 Q {gx + 12} 116 {gx + 10} 124 Z" fill="#6E9E8E"/>')
    out.append(f'<path d="M {gx - 10} 124 Q {gx - 12} 116 {gx - 6} 112 Q {gx - 9} 106 {gx - 4} 102 Q {gx - 5} 98 {gx} 94 L {gx - 1} 124 Z" fill="#B8D8C0" opacity="0.5"/>')
    out.append(f'<line x1="{gx}" y1="94" x2="{gx}" y2="86" stroke="#5E5880" stroke-width="1.4"/>')
    # Lesser Town roofs and the green dome of St Nicholas, half drowned in morning mist
    rnd = random.Random(64)
    roofs = []
    for _ in range(70):
        x = rnd.uniform(150, 610)
        y = rnd.uniform(226, 262) + (0 if x < 300 else -6)
        w = rnd.uniform(10, 24)
        c = rnd.choice(["#D8A0A0", "#C88E98", "#E2B0AA", "#BE8494"])
        roofs.append(poly([(x, y), (x + w * 0.5, y - w * 0.32), (x + w, y), (x + w, y + 10), (x, y + 10)], c))
        roofs.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="10" fill="#EAD0D0" opacity="0.65"/>')
    out.append("".join(roofs))
    nx_, ny_ = 214, 214
    out.append(f'<rect x="{nx_ - 16}" y="{ny_}" width="32" height="26" fill="#E8C8C8"/>')
    out.append(f'<path d="M {nx_ - 18} {ny_} Q {nx_ - 18} {ny_ - 30} {nx_} {ny_ - 32} Q {nx_ + 18} {ny_ - 30} {nx_ + 18} {ny_} Z" fill="#7EA898"/>')
    out.append(f'<path d="M {nx_ - 18} {ny_} Q {nx_ - 18} {ny_ - 30} {nx_} {ny_ - 32} L {nx_ - 4} {ny_} Z" fill="#B8D8C8" opacity="0.6"/>')
    out.append(f'<rect x="{nx_ - 3}" y="{ny_ - 44}" width="6" height="12" fill="#E8C8C8"/><path d="M {nx_ - 5} {ny_ - 44} Q {nx_} {ny_ - 54} {nx_ + 5} {ny_ - 44} Z" fill="#7EA898"/>')
    out.append(f'<rect x="{nx_ + 26}" y="{ny_ - 18}" width="12" height="44" fill="#E2C2C4"/>'
               f'<path d="M {nx_ + 24} {ny_ - 18} Q {nx_ + 26} {ny_ - 30} {nx_ + 32} {ny_ - 36} Q {nx_ + 38} {ny_ - 30} {nx_ + 40} {ny_ - 18} Z" fill="#7EA898"/>'
               f'<rect x="{nx_ + 29}" y="{ny_ - 12}" width="6" height="9" rx="3" fill="#8E7090"/>')
    rnd = random.Random(66)
    fac = []
    for row, (y0, fade) in enumerate(((270, 0.55), (292, 0.7), (314, 0.85))):
        x = -10 + rnd.uniform(0, 10)
        while x < 610:
            w = rnd.uniform(16, 30)
            h = rnd.uniform(22, 34)
            col = mix(rnd.choice(["#E8B8A8", "#F2D2B8", "#D8A8B0", "#F0C8A0", "#E2C0C8", "#F6DCC8"]), "#FBE6DC", 1 - fade)
            fac.append(poly([(x, y0), (x, y0 - h), (x + w, y0 - h), (x + w, y0)], col))
            fac.append(poly([(x - 1, y0 - h), (x + w / 2, y0 - h - w * 0.35), (x + w + 1, y0 - h)], mix("#B87E8A", "#FBE6DC", 1 - fade)))
            for wy in range(2):
                for wx in range(int(w / 7)):
                    fac.append(f'<rect x="{x + 3 + wx * 7:.1f}" y="{y0 - h + 6 + wy * 9:.1f}" width="2.6" height="4.2" fill="{mix("#7E6488", "#FBE6DC", 1 - fade)}"/>')
            x += w + rnd.uniform(0, 4)
        fac.append(mist(300, y0 - 4, 420, 16, "#FFF0EA", f"{u}-fm{row}", 0.7))
    out.append("".join(fac))
    out.append(f'<rect x="0" y="196" width="600" height="96" fill="url(#{u}-hz)"/>')
    out.append(mist(160, 262, 260, 26, "#FFF0EA", f"{u}-m1", 0.8) + mist(470, 240, 220, 22, "#FFF0EA", f"{u}-m2", 0.75))

    # ---- the Lesser Town Bridge Towers at the far end of the bridge
    ZG = 110.0
    # Judith Tower (left, lower, Romanesque)
    jt = [C(-13, 0, ZG + 4), C(-13, 21, ZG + 4), C(-4.5, 21, ZG + 4), C(-4.5, 0, ZG + 4)]
    out.append(poly(jt, f"url(#{u}-twr)"))
    out.append(poly([C(-13.8, 21, ZG + 4), C(-8.75, 31, ZG + 8), C(-3.7, 21, ZG + 4)], f"url(#{u}-roof)"))
    out.append(poly([C(-13.8, 21, ZG + 4), C(-8.75, 31, ZG + 8), C(-9.6, 21, ZG + 4)], "#B6A2BE", ' opacity="0.45"'))
    for (yy, xx) in ((15, -9.8), (15, -7.4), (9, -8.6)):
        a_, b_ = C(xx - 0.5, yy + 2, ZG + 4), C(xx + 0.5, yy, ZG + 4)
        out.append(f'<rect x="{a_[0]:.1f}" y="{a_[1]:.1f}" width="{b_[0] - a_[0]:.1f}" height="{b_[1] - a_[1]:.1f}" rx="1" fill="#4A3A52"/>')
    # the gate of 1411 between them, crenellated
    g0, g1 = -4.6, 4.6
    gate = [C(g0, 0, ZG), C(g0, 12.5, ZG), C(g1, 12.5, ZG), C(g1, 0, ZG)]
    out.append(poly(gate, "#D8AEA6"))
    a0, a1 = C(-2.6, 0, ZG), C(2.6, 7.2, ZG)
    out.append(f'<path d="M {a0[0]:.1f} {a0[1]:.1f} L {a0[0]:.1f} {a1[1] + 8:.1f} Q {a0[0]:.1f} {a1[1]:.1f} {(a0[0] + a1[0]) / 2:.1f} {a1[1] - 4:.1f} '
               f'Q {a1[0]:.1f} {a1[1]:.1f} {a1[0]:.1f} {a1[1] + 8:.1f} L {a1[0]:.1f} {a0[1]:.1f} Z" fill="#5A4458"/>')
    out.append(f'<path d="M {a0[0] + 3:.1f} {a0[1]:.1f} L {a0[0] + 3:.1f} {a1[1] + 10:.1f} Q {(a0[0] + a1[0]) / 2:.1f} {a1[1] + 2:.1f} {a1[0] - 3:.1f} {a1[1] + 10:.1f} L {a1[0] - 3:.1f} {a0[1]:.1f} Z" fill="#F6D2B0" opacity="0.55"/>')
    for i in range(5):
        m0, m1 = C(g0 + 0.3 + i * 1.95, 12.5, ZG), C(g0 + 1.3 + i * 1.95, 14, ZG)
        out.append(f'<rect x="{m0[0]:.1f}" y="{m1[1]:.1f}" width="{m1[0] - m0[0]:.1f}" height="{m0[1] - m1[1]:.1f}" fill="#D8AEA6"/>')
    for i, c in enumerate(("#C8A040", "#B84A48", "#C8A040")):           # the three coats of arms over the arch
        cc = C(-2.2 + i * 2.2, 10.2, ZG)
        out.append(f'<path d="M {cc[0] - 3:.1f} {cc[1] - 3.5:.1f} L {cc[0] + 3:.1f} {cc[1] - 3.5:.1f} L {cc[0] + 3:.1f} {cc[1]:.1f} Q {cc[0]:.1f} {cc[1] + 4:.1f} {cc[0] - 3:.1f} {cc[1]:.1f} Z" fill="{c}"/>')
    # Lesser Town Bridge Tower (right, tall, late Gothic)
    side = [C(4.4, 0, ZG - 1), C(4.4, 31, ZG - 1), C(4.4, 31, ZG + 12), C(4.4, 0, ZG + 12)]
    out.append(poly(side, "#B48A94"))
    front = [C(4.4, 0, ZG - 1), C(4.4, 31, ZG - 1), C(16.5, 31, ZG - 1), C(16.5, 0, ZG - 1)]
    out.append(poly(front, f"url(#{u}-twr)"))
    out.append(f'<polyline points="{P([front[0], front[1]])}" fill="none" stroke="#FFE0C8" stroke-width="1.8" opacity="0.9"/>')
    # blind gothic tracery panels and the gallery windows
    for i in range(3):
        xx = 5.8 + i * 3.7
        p0, p1 = C(xx, 17, ZG - 1), C(xx + 2.6, 27, ZG - 1)
        out.append(f'<path d="M {p0[0]:.1f} {p0[1]:.1f} L {p0[0]:.1f} {p1[1] + 5:.1f} Q {(p0[0] + p1[0]) / 2:.1f} {p1[1] - 4:.1f} {p1[0]:.1f} {p1[1] + 5:.1f} L {p1[0]:.1f} {p0[1]:.1f} Z" fill="none" stroke="#8A6878" stroke-width="1.3"/>')
        w0, w1 = C(xx + 0.7, 21, ZG - 1), C(xx + 1.9, 25, ZG - 1)
        out.append(f'<rect x="{w0[0]:.1f}" y="{w1[1]:.1f}" width="{w1[0] - w0[0]:.1f}" height="{w0[1] - w1[1]:.1f}" rx="1.2" fill="#4A3A52"/>')
    for yy in (6, 11):
        w0, w1 = C(9.6, yy, ZG - 1), C(11.2, yy + 3, ZG - 1)
        out.append(f'<rect x="{w0[0]:.1f}" y="{w1[1]:.1f}" width="{w1[0] - w0[0]:.1f}" height="{w0[1] - w1[1]:.1f}" fill="#4A3A52"/>')
    out.append(f'<polyline points="{P([C(4.4, 15.5, ZG - 1), C(16.5, 15.5, ZG - 1)])}" fill="none" stroke="#8A6878" stroke-width="1.6"/>')
    # the gallery parapet, steep slate roof and the four corner turrets
    ga, gb = C(4.1, 31, ZG - 1), C(16.8, 32.6, ZG - 1)
    out.append(f'<rect x="{ga[0]:.1f}" y="{gb[1]:.1f}" width="{gb[0] - ga[0]:.1f}" height="{ga[1] - gb[1]:.1f}" fill="#E2BCAE"/>')
    for i in range(10):
        q0 = C(4.4 + i * 1.22, 32.4, ZG - 1)
        out.append(f'<path d="M {q0[0]:.1f} {q0[1]:.1f} l 1.6 -3 l 1.6 3 Z" fill="#8A6878"/>')
    rt = C(10.45, 43.5, ZG + 5.5)
    out.append(poly([C(5.2, 32.6, ZG), rt, C(15.7, 32.6, ZG)], f"url(#{u}-roof)"))
    out.append(poly([C(5.2, 32.6, ZG), rt, C(9.6, 32.6, ZG)], "#B6A2C2", ' opacity="0.45"'))
    for t in (0.33, 0.66):
        aa = (C(5.2, 32.6, ZG)[0] + (rt[0] - C(5.2, 32.6, ZG)[0]) * t, C(5.2, 32.6, ZG)[1] + (rt[1] - C(5.2, 32.6, ZG)[1]) * t)
        bb = (C(15.7, 32.6, ZG)[0] + (rt[0] - C(15.7, 32.6, ZG)[0]) * t, aa[1])
        out.append(line(aa, bb, "#8E86AA", 1.1, ' opacity="0.7"'))
    out.append(line(rt, (rt[0], rt[1] - 10), "#3E405E", 1.6) + f'<circle cx="{rt[0]:.1f}" cy="{rt[1] - 11:.1f}" r="2.2" fill="#E8C070"/>')
    for xx in (4.6, 16.3):
        b0 = C(xx, 32.6, ZG - 1)
        out.append(f'<rect x="{b0[0] - 2.5:.1f}" y="{b0[1] - 8:.1f}" width="5" height="8" fill="#D8B0A6"/>'
                   f'<path d="M {b0[0] - 3.5:.1f} {b0[1] - 8:.1f} L {b0[0]:.1f} {b0[1] - 22:.1f} L {b0[0] + 3.5:.1f} {b0[1] - 8:.1f} Z" fill="#3E405E"/>')
    # small dormers on the roof
    for (xx, yy) in ((8.2, 36), (12.6, 36), (10.4, 39.5)):
        d0 = C(xx, yy, ZG + 1.5)
        out.append(f'<path d="M {d0[0] - 2.5:.1f} {d0[1]:.1f} L {d0[0] - 2.5:.1f} {d0[1] - 3:.1f} L {d0[0]:.1f} {d0[1] - 5.5:.1f} L {d0[0] + 2.5:.1f} {d0[1] - 3:.1f} L {d0[0] + 2.5:.1f} {d0[1]:.1f} Z" fill="#D8B0A6"/>')
    # morning mist rolling across the feet of the towers
    out.append(mist(300, 344, 330, 18, "#FBE6DC", f"{u}-m3", 0.85))

    # ---- the bridge: cobbled deck between two parapets, statues and lamps receding
    deck = [C(-5.2, 0, 3), C(-5.2, 0, ZG), C(5.2, 0, ZG), C(5.2, 0, 3)]
    out.append(poly(deck, f"url(#{u}-deck)"))
    out.append(f'<clipPath id="{u}-dk"><polygon points="{P(deck)}"/></clipPath>')
    cob = []
    rnd = random.Random(65)
    z = 3.0
    while z < ZG:
        a_, b_ = C(-5.2, 0, z), C(5.2, 0, z)
        cob.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#4E3E4E" stroke-width="{max(0.5, 30 / z):.2f}" opacity="0.35"/>')
        z *= 1.07
    for X in [-5.2 + i * 0.6 for i in range(18)]:
        a_, b_ = C(X, 0, 3), C(X, 0, ZG)
        cob.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#4E3E4E" stroke-width="0.8" opacity="0.18"/>')
    for _ in range(140):
        X, Z = rnd.uniform(-5, 5), 3 + rnd.random() ** 1.6 * 60
        x_, y_ = C(X, 0, Z)
        r_ = 30 / Z
        cob.append(f'<ellipse cx="{x_:.1f}" cy="{y_:.1f}" rx="{r_ * 1.4:.1f}" ry="{r_ * 0.5:.1f}" fill="{rnd.choice(["#C8B0B4", "#D8BCB8", "#6E5A6A"])}" opacity="0.45"/>')
    # a long warm stripe of first sunlight running down the deck, broken by statue shadows
    sun_strip = [C(-1.0, 0, 3), C(1.5, 0, ZG), C(4.6, 0, ZG), C(5.2, 0, 3)]
    near_sh = [C(-5.2, 0, 3), C(-5.2, 0, 5.2), C(3.5, 0, 9.5), C(5.2, 0, 8.2), C(5.2, 0, 6.4), C(2.0, 0, 5.0), C(1.2, 0, 3)]
    puddles = ""
    for X, Z, w in ((1.6, 7.5, 1.6), (-2.4, 12, 1.1), (2.8, 22, 1.4)):
        x_, y_ = C(X, 0, Z)
        rx = 560 * w / Z
        pts = [(x_ + rx * math.cos(a) * (1 + 0.25 * math.sin(3 * a + X)), y_ + rx * 0.09 * math.sin(a) * (1 + 0.3 * math.cos(2 * a))) for a in [i * math.pi / 10 for i in range(20)]]
        puddles += (poly(pts, "#D8A8B4", ' opacity="0.45"')
                    + f'<rect x="{x_ - rx * 0.5:.1f}" y="{y_ - rx * 0.03:.1f}" width="{rx * 0.7:.1f}" height="{max(0.8, rx * 0.025):.1f}" fill="#FFE6D6" opacity="0.6"/>')
    out.append(f'<g clip-path="url(#{u}-dk)">' + "".join(cob) + poly(sun_strip, "#FFD2B0", ' opacity="0.28"') + puddles
               + poly(near_sh, "#3A2A44", ' opacity="0.32"') + "</g>")
    # parapets: inner faces seen obliquely, tops catching the light
    for sgn in (-1, 1):
        X = 5.2 * sgn
        face = [C(X, 0, 3), C(X, 1.15, 3), C(X, 1.15, ZG), C(X, 0, ZG)]
        out.append(poly(face, f"url(#{u}-par)" if sgn < 0 else "#7A6070"))
        top = [C(X, 1.15, 3), C(X + 0.6 * sgn, 1.25, 3), C(X + 0.6 * sgn, 1.25, ZG), C(X, 1.15, ZG)]
        out.append(poly(top, "#E8C2B4" if sgn > 0 else "#C8A0A4"))
        out.append(f'<polyline points="{P([C(X, 1.15, 3), C(X, 1.15, ZG)])}" fill="none" stroke="#FFE2CC" stroke-width="1.6" opacity="0.8"/>')
        # stone courses on the parapet face
        z = 4.0
        while z < ZG:
            a_, b_ = C(X, 0, z), C(X, 1.15, z)
            out.append(line(a_, b_, "#3E2E3E", max(0.6, 12 / z), ' opacity="0.35"'))
            z *= 1.18
    # statues (far to near) and lamps along both parapets
    stat = [(-1, 92, 3, False), (1, 80, 1, False), (-1, 64, 0, False), (1, 54, 0, True), (-1, 38, 1, False), (1, 30, 3, False), (-1, 17, 1, False)]
    lamps = [(-1, 100), (1, 96), (-1, 76), (1, 66), (-1, 50), (1, 42), (-1, 27), (1, 15)]
    things = [(Z, "s", sgn, kind, halo) for sgn, Z, kind, halo in stat] + [(Z, "l", sgn, 0, False) for sgn, Z in lamps]
    for k, (Z, typ, sgn, kind, halo) in enumerate(sorted(things, key=lambda t: -t[0])):
        X = 5.5 * sgn
        bx, by_ = C(X, 1.2, Z)
        if typ == "s":
            hgt = 560 * 7.4 / Z
            body = mix("#2A2434", "#A890AC", min(0.55, Z / 190))
            # its long shadow thrown across the deck by the low sun behind-left
            if sgn < 0:
                sh = [C(X, 0, Z - 0.9), C(X, 0, Z + 0.9), C(X + 10.5, 0, Z + 12), C(X + 10.5, 0, Z + 8)]
                out.append(f'<g clip-path="url(#{u}-dk)">' + poly(sh, "#3E2E48", ' opacity="0.3"') + "</g>")
            out.append(baroque_saint(bx, by_, hgt, 70 + k, body=body, rim="#FFC8B0" if sgn > 0 else "#F6B4AC", rim_side=-1, kind=kind, halo=halo))
        else:
            if sgn < 0:
                sh = [C(X, 0, Z - 0.12), C(X, 0, Z + 0.12), C(X + 10.5, 0, Z + 8.6), C(X + 10.5, 0, Z + 8.2)]
                out.append(f'<g clip-path="url(#{u}-dk)">' + poly(sh, "#3E2E48", ' opacity="0.25"') + "</g>")
            out.append(bridge_lamp(bx, by_, 560 * 4.6 / Z, u, k))
    # people: an early photographer with a tripod, a couple strolling toward the towers, a jogger
    def walker(X, Z, h, col, legs="#2E2838", rim="#FFD0B4", flip=1):
        x_, y_ = C(X, 0, Z)
        hh = 560 * h / Z
        s = hh / 100
        g = (f'<g transform="translate({x_:.1f} {y_:.1f}) scale({s * flip:.3f} {s:.3f})">'
             f'<ellipse cx="18" cy="0" rx="26" ry="3" fill="#3E2E48" opacity="0.25"/>'
             f'<path d="M -8 -50 L 7 -50 L 9 0 L 3 0 L 0 -32 L -4 0 L -10 0 Z" fill="{legs}"/>'
             f'<path d="M -12 -86 Q 0 -93 12 -86 L 11 -46 L -11 -46 Z" fill="{col}"/>'
             f'<circle cx="0" cy="-95" r="8.5" fill="#3A2A2A"/>'
             f'<path d="M -12 -86 L -11 -48" stroke="{rim}" stroke-width="3" opacity="0.8"/></g>')
        return g
    out.append(walker(-0.6, 42, 1.75, "#4E5A86"))
    out.append(walker(0.2, 43, 1.65, "#B8505A"))
    out.append(walker(2.4, 30, 1.7, "#E8D8C8", flip=-1))
    px_, py_ = C(-2.6, 0, 17)
    k_ = 560 / 17
    out.append(f'<g transform="translate({px_:.1f} {py_:.1f}) scale({k_ / 100:.3f})">'
               '<ellipse cx="60" cy="0" rx="70" ry="5" fill="#3E2E48" opacity="0.25"/>'
               '<path d="M 50 0 L 62 -120 L 74 0 M 62 -120 L 62 0" fill="none" stroke="#2A2432" stroke-width="3"/>'
               '<rect x="52" y="-136" width="22" height="15" rx="2" fill="#2A2432"/><rect x="72" y="-132" width="6" height="8" fill="#2A2432"/>'
               '<path d="M -10 -90 L 10 -90 L 12 0 L 5 0 L 1 -55 L -3 0 L -10 0 Z" fill="#3A3448"/>'
               '<path d="M -16 -158 Q 0 -168 16 -158 L 14 -88 L -14 -88 Z" fill="#6E8A6E"/>'
               '<path d="M 12 -150 Q 36 -142 54 -130" fill="none" stroke="#6E8A6E" stroke-width="9" stroke-linecap="round"/>'
               '<circle cx="2" cy="-172" r="12" fill="#3A2A26"/><path d="M -10 -176 Q 2 -192 14 -176 Z" fill="#B84A48"/>'
               '<path d="M -16 -158 L -14 -92" stroke="#FFD0B4" stroke-width="4" opacity="0.8"/></g>')
    # pigeons on the parapet and a pair in flight over the river
    for x_, y_ in ((450, 368), (462, 365), (150, 372)):
        out.append(f'<path d="M {x_} {y_} q 4 -6 9 -3 l 3 -2 l 0 3 q -2 4 -9 4 Z" fill="#5E5470"/>')
    out.append(gulls([(250, 160, 9), (268, 168, 7), (360, 150, 8)], "#6E5A7E", 1.8))
    return "\n".join(out)


# ================================================================ BUDAPEST — the Parliament across the Danube from the Buda quay, blue hour
def pinnacle(x, base, h, w, lit="#FFD98A", shade="#B8783E"):
    """Slim gothic pinnacle: a little shaft and a steep crocketed spike, floodlit from below."""
    return (f'<rect x="{x - w / 2:.1f}" y="{base - h * 0.45:.1f}" width="{w:.1f}" height="{h * 0.45:.1f}" fill="{lit}"/>'
            f'<rect x="{x:.1f}" y="{base - h * 0.45:.1f}" width="{w / 2:.1f}" height="{h * 0.45:.1f}" fill="{shade}" opacity="0.55"/>'
            f'<path d="M {x - w * 0.6:.1f} {base - h * 0.45:.1f} L {x:.1f} {base - h:.1f} L {x + w * 0.6:.1f} {base - h * 0.45:.1f} Z" fill="{lit}"/>'
            f'<path d="M {x:.1f} {base - h:.1f} L {x + w * 0.6:.1f} {base - h * 0.45:.1f} L {x:.1f} {base - h * 0.45:.1f} Z" fill="{shade}" opacity="0.5"/>')


def parliament(cx, B, u):
    """The Hungarian Parliament's Danube front, floodlit gold at blue hour, symmetric about cx, foot at y=B."""
    out = [defs(lg(f"{u}-fac", [(0, "#F6D088"), (0.6, "#FFE6A8"), (1, "#FFF2C8")]),
                lg(f"{u}-roof", [(0, "#7A3A3E"), (1, "#B8584A")]),
                lg(f"{u}-dome", [(0, "#8A4440"), (0.35, "#C8704E"), (0.6, "#E89A62"), (1, "#7A3A3E")], 0, 0, 1, 0),
                lg(f"{u}-drum", [(0, "#C88A4E"), (0.4, "#FFE2A0"), (1, "#C88A4E")], 0, 0, 1, 0))]
    L, R = cx - 262, cx + 262
    top = B - 52                 # main cornice
    # long roof of the wings: steep, dark red, a floodlit ridge
    out.append(poly([(L + 6, top), (L + 14, top - 20), (R - 14, top - 20), (R - 6, top)], f"url(#{u}-roof)"))
    out.append(f'<line x1="{L + 14}" y1="{top - 20}" x2="{R - 14}" y2="{top - 20}" stroke="#F6B86E" stroke-width="1.4" opacity="0.8"/>')
    # the facade, with a darker basement arcade and three storeys of tall windows
    out.append(f'<rect x="{L}" y="{top}" width="{R - L}" height="{B - top}" fill="url(#{u}-fac)"/>')
    out.append(f'<rect x="{L}" y="{B - 13}" width="{R - L}" height="13" fill="#E8B06A"/>')
    for i in range(int((R - L) / 7)):
        x = L + 3 + i * 7
        out.append(f'<path d="M {x:.1f} {B:.1f} L {x:.1f} {B - 8:.1f} Q {x + 2:.1f} {B - 11:.1f} {x + 4:.1f} {B - 8:.1f} L {x + 4:.1f} {B:.1f} Z" fill="#6A4A4A"/>')
        for k, (y0, hh) in enumerate(((B - 32, 13), (top + 6, 9))):
            out.append(f'<rect x="{x + 0.6:.1f}" y="{y0:.1f}" width="2.8" height="{hh}" rx="1.3" fill="{"#B07A4E" if k else "#A86E48"}"/>')
    out.append(f'<line x1="{L}" y1="{top + 1}" x2="{R}" y2="{top + 1}" stroke="#FFF6D8" stroke-width="2"/>')
    # pinnacles along the whole roofline (the building's forest of spires)
    for i in range(37):
        x = L + 8 + i * (R - L - 16) / 36
        if abs(x - cx) < 52:
            continue
        out.append(pinnacle(x, top, 18, 3.2))
    # projecting pavilions with steep pyramid roofs and four corner spires, symmetric pairs
    for d, w, h, rh in ((86, 30, 70, 30), (168, 28, 64, 26), (238, 34, 74, 34)):
        for sgn in (-1, 1):
            x0 = cx + sgn * d - w / 2
            y_top = B - h
            out.append(f'<rect x="{x0:.1f}" y="{y_top:.1f}" width="{w}" height="{h}" fill="url(#{u}-fac)"/>')
            out.append(f'<rect x="{x0 + w * 0.62:.1f}" y="{y_top:.1f}" width="{w * 0.38:.1f}" height="{h}" fill="#C88A52" opacity="0.35"/>')
            for k in range(3):
                out.append(f'<path d="M {x0 + 5 + k * (w - 10) / 2.2:.1f} {y_top + 30:.1f} L {x0 + 5 + k * (w - 10) / 2.2:.1f} {y_top + 12:.1f} '
                           f'Q {x0 + 7 + k * (w - 10) / 2.2:.1f} {y_top + 7:.1f} {x0 + 9 + k * (w - 10) / 2.2:.1f} {y_top + 12:.1f} L {x0 + 9 + k * (w - 10) / 2.2:.1f} {y_top + 30:.1f} Z" fill="#8E5A44"/>')
            out.append(f'<line x1="{x0}" y1="{y_top + 1}" x2="{x0 + w}" y2="{y_top + 1}" stroke="#FFF6D8" stroke-width="1.6"/>')
            out.append(poly([(x0 + 2, y_top), (x0 + w / 2, y_top - rh), (x0 + w - 2, y_top)], f"url(#{u}-roof)"))
            out.append(poly([(x0 + 2, y_top), (x0 + w / 2, y_top - rh), (x0 + w / 2, y_top)], "#D88A6A", ' opacity="0.35"'))
            out.append(f'<line x1="{x0 + w / 2:.1f}" y1="{y_top - rh:.1f}" x2="{x0 + w / 2:.1f}" y2="{y_top - rh - 8:.1f}" stroke="#FFD98A" stroke-width="1.4"/>')
            for px_ in (x0 + 1.5, x0 + w - 1.5):
                out.append(pinnacle(px_, y_top, 26 if d != 168 else 22, 4))
    # the central pavilion with its gable, then the drum and the great ribbed dome
    out.append(f'<rect x="{cx - 50}" y="{B - 78}" width="100" height="78" fill="url(#{u}-fac)"/>')
    for k in range(5):
        x = cx - 40 + k * 18
        out.append(f'<path d="M {x:.1f} {B - 18:.1f} L {x:.1f} {B - 54:.1f} Q {x + 4:.1f} {B - 64:.1f} {x + 8:.1f} {B - 54:.1f} L {x + 8:.1f} {B - 18:.1f} Z" fill="#8E5A44"/>'
                   f'<path d="M {x + 1.5:.1f} {B - 20:.1f} L {x + 1.5:.1f} {B - 52:.1f} L {x + 6.5:.1f} {B - 52:.1f} L {x + 6.5:.1f} {B - 20:.1f} Z" fill="#FFC870" opacity="0.55"/>')
    out.append(poly([(cx - 52, B - 78), (cx, B - 112), (cx + 52, B - 78)], f"url(#{u}-fac)"))
    out.append(f'<path d="M {cx - 52} {B - 78} L {cx} {B - 112} L {cx + 52} {B - 78}" fill="none" stroke="#FFF6D8" stroke-width="2"/>')
    out.append(f'<circle cx="{cx}" cy="{B - 92}" r="8" fill="#8E5A44"/><circle cx="{cx}" cy="{B - 92}" r="5" fill="#FFD98A"/>')
    for sx in (-52, 52):
        out.append(pinnacle(cx + sx, B - 78, 40, 5))
    out.append(pinnacle(cx, B - 112, 18, 3.5))
    # drum: a ring of tall gothic windows between buttress pinnacles
    dt = B - 122
    out.append(f'<rect x="{cx - 44}" y="{dt}" width="88" height="{B - 112 - dt + 30}" fill="url(#{u}-drum)"/>')
    for k in range(8):
        x = cx - 38 + k * 10.6
        out.append(f'<path d="M {x:.1f} {dt + 27:.1f} L {x:.1f} {dt + 9:.1f} Q {x + 2.5:.1f} {dt + 4:.1f} {x + 5:.1f} {dt + 9:.1f} L {x + 5:.1f} {dt + 27:.1f} Z" fill="#9A6040"/>')
    for k in range(9):
        out.append(pinnacle(cx - 44 + k * 11, dt + 2, 20, 3))
    # the dome itself: a tall ogival ribbed dome with lantern and spire
    dh = 54
    out.append(f'<path d="M {cx - 42} {dt} C {cx - 44} {dt - dh * 0.55} {cx - 18} {dt - dh * 0.9} {cx} {dt - dh} C {cx + 18} {dt - dh * 0.9} {cx + 44} {dt - dh * 0.55} {cx + 42} {dt} Z" fill="url(#{u}-dome)"/>')
    for t in (-0.75, -0.45, -0.15, 0.15, 0.45, 0.75):
        out.append(f'<path d="M {cx + 42 * t:.1f} {dt} Q {cx + 30 * t:.1f} {dt - dh * 0.7:.1f} {cx} {dt - dh}" fill="none" stroke="#FFD08A" stroke-width="1.6" opacity="{0.85 - abs(t) * 0.4:.2f}"/>')
    for k, f in enumerate((0.28, 0.55)):
        yy = dt - dh * f
        wd = 42 * (1 - f ** 1.6) * 1.0
        for j in range(7):
            xx = cx - wd * 0.8 + j * wd * 1.6 / 6
            out.append(f'<rect x="{xx - 1.2:.1f}" y="{yy - 3:.1f}" width="2.4" height="4" rx="1" fill="#FFE6A8" opacity="0.85"/>')
    lt = dt - dh
    out.append(f'<rect x="{cx - 5}" y="{lt - 12}" width="10" height="13" fill="#FFE2A0"/><rect x="{cx}" y="{lt - 12}" width="5" height="13" fill="#C8884E" opacity="0.5"/>')
    out.append(f'<path d="M {cx - 6} {lt - 12} L {cx} {lt - 26} L {cx + 6} {lt - 12} Z" fill="#C8704E"/>')
    out.append(f'<line x1="{cx}" y1="{lt - 26}" x2="{cx}" y2="{lt - 32}" stroke="#FFE2A0" stroke-width="1.6"/>')
    return "".join(out)


def river_cruiser(x, wl, k, u, flip=False):
    """A long Danube dinner-cruise boat: white hull, glazed salon with warm lights, a flag at the stern."""
    sx = -k if flip else k
    rnd = random.Random(int(x))
    wins = "".join(f'<rect x="{-70 + i * 9:.1f}" y="-19" width="6" height="7" rx="1" fill="{rnd.choice(["#FFE2A0", "#FFD27A", "#FFF0C8"])}"/>' for i in range(15))
    return (f'<g transform="translate({x:.1f} {wl:.1f}) scale({sx:.3f} {k:.3f})">'
            '<path d="M 82 4 Q 120 8 170 10 M 80 7 Q 116 14 160 18" fill="none" stroke="#C8B8E0" stroke-width="2" opacity="0.6"/>'
            '<path d="M -86 -8 L 84 -8 Q 90 -6 86 2 L -78 2 Q -88 -2 -86 -8 Z" fill="#F2EEF6"/>'
            '<path d="M -82 -1 L 86 -1 L 86 2 L -78 2 Z" fill="#2E3A6A"/>'
            '<rect x="-74" y="-24" width="142" height="16" rx="2" fill="#2A2E52"/>' + wins +
            '<rect x="-60" y="-30" width="110" height="6" fill="#F2EEF6"/><rect x="-20" y="-36" width="26" height="6" fill="#F2EEF6"/>'
            '<line x1="-82" y1="-8" x2="-82" y2="-30" stroke="#F2EEF6" stroke-width="1.4"/><path d="M -82 -30 L -72 -27 L -82 -24 Z" fill="#C8303A"/>'
            '</g>')


def budapest():
    u = "budapest"
    B = 296
    out = [defs(
        lg(f"{u}-sky", [(0, "#1E2458"), (0.35, "#3A3C80"), (0.6, "#7A5E9E"), (0.78, "#D88A9E"), (0.9, "#F2B08E")], 0, 40, 0, B, units="userSpaceOnUse"),
        lg(f"{u}-river", [(0, "#4A3E7A"), (0.25, "#2E2E66"), (1, "#141A3E")], 0, B, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-quay", [(0, "#4A4466"), (1, "#22203A")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(50, 81, (0, 40, 600, 150), "#F6F0FF", r=(0.6, 1.3), opacity=(0.35, 0.9)))
    for x, y, w, c in ((110, 168, 140, "#C8889E"), (70, 186, 90, "#E8A0A0"), (480, 160, 130, "#A07AA6"), (540, 182, 80, "#D8909E"), (300, 196, 100, "#E8A498")):
        out.append(streak_cloud(x, y, w, c, 0.55, 3.6))
        out.append(streak_cloud(x - 10, y + 3, w * 0.6, "#FFC8A8", 0.4, 1.6))
    out.append(glow(300, B, 330, "#FFB078", f"{u}-dusk", 0.35))
    # Pest beyond: rooftops in silhouette with a sprinkle of lit windows, the Basilica dome to the right
    rnd = random.Random(82)
    x = -10
    city = []
    while x < 610:
        w = rnd.uniform(12, 30)
        h = rnd.uniform(14, 34)
        city.append(f'<rect x="{x:.1f}" y="{B - 30 - h:.1f}" width="{w + 0.5:.1f}" height="{h + 30:.1f}" fill="{rnd.choice(["#3E3A72", "#463F7A", "#38366A"])}"/>')
        city.append(dots(int(w * h / 90), int(x * 7), (x + 2, B - 28 - h, x + w - 2, B - 26), "#FFD98E", r=(0.6, 1.1), opacity=(0.4, 1)))
        x += w
    out.append("".join(city))
    bx_ = 548
    out.append(f'<g fill="#463F7A"><rect x="{bx_ - 22}" y="{B - 96}" width="44" height="40"/><path d="M {bx_ - 20} {B - 96} Q {bx_ - 20} {B - 126} {bx_} {B - 128} Q {bx_ + 20} {B - 126} {bx_ + 20} {B - 96} Z"/>'
               f'<rect x="{bx_ - 3}" y="{B - 142}" width="6" height="16"/><path d="M {bx_ - 4} {B - 142} L {bx_} {B - 150} L {bx_ + 4} {B - 142} Z"/></g>'
               f'<path d="M {bx_ - 20} {B - 96} Q {bx_ - 20} {B - 126} {bx_} {B - 128}" fill="none" stroke="#F2B08E" stroke-width="1.2" opacity="0.6"/>')
    # the Parliament
    out.append(parliament(300, B, u))
    # Pest embankment: the quay wall, trees, a yellow line-2 tram gliding past, street lamps
    out.append(f'<rect x="-10" y="{B}" width="620" height="8" fill="#5E4E6E"/><rect x="-10" y="{B + 8}" width="620" height="3" fill="#3A3058"/>')
    for i in range(30):
        x = -6 + i * 21
        out.append(f'<circle cx="{x:.1f}" cy="{B - 2}" r="2.2" fill="#FFE6A8"/>')
    tx = 186
    out.append(f'<g><rect x="{tx}" y="{B - 11}" width="54" height="11" rx="2" fill="#F2C230"/><rect x="{tx}" y="{B - 4}" width="54" height="2" fill="#C8902A"/>'
               + "".join(f'<rect x="{tx + 3 + i * 6.4:.1f}" y="{B - 9}" width="4.4" height="4" fill="#FFF2C8"/>' for i in range(8))
               + f'<line x1="{tx + 27}" y1="{B - 11}" x2="{tx + 22}" y2="{B - 17}" stroke="#2A2440" stroke-width="1"/></g>')
    # the Danube: blue-violet, broken gold reflections of the floodlit facade
    out.append(f'<rect x="-10" y="{B + 11}" width="620" height="{444 - B - 11}" fill="url(#{u}-river)"/>')
    rnd = random.Random(83)
    refl = []
    for i in range(420):
        x = rnd.uniform(36, 564)
        y = B + 12 + rnd.random() ** 1.5 * 120
        dome = abs(x - 300) < 46
        if not dome and rnd.random() < 0.25:
            continue
        w = rnd.uniform(4, 16) * (0.6 + (y - B) / 80)
        c = rnd.choice(["#FFD98A", "#FFC870", "#F6B060", "#FFE6A8"])
        refl.append(f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{1 + (y - B) / 70:.1f}" rx="0.8" fill="{c}" opacity="{rnd.uniform(0.35, 0.9) * (1 - (y - B) / 200):.2f}"/>')
    for i in range(120):
        y = B + 12 + rnd.random() * 150
        x = rnd.uniform(-10, 610)
        w = rnd.uniform(8, 40) * (0.5 + (y - B) / 100)
        refl.append(f'<rect x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="1.3" rx="0.6" fill="{rnd.choice(["#8E7AB8", "#E8A0A8", "#5A5A9A"])}" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    out.append("".join(refl))
    out.append(defs(rg(f"{u}-dsh", [(0, "#FFC878", 0.42), (0.6, "#FFC878", 0.15), (1, "#FFC878", 0)], cx=0.5, cy=0.0, r=0.6))
               + f'<ellipse cx="300" cy="{B + 11}" rx="70" ry="110" fill="url(#{u}-dsh)"/>')
    # a cruise boat heading downstream, its lights doubling in the water
    out.append(river_cruiser(372, 352, 0.82, u, flip=True))
    out.append(water_lines(18, 84, (290, 356, 450, 368), ["#FFD98A", "#FFE6A8"], w=(6, 18), h=(1, 1.6), opacity=(0.4, 0.8)))
    # Buda quay in the foreground: stone balustrade, an ornate lamp post, a couple watching the lights
    q = rough([(-10, 404), (200, 402), (400, 404), (610, 402)], 85, amp=1, depth=2)
    out.append(poly(q + [(610, 444), (-10, 444)], f"url(#{u}-quay)"))
    out.append(f'<polyline points="{P(q)}" fill="none" stroke="#C8A0B8" stroke-width="2.2" opacity="0.8"/>')
    out.append(f'<rect x="-10" y="404" width="620" height="5" fill="#5A4E78"/>')
    for i in range(32):
        x = -4 + i * 20
        out.append(f'<path d="M {x} 444 L {x} 432 Q {x - 4} 424 {x + 1} 418 Q {x + 5} 413 {x} 410 L {x + 8} 410 Q {x + 3} 413 {x + 7} 418 Q {x + 12} 424 {x + 8} 432 L {x + 8} 444 Z" fill="#2E2A48"/>'
                   f'<path d="M {x + 1} 418 Q {x + 5} 413 {x} 410" fill="none" stroke="#B890B0" stroke-width="1.2" opacity="0.7"/>')
    lx = 94
    out.append(glow(lx, 252, 70, "#FFD98E", f"{u}-lamp", 0.85))
    out.append(f'<g fill="#1E1C34"><path d="M {lx - 9} 410 L {lx + 9} 410 L {lx + 6} 396 L {lx + 3} 392 L {lx + 2.4} 276 L {lx - 2.4} 276 L {lx - 3} 392 L {lx - 6} 396 Z"/>'
               f'<rect x="{lx - 6}" y="352" width="12" height="4"/><rect x="{lx - 5}" y="300" width="10" height="3"/>'
               f'<path d="M {lx} 282 Q {lx - 16} 278 {lx - 18} 266 M {lx} 282 Q {lx + 16} 278 {lx + 18} 266" fill="none" stroke="#1E1C34" stroke-width="2.4"/></g>')
    for sx in (-18, 18, 0):
        yy = 252 if sx == 0 else 262
        out.append(f'<path d="M {lx + sx - 6} {yy + 4} L {lx + sx + 6} {yy + 4} L {lx + sx + 7} {yy - 10} L {lx + sx - 7} {yy - 10} Z" fill="#FFE6A8"/>'
                   f'<path d="M {lx + sx - 8} {yy - 10} L {lx + sx + 8} {yy - 10} L {lx + sx} {yy - 18} Z" fill="#1E1C34"/>'
                   f'<rect x="{lx + sx - 6}" y="{yy + 4}" width="12" height="2" fill="#1E1C34"/>')
    out.append(f'<line x1="{lx - 2}" y1="282" x2="{lx - 2}" y2="400" stroke="#B890B0" stroke-width="1" opacity="0.6"/>')
    # the couple leaning on the balustrade, backs to us
    out.append('<g transform="translate(486 412) scale(0.8) translate(-447 -412)">')
    for px_, c, hc, long_hair in ((432, "#C8484E", "#3A2422", True), (462, "#3E4A7A", "#2A1E1E", False)):
        out.append(f'<path d="M {px_ - 13} 412 Q {px_ - 15} 374 {px_} 368 Q {px_ + 15} 374 {px_ + 13} 412 Z" fill="{c}"/>'
                   f'<circle cx="{px_}" cy="358" r="10" fill="{hc}"/>'
                   f'<path d="M {px_ + 13} 410 Q {px_ + 15} 378 {px_ + 2} 369" fill="none" stroke="#FFC890" stroke-width="2.4" opacity="0.75" stroke-linecap="round"/>'
                   f'<path d="M {px_ + 6} 350 Q {px_ + 11} 356 {px_ + 9} 364" fill="none" stroke="#FFC890" stroke-width="2" opacity="0.7" stroke-linecap="round"/>')
        if long_hair:
            out.append(f'<path d="M {px_ - 9} 356 Q {px_} 344 {px_ + 9} 356 Q {px_ + 11} 372 {px_ + 6} 378 L {px_ - 6} 378 Q {px_ - 11} 370 {px_ - 9} 356 Z" fill="{hc}"/>')
    out.append('<path d="M 440 384 Q 448 388 455 384" fill="none" stroke="#C8484E" stroke-width="5" stroke-linecap="round"/></g>')
    out.append(gulls([(150, 120, 9), (170, 128, 7), (420, 112, 8)], "#F2C8B8", 1.8))
    return "\n".join(out)


# ================================================================ VIENNA — a fiaker crossing the court of honour at Schönbrunn, summer morning
def horse(uid, coat, shade, rim, mane, step=0, harness="#2A1E1E", brass="#E8B848"):
    """Side view of a carriage horse facing left, ~100 units long, withers at y=-64, hooves on y=0. step alternates the trot."""
    out = [defs(lg(uid, [(0, rim), (0.25, coat), (1, shade)], 0, 0, 1, 0.3))]
    legs_a = [((-34, -40), (-38, -21), (-34, -5), (-37, 0)), ((40, -40), (46, -20), (43, -4), (45, 0))]
    legs_b = [((-40, -40), (-52, -26), (-58, -14), (-62, -12)), ((34, -40), (30, -22), (22, -10), (19, -10))]
    if step:
        legs_a, legs_b = [legs_b[0], legs_a[1]], [legs_a[0], legs_b[1]]
    for leg in legs_b:              # far legs, darker
        out.append(f'<polyline points="{P(leg)}" fill="none" stroke="{shade}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
        out.append(f'<circle cx="{leg[-1][0]}" cy="{leg[-1][1]}" r="4" fill="#2A2228"/>')
    body = ("M -40 -48 C -44 -60 -48 -72 -56 -82 L -68 -70 Q -76 -70 -75 -77 L -62 -98 Q -57 -104 -52 -99 "
            "C -42 -86 -36 -72 -26 -65 Q 0 -59 30 -63 Q 47 -66 51 -52 Q 53 -40 44 -35 Q 0 -30 -36 -37 Z")
    out.append(f'<path d="{body}" fill="url(#{uid})"/>')
    for leg in legs_a:              # near legs
        out.append(f'<polyline points="{P(leg)}" fill="none" stroke="{coat}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>')
        out.append(f'<polyline points="{P(leg[:2])}" fill="none" stroke="{rim}" stroke-width="2" stroke-linecap="round" opacity="0.8" transform="translate(-2.5 0)"/>')
        out.append(f'<circle cx="{leg[-1][0]}" cy="{leg[-1][1] - 1}" r="4.4" fill="#2A2228"/>')
    out.append(f'<path d="M -54 -101 L -57 -110 L -50 -103 Z M -50 -100 L -51 -109 L -46 -101 Z" fill="{coat}"/>')
    out.append(f'<path d="M -52 -99 C -44 -88 -36 -74 -26 -66" fill="none" stroke="{mane}" stroke-width="5" stroke-linecap="round"/>')
    out.append(f'<path d="M 50 -56 Q 62 -46 56 -24 Q 54 -16 58 -10" fill="none" stroke="{mane}" stroke-width="6" stroke-linecap="round"/>')
    out.append(f'<path d="M -40 -48 C -44 -60 -48 -72 -56 -82 L -68 -70 Q -76 -70 -75 -77 L -62 -98" fill="none" stroke="{rim}" stroke-width="2" opacity="0.9"/>')
    out.append('<circle cx="-62" cy="-88" r="1.6" fill="#1E1418"/>')
    # harness: collar, bridle, saddle pad, traces
    out.append(f'<path d="M -46 -80 Q -36 -74 -38 -52" fill="none" stroke="{harness}" stroke-width="6" stroke-linecap="round"/>'
               f'<path d="M -46 -80 Q -36 -74 -38 -52" fill="none" stroke="{brass}" stroke-width="1.6" stroke-linecap="round"/>'
               f'<path d="M -73 -76 L -60 -90 L -55 -98 M -62 -84 L -56 -94" fill="none" stroke="{harness}" stroke-width="2"/>'
               f'<circle cx="-62" cy="-90" r="2" fill="{brass}"/>'
               f'<rect x="-14" y="-66" width="16" height="10" rx="3" fill="{harness}"/><circle cx="-6" cy="-67" r="2" fill="{brass}"/>'
               f'<path d="M -38 -54 L 60 -50" stroke="{harness}" stroke-width="2.4"/><path d="M -6 -56 L -2 -36" stroke="{harness}" stroke-width="2.4"/>')
    return "".join(out)


def fiaker(x, base, k, u):
    """Two-horse Viennese fiaker heading left: grey and chestnut pair, black carriage with red wheels, coachman in a bowler."""
    out = [f'<g transform="translate({x:.1f} {base:.1f}) scale({k:.3f})">']
    out.append('<ellipse cx="110" cy="2" rx="190" ry="7" fill="#7A6450" opacity="0.28"/>')
    # far horse (chestnut), a step behind and a touch higher
    out.append('<g transform="translate(6 -3)">' + horse(f"{u}-h2", "#8A4A2E", "#4A2418", "#D8925E", "#2A1610", step=1) + "</g>")
    out.append(horse(f"{u}-h1", "#EEE6DA", "#9E968E", "#FFFDF4", "#C8BEB2"))
    # reins from the coachman's hands
    out.append('<path d="M 96 -96 Q 30 -100 -56 -92" fill="none" stroke="#2A1E1E" stroke-width="1.4"/>')
    # carriage
    out.append(defs(lg(f"{u}-cb", [(0, "#4A4A5E"), (0.3, "#1E1E2A"), (1, "#0E0E16")], 0, 0, 1, 1)))
    wheel = lambda cx, cy, r: (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#B82E2E" stroke-width="3.4"/>'
                               + "".join(f'<line x1="{cx}" y1="{cy}" x2="{cx + r * math.cos(a):.1f}" y2="{cy + r * math.sin(a):.1f}" stroke="#B82E2E" stroke-width="1.8"/>'
                                         for a in [i * math.pi / 6 for i in range(12)])
                               + f'<circle cx="{cx}" cy="{cy}" r="{r * 0.18:.1f}" fill="#E8B848"/><circle cx="{cx}" cy="{cy}" r="{r + 1.6}" fill="none" stroke="#1A1A22" stroke-width="1.6"/>')
    out.append(wheel(144, -30, 30))                                   # far rear wheel peeks under the body
    out.append('<path d="M 62 -46 Q 70 -36 88 -38 L 170 -40 Q 180 -54 172 -84 L 128 -86 Q 116 -66 96 -64 L 74 -62 Q 64 -60 62 -46 Z" fill="url(#' + u + '-cb)"/>')
    out.append('<path d="M 74 -61 L 96 -63 Q 116 -65 128 -85" fill="none" stroke="#E8B848" stroke-width="1.6"/>')
    out.append('<path d="M 88 -40 L 168 -42" stroke="#E8B848" stroke-width="1.4"/>')
    # folded hood (accordion of black leather) behind the passengers
    out.append('<path d="M 160 -84 Q 176 -104 194 -94 Q 196 -80 178 -76 Z" fill="#14141C"/>'
               '<path d="M 166 -86 Q 178 -98 190 -93 M 170 -82 Q 180 -92 192 -86" fill="none" stroke="#5A5A6E" stroke-width="1.4"/>')
    # passengers: a couple, she with a sun hat
    out.append('<path d="M 132 -84 Q 134 -104 146 -106 Q 158 -104 158 -84 Z" fill="#E8E0D0"/><circle cx="146" cy="-114" r="7" fill="#E2B08E"/>'
               '<ellipse cx="146" cy="-120" rx="13" ry="3.4" fill="#F2D8A8"/><path d="M 139 -121 Q 146 -132 153 -121 Z" fill="#F2D8A8"/><rect x="139" y="-123" width="14" height="2.4" fill="#C83E4E"/>'
               '<path d="M 156 -84 Q 158 -106 170 -108 Q 182 -104 180 -84 Z" fill="#3E5A8E"/><circle cx="169" cy="-116" r="7" fill="#D8A07A"/><path d="M 162 -118 Q 169 -126 176 -118 Z" fill="#4A3426"/>')
    # coachman on the high box: bowler hat, grey jacket, whip
    out.append('<path d="M 84 -64 L 84 -92 L 108 -92 L 110 -64 Z" fill="#1E1E2A"/>'
               '<path d="M 90 -92 Q 90 -118 100 -120 Q 112 -118 110 -92 Z" fill="#6A6E7A"/><path d="M 92 -112 Q 100 -100 96 -96" stroke="#FFF6E2" stroke-width="2" fill="none"/>'
               '<circle cx="100" cy="-128" r="7.4" fill="#E2B08E"/><ellipse cx="100" cy="-134" rx="11" ry="2.6" fill="#141418"/><path d="M 93 -134 Q 93 -146 100 -146 Q 107 -146 107 -134 Z" fill="#141418"/>'
               '<path d="M 92 -104 Q 82 -102 90 -96" fill="none" stroke="#6A6E7A" stroke-width="5" stroke-linecap="round"/>'
               '<path d="M 90 -98 Q 70 -150 30 -160" fill="none" stroke="#2A1E1E" stroke-width="1.3"/>')
    out.append('<path d="M 84 -64 L 84 -92" stroke="#FFF2D2" stroke-width="1.4" opacity="0.6"/>')
    out.append(wheel(88, -22, 22))                                    # near front wheel
    out.append(wheel(152, -30, 30))                                   # near rear wheel
    out.append('<path d="M 72 -46 Q 80 -24 88 -22 M 170 -42 Q 160 -34 152 -30" fill="none" stroke="#1A1A22" stroke-width="2.4"/>')
    out.append("</g>")
    return "".join(out)


def gilded_eagle(cx, cy, k, u):
    """Gilded eagle with spread wings atop a gate obelisk, lit by the morning sun from the left."""
    g = f"{u}-gold"
    out = [defs(lg(g, [(0, "#FFF2B8"), (0.3, "#F6CC5A"), (0.7, "#C8902A"), (1, "#7A5418")], 0, 0, 1, 1))]
    out.append(f'<g transform="translate({cx:.1f} {cy:.1f}) scale({k:.3f})">')
    for sgn in (-1, 1):
        feathers = " ".join(f"L {sgn * (14 + i * 7):.1f} {-34 - i * 5 + (i % 2) * 6:.1f}" for i in range(6))
        out.append(f'<path d="M {sgn * 6} -8 Q {sgn * 26} -14 {sgn * 34} -40 Q {sgn * 52} -64 {sgn * 58} -82 {feathers} L {sgn * 8} -18 Z" fill="url(#{g})"/>')
        for i in range(4):
            out.append(f'<path d="M {sgn * (12 + i * 9)} -18 L {sgn * (24 + i * 9)} {-46 - i * 7}" stroke="#8E6420" stroke-width="1.4" opacity="0.7"/>')
    out.append(f'<path d="M -8 -2 Q -12 -26 -4 -36 Q 0 -40 4 -36 Q 12 -26 8 -2 Z" fill="url(#{g})"/>')
    out.append(f'<path d="M -2 -36 Q -8 -46 -1 -50 Q 6 -50 6 -44 L 12 -42 L 5 -38 Z" fill="url(#{g})"/><circle cx="1.6" cy="-46" r="1.2" fill="#5A3A10"/>')
    out.append(f'<path d="M -6 -2 L -10 6 M 6 -2 L 10 6 M -9 0 L 9 0" stroke="#C8902A" stroke-width="3" stroke-linecap="round"/>')
    out.append(f'<path d="M -8 -2 Q -12 -26 -4 -36" fill="none" stroke="#FFFBE0" stroke-width="1.6"/>')
    out.append('</g>')
    return "".join(out)


def vienna():
    u = "vienna"
    C = Cam(f=440, cx=300, vpy=281, eye=1.7)
    ZF = 112.0
    out = [defs(
        lg(f"{u}-sky", [(0, "#3E7CC8"), (0.5, "#7EB2E2"), (0.85, "#CFE4F2"), (1, "#EEF4EE")], 0, 40, 0, 281, units="userSpaceOnUse"),
        lg(f"{u}-yel", [(0, "#FBD66A"), (1, "#E8B442")], 0, 0, 1, 0),
        lg(f"{u}-yelsh", [(0, "#D8A04A"), (1, "#B8823E")], 0, 0, 1, 0),
        lg(f"{u}-grav", [(0, "#E8D2AA"), (0.4, "#DCC096"), (1, "#C8A47A")], 0, 281, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-obl", [(0, "#F6EEDE"), (0.35, "#E2D6C2"), (1, "#9A8E80")], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(-40, 120, 300, "#FFF6DA", f"{u}-sun", 0.8))
    out.append(cumulus(f"{u}-c1", 250, 128, 170, 44, 91, "#FFFFFF", "#F4F6FA", "#B8C8DE", hi="#FFFFFF", hi_op=0.75, light=-1))
    out.append(cumulus(f"{u}-c2", 470, 108, 130, 32, 92, "#FFFFFF", "#F2F4F8", "#B8C8DE", hi="#FFFFFF", hi_op=0.75, light=-1))
    out.append(cumulus(f"{u}-c3", 380, 168, 90, 18, 93, "#FFFFFF", "#F2F4F8", "#C8D4E4", light=-1))
    # the trees of the park rising behind the palace roofs
    rnd = random.Random(94)
    for i in range(22):
        x = rnd.uniform(-20, 620)
        out.append(leaf_canopy(f"{u}-pk{i}", x, rnd.uniform(170, 180), rnd.uniform(26, 40), rnd.uniform(14, 20), 95 + i,
                               "#4E6E52", "#6A8A62", "#A8C08A", n=26, light=(-1, -1)))
    # ---- the palace: long Schönbrunn-yellow front, white pilasters, grey roof with dormers, balustrade with vases and trophies
    X0, X1 = -112.0, 112.0
    yc, yr, ya = 21.0, 29.0, 23.0
    fa = C.quad_z(ZF, X0, X1, 0, yc)
    out.append(poly(fa, f"url(#{u}-yel)"))
    out.append(poly(C.quad_z(ZF, X0, X1, 0, 1.6), "#C8A060"))
    roof = [C(X0, yc + 0.4, ZF), C(X0 + 3, yr, ZF + 8), C(X1 - 3, yr, ZF + 8), C(X1, yc + 0.4, ZF)]
    out.append(poly(roof, "#7E8A92"))
    out.append(poly([roof[0], roof[1], C(X0 + 3, yr - 2, ZF + 8), C(X0, yc + 0.4, ZF)], "#A8B4BA", ' opacity="0.6"'))
    # dormers
    for X in [X0 + 6 + i * 6.2 for i in range(36)]:
        if abs(X) < 22:
            continue
        a_, b_ = C(X - 0.9, yc + 3.2, ZF + 2), C(X + 0.9, yc + 5.2, ZF + 2)
        out.append(f'<rect x="{a_[0]:.1f}" y="{b_[1]:.1f}" width="{b_[0] - a_[0]:.1f}" height="{a_[1] - b_[1]:.1f}" fill="#F2EEE4"/>'
                   f'<path d="M {a_[0] - 0.8:.1f} {b_[1]:.1f} L {(a_[0] + b_[0]) / 2:.1f} {b_[1] - 2.6:.1f} L {b_[0] + 0.8:.1f} {b_[1]:.1f} Z" fill="#5E6A72"/>')
    # windows: three storeys, white surrounds, green-grey glass with sky reflections; pilasters every three bays
    rnd = random.Random(96)
    for i in range(64):
        X = X0 + 2.2 + i * 3.45
        if abs(X) < 20:
            continue
        for (y0, y1, cap) in ((3.2, 7.6, 1), (10.0, 15.6, 2), (17.2, 19.6, 0)):
            a_, b_ = C(X - 0.8, y0, ZF), C(X + 0.8, y1, ZF)
            out.append(f'<rect x="{a_[0] - 1:.1f}" y="{b_[1] - 1:.1f}" width="{b_[0] - a_[0] + 2:.1f}" height="{a_[1] - b_[1] + 2:.1f}" fill="#FFFBF0"/>')
            out.append(f'<rect x="{a_[0]:.1f}" y="{b_[1]:.1f}" width="{b_[0] - a_[0]:.1f}" height="{a_[1] - b_[1]:.1f}" fill="{rnd.choice(["#5E7A86", "#6E8A92", "#526E7C"])}"/>')
            out.append(f'<rect x="{a_[0]:.1f}" y="{b_[1]:.1f}" width="{(b_[0] - a_[0]) * 0.4:.1f}" height="{a_[1] - b_[1]:.1f}" fill="#BCD8E4" opacity="0.6"/>')
            if cap == 2:
                out.append(f'<path d="M {a_[0] - 1.6:.1f} {b_[1] - 1:.1f} L {(a_[0] + b_[0]) / 2:.1f} {b_[1] - 3.4:.1f} L {b_[0] + 1.6:.1f} {b_[1] - 1:.1f} Z" fill="#FFFBF0"/>')
        if i % 3 == 0:
            p0, p1 = C(X + 1.7, 1.6, ZF), C(X + 2.3, yc, ZF)
            out.append(f'<rect x="{p0[0]:.1f}" y="{p1[1]:.1f}" width="{max(1.4, p1[0] - p0[0]):.1f}" height="{p0[1] - p1[1]:.1f}" fill="#FFF6DC"/>')
    for yy, w_ in ((8.8, 1.6), (yc, 2.4)):
        out.append(f'<polyline points="{P([C(X0, yy, ZF), C(X1, yy, ZF)])}" fill="none" stroke="#FFFBF0" stroke-width="{w_}"/>')
    # balustrade with vases along the roofline
    out.append(f'<polyline points="{P([C(X0, yc + 1.4, ZF), C(X1, yc + 1.4, ZF)])}" fill="none" stroke="#F6F0E2" stroke-width="2.6"/>')
    for X in [X0 + 3 + i * 9.2 for i in range(25)]:
        if abs(X) < 20:
            continue
        v = C(X, yc + 1.4, ZF)
        out.append(f'<path d="M {v[0] - 1.6:.1f} {v[1]:.1f} Q {v[0] - 3:.1f} {v[1] - 3:.1f} {v[0]:.1f} {v[1] - 5:.1f} Q {v[0] + 3:.1f} {v[1] - 3:.1f} {v[0] + 1.6:.1f} {v[1]:.1f} Z" fill="#F6F0E2"/>')
    # central block: forward, taller, columns, balcony, attic with the clock and sculpture
    Zc = ZF - 6
    cx0, cx1 = -20.0, 20.0
    side = [C(cx0, 0, Zc), C(cx0, yc + 4, Zc), C(cx0, yc + 4, ZF), C(cx0, 0, ZF)]
    out.append(poly(side, f"url(#{u}-yelsh)"))
    out.append(poly(C.quad_z(Zc, cx0, cx1, 0, yc + 4), f"url(#{u}-yel)"))
    out.append(poly(C.quad_z(Zc, cx0, cx1, 0, 7.8), "#EAC060"))
    for X in (-11, -3.5, 3.5, 11):                   # arched carriage passages under the balcony
        a_, b_ = C(X - 1.9, 0, Zc), C(X + 1.9, 6.2, Zc)
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {a_[0]:.1f} {b_[1] + 5:.1f} Q {(a_[0] + b_[0]) / 2:.1f} {b_[1] - 4:.1f} {b_[0]:.1f} {b_[1] + 5:.1f} L {b_[0]:.1f} {a_[1]:.1f} Z" fill="#6E5A3E"/>'
                   f'<path d="M {a_[0]:.1f} {b_[1] + 5:.1f} Q {(a_[0] + b_[0]) / 2:.1f} {b_[1] - 4:.1f} {b_[0]:.1f} {b_[1] + 5:.1f}" fill="none" stroke="#FFFBF0" stroke-width="1.6"/>')
    for i in range(8):                      # giant order of columns
        X = cx0 + 2.5 + i * 5
        p0, p1 = C(X - 0.6, 8.6, Zc - 0.6), C(X + 0.6, yc + 3, Zc - 0.6)
        out.append(f'<rect x="{p0[0]:.1f}" y="{p1[1]:.1f}" width="{p1[0] - p0[0]:.1f}" height="{p0[1] - p1[1]:.1f}" fill="#FFF8E8"/>'
                   f'<rect x="{p0[0] + (p1[0] - p0[0]) * 0.55:.1f}" y="{p1[1]:.1f}" width="{(p1[0] - p0[0]) * 0.45:.1f}" height="{p0[1] - p1[1]:.1f}" fill="#D8C8A8"/>')
        if i < 7:
            a_, b_ = C(X + 1.4, 10.6, Zc), C(X + 3.6, 17.4, Zc)
            out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {a_[0]:.1f} {b_[1] + 3:.1f} Q {(a_[0] + b_[0]) / 2:.1f} {b_[1] - 2:.1f} {b_[0]:.1f} {b_[1] + 3:.1f} L {b_[0]:.1f} {a_[1]:.1f} Z" fill="#5E7A86"/>'
                       f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {a_[0]:.1f} {b_[1] + 3:.1f} Q {a_[0] + 1:.1f} {b_[1]:.1f} {(a_[0] + b_[0]) / 2:.1f} {b_[1] - 1:.1f} L {(a_[0] + b_[0]) / 2:.1f} {a_[1]:.1f} Z" fill="#BCD8E4" opacity="0.5"/>')
    out.append(f'<polyline points="{P([C(cx0, 8.6, Zc - 1), C(cx1, 8.6, Zc - 1)])}" fill="none" stroke="#FFFBF0" stroke-width="3"/>')
    for X in [cx0 + 1 + i * 1.6 for i in range(25)]:
        a_ = C(X, 8.6, Zc - 1)
        out.append(f'<rect x="{a_[0] - 0.7:.1f}" y="{a_[1] - 5:.1f}" width="1.4" height="5" fill="#FFFBF0"/>')
    out.append(f'<polyline points="{P([C(cx0, 9.8, Zc - 1), C(cx1, 9.8, Zc - 1)])}" fill="none" stroke="#FFFBF0" stroke-width="1.6"/>')
    out.append(poly(C.quad_z(Zc, cx0 - 0.4, cx1 + 0.4, yc + 4, yc + 4.8), "#FFF8E8"))
    at = C.quad_z(Zc, -9, 9, yc + 4.8, yc + 9.5)
    out.append(poly(at, f"url(#{u}-yel)"))
    out.append(f'<polyline points="{P([at[1], at[2]])}" fill="none" stroke="#FFFBF0" stroke-width="2.2"/>')
    ck = C(0, yc + 7.2, Zc)
    out.append(f'<circle cx="{ck[0]:.1f}" cy="{ck[1]:.1f}" r="6.4" fill="#FFFBF0"/><circle cx="{ck[0]:.1f}" cy="{ck[1]:.1f}" r="5" fill="#2E3A4E"/>'
               f'<path d="M {ck[0]:.1f} {ck[1]:.1f} L {ck[0]:.1f} {ck[1] - 3.6:.1f} M {ck[0]:.1f} {ck[1]:.1f} L {ck[0] + 2.4:.1f} {ck[1] + 1:.1f}" stroke="#F6CC5A" stroke-width="1.2"/>')
    for X, h_ in ((-8, 4.6), (8, 4.6), (-18, 3.6), (18, 3.6)):           # sculpture groups and trophies on the attic
        b0 = C(X, yc + (4.8 if abs(X) < 10 else 4.8), Zc)
        hh = 440 * h_ / Zc
        out.append(f'<path d="M {b0[0] - 3:.1f} {b0[1]:.1f} Q {b0[0] - 4:.1f} {b0[1] - hh * 0.6:.1f} {b0[0]:.1f} {b0[1] - hh:.1f} Q {b0[0] + 4:.1f} {b0[1] - hh * 0.6:.1f} {b0[0] + 3:.1f} {b0[1]:.1f} Z" fill="#F2ECE0"/>'
                   f'<path d="M {b0[0] + 1:.1f} {b0[1]:.1f} Q {b0[0] + 3.4:.1f} {b0[1] - hh * 0.6:.1f} {b0[0]:.1f} {b0[1] - hh:.1f}" fill="none" stroke="#B8AE9E" stroke-width="1.4"/>')
    # the double external staircase of the court front
    for sgn in (-1, 1):
        st = [C(sgn * 4, 8.6, Zc - 1), C(sgn * 4, 8.6, Zc - 3), C(sgn * 16, 0, Zc - 14), C(sgn * 22, 0, Zc - 14), C(sgn * 22, 1.2, Zc - 13)]
        out.append(poly([C(sgn * 4, 8.6, Zc - 1), C(sgn * 4, 7.6, Zc - 3), C(sgn * 20, 0, Zc - 14), C(sgn * 23, 0, Zc - 14), C(sgn * 23, 1.4, Zc - 13), C(sgn * 6, 9.2, Zc - 1)], "#F6F0E2"))
        out.append(f'<polyline points="{P([C(sgn * 6, 10.2, Zc - 1), C(sgn * 23, 2.4, Zc - 13)])}" fill="none" stroke="#FFFBF0" stroke-width="2"/>')
        for k in range(8):
            t = k / 8
            a_ = C(sgn * (4 + 16 * t), 8.6 * (1 - t), Zc - 1 - 13 * t)
            out.append(f'<line x1="{a_[0] - 3:.1f}" y1="{a_[1]:.1f}" x2="{a_[0] + 3:.1f}" y2="{a_[1]:.1f}" stroke="#C8B89E" stroke-width="0.8"/>')
    # the court: raked gravel in morning light, the two fountains, visitors
    ground = [C(-400, 0, ZF), C(400, 0, ZF), (620, 444), (-20, 444)]
    out.append(poly(ground, f"url(#{u}-grav)"))
    out.append(f'<rect x="-10" y="{C(0, 0, ZF)[1]:.1f}" width="620" height="2" fill="#B89A72" opacity="0.6"/>')
    out.append(dots(260, 97, (-10, 290, 610, 444), "#A88A62", r=(0.6, 1.6), opacity=(0.3, 0.7)))
    out.append(dots(160, 98, (-10, 290, 610, 444), "#FFF6E2", r=(0.6, 1.4), opacity=(0.4, 0.8)))
    for i in range(8):                       # rake lines converging on the palace
        X = -60 + i * 17
        out.append(line(C(X, 0, ZF - 10), C(X * 0.3, 0, 6), "#C8AA80", 1, ' opacity="0.35"'))
    for sgn in (-1, 1):
        fx, fy = C(sgn * 40, 0, 62)
        out.append(f'<ellipse cx="{fx:.1f}" cy="{fy:.1f}" rx="34" ry="5" fill="#E8DCC4"/><ellipse cx="{fx:.1f}" cy="{fy - 1.4:.1f}" rx="30" ry="3.6" fill="#8EB4C8"/>'
                   f'<path d="M {fx - 6:.1f} {fy - 2:.1f} Q {fx - 8:.1f} {fy - 18:.1f} {fx:.1f} {fy - 24:.1f} Q {fx + 8:.1f} {fy - 18:.1f} {fx + 6:.1f} {fy - 2:.1f} Z" fill="#E8E0D0"/>'
                   f'<path d="M {fx:.1f} {fy - 24:.1f} Q {fx - 10:.1f} {fy - 30:.1f} {fx - 18:.1f} {fy - 4:.1f} M {fx:.1f} {fy - 24:.1f} Q {fx + 10:.1f} {fy - 30:.1f} {fx + 18:.1f} {fy - 4:.1f}" fill="none" stroke="#E2F2FA" stroke-width="1.4" opacity="0.85"/>')
    for X, Z, c in ((22, 44, "#C8484E"), (23.2, 45, "#3E5A8E"), (-22, 70, "#F2E6D0"), (12, 90, "#5E7A4E"), (-52, 84, "#E8A040"), (54, 58, "#4E7A9E")):
        x_, y_ = C(X, 0, Z)
        h_ = 440 * 1.7 / Z
        out.append(f'<path d="M {x_:.1f} {y_:.1f} L {x_ + h_ * 0.9:.1f} {y_ + h_ * 0.12:.1f}" stroke="#A88660" stroke-width="{max(1.2, h_ * 0.12):.1f}" opacity="0.5"/>')
        out.append(figure(x_, y_, h_, c, rim="#FFF2D2", rim_side=-1))
    # the fiaker, with its long morning shadow thrown to the right
    fx, fy = C(-3.2, 0, 12.5)
    k_ = 0.98
    out.append(f'<path d="M {fx - 70 * k_:.1f} {fy + 1:.1f} L {fx + 196 * k_:.1f} {fy + 2:.1f} L {fx + 270 * k_:.1f} {fy + 16:.1f} L {fx:.1f} {fy + 14:.1f} Z" fill="#8A6A50" opacity="0.28"/>')
    # the shadow of the other gate obelisk, out of frame on the left, laid across the gravel
    out.append('<path d="M -10 414 L 250 392 L 254 398 L -10 432 Z" fill="#8A6A50" opacity="0.2"/>'
               '<path d="M 250 392 Q 262 384 280 386 Q 270 392 272 398 Q 262 400 254 398 Z" fill="#8A6A50" opacity="0.2"/>')
    out.append(fiaker(fx, fy, k_, u))
    out.append('<g fill="#6A6470">' + "".join(f'<path d="M {x} {y} q 4 -6 9 -3 l 3 -2 l 0 3 q -2 4 -9 4 Z"/><path d="M {x + 3} {y} l 0 3" stroke="#C88A4A" stroke-width="1"/>' for x, y in ((150, 404), (166, 410), (136, 414))) + "</g>")
    # the gate obelisk at the right with its gilded eagle; wrought-iron gate with gilt spear tips; the obelisk's long shadow
    out.append('<path d="M 560 444 L 610 420 L 610 444 Z" fill="#8A6A50" opacity="0.3"/>')
    out.append(f'<g>' + "".join(
        f'<line x1="{x}" y1="444" x2="{x}" y2="{376 + (x % 3) * 2}" stroke="#1E2420" stroke-width="2.6"/><path d="M {x - 3} {376 + (x % 3) * 2} L {x} {366 + (x % 3) * 2} L {x + 3} {376 + (x % 3) * 2} Z" fill="#F2C84E"/>'
        for x in range(436, 508, 9)) + '<rect x="432" y="396" width="80" height="3" fill="#1E2420"/><rect x="432" y="424" width="80" height="3" fill="#1E2420"/>'
        + "".join(f'<circle cx="{440 + i * 18}" cy="410" r="5" fill="none" stroke="#C89A30" stroke-width="2"/>' for i in range(4)) + '</g>')
    ox = 548
    out.append(f'<path d="M {ox - 22} 444 L {ox - 17} 214 L {ox + 17} 214 L {ox + 22} 444 Z" fill="url(#{u}-obl)"/>')
    out.append(f'<path d="M {ox - 32} 444 L {ox - 32} 404 L {ox + 32} 404 L {ox + 32} 444 Z" fill="#E2D6C2"/><path d="M {ox + 8} 404 L {ox + 32} 404 L {ox + 32} 444 L {ox + 8} 444 Z" fill="#A89C8C" opacity="0.6"/>'
               f'<rect x="{ox - 36}" y="398" width="72" height="8" fill="#F2EADA"/>')
    out.append(f'<path d="M {ox - 17} 214 L {ox} 192 L {ox + 17} 214 Z" fill="#EEE4D2"/><path d="M {ox} 192 L {ox + 17} 214 L {ox + 6} 214 Z" fill="#A89C8C"/>'
               f'<rect x="{ox - 12}" y="190" width="24" height="5" fill="#C89A30"/><circle cx="{ox}" cy="183" r="8" fill="#E8B848"/><circle cx="{ox - 3}" cy="180" r="3" fill="#FFF2B8" opacity="0.8"/>')
    out.append(f'<line x1="{ox - 17}" y1="216" x2="{ox - 22}" y2="440" stroke="#FFFBEE" stroke-width="2" opacity="0.8"/>')
    for yy in (260, 320):
        out.append(f'<line x1="{ox - 17 - (yy - 214) * 0.02:.1f}" y1="{yy}" x2="{ox + 17 + (yy - 214) * 0.02:.1f}" y2="{yy}" stroke="#C8BCA8" stroke-width="1" opacity="0.6"/>')
    out.append(gilded_eagle(ox, 176, 0.62, u))
    out.append(gulls([(400, 150, 8), (418, 158, 6)], "#3E5A7E", 1.6))
    return "\n".join(out)


# ================================================================ BERLIN — the Brandenburg Gate from Pariser Platz at sunset
def quadriga(cx, base, k, body="#3E4A52", rim="#FFC870", cop="#5E7E74"):
    """The quadriga seen from the front, against the low sun: four horses abreast, Victoria with her staff. k px per metre."""
    out = [f'<g transform="translate({cx:.1f} {base:.1f}) scale({k / 10:.3f})">']
    # chariot behind the horses
    out.append(f'<path d="M -22 -10 L 22 -10 L 18 -26 L -18 -26 Z" fill="{body}"/>')
    # Victoria: robe, wings raised behind, right arm holding the staff with the wreath, cross and eagle
    out.append(f'<path d="M -16 -40 Q -26 -66 -20 -84 Q -14 -70 -8 -60 Z M 16 -40 Q 26 -66 20 -84 Q 14 -70 8 -60 Z" fill="{body}"/>')
    out.append(f'<path d="M -9 -24 Q -11 -48 -5 -58 L 5 -58 Q 11 -48 9 -24 Z" fill="{body}"/><circle cx="0" cy="-63" r="4.2" fill="{body}"/>')
    out.append(f'<path d="M 4 -54 Q 12 -60 13 -70" fill="none" stroke="{body}" stroke-width="2.6" stroke-linecap="round"/>')
    out.append(f'<line x1="13" y1="-50" x2="13" y2="-92" stroke="{body}" stroke-width="1.8"/>'
               f'<circle cx="13" cy="-84" r="5.2" fill="none" stroke="{body}" stroke-width="2"/>'
               f'<path d="M 11 -87 L 15 -87 L 15 -85 L 17 -85 L 17 -83 L 15 -83 L 15 -81 L 11 -81 L 11 -83 L 9 -83 L 9 -85 L 11 -85 Z" fill="{body}"/>'
               f'<path d="M 7 -95 Q 13 -91 19 -95 L 17 -99 Q 13 -95 9 -99 Z M 12 -97 L 14 -97 L 13 -101 Z" fill="{body}"/>')
    # four horses abreast, chests toward us, the outer pair turning outward, forelegs raised in step
    for i, hx in enumerate((-31, -12, 12, 31)):
        turn = -1 if hx < 0 else 1
        lift_y = -4 if i in (1, 2) else 0
        out.append(f'<g transform="translate({hx} {lift_y})">')
        out.append(f'<ellipse cx="0" cy="-20" rx="7.2" ry="9" fill="{body}"/>')
        out.append(f'<path d="M -5 -26 Q {-3 + turn * 2} -42 {turn * 3} -46 Q {turn * 8} -46 {turn * 7} -40 Q {turn * 5} -34 {turn * 6} -30 L {turn * 9} -28 Q {turn * 10} -26 {turn * 8} -24 Q {turn * 3} -24 4 -22 Z" fill="{body}"/>')
        out.append(f'<path d="M {turn * 1} -46 L {turn * 0} -51 L {turn * 3} -47 Z" fill="{body}"/>')
        lift = 1 if i % 2 == 0 else -1
        out.append(f'<path d="M -3 -14 L {-3 - lift * 1} 0 M 3 -14 Q {3 + lift * 5} -10 {3 + lift * 4} -4" fill="none" stroke="{body}" stroke-width="2.6" stroke-linecap="round"/>')
        out.append(f'<path d="M -6 -26 Q {-3 + turn * 2} -42 {turn * 3} -46" fill="none" stroke="{rim}" stroke-width="1.2" opacity="0.85"/>')
        out.append('</g>')
    # rim of sunlight along Victoria and the wings
    out.append(f'<path d="M -20 -84 Q -26 -66 -16 -40 M 20 -84 Q 26 -66 16 -40" fill="none" stroke="{rim}" stroke-width="1.4" opacity="0.9"/>'
               f'<path d="M -4 -67 Q 0 -69 4 -67" fill="none" stroke="{rim}" stroke-width="1.2"/>'
               f'<path d="M 9 -87 Q 13 -91 17 -87" fill="none" stroke="{rim}" stroke-width="1.2"/>')
    out.append("</g>")
    return "".join(out)


def cyclist(x, base, h, body="#2A2030", rim="#FFC870", bike="#2A2030", flip=False):
    """A cyclist seen from the side, riding right, backlit by the sun."""
    s = h / 100.0
    sx = -s if flip else s
    return (f'<g transform="translate({x:.1f} {base:.1f}) scale({sx:.3f} {s:.3f})">'
            '<path d="M -70 2 L 70 2 L 120 26 L -20 26 Z" fill="#3A2440" opacity="0.28"/>'
            f'<circle cx="-34" cy="-22" r="21" fill="none" stroke="{bike}" stroke-width="3.4"/><circle cx="34" cy="-22" r="21" fill="none" stroke="{bike}" stroke-width="3.4"/>'
            f'<circle cx="-34" cy="-22" r="21" fill="none" stroke="{rim}" stroke-width="1.2" opacity="0.5" stroke-dasharray="14 52"/>'
            f'<path d="M -34 -22 L -8 -22 L 18 -50 L -14 -50 Z M -8 -22 L -16 -56 M 34 -22 L 22 -62 L 14 -64 M -20 -58 L -10 -58" fill="none" stroke="{bike}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<rect x="20" y="-58" width="16" height="10" rx="2" fill="#C8484E"/><path d="M 22 -58 Q 28 -64 34 -58" fill="none" stroke="#3E7A4E" stroke-width="2"/>'
            f'<path d="M -16 -60 Q -10 -96 2 -100 Q 12 -98 14 -88 L 18 -66 L 12 -64 L 6 -84 Q -2 -78 -4 -60 Z" fill="{body}"/>'
            f'<path d="M -16 -60 L -2 -40 L -6 -22 M -10 -58 L 6 -48 L 2 -30" fill="none" stroke="{body}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
            '<circle cx="6" cy="-110" r="9" fill="#2A2030"/><path d="M -3 -114 Q 6 -124 15 -114 L 16 -110 L -4 -110 Z" fill="#E8B848"/>'
            f'<path d="M -16 -62 Q -12 -94 0 -100" fill="none" stroke="{rim}" stroke-width="3" opacity="0.9"/>'
            f'<path d="M -3 -116 Q 0 -120 4 -121" fill="none" stroke="{rim}" stroke-width="2.4"/>'
            '</g>')


def berlin():
    u = "berlin"
    C = Cam(f=460, cx=300, vpy=319, eye=1.7)
    ZG = 70.0
    k = 460 / ZG
    out = [defs(
        lg(f"{u}-sky", [(0, "#3A2E6A"), (0.25, "#7A4A86"), (0.5, "#D86A6E"), (0.72, "#F69A5A"), (0.88, "#FFC874"), (1, "#FFE6A8")], 0, 40, 0, 330, units="userSpaceOnUse"),
        lg(f"{u}-gate", [(0, "#A07A84"), (0.6, "#7E5E70"), (1, "#5E4458")]),
        lg(f"{u}-col", [(0, "#FFD08A"), (0.12, "#A47E80"), (0.55, "#7A5A6C"), (1, "#5A4256")], 0, 0, 1, 0),
        lg(f"{u}-plaza", [(0, "#C88A7A"), (0.25, "#9A6A72"), (1, "#5A3E52")], 0, 330, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-ray", [(0, "#FFD08A", 0.75), (1, "#FFD08A", 0)], 0, 330, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(300, 304, 260, "#FFE2A0", f"{u}-sun", 0.9))
    for x, y, w, c in ((110, 110, 140, "#E89A8A"), (60, 128, 80, "#F6B28A"), (480, 96, 150, "#C87A9A"), (540, 122, 70, "#F0A08A"), (300, 150, 120, "#FFC08A"), (200, 176, 80, "#FFD098")):
        out.append(streak_cloud(x, y, w, c, 0.6, 4.4))
        out.append(streak_cloud(x - 12, y + 3, w * 0.6, "#FFE6B8", 0.5, 1.8))
        out.append(streak_cloud(x + 10, y - 3, w * 0.7, "#8A5A8A", 0.35, 1.6))
    # Tiergarten treetops on the horizon beyond the gate, the Victory Column far down the axis
    tg = rough([(-10, 318), (100, 312), (200, 314), (300, 311), (400, 313), (500, 310), (610, 316)], 101, amp=3, depth=4)
    out.append(poly(tg + [(610, 334), (-10, 334)], "#B8606E"))
    out.append(blobs(60, 102, (0, 306, 600, 318), ["#B8606E", "#A85868"], r=(4, 9), opacity=(0.9, 1), squash=0.8))
    out.append(f'<rect x="298.6" y="290" width="2.8" height="26" fill="#9A4E62"/><rect x="297" y="300" width="6" height="3" fill="#9A4E62"/>'
               f'<path d="M 297.5 290 L 300 284 L 302.5 290 Z" fill="#FFD27A"/><circle cx="300" cy="306" r="18" fill="#FFF2C8" opacity="0.35"/>')
    sun_c = (300, 300)
    out.append(f'<circle cx="{sun_c[0]}" cy="{sun_c[1] + 6}" r="13" fill="#FFF6D8" opacity="0.95"/>')
    # the houses flanking the gate on Pariser Platz, in shadow, a few lit windows
    rnd = random.Random(103)
    for sgn in (-1, 1):
        q = C.quad_z(ZG + 6, sgn * 34, sgn * 70, 0, 21)
        out.append(poly(q, "#6A4A62"))
        r0 = C.quad_z(ZG + 6, sgn * 34, sgn * 70, 21, 25)
        out.append(poly([r0[0], (r0[1][0] + sgn * 8, r0[1][1]), (r0[2][0] - sgn * 8, r0[2][1]), r0[3]], "#4E3A52"))
        for fl in range(5):
            for c_ in range(10):
                X = sgn * (36 + c_ * 3.4)
                a_, b_ = C(X, 2.5 + fl * 3.8, ZG + 6), C(X + sgn * 1.4, 4.6 + fl * 3.8, ZG + 6)
                lit_ = rnd.random() < 0.25
                out.append(f'<rect x="{min(a_[0], b_[0]):.1f}" y="{b_[1]:.1f}" width="{abs(b_[0] - a_[0]):.1f}" height="{a_[1] - b_[1]:.1f}" fill="{"#FFD27A" if lit_ else "#4A3450"}"/>')
    # ---- the gate: side guard houses, attic, entablature, six Doric columns and the open passages
    gate_c = f"url(#{u}-gate)"
    for sgn in (-1, 1):                      # the two little temple-fronted guard houses
        x0, x1 = sgn * 17, sgn * 32
        out.append(poly(C.quad_z(ZG + 2, x0, x1, 0, 10.5), "#7A5A6C"))
        out.append(poly(C.quad_z(ZG + 2, x0, x1, 10.5, 12.2), "#8E6A7A"))
        out.append(f'<polyline points="{P([C(x0, 12.2, ZG + 2), C(x1, 12.2, ZG + 2)])}" fill="none" stroke="#FFC870" stroke-width="1.6" opacity="0.8"/>')
        for i in range(4):
            X = x0 + sgn * (1.8 + i * 3.8)
            a_, b_ = C(X - 0.55, 0, ZG + 1), C(X + 0.55, 10.4, ZG + 1)
            out.append(f'<rect x="{a_[0]:.1f}" y="{b_[1]:.1f}" width="{b_[0] - a_[0]:.1f}" height="{a_[1] - b_[1]:.1f}" fill="url(#{u}-col)"/>')
        for i in range(3):
            X = x0 + sgn * (3.7 + i * 3.8)
            a_, b_ = C(X - 1, 1, ZG + 2), C(X + 1, 7, ZG + 2)
            out.append(f'<rect x="{a_[0]:.1f}" y="{b_[1]:.1f}" width="{b_[0] - a_[0]:.1f}" height="{a_[1] - b_[1]:.1f}" fill="#5A4256"/>')
    # main block: entablature with triglyphs and the relief metopes, stepped attic with the relief panel
    E0, E1, A0, A1 = 13.4, 16.2, 16.2, 20.6
    W = 16.2
    out.append(poly(C.quad_z(ZG, -W, W, E0, E1), gate_c))
    out.append(f'<polyline points="{P([C(-W, E0 + 0.9, ZG), C(W, E0 + 0.9, ZG)])}" fill="none" stroke="#5A4256" stroke-width="1.2"/>')
    for i in range(23):
        X = -W + 0.7 + i * (2 * W - 1.4) / 22
        a_, b_ = C(X - 0.35, E0 + 1.1, ZG), C(X + 0.35, E1 - 0.4, ZG)
        out.append(f'<rect x="{a_[0]:.1f}" y="{b_[1]:.1f}" width="{b_[0] - a_[0]:.1f}" height="{a_[1] - b_[1]:.1f}" fill="#5A4256"/>')
        if i < 22:
            m_ = C(X + 0.72, E0 + 1.8, ZG)
            out.append(f'<ellipse cx="{m_[0]:.1f}" cy="{m_[1] - 2:.1f}" rx="2.2" ry="2.6" fill="#8E6A7A"/>')
    out.append(poly(C.quad_z(ZG, -W - 0.4, W + 0.4, E1 - 0.4, E1 + 0.3), "#9A7484"))
    out.append(f'<polyline points="{P([C(-W - 0.4, E1 + 0.3, ZG), C(W + 0.4, E1 + 0.3, ZG)])}" fill="none" stroke="#FFC870" stroke-width="2" opacity="0.9"/>')
    out.append(poly(C.quad_z(ZG, -W + 0.6, W - 0.6, A0 + 0.3, A1 - 1.4), gate_c))
    out.append(poly(C.quad_z(ZG, -8.8, 8.8, A1 - 1.4, A1 + 0.6), gate_c))
    out.append(f'<polyline points="{P([C(-W + 0.6, A1 - 1.4, ZG), C(-8.8, A1 - 1.4, ZG), C(-8.8, A1 + 0.6, ZG), C(8.8, A1 + 0.6, ZG), C(8.8, A1 - 1.4, ZG), C(W - 0.6, A1 - 1.4, ZG)])}" fill="none" stroke="#FFC870" stroke-width="1.8" opacity="0.9"/>')
    rp = C.quad_z(ZG, -7.6, 7.6, A0 + 0.9, A1 - 1.0)
    out.append(poly(rp, "#6A4E62"))
    rnd = random.Random(104)
    for i in range(14):                   # the relief: a procession, just suggested
        X = -7 + i * 1.05
        a_ = C(X, A0 + 1.0, ZG)
        hh_ = rnd.uniform(9, 12)
        out.append(f'<rect x="{a_[0]:.1f}" y="{a_[1] - hh_:.1f}" width="2.6" height="{hh_:.1f}" rx="1.3" fill="#86687A" opacity="0.8"/><circle cx="{a_[0] + 1.3:.1f}" cy="{a_[1] - hh_ - 1.6:.1f}" r="1.6" fill="#86687A" opacity="0.8"/>')
    # columns and passages (the sky and sun visible through them)
    xs = [-14.8, -9.25, -3.7, 3.7, 9.25, 14.8]
    for X in xs:
        a_, b_ = C(X - 0.9, 0, ZG), C(X + 0.9, E0, ZG)
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {a_[0] + 1:.1f} {b_[1]:.1f} L {b_[0] - 1:.1f} {b_[1]:.1f} L {b_[0]:.1f} {a_[1]:.1f} Z" fill="url(#{u}-col)"/>')
        for f_ in (0.3, 0.55, 0.8):
            xx = a_[0] + (b_[0] - a_[0]) * f_
            out.append(f'<line x1="{xx:.1f}" y1="{a_[1]:.1f}" x2="{xx:.1f}" y2="{b_[1]:.1f}" stroke="#4A3448" stroke-width="0.8" opacity="0.4"/>')
        cap = C.quad_z(ZG, X - 1.15, X + 1.15, E0 - 0.5, E0)
        out.append(poly(cap, "#9A7484"))
        # sunlit edge where the light wraps round the column
        out.append(f'<line x1="{b_[0] - 0.8:.1f}" y1="{a_[1]:.1f}" x2="{b_[0] - 1.6:.1f}" y2="{b_[1]:.1f}" stroke="#FFC870" stroke-width="1.6" opacity="0.85"/>')
    # the walls dividing the passages, seen edge-on just behind the columns
    for X in xs[1:-1]:
        a_, b_ = C(X - 0.5, 0, ZG + 2), C(X + 0.5, E0, ZG + 2)
        out.append(f'<rect x="{a_[0]:.1f}" y="{b_[1]:.1f}" width="{b_[0] - a_[0]:.1f}" height="{a_[1] - b_[1]:.1f}" fill="#5A4256" opacity="0.0"/>')
    # quadriga on top
    qb = C(0, A1 + 0.6, ZG)
    out.append(quadriga(qb[0], qb[1], k * 1.3, body="#3A3A4C", rim="#FFC870"))
    # ---- Pariser Platz: granite paving in long shadow, gold light pouring through the five passages
    plaza = [(-10, 330), (610, 330), (610, 444), (-10, 444)]
    out.append(poly(plaza, f"url(#{u}-plaza)"))
    out.append(f'<clipPath id="{u}-pz"><polygon points="{P(plaza)}"/></clipPath>')
    rays = []
    edges = [(-16.2, -14.8 + 0.9), (-14.8 - 0.9, -9.25 + 0.9)]
    gaps = [(xs[i] + 0.9, xs[i + 1] - 0.9) for i in range(5)]
    for (a, b) in gaps:
        rays.append(poly([C(a, 0, ZG), C(b, 0, ZG), C(b * 1.05, 0, 3), C(a * 1.05, 0, 3)], f"url(#{u}-ray)"))
    pav = []
    z = 6.0
    while z < ZG:
        a_, b_ = C(-60, 0, z), C(60, 0, z)
        pav.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#3E2A40" stroke-width="{max(0.5, 14 / z):.2f}" opacity="0.3"/>')
        z *= 1.12
    for X in range(-60, 61, 4):
        a_, b_ = C(X, 0, 4), C(X, 0, ZG)
        pav.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#3E2A40" stroke-width="0.8" opacity="0.2"/>')
    out.append(f'<g clip-path="url(#{u}-pz)">' + "".join(pav) + "".join(rays) + "</g>")
    out.append(f'<rect x="-10" y="329" width="620" height="2.4" fill="#FFD08A" opacity="0.7"/>')
    # people strolling, long shadows toward us
    for X, Z, c in ((-6, 40, "#4A3A58"), (-5.2, 41, "#C8484E"), (8, 34, "#3E4A6E"), (-20, 30, "#2E3A4E"), (12.5, 52, "#4A3A58"), (22, 26, "#5E4A3E")):
        x_, y_ = C(X, 0, Z)
        h_ = 460 * 1.75 / Z
        out.append(f'<path d="M {x_ - h_ * 0.08:.1f} {y_:.1f} L {x_ + h_ * 0.08:.1f} {y_:.1f} L {x_ + h_ * 0.12 + X * 0.3:.1f} {y_ + h_ * 0.9:.1f} L {x_ - h_ * 0.1 + X * 0.3:.1f} {y_ + h_ * 0.9:.1f} Z" fill="#3A2440" opacity="0.3"/>')
        out.append(figure(x_, y_, h_, c, head="#2A1E28", legs="#2A2030", rim="#FFC870", rim_side=1))
    # the cyclist gliding across the square
    cx_, cy_ = C(-4, 0, 12.5)
    out.append(cyclist(cx_, cy_, 460 * 1.8 / 12.5, rim="#FFC870"))
    out.append(f'<g fill="#4A3450">' + "".join(f'<path d="M {x} {y} q 3 -5 7 -3 l 3 -1.5 l -0.5 3 q -2 3 -7 3 Z"/>' for x, y in ((392, 404), (404, 408), (380, 412))) + "</g>")
    # the lime trees of Unter den Linden framing both sides, backlit: dark crowns with glowing edges and sky showing through
    for sgn, x, seed in ((-1, 34, 105), (1, 568, 106)):
        out.append(f'<path d="M {x - 11} 444 Q {x - 6} 330 {x - 4} 200 L {x + 7} 200 Q {x + 8} 330 {x + 13} 444 Z" fill="#2A1E2A"/>')
        rim_x = x + 13 if sgn < 0 else x - 11
        out.append(f'<path d="M {rim_x} 444 Q {x + (8 if sgn < 0 else -6)} 330 {x + (7 if sgn < 0 else -4)} 200" fill="none" stroke="#FFC870" stroke-width="1.8" opacity="0.7"/>')
        out.append(f'<path d="M {x + 1} 300 Q {x - sgn * 36} 252 {x - sgn * 66} 214" fill="none" stroke="#2A1E2A" stroke-width="5" stroke-linecap="round"/>')
        out.append(f'<path d="M {x + 1} 250 Q {x - sgn * 20} 200 {x - sgn * 30} 150" fill="none" stroke="#2A1E2A" stroke-width="4" stroke-linecap="round"/>')
        out.append(leaf_canopy(f"{u}-ln{sgn}", x - sgn * 40, 70, 130, 120, seed, "#1A161C", "#2A2626", "#3A3430", gold=None,
                               light=(-sgn, 0.3), n=130, holes="#C8787E", r=(0.12, 0.22)))
        out.append(leaf_canopy(f"{u}-lm{sgn}", x - sgn * 72, 196, 56, 30, seed + 10, "#1A161C", "#2A2626", "#3A3430", gold=None,
                               light=(-sgn, 0.3), n=40, holes="#E8A07A", r=(0.18, 0.3)))
        # heart-shaped linden leaves hanging at the edge of the crown, lit through
        rnd = random.Random(seed + 20)
        for _ in range(18):
            lx_ = x - sgn * rnd.uniform(60, 150)
            ly_ = rnd.uniform(120, 230)
            if ly_ > 70 + 120 * math.sqrt(max(0, 1 - ((lx_ - (x - sgn * 40)) / 130) ** 2)) + 6:
                continue
            r_ = rnd.uniform(4, 6.5)
            out.append(f'<path d="M {lx_:.1f} {ly_ + r_:.1f} C {lx_ - r_ * 1.4:.1f} {ly_:.1f} {lx_ - r_:.1f} {ly_ - r_ * 1.1:.1f} {lx_:.1f} {ly_ - r_ * 0.4:.1f} '
                       f'C {lx_ + r_:.1f} {ly_ - r_ * 1.1:.1f} {lx_ + r_ * 1.4:.1f} {ly_:.1f} {lx_:.1f} {ly_ + r_:.1f} Z" fill="{rnd.choice(["#B8963E", "#8E7A34", "#D8B050"])}" opacity="0.85"/>')
    out.append(gulls([(210, 196, 8), (226, 204, 6), (380, 190, 7)], "#4A2E4E", 1.6))
    return "\n".join(out)


BUILD = {
    "athens": (athens, "ATHENS", "GREECE · EUROPE", "#353D22", "#E8B65A", "#FBF0D8", "#E8C878"),
    "dubrovnik": (dubrovnik, "DUBROVNIK", "CROATIA · ADRIATIC", "#0F4566", "#E8743A", "#FFF4E6", "#F6B07A"),
    "prague": (prague, "PRAGUE", "CZECHIA · EUROPE", "#3A2C48", "#F2A88E", "#FFF0E6", "#F6BCA8"),
    "budapest": (budapest, "BUDAPEST", "HUNGARY · EUROPE", "#1A1C42", "#F2B860", "#FFF2DC", "#F6C27A"),
    "vienna": (vienna, "VIENNA", "AUSTRIA · EUROPE", "#6E1E2A", "#E8B848", "#FFF6E2", "#F2CC6E"),
    "berlin": (berlin, "BERLIN", "GERMANY · EUROPE", "#2A1E34", "#F29A5A", "#FFF0E0", "#F6B07A"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("world", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
