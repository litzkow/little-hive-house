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
    def __init__(self, f, H, phi, cx=300, cy=300, cam_x=0.0):
        self.f, self.H, self.cx, self.cy, self.camx = f, H, cx, cy, cam_x
        self.s, self.c = math.sin(math.radians(phi)), math.cos(math.radians(phi))

    def __call__(self, X, Y, Z):
        dy = Y - self.H
        zc = -dy * self.s + Z * self.c
        yc = dy * self.c + Z * self.s
        return (self.cx + self.f * (X - self.camx) / zc, self.cy - self.f * yc / zc)

    def depth(self, X, Y, Z):
        return -(Y - self.H) * self.s + Z * self.c


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
            '<path d="M -8 1 Q -40 4 -80 10 M -8 2 Q -36 10 -66 18" fill="none" stroke="#FFFFFF" stroke-width="1.8" opacity="0.7"/>'
            f'<path d="M -8 -2 L 10 -2 L 6 2 L -8 2 Z" fill="{col}"/><rect x="-4" y="-5" width="7" height="3" fill="#2E4A6A"/></g>')


def dubrovnik():
    u = "dubrovnik"
    C = PCam(f=700, H=150, phi=16, cx=300, cy=332, cam_x=-30)
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
    isl = [C(X, 0, Z) for X, Z in ((-380, 1260), (-560, 1180), (-820, 1210), (-1100, 1380), (-1200, 1560), (-900, 1700), (-600, 1560))]
    xs_ = sorted(p[0] for p in isl)
    top_ = rough([(xs_[0], isl[0][1] - 1), (xs_[0] + 30, isl[0][1] - 10), (xs_[0] + 90, isl[0][1] - 17), (xs_[0] + 130, isl[0][1] - 12), (xs_[-1], isl[0][1] - 2)], 21, amp=3, depth=3)
    by = max(p[1] for p in isl)
    out.append(poly(top_ + [(xs_[-1], by + 2), (xs_[0], by + 2)], "#2E5A3E"))
    out.append(tree_line(top_, 22, ["#2A4E36", "#355E40", "#3E6A44"], density=4, hmin=4, hmax=8, xmin=xs_[0] + 4, xmax=xs_[-1] - 4, sink=3))
    out.append(f'<polyline points="{P([(xs_[0], by + 1), (xs_[-1], by + 1)])}" fill="none" stroke="#E8E4D8" stroke-width="1.6"/>')
    fx = xs_[0] + 92
    out.append(f'<rect x="{fx - 5:.1f}" y="{isl[0][1] - 22:.1f}" width="10" height="7" fill="#D8D0C0"/>')
    # coast: the rock the town stands on, washed by surf
    rock = [(-260, 720), (-268, 800), (-200, 836), (-80, 848), (40, 852), (140, 836), (205, 806), (238, 770), (250, 720), (240, 640)]
    rk = [C(X, 0, Z) for X, Z in rock]
    out.append(poly(rk + [C(240, 0, 600), C(-260, 0, 600)], "#C8BCA8"))
    out.append(f'<polyline points="{P(rk[:-1])}" fill="none" stroke="#FFFFFF" stroke-width="2.2" opacity="0.85"/>')
    out.append(f'<polyline points="{P([(x, y + 2.4) for x, y in rk[:-1]])}" fill="none" stroke="#9ADCE0" stroke-width="2" opacity="0.7"/>')
    # Fort Lovrijenac on its cliff, beyond the Pile inlet
    lx, ly = C(300, 0, 740)
    cliff = rough([(lx - 34, ly + 6), (lx - 24, ly - 26), (lx + 10, ly - 32), (lx + 60, ly - 26), (lx + 80, ly + 4)], 31, amp=3, depth=2)
    out.append(poly(cliff, "#B8AC98"))
    out.append(poly([(lx - 22, ly - 26), (lx - 18, ly - 52), (lx + 34, ly - 56), (lx + 44, ly - 30)], lit("#E8DCC4", (0, 0, -1))))
    out.append(poly([(lx + 34, ly - 56), (lx + 54, ly - 50), (lx + 58, ly - 26), (lx + 44, ly - 30)], lit("#E8DCC4", (1, 0, 0))))
    out.append(f'<path d="M {lx - 18} {ly - 52} L {lx + 34} {ly - 56} L {lx + 54} {ly - 50}" fill="none" stroke="#5A4A5A" stroke-width="1.8" stroke-dasharray="2 2"/>')
    out.append(f'<polyline points="{lx - 34},{ly + 6} {lx + 80},{ly + 4}" fill="none" stroke="#FFFFFF" stroke-width="2"/>')

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
        nx, nz = (bz - az) / L, -(bx - ax) / L          # outward normal (outline runs clockwise seen from above)
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            px0, pz0 = ax + (bx - ax) * t0, az + (bz - az) * t0
            px1, pz1 = ax + (bx - ax) * t1, az + (bz - az) * t1
            g0 = db_ground(px0, pz0)
            g1 = db_ground(px1, pz1)
            sea = pz0 > 700 or px0 > 205 or px0 < -228
            top0 = (g0 + 20) if not sea else 22
            top1 = (g1 + 20) if not sea else 22
            b0, b1 = (g0 - 14, g1 - 14) if not sea else (0, 0)
            T = 5.0
            o0, o1 = (px0 + nx * T, pz0 + nz * T), (px1 + nx * T, pz1 + nz * T)
            face = []
            camv = (C.camx - (px0 + px1) / 2, -(pz0 + pz1) / 2)
            if nx * camv[0] + nz * camv[1] > 0:          # outer face toward us
                q = [C(o0[0], b0, o0[1]), C(o0[0], top0, o0[1]), C(o1[0], top1, o1[1]), C(o1[0], b1, o1[1])]
                fc = lit("#E2D2B6", (nx, 0, nz))
                face.append(poly(q, fc))
                face.append(line(q[1], q[2], mix(fc, "#FFFFFF", 0.4), 2.2, ' stroke-dasharray="1.6 1.6"'))
                face.append(poly([q[0], (q[0][0], q[0][1] - (q[0][1] - q[1][1]) * 0.18), (q[3][0], q[3][1] - (q[3][1] - q[2][1]) * 0.18), q[3]], "#6E5A6A", ' opacity="0.2"'))
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
    # foreground: the hillside below us, pines and cypresses, a bougainvillea-draped terrace wall
    hill = rough([(-10, 352), (60, 350), (130, 360), (200, 368), (300, 372), (400, 366), (480, 354), (560, 348), (610, 352)], 41, amp=4, depth=3)
    out.append(poly(hill + [(610, 444), (-10, 444)], f"url(#{u}-hill)"))
    out.append(blobs(60, 42, (-10, 360, 610, 444), ["#4E6E3A", "#5E7E44", "#3A5634", "#7E944E"], r=(6, 16), opacity=(0.6, 0.95), squash=0.6))
    rnd = random.Random(43)
    for _ in range(9):
        x = rnd.uniform(0, 600)
        out.append(cypress_tree(x, rnd.uniform(392, 430), rnd.uniform(40, 70), rnd.uniform(9, 13), rnd.random() * 99, "#22361E", "#33502A", "#7E9A4A"))
    for k_, (x, base, h, sp) in enumerate(((36, 444, 150, 120), (566, 444, 170, 140))):
        out.append(umbrella_pine(x, base, h, sp, 60 + k_, lean=0.08 if x < 300 else -0.06, dark="#1E3222", mid="#2E4A2C", lit="#7E9A4A", gold="#C8D070", trunk="#4A3A30", trunk_lit="#C89A6A"))
    # terrace wall with bougainvillea in the bottom-left corner
    out.append(poly([(-10, 420), (180, 412), (190, 444), (-10, 444)], "#D8C8A8"))
    out.append(f'<g stroke="#A8987E" stroke-width="1" opacity="0.7">' + "".join(
        f'<line x1="-10" y1="{420 + k * 6}" x2="{180 + k * 1.6:.0f}" y2="{412 + k * 6}"/>' for k in range(1, 6)) + "</g>")
    out.append(f'<polyline points="-10,420 180,412" fill="none" stroke="#FFF6E0" stroke-width="2.2"/>')
    out.append(leaf_canopy(f"{u}-bg", 70, 414, 70, 18, 77, "#7A1E4E", "#C2307A", "#F06AAE", gold="#FFB0D8", n=70, r=(0.2, 0.4)))
    out.append(dots(40, 78, (10, 400, 140, 430), "#3E6A2E", r=(1.4, 2.6), opacity=(0.6, 0.9)))
    out.append(gulls([(330, 118, 10), (350, 128, 7), (200, 100, 8)], "#2A4A6A", 1.8))
    return "\n".join(out)


BUILD = {
    "athens": (athens, "ATHENS", "GREECE · EUROPE", "#353D22", "#E8B65A", "#FBF0D8", "#E8C878"),
    "dubrovnik": (dubrovnik, "DUBROVNIK", "CROATIA · ADRIATIC", "#0F4566", "#E8743A", "#FFF4E6", "#F6B07A"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("world", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
