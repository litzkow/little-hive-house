"""Bee Kind, hand-painted (gouache / storybook) edition: the shop's signature collection.

Every magnet repainted as a gouache illustration - fuzzy brush-stroked bees with translucent veined wings,
glossy honey drips, waxy honeycomb, straw skeps, honey jars and wildflowers - in honey gold, amber, cream,
warm black, sage and lavender. Each piece is its own composition with designed lettering.

Run from tools/designs:  python3 bee_kind_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from gouache import blob, blob_pts, grain, ink, jitter, paper, smooth_closed, smooth_open
from fall_gouache_b import (brush, dabs, form, glow, shadow, bg, vignette, btext, plain, hand_rule, sparkle, heart_path,
                            lgrad, wobble_line)
from poster import ANTON

COL = "bee-kind"

# ---------------------------------------------------------------- palette
INK = "#3A2418"          # warm brown pen line
NOIR = "#2A1D14"         # warm black (bee stripes, dark grounds)
PAPER = "#F7EEDC"
FLECK = "#8A6A4A"
CREAM = "#FBF3E2"
# (base, dark, light)
HONEY = ("#F2B33A", "#C47A16", "#FFDA7A")
AMBER = ("#DE8E22", "#9A5410", "#F6BC52")
GOLD = ("#F6CE5A", "#D49A22", "#FFEBA6")
SAGE = ("#A9B48A", "#6E7A50", "#D2DAB4")
LEAF = ("#7E9450", "#4E6232", "#AFC27A")
LAV = ("#A898CC", "#6E5E9A", "#D4CAEC")
ROSE = ("#E58C82", "#B05650", "#F8C0B4")
WAX = ("#F6E2B0", "#D8B676", "#FFF6DA")
WOOD = ("#C8945A", "#8A5A2E", "#E8BE86")
STRAW = ("#E2B060", "#A8742E", "#F6D896")


def _f(v):
    return f"{v:.1f}"


class Ids:
    """Unique, slug-prefixed ids (pages inline many SVGs)."""

    def __init__(self, slug):
        self.p, self.n = "bkp-" + slug, 0

    def __call__(self, tag="i"):
        self.n += 1
        return f"{self.p}-{tag}{self.n}"


def rot_pt(x, y, cx, cy, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c


def finish(u, color=INK, op=0.8, seed=9):
    return grain(u("gr"), color, seed, op)


# ================================================================ the painted bee
def bee(u, cx, cy, s, seed, rot=0, flip=False, mood="smile", wings="up", body=HONEY, stripe=NOIR, cheek="#F08A78",
        legs=True, arms=None, fuzz=True, wing_tint="#EAF4F6", shadow_op=0.0, ink_px=2.2, crown=False, eye_dir=(0, 0),
        stripes=3, pollen=False, buzz=False, under="", over="", head_over=""):
    """A fuzzy storybook bee seen from the side, head toward -x (or +x with flip).
    s = half the body length in px.  mood: smile | grin | wow | sleep | wink | calm.
    wings: up | flat | spread.  arms: None | 'forward' | 'up' | 'hug' (short dark limbs from under the head)."""
    rnd = random.Random(seed)
    k = s / 100.0                       # everything below is drawn at s=100, then scaled
    iw = lambda px: px / k               # stroke width in local units for a given on-paper px width
    o = []
    tr = f"translate({_f(cx)} {_f(cy)}) rotate({rot}) scale({'-' if flip else ''}{k:.4f} {k:.4f})"
    o.append(f'<g transform="{tr}">')
    if shadow_op:
        o.append(f'<ellipse cx="0" cy="96" rx="92" ry="12" fill="#2A1608" opacity="{shadow_op}"/>')

    def wing(cxw, cyw, rx, ry, ang, back):
        wid = u("w")
        pts = blob_pts(cxw, cyw, rx, ry, seed + int(cxw), 0.03, 16, ang)
        d = smooth_closed(pts)
        a = math.radians(ang)
        # base of wing = end of major axis nearest the body
        bx, by = cxw - ry * math.sin(-a) * 0.0, cyw + ry * 0.92
        bx, by = rot_pt(cxw, cyw + ry * 0.94, cxw, cyw, ang)
        tx, ty = rot_pt(cxw, cyw - ry * 0.94, cxw, cyw, ang)
        lx, ly = rot_pt(cxw - rx * 0.9, cyw - ry * 0.1, cxw, cyw, ang)
        rx_, ry_ = rot_pt(cxw + rx * 0.9, cyw - ry * 0.1, cxw, cyw, ang)
        mx, my = rot_pt(cxw, cyw + ry * 0.05, cxw, cyw, ang)
        veins = (f"M {_f(bx)} {_f(by)} Q {_f(mx - 6)} {_f(my)} {_f(lx)} {_f(ly)} "
                 f"M {_f(bx)} {_f(by)} Q {_f(mx)} {_f(my - 10)} {_f(tx)} {_f(ty)} "
                 f"M {_f(bx)} {_f(by)} Q {_f(mx + 8)} {_f(my)} {_f(rx_)} {_f(ry_)} ")
        c1 = rot_pt(cxw - rx * 0.6, cyw - ry * 0.35, cxw, cyw, ang)
        c2 = rot_pt(cxw + rx * 0.55, cyw - ry * 0.4, cxw, cyw, ang)
        c3 = rot_pt(cxw, cyw - ry * 0.55, cxw, cyw, ang)
        veins += f"M {_f(c1[0])} {_f(c1[1])} Q {_f(c3[0])} {_f(c3[1] - 6)} {_f(c2[0])} {_f(c2[1])} "
        hi1 = rot_pt(cxw - rx * 0.45, cyw - ry * 0.55, cxw, cyw, ang)
        hi2 = rot_pt(cxw - rx * 0.7, cyw + ry * 0.05, cxw, cyw, ang)
        hi3 = rot_pt(cxw - rx * 0.4, cyw + ry * 0.45, cxw, cyw, ang)
        op = 0.62 if back else 0.55
        r = [f'<defs><clipPath id="{wid}"><path d="{d}"/></clipPath></defs>',
             f'<path d="{d}" fill="{wing_tint}" opacity="{op}"/>',
             f'<g clip-path="url(#{wid})">',
             f'<path d="{blob(cxw + rx * 0.3, cyw + ry * 0.3, rx * 0.8, ry * 0.7, seed + 3, 0.1, 12, ang)}" fill="#BFD6E0" opacity="0.35"/>',
             brush((cxw - rx, cyw - ry, cxw + rx, cyw + ry), ["#FFFFFF", "#D6E8EE", "#FFFFFF"], seed + int(rx), 14, ang - 90,
                   (ry * 0.3, ry * 0.8), (1.5, 3.5), (0.25, 0.55), 0.2),
             "</g>",
             f'<path d="{veins}" fill="none" stroke="#6E5A4A" stroke-width="{iw(1.1):.2f}" stroke-linecap="round" opacity="0.55"/>',
             f'<path d="M {_f(hi1[0])} {_f(hi1[1])} Q {_f(hi2[0])} {_f(hi2[1])} {_f(hi3[0])} {_f(hi3[1])}" stroke="#FFFFFF" stroke-width="{iw(2.4):.2f}" fill="none" stroke-linecap="round" opacity="0.85"/>',
             ink(d, "#5A4636", iw(1.5), seed + 5, 2, 0.75)]
        return "".join(r)

    if wings == "up":
        W1, W2 = (12, -88, 30, 56, 24), (-22, -92, 34, 62, -14)
    elif wings == "spread":
        W1, W2 = (34, -78, 30, 56, 48), (-34, -84, 34, 60, -40)
    else:  # flat, swept back
        W1, W2 = (40, -62, 28, 58, 62), (14, -70, 32, 62, 42)
    o.append(wing(*W1, True))
    o.append(under)

    # ---- body (thorax + abdomen) : egg shape, fatter at the rear
    bpts = []
    for i in range(28):
        a = 2 * math.pi * i / 28
        ca, sa = math.cos(a), math.sin(a)
        rx = 100 if ca > 0 else 92
        ry = 74 * (1 + 0.06 * ca)
        bpts.append((rx * ca + 4, ry * sa + 2))
    bpts = jitter(bpts, seed, 1.2)
    bd = smooth_closed(bpts)
    sting = f"M 96 -6 Q 122 2 132 8 Q 120 12 96 14 Z"
    o.append(f'<path d="{sting}" fill="{stripe}"/>')
    # fuzz halo behind the body edge
    bodyc, bdark, blight = body

    BANDS = {3: ((-10, 12), (36, 58), (84, 140)), 2: ((-4, 20), (48, 72)), 1: ((14, 38),)}
    CURV = -0.0045

    def band_at(x):
        return any(b0 <= x <= b1 for b0, b1 in BANDS[stripes])

    if fuzz:
        fz = {}
        for i in range(190):
            a = 2 * math.pi * i / 190 + rnd.uniform(-0.02, 0.02)
            ca, sa = math.cos(a), math.sin(a)
            rx = 100 if ca > 0 else 92
            ry = 74 * (1 + 0.06 * ca)
            x, y = rx * ca + 4, ry * sa + 2
            col = stripe if band_at(x - CURV * y * y) else rnd.choice([bodyc, bdark, blight, bodyc])
            L = rnd.uniform(3, 7)
            da = a + rnd.uniform(-0.35, 0.35)
            nx, ny = math.cos(da), math.sin(da)
            w = rnd.uniform(1.0, 2.0)
            sx, sy = x - nx * 4, y - ny * 4
            ex, ey = sx + nx * (L + 4), sy + ny * (L + 4)
            px, py = -ny * w, nx * w
            fz.setdefault(col, []).append(f"M{_f(sx + px)} {_f(sy + py)}L{_f(ex)} {_f(ey)}L{_f(sx - px)} {_f(sy - py)}Z")
        o.append("".join(f'<path d="{"".join(v)}" fill="{c}" opacity="0.85"/>' for c, v in fz.items()))
    # painted body with radial strokes
    stripe_paths = []
    for b0, b1 in BANDS[stripes]:
        pts = [(b0 + CURV * y * y, y) for y in range(-90, 91, 15)] + [(b1 + CURV * y * y, y) for y in range(90, -91, -15)]
        stripe_paths.append(smooth_closed(jitter(pts, seed + b0, 1.6)))
    sid = u("st")
    stripes_svg = (f'<path d="{" ".join(stripe_paths)}" fill="{stripe}"/>' +
                   f'<clipPath id="{sid}"><path d="{" ".join(stripe_paths)}"/></clipPath><g clip-path="url(#{sid})">' +
                   brush((-100, -90, 120, 90), ["#4A3626", "#1A120C", "#5E4632"], seed + 7, 70, lambda x, y: math.degrees(math.atan2(y, x)),
                         (8, 22), (1.4, 3.2), (0.3, 0.6), 0.2) + "</g>")
    o.append(form(u, bd, (-96, -76, 106, 80), bodyc, bdark, blight, seed + 1, lambda x, y: math.degrees(math.atan2(y, x - 4)),
                  n=220, shade=(-2, 20), shade_op=0.55, hi=(-10, -40, 46, 20), hi_op=0.5, ink_w=0, length=(8, 24), width=(1.4, 3.4),
                  extra_in=stripes_svg + f'<path d="{blob(10, 52, 90, 26, seed + 4, 0.1, 14)}" fill="{NOIR}" opacity="0.18"/>'
                  + f'<path d="M -60 -50 Q -10 -70 50 -56" stroke="#FFF2C8" stroke-width="7" fill="none" stroke-linecap="round" opacity="0.45"/>'))
    o.append(ink(bd, INK, iw(ink_px), seed + 2, 2, 0.8))
    if pollen:
        o.append(f'<path d="{blob(40, 74, 16, 11, seed + 9, 0.15, 10)}" fill="#F08A2A"/><path d="{blob(36, 70, 6, 4, seed + 9, 0.2, 8)}" fill="#FFD08A"/>')

    # ---- legs
    if legs:
        L = []
        for lx, sw in ((-50, -1), (-10, 0), (32, 1)):
            L.append(f"M {lx} 62 q {-4 + sw * 3} 12 {-10 + sw * 4} 20 l -7 1")
        o.append(f'<path d="{" ".join(L)}" stroke="{NOIR}" stroke-width="{max(5.0, iw(3.8)):.2f}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    # ---- head
    hx, hy, hr = -98, -6, 52
    hd = blob(hx, hy, hr, hr * 0.96, seed + 11, 0.03, 16)
    if fuzz:
        hz = []
        for i in range(90):
            a = 2 * math.pi * i / 90 + rnd.uniform(-0.03, 0.03)
            x, y = hx + hr * math.cos(a), hy + hr * 0.96 * math.sin(a)
            Lz = rnd.uniform(2, 5)
            da = a + rnd.uniform(-0.4, 0.4)
            nx, ny = math.cos(da), math.sin(da)
            w = rnd.uniform(0.9, 1.8)
            sx, sy = x - nx * 3, y - ny * 3
            hz.append(f"M{_f(sx - ny * w)} {_f(sy + nx * w)}L{_f(sx + nx * (Lz + 3))} {_f(sy + ny * (Lz + 3))}L{_f(sx + ny * w)} {_f(sy - nx * w)}Z")
        o.append(f'<path d="{"".join(hz)}" fill="{stripe}" opacity="0.9"/>')
    o.append(form(u, hd, (hx - hr, hy - hr, hx + hr, hy + hr), stripe, "#120C08", "#5E4632", seed + 12,
                  lambda x, y: math.degrees(math.atan2(y - hy, x - hx)), n=70, shade=(-6, 10), shade_op=0.6, hi=(hx - 10, hy - 26, 20, 10),
                  hi_op=0.45, ink_w=iw(1.4), ink_col="#120C08", length=(6, 16), width=(1.2, 3)))
    # antennae
    for ax0, ay0, ax1, ay1, cxx, cyy in ((-112, -50, -150, -112, -118, -96), (-82, -54, -84, -124, -70, -96)):
        o.append(ink(f"M {ax0} {ay0} Q {cxx} {cyy} {ax1} {ay1}", stripe, iw(3.4), seed + ax0, 1, 1))
        o.append(f'<circle cx="{ax1}" cy="{ay1}" r="{max(7, iw(4.2)):.1f}" fill="{stripe}"/><circle cx="{ax1 - 2}" cy="{ay1 - 2}" r="{max(2, iw(1.4)):.1f}" fill="#8A7060"/>')
    if crown:
        cr = "M -130 -44 L -136 -96 L -116 -74 L -98 -108 L -80 -74 L -60 -96 L -66 -44 Q -98 -36 -130 -44 Z"
        o.append(form(u, cr, (-138, -110, -58, -40), GOLD[0], GOLD[1], GOLD[2], seed + 21, -80, n=40, shade=(-4, 6), ink_w=iw(1.8),
                      ink_col="#7A4A0E", length=(6, 16), width=(1, 2.4)))
        for jx, jy, jc in ((-98, -60, "#C8344A"), (-120, -58, "#5E8ACA"), (-76, -58, "#5E8ACA")):
            o.append(f'<circle cx="{jx}" cy="{jy}" r="{max(5, iw(2.6)):.1f}" fill="{jc}"/><circle cx="{jx - 1.5}" cy="{jy - 1.5}" r="{max(1.5, iw(1)):.1f}" fill="#FFFFFF" opacity="0.8"/>')
        for px, py in ((-136, -96), (-98, -108), (-60, -96)):
            o.append(f'<circle cx="{px}" cy="{py}" r="{max(5, iw(2.4)):.1f}" fill="{GOLD[2]}" stroke="#7A4A0E" stroke-width="{iw(1.2):.2f}"/>')
    # face
    ex, ey = -118 + eye_dir[0], -14 + eye_dir[1]
    if mood == "sleep":
        o.append(f'<path d="M {ex - 13} {ey} Q {ex} {ey + 11} {ex + 13} {ey}" stroke="#FFF2D8" stroke-width="{iw(3):.2f}" fill="none" stroke-linecap="round"/>')
        o.append(f'<path d="M {ex - 12} {ey + 4} l -6 5 M {ex - 4} {ey + 8} l -3 6 M {ex + 5} {ey + 8} l 0 6" stroke="#FFF2D8" stroke-width="{iw(1.8):.2f}" stroke-linecap="round"/>')
    elif mood == "wink":
        o.append(f'<path d="M {ex - 12} {ey + 2} Q {ex} {ey - 10} {ex + 12} {ey + 2}" stroke="#FFF2D8" stroke-width="{iw(3.2):.2f}" fill="none" stroke-linecap="round"/>')
    else:
        er = 19 if mood == "wow" else 16
        o.append(f'<ellipse cx="{ex}" cy="{ey}" rx="{er}" ry="{er * 1.08:.1f}" fill="#FFF8EC"/>')
        px, py = ex - 4 + eye_dir[0] * 0.3, ey + 1 + eye_dir[1] * 0.3
        pr = 9 if mood == "wow" else 11
        o.append(f'<ellipse cx="{px}" cy="{py}" rx="{pr}" ry="{pr * 1.1:.1f}" fill="#1A100A"/>')
        o.append(f'<circle cx="{px - 3.5}" cy="{py - 4.5}" r="4.2" fill="#FFFFFF"/><circle cx="{px + 3}" cy="{py + 4}" r="1.8" fill="#FFFFFF" opacity="0.8"/>')
        if mood != "calm":
            o.append(f'<path d="M {ex - 12} {ey - er - 6} q 10 -8 22 -2" stroke="#120C08" stroke-width="{iw(2):.2f}" fill="none" stroke-linecap="round" opacity="0.6"/>')
    o.append(f'<ellipse cx="{ex + 16}" cy="{ey + 24}" rx="13" ry="8" fill="{cheek}" opacity="0.75"/>')
    mx, my = -130, 22
    if mood in ("smile", "sleep", "wink", "calm"):
        o.append(f'<path d="M {mx - 6} {my} Q {mx + 6} {my + 12} {mx + 18} {my + 2}" stroke="#FFE6CC" stroke-width="{iw(2.6):.2f}" fill="none" stroke-linecap="round"/>')
    elif mood == "grin":
        o.append(f'<path d="M {mx - 8} {my - 2} Q {mx + 6} {my + 20} {mx + 22} {my} Q {mx + 6} {my + 6} {mx - 8} {my - 2} Z" fill="#7A2A22" stroke="#FFE6CC" stroke-width="{iw(1.6):.2f}"/>')
    elif mood == "wow":
        o.append(f'<ellipse cx="{mx + 6}" cy="{my + 6}" rx="7" ry="9" fill="#7A2A22" stroke="#FFE6CC" stroke-width="{iw(1.6):.2f}"/>')
    # arms
    if arms:
        if arms == "forward":
            A = ["M -70 40 q -24 10 -40 4", "M -52 48 q -22 18 -40 16"]
        elif arms == "up":
            A = ["M -70 36 q -26 -10 -38 -34", "M -54 44 q -30 -2 -48 -22"]
        elif arms == "hug":
            A = ["M -70 34 q -30 -4 -46 -22", "M -56 46 q -34 4 -52 -10"]
        else:
            A = arms
        o.append(f'<path d="{" ".join(A)}" stroke="{NOIR}" stroke-width="{iw(4.4):.2f}" fill="none" stroke-linecap="round"/>')
    o.append(head_over)
    o.append(wing(*W2, False))
    o.append(over)
    if buzz:
        o.append(f'<path d="M 150 -40 q 10 -6 18 0 M 156 -20 q 12 -4 22 2 M 150 0 q 10 2 18 8" stroke="{INK}" stroke-width="{iw(2):.2f}" fill="none" stroke-linecap="round" opacity="0.6"/>')
    o.append("</g>")
    return "".join(o)


def bee_pt(cx, cy, s, rot, flip, lx, ly):
    """Where a point given in the bee's local (s=100) coordinates lands on the page."""
    k = s / 100.0
    x, y = (-lx if flip else lx) * k, ly * k
    a = math.radians(rot)
    return cx + x * math.cos(a) - y * math.sin(a), cy + x * math.sin(a) + y * math.cos(a)


