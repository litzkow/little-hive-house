"""American Places, painted edition (batch D): Austin, San Antonio, Santa Fe, Sedona, Arches,
Monument Valley, Atlanta and Memphis. Same gouache-poster language as places_painted.py: graded skies,
a real light direction, atmospheric depth, textured rock / water / foliage and small storytelling details."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, y_on)
from places_painted import Cam, facade_windows, puff_column
from common import SERIF_IT, MONO
from poster import ANTON, poster
import figures as F


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


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


def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def bat(x, y, s, rot, flap, col):
    """Flying bat seen from below: s = half wingspan in px; flap 0.4..1.2 squashes the wings."""
    return (f'<path transform="translate({x:.1f} {y:.1f}) rotate({rot:.0f}) scale({s / 10:.3f} {s / 10 * flap:.3f})" '
            f'd="M -10 0 Q -7 -5 -3.5 -1.5 Q -1.6 -3.6 0 -1.6 Q 1.6 -3.6 3.5 -1.5 Q 7 -5 10 0 Q 7 -1.4 5.6 1.8 Q 4 0.2 2.4 2.4 '
            f'Q 1.2 1.4 0 3.4 Q -1.2 1.4 -2.4 2.4 Q -4 0.2 -5.6 1.8 Q -7 -1.4 -10 0 Z" fill="{col}"/>')


def figure(x, base, h, col, head="#1E1418", seed=0, arm=None, rim=None, pose=None, facing=1, light=-1, pal=None, tint=None):
    """Small painted person (figures.py), h px tall. arm='point' raises an arm toward the right."""
    p = {"top": col}
    p.update(pal or {})
    pose = pose or ("point" if arm == "point" else "stand_34")
    return F.person(x, base, h, pose, facing, p, seed=seed, rim=rim, light=light, tint=tint)


def canopy_band(x0, x1, ybase, seed, colors, h=(6, 16), rim=None, n=None):
    """Irregular band of broadleaf tree crowns sitting on y = ybase (distant shoreline woods)."""
    rnd = random.Random(seed)
    n = n or int((x1 - x0) / 3)
    out = [f'<rect x="{x0}" y="{ybase - h[0] * 0.8:.1f}" width="{x1 - x0}" height="{h[0] * 0.8 + 2:.1f}" fill="{colors[0]}"/>']
    rims = []
    for _ in range(n):
        x = rnd.uniform(x0, x1)
        r = rnd.uniform(*h) * 0.55
        y = ybase - rnd.uniform(0.3, 1.0) * r * 1.4
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * rnd.uniform(0.8, 1.2):.1f}" ry="{r:.1f}" fill="{rnd.choice(colors)}"/>')
        if rim and rnd.random() < 0.5:
            rims.append(f'<path d="M {x - r * 0.9:.1f} {y:.1f} A {r:.1f} {r:.1f} 0 0 1 {x - r * 0.1:.1f} {y - r * 0.95:.1f}"/>')
    if rims:
        out.append(f'<g fill="none" stroke="{rim}" stroke-width="1.5" opacity="0.45">' + "".join(rims) + "</g>")
    return "".join(out)


# ================================================================ AUSTIN
def texas_capitol(cx, base, k, u):
    """Texas State Capitol (south facade) in local units, scaled by k: granite wings, pedimented centre,
    two-tier drum, ribbed dome, lantern and the Goddess of Liberty holding her star."""
    rnd = random.Random(5)
    g = [defs(lg(f"{u}-gran", [(0, "#F6CDB2"), (1, "#C98F7E")]),
              lg(f"{u}-dome", [(0, "#FFE6C8"), (0.45, "#F2C2A0"), (1, "#A8746E")], 0, 0, 1, 0),
              lg(f"{u}-drum", [(0, "#FBD9BC"), (1, "#C08A7C")], 0, 0, 1, 0))]
    g.append(glow(0, -95, 150, "#FFD9A6", f"{u}-cg", 0.55))
    # wings with end pavilions and a low mansard roof
    g.append('<path d="M -128 -40 L -124 -50 L 124 -50 L 128 -40 Z" fill="#7A5A62"/>')
    g.append(f'<rect x="-130" y="-40" width="260" height="40" fill="url(#{u}-gran)"/>')
    for sx in (-130, 104):
        g.append(f'<rect x="{sx}" y="-48" width="26" height="48" fill="url(#{u}-gran)"/><path d="M {sx - 1} -48 L {sx + 3} -56 L {sx + 23} -56 L {sx + 27} -48 Z" fill="#7A5A62"/>')
    g.append('<rect x="-130" y="-42" width="260" height="2.4" fill="#FFF0DC" opacity="0.8"/><rect x="-130" y="-16" width="260" height="1.6" fill="#A87266" opacity="0.6"/>')
    for row, (y, hh) in enumerate(((-36, 8), (-25, 7), (-12, 7))):
        for i in range(24):
            x = -125 + i * 10.6
            if -40 < x < 34:
                continue
            on = rnd.random() < 0.55
            g.append(f'<rect x="{x:.1f}" y="{y}" width="4.6" height="{hh}" rx="2.2" fill="{rnd.choice(["#FFD98E", "#F7C873"]) if on else "#7A5054"}"/>')
    # central pavilion, portico and pediment
    g.append(f'<rect x="-40" y="-58" width="80" height="58" fill="url(#{u}-gran)"/>')
    g.append('<polygon points="-42,-58 0,-74 42,-58" fill="#F8D8C0"/><polygon points="-34,-60 0,-71 34,-60" fill="#D9A894"/>')
    g.append('<rect x="-42" y="-60" width="84" height="3" fill="#FFF0DC"/>')
    for i in range(6):
        x = -30 + i * 12
        g.append(f'<rect x="{x - 2.4:.1f}" y="-56" width="4.8" height="38" fill="#FBE4CF"/><rect x="{x + 0.8:.1f}" y="-56" width="1.6" height="38" fill="#B98274" opacity="0.6"/>')
    g.append('<rect x="-36" y="-18" width="72" height="4" fill="#E9BDA6"/>')
    g.append("".join(f'<rect x="{-26 + i * 12}" y="-50" width="4" height="26" rx="2" fill="#FFD98E" opacity="0.85"/>' for i in range(5)))
    g.append('<path d="M -44 0 L -36 -10 L 36 -10 L 44 0 Z" fill="#E2B49E"/>')
    g.append("".join(f'<rect x="{-40 + i * 2}" y="{-9 + i * 2.2:.1f}" width="{80 - i * 4 + 8 * i}" height="1" fill="#A8786C" opacity="0.5" transform="translate({-4 * i} 0)"/>' for i in range(4)))
    # drum: lower tier with pilasters and tall arched windows, upper attic with oculi
    g.append(f'<rect x="-36" y="-108" width="72" height="34" fill="url(#{u}-drum)"/>')
    g.append('<rect x="-38" y="-76" width="76" height="3" fill="#FFF0DC"/><rect x="-38" y="-110" width="76" height="3" fill="#FFF0DC"/>')
    for i in range(7):
        x = -31 + i * 10.3
        g.append(f'<rect x="{x - 1.4:.1f}" y="-106" width="2.8" height="30" fill="#FFE8D2" opacity="0.8"/>')
        if i < 6:
            g.append(f'<rect x="{x + 2.4:.1f}" y="-102" width="5" height="18" rx="2.5" fill="#FFD27E"/>')
    g.append(f'<rect x="-30" y="-124" width="60" height="14" fill="url(#{u}-drum)"/>')
    g.append("".join(f'<circle cx="{-22 + i * 11}" cy="-117" r="2.6" fill="#FFD27E"/>' for i in range(5)))
    g.append('<rect x="-32" y="-126" width="64" height="2.6" fill="#FFF0DC"/>')
    # ribbed dome
    dome = "M -30 -126 C -30 -152 -14 -170 0 -172 C 14 -170 30 -152 30 -126 Z"
    g.append(f'<path d="{dome}" fill="url(#{u}-dome)"/>')
    for t in (-0.78, -0.5, -0.22, 0.06, 0.34, 0.62):
        g.append(f'<path d="M {30 * t:.1f} -126 Q {30 * t * 0.9:.1f} -158 {3 * t:.1f} -171" fill="none" stroke="#9A6A64" stroke-width="1.2" opacity="0.55"/>')
    g.append('<path d="M -24 -132 Q -24 -156 -6 -167" fill="none" stroke="#FFF6E8" stroke-width="2.4" stroke-linecap="round" opacity="0.8"/>')
    g.append('<path d="M -30 -138 Q 0 -134 30 -138" fill="none" stroke="#B98274" stroke-width="1.2" opacity="0.6"/>')
    # lantern, cap and the statue with her star raised
    g.append('<rect x="-7" y="-186" width="14" height="14" fill="#F4CDB0"/><rect x="2" y="-186" width="5" height="14" fill="#B98274" opacity="0.6"/>')
    g.append('<rect x="-4" y="-183" width="2.6" height="8" fill="#FFD27E"/><rect x="1.4" y="-183" width="2.6" height="8" fill="#FFD27E"/>')
    g.append('<path d="M -9 -186 Q 0 -196 9 -186 Z" fill="#E8B79E"/>')
    g.append('<path d="M -1.6 -194 L -2.4 -204 L -1 -210 L 1.2 -210 L 2.4 -204 L 1.6 -194 Z" fill="#8E6A66"/><circle cx="0" cy="-212" r="1.8" fill="#8E6A66"/>'
             '<path d="M 1 -208 L 4.5 -216" stroke="#8E6A66" stroke-width="1.6" stroke-linecap="round"/>'
             f'<polygon points="{star_pts(5, -218, 3.2)}" fill="#FFE9A8"/>')
    g.append(glow(5, -218, 9, "#FFE9A8", f"{u}-star", 0.8))
    return f'<g transform="translate({cx} {base}) scale({k})">' + "".join(g) + "</g>"


def star_pts(cx, cy, r):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.radians(-90 + i * 36)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return P(pts)


def austin():
    u = "pd-austin"
    C = Cam(f=380, cx=300, vpy=284, eye=2.4)
    CX = -8   # camera stands on the east sidewalk; the avenue centre is 8 m to the left
    out = [defs(
        lg(f"{u}-sky", [(0, "#121638"), (0.28, "#262C62"), (0.5, "#4E3E80"), (0.66, "#9A5486"), (0.78, "#E07A72"), (0.9, "#F6A866"), (1, "#F9C27A")], 0, 0, 0, 312, units="userSpaceOnUse"),
        lg(f"{u}-lake", [(0, "#E79A78"), (0.25, "#8E6A8E"), (0.7, "#3A3E6E"), (1, "#1E2246")], 0, 284, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-deck", [(0, "#4A4258"), (0.4, "#2E2A3A"), (1, "#1A1822")], 0, 262, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-walk", [(0, "#6A5E6E"), (1, "#3A3240")], 0, 262, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-glass", [(0, "#4A5A8E"), (1, "#232A52")]),
        lg(f"{u}-glass2", [(0, "#3E4C7E"), (1, "#1C2246")]),
        lg(f"{u}-dark", [(0, "#100E22", 0), (0.6, "#100E22", 0.15), (1, "#100E22", 0.55)], 0, 0, 0, 1),
        lg(f"{u}-rimL", [(0, "#FFB27A", 0.65), (1, "#FFB27A", 0)], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(70, 2, (0, 40, 600, 150), "#F6EDE0", r=(0.6, 1.5), opacity=(0.35, 1)))
    out.append(glow(70, 290, 260, "#FFC07A", f"{u}-sun", 0.75))
    # thin dusk clouds lit from below
    out.append('<g fill="#F49C86" opacity="0.5">' + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{h}"/>' for x, y, w, h in ((90, 216, 110, 4), (40, 230, 70, 3), (180, 196, 80, 3), (470, 206, 90, 3.5), (560, 224, 60, 3))) + "</g>")
    out.append('<g fill="#6E4A86" opacity="0.45">' + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="3"/>' for x, y, w in ((96, 212, 90), (468, 202, 70))) + "</g>")
    # Texas Hill Country on the horizon (west, left) and the hazy far shore
    poly, _ = ridge_poly([(-10, 284), (60, 276), (130, 280), (200, 274), (260, 282), (340, 280), (420, 276), (520, 280), (610, 274)], 7, base=297, amp=3, fill="#6A4A7A")
    out.append(poly)
    # Lady Bird Lake on both sides of the bridge
    out.append(f'<rect x="0" y="284" width="600" height="160" fill="url(#{u}-lake)"/>')
    rnd = random.Random(11)
    for i in range(70):
        y = 288 + (i / 70) ** 1.6 * 130
        x = rnd.uniform(0, 600)
        w = rnd.uniform(10, 50) * (0.4 + (y - 262) / 120)
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="1.2" fill="{"#FFC890" if x < 260 else "#9A8AB6"}" opacity="{rnd.uniform(0.25, 0.6):.2f}"/>')
    # shoreline trees on the north bank (irregular canopy, lit on the sunset side)
    out.append(canopy_band(-10, 170, 284, 5, ["#2A2A46", "#30304E", "#26243E"], h=(6, 16), rim="#E89A7A"))
    out.append(canopy_band(430, 610, 284, 6, ["#2A2A46", "#30304E", "#26243E"], h=(6, 14)))
    # the avenue rising beyond the bridge, lined by historic storefronts and towers
    def X(x):
        return x + CX
    towers = [  # (X0, X1, Z, height m, fill, crown)
        (-64, -44, 170, 48, f"url(#{u}-glass2)", "flat"), (-42, -26, 210, 44, f"url(#{u}-glass)", "notch"),
        (-30, -19, 270, 34, f"url(#{u}-glass2)", "flat"), (-84, -64, 140, 36, "#5A3E52", "flat"),
        (22, 38, 210, 46, f"url(#{u}-glass)", "spire"), (18, 27, 270, 32, f"url(#{u}-glass2)", "flat"),
        (40, 56, 170, 34, "#4E3A50", "slant"),
    ]
    for X0, X1, Z, h, fill, crown in sorted(towers, key=lambda t: -t[2]):
        q = C.quad_z(Z, X(X0), X(X1), 0, h)
        x0, x1, yt, yb = q[0][0], q[2][0], q[1][1], q[0][1]
        w = x1 - x0
        if crown == "notch":   # a pointed crown with notched shoulders, like the tower on Congress
            out.append(f'<polygon points="{P([(x0, yb), (x0, yt), (x0 + w * 0.2, yt - w * 0.25), (x0 + w * 0.35, yt - w * 0.18), (x0 + w * 0.5, yt - w * 0.9), (x0 + w * 0.65, yt - w * 0.18), (x0 + w * 0.8, yt - w * 0.25), (x1, yt), (x1, yb)])}" fill="{fill}"/>')
        elif crown == "spire":
            out.append(f'<polygon points="{P([(x0, yb), (x0, yt), (x0 + w * 0.5, yt - w * 0.45), (x1, yt), (x1, yb)])}" fill="{fill}"/>')
            out.append(f'<line x1="{x0 + w * 0.5:.1f}" y1="{yt - w * 0.45:.1f}" x2="{x0 + w * 0.5:.1f}" y2="{yt - w * 0.9:.1f}" stroke="#2A2E58" stroke-width="1.6"/><circle cx="{x0 + w * 0.5:.1f}" cy="{yt - w * 0.9:.1f}" r="1.6" fill="#FF6A6A"/>')
        elif crown == "slant":
            out.append(f'<polygon points="{P([(x0, yb), (x0, yt + w * 0.35), (x1, yt), (x1, yb)])}" fill="{fill}"/>')
        else:
            out.append(f'<rect x="{x0:.1f}" y="{yt:.1f}" width="{w:.1f}" height="{yb - yt:.1f}" fill="{fill}"/>')
        r3 = random.Random(int(Z * 7 + X0))
        cw = w / 9
        for yy in [yt + 4 + i * 4.2 for i in range(int((yb - yt - 6) / 4.2))]:
            for j in range(8):
                if r3.random() < 0.36:
                    out.append(f'<rect x="{x0 + cw * (j + 0.65):.1f}" y="{yy:.1f}" width="{cw * 0.62:.1f}" height="2.2" fill="{r3.choice(["#FFD98E", "#F7C873", "#FFE7B0"])}" opacity="{r3.uniform(0.6, 1):.2f}"/>')
        if x1 < 300:   # rim light from the western glow on the left edges
            out.append(f'<rect x="{x0:.1f}" y="{yt:.1f}" width="{max(2, w * 0.12):.1f}" height="{yb - yt:.1f}" fill="url(#{u}-rimL)"/>')
        else:
            out.append(f'<rect x="{x0:.1f}" y="{yt:.1f}" width="{max(1.5, w * 0.08):.1f}" height="{yb - yt:.1f}" fill="#F7A07A" opacity="0.35"/>')
    # the Capitol at the head of the avenue, floodlit (drawn larger than life, as posters do)
    out.append(texas_capitol(C(X(0), 0, 430)[0], 291, 0.88, u))
    # low historic storefronts along Congress Avenue
    blds = {-1: [(48, 70, 16, "#8E4E44"), (70, 96, 12, "#C9A27A"), (96, 130, 18, "#6E4252"), (130, 170, 11, "#A86A4E"), (170, 230, 14, "#5A4258"), (230, 330, 10, "#7A5A5A")],
            1: [(48, 64, 13, "#C2946E"), (64, 90, 17, "#7E3E3A"), (90, 120, 11, "#5E5070"), (120, 165, 15, "#A0583E"), (165, 230, 12, "#6A4A5A"), (230, 330, 10, "#8A6A5A")]}
    for sgn, lst in blds.items():
        Xf = X(sgn * 14)
        for k, (z0, z1, h, col) in enumerate(lst):
            out.append(f'<polygon points="{P(C.quad_x(Xf, z0, z1, 0, h))}" fill="{col}"/>')
            out.append(facade_windows(C, Xf, z0, z1, 4.5, h - 1.5, 3.6, max(2, int((z1 - z0) / 7)), "#2A2030", k * 13 + sgn, lit_p=0.55))
            out.append(f'<polygon points="{P(C.quad_x(Xf, z0, z1, h - 0.8, h))}" fill="#F4D8B8" opacity="0.55"/>')
            out.append(f'<polygon points="{P(C.quad_x(Xf, z0 + 0.6, z1 - 0.6, 0.2, 3.4))}" fill="#F6B260" opacity="0.85"/>')
            out.append(f'<polygon points="{P(C.quad_x(Xf, z0, z0 + 0.6, 0, h))}" fill="#000" opacity="0.25"/>')
            out.append(f'<polygon points="{P(C.quad_x(Xf, z0, z1, 0, h))}" fill="url(#{u}-dark)"/>')
    # avenue surface beyond the bridge and the bridge deck
    out.append(f'<polygon points="{P([C(X(-14), 0, 46), C(X(14), 0, 46), C(X(14), 0, 430), C(X(-14), 0, 430)])}" fill="#3A3246"/>')
    out.append(f'<polygon points="{P([C(X(-13), 0, 3), C(X(13), 0, 3), C(X(13), 0, 48), C(X(-13), 0, 48)])}" fill="url(#{u}-deck)"/>')
    for sgn in (-1, 1):
        out.append(f'<polygon points="{P([C(X(sgn * 10), 0.15, 3), C(X(sgn * 13), 0.15, 3), C(X(sgn * 13), 0.15, 48), C(X(sgn * 10), 0.15, 48)])}" fill="url(#{u}-walk)"/>')
    # green bike lanes and the warm pools of lamplight on the asphalt
    for sgn in (-1, 1):
        out.append(f'<polygon points="{P([C(X(sgn * 8.6), 0, 3), C(X(sgn * 10), 0, 3), C(X(sgn * 10), 0, 48), C(X(sgn * 8.6), 0, 48)])}" fill="#3E6A5A" opacity="0.22"/>')
        for Z in (6, 12, 20, 30, 44):
            px, py = C(X(sgn * 10.5), 0, Z)
            out.append(mist(px, py, C.f * 5 / Z, C.f * 1.2 / Z, "#FFD9A0", f"{u}-pool{Z}{sgn + 1}", 0.35))
    out.append(dots(160, 41, (0, 330, 600, 404), "#8A7A90", r=(0.6, 1.4), opacity=(0.15, 0.4)))
    # lane lines and long-exposure light trails up the hill
    for x_ in (-3.4, 3.4):
        for z in (5, 8, 11.5, 16, 22, 30, 40, 54, 72, 96, 128, 170, 225, 300):
            out.append(f'<polygon points="{P([C(X(x_) - 0.1, 0, z), C(X(x_) + 0.1, 0, z), C(X(x_) + 0.1, 0, z * 1.1), C(X(x_) - 0.1, 0, z * 1.1)])}" fill="#E8E0D8" opacity="0.7"/>')
    out.append(f'<polygon points="{P([C(X(-0.25), 0, 3), C(X(0.25), 0, 3), C(X(0.25), 0, 430), C(X(-0.25), 0, 430)])}" fill="#E9B949" opacity="0.8"/>')
    # traffic: tail lights heading up the hill on the right, headlights coming down on the left
    def car(Xc, Z, col, toward):
        x, b = C(X(Xc), 0, Z)
        k = C.f / Z / 20
        g = (f'<g transform="translate({x:.1f} {b:.1f}) scale({k:.3f})">'
             f'<path d="M -40 -6 L -40 -26 Q -40 -30 -36 -30 L -26 -30 L -20 -46 Q -18 -50 -14 -50 L 14 -50 Q 18 -50 20 -46 L 26 -30 L 36 -30 Q 40 -30 40 -26 L 40 -6 Z" fill="{col}"/>'
             '<path d="M -16 -32 L -12 -46 L 12 -46 L 16 -32 Z" fill="#2A2638" opacity="0.8"/><rect x="-40" y="-14" width="80" height="5" fill="#1A1822" opacity="0.5"/>'
             '<rect x="-36" y="-8" width="14" height="10" rx="3" fill="#0E0C12"/><rect x="22" y="-8" width="14" height="10" rx="3" fill="#0E0C12"/>')
        lc = "#FFF4D0" if toward else "#FF3A3A"
        g += f'<rect x="-38" y="-26" width="10" height="6" rx="2" fill="{lc}"/><rect x="28" y="-26" width="10" height="6" rx="2" fill="{lc}"/></g>'
        for sx in (-33, 33):
            g += glow(x + sx * k, b - 23 * k, (30 if toward else 18) * k, lc, f"{u}-c{int(Z)}{sx}", 0.7)
            g += f'<rect x="{x + sx * k - 3 * k:.1f}" y="{b + 1:.1f}" width="{6 * k:.1f}" height="{min(30, 500 / Z):.1f}" fill="{lc}" opacity="0.14"/>'
        return g
    for Xc, Z, col, tw in ((5.4, 140, "#3E5A7A", False), (-5.2, 105, "#8A3A3A", True), (5.4, 78, "#C9A24A", False), (-5.6, 34, "#2E5A6A", True)):
        out.append(car(Xc, Z, col, tw))
    # bridge railings with balusters and lamp standards
    for sgn in (-1, 1):
        Xr = X(sgn * 13)
        out.append(f'<polygon points="{P([C(Xr, 0, 3), C(Xr, 1.1, 3), C(Xr, 1.1, 48), C(Xr, 0, 48)])}" fill="#8E8090" opacity="0.35"/>')
        bal = []
        z = 4.0
        while z < 48:
            a_, b_ = C(Xr, 0.15, z), C(Xr, 1.0, z)
            bal.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke-width="{max(1.2, C.f * 0.12 / z):.1f}"/>')
            z *= 1.07
        out.append('<g stroke="#C9B8C0" opacity="0.85">' + "".join(bal) + "</g>")
        out.append(f'<polyline points="{P([C(Xr, 1.1, 3), C(Xr, 1.1, 48)])}" fill="none" stroke="#E6D6D8" stroke-width="2.4"/>')
        for Z in (6, 12, 20, 30, 44):
            a_, b_ = C(Xr, 0, Z), C(Xr, 7, Z)
            h_ = C(Xr - sgn * 1.4, 7, Z)
            sw = max(1.5, C.f * 0.16 / Z)
            out.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} L {b_[0]:.1f} {b_[1]:.1f} Q {b_[0]:.1f} {b_[1] - sw * 2:.1f} {h_[0]:.1f} {h_[1]:.1f}" fill="none" stroke="#2A2434" stroke-width="{sw:.1f}"/>')
            out.append(glow(h_[0], h_[1] + sw, C.f * 1.4 / Z, "#FFE2A0", f"{u}-l{Z}{sgn + 1}", 0.8))
            out.append(f'<circle cx="{h_[0]:.1f}" cy="{h_[1] + sw:.1f}" r="{max(1.5, sw * 0.9):.1f}" fill="#FFF4D6"/>')
    # the bats: a smoky ribbon pouring out from under the bridge and curling away east into the dusk
    rb = random.Random(21)
    path = [((440, 318), (480, 280), (520, 290), (560, 250)), ((560, 250), (590, 222), (560, 190), (620, 160)),
            ((466, 300), (420, 262), (470, 220), (420, 190))]
    for seg in path[:2]:
        d = "M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f" % (*seg[0], *seg[1], *seg[2], *seg[3])
        out.append(f'<path d="{d}" fill="none" stroke="#2A1E34" stroke-width="26" stroke-linecap="round" opacity="0.16"/>'
                   f'<path d="{d}" fill="none" stroke="#2A1E34" stroke-width="12" stroke-linecap="round" opacity="0.2"/>')
    bats_ = []
    for seg_i, (seg, n, sp) in enumerate(zip(path, (460, 300, 110), (12, 15, 10))):
        for i in range(n):
            t = rb.random() ** (0.8 if seg_i == 0 else 1.3)
            x, y = bez(*seg, t)
            x += rb.gauss(0, sp * (0.6 + t))
            y += rb.gauss(0, sp * 0.5 * (0.6 + t))
            s = rb.uniform(2.0, 3.6) * (1.0 + 0.25 * (seg_i == 1))
            bats_.append(bat(x, y, s, rb.uniform(-35, 35), rb.uniform(0.5, 1.2), rb.choice(["#1A1426", "#241A30", "#2E2238"])))
    out.append("".join(bats_))
    for x, y, s, r in ((506, 226, 7, -10), (530, 196, 8, 12), (480, 170, 6, -20), (566, 132, 7, 8), (398, 214, 5, -8), (510, 136, 6, 15), (446, 148, 5, 5), (536, 268, 6, -6)):
        out.append(bat(x, y, s, r, 0.9, "#1A1426"))
    # crowd at the east railing watching the bats (we stand among them)
    for Xp, Z, h, col, arm, sd in ((12.4, 30, 1.6, "#7A5A8A", None, 1), (12.3, 24, 1.75, "#C9734A", None, 2), (12.5, 19, 1.7, "#3E6A8A", None, 3),
                                   (12.2, 15, 1.2, "#E0B24A", "point", 4), (12.5, 14.3, 1.8, "#5A3A4A", None, 5), (12.3, 10.5, 1.72, "#8A3A4A", None, 6),
                                   (12.5, 8.6, 1.66, "#3A5A4A", "point", 7)):
        x, b = C(X(Xp), 0.15, Z)
        hh = C.f * h / Z
        pose = "child_34" if h < 1.5 else ("point" if arm else ("stand_side", "photo", "stand_side", "lean", "stand_side", "stand_side", "point")[sd - 1])
        out.append(figure(x, b, hh, col, seed=sd, rim="#FFB27A", pose=pose, facing=1, light=-1, tint=("#2A2040", 0.18)))
    for Xp, Z, h, col, sd in ((-11.5, 22, 1.7, "#4A5A7A", 8), (-11.8, 14, 1.65, "#9A5A4A", 9)):
        x, b = C(X(Xp), 0.15, Z)
        out.append(figure(x, b, C.f * h / Z, col, seed=sd, pose="walk", facing=-1, light=1, tint=("#2A2040", 0.18)))
    # a cyclist rolling down the bike lane toward us
    x, b = C(X(-9.2), 0, 34)
    k = C.f / 34 / 100
    out.append(F.person(x, b, 100 * k, "cyclist_front", 1, {"top": "#D9A04A", "bottom": "#1E1A28", "bottom_kind": "trousers", "hat_kind": "helmet", "hat": "#E9E0D8"},
                        seed=8, rim="#FFB27A", light=-1, tint=("#2A2040", 0.2)))
    out.append(glow(x, b - 48 * k, 26 * k, "#FFF4D0", f"{u}-bk", 0.8))
    # right foreground: a dad with his daughter on his shoulders, rim-lit by the lamps
    x, b = C(X(10.6), 0.15, 5.6)
    k = C.f / 5.6 / 100
    out.append(F.parent_child(x, b, 104 * k, 1, {"top": "#3E4A6A", "form": "m", "bottom": "#1A1622", "top_kind": "jacket"}, seed=9, rim="#FFB27A", light=-1,
                              tint=("#2A2040", 0.22), view="back"))
    return "\n".join(out)


# ================================================================ SAN ANTONIO (the River Walk)
def bald_cypress(x, base, h, seed, lit="#9CC46A", mid="#5E8A44", dark="#2E4A30", trunk="#6E5444", top=None, fol=None, wk=0.035, nf=None):
    """River Walk bald cypress: flared, buttressed trunk and feathery drooping sprays of foliage."""
    rnd = random.Random(seed)
    w = h * wk
    tt = top if top is not None else base - h
    fy0, fy1 = fol if fol else (tt - h * 0.05, base - h * 0.42)
    out = [f'<path d="M {x - w * 2.2:.1f} {base:.1f} Q {x - w * 0.9:.1f} {base - h * 0.06:.1f} {x - w:.1f} {base - h * 0.2:.1f} L {x - w * 0.55:.1f} {tt:.1f} '
           f'L {x + w * 0.55:.1f} {tt:.1f} L {x + w:.1f} {base - h * 0.2:.1f} Q {x + w * 0.9:.1f} {base - h * 0.06:.1f} {x + w * 2.4:.1f} {base:.1f} Z" fill="{trunk}"/>',
           f'<path d="M {x + w * 0.2:.1f} {base:.1f} L {x + w * 0.4:.1f} {base - h * 0.2:.1f} L {x + w * 0.4:.1f} {tt:.1f} L {x + w * 0.55:.1f} {tt:.1f} L {x + w:.1f} {base - h * 0.2:.1f} Q {x + w * 0.9:.1f} {base - h * 0.06:.1f} {x + w * 2.4:.1f} {base:.1f} Z" fill="#3A2C26" opacity="0.45"/>']
    out.append(f'<g stroke="#4A3A32" stroke-width="1.5" opacity="0.6" fill="none">' + "".join(
        f'<path d="M {x + rnd.uniform(-w * 0.6, w * 0.4):.1f} {base - rnd.uniform(0, h * 0.1):.1f} l {rnd.uniform(-1, 1):.1f} {-rnd.uniform(h * 0.15, h * 0.4):.1f}"/>' for _ in range(5)) + "</g>")
    # foliage sprays: drooping clumps, dark under, lit on top-right
    for i in range(nf or int(h / 5)):
        cy = rnd.uniform(fy0, fy1)
        cx = x + rnd.uniform(-h * 0.32, h * 0.34)
        r = rnd.uniform(h * 0.05, h * 0.11)
        out.append(f'<path d="M {cx - r * 1.3:.1f} {cy:.1f} Q {cx:.1f} {cy - r * 1.1:.1f} {cx + r * 1.3:.1f} {cy:.1f} Q {cx + r * 0.9:.1f} {cy + r * 0.9:.1f} {cx + r * 0.3:.1f} {cy + r * 1.3:.1f} '
                   f'Q {cx:.1f} {cy + r * 0.7:.1f} {cx - r * 0.4:.1f} {cy + r * 1.2:.1f} Q {cx - r:.1f} {cy + r * 0.8:.1f} {cx - r * 1.3:.1f} {cy:.1f} Z" fill="{rnd.choice([mid, dark, mid])}"/>')
        if rnd.random() < 0.6:
            out.append(f'<path d="M {cx - r * 0.6:.1f} {cy - r * 0.3:.1f} Q {cx + r * 0.2:.1f} {cy - r * 0.95:.1f} {cx + r * 1.1:.1f} {cy - r * 0.1:.1f}" fill="none" stroke="{lit}" stroke-width="{max(1.5, r * 0.35):.1f}" stroke-linecap="round" opacity="0.8"/>')
        # hanging needle strands
        out.append(f'<g stroke="{mid}" stroke-width="1.5" stroke-linecap="round">' + "".join(
            f'<line x1="{cx + d:.1f}" y1="{cy + r * 0.6:.1f}" x2="{cx + d + 1:.1f}" y2="{cy + r * rnd.uniform(1.2, 1.9):.1f}"/>' for d in (rnd.uniform(-r, r) for _ in range(3))) + "</g>")
    return "".join(out)


def umbrella(x, y, r, col, shade, rim="#FFF6E0"):
    """Patio umbrella, 8 panels, seen from slightly below/side: (x, y) = canopy top centre, r = half width."""
    h = r * 0.55
    edge = y + h
    out = [f'<path d="M {x - r:.1f} {edge:.1f} Q {x - r * 0.6:.1f} {y + h * 0.05:.1f} {x:.1f} {y:.1f} Q {x + r * 0.6:.1f} {y + h * 0.05:.1f} {x + r:.1f} {edge:.1f} Z" fill="{col}"/>']
    # panel seams and alternating shade (light from the right)
    for i, t in enumerate((-0.62, -0.22, 0.22, 0.62)):
        out.append(f'<path d="M {x:.1f} {y:.1f} Q {x + r * t * 0.7:.1f} {y + h * 0.4:.1f} {x + r * t:.1f} {edge:.1f}" fill="none" stroke="{shade}" stroke-width="{max(1, r * 0.04):.1f}" opacity="0.7"/>')
    out.append(f'<path d="M {x - r:.1f} {edge:.1f} Q {x - r * 0.6:.1f} {y + h * 0.05:.1f} {x:.1f} {y:.1f} L {x - r * 0.22:.1f} {edge:.1f} Z" fill="{shade}" opacity="0.45"/>')
    out.append(f'<path d="M {x + r * 0.22:.1f} {edge:.1f} L {x:.1f} {y:.1f} Q {x + r * 0.6:.1f} {y + h * 0.05:.1f} {x + r:.1f} {edge:.1f} Z" fill="#FFFFFF" opacity="0.18"/>')
    # scalloped valance
    n = 8
    sc = "".join(f'Q {x - r + (i + 0.5) * 2 * r / n:.1f} {edge + r * 0.14:.1f} {x - r + (i + 1) * 2 * r / n:.1f} {edge:.1f} ' for i in range(n))
    out.append(f'<path d="M {x - r:.1f} {edge:.1f} {sc}Z" fill="{shade}"/>')
    out.append(f'<circle cx="{x:.1f}" cy="{y - r * 0.05:.1f}" r="{max(1, r * 0.06):.1f}" fill="{rim}"/>')
    return "".join(out)


def papel(x0, y0, x1, y1, sag, n, seed, cols, size=1.0, u="pp"):
    """String of papel picado flags along a sagging line, each with little cut-out shapes."""
    rnd = random.Random(seed)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    out = [f'<path d="M {x0:.1f} {y0:.1f} Q {mx:.1f} {my + sag:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="#4A3A3A" stroke-width="1.5"/>']
    for i in range(n):
        t = (i + 0.5) / n
        x = (1 - t) ** 2 * x0 + 2 * t * (1 - t) * mx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * t * (1 - t) * (my + sag) + t * t * y1
        w = 2 * abs(x1 - x0) / n * 0.42 * size
        hh = w * 1.25
        sk = rnd.uniform(-0.12, 0.12) * w
        col = cols[i % len(cols)]
        out.append(f'<path d="M {x - w / 2:.1f} {y:.1f} L {x + w / 2:.1f} {y:.1f} L {x + w / 2 + sk:.1f} {y + hh:.1f} '
                   + "".join(f'L {x + w / 2 + sk - (j + 0.5) * w / 4:.1f} {y + hh - w * 0.12:.1f} L {x + w / 2 + sk - (j + 1) * w / 4:.1f} {y + hh:.1f} ' for j in range(4))
                   + f'Z" fill="{col}" opacity="0.92"/>')
        # cut-outs: a flower and little diamonds
        cy = y + hh * 0.48
        out.append(f'<g fill="#FFF4E6" opacity="0.7"><circle cx="{x + sk / 2:.1f}" cy="{cy:.1f}" r="{w * 0.13:.1f}"/>'
                   + "".join(f'<circle cx="{x + sk / 2 + w * 0.22 * math.cos(a):.1f}" cy="{cy + w * 0.22 * math.sin(a):.1f}" r="{w * 0.07:.1f}"/>' for a in (0, 1.57, 3.14, 4.71))
                   + f'<rect x="{x - w * 0.32:.1f}" y="{y + hh * 0.14:.1f}" width="{w * 0.64:.1f}" height="{max(1, w * 0.05):.1f}"/></g>')
    return "".join(out)


def san_antonio():
    u = "pd-sanantonio"
    C = Cam(f=330, cx=300, vpy=236, eye=3.6)
    W = 7.0      # river half width
    out = [defs(
        lg(f"{u}-sky", [(0, "#8CCFD6"), (0.6, "#D8EED6"), (1, "#FCE8B8")], 0, 40, 0, 240, units="userSpaceOnUse"),
        lg(f"{u}-river", [(0, "#A9D6B6"), (0.15, "#5FA894"), (0.55, "#2F7A6E"), (1, "#1E5550")], 0, 236, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-walkL", [(0, "#D9BE98"), (1, "#A88262")], 0, 236, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-walkR", [(0, "#BFA486"), (1, "#7E6450")], 0, 236, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-wallL", [(0, "#F2DDB8"), (1, "#D6B48A")]),
        lg(f"{u}-shade", [(0, "#1E3A2E", 0.0), (1, "#1E3A2E", 0.45)], 0, 0, 1, 0),
        lg(f"{u}-arch", [(0, "#EED8B2"), (1, "#C9A47A")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(390, 150, 200, "#FFF6D8", f"{u}-sun", 0.8))
    # far bend: sunlit hotel walls and treetops closing the view
    out.append('<rect x="200" y="140" width="70" height="100" fill="#E8C49A"/><rect x="200" y="140" width="70" height="6" fill="#B86A4A"/>')
    out.append("".join(f'<rect x="{206 + i * 12}" y="{152 + j * 16}" width="6" height="9" rx="3" fill="#A87A5E"/>' for i in range(5) for j in range(5)))
    out.append('<rect x="330" y="118" width="64" height="122" fill="#D9A98A"/><rect x="330" y="118" width="64" height="5" fill="#9A5A44"/>')
    out.append("".join(f'<rect x="{336 + i * 12}" y="{130 + j * 15}" width="6" height="8" fill="#8E6A5E"/>' for i in range(5) for j in range(7)))
    out.append(canopy_band(180, 440, 242, 12, ["#4E7A44", "#5E8A4A", "#6E9A4E"], h=(14, 34), rim="#C8E08A", n=120))
    # the river and its walkways
    out.append(f'<polygon points="{P([C(-W, 0, 400), C(W, 0, 400), C(W, 0, 3), C(-W, 0, 3)])}" fill="url(#{u}-river)"/>')
    out.append(f'<polygon points="{P([C(-W, 1.0, 400), C(-14, 1.0, 400), C(-14, 1.0, 3), C(-W, 1.0, 3)])}" fill="url(#{u}-walkL)"/>')
    out.append(f'<polygon points="{P([C(W, 1.0, 400), C(14, 1.0, 400), C(14, 1.0, 3), C(W, 1.0, 3)])}" fill="url(#{u}-walkR)"/>')
    # flagstone joints
    for sgn in (-1, 1):
        for z in (5, 6.5, 8.4, 10.8, 14, 18, 23, 30, 39):
            a_, b_ = C(sgn * W, 1.0, z), C(sgn * 14, 1.0, z)
            out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#7A5E48" stroke-width="1.2" opacity="0.4"/>')
        for xx in (W + 2.4, W + 4.8):
            a_, b_ = C(sgn * xx, 1.0, 4), C(sgn * xx, 1.0, 60)
            out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#7A5E48" stroke-width="1.2" opacity="0.3"/>')
        # limestone coping along the water (no railings on the River Walk)
        out.append(f'<polygon points="{P([C(sgn * W, 1.0, 3), C(sgn * W, 1.0, 400), C(sgn * W, 0, 400), C(sgn * W, 0, 3)])}" fill="#8A6E58"/>')
        out.append(f'<polyline points="{P([C(sgn * W, 1.0, 3), C(sgn * W, 1.0, 400)])}" fill="none" stroke="#F2E2C4" stroke-width="2"/>')
    # left bank: stucco and limestone buildings with balconies, arched doorways, bougainvillea
    blds = [(4, 13, 13, "#F0D4AE"), (13, 21, 11, "#E7A57E"), (21, 30, 14, "#F2E4C6"), (30, 40, 10, "#D98E6A"), (40, 60, 12, "#EBCDA2")]
    for k, (z0, z1, h, col) in enumerate(blds):
        Xw = -14
        out.append(f'<polygon points="{P(C.quad_x(Xw, z0, z1, 1, h))}" fill="{col}"/>')
        out.append(f'<polygon points="{P(C.quad_x(Xw, z0, z1, h - 0.6, h))}" fill="#A8604A"/>')
        out.append(f'<polygon points="{P(C.quad_x(Xw, z0, z0 + 0.4, 1, h))}" fill="#000" opacity="0.15"/>')
        bays = max(2, int((z1 - z0) / 3))
        for i in range(bays):
            za, zb = z0 + (z1 - z0) * (i + 0.25) / bays, z0 + (z1 - z0) * (i + 0.75) / bays
            # ground floor arches glowing warm
            out.append(f'<polygon points="{P(C.quad_x(Xw, za, zb, 1, 3.4))}" fill="#7A4434"/>')
            out.append(f'<polygon points="{P(C.quad_x(Xw, za + 0.15, zb - 0.15, 1, 3.1))}" fill="#F6C27A" opacity="0.8"/>')
            for fl in range(1, int((h - 2) / 3.4)):
                y0 = 1 + fl * 3.4 + 0.7
                out.append(f'<polygon points="{P(C.quad_x(Xw, za, zb, y0, y0 + 2.0))}" fill="#4E3A3A"/>')
                out.append(f'<polygon points="{P(C.quad_x(Xw, za - 0.1, zb + 0.1, y0 + 2.0, y0 + 2.25))}" fill="#FFF0D8" opacity="0.7"/>')
                out.append(f'<polygon points="{P(C.quad_x(Xw, za - 0.15, za + 0.25, y0, y0 + 2.0))}" fill="{["#3E7A6A", "#2E5A8A", "#7A3A3A"][k % 3]}"/>')
                # wrought-iron balcony
                a_, b_ = C(Xw + 0.5, y0 + 0.7, za - 0.3), C(Xw + 0.5, y0 + 0.7, zb + 0.3)
                out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#2A2222" stroke-width="{max(1.2, C.f * 0.08 / za):.1f}"/>')
        out.append(f'<polygon points="{P(C.quad_x(Xw, z0, z1, 1, h))}" fill="url(#{u}-shade)"/>')
    # bougainvillea spilling over the balconies
    rb = random.Random(4)
    for z, y in ((6, 6.5), (9, 9.8), (16, 6.2), (24, 9.6), (33, 5.8)):
        x, yy = C(-13.6, y, z)
        rr = C.f * 0.9 / z
        out.append(blobs(14, int(z * 3), (x - rr, yy - rr * 0.4, x + rr, yy + rr * 0.8), ["#E0458A", "#F06AA0", "#C2306E"], r=(rr * 0.15, rr * 0.35), opacity=(0.8, 1), squash=0.8))
        out.append(blobs(6, int(z * 5), (x - rr, yy, x + rr, yy + rr * 0.6), ["#4E7A3E", "#3A6A34"], r=(rr * 0.1, rr * 0.2), opacity=(0.8, 1), squash=0.7))
    # patio tables with colourful umbrellas on the left walkway
    ucols = [("#E8423E", "#A82A2E"), ("#F6B83A", "#C2861E"), ("#2EA6A0", "#1E7470"), ("#F07A2E", "#B8521E"), ("#E85A9A", "#A8306A"), ("#3A7AC8", "#24508A")]
    for i, Z in enumerate((40, 32, 26, 21, 17, 13.5, 10.6, 8.4)):
        for Xu, off in ((-11.6, 0), (-8.9, 1)):
            if Z < 9 and Xu > -10:
                continue
            col, sh = ucols[(i * 2 + off) % len(ucols)]
            x, y = C(Xu, 3.6, Z)
            r = C.f * 1.25 / Z
            bx, by = C(Xu, 1.0, Z)
            out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="#3A2A22" stroke-width="{max(1, r * 0.06):.1f}"/>')
            # table, diners
            tw = r * 0.45
            out.append(f'<rect x="{bx - tw:.1f}" y="{by - r * 0.36:.1f}" width="{tw * 2:.1f}" height="{r * 0.06 + 1:.1f}" fill="#F4ECE0"/>')
            for dx, pc in ((-tw * 1.1, ["#2E4A6A", "#8A3A4A", "#3A6A4A", "#D9A04A"][(i + off) % 4]), (tw * 1.1, ["#C9734A", "#4A4A7A", "#E0C27A", "#6A3A5A"][(i + off) % 4])):
                out.append(F.person(bx + dx * 1.15, by - r * 0.2, r * 1.1, "sit", 1 if dx < 0 else -1, {"top": pc, "season": "summer"}, seed=i * 7 + off * 3 + (dx > 0),
                                    rim="#FFE8B8", light=-1))
            out.append(umbrella(x, y - r * 0.3, r, col, sh))
            out.append(mist(bx, by + 2, r * 0.9, r * 0.18, "#5A3A2A", f"{u}-us{i}{off}", 0.3))
    # right bank: shady garden wall, stone stair and giant bald cypresses
    out.append(f'<polygon points="{P(C.quad_x(14, 3, 60, 1, 6))}" fill="#7A6A52"/>')
    out.append(f'<polygon points="{P(C.quad_x(14, 3, 60, 5.4, 6))}" fill="#C9B08A"/>')
    out.append(blobs(40, 9, (440, 150, 610, 250), ["#3E6A3A", "#4E7A3E", "#2E4E2E"], r=(10, 26), opacity=(0.9, 1), squash=0.8))
    for Zt, sd, fol, nf, wk in ((40, 3, (60, 200), 40, 0.04), (24, 5, (10, 170), 44, 0.035), (12.5, 7, (-20, 120), 40, 0.03)):
        x, b = C(10.6, 1.0, Zt)
        h = C.f * 26 / Zt
        out.append(bald_cypress(x, b, min(h, 420), sd, top=-20, fol=fol, nf=nf, wk=wk))
    # terracotta planter with elephant ears on the right walkway
    px, pb = C(8.6, 1.0, 11)
    k = C.f / 11 / 100
    out.append(f'<g transform="translate({px:.1f} {pb:.1f}) scale({k:.3f})">'
               '<ellipse cx="0" cy="2" rx="46" ry="8" fill="#5A4030" opacity="0.4"/>'
               '<path d="M -34 -46 L 34 -46 L 26 0 L -26 0 Z" fill="#C2643E"/><path d="M 10 -46 L 34 -46 L 26 0 L 6 0 Z" fill="#8E4228" opacity="0.6"/>'
               '<rect x="-38" y="-54" width="76" height="10" rx="3" fill="#D9784E"/><rect x="-38" y="-54" width="76" height="3" fill="#F2A07A"/>'
               + "".join(f'<g transform="translate({dx} -54) rotate({a})"><path d="M 0 0 L 0 -{L * 0.55:.0f} M 0 -{L * 0.55:.0f} C {-L * 0.45:.0f} -{L * 0.5:.0f} {-L * 0.4:.0f} -{L * 1.05:.0f} 0 -{L:.0f} C {L * 0.4:.0f} -{L * 1.05:.0f} {L * 0.45:.0f} -{L * 0.5:.0f} 0 -{L * 0.55:.0f} Z" fill="{c}" stroke="#2E5A2A" stroke-width="2"/>'
                         f'<path d="M 0 -{L * 0.56:.0f} L 0 -{L * 0.98:.0f}" stroke="#B8DA7A" stroke-width="2"/></g>'
                         for dx, a, L, c in ((-14, -40, 80, "#3E7A34"), (12, 38, 86, "#4E8A3E"), (-4, -12, 100, "#5E9A44"), (4, 14, 92, "#3E7A34"), (-20, -62, 64, "#4E8A3E"), (22, 60, 66, "#5E9A44")))
               + '</g>')
    # stone arch footbridge at the bend
    Zb = 46
    x0, yw = C(-W, 0, Zb)
    x1, _ = C(W, 0, Zb)
    _, ytop = C(0, 4.4, Zb)
    _, ydeck = C(0, 3.5, Zb)
    _, yspring = C(0, 0.3, Zb)
    xl, _ = C(-15, 0, Zb)
    xr, _ = C(15, 0, Zb)
    out.append(f'<path d="M {xl:.1f} {ytop:.1f} L {xr:.1f} {ytop:.1f} L {xr:.1f} {yw:.1f} L {x1:.1f} {yw:.1f} Q {x1:.1f} {yspring - (yspring - ydeck) * 0.2:.1f} {(x0 + x1) / 2:.1f} {ydeck + 2:.1f} '
               f'Q {x0:.1f} {yspring - (yspring - ydeck) * 0.2:.1f} {x0:.1f} {yw:.1f} L {xl:.1f} {yw:.1f} Z" fill="url(#{u}-arch)"/>')
    out.append(f'<path d="M {x1:.1f} {yw:.1f} Q {x1:.1f} {yspring - (yspring - ydeck) * 0.2:.1f} {(x0 + x1) / 2:.1f} {ydeck + 2:.1f} Q {x0:.1f} {yspring - (yspring - ydeck) * 0.2:.1f} {x0:.1f} {yw:.1f}" fill="none" stroke="#9A7454" stroke-width="2.4"/>')
    out.append("".join(f'<line x1="{(x0 + x1) / 2 + (x1 - x0) * 0.55 * math.sin(a):.1f}" y1="{ydeck + 2 + (yw - ydeck) * (1 - math.cos(a)) * 0.9:.1f}" x2="{(x0 + x1) / 2 + (x1 - x0) * 0.62 * math.sin(a):.1f}" y2="{ydeck - 3 + (yw - ydeck) * (1 - math.cos(a)) * 0.9:.1f}" stroke="#A8845E" stroke-width="1.5"/>' for a in (-1.2, -0.8, -0.4, 0, 0.4, 0.8, 1.2)))
    out.append(f'<rect x="{xl:.1f}" y="{ytop - 4:.1f}" width="{xr - xl:.1f}" height="4" fill="#F6E6C8"/>')
    out.append(blobs(18, 31, (xl + 10, ytop - 12, xr - 10, ytop - 2), ["#E0458A", "#4E7A3E", "#F6B83A", "#3A6A34"], r=(2, 5), opacity=(0.9, 1)))
    for px, col in ((xl + 30, "#3E6AA8"), (xl + 38, "#E0C27A"), (xr - 34, "#C9574A")):
        out.append(figure(px, ytop - 3, 15, col, seed=int(px), pose="lean_back" if px > 300 else "stand_34", pal={"season": "summer"}))
    # reflections in the jade water: umbrellas, bridge, foliage and sun glints
    rnd = random.Random(8)
    _, yb_ = C(0, 0, Zb)
    out.append(f'<path d="M {x0:.1f} {yb_:.1f} Q {(x0 + x1) / 2:.1f} {yb_ + (yb_ - ydeck) * 0.8:.1f} {x1:.1f} {yb_:.1f} Z" fill="#E8D2A8" opacity="0.35"/>')
    # cypress shade on the right half of the river, sky glow down the middle
    out.append(f'<polygon points="{P([C(W, 0, 46), C(1.5, 0, 46), C(2.5, 0, 20), C(0.5, 0, 8), C(1.5, 0, 3), C(W, 0, 3)])}" fill="#1A4A40" opacity="0.4"/>')
    out.append(f'<polygon points="{P([C(-0.8, 0, 46), C(1.2, 0, 46), C(2.2, 0, 4), C(-1.8, 0, 4)])}" fill="#D9F0DC" opacity="0.1"/>')
    # wavering reflections of the umbrellas below the left coping
    for i, Z in enumerate((40, 32, 26, 21, 17, 13.5, 10.6, 8.4)):
        col = ucols[(i * 2) % len(ucols)][0]
        x, y = C(-W + 0.3, 0, Z)
        L = C.f * 2.6 / Z
        ww = C.f * 1.1 / Z
        rr = random.Random(i)
        for j in range(7):
            yy = y + L * (j + 0.3) / 7
            w_ = ww * rr.uniform(0.5, 1.1) * (1 - j / 10)
            out.append(f'<rect x="{x + rr.uniform(0, ww * 0.4):.1f}" y="{yy:.1f}" width="{w_:.1f}" height="{max(1.2, L / 16):.1f}" rx="1" fill="{col}" opacity="{0.55 - j * 0.06:.2f}"/>')
    for i in range(70):
        Z = 4.5 * 1.034 ** i
        if Z > 46:
            break
        X = rnd.uniform(-W + 0.5, W - 0.5)
        x, y = C(X, 0, Z)
        w = C.f * rnd.uniform(0.8, 2.4) / Z
        out.append(f'<path d="M {x - w / 2:.1f} {y:.1f} q {w / 4:.1f} {-max(1, C.f * 0.05 / Z):.1f} {w / 2:.1f} 0 t {w / 2:.1f} 0" fill="none" stroke="{rnd.choice(["#CDEFD8", "#FFF4D0", "#9AD2B6"])}" stroke-width="{max(1.2, C.f * 0.05 / Z):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.35, 0.75):.2f}"/>')
    # the river barge heading away toward the bridge, full of visitors, a guide at the tiller
    bz0, bz1, bx0, bx1 = 15, 26, 0.6, 3.9
    hull_side = C.quad_x(bx0, bz0, bz1, 0, 0.9)
    out.append(f'<polygon points="{P([C(bx0 - 0.2, 0, bz0), C(bx1 + 0.2, 0, bz0), C(bx1 + 1.4, 0, bz0 - 6), C(bx0 - 1.4, 0, bz0 - 6)])}" fill="#BFE6D0" opacity="0.2"/>')
    for dx in (-1, 1):
        xs_ = bx0 if dx < 0 else bx1
        pts = [C(xs_ + dx * 2.2 * (t / 6) ** 0.8, 0, bz0 - t) for t in (0, 1, 2, 3, 4.5, 6, 7.5)]
        for j, (p_, q_) in enumerate(zip(pts, pts[1:])):
            out.append(f'<line x1="{p_[0]:.1f}" y1="{p_[1]:.1f}" x2="{q_[0]:.1f}" y2="{q_[1]:.1f}" stroke="#EAF6EE" stroke-width="{2.4 - j * 0.15:.1f}" stroke-linecap="round" opacity="{0.75 - j * 0.11:.2f}"/>')
    out.append(f'<polygon points="{P(C.quad_z(bz0, bx0, bx1, 0, 0.9))}" fill="#1E6A8A"/>')
    out.append(f'<polygon points="{P(hull_side)}" fill="#2A86A8"/>')
    out.append(f'<polygon points="{P([C(bx0, 0.9, bz0), C(bx1, 0.9, bz0), C(bx1, 0.9, bz1), C(bx0, 0.9, bz1)])}" fill="#E8DCC8"/>')
    out.append(f'<polygon points="{P(C.quad_z(bz0, bx0, bx1, 0.62, 0.78))}" fill="#F6B83A"/><polygon points="{P(C.quad_x(bx0, bz0, bz1, 0.62, 0.78))}" fill="#F6B83A"/>')
    rows = []
    rp = random.Random(3)
    for zr in [bz1 - 0.9 - i * 1.0 for i in range(10)]:
        for xr_ in (bx0 + 0.6, bx0 + 1.5, bx0 + 2.4, bx0 + 3.0):
            x, y = C(xr_, 0.9, zr)
            s_ = C.f / zr
            rows.append((zr, F.person(x, y, s_ * 1.45, "sit_back", 1, {"top": rp.choice(["#E8423E", "#F6EEDC", "#3A7AC8", "#F6B83A", "#4E9AA2"]), "season": "summer"},
                                      seed=int(zr * 10 + xr_ * 3), rim="#FFF0C8", light=-1, shadow=0)))
    out.append("".join(r_ for _, r_ in sorted(rows, key=lambda t: -t[0])))
    gx, gy = C(bx1 - 0.6, 0.9, bz0 + 0.4)
    out.append(figure(gx, gy, C.f * 1.75 / (bz0 + 0.4), "#F6EEDC", seed=11, pose="stand_back", pal={"hat_kind": "cap", "hat": "#2A5A7A", "form": "m"}))
    out.append(f'<polygon points="{P(C.quad_z(bz0, bx0, bx1, 0.9, 1.25))}" fill="#1E6A8A"/>')
    # a pair of mallards paddling by
    for X, Z, drake in ((-3.6, 8.6, True), (-2.5, 9.6, False)):
        x, y = C(X, 0, Z)
        k = C.f / Z / 40
        body = "#7A6A5A" if drake else "#9A7A52"
        head = "#1E6A3A" if drake else "#8A6A42"
        out.append(f'<g transform="translate({x:.1f} {y:.1f}) scale({k:.3f})">'
                   '<ellipse cx="2" cy="3" rx="24" ry="4" fill="#1A4A40" opacity="0.4"/>'
                   f'<path d="M -20 0 Q -24 -6 -18 -10 Q -8 -14 8 -12 Q 14 -12 16 -8 Q 18 -2 12 0 Z" fill="{body}"/>'
                   '<path d="M -18 -9 Q -6 -12 6 -10 Q 0 -6 -12 -6 Z" fill="#FFFFFF" opacity="0.35"/>'
                   f'<path d="M 9 -11 Q 8 -20 12 -24 Q 18 -27 20 -21 Q 21 -17 18 -14 Z" fill="{head}"/>'
                   '<path d="M 19 -21 L 26 -19 L 19 -17 Z" fill="#E8B83A"/><circle cx="16" cy="-21" r="1.2" fill="#111"/>'
                   + ('<path d="M 10 -13 Q 14 -14 18 -13" stroke="#FFFFFF" stroke-width="1.6" fill="none"/>' if drake else "")
                   + '<path d="M -22 1 Q -2 4 18 1" stroke="#EAF6EE" stroke-width="1.6" fill="none" opacity="0.8"/></g>')
    # overhead: strings of papel picado across the river and the cypress canopy at top right
    out.append(papel(-20, 52, 640, 44, 22, 22, 2, ["#E8423E", "#F6B83A", "#2EA6A0", "#E85A9A", "#F07A2E", "#7A5AC8", "#5AB85A"], size=0.95))
    out.append(papel(120, 128, 500, 122, 10, 16, 3, ["#F6B83A", "#E85A9A", "#3A7AC8", "#F07A2E", "#5AB85A", "#E8423E"], size=0.85))
    # warm afternoon light raking across the walkway
    out.append(f'<polygon points="{P([C(W, 1.01, 5), C(14, 1.01, 5), C(14, 1.01, 9), C(W, 1.01, 11)])}" fill="#FFE9B0" opacity="0.25"/>')
    return "\n".join(out)


# ================================================================ SANTA FE (adobe lane, alpenglow on the Sangre de Cristo)
def adobe_block(x0, x1, ytop, ybase, fill, seed, shade=None, round_r=8):
    """Soft-cornered adobe mass with a slightly wavy hand-plastered parapet."""
    rnd = random.Random(seed)
    n = max(3, int((x1 - x0) / 30))
    top = [(x0 + (x1 - x0) * i / n, ytop + rnd.uniform(-1.5, 1.5)) for i in range(n + 1)]
    d = f"M {x0:.1f} {ybase:.1f} L {x0:.1f} {ytop + round_r:.1f} Q {x0:.1f} {ytop:.1f} {x0 + round_r:.1f} {top[0][1]:.1f} "
    for x, y in top[1:-1]:
        d += f"L {x:.1f} {y:.1f} "
    d += f"L {x1 - round_r:.1f} {top[-1][1]:.1f} Q {x1:.1f} {ytop:.1f} {x1:.1f} {ytop + round_r:.1f} L {x1:.1f} {ybase:.1f} Z"
    out = f'<path d="{d}" fill="{fill}"/>'
    if shade:
        out += f'<path d="{d}" fill="{shade}"/>'
    return out


def vigas(x0, x1, y, r, n, end="#C9925E", grain="#7A4A2E", shadow="#8A4A34"):
    out = []
    for i in range(n):
        x = x0 + (x1 - x0) * (i + 0.5) / n
        out.append(f'<ellipse cx="{x + r * 0.9:.1f}" cy="{y + r * 0.5:.1f}" rx="{r * 1.4:.1f}" ry="{r * 0.8:.1f}" fill="{shadow}" opacity="0.35"/>'
                   f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{end}"/><circle cx="{x - r * 0.15:.1f}" cy="{y - r * 0.1:.1f}" r="{r * 0.55:.1f}" fill="none" stroke="{grain}" stroke-width="{max(1, r * 0.18):.1f}" opacity="0.6"/>')
    return "".join(out)


def ristra(x, y, L, seed, w=None):
    """Hanging string of dried red chiles: a tapered braid of overlapping glossy pods."""
    rnd = random.Random(seed)
    w = w or L * 0.16
    out = [f'<line x1="{x:.1f}" y1="{y - 6:.1f}" x2="{x:.1f}" y2="{y + 2:.1f}" stroke="#8A6A3A" stroke-width="1.6"/>']
    n = int(L / 3.2)
    for i in range(n):
        t = i / n
        yy = y + t * L
        ww = w * (1 - 0.55 * t) * (0.8 + 0.4 * math.sin(i * 1.7))
        for side in (-1, 1):
            a = side * rnd.uniform(25, 60)
            col = rnd.choice(["#B81E1E", "#A01818", "#C8301E", "#8E1414"])
            out.append(f'<ellipse cx="{x + side * ww * 0.45:.1f}" cy="{yy:.1f}" rx="{w * 0.22:.1f}" ry="{w * 0.5:.1f}" transform="rotate({a:.0f} {x + side * ww * 0.45:.1f} {yy:.1f})" fill="{col}"/>')
        if i % 2 == 0:
            out.append(f'<ellipse cx="{x - ww * 0.25:.1f}" cy="{yy - w * 0.15:.1f}" rx="{w * 0.08:.1f}" ry="{w * 0.25:.1f}" fill="#FF8A6A" opacity="0.6"/>')
    out.append(f'<path d="M {x - 2:.1f} {y + L:.1f} l 2 6 l 2 -6" fill="#6A8A3A"/>')
    return "".join(out)


def hollyhock(x, base, h, col, seed):
    rnd = random.Random(seed)
    out = [f'<path d="M {x:.1f} {base:.1f} q {rnd.uniform(-3, 3):.1f} {-h / 2:.1f} {rnd.uniform(-2, 2):.1f} {-h:.1f}" stroke="#4E6A34" stroke-width="2" fill="none"/>']
    for i in range(7):
        t = 0.25 + i * 0.11
        yy = base - h * t
        r = (1 - t) * 7 + 2.4
        side = -1 if i % 2 else 1
        out.append(f'<ellipse cx="{x + side * 4:.1f}" cy="{yy + 3:.1f}" rx="5" ry="2.4" fill="#5A7A3A" transform="rotate({side * 25} {x + side * 4:.1f} {yy + 3:.1f})"/>')
        out.append(f'<circle cx="{x + side * r * 0.3:.1f}" cy="{yy:.1f}" r="{r:.1f}" fill="{col}"/><circle cx="{x + side * r * 0.3:.1f}" cy="{yy:.1f}" r="{r * 0.35:.1f}" fill="#FFE8A8" opacity="0.8"/>')
    return "".join(out)


def santa_fe():
    u = "pd-santafe"
    out = [defs(
        lg(f"{u}-sky", [(0, "#2C3E7A"), (0.35, "#6A6AA6"), (0.6, "#C98AAE"), (0.78, "#F2B2A6"), (0.9, "#D9B6C6"), (1, "#9AA6CC")], 0, 40, 0, 270, units="userSpaceOnUse"),
        lg(f"{u}-peak", [(0, "#F7A2A6"), (0.5, "#D9708E"), (1, "#8A4E7E")]),
        lg(f"{u}-foot", [(0, "#7A5A86"), (1, "#5A4670")]),
        lg(f"{u}-wallL", [(0, "#F0A672"), (1, "#C9744E")], 0, 0, 1, 0),
        lg(f"{u}-wallR", [(0, "#D8865E"), (1, "#E9A070")], 0, 0, 1, 0),
        lg(f"{u}-ground", [(0, "#D49A72"), (1, "#9E6448")], 0, 290, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-door", [(0, "#2FB0A8"), (1, "#1A7A7A")], 0, 0, 1, 0),
        lg(f"{u}-win", [(0, "#FFE2A0"), (1, "#F2A050")]),
        lg(f"{u}-church", [(0, "#F2B486"), (1, "#C97E5A")], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(26, 8, (60, 44, 560, 120), "#FFF6E8", r=(0.6, 1.3), opacity=(0.4, 0.9)))
    out.append('<circle cx="170" cy="84" r="2.4" fill="#FFF8E8"/>')
    out.append(glow(170, 84, 10, "#FFF8E8", f"{u}-venus", 0.7))
    # full moon rising in the Belt of Venus over the range
    out.append(glow(408, 166, 70, "#FFE8D8", f"{u}-mg", 0.5))
    out.append('<circle cx="408" cy="166" r="17" fill="#FFF2E2"/><circle cx="403" cy="161" r="4" fill="#F2DCD0"/><circle cx="413" cy="171" r="3" fill="#F2DCD0"/><circle cx="414" cy="160" r="2" fill="#F2DCD0"/>')
    out.append('<g fill="#F7C0B6" opacity="0.6">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="3"/>' for x, y, w in ((110, 148, 70), (300, 132, 90), (520, 140, 60))) + "</g>")
    # Sangre de Cristo range glowing pink in the last light: bare summits lit, forested flanks in violet shade
    poly, far = ridge_poly([(-10, 222), (50, 196), (120, 170), (176, 182), (236, 150), (300, 172), (360, 160), (430, 190), (500, 178), (560, 200), (610, 192)], 14, base=300, amp=10, fill=f"url(#{u}-peak)")
    out.append(poly)
    clipid = f"{u}-pk"
    out.append(f'<clipPath id="{clipid}"><polygon points="{P(far + [(610, 300), (-10, 300)])}"/></clipPath>')
    rr = random.Random(12)
    gullies = []
    for _ in range(46):
        x = rr.uniform(-10, 610)
        y0 = (y_on(far, x) or 200) + rr.uniform(2, 10)
        L = rr.uniform(16, 48)
        dx = rr.uniform(-6, 6)
        gullies.append(f'<path d="M {x:.1f} {y0:.1f} q {dx:.1f} {L * 0.5:.1f} {dx * 1.6:.1f} {L:.1f}" stroke="{rr.choice(["#B0607E", "#9A5280"])}" stroke-width="{rr.uniform(1.5, 3):.1f}" fill="none" stroke-linecap="round" opacity="{rr.uniform(0.3, 0.6):.2f}"/>')
    forest = blobs(420, 19, (-10, 214, 610, 300), ["#5A3E66", "#4E3A5E", "#664876"], r=(2, 4.5), opacity=(0.75, 1), squash=0.8)
    out.append(f'<g clip-path="url(#{clipid})">' + "".join(gullies)
               + f'<path d="M -10 230 Q 120 214 250 222 Q 380 230 610 212 L 610 300 L -10 300 Z" fill="#5A3E66" opacity="0.55"/>' + forest + "</g>")
    out.append(f'<polyline points="{P(far)}" fill="none" stroke="#FFD6C8" stroke-width="2" opacity="0.85"/>')
    out.append(mist(300, 262, 380, 26, "#C98AAE", f"{u}-haze", 0.45))
    poly, foot = ridge_poly([(-10, 262), (90, 252), (200, 260), (300, 248), (420, 258), (520, 250), (610, 258)], 15, base=300, amp=5, fill=f"url(#{u}-foot)")
    out.append(poly)
    out.append(blobs(140, 17, (-10, 254, 610, 294), ["#3E4A4A", "#4A5450", "#36423E"], r=(2, 4.5), opacity=(0.7, 1), squash=0.7))
    # the old town in the middle distance: low adobes, warm windows, a mission chapel with its bell tower
    rnd = random.Random(3)
    for x0, w, h, col in ((150, 60, 22, "#D99A72"), (205, 40, 30, "#E2A57A"), (360, 50, 26, "#D08E68"), (405, 46, 18, "#E0A47A"), (330, 34, 18, "#C98862")):
        out.append(adobe_block(x0, x0 + w, 292 - h, 296, col, x0, round_r=4))
        out.append(vigas(x0 + 4, x0 + w - 4, 292 - h + 5, 1.6, int(w / 8), shadow="#7A3E2E"))
        for _ in range(2):
            wx = rnd.uniform(x0 + 6, x0 + w - 12)
            out.append(f'<rect x="{wx:.1f}" y="{292 - h * 0.55:.1f}" width="6" height="7" fill="#FFD48A"/>')
    cx = 286
    out.append(adobe_block(cx - 30, cx + 30, 232, 296, f"url(#{u}-church)", 7, round_r=6))
    out.append(adobe_block(cx - 16, cx + 16, 204, 236, f"url(#{u}-church)", 8, round_r=5))
    out.append(adobe_block(cx - 10, cx + 10, 186, 208, f"url(#{u}-church)", 9, round_r=4))
    out.append(f'<path d="M {cx - 4} 194 Q {cx} 186 {cx + 4} 194 L {cx + 4} 204 L {cx - 4} 204 Z" fill="#5A3A2E"/><circle cx="{cx}" cy="199" r="2.4" fill="#C9A24A"/>')
    out.append(f'<rect x="{cx - 1.2}" y="168" width="2.4" height="18" fill="#5A3A2E"/><rect x="{cx - 6}" y="173" width="12" height="2.4" fill="#5A3A2E"/>')
    out.append(f'<path d="M {cx - 9} 296 L {cx - 9} 266 Q {cx} 254 {cx + 9} 266 L {cx + 9} 296 Z" fill="#6A3E2A"/><path d="M {cx - 9} 266 Q {cx} 254 {cx + 9} 266" fill="none" stroke="#F6D2B0" stroke-width="2"/>')
    out.append(f'<rect x="{cx - 5}" y="214" width="10" height="12" rx="5" fill="#FFD48A"/>')
    out.append(vigas(cx - 28, cx + 28, 240, 1.8, 8, shadow="#7A3E2E"))
    out.append(f'<rect x="{cx + 18}" y="232" width="12" height="64" fill="#8A4E3A" opacity="0.25"/>')
    # the lane: packed earth and brick, curving toward the chapel
    out.append(f'<path d="M -10 300 L 610 300 L 610 444 L -10 444 Z" fill="url(#{u}-ground)"/>')
    out.append(f'<path d="M 268 298 Q 250 330 214 360 Q 170 400 110 444 L 520 444 Q 420 400 360 360 Q 316 330 304 298 Z" fill="#B87A5A" opacity="0.6"/>')
    rb = random.Random(5)
    for row in range(14):
        t = row / 13
        y = 302 + (444 - 302) * t ** 1.6
        xl = 268 - (268 - 110) * t ** 1.3
        xr = 304 + (520 - 304) * t ** 1.3
        out.append(f'<line x1="{xl:.1f}" y1="{y:.1f}" x2="{xr:.1f}" y2="{y:.1f}" stroke="#8E5A44" stroke-width="{0.8 + t * 1.2:.1f}" opacity="0.45"/>')
        nb = int(4 + t * 10)
        for j in range(nb):
            xx = xl + (xr - xl) * (j + (row % 2) * 0.5) / nb
            nxt = y + (444 - 302) * (((row + 1) / 13) ** 1.6 - t ** 1.6)
            out.append(f'<line x1="{xx:.1f}" y1="{y:.1f}" x2="{xx:.1f}" y2="{min(444, nxt):.1f}" stroke="#8E5A44" stroke-width="{0.8 + t:.1f}" opacity="0.35"/>')
    out.append(dots(160, 6, (-10, 300, 610, 444), "#7A4A34", r=(0.6, 1.8), opacity=(0.2, 0.5)))
    # right: adobe garden wall, coyote fence, turquoise gate, hollyhocks and a pinon pine
    out.append(conifer(560, 300, 150, "#3E5A44", 4, width=0.75, light="#7A8A5A"))
    out.append(blobs(30, 7, (490, 160, 610, 290), ["#3E5A44", "#4E6A4A", "#2E4A3A"], r=(10, 22), opacity=(0.95, 1), squash=0.75))
    out.append(blobs(16, 8, (500, 160, 600, 230), ["#7A8A5A", "#8E9A62"], r=(6, 12), opacity=(0.6, 0.8), squash=0.6))
    # coyote fence of rough latillas standing on the ground, then the garden wall with its gate
    rf = random.Random(9)
    for i in range(22):
        x = 372 + i * 5.2
        top = 262 + rf.uniform(-6, 6)
        out.append(f'<path d="M {x:.1f} 334 L {x + rf.uniform(-1.2, 1.2):.1f} {top:.1f}" stroke="{rf.choice(["#8A6A4E", "#7A5A42", "#9A7A5A", "#6E5038"])}" stroke-width="4.8" stroke-linecap="round"/>')
        out.append(f'<path d="M {x - 1.4:.1f} 330 L {x - 1:.1f} {top + 4:.1f}" stroke="#C9A47E" stroke-width="1.2" opacity="0.6"/>')
    out.append('<line x1="368" y1="280" x2="488" y2="278" stroke="#5A4232" stroke-width="2.4"/><line x1="368" y1="312" x2="488" y2="312" stroke="#5A4232" stroke-width="2.4"/>')
    out.append(adobe_block(482, 620, 262, 336, f"url(#{u}-wallR)", 11, round_r=10))
    out.append(f'<rect x="482" y="326" width="140" height="10" fill="#9A5A3E" opacity="0.3"/>')
    out.append(f'<path d="M 500 336 L 500 296 Q 522 276 544 296 L 544 336 Z" fill="url(#{u}-door)"/>')
    out.append('<path d="M 500 296 Q 522 276 544 296" fill="none" stroke="#7A4A2E" stroke-width="4"/>')
    out.append("".join(f'<line x1="{x}" y1="298" x2="{x}" y2="336" stroke="#156A6A" stroke-width="1.6"/>' for x in (511, 522, 533)))
    out.append('<circle cx="537" cy="318" r="1.8" fill="#E9C46A"/>')
    for x, c, sd in ((384, "#E8506E", 1), (404, "#F7F0E6", 2), (426, "#C23A6A", 3), (452, "#E8506E", 4), (470, "#F7F0E6", 5)):
        out.append(hollyhock(x, 340, 64 + sd * 3, c, sd))
    out.append(grass(50, 3, (370, 330, 490, 342), ["#6A7A3A", "#8A8A4A"], h=(5, 10)))
    # left: the big adobe with its portal, ristras, a deep-set window and the turquoise door
    out.append(adobe_block(-20, 252, 128, 380, f"url(#{u}-wallL)", 21, round_r=12))
    rs = random.Random(13)
    out.append("".join(f'<ellipse cx="{rs.uniform(-10, 240):.1f}" cy="{rs.uniform(140, 370):.1f}" rx="{rs.uniform(6, 18):.1f}" ry="{rs.uniform(3, 8):.1f}" fill="{rs.choice(["#F7B686", "#D07A54"])}" opacity="0.3"/>' for _ in range(40)))
    out.append(vigas(0, 244, 142, 4.2, 9))
    out.append(f'<path d="M 236 128 L 252 128 L 252 380 L 236 380 Z" fill="#B0603E" opacity="0.4"/>')
    out.append('<path d="M 60 130 l 0 -6 l 20 0 l 0 6 Z" fill="#8A5A3A"/><path d="M 70 130 l 0 16" stroke="#8A5A3A" stroke-width="3"/>')
    # kiva-style chimney
    out.append(adobe_block(184, 214, 102, 130, f"url(#{u}-wallL)", 22, round_r=8))
    out.append('<rect x="190" y="98" width="18" height="6" rx="3" fill="#B0603E"/>')
    # deep-set window with a warm glow and a little sill
    out.append('<rect x="34" y="186" width="58" height="64" rx="6" fill="#A85A3A"/><rect x="40" y="192" width="46" height="54" fill="url(#pd-santafe-win)"/>')
    out.append('<path d="M 63 192 L 63 246 M 40 219 L 86 219" stroke="#4A6A8A" stroke-width="3"/><rect x="30" y="250" width="66" height="6" rx="3" fill="#F7C69A"/>')
    out.append(glow(63, 220, 60, "#FFD48A", f"{u}-wg", 0.35))
    # portal: wooden posts, carved corbels, a viga roof, and its shadow
    out.append('<rect x="88" y="252" width="168" height="128" fill="#7A3E2A" opacity="0.32"/>')
    out.append('<rect x="80" y="244" width="182" height="10" fill="#6E4A32"/><rect x="80" y="244" width="182" height="3" fill="#B08A62"/>')
    for x in (90, 172, 250):
        out.append(f'<rect x="{x - 4}" y="254" width="8" height="126" fill="#7A563C"/><rect x="{x - 4}" y="254" width="3" height="126" fill="#A47E5A"/>')
        out.append(f'<path d="M {x - 16} 254 L {x + 16} 254 L {x + 13} 260 Q {x + 8} 258 {x + 6} 264 L {x - 6} 264 Q {x - 8} 258 {x - 13} 260 Z" fill="#6E4A32"/>')
    out.append(vigas(84, 262, 239, 3, 9, end="#B48A5E"))
    # turquoise door with its weathered frame
    out.append('<rect x="112" y="282" width="52" height="98" fill="#7A4A2E"/>')
    out.append(f'<rect x="117" y="287" width="42" height="93" fill="url(#{u}-door)"/>')
    out.append('<g fill="none" stroke="#156A6A" stroke-width="2"><rect x="122" y="294" width="14" height="34"/><rect x="140" y="294" width="14" height="34"/><rect x="122" y="336" width="14" height="36"/><rect x="140" y="336" width="14" height="36"/></g>')
    out.append('<path d="M 118 288 L 118 380" stroke="#7FE0D6" stroke-width="2" opacity="0.6"/><circle cx="153" cy="334" r="2.2" fill="#E9C46A"/>')
    out.append('<path d="M 106 282 L 170 282" stroke="#5A3A24" stroke-width="5"/>')
    # ristras hanging from the portal beam
    for x, L, sd in ((100, 70, 1), (196, 84, 2), (226, 62, 3), (262, 50, 4)):
        out.append(ristra(x, 256, L, sd))
    # blue pots, a bench and a sleeping dog in the portal
    out.append('<path d="M 186 380 L 186 352 L 236 352 L 236 380" fill="none" stroke="#5A3A24" stroke-width="4"/><rect x="182" y="348" width="58" height="6" rx="2" fill="#8A603E"/>')
    out.append('<path d="M 64 380 L 60 352 L 84 352 L 80 380 Z" fill="#2E6AA8"/><rect x="58" y="348" width="28" height="6" rx="2" fill="#4A8AC8"/>')
    out.append(blobs(12, 4, (56, 326, 88, 350), ["#5A8A3A", "#E8506E", "#F2C14E"], r=(3, 6), opacity=(0.9, 1)))
    out.append('<g transform="translate(212 381)"><ellipse cx="0" cy="0" rx="20" ry="3" fill="#5A2E1E" opacity="0.35"/>'
               '<path d="M -18 0 Q -20 -14 -4 -15 Q 12 -16 16 -6 L 17 0 Z" fill="#E6CFA8"/><path d="M -18 0 Q -24 -4 -20 -9" stroke="#E6CFA8" stroke-width="3.4" fill="none" stroke-linecap="round"/>'
               '<path d="M 10 -8 Q 14 -16 22 -14 Q 28 -12 28 -6 Q 28 -1 20 0 L 10 0 Z" fill="#EAD6B2"/><path d="M 16 -14 Q 13 -8 17 -5 Q 20 -10 19 -14 Z" fill="#B48E62"/>'
               '<path d="M 22 -7 q 3 1 5 -1" stroke="#5A3A2A" stroke-width="1.5" fill="none" stroke-linecap="round"/><circle cx="28" cy="-6" r="1.5" fill="#3A2A22"/>'
               '<path d="M -10 -12 Q 0 -16 10 -11" stroke="#FFF2DC" stroke-width="2" fill="none" opacity="0.7"/></g>')
    out.append('<rect x="-10" y="380" width="272" height="6" fill="#6E3E2A" opacity="0.35"/>')
    # a couple strolling up the lane toward the chapel, their long shadows reaching ahead of them
    for x, b, h, col, sd in ((318, 336, 30, "#2E5A8A", 1), (332, 337, 27, "#B8463E", 2)):
        out.append(f'<path d="M {x - 3} {b} L {x + 6} {b - 26} L {x + 10} {b - 25} L {x + 3} {b} Z" fill="#7A4434" opacity="0.35"/>')
        pass
    out.append(F.couple(325, 336.5, 29, palette={"top": "#2E5A8A", "season": "any"}, seed=31, rim="#FFD4A0", light=-1, gap=46))
    # an old iron street lamp
    out.append('<path d="M 362 350 L 362 268" stroke="#2E2A2A" stroke-width="3.4"/><rect x="356" y="256" width="12" height="13" fill="#2E2A2A"/><rect x="358.2" y="258.6" width="7.6" height="8" fill="#FFE2A0"/>'
               '<path d="M 354 256 L 362 249 L 370 256 Z" fill="#2E2A2A"/><path d="M 358 350 L 366 350 L 370 355 L 354 355 Z" fill="#2E2A2A"/>')
    out.append(glow(362, 262, 24, "#FFE2A0", f"{u}-lamp", 0.7))
    # chamisa in autumn bloom and a few sage clumps along the right edge of the lane
    rc = random.Random(31)
    for x, y, r in ((448, 400, 26), (520, 380, 22), (580, 420, 30), (404, 430, 18), (490, 432, 20)):
        out.append(blobs(16, int(x), (x - r, y - r * 0.8, x + r, y), ["#7A8A5A", "#8E9A6A", "#6A7A4A"], r=(r * 0.18, r * 0.32), opacity=(0.9, 1), squash=0.7))
        out.append(blobs(14, int(x) + 1, (x - r * 0.8, y - r * 1.0, x + r * 0.8, y - r * 0.4), ["#F2C434", "#E8B020", "#FFD85A"], r=(r * 0.1, r * 0.2), opacity=(0.9, 1), squash=0.8))
        out.append(f'<ellipse cx="{x + r * 0.3:.1f}" cy="{y + 2:.1f}" rx="{r:.1f}" ry="{r * 0.18:.1f}" fill="#7A4434" opacity="0.3"/>')
    return "\n".join(out)


# ================================================================ SEDONA (Cathedral Rock at sunset from the trail)
def column(cx, top, w, base, seed, taper=0.12, cap=0.5):
    """Sandstone spire / fin: slightly irregular tapered column with a rounded, eroded cap."""
    rnd = random.Random(seed)
    tw = w * (1 - taper)
    n = 7
    left = [(cx - tw / 2 - (w - tw) / 2 * i / n + rnd.uniform(-w * 0.04, w * 0.04), top + w * cap * 0.6 + (base - top - w * cap * 0.6) * i / n) for i in range(n + 1)]
    right = [(cx + tw / 2 + (w - tw) / 2 * i / n + rnd.uniform(-w * 0.04, w * 0.04), top + w * cap * 0.6 + (base - top - w * cap * 0.6) * i / n) for i in range(n + 1)]
    d = f"M {left[-1][0]:.1f} {base:.1f} " + "".join(f"L {x:.1f} {y:.1f} " for x, y in left[::-1])
    d += f"Q {cx - tw * 0.45:.1f} {top:.1f} {cx + rnd.uniform(-w * 0.1, w * 0.1):.1f} {top:.1f} Q {cx + tw * 0.45:.1f} {top:.1f} {right[0][0]:.1f} {right[0][1]:.1f} "
    d += "".join(f"L {x:.1f} {y:.1f} " for x, y in right[1:]) + "Z"
    return d


def juniper(x, base, h, seed, dark="#2E4A3A", mid="#4E6A4E", lit="#9AA86A", trunk="#5A3A2A", rim=None):
    """Utah juniper: short twisted trunk, irregular clumpy blue-green crown, warm light on the sun side."""
    rnd = random.Random(seed)
    w = h * rnd.uniform(0.9, 1.3)
    out = [f'<path d="M {x - h * 0.05:.1f} {base:.1f} Q {x + h * 0.08:.1f} {base - h * 0.2:.1f} {x - h * 0.04:.1f} {base - h * 0.42:.1f} L {x + h * 0.04:.1f} {base - h * 0.42:.1f} '
           f'Q {x + h * 0.16:.1f} {base - h * 0.2:.1f} {x + h * 0.06:.1f} {base:.1f} Z" fill="{trunk}"/>',
           f'<path d="M {x:.1f} {base - h * 0.3:.1f} q {h * 0.15:.1f} {-h * 0.05:.1f} {h * 0.22:.1f} {-h * 0.2:.1f}" stroke="{trunk}" stroke-width="{max(1.5, h * 0.04):.1f}" fill="none"/>']
    clumps = []
    for _ in range(int(9 + h / 6)):
        cx = x + rnd.uniform(-w / 2, w / 2)
        t = abs(cx - x) / (w / 2)
        cy = base - h * (0.5 + 0.42 * (1 - t ** 2) * rnd.uniform(0.6, 1.0))
        r = h * rnd.uniform(0.1, 0.18)
        clumps.append((cx, cy, r))
    out.append("".join(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r * 1.2:.1f}" ry="{r:.1f}" fill="{dark}"/>' for cx, cy, r in clumps))
    out.append("".join(f'<ellipse cx="{cx - r * 0.2:.1f}" cy="{cy - r * 0.2:.1f}" rx="{r * 0.9:.1f}" ry="{r * 0.7:.1f}" fill="{mid}"/>' for cx, cy, r in clumps))
    out.append("".join(f'<path d="M {cx - r * 1.05:.1f} {cy:.1f} Q {cx - r * 0.9:.1f} {cy - r * 0.8:.1f} {cx - r * 0.1:.1f} {cy - r * 0.85:.1f}" fill="none" stroke="{rim or lit}" stroke-width="{max(1.5, r * 0.22):.1f}" stroke-linecap="round" opacity="0.7"/>' for cx, cy, r in clumps if cx < x + w * 0.05))
    # feathery scale-leaf texture and a few dusty-blue berries
    out.append(f'<g stroke="{dark}" stroke-width="1.2" opacity="0.5" stroke-linecap="round">' + "".join(
        f'<line x1="{cx + rnd.uniform(-r, r):.1f}" y1="{cy + rnd.uniform(-r * 0.5, r * 0.5):.1f}" x2="{cx + rnd.uniform(-r, r):.1f}" y2="{cy + rnd.uniform(-r * 0.2, r * 0.8):.1f}"/>' for cx, cy, r in clumps if h > 40) + "</g>")
    out.append(dots(int(h / 8), seed, (x - w / 3, base - h * 0.85, x + w / 3, base - h * 0.5), "#8A9AC0", r=(0.9, 1.5), opacity=(0.5, 0.8)))
    return "".join(out)


def prickly_pear(x, base, s, seed):
    rnd = random.Random(seed)
    pads = [(0, -12, 9, 12, 0)]
    for i in range(5):
        px, py, rx, ry, a = rnd.choice(pads)
        ang = rnd.uniform(-60, 60)
        nx = px + math.sin(math.radians(ang)) * ry * 1.4
        ny = py - math.cos(math.radians(ang)) * ry * 1.4
        pads.append((nx, ny, rx * 0.85, ry * 0.85, ang))
    out = [f'<g transform="translate({x:.1f} {base:.1f}) scale({s:.2f})">']
    for px, py, rx, ry, a in pads:
        out.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" transform="rotate({a:.0f} {px:.1f} {py:.1f})" fill="#5E8A4A"/>'
                   f'<ellipse cx="{px - rx * 0.3:.1f}" cy="{py - ry * 0.2:.1f}" rx="{rx * 0.45:.1f}" ry="{ry * 0.6:.1f}" transform="rotate({a:.0f} {px:.1f} {py:.1f})" fill="#9ABA6A" opacity="0.6"/>')
        out.append("".join(f'<circle cx="{px + rnd.uniform(-rx, rx) * 0.6:.1f}" cy="{py + rnd.uniform(-ry, ry) * 0.6:.1f}" r="0.9" fill="#F2E6B8"/>' for _ in range(4)))
    for px, py, rx, ry, a in pads[2:5]:
        out.append(f'<ellipse cx="{px:.1f}" cy="{py - ry:.1f}" rx="2.6" ry="3.4" fill="#C2305A"/>')
    out.append("</g>")
    return "".join(out)


def sedona():
    u = "pd-sedona"
    out = [defs(
        lg(f"{u}-sky", [(0, "#1E3A78"), (0.35, "#3E62A8"), (0.62, "#8E8AC0"), (0.8, "#E8A0A8"), (1, "#F6C49A")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-rock", [(0, "#FF9A54"), (0.45, "#E8582E"), (0.7, "#B23A2E"), (1, "#6E2A3A")], 0, 0, 1, 0),
        lg(f"{u}-rockb", [(0, "#E86A3A"), (1, "#8A3434")], 0, 0, 1, 0),
        lg(f"{u}-rim", [(0, "#D9A0A6"), (1, "#B87A8E")]),
        lg(f"{u}-ground", [(0, "#B4553A"), (1, "#7A3428")], 0, 290, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-trail", [(0, "#E8865A"), (1, "#C8603E")], 0, 290, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-butte", [(0, "#F08A5A"), (0.6, "#C24E3A"), (1, "#7A3040")], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    # long strands of cloud lit pink-gold from below by the sun setting behind us
    rc = random.Random(4)
    for cx, cy, w in ((130, 104, 170), (440, 82, 200), (500, 150, 110), (210, 158, 90)):
        for _ in range(9):
            x = cx + rc.uniform(-w / 2, w / 2) * 0.7
            y = cy + rc.uniform(-5, 5)
            rx = rc.uniform(0.18, 0.4) * w
            ry = rc.uniform(3, 7)
            out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#8A78B0" opacity="0.55"/>'
                       f'<ellipse cx="{x + 4:.1f}" cy="{y + ry * 0.5:.1f}" rx="{rx * 0.85:.1f}" ry="{ry * 0.5:.1f}" fill="#FFB89A" opacity="0.7"/>')
    # Mogollon Rim, far and violet
    poly, rim = ridge_poly([(-10, 246), (60, 238), (64, 228), (180, 226), (186, 240), (300, 244), (420, 236), (424, 226), (520, 224), (528, 236), (610, 240)], 4, base=300, amp=2, depth=3, fill=f"url(#{u}-rim)")
    out.append(poly)
    out.append(f'<polyline points="{P(rim)}" fill="none" stroke="#F6C4B6" stroke-width="1.5" opacity="0.8"/>')
    out.append(mist(300, 270, 360, 30, "#E8A0A8", f"{u}-haze", 0.5))
    # a stepped butte on the left (lit face, shadowed right flank, ledges)
    butte = [(-10, 300), (-10, 236), (14, 232), (20, 214), (40, 210), (46, 186), (60, 182), (66, 162), (92, 158), (120, 160), (126, 176), (140, 180), (146, 204), (166, 210), (172, 232), (190, 244), (204, 300)]
    out.append(f'<clipPath id="{u}-bt"><polygon points="{P(butte)}"/></clipPath><polygon points="{P(butte)}" fill="url(#{u}-butte)"/>')
    out.append(f'<g clip-path="url(#{u}-bt)">'
               + "".join(f'<path d="M -10 {y} Q 100 {y + 2} 210 {y - 1}" stroke="{c}" stroke-width="2.2" fill="none" opacity="0.35"/>' for y, c in ((172, "#FFC08A"), (192, "#7A2A30"), (214, "#FFC08A"), (236, "#7A2A30"), (256, "#FFB07A")))
               + streaks(40, 8, (-10, 160, 200, 300), ["#7A2A30", "#FFB27A"], w=(1.2, 3), length=(10, 40), opacity=(0.2, 0.5), slant=0.05)
               + f'<polygon points="{P([(120, 160), (126, 176), (140, 180), (146, 204), (166, 210), (172, 232), (190, 244), (204, 300), (118, 300), (112, 200)])}" fill="#5E2236" opacity="0.4"/>'
               + blobs(50, 10, (-10, 250, 200, 300), ["#2E4A3A", "#3E5A44"], r=(2, 4), opacity=(0.85, 1), squash=0.75) + "</g>")
    out.append(f'<polyline points="{P(butte[2:10])}" fill="none" stroke="#FFD2A0" stroke-width="2" stroke-linejoin="round" opacity="0.8"/>')
    # Cathedral Rock: one jagged silhouette of fluted spires on a broad base, stepped by ledges
    cr = [(168, 300), (190, 280), (206, 262), (214, 250), (226, 244), (232, 232), (240, 228), (244, 214), (250, 210), (254, 196), (258, 192), (262, 172),
          (266, 166), (269, 150), (275, 146), (280, 152), (283, 170), (290, 174), (294, 160), (297, 142), (302, 134), (307, 137), (310, 150), (316, 153),
          (319, 130), (323, 114), (328, 106), (333, 104), (336, 110), (338, 124), (342, 128), (345, 110), (349, 96), (354, 92), (359, 97), (362, 114),
          (366, 126), (369, 152), (373, 152), (376, 126), (379, 110), (384, 102), (389, 105), (392, 120), (396, 136), (403, 140), (409, 152), (416, 155),
          (421, 148), (427, 152), (433, 165), (440, 171), (448, 175), (452, 190), (460, 196), (466, 212), (476, 220), (482, 236), (496, 250), (510, 268),
          (530, 288), (540, 300)]
    out.append(f'<clipPath id="{u}-cr"><polygon points="{P(cr)}"/></clipPath><polygon points="{P(cr)}" fill="url(#{u}-rockb)"/>')
    g = [f'<rect x="160" y="80" width="400" height="230" fill="url(#{u}-rock)" opacity="0.85"/>']
    for y in range(96, 300, 8):
        rr = random.Random(y)
        g.append(f'<path d="M 160 {y + rr.uniform(-1, 1):.1f} Q 340 {y + rr.uniform(-3, 3):.1f} 550 {y + rr.uniform(-1, 1):.1f}" stroke="{rr.choice(["#FFC08A", "#7A2A30", "#FFB07A", "#9A3A34"])}" stroke-width="{rr.uniform(1.5, 3.2):.1f}" fill="none" opacity="{rr.uniform(0.2, 0.45):.2f}"/>')
    g.append(streaks(160, 7, (180, 90, 540, 300), ["#7A2A30", "#5E2236", "#FFB27A"], w=(1.2, 3), length=(10, 46), opacity=(0.2, 0.5), slant=0.05))
    # shadow faces on the right of each spire (sun low behind-left), and the deep cleft between the twin spires
    shadows = [[(275, 146), (280, 152), (283, 170), (290, 174), (288, 300), (276, 300), (277, 160)],
               [(302, 134), (307, 137), (310, 150), (316, 153), (314, 300), (304, 300), (305, 146)],
               [(333, 104), (336, 110), (338, 124), (342, 128), (340, 300), (334, 300), (334, 118)],
               [(354, 92), (359, 97), (362, 114), (366, 126), (369, 152), (370, 300), (357, 300), (356, 110)],
               [(384, 102), (389, 105), (392, 120), (396, 136), (403, 140), (409, 152), (416, 155), (414, 300), (390, 300), (387, 118)],
               [(421, 148), (427, 152), (433, 165), (440, 171), (448, 175), (452, 190), (460, 196), (466, 212), (476, 220), (482, 236), (496, 250), (510, 268), (530, 288), (540, 300), (430, 300), (424, 170)]]
    for sh in shadows:
        g.append(f'<polygon points="{P(sh)}" fill="#4E1E3A" opacity="0.42"/>')
    g.append('<polygon points="366,126 369,152 373,152 376,126 372,300 368,300" fill="#3A1430" opacity="0.6"/>')
    g.append(blobs(110, 9, (180, 252, 540, 300), ["#2E4A3A", "#3E5A44", "#4E6A4E"], r=(1.8, 3.6), opacity=(0.85, 1), squash=0.75))
    g.append(blobs(30, 19, (200, 236, 520, 256), ["#3E5A44", "#4E6A4E"], r=(1.5, 2.6), opacity=(0.7, 0.9), squash=0.75))
    g.append(mist(330, 150, 120, 80, "#FFB070", f"{u}-glowr", 0.25))
    g.append(f'<rect x="150" y="262" width="420" height="50" fill="#5E2A3A" opacity="0.22"/>')
    out.append(f'<g clip-path="url(#{u}-cr)">' + "".join(g) + "</g>")
    lit = [cr[i:j] for i, j in ((4, 9), (11, 15), (19, 23), (24, 28), (31, 34), (38, 42))]
    for seg in lit:
        out.append(f'<polyline points="{P(seg)}" fill="none" stroke="#FFD2A0" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" opacity="0.85"/>')
    # midground: rolling scrub with junipers in long shadow
    poly, mg = ridge_poly([(-10, 298), (120, 292), (260, 300), (400, 290), (610, 298)], 21, base=444, amp=4, fill="#6E3A34")
    out.append(poly)
    rj = random.Random(22)
    for _ in range(34):
        x = rj.uniform(-10, 610)
        y = rj.uniform(298, 322)
        out.append(juniper(x, y, rj.uniform(8, 16) * (1 + (y - 298) / 40), rj.randrange(999), rim="#D9A070"))
    out.append(f'<path d="M -10 318 Q 200 306 610 316 L 610 444 L -10 444 Z" fill="url(#{u}-ground)"/>')
    out.append(dots(260, 23, (-10, 318, 610, 444), "#5A2420", r=(0.7, 2), opacity=(0.25, 0.6)))
    out.append(grass(70, 24, (-10, 330, 610, 444), ["#C9A46A", "#A88A52", "#8E7A4A"], h=(4, 11)))
    # sandstone ledges breaking through the soil
    for pts, sh in (([(-10, 372), (60, 366), (140, 370), (170, 380), (150, 392), (-10, 398)], [(-10, 392), (150, 392), (170, 380), (176, 388), (156, 400), (-10, 406)]),
                    ([(420, 350), (480, 344), (560, 346), (610, 352), (610, 364), (430, 362)], [(430, 362), (610, 364), (610, 372), (436, 370)])):
        out.append(f'<polygon points="{P(pts)}" fill="#D97A52"/><polygon points="{P(sh)}" fill="#7A3428" opacity="0.7"/>')
        out.append(f'<polyline points="{P(pts[:3])}" fill="none" stroke="#FFC08A" stroke-width="2" opacity="0.7"/>')
    # the winding trail, from our feet toward the rock
    trail = "M 230 444 C 250 410 330 400 340 378 C 350 356 280 350 290 334 C 298 322 350 322 360 316 L 372 316 C 368 326 316 330 312 338 C 304 352 378 360 372 384 C 364 410 300 418 300 444 Z"
    out.append(f'<path d="{trail}" fill="url(#{u}-trail)"/>')
    out.append(f'<path d="M 300 444 C 300 418 364 410 372 384" fill="none" stroke="#FFC08A" stroke-width="2" opacity="0.5"/>')
    out.append(dots(80, 25, (240, 330, 380, 444), "#F6B080", r=(0.8, 1.8), opacity=(0.4, 0.8)))
    # a basket cairn marking the trail, and a hiker pausing to watch the glow
    out.append('<g transform="translate(386 352)"><path d="M -9 0 L -7 -20 L 7 -20 L 9 0 Z" fill="#8A5A44"/>'
               + "".join(f'<ellipse cx="{dx}" cy="{dy}" rx="4" ry="2.6" fill="{c}"/>' for dx, dy, c in ((-4, -3, "#B4553A"), (3, -4, "#C8603E"), (-2, -9, "#9A4434"), (4, -11, "#B4553A"), (-3, -15, "#C8603E"), (2, -18, "#9A4434")))
               + '<g stroke="#3A2A2A" stroke-width="1" opacity="0.8"><path d="M -8 -10 L 8 -10 M -8.5 -5 L 8.5 -5 M -7.5 -15 L 7.5 -15"/><path d="M -3 0 L -2 -20 M 3 0 L 2 -20"/></g></g>')
    hx, hb = 318, 412
    out.append(f'<ellipse cx="{hx + 18}" cy="{hb}" rx="24" ry="3.2" fill="#5A2420" opacity="0.4"/>')
    out.append(F.person(hx, hb, 62, "hiker", -1, {"top": "#2E7A8A", "top_kind": "tee", "bottom": "#B8A078", "bottom_kind": "shorts", "bag": "#C9734A",
                                                 "hat_kind": "sunhat", "hat": "#E8D6B0", "skin": "#C88A60", "shoes": "#5A3A2A", "form": "m"},
                        seed=41, rim="#FFC08A", light=-1))
    # foreground: junipers rim-lit by the sun behind us, prickly pear, a yucca
    out.append(juniper(120, 330, 70, 3, rim="#E8B070"))
    out.append(juniper(500, 334, 60, 4, rim="#E8B070"))
    out.append(juniper(46, 420, 120, 5, rim="#F0B878"))
    out.append(juniper(566, 430, 130, 6, rim="#F0B878"))
    out.append(prickly_pear(190, 420, 1.3, 2))
    out.append(prickly_pear(450, 412, 1.1, 3))
    out.append('<g transform="translate(410 400)">' + "".join(f'<path d="M 0 0 Q {math.sin(math.radians(a)) * 10:.1f} -14 {math.sin(math.radians(a)) * 26:.1f} {-math.cos(math.radians(a)) * 26:.1f}" stroke="{c}" stroke-width="2.4" fill="none" stroke-linecap="round"/>' for a, c in ((-70, "#5E7A4A"), (-45, "#7A9A5A"), (-20, "#5E7A4A"), (0, "#8EAA6A"), (22, "#5E7A4A"), (46, "#7A9A5A"), (70, "#5E7A4A"))) + "</g>")
    # long shadows of the foreground shrubs stretching toward the rock
    out.append('<path d="M 46 420 L 140 380 L 170 384 L 90 424 Z" fill="#5A2420" opacity="0.25"/><path d="M 566 430 L 640 392 L 640 410 L 600 434 Z" fill="#5A2420" opacity="0.25"/>')
    # ravens riding the evening air
    out.append('<g fill="none" stroke="#2A1E2E" stroke-width="2.2" stroke-linecap="round"><path d="M 470 128 q 7 -6 14 0 q 6 -6 13 0"/><path d="M 500 150 q 5 -4 9 0 q 4 -4 9 0"/></g>')
    return "\n".join(out)


# ================================================================ ARCHES (Delicate Arch at golden hour, La Sal Mountains behind)
def arches():
    u = "pd-arches"
    out = [defs(
        lg(f"{u}-sky", [(0, "#2A5CA8"), (0.45, "#6A9ACC"), (0.75, "#BCD2DC"), (0.9, "#F2DCC0"), (1, "#F8D2A8")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-arch", [(0, "#F9A85A"), (0.3, "#F2782E"), (0.75, "#D8522A"), (0.9, "#D8683A"), (1, "#EAA06A")], 0, 96, 0, 336, units="userSpaceOnUse"),
        lg(f"{u}-mtn", [(0, "#8A7AAE"), (1, "#5E5A8E")]),
        lg(f"{u}-valley", [(0, "#9A6A86"), (1, "#6E4A6E")]),
        lg(f"{u}-rock", [(0, "#F2B486"), (1, "#E08E5E")], 0, 330, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-bowl", [(0, "#B8644A"), (1, "#E89A6A")], 0, 336, 0, 380, units="userSpaceOnUse"),
        lg(f"{u}-pool", [(0, "#BCD8E6"), (1, "#7AA6CC")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(300, 300, 300, "#FFE6C2", f"{u}-warm", 0.45))
    rc = random.Random(6)
    for cx, cy, w in ((120, 120, 110), (480, 96, 130)):
        for _ in range(7):
            x = cx + rc.uniform(-w / 2, w / 2) * 0.7
            out.append(f'<ellipse cx="{x:.1f}" cy="{cy + rc.uniform(-4, 4):.1f}" rx="{rc.uniform(0.15, 0.35) * w:.1f}" ry="{rc.uniform(2.5, 5):.1f}" fill="#FFE2CC" opacity="0.55"/>')
    # La Sal Mountains: snowy summits catching the last sun, forested flanks in blue shadow
    poly, mtn = ridge_poly([(-10, 288), (60, 280), (120, 266), (170, 248), (210, 236), (250, 224), (290, 208), (330, 222), (370, 196), (410, 214), (446, 204), (490, 230), (540, 250), (610, 262)], 31, base=320, amp=6, fill=f"url(#{u}-mtn)")
    out.append(poly)
    out.append(f'<clipPath id="{u}-ms"><polygon points="{P(mtn + [(610, 320), (-10, 320)])}"/></clipPath>')
    rr = random.Random(32)
    top = [(x, y_on(mtn, x)) for x in range(150, 560, 4)]
    top = [(x, y) for x, y in top if y is not None]
    low = []
    knots = [rr.uniform(0.35, 0.9) for _ in range(len(top) // 4 + 2)]
    for i, (x, y) in enumerate(top):
        f_ = i / 4
        k0 = knots[int(f_)]
        k1 = knots[int(f_) + 1]
        k = k0 + (k1 - k0) * (f_ - int(f_))
        d = max(0, (258 - y)) * k + rr.uniform(-1.5, 1.5)
        low.append((x, y + max(0, d)))
    snowpoly = top + low[::-1]
    ribs = "".join(f'<path d="M {x + rr.uniform(-2, 2):.1f} {y + rr.uniform(4, 14):.1f} q {rr.uniform(-4, 4):.1f} 8 {rr.uniform(-6, 6):.1f} {rr.uniform(8, 22):.1f}" stroke="#8A82B8" stroke-width="{rr.uniform(1.5, 2.6):.1f}" fill="none" stroke-linecap="round" opacity="{rr.uniform(0.35, 0.6):.2f}"/>' for x, y in top[::5] if y < 238)
    out.append(f'<g clip-path="url(#{u}-ms)"><polygon points="{P(snowpoly)}" fill="#FFF4EE"/>'
               + f'<polygon points="{P(snowpoly)}" fill="#C8C2E6" opacity="0.0"/>' + ribs
               + "".join(f'<path d="M {x} 192 L {x + 30} 300 L {x + 52} 300 Z" fill="#6A64A0" opacity="0.3"/>' for x, _ in [(296, 0), (376, 0), (452, 0)])
               + f'<path d="M -10 276 Q 300 262 610 276 L 610 320 L -10 320 Z" fill="#4E4E7E" opacity="0.35"/>'
               + "</g>")
    out.append(f'<polyline points="{P([p for p in mtn if p[1] < 250])}" fill="none" stroke="#FFE8D8" stroke-width="1.5" opacity="0.7"/>')
    out.append(mist(300, 300, 360, 22, "#F2DCC0", f"{u}-haze", 0.6))
    # Cache Valley below: fins and mesas in violet evening shade
    poly, _ = ridge_poly([(-10, 300), (40, 296), (44, 290), (110, 290), (116, 300), (220, 304), (300, 298), (304, 292), (380, 292), (386, 300), (470, 296), (476, 288), (560, 288), (566, 298), (610, 300)], 34, base=340, amp=2, depth=3, fill=f"url(#{u}-valley)")
    out.append(poly)
    out.append('<g fill="#F2A07A" opacity="0.6">' + "".join(f'<rect x="{x}" y="{y}" width="{w}" height="2"/>' for x, y, w in ((44, 290, 66), (304, 292, 76), (476, 288, 84))) + "</g>")
    # the far rim of the slickrock bowl on which the arch stands
    rim = [(-10, 334), (60, 330), (140, 328), (196, 330), (230, 326), (300, 328), (380, 330), (420, 328), (500, 334), (610, 330)]
    out.append(f'<path d="{smooth(rim)} L 610 444 L -10 444 Z" fill="#E89A6A"/>')
    out.append(f'<path d="{smooth(rim)}" fill="none" stroke="#FFD0A0" stroke-width="2.4"/>')
    # Delicate Arch: thick left leg, slender right leg pinched near its foot, a pale cap
    outer = [(190, 334), (197, 300), (191, 262), (195, 222), (203, 184), (217, 150), (239, 122), (267, 104), (299, 96), (328, 100), (350, 116),
             (364, 140), (370, 172), (368, 208), (362, 244), (360, 272), (364, 300), (370, 320), (378, 334)]
    inner = [(348, 334), (344, 312), (339, 292), (337, 270), (340, 244), (343, 206), (340, 172), (328, 148), (306, 134), (284, 136), (266, 150),
             (256, 176), (250, 212), (248, 256), (250, 298), (254, 334)]
    out.append('<path d="M 150 344 Q 180 322 260 324 Q 340 320 420 342 Z" fill="#F0A878"/><path d="M 170 334 Q 260 318 400 334" fill="none" stroke="#FFD6A8" stroke-width="2"/>')
    d = smooth(outer) + " L " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in inner[:1]) + " " + smooth(inner)[smooth(inner).index("C"):] + " Z"
    out.append(f'<clipPath id="{u}-ac"><path d="{d}"/></clipPath>')
    out.append(f'<path d="{d}" fill="url(#{u}-arch)"/>')
    g = []
    for y in range(104, 334, 6):
        r_ = random.Random(y)
        g.append(f'<path d="M 190 {y + r_.uniform(-1, 1):.1f} Q 290 {y + r_.uniform(-2, 2):.1f} 380 {y + r_.uniform(-1, 1):.1f}" stroke="{r_.choice(["#FFC08A", "#A8442A", "#FFB07A"])}" stroke-width="{r_.uniform(1.2, 2.6):.1f}" fill="none" opacity="{r_.uniform(0.2, 0.45):.2f}"/>')
    g.append(streaks(70, 3, (200, 110, 372, 332), ["#A8442A", "#7A3426", "#FFC890"], w=(1.2, 3), length=(10, 40), opacity=(0.2, 0.5), slant=0.08))
    g.append('<path d="M 190 96 Q 300 92 380 100 L 380 128 Q 300 118 190 132 Z" fill="#F6D2A6" opacity="0.4"/>')   # paler cap rock
    g.append('<path d="M 190 300 L 380 300 L 380 334 L 190 334 Z" fill="#F2C49A" opacity="0.35"/>')                     # paler base layer
    g.append('<path d="M 248 256 L 250 212 L 256 176 L 266 150 L 284 136 L 274 162 L 266 204 L 262 260 L 266 334 L 248 334 Z" fill="#8A3A2A" opacity="0.4"/>')  # inner face in shade
    g.append('<path d="M 362 244 L 368 208 L 370 172 L 364 140 L 384 150 L 384 334 L 368 334 Z" fill="#8A3A2A" opacity="0.32"/>')
    g.append('<path d="M 200 150 Q 230 110 300 98 L 300 110 Q 236 122 210 170 Z" fill="#FFD29A" opacity="0.35"/>')
    out.append(f'<g clip-path="url(#{u}-ac)">' + "".join(g) + "</g>")
    out.append(f'<path d="{smooth(outer[2:12])}" fill="none" stroke="#FFDAB0" stroke-width="2.6" stroke-linecap="round" opacity="0.85"/>')
    # visitors under the arch for scale
    out.append(figure(296, 334, 24, "#2E5A8A", seed=3, pose="point", facing=1, light=1, rim="#FFDAB0", pal={"season": "summer", "hat_kind": "sunhat"}))
    out.append(figure(312, 334, 22, "#E8C24A", seed=4, pose="photo", facing=1, light=1, rim="#FFDAB0", pal={"season": "summer", "form": "f"}))
    # the long evening shadow of the arch laid across the bowl
    out.append('<path d="M 196 338 L 120 352 Q 80 356 60 354 L 66 360 Q 120 362 214 342 Z" fill="#8A3A3A" opacity="0.35"/>')
    # the bowl: a broad dip of slickrock between us and the arch, its far wall in shade
    out.append(f'<path d="M -10 344 Q 150 332 300 338 Q 460 344 610 336 L 610 384 Q 300 362 -10 392 Z" fill="url(#{u}-bowl)" opacity="0.8"/>')
    for k in range(9):
        y = 346 + k * 5
        out.append(f'<path d="M -10 {y + 6} Q 200 {y - 6 + k} 400 {y + 2} T 610 {y - 2}" stroke="#C26A48" stroke-width="1.6" fill="none" opacity="0.4"/>')
    # near slickrock at our feet: cross-bedded swirls, potholes holding the sky
    out.append(f'<path d="M -10 392 Q 300 362 610 384 L 610 444 L -10 444 Z" fill="url(#{u}-rock)"/>')
    for k in range(7):
        out.append(f'<path d="M {-20 + k * 30} 444 Q {120 + k * 40} {400 - k * 3} {300 + k * 50} {392 + k * 4}" stroke="#D07A50" stroke-width="1.8" fill="none" opacity="0.5"/>')
    for k in range(5):
        out.append(f'<path d="M {380 + k * 26} 444 Q {470 + k * 20} {404 + k * 4} {620} {396 + k * 8}" stroke="#D07A50" stroke-width="1.8" fill="none" opacity="0.5"/>')
    for cx, cy, rx, ry in ((470, 414, 36, 6), (150, 424, 26, 4.5), (540, 432, 18, 3.2)):
        out.append(f'<ellipse cx="{cx}" cy="{cy + 1.6}" rx="{rx + 3}" ry="{ry + 2}" fill="#B8644A"/><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{u}-pool)"/>'
                   f'<ellipse cx="{cx - rx * 0.3:.1f}" cy="{cy - ry * 0.2:.1f}" rx="{rx * 0.35:.1f}" ry="{ry * 0.3:.1f}" fill="#F2DCC0" opacity="0.8"/>')
    out.append(dots(120, 41, (-10, 392, 610, 444), "#A8584A", r=(0.6, 1.6), opacity=(0.2, 0.5)))
    # blackbrush tufts in the cracks
    for x, y in ((90, 404), (250, 396), (560, 392), (380, 438)):
        out.append(blobs(10, x, (x - 10, y - 8, x + 10, y), ["#5A5A3E", "#6E6A44", "#4A4A34"], r=(2, 4), opacity=(0.9, 1), squash=0.8))
    # a photographer at the tripod on the near left, rim-lit gold
    out.append('<g transform="translate(108 412) scale(0.62)">'
               '<path d="M 40 0 L 52 -58 L 64 0 M 52 -58 L 52 0" stroke="#2A2224" stroke-width="2.6" fill="none"/><rect x="42" y="-72" width="22" height="14" rx="2" fill="#2A2224"/><circle cx="64" cy="-65" r="4.5" fill="#3A4A5A"/>'
               '</g>')
    out.append(F.person(108 + 22 * 0.62, 412, 62, "lean", 1, {"top": "#B8463E", "top_kind": "jacket", "bottom": "#3A3240", "bottom_kind": "trousers",
                                                               "hat_kind": "cap", "hat": "#2E4A5A", "form": "m"}, seed=71, rim="#FFD08A", light=1))
    out.append('<path d="M 100 413 L 24 424 L 30 428 L 112 414 Z" fill="#8A3A3A" opacity="0.3"/>')
    # ravens
    out.append('<g fill="none" stroke="#2A2230" stroke-width="2.2" stroke-linecap="round"><path d="M 420 150 q 6 -5 12 0 q 6 -5 12 0"/><path d="M 446 168 q 4 -3 8 0 q 4 -3 8 0"/></g>')
    return "\n".join(out)


# ================================================================ MONUMENT VALLEY (sunrise, the long road in)
def butte(u, k, outline, lit_pts, grad, base_y, seed, skirt, shadow_from):
    """Sheer sandstone butte on a talus skirt: lit left faces, violet shadow on the right, strata and varnish."""
    cid = f"{u}-b{k}"
    out = [f'<path d="{skirt}" fill="#A8504A"/>',
           f'<clipPath id="{cid}"><polygon points="{P(outline)}"/></clipPath><polygon points="{P(outline)}" fill="url(#{grad})"/>']
    xs = [x for x, _ in outline]
    ys = [y for _, y in outline]
    box = (min(xs), min(ys), max(xs), max(ys))
    g = [streaks(int((box[2] - box[0]) * 0.9), seed, box, ["#6A2A3A", "#4E2240", "#FFC890"], w=(1.2, 3), length=(10, 50), opacity=(0.2, 0.5), slant=0.04)]
    for y in range(int(box[1]) + 6, int(box[3]), 7):
        g.append(f'<line x1="{box[0]}" y1="{y}" x2="{box[2]}" y2="{y + random.Random(y).uniform(-1, 1):.1f}" stroke="{random.Random(y + seed).choice(["#FFC890", "#7A3040"])}" stroke-width="1.5" opacity="0.25"/>')
    g.append(f'<polygon points="{P(shadow_from)}" fill="#3E2050" opacity="0.5"/>')
    out.append(f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>")
    out.append(f'<polyline points="{P(lit_pts)}" fill="none" stroke="#FFD89A" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round" opacity="0.9"/>')
    return "".join(out)


def horse(x, base, s, col, mane="#2A1A16", rim="#FFC870", grazing=False, flip=False):
    tf = f'translate({x:.1f} {base:.1f}) scale({-s if flip else s:.3f} {s:.3f})'
    neck = ('<path d="M 30 -50 Q 40 -40 50 -14 L 56 -10 Q 60 -14 56 -22 Q 50 -46 40 -58 Z" fill="{c}"/><path d="M 48 -16 Q 54 -6 60 -8" stroke="{c}" stroke-width="5" fill="none"/>' if grazing else
            '<path d="M 30 -50 Q 40 -66 50 -78 L 58 -72 Q 64 -66 60 -62 L 52 -64 Q 46 -56 42 -46 Z" fill="{c}"/>').format(c=col)
    return (f'<g transform="{tf}">'
            f'<path d="M -30 -50 Q -32 -62 -14 -62 L 22 -60 Q 34 -60 34 -48 L 32 -34 Q 28 -28 20 -30 L -22 -30 Q -32 -32 -30 -50 Z" fill="{col}"/>'
            + neck +
            f'<g stroke="{col}" stroke-width="5" stroke-linecap="round"><path d="M -22 -34 L -24 0"/><path d="M -14 -32 L -12 0"/><path d="M 18 -32 L 16 0"/><path d="M 26 -34 L 30 0"/></g>'
            f'<path d="M -30 -54 Q -42 -46 -38 -24" stroke="{mane}" stroke-width="5" fill="none" stroke-linecap="round"/>'
            f'<path d="M -28 -60 Q 0 -66 32 -58" stroke="{rim}" stroke-width="2.4" fill="none" opacity="0.85"/>'
            "</g>")


def sagebrush(x, y, r, seed, rim="#F2D2A0"):
    """Big sagebrush: a low dome of grey-green twiggy strokes, silvery tips catching the light."""
    rnd = random.Random(seed)
    out = [f'<ellipse cx="{x:.1f}" cy="{y - r * 0.35:.1f}" rx="{r:.1f}" ry="{r * 0.55:.1f}" fill="#5E6248"/>']
    strokes = []
    for _ in range(int(r * 2.2)):
        a = rnd.uniform(-1.3, 1.3)
        L = r * rnd.uniform(0.5, 0.95)
        bx = x + rnd.uniform(-r * 0.5, r * 0.5)
        ex, ey = bx + math.sin(a) * L, y - math.cos(a) * L * 0.75
        strokes.append(f'<path d="M {bx:.1f} {y:.1f} Q {bx + math.sin(a) * L * 0.3:.1f} {y - L * 0.5:.1f} {ex:.1f} {ey:.1f}" stroke="{rnd.choice(["#8A9070", "#9AA080", "#7A8064"])}"/>')
    out.append(f'<g fill="none" stroke-width="{max(1.5, r * 0.09):.1f}" stroke-linecap="round">' + "".join(strokes) + "</g>")
    out.append(dots(int(r * 0.9), seed, (x - r * 0.9, y - r * 0.9, x - r * 0.1, y - r * 0.4), rim, r=(r * 0.05, r * 0.1), opacity=(0.5, 0.9)))
    return "".join(out)


def monument_valley():
    u = "pd-monvalley"
    C = Cam(f=380, cx=300, vpy=292, eye=2.6)
    out = [defs(
        lg(f"{u}-sky", [(0, "#2A2E6A"), (0.32, "#5A4C8E"), (0.58, "#B8749A"), (0.78, "#F2A486"), (0.92, "#FFD490"), (1, "#FFE6B0")], 0, 40, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-bt", [(0, "#F6A060"), (0.4, "#D8603E"), (1, "#8E3A44")], 0, 0, 1, 0),
        lg(f"{u}-bt2", [(0, "#E88A5A"), (0.5, "#C2583E"), (1, "#7E3646")], 0, 0, 1, 0),
        lg(f"{u}-floor", [(0, "#C8705A"), (0.4, "#B4553E"), (1, "#8A3A2E")], 0, 292, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-road", [(0, "#8A6A7A"), (0.5, "#4E3E4E"), (1, "#2E2632")], 0, 292, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(30, 3, (0, 40, 600, 120), "#FFF6E8", r=(0.6, 1.2), opacity=(0.3, 0.8)))
    # the sun just clearing the eastern horizon (left), with a broad warm glow
    out.append(glow(96, 286, 300, "#FFD08A", f"{u}-sun", 0.85))
    out.append(glow(96, 286, 60, "#FFF2C8", f"{u}-sun2", 0.9))
    out.append('<circle cx="96" cy="288" r="18" fill="#FFF6DC"/>')
    rc = random.Random(9)
    for cx, cy, w in ((420, 118, 200), (170, 150, 150), (520, 176, 90)):
        for _ in range(9):
            x = cx + rc.uniform(-w / 2, w / 2) * 0.7
            y = cy + rc.uniform(-5, 5)
            rx = rc.uniform(0.15, 0.35) * w
            out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{rc.uniform(3, 6):.1f}" fill="#7A5A96" opacity="0.5"/>'
                       f'<ellipse cx="{x - 6:.1f}" cy="{y + 2:.1f}" rx="{rx * 0.8:.1f}" ry="2.6" fill="#FFC09A" opacity="0.75"/>')
    # distant mesas on the horizon, hazy
    poly, _ = ridge_poly([(-10, 292), (20, 284), (24, 274), (60, 272), (64, 284), (200, 288), (420, 286), (424, 276), (470, 274), (474, 284), (610, 288)], 51, base=300, amp=1.5, depth=3, fill="#9A6A8E")
    out.append(poly)
    out.append(mist(300, 290, 360, 18, "#FFD4A8", f"{u}-hz0", 0.6))
    # East Mitten (left) and West Mitten (right), thumbs facing in; Merrick Butte beyond on the right
    em = [(150, 262), (152, 182), (158, 176), (160, 168), (226, 166), (232, 172), (236, 180), (238, 262)]
    em_t = [(244, 262), (246, 200), (249, 186), (253, 182), (257, 188), (258, 206), (260, 262)]
    wm = [(372, 262), (374, 178), (378, 172), (382, 166), (448, 168), (452, 176), (456, 184), (458, 262)]
    wm_t = [(342, 262), (343, 206), (346, 190), (350, 184), (354, 188), (357, 200), (358, 262)]
    mb = [(486, 270), (490, 214), (500, 208), (504, 196), (560, 196), (564, 206), (590, 210), (600, 222), (604, 270)]
    out.append(butte(u, 1, mb, [mb[1], mb[2], mb[3], mb[4]], f"{u}-bt2", 270, 61, "M 470 296 Q 490 262 520 262 L 580 262 Q 610 270 630 296 Z",
                     [(540, 196), (604, 196), (604, 270), (548, 270)]))
    out.append(butte(u, 2, em, [em[0], em[1], em[2], em[3], em[4]], f"{u}-bt", 262, 62, "M 110 300 Q 140 258 170 252 L 240 252 Q 280 262 300 300 Z",
                     [(206, 160), (240, 160), (240, 262), (214, 262)]))
    out.append(butte(u, 3, em_t, [em_t[0], em_t[1], em_t[2], em_t[3]], f"{u}-bt", 262, 63, "M 236 300 Q 244 262 252 258 L 262 262 Z",
                     [(253, 180), (262, 180), (262, 262), (254, 262)]))
    out.append(butte(u, 4, wm, [wm[0], wm[1], wm[2], wm[3], wm[4]], f"{u}-bt", 262, 64, "M 330 300 Q 360 258 390 252 L 450 252 Q 486 262 510 300 Z",
                     [(426, 160), (460, 160), (460, 262), (432, 262)]))
    out.append(butte(u, 5, wm_t, [wm_t[0], wm_t[1], wm_t[2], wm_t[3]], f"{u}-bt", 262, 65, "M 336 300 Q 342 262 350 258 L 360 262 Z",
                     [(350, 182), (360, 182), (360, 262), (352, 262)]))
    # talus skirts: lit on the sunrise side
    out.append('<path d="M 112 298 Q 140 260 168 254 L 196 254 Q 160 268 132 298 Z" fill="#E08A5E" opacity="0.6"/><path d="M 332 298 Q 360 260 388 254 L 410 254 Q 380 268 352 298 Z" fill="#E08A5E" opacity="0.6"/>')
    # small spires on the far left
    for x, t, w in ((20, 230, 14), (44, 214, 10), (62, 246, 12)):
        pts = [(x - w / 2, 296), (x - w / 2 + 1, t + 6), (x, t), (x + w / 2 - 1, t + 6), (x + w / 2, 296)]
        out.append(f'<polygon points="{P(pts)}" fill="#7A4A6A"/><polyline points="{P(pts[:3])}" fill="none" stroke="#FFC890" stroke-width="1.6" opacity="0.8"/>')
    out.append(mist(300, 292, 380, 22, "#F6B6A0", f"{u}-hz1", 0.55))
    # valley floor, with the buttes' long morning shadows reaching right
    out.append(f'<rect x="-10" y="292" width="620" height="152" fill="url(#{u}-floor)"/>')
    out.append('<g fill="#5A2A4A" opacity="0.35"><path d="M 238 300 L 610 316 L 610 330 L 222 304 Z"/><path d="M 458 298 L 610 304 L 610 312 L 448 302 Z"/><path d="M 260 300 L 330 304 L 326 306 L 258 302 Z"/></g>')
    rs = random.Random(13)
    out.append("".join(f'<ellipse cx="{(x := rs.uniform(-10, 610)):.1f}" cy="{(y := 296 + (rs.random() ** 1.8) * 148):.1f}" rx="{(r := (1.2 + (y - 292) / 22) * rs.uniform(0.7, 1.3)):.1f}" ry="{r * 0.55:.1f}" fill="{rs.choice(["#7A6A4A", "#8A7A52", "#6A5A40", "#8E7A5A"])}" opacity="0.8"/>' for _ in range(150)))
    out.append(grass(90, 14, (-10, 330, 610, 444), ["#D9A070", "#C28A5A", "#E8B07A"], h=(4, 10)))
    # the long straight road in, with a sunlit sheen down its middle
    out.append(f'<polygon points="{P([C(-6.2, 0, 3), C(6.2, 0, 3), C(6.2, 0, 3000), C(-6.2, 0, 3000)])}" fill="#C9805E" opacity="0.6"/>')
    out.append(f'<polygon points="{P([C(-4.6, 0, 3), C(4.6, 0, 3), C(4.6, 0, 3000), C(-4.6, 0, 3000)])}" fill="url(#{u}-road)"/>')
    for z in (60, 140, 400):   # warm sheen where the road catches the sky
        out.append(f'<polygon points="{P([C(-4.6, 0, z), C(4.6, 0, z), C(4.6, 0, z * 1.6), C(-4.6, 0, z * 1.6)])}" fill="#F6B88E" opacity="0.18"/>')
    for X in (-0.16, 0.16):
        out.append(f'<polygon points="{P([C(X - 0.07, 0, 3), C(X + 0.07, 0, 3), C(X + 0.07, 0, 3000), C(X - 0.07, 0, 3000)])}" fill="#F2C440"/>')
    for X in (-4.3, 4.3):
        out.append(f'<polygon points="{P([C(X - 0.08, 0, 3), C(X + 0.08, 0, 3), C(X + 0.08, 0, 3000), C(X - 0.08, 0, 3000)])}" fill="#F2E6DA" opacity="0.85"/>')
    # ranch fence along the right shoulder
    for z in (8, 11, 15, 20, 27, 36, 48, 64, 86, 115, 150):
        a_, b_ = C(8.5, 0, z), C(8.5, 1.3, z)
        out.append(f'<line x1="{a_[0]:.1f}" y1="{a_[1]:.1f}" x2="{b_[0]:.1f}" y2="{b_[1]:.1f}" stroke="#4A3030" stroke-width="{max(1.5, C.f * 0.1 / z):.1f}"/>')
    for yy in (0.8, 1.15):
        out.append(f'<polyline points="{P([C(8.5, yy, 8), C(8.5, yy, 150)])}" fill="none" stroke="#5A3A3A" stroke-width="1.5" opacity="0.7"/>')
    # free-roaming horses grazing by the road, rim-lit by the rising sun
    for X, Z, col, gz, fl in ((-10, 26, "#5A3A2E", True, False), (-13.5, 31, "#8A5A3A", False, True), (-8.5, 36, "#2E2220", True, True)):
        x, b = C(X, 0, Z)
        out.append(horse(x, b, C.f * 1.6 / Z / 66, col, grazing=gz, flip=fl))
        out.append(f'<ellipse cx="{x + 14:.1f}" cy="{b:.1f}" rx="{C.f * 2.4 / Z:.1f}" ry="1.6" fill="#5A2A3A" opacity="0.4"/>')
    # roadside sagebrush in the foreground, long shadows falling right
    for x, y, r in ((44, 430, 26), (110, 404, 18), (520, 410, 22), (574, 436, 28), (30, 380, 12), (586, 372, 12)):
        out.append(f'<ellipse cx="{x + r * 1.2:.1f}" cy="{y + 1:.1f}" rx="{r * 1.6:.1f}" ry="{r * 0.2:.1f}" fill="#5A2A3A" opacity="0.35"/>')
        out.append(sagebrush(x, y, r, int(x)))
    out.append('<g fill="none" stroke="#2A1E2E" stroke-width="2.2" stroke-linecap="round"><path d="M 300 136 q 6 -5 12 0 q 6 -5 12 0"/></g>')
    return "\n".join(out)


# ================================================================ ATLANTA (Midtown from Lake Clara Meer, Piedmont Park, golden hour)
def dogwood(x, y, r, rot, seed, tint="#F6E2D8"):
    """Flowering dogwood blossom: four broad bracts with a notched, rosy-brown tip, green-gold centre."""
    rnd = random.Random(seed)
    out = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.0f})">']
    for i in range(4):
        a = i * 90 + rnd.uniform(-8, 8)
        L = r * rnd.uniform(0.92, 1.08)
        out.append(f'<g transform="rotate({a:.0f})">'
                   f'<path d="M 0 0 C {-L * 0.55:.1f} {-L * 0.2:.1f} {-L * 0.6:.1f} {-L * 0.95:.1f} {-L * 0.14:.1f} {-L:.1f} Q 0 {-L * 0.86:.1f} {L * 0.14:.1f} {-L:.1f} C {L * 0.6:.1f} {-L * 0.95:.1f} {L * 0.55:.1f} {-L * 0.2:.1f} 0 0 Z" fill="#FFFDF8"/>'
                   f'<path d="M 0 0 C {L * 0.55:.1f} {-L * 0.2:.1f} {L * 0.6:.1f} {-L * 0.95:.1f} {L * 0.14:.1f} {-L:.1f} Q {L * 0.1:.1f} {-L * 0.7:.1f} 0 0 Z" fill="{tint}" opacity="0.8"/>'
                   f'<path d="M {-L * 0.16:.1f} {-L * 0.99:.1f} Q 0 {-L * 0.84:.1f} {L * 0.16:.1f} {-L * 0.99:.1f}" stroke="#A8566A" stroke-width="{max(1.5, L * 0.12):.1f}" fill="none" stroke-linecap="round"/>'
                   f'<path d="M 0 {-L * 0.15:.1f} L 0 {-L * 0.75:.1f}" stroke="#E8D2C4" stroke-width="1" opacity="0.8"/>'
                   "</g>")
    out.append(f'<circle cx="0" cy="0" r="{r * 0.22:.1f}" fill="#9AAA4A"/>')
    out.append("".join(f'<circle cx="{r * 0.12 * math.cos(k):.1f}" cy="{r * 0.12 * math.sin(k):.1f}" r="{r * 0.07:.1f}" fill="#D8D86A"/>' for k in range(0, 7)))
    out.append("</g>")
    return "".join(out)


def dogwood_branch(pts, seed, flowers, leaves=6, w=6):
    """A dark dogwood branch along pts (smooth), blossoms at (t, r) positions, a few fresh leaves."""
    rnd = random.Random(seed)
    d = smooth(pts)
    out = [f'<path d="{d}" fill="none" stroke="#3E2E2A" stroke-width="{w}" stroke-linecap="round"/>',
           f'<path d="{d}" fill="none" stroke="#8A6A5A" stroke-width="{w * 0.3:.1f}" stroke-linecap="round" opacity="0.6" transform="translate(-1 -1)"/>']
    for _ in range(leaves):
        i = rnd.randrange(1, len(pts))
        x, y = pts[i]
        a = rnd.uniform(0, 360)
        L = rnd.uniform(18, 28)
        out.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({a:.0f})"><path d="M 0 0 Q {L * 0.5:.1f} {-L * 0.35:.1f} {L:.1f} 0 Q {L * 0.5:.1f} {L * 0.35:.1f} 0 0 Z" fill="#6E9A4A"/>'
                   f'<path d="M 0 0 L {L * 0.9:.1f} 0" stroke="#A8C878" stroke-width="1.2"/></g>')
    for i, (x, y, r) in enumerate(flowers):
        out.append(dogwood(x, y, r, rnd.uniform(0, 90), seed * 10 + i))
    return "".join(out)


def peach(x, y, r, rot=0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot})">'
            f'<circle cx="0" cy="0" r="{r}" fill="#F49A5A"/><circle cx="{-r * 0.3:.1f}" cy="{-r * 0.1:.1f}" r="{r * 0.72:.1f}" fill="#F7B26A"/>'
            f'<path d="M {r * 0.55:.1f} {-r * 0.1:.1f} A {r:.1f} {r:.1f} 0 0 1 {-r * 0.2:.1f} {r * 0.98:.1f}" fill="#E0604A" opacity="0.6"/>'
            f'<path d="M 0 {-r:.1f} Q {r * 0.25:.1f} 0 0 {r:.1f}" stroke="#D8704A" stroke-width="1.5" fill="none" opacity="0.7"/>'
            f'<ellipse cx="{-r * 0.45:.1f}" cy="{-r * 0.45:.1f}" rx="{r * 0.22:.1f}" ry="{r * 0.14:.1f}" fill="#FFE6C2" opacity="0.8"/>'
            f'<path d="M 0 {-r:.1f} q 2 -4 6 -5" stroke="#5A3A2A" stroke-width="1.8" fill="none"/><path d="M 4 {-r - 4:.1f} q 8 -6 14 0 q -8 4 -14 0 Z" fill="#6E9A4A"/></g>')


def jogger(x, base, h, shirt, shorts="#2A2A3A", skin="#6A4A3A", phase=0, cap=None, rim="#FFD08A"):
    """Runner mid-stride, facing left, rim-lit from behind (the sun is ahead of us, behind the skyline)."""
    p = {"top": shirt, "top_kind": "tank" if phase == 0 else "tee", "bottom": shorts, "bottom_kind": "shorts", "skin": skin, "shoes": "#E6E0D6",
         "form": "f" if phase == 0 else "m", "hair_style": "ponytail" if phase == 0 else "short"}
    if cap:
        p.update(hat_kind="cap", hat=cap)
    return F.person(x, base, h, "jog", -1, p, seed=int(x) + phase, rim=rim, light=1)


def atlanta():
    u = "pd-atlanta"
    out = [defs(
        lg(f"{u}-sky", [(0, "#6E9AC6"), (0.35, "#B4B6CC"), (0.6, "#F4C4A0"), (0.82, "#FFD48C"), (1, "#FFE4A8")], 0, 40, 0, 270, units="userSpaceOnUse"),
        lg(f"{u}-lake", [(0, "#F6D29A"), (0.25, "#E8B48A"), (0.6, "#8A9AB4"), (1, "#4E6A8A")], 0, 276, 0, 372, units="userSpaceOnUse"),
        lg(f"{u}-lawn", [(0, "#8AAA4E"), (1, "#4E7A3A")], 0, 356, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-granite", [(0, "#E8BBA0"), (0.6, "#C98E82"), (1, "#8A6A78")], 0, 0, 1, 0),
        lg(f"{u}-brick", [(0, "#B87A6A"), (0.6, "#7A4A50"), (1, "#5A3A4A")], 0, 0, 1, 0),
        lg(f"{u}-glass", [(0, "#F6D8A8"), (0.3, "#8EA6C0"), (1, "#4E6488")], 0, 0, 1, 0),
        lg(f"{u}-glass2", [(0, "#A8B8CC"), (1, "#5E7090")], 0, 0, 1, 0),
        lg(f"{u}-gold", [(0, "#FFE8A0"), (1, "#D8A040")], 0, 0, 1, 0),
        lg(f"{u}-path", [(0, "#E8D2B0"), (1, "#C8AE8A")], 0, 360, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(430, 232, 280, "#FFE2A0", f"{u}-sun", 0.75))
    rc = random.Random(5)
    for cx, cy, w in ((150, 104, 180), (500, 130, 120)):
        for _ in range(8):
            x = cx + rc.uniform(-w / 2, w / 2) * 0.7
            y = cy + rc.uniform(-5, 5)
            rx = rc.uniform(0.15, 0.32) * w
            out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{rc.uniform(3, 6):.1f}" fill="#E8C4C0" opacity="0.6"/>'
                       f'<ellipse cx="{x + 4:.1f}" cy="{y + 2:.1f}" rx="{rx * 0.8:.1f}" ry="2.4" fill="#FFE2B0" opacity="0.8"/>')
    out.append(glow(430, 232, 40, "#FFF6DC", f"{u}-sun2", 0.95))
    out.append('<circle cx="430" cy="234" r="14" fill="#FFF8E4"/>')
    # Midtown and downtown skyline, back-lit: far towers paler, near ones warmer
    rb = random.Random(7)
    def tower(x, w, top, fill, base=268, lit=0.25, rim=True, bands=False):
        g = [f'<rect x="{x}" y="{top}" width="{w}" height="{base - top}" fill="{fill}"/>']
        for yy in range(int(top) + 6, base - 4, 5):
            for j in range(int(w / 5)):
                if rb.random() < lit:
                    g.append(f'<rect x="{x + 2 + j * 5}" y="{yy}" width="2.6" height="2.4" fill="#FFE2A0" opacity="{rb.uniform(0.5, 0.95):.2f}"/>')
        if bands:
            g.append("".join(f'<rect x="{x}" y="{yy}" width="{w}" height="1.4" fill="#FFFFFF" opacity="0.18"/>' for yy in range(int(top) + 4, base, 6)))
        if rim:
            g.append(f'<rect x="{x + w - 2.2}" y="{top}" width="2.2" height="{base - top}" fill="#FFD890" opacity="0.8"/>')
        return "".join(g)
    # far towers in the haze
    for x, w, t in ((96, 22, 200), (122, 18, 186), (430, 26, 196), (468, 20, 210), (500, 26, 224), (226, 18, 190)):
        out.append(f'<rect x="{x}" y="{t}" width="{w}" height="{270 - t}" fill="#C4A6B0"/>')
    # the tallest: a dark granite tower with a gold-leafed open obelisk crown and spire
    bx, bw = 150, 34
    out.append(tower(bx, bw, 150, f"url(#{u}-brick)", lit=0.2))
    out.append(f'<polygon points="{P([(bx - 2, 150), (bx + bw + 2, 150), (bx + bw - 4, 144), (bx + 4, 144)])}" fill="#5A3A4A"/>')
    ob = [(bx + 4, 144), (bx + bw / 2, 104), (bx + bw - 4, 144)]
    out.append(f'<polygon points="{P(ob)}" fill="url(#{u}-gold)"/>')
    out.append(f'<g stroke="#A86A2A" stroke-width="1.2" opacity="0.8">' + "".join(
        f'<line x1="{bx + 4 + i * (bw - 8) / 6:.1f}" y1="144" x2="{bx + bw / 2:.1f}" y2="104"/>' for i in range(1, 6))
        + "".join(f'<line x1="{bx + 4 + (bw / 2 - 4) * t:.1f}" y1="{144 - 40 * t:.1f}" x2="{bx + bw - 4 - (bw / 2 - 4) * t:.1f}" y2="{144 - 40 * t:.1f}"/>' for t in (0.2, 0.4, 0.6, 0.8)) + "</g>")
    out.append(f'<line x1="{bx + bw / 2}" y1="104" x2="{bx + bw / 2}" y2="92" stroke="#D8A040" stroke-width="1.6"/>')
    out.append(glow(bx + bw / 2, 128, 30, "#FFE8A0", f"{u}-ob", 0.5))
    # mid-rise glass and stone between
    out.append(tower(194, 30, 196, f"url(#{u}-glass2)", lit=0.15, bands=True))
    out.append(tower(236, 26, 176, f"url(#{u}-glass)", bands=True))
    # the postmodern granite tower with its steep copper-gold pyramid crown and pinnacles
    ox, ow = 284, 46
    out.append(tower(ox, ow, 150, f"url(#{u}-granite)", lit=0.12))
    out.append(f'<rect x="{ox - 4}" y="196" width="{ow + 8}" height="72" fill="url(#{u}-granite)"/><rect x="{ox - 4}" y="196" width="{ow + 8}" height="2" fill="#FFE2C0"/>')
    for k in range(5):
        xx = ox + 5 + k * 9
        out.append(f'<rect x="{xx}" y="152" width="3" height="116" fill="#7A5A68" opacity="0.35"/>')
    out.append(f'<polygon points="{P([(ox + 2, 150), (ox + ow / 2, 108), (ox + ow - 2, 150)])}" fill="#C98A4A"/>')
    out.append(f'<polygon points="{P([(ox + ow / 2, 108), (ox + ow - 2, 150), (ox + ow / 2 + 4, 150)])}" fill="#8A5A3A" opacity="0.6"/>')
    out.append(f'<g stroke="#F6C88A" stroke-width="1.2" opacity="0.7">' + "".join(f'<line x1="{ox + 6 + i * 7}" y1="150" x2="{ox + ow / 2:.1f}" y2="108"/>' for i in range(5)) + "</g>")
    for px in (ox, ox + ow):
        out.append(f'<polygon points="{P([(px - 3, 152), (px, 138), (px + 3, 152)])}" fill="#C98A4A"/>')
    out.append(f'<line x1="{ox + ow / 2}" y1="108" x2="{ox + ow / 2}" y2="94" stroke="#C98A4A" stroke-width="1.8"/><circle cx="{ox + ow / 2}" cy="94" r="1.8" fill="#FFE2A0"/>')
    out.append(f'<rect x="{ox + ow - 3}" y="150" width="3" height="118" fill="#FFD890" opacity="0.85"/>')
    # sleek glass tower with a sloped crown and a fin, catching the sun
    gx, gw = 352, 34
    out.append(tower(gx, gw, 140, f"url(#{u}-glass)", bands=True, lit=0.1))
    out.append(f'<polygon points="{P([(gx, 140), (gx + gw, 140), (gx + gw, 122)])}" fill="url(#{u}-glass)"/>')
    out.append(f'<polygon points="{P([(gx + gw - 3, 122), (gx + gw, 104), (gx + gw + 1, 140), (gx + gw - 3, 140)])}" fill="#E8EEF4"/>')
    out.append(f'<rect x="{gx}" y="140" width="10" height="128" fill="#FFE6B0" opacity="0.4"/>')
    out.append(tower(392, 28, 186, f"url(#{u}-glass2)", bands=True, lit=0.15))
    out.append(tower(258, 24, 214, "#9A7A88", lit=0.3))
    out.append(tower(420, 34, 218, "#8E7488", lit=0.3))
    out.append(tower(330, 22, 206, "#A88A90", lit=0.25))
    out.append(mist(300, 262, 340, 26, "#FFE2B0", f"{u}-hz", 0.55))
    # the park's tree line across the lake, crowns lit gold on their sunward edges
    rt = random.Random(23)
    for _ in range(26):   # taller park oaks and magnolias rising unevenly behind the shore
        x = rt.uniform(-10, 610)
        h = rt.uniform(24, 48)
        out.append(canopy_band(x - h * 0.6, x + h * 0.6, 282, rt.randrange(999), ["#34503A", "#3E5A3A", "#2E4A34"], h=(h * 0.5, h), rim="#FFD890", n=int(h / 2)))
    out.append(canopy_band(-10, 610, 284, 24, ["#3E5A3A", "#4A6A40", "#56763E", "#2E4A30"], h=(12, 26), rim="#FFD890", n=200))
    out.append(conifer(70, 284, 70, "#2E4A30", 5, width=0.35))
    out.append(conifer(540, 284, 60, "#2E4A30", 6, width=0.35))
    # Lake Clara Meer, mirroring the gold sky and the towers
    out.append(f'<rect x="-10" y="276" width="620" height="96" fill="url(#{u}-lake)"/>')
    for x, w, t, col in ((150, 34, 150, "#9A6A6A"), (284, 46, 150, "#C9A08E"), (352, 34, 140, "#B8C0CC"), (236, 26, 176, "#C8B8B8")):
        L = (282 - t) * 0.42
        for j in range(8):
            yy = 284 + L * j / 8
            ww = w * (0.9 - 0.06 * j)
            out.append(f'<rect x="{x + (w - ww) / 2 + random.Random(j + x).uniform(-3, 3):.1f}" y="{yy:.1f}" width="{ww:.1f}" height="{L / 8 * 0.6:.1f}" fill="{col}" opacity="{0.4 - j * 0.04:.2f}"/>')
    rg_ = random.Random(14)
    for i in range(80):   # glitter path under the sun
        y = 284 + (i / 80) ** 1.4 * 84
        w = rg_.uniform(4, 16) * (0.5 + (y - 284) / 60)
        out.append(f'<rect x="{430 + rg_.gauss(0, 10 + (y - 284) * 0.5) - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="1.6" rx="0.8" fill="#FFF4D0" opacity="{rg_.uniform(0.5, 0.95):.2f}"/>')
    out.append('<g stroke="#FFFFFF" stroke-width="1.5" opacity="0.35">' + "".join(f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}"/>' for x, y, w in ((40, 300, 50), (120, 318, 70), (230, 306, 40), (60, 340, 90), (280, 330, 60), (180, 352, 70))) + "</g>")
    # the wooden boardwalk pier on the right, with strollers at the rail
    out.append('<polygon points="610,312 452,318 452,324 610,320" fill="#8A5A3A"/><polygon points="452,318 610,312 610,306 452,312" fill="#C89A6A"/>')
    out.append('<g stroke="#5A3A2A" stroke-width="1.6">' + "".join(f'<line x1="{x}" y1="{318 - (x - 452) * 0.035:.1f}" x2="{x}" y2="{330 - (x - 452) * 0.03:.1f}"/>' for x in range(456, 610, 14)) + "</g>")
    out.append('<polyline points="452,306 610,300" fill="none" stroke="#5A3A2A" stroke-width="1.6"/>')
    out.append('<rect x="452" y="324" width="158" height="10" fill="#E8B48A" opacity="0.25"/>')
    for px, h, col in ((478, 18, "#3E5A8A"), (488, 16, "#C85A6A"), (530, 17, "#F2C25A")):
        out.append(figure(px, 312 - (px - 452) * 0.035, h, col, seed=px, rim="#FFD890", pose={478: "lean_back", 488: "lean_back", 530: "walk"}[px], facing=-1, light=1))
    # Canada geese gliding, with their wakes
    for x, y, s_ in ((200, 332, 0.62), (222, 338, 0.7), (184, 344, 0.56)):
        out.append(f'<g transform="translate({x} {y}) scale({s_})">'
                   '<path d="M -26 4 L 22 4" stroke="#FFF4D0" stroke-width="2" opacity="0.7"/><path d="M -24 6 L -46 12 M -24 6 L -44 0" stroke="#FFFFFF" stroke-width="1.6" opacity="0.45"/>'
                   '<path d="M -20 0 Q -24 -10 -10 -12 L 8 -12 Q 14 -12 14 -4 L 12 0 Z" fill="#8A7460"/><path d="M -18 -6 Q -4 -10 8 -8" stroke="#C8B49A" stroke-width="1.6" fill="none"/>'
                   '<path d="M -20 -4 L -26 -8 L -22 -2 Z" fill="#2A2220"/>'
                   '<path d="M 8 -10 Q 10 -26 14 -30 L 18 -30 Q 15 -24 14 -10 Z" fill="#1E1A1A"/><path d="M 14 -31 Q 22 -32 24 -28 L 16 -27 Z" fill="#1E1A1A"/>'
                   '<path d="M 14 -28 Q 16 -24 18 -27" stroke="#FFFFFF" stroke-width="2" fill="none"/></g>')
    # near bank: lawn, the lakeside path, joggers, a picnic with a basket of Georgia peaches
    out.append(f'<path d="M -10 372 Q 200 358 400 364 Q 520 368 610 360 L 610 444 L -10 444 Z" fill="url(#{u}-lawn)"/>')
    out.append('<path d="M -10 372 Q 200 358 400 364 Q 520 368 610 360 L 610 366 Q 520 374 400 370 Q 200 364 -10 378 Z" fill="#3E5A3A" opacity="0.6"/>')
    out.append(f'<path d="M -10 392 Q 220 376 400 384 Q 520 390 610 380 L 610 398 Q 520 408 400 402 Q 220 394 -10 412 Z" fill="url(#{u}-path)"/>')
    out.append(grass(160, 15, (-10, 372, 610, 444), ["#A8C468", "#7A9A4A", "#C8D888", "#5E7E3E"], h=(4, 12)))
    # two runners on the lakeside path, painted close enough to read: running tights and a tank, a tee and shorts
    out.append(f'<ellipse cx="350" cy="404" rx="70" ry="4" fill="#3A4A2A" opacity="0.18"/>')
    out.append(F.person(392, 403, 84, "jog", -1, {"top": "#3E7AB8", "top_kind": "tee", "bottom": "#1E1E2A", "bottom_kind": "shorts", "skin": "#8E5A3A",
                                                 "shoes": "#E6E0D6", "form": "m", "hair_style": "buzz", "hair": "#1C1412"}, seed=392, rim="#FFD08A", light=1))
    out.append(F.person(338, 405, 80, "jog", -1, {"top": "#E8506E", "top_kind": "tank", "bottom": "#2A2A3A", "bottom_kind": "trousers", "skin": "#E8B48E",
                                                 "shoes": "#F2F0EA", "form": "f", "hair_style": "ponytail", "hair": "#6E4426", "hat_kind": "cap", "hat": "#2E4A6A"},
                        seed=338, rim="#FFD08A", light=1))
    # her dog trotting alongside on a loose lead (painted like the people: shaded body, rim light)
    dp = F.Painter(0.9, 1, "#FFD08A", None, 2)
    F._dog(dp, 0, 0, 1.0, "#C8884A", facing=-1)
    out.append('<ellipse cx="284" cy="407" rx="16" ry="2.4" fill="#2A3A1A" opacity="0.2"/>')
    out.append(f'<g transform="translate(290 406) scale(0.9)">' + "".join(dp.out) + '</g>')
    out.append('<path d="M 284 360 L 266 376" stroke="#3A2A2A" stroke-width="1.2" opacity="0"/>')
    # picnic: gingham blanket, a woven basket of peaches, two peaches rolled out on the cloth
    out.append('<g transform="translate(150 424)"><polygon points="-70,0 40,-22 104,4 -10,30" fill="#F4F0E8"/>')
    gg = []
    for i in range(1, 8):
        t = i / 8
        gg.append(f'<line x1="{-70 + 110 * t:.1f}" y1="{0 - 22 * t:.1f}" x2="{-10 + 114 * t:.1f}" y2="{30 - 26 * t:.1f}"/>')
        gg.append(f'<line x1="{-70 + 60 * t:.1f}" y1="{0 + 30 * t:.1f}" x2="{40 + 64 * t:.1f}" y2="{-22 + 26 * t:.1f}"/>')
    out.append(f'<g stroke="#E8707A" stroke-width="4.5" opacity="0.55">' + "".join(gg) + "</g></g>")
    out.append('<g transform="translate(160 414)"><ellipse cx="0" cy="12" rx="34" ry="6" fill="#3E5A3A" opacity="0.35"/>'
               '<path d="M -28 -8 L 28 -8 L 22 14 L -22 14 Z" fill="#C8904A"/>'
               + "".join(f'<line x1="{-26 + i * 6.5:.1f}" y1="-8" x2="{-20 + i * 5:.1f}" y2="14" stroke="#9A6A32" stroke-width="1.5"/>' for i in range(9))
               + "".join(f'<path d="M -26 {y} L 26 {y}" stroke="#E8B870" stroke-width="1.5" opacity="0.7"/>' for y in (-2, 5, 11))
               + '<path d="M -24 -8 Q 0 -44 24 -8" fill="none" stroke="#9A6A32" stroke-width="4"/></g>')
    for x, y, r, rot in ((146, 404, 10, -10), (166, 403, 11, 15), (156, 397, 10, 5), (176, 407, 9, 30), (138, 407, 8, -20), (212, 426, 11, 20), (230, 432, 10, -15)):
        out.append(peach(x, y, r, rot))
    # dogwood boughs framing the view
    out.append(dogwood_branch([(-20, 54), (40, 74), (100, 84), (160, 102), (210, 128)], 3,
                              [(62, 68, 15), (98, 100, 17), (130, 78, 13), (170, 114, 15), (34, 94, 13), (200, 140, 12), (82, 56, 11)], leaves=7, w=7))
    out.append(dogwood_branch([(640, 104), (590, 118), (540, 140), (500, 170)], 4,
                              [(566, 104, 15), (536, 156, 14), (502, 180, 12), (588, 140, 13), (552, 126, 11)], leaves=6, w=6))
    out.append(dogwood_branch([(-20, 210), (30, 200), (70, 214)], 5, [(40, 186, 14), (70, 222, 12), (10, 226, 12)], leaves=4, w=5))
    return "\n".join(out)


# ================================================================ MEMPHIS (the Mississippi from Cobblestone Landing at sunset)
def neon_word(x, y, word, size, color, u, vertical=True):
    out = [glow(x, y + (len(word) * size * 0.95) / 2 if vertical else y, size * len(word) * 0.6, color, f"{u}-ng", 0.45)]
    for i, c in enumerate(word):
        yy = y + i * size * 0.95 + size * 0.8 if vertical else y
        xx = x if vertical else x + (i - len(word) / 2 + 0.5) * size * 0.7
        out.append(f'<text x="{xx:.1f}" y="{yy:.1f}" text-anchor="middle" {ANTON} font-size="{size:.1f}" fill="none" stroke="{color}" stroke-width="{size * 0.22:.1f}" stroke-linejoin="round" opacity="0.35">{c}</text>'
                   f'<text x="{xx:.1f}" y="{yy:.1f}" text-anchor="middle" {ANTON} font-size="{size:.1f}" fill="#FFF6F0" stroke="{color}" stroke-width="{size * 0.06:.1f}">{c}</text>')
    return "".join(out)


def memphis():
    u = "pd-memphis"
    out = [defs(
        lg(f"{u}-sky", [(0, "#1E2458"), (0.3, "#4A3A7A"), (0.55, "#B04A72"), (0.75, "#E8664A"), (0.9, "#F8A24A"), (1, "#FFD07A")], 0, 40, 0, 266, units="userSpaceOnUse"),
        lg(f"{u}-river", [(0, "#F2A05A"), (0.2, "#C8645A"), (0.55, "#6A4A6E"), (1, "#2E2E4E")], 0, 262, 0, 356, units="userSpaceOnUse"),
        lg(f"{u}-pyr", [(0, "#F6C4A0"), (0.5, "#C88A8E"), (1, "#5E4A6E")], 0, 0, 1, 0),
        lg(f"{u}-brick", [(0, "#8A3E34"), (1, "#5A2A2E")], 0, 0, 1, 0),
        lg(f"{u}-cob", [(0, "#6A4A5A"), (1, "#2E2430")], 0, 346, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-door", [(0, "#FFE0A0"), (1, "#F09A4A")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(dots(30, 2, (0, 40, 600, 110), "#FFF0E0", r=(0.6, 1.2), opacity=(0.3, 0.8)))
    out.append(glow(150, 262, 280, "#FFC060", f"{u}-sun", 0.8))
    # long sunset clouds, burning underneath
    rc = random.Random(3)
    for cx, cy, w in ((120, 130, 220), (430, 110, 240), (300, 180, 160), (560, 168, 90)):
        for _ in range(10):
            x = cx + rc.uniform(-w / 2, w / 2) * 0.75
            y = cy + rc.uniform(-6, 6)
            rx = rc.uniform(0.14, 0.32) * w
            out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rx:.1f}" ry="{rc.uniform(3, 7):.1f}" fill="#6A3A6E" opacity="0.6"/>'
                       f'<ellipse cx="{x - 6:.1f}" cy="{y + 3:.1f}" rx="{rx * 0.8:.1f}" ry="2.6" fill="#FF9A5A" opacity="0.85"/>')
    out.append(glow(150, 260, 46, "#FFF2C8", f"{u}-sun2", 0.95))
    out.append('<path d="M 124 262 A 26 26 0 0 1 176 262 Z" fill="#FFF4D2"/>')
    # Arkansas shore: low woods on the far bank
    out.append(canopy_band(-10, 610, 266, 4, ["#3A2A4A", "#432E52", "#36284A"], h=(6, 14), n=260))
    # the Hernando de Soto bridge: two steel arches making an M, its light necklace just switched on
    def deck_y(x):
        return 246 + (x - 400) * 0.03
    out.append(f'<polygon points="{P([(-10, deck_y(-10)), (420, deck_y(420)), (420, deck_y(420) + 5), (-10, deck_y(-10) + 4)])}" fill="#3A2E4A"/>')
    for px in (-4, 44, 222, 400):   # piers
        out.append(f'<rect x="{px - 4}" y="{deck_y(px) + 4:.1f}" width="8" height="{266 - deck_y(px):.1f}" fill="#3A2E4A"/>')
    for i in range(10):            # approach spans to the left
        x0 = -10 + i * 7
        out.append(f'<line x1="{x0}" y1="{deck_y(x0) + 4:.1f}" x2="{x0}" y2="266" stroke="#3A2E4A" stroke-width="1.5" opacity="0.6"/>')
    arch_pts = []
    for (xa, xb, top) in ((44, 222, 176), (222, 400, 166)):
        pts = []
        for k in range(33):
            t = k / 32
            x = xa + (xb - xa) * t
            y = deck_y(x) - (deck_y(x) - top) * math.sin(math.pi * t) ** 0.85
            pts.append((x, y))
        arch_pts.append(pts)
        out.append(f'<polyline points="{P(pts)}" fill="none" stroke="#4A3E5E" stroke-width="5" stroke-linejoin="round"/>')
        out.append(f'<polyline points="{P(pts[:17])}" fill="none" stroke="#FFC890" stroke-width="1.6" opacity="0.7"/>')
        out.append('<g stroke="#4A3E5E" stroke-width="1.5">' + "".join(f'<line x1="{x:.1f}" y1="{y + 2:.1f}" x2="{x:.1f}" y2="{deck_y(x):.1f}"/>' for x, y in pts[2:-2:2]) + "</g>")
        out.append("".join(f'<circle cx="{x:.1f}" cy="{y - 2.6:.1f}" r="1.6" fill="#FFF0C0"/>' for x, y in pts[1:-1:2]))
    out.append(f'<polyline points="{P([(-10, deck_y(-10) - 2), (420, deck_y(420) - 2)])}" fill="none" stroke="#FFC890" stroke-width="1.2" opacity="0.5"/>')
    # the pyramid on the Tennessee bank, its steel skin mirroring the sunset
    pa, px0, px1 = (408, 190), 352, 462
    out.append(f'<polygon points="{P([(px0, 268), pa, (px1, 268)])}" fill="url(#{u}-pyr)"/>')
    out.append(f'<polygon points="{P([pa, (px1, 268), (424, 268)])}" fill="#4E3E62" opacity="0.6"/>')
    out.append('<g stroke="#FFE2C8" stroke-width="1" opacity="0.35">' + "".join(f'<line x1="{px0 + i * 7}" y1="268" x2="{pa[0] - 6 + i * 0.9:.1f}" y2="{pa[1] + 8}"/>' for i in range(1, 10))
               + "".join(f'<line x1="{px0 + (pa[0] - px0) * t:.1f}" y1="{268 - 78 * t:.1f}" x2="{px1 - (px1 - pa[0]) * t:.1f}" y2="{268 - 78 * t:.1f}"/>' for t in (0.2, 0.4, 0.6, 0.8)) + "</g>")
    out.append(f'<polyline points="{P([(px0, 268), pa])}" fill="none" stroke="#FFD8B0" stroke-width="1.8" opacity="0.8"/>')
    out.append(f'<path d="M {pa[0]} {pa[1]} L {pa[0]} {pa[1] - 8}" stroke="#4E3E62" stroke-width="1.6"/>')
    # downtown towers behind on the right
    for x, w, t in ((508, 26, 196), (536, 30, 176), (568, 40, 206)):
        out.append(f'<rect x="{x}" y="{t}" width="{w}" height="{270 - t}" fill="#3E3256"/>' + "".join(
            f'<rect x="{x + 3 + j * 6}" y="{yy}" width="2.6" height="2.4" fill="#FFD890" opacity="0.8"/>' for yy in range(t + 6, 266, 7) for j in range(int(w / 6)) if random.Random(x * yy + j).random() < 0.3))
    # the river, wide and slow, burning with the sky
    out.append(f'<rect x="-10" y="266" width="620" height="90" fill="url(#{u}-river)"/>')
    rr = random.Random(9)
    for i in range(90):
        y = 268 + (i / 90) ** 1.5 * 86
        w = rr.uniform(6, 22) * (0.5 + (y - 266) / 50)
        out.append(f'<rect x="{150 + rr.gauss(0, 8 + (y - 266) * 0.6) - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="1.8" rx="0.9" fill="#FFE8B0" opacity="{rr.uniform(0.5, 0.95):.2f}"/>')
    for i in range(50):
        y = 270 + (i / 50) ** 1.4 * 80
        x = rr.uniform(-10, 610)
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{rr.uniform(10, 40) * (0.5 + (y - 266) / 60):.1f}" height="1.4" fill="{rr.choice(["#F8B07A", "#B06A8A", "#E88A6A"])}" opacity="{rr.uniform(0.3, 0.6):.2f}"/>')
    # bridge necklace reflected in the water
    for pts in arch_pts:
        out.append("".join(f'<rect x="{x - 1:.1f}" y="{266 + (266 - y) * 0.55 + rr.uniform(-2, 2):.1f}" width="2" height="3" fill="#FFF0C0" opacity="0.35"/>' for x, y in pts[1:-1:3]))
    # the sternwheeler heading downriver, decks aglow, wake trailing
    bx, by = 250, 322
    out.append(f'<path d="M {bx - 110} {by + 3} Q {bx} {by + 10} {bx + 130} {by + 2}" fill="none" stroke="#FFD8B0" stroke-width="2" opacity="0.5"/>')
    out.append(f'<path d="M {bx + 82} {by + 2} L {bx + 200} {by + 14} M {bx + 82} {by + 6} L {bx + 190} {by + 22}" stroke="#FFE8C8" stroke-width="1.6" opacity="0.45"/>')
    out.append(f'<g transform="translate({bx} {by})">'
               # reflection
               '<rect x="-94" y="2" width="170" height="16" fill="#F6E6D8" opacity="0.18"/>'
               + "".join(f'<rect x="{-86 + i * 13}" y="{6 + (i % 3) * 3}" width="6" height="2" fill="#FFD890" opacity="0.5"/>' for i in range(12))
               # hull and paddlewheel
               + '<path d="M -100 -10 L 84 -10 L 80 2 L -88 2 Z" fill="#F4ECE4"/><rect x="-100" y="-12" width="184" height="4" fill="#B8343A"/>'
               '<rect x="78" y="-34" width="26" height="34" rx="3" fill="#B8343A"/>'
               + "".join(f'<line x1="{80 + i * 4}" y1="-34" x2="{80 + i * 4}" y2="0" stroke="#7A1E26" stroke-width="1.5"/>' for i in range(7))
               + '<rect x="78" y="-36" width="26" height="4" fill="#F4ECE4"/>'
               # main deck, cabin deck, texas deck, pilot house
               '<rect x="-92" y="-30" width="166" height="20" fill="#F7F0E8"/>'
               + "".join(f'<rect x="{-86 + i * 11}" y="-26" width="7" height="10" fill="#FFD890"/>' for i in range(14))
               + '<rect x="-96" y="-33" width="174" height="3" fill="#B8343A"/>'
               '<rect x="-76" y="-50" width="134" height="17" fill="#F7F0E8"/>'
               + "".join(f'<rect x="{-70 + i * 11}" y="-46" width="7" height="9" fill="#FFE2A0"/>' for i in range(12))
               + '<rect x="-80" y="-53" width="142" height="3" fill="#B8343A"/>'
               '<g stroke="#F7F0E8" stroke-width="1.5">' + "".join(f'<line x1="{-90 + i * 9}" y1="-33" x2="{-90 + i * 9}" y2="-30"/>' for i in range(19)) + '</g>'
               '<rect x="-46" y="-66" width="40" height="13" fill="#F7F0E8"/><rect x="-42" y="-63" width="32" height="6" fill="#FFE2A0"/><rect x="-48" y="-68" width="44" height="3" fill="#B8343A"/>'
               # twin stacks with feathered crowns
               '<rect x="-70" y="-92" width="7" height="40" fill="#2A2230"/><rect x="-56" y="-92" width="7" height="40" fill="#2A2230"/>'
               '<path d="M -73 -92 l 2 -6 l 2 4 l 2 -6 l 2 4 l 2 -6 l 1 10 Z M -59 -92 l 2 -6 l 2 4 l 2 -6 l 2 4 l 2 -6 l 1 10 Z" fill="#E8B84A"/>'
               '<path d="M 40 -53 L 40 -78 L 56 -74 L 40 -70" fill="#B8343A" stroke="#2A2230" stroke-width="1.2"/>'
               '<path d="M -100 -12 L -100 -30 M -100 -30 L -92 -30" stroke="#F7F0E8" stroke-width="1.5"/>'
               '<path d="M -100 -10 L -100 -32" stroke="#FFC890" stroke-width="1.5" opacity="0.8"/>'
               '</g>')
    out.append(glow(bx - 10, by - 30, 110, "#FFD890", f"{u}-boat", 0.3))
    # light smoke drifting from the stacks
    for k in range(6):
        out.append(f'<circle cx="{bx - 62 + k * 10}" cy="{by - 98 - k * 5}" r="{4 + k * 2}" fill="#C8A0B0" opacity="{0.35 - k * 0.05:.2f}"/>')
    # Cobblestone Landing sloping into the river
    out.append(f'<path d="M -10 352 Q 300 340 610 348 L 610 444 L -10 444 Z" fill="url(#{u}-cob)"/>')
    out.append('<path d="M -10 352 Q 300 340 610 348" fill="none" stroke="#F8B07A" stroke-width="2" opacity="0.6"/>')
    rcb = random.Random(17)
    for row in range(12):
        t = row / 11
        y = 354 + 90 * t ** 1.5
        h = 3 + 9 * t
        x = -10 + rcb.uniform(0, 20)
        while x < 610:
            w = (8 + 22 * t) * rcb.uniform(0.75, 1.25)
            sheen = 1 - abs(x - 150) / 400
            col = rcb.choice(["#5A4252", "#6A4E5E", "#4E3A4A", "#76586A"])
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w - 2:.1f}" height="{h:.1f}" rx="{h * 0.45:.1f}" fill="{col}"/>')
            if sheen > 0.2:
                out.append(f'<rect x="{x + w * 0.15:.1f}" y="{y + 0.6:.1f}" width="{w * 0.5:.1f}" height="{max(1.2, h * 0.22):.1f}" rx="1" fill="#FFB07A" opacity="{0.55 * sheen:.2f}"/>')
            x += w
    out.append(f'<path d="M 120 352 L 180 352 L 250 444 L 60 444 Z" fill="#F8A05A" opacity="0.12"/>')
    # a couple sitting on the stones, watching the sun go down
    out.append('<ellipse cx="116" cy="406" rx="34" ry="4" fill="#1E1820" opacity="0.5"/>')
    out.append(F.person(102, 404, 66, "sit_back", 1, {"top": "#3E5A8A", "form": "m"}, seed=51, rim="#FFB07A", light=-1, tint=("#3A2A3A", 0.15)))
    out.append(F.person(122, 404, 61, "sit_back", 1, {"top": "#C8463E", "form": "f", "hair_style": "long"}, seed=52, rim="#FFB07A", light=-1, tint=("#3A2A3A", 0.15)))
    # the blues club on the right: old brick, warm windows, a doorway spilling light, the neon blade sign
    out.append(f'<rect x="488" y="138" width="130" height="306" fill="url(#{u}-brick)"/>')
    out.append('<g stroke="#3A1E22" stroke-width="1" opacity="0.4">' + "".join(f'<line x1="488" y1="{y}" x2="620" y2="{y}"/>' for y in range(142, 444, 5)) + "</g>")
    out.append('<rect x="484" y="132" width="136" height="8" fill="#6A2E2E"/><rect x="484" y="132" width="136" height="2" fill="#F8B07A" opacity="0.7"/>')
    out.append('<rect x="488" y="138" width="4" height="306" fill="#F8A060" opacity="0.6"/>')
    for wy in (160, 222):
        for wx in (510, 556):
            out.append(f'<path d="M {wx} {wy + 40} L {wx} {wy + 10} Q {wx + 14} {wy - 2} {wx + 28} {wy + 10} L {wx + 28} {wy + 40} Z" fill="#FFD890"/>'
                       f'<path d="M {wx + 14} {wy + 2} L {wx + 14} {wy + 40} M {wx} {wy + 22} L {wx + 28} {wy + 22}" stroke="#6A2E2E" stroke-width="2"/>'
                       f'<rect x="{wx - 3}" y="{wy + 40}" width="34" height="4" fill="#C87A5A"/>')
    out.append(f'<rect x="512" y="320" width="56" height="112" fill="url(#{u}-door)"/><rect x="508" y="314" width="64" height="8" fill="#3A1E22"/>')
    out.append('<path d="M 540 320 L 540 432" stroke="#8A4A2A" stroke-width="2"/><circle cx="534" cy="380" r="2" fill="#8A4A2A"/>')
    out.append(glow(540, 380, 90, "#FFC870", f"{u}-dg", 0.45))
    out.append('<path d="M 512 432 L 568 432 L 600 444 L 470 444 Z" fill="#FFC870" opacity="0.3"/>')
    # string of bulbs across the facade
    bulbs = [(490 + i * 10, 300 + 6 * math.sin(i * 0.55)) for i in range(13)]
    out.append(f'<polyline points="{P(bulbs)}" fill="none" stroke="#2A1E22" stroke-width="1.2"/>' + "".join(
        glow(x, y + 3, 7, "#FFE2A0", f"{u}-sb{i}", 0.7) + f'<circle cx="{x}" cy="{y + 3:.1f}" r="2" fill="#FFF2C8"/>' for i, (x, y) in enumerate(bulbs)))
    # neon blade sign
    out.append('<rect x="458" y="152" width="34" height="140" rx="6" fill="#1E1428" stroke="#3E7AE8" stroke-width="3"/><rect x="476" y="160" width="12" height="4" fill="#2A2230"/>')
    out.append('<path d="M 488 170 L 492 170 M 488 274 L 492 274" stroke="#2A2230" stroke-width="3"/>')
    out.append(neon_word(475, 156, "BLUES", 24, "#3E8AFF", u))
    out.append('<rect x="460" y="154" width="30" height="136" rx="5" fill="none" stroke="#FF5A6A" stroke-width="1.6" opacity="0.8"/>')
    # lamp post on the landing
    out.append('<path d="M 430 432 L 430 318" stroke="#1E1820" stroke-width="5"/><path d="M 424 432 L 436 432 L 440 440 L 420 440 Z" fill="#1E1820"/>'
               '<path d="M 420 306 L 440 306 L 437 320 L 423 320 Z" fill="#FFE8B0"/><path d="M 418 306 L 430 296 L 442 306 Z" fill="#1E1820"/><rect x="419" y="319" width="22" height="3" fill="#1E1820"/>')
    out.append(glow(430, 312, 50, "#FFE2A0", f"{u}-lamp", 0.7))
    # a bluesman on a crate under the lamp, guitar in his lap, case open for tips
    out.append('<g transform="translate(386 430)">'
               '<rect x="-16" y="-24" width="32" height="24" fill="#7A5A3E"/><path d="M -16 -16 L 16 -16 M -16 -8 L 16 -8" stroke="#5A3E2A" stroke-width="1.5"/>'
               '</g>')
    out.append(F.person(386, 406, 84, "guitar", 1, {"top": "#2E3A5A", "top_kind": "jacket", "bottom": "#1E1820", "bottom_kind": "trousers", "skin": "#4A3228",
                                                   "hat_kind": "fedora", "hat": "#1E1820", "form": "m", "hair_style": "short", "shoes": "#2A2230", "inner": "#E8DCC8"},
                        seed=61, rim="#FFC870", light=1))
    out.append('<g transform="translate(330 436)"><path d="M -24 0 L 20 0 L 24 -6 L -20 -6 Z" fill="#2A1E1A"/><path d="M -20 -6 L 20 -6 L 16 -3 L -16 -3 Z" fill="#8A2A3A"/>'
               '<circle cx="-6" cy="-4" r="1.6" fill="#E8C24A"/><circle cx="2" cy="-4" r="1.6" fill="#E8C24A"/><rect x="6" y="-6" width="6" height="3" fill="#7AAA6A"/></g>')
    # music in the air: a few drifting notes from his guitar
    for x, y, r in ((404, 372, -10), (420, 350, 8), (440, 334, -6)):
        out.append(f'<g transform="translate({x} {y}) rotate({r})" fill="#FFE2A0" opacity="0.85"><ellipse cx="0" cy="0" rx="3.4" ry="2.6" transform="rotate(-20)"/><rect x="2.4" y="-12" width="1.6" height="12"/><path d="M 4 -12 q 5 2 4 7" stroke="#FFE2A0" stroke-width="1.6" fill="none"/></g>')
    out.append('<g fill="none" stroke="#2A1E2E" stroke-width="2.2" stroke-linecap="round"><path d="M 300 132 q 6 -5 12 0 q 6 -5 12 0"/><path d="M 330 148 q 4 -3 8 0 q 4 -3 8 0"/></g>')
    return "\n".join(out)


BUILD = {
    "memphis": (memphis, "MEMPHIS", "TENNESSEE · USA", "#1C1A3A", "#3E8AFF", "#FBEBD4", "#F8B07A"),
    "atlanta": (atlanta, "ATLANTA", "GEORGIA · EST. 1837", "#1E3A2E", "#F4A27A", "#FBEBD4", "#F7B98A"),
    "san-antonio": (san_antonio, "SAN ANTONIO", "TEXAS · RIVER WALK", "#17423E", "#F0568A", "#FBEBD4", "#F7D06A"),
    "santa-fe": (santa_fe, "SANTA FE", "NEW MEXICO · EST. 1610", "#2A2450", "#2FB0A8", "#FBEBD4", "#F7B2A6"),
    "sedona": (sedona, "SEDONA", "ARIZONA · RED ROCKS", "#3A1A2E", "#F0703A", "#FBEBD4", "#F6B07A"),
    "arches": (arches, "ARCHES", "UTAH · NATIONAL PARK", "#24345A", "#F07A3A", "#FBEBD4", "#F6C08A"),
    "monument-valley": (monument_valley, "MONUMENT VALLEY", "UTAH · ARIZONA", "#2E1E3E", "#F2A060", "#FBEBD4", "#FFC890"),
    "austin": (austin, "AUSTIN", "TEXAS · USA", "#1A1C3C", "#F29A5A", "#FBEBD4", "#F6C27A"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("places", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
