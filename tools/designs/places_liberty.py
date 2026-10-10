"""Statue of Liberty, painted travel poster: the copper-green statue on its granite pedestal and star-shaped fort
on Liberty Island, seen from the water at sunrise, with lower Manhattan in the haze, a harbor ferry, gulls and
glinting water. The fort and pedestal are built in 3-D (pinhole camera from places_painted.Cam); the statue is
painted in 2-D in metres (heel = 0, y up) and placed on the pedestal at the camera's scale."""
import math
import random
import sys

from paint import P, dots, glow, lg, rg, rough
from places_painted import Cam, defs
from poster import poster

U = "sol"
LIGHT_DIR = (0.82, 0.18, -0.55)          # sunrise from the east: to the viewer's right, a little toward us


def _rgb(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return "#" + "".join(f"{max(0, min(255, round(x + (y - x) * t))):02X}" for x, y in zip(ra, rb))


def smooth(pts, closed=True, t=0.5):
    """Catmull-Rom through the points -> cubic Bezier path data."""
    n = len(pts)
    if n < 3:
        return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts)
    d = [f"M {pts[0][0]:.2f} {pts[0][1]:.2f}"]
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[0]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        d.append(f"C {c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}")
    if closed:
        d.append("Z")
    return " ".join(d)


# ------------------------------------------------------------------------------------------------ the statue
# verdigris palette, sunrise light from the right
V_DEEP, V_SHADE, V_MID, V_LIT, V_HI, V_RIM = "#24504F", "#356E69", "#5E9C8A", "#97C9AE", "#C9E4BE", "#F6E2B0"

ROBE = [(-5.3, 0.0), (-5.55, 3.0), (-5.25, 7.0), (-4.85, 11.0), (-4.55, 15.0), (-4.45, 19.0), (-4.55, 22.0), (-4.95, 24.5),
        (-4.65, 26.8), (-3.6, 27.9), (-1.3, 28.55), (1.3, 28.6), (3.0, 28.35), (4.25, 27.6), (4.95, 26.0), (5.35, 23.5),
        (5.85, 20.5), (6.3, 17.0), (6.5, 13.5), (6.2, 10.5), (5.75, 8.3), (5.45, 5.0), (5.35, 2.0), (5.0, 0.15),
        (4.0, 0.32), (3.0, 0.02), (2.0, 0.34), (1.0, 0.05), (0.0, 0.32), (-1.1, 0.0), (-2.2, 0.36), (-3.3, 0.04), (-4.3, 0.3)]
SLEEVE = [(-5.0, 31.4), (-5.65, 31.6), (-6.2, 29.2), (-6.15, 26.6), (-5.45, 24.6), (-4.65, 23.5), (-4.3, 25.2), (-4.35, 27.3),
          (-4.75, 29.4)]
ARM_UP = [(-4.6, 27.6), (-5.2, 29.5), (-5.5, 32.4), (-5.3, 35.3), (-5.05, 37.6), (-3.65, 37.6), (-3.72, 35.3), (-3.9, 32.4),
          (-3.3, 29.8), (-2.5, 28.3)]
FIST = [(-5.35, 37.25), (-5.45, 38.4), (-5.1, 39.6), (-4.0, 39.75), (-3.45, 38.9), (-3.55, 37.5), (-4.2, 37.05)]
HEAD = [(1.0, 28.62), (1.6, 28.98), (1.92, 29.42), (2.06, 29.78), (2.18, 30.12), (2.52, 30.42), (2.34, 30.72), (2.26, 31.3),
        (2.28, 31.68), (2.12, 32.5), (1.3, 33.4), (0.1, 33.75), (-1.15, 33.4), (-1.9, 32.6), (-2.2, 31.45), (-2.3, 30.3),
        (-1.95, 29.45), (-1.3, 28.95), (-0.2, 28.62)]
NECK = [(-1.3, 28.35), (-1.25, 29.6), (0.0, 29.1), (1.35, 29.3), (1.35, 28.45)]
TABLET = [(3.0, 29.05), (5.3, 28.1), (6.0, 20.0), (4.1, 20.4)]
TABLET_EDGE = [(2.55, 28.8), (3.0, 29.05), (4.1, 20.4), (3.7, 20.25)]
FOREARM = [(4.6, 25.6), (5.75, 23.4), (6.15, 21.6), (5.6, 20.6), (4.4, 20.55), (4.7, 22.2), (4.3, 24.6)]


