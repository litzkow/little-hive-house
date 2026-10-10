"""Detailed illustration pieces with light and shade, shared by the seasonal and phrase collections."""
import math

from common import heart, star_points


def P(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def rot_pt(x, y, cx, cy, deg):
    a = math.radians(deg)
    dx, dy = x - cx, y - cy
    return cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a)


# ---------------------------------------------------------------- autumn
MAPLE = [(0, -1.0), (0.12, -0.62), (0.32, -0.74), (0.28, -0.40), (0.62, -0.60), (0.56, -0.30), (0.96, -0.32),
         (0.78, -0.08), (0.92, 0.06), (0.50, 0.22), (0.56, 0.42), (0.18, 0.32), (0.05, 0.46)]


def maple(cx, cy, s, fill, vein="#FFFFFF", rot=0, shade=None, stem=None):
    pts = MAPLE + [(-x, y) for x, y in reversed(MAPLE[1:])]
    poly = P([(cx + x * s, cy + y * s) for x, y in pts])
    right = [(0, -1.0)] + MAPLE[1:] + [(0, 0.46)]
    out = [f'<g transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})">', f'<polygon points="{poly}" fill="{fill}"/>']
    if shade:
        out.append(f'<polygon points="{P([(cx + x * s, cy + y * s) for x, y in right])}" fill="{shade}"/>')
    base = (cx, cy + 0.38 * s)
    for tx, ty in ((0, -0.86), (0.82, -0.28), (-0.82, -0.28), (0.5, 0.18), (-0.5, 0.18)):
        out.append(f'<line x1="{base[0]:.1f}" y1="{base[1]:.1f}" x2="{cx + tx * s:.1f}" y2="{cy + ty * s:.1f}" stroke="{vein}" stroke-width="{max(1.2, s * 0.03):.1f}" stroke-linecap="round" opacity="0.75"/>')
    out.append(f'<path d="M {cx:.1f} {cy + 0.38 * s:.1f} Q {cx + 0.04 * s:.1f} {cy + 0.7 * s:.1f} {cx - 0.06 * s:.1f} {cy + 1.0 * s:.1f}" fill="none" stroke="{stem or fill}" stroke-width="{max(2, s * 0.06):.1f}" stroke-linecap="round"/>')
    out.append("</g>")
    return "".join(out)


def oak_leaf(cx, cy, s, fill, vein="#FFFFFF", rot=0):
    pts = []
    for i in range(0, 361, 6):
        a = math.radians(i)
        wob = 1 + 0.18 * math.sin(a * 6) if 20 < i < 340 else 1
        pts.append((cx + 0.42 * s * math.sin(a) * wob, cy - s * math.cos(a) * (0.9 if i < 180 else 0.9)))
    return (f'<g transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})"><polygon points="{P(pts)}" fill="{fill}"/>'
            f'<line x1="{cx:.1f}" y1="{cy + 0.9 * s:.1f}" x2="{cx:.1f}" y2="{cy - 0.8 * s:.1f}" stroke="{vein}" stroke-width="{max(1.2, s * 0.035):.1f}" opacity="0.75"/>'
            f'<line x1="{cx:.1f}" y1="{cy + 0.9 * s:.1f}" x2="{cx:.1f}" y2="{cy + 1.15 * s:.1f}" stroke="{fill}" stroke-width="{max(2, s * 0.06):.1f}" stroke-linecap="round"/></g>')


def acorn(cx, cy, s, nut, cap, rot=0):
    return (f'<g transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})">'
            f'<ellipse cx="{cx:.1f}" cy="{cy + 0.25 * s:.1f}" rx="{0.42 * s:.1f}" ry="{0.55 * s:.1f}" fill="{nut}"/>'
            f'<path d="M {cx - 0.5 * s:.1f} {cy:.1f} Q {cx:.1f} {cy - 0.62 * s:.1f} {cx + 0.5 * s:.1f} {cy:.1f} Q {cx:.1f} {cy + 0.12 * s:.1f} {cx - 0.5 * s:.1f} {cy:.1f} Z" fill="{cap}"/>'
            f'<line x1="{cx:.1f}" y1="{cy - 0.3 * s:.1f}" x2="{cx + 0.08 * s:.1f}" y2="{cy - 0.55 * s:.1f}" stroke="{cap}" stroke-width="{0.1 * s:.1f}" stroke-linecap="round"/>'
            f'<ellipse cx="{cx - 0.16 * s:.1f}" cy="{cy + 0.25 * s:.1f}" rx="{0.08 * s:.1f}" ry="{0.22 * s:.1f}" fill="#FFFFFF" opacity="0.25"/></g>')