def trail(pts, color=INK, w=2.4, dash="2 9", op=0.6):
    """Dotted flight path behind a bee."""
    return f'<path d="{smooth_open(pts)}" fill="none" stroke="{color}" stroke-width="{w}" stroke-dasharray="{dash}" stroke-linecap="round" opacity="{op}"/>'


def loop_trail(x0, y0, x1, y1, loop_r=26, color=INK, w=2.4, op=0.6, up=True):
    """Dotted path with a loop-the-loop in the middle."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    sg = -1 if up else 1
    pts = [(x0, y0), ((x0 + mx) / 2, (y0 + my) / 2 + 10 * sg), (mx - loop_r * 0.2, my), (mx + loop_r * 0.7, my + sg * loop_r * 1.4),
           (mx - loop_r * 0.4, my + sg * loop_r * 2.0), (mx - loop_r * 0.9, my + sg * loop_r * 1.0), (mx + loop_r * 0.4, my + sg * 2),
           ((mx + x1) / 2, (my + y1) / 2 - 6 * sg), (x1, y1)]
    return trail(pts, color, w, "2 9", op)


# ================================================================ honey: drips, puddles, comb, jars, dippers
def drip_curtain(u, y0, y_top, seed, x0=-20, x1=620, depth=(30, 150), wid=(44, 80), base=AMBER, body_dark="#8A4A0A", hi="#FFF2C8",
                 gloss=True, ink_col="#6A3608", p_drip=0.62, band_hi=True):
    """Honey running down from the top edge: a wavy band whose lower edge breaks into rounded drips."""
    rnd = random.Random(seed)
    pts = [(x0, y_top), (x0, y0)]
    x = x0
    drips = []
    while x < x1:
        w = rnd.uniform(*wid)
        if rnd.random() < p_drip:
            dd = rnd.uniform(*depth)
            yb = y0 + rnd.uniform(-6, 6)
            pts += [(x + w * 0.2, yb + w * 0.1), (x + w * 0.3, yb + dd * 0.45), (x + w * 0.27, yb + dd - w * 0.05),
                    (x + w * 0.36, yb + dd + w * 0.22), (x + w * 0.5, yb + dd + w * 0.3), (x + w * 0.64, yb + dd + w * 0.22),
                    (x + w * 0.73, yb + dd - w * 0.05), (x + w * 0.7, yb + dd * 0.45), (x + w * 0.8, yb + w * 0.1), (x + w, yb + rnd.uniform(-4, 4))]
            drips.append((x + w * 0.5, yb, dd, w))
        else:
            pts += [(x + w * 0.5, y0 + rnd.uniform(0, 14)), (x + w, y0 + rnd.uniform(-6, 6))]
        x += w
    pts += [(x1 + 20, y0), (x1 + 20, y_top)]
    d = smooth_closed(pts)
    g = u("hg")
    yb_max = y0 + depth[1] + wid[1] * 0.4
    out = [f'<defs>{lgrad(g, [(0, base[2]), (0.45, base[0]), (1, base[1])], 0, 0, 0, 1)}</defs>']
    out.append(f'<path d="{d}" fill="{body_dark}" opacity="0.22" transform="translate(3 7)"/>')
    out.append(form(u, d, (x0, y_top, x1, yb_max), base[0], base[1], base[2], seed + 1, -90, n=200, shade=(-8, -10), shade_op=0.4,
                    ink_w=2.2, ink_col=ink_col, ink_op=0.7, length=(14, 50), width=(1.6, 4), sop=(0.1, 0.28),
                    extra_in=f'<rect x="{x0 - 30}" y="{y_top}" width="{x1 - x0 + 60}" height="{yb_max - y_top}" fill="url(#{g})" opacity="0.5"/>'))
    if gloss:
        hl = []
        for cxd, yb, dd, w in drips:
            if dd > w * 0.5:
                hl.append(f'<path d="M {_f(cxd - w * 0.12)} {_f(yb + w * 0.3)} Q {_f(cxd - w * 0.15)} {_f(yb + dd * 0.6)} {_f(cxd - w * 0.13)} {_f(yb + dd - w * 0.05)}" stroke="{hi}" stroke-width="{max(2.4, w * 0.08):.1f}" stroke-linecap="round" fill="none" opacity="0.8"/>')
            hl.append(f'<ellipse cx="{_f(cxd - w * 0.08)}" cy="{_f(yb + dd + w * 0.16)}" rx="{max(2.2, w * 0.06):.1f}" ry="{max(3, w * 0.09):.1f}" fill="#FFFFFF" opacity="0.9"/>')
        if band_hi:
            for hx0 in range(int(x0) + rnd.randint(20, 80), int(x1) - 60, 150):
                L = rnd.uniform(40, 90)
                hl.append(f'<path d="M {hx0} {_f(y0 - 18)} q {_f(L / 2)} -6 {_f(L)} -2" stroke="{hi}" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.55"/>')
        out.append("".join(hl))
    return "".join(out)


def honey_blob(u, d, box, seed, base=AMBER, ink_col="#6A3608", hi=None, angle=-90, n=None, shade=(-4, -6)):
    """A glossy honey shape (puddle, drop, drizzle) - wash + strokes + white gloss."""
    o = [form(u, d, box, base[0], base[1], base[2], seed, angle, n=n, shade=shade, shade_op=0.5, ink_w=1.8, ink_col=ink_col, ink_op=0.7,
              sop=(0.12, 0.32), hi=hi, hi_op=0.55)]
    return "".join(o)


def drop(u, cx, cy, s, seed, base=AMBER):
    """A single honey drop (teardrop) with a gloss highlight."""
    d = f"M {_f(cx)} {_f(cy - s * 1.5)} Q {_f(cx + s * 0.25)} {_f(cy - s * 0.6)} {_f(cx + s)} {_f(cy + s * 0.15)} A {_f(s)} {_f(s)} 0 1 1 {_f(cx - s)} {_f(cy + s * 0.15)} Q {_f(cx - s * 0.25)} {_f(cy - s * 0.6)} {_f(cx)} {_f(cy - s * 1.5)} Z"
    return (form(u, d, (cx - s, cy - s * 1.5, cx + s, cy + s * 1.2), base[0], base[1], base[2], seed, -90, n=max(6, s * 2), shade=(-s * 0.2, -s * 0.2),
                 ink_w=max(1.2, s * 0.08), ink_col="#6A3608", length=(s * 0.3, s * 0.8), width=(0.8, max(1.2, s * 0.08))) +
            f'<ellipse cx="{_f(cx - s * 0.38)}" cy="{_f(cy + s * 0.1)}" rx="{_f(s * 0.16)}" ry="{_f(s * 0.32)}" fill="#FFFFFF" opacity="0.8" transform="rotate(20 {_f(cx - s * 0.38)} {_f(cy + s * 0.1)})"/>')


def hex_pts(cx, cy, r, flat=False):
    off = 0 if flat else -90
    return [(cx + r * math.cos(math.radians(off + 60 * i)), cy + r * math.sin(math.radians(off + 60 * i))) for i in range(6)]


def poly_d(pts, close=True):
    return "M " + " L ".join(f"{_f(x)} {_f(y)}" for x, y in pts) + (" Z" if close else "")


def soft_poly(pts, seed, amt=1.2, round_k=0.18):
    """Hand-drawn polygon: jittered corners, slightly rounded."""
    pts = jitter(pts, seed, amt)
    n = len(pts)
    d = []
    for i in range(n):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        a = (p1[0] + (p0[0] - p1[0]) * round_k, p1[1] + (p0[1] - p1[1]) * round_k)
        b = (p1[0] + (p2[0] - p1[0]) * round_k, p1[1] + (p2[1] - p1[1]) * round_k)
        d.append(("M" if i == 0 else "L") + f" {_f(a[0])} {_f(a[1])} Q {_f(p1[0])} {_f(p1[1])} {_f(b[0])} {_f(b[1])}")
    return " ".join(d) + " Z"


def comb_cells(cx, cy, r, rows, cols, flat=False, keep=None):
    """Centres of a hex grid (pointy-top by default)."""
    out = []
    if flat:
        dx, dy = 1.5 * r, math.sqrt(3) * r
        for c in range(cols):
            for rr in range(rows):
                x = cx + (c - (cols - 1) / 2) * dx
                y = cy + (rr - (rows - 1) / 2) * dy + (dy / 2 if c % 2 else 0)
                if keep is None or keep(x, y, c, rr):
                    out.append((x, y))
    else:
        dx, dy = math.sqrt(3) * r, 1.5 * r
        for rr in range(rows):
            for c in range(cols):
                x = cx + (c - (cols - 1) / 2) * dx + (dx / 2 if rr % 2 else 0)
                y = cy + (rr - (rows - 1) / 2) * dy
                if keep is None or keep(x, y, c, rr):
                    out.append((x, y))
    return out


def comb_cell(u, x, y, r, kind, seed, flat=False, wax=WAX, honey=AMBER, rim_w=None, ink_col="#7A4A16", light=(-1, -1)):
    """One painted honeycomb cell. kind: honey | capped | empty | dark."""
    rnd = random.Random(seed)
    rim_w = rim_w or max(2.0, r * 0.16)
    outer = soft_poly(hex_pts(x, y, r, flat), seed, max(0.4, r * 0.03), 0.16)
    inner = soft_poly(hex_pts(x, y, r - rim_w, flat), seed + 1, max(0.4, r * 0.035), 0.24)
    o = [f'<path d="{outer}" fill="{wax[1]}"/>', f'<path d="{outer}" fill="{wax[0]}" transform="translate({_f(light[0] * 1.2)} {_f(light[1] * 1.2)})" opacity="0.8"/>']
    ri = r - rim_w
    if kind == "honey":
        g = u("ch")
        o.append(f'<defs><radialGradient id="{g}" cx="0.36" cy="0.32" r="0.8"><stop offset="0" stop-color="{honey[2]}"/><stop offset="0.5" stop-color="{honey[0]}"/>'
                 f'<stop offset="1" stop-color="{honey[1]}"/></radialGradient></defs><path d="{inner}" fill="url(#{g})"/>')
        o.append(f'<path d="{blob(x + ri * 0.15, y + ri * 0.2, ri * 0.55, ri * 0.4, seed + 2, 0.15, 10)}" fill="{honey[1]}" opacity="0.35"/>')
        o.append(f'<path d="M {_f(x - ri * 0.55)} {_f(y - ri * 0.1)} Q {_f(x - ri * 0.45)} {_f(y - ri * 0.55)} {_f(x - ri * 0.02)} {_f(y - ri * 0.62)}" stroke="#FFFFFF" stroke-width="{max(1.6, ri * 0.13):.1f}" fill="none" stroke-linecap="round" opacity="0.8"/>')
        o.append(f'<circle cx="{_f(x + ri * 0.35)}" cy="{_f(y + ri * 0.35)}" r="{max(1, ri * 0.07):.1f}" fill="#FFFFFF" opacity="0.6"/>')
    elif kind == "capped":
        g = u("cc")
        o.append(f'<defs><radialGradient id="{g}" cx="0.38" cy="0.35" r="0.75"><stop offset="0" stop-color="{wax[2]}"/><stop offset="0.6" stop-color="{wax[0]}"/>'
                 f'<stop offset="1" stop-color="{wax[1]}"/></radialGradient></defs><path d="{inner}" fill="url(#{g})"/>')
        o.append(dabs((x - ri * 0.7, y - ri * 0.7, x + ri * 0.7, y + ri * 0.7), [wax[1], "#FFFFFF", wax[2]], seed + 3, ri * 0.5, (max(0.6, ri * 0.05), max(1, ri * 0.1)), (0.2, 0.5)))
        o.append(f'<path d="M {_f(x - ri * 0.4)} {_f(y - ri * 0.25)} Q {_f(x - ri * 0.1)} {_f(y - ri * 0.5)} {_f(x + ri * 0.25)} {_f(y - ri * 0.42)}" stroke="#FFFFFF" stroke-width="{max(1.2, ri * 0.09):.1f}" fill="none" stroke-linecap="round" opacity="0.7"/>')
    elif kind == "empty":
        g = u("ce")
        o.append(f'<defs><radialGradient id="{g}" cx="0.6" cy="0.62" r="0.8"><stop offset="0" stop-color="#E8B868"/><stop offset="0.7" stop-color="#B87A2E"/>'
                 f'<stop offset="1" stop-color="#8A5218"/></radialGradient></defs><path d="{inner}" fill="url(#{g})"/>')
        o.append(f'<path d="{soft_poly(hex_pts(x + ri * 0.12, y + ri * 0.12, ri * 0.55, flat), seed + 4, 0.5, 0.3)}" fill="#7A4614" opacity="0.35"/>')
    else:  # dark (deep cell)
        o.append(f'<path d="{inner}" fill="#6A3A10"/><path d="{soft_poly(hex_pts(x + ri * 0.15, y + ri * 0.15, ri * 0.6, flat), seed + 4, 0.5, 0.3)}" fill="#3E200A" opacity="0.6"/>')
    # wax rim texture + ink
    o.append(f'<path d="{outer}" fill="none" stroke="{ink_col}" stroke-width="{max(1.2, r * 0.05):.2f}" stroke-linejoin="round" opacity="0.7"/>')
    o.append(f'<path d="{inner}" fill="none" stroke="{ink_col}" stroke-width="{max(0.9, r * 0.03):.2f}" stroke-linejoin="round" opacity="0.45"/>')
    return "".join(o)


def comb(u, cells, r, seed, kinds=None, flat=False, wax=WAX, honey=AMBER, ink_col="#7A4A16", texture=True):
    """A slab of painted comb from a list of cell centres. kinds: function(i, x, y) -> kind, or list."""
    rnd = random.Random(seed)
    o = []
    for i, (x, y) in enumerate(cells):
        if callable(kinds):
            kd = kinds(i, x, y)
        elif kinds:
            kd = kinds[i % len(kinds)]
        else:
            kd = rnd.choice(["honey", "honey", "capped", "empty"])
        o.append(comb_cell(u, x, y, r, kd, seed + i * 3, flat, wax, honey, ink_col=ink_col))
    return "".join(o)


def dipper(u, x, y, length, ang, seed, wood=WOOD, honey=True, scale=1.0):
    """Wooden honey dipper: handle from (x,y) along angle ang (deg, 0 = right), grooved head at the far end."""
    s = scale
    o = [f'<g transform="translate({_f(x)} {_f(y)}) rotate({ang})">']
    L = length
    hd = f"M 0 {-5 * s} Q {L * 0.5} {-6 * s} {L - 60 * s} {-5 * s} L {L - 60 * s} {5 * s} Q {L * 0.5} {6 * s} 0 {5 * s} Q {-6 * s} 0 0 {-5 * s} Z"
    o.append(form(u, hd, (-6 * s, -7 * s, L - 58 * s, 7 * s), wood[0], wood[1], wood[2], seed, 0, n=L * 0.3, shade=(0, -3 * s), ink_w=1.8,
                  ink_col="#5A3416", length=(10 * s, 30 * s), width=(0.6, 1.6)))
    # head: a stack of rounded discs
    hx = L - 60 * s
    head = smooth_closed([(hx - 4 * s, -10 * s), (hx + 8 * s, -22 * s), (hx + 30 * s, -26 * s), (hx + 52 * s, -22 * s), (hx + 64 * s, -12 * s),
                          (hx + 64 * s, 12 * s), (hx + 52 * s, 22 * s), (hx + 30 * s, 26 * s), (hx + 8 * s, 22 * s), (hx - 4 * s, 10 * s)])
    groove = "".join(f'<path d="M {_f(hx + gx * s)} {_f(-24 * s)} Q {_f(hx + gx * s + 4 * s)} 0 {_f(hx + gx * s)} {_f(24 * s)}" stroke="#6A3E18" stroke-width="{2.6 * s:.1f}" fill="none" opacity="0.7"/>'
                     for gx in (10, 22, 34, 46))
    o.append(form(u, head, (hx - 6 * s, -28 * s, hx + 66 * s, 28 * s), wood[0], wood[1], wood[2], seed + 1, -90, n=50, shade=(0, -6 * s), shade_op=0.5,
                  hi=(hx + 26 * s, -14 * s, 22 * s, 5 * s), ink_w=2.0, ink_col="#5A3416", length=(6 * s, 16 * s), width=(0.8, 2), extra_in=groove))
    if honey:
        hn = smooth_closed([(hx + 4 * s, 4 * s), (hx + 30 * s, 10 * s), (hx + 60 * s, 4 * s), (hx + 66 * s, 16 * s), (hx + 50 * s, 30 * s), (hx + 30 * s, 32 * s),
                            (hx + 10 * s, 28 * s), (hx, 16 * s)])
        o.append(form(u, hn, (hx, 2 * s, hx + 66 * s, 34 * s), AMBER[0], AMBER[1], AMBER[2], seed + 2, -90, n=30, shade=(0, -4 * s), ink_w=1.6,
                      ink_col="#6A3608", length=(4 * s, 12 * s), width=(0.8, 2)))
        o.append(f'<path d="M {_f(hx + 12 * s)} {_f(16 * s)} Q {_f(hx + 30 * s)} {_f(22 * s)} {_f(hx + 50 * s)} {_f(16 * s)}" stroke="#FFF4D0" stroke-width="{2.6 * s:.1f}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    o.append("</g>")
    return "".join(o)


def skep(u, cx, base, w, h, seed, door=True, straw=STRAW, ink_col="#6A4214", coils=None, sag=0.22, stitch=True):
    """A woven straw skep hive: a dome of fat rolled straw coils, each painted with twisted straw strokes."""
    rnd = random.Random(seed)
    coils = coils or max(5, int(h / 44))
    bh = h / (coils + 0.35)
    o = [shadow(u, cx + w * 0.06, base + 6, w * 0.64, h * 0.07, 0.4)]
    hw = lambda t: w / 2 * max(0.0, 1 - t ** 2.6) ** 0.5
    shapes = []
    for i in range(coils):
        yc = base - bh * (i + 0.5)
        t = (base - yc) / h
        half = max(hw(t), w * 0.12) + bh * 0.08
        sg = bh * sag * (half / (w / 2))
        top = [(cx + half * (2 * j / 8 - 1), yc - bh * 0.56 + sg * (1 - (2 * j / 8 - 1) ** 2)) for j in range(9)]
        bot = [(cx + half * (1 - 2 * j / 8), yc + bh * 0.56 + sg * (1 - (1 - 2 * j / 8) ** 2)) for j in range(9)]
        pts = top + [(cx + half + bh * 0.42, yc + sg * 0.1)] + bot + [(cx - half - bh * 0.42, yc + sg * 0.1)]
        shapes.append((yc, half, sg, smooth_closed(jitter(pts, seed + i, 1.0))))
    # cap
    yc_top = base - bh * coils - bh * 0.1
    capd = blob(cx, yc_top + bh * 0.1, w * 0.1, bh * 0.45, seed + 99, 0.05, 12)
    o.append(form(u, capd, (cx - w * 0.12, yc_top - bh * 0.5, cx + w * 0.12, yc_top + bh * 0.6), straw[0], straw[1], straw[2], seed + 98, 60,
                  n=20, shade=(-3, -4), ink_w=2.0, ink_col=ink_col, length=(4, 12), width=(0.8, 1.8)))
    for i, (yc, half, sg, d) in reversed(list(enumerate(shapes))):
        x0, x1 = cx - half - bh * 0.5, cx + half + bh * 0.5
        y0, y1 = yc - bh * 0.6, yc + bh * 0.6 + sg
        cid, g = u("kc"), u("kg")
        o.append(f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{straw[2]}"/><stop offset="0.45" stop-color="{straw[0]}"/>'
                 f'<stop offset="1" stop-color="{straw[1]}"/></linearGradient><linearGradient id="{g}x" x1="0" x2="1"><stop offset="0" stop-color="#FFF4D0" stop-opacity="0.35"/>'
                 f'<stop offset="0.35" stop-color="#FFF4D0" stop-opacity="0"/><stop offset="0.7" stop-color="#5A3008" stop-opacity="0"/><stop offset="1" stop-color="#5A3008" stop-opacity="0.45"/></linearGradient>'
                 f'<clipPath id="{cid}"><path d="{d}"/></clipPath></defs>')
        o.append(f'<path d="{d}" fill="url(#{g})"/>')
        o.append(f'<g clip-path="url(#{cid})">')
        o.append(brush((x0, y0, x1, y1), [straw[2], straw[1], "#FFF0C0", "#C08A3A", straw[0]], seed + i * 5, (x1 - x0) * bh / 70, 62,
                       (bh * 0.45, bh * 1.0), (0.9, 2.2), (0.35, 0.85), 0.12, 8))
        o.append(f'<rect x="{_f(x0)}" y="{_f(y0)}" width="{_f(x1 - x0)}" height="{_f(y1 - y0)}" fill="url(#{g}x)"/>')
        if stitch:
            for sx in range(int(cx - half) + rnd.randint(4, 30), int(cx + half - 6), 44):
                rel = (sx - cx) / max(half, 1)
                sy = yc + sg * (1 - rel ** 2) * 0.6
                o.append(f'<path d="M {sx - 4} {_f(sy - bh * 0.42)} q 6 {_f(bh * 0.4)} 2 {_f(bh * 0.84)}" stroke="{straw[1]}" stroke-width="3.2" fill="none" stroke-linecap="round" opacity="0.9"/>'
                         f'<path d="M {sx - 2} {_f(sy - bh * 0.42)} q 6 {_f(bh * 0.4)} 2 {_f(bh * 0.84)}" stroke="#FFF0C0" stroke-width="1.2" fill="none" stroke-linecap="round" opacity="0.6"/>')
        o.append("</g>")
        o.append(ink(d, ink_col, 2.0, seed + i, 1, 0.7))
    if door:
        dw, dh = w * 0.13, bh * 0.95
        dd = f"M {_f(cx - dw)} {_f(base + 2)} Q {_f(cx - dw)} {_f(base - dh)} {_f(cx)} {_f(base - dh)} Q {_f(cx + dw)} {_f(base - dh)} {_f(cx + dw)} {_f(base + 2)} Z"
        o.append(f'<path d="{dd}" fill="#2A160A"/>' + ink(dd, ink_col, 2.4, seed + 7, 1, 0.9))
    return "".join(o)


def mixc(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(a[i] + (b[i] - a[i]) * t):02X}" for i in range(3))


# ================================================================ flowers & greenery
def stem(pts, color="#5E7A3A", w=3.0, seed=1):
    return ink(smooth_open(pts), color, w, seed, 1, 1)


def leaf_shape(x, y, L, wd, ang, seed):
    """Simple lanceolate leaf from base (x,y) pointing at angle ang (deg)."""
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    nx, ny = -sa, ca
    tip = (x + ca * L, y + sa * L)
    pts = [(x, y), (x + ca * L * 0.35 + nx * wd, y + sa * L * 0.35 + ny * wd), (x + ca * L * 0.75 + nx * wd * 0.6, y + sa * L * 0.75 + ny * wd * 0.6), tip,
           (x + ca * L * 0.75 - nx * wd * 0.6, y + sa * L * 0.75 - ny * wd * 0.6), (x + ca * L * 0.35 - nx * wd, y + sa * L * 0.35 - ny * wd)]
    return smooth_closed(jitter(pts, seed, 0.6)), tip


def green_leaf(u, x, y, L, wd, ang, seed, pal=LEAF, vein=True, inkc="#34461E"):
    d, tip = leaf_shape(x, y, L, wd, ang, seed)
    o = form(u, d, (min(x, tip[0]) - wd, min(y, tip[1]) - wd, max(x, tip[0]) + wd, max(y, tip[1]) + wd), pal[0], pal[1], pal[2], seed, ang,
             n=max(6, L * wd / 30), shade=(math.cos(math.radians(ang + 90)) * wd * 0.3, math.sin(math.radians(ang + 90)) * wd * 0.3), shade_op=0.45,
             ink_w=max(1.0, wd * 0.12), ink_col=inkc, ink_op=0.7, length=(L * 0.2, L * 0.5), width=(0.8, max(1.2, wd * 0.15)))
    if vein:
        o += f'<path d="M {_f(x)} {_f(y)} L {_f(x + (tip[0] - x) * 0.85)} {_f(y + (tip[1] - y) * 0.85)}" stroke="{pal[2]}" stroke-width="{max(1, wd * 0.1):.1f}" opacity="0.7" stroke-linecap="round"/>'
    return o


def daisy(u, cx, cy, r, seed, petal=("#FFFDF4", "#D8CCB4", "#FFFFFF"), center=GOLD, tilt=1.0, rot=0, n=13, detail=True):
    rnd = random.Random(seed)
    o = [f'<g transform="translate({_f(cx)} {_f(cy)}) rotate({rot}) scale(1 {tilt}) translate({_f(-cx)} {_f(-cy)})">']
    ds = []
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.08, 0.08)
        L = r * rnd.uniform(0.9, 1.05)
        w = r * 0.2 * rnd.uniform(0.85, 1.15)
        ca, sa = math.cos(a), math.sin(a)
        nx, ny = -sa, ca
        b = r * 0.22
        pts = [(cx + ca * b + nx * w * 0.4, cy + sa * b + ny * w * 0.4), (cx + ca * L * 0.6 + nx * w, cy + sa * L * 0.6 + ny * w), (cx + ca * L, cy + sa * L),
               (cx + ca * L * 0.6 - nx * w, cy + sa * L * 0.6 - ny * w), (cx + ca * b - nx * w * 0.4, cy + sa * b - ny * w * 0.4)]
        ds.append(smooth_closed(pts))
    d = " ".join(ds)
    if detail:
        o.append(form(u, d, (cx - r, cy - r, cx + r, cy + r), petal[0], petal[1], petal[2], seed, lambda x, y: math.degrees(math.atan2(y - cy, x - cx)),
                      n=r * r / 14, shade=(r * 0.06, r * 0.08), shade_op=0.5, ink_w=max(0.9, r * 0.03), ink_col="#8A7A60", ink_op=0.7,
                      length=(r * 0.2, r * 0.6), width=(0.6, max(1, r * 0.05))))
    else:
        o.append(f'<path d="{d}" fill="{petal[0]}"/><path d="{d}" fill="none" stroke="{petal[1]}" stroke-width="1"/>')
    cr = r * 0.3
    cd = blob(cx, cy, cr, cr, seed + 1, 0.06, 12)
    o.append(form(u, cd, (cx - cr, cy - cr, cx + cr, cy + cr), center[0], center[1], center[2], seed + 2, -45, n=max(4, cr), shade=(cr * 0.25, cr * 0.25),
                  hi=(cx - cr * 0.3, cy - cr * 0.3, cr * 0.4, cr * 0.3) if detail else None, ink_w=max(0.8, r * 0.025), ink_col="#8A5A10",
                  length=(cr * 0.2, cr * 0.6), width=(0.6, max(1, cr * 0.1))))
    if detail and cr > 6:
        o.append(dabs((cx - cr * 0.7, cy - cr * 0.7, cx + cr * 0.7, cy + cr * 0.7), [center[1], "#8A5A10"], seed + 3, cr * 0.9, (0.6, max(0.9, cr * 0.07)), (0.4, 0.8),
                      clip=lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 < (cr * 0.75) ** 2))
    o.append("</g>")
    return "".join(o)


def lavender(u, x, y, h, seed, ang=-90, pal=LAV, stem_c="#6E7E54", buds=11, bw=None):
    """A lavender sprig from base (x,y), length h, leaning at ang."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ca, sa = math.cos(a), math.sin(a)
    tip = (x + ca * h, y + sa * h)
    bend = h * 0.06
    nx, ny = -sa, ca
    pts = [(x, y), (x + ca * h * 0.5 + nx * bend, y + sa * h * 0.5 + ny * bend), tip]
    o = [ink(smooth_open(pts), stem_c, max(1.8, h * 0.012), seed, 1, 1)]
    bw = bw or max(4.0, h * 0.032)
    for i in range(buds):
        t = 0.48 + 0.52 * i / (buds - 1)
        px = x + ca * h * t + nx * bend * math.sin(math.pi * t) * 1.0
        py = y + sa * h * t + ny * bend * math.sin(math.pi * t) * 1.0
        sz = bw * (1.15 - 0.55 * (i / buds))
        for side in (-1, 1):
            if i == buds - 1 and side == 1:
                continue
            bx, by = px + nx * side * sz * 0.55, py + ny * side * sz * 0.55
            rot = math.degrees(a) + side * 30
            c = rnd.choice([pal[0], pal[1], pal[0], pal[2]])
            o.append(f'<ellipse cx="{_f(bx)}" cy="{_f(by)}" rx="{_f(sz * 0.95)}" ry="{_f(sz * 0.6)}" fill="{c}" transform="rotate({rot:.0f} {_f(bx)} {_f(by)})"/>')
            o.append(f'<ellipse cx="{_f(bx - 0.3 * sz)}" cy="{_f(by - 0.25 * sz)}" rx="{_f(sz * 0.35)}" ry="{_f(sz * 0.2)}" fill="{pal[2]}" opacity="0.7" transform="rotate({rot:.0f} {_f(bx)} {_f(by)})"/>')
    # two slim leaves at the base
    for side in (-1, 1):
        d, _ = leaf_shape(x + ca * h * 0.12, y + sa * h * 0.12, h * 0.22, h * 0.02 + 1.5, math.degrees(a) + side * 28, seed + side)
        o.append(f'<path d="{d}" fill="{SAGE[1]}"/>')
    return "".join(o)