def statue(x0, y0, s, uid=U + "-st"):
    """Painted statue; (x0, y0) = screen point under her heel line (pedestal top), s = px per metre."""
    o = []
    D = []
    D.append(lg(f"{uid}-body", [(0, V_DEEP), (0.16, V_SHADE), (0.46, V_MID), (0.7, V_LIT), (0.88, V_HI), (1, V_RIM)], -6.2, 0, 6.6, 0, units="userSpaceOnUse"))
    D.append(lg(f"{uid}-arm", [(0, V_DEEP), (0.4, V_SHADE), (0.8, V_MID), (1, V_LIT)], -6.2, 0, -3.4, 0, units="userSpaceOnUse"))
    D.append(lg(f"{uid}-head", [(0, V_SHADE), (0.35, V_MID), (0.68, V_LIT), (1, V_HI)], -2.3, 0, 2.5, 0, units="userSpaceOnUse"))
    D.append(lg(f"{uid}-tab", [(0, V_LIT), (0.55, V_HI), (1, "#EAF0C8")], 3.0, 0, 6.0, 0, units="userSpaceOnUse"))
    D.append(lg(f"{uid}-gold", [(0, "#FFF6C8"), (0.3, "#FFD86E"), (0.72, "#E89E2C"), (1, "#B0681C")], 0, 46.8, 0, 42.8, units="userSpaceOnUse"))
    D.append(lg(f"{uid}-goldx", [(0, "#A8601A", 0.85), (0.5, "#FFE08A", 0), (1, "#FFF8D8", 0.9)], -6.0, 0, -2.6, 0, units="userSpaceOnUse"))
    D.append(f'<clipPath id="{uid}-cr"><path d="{smooth(ROBE)}"/></clipPath>')
    D.append(f'<clipPath id="{uid}-ch"><path d="{smooth(HEAD)}"/></clipPath>')
    D.append(f'<clipPath id="{uid}-cs"><path d="{smooth(SLEEVE)}"/></clipPath>')
    D.append(f'<clipPath id="{uid}-ca"><path d="{smooth(ARM_UP)}"/></clipPath>')
    # ---- crown rays behind the head: faceted spikes, sun-side facet lit
    rays = []
    cx, cy = 0.3, 31.75
    for ang, L, w in ((167, 2.6, 0.9), (142, 3.2, 0.98), (116, 3.55, 1.02), (91, 3.75, 1.05), (66, 3.75, 1.05), (41, 3.5, 1.0), (17, 3.0, 0.95)):
        a = math.radians(ang)
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        bx, by = cx + ux * 1.85, cy + uy * 1.6
        tx, ty = bx + ux * L, by + uy * L
        l1 = (bx + nx * w / 2, by + ny * w / 2)
        r1 = (bx - nx * w / 2, by - ny * w / 2)
        lit_half = [r1, (tx, ty), (bx, by)]
        dark_half = [l1, (tx, ty), (bx, by)]
        rays.append(f'<polygon points="{P(dark_half)}" fill="{V_DEEP if ang > 120 else V_SHADE}"/>')
        rays.append(f'<polygon points="{P(lit_half)}" fill="{V_SHADE if ang > 150 else V_MID if ang > 110 else V_LIT if ang > 55 else V_HI}"/>')
        if ang < 120:
            rays.append(f'<polyline points="{P([r1, (tx, ty)])}" fill="none" stroke="{V_RIM}" stroke-width="0.12" opacity="0.85"/>')
    o.append("".join(rays))
    # ---- robe body
    o.append(f'<path d="{smooth(ROBE)}" fill="url(#{uid}-body)"/>')
    folds = []
    # stola below the mantle: deep vertical folds flaring to the scalloped hem
    for i in range(13):
        x = -4.9 + i * 0.85
        top = 10.4 + 0.4 * math.sin(i * 1.7) + (1.4 if x < -3 else 0) - x * 0.12
        dk = 0.34 if x < 1.5 else 0.26
        folds.append(f'<path d="M {x:.2f} {top:.2f} C {x - 0.12:.2f} {top - 3.4:.2f} {x - 0.3:.2f} {top - 6.5:.2f} {x - 0.35 + (i - 6) * 0.05:.2f} 0.1" '
                     f'stroke="{V_DEEP}" stroke-width="{dk:.2f}" opacity="{0.8 if x < 2 else 0.55}"/>')
        folds.append(f'<path d="M {x + 0.36:.2f} {top - 0.6:.2f} C {x + 0.28:.2f} {top - 3.8:.2f} {x + 0.12:.2f} {top - 6.5:.2f} {x + 0.1 + (i - 6) * 0.05:.2f} 0.4" '
                     f'stroke="{V_HI}" stroke-width="0.15" opacity="{0.22 if x < -1 else 0.65}"/>')
    # her right knee pressing forward through the cloth as she steps
    folds.append(f'<path d="M -3.4 13.2 Q -2.2 11.8 -1.0 12.6" stroke="{V_HI}" stroke-width="0.2" opacity="0.4"/>')
    # the mantle: drooping lower hem with its shadow, diagonal top edge, three swags round the hips
    mantle_hem = [(-4.8, 13.2), (-3.0, 11.6), (-1.0, 10.6), (1.2, 10.2), (3.4, 9.7), (5.2, 9.0), (6.4, 9.2)]
    folds.append(f'<path d="{smooth(mantle_hem, closed=False)} L 6.6 7.9 C 4.2 8.3 1.6 8.9 -1.0 9.6 C -3.0 10.3 -4.3 11.4 -5.1 12.2 Z" fill="{V_DEEP}" opacity="0.6"/>')
    folds.append(f'<path d="{smooth(mantle_hem, closed=False)}" stroke="{V_HI}" stroke-width="0.2" opacity="0.65"/>')
    diag = [(4.2, 27.4), (2.6, 25.6), (0.7, 23.3), (-1.4, 20.9), (-3.2, 19.2), (-4.6, 18.3)]
    folds.append(f'<path d="{smooth(diag, closed=False)} L -4.6 17.1 C -3.0 17.9 -1.2 19.6 0.8 21.9 C 2.4 23.8 3.6 25.6 4.4 26.6 Z" fill="{V_DEEP}" opacity="0.55"/>')
    folds.append(f'<path d="{smooth(diag, closed=False)}" stroke="{V_HI}" stroke-width="0.22" opacity="0.8"/>')
    for k, (y, dip, wd) in enumerate(((16.6, 1.4, 0.42), (14.4, 1.1, 0.34), (12.6, 0.8, 0.3))):
        sw = [(6.2, y + 3.6), (3.6, y + 1.0), (1.0, y - dip), (-1.6, y - dip * 0.6), (-4.4, y + 0.9)]
        folds.append(f'<path d="{smooth(sw, closed=False)}" stroke="{V_DEEP}" stroke-width="{wd}" opacity="0.6"/>')
        sw2 = [(p[0], p[1] + 0.45) for p in sw]
        folds.append(f'<path d="{smooth(sw2, closed=False)}" stroke="{V_HI}" stroke-width="0.16" opacity="0.5"/>')
    # gathered chiton folds over the chest, above the mantle
    for k in range(6):
        x = -3.9 + k * 0.95
        folds.append(f'<path d="M {x:.2f} {27.3 - abs(k - 2.5) * 0.25:.2f} Q {x - 0.2 + k * 0.05:.2f} 24.5 {x - 0.55 + k * 0.08:.2f} {21.4 - k * 0.6:.2f}" stroke="{V_DEEP}" stroke-width="0.22" opacity="0.5"/>')
    # cascade of the mantle hanging from the left forearm: zig-zag folds on the sunlit side
    for k in range(4):
        x = 4.6 + k * 0.45
        folds.append(f'<path d="M {x:.2f} 20.4 C {x + 0.25:.2f} 17.0 {x + 0.55:.2f} 13.0 {x + 0.15 - k * 0.1:.2f} 9.0" stroke="{V_SHADE}" stroke-width="0.26" opacity="0.65"/>')
        folds.append(f'<path d="M {x + 0.22:.2f} 20.4 C {x + 0.47:.2f} 17.0 {x + 0.75:.2f} 13.0 {x + 0.37 - k * 0.1:.2f} 8.8" stroke="{V_RIM}" stroke-width="0.13" opacity="0.55"/>')
    # form shadows: under the raised arm, cast by the tablet, the turning shadow side of the body
    folds.append(f'<path d="M -4.8 26.0 C -3.4 25.2 -2.6 23.6 -2.8 21.2 C -3.5 21.7 -4.1 22.6 -4.6 23.4 Z" fill="{V_DEEP}" opacity="0.55"/>')
    folds.append(f'<path d="M 4.1 20.4 C 3.4 21.0 2.7 23.6 2.5 28.4 L 3.0 29.0 Z" fill="{V_DEEP}" opacity="0.6"/>')
    folds.append(f'<path d="M -5.9 0 L -5.9 28 L -3.8 28 C -4.1 20 -4.2 10 -4.1 0 Z" fill="{V_DEEP}" opacity="0.35"/>')
    o.append(f'<g clip-path="url(#{uid}-cr)" fill="none" stroke-linecap="round">' + "".join(folds) + "</g>")
    o.append(f'<path d="{smooth(ROBE[11:24], closed=False)}" fill="none" stroke="{V_RIM}" stroke-width="0.2" opacity="0.85"/>')
    # sandaled toes of the left foot under the hem
    o.append(f'<path d="M 0.6 0.05 Q 1.0 0.62 1.9 0.48 Q 2.25 0.25 2.15 0.0 Z" fill="{V_MID}"/>')
    # ---- left forearm and the tablet (keystone-shaped, inscribed with the date)
    o.append(f'<path d="{smooth(FOREARM)}" fill="{V_LIT}"/>')
    o.append(f'<polygon points="{P(TABLET_EDGE)}" fill="{V_SHADE}"/>')
    o.append(f'<polygon points="{P(TABLET)}" fill="url(#{uid}-tab)"/>')
    for a in (0.3, 0.42, 0.54):
        p1 = (TABLET[0][0] + (TABLET[3][0] - TABLET[0][0]) * a, TABLET[0][1] + (TABLET[3][1] - TABLET[0][1]) * a)
        p2 = (TABLET[1][0] + (TABLET[2][0] - TABLET[1][0]) * a, TABLET[1][1] + (TABLET[2][1] - TABLET[1][1]) * a)
        o.append(f'<line x1="{p1[0] + 0.45:.2f}" y1="{p1[1]:.2f}" x2="{p2[0] - 0.45:.2f}" y2="{p2[1]:.2f}" stroke="{V_SHADE}" stroke-width="0.2" opacity="0.7"/>')
    o.append(f'<polyline points="{P([TABLET[0], TABLET[1], TABLET[2]])}" fill="none" stroke="{V_RIM}" stroke-width="0.17" opacity="0.95"/>')
    o.append(f'<path d="M 4.0 21.0 Q 4.5 22.0 5.2 21.4 Q 5.9 20.9 5.9 20.25 Q 4.8 19.9 4.0 21.0 Z" fill="{V_LIT}"/>')
    o.append(f'<path d="M 4.3 20.7 L 5.75 20.45 M 4.4 21.15 L 5.65 20.9" stroke="{V_SHADE}" stroke-width="0.1"/>')
    # ---- raised right arm, the sleeve slipped down into a heavy drape below the shoulder
    o.append(f'<path d="{smooth(ARM_UP)}" fill="url(#{uid}-arm)"/>')
    o.append(f'<g clip-path="url(#{uid}-ca)" fill="none">'
             f'<path d="M -3.0 29.4 Q -3.7 33.0 -3.8 37.6" stroke="{V_LIT}" stroke-width="0.35" opacity="0.7"/>'
             f'<path d="M -5.0 32.0 Q -4.6 32.5 -4.2 32.2" stroke="{V_DEEP}" stroke-width="0.16" opacity="0.7"/></g>')
    o.append(f'<path d="{smooth(SLEEVE)}" fill="url(#{uid}-arm)"/>')
    sl = []
    for k in range(4):
        sl.append(f'<path d="M {-4.6 - k * 0.38:.2f} {29.6 + k * 0.4:.2f} Q {-5.6 - k * 0.12:.2f} {27.6:.2f} {-5.1 - k * 0.22:.2f} {24.6 + k * 0.4:.2f}" stroke="{V_DEEP}" stroke-width="0.22" opacity="0.7"/>')
        sl.append(f'<path d="M {-4.4 - k * 0.38:.2f} {29.6 + k * 0.4:.2f} Q {-5.4 - k * 0.12:.2f} {27.6:.2f} {-4.9 - k * 0.22:.2f} {24.6 + k * 0.4:.2f}" stroke="{V_MID}" stroke-width="0.12" opacity="0.6"/>')
    o.append(f'<g clip-path="url(#{uid}-cs)" fill="none" stroke-linecap="round">' + "".join(sl) + "</g>")
    o.append(f'<path d="{smooth(FIST)}" fill="{V_MID}"/>')
    o.append(f'<path d="M -5.3 37.9 L -3.6 38.0 M -5.35 38.65 L -3.5 38.75" stroke="{V_DEEP}" stroke-width="0.13" opacity="0.7"/>')
    o.append(f'<path d="M -3.6 37.5 Q -3.35 38.4 -3.55 39.3" fill="none" stroke="{V_LIT}" stroke-width="0.2"/>')
    # ---- the torch: handle, ornamented cup, railed balcony, gold-leaf flame
    o.append(f'<polygon points="{P([(-4.85, 39.5), (-4.72, 41.0), (-3.95, 41.0), (-3.82, 39.5)])}" fill="{V_SHADE}"/>')
    o.append(f'<polygon points="{P([(-5.0, 40.9), (-5.85, 42.55), (-2.85, 42.55), (-3.7, 40.9)])}" fill="url(#{uid}-arm)"/>')
    o.append(f'<path d="M -5.8 42.5 L -2.9 42.5 M -5.5 41.95 L -3.2 41.95 M -5.2 41.4 L -3.5 41.4" stroke="{V_DEEP}" stroke-width="0.12" opacity="0.8"/>')
    o.append(f'<path d="M -3.2 41.95 L -2.9 42.5 M -3.5 41.1 L -3.2 41.9" stroke="{V_LIT}" stroke-width="0.15"/>')
    o.append(f'<ellipse cx="-4.35" cy="42.65" rx="2.55" ry="0.4" fill="{V_SHADE}"/><ellipse cx="-4.35" cy="42.78" rx="2.55" ry="0.26" fill="{V_MID}"/>')
    o.append(f'<path d="M -6.85 43.45 Q -4.35 43.8 -1.85 43.45" fill="none" stroke="{V_MID}" stroke-width="0.15"/>')
    o.append(f'<g stroke="{V_MID}" stroke-width="0.12">' + "".join(f'<line x1="{-6.8 + i * 0.62:.2f}" y1="42.75" x2="{-6.8 + i * 0.62:.2f}" y2="{43.48 + 0.3 * math.sin(math.pi * i / 8):.2f}"/>' for i in range(9)) + "</g>")
    flame = [(-5.5, 42.95), (-5.95, 43.9), (-5.65, 45.0), (-5.0, 45.75), (-4.55, 46.35), (-4.1, 47.0), (-3.95, 45.9), (-3.4, 45.0), (-2.95, 44.0), (-3.3, 42.95)]
    o.append(f'<path d="{smooth(flame)}" fill="url(#{uid}-gold)"/>')
    o.append(f'<path d="{smooth(flame)}" fill="url(#{uid}-goldx)"/>')
    o.append(f'<path d="M -4.75 43.2 Q -5.2 44.4 -4.4 45.6 Q -4.0 44.4 -4.0 43.2 Z" fill="#FFF8DC" opacity="0.85"/>')
    o.append(f'<path d="M -3.55 43.1 Q -3.05 44.0 -3.6 45.0" fill="none" stroke="#FFF4C8" stroke-width="0.16"/>')
    # ---- neck, head, hair, face
    o.append(f'<path d="{smooth(NECK)}" fill="url(#{uid}-head)"/>')
    o.append(f'<path d="M -1.2 28.4 Q -0.2 28.95 0.7 28.95" fill="none" stroke="{V_DEEP}" stroke-width="0.16" opacity="0.5"/>')
    o.append(f'<path d="{smooth(HEAD)}" fill="url(#{uid}-head)"/>')
    hd = []
    hair = [(-0.2, 32.7), (0.55, 32.35), (1.2, 32.45), (0.95, 31.95), (0.2, 31.6), (-0.5, 30.95), (-0.8, 30.1), (-1.05, 29.45), (-1.85, 29.35), (-2.4, 30.4), (-2.3, 31.7), (-1.7, 32.7)]
    hd.append(f'<path d="{smooth(hair)}" fill="{V_SHADE}"/>')
    for k in range(4):
        hd.append(f'<path d="M {0.7 - k * 0.6:.2f} {32.25 - k * 0.12:.2f} Q {-0.05 - k * 0.5:.2f} {31.4 - k * 0.2:.2f} {-0.55 - k * 0.42:.2f} {30.2 - k * 0.15:.2f}" stroke="{V_MID}" stroke-width="0.15" opacity="0.8" fill="none"/>')
    hd.append(f'<ellipse cx="-2.0" cy="29.75" rx="0.6" ry="0.55" fill="{V_DEEP}"/>')
    hd.append(f'<path d="M 0.15 32.3 Q 0.65 30.4 0.95 28.7 L -0.6 28.6 Q -0.6 30.8 0.15 32.3 Z" fill="{V_SHADE}" opacity="0.35"/>')
    hd.append(f'<path d="M 1.05 31.75 Q 1.65 32.0 2.25 31.8" fill="none" stroke="{V_DEEP}" stroke-width="0.16" opacity="0.75"/>')
    hd.append(f'<ellipse cx="1.68" cy="31.38" rx="0.38" ry="0.2" fill="{V_DEEP}" opacity="0.85"/>')
    hd.append(f'<path d="M 2.26 31.35 L 2.5 30.45 L 2.15 30.18" fill="none" stroke="{V_DEEP}" stroke-width="0.13" opacity="0.55"/>')
    hd.append(f'<path d="M 1.35 29.68 Q 1.7 29.8 2.0 29.68" fill="none" stroke="{V_DEEP}" stroke-width="0.14" opacity="0.75"/>')
    hd.append(f'<path d="M 2.05 30.38 Q 2.25 31.1 2.2 31.75 L 2.42 31.75 L 2.55 30.45 Z" fill="{V_HI}" opacity="0.8"/>')
    o.append(f'<g clip-path="url(#{uid}-ch)">' + "".join(hd) + "</g>")
    o.append(f'<path d="{smooth(HEAD[0:12], closed=False)}" fill="none" stroke="{V_RIM}" stroke-width="0.15" opacity="0.9"/>')
    # diadem band with its row of windows, over the brow
    band = [(-2.05, 32.45), (-1.1, 33.1), (0.25, 33.45), (1.4, 33.25), (2.3, 32.7), (2.35, 32.05), (1.4, 32.6), (0.25, 32.8), (-1.1, 32.55), (-2.1, 31.85)]
    o.append(f'<path d="{smooth(band)}" fill="{V_LIT}"/>')
    o.append(f'<path d="{smooth(band[:5], closed=False)}" fill="none" stroke="{V_SHADE}" stroke-width="0.12"/>')
    o.append(f'<g fill="{V_DEEP}">' + "".join(f'<rect x="{-1.45 + i * 0.4:.2f}" y="{32.6 + 0.38 * math.sin((i + 1.5) / 9.5 * math.pi) - 0.12:.2f}" width="0.2" height="0.25"/>' for i in range(9)) + "</g>")
    return (defs(*D) + f'<g transform="translate({x0:.1f} {y0:.1f}) scale({s:.4f} {-s:.4f})">' + "".join(o) + "</g>")