def pumpkin(cx, cy, w, h, base="#E37B33", dark="#C45F22", light="#F4A15C", stem="#6B5A2E", leaf="#5E7A3A", face=None, glow="#FFD25E"):
    out = [f'<path d="M {cx + 0.04 * w:.1f} {cy - 0.42 * h:.1f} Q {cx + 0.02 * w:.1f} {cy - 0.62 * h:.1f} {cx + 0.12 * w:.1f} {cy - 0.7 * h:.1f}" '
           f'fill="none" stroke="{stem}" stroke-width="{0.09 * w:.1f}" stroke-linecap="round"/>']
    out.append(f'<path d="M {cx + 0.08 * w:.1f} {cy - 0.48 * h:.1f} Q {cx + 0.36 * w:.1f} {cy - 0.78 * h:.1f} {cx + 0.44 * w:.1f} {cy - 0.52 * h:.1f} '
               f'Q {cx + 0.24 * w:.1f} {cy - 0.42 * h:.1f} {cx + 0.08 * w:.1f} {cy - 0.48 * h:.1f} Z" fill="{leaf}"/>')
    out.append(f'<path d="M {cx - 0.04 * w:.1f} {cy - 0.5 * h:.1f} q {-0.14 * w:.1f} {-0.02 * h:.1f} {-0.16 * w:.1f} {-0.14 * h:.1f} '
               f'q {0.0:.1f} {-0.1 * h:.1f} {0.08 * w:.1f} {-0.08 * h:.1f} q {0.06 * w:.1f} {0.04 * h:.1f} {0.0:.1f} {0.08 * h:.1f}" fill="none" stroke="{leaf}" stroke-width="{max(1.5, 0.018 * w):.1f}" stroke-linecap="round"/>')
    lobes = [(-0.33, 0.27, 0.44, dark), (0.33, 0.27, 0.44, dark), (-0.17, 0.27, 0.49, base), (0.17, 0.27, 0.49, base), (0, 0.24, 0.51, base)]
    for dx, rx, ry, col in lobes:
        out.append(f'<ellipse cx="{cx + dx * w:.1f}" cy="{cy:.1f}" rx="{rx * w:.1f}" ry="{ry * h:.1f}" fill="{col}"/>')
    for dx in (-0.25, 0.25, -0.09, 0.09):
        out.append(f'<path d="M {cx + dx * w:.1f} {cy - 0.42 * h:.1f} Q {cx + dx * 1.35 * w:.1f} {cy:.1f} {cx + dx * w:.1f} {cy + 0.45 * h:.1f}" fill="none" stroke="{dark}" stroke-width="{max(1.5, 0.02 * w):.1f}" opacity="0.55"/>')
    out.append(f'<path d="M {cx - 0.16 * w:.1f} {cy - 0.28 * h:.1f} Q {cx - 0.24 * w:.1f} {cy - 0.05 * h:.1f} {cx - 0.18 * w:.1f} {cy + 0.2 * h:.1f}" fill="none" stroke="{light}" stroke-width="{max(2, 0.035 * w):.1f}" stroke-linecap="round"/>')
    if face:
        k = w / 200
        out.append(f'<g fill="{face}">'
                   f'<polygon points="{P([(cx - 52 * k, cy - 6 * k), (cx - 18 * k, cy - 6 * k), (cx - 35 * k, cy - 38 * k)])}"/>'
                   f'<polygon points="{P([(cx + 52 * k, cy - 6 * k), (cx + 18 * k, cy - 6 * k), (cx + 35 * k, cy - 38 * k)])}"/>'
                   f'<polygon points="{P([(cx - 8 * k, cy + 10 * k), (cx + 8 * k, cy + 10 * k), (cx, cy - 2 * k)])}"/>'
                   f'<path d="M {cx - 62 * k:.1f} {cy + 22 * k:.1f} Q {cx:.1f} {cy + 80 * k:.1f} {cx + 62 * k:.1f} {cy + 22 * k:.1f} L {cx + 44 * k:.1f} {cy + 34 * k:.1f} L {cx + 30 * k:.1f} {cy + 24 * k:.1f} '
                   f'L {cx + 14 * k:.1f} {cy + 38 * k:.1f} L {cx - 2 * k:.1f} {cy + 28 * k:.1f} L {cx - 18 * k:.1f} {cy + 40 * k:.1f} L {cx - 32 * k:.1f} {cy + 26 * k:.1f} L {cx - 46 * k:.1f} {cy + 36 * k:.1f} Z"/></g>')
    return "".join(out)


def wheat(x, y_bottom, y_top, ink, sw=4, lean=0):
    tx = x + lean
    out = [f'<path d="M {x} {y_bottom} Q {x + lean * 0.3:.1f} {(y_bottom + y_top) / 2:.1f} {tx:.1f} {y_top + 20}" fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linecap="round"/>']
    for i in range(6):
        yy = y_top + 14 + i * 15
        xx = tx - lean * i / 30
        for side in (-1, 1):
            out.append(f'<ellipse cx="{xx + side * 8:.1f}" cy="{yy}" rx="5.5" ry="11" transform="rotate({side * 30} {xx + side * 8:.1f} {yy})" fill="{ink}"/>')
            out.append(f'<line x1="{xx + side * 12:.1f}" y1="{yy - 8}" x2="{xx + side * 22:.1f}" y2="{yy - 26}" stroke="{ink}" stroke-width="1.4" opacity="0.8"/>')
    out.append(f'<ellipse cx="{tx:.1f}" cy="{y_top}" rx="5" ry="12" fill="{ink}"/>')
    return "".join(out)


