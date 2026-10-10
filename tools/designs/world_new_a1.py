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
            out.append(porto_house(x, yb, w, h, k, rnd, lit_p=0.42))
            if rnd.random() < 0.08:
                out.append(blobs(int(8 * k), ri * 300 + int(x), (x, yb - h * 0.5, x + w, yb), ["#2E3A3A", "#3E4A44"], r=(2 * k, 4 * k), opacity=(0.9, 1), squash=1))
            x += w + rnd.uniform(-0.5, 1.5) * k
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


BUILD = {
    "lisbon": (lisbon, "LISBON", "PORTUGAL · LISBOA", "#173B6C", "#F6C028", "#FFF6E2", "#F6C028"),
    "porto": (porto, "PORTO", "PORTUGAL · DOURO RIVER", "#4A1630", "#F2B868", "#FCEBD5", "#F2B868"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("world", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