# ------------------------------------------------------------------------------------------------ the scene
ZS = 320.0                    # distance to the statue's axis (m)
EYE, HZ = 24.0, 312           # eye height on the ferry deck, horizon line
ROT = math.radians(30)        # the pedestal (and statue) turned to face the viewer's right, toward the harbor mouth
LX, LZ = 0.8 / 0.97, -0.55 / 0.97


def W(a, y, b):
    """Local pedestal coordinates (a across the front face, b toward the back) -> world."""
    return (a * math.cos(ROT) - b * math.sin(ROT), y, ZS + a * math.sin(ROT) + b * math.cos(ROT))


def shade(lit, dark, nx, nz, amb=0.0):
    lam = max(0.0, nx * LX + nz * LZ)
    return mix(dark, lit, min(1.0, amb + lam * 1.05))


def prism(C, pts, Y0, Y1, lit, dark, extra=None, top=None):
    """Vertical prism over a closed footprint (list of world (X, Z) points, counter-clockwise seen from above):
    draws the outward faces that look toward the camera, shaded by the sunrise."""
    out = []
    faces = []
    n = len(pts)
    for i in range(n):
        (x1, z1), (x2, z2) = pts[i], pts[(i + 1) % n]
        nx, nz = (z2 - z1), -(x2 - x1)
        L = math.hypot(nx, nz)
        nx, nz = nx / L, nz / L
        mx, mz = (x1 + x2) / 2, (z1 + z2) / 2
        if nx * (0 - mx) + nz * (0 - mz) <= 0:
            continue
        faces.append(((mz), [(x1, z1), (x2, z2)], nx, nz))
    for _, ((x1, z1), (x2, z2)), nx, nz in sorted(faces, key=lambda f: -f[0]):
        q = [C(x1, Y0, z1), C(x1, Y1, z1), C(x2, Y1, z2), C(x2, Y0, z2)]
        col = shade(lit, dark, nx, nz)
        out.append(f'<polygon points="{P(q)}" fill="{col}"/>')
        if extra:
            out.append(extra(C, (x1, z1), (x2, z2), Y0, Y1, nx, nz, col))
    if Y1 < C.eye:
        out.append(f'<polygon points="{P([C(x, Y1, z) for x, z in pts])}" fill="{top or mix(lit, "#FFFFFF", 0.15)}"/>')
    return "".join(out)


