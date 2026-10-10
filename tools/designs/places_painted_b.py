"""American Places, painted edition (part B): St. Augustine, New Orleans, Charleston, Seattle, Boston,
Philadelphia and Yosemite repainted as small gouache scenes — real viewpoints, light, haze and life."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from places_painted import Cam, palm_tree, puff_column
from common import SERIF_IT, MONO
from poster import ANTON, poster
import figures as F


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


def poly(pts, fill, extra=""):
    return f'<polygon points="{P(pts)}" fill="{fill}"{extra}/>'


def cumulus(cx, base, w, h, seed, grad, hi="#FFFFFF", hi_op=0.7, shade="#8E9CB8", shade_op=0.22, n=None):
    """Fair-weather cumulus: flat base, piled puffs, lit tops, shaded underside (one shared gradient)."""
    rnd = random.Random(seed)
    n = n or int(w / 6)
    body, lights, shades = [], [], []
    for _ in range(n):
        t = rnd.random()
        x = cx + (t - 0.5) * w
        env = math.sin(math.pi * t) ** 0.8
        top = base - h * env * rnd.uniform(0.55, 1.0)
        r = max(6, (base - top) * rnd.uniform(0.35, 0.6))
        y = min(base - r * 0.55, top + r)
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>')
        lights.append(f'<circle cx="{x - r * 0.18:.1f}" cy="{y - r * 0.3:.1f}" r="{r * 0.62:.1f}"/>')
        if rnd.random() < 0.6:
            shades.append(f'<ellipse cx="{x + r * 0.2:.1f}" cy="{base - r * 0.15:.1f}" rx="{r * 0.9:.1f}" ry="{r * 0.35:.1f}"/>')
    cid = f"{grad}-c{seed}"
    return (f'<clipPath id="{cid}"><rect x="{cx - w}" y="{base - h * 1.5}" width="{2 * w}" height="{h * 1.5}"/></clipPath>'
            f'<g clip-path="url(#{cid})"><g fill="url(#{grad})">' + "".join(body) + "</g>"
            + f'<g fill="{shade}" opacity="{shade_op}">' + "".join(shades) + "</g>"
            + f'<g fill="{hi}" opacity="{hi_op}">' + "".join(lights) + "</g></g>")


def gulls(spec, color="#3A3A4A", sw=2):
    return (f'<g fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
            + "".join(f'<path d="M {x} {y} q {s * 0.5:.1f} {-s * 0.4:.1f} {s:.1f} 0 q {s * 0.5:.1f} {-s * 0.4:.1f} {s:.1f} 0"/>' for x, y, s in spec) + "</g>")


def figure(x, base, h, coat, legs="#2A2420", head="#3A2A22", rim=None, skirt=False, hat=None, pose="stand_34", facing=1, light=-1, seed=None, pal=None, tint=None):
    """Small painted person (figures.py), base = feet. skirt -> a woman in a dress or skirt; hat -> a sun hat."""
    p = {"top": coat}
    if skirt:
        p.update(form="f", top_kind="dress")
    if hat:
        p.update(hat_kind="sunhat", hat=hat)
    p.update(pal or {})
    return F.person(x, base, h, pose, facing, p, seed=int(x * 3 + base * 7) if seed is None else seed, rim=rim, light=light, tint=tint)


# ---------------------------------------------------------------- St. Augustine (the Castillo by the bay)
def galleon(x, y, s, hull="#4A2E22", trim="#D8A94A", sail="#F4EAD2", sail_sh="#C9B994", flag="#C23A2E"):
    """Spanish-style galleon sailing left; (x, y) = waterline centre, s = scale (1 -> 120 px long)."""
    out = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">']
    # hull with a high stern castle on the right
    out.append(poly([(-58, -14), (-40, -8), (34, -8), (40, -26), (58, -30), (60, -14), (52, 2), (-44, 2)], hull))
    out.append(poly([(-56, -13), (-40, -7), (34, -7), (36, -12), (-46, -12)], trim, ' opacity="0.9"'))
    out.append(f'<rect x="38" y="-26" width="20" height="3" fill="{trim}"/>')
    out.append("".join(f'<rect x="{-30 + i * 9}" y="-5" width="4" height="3" fill="#1E120C"/>' for i in range(8)))
    out.append(f'<rect x="44" y="-21" width="4" height="4" fill="#FFD98E"/><rect x="51" y="-21" width="4" height="4" fill="#FFD98E"/>')
    out.append(f'<line x1="-58" y1="-14" x2="-86" y2="-30" stroke="{hull}" stroke-width="2.4"/>')
    # masts, yards and bellied square sails
    for mx, top, k in ((-30, -96, 0.8), (2, -112, 1.0), (32, -84, 0.7)):
        out.append(f'<line x1="{mx}" y1="-8" x2="{mx}" y2="{top}" stroke="#3A241A" stroke-width="2.6"/>')
        for j, (y0, h, w) in enumerate(((top + 30 * k, 26 * k, 24 * k), (top + 8 * k, 20 * k, 18 * k))):
            if y0 + h > -12:
                continue
            out.append(f'<path d="M {mx - w:.1f} {y0:.1f} Q {mx - 4:.1f} {y0 + 3:.1f} {mx + w:.1f} {y0:.1f} Q {mx + w + 3:.1f} {y0 + h * 0.6:.1f} {mx + w - 2:.1f} {y0 + h:.1f} Q {mx - 4:.1f} {y0 + h + 4:.1f} {mx - w + 2:.1f} {y0 + h:.1f} Q {mx - w - 3:.1f} {y0 + h * 0.6:.1f} {mx - w:.1f} {y0:.1f} Z" fill="{sail}"/>')
            out.append(f'<path d="M {mx + w * 0.2:.1f} {y0 + 1:.1f} Q {mx + w + 3:.1f} {y0 + h * 0.6:.1f} {mx + w - 2:.1f} {y0 + h:.1f} Q {mx + w * 0.4:.1f} {y0 + h + 3:.1f} {mx + w * 0.2:.1f} {y0 + h + 2:.1f} Z" fill="{sail_sh}" opacity="0.7"/>')
            out.append(f'<line x1="{mx - w - 2:.1f}" y1="{y0:.1f}" x2="{mx + w + 2:.1f}" y2="{y0:.1f}" stroke="#3A241A" stroke-width="1.6"/>')
            if j == 0 and k == 1.0:
                cx_, cy_ = mx, y0 + h * 0.5
                out.append(f'<path d="M {cx_ - 9:.1f} {cy_ - 9:.1f} L {cx_ + 9:.1f} {cy_ + 9:.1f} M {cx_ + 9:.1f} {cy_ - 9:.1f} L {cx_ - 9:.1f} {cy_ + 9:.1f}" stroke="{flag}" stroke-width="3.2" stroke-linecap="round"/>')
        out.append(f'<path d="M {mx} {top} l -12 3 l 12 3 Z" fill="{flag}"/>')
    # lateen on the mizzen and spritsail under the bowsprit
    out.append(f'<path d="M 32 -84 L 54 -30 L 30 -36 Z" fill="{sail}" opacity="0.95"/>')
    out.append(f'<path d="M -78 -28 Q -70 -14 -60 -22 L -66 -32 Z" fill="{sail}"/>')
    # rigging
    out.append('<g stroke="#3A241A" stroke-width="0.9" opacity="0.7"><line x1="-86" y1="-30" x2="-30" y2="-96"/><line x1="-30" y1="-96" x2="2" y2="-112"/><line x1="2" y1="-112" x2="32" y2="-84"/><line x1="32" y1="-84" x2="58" y2="-30"/></g>')
    out.append("</g>")
    return "".join(out)


def sabal(x, base, h, seed, frond="#4E7A3E", dark="#2E4E2A", rim="#B8D88A", trunk="#7A6650", lean=0.0, skirt=False):
    """Sabal palmetto (Florida / Carolina state tree): crosshatched boot trunk, dense round crown of fan fronds."""
    rnd = random.Random(seed)
    tx, ty = x + lean * h, base - h
    w = max(2.0, h * 0.045)
    out = [f'<path d="M {x - w:.1f} {base:.1f} Q {x + lean * h * 0.5 - w:.1f} {base - h * 0.5:.1f} {tx - w * 0.9:.1f} {ty + h * 0.05:.1f} L {tx + w * 0.9:.1f} {ty + h * 0.05:.1f} Q {x + lean * h * 0.5 + w:.1f} {base - h * 0.5:.1f} {x + w:.1f} {base:.1f} Z" fill="{trunk}"/>']
    # boot texture (crosshatch of old leaf bases) and a shaded right side
    marks = []
    for i in range(int(h / max(5, w * 1.4))):
        t = i / (h / max(5, w * 1.4))
        yy = base - h * t * 0.95
        xx = x + lean * h * t
        marks.append(f'<path d="M {xx - w * 0.9:.1f} {yy:.1f} l {w * 0.9:.1f} {-w * 0.7:.1f} l {w * 0.9:.1f} {w * 0.7:.1f}"/>')
    out.append(f'<g fill="none" stroke="#3E3226" stroke-width="{max(0.8, w * 0.22):.1f}" opacity="0.45">' + "".join(marks) + "</g>")
    out.append(f'<path d="M {x + w * 0.2:.1f} {base:.1f} Q {x + lean * h * 0.5 + w * 0.2:.1f} {base - h * 0.5:.1f} {tx + w * 0.2:.1f} {ty + h * 0.05:.1f} L {tx + w * 0.9:.1f} {ty + h * 0.05:.1f} Q {x + lean * h * 0.5 + w:.1f} {base - h * 0.5:.1f} {x + w:.1f} {base:.1f} Z" fill="#000" opacity="0.2"/>')
    out.append(f'<path d="M {x - w * 0.75:.1f} {base:.1f} Q {x + lean * h * 0.5 - w * 0.75:.1f} {base - h * 0.5:.1f} {tx - w * 0.65:.1f} {ty + h * 0.05:.1f} L {tx - w * 0.3:.1f} {ty + h * 0.05:.1f} Q {x + lean * h * 0.5 - w * 0.35:.1f} {base - h * 0.5:.1f} {x - w * 0.35:.1f} {base:.1f} Z" fill="#FFF0D0" opacity="0.22"/>')
    R = h * 0.36
    if skirt:
        for i in range(9):
            dx = rnd.uniform(-0.35, 0.35) * R
            L = R * rnd.uniform(0.45, 0.7)
            out.append(f'<path d="M {tx + dx * 0.3:.1f} {ty:.1f} Q {tx + dx:.1f} {ty + L * 0.4:.1f} {tx + dx * 1.1:.1f} {ty + L:.1f} L {tx + dx * 1.1 + L * 0.06:.1f} {ty + L * 0.9:.1f} Q {tx + dx + L * 0.1:.1f} {ty + L * 0.4:.1f} {tx + dx * 0.3 + L * 0.08:.1f} {ty:.1f} Z" fill="{rnd.choice(["#8A7050", "#A08460", "#6E5A40"])}"/>')
    fronds = []
    for i in range(26):
        a = math.radians(rnd.uniform(-200, 20))
        L = R * rnd.uniform(0.55, 1.0)
        px, py = tx + L * 0.45 * math.cos(a), ty + L * 0.45 * math.sin(a) * 0.8
        fronds.append((math.sin(a), a, L, px, py))
    for sa, a, L, px, py in sorted(fronds, key=lambda t: t[0]):
        col = frond if sa < -0.2 else dark if sa > 0.45 else rnd.choice([frond, dark])
        droop = 0.35 * L * max(0, math.cos(a) ** 2)
        tips = []
        for j in range(15):
            b = a + math.radians(-42 + j * 6)
            rr = L * (0.62 if j % 2 else 1.0) * rnd.uniform(0.88, 1.05)
            tips.append((px + rr * 0.55 * math.cos(b), py + rr * 0.55 * math.sin(b) * 0.85 + droop * (0.6 + 0.4 * j / 14)))
        out.append(f'<line x1="{tx:.1f}" y1="{ty:.1f}" x2="{px:.1f}" y2="{py:.1f}" stroke="{dark}" stroke-width="{max(0.8, h * 0.008):.1f}"/>')
        out.append(poly([(px, py)] + tips, col))
        if sa < 0.1:
            out.append(poly([(px, py)] + tips[:8], rim, ' opacity="0.28"'))
            out.append(f'<polyline points="{P(tips[6:])}" fill="none" stroke="{rim}" stroke-width="{max(0.7, h * 0.006):.1f}" opacity="0.7"/>')
    return "".join(out)


def st_augustine():
    u = "sa"
    C = Cam(f=380, cx=300, vpy=250, eye=2.0)
    V = C
    out = [defs(
        lg(f"{u}-sky", [(0, "#2C74B6"), (0.45, "#6CA8D6"), (0.8, "#B6DAEA"), (1, "#E2F0EC")]),
        lg(f"{u}-cl", [(0, "#FFFFFF"), (0.6, "#F2F4F6"), (1, "#B4C0D6")], 0, 0, 0, 1),
        lg(f"{u}-bay", [(0, "#74B8BE"), (0.12, "#4AA0AA"), (0.6, "#2A8090"), (1, "#1C5E70")], 0, 248, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-lit", [(0, "#EDE3CA"), (1, "#CFC0A0")], 0, 0, 1, 0),
        lg(f"{u}-shd", [(0, "#9E9584"), (1, "#7A7062")], 0, 0, 1, 0),
        lg(f"{u}-lawn", [(0, "#9AB862"), (0.4, "#78A04A"), (1, "#4E7E36")], 0, 250, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-gar", [(0, "#F6EEDA"), (0.45, "#DCCEAE"), (1, "#8A8070")], 0, 0, 1, 0),
        lg(f"{u}-haze", [(0, "#E2F0EC", 0), (1, "#E2F0EC", 0.85)]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(30, 30, 280, "#FFF8E0", f"{u}-sun", 0.8))
    # towering Florida cumulus over the bay
    out.append(cumulus(150, 190, 300, 120, 3, f"{u}-cl"))
    out.append(cumulus(500, 130, 200, 60, 7, f"{u}-cl", hi_op=0.6))
    out.append(cumulus(330, 226, 220, 26, 11, f"{u}-cl", hi_op=0.5))
    out.append(f'<rect x="0" y="200" width="600" height="52" fill="url(#{u}-haze)"/>')
    # Anastasia Island across the bay, with the spiral-striped lighthouse
    pl, isl = ridge_poly([(-10, 248), (60, 245), (140, 246), (230, 244), (330, 247), (610, 246)], 5, base=252, amp=2, fill="#78A08E")
    out.append(pl)
    out.append(tree_line(isl, 6, ["#6A9282", "#73988A", "#5E8A78"], density=1.8, hmin=4, hmax=8, xmax=330))
    lx, lb, lh = 206, 247, 58
    body = [(lx - 5.5, lb), (lx - 3.6, lb - lh), (lx + 3.6, lb - lh), (lx + 5.5, lb)]
    out.append(poly(body, "#F6F2EA"))
    cid = f"{u}-lhc"
    out.append(f'<clipPath id="{cid}"><polygon points="{P(body)}"/></clipPath>')
    out.append(f'<g clip-path="url(#{cid})" fill="#1E1E24">' + "".join(
        poly([(lx - 8, lb - lh + i * 14 + 9), (lx + 8, lb - lh + i * 14), (lx + 8, lb - lh + i * 14 + 6.5), (lx - 8, lb - lh + i * 14 + 15.5)], "#1E1E24") for i in range(5)) + "</g>")
    out.append(poly([(lx + 1, lb), (lx + 1.6, lb - lh), (lx + 3.6, lb - lh), (lx + 5.5, lb)], "#000", ' opacity="0.16"'))
    out.append(f'<rect x="{lx - 5.5}" y="{lb - lh - 3}" width="11" height="3" fill="#2A2A2A"/><rect x="{lx - 3.2}" y="{lb - lh - 11}" width="6.4" height="8" fill="#C23A2E"/>'
               f'<rect x="{lx - 2}" y="{lb - lh - 10}" width="4" height="4.5" fill="#FFE9A8"/><path d="M {lx - 3.8} {lb - lh - 11} Q {lx} {lb - lh - 17} {lx + 3.8} {lb - lh - 11} Z" fill="#C23A2E"/>')
    out.append(f'<rect x="{lx - 13}" y="{lb - 6}" width="10" height="6" fill="#ECE2CC"/><polygon points="{P([(lx - 14, lb - 6), (lx - 8, lb - 10.5), (lx - 2, lb - 6)])}" fill="#B8503E"/>')
    # Matanzas Bay with sun glitter
    out.append(f'<rect x="0" y="248" width="600" height="196" fill="url(#{u}-bay)"/>')
    out.append(f'<g transform="translate(0 {292 * 1.6:.1f}) scale(1 -0.6)" opacity="0.16">{galleon(108, 292, 0.95)}</g>')
    rnd = random.Random(4)
    out.append('<g fill="#EAF8F4">' + "".join(
        f'<rect x="{rnd.uniform(-10, 330):.1f}" y="{(yy := 250 + 190 * rnd.random() ** 1.5):.1f}" width="{rnd.uniform(6, 24) * (0.4 + (yy - 248) / 50):.1f}" height="{0.8 + (yy - 248) / 60:.1f}" rx="1" opacity="{rnd.uniform(0.2, 0.6):.2f}"/>' for _ in range(150)) + "</g>")
    out.append(gulls([(258, 160, 10), (278, 172, 7), (60, 118, 9)], "#2E4A5E"))
    # a small sloop far out, and the galleon on the bay with its reflection
    out.append('<path d="M 30 250 l 16 0 l -3 3 l -11 0 Z" fill="#3A3A40"/><path d="M 38 249 L 38 228 L 47 248 Z" fill="#FBF6EA"/><path d="M 37 249 L 37 232 L 30 248 Z" fill="#E8E0D0"/>')
    gx, gy, gs = 108, 292, 0.95
    out.append(galleon(gx, gy, gs))
    out.append(f'<path d="M {gx + 56} {gy + 1} q 40 6 100 3 M {gx - 52} {gy + 2} q -20 3 -40 1" stroke="#F2FAF6" stroke-width="2" fill="none" opacity="0.8"/>')
    out.append(f'<path d="M {gx - 48} {gy + 3} q 50 6 104 -1" stroke="#0E3A48" stroke-width="2.4" fill="none" opacity="0.35"/>')
    # --- the fort: a bastion pointing at us (sunlit east face on the left, shaded face on the right)
    pt = (8.0, 30.0)
    d1, L1 = (-0.6, 0.8), 28
    d2, L2 = (0.93, 0.37), 70
    e1 = (pt[0] + d1[0] * L1, pt[1] + d1[1] * L1)
    e2 = (pt[0] + d2[0] * L2, pt[1] + d2[1] * L2)
    H, bat = 10.0, 1.1
    n1, n2 = (-0.8, -0.6), (0.37, -0.93)
    dot = n1[0] * n2[0] + n1[1] * n2[1]
    tpt = (pt[0] - (n1[0] + n2[0]) / (1 + dot) * bat, pt[1] - (n1[1] + n2[1]) / (1 + dot) * bat)
    te1 = (e1[0] - n1[0] * bat, e1[1] - n1[1] * bat)
    te2 = (e2[0] - n2[0] * bat, e2[1] - n2[1] * bat)
    fl_end = (e1[0] + 4, e1[1] + 10)
    # far curtain + next bastion beyond the flank, slightly hazed
    out.append(poly([V(fl_end[0], 0, fl_end[1]), V(fl_end[0], H, fl_end[1]), V(fl_end[0] - 1, H, fl_end[1] + 30), V(fl_end[0] - 1, 0, fl_end[1] + 30)], "#C4B89E"))
    out.append(poly([V(e1[0], 0, e1[1]), V(te1[0], H, te1[1]), V(fl_end[0], H, fl_end[1]), V(fl_end[0], 0, fl_end[1])], "#A0947E"))
    face1 = [V(pt[0], 0, pt[1]), V(e1[0], 0, e1[1]), V(te1[0], H, te1[1]), V(tpt[0], H, tpt[1])]
    face2 = [V(pt[0], 0, pt[1]), V(tpt[0], H, tpt[1]), V(te2[0], H, te2[1]), V(e2[0], 0, e2[1])]
    for k, (face, grad, a, b) in enumerate(((face1, f"{u}-lit", pt, e1), (face2, f"{u}-shd", pt, e2))):
        cid = f"{u}-f{k}"
        out.append(f'<clipPath id="{cid}"><polygon points="{P(face)}"/></clipPath>')
        out.append(poly(face, f"url(#{grad})"))
        xs = [p[0] for p in face]
        ys = [p[1] for p in face]
        box = (min(xs), min(ys), max(xs), max(ys))
        g = []
        rb = random.Random(30 + k)
        Ltot = math.hypot(b[0] - a[0], b[1] - a[1])
        for row in range(14):
            y0 = row * 0.72
            s = -rb.uniform(0, 1.4)
            while s < Ltot:
                bl = rb.uniform(1.0, 2.2)
                t0, t1 = max(0, s) / Ltot, min(Ltot, s + bl) / Ltot
                ax, az = a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0
                bx, bz = a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1
                shade = rb.choice(["#FFF6E0", "#B8AA8C", "#E2D4B4", "#9A8E78", "#F0E4C8"]) if k == 0 else rb.choice(["#A89E8A", "#6E6658", "#8E8472", "#B0A690"])
                g.append(poly([V(ax, y0 + 0.06, az), V(ax, y0 + 0.66, az), V(bx, y0 + 0.66, bz), V(bx, y0 + 0.06, bz)], shade, f' opacity="{rb.uniform(0.18, 0.42):.2f}"'))
                s += bl
            p0, p1 = V(a[0], y0, a[1]), V(b[0], y0, b[1])
            g.append(f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" stroke="#6E6252" stroke-width="0.9" opacity="0.35"/>')
        g.append(dots(int((box[2] - box[0]) * (box[3] - box[1]) / 16), 40 + k, box, "#5E5446", r=(0.5, 1.6), opacity=(0.25, 0.7)))
        g.append(dots(int((box[2] - box[0]) * (box[3] - box[1]) / 36), 50 + k, box, "#FFF8E8", r=(0.4, 1.2), opacity=(0.3, 0.7)))
        g.append(streaks(int((box[2] - box[0]) / 4), 60 + k, (box[0], box[1] - 6, box[2], box[1] + 50), ["#5A5448", "#7A7262", "#4A463E"], w=(1, 4), length=(16, 70), opacity=(0.12, 0.35), slant=0.05))
        g.append(blobs(22, 70 + k, (box[0], box[3] - 34, box[2], box[3]), ["#5E6A4A", "#4A5640", "#6E6A52"], r=(6, 20), opacity=(0.15, 0.35), squash=0.4))
        if k == 0:   # warm bounce light at the salient edge
            g.append(f'<polygon points="{P([face[0], face[3], V(tpt[0] - 3, H, tpt[1] + 4), V(pt[0] - 3, 0, pt[1] + 4)])}" fill="#FFF4D8" opacity="0.18"/>')
        out.append(f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>")
    out.append(f'<polyline points="{P([face1[0], face1[3]])}" fill="none" stroke="#FFF6DE" stroke-width="2" opacity="0.8"/>')

    def parapet(a, b, body_c, cap_c, n_emb):
        res = []
        Ltot = math.hypot(b[0] - a[0], b[1] - a[1])
        ux, uz = (b[0] - a[0]) / Ltot, (b[1] - a[1]) / Ltot
        emb = [Ltot * (i + 0.6) / n_emb for i in range(n_emb)]
        segs, s = [], 0
        for e in emb:
            segs.append((s, e - 0.8))
            s = e + 0.8
        segs.append((s, Ltot))
        # rear parapet / gun deck seen through the embrasures
        res.append(poly([V(a[0], H, a[1]), V(a[0], H + 1.45, a[1]), V(b[0], H + 1.45, b[1]), V(b[0], H, b[1])], "#6E6454"))
        for s0, s1 in segs:
            ax, az, bx, bz = a[0] + ux * s0, a[1] + uz * s0, a[0] + ux * s1, a[1] + uz * s1
            res.append(poly([V(ax, H - 0.1, az), V(ax, H + 1.5, az), V(bx, H + 1.5, bz), V(bx, H - 0.1, bz)], body_c))
            res.append(poly([V(ax, H + 1.3, az), V(ax, H + 1.62, az), V(bx, H + 1.62, bz), V(bx, H + 1.3, bz)], cap_c))
        for e in emb:   # dark mouth of each embrasure
            ex, ez = a[0] + ux * e, a[1] + uz * e
            res.append(poly([V(ex - ux * 0.8, H + 1.5, ez - uz * 0.8), V(ex - ux * 0.45, H + 0.2, ez - uz * 0.45), V(ex + ux * 0.45, H + 0.2, ez + uz * 0.45), V(ex + ux * 0.8, H + 1.5, ez + uz * 0.8)], "#4A4238", ' opacity="0.55"'))
        return "".join(res)
    out.append(parapet(tpt, te1, "#E0D3B4", "#FBF4E2", 3))
    out.append(parapet(tpt, te2, "#968A76", "#B6AC98", 5))
    # the Cross of Burgundy flag over the gun deck, visitors along the rampart
    fx, fby = V(pt[0] - 10, H + 1.6, pt[1] + 26)
    _, fty = V(pt[0] - 10, H + 12, pt[1] + 26)
    out.append(f'<line x1="{fx:.1f}" y1="{fby:.1f}" x2="{fx:.1f}" y2="{fty:.1f}" stroke="#4A4440" stroke-width="2.2"/><circle cx="{fx:.1f}" cy="{fty - 1:.1f}" r="2.2" fill="#D8A94A"/>')
    fw, fh_ = 40, 26
    out.append(f'<path d="M {fx:.1f} {fty + 1:.1f} q {fw * 0.5:.1f} -5 {fw:.1f} 1 l 0 {fh_:.1f} q {-fw * 0.5:.1f} -6 {-fw:.1f} -1 Z" fill="#FBF6EA"/>')
    out.append(f'<g stroke="#C2322A" stroke-width="3.6" stroke-linecap="round" fill="none"><path d="M {fx + 5:.1f} {fty + 4:.1f} q 8 7 {fw - 10:.1f} {fh_ - 4:.1f}"/><path d="M {fx + fw - 5:.1f} {fty + 3:.1f} q -9 9 {-fw + 10:.1f} {fh_ - 2:.1f}"/></g>')
    out.append(f'<path d="M {fx + fw * 0.55:.1f} {fty - 0.5:.1f} q {fw * 0.2:.1f} 1 {fw * 0.45:.1f} 2.5 l 0 {fh_:.1f} q {-fw * 0.2:.1f} -2 {-fw * 0.45:.1f} -3 Z" fill="#6E6458" opacity="0.18"/>')
    for k_, (X, Z, c) in enumerate(((pt[0] - 13, pt[1] + 20, "#3E6A9A"), (pt[0] - 12, pt[1] + 20.5, "#D8574A"), (pt[0] + 9, pt[1] + 18, "#E0B040"), (pt[0] + 10, pt[1] + 18.3, "#5A7A5A"))):
        x, b = V(X, H + 1.6, Z)
        out.append(figure(x, b + 1, 380 * 1.7 / Z, c, pose=("stand_34", "point", "stand", "photo")[k_], facing=(1, -1, 1, -1)[k_], seed=100 + k_, pal={"season": "summer"}))
    # the garita (sentry box) cantilevered from the salient, sunlit from the left
    gx_, gyb = V(tpt[0] - 0.1, H - 1.2, tpt[1] - 0.5)
    _, gyt = V(tpt[0] - 0.1, H + 2.7, tpt[1] - 0.5)
    r = 380 * 1.1 / (tpt[1] - 0.5)
    out.append(f'<path d="M {gx_ - r:.1f} {gyb + r * 0.7:.1f} Q {gx_:.1f} {gyb + r * 2.8:.1f} {gx_ + r:.1f} {gyb + r * 0.7:.1f} Z" fill="url(#{u}-gar)"/>')
    out.append(f'<path d="M {gx_ - r:.1f} {gyb + r * 0.6:.1f} L {gx_ - r:.1f} {gyt:.1f} A {r:.1f} {r * 0.3:.1f} 0 0 1 {gx_ + r:.1f} {gyt:.1f} L {gx_ + r:.1f} {gyb + r * 0.6:.1f} A {r:.1f} {r * 0.3:.1f} 0 0 1 {gx_ - r:.1f} {gyb + r * 0.6:.1f} Z" fill="url(#{u}-gar)"/>')
    out.append(f'<rect x="{gx_ - r * 1.1:.1f}" y="{gyb + r * 0.4:.1f}" width="{r * 2.2:.1f}" height="{r * 0.35:.1f}" rx="2" fill="#EFE5CC"/><rect x="{gx_ + r * 0.3:.1f}" y="{gyb + r * 0.4:.1f}" width="{r * 0.8:.1f}" height="{r * 0.35:.1f}" fill="#8A8070" opacity="0.5"/>')
    out.append(f'<rect x="{gx_ - r * 0.5:.1f}" y="{gyt + r * 0.6:.1f}" width="{r * 0.3:.1f}" height="{r * 1.2:.1f}" rx="{r * 0.15:.1f}" fill="#2A2420"/>')
    out.append(dots(30, 5, (gx_ - r, gyt, gx_ + r, gyb + r * 0.5), "#6E6252", r=(0.4, 1.1), opacity=(0.3, 0.6)))
    out.append(f'<rect x="{gx_ - r * 1.12:.1f}" y="{gyt - r * 0.2:.1f}" width="{r * 2.24:.1f}" height="{r * 0.32:.1f}" rx="2" fill="#F4ECD8"/>')
    out.append(f'<path d="M {gx_ - r:.1f} {gyt - r * 0.12:.1f} Q {gx_ - r:.1f} {gyt - r * 1.3:.1f} {gx_:.1f} {gyt - r * 1.35:.1f} Q {gx_ + r:.1f} {gyt - r * 1.3:.1f} {gx_ + r:.1f} {gyt - r * 0.12:.1f} Z" fill="url(#{u}-gar)"/>')
    out.append(f'<circle cx="{gx_:.1f}" cy="{gyt - r * 1.5:.1f}" r="{r * 0.22:.1f}" fill="#E2D6BA"/>')
    # lawn of the moat and grounds
    base_line = [V(fl_end[0], 0, fl_end[1] + 30), V(fl_end[0], 0, fl_end[1]), V(e1[0], 0, e1[1]), V(pt[0], 0, pt[1]), V(e2[0], 0, e2[1])]
    sea = [(250, 262), (236, 300), (212, 350), (190, 400), (176, 444)]
    out.append(poly([base_line[0]] + base_line[1:] + [(640, 266), (640, 444)] + sea[::-1], f"url(#{u}-lawn)"))
    out.append(poly([V(pt[0], 0, pt[1]), V(e2[0], 0, e2[1]), (640, 272), V(pt[0] + 1.5, 0, pt[1] - 4)], "#3E5A2E", ' opacity="0.3"'))
    out.append(poly([V(pt[0], 0, pt[1]), V(e1[0], 0, e1[1]), V(e1[0] + 1, 0, e1[1] - 5), V(pt[0] - 1, 0, pt[1] - 4)], "#FFF4C8", ' opacity="0.12"'))
    out.append(grass(220, 81, (240, 272, 600, 340), ["#A8C870", "#7AA24E", "#C4D888"], h=(3, 8), sw=1.3))
    # seawall promenade sweeping in from the foreground
    wall_top = [(252, 262), (240, 298), (219, 348), (199, 398), (186, 444)]
    wall_out = [(248, 263), (231, 300), (205, 351), (180, 402), (162, 444)]
    out.append(poly(wall_top + wall_out[::-1], "#B5A68A"))
    out.append(dots(90, 7, (160, 262, 252, 444), "#6E6252", r=(0.5, 1.4), opacity=(0.3, 0.7)))
    out.append(f'<polyline points="{P(wall_out)}" fill="none" stroke="#5A5040" stroke-width="2" opacity="0.6"/>')
    walk = [(252, 262), (240, 298), (219, 348), (199, 398), (186, 444), (300, 444), (290, 400), (276, 350), (264, 300), (256, 263)]
    out.append(poly(walk, "#E6D6B0"))
    out.append(poly([(256, 263), (264, 300), (276, 350), (290, 400), (300, 444), (310, 444), (298, 400), (282, 350), (268, 300), (258, 263)], "#A88E66", ' opacity="0.6"'))
    cap = [(250, 260), (237, 297), (215, 346), (194, 396), (180, 444), (192, 444), (205, 398), (224, 349), (243, 299), (254, 261)]
    out.append(poly(cap, "#F4EBD4"))
    out.append(f'<polyline points="{P([(254, 261), (243, 299), (224, 349), (205, 398), (192, 444)])}" fill="none" stroke="#9A8C72" stroke-width="2"/>')
    out.append(grass(240, 92, (300, 330, 610, 444), ["#A8C870", "#7AA24E", "#C8D888", "#5E8A3E"], h=(6, 16)))
    # strollers on the promenade
    for x, b, h, c, sk, hat in ((262, 318, 22, "#2E5E8A", False, None), (271, 316, 20, "#E06A5A", True, "#F2E2B4"), (252, 356, 30, "#F2F0E8", False, "#E8D8A8"), (244, 410, 44, "#C8574A", True, None)):
        out.append(f'<ellipse cx="{x + 5}" cy="{b + 1}" rx="{h * 0.3:.1f}" ry="{h * 0.06:.1f}" fill="#7A6A4A" opacity="0.35"/>')
        out.append(figure(x, b, h, c, skirt=sk, hat=hat, rim="#FFF4D8", pose="walk", facing=-1 if b < 340 else 1, pal={"season": "summer"}))
    # cannonball pyramid on the lawn
    for bx, by in ((420, 384), (433, 384), (446, 384), (459, 384), (426, 373), (439, 373), (452, 373), (432, 362), (445, 362), (438, 351)):
        out.append(f'<circle cx="{bx}" cy="{by}" r="7" fill="#2A2624"/><circle cx="{bx - 2.4}" cy="{by - 2.4}" r="2.3" fill="#8A8278"/>')
    out.append('<ellipse cx="444" cy="392" rx="34" ry="4" fill="#2E4A24" opacity="0.4"/>')
    out.append(grass(50, 95, (408, 384, 476, 394), ["#A8C870", "#7AA24E", "#C8D888"], h=(4, 9)))
    # pelican on a piling in the water, sabal palms framing the right
    out.append('<rect x="120" y="360" width="10" height="84" fill="#6A5640"/><rect x="120" y="360" width="4" height="84" fill="#8A7458"/><ellipse cx="125" cy="360" rx="5" ry="2" fill="#9A8466"/>')
    out.append('<g transform="translate(125 360)"><path d="M -10 -2 Q -14 -20 -2 -26 Q 6 -28 8 -20 L 8 -2 Z" fill="#7A6A5E"/><path d="M -6 -6 Q -10 -18 -2 -22 L 2 -8 Z" fill="#5E5048"/>'
               '<path d="M 0 -20 Q 0 -32 6 -34 Q 12 -34 11 -28 Q 8 -26 7 -18 Z" fill="#EDE4D2"/><path d="M 6 -34 Q 10 -37 13 -33 Q 10 -31 6 -32 Z" fill="#F6EFD8"/>'
               '<path d="M 12 -34 Q 20 -24 18 -6 Q 15 -10 12 -26 Z" fill="#9A7A5A"/><path d="M 12 -34 Q 21 -25 19 -7" fill="none" stroke="#D8A85A" stroke-width="1.6"/><circle cx="9.5" cy="-33" r="0.9" fill="#1E1A18"/></g>')
    out.append(sabal(560, 446, 250, 17))
    out.append(sabal(500, 446, 170, 23, frond="#5A864A", dark="#3A5E34"))
    return "\n".join(out)


# ---------------------------------------------------------------- New Orleans (a French Quarter street at dusk)
def musician(x, base, h, coat="#2E2A3A", rim="#FFC870", brass="#E8B64A"):
    """Street trumpeter facing left, horn raised; (x, base) = feet."""
    return F.person(x, base, h, "trumpet", -1, {"top": coat, "top_kind": "jacket", "bottom": "#16141C", "hat_kind": "cap", "hat": "#1A1820", "skin": "#6A4028",
                                                "hair_style": "short", "form": "m", "brass": brass, "shoes": "#0E0C10", "inner": "#E8DCC8"},
                    seed=7, rim=rim, light=1, tint=("#2A2040", 0.15))


def lace_railing(C, X, z0, z1, y0, y1, color, seed):
    """Cast-iron lace railing in the plane X = const: rails, balusters and scroll circles."""
    out = []
    zm = (z0 + z1) / 2
    sw = max(0.6, C.f * 0.05 / zm)
    a, b = C(X, y1, z0), C(X, y1, z1)
    c, d = C(X, y0, z0), C(X, y0, z1)
    out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{color}" stroke-width="{sw * 1.8:.1f}"/>')
    out.append(f'<line x1="{c[0]:.1f}" y1="{c[1]:.1f}" x2="{d[0]:.1f}" y2="{d[1]:.1f}" stroke="{color}" stroke-width="{sw * 1.4:.1f}"/>')
    step = 0.32 if zm < 30 else 0.6 if zm < 70 else 1.2
    z = z0
    bal = []
    circ = []
    i = 0
    while z < z1:
        p, q = C(X, y0, z), C(X, y1, z)
        bal.append(f'M {p[0]:.1f} {p[1]:.1f} L {q[0]:.1f} {q[1]:.1f}')
        if zm < 70 and i % 2 == 0 and z + step < z1:
            cz = z + step
            cx_, cy_ = C(X, (y0 + y1) / 2, cz)
            ry = C.f * (y1 - y0) * 0.28 / cz
            rx = ry * abs(X) / cz
            circ.append(f'<ellipse cx="{cx_:.1f}" cy="{cy_:.1f}" rx="{max(0.4, rx):.1f}" ry="{ry:.1f}"/>')
        z += step
        i += 1
    out.append(f'<path d="{" ".join(bal)}" stroke="{color}" stroke-width="{sw:.1f}" fill="none"/>')
    out.append(f'<g fill="none" stroke="{color}" stroke-width="{sw:.1f}">' + "".join(circ) + "</g>")
    return "".join(out)


def fern(cx, cy, r, seed, cols=("#4E8A3E", "#6EA84A", "#3A6A30", "#8CC060")):
    """Boston fern in a pot on the railing, fronds arching up and draping down over the iron."""
    rnd = random.Random(seed)
    out = []
    for _ in range(16):
        side = rnd.choice((-1, 1))
        L = r * rnd.uniform(1.0, 2.1)
        ex = cx + side * L * rnd.uniform(0.3, 0.8)
        ey = cy + L * rnd.uniform(0.2, 1.1)
        out.append(f'<path d="M {cx:.1f} {cy - r * 0.4:.1f} Q {cx + side * L * 0.7:.1f} {cy - r * 0.9:.1f} {ex:.1f} {ey:.1f}" stroke="{rnd.choice(cols)}" stroke-width="{max(0.8, r * 0.3):.1f}" fill="none" stroke-linecap="round"/>')
    out.append(f'<ellipse cx="{cx:.1f}" cy="{cy - r * 0.35:.1f}" rx="{r * 0.9:.1f}" ry="{r * 0.55:.1f}" fill="{cols[0]}"/>')
    out.append(f'<ellipse cx="{cx - r * 0.25:.1f}" cy="{cy - r * 0.55:.1f}" rx="{r * 0.5:.1f}" ry="{r * 0.28:.1f}" fill="{cols[3]}" opacity="0.8"/>')
    out.append(f'<path d="M {cx - r * 0.45:.1f} {cy - r * 0.1:.1f} L {cx + r * 0.45:.1f} {cy - r * 0.1:.1f} L {cx + r * 0.35:.1f} {cy + r * 0.5:.1f} L {cx - r * 0.35:.1f} {cy + r * 0.5:.1f} Z" fill="#A85A3A"/>')
    return "".join(out)


def new_orleans():
    u = "no"
    C = Cam(f=420, cx=300, vpy=300, eye=1.6)
    W, XO = 6.0, 3.9          # facade line, gallery / curb line
    out = [defs(
        lg(f"{u}-sky", [(0, "#18264E"), (0.35, "#34407A"), (0.62, "#7A5A96"), (0.85, "#D27A8A"), (1, "#F4AE84")]),
        lg(f"{u}-street", [(0, "#6A4A5A"), (0.4, "#4A3448"), (1, "#20182A")], 0, 300, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-walk", [(0, "#8A6A6A"), (1, "#3A2A34")], 0, 300, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-dark", [(0, "#140E24", 0.75), (0.45, "#140E24", 0.35), (1, "#140E24", 0.05)], 0, 0, 0, 330, units="userSpaceOnUse"),
        lg(f"{u}-cath", [(0, "#FFF6E6"), (1, "#E8D6C8")], 0, 0, 1, 0),
        lg(f"{u}-win", [(0, "#FFE4A0"), (1, "#F2A050")]),
        rg(f"{u}-pool", [(0, "#FFC870", 0.35), (1, "#FFC870", 0)]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(26, 3, (140, 40, 460, 140), "#FFF4E0", r=(0.6, 1.3), opacity=(0.4, 0.9)))
    out.append('<circle cx="372" cy="118" r="2.2" fill="#FFF8E8"/>')
    out.append(glow(300, 290, 230, "#FFB880", f"{u}-dusk", 0.5))
    # St. Louis Cathedral closing the street: three spires, floodlit white
    Zc = 118
    def cq(X0, X1, Y0, Y1, fill, extra=""):
        return poly(C.quad_z(Zc, X0, X1, Y0, Y1), fill, extra)
    cat = []
    cat.append(cq(-17, 17, 0, 16, f"url(#{u}-cath)"))
    for X0, X1 in ((-17, -10), (10, 17)):           # side towers
        cat.append(cq(X0, X1, 16, 24, f"url(#{u}-cath)"))
        x0, yb = C(X0, 24, Zc)
        x1, _ = C(X1, 24, Zc)
        _, yt = C(0, 37, Zc)
        cat.append(f'<polygon points="{P([(x0 + 1, yb), ((x0 + x1) / 2, yt), (x1 - 1, yb)])}" fill="#3A3448"/>')
        cat.append(f'<polygon points="{P([(x0 + 1, yb), ((x0 + x1) / 2, yt), ((x0 + x1) / 2, yb)])}" fill="#56506A"/>')
        cat.append(cq(X0 + 1.5, X1 - 1.5, 18, 22, "#3A3448", ' opacity="0.55"'))
    # central tower: belfry with clock, then the tall spire
    cat.append(cq(-4.5, 4.5, 16, 30, f"url(#{u}-cath)"))
    cat.append(cq(-3.2, 3.2, 30, 34, "#F2E4D6"))
    cx_, cy_ = C(0, 24.5, Zc)
    cat.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{C.f * 2.2 / Zc:.1f}" fill="#2A2638"/><circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{C.f * 1.8 / Zc:.1f}" fill="#FFF2D2"/>')
    cat.append(f'<path d="M {cx_:.1f} {cy_:.1f} l 0 -4 M {cx_:.1f} {cy_:.1f} l 3 1" stroke="#2A2638" stroke-width="1.2"/>')
    x0, yb = C(-3.2, 34, Zc)
    x1, _ = C(3.2, 34, Zc)
    _, yt = C(0, 52, Zc)
    cat.append(f'<polygon points="{P([(x0, yb), (300, yt), (x1, yb)])}" fill="#3A3448"/><polygon points="{P([(x0, yb), (300, yt), (300, yb)])}" fill="#58526C"/>')
    cat.append(f'<line x1="300" y1="{yt:.1f}" x2="300" y2="{yt - 9:.1f}" stroke="#3A3448" stroke-width="1.6"/><line x1="296" y1="{yt - 6:.1f}" x2="304" y2="{yt - 6:.1f}" stroke="#3A3448" stroke-width="1.6"/>')
    # arched openings, columns and the belfry louvres, softened by evening haze
    for X, Y0, Y1 in ((-14, 3, 10), (-6, 3, 11), (6, 3, 11), (14, 3, 10), (-13.5, 17, 22), (13.5, 17, 22), (0, 19, 23), (-2, 31, 33), (2, 31, 33)):
        a_, b_ = C(X - 1.2, Y0, Zc), C(X + 1.2, Y1, Zc)
        cat.append(f'<rect x="{a_[0]:.1f}" y="{b_[1]:.1f}" width="{b_[0] - a_[0]:.1f}" height="{a_[1] - b_[1]:.1f}" rx="{(b_[0] - a_[0]) / 2:.1f}" fill="#8A7A8E" opacity="0.7"/>')
    for X in (-8.5, 8.5, -2.6, 2.6):
        a_, b_ = C(X - 0.4, 1, Zc), C(X + 0.4, 15, Zc)
        cat.append(f'<rect x="{a_[0]:.1f}" y="{b_[1]:.1f}" width="{b_[0] - a_[0]:.1f}" height="{a_[1] - b_[1]:.1f}" fill="#FFFFFF" opacity="0.7"/>')
    cat.append(cq(-17, 17, 15.4, 16, "#FFFFFF", ' opacity="0.8"'))
    out.append(glow(300, C(0, 18, Zc)[1], 120, "#FFE8C8", f"{u}-cg", 0.5))
    out.append("".join(cat))
    out.append(poly(C.quad_z(Zc, -17, 17, 0, 52), "#7A5A96", ' opacity="0.16"'))
    # garden trees in front of the cathedral
    for X in (-6, 6):   # warm doorways
        a_, b_ = C(X - 1, 0, Zc), C(X + 1, 4, Zc)
        out.append(f'<rect x="{a_[0]:.1f}" y="{b_[1]:.1f}" width="{b_[0] - a_[0]:.1f}" height="{a_[1] - b_[1]:.1f}" rx="{(b_[0] - a_[0]) / 2:.1f}" fill="#F4B868"/>')
    a_, b_ = C(-1.5, 0, Zc), C(1.5, 5.5, Zc)
    out.append(f'<rect x="{a_[0]:.1f}" y="{b_[1]:.1f}" width="{b_[0] - a_[0]:.1f}" height="{a_[1] - b_[1]:.1f}" rx="{(b_[0] - a_[0]) / 2:.1f}" fill="#FFCE80"/>')
    fl, fr = C(-17, 1.4, Zc - 8), C(17, 1.4, Zc - 8)
    fb = C(0, 0, Zc - 8)[1]
    out.append(f'<rect x="{fl[0]:.1f}" y="{fl[1]:.1f}" width="{fr[0] - fl[0]:.1f}" height="{fb - fl[1]:.1f}" fill="none" stroke="#2A2234" stroke-width="0.8" stroke-dasharray="0.8 1.6"/>')
    out.append(f'<line x1="{fl[0]:.1f}" y1="{fl[1]:.1f}" x2="{fr[0]:.1f}" y2="{fr[1]:.1f}" stroke="#2A2234" stroke-width="1"/>')
    # street, banquettes and curbs
    Z0, Z1 = 2.5, Zc - 4
    out.append(poly([C(-XO, 0, Z1), C(XO, 0, Z1), C(XO, 0, Z0), C(-XO, 0, Z0)], f"url(#{u}-street)"))
    for sgn in (-1, 1):
        out.append(poly([C(sgn * XO, 0.15, Z1), C(sgn * W, 0.15, Z1), C(sgn * W, 0.15, Z0), C(sgn * XO, 0.15, Z0)], f"url(#{u}-walk)"))
        out.append(poly([C(sgn * XO, 0.15, Z1), C(sgn * XO, 0.15, Z0), C(sgn * XO, 0, Z0), C(sgn * XO, 0, Z1)], "#B89A8A"))
        # flagstone joints on the banquette
        for z in (3.5, 4.6, 5.9, 7.4, 9.2, 11.4, 14, 17.5, 22, 28, 36):
            a_, b_ = C(sgn * XO, 0.15, z), C(sgn * W, 0.15, z)
            out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#2A1E28" stroke-width="{max(0.5, 12 / z):.1f}" opacity="0.4"/>')
    # buildings: (Z0, Z1, height, colour, shutter colour, stories)
    left = [(2, 12, 12.5, "#E39A72", "#2E5A44", 3), (12, 21, 10, "#C8707A", "#2E4A5E", 2), (21, 31, 12, "#E6B860", "#3E6A4E", 3),
            (31, 40, 9.5, "#9A80B4", "#2E5A44", 2), (44, 56, 9, "#E8A27E", "#2E4A5E", 2), (56, 70, 9.5, "#6AA4A0", "#4A3A2A", 2), (70, 112, 8.5, "#D88A7A", "#2E5A44", 2)]
    right = [(2, 10, 11, "#5E9C9A", "#3A2A24", 2), (10, 22, 13, "#E2C070", "#2E5A44", 3), (22, 30, 10, "#E08A86", "#2E4A5E", 2),
             (30, 40, 9.5, "#88A0C8", "#2E3A4E", 2), (44, 54, 9, "#E8B48A", "#2E5A44", 2), (54, 72, 9.5, "#B88AB0", "#2E4A44", 2), (72, 112, 8.5, "#E2A060", "#2E5A44", 2)]
    lit = ["#FFD98E", "#F7C873", "#FFE2A8", "#F4B060"]
    galleries = []
    for sgn, blds in ((-1, left), (1, right)):
        X = sgn * W
        # cross street (gap between Z 40 and 44): far corner wall in shadow
        for k, (z0, z1, h, col, shut, st) in enumerate(sorted(blds, key=lambda t: -t[0])):
            rb = random.Random(k * 7 + sgn)
            out.append(poly(C.quad_x(X, z0, z1, 0, h), col))
            if z0 in (44,):
                out.append(poly([C(X, 0, z0), C(X, h, z0), C(X + sgn * 6, h, z0), C(X + sgn * 6, 0, z0)], col, ' opacity="1"'))
                out.append(poly([C(X, 0, z0), C(X, h, z0), C(X + sgn * 6, h, z0), C(X + sgn * 6, 0, z0)], "#140E24", ' opacity="0.45"'))
            # stucco texture
            out.append(f'<g opacity="0.08" stroke="#FFFFFF" stroke-width="{max(0.5, 30 / z1):.1f}">' + "".join(
                f'<line x1="{C(X, y, z0)[0]:.1f}" y1="{C(X, y, z0)[1]:.1f}" x2="{C(X, y, z1)[0]:.1f}" y2="{C(X, y, z1)[1]:.1f}"/>' for y in [1 + 0.9 * i for i in range(int(h / 0.9))]) + "</g>")
            out.append(poly(C.quad_x(X, z0, z1, h - 0.7, h), "#FFF0DC", ' opacity="0.55"'))
            out.append(poly(C.quad_x(X, z0, z1, h - 1.3, h - 0.7), "#000", ' opacity="0.2"'))
            bays = max(2, int((z1 - z0) / 3.2))
            for f_ in range(st):
                y0 = 0.25 if f_ == 0 else 3.6 * f_ + 0.4
                hh = 3.0 if f_ == 0 else 2.7
                for i in range(bays):
                    za = z0 + (z1 - z0) * (i + 0.3) / bays
                    zb = z0 + (z1 - z0) * (i + 0.7) / bays
                    on = rb.random() < (0.75 if f_ == 0 else 0.45)
                    q = C.quad_x(X, za, zb, y0, y0 + hh)
                    out.append(poly(q, rb.choice(lit) if on else "#2A2234"))
                    if on:
                        mid = (za + zb) / 2
                        a_, b_ = C(X, y0, mid), C(X, y0 + hh, mid)
                        out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#7A4A2A" stroke-width="{max(0.5, 25 / mid):.1f}" opacity="0.6"/>')
                    # louvered shutters folded open beside the doors
                    for zs0, zs1 in ((za - (zb - za) * 0.5, za), (zb, zb + (zb - za) * 0.5)):
                        out.append(poly(C.quad_x(X, zs0, zs1, y0, y0 + hh), shut))
                    out.append(poly(C.quad_x(X, za - 0.1, zb + 0.1, y0 + hh, y0 + hh + 0.25), "#FFF0DC", ' opacity="0.5"'))
            out.append(poly(C.quad_x(X, z0, z0 + 0.35, 0, h), "#000", ' opacity="0.18"'))
            if z0 != 44:
                galleries.append((sgn, z0, z1, h, st, k))
        out.append(f'<g>' + "".join(poly(C.quad_x(X, z0, z1, 0, h), f"url(#{u}-dark)") for z0, z1, h, *_ in blds) + "</g>")
    # warm light pools under each gallery
    for sgn, z0, z1, h, st, k in galleries:
        out.append(poly([C(sgn * W, 0.16, z0 + 0.5), C(sgn * W, 0.16, z1 - 0.5), C(sgn * XO, 0.16, z1 - 0.5), C(sgn * XO, 0.16, z0 + 0.5)], "#FFB860", ' opacity="0.16"'))
    # cast-iron galleries, far to near, with ferns and gas lanterns
    iron = "#1A1420"
    for sgn, z0, z1, h, st, k in sorted(galleries, key=lambda t: -t[1]):
        X, Xo = sgn * W, sgn * XO
        levels = [3.6, 7.2] if st == 3 else [3.6]
        top = 10.8 if st == 3 else 7.0
        zm = (z0 + z1) / 2
        for Yd in levels:
            out.append(poly([C(X, Yd, z0), C(X, Yd, z1), C(Xo, Yd, z1), C(Xo, Yd, z0)], "#2A1E2A"))     # soffit
            out.append(poly(C.quad_x(Xo, z0, z1, Yd - 0.25, Yd), "#3A2A34"))                           # fascia
            out.append(lace_railing(C, Xo, z0, z1, Yd, Yd + 1.0, iron, k))
        out.append(poly([C(X, top, z0), C(X, top, z1), C(Xo, top, z1), C(Xo, top, z0)], "#241A26"))
        out.append(poly(C.quad_x(Xo, z0, z1, top - 0.3, top), "#3A2A34"))
        # posts at the curb with lacy brackets
        n = max(2, int((z1 - z0) / 3)) + 1
        for i in range(n):
            z = z0 + (z1 - z0) * i / (n - 1)
            a_, b_ = C(Xo, 0.15, z), C(Xo, top, z)
            out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="{iron}" stroke-width="{max(0.7, C.f * 0.09 / z):.1f}"/>')
            for Yd in levels + [top]:
                p1, p2, p3 = C(Xo, Yd - 0.7, z), C(Xo, Yd - 0.05, z + 0.6), C(Xo, Yd - 0.05, z - 0.6)
                out.append(f'<path d="M {p2[0]:.1f} {p2[1]:.1f} Q {p1[0]:.1f} {p2[1]:.1f} {p1[0]:.1f} {p1[1]:.1f} Q {p1[0]:.1f} {p3[1]:.1f} {p3[0]:.1f} {p3[1]:.1f}" fill="none" stroke="{iron}" stroke-width="{max(0.5, C.f * 0.05 / z):.1f}"/>')
        # ferns and flowers along the railings
        rf = random.Random(k * 13 + sgn)
        for Yd in levels:
            for i in range(max(1, int((z1 - z0) / 4))):
                z = z0 + (z1 - z0) * (i + rf.uniform(0.3, 0.7)) / max(1, int((z1 - z0) / 4))
                x, y = C(Xo, Yd + 1.0, z)
                out.append(fern(x, y, C.f * rf.uniform(0.2, 0.28) / z, rf.randrange(999)))
                if rf.random() < 0.5:
                    x2, y2 = C(Xo, Yd + 1.05, z + 0.9)
                    out.append(dots(6, rf.randrange(999), (x2 - C.f * 0.3 / z, y2 - C.f * 0.2 / z, x2 + C.f * 0.3 / z, y2), rf.choice(["#F25A7A", "#FFD25E", "#F28AA8"]), r=(C.f * 0.06 / z, C.f * 0.1 / z), opacity=(0.8, 1)))
        # gas lantern by the door
        lz = z0 + (z1 - z0) * 0.5
        lx, ly = C(X - sgn * 0.35, 2.7, lz)
        s = C.f / lz
        out.append(glow(lx, ly, s * 1.6, "#FFC870", f"{u}-gl{k}{sgn + 1}", 0.7))
        out.append(f'<path d="M {lx - s * 0.16:.1f} {ly - s * 0.25:.1f} L {lx + s * 0.16:.1f} {ly - s * 0.25:.1f} L {lx + s * 0.12:.1f} {ly + s * 0.22:.1f} L {lx - s * 0.12:.1f} {ly + s * 0.22:.1f} Z" fill="#FFE6A0" stroke="#2A1E1A" stroke-width="{max(0.5, s * 0.03):.1f}"/>')
        out.append(f'<path d="M {lx - s * 0.2:.1f} {ly - s * 0.25:.1f} L {lx:.1f} {ly - s * 0.42:.1f} L {lx + s * 0.2:.1f} {ly - s * 0.25:.1f} Z" fill="#2A1E1A"/>')
    # Mardi Gras beads looped over the lower railings
    rbd = random.Random(21)
    for sgn, z0, z1, h, st, k in galleries:
        if z0 > 60 or z0 < 8:
            continue
        Xo = sgn * XO
        for i in range(int((z1 - z0) / 2.5)):
            za = z0 + rbd.uniform(0.3, 0.6) + i * 2.5
            zb = za + rbd.uniform(0.6, 1.2)
            sag = rbd.uniform(0.5, 1.1)
            a_, b_, m_ = C(Xo, 4.6, za), C(Xo, 4.6, zb), C(Xo, 4.6 - sag, (za + zb) / 2)
            col = rbd.choice(["#9A4ACF", "#3EBE5A", "#F2C030"])
            out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} Q {2 * m_[0] - (a_[0] + b_[0]) / 2:.1f} {2 * m_[1] - (a_[1] + b_[1]) / 2:.1f} {b_[0]:.1f} {b_[1]:.1f}" fill="none" stroke="{col}" stroke-width="{min(3, max(1, C.f * 0.05 / za)):.1f}" stroke-dasharray="{max(0.8, C.f * 0.05 / za):.1f} {max(0.4, C.f * 0.02 / za):.1f}" stroke-linecap="round"/>')
    # street texture: worn asphalt, a gutter line, glints of lamplight
    out.append(dots(160, 31, (0, 320, 600, 444), "#8A6A7A", r=(0.5, 1.6), opacity=(0.15, 0.4)))
    for sgn in (-1, 1):
        g0, g1 = C(sgn * (XO - 0.4), 0, 3), C(sgn * (XO - 0.4), 0, 100)
        out.append(f'<line x1="{g0[0]:.1f}" y1="{g0[1]:.1f}" x2="{g1[0]:.1f}" y2="{g1[1]:.1f}" stroke="#1A1220" stroke-width="2" opacity="0.4"/>')
    for sgn, z0, z1, h, st, k in galleries:
        lz = z0 + (z1 - z0) * 0.5
        x, y = C(sgn * (XO - 1.2), 0, lz + 1.5)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{C.f * 0.7 / lz:.1f}" ry="{C.f * 0.1 / lz:.1f}" fill="url(#{u}-pool)"/>')
    # people strolling and a couple dancing to the horn
    for X, Z, h, c, sk in ((-2.4, 60, 1.7, "#E0C27A", False), (-1.8, 60.5, 1.6, "#B8574A", True), (2.6, 34, 1.75, "#3E6A8A", False),
                           (-4.6, 24, 1.7, "#7A5A9A", False), (4.4, 18, 1.6, "#E89A6A", True), (-1.3, 12.5, 1.65, "#C8486A", True), (-0.6, 12.6, 1.8, "#2E3A5A", False)):
        x, b = C(X, 0.15 if abs(X) > XO else 0, Z)
        hh = C.f * h / Z
        if Z == 12.5:      # the dancing couple: she twirls under his raised hand
            out.append(figure(x, b, hh, c, skirt=True, rim="#FFB870", pose="wave", light=1, seed=201, tint=("#2A2040", 0.22)))
        elif Z == 12.6:
            out.append(figure(x, b, hh, c, rim="#FFB870", pose="point", facing=-1, light=1, seed=202, tint=("#2A2040", 0.22), pal={"top_kind": "jacket", "bottom": "#1E1A26", "hat_kind": "cap"}))
        else:
            out.append(figure(x, b, hh, c, skirt=sk, rim="#FFB870", pose=("stand_back", "walk", "stand_34")[int(Z) % 3], facing=-1 if X > 0 else 1, light=1 if X < 0 else -1,
                              tint=("#2A2040", 0.25)))
    # the trumpeter on the near banquette, his open case catching coins
    mx, mb = C(3.1, 0, 7.0)
    out.append(f'<ellipse cx="{mx:.1f}" cy="{mb + 2:.1f}" rx="34" ry="5" fill="#140E18" opacity="0.5"/>')
    out.append(f'<path d="M {mx - 10:.1f} {mb + 1:.1f} L {mx - 120:.1f} {mb + 26:.1f} L {mx - 100:.1f} {mb + 30:.1f} L {mx + 8:.1f} {mb + 2:.1f} Z" fill="#140E18" opacity="0.35"/>')
    out.append(musician(mx, mb, C.f * 1.8 / 7.0))
    out.append(f'<path d="M {mx - 64:.1f} {mb + 4:.1f} l 40 -4 l 6 10 l -40 5 Z" fill="#3A2420"/><path d="M {mx - 61:.1f} {mb + 5:.1f} l 34 -3.6 l 4 7 l -34 4 Z" fill="#7A2A3A"/>')
    out.append(dots(9, 77, (mx - 56, mb + 4, mx - 30, mb + 10), "#FFE08A", r=(1, 1.8), opacity=(0.8, 1)))
    out.append(gulls([(250, 150, 8), (268, 160, 6)], "#2A2440", 1.8))
    return "\n".join(out)



# ---------------------------------------------------------------- Charleston (Rainbow Row, early morning)
def carriage(x, y, s, angle):
    """Horse-drawn tour carriage in profile heading left, skewed to sit on a receding street."""
    k = math.tan(math.radians(angle))
    return (f'<g transform="translate({x:.1f} {y:.1f}) matrix({s:.3f} {s * k:.3f} 0 {s:.3f} 0 0)">'
            '<ellipse cx="18" cy="2" rx="96" ry="6" fill="#4A3A3A" opacity="0.3"/>'
            # horse (grey draft mule) walking left
            '<path d="M -70 -50 Q -64 -62 -48 -62 L -20 -62 Q -6 -62 -4 -48 L -6 -36 L -12 -36 L -14 -8 L -20 -8 L -22 -34 L -48 -36 L -52 -8 L -58 -8 L -60 -36 Q -70 -40 -70 -50 Z" fill="#CFC8C0"/>'
            '<path d="M -70 -50 Q -64 -62 -48 -62 L -40 -62 Q -56 -56 -60 -40 Q -68 -42 -70 -50 Z" fill="#F2EEE8"/>'
            '<path d="M -64 -58 L -78 -84 Q -82 -92 -90 -88 L -98 -70 Q -100 -64 -94 -64 L -84 -70 L -72 -50 Z" fill="#CFC8C0"/>'
            '<path d="M -78 -84 L -74 -94 L -72 -82 Z M -84 -86 L -84 -96 L -79 -86 Z" fill="#B8B0A8"/>'
            '<path d="M -64 -58 L -76 -80 Q -72 -70 -60 -56 Z" fill="#8A8078"/>'
            '<circle cx="-89" cy="-80" r="1.6" fill="#2A2420"/>'
            '<path d="M -94 -68 L -70 -60 L -48 -48 L 6 -44" fill="none" stroke="#3A2A22" stroke-width="2.4"/>'
            '<path d="M -66 -60 Q -58 -48 -60 -38" fill="none" stroke="#3A2A22" stroke-width="3.6"/>'
            '<path d="M -4 -48 Q 4 -44 2 -28" fill="none" stroke="#8A8078" stroke-width="3" stroke-linecap="round"/>'
            '<path d="M -58 -8 L -58 -2 M -52 -8 L -50 -2 M -20 -8 L -22 -2 M -14 -8 L -12 -2" stroke="#3A322E" stroke-width="4.4" stroke-linecap="round"/>'
            # carriage: green body, cream canopy with scalloped fringe, yellow wheels
            '<path d="M 0 -44 L 116 -44 L 116 -20 L 6 -20 Q 0 -30 0 -44 Z" fill="#2E5A44"/>'
            '<path d="M 0 -44 L 116 -44 L 116 -40 L 0 -40 Z" fill="#E8C870"/>'
            '<path d="M 10 -44 L 10 -94 M 60 -44 L 60 -94 M 112 -44 L 112 -94" stroke="#2A2A26" stroke-width="2"/>'
            '<path d="M 4 -94 Q 60 -104 118 -94 L 118 -88 L 4 -88 Z" fill="#F6F0E2"/>'
            '<path d="M 4 -88 ' + " ".join(f'q 3.6 5 7.2 0' for _ in range(16)) + ' L 4 -88 Z" fill="#F6F0E2"/>'
            '<path d="M 4 -94 Q 60 -104 118 -94 L 118 -91 Q 60 -100 4 -91 Z" fill="#D8C8A8"/>'
            # passengers and the driver
            + "".join(F.person(px, -41, 70, "sit_front", 1, {"top": c, "hair": hc, "no_legs": True, "season": "summer"}, seed=300 + px, rim="#FFF0D0", light=1, shadow=0)
                      for px, c, hc in ((30, "#E07A6A", "#5A3A2A"), (48, "#3E6A9A", "#2A1E18"), (76, "#F2D07A", "#7A4A30"), (94, "#7A5A9A", "#3A2A20")))
            + F.person(11, -41, 74, "sit", -1, {"top": "#2A2A30", "top_kind": "jacket", "bottom": "#2A2A30", "hat_kind": "sunhat", "hat": "#E8DCC0", "form": "m", "no_legs": True},
                       seed=311, rim="#FFF0D0", light=1, shadow=0) +
            '<path d="M 4 -56 L -50 -58" stroke="#2A2420" stroke-width="1.2"/>'
            + "".join(f'<g transform="translate({wx} -14)"><circle r="{wr}" fill="none" stroke="#E8B848" stroke-width="3.4"/><circle r="3" fill="#E8B848"/>'
                      + "".join(f'<line x1="0" y1="0" x2="{wr * math.cos(i * math.pi / 5):.1f}" y2="{wr * math.sin(i * math.pi / 5):.1f}" stroke="#E8B848" stroke-width="1.4"/>' for i in range(10)) + "</g>"
                      for wx, wr in ((24, 13), (100, 15)))
            + "</g>")


def charleston():
    u = "cs"
    C = Cam(f=330, cx=520, vpy=340, eye=1.7)
    XF = -24.0                       # facade plane (we stand across East Bay Street)
    out = [defs(
        lg(f"{u}-sky", [(0, "#7FB4DA"), (0.45, "#B4D6E8"), (0.8, "#EDE6D6"), (1, "#F8DCC0")]),
        lg(f"{u}-cl", [(0, "#FFFFFF"), (1, "#E8D4D0")], 0, 0, 0, 1),
        lg(f"{u}-street", [(0, "#B8A898"), (1, "#7A6A62")], 0, 340, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-glass", [(0, "#4A5E72"), (0.5, "#7A98AE"), (1, "#3A4A5E")]),
        lg(f"{u}-warm", [(0, "#FFE8C0", 0.0), (1, "#FFD8A0", 0.25)], 0, 0, 1, 0),
        lg(f"{u}-shade", [(0, "#3A2A4A", 0.2), (0.3, "#3A2A4A", 0.0)], 0, 0, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(540, 330, 260, "#FFE6C0", f"{u}-sun", 0.6))
    # soft morning cloud banks, pink underneath
    rw = random.Random(6)
    for cx0, cy0, wd, n in ((330, 110, 260, 18), (470, 182, 180, 12), (130, 70, 160, 10)):
        for i in range(n):
            x = cx0 + rw.uniform(-0.5, 0.5) * wd
            y = cy0 + rw.uniform(-8, 8)
            rx, ry = rw.uniform(24, 60), rw.uniform(5, 10)
            out.append(f'<ellipse cx="{x:.1f}" cy="{y + ry * 0.5:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#F0C8C8" opacity="0.45"/>')
            out.append(f'<ellipse cx="{x - 4:.1f}" cy="{y:.1f}" rx="{rx * 0.9:.1f}" ry="{ry * 0.8:.1f}" fill="#FFFFFF" opacity="0.6"/>')
    # live oaks of White Point Garden closing the far end of the street
    ro = random.Random(2)
    oak = []
    for i in range(60):
        X = ro.uniform(-14, 60)
        Z = ro.uniform(240, 320)
        x, y = C(X, ro.uniform(3, 9), Z)
        oak.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{C.f * ro.uniform(2, 4) / Z:.1f}" fill="{ro.choice(["#7A9A84", "#88A890", "#6E8E7A"])}"/>')
    out.append("".join(oak))
    out.append(gulls([(330, 120, 9), (350, 132, 6), (420, 110, 7)], "#4A5A6E"))
    houses = [(5, 13, 12.4, "#F2E6CC", "flat"), (13, 20, 13.2, "#EFAFBE", "roof"), (20, 27, 12.0, "#F4DC8A", "flat"), (27, 33.5, 12.6, "#A6CFE4", "roof"),
              (33.5, 39.5, 11.6, "#B8DDB0", "flat"), (39.5, 46, 12.8, "#D6BCE6", "roof"), (46, 52.5, 11.8, "#F6C29A", "flat"),
              (52.5, 59, 12.4, "#9ED6CE", "roof"), (59, 66, 11.4, "#E8A0A8", "flat"), (66, 73, 12.2, "#F0D27A", "roof"),
              (73, 81, 11.8, "#9CC0E0", "flat"), (81, 90, 12.4, "#F2C0A8", "roof"), (90, 220, 11.0, "#E6D2B8", "flat")]
    green = "#24402F"
    # roofs first (they sit behind the parapets), then facades near-last
    for k, (z0, z1, h, col, kind) in enumerate(reversed(houses)):
        if kind == "roof":
            out.append(poly([C(XF, h - 0.2, z0), C(XF, h - 0.2, z1), C(XF - 3.5, h + 3.4, z1), C(XF - 3.5, h + 3.4, z0)], "#6A4E4A"))
            out.append(poly([C(XF, h - 0.2, z0), C(XF, h - 0.2, z1), C(XF - 0.6, h + 0.4, z1), C(XF - 0.6, h + 0.4, z0)], "#8A6A60"))
            zc = z0 + (z1 - z0) * 0.5
            out.append(poly(C.quad_x(XF - 1.6, zc - 0.9, zc + 0.9, h + 1.4, h + 2.8), "#F4EEE2"))
            out.append(poly([C(XF - 1.6, h + 2.8, zc - 1.1), C(XF - 1.6, h + 2.8, zc + 1.1), C(XF - 1.6, h + 3.6, zc)], "#5A4040"))
            out.append(poly(C.quad_x(XF - 1.6, zc - 0.5, zc + 0.5, h + 1.6, h + 2.6), "#5A6E80"))
        cz = z1 - 1.2
        out.append(poly(C.quad_x(XF - 2.5, cz - 0.6, cz + 0.6, h, h + 4.4), "#9A5A48"))
        out.append(poly(C.quad_x(XF - 2.5, cz - 0.7, cz + 0.7, h + 4.1, h + 4.5), "#7A4438"))
    for k, (z0, z1, h, col, kind) in enumerate(reversed(houses)):
        rb = random.Random(k * 3 + 1)
        face = C.quad_x(XF, z0, z1, 0, h)
        out.append(poly(face, col))
        zm = (z0 + z1) / 2
        sw = max(0.5, C.f * 0.04 / zm)
        # stucco scoring and grime at the base
        out.append(f'<g stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="{sw:.1f}">' + "".join(
            f'<line x1="{C(XF, y, z0)[0]:.1f}" y1="{C(XF, y, z0)[1]:.1f}" x2="{C(XF, y, z1)[0]:.1f}" y2="{C(XF, y, z1)[1]:.1f}"/>' for y in [0.6 + 0.6 * i for i in range(int(h / 0.6))]) + "</g>")
        out.append(poly(C.quad_x(XF, z0, z1, 0, 0.9), "#5A4A44", ' opacity="0.22"'))
        # cornice and parapet
        out.append(poly(C.quad_x(XF, z0, z1, h - 0.9, h), "#FBF6EC"))
        out.append(poly(C.quad_x(XF, z0, z1, h - 1.25, h - 0.9), "#000", ' opacity="0.16"'))
        out.append(poly(C.quad_x(XF, z0, z1, 3.5, 3.8), "#FBF6EC", ' opacity="0.8"'))
        bays = 3
        for fl, (ya, yb) in enumerate(((4.5, 6.9), (8.1, 10.2))):
            for i in range(bays):
                za = z0 + (z1 - z0) * (i + 0.32) / bays
                zb = z0 + (z1 - z0) * (i + 0.68) / bays
                out.append(poly(C.quad_x(XF, za - 0.08, zb + 0.08, ya - 0.08, yb + 0.12), "#FBF6EC"))
                out.append(poly(C.quad_x(XF, za, zb, ya, yb), f"url(#{u}-glass)"))
                if zm < 40:
                    m1, m2 = C(XF, ya, (za + zb) / 2), C(XF, yb, (za + zb) / 2)
                    out.append(f'<line x1="{m1[0]:.1f}" y1="{m1[1]:.1f}" x2="{m2[0]:.1f}" y2="{m2[1]:.1f}" stroke="#FBF6EC" stroke-width="{sw:.1f}"/>')
                    for t in (0.33, 0.66):
                        a_, b_ = C(XF, ya + (yb - ya) * t, za), C(XF, ya + (yb - ya) * t, zb)
                        out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#FBF6EC" stroke-width="{sw:.1f}"/>')
                # Charleston-green shutters
                wz = (zb - za) * 0.5
                for zs0, zs1 in ((za - wz - 0.06, za - 0.06), (zb + 0.06, zb + wz + 0.06)):
                    out.append(poly(C.quad_x(XF, zs0, zs1, ya, yb), green))
                    if zm < 30:
                        out.append(f'<g stroke="#3E6A50" stroke-width="{sw * 0.8:.1f}">' + "".join(
                            f'<line x1="{C(XF, yy, zs0)[0]:.1f}" y1="{C(XF, yy, zs0)[1]:.1f}" x2="{C(XF, yy, zs1)[0]:.1f}" y2="{C(XF, yy, zs1)[1]:.1f}"/>' for yy in [ya + 0.18 * j for j in range(1, int((yb - ya) / 0.18))]) + "</g>")
                if fl == 0 and rb.random() < 0.45:      # window box with flowers
                    out.append(poly(C.quad_x(XF + 0.2, za - 0.1, zb + 0.1, ya - 0.45, ya - 0.05), "#3A5A3A"))
                    bx0, by0 = C(XF + 0.2, ya + 0.15, za)
                    bx1, by1 = C(XF + 0.2, ya - 0.1, zb)
                    out.append(blobs(10, k * 10 + i, (bx0, by0, bx1, by1), ["#E8507A", "#F2A0B8", "#FFFFFF", "#5E9A4A"], r=(C.f * 0.08 / zm, C.f * 0.16 / zm), opacity=(0.9, 1), squash=0.8))
        # ground floor: panelled door with fanlight, two shop windows
        dz0, dz1 = z0 + (z1 - z0) * 0.1, z0 + (z1 - z0) * 0.26
        out.append(poly(C.quad_x(XF, dz0 - 0.1, dz1 + 0.1, 0.1, 3.0), "#FBF6EC"))
        out.append(poly(C.quad_x(XF, dz0, dz1, 0.1, 2.4), rb.choice([green, "#2E3E5E", "#6A2E2E"])))
        out.append(poly(C.quad_x(XF, dz0, dz1, 2.45, 2.95), f"url(#{u}-glass)"))
        for za, zb in ((z0 + (z1 - z0) * 0.4, z0 + (z1 - z0) * 0.62), (z0 + (z1 - z0) * 0.72, z0 + (z1 - z0) * 0.92)):
            out.append(poly(C.quad_x(XF, za - 0.08, zb + 0.08, 0.7, 3.1), "#FBF6EC"))
            out.append(poly(C.quad_x(XF, za, zb, 0.8, 3.0), f"url(#{u}-glass)"))
        if kind == "roof" and zm < 60:      # wrought-iron balcony on the piano nobile
            za, zb = z0 + (z1 - z0) * 0.25, z0 + (z1 - z0) * 0.75
            out.append(poly([C(XF, 4.4, za), C(XF, 4.4, zb), C(XF + 0.8, 4.4, zb), C(XF + 0.8, 4.4, za)], "#1E1E22"))
            out.append(poly(C.quad_x(XF + 0.8, za, zb, 4.4, 4.5), "#1E1E22"))
            out.append(lace_railing(C, XF + 0.8, za, zb, 4.4, 5.3, "#1E1E22", k))
        # party-wall shadow line and a soft warm wash of morning light
        out.append(poly(C.quad_x(XF, z0, z0 + 0.25, 0, h), "#000", ' opacity="0.12"'))
        out.append(poly(face, f"url(#{u}-warm)"))
    # sidewalk, curb and the cobbled street
    XC = -21.0
    out.append(poly([C(XF, 0, 300), C(XC, 0.15, 300), C(XC, 0.15, 4), C(XF, 0, 4)], "#C9B8A4"))
    for z in (6, 7.5, 9.2, 11.4, 14, 17, 21, 26, 32, 40, 50, 64):
        a_, b_ = C(XF, 0, z), C(XC, 0.15, z)
        out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#8A7868" stroke-width="{max(0.5, 10 / z):.1f}" opacity="0.6"/>')
    out.append(poly([C(XC, 0.15, 300), C(XC, 0.15, 4), C(XC, 0, 4), C(XC, 0, 300)], "#E8DCCC"))
    out.append(poly([C(XC, 0, 300), C(6, 0, 300), C(6, 0, 2.2), C(XC, 0, 2.2)], "#5E5048"))
    rc = random.Random(9)
    cob = []
    z = 2.3
    while z < 70:
        dz = 0.26 * (z / 3) ** 0.2
        X = XC + rc.uniform(0, 0.3)
        while X < 6:
            w = rc.uniform(0.28, 0.46) * (z / 3) ** 0.2
            q = [C(X + 0.04, 0, z + 0.03), C(X + w - 0.04, 0, z + dz - 0.03)]
            if q[1][0] > -5 and q[0][0] < 605 and q[0][1] > 330:
                x0_, x1_ = q[0][0], q[1][0]
                y0_, y1_ = q[1][1], q[0][1]
                rr = (y1_ - y0_) * 0.45
                cob.append(f'<rect x="{x0_:.1f}" y="{y0_:.1f}" width="{x1_ - x0_:.1f}" height="{y1_ - y0_:.1f}" rx="{rr:.1f}" fill="{rc.choice(["#C8B8A4", "#A89684", "#B8A694", "#D2C2AC", "#968472", "#B4A08A"])}"/>')
                if y1_ - y0_ > 3:
                    cob.append(f'<rect x="{x0_ + (x1_ - x0_) * 0.15:.1f}" y="{y0_ + 0.5:.1f}" width="{(x1_ - x0_) * 0.6:.1f}" height="{(y1_ - y0_) * 0.3:.1f}" rx="{rr * 0.4:.1f}" fill="#F4E8D4" opacity="0.45"/>')
            X += w
        z += dz
    out.append("".join(cob))
    out.append(f'<rect x="0" y="340" width="600" height="104" fill="url(#{u}-shade)"/>')
    # long morning shadows of the palmettos lying across the street toward the houses
    for zs in (17, 32, 54, 9):
        a_, b_, c_, d_ = C(1.3, 0, zs), C(XC, 0, zs + 6), C(XC, 0, zs + 6.25), C(1.3, 0, zs + 0.3)
        out.append(poly([a_, b_, c_, d_], "#3A2E4A", ' opacity="0.24"'))
        x, y = C(XC + 0.5, 0, zs + 6.6)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{C.f * 2.4 / (zs + 6):.1f}" ry="{C.f * 0.45 / (zs + 6):.1f}" fill="#3A2E4A" opacity="0.16"/>')
    # people on the sidewalk
    for X, Z, h, c, sk in ((-22.6, 30, 1.7, "#E07A6A", True), (-22.2, 30.6, 1.8, "#3E5A8A", False), (-22.4, 52, 1.7, "#F2F0E8", False), (-22.0, 18, 1.65, "#7A5A9A", True), (-22.8, 40, 1.6, "#5A8A6A", False)):
        x, b = C(X, 0.1, Z)
        out.append(figure(x, b, C.f * h / Z, c, skirt=sk, rim="#FFF0D0", pose=("walk", "stand_back", "stand")[int(Z) % 3], facing=1, light=1, pal={"season": "summer"}))
    # the carriage clopping toward us
    cx_, cy_ = C(-11.5, 0, 14)
    ang = math.degrees(math.atan2(340 - cy_, 520 - cx_))
    out.append(f'<path d="M {cx_ - 90:.1f} {cy_ + 2:.1f} L {cx_ - 150:.1f} {cy_ + 6:.1f} L {cx_ + 90:.1f} {cy_ - 30:.1f} L {cx_ + 120:.1f} {cy_ - 30:.1f} Z" fill="#3A2E4A" opacity="0.12"/>')
    out.append(carriage(cx_, cy_, C.f / 14 / 46, ang * 0.9))
    # sabal palmettos along our side of the street
    for X, Z, hh, sd in ((1.2, 90, 8.5, 2), (1.2, 54, 8.5, 3), (1.2, 32, 9, 5), (1.4, 17, 9.5, 7)):
        x, b = C(X, 0, Z)
        out.append(sabal(x, b, C.f * hh / Z, sd, frond="#4E8A4A", dark="#2E5A34", rim="#E8F0A8", trunk="#8A7660"))
    # pigeons pecking between the stones
    for px, py, s_, fl in ((150, 418, 1.0, 1), (178, 426, 1.1, -1), (205, 414, 0.9, 1)):
        out.append(f'<g transform="translate({px} {py}) scale({s_ * fl} {s_})"><ellipse cx="0" cy="-6" rx="9" ry="5.5" fill="#8A8E9E"/><path d="M 6 -9 L 16 -12 L 12 -5 Z" fill="#6E7282"/>'
                   '<circle cx="-8" cy="-10" r="3.6" fill="#6E7282"/><path d="M -11 -10 l -3 1.2 l 3 0.8 Z" fill="#E8C8A0"/><path d="M -6 -7 q 4 2 8 0" stroke="#7ABAA0" stroke-width="1.6" fill="none"/>'
                   '<path d="M -2 -1 l -1 3 M 2 -1 l 1 3" stroke="#D8786A" stroke-width="1.2"/></g>')
    x, b = C(1.6, 0, 9)
    out.append(sabal(x, b + 10, C.f * 9.2 / 9, 13, frond="#467E44", dark="#2A4E30", rim="#F0F4B0", trunk="#8A7660", lean=-0.03))
    return "\n".join(out)



# ---------------------------------------------------------------- Seattle (a ferry crossing Elliott Bay at dusk)
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


def wsf_ferry(x, y, s, u):
    """Double-ended green-and-white car ferry seen broadside, heading left; (x, y) = waterline centre,
    s = scale (1 -> 240 px long). Lit by the afterglow from behind the viewer."""
    rnd = random.Random(31)
    g = []
    L = 120
    # hull: raked ends, white topsides, dark green boot-top at the waterline
    hull = [(-L, -24), (L, -24), (L - 10, 0), (-L + 12, 0)]
    g.append(poly(hull, f"url(#{u}-hull)"))
    g.append(poly([(-L + 6, -8), (L - 4, -8), (L - 10, 0), (-L + 12, 0)], "#1E4A3A"))
    # open car deck: dark bays between steel frames, headlights and tail-lights of waiting cars
    g.append(f'<rect x="{-L + 10}" y="-21" width="{2 * L - 20}" height="11" fill="#2A2A3E"/>')
    for i in range(-L + 14, L - 14, 13):
        g.append(f'<rect x="{i}" y="-21" width="3" height="11" fill="#E8E2E6"/>')
    for i in range(14):
        cx = rnd.uniform(-L + 18, L - 18)
        g.append(f'<rect x="{cx:.1f}" y="-15" width="7" height="4.2" rx="1.6" fill="{rnd.choice(["#8A3A4A", "#4A5A7A", "#C8C2CA", "#5A5A6A"])}"/>'
                 f'<circle cx="{cx + 1:.1f}" cy="-12.6" r="0.9" fill="#FFE2A0"/>')
    g.append(f'<rect x="{-L + 4}" y="-26" width="{2 * L - 8}" height="5" fill="#1F7A4E"/>')       # the green stripe
    g.append(f'<rect x="{-L + 4}" y="-26" width="{2 * L - 8}" height="1.4" fill="#7ED0A0" opacity="0.7"/>')
    # passenger cabin with a long band of warm windows
    g.append(poly([(-L + 16, -26), (-L + 22, -44), (L - 22, -44), (L - 16, -26)], f"url(#{u}-cab)"))
    for i in range(-L + 26, L - 28, 7):
        g.append(f'<rect x="{i}" y="-40" width="5" height="8" rx="1" fill="{rnd.choice(["#FFD98E", "#FFE6B0", "#F7C873", "#FFD98E", "#B8A8C0"])}"/>')
    g.append(f'<rect x="{-L + 22}" y="-30" width="{2 * L - 44}" height="1.6" fill="#1F7A4E"/>')
    # sun deck and its railing, a few passengers at the rail
    g.append(f'<rect x="{-L + 20}" y="-46" width="{2 * L - 40}" height="3" fill="#F6F0F0"/>')
    g.append(f'<rect x="{-L + 40}" y="-58" width="{2 * L - 80}" height="12" fill="url(#{u}-cab)"/>')
    for i in range(-L + 46, L - 46, 8):
        g.append(f'<rect x="{i}" y="-55" width="5" height="5" fill="#FFE2A8" opacity="0.9"/>')
    g.append(f'<path d="M {-L + 22} -52 L {-L + 40} -52 M {L - 40} -52 L {L - 22} -52" stroke="#E8E2E6" stroke-width="1.4"/>')
    g.append("".join(f'<line x1="{i}" y1="-52" x2="{i}" y2="-46" stroke="#E8E2E6" stroke-width="1"/>' for i in list(range(-L + 22, -L + 40, 4)) + list(range(L - 40, L - 21, 4))))
    for px, c in ((-L + 28, "#2A2A3E"), (-L + 34, "#6A2A4A"), (L - 30, "#2A3A5A")):
        g.append(F.person(px, -46, 12, "stand_back", 1, {"top": c}, seed=int(px) + 700, shadow=0))
    # a pilot house at each end (double-ended), dark windows with a glint
    for sx in (-1, 1):
        hx = sx * (L - 58)
        g.append(f'<rect x="{hx - 14}" y="-68" width="28" height="10" fill="#F6F0F0"/><rect x="{hx - 12}" y="-66" width="24" height="4.5" fill="#2A3A4A"/>'
                 f'<rect x="{hx - 12}" y="-66" width="24" height="1.4" fill="#F8C8C0" opacity="0.8"/><rect x="{hx - 16}" y="-70" width="32" height="2.6" fill="#1F7A4E"/>')
    # funnel amidships, white with a green band, and a mast with running lights
    g.append(poly([(-9, -58), (-7, -84), (7, -84), (9, -58)], "#F6F0F0"))
    g.append(poly([(1, -58), (2, -84), (7, -84), (9, -58)], "#C8BCD0", ' opacity="0.8"'))
    g.append(f'<rect x="-7.4" y="-80" width="14.8" height="6" fill="#1F7A4E"/><rect x="-7.6" y="-86" width="15.2" height="3" fill="#2A2A36"/>')
    g.append(f'<line x1="-30" y1="-58" x2="-30" y2="-92" stroke="#3A3A4A" stroke-width="1.6"/><line x1="-36" y1="-84" x2="-24" y2="-84" stroke="#3A3A4A" stroke-width="1.4"/>')
    g.append(f'<circle cx="-30" cy="-93" r="1.8" fill="#FFF4D8"/><circle cx="-36" cy="-84" r="1.4" fill="#FF6A5A"/><circle cx="-24" cy="-84" r="1.4" fill="#5AE08A"/>')
    g.append(f'<path d="M 30 -58 L 30 -76 L 42 -73 L 30 -70" fill="#1F7A4E" stroke="#3A3A4A" stroke-width="1"/>')
    # afterglow rim on the cabin roofs and bow
    g.append(f'<path d="M {-L + 22} -44 L {L - 22} -44 M {-L + 40} -58 L {L - 40} -58 M {-L} -24 L {L} -24" stroke="#FFD8D0" stroke-width="1.2" opacity="0.8"/>')
    # bow wave
    g.append(f'<path d="M {-L + 18} 1 Q {-L + 6} -7 {-L - 2} -3 Q {-L - 8} 0 {-L - 12} 2 Q {-L + 2} 4 {-L + 18} 3 Z" fill="#FFFFFF" opacity="0.92"/>')
    g.append("".join(f'<ellipse cx="{-L - 10 - i * 6}" cy="{2.6 + i * 0.6:.1f}" rx="{3.6 - i * 0.7:.1f}" ry="1.1" fill="#FFF4F4" opacity="{0.7 - i * 0.15:.2f}"/>' for i in range(4)))
    g.append(f'<path d="M {-L + 12} 1 L {L - 10} 1" stroke="#FFF0F2" stroke-width="1.6" opacity="0.7"/>')
    return f'<g transform="translate({x} {y}) scale({s})">' + "".join(g) + "</g>"


def lamp_post(x, base, h, u, k):
    """Old waterfront lamp: fluted cast-iron post, crossbar, glowing globe."""
    top = base - h
    return (glow(x, top + 2, h * 0.55, "#FFD8A0", f"{u}-lp{k}", 0.75)
            + f'<path d="M {x - 5} {base} L {x - 2.4} {base - 12} L {x - 1.8} {top + 14} L {x + 1.8} {top + 14} L {x + 2.4} {base - 12} L {x + 5} {base} Z" fill="#141626"/>'
            + f'<rect x="{x - 4}" y="{top + 12}" width="8" height="4" fill="#141626"/>'
            + f'<circle cx="{x}" cy="{top + 4}" r="8" fill="#FFF0CC"/><circle cx="{x - 2.4}" cy="{top + 1.6}" r="3.4" fill="#FFFFFF"/>'
            + f'<path d="M {x - 5} {top - 3} L {x + 5} {top - 3} L {x} {top - 8} Z" fill="#141626"/>'
            + f'<line x1="{x + 2.4}" y1="{base - 12}" x2="{x + 1.8}" y2="{top + 14}" stroke="#F0A8B0" stroke-width="1" opacity="0.5"/>')


def perched_gull(x, y, s):
    """Glaucous-winged gull standing on a piling, facing left."""
    return (f'<g transform="translate({x} {y}) scale({s})">'
            '<path d="M -4 -14 Q -12 -16 -13 -22 Q -12 -28 -5 -28 Q 1 -27 2 -20 L 14 -18 Q 26 -14 30 -10 L 22 -6 Q 12 -2 2 -4 Q -6 -6 -4 -14 Z" fill="#F4F0F2"/>'
            '<path d="M 0 -18 Q 12 -20 30 -10 L 22 -6 Q 12 -6 4 -10 Z" fill="#A8AEBE"/>'
            '<path d="M 22 -12 L 32 -9 L 24 -6 Z" fill="#2A2A36"/>'
            '<path d="M -13 -23 L -21 -21.5 L -13 -20 Z" fill="#F2C24A"/><circle cx="-18" cy="-21.6" r="0.9" fill="#D84A3A"/>'
            '<circle cx="-8" cy="-23.5" r="1.2" fill="#1A1A22"/>'
            '<path d="M 0 -4 L -1 2 M 6 -4 L 6 2" stroke="#E8A0A0" stroke-width="1.6" stroke-linecap="round"/>'
            '<path d="M -5 -28 Q 2 -28 2 -20" stroke="#FFD8D0" stroke-width="1.2" fill="none"/></g>')


def seattle():
    u = "se"
    out = [defs(
        lg(f"{u}-sky", [(0, "#16204C"), (0.28, "#2E3C7A"), (0.52, "#6E68A4"), (0.72, "#C88CB0"), (0.88, "#F2AEB0"), (1, "#F8C8A8")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-mtn", [(0, "#FFF0EE"), (0.3, "#F8C4CC"), (0.7, "#D898B8"), (1, "#A884B0")], 0, 120, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-mtnS", [(0, "#B0A0CC"), (1, "#7A70A0")]),
        lg(f"{u}-bay", [(0, "#F0B4B4"), (0.12, "#C894B4"), (0.4, "#6A6498"), (0.75, "#2E3466"), (1, "#181E42")], 0, 300, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-twr", [(0, "#4C4C80"), (1, "#2A2A56")]),
        lg(f"{u}-haze", [(0, "#D8A0B8", 0), (1, "#D8A0B8", 0.8)]),
        lg(f"{u}-hull", [(0, "#FFF8F4"), (1, "#E2D4DA")]),
        lg(f"{u}-cab", [(0, "#FFFFFF"), (1, "#EADCE2")]),
        lg(f"{u}-pier", [(0, "#4A3A48"), (1, "#241C2A")]),
        lg(f"{u}-len", [(0, "#FFE8EC"), (1, "#E8A8BC")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(40, 2, (0, 40, 600, 140), "#FFF4E0", r=(0.6, 1.3), opacity=(0.3, 0.9)))
    # long cloud streaks lit pink from below
    out.append('<g fill="#F2A8BC" opacity="0.5">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{h}"/>' for x, y, w, h in (
        (100, 150, 100, 5), (40, 162, 60, 3.5), (210, 132, 70, 3), (560, 196, 70, 4), (530, 84, 80, 3))) + "</g>")
    out.append('<g fill="#FFD8C8" opacity="0.5">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="1.8"/>' for x, y, w in ((108, 148, 70), (214, 131, 40), (532, 83, 50))) + "</g>")

    # --- Mount Rainier in alpenglow: broad glaciated dome, Liberty Cap shoulder left, Little Tahoma bump right
    pk = [(250, 296), (300, 270), (340, 240), (370, 210), (392, 184), (410, 160), (424, 146), (440, 136), (462, 131), (484, 133), (502, 140),
          (520, 154), (538, 172), (556, 184), (566, 182), (574, 192), (596, 214), (630, 244), (650, 262)]
    line = rough(pk, 7, amp=3, depth=3)
    mpoly = line + [(650, 300), (250, 300)]
    # a lenticular cap cloud hanging over the summit (Rainier's signature): stacked lenses, lit tops, shaded bellies
    for dy, w, th, op in ((-12, 96, 9, 0.95), (-21, 78, 7, 0.85), (-28, 54, 5, 0.7)):
        cy = 131 + dy
        out.append(f'<path d="M {462 - w} {cy} Q {462 - w * 0.4:.0f} {cy - th * 1.6:.1f} {462} {cy - th * 1.5:.1f} Q {462 + w * 0.4:.0f} {cy - th * 1.6:.1f} {462 + w} {cy} '
                   f'Q {462 + w * 0.4:.0f} {cy + th * 0.9:.1f} {462} {cy + th:.1f} Q {462 - w * 0.4:.0f} {cy + th * 0.9:.1f} {462 - w} {cy} Z" fill="url(#{u}-len)" opacity="{op}"/>')
        out.append(f'<path d="M {462 - w * 0.8:.0f} {cy - th * 0.5:.1f} Q {462} {cy - th * 1.4:.1f} {462 + w * 0.8:.0f} {cy - th * 0.5:.1f}" stroke="#FFF6F4" stroke-width="1.6" fill="none" opacity="0.8"/>')
    out.append(poly(mpoly, f"url(#{u}-mtn)"))
    cid = f"{u}-mc"
    out.append(f'<clipPath id="{cid}"><polygon points="{P(mpoly)}"/></clipPath>')
    g = []
    # shadowed north face on the left
    g.append(poly([(440, 136), (424, 146), (410, 160), (392, 184), (370, 210), (340, 240), (300, 270), (250, 296), (250, 300), (400, 300), (404, 240), (418, 190), (434, 156)], f"url(#{u}-mtnS)", ' opacity="0.7"'))
    # broad fluted facets: soft lavender shadow wedges running down from below the summit dome
    rr = random.Random(13)
    for i in range(9):
        x0 = 410 + i * 20 + rr.uniform(-6, 6)
        y0 = (y_on(line, x0) or 200) + rr.uniform(16, 30)
        dx = (x0 - 466) * 0.55
        L = rr.uniform(70, 120)
        w = rr.uniform(7, 14)
        g.append(poly([(x0, y0), (x0 + dx * 0.5 + w, y0 + L * 0.6), (x0 + dx + w * 0.4, y0 + L), (x0 + dx - w * 0.6, y0 + L), (x0 + dx * 0.45 - w * 0.2, y0 + L * 0.5)],
                      "#B888B4", f' opacity="{rr.uniform(0.18, 0.3):.2f}"'))
    # dark rock cleavers on the lower flanks between the glaciers: irregular tapered ribs with a lit edge
    for i, (x0, y0, L, w) in enumerate(((378, 214, 46, 4.5), (414, 196, 34, 3), (444, 176, 30, 2.6), (512, 172, 40, 3.4), (540, 196, 54, 4.6),
                                        (566, 214, 40, 4), (590, 232, 36, 4.2), (470, 214, 30, 3), (346, 248, 40, 4))):
        ang = math.radians(90 + (x0 - 466) * 0.32)
        pts = [(x0, y0)]
        for j in range(6):
            ang += math.radians(rr.uniform(-9, 9))
            px, py = pts[-1]
            pts.append((px + L / 6 * math.cos(ang), py + L / 6 * math.sin(ang)))
        left = [(px - w * math.sin(math.pi * (k + 0.5) / 7) * rr.uniform(0.7, 1.2), py) for k, (px, py) in enumerate(pts)]
        right = [(px + w * 0.6 * math.sin(math.pi * (k + 0.5) / 7), py) for k, (px, py) in enumerate(pts)]
        g.append(poly(left + right[::-1], rr.choice(["#7A5C86", "#86668E", "#6E5482"]), ' opacity="0.55"'))
        g.append(f'<polyline points="{P(left[1:-1])}" fill="none" stroke="#FFE4EA" stroke-width="1.1" opacity="0.55"/>')
    # crevasse lines across the glaciers
    g.append('<g stroke="#C08AAA" stroke-width="1.2" fill="none" opacity="0.45">' + "".join(
        f'<path d="M {x} {y} q {rr.uniform(6, 12):.1f} {rr.uniform(-2, 2):.1f} {rr.uniform(14, 24):.1f} 0"/>' for x, y in
        [(rr.uniform(440, 570), rr.uniform(170, 236)) for _ in range(10)]) + "</g>")
    g.append(f'<rect x="240" y="232" width="420" height="70" fill="url(#{u}-haze)"/>')
    out.append(f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>")
    out.append(f'<polyline points="{P([p for p in line if 430 < p[0] < 600])}" fill="none" stroke="#FFF6F2" stroke-width="2" opacity="0.9"/>')

    # far hills in blue haze under the mountain
    pl, fl = ridge_poly([(-10, 286), (120, 280), (260, 286), (380, 278), (500, 284), (610, 276)], 3, base=304, amp=3, fill="#8A78A8")
    out.append(pl)
    out.append(tree_line(fl, 5, ["#8072A2", "#7A6C9C"], density=1.4, hmin=4, hmax=8))
    out.append(f'<rect x="0" y="250" width="600" height="56" fill="url(#{u}-haze)" opacity="0.7"/>')

    # --- port cranes in the harbour beneath the mountain
    for cx_, hgt, flip in ((452, 50, 1), (494, 56, -1), (530, 48, 1)):
        b = 302
        t = b - hgt
        out.append(f'<g stroke="#4A4070" stroke-width="2" fill="none" stroke-linejoin="round">'
                   f'<path d="M {cx_ - 9} {b} L {cx_ - 6} {t} L {cx_ + 6} {t} L {cx_ + 9} {b} M {cx_ - 8} {b - hgt * 0.4:.1f} L {cx_ + 8} {b - hgt * 0.4:.1f}"/>'
                   f'<path d="M {cx_ - 22 * flip} {t + 4} L {cx_ + 34 * flip} {t + 4} M {cx_} {t} L {cx_ + 4 * flip} {t - 10} L {cx_ + 28 * flip} {t + 4}"/></g>'
                   f'<rect x="{cx_ - 5}" y="{t - 1}" width="10" height="6" fill="#4A4070"/><circle cx="{cx_ + 4 * flip}" cy="{t - 11}" r="1.5" fill="#FF6A6A"/>')
    out.append(f'<rect x="420" y="298" width="150" height="5" fill="#3E3664"/>')
    rc = random.Random(17)
    out.append("".join(f'<rect x="{rc.uniform(424, 560):.1f}" y="{rc.choice([292, 295, 298]):.0f}" width="9" height="3.4" fill="{rc.choice(["#B05A5A", "#4E7A9A", "#C8964A", "#6A5A8A"])}" opacity="0.8"/>' for _ in range(16)))

    # --- downtown skyline on the left shore, lights coming on (generic towers)
    towers = [(48, 26, 222, 0), (74, 22, 200, 1), (96, 30, 176, 2), (124, 24, 158, 3), (150, 34, 140, 4), (182, 24, 190, 1),
              (204, 26, 168, 2), (228, 20, 208, 0), (246, 28, 186, 3), (272, 22, 226, 1), (294, 30, 244, 0), (30, 18, 246, 2), (318, 24, 262, 1)]
    for i, (cx_, w, top, sty) in enumerate(sorted(towers, key=lambda t: -t[2])):
        x0, x1 = cx_ - w / 2, cx_ + w / 2
        bot = 304
        if sty == 4:     # tall dark tower with stepped shoulders
            shape = [(x0, bot), (x0, top + 24), (x0 + 6, top + 24), (x0 + 6, top + 8), (x0 + 12, top + 8), (x0 + 12, top), (x1 - 8, top), (x1 - 8, top + 12), (x1, top + 12), (x1, bot)]
            col = "#2A2850"
        elif sty == 3:   # slanted crown
            shape = [(x0, bot), (x0, top + 14), (x1, top), (x1, bot)]
            col = "#3A3A6A"
        elif sty == 2:   # pyramid cap
            shape = [(x0, bot), (x0, top + 10), (cx_, top - 6), (x1, top + 10), (x1, bot)]
            col = "#45466E"
        elif sty == 1:
            shape = [(x0, bot), (x0, top), (x1, top), (x1, bot)]
            col = "#4E4E7A"
        else:
            shape = [(x0, bot), (x0, top + 4), (x0 + 3, top), (x1 - 3, top), (x1, top + 4), (x1, bot)]
            col = "#3E4272"
        out.append(poly(shape, col))
        out.append(poly([(cx_ + w * 0.15, bot), (cx_ + w * 0.15, top + 12), (x1, top + 12 - (12 if sty in (1, 0) else 0)), (x1, bot)], "#1A1A3A", ' opacity="0.35"'))
        out.append(f'<line x1="{x0 + 0.8:.1f}" y1="{top + 14:.1f}" x2="{x0 + 0.8:.1f}" y2="{bot:.1f}" stroke="#F0B0C0" stroke-width="1.4" opacity="0.55"/>')
        rw = random.Random(i * 5 + 1)
        for yy in range(int(top + 14), bot - 2, 5):
            for j in range(int((w - 4) / 4)):
                if rw.random() < 0.4:
                    out.append(f'<rect x="{x0 + 2.5 + j * 4:.1f}" y="{yy}" width="2.2" height="2.4" fill="{rw.choice(["#FFD98E", "#FFE8B0", "#F7C873", "#E8F0FF"])}" opacity="{rw.uniform(0.6, 1):.2f}"/>')
        if top < 200:
            out.append(f'<circle cx="{cx_:.1f}" cy="{top - (6 if sty == 2 else 2):.1f}" r="1.6" fill="#FF6A6A"/>')
    # waterfront below the towers: piers, warehouses, a big wheel-free strip of lights
    out.append('<rect x="-10" y="298" width="360" height="8" fill="#22224A"/>')
    out.append(dots(90, 9, (0, 299, 350, 305), "#FFD98E", r=(0.6, 1.4), opacity=(0.5, 1)))
    # evergreen bluff on the right edge (West Seattle side), dark against the haze
    pl, bl = ridge_poly([(560, 304), (580, 268), (596, 252), (612, 248)], 41, base=310, amp=3, fill="#262A4E")
    out.append(pl)
    rt = random.Random(41)
    for _ in range(14):
        x = rt.uniform(556, 612)
        y = (y_on(bl, x) or 300) + 6
        out.append(conifer(x, y, rt.uniform(18, 34), rt.choice(["#22264A", "#262A50"]), rt.random()))

    # --- Elliott Bay
    out.append(f'<rect x="-10" y="303" width="620" height="141" fill="url(#{u}-bay)"/>')
    # Rainier's pink reflection, broken by ripples
    rr2 = random.Random(23)
    refl = []
    for _ in range(140):
        y = rr2.uniform(306, 372)
        d = y - 303
        half = max(0, 150 - d * 1.6)
        if half < 4:
            continue
        x = rr2.uniform(470 - half, 470 + half)
        refl.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{rr2.uniform(8, 30):.1f}" height="1.6" fill="{rr2.choice(["#F8C8D0", "#F2B4C4", "#FFE0E0"])}" opacity="{rr2.uniform(0.25, 0.6) * (1 - d / 80):.2f}"/>')
    out.append("".join(refl))
    out.append(reflect_streaks(11, list(range(26, 330, 7)), 307, 360, ["#FFD98E", "#F7C873", "#FFF0C8"], w=(2, 5), op=(0.25, 0.7), step=(4, 8)))
    out.append(ripples(160, 12, (-10, 310, 610, 440), ["#9A8AC0", "#C8A0C0", "#4A4C84"], w=(6, 24), h=(1, 1.8), opacity=(0.25, 0.6), persp=(303, 444)))
    # a sailboat heading home under the mountain
    out.append('<path d="M 380 318 L 400 318 L 397 322 L 383 322 Z" fill="#2A2850"/><path d="M 390 317 L 390 290 L 401 315 Z" fill="#F8E4E8"/><path d="M 389 317 L 389 294 L 381 316 Z" fill="#E8C8D4"/>')
    out.append('<path d="M 386 324 h 14" stroke="#F8D0D8" stroke-width="1.2" opacity="0.6"/>')

    # --- the ferry crossing, with its wake and reflection
    fx, fy, fs = 322, 374, 1.04
    wake = []
    for k, (dy, sw, op) in enumerate(((0, 3.2, 0.75), (5, 2.2, 0.5), (11, 1.8, 0.35), (-3, 1.6, 0.5))):
        wake.append(f'<path d="M {fx + 112} {fy - 2 + dy * 0.3} Q {fx + 190} {fy + dy} {fx + 320} {fy + dy * 2.4 + 6}" stroke="#FFF2F2" stroke-width="{sw}" fill="none" opacity="{op}" stroke-linecap="round"/>')
    out.append("".join(wake))
    out.append(blobs(40, 14, (fx + 108, fy - 4, fx + 200, fy + 8), ["#FFFFFF", "#F8E0E8"], r=(1.5, 4), opacity=(0.4, 0.9), squash=0.5))
    out.append(f'<rect x="{fx - 112}" y="{fy}" width="226" height="16" fill="#1A1E44" opacity="0.45"/>')
    out.append(reflect_streaks(15, list(range(fx - 92, fx + 92, 7)), fy + 4, fy + 40, ["#FFD98E", "#F7C873"], w=(2, 5), op=(0.3, 0.75), step=(3, 6)))
    out.append(reflect_streaks(16, list(range(fx - 108, fx + 108, 10)), fy + 2, fy + 18, ["#F8E8EC"], w=(4, 8), op=(0.25, 0.5), step=(3, 5)))
    out.append(wsf_ferry(fx, fy, fs, u))
    # gulls trailing the ferry, wheeling over the bay
    out.append(gulls([(372, 262, 10), (396, 252, 7), (346, 246, 6), (420, 270, 8)], "#F8ECF0", 2))
    out.append(gulls([(150, 104, 11), (172, 96, 7)], "#2A2650", 2))

    # --- foreground: the end of an old timber pier, lamps, pilings, a gull keeping watch
    # pier deck receding from the lower-left corner
    deck = [(-10, 400), (200, 404), (214, 412), (214, 444), (-10, 444)]
    out.append(poly(deck, f"url(#{u}-pier)"))
    out.append('<path d="M -10 400 L 200 404 L 214 412" stroke="#E8A8B4" stroke-width="1.6" fill="none" opacity="0.6"/>')
    out.append('<g stroke="#1A1424" stroke-width="1" opacity="0.6">' + "".join(f'<line x1="{x}" y1="{400 + x * 0.019:.1f}" x2="{x + 4}" y2="444"/>' for x in range(0, 210, 12)) + "</g>")
    # railing
    rail_y = lambda x: 400 + x * 0.019 - 26
    out.append(f'<path d="M -10 {rail_y(-10):.1f} L 204 {rail_y(204):.1f}" stroke="#141626" stroke-width="3.4"/>')
    out.append(f'<path d="M -10 {rail_y(-10) - 1.4:.1f} L 204 {rail_y(204) - 1.4:.1f}" stroke="#F0A8B4" stroke-width="1" opacity="0.6"/>')
    out.append(f'<path d="M -10 {rail_y(-10) + 12:.1f} L 204 {rail_y(204) + 12:.1f}" stroke="#141626" stroke-width="1.8"/>')
    out.append('<g stroke="#141626" stroke-width="2.4">' + "".join(f'<line x1="{x}" y1="{rail_y(x):.1f}" x2="{x}" y2="{rail_y(x) + 26:.1f}"/>' for x in range(4, 210, 20)) + "</g>")
    # big pilings under the pier end, with their dark reflections
    out.append('<rect x="200" y="404" width="16" height="40" fill="#1E1626"/><rect x="200" y="404" width="16" height="5" fill="#3A2C3E"/>')
    for x, top, w in ((218, 398, 10), (232, 404, 9)):
        out.append(f'<path d="M {x} {top + 2} Q {x + w / 2} {top - 2} {x + w} {top + 2} L {x + w} 444 L {x} 444 Z" fill="#1E1830"/><rect x="{x}" y="{top + 2}" width="2" height="{442 - top}" fill="#E8A0A8" opacity="0.45"/>')
    # lamps along the pier, warm pools of light on the deck
    for k, (x, h) in enumerate(((72, 104), (176, 92))):
        b = 400 + x * 0.019
        out.append(f'<ellipse cx="{x}" cy="{b + 6:.1f}" rx="44" ry="6" fill="#FFD098" opacity="0.28"/>')
        out.append(lamp_post(x, b, h, u, k))
    # two people leaning on the rail, watching the boat
    out.append(figure(118, 402, 44, "#3A3460", rim="#F0A8B4", pose="lean_back", light=1, seed=401, pal={"season": "winter", "form": "m"}, tint=("#2A2448", 0.25)))
    out.append(figure(136, 403, 41, "#7A3A5A", rim="#F0A8B4", pose="lean_back", light=1, seed=402, pal={"season": "winter", "form": "f", "hair_style": "long"}, tint=("#2A2448", 0.25)))
    # lone pilings out in the water on the right, a gull standing on the tallest
    for x, top, w in ((474, 384, 11), (494, 396, 10), (512, 390, 10), (534, 402, 9)):
        out.append(f'<path d="M {x} {top + 2} Q {x + w / 2} {top - 2} {x + w} {top + 2} L {x + w} 444 L {x} 444 Z" fill="#1E1830"/>'
                   f'<rect x="{x}" y="{top + 2}" width="2.2" height="{442 - top}" fill="#E8A0A8" opacity="0.45"/>'
                   f'<path d="M {x - 3} 438 h {w + 6}" stroke="#F0B8C0" stroke-width="1.4" opacity="0.5"/>')
    out.append(perched_gull(478, 384, 1.25))
    return "\n".join(out)



# ---------------------------------------------------------------- Boston (Acorn Street, Beacon Hill, in autumn)
def leaf_scatter(n, seed, box, cols, s=(2.5, 5), opacity=(0.7, 1)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        k = rnd.uniform(*s) * (0.5 + 0.8 * (y - y0) / max(1, y1 - y0))
        a = rnd.uniform(0, 180)
        out.append(f'<path d="M {-k:.1f} 0 Q 0 {-k * 0.7:.1f} {k:.1f} 0 Q 0 {k * 0.7:.1f} {-k:.1f} 0 Z" transform="translate({x:.1f} {y:.1f}) rotate({a:.0f})" fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*opacity):.2f}"/>')
    return "".join(out)


def foliage(cx, cy, r, seed, dark, mid, light, light_dir=(-0.5, -0.8), n=None, squash=0.85):
    """Painterly tree crown: a dark core, mid-tone dabs, then lit dabs on the side facing the light."""
    rnd = random.Random(seed)
    n = n or int(60 + r * 4)
    out = []
    for layer, cols, k, bias in ((0, dark, 1.0, 0.0), (1, mid, 0.9, 0.25), (2, light, 0.75, 0.55)):
        groups = {c: [] for c in cols}
        for _ in range(n if layer < 2 else n // 2):
            a = rnd.uniform(0, 2 * math.pi)
            d = r * k * math.sqrt(rnd.random())
            x = cx + d * math.cos(a) + light_dir[0] * r * bias
            y = cy + d * math.sin(a) * squash + light_dir[1] * r * bias * squash
            rr = r * rnd.uniform(0.05, 0.12)
            groups[rnd.choice(cols)].append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rr:.1f}" ry="{rr * 0.8:.1f}"/>')
        out += [f'<g fill="{c}">' + "".join(v) + "</g>" for c, v in groups.items() if v]
    return "".join(out)


def ivy(box, seed, sz, cols=("#C8402A", "#E86A2E", "#9A2A24", "#F2A040", "#6E2A22"), base="#7A2620", density=1.6):
    """Dense mat of Boston ivy: a dark base of overlapping dabs, then many small leaves on top."""
    x0, y0, x1, y1 = box
    area = max(1, (x1 - x0) * (y1 - y0))
    n = int(area / (sz * sz) * density)
    return (blobs(max(6, n // 6), seed, box, [base, "#8E3024"], r=(sz * 1.2, sz * 2.4), opacity=(0.9, 1), squash=0.7)
            + leaf_scatter(n, seed + 1, box, list(cols), s=(sz * 0.7, sz * 1.15), opacity=(0.9, 1)))


def boston():
    u = "bo"
    C = Cam(f=235, cx=306, vpy=222, eye=1.6)
    g = lambda Z: -0.075 * max(0, Z - 3)          # the lane drops away downhill
    XL, XR = -2.7, 2.5
    def Q(X, Z0, Z1, Y0, Y1, rel=True):
        """Facade rectangle in plane X; Y relative to the sloping ground under each edge when rel."""
        b0, b1 = (g(Z0), g(Z1)) if rel else (0, 0)
        return [C(X, b0 + Y0, Z0), C(X, b0 + Y1, Z0), C(X, b1 + Y1, Z1), C(X, b1 + Y0, Z1)]
    def QF(X, Z0, Z1, Y0, Y1, base):
        """Rectangle on a building whose floor levels are flat (base = ground at its downhill... uphill start)."""
        return [C(X, base + Y0, Z0), C(X, base + Y1, Z0), C(X, base + Y1, Z1), C(X, base + Y0, Z1)]
    def joints(X, z0, z1, y0, y1, base_fn, row=0.3, brick=0.62, zmax=16):
        """Staggered vertical mortar joints so near walls read as brick, not siding."""
        res = []
        z1c = min(z1, zmax)
        if z0 >= z1c:
            return ""
        rr_ = random.Random(int(z0 * 10 + X))
        for i in range(int((y1 - y0) / row)):
            yy = y0 + i * row
            z = z0 + (brick / 2 if i % 2 else 0) + rr_.uniform(0, 0.05)
            while z < z1c:
                a_, b_ = C(X, base_fn(z) + yy, z), C(X, base_fn(z) + yy + row, z)
                res.append(f"M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f}")
                z += brick
        return f'<path d="{" ".join(res)}" stroke="#5A2A22" stroke-opacity="0.3" stroke-width="1" fill="none"/>'
    out = [defs(
        lg(f"{u}-sky", [(0, "#6E9CCB"), (0.5, "#B8C8D8"), (0.85, "#F4D6A8"), (1, "#FCE2B0")]),
        lg(f"{u}-sun", [(0, "#FFF2C8", 0.0), (1, "#FFD890", 0.5)], 0, 0, 0, 1),
        lg(f"{u}-brickL", [(0, "#7A3A2E"), (1, "#B05A40")], 0, 0, 1, 0),
        lg(f"{u}-brickR", [(0, "#C4704E"), (1, "#8A4232")], 0, 0, 1, 0),
        lg(f"{u}-lane", [(0, "#C8A884"), (0.4, "#8A7464"), (1, "#4A3E3A")], 0, 222, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-shade", [(0, "#2A1E2A", 0.45), (0.5, "#2A1E2A", 0.15), (1, "#2A1E2A", 0)], 0, 0, 1, 0),
        lg(f"{u}-glass", [(0, "#2E3442"), (0.6, "#5A6478"), (1, "#2A2E3A")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(312, 226, 200, "#FFE8B0", f"{u}-glow", 0.9))
    # the far end: across West Cedar Street, a sunlit brick house and a blazing maple
    zf = 64
    out.append(poly(QF(-14, zf, zf, 0, 0, 0)[:0] + [C(-10, g(zf) - 0.5, zf), C(-10, g(zf) + 11, zf), C(10, g(zf) + 11, zf), C(10, g(zf) - 0.5, zf)], "#D49068"))
    rw = random.Random(1)
    for i in range(4):
        for j in range(3):
            a_, b_ = C(-6 + i * 3.6, g(zf) + 2.4 + j * 3, zf), C(-6 + i * 3.6 + 1.3, g(zf) + 4.2 + j * 3, zf)
            out.append(f'<rect x="{a_[0]:.1f}" y="{b_[1]:.1f}" width="{b_[0] - a_[0]:.1f}" height="{a_[1] - b_[1]:.1f}" fill="#5A4A50"/>')
    mx, my = C(1.8, g(zf) + 6, zf - 4)
    out.append(foliage(mx, my - 12, 22, 3, ["#B8502A", "#C8602A"], ["#E8782A", "#F2A030"], ["#FFD060", "#FFE890"], light_dir=(0, -0.6)))
    out.append(f'<rect x="{mx - 1.5:.1f}" y="{my:.1f}" width="3" height="{C(0, g(zf - 4), zf - 4)[1] - my:.1f}" fill="#4A3028"/>')
    out.append(f'<rect x="0" y="150" width="600" height="110" fill="url(#{u}-sun)"/>')
    # the lane: rounded river-stone cobbles running downhill
    out.append(poly([C(XL + 1.0, g(70), 70), C(XR, g(70), 70), C(XR, g(1.6), 1.6), C(XL + 1.0, g(1.6), 1.6)], f"url(#{u}-lane)"))
    rc = random.Random(11)
    cob = []
    z = 1.7
    while z < 62:
        dz = 0.17 * (z / 2) ** 0.3
        X = XL + 1.0 + rc.uniform(0, 0.1)
        while X < XR:
            w = rc.uniform(0.15, 0.24) * (z / 2) ** 0.3
            p0, p1 = C(X + 0.02, g(z), z + 0.02), C(X + w - 0.02, g(z + dz), z + dz - 0.02)
            if -5 < p1[0] and p0[0] < 605 and p0[1] < 450:
                x0_, x1_, y0_, y1_ = p0[0], p1[0], p1[1], p0[1]
                hgt = y1_ - y0_
                lit = 1 - min(1, z / 50)
                cob.append(f'<ellipse cx="{(x0_ + x1_) / 2:.1f}" cy="{(y0_ + y1_) / 2:.1f}" rx="{abs(x1_ - x0_) / 2:.1f}" ry="{hgt / 2:.1f}" fill="{rc.choice(["#7A6A60", "#8E7A6A", "#6A5A52", "#9A8676", "#5E504A"])}"/>')
                if hgt > 2.5:
                    cob.append(f'<ellipse cx="{(x0_ + x1_) / 2:.1f}" cy="{y0_ + hgt * 0.32:.1f}" rx="{abs(x1_ - x0_) * 0.3:.1f}" ry="{hgt * 0.16:.1f}" fill="#FFE6B8" opacity="{0.25 + 0.3 * (1 - lit):.2f}"/>')
            X += w
        z += dz
    out.append("".join(cob))
    # brick sidewalk along the left houses
    out.append(poly([C(XL, g(70), 70), C(XL + 1.0, g(70) + 0.12, 70), C(XL + 1.0, g(1.6) + 0.12, 1.6), C(XL, g(1.6), 1.6)], "#9A5A44"))
    out.append(poly([C(XL + 1.0, g(70) + 0.12, 70), C(XL + 1.0, g(70), 70), C(XL + 1.0, g(1.6), 1.6), C(XL + 1.0, g(1.6) + 0.12, 1.6)], "#C8B8A4"))
    # ---- left: Federal rowhouses stepping down the hill
    houses = [(1.0, 7.4, 12.5, "#9A4634"), (7.4, 13.6, 12.0, "#A8523C"), (13.6, 19.6, 12.6, "#8E3E30"), (19.6, 25.4, 11.8, "#B05C44"),
              (25.4, 31.4, 12.2, "#94443A"), (31.4, 37.6, 11.6, "#A44E3A"), (37.6, 44, 12.0, "#8A4034"), (44, 52, 11.4, "#A85A44"), (52, 62, 11.8, "#94483A")]
    lamps = []
    for k, (z0, z1, h, col) in enumerate(reversed(houses)):
        base = g(z0)
        face = QF(XL, z0, z1, g(z1) - base - 0.3, h, base)
        out.append(poly(face, col))
        zm = (z0 + z1) / 2
        sw = max(0.5, C.f * 0.03 / zm)
        # brick courses
        out.append(f'<g stroke="#5A2A22" stroke-opacity="0.35" stroke-width="{sw:.1f}">' + "".join(
            f'<line x1="{C(XL, base + y, z0)[0]:.1f}" y1="{C(XL, base + y, z0)[1]:.1f}" x2="{C(XL, base + y, z1)[0]:.1f}" y2="{C(XL, base + y, z1)[1]:.1f}"/>'
            for y in [0.32 * i for i in range(int(h / 0.32))]) + "</g>")
        rb = random.Random(k * 17)
        out.append(joints(XL, z0, z1, 0, h, lambda z, b=base: b))
        out.append(blobs(int(40 * 10 / zm) + 6, k, (min(p[0] for p in face), min(p[1] for p in face), max(p[0] for p in face), max(p[1] for p in face)),
                         ["#C86A50", "#6A2E24", "#B8604A"], r=(0.6, 2.2 * 10 / zm + 0.5), opacity=(0.2, 0.45), squash=0.4))
        # cornice
        out.append(poly(QF(XL, z0, z1, h - 0.5, h, base), "#E8E0D2"))
        out.append(poly(QF(XL, z0, z1, h - 0.8, h - 0.5, base), "#000", ' opacity="0.25"'))
        # granite stoop + black door with fanlight and white surround (on the uphill side)
        dz0, dz1 = z0 + 0.6, z0 + 1.7
        out.append(poly(QF(XL + 0.02, dz0 - 0.25, dz1 + 0.25, 0.3, 2.9, base), "#EFE8DA"))
        out.append(poly(QF(XL + 0.03, dz0, dz1, 0.3, 2.35, base), "#16161C"))
        out.append(poly(QF(XL + 0.03, dz0, dz1, 2.42, 2.82, base), "#F0C878"))
        kx, ky = C(XL + 0.04, base + 1.5, (dz0 + dz1) / 2)
        out.append(f'<circle cx="{kx:.1f}" cy="{ky:.1f}" r="{max(0.6, C.f * 0.06 / zm):.1f}" fill="#E8C060"/>')
        for st in range(2):
            out.append(poly([C(XL, base + 0.15 * st, dz0 - 0.3), C(XL, base + 0.15 * st, dz1 + 0.3), C(XL + 0.5 - st * 0.2, base + 0.15 * st, dz1 + 0.3), C(XL + 0.5 - st * 0.2, base + 0.15 * st, dz0 - 0.3)], "#C8C0B4"))
            out.append(poly([C(XL + 0.5 - st * 0.2, base + 0.15 * st, dz0 - 0.3), C(XL + 0.5 - st * 0.2, base + 0.15 * (st + 1), dz0 - 0.3), C(XL + 0.5 - st * 0.2, base + 0.15 * (st + 1), dz1 + 0.3), C(XL + 0.5 - st * 0.2, base + 0.15 * st, dz1 + 0.3)], "#A8A094"))
        # 6-over-6 windows with black shutters on three floors
        for fy0, fy1 in ((0.9, 2.6), (3.9, 6.0), (7.2, 9.2), (10.0, 11.4)):
            for wz0 in (z0 + 2.4, z0 + 4.4) if fy0 < 1 else (z0 + 0.8, z0 + 2.6, z0 + 4.4):
                wz1 = wz0 + 1.0
                if wz1 > z1 - 0.3:
                    continue
                out.append(poly(QF(XL + 0.01, wz0 - 0.08, wz1 + 0.08, fy0 - 0.12, fy1 + 0.1, base), "#F2EEE6"))
                out.append(poly(QF(XL + 0.02, wz0, wz1, fy0, fy1, base), f"url(#{u}-glass)"))
                if zm < 30:
                    mz = (wz0 + wz1) / 2
                    a_, b_ = C(XL + 0.02, base + fy0, mz), C(XL + 0.02, base + fy1, mz)
                    out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#F2EEE6" stroke-width="{sw:.1f}"/>')
                    a_, b_ = C(XL + 0.02, base + (fy0 + fy1) / 2, wz0), C(XL + 0.02, base + (fy0 + fy1) / 2, wz1)
                    out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#F2EEE6" stroke-width="{sw * 1.4:.1f}"/>')
                for s0, s1 in ((wz0 - 0.5, wz0 - 0.08), (wz1 + 0.08, wz1 + 0.5)):
                    out.append(poly(QF(XL + 0.03, s0, s1, fy0, fy1, base), "#1E1E22"))
                if fy0 < 4.5 and rb.random() < 0.7:     # window box: mums and trailing ivy
                    out.append(poly(QF(XL + 0.25, wz0 - 0.1, wz1 + 0.1, fy0 - 0.45, fy0 - 0.08, base), "#2A2A2E"))
                    p0, p1 = C(XL + 0.25, base + fy0 + 0.2, wz0 - 0.1), C(XL + 0.25, base + fy0 - 0.1, wz1 + 0.1)
                    out.append(blobs(12, k * 7 + int(fy0), (min(p0[0], p1[0]), p0[1], max(p0[0], p1[0]), p1[1]), ["#E8782A", "#F2A030", "#C8402A", "#FFD25A"],
                                     r=(C.f * 0.07 / zm, C.f * 0.14 / zm), opacity=(0.95, 1), squash=0.85))
        # party wall line, then the gas lamp on its bracket
        out.append(poly(QF(XL, z0, z0 + 0.15, g(z1) - base - 0.3, h, base), "#000", ' opacity="0.25"'))
        lamps.append((z0 + 2.0, base))
    # Boston ivy turned crimson, climbing the first houses
    for z0, z1, y0, y1, sd in ((13.6, 15.4, 0, 8, 2), (31.4, 33.0, 0, 6, 3)):
        p0, p1 = C(XL, g(z0) + y1, z0), C(XL, g(z1) + y0, z1)
        out.append(ivy((min(p0[0], p1[0]), p0[1], max(p0[0], p1[0]), p1[1]), sd, max(1.6, C.f * 0.1 / z0)))
    out.append(poly([C(XL, -0.2, 1), C(XL, 14, 1), C(XL, 14, 70), C(XL, g(70) - 0.2, 70)], f"url(#{u}-shade)"))
    for z, base in lamps:
        x, y = C(XL + 0.45, base + 3.3, z)
        s = C.f / z
        out.append(glow(x, y, s * 1.2, "#FFD488", f"{u}-gl{int(z * 10)}", 0.7))
        a_ = C(XL, base + 3.0, z)
        out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} Q {x:.1f} {a_[1]:.1f} {x:.1f} {y - s * 0.28:.1f}" fill="none" stroke="#141418" stroke-width="{max(0.6, s * 0.05):.1f}"/>')
        out.append(f'<path d="M {x - s * 0.15:.1f} {y - s * 0.26:.1f} L {x + s * 0.15:.1f} {y - s * 0.26:.1f} L {x + s * 0.11:.1f} {y + s * 0.2:.1f} L {x - s * 0.11:.1f} {y + s * 0.2:.1f} Z" fill="#FFE8A8" stroke="#141418" stroke-width="{max(0.5, s * 0.035):.1f}"/>')
        out.append(f'<path d="M {x - s * 0.2:.1f} {y - s * 0.26:.1f} L {x:.1f} {y - s * 0.42:.1f} L {x + s * 0.2:.1f} {y - s * 0.26:.1f} Z" fill="#141418"/>')
    # ---- right: high garden walls with doors, trees leaning over, then houses further down
    segs = [(1.0, 9.0, "wall"), (9.0, 15.0, "house"), (15.0, 24.0, "wall"), (24.0, 30.0, "house"), (30.0, 40.0, "wall"), (40.0, 62.0, "house")]
    for k, (z0, z1, kind) in enumerate(reversed(segs)):
        base = g(z0)
        zm = (z0 + z1) / 2
        sw = max(0.5, C.f * 0.03 / zm)
        if kind == "wall":
            hh = 3.6
            out.append(poly(Q(XR, z0, z1, -0.3, hh), "#A85A42"))
            out.append(f'<g stroke="#5A2A22" stroke-opacity="0.3" stroke-width="{sw:.1f}">' + "".join(
                f'<line x1="{C(XR, g(z0) + y, z0)[0]:.1f}" y1="{C(XR, g(z0) + y, z0)[1]:.1f}" x2="{C(XR, g(z1) + y, z1)[0]:.1f}" y2="{C(XR, g(z1) + y, z1)[1]:.1f}"/>' for y in [0.3 * i for i in range(int(3.6 / 0.3))]) + "</g>")
            out.append(joints(XR, z0, z1, 0, hh, g))
            out.append(poly(Q(XR, z0, z1, hh - 0.2, hh), "#D8C8B4"))
            # arched garden door
            dz0 = z0 + (z1 - z0) * 0.45
            dz1 = dz0 + 1.1
            d = Q(XR - 0.02, dz0, dz1, 0, 2.5)
            out.append(poly(d, "#2E4A3A"))
            out.append(poly(Q(XR - 0.03, dz0 + 0.1, dz1 - 0.1, 0.2, 2.3), "#3E5E4A"))
            # trees in the gardens behind
            for t in range(2):
                tz = z0 + (z1 - z0) * (t + 0.5) / 2
                tx, ty = C(XR + 3.5, g(tz) + 7.5, tz + 2)
                r = C.f * 3.4 / (tz + 2)
                out.append(foliage(tx, ty, r, k * 9 + t, ["#9A4222", "#A8502A"], ["#E8862A", "#D86A28", "#F2A438"], ["#FFD060", "#FFE08A", "#F8C048"], light_dir=(-0.6, -0.6)))
            # ivy cascading over the coping
            p0, p1 = C(XR, g(z0) + hh + 0.3, z0), C(XR, g(z1) + hh - 1.8, z1)
            sz = max(1.6, C.f * 0.1 / (z0 + 3))
            # a cascade hanging from the coping: denser near the top
            top_pts = [C(XR, g(z) + hh + 0.2, z) for z in (z0, z1)]
            zs = max(z0, 5.0)
            for j in range(6):
                t = j / 6
                za, zb = zs + (z1 - zs) * t, zs + (z1 - zs) * (t + 0.14)
                drop = random.Random(k * 31 + j).uniform(0.3, 1.3)
                a_, b_ = C(XR, g(za) + hh + 0.15, za), C(XR, g(zb) + hh - drop, min(zb, z1))
                out.append(ivy((min(a_[0], b_[0]), min(a_[1], b_[1]), max(a_[0], b_[0]), max(a_[1], b_[1])), k * 50 + j, sz, cols=("#D8482E", "#E86A2E", "#F2A040", "#B8302A"), base="#A83A28", density=1.0))
        else:
            h = 12.0
            face = QF(XR, z0, z1, g(z1) - base - 0.3, h, base)
            out.append(poly(face, "#B86448"))
            out.append(f'<g stroke="#5A2A22" stroke-opacity="0.3" stroke-width="{sw:.1f}">' + "".join(
                f'<line x1="{C(XR, base + y, z0)[0]:.1f}" y1="{C(XR, base + y, z0)[1]:.1f}" x2="{C(XR, base + y, z1)[0]:.1f}" y2="{C(XR, base + y, z1)[1]:.1f}"/>' for y in [0.32 * i for i in range(int(12 / 0.32))]) + "</g>")
            out.append(poly(QF(XR, z0, z1, h - 0.5, h, base), "#E8E0D2"))
            for fy0, fy1 in ((1.0, 2.7), (3.9, 6.0), (7.2, 9.2), (10.0, 11.4)):
                wz = z0 + 0.7
                while wz + 1.0 < z1 - 0.4:
                    out.append(poly(QF(XR - 0.01, wz - 0.08, wz + 1.08, fy0 - 0.1, fy1 + 0.1, base), "#F2EEE6"))
                    out.append(poly(QF(XR - 0.02, wz, wz + 1.0, fy0, fy1, base), f"url(#{u}-glass)"))
                    wz += 2.0
            dz = z0 + 0.3
            out.append(poly(QF(XR - 0.03, dz, dz + 1.0, 0.2, 2.4, base), "#16161C"))
            out.append(poly(QF(XR, z0, z0 + 0.15, g(z1) - base - 0.3, h, base), "#000", ' opacity="0.2"'))
    # the low sun at the end of the lane gilds the right-hand wall tops
    out.append(poly([C(XR, -0.2, 1), C(XR, 14, 1), C(XR, 14, 70), C(XR, g(70) - 0.2, 70)], "#FFD890", ' opacity="0.08"'))
    # fallen leaves on the cobbles, a pumpkin on the stoop, a cat, a walker heading down the hill
    lane = [C(XL + 1.0, g(70), 70), C(XR, g(70), 70), C(XR, g(1.6), 1.6), C(XL + 1.0, g(1.6), 1.6)]
    out.append(f'<clipPath id="{u}-lc"><polygon points="{P(lane)}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-lc)">' + leaf_scatter(150, 4, (0, 300, 600, 444), ["#E8782A", "#F2A030", "#C8402A", "#FFC850", "#B8502A"], s=(2, 5))
               + leaf_scatter(70, 5, (200, 236, 440, 300), ["#E8782A", "#F2A030", "#C8402A"], s=(1, 2.2)) + "</g>")
    px, py = C(XL + 0.55, g(2.2) + 0.32, 2.4)
    out.append(f'<g transform="translate({px:.1f} {py:.1f})"><ellipse cx="0" cy="-14" rx="24" ry="17" fill="#E8742A"/><path d="M -10 -30 Q -16 -14 -10 2 M 0 -31 L 0 3 M 10 -30 Q 16 -14 10 2" stroke="#B8501E" stroke-width="2" fill="none"/>'
               '<ellipse cx="-8" cy="-20" rx="5" ry="8" fill="#FFA850" opacity="0.6"/><path d="M -1 -31 q 2 -8 6 -9" stroke="#4A5A2A" stroke-width="3.4" fill="none" stroke-linecap="round"/></g>')
    cx_, cy_ = C(XL + 0.6, g(8) + 0.32, 8.0)
    out.append(f'<g transform="translate({cx_:.1f} {cy_:.1f}) scale(0.9)"><path d="M -8 0 Q -10 -16 -2 -20 Q 6 -22 8 -12 Q 10 -4 8 0 Z" fill="#1E1A1E"/><circle cx="2" cy="-23" r="5.5" fill="#1E1A1E"/>'
               '<path d="M -2 -27 l -1 -6 l 4 4 Z M 5 -27 l 2 -6 l 1 5 Z" fill="#1E1A1E"/><path d="M 8 -2 q 10 0 8 -12" stroke="#1E1A1E" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
               '<circle cx="0.5" cy="-23.5" r="0.9" fill="#E8D060"/><circle cx="4" cy="-23.5" r="0.9" fill="#E8D060"/><path d="M -8 -2 Q -10 -14 -3 -19" stroke="#FFD890" stroke-width="1" fill="none" opacity="0.6"/></g>')
    for X, Z, h, c, sk in ((0.6, 26, 1.7, "#2E4A6A", False), (0.2, 44, 1.65, "#C86A4A", True)):
        x, b = C(X, g(Z), Z)
        out.append(f'<ellipse cx="{x:.1f}" cy="{b + 1:.1f}" rx="{C.f * 0.5 / Z:.1f}" ry="{C.f * 0.08 / Z:.1f}" fill="#2A1E1A" opacity="0.4"/>')
        out.append(figure(x, b, C.f * h / Z, c, skirt=sk, rim="#FFE0A0", pose="stand_back", light=1, seed=int(Z), pal={"season": "winter"}))
    dx_, dy_ = C(1.0, g(26.5), 26.5)
    out.append(f'<g transform="translate({dx_:.1f} {dy_:.1f}) scale({C.f / 26.5 / 40:.3f})"><ellipse cx="0" cy="-10" rx="12" ry="5" fill="#C8904A"/><circle cx="10" cy="-15" r="4.5" fill="#C8904A"/><path d="M -8 -6 l -1 6 M -4 -6 l 0 6 M 5 -6 l 0 6 M 8 -6 l 1 6" stroke="#8A5A2A" stroke-width="2"/></g>')
    # falling leaves caught mid-air in the light
    out.append(leaf_scatter(14, 9, (140, 150, 480, 300), ["#F2A030", "#FFC850", "#E8782A"], s=(2.5, 4)))
    return "\n".join(out)



# ---------------------------------------------------------------- Philadelphia (Independence Hall from the square)
def tree_crown(cx, cy, r, seed, dark, mid, light, light_dir=(-0.7, -0.5), branch="#4A3A2E", lobes=6):
    """Irregular broadleaf crown: several foliage clusters around a few visible limbs."""
    rnd = random.Random(seed)
    clusters = []
    for i in range(lobes):
        a = rnd.uniform(0, 2 * math.pi) if i else -math.pi / 2
        d = r * (rnd.uniform(0.25, 0.55) if i else 0.2)
        clusters.append((cx + d * math.cos(a), cy + d * math.sin(a) * 0.75, r * rnd.uniform(0.42, 0.62)))
    out = []
    for x, y, rr in clusters:     # limbs reaching into each cluster
        out.append(f'<path d="M {cx:.1f} {cy + r * 0.7:.1f} Q {(cx + x) / 2:.1f} {(cy + r * 0.7 + y) / 2 + rr * 0.3:.1f} {x:.1f} {y + rr * 0.2:.1f}" stroke="{branch}" stroke-width="{max(1.2, r * 0.035):.1f}" fill="none" stroke-linecap="round"/>')
    for k, (x, y, rr) in enumerate(sorted(clusters, key=lambda c: c[1])):
        out.append(foliage(x, y, rr, seed * 10 + k, dark, mid, light, light_dir=light_dir, squash=0.85, n=int(50 + rr * 3)))
    return "".join(out)


def philadelphia():
    u = "ph"
    C = Cam(f=262, cx=300, vpy=348, eye=1.6)
    ZB = 52.0                                  # facade plane (metres)
    def R(X0, X1, Y0, Y1, fill, Z=ZB, extra=""):
        return poly(C.quad_z(Z, X0, X1, Y0, Y1), fill, extra)
    def pt(X, Y, Z=ZB):
        return C(X, Y, Z)
    out = [defs(
        lg(f"{u}-sky", [(0, "#4A78B4"), (0.45, "#8AA8CC"), (0.75, "#E8C8A8"), (1, "#F8D49C")]),
        lg(f"{u}-brick", [(0, "#B4583E"), (1, "#9A4634")], 0, 0, 1, 0),
        lg(f"{u}-brickS", [(0, "#7A3A2E"), (1, "#5E2C24")], 0, 0, 1, 0),
        lg(f"{u}-white", [(0, "#FFFDF6"), (0.55, "#F2ECE0"), (1, "#C8BEB4")], 0, 0, 1, 0),
        lg(f"{u}-lawn", [(0, "#8AA848"), (1, "#4E7A30")], 0, 348, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-path", [(0, "#C88A6A"), (1, "#9A5A44")], 0, 348, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-glass", [(0, "#3A3E48"), (0.6, "#6A7484"), (1, "#3A3E48")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(40, 280, 300, "#FFD898", f"{u}-sun", 0.85))
    for x, y, w in ((470, 110, 90), (520, 124, 60), (150, 96, 70), (400, 150, 50)):
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="6" fill="#FFF4E0" opacity="0.55"/><ellipse cx="{x + 10}" cy="{y + 3}" rx="{w * 0.7:.0f}" ry="3.5" fill="#F8C8A0" opacity="0.6"/>')
    # distant city beyond, hazed
    for X0, X1, h in ((-60, -46, 40), (-44, -36, 28), (36, 48, 34), (50, 62, 46), (-34, -26, 22)):
        out.append(R(X0, X1, 0, h, "#B8C4D4", Z=200))
    # wings and the arcades that tie them to the main block
    for sgn in (-1, 1):
        X0, X1 = sorted((sgn * 16.3, sgn * 27))
        out.append(R(X0, X1, 0, 8.6, f"url(#{u}-brick)"))
        out.append(poly([pt(X0, 8.6), pt(X0 + 1.5, 11), pt(X1 - 1.5, 11), pt(X1, 8.6)], "#5A4E50"))
        out.append(R(X0, X1, 8.2, 8.6, "#F2ECE0"))
        for i in range(4):
            xx = X0 + 1.4 + i * 2.6
            for y0, y1 in ((1.2, 3.6), (5.0, 7.2)):
                out.append(R(xx - 0.06, xx + 1.26, y0 - 0.1, y1 + 0.1, "#F2ECE0"))
                out.append(R(xx, xx + 1.2, y0, y1, f"url(#{u}-glass)"))
    # main block
    out.append(R(-16.3, 16.3, 0, 12.2, f"url(#{u}-brick)"))
    rb = random.Random(3)
    a_, b_ = pt(-16.3, 0), pt(16.3, 12.2)
    out.append(f'<g stroke="#6A2E24" stroke-opacity="0.28" stroke-width="0.8">' + "".join(
        f'<line x1="{a_[0]:.1f}" y1="{y:.1f}" x2="{b_[0]:.1f}" y2="{y:.1f}"/>' for y in range(int(b_[1]) + 2, int(a_[1]), 3)) + "</g>")
    out.append(dots(260, 4, (a_[0], b_[1], b_[0], a_[1]), "#D88A6A", r=(0.5, 1.2), opacity=(0.2, 0.5)))
    # roof with its balustraded deck and the end chimneys
    out.append(poly([pt(-16.6, 12.2), pt(-13.4, 16.2), pt(13.4, 16.2), pt(16.6, 12.2)], "#4E4448"))
    out.append(poly([pt(-16.6, 12.2), pt(-13.4, 16.2), pt(-12.4, 16.2), pt(-15.2, 12.2)], "#6A5E62"))
    out.append(R(-16.7, 16.7, 11.7, 12.4, "#F6F0E4"))
    out.append(R(-16.7, 16.7, 11.4, 11.7, "#000", extra=' opacity="0.18"'))
    out.append(R(-13, 13, 16.2, 16.5, "#F6F0E4"))
    out.append(R(-13, 13, 17.4, 17.7, "#F6F0E4"))
    bx0, by0 = pt(-13, 16.5)
    bx1, by1 = pt(13, 17.4)
    out.append(f'<g stroke="#F6F0E4" stroke-width="1.4">' + "".join(f'<line x1="{x:.1f}" y1="{by0:.1f}" x2="{x:.1f}" y2="{by1:.1f}"/>' for x in [bx0 + i * 3.2 for i in range(int((bx1 - bx0) / 3.2) + 1)]) + "</g>")
    for sgn in (-1, 1):
        X0, X1 = sorted((sgn * 15.0, sgn * 12.6))
        out.append(R(X0, X1, 12.2, 20.2, f"url(#{u}-brick)"))
        out.append(R(X0 - 0.2, X1 + 0.2, 19.6, 20.2, "#F2ECE0"))
        out.append(R(X0 + 1.2 if sgn < 0 else X0, X1 if sgn < 0 else X1 - 1.2, 12.2, 20.2, "#000", extra=' opacity="0.15"'))
    # windows: tall sashes with white frames, marble keystones and panels
    for sgn in (-1, 1):
        for X in (6.2, 8.9, 11.6, 14.3):
            xc = sgn * X
            for y0, y1 in ((1.4, 4.9), (6.9, 10.3)):
                out.append(R(xc - 0.86, xc + 0.86, y0 - 0.14, y1 + 0.12, "#F6F0E4"))
                out.append(R(xc - 0.72, xc + 0.72, y0, y1, f"url(#{u}-glass)"))
                m0, m1 = pt(xc, y0), pt(xc, y1)
                out.append(f'<line x1="{m0[0]:.1f}" y1="{m0[1]:.1f}" x2="{m1[0]:.1f}" y2="{m1[1]:.1f}" stroke="#F6F0E4" stroke-width="0.9"/>')
                for t in (0.33, 0.5, 0.67):
                    l0, l1 = pt(xc - 0.72, y0 + (y1 - y0) * t), pt(xc + 0.72, y0 + (y1 - y0) * t)
                    out.append(f'<line x1="{l0[0]:.1f}" y1="{l0[1]:.1f}" x2="{l1[0]:.1f}" y2="{l1[1]:.1f}" stroke="#F6F0E4" stroke-width="{1.3 if t == 0.5 else 0.7}"/>')
                k0, k1 = pt(xc - 0.3, y1 + 0.12), pt(xc + 0.3, y1 + 0.75)
                out.append(f'<polygon points="{P([(k0[0], k0[1]), (k1[0], k0[1]), (k1[0] + 1.2, k1[1]), (k0[0] - 1.2, k1[1])])}" fill="#F6F0E4"/>')
            out.append(R(xc - 0.86, xc + 0.86, 5.3, 6.4, "#EDE4D4"))
    out.append(R(-16.3, 16.3, 5.0, 5.35, "#F6F0E4"))
    out.append(R(-16.3, 16.3, 0, 0.9, "#8A7E74"))
    # the tower, projecting forward, its right side in shade
    ZT = ZB - 2.0
    out.append(poly([pt(4.6, 0, ZT), pt(4.6, 26, ZT), pt(4.6, 26, ZB), pt(4.6, 0, ZB)], f"url(#{u}-brickS)"))
    out.append(R(-4.6, 4.6, 0, 26, f"url(#{u}-brick)", Z=ZT))
    a_, b_ = pt(-4.6, 0, ZT), pt(4.6, 26, ZT)
    out.append(f'<g stroke="#6A2E24" stroke-opacity="0.28" stroke-width="0.8">' + "".join(
        f'<line x1="{a_[0]:.1f}" y1="{y:.1f}" x2="{b_[0]:.1f}" y2="{y:.1f}"/>' for y in range(int(b_[1]) + 2, int(a_[1]), 3)) + "</g>")
    out.append(dots(160, 5, (a_[0], b_[1], b_[0], a_[1]), "#D88A6A", r=(0.5, 1.2), opacity=(0.2, 0.5)))
    for Y0, Y1 in ((0, 0.9), (5.0, 5.35), (11.7, 12.4), (19.4, 19.8), (25.4, 26.2)):
        out.append(R(-4.7, 4.7, Y0, Y1, "#F6F0E4" if Y0 > 0 else "#8A7E74", Z=ZT))
    def arch(xc, y0, y1, hw, fill, Z, frame=None):
        a0, a1 = pt(xc - hw, y0, Z), pt(xc + hw, y1, Z)
        r = (a1[0] - a0[0]) / 2
        d = f'M {a0[0]:.1f} {a0[1]:.1f} L {a0[0]:.1f} {a1[1] + r:.1f} A {r:.1f} {r:.1f} 0 0 1 {a1[0]:.1f} {a1[1] + r:.1f} L {a1[0]:.1f} {a0[1]:.1f} Z'
        return (f'<path d="{d}" fill="{frame}" transform="translate({(a0[0] + a1[0]) / 2:.1f} {a0[1]:.1f}) scale(1.16 1.05) translate({-(a0[0] + a1[0]) / 2:.1f} {-a0[1]:.1f})"/>' if frame else "") + f'<path d="{d}" fill="{fill}"/>'
    out.append(arch(0, 0.9, 4.6, 1.25, "#3A2A26", ZT, "#F6F0E4"))
    out.append(arch(0, 1.0, 3.4, 0.95, "#5A3E34", ZT))
    out.append(arch(0, 6.6, 11.0, 0.95, f"url(#{u}-glass)", ZT, "#F6F0E4"))
    for sx in (-1.75, 1.75):
        out.append(R(sx - 0.55, sx + 0.55, 6.6, 9.6, "#F6F0E4", Z=ZT))
        out.append(R(sx - 0.42, sx + 0.42, 6.75, 9.45, f"url(#{u}-glass)", Z=ZT))
    out.append(arch(0, 13.4, 18.4, 1.0, f"url(#{u}-glass)", ZT, "#F6F0E4"))
    out.append(arch(0, 20.6, 24.4, 0.85, "#4A3A3A", ZT, "#F6F0E4"))
    # balustrade with urns on the tower top
    out.append(R(-4.8, 4.8, 26.2, 26.5, "#F6F0E4", Z=ZT))
    out.append(R(-4.8, 4.8, 27.3, 27.6, "#F6F0E4", Z=ZT))
    q0, q1 = pt(-4.6, 26.5, ZT), pt(4.6, 27.3, ZT)
    out.append(f'<g stroke="#F6F0E4" stroke-width="1.3">' + "".join(f'<line x1="{q0[0] + i * 2.6:.1f}" y1="{q0[1]:.1f}" x2="{q0[0] + i * 2.6:.1f}" y2="{q1[1]:.1f}"/>' for i in range(int((q1[0] - q0[0]) / 2.6) + 1)) + "</g>")
    for sx in (-4.5, 4.5):
        ux, uy = pt(sx, 28.4, ZT)
        out.append(f'<ellipse cx="{ux:.1f}" cy="{uy:.1f}" rx="2.4" ry="3.4" fill="#F6F0E4"/><rect x="{ux - 1:.1f}" y="{uy - 6:.1f}" width="2" height="3" fill="#F6F0E4"/>')
    # the white wooden steeple: clock stage, open belfry, lantern, dome and spire
    ZS = ZT + 1.0
    def stage(hw, Y0, Y1, shade_w=0.42):
        return (R(-hw, hw, Y0, Y1, f"url(#{u}-white)", Z=ZS))
    out.append(stage(3.5, 27.6, 33.4))
    for sx in (-3.1, 3.1):
        out.append(R(sx - 0.35, sx + 0.35, 27.6, 33.4, "#FFFFFF" if sx < 0 else "#B8AEA6", Z=ZS))
    out.append(R(-3.7, 3.7, 33.2, 33.8, "#FFFFFF", Z=ZS))
    cx_, cy_ = pt(0, 30.5, ZS)
    cr = C.f * 1.55 / ZS
    out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{cr + 1.6:.1f}" fill="#2A2A30"/><circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{cr:.1f}" fill="#FFFDF4"/>')
    out.append("".join(f'<circle cx="{cx_ + cr * 0.8 * math.cos(i * math.pi / 6):.1f}" cy="{cy_ + cr * 0.8 * math.sin(i * math.pi / 6):.1f}" r="0.7" fill="#2A2A30"/>' for i in range(12)))
    out.append(f'<path d="M {cx_:.1f} {cy_:.1f} L {cx_ + cr * 0.45:.1f} {cy_ + cr * 0.3:.1f} M {cx_:.1f} {cy_:.1f} L {cx_ - cr * 0.1:.1f} {cy_ - cr * 0.65:.1f}" stroke="#2A2A30" stroke-width="1.3" stroke-linecap="round"/>')
    out.append(stage(2.9, 33.8, 39.6))
    for i, xc in enumerate((-1.75, 0, 1.75)):
        out.append(arch(xc, 34.6, 38.6, 0.55, "#5A4E52" if i < 2 else "#3E3438", ZS))
    for xc in (-2.6, -0.9, 0.9, 2.6):
        out.append(R(xc - 0.18, xc + 0.18, 34.0, 39.2, "#FFFFFF", Z=ZS))
    out.append(R(-3.1, 3.1, 39.4, 40.0, "#FFFFFF", Z=ZS))
    out.append(stage(2.1, 40.0, 43.4))
    for xc in (-1.0, 1.0):
        ox, oy = pt(xc, 41.7, ZS)
        out.append(f'<ellipse cx="{ox:.1f}" cy="{oy:.1f}" rx="2" ry="2.8" fill="#5A4E52"/>')
    out.append(R(-2.3, 2.3, 43.2, 43.7, "#FFFFFF", Z=ZS))
    d0, d1 = pt(-2.0, 43.7, ZS), pt(2.0, 46.6, ZS)
    out.append(f'<path d="M {d0[0]:.1f} {d0[1]:.1f} Q {d0[0]:.1f} {d1[1]:.1f} {(d0[0] + d1[0]) / 2:.1f} {d1[1]:.1f} Q {d1[0]:.1f} {d1[1]:.1f} {d1[0]:.1f} {d0[1]:.1f} Z" fill="url(#{u}-white)"/>')
    l0, l1 = pt(-0.6, 46.4, ZS), pt(0.6, 48.4, ZS)
    out.append(f'<rect x="{l0[0]:.1f}" y="{l1[1]:.1f}" width="{l1[0] - l0[0]:.1f}" height="{l0[1] - l1[1]:.1f}" fill="#F2ECE0"/>')
    s0 = pt(0, 48.4, ZS)
    s1 = pt(0, 51.5, ZS)
    out.append(f'<polygon points="{P([(s0[0] - 2.4, s0[1]), (s1[0], s1[1]), (s0[0] + 2.4, s0[1])])}" fill="#E8E2D6"/>')
    out.append(f'<circle cx="{s1[0]:.1f}" cy="{s1[1] + 4:.1f}" r="1.8" fill="#E0B850"/><line x1="{s1[0]:.1f}" y1="{s1[1]:.1f}" x2="{s1[0]:.1f}" y2="{s1[1] - 6:.1f}" stroke="#2A2A30" stroke-width="1.2"/>'
               f'<path d="M {s1[0] - 4:.1f} {s1[1] - 5:.1f} L {s1[0] + 5:.1f} {s1[1] - 5:.1f} L {s1[0] + 3:.1f} {s1[1] - 7:.1f}" fill="none" stroke="#2A2A30" stroke-width="1.2"/>')
    # warm afternoon light raking from the left: lit edges, shadow halves
    for hw, Y0, Y1 in ((3.5, 27.6, 33.4), (2.9, 33.8, 39.6), (2.1, 40.0, 43.4)):
        out.append(R(hw * 0.35, hw, Y0, Y1, "#8A7E88", Z=ZS, extra=' opacity="0.22"'))
    out.append(R(-27, 27, 0, 12.2, "#FFB060", extra=' opacity="0.12"'))
    out.append(R(-4.6, 4.6, 0, 26, "#FFB060", Z=ZT, extra=' opacity="0.1"'))
    # Independence Square: lawns, brick walks, trees, lamps, visitors
    out.append(poly([C(-80, 0, 300), C(80, 0, 300), C(80, 0, 2), C(-80, 0, 2)], f"url(#{u}-lawn)"))
    out.append(grass(200, 8, (-10, 352, 610, 444), ["#A8C060", "#6E9440", "#C8D078"], h=(4, 10), sw=1.2))
    out.append(poly([C(-30, 0, ZB - 4), C(30, 0, ZB - 4), C(30, 0, ZB), C(-30, 0, ZB)], "#B87A5E"))
    out.append(poly([C(-2.2, 0, ZB - 4), C(2.2, 0, ZB - 4), C(3.2, 0, 2), C(-3.2, 0, 2)], f"url(#{u}-path)"))
    for sgn in (-1, 1):
        out.append(poly([C(sgn * 2.2, 0, ZB - 4), C(sgn * 6, 0, ZB - 4), C(sgn * 60, 0, 12), C(sgn * 52, 0, 10)], f"url(#{u}-path)"))
    rcob = random.Random(6)
    # herringbone brick of the walk
    for z in [ZB - 4 - i * 1.2 for i in range(40)]:
        if z < 2.5:
            break
        a_, b_ = C(-2.2 - (ZB - 4 - z) / (ZB - 6) * 1.0, 0, z), C(2.2 + (ZB - 4 - z) / (ZB - 6) * 1.0, 0, z)
        out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#7A3E2E" stroke-width="{max(0.5, 8 / z):.1f}" opacity="0.4"/>')
    # boxwood hedge along the foot of the hall
    hx0, hy = C(-27, 0.0, ZB - 3)
    hx1, _ = C(27, 0.0, ZB - 3)
    out.append(blobs(70, 12, (hx0, hy - 6, hx1, hy), ["#3E5E2E", "#4A6E34", "#2E4A24"], r=(3, 6), opacity=(1, 1), squash=0.7))
    out.append(blobs(30, 13, (hx0, hy - 7, hx1, hy - 3), ["#8AA84E", "#A0BC60"], r=(1.5, 3), opacity=(0.8, 1), squash=0.7))
    # dappled shade of the sycamores across the walk
    rd = random.Random(14)
    out.append('<g fill="#3A2A2A" opacity="0.2">' + "".join(
        f'<ellipse cx="{rd.uniform(150, 470):.1f}" cy="{(yy := rd.uniform(372, 444)):.1f}" rx="{rd.uniform(8, 26) * (yy - 340) / 60:.1f}" ry="{rd.uniform(2, 4) * (yy - 340) / 60:.1f}"/>' for _ in range(34)) + "</g>")
    # tree shadows pooling on the lawn (sun from the left)
    for x, y, w in ((110, 392, 120), (500, 388, 110), (30, 430, 90), (570, 432, 80)):
        out.append(f'<ellipse cx="{x + 30}" cy="{y}" rx="{w}" ry="{w * 0.16:.0f}" fill="#2E4A24" opacity="0.32"/>')
    # colonial lamp posts along the walk
    for X, Z in ((-4.2, 30), (4.2, 30), (-4.0, 16), (4.0, 16)):
        x, b = C(X, 0, Z)
        h = C.f * 3.2 / Z
        out.append(f'<rect x="{x - h * 0.02:.1f}" y="{b - h:.1f}" width="{max(1.4, h * 0.04):.1f}" height="{h:.1f}" fill="#1E2224"/>')
        out.append(f'<path d="M {x - h * 0.08:.1f} {b - h:.1f} L {x + h * 0.08:.1f} {b - h:.1f} L {x + h * 0.11:.1f} {b - h * 1.18:.1f} L {x - h * 0.11:.1f} {b - h * 1.18:.1f} Z" fill="#F4EAD0" stroke="#1E2224" stroke-width="1.2"/>'
                   f'<path d="M {x - h * 0.13:.1f} {b - h * 1.18:.1f} L {x:.1f} {b - h * 1.28:.1f} L {x + h * 0.13:.1f} {b - h * 1.18:.1f} Z" fill="#1E2224"/>')
    # visitors: a costumed guide in tricorn hat leading a small group
    gx, gb = C(-1.2, 0, 13)
    gh = C.f * 1.8 / 13
    out.append(f'<path d="M {gx:.1f} {gb:.1f} L {gx + gh * 1.2:.1f} {gb + 3:.1f} L {gx + gh * 1.2:.1f} {gb + 6:.1f} L {gx - 3:.1f} {gb + 2:.1f} Z" fill="#4A2A22" opacity="0.3"/>')
    out.append(F.person(gx, gb, gh, "point", 1, {"top": "#2E3E6A", "top_kind": "coat", "bottom": "#F2EEE6", "bottom_kind": "trousers", "shoes": "#1E1A1A",
                                                 "hat_kind": "tricorn", "hat": "#1E1A1A", "hair_style": "ponytail", "hair": "#E8E2D8", "form": "m", "skin": "#E8B898"},
                        seed=501, rim="#FFE0A8", light=-1))
    for X, Z, h, c, sk in ((1.0, 15, 1.7, "#E07A5A", True), (1.9, 15.4, 1.75, "#4A6A8A", False), (1.5, 14.4, 1.1, "#F2C84A", False), (-1.6, 30, 1.7, "#7A5A9A", False), (1.0, 38, 1.7, "#D8574A", True), (-6, 26, 1.7, "#3E7A6A", False)):
        x, b = C(X, 0, Z)
        out.append(f'<path d="M {x:.1f} {b:.1f} L {x + C.f * 2.2 / Z:.1f} {b + 2:.1f} L {x + C.f * 2.2 / Z:.1f} {b + 4:.1f} L {x - 2:.1f} {b + 1.5:.1f} Z" fill="#4A2A22" opacity="0.3"/>')
        if h < 1.5:
            out.append(F.person(x, b, C.f * h / Z, "child_34", -1, {"top": c}, seed=510, rim="#FFE6B0", light=-1))
        else:
            out.append(figure(x, b, C.f * h / Z, c, skirt=sk, rim="#FFE6B0", pose="stand_34" if Z < 20 else "walk", facing=-1, light=-1, seed=int(X * 10 + Z)))
    # big sycamores of the square framing the hall, sunlit from the left
    for cx_, cy_, r, sd in ((10, 150, 130, 1), (594, 130, 130, 2), (112, 262, 60, 3), (492, 256, 60, 4)):
        tb = 356 if r < 100 else 444
        out.append(f'<path d="M {cx_ - r * 0.07:.1f} {tb} Q {cx_ - r * 0.03:.1f} {cy_ + r * 0.5:.1f} {cx_ - r * 0.02:.1f} {cy_:.1f} L {cx_ + r * 0.05:.1f} {cy_:.1f} Q {cx_ + r * 0.04:.1f} {cy_ + r * 0.5:.1f} {cx_ + r * 0.08:.1f} {tb} Z" fill="#DCD2BC"/>')
        out.append(f'<path d="M {cx_ + r * 0.01:.1f} {tb} Q {cx_ + r * 0.02:.1f} {cy_ + r * 0.5:.1f} {cx_ + r * 0.02:.1f} {cy_:.1f} L {cx_ + r * 0.05:.1f} {cy_:.1f} Q {cx_ + r * 0.04:.1f} {cy_ + r * 0.5:.1f} {cx_ + r * 0.08:.1f} {tb} Z" fill="#8A7A6A" opacity="0.6"/>')
        out.append(blobs(int(r / 3), sd, (cx_ - r * 0.06, cy_ + r * 0.2, cx_ + r * 0.06, tb - 10), ["#8E9068", "#A8A080", "#7A7458", "#C8BEA0"], r=(r * 0.02, r * 0.045), opacity=(0.6, 0.9), squash=1.4))
        out.append(tree_crown(cx_, cy_, r, sd + 10, ["#22381C", "#2A4422"], ["#3A6228", "#46702E", "#345A26"], ["#8EAA44", "#A8B850", "#D8C468"], branch="#6E6250"))
    out.append(gulls([(330, 150, 8), (346, 160, 6), (250, 120, 7)], "#3A3A4A", 1.8))
    # a grey squirrel on the lawn and pigeons on the walk
    out.append('<g transform="translate(96 414)"><path d="M 0 0 Q -4 -12 4 -16 Q 12 -18 12 -8 L 10 0 Z" fill="#8A847C"/><circle cx="12" cy="-16" r="4.6" fill="#8A847C"/><path d="M 13 -20 l 1 -4 l 2 4 Z" fill="#8A847C"/>'
               '<path d="M 0 -2 Q -16 -6 -14 -24 Q -12 -34 -2 -30 Q -10 -22 -4 -10 Z" fill="#9A948A"/><circle cx="14.5" cy="-16.5" r="0.9" fill="#1E1A18"/><path d="M -12 -26 Q -8 -32 -2 -30" stroke="#E8E0D0" stroke-width="1.2" fill="none"/></g>')
    for px, py, s_, fl in ((330, 424, 0.9, 1), (352, 432, 1.0, -1), (282, 436, 0.95, 1)):
        out.append(f'<g transform="translate({px} {py}) scale({s_ * fl} {s_})"><ellipse cx="0" cy="-6" rx="9" ry="5.5" fill="#8A8E9E"/><path d="M 6 -9 L 16 -12 L 12 -5 Z" fill="#6E7282"/>'
                   '<circle cx="-8" cy="-10" r="3.6" fill="#6E7282"/><path d="M -11 -10 l -3 1.2 l 3 0.8 Z" fill="#E8C8A0"/><path d="M -6 -7 q 4 2 8 0" stroke="#7ABAA0" stroke-width="1.6" fill="none"/>'
                   '<path d="M -2 -1 l -1 3 M 2 -1 l 1 3" stroke="#D8786A" stroke-width="1.2"/></g>')
    return "\n".join(out)



# ---------------------------------------------------------------- Yosemite (Tunnel View at sunset)
def yosemite():
    u = "yo"
    out = [defs(
        lg(f"{u}-sky", [(0, "#4E6AA0"), (0.4, "#8E9CC4"), (0.72, "#E4B8C0"), (0.9, "#F6CDB4"), (1, "#F8DCC0")]),
        lg(f"{u}-elcap", [(0, "#F6C88A"), (0.45, "#E8A070"), (1, "#9A7A80")], 0, 0, 1, 1),
        lg(f"{u}-hd", [(0, "#F6C0A0"), (1, "#C08A98")], 0, 0, 1, 0),
        lg(f"{u}-south", [(0, "#6E7298"), (1, "#4A4E74")], 0, 0, 1, 0),
        lg(f"{u}-far", [(0, "#B8A4C4"), (1, "#9A90B8")]),
        lg(f"{u}-valley", [(0, "#4A5E6E"), (1, "#2A3A44")]),
        lg(f"{u}-fall", [(0, "#FFFFFF", 0.95), (1, "#F0F4FA", 0.6)]),
        lg(f"{u}-haze", [(0, "#E8C8D0", 0), (1, "#E8C8D0", 0.7)]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    # sunset clouds over the high country
    out.append('<g fill="#F8C8B0" opacity="0.7">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{h}"/>' for x, y, w, h in (
        (330, 118, 110, 7), (280, 128, 70, 4), (420, 102, 80, 5), (200, 96, 60, 4), (500, 132, 50, 3))) + "</g>")
    out.append('<g fill="#FFE8D8" opacity="0.6">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="2.4"/>' for x, y, w in ((320, 115, 80), (420, 100, 50))) + "</g>")
    # Clouds Rest and the far high country, hazed
    pl, far = ridge_poly([(150, 214), (220, 196), (290, 186), (330, 180), (380, 190), (450, 200), (520, 210), (610, 216)], 3, base=300, amp=5, fill=f"url(#{u}-far)")
    out.append(pl)
    # Half Dome: rounded back to the right, sheer face to the left, glowing in alpenglow
    hd = [(290, 250), (294, 224), (297, 196), (299, 176), (302, 166), (310, 161), (324, 160), (338, 164), (352, 172), (366, 184), (380, 200), (394, 218), (410, 236), (424, 250)]
    out.append(poly(hd, f"url(#{u}-hd)"))
    # the sheer northwest face, glowing, with its dark water streaks
    out.append(poly([(290, 250), (294, 224), (297, 196), (299, 176), (302, 166), (308, 162), (309, 190), (306, 222), (304, 250)], "#FAD8BC"))
    out.append('<g stroke="#B88094" stroke-width="1.4" opacity="0.55" fill="none" stroke-linecap="round">' + "".join(f'<path d="M {x} {y} q 1.5 {L / 2:.0f} -0.5 {L}"/>' for x, y, L in ((299, 182, 46), (302, 170, 56), (305, 166, 30), (296, 214, 30))) + "</g>")
    out.append('<g stroke="#FFE6D2" stroke-width="1.2" opacity="0.55" fill="none">' + "".join(f'<path d="M {x} {y} q {d} 10 {d * 2} 22"/>' for x, y, d in ((330, 168, 4), (350, 176, 5), (368, 192, 6))) + "</g>")
    out.append(f'<polyline points="{P(hd[4:12])}" fill="none" stroke="#FFE8D4" stroke-width="1.6" opacity="0.8"/>')
    out.append(f'<rect x="140" y="200" width="460" height="70" fill="url(#{u}-haze)"/>')
    # south wall beyond Bridalveil: Sentinel Rock and the spires, in cool shade
    pts_s = [(330, 262), (370, 236), (392, 214), (404, 206), (414, 214), (430, 200), (446, 186), (462, 170), (480, 152), (500, 146), (530, 140), (570, 136), (610, 132)]
    pl, sw_ = ridge_poly(pts_s, 8, base=330, amp=4, fill=f"url(#{u}-south)")
    out.append(pl)
    cid = f"{u}-swc"
    out.append(f'<clipPath id="{cid}"><polygon points="{P(sw_ + [(610, 330), (330, 330)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{cid})">' + streaks(80, 9, (360, 130, 610, 300), ["#5A5E86", "#8A8CB0", "#4E527A"], w=(0.8, 2.4), length=(16, 60), opacity=(0.25, 0.5), slant=0.06) + "</g>")
    out.append(f'<polyline points="{P([p for p in sw_ if 380 < p[0] < 600])}" fill="none" stroke="#E8B8C0" stroke-width="1.3" opacity="0.6"/>')
    # Cathedral Rocks with Bridalveil Fall dropping from its hanging valley
    cr = [(392, 330), (404, 268), (418, 236), (430, 218), (444, 190), (452, 178), (466, 176), (476, 170), (488, 186), (498, 212), (520, 206), (548, 196), (580, 188), (610, 186), (610, 330)]
    crl = rough(cr[1:-1], 21, amp=3, depth=3)
    out.append(poly([cr[0]] + crl + [cr[-1]], "#53587E"))
    cid = f"{u}-crc"
    out.append(f'<clipPath id="{cid}"><polygon points="{P([cr[0]] + crl + [cr[-1]])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{cid})">' + streaks(110, 22, (392, 170, 610, 330), ["#3E4268", "#6A6E96", "#464A70"], w=(1, 3.5), length=(14, 60), opacity=(0.3, 0.6), slant=0.08)
               + f'<polygon points="{P([(392, 330), (404, 268), (418, 236), (430, 218), (444, 190), (452, 178), (462, 240), (446, 330)])}" fill="#7A7EA8" opacity="0.35"/></g>')
    out.append(f'<polyline points="{P([p for p in crl if p[0] < 456])}" fill="none" stroke="#E8B8B8" stroke-width="1.4" opacity="0.7"/>')
    # forested slopes stepping down the valley, hazier with distance
    pl, m1 = ridge_poly([(220, 244), (270, 238), (320, 242), (360, 240), (410, 248)], 61, base=320, amp=2, fill="#8E88AA")
    out.append(pl + tree_line(m1, 62, ["#7E7A9E", "#86829E"], density=3, hmin=3, hmax=6, xmin=220, xmax=410, sink=1))
    pl, m2 = ridge_poly([(200, 270), (260, 262), (330, 266), (400, 260), (460, 272)], 63, base=320, amp=2, fill="#6E7092")
    out.append(pl + tree_line(m2, 64, ["#62668A", "#5A5E82", "#6A6E90"], density=3, hmin=5, hmax=10, xmin=200, xmax=460, sink=1))
    out.append(mist(330, 268, 140, 10, "#F0D8E0", f"{u}-m0", 0.5))
    # the fall: a wind-blown ribbon with a mist plume at its base
    fx = 506
    out.append(f'<path d="M {fx - 3} 212 Q {fx - 6} 240 {fx - 10} 270 Q {fx - 13} 290 {fx - 16} 304 L {fx - 4} 304 Q {fx - 3} 288 {fx - 1} 268 Q {fx + 1} 240 {fx + 3} 212 Z" fill="url(#{u}-fall)"/>')
    out.append(f'<path d="M {fx - 1} 214 Q {fx - 3} 250 {fx - 8} 296" stroke="#FFFFFF" stroke-width="1.4" fill="none" opacity="0.9"/>')
    out.append(mist(fx - 10, 306, 34, 18, "#F4F6FA", f"{u}-fm", 0.85))
    out.append(mist(fx - 14, 296, 18, 26, "#FFFFFF", f"{u}-fm2", 0.5))
    # El Capitan: the great sunlit face and the Nose, black water streaks, trees on the rim
    ec = [(-10, 120), (30, 112), (80, 108), (120, 110), (156, 118), (186, 128), (208, 142), (222, 160), (232, 190), (238, 230), (244, 280), (250, 340), (-10, 340)]
    ecl = rough(ec[:7], 31, amp=3, depth=3) + ec[7:]
    out.append(poly(ecl, f"url(#{u}-elcap)"))
    cid = f"{u}-ecc"
    out.append(f'<clipPath id="{cid}"><polygon points="{P(ecl)}"/></clipPath>')
    g = [streaks(260, 32, (-10, 110, 250, 340), ["#C88A6E", "#B8826E", "#A07070", "#F2B884"], w=(0.6, 1.8), length=(30, 120), opacity=(0.25, 0.55), slant=0.02),
         streaks(40, 33, (30, 120, 210, 320), ["#4A3E50", "#3A3446"], w=(0.8, 2.4), length=(50, 160), opacity=(0.2, 0.4), slant=0.02),
         # the dark diorite of the North America Wall
         f'<path d="M 122 184 Q 136 176 150 182 Q 166 180 170 196 Q 162 208 168 222 Q 158 240 150 258 Q 140 250 132 254 Q 118 238 124 222 Q 114 206 122 184 Z" fill="#4A3E54" opacity="0.16"/>',
         # horizontal exfoliation ledges catching light
         '<g stroke="#FFE0B8" stroke-width="1.2" opacity="0.4" fill="none">' + "".join(f'<path d="M {x} {y} q {w / 2} -3 {w} 1"/>' for x, y, w in ((60, 160, 40), (140, 150, 30), (100, 214, 36), (180, 262, 28), (70, 280, 40), (190, 190, 20))) + "</g>",
         # the shaded west face around the corner and a warm reflected glow on the prow
         f'<polygon points="{P([(-10, 120), (30, 112), (60, 160), (40, 240), (-10, 340)])}" fill="#5E5070" opacity="0.4"/>',
         f'<path d="M 214 150 Q 232 200 244 300 L 250 340 L 236 340 Q 226 240 206 150 Z" fill="#FFE0B0" opacity="0.35"/>']
    out.append(f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>")
    out.append(f'<polyline points="{P(ecl[2:9])}" fill="none" stroke="#FFF0D0" stroke-width="2" opacity="0.85" stroke-linejoin="round"/>')
    rnd = random.Random(35)
    for _ in range(26):
        x = rnd.uniform(-10, 200)
        y = y_on(ecl[:8], x)
        if y is None:
            continue
        out.append(conifer(x, y + 3, rnd.uniform(5, 11), rnd.choice(["#3E4A44", "#4A5648", "#344038"]), rnd.random()))
    # valley floor: a sea of conifers with mist drifting between them
    out.append(f'<rect x="0" y="300" width="600" height="144" fill="url(#{u}-valley)"/>')
    pl, vl = ridge_poly([(-10, 312), (120, 308), (240, 314), (360, 306), (480, 316), (610, 310)], 41, base=444, amp=3, fill="#3A4E58")
    out.append(pl)
    out.append(tree_line(vl, 42, ["#2E4048", "#34464E", "#2A3A42"], density=3.2, hmin=10, hmax=24))
    out.append(mist(300, 312, 300, 22, "#E8D4DC", f"{u}-m1", 0.65))
    pl, vl2 = ridge_poly([(-10, 336), (140, 330), (300, 338), (460, 330), (610, 336)], 43, base=444, amp=3, fill="#2C3E44")
    out.append(pl)
    out.append(tree_line(vl2, 44, ["#24363C", "#2A3C42", "#203036"], density=3.0, hmin=14, hmax=30))
    out.append(mist(240, 340, 220, 16, "#E8D4DC", f"{u}-m2", 0.45))
    out.append(mist(470, 334, 160, 14, "#F0DCE0", f"{u}-m3", 0.45))
    # foreground: the granite of the overlook and tall pines, warm last light on their tips
    pl, fg = ridge_poly([(-10, 378), (120, 368), (240, 380), (380, 372), (500, 382), (610, 374)], 51, base=444, amp=4, fill="#1E2C2E")
    out.append(pl)
    out.append(tree_line(fg, 52, ["#1A2828", "#1E2E2C", "#162222"], density=2.4, hmin=26, hmax=52))
    out.append('<path d="M -10 420 Q 120 404 260 414 Q 330 418 390 410 Q 430 408 450 426 Q 460 440 470 450 L -10 450 Z" fill="#6E6A72"/>')
    out.append('<path d="M -10 420 Q 120 404 260 414 Q 330 418 390 410 Q 430 408 450 426" stroke="#E8C0A0" stroke-width="2" fill="none" opacity="0.7"/>')
    out.append(streaks(40, 53, (-10, 414, 450, 444), ["#5A5660", "#8A8690"], w=(1, 3), length=(6, 20), opacity=(0.3, 0.6), slant=0.6))
    for x, b, h, sd in ((34, 446, 250, 61), (566, 446, 230, 62), (526, 446, 150, 63)):
        out.append(conifer(x, b, h, "#142020", sd, width=0.36, trunk="#2A1E1A"))
    # two hikers at the rail, and a raven riding the evening air
    for x, c, h in ((300, "#C8574A", 26), (314, "#3E5A7A", 28)):
        out.append(figure(x, 414, h, c, rim="#F8C8A0", pose="lean_back", light=1, seed=x, pal={"pack": True, "bag": "#3A4A3A" if x < 310 else "#B8573E", "season": "any"}))
    out.append('<path d="M 304 396 L 318 404" stroke="#3A3A3A" stroke-width="1.6"/>')
    out.append(gulls([(250, 160, 12), (230, 150, 7)], "#2A2430", 2.2))
    return "\n".join(out)



BUILD = {
    "yosemite": (yosemite, "YOSEMITE", "CALIFORNIA · NATIONAL PARK", "#22303A", "#F2A878", "#FBEFE4", "#F6C8A8"),
    "philadelphia": (philadelphia, "PHILADELPHIA", "PENNSYLVANIA · EST. 1682", "#4A2620", "#F2C46A", "#FBF1E2", "#F2C46A"),
    "boston": (boston, "BOSTON", "MASSACHUSETTS · EST. 1630", "#2A1E22", "#E8782A", "#FBEFE2", "#F2B85A"),
    "seattle": (seattle, "SEATTLE", "WASHINGTON · EMERALD CITY", "#1C2246", "#F4A8B8", "#FBEFF0", "#9ED8D0"),
    "charleston": (charleston, "CHARLESTON", "SOUTH CAROLINA · EST. 1670", "#24493A", "#EFAFBE", "#FBF4E8", "#F4DC8A"),
    "new-orleans": (new_orleans, "NEW ORLEANS", "LOUISIANA · EST. 1718", "#2A1E44", "#F2A07A", "#FBEFE2", "#F6C870"),
    "st-augustine": (st_augustine, "ST. AUGUSTINE", "FLORIDA · EST. 1565", "#14485A", "#E9C46A", "#FBF3E2", "#9ED6D2"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("places", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