def mug(cx, top, body, ink, sw=5, steam=True, band=None, band2=None, heart_fill=None, coffee="#5A3A22", w=150, h=118):
    l, r, b = cx - w / 2, cx + w / 2, top + h
    out = [f'<path d="M {r - 4} {top + 22} Q {r + 44} {top + 22} {r + 40} {top + 56} Q {r + 36} {top + 88} {r - 10} {top + 88}" fill="none" stroke="{ink}" stroke-width="{sw + 9}" stroke-linecap="round"/>',
           f'<path d="M {r - 4} {top + 22} Q {r + 44} {top + 22} {r + 40} {top + 56} Q {r + 36} {top + 88} {r - 10} {top + 88}" fill="none" stroke="{body}" stroke-width="{sw + 1}" stroke-linecap="round"/>',
           f'<path d="M {l} {top} L {r} {top} L {r - 12} {b - 14} Q {r - 16} {b} {r - 34} {b} L {l + 34} {b} Q {l + 16} {b} {l + 12} {b - 14} Z" fill="{body}" stroke="{ink}" stroke-width="{sw}" stroke-linejoin="round"/>']
    if band:
        out.append(f'<clipPath id="mugclip{int(cx)}{int(top)}"><path d="M {l} {top} L {r} {top} L {r - 12} {b - 14} Q {r - 16} {b} {r - 34} {b} L {l + 34} {b} Q {l + 16} {b} {l + 12} {b - 14} Z"/></clipPath>')
        g = [f'<rect x="{l}" y="{top + 38}" width="{w}" height="34" fill="{band}"/>']
        if band2:
            g += [f'<polygon points="{P([(x, top + 55), (x + 9, top + 44), (x + 18, top + 55), (x + 9, top + 66)])}" fill="{band2}"/>' for x in range(int(l) + 4, int(r), 22)]
        out.append(f'<g clip-path="url(#mugclip{int(cx)}{int(top)})">' + "".join(g) + "</g>")
        out.append(f'<path d="M {l} {top} L {r} {top} L {r - 12} {b - 14} Q {r - 16} {b} {r - 34} {b} L {l + 34} {b} Q {l + 16} {b} {l + 12} {b - 14} Z" fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linejoin="round"/>')
    out.append(f'<ellipse cx="{cx}" cy="{top + 1}" rx="{w / 2 - 3}" ry="9" fill="{coffee}" stroke="{ink}" stroke-width="{sw * 0.7:.1f}"/>')
    out.append(f'<path d="M {l + 22} {top + 22} L {l + 30} {b - 22}" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" opacity="0.35"/>')
    if heart_fill:
        out.append(heart(cx - 4, top + 58, 18, heart_fill))
    if steam:
        out.append(f'<g fill="none" stroke="{ink}" stroke-width="{sw - 1}" stroke-linecap="round">'
                   + "".join(f'<path d="M {cx + dx} {top - 18} q -10 -12 0 -24 t 0 -24"/>' for dx in (-28, 2, 32)) + "</g>")
    return "".join(out)


def cinnamon(x1, y1, x2, y2, col="#8A4B2A", dark="#6B3820"):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="16" stroke-linecap="round"/>'
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{dark}" stroke-width="4" stroke-linecap="round" opacity="0.6"/>')


def star_anise(cx, cy, r, col="#7A3E22", seed="#E9B949"):
    out = []
    for i in range(8):
        a = i * 45
        x, y = rot_pt(cx, cy - r * 0.6, cx, cy, a)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 0.22:.1f}" ry="{r * 0.45:.1f}" transform="rotate({a} {x:.1f} {y:.1f})" fill="{col}"/>')
        sx, sy = rot_pt(cx, cy - r * 0.55, cx, cy, a)
        out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r * 0.07:.1f}" fill="{seed}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.16:.1f}" fill="{col}"/>')
    return "".join(out)


# ---------------------------------------------------------------- halloween
def ghost(cx, top, w, body="#F6EFE0", shade="#E2D8C6", eye="#151515", blush="#F2A6B4", arms=True):
    k = w / 128
    l, r = cx - 64 * k, cx + 64 * k
    bottom = top + 190 * k
    wav = "".join(f" q {-10.7 * k:.1f} {18 * k:.1f} {-21.3 * k:.1f} 0" for _ in range(6))
    d = f"M {l:.1f} {bottom:.1f} L {l:.1f} {top + 72 * k:.1f} Q {l:.1f} {top:.1f} {cx:.1f} {top:.1f} Q {r:.1f} {top:.1f} {r:.1f} {top + 72 * k:.1f} L {r:.1f} {bottom:.1f}{wav} Z"
    out = [f'<path d="{d}" fill="{body}"/>',
           f'<path d="M {cx + 24 * k:.1f} {top + 6 * k:.1f} Q {r:.1f} {top + 10 * k:.1f} {r:.1f} {top + 72 * k:.1f} L {r:.1f} {bottom:.1f} q {-10.7 * k:.1f} {18 * k:.1f} {-21.3 * k:.1f} 0 L {cx + 40 * k:.1f} {top + 80 * k:.1f} Q {cx + 40 * k:.1f} {top + 28 * k:.1f} {cx + 24 * k:.1f} {top + 6 * k:.1f} Z" fill="{shade}"/>']
    if arms:
        out.append(f'<path d="M {l + 2 * k:.1f} {top + 96 * k:.1f} Q {l - 26 * k:.1f} {top + 104 * k:.1f} {l - 20 * k:.1f} {top + 126 * k:.1f} Q {l - 6 * k:.1f} {top + 118 * k:.1f} {l + 2 * k:.1f} {top + 116 * k:.1f} Z" fill="{body}"/>')
        out.append(f'<path d="M {r - 2 * k:.1f} {top + 96 * k:.1f} Q {r + 26 * k:.1f} {top + 88 * k:.1f} {r + 24 * k:.1f} {top + 66 * k:.1f} Q {r + 8 * k:.1f} {top + 74 * k:.1f} {r - 2 * k:.1f} {top + 80 * k:.1f} Z" fill="{shade}"/>')
    out.append(f'<ellipse cx="{cx - 22 * k:.1f}" cy="{top + 70 * k:.1f}" rx="{9 * k:.1f}" ry="{14 * k:.1f}" fill="{eye}"/>')
    out.append(f'<ellipse cx="{cx + 22 * k:.1f}" cy="{top + 70 * k:.1f}" rx="{9 * k:.1f}" ry="{14 * k:.1f}" fill="{eye}"/>')
    out.append(f'<circle cx="{cx - 19 * k:.1f}" cy="{top + 65 * k:.1f}" r="{3 * k:.1f}" fill="{body}"/><circle cx="{cx + 25 * k:.1f}" cy="{top + 65 * k:.1f}" r="{3 * k:.1f}" fill="{body}"/>')
    out.append(f'<ellipse cx="{cx:.1f}" cy="{top + 106 * k:.1f}" rx="{9 * k:.1f}" ry="{12 * k:.1f}" fill="{eye}"/>')
    out.append(f'<ellipse cx="{cx - 40 * k:.1f}" cy="{top + 92 * k:.1f}" rx="{9 * k:.1f}" ry="{5 * k:.1f}" fill="{blush}" opacity="0.8"/>'
               f'<ellipse cx="{cx + 40 * k:.1f}" cy="{top + 92 * k:.1f}" rx="{9 * k:.1f}" ry="{5 * k:.1f}" fill="{blush}" opacity="0.8"/>')
    return "".join(out)