def seawall(C, p1, p2, Y0, Y1, nx, nz, col):
    """Granite sea wall: a pale coping along the top, the dark wet foot at the waterline."""
    (x1, z1), (x2, z2) = p1, p2
    top = [C(x1, Y1, z1), C(x2, Y1, z2), C(x2, Y1 - 0.5, z2), C(x1, Y1 - 0.5, z1)]
    foot = [C(x1, 0, z1), C(x2, 0, z2), C(x2, 0.7, z2), C(x1, 0.7, z1)]
    return f'<polygon points="{P(top)}" fill="#F6E4CC"/><polygon points="{P(foot)}" fill="#4A4660"/>'


def fortwall(C, p1, p2, Y0, Y1, nx, nz, col):
    """Old granite walls of the star fort: coursed blocks, a coping lit by the sun, a shadowed foot."""
    (x1, z1), (x2, z2) = p1, p2
    o = []
    for yy in (4.6, 6.2, 7.8, 9.2):
        a, b = C(x1, yy, z1), C(x2, yy, z2)
        o.append(f'M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}')
    top = [C(x1, Y1, z1), C(x2, Y1, z2), C(x2, Y1 - 0.7, z2), C(x1, Y1 - 0.7, z1)]
    foot = [C(x1, Y0, z1), C(x2, Y0, z2), C(x2, Y0 + 0.8, z2), C(x1, Y0 + 0.8, z1)]
    return (f'<path d="{"".join(o)}" stroke="#4A4060" stroke-width="0.5" opacity="0.3" fill="none"/>'
            f'<polygon points="{P(top)}" fill="{mix(col, "#FFF4E0", 0.35)}"/><polygon points="{P(foot)}" fill="#3A3450" opacity="0.4"/>')


def reflect(C, pts3, col, seed, op=0.4):
    """Mirrored (Y -> -Y) projection broken into horizontal dabs, fading with depth."""
    rnd = random.Random(seed)
    poly = [C(X, -Y, Z) for X, Y, Z in pts3]
    ys = [y for _, y in poly]
    y0, y1 = min(ys), min(max(ys), 444)
    out = []
    y = y0
    while y < y1:
        xs = []
        for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
            if (ay <= y < by) or (by <= y < ay):
                xs.append(ax + (bx - ax) * (y - ay) / (by - ay))
        h = rnd.uniform(0.9, 2.0)
        if len(xs) >= 2:
            a, b = min(xs), max(xs)
            w = b - a
            a += rnd.uniform(-0.1, 0.15) * w
            b += rnd.uniform(-0.15, 0.1) * w
            t = (y - y0) / max(1, (y1 - y0))
            x = a
            while x < b:
                L_ = min(b - x, rnd.uniform(0.2, 0.7) * w + 2)
                out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{L_:.1f}" height="{h:.1f}" rx="{h / 2:.1f}" fill="{col}" opacity="{op * (1 - 0.6 * t) * rnd.uniform(0.55, 1):.2f}"/>')
                x += L_ + rnd.uniform(0.04, 0.2) * w + 1
        y += h + rnd.uniform(0.6, 1.8)
    return "".join(out)


def square(a, b0=None):
    """Footprint of the square pedestal tier with half-width a (counter-clockwise from above)."""
    b0 = a if b0 is None else b0
    loc = [(-a, -b0), (a, -b0), (a, b0), (-a, b0)]
    return [(W(x, 0, z)[0], W(x, 0, z)[2]) for x, z in loc]


def star(n=11, ro=46.0, ri=33.0, rot=0.12):
    pts = []
    for i in range(2 * n):
        r = ro if i % 2 == 0 else ri
        a = rot + math.pi * i / n
        pts.append((r * math.sin(a), ZS + 6 + r * math.cos(a)))
    return pts[::-1]


def cloud_bank(uid, puffs, top, bottom, lit, shadow, rim):
    """Cumulus built from overlapping puffs: one vertical gradient for the body, then sun-warmed puffs on
    the right/upper sides and a rim along the sunward edges."""
    body = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>' for x, y, r in puffs)
    lights = "".join(f'<circle cx="{x + r * 0.28:.1f}" cy="{y - r * 0.22:.1f}" r="{r * 0.72:.1f}"/>' for x, y, r in puffs)
    rims = "".join(f'<path d="M {x + r * 0.2:.1f} {y - r * 0.98:.1f} A {r:.1f} {r:.1f} 0 0 1 {x + r * 0.98:.1f} {y + r * 0.2:.1f}"/>' for x, y, r in puffs)
    return (defs(lg(uid, [(0, lit), (1, shadow)], 0, top, 0, bottom, units="userSpaceOnUse"))
            + f'<g fill="url(#{uid})">{body}</g><g fill="{lit}" opacity="0.55">{lights}</g>'
            + f'<g fill="none" stroke="{rim}" stroke-width="1.6" opacity="0.7">{rims}</g>')


def puffs_row(seed, x0, x1, y, h, rmin, rmax, n):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        t = i / (n - 1)
        x = x0 + (x1 - x0) * t + rnd.uniform(-6, 6)
        hump = math.sin(math.pi * t) ** 0.7
        r = rmin + (rmax - rmin) * hump * rnd.uniform(0.7, 1.05)
        out.append((x, y - h * hump * rnd.uniform(0.6, 1.0) + r * 0.3, r))
    for i in range(n):
        x = x0 + (x1 - x0) * rnd.random()
        out.append((x, y + rnd.uniform(-2, 3), rmin * rnd.uniform(0.7, 1.1)))
    return out