def clover(u, cx, cy, r, seed, pal=("#E8A0B8", "#B05A7A", "#FAD0DC")):
    """A round clover blossom (red clover)."""
    rnd = random.Random(seed)
    o = [f'<path d="{blob(cx, cy, r, r * 1.05, seed, 0.08, 14)}" fill="{pal[1]}"/>']
    for i in range(int(r * 2.2)):
        a = rnd.uniform(0, 2 * math.pi)
        rr = r * math.sqrt(rnd.random()) * 0.9
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr - r * 0.05
        o.append(f'<path d="M {_f(x)} {_f(y + r * 0.18)} l {_f(rnd.uniform(-1, 1))} {_f(-r * 0.32)}" stroke="{rnd.choice(pal)}" stroke-width="{max(1.6, r * 0.14):.1f}" stroke-linecap="round" opacity="0.9"/>')
    o.append(f'<path d="{blob(cx - r * 0.3, cy - r * 0.35, r * 0.35, r * 0.25, seed + 1, 0.2, 10)}" fill="{pal[2]}" opacity="0.5"/>')
    o.append(ink(blob(cx, cy, r, r * 1.05, seed, 0.08, 14), pal[1], max(1, r * 0.06), seed, 1, 0.5))
    return "".join(o)


def cosmos(u, cx, cy, r, seed, pal=ROSE, center=GOLD, rot=0, tilt=1.0, n=8):
    """Broad notched petals (cosmos / wild rose)."""
    rnd = random.Random(seed)
    o = [f'<g transform="translate({_f(cx)} {_f(cy)}) rotate({rot}) scale(1 {tilt}) translate({_f(-cx)} {_f(-cy)})">']
    ds = []
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.06, 0.06)
        ca, sa = math.cos(a), math.sin(a)
        nx, ny = -sa, ca
        L = r * rnd.uniform(0.92, 1.05)
        w = r * 0.42
        pts = [(cx + ca * r * 0.1, cy + sa * r * 0.1), (cx + ca * L * 0.5 + nx * w * 0.8, cy + sa * L * 0.5 + ny * w * 0.8),
               (cx + ca * L + nx * w * 0.45, cy + sa * L + ny * w * 0.45), (cx + ca * L * 0.9, cy + sa * L * 0.9),
               (cx + ca * L - nx * w * 0.45, cy + sa * L - ny * w * 0.45), (cx + ca * L * 0.5 - nx * w * 0.8, cy + sa * L * 0.5 - ny * w * 0.8)]
        ds.append(smooth_closed(pts))
    d = " ".join(ds)
    o.append(form(u, d, (cx - r, cy - r, cx + r, cy + r), pal[0], pal[1], pal[2], seed, lambda x, y: math.degrees(math.atan2(y - cy, x - cx)),
                  n=r * r / 10, shade=(r * 0.05, r * 0.07), ink_w=max(0.9, r * 0.03), ink_col=pal[1], length=(r * 0.25, r * 0.7), width=(0.8, max(1.2, r * 0.05))))
    for i in range(n):
        a = 2 * math.pi * (i + 0.5) / n
        o.append(f'<path d="M {_f(cx)} {_f(cy)} l {_f(math.cos(a - math.pi / n) * r * 0.55)} {_f(math.sin(a - math.pi / n) * r * 0.55)}" stroke="{pal[1]}" stroke-width="{max(0.8, r * 0.025):.1f}" opacity="0.4"/>')
    cr = r * 0.26
    o.append(form(u, blob(cx, cy, cr, cr, seed + 1, 0.08, 10), (cx - cr, cy - cr, cx + cr, cy + cr), center[0], center[1], center[2], seed + 2, -45,
                  n=max(4, cr), shade=(cr * 0.2, cr * 0.2), ink_w=max(0.8, r * 0.025), ink_col="#8A5A10", length=(cr * 0.2, cr * 0.5), width=(0.6, 1.2)))
    o.append(dabs((cx - cr, cy - cr, cx + cr, cy + cr), ["#8A5A10", center[2]], seed + 3, cr * 0.8, (0.6, max(1, cr * 0.08)), (0.5, 0.9),
                  clip=lambda x, y: (x - cx) ** 2 + (y - cy) ** 2 < (cr * 0.8) ** 2))
    o.append("</g>")
    return "".join(o)


def bluebell(u, cx, cy, r, seed, pal=("#7E9AD0", "#4A5E9A", "#B8C8EC"), rot=0):
    """Cornflower: a frilly round head of small petals."""
    rnd = random.Random(seed)
    o = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    for i in range(10):
        a = 2 * math.pi * i / 10
        x, y = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55
        d = smooth_closed([(cx + math.cos(a) * r * 0.15, cy + math.sin(a) * r * 0.15), (x + math.cos(a + 1.2) * r * 0.3, y + math.sin(a + 1.2) * r * 0.3),
                           (cx + math.cos(a + 0.18) * r, cy + math.sin(a + 0.18) * r), (cx + math.cos(a) * r * 0.85, cy + math.sin(a) * r * 0.85),
                           (cx + math.cos(a - 0.18) * r, cy + math.sin(a - 0.18) * r), (x + math.cos(a - 1.2) * r * 0.3, y + math.sin(a - 1.2) * r * 0.3)])
        o.append(f'<path d="{d}" fill="{rnd.choice(pal[:2] + (pal[0],))}"/><path d="{d}" fill="none" stroke="{pal[1]}" stroke-width="{max(0.8, r * 0.04):.1f}" opacity="0.7"/>')
    o.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 0.2)}" fill="#3A3A6A"/>')
    o.append(dabs((cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6), [pal[2], "#FFFFFF"], seed, r * 0.6, (0.6, max(1, r * 0.05)), (0.4, 0.8)))
    o.append("</g>")
    return "".join(o)


def poppy(u, cx, cy, r, seed, pal=("#E8603A", "#B03A1E", "#F89A6A"), rot=0, tilt=0.85):
    rnd = random.Random(seed)
    o = [f'<g transform="translate({_f(cx)} {_f(cy)}) rotate({rot}) scale(1 {tilt}) translate({_f(-cx)} {_f(-cy)})">']
    for i, (a0, rr) in enumerate(((-150, 1.0), (-30, 1.0), (90, 0.95), (-90, 0.85))):
        a = math.radians(a0)
        px, py = cx + math.cos(a) * r * 0.45, cy + math.sin(a) * r * 0.45
        d = blob(px, py, r * 0.62 * rr, r * 0.55 * rr, seed + i, 0.1, 14, a0)
        o.append(form(u, d, (px - r * 0.7, py - r * 0.7, px + r * 0.7, py + r * 0.7), pal[0], pal[1], pal[2], seed + i,
                      lambda x, y: math.degrees(math.atan2(y - cy, x - cx)), n=r * r / 14, shade=(r * 0.08, r * 0.08), ink_w=max(0.9, r * 0.03),
                      ink_col=pal[1], length=(r * 0.2, r * 0.5), width=(0.8, max(1.2, r * 0.05))))
    o.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 0.24)}" fill="#2A1A14"/>')
    o.append("".join(f'<path d="M {_f(cx)} {_f(cy)} l {_f(math.cos(a) * r * 0.36)} {_f(math.sin(a) * r * 0.36)}" stroke="#2A1A14" stroke-width="{max(1, r * 0.04):.1f}" stroke-linecap="round"/>'
                     for a in [i * 0.7 for i in range(9)]))
    o.append(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r * 0.12)}" fill="#7E8A54"/>')
    o.append("</g>")
    return "".join(o)