def bat(cx, cy, s, fill, eyes=None):
    k = s / 50
    d = (f"M {cx} {cy - 6 * k:.1f} L {cx - 6 * k:.1f} {cy - 15 * k:.1f} L {cx - 9 * k:.1f} {cy - 4 * k:.1f} "
         f"Q {cx - 24 * k:.1f} {cy - 22 * k:.1f} {cx - 50 * k:.1f} {cy - 12 * k:.1f} Q {cx - 38 * k:.1f} {cy - 2 * k:.1f} {cx - 40 * k:.1f} {cy + 10 * k:.1f} "
         f"Q {cx - 28 * k:.1f} {cy:.1f} {cx - 22 * k:.1f} {cy + 12 * k:.1f} Q {cx - 12 * k:.1f} {cy + 2 * k:.1f} {cx} {cy + 14 * k:.1f} "
         f"Q {cx + 12 * k:.1f} {cy + 2 * k:.1f} {cx + 22 * k:.1f} {cy + 12 * k:.1f} Q {cx + 28 * k:.1f} {cy:.1f} {cx + 40 * k:.1f} {cy + 10 * k:.1f} "
         f"Q {cx + 38 * k:.1f} {cy - 2 * k:.1f} {cx + 50 * k:.1f} {cy - 12 * k:.1f} Q {cx + 24 * k:.1f} {cy - 22 * k:.1f} {cx + 9 * k:.1f} {cy - 4 * k:.1f} "
         f"L {cx + 6 * k:.1f} {cy - 15 * k:.1f} Z")
    e = ""
    if eyes:
        e = f'<circle cx="{cx - 3.5 * k:.1f}" cy="{cy - 1 * k:.1f}" r="{1.8 * k:.1f}" fill="{eyes}"/><circle cx="{cx + 3.5 * k:.1f}" cy="{cy - 1 * k:.1f}" r="{1.8 * k:.1f}" fill="{eyes}"/>'
    return f'<path d="{d}" fill="{fill}"/>{e}'


def crescent(cx, cy, r, fill, bg, crater=None):
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>']
    if crater:
        out += [f'<circle cx="{cx - r * 0.45:.1f}" cy="{cy + r * 0.2:.1f}" r="{r * 0.14:.1f}" fill="{crater}"/>',
                f'<circle cx="{cx - r * 0.2:.1f}" cy="{cy + r * 0.55:.1f}" r="{r * 0.09:.1f}" fill="{crater}"/>',
                f'<circle cx="{cx - r * 0.6:.1f}" cy="{cy - r * 0.25:.1f}" r="{r * 0.08:.1f}" fill="{crater}"/>']
    out.append(f'<circle cx="{cx + r * 0.42:.1f}" cy="{cy - r * 0.22:.1f}" r="{r * 0.86:.1f}" fill="{bg}"/>')
    return "".join(out)


def cat(cx, base, s, fill, eye="#F3D27A", tail=True):
    k = s / 100
    out = [f'<g fill="{fill}">',
           f'<path d="M {cx - 48 * k:.1f} {base:.1f} Q {cx - 60 * k:.1f} {base - 92 * k:.1f} {cx - 22 * k:.1f} {base - 122 * k:.1f} L {cx + 22 * k:.1f} {base - 122 * k:.1f} Q {cx + 60 * k:.1f} {base - 92 * k:.1f} {cx + 48 * k:.1f} {base:.1f} Z"/>',
           f'<ellipse cx="{cx:.1f}" cy="{base - 142 * k:.1f}" rx="{40 * k:.1f}" ry="{34 * k:.1f}"/>',
           f'<polygon points="{P([(cx - 36 * k, base - 154 * k), (cx - 34 * k, base - 200 * k), (cx - 8 * k, base - 172 * k)])}"/>',
           f'<polygon points="{P([(cx + 36 * k, base - 154 * k), (cx + 34 * k, base - 200 * k), (cx + 8 * k, base - 172 * k)])}"/></g>']
    if tail:
        out.append(f'<path d="M {cx + 40 * k:.1f} {base - 8 * k:.1f} Q {cx + 116 * k:.1f} {base - 6 * k:.1f} {cx + 100 * k:.1f} {base - 84 * k:.1f} Q {cx + 94 * k:.1f} {base - 104 * k:.1f} {cx + 110 * k:.1f} {base - 110 * k:.1f}" fill="none" stroke="{fill}" stroke-width="{14 * k:.1f}" stroke-linecap="round"/>')
    out.append(f'<g fill="{eye}"><ellipse cx="{cx - 15 * k:.1f}" cy="{base - 146 * k:.1f}" rx="{8 * k:.1f}" ry="{10 * k:.1f}"/><ellipse cx="{cx + 15 * k:.1f}" cy="{base - 146 * k:.1f}" rx="{8 * k:.1f}" ry="{10 * k:.1f}"/></g>')
    out.append(f'<g fill="{fill}"><ellipse cx="{cx - 15 * k:.1f}" cy="{base - 146 * k:.1f}" rx="{2.6 * k:.1f}" ry="{8 * k:.1f}"/><ellipse cx="{cx + 15 * k:.1f}" cy="{base - 146 * k:.1f}" rx="{2.6 * k:.1f}" ry="{8 * k:.1f}"/></g>')
    out.append(f'<polygon points="{P([(cx - 5 * k, base - 132 * k), (cx + 5 * k, base - 132 * k), (cx, base - 126 * k)])}" fill="#F2A6B4"/>')
    return "".join(out)