def skyline(C):
    """Lower Manhattan across the harbor, faces toward the sunrise glowing, the rest in blue haze."""
    out = []
    rnd = random.Random(11)
    Z = 4600.0
    k = C.f / Z
    base = C(0, 0, Z)[1]
    haze = "#B9A8C4"
    blds = []
    # (x centre px, width px, height px, kind)
    spec = [(372, 10, 30, "box"), (384, 9, 44, "box"), (394, 12, 36, "box"), (404, 8, 58, "box"), (414, 12, 50, "pyr"),
            (426, 10, 72, "box"), (437, 13, 62, "box"), (447, 9, 84, "box"), (458, 12, 70, "slant"), (470, 9, 92, "box"),
            (482, 14, 74, "box"), (494, 10, 58, "spire"), (505, 12, 66, "box"), (516, 9, 48, "box"), (526, 13, 56, "box"),
            (538, 10, 40, "box"), (549, 12, 46, "pyr"), (561, 10, 34, "box"), (572, 14, 38, "box"), (586, 12, 28, "box"),
            (598, 16, 24, "box"), (362, 12, 22, "box"), (352, 14, 18, "box")]
    for x, w, h, kind in sorted(spec, key=lambda t: t[2]):
        blds.append((x, w, h, kind))
    far = []
    for i in range(30):
        x = rnd.uniform(340, 610)
        far.append(f'<rect x="{x:.0f}" y="{base - rnd.uniform(10, 40):.0f}" width="{rnd.uniform(6, 14):.0f}" height="60" fill="#BCA8C8"/>')
    out.append("".join(far))
    for x, w, h, kind in blds:
        top = base - h
        side = w * 0.35
        lit_c, sh_c = "#FFD0A0", rnd.choice(["#8A82AA", "#7E7AA4", "#9488B0", "#857CA6"])
        # shaded front (south-west) face, sunlit east face as a narrow strip on the right
        if kind == "pyr":
            out.append(f'<polygon points="{P([(x - w / 2, base), (x - w / 2, top + 6), (x, top - 4), (x + w / 2, top + 6), (x + w / 2, base)])}" fill="{sh_c}"/>')
            out.append(f'<polygon points="{P([(x, top - 4), (x + w / 2, top + 6), (x + w / 2 + side, top + 7), (x + w / 2 + side, base)])}" fill="{lit_c}"/>')
        elif kind == "slant":
            out.append(f'<polygon points="{P([(x - w / 2, base), (x - w / 2, top + 8), (x + w / 2, top), (x + w / 2, base)])}" fill="{sh_c}"/>')
            out.append(f'<polygon points="{P([(x + w / 2, top), (x + w / 2 + side, top + 2), (x + w / 2 + side, base), (x + w / 2, base)])}" fill="{lit_c}"/>')
        else:
            out.append(f'<rect x="{x - w / 2:.1f}" y="{top:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{sh_c}"/>')
            out.append(f'<polygon points="{P([(x + w / 2, top), (x + w / 2 + side, top + 1.5), (x + w / 2 + side, base), (x + w / 2, base)])}" fill="{lit_c}"/>')
            if kind == "spire":
                out.append(f'<polygon points="{P([(x - 2.5, top), (x, top - 14), (x + 2.5, top)])}" fill="{sh_c}"/><line x1="{x}" y1="{top - 14}" x2="{x}" y2="{top - 20}" stroke="{sh_c}" stroke-width="1"/>')
        # window rows glinting gold in the sunrise
        g = []
        for yy in range(int(top + 4), int(base - 2), 4):
            if rnd.random() < 0.5:
                g.append(f'<rect x="{x - w / 2 + 1.5:.1f}" y="{yy}" width="{w - 3:.1f}" height="1" fill="#D8C0C8" opacity="0.5"/>')
            if rnd.random() < 0.25:
                g.append(f'<rect x="{x + w / 2 + 0.6:.1f}" y="{yy}" width="{side - 1:.1f}" height="1.2" fill="#FFF0C8" opacity="0.9"/>')
        out.append("".join(g))
    # the tallest tower: a square shaft twisting into eight tall triangles, then the spire
    x, w, h = 462, 20, 118
    top = base - h
    tw = w * 0.62
    out.append(f'<polygon points="{P([(x - w / 2, base), (x - w / 2, base - 22), (x - tw / 2, top), (x + tw / 2, top), (x + w / 2, base - 22), (x + w / 2, base)])}" fill="#A498B8"/>')
    out.append(f'<polygon points="{P([(x - w / 2, base - 22), (x - tw / 2, top), (x, top), (x - w / 2 + 2, base - 22)])}" fill="#8C82A6"/>')
    out.append(f'<polygon points="{P([(x, top), (x + tw / 2, top), (x + w / 2, base - 22), (x + 1, base - 22)])}" fill="#E8BFA8"/>')
    out.append(f'<polygon points="{P([(x + 1, base - 22), (x + w / 2, base - 22), (x + w / 2, base), (x + 1, base)])}" fill="#D6B0A2"/>')
    out.append(f'<polygon points="{P([(x - w / 2, base - 22), (x + 1, base - 22), (x + 1, base), (x - w / 2, base)])}" fill="#9A90AE"/>')
    out.append(f'<path d="M {x + 1} {base - 22} L {x + tw / 2 - 0.5} {top + 1}" stroke="#FFF2D8" stroke-width="1" opacity="0.8"/>')
    out.append(f'<rect x="{x - tw / 2 + 0.5:.1f}" y="{top - 2:.1f}" width="{tw - 1:.1f}" height="2" fill="#7E7498"/>')
    out.append(f'<line x1="{x}" y1="{top - 2}" x2="{x}" y2="{top - 34}" stroke="#8C82A6" stroke-width="1.6"/><line x1="{x + 0.5}" y1="{top - 2}" x2="{x + 0.5}" y2="{top - 34}" stroke="#FFE8C8" stroke-width="0.5"/>')
    out.append(f'<circle cx="{x}" cy="{top - 34}" r="1.2" fill="#FFF4E0"/>')
    # haze over the foot of the city
    out.append(defs(lg(f"{U}-cityhaze", [(0, haze, 0), (0.6, "#E8C4C0", 0.25), (1, "#F0CCC0", 0.75)], 0, base - 70, 0, base, units="userSpaceOnUse")))
    out.append(f'<rect x="0" y="{base - 70:.0f}" width="600" height="72" fill="url(#{U}-cityhaze)"/>')
    return "".join(out)


def gull(x, y, s, flap=0.0, flip=1, body="#F6F2EC", back="#B8B6C6"):
    k = s / 20
    w = 9 - 6 * flap
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({k * flip:.3f} {k:.3f})">'
            f'<path d="M -21 {w - 6:.1f} Q -11 {-w - 5:.1f} -2 -1 L 2 -1 Q 11 {-w - 5:.1f} 21 {w - 6:.1f} Q 11 {-w + 2:.1f} 2 2.5 L -2 2.5 Q -11 {-w + 2:.1f} -21 {w - 6:.1f} Z" fill="{back}"/>'
            f'<path d="M -21 {w - 6:.1f} Q -18 {w - 9:.1f} -15 {w - 9.6:.1f} L -16 {w - 6.4:.1f} Z M 21 {w - 6:.1f} Q 18 {w - 9:.1f} 15 {w - 9.6:.1f} L 16 {w - 6.4:.1f} Z" fill="#2A2630"/>'
            f'<path d="M 2 -1 Q 11 {-w - 5:.1f} 21 {w - 6:.1f}" fill="none" stroke="#FFE4B8" stroke-width="1.4"/>'
            f'<ellipse cx="0" cy="1.2" rx="2.8" ry="6" fill="{body}"/><circle cx="0.4" cy="-5" r="2.2" fill="{body}"/>'
            '<path d="M 0.6 -5.6 L 3.6 -5.0 L 0.8 -4.4 Z" fill="#E8B03A"/>'
            '<path d="M -2 3 Q 0 6 2 3" fill="none" stroke="#B8B0C0" stroke-width="1"/></g>')