def grass(seed, box, cols, n=120, h=(8, 20), w=1.6, lean=(-0.35, 0.35), op=(0.5, 0.95)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    groups = {}
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        hh = rnd.uniform(*h)
        l = rnd.uniform(*lean)
        groups.setdefault(rnd.choice(cols), []).append(f"M{_f(x)} {_f(y)}q{_f(l * hh * 0.3)} {_f(-hh * 0.5)} {_f(l * hh)} {_f(-hh)}")
    return "".join(f'<path d="{"".join(v)}" stroke="{c}" stroke-width="{w}" fill="none" stroke-linecap="round" opacity="{rnd.uniform(*op):.2f}"/>' for c, v in groups.items())


# ================================================================ lettering helpers
def two_line_fit(a, fa, sa, b, fb, sb, max_w, lsa=0, lsb=0):
    """Return font sizes so that both lines fit max_w."""
    return fit_size(a, fa, sa, max_w, lsa), fit_size(b, fb, sb, max_w, lsb)


def badge_text(u, x, y, s, font, size, fill, seed, max_w=440, ls=0, shadow_c=None):
    return btext(u, x, y, s, font, size, fill, [mixc(fill, "#FFFFFF", 0.3), mixc(fill, "#000000", 0.15), fill], seed, max_w=max_w, ls=ls,
                 shadow=shadow_c)[0]


def ribbon(u, cx, cy, w, h, pal, seed, tail=36, ink_col=INK, bend=8):
    """A painted ribbon banner with folded tails."""
    x0, x1 = cx - w / 2, cx + w / 2
    tl = [(x0 + 10, cy - h * 0.2), (x0 - tail, cy - h * 0.2 + 6), (x0 - tail + 16, cy + h * 0.32 + 6), (x0 - tail, cy + h * 0.84 + 6), (x0 + 10, cy + h * 0.84)]
    tr = [(x1 - 10, cy - h * 0.2), (x1 + tail, cy - h * 0.2 + 6), (x1 + tail - 16, cy + h * 0.32 + 6), (x1 + tail, cy + h * 0.84 + 6), (x1 - 10, cy + h * 0.84)]
    o = []
    for pts in (tl, tr):
        d = poly_d(jitter(pts, seed, 0.8))
        o.append(f'<path d="{d}" fill="{pal[1]}"/>' + ink(d, ink_col, 1.8, seed, 1, 0.7))
    body = (f"M {_f(x0)} {_f(cy - h / 2)} Q {cx} {_f(cy - h / 2 + bend)} {_f(x1)} {_f(cy - h / 2)} L {_f(x1)} {_f(cy + h / 2)} "
            f"Q {cx} {_f(cy + h / 2 + bend)} {_f(x0)} {_f(cy + h / 2)} Z")
    o.append(form(u, body, (x0, cy - h / 2, x1, cy + h / 2 + bend), pal[0], pal[1], pal[2], seed + 1, -4, n=w * h / 60, shade=(0, -h * 0.12),
                  ink_w=2.0, ink_col=ink_col, length=(20, 60), width=(1, 3), sop=(0.12, 0.3)))
    return "".join(o)


# ================================================================ more painted objects
def rays(cx, cy, n, col, op=0.25, r=900, rot=0, frac=0.5):
    """Sunburst wedges (vintage poster rays)."""
    ds = []
    for i in range(n):
        a0 = math.radians(rot + 360 * i / n)
        a1 = math.radians(rot + 360 * (i + frac) / n)
        ds.append(f"M {_f(cx)} {_f(cy)} L {_f(cx + r * math.cos(a0))} {_f(cy + r * math.sin(a0))} L {_f(cx + r * math.cos(a1))} {_f(cy + r * math.sin(a1))} Z")
    return f'<path d="{" ".join(ds)}" fill="{col}" opacity="{op}"/>'


def flame(u, cx, base, h, seed):
    w = h * 0.36
    d = smooth_closed([(cx, base - h), (cx + w * 0.55, base - h * 0.45), (cx + w * 0.5, base - h * 0.1), (cx, base),
                       (cx - w * 0.5, base - h * 0.1), (cx - w * 0.6, base - h * 0.45)])
    di = smooth_closed([(cx, base - h * 0.62), (cx + w * 0.3, base - h * 0.25), (cx, base - h * 0.02), (cx - w * 0.3, base - h * 0.25)])
    return (glow(u, cx, base - h * 0.45, h * 2.2, "#FFC860", 0.55) + glow(u, cx, base - h * 0.45, h * 0.9, "#FFF0B0", 0.7) +
            f'<path d="{d}" fill="#F6A83A"/><path d="{di}" fill="#FFF4C8"/>' +
            f'<ellipse cx="{_f(cx)}" cy="{_f(base - h * 0.08)}" rx="{_f(w * 0.18)}" ry="{_f(h * 0.1)}" fill="#7AA0D0" opacity="0.6"/>')


def candle(u, cx, top, w, h, seed):
    """A rolled beeswax pillar candle: honeycomb-embossed wax, rounded form, melted pool, lit wick."""
    rnd = random.Random(seed)
    x0, x1 = cx - w / 2, cx + w / 2
    ry = w * 0.14
    body = f"M {_f(x0)} {_f(top)} L {_f(x0)} {_f(top + h)} A {_f(w / 2)} {_f(ry)} 0 0 0 {_f(x1)} {_f(top + h)} L {_f(x1)} {_f(top)} Z"
    cid, g = u("cd"), u("cg")
    o = [shadow(u, cx + 10, top + h + ry * 0.6, w * 0.75, ry * 1.4, 0.45)]
    o.append(f'<defs><clipPath id="{cid}"><path d="{body}"/></clipPath><linearGradient id="{g}" x1="0" x2="1">'
             f'<stop offset="0" stop-color="#FFF4C8" stop-opacity="0.15"/><stop offset="0.28" stop-color="#FFF4C8" stop-opacity="0.55"/>'
             f'<stop offset="0.55" stop-color="#FFF4C8" stop-opacity="0"/><stop offset="1" stop-color="#5A2E06" stop-opacity="0.55"/></linearGradient></defs>')
    o.append(f'<path d="{body}" fill="#E8A83A"/><g clip-path="url(#{cid})">')
    # embossed honeycomb sheet, foreshortened at the sides (wrapped round the pillar)
    r = w * 0.085
    cells = []
    for row in range(int(h / (1.5 * r)) + 3):
        for c in range(-8, 9):
            u_ = (c + (0.5 if row % 2 else 0)) * math.sqrt(3) * r / (w / 2)
            if abs(u_) > 1.0:
                continue
            x = cx + (w / 2) * math.sin(u_ * math.pi / 2)
            y = top - r + row * 1.5 * r + ry * math.cos(u_ * math.pi / 2) * 0.9
            sq = math.cos(u_ * math.pi / 2)
            pts = [(x + r * 0.92 * math.cos(math.radians(-90 + 60 * i)) * sq, y + r * 0.92 * math.sin(math.radians(-90 + 60 * i))) for i in range(6)]
            cells.append(poly_d(pts))
    o.append(f'<path d="{" ".join(cells)}" fill="#F6C860" stroke="#B87418" stroke-width="2" stroke-linejoin="round"/>')
    o.append(f'<path d="{" ".join(cells)}" fill="none" stroke="#FFE8A0" stroke-width="1" transform="translate(-1 -1)" opacity="0.7"/>')
    o.append(brush((x0, top, x1, top + h + ry), ["#FFE8A0", "#C88420", "#F6C860"], seed, w * h / 220, -90, (10, 30), (1, 2.4), (0.15, 0.35)))
    o.append(f'<rect x="{_f(x0)}" y="{_f(top - ry)}" width="{_f(w)}" height="{_f(h + ry * 2)}" fill="url(#{g})"/>')
    o.append("</g>")
    o.append(ink(body, "#5A2E06", 2.4, seed, 2, 0.8))
    # top: melted rim and pool
    o.append(f'<ellipse cx="{_f(cx)}" cy="{_f(top)}" rx="{_f(w / 2)}" ry="{_f(ry)}" fill="#F6C860" stroke="#8A4E0E" stroke-width="2.2"/>')
    o.append(f'<ellipse cx="{_f(cx)}" cy="{_f(top + ry * 0.15)}" rx="{_f(w * 0.4)}" ry="{_f(ry * 0.7)}" fill="#E29A2E"/>')
    o.append(f'<ellipse cx="{_f(cx - w * 0.12)}" cy="{_f(top - ry * 0.1)}" rx="{_f(w * 0.16)}" ry="{_f(ry * 0.25)}" fill="#FFF0B8" opacity="0.7"/>')
    # a wax drip over the rim
    o.append(f'<path d="M {_f(x0 + w * 0.12)} {_f(top + ry * 0.5)} q 4 {_f(h * 0.12)} 0 {_f(h * 0.2)} q -6 6 -10 -2 q -2 {_f(-h * 0.08)} -6 {_f(-h * 0.18)} Z" fill="#F6C860" stroke="#8A4E0E" stroke-width="1.6"/>')
    o.append(f'<path d="M {_f(cx)} {_f(top + ry * 0.1)} q 2 -10 -2 -20" stroke="#2A160A" stroke-width="3" fill="none" stroke-linecap="round"/>')
    o.append(flame(u, cx - 2, top - 16, 54, seed))
    return "".join(o)


def box_hive(u, cx, base, w, seed, boxes=(("#DCE3C8", "#A8B48C", "#F2F5E6"), ("#F2D07A", "#C89A3A", "#FFF0B8"), ("#E8DCC8", "#B8A88C", "#FFF8EC")),
             roof=("#C86A4A", "#8A3E26", "#E89A7A")):
    """A painted wooden box beehive on a little stand: stacked supers, a peaked roof, an entrance and a landing board."""
    o = [shadow(u, cx + 10, base + 4, w * 0.75, 14, 0.4)]
    # legs
    for lx in (cx - w * 0.38, cx + w * 0.38):
        d = f"M {_f(lx - 7)} {_f(base - 40)} L {_f(lx + 7)} {_f(base - 40)} L {_f(lx + 6)} {_f(base)} L {_f(lx - 6)} {_f(base)} Z"
        o.append(form(u, d, (lx - 8, base - 42, lx + 8, base), WOOD[0], WOOD[1], WOOD[2], seed + int(lx), -90, n=8, shade=(4, 0), ink_w=1.8))
    y = base - 40
    # landing board
    lb = f"M {_f(cx - w * 0.56)} {_f(y)} L {_f(cx + w * 0.56)} {_f(y)} L {_f(cx + w * 0.52)} {_f(y - 16)} L {_f(cx - w * 0.52)} {_f(y - 16)} Z"
    o.append(form(u, lb, (cx - w * 0.56, y - 16, cx + w * 0.56, y), WOOD[0], WOOD[1], WOOD[2], seed + 3, 0, n=30, shade=(0, -4), ink_w=2.0))
    y -= 16
    hts = [w * 0.5, w * 0.36, w * 0.36][:len(boxes)]
    for i, (pal, bh) in enumerate(zip(boxes, hts)):
        x0, x1 = cx - w / 2, cx + w / 2
        d = soft_poly([(x0, y), (x1, y), (x1, y - bh), (x0, y - bh)], seed + i, 1.0, 0.04)
        hh = (f'<path d="M {_f(cx - w * 0.14)} {_f(y - bh * 0.62)} q {_f(w * 0.14)} -8 {_f(w * 0.28)} 0" stroke="{pal[1]}" stroke-width="6" fill="none" stroke-linecap="round"/>'
              f'<path d="M {_f(cx - w * 0.14)} {_f(y - bh * 0.62 + 4)} q {_f(w * 0.14)} -8 {_f(w * 0.28)} 0" stroke="#5A4630" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.5"/>')
        grainl = "".join(f'<path d="M {_f(x0 + 4)} {_f(y - bh * t)} q {_f(w * 0.5)} {random.Random(seed + i * 9 + int(t * 10)).uniform(-3, 3):.1f} {_f(w - 8)} 0" stroke="{pal[1]}" stroke-width="1.2" fill="none" opacity="0.5"/>' for t in (0.2, 0.42, 0.84))
        o.append(form(u, d, (x0, y - bh, x1, y), pal[0], pal[1], pal[2], seed + 10 + i, -2, n=w * bh / 70, shade=(10, 0), shade_op=0.45, ink_w=2.2,
                      length=(20, 60), width=(1.2, 3), extra_in=grainl + hh + f'<rect x="{_f(x0)}" y="{_f(y - bh)}" width="{_f(w)}" height="5" fill="{pal[1]}" opacity="0.4"/>'))
        if i == 0:
            ent = f"M {_f(cx - w * 0.3)} {_f(y)} L {_f(cx - w * 0.3)} {_f(y - 12)} L {_f(cx + w * 0.3)} {_f(y - 12)} L {_f(cx + w * 0.3)} {_f(y)} Z"
            o.append(f'<path d="{ent}" fill="#2A160A"/>')
        y -= bh
    # roof
    rf = smooth_closed([(cx - w * 0.62, y + 4), (cx - w * 0.6, y - 4), (cx, y - w * 0.3), (cx + w * 0.6, y - 4), (cx + w * 0.62, y + 4)])
    rf = poly_d(jitter([(cx - w * 0.62, y + 6), (cx, y - w * 0.3), (cx + w * 0.62, y + 6), (cx + w * 0.56, y + 12), (cx - w * 0.56, y + 12)], seed + 40, 1.0))
    o.append(form(u, rf, (cx - w * 0.62, y - w * 0.3, cx + w * 0.62, y + 12), roof[0], roof[1], roof[2], seed + 41, 30, n=w * 0.6, shade=(-8, 0), ink_w=2.4,
                  length=(14, 40), width=(1.2, 3)))
    return "".join(o)


def wildflower_band(u, y, seed, x0=-20, x1=620, depth=150, kinds=("daisy", "cosmos", "lav", "clover", "corn", "poppy"), scale=1.0, grass_cols=None):
    """A dense painted meadow edge: grass, leaves and a mix of wildflowers whose heads sit around y."""
    rnd = random.Random(seed)
    o = []
    gc = grass_cols or ["#6E8A44", "#4E6A30", "#8EA65A", "#A8B870"]
    o.append(f'<path d="{smooth_open([(x0, y + 40), (150, y + 26), (300, y + 36), (450, y + 22), (x1, y + 34)])} L {x1} 640 L {x0} 640 Z" fill="#7E9450"/>')
    o.append(brush((x0, y + 20, x1, 640), ["#5E7A3A", "#8EA65A", "#4A6230", "#A8BC70"], seed, 260, -90, (20, 50), (1.5, 3.5), (0.3, 0.7), 0.2))
    o.append(grass(seed + 1, (x0, y + 10, x1, y + depth), gc, n=int(260 * scale), h=(16, 44), w=2.0))
    items = []
    x = x0 + 20
    while x < x1:
        items.append((x + rnd.uniform(-8, 8), y + rnd.uniform(-14, 30), rnd.choice(kinds)))
        x += rnd.uniform(38, 62) * scale
    items.sort(key=lambda t: t[1])
    for i, (fx, fy, k) in enumerate(items):
        sd = seed + i * 7
        o.append(stem([(fx, fy), (fx + rnd.uniform(-6, 6), fy + 50), (fx + rnd.uniform(-10, 10), fy + 140)], "#5E7A3A", 2.4, sd))
        if rnd.random() < 0.5:
            o.append(green_leaf(u, fx, fy + 60, 34 * scale, 8 * scale, rnd.choice([-150, -30]), sd + 1, vein=False))
        r = rnd.uniform(16, 24) * scale
        if k == "daisy":
            o.append(daisy(u, fx, fy, r, sd, tilt=rnd.uniform(0.7, 1.0), rot=rnd.uniform(-20, 20)))
        elif k == "cosmos":
            o.append(cosmos(u, fx, fy, r * 1.05, sd, pal=rnd.choice([ROSE, ("#F2B8C8", "#C07890", "#FFE0EA")]), tilt=rnd.uniform(0.75, 1.0), rot=rnd.uniform(-30, 30)))
        elif k == "lav":
            o.append(lavender(u, fx, fy + 70, 100 * scale, sd, ang=-90 + rnd.uniform(-14, 14), buds=8))
        elif k == "clover":
            o.append(clover(u, fx, fy, r * 0.65, sd))
        elif k == "corn":
            o.append(bluebell(u, fx, fy, r * 0.85, sd, rot=rnd.uniform(0, 60)))
        elif k == "poppy":
            o.append(poppy(u, fx, fy, r, sd, rot=rnd.uniform(-20, 20)))
    return "".join(o)


def gingham(u, col="#C8484A", base="#FBF3E4", size=12, rot=0, op=0.5):
    gid = u("gh")
    return gid, (f'<defs><pattern id="{gid}" width="{size}" height="{size}" patternUnits="userSpaceOnUse" patternTransform="rotate({rot})">'
                 f'<rect width="{size}" height="{size}" fill="{base}"/><rect width="{size / 2}" height="{size}" fill="{col}" opacity="{op}"/>'
                 f'<rect width="{size}" height="{size / 2}" fill="{col}" opacity="{op}"/></pattern></defs>')


def honey_jar(u, cx, base, w, h, seed, cloth="#C8484A", label="honey", label_font=None, fill_level=0.8, dipper_on=True, drips=True,
              twine="#8A6A3A", label_col="#F6EAD2", label_ink="#5A3418", lid_on=True):
    """A glass honey jar: amber honey seen through glass, gloss, a fabric-covered lid tied with twine, a kraft label."""
    rnd = random.Random(seed)
    x0, x1 = cx - w / 2, cx + w / 2
    top = base - h
    neck = top + h * 0.12
    body = smooth_closed([(x0 + w * 0.12, neck), (x0 + w * 0.02, neck + h * 0.1), (x0, top + h * 0.5), (x0 + w * 0.02, base - h * 0.08), (x0 + w * 0.14, base),
                          (x1 - w * 0.14, base), (x1 - w * 0.02, base - h * 0.08), (x1, top + h * 0.5), (x1 - w * 0.02, neck + h * 0.1), (x1 - w * 0.12, neck)])
    o = [shadow(u, cx + w * 0.08, base + 4, w * 0.62, h * 0.06, 0.45)]
    # honey glow cast on the table
    o.append(glow(u, cx + w * 0.3, base + 2, w * 0.5, "#F2A030", 0.35, h * 0.05))
    cid = u("jr")
    o.append(f'<defs><clipPath id="{cid}"><path d="{body}"/></clipPath></defs>')
    o.append(f'<path d="{body}" fill="#F6E8CC" opacity="0.6"/>')
    o.append(f'<g clip-path="url(#{cid})">')
    hy = base - (h * 0.88) * fill_level
    g = u("jh")
    o.append(f'<defs><linearGradient id="{g}" x1="0" x2="1"><stop offset="0" stop-color="#F6B440"/><stop offset="0.35" stop-color="#E89220"/>'
             f'<stop offset="0.8" stop-color="#B8620E"/><stop offset="1" stop-color="#8A4408"/></linearGradient></defs>')
    hon = f"M {_f(x0 - 5)} {_f(hy)} Q {_f(cx)} {_f(hy + h * 0.05)} {_f(x1 + 5)} {_f(hy)} L {_f(x1 + 5)} {_f(base + 5)} L {_f(x0 - 5)} {_f(base + 5)} Z"
    o.append(f'<path d="{hon}" fill="url(#{g})"/>')
    o.append(brush((x0, hy, x1, base), ["#FFD070", "#C86A10", "#F2A430"], seed, w * h / 160, -80, (h * 0.06, h * 0.2), (1.2, 3), (0.15, 0.35)))
    o.append(glow(u, cx - w * 0.12, (hy + base) / 2, w * 0.36, "#FFE08A", 0.55))
    o.append(f'<ellipse cx="{_f(cx)}" cy="{_f(hy)}" rx="{_f(w / 2 + 4)}" ry="{_f(h * 0.035)}" fill="#FFC85A" opacity="0.8"/>')
    # bubbles
    for _ in range(7):
        bx, by = rnd.uniform(x0 + w * 0.15, x1 - w * 0.15), rnd.uniform(hy + 20, base - 16)
        o.append(f'<circle cx="{_f(bx)}" cy="{_f(by)}" r="{rnd.uniform(1.6, 3.4):.1f}" fill="none" stroke="#FFE6A8" stroke-width="1.2" opacity="0.7"/>')
    # glass side shading + gloss
    o.append(f'<rect x="{_f(x1 - w * 0.16)}" y="{_f(top)}" width="{_f(w * 0.2)}" height="{_f(h)}" fill="#5A2A04" opacity="0.25"/>')
    o.append("</g>")
    if dipper_on:
        o.append(f'<g clip-path="url(#{cid})">' + f'<path d="M {_f(cx + w * 0.05)} {_f(top - 30)} L {_f(cx - w * 0.12)} {_f(hy + h * 0.3)}" stroke="#B8844A" stroke-width="{_f(w * 0.06)}" opacity="0.55" stroke-linecap="round"/></g>')
    o.append(f'<path d="M {_f(x0 + w * 0.1)} {_f(neck + h * 0.14)} Q {_f(x0 + w * 0.04)} {_f(top + h * 0.5)} {_f(x0 + w * 0.1)} {_f(base - h * 0.14)}" stroke="#FFFFFF" stroke-width="{_f(max(4, w * 0.045))}" fill="none" stroke-linecap="round" opacity="0.75"/>')
    o.append(f'<path d="M {_f(x0 + w * 0.2)} {_f(neck + h * 0.12)} L {_f(x0 + w * 0.2)} {_f(neck + h * 0.24)}" stroke="#FFFFFF" stroke-width="{_f(max(3, w * 0.03))}" stroke-linecap="round" opacity="0.7"/>')
    o.append(f'<path d="M {_f(x1 - w * 0.1)} {_f(base - h * 0.34)} Q {_f(x1 - w * 0.05)} {_f(base - h * 0.2)} {_f(x1 - w * 0.12)} {_f(base - h * 0.08)}" stroke="#FFF2C8" stroke-width="{_f(max(2.5, w * 0.025))}" fill="none" stroke-linecap="round" opacity="0.6"/>')
    o.append(ink(body, "#6A3A10", 2.4, seed + 1, 2, 0.75))
    # label
    if label:
        ly, lh, lw = top + h * 0.5, h * 0.3, w * 0.66
        ld = smooth_closed([(cx - lw / 2, ly - lh / 2), (cx, ly - lh / 2 - 4), (cx + lw / 2, ly - lh / 2), (cx + lw / 2 + 3, ly), (cx + lw / 2, ly + lh / 2),
                            (cx, ly + lh / 2 + 4), (cx - lw / 2, ly + lh / 2), (cx - lw / 2 - 3, ly)])
        o.append(form(u, ld, (cx - lw / 2, ly - lh / 2, cx + lw / 2, ly + lh / 2), label_col, "#D8C4A0", "#FFFFFF", seed + 2, -10, n=lw * lh / 70,
                      shade=(-4, -3), shade_op=0.3, ink_w=1.8, ink_col="#8A6A40", length=(10, 30), width=(1, 2.4), sop=(0.1, 0.25)))
        f = label_font or SERIF_IT
        o.append(plain(cx, ly + lh * 0.18, label, f, lh * 0.56, label_ink, max_w=lw * 0.84))
        o.append(f'<path d="M {_f(cx - lw * 0.3)} {_f(ly + lh * 0.32)} L {_f(cx + lw * 0.3)} {_f(ly + lh * 0.32)}" stroke="{label_ink}" stroke-width="1.6" opacity="0.6"/>')
    if not lid_on:
        rim = soft_poly([(x0 + w * 0.1, neck), (x1 - w * 0.1, neck), (x1 - w * 0.1, top + h * 0.03), (x0 + w * 0.1, top + h * 0.03)], seed + 3, 0.8, 0.2)
        o.append(f'<path d="{rim}" fill="#F2E6CC" opacity="0.7"/>' + ink(rim, "#6A3A10", 2.0, seed + 3, 1, 0.75))
        o.append(f'<ellipse cx="{_f(cx)}" cy="{_f(top + h * 0.03)}" rx="{_f(w * 0.4)}" ry="{_f(h * 0.03)}" fill="#C8741A" stroke="#6A3A10" stroke-width="2"/>')
        for i, (dx, dl) in enumerate(((-0.3, 0.16), (0.32, 0.26), (0.05, 0.1))):
            xx = cx + dx * w
            dd = (f"M {_f(xx - 12)} {_f(top + h * 0.02)} Q {_f(xx - 10)} {_f(top + h * dl * 0.5)} {_f(xx - 6)} {_f(top + h * dl)} "
                  f"A 7 7 0 0 0 {_f(xx + 7)} {_f(top + h * dl)} Q {_f(xx + 9)} {_f(top + h * dl * 0.5)} {_f(xx + 12)} {_f(top + h * 0.02)} Z")
            o.append(f'<path d="{dd}" fill="#E0901E"/>' + ink(dd, "#6A3608", 1.8, seed + 20 + i, 1, 0.75) +
                     f'<path d="M {_f(xx - 6)} {_f(top + h * 0.04)} L {_f(xx - 3)} {_f(top + h * dl - 2)}" stroke="#FFF2C8" stroke-width="2.6" stroke-linecap="round" opacity="0.8"/>')
        return "".join(o)
    # lid: threaded band + cloth cover + twine bow
    lid = soft_poly([(x0 + w * 0.08, neck), (x1 - w * 0.08, neck), (x1 - w * 0.08, top), (x0 + w * 0.08, top)], seed + 3, 0.8, 0.12)
    o.append(form(u, lid, (x0, top, x1, neck), "#D8A84A", "#9A6A1A", "#F6D88A", seed + 4, 0, n=30, shade=(-6, 0), ink_w=2, ink_col="#6A4214"))
    gid, gdef = gingham(u, cloth, "#FBF3E4", 12, 15)
    o.append(gdef)
    cl = []
    rr = random.Random(seed + 5)
    for i in range(13):
        t = i / 12
        x = x0 - w * 0.08 + (w * 1.16) * t
        cl.append((x, neck + h * 0.06 + rr.uniform(0, h * 0.07) + (h * 0.05 if i % 2 else 0)))
    cloth_d = smooth_closed([(x0 - w * 0.06, top + h * 0.02), (cx - w * 0.3, top - h * 0.07), (cx, top - h * 0.09), (cx + w * 0.3, top - h * 0.07),
                             (x1 + w * 0.06, top + h * 0.02)] + list(reversed(cl)))
    o.append(f'<path d="{cloth_d}" fill="url(#{gid})"/>')
    o.append(f'<path d="{cloth_d}" fill="#7A1E14" opacity="0.12" transform="translate(0 4)"/>')
    o.append(brush((x0 - 10, top - h * 0.1, x1 + 10, neck + h * 0.12), ["#FFFFFF", "#7A1E14"], seed + 6, 20, -70, (6, 18), (1, 2), (0.1, 0.25)))
    o.append(ink(cloth_d, "#6A1A10", 2.0, seed + 7, 2, 0.8))
    tw = f"M {_f(x0 + w * 0.02)} {_f(neck - h * 0.01)} Q {_f(cx)} {_f(neck + h * 0.03)} {_f(x1 - w * 0.02)} {_f(neck - h * 0.01)}"
    o.append(f'<path d="{tw}" stroke="{twine}" stroke-width="4.5" fill="none" stroke-linecap="round"/><path d="{tw}" stroke="#E8D0A0" stroke-width="1.4" fill="none" stroke-dasharray="3 4"/>')
    bx, by = cx + w * 0.22, neck + h * 0.015
    o.append(f'<path d="M {_f(bx)} {_f(by)} q -22 -18 -26 -2 q 4 12 26 2 q 22 -18 26 -2 q -4 12 -26 2 m 0 0 q -6 18 -14 28 m 14 -28 q 8 16 18 24" '
             f'stroke="{twine}" stroke-width="3.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    return "".join(o)


def heart_balloon(u, cx, cy, s, seed, pal=("#D8444A", "#9A2028", "#F68A84")):
    d = heart_path(cx, cy, s)
    return (form(u, d, (cx - s * 1.9, cy - s * 1.6, cx + s * 1.9, cy + s * 1.2), pal[0], pal[1], pal[2], seed, -60, n=s * 6,
                 shade=(s * 0.2, s * 0.18), shade_op=0.55, hi=(cx - s * 0.75, cy - s * 0.65, s * 0.32, s * 0.2), hi_op=0.6, ink_w=max(1.4, s * 0.06),
                 ink_col="#6A1018") +
            f'<path d="M {_f(cx - s * 1.05)} {_f(cy - s * 0.35)} Q {_f(cx - s * 1.0)} {_f(cy - s * 0.95)} {_f(cx - s * 0.5)} {_f(cy - s * 1.05)}" stroke="#FFFFFF" stroke-width="{_f(max(2.5, s * 0.1))}" fill="none" stroke-linecap="round" opacity="0.75"/>')


# ================================================================ designs
DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


# ================================================================ bee kind (the signature piece)
@design("bee-kind")
def bee_kind():
    u = Ids("bee-kind")
    o = [bg(u, "#F7EEDC", ["#F2E2C0", "#FBF4E6", "#EED8B0", "#F6E8CC"], 11, angle=-20)]
    o.append(glow(u, 300, 230, 270, "#FFD77A", 0.5))
    # comb peeking in at two corners
    o.append(comb(u, comb_cells(600, 0, 40, 5, 5, keep=lambda x, y, c, r: math.hypot(x - 640, y + 20) < 190), 40, 21,
                  kinds=lambda i, x, y: ["honey", "capped", "honey", "empty"][i % 4]))
    o.append(comb(u, comb_cells(0, 600, 40, 5, 5, keep=lambda x, y, c, r: math.hypot(x + 40, y - 620) < 170), 40, 31,
                  kinds=lambda i, x, y: ["capped", "honey", "honey", "empty"][i % 4]))
    o.append(loop_trail(556, 110, 420, 190, 28, INK, 2.6, 0.55))
    # a daisy offered forward
    o.append(stem([(200, 268), (172, 254), (146, 228)], "#5E7A3A", 3.2, 4))
    o.append(green_leaf(u, 170, 252, 30, 9, -120, 5, vein=False))
    o.append(bee(u, 322, 200, 108, 3, rot=-6, mood="smile", arms=["M -66 40 q -24 12 -60 18", "M -50 50 q -24 18 -58 22"]))
    o.append(daisy(u, 140, 220, 36, 6, rot=-10))
    for x, y, sz in ((86, 150, 7), (520, 300, 6), (470, 70, 5), (96, 360, 5)):
        o.append(sparkle(x, y, sz, "#E8A830", 0.85))
    t, _, _ = btext(u, 300, 396, "bee", SERIF_IT, 96, INK, ["#5A3A24", "#2A1810", "#6E4A30"], 7, angle=-40, shadow="#E8B860", soff=(0.02, 0.04))
    o.append(t)
    t, _, _ = btext(u, 300, 532, "KIND", ANTON, 124, "#E8A225", ["#F6C450", "#C47A16", "#FFD87A", "#D8901C"], 8, ls=10, angle=-78,
                    shadow=INK, soff=(0.025, 0.035), hi="#FFF0C0")
    o.append(t)
    o.append(finish(u, INK, 0.7))
    return "".join(o)


# ================================================================ queen bee
@design("queen-bee")
def queen_bee():
    u = Ids("queen-bee")
    o = [bg(u, "#C9821E", ["#D8922A", "#B87012", "#E2A23A", "#A8640E"], 21, fleck="#FFE8B0", angle=-30)]
    o.append(rays(300, 250, 28, "#FFE08A", 0.12))
    o.append(glow(u, 300, 250, 280, "#FFE29A", 0.55))
    o.append(vignette(u, "#6A3606", 0.5))
    # an oval cameo with a gold beaded frame
    cx, cy, rx, ry = 300, 248, 186, 176
    ov = blob(cx, cy, rx, ry, 22, 0.012, 30)
    o.append(shadow(u, cx + 6, cy + 16, rx + 16, ry + 16, 0.45, "#4A2204"))
    o.append(form(u, blob(cx, cy, rx + 16, ry + 16, 23, 0.012, 30), (cx - rx - 16, cy - ry - 16, cx + rx + 16, cy + ry + 16), GOLD[0], GOLD[1], GOLD[2], 24,
                  lambda x, y: math.degrees(math.atan2(y - cy, x - cx)) + 90, n=260, shade=(10, 12), hi=(cx - 80, cy - 150, 60, 14), ink_w=2.4, ink_col="#7A4A0E",
                  length=(10, 30), width=(1.2, 3)))
    o.append(form(u, ov, (cx - rx, cy - ry, cx + rx, cy + ry), "#EFE6D6", "#C8B89C", "#FFFAF0", 25, -60, n=220, shade=(-8, -10), shade_op=0.3, ink_w=2.0,
                  ink_col="#7A4A0E", length=(20, 60), width=(2, 5), sop=(0.08, 0.2),
                  extra_in=glow(u, cx, cy - 10, 160, "#FFE29A", 0.5)))
    beads = []
    for i in range(44):
        a = 2 * math.pi * i / 44
        bx, by = cx + (rx + 9) * math.cos(a), cy + (ry + 9) * math.sin(a)
        beads.append(f'<circle cx="{_f(bx)}" cy="{_f(by)}" r="4.2" fill="#FFF0B0" stroke="#9A6010" stroke-width="1.2"/>')
    o.append("".join(beads))
    # laurel sprigs inside the cameo
    for side in (-1, 1):
        for k in range(7):
            t = k / 6
            a = math.radians(110 - 70 * t) if side < 0 else math.radians(70 + 70 * t)
            lx, ly = cx + side * 0 + (rx - 30) * math.cos(math.pi - a if side < 0 else a) * 1.0, cy + 40 + (ry - 40) * math.sin(a) * 0.95
        pass
    # a laurel of sage leaves and tiny daisies around the lower half of the cameo
    for side in (-1, 1):
        arc = [(cx + side * (rx - 26) * math.cos(math.radians(a)), cy + (ry - 26) * math.sin(math.radians(a))) for a in range(-10, 91, 10)]
        o.append(ink(smooth_open(arc), "#6E7A50", 3, 26 + side, 1, 0.9))
        for i, (vx, vy) in enumerate(arc[:-1]):
            tang = math.degrees(math.atan2(arc[i + 1][1] - vy, arc[i + 1][0] - vx))
            for k in (-1, 1):
                o.append(green_leaf(u, vx, vy, 26, 8, tang + k * 48, 27 + i * 3 + k + side * 50, pal=SAGE, vein=False, inkc="#4E5A34"))
        for j, a in enumerate((12, 52)):
            o.append(daisy(u, cx + side * (rx - 26) * math.cos(math.radians(a)), cy + (ry - 26) * math.sin(math.radians(a)), 13, 40 + j + side * 9, n=11))
    o.append(bee(u, 316, 236, 104, 28, rot=-4, mood="calm", crown=True, wings="up", eye_dir=(2, 0)))
    for x, y, sz in ((116, 92, 9), (488, 96, 8), (520, 360, 6), (80, 330, 6)):
        o.append(sparkle(x, y, sz, "#FFF4C8", 0.9))
    o.append(ribbon(u, 300, 474, 400, 76, ("#3A2418", "#1E120A", "#5A3A26"), 29, tail=40, ink_col="#120A04"))
    t, _, _ = btext(u, 300, 500, "QUEEN BEE", CINZEL, 60, "#F6CE5A", ["#FFE08A", "#D49A22", "#FFF0B8"], 30, max_w=360, ls=4, angle=-70)
    o.append(t)
    o.append(plain(300, 548, "OF THE HIVE", JOST, 20, "#FFF4D8", ls=8))
    o.append(finish(u, "#FFE8B0", 0.5))
    return "".join(o)


# ================================================================ mind your own beeswax
@design("mind-your-own-beeswax")
def beeswax():
    u = Ids("mind-your-own-beeswax")
    o = [bg(u, "#2E2016", ["#3A2A1E", "#22180E", "#46342A", "#1A120A"], 31, fleck="#F2D8A8", angle=-25)]
    o.append(glow(u, 300, 230, 250, "#F2A83A", 0.42))
    o.append(drip_curtain(u, 46, -20, 32, depth=(16, 86), wid=(40, 74), band_hi=False))
    # table edge
    tb = smooth_closed([(-20, 372), (300, 366), (620, 372), (620, 640), (-20, 640)])
    o.append(form(u, tb, (-20, 360, 620, 640), "#4A3022", "#2A1A10", "#6A4A34", 33, -2, n=120, shade=None, ink_w=0, length=(40, 120), width=(2, 5)))
    o.append(f'<path d="M -10 370 Q 300 362 610 370" stroke="#8A6040" stroke-width="2.4" fill="none" opacity="0.6"/>')
    o.append(candle(u, 300, 214, 132, 150, 34))
    # the bee leaning on the candle, side-eyeing us
    o.append(bee(u, 166, 314, 62, 35, rot=-4, flip=False, mood="calm", wings="flat", eye_dir=(6, -2), legs=True,
                 arms=["M -60 40 q -10 18 4 30"]))
    o.append(f'<path d="M 120 266 q 8 -6 16 -2" stroke="#120C08" stroke-width="3" fill="none" stroke-linecap="round"/>')
    t, _, _ = btext(u, 300, 440, "mind your own", SERIF_IT, 56, "#FBEBD2", ["#FFF6E6", "#E8D2B4"], 36, max_w=420, angle=-35, shadow="#120A04",
                    soff=(0.02, 0.05))
    o.append(t)
    t, _, _ = btext(u, 300, 536, "BEESWAX", ANTON, 104, "#F2B33A", ["#F6C450", "#C47A16", "#FFD87A"], 37, max_w=460, ls=6, angle=-78,
                    shadow="#120A04", soff=(0.025, 0.04), hi="#FFF0C0")
    o.append(t)
    o.append(finish(u, "#F2D8A8", 0.5))
    return "".join(o)


# ================================================================ bee happy
@design("bee-happy")
def bee_happy():
    u = Ids("bee-happy")
    o = [bg(u, "#F6C844", ["#F8D25A", "#EAB030", "#FBE07A", "#E8A82A"], 41, fleck="#8A5A10", angle=-20)]
    o.append(rays(300, 310, 24, "#FFF0A8", 0.35, rot=4))
    o.append(glow(u, 300, 300, 230, "#FFF6C8", 0.6))
    t, _, _ = btext(u, 300, 168, "bee happy", SERIF_IT, 116, "#3A2418", ["#5A3A24", "#2A1810", "#6E4A30"], 42, max_w=470, angle=-40,
                    shadow="#FFF2C0", soff=(-0.02, -0.025))
    o.append(t)
    o.append(loop_trail(76, 330, 214, 300, 28, INK, 2.6, 0.55, up=True))
    o.append(bee(u, 334, 326, 88, 43, rot=-14, mood="grin", wings="spread", arms="up"))
    for x, y, sz in ((520, 210, 9), (92, 214, 6), (510, 380, 7), (230, 210, 5)):
        o.append(sparkle(x, y, sz, "#FFFFFF", 0.9))
    o.append(wildflower_band(u, 486, 44, kinds=("daisy", "daisy", "cosmos", "clover", "daisy", "lav"), scale=1.45))
    o.append(finish(u, INK, 0.6))
    return "".join(o)


# ================================================================ sweet as honey
@design("sweet-as-honey")
def sweet_as_honey():
    u = Ids("sweet-as-honey")
    o = [bg(u, "#F8E8D2", ["#F6DCC0", "#FBF2E4", "#F2D4B0", "#F8E2C8"], 51, angle=-20)]
    o.append(glow(u, 300, 380, 300, "#FFC86A", 0.45))
    t, _, _ = btext(u, 300, 124, "sweet as", SERIF_IT, 76, "#6A3A1A", ["#8A5230", "#4A2410"], 52, angle=-40, shadow="#F2C890", soff=(0.02, 0.04))
    o.append(t)
    t, _, _ = btext(u, 282, 238, "HONEY", ANTON, 124, "#E0921E", ["#F6C450", "#B86A10", "#FFD87A", "#D8901C"], 53, ls=10, angle=-78, max_w=390,
                    shadow="#6A3A1A", soff=(0.025, 0.035), hi="#FFF0C0")
    o.append(t)
    # a slab of comb with honey oozing over the front edge
    cells = comb_cells(300, 470, 38, 5, 11)
    slab = smooth_closed([(-20, 360), (80, 330), (180, 338), (300, 326), (420, 334), (520, 324), (620, 340), (620, 640), (-20, 640)])
    o.append(shadow(u, 300, 336, 340, 22, 0.35))
    cid = u("sl")
    o.append(f'<defs><clipPath id="{cid}"><path d="{slab}"/></clipPath></defs><path d="{slab}" fill="#C88A2E"/><g clip-path="url(#{cid})">')
    o.append(comb(u, cells, 38, 54, kinds=lambda i, x, y: "capped" if (i * 7) % 5 == 0 else ("empty" if (i * 3) % 7 == 0 else "honey")))
    o.append("</g>")
    o.append(ink(slab, "#7A4A16", 2.4, 55, 2, 0.8))
    # honey running over the top edge of the slab
    ooze = smooth_closed([(60, 336), (140, 328), (180, 336), (186, 366), (194, 404), (204, 420), (214, 400), (222, 356), (260, 334), (330, 326),
                          (362, 334), (368, 370), (376, 384), (386, 364), (392, 336), (440, 330), (470, 340), (440, 352), (300, 350), (100, 352)])
    o.append(form(u, ooze, (60, 320, 470, 422), AMBER[0], AMBER[1], AMBER[2], 56, -90, n=60, shade=(-3, -5), ink_w=2.0, ink_col="#6A3608"))
    o.append(f'<path d="M 120 336 Q 200 330 300 334" stroke="#FFF2C8" stroke-width="3.5" fill="none" stroke-linecap="round" opacity="0.75"/>'
             f'<path d="M 199 368 L 200 398" stroke="#FFF2C8" stroke-width="3" stroke-linecap="round" opacity="0.8"/><circle cx="371" cy="368" r="2.6" fill="#FFF" opacity="0.8"/>')
    # a bee sipping a cell through a little straw
    o.append(bee(u, 474, 306, 56, 57, rot=-4, mood="sleep", wings="up", arms=["M -62 40 q -14 10 -30 12"]))
    o.append(f'<path d="M 404 322 L 382 362" stroke="#F2EEE6" stroke-width="7" stroke-linecap="round"/><path d="M 404 322 L 382 362" stroke="#D84A4A" stroke-width="7" stroke-dasharray="6 6" stroke-linecap="butt"/>')
    o.append(drop(u, 120, 444, 14, 58))
    o.append(finish(u, INK, 0.6))
    return "".join(o)


# ================================================================ hive sweet hive
@design("hive-sweet-hive")
def hive_sweet_hive():
    u = Ids("hive-sweet-hive")
    o = [bg(u, "#EAF0E2", ["#E2EAD6", "#F2F5EC", "#D8E2CA", "#EEF2E6"], 61, fleck="#6E7A50", angle=-15)]
    sky = u("sk")
    o.append(f'<defs>{lgrad(sky, [(0, "#CFE0E6"), (0.6, "#F4EEDC"), (1, "#F8E6C4")])}</defs><rect width="600" height="420" fill="url(#{sky})" opacity="0.8"/>')
    o.append(glow(u, 470, 300, 220, "#FFE6A8", 0.5))
    # distant hedge and meadow
    o.append(f'<path d="{smooth_open([(-20, 380), (80, 360), (200, 370), (320, 352), (440, 366), (620, 350)])} L 620 640 L -20 640 Z" fill="#A9B88A"/>')
    o.append(brush((-20, 350, 620, 420), ["#94A878", "#BCC89C", "#8A9E6A"], 62, 120, -90, (10, 26), (2, 5), (0.3, 0.6)))
    o.append(f'<path d="{smooth_open([(-20, 430), (120, 420), (300, 428), (460, 416), (620, 426)])} L 620 640 L -20 640 Z" fill="#8EA466"/>')
    o.append(grass(63, (-20, 420, 620, 600), ["#6E8A44", "#A8BC70", "#5E7A3A"], 220, (10, 26), 2.0))
    o.append(box_hive(u, 300, 540, 176, 64))
    # hollyhocks and lavender beside the hive
    for i, (x, b, h) in enumerate(((108, 560, 230), (500, 560, 210))):
        o.append(stem([(x, b), (x + 4, b - h * 0.5), (x - 2, b - h)], "#5E7A3A", 4, 65 + i))
        for k in range(6):
            yy = b - h + k * 30
            r = 20 - k * 1.2
            o.append(cosmos(u, x + (k % 2) * 10 - 5, yy, r, 66 + i * 10 + k, pal=ROSE if i == 0 else ("#F2B8C8", "#C07890", "#FFE0EA"), n=6, tilt=0.9))
        o.append(green_leaf(u, x, b - 40, 46, 14, -150 if i == 0 else -30, 70 + i))
    o.append(lavender(u, 182, 590, 150, 71, ang=-96, buds=9))
    o.append(lavender(u, 200, 590, 130, 72, ang=-80, buds=8))
    o.append(lavender(u, 410, 590, 140, 73, ang=-84, buds=9))
    o.append(bee(u, 432, 262, 28, 74, rot=-10, flip=True, mood="smile", wings="spread"))
    o.append(bee(u, 172, 300, 24, 75, rot=10, mood="smile", wings="up"))
    t, _, _ = btext(u, 300, 118, "hive sweet hive", SERIF_IT, 76, "#3A2418", ["#5A3A24", "#2A1810", "#6E4A30"], 76, max_w=460, angle=-40,
                    shadow="#F6E6C0", soff=(0.02, 0.04))
    o.append(t)
    o.append(ruled_c(u, 168, "HOME IS WHERE THE HONEY IS", JOST, 19, "#8A5A20", 77, ls=4, line_w=30))
    o.append(finish(u, INK, 0.55))
    return "".join(o)


# ================================================================ the bee's knees
@design("bees-knees")
def bees_knees():
    u = Ids("bees-knees")
    o = [bg(u, "#241A12", ["#2E2218", "#1A120A", "#3A2A1E"], 81, fleck="#F2D8A8", angle=-25)]
    o.append(glow(u, 300, 250, 260, "#E8A030", 0.35))
    # art-deco sunrise fan
    fan = []
    for i in range(19):
        a = math.radians(180 + i * 10)
        fan.append(f"M {_f(300 + 70 * math.cos(a))} {_f(330 + 70 * math.sin(a))} L {_f(300 + 250 * math.cos(a))} {_f(330 + 250 * math.sin(a))}")
    o.append(f'<path d="{" ".join(fan)}" stroke="#E2A83A" stroke-width="3" opacity="0.55"/>')
    for r in (70, 110, 250):
        o.append(f'<path d="M {300 - r} 330 A {r} {r} 0 0 1 {300 + r} 330" stroke="#E2A83A" stroke-width="{4 if r == 250 else 3}" fill="none" opacity="0.7"/>')
    # stepped deco frame
    for inset, w_ in ((44, 3.2), (54, 1.6)):
        a, b = inset, 600 - inset
        st = 26
        pts = [(a + st, a), (b - st, a), (b - st, a + st * 0.4), (b - st * 0.4, a + st * 0.4), (b - st * 0.4, a + st), (b, a + st),
               (b, b - st), (b - st * 0.4, b - st), (b - st * 0.4, b - st * 0.4), (b - st, b - st * 0.4), (b - st, b),
               (a + st, b), (a + st, b - st * 0.4), (a + st * 0.4, b - st * 0.4), (a + st * 0.4, b - st), (a, b - st),
               (a, a + st), (a + st * 0.4, a + st), (a + st * 0.4, a + st * 0.4), (a + st, a + st * 0.4)]
        o.append(ink(poly_d(jitter(pts, inset, 0.5)), "#E2A83A", w_, inset, 1, 0.9))
    # bow tie and a boater, drawn in the bee's own coordinates
    bow = ('<path d="M -78 50 L -112 30 L -108 76 Z M -78 50 L -46 30 L -48 74 Z" fill="#C8344A" stroke="#4A0E14" stroke-width="3" stroke-linejoin="round"/>'
           '<path d="M -104 40 L -102 66 M -52 40 L -54 64" stroke="#F6B0A8" stroke-width="3" opacity="0.6"/>'
           '<ellipse cx="-78" cy="52" rx="9" ry="11" fill="#A82034" stroke="#4A0E14" stroke-width="3"/>')
    hat = ('<g transform="rotate(-14 -98 -56)"><ellipse cx="-98" cy="-52" rx="62" ry="13" fill="#E8C878" stroke="#6A4A1A" stroke-width="3"/>'
           '<path d="M -136 -54 L -134 -92 Q -98 -100 -62 -92 L -60 -54 Q -98 -46 -136 -54 Z" fill="#F2D68A" stroke="#6A4A1A" stroke-width="3"/>'
           '<path d="M -135 -66 Q -98 -58 -61 -66 L -61 -76 Q -98 -68 -135 -76 Z" fill="#2A1D14"/>'
           '<ellipse cx="-98" cy="-93" rx="36" ry="7" fill="#F8E0A0" stroke="#6A4A1A" stroke-width="2.4"/>'
           '<path d="M -128 -84 l 10 -1 M -110 -86 l 12 0 M -126 -58 l 10 1" stroke="#B8944A" stroke-width="2" opacity="0.7"/></g>')
    o.append(bee(u, 316, 250, 104, 82, rot=-8, mood="wink", wings="spread", head_over=bow + hat, arms=["M -60 44 q -20 20 -48 12"]))
    for x, y, sz in ((120, 120, 8), (480, 120, 8), (96, 330, 6), (504, 330, 6)):
        o.append(sparkle(x, y, sz, "#F6D07A", 0.9))
    o.append(plain(300, 430, "you're the", SERIF_IT, 50, "#FBEBD2"))
    t, _, _ = btext(u, 300, 524, "BEE'S KNEES", BEBAS, 108, "#F2B94A", ["#F6CE6A", "#C8841E", "#FFE08A"], 83, max_w=430, ls=5, angle=-78,
                    shadow="#000000", soff=(0.02, 0.035), hi="#FFF0C0")
    o.append(t)
    o.append(finish(u, "#F2D8A8", 0.45))
    return "".join(o)


# ================================================================ bee mine
@design("bee-mine")
def bee_mine():
    u = Ids("bee-mine")
    o = [bg(u, "#F6D8CE", ["#F2CCC0", "#FBE6DE", "#EEC0B4", "#F8DCD2"], 91, fleck="#8A4A40", angle=-20)]
    o.append(glow(u, 220, 190, 240, "#FFF0E8", 0.6))
    rnd = random.Random(92)
    for x, y, sz in ((470, 96, 14), (530, 210, 10), (90, 330, 11), (520, 380, 9), (96, 96, 9), (360, 110, 8)):
        o.append(f'<path d="{heart_path(x, y, sz)}" fill="#E07A78" opacity="0.7" transform="rotate({rnd.uniform(-20, 20):.0f} {x} {y})"/>')
    # balloon string from the bee's hand to the heart
    hx, hy = bee_pt(380, 318, 88, -6, False, -112, 2)
    o.append(f'<path d="M {_f(hx)} {_f(hy)} C {_f(hx - 40)} {_f(hy - 30)} 250 280 214 236" stroke="#6A3A30" stroke-width="2.4" fill="none"/>')
    o.append(heart_balloon(u, 212, 168, 66, 93))
    o.append(f'<path d="M 206 236 l 6 -8 l 6 8 Z" fill="#9A2028"/>')
    o.append(bee(u, 380, 318, 88, 94, rot=-6, mood="smile", wings="up", arms=["M -66 40 q -24 -8 -46 -38", "M -52 48 q -26 -10 -42 -34"]))
    t, _, _ = btext(u, 300, 520, "bee mine", DMS, 124, "#9A2028", ["#B83038", "#7A1018", "#C84850"], 95, max_w=440, angle=-60,
                    shadow="#F6B8AC", soff=(0.02, 0.04), hi="#F8A0A0")
    o.append(t)
    o.append(finish(u, "#6A2A20", 0.5))
    return "".join(o)


# ================================================================ bee brave
@design("bee-brave")
def bee_brave():
    u = Ids("bee-brave")
    sk = u("sk")
    o = [bg(u, "#24404C", ["#2A4A56", "#1C3440", "#345864"], 101, fleck="#E8DCC0", angle=-15)]
    o.append(f'<defs>{lgrad(sk, [(0, "#1A2E44", 0.9), (0.6, "#2E5460", 0.4), (1, "#E8A060", 0.5)])}</defs><rect width="600" height="600" fill="url(#{sk})"/>')
    rnd = random.Random(102)
    for _ in range(40):
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 340)
        o.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{rnd.uniform(0.8, 2.2):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    for x, y, sz in ((110, 120, 9), (470, 80, 7), (520, 260, 6)):
        o.append(sparkle(x, y, sz, "#FFF0C0", 0.9))
    # moon
    o.append(glow(u, 492, 112, 80, "#FFF0C0", 0.4))
    moon = f"M 502 80 A 36 36 0 1 0 514 140 A 29 29 0 1 1 502 80 Z"
    o.append(form(u, moon, (446, 74, 520, 150), "#FBE8B0", "#D8B870", "#FFFBEA", 103, -60, n=40, shade=None, ink_w=1.6, ink_col="#B8984A"))
    # distant hills
    o.append(f'<path d="{smooth_open([(-20, 380), (100, 340), (220, 372), (360, 330), (480, 366), (620, 340)])} L 620 640 L -20 640 Z" fill="#1E3640"/>')
    o.append(f'<path d="{smooth_open([(-20, 420), (140, 396), (300, 414), (460, 390), (620, 410)])} L 620 640 L -20 640 Z" fill="#162A30"/>')
    o.append(brush((-20, 330, 620, 640), ["#24404A", "#0E1E24", "#2E4C56"], 104, 140, -4, (30, 90), (2, 5), (0.2, 0.5)))
    # cape flowing behind (bee coordinates)
    cape_d = ("M -66 -34 Q 10 -46 70 -6 Q 120 30 160 12 Q 200 -6 236 14 Q 214 40 232 70 Q 250 96 226 118 "
              "Q 190 104 160 124 Q 120 146 80 112 Q 20 70 -60 34 Z")
    cape = ('<path d="' + cape_d + '" fill="#C8343A"/>'
            '<path d="M 60 30 Q 120 70 170 60 Q 200 54 226 90 M 20 50 Q 90 100 140 110" stroke="#8A1820" stroke-width="7" fill="none" opacity="0.55" stroke-linecap="round"/>'
            '<path d="M -50 -28 Q 30 -36 90 4 Q 130 30 170 20" stroke="#F27A6A" stroke-width="8" fill="none" opacity="0.6" stroke-linecap="round"/>'
            + brush((-60, -40, 240, 140), ["#E8565A", "#9A2028", "#F27A6A"], 108, 60, 20, (16, 50), (1.5, 4), (0.15, 0.4), 0.2) +
            '<path d="' + cape_d + '" fill="none" stroke="#5A0E14" stroke-width="3.4" stroke-linejoin="round"/>')
    clasp = '<circle cx="-62" cy="0" r="9" fill="#F6CE5A" stroke="#7A4A0E" stroke-width="3"/>'
    o.append(bee(u, 316, 200, 92, 105, rot=-22, flip=True, mood="grin", wings="spread", under=cape, head_over=clasp, arms="up"))
    t, _, _ = btext(u, 300, 412, "bee", SERIF_IT, 92, "#F6CE5A", ["#FFE08A", "#D49A22"], 106, angle=-40, shadow="#0A161C", soff=(0.02, 0.04))
    o.append(t)
    t, _, _ = btext(u, 300, 540, "BRAVE", ANTON, 132, "#FBEBD2", ["#FFF6E6", "#E8D2B4", "#F6E0C0"], 107, ls=12, angle=-78, shadow="#0A161C",
                    soff=(0.025, 0.035))
    o.append(t)
    o.append(finish(u, "#E8DCC0", 0.45))
    return "".join(o)


# ================================================================ busy bee
def lavender_rows(u, horizon, seed, x_vp=300, rows=9, pal=LAV):
    """A lavender field in perspective: mounded rows converging on a vanishing point."""
    rnd = random.Random(seed)
    o = [f'<rect x="-20" y="{horizon}" width="640" height="{620 - horizon}" fill="#7A8A5A"/>']
    for i in range(rows, -1, -1):
        # each row is a wedge from the vanishing point down to the bottom edge
        xa = x_vp + (i - rows / 2 - 0.5) * 140 * 1.0
        xb = x_vp + (i - rows / 2 + 0.05) * 140 * 1.0
        d = f"M {_f(x_vp + (i - rows / 2 - 0.5) * 6)} {horizon} L {_f(x_vp + (i - rows / 2 + 0.05) * 6)} {horizon} L {_f(xb * 1.0 + (xb - x_vp) * 0.9)} 640 L {_f(xa + (xa - x_vp) * 0.9)} 640 Z"
        o.append(f'<path d="{d}" fill="{pal[1]}"/>')
        cx0, cx1 = x_vp + (i - rows / 2 - 0.22) * 6, (xa + xb) / 2 + ((xa + xb) / 2 - x_vp) * 0.9
        for k in range(70):
            t = (k / 69) ** 1.5
            x = cx0 + (cx1 - cx0) * t
            y = horizon + (640 - horizon) * t
            r = 2 + 30 * t
            o.append(f'<path d="{blob(x + rnd.uniform(-r * 0.2, r * 0.2), y - r * 0.3, r * 0.95, r * 0.5, k + i * 100, 0.18, 10)}" fill="{rnd.choice([pal[0], "#8A78B8", pal[0], pal[1]])}"/>')
            if t > 0.15:
                spikes = "".join(f"M {_f(x + dx * r * 0.8)} {_f(y - r * 0.4)} l {_f(dx * r * 0.3 + rnd.uniform(-1, 1))} {_f(-r * rnd.uniform(0.35, 0.6))}" for dx in (-0.8, -0.4, 0, 0.4, 0.8))
                o.append(f'<path d="{spikes}" stroke="{rnd.choice([pal[2], pal[0]])}" stroke-width="{_f(max(1.4, r * 0.1))}" stroke-linecap="round" fill="none" opacity="0.9"/>')
    return "".join(o)


@design("busy-bee")
def busy_bee():
    u = Ids("busy-bee")
    sk = u("sk")
    o = [bg(u, "#F8E6C8", ["#F6DCB8", "#FBF0DC", "#F2D4A8"], 111, angle=-10)]
    o.append(f'<defs>{lgrad(sk, [(0, "#F2C46A", 0.5), (0.6, "#FBEAC8", 0.2), (1, "#F8D8A8", 0.6)])}</defs><rect width="600" height="420" fill="url(#{sk})"/>')
    o.append(glow(u, 300, 400, 200, "#FFE6A0", 0.7, 90))
    # far tree line & a farmhouse on the horizon
    o.append(f'<path d="{smooth_open([(-20, 404), (60, 392), (120, 398), (200, 388), (300, 396), (420, 386), (520, 396), (620, 390)])} L 620 412 L -20 412 Z" fill="#8E9A6A"/>')
    for x, r in ((88, 22), (122, 16), (472, 20), (506, 26), (540, 18)):
        o.append(f'<path d="{blob(x, 396 - r * 0.7, r, r * 0.8, x, 0.12, 12)}" fill="#7A8A58"/>')
    o.append(lavender_rows(u, 408, 112))
    # the bee, zooming left with a basket of blossoms
    for i, (y, L) in enumerate(((280, 120), (308, 150), (336, 100))):
        o.append(brush((410, y - 3, 410 + L, y + 3), ["#E2A23A", "#C47A16"], 113 + i, 6, 0, (L * 0.4, L * 0.8), (2, 4), (0.4, 0.7), 0.05, 2))
    basket = ('<path d="M -150 40 Q -150 -10 -112 -12 Q -76 -10 -76 40" stroke="#8A5A2E" stroke-width="5" fill="none"/>'
              '<path d="M -164 40 L -62 40 L -72 90 Q -112 100 -154 90 Z" fill="#C8945A" stroke="#5A3416" stroke-width="3.4" stroke-linejoin="round"/>'
              '<path d="M -160 56 L -66 56 M -158 72 L -68 72" stroke="#8A5A2E" stroke-width="3"/>'
              '<path d="M -140 40 L -136 92 M -120 40 L -118 96 M -100 40 L -100 96 M -80 40 L -84 92" stroke="#8A5A2E" stroke-width="2.4" opacity="0.7"/>')
    o.append(bee(u, 340, 300, 74, 114, rot=-4, mood="smile", wings="spread", arms=["M -60 40 q -20 0 -40 4", "M -46 50 q -22 0 -44 -4"]))
    # basket under the bee's arms
    bx, by = bee_pt(340, 300, 74, -4, False, -112, 50)
    o.append(f'<g transform="translate({_f(bx)} {_f(by)})">'
             f'<path d="M -34 6 L 34 6 L 26 52 Q 0 60 -26 52 Z" fill="#C8945A" stroke="#5A3416" stroke-width="2.6" stroke-linejoin="round"/>'
             f'<path d="M -32 20 L 32 20 M -30 34 L 30 34" stroke="#8A5A2E" stroke-width="2.4"/>'
             f'<path d="M -16 6 L -14 56 M 0 6 L 0 58 M 16 6 L 14 56" stroke="#8A5A2E" stroke-width="2" opacity="0.7"/>'
             f'<path d="M -30 8 Q 0 -40 30 8" stroke="#5A3416" stroke-width="3.4" fill="none"/></g>')
    o.append(daisy(u, bx - 14, by + 2, 13, 115, n=11) + cosmos(u, bx + 12, by - 2, 13, 116) + clover(u, bx + 1, by - 8, 8, 117))
    o.append(lavender(u, bx - 26, by + 10, 46, 118, ang=-130, buds=6, bw=4))
    t, _, _ = btext(u, 300, 150, "BUSY BEE", JOS, 92, "#3A2418", ["#5A3A24", "#2A1810", "#6E4A30"], 120, ls=6, angle=-78, max_w=460,
                    shadow="#F6C870", soff=(0.025, 0.035))
    o.append(t)
    o.append(ruled_c(u, 188, "FROM SUNUP TO SUNDOWN", JOST, 19, "#8A5A20", 119, ls=4, line_w=30))
    o.append(finish(u, INK, 0.5))
    return "".join(o)


# ================================================================ honey, I'm home
@design("honey-im-home")
def honey_im_home():
    u = Ids("honey-im-home")
    sk = u("sk")
    o = [bg(u, "#E8C8C0", ["#E2BCB8", "#F0D4C8", "#D8B0B4"], 121, angle=-10)]
    o.append(f'<defs>{lgrad(sk, [(0, "#6E5E96", 0.85), (0.45, "#C890A8", 0.55), (0.8, "#F6C08A", 0.6), (1, "#FBD89A", 0.7)])}</defs><rect width="600" height="600" fill="url(#{sk})"/>')
    rnd = random.Random(122)
    for _ in range(26):
        o.append(f'<circle cx="{_f(rnd.uniform(20, 580))}" cy="{_f(rnd.uniform(20, 200))}" r="{rnd.uniform(0.8, 2):.1f}" fill="#FFF6E0" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    o.append(glow(u, 300, 420, 260, "#FFD58A", 0.55, 160))
    # hills
    o.append(f'<path d="{smooth_open([(-20, 400), (120, 370), (260, 390), (420, 362), (620, 386)])} L 620 640 L -20 640 Z" fill="#8E8A9A"/>')
    hill = smooth_open([(-20, 470), (120, 440), (300, 452), (480, 436), (620, 456)]) + " L 620 640 L -20 640 Z"
    o.append(form(u, hill, (-20, 430, 620, 640), "#7E9450", "#4E6232", "#AFC27A", 123, -4, n=160, shade=None, ink_w=0, length=(20, 60), width=(2, 5)))
    o.append(grass(124, (-20, 450, 620, 600), ["#6E8A44", "#A8BC70", "#4E6A30"], 200, (8, 22), 2.0))
    # winding path to the door
    path = f"M 300 532 Q 270 560 250 600 L 360 600 Q 336 560 316 532 Z"
    o.append(form(u, path, (250, 530, 360, 600), "#E8D2A8", "#C0A47A", "#FFF2D8", 125, -90, n=30, shade=None, ink_w=1.6, ink_col="#8A6A40"))
    for x, y, r in ((272, 580, 7), (330, 566, 6), (300, 592, 5)):
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 0.5}" fill="#C0A47A"/>')
    # the skep cottage
    o.append(skep(u, 300, 534, 252, 262, 126, door=False))
    door = "M 278 534 L 278 486 A 26 26 0 0 1 330 486 L 330 534 Z"
    o.append(form(u, door, (278, 460, 330, 534), "#5E8A8A", "#3A5E60", "#8ABAB4", 127, -90, n=30, shade=(6, 0), ink_w=2.4, ink_col="#22383A",
                  extra_in='<path d="M 304 462 L 304 534" stroke="#3A5E60" stroke-width="2"/>'))
    o.append('<circle cx="320" cy="506" r="3.6" fill="#F6CE5A" stroke="#6A4A1A" stroke-width="1.2"/>')
    o.append(glow(u, 236, 440, 60, "#FFD070", 0.7))
    win = blob(236, 440, 22, 22, 128, 0.02, 14)
    o.append(f'<path d="{win}" fill="#FFD878"/>' + glow(u, 236, 440, 18, "#FFF6C8", 0.9) + ink(win, "#5A3A14", 3.2, 128, 1, 0.9) +
             '<path d="M 236 418 L 236 462 M 214 440 L 258 440" stroke="#5A3A14" stroke-width="3"/>')
    # flower box under the window
    o.append(f'<path d="M 206 464 L 266 464 L 262 478 L 210 478 Z" fill="#B87A4A" stroke="#5A3416" stroke-width="2"/>')
    for i, x in enumerate((214, 230, 246, 260)):
        o.append(daisy(u, x, 460, 7, 129 + i, n=9, detail=False) if i % 2 else cosmos(u, x, 460, 7, 129 + i, n=6))
    o.append(daisy(u, 366, 528, 13, 135, n=11) + daisy(u, 384, 540, 10, 136, n=10) + cosmos(u, 220, 532, 13, 137))
    o.append(lavender(u, 410, 560, 90, 138, ang=-84, buds=8) + lavender(u, 192, 562, 80, 139, ang=-98, buds=7))
    # the bee coming home with a tiny suitcase
    o.append(trail([(570, 250), (548, 290), (520, 316)], "#FFF6E0", 2.4, "2 9", 0.8))
    case = ('<path d="M -128 40 L -64 40 L -62 84 L -130 84 Z" fill="#B8603A" stroke="#4A1E0E" stroke-width="3.4" stroke-linejoin="round"/>'
            '<path d="M -110 40 Q -110 26 -96 26 Q -82 26 -82 40" stroke="#4A1E0E" stroke-width="4" fill="none"/>'
            '<path d="M -128 54 L -64 54" stroke="#F6CE5A" stroke-width="4"/><path d="M -118 64 l 14 0" stroke="#F8C8A8" stroke-width="2"/>')
    o.append(bee(u, 494, 336, 50, 140, rot=6, mood="smile", wings="spread", head_over=case, arms=["M -66 40 q -18 2 -30 -8"]))
    t, _, _ = btext(u, 300, 122, "honey,", SERIF_IT, 88, "#FFF4DE", ["#FFFFFF", "#F2DCC0"], 141, angle=-40, shadow="#4A3A6A", soff=(0.02, 0.04))
    o.append(t)
    t, _, _ = btext(u, 300, 236, "I'M HOME", BEBAS, 124, "#F6C450", ["#FFD87A", "#D8941E", "#FFE8A8"], 142, ls=8, angle=-78, shadow="#4A2A4A",
                    soff=(0.02, 0.035), hi="#FFF4C8")
    o.append(t)
    o.append(finish(u, INK, 0.45))
    return "".join(o)


# ================================================================ honey pot
@design("honey-pot")
def honey_pot():
    u = Ids("honey-pot")
    o = [bg(u, "#DCE2CC", ["#D2DAC0", "#E6EAD8", "#C8D2B4"], 151, fleck="#5A6A40", angle=-10)]
    o.append(glow(u, 300, 330, 260, "#FFF2CC", 0.6))
    # gingham tablecloth
    gid, gdef = gingham(u, "#E8A830", "#FBF3E2", 26, 0, 0.45)
    tbl = smooth_closed([(-20, 430), (300, 422), (620, 430), (620, 640), (-20, 640)])
    o.append(gdef + f'<path d="{tbl}" fill="url(#{gid})"/>' + f'<path d="{tbl}" fill="#6A4A10" opacity="0.08"/>')
    o.append(brush((-20, 420, 620, 640), ["#FFFFFF", "#C88A20"], 152, 80, -2, (40, 100), (1.5, 3), (0.08, 0.2)))
    o.append('<path d="M -10 432 Q 300 420 610 432" stroke="#B88A30" stroke-width="2.4" fill="none" opacity="0.7"/>')
    # dipper resting in the open jar
    o.append(dipper(u, 372, 226, 230, 112, 153, scale=1.25, honey=False))
    o.append(honey_jar(u, 300, 512, 210, 230, 154, label="pure honey", lid_on=False))
    # the handle in front of the rim, with honey running down it
    o.append(f'<path d="M 346 290 L 372 226" stroke="#C8945A" stroke-width="10" stroke-linecap="round"/><path d="M 346 290 L 372 226" stroke="#5A3416" stroke-width="1.6" stroke-linecap="round" opacity="0.6" transform="translate(4 2)"/>'
             f'<path d="M 343 296 L 352 274 q 3 10 0 22 Z" fill="#E0901E" stroke="#6A3608" stroke-width="1.4"/>')
    # a chunk of comb on a little plate, a flower sprig
    o.append(shadow(u, 120, 506, 76, 14, 0.4))
    o.append(f'<ellipse cx="118" cy="498" rx="78" ry="18" fill="#F6F0E4" stroke="#8A7A60" stroke-width="2"/><ellipse cx="118" cy="494" rx="60" ry="11" fill="#E8DCC8"/>')
    o.append(comb(u, comb_cells(118, 470, 17, 2, 4), 17, 155, kinds=["honey", "capped", "honey", "honey", "empty", "honey", "capped", "honey"]))
    o.append(drop(u, 470, 482, 14, 156))
    o.append(daisy(u, 486, 438, 20, 157, tilt=0.8) + daisy(u, 512, 462, 15, 158, tilt=0.8))
    o.append(bee(u, 128, 320, 38, 159, rot=8, mood="smile", wings="spread"))
    o.append(bee(u, 486, 318, 32, 160, rot=-10, flip=True, mood="wink", wings="up"))
    o.append(trail([(154, 346), (186, 380), (204, 350)], INK, 2, "2 8", 0.5))
    t, _, _ = btext(u, 300, 158, "HONEY POT", ANTON, 96, "#D88A1E", ["#F6C450", "#B86A10", "#FFD87A"], 161, ls=6, angle=-78, max_w=440,
                    shadow="#5A3418", soff=(0.025, 0.035), hi="#FFF0C0")
    o.append(t)
    o.append(ruled_c(u, 202, "RAW · LOCAL · SWEET", JOST, 19, "#5A6A40", 162, ls=5, line_w=34))
    o.append(finish(u, INK, 0.5))
    return "".join(o)


# ================================================================ bee yourself
@design("bee-yourself")
def bee_yourself():
    u = Ids("bee-yourself")
    o = [f'<rect width="600" height="600" fill="#C88A2E"/>']
    # a wall of identical capped comb ... and one bee who is nothing like the others
    cells = comb_cells(300, 300, 44, 9, 9)
    o.append(comb(u, cells, 44, 171, kinds=lambda i, x, y: "capped" if (i * 5) % 11 else "honey", wax=("#F2D48A", "#C8963A", "#FFF0BE")))
    o.append(f'<rect width="600" height="600" fill="#6A3A0A" opacity="0.18"/>')
    o.append(glow(u, 300, 250, 230, "#FFF2C8", 0.65))
    # the medallion cell
    med = soft_poly(hex_pts(300, 238, 168), 172, 1.2, 0.1)
    o.append(shadow(u, 306, 262, 180, 170, 0.45, "#3A1A04"))
    o.append(form(u, med, (132, 70, 468, 406), "#F8EDD6", "#D8C29A", "#FFFBF2", 173, -60, n=200, shade=(-8, -10), shade_op=0.3, ink_w=3,
                  ink_col="#7A4A16", length=(20, 60), width=(2, 5), sop=(0.08, 0.2), extra_in=glow(u, 300, 230, 150, "#DDE6C4", 0.7)))
    o.append(f'<path d="{soft_poly(hex_pts(300, 238, 154), 174, 1.0, 0.1)}" fill="none" stroke="#C8963A" stroke-width="3" stroke-dasharray="1 8" stroke-linecap="round"/>')
    crown = "".join([daisy(u, -136, -52, 15, 175, n=10), cosmos(u, -112, -62, 15, 176, pal=("#F2B8C8", "#C07890", "#FFE0EA"), n=7),
                     daisy(u, -86, -64, 14, 177, n=10), cosmos(u, -62, -56, 13, 178, pal=LAV, n=7), green_leaf(u, -150, -44, 22, 7, 200, 179, vein=False),
                     green_leaf(u, -48, -50, 22, 7, -20, 180, vein=False)])
    o.append(bee(u, 318, 252, 94, 181, rot=-6, mood="smile", wings="up", head_over=crown, body=("#F6C04A", "#C47A16", "#FFE08A")))
    for x, y, sz in ((196, 120, 7), (420, 340, 6), (190, 340, 5)):
        o.append(sparkle(x, y, sz, "#E8A830", 0.9))
    # cream label below
    lab = smooth_closed(jitter([(70, 430), (300, 420), (530, 430), (536, 500), (530, 552), (300, 562), (70, 552), (64, 500)], 182, 2))
    o.append(shadow(u, 306, 500, 250, 70, 0.4, "#3A1A04"))
    o.append(form(u, lab, (64, 420, 536, 562), "#FBF3E2", "#DCC8A4", "#FFFFFF", 183, -6, n=140, shade=(0, -6), shade_op=0.3, ink_w=2.4,
                  ink_col="#7A4A16", length=(30, 80), width=(2, 5), sop=(0.08, 0.2)))
    t, _, _ = btext(u, 300, 520, "bee yourself", DMS, 92, "#3A2418", ["#5A3A24", "#2A1810", "#6E4A30"], 184, max_w=430, angle=-50)
    o.append(t)
    o.append(finish(u, INK, 0.5))
    return "".join(o)


# ================================================================ bee-lieve in yourself
def cloud(u, cx, cy, w, h, seed, base="#FFF6EC", shade_c="#D8B8C8", light="#FFFFFF"):
    rnd = random.Random(seed)
    puffs = []
    n = max(4, int(w / 34))
    for i in range(n):
        t = i / (n - 1)
        px = cx - w / 2 + w * t
        r = h * (0.45 + 0.55 * math.sin(math.pi * t)) * rnd.uniform(0.8, 1.05)
        puffs.append(blob(px, cy - r * 0.35, r * 0.75, r * 0.62, seed + i, 0.08, 12))
    d = " ".join(puffs) + f" M {_f(cx - w / 2 - 6)} {_f(cy)} L {_f(cx + w / 2 + 6)} {_f(cy)} L {_f(cx + w / 2)} {_f(cy + h * 0.25)} L {_f(cx - w / 2)} {_f(cy + h * 0.25)} Z"
    return form(u, d, (cx - w / 2 - 20, cy - h * 1.2, cx + w / 2 + 20, cy + h * 0.3), base, shade_c, light, seed, -10, n=w * h / 90, shade=(-6, -10),
                shade_op=0.6, ink_w=0, length=(10, 30), width=(2, 5), sop=(0.15, 0.4))


@design("bee-lieve-in-yourself")
def bee_lieve():
    u = Ids("bee-lieve-in-yourself")
    sk = u("sk")
    o = [bg(u, "#E8D6E6", ["#E2CCE0", "#F0E2EE", "#D8C2D8"], 191, angle=-10)]
    o.append(f'<defs>{lgrad(sk, [(0, "#8E7EB8", 0.85), (0.5, "#D8B0C8", 0.55), (0.85, "#F8D2A8", 0.7), (1, "#FBE2B0", 0.8)])}</defs><rect width="600" height="600" fill="url(#{sk})"/>')
    rnd = random.Random(192)
    for _ in range(30):
        o.append(f'<circle cx="{_f(rnd.uniform(20, 580))}" cy="{_f(rnd.uniform(20, 260))}" r="{rnd.uniform(0.8, 2):.1f}" fill="#FFF6E0" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    # the star she is reaching for
    o.append(glow(u, 452, 120, 110, "#FFE6A0", 0.75))
    st = []
    for i in range(10):
        r = 44 if i % 2 == 0 else 19
        a = math.radians(-90 + 36 * i)
        st.append((452 + r * math.cos(a), 122 + r * math.sin(a)))
    o.append(form(u, soft_poly(st, 193, 0.8, 0.14), (408, 78, 496, 166), GOLD[0], GOLD[1], GOLD[2], 194, -60, n=40, shade=(6, 6), ink_w=2.2,
                  ink_col="#9A6010", hi=(440, 106, 12, 8)))
    for x, y, sz in ((396, 70, 6), (512, 186, 5), (520, 90, 4)):
        o.append(sparkle(x, y, sz, "#FFF6D0", 0.95))
    # clouds below
    o.append(cloud(u, 130, 470, 300, 90, 195))
    o.append(cloud(u, 470, 486, 320, 84, 196))
    o.append(cloud(u, 300, 530, 520, 110, 197, base="#FFF8F0"))
    o.append(trail([(70, 420), (120, 380), (160, 400), (140, 430), (110, 400), (170, 330), (240, 280), (300, 250)], "#FFFFFF", 2.6, "2 9", 0.85))
    o.append(bee(u, 336, 216, 70, 198, rot=-34, flip=True, mood="smile", wings="spread", arms=["M -64 36 q -30 -10 -48 -40"]))
    t, _, _ = btext(u, 300, 470, "bee-lieve", SERIF_IT, 112, "#6A3A5A", ["#8A4A72", "#4A2440", "#9A5A80"], 199, max_w=440, angle=-40,
                    shadow="#FFF4EC", soff=(-0.015, -0.02))
    o.append(t)
    o.append(ruled_c(u, 540, "IN YOURSELF", JOS, 30, "#6A3A5A", 200, ls=8, line_w=44))
    o.append(finish(u, INK, 0.45))
    return "".join(o)


# ================================================================ you are bee-utiful
@design("you-are-bee-utiful")
def bee_utiful():
    u = Ids("you-are-bee-utiful")
    o = [bg(u, "#FBF3E8", ["#F6EADA", "#FFFAF2", "#F2E2CC"], 211, angle=-20)]
    o.append(glow(u, 300, 320, 240, "#FFE2C0", 0.6))
    cx, cy, R = 300, 322, 212
    rnd = random.Random(212)
    # wreath: vine, leaves, then blossoms all the way round (gap at the top for the bee)
    vine = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in range(-62, 243, 8)]
    o.append(ink(smooth_open(vine), "#6E7A50", 3.4, 213, 1, 0.9))
    for i, (vx, vy) in enumerate(vine[1:-1]):
        tang = math.degrees(math.atan2(vine[i + 2][1] - vy, vine[i + 2][0] - vx))
        for k in (-1, 1):
            o.append(green_leaf(u, vx, vy, rnd.uniform(26, 36), rnd.uniform(8, 11), tang + k * 50 + rnd.uniform(-10, 10), 214 + i * 3 + k,
                                pal=rnd.choice([SAGE, LEAF]), vein=False, inkc="#3E4A2A"))
    for i, a in enumerate(range(-46, 236, 22)):
        a2 = math.radians(a + rnd.uniform(-4, 4))
        fx, fy = cx + (R + rnd.uniform(-6, 6)) * math.cos(a2), cy + (R + rnd.uniform(-6, 6)) * math.sin(a2)
        k = i % 5
        if k == 0:
            o.append(cosmos(u, fx, fy, 24, 230 + i, pal=ROSE, rot=rnd.uniform(0, 60)))
        elif k == 1:
            o.append(daisy(u, fx, fy, 20, 230 + i, rot=rnd.uniform(0, 60)))
        elif k == 2:
            o.append(lavender(u, fx, fy, 50, 230 + i, ang=math.degrees(a2) + 90 + rnd.choice([-1, 1]) * 30, buds=6, bw=4.4))
        elif k == 3:
            o.append(cosmos(u, fx, fy, 20, 230 + i, pal=("#F2B8C8", "#C07890", "#FFE0EA"), rot=rnd.uniform(0, 60)))
        else:
            o.append(clover(u, fx, fy, 12, 230 + i) + daisy(u, fx + 14, fy + 10, 11, 260 + i, n=10))
    o.append(bee(u, 316, 116, 60, 216, rot=-4, mood="smile", wings="up", legs=True))
    o.append(plain(300, 268, "you are", SERIF_IT, 52, "#8A5A3A"))
    t, _, _ = btext(u, 300, 366, "bee-utiful", SERIF_IT, 92, "#C46A3A", ["#D8824A", "#A8502A", "#E89A62"], 217, max_w=340, angle=-40,
                    shadow="#F6D6B8", soff=(0.02, 0.04))
    o.append(t)
    for x in (252, 300, 348):
        o.append(f'<path d="{heart_path(x, 406, 7)}" fill="#E07A78"/>')
    o.append(finish(u, INK, 0.45))
    return "".join(o)


# ================================================================ save the bees
@design("save-the-bees")
def save_the_bees():
    u = Ids("save-the-bees")
    sk = u("sk")
    o = [bg(u, "#E6EADC", ["#DCE2CE", "#EEF0E6", "#D2DAC2"], 241, fleck="#5A6A40", angle=-10)]
    o.append(f'<defs>{lgrad(sk, [(0, "#B8D0D8", 0.7), (0.6, "#F2EEDA", 0.3), (1, "#F8E6BE", 0.5)])}</defs><rect width="600" height="400" fill="url(#{sk})"/>')
    t, _, _ = btext(u, 300, 150, "SAVE THE", ANTON, 84, "#3E5A30", ["#4E6A3A", "#2E4422", "#5E7A44"], 242, ls=6, angle=-78, max_w=360,
                    shadow="#F6EEDA", soff=(0.02, 0.035))
    o.append(t)
    t, _, _ = btext(u, 300, 262, "BEES", ANTON, 122, "#E8A225", ["#F6C450", "#C47A16", "#FFD87A"], 243, ls=12, angle=-78, shadow="#3E5A30",
                    soff=(0.025, 0.035), hi="#FFF0C0")
    o.append(t)
    # a tall, lush meadow, big blooms in front
    o.append(f'<path d="{smooth_open([(-20, 380), (140, 366), (300, 378), (460, 362), (620, 374)])} L 620 640 L -20 640 Z" fill="#8EA466"/>')
    o.append(grass(244, (-20, 360, 620, 640), ["#6E8A44", "#A8BC70", "#5E7A3A", "#4E6A30"], 340, (20, 60), 2.2))
    rnd = random.Random(245)
    back = [(x, rnd.uniform(370, 410)) for x in range(10, 600, 34)]
    for i, (x, y) in enumerate(back):
        k = i % 4
        o.append(stem([(x, y), (x + 2, y + 60)], "#5E7A3A", 2, 246 + i))
        if k == 0:
            o.append(daisy(u, x, y, 12, 250 + i, tilt=0.8, detail=False))
        elif k == 1:
            o.append(bluebell(u, x, y, 10, 250 + i))
        elif k == 2:
            o.append(clover(u, x, y, 8, 250 + i))
        else:
            o.append(cosmos(u, x, y, 11, 250 + i, tilt=0.8))
    front = [("poppy", 90, 452, 40), ("daisy", 196, 486, 38), ("corn", 300, 448, 32), ("cosmos", 404, 480, 40), ("poppy", 512, 450, 36),
             ("lav", 150, 600, 0), ("lav", 460, 600, 0), ("daisy", 556, 540, 30), ("cosmos", 40, 540, 32)]
    for i, (k, x, y, r) in enumerate(front):
        sd = 270 + i * 5
        if k == "lav":
            o.append(lavender(u, x, y, 190, sd, ang=-90 + rnd.uniform(-8, 8), buds=11, bw=7))
            continue
        o.append(stem([(x, y), (x + rnd.uniform(-8, 8), y + 80), (x + rnd.uniform(-12, 12), y + 200)], "#4E6A30", 4, sd))
        o.append(green_leaf(u, x + 2, y + 70, 54, 14, rnd.choice([-150, -30]), sd + 1))
        if k == "poppy":
            o.append(poppy(u, x, y, r, sd, rot=rnd.uniform(-20, 20)))
        elif k == "daisy":
            o.append(daisy(u, x, y, r, sd, rot=rnd.uniform(-20, 20), tilt=0.85))
        elif k == "corn":
            o.append(bluebell(u, x, y, r, sd, rot=rnd.uniform(0, 40)))
        else:
            o.append(cosmos(u, x, y, r, sd, rot=rnd.uniform(0, 40), tilt=0.85))
    o.append(bee(u, 302, 404, 40, 290, rot=10, mood="smile", wings="up", pollen=True))
    o.append(bee(u, 470, 330, 32, 291, rot=-12, flip=True, mood="smile", wings="spread"))
    o.append(bee(u, 120, 330, 30, 292, rot=8, mood="wink", wings="spread"))
    o.append(trail([(150, 340), (200, 360), (250, 390), (270, 400)], INK, 2, "2 8", 0.45))
    o.append(finish(u, INK, 0.45))
    return "".join(o)


# ================================================================ bee the change
@design("bee-the-change")
def bee_the_change():
    u = Ids("bee-the-change")
    o = [bg(u, "#EEE8D6", ["#E6DEC6", "#F4F0E2", "#DED4B8"], 301, angle=-15)]
    o.append(glow(u, 300, 300, 240, "#FFF0C8", 0.6))
    t, _, _ = btext(u, 300, 140, "bee the", SERIF_IT, 84, "#5A6A40", ["#6E7E50", "#3E4A2A"], 302, angle=-40, shadow="#FBF6E8", soff=(0.02, 0.04))
    o.append(t)
    t, _, _ = btext(u, 300, 250, "CHANGE", ANTON, 110, "#E8A225", ["#F6C450", "#C47A16", "#FFD87A"], 303, ls=8, angle=-78, max_w=420,
                    shadow="#4E5A34", soff=(0.025, 0.035), hi="#FFF0C0")
    o.append(t)
    # mound of soil with a sprouting seedling ... and one bloom already open
    soil = smooth_closed([(120, 520), (170, 470), (240, 452), (330, 450), (420, 460), (480, 490), (500, 524), (300, 534)])
    o.append(shadow(u, 310, 528, 210, 18, 0.35))
    o.append(form(u, soil, (120, 446, 500, 534), "#8A5E3A", "#5A3A20", "#B08460", 304, -10, n=80, shade=(0, -8), ink_w=2.4, ink_col="#3A2414",
                  length=(10, 30), width=(1.5, 4)))
    o.append(dabs((150, 456, 480, 520), ["#5A3A20", "#B08460", "#3A2414"], 305, 70, (1.5, 3.5), (0.5, 0.9)))
    o.append(stem([(290, 460), (286, 410), (300, 360), (306, 330)], "#5E7A3A", 5, 306))
    o.append(green_leaf(u, 290, 420, 60, 20, -150, 307) + green_leaf(u, 294, 400, 56, 18, -30, 308))
    o.append(green_leaf(u, 302, 350, 34, 12, -160, 309))
    o.append(cosmos(u, 308, 322, 34, 310, pal=("#F6C860", "#C88A20", "#FFE8A0"), center=("#B8642A", "#7A3A14", "#E08A4A"), tilt=0.9))
    # small sprouts popping up around it
    for i, x in enumerate((196, 404, 446)):
        o.append(stem([(x, 470 + (i % 2) * 8), (x + 2, 446)], "#5E7A3A", 3, 311 + i) + green_leaf(u, x + 2, 448, 20, 8, -140, 314 + i, vein=False) +
                 green_leaf(u, x + 2, 448, 20, 8, -40, 317 + i, vein=False))
    # the bee with a watering can
    can = ('<g transform="translate(-150 50) rotate(-18)"><path d="M -30 -30 L 30 -30 L 26 30 Q 0 36 -26 30 Z" fill="#7EA0A8" stroke="#2E4448" stroke-width="3.4" stroke-linejoin="round"/>'
           '<path d="M -28 -10 L 28 -10" stroke="#A8C4C8" stroke-width="4" opacity="0.8"/>'
           '<path d="M -26 -2 L -80 -40 L -84 -32 L -30 12 Z" fill="#7EA0A8" stroke="#2E4448" stroke-width="3" stroke-linejoin="round"/>'
           '<ellipse cx="-86" cy="-38" rx="9" ry="14" transform="rotate(-50 -86 -38)" fill="#A8C4C8" stroke="#2E4448" stroke-width="3"/>'
           '<path d="M 26 -24 Q 56 -20 50 10 Q 46 26 26 22" stroke="#2E4448" stroke-width="5" fill="none"/>'
           '<path d="M -14 -30 Q 0 -60 22 -30" stroke="#2E4448" stroke-width="5" fill="none"/></g>')
    o.append(bee(u, 470, 348, 58, 320, rot=-6, mood="smile", wings="spread", head_over=can, arms=["M -62 40 q -30 6 -56 4", "M -50 50 q -30 -6 -62 -20"]))
    for i, (x, y) in enumerate(((356, 380), (346, 400), (366, 404), (340, 424), (358, 430))):
        o.append(drop(u, x, y, 4.2, 321 + i, base=("#A8D0DC", "#5E8A9A", "#E0F2F6")))
    o.append(finish(u, INK, 0.45))
    return "".join(o)


# ================================================================ what's the buzz
@design("whats-the-buzz")
def whats_the_buzz():
    u = Ids("whats-the-buzz")
    o = [bg(u, "#D8DEC6", ["#CED6BA", "#E2E6D4", "#C4CEAE"], 331, fleck="#5A6A40", angle=-15)]
    o.append(glow(u, 300, 420, 260, "#FFF4D6", 0.6))
    t, _, _ = btext(u, 300, 132, "what's the", SERIF_IT, 76, "#3A2418", ["#5A3A24", "#2A1810"], 332, angle=-40, shadow="#F2F0E2", soff=(0.02, 0.04))
    o.append(t)
    t, _, _ = btext(u, 300, 256, "BUZZ?", ANTON, 140, "#E8A225", ["#F6C450", "#C47A16", "#FFD87A"], 333, ls=10, angle=-78,
                    shadow="#3A2418", soff=(0.025, 0.035), hi="#FFF0C0")
    o.append(t)
    # a giant daisy (cropped by the bottom edge) for the two gossips to sit on
    o.append(stem([(300, 620), (296, 560)], "#5E7A3A", 10, 334))
    o.append(daisy(u, 300, 510, 230, 335, tilt=0.42, n=22))
    o.append(bee(u, 206, 438, 56, 336, rot=4, flip=True, mood="smile", wings="up", arms=["M -64 30 q -20 -20 -22 -44"]))
    o.append(bee(u, 400, 440, 56, 337, rot=-4, mood="wow", wings="up"))
    # little gossip marks
    o.append(f'<path d="M 278 382 q 8 -6 16 0 M 282 364 q 10 -8 20 0 M 288 346 q 12 -9 24 0" stroke="{INK}" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.7"/>')
    for x, y, sz in ((470, 360, 8), (488, 330, 5), (100, 330, 6)):
        o.append(sparkle(x, y, sz, "#E8A830", 0.9))
    o.append(finish(u, INK, 0.45))
    return "".join(o)


def ruled_c(u, y, s, font, size, fill, seed, ls=5, line=None, line_w=42, gap=14, w=2.2, max_w=440, cx=300):
    size = fit_size(s, font, size, max_w - 2 * (line_w + gap), ls)
    tw = measure(s, font, size, ls)
    ly = y - size * 0.34
    a, b = cx - tw / 2 - gap, cx + tw / 2 + gap
    return (plain(cx, y, s, font, size, fill, max_w, ls) + hand_rule(a - line_w, a, ly, line or fill, w, seed) +
            hand_rule(b, b + line_w, ly, line or fill, w, seed + 1))


def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
