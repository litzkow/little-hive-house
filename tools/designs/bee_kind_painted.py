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
                            lgrad, wobble_line, hill, fruit_tree, deckle, sunflower, sf_leaf, steam, painted_heart)
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
def cr_sample(pts, per=8):
    """Dense points along a closed Catmull-Rom curve (same curve smooth_closed draws)."""
    n = len(pts)
    out = []
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        for j in range(per):
            t = j / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 +
                                    (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    return out


def fur(samples, centre, color_at, seed, L=(3, 7), w=(0.8, 1.8), inset=3.5, reps=1, spread=0.4, op=0.9):
    """Tapered hairs bristling outward along a silhouette. color_at(x, y) -> colour."""
    rnd = random.Random(seed)
    cx, cy = centre
    groups = {}
    for (x, y) in samples:
        for _ in range(reps):
            a = math.atan2(y - cy, x - cx) + rnd.uniform(-spread, spread)
            nx, ny = math.cos(a), math.sin(a)
            ln, ww = rnd.uniform(*L), rnd.uniform(*w)
            px, py = x + rnd.uniform(-1.2, 1.2), y + rnd.uniform(-1.2, 1.2)
            sx, sy = px - nx * inset, py - ny * inset
            ex, ey = px + nx * ln, py + ny * ln
            groups.setdefault(color_at(px, py), []).append(
                f"M{_f(sx - ny * ww)} {_f(sy + nx * ww)}L{_f(ex)} {_f(ey)}L{_f(sx + ny * ww)} {_f(sy - nx * ww)}Z")
    return "".join(f'<path d="{"".join(v)}" fill="{c}" opacity="{op}"/>' for c, v in groups.items())


def wing_d(L, W):
    """A bee wing in its own frame: base at (0,0), reaching up (-y); leading edge on the -x side."""
    pts = [(0, 0), (-W * 0.2, -L * 0.12), (-W * 0.42, -L * 0.42), (-W * 0.44, -L * 0.72), (-W * 0.22, -L * 0.95), (W * 0.06, -L),
           (W * 0.38, -L * 0.86), (W * 0.56, -L * 0.6), (W * 0.48, -L * 0.3), (W * 0.22, -L * 0.08)]
    return smooth_closed(pts)


def wing_veins(L, W):
    p = lambda fx, fy: f"{_f(fx * W)} {_f(fy * L)}"
    return (f"M {p(-0.1, -0.04)} Q {p(-0.46, -0.36)} {p(-0.34, -0.74)} "            # costa (leading edge)
            f"M {p(-0.02, -0.05)} Q {p(-0.22, -0.4)} {p(-0.06, -0.66)} "            # radius
            f"M {p(-0.34, -0.74)} Q {p(-0.18, -0.78)} {p(-0.06, -0.66)} "           # marginal cell
            f"M {p(0.06, -0.06)} Q {p(0.14, -0.34)} {p(0.22, -0.56)} "              # cubitus
            f"M {p(-0.2, -0.43)} Q {p(-0.04, -0.44)} {p(0.12, -0.38)} "              # cross veins -> submarginal cells
            f"M {p(-0.12, -0.58)} Q {p(0.04, -0.6)} {p(0.2, -0.54)} "
            f"M {p(0.22, -0.56)} Q {p(0.3, -0.62)} {p(0.36, -0.7)} "
            f"M {p(0.1, -0.06)} Q {p(0.32, -0.18)} {p(0.42, -0.36)}")


def bee(u, cx, cy, s, seed, rot=0, flip=False, mood="smile", wings="up", body=HONEY, stripe=NOIR, cheek="#F08A78",
        legs=True, arms=None, fuzz=True, wing_tint="#EAF4F8", shadow_op=0.0, ink_px=2.0, crown=False, eye_dir=(0, 0),
        stripes=3, pollen=False, buzz=False, under="", over="", head_over="", pose="fly", lashes=False, thorax=None, knee=None):
    """A fuzzy storybook honeybee seen from the side, head toward -x (or +x with flip); s = half the body length in px.
    Head, a fluffy golden thorax and a striped, tapering abdomen; elbowed antennae; four translucent veined wings
    (two behind the body, two in front); six jointed legs.  mood: smile | grin | wow | sleep | wink | calm.
    wings: up | flat | spread.  pose: fly (legs trail) | stand (legs reach down to y=96) | tuck.
    arms: None | 'forward' | 'up' | 'hug' | list of path strings (front legs used as arms)."""
    rnd = random.Random(seed)
    k = s / 100.0
    iw = lambda px: px / k                      # local width for a given on-paper px width
    lw = lambda local, px_min: max(local, iw(px_min))
    o = []
    tr = f"translate({_f(cx)} {_f(cy)}) rotate({rot}) scale({'-' if flip else ''}{k:.4f} {k:.4f})"
    o.append(f'<g transform="{tr}">')
    if shadow_op:
        o.append(f'<ellipse cx="0" cy="104" rx="96" ry="12" fill="#2A1608" opacity="{shadow_op}"/>')
    bodyc, bdark, blight = body
    thx = thorax or ("#E6A23A", "#A8661C", "#FFD486")

    # ---- wings
    def wing(bx, by, L, W, ang, near):
        wid, gid = u("w"), u("wg")
        d = wing_d(L, W)
        op = 0.62 if near else 0.42
        r = [f'<g transform="translate({_f(bx)} {_f(by)}) rotate({ang})">',
             f'<defs><clipPath id="{wid}"><path d="{d}"/></clipPath>'
             f'<linearGradient id="{gid}" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#C8DCE6" stop-opacity="0.95"/>'
             f'<stop offset="0.55" stop-color="{wing_tint}" stop-opacity="0.75"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0.55"/></linearGradient></defs>',
             f'<path d="{d}" fill="url(#{gid})" opacity="{op}"/>',
             f'<g clip-path="url(#{wid})">',
             f'<ellipse cx="{_f(W * 0.25)}" cy="{_f(-L * 0.55)}" rx="{_f(W * 0.3)}" ry="{_f(L * 0.22)}" fill="#F8D8E8" opacity="{0.22 if near else 0.12}"/>',
             f'<ellipse cx="{_f(-W * 0.2)}" cy="{_f(-L * 0.3)}" rx="{_f(W * 0.22)}" ry="{_f(L * 0.2)}" fill="#D8F0DA" opacity="{0.2 if near else 0.1}"/>',
             brush((-W * 0.6, -L, W * 0.6, 0), ["#FFFFFF", "#DCEBF2"], seed + int(L), 10, -90, (L * 0.2, L * 0.5), (1.2, 3), (0.2, 0.45), 0.15),
             "</g>",
             f'<path d="{wing_veins(L, W)}" fill="none" stroke="#6E5A4C" stroke-width="{lw(1.3, 0.9):.2f}" stroke-linecap="round" opacity="{0.6 if near else 0.35}"/>',
             f'<path d="M {_f(-W * 0.3)} {_f(-L * 0.22)} Q {_f(-W * 0.38)} {_f(-L * 0.55)} {_f(-W * 0.18)} {_f(-L * 0.84)}" stroke="#FFFFFF" '
             f'stroke-width="{lw(3.2, 1.6):.2f}" fill="none" stroke-linecap="round" opacity="{0.85 if near else 0.5}"/>',
             ink(d, "#5A4636", lw(2.0, 1.2), seed + int(L), 2, 0.8 if near else 0.45),
             "</g>"]
        return "".join(r)

    WB = (-44, -34)                 # wing root on the thorax
    if wings == "up":
        far = [(WB[0] + 8, WB[1] - 2, 104, 50, -10)]
        near = [(WB[0] + 10, WB[1] + 4, 72, 36, 46), (WB[0], WB[1], 116, 56, 16)]
    elif wings == "spread":
        far = [(WB[0] + 6, WB[1] - 2, 100, 50, -34)]
        near = [(WB[0] + 10, WB[1] + 4, 70, 36, 72), (WB[0], WB[1], 112, 56, 38)]
    else:  # flat, swept back over the abdomen
        far = [(WB[0] + 8, WB[1] - 2, 104, 48, 56)]
        near = [(WB[0] + 10, WB[1] + 4, 74, 34, 92), (WB[0], WB[1], 116, 52, 72)]
    for wsp in far:
        o.append(wing(*wsp, False))
    o.append(under)

    # ---- legs (jointed, fuzzy) - far side first, darker
    LEGS = {
        "fly": [((-64, 30), (-78, 50), (-74, 66), (-84, 72)), ((-48, 36), (-54, 58), (-44, 74), (-50, 82)),
                ((-30, 36), (-14, 58), (2, 72), (6, 84))],
        "stand": [((-64, 30), (-84, 56), (-86, 92), (-98, 95)), ((-48, 36), (-46, 62), (-44, 93), (-56, 95)),
                  ((-30, 36), (-2, 60), (4, 93), (-8, 95))],
        "kick": [((-64, 30), (-84, 56), (-86, 92), (-98, 95)), ((-48, 36), (-40, 62), (-46, 93), (-58, 95)),
                 ((-30, 36), (6, 74), (52, 82), (64, 74))],
        "tuck": [((-64, 30), (-80, 44), (-76, 58), (-86, 62)), ((-48, 36), (-56, 54), (-46, 66), (-52, 72)),
                 ((-30, 36), (-12, 54), (2, 64), (6, 72))],
    }
    if arms == "forward":
        arm_paths = ["M -64 36 Q -100 58 -140 48", "M -50 44 Q -88 70 -128 66"]
    elif arms == "up":
        arm_paths = ["M -62 38 Q -116 64 -150 26"]
    elif arms == "hug":
        arm_paths = ["M -64 36 Q -118 56 -146 26", "M -50 44 Q -104 68 -136 50"]
    else:
        arm_paths = arms or []
    n_arm = min(2, len(arm_paths))

    def leg(pts, col, hi, far_leg, idx):
        (ax, ay), (bx, by), (ex, ey), (fx, fy) = pts
        if far_leg:
            ax, ay, bx, by, ex, ey, fx, fy = ax + 14, ay - 8, bx + 14, by - 8, ex + 14, ey - 8, fx + 14, fy - 8
        wf, wt, wr = lw(10, 2), lw(8.5, 1.8), lw(5.4, 1.3)
        r = [f'<path d="M {ax} {ay} L {bx} {by}" stroke="{col}" stroke-width="{wf:.2f}" stroke-linecap="round"/>',
             f'<path d="M {bx} {by} L {ex} {ey}" stroke="{col}" stroke-width="{wt:.2f}" stroke-linecap="round"/>',
             f'<path d="M {ex} {ey} Q {_f((ex + fx) / 2)} {_f(max(ey, fy) + 2)} {fx} {fy}" stroke="{col}" stroke-width="{wr:.2f}" stroke-linecap="round" fill="none"/>']
        if not far_leg and knee:
            r.append(f'<circle cx="{bx}" cy="{by}" r="{lw(9, 2.6):.1f}" fill="{knee}"/><circle cx="{bx - 2}" cy="{by - 2}" r="{lw(2.4, 0.6):.1f}" fill="#FFFFFF" opacity="0.6"/>')
        if not far_leg:
            r.append(f'<path d="M {_f(ax - 1)} {_f(ay + 2)} L {_f(bx - 1.5)} {_f(by - 1)} M {_f(bx - 1)} {_f(by + 2)} L {_f(ex - 1.5)} {_f(ey - 2)}" stroke="{hi}" '
                     f'stroke-width="{lw(1.8, 0.7):.2f}" stroke-linecap="round" opacity="0.55"/>')
            hairs = []
            for t in (0.3, 0.6, 0.85):
                hx, hy = bx + (ex - bx) * t, by + (ey - by) * t
                hairs.append(f"M {_f(hx)} {_f(hy)} l {_f(4 + rnd.uniform(0, 3))} {_f(rnd.uniform(-2, 2))}")
            r.append(f'<path d="{" ".join(hairs)}" stroke="{col}" stroke-width="{lw(1.6, 0.6):.2f}" stroke-linecap="round"/>')
            if pollen and idx == 2:
                pb = blob((bx + ex) / 2 + 3, (by + ey) / 2 + 2, 11, 8, seed + 9, 0.15, 10, math.degrees(math.atan2(ey - by, ex - bx)))
                r.append(f'<path d="{pb}" fill="#F08A2A"/><path d="{blob((bx + ex) / 2 + 1, (by + ey) / 2, 4.5, 3, seed + 10, 0.2, 8)}" fill="#FFD08A"/>'
                         + ink(pb, "#9A4A10", lw(1.4, 0.7), seed + 9, 1, 0.7))
        return "".join(r)

    if legs:
        P = LEGS.get(pose, LEGS["fly"])
        o.append("".join(leg(p, "#5A4434", "#8A7060", True, i) for i, p in enumerate(P) if i > 0))
        o.append("".join(leg(p, stripe, "#8A7060", False, i) for i, p in enumerate(P) if i >= n_arm))

    # ---- abdomen
    A = [(-26, -30), (-2, -52), (38, -60), (78, -50), (106, -26), (124, 4), (108, 34), (78, 58), (38, 66), (-2, 58), (-24, 34), (-32, 2)]
    A = jitter(A, seed, 1.0)
    ad = smooth_closed(A)
    o.append(f'<path d="M 112 -4 Q 130 4 140 10 Q 128 14 112 16 Z" fill="{stripe}"/>')       # sting
    BANDS = {3: ((8, 30), (52, 74), (96, 170)), 2: ((24, 48), (78, 170)), 1: ((40, 66),)}[stripes]
    bulge, yc, R = 9.0, 4.0, 66.0
    bx_at = lambda x0, y: x0 + bulge * (1 - min(1.0, ((y - yc) / R) ** 2))

    def in_band(x, y):
        return any(bx_at(b0, y) <= x <= bx_at(b1, y) for b0, b1 in BANDS)

    asamp = cr_sample(A, 14)
    if fuzz:
        o.append(fur(asamp, (40, 4), lambda x, y: stripe if in_band(x, y) else rnd.choice([bodyc, bdark, bodyc, blight]), seed + 1,
                     L=(3, 7), w=(0.9, 1.9), inset=4, reps=1, spread=0.45))
    sp = []
    for b0, b1 in BANDS:
        pts = [(bx_at(b0, y), y) for y in range(-70, 81, 10)] + [(bx_at(b1, y), y) for y in range(80, -71, -10)]
        sp.append(smooth_closed(jitter(pts, seed + b0, 1.4)))
    sid = u("st")
    seg_hi = "".join(f'<path d="{smooth_open([(bx_at(b0, y) - 3, y) for y in range(-64, 71, 12)])}" stroke="{blight}" stroke-width="5" fill="none" opacity="0.55"/>'
                     for b0, b1 in BANDS[1:] + BANDS[:1])
    stripes_svg = (f'<path d="{" ".join(sp)}" fill="{stripe}"/>'
                   f'<clipPath id="{sid}"><path d="{" ".join(sp)}"/></clipPath><g clip-path="url(#{sid})">'
                   + brush((-40, -70, 140, 80), ["#5A4432", "#1A120C", "#6E5440", "#2E2018"], seed + 7, 90,
                           lambda x, y: math.degrees(math.atan2(y - 4, x - 40)), (6, 18), (1.2, 2.8), (0.3, 0.65), 0.25) + "</g>"
                   + seg_hi)
    sh = u("ab")
    shading = (f'<defs><radialGradient id="{sh}" cx="0.42" cy="0.28" r="0.75"><stop offset="0" stop-color="#FFF4CC" stop-opacity="0.55"/>'
               f'<stop offset="0.45" stop-color="#FFF4CC" stop-opacity="0"/><stop offset="0.8" stop-color="#5A2E06" stop-opacity="0.1"/>'
               f'<stop offset="1" stop-color="#3A1A04" stop-opacity="0.45"/></radialGradient></defs>'
               f'<rect x="-40" y="-70" width="180" height="150" fill="url(#{sh})"/>'
               f'<path d="{blob(44, 62, 84, 20, seed + 4, 0.1, 14)}" fill="{NOIR}" opacity="0.2"/>'
               f'<path d="M -6 -40 Q 40 -60 92 -36" stroke="#FFF6D0" stroke-width="6" fill="none" stroke-linecap="round" opacity="0.5"/>'
               f'<path d="M 0 52 Q 40 62 86 46" stroke="#F6B860" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.35"/>')
    o.append(form(u, ad, (-34, -62, 126, 68), bodyc, bdark, blight, seed + 2, lambda x, y: math.degrees(math.atan2(y - 4, x - 40)),
                  n=200, shade=(0, 14), shade_op=0.45, ink_w=0, length=(6, 18), width=(1.2, 3), sop=(0.18, 0.45),
                  extra_in=stripes_svg + shading))
    o.append(ink(ad, INK, iw(ink_px), seed + 3, 2, 0.75))

    # ---- thorax: a fluffy golden collar
    T = blob_pts(-46, -2, 40, 42, seed + 5, 0.05, 16)
    td = smooth_closed(T)
    if fuzz:
        o.append(fur(cr_sample(T, 10), (-46, -2), lambda x, y: rnd.choice([thx[0], thx[1], thx[2], thx[0]]), seed + 6,
                     L=(4, 10), w=(1.1, 2.4), inset=4, reps=1, spread=0.55))
    tg = u("tg")
    o.append(form(u, td, (-88, -46, -4, 42), thx[0], thx[1], thx[2], seed + 7, lambda x, y: math.degrees(math.atan2(y + 2, x + 46)),
                  n=110, shade=(2, 12), shade_op=0.5, ink_w=0, length=(5, 14), width=(1.2, 2.8), sop=(0.25, 0.6),
                  extra_in=f'<defs><radialGradient id="{tg}" cx="0.4" cy="0.3" r="0.7"><stop offset="0" stop-color="#FFF0C0" stop-opacity="0.5"/>'
                           f'<stop offset="1" stop-color="#FFF0C0" stop-opacity="0"/></radialGradient></defs><rect x="-88" y="-46" width="84" height="88" fill="url(#{tg})"/>'))
    o.append(ink(td, "#6A3E14", iw(ink_px * 0.7), seed + 8, 1, 0.5))

    # ---- head
    hx, hy, hr = -100, -6, 50
    H = blob_pts(hx, hy, hr, hr * 0.97, seed + 11, 0.03, 16)
    hd = smooth_closed(H)
    if fuzz:
        o.append(fur(cr_sample(H, 8), (hx, hy), lambda x, y: stripe, seed + 12, L=(2, 5), w=(0.8, 1.6), inset=3, spread=0.4))
    hg = u("hg")
    o.append(form(u, hd, (hx - hr, hy - hr, hx + hr, hy + hr), stripe, "#120C08", "#5E4632", seed + 13,
                  lambda x, y: math.degrees(math.atan2(y - hy, x - hx)), n=80, shade=(4, 10), shade_op=0.6, ink_w=iw(1.3), ink_col="#120C08",
                  length=(5, 14), width=(1.1, 2.6),
                  extra_in=f'<defs><radialGradient id="{hg}" cx="0.36" cy="0.3" r="0.6"><stop offset="0" stop-color="#8A6A52" stop-opacity="0.7"/>'
                           f'<stop offset="1" stop-color="#8A6A52" stop-opacity="0"/></radialGradient></defs>'
                           f'<rect x="{hx - hr}" y="{hy - hr}" width="{2 * hr}" height="{2 * hr}" fill="url(#{hg})"/>'))
    # elbowed antennae
    for ax0, ay0, path, tx_, ty_ in ((-114, -48, "M -114 -48 Q -120 -66 -124 -80 Q -130 -96 -148 -102", -148, -102),
                                     (-88, -54, "M -88 -54 Q -88 -72 -90 -86 Q -88 -102 -70 -112", -70, -112)):
        o.append(ink(path, stripe, lw(4.4, 1.5), seed + ax0, 1, 1))
        o.append(f'<ellipse cx="{tx_}" cy="{ty_}" rx="{lw(5.5, 2.2):.1f}" ry="{lw(4.6, 1.9):.1f}" fill="{stripe}" transform="rotate({-30 if tx_ < -100 else 30} {tx_} {ty_})"/>'
                 f'<circle cx="{tx_ - 1.5}" cy="{ty_ - 1.5}" r="{lw(1.6, 0.7):.1f}" fill="#9A8070"/>')
    if crown:
        cr = "M -128 -40 L -134 -92 L -114 -70 L -96 -104 L -78 -70 L -58 -92 L -64 -40 Q -96 -32 -128 -40 Z"
        o.append(form(u, cr, (-136, -106, -56, -36), GOLD[0], GOLD[1], GOLD[2], seed + 21, -80, n=40, shade=(-4, 6), ink_w=iw(1.8),
                      ink_col="#7A4A0E", length=(6, 16), width=(1, 2.4)))
        for jx, jy, jc in ((-96, -56, "#C8344A"), (-118, -54, "#5E8ACA"), (-74, -54, "#5E8ACA")):
            o.append(f'<circle cx="{jx}" cy="{jy}" r="{lw(5, 2.6):.1f}" fill="{jc}"/><circle cx="{jx - 1.5}" cy="{jy - 1.5}" r="{lw(1.6, 1):.1f}" fill="#FFFFFF" opacity="0.8"/>')
        for px_, py_ in ((-134, -92), (-96, -104), (-58, -92)):
            o.append(f'<circle cx="{px_}" cy="{py_}" r="{lw(5, 2.4):.1f}" fill="{GOLD[2]}" stroke="#7A4A0E" stroke-width="{iw(1.2):.2f}"/>')
    # face
    ex, ey = -120 + eye_dir[0], -10 + eye_dir[1]
    lid = "#FFF2D8"
    if mood == "sleep":
        o.append(f'<path d="M {ex - 13} {ey} Q {ex} {ey + 11} {ex + 13} {ey}" stroke="{lid}" stroke-width="{lw(3.4, 1.4):.2f}" fill="none" stroke-linecap="round"/>')
        o.append(f'<path d="M {ex - 12} {ey + 4} l -6 5 M {ex - 4} {ey + 8} l -3 6 M {ex + 5} {ey + 8} l 0 6" stroke="{lid}" stroke-width="{lw(2, 0.9):.2f}" stroke-linecap="round"/>')
    elif mood == "wink":
        o.append(f'<path d="M {ex - 13} {ey + 3} Q {ex} {ey - 10} {ex + 13} {ey + 3}" stroke="{lid}" stroke-width="{lw(3.6, 1.4):.2f}" fill="none" stroke-linecap="round"/>')
    else:
        er = 18 if mood == "wow" else 16
        o.append(f'<ellipse cx="{ex}" cy="{ey}" rx="{er}" ry="{er * 1.1:.1f}" fill="#FFF8EC"/>')
        o.append(f'<path d="M {ex - er} {ey} A {er} {er * 1.1:.1f} 0 0 0 {ex + er} {ey}" fill="#E8D8C8" opacity="0.5"/>')
        px_, py_ = ex - 3 + eye_dir[0] * 0.35, ey + 1 + eye_dir[1] * 0.35
        pr = 9 if mood == "wow" else 11.5
        ig = u("ir")
        o.append(f'<defs><radialGradient id="{ig}" cx="0.5" cy="0.62" r="0.6"><stop offset="0" stop-color="#7A4A22"/><stop offset="0.55" stop-color="#2A160A"/>'
                 f'<stop offset="1" stop-color="#120804"/></radialGradient></defs>'
                 f'<ellipse cx="{_f(px_)}" cy="{_f(py_)}" rx="{pr}" ry="{pr * 1.12:.1f}" fill="url(#{ig})"/>')
        o.append(f'<circle cx="{_f(px_ - 3.8)}" cy="{_f(py_ - 4.8)}" r="4.4" fill="#FFFFFF"/><circle cx="{_f(px_ + 3.4)}" cy="{_f(py_ + 4.2)}" r="2" fill="#FFFFFF" opacity="0.85"/>')
        if mood == "calm":
            ec = u("ec")
            o.append(f'<defs><clipPath id="{ec}"><ellipse cx="{ex}" cy="{ey}" rx="{er + 0.5}" ry="{er * 1.1 + 0.5:.1f}"/></clipPath></defs>'
                     f'<g clip-path="url(#{ec})"><path d="M {ex - er - 2} {ey - 3} Q {ex} {ey - 1} {ex + er + 2} {ey - 5} L {ex + er + 2} {ey - er * 1.3} L {ex - er - 2} {ey - er * 1.3} Z" fill="#2E2018"/></g>'
                     f'<path d="M {ex - er - 1} {ey - 3} Q {ex} {ey - 1} {ex + er + 1} {ey - 5}" stroke="{lid}" stroke-width="{lw(2.4, 1):.2f}" fill="none" stroke-linecap="round" opacity="0.8"/>')
        else:
            o.append(f'<path d="M {ex - 12} {ey - er - 7} q 10 -8 22 -2" stroke="#120C08" stroke-width="{lw(2.4, 1):.2f}" fill="none" stroke-linecap="round" opacity="0.7"/>')
    if lashes and mood not in ("sleep",):
        o.append(f'<path d="M {ex - 16} {ey - 6} l -8 -4 M {ex - 15} {ey - 11} l -6 -8 M {ex - 11} {ey - 15} l -2 -9" stroke="#FFF2D8" stroke-width="{lw(2.2, 0.9):.2f}" stroke-linecap="round"/>')
    o.append(f'<ellipse cx="{ex + 18}" cy="{ey + 24}" rx="13" ry="8" fill="{cheek}" opacity="0.8"/>'
             f'<ellipse cx="{ex + 15}" cy="{ey + 22}" rx="4" ry="2.4" fill="#FFFFFF" opacity="0.45"/>')
    mx, my = -136, 24
    if mood in ("smile", "sleep", "wink", "calm"):
        o.append(f'<path d="M {mx - 6} {my} Q {mx + 6} {my + 12} {mx + 18} {my + 2}" stroke="#FFE6CC" stroke-width="{lw(2.8, 1.2):.2f}" fill="none" stroke-linecap="round"/>')
    elif mood == "grin":
        o.append(f'<path d="M {mx - 8} {my - 2} Q {mx + 6} {my + 20} {mx + 22} {my} Q {mx + 6} {my + 6} {mx - 8} {my - 2} Z" fill="#7A2A22" stroke="#FFE6CC" stroke-width="{lw(1.8, 0.9):.2f}"/>'
                 f'<path d="M {mx + 2} {my + 9} Q {mx + 8} {my + 13} {mx + 14} {my + 8}" stroke="#E87A6A" stroke-width="3" fill="none" opacity="0.8"/>')
    elif mood == "wow":
        o.append(f'<ellipse cx="{mx + 6}" cy="{my + 6}" rx="7" ry="9" fill="#7A2A22" stroke="#FFE6CC" stroke-width="{lw(1.8, 0.9):.2f}"/>')
    elif mood == "grump":
        o.append(f'<path d="M {mx - 6} {my + 8} Q {mx + 6} {my - 2} {mx + 18} {my + 6}" stroke="#FFE6CC" stroke-width="{lw(2.8, 1.2):.2f}" fill="none" stroke-linecap="round"/>')
    # arms (front legs used as arms): tapered fuzzy limbs with a little round hand
    for ap in arm_paths[:2]:
        o.append(f'<path d="{ap}" stroke="{stripe}" stroke-width="{lw(7.5, 1.8):.2f}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        nums = [float(v) for v in ap.replace("M", " ").replace("Q", " ").replace("q", " ").replace("L", " ").replace("l", " ").split()]
        if "q" in ap or "l" in ap:
            ex2, ey2 = nums[0] + nums[-2], nums[1] + nums[-1]
        else:
            ex2, ey2 = nums[-2], nums[-1]
        o.append(f'<circle cx="{_f(ex2)}" cy="{_f(ey2)}" r="{lw(5.2, 1.4):.1f}" fill="{stripe}"/>')
    o.append(head_over)
    for wsp in near:
        o.append(wing(*wsp, True))
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
def spot(u, cx, cy, rx, ry, pal, seed, paper_c=PAPER, deck=True, n=None, angle=-30, wob=0.05):
    """A gouache 'spot illustration' ground: a soft painted blob with brush texture and a frayed dry-brush edge."""
    pts = blob_pts(cx, cy, rx, ry, seed, wob, 22)
    d = smooth_closed(pts)
    o = [form(u, d, (cx - rx, cy - ry, cx + rx, cy + ry), pal[0], pal[1], pal[2], seed + 1, angle, n=n or rx * ry / 60, shade=None, ink_w=0,
              length=(rx * 0.15, rx * 0.5), width=(3, 9), sop=(0.08, 0.22))]
    if deck:
        o.append(deckle(u, pts, paper_c, seed + 2, (3, 8)))
    return "".join(o)


def floating_hearts(u, pts, seed, pal=("#E0727A", "#A83A48", "#F6A8A8")):
    o = []
    for i, (x, y, sz, r) in enumerate(pts):
        o.append(f'<g transform="rotate({r} {x} {y})">' + painted_heart(u, x, y, sz, pal, seed + i) + "</g>")
    return "".join(o)


def honey_stream(u, x1, y1, x2, y2, seed, w0=11, w1=5, sway=18, base=AMBER):
    """A glossy ribbon of honey falling from (x1,y1) to (x2,y2), tapering, with a light core and a coil where it lands."""
    n = 14
    left, right, core = [], [], []
    for i in range(n + 1):
        t = i / n
        x = x1 + (x2 - x1) * t + sway * math.sin(t * math.pi) * (1 - t * 0.3)
        y = y1 + (y2 - y1) * t
        w = (w0 + (w1 - w0) * t ** 0.6) / 2
        left.append((x - w, y))
        right.append((x + w, y))
        core.append((x - w * 0.35, y))
    d = smooth_open(left) + " L " + " L ".join(f"{_f(x)} {_f(y)}" for x, y in reversed(right)) + " Z"
    g = u("hs")
    o = [f'<defs><linearGradient id="{g}" x1="0" x2="1"><stop offset="0" stop-color="{base[1]}"/><stop offset="0.35" stop-color="{base[2]}"/>'
         f'<stop offset="0.6" stop-color="{base[0]}"/><stop offset="1" stop-color="#8A4A0A"/></linearGradient></defs>',
         f'<path d="{d}" fill="url(#{g})" opacity="0.95"/>',
         f'<path d="{smooth_open(core[1:-2])}" stroke="#FFF4D0" stroke-width="{max(1.6, w1 * 0.35):.1f}" fill="none" stroke-linecap="round" opacity="0.85"/>',
         ink(d, "#7A3E08", 1.4, seed, 1, 0.55)]
    # coil / pile where it lands
    for k in range(3):
        rx = w0 * (1.5 - k * 0.38)
        yy = y2 - k * w1 * 0.7
        o.append(f'<ellipse cx="{_f(x2 + sway * 0.0)}" cy="{_f(yy)}" rx="{_f(rx)}" ry="{_f(w1 * 0.75)}" fill="{base[0]}" stroke="#8A4A0A" stroke-width="1.2" opacity="0.95"/>'
                 f'<path d="M {_f(x2 - rx * 0.6)} {_f(yy - w1 * 0.25)} Q {_f(x2)} {_f(yy - w1 * 0.7)} {_f(x2 + rx * 0.4)} {_f(yy - w1 * 0.35)}" stroke="#FFF4D0" stroke-width="1.6" fill="none" opacity="0.8"/>')
    return "".join(o)


def honey_pool(u, cx, cy, rx, ry, seed, drips=(), base=AMBER, op=0.93):
    """Translucent glossy puddle of honey (things beneath show faintly through), with optional drips [(x, length, width)]."""
    pts = blob_pts(cx, cy, rx, ry, seed, 0.12, 18)
    d = smooth_closed(pts)
    dd = []
    for (dx_, L, w) in drips:
        dd.append(smooth_closed([(dx_ - w * 1.3, cy), (dx_ - w * 0.75, cy + L * 0.5), (dx_ - w * 0.8, cy + L), (dx_ - w * 0.5, cy + L + w * 0.75),
                                 (dx_, cy + L + w * 1.0), (dx_ + w * 0.5, cy + L + w * 0.75), (dx_ + w * 0.8, cy + L), (dx_ + w * 0.75, cy + L * 0.5), (dx_ + w * 1.3, cy)]))
    if dd:
        gd = u("hd")
        drip_svg = (f'<defs>{lgrad(gd, [(0, base[0]), (0.6, base[1]), (1, "#9A520C")])}</defs>' +
                    "".join(f'<path d="{x}" fill="#6A3608" opacity="0.25" transform="translate(2 4)"/><path d="{x}" fill="url(#{gd})" opacity="0.95"/>' + ink(x, "#7A3E08", 1.6, seed + i, 1, 0.6) for i, x in enumerate(dd)))
    else:
        drip_svg = ""
    g, cid = u("hp"), u("hpc")
    o = [drip_svg, f'<defs><radialGradient id="{g}" cx="0.4" cy="0.35" r="0.75"><stop offset="0" stop-color="{base[2]}"/><stop offset="0.5" stop-color="{base[0]}"/>'
         f'<stop offset="1" stop-color="{base[1]}"/></radialGradient><clipPath id="{cid}"><path d="{d}"/></clipPath></defs>',
         f'<path d="{d}" fill="#6A3608" opacity="0.25" transform="translate(2 5)"/>',
         f'<path d="{d}" fill="url(#{g})" opacity="{op}"/>',
         f'<g clip-path="url(#{cid})">' + glow(u, cx - rx * 0.1, cy, rx * 0.7, "#FFE69A", 0.5, ry * 0.7) +
         brush((cx - rx, cy - ry, cx + rx, cy + ry + 60), ["#FFD87A", "#C86A10"], seed, rx * ry / 120, -10, (rx * 0.2, rx * 0.5), (1.2, 3), (0.12, 0.3), 0.2) + "</g>",
         f'<path d="M {_f(cx - rx * 0.6)} {_f(cy - ry * 0.3)} Q {_f(cx - rx * 0.1)} {_f(cy - ry * 0.75)} {_f(cx + rx * 0.45)} {_f(cy - ry * 0.45)}" stroke="#FFFFFF" '
         f'stroke-width="{max(2.4, ry * 0.12):.1f}" fill="none" stroke-linecap="round" opacity="0.75"/>',
         ink(d, "#7A3E08", 1.8, seed, 1, 0.6)]
    for (dx_, L, w) in drips:
        o.append(f'<path d="M {_f(dx_ - w * 0.35)} {_f(cy + 4)} L {_f(dx_ - w * 0.35)} {_f(cy + L - 2)}" stroke="#FFF4D0" stroke-width="{max(1.6, w * 0.3):.1f}" stroke-linecap="round" opacity="0.8"/>'
                 f'<circle cx="{_f(dx_ - w * 0.3)}" cy="{_f(cy + L + w * 0.4)}" r="{max(1.4, w * 0.24):.1f}" fill="#FFFFFF" opacity="0.85"/>')
    return "".join(o)


def box_hive2(u, cx, base, w, seed, supers=None, roof=("#C8684A", "#8A3A24", "#E8987A"), stand=WOOD):
    """A painted wooden beehive in three-quarter view: stand, landing board, stacked boxes with a receding side, gabled roof."""
    supers = supers or [(0.5, ("#E8E2CC", "#B8AE90", "#FFFBEE")), (0.36, ("#F2CE72", "#C8962E", "#FFEDB0")), (0.36, ("#BCCCB0", "#86987A", "#E2ECD6"))]
    dx, dy = w * 0.28, -w * 0.15
    x0, x1 = cx - w / 2 - dx / 2, cx + w / 2 - dx / 2
    o = [shadow(u, cx + dx * 0.4, base + 2, w * 0.82, 16, 0.42)]
    # stand legs and landing board
    for lx in (x0 + 10, x1 - 10, x1 + dx - 8):
        back = lx > x1
        d = soft_poly([(lx - 6, base - 46 + (dy if back else 0)), (lx + 6, base - 46 + (dy if back else 0)), (lx + 5, base + (dy if back else 0)), (lx - 5, base + (dy if back else 0))], seed + int(lx), 0.6, 0.1)
        o.append(form(u, d, (lx - 7, base - 50 + dy, lx + 7, base), stand[1] if back else stand[0], stand[1], stand[2], seed + int(lx), -90, n=8, shade=(3, 0), ink_w=1.8))
    y = base - 46
    lb = soft_poly([(x0 - 22, y), (x1 + 8, y), (x1 + 8 + dx, y + dy), (x0 - 22 + dx * 0.4, y + dy * 0.6)], seed + 2, 0.8, 0.06)
    o.append(form(u, lb, (x0 - 22, y + dy, x1 + dx + 8, y), stand[2], stand[1], "#FFF0D0", seed + 3, 0, n=30, shade=None, ink_w=2.0))
    lbf = soft_poly([(x0 - 22, y), (x1 + 8, y), (x1 + 8, y + 9), (x0 - 22, y + 9)], seed + 4, 0.6, 0.1)
    o.append(form(u, lbf, (x0 - 22, y, x1 + 8, y + 9), stand[0], stand[1], stand[2], seed + 5, 0, n=12, shade=None, ink_w=1.8))
    y -= 2
    for i, (hf, pal) in enumerate(supers):
        h = w * hf
        front = soft_poly([(x0, y), (x1, y), (x1, y - h), (x0, y - h)], seed + 10 + i, 0.8, 0.04)
        side = soft_poly([(x1, y), (x1 + dx, y + dy), (x1 + dx, y + dy - h), (x1, y - h)], seed + 20 + i, 0.8, 0.04)
        rnd = random.Random(seed + i)
        grain_ = "".join(f'<path d="M {_f(x0 + 4)} {_f(y - h * t)} q {_f(w * 0.4)} {rnd.uniform(-2.5, 2.5):.1f} {_f(x1 - x0 - 8)} {rnd.uniform(-1.5, 1.5):.1f}" stroke="{pal[1]}" stroke-width="1.3" fill="none" opacity="0.55"/>' for t in (0.22, 0.5, 0.78))
        knots = f'<ellipse cx="{_f(x0 + (x1 - x0) * rnd.uniform(0.2, 0.8))}" cy="{_f(y - h * rnd.uniform(0.3, 0.7))}" rx="5" ry="2.4" fill="none" stroke="{pal[1]}" stroke-width="1.2" opacity="0.6"/>'
        o.append(form(u, front, (x0, y - h, x1, y), pal[0], pal[1], pal[2], seed + 30 + i, -2, n=w * h / 60, shade=None, ink_w=2.2,
                      length=(20, 60), width=(1.2, 3), sop=(0.14, 0.34), extra_in=grain_ + knots +
                      f'<rect x="{_f(x0)}" y="{_f(y - h)}" width="{_f(x1 - x0)}" height="6" fill="{pal[2]}" opacity="0.7"/>'
                      f'<rect x="{_f(x0)}" y="{_f(y - 5)}" width="{_f(x1 - x0)}" height="5" fill="{pal[1]}" opacity="0.5"/>'))
        hh = (f'<path d="M {_f(x1 + dx * 0.3)} {_f(y + dy * 0.3 - h * 0.6)} L {_f(x1 + dx * 0.7)} {_f(y + dy * 0.7 - h * 0.6)}" stroke="#3A2A1A" stroke-width="7" stroke-linecap="round" opacity="0.55"/>')
        o.append(form(u, side, (x1, y + dy - h, x1 + dx, y), pal[1], mixc(pal[1], "#2A1A0A", 0.3), pal[0], seed + 40 + i, -90 + 28, n=dx * h / 70, shade=None, ink_w=2.2,
                      length=(10, 40), width=(1, 2.6), sop=(0.15, 0.35), extra_in=hh))
        if i == 0:
            ent = soft_poly([(x0 + w * 0.18, y), (x1 - w * 0.18, y), (x1 - w * 0.18, y - 13), (x0 + w * 0.18, y - 13)], seed + 6, 0.6, 0.2)
            o.append(f'<path d="{ent}" fill="#1E1008"/>' + ink(ent, "#1E1008", 1.6, seed + 6, 1, 0.8))
        y -= h
    # gabled roof: front gable, visible right-hand slope with shingles
    ov = 10
    rt = y - w * 0.34
    ridge_f, ridge_b = (cx - dx / 2, rt), (cx - dx / 2 + dx, rt + dy)
    gable = soft_poly([(x0 - ov, y + 4), (x1 + ov, y + 4), ridge_f], seed + 50, 0.8, 0.08)
    slope = soft_poly([ridge_f, ridge_b, (x1 + ov + dx, y + 4 + dy), (x1 + ov, y + 4)], seed + 51, 0.8, 0.05)
    shing = []
    for t in (0.25, 0.5, 0.75):
        a = (ridge_f[0] + (x1 + ov - ridge_f[0]) * t, ridge_f[1] + (y + 4 - ridge_f[1]) * t)
        shing.append(f"M {_f(a[0])} {_f(a[1])} l {_f(dx)} {_f(dy)}")
    for t in (0.2, 0.4, 0.6, 0.8):
        a = (ridge_f[0] + dx * t, ridge_f[1] + dy * t)
        shing.append(f"M {_f(a[0])} {_f(a[1])} l {_f(x1 + ov - ridge_f[0])} {_f(y + 4 - ridge_f[1])}")
    o.append(form(u, slope, (ridge_f[0], ridge_b[1], x1 + ov + dx, y + 4), roof[0], roof[1], roof[2], seed + 52, 40, n=w * 0.8, shade=None, ink_w=2.4,
                  length=(12, 36), width=(1.2, 3), extra_in=f'<path d="{" ".join(shing)}" stroke="{roof[1]}" stroke-width="2" opacity="0.6"/>'))
    o.append(form(u, gable, (x0 - ov, rt, x1 + ov, y + 4), "#F2E6CC", "#C8B48E", "#FFFBEE", seed + 53, -90, n=w * 0.6, shade=None, ink_w=2.4,
                  length=(10, 30), width=(1.2, 3)))
    o.append(f'<path d="M {_f(x0 - ov - 2)} {_f(y + 6)} L {_f(ridge_f[0])} {_f(rt - 4)} L {_f(x1 + ov + 2)} {_f(y + 6)}" stroke="{roof[0]}" stroke-width="9" fill="none" stroke-linejoin="round" stroke-linecap="round"/>'
             f'<path d="M {_f(x0 - ov - 2)} {_f(y + 6)} L {_f(ridge_f[0])} {_f(rt - 4)} L {_f(x1 + ov + 2)} {_f(y + 6)}" stroke="{roof[1]}" stroke-width="2" fill="none" stroke-linejoin="round" transform="translate(0 4)" opacity="0.7"/>')
    o.append(f'<path d="{heart_path(ridge_f[0], (rt + y) / 2 + 8, 11)}" fill="{roof[0]}" stroke="{roof[1]}" stroke-width="1.6"/>')
    return "".join(o)


def picket_fence(u, y, seed, x0=-10, x1=610, h=70, gap=30, col=("#F6F0E2", "#C8BCA4", "#FFFFFF")):
    rnd = random.Random(seed)
    o = []
    rails = f"M {x0} {y - h * 0.3} L {x1} {y - h * 0.32} M {x0} {y - h * 0.75} L {x1} {y - h * 0.77}"
    o.append(f'<path d="{rails}" stroke="{col[1]}" stroke-width="9" stroke-linecap="round"/><path d="{rails}" stroke="{col[0]}" stroke-width="6" stroke-linecap="round" transform="translate(0 -1)"/>')
    x = x0
    while x < x1:
        hh = h * rnd.uniform(0.96, 1.04)
        d = soft_poly([(x, y), (x + 16, y), (x + 16, y - hh + 8), (x + 8, y - hh), (x, y - hh + 8)], seed + int(x), 0.5, 0.1)
        o.append(f'<path d="{d}" fill="{col[0]}"/><path d="M {x + 11} {y - 2} L {x + 11} {y - hh + 10}" stroke="{col[1]}" stroke-width="5" opacity="0.55"/>'
                 + ink(d, "#8A7A62", 1.4, seed + int(x), 1, 0.55))
        x += gap
    return "".join(o)


def rose(u, cx, cy, r, seed, pal=("#E88A9A", "#B04A62", "#FAC4CC"), rot=0):
    """A cupped garden rose: overlapping outer petals and a spiral heart."""
    rnd = random.Random(seed)
    o = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    base = blob(cx, cy, r, r * 0.9, seed, 0.1, 14)
    o.append(form(u, base, (cx - r, cy - r, cx + r, cy + r), pal[0], pal[1], pal[2], seed, lambda x, y: math.degrees(math.atan2(y - cy, x - cx)),
                  n=r * r / 10, shade=(r * 0.1, r * 0.12), shade_op=0.5, ink_w=max(1, r * 0.04), ink_col=pal[1], length=(r * 0.2, r * 0.5),
                  width=(0.8, max(1.2, r * 0.06))))
    for i, a in enumerate((200, 260, 320, 20, 80, 140)):
        ar = math.radians(a + rnd.uniform(-10, 10))
        px, py = cx + math.cos(ar) * r * 0.48, cy + math.sin(ar) * r * 0.42
        pd = f"M {_f(px - math.sin(ar) * r * 0.45)} {_f(py + math.cos(ar) * r * 0.4)} Q {_f(px + math.cos(ar) * r * 0.42)} {_f(py + math.sin(ar) * r * 0.42)} {_f(px + math.sin(ar) * r * 0.45)} {_f(py - math.cos(ar) * r * 0.4)}"
        o.append(f'<path d="{pd}" stroke="{pal[1]}" stroke-width="{max(1, r * 0.06):.1f}" fill="none" stroke-linecap="round" opacity="0.6"/>')
    sp = [(cx + math.cos(t) * r * 0.06 * t, cy + math.sin(t) * r * 0.05 * t) for t in [i * 0.5 for i in range(1, 14)]]
    o.append(f'<path d="{blob(cx, cy, r * 0.42, r * 0.36, seed + 2, 0.12, 12)}" fill="{mixc(pal[0], pal[1], 0.35)}"/>')
    o.append(f'<path d="{smooth_open(sp)}" stroke="{pal[1]}" stroke-width="{max(1.2, r * 0.07):.1f}" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="M {_f(cx - r * 0.5)} {_f(cy - r * 0.45)} Q {_f(cx - r * 0.1)} {_f(cy - r * 0.75)} {_f(cx + r * 0.35)} {_f(cy - r * 0.55)}" stroke="{pal[2]}" stroke-width="{max(1.2, r * 0.08):.1f}" fill="none" stroke-linecap="round" opacity="0.8"/>')
    o.append("</g>")
    return "".join(o)


def cottage(u, x, base, w, h, seed, wall=("#E8D8BC", "#B8A484", "#FFF4DE"), roof=("#8A4A3A", "#5A2A20", "#B06A54"), lit=True, chimney=True):
    """A small storybook cottage (front gable), lit windows glowing at night."""
    o = []
    wd = soft_poly([(x - w / 2, base), (x + w / 2, base), (x + w / 2, base - h), (x - w / 2, base - h)], seed, 0.6, 0.06)
    o.append(form(u, wd, (x - w / 2, base - h, x + w / 2, base), wall[0], wall[1], wall[2], seed, -90, n=w * h / 50, shade=(w * 0.12, 0), ink_w=1.4, ink_col="#3A2418"))
    rf = soft_poly([(x - w / 2 - w * 0.12, base - h + 2), (x, base - h - w * 0.55), (x + w / 2 + w * 0.12, base - h + 2)], seed + 1, 0.6, 0.08)
    if chimney:
        ch = soft_poly([(x + w * 0.18, base - h - w * 0.2), (x + w * 0.32, base - h - w * 0.2), (x + w * 0.32, base - h - w * 0.62), (x + w * 0.18, base - h - w * 0.62)], seed + 2, 0.4, 0.1)
        o.append(f'<path d="{ch}" fill="{roof[1]}"/>')
    o.append(form(u, rf, (x - w * 0.62, base - h - w * 0.55, x + w * 0.62, base - h + 2), roof[0], roof[1], roof[2], seed + 3, 30, n=w * 0.6, shade=(w * 0.08, 0), ink_w=1.4, ink_col="#2A160E"))
    wins = [(x - w * 0.22, base - h * 0.55), (x + w * 0.22, base - h * 0.55)]
    for i, (wx, wy) in enumerate(wins):
        ww, wh = w * 0.18, h * 0.3
        if lit:
            o.append(glow(u, wx, wy, w * 0.32, "#FFC860", 0.6))
        o.append(f'<rect x="{_f(wx - ww / 2)}" y="{_f(wy - wh / 2)}" width="{_f(ww)}" height="{_f(wh)}" rx="1" fill="{"#FFD878" if lit else "#4A5A6A"}" stroke="#3A2418" stroke-width="1.2"/>'
                 f'<path d="M {_f(wx)} {_f(wy - wh / 2)} L {_f(wx)} {_f(wy + wh / 2)} M {_f(wx - ww / 2)} {_f(wy)} L {_f(wx + ww / 2)} {_f(wy)}" stroke="#3A2418" stroke-width="1"/>')
    dw, dh = w * 0.16, h * 0.42
    o.append(f'<path d="M {_f(x - dw / 2)} {base} L {_f(x - dw / 2)} {_f(base - dh + dw / 2)} A {_f(dw / 2)} {_f(dw / 2)} 0 0 1 {_f(x + dw / 2)} {_f(base - dh + dw / 2)} L {_f(x + dw / 2)} {base} Z" fill="#5A3A28" stroke="#2A160E" stroke-width="1.2"/>')
    return "".join(o)


def round_tree(u, x, base, r, seed, pal=("#3E5A4A", "#26382E", "#5E7A64"), trunk="#2A1E18"):
    o = [f'<path d="M {_f(x - r * 0.08)} {base} L {_f(x - r * 0.05)} {_f(base - r * 0.9)} L {_f(x + r * 0.05)} {_f(base - r * 0.9)} L {_f(x + r * 0.08)} {base} Z" fill="{trunk}"/>']
    d = " ".join(blob(x + dx * r, base - r * 1.25 + dy * r, rr * r, rr * r * 0.9, seed + i, 0.08, 12) for i, (dx, dy, rr) in enumerate(((-0.35, 0.1, 0.55), (0.35, 0.08, 0.55), (0, -0.25, 0.62))))
    o.append(form(u, d, (x - r, base - r * 2.1, x + r, base - r * 0.6), pal[0], pal[1], pal[2], seed, lambda px, py: math.degrees(math.atan2(py - base + r * 1.25, px - x)) + 90,
                  n=r * r / 12, shade=(r * 0.15, r * 0.1), ink_w=0, length=(r * 0.1, r * 0.3), width=(0.8, max(1.2, r * 0.06))))
    return "".join(o)


def poplar(u, x, base, h, seed, pal=("#6E7E4A", "#4A5A30", "#9AA86A")):
    w = h * 0.16
    d = smooth_closed([(x, base - h), (x + w * 0.7, base - h * 0.6), (x + w, base - h * 0.25), (x + w * 0.5, base - h * 0.05), (x - w * 0.5, base - h * 0.05),
                       (x - w, base - h * 0.25), (x - w * 0.7, base - h * 0.6)])
    return (f'<path d="M {x} {base} L {x} {_f(base - h * 0.1)}" stroke="#4A3A28" stroke-width="{max(1.5, w * 0.18):.1f}"/>' +
            form(u, d, (x - w, base - h, x + w, base), pal[0], pal[1], pal[2], seed, -90, n=h * w / 30, shade=(w * 0.3, 0), ink_w=0,
                 length=(h * 0.08, h * 0.25), width=(0.8, max(1.2, w * 0.12))))


def cloud2(u, cx, cy, w, h, seed, base="#FFF6EC", shade_c="#D8B8C8", light="#FFFFFF"):
    """A painted cumulus: a flat-bottomed row of puffs with a taller crown, lit from above."""
    rnd = random.Random(seed)
    puffs = []
    n = max(4, int(w / 34))
    for i in range(n):
        t = i / (n - 1)
        px = cx - w / 2 + w * t
        r = h * (0.45 + 0.55 * math.sin(math.pi * t)) * rnd.uniform(0.8, 1.05)
        puffs.append(blob(px, cy - r * 0.35, r * 0.75, r * 0.62, seed + i, 0.08, 12))
    for i in range(max(2, n - 3)):
        t = (i + 1) / (max(2, n - 3) + 1)
        px = cx - w * 0.32 + w * 0.64 * t
        r = h * (0.6 + 0.4 * math.sin(math.pi * t)) * rnd.uniform(0.85, 1.05)
        puffs.append(blob(px, cy - h * 0.55 - r * 0.2, r * 0.7, r * 0.6, seed + 40 + i, 0.08, 12))
    d = " ".join(puffs) + f" M {_f(cx - w / 2 - 6)} {_f(cy)} L {_f(cx + w / 2 + 6)} {_f(cy)} L {_f(cx + w / 2)} {_f(cy + h * 0.25)} L {_f(cx - w / 2)} {_f(cy + h * 0.25)} Z"
    return form(u, d, (cx - w / 2 - 20, cy - h * 1.5, cx + w / 2 + 20, cy + h * 0.3), base, shade_c, light, seed, -10, n=w * h / 70, shade=(3, h * 0.3),
                shade_op=0.55, hi=(cx - w * 0.1, cy - h * 1.0, w * 0.28, h * 0.22), hi_op=0.55, ink_w=0, length=(10, 30), width=(2, 5), sop=(0.15, 0.4))


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
    o.append(spot(u, 300, 246, 226, 186, ("#F8DFA4", "#EEC478", "#FFF0C8"), 14, paper_c="#F7EEDC", wob=0.03))
    o.append(glow(u, 300, 220, 220, "#FFE6A0", 0.55))
    # comb peeking in at two corners
    o.append(comb(u, comb_cells(600, 0, 40, 5, 5, keep=lambda x, y, c, r: math.hypot(x - 640, y + 20) < 190), 40, 21,
                  kinds=lambda i, x, y: ["honey", "capped", "honey", "empty"][i % 4]))
    o.append(comb(u, comb_cells(0, 600, 40, 5, 5, keep=lambda x, y, c, r: math.hypot(x + 40, y - 620) < 170), 40, 31,
                  kinds=lambda i, x, y: ["capped", "honey", "honey", "empty"][i % 4]))
    # big bee offers a daisy to a shy little one
    big = (226, 214, 84, 3, -4, True)
    hx, hy = bee_pt(*big[:3], big[4], True, -150, 46)
    o.append(trail([(118, 150), (96, 196), (120, 236), (136, 224)], INK, 2.4, "2 9", 0.45))
    o.append(bee(u, big[0], big[1], big[2], big[3], rot=big[4], flip=True, mood="smile", wings="up", pose="tuck",
                 arms=["M -64 36 Q -108 60 -150 46"]))
    o.append(stem([(hx - 2, hy + 6), (hx + 14, hy - 14), (hx + 26, hy - 38)], "#5E7A3A", 3.2, 4))
    o.append(green_leaf(u, hx + 12, hy - 12, 24, 8, -10, 5, vein=False))
    o.append(daisy(u, hx + 28, hy - 46, 24, 6, rot=-10))
    o.append(f'<circle cx="{_f(hx)}" cy="{_f(hy)}" r="5" fill="{NOIR}"/>')
    o.append(bee(u, 470, 236, 44, 7, rot=8, mood="smile", wings="up", pose="tuck", cheek="#F06A6A"))
    o.append(floating_hearts(u, [(412, 150, 9, -12), (440, 118, 6.5, 10), (392, 112, 5, -4)], 8))
    for x, y, sz in ((90, 140, 7), (520, 330, 6), (330, 70, 5), (110, 360, 5)):
        o.append(sparkle(x, y, sz, "#E8A830", 0.85))
    t, _, _ = btext(u, 300, 402, "bee", SERIF_IT, 100, INK, ["#5A3A24", "#2A1810", "#6E4A30"], 7, angle=-40, shadow="#E8B860", soff=(0.02, 0.04))
    o.append(t)
    t, _, _ = btext(u, 300, 530, "KIND", ANTON, 126, "#E8A225", ["#F6C450", "#C47A16", "#FFD87A", "#D8901C"], 8, ls=10, angle=-78,
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
    cx, cy, rx, ry = 300, 250, 190, 180
    ov = blob(cx, cy, rx, ry, 22, 0.012, 30)
    o.append(shadow(u, cx + 6, cy + 16, rx + 16, ry + 16, 0.45, "#4A2204"))
    o.append(form(u, blob(cx, cy, rx + 18, ry + 18, 23, 0.012, 30), (cx - rx - 18, cy - ry - 18, cx + rx + 18, cy + ry + 18), GOLD[0], GOLD[1], GOLD[2], 24,
                  lambda x, y: math.degrees(math.atan2(y - cy, x - cx)) + 90, n=260, shade=(10, 12), hi=(cx - 80, cy - 150, 60, 14), ink_w=2.4, ink_col="#7A4A0E",
                  length=(10, 30), width=(1.2, 3)))
    o.append(form(u, ov, (cx - rx, cy - ry, cx + rx, cy + ry), "#F4E8D2", "#D8C29C", "#FFFAF0", 25, -60, n=220, shade=(-8, -10), shade_op=0.3, ink_w=2.0,
                  ink_col="#7A4A0E", length=(20, 60), width=(2, 5), sop=(0.08, 0.2),
                  extra_in=glow(u, cx, cy - 10, 170, "#FFE29A", 0.55) + rays(cx, cy - 10, 20, "#F2C860", 0.1, r=200)))
    beads = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        bx, by = cx + (rx + 9) * math.cos(a), cy + (ry + 9) * math.sin(a)
        beads.append(f'<circle cx="{_f(bx)}" cy="{_f(by)}" r="4.4" fill="#FFF0B0" stroke="#9A6010" stroke-width="1.3"/><circle cx="{_f(bx - 1.2)}" cy="{_f(by - 1.2)}" r="1.4" fill="#FFFFFF"/>')
    o.append("".join(beads))
    for jx, jy in ((cx, cy - ry - 9), (cx - rx - 9, cy), (cx + rx + 9, cy)):
        o.append(f'<path d="{blob(jx, jy, 11, 13, int(jx), 0.04, 10)}" fill="#C8344A" stroke="#6A1018" stroke-width="2"/><circle cx="{jx - 3}" cy="{jy - 4}" r="3" fill="#FFFFFF" opacity="0.8"/>')
    # laurel of sage leaves and tiny daisies around the lower half of the cameo
    for side in (-1, 1):
        arc = [(cx + side * (rx - 26) * math.cos(math.radians(a)), cy + (ry - 26) * math.sin(math.radians(a))) for a in range(-10, 91, 10)]
        o.append(ink(smooth_open(arc), "#8E9A6E", 3, 26 + side, 1, 0.9))
        for i, (vx, vy) in enumerate(arc[:-1]):
            tang = math.degrees(math.atan2(arc[i + 1][1] - vy, arc[i + 1][0] - vx))
            for k in (-1, 1):
                o.append(green_leaf(u, vx, vy, 26, 8, tang + k * 48, 27 + i * 3 + k + side * 50, pal=SAGE, vein=False, inkc="#4E5A34"))
        for j, a in enumerate((12, 52)):
            o.append(daisy(u, cx + side * (rx - 26) * math.cos(math.radians(a)), cy + (ry - 26) * math.sin(math.radians(a)), 13, 40 + j + side * 9, n=11))
    # the queen, with a honey-dipper sceptre
    bq = (322, 236, 100, -4)
    sx, sy = bee_pt(bq[0], bq[1], bq[2], bq[3], False, -142, 30)
    o.append(bee(u, bq[0], bq[1], bq[2], 28, rot=bq[3], mood="calm", crown=True, wings="up", eye_dir=(2, 0), lashes=True, pose="tuck",
                 arms=["M -64 36 Q -110 56 -142 30"], cheek="#F07A70"))
    o.append(dipper(u, sx + 30, sy + 46, 150, -112, 31, scale=0.62, honey=True))
    o.append(f'<circle cx="{_f(sx)}" cy="{_f(sy)}" r="5.6" fill="{NOIR}"/>')
    for x, y, sz in ((112, 92, 9), (488, 96, 8), (530, 360, 6), (70, 330, 6)):
        o.append(sparkle(x, y, sz, "#FFF4C8", 0.9))
    o.append(ribbon(u, 300, 476, 410, 78, ("#3A2418", "#1E120A", "#5A3A26"), 29, tail=40, ink_col="#120A04"))
    t, _, _ = btext(u, 300, 503, "QUEEN BEE", CINZEL, 62, "#F6CE5A", ["#FFE08A", "#D49A22", "#FFF0B8"], 30, max_w=370, ls=4, angle=-70)
    o.append(t)
    o.append(plain(300, 550, "OF THE HIVE", JOST, 20, "#FFF4D8", ls=8))
    o.append(finish(u, "#FFE8B0", 0.5))
    return "".join(o)


# ================================================================ mind your own beeswax
@design("mind-your-own-beeswax")
def beeswax():
    u = Ids("mind-your-own-beeswax")
    o = [bg(u, "#2E2016", ["#3A2A1E", "#22180E", "#46342A", "#1A120A"], 31, fleck="#F2D8A8", angle=-25)]
    o.append(glow(u, 350, 250, 280, "#F2A83A", 0.45))
    o.append(drip_curtain(u, 46, -20, 32, depth=(16, 86), wid=(40, 74), band_hi=False))
    # wooden table, lit by the candle
    tb = smooth_closed([(-20, 386), (300, 380), (620, 386), (620, 640), (-20, 640)])
    o.append(form(u, tb, (-20, 374, 620, 640), "#5A3A26", "#2E1C10", "#7A5236", 33, -2, n=140, shade=None, ink_w=0, length=(40, 120), width=(2, 5)))
    o.append(glow(u, 360, 392, 230, "#F6B04A", 0.35, 34))
    o.append(f'<path d="M -10 384 Q 300 376 610 384" stroke="#A87A50" stroke-width="2.4" fill="none" opacity="0.6"/>')
    o.append(candle(u, 352, 230, 128, 150, 34))
    # a little dish of comb and a resting dipper
    o.append(shadow(u, 506, 392, 62, 10, 0.5))
    o.append(f'<ellipse cx="502" cy="386" rx="60" ry="13" fill="#E8DCC4" stroke="#6A5034" stroke-width="2"/><ellipse cx="502" cy="383" rx="46" ry="8" fill="#C8B898"/>')
    o.append(comb(u, comb_cells(502, 366, 13, 2, 4), 13, 155, kinds=["honey", "capped", "honey", "honey", "empty", "honey", "capped", "honey"]))
    # the bee leaning back against the candle, side-eyeing us
    o.append(bee(u, 186, 302, 74, 35, rot=-4, mood="calm", wings="flat", eye_dir=(-5, -1), pose="stand",
                 arms=["M -62 38 Q -80 64 -60 70"], cheek="#E87A6A"))
    t, _, _ = btext(u, 300, 456, "mind your own", SERIF_IT, 58, "#FBEBD2", ["#FFF6E6", "#E8D2B4"], 36, max_w=430, angle=-35, shadow="#120A04",
                    soff=(0.02, 0.05))
    o.append(t)
    t, _, _ = btext(u, 300, 548, "BEESWAX", ANTON, 104, "#F2B33A", ["#F6C450", "#C47A16", "#FFD87A"], 37, max_w=460, ls=6, angle=-78,
                    shadow="#120A04", soff=(0.025, 0.04), hi="#FFF0C0")
    o.append(t)
    o.append(finish(u, "#F2D8A8", 0.5))
    return "".join(o)


# ================================================================ bee happy
@design("bee-happy")
def bee_happy():
    u = Ids("bee-happy")
    o = [bg(u, "#F6C844", ["#F8D25A", "#EAB030", "#FBE07A", "#E8A82A"], 41, fleck="#8A5A10", angle=-20)]
    o.append(rays(300, 330, 26, "#FFF0A8", 0.35, rot=4))
    o.append(glow(u, 300, 320, 250, "#FFF6C8", 0.65))
    t, _, _ = btext(u, 300, 166, "bee happy", SERIF_IT, 116, "#3A2418", ["#5A3A24", "#2A1810", "#6E4A30"], 42, max_w=470, angle=-40,
                    shadow="#FFF2C0", soff=(-0.02, -0.025))
    o.append(t)
    o.append(ruled_c(u, 212, "SUNNY DAYS · SWEET FLOWERS", JOST, 18, "#7A4A12", 46, ls=4, line_w=26))
    o.append(loop_trail(70, 352, 206, 318, 26, INK, 2.6, 0.5, up=True))
    o.append(bee(u, 160, 432, 22, 47, rot=10, mood="smile", wings="spread"))
    o.append(bee(u, 334, 330, 92, 43, rot=-12, mood="grin", wings="spread", pose="tuck"))
    for x, y, sz in ((520, 250, 9), (86, 250, 6), (512, 400, 7), (236, 262, 5)):
        o.append(sparkle(x, y, sz, "#FFFFFF", 0.9))
    o.append(wildflower_band(u, 478, 44, kinds=("daisy", "clover", "lav", "daisy", "corn"), scale=0.9))
    o.append(wildflower_band(u, 540, 48, kinds=("daisy", "cosmos", "daisy", "poppy", "daisy"), scale=1.6, x0=-40, x1=640))
    o.append(finish(u, INK, 0.6))
    return "".join(o)


# ================================================================ sweet as honey
@design("sweet-as-honey")
def sweet_as_honey():
    u = Ids("sweet-as-honey")
    o = [bg(u, "#F8E8D2", ["#F6DCC0", "#FBF2E4", "#F2D4B0", "#F8E2C8"], 51, angle=-20)]
    o.append(glow(u, 420, 300, 300, "#FFC86A", 0.45))
    t, _, _ = btext(u, 250, 118, "sweet as", SERIF_IT, 78, "#6A3A1A", ["#8A5230", "#4A2410"], 52, angle=-40, shadow="#F2C890", soff=(0.02, 0.04), max_w=330)
    o.append(t)
    t, _, _ = btext(u, 250, 236, "HONEY", ANTON, 126, "#E0921E", ["#F6C450", "#B86A10", "#FFD87A", "#D8901C"], 53, ls=8, angle=-78, max_w=360,
                    shadow="#6A3A1A", soff=(0.025, 0.035), hi="#FFF0C0")
    o.append(t)
    # a slab of comb across the bottom
    cells = comb_cells(300, 474, 38, 5, 11)
    slab = smooth_closed([(-20, 360), (80, 334), (180, 342), (300, 330), (420, 338), (520, 328), (620, 344), (620, 640), (-20, 640)])
    o.append(shadow(u, 300, 340, 340, 22, 0.35))
    cid = u("sl")
    o.append(f'<defs><clipPath id="{cid}"><path d="{slab}"/></clipPath></defs><path d="{slab}" fill="#C88A2E"/><g clip-path="url(#{cid})">')
    o.append(comb(u, cells, 38, 54, kinds=lambda i, x, y: "capped" if (i * 7) % 5 == 0 else ("empty" if (i * 3) % 7 == 0 else "honey")))
    o.append("</g>")
    o.append(ink(slab, "#7A4A16", 2.4, 55, 2, 0.8))
    # honey falling from a dipper and pooling over the comb, running over the edge of the cells
    o.append(honey_pool(u, 446, 400, 86, 30, 56, drips=((392, 64, 9), (470, 104, 11), (512, 46, 8))))
    o.append(honey_stream(u, 474, 168, 450, 390, 57, w0=13, w1=6, sway=-14))
    o.append(dipper(u, 610, 70, 186, 151, 58, scale=0.95, honey=True))
    # a bee sipping from a cell through a striped straw
    o.append(bee(u, 150, 296, 48, 59, rot=-2, mood="sleep", wings="up", pose="stand", arms=["M -62 40 Q -76 50 -92 54"]))
    o.append(f'<path d="M 106 318 L 92 372" stroke="#F2EEE6" stroke-width="6" stroke-linecap="round"/><path d="M 106 318 L 92 372" stroke="#D84A4A" stroke-width="6" stroke-dasharray="5 5" stroke-linecap="butt"/>')
    for x, y, sz in ((520, 110, 8), (556, 300, 6), (70, 180, 6)):
        o.append(sparkle(x, y, sz, "#E8A830", 0.85))
    o.append(finish(u, INK, 0.6))
    return "".join(o)


# ================================================================ hive sweet hive
@design("hive-sweet-hive")
def hive_sweet_hive():
    u = Ids("hive-sweet-hive")
    sky = u("sk")
    o = [bg(u, "#EAF0E2", ["#E2EAD6", "#F2F5EC", "#D8E2CA", "#EEF2E6"], 61, fleck="#6E7A50", angle=-15)]
    o.append(f'<defs>{lgrad(sky, [(0, "#C4DCE4"), (0.55, "#F2EEDC"), (1, "#F8E4BC")])}</defs><rect width="600" height="460" fill="url(#{sky})" opacity="0.9"/>')
    o.append(glow(u, 500, 250, 240, "#FFE6A8", 0.6))
    # distant hills, hazy; a hedge; the garden lawn
    o.append(hill(u, [(-20, 362), (90, 334), (210, 350), (330, 326), (450, 344), (620, 322)], 640, "#B8C8B0", "#9AAE98", "#D8E2D0", 62))
    o.append(hill(u, [(-20, 392), (120, 376), (260, 388), (400, 370), (520, 382), (620, 372)], 640, "#9AB07A", "#7A9460", "#BCCC9C", 63))
    o.append(fruit_tree(u, 92, 470, 72, 64, greens=("#7E9A58", "#56703A", "#A8C27A"), fruit=26, fruitc=("#F4B8C4", "#FFFFFF")))
    o.append(fruit_tree(u, 540, 432, 46, 65, greens=("#8EA668", "#66804A", "#B4C88C"), fruit=14, fruitc=("#F4B8C4", "#FFFFFF"), detail=False))
    o.append(picket_fence(u, 470, 66, gap=32, h=64))
    o.append(hill(u, [(-20, 466), (150, 458), (300, 464), (450, 456), (620, 462)], 640, "#8EA466", "#6E8A44", "#B4C67E", 67))
    o.append(grass(68, (-20, 460, 620, 600), ["#6E8A44", "#A8BC70", "#5E7A3A"], 200, (8, 22), 2.0))
    # stepping stones to the hive
    for i, (x, y, r) in enumerate(((246, 586, 22), (276, 556, 18), (298, 532, 14))):
        o.append(form(u, blob(x, y, r, r * 0.45, 69 + i, 0.1, 12), (x - r, y - r * 0.5, x + r, y + r * 0.5), "#E2D6BE", "#B0A084", "#FFF8E8", 69 + i, 0, n=10, shade=(0, -3), ink_w=1.4, ink_col="#7A6A50"))
    o.append(box_hive2(u, 314, 520, 168, 70))
    # hollyhocks right, lavender and daisies left
    for i, (x, b, h) in enumerate(((520, 600, 250), (480, 600, 200))):
        o.append(stem([(x, b), (x + 4, b - h * 0.5), (x - 2, b - h)], "#5E7A3A", 4, 71 + i))
        for kk in range(6):
            yy = b - h + kk * 30
            r = 21 - kk * 1.3
            o.append(cosmos(u, x + (kk % 2) * 10 - 5, yy, r, 72 + i * 10 + kk, pal=ROSE if i == 0 else ("#F2B8C8", "#C07890", "#FFE0EA"), n=6, tilt=0.9))
        o.append(green_leaf(u, x, b - 50, 50, 15, -30 if i == 0 else -150, 90 + i))
    o.append(lavender(u, 108, 600, 150, 91, ang=-96, buds=10) + lavender(u, 128, 600, 130, 92, ang=-82, buds=9) + lavender(u, 82, 600, 120, 93, ang=-104, buds=8))
    o.append(daisy(u, 174, 560, 18, 94, tilt=0.8) + daisy(u, 200, 584, 15, 95, tilt=0.8) + daisy(u, 410, 572, 16, 96, tilt=0.8))
    # bees coming home
    o.append(trail([(196, 300), (226, 352), (262, 408), (288, 450)], INK, 2.2, "2 8", 0.5))
    o.append(bee(u, 182, 290, 26, 97, rot=14, mood="smile", wings="spread"))
    o.append(bee(u, 444, 322, 30, 98, rot=-8, flip=True, mood="smile", wings="up"))
    o.append(bee(u, 380, 248, 20, 99, rot=-16, flip=True, mood="wink", wings="spread"))
    t, _, _ = btext(u, 300, 118, "hive sweet hive", SERIF_IT, 78, "#3A2418", ["#5A3A24", "#2A1810", "#6E4A30"], 76, max_w=470, angle=-40,
                    shadow="#F6E6C0", soff=(0.02, 0.04))
    o.append(t)
    o.append(ruled_c(u, 168, "HOME IS WHERE THE HONEY IS", JOST, 19, "#7A4A16", 77, ls=4, line_w=30))
    o.append(finish(u, INK, 0.55))
    return "".join(o)


# ================================================================ the bee's knees
@design("bees-knees")
def bees_knees():
    u = Ids("bees-knees")
    o = [bg(u, "#241A12", ["#2E2218", "#1A120A", "#3A2A1E"], 81, fleck="#F2D8A8", angle=-25)]
    o.append(glow(u, 300, 250, 270, "#E8A030", 0.35))
    fan = []
    for i in range(19):
        a = math.radians(180 + i * 10)
        fan.append(f"M {_f(300 + 74 * math.cos(a))} {_f(342 + 74 * math.sin(a))} L {_f(300 + 252 * math.cos(a))} {_f(342 + 252 * math.sin(a))}")
    o.append(f'<path d="{" ".join(fan)}" stroke="#E2A83A" stroke-width="3" opacity="0.5"/>')
    for r in (74, 116, 252):
        o.append(f'<path d="M {300 - r} 342 A {r} {r} 0 0 1 {300 + r} 342" stroke="#E2A83A" stroke-width="{4 if r == 252 else 3}" fill="none" opacity="0.7"/>')
    for inset, w_ in ((44, 3.2), (54, 1.6)):
        a, b = inset, 600 - inset
        st = 26
        pts = [(a + st, a), (b - st, a), (b - st, a + st * 0.4), (b - st * 0.4, a + st * 0.4), (b - st * 0.4, a + st), (b, a + st),
               (b, b - st), (b - st * 0.4, b - st), (b - st * 0.4, b - st * 0.4), (b - st, b - st * 0.4), (b - st, b),
               (a + st, b), (a + st, b - st * 0.4), (a + st * 0.4, b - st * 0.4), (a + st * 0.4, b - st), (a, b - st),
               (a, a + st), (a + st * 0.4, a + st), (a + st * 0.4, a + st * 0.4), (a + st, a + st * 0.4)]
        o.append(ink(poly_d(jitter(pts, inset, 0.5)), "#E2A83A", w_, inset, 1, 0.9))
    # spotlight and a little round stage
    sl = u("sl")
    o.append(f'<defs>{lgrad(sl, [(0, "#FFF4D0", 0.0), (0.5, "#FFE8A8", 0.16), (1, "#FFE8A8", 0.3)])}</defs>'
             f'<path d="M 262 60 L 338 60 L 440 340 L 160 340 Z" fill="url(#{sl})"/>')
    stage_top = smooth_closed([(160, 344), (300, 330), (440, 344), (300, 358)])
    o.append(f'<path d="M 160 344 L 160 366 Q 300 392 440 366 L 440 344 Z" fill="#7A1E28"/><path d="M 160 366 Q 300 392 440 366" stroke="#E2A83A" stroke-width="3" fill="none"/>')
    o.append(form(u, stage_top, (160, 328, 440, 360), "#C8944A", "#8A5A2A", "#F2C47A", 84, 0, n=40, shade=None, ink_w=2.2, ink_col="#E2A83A", ink_op=0.9))
    o.append(glow(u, 300, 344, 130, "#FFE8A8", 0.45, 14))
    bow = ('<path d="M -84 52 L -118 32 L -114 78 Z M -84 52 L -52 32 L -54 76 Z" fill="#C8344A" stroke="#4A0E14" stroke-width="3" stroke-linejoin="round"/>'
           '<path d="M -110 42 L -108 68 M -58 42 L -60 66" stroke="#F6B0A8" stroke-width="3" opacity="0.6"/>'
           '<ellipse cx="-84" cy="54" rx="9" ry="11" fill="#A82034" stroke="#4A0E14" stroke-width="3"/>')
    hat = ('<g transform="rotate(-14 -100 -58)"><ellipse cx="-100" cy="-54" rx="64" ry="13" fill="#E8C878" stroke="#6A4A1A" stroke-width="3"/>'
           '<path d="M -138 -56 L -136 -94 Q -100 -102 -64 -94 L -62 -56 Q -100 -48 -138 -56 Z" fill="#F2D68A" stroke="#6A4A1A" stroke-width="3"/>'
           '<path d="M -137 -68 Q -100 -60 -63 -68 L -63 -78 Q -100 -70 -137 -78 Z" fill="#2A1D14"/>'
           '<ellipse cx="-100" cy="-95" rx="36" ry="7" fill="#F8E0A0" stroke="#6A4A1A" stroke-width="2.4"/>'
           '<path d="M -130 -86 l 10 -1 M -112 -88 l 12 0 M -128 -60 l 10 1" stroke="#B8944A" stroke-width="2" opacity="0.7"/></g>')
    o.append(bee(u, 318, 246, 92, 82, rot=-6, mood="wink", wings="spread", head_over=bow + hat, pose="kick", knee="#D8344A"))
    for x, y, sz in ((116, 116, 8), (484, 116, 8), (100, 300, 6), (500, 300, 6)):
        o.append(sparkle(x, y, sz, "#F6D07A", 0.9))
    o.append(plain(300, 444, "you're the", SERIF_IT, 50, "#FBEBD2"))
    t, _, _ = btext(u, 300, 532, "BEE'S KNEES", BEBAS, 108, "#F2B94A", ["#F6CE6A", "#C8841E", "#FFE08A"], 83, max_w=430, ls=5, angle=-78,
                    shadow="#000000", soff=(0.02, 0.035), hi="#FFF0C0")
    o.append(t)
    o.append(finish(u, "#F2D8A8", 0.45))
    return "".join(o)


# ================================================================ bee mine
@design("bee-mine")
def bee_mine():
    u = Ids("bee-mine")
    o = [bg(u, "#F6D8CE", ["#F2CCC0", "#FBE6DE", "#EEC0B4", "#F8DCD2"], 91, fleck="#8A4A40", angle=-20)]
    o.append(glow(u, 300, 250, 260, "#FFF0E8", 0.6))
    big = heart_path(300, 236, 150)
    o.append(form(u, big, (60, 0, 540, 430), "#F8C4BC", "#EEA8A0", "#FFE2DC", 92, -40, n=200, shade=None, ink_w=0, length=(30, 90), width=(4, 10), sop=(0.1, 0.25)))
    # sprays of roses and leaves in the two top corners
    for side in (-1, 1):
        bx = 300 + side * 262
        for i, (dx, dy, L, a) in enumerate(((0, 40, 70, 90 + side * 30), (side * -40, 70, 60, 90 + side * 60), (side * -10, 10, 60, 90 + side * 5))):
            o.append(green_leaf(u, bx + dx, dy, L, 18, a, 93 + i + side * 10, pal=SAGE, inkc="#4E5A34"))
        o.append(rose(u, bx - side * 6, 56, 40, 100 + side, rot=side * 20))
        o.append(rose(u, bx - side * 56, 30, 26, 102 + side, pal=("#F2B0B8", "#C06878", "#FFE0E4"), rot=side * -10))
        o.append(cosmos(u, bx - side * 10, 116, 18, 104 + side, pal=("#F8E2E0", "#C89A98", "#FFFFFF"), n=7))
    o.append(floating_hearts(u, [(110, 260, 13, -14), (500, 300, 11, 12), (468, 168, 8, -6), (150, 380, 8, 10), (530, 420, 7, -8)], 105))
    hx, hy = bee_pt(372, 300, 86, -6, False, -150, 30)
    o.append(f'<path d="M {_f(hx)} {_f(hy)} C {_f(hx - 30)} {_f(hy - 50)} 250 270 222 228" stroke="#6A3A30" stroke-width="2.4" fill="none"/>')
    o.append(heart_balloon(u, 216, 160, 62, 106))
    o.append(f'<path d="M 214 226 l 7 -9 l 7 9 Z" fill="#9A2028"/>')
    o.append(bee(u, 372, 300, 86, 94, rot=-6, mood="smile", wings="up", pose="tuck", arms=["M -64 36 Q -110 56 -150 30"], lashes=True))
    o.append(f'<circle cx="{_f(hx)}" cy="{_f(hy)}" r="5" fill="{NOIR}"/>')
    t, _, _ = btext(u, 300, 504, "bee mine", DMS, 124, "#9A2028", ["#B83038", "#7A1018", "#C84850"], 95, max_w=440, angle=-60,
                    shadow="#F6B8AC", soff=(0.02, 0.04), hi="#F8A0A0")
    o.append(t)
    o.append(ruled_c(u, 552, "X O X O", JOS, 20, "#9A2028", 96, ls=6, line_w=40))
    o.append(finish(u, "#6A2A20", 0.5))
    return "".join(o)


# ================================================================ bee brave
@design("bee-brave")
def bee_brave():
    u = Ids("bee-brave")
    sk = u("sk")
    o = [bg(u, "#24404C", ["#2A4A56", "#1C3440", "#345864"], 101, fleck="#E8DCC0", angle=-15)]
    o.append(f'<defs>{lgrad(sk, [(0, "#16243C", 0.95), (0.45, "#2A4A64", 0.6), (0.68, "#6A6A86", 0.45), (0.8, "#E89A6A", 0.55), (1, "#E89A6A", 0.4)])}</defs><rect width="600" height="600" fill="url(#{sk})"/>')
    rnd = random.Random(102)
    for _ in range(60):
        x, y = rnd.uniform(10, 590), rnd.uniform(10, 330)
        o.append(f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{rnd.uniform(0.8, 2.2):.1f}" fill="#FFF6D8" opacity="{rnd.uniform(0.35, 0.9):.2f}"/>')
    for x, y, sz in ((110, 112, 9), (466, 218, 6), (540, 300, 6), (70, 270, 5)):
        o.append(sparkle(x, y, sz, "#FFF0C0", 0.9))
    # moon and moonlit clouds
    o.append(glow(u, 476, 120, 150, "#FFF0C0", 0.35))
    moon = blob(476, 120, 46, 46, 103, 0.015, 20)
    o.append(form(u, moon, (430, 74, 522, 166), "#FBEFC8", "#D8C890", "#FFFDF0", 103, -60, n=50, shade=(8, 8), shade_op=0.35, ink_w=1.4, ink_col="#C8B070",
                  extra_in="".join(f'<path d="{blob(476 + dx, 120 + dy, r, r * 0.8, 104 + i, 0.15, 10)}" fill="#D8C890" opacity="0.45"/>' for i, (dx, dy, r) in enumerate(((-14, -10, 9), (12, 14, 7), (18, -16, 5), (-8, 22, 5))))))
    o.append(cloud2(u, 420, 206, 210, 48, 105, base="#6E7AA0", shade_c="#3E4A70", light="#C8D0E6"))
    o.append(cloud2(u, 118, 170, 180, 42, 106, base="#5E6A92", shade_c="#38446A", light="#AEB8D6"))
    o.append(cloud2(u, 250, 318, 150, 30, 118, base="#4A5A80", shade_c="#2E3A5E", light="#8A98BC"))
    # layered hills and a little village with its lights on
    o.append(hill(u, [(-20, 400), (90, 368), (220, 392), (360, 360), (480, 382), (620, 356)], 640, "#2E4A5C", "#1E3444", "#46647A", 107))
    for i, (x, b, w, h) in enumerate(((110, 404, 34, 24), (156, 410, 28, 20), (430, 392, 32, 24), (472, 396, 26, 18))):
        o.append(cottage(u, x, b, w, h, 108 + i, wall=("#8A8AA0", "#5E5E78", "#B0B0C4"), roof=("#4A3A4E", "#2A1E30", "#6A5A6E")))
    for i, x in enumerate((60, 200, 260, 390, 520, 560)):
        o.append(round_tree(u, x, 412 if i % 2 else 400, 20 + (i % 3) * 4, 112 + i))
    o.append(hill(u, [(-20, 436), (140, 414), (300, 430), (460, 410), (620, 426)], 640, "#1E3440", "#122430", "#2E4A58", 113, n=140, length=(30, 80)))
    o.append(grass(114, (-20, 420, 620, 470), ["#2E4A58", "#16282E"], 120, (6, 16), 1.6))
    # the hero: cape streaming, fist forward
    cape_d = ("M -66 -34 Q 10 -46 70 -6 Q 120 30 160 12 Q 200 -6 236 14 Q 214 40 232 70 Q 250 96 226 118 "
              "Q 190 104 160 124 Q 120 146 80 112 Q 20 70 -60 34 Z")
    cape = ('<path d="' + cape_d + '" fill="#C8343A"/>'
            '<path d="M 60 30 Q 120 70 170 60 Q 200 54 226 90 M 20 50 Q 90 100 140 110" stroke="#8A1820" stroke-width="7" fill="none" opacity="0.55" stroke-linecap="round"/>'
            '<path d="M -50 -28 Q 30 -36 90 4 Q 130 30 170 20" stroke="#F27A6A" stroke-width="8" fill="none" opacity="0.6" stroke-linecap="round"/>'
            + brush((-60, -40, 240, 140), ["#E8565A", "#9A2028", "#F27A6A"], 108, 60, 20, (16, 50), (1.5, 4), (0.15, 0.4), 0.2) +
            '<path d="' + cape_d + '" fill="none" stroke="#5A0E14" stroke-width="3.4" stroke-linejoin="round"/>')
    o.append(trail([(60, 360), (120, 330), (180, 300), (230, 268)], "#FFF0C0", 2.4, "2 9", 0.7))
    o.append(bee(u, 336, 180, 80, 115, rot=-24, flip=True, mood="grin", wings="spread", under=cape, pose="tuck",
                 arms=["M -64 36 Q -110 40 -152 4"]))
    t, _, _ = btext(u, 300, 424, "bee", SERIF_IT, 92, "#F6CE5A", ["#FFE08A", "#D49A22"], 116, angle=-40, shadow="#0A161C", soff=(0.02, 0.04))
    o.append(t)
    t, _, _ = btext(u, 300, 546, "BRAVE", ANTON, 132, "#FBEBD2", ["#FFF6E6", "#E8D2B4", "#F6E0C0"], 117, ls=12, angle=-78, shadow="#0A161C",
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
    o.append(f'<defs>{lgrad(sk, [(0, "#9CC0D4", 0.55), (0.55, "#FBEAC8", 0.3), (1, "#F8C890", 0.7)])}</defs><rect width="600" height="420" fill="url(#{sk})"/>')
    o.append(glow(u, 440, 384, 220, "#FFE6A0", 0.75, 120))
    o.append(f'<path d="{blob(440, 384, 34, 34, 120, 0.01, 16)}" fill="#FFE8A8" opacity="0.9"/>')
    o.append(hill(u, [(-20, 380), (100, 366), (240, 376), (380, 362), (520, 374), (620, 364)], 420, "#B8B8C8", "#9A9AB0", "#D2D2DE", 112, n=60))
    # farmhouse and poplars on the horizon
    o.append(hill(u, [(-20, 400), (80, 390), (200, 396), (320, 388), (460, 396), (620, 390)], 420, "#9AA478", "#7A8458", "#BCC69C", 113, n=60))
    o.append(cottage(u, 150, 400, 40, 26, 114, wall=("#F2E2C4", "#C8B08C", "#FFF8EA"), roof=("#C0644A", "#8A3E2A", "#E08A6A"), lit=False))
    for i, (x, h) in enumerate(((104, 70), (194, 84), (214, 64), (500, 76), (524, 60))):
        o.append(poplar(u, x, 402, h, 115 + i))
    o.append(lavender_rows(u, 408, 112))
    o.append(glow(u, 300, 420, 340, "#FFF4DC", 0.45, 40))
    # the bee, zooming left with a basket of blossoms
    for i, (y, L) in enumerate(((284, 120), (312, 150), (340, 100))):
        o.append(brush((420, y - 3, 420 + L, y + 3), ["#E2A23A", "#C47A16"], 113 + i, 6, 0, (L * 0.4, L * 0.8), (2, 4), (0.4, 0.7), 0.05, 2))
    o.append(bee(u, 344, 296, 82, 114, rot=-4, mood="smile", wings="spread", pose="tuck", arms=["M -62 40 Q -96 64 -126 52"]))
    bx, by = bee_pt(344, 296, 82, -4, False, -126, 60)
    o.append(f'<g transform="translate({_f(bx)} {_f(by)})">'
             f'<path d="M -34 6 L 34 6 L 26 52 Q 0 60 -26 52 Z" fill="#C8945A" stroke="#5A3416" stroke-width="2.6" stroke-linejoin="round"/>'
             f'<path d="M -32 20 L 32 20 M -30 34 L 30 34" stroke="#8A5A2E" stroke-width="2.4"/>'
             f'<path d="M -16 6 L -14 56 M 0 6 L 0 58 M 16 6 L 14 56" stroke="#8A5A2E" stroke-width="2" opacity="0.7"/>'
             f'<path d="M -30 8 Q 0 -40 30 8" stroke="#5A3416" stroke-width="3.4" fill="none"/></g>')
    o.append(daisy(u, bx - 14, by + 2, 13, 115, n=11) + cosmos(u, bx + 12, by - 2, 13, 116) + clover(u, bx + 1, by - 8, 8, 117))
    o.append(lavender(u, bx - 26, by + 10, 46, 118, ang=-130, buds=6, bw=4))
    o.append(f'<circle cx="{_f(bx)}" cy="{_f(by - 8)}" r="5" fill="{NOIR}"/>')
    o.append(bee(u, 520, 230, 18, 119, rot=-6, mood="smile", wings="spread"))
    o.append(trail([(540, 234), (572, 250), (600, 240)], INK, 1.8, "2 7", 0.45))
    t, _, _ = btext(u, 300, 150, "BUSY BEE", JOS, 92, "#3A2418", ["#5A3A24", "#2A1810", "#6E4A30"], 120, ls=6, angle=-78, max_w=460,
                    shadow="#F6C870", soff=(0.025, 0.035))
    o.append(t)
    o.append(ruled_c(u, 190, "FROM SUNUP TO SUNDOWN", JOST, 19, "#7A4A16", 119, ls=4, line_w=30))
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