def witch_hat(cx, base, s, hat="#151515", band="#5B3A7A", buckle="#E9B949", brim_shade="#2A2A2A"):
    k = s / 100
    return (f'<ellipse cx="{cx:.1f}" cy="{base:.1f}" rx="{150 * k:.1f}" ry="{26 * k:.1f}" fill="{hat}"/>'
            f'<ellipse cx="{cx:.1f}" cy="{base + 4 * k:.1f}" rx="{120 * k:.1f}" ry="{14 * k:.1f}" fill="{brim_shade}"/>'
            f'<path d="M {cx - 82 * k:.1f} {base - 4 * k:.1f} L {cx - 6 * k:.1f} {base - 170 * k:.1f} Q {cx + 30 * k:.1f} {base - 200 * k:.1f} {cx + 58 * k:.1f} {base - 162 * k:.1f} '
            f'Q {cx + 30 * k:.1f} {base - 172 * k:.1f} {cx + 22 * k:.1f} {base - 148 * k:.1f} L {cx + 82 * k:.1f} {base - 4 * k:.1f} Z" fill="{hat}"/>'
            f'<path d="M {cx - 76 * k:.1f} {base - 18 * k:.1f} L {cx + 78 * k:.1f} {base - 18 * k:.1f} L {cx + 70 * k:.1f} {base - 46 * k:.1f} L {cx - 66 * k:.1f} {base - 46 * k:.1f} Z" fill="{band}"/>'
            f'<rect x="{cx - 14 * k:.1f}" y="{base - 48 * k:.1f}" width="{28 * k:.1f}" height="{32 * k:.1f}" fill="none" stroke="{buckle}" stroke-width="{5 * k:.1f}"/>'
            f'<path d="M {cx - 40 * k:.1f} {base - 60 * k:.1f} L {cx - 10 * k:.1f} {base - 150 * k:.1f}" stroke="#FFFFFF" stroke-width="{5 * k:.1f}" stroke-linecap="round" opacity="0.15"/>')


def candy_corn(cx, cy, s, rot=0):
    k = s / 40
    tri = f"M {cx} {cy - 30 * k:.1f} Q {cx + 6 * k:.1f} {cy - 30 * k:.1f} {cx + 22 * k:.1f} {cy + 14 * k:.1f} Q {cx + 24 * k:.1f} {cy + 24 * k:.1f} {cx} {cy + 24 * k:.1f} Q {cx - 24 * k:.1f} {cy + 24 * k:.1f} {cx - 22 * k:.1f} {cy + 14 * k:.1f} Q {cx - 6 * k:.1f} {cy - 30 * k:.1f} {cx} {cy - 30 * k:.1f} Z"
    cid = f"cc{int(cx)}{int(cy)}"
    return (f'<g transform="rotate({rot:.1f} {cx} {cy})"><clipPath id="{cid}"><path d="{tri}"/></clipPath>'
            f'<g clip-path="url(#{cid})"><rect x="{cx - 30 * k:.1f}" y="{cy - 32 * k:.1f}" width="{60 * k:.1f}" height="{60 * k:.1f}" fill="#FBF3E2"/>'
            f'<rect x="{cx - 30 * k:.1f}" y="{cy - 14 * k:.1f}" width="{60 * k:.1f}" height="{20 * k:.1f}" fill="#F08A2C"/>'
            f'<rect x="{cx - 30 * k:.1f}" y="{cy + 6 * k:.1f}" width="{60 * k:.1f}" height="{20 * k:.1f}" fill="#F7C531"/></g></g>')


def wrapped_candy(cx, cy, s, body, stripe, rot=0):
    k = s / 60
    return (f'<g transform="rotate({rot:.1f} {cx} {cy})"><polygon points="{P([(cx - 28 * k, cy), (cx - 54 * k, cy - 20 * k), (cx - 50 * k, cy), (cx - 54 * k, cy + 20 * k)])}" fill="{body}"/>'
            f'<polygon points="{P([(cx + 28 * k, cy), (cx + 54 * k, cy - 20 * k), (cx + 50 * k, cy), (cx + 54 * k, cy + 20 * k)])}" fill="{body}"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{34 * k:.1f}" ry="{24 * k:.1f}" fill="{body}"/>'
            f'<path d="M {cx - 16 * k:.1f} {cy - 20 * k:.1f} Q {cx:.1f} {cy:.1f} {cx - 10 * k:.1f} {cy + 22 * k:.1f}" fill="none" stroke="{stripe}" stroke-width="{6 * k:.1f}"/>'
            f'<path d="M {cx + 8 * k:.1f} {cy - 23 * k:.1f} Q {cx + 24 * k:.1f} {cy:.1f} {cx + 12 * k:.1f} {cy + 23 * k:.1f}" fill="none" stroke="{stripe}" stroke-width="{6 * k:.1f}"/></g>')


