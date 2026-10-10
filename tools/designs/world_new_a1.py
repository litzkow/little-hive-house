"""World Places, painted edition — batch A1: Lisbon, Porto, Amsterdam, Barcelona, Florence, Pisa and the
Amalfi Coast. Same travel-poster idiom as world_painted.py: a real viewpoint (often a perspective camera), a
time of day with a light direction, atmospheric depth, texture and small storytelling details."""
import math
import random
import sys

from paint import (P, blobs, conifer, dots, glow, grass, lg, mist, rg, ridge_poly, rough, streaks, tree_line, y_on)
from places_painted import Cam, palm_tree
from world_painted import (Q, cumulus, defs, figure, gulls, leaf_canopy, lerp, mix, streak_cloud, umbrella_pine,
                           water_lines)
from common import MONO
from poster import ANTON, poster


def proj(C, X, pts):
    """Project (Z, Y) points lying in the facade plane X."""
    return [C(X, y, z) for z, y in pts]


def hline(C, X, z0, z1, y, color, w, op=1.0, dy0=0.0, dy1=0.0):
    a, b = C(X, y + dy0, z0), C(X, y + dy1, z1)
    return f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{color}" stroke-width="{w:.2f}" opacity="{op}"/>'


def cypress_tree(x, base, h, seed, dark="#1E3226", mid="#2E4A34", lit="#6E8A4E", w=0.16, light=-1):
    """Tuscan cypress: a tall flame of foliage with ragged edges, lit on one side."""
    rnd = random.Random(seed)
    n = 18
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        y = base - h * t
        prof = math.sin(math.pi * min(1, 0.12 + t * 0.95)) ** 0.7 * (1 - t) ** 0.25
        ww = h * w * 0.5 * prof
        left.append((x - ww * rnd.uniform(0.82, 1.08), y))
        right.append((x + ww * rnd.uniform(0.82, 1.08), y))
    pts = left + right[::-1]
    side = left if light < 0 else right
    lit_pts = [(px, py) for px, py in side] + [(x + (px - x) * 0.25, py) for px, py in side[::-1]]
    return (Q(pts, mid) + Q(lit_pts, lit, ' opacity="0.6"')
            + Q([(x + (px - x) * 0.3, py) for px, py in (right if light < 0 else left)] + (right if light < 0 else left)[::-1], dark, ' opacity="0.7"'))


def roof_house(x, base, w, h, k, rnd, light=1):
    """Small Lisbon house seen from above: pastel wall, hipped terracotta roof with tile courses."""
    walls = [("#F4E6CC", "#D8C2A6"), ("#F2D27A", "#D2A85A"), ("#F0B8A0", "#CC8E7C"), ("#F8F2E6", "#D4CCBE"),
             ("#E8C8D8", "#C2A0B4"), ("#B8D2E0", "#8EAABE"), ("#F6DEB0", "#D4B888")]
    wall, wsh = rnd.choice(walls)
    rh = h * rnd.uniform(0.45, 0.7)
    out = [f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{wall}"/>',
           f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h * 0.18:.1f}" fill="{wsh}" opacity="0.7"/>']
    # windows in rows
    rows = max(1, int(h / (5.5 * k)))
    cols = max(1, int(w / (6 * k)))
    for r_ in range(rows):
        for c_ in range(cols):
            wx = x + (c_ + 0.5) * w / cols - 1.1 * k
            wy = base - h + h * 0.25 + r_ * 5.5 * k
            if wy + 3.2 * k > base:
                continue
            out.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{2.2 * k:.1f}" height="{3.2 * k:.1f}" fill="{rnd.choice(["#4A4A5A", "#3E5A4A", "#5A3E3A", "#4A4A5A"])}"/>')
    # hipped roof: left plane in shade, right plane lit
    ov = 1.2 * k
    top_y = base - h - rh
    ridge0, ridge1 = x + w * 0.3, x + w * 0.7
    out.append(Q([(x - ov, base - h), (ridge0, top_y), (ridge1, top_y), (x + w + ov, base - h)], "#C8603E"))
    out.append(Q([(x + w * 0.5, base - h), (ridge1, top_y), (x + w + ov, base - h)] if light > 0 else [(x - ov, base - h), (ridge0, top_y), (x + w * 0.5, base - h)], "#E88A5A"))
    out.append(Q([(x - ov, base - h), (ridge0, top_y), (x + w * 0.22, base - h)] if light > 0 else [(x + w * 0.78, base - h), (ridge1, top_y), (x + w + ov, base - h)], "#9A4430"))
    n = max(2, int(rh / (1.6 * k)))
    for i in range(1, n):
        t = i / n
        y = base - h - rh * t
        xa, xb = lerp(x - ov, ridge0, t), lerp(x + w + ov, ridge1, t)
        out.append(f'<line x1="{xa:.1f}" y1="{y:.1f}" x2="{xb:.1f}" y2="{y:.1f}" stroke="#8A3A2A" stroke-width="{max(0.6, 0.5 * k):.1f}" opacity="0.45"/>')
    out.append(f'<line x1="{x - ov:.1f}" y1="{base - h + 0.4:.1f}" x2="{x + w + ov:.1f}" y2="{base - h + 0.4:.1f}" stroke="#5A2E24" stroke-width="{max(0.8, 0.7 * k):.1f}" opacity="0.6"/>')
    if rnd.random() < 0.3:
        cx_ = x + w * rnd.uniform(0.25, 0.75)
        cy_ = base - h - rh * 0.55
        out.append(f'<rect x="{cx_ - 1.2 * k:.1f}" y="{cy_ - 4 * k:.1f}" width="{2.4 * k:.1f}" height="{4 * k:.1f}" fill="{wall}"/><rect x="{cx_ - 1.6 * k:.1f}" y="{cy_ - 4.6 * k:.1f}" width="{3.2 * k:.1f}" height="{0.9 * k:.1f}" fill="#9A4430"/>')
    return "".join(out)


# ================================================================ LISBON — the yellow tram climbing past a miradouro, late morning
def tile_field(x0, y0, x1, y1, step, cols, seed, kind="diamond"):
    """Azulejo field: rows of small motifs on a glazed white ground (2D)."""
    rnd = random.Random(seed)
    out = []
    j = 0
    y = y0 + step / 2
    while y < y1:
        x = x0 + (step / 2 if j % 2 else 0) + step / 2
        while x < x1:
            c = cols[0] if rnd.random() > 0.1 else cols[1]
            r = step * 0.36
            if kind == "diamond":
                out.append(f'<polygon points="{x:.1f},{y - r:.1f} {x + r:.1f},{y:.1f} {x:.1f},{y + r:.1f} {x - r:.1f},{y:.1f}" fill="{c}"/>')
            else:  # little quatrefoil
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.62:.1f}" fill="{c}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.25:.1f}" fill="#F6F4EE"/>')
            x += step
        y += step * 0.86
        j += 1
    return "".join(out)


def lisbon_house(x, base_l, base_r, w, h, style, seed, u, k):
    """House front facing the street; bottom edge follows the slope (base_l at x, base_r at x + w)."""
    rnd = random.Random(seed)
    top = base_l - h
    face = [(x, base_l + 2), (x, top), (x + w, top), (x + w, base_r + 2)]
    walls = {"azul": "#F6F4EE", "verde": "#F2F4EE", "ochre": "#F2C25A", "rosa": "#F0A890", "creme": "#F6E6C6", "lilac": "#DCC2DC"}
    wall = walls[style]
    cid = f"{u}-h{k}"
    out = [Q(face, wall), f'<clipPath id="{cid}"><polygon points="{P(face)}"/></clipPath>']
    g = []
    if style == "azul":
        g.append(tile_field(x, top, x + w, base_l, 7.2, ("#2E5EA8", "#1E3E7E"), seed))
    elif style == "verde":
        g.append(tile_field(x, top, x + w, base_l, 7.6, ("#3E8A6A", "#2A6A50"), seed, kind="flower"))
    # sunlight from the upper left: warm wash fading to the right, soft vertical weathering
    g.append(f'<rect x="{x}" y="{top}" width="{w}" height="{h + 30}" fill="url(#{u}-wash)"/>')
    g.append(streaks(int(w * h / 500), seed + 3, (x, top + 10, x + w, base_l), ["#7A6A5A", "#A08A70"], w=(0.8, 2), length=(10, 40), opacity=(0.06, 0.16), slant=0.02))
    # stone corner pilasters, plinth along the slope
    trim = "#FBF7EC" if style not in ("creme",) else "#E8C27A"
    g.append(f'<rect x="{x}" y="{top}" width="5" height="{h + 30}" fill="{trim}"/><rect x="{x + w - 5}" y="{top}" width="5" height="{h + 30}" fill="{trim}"/>')
    g.append(f'<rect x="{x + w - 2}" y="{top}" width="2" height="{h + 30}" fill="#000" opacity="0.08"/>')
    g.append(Q([(x, base_l - 16), (x + w, base_r - 16), (x + w, base_r + 3), (x, base_l + 3)], "#E2D6C2"))
    # floors of tall windows
    cols_ = max(2, int(w / 30))
    fh = 40
    nf = int((h - 50) / fh)
    shutter = rnd.choice(["#3E7A5A", "#2E5A7A", "#7A3A34"])
    for f_ in range(nf):
        wy = top + 22 + f_ * fh
        for c_ in range(cols_):
            wx = x + 8 + (c_ + 0.5) * (w - 16) / cols_ - 7.5
            if wy + 30 > min(base_l, base_r) - 18:
                continue
            g.append(f'<rect x="{wx - 2.5:.1f}" y="{wy - 3:.1f}" width="20" height="35" fill="{trim}"/>')
            g.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="15" height="30" fill="#3A3E50"/>')
            g.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="15" height="13" fill="#9EC6E2" opacity="0.45"/>')
            g.append(f'<line x1="{wx + 7.5:.1f}" y1="{wy:.1f}" x2="{wx + 7.5:.1f}" y2="{wy + 30:.1f}" stroke="{trim}" stroke-width="1.6"/>')
            g.append(f'<line x1="{wx:.1f}" y1="{wy + 13:.1f}" x2="{wx + 15:.1f}" y2="{wy + 13:.1f}" stroke="{trim}" stroke-width="1.4"/>')
            r = rnd.random()
            if r < 0.3:   # one shutter folded open
                g.append(f'<rect x="{wx + 15.5:.1f}" y="{wy:.1f}" width="6" height="30" fill="{shutter}"/>' + "".join(
                    f'<line x1="{wx + 15.5:.1f}" y1="{wy + 3 + i * 4:.1f}" x2="{wx + 21.5:.1f}" y2="{wy + 3 + i * 4:.1f}" stroke="#000" stroke-opacity="0.25" stroke-width="1"/>' for i in range(7)))
            elif r < 0.45:  # closed shutters
                g.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="15" height="30" fill="{shutter}"/>' + "".join(
                    f'<line x1="{wx:.1f}" y1="{wy + 3 + i * 4:.1f}" x2="{wx + 15:.1f}" y2="{wy + 3 + i * 4:.1f}" stroke="#000" stroke-opacity="0.25" stroke-width="1"/>' for i in range(7)))
            # wrought-iron balcony with a shadow on the wall
            if f_ < nf - 1 and rnd.random() < 0.7:
                g.append(f'<rect x="{wx - 5:.1f}" y="{wy + 33:.1f}" width="25" height="8" fill="#000" opacity="0.12"/>')
                g.append(f'<rect x="{wx - 5:.1f}" y="{wy + 29:.1f}" width="25" height="3" fill="#2E2A2E"/>')
                g.append(f'<path d="M {wx - 5:.1f} {wy + 17:.1f} L {wx + 20:.1f} {wy + 17:.1f}" stroke="#2E2A2E" stroke-width="1.8"/>'
                         + "".join(f'<line x1="{wx - 4 + i * 3:.1f}" y1="{wy + 17:.1f}" x2="{wx - 4 + i * 3:.1f}" y2="{wy + 29:.1f}" stroke="#2E2A2E" stroke-width="1"/>' for i in range(9)))
                if rnd.random() < 0.5:  # geraniums
                    g.append(blobs(9, seed * 7 + f_ * 3 + c_, (wx - 4, wy + 10, wx + 19, wy + 18), ["#E83A4A", "#FF6A6A", "#3E7A3A", "#5A9A44"], r=(2, 3.6), opacity=(0.95, 1), squash=1))
    # ground floor: door with fanlight, a barred window
    dx = x + w * rnd.uniform(0.18, 0.5)
    by = lerp(base_l, base_r, (dx - x) / w)
    g.append(f'<path d="M {dx:.1f} {by - 2:.1f} L {dx:.1f} {by - 36:.1f} Q {dx + 10:.1f} {by - 46:.1f} {dx + 20:.1f} {by - 36:.1f} L {dx + 20:.1f} {by - 2:.1f} Z" fill="{trim}"/>')
    g.append(f'<path d="M {dx + 3:.1f} {by - 2:.1f} L {dx + 3:.1f} {by - 34:.1f} Q {dx + 10:.1f} {by - 41:.1f} {dx + 17:.1f} {by - 34:.1f} L {dx + 17:.1f} {by - 2:.1f} Z" fill="{rnd.choice(["#5A3A2E", "#2E4A6A", "#3E6A4A"])}"/>')
    g.append(f'<line x1="{dx + 10:.1f}" y1="{by - 30:.1f}" x2="{dx + 10:.1f}" y2="{by - 2:.1f}" stroke="#000" stroke-opacity="0.3" stroke-width="1"/>')
    out.append(f'<g clip-path="url(#{cid})">' + "".join(g) + "</g>")
    # cornice and the terracotta eave, shadow beneath
    out.append(f'<rect x="{x - 3}" y="{top - 5}" width="{w + 6}" height="6" fill="{trim}"/><rect x="{x - 2}" y="{top + 1}" width="{w + 4}" height="5" fill="#000" opacity="0.14"/>')
    out.append(Q([(x - 8, top - 5), (x + 4, top - 18), (x + w - 4, top - 18), (x + w + 8, top - 5)], "#C2603E"))
    out.append(Q([(x - 8, top - 5), (x + 4, top - 18), (x + w * 0.45, top - 18), (x + w * 0.4, top - 5)], "#E28A5A"))
    out.append("".join(f'<path d="M {x - 6 + i * 6:.1f} {top - 4:.1f} q 3 -4 6 0" fill="none" stroke="#8A3A2A" stroke-width="1.2"/>' for i in range(int((w + 12) / 6))))
    if rnd.random() < 0.7:
        cxp = x + w * rnd.uniform(0.2, 0.8)
        out.append(f'<rect x="{cxp - 4:.1f}" y="{top - 30:.1f}" width="8" height="14" fill="{wall}"/><rect x="{cxp - 6:.1f}" y="{top - 33:.1f}" width="12" height="4" fill="#9A4430"/>')
    return "".join(out)


def tram_profile(x, base, k, ang, u):
    """Remodelado tram in profile climbing to the right, local units in metres, rear wheel contact at (x, base)."""
    g = [f'<g transform="translate({x:.1f} {base:.1f}) rotate({ang:.2f}) scale({k:.3f})">']
    sw = 1 / k
    # overhead wire and the trailing trolley pole
    g.append(f'<line x1="-5" y1="-6.1" x2="16" y2="-6.1" stroke="#2A2630" stroke-width="{1.6 * sw:.3f}"/>')
    g.append(f'<line x1="3.4" y1="-3.6" x2="-0.4" y2="-6.05" stroke="#2A2630" stroke-width="{2.2 * sw:.3f}" stroke-linecap="round"/>')
    g.append(f'<path d="M 3.0 -3.62 L 3.8 -3.62 L 3.6 -3.85 L 3.2 -3.85 Z" fill="#3A3640"/><circle cx="-0.4" cy="-6.05" r="{3 * sw:.3f}" fill="#2A2630"/>')
    # running gear
    for wx in (2.0, 6.6):
        g.append(f'<circle cx="{wx}" cy="-0.27" r="0.27" fill="#1A181C"/><circle cx="{wx}" cy="-0.27" r="0.1" fill="#8A8690"/>'
                 f'<rect x="{wx - 0.75}" y="-0.62" width="1.5" height="0.3" rx="0.08" fill="#2E2A32"/>')
    g.append('<path d="M 0.2 -0.5 L 8.4 -0.5 L 8.4 -0.95 L 0.2 -0.95 Z" fill="#26222A"/>')
    g.append('<path d="M 8.4 -0.55 L 9.15 -0.4 L 9.15 -0.3 L 8.4 -0.42 Z" fill="#3A3640"/><path d="M 0.2 -0.55 L -0.55 -0.4 L -0.55 -0.3 L 0.2 -0.42 Z" fill="#3A3640"/>')
    # body: rounded ends, yellow lower panel with a lit top edge, cream window band, white roof
    body = "M 0 -0.95 L 8.6 -0.95 Q 8.85 -0.95 8.85 -1.3 L 8.85 -3.05 Q 8.8 -3.3 8.5 -3.3 L 0.1 -3.3 Q -0.2 -3.3 -0.25 -3.05 L -0.25 -1.3 Q -0.25 -0.95 0 -0.95 Z"
    g.append(f'<path d="{body}" fill="url(#{u}-ty)"/>')
    g.append('<path d="M -0.25 -1.95 L 8.85 -1.95 L 8.85 -3.05 Q 8.8 -3.3 8.5 -3.3 L 0.1 -3.3 Q -0.2 -3.3 -0.25 -3.05 Z" fill="#F6F0DE"/>')
    g.append(f'<line x1="-0.25" y1="-1.95" x2="8.85" y2="-1.95" stroke="#D89A1A" stroke-width="{2 * sw:.3f}"/>')
    g.append(f'<line x1="-0.2" y1="-1.0" x2="8.8" y2="-1.0" stroke="#FFF2A8" stroke-width="{1.8 * sw:.3f}" opacity="0.8"/>')
    # panel seams on the yellow
    g.append(f'<g stroke="#C8901A" stroke-width="{1.1 * sw:.3f}" opacity="0.7">' + "".join(f'<line x1="{xx}" y1="-1.05" x2="{xx}" y2="-1.9"/>' for xx in (0.9, 2.5, 4.1, 5.7, 7.3)) + "</g>")
    # roof with a low monitor and a lit leading edge
    g.append('<path d="M 0 -3.3 L 8.6 -3.3 Q 8.6 -3.45 8.3 -3.48 L 0.3 -3.48 Q 0 -3.45 0 -3.3 Z" fill="#E6E0D0"/>')
    g.append('<rect x="1.2" y="-3.62" width="6.2" height="0.16" rx="0.06" fill="#D2CCBE"/>')
    g.append(f'<line x1="0.3" y1="-3.48" x2="8.3" y2="-3.48" stroke="#FFFFFF" stroke-width="{1.6 * sw:.3f}"/>')
    # side windows with passengers and sky reflections
    rnd = random.Random(28)
    for i in range(7):
        wx = 0.85 + i * 0.86
        g.append(f'<rect x="{wx:.2f}" y="-3.02" width="0.66" height="0.92" rx="0.08" fill="#34405A"/>')
        if rnd.random() < 0.65:
            hc = rnd.choice(["#2A1E1A", "#5A3A2A", "#C8B8A8", "#3A2A22"])
            sc = rnd.choice(["#C8574A", "#3E6A9A", "#E8C060", "#5A8A5A", "#8A5A9A"])
            g.append(f'<path d="M {wx + 0.12:.2f} -2.1 Q {wx + 0.33:.2f} -2.55 {wx + 0.54:.2f} -2.1 Z" fill="{sc}"/><circle cx="{wx + 0.33:.2f}" cy="-2.62" r="0.13" fill="{hc}"/>')
        g.append(f'<path d="M {wx:.2f} -2.3 L {wx + 0.66:.2f} -2.75 L {wx + 0.66:.2f} -2.95 Q {wx + 0.66:.2f} -3.02 {wx + 0.58:.2f} -3.02 L {wx + 0.3:.2f} -3.02 Z" fill="#B8D8EE" opacity="0.45"/>')
    # front: door, motorman's window, headlamp, number box
    g.append('<rect x="7.98" y="-3.02" width="0.72" height="2.0" rx="0.06" fill="#E8B21E"/>')
    g.append('<rect x="8.04" y="-2.96" width="0.6" height="0.86" rx="0.06" fill="#34405A"/><path d="M 8.04 -2.3 L 8.64 -2.7 L 8.64 -2.96 L 8.3 -2.96 Z" fill="#B8D8EE" opacity="0.5"/>')
    g.append(f'<line x1="8.34" y1="-2.0" x2="8.34" y2="-1.02" stroke="#B8801A" stroke-width="{1.2 * sw:.3f}"/>')
    g.append('<circle cx="8.38" cy="-2.62" r="0.12" fill="#2A1E1A"/>')
    g.append('<rect x="5.95" y="-3.27" width="0.9" height="0.24" rx="0.04" fill="#1E1E24"/>')
    g.append(f'<text x="6.4" y="-3.08" text-anchor="middle" {ANTON} font-size="0.22" fill="#FFD84A">28</text>')
    g.append('<path d="M 8.85 -1.55 L 9.0 -1.6 L 9.0 -1.25 L 8.85 -1.3 Z" fill="#E8E2D2"/>')
    g.append('<rect x="8.75" y="-0.98" width="0.3" height="0.2" fill="#26222A"/><rect x="-0.45" y="-0.98" width="0.3" height="0.2" fill="#26222A"/>')
    # rear platform window and tail lamp
    g.append('<rect x="-0.12" y="-2.96" width="0.52" height="0.86" rx="0.06" fill="#34405A"/>')
    g.append('<circle cx="-0.18" cy="-1.4" r="0.07" fill="#E83A3A"/>')
    # shading: the shadow side under the window sill, the lit top
    g.append('<rect x="-0.25" y="-1.25" width="9.1" height="0.3" fill="#B8801A" opacity="0.35"/>')
    g.append("</g>")
    return "".join(g)