def ferry(C, Xb, Xs, Z, seed):
    """Harbor ferry broadside, bow to the left, decks crowded with visitors at the rails, sunlit side."""
    from figures import person
    rnd = random.Random(seed)
    out = []
    k = C.f / Z
    x0, wl = C(Xb, 0, Z)
    x1, _ = C(Xs, 0, Z)
    L = x1 - x0

    def y(h):
        return wl - h * k
    # wake trailing to the right and a bow wave
    for j in range(16):
        t = j / 15
        xx = x1 + t * 80
        out.append(f'<ellipse cx="{xx:.1f}" cy="{wl + 1 + t * 2:.1f}" rx="{10 - t * 4:.1f}" ry="{1.4:.1f}" fill="#FFF6E6" opacity="{0.8 - t * 0.7:.2f}"/>')
    out.append(f'<path d="M {x0 - 4:.1f} {wl + 1:.1f} q 10 -4 22 0 q -10 3 -22 0 Z" fill="#FFFFFF" opacity="0.85"/>')
    # reflection
    out.append(reflect(C, [(Xb + 1, 0, Z), (Xb + 1, 6, Z), (Xs - 1, 6, Z), (Xs - 1, 0, Z)], "#F2E8E0", seed + 40, 0.5))
    out.append(reflect(C, [(Xb + 1, 0, Z), (Xb + 1, 1.2, Z), (Xs - 1, 1.2, Z), (Xs - 1, 0, Z)], "#1E3E6A", seed + 41, 0.5))
    # hull with a raked bow and a navy boot stripe
    hull = [(x0 - 3, y(3.2)), (x1, y(3.0)), (x1 - 1, wl), (x0 + 8, wl)]
    out.append(f'<polygon points="{P(hull)}" fill="#F2ECE4"/>')
    out.append(f'<polygon points="{P([(x0 + 3, wl - 1.2 * k), (x1 - 0.5, wl - 1.2 * k), (x1 - 1, wl), (x0 + 8, wl)])}" fill="#1E3E6A"/>')
    out.append(f'<line x1="{x0 - 3:.1f}" y1="{y(3.2):.1f}" x2="{x1:.1f}" y2="{y(3.0):.1f}" stroke="#C8473A" stroke-width="1.2"/>')
    # main deck cabin with a band of windows, upper deck cabin, open top deck
    d1 = [(x0 + 6, y(3.1)), (x0 + 10, y(6.0)), (x1 - 4, y(6.0)), (x1 - 4, y(3.0))]
    out.append(f'<polygon points="{P(d1)}" fill="#F7F2EA"/>')
    out.append(f'<rect x="{x0 + 12:.1f}" y="{y(5.4):.1f}" width="{L - 18:.1f}" height="{1.6 * k:.1f}" fill="#4A6488"/>')
    out.append(f'<rect x="{x0 + 12:.1f}" y="{y(5.4):.1f}" width="{L - 18:.1f}" height="{0.5 * k:.1f}" fill="#FFE2B0" opacity="0.6"/>')
    out.append(f'<rect x="{x0 + 8:.1f}" y="{y(6.3):.1f}" width="{L - 10:.1f}" height="{0.4 * k:.1f}" fill="#1E3E6A"/>')
    d2 = [(x0 + 16, y(6.3)), (x0 + 19, y(8.8)), (x1 - 10, y(8.8)), (x1 - 10, y(6.3))]
    out.append(f'<polygon points="{P(d2)}" fill="#F2ECE4"/>')
    out.append(f'<rect x="{x0 + 21:.1f}" y="{y(8.3):.1f}" width="{L - 34:.1f}" height="{1.4 * k:.1f}" fill="#4A6488"/>')
    for i in range(int((L - 34) / 6)):
        out.append(f'<rect x="{x0 + 21 + i * 6 + 4.6:.1f}" y="{y(8.3):.1f}" width="1.2" height="{1.4 * k:.1f}" fill="#F2ECE4"/>')
    out.append(f'<rect x="{x0 + 14:.1f}" y="{y(9.1):.1f}" width="{L - 22:.1f}" height="{0.35 * k:.1f}" fill="#1E3E6A"/>')
    # wheelhouse forward on the top deck
    out.append(f'<polygon points="{P([(x0 + 20, y(9.1)), (x0 + 22, y(11.0)), (x0 + 34, y(11.0)), (x0 + 34, y(9.1))])}" fill="#F7F2EA"/>')
    out.append(f'<rect x="{x0 + 23:.1f}" y="{y(10.6):.1f}" width="10" height="{0.8 * k:.1f}" fill="#2E3E5A"/>')
    # rails
    for yy, xa, xb in ((y(4.1), x0 + 2, x1 - 2), (y(7.2), x0 + 12, x1 - 6), (y(10.1), x0 + 16, x1 - 12)):
        out.append(f'<line x1="{xa:.1f}" y1="{yy:.1f}" x2="{xb:.1f}" y2="{yy:.1f}" stroke="#FFFFFF" stroke-width="0.8"/>')
    # visitors crowding the rails on the open decks, all turned toward the statue
    ppl = []
    for i in range(14):
        xx = x0 + 38 + i * (L - 52) / 13 + rnd.uniform(-1.5, 1.5)
        ppl.append(person(xx, y(9.1), 1.7 * k * rnd.uniform(0.92, 1.05), "tiny", -1, None, seed * 5 + i, rim="#FFE0B0", light=1))
    for i in range(6):
        xx = x0 + 4 + i * 3.4
        ppl.append(person(xx, y(3.1) + 0.5, 1.7 * k, "tiny", -1, None, seed * 9 + i, rim="#FFE0B0", light=1))
    out.append("".join(ppl))
    # flag at the stern
    fx = x1 - 8
    out.append(f'<line x1="{fx:.1f}" y1="{y(9.1):.1f}" x2="{fx:.1f}" y2="{y(13.5):.1f}" stroke="#3A3440" stroke-width="0.7"/>')
    out.append(f'<path d="M {fx:.1f} {y(13.5):.1f} q 3 -1 6 0.5 l 0 3.4 q -3 -1.5 -6 -0.5 Z" fill="#C8473A"/><rect x="{fx:.1f}" y="{y(13.5):.1f}" width="2.6" height="2" fill="#2E4A7A"/>')
    return "".join(out)