def web_corner(color, size=260, sw=2):
    out = []
    for i in range(7):
        a = math.radians(i * 15)
        out.append(f'<line x1="0" y1="0" x2="{size * math.cos(a):.1f}" y2="{size * math.sin(a):.1f}"/>')
    for r in (50, 95, 140, 185, 230):
        pts = [(r * math.cos(math.radians(i * 15)), r * math.sin(math.radians(i * 15))) for i in range(7)]
        d = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}" + "".join(
            f" Q {(pts[j - 1][0] + pts[j][0]) / 2 * 0.9:.1f} {(pts[j - 1][1] + pts[j][1]) / 2 * 0.9:.1f} {pts[j][0]:.1f} {pts[j][1]:.1f}" for j in range(1, 7))
        out.append(f'<path d="{d}" fill="none"/>')
    return f'<g stroke="{color}" stroke-width="{sw}">' + "".join(out) + "</g>"


def spider(cx, cy, s, body, line):
    k = s / 20
    legs = "".join(f'<path d="M {cx + side * 6 * k:.1f} {cy + dy * k:.1f} q {side * 10 * k:.1f} {-8 * k:.1f} {side * 16 * k:.1f} {(dy + 2) * k:.1f}" fill="none" stroke="{body}" stroke-width="{2.4 * k:.1f}" stroke-linecap="round"/>'
                   for side in (-1, 1) for dy in (-6, -1, 4, 9))
    return (legs + f'<ellipse cx="{cx}" cy="{cy + 2 * k:.1f}" rx="{9 * k:.1f}" ry="{11 * k:.1f}" fill="{body}"/><circle cx="{cx}" cy="{cy - 10 * k:.1f}" r="{6 * k:.1f}" fill="{body}"/>'
            f'<circle cx="{cx - 2.5 * k:.1f}" cy="{cy - 11 * k:.1f}" r="{1.6 * k:.1f}" fill="#FFFFFF"/><circle cx="{cx + 2.5 * k:.1f}" cy="{cy - 11 * k:.1f}" r="{1.6 * k:.1f}" fill="#FFFFFF"/>')


# ---------------------------------------------------------------- christmas
def ornament(cx, cy, r, body, pattern, cap="#E9B949", hook=None, kind="stripe"):
    cid = f"orn{int(cx)}{int(cy)}"
    pat = ""
    if kind == "stripe":
        pat = f'<rect x="{cx - r}" y="{cy - r * 0.2:.1f}" width="{2 * r}" height="{r * 0.4:.1f}" fill="{pattern}"/>' + \
              "".join(f'<circle cx="{cx + dx * r:.1f}" cy="{cy:.1f}" r="{r * 0.08:.1f}" fill="{body}"/>' for dx in (-0.6, -0.2, 0.2, 0.6))
    elif kind == "zig":
        pts = [(cx - r + i * r / 4, cy + (r * 0.18 if i % 2 else -r * 0.18)) for i in range(9)]
        pat = f'<polyline points="{P(pts)}" fill="none" stroke="{pattern}" stroke-width="{r * 0.16:.1f}" stroke-linejoin="round"/>'
    elif kind == "dots":
        pat = "".join(f'<circle cx="{cx + dx * r:.1f}" cy="{cy + dy * r:.1f}" r="{r * 0.12:.1f}" fill="{pattern}"/>'
                      for dx, dy in ((-0.5, -0.4), (0.1, -0.55), (0.55, -0.2), (-0.2, 0.05), (0.35, 0.35), (-0.55, 0.35), (0.05, 0.6)))
    out = []
    if hook:
        out.append(f'<line x1="{cx}" y1="{hook}" x2="{cx}" y2="{cy - r - 10:.1f}" stroke="{cap}" stroke-width="2"/>')
    out += [f'<rect x="{cx - r * 0.26:.1f}" y="{cy - r - 12:.1f}" width="{r * 0.52:.1f}" height="14" rx="3" fill="{cap}"/>',
            f'<clipPath id="{cid}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>',
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{body}"/>',
            f'<g clip-path="url(#{cid})">{pat}<circle cx="{cx + r * 0.35:.1f}" cy="{cy + r * 0.35:.1f}" r="{r}" fill="#000000" opacity="0.12"/></g>',
            f'<path d="M {cx - r * 0.55:.1f} {cy - r * 0.35:.1f} Q {cx - r * 0.45:.1f} {cy - r * 0.62:.1f} {cx - r * 0.15:.1f} {cy - r * 0.7:.1f}" fill="none" stroke="#FFFFFF" stroke-width="{max(2, r * 0.1):.1f}" stroke-linecap="round" opacity="0.6"/>']
    return "".join(out)


def snowflake(cx, cy, r, ink, sw=3):
    out = []
    for i in range(6):
        a = math.radians(i * 60 - 90)
        x2, y2 = cx + r * math.cos(a), cy + r * math.sin(a)
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
        for f, L in ((0.45, 0.28), (0.72, 0.2)):
            mx, my = cx + f * r * math.cos(a), cy + f * r * math.sin(a)
            for d in (-45, 45):
                b = a + math.radians(d)
                out.append(f'<line x1="{mx:.1f}" y1="{my:.1f}" x2="{mx + L * r * math.cos(b):.1f}" y2="{my + L * r * math.sin(b):.1f}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{max(2, r * 0.08):.1f}" fill="{ink}"/>')
    return f'<g stroke="{ink}" stroke-width="{sw}" stroke-linecap="round">' + "".join(out) + "</g>"