def lisbon():
    u = "lx"
    near = lambda x: 444 - 0.2 * (x + 10)
    far = lambda x: near(x) - 64
    ang = -math.degrees(math.atan(0.2))
    out = [defs(
        lg(f"{u}-sky", [(0, "#2A68B2"), (0.45, "#5E9CD6"), (0.8, "#A8D0EA"), (1, "#E2EEEC")], 0, 40, 0, 182, units="userSpaceOnUse"),
        lg(f"{u}-river", [(0, "#A6CCDE"), (0.3, "#6AA2C8"), (1, "#3A74A6")], 0, 178, 0, 232, units="userSpaceOnUse"),
        lg(f"{u}-street", [(0, "#6E6268"), (1, "#9A8E8A")], 0, 0, 0, 1),
        lg(f"{u}-haze", [(0, "#E2EEEC", 0), (1, "#E2EEEC", 0.7)], 0, 160, 0, 236, units="userSpaceOnUse"),
        lg(f"{u}-wash", [(0, "#FFF4D0", 0.32), (0.6, "#FFF4D0", 0.08), (1, "#3A3050", 0.08)], 0, 0, 1, 0),
        lg(f"{u}-ty", [(0, "#FFD43A"), (0.6, "#F8C424"), (1, "#E2A814")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(70, 60, 240, "#FFF8DC", f"{u}-sun", 0.75))
    out.append(cumulus(f"{u}-c1", 210, 108, 160, 46, 3, "#FFFFFF", "#F0F4F8", "#B4C6DC", light=-1))
    out.append(cumulus(f"{u}-c2", 420, 82, 120, 34, 9, "#FFFFFF", "#F0F4F8", "#BCCCE0", light=-1))
    out.append(streak_cloud(80, 150, 60, "#FFFFFF", 0.6, 3))
    # far shore of the Tagus with a white town and the monument on its bluff
    poly, _ = ridge_poly([(-10, 176), (80, 170), (170, 174), (250, 166), (330, 172), (420, 168), (610, 172)], 31, base=181, amp=3, fill="#8CA4BE")
    out.append(poly)
    out.append(dots(90, 33, (-10, 168, 400, 178), "#EEF2F2", r=(0.6, 1.3), opacity=(0.5, 0.9)))
    out.append('<g fill="#7A92AE"><rect x="236" y="148" width="6" height="22"/><rect x="233" y="146" width="12" height="3"/>'
               '<rect x="237.6" y="137" width="2.8" height="9"/><rect x="233" y="139.5" width="12" height="1.8"/><circle cx="239" cy="135.6" r="1.6"/></g>')
    out.append(f'<rect x="0" y="178" width="600" height="56" fill="url(#{u}-river)"/>')
    # the long red suspension bridge striding across the river from the left
    out.append('<path d="M -10 216 L 262 182" stroke="#A8382A" stroke-width="3"/><path d="M -10 219 L 262 184" stroke="#6A3A3A" stroke-width="1.2" opacity="0.6"/>')
    for tx, tb, tt, tw in ((52, 209, 128, 4.2), (184, 192, 146, 2.8)):
        out.append(f'<rect x="{tx - tw * 1.3:.1f}" y="{tt}" width="{tw:.1f}" height="{tb - tt + 14}" fill="#C4442E"/><rect x="{tx + tw * 0.3:.1f}" y="{tt}" width="{tw:.1f}" height="{tb - tt + 14}" fill="#C4442E"/>'
                   f'<rect x="{tx - tw * 1.3:.1f}" y="{tt + 6}" width="{tw * 2.6:.1f}" height="{tw * 0.5:.1f}" fill="#C4442E"/><rect x="{tx - tw * 1.3:.1f}" y="{tt + (tb - tt) * 0.5:.1f}" width="{tw * 2.6:.1f}" height="{tw * 0.5:.1f}" fill="#C4442E"/>'
                   f'<rect x="{tx + tw * 0.3:.1f}" y="{tt}" width="{tw * 0.5:.1f}" height="{tb - tt + 14}" fill="#FFB89A" opacity="0.6"/>')
    out.append('<path d="M -10 150 Q 22 196 52 128 Q 120 196 184 146 Q 226 186 262 180" fill="none" stroke="#B83E2C" stroke-width="1.6"/>')
    out.append('<g stroke="#B83E2C" stroke-width="0.8" opacity="0.7">' + "".join(
        f'<line x1="{x}" y1="{216 - (x + 10) * 34 / 272:.1f}" x2="{x}" y2="{(lambda t: (1 - t) ** 2 * 128 + 2 * t * (1 - t) * 196 + t * t * 146)((x - 52) / 132):.1f}"/>' for x in range(62, 180, 9)) + "</g>")
    # glitter, ripples, the orange ferry and a yacht
    rnd = random.Random(4)
    for _ in range(110):
        y = 180 + rnd.random() ** 1.3 * 50
        x = rnd.uniform(-10, 330)
        w = rnd.uniform(4, 14) * (0.5 + (y - 178) / 50)
        out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="1.2" rx="0.6" fill="{rnd.choice(["#FFFFFF", "#DCEEF6", "#2E6496"])}" opacity="{rnd.uniform(0.35, 0.85):.2f}"/>')
    out.append('<g transform="translate(236 210)"><path d="M -24 0 L 24 0 L 20 6 L -20 6 Z" fill="#E8742E"/><rect x="-16" y="-7" width="32" height="7" fill="#F6F2EA"/>'
               '<rect x="-12" y="-5" width="24" height="2.4" fill="#3A4A5E"/><rect x="-3" y="-13" width="7" height="6" fill="#F6F2EA"/><rect x="-1.6" y="-17" width="3.2" height="4" fill="#2A2A30"/>'
               '<path d="M -24 4 Q -44 6 -66 5" stroke="#FFFFFF" stroke-width="1.6" fill="none" opacity="0.7"/></g>')
    out.append('<g transform="translate(118 194)"><path d="M -8 0 L 8 0 L 6 3 L -6 3 Z" fill="#F6F2EA"/><line x1="0" y1="0" x2="0" y2="-20" stroke="#4A4A5A" stroke-width="1.2"/>'
               '<path d="M 1 -19 Q 9 -10 10 -1 L 1 -1 Z" fill="#FFFFFF"/><path d="M -1 -17 Q -7 -9 -8 -2 L -1 -2 Z" fill="#E8EEF2"/></g>')
    # the old town tumbling down to the river
    out.append(f'<rect x="0" y="170" width="600" height="70" fill="url(#{u}-haze)"/>')
    rnd = random.Random(42)
    rows = [(232, 0.55), (244, 0.68), (258, 0.82), (274, 0.98), (294, 1.18), (318, 1.42), (346, 1.72), (380, 2.06), (418, 2.4)]
    for ri, (yb, k) in enumerate(rows):
        x = rnd.uniform(-30, -10)
        while x < 340:
            w = rnd.uniform(14, 26) * k
            h = rnd.uniform(8, 15) * k
            out.append(roof_house(x, yb + rnd.uniform(-3, 3) * k, w, h, k, rnd, light=-1))
            if rnd.random() < 0.14:
                out.append(blobs(int(10 * k), ri * 100 + int(x), (x, yb - h * 0.7, x + w * 0.6, yb), ["#3E6A3A", "#5A8A44", "#2E5230"], r=(1.5 * k, 3 * k), opacity=(0.9, 1), squash=1))
            x += w + rnd.uniform(1, 5) * k
        if ri == 1:
            # monastery church with twin bell towers, catching the sun
            cx_, cb = 196, 262
            out.append(Q([(cx_ - 30, cb), (cx_ - 30, cb - 30), (cx_ + 30, cb - 30), (cx_ + 30, cb)], "#F6F0E4"))
            out.append(Q([(cx_ + 18, cb), (cx_ + 18, cb - 30), (cx_ + 30, cb - 30), (cx_ + 30, cb)], "#D8D0C4"))
            for tx in (cx_ - 30, cx_ + 20):
                out.append(f'<rect x="{tx}" y="{cb - 52}" width="11" height="52" fill="#FBF7EE"/><rect x="{tx + 7.5}" y="{cb - 52}" width="3.5" height="52" fill="#D8D0C4"/>'
                           f'<path d="M {tx - 1} {cb - 52} Q {tx + 5.5} {cb - 66} {tx + 12} {cb - 52} Z" fill="#ECE4D6"/><rect x="{tx + 3}" y="{cb - 47}" width="5" height="8" rx="2.5" fill="#5A5A6A"/>')
            out.append(Q([(cx_ - 18, cb - 30), (cx_, cb - 42), (cx_ + 18, cb - 30)], "#FBF7EE"))
            for i in range(4):
                out.append(f'<rect x="{cx_ - 15 + i * 8.5}" y="{cb - 24}" width="4" height="8" rx="2" fill="#6A6A7A"/>')
        if ri == 3:
            # the white-domed church
            dx, db = 66, 278
            out.append(f'<rect x="{dx - 20}" y="{db - 28}" width="40" height="28" fill="#F4EEE2"/><rect x="{dx + 8}" y="{db - 28}" width="12" height="28" fill="#D8D2C8"/><rect x="{dx - 13}" y="{db - 39}" width="26" height="11" fill="#F8F4EC"/>'
                       f'<path d="M {dx - 14} {db - 39} C {dx - 14} {db - 59} {dx + 14} {db - 59} {dx + 14} {db - 39} Z" fill="#FBF8F0"/>'
                       f'<path d="M {dx + 2} {db - 54} C {dx + 9} {db - 51} {dx + 14} {db - 46} {dx + 14} {db - 39} L {dx + 6} {db - 39} Z" fill="#D8D2C8"/>'
                       f'<rect x="{dx - 1.5}" y="{db - 64}" width="3" height="7" fill="#ECE6DA"/>')
    out.append(f'<rect x="0" y="226" width="600" height="20" fill="#E2EEEC" opacity="0.22"/>')

    # ---- the parapet of the miradouro along the far side of the street
    xP = 300
    par = [(-10, far(-10) - 30), (xP, far(xP) - 30), (xP, far(xP) + 2), (-10, far(-10) + 2)]
    out.append(Q(par, "#F2EADC"))
    out.append(Q([(-10, far(-10) - 34), (xP, far(xP) - 34), (xP, far(xP) - 27), (-10, far(-10) - 27)], "#E2C890"))
    out.append(Q([(-10, far(-10) - 27), (xP, far(xP) - 27), (xP, far(xP) - 24), (-10, far(-10) - 24)], "#000", ' opacity="0.12"'))
    out.append(f'<clipPath id="{u}-pc"><polygon points="{P(par)}"/></clipPath>')
    # an azulejo panel set into the wall
    out.append(f'<g clip-path="url(#{u}-pc)">' + tile_field(-10, 300, xP, 430, 6.4, ("#2E5EA8", "#1E3E7E"), 77)
               + Q([(-10, far(-10) - 24), (xP, far(xP) - 24), (xP, far(xP) - 20), (-10, far(-10) - 20)], "#F2EADC")
               + Q([(-10, far(-10) - 4), (xP, far(xP) - 4), (xP, far(xP) + 4), (-10, far(-10) + 4)], "#F2EADC") + "</g>")
    # people at the parapet enjoying the view, a cat sunning on the coping
    for px, h, c, hd in ((72, 46, "#2E4A7A", "#2A1E1A"), (88, 42, "#D8504A", "#6A3A22")):
        out.append(figure(px, far(px) + 2, h, c, head=hd, rim="#FFF2C8", rim_side=-1))
    cx_, cy_ = 256, far(256) - 34
    out.append(f'<g transform="translate({cx_:.1f} {cy_:.1f}) rotate({ang:.1f})"><path d="M -12 0 Q -14 -10 -4 -12 L -2 -17 L 1 -13 L 4 -17 L 5 -11 Q 8 -5 6 0 Z" fill="#3A2A2A"/>'
               '<path d="M -12 0 Q -22 2 -22 -7" fill="none" stroke="#3A2A2A" stroke-width="2.6" stroke-linecap="round"/><path d="M -4 -12 L -2 -17 L 1 -13" fill="none" stroke="#FFE6B0" stroke-width="1.2"/></g>')

    # ---- houses climbing on the right
    hs = [(300, 82, 186, "azul"), (382, 74, 196, "ochre"), (456, 78, 204, "verde"), (534, 86, 214, "rosa")]
    for k, (x, w, h, st) in enumerate(hs):
        out.append(lisbon_house(x, far(x), far(x + w), w, h, st, 11 + k, u, k))
    # laundry strung across a window, a wall lantern
    lx0, lx1, ly = 392, 446, 196
    out.append(f'<path d="M {lx0} {ly} Q {(lx0 + lx1) / 2} {ly + 8} {lx1} {ly}" fill="none" stroke="#4A4448" stroke-width="1"/>')
    rnd = random.Random(5)
    for i in range(5):
        t = (i + 0.5) / 5
        px = lerp(lx0, lx1, t)
        py = ly + 8 * math.sin(math.pi * t) * 0.95
        ww, hh = 8, rnd.uniform(9, 15)
        out.append(f'<rect x="{px - ww / 2:.1f}" y="{py:.1f}" width="{ww}" height="{hh:.1f}" fill="{rnd.choice(["#FFFFFF", "#E85A5A", "#5A8AD8", "#F2C84E", "#8AC0A0"])}"/><rect x="{px - ww / 2:.1f}" y="{py:.1f}" width="2" height="{hh:.1f}" fill="#000" opacity="0.1"/>')
    for lxp, lyp in ((382, far(382) - 70),):
        out.append(f'<path d="M {lxp} {lyp} L {lxp - 12} {lyp}" stroke="#2A2628" stroke-width="2"/>'
                   f'<path d="M {lxp - 18} {lyp + 2} L {lxp - 6} {lyp + 2} L {lxp - 8} {lyp + 16} L {lxp - 16} {lyp + 16} Z" fill="#F8ECC8" stroke="#2A2628" stroke-width="1.6"/>'
                   f'<path d="M {lxp - 19} {lyp + 2} L {lxp - 12} {lyp - 5} L {lxp - 5} {lyp + 2} Z" fill="#2A2628"/>')

    # ---- the street: setts, kerbs, rails
    st = [(-10, far(-10)), (610, far(610)), (610, near(610)), (-10, near(-10))]
    out.append(Q(st, "#857A7C"))
    out.append(f'<clipPath id="{u}-sc"><polygon points="{P(st)}"/></clipPath>')
    rnd = random.Random(7)
    sets = []
    for j in range(13):
        t = (j + 0.5) / 13
        for i in range(70):
            x = -10 + i * 9 + (4.5 if j % 2 else 0) + rnd.uniform(-1, 1)
            y = lerp(far(x), near(x), t)
            sets.append(f'<rect x="{x:.1f}" y="{y - 2:.1f}" width="7.4" height="{3.2 + t * 1.6:.1f}" rx="1.2" transform="rotate({ang:.1f} {x:.1f} {y:.1f})" fill="{rnd.choice(["#A2969A", "#948890", "#B2A8A6", "#7A6E74"])}" opacity="0.7"/>')
    out.append(f'<g clip-path="url(#{u}-sc)">' + "".join(sets) + "</g>")
    for t in (0.36, 0.64):
        out.append(f'<line x1="-10" y1="{lerp(far(-10), near(-10), t):.1f}" x2="610" y2="{lerp(far(610), near(610), t):.1f}" stroke="#3A3036" stroke-width="2.4"/>'
                   f'<line x1="-10" y1="{lerp(far(-10), near(-10), t) - 1.4:.1f}" x2="610" y2="{lerp(far(610), near(610), t) - 1.4:.1f}" stroke="#ECE6DE" stroke-width="1.1" opacity="0.85"/>')
    out.append(f'<line x1="-10" y1="{far(-10) + 1:.1f}" x2="610" y2="{far(610) + 1:.1f}" stroke="#D8CEC2" stroke-width="3"/>')
    # span wires from the houses to the overhead line
    # the tram, its shadow thrown back across the setts by the sun in front-left
    tx, tb = 112, None
    tb = lerp(far(112), near(112), 0.5) + 4
    out.append(Q([(tx + 20, tb), (tx + 300, tb - 56), (tx + 330, tb - 70), (tx + 50, tb - 14)], "#2E2430", ' opacity="0.3"'))
    out.append(tram_profile(tx, tb, 33, ang, u))
    out.append(f'<ellipse cx="{tx + 140:.1f}" cy="{tb - 26:.1f}" rx="150" ry="5" transform="rotate({ang:.1f} {tx + 140:.1f} {tb - 26:.1f})" fill="#1E1A20" opacity="0.0"/>')

    # ---- near pavement in calcada portuguesa, a lamp post, an old lady climbing with her shopping
    pv = [(-10, near(-10) + 2), (610, near(610) + 2), (610, 444), (-10, 444)]
    out.append(Q([(-10, near(-10)), (610, near(610)), (610, near(610) + 6), (-10, near(-10) + 6)], "#C8BEB2"))
    out.append(Q([(-10, near(-10) + 6), (610, near(610) + 6), (610, 444), (-10, 444)], "#F2ECE2"))
    out.append(f'<clipPath id="{u}-pv"><polygon points="{P(pv)}"/></clipPath>')
    bands = []
    for j in range(6):
        top_ = [(x, near(x) + 16 + j * 20 + 4 * math.sin(x * 0.09 + j * 1.3)) for x in range(-10, 620, 8)]
        bot = [(x, y + 4.5 + j * 0.5) for x, y in top_]
        bands.append(Q(top_ + bot[::-1], "#3A3640", ' opacity="0.8"'))
    out.append(f'<g clip-path="url(#{u}-pv)">' + "".join(bands) + dots(320, 9, (0, 300, 610, 444), "#B8B0A8", r=(0.6, 1.4), opacity=(0.3, 0.6)) + "</g>")
    lpx = 520
    lpb = near(lpx) + 26
    out.append(f'<rect x="{lpx - 3}" y="{lpb - 150}" width="6" height="150" fill="#2A2830"/><rect x="{lpx - 7}" y="{lpb - 18}" width="14" height="18" rx="2" fill="#2A2830"/>'
               f'<rect x="{lpx - 1}" y="{lpb - 150}" width="2" height="132" fill="#6A6A78"/>'
               f'<path d="M {lpx - 11} {lpb - 152} L {lpx + 11} {lpb - 152} L {lpx + 8} {lpb - 176} L {lpx - 8} {lpb - 176} Z" fill="#F8ECC8" stroke="#2A2830" stroke-width="2.4"/>'
               f'<path d="M {lpx - 13} {lpb - 176} L {lpx} {lpb - 188} L {lpx + 13} {lpb - 176} Z" fill="#2A2830"/><circle cx="{lpx}" cy="{lpb - 191}" r="3" fill="#2A2830"/>'
               f'<line x1="{lpx}" y1="{lpb - 176}" x2="{lpx}" y2="{lpb - 152}" stroke="#2A2830" stroke-width="1.4"/>')
    out.append(f'<ellipse cx="{lpx + 30}" cy="{lpb - 2}" rx="34" ry="4" fill="#2A2430" opacity="0.18"/>')
    ox = 452
    out.append(figure(ox, near(ox) + 30, 64, "#5A3A6A", head="#C8C0B8", legs="#3A2E36", rim="#FFF2C8", rim_side=-1, bag="#E8C060"))
    out.append(gulls([(330, 120, 12), (356, 134, 8), (40, 104, 10)], "#2E3A5A", 1.9))
    return "\n".join(out)


# ================================================================ PORTO — the Ribeira from the Gaia quay at dusk
def porto_house(x, base, w, h, k, rnd, lit_p=0.5, dusk="#4A4A7A", arcade=False):
    """Tall narrow riverfront house: coloured or tiled front, rows of windows (some lit), hipped tile roof."""
    walls = ["#E8B048", "#C8503E", "#E8DCC4", "#7EA2C0", "#D88A6A", "#F2D27A", "#A8C0A0", "#E6A8A0", "#F4EEE0", "#B85A4A"]
    wall = rnd.choice(walls)
    out = [f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{wall}"/>']
    if rnd.random() < 0.22:  # tiled front
        tc = rnd.choice(["#3E6AA8", "#3E8A6A", "#8A4A6A"])
        out.append(dots(int(w * h / (14 * k * k)), int(x * 7), (x, base - h, x + w, base - 2 * k), tc, r=(0.5 * k, 1.0 * k), opacity=(0.5, 0.9)))
    out.append(f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{dusk}" opacity="0.32"/>')
    out.append(f'<rect x="{x + w - 1.6 * k:.1f}" y="{base - h:.1f}" width="{1.6 * k:.1f}" height="{h:.1f}" fill="#1E1A30" opacity="0.25"/>')
    cols = max(1, int(w / (7 * k)))
    rows = max(1, int((h - 4 * k) / (8 * k)))
    for r_ in range(rows):
        wy = base - h + 3.5 * k + r_ * 8 * k
        if arcade and wy > base - 12 * k:
            continue
        for c_ in range(cols):
            wx = x + (c_ + 0.5) * w / cols - 1.6 * k
            on = rnd.random() < lit_p
            col = rnd.choice(["#FFD27A", "#FFC060", "#FFE2A0"]) if on else rnd.choice(["#2E2A44", "#3A3450", "#2A2840"])
            out.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{3.2 * k:.1f}" height="{4.8 * k:.1f}" fill="{col}"/>')
            if on and k > 0.8:
                out.append(f'<rect x="{wx - 0.6 * k:.1f}" y="{wy + 4.8 * k:.1f}" width="{4.4 * k:.1f}" height="{0.7 * k:.1f}" fill="#F4E8D0" opacity="0.7"/>')
            if k > 0.9 and r_ < rows - 1 and rnd.random() < 0.35:  # little iron balcony
                out.append(f'<rect x="{wx - 0.8 * k:.1f}" y="{wy + 3 * k:.1f}" width="{4.8 * k:.1f}" height="{1.8 * k:.1f}" fill="none" stroke="#1E1A28" stroke-width="{0.5 * k:.1f}"/>')
    if arcade:
        n = max(1, int(w / (9 * k)))
        for i in range(n):
            ax = x + (i + 0.5) * w / n
            aw = w / n * 0.62
            out.append(f'<path d="M {ax - aw / 2:.1f} {base:.1f} L {ax - aw / 2:.1f} {base - 6 * k:.1f} Q {ax:.1f} {base - 10 * k:.1f} {ax + aw / 2:.1f} {base - 6 * k:.1f} L {ax + aw / 2:.1f} {base:.1f} Z" fill="#FFB860"/>')
            out.append(f'<rect x="{ax - aw / 2:.1f}" y="{base - 3 * k:.1f}" width="{aw:.1f}" height="{3 * k:.1f}" fill="#7A3A2A" opacity="0.5"/>')
    # roof
    rh = rnd.uniform(3, 5) * k
    out.append(Q([(x - 0.8 * k, base - h), (x + w * 0.25, base - h - rh), (x + w * 0.75, base - h - rh), (x + w + 0.8 * k, base - h)], "#9A4A3E"))
    out.append(Q([(x - 0.8 * k, base - h), (x + w * 0.25, base - h - rh), (x + w * 0.45, base - h - rh), (x + w * 0.3, base - h)], "#C87058", ' opacity="0.8"'))
    if rnd.random() < 0.4:
        cx_ = x + w * rnd.uniform(0.2, 0.8)
        out.append(f'<rect x="{cx_ - 1 * k:.1f}" y="{base - h - rh - 2.5 * k:.1f}" width="{2 * k:.1f}" height="{3.5 * k:.1f}" fill="#7A4A44"/>')
    return "".join(out)


def rabelo(x, wl, k, sail=True, flip=False, barrels=6, seed=0, sail_col="#F4E6CC"):
    """Douro rabelo boat in profile, bow left: long flat hull, high stern platform with the steering oar,
    a stack of port barrels, one mast with a square sail. (x, wl) = mid-hull on the waterline, k px per metre."""
    sx = -k if flip else k
    rnd = random.Random(seed)
    g = [f'<g transform="translate({x:.1f} {wl:.1f}) scale({sx:.3f} {k:.3f})">']
    sw = 1 / k
    # hull: low curved planked boat, bow sweeping up
    g.append('<path d="M -11 -1.4 Q -10.6 -0.2 -8 0.35 L 8.5 0.35 Q 10.2 0 10.8 -1.6 L 10.6 -2.0 Q 0 -1.15 -10.8 -2.1 Z" fill="#4A2E24"/>')
    g.append('<path d="M -10.8 -2.1 Q 0 -1.15 10.6 -2.0 L 10.6 -1.55 Q 0 -0.75 -10.9 -1.65 Z" fill="#8A5A3A"/>')
    g.append(f'<path d="M -10.8 -2.1 Q 0 -1.15 10.6 -2.0" fill="none" stroke="#E8B888" stroke-width="{1.4 * sw:.3f}"/>')
    g.append(f'<g stroke="#2E1E18" stroke-width="{0.9 * sw:.3f}" opacity="0.6">' + "".join(
        f'<path d="M -10.6 {-1.3 + i * 0.4:.2f} Q 0 {-0.45 + i * 0.35:.2f} 10.4 {-1.2 + i * 0.4:.2f}" fill="none"/>' for i in range(3)) + "</g>")
    # bow post and the stern platform (apegada) with railing and the long steering oar (espadela)
    g.append('<path d="M -10.8 -2.1 L -11.6 -3.2 L -11.2 -3.3 L -10.3 -2.0 Z" fill="#4A2E24"/>')
    g.append('<path d="M 6.2 -2.0 L 6.2 -4.6 L 10.6 -4.6 L 10.6 -2.0 Z" fill="#6A4430"/><path d="M 6 -4.6 L 10.8 -4.6 L 10.8 -4.9 L 6 -4.9 Z" fill="#E8B888"/>')
    g.append(f'<g stroke="#3A2620" stroke-width="{1.1 * sw:.3f}">' + "".join(f'<line x1="{xx}" y1="-4.9" x2="{xx}" y2="-5.9"/>' for xx in (6.2, 7.4, 8.6, 9.8, 10.6)) + '<line x1="6.2" y1="-5.9" x2="10.6" y2="-5.9"/></g>')
    g.append(f'<line x1="8.4" y1="-7.6" x2="14.6" y2="0.6" stroke="#5A3A2A" stroke-width="{2.4 * sw:.3f}"/><path d="M 13.4 -1.0 L 15.4 0.2 L 14.6 1.6 L 12.9 0.3 Z" fill="#5A3A2A"/>')
    # barrels of port, stacked
    for i in range(barrels):
        bx = -6.6 + (i % 5) * 1.55
        by = -2.0 if i < 5 else -3.15
        if i >= 5:
            bx = -5.8 + (i - 5) * 1.55
        g.append(f'<rect x="{bx:.2f}" y="{by - 1.1:.2f}" width="1.4" height="1.15" rx="0.35" fill="#8A5A34"/>'
                 f'<rect x="{bx:.2f}" y="{by - 0.95:.2f}" width="1.4" height="0.12" fill="#3A3036"/><rect x="{bx:.2f}" y="{by - 0.2:.2f}" width="1.4" height="0.12" fill="#3A3036"/>'
                 f'<rect x="{bx + 0.15:.2f}" y="{by - 1.05:.2f}" width="0.3" height="1.0" fill="#E8B080" opacity="0.5"/>')
    # mast and square sail
    g.append(f'<line x1="-1.0" y1="-2.0" x2="-1.0" y2="-17" stroke="#3A2620" stroke-width="{2.2 * sw:.3f}"/>')
    if sail:
        g.append(f'<line x1="-5.2" y1="-16.2" x2="3.2" y2="-16.2" stroke="#3A2620" stroke-width="{1.8 * sw:.3f}"/>')
        g.append(f'<path d="M -5.0 -16.1 Q -1 -15.4 3.0 -16.1 Q 3.6 -10.5 3.2 -5.2 Q -1 -4.6 -5.2 -5.2 Q -5.6 -10.5 -5.0 -16.1 Z" fill="{sail_col}"/>')
        g.append('<path d="M -1 -15.6 Q 3.6 -10.5 3.2 -5.2 Q 1.2 -4.9 -1 -4.85 Z" fill="#000" opacity="0.08"/>')
        g.append(f'<path d="M -5.0 -16.1 Q -5.6 -10.5 -5.2 -5.2" fill="none" stroke="#FFD6A8" stroke-width="{1.6 * sw:.3f}"/>')
        for i, c in enumerate(("#B8303A", "#B8303A")):
            g.append(f'<path d="M {-5.25 + i * 0.0:.2f} {-12.2 + i * 1.6:.2f} Q -1 {-11.6 + i * 1.6:.2f} {3.35:.2f} {-12.2 + i * 1.6:.2f} L 3.35 {-11.6 + i * 1.6:.2f} Q -1 {-11.0 + i * 1.6:.2f} -5.3 {-11.6 + i * 1.6:.2f} Z" fill="{c}" opacity="0.85"/>')
        g.append(f'<g stroke="#3A2620" stroke-width="{0.8 * sw:.3f}" fill="none"><line x1="-5.2" y1="-5.2" x2="-8" y2="-2.1"/><line x1="3.2" y1="-5.2" x2="5.6" y2="-2.1"/><line x1="-1" y1="-17" x2="-10.8" y2="-2.2"/><line x1="-1" y1="-17" x2="8" y2="-4.6"/></g>')
    else:
        g.append(f'<line x1="-4.8" y1="-14.8" x2="3.0" y2="-14.8" stroke="#3A2620" stroke-width="{1.8 * sw:.3f}"/>')
        g.append(f'<path d="M -4.6 -14.8 Q -1 -13.6 2.8 -14.8 L 2.6 -14.1 Q -1 -12.8 -4.4 -14.1 Z" fill="{sail_col}"/>')
    g.append("</g>")
    return "".join(g)


def porto():
    u = "po"
    wl = 324
    out = [defs(
        lg(f"{u}-sky", [(0, "#1E2856"), (0.3, "#3E4682"), (0.58, "#8A6496"), (0.8, "#E08A8A"), (1, "#F6B884")], 0, 40, 0, 250, units="userSpaceOnUse"),
        lg(f"{u}-river", [(0, "#6A5A8A"), (0.25, "#3E3E70"), (1, "#1A1E3E")], 0, wl, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-iron", [(0, "#3A3046"), (1, "#241E30")]),
        lg(f"{u}-quay", [(0, "#6A5A64"), (1, "#3A3040")]),
        lg(f"{u}-haze", [(0, "#E8A0A0", 0), (1, "#E8A0A0", 0.35)], 0, 140, 0, 240, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(30, 236, 320, "#FFC890", f"{u}-dusk", 0.6))
    out.append(dots(40, 2, (220, 44, 600, 120), "#F6F0E8", r=(0.6, 1.3), opacity=(0.4, 0.9)))
    for x, y, w, c in ((110, 130, 100, "#F2A8A0"), (60, 150, 70, "#FFC8A0"), (300, 110, 120, "#B87A9E"), (460, 92, 90, "#8A6A9A"), (210, 168, 70, "#FFC09A")):
        out.append(streak_cloud(x, y, w, c, 0.65, 3.5))
    out.append(f'<path d="M 440 74 a 9 9 0 1 0 8 13 a 7 7 0 1 1 -8 -13 Z" fill="#FFF2D8"/>')
    # the hill of the old town, rows of houses from the top down to the river
    hill = rough([(-10, 196), (90, 186), (200, 176), (300, 160), (380, 150), (480, 158), (610, 150)], 5, amp=5, depth=3)
    out.append(Q(hill + [(610, wl), (-10, wl)], "#3A3058"))
    out.append(f'<clipPath id="{u}-hc"><polygon points="{P(hill + [(610, wl), (-10, wl)])}"/></clipPath>')
    out.append(f'<rect x="0" y="140" width="600" height="110" fill="url(#{u}-haze)"/>')
    rnd = random.Random(11)
    # the Clerigos-style baroque tower on the left hill, the cathedral's twin towers above the bridge
    tx = 118
    out.append(f'<rect x="{tx - 7}" y="118" width="14" height="76" fill="#5A4A6A"/><rect x="{tx + 2}" y="118" width="5" height="76" fill="#463A58"/>'
               f'<rect x="{tx - 9}" y="140" width="18" height="3" fill="#7A6A88"/><rect x="{tx - 9}" y="160" width="18" height="3" fill="#7A6A88"/>'
               f'<rect x="{tx - 5.5}" y="106" width="11" height="13" fill="#5A4A6A"/><path d="M {tx - 6.5} 106 Q {tx} 94 {tx + 6.5} 106 Z" fill="#5A4A6A"/>'
               f'<rect x="{tx - 0.8}" y="88" width="1.6" height="8" fill="#5A4A6A"/><rect x="{tx - 3}" y="91" width="6" height="1.4" fill="#5A4A6A"/>'
               f'<rect x="{tx - 3}" y="126" width="6" height="9" rx="3" fill="#FFD27A"/><rect x="{tx - 2.5}" y="109" width="5" height="7" rx="2.5" fill="#FFC060"/>')
    sx = 296
    out.append(f'<rect x="{sx - 30}" y="146" width="60" height="30" fill="#5E4E70"/>'
               + "".join(f'<rect x="{tx_}" y="130" width="15" height="46" fill="#62527A"/><rect x="{tx_ + 10}" y="130" width="5" height="46" fill="#4A3E5E"/>'
                         f'<path d="M {tx_ - 1} 130 L {tx_ + 16} 130 L {tx_ + 16} 126 L {tx_ - 1} 126 Z" fill="#7A6A90"/><path d="M {tx_ + 3} 126 Q {tx_ + 7.5} 116 {tx_ + 12} 126 Z" fill="#62527A"/>'
                         + "".join(f'<rect x="{tx_ + 2 + i * 4}" y="122" width="2" height="4" fill="#7A6A90"/>' for i in range(3)) for tx_ in (sx - 34, sx + 19))
               + f'<circle cx="{sx}" cy="156" r="7" fill="#FFD27A" opacity="0.85"/><circle cx="{sx}" cy="156" r="7" fill="none" stroke="#4A3E5E" stroke-width="1.6"/>')
    rows = [(198, 0.42, -0.05), (210, 0.5, -0.06), (224, 0.58, -0.06), (240, 0.68, -0.05), (258, 0.8, -0.04), (278, 0.94, -0.03)]
    for ri, (yb0, k, sl) in enumerate(rows):
        x = rnd.uniform(-20, -6)
        while x < 620:
            w = rnd.uniform(9, 16) * k
            h = rnd.uniform(18, 30) * k
            yb = yb0 + sl * x + rnd.uniform(-2, 2) * k
            out.append(porto_house(x, yb, w, h, k, rnd, lit_p=0.22 + ri * 0.05))
            if rnd.random() < 0.08:
                out.append(blobs(int(8 * k), ri * 300 + int(x), (x, yb - h * 0.5, x + w, yb), ["#2E3A3A", "#3E4A44"], r=(2 * k, 4 * k), opacity=(0.9, 1), squash=1))
            x += w + rnd.uniform(-0.5, 1.5) * k
        if ri < len(rows) - 1:
            out.append(f'<polygon points="-10,{yb0 + 4 - sl * 10:.1f} 610,{yb0 + 4 + sl * 610:.1f} 610,0 -10,0" fill="#4A3A6A" opacity="0.16" clip-path="url(#{u}-hc)"/>')
    # the riverfront row with its arcaded quay wall
    x = -12
    front = []
    while x < 380:
        w = rnd.uniform(14, 22) * 1.25
        h = rnd.uniform(50, 66)
        front.append((x, w, h))
        x += w
    for x, w, h in front:
        out.append(porto_house(x, wl - 12, w, h, 1.25, rnd, lit_p=0.55, arcade=True))
    out.append(Q([(-10, wl - 12), (390, wl - 12), (390, wl), (-10, wl)], "#6A5A6A"))
    out.append(f'<line x1="-10" y1="{wl - 12}" x2="390" y2="{wl - 12}" stroke="#C8A8A0" stroke-width="1.6"/>')
    # cafe umbrellas and strolling figures on the quay
    for ux in (40, 120, 200, 280):
        out.append(f'<path d="M {ux - 12} {wl - 22} Q {ux} {wl - 30} {ux + 12} {wl - 22} Z" fill="#E8E0D0"/><line x1="{ux}" y1="{wl - 22}" x2="{ux}" y2="{wl - 12}" stroke="#3A3040" stroke-width="1.2"/>')
    for px, c in ((70, "#2E3A6A"), (160, "#B8443E"), (236, "#3E5A4A"), (330, "#5A4A7A")):
        out.append(figure(px, wl - 12, 15, c, head="#2A1E22"))

    # ---- the double-deck iron arch bridge
    A0, A1, crown, xa = 360, 760, 154, 560
    def arch(x, d=0):
        t = (x - xa) / ((A1 - A0) / 2)
        return crown + d + (wl - 6 - crown) * t * t
    top = [(x, arch(x)) for x in range(A0, 612, 6)]
    bot = [(x, arch(x, 16 - 6 * abs((x - xa) / 200))) for x in range(A0 + 10, 612, 6)]
    out.append(Q(top + bot[::-1], f"url(#{u}-iron)"))
    out.append(f'<polyline points="{P(top)}" fill="none" stroke="#E89A8A" stroke-width="1.6" opacity="0.6"/>')
    out.append(f'<g stroke="#2A2434" stroke-width="1.2">' + "".join(
        f'<line x1="{x:.1f}" y1="{arch(x):.1f}" x2="{x + 12:.1f}" y2="{arch(x + 12, 16 - 6 * abs((x + 12 - xa) / 200)):.1f}"/>'
        f'<line x1="{x + 12:.1f}" y1="{arch(x + 12):.1f}" x2="{x:.1f}" y2="{arch(x, 16 - 6 * abs((x - xa) / 200)):.1f}"/>' for x in range(A0 + 12, 600, 12)) + "</g>")
    out.append(f'<g fill="#6A5A7A" opacity="0.7">' + "".join(f'<circle cx="{x}" cy="{arch(x, 8):.1f}" r="1.6"/>' for x in range(A0 + 18, 600, 24)) + "</g>")
    # upper deck on lattice piers, with lamps
    dk = 148
    out.append(Q([(318, dk - 2), (612, dk - 2), (612, dk + 7), (318, dk + 7)], "#2E2638"))
    out.append(f'<line x1="318" y1="{dk - 2}" x2="612" y2="{dk - 2}" stroke="#E8A090" stroke-width="1.4" opacity="0.7"/>')
    for px in range(330, 612, 16):
        y1 = arch(px) if px > A0 else 260
        if y1 - dk < 6:
            continue
        out.append(f'<line x1="{px}" y1="{dk + 7}" x2="{px}" y2="{y1:.1f}" stroke="#2A2434" stroke-width="2.4"/>')
        out.append(f'<line x1="{px - 8}" y1="{dk + 7}" x2="{px + 8}" y2="{min(y1, arch(px + 8) if px + 8 > A0 else 260):.1f}" stroke="#2A2434" stroke-width="0.9" opacity="0.8"/>')
    for lx in range(326, 612, 22):
        out.append(f'<line x1="{lx}" y1="{dk - 2}" x2="{lx}" y2="{dk - 10}" stroke="#2A2434" stroke-width="1"/><circle cx="{lx}" cy="{dk - 10}" r="1.8" fill="#FFE2A0"/>')
    out.append(glow(470, dk - 8, 90, "#FFD8A0", f"{u}-dg", 0.12))
    # a metro train crossing the top deck
    out.append(f'<rect x="420" y="{dk - 13}" width="70" height="11" rx="3" fill="#E8E4EA"/><rect x="424" y="{dk - 11}" width="62" height="4" fill="#FFD890"/><rect x="420" y="{dk - 4.5}" width="70" height="2" fill="#C8B020"/>')
    # stone pylons of the lower deck and the lower deck hung from the arch
    ld = wl - 34
    for px in (346, 368):
        out.append(f'<rect x="{px - 7}" y="{ld - 36}" width="14" height="{wl - ld + 36}" fill="#8A7A8A"/><rect x="{px + 3}" y="{ld - 36}" width="4" height="{wl - ld + 36}" fill="#6A5A70"/>'
                   f'<rect x="{px - 8}" y="{ld - 39}" width="16" height="4" fill="#A8909A"/><path d="M {px - 6} {ld - 39} L {px} {ld - 46} L {px + 6} {ld - 39} Z" fill="#7A6A7A"/>')
    out.append(Q([(352, ld), (612, ld), (612, ld + 6), (352, ld + 6)], "#2A2434"))
    out.append(f'<g stroke="#2A2434" stroke-width="1">' + "".join(f'<line x1="{x}" y1="{arch(x, 14):.1f}" x2="{x}" y2="{ld}"/>' for x in range(392, 612, 12) if arch(x, 14) < ld) + "</g>")
    for lx in range(360, 612, 18):
        out.append(f'<circle cx="{lx}" cy="{ld - 3}" r="1.6" fill="#FFE2A0"/>')

    # ---- the river: reflections of lights and the arch
    out.append(Q([(-10, wl), (610, wl), (610, 444), (-10, 444)], f"url(#{u}-river)"))
    rnd = random.Random(8)
    refl = []
    for x, w, h in front:
        for i in range(3):
            if rnd.random() < 0.7:
                xx = x + rnd.uniform(0.1, 0.9) * w
                for j in range(int(rnd.uniform(4, 9))):
                    yy = wl + 3 + j * 6 + rnd.uniform(-1, 1)
                    ww = rnd.uniform(2, 6) * (1 + j * 0.15)
                    refl.append(f'<rect x="{xx - ww / 2 + math.sin(j * 1.7 + i) * 2:.1f}" y="{yy:.1f}" width="{ww:.1f}" height="1.6" rx="0.8" fill="{rnd.choice(["#FFD27A", "#FFC060"])}" opacity="{0.8 - j * 0.07:.2f}"/>')
    out.append("".join(refl))
    out.append(f'<g stroke="#1E1A2E" stroke-width="3" opacity="0.5" fill="none"><path d="' + " ".join(
        f'M {x - 4:.1f} {2 * wl - arch(x) + 4 * math.sin(x * 0.3):.1f} l 8 0' for x in range(A0 + 6, 610, 5) if 2 * wl - arch(x) < 444) + '"/></g>')
    out.append(water_lines(120, 3, (-10, wl + 2, 610, 444), ["#8A6A9A", "#E8A0A0", "#2A2850", "#5A5088"], w=(10, 50), h=(0.8, 2.0), opacity=(0.25, 0.6)))
    out.append(Q([(-10, wl), (610, wl), (610, wl + 3), (-10, wl + 3)], "#F2B8A0", ' opacity="0.35"'))

    # ---- the rabelos moored off the Gaia quay
    out.append(rabelo(468, 382, 5.0, sail=False, seed=2, sail_col="#E8DCC8"))
    out.append(f'<path d="M 410 386 Q 470 392 530 386" stroke="#F2C0A8" stroke-width="1.4" fill="none" opacity="0.5"/>')
    out.append(rabelo(232, 404, 7.6, sail=True, seed=1))
    out.append(f'<path d="M 140 408 Q 230 416 330 408" stroke="#F2C0A8" stroke-width="1.8" fill="none" opacity="0.5"/>')
    # stone quay edge, a bollard with the mooring line, a gull
    out.append(Q([(-10, 426), (610, 430), (610, 444), (-10, 444)], f"url(#{u}-quay)"))
    out.append(f'<line x1="-10" y1="426" x2="610" y2="430" stroke="#C8A8A0" stroke-width="2"/>')
    out.append('<path d="M 96 428 L 96 414 Q 104 406 112 414 L 112 428 Z" fill="#2A2430"/><rect x="94" y="412" width="20" height="4" rx="2" fill="#3A3240"/>'
               '<path d="M 112 414 Q 140 420 160 406" fill="none" stroke="#C8A878" stroke-width="2"/>')
    out.append('<g transform="translate(104 405)"><path d="M -10 -6 Q -4 -12 6 -10 L 12 -8 L 6 -4 Q -2 -2 -10 -6 Z" fill="#E8E4EA"/><circle cx="-12" cy="-9" r="3.4" fill="#E8E4EA"/>'
               '<path d="M -15 -9 L -19 -8" stroke="#F2B040" stroke-width="1.6"/><path d="M -2 -10 Q 4 -12 10 -8 L 4 -6 Z" fill="#6A6A7A"/></g>')
    out.append(gulls([(190, 116, 11), (214, 128, 8), (520, 210, 9)], "#2A2444", 1.8))
    return "\n".join(out)


# ================================================================ AMSTERDAM — gabled houses across the gracht, a spring morning
def bike_parts(frame="#24242A", crate=None, tulips=None, seed=0):
    """Dutch upright bike in local metres: u along the bike (rear axle u=0, front axle u=1.12), v up.
    Returns a list of (kind, points, width_m, colour) — 'line' polylines or 'fill' polygons."""
    R = 0.34

    def circ(cu, cv, r, a0=0, a1=2 * math.pi, n=26):
        return [(cu + r * math.cos(a0 + (a1 - a0) * i / n), cv + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    p = []
    for cu in (0.0, 1.12):
        p.append(("line", circ(cu, R, R), 0.05, "#141418"))
        p.append(("line", circ(cu, R, R * 0.84), 0.016, "#A8A8B2"))
        p.append(("line", [(cu - 0.27, R - 0.05), (cu + 0.27, R + 0.05)], 0.008, "#8A8A94"))
        p.append(("line", [(cu - 0.05, R + 0.27), (cu + 0.05, R - 0.27)], 0.008, "#8A8A94"))
        p.append(("line", circ(cu, R, R + 0.05, 0.25, 2.9), 0.04, frame))          # mudguard
    bb, seat, head0, head1 = (0.46, 0.3), (0.3, 0.92), (0.98, 0.74), (0.95, 0.98)
    p.append(("line", [bb, seat], 0.045, frame))
    p.append(("line", [bb, (0.66, 0.56), head0], 0.05, frame))                      # low step-through tube
    p.append(("line", [(0.34, 0.74), (0.62, 0.62), head0], 0.04, frame))
    p.append(("line", [head0, head1], 0.055, frame))
    p.append(("line", [(0.0, R), bb], 0.03, frame))
    p.append(("line", [(0.0, R), (0.32, 0.86)], 0.03, frame))
    p.append(("line", [head0, (1.12, R)], 0.035, frame))
    p.append(("fill", [(0.12, 0.30), (0.6, 0.26), (0.62, 0.36), (0.14, 0.42)], 0, frame))   # chain guard
    p.append(("line", [head1, (0.92, 1.1), (0.78, 1.12)], 0.035, "#2A2A2E"))           # swept-back bars
    p.append(("line", [(0.74, 1.12), (0.82, 1.12)], 0.06, "#4A3226"))
    p.append(("fill", [(0.18, 0.95), (0.42, 0.97), (0.40, 1.02), (0.2, 1.01)], 0, "#3A2A22"))  # saddle
    p.append(("line", [(-0.14, 0.78), (0.3, 0.78)], 0.04, "#2A2A2E"))                  # rear rack
    p.append(("line", [(-0.12, 0.78), (0.0, R)], 0.02, "#2A2A2E"))
    if crate:
        p.append(("fill", [(1.0, 0.82), (1.46, 0.82), (1.46, 1.12), (1.0, 1.12)], 0, crate))
        p.append(("line", [(1.0, 0.92), (1.46, 0.92)], 0.02, "#00000055"))
        p.append(("line", [(1.0, 1.02), (1.46, 1.02)], 0.02, "#00000055"))
        if tulips:
            rnd = random.Random(seed)
            for i in range(9):
                cu = 1.04 + i * 0.048 + rnd.uniform(-0.01, 0.01)
                top = 1.3 + rnd.uniform(-0.05, 0.06)
                p.append(("line", [(cu, 1.1), (cu + rnd.uniform(-0.03, 0.03), top)], 0.018, "#3E7A3A"))
                c = rnd.choice(tulips)
                p.append(("fill", [(cu - 0.035, top), (cu - 0.03, top + 0.07), (cu - 0.012, top + 0.05), (cu, top + 0.085), (cu + 0.012, top + 0.05), (cu + 0.03, top + 0.07), (cu + 0.035, top), (cu, top - 0.03)], 0, c))
            p.append(("fill", [(1.02, 1.1), (1.1, 1.24), (1.06, 1.1)], 0, "#4E8A44"))
            p.append(("fill", [(1.42, 1.1), (1.36, 1.26), (1.38, 1.1)], 0, "#4E8A44"))
    return p


def render_parts(parts, mapf, scale, minw=0.7):
    out = []
    for kind, pts, w, col in parts:
        sp = [mapf(u_, v_) for u_, v_ in pts]
        if kind == "fill":
            out.append(f'<polygon points="{P(sp)}" fill="{col}"/>')
        else:
            out.append(f'<polyline points="{P(sp)}" fill="none" stroke="{col}" stroke-width="{max(minw, w * scale):.2f}" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(out)


def bike2d(x, base, s, frame="#24242A", flip=False, **kw):
    d = -1 if flip else 1
    return render_parts(bike_parts(frame, **kw), lambda u_, v_: (x + d * s * u_, base - s * v_), s)


def gable_outline(kind, w, hb, g):
    """Facade outline (metres, y up) of a canal house: body to hb, then the gable of height g."""
    L = [(0, 0), (0, hb)]
    if kind == "step":
        n, tw = 3, 0.3 * w
        dx, dh = (w - tw) / 2 / n, g / (n + 1)
        x, y = 0.0, hb
        for _ in range(n):
            y += dh
            L.append((x, y))
            x += dx
            L.append((x, y))
        L.append((x, hb + g))
        R = [(w - px, py) for px, py in L[2:]][::-1]
        return L + R + [(w, hb), (w, 0)]
    if kind == "bell":
        prof = [(0, 0.47), (0.12, 0.40), (0.3, 0.30), (0.5, 0.27), (0.68, 0.25), (0.82, 0.2), (0.92, 0.13), (0.98, 0.06), (1, 0)]
        left = [(w / 2 - hw * w, hb + t * g) for t, hw in prof]
        return L + left + [(w / 2 + hw * w, hb + t * g) for t, hw in prof[::-1]][1:] + [(w, hb), (w, 0)]
    if kind == "neck":
        nw = 0.24 * w
        left = [(0.03 * w, hb), (0.06 * w, hb + 0.18 * g), (0.16 * w, hb + 0.34 * g), (w / 2 - nw, hb + 0.46 * g), (w / 2 - nw, hb + 0.8 * g),
                (w / 2 - nw - 0.04 * w, hb + 0.8 * g), (w / 2, hb + g)]
        return L + left + [(w - px, py) for px, py in left[::-1]][1:] + [(w, hb), (w, 0)]
    if kind == "spout":
        left = [(0, hb), (w * 0.34, hb + g * 0.8), (w * 0.34, hb + g)]
        return L + left[1:] + [(w * 0.66, hb + g), (w * 0.66, hb + g * 0.8), (w, hb), (w, 0)]
    # cornice: flat top
    return L + [(0, hb + g), (w, hb + g), (w, hb), (w, 0)]


def canal_house(x0, y0, s, w, hb, g, kind, wall, seed, lean=0.0, trim="#F6F1E6", glass_top="#BCD6EA", sun=True):
    """Front of an Amsterdam canal house, drawn in metres inside a transform (s px/m) with its bottom-left at (x0, y0)."""
    rnd = random.Random(seed)
    sw = 1 / s
    out = [f'<g transform="translate({x0:.1f} {y0:.1f}) skewX({lean:.2f}) scale({s:.3f} {-s:.3f})">']
    ol = gable_outline(kind, w, hb, g)
    cid = f"am-h{seed}"
    out.append(f'<clipPath id="{cid}"><polygon points="{P(ol)}"/></clipPath>')
    out.append(f'<polygon points="{P(ol)}" fill="{wall}"/>')
    g_ = [f'<g clip-path="url(#{cid})">']
    brick = wall not in ("#EEE6D6", "#F2EEE4", "#DCE2DC", "#E6D6B8")
    if brick:
        g_.append(f'<g stroke="#000" stroke-width="{0.6 * sw:.3f}" opacity="0.09">' + "".join(
            f'<line x1="0" y1="{yy * 0.42:.2f}" x2="{w}" y2="{yy * 0.42:.2f}"/>' for yy in range(1, int((hb + g) / 0.42))) + "</g>")
        g_.append(dots(int(w * (hb + g) * 1.4), seed + 5, (0, 0, w, hb + g), "#2A1A14", r=(0.05, 0.12), opacity=(0.15, 0.35)))
    # morning light: warm from the upper left, a cooler foot
    g_.append(f'<rect x="0" y="0" width="{w}" height="{hb + g}" fill="url(#am-wash)"/>')
    # sandstone dressing on the gable edges and the base of the gable
    if kind in ("bell", "neck", "step"):
        gp = [p for p in ol if p[1] >= hb - 0.01]
        g_.append(f'<polyline points="{P(gp)}" fill="none" stroke="{trim}" stroke-width="0.5"/>')
    if kind == "neck":
        for sx in (1, -1):
            cx_ = w * 0.13 if sx > 0 else w * 0.87
            g_.append(f'<circle cx="{cx_:.2f}" cy="{hb + 0.16 * g:.2f}" r="{0.07 * w:.2f}" fill="none" stroke="{trim}" stroke-width="0.3"/>')
    if kind == "bell":
        g_.append(f'<path d="M {w * 0.06:.2f} {hb + 0.05:.2f} q {w * 0.06:.2f} {g * 0.12:.2f} {w * 0.14:.2f} {g * 0.06:.2f}" fill="none" stroke="{trim}" stroke-width="0.32"/>'
                  f'<path d="M {w * 0.94:.2f} {hb + 0.05:.2f} q {-w * 0.06:.2f} {g * 0.12:.2f} {-w * 0.14:.2f} {g * 0.06:.2f}" fill="none" stroke="{trim}" stroke-width="0.32"/>')
    if kind == "cornice":
        g_.append(f'<rect x="0" y="{hb + g - 0.55:.2f}" width="{w}" height="0.55" fill="{trim}"/><rect x="0" y="{hb + g - 0.8:.2f}" width="{w}" height="0.25" fill="#000" opacity="0.18"/>')
        g_.append("".join(f'<rect x="{0.2 + i * (w - 0.4) / 9:.2f}" y="{hb + g - 0.45:.2f}" width="0.18" height="0.3" fill="#000" opacity="0.12"/>' for i in range(10)))
    # string course under the gable
    g_.append(f'<rect x="0" y="{hb - 0.25:.2f}" width="{w}" height="0.25" fill="{trim}" opacity="0.9"/>')

    def window(xa, ya, ww, hh, panes_top=True, shutter=None):
        s_ = [f'<rect x="{xa - 0.14:.2f}" y="{ya - 0.14:.2f}" width="{ww + 0.28:.2f}" height="{hh + 0.28:.2f}" fill="{trim}"/>',
              f'<rect x="{xa:.2f}" y="{ya:.2f}" width="{ww:.2f}" height="{hh:.2f}" fill="url(#am-glass)"/>',
              f'<path d="M {xa:.2f} {ya + hh * 0.5:.2f} L {xa + ww:.2f} {ya + hh * 0.85:.2f} L {xa + ww:.2f} {ya + hh:.2f} L {xa + ww * 0.55:.2f} {ya + hh:.2f} Z" fill="#FFFFFF" opacity="0.18"/>']
        s_.append(f'<g stroke="{trim}" stroke-width="0.09">'
                  f'<line x1="{xa:.2f}" y1="{ya + hh * 0.52:.2f}" x2="{xa + ww:.2f}" y2="{ya + hh * 0.52:.2f}"/>'
                  f'<line x1="{xa + ww / 2:.2f}" y1="{ya:.2f}" x2="{xa + ww / 2:.2f}" y2="{ya + hh:.2f}"/>')
        if panes_top:
            s_.append(f'<line x1="{xa:.2f}" y1="{ya + hh * 0.76:.2f}" x2="{xa + ww:.2f}" y2="{ya + hh * 0.76:.2f}"/>'
                      f'<line x1="{xa + ww * 0.25:.2f}" y1="{ya + hh * 0.52:.2f}" x2="{xa + ww * 0.25:.2f}" y2="{ya + hh:.2f}"/>'
                      f'<line x1="{xa + ww * 0.75:.2f}" y1="{ya + hh * 0.52:.2f}" x2="{xa + ww * 0.75:.2f}" y2="{ya + hh:.2f}"/>')
        s_.append("</g>")
        # recess shadow: the sun from the upper left darkens the top and the right reveal
        s_.append(f'<rect x="{xa:.2f}" y="{ya + hh - 0.16:.2f}" width="{ww:.2f}" height="0.16" fill="#1A1420" opacity="0.45"/>'
                  f'<rect x="{xa + ww - 0.12:.2f}" y="{ya:.2f}" width="0.12" height="{hh:.2f}" fill="#1A1420" opacity="0.35"/>')
        s_.append(f'<rect x="{xa - 0.2:.2f}" y="{ya - 0.32:.2f}" width="{ww + 0.4:.2f}" height="0.2" fill="{trim}"/>')
        if shutter:
            for sx_ in (xa - 0.62, xa + ww + 0.16):
                s_.append(f'<rect x="{sx_:.2f}" y="{ya:.2f}" width="0.46" height="{hh:.2f}" fill="{shutter}"/>'
                          f'<path d="M {sx_:.2f} {ya:.2f} L {sx_ + 0.46:.2f} {ya + hh:.2f} M {sx_:.2f} {ya + hh:.2f} L {sx_ + 0.46:.2f} {ya:.2f}" stroke="{trim}" stroke-width="0.08"/>')
        return "".join(s_)

    bays = 3 if w > 6.2 else 2
    ww = 1.05 if bays == 3 else 1.2
    floors = [(1.5, 1.9), (4.5, 2.1), (7.6, 1.9)]
    if hb > 12:
        floors.append((10.5, 1.5))
    shut = rnd.choice([None, None, "#2E5A3E", "#7A2A2A"])
    for fi, (ya, hh) in enumerate(floors):
        if ya + hh > hb - 0.5:
            continue
        for b in range(bays):
            cx_ = w * (b + 0.5) / bays
            if fi == 0 and b == 0:
                continue
            g_.append(window(cx_ - ww / 2, ya, ww, hh, shutter=shut if fi == 0 else None))
    # front door up a stoop, with a fanlight; basement hatch beside the steps
    dx = w * 0.5 / bays
    g_.append(f'<rect x="{dx - 0.62:.2f}" y="1.1" width="1.24" height="2.5" fill="{trim}"/>'
              f'<rect x="{dx - 0.48:.2f}" y="1.1" width="0.96" height="2.0" fill="{rnd.choice(["#2A3A30", "#3A2622", "#1E2A3A", "#4A2A2A"])}"/>'
              f'<rect x="{dx - 0.48:.2f}" y="3.15" width="0.96" height="0.38" fill="url(#am-glass)"/>'
              f'<circle cx="{dx + 0.3:.2f}" cy="2.1" r="0.05" fill="#E8C060"/>')
    for i in range(3):
        g_.append(f'<rect x="{dx - 0.7 - i * 0.12:.2f}" y="{1.1 - (i + 1) * 0.3:.2f}" width="{1.4 + i * 0.24:.2f}" height="0.3" fill="#B8B0A8"/>'
                  f'<rect x="{dx - 0.7 - i * 0.12:.2f}" y="{1.1 - (i + 1) * 0.3:.2f}" width="{1.4 + i * 0.24:.2f}" height="0.06" fill="#5A5254" opacity="0.6"/>')
    g_.append(f'<path d="M {dx + 0.85:.2f} 0.2 L {dx + 0.85:.2f} 1.15 L {dx - 0.85:.2f} 1.15" fill="none" stroke="#1E1E22" stroke-width="0.06"/>')
    if bays == 3:
        g_.append(f'<rect x="{w * 0.5 - 0.5:.2f}" y="0.15" width="1.0" height="0.75" fill="#2A2830"/><rect x="{w * 0.83 - 0.5:.2f}" y="0.15" width="1.0" height="0.75" fill="#2A2830"/>')
    # windows and the hoist hatch in the gable, the hoist beam with its hook
    gy = hb + 0.5
    if kind != "cornice":
        if g > 3.2:
            for gx in ((w * 0.36, w * 0.64) if kind in ("step", "cornice") and w > 6 else (w * 0.5,)):
                g_.append(window(gx - 0.45, gy, 0.9, 1.3, panes_top=False))
        g_.append(f'<rect x="{w / 2 - 0.42:.2f}" y="{hb + g - 1.75:.2f}" width="0.84" height="1.05" fill="{rnd.choice(["#2E4A36", "#3A2A24", "#2A2A30"])}"/>'
                  f'<rect x="{w / 2 - 0.42:.2f}" y="{hb + g - 1.75:.2f}" width="0.84" height="1.05" fill="none" stroke="{trim}" stroke-width="0.12"/>')
    else:
        g_.append(f'<rect x="{w / 2 - 0.42:.2f}" y="{hb + 0.3:.2f}" width="0.84" height="1.0" fill="#2A2A30" stroke="{trim}" stroke-width="0.12"/>')
    if not brick:
        g_.append(streaks(int(w * 2), seed + 9, (0, 1, w, hb + g), ["#8A8478", "#B8B0A0"], w=(0.05, 0.14), length=(0.6, 2.4), opacity=(0.1, 0.25), slant=0.05))
    g_.append("</g>")
    out.append("".join(g_))
    beam_y = hb + g - 0.35 if kind != "cornice" else hb + g + 0.1
    out.append(f'<path d="M {w / 2:.2f} {beam_y:.2f} L {w / 2 + 0.06:.2f} {beam_y + 0.25:.2f} L {w / 2 + 0.1:.2f} {beam_y:.2f}" fill="#3A2A22"/>'
               f'<rect x="{w / 2 - 0.08:.2f}" y="{beam_y - 0.12:.2f}" width="0.16" height="0.28" fill="#3A2A22"/>'
               f'<line x1="{w / 2:.2f}" y1="{beam_y - 0.1:.2f}" x2="{w / 2:.2f}" y2="{beam_y - 0.75:.2f}" stroke="#2A2A2E" stroke-width="{1.2 * sw:.3f}"/>'
               f'<path d="M {w / 2:.2f} {beam_y - 0.75:.2f} q 0.14 -0.05 0.1 -0.18" fill="none" stroke="#2A2A2E" stroke-width="{1.2 * sw:.3f}"/>')
    if kind in ("bell", "neck"):  # crowning cap / pediment
        out.append(f'<path d="M {w / 2 - 0.55:.2f} {hb + g - 0.05:.2f} Q {w / 2:.2f} {hb + g + 0.55:.2f} {w / 2 + 0.55:.2f} {hb + g - 0.05:.2f} Z" fill="{trim}"/>')
    if kind == "step":
        out.append(f'<rect x="{w / 2 - 0.06:.2f}" y="{hb + g:.2f}" width="0.12" height="0.7" fill="#2A2A2E"/><circle cx="{w / 2:.2f}" cy="{hb + g + 0.75:.2f}" r="0.12" fill="#C8A040"/>')
    out.append("</g>")
    return "".join(out)


AMS_HOUSES = [  # X0, width, body height, gable height, kind, wall
    (-31.0, 6.4, 10.6, 3.4, "spout", "#5A3A30"),
    (-24.6, 7.2, 11.4, 4.6, "bell", "#8E4430"),
    (-17.4, 6.0, 12.2, 4.4, "neck", "#3A3E42"),
    (-11.4, 8.4, 12.8, 1.4, "cornice", "#EEE6D6"),
    (-3.0, 6.6, 11.2, 5.0, "step", "#A4553A"),
    (3.6, 5.8, 12.4, 4.6, "neck", "#E6D6B8"),
    (9.4, 7.0, 11.6, 4.2, "bell", "#5E3426"),
    (16.4, 6.2, 12.6, 3.8, "spout", "#2E3A36"),
    (22.6, 8.6, 12.0, 1.4, "cornice", "#C88A5A"),
]


def amsterdam():
    u = "am"
    C = Cam(f=520, cx=300, vpy=230, eye=4.0)
    ZF, ZQ, ZN, WL = 49.0, 46.0, 13.2, -1.4
    out = [defs(
        lg(f"{u}-sky", [(0, "#2F6DB8"), (0.4, "#5E98D2"), (0.75, "#A8CCE6"), (1, "#E4EEF0")], 0, 40, 0, 280, units="userSpaceOnUse"),
        lg(f"{u}-water", [(0, "#6E8E8A"), (0.25, "#4E6E70"), (1, "#24403E")], 0, 290, 0, 362, units="userSpaceOnUse"),
        lg(f"{u}-wash", [(0, "#FFF0C8", 0.0), (0.55, "#FFF0C8", 0.0), (1, "#FFF0C8", 0.22)], 0, 0, 1, 1),
        lg(f"{u}-glass", [(0, "#24303E"), (0.55, "#3E5068"), (1, "#8EB0CC")], 0, 0, 0, 1),
        lg(f"{u}-pave", [(0, "#9C8A80"), (1, "#7A665E")], 0, 360, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-brick", [(0, "#A85A44"), (1, "#7E3E30")], 0, 0, 0, 1),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(40, 40, 260, "#FFF6D8", f"{u}-sun", 0.7))
    # a big Dutch sky: towering cumulus built from many puffs, lit from the upper left
    out.append(cumulus(f"{u}-c1", 440, 150, 260, 92, 12, "#FFFFFF", "#EEF2F6", "#A8B8CE", hi="#FFFFFF", hi_op=0.8, light=-1))
    out.append(cumulus(f"{u}-c2", 130, 128, 170, 52, 5, "#FFFFFF", "#F0F4F8", "#B0C0D4", hi="#FFFFFF", hi_op=0.8, light=-1))
    out.append(cumulus(f"{u}-c3", 300, 92, 90, 22, 19, "#FFFFFF", "#F2F6FA", "#C2D0E0", light=-1))
    out.append(streak_cloud(240, 182, 70, "#FFFFFF", 0.5, 3))

    def house_px(X0):
        return C(X0, 0, ZF)
    s = C.f / ZF
    hs = []
    for i, (X0, w, hb, g, kind, wall) in enumerate(AMS_HOUSES):
        hs.append((X0, w, hb, g, kind, wall, 0.9 * math.sin(i * 2.3)))
    # side walls and steep roofs that show above lower neighbours (true perspective, deep plots behind)
    back = []
    for X0, w, hb, g, kind, wall, lean in hs:
        for Xe, face in ((X0 + w, 1), (X0, -1)):
            if (Xe < 0 and face == 1) or (Xe > 0 and face == -1):
                q = C.quad_x(Xe, ZF, ZF + 14, 0, hb)
                back.append(Q(q, mix(wall, "#20283A", 0.45 if face == 1 else 0.15)))
                back.append(Q(C.quad_x(Xe, ZF, ZF + 14, hb - 0.3, hb), "#000", ' opacity="0.2"'))
        if kind != "cornice":
            Xc = X0 + w / 2
            for Xe in ((X0 + w,) if Xc < 0 else (X0,)):
                pts = [C(Xe, hb, ZF), C(Xc, hb + g * 0.92, ZF), C(Xc, hb + g * 0.92, ZF + 13), C(Xe, hb, ZF + 13)]
                back.append(Q(pts, "#4A3A3E" if Xc < 0 else "#6A5050"))
                back.append(f'<g stroke="#2A2026" stroke-width="0.8" opacity="0.5">' + "".join(
                    f'<line x1="{lerp(pts[0][0], pts[1][0], t):.1f}" y1="{lerp(pts[0][1], pts[1][1], t):.1f}" x2="{lerp(pts[3][0], pts[2][0], t):.1f}" y2="{lerp(pts[3][1], pts[2][1], t):.1f}"/>' for t in (0.2, 0.4, 0.6, 0.8)) + "</g>")
    out.append("".join(back))
    facades = []
    for i, (X0, w, hb, g, kind, wall, lean) in enumerate(hs):
        x0, y0 = house_px(X0)
        facades.append(canal_house(x0, y0, s, w, hb, g, kind, wall, 300 + i, lean=lean))
    out.append(f'<g id="{u}-fac">' + "".join(facades) + "</g>")
    # elms along the far quay throw dappled shade across the fronts
    for Xt, ht, sp, sd in ((-20.5, 9.5, 5.2, 3), (6.2, 8.2, 4.4, 8)):
        bx, by = C(Xt, 0, ZQ + 1.2)
        st = C.f / (ZQ + 1.2)
        out.append(f'<g opacity="0.22" fill="#2A2430">' + "".join(
            f'<ellipse cx="{bx + st * (sp * 0.5 + dx):.1f}" cy="{by - st * (ht * 0.5 + dy):.1f}" rx="{st * r:.1f}" ry="{st * r * 0.7:.1f}"/>'
            for dx, dy, r in ((0, 0, 2.6), (1.8, 1.4, 1.8), (-1.6, 1.0, 1.6), (0.6, -1.6, 1.8))) + "</g>")
    # far quay: brick wall to the water, parked bikes, walkers
    qa, qb = C(-40, 0, ZQ), C(40, 0, ZQ)
    qw = C(0, WL, ZQ)[1]
    out.append(Q([(-10, house_px(0)[1]), (610, house_px(0)[1]), (610, qa[1]), (-10, qa[1])], "#8A7A74"))
    out.append(Q([(-10, qa[1]), (610, qa[1]), (610, qw), (-10, qw)], f"url(#{u}-brick)"))
    out.append(f'<rect x="-10" y="{qa[1]:.1f}" width="620" height="1.8" fill="#D8CCBE"/>')
    out.append(f'<g stroke="#5A2A22" stroke-width="0.6" opacity="0.4">' + "".join(f'<line x1="-10" y1="{qa[1] + 3 + j * 3:.1f}" x2="610" y2="{qa[1] + 3 + j * 3:.1f}"/>' for j in range(int((qw - qa[1] - 3) / 3) + 1)) + "</g>")
    sq = C.f / (ZQ + 0.6)
    yb = C(0, 0, ZQ + 0.6)[1]
    rnd = random.Random(21)
    for Xb in [-28.5, -27.2, -14.0, -12.8, -11.5, -1.0, 0.4, 2.0, 3.2, 19.0, 20.5, 25.0]:
        out.append(bike2d(C(Xb, 0, ZQ + 0.6)[0], yb, sq, frame=rnd.choice(["#24242A", "#24242A", "#3A5A6A", "#7A2E2A", "#E8E0CC"]), flip=rnd.random() < 0.5))
    for Xp, c in ((-8.0, "#C8463E"), (-6.8, "#2E4A6A"), (17.5, "#E0B04A")):
        out.append(figure(C(Xp, 0, ZF - 1.5)[0], C(Xp, 0, ZF - 1.5)[1], 1.75 * C.f / (ZF - 1.5), c, rim="#FFF2CC", rim_side=-1))
    # elm trunks and crowns
    for Xt, ht, sp, sd in ((-20.5, 9.5, 5.2, 3), (6.2, 8.2, 4.4, 8)):
        bx, by = C(Xt, 0, ZQ + 1.2)
        st = C.f / (ZQ + 1.2)
        out.append(f'<path d="M {bx - 0.22 * st:.1f} {by:.1f} Q {bx - 0.1 * st:.1f} {by - ht * 0.3 * st:.1f} {bx - 0.5 * st:.1f} {by - ht * 0.55 * st:.1f} L {bx + 0.4 * st:.1f} {by - ht * 0.55 * st:.1f} Q {bx + 0.2 * st:.1f} {by - ht * 0.3 * st:.1f} {bx + 0.25 * st:.1f} {by:.1f} Z" fill="#3A3230"/>'
                   f'<path d="M {bx - 0.22 * st:.1f} {by:.1f} Q {bx - 0.1 * st:.1f} {by - ht * 0.3 * st:.1f} {bx - 0.5 * st:.1f} {by - ht * 0.55 * st:.1f}" fill="none" stroke="#8A7A64" stroke-width="1.2"/>')
        out.append(leaf_canopy(f"{u}-t{sd}", bx, by - ht * 0.72 * st, sp * st, ht * 0.3 * st, sd, "#2E4A2A", "#4E7A34", "#9CC456", gold="#D8E68A", light=(-1, -1), n=110, r=(0.12, 0.24)))

    # the canal: reflections of the facades, broken by ripples
    yw = C(0, WL, ZQ)[1]
    ym = C(0, WL, ZF)[1]
    out.append(Q([(-10, yw), (610, yw), (610, 400), (-10, 400)], f"url(#{u}-water)"))
    out.append(f'<clipPath id="{u}-wc"><rect x="-10" y="{yw:.1f}" width="620" height="{400 - yw:.1f}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-wc)"><use href="#{u}-fac" opacity="0.42" transform="translate(0 {2 * ym:.1f}) scale(1 -1)"/>'
               f'<rect x="-10" y="{yw:.1f}" width="620" height="{400 - yw:.1f}" fill="url(#{u}-water)" opacity="0.45"/></g>')
    out.append(water_lines(170, 31, (-10, yw + 1, 610, 362), ["#E4EEF0", "#A8C4C8", "#1E3432", "#2E4A48"], w=(8, 46), h=(0.8, 2.0), opacity=(0.3, 0.75)))
    out.append(f'<rect x="-10" y="{yw:.1f}" width="620" height="2" fill="#1E2A2A" opacity="0.4"/>')
    # a pair of mallards paddling across, V-wakes behind them
    for dx_, dy_, head in ((262, 336, "#2E6A4A"), (284, 342, "#8A6A4A")):
        out.append(f'<path d="M {dx_ + 8} {dy_ + 1} L {dx_ + 34} {dy_ - 3} M {dx_ + 8} {dy_ + 2} L {dx_ + 34} {dy_ + 7}" stroke="#E4EEF0" stroke-width="1.1" opacity="0.6"/>'
                   f'<g transform="translate({dx_} {dy_})"><ellipse cx="4" cy="0" rx="8" ry="3.4" fill="{"#8A7A6A" if head != "#2E6A4A" else "#9A9690"}"/><path d="M 8 -1 Q 13 -5 11 1 Z" fill="#3A3230"/>'
                   f'<path d="M -1 -1 Q -2 -7 -5 -8" stroke="{head}" stroke-width="3.2" stroke-linecap="round" fill="none"/><circle cx="-5" cy="-8" r="2.6" fill="{head}"/><path d="M -7 -8 L -10 -7.4" stroke="#E8B030" stroke-width="1.6"/>'
                   f'<ellipse cx="4" cy="2.4" rx="9" ry="1.2" fill="#1E3432" opacity="0.4"/></g>')

    # houseboat moored along the far quay: hull, cabin with big windows, tulips on deck, a cat
    hz = 43.5
    sh_ = C.f / hz
    hx0, _ = C(-29, 0, hz)
    hx1, _ = C(-15.5, 0, hz)
    hw_ = C(0, WL, hz)[1]
    out.append(f'<g opacity="0.35" transform="translate(0 {2 * hw_:.1f}) scale(1 -1)"><rect x="{hx0:.1f}" y="{hw_ - 1.0 * sh_:.1f}" width="{hx1 - hx0:.1f}" height="{1.0 * sh_:.1f}" fill="#2E4A3A"/><rect x="{hx0 + 1.4 * sh_:.1f}" y="{hw_ - 3.2 * sh_:.1f}" width="{hx1 - hx0 - 2.6 * sh_:.1f}" height="{2.2 * sh_:.1f}" fill="#E8E0CC"/></g>')
    out.append(f'<rect x="{hx0:.1f}" y="{hw_ - 1.1 * sh_:.1f}" width="{hx1 - hx0:.1f}" height="{1.1 * sh_:.1f}" fill="#2E4A3A"/><rect x="{hx0:.1f}" y="{hw_ - 1.1 * sh_:.1f}" width="{hx1 - hx0:.1f}" height="2" fill="#E8C060"/>'
               f'<rect x="{hx0:.1f}" y="{hw_ - 0.3 * sh_:.1f}" width="{hx1 - hx0:.1f}" height="{0.3 * sh_:.1f}" fill="#1A2A22"/>')
    cab0, cab1 = hx0 + 1.4 * sh_, hx1 - 1.2 * sh_
    out.append(f'<rect x="{cab0:.1f}" y="{hw_ - 3.4 * sh_:.1f}" width="{cab1 - cab0:.1f}" height="{2.3 * sh_:.1f}" fill="#EDE4CE"/>'
               f'<rect x="{cab0 - 0.3 * sh_:.1f}" y="{hw_ - 3.65 * sh_:.1f}" width="{cab1 - cab0 + 0.6 * sh_:.1f}" height="{0.3 * sh_:.1f}" fill="#2E4A3A"/>'
               f'<rect x="{cab0:.1f}" y="{hw_ - 3.4 * sh_:.1f}" width="{0.5 * sh_:.1f}" height="{2.3 * sh_:.1f}" fill="#FFF6E0" opacity="0.6"/>')
    for i in range(5):
        wx = cab0 + (0.8 + i * 2.1) * sh_
        if wx + 1.3 * sh_ > cab1:
            break
        out.append(f'<rect x="{wx:.1f}" y="{hw_ - 3.0 * sh_:.1f}" width="{1.3 * sh_:.1f}" height="{1.2 * sh_:.1f}" fill="url(#{u}-glass)"/><rect x="{wx:.1f}" y="{hw_ - 3.0 * sh_:.1f}" width="{1.3 * sh_:.1f}" height="{1.2 * sh_:.1f}" fill="none" stroke="#2E4A3A" stroke-width="1"/>')
    rnd = random.Random(14)
    for i in range(16):
        px = cab0 + rnd.uniform(0.2, 1) * (cab1 - cab0)
        py = hw_ - 3.65 * sh_
        hh = rnd.uniform(0.35, 0.7) * sh_
        out.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{px + rnd.uniform(-1, 1):.1f}" y2="{py - hh:.1f}" stroke="#3E7A3A" stroke-width="1"/><ellipse cx="{px:.1f}" cy="{py - hh:.1f}" rx="1.6" ry="2.2" fill="{rnd.choice(["#E83A3A", "#F6C23A", "#F28AB0", "#E83A3A", "#FFFFFF"])}"/>')
    out.append(f'<rect x="{cab0 + 0.3 * sh_:.1f}" y="{hw_ - 3.65 * sh_ - 2:.1f}" width="{cab1 - cab0 - 0.6 * sh_:.1f}" height="3" fill="#8A5A3A"/>')
    cx_, cy_ = hx1 - 0.7 * sh_, hw_ - 1.1 * sh_
    out.append(f'<path d="M {cx_ - 5:.1f} {cy_:.1f} Q {cx_ - 6:.1f} {cy_ - 6:.1f} {cx_ - 2:.1f} {cy_ - 7:.1f} L {cx_ - 1:.1f} {cy_ - 10:.1f} L {cx_ + 1:.1f} {cy_ - 8:.1f} L {cx_ + 3:.1f} {cy_ - 10:.1f} L {cx_ + 3:.1f} {cy_ - 6:.1f} Q {cx_ + 4:.1f} {cy_ - 2:.1f} {cx_ + 3:.1f} {cy_:.1f} Z" fill="#E8862E"/>'
               f'<path d="M {cx_ - 5:.1f} {cy_:.1f} Q {cx_ - 10:.1f} {cy_ + 1:.1f} {cx_ - 10:.1f} {cy_ - 4:.1f}" fill="none" stroke="#E8862E" stroke-width="1.6" stroke-linecap="round"/>')
    out.append(f'<path d="M {hx0 - 4:.1f} {hw_ + 1:.1f} L {hx1 + 4:.1f} {hw_ + 1:.1f}" stroke="#E4EEF0" stroke-width="1.2" opacity="0.6"/>')

    # ---- the humpback bridge striding across the canal on the right, bikes along its railing
    X1, X2 = 9.0, 15.0
    def deck(Z):
        t = min(1, max(0, (Z - ZN) / (ZQ - ZN)))
        return 0.15 + 1.25 * math.sin(math.pi * t)
    zs = [ZN - 2 + i * 0.5 for i in range(int((ZQ + 1 - ZN + 2) / 0.5) + 1)]
    A0, A1, AY = 24.5, 37.5, 0.75

    def arch_y(Z):
        t = (Z - (A0 + A1) / 2) / ((A1 - A0) / 2)
        return WL + (AY - WL) * math.sqrt(max(0, 1 - t * t))
    def face(X, refl=False):
        f_ = (lambda Y: -2 * (-WL) - Y + 2 * WL + 2 * (-WL)) if False else None
        mY = (lambda Y: 2 * WL - Y) if refl else (lambda Y: Y)
        top = [C(X, mY(deck(Z) - 0.25), Z) for Z in zs]
        bot = [C(X, mY(WL), Z) for Z in zs[::-1]]
        hole = [C(X, mY(arch_y(A0 + (A1 - A0) * i / 30)), A0 + (A1 - A0) * i / 30) for i in range(31)]
        ring = [C(X, mY(arch_y(A0 + (A1 - A0) * i / 30) + 0.45 * math.sin(math.pi * i / 30) + 0.12), A0 + (A1 - A0) * i / 30) for i in range(31)]
        return top, bot, hole, ring
    # reflection first (in the water), then the bridge
    top, bot, hole, ring = face(X1, refl=True)
    out.append(f'<g clip-path="url(#{u}-wc)" opacity="0.5">{Q(top + bot, "#6A3A30")}{Q(hole, "#16201E")}<polyline points="{P(ring)}" fill="none" stroke="#C8C0B4" stroke-width="2"/></g>')
    top, bot, hole, ring = face(X1)
    out.append(f'<clipPath id="{u}-bf"><polygon points="{P(top + bot)}"/></clipPath>')
    out.append(Q(top + bot, f"url(#{u}-brick)"))
    out.append(f'<g clip-path="url(#{u}-bf)"><g stroke="#4A2018" stroke-width="0.7" opacity="0.45">' + "".join(
        f'<polyline points="{P([C(X1, WL + j * 0.28, Z) for Z in zs])}" fill="none"/>' for j in range(1, 14)) + "</g>"
        + f'<polygon points="{P(top + bot)}" fill="#FFE6B8" opacity="0.12"/></g>')
    # through the arch: the dark vault and daylight on the water beyond
    out.append(Q(hole, "#1A2422"))
    far_hole = [C(X2, arch_y(A0 + (A1 - A0) * i / 30), A0 + (A1 - A0) * i / 30) for i in range(31)]
    out.append(Q(far_hole, "#6E8E8A"))
    out.append(Q([C(X2, WL, A0), C(X2, WL + 0.4, A0), C(X2, WL + 0.4, A1), C(X2, WL, A1)], "#A8C4C8", ' opacity="0.6"'))
    out.append(f'<polyline points="{P(ring)}" fill="none" stroke="#EDE6DA" stroke-width="3.2"/>')
    out.append(f'<g stroke="#9A9088" stroke-width="0.9">' + "".join(
        f'<line x1="{C(X1, arch_y(Z) + 0.02, Z)[0]:.1f}" y1="{C(X1, arch_y(Z) + 0.02, Z)[1]:.1f}" x2="{C(X1, arch_y(Z) + 0.5, Z)[0]:.1f}" y2="{C(X1, arch_y(Z) + 0.5, Z)[1]:.1f}"/>'
        for Z in [A0 + (A1 - A0) * i / 14 for i in range(1, 14)]) + "</g>")
    # deck surface, far railing, coping
    dk = [C(X1, deck(Z), Z) for Z in zs] + [C(X2, deck(Z), Z) for Z in zs[::-1]]
    out.append(Q(dk, "#9A8E88"))
    out.append(f'<polyline points="{P([C(X2, deck(Z) + 1.0, Z) for Z in zs])}" fill="none" stroke="#2A2A30" stroke-width="1.4"/>')
    out.append(f'<g stroke="#2A2A30" stroke-width="0.8">' + "".join(
        f'<line x1="{C(X2, deck(Z), Z)[0]:.1f}" y1="{C(X2, deck(Z), Z)[1]:.1f}" x2="{C(X2, deck(Z) + 1.0, Z)[0]:.1f}" y2="{C(X2, deck(Z) + 1.0, Z)[1]:.1f}"/>' for Z in zs[::2]) + "</g>")
    # a cyclist crossing, with a child on the back
    Zc = 33.0
    cyc = bike_parts("#3A5A6A", crate="#8A5A34")
    scc = C.f / Zc
    def mp_c(u_, v_):
        return C(12.6, deck(Zc + u_ * 0.6) + v_, Zc + u_ * 0.6)
    out.append(render_parts(cyc, mp_c, scc * 0.55))
    rx_, ry_ = C(12.6, deck(Zc + 0.2) + 1.1, Zc + 0.2)
    out.append(f'<g transform="translate({rx_:.1f} {ry_:.1f}) scale({scc / 100 * 1.0:.3f})"><path d="M -12 0 Q -14 -40 0 -46 Q 14 -40 12 0 Z" fill="#D8463A"/><circle cx="0" cy="-58" r="10" fill="#E8C8A8"/><path d="M -10 -62 Q 0 -74 10 -62 Z" fill="#E8C060"/>'
               f'<path d="M 4 -36 L 34 -40" stroke="#D8463A" stroke-width="7" stroke-linecap="round"/><path d="M -6 0 L 8 40" stroke="#2A3A5A" stroke-width="9" stroke-linecap="round"/></g>')
    # near railing on the parapet with flower boxes, bikes locked along it
    rail_top = [C(X1, deck(Z) + 0.95, Z) for Z in zs]
    out.append(Q([C(X1, deck(Z) - 0.25, Z) for Z in zs] + [C(X1, deck(Z) + 0.15, Z) for Z in zs[::-1]], "#EDE6DA"))
    out.append(f'<polyline points="{P(rail_top)}" fill="none" stroke="#1E1E24" stroke-width="2.2"/>')
    out.append(f'<g stroke="#1E1E24" stroke-width="1.1">' + "".join(
        f'<line x1="{C(X1, deck(Z) + 0.15, Z)[0]:.1f}" y1="{C(X1, deck(Z) + 0.15, Z)[1]:.1f}" x2="{C(X1, deck(Z) + 0.95, Z)[0]:.1f}" y2="{C(X1, deck(Z) + 0.95, Z)[1]:.1f}"/>' for Z in zs[::2]) + "</g>")
    for Zb in (21.0, 26.5, 31.0, 36.0, 40.5):
        a = C(X1, deck(Zb) + 0.95, Zb)
        b = C(X1, deck(Zb + 2.4) + 0.95, Zb + 2.4)
        sb = C.f / Zb
        out.append(Q([a, b, (b[0], b[1] + 0.35 * sb * Zb / (Zb + 2.4)), (a[0], a[1] + 0.35 * sb)], "#5A3A2A"))
        rnd = random.Random(int(Zb * 10))
        for i in range(7):
            t = (i + 0.5) / 7
            fx, fy = lerp(a[0], b[0], t), lerp(a[1], b[1], t)
            out.append(f'<circle cx="{fx:.1f}" cy="{fy - rnd.uniform(0.5, 2.5):.1f}" r="{max(1.1, sb * 0.09):.1f}" fill="{rnd.choice(["#E8343A", "#F65A5A", "#FFFFFF", "#E8343A"])}"/>'
                       f'<circle cx="{fx + 1:.1f}" cy="{fy + 1:.1f}" r="{max(0.9, sb * 0.07):.1f}" fill="#3E7A34"/>')
    # lamp posts on the bridge
    for Zl in (19.0, 44.0):
        a = C(X1, deck(Zl), Zl)
        b = C(X1, deck(Zl) + 3.6, Zl)
        sl = C.f / Zl
        out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#1E1E24" stroke-width="{max(1.4, 0.12 * sl):.1f}"/>'
                   f'<path d="M {b[0] - 0.22 * sl:.1f} {b[1]:.1f} L {b[0] + 0.22 * sl:.1f} {b[1]:.1f} L {b[0] + 0.3 * sl:.1f} {b[1] - 0.5 * sl:.1f} L {b[0] - 0.3 * sl:.1f} {b[1] - 0.5 * sl:.1f} Z" fill="#F4ECD0" stroke="#1E1E24" stroke-width="1.2"/>'
                   f'<path d="M {b[0] - 0.36 * sl:.1f} {b[1] - 0.5 * sl:.1f} L {b[0]:.1f} {b[1] - 0.75 * sl:.1f} L {b[0] + 0.36 * sl:.1f} {b[1] - 0.5 * sl:.1f} Z" fill="#1E1E24"/>')
    rnd = random.Random(6)
    for Zb in (17.5, 18.4, 22.5, 23.4, 24.3, 28.6, 29.4, 34.0, 38.6, 39.4):
        sb = C.f / Zb
        fr = rnd.choice(["#24242A", "#24242A", "#24242A", "#8EC0B0", "#B8342E", "#E8E0CC", "#3A4E7A"])
        def mp(u_, v_, Zb=Zb):
            return C(X1 - 0.35, deck(Zb + u_ * 0.55) + v_, Zb + u_ * 0.55)
        out.append(render_parts(bike_parts(fr), mp, sb * 0.55))

    # ---- the near quay: brick paving, a stone kerb, a bike with a crate of tulips, the bollards
    yk = C(0, 0, ZN)[1]
    out.append(Q([(-10, yk), (610, yk), (610, 444), (-10, 444)], f"url(#{u}-pave)"))
    out.append(f'<rect x="-10" y="{yk:.1f}" width="620" height="6" fill="#C8C0B6"/><rect x="-10" y="{yk + 6:.1f}" width="620" height="2" fill="#4A3A36" opacity="0.5"/>')
    pv = []
    rnd = random.Random(3)
    Z = ZN - 0.3
    j = 0
    while Z > 8.6:
        y1 = C(0, 0, Z)[1]
        Z2 = Z - 0.22
        y2 = C(0, 0, Z2)[1]
        for Xb in [-40 + i * 0.44 + (0.22 if j % 2 else 0) for i in range(180)]:
            a, b = C(Xb, 0, Z), C(Xb + 0.4, 0, Z2)
            if b[0] < -10 or a[0] > 610:
                continue
            pv.append(f'<rect x="{a[0]:.1f}" y="{y1:.1f}" width="{b[0] - a[0]:.1f}" height="{y2 - y1 - 0.6:.1f}" fill="{rnd.choice(["#A06A58", "#8E5A4A", "#B47C66", "#7E5446", "#9A6656"])}" opacity="0.75"/>')
        Z = Z2
        j += 1
    out.append("".join(pv))
    out.append(f'<rect x="-10" y="{yk:.1f}" width="620" height="84" fill="#FFF2CC" opacity="0.1"/>')
    # bollards
    for Xb in (-5.6, 3.2):
        a = C(Xb, 0, 11.6)
        sb = C.f / 11.6
        out.append(f'<ellipse cx="{a[0] + 0.5 * sb:.1f}" cy="{a[1]:.1f}" rx="{0.45 * sb:.1f}" ry="{0.08 * sb:.1f}" fill="#2A1E1A" opacity="0.35"/>'
                   f'<path d="M {a[0] - 0.11 * sb:.1f} {a[1]:.1f} L {a[0] - 0.09 * sb:.1f} {a[1] - 0.8 * sb:.1f} Q {a[0]:.1f} {a[1] - 0.94 * sb:.1f} {a[0] + 0.09 * sb:.1f} {a[1] - 0.8 * sb:.1f} L {a[0] + 0.11 * sb:.1f} {a[1]:.1f} Z" fill="#6E2A22"/>'
                   f'<path d="M {a[0] - 0.08 * sb:.1f} {a[1]:.1f} L {a[0] - 0.06 * sb:.1f} {a[1] - 0.82 * sb:.1f}" stroke="#C8705A" stroke-width="1.4"/>')
    # the hero bike leaning on its stand, crate of tulips on the front carrier, its shadow on the bricks
    bz = 10.4
    sbk = C.f / bz
    bx0, by0 = C(-4.6, 0, bz)
    out.append(f'<path d="M {bx0 - 4:.1f} {by0:.1f} L {bx0 + 1.5 * sbk:.1f} {by0 + 0.02 * sbk:.1f} L {bx0 + 1.9 * sbk:.1f} {by0 + 0.12 * sbk:.1f} L {bx0 + 0.2 * sbk:.1f} {by0 + 0.12 * sbk:.1f} Z" fill="#2A1E1A" opacity="0.3"/>')
    out.append(bike2d(bx0, by0, sbk, frame="#7EC4AE", crate="#B8844E", tulips=["#E8303A", "#F6C030", "#F07AA8", "#E8303A", "#FFFFFF"], seed=4))
    # a bucket of tulips on the kerb, a pigeon
    tx, ty = C(-0.6, 0, 10.0)
    st = C.f / 10.0 * 1.35
    out.append(f'<ellipse cx="{tx + 0.3 * st:.1f}" cy="{ty:.1f}" rx="{0.4 * st:.1f}" ry="{0.06 * st:.1f}" fill="#2A1E1A" opacity="0.3"/>'
               f'<path d="M {tx - 0.24 * st:.1f} {ty - 0.42 * st:.1f} L {tx + 0.24 * st:.1f} {ty - 0.42 * st:.1f} L {tx + 0.19 * st:.1f} {ty:.1f} L {tx - 0.19 * st:.1f} {ty:.1f} Z" fill="#7E8A92"/>'
               f'<path d="M {tx - 0.24 * st:.1f} {ty - 0.42 * st:.1f} L {tx - 0.19 * st:.1f} {ty:.1f} L {tx - 0.1 * st:.1f} {ty:.1f} L {tx - 0.14 * st:.1f} {ty - 0.42 * st:.1f} Z" fill="#C8D0D6"/>')
    rnd = random.Random(9)
    for i in range(14):
        a_ = rnd.uniform(-0.6, 0.6)
        L_ = rnd.uniform(0.35, 0.55) * st
        ex, ey = tx + math.sin(a_) * L_, ty - 0.42 * st - math.cos(a_) * L_
        out.append(f'<line x1="{tx + a_ * 0.2 * st:.1f}" y1="{ty - 0.4 * st:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="#3E7A34" stroke-width="1.4"/>')
        c = rnd.choice(["#E8303A", "#F6C030", "#F07AA8", "#E8303A", "#FF8A3A"])
        r_ = 0.055 * st
        out.append(f'<path d="M {ex - r_:.1f} {ey:.1f} L {ex - r_ * 0.9:.1f} {ey - r_ * 1.6:.1f} L {ex - r_ * 0.3:.1f} {ey - r_ * 1.1:.1f} L {ex:.1f} {ey - r_ * 1.9:.1f} L {ex + r_ * 0.3:.1f} {ey - r_ * 1.1:.1f} L {ex + r_ * 0.9:.1f} {ey - r_ * 1.6:.1f} L {ex + r_:.1f} {ey:.1f} Q {ex:.1f} {ey + r_ * 0.6:.1f} {ex - r_:.1f} {ey:.1f} Z" fill="{c}"/>'
                   f'<path d="M {ex - r_ * 0.6:.1f} {ey - r_ * 0.3:.1f} L {ex - r_ * 0.5:.1f} {ey - r_ * 1.2:.1f}" stroke="#FFFFFF" stroke-width="0.8" opacity="0.5"/>')
    px_, py_ = C(3.6, 0, 10.6)
    out.append(f'<g transform="translate({px_:.1f} {py_:.1f})"><ellipse cx="0" cy="-7" rx="9" ry="6" fill="#8A8EA0"/><path d="M -2 -10 Q 6 -14 10 -8 L 4 -6 Z" fill="#6A6E82"/>'
               f'<circle cx="-8" cy="-12" r="3.6" fill="#7A7E92"/><path d="M -9 -10 Q -6 -8 -4 -9" stroke="#6AA88A" stroke-width="1.6" fill="none"/><path d="M -11.5 -12 L -14 -11.5" stroke="#3A3A40" stroke-width="1.2"/>'
               f'<path d="M 8 -8 L 14 -6 L 8 -5 Z" fill="#4A4E60"/><path d="M -1 -1 L -1 2 M 2 -1 L 2 2" stroke="#C8686A" stroke-width="1.2"/></g>')
    out.append(gulls([(250, 104, 10), (272, 116, 7)], "#2A3A5A", 1.8))
    return "\n".join(out)


# ================================================================ BARCELONA — over the mosaic bench to the city and the sea, late afternoon
def trencadis(box, seed, palette, cell=(5, 12), y_grow=(300, 444), grout="#E2DCCF"):
    """Broken-tile mosaic: a jittered grid of irregular shards with grout gaps; tiles grow toward the viewer.
    palette(x, y, rnd) -> colour. Use inside a clipPath."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{grout}"/>']
    y = y0
    while y < y1:
        t = min(1, max(0, (y - y_grow[0]) / (y_grow[1] - y_grow[0])))
        c = lerp(cell[0], cell[1], t)
        x = x0 - rnd.uniform(0, c)
        while x < x1:
            w = c * rnd.uniform(0.7, 1.4)
            h = c * rnd.uniform(0.7, 1.15)
            g = c * 0.11
            pts = [(x + g + rnd.uniform(-0.15, 0.15) * c, y + g + rnd.uniform(-0.1, 0.1) * c),
                   (x + w - g + rnd.uniform(-0.15, 0.15) * c, y + g + rnd.uniform(-0.1, 0.1) * c),
                   (x + w - g + rnd.uniform(-0.15, 0.15) * c, y + h - g + rnd.uniform(-0.1, 0.1) * c),
                   (x + g + rnd.uniform(-0.15, 0.15) * c, y + h - g + rnd.uniform(-0.1, 0.1) * c)]
            if rnd.random() < 0.35:  # some shards break into triangles
                k = rnd.randint(0, 3)
                pts = pts[:k] + pts[k + 1:]
            col = palette(x + w / 2, y + h / 2, rnd)
            out.append(f'<polygon points="{P(pts)}" fill="{col}"/>')
            if rnd.random() < 0.4:  # glaze glint
                out.append(f'<line x1="{pts[0][0] + 0.8:.1f}" y1="{pts[0][1] + 0.8:.1f}" x2="{pts[1][0] - 0.8:.1f}" y2="{pts[1][1] + 0.8:.1f}" stroke="#FFFFFF" stroke-width="{max(0.6, c * 0.1):.1f}" opacity="0.5"/>')
            x += w
        y += c * 0.95
    return "".join(out)


def gaudi_spires(cx, base, k, u, stone="#C8A47E", shade="#8E7468", lit="#F2D2A2", haze="#E8D2B4", haze_op=0.35):
    """A generic cluster of slender, perforated, tapering spires with bulbous finials (kept non-specific),
    two construction cranes beside them. k = px per unit; lit from the right."""
    out = []
    out.append(f'<path d="M {cx - 40 * k:.1f} {base:.1f} L {cx - 40 * k:.1f} {base - 30 * k:.1f} L {cx - 10 * k:.1f} {base - 46 * k:.1f} L {cx + 30 * k:.1f} {base - 34 * k:.1f} L {cx + 44 * k:.1f} {base - 26 * k:.1f} L {cx + 44 * k:.1f} {base:.1f} Z" fill="{shade}"/>')
    towers = [(-30, 92, 6.5), (-21, 104, 6.8), (-12, 100, 6.6), (-3, 90, 6.2), (8, 150, 9.5), (19, 116, 7.2), (28, 122, 7.4), (37, 108, 6.8)]
    for dx, h, w in towers:
        x = cx + dx * k
        top = base - h * k
        hw = w * k / 2
        body = f'M {x - hw:.1f} {base:.1f} L {x - hw * 0.62:.1f} {top + h * k * 0.18:.1f} Q {x:.1f} {top - 2 * k:.1f} {x + hw * 0.62:.1f} {top + h * k * 0.18:.1f} L {x + hw:.1f} {base:.1f} Z'
        out.append(f'<path d="{body}" fill="{stone}"/>')
        out.append(f'<path d="M {x + hw * 0.15:.1f} {base:.1f} L {x + hw * 0.1:.1f} {top + h * k * 0.18:.1f} Q {x + hw * 0.4:.1f} {top + h * k * 0.08:.1f} {x + hw * 0.62:.1f} {top + h * k * 0.18:.1f} L {x + hw:.1f} {base:.1f} Z" fill="{lit}" opacity="0.8"/>')
        for j in range(int(h * 0.62 / 5)):
            yy = base - 10 * k - j * 5 * k
            if yy < top + h * k * 0.25:
                break
            tw = hw * (1 - (base - yy) / (h * k) * 0.38)
            out.append(f'<rect x="{x - tw * 0.45:.1f}" y="{yy - 2.6 * k:.1f}" width="{tw * 0.5:.1f}" height="{2.6 * k:.1f}" rx="{0.6 * k:.1f}" fill="{shade}" opacity="0.85"/>')
        fy = top + h * k * 0.06
        out.append(f'<ellipse cx="{x:.1f}" cy="{fy:.1f}" rx="{hw * 0.55:.1f}" ry="{hw * 0.75:.1f}" fill="{lit}"/>'
                   f'<circle cx="{x:.1f}" cy="{fy - hw * 0.9:.1f}" r="{hw * 0.32:.1f}" fill="#E8C070"/>'
                   f'<circle cx="{x - hw * 0.4:.1f}" cy="{fy:.1f}" r="{hw * 0.2:.1f}" fill="#C86A5A"/><circle cx="{x + hw * 0.4:.1f}" cy="{fy:.1f}" r="{hw * 0.2:.1f}" fill="#E8E0D0"/>')
    for x, h, jib in ((cx - 52 * k, 120, 46), (cx + 50 * k, 138, -40)):
        top = base - h * k
        out.append(f'<g stroke="#C8504A" stroke-width="{max(0.9, 1.2 * k):.1f}" fill="none"><line x1="{x:.1f}" y1="{base:.1f}" x2="{x:.1f}" y2="{top:.1f}"/>'
                   f'<line x1="{x - jib * 0.25 * k:.1f}" y1="{top:.1f}" x2="{x + jib * k:.1f}" y2="{top:.1f}"/><line x1="{x:.1f}" y1="{top - 6 * k:.1f}" x2="{x + jib * k:.1f}" y2="{top:.1f}"/>'
                   f'<line x1="{x:.1f}" y1="{top - 6 * k:.1f}" x2="{x - jib * 0.25 * k:.1f}" y2="{top:.1f}"/></g>'
                   f'<line x1="{x + jib * 0.6 * k:.1f}" y1="{top:.1f}" x2="{x + jib * 0.6 * k:.1f}" y2="{top + 14 * k:.1f}" stroke="#5A4A4A" stroke-width="0.8"/>')
    return "".join(out)


def date_palm(x, base, h, seed, lean=0.05, light=1, trunk="#8A6A4E", trunk_dk="#5A4434", trunk_lit="#D8A878",
              fr_dk="#2A4A2A", fr="#3E6A34", fr_lit="#9AB85A", n=22):
    """Canary date palm: a stout trunk patterned with diamond leaf scars, a crown of long arching fronds
    each fringed with leaflets; lit from `light` (+1 right)."""
    rnd = random.Random(seed)
    tx, ty = x + lean * h, base - h
    w0, w1 = h * 0.06, h * 0.045
    spine = [(x + lean * h * (t ** 1.6), base - h * t) for t in [i / 20 for i in range(21)]]
    L = [(px - lerp(w0, w1, i / 20), py) for i, (px, py) in enumerate(spine)]
    Rr = [(px + lerp(w0, w1, i / 20), py) for i, (px, py) in enumerate(spine)]
    out = [Q(L + Rr[::-1], trunk)]
    out.append(Q([((a[0] + b[0]) / 2 + light * (b[0] - a[0]) * 0.2, a[1]) for a, b in zip(L, Rr)] + (Rr if light > 0 else L)[::-1], trunk_lit, ' opacity="0.5"'))
    out.append(Q([((a[0] + b[0]) / 2 - light * (b[0] - a[0]) * 0.3, a[1]) for a, b in zip(L, Rr)] + (L if light > 0 else Rr)[::-1], trunk_dk, ' opacity="0.55"'))
    # diamond leaf-base scars
    for i in range(1, 40):
        t = i / 40
        cx_, cy_ = x + lean * h * (t ** 1.6), base - h * t
        ww = lerp(w0, w1, t)
        off = (i % 2) * 0.5
        for j in range(-1, 2):
            dx = (j + off) * ww * 0.7
            if abs(dx) > ww * 0.95:
                continue
            out.append(f'<path d="M {cx_ + dx - ww * 0.3:.1f} {cy_:.1f} L {cx_ + dx:.1f} {cy_ - h * 0.012:.1f} L {cx_ + dx + ww * 0.3:.1f} {cy_:.1f}" fill="none" stroke="{trunk_dk}" stroke-width="{max(0.8, h * 0.004):.1f}" opacity="0.6"/>')
    # crown knob
    out.append(f'<ellipse cx="{tx:.1f}" cy="{ty:.1f}" rx="{w1 * 1.6:.1f}" ry="{w1 * 1.1:.1f}" fill="#7A6A3A"/>')
    fronds = []
    for i in range(n):
        a = -math.pi + math.pi * (i + rnd.uniform(-0.3, 0.3)) / (n - 1)
        a = a * 1.15 + (0.08 if a > -math.pi / 2 else -0.08)
        Lf = h * rnd.uniform(0.34, 0.46)
        droop = rnd.uniform(0.5, 0.9)
        pts = []
        for j in range(13):
            t = j / 12
            px = tx + math.cos(a) * Lf * t
            py = ty + math.sin(a) * Lf * t * 0.75 + Lf * droop * t * t * 0.8
            pts.append((px, py))
        fronds.append((math.sin(a), pts))
    fronds.sort(key=lambda f: f[0])  # back (upward) fronds first
    for up, pts in fronds:
        col = fr_dk if up < -0.6 else fr
        g = []
        for j in range(1, 12):
            (x1, y1), (x2, y2) = pts[j], pts[j + 1]
            dx, dy = x2 - x1, y2 - y1
            nl = math.hypot(dx, dy) or 1
            nx, ny = -dy / nl, dx / nl
            ll = h * 0.07 * math.sin(math.pi * (j / 12) ** 0.8)
            for sgn in (1, -1):
                g.append(f'M {x1:.1f} {y1:.1f} q {nx * ll * sgn * 0.5 + dx * 0.4:.1f} {ny * ll * sgn * 0.5 + dy * 0.4 + ll * 0.3:.1f} {nx * ll * sgn + dx * 0.9:.1f} {ny * ll * sgn + dy * 0.9 + ll * 0.6:.1f}')
        out.append(f'<path d="{" ".join(g)}" fill="none" stroke="{col}" stroke-width="{max(1.2, h * 0.008):.1f}" stroke-linecap="round"/>')
        out.append(f'<polyline points="{P(pts)}" fill="none" stroke="{mix(col, "#C8B060", 0.4)}" stroke-width="{max(1.2, h * 0.007):.1f}"/>')
        if (pts[-1][0] - pts[0][0]) * light > 0 or up < -0.5:
            hl = []
            for j in range(2, 11, 2):
                (x1, y1), (x2, y2) = pts[j], pts[j + 1]
                hl.append(f'M {x1:.1f} {y1 - 1:.1f} L {x2:.1f} {y2 - 1:.1f}')
            out.append(f'<path d="{" ".join(hl)}" stroke="{fr_lit}" stroke-width="{max(1, h * 0.006):.1f}" fill="none" opacity="0.8"/>')
    # date clusters under the crown
    out.append(blobs(16, seed + 3, (tx - w1 * 1.4, ty + 2, tx + w1 * 1.4, ty + h * 0.05), ["#E8A030", "#D8862A", "#F2C050"], r=(1.4, 2.6), opacity=(0.9, 1), squash=1))
    return "".join(out)


def barcelona():
    u = "bc"
    hz = 206
    out = [defs(
        lg(f"{u}-sky", [(0, "#2C78C2"), (0.45, "#74AEDC"), (0.8, "#C8DCE4"), (1, "#F6E2BC")], 0, 40, 0, hz, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#9CBCD0"), (0.4, "#5E94BC"), (1, "#3E78A8")], 0, hz, 0, 252, units="userSpaceOnUse"),
        lg(f"{u}-haze", [(0, "#F6E2BC", 0.7), (1, "#F6E2BC", 0)], 0, hz + 14, 0, 280, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(560, 120, 300, "#FFF2D0", f"{u}-sun", 0.8))
    out.append(streak_cloud(140, 110, 90, "#FFFFFF", 0.55, 4))
    out.append(streak_cloud(220, 132, 60, "#FFFFFF", 0.45, 3))
    out.append(cumulus(f"{u}-c1", 420, 168, 120, 30, 7, "#FFF8EC", "#F4ECE2", "#C8C8D4", hi="#FFFFFF", hi_op=0.7, light=1))
    # the sea, a sail and a ferry far out, glitter under the sun
    out.append(f'<rect x="0" y="{hz}" width="600" height="60" fill="url(#{u}-sea)"/>')
    out.append(water_lines(90, 12, (300, hz + 1, 610, 248), ["#FFF6DC", "#FFFFFF"], w=(3, 14), h=(0.6, 1.2), opacity=(0.5, 0.95)))
    out.append(water_lines(60, 13, (-10, hz + 1, 300, 248), ["#B8D0E0", "#4A80AE"], w=(4, 18), h=(0.6, 1.2), opacity=(0.3, 0.6)))
    out.append(f'<path d="M 160 {hz + 6} L 172 {hz + 6} L 170 {hz + 8} L 162 {hz + 8} Z" fill="#F6F2EA"/><path d="M 166 {hz + 5} L 166 {hz - 8} L 172 {hz + 5} Z" fill="#FFFFFF"/>')
    out.append(f'<rect x="250" y="{hz + 3}" width="24" height="4" fill="#F6F2EA"/><rect x="254" y="{hz}" width="12" height="3" fill="#E8E2D8"/><rect x="262" y="{hz - 3}" width="3" height="3" fill="#C8463A"/>')
    # the hill by the harbour on the right with its fortress
    hill = rough([(380, 250), (430, 226), (480, 206), (520, 198), (560, 202), (610, 214)], 41, amp=4, depth=3)
    out.append(Q(hill + [(610, 260), (380, 260)], "#A8A49A"))
    out.append(dots(60, 42, (420, 204, 610, 240), "#8A8E7E", r=(1.5, 3), opacity=(0.4, 0.7)))
    out.append('<g fill="#B8AE9E"><rect x="510" y="191" width="34" height="9"/><rect x="514" y="186" width="6" height="6"/><rect x="532" y="186" width="6" height="6"/></g>')
    # the city: rows of blocks from the shore up the slope toward us, hazier with distance
    rnd = random.Random(19)
    rows = [(226 + i * 8 + i * i * 0.6, 0.4 + i * 0.09) for i in range(12)]
    walls = ["#F2E4CC", "#EAC9A0", "#F6EADA", "#E2A880", "#F0D6B4", "#D88E6A", "#ECE2D4", "#E8BC8A"]
    for ri, (yb, k) in enumerate(rows):
        x = rnd.uniform(-30, -5)
        hzop = max(0, 0.62 - ri * 0.06)
        row = [f'<rect x="-10" y="{yb - 6 * k:.1f}" width="620" height="{30 * k + 6:.1f}" fill="#8A6A62"/>']
        while x < 620:
            w = rnd.uniform(16, 34) * k
            h = rnd.uniform(9, 20) * k
            side = rnd.uniform(3, 6) * k
            wall = rnd.choice(walls)
            y = yb + rnd.uniform(-2, 2) * k
            row.append(f'<rect x="{x:.1f}" y="{y - h:.1f}" width="{w:.1f}" height="{h + 30 * k:.1f}" fill="{wall}"/>')
            row.append(f'<rect x="{x + w:.1f}" y="{y - h + side * 0.3:.1f}" width="{side:.1f}" height="{h + 30 * k:.1f}" fill="{mix(wall, "#FFE8C0", 0.45)}"/>')
            row.append(f'<rect x="{x:.1f}" y="{y - h:.1f}" width="{w:.1f}" height="{h + 30 * k:.1f}" fill="#6A4A5A" opacity="0.12"/>')
            row.append(f'<rect x="{x:.1f}" y="{y - h:.1f}" width="{w + side:.1f}" height="{1.6 * k:.1f}" fill="{mix(wall, "#FFFFFF", 0.4)}"/>')
            for j in range(int(h / (4.2 * k))):
                out_y = y - h + 3 * k + j * 4.2 * k
                row.append(f'<rect x="{x + 1.5 * k:.1f}" y="{out_y:.1f}" width="{w - 3 * k:.1f}" height="{1.3 * k:.1f}" fill="{mix(wall, "#5A4A5A", 0.45)}" opacity="0.55"/>')
            if rnd.random() < 0.5:
                row.append(f'<rect x="{x + w * rnd.uniform(0.1, 0.6):.1f}" y="{y - h - 3 * k:.1f}" width="{5 * k:.1f}" height="{3 * k:.1f}" fill="{wall}"/>')
            if rnd.random() < 0.3:
                row.append(f'<path d="M {x:.1f} {y - h:.1f} L {x + w * 0.12:.1f} {y - h - 2.6 * k:.1f} L {x + w * 0.88:.1f} {y - h - 2.6 * k:.1f} L {x + w + side:.1f} {y - h + side * 0.3:.1f} Z" fill="#C8644A"/>')
            x += w + side + rnd.uniform(-2, 4) * k
            if rnd.random() < 0.3:  # a tree-lined street between blocks
                row.append(blobs(int(6 + 8 * k), int(x * 3 + ri), (x - 6 * k, y - 4 * k, x + 4 * k, y), ["#5E7A44", "#6E8A4E", "#4A6238"], r=(2 * k, 3.6 * k), opacity=(0.9, 1), squash=0.8))
                x += 6 * k
        out.append("".join(row))
        if hzop > 0:
            out.append(f'<rect x="-10" y="{yb - 22 * k:.1f}" width="620" height="{52 * k:.1f}" fill="#F2DEC0" opacity="{hzop:.2f}"/>')
        if ri == 3:
            out.append(gaudi_spires(246, 270, 1.12, u, stone="#C8986C", shade="#8A6252", lit="#F6D6A6"))
    out.append(f'<rect x="0" y="{hz + 14}" width="600" height="60" fill="url(#{u}-haze)" opacity="0.6"/>')
    # the park's slope below the terrace: stone pines, shrubs
    out.append(Q(rough([(-10, 318), (120, 326), (260, 318), (400, 330), (610, 316)], 51, amp=6, depth=3) + [(610, 400), (-10, 400)], "#6E7A48"))
    out.append(blobs(70, 52, (-10, 318, 610, 360), ["#4E5E36", "#7A8A50", "#5E6E3E", "#8A9A5A"], r=(5, 12), opacity=(0.8, 1), squash=0.7))
    for x, y, rx, ry, sd in ((150, 322, 46, 22, 61), (330, 326, 40, 18, 62), (480, 318, 56, 26, 63), (250, 330, 30, 14, 64)):
        out.append(leaf_canopy(f"{u}-o{sd}", x, y, rx, ry, sd, "#2E3E26", "#4E5E36", "#8A9A52", gold="#E8D08A", light=(1, -1), n=130, r=(0.11, 0.2)))
    out.append(cypress_tree(398, 340, 64, 5, dark="#1E2E22", mid="#2E4430", lit="#7A8A4A", light=1))
    out.append(cypress_tree(412, 342, 50, 6, dark="#1E2E22", mid="#2E4430", lit="#7A8A4A", light=1))

    # ---- the serpentine mosaic bench, seen from the terrace: backrest, seat and front, undulating in plan
    def d(x):
        return math.sin(x * 0.0165 + 0.6) * 0.85 + math.sin(x * 0.041 + 2) * 0.15
    xs = [x for x in range(-20, 625, 5)]
    yt = [(x, 350 + 16 * d(x)) for x in xs]
    ys = [(x, 384 + 22 * d(x)) for x in xs]
    yf = [(x, 398 + 26 * d(x)) for x in xs]
    back = yt + ys[::-1]
    seat = ys + yf[::-1]
    front = yf + [(625, 470), (-20, 470)]
    pal_sections = [
        ("#F6F2EA", ["#2E5EA8", "#5E9AD8", "#F6F2EA", "#F6F2EA", "#E8C040"]),
        ("#F6F2EA", ["#E8A040", "#F6D060", "#3E8A5A", "#F6F2EA", "#C8503A"]),
        ("#F6F2EA", ["#2E5EA8", "#F6F2EA", "#7AB8D8", "#3E8A5A", "#F6F2EA"]),
        ("#F6F2EA", ["#C8503A", "#E8C040", "#F6F2EA", "#2E5EA8", "#F6F2EA"]),
    ]

    def pal(x, y, rnd):
        i = int((x + 20) // 160) % 4
        base_, acc = pal_sections[i]
        cxr = (int((x + 20) // 80) + 0.5) * 80 - 20
        if 352 < y < 392 and abs(x - cxr) < 14 and abs(y - (366 + 16 * d(cxr))) < 11:
            return acc[0] if (abs(x - cxr) + abs(y - (366 + 16 * d(cxr)))) > 8 else "#E8C040"
        return rnd.choice(acc) if rnd.random() < 0.55 else base_
    out.append(f'<clipPath id="{u}-bk"><polygon points="{P(back)}"/></clipPath><clipPath id="{u}-st"><polygon points="{P(seat)}"/></clipPath><clipPath id="{u}-fr"><polygon points="{P(front)}"/></clipPath>')
    out.append(Q(back, "#E2DCCF"))
    out.append(f'<g clip-path="url(#{u}-bk)">' + trencadis((-20, 330, 625, 410), 71, pal, cell=(6, 8), y_grow=(330, 410))
               + f'<polygon points="{P(back)}" fill="#3A2A4A" opacity="0.08"/></g>')
    out.append(Q(seat, "#E2DCCF"))
    out.append(f'<g clip-path="url(#{u}-st)">' + trencadis((-20, 360, 625, 430), 72, lambda x, y, r: r.choice(["#F6F2EA", "#F6F2EA", "#E8C040", "#5E9AD8", "#F6F2EA", "#3E8A5A"]), cell=(7, 9), y_grow=(360, 430))
               + f'<polygon points="{P(seat)}" fill="#FFF6E0" opacity="0.42"/></g>')
    out.append(Q(front, "#E2DCCF"))
    out.append(f'<g clip-path="url(#{u}-fr)">' + trencadis((-20, 376, 625, 470), 73, pal, cell=(8, 11), y_grow=(376, 444))
               + f'<polygon points="{P(front)}" fill="#2A2040" opacity="0.3"/>'
               + f'<polygon points="{P(yf + [(x, y + 16) for x, y in yf[::-1]])}" fill="#2A2040" opacity="0.18"/></g>')
    out.append(f'<polyline points="{P(yt)}" fill="none" stroke="#F6F2EA" stroke-width="5" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{P([(x, y + 1.5) for x, y in yt])}" fill="none" stroke="#FFFFFF" stroke-width="1.6"/>')
    out.append(f'<polyline points="{P([(x, y + 3) for x, y in yf])}" fill="none" stroke="#3A2A3A" stroke-width="3" opacity="0.25"/>')
    out.append(f'<polyline points="{P(yf)}" fill="none" stroke="#FFF8E8" stroke-width="2"/>')
    # visitors on the bench (in a hollow), a green parakeet on the backrest
    for px, c, hair, skin, legs, lean_ in ((214, "#E8C040", "#2A1E1A", "#C8906A", "#2E3E6A", -4), (240, "#C8463A", "#6A4A2A", "#E8B898", "#E8E2D6", 3)):
        by_ = 391 + 24 * d(px)
        out.append(f'<path d="M {px - 14} {by_ + 8:.1f} L {px + 6} {by_ + 8:.1f} L {px - 4} {by_ + 34:.1f} L {px - 22} {by_ + 34:.1f} Z" fill="#2A2040" opacity="0.22"/>'
                   f'<g transform="translate({px} {by_:.1f}) rotate({lean_})"><path d="M -10 0 L -9 -28 Q 0 -34 9 -28 L 10 0 Z" fill="{c}"/><path d="M 4 -30 L 9 -28 L 10 0 L 6 0 Z" fill="#000" opacity="0.15"/>'
                   f'<path d="M -9 -1 L -9 6 L -5 22 L -1 22 L -3 6 L 1 6 L 3 22 L 7 22 L 5 4 L 9 -1 Z" fill="{legs}"/>'
                   f'<circle cx="0" cy="-37" r="7.5" fill="{skin}"/><path d="M -8 -37 Q -8 -47 0 -46 Q 8 -47 8 -37 Q 6 -42 0 -42 Q -6 -42 -8 -37 Z" fill="{hair}"/>'
                   f'<path d="M -9 -26 Q -14 -14 -6 -8" fill="none" stroke="{skin}" stroke-width="3" stroke-linecap="round"/></g>')
    qx, qy = 410, 350 + 16 * d(410) - 2
    out.append(f'<g transform="translate({qx} {qy:.1f})"><path d="M -8 0 Q -10 -14 0 -18 Q 8 -18 8 -8 Q 6 0 -2 2 Z" fill="#5EB84A"/><path d="M -2 2 L -14 10 L -10 3 Z" fill="#3E8A3A"/>'
               f'<circle cx="4" cy="-16" r="5.5" fill="#7ACC5A"/><path d="M 8 -17 Q 12 -15 9 -12 Z" fill="#E8C060"/><circle cx="5" cy="-17" r="1.2" fill="#1A1A1A"/>'
               f'<path d="M -6 -12 Q -2 -6 -6 -1" fill="none" stroke="#9AE07A" stroke-width="1.6"/><path d="M -1 1 L -1 4 M 2 0 L 2 3" stroke="#6A5A5A" stroke-width="1.2"/></g>')
    # framing palms: a date palm on the left, a second on the right
    out.append(date_palm(40, 470, 360, 4, lean=0.07, light=1))
    out.append(date_palm(588, 470, 290, 9, lean=-0.07, light=1))
    out.append(gulls([(330, 150, 10), (352, 162, 7)], "#3A4A6A", 1.8))
    return "\n".join(out)


# ================================================================ FLORENCE — the city at sunset from the hillside terrace across the Arno
def tuscan_roof_row(yb, k, seed, x0=-20, x1=620, sun=-1, haze=0.0, haze_col="#E8A890", lit_p=0.0, walls=None):
    """A row of Tuscan houses in raking sunset light: ochre / cream / rose walls, shallow hipped terracotta roofs
    (sun side glowing), green shutters, chimneys."""
    rnd = random.Random(seed)
    walls = walls or [("#E8C08A", "#B8866A"), ("#F0D6A8", "#C29A80"), ("#E6A878", "#B47462"), ("#F2E2C4", "#C4A894"),
                      ("#D89A6A", "#A86A5A"), ("#ECCB96", "#BC9070")]
    out = []
    x = x0 + rnd.uniform(-10, 0) * k
    while x < x1:
        w = rnd.uniform(18, 34) * k
        h = rnd.uniform(10, 18) * k
        wall, wsh = rnd.choice(walls)
        y = yb + rnd.uniform(-1.5, 1.5) * k
        out.append(f'<rect x="{x:.1f}" y="{y - h:.1f}" width="{w:.1f}" height="{h + 12 * k:.1f}" fill="{wall}"/>')
        out.append(f'<rect x="{x + w * (0.72 if sun < 0 else 0):.1f}" y="{y - h:.1f}" width="{w * 0.28:.1f}" height="{h + 12 * k:.1f}" fill="{wsh}" opacity="0.55"/>')
        # windows with green shutters, a few lit
        rows_ = max(1, int(h / (5 * k)))
        cols_ = max(1, int(w / (6 * k)))
        for r_ in range(rows_):
            for c_ in range(cols_):
                wx = x + (c_ + 0.5) * w / cols_ - 1.1 * k
                wy = y - h + 2.6 * k + r_ * 5 * k
                if rnd.random() < lit_p:
                    out.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{2.2 * k:.1f}" height="{3 * k:.1f}" fill="#FFD27A"/>')
                elif rnd.random() < 0.6:
                    out.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{2.2 * k:.1f}" height="{3 * k:.1f}" fill="{rnd.choice(["#4E6A4A", "#5A7A52", "#3E4A44"])}"/>')
                else:
                    out.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{2.2 * k:.1f}" height="{3 * k:.1f}" fill="#4A3440"/>')
        # shallow hipped roof with deep eaves
        rh = rnd.uniform(3.5, 6) * k
        ov = 1.6 * k
        r0, r1 = x + w * 0.3, x + w * 0.7
        out.append(Q([(x - ov, y - h), (r0, y - h - rh), (r1, y - h - rh), (x + w + ov, y - h)], "#B85A3E"))
        if sun < 0:
            out.append(Q([(x - ov, y - h), (r0, y - h - rh), (r0 + (r1 - r0) * 0.5, y - h - rh), (x + w * 0.45, y - h)], "#F0905A"))
        else:
            out.append(Q([(x + w * 0.55, y - h), (r1 - (r1 - r0) * 0.5, y - h - rh), (r1, y - h - rh), (x + w + ov, y - h)], "#F0905A"))
        out.append(f'<rect x="{x - ov:.1f}" y="{y - h:.1f}" width="{w + 2 * ov:.1f}" height="{1.2 * k:.1f}" fill="#5A2A2A" opacity="0.45"/>')
        out.append(f'<g stroke="#7A3428" stroke-width="{max(0.5, 0.45 * k):.2f}" opacity="0.4">' + "".join(
            f'<line x1="{lerp(x - ov, r0, t):.1f}" y1="{y - h - rh * t:.1f}" x2="{lerp(x + w + ov, r1, t):.1f}" y2="{y - h - rh * t:.1f}"/>' for t in (0.33, 0.66)) + "</g>")
        if rnd.random() < 0.45:
            cxx = x + w * rnd.uniform(0.2, 0.8)
            out.append(f'<rect x="{cxx - 1.1 * k:.1f}" y="{y - h - rh * 0.7 - 3.5 * k:.1f}" width="{2.2 * k:.1f}" height="{3.5 * k:.1f}" fill="{wall}"/><rect x="{cxx - 1.6 * k:.1f}" y="{y - h - rh * 0.7 - 4.3 * k:.1f}" width="{3.2 * k:.1f}" height="{1 * k:.1f}" fill="#8A3A2A"/>')
        x += w + rnd.uniform(-1, 2.5) * k
    if haze > 0:
        out.append(f'<rect x="-10" y="{yb - 30 * k:.1f}" width="620" height="{42 * k:.1f}" fill="{haze_col}" opacity="{haze:.2f}"/>')
    return "".join(out)


def duomo(cx, spring, R, H, u):
    """The great ribbed octagonal dome on its drum, in sunset light from the left; tribunes and lantern."""
    lit, mid, shd = "#F6A060", "#D8704A", "#8E4A50"
    marble, mshd, green = "#F6E8D6", "#C8A8A8", "#4E6A5A"
    out = [defs(lg(f"{u}-dl", [(0, "#FFC07A"), (1, lit)], 0, 0, 1, 0), lg(f"{u}-dr", [(0, mid), (1, shd)], 0, 0, 1, 0))]

    def hw(s):
        return max(0.16 * R, R * (1 - s ** 1.75) ** 0.62)
    top = spring - H
    # drum
    dh = R * 0.42
    db = spring + dh
    corners = [-1, -0.924, -0.383, 0.383, 0.924, 1]
    for a, b, col in ((-1.0, -0.924, marble), (-0.924, -0.383, marble), (-0.383, 0.383, "#EADACB"), (0.383, 0.924, mshd), (0.924, 1.0, mshd)):
        out.append(f'<rect x="{cx + a * R * 1.04:.1f}" y="{spring:.1f}" width="{(b - a) * R * 1.04:.1f}" height="{dh:.1f}" fill="{col}"/>')
        fw = (b - a) * R * 1.04
        if fw > R * 0.2:
            fx = cx + (a + b) / 2 * R * 1.04
            out.append(f'<rect x="{cx + a * R * 1.04 + fw * 0.08:.1f}" y="{spring + dh * 0.12:.1f}" width="{fw * 0.84:.1f}" height="{dh * 0.76:.1f}" fill="none" stroke="{green}" stroke-width="{max(0.8, R * 0.016):.1f}"/>')
            out.append(f'<ellipse cx="{fx:.1f}" cy="{spring + dh * 0.5:.1f}" rx="{fw * 0.11:.1f}" ry="{dh * 0.19:.1f}" fill="#6A4A58"/><ellipse cx="{fx:.1f}" cy="{spring + dh * 0.5:.1f}" rx="{fw * 0.11:.1f}" ry="{dh * 0.19:.1f}" fill="none" stroke="{marble}" stroke-width="{max(1, R * 0.025):.1f}"/>')
    for c_ in corners[1:-1]:
        out.append(f'<rect x="{cx + c_ * R * 1.04 - R * 0.02:.1f}" y="{spring:.1f}" width="{R * 0.04:.1f}" height="{dh:.1f}" fill="{green}" opacity="0.8"/>')
    out.append(f'<rect x="{cx - R * 1.08:.1f}" y="{spring - R * 0.05:.1f}" width="{R * 2.16:.1f}" height="{R * 0.07:.1f}" fill="{marble}"/>')
    out.append(f'<rect x="{cx - R * 1.06:.1f}" y="{spring + R * 0.02:.1f}" width="{R * 2.12:.1f}" height="{R * 0.03:.1f}" fill="#5A3A40" opacity="0.4"/>')
    # dome shell: facets between the eight white ribs; lit facets on the left
    n = 30
    ss = [i / n for i in range(n + 1)]
    for a, b in ((-1, -0.924), (-0.924, -0.383), (-0.383, 0.383), (0.383, 0.924), (0.924, 1)):
        L = [(cx + a * hw(s), spring - H * s) for s in ss]
        Rr = [(cx + b * hw(s), spring - H * s) for s in ss]
        mid_ = (a + b) / 2
        fill = f"url(#{u}-dl)" if mid_ < -0.1 else ("#E8885A" if abs(mid_) < 0.1 else f"url(#{u}-dr)")
        out.append(Q(L + Rr[::-1], fill))
        # tile courses curving across each facet
        for j in range(1, 16):
            s = j / 16
            y0 = spring - H * s
            xa, xb = cx + a * hw(s), cx + b * hw(s)
            sag = (xb - xa) * 0.06
            out.append(f'<path d="M {xa:.1f} {y0:.1f} Q {(xa + xb) / 2:.1f} {y0 + sag:.1f} {xb:.1f} {y0:.1f}" fill="none" stroke="#7A3A30" stroke-width="{max(0.5, R * 0.01):.2f}" opacity="0.35"/>')
        # the oval windows in the shell, low down
        if abs(mid_) < 0.8:
            s = 0.18
            wx = cx + mid_ * hw(s)
            out.append(f'<ellipse cx="{wx:.1f}" cy="{spring - H * s:.1f}" rx="{R * 0.04 * (1 - abs(mid_) * 0.6):.1f}" ry="{R * 0.05:.1f}" fill="#4A2A30" opacity="0.8"/>')
    # sun glow sweeping across the left facets
    out.append(Q([(cx - hw(s), spring - H * s) for s in ss] + [(cx - 0.55 * hw(s), spring - H * s) for s in ss[::-1]], "#FFD49A", ' opacity="0.35"'))
    for c_ in (-0.924, -0.383, 0.383, 0.924):
        rib = [(cx + c_ * hw(s), spring - H * s) for s in ss]
        out.append(f'<polyline points="{P(rib)}" fill="none" stroke="{marble if c_ < 0.5 else "#E2C8C0"}" stroke-width="{max(1.6, R * 0.06):.1f}" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{P([(cx - hw(s), spring - H * s) for s in ss])}" fill="none" stroke="#FFE2B0" stroke-width="{max(1.4, R * 0.035):.1f}"/>')
    # lantern: marble octagon with buttress volutes, conical cap, gilded ball and cross
    lw, lh = R * 0.15, R * 0.36
    out.append(f'<rect x="{cx - lw * 1.3:.1f}" y="{top - R * 0.04:.1f}" width="{lw * 2.6:.1f}" height="{R * 0.06:.1f}" fill="{marble}"/>')
    out.append(f'<rect x="{cx - lw:.1f}" y="{top - lh:.1f}" width="{lw * 2:.1f}" height="{lh:.1f}" fill="{marble}"/><rect x="{cx + lw * 0.2:.1f}" y="{top - lh:.1f}" width="{lw * 0.8:.1f}" height="{lh:.1f}" fill="{mshd}"/>')
    for dx in (-0.55, 0.0, 0.55):
        out.append(f'<rect x="{cx + dx * lw - lw * 0.14:.1f}" y="{top - lh * 0.82:.1f}" width="{lw * 0.28:.1f}" height="{lh * 0.6:.1f}" rx="{lw * 0.14:.1f}" fill="#4A3A44"/>')
    for sx in (-1, 1):
        out.append(f'<path d="M {cx + sx * lw:.1f} {top - lh * 0.75:.1f} Q {cx + sx * lw * 1.7:.1f} {top - lh * 0.4:.1f} {cx + sx * lw * 1.45:.1f} {top:.1f} L {cx + sx * lw:.1f} {top:.1f} Z" fill="{marble if sx < 0 else mshd}"/>')
    out.append(f'<path d="M {cx - lw * 1.1:.1f} {top - lh:.1f} L {cx:.1f} {top - lh - R * 0.32:.1f} L {cx + lw * 1.1:.1f} {top - lh:.1f} Z" fill="{marble}"/><path d="M {cx:.1f} {top - lh - R * 0.32:.1f} L {cx + lw * 1.1:.1f} {top - lh:.1f} L {cx + lw * 0.2:.1f} {top - lh:.1f} Z" fill="{mshd}"/>')
    by = top - lh - R * 0.36
    out.append(f'<circle cx="{cx:.1f}" cy="{by:.1f}" r="{R * 0.06:.1f}" fill="#F2C050"/><circle cx="{cx - R * 0.02:.1f}" cy="{by - R * 0.02:.1f}" r="{R * 0.025:.1f}" fill="#FFF0B0"/>'
               f'<line x1="{cx:.1f}" y1="{by - R * 0.06:.1f}" x2="{cx:.1f}" y2="{by - R * 0.18:.1f}" stroke="#E8B040" stroke-width="{max(1, R * 0.025):.1f}"/>'
               f'<line x1="{cx - R * 0.045:.1f}" y1="{by - R * 0.13:.1f}" x2="{cx + R * 0.045:.1f}" y2="{by - R * 0.13:.1f}" stroke="#E8B040" stroke-width="{max(1, R * 0.025):.1f}"/>')
    # the tribunes: little half-domes around the base of the drum
    for dx, rr in ((-1.15, 0.22), (1.12, 0.2)):
        tx = cx + dx * R
        ty = db + R * 0.36
        out.append(f'<rect x="{tx - rr * R:.1f}" y="{ty:.1f}" width="{2 * rr * R:.1f}" height="{R * 0.3:.1f}" fill="{marble if dx < 0 else mshd}"/>')
        out.append(f'<path d="M {tx - rr * R:.1f} {ty:.1f} Q {tx - rr * R:.1f} {ty - rr * R * 0.9:.1f} {tx:.1f} {ty - rr * R * 0.95:.1f} Q {tx + rr * R:.1f} {ty - rr * R * 0.9:.1f} {tx + rr * R:.1f} {ty:.1f} Z" fill="{lit if dx < 0 else mid}"/>')
        out.append(f'<path d="M {tx:.1f} {ty - rr * R * 0.95:.1f} Q {tx + rr * R:.1f} {ty - rr * R * 0.9:.1f} {tx + rr * R:.1f} {ty:.1f} L {tx + rr * R * 0.3:.1f} {ty:.1f} Z" fill="{shd}" opacity="0.45"/>')
        out.append(f'<rect x="{tx - rr * R:.1f}" y="{ty:.1f}" width="{2 * rr * R:.1f}" height="{R * 0.04:.1f}" fill="#5A3A40" opacity="0.35"/>')
    # the nave running back toward the bell tower, with its striped marble flank
    out.append(Q([(cx - R * 1.6, db + R * 0.1), (cx - R * 2.7, db + R * 0.15), (cx - R * 2.7, db + R * 0.42), (cx - R * 1.6, db + R * 0.42)], marble))
    out.append(Q([(cx - R * 1.62, db - R * 0.08), (cx - R * 2.72, db - R * 0.02), (cx - R * 2.72, db + R * 0.15), (cx - R * 1.62, db + R * 0.1)], "#D07050"))
    out.append(f'<g stroke="{green}" stroke-width="{max(0.8, R * 0.02):.1f}">' + "".join(
        f'<line x1="{cx - R * (1.65 + i * 0.16):.1f}" y1="{db + R * 0.15:.1f}" x2="{cx - R * (1.65 + i * 0.16):.1f}" y2="{db + R * 0.42:.1f}"/>' for i in range(7)) + "</g>")
    return "".join(out)


def campanile(cx, base, top, w, u):
    """Slender square bell tower clad in white, green and rose marble; Gothic openings growing toward the top."""
    marble, shd, green, rose = "#F6EADC", "#CDB2B2", "#4E6A5A", "#E0A0A0"
    H = base - top
    side = w * 0.32
    out = [f'<rect x="{cx - w / 2 - side:.1f}" y="{top:.1f}" width="{side:.1f}" height="{H:.1f}" fill="#FFE6C8"/>',
           f'<rect x="{cx - w / 2:.1f}" y="{top:.1f}" width="{w:.1f}" height="{H:.1f}" fill="{shd}"/>']
    levels = [0, 0.18, 0.32, 0.47, 0.64, 0.84, 1.0]
    for i in range(len(levels) - 1):
        y0, y1 = base - H * levels[i], base - H * levels[i + 1]
        out.append(f'<rect x="{cx - w / 2:.1f}" y="{y1:.1f}" width="{w:.1f}" height="{y0 - y1:.1f}" fill="{marble if i % 2 == 0 else "#EEDCD0"}" opacity="0.55"/>')
        out.append(f'<rect x="{cx - w / 2:.1f}" y="{y1:.1f}" width="{w:.1f}" height="{max(1, H * 0.01):.1f}" fill="{green}"/>')
        out.append(f'<rect x="{cx - w / 2 + w * 0.12:.1f}" y="{y1 + (y0 - y1) * 0.15:.1f}" width="{w * 0.76:.1f}" height="{(y0 - y1) * 0.7:.1f}" fill="none" stroke="{rose if i % 2 else green}" stroke-width="{max(0.8, w * 0.05):.1f}"/>')
        if i >= 2:
            ow = w * (0.2 + 0.1 * (i - 2))
            n_ = 1 if i < 4 else 2
            for j in range(n_):
                ox = cx - (n_ - 1) * ow * 0.62 + j * ow * 1.24
                oy0, oy1 = y1 + (y0 - y1) * 0.25, y0 - (y0 - y1) * 0.12
                out.append(f'<path d="M {ox - ow / 2:.1f} {oy1:.1f} L {ox - ow / 2:.1f} {oy0 + ow * 0.5:.1f} L {ox:.1f} {oy0 - ow * 0.2:.1f} L {ox + ow / 2:.1f} {oy0 + ow * 0.5:.1f} L {ox + ow / 2:.1f} {oy1:.1f} Z" fill="#3E2A3A"/>')
    out.append(f'<rect x="{cx - w / 2 - side:.1f}" y="{top:.1f}" width="{side * 0.35:.1f}" height="{H:.1f}" fill="#FFF2DE" opacity="0.7"/>')
    out.append(f'<rect x="{cx - w / 2 - side - w * 0.08:.1f}" y="{top - w * 0.12:.1f}" width="{w + side + w * 0.16:.1f}" height="{w * 0.16:.1f}" fill="{marble}"/>'
               f'<rect x="{cx - w / 2 - side - w * 0.08:.1f}" y="{top + w * 0.04:.1f}" width="{w + side + w * 0.16:.1f}" height="{w * 0.06:.1f}" fill="#6A4A50" opacity="0.4"/>')
    return "".join(out)


def palazzo_tower(cx, base, top, w, u):
    """The old palace: a rusticated block with square merlons and a slender tower with a machicolated gallery,
    swallow-tail merlons, a clock and an open belfry."""
    st, sd, lit = "#C89A6A", "#8E6458", "#F2C28A"
    out = []
    # palace block
    bw, bh = w * 5.2, (base - top) * 0.36
    bx = cx - bw * 0.45
    out.append(f'<rect x="{bx:.1f}" y="{base - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{st}"/>'
               f'<rect x="{bx:.1f}" y="{base - bh:.1f}" width="{bw * 0.18:.1f}" height="{bh:.1f}" fill="{lit}" opacity="0.7"/>')
    out.append(f'<rect x="{bx - 2:.1f}" y="{base - bh - w * 0.7:.1f}" width="{bw + 4:.1f}" height="{w * 0.7:.1f}" fill="{st}"/>'
               + "".join(f'<rect x="{bx + i * w * 0.5:.1f}" y="{base - bh - w * 1.05:.1f}" width="{w * 0.3:.1f}" height="{w * 0.38:.1f}" fill="{st}"/>' for i in range(int(bw / (w * 0.5)) + 1)))
    out.append(f'<g fill="#5A3A40" opacity="0.7">' + "".join(f'<rect x="{bx + bw * (0.12 + i * 0.16):.1f}" y="{base - bh * (0.75 - j * 0.32):.1f}" width="{w * 0.28:.1f}" height="{w * 0.5:.1f}" rx="{w * 0.14:.1f}"/>' for i in range(6) for j in range(2)) + "</g>")
    # tower shaft sits forward on the facade
    gy = top + (base - top) * 0.3
    out.append(f'<rect x="{cx - w / 2:.1f}" y="{gy:.1f}" width="{w:.1f}" height="{base - bh - gy:.1f}" fill="{st}"/><rect x="{cx - w / 2:.1f}" y="{gy:.1f}" width="{w * 0.3:.1f}" height="{base - bh - gy:.1f}" fill="{lit}" opacity="0.8"/>')
    # gallery with corbels and swallow-tail merlons
    gw = w * 1.35
    out.append(f'<rect x="{cx - gw / 2:.1f}" y="{gy - w * 0.9:.1f}" width="{gw:.1f}" height="{w * 0.9:.1f}" fill="{st}"/><rect x="{cx - gw / 2:.1f}" y="{gy - w * 0.9:.1f}" width="{gw * 0.3:.1f}" height="{w * 0.9:.1f}" fill="{lit}" opacity="0.8"/>')
    out.append(f'<g fill="{sd}">' + "".join(f'<rect x="{cx - gw / 2 + i * gw / 5 + gw / 20:.1f}" y="{gy - w * 0.1:.1f}" width="{gw / 10:.1f}" height="{w * 0.35:.1f}"/>' for i in range(5)) + "</g>")
    for i in range(4):
        mx = cx - gw / 2 + (i + 0.5) * gw / 4
        out.append(f'<path d="M {mx - gw * 0.09:.1f} {gy - w * 0.9:.1f} L {mx - gw * 0.09:.1f} {gy - w * 1.35:.1f} L {mx:.1f} {gy - w * 1.15:.1f} L {mx + gw * 0.09:.1f} {gy - w * 1.35:.1f} L {mx + gw * 0.09:.1f} {gy - w * 0.9:.1f} Z" fill="{st}"/>')
    # clock face
    out.append(f'<circle cx="{cx:.1f}" cy="{gy + w * 0.9:.1f}" r="{w * 0.32:.1f}" fill="#2A3A5A"/><circle cx="{cx:.1f}" cy="{gy + w * 0.9:.1f}" r="{w * 0.32:.1f}" fill="none" stroke="#F2C060" stroke-width="{max(0.8, w * 0.06):.1f}"/>')
    # open belfry on four columns, cupola, finial
    by0 = gy - w * 1.35
    bw2 = w * 0.62
    out.append(f'<rect x="{cx - bw2 / 2:.1f}" y="{by0 - w * 1.0:.1f}" width="{bw2:.1f}" height="{w * 1.0:.1f}" fill="#3E2A34"/>'
               + "".join(f'<rect x="{cx - bw2 / 2 + j * bw2 * 0.43:.1f}" y="{by0 - w * 1.0:.1f}" width="{bw2 * 0.14:.1f}" height="{w * 1.0:.1f}" fill="{st}"/>' for j in range(3))
               + f'<path d="M {cx - bw2 * 0.65:.1f} {by0 - w * 1.0:.1f} Q {cx:.1f} {by0 - w * 1.9:.1f} {cx + bw2 * 0.65:.1f} {by0 - w * 1.0:.1f} Z" fill="{st}"/>'
               + f'<line x1="{cx:.1f}" y1="{by0 - w * 1.6:.1f}" x2="{cx:.1f}" y2="{by0 - w * 2.2:.1f}" stroke="{sd}" stroke-width="1.2"/><circle cx="{cx:.1f}" cy="{by0 - w * 2.2:.1f}" r="1.6" fill="#E8B040"/>')
    return "".join(out)


def florence():
    u = "fl"
    out = [defs(
        lg(f"{u}-sky", [(0, "#2E2E66"), (0.28, "#5A4886"), (0.55, "#C0708A"), (0.78, "#F29A72"), (1, "#FFD08A")], 0, 40, 0, 250, units="userSpaceOnUse"),
        lg(f"{u}-river", [(0, "#FFC88A"), (0.35, "#E8907A"), (1, "#6A4A6A")], 0, 300, 0, 372, units="userSpaceOnUse"),
        lg(f"{u}-hills", [(0, "#8A5E86"), (1, "#B87A8A")], 0, 190, 0, 250, units="userSpaceOnUse"),
        lg(f"{u}-near", [(0, "#4A2E46"), (1, "#2A1A2E")], 0, 340, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(112, 214, 300, "#FFE2A0", f"{u}-sun", 0.95))
    out.append(f'<circle cx="112" cy="211" r="15" fill="#FFF2CC"/>')
    for x, y, w, c in ((150, 120, 120, "#F4A0A0"), (420, 98, 130, "#C88AAE"), (520, 140, 80, "#F2B0A0"), (250, 158, 90, "#FFC8A0"), (90, 168, 70, "#FFD8A8"), (360, 182, 110, "#F8B890")):
        out.append(streak_cloud(x, y, w, c, 0.7, 4))
        out.append(streak_cloud(x - w * 0.2, y + 3, w * 0.6, "#FFE8C8", 0.5, 1.6))
    # the hills of Fiesole, villas and cypresses on the ridge
    ridge = rough([(-10, 222), (80, 214), (190, 200), (300, 206), (420, 192), (520, 198), (610, 190)], 23, amp=5, depth=4)
    out.append(Q(ridge + [(610, 260), (-10, 260)], f"url(#{u}-hills)"))
    rnd = random.Random(31)
    for _ in range(26):
        x = rnd.uniform(120, 600)
        y = y_on(ridge, x) or 210
        out.append(cypress_tree(x, y + 4, rnd.uniform(9, 16), rnd.random(), dark="#6A4A6E", mid="#7A5478", lit="#B07A8A", w=0.22))
    for _ in range(9):
        x = rnd.uniform(150, 590)
        y = (y_on(ridge, x) or 210) + rnd.uniform(6, 22)
        out.append(f'<rect x="{x:.1f}" y="{y - 4:.1f}" width="8" height="5" fill="#D8A8A0"/><path d="M {x - 1:.1f} {y - 4:.1f} L {x + 4:.1f} {y - 6.5:.1f} L {x + 9:.1f} {y - 4:.1f} Z" fill="#B87A7A"/>')
    out.append(f'<rect x="0" y="200" width="600" height="60" fill="#F8B890" opacity="0.18"/>')
    # rooftops of the city, far to near, with the landmarks rising out of them
    out.append(tuscan_roof_row(242, 0.42, 1, haze=0.5, haze_col="#E8A0A0"))
    out.append(tuscan_roof_row(250, 0.5, 2, haze=0.4, haze_col="#E8A0A0"))
    out.append(duomo(410, 196, 52, 66, u))
    out.append(campanile(334, 252, 128, 15, u))
    out.append(tuscan_roof_row(258, 0.58, 3, haze=0.3, haze_col="#E8A898"))
    out.append(palazzo_tower(190, 262, 120, 11, u))
    out.append(tuscan_roof_row(268, 0.68, 4, haze=0.2, haze_col="#E8A898"))
    out.append(tuscan_roof_row(280, 0.8, 5, haze=0.1, haze_col="#E8A898", lit_p=0.05))
    # the north bank facing the river (Lungarni), raking light from the left
    out.append(tuscan_roof_row(300, 1.0, 6, lit_p=0.08))
    out.append(Q([(-10, 300), (610, 300), (610, 306), (-10, 306)], "#B88A78"))
    # the Arno, glowing with the sky, the old bridge with its shops
    out.append(Q([(-10, 306), (610, 306), (610, 372), (-10, 372)], f"url(#{u}-river)"))
    out.append(water_lines(110, 5, (-10, 308, 610, 370), ["#FFE2B0", "#FFC890", "#8A5A7A", "#5A3A5A"], w=(8, 40), h=(0.8, 1.8), opacity=(0.35, 0.8)))
    out.append(water_lines(50, 6, (20, 308, 140, 370), ["#FFF2CC", "#FFFFFF"], w=(4, 16), h=(0.6, 1.4), opacity=(0.6, 1)))
    bx0, bx1, dk = 70, 300, 314
    piers = [70, 140, 222, 300]
    # reflection of the bridge
    out.append(f'<g opacity="0.35"><rect x="{bx0}" y="{dk + 22}" width="{bx1 - bx0}" height="26" fill="#4A2E46"/></g>')
    # houses hanging off the bridge: a jumble of little shop fronts with overhanging back-rooms on brackets
    rnd = random.Random(8)
    x = bx0 - 4
    cols = ["#E8A060", "#D8784E", "#F0C080", "#E6B090", "#C86A4E", "#F2D2A0", "#D89060"]
    while x < bx1 + 2:
        w = rnd.uniform(9, 16)
        h = rnd.uniform(16, 26)
        c = rnd.choice(cols)
        ov = rnd.uniform(1, 5)
        out.append(f'<rect x="{x:.1f}" y="{dk - h:.1f}" width="{w:.1f}" height="{h + ov:.1f}" fill="{c}"/>'
                   f'<rect x="{x + w * 0.7:.1f}" y="{dk - h:.1f}" width="{w * 0.3:.1f}" height="{h + ov:.1f}" fill="#7A3A4A" opacity="0.3"/>')
        for j in range(int(h / 8)):
            out.append(f'<rect x="{x + w * 0.25:.1f}" y="{dk - h + 3 + j * 8:.1f}" width="{w * 0.4:.1f}" height="4" fill="{rnd.choice(["#4E6A4A", "#4A3040", "#FFD27A"])}"/>')
        out.append(f'<path d="M {x:.1f} {dk + ov:.1f} L {x + w * 0.5:.1f} {dk + ov + 4:.1f} L {x + w:.1f} {dk + ov:.1f}" fill="none" stroke="#5A3A3A" stroke-width="1"/>')
        out.append(Q([(x - 1, dk - h), (x + w * 0.3, dk - h - 4), (x + w * 0.7, dk - h - 4), (x + w + 1, dk - h)], "#B85A3E"))
        out.append(Q([(x - 1, dk - h), (x + w * 0.3, dk - h - 4), (x + w * 0.5, dk - h - 4), (x + w * 0.4, dk - h)], "#F0905A"))
        x += w
    # the corridor running along the top with its row of small windows
    out.append(Q([(bx0 - 4, dk - 30), (bx1 + 4, dk - 30), (bx1 + 4, dk - 24), (bx0 - 4, dk - 24)], "#E8B078"))
    out.append(f'<g fill="#4A3040">' + "".join(f'<rect x="{bx0 + i * 7:.1f}" y="{dk - 28.5:.1f}" width="3" height="3"/>' for i in range(int((bx1 - bx0) / 7))) + "</g>")
    out.append(Q([(bx0 - 4, dk - 33), (bx1 + 4, dk - 33), (bx1 + 4, dk - 30), (bx0 - 4, dk - 30)], "#B85A3E"))
    # deck and three segmental arches
    out.append(Q([(bx0 - 6, dk), (bx1 + 6, dk), (bx1 + 6, dk + 22), (bx0 - 6, dk + 22)], "#D8A070"))
    for a, b in zip(piers, piers[1:]):
        a2, b2 = a + 6, b - 6
        out.append(f'<path d="M {a2} {dk + 24} L {a2} {dk + 14} Q {(a2 + b2) / 2} {dk + 2} {b2} {dk + 14} L {b2} {dk + 24} Z" fill="#3A2238"/>')
        out.append(f'<path d="M {a2} {dk + 14} Q {(a2 + b2) / 2} {dk + 2} {b2} {dk + 14}" fill="none" stroke="#FFD8A0" stroke-width="1.6"/>')
    for p in piers[1:-1]:
        out.append(f'<path d="M {p - 7} {dk + 24} L {p - 7} {dk + 12} L {p} {dk + 6} L {p + 7} {dk + 12} L {p + 7} {dk + 24} Z" fill="#C88A64"/><rect x="{p - 7}" y="{dk + 12}" width="5" height="12" fill="#FFD8A0" opacity="0.5"/>')
    out.append(f'<rect x="{bx0 - 6}" y="{dk}" width="{bx1 - bx0 + 12}" height="2" fill="#FFE2B0"/>')
    out.append(f'<path d="M {bx0 - 6} {dk + 24} Q 200 {dk + 28} {bx1 + 6} {dk + 24}" stroke="#FFE8C0" stroke-width="1.2" fill="none" opacity="0.6"/>')
    # a rowing scull on the river
    out.append(f'<path d="M 400 352 L 470 352 L 466 355 L 404 355 Z" fill="#F6F0E6"/><circle cx="436" cy="347" r="3" fill="#2A1E2A"/><path d="M 433 350 L 439 350 L 438 353 L 434 353 Z" fill="#C83A3A"/>'
               f'<path d="M 420 346 L 452 358 M 452 346 L 420 358" stroke="#2A1E2A" stroke-width="1"/><path d="M 470 354 Q 500 356 540 354" stroke="#FFE2B0" stroke-width="1.2" fill="none" opacity="0.7"/>')
    # the near (south) bank in shadow: rooftops, a few lit windows, umbrella pine and cypresses on the hillside
    near = []
    rnd = random.Random(44)
    x = -20
    while x < 620:
        w = rnd.uniform(26, 48)
        h = rnd.uniform(8, 18)
        y = 388 + rnd.uniform(-3, 4)
        near.append(f'<rect x="{x:.1f}" y="{y - h:.1f}" width="{w:.1f}" height="{h + 60:.1f}" fill="{rnd.choice(["#5A3A50", "#4E3448", "#62405A"])}"/>')
        near.append(Q([(x - 2, y - h), (x + w * 0.3, y - h - 6), (x + w * 0.7, y - h - 6), (x + w + 2, y - h)], "#6A3A44"))
        near.append(Q([(x - 2, y - h), (x + w * 0.3, y - h - 6), (x + w * 0.45, y - h - 6), (x + w * 0.4, y - h)], "#C8705A", ' opacity="0.8"'))
        for j in range(3):
            if rnd.random() < 0.4:
                near.append(f'<rect x="{x + rnd.uniform(4, w - 8):.1f}" y="{y - h + 6 + j * 9:.1f}" width="4" height="5" fill="#FFD27A"/>')
        x += w
    out.append(f'<g>{"".join(near)}</g>')
    out.append(f'<rect x="-10" y="350" width="620" height="94" fill="url(#{u}-near)" opacity="0.55"/>')
    out.append(cypress_tree(566, 444, 230, 14, dark="#1A1220", mid="#2A1E2E", lit="#7A4048", w=0.2, light=-1))
    out.append(cypress_tree(598, 444, 180, 15, dark="#1A1220", mid="#2A1E2E", lit="#7A4048", w=0.22, light=-1))
    # the terrace balustrade, a couple watching the sun go down, a lamp just lit
    by = 408
    out.append(Q([(-10, by), (610, by), (610, 444), (-10, 444)], "#6A4A58"))
    out.append(f'<rect x="-10" y="{by - 34}" width="620" height="8" fill="#E8B898"/><rect x="-10" y="{by - 34}" width="620" height="2.5" fill="#FFE2B8"/><rect x="-10" y="{by - 26}" width="620" height="3" fill="#3A2238" opacity="0.5"/>')
    for i in range(32):
        bx = -6 + i * 20
        out.append(f'<path d="M {bx} {by} L {bx} {by - 5} Q {bx + 4} {by - 8} {bx + 1} {by - 13} Q {bx - 2} {by - 20} {bx + 2} {by - 24} L {bx + 10} {by - 24} Q {bx + 14} {by - 20} {bx + 11} {by - 13} Q {bx + 8} {by - 8} {bx + 12} {by - 5} L {bx + 12} {by} Z" fill="#C8907A"/>'
                   f'<path d="M {bx + 1} {by - 13} Q {bx - 2} {by - 20} {bx + 2} {by - 24} L {bx + 5} {by - 24} Q {bx + 2} {by - 18} {bx + 4} {by - 13} Z" fill="#FFD0A8" opacity="0.8"/>')
    out.append(f'<rect x="-10" y="{by}" width="620" height="6" fill="#E0A888"/><rect x="-10" y="{by + 6}" width="620" height="40" fill="#4A3044"/>')
    # couple, backlit, leaning on the rail
    # couple seen from behind, forearms on the coping, his arm around her shoulders; rim light from the sun
    cp = by - 34
    out.append(f'<g transform="translate(318 {cp})">'
               # him: broad back, jacket, head
               f'<path d="M -46 40 L -44 6 Q -44 -12 -32 -16 L -14 -16 Q -2 -12 -2 6 L 0 40 Z" fill="#2E2236"/>'
               f'<path d="M -44 6 Q -50 0 -48 -2 L -40 -4" fill="none" stroke="#2E2236" stroke-width="7" stroke-linecap="round"/>'
               f'<path d="M -30 -17 L -28 -24 L -18 -24 L -16 -17 Z" fill="#3A2A2E"/><ellipse cx="-23" cy="-33" rx="9" ry="10.5" fill="#2A1A22"/>'
               f'<path d="M -32 -36 Q -30 -46 -22 -45 Q -14 -46 -13 -36 Q -16 -42 -23 -42 Q -29 -42 -32 -36 Z" fill="#1A1016"/>'
               # her: slimmer, long hair, light dress
               f'<path d="M 0 40 L 2 4 Q 2 -10 12 -13 L 24 -13 Q 32 -10 32 4 L 34 40 Z" fill="#E8A08A"/><path d="M 22 -13 Q 32 -10 32 4 L 34 40 L 26 40 Z" fill="#B8707A" opacity="0.6"/>'
               f'<path d="M 32 4 Q 38 -2 36 -4 L 30 -6" fill="none" stroke="#E8A08A" stroke-width="5" stroke-linecap="round"/>'
               f'<ellipse cx="17" cy="-26" rx="8" ry="9.5" fill="#3A2224"/><path d="M 8 -26 Q 6 -40 17 -38 Q 28 -40 26 -26 L 28 -8 Q 17 -4 7 -8 Z" fill="#4A2A26"/>'
               # his arm across her shoulders
               f'<path d="M -6 -10 Q 8 -16 22 -12" fill="none" stroke="#2E2236" stroke-width="6" stroke-linecap="round"/>'
               # warm rim light on the sunward (left) edges
               f'<path d="M -45 30 L -44 6 Q -44 -12 -32 -16 M -31 -38 Q -29 -45 -22 -45" fill="none" stroke="#FFC890" stroke-width="2.2" stroke-linecap="round"/>'
               f'<path d="M 3 30 L 2 4 Q 2 -10 9 -12 M 8 -27 Q 7 -38 15 -38" fill="none" stroke="#FFD8A8" stroke-width="2" stroke-linecap="round"/></g>')
    lx = 110
    out.append(glow(lx, by - 104, 40, "#FFE2A0", f"{u}-lamp", 0.7))
    out.append(f'<rect x="{lx - 2.5}" y="{by - 96}" width="5" height="96" fill="#2A1A2A"/><rect x="{lx - 6}" y="{by - 12}" width="12" height="12" fill="#2A1A2A"/>'
               f'<path d="M {lx - 8} {by - 96} L {lx + 8} {by - 96} L {lx + 6} {by - 114} L {lx - 6} {by - 114} Z" fill="#FFE6A8" stroke="#2A1A2A" stroke-width="2"/><path d="M {lx - 9} {by - 114} L {lx} {by - 122} L {lx + 9} {by - 114} Z" fill="#2A1A2A"/>')
    # a tall cypress framing the left edge, swifts over the river
    out.append(cypress_tree(30, 444, 300, 12, dark="#1A1220", mid="#2A1E2E", lit="#8A4A4A", w=0.2, light=-1))
    out.append(gulls([(250, 132, 9), (268, 142, 6), (470, 70, 8), (486, 78, 6)], "#3A2440", 1.8))
    return "\n".join(out)


# ================================================================ PISA — the leaning tower and the cathedral on the lawn, a clear morning
def leaning_tower(cx, base, D, lean, u):
    """Round Romanesque bell tower: a tall blind-arcaded ground storey, six open loggias of slender columns and a
    narrower bell chamber; cylinder shading lit from the upper left; drawn upright then rotated by `lean` degrees."""
    r = D / 2
    marble, shade, deep, hi = "#F8F4EA", "#A6AEC6", "#5A6480", "#FFFFFF"
    out = [defs(lg(f"{u}-cyl", [(0, "#DCD8D4"), (0.18, hi), (0.42, marble), (0.75, "#C8CAD6"), (1, shade)], 0, 0, 1, 0),
                lg(f"{u}-in", [(0, "#8A90A8"), (0.3, "#B8BCCC"), (0.7, deep), (1, "#3E4660")], 0, 0, 1, 0))]
    out.append(f'<g transform="rotate({lean:.2f} {cx:.1f} {base:.1f})">')
    H0 = 0.72 * D
    FH = 0.42 * D
    levels = [0, H0] + [H0 + FH * (i + 1) for i in range(6)]
    top6 = levels[-1]

    def sag(y):  # rings above the eye bow upward a little more the higher they are
        return 1.5 + (base - y) * 0.012

    def band(y0, y1, rr, fill, extra=""):
        s0, s1 = sag(y0), sag(y1)
        return (f'<path d="M {cx - rr:.1f} {y0 + s0:.1f} Q {cx:.1f} {y0 - s0:.1f} {cx + rr:.1f} {y0 + s0:.1f} L {cx + rr:.1f} {y1 + s1:.1f} '
                f'Q {cx:.1f} {y1 - s1:.1f} {cx - rr:.1f} {y1 + s1:.1f} Z" fill="{fill}"{extra}/>')
    # ground storey: wall with tall blind arches on engaged columns
    y0, y1 = base, base - H0
    out.append(band(y0, y1, r, f"url(#{u}-cyl)"))
    n = 15
    for i in range(n):
        th = -math.pi / 2 + math.pi * (i + 0.5) / n
        x = cx + r * math.sin(th)
        cw = max(0.6, D * 0.035 * math.cos(th))
        out.append(f'<rect x="{x - cw / 2:.1f}" y="{y1 + D * 0.08:.1f}" width="{cw:.1f}" height="{H0 - D * 0.1:.1f}" fill="{hi if math.sin(th) < 0.1 else "#D8DAE2"}" opacity="0.8"/>')
        if i < n - 1:
            th2 = -math.pi / 2 + math.pi * (i + 1.5) / n
            xa, xb = x, cx + r * math.sin(th2)
            out.append(f'<path d="M {xa:.1f} {y1 + D * 0.2:.1f} Q {(xa + xb) / 2:.1f} {y1 + D * 0.05 - sag(y1) * 0.6:.1f} {xb:.1f} {y1 + D * 0.2:.1f}" fill="none" stroke="#9EA4BA" stroke-width="{max(0.6, D * 0.012 * math.cos(th)):.2f}"/>')
    # a door with a lunette
    out.append(f'<path d="M {cx - D * 0.08:.1f} {base + 1:.1f} L {cx - D * 0.08:.1f} {base - D * 0.22:.1f} Q {cx:.1f} {base - D * 0.3:.1f} {cx + D * 0.08:.1f} {base - D * 0.22:.1f} L {cx + D * 0.08:.1f} {base + 1:.1f} Z" fill="#4A4E62"/>')
    # six loggias
    for k in range(6):
        ya, yb = base - levels[k + 1], base - levels[k + 2]
        out.append(band(ya, yb, r * 0.9, f"url(#{u}-in)"))
        # inner wall arches glimpsed behind
        cols = 30
        for i in range(cols):
            th = -math.pi / 2 + math.pi * (i + 0.5) / (cols / 2)
            if abs(th) > math.pi / 2:
                continue
            x = cx + r * 0.98 * math.sin(th)
            cw = max(0.7, D * 0.022 * math.cos(th) + 0.4)
            out.append(f'<rect x="{x - cw / 2:.1f}" y="{yb + D * 0.07:.1f}" width="{cw:.1f}" height="{FH - D * 0.11:.1f}" fill="{hi if math.sin(th) < 0.15 else "#C8CCD8"}"/>')
            th2 = th + math.pi / (cols / 2)
            if abs(th2) <= math.pi / 2:
                xb = cx + r * 0.98 * math.sin(th2)
                out.append(f'<path d="M {x:.1f} {yb + D * 0.12:.1f} Q {(x + xb) / 2:.1f} {yb + D * 0.03:.1f} {xb:.1f} {yb + D * 0.12:.1f}" fill="none" stroke="{marble if math.sin(th) < 0.3 else "#C0C4D2"}" stroke-width="{max(0.8, D * 0.025 * math.cos(th)):.2f}"/>')
        # shade the right part of the colonnade
        out.append(band(ya, yb, r, "#5A6480", ' opacity="0"'))
        # cornice ledge with a lit top and a shadow below it
        out.append(band(yb + D * 0.035, yb - D * 0.005, r * 1.04, f"url(#{u}-cyl)"))
        out.append(f'<path d="M {cx - r * 1.04:.1f} {yb + D * 0.035 + sag(yb):.1f} Q {cx:.1f} {yb + D * 0.035 - sag(yb):.1f} {cx + r * 1.04:.1f} {yb + D * 0.035 + sag(yb):.1f}" fill="none" stroke="#6A7090" stroke-width="{max(0.8, D * 0.02):.1f}" opacity="0.5"/>')
        out.append(band(ya - D * 0.01, ya - D * 0.035, r * 1.03, f"url(#{u}-cyl)"))
    # bell chamber
    yb6 = base - top6
    rb = r * 0.66
    hb = D * 0.3
    out.append(band(yb6, yb6 - hb, rb, f"url(#{u}-cyl)"))
    for i in range(7):
        th = -math.pi / 2 + math.pi * (i + 0.5) / 7
        x = cx + rb * 0.8 * math.sin(th)
        ow = max(1, D * 0.06 * math.cos(th))
        out.append(f'<path d="M {x - ow / 2:.1f} {yb6 - hb * 0.15:.1f} L {x - ow / 2:.1f} {yb6 - hb * 0.62:.1f} Q {x:.1f} {yb6 - hb * 0.82:.1f} {x + ow / 2:.1f} {yb6 - hb * 0.62:.1f} L {x + ow / 2:.1f} {yb6 - hb * 0.15:.1f} Z" fill="{deep}"/>')
    out.append(band(yb6 - hb + D * 0.02, yb6 - hb - D * 0.03, rb * 1.06, f"url(#{u}-cyl)"))
    # sunlit stripe and soft shadow side over the whole shaft
    out.append(f'<path d="M {cx - r * 0.55:.1f} {base:.1f} L {cx - r * 0.55:.1f} {yb6:.1f} L {cx - r * 0.25:.1f} {yb6:.1f} L {cx - r * 0.25:.1f} {base:.1f} Z" fill="#FFFFFF" opacity="0.18"/>')
    out.append(f'<path d="M {cx + r * 0.6:.1f} {base:.1f} L {cx + r * 0.6:.1f} {yb6 + D * 0.04:.1f} L {cx + r * 0.97:.1f} {yb6 + D * 0.04:.1f} L {cx + r * 0.97:.1f} {base:.1f} Z" fill="#4A5478" opacity="0.16"/>')
    out.append("</g>")
    return "".join(out)


def pisa_cathedral(u):
    """The cathedral at three-quarters: the arcaded facade on the left, its striped flank, the transept gable and
    the oval dome at the crossing, receding to the right."""
    marble, shd, stripe, deep = "#F6F2E8", "#C6C8D4", "#9EA2B4", "#4E5670"
    out = []
    g0 = 318
    # flank (receding right): aisle wall, clerestory, roofs
    fl_top_a = [(226, 236), (420, 262)]      # aisle eave line
    fl_top_c = [(226, 196), (420, 238)]      # clerestory eave line
    out.append(Q([(226, g0), (226, 196), (420, 238), (420, 300)], shd))
    out.append(Q([(226, 196), (226, 188), (420, 232), (420, 238)], "#8A8E9E"))
    out.append(Q([(226, 236), (226, 228), (420, 256), (420, 262)], "#8A8E9E"))
    for j in range(10):  # grey bands of the striped marble
        t = j / 10
        out.append(f'<line x1="226" y1="{lerp(240, g0, t):.1f}" x2="420" y2="{lerp(264, 300, t):.1f}" stroke="{stripe}" stroke-width="1.4" opacity="0.6"/>')
    for i in range(9):  # blind arcades of the aisle and the clerestory windows
        t = (i + 0.5) / 9
        x = lerp(232, 414, t)
        ya = lerp(250, 270, t)
        w_ = lerp(14, 8, t)
        out.append(f'<path d="M {x - w_ / 2:.1f} {lerp(g0, 300, t):.1f} L {x - w_ / 2:.1f} {ya:.1f} Q {x:.1f} {ya - w_ * 0.6:.1f} {x + w_ / 2:.1f} {ya:.1f} L {x + w_ / 2:.1f} {lerp(g0, 300, t):.1f}" fill="none" stroke="{stripe}" stroke-width="1.2"/>')
        out.append(f'<rect x="{x - w_ * 0.18:.1f}" y="{lerp(206, 244, t):.1f}" width="{w_ * 0.36:.1f}" height="{lerp(14, 9, t):.1f}" rx="{w_ * 0.18:.1f}" fill="{deep}"/>')
    # transept arm projecting toward us with its own arcaded gable
    tx0, tx1 = 336, 372
    out.append(Q([(tx0, 302), (tx0, 214), (tx1, 220), (tx1, 300)], marble))
    out.append(Q([(tx0 - 2, 214), ((tx0 + tx1) / 2, 194), (tx1 + 2, 220)], marble))
    out.append(Q([((tx0 + tx1) / 2, 194), (tx1 + 2, 220), (tx1 + 14, 226), ((tx0 + tx1) / 2 + 12, 199)], "#8A8E9E"))
    out.append(Q([(tx1, 300), (tx1, 220), (tx1 + 14, 226), (tx1 + 14, 298)], shd))
    for j in range(5):
        out.append(f'<rect x="{tx0 + 4 + j * 6.4:.1f}" y="218" width="3.4" height="10" rx="1.7" fill="{deep}"/>')
    for j in range(8):
        out.append(f'<line x1="{tx0}" y1="{232 + j * 9}" x2="{tx1}" y2="{233 + j * 9}" stroke="{stripe}" stroke-width="1.2" opacity="0.6"/>')
    # oval dome on its arcaded drum at the crossing
    dx, dy = 352, 196
    out.append(f'<rect x="{dx - 26}" y="{dy - 2}" width="52" height="14" fill="{marble}"/>' + "".join(
        f'<rect x="{dx - 24 + j * 5.2:.1f}" y="{dy + 1}" width="2.6" height="8" rx="1.3" fill="{deep}"/>' for j in range(10)))
    out.append(f'<path d="M {dx - 27} {dy - 2} Q {dx - 26} {dy - 34} {dx} {dy - 36} Q {dx + 26} {dy - 34} {dx + 27} {dy - 2} Z" fill="#8E96A8"/>'
               f'<path d="M {dx - 27} {dy - 2} Q {dx - 26} {dy - 34} {dx} {dy - 36} Q {dx - 12} {dy - 26} {dx - 10} {dy - 2} Z" fill="#C8D0DA"/>')
    for t in (-0.6, -0.2, 0.2, 0.6):
        out.append(f'<path d="M {dx + t * 27:.1f} {dy - 2} Q {dx + t * 22:.1f} {dy - 28} {dx} {dy - 36}" fill="none" stroke="#6A7288" stroke-width="0.9" opacity="0.7"/>')
    out.append(f'<rect x="{dx - 3}" y="{dy - 44}" width="6" height="8" fill="{marble}"/><path d="M {dx - 4} {dy - 44} Q {dx} {dy - 51} {dx + 4} {dy - 44} Z" fill="#8E96A8"/><circle cx="{dx}" cy="{dy - 52}" r="1.6" fill="#E8C060"/>')
    # facade: blind arcade and three bronze doors, then four tiers of open galleries
    fx0, fx1 = 70, 226
    W = fx1 - fx0
    out.append(Q([(fx0, g0), (fx0, 216), (fx0 + W * 0.24, 200), (fx0 + W * 0.24, 152), (fx0 + W * 0.5, 128), (fx1 - W * 0.24, 152), (fx1 - W * 0.24, 200), (fx1, 216), (fx1, g0)], marble))
    for j in range(9):
        out.append(f'<line x1="{fx0}" y1="{g0 - 6 - j * 7}" x2="{fx1}" y2="{g0 - 6 - j * 7}" stroke="{stripe}" stroke-width="1.3" opacity="0.55"/>')
    for i in range(7):
        x = fx0 + W * (i + 0.5) / 7
        w_ = W / 7 * 0.72
        out.append(f'<path d="M {x - w_ / 2:.1f} {g0} L {x - w_ / 2:.1f} 266 Q {x:.1f} 252 {x + w_ / 2:.1f} 266 L {x + w_ / 2:.1f} {g0}" fill="none" stroke="#B8BCC8" stroke-width="2"/>')
        if i in (1, 3, 5):
            dw = w_ * (0.62 if i != 3 else 0.74)
            out.append(f'<rect x="{x - dw / 2:.1f}" y="{g0 - (40 if i == 3 else 32)}" width="{dw:.1f}" height="{40 if i == 3 else 32}" fill="#7A5A3A"/><rect x="{x - dw / 2:.1f}" y="{g0 - (40 if i == 3 else 32)}" width="{dw:.1f}" height="{40 if i == 3 else 32}" fill="none" stroke="#E8C070" stroke-width="1"/>'
                       f'<line x1="{x:.1f}" y1="{g0 - (40 if i == 3 else 32)}" x2="{x:.1f}" y2="{g0}" stroke="#4A3422" stroke-width="1"/>')
    for k, (ya, yb, xa, xb) in enumerate(((246, 222, fx0, fx1), (218, 202, fx0 + 6, fx1 - 6), (198, 176, fx0 + W * 0.24, fx1 - W * 0.24), (172, 154, fx0 + W * 0.28, fx1 - W * 0.28))):
        out.append(f'<rect x="{xa:.1f}" y="{yb:.1f}" width="{xb - xa:.1f}" height="{ya - yb:.1f}" fill="{deep}"/>')
        nn = int((xb - xa) / 7.5)
        for i in range(nn + 1):
            x = xa + (xb - xa) * i / nn
            out.append(f'<rect x="{x - 1.2:.1f}" y="{yb:.1f}" width="2.4" height="{ya - yb:.1f}" fill="{marble}"/>')
            if i < nn:
                out.append(f'<path d="M {x:.1f} {yb + 5:.1f} Q {x + (xb - xa) / nn / 2:.1f} {yb - 1:.1f} {x + (xb - xa) / nn:.1f} {yb + 5:.1f}" fill="none" stroke="{marble}" stroke-width="1.6"/>')
        out.append(f'<rect x="{xa - 2:.1f}" y="{ya:.1f}" width="{xb - xa + 4:.1f}" height="3" fill="{marble}"/><rect x="{xa - 2:.1f}" y="{yb - 2:.1f}" width="{xb - xa + 4:.1f}" height="3" fill="{marble}"/>')
    # sloping gallery sides of the upper tiers and the statue on the apex
    out.append(Q([(fx0, 216), (fx0 + W * 0.24, 200), (fx0 + W * 0.24, 204), (fx0, 220)], "#B8BCC8"))
    out.append(Q([(fx1, 216), (fx1 - W * 0.24, 200), (fx1 - W * 0.24, 204), (fx1, 220)], "#B8BCC8"))
    out.append(f'<path d="M {fx0 + W * 0.5 - 3:.1f} 128 L {fx0 + W * 0.5 - 2:.1f} 116 Q {fx0 + W * 0.5:.1f} 112 {fx0 + W * 0.5 + 2:.1f} 116 L {fx0 + W * 0.5 + 3:.1f} 128 Z" fill="#E8E4DA"/>')
    for sx_ in (fx0 + 2, fx1 - 2, fx0 + W * 0.24, fx1 - W * 0.24):
        out.append(f'<path d="M {sx_ - 2:.1f} {216 if sx_ in (fx0 + 2, fx1 - 2) else 152} l 1 -9 q 1 -3 2 0 l 1 9 Z" fill="#E8E4DA"/>')
    # morning light from the left: the facade glows, the flank sits in soft blue shade
    out.append(Q([(fx0, g0), (fx0, 216), (fx0 + W * 0.24, 200), (fx0 + W * 0.24, 152), (fx0 + W * 0.5, 128), (fx0 + W * 0.5, g0)], "#FFF2D8", ' opacity="0.22"'))
    out.append(Q([(226, g0), (226, 196), (420, 238), (420, 300)], "#7A84A8", ' opacity="0.18"'))
    return "".join(out)


def pisa():
    u = "pi"
    out = [defs(
        lg(f"{u}-sky", [(0, "#2A72C8"), (0.45, "#5E9CDA"), (0.8, "#A8CCEA"), (1, "#E2EEF2")], 0, 40, 0, 320, units="userSpaceOnUse"),
        lg(f"{u}-lawn", [(0, "#7CBA54"), (0.4, "#4E9A3E"), (1, "#2E7234")], 0, 300, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-path", [(0, "#E8E4DA"), (1, "#C8C2B6")], 0, 300, 0, 444, units="userSpaceOnUse"),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(30, 50, 280, "#FFFBEA", f"{u}-sun", 0.75))
    out.append(cumulus(f"{u}-c1", 250, 92, 120, 28, 3, "#FFFFFF", "#F2F6FA", "#B8C8DE", hi="#FFFFFF", hi_op=0.8, light=-1))
    out.append(cumulus(f"{u}-c2", 560, 150, 110, 26, 8, "#FFFFFF", "#F2F6FA", "#BCCCE0", hi="#FFFFFF", hi_op=0.8, light=-1))
    out.append(streak_cloud(196, 122, 60, "#FFFFFF", 0.55, 3))
    # beyond the square: the old walls, stone pines and the long cloister wall
    out.append(Q(rough([(-10, 292), (200, 290), (400, 288), (610, 290)], 3, amp=2, depth=3) + [(610, 312), (-10, 312)], "#C8B49C"))
    out.append(f'<g fill="#C8B49C">' + "".join(f'<rect x="{x}" y="286" width="6" height="5"/>' for x in range(420, 610, 11)) + "</g>")
    for x, y, rx, ry, sd in ((500, 282, 40, 16, 21), (566, 278, 44, 20, 22), (12, 282, 36, 16, 24), (450, 290, 26, 10, 25)):
        out.append(leaf_canopy(f"{u}-p{sd}", x, y, rx, ry, sd, "#4E6A5A", "#6A8468", "#A8BC86", gold="#E8E2A8", light=(-1, -1), n=50, r=(0.2, 0.34)))
    for x, h in ((470, 50), (528, 58), (600, 46)):
        out.append(cypress_tree(x, 302, h, x, dark="#3E5A4A", mid="#4E6A56", lit="#94AA7E", light=-1))
    out.append(Q([(-10, 300), (610, 300), (610, 316), (-10, 316)], "#EAE6DC"))
    out.append(f'<rect x="-10" y="300" width="620" height="2" fill="#FFFFFF"/><rect x="-10" y="314" width="620" height="2" fill="#B8B4AA"/>')
    # the lawn with mowing stripes fanning toward us
    out.append(Q([(-10, 312), (610, 312), (610, 444), (-10, 444)], f"url(#{u}-lawn)"))
    for i in range(-12, 14):
        x0 = 300 + i * 26
        x1 = 300 + i * 120
        if i % 2:
            out.append(Q([(x0, 312), (x0 + 26, 312), (x1 + 120, 470), (x1, 470)], "#FFFFFF", ' opacity="0.07"'))
    rg_ = random.Random(4)
    tufts = []
    for _ in range(110):
        x, y = rg_.uniform(300, 610), rg_.uniform(372, 444)
        hh = 3 + (y - 372) * 0.07
        c = rg_.choice(["#2E6A2E", "#3E7E36", "#9AD46A"])
        tufts.append(f'<path d="M {x - 2:.1f} {y:.1f} l -1 {-hh:.1f} M {x:.1f} {y:.1f} l 0.5 {-hh * 1.3:.1f} M {x + 2:.1f} {y:.1f} l 1.4 {-hh:.1f}" stroke="{c}"/>')
    out.append(f'<g fill="none" stroke-width="1.2" stroke-linecap="round" opacity="0.7">{"".join(tufts)}</g>')
    # cathedral and the tower behind it, with their shadows thrown right across the lawn
    out.append(Q([(172, 318), (337, 302), (420, 312), (240, 332)], "#2E5A3A", ' opacity="0.3"'))
    out.append(f'<g transform="translate(52 318) scale(0.85) translate(-70 -318)">{pisa_cathedral(u)}</g>')
    tcx, tb, D, lean = 392, 338, 68, 4.0
    out.append(Q([(tcx - 30, tb + 2), (tcx + 30, tb + 2), (tcx + 200, tb + 30), (tcx + 150, tb + 42)], "#1E4A2A", ' opacity="0.3"'))
    out.append(f'<ellipse cx="{tcx}" cy="{tb + 1}" rx="{D * 0.62:.1f}" ry="5" fill="#E8E4DA"/><ellipse cx="{tcx}" cy="{tb - 1}" rx="{D * 0.56:.1f}" ry="4" fill="#F6F2EA"/>')
    out.append(leaning_tower(tcx, tb, D, lean, f"{u}-t"))
    # marble paths
    out.append(Q([(60, 320), (240, 320), (300, 444), (-10, 444), (-10, 400)], f"url(#{u}-path)"))
    out.append(Q([(60, 320), (240, 320), (244, 324), (62, 324)], "#FFFFFF", ' opacity="0.6"'))
    out.append(dots(80, 8, (0, 330, 290, 444), "#A8A296", r=(0.6, 1.4), opacity=(0.3, 0.6)))
    # visitors on the square — one of them, of course, propping up the tower
    for px, py, h, c, pose in ((120, 340, 30, "#E8504A", 0), (140, 342, 29, "#3E5A8A", 0), (186, 352, 34, "#F2C24A", 1), (76, 358, 36, "#6A4A8A", 0), (262, 336, 26, "#2E8A7A", 1), (300, 334, 25, "#E87A9A", 0)):
        out.append(figure(px, py, h, c, rim="#FFF6E0", rim_side=-1))
        if pose:
            s_ = h / 100
            out.append(f'<path d="M {px + 10 * s_:.1f} {py - 80 * s_:.1f} L {px + 30 * s_:.1f} {py - 118 * s_:.1f}" stroke="{c}" stroke-width="{max(1.4, 7 * s_):.1f}" stroke-linecap="round"/>'
                       f'<circle cx="{px + 31 * s_:.1f}" cy="{py - 121 * s_:.1f}" r="{max(1, 4 * s_):.1f}" fill="#E8B898"/>')
    # a friend crouching to frame the shot
    out.append(f'<g transform="translate(222 372)"><ellipse cx="0" cy="2" rx="16" ry="3" fill="#1E4A26" opacity="0.4"/><path d="M -10 0 L -8 -14 L 8 -16 L 10 0 Z" fill="#2E3446"/>'
               f'<path d="M -9 -14 Q -10 -34 2 -36 Q 12 -34 10 -16 Z" fill="#E8E2D2"/><circle cx="2" cy="-44" r="7" fill="#C8906A"/><path d="M -5 -46 Q 2 -54 9 -46 Z" fill="#3A2A22"/>'
               f'<rect x="-14" y="-46" width="9" height="6" rx="1.5" fill="#2A2A30"/><path d="M -2 -32 L -10 -42" stroke="#C8906A" stroke-width="3" stroke-linecap="round"/></g>')
    # the hero tourist in the foreground, palm pressed to the tower as if holding it up
    hx, hy = 486, 448
    out.append(f'<ellipse cx="{hx + 20}" cy="{hy - 4}" rx="44" ry="7" fill="#1E4A26" opacity="0.35"/>')
    out.append(f'<g transform="translate({hx} {hy})">'
               # legs, shorts
               f'<path d="M -16 0 L -14 -62 L -2 -62 L -4 0 Z" fill="#C8906A"/><path d="M 2 0 L 2 -62 L 14 -62 L 16 0 Z" fill="#B87E5A"/>'
               f'<path d="M -20 -58 L -18 -96 L 20 -96 L 20 -58 L 4 -58 L 1 -70 L -2 -58 Z" fill="#2E5A8E"/>'
               # torso: striped tee, tote bag on the shoulder
               f'<path d="M -22 -94 L -24 -146 Q -2 -158 22 -148 L 22 -94 Z" fill="#F6F2EA"/>'
               + "".join(f'<rect x="-24" y="{-150 + j * 10}" width="47" height="4" fill="#E8504A"/>' for j in range(6))
               + f'<path d="M 22 -148 L 22 -94 L 10 -94 Q 14 -120 12 -150 Z" fill="#2A3048" opacity="0.15"/>'
               f'<path d="M 16 -146 L 26 -96" stroke="#C8A060" stroke-width="3"/><rect x="18" y="-100" width="22" height="26" rx="3" fill="#E8C060"/><rect x="18" y="-100" width="22" height="5" fill="#D8A040"/>'
               # the raised arm reaching up-left to the tower, palm flat
               f'<path d="M -18 -144 Q -40 -170 -56 -196" fill="none" stroke="#C8906A" stroke-width="10" stroke-linecap="round"/>'
               f'<path d="M -18 -144 Q -26 -152 -30 -160" fill="none" stroke="#F6F2EA" stroke-width="13" stroke-linecap="round"/>'
               f'<path d="M -56 -196 L -66 -206 Q -70 -212 -64 -214 L -58 -208 L -60 -218 Q -58 -224 -53 -219 L -51 -208 L -49 -220 Q -46 -225 -43 -219 L -45 -205 Q -46 -196 -52 -192 Z" fill="#D89A74"/>'
               # other hand on the hip
               f'<path d="M 20 -140 Q 34 -122 22 -104" fill="none" stroke="#C8906A" stroke-width="9" stroke-linecap="round"/>'
               # head, straw sun hat, sunglasses, smile
               f'<rect x="-6" y="-166" width="12" height="12" fill="#C8906A"/><ellipse cx="0" cy="-180" rx="15" ry="17" fill="#D89A74"/>'
               f'<path d="M -15 -184 Q -16 -170 -12 -160 Q -18 -168 -18 -180 Z" fill="#6A3A22"/><path d="M 15 -184 Q 18 -168 12 -158 Q 20 -164 19 -180 Z" fill="#6A3A22"/>'
               f'<ellipse cx="0" cy="-192" rx="32" ry="7" fill="#E8C878"/><path d="M -16 -192 Q -14 -212 0 -212 Q 14 -212 16 -192 Z" fill="#F0D488"/><rect x="-16" y="-198" width="32" height="5" fill="#E8504A"/>'
               f'<path d="M -32 -192 Q 0 -186 32 -192" fill="none" stroke="#C8A050" stroke-width="1.5"/>'
               f'<rect x="-12" y="-185" width="10" height="7" rx="3" fill="#1E1E28"/><rect x="2" y="-185" width="10" height="7" rx="3" fill="#1E1E28"/><line x1="-2" y1="-183" x2="2" y2="-183" stroke="#1E1E28" stroke-width="1.5"/>'
               f'<path d="M -6 -171 Q 0 -166 6 -171" fill="none" stroke="#8A3A30" stroke-width="2" stroke-linecap="round"/>'
               # morning rim light on the left edges
               f'<path d="M -22 -96 L -24 -146" stroke="#FFFFFF" stroke-width="2" opacity="0.7"/><path d="M -14 -60 L -16 0" stroke="#F2C8A8" stroke-width="2"/></g>')
    out.append(gulls([(150, 110, 9), (170, 120, 6), (360, 80, 8)], "#3A4A6A", 1.8))
    return "\n".join(out)


# ================================================================ AMALFI COAST — a pastel village tumbling down to the sea, late afternoon
def lemon(cx, cy, rx, ry, rot, seed):
    rnd = random.Random(seed)
    g = [f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.1f})">']
    g.append(f'<path d="M {-rx:.1f} 0 Q {-rx:.1f} {-ry:.1f} 0 {-ry:.1f} Q {rx * 0.8:.1f} {-ry:.1f} {rx:.1f} {-ry * 0.15:.1f} L {rx * 1.22:.1f} 0 L {rx:.1f} {ry * 0.15:.1f} Q {rx * 0.8:.1f} {ry:.1f} 0 {ry:.1f} Q {-rx:.1f} {ry:.1f} {-rx:.1f} 0 Z" fill="url(#ac-lemon)"/>')
    g.append(f'<path d="M {-rx * 1.12:.1f} 0 L {-rx * 0.92:.1f} {-ry * 0.12:.1f} L {-rx * 0.92:.1f} {ry * 0.12:.1f} Z" fill="#C8A020"/>')
    g.append(f'<ellipse cx="{-rx * 0.25:.1f}" cy="{-ry * 0.45:.1f}" rx="{rx * 0.4:.1f}" ry="{ry * 0.18:.1f}" fill="#FFFBD0" opacity="0.75"/>')
    g.append(f'<path d="M {-rx * 0.6:.1f} {ry * 0.6:.1f} Q 0 {ry * 1.0:.1f} {rx * 0.7:.1f} {ry * 0.5:.1f}" fill="none" stroke="#C88A10" stroke-width="{max(1, ry * 0.12):.1f}" opacity="0.45"/>')
    g.append(dots(int(rx * ry / 6), seed, (-rx * 0.8, -ry * 0.7, rx * 0.8, ry * 0.7), "#D8A818", r=(0.4, 0.9), opacity=(0.3, 0.6)))
    g.append("</g>")
    return "".join(g)


def leaf(x, y, L, ang, w=0.32, dark="#1E4A26", mid="#2E6A30", lit="#7AAE4A"):
    a = math.radians(ang)
    ex, ey = x + L * math.cos(a), y + L * math.sin(a)
    nx, ny = -math.sin(a) * L * w, math.cos(a) * L * w
    mx, my = (x + ex) / 2, (y + ey) / 2
    return (f'<path d="M {x:.1f} {y:.1f} Q {mx + nx:.1f} {my + ny:.1f} {ex:.1f} {ey:.1f} Q {mx - nx:.1f} {my - ny:.1f} {x:.1f} {y:.1f} Z" fill="{mid}"/>'
            f'<path d="M {x:.1f} {y:.1f} Q {mx - nx:.1f} {my - ny:.1f} {ex:.1f} {ey:.1f} Q {mx - nx * 0.2:.1f} {my - ny * 0.2:.1f} {x:.1f} {y:.1f} Z" fill="{lit}" opacity="0.75"/>'
            f'<path d="M {x:.1f} {y:.1f} Q {mx + nx * 0.1:.1f} {my + ny * 0.1:.1f} {ex:.1f} {ey:.1f}" fill="none" stroke="{dark}" stroke-width="{max(0.8, L * 0.04):.1f}" opacity="0.7"/>')


def amalfi_house(x, base, w, h, rnd, k=1.0, sun=-1):
    """A cubic house on the slope: pastel wall in raking light, flat terrace roof or a small white vault,
    arched windows with shutters, sometimes a pergola or bougainvillea."""
    walls = [("#F6C8A8", "#C88E7E"), ("#F8E0B0", "#CDAE88"), ("#F4B2A6", "#C47E80"), ("#FBF2E4", "#CEC2BA"), ("#F2D27A", "#C8A060"),
             ("#F6D8C8", "#C8A2A2"), ("#E8A88A", "#B87468"), ("#FFF4D8", "#D0C2AA")]
    wall, wsh = rnd.choice(walls)
    out = [f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h + 8 * k:.1f}" fill="{wall}"/>']
    # shade side (sun from the left): the right strip, and a cast shadow under the parapet
    sw = w * rnd.uniform(0.18, 0.3)
    out.append(f'<rect x="{x + w - sw:.1f}" y="{base - h:.1f}" width="{sw:.1f}" height="{h + 8 * k:.1f}" fill="{wsh}"/>')
    out.append(f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w * 0.35:.1f}" height="{h + 8 * k:.1f}" fill="#FFF0C8" opacity="0.28"/>')
    # windows: small arched openings with green or blue shutters
    cols = max(1, int((w - sw) / (7 * k)))
    rows = max(1, int(h / (8 * k)))
    sh = rnd.choice(["#3E7A5A", "#2E6A8A", "#4E8A6A", "#5A6A8A"])
    for r_ in range(rows):
        for c_ in range(cols):
            wx = x + (c_ + 0.5) * (w - sw) / cols - 1.5 * k
            wy = base - h + 3 * k + r_ * 8 * k
            if rnd.random() < 0.8:
                out.append(f'<path d="M {wx:.1f} {wy + 4.5 * k:.1f} L {wx:.1f} {wy + 1.2 * k:.1f} Q {wx + 1.5 * k:.1f} {wy - 0.4 * k:.1f} {wx + 3 * k:.1f} {wy + 1.2 * k:.1f} L {wx + 3 * k:.1f} {wy + 4.5 * k:.1f} Z" fill="#3A2E3A"/>')
                if rnd.random() < 0.5:
                    out.append(f'<rect x="{wx - 1.4 * k:.1f}" y="{wy + 0.6 * k:.1f}" width="{1.3 * k:.1f}" height="{3.9 * k:.1f}" fill="{sh}"/><rect x="{wx + 3.1 * k:.1f}" y="{wy + 0.6 * k:.1f}" width="{1.3 * k:.1f}" height="{3.9 * k:.1f}" fill="{sh}"/>')
    # roof: terrace parapet, or a little white barrel vault, sometimes a pergola
    r = rnd.random()
    out.append(f'<rect x="{x - 0.5 * k:.1f}" y="{base - h - 1.6 * k:.1f}" width="{w + k:.1f}" height="{1.8 * k:.1f}" fill="{mix(wall, "#FFFFFF", 0.4)}"/>')
    out.append(f'<rect x="{x:.1f}" y="{base - h + 0.2 * k:.1f}" width="{w:.1f}" height="{1.2 * k:.1f}" fill="#000" opacity="0.12"/>')
    if r < 0.28:
        out.append(f'<path d="M {x + w * 0.1:.1f} {base - h - 1.6 * k:.1f} Q {x + w * 0.45:.1f} {base - h - 8 * k:.1f} {x + w * 0.8:.1f} {base - h - 1.6 * k:.1f} Z" fill="#FBF6EC"/>'
                   f'<path d="M {x + w * 0.45:.1f} {base - h - 6.4 * k:.1f} Q {x + w * 0.7:.1f} {base - h - 5 * k:.1f} {x + w * 0.8:.1f} {base - h - 1.6 * k:.1f} L {x + w * 0.5:.1f} {base - h - 1.6 * k:.1f} Z" fill="#D8CCC4"/>')
    elif r < 0.5:
        px0 = x + w * 0.1
        out.append(f'<g stroke="#7A5A44" stroke-width="{max(0.7, 0.5 * k):.1f}">' + "".join(
            f'<line x1="{px0 + i * w * 0.2:.1f}" y1="{base - h - 1.6 * k:.1f}" x2="{px0 + i * w * 0.2:.1f}" y2="{base - h - 6 * k:.1f}"/>' for i in range(5)) + "</g>")
        out.append(blobs(int(6 + w / 3), int(x * 7), (px0 - 2, base - h - 8 * k, px0 + w * 0.82, base - h - 5 * k), ["#4E7A34", "#6A9A40", "#3E6A2E"], r=(1.4 * k, 2.6 * k), opacity=(0.9, 1), squash=0.7))
    if rnd.random() < 0.28:
        side = rnd.choice((0, 1))
        bx = x + (w * 0.05 if side == 0 else w * 0.6)
        out.append(blobs(int(8 + w / 2), int(x * 11), (bx, base - h * 0.6, bx + w * 0.4, base + 2 * k), ["#D8327A", "#F25A9A", "#B8205E", "#4E7A34"], r=(1.2 * k, 2.4 * k), opacity=(0.9, 1), squash=0.9))
    return "".join(out)


def majolica_dome(cx, base, r, u):
    """Church with a dome of glazed majolica tiles (yellow, green, blue diamonds) and a lantern; bell tower."""
    out = [defs(lg(f"{u}-dome", [(0, "#FFE890"), (0.4, "#E8B830"), (1, "#7A6A30")], 0, 0, 1, 0))]
    # church body and bell tower
    out.append(f'<rect x="{cx - r * 1.8:.1f}" y="{base - r * 1.1:.1f}" width="{r * 3.6:.1f}" height="{r * 1.4:.1f}" fill="#FBF2E2"/><rect x="{cx + r * 0.9:.1f}" y="{base - r * 1.1:.1f}" width="{r * 0.9:.1f}" height="{r * 1.4:.1f}" fill="#D8CABC"/>')
    bt = cx - r * 2.4
    out.append(f'<rect x="{bt - r * 0.45:.1f}" y="{base - r * 2.9:.1f}" width="{r * 0.9:.1f}" height="{r * 3.2:.1f}" fill="#FBF2E2"/><rect x="{bt + r * 0.15:.1f}" y="{base - r * 2.9:.1f}" width="{r * 0.3:.1f}" height="{r * 3.2:.1f}" fill="#D8CABC"/>'
               f'<path d="M {bt - r * 0.18:.1f} {base - r * 2.2:.1f} L {bt - r * 0.18:.1f} {base - r * 2.55:.1f} Q {bt:.1f} {base - r * 2.75:.1f} {bt + r * 0.18:.1f} {base - r * 2.55:.1f} L {bt + r * 0.18:.1f} {base - r * 2.2:.1f} Z" fill="#4A3A44"/>'
               f'<path d="M {bt - r * 0.55:.1f} {base - r * 2.9:.1f} L {bt + r * 0.55:.1f} {base - r * 2.9:.1f} L {bt:.1f} {base - r * 3.5:.1f} Z" fill="#E8B830"/>')
    # drum and dome
    out.append(f'<rect x="{cx - r * 0.95:.1f}" y="{base - r * 1.55:.1f}" width="{r * 1.9:.1f}" height="{r * 0.5:.1f}" fill="#FBF2E2"/><rect x="{cx + r * 0.4:.1f}" y="{base - r * 1.55:.1f}" width="{r * 0.55:.1f}" height="{r * 0.5:.1f}" fill="#D8CABC"/>')
    dome_d = f'M {cx - r:.1f} {base - r * 1.55:.1f} Q {cx - r:.1f} {base - r * 2.6:.1f} {cx:.1f} {base - r * 2.7:.1f} Q {cx + r:.1f} {base - r * 2.6:.1f} {cx + r:.1f} {base - r * 1.55:.1f} Z'
    out.append(f'<clipPath id="{u}-dc"><path d="{dome_d}"/></clipPath><path d="{dome_d}" fill="url(#{u}-dome)"/>')
    g = [f'<g clip-path="url(#{u}-dc)">']
    for j in range(7):
        y0 = base - r * 1.55 - j * r * 0.17
        for i in range(-6, 7):
            t = i / 6
            x0 = cx + math.sin(t * 1.3) * r * 0.95
            s = r * 0.09 * math.cos(t * 1.1)
            c = ["#2E8A5A", "#2E5EA8", "#2E8A5A", "#F6F0E0"][(i + j) % 4]
            g.append(f'<path d="M {x0:.1f} {y0 - s * 1.4:.1f} L {x0 + s:.1f} {y0 - s * 0.4:.1f} L {x0:.1f} {y0 + s * 0.6:.1f} L {x0 - s:.1f} {y0 - s * 0.4:.1f} Z" fill="{c}" opacity="0.9"/>')
    g.append(f'<path d="M {cx + r * 0.2:.1f} {base - r * 2.7:.1f} Q {cx + r:.1f} {base - r * 2.6:.1f} {cx + r:.1f} {base - r * 1.55:.1f} L {cx + r * 0.3:.1f} {base - r * 1.55:.1f} Z" fill="#3A2A3A" opacity="0.28"/>')
    g.append(f'<path d="M {cx - r * 0.75:.1f} {base - r * 1.75:.1f} Q {cx - r * 0.7:.1f} {base - r * 2.45:.1f} {cx - r * 0.1:.1f} {base - r * 2.62:.1f}" fill="none" stroke="#FFFBE0" stroke-width="{max(1.2, r * 0.1):.1f}" opacity="0.8"/>')
    g.append("</g>")
    out.append("".join(g))
    out.append(f'<rect x="{cx - r * 0.18:.1f}" y="{base - r * 3.05:.1f}" width="{r * 0.36:.1f}" height="{r * 0.38:.1f}" fill="#FBF2E2"/><path d="M {cx - r * 0.24:.1f} {base - r * 3.05:.1f} Q {cx:.1f} {base - r * 3.3:.1f} {cx + r * 0.24:.1f} {base - r * 3.05:.1f} Z" fill="#E8B830"/>')
    return "".join(out)


def amalfi():
    u = "ac"
    out = [defs(
        lg(f"{u}-sky", [(0, "#3A7CC0"), (0.45, "#7CB2DC"), (0.8, "#D6E2DC"), (1, "#F8E4BC")], 0, 40, 0, 250, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#4ACAC4"), (0.25, "#2AA2B8"), (0.7, "#1A6E9E"), (1, "#14507E")], 0, 366, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#A8A8BE"), (1, "#C8C0C6")], 0, 100, 0, 240, units="userSpaceOnUse"),
        lg(f"{u}-mid", [(0, "#A09A92"), (0.35, "#7E8462"), (1, "#4E6A3E")], 0, 100, 0, 300, units="userSpaceOnUse"),
        lg(f"{u}-lemon", [(0, "#FFF27A"), (0.55, "#F6D234"), (1, "#D8A418")], 0, 0, 0, 1),
        lg(f"{u}-rock", [(0, "#D8B48A"), (1, "#8A6E62")], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    out.append(glow(20, 150, 300, "#FFF0C8", f"{u}-sun", 0.8))
    out.append(streak_cloud(300, 96, 90, "#FFFFFF", 0.55, 4))
    out.append(cumulus(f"{u}-c1", 210, 130, 110, 26, 4, "#FFFAF0", "#F4F0EA", "#C0C4D4", hi="#FFFFFF", light=-1))
    # the Lattari mountains: a far pale range, then the steep limestone peaks over the village
    far = rough([(-10, 196), (60, 168), (130, 150), (190, 172), (260, 140), (330, 118), (390, 150), (460, 132), (530, 160), (610, 150)], 61, amp=7, depth=4)
    out.append(Q(far + [(610, 300), (-10, 300)], f"url(#{u}-far)"))
    mid_r = rough([(-10, 196), (50, 150), (110, 118), (170, 150), (230, 132), (300, 160), (360, 128), (420, 104), (480, 136), (540, 120), (610, 150)], 62, amp=9, depth=4)
    out.append(Q(mid_r + [(610, 360), (-10, 360)], f"url(#{u}-mid)"))
    out.append(f'<clipPath id="{u}-mc"><polygon points="{P(mid_r + [(610, 360), (-10, 360)])}"/></clipPath>')
    out.append(f'<g clip-path="url(#{u}-mc)">' + streaks(110, 63, (-10, 100, 610, 250), ["#B8AEA0", "#E8D8BC", "#5E5A54"], w=(1.5, 4.5), length=(12, 50), opacity=(0.25, 0.55), slant=0.2)
               + blobs(420, 64, (-10, 130, 610, 300), ["#4E6A3A", "#5E7A42", "#3E5A32", "#6E8A4A", "#7E9A56"], r=(1.6, 5), opacity=(0.55, 0.95), squash=0.6)
               + f'<polygon points="{P([(x, y) for x, y in mid_r] + [(610, 260), (-10, 260)])}" fill="#FFE2B0" opacity="0.12"/></g>')
    # the road threading along the mountainside
    out.append(f'<path d="M -10 206 Q 90 186 170 196 Q 250 206 300 190 Q 380 166 470 176 Q 540 184 610 172" fill="none" stroke="#E8DCC8" stroke-width="2.4" opacity="0.8"/>')
    out.append(f'<path d="M -10 208 Q 90 188 170 198 Q 250 208 300 192 Q 380 168 470 178 Q 540 186 610 174" fill="none" stroke="#5A5A4A" stroke-width="1" opacity="0.5"/>')
    # the village: tiers of houses stepping down the bowl of the valley to the beach (top rows first)
    # the green ravine behind the houses, lemon terraces striping the slopes
    rav = rough([(-10, 260), (80, 236), (170, 200), (250, 170), (300, 160), (350, 166), (430, 196), (520, 232), (610, 256)], 66, amp=5, depth=3)
    out.append(Q(rav + [(610, 380), (-10, 380)], "#5A763C"))
    out.append(blobs(120, 67, (-10, 170, 610, 330), ["#4A6A34", "#6E8E46", "#3E5A2E"], r=(4, 9), opacity=(0.7, 1), squash=0.7))
    # lemon terraces on the outer slopes: dry-stone walls, dark pergola rows dotted with fruit
    for j in range(8):
        for sx in (-1, 1):
            xa = 300 + sx * (120 + j * 26)
            xb = 300 + sx * 320
            ya = 214 + j * 13
            pts = [(lerp(xa, xb, t), ya + 0.36 * abs(lerp(xa, xb, t) - xa) + 6 * math.sin(t * 3 + j)) for t in [i / 12 for i in range(13)]]
            out.append(f'<polyline points="{P(pts)}" fill="none" stroke="#D8C49A" stroke-width="1.5" opacity="0.9"/>')
            out.append(f'<polyline points="{P([(x, y - 3) for x, y in pts])}" fill="none" stroke="#2E4A26" stroke-width="3.6" stroke-dasharray="6 2.5" opacity="0.9"/>')
            rr = random.Random(j * 7 + sx)
            out.append("".join(f'<circle cx="{x + rr.uniform(-3, 3):.1f}" cy="{y - 3 + rr.uniform(-1, 1):.1f}" r="{rr.uniform(1, 1.6):.1f}" fill="#F6D234"/>' for x, y in pts[1:] if rr.random() < 0.8))
    # the village: houses along V-shaped contours, so the town tumbles from both flanks down to the beach
    rnd = random.Random(77)
    houses = []
    for c in range(16):
        base_c = 368 - c * 12.0
        x = 300 - 300 + rnd.uniform(-8, 8)
        while x < 300 + 300:
            k = rnd.uniform(0.82, 1.04)
            w = rnd.uniform(15, 27) * k
            h = rnd.uniform(11, 17) * k
            dx = abs(x + w / 2 - 300)
            yb = base_c + 0.42 * dx + rnd.uniform(-2, 2)
            top_lim = 172 + 0.5 * dx
            if yb - h > top_lim and yb < 372 - 0.1 * dx and dx < 230 - c * 4:
                houses.append((yb, x, w, h, k, rnd.random()))
            x += w + rnd.uniform(-1, 2)
    houses.sort(key=lambda hh: hh[0])
    hr = random.Random(5)
    for yb, x, w, h, k, r_ in houses:
        if r_ < 0.1:
            out.append(blobs(int(9 * k), int(x * 3 + yb), (x, yb - h * 0.9, x + w, yb + 4), ["#3E6A2E", "#5A8A3A", "#2E5226", "#7AA24A"], r=(2.4 * k, 4.6 * k), opacity=(0.9, 1), squash=0.85))
            if r_ < 0.04:
                out.append(cypress_tree(x + w / 2, yb + 4, 30 * k, int(x), dark="#1E3A24", mid="#2E5230", lit="#7A9A4A", light=-1))
        elif r_ < 0.14:   # a bare rock face between the houses
            rp = rough([(x, yb + 4), (x + w * 0.2, yb - h), (x + w * 0.8, yb - h * 0.8), (x + w, yb + 4)], int(x), amp=2, depth=2)
            out.append(Q(rp, "#B8967A") + streaks(4, int(x), (x, yb - h, x + w, yb), ["#7A5E54", "#E8C8A0"], w=(1, 2), length=(4, 10), opacity=(0.4, 0.7), slant=0.2))
        else:
            if hr.random() < 0.35:  # the rock ledge or retaining wall the house stands on
                out.append(Q([(x - 2, yb + 1), (x + w + 2, yb + 1), (x + w, yb + 10), (x, yb + 12)], hr.choice(["#C8A684", "#B8967A", "#D8C0A0"])))
                out.append(f'<line x1="{x - 1:.1f}" y1="{yb + 2:.1f}" x2="{x + w + 1:.1f}" y2="{yb + 2:.1f}" stroke="#6A5048" stroke-width="1" opacity="0.5"/>')
            out.append(amalfi_house(x, yb, w, h, hr, k))
    out.append(majolica_dome(318, 360, 16, f"{u}-ch"))
    # rocky spurs dropping into the sea on either side of the bay
    for pts, sd in (([(-10, 300), (40, 306), (90, 330), (130, 352), (150, 372), (-10, 380)], 71), ([(610, 296), (560, 310), (510, 336), (474, 360), (460, 374), (610, 380)], 72)):
        rp = rough(pts, sd, amp=6, depth=3)
        out.append(Q(rp, f"url(#{u}-rock)"))
        out.append(f'<clipPath id="{u}-r{sd}"><polygon points="{P(rp)}"/></clipPath>')
        out.append(f'<g clip-path="url(#{u}-r{sd})">' + streaks(40, sd, (min(p[0] for p in pts), 290, max(p[0] for p in pts), 380), ["#6A5450", "#F2D2A8", "#8A7064"], w=(1.5, 4), length=(8, 30), opacity=(0.3, 0.6), slant=0.3)
                   + blobs(30, sd + 1, (min(p[0] for p in pts), 296, max(p[0] for p in pts), 330), ["#4E6A3A", "#6E8A4A"], r=(3, 7), opacity=(0.8, 1), squash=0.7) + "</g>")
    # the beach: dark sand, rows of orange umbrellas, boats pulled up
    out.append(Q([(140, 362), (470, 360), (466, 372), (150, 374)], "#8A7A72"))
    out.append(Q([(140, 362), (470, 360), (470, 363), (140, 365)], "#B8A496"))
    for i in range(14):
        ux = 166 + i * 21
        out.append(f'<line x1="{ux}" y1="364" x2="{ux}" y2="370" stroke="#4A3A3A" stroke-width="1"/><path d="M {ux - 8} 365 Q {ux} 357 {ux + 8} 365 Z" fill="{["#F08A30", "#F6F0E4", "#2E6AA8", "#F08A30"][i % 4]}"/>')
    for bx, c in ((200, "#2E6AA8"), (330, "#E8E4DA"), (420, "#C8463A")):
        out.append(f'<path d="M {bx - 10} 370 L {bx + 10} 370 L {bx + 7} 374 L {bx - 7} 374 Z" fill="{c}"/>')
    # the sea: turquoise over the shallows, deep blue beyond, sun glitter, a wooden boat with its wake
    out.append(Q([(-10, 372), (610, 372), (610, 444), (-10, 444)], f"url(#{u}-sea)"))
    out.append(Q([(130, 372), (480, 372), (520, 384), (100, 384)], "#7AE0D0", ' opacity="0.45"'))
    out.append(water_lines(140, 81, (-10, 375, 610, 444), ["#A8F0E8", "#FFFFFF", "#0E4A6E", "#3ABAC0"], w=(8, 40), h=(0.8, 2.2), opacity=(0.3, 0.75)))
    out.append(water_lines(40, 82, (-10, 376, 200, 444), ["#FFF6D8", "#FFFFFF"], w=(4, 14), h=(0.8, 1.4), opacity=(0.6, 1)))
    # reflections of the rocky spurs
    out.append(Q([(-10, 372), (150, 372), (110, 392), (-10, 396)], "#6A5A60", ' opacity="0.25"'))
    out.append(Q([(460, 372), (610, 372), (610, 394), (490, 390)], "#6A5A60", ' opacity="0.25"'))
    bx, by = 330, 414
    out.append(f'<path d="M {bx - 60} {by + 2} Q {bx - 150} {by + 12} {bx - 260} {by + 26} M {bx - 60} {by + 6} Q {bx - 140} {by + 4} {bx - 240} {by - 2}" fill="none" stroke="#FFFFFF" stroke-width="2.4" opacity="0.6"/>'
               f'<path d="M {bx - 62} {by + 2} Q {bx - 100} {by + 8} {bx - 150} {by + 10}" fill="none" stroke="#E8FFFA" stroke-width="5" opacity="0.4"/>')
    out.append(f'<g transform="translate({bx} {by})">'
               f'<path d="M -64 -2 Q -60 8 -40 9 L 44 9 Q 62 6 70 -8 L 66 -10 Q 0 -6 -64 -6 Z" fill="#F8F4EC"/>'
               f'<path d="M -63 2 Q -58 8 -40 9 L 44 9 Q 60 6 68 -4 Q 0 0 -63 2 Z" fill="#1E5A9A"/>'
               f'<path d="M -64 -6 Q 0 -6 66 -10" fill="none" stroke="#8A5A34" stroke-width="2.4"/>'
               f'<path d="M -64 -2 Q -60 8 -40 9 L 44 9" fill="none" stroke="#FFFFFF" stroke-width="1.2" opacity="0.5"/>'
               f'<line x1="-30" y1="-6" x2="-30" y2="-26" stroke="#8A6A4A" stroke-width="1.6"/><line x1="30" y1="-8" x2="30" y2="-28" stroke="#8A6A4A" stroke-width="1.6"/>'
               f'<path d="M -36 -26 L 36 -29 L 34 -24 L -34 -21 Z" fill="#F6E8C8"/><path d="M -36 -26 L 36 -29 L 36 -27 L -36 -24 Z" fill="#E8463A"/>'
               f'<path d="M -20 -7 L -20 -16 Q -16 -21 -12 -16 L -12 -7 Z" fill="#E8B830"/><circle cx="-16" cy="-19" r="3.4" fill="#C8906A"/>'
               f'<path d="M -4 -7 L -4 -15 Q 0 -20 4 -15 L 4 -7 Z" fill="#E87A9A"/><circle cx="0" cy="-18" r="3.4" fill="#6A3A22"/>'
               f'<path d="M 44 -9 L 44 -18 Q 48 -22 52 -18 L 52 -9 Z" fill="#F6F2EA"/><circle cx="48" cy="-21" r="3.2" fill="#B87E5A"/><rect x="45" y="-25" width="6" height="2" fill="#2E3A5A"/></g>')
    out.append(f'<path d="M {bx - 64} {by + 11} Q {bx} {by + 15} {bx + 70} {by + 9}" fill="none" stroke="#0E3A5E" stroke-width="3" opacity="0.35"/>')
    # a sail far out
    out.append(f'<path d="M 520 392 L 540 392 L 537 395 L 523 395 Z" fill="#F6F2EA"/><path d="M 530 391 L 530 370 L 541 391 Z" fill="#FFFFFF"/><path d="M 529 391 L 529 374 L 521 391 Z" fill="#E8E4DA"/>')
    # a lemon bough reaching in from the top right: glossy leaves, ripe lemons, a blossom
    br = [(640, 30), (590, 62), (540, 86), (500, 98), (470, 118)]
    out.append(f'<path d="M {P(br).replace(" ", " L ")}" fill="none" stroke="#5A4434" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<path d="M 560 76 Q 548 100 540 122" fill="none" stroke="#5A4434" stroke-width="3" stroke-linecap="round"/><path d="M 515 94 Q 512 110 506 128" fill="none" stroke="#5A4434" stroke-width="2.5" stroke-linecap="round"/>')
    lv = [(600, 58, 34, 160), (588, 60, 30, 210), (570, 72, 36, 120), (556, 80, 30, 230), (548, 82, 34, 95), (530, 92, 30, 200), (520, 92, 34, 140),
          (500, 100, 30, 230), (486, 108, 32, 160), (476, 116, 28, 200), (470, 118, 30, 120), (610, 44, 30, 120), (575, 66, 30, 300), (535, 88, 28, 320),
          (495, 102, 26, 300), (620, 48, 34, 200)]
    for x, y, L, a in lv:
        out.append(leaf(x, y, L, a))
    out.append(lemon(538, 140, 21, 16, 80, 1))
    out.append(lemon(503, 146, 18, 14, 96, 2))
    out.append(lemon(574, 124, 17, 13, 70, 3))
    for x, y, L, a in ((546, 118, 24, 40), (510, 126, 22, 150)):
        out.append(leaf(x, y, L, a))
    fx, fy = 492, 118
    out.append("".join(f'<ellipse cx="{fx + 4 * math.cos(i * 1.257):.1f}" cy="{fy + 4 * math.sin(i * 1.257):.1f}" rx="3.2" ry="2.2" transform="rotate({i * 72} {fx + 4 * math.cos(i * 1.257):.1f} {fy + 4 * math.sin(i * 1.257):.1f})" fill="#FFFFFF"/>' for i in range(5))
               + f'<circle cx="{fx}" cy="{fy}" r="1.8" fill="#F2C84A"/>')
    out.append(gulls([(150, 120, 10), (172, 132, 7), (360, 200, 8)], "#3A4A6A", 1.8))
    return "\n".join(out)


BUILD = {
    "lisbon": (lisbon, "LISBON", "PORTUGAL · LISBOA", "#173B6C", "#F6C028", "#FFF6E2", "#F6C028"),
    "porto": (porto, "PORTO", "PORTUGAL · DOURO RIVER", "#4A1630", "#F2B868", "#FCEBD5", "#F2B868"),
    "amsterdam": (amsterdam, "AMSTERDAM", "NETHERLANDS · EUROPE", "#1F3B33", "#E8483A", "#FFF4E2", "#F2C24A"),
    "barcelona": (barcelona, "BARCELONA", "SPAIN · CATALONIA", "#86291E", "#F4B83A", "#FFF4E2", "#F6C65A"),
    "florence": (florence, "FLORENCE", "ITALY · TOSCANA", "#3A1E3A", "#F29A5A", "#FFEBD6", "#F6B27A"),
    "pisa": (pisa, "PISA", "ITALY · TOSCANA", "#245A38", "#F2D25A", "#FFF8EA", "#F2D25A"),
    "amalfi-coast": (amalfi, "AMALFI COAST", "ITALY · CAMPANIA", "#0E4E66", "#F2D23A", "#FFF8E6", "#F6DA5A"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("world", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