def liberty():
    from figures import person
    C = Cam(f=1000, cx=250, vpy=HZ, eye=EYE)
    out = [defs(
        lg(f"{U}-sky", [(0, "#3E5794"), (0.26, "#6A78B2"), (0.5, "#B49AC0"), (0.66, "#EBB6AE"), (0.78, "#FAD0A2"), (0.83, "#FDE2B6"), (1, "#FDE2B6")]),
        lg(f"{U}-skyr", [(0, "#FFD8A0", 0), (1, "#FFD8A0", 0.6)], 0, 0, 1, 0),
        lg(f"{U}-sea", [(0, "#EAC8B8"), (0.1, "#A2AACA"), (0.42, "#56729E"), (1, "#22385E")], 0, HZ, 0, 444, units="userSpaceOnUse"),
        lg(f"{U}-lawn", [(0, "#7A9A5A"), (1, "#4E6E44")]),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{U}-sky)"/>')
    out.append(glow(640, 330, 340, "#FFE2A8", f"{U}-sun", 0.75))
    # cumulus banks catching the sunrise
    out.append(cloud_bank(f"{U}-c1", puffs_row(3, 330, 560, 150, 34, 10, 26, 12), 110, 165, "#FFE6D0", "#B8A2C8", "#FFD8A8"))
    out.append(cloud_bank(f"{U}-c2", puffs_row(5, 20, 160, 196, 22, 8, 18, 9), 170, 205, "#F8DCD4", "#A898C0", "#FFD8A8"))
    out.append(cloud_bank(f"{U}-c3", puffs_row(8, 400, 600, 236, 18, 7, 15, 10), 214, 244, "#FFE8D2", "#C4ACC8", "#FFE0B0"))
    out.append('<g fill="#F6D0C8" opacity="0.5">' + "".join(f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="2.5"/>' for x, y, w in ((90, 122, 70), (140, 134, 46), (400, 92, 60), (560, 80, 40))) + "</g>")
    # far shores: New Jersey on the left, Brooklyn on the right, low in the haze
    poly, _ = (P(rough([(-10, HZ - 3), (80, HZ - 6), (160, HZ - 4), (230, HZ - 5)], 4, amp=2) + [(230, HZ + 1), (-10, HZ + 1)]), None)
    out.append(f'<polygon points="{poly}" fill="#B8A8C0"/>')
    out.append(skyline(C))
    out.append(f'<polygon points="{P(rough([(330, HZ - 2), (420, HZ - 4), (520, HZ - 3), (610, HZ - 5)], 6, amp=1.5) + [(610, HZ + 1.5), (330, HZ + 1.5)])}" fill="#A898B8"/>')
    # the harbor
    out.append(f'<rect x="0" y="{HZ}" width="600" height="{444 - HZ + 1}" fill="url(#{U}-sea)"/>')
    rnd = random.Random(2)
    rip = []
    for i in range(260):
        Z = 60 * (1.02 ** (i % 130)) * rnd.uniform(0.9, 1.1)
        X = rnd.uniform(-2, 2) * Z
        x, yy = C(X, 0, Z)
        if not (0 <= x <= 600) or yy > 444:
            continue
        w = C.f * rnd.uniform(1.5, 4) / Z
        col = rnd.choice(["#FFE8C0", "#F8C898", "#B8C4E0"]) if x > 300 else rnd.choice(["#9AA8D0", "#C8C8E4", "#2E4672"])
        rip.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{w:.1f}" height="{max(0.6, C.f * 0.12 / Z):.1f}" rx="0.4" fill="{col}" opacity="{rnd.uniform(0.35, 0.85):.2f}"/>')
    out.append("".join(rip))
    # the monument and the island trees mirrored in the harbor, broken by the swell
    out.append(reflect(C, [W(-10, 3, -10), W(-10, 47, -10), W(10, 47, -10), W(10, 3, -10)], "#F2D2B0", 3, 0.45))
    out.append(reflect(C, [(-4, 47, ZS), (-4, 80, ZS), (4, 80, ZS), (4, 47, ZS)], "#8EC2A8", 4, 0.45))
    out.append(reflect(C, [(-46, 3, ZS - 40), (-46, 11, ZS - 40), (46, 11, ZS - 40), (46, 3, ZS - 40)], "#D8BCA0", 5, 0.4))
    out.append(reflect(C, [(-230, 3, ZS + 40), (-230, 12, ZS + 40), (-60, 12, ZS - 30), (-60, 3, ZS - 30)], "#4E6A48", 6, 0.35))
    # ---- Liberty Island: granite sea wall, lawn and paths, trees, the star fort, the pedestal, the statue
    isl = [(-230, ZS + 150), (-190, ZS + 40), (-120, ZS - 30), (-55, ZS - 66), (15, ZS - 74), (62, ZS - 52), (78, ZS - 5),
           (66, ZS + 60), (10, ZS + 160), (-120, ZS + 230)]
    isl = rough(isl + [isl[0]], 17, amp=4, depth=2)[:-1]
    ring = [(x * 0.94 + 0, ZS + (z - ZS) * 0.94) for x, z in isl]
    out.append(prism(C, isl, 0.0, 3.0, "#E6CAAA", "#7A7290", seawall, top="#D8C4A8"))
    out.append(f'<polygon points="{P([C(x, 3.0, z) for x, z in ring])}" fill="url(#{U}-lawn)"/>')
    # trees around the fort: rounded crowns lit from the right, in perspective
    trees = []
    rnd = random.Random(7)
    for i in range(120):
        X = rnd.uniform(-230, 80)
        Z = rnd.uniform(ZS - 40, ZS + 230)
        if math.hypot(X, Z - ZS - 6) < 54 or (Z < ZS + 30 and X > -100):
            continue
        inside = False
        for (ax, az), (bx_, bz) in zip(ring, ring[1:] + ring[:1]):
            if (az > Z) != (bz > Z) and X < ax + (bx_ - ax) * (Z - az) / (bz - az):
                inside = not inside
        if inside:
            trees.append((Z, X, rnd.uniform(3.2, 5.2)))
    tr = []
    for Z, X, r in sorted(trees, reverse=True):
        x, yb = C(X, 3.0, Z)
        rr = r * C.f / Z
        t = [f'<ellipse cx="{x + rr * 0.4:.1f}" cy="{yb:.1f}" rx="{rr * 1.2:.1f}" ry="{rr * 0.25:.1f}" fill="#2E3E34" opacity="0.35"/>']
        for col, n, dx, dy, sc in (("#34503A", 5, 0, 0, 1.0), ("#5E8046", 4, 0.22, -0.2, 0.7), ("#A8B060", 3, 0.38, -0.42, 0.42)):
            for _ in range(n):
                a = rnd.uniform(0, 2 * math.pi)
                d = rnd.uniform(0, 0.5) * rr * sc
                t.append(f'<circle cx="{x + dx * rr + d * math.cos(a):.1f}" cy="{yb - rr + dy * rr + d * math.sin(a) * 0.8:.1f}" r="{rr * sc * rnd.uniform(0.5, 0.75):.1f}" fill="{col}"/>')
        tr.append("".join(t))
    out.append("".join(tr))
    # Fort Wood: eleven-pointed star of granite walls, facets alternating sun and shade
    st = star()
    out.append(prism(C, st, 3.0, 10.5, "#EACAA6", "#7C7290", fortwall, top="#E8D6BC"))
    inner = [(x * 0.86, ZS + 6 + (z - ZS - 6) * 0.86) for x, z in st]
    out.append(f'<polygon points="{P([C(x, 10.5, z) for x, z in inner])}" fill="#7E9A5E"/>')
    out.append(f'<polyline points="{P([C(x, 10.5, z) for x, z in st] + [C(*((st[0][0], 10.5, st[0][1])))])}" fill="none" stroke="#FFF0D8" stroke-width="0.7" opacity="0.7"/>')
    # stepped foundation and the pedestal tiers
    out.append(prism(C, square(22.0), 10.5, 14.5, "#E4D4C0", "#7E7A90"))
    out.append(prism(C, square(18.5), 14.5, 18.5, "#E4D4C0", "#7E7A90"))
    out.append(prism(C, square(15.0), 18.5, 22.0, "#E4D4C0", "#7E7A90"))
    out.append(prism(C, square(12.2), 22.0, 24.0, "#E4D4C0", "#7E7A90"))
    out.append(prism(C, square(10.6), 24.0, 26.6, "#F2CEA6", "#8A7C92"))

    def dado(C, p1, p2, Y0, Y1, nx, nz, col):
        # recessed central panel with a shadowed top edge
        (x1, z1), (x2, z2) = p1, p2
        a = [(x1 + (x2 - x1) * t, z1 + (z2 - z1) * t) for t in (0.24, 0.76)]
        q = [C(a[0][0], Y0 + 1.2, a[0][1]), C(a[0][0], Y1 - 1.0, a[0][1]), C(a[1][0], Y1 - 1.0, a[1][1]), C(a[1][0], Y0 + 1.2, a[1][1])]
        sh = [C(a[0][0], Y1 - 1.0, a[0][1]), C(a[1][0], Y1 - 1.0, a[1][1]), C(a[1][0], Y1 - 1.6, a[1][1]), C(a[0][0], Y1 - 1.6, a[0][1])]
        return (f'<polygon points="{P(q)}" fill="{mix(col, "#5A4A6A", 0.18)}"/><polygon points="{P(sh)}" fill="#3A3050" opacity="0.4"/>'
                + "".join(f'<line x1="{C(x1, yy, z1)[0]:.1f}" y1="{C(x1, yy, z1)[1]:.1f}" x2="{C(x2, yy, z2)[0]:.1f}" y2="{C(x2, yy, z2)[1]:.1f}" stroke="#5A4A6A" stroke-width="0.5" opacity="0.35"/>' for yy in (Y0 + 2.6, Y0 + 4.2, Y0 + 5.8)))

    def discs(C, p1, p2, Y0, Y1, nx, nz, col):
        (x1, z1), (x2, z2) = p1, p2
        o = []
        for i in range(8):
            t = (i + 0.5) / 8
            cx_, cy_ = C(x1 + (x2 - x1) * t, (Y0 + Y1) / 2, z1 + (z2 - z1) * t)
            o.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="1.6" fill="{mix(col, "#4A3A5A", 0.3)}"/><circle cx="{cx_ + 0.35:.1f}" cy="{cy_ - 0.3:.1f}" r="1.0" fill="{mix(col, "#FFF0D8", 0.2)}"/>')
        return "".join(o)

    def loggia(C, p1, p2, Y0, Y1, nx, nz, col):
        # recessed gallery with columns: dark openings between pale shafts
        (x1, z1), (x2, z2) = p1, p2
        o = []
        a0, a1 = 0.2, 0.8
        pa = (x1 + (x2 - x1) * a0, z1 + (z2 - z1) * a0)
        pb = (x1 + (x2 - x1) * a1, z1 + (z2 - z1) * a1)
        o.append(f'<polygon points="{P([C(pa[0], Y0 + 1.2, pa[1]), C(pa[0], Y1 - 1.2, pa[1]), C(pb[0], Y1 - 1.2, pb[1]), C(pb[0], Y0 + 1.2, pb[1])])}" fill="#3A3048"/>')
        for i in range(4):
            t = a0 + (a1 - a0) * (i + 0.5) / 4
            wa = (a1 - a0) / 4 * 0.3
            pc = (x1 + (x2 - x1) * (t - wa), z1 + (z2 - z1) * (t - wa))
            pd = (x1 + (x2 - x1) * (t + wa), z1 + (z2 - z1) * (t + wa))
            o.append(f'<polygon points="{P([C(pc[0], Y0 + 1.2, pc[1]), C(pc[0], Y1 - 1.2, pc[1]), C(pd[0], Y1 - 1.2, pd[1]), C(pd[0], Y0 + 1.2, pd[1])])}" fill="{mix(col, "#FFFFFF", 0.08)}"/>')
        o.append(f'<polygon points="{P([C(pa[0], Y1 - 1.2, pa[1]), C(pb[0], Y1 - 1.2, pb[1]), C(pb[0], Y1 - 1.9, pb[1]), C(pa[0], Y1 - 1.9, pa[1])])}" fill="#2A2238" opacity="0.5"/>')
        return "".join(o)
    out.append(prism(C, square(9.7), 26.6, 33.6, "#F2CEA6", "#8A7C92", dado))
    out.append(prism(C, square(9.9), 33.6, 35.6, "#F6D4AE", "#8E8096", discs))
    out.append(prism(C, square(9.1), 35.6, 43.0, "#F2CEA6", "#8A7C92", loggia))
    out.append(prism(C, square(9.9), 43.0, 44.6, "#FBDCB8", "#968AA0"))
    out.append(prism(C, square(9.3), 44.6, 46.4, "#F4D0AA", "#8A7C92"))
    # visitors on the crown of the pedestal
    for i, a in enumerate((-9, -4, 2, 7, 11)):
        X, Y, Z = W(a * 0.68, 46.4, -8.6)
        x, yy = C(X, Y, Z)
        out.append(f'<rect x="{x - 0.5:.1f}" y="{yy - 4:.1f}" width="1.1" height="2.6" fill="{["#C8473A", "#3E6A8A", "#E3A43E", "#F2E6D0", "#4A7A5A"][i]}"/><circle cx="{x:.1f}" cy="{yy - 4.7:.1f}" r="0.6" fill="#3A2A22"/>')
    out.append(prism(C, square(6.8), 46.4, 47.0, "#F6D4AE", "#8A7C92"))
    # the statue, at the camera's scale on top of the pedestal
    sx, sy = C(0, 47.0, ZS)
    out.append(glow(sx + 10, sy - 70, 120, "#FFE8C0", f"{U}-halo", 0.35))
    out.append(statue(sx, sy, C.f / ZS))
    # the gold-leaf flame catching the first sun
    k = C.f / ZS
    out.append(glow(sx - 4.4 * k, sy - 44.4 * k, 26, "#FFD878", f"{U}-torch", 0.55))
    # flag on the island, visitors strolling the promenade along the sea wall
    fx, fb = C(118, 3.0, ZS - 30)
    _, ft = C(118, 30, ZS - 30)
    out.append(f'<line x1="{fx:.1f}" y1="{fb:.1f}" x2="{fx:.1f}" y2="{ft:.1f}" stroke="#E8E2D8" stroke-width="1"/>')
    fl = [f'<rect x="0" y="0" width="13" height="8" fill="#F4EEE6"/>']
    for i in range(0, 7, 2):
        fl.append(f'<rect x="0" y="{i * 8 / 7:.2f}" width="13" height="{8 / 7:.2f}" fill="#C8373A"/>')
    fl.append('<rect x="0" y="0" width="5.6" height="4.3" fill="#2A3A6A"/>')
    out.append(f'<g transform="translate({fx:.1f} {ft:.1f}) skewY(8)">' + "".join(fl) + "</g>")
    vis = []
    rnd = random.Random(31)
    for i in range(14):
        k = rnd.randrange(len(isl))
        (ax, az), (bx_, bz) = isl[k], isl[(k + 1) % len(isl)]
        t = rnd.random()
        X, Z = ax + (bx_ - ax) * t, az + (bz - az) * t
        X, Z = X * 0.97, ZS + (Z - ZS) * 0.97
        if Z > ZS + 40:
            continue
        x, yb = C(X, 3.0, Z)
        vis.append((yb, person(x, yb, 1.7 * C.f / Z, "tiny", 1 if i % 2 else -1, None, 300 + i, rim="#FFE0B0", light=1)))
    out.append("".join(v for _, v in sorted(vis)))
    # ---- the ferry heading for the island
    out.append(ferry(C, 30, 74, 228, 5))
    # glints on the water toward the light, a channel buoy with a gull on it
    rnd = random.Random(13)
    gl = []
    for i in range(140):
        x = rnd.uniform(240, 600) ** 1.0
        yy = rnd.uniform(388, 444)
        w = rnd.uniform(1.5, 6) * (yy - 360) / 60
        gl.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{w:.1f}" height="{max(0.7, (yy - 360) / 60):.1f}" rx="0.5" fill="#FFF0CC" opacity="{rnd.uniform(0.35, 0.95) * (x - 200) / 400:.2f}"/>')
    out.append("".join(gl))
    bx, by = 84, 432
    out.append(f'<ellipse cx="{bx + 2}" cy="{by + 2}" rx="14" ry="2.5" fill="#1A2A4A" opacity="0.5"/>')
    out.append(f'<polygon points="{P([(bx - 7, by), (bx - 5, by - 16), (bx, by - 22), (bx + 5, by - 16), (bx + 7, by)])}" fill="#C8473A"/>')
    out.append(f'<polygon points="{P([(bx, by - 22), (bx + 5, by - 16), (bx + 7, by), (bx + 1, by)])}" fill="#E8735A"/>')
    out.append(f'<rect x="{bx - 7.5}" y="{by - 1}" width="15" height="3" fill="#2A2A36"/>')
    out.append(f'<text x="{bx - 1}" y="{by - 6}" text-anchor="middle" font-family="Anton, Impact, sans-serif" font-size="8" fill="#F6EEE4">2</text>')
    out.append(gull(bx + 1, by - 26, 10, 0.95, -1))
    for x, yy, sz, fl_, fp in ((150, 200, 14, 0.2, 1), (178, 214, 9, 0.7, 1), (420, 268, 8, 0.4, -1), (110, 262, 11, 0.85, -1), (330, 120, 7, 0.3, 1)):
        out.append(gull(x, yy, sz, fl_, fp))
    return "\n".join(out)


BUILD = {
    "statue-of-liberty": (liberty, "STATUE OF LIBERTY", "NEW YORK HARBOR · 1886", "#1E2E4E", "#F2B866", "#FBEBD4", "#9FD3BC"),
}


def build(only=None):
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        if only and slug not in only:
            continue
        poster("places", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(sys.argv[1:])