def xmas_tree(cx, top, s, green="#2F7A57", dark="#24604A", trunk="#6B4A2E", star="#E9B949", balls=("#C2343A", "#E9B949", "#F6EFE0"), garland="#E9B949", gifts=True):
    k = s / 100
    tiers = [(top + 34 * k, 50 * k, 64 * k), (top + 82 * k, 74 * k, 74 * k), (top + 136 * k, 98 * k, 82 * k)]
    out = [f'<rect x="{cx - 13 * k:.1f}" y="{top + 196 * k:.1f}" width="{26 * k:.1f}" height="{28 * k:.1f}" fill="{trunk}"/>']
    for y, hw, h in reversed(tiers):
        out.append(f'<path d="M {cx:.1f} {y - h * 0.42:.1f} L {cx + hw:.1f} {y + h * 0.72:.1f} Q {cx:.1f} {y + h * 0.86:.1f} {cx - hw:.1f} {y + h * 0.72:.1f} Z" fill="{green}"/>')
        out.append(f'<path d="M {cx:.1f} {y - h * 0.42:.1f} L {cx + hw:.1f} {y + h * 0.72:.1f} Q {cx + hw * 0.5:.1f} {y + h * 0.82:.1f} {cx + hw * 0.1:.1f} {y + h * 0.84:.1f} Z" fill="{dark}"/>')
        out.append(f'<path d="M {cx - hw * 0.7:.1f} {y + h * 0.5:.1f} Q {cx:.1f} {y + h * 0.66:.1f} {cx + hw * 0.7:.1f} {y + h * 0.34:.1f}" fill="none" stroke="{garland}" stroke-width="{3 * k:.1f}" stroke-linecap="round"/>')
    pos = [(-26, 70), (24, 92), (-44, 152), (6, 140), (54, 176), (-12, 198), (34, 44), (-58, 196), (40, 128)]
    for (dx, dy), col in zip(pos, list(balls) * 3):
        out.append(f'<circle cx="{cx + dx * k:.1f}" cy="{top + dy * k:.1f}" r="{7.5 * k:.1f}" fill="{col}"/>')
        out.append(f'<circle cx="{cx + dx * k - 2.5 * k:.1f}" cy="{top + dy * k - 2.5 * k:.1f}" r="{2 * k:.1f}" fill="#FFFFFF" opacity="0.6"/>')
    out.append(f'<polygon points="{star_points(cx, top - 2 * k, 24 * k, 10 * k)}" fill="{star}"/>')
    if gifts:
        for gx, gw, gh, col, rib in ((-92, 46, 34, "#C2343A", "#E9B949"), (52, 52, 40, "#E9B949", "#C2343A"), (-40, 34, 26, "#F6EFE0", "#2F7A57")):
            x, y = cx + gx * k, top + (224 - gh) * k
            out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{gw * k:.1f}" height="{gh * k:.1f}" fill="{col}"/>'
                       f'<rect x="{x + gw * k / 2 - 3 * k:.1f}" y="{y:.1f}" width="{6 * k:.1f}" height="{gh * k:.1f}" fill="{rib}"/>'
                       f'<path d="M {x + gw * k / 2:.1f} {y:.1f} q {-12 * k:.1f} {-12 * k:.1f} {-14 * k:.1f} 0 Z M {x + gw * k / 2:.1f} {y:.1f} q {12 * k:.1f} {-12 * k:.1f} {14 * k:.1f} 0 Z" fill="{rib}"/>')
    return "".join(out)


def string_lights(y, color_wire, bulbs, amp=26, x0=40, x1=560, n=9):
    pts = []
    d = f"M {x0} {y}"
    seg = (x1 - x0) / 4
    for i in range(4):
        d += f" q {seg / 2:.1f} {amp} {seg:.1f} 0"
    out = [f'<path d="{d}" fill="none" stroke="{color_wire}" stroke-width="2.5"/>']
    for i in range(n):
        t = (i + 0.5) / n
        x = x0 + t * (x1 - x0)
        local = (t * 4) % 1
        yy = y + amp * 2 * local * (1 - local)
        col = bulbs[i % len(bulbs)]
        out.append(f'<rect x="{x - 3:.1f}" y="{yy - 2:.1f}" width="6" height="7" fill="{color_wire}"/>'
                   f'<ellipse cx="{x:.1f}" cy="{yy + 14:.1f}" rx="7" ry="11" fill="{col}"/>'
                   f'<ellipse cx="{x - 2:.1f}" cy="{yy + 10:.1f}" rx="2" ry="4" fill="#FFFFFF" opacity="0.5"/>')
    return "".join(out)


def santa_hat(cx, base, s, red="#C2343A", fur="#FBF6EE", shade="#9E2428"):
    k = s / 100
    return (f'<path d="M {cx - 80 * k:.1f} {base:.1f} Q {cx - 70 * k:.1f} {base - 110 * k:.1f} {cx + 10 * k:.1f} {base - 120 * k:.1f} Q {cx + 80 * k:.1f} {base - 118 * k:.1f} {cx + 104 * k:.1f} {base - 60 * k:.1f} '
            f'Q {cx + 50 * k:.1f} {base - 84 * k:.1f} {cx + 40 * k:.1f} {base - 40 * k:.1f} L {cx + 80 * k:.1f} {base:.1f} Z" fill="{red}"/>'
            f'<path d="M {cx + 10 * k:.1f} {base - 120 * k:.1f} Q {cx + 80 * k:.1f} {base - 118 * k:.1f} {cx + 104 * k:.1f} {base - 60 * k:.1f} Q {cx + 62 * k:.1f} {base - 90 * k:.1f} {cx + 20 * k:.1f} {base - 98 * k:.1f} Z" fill="{shade}"/>'
            f'<rect x="{cx - 92 * k:.1f}" y="{base - 16 * k:.1f}" width="{184 * k:.1f}" height="{36 * k:.1f}" rx="{18 * k:.1f}" fill="{fur}"/>'
            f'<circle cx="{cx + 106 * k:.1f}" cy="{base - 52 * k:.1f}" r="{20 * k:.1f}" fill="{fur}"/>')


def candy_cane(x, y, h, w=12, red="#C2343A", white="#FBF6EE", rot=0):
    cid = f"cane{int(x)}{int(y)}"
    d = f"M {x} {y + h} L {x} {y + 22} Q {x} {y} {x + 20} {y} Q {x + 40} {y} {x + 40} {y + 20}"
    stripes = "".join(f'<line x1="{x - 30}" y1="{y + i}" x2="{x + 70}" y2="{y + i - 40}" stroke="{red}" stroke-width="7"/>' for i in range(-10, h + 50, 18))
    return (f'<g transform="rotate({rot} {x} {y + h / 2})"><mask id="{cid}"><path d="{d}" fill="none" stroke="#FFFFFF" stroke-width="{w}" stroke-linecap="round"/></mask>'
            f'<path d="{d}" fill="none" stroke="{white}" stroke-width="{w}" stroke-linecap="round"/><g mask="url(#{cid})">{stripes}</g></g>')


def holly(cx, cy, s, leaf="#2F7A57", vein="#24604A", berry="#C2343A"):
    out = []
    for rot in (-35, 35):
        pts = []
        for i in range(13):
            t = i / 12
            w = 0.32 * s * math.sin(math.pi * t) * (1.25 if i % 2 else 0.8)
            pts.append((cx + 0 + w, cy - t * s))
        for i in range(12, -1, -1):
            t = i / 12
            w = 0.32 * s * math.sin(math.pi * t) * (1.25 if i % 2 else 0.8)
            pts.append((cx - w, cy - t * s))
        out.append(f'<g transform="rotate({rot} {cx} {cy})"><polygon points="{P(pts)}" fill="{leaf}"/><line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - s:.1f}" stroke="{vein}" stroke-width="2"/></g>')
    for dx, dy in ((-7, 4), (7, 4), (0, -6)):
        out.append(f'<circle cx="{cx + dx * s / 50:.1f}" cy="{cy + dy * s / 50:.1f}" r="{0.14 * s:.1f}" fill="{berry}"/>')
    return "".join(out)


def gingerbread(cx, cy, s, body="#B8743F", icing="#FBF6EE", button="#C2343A"):
    k = s / 100
    d = (f"M {cx:.1f} {cy - 96 * k:.1f} A {30 * k:.1f} {30 * k:.1f} 0 0 1 {cx + 18 * k:.1f} {cy - 42 * k:.1f} L {cx + 58 * k:.1f} {cy - 36 * k:.1f} "
         f"A {14 * k:.1f} {14 * k:.1f} 0 0 1 {cx + 58 * k:.1f} {cy - 8 * k:.1f} L {cx + 30 * k:.1f} {cy - 6 * k:.1f} L {cx + 44 * k:.1f} {cy + 60 * k:.1f} "
         f"A {15 * k:.1f} {15 * k:.1f} 0 0 1 {cx + 16 * k:.1f} {cy + 68 * k:.1f} L {cx:.1f} {cy + 24 * k:.1f} L {cx - 16 * k:.1f} {cy + 68 * k:.1f} "
         f"A {15 * k:.1f} {15 * k:.1f} 0 0 1 {cx - 44 * k:.1f} {cy + 60 * k:.1f} L {cx - 30 * k:.1f} {cy - 6 * k:.1f} L {cx - 58 * k:.1f} {cy - 8 * k:.1f} "
         f"A {14 * k:.1f} {14 * k:.1f} 0 0 1 {cx - 58 * k:.1f} {cy - 36 * k:.1f} L {cx - 18 * k:.1f} {cy - 42 * k:.1f} A {30 * k:.1f} {30 * k:.1f} 0 0 1 {cx:.1f} {cy - 96 * k:.1f} Z")
    return (f'<path d="{d}" fill="{body}"/>'
            f'<g fill="{icing}"><circle cx="{cx - 9 * k:.1f}" cy="{cy - 72 * k:.1f}" r="{3.5 * k:.1f}"/><circle cx="{cx + 9 * k:.1f}" cy="{cy - 72 * k:.1f}" r="{3.5 * k:.1f}"/></g>'
            f'<path d="M {cx - 10 * k:.1f} {cy - 58 * k:.1f} Q {cx:.1f} {cy - 50 * k:.1f} {cx + 10 * k:.1f} {cy - 58 * k:.1f}" fill="none" stroke="{icing}" stroke-width="{3 * k:.1f}" stroke-linecap="round"/>'
            f'<g fill="none" stroke="{icing}" stroke-width="{3.5 * k:.1f}" stroke-linecap="round">'
            f'<path d="M {cx + 44 * k:.1f} {cy - 32 * k:.1f} q {4 * k:.1f} {6 * k:.1f} 0 {12 * k:.1f} q {-4 * k:.1f} {6 * k:.1f} 0 {12 * k:.1f}"/>'
            f'<path d="M {cx - 44 * k:.1f} {cy - 32 * k:.1f} q {4 * k:.1f} {6 * k:.1f} 0 {12 * k:.1f} q {-4 * k:.1f} {6 * k:.1f} 0 {12 * k:.1f}"/>'
            f'<path d="M {cx + 26 * k:.1f} {cy + 54 * k:.1f} q {6 * k:.1f} {-4 * k:.1f} {12 * k:.1f} 0"/><path d="M {cx - 38 * k:.1f} {cy + 54 * k:.1f} q {6 * k:.1f} {-4 * k:.1f} {12 * k:.1f} 0"/></g>'
            f'<g fill="{button}"><circle cx="{cx:.1f}" cy="{cy - 26 * k:.1f}" r="{5 * k:.1f}"/><circle cx="{cx:.1f}" cy="{cy - 6 * k:.1f}" r="{5 * k:.1f}"/></g>')
