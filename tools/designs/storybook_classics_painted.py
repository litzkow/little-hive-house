"""Storybook Classics, hand-painted (gouache / storybook) edition: 30 magnets for bookworms.

Each magnet is a painted "vintage book plate / illustrated edition" for a beloved PUBLIC-DOMAIN book (first
published in the US before 1931): an original painted scene or emblem from the story, the title, and where it
fits a short line quoted exactly from the text. Typography borrows from old cloth bindings and libraries: gilt
stamped capitals, ex-libris frames, library cards and due-date stamps, playbills, luggage labels, maps.

Painted in the house gouache idiom (warm paper, layered washes with pooled edges, brush strokes following the
form, a warm brown pen line, soft light, grain on top). Colour story: book-cloth colours (bottle green, oxblood,
navy, mustard, plum) with gilt, on warm cream paper.

Run from tools/designs:  python3 storybook_classics_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (apple, blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ridge, ruled, shift, sky, soft_glow, specks, taper, catmull, steam_wisps, mist)
from fall_painted import Doc
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines, sea
import holidays_gouache as hg

COL = "storybook-classics"
INK = "#3A2418"
FLECK = "#8A6A4A"

lt, dk = hg.lt, hg.dk

# (light, base, dark) gouache palettes
GOLD = ("#FBE7A4", "#D9A945", "#8A6020")
BRASS = ("#F6DC8A", "#C89A3A", "#7A5418")
GREEN = ("#7FAE86", "#2E6A48", "#163A26")
OXBLOOD = ("#D0706A", "#8E2A2A", "#4E1014")
NAVY = ("#6A82B8", "#24386A", "#0E1A3A")
MUSTARD = ("#F2CF6E", "#D2A033", "#8A6418")
PLUM = ("#A8789A", "#5E3050", "#2E1426")
WOOD = ("#C8925E", "#8E5A30", "#4E2E14")
DARKWOOD = ("#8A5A3A", "#4E2E1A", "#24140A")
CREAM = ("#FFFDF4", "#F2E8D2", "#C4B190")
MARBLE = ("#FFFFFF", "#ECE6DA", "#A89E90")
SILVER = ("#FFFFFF", "#C8CED8", "#6A7484")
LEAF = ("#9CCB7A", "#4E8A3E", "#22502A")
ROSE = ("#F69A9A", "#D2384A", "#7E1426")
SKY = ("#BEE0F2", "#7AB0D8", "#3E6A9A")

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


class Doc2(Doc):
    """fall_painted.Doc plus the Pn interface (id / lg / rg / glow) so holidays_gouache helpers work with it."""

    def id(self, p="g"):
        return self.nid()

    def lg(self, stops, x1=0, y1=0, x2=0, y2=1, units="objectBoundingBox"):
        return self.lin(stops, x1, y1, x2, y2, units)[5:-1]

    def rg(self, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None):
        return self.rad(stops, cx, cy, r, fx, fy)[5:-1]

    def glow(self, x, y, r, col, s=0.7, ry=None):
        g = self.rad([(0, col, s), (0.35, col, s * 0.5), (1, col, 0)])
        if ry:
            return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{ry:.1f}" fill="{g}"/>'
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{g}"/>'


# ================================================================ toolkit
def ell_pts(cx, cy, rx, ry, a0=0, a1=360, n=24):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def pd(pts, close=True):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if close else "")


def T(pts, ox, oy, s=1.0, flip=False, ang=0):
    """Place local points: scale, mirror, rotate (deg) and translate."""
    out = []
    a = math.radians(ang)
    c, si = math.cos(a), math.sin(a)
    for x, y in pts:
        x = -x if flip else x
        x, y = x * s, y * s
        out.append((ox + x * c - y * si, oy + x * si + y * c))
    return out


def shade_over(D, d, col="#1A0A04", op=0.4, x1=0, y1=0, x2=1, y2=1, start=0.35):
    g = D.lin([(0, col, 0), (start, col, 0), (1, col, op)], x1, y1, x2, y2)
    return f'<path d="{d}" fill="{g}"/>'


def light_over(D, d, col="#FFFFFF", op=0.45, x1=0, y1=0, x2=1, y2=1, end=0.55):
    g = D.lin([(0, col, op), (end, col, 0)], x1, y1, x2, y2)
    return f'<path d="{d}" fill="{g}"/>'


def finish_b(D, out, seed, color=INK, op=1.0):
    return finish(D, out, seed, color, op)


def tx(x, y, s, font, size, fill, ls=0, max_w=460, anchor="middle", extra="", op=None):
    """Fitted text line; centred text with letter-spacing is nudged so it stays optically centred."""
    fs = fit_size(s, font, size, max_w, ls)
    xx = x + ls / 2 if (ls and anchor == "middle") else x
    lsa = f' letter-spacing="{ls}"' if ls else ""
    o = f' opacity="{op}"' if op is not None else ""
    return f'<text x="{xx:.1f}" y="{y:.1f}" text-anchor="{anchor}" {font} font-size="{fs}"{lsa} fill="{fill}"{o}{extra}>{esc(s)}</text>'


def gilt_fill(D, y0, y1, pal="gold"):
    if pal == "silver":
        stops = [(0, "#FFFFFF"), (0.42, "#D6DCE6"), (0.55, "#8A94A6"), (0.8, "#E8ECF2"), (1, "#B4BCCA")]
    elif pal == "pale":
        stops = [(0, "#FFF8DA"), (0.45, "#F2D890"), (0.58, "#C89A48"), (1, "#F8E6A8")]
    else:
        stops = [(0, "#FFF0B0"), (0.4, "#E8BE5A"), (0.56, "#A87A28"), (0.8, "#E0B050"), (1, "#F6DC90")]
    return D.lin(stops, 0, y0, 0, y1, "userSpaceOnUse")


def gilt(D, x, y, s, font, size, ls=0, max_w=460, anchor="middle", deboss="#1A0C04", dop=0.6, pal="gold", wear=True, seed=1):
    """Gilt-stamped lettering: debossed shadow, metallic gradient, a bright top edge and a little rubbed wear."""
    fs = fit_size(s, font, size, max_w, ls)
    xx = x + ls / 2 if (ls and anchor == "middle") else x
    lsa = f' letter-spacing="{ls}"' if ls else ""
    g = gilt_fill(D, y - fs * 0.78, y + fs * 0.05, pal)

    def t(dx, dy, fill, op=1):
        return f'<text x="{xx + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}" {font} font-size="{fs}"{lsa} fill="{fill}" opacity="{op}">{esc(s)}</text>'
    out = [t(fs * 0.025, fs * 0.04, deboss, dop), t(-fs * 0.012, -fs * 0.018, "#FFF8E0", 0.55), t(0, 0, g)]
    if wear:
        W = measure(s, font, fs, ls)
        x0 = xx - W / 2 if anchor == "middle" else (xx - W if anchor == "end" else xx)
        uid = D.nid()
        rnd = random.Random(seed)
        sp = "".join(f'<circle cx="{rnd.uniform(x0, x0 + W):.1f}" cy="{rnd.uniform(y - fs * 0.8, y):.1f}" r="{rnd.uniform(0.5, 1.4):.1f}" fill="{rnd.choice([deboss, "#FFFFFF"])}" opacity="{rnd.uniform(0.25, 0.6):.2f}"/>'
                     for _ in range(int(W / 4)))
        out.append(f'<clipPath id="{uid}"><text x="{xx:.1f}" y="{y:.1f}" text-anchor="{anchor}" {font} font-size="{fs}"{lsa}>{esc(s)}</text></clipPath><g clip-path="url(#{uid})">{sp}</g>')
    return "".join(out)


def cloth_bg(D, base, seed, x0=0, y0=0, x1=600, y1=600, weave=4, vign=0.45):
    """Book cloth: base colour, fine woven texture, uneven dye mottling, darker rubbed edges."""
    rnd = random.Random(seed)
    w = weave
    pat = D.pattern(w * 2, w * 2, f'<rect width="{w * 2}" height="{w * 2}" fill="{base}"/>'
                    f'<rect width="{w * 2}" height="{w * 0.55:.1f}" fill="{lt(base, 0.14)}" opacity="0.5"/>'
                    f'<rect y="{w}" width="{w * 2}" height="{w * 0.55:.1f}" fill="{dk(base, 0.14)}" opacity="0.4"/>'
                    f'<rect width="{w * 0.5:.1f}" height="{w * 2}" fill="{dk(base, 0.18)}" opacity="0.35"/>'
                    f'<rect x="{w}" width="{w * 0.5:.1f}" height="{w * 2}" fill="{lt(base, 0.1)}" opacity="0.35"/>')
    d = f"M {x0} {y0} L {x1} {y0} L {x1} {y1} L {x0} {y1} Z"
    out = [f'<path d="{d}" fill="{pat}"/>']
    for i in range(10):
        c = rnd.choice([lt(base, 0.18), dk(base, 0.2)])
        out.append(f'<path d="{blob(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(60, 160), rnd.uniform(40, 120), seed + i, 0.2, 14)}" fill="{c}" opacity="{rnd.uniform(0.08, 0.18):.2f}"/>')
    g = D.rad([(0, "#000000", 0), (0.65, "#000000", 0), (1, "#000000", vign)], cx=0.5, cy=0.5, r=0.75)
    out.append(f'<path d="{d}" fill="{g}"/>')
    return "".join(out)


def rule_frame(D, x0, y0, x1, y1, col, w=2.4, gap=7, inner_w=1.2, corner=None, seed=1):
    """Double ruled frame (hand-ruled) with optional corner ornaments."""
    out = [f'<path d="{hg.org_rect(x0, y0, x1 - x0, y1 - y0, seed, 0.5, 30, 1)}" fill="none" stroke="{col}" stroke-width="{w}"/>']
    if gap:
        out.append(f'<path d="{hg.org_rect(x0 + gap, y0 + gap, x1 - x0 - 2 * gap, y1 - y0 - 2 * gap, seed + 1, 0.5, 30, 1)}" fill="none" stroke="{col}" stroke-width="{inner_w}"/>')
    if corner:
        for (cx, cy, r) in ((x0, y0, 45), (x1, y0, 135), (x1, y1, 225), (x0, y1, 315)):
            out.append(corner(cx, cy, r))
    return "".join(out)


def fleuron(cx, cy, s, col, rot_=0, op=1.0):
    """Printer's fleuron (hedera leaf) with a curled stem."""
    leaf = [(0, 0.9), (-0.55, 0.35), (-0.62, -0.15), (-0.35, -0.5), (0, -0.32), (0.35, -0.5), (0.62, -0.15), (0.55, 0.35)]
    pts = [(cx + x * s, cy + y * s) for x, y in leaf]
    pts = rot(pts, cx, cy, rot_)
    stem = rot([(cx, cy - 0.32 * s), (cx + 0.1 * s, cy - 0.7 * s), (cx + 0.38 * s, cy - 0.92 * s), (cx + 0.55 * s, cy - 0.78 * s)], cx, cy, rot_)
    return (f'<g opacity="{op}"><path d="{smooth_closed(pts)}" fill="{col}"/>'
            f'{taper(stem, s * 0.16, s * 0.05, col)}</g>')


def flourish(cx, cy, w, col, sw=2.0, dots=True, seed=1):
    """Symmetric scroll divider: a lozenge in the middle, S-scrolls each side ending in curls."""
    out = [f'<path d="M {cx - 7:.1f} {cy:.1f} L {cx:.1f} {cy - 5:.1f} L {cx + 7:.1f} {cy:.1f} L {cx:.1f} {cy + 5:.1f} Z" fill="{col}"/>']
    for sg in (-1, 1):
        a = cx + sg * 12
        b = cx + sg * w / 2
        m = (a + b) / 2
        pts = [(a, cy), (a + sg * (b - a) * 0.12 * sg, cy), (m - sg * 6, cy - 6), (m, cy - 1), (m + sg * 8, cy + 5), ((m + b) / 2, cy + 2), (b - sg * 10, cy - 3)]
        pts = [(a, cy), ((a + m) / 2, cy + 4), (m, cy - 1), ((m + b) / 2, cy - 5), (b - sg * 8, cy - 1)]
        out.append(taper(catmull(pts, 6), sw * 1.4, sw * 0.6, col))
        # end curl
        ex = b - sg * 8
        curl = [(ex, cy - 1), (ex + sg * 6, cy + 2), (ex + sg * 4, cy + 7), (ex - sg * 1, cy + 5)]
        out.append(taper(catmull(curl, 5), sw * 0.9, sw * 0.5, col))
        if dots:
            out.append(f'<circle cx="{m - sg * 4:.1f}" cy="{cy + 7:.1f}" r="{sw * 0.9:.1f}" fill="{col}"/>')
    return "".join(out)


def laurel(D, pts, s, pal, seed, side=1, n=None, inkw=0.9, berries=None):
    """A sprig of small paired leaves along a curve (pts), tip at the last point."""
    path = catmull(pts, 8)
    rnd = random.Random(seed)
    out = [taper(path, s * 0.22, s * 0.06, pal[2])]
    n = n or int(len(path) / 3)
    for i in range(1, n):
        t = i / n
        k = int(t * (len(path) - 2))
        (x0, y0), (x1, y1) = path[k], path[k + 1]
        a = math.degrees(math.atan2(y1 - y0, x1 - x0))
        L = s * (1.0 - 0.45 * t)
        for sg in (-1, 1):
            ang = a + sg * 38
            cx, cy = x0 + math.cos(math.radians(ang)) * L * 0.5, y0 + math.sin(math.radians(ang)) * L * 0.5
            lp = blob_pts(cx, cy, L * 0.5, L * 0.2, seed + i * 3 + sg, 0.05, 10, ang)
            c = pal[0] if (sg * side) < 0 else pal[1]
            out.append(f'<path d="{smooth_closed(lp)}" fill="{c}"/>')
            out.append(f'<path d="M {x0:.1f} {y0:.1f} L {x0 + math.cos(math.radians(ang)) * L * 0.85:.1f} {y0 + math.sin(math.radians(ang)) * L * 0.85:.1f}" stroke="{pal[2]}" stroke-width="0.8" opacity="0.6"/>')
            if inkw:
                out.append(ink(smooth_closed(lp), pal[2], inkw, seed + i, 1, 0.55))
        if berries and i % 3 == 1:
            out.append(f'<circle cx="{x0:.1f}" cy="{y0 + 3:.1f}" r="{s * 0.13:.1f}" fill="{berries}"/>')
    tx_, ty_ = path[-1]
    out.append(f'<path d="{blob(tx_, ty_, s * 0.42, s * 0.16, seed + 99, 0.05, 10, math.degrees(math.atan2(path[-1][1] - path[-2][1], path[-1][0] - path[-2][0])))}" fill="{pal[1]}"/>')
    return "".join(out)


def candle(D, cx, base, h, seed, w=16, wax=CREAM, flame=True, holder=BRASS, glow_r=120, drip=True):
    """Lit candle in a brass chamberstick; base = bottom of the holder dish."""
    out = []
    if flame:
        out.append(soft_glow(D, cx, base - h - 22, glow_r, "#FFC860", 0.55))
        out.append(soft_glow(D, cx, base - h - 18, glow_r * 0.35, "#FFE8A0", 0.7))
    # dish
    dish = ell_pts(cx, base - 4, w * 2.2, w * 0.5, 0, 360, 24)
    out.append(painted(D, dish, holder, seed, sdir=(0.5, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.5))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - 7, w * 1.7, w * 0.32, 0, 360, 20))}" fill="{holder[2]}" opacity="0.45"/>')
    # handle ring
    out.append(ink(f"M {cx + w * 2.0:.1f} {base - 6:.1f} q {w * 0.9:.1f} {-w * 0.1:.1f} {w * 0.7:.1f} {-w * 0.8:.1f} q {-w * 0.2:.1f} {-w * 0.5:.1f} {-w * 0.8:.1f} {-w * 0.2:.1f}", holder[2], 3, seed, 1, 0.9))
    # wax
    top = base - 8 - h
    body = [(cx - w / 2, base - 8), (cx - w / 2, top + 3), (cx - w * 0.2, top), (cx + w * 0.25, top + 2), (cx + w / 2, top + 4), (cx + w / 2, base - 8)]
    out.append(painted(D, body, wax, seed + 1, sdir=(1, 0.2), sk=0.25, angle=-90, n=10, inkw=1.4, hi=0.6, hik=0.12))
    if drip:
        out.append(taper([(cx - w * 0.35, top + 2), (cx - w * 0.42, top + h * 0.25), (cx - w * 0.38, top + h * 0.36)], w * 0.3, w * 0.22, lt(wax[1], 0.4)))
        out.append(f'<circle cx="{cx - w * 0.38:.1f}" cy="{top + h * 0.37:.1f}" r="{w * 0.13:.1f}" fill="{lt(wax[1], 0.4)}"/>')
    out.append(f'<path d="M {cx:.1f} {top + 1:.1f} l 0.6 -7" stroke="#2A1A10" stroke-width="1.6" stroke-linecap="round"/>')
    if flame:
        fy = top - 6
        out.append(f'<path d="M {cx:.1f} {fy - 26:.1f} C {cx + 7:.1f} {fy - 12:.1f} {cx + 8:.1f} {fy:.1f} {cx:.1f} {fy + 2:.1f} C {cx - 8:.1f} {fy:.1f} {cx - 6:.1f} {fy - 12:.1f} {cx:.1f} {fy - 26:.1f} Z" fill="#FFB43A"/>')
        out.append(f'<path d="M {cx:.1f} {fy - 18:.1f} C {cx + 4:.1f} {fy - 9:.1f} {cx + 4:.1f} {fy - 1:.1f} {cx:.1f} {fy:.1f} C {cx - 4:.1f} {fy - 1:.1f} {cx - 4:.1f} {fy - 9:.1f} {cx:.1f} {fy - 18:.1f} Z" fill="#FFF4C0"/>')
        out.append(f'<ellipse cx="{cx:.1f}" cy="{fy - 1:.1f}" rx="2.4" ry="3.4" fill="#6A8AE0" opacity="0.6"/>')
    return "".join(out)


def quill(D, x0, y0, x1, y1, seed, vane=CREAM, w=22):
    """A goose-feather quill from nib (x0, y0) to tip (x1, y1)."""
    a = math.atan2(y1 - y0, x1 - x0)
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    out = []
    left, right = [], []
    for i in range(15):
        t = 0.28 + 0.72 * i / 14
        ww = w * max(0.0, math.sin(math.pi * (t - 0.28) / 0.72)) ** 0.7 * (1 - 0.25 * t)
        px, py = x0 + ux * L * t, y0 + uy * L * t
        left.append((px + nx * ww * 0.55, py + ny * ww * 0.55))
        right.append((px - nx * ww * 0.85, py - ny * ww * 0.85))
    pts = left + right[::-1]
    out.append(painted(D, pts, vane, seed, sdir=(nx, ny), sk=0.12, angle=math.degrees(a) + 60, n=40, slen=(w * 0.3, w * 0.9), sw=(0.5, 1.2), inkw=1.2, hi=0.3))
    rnd = random.Random(seed)
    for i in range(16):
        t = 0.32 + 0.64 * i / 15
        px, py = x0 + ux * L * t, y0 + uy * L * t
        for sg, k in ((1, 0.5), (-1, 0.8)):
            ww = w * max(0.0, math.sin(math.pi * (t - 0.28) / 0.72)) ** 0.7 * k
            out.append(f'<path d="M {px:.1f} {py:.1f} q {ux * 4 + sg * nx * ww * 0.5:.1f} {uy * 4 + sg * ny * ww * 0.5:.1f} {ux * 9 + sg * nx * ww:.1f} {uy * 9 + sg * ny * ww:.1f}" stroke="{vane[2]}" stroke-width="0.8" fill="none" opacity="0.5"/>')
    out.append(taper([(x0, y0), (x0 + ux * L * 0.5, y0 + uy * L * 0.5), (x1, y1)], 3.2, 1.2, "#F8F0DC"))
    out.append(pline([(x0, y0), (x0 + ux * L * 0.3, y0 + uy * L * 0.3)], "#8A7A60", 1.2, seed, 0.8, 1))
    out.append(taper([(x0 - ux * 2, y0 - uy * 2), (x0 + ux * 14, y0 + uy * 14)], 1, 3, "#2A1A10"))
    return "".join(out)


def inkwell(D, cx, base, w, seed, glass=("#7A8AA8", "#2A3450", "#0E1424"), cap=BRASS):
    """Squat glass inkwell with a brass collar."""
    h = w * 0.62
    body = [(cx - w / 2, base - 4), (cx - w / 2 - 2, base - h * 0.6), (cx - w * 0.36, base - h), (cx + w * 0.36, base - h), (cx + w / 2 + 2, base - h * 0.6), (cx + w / 2, base - 4), (cx, base + 1)]
    out = [cast(D, cx + 8, base, w * 0.7, 8, strength=0.45, seed=seed)]
    out.append(painted(D, body, glass, seed, sdir=(1, 0.4), sk=0.2, angle=-90, n=12, inkw=1.6, hi=0.35))
    out.append(taper([(cx - w * 0.34, base - h * 0.85), (cx - w * 0.4, base - h * 0.35)], 5, 2, "#FFFFFF", 0.55))
    col = rect_pts(cx - w * 0.22, base - h - 12, cx + w * 0.22, base - h + 2, 8, seed, 0.3)
    out.append(painted(D, col, cap, seed + 1, sdir=(1, 0.2), sk=0.2, angle=0, n=6, inkw=1.4, hi=0.5))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - h - 12, w * 0.22, w * 0.06, 0, 360, 16))}" fill="#120A06"/>')
    return "".join(out)


def book3(D, x, y, w, h, thick, seed, cover=OXBLOOD, pages="#F4E8CC", spine_side=-1, title_band=True):
    """A closed book lying flat, seen from slightly above: cover top + page block front edge."""
    out = [cast(D, x + w / 2 + 6, y + h + thick, w * 0.62, 10, strength=0.4, seed=seed)]
    # page block (front edge)
    pb = [(x + 4, y + h - 2), (x + w - 2, y + h - 2), (x + w - 2, y + h + thick - 2), (x + 4, y + h + thick - 2)]
    out.append(f'<path d="{hg.org_poly(pb, seed, 0.4, 10, 1)}" fill="{pages}"/>')
    for k in range(1, int(thick / 2.6)):
        out.append(f'<path d="M {x + 6:.1f} {y + h - 2 + k * 2.6:.1f} L {x + w - 4:.1f} {y + h - 2 + k * 2.6:.1f}" stroke="#C8B48A" stroke-width="0.7" opacity="0.8"/>')
    cov = rect_pts(x, y, x + w, y + h + 2, 14, seed, 0.5)
    out.append(painted(D, cov, cover, seed + 1, sdir=(0.6, 0.8), sk=0.1, angle=-8, n=24, inkw=1.6, hi=0.3))
    # bottom board edge
    out.append(f'<path d="M {x:.1f} {y + h + 2:.1f} L {x + w:.1f} {y + h + 2:.1f} L {x + w:.1f} {y + h + thick:.1f} L {x:.1f} {y + h + thick:.1f} Z" fill="{cover[2]}" opacity="0.0"/>')
    sx = x + 8 if spine_side < 0 else x + w - 8
    out.append(f'<path d="M {sx:.1f} {y + 2:.1f} L {sx:.1f} {y + h:.1f}" stroke="{cover[2]}" stroke-width="2" opacity="0.6"/>')
    if title_band:
        out.append(f'<rect x="{x + w * 0.3:.1f}" y="{y + h * 0.3:.1f}" width="{w * 0.4:.1f}" height="{h * 0.16:.1f}" fill="none" stroke="{GOLD[1]}" stroke-width="1.6"/>')
    return "".join(out)


def bird_v(x, y, s, col=INK, op=0.85):
    return pline([(x - s, y - s * 0.2), (x - s * 0.45, y - s * 0.5), (x, y)], col, max(1.5, s * 0.16), int(x * 7), op, 1) + \
        pline([(x, y), (x + s * 0.45, y - s * 0.5), (x + s, y - s * 0.25)], col, max(1.5, s * 0.16), int(y * 7), op, 1)


def star4(cx, cy, r, col, op=1.0):
    return sparkle(cx, cy, r, col, op)


def stars_field(seed, box, n, cols=("#FFFFFF", "#FFF2C8", "#DCE6FF"), r=(0.6, 1.8), op=(0.5, 1.0)):
    return specks(seed, box, list(cols), n, r, op)


def pocket_watch(D, cx, cy, r, seed, case=GOLD, face="#FFF8E8", hands=(10, 10), chain=None, numerals=True):
    """Gold pocket watch: crown and bow, bevelled case, enamel dial with numerals and hands."""
    out = [cast(D, cx + r * 0.15, cy + r * 0.2, r * 1.1, r * 1.05, strength=0.3, seed=seed)]
    # bow and crown
    out.append(ink(smooth_open(ell_pts(cx, cy - r * 1.18, r * 0.32, r * 0.26, 180, 360, 14)), case[2], max(2.5, r * 0.12), seed, 1, 1))
    out.append(ink(smooth_open(ell_pts(cx, cy - r * 1.18, r * 0.32, r * 0.26, 180, 360, 14)), case[0], max(1, r * 0.05), seed + 1, 1, 0.9))
    out.append(painted(D, rect_pts(cx - r * 0.13, cy - r * 1.2, cx + r * 0.13, cy - r * 0.92, 4, seed, 0.2), case, seed + 2, sk=0.2, angle=-90, n=4, inkw=1, hi=0.5))
    out.append(painted(D, blob_pts(cx, cy, r, r, seed, 0.01, 28), case, seed + 3, sdir=(0.6, 0.8), sk=0.14, angle=-30, n=int(r * 0.8) + 6, inkw=1.6, hi=0.55, hik=0.1))
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.82:.1f}" fill="none" stroke="{case[2]}" stroke-width="{max(1, r * 0.04):.1f}" opacity="0.7"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.78:.1f}" fill="{face}"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx + r * 0.08, cy + r * 0.1, r * 0.78, r * 0.78, 0, 360, 28))}" fill="#C8B48A" opacity="0.18"/>')
    for i in range(60):
        a = math.radians(i * 6)
        r0 = r * (0.62 if i % 5 == 0 else 0.69)
        out.append(f'<path d="M {cx + math.cos(a) * r0:.1f} {cy + math.sin(a) * r0:.1f} L {cx + math.cos(a) * r * 0.73:.1f} {cy + math.sin(a) * r * 0.73:.1f}" stroke="#2A1A10" stroke-width="{1.4 if i % 5 == 0 else 0.6}" opacity="0.85"/>')
    if numerals and r > 30:
        romans = ["XII", "I", "II", "III", "IIII", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
        for i, s in enumerate(romans):
            a = math.radians(-90 + i * 30)
            fx, fy = cx + math.cos(a) * r * 0.5, cy + math.sin(a) * r * 0.5 + r * 0.05
            out.append(f'<text x="{fx:.1f}" y="{fy:.1f}" text-anchor="middle" {CINZEL} font-size="{r * 0.13:.1f}" fill="#2A1A10" transform="rotate({i * 30} {fx:.1f} {fy - r * 0.045:.1f})">{s}</text>')
    hh, mm = hands
    for ang, L, wdt in ((-90 + hh * 30 + mm * 0.5, 0.38, 3.0), (-90 + mm * 6, 0.6, 2.0)):
        a = math.radians(ang)
        out.append(taper([(cx, cy), (cx + math.cos(a) * r * L * 0.6, cy + math.sin(a) * r * L * 0.6), (cx + math.cos(a) * r * L, cy + math.sin(a) * r * L)], max(2, r * 0.06 * wdt / 2), 0.8, "#1A1210"))
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{max(2, r * 0.05):.1f}" fill="{case[1]}"/>')
    # glass glint
    out.append(taper([(cx - r * 0.5, cy - r * 0.35), (cx - r * 0.3, cy - r * 0.58), (cx - r * 0.05, cy - r * 0.68)], max(2, r * 0.08), 1, "#FFFFFF", 0.7))
    return "".join(out)


def scroll_banner(D, cx, cy, w, h, pal, seed, tail=34, bend=8, drop=None):
    """Ribbon banner with folded swallow-tail ends (painted)."""
    from fall_gouache_a import ribbon
    return ribbon(D, cx, cy, w, h, pal, seed, tail, drop, bend)


def rose_bloom(D, cx, cy, r, seed, pal=ROSE, rot_=0):
    """Painted cabbage rose seen from above / three-quarter: outer petals, cupped spiral centre."""
    rnd = random.Random(seed)
    out = [painted(D, blob_pts(cx, cy, r, r * 0.92, seed, 0.12, 14, rot_), pal, seed, sdir=(0.5, 0.8), sk=0.18, angle=-60, n=8, inkw=1.1, hi=0.4)]
    for k in range(5):
        a = math.radians(rot_ + k * 72 + rnd.uniform(-10, 10))
        px, py = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.5
        out.append(f'<path d="{blob(px, py, r * 0.42, r * 0.28, seed + k, 0.12, 10, math.degrees(a) + 90)}" fill="{pal[0]}" opacity="0.55"/>')
        out.append(pline([(cx + math.cos(a) * r * 0.25, cy + math.sin(a) * r * 0.22), (px + math.cos(a + 1) * r * 0.3, py + math.sin(a + 1) * r * 0.3)], pal[2], 1.1, seed + k, 0.55, 1))
    sp = [(cx + math.cos(t) * r * 0.08 * t, cy + math.sin(t) * r * 0.07 * t) for t in [i * 0.5 for i in range(1, 11)]]
    out.append(pline(sp, pal[2], 1.4, seed, 0.75, 1))
    out.append(f'<path d="{blob(cx - r * 0.1, cy - r * 0.1, r * 0.25, r * 0.18, seed + 9, 0.1, 8)}" fill="{pal[2]}" opacity="0.35"/>')
    return "".join(out)


def leaf_simple(D, x, y, L, W, ang, pal, seed, vein=True, inkw=1.2, inkc=INK):
    """Pointed leaf from base point (x, y) toward `ang` degrees."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    right, left = [], []
    for i in range(13):
        t = i / 12
        w = W * math.sin(math.pi * t) ** 0.85 * (1 - 0.3 * t)
        bend = 0.08 * L * t * t
        px, py = x + ux * L * t + nx * bend, y + uy * L * t + ny * bend
        right.append((px + nx * w, py + ny * w))
        left.append((px - nx * w, py - ny * w))
    pts = right + left[::-1][1:-1]
    out = [painted(D, pts, pal, seed, sdir=(nx, ny), sk=0.14, angle=ang + 35, n=int(L * W / 60) + 6, slen=(W * 0.4, W * 1.2),
                   sw=(0.8, max(1.2, W * 0.12)), inkw=inkw, inkc=inkc, inkop=0.6, hi=0.3, hik=0.08)]
    if vein:
        sp = [(x + ux * L * t + nx * 0.08 * L * t * t, y + uy * L * t + ny * 0.08 * L * t * t) for t in (0.05, 0.5, 0.92)]
        out.append(pline(sp, lt(pal[0], 0.35), max(1, W * 0.08), seed, 0.7, 1))
    return "".join(out)


def wallpaper_damask(D, base, motif, seed, cell=60, op=0.16):
    """Subtle damask wallpaper (fleur motif tiles)."""
    c = cell
    m = []
    for (ox, oy) in ((c / 2, c / 2), (0, 0), (c, 0), (0, c), (c, c)):
        s = c * 0.22
        m.append(f'<path d="{smooth_closed([(ox, oy - s * 1.4), (ox + s * 0.5, oy - s * 0.4), (ox + s * 1.1, oy - s * 0.2), (ox + s * 0.5, oy + s * 0.3), (ox, oy + s * 1.2), (ox - s * 0.5, oy + s * 0.3), (ox - s * 1.1, oy - s * 0.2), (ox - s * 0.5, oy - s * 0.4)])}" fill="{motif}" opacity="{op}"/>')
        m.append(f'<circle cx="{ox:.1f}" cy="{oy - s * 1.7:.1f}" r="{s * 0.18:.1f}" fill="{motif}" opacity="{op}"/>')
    pat = D.pattern(c, c, f'<rect width="{c}" height="{c}" fill="{base}"/>' + "".join(m))
    return f'<rect width="600" height="600" fill="{pat}"/>'


# ================================================================ 1. the raven — on the bust of Pallas, by candlelight
def raven(D, ox, oy, s, seed, flip=False, rim="#FFB060"):
    """Common raven perched, facing left (flip -> right); (ox, oy) = feet; s=1 ~ 150 px tall."""
    def L(pts):
        return T(pts, ox, oy, s, flip)
    out = []
    pal = ("#5A5E80", "#1C1C28", "#050508")
    # tail (wedge) behind
    tail = L([(30, -30), (62, -8), (104, 30), (112, 44), (92, 46), (70, 24), (34, -6)])
    out.append(painted(D, tail, pal, seed, sdir=(0.3, 1), sk=0.15, angle=35, n=26, cols=["#3A3E58", "#0A0A10", "#4A5070"], inkw=1.6, inkc="#050508", hi=0.3))
    for t in (0.3, 0.55, 0.8):
        out.append(pline(L([(40 + 50 * t, -14 + 40 * t), (70 + 30 * t, 4 + 30 * t)]), "#6A7090", 1.1, seed, 0.45, 1))
    # body
    body = L([(-34, -112), (-14, -120), (10, -106), (30, -82), (52, -52), (70, -24), (64, -8), (40, -4), (14, -2), (-12, -10),
              (-30, -28), (-42, -56), (-46, -84), (-42, -102)])
    out.append(painted(D, body, pal, seed + 1, sdir=(1, 0.5) if not flip else (-1, 0.5), sk=0.16, angle=60, n=90,
                       cols=["#40445E", "#16161E", "#5A6488", "#0A0A10"], sop=(0.25, 0.55), inkw=2, inkc="#050508", hi=0.4, hik=0.06))
    # shaggy throat hackles
    hack = L([(-44, -96), (-56, -88), (-50, -84), (-60, -76), (-50, -74), (-56, -64), (-46, -64), (-48, -54), (-38, -60), (-36, -84)])
    out.append(painted(D, hack, pal, seed + 2, sk=0.1, angle=100, n=14, inkw=1.4, inkc="#050508", hi=0.2))
    # folded wing with primaries
    wing = L([(-20, -88), (6, -84), (34, -60), (62, -26), (96, 12), (104, 22), (84, 18), (54, -2), (20, -20), (-6, -40), (-18, -62)])
    out.append(painted(D, wing, ("#4A4E6A", "#121218", "#020204"), seed + 3, sdir=(1, 0.3), sk=0.15, angle=40, n=40,
                       cols=["#3A4060", "#5A6890", "#0A0A12"], inkw=1.6, inkc="#020204", hi=0.3))
    for k in range(5):
        t = 0.35 + k * 0.13
        a = L([(-6 + 70 * t, -64 + 60 * t)])[0]
        b = L([(18 + 82 * t, -36 + 54 * t)])[0]
        out.append(pline([a, b], "#6E7AA0", 1.3, seed + k, 0.55, 1))
    # scalloped covert feathers
    rnd = random.Random(seed)
    for i in range(10):
        x, y = rnd.uniform(-16, 20), rnd.uniform(-76, -34)
        out.append(pline(L([(x - 6, y - 2), (x, y + 3), (x + 6, y - 2)]), "#646C90", 1.2, seed + i, 0.5, 1))
    # iridescent sheen on the back
    out.append(taper(L([(-30, -112), (-6, -116), (16, -100), (34, -78)]), 5 * s, 2 * s, "#8A96D0", 0.45))
    # head
    head = L([(-50, -118), (-44, -134), (-28, -142), (-10, -138), (0, -124), (-4, -110), (-22, -102), (-42, -104)])
    out.append(painted(D, head, pal, seed + 4, sdir=(1, 0.5), sk=0.15, angle=0, n=18, inkw=1.8, inkc="#050508", hi=0.45))
    # heavy beak
    beak = L([(-46, -132), (-64, -132), (-84, -124), (-92, -116), (-80, -114), (-62, -112), (-46, -110)])
    out.append(painted(D, beak, ("#5A5A68", "#1E1E26", "#060608"), seed + 5, sdir=(0.2, 1), sk=0.15, angle=-5, n=10, inkw=1.6, inkc="#050508", hi=0.5))
    out.append(pline(L([(-48, -121), (-70, -121), (-88, -117)]), "#000000", 1.4, seed, 0.8, 1))
    out.append(taper(L([(-52, -129), (-70, -128), (-84, -122)]), 2.6 * s, 0.8, "#9AA0B8", 0.6))
    # nasal bristles
    out.append(pline(L([(-44, -130), (-54, -127)]), "#2A2A36", 1.6, seed, 0.9, 1))
    # eye with glint
    ex, ey = L([(-34, -124)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{4.4 * s:.1f}" fill="#0A0806"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="{4.4 * s:.1f}" fill="none" stroke="#5A4A3A" stroke-width="1"/>'
               f'<circle cx="{ex - 1.4 * s * (-1 if flip else 1):.1f}" cy="{ey - 1.5 * s:.1f}" r="{1.5 * s:.1f}" fill="#FFF0D0"/>')
    # warm rim light from the candle on the leading edge
    if rim:
        out.append(taper(L([(-56, -86), (-50, -70), (-46, -56), (-40, -40)]), 3.0 * s, 1, rim, 0.45))
        out.append(taper(L([(-82, -121), (-66, -127), (-50, -130)]), 2.0 * s, 1, rim, 0.5))
    # feet gripping
    for dx in (-14, 4):
        fx, fy = L([(dx, -4)])[0]
        out.append(taper([(fx, fy - 8 * s), (fx, fy + 2)], 4 * s, 3 * s, "#1A1A22"))
        for tdx in (-8, -2, 5):
            out.append(taper([(fx, fy + 1), (fx + tdx * s * (-1 if flip else 1), fy + 6 * s)], 2.6 * s, 1.2, "#1A1A22"))
    return "".join(out)


def pallas_bust(D, cx, base, s, seed, light=-1):
    """Marble bust of Pallas Athena in profile (facing left), crested Greek helmet pushed up; base = bottom of socle.
    Returns (svg, perch) where perch is the top of the crest."""
    def L(pts):
        return T(pts, cx, base, s)
    out = []
    pal = MARBLE
    sd = (1, 0.3)
    # socle
    out.append(painted(D, L([(-40, 0), (-32, -8), (-36, -16), (36, -16), (32, -8), (40, 0)]), pal, seed, sdir=sd, sk=0.2, angle=0, n=10, inkw=1.6, hi=0.4))
    out.append(painted(D, L([(-24, -16), (-20, -26), (20, -26), (24, -16)]), pal, seed + 1, sdir=sd, sk=0.2, angle=0, n=6, inkw=1.4, hi=0.4))
    # shoulders with a draped peplos
    sh = L([(-70, -38), (-60, -62), (-38, -76), (-14, -82), (16, -84), (40, -78), (62, -62), (72, -38), (54, -30), (20, -26), (-20, -26), (-54, -30)])
    out.append(painted(D, sh, pal, seed + 2, sdir=sd, sk=0.18, angle=-70, n=30, inkw=1.8, hi=0.45))
    for k in range(4):
        out.append(pline(L([(-44 + k * 16, -72 + k * 2), (-32 + k * 16, -50), (-26 + k * 15, -30)]), "#9A8E80", 1.3, seed + k, 0.5, 1))
    out.append(pline(L([(-56, -60), (-20, -58), (20, -64), (52, -58)]), "#9A8E80", 1.4, seed, 0.55, 1))
    bx, by = L([(-30, -60)])[0]
    out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{6 * s:.1f}" fill="#E2DACC" stroke="#8A8072" stroke-width="1.2"/>')
    # neck
    out.append(painted(D, L([(-14, -80), (-12, -106), (14, -110), (16, -80)]), pal, seed + 3, sdir=sd, sk=0.25, angle=-90, n=8, inkw=1.4, hi=0.4))
    # hair mass behind, gathered at the nape
    hair = L([(-4, -142), (16, -142), (28, -128), (30, -112), (22, -100), (6, -104), (0, -120)])
    out.append(painted(D, hair, ("#FFFFFF", "#E2DCD0", "#9A9084"), seed + 4, sdir=sd, sk=0.2, angle=-70, n=12, inkw=1.4, hi=0.4))
    for k in range(4):
        out.append(pline(L([(4 + k * 6, -138), (8 + k * 6, -124), (6 + k * 6, -108)]), "#9A9084", 1.1, seed + k, 0.6, 1))
    out.append(painted(D, blob_pts(*L([(24, -102)])[0], 9 * s, 8 * s, seed + 5, 0.1, 10), ("#FFFFFF", "#E2DCD0", "#9A9084"), seed + 5, sk=0.2, n=4, inkw=1.2, hi=0.4))
    # profile face: straight Greek brow and nose
    face = L([(-2, -146), (-16, -144), (-22, -136), (-24, -128), (-30, -120), (-26, -117), (-25, -113), (-27, -110), (-24, -107),
              (-22, -102), (-12, -98), (2, -102), (6, -120)])
    out.append(painted(D, face, pal, seed + 6, sdir=sd, sk=0.18, angle=-80, n=14, inkw=1.6, hi=0.55, hik=0.08))
    out.append(pline(L([(-17, -131), (-12, -129.5), (-8, -131)]), "#7A6E62", 1.3, seed, 0.75, 1))
    out.append(pline(L([(-18, -134), (-10, -135)]), "#9A8E80", 1.1, seed, 0.5, 1))
    out.append(pline(L([(-24, -112), (-19, -112)]), "#9A7068", 1.2, seed, 0.6, 1))
    # crested helmet pushed up on the head, visor pointing forward
    helm = L([(-30, -146), (-20, -150), (-14, -160), (2, -166), (18, -162), (28, -150), (30, -138), (20, -140), (4, -146), (-12, -144), (-26, -142)])
    out.append(painted(D, helm, pal, seed + 7, sdir=sd, sk=0.2, angle=-20, n=14, inkw=1.6, hi=0.5))
    out.append(pline(L([(-26, -146), (0, -150), (28, -142)]), "#9A8E80", 1.3, seed, 0.6, 1))
    crest = L([(-12, -162), (-10, -176), (2, -186), (18, -186), (32, -176), (40, -160), (42, -140), (34, -146), (28, -160), (14, -168)])
    out.append(painted(D, crest, pal, seed + 8, sdir=sd, sk=0.2, angle=-50, n=14, inkw=1.6, hi=0.45))
    for k in range(7):
        t = k / 6
        p0 = L([(-8 + 40 * t, -166 + (8 if t > 0.6 else 0) + abs(t - 0.4) * 10)])[0]
        p1 = L([(-6 + 44 * t, -182 + abs(t - 0.35) * 46)])[0]
        out.append(pline([p0, p1], "#9A8E80", 1, seed + k, 0.5, 1))
    return "".join(out), L([(4, -184)])[0]


@design("the-raven")
def the_raven():
    D = Doc2("sbc-rv")
    out = [wallpaper_damask(D, "#2A1A2A", "#6A4A6A", 3, 64, 0.22)]
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#000000", 0), (0.6, "#000000", 0.25), (1, "#000000", 0.7)], cx=0.38, cy=0.5, r=0.75)}"/>')
    out.append(soft_glow(D, 170, 330, 300, "#FFA040", 0.34))
    LY = 404                                    # top of the lintel (where the bust stands)
    dx0, dx1 = 132, 468
    out.append(painted(D, rect_pts(dx0, LY + 30, dx1, 620, 30, 2, 0.4), DARKWOOD, 2, sdir=(1, 0.2), sk=0.06, angle=-90, n=60, inkw=1.6, hi=0.18))
    out.append(painted(D, rect_pts(dx0 + 22, LY + 46, dx1 - 22, 620, 30, 1, 0.4), ("#6A4028", "#3A2214", "#1A0E06"), 3, sdir=(1, 0.2), sk=0.08, angle=-90, n=60, inkw=1.6, hi=0.2))
    for (px0, py0, px1, py1) in ((172, LY + 62, 290, 640), (310, LY + 62, 428, 640)):
        out.append(f'<path d="{hg.org_rect(px0, py0, px1 - px0, py1 - py0, px0, 0.4, 20, 1)}" fill="#2A180C" opacity="0.55"/>')
        out.append(f'<path d="{hg.org_rect(px0 + 8, py0 + 8, px1 - px0 - 16, py1 - py0 - 16, px0 + 1, 0.4, 20, 1)}" fill="#4A2C18" opacity="0.7"/>')
        out.append(pline([(px0 + 2, py0 + 2), (px1 - 2, py0 + 2)], "#C88A50", 1.4, px0, 0.35, 1))
    # lintel: cornice, frieze band carrying the title, dentils
    out.append(painted(D, rect_pts(112, LY + 8, 488, LY + 44, 24, 4, 0.4), ("#7A5034", "#4A2C18", "#22120A"), 4, sdir=(1, 0.6), sk=0.1, angle=0, n=30, inkw=1.6, hi=0.25))
    out.append(painted(D, rect_pts(98, LY - 4, 502, LY + 10, 24, 5, 0.3), ("#8A5E3E", "#5A3620", "#26140A"), 5, sdir=(0.5, 1), sk=0.15, angle=0, n=20, inkw=1.4, hi=0.4))
    out.append(pline([(100, LY - 3), (300, LY - 4), (500, LY - 3)], "#F0B070", 1.6, 6, 0.5, 1))
    for k in range(19):
        x = 116 + k * 19.6
        out.append(f'<rect x="{x:.1f}" y="{LY + 44}" width="10" height="8" fill="#2A160A" opacity="0.7"/>')
    out.append(gilt(D, 300, LY + 35, "THE RAVEN", CINZEL, 25, ls=9, max_w=300, seed=13, dop=0.8))
    for sg in (-1, 1):
        out.append(fleuron(300 + sg * 152, LY + 26, 8, "#C8A050", 90 * sg, 0.9))
    # candle on the lintel: the light source
    out.append(candle(D, 150, LY - 2, 46, 7, w=16, glow_r=180))
    # the bust and the raven
    out.append(cast(D, 312, LY - 2, 74, 6, strength=0.55, seed=8))
    bust, (px, py) = pallas_bust(D, 300, LY - 2, 1.1, 9, light=-1)
    out.append(bust)
    out.append(raven(D, px + 2, py + 3, 0.98, 10))
    # a loose feather spiralling down
    fx, fy = 486, 300
    fpts = rot([(fx - 5, fy), (fx - 8, fy - 22), (fx - 3, fy - 40), (fx + 4, fy - 44), (fx + 7, fy - 24), (fx + 5, fy)], fx, fy, 38)
    out.append(painted(D, fpts, ("#5A5E80", "#16161E", "#050508"), 11, sk=0.12, angle=-50, n=10, inkw=1.2, inkc="#000000", hi=0.4))
    out.append(pline(rot([(fx, fy + 8), (fx, fy - 40)], fx, fy, 38), "#7A80A0", 1.2, 12, 0.8, 1))
    # the quotation over the door
    out.append(tx(300, 486, "Quoth the Raven,", SERIF_IT, 34, "#F4E2C0", max_w=320))
    out.append(gilt(D, 300, 538, "\u201cNevermore.\u201d", SERIF_IT, 64, max_w=380, seed=14, pal="pale"))
    return finish_b(D, out, 15, "#000000", 0.6)


# ================================================================ 2. sherlock holmes — the desk at 221B, seen from above
def tweed(D, d, base, seed, c1="#6A4A2E", c2="#A8442A", cell=14, rot_=20):
    """Tweed check: base wool, dark overcheck, a thin rust windowpane and flecks."""
    c = cell
    pat = D.pattern(c, c, f'<rect width="{c}" height="{c}" fill="{base}"/>'
                    f'<rect width="{c}" height="{c * 0.3:.1f}" fill="{c1}" opacity="0.35"/>'
                    f'<rect width="{c * 0.3:.1f}" height="{c}" fill="{c1}" opacity="0.35"/>'
                    f'<rect y="{c * 0.62:.1f}" width="{c}" height="1.2" fill="{c2}" opacity="0.6"/>'
                    f'<rect x="{c * 0.62:.1f}" width="1.2" height="{c}" fill="{c2}" opacity="0.6"/>'
                    f'<circle cx="{c * 0.2:.1f}" cy="{c * 0.8:.1f}" r="0.8" fill="#F2E2C0" opacity="0.6"/>', transform=f"rotate({rot_})")
    return f'<path d="{d}" fill="{pat}"/>'


def deerstalker(D, cx, cy, r, seed, ang=-20):
    """Deerstalker cap from above: oval six-panel crown, a peak fore and aft, ear flaps tied up over the crown."""
    out = [cast(D, cx + 14, cy + 16, r * 1.7, r * 0.95, strength=0.45, seed=seed)]
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    base = "#B89A6E"

    def E(px, py, rx, ry, a0=0, a1=360, n=28):
        return [(px + ux * rx * math.cos(math.radians(t)) + nx * ry * math.sin(math.radians(t)),
                 py + uy * rx * math.cos(math.radians(t)) + ny * ry * math.sin(math.radians(t))) for t in [a0 + (a1 - a0) * i / n for i in range(n + 1)]]
    # peaks (visors) fore and aft
    for sg in (1, -1):
        pk = E(cx + ux * sg * r * 0.7, cy + uy * sg * r * 0.7, r * 0.62, r * 0.6, -90 if sg > 0 else 90, 90 if sg > 0 else 270, 20)
        dpk = smooth_closed(pk)
        out.append(f'<path d="{dpk}" fill="{dk(base, 0.1)}"/>')
        out.append(tweed(D, dpk, dk(base, 0.1), seed + sg))
        out.append(shade_over(D, dpk, "#2A1608", 0.35, 0.3, 0, 1, 1))
        out.append(ink(dpk, INK, 1.8, seed + sg, 2, 0.75))
        for k in (0.86, 0.72):
            arc = E(cx + ux * sg * r * 0.7, cy + uy * sg * r * 0.7, r * 0.62 * k, r * 0.6 * k, -80 if sg > 0 else 100, 80 if sg > 0 else 260, 16)
            out.append(f'<path d="{smooth_open(arc)}" fill="none" stroke="#4A3018" stroke-width="1.1" stroke-dasharray="3 2.5" opacity="0.75"/>')
    # crown
    crown = E(cx, cy, r * 0.98, r * 0.8, 0, 360, 32)[:-1]
    dc = smooth_closed(crown)
    out.append(f'<path d="{dc}" fill="{base}"/>')
    out.append(tweed(D, dc, base, seed + 3))
    cid = D.clip(f'<path d="{dc}"/>')
    inner = []
    for k in range(6):
        t = math.radians(30 + k * 60)
        ex, ey = cx + ux * r * math.cos(t) + nx * r * 0.82 * math.sin(t), cy + uy * r * math.cos(t) + ny * r * 0.82 * math.sin(t)
        inner.append(pline([(cx, cy), ((cx + ex) / 2 + 2, (cy + ey) / 2 + 2), (ex, ey)], "#4A3018", 2.0, seed + k, 0.55, 1))
    inner.append(f'<path d="{dc}" fill="{D.rad([(0, "#FFF4D8", 0.4), (0.5, "#FFF4D8", 0), (1, "#2A1608", 0.5)], cx=0.38, cy=0.35, r=0.72)}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(dc, INK, 2.2, seed + 4, 2, 0.8))
    # ear flaps folded up over the crown, meeting at the top under a bow
    for sg in (1, -1):
        fp = E(cx + nx * sg * r * 0.36, cy + ny * sg * r * 0.36, r * 0.36, r * 0.3, 0, 360, 22)[:-1]
        dfp = smooth_closed(fp)
        out.append(f'<path d="{smooth_closed(shift(fp, 4, 5))}" fill="#2A1608" opacity="0.3"/>')
        out.append(f'<path d="{dfp}" fill="{lt(base, 0.05)}"/>')
        out.append(tweed(D, dfp, lt(base, 0.05), seed + 6 + sg, rot_=ang + 20))
        out.append(shade_over(D, dfp, "#2A1608", 0.3, 0, 0, 1, 1))
        inn = E(cx + nx * sg * r * 0.36, cy + ny * sg * r * 0.36, r * 0.29, r * 0.23, 0, 360, 22)
        out.append(f'<path d="{smooth_open(inn)}" fill="none" stroke="#4A3018" stroke-width="1" stroke-dasharray="3 2.5" opacity="0.7"/>')
        out.append(ink(dfp, INK, 1.6, seed + 7 + sg, 2, 0.75))
    # ribbon bow tying the flaps
    for sg in (1, -1):
        lp = blob_pts(cx + ux * sg * 13, cy + uy * sg * 13, 13, 6.5, seed + 9 + sg, 0.1, 10, ang + sg * 10)
        out.append(painted(D, lp, ("#A88A5E", "#6A4A2A", "#3A2412"), seed + 9 + sg, sk=0.2, n=4, inkw=1.2, hi=0.3))
    for sg in (1, -1):
        out.append(taper([(cx, cy), (cx + nx * 12 + ux * sg * 6, cy + ny * 12 + uy * sg * 6), (cx + nx * 24 + ux * sg * 12, cy + ny * 24 + uy * sg * 12)], 4.5, 2.5, "#6A4A2A"))
    out.append(f'<path d="{blob(cx, cy, 6, 5, seed, 0.1, 8)}" fill="#5A3A1E" stroke="{INK}" stroke-width="1.2"/>')
    return "".join(out)


def magnifier(D, cx, cy, r, ang, handle_len, seed, lens_art=None):
    """Magnifying glass: brass rim, glass with what it magnifies (lens_art(cx, cy, r)), turned wooden handle."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    hx0, hy0 = cx + ux * r * 1.05, cy + uy * r * 1.05
    hx1, hy1 = cx + ux * (r + handle_len), cy + uy * (r + handle_len)
    out = [cast(D, cx + 16, cy + 18, r * 1.15, r * 1.05, strength=0.35, seed=seed)]
    out.append(taper([(hx0 + 16, hy0 + 18), (hx1 + 16, hy1 + 18)], 18, 20, "#1A0A04", 0.25))
    # handle: brass ferrule then turned wood
    fx, fy = cx + ux * (r + 26), cy + uy * (r + 26)
    out.append(taper([(hx0, hy0), (fx, fy)], 12, 14, BRASS[1]))
    out.append(taper([(hx0 - uy * 3, hy0 + ux * 3), (fx - uy * 3, fy + ux * 3)], 3, 3, BRASS[0], 0.8))
    wood = []
    for i in range(9):
        t = i / 8
        bulge = 1 + 0.25 * math.sin(math.pi * t) + (0.15 if i in (2, 6) else 0)
        wood.append((fx + (hx1 - fx) * t, fy + (hy1 - fy) * t, 9 * bulge))
    left = [(x - uy * w, y + ux * w) for x, y, w in wood]
    right = [(x + uy * w, y - ux * w) for x, y, w in wood]
    out.append(painted(D, left + right[::-1], DARKWOOD, seed + 1, sdir=(-uy, ux), sk=0.25, angle=ang, n=20, inkw=1.6, hi=0.5))
    for i in (2, 6):
        x, y, w = wood[i]
        out.append(pline([(x - uy * w, y + ux * w), (x + uy * w, y - ux * w)], "#1A0E06", 1.4, seed + i, 0.7, 1))
    # lens content
    cid = D.clip(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}"/>')
    if lens_art:
        out.append(f'<g {cid}>{lens_art(cx, cy, r)}</g>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{D.rad([(0, "#FFFFFF", 0.0), (0.75, "#BFE0E8", 0.12), (1, "#5A8A9A", 0.35)])}"/>')
    out.append(taper([(cx - r * 0.62, cy - r * 0.2), (cx - r * 0.5, cy - r * 0.5), (cx - r * 0.2, cy - r * 0.66)], 7, 2, "#FFFFFF", 0.6))
    out.append(f'<circle cx="{cx + r * 0.42:.1f}" cy="{cy + r * 0.42:.1f}" r="{r * 0.07:.1f}" fill="#FFFFFF" opacity="0.5"/>')
    # brass rim
    ring = blob_pts(cx, cy, r + 9, r + 9, seed, 0.004, 40)
    inner_r = blob_pts(cx, cy, r, r, seed + 1, 0.0, 40)
    rim_d = smooth_closed(ring) + " " + smooth_closed(inner_r[::-1])
    out.append(f'<path d="{rim_d}" fill="{BRASS[1]}" fill-rule="evenodd"/>')
    out.append(f'<path d="{rim_d}" fill="{D.lin([(0, "#FFF0B0", 0.9), (0.5, "#C89A3A", 0), (1, "#5A3A10", 0.8)], 0, 0, 1, 1)}" fill-rule="evenodd"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r + 4.5:.1f}" fill="none" stroke="{BRASS[2]}" stroke-width="1" opacity="0.6"/>')
    out.append(ink(smooth_closed(ring), "#3A2408", 1.8, seed, 1, 0.8))
    out.append(ink(smooth_closed(inner_r), "#3A2408", 1.2, seed + 2, 1, 0.6))
    return "".join(out)


def briar_pipe(D, x, y, s, seed, ang=0):
    """Bent briar pipe lying on its side: bowl at (x, y), stem curving away; smoke rising from the bowl."""
    def L(pts):
        return T(pts, x, y, s, False, ang)
    out = [cast(D, x + 60 * s, y + 26 * s, 90 * s, 10 * s, strength=0.4, seed=seed)]
    stem = L([(20, -6), (60, 2), (110, 0), (150, -10), (166, -16), (168, -8), (152, 0), (112, 10), (60, 12), (20, 10)])
    out.append(painted(D, stem, ("#4A3A30", "#1E1610", "#080604"), seed, sdir=(0, 1), sk=0.2, angle=ang, n=14, inkw=1.4, inkc="#000000", hi=0.4))
    out.append(taper(L([(30, -3), (80, 2), (130, 0), (160, -11)]), 2.2, 1, "#8A7A6A", 0.7))
    out.append(painted(D, L([(14, -10), (30, -10), (30, 14), (14, 14)]), BRASS, seed + 1, sk=0.2, angle=-90, n=4, inkw=1.2, hi=0.5))
    bowl = L([(-24, -30), (16, -30), (20, -8), (16, 14), (4, 26), (-14, 26), (-26, 12), (-28, -10)])
    out.append(painted(D, bowl, ("#C87A40", "#7A3E1A", "#3A1A08"), seed + 2, sdir=(0.6, 0.8), sk=0.2, angle=-80, n=24,
                       cols=["#A85A28", "#5A2A10", "#D88A4A", "#4A200A"], inkw=1.8, hi=0.45))
    # briar grain
    for k in range(5):
        out.append(pline(L([(-22 + k * 9, -26), (-20 + k * 9, 0), (-16 + k * 8, 22)]), "#3A1806", 1, seed + k, 0.4, 1))
    rim_ = ell_pts(*L([(-4, -30)])[0], 20 * s, 6 * s, 0, 360, 18)
    out.append(f'<path d="{smooth_closed(rim_)}" fill="#2A1408"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(*L([(-4, -29)])[0], 14 * s, 3.6 * s, 0, 360, 14))}" fill="#E8602A" opacity="0.7"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(*L([(-6, -29)])[0], 6 * s, 1.8 * s, 0, 360, 10))}" fill="#FFC060" opacity="0.8"/>')
    return "".join(out)


def smoke(pts, w0, w1, col="#F2EEE8", op=0.4):
    return taper(catmull(pts, 8), w0, w1, col, op)


@design("sherlock-holmes")
def sherlock_holmes():
    D = Doc2("sbc-sh")
    # desk: walnut surround, green leather inlay with a gilt-tooled border
    out = [cloth_bg(D, "#4E2E18", 1, weave=3, vign=0.5)]
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 600 L 0 600 Z", (-40, 0, 600, 600), ["#6A4026", "#2E1A0C", "#7A4A2A"], 2, n=260,
                       angle=-2, length=(60, 200), width=(1, 3), opacity=(0.15, 0.4), curve=0.04))
    lx0, ly0, lx1, ly1 = 34, 34, 566, 566
    out.append(cloth_bg(D, "#2C5A3E", 3, lx0, ly0, lx1, ly1, weave=3, vign=0.55))
    out.append(f'<rect x="{lx0}" y="{ly0}" width="{lx1 - lx0}" height="{ly1 - ly0}" fill="none" stroke="#1A0C04" stroke-width="3" opacity="0.6"/>')
    g = gilt_fill(D, 0, 600)
    out.append(f'<rect x="{lx0 + 12}" y="{ly0 + 12}" width="{lx1 - lx0 - 24}" height="{ly1 - ly0 - 24}" fill="none" stroke="{g}" stroke-width="2.2"/>')
    out.append(f'<rect x="{lx0 + 18}" y="{ly0 + 18}" width="{lx1 - lx0 - 36}" height="{ly1 - ly0 - 36}" fill="none" stroke="{g}" stroke-width="1" stroke-dasharray="1 4" stroke-linecap="round"/>')
    for (x, y, r) in ((lx0 + 12, ly0 + 12, 0), (lx1 - 12, ly0 + 12, 90), (lx1 - 12, ly1 - 12, 180), (lx0 + 12, ly1 - 12, 270)):
        out.append(fleuron(x + 14 * math.cos(math.radians(r + 45)) * 1.4, y + 14 * math.sin(math.radians(r + 45)) * 1.4, 10, "#D9A945", r + 135, 0.9))
    # lettering at the top
    out.append(letters(D, 300, 140, "The game is afoot.", SERIF_IT, 62, "#F6E6C2", ["#FFF4DC", "#E8D0A0"], 20, max_w=440,
                       shadow="#0E2A1A", soff=(0.02, 0.04), angle=-40, wob=0.5))
    out.append(tx(300, 96, "“COME, WATSON, COME!”", JOS, 19, "#E2C27A", ls=4, max_w=360))
    # a folded newspaper under everything
    npp = rot(rect_pts(250, 196, 520, 470, 30, 4, 0.6), 385, 333, 8)
    out.append(f'<path d="{smooth_closed(shift(npp, 8, 10))}" fill="#000000" opacity="0.3"/>')
    out.append(painted(D, npp, ("#FBF6EA", "#ECE4D0", "#B8AC92"), 5, sdir=(0.6, 0.8), sk=0.06, angle=-6, n=30, inkw=1.4, hi=0.2))
    rnd = random.Random(6)
    news = []
    news.append(f'<text x="385" y="224" text-anchor="middle" {DMS} font-size="21" fill="#2A2420">THE TIMES</text>')
    news.append(f'<path d="M 262 232 L 508 232 M 262 236 L 508 236" stroke="#2A2420" stroke-width="1"/>')
    for col_ in range(3):
        x0 = 266 + col_ * 82
        for k in range(26):
            y = 250 + k * 8
            if col_ == 1 and 290 < y < 330:
                continue
            news.append(f'<path d="M {x0} {y} L {x0 + rnd.uniform(56, 72):.0f} {y}" stroke="#5A544C" stroke-width="2" opacity="0.55"/>')
    news.append(f'<text x="389" y="314" text-anchor="middle" {CINZEL} font-size="11" fill="#2A2420">MYSTERY AT</text>')
    news.append(f'<text x="389" y="327" text-anchor="middle" {CINZEL} font-size="11" fill="#2A2420">THE GRANGE</text>')
    out.append(f'<g transform="rotate(8 385 333)">{"".join(news)}</g>')
    # deerstalker on the left
    out.append(deerstalker(D, 176, 336, 84, 7, ang=-28))

    # magnifier over the paper showing a magnified bootprint
    def lens(cx, cy, r):
        a = [f'<circle cx="{cx}" cy="{cy}" r="{r + 2}" fill="#F2EBD8"/>']
        for k in range(8):
            y = cy - r + 18 + k * 17
            a.append(f'<path d="M {cx - r} {y:.1f} L {cx + r} {y + 2:.1f}" stroke="#5A544C" stroke-width="4.5" opacity="0.35"/>')
        bp = rot([(cx - 12, cy - 30), (cx + 10, cy - 34), (cx + 18, cy - 18), (cx + 14, cy + 2), (cx + 6, cy + 10), (cx - 8, cy + 8), (cx - 16, cy - 8)], cx, cy, 20)
        a.append(f'<path d="{smooth_closed(bp)}" fill="#6A4A2A" opacity="0.75"/>')
        hp = rot(blob_pts(cx - 2, cy + 30, 13, 11, 9, 0.08, 12), cx, cy, 20)
        a.append(f'<path d="{smooth_closed(hp)}" fill="#6A4A2A" opacity="0.75"/>')
        for k in range(5):
            a.append(f'<circle cx="{cx - 8 + k * 5:.1f}" cy="{cy - 16 + k * 4:.1f}" r="2.2" fill="#F2EBD8" opacity="0.7"/>')
        a.append(specks(31, (cx - 30, cy - 40, cx + 30, cy + 46), ["#6A4A2A", "#8A6A4A"], 30, (0.8, 2.2), (0.4, 0.8)))
        return "".join(a)
    out.append(magnifier(D, 418, 322, 62, 48, 96, 8, lens))
    # briar pipe at the bottom with a curl of smoke
    out.append(smoke([(238, 432), (230, 404), (246, 380), (236, 352), (250, 330)], 7, 2, "#F2EEE8", 0.35))
    out.append(briar_pipe(D, 240, 462, 0.95, 9, ang=-6))
    # brass "221B" door number plate
    pl = rect_pts(388, 462, 492, 510, 12, 10, 0.4)
    out.append(cast(D, 446, 512, 58, 8, strength=0.4, seed=10))
    out.append(painted(D, pl, BRASS, 10, sdir=(0.6, 0.8), sk=0.15, angle=0, n=10, inkw=1.6, hi=0.55))
    out.append(gilt(D, 440, 500, "221B", DMS, 34, max_w=90, deboss="#3A2408", dop=0.7, pal="pale", wear=False))
    for x in (396, 484):
        out.append(f'<circle cx="{x}" cy="486" r="3" fill="{BRASS[2]}"/><path d="M {x - 2} 486 l 4 0" stroke="#FFF0B0" stroke-width="0.8"/>')
    out.append(gilt(D, 300, 534, "SHERLOCK HOLMES", CINZEL, 26, ls=6, max_w=330, seed=11))
    return finish_b(D, out, 12, INK, 0.7)


# ================================================================ 3. the wonderful wizard of oz — the road to the Emerald City
def emerald_city(D, cx, base, w, seed):
    rnd = random.Random(seed)
    out = [soft_glow(D, cx, base - 40, w * 0.9, "#9AF0B0", 0.55)]
    spires = []
    for i in range(15):
        t = i / 14
        x = cx - w / 2 + w * t + rnd.uniform(-6, 6)
        h = (26 + 84 * math.sin(math.pi * t) ** 1.6) * rnd.uniform(0.75, 1.08)
        ww = rnd.uniform(9, 17)
        spires.append((h, x, ww))
    for h, x, ww in sorted(spires):
        pts = [(x - ww / 2, base), (x - ww / 2, base - h * 0.72), (x - ww * 0.15, base - h * 0.92), (x, base - h), (x + ww * 0.15, base - h * 0.92), (x + ww / 2, base - h * 0.72), (x + ww / 2, base)]
        out.append(painted(D, pts, ("#B8F2C8", "#3EB46A", "#14683A"), seed + int(x), sdir=(1, 0.2), sk=0.3, angle=-90, n=6, inkw=1.0, inkc="#0E4A28", inkop=0.6, hi=0.6, hik=0.15))
        for k in range(int(h / 22)):
            wy = base - 10 - k * 18
            out.append(f'<rect x="{x - 1.5:.1f}" y="{wy:.1f}" width="3" height="6" fill="#F6FFE0" opacity="0.8"/>')
    # domes in front
    for k, (dx, r) in enumerate(((-w * 0.28, 18), (w * 0.05, 24), (w * 0.3, 16))):
        out.append(painted(D, ell_pts(cx + dx, base - 6, r, r * 1.1, 180, 360, 14) + [(cx + dx + r, base), (cx + dx - r, base)], ("#C8F8D0", "#4AC478", "#16703E"), seed + 40 + k,
                           sdir=(1, 0.3), sk=0.25, n=6, inkw=1, inkc="#0E4A28", hi=0.6))
        out.append(f'<path d="M {cx + dx:.1f} {base - 6 - r * 1.1:.1f} l 0 -10" stroke="#2E8A4E" stroke-width="2"/>')
    out.append(f'<rect x="{cx - w * 0.52:.1f}" y="{base - 22}" width="{w * 1.04:.1f}" height="22" fill="#2E9A5A"/>')
    for k in range(int(w / 10)):
        out.append(f'<rect x="{cx - w * 0.52 + k * 10:.1f}" y="{base - 28}" width="6" height="7" fill="#2E9A5A"/>')
    out.append(f'<rect x="{cx - w * 0.52:.1f}" y="{base - 22}" width="{w * 1.04:.1f}" height="6" fill="#8AE8A8" opacity="0.6"/>')
    for k in range(5):
        out.append(sparkle(cx + rnd.uniform(-w / 2, w / 2), base - rnd.uniform(30, 130), rnd.uniform(4, 7), "#FFFFFF", 0.85))
    return "".join(out)


def brick_road(D, center, widths, seed, rows=28):
    """Yellow brick road receding: center = list of (x, y) from near to far, widths at those points."""
    rnd = random.Random(seed)
    out = []
    n = len(center)
    L = []
    R = []
    for i in range(n):
        (x, y), w = center[i], widths[i]
        a = center[max(i - 1, 0)]
        b = center[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        L.append((x + nx * w / 2, y + ny * w / 2))
        R.append((x - nx * w / 2, y - ny * w / 2))
    road = L + R[::-1]
    out.append(f'<path d="{smooth_closed(road)}" fill="#E8B830"/>')
    cid = D.clip(f'<path d="{smooth_closed(road)}"/>')
    inner = []
    # rows of bricks: interpolate across, rows spaced by perspective (dense far away)
    for i in range(n - 1):
        (lx0, ly0), (rx0, ry0) = L[i], R[i]
        (lx1, ly1), (rx1, ry1) = L[i + 1], R[i + 1]
        w0 = math.hypot(rx0 - lx0, ry0 - ly0)
        nb = max(2, int(w0 / 26) + 2)
        off = 0.5 if i % 2 else 0
        for j in range(nb + 1):
            t0 = (j - off) / nb
            t1 = (j + 1 - off) / nb
            t0, t1 = max(0, t0), min(1, t1)
            if t1 <= t0:
                continue
            q = [(lx0 + (rx0 - lx0) * t0, ly0 + (ry0 - ly0) * t0), (lx0 + (rx0 - lx0) * t1, ly0 + (ry0 - ly0) * t1),
                 (lx1 + (rx1 - lx1) * t1, ly1 + (ry1 - ly1) * t1), (lx1 + (rx1 - lx1) * t0, ly1 + (ry1 - ly1) * t0)]
            c = rnd.choice(["#F6CA3A", "#EDB52A", "#F8D452", "#E0A422", "#F4C030"])
            inner.append(f'<path d="{pd(q)}" fill="{c}" stroke="#A8761A" stroke-width="{max(0.6, w0 / 120):.1f}" stroke-linejoin="round"/>')
            if w0 > 60 and rnd.random() < 0.5:
                inner.append(f'<path d="{pd([q[0], q[1], ((q[1][0] + q[2][0]) / 2, (q[1][1] + q[2][1]) / 2), ((q[0][0] + q[3][0]) / 2, (q[0][1] + q[3][1]) / 2)])}" fill="#FFF0A0" opacity="0.35"/>')
    inner.append(f'<path d="{smooth_closed(road)}" fill="{D.lin([(0, "#FFF2C0", 0.0), (0.7, "#FFF2C0", 0.0), (1, "#FFF6D8", 0.6)], 0, 0, 0, 1)}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(smooth_open(L), "#8A5A10", 1.6, seed, 1, 0.6))
    out.append(ink(smooth_open(R), "#8A5A10", 1.6, seed + 1, 1, 0.6))
    return "".join(out)


def silver_shoe(D, x, y, s, seed, flip=False):
    """A silver slipper (pointed toe, low curved heel, bow on the vamp), toe left; (x, y) = ground under the shoe."""
    def L(pts):
        return T(pts, x, y, s, flip)
    out = [cast(D, x + 2 * s, y + 1, 64 * s, 6 * s, strength=0.5, seed=seed)]
    sole = L([(-62, -2), (-40, 1), (-12, 1), (8, -4), (26, -11), (48, -13), (50, -9), (28, -7), (8, 0), (-14, 4), (-44, 4), (-62, 1)])
    out.append(f'<path d="{smooth_closed(sole)}" fill="#4A5060"/>')
    heel = L([(34, -10), (50, -12), (48, -4), (43, 2), (42, 4), (36, 4), (37, 0), (36, -6)])
    out.append(painted(D, heel, SILVER, seed, sdir=(1, 0.3), sk=0.25, angle=-90, n=6, inkw=1.4, inkc="#3A4250", hi=0.5))
    upper = L([(-64, -3), (-58, -11), (-44, -18), (-26, -22), (-10, -24), (8, -25), (28, -28), (46, -34), (52, -26), (50, -14),
               (30, -12), (10, -6), (-12, -1), (-40, 0)])
    out.append(painted(D, upper, SILVER, seed + 1, sdir=(0.6, 0.8), sk=0.2, angle=-8, n=26, cols=["#FFFFFF", "#9AA4B8", "#E8ECF4", "#6A7488"],
                       inkw=1.6, inkc="#3A4250", hi=0.6, hik=0.1))
    op_ = L([(-10, -24), (8, -27), (28, -31), (46, -34), (30, -27), (10, -23)])
    out.append(f'<path d="{smooth_closed(op_)}" fill="#3A4252"/>')
    out.append(f'<path d="{smooth_closed(L([(-4, -24.5), (10, -26), (28, -29), (40, -32), (28, -28), (10, -24.5)]))}" fill="#D8D0E8" opacity="0.7"/>')
    # bow on the vamp
    bx, by = L([(-24, -22)])[0]
    for sg in (-1, 1):
        lp = blob_pts(bx + sg * 7 * s, by - 3 * s, 8 * s, 4.6 * s, seed + 3 + sg, 0.1, 10, sg * 25)
        out.append(painted(D, lp, SILVER, seed + 3 + sg, sk=0.2, n=3, inkw=1.2, inkc="#3A4250", hi=0.6))
        out.append(taper([(bx, by - 2 * s), (bx + sg * 5 * s, by + 6 * s)], 3 * s, 1.5, "#9AA4B8"))
    out.append(f'<circle cx="{bx:.1f}" cy="{by - 3 * s:.1f}" r="{3 * s:.1f}" fill="#E8ECF4" stroke="#3A4250" stroke-width="1"/>')
    rnd = random.Random(seed)
    for _ in range(7):
        px, py = L([(rnd.uniform(-56, 46), rnd.uniform(-28, -6))])[0]
        out.append(sparkle(px, py, rnd.uniform(2.5, 5.5) * s, "#FFFFFF", 0.95))
    out.append(taper(L([(-58, -9), (-44, -16), (-24, -20)]), 3 * s, 1, "#FFFFFF", 0.85))
    return "".join(out)


def poppy(D, x, y, r, seed):
    out = [f'<path d="{blob(x, y, r, r * 0.8, seed, 0.18, 10)}" fill="#E8302A"/>',
           f'<path d="{blob(x + r * 0.2, y + r * 0.15, r * 0.6, r * 0.45, seed + 1, 0.2, 8)}" fill="#A8141A" opacity="0.5"/>',
           f'<path d="{blob(x - r * 0.3, y - r * 0.3, r * 0.4, r * 0.25, seed + 2, 0.2, 8)}" fill="#FF8A6A" opacity="0.6"/>',
           f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.22:.1f}" fill="#1A0A0A"/>']
    return "".join(out)


@design("the-wonderful-wizard-of-oz")
def wizard_of_oz():
    D = Doc2("sbc-oz")
    out = [sky(D, [(0, "#9ED2EC"), (0.55, "#DDF0E8"), (1, "#FFF2CC")], 1, 600, ["#FFFFFF", "#BFE4F2", "#FFF6DA"], 60)]
    out.append(puff_cloud(D, 120, 196, 150, 2, ("#FFFFFF", "#FAF6EE", "#C8D8E4")))
    out.append(puff_cloud(D, 486, 176, 130, 3, ("#FFFFFF", "#FAF6EE", "#C8D8E4")))
    hor = 300
    out.append(emerald_city(D, 300, hor, 156, 4))
    # distant fields then rolling hills, poppy fields either side
    out.append(hill(D, [(-20, hor + 6), (150, hor - 4), (300, hor + 2), (450, hor - 6), (620, hor + 4)], 640, ("#C8E0A0", "#9CC478", "#6A9A52"), 5, inkw=0, n=40))
    out.append(hill(D, [(-20, 340), (90, 322), (210, 344), (330, 350)], 640, ("#A8D07A", "#6AA850", "#3E7A34"), 6, inkw=1.2, n=60))
    out.append(hill(D, [(270, 352), (400, 330), (520, 318), (620, 330)], 640, ("#B0D682", "#72AE52", "#427E36"), 7, inkw=1.2, n=60))
    rnd = random.Random(8)
    for k in range(70):
        x = rnd.uniform(0, 600)
        y = rnd.uniform(350, 470)
        if 200 < x < 400:
            continue
        r = 3 + (y - 340) / 18
        out.append(poppy(D, x, y, r, 100 + k))
    out.append(dab_crown(D, 54, 330, 40, 34, [LEAF, ("#B8DA8A", "#6AA64A", "#2E6A2A")], 9, n=70, inkw=1))
    out.append(taper([(54, 380), (52, 350)], 9, 5, "#5A3A22"))
    out.append(dab_crown(D, 540, 324, 34, 30, [LEAF, ("#B8DA8A", "#6AA64A", "#2E6A2A")], 10, n=60, inkw=1))
    out.append(taper([(540, 370), (541, 344)], 8, 5, "#5A3A22"))
    # the road, winding from our feet to the city
    cpts = catmull([(300, 640), (250, 560), (330, 470), (260, 400), (300, 340), (300, hor)], 6)
    ws = [260 * (1 - i / (len(cpts) - 1)) ** 1.35 + 4 for i in range(len(cpts))]
    out.append(brick_road(D, cpts, ws, 11))
    out.append(grass(12, (0, 470, 600, 600), ["#4E8A3E", "#7AB85A", "#2E6A2A"], 220, (8, 18)))
    # the silver shoes standing on the road
    out.append(silver_shoe(D, 276, 516, 1.15, 13))
    out.append(silver_shoe(D, 332, 532, 1.15, 14))
    # lettering: title over the sky, quote on a ribbon
    out.append(tx(300, 92, "THE WONDERFUL", CINZEL, 26, "#1E5A36", ls=8, max_w=330))
    out.append(letters(D, 300, 168, "Wizard of Oz", DMS, 80, "#1E7A44", ["#2E9A58", "#0E5A2E", "#5AC07A"], 15, max_w=430,
                       shadow="#F6D24A", soff=(0.02, 0.035), angle=-60, wob=0.4))
    out.append(scroll_banner(D, 300, 440, 300, 42, ("#FFF2C8", "#F6E6B8", "#B89A5A"), 16, tail=30, bend=6))
    out.append(tx(300, 448, "There is no place like home.", SERIF_IT, 24, "#1E5A36", max_w=270))
    return finish_b(D, out, 17, INK, 0.7)


# ================================================================ 4. peter pan — the nursery window, second star to the right
def flyer(x, y, s, kind, ang=-12, col="#121C3C", rim="#C8D8FF"):
    """A child flying (moonlit silhouette), heading right; (x, y) = waist."""
    def L(pts):
        return T(pts, x, y, s, False, ang)
    out = []

    def limb(pts, w0, w1):
        out.append(taper(catmull(L(pts), 5), w0 * s, w1 * s, col))
        ex, ey = L([pts[-1]])[0]
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{w1 * s * 0.62:.1f}" fill="{col}"/>')
    if kind == "gown":                      # Wendy: long hair and a billowing nightgown
        head, hr = (22, -6), 6.2
        body = [(16, -7), (4, -8), (-10, -9), (-26, -12), (-42, -16), (-37, -9), (-46, -5), (-35, -1), (-43, 5), (-26, 4), (-10, 5), (6, 4), (16, 2)]
        extra = [[(28, -11), (20, -13.5), (8, -12.5), (-6, -10), (-16, -5), (-2, -5), (10, -3), (18, -2)]]
        limb([(-38, -3), (-44, -2.5), (-49, -2)], 3.4, 2.4)
        limb([(14, -5), (26, -10), (38, -15)], 4.4, 2.8)
        limb([(10, 0), (2, 6), (-6, 10)], 4.0, 2.6)
        rim_line = [(28, -12), (12, -12.5), (-6, -10.5), (-26, -13), (-40, -16)]
    elif kind == "peter":                   # Peter: leaf tunic, pointed cap with a feather, pointing the way
        head, hr = (22, -5), 5.6
        body = [(16, -6), (4, -7), (-8, -7), (-12, -6), (-16, -3), (-12, 0), (-16, 3), (-8, 5), (4, 5), (16, 3)]
        extra = [[(27, -9), (22, -13.5), (12, -17), (2, -15), (16, -8)]]
        limb([(-9, -3), (-22, -6), (-36, -5)], 5.0, 3.0)
        limb([(-9, 2), (-20, 6), (-30, 13)], 5.0, 3.0)
        limb([(14, -4), (28, -12), (42, -21)], 4.0, 2.6)
        limb([(10, 1), (0, 8), (-8, 7)], 3.8, 2.4)
        out.append(taper(L([(10, -15), (2, -20), (-6, -26)]), 2.4 * s, 0.6 * s, col))
        rim_line = [(26, -12), (12, -16), (2, -14)]
    elif kind == "hat":                     # John: nightshirt, Sunday top hat
        head, hr = (22, -4), 5.8
        body = [(16, -6), (2, -7), (-14, -7), (-18, -1), (-14, 5), (2, 5), (16, 3)]
        extra = [[(17, -9.5), (28, -10.5), (29.5, -23), (18.5, -22)]]
        out.append(taper(L([(13, -9), (32, -11)]), 2.8 * s, 2.8 * s, col))
        limb([(-14, -3), (-28, -4), (-41, -2)], 5.2, 3.2)
        limb([(-14, 2), (-27, 4), (-38, 9)], 5.2, 3.2)
        limb([(14, -3), (26, -7), (37, -6)], 4.2, 2.8)
        limb([(10, 1), (0, 7), (-8, 10)], 4.0, 2.6)
        rim_line = [(18, -22), (29, -23)]
    else:                                   # Michael: the little one
        head, hr = (16, -4), 6.2
        body = [(12, -5), (0, -6), (-10, -5), (-12, 0), (-8, 5), (4, 5), (12, 3)]
        extra = []
        limb([(-8, -2), (-18, -3), (-27, -1)], 4.8, 3.2)
        limb([(-8, 2), (-17, 5), (-25, 10)], 4.8, 3.2)
        limb([(10, -3), (20, -8), (29, -12)], 4.0, 2.6)
        limb([(6, 1), (-2, 7), (-8, 9)], 3.8, 2.4)
        rim_line = [(20, -10), (10, -10)]
    out.append(f'<path d="{smooth_closed(L(body))}" fill="{col}"/>')
    for e in extra:
        out.append(f'<path d="{smooth_closed(L(e))}" fill="{col}"/>')
    hx, hy = L([head])[0]
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{hr * s:.1f}" fill="{col}"/>')
    out.append(ink(smooth_open(L(rim_line)), rim, 1.3 * s * 0.6, 2, 1, 0.55))
    return "".join(out)


def chimney_row(D, base, seed, col="#1A2444", lit="#FFC870"):
    """London roofline: slate roofs, chimney stacks with pots and smoke, a few lit windows."""
    rnd = random.Random(seed)
    out = []
    x = -20
    roofs = []
    while x < 620:
        w = rnd.uniform(70, 120)
        h = rnd.uniform(26, 60)
        roofs.append((x, w, h))
        x += w - 6
    for i, (x, w, h) in enumerate(roofs):
        top = base - h
        pitch = rnd.choice([0, 1])
        if pitch:
            pts = [(x, base + 40), (x, top + 18), (x + w * 0.5, top - 4), (x + w, top + 18), (x + w, base + 40)]
        else:
            pts = [(x, base + 40), (x, top + 12), (x + 8, top), (x + w - 8, top), (x + w, top + 12), (x + w, base + 40)]
        c = mix(col, "#3A4A78", rnd.uniform(0, 0.25))
        out.append(f'<path d="{hg.org_poly(pts, seed + i, 0.5, 14, 2)}" fill="{c}"/>')
        out.append(pline([pts[1], pts[2], pts[3]] if not pitch else [pts[1], pts[2], pts[3]], "#7A90C8", 1.6, seed + i, 0.5, 1))
        # chimney stacks with pots
        for k in range(rnd.choice([1, 1, 2])):
            cx = x + w * rnd.uniform(0.2, 0.8)
            ch_top = top - rnd.uniform(16, 30)
            out.append(f'<path d="{hg.org_rect(cx - 9, ch_top, 18, top - ch_top + 12, seed + i * 7 + k, 0.4, 8, 1)}" fill="{dk(c, 0.1)}"/>')
            out.append(f'<rect x="{cx - 11:.1f}" y="{ch_top - 3:.1f}" width="22" height="4" fill="{dk(c, 0.15)}"/>')
            for j in range(rnd.choice([2, 3])):
                px = cx - 6 + j * 6
                out.append(f'<rect x="{px - 2:.1f}" y="{ch_top - 10:.1f}" width="4.5" height="8" fill="#5A3A3A"/>')
            if rnd.random() < 0.6:
                out.append(taper(catmull([(cx, ch_top - 12), (cx + 6, ch_top - 30), (cx + 20, ch_top - 44), (cx + 40, ch_top - 50)], 5), 5, 12, "#9AA8D0", 0.22))
        # windows
        for k in range(rnd.randint(1, 3)):
            wx = x + rnd.uniform(10, w - 22)
            wy = top + rnd.uniform(20, 30)
            if wy > base - 4:
                continue
            on = rnd.random() < 0.55
            out.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="9" height="11" fill="{lit if on else dk(c, 0.3)}"/>')
            if on:
                out.append(soft_glow(D, wx + 4.5, wy + 5, 16, lit, 0.4))
    return "".join(out)


def curtain(D, x_attach, top, bottom, side, seed, pal=("#F2D6CC", "#C8907E", "#7A4A48")):
    """A heavy curtain hanging from the rail, blowing in toward the room (side=-1 left, 1 right)."""
    rnd = random.Random(seed)
    xa = x_attach
    pts = [(xa - side * 6, top)]
    pts += [(xa + side * 70, top), (xa + side * 64, top + (bottom - top) * 0.3), (xa + side * 40, top + (bottom - top) * 0.62),
            (xa + side * 22, top + (bottom - top) * 0.82), (xa + side * 50, bottom), (xa + side * 10, bottom + 6), (xa - side * 10, bottom - 8),
            (xa - side * 30, top + (bottom - top) * 0.55), (xa - side * 14, top + (bottom - top) * 0.22)]
    d = smooth_closed(pts)
    out = [f'<path d="{smooth_closed(shift(pts, side * 8, 8))}" fill="#000000" opacity="0.25"/>']
    out.append(painted(D, pts, pal, seed, sdir=(side, 0.2), sk=0.12, angle=-92, n=40, inkw=1.6, hi=0.35))
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for k in range(5):
        fx = xa + side * (-18 + k * 18)
        inner.append(taper(catmull([(fx, top), (fx - side * 6, (top + bottom) / 2), (fx - side * (14 - k * 4), bottom)], 6), 7, 12, pal[2], 0.3))
        inner.append(taper(catmull([(fx + side * 6, top), (fx, (top + bottom) / 2), (fx - side * (8 - k * 4), bottom)], 6), 3, 5, pal[0], 0.45))
    # sprigged print
    for _ in range(40):
        px, py = rnd.uniform(xa - 60, xa + 80) if side > 0 else rnd.uniform(xa - 80, xa + 60), rnd.uniform(top, bottom)
        inner.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2" fill="#8A3A4A" opacity="0.45"/>')
        inner.append(f'<path d="M {px - 3:.1f} {py + 3:.1f} l -3 3" stroke="#5A7A4A" stroke-width="1.2" opacity="0.5"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(out)


def thimble(D, cx, base, h, seed):
    w = h * 0.8
    body = [(cx - w / 2, base), (cx - w * 0.42, base - h * 0.75), (cx - w * 0.25, base - h), (cx + w * 0.25, base - h), (cx + w * 0.42, base - h * 0.75), (cx + w / 2, base)]
    out = [cast(D, cx + 4, base, w * 0.8, 4, strength=0.45, seed=seed)]
    out.append(painted(D, body, SILVER, seed, sdir=(1, 0.3), sk=0.25, angle=-90, n=6, inkw=1.2, inkc="#3A4250", hi=0.6))
    rnd = random.Random(seed)
    for i in range(14):
        out.append(f'<circle cx="{cx + rnd.uniform(-w * 0.3, w * 0.3):.1f}" cy="{base - rnd.uniform(h * 0.25, h * 0.9):.1f}" r="0.9" fill="#5A6070" opacity="0.6"/>')
    out.append(f'<path d="M {cx - w / 2:.1f} {base - 3:.1f} L {cx + w / 2:.1f} {base - 3:.1f}" stroke="#5A6070" stroke-width="1.4"/>')
    return "".join(out)


def acorn_button(D, cx, cy, s, seed, rot_=0):
    from gouache import acorn
    return cast(D, cx + 3, cy + s * 0.9, s * 0.6, 3, strength=0.4, seed=seed) + acorn(cx, cy, s, rot_)


@design("peter-pan")
def peter_pan():
    D = Doc2("sbc-pp")
    # nursery wall in moonlit blue with a faint striped paper
    out = [f'<rect width="600" height="600" fill="#2C3858"/>']
    for k in range(20):
        out.append(f'<rect x="{k * 30}" y="0" width="12" height="600" fill="#3A4A70" opacity="0.35"/>')
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#A8C0F0", 0.25), (0.5, "#A8C0F0", 0.05), (1, "#000010", 0.55)], cx=0.5, cy=0.42, r=0.7)}"/>')
    wx0, wy0, wx1, wy1 = 150, 152, 450, 404
    # the night outside
    cid = D.clip(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}"/>')
    night = [f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="{D.lin([(0, "#0C1838"), (0.6, "#24407A"), (1, "#5A78B0")])}"/>']
    night.append(stars_field(3, (wx0, wy0, wx1, wy1 - 70), 90))
    night.append(soft_glow(D, 206, 206, 90, "#E8F0FF", 0.35))
    night.append(f'<path d="{blob(206, 206, 26, 26, 4, 0.02, 20)}" fill="#F6F2E0"/>')
    night.append(f'<path d="{blob(217, 200, 26, 26, 5, 0.02, 20)}" fill="#203A72" opacity="0.92"/>')
    night.append(puff_cloud(D, 300, 330, 300, 5, ("#D8E2F8", "#A8B8E0", "#6A7AAA"), op=0.9))
    night.append(puff_cloud(D, 160, 300, 150, 9, ("#C8D4F0", "#98A8D4", "#5A6A9A"), op=0.75))
    # the stars to steer by: the second from the right shines brightest
    for (sx, sy, r, g) in ((408, 196, 13, 0.75), (370, 178, 6, 0.4), (430, 238, 5, 0.35), (330, 190, 4, 0.3)):
        night.append(soft_glow(D, sx, sy, r * 6, "#FFF2C0", g))
        night.append(star4(sx, sy, r * 2.2, "#FFFFFF", 0.95))
        night.append(f'<circle cx="{sx}" cy="{sy}" r="{r * 0.45:.1f}" fill="#FFFFFF"/>')
    # fairy dust trail and the flying children
    rnd = random.Random(6)
    trail = catmull([(160, 340), (200, 300), (260, 270), (320, 250), (372, 228), (398, 214)], 8)
    for (px, py) in trail:
        for _ in range(3):
            night.append(f'<circle cx="{px + rnd.uniform(-8, 8):.1f}" cy="{py + rnd.uniform(-8, 8):.1f}" r="{rnd.uniform(0.6, 1.8):.1f}" fill="#FFE8A0" opacity="{rnd.uniform(0.4, 0.95):.2f}"/>')
    night.append(soft_glow(D, 392, 222, 18, "#FFE070", 0.95))
    night.append(f'<circle cx="392" cy="222" r="3" fill="#FFFBE0"/>')
    night.append(flyer(352, 240, 1.25, "peter", -24))
    night.append(flyer(282, 286, 1.3, "gown", -18))
    night.append(flyer(232, 240, 1.15, "hat", -14))
    night.append(flyer(258, 336, 1.1, "small", -10))
    night.append(chimney_row(D, 382, 7))
    night.append(f'<rect x="{wx0}" y="350" width="{wx1 - wx0}" height="60" fill="{D.lin([(0, "#0A1028", 0), (1, "#0A1028", 0.6)])}"/>')
    out.append(f'<g {cid}>{"".join(night)}</g>')
    # window frame: casement leaves swung open, glazing bars, moonlight on the reveal
    frame = "#E8E2D2"
    out.append(f'<path d="{hg.org_rect(wx0 - 16, wy0 - 16, wx1 - wx0 + 32, wy1 - wy0 + 32, 8, 0.5, 30, 1)} {hg.org_rect(wx0, wy0, wx1 - wx0, wy1 - wy0, 9, 0.4, 30, 1)}" fill="{frame}" fill-rule="evenodd"/>')
    out.append(f'<path d="{hg.org_rect(wx0 - 16, wy0 - 16, wx1 - wx0 + 32, wy1 - wy0 + 32, 8, 0.5, 30, 1)} {hg.org_rect(wx0, wy0, wx1 - wx0, wy1 - wy0, 9, 0.4, 30, 1)}" fill="{D.lin([(0, "#FFFFFF", 0.3), (1, "#5A6A90", 0.5)], 0, 0, 1, 1)}" fill-rule="evenodd"/>')
    out.append(ink(hg.org_rect(wx0 - 16, wy0 - 16, wx1 - wx0 + 32, wy1 - wy0 + 32, 8, 0.5, 30, 1), "#1A2038", 1.8, 10, 1, 0.7))
    for sg, xe in ((-1, wx0), (1, wx1)):
        leaf_ = [(xe, wy0), (xe + sg * 40, wy0 + 26), (xe + sg * 40, wy1 - 26), (xe, wy1)]
        out.append(f'<path d="{pd(leaf_)}" fill="#C8C8D0"/>')
        out.append(f'<path d="{pd([(xe + sg * 4, wy0 + 10), (xe + sg * 34, wy0 + 32), (xe + sg * 34, wy1 - 32), (xe + sg * 4, wy1 - 10)])}" fill="{D.lin([(0, "#8AA8E0"), (1, "#3A5088")])}"/>')
        for t in (0.33, 0.66):
            y0_ = wy0 + 10 + (wy1 - wy0 - 20) * t
            out.append(f'<path d="M {xe + sg * 4:.1f} {y0_:.1f} L {xe + sg * 34:.1f} {y0_ + 22 * (0.5 - t) * 0.6:.1f}" stroke="#C8C8D0" stroke-width="4"/>')
        out.append(taper([(xe + sg * 10, wy0 + 30), (xe + sg * 26, wy0 + 60)], 4, 1, "#FFFFFF", 0.5))
        out.append(ink(pd(leaf_), "#1A2038", 1.4, 11, 1, 0.6))
    # curtains billowing in
    out.append(curtain(D, wx0 - 6, wy0 - 30, wy1 + 34, -1, 12))
    out.append(curtain(D, wx1 + 6, wy0 - 30, wy1 + 34, 1, 13))
    out.append(painted(D, rect_pts(70, wy0 - 40, 530, wy0 - 28, 30, 14, 0.3), BRASS, 14, sk=0.2, angle=0, n=12, inkw=1.2, hi=0.5))
    for x in (70, 530):
        out.append(f'<circle cx="{x}" cy="{wy0 - 34}" r="9" fill="{BRASS[1]}" stroke="{BRASS[2]}" stroke-width="1.5"/>')
    # sill with Wendy's thimble and Peter's acorn button
    out.append(painted(D, rect_pts(110, wy1 + 14, 490, wy1 + 38, 30, 15, 0.3), ("#F2EEE4", "#D8D2C2", "#8A8478"), 15, sdir=(0.3, 1), sk=0.25, angle=0, n=20, inkw=1.6, hi=0.4))
    out.append(thimble(D, 262, wy1 + 18, 28, 16))
    out.append(acorn_button(D, 334, wy1 + 2, 20, 17, 18))
    out.append(taper([(300, wy1 + 14), (316, wy1 + 4), (326, wy1 - 4)], 1.6, 1, "#8A6A4A"))
    # lettering
    out.append(gilt(D, 300, 88, "PETER PAN", CINZEL, 32, ls=10, max_w=300, seed=18, pal="pale"))
    out.append(letters(D, 300, 492, "Second to the right,", SERIF_IT, 44, "#FFF2D0", ["#FFF8E6", "#E8D8B0"], 19, max_w=420,
                       shadow="#0E1630", soff=(0.02, 0.05), angle=-40, wob=0.4))
    out.append(letters(D, 300, 536, "and straight on till morning.", SERIF_IT, 34, "#F2D890", ["#FFE8A8", "#D8B868"], 20, max_w=440,
                       shadow="#0E1630", soff=(0.02, 0.05), angle=-40, wob=0.4))
    return finish_b(D, out, 21, "#000010", 0.6)


# ================================================================ 5. treasure island — the map, X marks the treasure
def compass_rose(cx, cy, r, ink_c="#5A3418", fill1="#C8402A", fill2="#E8D2A0"):
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r * 0.62:.1f}" fill="none" stroke="{ink_c}" stroke-width="1.4"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{r * 0.55:.1f}" fill="none" stroke="{ink_c}" stroke-width="0.8"/>']
    for i in range(16):
        a = math.radians(i * 22.5 - 90)
        L = r if i % 4 == 0 else (r * 0.7 if i % 2 == 0 else r * 0.48)
        w = r * (0.16 if i % 4 == 0 else 0.1)
        b1 = (cx + math.cos(a + math.pi / 2) * w, cy + math.sin(a + math.pi / 2) * w)
        b2 = (cx + math.cos(a - math.pi / 2) * w, cy + math.sin(a - math.pi / 2) * w)
        tip = (cx + math.cos(a) * L, cy + math.sin(a) * L)
        c = fill1 if i % 4 == 0 else ink_c
        out.append(f'<path d="{pd([(cx, cy), b1, tip])}" fill="{c}" opacity="0.9"/>')
        out.append(f'<path d="{pd([(cx, cy), b2, tip])}" fill="{fill2 if i % 4 == 0 else lt(ink_c, 0.35)}"/>')
        out.append(f'<path d="{pd([b1, tip, b2], False)}" fill="none" stroke="{ink_c}" stroke-width="0.9"/>')
    out.append(f'<text x="{cx}" y="{cy - r - 6:.1f}" text-anchor="middle" {CINZEL} font-size="{r * 0.42:.1f}" fill="{ink_c}">N</text>')
    return "".join(out)


def tall_ship(x, y, s, col="#5A3418", sail="#F2E6C8"):
    """Little pen-and-wash ship for the map."""
    def L(pts):
        return T(pts, x, y, s)
    out = [f'<path d="{smooth_closed(L([(-30, 0), (30, 0), (24, 10), (-24, 10)]))}" fill="#8A5A30" stroke="{col}" stroke-width="1.2"/>']
    for mx, h in ((-12, 40), (8, 48), (24, 30)):
        out.append(f'<path d="M {L([(mx, 0)])[0][0]:.1f} {L([(mx, 0)])[0][1]:.1f} L {L([(mx, -h)])[0][0]:.1f} {L([(mx, -h)])[0][1]:.1f}" stroke="{col}" stroke-width="1.4"/>')
        for k, (w, yy) in enumerate(((10, -h * 0.85), (12, -h * 0.5))):
            sp = L([(mx - w, yy - h * 0.25), (mx + w, yy - h * 0.25), (mx + w * 0.85, yy + 2), (mx - w * 0.85, yy + 2)])
            out.append(f'<path d="{smooth_closed(sp)}" fill="{sail}" stroke="{col}" stroke-width="1"/>')
    out.append(f'<path d="{pd(L([(8, -48), (8, -56), (18, -53)]))}" fill="#C8402A"/>')
    return "".join(out)


def coin(D, cx, cy, r, seed, tilt=1.0):
    out = [cast(D, cx + 4, cy + 5, r * 1.1, r * tilt * 1.1, strength=0.45, seed=seed)]
    out.append(painted(D, ell_pts(cx, cy, r, r * tilt, 0, 360, 24)[:-1], GOLD, seed, sdir=(0.6, 0.8), sk=0.18, angle=-30, n=10, inkw=1.4, inkc="#6A4810", hi=0.5))
    out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r * 0.78:.1f}" ry="{r * 0.78 * tilt:.1f}" fill="none" stroke="#8A6020" stroke-width="1.2" opacity="0.8"/>')
    # cross of a piece of eight
    out.append(f'<path d="M {cx:.1f} {cy - r * 0.5 * tilt:.1f} L {cx:.1f} {cy + r * 0.5 * tilt:.1f} M {cx - r * 0.5:.1f} {cy:.1f} L {cx + r * 0.5:.1f} {cy:.1f}" stroke="#8A6020" stroke-width="{max(1.5, r * 0.12):.1f}" opacity="0.75"/>')
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.append(f'<circle cx="{cx + sx * r * 0.32:.1f}" cy="{cy + sy * r * 0.32 * tilt:.1f}" r="{r * 0.07:.1f}" fill="#8A6020"/>')
    out.append(taper([(cx - r * 0.6, cy - r * 0.3 * tilt), (cx - r * 0.3, cy - r * 0.62 * tilt)], 3, 1, "#FFF6C8", 0.8))
    return "".join(out)


@design("treasure-island")
def treasure_island():
    D = Doc2("sbc-ti")
    out = [cloth_bg(D, "#3E2414", 1, weave=3, vign=0.6)]
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 600 L 0 600 Z", (-40, 0, 600, 600), ["#5A3620", "#24140A", "#6A4226"], 2, n=240,
                       angle=4, length=(60, 220), width=(1, 3), opacity=(0.2, 0.45), curve=0.04))
    # the map: parchment with ragged, scorched edges
    mp = []
    rnd = random.Random(3)
    corners = [(52, 64), (548, 50), (556, 548), (46, 556)]
    for k in range(4):
        (ax, ay), (bx, by) = corners[k], corners[(k + 1) % 4]
        n = 22
        for i in range(n):
            t = i / n
            mp.append((ax + (bx - ax) * t + rnd.uniform(-4, 4), ay + (by - ay) * t + rnd.uniform(-4, 4)))
    md = smooth_closed(mp)
    out.append(f'<path d="{smooth_closed(shift(mp, 10, 12))}" fill="#000000" opacity="0.4"/>')
    out.append(f'<path d="{md}" fill="#EAD6A6"/>')
    cid = D.clip(f'<path d="{md}"/>')
    inner = [blooms(4, ["#C8A060", "#B88A48", "#D8B878"], 9, (60, 60, 540, 540), (60, 140), (0.12, 0.22))]
    inner.append(f'<path d="{md}" fill="{D.rad([(0, "#000000", 0), (0.7, "#5A3010", 0.05), (1, "#5A2A08", 0.55)], r=0.72)}"/>')
    # sea wash and ruled wave hatching
    inner.append(f'<rect width="600" height="600" fill="#7AA8A0" opacity="0.28"/>')
    for k in range(60):
        y = 70 + k * 8
        inner.append(f'<path d="M 40 {y} q 6 -3 12 0 t 12 0 t 12 0 t 12 0" stroke="#4A7A78" stroke-width="1" fill="none" opacity="0.0"/>')
    inner.append(wave_lines(5, (70, 80, 530, 530), ["#3E6A6A", "#5A8A84"], 70, (10, 22), 1.6, 2.5, (0.35, 0.7)))
    # the island
    isl = [(170, 210), (214, 168), (262, 176), (300, 150), (352, 160), (392, 140), (430, 170), (444, 214), (420, 248), (446, 290),
           (432, 340), (392, 360), (370, 400), (322, 412), (300, 384), (262, 400), (224, 384), (210, 344), (172, 330), (182, 292), (150, 262)]
    for k, off in enumerate((26, 16, 8)):
        ring = blob_pts(300, 280, 1, 1, 1)
        sc = 1 + off / 140
        ring = [(300 + (x - 300) * sc, 280 + (y - 280) * sc) for x, y in isl]
        inner.append(f'<path d="{smooth_closed(ring)}" fill="none" stroke="#3E6A6A" stroke-width="1.2" opacity="{0.25 + k * 0.15:.2f}"/>')
    idd = smooth_closed(isl)
    inner.append(f'<path d="{idd}" fill="#D8C080"/>')
    inner.append(f'<path d="{smooth_closed([(300 + (x - 300) * 0.86, 280 + (y - 280) * 0.86) for x, y in isl])}" fill="#A8B872" opacity="0.75"/>')
    inner.append(strokes(D.nid(), idd, (150, 140, 450, 420), ["#8AA05A", "#C8B070", "#6A8A48"], 6, n=60, angle=-30, length=(10, 24), width=(2, 4), opacity=(0.2, 0.4)))
    inner.append(ink(idd, "#4A2A10", 2.2, 7, 2, 0.85))
    # hills with hachures: the spy-glass hill is the tallest
    for (hx, hy, hw, hh) in ((330, 214, 44, 34), (250, 250, 30, 22), (390, 300, 28, 20), (220, 320, 24, 16)):
        inner.append(f'<path d="M {hx - hw} {hy} Q {hx} {hy - hh * 2} {hx + hw} {hy} Z" fill="#B89A5A" opacity="0.8"/>')
        inner.append(pline([(hx - hw, hy), (hx - hw * 0.4, hy - hh * 0.8), (hx, hy - hh), (hx + hw * 0.5, hy - hh * 0.7), (hx + hw, hy)], "#4A2A10", 1.6, hx, 0.85, 1))
        for j in range(7):
            t = j / 6
            px = hx - hw * 0.8 + hw * 1.6 * t
            inner.append(f'<path d="M {px:.1f} {hy - hh * 0.9 * math.sin(math.pi * (0.1 + 0.8 * t)):.1f} l {2 + t * 2:.1f} {hh * 0.55:.1f}" stroke="#4A2A10" stroke-width="1" opacity="0.6"/>')
    # trees as little inked tufts
    for k in range(34):
        tx_, ty_ = rnd.uniform(190, 420), rnd.uniform(190, 390)
        if not (170 < tx_ < 440) or (340 < tx_ and 236 < ty_ < 306):
            continue
        inner.append(f'<path d="M {tx_:.1f} {ty_:.1f} l 0 6" stroke="#4A2A10" stroke-width="1.2"/><path d="{blob(tx_, ty_ - 2, 5, 4.5, k, 0.2, 8)}" fill="#5A7A3A" stroke="#3A2A10" stroke-width="0.9"/>')
    # dotted trail to the treasure
    trail = catmull([(232, 396), (262, 360), (296, 340), (322, 310), (352, 292)], 6)
    inner.append(f'<path d="{smooth_open(trail)}" fill="none" stroke="#8A2A1A" stroke-width="2.2" stroke-dasharray="1 7" stroke-linecap="round"/>')
    # the red X
    for sg in (-1, 1):
        inner.append(taper([(352 - 13, 292 - 13 * sg), (352 + 13, 292 + 13 * sg)], 5, 4, "#B8241A"))
    inner.append(f'<path d="{blob(424, 272, 74, 30, 77, 0.12, 14, -8)}" fill="#F2E2B8" opacity="0.85"/>')
    inner.append(f'<text x="372" y="270" {SERIF_IT} font-size="20" fill="#9A1E14" transform="rotate(-8 372 270)">Bulk of</text>')
    inner.append(f'<text x="368" y="290" {SERIF_IT} font-size="19" fill="#9A1E14" transform="rotate(-8 368 290)">treasure here</text>')
    # compass rose, ship, sea serpent
    inner.append(compass_rose(118, 138, 44))
    inner.append(tall_ship(478, 410, 0.9))
    inner.append(wave_lines(8, (440, 412, 520, 424), ["#3E6A6A"], 6, (10, 16), 1.4, 2, (0.6, 0.8)))
    serp = catmull([(88, 436), (104, 420), (120, 438), (136, 420), (152, 438), (166, 424), (176, 414)], 6)
    inner.append(taper(serp, 9, 4, "#5A7A48", 0.9))
    inner.append(pline(serp, "#3A2A10", 1.2, 9, 0.8, 1))
    inner.append(f'<path d="{blob(180, 412, 8, 6, 9, 0.1, 8, -30)}" fill="#5A7A48" stroke="#3A2A10" stroke-width="1"/>')
    inner.append(f'<circle cx="182" cy="410" r="1.4" fill="#1A1008"/>')
    inner.append(wave_lines(10, (80, 430, 190, 444), ["#3E6A6A"], 8, (8, 14), 1.4, 2, (0.6, 0.8)))
    # scorch along the edges
    inner.append(ink(md, "#3A1A06", 7, 11, 1, 0.5))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(md, "#2A1206", 1.6, 12, 1, 0.8))
    # cartouche scroll with the title
    out.append(scroll_banner(D, 270, 480, 320, 58, ("#F6E6BE", "#E8D2A0", "#9A7A48"), 13, tail=32, bend=7))
    out.append(tx(270, 496, "Treasure Island", DMS, 44, "#4A2410", max_w=290))
    out.append(tx(300, 104, "R. L. STEVENSON · 1883", MONO, 16, "#5A3418", ls=3, max_w=250, extra=' transform="rotate(-1.5 300 104)"'))
    # gold coins spilled on the corner
    out.append(coin(D, 488, 494, 24, 14))
    out.append(coin(D, 516, 470, 20, 15, 0.9))
    out.append(coin(D, 470, 526, 18, 16, 0.6))
    return finish_b(D, out, 17, INK, 0.8)


# ================================================================ 6. alice's adventures in wonderland — late! the white rabbit
def white_rabbit(D, ox, oy, s, seed):
    """The White Rabbit in a waistcoat, mid-hurry, facing left, holding up his pocket watch; (ox, oy) = ground."""
    def L(pts):
        return T(pts, ox, oy, s)
    fur = ("#FFFFFF", "#F2EEE6", "#A8A098")
    fcol = ["#FFFFFF", "#E2DCD2", "#C8C0B6", "#FFFFFF"]
    inkc = "#6A5A50"
    out = [cast(D, ox + 10 * s, oy, 90 * s, 9 * s, strength=0.35, seed=seed)]
    # far hind leg kicked back
    far = L([(20, -60), (44, -44), (70, -20), (96, -8), (98, 0), (66, 0), (40, -18), (14, -40)])
    out.append(painted(D, far, ("#E8E2D8", "#CFC8BC", "#8A8278"), seed, sk=0.2, angle=-20, n=16, cols=fcol, inkw=1.4, inkc=inkc, hi=0.3))
    # tail
    out.append(painted(D, blob_pts(*L([(44, -84)])[0], 15 * s, 13 * s, seed + 1, 0.2, 12), fur, seed + 1, sk=0.2, n=10, cols=fcol, inkw=1.2, inkc=inkc, hi=0.4))
    # body
    body = L([(-24, -170), (6, -176), (34, -150), (48, -110), (46, -70), (30, -44), (0, -36), (-26, -48), (-38, -86), (-38, -130)])
    out.append(painted(D, body, fur, seed + 2, sdir=(1, 0.4), sk=0.14, angle=-70, n=40, cols=fcol, inkw=1.6, inkc=inkc, hi=0.4))
    # near hind leg (big thigh, foot forward)
    thigh = L([(-6, -84), (26, -96), (44, -70), (36, -36), (10, -16), (-30, -6), (-62, -2), (-66, 4), (-30, 6), (6, 2), (-18, -40)])
    out.append(painted(D, thigh, fur, seed + 3, sdir=(1, 0.5), sk=0.16, angle=-30, n=30, cols=fcol, inkw=1.6, inkc=inkc, hi=0.4))
    out.append(pline(L([(-56, 1), (-48, -3)]), inkc, 1.2, seed, 0.6, 1))
    # waistcoat (plum check) with buttons and a watch-pocket
    wc = L([(-22, -164), (-2, -160), (12, -150), (24, -120), (26, -88), (14, -66), (-16, -60), (-30, -76), (-32, -118), (-30, -150)])
    wd = smooth_closed(wc)
    out.append(f'<path d="{wd}" fill="#7A2E4A"/>')
    pat = D.pattern(12, 12, '<rect width="12" height="12" fill="#7A2E4A"/><rect width="12" height="4" fill="#9A4262" opacity="0.7"/><rect width="4" height="12" fill="#9A4262" opacity="0.7"/>'
                    '<rect y="8" width="12" height="1" fill="#E8C060" opacity="0.6"/>', transform="rotate(12)")
    out.append(f'<path d="{wd}" fill="{pat}"/>')
    out.append(shade_over(D, wd, "#1A0410", 0.45, 0, 0, 1, 0.6))
    out.append(ink(wd, "#3A1020", 1.8, seed + 4, 2, 0.8))
    for k in range(4):
        bx, by = L([(-10 + k * 1.5, -146 + k * 18)])[0]
        out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{3.4 * s:.1f}" fill="#E8C060" stroke="#6A4A10" stroke-width="1"/>')
    # cravat / bow at the collar
    for sg in (-1, 1):
        out.append(painted(D, blob_pts(*L([(-14 + sg * 9, -166)])[0], 9 * s, 6 * s, seed + 5 + sg, 0.12, 10, sg * 20), ("#F0E4C8", "#E0CFA8", "#9A8A60"), seed + 5 + sg, sk=0.2, n=4, inkw=1.2, inkc=inkc, hi=0.4))
    # head
    head = L([(-30, -232), (-12, -244), (12, -238), (24, -220), (20, -196), (2, -178), (-24, -174), (-44, -182), (-56, -194), (-54, -212), (-44, -226)])
    out.append(painted(D, head, fur, seed + 6, sdir=(1, 0.5), sk=0.14, angle=-20, n=26, cols=fcol, inkw=1.6, inkc=inkc, hi=0.45))
    # cheek fluff
    out.append(pline(L([(-10, -186), (-4, -180), (2, -184), (6, -178)]), inkc, 1.1, seed, 0.5, 1))
    # ears, long, swept back with the rush
    for k, (base_, tip, w) in enumerate((((-8, -236), (52, -330), 15), ((6, -234), (76, -306), 13))):
        ux, uy = tip[0] - base_[0], tip[1] - base_[1]
        Ln = math.hypot(ux, uy)
        nx, ny = -uy / Ln, ux / Ln
        ear = []
        for i in range(9):
            t = i / 8
            ww = w * math.sin(math.pi * min(0.98, 0.15 + t * 0.85)) ** 0.6
            ear.append((base_[0] + ux * t + nx * ww, base_[1] + uy * t + ny * ww))
        for i in range(8, -1, -1):
            t = i / 8
            ww = w * math.sin(math.pi * min(0.98, 0.15 + t * 0.85)) ** 0.6
            ear.append((base_[0] + ux * t - nx * ww, base_[1] + uy * t - ny * ww))
        out.append(painted(D, L(ear), fur if k == 0 else ("#F2EEE6", "#E2DCD2", "#9A928A"), seed + 7 + k, sk=0.15, angle=-60, n=12, cols=fcol, inkw=1.4, inkc=inkc, hi=0.4))
        inner = [(base_[0] + ux * t + nx * w * 0.45 * math.sin(math.pi * (0.2 + t * 0.7)), base_[1] + uy * t + ny * w * 0.45 * math.sin(math.pi * (0.2 + t * 0.7))) for t in [i / 8 for i in range(1, 8)]]
        inner += [(base_[0] + ux * t - nx * w * 0.35 * math.sin(math.pi * (0.2 + t * 0.7)), base_[1] + uy * t - ny * w * 0.35 * math.sin(math.pi * (0.2 + t * 0.7))) for t in [i / 8 for i in range(7, 0, -1)]]
        if k == 0:
            out.append(f'<path d="{smooth_closed(L(inner))}" fill="#F2A8B0" opacity="0.85"/>')
    # eye (pink, as in the book), nose, whiskers
    ex, ey = L([(-26, -212)])[0]
    out.append(f'<path d="{blob(ex, ey, 7.5 * s, 8.5 * s, seed + 9, 0.05, 12)}" fill="#C83A5A"/>')
    out.append(f'<circle cx="{ex - 1 * s:.1f}" cy="{ey:.1f}" r="{3.6 * s:.1f}" fill="#3A0A14"/>')
    out.append(f'<circle cx="{ex - 3 * s:.1f}" cy="{ey - 3 * s:.1f}" r="{2.2 * s:.1f}" fill="#FFFFFF"/>')
    out.append(pline(L([(-34, -220), (-26, -224), (-18, -220)]), inkc, 1.3, seed, 0.6, 1))
    nx_, ny_ = L([(-55, -200)])[0]
    out.append(f'<path d="{blob(nx_, ny_, 5 * s, 4 * s, seed + 10, 0.1, 8)}" fill="#E87A8A"/>')
    out.append(pline(L([(-54, -195), (-50, -188), (-44, -186)]), inkc, 1.2, seed, 0.6, 1))
    for k in range(3):
        out.append(pline(L([(-48, -196 + k * 4), (-76, -204 + k * 9)]), "#8A8078", 1.1, seed + k, 0.7, 1))
    # arm holding the watch out in front
    arm = L([(-18, -150), (-36, -146), (-58, -136), (-70, -128), (-66, -118), (-50, -124), (-30, -126), (-14, -132)])
    out.append(painted(D, arm, fur, seed + 11, sk=0.15, angle=-10, n=14, cols=fcol, inkw=1.4, inkc=inkc, hi=0.4))
    # watch chain from the waistcoat pocket
    p0 = L([(4, -112)])[0]
    p1 = L([(-60, -114)])[0]
    out.append(f'<path d="M {p0[0]:.1f} {p0[1]:.1f} Q {(p0[0] + p1[0]) / 2:.1f} {p0[1] + 34 * s:.1f} {p1[0]:.1f} {p1[1]:.1f}" fill="none" stroke="#B8862E" stroke-width="2.6" stroke-dasharray="3 1.5"/>')
    wx, wy = L([(-92, -134)])[0]
    out.append(pocket_watch(D, wx, wy, 36 * s, seed + 12, hands=(11, 56)))
    # paw over the watch
    out.append(painted(D, blob_pts(*L([(-68, -124)])[0], 9 * s, 7 * s, seed + 13, 0.1, 10), fur, seed + 13, sk=0.2, n=4, cols=fcol, inkw=1.2, inkc=inkc, hi=0.4))
    # motion swishes
    for k in range(3):
        out.append(pline(L([(70, -170 + k * 30), (100, -172 + k * 30)]), "#B8A898", 2, seed + k, 0.5, 1))
    return "".join(out)


@design("alice-in-wonderland")
def alice_in_wonderland():
    D = Doc2("sbc-al")
    out = [paper(D.nid(), "#F2EAD6", FLECK, 31)]
    out.append(blooms(32, ["#B8D4B0", "#E8B8C0", "#C8DCC0"], 7, (60, 120, 540, 520), (110, 180), (0.12, 0.2)))
    # a rose hedge arch behind: white roses being painted red
    rnd = random.Random(33)
    hedge = []
    for k in range(26):
        a = math.radians(180 + k * (180 / 25))
        hx, hy = 300 + math.cos(a) * 214, 430 + math.sin(a) * 236
        hedge.append((hx, hy))
    for k, (hx, hy) in enumerate(hedge):
        out.append(dab_crown(D, hx, hy, 40, 30, [LEAF, ("#7AAE6A", "#3A7A40", "#1A4A24")], 34 + k, n=26, size=(6, 11), inkw=0, base=False))
    for k, (hx, hy) in enumerate(hedge[1:-1:2]):
        red = k % 3 != 1
        pal_ = ROSE if red else ("#FFFFFF", "#F6F0E6", "#B8B0A0")
        out.append(rose_bloom(D, hx + rnd.uniform(-8, 8), hy + rnd.uniform(-6, 10), 13, 60 + k, pal_, rnd.uniform(0, 90)))
        if k == 4:
            out.append(taper([(hx + 4, hy + 12), (hx + 5, hy + 26), (hx + 4, hy + 30)], 3.2, 2.2, ROSE[1]))
            out.append(f'<circle cx="{hx + 4:.1f}" cy="{hy + 31:.1f}" r="2.4" fill="{ROSE[1]}"/>')
    # paint pot and brush at the foot of the hedge (the gardeners left in a hurry)
    out.append(cast(D, 474, 498, 34, 6, strength=0.4, seed=40))
    pot = [(452, 452), (494, 452), (490, 496), (456, 496)]
    out.append(painted(D, poly_pts(pot, 8, 41, 0.4), ("#C8C0B0", "#8A8478", "#4A4640"), 41, sdir=(1, 0.3), sk=0.25, angle=-90, n=8, inkw=1.4, hi=0.4))
    out.append(f'<path d="{smooth_closed(ell_pts(473, 452, 21, 5, 0, 360, 16))}" fill="{ROSE[1]}"/>')
    out.append(taper([(452, 456), (450, 470), (451, 476)], 4, 3, ROSE[1]))
    out.append(taper([(478, 448), (506, 410)], 4, 3, "#A8784A"))
    out.append(painted(D, rot([(500, 406), (512, 406), (514, 390), (506, 384), (498, 390)], 506, 398, 36), ROSE, 42, sk=0.2, n=4, inkw=1.2, hi=0.3))
    # "DRINK ME" bottle on the left
    bx, by = 128, 500
    out.append(cast(D, bx + 6, by, 30, 6, strength=0.4, seed=43))
    bottle = [(bx - 18, by - 2), (bx - 20, by - 40), (bx - 8, by - 52), (bx - 6, by - 70), (bx + 6, by - 70), (bx + 8, by - 52), (bx + 20, by - 40), (bx + 18, by - 2)]
    out.append(painted(D, bottle, ("#B8E0E8", "#6AA8B8", "#2A5A6A"), 43, sdir=(1, 0.2), sk=0.2, angle=-90, n=10, inkw=1.4, hi=0.5))
    out.append(f'<path d="M {bx - 18} {by - 26} L {bx + 18} {by - 26} L {bx + 18} {by - 4} L {bx - 18} {by - 4} Z" fill="#7A3A5A" opacity="0.55"/>')
    out.append(painted(D, rect_pts(bx - 6, by - 82, bx + 6, by - 68, 4, 44, 0.3), WOOD, 44, sk=0.2, n=4, inkw=1.2, hi=0.3))
    out.append(taper([(bx - 12, by - 38), (bx - 13, by - 14)], 3, 2, "#FFFFFF", 0.6))
    tag = rot([(bx + 8, by - 64), (bx + 52, by - 70), (bx + 54, by - 50), (bx + 10, by - 46)], bx + 30, by - 58, -8)
    out.append(painted(D, tag, ("#FFFDF4", "#F2E8D2", "#B8A88A"), 45, sk=0.1, n=6, inkw=1.2, hi=0.2))
    out.append(pline([(bx + 6, by - 66), (bx + 10, by - 58)], "#8A6A4A", 1.2, 45, 0.8, 1))
    out.append(f'<text x="{bx + 31}" y="{by - 54}" text-anchor="middle" {SERIF_IT} font-size="11" fill="#5A2A3A" transform="rotate(-8 {bx + 31} {by - 58})">Drink me</text>')
    # the rabbit
    out.append(white_rabbit(D, 330, 486, 1.0, 50))
    # lettering
    out.append(tx(300, 92, "ALICE\u2019S ADVENTURES", CINZEL, 25, "#7A2E4A", ls=6, max_w=360))
    out.append(letters(D, 300, 150, "in Wonderland", SERIF_IT, 64, "#2E5A3E", ["#3E7A50", "#1E4A2E"], 51, max_w=420,
                       shadow="#F6C8D0", soff=(0.02, 0.04), angle=-40, wob=0.5))
    for sg in (-1, 1):
        out.append(fleuron(300 + sg * 196, 527, 8, "#7A2E4A", 90 * sg))
    out.append(letters(D, 300, 538, "“We’re all mad here.”", SERIF_IT, 34, "#7A2E4A", ["#9A3E5E", "#5A1E36"], 52, max_w=380, wob=0.3))
    return finish_b(D, out, 53)


# ================================================================ 7. pride and prejudice — the letter on sprigged muslin
def sprig_muslin(D, base, sprig, leafc, seed, cell=46):
    rnd = random.Random(seed)
    m = [f'<rect width="{cell}" height="{cell}" fill="{base}"/>']
    for (fx, fy) in ((0.25, 0.25), (0.75, 0.75)):
        cx, cy = fx * cell, fy * cell
        for j in range(5):
            a = math.radians(j * 72 + fx * 90)
            m.append(f'<circle cx="{cx + math.cos(a) * 2.6:.1f}" cy="{cy + math.sin(a) * 2.6:.1f}" r="1.9" fill="{sprig}"/>')
        m.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.2" fill="#F6D86A"/>')
        m.append(f'<path d="M {cx - 3:.1f} {cy + 3:.1f} q -4 3 -7 8" stroke="{leafc}" stroke-width="1.2" fill="none"/>')
        m.append(f'<path d="{blob(cx - 8, cy + 7, 3, 1.5, seed, 0.1, 8, 40)}" fill="{leafc}"/>')
    return D.pattern(cell, cell, "".join(m), transform="rotate(-8)")


def wax_seal(D, cx, cy, r, seed, pal=("#E86A5A", "#B0262A", "#640E12"), mark="heart"):
    out = [cast(D, cx + 4, cy + 6, r * 1.15, r * 1.0, strength=0.4, seed=seed)]
    pts = blob_pts(cx, cy, r, r * 0.95, seed, 0.12, 20)
    out.append(painted(D, pts, pal, seed, sdir=(0.6, 0.8), sk=0.16, angle=-40, n=16, inkw=1.4, hi=0.45))
    out.append(f'<path d="{blob(cx, cy, r * 0.66, r * 0.64, seed + 1, 0.04, 16)}" fill="{pal[2]}" opacity="0.35"/>')
    out.append(f'<path d="{blob(cx - 1, cy - 1, r * 0.62, r * 0.6, seed + 1, 0.04, 16)}" fill="{pal[1]}"/>')
    if mark == "heart":
        hp = []
        for i in range(30):
            t = i / 30 * 2 * math.pi
            hp.append((cx + 16 * math.sin(t) ** 3 * r / 46, cy + 2 - (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) * r / 46))
        out.append(f'<path d="{smooth_closed(hp)}" fill="{pal[2]}" opacity="0.6"/>')
        out.append(f'<path d="{smooth_closed(shift(hp, -1, -1.2))}" fill="{pal[0]}" opacity="0.5"/>')
    else:
        out.append(f'<text x="{cx:.1f}" y="{cy + r * 0.25:.1f}" text-anchor="middle" {SERIF_IT} font-size="{r * 0.8:.1f}" fill="{pal[2]}" opacity="0.75">{mark}</text>')
    out.append(taper([(cx - r * 0.6, cy - r * 0.2), (cx - r * 0.35, cy - r * 0.6)], 3, 1, "#FFFFFF", 0.6))
    return "".join(out)


def forget_me_not(D, cx, cy, r, seed):
    out = []
    for j in range(5):
        a = math.radians(j * 72 + seed * 13)
        out.append(f'<path d="{blob(cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55, r * 0.5, r * 0.45, seed + j, 0.12, 8)}" fill="#7AA8E0"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.3:.1f}" fill="#FFF2A0"/><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.12:.1f}" fill="#E8A02A"/>')
    return "".join(out)


@design("pride-and-prejudice")
def pride_and_prejudice():
    D = Doc2("sbc-pr")
    out = [f'<rect width="600" height="600" fill="{sprig_muslin(D, "#DCE8EC", "#FFFFFF", "#8AAA9A", 1)}"/>']
    # soft folds in the muslin
    for k, (x0, y0, x1, y1) in enumerate(((-20, 120, 640, 40), (-20, 560, 640, 470), (60, -20, 10, 640))):
        out.append(taper([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 + 20), (x1, y1)], 60, 40, "#5A7A86", 0.08))
        out.append(taper([(x0, y0 - 24), ((x0 + x1) / 2, (y0 + y1) / 2 - 4), (x1, y1 - 24)], 30, 20, "#FFFFFF", 0.18))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFFFFF", 0.2), (0.6, "#FFFFFF", 0), (1, "#2A4A56", 0.35)], cy=0.45, r=0.75)}"/>')
    # title
    out.append(tx(300, 84, "JANE AUSTEN · 1813", CINZEL, 18, "#3A5A66", ls=5, max_w=300))
    out.append(letters(D, 300, 150, "Pride and Prejudice", SERIF_IT, 60, "#5A1E2A", ["#7A2E3A", "#3A0E16"], 2, max_w=460,
                       shadow="#FFFFFF", soff=(0.015, 0.03), angle=-40, wob=0.4))
    # the letter, folded in three, slightly askew
    cx, cy, ang = 304, 330, -3
    lp = rot(rect_pts(96, 196, 512, 466, 26, 3, 0.5), cx, cy, ang)
    out.append(f'<path d="{smooth_closed(shift(lp, 8, 10))}" fill="#1A3440" opacity="0.25"/>')
    out.append(painted(D, lp, ("#FFFEF6", "#F6EEDA", "#C8B898"), 4, sdir=(0.5, 0.8), sk=0.05, angle=-4, n=40, inkw=1.4, hi=0.2))
    letter = []
    for k in range(14):
        letter.append(f'<path d="M 104 {200 + k * 19} L 504 {200 + k * 19}" stroke="#E2D6BC" stroke-width="0.8" opacity="0.8"/>')
    for fy in (286, 376):
        letter.append(f'<rect x="96" y="{fy - 7}" width="416" height="7" fill="#A89878" opacity="0.18"/><path d="M 98 {fy} L 510 {fy}" stroke="#FFFFFF" stroke-width="1.6" opacity="0.8"/>')
    letter.append(f'<text x="484" y="232" text-anchor="end" {SERIF_IT} font-size="18" fill="#6A4A30">Longbourn</text>')
    letter.append(f'<path d="M 400 238 q 40 3 84 -1" stroke="#6A4A30" stroke-width="1.2" fill="none" opacity="0.7"/>')
    letter.append(f'<text x="300" y="300" text-anchor="middle" {SERIF_IT} font-size="{fit_size("It is a truth universally", SERIF_IT, 46, 380)}" fill="#3A2214">It is a truth universally</text>')
    letter.append(f'<text x="300" y="352" text-anchor="middle" {SERIF_IT} font-size="{fit_size("acknowledged…", SERIF_IT, 46, 380)}" fill="#3A2214">acknowledged…</text>')
    rnd = random.Random(5)
    for k in range(4):
        y = 392 + k * 18
        x = 128 if k else 150
        while x < 470 - (60 if k == 3 else 0):
            w = rnd.uniform(20, 46)
            pts = [(x + i * w / 6, y + math.sin(i * 1.9 + k) * 2.2) for i in range(7)]
            letter.append(f'<path d="{smooth_open(pts)}" stroke="#6A4A30" stroke-width="1.6" fill="none" opacity="0.55"/>')
            x += w + rnd.uniform(6, 10)
    out.append(f'<g transform="rotate({ang} {cx} {cy})">{"".join(letter)}</g>')
    # quill and a little inkwell
    out.append(quill(D, 214, 506, 66, 352, 7, w=26))
    out.append(inkwell(D, 112, 538, 50, 8))
    # wax seal with a ribbon and forget-me-nots
    out.append(taper([(380, 500), (430, 474), (470, 482), (520, 470)], 10, 9, "#E8A8B0"))
    out.append(taper([(380, 500), (430, 476), (470, 484), (520, 472)], 3, 2, "#FFFFFF", 0.4))
    out.append(taper([(440, 470), (452, 510), (446, 540)], 10, 8, "#D8909A"))
    out.append(wax_seal(D, 444, 474, 36, 9))
    for k, (fx, fy) in enumerate(((396, 470), (404, 492), (384, 488), (486, 452))):
        out.append(forget_me_not(D, fx, fy, 8, 20 + k))
    out.append(leaf_simple(D, 392, 482, 26, 6, 160, LEAF, 30))
    return finish_b(D, out, 10, INK, 0.6)


# ================================================================ 8. jane eyre — the open cage at the moorland window
def birdcage(D, cx, base, w, h, seed, door_open=True, pal=BRASS):
    out = [cast(D, cx + 8, base, w * 0.7, 7, strength=0.45, seed=seed)]
    top = base - h
    dome_h = w * 0.42
    # back bars
    for k in range(9):
        t = k / 8
        x = cx - w / 2 + w * t
        yt = top + dome_h * (1 - math.sin(math.pi * t) ** 0.6)
        out.append(f'<path d="M {x:.1f} {base - 12:.1f} L {x:.1f} {top + dome_h * 0.9:.1f} Q {x:.1f} {yt:.1f} {cx:.1f} {top:.1f}" stroke="{pal[2]}" stroke-width="1.4" fill="none" opacity="0.55"/>')
    # perch and water cup
    out.append(f'<path d="M {cx - w * 0.38:.1f} {base - h * 0.42:.1f} L {cx + w * 0.38:.1f} {base - h * 0.42:.1f}" stroke="#7A5030" stroke-width="3"/>')
    # front bars
    for k in range(9):
        t = k / 8
        x = cx - w / 2 + w * t
        if door_open and 0.55 < t < 0.9:
            continue
        yt = top + dome_h * (1 - math.sin(math.pi * t) ** 0.6)
        out.append(f'<path d="M {x:.1f} {base - 12:.1f} L {x:.1f} {top + dome_h:.1f} Q {x:.1f} {yt:.1f} {cx:.1f} {top:.1f}" stroke="{pal[1]}" stroke-width="2" fill="none"/>')
        out.append(f'<path d="M {x - 0.8:.1f} {base - 14:.1f} L {x - 0.8:.1f} {top + dome_h:.1f}" stroke="{pal[0]}" stroke-width="0.8" fill="none" opacity="0.7"/>')
    for yy in (top + dome_h, base - h * 0.62):
        out.append(f'<path d="{smooth_open(ell_pts(cx, yy, w / 2, w * 0.06, 0, 180, 16))}" stroke="{pal[1]}" stroke-width="2.4" fill="none"/>')
    # base tray
    tray = rect_pts(cx - w / 2 - 6, base - 14, cx + w / 2 + 6, base, 10, seed, 0.3)
    out.append(painted(D, tray, pal, seed, sdir=(0.5, 1), sk=0.25, angle=0, n=10, inkw=1.4, hi=0.5))
    # hook ring on top
    out.append(ink(smooth_closed(ell_pts(cx, top - 9, 7, 9, 0, 360, 14)), pal[2], 2.6, seed, 1, 1))
    out.append(f'<circle cx="{cx:.1f}" cy="{top:.1f}" r="4" fill="{pal[1]}"/>')
    if door_open:
        x0, x1 = cx + w * 0.55 - w / 2 + w * 0.06, cx + w * 0.9 - w / 2 - w * 0.02
        dy0, dy1 = base - h * 0.62, base - 14
        dw = x1 - x0
        # door swung outward toward us
        door = [(x1, dy0), (x1 + dw * 0.75, dy0 + 6), (x1 + dw * 0.75, dy1 + 6), (x1, dy1)]
        out.append(f'<path d="{pd(door)}" fill="none" stroke="{pal[1]}" stroke-width="2.4"/>')
        for k in range(1, 4):
            t = k / 4
            out.append(f'<path d="M {x1 + dw * 0.75 * t:.1f} {dy0 + 6 * t:.1f} L {x1 + dw * 0.75 * t:.1f} {dy1 + 6 * t:.1f}" stroke="{pal[1]}" stroke-width="1.8"/>')
    return "".join(out)


def songbird(D, x, y, s, seed, pal=(("#E8C8A0", "#B88A5A", "#6A4A2A")), breast="#E89A6A", flip=False, wings="up"):
    """Small songbird in flight (wings up) or perched (wings='fold'); facing right unless flip."""
    def L(pts):
        return T(pts, x, y, s, flip)
    out = []
    if wings == "up":
        for k, (pts, c) in enumerate(((([-4, -4], [-16, -30], [-6, -44], [6, -26], [8, -6]), dk(pal[1], 0.15)),
                                      (([0, -4], [10, -34], [26, -46], [22, -24], [12, -4]), pal[1]))):
            out.append(painted(D, L(pts), (pal[0], c, pal[2]), seed + k, sk=0.15, angle=-70, n=8, inkw=1.2, hi=0.3))
            for j in range(3):
                a, b = L([pts[2]])[0], L([(pts[2][0] - 4 + j * 4, pts[2][1] + 12)])[0]
                out.append(pline([a, b], pal[2], 1, seed + j, 0.5, 1))
    body = L([(-22, 2), (-10, -6), (6, -8), (18, -6), (24, -2), (18, 4), (4, 8), (-10, 6)])
    out.append(painted(D, body, pal, seed + 3, sk=0.18, angle=0, n=10, inkw=1.2, hi=0.35))
    out.append(f'<path d="{smooth_closed(L([(4, 0), (14, 0), (20, 2), (12, 7), (2, 6)]))}" fill="{breast}" opacity="0.85"/>')
    tail = L([(-20, 0), (-36, -6), (-38, 2), (-34, 6), (-20, 4)])
    out.append(painted(D, tail, pal, seed + 4, sk=0.15, n=4, inkw=1.1, hi=0.2))
    out.append(f'<path d="{pd(L([(24, -4), (31, -1.5), (24, 1)]))}" fill="#3A2A18"/>')
    ex, ey = L([(18, -3)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.6 * s:.1f}" fill="#100804"/><circle cx="{ex + 0.5 * s * (-1 if flip else 1):.1f}" cy="{ey - 0.5 * s:.1f}" r="{0.5 * s:.1f}" fill="#FFFFFF"/>')
    if wings == "fold":
        wing = L([(-12, -4), (4, -6), (12, -2), (0, 3), (-14, 3)])
        out.append(painted(D, wing, (pal[0], dk(pal[1], 0.1), pal[2]), seed + 5, sk=0.15, n=4, inkw=1.1, hi=0.3))
    return "".join(out)


@design("jane-eyre")
def jane_eyre():
    D = Doc2("sbc-je")
    # stone wall of the room, lit from the window
    out = [f'<rect width="600" height="600" fill="#6A6070"/>']
    rnd = random.Random(1)
    for row in range(14):
        y = row * 44 - 10
        off = (row % 2) * 40
        for col_ in range(-1, 8):
            x = col_ * 80 + off
            c = mix("#7A7080", rnd.choice(["#8A8090", "#5A5060", "#7A6A70"]), rnd.uniform(0.2, 0.6))
            out.append(f'<path d="{hg.org_rect(x + 2, y + 2, 76, 40, row * 31 + col_, 0.8, 16, 3)}" fill="{c}"/>')
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFD8B8", 0.35), (0.5, "#FFD8B8", 0.06), (1, "#140A1A", 0.7)], cy=0.38, r=0.7)}"/>')
    # lancet window
    ax0, ax1, sill = 176, 424, 372
    spring, apex = 196, 72
    def arch(x0, x1, sp, ap, n=16):
        cxa = (x0 + x1) / 2
        R = (x1 - x0)
        left = [(x0, sill)]
        for i in range(n + 1):
            t = i / n
            a = math.radians(180 - 60 * t)
            left.append((x1 + R * math.cos(a), sp - (sp - ap) * math.sin(math.radians(60 * t)) / math.sin(math.radians(60))))
        right = []
        for i in range(n + 1):
            t = 1 - i / n
            a = math.radians(60 * t)
            right.append((x0 + R * math.cos(a), sp - (sp - ap) * math.sin(math.radians(60 * t)) / math.sin(math.radians(60))))
        return left + right[1:] + [(x1, sill)]
    win = arch(ax0, ax1, spring, apex)
    surround = arch(ax0 - 22, ax1 + 22, spring, apex - 26)
    out.append(painted(D, surround + [(ax1 + 22, sill + 26), (ax0 - 22, sill + 26)], ("#B8AEB8", "#8A8090", "#4A4050"), 2, sdir=(0, 1), sk=0.08, angle=-90, n=40, inkw=1.6, hi=0.3))
    cid = D.clip(f'<path d="{pd(win)}"/>')
    view = [f'<rect width="600" height="600" fill="{D.lin([(0, "#3A3466"), (0.45, "#8A6A9A"), (0.75, "#E8A08A"), (1, "#FFD6A0")], 0, apex, 0, sill, "userSpaceOnUse")}"/>']
    view.append(strokes(D.nid(), pd(win), (150, apex, 450, sill), ["#A88AB0", "#5A4A7A", "#F2B89A"], 3, n=60, angle=-6, length=(40, 120), width=(3, 8), opacity=(0.1, 0.25)))
    view.append(soft_glow(D, 340, 300, 120, "#FFE0B0", 0.6))
    view.append(puff_cloud(D, 230, 190, 140, 4, ("#B8A0C8", "#8A729E", "#5A4A70"), op=0.8))
    view.append(puff_cloud(D, 380, 150, 110, 5, ("#C8A8C8", "#9A80A8", "#6A5478"), op=0.7))
    view.append(hill(D, [(150, 316), (230, 296), (320, 312), (440, 290), (460, 300)], 400, ("#9A7AA0", "#6A5078", "#3E2E50"), 6, inkw=0, n=30))
    view.append(hill(D, [(150, 336), (240, 322), (330, 340), (420, 318), (460, 326)], 400, ("#8A5A7A", "#5A3A5A", "#2E1A32"), 7, inkw=0, n=30))
    view.append(specks(8, (150, 330, 460, 372), ["#C87AA8", "#A85A8A", "#E8A0C8"], 90, (0.8, 2), (0.4, 0.9)))
    # a lone wind-bent hawthorn on the moor
    tx_, ty_ = 236, 326
    view.append(taper(catmull([(tx_, ty_), (tx_ + 4, ty_ - 14), (tx_ + 14, ty_ - 26), (tx_ + 26, ty_ - 32)], 5), 5, 2, "#2A1A2A"))
    view.append(dab_crown(D, tx_ + 26, ty_ - 36, 22, 10, [("#5A4A60", "#3A2A44", "#1E1426")], 9, n=24, size=(3, 6), inkw=0))
    # the freed bird flying out toward the evening light
    view.append(songbird(D, 352, 196, 1.2, 10))
    out.append(f'<g {cid}>{"".join(view)}</g>')
    # mullion and glazing (one casement open)
    out.append(f'<path d="{pd(win)}" fill="none" stroke="#3A3040" stroke-width="3"/>')
    out.append(f'<path d="M 300 {apex + 10} L 300 {sill}" stroke="#4A4050" stroke-width="7"/>')
    for yy in range(apex + 40, sill, 46):
        out.append(f'<path d="M {ax0} {yy} L 296 {yy}" stroke="#3A3040" stroke-width="1.6" opacity="0.8"/>')
    for k in range(5):
        out.append(f'<path d="M {ax0 + k * 24} {apex + 70} L {ax0 + k * 24} {sill}" stroke="#3A3040" stroke-width="1.3" opacity="0.5"/>')
    out.append(f'<path d="M {ax0} {apex + 110} L 296 {apex + 110}" stroke="#3A3040" stroke-width="1.3" opacity="0.5"/>')
    out.append(f'<path d="{pd([(ax0, spring + 10), (ax0, sill - 10), (296, sill - 10), (296, spring + 10)])}" fill="#C8D8E8" opacity="0.12"/>')
    # deep sill
    out.append(painted(D, rect_pts(ax0 - 44, sill, ax1 + 44, sill + 30, 20, 11, 0.4), ("#C8BEC8", "#9A90A0", "#5A5060"), 11, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.6, hi=0.35))
    # the cage, door open, on the sill
    out.append(birdcage(D, 238, sill + 8, 84, 132, 12))
    # a feather left behind
    out.append(painted(D, rot([(318, 372), (324, 360), (334, 356), (330, 368), (320, 376)], 326, 366, 0), ("#E8C8A0", "#B88A5A", "#6A4A2A"), 13, sk=0.15, n=3, inkw=1, hi=0.3))
    # lettering
    out.append(gilt(D, 300, 446, "JANE EYRE", CINZEL, 30, ls=10, max_w=300, seed=14, deboss="#140A18"))
    out.append(letters(D, 300, 494, "I am no bird; and", SERIF_IT, 40, "#FFF0E0", ["#FFFFFF", "#F2D8C8"], 15, max_w=420, shadow="#2A1E30", soff=(0.02, 0.05), angle=-40, wob=0.3))
    out.append(letters(D, 300, 536, "no net ensnares me", SERIF_IT, 40, "#FFF0E0", ["#FFFFFF", "#F2D8C8"], 16, max_w=420, shadow="#2A1E30", soff=(0.02, 0.05), angle=-40, wob=0.3))
    return finish_b(D, out, 17, "#140A18", 0.6)


# ================================================================ 9. moby-dick — the white whale sounding beside the boat
def fluke(D, cx, wl, w, seed):
    """Sperm whale tail rising from the sea, seen from behind, streaming water. wl = waterline."""
    h = w * 0.62
    def L(pts):
        return [(cx + x * w / 2, wl - y * h) for x, y in pts]
    out = []
    stock = L([(-0.26, 0), (-0.2, 0.22), (-0.14, 0.42), (-0.1, 0.58), (0.1, 0.58), (0.14, 0.42), (0.2, 0.22), (0.26, 0)])
    out.append(painted(D, stock, ("#F4F2EC", "#C8CCD0", "#6A7480"), seed, sdir=(1, 0.2), sk=0.25, angle=-90, n=20, inkw=1.6, inkc="#2A3440", hi=0.5))
    lobes = L([(0, 0.5), (-0.18, 0.52), (-0.4, 0.58), (-0.66, 0.68), (-0.88, 0.82), (-1.0, 0.98), (-0.84, 0.99), (-0.6, 0.95), (-0.34, 0.9), (-0.12, 0.88), (-0.03, 0.84),
               (0, 0.8), (0.03, 0.84), (0.12, 0.88), (0.34, 0.9), (0.6, 0.95), (0.84, 0.99), (1.0, 0.98), (0.88, 0.82), (0.66, 0.68), (0.4, 0.58), (0.18, 0.52)])
    out.append(painted(D, lobes, ("#FFFFFF", "#DADCDE", "#7A848E"), seed + 1, sdir=(0.3, 1), sk=0.2, angle=-4, n=50, cols=["#FFFFFF", "#B8BEC6", "#E8EAEC"],
                       inkw=1.8, inkc="#2A3440", hi=0.55))
    # old scars and barnacle marks
    rnd = random.Random(seed)
    for k in range(9):
        x, y = rnd.uniform(-0.8, 0.8), rnd.uniform(0.72, 0.9)
        a, b = L([(x, y)])[0], L([(x + rnd.uniform(-0.1, 0.1), y + rnd.uniform(-0.04, 0.04))])[0]
        out.append(pline([a, b], "#8A929A", 1.4, seed + k, 0.6, 1))
    for k in range(6):
        x, y = L([(rnd.uniform(-0.1, 0.1), rnd.uniform(0.1, 0.55))])[0]
        out.append(f'<path d="{blob(x, y, 4, 2.5, seed + k, 0.2, 8)}" fill="#9AA0A8" opacity="0.6"/>')
    # water streaming from the trailing edge
    for k in range(16):
        t = -0.95 + k * 0.127
        x, y = L([(t, 0.86 + 0.12 * abs(t) ** 1.4)])[0]
        L_ = rnd.uniform(30, 110) * (1 - abs(t) * 0.4)
        out.append(taper([(x, y), (x + rnd.uniform(-4, 4), y + L_ * 0.5), (x + rnd.uniform(-6, 6), y + L_)], rnd.uniform(3, 6), 0.8, "#E8F4F8", 0.65))
        for _ in range(2):
            out.append(f'<circle cx="{x + rnd.uniform(-8, 8):.1f}" cy="{y + rnd.uniform(L_ * 0.6, L_ * 1.2):.1f}" r="{rnd.uniform(1, 2.6):.1f}" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


def whaleboat(D, x, y, s, seed, ang=0, col="#2A2018"):
    """Whaleboat with five oarsmen and a harpooner standing in the bow (painted silhouettes); faces right."""
    def L(pts):
        return T(pts, x, y, s, False, ang)
    out = []
    hull = L([(-60, -6), (-40, 0), (40, 0), (64, -10), (58, 6), (30, 12), (-34, 12), (-62, 4)])
    out.append(painted(D, hull, ("#6A5A4A", "#3A2E24", "#1A120C"), seed, sk=0.2, angle=0, n=8, inkw=1.4, inkc="#100A06", hi=0.3))
    out.append(taper(L([(-58, -5), (0, 1), (62, -9)]), 2.4 * s, 2 * s, "#C8B89A", 0.8))
    for k in range(5):
        px = -40 + k * 18
        hx, hy = L([(px, -18)])[0]
        out.append(f'<path d="{smooth_closed(L([(px - 5, 0), (px - 6, -12), (px - 2, -16), (px + 4, -14), (px + 5, 0)]))}" fill="{col}"/>')
        out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{3.6 * s:.1f}" fill="{col}"/>')
        out.append(taper(L([(px + 2, -8), (px - 14, 10), (px - 26, 26)]), 2.2 * s, 2 * s, "#4A3A2A"))
    # harpooner braced in the bow, iron raised
    out.append(f'<path d="{smooth_closed(L([(48, -2), (46, -18), (50, -30), (56, -28), (58, -14), (56, -2)]))}" fill="{col}"/>')
    hx, hy = L([(53, -35)])[0]
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{3.8 * s:.1f}" fill="{col}"/>')
    out.append(taper(L([(54, -26), (60, -38), (64, -46)]), 2.4 * s, 2 * s, col))
    out.append(taper(L([(40, -32), (64, -46), (96, -64)]), 1.8 * s, 1.4 * s, "#3A2A1A"))
    out.append(f'<path d="{pd(L([(96, -64), (90, -64), (100, -70), (94, -58)]))}" fill="#2A2420"/>')
    return "".join(out)


@design("moby-dick")
def moby_dick():
    D = Doc2("sbc-md")
    out = [sky(D, [(0, "#2A3A48"), (0.45, "#5A7080"), (0.7, "#A8B8B8"), (1, "#C8D0C8")], 1, 600, ["#8A9AA8", "#3A4A58", "#C8D0D0"], 70)]
    out.append(soft_glow(D, 420, 200, 200, "#FFF2D0", 0.45))
    for k in range(9):
        out.append(taper([(440 + k * 10 - 60, 110), (420 + k * 16 - 100, 330)], 14, 30, "#FFF6E0", 0.06))
    out.append(puff_cloud(D, 140, 150, 220, 2, ("#7A8A98", "#4A5A6A", "#26323E"), op=0.85))
    out.append(puff_cloud(D, 500, 120, 180, 3, ("#8A9AA6", "#5A6A78", "#2E3A46"), op=0.7))
    wl = 372
    out.append(sea(D, wl - 20, 600, [(0, "#4A7A86"), (0.4, "#2A5462"), (1, "#14303A")], 4, ["#6A9AA4", "#1E3E48", "#8AB8BC"], 140,
                   ticks=["#A8D0D4", "#E8F4F4"]))
    # rolling swells
    rnd = random.Random(5)
    for k in range(6):
        y = wl + 10 + k * 34
        pts = [(-20 + i * 70, y + math.sin(i * 1.3 + k) * (6 + k * 2)) for i in range(11)]
        out.append(pline(pts, "#0E2A34", 2.4, 6 + k, 0.35, 1))
        out.append(pline([(px, py - 4) for px, py in pts], "#9AC8CC", 1.6, 7 + k, 0.3, 1))
    # the great fluke
    out.append(f'<path d="{blob(300, wl + 60, 200, 34, 18, 0.12, 18, -6)}" fill="#8AB8BC" opacity="0.35"/>')
    out.append(f'<path d="{blob(330, wl + 40, 120, 20, 19, 0.12, 18, -8)}" fill="#C8E2E2" opacity="0.3"/>')
    out.append(f'<path d="{blob(368, wl + 4, 150, 16, 8, 0.1, 18)}" fill="#E8F4F4" opacity="0.6"/>')
    out.append(fluke(D, 346, wl, 340, 9))
    # surge and spray where the tail leaves the water
    for k in range(40):
        a = rnd.uniform(math.pi, 2 * math.pi)
        r = rnd.uniform(20, 150)
        out.append(f'<circle cx="{368 + math.cos(a) * r:.1f}" cy="{wl + 4 + math.sin(a) * r * 0.25:.1f}" r="{rnd.uniform(1.5, 5):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    out.append(f'<path d="{smooth_closed([(230, wl + 6), (280, wl - 6), (320, wl + 2), (368, wl - 8), (420, wl + 2), (460, wl - 4), (506, wl + 8), (368, wl + 20)])}" fill="#F2FAFA" opacity="0.85"/>')
    # whaleboat riding a swell at the left
    out.append(f'<path d="{smooth_closed([(40, 470), (110, 446), (190, 452), (240, 474), (150, 486)])}" fill="#2A5462"/>')
    out.append(whaleboat(D, 128, 456, 1.05, 10, ang=-6))
    out.append(wave_lines(11, (40, 462, 250, 500), ["#E8F4F4", "#A8D0D4"], 18, (10, 22), 2, 2.4, (0.5, 0.9)))
    # gulls
    out.append(bird_v(470, 240, 9, "#2A3440"))
    out.append(bird_v(500, 266, 6, "#2A3440"))
    # lettering
    out.append(letters(D, 300, 140, "Call me Ishmael.", SERIF_IT, 72, "#FFF8EC", ["#FFFFFF", "#E2E8E8"], 12, max_w=460,
                       shadow="#14242E", soff=(0.02, 0.04), angle=-40, wob=0.5))
    out.append(tx(300, 84, "HERMAN MELVILLE · 1851", CINZEL, 17, "#DCE6E8", ls=5, max_w=330))
    out.append(scroll_banner(D, 300, 520, 270, 40, ("#F4EEDC", "#E8DCC0", "#9A8A68"), 13, tail=28, bend=6))
    out.append(tx(300, 530, "MOBY-DICK", CINZEL, 28, "#1E3A46", ls=8, max_w=240))
    return finish_b(D, out, 14, "#0A1418", 0.6)


# ================================================================ 10. the great gatsby — the green light across the bay
def coupe(D, cx, base, w, seed, fill=("#FFF2B0", "#E8C860", "#A8862A")):
    """Champagne coupe on its stem, glinting."""
    out = [cast(D, cx + 6, base, w * 0.45, 5, strength=0.5, seed=seed)]
    foot = ell_pts(cx, base - 3, w * 0.34, w * 0.07, 0, 360, 20)
    out.append(f'<path d="{smooth_closed(foot)}" fill="#C8D8E8" opacity="0.8" stroke="#E8F2FF" stroke-width="1.2"/>')
    stem_top = base - w * 0.78
    out.append(taper([(cx, base - 4), (cx, (base + stem_top) / 2), (cx, stem_top)], 4, 3, "#D8E6F2", 0.9))
    out.append(taper([(cx - 1, base - 6), (cx - 1, stem_top + 4)], 1.2, 1, "#FFFFFF", 0.9))
    bowl_y = stem_top - w * 0.2
    bowl = ell_pts(cx, bowl_y, w * 0.5, w * 0.26, 0, 180, 20)
    liquid = [(cx - w * 0.47, bowl_y + 2)] + ell_pts(cx, bowl_y, w * 0.47, w * 0.23, 5, 175, 18)[::-1] + [(cx + w * 0.47, bowl_y + 2)]
    out.append(f'<path d="{smooth_closed(bowl)}" fill="#C8D8E8" opacity="0.45"/>')
    out.append(painted(D, liquid, fill, seed, sdir=(1, 0.3), sk=0.2, angle=0, n=8, inkw=0, hi=0.5))
    rnd = random.Random(seed)
    for _ in range(9):
        out.append(f'<circle cx="{cx + rnd.uniform(-w * 0.3, w * 0.3):.1f}" cy="{bowl_y + rnd.uniform(3, w * 0.18):.1f}" r="{rnd.uniform(0.8, 1.8):.1f}" fill="#FFFFFF" opacity="0.85"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, bowl_y, w * 0.5, w * 0.07, 0, 360, 24))}" fill="#FFF6D0" opacity="0.55" stroke="#F2F8FF" stroke-width="1.6"/>')
    out.append(ink(smooth_open(bowl), "#E8F2FF", 1.6, seed, 1, 0.9))
    out.append(taper([(cx - w * 0.38, bowl_y + 4), (cx - w * 0.3, bowl_y + w * 0.16)], 3, 1, "#FFFFFF", 0.85))
    return "".join(out)


def deco_corner(D, x, y, sx, sy, g):
    """Stepped art-deco corner ornament in gilt (sx, sy = direction into the frame)."""
    out = []
    for k, L in enumerate((54, 40, 26)):
        o = 8 + k * 8
        out.append(f'<path d="M {x + sx * o:.1f} {y + sy * (o + L):.1f} L {x + sx * o:.1f} {y + sy * o:.1f} L {x + sx * (o + L):.1f} {y + sy * o:.1f}" fill="none" stroke="{g}" stroke-width="{2.2 - k * 0.4:.1f}"/>')
    out.append(f'<path d="M {x + sx * 36:.1f} {y + sy * 36:.1f} l {sx * 6:.1f} 0 l 0 {sy * 6:.1f} l {-sx * 6:.1f} 0 Z" fill="{g}"/>')
    return "".join(out)


@design("the-great-gatsby")
def great_gatsby():
    D = Doc2("sbc-gg")
    hor = 330
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#060C22"), (0.5, "#14244A"), (0.55, "#1E3460"), (1, "#0A1630")])}"/>']
    out.append(stars_field(1, (0, 0, 600, hor - 30), 120))
    gx, gy = 236, 326
    # deco sunburst from the green light
    g = gilt_fill(D, 0, 600)
    for k in range(25):
        a = math.radians(-172 + k * 6.6)
        out.append(f'<path d="M {gx:.1f} {gy:.1f} L {gx + math.cos(a) * 700:.1f} {gy + math.sin(a) * 700:.1f}" stroke="#D9B85A" stroke-width="1.2" opacity="{0.12 if k % 2 else 0.2}"/>')
    out.append(soft_glow(D, gx, gy, 120, "#5AF0A0", 0.28))
    # far shore: East Egg, a house with lit windows, the dock reaching out
    shore = [(-20, hor - 4), (60, hor - 12), (140, hor - 10), (210, hor - 4), (330, hor - 8), (430, hor - 20), (520, hor - 16), (620, hor - 8)]
    out.append(f'<path d="{smooth_open(shore)} L 620 {hor + 8} L -20 {hor + 8} Z" fill="#081026"/>')
    for k in range(20):
        x = -10 + k * 32
        out.append(f'<path d="{blob(x, hor - 16 - (k % 3) * 4, 22, 14, k, 0.2, 10)}" fill="#0A1430"/>')
    hx = 380
    out.append(f'<path d="{pd([(hx - 50, hor - 12), (hx - 50, hor - 46), (hx - 30, hor - 62), (hx + 30, hor - 62), (hx + 50, hor - 46), (hx + 50, hor - 12)])}" fill="#101C3E"/>')
    out.append(f'<rect x="{hx - 70}" y="{hor - 38}" width="24" height="26" fill="#101C3E"/><rect x="{hx + 46}" y="{hor - 38}" width="24" height="26" fill="#101C3E"/>')
    rnd = random.Random(2)
    for row in range(2):
        for k in range(7):
            if rnd.random() < 0.7:
                wx_ = hx - 42 + k * 12
                wy_ = hor - 52 + row * 18
                out.append(f'<rect x="{wx_}" y="{wy_}" width="6" height="9" fill="#FFD27A"/>')
                out.append(soft_glow(D, wx_ + 3, wy_ + 4, 12, "#FFC860", 0.35))
                out.append(f'<rect x="{wx_ + 1}" y="{hor + 6 + row * 10}" width="4" height="{14 + rnd.uniform(0, 14):.0f}" fill="#FFD27A" opacity="0.25"/>')
    # the dock and its green light
    out.append(f'<path d="M 300 {hor - 2} L {gx - 6} {gy + 4} L {gx - 6} {gy + 7} L 300 {hor + 2} Z" fill="#1A2A50"/>')
    for k in range(6):
        px = 300 - k * 12
        out.append(f'<path d="M {px} {hor + 1 - k * 0.5:.1f} l 0 8" stroke="#1A2A50" stroke-width="2"/>')
    out.append(f'<path d="M {gx} {gy + 4} L {gx} {gy - 12}" stroke="#2A3A60" stroke-width="2.4"/>')
    out.append(soft_glow(D, gx, gy - 14, 46, "#6AFFAA", 0.75))
    out.append(soft_glow(D, gx, gy - 14, 14, "#E8FFF0", 0.9))
    out.append(f'<circle cx="{gx}" cy="{gy - 14}" r="3.6" fill="#F0FFF4"/>')
    # the bay
    out.append(f'<rect x="0" y="{hor + 6}" width="600" height="{600 - hor}" fill="{D.lin([(0, "#14284E"), (1, "#081430")])}"/>')
    out.append(strokes(D.nid(), f"M 0 {hor + 6} L 600 {hor + 6} L 600 600 L 0 600 Z", (-60, hor + 6, 600, 600), ["#2A4A7A", "#0A1838", "#3A5A8A"], 3, n=120,
                       angle=0, length=(40, 160), width=(1.5, 4), opacity=(0.2, 0.45), curve=0.05))
    # the green light's broken reflection
    for k in range(18):
        y = hor + 12 + k * 8
        w = 8 + k * 2.2 + rnd.uniform(-3, 3)
        out.append(f'<path d="M {gx - w / 2 + rnd.uniform(-4, 4):.1f} {y} l {w:.1f} 0" stroke="#5AF0A0" stroke-width="{2.4 + k * 0.08:.1f}" stroke-linecap="round" opacity="{0.7 - k * 0.032:.2f}"/>')
    out.append(wave_lines(4, (0, hor + 30, 600, 470), ["#4A6A9A", "#2A4A7A"], 40, (14, 30), 1.6, 2, (0.4, 0.7)))
    # stone balustrade of the terrace in the foreground
    by_ = 476
    for k in range(9):
        bx = 22 + k * 70
        bal = [(bx - 12, 600), (bx - 9, 572), (bx - 16, 548), (bx - 8, 516), (bx - 10, by_ + 22), (bx + 10, by_ + 22), (bx + 8, 516), (bx + 16, 548), (bx + 9, 572), (bx + 12, 600)]
        out.append(painted(D, bal, ("#8A9AC0", "#4A5A84", "#1E2848"), 5 + k, sdir=(1, 0.2), sk=0.3, angle=-90, n=8, inkw=1.2, inkc="#0A1028", hi=0.45))
    out.append(painted(D, rect_pts(-10, by_, 610, by_ + 24, 30, 6, 0.3), ("#A8B4D8", "#5A6A94", "#26304E"), 6, sdir=(0, 1), sk=0.3, angle=0, n=30, inkw=1.4, inkc="#0A1028", hi=0.5))
    out.append(f'<path d="M -10 {by_} L 610 {by_}" stroke="#C8D8FF" stroke-width="2" opacity="0.5"/>')
    out.append(coupe(D, 466, by_ + 2, 74, 7))
    out.append(soft_glow(D, 466, by_ - 70, 30, "#FFF2C0", 0.3))
    # deco frame in gilt
    out.append(f'<rect x="20" y="20" width="560" height="560" fill="none" stroke="{g}" stroke-width="2.4"/>')
    out.append(f'<rect x="28" y="28" width="544" height="544" fill="none" stroke="{g}" stroke-width="1"/>')
    for (x, y, sx, sy) in ((28, 28, 1, 1), (572, 28, -1, 1), (28, 572, 1, -1), (572, 572, -1, -1)):
        out.append(deco_corner(D, x, y, sx, sy, g))
    # lettering
    out.append(gilt(D, 300, 104, "THE GREAT GATSBY", JOS, 40, ls=8, max_w=430, seed=8))
    out.append(f'<path d="M 170 120 L 430 120" stroke="{g}" stroke-width="1.4"/><path d="M 292 120 l 8 -6 l 8 6 l -8 6 Z" fill="{g}"/>')
    out.append(tx(300, 156, "So we beat on, boats against the current,", SERIF_IT, 22, "#E8E2C8", max_w=420))
    out.append(tx(300, 184, "borne back ceaselessly into the past.", SERIF_IT, 22, "#E8E2C8", max_w=420))
    return finish_b(D, out, 9, "#000000", 0.5)


# ================================================================ 11. the odyssey — a black-figure amphora on the wine-dark sea
def amphora_profile(cx):
    prof = [(140, 64), (150, 54), (180, 46), (212, 48), (236, 100), (270, 134), (320, 148), (370, 140), (410, 116), (446, 76), (466, 44), (472, 54), (488, 70)]
    pts = catmull([(cx + w, y) for y, w in prof], 5)
    left = [(2 * cx - x, y) for x, y in pts]
    return pts + left[::-1]


def black_ship(cx, cy, s, col="#1A0E08", inc="#D8784A"):
    """Black-figure galley with a square sail, oars and an eye on the prow; faces right."""
    def L(pts):
        return T(pts, cx, cy, s)
    out = []
    hull = L([(-80, -4), (-92, -26), (-86, -30), (-74, -10), (60, -10), (82, -14), (100, -6), (88, -2), (70, 6), (-60, 6)])
    out.append(f'<path d="{smooth_closed(hull)}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed(L([(82, -2), (104, 2), (82, 6)]))}" fill="{col}"/>')
    # mast, yard, sail with incised panels
    out.append(f'<path d="M {L([(0, -10)])[0][0]:.1f} {L([(0, -10)])[0][1]:.1f} L {L([(0, -86)])[0][0]:.1f} {L([(0, -86)])[0][1]:.1f}" stroke="{col}" stroke-width="{3 * s:.1f}"/>')
    sail = L([(-40, -80), (40, -80), (42, -56), (36, -32), (0, -28), (-36, -32), (-42, -56)])
    out.append(f'<path d="{smooth_closed(sail)}" fill="{col}"/>')
    for k in (1, 2, 3):
        y = -80 + k * 13
        out.append(pline(L([(-38, y), (0, y + 4), (38, y)]), inc, 1.0, k, 0.9, 1))
    for k in (-1, 1):
        out.append(pline(L([(k * 20, -79), (k * 22, -56), (k * 19, -31)]), inc, 0.9, k + 5, 0.8, 1))
    out.append(f'<path d="M {L([(-46, -82)])[0][0]:.1f} {L([(-46, -82)])[0][1]:.1f} L {L([(46, -82)])[0][0]:.1f} {L([(46, -82)])[0][1]:.1f}" stroke="{col}" stroke-width="{3 * s:.1f}"/>')
    for sg in (-1, 1):
        out.append(f'<path d="M {L([(sg * 46, -82)])[0][0]:.1f} {L([(sg * 46, -82)])[0][1]:.1f} L {L([(sg * 76, -10)])[0][0]:.1f} {L([(sg * 76, -10)])[0][1]:.1f}" stroke="{col}" stroke-width="1"/>')
    # oarsmen and oars
    for k in range(9):
        x = -60 + k * 14
        hx, hy = L([(x, -16)])[0]
        out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{3.4 * s:.1f}" fill="{col}"/>')
        a, b = L([(x, -6)])[0], L([(x - 10, 22)])[0]
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{col}" stroke-width="{1.8 * s:.1f}"/>')
    # helmsman's steering oar, incised hull lines and prow eye
    a, b = L([(-74, -14)])[0], L([(-96, 16)])[0]
    out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{col}" stroke-width="{3 * s:.1f}"/>')
    out.append(pline(L([(-70, -2), (0, -1), (70, -4)]), inc, 1.1, 1, 0.9, 1))
    ex, ey = L([(74, -6)])[0]
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{5 * s:.1f}" ry="{3 * s:.1f}" fill="none" stroke="{inc}" stroke-width="1.2"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.4 * s:.1f}" fill="{inc}"/>')
    return "".join(out)


def dolphin(x, y, s, col="#1A0E08", inc="#D8784A", flip=False, ang=0):
    def L(pts):
        return T(pts, x, y, s, flip, ang)
    body = L([(-30, 2), (-14, -8), (8, -10), (24, -6), (34, -2), (40, 0), (34, 2), (20, 6), (0, 8), (-20, 6), (-34, 10), (-40, 4), (-36, -2)])
    out = [f'<path d="{smooth_closed(body)}" fill="{col}"/>',
           f'<path d="{smooth_closed(L([(0, -9), (6, -18), (10, -9)]))}" fill="{col}"/>',
           f'<path d="{smooth_closed(L([(4, 6), (0, 14), (12, 7)]))}" fill="{col}"/>']
    ex, ey = L([(26, -3)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.4 * s:.1f}" fill="{inc}"/>')
    out.append(pline(L([(-26, 2), (0, 2), (24, 0)]), inc, 1, 2, 0.9, 1))
    return "".join(out)


def meander(x0, x1, y, h, col, sw=2.6):
    """Greek key band."""
    out = []
    u = h / 3
    x = x0
    d = []
    while x + 4 * u <= x1:
        d.append(f"M {x:.1f} {y + h:.1f} L {x:.1f} {y:.1f} L {x + 3 * u:.1f} {y:.1f} L {x + 3 * u:.1f} {y + 2 * u:.1f} L {x + u:.1f} {y + 2 * u:.1f} L {x + u:.1f} {y + u:.1f} L {x + 2 * u:.1f} {y + u:.1f}")
        d.append(f"M {x:.1f} {y + h:.1f} L {x + 4 * u:.1f} {y + h:.1f}")
        x += 4 * u
    out.append(f'<path d="{" ".join(d)}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linejoin="miter"/>')
    return "".join(out)


@design("the-odyssey")
def the_odyssey():
    D = Doc2("sbc-od")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#2A1236"), (0.6, "#3A1A40"), (1, "#16243E")])}"/>']
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 600 L 0 600 Z", (-60, 0, 600, 600), ["#4A2456", "#1A0C24", "#2A3A5A"], 1, n=160,
                       angle=-4, length=(60, 200), width=(3, 9), opacity=(0.12, 0.3), curve=0.08))
    # stylised waves (running-dog scroll) along the bottom, in gold
    g = gilt_fill(D, 520, 600)
    wave = []
    for k in range(-1, 14):
        x = k * 46
        wave.append(f"M {x} 586 C {x + 10} 586 {x + 18} 576 {x + 18} 566 C {x + 18} 556 {x + 30} 552 {x + 36} 558 C {x + 42} 564 {x + 36} 574 {x + 28} 572 C {x + 22} 570 {x + 24} 562 {x + 30} 562")
    out.append(f'<path d="{" ".join(wave)}" fill="none" stroke="{g}" stroke-width="3"/>')
    out.append(f'<path d="M 0 592 L 600 592" stroke="{g}" stroke-width="2"/>')
    cx = 300
    out.append(soft_glow(D, cx, 330, 260, "#E8784A", 0.22))
    out.append(cast(D, cx + 10, 494, 120, 12, color="#000000", strength=0.6, seed=2))
    prof = amphora_profile(cx)
    vd = smooth_closed(prof)
    # handles (behind the body edges)
    for sg in (-1, 1):
        hpts = [(cx + sg * 44, 178), (cx + sg * 84, 168), (cx + sg * 104, 186), (cx + sg * 102, 218), (cx + sg * 92, 246)]
        out.append(taper(catmull(hpts, 6), 15, 13, "#1A0E08"))
        out.append(taper(catmull([(x - sg * 2, y - 2) for x, y in hpts], 6), 4, 3, "#5A3020", 0.8))
    out.append(f'<path d="{vd}" fill="#D8743E"/>')
    cid = D.clip(f'<path d="{vd}"/>')
    inner = [f'<rect width="600" height="600" fill="{D.lin([(0, "#F0A060"), (1, "#C05A2A")])}"/>']
    inner.append(strokes(D.nid(), vd, (150, 130, 450, 500), ["#F2A86A", "#B8562A", "#E08A4E"], 3, n=90, angle=-90, length=(20, 60), width=(2, 5), opacity=(0.15, 0.35)))
    col = "#1A0E08"
    # black glaze on neck, lip and foot
    inner.append(f'<rect x="0" y="130" width="600" height="30" fill="{col}"/>')
    inner.append(f'<rect x="0" y="440" width="600" height="80" fill="{col}"/>')
    # neck: palmette-lotus chain
    for k in range(5):
        px = cx - 32 + k * 16
        inner.append(f'<path d="M {px} 206 C {px - 7} 196 {px - 5} 180 {px} 172 C {px + 5} 180 {px + 7} 196 {px} 206 Z" fill="{col}"/>')
        inner.append(f'<circle cx="{px + 8}" cy="200" r="2.4" fill="{col}"/>')
    # shoulder: tongues
    for k in range(24):
        a = -0.95 + k * 0.083
        x0_ = cx + math.sin(a) * 100
        inner.append(f'<path d="M {x0_:.1f} 226 Q {x0_ + math.sin(a) * 10:.1f} 248 {x0_ + math.sin(a) * 14 + 0:.1f} 252" stroke="{col}" stroke-width="7" stroke-linecap="round" fill="none"/>')
    inner.append(f'<path d="M 150 258 L 450 258" stroke="{col}" stroke-width="3"/>')
    # main frieze: the ship on the sea with dolphins
    inner.append(black_ship(cx - 8, 368, 1.05))
    inner.append(dolphin(cx - 104, 404, 0.9, ang=-14))
    inner.append(dolphin(cx + 102, 400, 0.9, ang=12))
    for k in range(13):
        x = 156 + k * 24
        inner.append(f'<path d="M {x} 396 q 6 -6 12 0 t 12 0" stroke="{col}" stroke-width="2" fill="none"/>')
    inner.append(meander(160, 444, 414, 16, col, 2.6))
    inner.append(f'<path d="M 150 410 L 450 410 M 150 434 L 450 434" stroke="{col}" stroke-width="2.4"/>')
    # rays rising from the foot (reserved in clay on the black)
    for k in range(13):
        x = cx - 72 + k * 12
        inner.append(f'<path d="M {x - 5} 448 L {x} 438 L {x + 5} 448 Z" fill="#D8743E"/>')
    inner.append(f'<path d="M 0 470 L 600 470" stroke="#D8743E" stroke-width="1.6"/>')
    # rounded volume: dark sides, a vertical sheen
    inner.append(f'<rect width="600" height="600" fill="{D.lin([(0, "#000000", 0.55), (0.32, "#000000", 0), (0.62, "#000000", 0), (1, "#000000", 0.62)], 150, 0, 450, 0, "userSpaceOnUse")}"/>')
    inner.append(taper([(196, 270), (182, 330), (190, 396)], 16, 10, "#FFE8C8", 0.22))
    inner.append(taper([(184, 300), (180, 340)], 4, 2, "#FFFFFF", 0.35))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(vd, "#0E0604", 2, 4, 2, 0.8))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, 141, 64, 9, 0, 360, 24))}" fill="#1A0E08" stroke="#5A3020" stroke-width="1.4"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, 142, 52, 6, 0, 360, 24))}" fill="#000000"/>')
    # lettering
    out.append(gilt(D, 300, 100, "THE ODYSSEY", CINZEL, 50, ls=10, max_w=440, seed=5, deboss="#0A0410"))
    out.append(gilt(D, 300, 534, "HOMER · THE WINE-DARK SEA", CINZEL, 19, ls=5, max_w=400, seed=6, deboss="#0A0410", wear=False))
    return finish_b(D, out, 7, "#000000", 0.5)


# ================================================================ 12. don quixote — windmills of La Mancha at sundown
def windmill(D, x, base, h, seed, sail_ang=20, lit=(1, 0)):
    """Whitewashed La Mancha windmill: tapering round tower, conical cap, four lattice sails."""
    out = []
    w0, w1 = h * 0.42, h * 0.34
    tower = [(x - w0 / 2, base), (x - w1 / 2, base - h), (x + w1 / 2, base - h), (x + w0 / 2, base)]
    out.append(painted(D, poly_pts(tower, 10, seed, 0.4), ("#FFF2E0", "#F2D8C0", "#A88A90"), seed, sdir=(-lit[0], 0.1), sk=0.3, angle=-90, n=14, inkw=1.4, hi=0.6, hik=0.15))
    out.append(f'<path d="{pd([(x + w0 * 0.1, base), (x + w1 * 0.1, base - h), (x + w1 / 2, base - h), (x + w0 / 2, base)])}" fill="#8A6A9A" opacity="0.35"/>')
    out.append(f'<path d="{hg.org_rect(x - 5, base - h * 0.32, 10, h * 0.32, seed, 0.3, 6, 2)}" fill="#3A5A9A"/>')
    out.append(f'<rect x="{x - 3:.1f}" y="{base - h * 0.72:.1f}" width="6" height="8" fill="#2A2A3A"/>')
    cap = [(x - w1 / 2 - 4, base - h + 2), (x - w1 * 0.2, base - h - h * 0.26), (x + w1 * 0.2, base - h - h * 0.26), (x + w1 / 2 + 4, base - h + 2)]
    out.append(painted(D, cap, ("#8A7A70", "#5A4A48", "#2A2028"), seed + 1, sdir=(-lit[0], 0.3), sk=0.25, angle=-60, n=8, inkw=1.4, hi=0.4))
    hx, hy = x - w1 * 0.1, base - h - h * 0.08
    R = h * 0.78
    for k in range(4):
        a = math.radians(sail_ang + k * 90)
        ex, ey = hx + math.cos(a) * R, hy + math.sin(a) * R
        out.append(f'<path d="M {hx:.1f} {hy:.1f} L {ex:.1f} {ey:.1f}" stroke="#4A3428" stroke-width="2.6"/>')
        nx, ny = -math.sin(a), math.cos(a)
        p0 = (hx + math.cos(a) * R * 0.25, hy + math.sin(a) * R * 0.25)
        frame = [p0, (ex, ey), (ex + nx * R * 0.2, ey + ny * R * 0.2), (p0[0] + nx * R * 0.2, p0[1] + ny * R * 0.2)]
        out.append(f'<path d="{pd(frame)}" fill="#F2E2C8" opacity="0.35" stroke="#4A3428" stroke-width="1.3"/>')
        for j in range(1, 6):
            t = 0.25 + 0.75 * j / 6
            a1 = (hx + math.cos(a) * R * t, hy + math.sin(a) * R * t)
            out.append(f'<path d="M {a1[0]:.1f} {a1[1]:.1f} l {nx * R * 0.2:.1f} {ny * R * 0.2:.1f}" stroke="#4A3428" stroke-width="1"/>')
        out.append(f'<path d="M {p0[0] + nx * R * 0.1:.1f} {p0[1] + ny * R * 0.1:.1f} L {ex + nx * R * 0.1:.1f} {ey + ny * R * 0.1:.1f}" stroke="#4A3428" stroke-width="0.9"/>')
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="3.4" fill="#3A2A20"/>')
    return "".join(out)


def knight_and_squire(x, base, s, col="#3A1A2A", rim="#FFB060"):
    """Don Quixote on lean Rocinante with lance and shield, Sancho on his donkey behind; silhouettes facing right."""
    out = []

    def horse(hx, hb, k, donkey=False):
        def L(pts):
            return T(pts, hx, hb, k)
        parts = []
        body = L([(-36, -46), (-20, -52), (10, -52), (30, -50), (36, -42), (30, -32), (10, -30), (-18, -30), (-34, -34)])
        parts.append(f'<path d="{smooth_closed(body)}" fill="{col}"/>')
        if donkey:
            neck = L([(26, -48), (36, -58), (44, -62), (52, -52), (46, -44), (34, -38)])
            head = L([(42, -64), (50, -66), (62, -54), (64, -46), (56, -44), (46, -52)])
            ears = [L([(44, -62), (40, -84), (47, -64)]), L([(47, -63), (50, -84), (52, -62)])]
        else:
            neck = L([(24, -50), (36, -66), (46, -76), (54, -70), (42, -52), (34, -38)])
            head = L([(44, -76), (52, -80), (58, -74), (70, -56), (64, -52), (56, -60), (46, -64)])
            ears = [L([(48, -78), (46, -88), (52, -79)])]
        parts.append(f'<path d="{smooth_closed(neck)}" fill="{col}"/>')
        parts.append(f'<path d="{smooth_closed(head)}" fill="{col}"/>')
        for e in ears:
            parts.append(f'<path d="{pd(e)}" fill="{col}"/>')
        for leg in ([(28, -34), (31, -16), (31, 0)], [(22, -34), (17, -16), (12, -1)], [(-28, -36), (-33, -18), (-30, 0)], [(-20, -34), (-18, -16), (-23, -1)]):
            parts.append(taper(L(leg), 5.4 * k, 3.2 * k, col))
            fx, fy = L([leg[-1]])[0]
            parts.append(f'<path d="M {fx - 3 * k:.1f} {fy + 1:.1f} l {6 * k:.1f} 0 l -1 {-4 * k:.1f} l {-4 * k:.1f} 0 Z" fill="{col}"/>')
        parts.append(taper(L([(-34, -44), (-42, -36), (-44, -18)]), 5 * k, 2 * k, col))
        parts.append(ink(smooth_open(L([(-30, -50), (0, -54), (28, -52), (44, -74)])), rim, 1.4, 1, 1, 0.55))
        return "".join(parts)
    # Sancho on the donkey, a little behind
    sx, sb, k2 = x - 74, base + 4, s * 0.82
    out.append(horse(sx, sb, k2, donkey=True))

    def L2(pts):
        return T(pts, sx, sb, k2)
    out.append(f'<path d="{smooth_closed(L2([(-14, -50), (-18, -66), (-12, -80), (4, -82), (14, -70), (12, -52)]))}" fill="{col}"/>')
    hx_, hy_ = L2([(-2, -90)])[0]
    out.append(f'<circle cx="{hx_:.1f}" cy="{hy_:.1f}" r="{8 * k2:.1f}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed(L2([(-16, -94), (12, -94), (6, -100), (-8, -100)]))}" fill="{col}"/>')
    out.append(taper(L2([(0, -54), (8, -44), (6, -34)]), 6 * k2, 4 * k2, col))
    # Don Quixote on Rocinante
    out.append(horse(x, base, s))

    def L(pts):
        return T(pts, x, base, s)
    out.append(taper(L([(2, -52), (8, -40), (6, -26)]), 6 * s, 4 * s, col))
    out.append(f'<path d="{smooth_closed(L([(-6, -52), (8, -52), (10, -76), (6, -96), (-2, -98), (-8, -80)]))}" fill="{col}"/>')
    hx, hy = L([(2, -104)])[0]
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{6 * s:.1f}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed(L([(-8, -106), (-6, -114), (2, -117), (10, -114), (12, -106), (16, -104), (-12, -104)]))}" fill="{col}"/>')   # the basin helmet
    out.append(f'<path d="{pd(L([(6, -100), (10, -92), (8, -100)]))}" fill="{col}"/>')
    out.append(f'<path d="{blob(*L([(-8, -78)])[0], 9 * s, 13 * s, 3, 0.05, 12)}" fill="{col}"/>')                              # shield
    out.append(taper(L([(4, -84), (14, -76), (18, -70)]), 4 * s, 3 * s, col))
    out.append(taper(L([(-14, -40), (18, -72), (110, -168)]), 3.2 * s, 2 * s, col))                                           # the lance
    out.append(f'<path d="{pd(L([(110, -168), (104, -158), (116, -176), (114, -162)]))}" fill="{col}"/>')
    out.append(ink(smooth_open(L([(-6, -80), (-2, -96), (2, -110), (10, -114)])), rim, 1.4, 2, 1, 0.6))
    return "".join(out)


@design("don-quixote")
def don_quixote():
    D = Doc2("sbc-dq")
    out = [sky(D, [(0, "#5A4A8A"), (0.35, "#C87A9A"), (0.62, "#F6A86A"), (0.8, "#FFD68A"), (1, "#FFE8B0")], 1, 600, ["#F2B8A0", "#8A6AA8", "#FFE2B0"], 80)]
    sx_, sy_ = 168, 352
    out.append(soft_glow(D, sx_, sy_, 230, "#FFE6A0", 0.75))
    out.append(f'<circle cx="{sx_}" cy="{sy_}" r="44" fill="#FFF2C8"/>')
    out.append(puff_cloud(D, 430, 230, 170, 2, ("#FFD8B8", "#E8A0A8", "#9A6A9A"), op=0.75))
    out.append(puff_cloud(D, 110, 214, 120, 3, ("#FFD0B0", "#E098A8", "#8A6098"), op=0.6))
    for k in range(5):
        out.append(taper([(sx_ - 60 + k * 10, 250 - k * 6), (sx_ + 220, 226 + k * 8)], 3, 1, "#FFF0D0", 0.25))
    # far ridge and the windmill hill
    out.append(hill(D, [(-20, 382), (120, 374), (240, 380), (330, 366), (620, 372)], 640, ("#C89AA8", "#A87A90", "#7A5A78"), 4, inkw=0, n=30))
    out.append(hill(D, [(240, 400), (330, 352), (420, 334), (520, 340), (620, 360)], 640, ("#E8B87A", "#C08A58", "#7A5A48"), 5, inkw=1.4, n=50))
    out.append(windmill(D, 352, 360, 64, 6, 28))
    out.append(windmill(D, 430, 342, 76, 7, 8))
    out.append(windmill(D, 510, 348, 68, 8, 40))
    # the plain of La Mancha, wheat stubble catching the light
    out.append(hill(D, [(-20, 410), (100, 400), (200, 404), (300, 420), (420, 412), (620, 418)], 640, ("#FFD88A", "#E2A852", "#9A6A38"), 9, inkw=1.4, n=90, lit="#FFF0C0"))
    out.append(grass(10, (0, 440, 600, 600), ["#C8862E", "#F2C46A", "#A8682A"], 220, (8, 20)))
    # long shadows of the riders
    out.append(f'<path d="{smooth_closed([(170, 412), (300, 432), (470, 452), (480, 460), (300, 444), (150, 418)])}" fill="#7A4A48" opacity="0.3"/>')
    out.append(knight_and_squire(192, 410, 1.08))
    # lettering
    out.append(letters(D, 300, 140, "Don Quixote", DMS, 84, "#3A1A3E", ["#5A2A5A", "#2A0E2A"], 11, max_w=440,
                       shadow="#FFD8A8", soff=(0.02, 0.035), angle=-50, wob=0.4))
    out.append(tx(300, 190, "MIGUEL DE CERVANTES · 1605", CINZEL, 17, "#3A1A3E", ls=5, max_w=380))
    out.append(letters(D, 300, 526, "“En un lugar de la Mancha…”", SERIF_IT, 34, "#4A1E2A", ["#6A2E3A", "#3A1018"], 12, max_w=420,
                       shadow="#FFE2A0", soff=(0.02, 0.04), angle=-40, wob=0.3))
    return finish_b(D, out, 13)


# ================================================================ 13. anne of green gables — the farmhouse in blossom time
def blossom_tree(D, x, base, h, seed, pals=(("#FFFFFF", "#FBE2EA", "#E8A8BC"), ("#FFF6F8", "#F6C8D6", "#D88AA4"))):
    out = [taper(catmull([(x, base), (x - 4, base - h * 0.35), (x + 2, base - h * 0.55)], 5), 12, 6, "#5A3A2A")]
    out.append(taper(catmull([(x - 2, base - h * 0.4), (x - 22, base - h * 0.6), (x - 30, base - h * 0.7)], 5), 6, 2, "#5A3A2A"))
    out.append(taper(catmull([(x + 1, base - h * 0.45), (x + 20, base - h * 0.62), (x + 30, base - h * 0.72)], 5), 6, 2, "#5A3A2A"))
    out.append(dab_crown(D, x, base - h * 0.72, h * 0.42, h * 0.32, list(pals), seed, n=int(h * 1.6), size=(4, 8), inkw=0))
    rnd = random.Random(seed)
    for _ in range(int(h * 0.3)):
        out.append(f'<circle cx="{x + rnd.uniform(-h * 0.4, h * 0.4):.1f}" cy="{base - h * 0.72 + rnd.uniform(-h * 0.3, h * 0.3):.1f}" r="1.4" fill="#E8789A" opacity="0.7"/>')
    return "".join(out)


def farmhouse(D, x, base, seed, wall=("#FFFFFF", "#F2EEE4", "#A8A49A"), roof=("#6A9A78", "#3E6A50", "#1E3A2A")):
    """Green Gables: white clapboard farmhouse with green-trimmed gables, a front cross gable and a red chimney."""
    out = []
    w, h = 150, 62
    l, r = x - w / 2, x + w / 2
    # back ell (kitchen wing)
    out.append(painted(D, rect_pts(r - 10, base - 44, r + 52, base, 14, seed, 0.4), wall, seed, sdir=(1, 0.2), sk=0.12, angle=0, n=10, inkw=1.2, hi=0.2))
    out.append(painted(D, [(r - 14, base - 42), (r + 20, base - 66), (r + 56, base - 42)], roof, seed + 1, sk=0.15, angle=0, n=8, inkw=1.2, hi=0.3))
    # main block
    out.append(painted(D, rect_pts(l, base - h, r, base, 16, seed + 2, 0.4), wall, seed + 2, sdir=(1, 0.2), sk=0.1, angle=0, n=20, inkw=1.4, hi=0.25))
    for k in range(1, 9):
        out.append(f'<path d="M {l + 2:.1f} {base - h + k * 7:.1f} L {r - 2:.1f} {base - h + k * 7:.1f}" stroke="#C8C4B8" stroke-width="0.8"/>')
    rf = [(l - 8, base - h + 2), (l + 10, base - h - 34), (r - 10, base - h - 34), (r + 8, base - h + 2)]
    out.append(painted(D, rf, roof, seed + 3, sdir=(0.3, 1), sk=0.15, angle=0, n=20, inkw=1.4, hi=0.3))
    # red brick chimneys
    for cx_ in (l + 30, r - 26):
        out.append(painted(D, rect_pts(cx_ - 7, base - h - 52, cx_ + 7, base - h - 26, 6, seed + int(cx_), 0.3), ("#E88A6A", "#B8442A", "#6A1E10"), seed + int(cx_), sk=0.2, angle=-90, n=4, inkw=1.2, hi=0.3))
    # front cross gable with Anne's window
    gx = x + 6
    gab = [(gx - 34, base - h + 2), (gx - 34, base - h - 18), (gx, base - h - 54), (gx + 34, base - h - 18), (gx + 34, base - h + 2)]
    out.append(painted(D, gab, wall, seed + 4, sdir=(1, 0.2), sk=0.1, angle=0, n=10, inkw=1.3, hi=0.2))
    out.append(pline([(gx - 40, base - h - 14), (gx, base - h - 60), (gx + 40, base - h - 14)], roof[1], 5, seed, 1, 1))
    out.append(pline([(gx - 40, base - h - 14), (gx, base - h - 60), (gx + 40, base - h - 14)], roof[0], 1.6, seed + 1, 0.8, 1))
    # windows with green shutters
    def window(wx, wy, ww=13, wh=17):
        o = [f'<rect x="{wx - ww / 2 - 6:.1f}" y="{wy:.1f}" width="5" height="{wh}" fill="{roof[1]}"/><rect x="{wx + ww / 2 + 1:.1f}" y="{wy:.1f}" width="5" height="{wh}" fill="{roof[1]}"/>',
             f'<rect x="{wx - ww / 2:.1f}" y="{wy:.1f}" width="{ww}" height="{wh}" fill="#3A4A5A" stroke="#FFFFFF" stroke-width="1.6"/>',
             f'<path d="M {wx:.1f} {wy:.1f} L {wx:.1f} {wy + wh:.1f} M {wx - ww / 2:.1f} {wy + wh / 2:.1f} L {wx + ww / 2:.1f} {wy + wh / 2:.1f}" stroke="#FFFFFF" stroke-width="1"/>',
             f'<path d="M {wx - ww / 2 + 2:.1f} {wy + 2:.1f} l 4 0 l -4 6 Z" fill="#A8C8E0" opacity="0.6"/>']
        return "".join(o)
    out.append(window(gx, base - h - 34, 11, 14))
    for wx in (l + 22, l + 52, r - 50, r - 22):
        out.append(window(wx, base - h + 10))
    out.append(window(r + 22, base - 34, 11, 14))
    out.append(f'<path d="{hg.org_rect(gx - 9, base - 30, 18, 30, seed, 0.3, 8, 1)}" fill="{roof[1]}"/>')
    out.append(f'<path d="M {gx - 14} {base - 32} L {gx + 14} {base - 32}" stroke="#FFFFFF" stroke-width="3"/>')
    return "".join(out)


def straw_hat(D, cx, cy, R, seed, ang=-10):
    """Straw hat with a wreath of buttercups and wild roses round the crown."""
    out = [cast(D, cx + 6, cy + R * 0.3, R * 1.1, R * 0.3, strength=0.35, seed=seed)]
    brim = rot(ell_pts(cx, cy, R, R * 0.36, 0, 360, 30)[:-1], cx, cy, ang)
    out.append(painted(D, brim, ("#FCE6A6", "#E8C070", "#A8803A"), seed, sdir=(0.4, 1), sk=0.15, angle=ang, n=40, cols=["#F6D88A", "#C89A4A", "#FFF0C0"], inkw=1.6, hi=0.4))
    for k in range(4):
        out.append(f'<path d="{smooth_closed(rot(ell_pts(cx, cy, R * (0.9 - k * 0.12), R * (0.32 - k * 0.04), 0, 360, 26)[:-1], cx, cy, ang))}" fill="none" stroke="#B8904A" stroke-width="1" opacity="0.6"/>')
    crown = rot([(cx - R * 0.45, cy), (cx - R * 0.42, cy - R * 0.42), (cx - R * 0.2, cy - R * 0.56), (cx + R * 0.2, cy - R * 0.56), (cx + R * 0.42, cy - R * 0.42), (cx + R * 0.45, cy)], cx, cy, ang)
    out.append(painted(D, crown, ("#FCE6A6", "#E8C070", "#A8803A"), seed + 1, sdir=(1, 0.4), sk=0.2, angle=-80, n=20, cols=["#F6D88A", "#C89A4A", "#FFF0C0"], inkw=1.6, hi=0.4))
    rnd = random.Random(seed)
    band = rot([(cx - R * 0.44 + R * 0.88 * t, cy - R * 0.08 - math.sin(math.pi * t) * R * 0.06) for t in [i / 8 for i in range(9)]], cx, cy, ang)
    for k, (bx, by) in enumerate(band):
        if k % 2:
            out.append(rose_bloom(D, bx, by, 9, seed + k, ("#FFC8D0", "#F08AA0", "#A84A62"), rnd.uniform(0, 90)))
        else:
            for j in range(5):
                a = math.radians(j * 72 + k * 10)
                out.append(f'<path d="{blob(bx + math.cos(a) * 4, by + math.sin(a) * 4, 4.5, 3.5, seed + k + j, 0.1, 8, math.degrees(a))}" fill="#F6D02A"/>')
            out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="2" fill="#C8902A"/>')
        out.append(leaf_simple(D, bx + 4, by + 2, 12, 3.5, rnd.uniform(-30, 30), LEAF, seed + 40 + k, vein=False, inkw=0.8))
    return "".join(out)


@design("anne-of-green-gables")
def anne_of_green_gables():
    D = Doc2("sbc-ag")
    out = [paper(D.nid(), "#F6EEDC", FLECK, 1)]
    vcx, vcy = 300, 326
    vig = blob_pts(vcx, vcy, 236, 160, 2, 0.06, 28)
    vd = smooth_closed(vig)
    cid = D.clip(f'<path d="{vd}"/>')
    sc = [f'<rect width="600" height="600" fill="{D.lin([(0, "#A8D0EA"), (0.5, "#E2F0F0"), (1, "#FFF6E0")], 0, 160, 0, 340, "userSpaceOnUse")}"/>']
    sc.append(puff_cloud(D, 190, 214, 130, 3, ("#FFFFFF", "#FAF6F0", "#D8E0E8")))
    # spruce wood and a glimpse of the pond
    sc.append(hill(D, [(40, 300), (180, 290), (300, 296), (450, 284), (560, 294)], 640, ("#B8D0A0", "#8AB078", "#5A8058"), 4, inkw=0, n=30))
    from paint import conifer
    rnd = random.Random(5)
    for k in range(20):
        x = 60 + k * 26 + rnd.uniform(-8, 8)
        c_ = mix("#3E6A50", "#7AA088", rnd.uniform(0, 0.4))
        sc.append(conifer(x, 304, rnd.uniform(36, 60), c_, k, width=0.34, light=lt(c_, 0.25)))
    sc.append(f'<path d="{blob(140, 316, 80, 9, 6, 0.1, 14)}" fill="#7AB0D0"/>')
    sc.append(f'<path d="M 90 314 L 180 314" stroke="#FFFFFF" stroke-width="1.6" opacity="0.7"/>')
    sc.append(hill(D, [(40, 330), (200, 318), (320, 326), (460, 316), (570, 326)], 640, ("#C8E0A0", "#98C070", "#5A8A48"), 7, inkw=1, n=60))
    sc.append(f'<g transform="translate(330 346) scale(1.22) translate(-330 -346)">{farmhouse(D, 330, 346, 8)}</g>')
    sc.append(blossom_tree(D, 160, 372, 130, 9))
    sc.append(blossom_tree(D, 496, 362, 112, 10))
    # the red lane and the white fence
    cl = catmull([(232, 500), (268, 450), (312, 404), (334, 370), (340, 350)], 8)
    wl_ = [110 * (1 - i / (len(cl) - 1)) ** 1.2 + 8 for i in range(len(cl))]
    Lp, Rp = [], []
    for i, (px, py) in enumerate(cl):
        q0, q1 = cl[max(i - 1, 0)], cl[min(i + 1, len(cl) - 1)]
        dx_, dy_ = q1[0] - q0[0], q1[1] - q0[1]
        ln = math.hypot(dx_, dy_) or 1
        Lp.append((px - dy_ / ln * wl_[i] / 2, py + dx_ / ln * wl_[i] / 2))
        Rp.append((px + dy_ / ln * wl_[i] / 2, py - dx_ / ln * wl_[i] / 2))
    sc.append(painted(D, Lp + Rp[::-1], ("#E8906A", "#C8603A", "#8A3A1E"), 11, sk=0.08, angle=-55, n=50, inkw=0, hi=0.25))
    sc.append(pline(Lp, "#9A4A2A", 1.2, 11, 0.5, 1))
    sc.append(pline(Rp, "#9A4A2A", 1.2, 12, 0.5, 1))
    for k in range(13):
        t = k / 12
        i = int(t * (len(Rp) - 1) * 0.92)
        px, py = Rp[i][0] + 12 * (1 - t), Rp[i][1] - 2
        ph = 30 * (1 - t) + 8
        sc.append(f'<path d="{hg.org_rect(px - 2.5 * (1 - t * 0.6), py - ph, 5 * (1 - t * 0.6), ph, k, 0.2, 6, 1)}" fill="#FFFFFF" stroke="#A8A49A" stroke-width="0.8"/>')
    rail = [(Rp[int(t * (len(Rp) - 1) * 0.92)][0] + 12 * (1 - t), Rp[int(t * (len(Rp) - 1) * 0.92)][1] - 2 - (30 * (1 - t) + 8) * 0.7) for t in [k / 12 for k in range(13)]]
    sc.append(pline(rail, "#FFFFFF", 2.6, 13, 1, 1))
    sc.append(pline([(x, y + 8 * (1 - (x - rail[0][0]) / 200)) for x, y in rail], "#FFFFFF", 2, 14, 0.9, 1))
    sc.append(grass(14, (40, 380, 600, 500), ["#5A9A48", "#8AC060", "#3E7A38"], 200, (6, 16)))
    for k in range(70):
        x, y = rnd.uniform(360, 560), rnd.uniform(380, 480)
        sc.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(2, 3.6):.1f}" fill="#F6D02A"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    # feathered vignette edge
    for k, (x, y) in enumerate(vig):
        out.append(f'<path d="{blob(x, y, 26, 14, 30 + k, 0.3, 10, rnd.uniform(0, 180))}" fill="#F6EEDC" opacity="0.6"/>')
    # Anne's flower-wreathed hat hung on the gatepost
    out.append(painted(D, rect_pts(104, 368, 124, 470, 12, 15, 0.4), ("#FFFFFF", "#ECE8E0", "#A8A49A"), 15, sk=0.2, angle=-90, n=8, inkw=1.4, hi=0.3))
    out.append(f'<path d="M 104 368 L 114 358 L 124 368 Z" fill="#ECE8E0" stroke="#8A867C" stroke-width="1.2"/>')
    out.append(straw_hat(D, 122, 392, 50, 16, ang=-14))
    # lettering
    out.append(tx(300, 84, "L. M. MONTGOMERY · 1908", CINZEL, 17, "#3E6A50", ls=5, max_w=360))
    out.append(letters(D, 300, 142, "Anne of Green Gables", SERIF_IT, 54, "#2E6A44", ["#3E8A54", "#1E4A2E"], 17, max_w=470,
                       shadow="#F6C8D2", soff=(0.02, 0.035), angle=-40, wob=0.4))
    out.append(tx(300, 504, "“…tomorrow is a new day", SERIF_IT, 31, "#7A3A30", max_w=440))
    out.append(tx(300, 538, "with no mistakes in it yet.”", SERIF_IT, 31, "#7A3A30", max_w=440))
    return finish_b(D, out, 18)


# ================================================================ 14. the secret garden — the door in the wall, the robin and the key
def robin(D, x, y, s, seed, flip=False):
    """European robin, plump, orange-red face and breast, tail cocked; facing right; (x, y) = feet."""
    def L(pts):
        return T(pts, x, y, s, flip)
    out = [cast(D, x, y + 1, 22 * s, 4 * s, strength=0.35, seed=seed)]
    brown = ("#B89A72", "#7A5E40", "#3E2A18")
    tail = L([(-24, -22), (-44, -42), (-50, -38), (-46, -32), (-30, -14)])
    out.append(painted(D, tail, brown, seed, sk=0.15, angle=-130, n=6, inkw=1.2, hi=0.3))
    for leg in ([(2, -8), (0, 0)], [(10, -8), (12, 0)]):
        out.append(taper(L(leg), 2.2 * s, 1.6 * s, "#5A3A2A"))
        fx, fy = L([leg[1]])[0]
        out.append(f'<path d="M {fx - 5 * s:.1f} {fy:.1f} L {fx + 6 * s:.1f} {fy:.1f}" stroke="#5A3A2A" stroke-width="{1.4 * s:.1f}" stroke-linecap="round"/>')
    body = L([(-30, -20), (-24, -34), (-8, -44), (10, -46), (24, -42), (32, -32), (30, -18), (18, -8), (-4, -5), (-22, -10)])
    out.append(painted(D, body, brown, seed + 1, sdir=(0.6, 0.6), sk=0.15, angle=-20, n=20, inkw=1.4, hi=0.35))
    head = blob_pts(*L([(22, -50)])[0], 14 * s, 13 * s, seed + 2, 0.05, 14)
    out.append(painted(D, head, brown, seed + 2, sk=0.15, angle=-20, n=8, inkw=1.4, hi=0.35))
    breast = L([(36, -52), (34, -40), (30, -26), (20, -12), (8, -14), (12, -28), (18, -42), (26, -56), (34, -58)])
    out.append(painted(D, breast, ("#FFB070", "#E8682A", "#A83A10"), seed + 3, sdir=(-0.3, 0.8), sk=0.15, angle=-70, n=16, inkw=0, hi=0.45))
    out.append(f'<path d="{smooth_closed(L([(20, -10), (-2, -6), (-10, -12), (6, -16)]))}" fill="#F2E8D8"/>')
    out.append(pline(L([(26, -58), (30, -44), (24, -28), (14, -14)]), "#C8C0B0", 1.4, seed, 0.6, 1))
    wing = L([(-22, -30), (-4, -40), (12, -36), (8, -22), (-12, -16), (-26, -20)])
    out.append(painted(D, wing, ("#A88A62", "#6A5034", "#36240E"), seed + 4, sk=0.15, angle=-10, n=8, inkw=1.2, hi=0.3))
    for k in range(3):
        out.append(pline(L([(-18 + k * 8, -30 + k * 2), (-4 + k * 8, -20 + k)]), "#3E2A18", 1, seed + k, 0.6, 1))
    out.append(f'<path d="{pd(L([(34, -54), (44, -52), (34, -49)]))}" fill="#2A1A10"/>')
    ex, ey = L([(27, -55)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{3.2 * s:.1f}" fill="#100804"/><circle cx="{ex + 1 * s * (-1 if flip else 1):.1f}" cy="{ey - 1.2 * s:.1f}" r="{1 * s:.1f}" fill="#FFFFFF"/>')
    return "".join(out)


def old_key(D, x, y, L_, ang, seed, pal=("#8A8A94", "#4A4A54", "#1A1A22"), rust="#8A4A2A"):
    """Old iron key: trefoil bow, long shank, toothed bit."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    out = [taper([(x + 4, y + 6), (x + ux * L_ + 4, y + uy * L_ + 6)], 10, 10, "#1A0E06", 0.3)]
    bx, by = x - ux * 18, y - uy * 18
    for k in range(3):
        aa = a + math.radians(180 + (k - 1) * 70)
        cx, cy = bx + math.cos(aa) * 13, by + math.sin(aa) * 13
        out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="11" fill="none" stroke="{pal[1]}" stroke-width="5.5"/>')
        out.append(f'<circle cx="{cx - 1:.1f}" cy="{cy - 1:.1f}" r="11" fill="none" stroke="{pal[0]}" stroke-width="1.4" opacity="0.7"/>')
    out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="7" fill="{pal[1]}"/>')
    out.append(taper([(x - ux * 6, y - uy * 6), (x + ux * L_, y + uy * L_)], 8, 7, pal[1]))
    out.append(taper([(x - ux * 4 - nx * 2, y - uy * 4 - ny * 2), (x + ux * L_ - nx * 2, y + uy * L_ - ny * 2)], 2, 2, pal[0], 0.8))
    for k in (0.1, 0.16):
        px, py = x + ux * L_ * k, y + uy * L_ * k
        out.append(f'<path d="M {px - nx * 6:.1f} {py - ny * 6:.1f} L {px + nx * 6:.1f} {py + ny * 6:.1f}" stroke="{pal[1]}" stroke-width="4"/>')
    tx_, ty_ = x + ux * L_, y + uy * L_
    bit = [(tx_ - ux * 22, ty_ - uy * 22), (tx_ - ux * 22 + nx * 18, ty_ - uy * 22 + ny * 18), (tx_ - ux * 14 + nx * 18, ty_ - uy * 14 + ny * 18),
           (tx_ - ux * 14 + nx * 10, ty_ - uy * 14 + ny * 10), (tx_ - ux * 8 + nx * 10, ty_ - uy * 8 + ny * 10), (tx_ - ux * 8 + nx * 18, ty_ - uy * 8 + ny * 18),
           (tx_ + nx * 18, ty_ + ny * 18), (tx_, ty_)]
    out.append(f'<path d="{pd(bit)}" fill="{pal[1]}" stroke="{pal[2]}" stroke-width="1.2"/>')
    rnd = random.Random(seed)
    for _ in range(14):
        t = rnd.uniform(0, 1)
        out.append(f'<circle cx="{x + ux * L_ * t + rnd.uniform(-3, 3):.1f}" cy="{y + uy * L_ * t + rnd.uniform(-3, 3):.1f}" r="{rnd.uniform(1, 2.2):.1f}" fill="{rust}" opacity="0.6"/>')
    return "".join(out)


def ivy(D, pts_list, seed, n=60, pals=(("#7AA86A", "#3E7040", "#1A3A22"), ("#9AC07A", "#5A8A48", "#2A4A26"))):
    rnd = random.Random(seed)
    out = []
    for pts in pts_list:
        path = catmull(pts, 8)
        out.append(pline(path, "#4A5A2A", 1.6, seed, 0.8, 1))
        for i in range(0, len(path), 2):
            x, y = path[i]
            for _ in range(2):
                lx, ly = x + rnd.uniform(-10, 10), y + rnd.uniform(-6, 8)
                pal = rnd.choice(pals)
                r = rnd.uniform(5, 9)
                lp = [(lx, ly - r), (lx + r * 0.9, ly - r * 0.2), (lx + r * 0.5, ly + r * 0.7), (lx, ly + r * 0.4), (lx - r * 0.5, ly + r * 0.7), (lx - r * 0.9, ly - r * 0.2)]
                lp = rot(lp, lx, ly, rnd.uniform(-40, 40))
                out.append(f'<path d="{smooth_closed(lp)}" fill="{rnd.choice(pal)}"/>')
                out.append(f'<path d="M {lx:.1f} {ly + r * 0.3:.1f} L {lx:.1f} {ly - r * 0.6:.1f}" stroke="{pal[2]}" stroke-width="0.8" opacity="0.6"/>')
    return "".join(out)


@design("the-secret-garden")
def the_secret_garden():
    D = Doc2("sbc-sg")
    out = [sky(D, [(0, "#CDE4EE"), (1, "#F6F2E2")], 1, 240, ["#FFFFFF", "#B8D8E8"], 30)]
    wt = 186
    # brick wall
    out.append(f'<rect x="0" y="{wt}" width="600" height="{420 - wt + 20}" fill="#B86A4A"/>')
    rnd = random.Random(2)
    for row in range(int((440 - wt) / 16) + 1):
        y = wt + 12 + row * 16
        off = (row % 2) * 18
        for col_ in range(-1, 18):
            x = col_ * 36 + off
            c = mix("#B8684A", rnd.choice(["#D88A62", "#8A4A32", "#C07050", "#A85A40"]), rnd.uniform(0.2, 0.7))
            out.append(f'<path d="{hg.org_rect(x + 1.5, y + 1.5, 33, 13, row * 40 + col_, 0.6, 12, 2)}" fill="{c}"/>')
    out.append(f'<rect x="0" y="{wt}" width="600" height="14" fill="#C8B8A0"/><rect x="0" y="{wt + 12}" width="600" height="4" fill="#5A3A2A" opacity="0.4"/>')
    out.append(f'<rect x="0" y="{wt}" width="600" height="{440 - wt}" fill="{D.lin([(0, "#2A140A", 0.1), (1, "#2A140A", 0.45)])}"/>')
    # the hidden door in the wall
    dx0, dx1, dtop, dbot = 236, 364, 262, 432
    R = (dx1 - dx0) / 2
    door = [(dx0, dbot)] + ell_pts((dx0 + dx1) / 2, dtop + R, R, R, 180, 360, 16) + [(dx1, dbot)]
    arch_out = [(dx0 - 12, dbot)] + ell_pts((dx0 + dx1) / 2, dtop + R, R + 12, R + 12, 180, 360, 16) + [(dx1 + 12, dbot)]
    out.append(painted(D, arch_out, ("#D8C8B0", "#B8A890", "#6A5A48"), 3, sk=0.1, angle=-90, n=20, inkw=1.4, hi=0.3))
    out.append(painted(D, door, ("#8AA07A", "#5A7050", "#2A3A26"), 4, sdir=(1, 0.3), sk=0.12, angle=-90, n=40, inkw=1.6, hi=0.25))
    for k in range(1, 5):
        x = dx0 + k * (dx1 - dx0) / 5
        out.append(pline([(x, dtop + 10 if abs(x - 300) < 30 else dtop + 30), (x + 1, dbot)], "#2A3A26", 1.6, k, 0.6, 1))
    for yy in (dtop + 56, dbot - 40):
        out.append(f'<path d="M {dx0 + 4} {yy} L {dx0 + 70} {yy}" stroke="#2A2420" stroke-width="5" stroke-linecap="round"/>')
    out.append(f'<circle cx="{dx1 - 22}" cy="{(dtop + dbot) / 2 + 20}" r="8" fill="none" stroke="#2A2420" stroke-width="3"/>')
    out.append(f'<path d="M {dx1 - 22} {(dtop + dbot) / 2 + 36} m -3 0 a 3 3 0 1 1 6 0 l -1 8 l -4 0 Z" fill="#1A1410"/>')
    # ivy curtains, one swept aside from the door
    out.append(ivy(D, [[(10, wt + 4), (20, 300), (12, 380), (24, 440)], [(70, wt + 4), (84, 290), (70, 360)], [(130, wt + 4), (124, 260), (140, 330)],
                       [(204, wt + 4), (226, 280), (214, 380), (230, 430)], [(254, wt + 4), (270, 262), (250, 330)], [(330, wt + 4), (352, 250)],
                       [(400, wt + 4), (380, 290), (392, 400), (380, 440)], [(460, wt + 4), (474, 280), (462, 350)], [(530, wt + 4), (520, 300), (536, 400)],
                       [(590, wt + 4), (580, 320), (592, 430)]], 5, n=60))
    out.append(ivy(D, [[(-10, wt + 6), (150, wt + 10), (300, wt + 4), (450, wt + 10), (610, wt + 4)]], 6))
    # climbing rose by the door
    for k, (x, y) in enumerate(((396, 300), (412, 340), (388, 372), (200, 320), (190, 360))):
        out.append(rose_bloom(D, x, y, 11, 40 + k, ("#FFC0C8", "#E8708A", "#A83A52"), k * 40))
    # the soil of the bed with first green shoots
    out.append(hill(D, [(-20, 432), (150, 426), (300, 434), (450, 426), (620, 432)], 640, ("#8A6A4A", "#5A3E28", "#2E1E12"), 7, inkw=1.2, n=80))
    out.append(specks(8, (0, 440, 600, 600), ["#3A2614", "#9A7A5A", "#2A1A0E"], 160, (0.8, 2.4), (0.4, 0.8)))
    for k in range(16):
        x = 30 + k * 36 + rnd.uniform(-10, 10)
        y = 446 + rnd.uniform(0, 30)
        out.append(taper([(x, y), (x + rnd.uniform(-3, 3), y - 18)], 3, 1, "#7AB060"))
        out.append(taper([(x + 2, y), (x + 8, y - 14)], 2.6, 1, "#5A9048"))
        if k % 3 == 0:
            out.append(f'<path d="{blob(x, y - 22, 3.4, 5, k, 0.1, 8)}" fill="#FFFFFF" stroke="#8AA0A0" stroke-width="0.8"/>')
        elif k % 3 == 1:
            out.append(f'<path d="{blob(x, y - 22, 3.6, 6, k, 0.1, 8)}" fill="#9A6AC8"/>')
    # the key, just turned up, and the robin who showed the way
    out.append(old_key(D, 340, 478, 92, -14, 9))
    out.append(f'<path d="{blob(390, 484, 40, 8, 10, 0.2, 12)}" fill="#3A2614" opacity="0.5"/>')
    out.append(robin(D, 232, 486, 1.3, 11))
    # lettering
    out.append(tx(300, 84, "FRANCES HODGSON BURNETT · 1911", CINZEL, 16, "#3E6A50", ls=3, max_w=380))
    out.append(letters(D, 300, 148, "The Secret Garden", SERIF_IT, 60, "#2E5A3E", ["#3E7A50", "#1E4A2E"], 12, max_w=450,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, wob=0.4))
    out.append(letters(D, 300, 538, "“Might I have a bit of earth?”", SERIF_IT, 32, "#FFF2D8", ["#FFFFFF", "#F2E2C0"], 13, max_w=420,
                       shadow="#1A0E06", soff=(0.02, 0.05), angle=-40, wob=0.3))
    return finish_b(D, out, 14)


# ================================================================ 15. little women — the library card, borrowed by four sisters
def marbled(D, seed, cols=("#6A7E9A", "#B07A72", "#D8B878", "#EFE4CE", "#8A9A86", "#EFE4CE"), base="#E8DCC0"):
    rnd = random.Random(seed)
    out = [f'<rect width="600" height="600" fill="{base}"/>']
    y = -20
    k = 0
    while y < 640:
        h = rnd.uniform(8, 18)
        c = cols[k % len(cols)]
        pts = [(-20 + i * 30, y + math.sin(i * 0.9 + k * 0.7) * 8 + math.sin(i * 0.31 + k) * 6) for i in range(23)]
        out.append(taper(pts, h, h * rnd.uniform(0.6, 1.2), c, rnd.uniform(0.55, 0.8)))
        y += h * 0.8
        k += 1
    # combed "nonpareil" peaks
    for i in range(30):
        x = i * 21
        out.append(f'<path d="M {x} -10 C {x + 8} 150 {x - 8} 300 {x + 6} 450 S {x - 4} 600 {x} 620" stroke="#F2E6CC" stroke-width="1.2" fill="none" opacity="0.35"/>')
    # stone "eyes"
    for _ in range(18):
        cx, cy, r = rnd.uniform(0, 600), rnd.uniform(0, 600), rnd.uniform(8, 18)
        c = rnd.choice(cols)
        out.append(f'<path d="{blob(cx, cy, r, r * 0.7, rnd.randint(0, 999), 0.2, 12)}" fill="{c}"/>')
        out.append(f'<path d="{blob(cx, cy, r * 0.6, r * 0.4, rnd.randint(0, 999), 0.2, 10)}" fill="#F2E6CC" opacity="0.7"/>')
        out.append(f'<path d="{blob(cx, cy, r, r * 0.7, rnd.randint(0, 999), 0.2, 12)}" fill="none" stroke="#1A1A2A" stroke-width="0.8" opacity="0.4"/>')
    return "".join(out)


def holly_leaf(D, x, y, L, ang, seed, pal=("#5A9A5A", "#2E6A3A", "#143A1E")):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    pts = []
    n = 5
    for i in range(n + 1):
        t = i / n
        w = L * 0.3 * math.sin(math.pi * min(0.97, 0.06 + t * 0.94)) ** 0.8
        px, py = x + ux * L * t, y + uy * L * t
        pts.append((px + nx * w * (1.25 if 0 < i < n else 1), py + ny * w * (1.25 if 0 < i < n else 1)))
        if i < n:
            t2 = (i + 0.5) / n
            w2 = L * 0.3 * math.sin(math.pi * (0.06 + t2 * 0.94)) ** 0.8 * 0.72
            pts.append((x + ux * L * t2 + nx * w2, y + uy * L * t2 + ny * w2))
    back = []
    for i in range(n + 1):
        t = 1 - i / n
        w = L * 0.3 * math.sin(math.pi * min(0.97, 0.06 + t * 0.94)) ** 0.8
        px, py = x + ux * L * t, y + uy * L * t
        back.append((px - nx * w * (1.25 if 0 < i < n else 1), py - ny * w * (1.25 if 0 < i < n else 1)))
        if i < n:
            t2 = t - 0.5 / n
            w2 = L * 0.3 * math.sin(math.pi * (0.06 + t2 * 0.94)) ** 0.8 * 0.72
            back.append((x + ux * L * t2 - nx * w2, y + uy * L * t2 - ny * w2))
    out = [painted(D, pts + back, pal, seed, sdir=(nx, ny), sk=0.15, angle=ang + 30, n=10, inkw=1.2, hi=0.45)]
    out.append(pline([(x, y), (x + ux * L * 0.95, y + uy * L * 0.95)], "#A8D08A", 1.4, seed, 0.7, 1))
    return "".join(out)


def holly_sprig(D, x, y, ang, seed):
    out = [taper([(x - 30, y + 30), (x, y), (x + 20, y - 26)], 4, 2, "#5A3A22")]
    for k, (dx, dy, a, L) in enumerate(((0, 0, ang - 150, 62), (0, 0, ang - 60, 58), (10, -10, ang + 10, 54), (-14, 14, ang + 110, 50), (6, -14, ang - 110, 46))):
        out.append(holly_leaf(D, x + dx, y + dy, L, a, seed + k))
    for k, (dx, dy) in enumerate(((-6, 4), (6, 8), (0, -6), (12, -2), (-2, 14))):
        bx, by = x + dx, y + dy
        out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="7.5" fill="#C8202A" stroke="#5A0A0E" stroke-width="1.2"/>')
        out.append(f'<circle cx="{bx + 1.5:.1f}" cy="{by + 1.5:.1f}" r="4.5" fill="#8A0E16" opacity="0.5"/>')
        out.append(f'<circle cx="{bx - 2.4:.1f}" cy="{by - 2.4:.1f}" r="2" fill="#FFFFFF" opacity="0.85"/>')
    return "".join(out)


def posy(D, x, y, ang, seed):
    """Four flowers tied with a ribbon (one for each sister): rose, daisy, lavender sprig, forget-me-nots."""
    out = []
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    stems = []
    for k, da in enumerate((-16, -5, 6, 16)):
        b = math.radians(ang + 180 + da)
        L = 92 + (k % 2) * 12
        tip = (x + math.cos(b) * L, y + math.sin(b) * L)
        stems.append(tip)
        out.append(taper([(x + ux * 46, y + uy * 46), (x, y), tip], 3, 2, "#4E7A3E"))
    out.append(leaf_simple(D, x - ux * 20, y - uy * 20, 34, 8, ang + 160, LEAF, seed, inkw=0.9))
    out.append(leaf_simple(D, x - ux * 26, y - uy * 26, 30, 7, ang + 200, LEAF, seed + 1, inkw=0.9))
    out.append(rose_bloom(D, *stems[0], 21, seed + 2, ROSE, 20))
    dx, dy = stems[1]
    for j in range(14):
        aa = math.radians(j * 360 / 14)
        out.append(f'<path d="{blob(dx + math.cos(aa) * 9, dy + math.sin(aa) * 9, 7.5, 2.6, seed + j, 0.1, 8, math.degrees(aa))}" fill="#FFFFFF" stroke="#C8C0B0" stroke-width="0.6"/>')
    out.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="5" fill="#F2C02A"/>')
    lx, ly = stems[2]
    for j in range(8):
        out.append(f'<path d="{blob(lx - math.cos(a) * j * 4.5, ly - math.sin(a) * j * 4.5, 3.4, 2.4, seed + 20 + j, 0.15, 8)}" fill="{["#9A7AC8", "#7A5AA8"][j % 2]}"/>')
    fx, fy = stems[3]
    for j in range(4):
        out.append(forget_me_not(D, fx + (j % 2) * 8 - 4, fy + (j // 2) * 8 - 4, 6, seed + 30 + j))
    # ribbon bow
    for sg in (-1, 1):
        out.append(painted(D, blob_pts(x + uy * sg * 10, y - ux * sg * 10, 11, 6, seed + 40 + sg, 0.1, 10, ang + 90 + sg * 30), OXBLOOD, seed + 40 + sg, sk=0.2, n=4, inkw=1.2, hi=0.4))
        out.append(taper([(x, y), (x + ux * 20 + uy * sg * 12, y + uy * 20 - ux * sg * 12), (x + ux * 34 + uy * sg * 8, y + uy * 34 - ux * sg * 8)], 5, 3, OXBLOOD[1]))
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{OXBLOOD[2]}"/>')
    return "".join(out)


@design("little-women")
def little_women():
    D = Doc2("sbc-lw")
    out = [marbled(D, 1)]
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#000000", 0), (0.7, "#000000", 0.1), (1, "#000000", 0.4)], r=0.75)}"/>')
    ang = -3
    cx, cy = 300, 300
    # library card sliding out of its pocket
    card = rot(rect_pts(170, 96, 430, 470, 30, 2, 0.3), cx, cy, ang)
    out.append(f'<path d="{smooth_closed(shift(card, 6, 8))}" fill="#000000" opacity="0.3"/>')
    out.append(painted(D, card, ("#FFFDF2", "#F6EEDA", "#C8B898"), 3, sdir=(0.5, 0.8), sk=0.04, angle=0, n=20, inkw=1.2, hi=0.1))
    c = []
    c.append(f'<rect x="170" y="96" width="260" height="10" fill="#B83A3A" opacity="0.85"/>')
    c.append(f'<text x="186" y="132" {MONO} font-size="16" fill="#3A3A4A">813.4  ALC</text>')
    c.append(f'<text x="414" y="132" text-anchor="end" {MONO} font-size="16" fill="#3A3A4A">1868</text>')
    c.append(f'<text x="186" y="154" {MONO} font-size="16" fill="#3A3A4A">Alcott, Louisa May</text>')
    c.append(f'<text x="300" y="196" text-anchor="middle" {DMS} font-size="{fit_size("Little Women", DMS, 44, 230)}" fill="#2A2A3A">Little Women</text>')
    c.append(f'<path d="M 176 212 L 424 212 M 176 238 L 424 238" stroke="#B83A3A" stroke-width="1.4"/>')
    c.append(f'<path d="M 256 212 L 256 470" stroke="#B83A3A" stroke-width="1.2"/>')
    c.append(f'<text x="216" y="230" text-anchor="middle" {MONO} font-size="11.5" fill="#B83A3A">DATE DUE</text>')
    c.append(f'<text x="340" y="230" text-anchor="middle" {MONO} font-size="11.5" fill="#B83A3A">BORROWER’S NAME</text>')
    rows = [("DEC 25", "Meg March", -4, "#5A3A8A"), ("DEC 26", "Jo March", 3, "#3A4A8A"), ("DEC 28", "Beth March", -2, "#5A3A8A"), ("JAN 2", "Amy March", 5, "#8A2A3A")]
    for k, (d, n, r, col_) in enumerate(rows):
        y = 266 + k * 32
        c.append(f'<path d="M 176 {y + 8} L 424 {y + 8}" stroke="#7AA0C8" stroke-width="0.9" opacity="0.8"/>')
        uid = D.nid()
        rnd = random.Random(k)
        holes = "".join(f'<circle cx="{rnd.uniform(186, 250):.1f}" cy="{rnd.uniform(y - 16, y + 2):.1f}" r="{rnd.uniform(0.6, 1.4):.1f}" fill="#000"/>' for _ in range(18))
        c.append(f'<mask id="{uid}"><rect x="170" y="{y - 30}" width="100" height="40" fill="#fff"/>{holes}</mask>')
        c.append(f'<text x="216" y="{y}" text-anchor="middle" {MONO} font-size="17" fill="{col_}" opacity="0.85" mask="url(#{uid})" transform="rotate({r} 216 {y - 6})">{d}</text>')
        c.append(f'<text x="268" y="{y}" {MONO} font-size="17" fill="#2A2A3A">{n}</text>')
    out.append(f'<g transform="rotate({ang} {cx} {cy})">{"".join(c)}</g>')
    # the pocket
    pk = rot(rect_pts(150, 384, 450, 560, 30, 4, 0.3), cx, cy, ang)
    out.append(f'<path d="{smooth_closed(shift(pk, 4, -4))}" fill="#000000" opacity="0.2"/>')
    out.append(painted(D, pk, ("#F2DCA8", "#E2C488", "#9A7A48"), 4, sdir=(0.4, 1), sk=0.06, angle=-4, n=30, inkw=1.4, hi=0.15))
    pc = [f'<path d="M 270 384 A 30 22 0 0 0 330 384 Z" fill="#B89A68" opacity="0.7"/>',
          f'<text x="300" y="432" text-anchor="middle" {CINZEL} font-size="19" fill="#5A3A1E" letter-spacing="4">LENDING LIBRARY</text>',
          f'<path d="M 190 446 L 410 446" stroke="#5A3A1E" stroke-width="1.2"/>',
          f'<text x="300" y="472" text-anchor="middle" {JOST} font-size="16" fill="#5A3A1E">Please return by the date last stamped</text>']
    out.append(f'<g transform="rotate({ang} {cx} {cy})">{"".join(pc)}</g>')
    # four flowers tied for four sisters, and Jo's apple
    out.append(holly_sprig(D, 128, 500, -20, 5))
    out.append(apple(D, 482, 506, 36, seed=6))
    return finish_b(D, out, 7)


# ================================================================ 16. frankenstein — lightning blasts the old oak
def branchy(x, y, ang, L, w, depth, seed, col, out, spread=28, shrink=0.72):
    rnd = random.Random(seed)
    a = math.radians(ang)
    mid = (x + math.cos(a) * L * 0.5 + rnd.uniform(-L, L) * 0.08, y + math.sin(a) * L * 0.5 + rnd.uniform(-L, L) * 0.08)
    ex, ey = x + math.cos(a) * L, y + math.sin(a) * L
    out.append(taper([(x, y), mid, (ex, ey)], w, w * 0.62, col))
    if depth <= 0:
        return
    for k in range(rnd.choice([2, 2, 3])):
        da = rnd.uniform(-spread, spread) + (spread * 0.6 if k == 0 else -spread * 0.6 if k == 1 else 0)
        branchy(ex, ey, ang + da, L * rnd.uniform(shrink - 0.08, shrink + 0.06), w * 0.62, depth - 1, seed * 7 + k + 1, col, out, spread, shrink)


def lightning(x0, y0, x1, y1, seed, forks=3):
    rnd = random.Random(seed)
    pts = [(x0, y0)]
    n = 12
    for i in range(1, n):
        t = i / n
        pts.append((x0 + (x1 - x0) * t + rnd.uniform(-22, 22), y0 + (y1 - y0) * t + rnd.uniform(-6, 6)))
    pts.append((x1, y1))
    out = [f'<path d="{pd(pts, False)}" stroke="#B8A0FF" stroke-width="18" fill="none" opacity="0.18" stroke-linejoin="round"/>',
           f'<path d="{pd(pts, False)}" stroke="#D8CCFF" stroke-width="8" fill="none" opacity="0.4" stroke-linejoin="round"/>',
           f'<path d="{pd(pts, False)}" stroke="#FFFFFF" stroke-width="3.2" fill="none" stroke-linejoin="round"/>']
    for k in range(forks):
        i = rnd.randint(2, n - 4)
        fx, fy = pts[i]
        fp = [(fx, fy)]
        for j in range(4):
            fx += rnd.uniform(-34, 10) if k % 2 else rnd.uniform(-10, 34)
            fy += rnd.uniform(12, 24)
            fp.append((fx, fy))
        out.append(f'<path d="{pd(fp, False)}" stroke="#D8CCFF" stroke-width="5" fill="none" opacity="0.35" stroke-linejoin="round"/>')
        out.append(f'<path d="{pd(fp, False)}" stroke="#FFFFFF" stroke-width="1.6" fill="none" stroke-linejoin="round"/>')
    return "".join(out)


@design("frankenstein")
def frankenstein():
    D = Doc2("sbc-fr")
    out = [sky(D, [(0, "#14182E"), (0.5, "#2E3A5A"), (0.75, "#5A6A8A"), (1, "#2A3048")], 1, 600, ["#3A4A6A", "#141A2E", "#6A7A9A"], 80)]
    bx, by = 300, 378
    out.append(soft_glow(D, bx + 60, 220, 300, "#C8C0FF", 0.4))
    out.append(puff_cloud(D, 150, 190, 260, 2, ("#5A6A8A", "#2E3A58", "#141A2E"), op=0.95))
    out.append(puff_cloud(D, 470, 150, 260, 3, ("#6A7A9A", "#3A4668", "#181E34"), op=0.95))
    out.append(puff_cloud(D, 320, 230, 200, 4, ("#7A88A8", "#3E4A6A", "#1A2038"), op=0.8))
    # Alpine peaks lit by the flash
    out.append(hill(D, ridge([(-20, 330), (60, 262), (120, 300), (190, 236), (260, 296), (330, 270), (420, 220), (500, 280), (620, 250)], 3, 10, 4), 640,
                    ("#8A96C0", "#4A5478", "#20263E"), 5, inkw=0, n=40, lit="#E8E8FF"))
    for (px, py) in ((190, 236), (420, 220), (60, 262)):
        out.append(f'<path d="{pd([(px - 18, py + 22), (px, py), (px + 16, py + 20), (px + 6, py + 16), (px - 4, py + 24)])}" fill="#E8ECFF" opacity="0.8"/>')
    # the storm-dark hill with the oak
    out.append(hill(D, [(-20, 452), (120, 432), (240, 420), (330, 416), (420, 426), (620, 446)], 640, ("#4A5A4A", "#26302A", "#0E1410"), 6, inkw=1.2, n=60, lit="#C8C8FF"))
    trunk = []
    tb = by + 50
    for k, (ang, L, w) in enumerate(((-150, 64, 13), (-122, 70, 12), (-96, 62, 11), (-64, 66, 12), (-34, 60, 11))):
        sx_ = bx - 16 + k * 8
        branchy(sx_, by - 76 + abs(k - 2) * 8, ang, L * 0.82, w, 4, 20 + k, "#1E1A16", trunk, 26, 0.68)
    out.append("".join(trunk))
    out.append(taper(catmull([(bx - 26, tb), (bx - 20, by - 10), (bx - 26, by - 60), (bx - 40, by - 84)], 6), 40, 14, "#2A221A"))
    out.append(taper(catmull([(bx + 22, tb), (bx + 16, by - 10), (bx + 28, by - 56), (bx + 48, by - 82)], 6), 36, 12, "#2A221A"))
    out.append(taper(catmull([(bx - 34, tb), (bx - 28, by - 10), (bx - 34, by - 58)], 6), 8, 3, "#7A7A9A", 0.55))
    for k in range(5):
        out.append(pline([(bx - 30 + k * 4, tb - 4), (bx - 26 + k * 3, by - 20), (bx - 30 + k * 2, by - 50)], "#120E0A", 1.2, k, 0.6, 1))
    # roots
    for dx_ in (-48, -30, 30, 50):
        out.append(taper([(bx + dx_ * 0.4, tb - 6), (bx + dx_, tb + 4), (bx + dx_ * 1.4, tb + 8)], 9, 2, "#2A221A"))
    # split heartwood glowing, flames licking up from the strike
    fy0 = by - 56
    out.append(f'<path d="{smooth_closed([(bx - 8, by + 20), (bx - 14, by - 20), (bx - 6, fy0 - 10), (bx + 6, fy0 + 4), (bx + 6, by - 4)])}" fill="#FF8A2A"/>')
    out.append(f'<path d="{smooth_closed([(bx - 5, by + 4), (bx - 9, by - 20), (bx - 3, fy0 + 6), (bx + 3, by - 26)])}" fill="#FFE07A"/>')
    for k, (fx, fh) in enumerate(((bx - 6, 56), (bx + 9, 42), (bx - 20, 36))):
        out.append(f'<path d="M {fx - 9} {fy0} C {fx - 10} {fy0 - fh * 0.5} {fx - 2} {fy0 - fh * 0.7} {fx} {fy0 - fh} C {fx + 4} {fy0 - fh * 0.6} {fx + 10} {fy0 - fh * 0.4} {fx + 9} {fy0} Z" fill="#FF9A3A" opacity="0.9"/>')
        out.append(f'<path d="M {fx - 4} {fy0} C {fx - 4} {fy0 - fh * 0.4} {fx} {fy0 - fh * 0.5} {fx + 1} {fy0 - fh * 0.7} C {fx + 3} {fy0 - fh * 0.4} {fx + 5} {fy0 - fh * 0.2} {fx + 4} {fy0} Z" fill="#FFE8A0"/>')
    out.append(soft_glow(D, bx, fy0, 100, "#FF9A3A", 0.5))
    rnd = random.Random(9)
    for _ in range(36):
        a, r = rnd.uniform(-3.0, -0.2), rnd.uniform(20, 100)
        out.append(f'<circle cx="{bx + math.cos(a) * r:.1f}" cy="{fy0 + math.sin(a) * r:.1f}" r="{rnd.uniform(0.8, 2.2):.1f}" fill="#FFD08A" opacity="{rnd.uniform(0.5, 1):.2f}"/>')
    out.append(lightning(500, 150, bx + 6, by - 62, 10, 3))
    # rain
    for _ in range(140):
        x, y = rnd.uniform(-40, 640), rnd.uniform(0, 600)
        out.append(f'<path d="M {x:.1f} {y:.1f} l -7 22" stroke="#C8D0F0" stroke-width="1.2" opacity="{rnd.uniform(0.15, 0.4):.2f}"/>')
    out.append(f'<rect y="440" width="600" height="160" fill="{D.lin([(0, "#0A0E18", 0), (0.35, "#0A0E18", 0.7), (1, "#0A0E18", 0.9)])}"/>')
    # lettering
    out.append(gilt(D, 300, 100, "FRANKENSTEIN", CINZEL, 50, ls=6, max_w=450, seed=11, pal="silver", deboss="#05060E"))
    out.append(tx(300, 128, "MARY SHELLEY · 1818", CINZEL, 16, "#C8D0F0", ls=5, max_w=300))
    out.append(letters(D, 300, 496, "“Beware; for I am fearless,", SERIF_IT, 38, "#F2EEFF", ["#FFFFFF", "#D8D8F0"], 12, max_w=440,
                       shadow="#05060E", soff=(0.02, 0.05), angle=-40, wob=0.3))
    out.append(letters(D, 300, 536, "and therefore powerful.”", SERIF_IT, 38, "#F2EEFF", ["#FFFFFF", "#D8D8F0"], 13, max_w=440,
                       shadow="#05060E", soff=(0.02, 0.05), angle=-40, wob=0.3))
    return finish_b(D, out, 14, "#000000", 0.5)


# ================================================================ 17. dracula — the castle under a blood moon, wolves singing
def bat(x, y, s, col="#140A14", flap=0.0, ang=0):
    def L(pts):
        return T(pts, x, y, s, False, ang)
    right = [(2, -2), (8, -6 - flap * 6), (16, -8 - flap * 8), (24, -6 - flap * 6), (32, -10 - flap * 4), (30, -2), (26, 2), (22, -1), (18, 3), (12, 0), (8, 4), (4, 3)]
    left = [(-x_, y_) for x_, y_ in right[::-1]]
    out = [f'<path d="{smooth_closed(L(right + left))}" fill="{col}"/>']
    out.append(f'<path d="{blob(*L([(0, 0)])[0], 3.4 * s, 5 * s, int(x), 0.1, 8)}" fill="{col}"/>')
    out.append(f'<path d="{pd(L([(-3, -4), (-2, -9), (0, -5), (2, -9), (3, -4)]))}" fill="{col}"/>')
    return "".join(out)


def wolf_howl(x, base, s, col="#140A18", rim="#FF8A6A", flip=False):
    """A wolf sitting on its haunches, muzzle raised to the sky, howling; faces left."""
    def L(pts):
        return T(pts, x, base, s, flip)
    pts = [(-18, 0), (-6, 0), (-6, -20), (2, -12), (12, -6), (16, 0), (44, 0), (48, -10), (44, -24), (36, -38), (26, -50), (16, -62),
           (10, -74), (8, -84), (12, -92), (6, -94), (0, -88), (-6, -92), (-16, -104), (-26, -116), (-32, -118), (-31, -112), (-26, -104),
           (-24, -98), (-22, -94), (-18, -84), (-20, -76), (-26, -68), (-22, -62), (-26, -54), (-20, -48), (-22, -36), (-16, -24)]
    out = [f'<path d="{smooth_closed(L(pts))}" fill="{col}"/>']
    out.append(taper(catmull(L([(42, -4), (56, 2), (70, 2), (80, -6)]), 5), 11 * s, 3 * s, col))
    out.append(ink(smooth_open(L([(-32, -118), (-26, -116), (-16, -104), (-6, -92), (0, -88), (6, -94), (12, -92), (8, -84), (10, -74), (16, -62), (26, -50), (36, -38)])), rim, 1.6, 1, 1, 0.65))
    return "".join(out)


def castle(D, base, seed, col="#1A0E1E", lit="#FFC870"):
    rnd = random.Random(seed)
    out = []
    towers = [(286, 28, 112, "cone"), (330, 22, 88, "cone"), (370, 34, 132, "cone"), (418, 26, 100, "battl"), (452, 22, 78, "cone"), (250, 20, 76, "battl")]
    # curtain walls
    out.append(f'<path d="{pd([(240, base), (240, base - 70), (470, base - 70), (470, base)])}" fill="{col}"/>')
    for k in range(20):
        out.append(f'<rect x="{240 + k * 12}" y="{base - 78}" width="7" height="9" fill="{col}"/>')
    for (x, w, h, roof) in sorted(towers, key=lambda t: t[2]):
        out.append(f'<path d="{pd([(x - w / 2, base), (x - w / 2, base - h), (x + w / 2, base - h), (x + w / 2, base)])}" fill="{col}"/>')
        if roof == "cone":
            out.append(f'<path d="{pd([(x - w / 2 - 5, base - h + 2), (x, base - h - w * 1.5), (x + w / 2 + 5, base - h + 2)])}" fill="{col}"/>')
            out.append(f'<path d="M {x} {base - h - w * 1.5} l 0 -12" stroke="{col}" stroke-width="2"/>')
        else:
            for j in range(int(w / 8) + 1):
                out.append(f'<rect x="{x - w / 2 + j * 8 - 1:.1f}" y="{base - h - 8}" width="5" height="9" fill="{col}"/>')
        for j in range(int(h / 30)):
            if rnd.random() < 0.45:
                wy = base - h + 16 + j * 30
                out.append(f'<path d="M {x - 3:.1f} {wy + 12} L {x - 3:.1f} {wy + 3} Q {x:.1f} {wy - 2} {x + 3:.1f} {wy + 3} L {x + 3:.1f} {wy + 12} Z" fill="{lit}"/>')
                out.append(soft_glow(D, x, wy + 6, 14, lit, 0.5))
    # rim light from the moon
    out.append(f'<path d="M 370 {base - 132 - 51} L {370 + 17} {base - 132}" stroke="#FF9A7A" stroke-width="1.4" opacity="0.6"/>')
    return "".join(out)


@design("dracula")
def dracula():
    D = Doc2("sbc-dr")
    out = [sky(D, [(0, "#1A0A24"), (0.45, "#4A1430"), (0.8, "#8A2A2A"), (1, "#3A1020")], 1, 600, ["#5A1A3A", "#2A0A1A", "#A83A3A"], 60)]
    out.append(stars_field(2, (0, 0, 600, 260), 70, cols=("#FFE8E0", "#FFFFFF")))
    mx, my, mr = 372, 250, 118
    out.append(soft_glow(D, mx, my, mr * 2.4, "#FF7A5A", 0.4))
    out.append(painted(D, blob_pts(mx, my, mr, mr, 3, 0.005, 40), ("#FFE2B8", "#F2A878", "#C8684A"), 3, sdir=(0.6, 0.6), sk=0.08, angle=-30, n=60, inkw=0, hi=0.3))
    for (cx_, cy_, r_) in ((340, 222, 22), (400, 280, 16), (410, 210, 12), (350, 290, 10)):
        out.append(f'<path d="{blob(cx_, cy_, r_, r_ * 0.85, int(cx_), 0.15, 12)}" fill="#C8684A" opacity="0.35"/>')
    out.append(taper([(240, 236), (380, 226), (520, 240)], 6, 3, "#3A1020", 0.55))
    out.append(taper([(200, 278), (330, 270), (480, 282)], 4, 2, "#3A1020", 0.5))
    # the crag
    crag = [(220, 620), (230, 470), (252, 420), (262, 380), (300, 362), (340, 356), (400, 360), (440, 356), (478, 372), (500, 420), (520, 520), (540, 620)]
    out.append(f'<path d="{smooth_closed(ridge(crag, 4, 8, 3))}" fill="#22101E"/>')
    for k in range(8):
        x = 250 + k * 32
        out.append(pline([(x, 380 + (k % 3) * 8), (x - 6 + k, 450), (x - 10, 530)], "#4A2030", 1.6, k, 0.5, 1))
    out.append(ink(smooth_open(ridge(crag, 4, 8, 3)[:6]), "#FF8A6A", 1.6, 5, 1, 0.45))
    out.append(castle(D, 362, 6))
    # bats
    for k, (x, y, sz, fl) in enumerate(((170, 210, 1.0, 0.4), (226, 262, 0.7, 0.9), (520, 176, 0.8, 0.2), (530, 236, 0.6, 0.8), (120, 300, 0.6, 0.0), (480, 300, 0.55, 0.6))):
        out.append(bat(x, y, sz, flap=fl, ang=k * 7 - 10))
    # forest of firs below and the wolves on their rock
    from paint import conifer
    rnd = random.Random(7)
    for k in range(22):
        x = -10 + k * 30 + rnd.uniform(-8, 8)
        out.append(conifer(x, 610, rnd.uniform(90, 140), "#120812", k, width=0.34))
    rock = [(-20, 620), (-20, 470), (40, 450), (120, 446), (180, 470), (210, 520), (230, 620)]
    out.append(f'<path d="{smooth_closed(rock)}" fill="#1A0A16"/>')
    out.append(ink(smooth_open(rock[1:5]), "#FF8A6A", 1.6, 8, 1, 0.5))
    out.append(wolf_howl(64, 452, 0.9))
    out.append(wolf_howl(176, 470, 0.66, flip=True))
    # lettering
    out.append(gilt(D, 300, 110, "DRACULA", CINZEL, 70, ls=12, max_w=420, seed=9, deboss="#0A0408"))
    out.append(tx(300, 140, "BRAM STOKER · 1897", CINZEL, 16, "#F2C8B0", ls=5, max_w=300))
    out.append(tx(300, 504, "“…the children of the night.", SERIF_IT, 30, "#FFE8D8", max_w=420))
    out.append(tx(300, 538, "What music they make!”", SERIF_IT, 30, "#FFE8D8", max_w=420))
    return finish_b(D, out, 10, "#000000", 0.5)


# ================================================================ 18. romeo and juliet — the balcony in Verona
def cypress_tree(D, x, base, h, seed, pal=("#3A5A4A", "#1E3A2E", "#0E2018")):
    pts = []
    for i in range(13):
        t = i / 12
        w = h * 0.11 * math.sin(math.pi * min(1, 0.08 + t * 0.95)) ** 0.7
        pts.append((x - w, base - h * t))
    rpts = [(x + w_ * -1 + 2 * x - 2 * x, y) for (w_, y) in []]
    pts2 = [(2 * x - px, py) for px, py in pts[::-1]]
    shape = jitter(pts + pts2, seed, 2)
    out = [painted(D, shape, pal, seed, sdir=(1, 0.2), sk=0.2, angle=-90, n=30, inkw=0, hi=0.3)]
    out.append(dab_crown(D, x, base - h * 0.5, h * 0.09, h * 0.45, [pal], seed + 1, n=int(h * 0.5), size=(3, 6), inkw=0, base=False))
    return "".join(out)


def juliet(x, y, s, col="#3A1A1A"):
    """Juliet at her window, leaning her cheek upon her hand: a warm-backlit silhouette (head and shoulders)."""
    def L(pts):
        return T(pts, x, y, s)
    out = [f'<path d="{smooth_closed(L([(-26, 0), (-22, -18), (-12, -26), (-4, -28), (6, -26), (14, -20), (22, -6), (26, 0)]))}" fill="{col}"/>']
    out.append(f'<path d="{smooth_closed(L([(-4, -26), (-6, -34), (2, -36), (6, -28)]))}" fill="{col}"/>')
    out.append(f'<path d="{blob(*L([(-2, -46)])[0], 9 * s, 11 * s, 3, 0.05, 12, 15)}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed(L([(-10, -54), (0, -60), (10, -54), (12, -40), (8, -30), (4, -44), (-6, -50)]))}" fill="{col}"/>')
    out.append(f'<path d="{blob(*L([(8, -56)])[0], 6 * s, 5 * s, 4, 0.1, 8)}" fill="{col}"/>')
    out.append(taper(L([(14, -6), (8, -18), (-6, -36)]), 6 * s, 4 * s, col))
    out.append(ink(smooth_open(L([(-10, -54), (-12, -46), (-10, -38), (-6, -34)])), "#FFD88A", 1.4, 1, 1, 0.7))
    return "".join(out)


@design("romeo-and-juliet")
def romeo_and_juliet():
    D = Doc2("sbc-rj")
    out = [sky(D, [(0, "#1E2A5A"), (0.5, "#4A4A8A"), (0.8, "#C8789A"), (1, "#F2B08A")], 1, 600, ["#5A5A9A", "#2A2A5A", "#E8A0A8"], 50)]
    out.append(stars_field(1, (0, 0, 600, 200), 40))
    out.append(f'<path d="{blob(110, 214, 16, 16, 2, 0.02, 16)}" fill="#FFF6DA"/><path d="{blob(118, 209, 15, 15, 3, 0.02, 16)}" fill="#3A3E78"/>')
    out.append(soft_glow(D, 110, 214, 50, "#FFF6DA", 0.3))
    out.append(cypress_tree(D, 70, 470, 270, 4))
    out.append(cypress_tree(D, 150, 480, 220, 5, ("#2E4A3E", "#16302A", "#081812")))
    # the palazzo wall (warm stucco, lamplit from within)
    wx0 = 220
    out.append(painted(D, rect_pts(wx0, 170, 640, 640, 30, 6, 0.4), ("#F2C89A", "#C88A64", "#7A4A3E"), 6, sdir=(-0.8, 0.2), sk=0.06, angle=-90, n=120, inkw=1.4, hi=0.2))
    out.append(f'<rect x="{wx0}" y="170" width="420" height="440" fill="{D.lin([(0, "#2A1A3A", 0.55), (0.45, "#2A1A3A", 0.25), (1, "#2A1A3A", 0.1)], 0, 0, 1, 0)}"/>')
    for k in range(9):
        out.append(f'<path d="M {wx0} {176 + k * 6} L 640 {176 + k * 6}" stroke="#E8B88A" stroke-width="1.2" opacity="0.3"/>')
    out.append(painted(D, rect_pts(wx0 - 8, 160, 640, 178, 20, 7, 0.3), ("#F6D8B0", "#D8A07A", "#8A5A48"), 7, sk=0.2, angle=0, n=20, inkw=1.4, hi=0.4))
    # the window, glowing, arched
    cx = 400
    ww, wt, wb = 100, 214, 342
    win = [(cx - ww / 2, wb)] + ell_pts(cx, wt + ww / 2, ww / 2, ww / 2, 180, 360, 18) + [(cx + ww / 2, wb)]
    frame = [(cx - ww / 2 - 14, wb)] + ell_pts(cx, wt + ww / 2, ww / 2 + 14, ww / 2 + 14, 180, 360, 18) + [(cx + ww / 2 + 14, wb)]
    out.append(soft_glow(D, cx, 290, 200, "#FFC870", 0.45))
    out.append(painted(D, frame, ("#FFF0D8", "#E8C8A0", "#9A7A60"), 8, sk=0.15, angle=-90, n=20, inkw=1.6, hi=0.4))
    out.append(f'<path d="{smooth_closed(win)}" fill="{D.lin([(0, "#FFE8A8"), (1, "#F2A050")])}"/>')
    out.append(soft_glow(D, cx, 300, 60, "#FFFFFF", 0.4))
    out.append(juliet(cx - 4, wb - 2, 1.25))
    out.append(f'<path d="M {cx} {wt + 4} L {cx} {wb}" stroke="#7A4A30" stroke-width="2" opacity="0.5"/>')
    # the balcony
    by0 = 342
    out.append(painted(D, rect_pts(cx - 96, by0, cx + 96, by0 + 16, 20, 9, 0.3), ("#FFF2DC", "#E2C8A8", "#8A6A54"), 9, sdir=(0, 1), sk=0.25, angle=0, n=16, inkw=1.6, hi=0.5))
    for k in range(9):
        bx = cx - 84 + k * 21
        bal = [(bx - 6, by0 + 74), (bx - 4, by0 + 60), (bx - 8, by0 + 44), (bx - 4, by0 + 22), (bx - 5, by0 + 16), (bx + 5, by0 + 16), (bx + 4, by0 + 22), (bx + 8, by0 + 44), (bx + 4, by0 + 60), (bx + 6, by0 + 74)]
        out.append(painted(D, bal, ("#FFF2DC", "#E2C8A8", "#7A5A48"), 10 + k, sdir=(1, 0.2), sk=0.3, angle=-90, n=5, inkw=1.1, hi=0.4))
    out.append(painted(D, rect_pts(cx - 100, by0 + 74, cx + 100, by0 + 90, 20, 11, 0.3), ("#FFF2DC", "#E2C8A8", "#8A6A54"), 11, sdir=(0, 1), sk=0.25, angle=0, n=16, inkw=1.6, hi=0.4))
    for k in range(4):
        x = cx - 72 + k * 48
        out.append(painted(D, [(x - 10, by0 + 90), (x + 10, by0 + 90), (x + 6, by0 + 110), (x, by0 + 120), (x - 6, by0 + 110)], ("#F2DCC0", "#C8A888", "#6A4A3A"), 12 + k, sk=0.25, n=4, inkw=1.2, hi=0.3))
    # climbing roses and leaves around the balcony
    rnd = random.Random(13)
    vine = catmull([(250, 610), (262, 520), (290, 470), (310, 430), (300, 380), (310, 340), (296, 280)], 8)
    out.append(pline(vine, "#3A4A22", 3, 13, 0.9, 1))
    for i in range(0, len(vine), 3):
        vx, vy = vine[i]
        out.append(leaf_simple(D, vx, vy, 20, 6, rnd.uniform(-170, 10), LEAF, 20 + i, vein=False, inkw=0.8))
        if i % 6 == 0:
            out.append(rose_bloom(D, vx + rnd.uniform(-8, 8), vy + rnd.uniform(-6, 6), 11, 40 + i, ROSE, rnd.uniform(0, 90)))
    for k in range(6):
        x = cx - 90 + k * 36
        out.append(leaf_simple(D, x, by0 + 76, 18, 5, rnd.uniform(60, 120), LEAF, 60 + k, vein=False, inkw=0.8))
        out.append(rose_bloom(D, x + 6, by0 + 86 + (k % 2) * 8, 9, 70 + k, ROSE, k * 30))
    # a single rose dropped on the balustrade
    out.append(leaf_simple(D, cx + 60, by0 + 4, 40, 3, 190, ("#7A9A4A", "#4A6A2A", "#2A3A14"), 80, vein=False, inkw=0.8))
    out.append(rose_bloom(D, cx + 64, by0 + 2, 10, 81, ROSE, 40))
    # dark garden hedge at the bottom for the quotation
    out.append(f'<path d="{smooth_closed([(-20, 470), (100, 456), (220, 468), (360, 462), (480, 470), (620, 460), (620, 640), (-20, 640)])}" fill="#14201A"/>')
    out.append(dab_crown(D, 300, 478, 340, 16, [("#3A5A3A", "#24402A", "#122016")], 14, n=140, size=(5, 10), inkw=0, base=False))
    # lettering
    out.append(tx(240, 84, "WILLIAM SHAKESPEARE", CINZEL, 16, "#F2E2D8", ls=5, max_w=330))
    out.append(letters(D, 240, 142, "Romeo and Juliet", SERIF_IT, 56, "#FFF2E2", ["#FFFFFF", "#F2D8D0"], 15, max_w=400,
                       shadow="#1A1240", soff=(0.02, 0.04), angle=-40, wob=0.4))
    out.append(tx(300, 510, "“But soft, what light through", SERIF_IT, 32, "#FFE8C8", max_w=440))
    out.append(tx(300, 544, "yonder window breaks?”", SERIF_IT, 32, "#FFE8C8", max_w=440))
    return finish_b(D, out, 16, "#000000", 0.5)


# ================================================================ 19. hamlet — the skull in the limelight
def skull(D, cx, cy, s, seed, pal=("#FFF6E2", "#E8D8B8", "#8A7458")):
    """Human skull in three-quarter view (upper jaw only), ivory, lit from upper left."""
    def L(pts):
        return T(pts, cx, cy, s)
    out = [cast(D, cx + 10 * s, cy + 44 * s, 56 * s, 9 * s, strength=0.45, seed=seed)]
    cran = L([(-44, -6), (-48, -34), (-36, -62), (-10, -76), (20, -74), (42, -56), (50, -30), (48, -4), (40, 14), (30, 20), (26, 34), (12, 44), (-10, 44), (-24, 36), (-30, 20), (-40, 10)])
    out.append(painted(D, cran, pal, seed, sdir=(0.7, 0.5), sk=0.18, angle=-60, n=40, inkw=1.8, inkc="#4A3A28", hi=0.55, hik=0.08))
    # temple hollow and cheekbone
    out.append(f'<path d="{smooth_closed(L([(26, -20), (42, -24), (46, -4), (36, 6), (26, -2)]))}" fill="{pal[2]}" opacity="0.35"/>')
    out.append(taper(L([(-30, 12), (-14, 16), (4, 12)]), 3 * s, 1.5 * s, pal[0], 0.8))
    # eye sockets
    for (ex, ey, rx, ry, k) in ((-18, -4, 13, 12, 0), (16, -4, 12, 12, 1)):
        ep = blob_pts(*L([(ex, ey)])[0], rx * s, ry * s, seed + 2 + k, 0.1, 14)
        out.append(f'<path d="{smooth_closed(ep)}" fill="#2A1C12"/>')
        out.append(f'<path d="{smooth_closed(shift(ep, 2 * s, 3 * s))}" fill="#120A06" opacity="0.6"/>')
        out.append(pline(L([(ex - rx, ey - ry * 0.6), (ex, ey - ry - 2), (ex + rx, ey - ry * 0.5)]), "#FFFFFF", 1.6 * s, seed, 0.5, 1))
    # nasal cavity
    out.append(f'<path d="{smooth_closed(L([(-4, 10), (0, 8), (4, 12), (3, 22), (-1, 24), (-5, 20)]))}" fill="#2A1C12"/>')
    # upper teeth
    for k in range(8):
        tx_ = -16 + k * 4.4
        out.append(f'<path d="{hg.org_rect(*L([(tx_, 30)])[0], 4 * s, 9 * s, seed + k, 0.2, 4, 1)}" fill="#F6ECD6" stroke="#6A5440" stroke-width="0.9"/>')
    out.append(pline(L([(-18, 30), (0, 32), (20, 29)]), "#6A5440", 1.2, seed, 0.7, 1))
    # cranial suture
    out.append(pline(L([(-6, -74), (-2, -66), (-8, -58), (-2, -50), (-6, -42)]), "#9A8460", 1.1, seed, 0.6, 1))
    return "".join(out)


def velvet_curtain(D, x0, x1, top, bottom, seed, pal=("#D84A4A", "#9A1A22", "#4A060A"), tie=None, side=-1):
    pts = [(x0, top), (x1, top), (x1, bottom)] if side < 0 else [(x0, top), (x1, top), (x0, bottom)]
    if tie:
        ty_ = tie
        if side < 0:
            pts = [(x0, top), (x1, top), (x1 - (x1 - x0) * 0.55, ty_), (x0 + (x1 - x0) * 0.35, ty_ + 30), (x0 + (x1 - x0) * 0.6, bottom), (x0, bottom)]
        else:
            pts = [(x0, top), (x1, top), (x1, bottom), (x1 - (x1 - x0) * 0.6, bottom), (x1 - (x1 - x0) * 0.35, ty_ + 30), (x0 + (x1 - x0) * 0.55, ty_)]
    d = smooth_closed(pts) if tie else pd(pts)
    out = [f'<path d="{d}" fill="{pal[1]}"/>']
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    rnd = random.Random(seed)
    for k in range(9):
        fx = x0 + (x1 - x0) * (k + 0.5) / 9
        inner.append(taper([(fx, top), (fx + rnd.uniform(-6, 6), (top + bottom) / 2), (fx + side * 30 * (k / 9), bottom)], 16, 22, pal[2], 0.5))
        inner.append(taper([(fx + 9, top), (fx + 9 + rnd.uniform(-4, 4), (top + bottom) / 2), (fx + 9 + side * 30 * (k / 9), bottom)], 5, 8, pal[0], 0.5))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, "#2A0206", 1.6, seed, 1, 0.6))
    return "".join(out)


@design("hamlet")
def hamlet():
    D = Doc2("sbc-hm")
    out = [f'<rect width="600" height="600" fill="#140808"/>']
    # stage boards in perspective
    floor = [(-40, 600), (640, 600), (470, 400), (130, 400)]
    out.append(f'<path d="{pd(floor)}" fill="#6A4026"/>')
    for k in range(13):
        t = k / 12
        out.append(f'<path d="M {130 + 340 * t:.1f} 400 L {-40 + 680 * t:.1f} 600" stroke="#3A200E" stroke-width="1.6" opacity="0.7"/>')
    out.append(strokes(D.nid(), pd(floor), (-40, 400, 640, 600), ["#8A5A36", "#4A2A14"], 2, n=80, angle=0, length=(30, 90), width=(1, 3), opacity=(0.2, 0.4)))
    # back wall in shadow
    out.append(f'<rect x="0" y="0" width="600" height="400" fill="{D.lin([(0, "#1A0A0C"), (1, "#2A1418")])}"/>')
    # limelight cone and pool
    out.append(f'<path d="M 270 0 L 330 0 L 420 470 L 180 470 Z" fill="{D.lin([(0, "#FFF2C8", 0.05), (1, "#FFF2C8", 0.22)])}"/>')
    out.append(f'<ellipse cx="300" cy="462" rx="150" ry="36" fill="{D.rad([(0, "#FFE8B0", 0.6), (1, "#FFE8B0", 0)])}"/>')
    # the stool, a book and the skull, a guttering candle
    sx_, sy_ = 300, 452
    out.append(cast(D, sx_ + 8, sy_ + 4, 80, 9, strength=0.5, seed=3))
    for lx in (-44, 44):
        out.append(taper([(sx_ + lx * 0.8, sy_ - 54), (sx_ + lx, sy_)], 8, 7, "#4A2A16"))
    out.append(painted(D, rect_pts(sx_ - 62, sy_ - 70, sx_ + 62, sy_ - 54, 16, 4, 0.3), WOOD, 4, sdir=(0.3, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.5))
    out.append(book3(D, sx_ - 54, sy_ - 92, 104, 18, 8, 5, cover=OXBLOOD))
    out.append(skull(D, sx_, sy_ - 140, 0.95, 6))
    out.append(candle(D, sx_ + 92, sy_ - 54 + 0, 30, 7, w=12, glow_r=70))
    # proscenium: curtains and a gilt arch with the title
    out.append(velvet_curtain(D, -10, 150, 0, 600, 8, tie=330, side=-1))
    out.append(velvet_curtain(D, 450, 610, 0, 600, 9, tie=330, side=1))
    for (tx_, ty_) in ((96, 336), (504, 336)):
        out.append(ink(f"M {tx_ - 30} {ty_ - 6} Q {tx_} {ty_ + 10} {tx_ + 30} {ty_ - 6}", "#D9A945", 5, 10, 1, 1))
        out.append(f'<path d="{blob(tx_, ty_ + 18, 9, 14, 11, 0.1, 10)}" fill="#D9A945"/>')
        for k in range(7):
            out.append(f'<path d="M {tx_ - 9 + k * 3} {ty_ + 28} l 0 18" stroke="#B8862E" stroke-width="2"/>')
    val = [(-10, 0), (610, 0), (610, 150)] + [(610 - k * 62, 150 + (24 if k % 2 else 0)) for k in range(11)] + [(-10, 150)]
    out.append(f'<path d="{smooth_closed(val)}" fill="#8E1820"/>')
    vid = D.clip(f'<path d="{smooth_closed(val)}"/>')
    swags = "".join(taper([(k * 62 - 31, 0), (k * 62, 150 + (24 if k % 2 else 0)), (k * 62 + 31, 0)], 14, 14, "#5A0810", 0.5) for k in range(11))
    out.append(f'<g {vid}>{swags}</g>')
    g = gilt_fill(D, 140, 190)
    for k in range(11):
        x = 610 - k * 62
        out.append(f'<circle cx="{x}" cy="{150 + (24 if k % 2 else 0) + 4}" r="5" fill="{g}"/>')
    out.append(f'<path d="{smooth_open(val[2:-1])}" fill="none" stroke="{g}" stroke-width="5" opacity="0.9"/>')
    out.append(gilt(D, 300, 100, "HAMLET", CINZEL, 62, ls=14, max_w=380, seed=12, deboss="#2A0206"))
    out.append(tx(300, 130, "PRINCE OF DENMARK", CINZEL, 16, "#F2D8A8", ls=6, max_w=300))
    # the line
    out.append(letters(D, 300, 512, "To be, or not to be,", SERIF_IT, 50, "#FFF2D8", ["#FFFFFF", "#F2DCB8"], 13, max_w=440,
                       shadow="#140808", soff=(0.02, 0.05), angle=-40, wob=0.3))
    out.append(tx(300, 544, "that is the question", SERIF_IT, 26, "#E8C888", max_w=360))
    return finish_b(D, out, 14, "#000000", 0.5)


# ================================================================ 20. through the looking-glass — the mirror melting into mist
def chess_piece(D, cx, base, h, kind, pal, seed):
    """Turned wooden chess piece (profile): 'queen' (coronet with ball) or 'king' (cross)."""
    w = h * 0.42
    prof = [(0, w * 0.5), (0.06, w * 0.5), (0.1, w * 0.42), (0.14, w * 0.44), (0.2, w * 0.3), (0.3, w * 0.2), (0.55, w * 0.14), (0.66, w * 0.2), (0.7, w * 0.14),
            (0.76, w * 0.18), (0.86, w * 0.3), (0.9, w * 0.26)]
    right = [(cx + ww, base - h * t * 0.9) for t, ww in prof]
    left = [(cx - ww, base - h * t * 0.9) for t, ww in prof[::-1]]
    out = [cast(D, cx + 6, base, w * 0.6, 5, strength=0.45, seed=seed)]
    out.append(painted(D, right + left, pal, seed, sdir=(1, 0.2), sk=0.25, angle=-90, n=16, inkw=1.4, hi=0.6, hik=0.12))
    top = base - h * 0.9 * 0.9
    if kind == "queen":
        crown = [(cx - w * 0.28, top), (cx - w * 0.36, top - h * 0.08), (cx - w * 0.2, top - h * 0.04), (cx - w * 0.1, top - h * 0.1), (cx, top - h * 0.05),
                 (cx + w * 0.1, top - h * 0.1), (cx + w * 0.2, top - h * 0.04), (cx + w * 0.36, top - h * 0.08), (cx + w * 0.28, top)]
        out.append(painted(D, crown, pal, seed + 1, sk=0.2, n=4, inkw=1.2, hi=0.5))
        out.append(painted(D, blob_pts(cx, top - h * 0.12, w * 0.12, w * 0.12, seed + 2, 0.02, 10), pal, seed + 2, sk=0.2, n=2, inkw=1.1, hi=0.6))
    else:
        out.append(painted(D, rect_pts(cx - w * 0.22, top - h * 0.06, cx + w * 0.22, top, 6, seed, 0.2), pal, seed + 1, sk=0.2, n=3, inkw=1.2, hi=0.5))
        out.append(painted(D, [(cx - 3, top - h * 0.06), (cx - 3, top - h * 0.12), (cx - 8, top - h * 0.12), (cx - 8, top - h * 0.16), (cx - 3, top - h * 0.16), (cx - 3, top - h * 0.2),
                               (cx + 3, top - h * 0.2), (cx + 3, top - h * 0.16), (cx + 8, top - h * 0.16), (cx + 8, top - h * 0.12), (cx + 3, top - h * 0.12), (cx + 3, top - h * 0.06)], pal, seed + 2, sk=0.2, n=2, inkw=1.1, hi=0.5))
    return "".join(out)


def rococo_frame(D, cx, cy, rx, ry, seed):
    """Gilt oval mirror frame with shell crest, scrolls and a beaded inner edge."""
    out = []
    outer = ell_pts(cx, cy, rx + 26, ry + 26, 0, 360, 48)[:-1]
    inner = ell_pts(cx, cy, rx, ry, 0, 360, 48)[:-1]
    d = smooth_closed(outer) + " " + smooth_closed(inner[::-1])
    out.append(f'<path d="{smooth_closed(shift(outer, 6, 8))}" fill="#000000" opacity="0.35"/>')
    out.append(f'<path d="{d}" fill="{GOLD[1]}" fill-rule="evenodd"/>')
    out.append(f'<path d="{d}" fill="{D.lin([(0, "#FFF2B8", 0.8), (0.45, "#D9A945", 0), (1, "#5A3A10", 0.75)], 0, 0, 1, 1)}" fill-rule="evenodd"/>')
    for k in range(36):
        a = math.radians(k * 10)
        x0_, y0_ = cx + math.cos(a) * (rx + 6), cy + math.sin(a) * (ry + 6)
        x1_, y1_ = cx + math.cos(a + 0.12) * (rx + 20), cy + math.sin(a + 0.12) * (ry + 20)
        out.append(f'<path d="M {x0_:.1f} {y0_:.1f} Q {(x0_ + x1_) / 2 + 4:.1f} {(y0_ + y1_) / 2:.1f} {x1_:.1f} {y1_:.1f}" stroke="#7A5418" stroke-width="1.6" fill="none" opacity="0.7"/>')
    for k in range(60):
        a = math.radians(k * 6)
        out.append(f'<circle cx="{cx + math.cos(a) * (rx + 3):.1f}" cy="{cy + math.sin(a) * (ry + 3):.1f}" r="2.2" fill="#FFE8A0" stroke="#8A6020" stroke-width="0.6"/>')
    # shell crest on top, scroll feet
    sx, sy = cx, cy - ry - 26
    shell = [(sx - 30, sy + 10)] + [(sx + 32 * math.cos(math.radians(a)), sy + 6 - 26 * math.sin(math.radians(a))) for a in range(180, -1, -15)] + [(sx + 30, sy + 10)]
    out.append(painted(D, shell, GOLD, seed, sdir=(0.5, 0.8), sk=0.2, angle=-90, n=10, inkw=1.4, inkc="#5A3A10", hi=0.5))
    for k in range(7):
        a = math.radians(15 + k * 25)
        out.append(f'<path d="M {sx:.1f} {sy + 8:.1f} L {sx + 29 * math.cos(a):.1f} {sy + 6 - 23 * math.sin(a):.1f}" stroke="#7A5418" stroke-width="1.6"/>')
    for sg in (-1, 1):
        out.append(taper(catmull([(cx + sg * 30, cy + ry + 18), (cx + sg * 70, cy + ry + 34), (cx + sg * 96, cy + ry + 20), (cx + sg * 88, cy + ry + 6), (cx + sg * 76, cy + ry + 14)], 6), 9, 4, GOLD[1]))
        out.append(taper(catmull([(cx + sg * (rx + 20), cy - 30), (cx + sg * (rx + 44), cy), (cx + sg * (rx + 30), cy + 40), (cx + sg * (rx + 16), cy + 30)], 6), 9, 4, GOLD[1]))
    out.append(ink(smooth_closed(outer), "#4A2E08", 1.8, seed, 1, 0.7))
    return "".join(out)


@design("through-the-looking-glass")
def through_the_looking_glass():
    D = Doc2("sbc-lg")
    out = [wallpaper_damask(D, "#2E5A5A", "#8AC0B0", 1, 58, 0.25)]
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFF2D8", 0.2), (0.6, "#000000", 0.1), (1, "#000000", 0.5)], cy=0.45, r=0.75)}"/>')
    cx, cy, rx, ry = 300, 314, 116, 112
    # the glass: a looking-glass country of chessboard fields, half dissolved in silver mist
    cid = D.clip(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/>')
    g = [f'<rect width="600" height="600" fill="{D.lin([(0, "#D8EEF2"), (1, "#FFF6E0")], 0, cy - ry, 0, cy + 20, "userSpaceOnUse")}"/>']
    hor = 300
    for i in range(-10, 11):
        for j in range(9):
            y0_, y1_ = hor + j * j * 3.2, hor + (j + 1) * (j + 1) * 3.2
            def X(i_, y_):
                return cx + i_ * 20 * (1 + (y_ - hor) / 30)
            q = [(X(i, y0_), y0_), (X(i + 1, y0_), y0_), (X(i + 1, y1_), y1_), (X(i, y1_), y1_)]
            c = "#7AB060" if (i + j) % 2 else "#C8D890"
            g.append(f'<path d="{pd(q)}" fill="{c}"/>')
    for k in range(5):
        y = hor + k * k * 3.2 * 4
        g.append(f'<path d="M 0 {y:.1f} L 600 {y:.1f}" stroke="#5A9AC8" stroke-width="{1 + k * 0.6:.1f}" opacity="0.8"/>')
    for k, (tx_, ty_) in enumerate(((220, 316), (390, 306), (330, 340), (250, 360))):
        g.append(taper([(tx_, ty_), (tx_, ty_ - 14 - k * 4)], 3 + k, 2, "#5A3A22"))
        g.append(dab_crown(D, tx_, ty_ - 22 - k * 5, 10 + k * 3, 9 + k * 2, [LEAF], 20 + k, n=18, size=(3, 5), inkw=0))
    g.append(puff_cloud(D, 240, 220, 120, 3, ("#FFFFFF", "#F2F6F8", "#C8D8E0")))
    # silvery mist dissolving the glass from the edges
    g.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{D.rad([(0, "#FFFFFF", 0), (0.55, "#E8F0F4", 0.15), (1, "#D8E2EA", 0.95)])}"/>')
    rnd = random.Random(4)
    for k in range(30):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(0.55, 0.95)
        g.append(f'<path d="{blob(cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r, rnd.uniform(14, 30), rnd.uniform(8, 16), 30 + k, 0.2, 10, math.degrees(a) + 90)}" fill="#FFFFFF" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>')
    for _ in range(14):
        g.append(sparkle(cx + rnd.uniform(-rx * 0.8, rx * 0.8), cy + rnd.uniform(-ry * 0.8, ry * 0.8), rnd.uniform(3, 6), "#FFFFFF", 0.9))
    out.append(f'<g {cid}>{"".join(g)}</g>')
    out.append(rococo_frame(D, cx, cy, rx, ry, 5))
    # the mantelpiece
    out.append(painted(D, rect_pts(0, 452, 600, 474, 30, 6, 0.3), ("#FFFFFF", "#E8E2D8", "#9A9088"), 6, sdir=(0, 1), sk=0.25, angle=0, n=30, inkw=1.6, hi=0.5))
    out.append(f'<rect x="0" y="474" width="600" height="140" fill="#D8D0C4"/>')
    out.append(strokes(D.nid(), "M 0 466 L 600 466 L 600 600 L 0 600 Z", (-40, 466, 600, 600), ["#B8B0A8", "#F2EEE8", "#8A8480"], 7, n=60, angle=20, length=(30, 90), width=(1, 3), opacity=(0.2, 0.4)))
    out.append(f'<rect x="0" y="466" width="600" height="140" fill="{D.lin([(0, "#000000", 0.25), (0.3, "#000000", 0.05), (1, "#000000", 0.2)])}"/>')
    # chess pieces on the mantel: the Red Queen and the White King
    out.append(chess_piece(D, 106, 456, 116, "queen", ("#F28A7A", "#C8322A", "#6A0E0E"), 8))
    out.append(chess_piece(D, 494, 456, 126, "king", ("#FFFFFF", "#F2EADA", "#A89A84"), 9))
    # lettering
    out.append(tx(300, 80, "THROUGH THE", CINZEL, 21, "#F2E2B8", ls=8, max_w=300))
    out.append(gilt(D, 300, 128, "Looking-Glass", SERIF_IT, 54, max_w=380, seed=10, deboss="#0E2424"))
    out.append(letters(D, 300, 506, "“…six impossible things", SERIF_IT, 34, "#3A2A30", ["#5A4048", "#2A1A20"], 11, max_w=440, wob=0.3))
    out.append(letters(D, 300, 538, "before breakfast.”", SERIF_IT, 34, "#3A2A30", ["#5A4048", "#2A1A20"], 12, max_w=440, wob=0.3))
    return finish_b(D, out, 13)


# ================================================================ 21. the wind in the willows — a plate from an illustrated edition
def willow(D, x, base, h, seed, pals=(("#C8DC8A", "#8AAE58", "#4A6A30"), ("#DCE8A0", "#A8C06A", "#5A7A3A"))):
    rnd = random.Random(seed)
    out = [taper(catmull([(x, base), (x - 6, base - h * 0.3), (x + 4, base - h * 0.5)], 5), h * 0.12, h * 0.07, "#5A4A3A")]
    out.append(taper(catmull([(x - 2, base - h * 0.42), (x - 26, base - h * 0.62), (x - 40, base - h * 0.7)], 5), h * 0.05, h * 0.02, "#5A4A3A"))
    out.append(taper(catmull([(x + 2, base - h * 0.45), (x + 24, base - h * 0.68), (x + 34, base - h * 0.78)], 5), h * 0.05, h * 0.02, "#5A4A3A"))
    out.append(dab_crown(D, x, base - h * 0.74, h * 0.48, h * 0.26, list(pals), seed, n=int(h * 0.9), size=(4, 8), inkw=0))
    for _ in range(int(h * 0.55)):
        sx = x + rnd.uniform(-h * 0.5, h * 0.5)
        sy = base - h * 0.74 + rnd.uniform(-h * 0.1, h * 0.2)
        L = rnd.uniform(h * 0.25, h * 0.6)
        c = rnd.choice([p_[rnd.randint(0, 2)] for p_ in pals])
        out.append(taper([(sx, sy), (sx + rnd.uniform(-4, 4), sy + L * 0.5), (sx + rnd.uniform(-8, 8), sy + L)], 3.2, 0.6, c, rnd.uniform(0.6, 0.95)))
    return "".join(out)


def rowing_boat(D, cx, wl, L, seed, hull=("#6A9AC8", "#2E5A8A", "#14304E")):
    """Clinker rowing boat side-on, moored; picnic hamper aboard, oars shipped."""
    def P_(x, y):
        return (cx + x * L / 2, wl + y * L / 2)
    out = []
    # reflection
    refl = [P_(-0.96, 0.02), P_(0.98, 0.02), P_(0.8, 0.16), P_(-0.8, 0.16)]
    out.append(f'<path d="{smooth_closed(refl)}" fill="{hull[1]}" opacity="0.35"/>')
    # hamper inside (drawn first, sits in the boat)
    hx, hy = P_(-0.15, -0.2)
    hamp = rect_pts(hx - 34, hy - 30, hx + 34, hy + 4, 8, seed, 0.4)
    out.append(painted(D, hamp, ("#F2D08A", "#C89A4A", "#7A5A22"), seed, sk=0.2, angle=0, n=12, inkw=1.4, hi=0.3))
    for k in range(5):
        out.append(f'<path d="M {hx - 34:.1f} {hy - 26 + k * 6:.1f} L {hx + 34:.1f} {hy - 26 + k * 6:.1f}" stroke="#8A6A2A" stroke-width="1" opacity="0.7"/>')
    for k in range(9):
        out.append(f'<path d="M {hx - 32 + k * 8:.1f} {hy - 30:.1f} L {hx - 32 + k * 8:.1f} {hy + 2:.1f}" stroke="#E8C070" stroke-width="1" opacity="0.6"/>')
    lid = [(hx - 36, hy - 30), (hx + 36, hy - 30), (hx + 46, hy - 58), (hx - 26, hy - 58)]
    out.append(painted(D, poly_pts(lid, 8, seed + 1, 0.4), ("#F2D08A", "#C89A4A", "#7A5A22"), seed + 1, sk=0.15, angle=-70, n=10, inkw=1.4, hi=0.3))
    cl = [(hx - 30, hy - 30), (hx - 20, hy - 42), (hx + 4, hy - 36), (hx + 20, hy - 44), (hx + 34, hy - 30)]
    from fall_gouache_a import mix as _mix
    cid = D.clip(f'<path d="{smooth_closed(cl)}"/>')
    out.append(f'<path d="{smooth_closed(cl)}" fill="#FFFFFF"/>')
    pat = D.pattern(8, 8, '<rect width="8" height="8" fill="#FFFFFF"/><rect width="4" height="8" fill="#D8382E" opacity="0.6"/><rect width="8" height="4" fill="#D8382E" opacity="0.6"/>')
    out.append(f'<path d="{smooth_closed(cl)}" fill="{pat}"/>')
    out.append(painted(D, rect_pts(hx + 6, hy - 64, hx + 14, hy - 34, 6, seed + 2, 0.2), ("#8AB878", "#3E7040", "#1A3A1E"), seed + 2, sk=0.25, angle=-90, n=4, inkw=1, hi=0.6))
    # oars shipped across
    out.append(taper([P_(-0.7, -0.24), P_(0.75, -0.3)], 4, 4, "#C8A070"))
    out.append(f'<path d="{blob(*P_(0.86, -0.32), 16, 5, seed, 0.1, 10, -4)}" fill="#C8A070" stroke="#6A4A2A" stroke-width="1"/>')
    # hull
    hullp = [P_(-1.0, -0.2), P_(-0.6, -0.16), P_(0, -0.15), P_(0.6, -0.18), P_(1.0, -0.3), P_(0.96, -0.14), P_(0.8, 0.0), P_(0.4, 0.08), P_(-0.4, 0.08), P_(-0.86, 0.0)]
    out.append(painted(D, hullp, hull, seed + 3, sdir=(0.2, 1), sk=0.15, angle=-2, n=30, inkw=1.6, hi=0.35))
    for k in range(3):
        t = 0.3 + k * 0.22
        pts = [(x, y * (1 - t) + (wl + 0.06 * L / 2) * t) for x, y in [P_(-0.98, -0.18), P_(0, -0.13), P_(0.98, -0.26)]]
        out.append(pline(pts, hull[2], 1.2, seed + k, 0.6, 1))
    out.append(taper([P_(-1.0, -0.21), P_(0, -0.165), P_(1.0, -0.31)], 5, 4, "#F6F0E2"))
    out.append(pline([P_(-0.98, -0.23), P_(0, -0.18), P_(0.98, -0.33)], INK, 1.2, seed, 0.6, 1))
    # painter rope to the bank
    out.append(pline([P_(-0.98, -0.2), (cx - L / 2 - 40, wl - 4), (cx - L / 2 - 80, wl - 26)], "#C8A878", 2, seed, 0.95, 1))
    return "".join(out)


def water_lily(D, x, y, r, seed, flower=False):
    out = [f'<path d="{blob(x, y, r, r * 0.38, seed, 0.06, 14)}" fill="#5A8A48"/>',
           f'<path d="M {x:.1f} {y:.1f} L {x + r * 0.9:.1f} {y - r * 0.1:.1f}" stroke="#2A4A22" stroke-width="1.2"/>',
           f'<path d="{blob(x - r * 0.2, y - r * 0.08, r * 0.6, r * 0.18, seed + 1, 0.1, 10)}" fill="#8AB870" opacity="0.6"/>']
    if flower:
        for k in range(7):
            a = math.radians(-160 + k * 23)
            out.append(f'<path d="{blob(x + math.cos(a) * r * 0.25, y - r * 0.2 + math.sin(a) * r * 0.15, r * 0.24, r * 0.1, seed + k, 0.1, 8, math.degrees(a))}" fill="#FFF0F2" stroke="#D8A0B0" stroke-width="0.8"/>')
        out.append(f'<circle cx="{x:.1f}" cy="{y - r * 0.24:.1f}" r="{r * 0.08:.1f}" fill="#F6C83A"/>')
    return "".join(out)


@design("the-wind-in-the-willows")
def wind_in_the_willows():
    D = Doc2("sbc-ww")
    out = [paper(D.nid(), "#F4ECD8", FLECK, 1)]
    out.append(tx(300, 82, "THE WIND IN THE WILLOWS", CINZEL, 21, "#4A5A2E", ls=5, max_w=430))
    px0, py0, px1, py1 = 72, 104, 528, 436
    out.append(f'<rect x="{px0 + 5}" y="{py0 + 7}" width="{px1 - px0}" height="{py1 - py0}" fill="#5A4A30" opacity="0.25"/>')
    cid = D.clip(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}"/>')
    sc = [sky(D, [(0, "#B8D8EA"), (0.6, "#EAF2E8"), (1, "#FFF6DC")], 2, 300, ["#FFFFFF", "#CDE4F0"], 30, y0=py0)]
    sc.append(puff_cloud(D, 200, 168, 150, 3, ("#FFFFFF", "#FBF8F0", "#D8E2E8")))
    sc.append(puff_cloud(D, 430, 150, 110, 4, ("#FFFFFF", "#FBF8F0", "#D8E2E8")))
    sc.append(hill(D, [(60, 262), (200, 250), (330, 258), (450, 244), (540, 254)], 330, ("#C8DCA0", "#9AC078", "#6A9058"), 5, inkw=0, n=30))
    sc.append(willow(D, 420, 290, 150, 6))
    sc.append(willow(D, 170, 284, 120, 7))
    sc.append(willow(D, 300, 276, 70, 8))
    sc.append(hill(D, [(60, 284), (200, 280), (330, 288), (450, 278), (540, 284)], 300, ("#A8C878", "#7AA858", "#4A7A3A"), 9, inkw=1, n=30))
    # the river, with the willows mirrored
    wy = 296
    sc.append(f'<rect x="{px0}" y="{wy}" width="{px1 - px0}" height="{py1 - wy}" fill="{D.lin([(0, "#9AC0A8"), (0.5, "#6A9A88"), (1, "#3E6A60")])}"/>')
    sc.append(f'<g transform="translate(0 {2 * wy}) scale(1 -1)" opacity="0.28">{willow(D, 420, 290, 150, 6)}{willow(D, 170, 284, 120, 7)}</g>')
    sc.append(strokes(D.nid(), f"M {px0} {wy} L {px1} {wy} L {px1} {py1} L {px0} {py1} Z", (px0 - 40, wy, px1, py1), ["#C8E2D0", "#4A7A6A", "#E8F2E0"], 10, n=70,
                      angle=0, length=(30, 100), width=(1.5, 4), opacity=(0.2, 0.45), curve=0.05))
    sc.append(wave_lines(11, (px0, wy + 10, px1, py1), ["#E8F4EC", "#A8C8B8"], 30, (12, 26), 1.6, 1.6, (0.4, 0.7)))
    for k, (x, y, r, f) in enumerate(((440, 404, 22, True), (480, 380, 16, False), (396, 420, 14, False), (500, 420, 18, False))):
        sc.append(water_lily(D, x, y, r, 12 + k, f))
    sc.append(rowing_boat(D, 300, 372, 220, 13))
    # near bank with reeds and a stake
    sc.append(hill(D, [(px0 - 10, 392), (110, 384), (150, 400), (190, 436)], 460, ("#9AC070", "#6A9A48", "#3A6A2A"), 14, inkw=1, n=20))
    sc.append(taper([(150, 396), (148, 352)], 7, 5, "#6A4A2A"))
    rnd = random.Random(15)
    for k in range(26):
        x = rnd.uniform(px0, 200)
        y = rnd.uniform(390, 440)
        sc.append(taper([(x, y), (x + rnd.uniform(-6, 6), y - rnd.uniform(30, 70))], 3, 0.8, rnd.choice(["#5A8A3A", "#8AB060", "#3E6A2A"])))
        if k % 5 == 0:
            sc.append(f'<path d="{blob(x + 2, y - 60, 3, 9, k, 0.1, 8)}" fill="#6A4A2A"/>')
    # a dragonfly over the water
    dx_, dy_ = 230, 318
    for sg in (-1, 1):
        sc.append(f'<path d="{blob(dx_ - 4, dy_ + sg * 7, 12, 3.4, 16 + sg, 0.1, 8, sg * 12)}" fill="#E8F6FF" opacity="0.8" stroke="#5A8AA0" stroke-width="0.7"/>')
        sc.append(f'<path d="{blob(dx_ + 4, dy_ + sg * 7, 11, 3, 17 + sg, 0.1, 8, -sg * 14)}" fill="#E8F6FF" opacity="0.8" stroke="#5A8AA0" stroke-width="0.7"/>')
    sc.append(taper([(dx_ - 4, dy_), (dx_ + 26, dy_ + 2)], 2.6, 1.4, "#2A7AA8"))
    sc.append(f'<circle cx="{dx_ - 6}" cy="{dy_}" r="3" fill="#2A5A80"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" fill="none" stroke="#3A3020" stroke-width="2"/>')
    out.append(f'<rect x="{px0 - 7}" y="{py0 - 7}" width="{px1 - px0 + 14}" height="{py1 - py0 + 14}" fill="none" stroke="#3A3020" stroke-width="0.9"/>')
    out.append(tx(300, 490, "“…simply messing about in boats.”", SERIF_IT, 34, "#2E4A2E", max_w=440))
    out.append(ruled(300, 528, "THE WATER RAT", "#7A5A3A", font=CINZEL, size=17, ls=5, line_w=34, gap=12, max_w=300))
    return finish_b(D, out, 18)


# ================================================================ 22. the velveteen rabbit — real isn't how you are made
def velveteen(D, cx, base, s, seed):
    """Spotted brown-and-white velveteen rabbit, sitting: thread whiskers, pink sateen ear linings, boot-button eyes."""
    def L(pts):
        return T(pts, cx, base, s)
    out = [cast(D, cx + 8 * s, base, 110 * s, 12 * s, strength=0.4, seed=seed)]
    cream = ("#FFF8EC", "#EFE2CC", "#A8927A")
    spot = "#9A6A44"

    def spotted(pts, sd, k, n=26):
        d = smooth_closed(pts)
        o = [painted(D, pts, cream, seed + k, sdir=sd, sk=0.18, angle=-60, n=n, cols=["#FFFFFF", "#D8C8B0", "#F6ECDA"], inkw=1.6, inkc="#6A4A30", hi=0.4)]
        cid = D.clip(f'<path d="{d}"/>')
        rnd = random.Random(seed + k)
        x0, y0, x1, y1 = bbox(pts)
        sp = []
        for _ in range(int((x1 - x0) * (y1 - y0) / 2200) + 2):
            sx, sy = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            r = rnd.uniform(10, 22) * s
            sp.append(f'<path d="{blob(sx, sy, r, r * 0.8, rnd.randint(0, 999), 0.25, 12)}" fill="{spot}" opacity="0.85"/>')
            sp.append(f'<path d="{blob(sx + 2, sy + 2, r * 0.7, r * 0.5, rnd.randint(0, 999), 0.25, 10)}" fill="#6A4428" opacity="0.4"/>')
        sp.append(f'<path d="{d}" fill="{D.rad([(0, "#FFFFFF", 0.2), (0.6, "#FFFFFF", 0), (1, "#3A2010", 0.35)], cx=0.35, cy=0.3, r=0.8)}"/>')
        o.append(f'<g {cid}>{"".join(sp)}</g>')
        o.append(ink(d, "#6A4A30", 1.6, seed + k, 2, 0.7))
        return "".join(o)
    # body
    body = L([(-60, -20), (-66, -70), (-50, -110), (-20, -128), (20, -128), (50, -110), (66, -70), (62, -20), (40, 0), (-40, 0)])
    out.append(spotted(body, (0.6, 0.6), 1, 50))
    out.append(pline(L([(0, -124), (2, -70), (0, -12)]), "#8A6A4A", 1.2, seed, 0.6, 1))
    out.append(f'<path d="{smooth_open(L([(0, -122), (2, -70), (0, -14)]))}" fill="none" stroke="#FFFFFF" stroke-width="1.2" stroke-dasharray="3 4" opacity="0.7"/>')
    # front paws
    for k, px in enumerate((-26, 28)):
        out.append(spotted(blob_pts(*L([(px, -48)])[0], 16 * s, 24 * s, seed + 10 + k, 0.08, 14), (0.5, 0.8), 10 + k, 10))
    # big hind feet with worn pads
    for k, px in enumerate((-50, 52)):
        fp = blob_pts(*L([(px, -10)])[0], 34 * s, 15 * s, seed + 20 + k, 0.06, 16, -8 if k == 0 else 8)
        out.append(spotted(fp, (0.4, 1), 20 + k, 10))
        out.append(f'<path d="{blob(*L([(px + (6 if k == 0 else -6), -10)])[0], 18 * s, 8 * s, seed + 30 + k, 0.1, 12)}" fill="#E8C8B8" stroke="#8A6A5A" stroke-width="1" stroke-dasharray="2 2"/>')
    # ears: one up, one flopped; lined with pink sateen
    for k, (base_, tip, w) in enumerate((((-16, -196), (-46, -296), 22), ((22, -190), (88, -238), 20))):
        ux, uy = tip[0] - base_[0], tip[1] - base_[1]
        Ln = math.hypot(ux, uy)
        nx, ny = -uy / Ln, ux / Ln
        ear, lin = [], []
        for i in range(9):
            t = i / 8
            ww = w * math.sin(math.pi * min(0.97, 0.12 + t * 0.88)) ** 0.6
            ear.append((base_[0] + ux * t + nx * ww, base_[1] + uy * t + ny * ww))
            lin.append((base_[0] + ux * t + nx * ww * 0.55, base_[1] + uy * t + ny * ww * 0.55))
        for i in range(8, -1, -1):
            t = i / 8
            ww = w * math.sin(math.pi * min(0.97, 0.12 + t * 0.88)) ** 0.6
            ear.append((base_[0] + ux * t - nx * ww, base_[1] + uy * t - ny * ww))
            lin.append((base_[0] + ux * t - nx * ww * 0.55, base_[1] + uy * t - ny * ww * 0.55))
        out.append(spotted(L(ear), (0.6, 0.6), 40 + k, 14))
        ld = smooth_closed(L(lin[:9][1:] + lin[9:][:-1]))
        out.append(f'<path d="{ld}" fill="{D.lin([(0, "#FFD8E0"), (0.5, "#F6A8BC"), (1, "#E890A8")], 0, 0, 1, 1)}"/>')
        out.append(taper(L([(base_[0] + ux * 0.25, base_[1] + uy * 0.25), (base_[0] + ux * 0.7, base_[1] + uy * 0.7)]), 3 * s, 1, "#FFFFFF", 0.7))
    # head
    head = L([(-58, -150), (-60, -184), (-40, -212), (0, -222), (40, -212), (60, -186), (56, -150), (30, -130), (-30, -130)])
    out.append(spotted(head, (0.6, 0.6), 50, 30))
    muz = blob_pts(*L([(0, -152)])[0], 30 * s, 20 * s, seed + 51, 0.06, 14)
    out.append(painted(D, muz, ("#FFFFFF", "#F6EEE0", "#C8B8A0"), seed + 51, sk=0.15, n=8, inkw=0, hi=0.4))
    # stitched nose and mouth
    nx_, ny_ = L([(0, -162)])[0]
    out.append(f'<path d="M {nx_ - 9 * s:.1f} {ny_ - 4 * s:.1f} L {nx_ + 9 * s:.1f} {ny_ - 4 * s:.1f} L {nx_:.1f} {ny_ + 6 * s:.1f} Z" fill="#D87A8A" stroke="#8A3A4A" stroke-width="1.2" stroke-linejoin="round"/>')
    out.append(pline(L([(0, -156), (0, -146), (-10, -140)]), "#6A3A3A", 1.6, seed, 0.9, 1))
    out.append(pline(L([(0, -146), (10, -140)]), "#6A3A3A", 1.6, seed + 1, 0.9, 1))
    # thread whiskers
    for sg in (-1, 1):
        for k in range(3):
            out.append(pline(L([(sg * 18, -152 + k * 5), (sg * 50, -160 + k * 10), (sg * 74, -166 + k * 16)]), "#4A3020", 1.2, seed + k, 0.8, 1))
    # boot-button eyes
    for k, ex in enumerate((-26, 26)):
        x_, y_ = L([(ex, -182)])[0]
        out.append(f'<circle cx="{x_:.1f}" cy="{y_:.1f}" r="{8.5 * s:.1f}" fill="#120A08"/><circle cx="{x_ - 3 * s:.1f}" cy="{y_ - 3 * s:.1f}" r="{2.8 * s:.1f}" fill="#FFFFFF"/>'
                   f'<circle cx="{x_ + 3 * s:.1f}" cy="{y_ + 3 * s:.1f}" r="{1.4 * s:.1f}" fill="#FFFFFF" opacity="0.5"/>')
    # a faded ribbon at the neck
    for sg in (-1, 1):
        out.append(painted(D, blob_pts(*L([(sg * 14, -128)])[0], 14 * s, 8 * s, seed + 60 + sg, 0.12, 10, sg * 20), ("#C8E0F0", "#8AB0D0", "#4A6A8A"), seed + 60 + sg, sk=0.2, n=4, inkw=1.2, hi=0.4))
        out.append(taper(L([(0, -126), (sg * 10, -112), (sg * 16, -98)]), 7 * s, 4 * s, "#8AB0D0"))
    out.append(f'<circle cx="{L([(0, -128)])[0][0]:.1f}" cy="{L([(0, -128)])[0][1]:.1f}" r="{6 * s:.1f}" fill="#6A90B8"/>')
    return "".join(out)


@design("the-velveteen-rabbit")
def velveteen_rabbit():
    D = Doc2("sbc-vr")
    out = [f'<rect width="600" height="600" fill="#F6E8E2"/>']
    for k in range(16):
        out.append(f'<rect x="{k * 40}" y="0" width="16" height="600" fill="#EAC8C8" opacity="0.55"/>')
    rnd = random.Random(1)
    for k in range(40):
        x, y = (k % 8) * 80 + 28 + (k // 8 % 2) * 40, (k // 8) * 90 + 40
        out.append(f'<circle cx="{x}" cy="{y}" r="3.4" fill="#D87A8A" opacity="0.6"/><path d="M {x - 2} {y + 3} q -4 3 -8 2" stroke="#8AAA8A" stroke-width="1.4" fill="none" opacity="0.6"/>')
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFFFFF", 0.3), (0.6, "#FFFFFF", 0), (1, "#5A3A3A", 0.3)], cy=0.45, r=0.75)}"/>')
    # patchwork quilt on the nursery floor
    qy = 420
    out.append(f'<path d="M -10 {qy} L 610 {qy} L 610 610 L -10 610 Z" fill="#E8D8C0"/>')
    cols = ["#E8A8A8", "#A8C8D8", "#F2D8A0", "#C8D8B0", "#F6F0E4", "#D8B8D8"]
    for i in range(-2, 12):
        for j in range(5):
            y0_, y1_ = qy + j * 40, qy + (j + 1) * 40
            def X(i_, y_):
                return 300 + (i_ * 60 - 300) * (1 + (y_ - qy) / 260)
            q = [(X(i, y0_), y0_), (X(i + 1, y0_), y0_), (X(i + 1, y1_), y1_), (X(i, y1_), y1_)]
            c = cols[(i * 2 + j * 3) % len(cols)]
            out.append(f'<path d="{pd(q)}" fill="{c}"/>')
            out.append(f'<path d="{pd(q)}" fill="none" stroke="#FFFFFF" stroke-width="1.4" stroke-dasharray="3 3" opacity="0.8"/>')
            if (i + j) % 3 == 0:
                cx_, cy_ = sum(p[0] for p in q) / 4, sum(p[1] for p in q) / 4
                out.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="4" fill="#FFFFFF" opacity="0.6"/>')
    out.append(f'<rect x="0" y="{qy}" width="600" height="190" fill="{D.lin([(0, "#3A2010", 0.25), (0.4, "#3A2010", 0), (1, "#3A2010", 0.2)])}"/>')
    # wooden blocks
    for k, (bx, by_, c) in enumerate(((112, 444, "#D85A4A"), (474, 450, "#4A8AC8"), (492, 404, "#E8B83A"))):
        sz = 46
        out.append(cast(D, bx + 6, by_ + sz / 2 + 2, sz * 0.7, 6, strength=0.4, seed=k))
        out.append(painted(D, rect_pts(bx - sz / 2, by_ - sz / 2, bx + sz / 2, by_ + sz / 2, 10, 20 + k, 0.4), ("#F6E2C0", "#E2C69A", "#9A7A50"), 20 + k, sk=0.15, n=8, inkw=1.4, hi=0.4))
        out.append(f'<path d="{pd([(bx - sz / 2, by_ - sz / 2), (bx - sz / 2 + 10, by_ - sz / 2 - 9), (bx + sz / 2 + 10, by_ - sz / 2 - 9), (bx + sz / 2, by_ - sz / 2)])}" fill="#F6E8D0" stroke="#9A7A50" stroke-width="1.2"/>')
        out.append(f'<path d="{pd([(bx + sz / 2, by_ - sz / 2), (bx + sz / 2 + 10, by_ - sz / 2 - 9), (bx + sz / 2 + 10, by_ + sz / 2 - 9), (bx + sz / 2, by_ + sz / 2)])}" fill="#C8A878" stroke="#9A7A50" stroke-width="1.2"/>')
        out.append(f'<path d="{hg.org_rect(bx - sz / 2 + 7, by_ - sz / 2 + 7, sz - 14, sz - 14, k, 0.3, 8, 2)}" fill="none" stroke="{c}" stroke-width="2.6"/>')
        if k == 0:
            out.append(p_star(bx, by_, 11, c))
        elif k == 1:
            out.append(f'<circle cx="{bx}" cy="{by_}" r="10" fill="{c}"/>')
        else:
            out.append(heart_shape(bx, by_ + 2, 11, c))
    out.append(velveteen(D, 300, 470, 1.0, 5))
    # lettering
    out.append(tx(300, 82, "MARGERY WILLIAMS · 1922", CINZEL, 17, "#8A4A5A", ls=5, max_w=360))
    out.append(letters(D, 300, 138, "The Velveteen Rabbit", SERIF_IT, 54, "#5A3A2A", ["#7A5038", "#3A2214"], 6, max_w=460,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, wob=0.4))
    lab = rect_pts(70, 474, 530, 556, 20, 30, 0.6)
    out.append(f'<path d="{smooth_closed(shift(lab, 3, 4))}" fill="#3A2010" opacity="0.2"/>')
    out.append(painted(D, lab, ("#FFFDF4", "#F6EEDC", "#C8B898"), 31, sk=0.06, angle=0, n=20, inkw=0, hi=0.1))
    out.append(f'<path d="{smooth_closed(rect_pts(78, 482, 522, 548, 20, 32, 0.4))}" fill="none" stroke="#C86A7A" stroke-width="1.6" stroke-dasharray="5 4"/>')
    out.append(letters(D, 300, 514, "\u201cReal isn\u2019t how you are made,\u201d", SERIF_IT, 34, "#5A2A3A", ["#7A3A4E", "#3A1424"], 7, max_w=420, wob=0.3))
    out.append(tx(300, 537, "SAID THE SKIN HORSE", CINZEL, 16, "#8A4A5A", ls=4, max_w=300))
    return finish_b(D, out, 8)


def p_star(cx, cy, r, col):
    from common import star_points
    return f'<polygon points="{star_points(cx, cy, r, r * 0.45)}" fill="{col}"/>'


def heart_shape(cx, cy, s, col):
    pts = []
    for i in range(30):
        t = i / 30 * 2 * math.pi
        pts.append((cx + 16 * math.sin(t) ** 3 * s / 16, cy - (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) * s / 16))
    return f'<path d="{smooth_closed(pts)}" fill="{col}"/>'


# ================================================================ 23. winnie-the-pooh — a bear, a blue balloon and the bees' tree
def teddy(D, cx, cy, s, seed, fur=("#F2D49A", "#D8A860", "#8A6030")):
    """A plain jointed teddy bear (no clothes), floating, one paw up holding a balloon string; soft watercolour."""
    def L(pts):
        return T(pts, cx, cy, s)
    out = []
    soft = dict(inkw=1.2, inkc="#8A6A40", inkop=0.5)
    # legs dangling
    for k, (px, ang) in enumerate(((-18, 8), (20, -6))):
        leg = blob_pts(*L([(px, 52)])[0], 15 * s, 26 * s, seed + k, 0.06, 14, ang)
        out.append(painted(D, leg, fur, seed + k, sdir=(0.6, 0.6), sk=0.18, angle=-80, n=12, **soft, hi=0.4))
        out.append(f'<path d="{blob(*L([(px + ang * 0.3, 72)])[0], 10 * s, 6 * s, seed + 5 + k, 0.08, 10)}" fill="#C8A47A" opacity="0.8"/>')
    # body
    body = blob_pts(*L([(0, 14)])[0], 38 * s, 46 * s, seed + 2, 0.05, 20)
    out.append(painted(D, body, fur, seed + 2, sdir=(0.7, 0.5), sk=0.18, angle=-70, n=30, **soft, hi=0.45))
    out.append(f'<path d="{blob(*L([(2, 20)])[0], 22 * s, 28 * s, seed + 3, 0.08, 14)}" fill="#FCE6B8" opacity="0.6"/>')
    # arm down and arm up holding the string
    out.append(painted(D, blob_pts(*L([(-34, 18)])[0], 11 * s, 24 * s, seed + 4, 0.08, 12, 20), fur, seed + 4, sk=0.2, n=8, **soft, hi=0.4))
    arm = L([(26, -10), (40, -30), (46, -54), (38, -58), (30, -36), (18, -18)])
    out.append(painted(D, arm, fur, seed + 5, sk=0.2, angle=-70, n=8, **soft, hi=0.4))
    # head with round ears and a pale muzzle
    for k, ex in enumerate((-26, 26)):
        ear = blob_pts(*L([(ex, -68)])[0], 13 * s, 12 * s, seed + 6 + k, 0.05, 12)
        out.append(painted(D, ear, fur, seed + 6 + k, sk=0.2, n=4, **soft, hi=0.3))
        out.append(f'<path d="{blob(*L([(ex, -67)])[0], 7 * s, 6 * s, seed + 8 + k, 0.08, 10)}" fill="#C8986A" opacity="0.6"/>')
    head = blob_pts(*L([(0, -46)])[0], 34 * s, 30 * s, seed + 10, 0.05, 18)
    out.append(painted(D, head, fur, seed + 10, sdir=(0.7, 0.5), sk=0.15, angle=-30, n=20, **soft, hi=0.45))
    out.append(f'<path d="{blob(*L([(-2, -36)])[0], 16 * s, 12 * s, seed + 11, 0.06, 12)}" fill="#FCEAC4"/>')
    nx_, ny_ = L([(-2, -40)])[0]
    out.append(f'<path d="{blob(nx_, ny_, 6 * s, 4.5 * s, seed + 12, 0.1, 10)}" fill="#5A3A22"/>')
    out.append(pline(L([(-2, -36), (-2, -31), (-7, -28)]), "#5A3A22", 1.2, seed, 0.8, 1))
    out.append(pline(L([(-2, -31), (3, -28)]), "#5A3A22", 1.2, seed + 1, 0.8, 1))
    for ex in (-14, 10):
        x_, y_ = L([(ex, -52)])[0]
        out.append(f'<circle cx="{x_:.1f}" cy="{y_:.1f}" r="{3.6 * s:.1f}" fill="#2A1A10"/><circle cx="{x_ - 1:.1f}" cy="{y_ - 1.2:.1f}" r="{1.1 * s:.1f}" fill="#FFFFFF"/>')
    out.append(f'<circle cx="{L([(-22, -40)])[0][0]:.1f}" cy="{L([(-22, -40)])[0][1]:.1f}" r="{6 * s:.1f}" fill="#F2A08A" opacity="0.35"/>')
    out.append(f'<circle cx="{L([(18, -40)])[0][0]:.1f}" cy="{L([(18, -40)])[0][1]:.1f}" r="{6 * s:.1f}" fill="#F2A08A" opacity="0.35"/>')
    # paw pad on the raised paw
    out.append(f'<path d="{blob(*L([(42, -56)])[0], 7 * s, 6 * s, seed + 13, 0.08, 10)}" fill="#C8A47A"/>')
    return "".join(out), L([(42, -60)])[0]


def bee_small(x, y, s, ang=0):
    def L(pts):
        return T(pts, x, y, s, False, ang)
    out = [f'<path d="{blob(*L([(-2, -7)])[0], 6 * s, 3.2 * s, int(x * 3), 0.1, 8, -30 + ang)}" fill="#FFFFFF" opacity="0.75" stroke="#8A9AA8" stroke-width="0.6"/>',
           f'<path d="{blob(*L([(4, -7)])[0], 5 * s, 3 * s, int(y * 3), 0.1, 8, 30 + ang)}" fill="#FFFFFF" opacity="0.75" stroke="#8A9AA8" stroke-width="0.6"/>',
           f'<path d="{blob(x, y, 7 * s, 4.6 * s, int(x + y), 0.05, 10, ang)}" fill="#F2B82A"/>']
    for dx in (-2, 2.4):
        a, b = L([(dx, -4.2)])[0], L([(dx, 4.2)])[0]
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#2A1A10" stroke-width="{1.6 * s:.1f}"/>')
    hx, hy = L([(-7, 0)])[0]
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{2.6 * s:.1f}" fill="#2A1A10"/>')
    return "".join(out)


@design("winnie-the-pooh")
def winnie_the_pooh():
    D = Doc2("sbc-wp")
    out = [paper(D.nid(), "#F8F2E4", FLECK, 1)]
    out.append(blooms(2, ["#B8D8E8", "#C8E0C0", "#F2E2B8"], 8, (60, 100, 540, 460), (100, 170), (0.14, 0.24)))
    # loose watercolour sky wash and the wood
    out.append(f'<path d="{blob(330, 220, 250, 150, 3, 0.12, 20)}" fill="#C8E2F0" opacity="0.55"/>')
    out.append(f'<path d="{blob(300, 420, 280, 90, 4, 0.12, 20)}" fill="#C8DCA8" opacity="0.6"/>')
    for k, (x, y, r) in enumerate(((470, 330, 50), (530, 300, 40), (420, 360, 36), (80, 360, 40))):
        out.append(dab_crown(D, x, y, r, r * 0.8, [("#C8E0A8", "#9AC080", "#6A9A5A")], 5 + k, n=40, size=(5, 10), inkw=0))
    # the big beech with the bees' hole
    tx_ = 140
    out.append(taper(catmull([(tx_ + 10, 470), (tx_, 380), (tx_ + 8, 300), (tx_ - 4, 220), (tx_ + 6, 180)], 6), 70, 36, "#B8A08A"))
    out.append(taper(catmull([(tx_ - 10, 470), (tx_ - 18, 380), (tx_ - 10, 280), (tx_ - 22, 180)], 6), 18, 8, "#8A7460", 0.5))
    out.append(taper(catmull([(tx_ + 26, 470), (tx_ + 22, 380), (tx_ + 28, 300)], 6), 10, 4, "#E8DCC8", 0.6))
    out.append(taper(catmull([(tx_ + 8, 250), (tx_ + 60, 222), (tx_ + 110, 206), (tx_ + 150, 200)], 6), 18, 6, "#B8A08A"))
    out.append(taper(catmull([(tx_ - 4, 230), (tx_ - 40, 200), (tx_ - 60, 180)], 6), 14, 5, "#B8A08A"))
    out.append(dab_crown(D, tx_ + 6, 190, 100, 58, [("#D2E6AA", "#9CC47A", "#5E8E4A"), ("#E2EEB8", "#B8D48A", "#7AA258")], 6, n=150, size=(7, 14), inkw=0))
    out.append(dab_crown(D, tx_ + 136, 196, 52, 30, [("#D2E6AA", "#9CC47A", "#5E8E4A")], 7, n=50, size=(6, 11), inkw=0))
    hx, hy = tx_ + 6, 290
    out.append(f'<path d="{blob(hx, hy, 13, 17, 8, 0.1, 12)}" fill="#3A2A1A"/>')
    out.append(f'<path d="{blob(hx, hy, 13, 17, 8, 0.1, 12)}" fill="none" stroke="#E8D8C0" stroke-width="2" opacity="0.6"/>')
    for k, (bx, by_, a) in enumerate(((hx + 34, hy - 20, -10), (hx + 56, hy + 8, 20), (hx + 20, hy + 30, -30), (hx + 80, hy - 30, 10), (hx + 100, hy + 20, 0))):
        out.append(bee_small(bx, by_, 1.25, a))
    out.append(f'<path d="M {hx + 14} {hy - 6} q 20 -20 40 -10 t 30 10 q 16 10 30 -6" stroke="#8A7A5A" stroke-width="1.2" fill="none" stroke-dasharray="2 4" opacity="0.7"/>')
    # meadow
    out.append(grass(9, (40, 440, 560, 490), ["#8AB070", "#B8D098", "#6A9A5A"], 160, (8, 18)))
    # honey pot at the foot of the tree
    px_, pb = 236, 474
    out.append(cast(D, px_ + 6, pb, 34, 6, strength=0.35, seed=10))
    pot = [(px_ - 22, pb), (px_ - 32, pb - 18), (px_ - 30, pb - 36), (px_ - 18, pb - 46), (px_ + 18, pb - 46), (px_ + 30, pb - 36), (px_ + 32, pb - 18), (px_ + 22, pb)]
    out.append(painted(D, pot, ("#F6E2B8", "#E2B870", "#9A6A2A"), 10, sdir=(1, 0.3), sk=0.2, angle=-90, n=12, inkw=1.2, inkc="#8A6A40", inkop=0.5, hi=0.45))
    out.append(painted(D, rect_pts(px_ - 16, pb - 56, px_ + 16, pb - 44, 6, 11, 0.3), ("#F6E2B8", "#E2B870", "#9A6A2A"), 11, sk=0.2, n=4, inkw=1.1, inkc="#8A6A40", hi=0.4))
    cover = [(px_ - 24, pb - 54), (px_ - 18, pb - 66), (px_, pb - 70), (px_ + 18, pb - 66), (px_ + 24, pb - 54), (px_ + 26, pb - 46), (px_ + 12, pb - 50), (px_ - 12, pb - 50), (px_ - 26, pb - 46)]
    out.append(painted(D, cover, ("#FFFDF4", "#F2E8D2", "#B8A88A"), 12, sk=0.12, n=6, inkw=1.1, inkc="#8A6A40", hi=0.3))
    out.append(f'<path d="M {px_ - 18} {pb - 52} Q {px_} {pb - 48} {px_ + 18} {pb - 52}" stroke="#A8442A" stroke-width="2" fill="none"/>')
    out.append(taper([(px_ + 26, pb - 36), (px_ + 30, pb - 22), (px_ + 29, pb - 14)], 5, 3.4, "#E8A830"))
    out.append(f'<circle cx="{px_ + 29}" cy="{pb - 13}" r="3" fill="#E8A830"/>')
    out.append(taper([(px_ - 16, pb - 34), (px_ - 18, pb - 14)], 4, 2, "#FFFFFF", 0.6))
    # the balloon and the bear
    bx_, by2 = 382, 168
    out.append(painted(D, blob_pts(bx_, by2, 54, 60, 11, 0.03, 22), ("#9AC8F0", "#4A8AD0", "#1E4A8A"), 11, sdir=(0.6, 0.7), sk=0.15, angle=-40, n=30, inkw=1.2, inkc="#2A5A9A", inkop=0.5, hi=0.5))
    out.append(taper([(bx_ - 26, by2 - 30), (bx_ - 34, by2 - 6)], 7, 3, "#FFFFFF", 0.7))
    out.append(f'<path d="{pd([(bx_ - 5, by2 + 58), (bx_ + 5, by2 + 58), (bx_ + 2, by2 + 64), (bx_ - 2, by2 + 64)])}" fill="#2A5A9A"/>')
    bear, hand = teddy(D, 430, 330, 1.05, 12)
    out.append(f'<path d="M {bx_} {by2 + 63} Q {bx_ + 30} {by2 + 100} {hand[0]:.1f} {hand[1]:.1f}" stroke="#6A6A7A" stroke-width="1.4" fill="none"/>')
    out.append(bear)
    # lettering, softly lettered
    out.append(letters(D, 300, 112, "Winnie-the-Pooh", SERIF_IT, 58, "#6A4A2A", ["#8A6238", "#4A3018", "#A87A48"], 13, max_w=420,
                       shadow="#F6DCA0", soff=(0.02, 0.035), angle=-40, wob=0.6))
    out.append(ruled(300, 528, "A. A. MILNE · 1926", "#6A7A4A", font=CINZEL, size=17, ls=5, line_w=40, gap=12, max_w=300))
    out.append(tx(300, 500, "THE HUNDRED ACRE WOOD", JOS, 17, "#8A6A40", ls=4, max_w=360))
    return finish_b(D, out, 14)


# ================================================================ 24. heidi — the Alm-Uncle's hut, the goats and the peaks
def goat(D, x, base, s, seed, pal, flip=False, head_down=False):
    def L(pts):
        return T(pts, x, base, s, flip)
    out = [cast(D, x, base + 1, 36 * s, 5 * s, strength=0.3, seed=seed)]
    for leg in ([(-26, -24), (-27, -12), (-26, 0)], [(-18, -24), (-16, -12), (-18, 0)], [(22, -24), (24, -12), (24, 0)], [(28, -24), (31, -12), (32, 0)]):
        out.append(taper(L(leg), 5 * s, 3.2 * s, pal[2] if leg[0][0] in (-18, 28) else pal[1]))
        fx, fy = L([leg[-1]])[0]
        out.append(f'<rect x="{fx - 2.6 * s:.1f}" y="{fy - 3 * s:.1f}" width="{5.2 * s:.1f}" height="{3.4 * s:.1f}" fill="#3A2A20"/>')
    body = L([(-36, -46), (-10, -50), (20, -48), (36, -42), (38, -30), (30, -22), (0, -20), (-28, -22), (-38, -30)])
    out.append(painted(D, body, pal, seed, sdir=(0.5, 0.8), sk=0.18, angle=-10, n=20, inkw=1.3, hi=0.4))
    if head_down:
        neck = L([(-30, -44), (-42, -40), (-50, -26), (-54, -14), (-46, -12), (-38, -28), (-30, -34)])
        head = L([(-46, -30), (-58, -20), (-64, -8), (-58, -4), (-50, -10), (-44, -18)])
        horn = L([(-50, -28), (-46, -38), (-38, -40)])
        beard = L([(-60, -6), (-62, 2)])
        eye = (-53, -20)
    else:
        neck = L([(-28, -42), (-40, -56), (-46, -62), (-54, -56), (-44, -44), (-34, -34)])
        head = L([(-44, -64), (-52, -66), (-62, -56), (-66, -48), (-60, -46), (-50, -52)])
        horn = L([(-48, -66), (-42, -76), (-32, -78)])
        beard = L([(-62, -48), (-60, -36)])
        eye = (-53, -58)
    out.append(painted(D, neck, pal, seed + 1, sk=0.18, n=8, inkw=1.2, hi=0.4))
    out.append(painted(D, head, pal, seed + 2, sk=0.18, n=6, inkw=1.2, hi=0.4))
    out.append(taper(horn, 4 * s, 1.4 * s, "#8A7A60"))
    out.append(taper(beard, 4 * s, 1.2 * s, pal[2]))
    ex, ey = L([eye])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.8 * s:.1f}" fill="#1A1008"/>')
    ear = L([(eye[0] + 6, eye[1] - 2), (eye[0] + 16, eye[1] + 2), (eye[0] + 8, eye[1] + 4)])
    out.append(f'<path d="{smooth_closed(ear)}" fill="{pal[1]}" stroke="{pal[2]}" stroke-width="1"/>')
    out.append(taper(L([(36, -42), (42, -50), (44, -54)]), 4 * s, 1.6 * s, pal[1]))
    # a little bell on a strap
    bx_, by_ = L([(-40, -38)])[0] if not head_down else L([(-46, -24)])[0]
    out.append(f'<path d="{blob(bx_, by_ + 4 * s, 3.6 * s, 4.4 * s, seed, 0.05, 10)}" fill="#D9A945" stroke="#7A5418" stroke-width="0.9"/>')
    return "".join(out)


def chalet(D, x, base, w, h, seed):
    out = []
    wall = rect_pts(x - w / 2, base - h, x + w / 2, base, 12, seed, 0.4)
    out.append(painted(D, wall, ("#B8804A", "#7A4A22", "#3A2010"), seed, sdir=(1, 0.2), sk=0.12, angle=0, n=30, inkw=1.4, hi=0.25))
    for k in range(1, int(h / 9)):
        out.append(f'<path d="M {x - w / 2 + 2:.1f} {base - k * 9:.1f} L {x + w / 2 - 2:.1f} {base - k * 9:.1f}" stroke="#4A2A12" stroke-width="1.2" opacity="0.6"/>')
    out.append(f'<rect x="{x - w / 2:.1f}" y="{base - h * 0.2:.1f}" width="{w:.1f}" height="{h * 0.2:.1f}" fill="#B8B0A0"/>')
    for k in range(int(w / 14)):
        out.append(f'<path d="{blob(x - w / 2 + 7 + k * 14, base - h * 0.1, 6, 4, seed + k, 0.2, 8)}" fill="#8A8478" opacity="0.6"/>')
    roof = [(x - w / 2 - 22, base - h + 6), (x, base - h - w * 0.36), (x + w / 2 + 22, base - h + 6), (x + w / 2 + 22, base - h + 14), (x, base - h - w * 0.36 + 10), (x - w / 2 - 22, base - h + 14)]
    out.append(painted(D, roof, ("#8A8478", "#5A5448", "#2A2620"), seed + 1, sk=0.15, angle=0, n=20, inkw=1.4, hi=0.3))
    for k in range(5):
        rx_ = x - w / 2 + 6 + k * w / 4.4
        out.append(f'<path d="{blob(rx_, base - h - w * 0.14 + abs(rx_ - x) * 0.36 - 6, 5, 3.5, seed + k, 0.2, 8)}" fill="#9A9488"/>')
    # windows with red geraniums in boxes
    for k, wx in enumerate((x - w * 0.24, x + w * 0.24)):
        wy = base - h * 0.62
        out.append(f'<rect x="{wx - 11:.1f}" y="{wy - 14:.1f}" width="22" height="22" fill="#F2E8D8"/><rect x="{wx - 8:.1f}" y="{wy - 11:.1f}" width="16" height="16" fill="#2A3A4A"/>')
        out.append(f'<path d="M {wx:.1f} {wy - 11:.1f} L {wx:.1f} {wy + 5:.1f} M {wx - 8:.1f} {wy - 3:.1f} L {wx + 8:.1f} {wy - 3:.1f}" stroke="#F2E8D8" stroke-width="1.6"/>')
        out.append(f'<rect x="{wx - 14:.1f}" y="{wy + 8:.1f}" width="28" height="7" fill="#5A3A1E"/>')
        rnd = random.Random(seed + k)
        for j in range(7):
            out.append(f'<circle cx="{wx - 12 + j * 4 + rnd.uniform(-1, 1):.1f}" cy="{wy + 6 + rnd.uniform(-3, 2):.1f}" r="3" fill="#D8282A"/>')
            out.append(f'<circle cx="{wx - 10 + j * 4:.1f}" cy="{wy + 9:.1f}" r="2.4" fill="#3E7A3A"/>')
    out.append(f'<path d="{hg.org_rect(x - 9, base - h * 0.48, 18, h * 0.48, seed, 0.3, 8, 1)}" fill="#4A2A12"/>')
    return "".join(out)


def edelweiss(D, x, y, r, seed):
    out = []
    for k in range(9):
        a = math.radians(k * 40 + seed * 7)
        out.append(f'<path d="{blob(x + math.cos(a) * r * 0.55, y + math.sin(a) * r * 0.55, r * 0.55, r * 0.2, seed + k, 0.12, 8, math.degrees(a))}" fill="#F6F4EC" stroke="#B8B8A8" stroke-width="0.8"/>')
    for k in range(5):
        out.append(f'<circle cx="{x + math.cos(k * 1.3) * r * 0.16:.1f}" cy="{y + math.sin(k * 1.3) * r * 0.16:.1f}" r="{r * 0.12:.1f}" fill="#E2D27A"/>')
    return "".join(out)


@design("heidi")
def heidi():
    D = Doc2("sbc-hd")
    out = [sky(D, [(0, "#6AA8E0"), (0.5, "#A8D0F0"), (1, "#E8F4F8")], 1, 600, ["#FFFFFF", "#8ABCE8"], 40)]
    out.append(puff_cloud(D, 470, 200, 140, 2))
    # the peaks, snow on the shoulders
    out.append(hill(D, ridge([(-20, 340), (60, 300), (130, 210), (190, 250), (260, 180), (330, 236), (400, 200), (470, 260), (540, 230), (620, 300)], 3, 8, 4), 640,
                    ("#C8D4E8", "#8A9AB8", "#5A6A8A"), 3, inkw=1, n=40))
    for (px, py, w) in ((130, 210, 34), (260, 180, 44), (400, 200, 36), (540, 230, 26)):
        out.append(f'<path d="{smooth_closed([(px - w, py + w * 0.9), (px - w * 0.4, py + w * 0.5), (px, py), (px + w * 0.5, py + w * 0.6), (px + w, py + w * 1.0), (px + w * 0.3, py + w * 0.8), (px - w * 0.2, py + w * 1.0)])}" fill="#FFFFFF" opacity="0.92"/>')
        out.append(f'<path d="{pd([(px, py), (px + w * 0.5, py + w * 0.6), (px + w, py + w * 1.0), (px + w * 0.3, py + w * 0.8)])}" fill="#C8D4E8" opacity="0.6"/>')
    out.append(mist(D, 340, 50, 4, "#FFFFFF", 0.6))
    from paint import conifer
    rnd = random.Random(5)
    out.append(hill(D, [(-20, 360), (120, 344), (260, 352), (400, 338), (620, 350)], 640, ("#8AB86A", "#5A8A48", "#2E5A2E"), 6, inkw=0, n=40))
    for k in range(18):
        x = rnd.uniform(-10, 610)
        out.append(conifer(x, 360 + rnd.uniform(-4, 10), rnd.uniform(30, 54), mix("#2E5A3A", "#4A7A4A", rnd.uniform(0, 0.5)), k, width=0.32))
    # the alpine meadow
    out.append(hill(D, [(-20, 400), (120, 384), (260, 392), (420, 376), (620, 392)], 640, ("#C8E28A", "#8AC05A", "#4A8A3A"), 7, inkw=1.2, n=80, lit="#F2FAC0"))
    out.append(chalet(D, 420, 392, 120, 66, 8))
    out.append(grass(9, (0, 420, 600, 600), ["#6AA048", "#A8D070", "#4A8A3A"], 260, (8, 20)))
    for k in range(70):
        x, y = rnd.uniform(0, 600), rnd.uniform(420, 600)
        c = rnd.choice(["#F6D02A", "#FFFFFF", "#7A6AD8", "#E8508A"])
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.6, 3.2):.1f}" fill="{c}" opacity="0.9"/>')
    # Little Swan and Little Bear, the white goat and the brown
    out.append(goat(D, 196, 486, 1.5, 10, ("#FFFFFF", "#ECE6DA", "#9A9080")))
    out.append(goat(D, 330, 456, 1.15, 11, ("#C8946A", "#8A5A34", "#4A2A14"), flip=True, head_down=True))
    # edelweiss and gentians in the foreground
    for k, (x, y) in enumerate(((80, 516), (110, 540), (500, 520))):
        out.append(edelweiss(D, x, y, 14, 20 + k))
    for k, (x, y) in enumerate(((530, 548), (470, 546), (60, 560))):
        out.append(f'<path d="{smooth_closed([(x - 6, y), (x - 9, y - 18), (x - 4, y - 24), (x, y - 18), (x + 4, y - 24), (x + 9, y - 18), (x + 6, y)])}" fill="#2A4AD0"/>')
        out.append(f'<path d="M {x} {y} L {x} {y + 10}" stroke="#3E7A3A" stroke-width="2"/>')
    # lettering
    out.append(letters(D, 300, 148, "Heidi", DMS, 110, "#B8242A", ["#D83A3A", "#8A1018"], 12, max_w=300,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-50, wob=0.4))
    out.append(tx(300, 186, "JOHANNA SPYRI · 1881", CINZEL, 18, "#1E3A6A", ls=5, max_w=330))
    return finish_b(D, out, 13)


# ================================================================ 25. robinson crusoe — one footprint on the shore
def footprint(D, cx, cy, L, ang, seed, sand=("#F6E2B8", "#E2C08A", "#9A7A4A")):
    """A bare human footprint pressed into wet sand (right foot), toes up; lit from the upper left."""
    def P_(pts):
        return T(pts, cx, cy, L / 100, False, ang)
    sole = P_([(-2, 46), (12, 42), (16, 26), (12, 8), (16, -10), (22, -26), (20, -40), (8, -46), (-8, -44), (-18, -34), (-18, -14), (-14, 6), (-16, 24), (-14, 40)])
    out = []
    d = smooth_closed(sole)
    out.append(f'<path d="{d}" fill="{sand[2]}" opacity="0.85"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = [f'<path d="{smooth_closed(shift(sole, 6, 7))}" fill="{sand[1]}"/>',
             f'<path d="{smooth_closed([(x * 0.7 + cx * 0.3 + 3, y * 0.7 + cy * 0.3 + 4) for x, y in sole])}" fill="{mix(sand[1], "#B8986A", 0.4)}" opacity="0.7"/>',
             f'<path d="{smooth_closed(shift(sole, 7, 9))}" fill="#7AA8B0" opacity="0.18"/>']
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(smooth_open(sole[6:13]), "#6A4A22", 2.2, seed, 1, 0.7))
    out.append(ink(smooth_open(sole[:6]), "#FFF8E8", 3, seed + 1, 1, 0.9))
    for k, (tx_, ty_, r) in enumerate(((8, -60, 9.5), (-6, -58, 7), (-16, -53, 6), (-24, -46, 5), (-29, -37, 4.2))):
        tp = blob_pts(*P_([(tx_, ty_)])[0], r * L / 100, r * 1.15 * L / 100, seed + k, 0.08, 12)
        out.append(f'<path d="{smooth_closed(tp)}" fill="{sand[1]}"/>')
        out.append(f'<path d="{smooth_closed(shift(tp, 1.2, 1.6))}" fill="{sand[2]}" opacity="0.45"/>')
        out.append(ink(smooth_open(tp[8:]), "#FFF6E0", 1.4, seed + k, 1, 0.8))
    return "".join(out)


def parrot(D, x, y, s, seed):
    """Crusoe's parrot: a green Amazon perched, facing right, yellow crown and a red wing flash; (x, y) = feet."""
    def L(pts):
        return T(pts, x, y, s)
    out = []
    green = ("#9AE07A", "#3E9A3A", "#1A5A22")
    tail = L([(-10, -10), (-26, 30), (-20, 34), (-4, 4)])
    out.append(painted(D, tail, green, seed, sk=0.15, angle=110, n=8, inkw=1.2, hi=0.3))
    body = L([(-16, -12), (-20, -40), (-10, -62), (8, -70), (20, -60), (22, -36), (12, -12), (-2, -4)])
    out.append(painted(D, body, green, seed + 1, sdir=(-0.6, 0.6), sk=0.15, angle=-80, n=22, inkw=1.4, hi=0.45))
    wing = L([(-18, -46), (-4, -56), (8, -44), (6, -20), (-8, -6), (-20, -18)])
    out.append(painted(D, wing, ("#7AC060", "#2E7A2E", "#123A16"), seed + 2, sk=0.15, angle=-70, n=12, inkw=1.2, hi=0.3))
    out.append(f'<path d="{smooth_closed(L([(-12, -40), (-2, -46), (0, -36), (-10, -32)]))}" fill="#E8302A"/>')
    for k in range(3):
        out.append(pline(L([(-14 + k * 6, -30), (-8 + k * 5, -10)]), "#123A16", 1.1, seed + k, 0.6, 1))
    head = blob_pts(*L([(12, -76)])[0], 14 * s, 13 * s, seed + 3, 0.05, 14)
    out.append(painted(D, head, green, seed + 3, sk=0.15, n=8, inkw=1.3, hi=0.45))
    out.append(f'<path d="{blob(*L([(10, -86)])[0], 9 * s, 5 * s, seed + 4, 0.1, 10)}" fill="#F6D82A"/>')
    beak = L([(22, -82), (32, -78), (34, -70), (28, -64), (22, -68)])
    out.append(painted(D, beak, ("#F2E2C8", "#C8B090", "#6A5A40"), seed + 5, sk=0.2, n=4, inkw=1.2, hi=0.5))
    ex, ey = L([(16, -78)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{4.2 * s:.1f}" fill="#FFFFFF"/><circle cx="{ex + 0.6:.1f}" cy="{ey:.1f}" r="{2.6 * s:.1f}" fill="#F2A01A"/><circle cx="{ex + 0.6:.1f}" cy="{ey:.1f}" r="{1.4 * s:.1f}" fill="#100804"/>')
    for fx in (-6, 6):
        out.append(taper(L([(fx, -6), (fx + 2, 2)]), 3 * s, 2.4 * s, "#8A8A8A"))
    return "".join(out)


@design("robinson-crusoe")
def robinson_crusoe():
    D = Doc2("sbc-rc")
    # surf at the top, wet sand shading to dry sand below
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#2AA0B0"), (0.22, "#5AC8C8"), (0.3, "#BFE6DA"), (0.36, "#E2CFA0"), (0.6, "#F0DCAE"), (1, "#F6E6C0")])}"/>']
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 170 L 0 170 Z", (-60, 0, 600, 170), ["#8AE0E0", "#1E8AA0", "#C8F2EE"], 2, n=60, angle=-2, length=(40, 140), width=(2, 6), opacity=(0.2, 0.45)))
    for k, (y, op) in enumerate(((150, 0.95), (186, 0.6), (214, 0.35))):
        pts = [(-20 + i * 40, y + math.sin(i * 0.8 + k) * 8 + k * 3) for i in range(17)]
        out.append(taper(pts, 6 - k, 4 - k * 0.8, "#FFFFFF", op))
        out.append(f'<path d="{smooth_open(pts)} L 620 {y - 40} L -20 {y - 40} Z" fill="#FFFFFF" opacity="{0.15 * (3 - k):.2f}"/>')
    out.append(specks(3, (0, 220, 600, 600), ["#C8A870", "#FFFFFF", "#B89060", "#E8C890"], 260, (0.6, 1.8), (0.3, 0.8)))
    rnd = random.Random(4)
    for k in range(6):
        x, y = rnd.uniform(80, 540), rnd.uniform(420, 520)
        out.append(f'<path d="{blob(x, y, 6, 4, k, 0.2, 10)}" fill="#FFF2E0" stroke="#C8A070" stroke-width="1"/>')
        out.append(f'<path d="M {x - 4} {y} q 4 -3 8 0" stroke="#C8A070" stroke-width="0.8" fill="none"/>')
    # palm fronds' shadows reaching in from the corner
    for k in range(6):
        a = math.radians(160 + k * 12)
        out.append(taper([(640, 240), (640 + math.cos(a) * 140, 240 + math.sin(a) * 80), (640 + math.cos(a) * 260, 240 + math.sin(a) * 140)], 30, 4, "#8A6A3A", 0.14))
    # the footprint
    out.append(footprint(D, 300, 316, 230, 12, 5))
    # driftwood with the parrot, the tally post
    dw = [(46, 420), (90, 404), (170, 400), (210, 410), (200, 422), (120, 426), (60, 432)]
    out.append(cast(D, 130, 432, 90, 8, strength=0.35, seed=6))
    out.append(painted(D, dw, ("#E8DCC8", "#B8A48A", "#6A5A48"), 6, sdir=(0.3, 1), sk=0.2, angle=-3, n=20, inkw=1.4, hi=0.5))
    for k in range(4):
        out.append(pline([(70 + k * 30, 412 + k), (100 + k * 30, 410)], "#7A6A58", 1, k, 0.6, 1))
    out.append(parrot(D, 120, 404, 1.1, 7))
    tpx = 500
    out.append(cast(D, tpx + 10, 412, 26, 6, strength=0.4, seed=8))
    out.append(painted(D, rect_pts(tpx - 10, 250, tpx + 10, 412, 14, 8, 0.5), ("#D8C0A0", "#A8865E", "#5A4028"), 8, sdir=(1, 0.2), sk=0.25, angle=-90, n=14, inkw=1.4, hi=0.4))
    for k in range(14):
        y = 264 + k * 9
        w = 12 if k % 7 == 6 else 7
        out.append(f'<path d="M {tpx - 10} {y} l {w} 0" stroke="#3A2414" stroke-width="2" stroke-linecap="round"/>')
    # lettering
    out.append(tx(300, 82, "DANIEL DEFOE · 1719", CINZEL, 17, "#0E4A5A", ls=5, max_w=330))
    out.append(letters(D, 300, 140, "Robinson Crusoe", DMS, 66, "#FFFFFF", ["#FFFFFF", "#E2F6F4"], 9, max_w=440,
                       shadow="#0E5A6A", soff=(0.02, 0.04), angle=-40, wob=0.4))
    out.append(tx(300, 500, "“…the print of a man’s naked foot", SERIF_IT, 32, "#6A3E1E", max_w=440))
    out.append(tx(300, 536, "on the shore…”", SERIF_IT, 32, "#6A3E1E", max_w=440))
    return finish_b(D, out, 10)


# ================================================================ 26. around the world in eighty days — the steamer label and the watch
def arc_label(cx, cy, r, s, font, size, fill, start_deg, ls=0, top=True, uid="a"):
    """Text along a circle via textPath (top=True reads clockwise over the top, else counter-clockwise under)."""
    if top:
        d = f"M {cx - r:.1f} {cy:.1f} A {r:.1f} {r:.1f} 0 0 1 {cx + r:.1f} {cy:.1f}"
    else:
        d = f"M {cx - r:.1f} {cy:.1f} A {r:.1f} {r:.1f} 0 0 0 {cx + r:.1f} {cy:.1f}"
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return (f'<path id="{uid}" d="{d}" fill="none"/>'
            f'<text {font} font-size="{size}" fill="{fill}"{lsa} text-anchor="middle"><textPath href="#{uid}" startOffset="{start_deg or 50}%">{esc(s)}</textPath></text>')


def soft_puffs(pts, s, seed, col="#E8E2DA"):
    rnd = random.Random(seed)
    out = []
    for i, (x, y) in enumerate(pts):
        r = (8 + i * 6) * s
        for j in range(3):
            out.append(f'<path d="{blob(x + rnd.uniform(-r, r) * 0.4, y + rnd.uniform(-r, r) * 0.3, r, r * 0.75, seed * 10 + i * 3 + j, 0.15, 10)}" fill="{col}" opacity="{0.5 - i * 0.08:.2f}"/>')
    return "".join(out)


def steamship(D, x, wl, s, seed):
    def L(pts):
        return T(pts, x, wl, s)
    out = []
    hull = L([(-110, -26), (96, -26), (120, -34), (108, -8), (92, 4), (-96, 4), (-112, -10)])
    out.append(painted(D, hull, ("#4A4A58", "#22222C", "#0A0A10"), seed, sk=0.15, angle=0, n=14, inkw=1.4, inkc="#000000", hi=0.3))
    out.append(f'<path d="{pd(L([(-108, -10), (110, -10), (106, -4), (-104, -4)]))}" fill="#B83A2A"/>')
    for k in range(12):
        px, py = L([(-90 + k * 15, -18)])[0]
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{2 * s:.1f}" fill="#FFE8A0"/>')
    sup = L([(-70, -26), (60, -26), (56, -46), (-64, -46)])
    out.append(painted(D, sup, ("#FFFFFF", "#F2EEE4", "#A8A49A"), seed + 1, sk=0.2, angle=0, n=8, inkw=1.2, hi=0.4))
    for k in range(9):
        px, py = L([(-56 + k * 13, -38)])[0]
        out.append(f'<rect x="{px - 2.5 * s:.1f}" y="{py - 3 * s:.1f}" width="{5 * s:.1f}" height="{5 * s:.1f}" fill="#3A4A5A"/>')
    for k, fx in enumerate((-24, 20)):
        fun = L([(fx - 11, -46), (fx + 11, -46), (fx + 9, -94), (fx - 9, -94)])
        out.append(painted(D, fun, ("#F2B07A", "#D8742A", "#7A3A10"), seed + 2 + k, sdir=(1, 0.2), sk=0.25, angle=-90, n=6, inkw=1.2, hi=0.4))
        out.append(f'<path d="{pd(L([(fx - 9, -94), (fx + 9, -94), (fx + 9, -84), (fx - 9, -84)]))}" fill="#1A1A20"/>')
        sx_, sy_ = L([(fx, -100)])[0]
        out.append(soft_puffs(L([(fx - 10, -108), (fx - 40, -122), (fx - 80, -130), (fx - 124, -128)]), s, seed + k))
    for mx in (-90, 84):
        a, b = L([(mx, -26)])[0], L([(mx, -110)])[0]
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#2A2A30" stroke-width="{2.4 * s:.1f}"/>')
    out.append(pline(L([(-120, -30), (-90, -110), (-24, -94), (20, -94), (84, -110), (122, -34)]), "#2A2A30", 1, seed, 0.6, 1))
    return "".join(out)


@design("around-the-world-in-eighty-days")
def around_the_world():
    D = Doc2("sbc-aw")
    # cognac leather of a travelling trunk with a stitched seam
    out = [cloth_bg(D, "#8A4A24", 1, weave=2, vign=0.55)]
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 600 L 0 600 Z", (-40, 0, 600, 600), ["#A85E30", "#5A2A10", "#B87040"], 2, n=200, angle=30, length=(20, 80), width=(2, 6), opacity=(0.1, 0.25)))
    out.append(f'<path d="M 0 40 L 600 40" stroke="#5A2A10" stroke-width="2" opacity="0.6"/><path d="M 0 46 L 600 46" stroke="#F2D8B0" stroke-width="2" stroke-dasharray="7 6" opacity="0.6"/>')
    out.append(f'<path d="M 0 560 L 600 560" stroke="#5A2A10" stroke-width="2" opacity="0.6"/><path d="M 0 554 L 600 554" stroke="#F2D8B0" stroke-width="2" stroke-dasharray="7 6" opacity="0.6"/>')
    cx, cy, R = 292, 296, 214
    # the label disc with a perforated edge
    edge = []
    for i in range(96):
        a = math.radians(i * 3.75)
        rr = R if i % 2 == 0 else R - 4
        edge.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    out.append(f'<path d="{pd(shift(edge, 6, 8))}" fill="#2A1006" opacity="0.4"/>')
    out.append(painted(D, edge, ("#FFFBEE", "#F4E8CC", "#C8B48A"), 2, sk=0.05, angle=0, n=40, inkw=1.2, hi=0.1))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R - 14}" fill="#9A2A24"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R - 14}" fill="{D.rad([(0, "#000000", 0), (0.8, "#000000", 0), (1, "#000000", 0.3)])}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R - 18}" fill="none" stroke="#F2D8A0" stroke-width="1.4"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R - 58}" fill="none" stroke="#F2D8A0" stroke-width="1.4"/>')
    out.append(arc_label(cx, cy, R - 44, "AROUND THE WORLD IN EIGHTY DAYS", JOS, 20, "#FFF2D0", 0, ls=2, top=True, uid="sbc-aw-arc1"))
    out.append(arc_label(cx, cy, R - 32, "LONDON · SUEZ · BOMBAY · HONG KONG", JOS, 16, "#F2D8A0", 38, ls=1.5, top=False, uid="sbc-aw-arc2"))
    for sg in (-1, 1):
        out.append(p_star(cx + sg * (R - 37), cy + 2, 7, "#F2D8A0"))
    # the painted vignette: a steamer at sunset
    ri = R - 62
    cid = D.clip(f'<circle cx="{cx}" cy="{cy}" r="{ri}"/>')
    sc = [sky(D, [(0, "#3A4A8A"), (0.4, "#C8789A"), (0.62, "#F6B070"), (0.72, "#FFE0A0")], 3, cy + 40, ["#F2B8A0", "#6A6AA8"], 30, y0=cy - ri)]
    sc.append(f'<circle cx="{cx - 50}" cy="{cy + 30}" r="30" fill="#FFF0C0"/>')
    sc.append(soft_glow(D, cx - 50, cy + 30, 120, "#FFE0A0", 0.5))
    sc.append(sea(D, cy + 38, cy + ri, [(0, "#3A5A8A"), (1, "#1A2A4A")], 4, ["#6A8AC0", "#0E1A30", "#F2C08A"], 40, ticks=["#F6C88A", "#A8C0E0"]))
    sc.append(f'<path d="M {cx - 90} {cy + 44} L {cx - 10} {cy + 44}" stroke="#FFE0A0" stroke-width="3" opacity="0.7"/>')
    sc.append(steamship(D, cx + 18, cy + 50, 0.9, 5))
    sc.append(bird_v(cx - 70, cy - 40, 8, "#3A2A40"))
    sc.append(bird_v(cx - 44, cy - 56, 6, "#3A2A40"))
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{ri}" fill="none" stroke="#3A1A10" stroke-width="2"/>')
    # Phileas Fogg's deadline: a quarter before nine
    out.append(f'<path d="M 430 536 Q 360 548 300 512" stroke="#C89A3A" stroke-width="3" fill="none" stroke-dasharray="4 2"/>')
    out.append(pocket_watch(D, 474, 470, 64, 6, hands=(8, 45)))
    return finish_b(D, out, 7)


# ================================================================ 27. twenty thousand leagues under the sea — through the Nautilus porthole
def squid(D, x, y, s, seed):
    """Giant squid drifting past: mantle with fins, a great eye, arms and two long tentacles with suckers."""
    def L(pts):
        return T(pts, x, y, s)
    pal = ("#E8907A", "#B8483A", "#5A1A18")
    out = []
    rnd = random.Random(seed)
    arms = [[(-8, 30), (-30, 80), (-70, 110), (-120, 104), (-150, 80)], [(0, 32), (-6, 90), (-40, 140), (-90, 160)], [(10, 30), (30, 90), (20, 140), (-10, 180)],
            [(-14, 26), (-60, 50), (-110, 50), (-150, 30), (-170, -4)], [(16, 26), (60, 70), (90, 120), (80, 160)]]
    for k, a in enumerate(arms):
        path = catmull(L(a), 6)
        out.append(taper(path, 16 * s, 3 * s, pal[1]))
        out.append(taper([(px - 2, py - 2) for px, py in path], 5 * s, 1 * s, pal[0], 0.6))
        for i in range(2, len(path) - 2, 2):
            px, py = path[i]
            out.append(f'<circle cx="{px + 4:.1f}" cy="{py + 4:.1f}" r="{max(1.4, 3.6 * s * (1 - i / len(path))):.1f}" fill="#F6D8C8" stroke="{pal[2]}" stroke-width="0.8"/>')
    mantle = L([(-26, 30), (-34, -20), (-30, -80), (-14, -150), (0, -180), (14, -150), (30, -80), (34, -20), (26, 30)])
    out.append(painted(D, mantle, pal, seed, sdir=(0.8, 0.4), sk=0.2, angle=-90, n=40, inkw=1.6, inkc=pal[2], hi=0.4))
    for sg in (-1, 1):
        fin = L([(0, -176), (sg * 34, -150), (sg * 50, -128), (sg * 20, -120)])
        out.append(painted(D, fin, pal, seed + sg, sk=0.2, n=6, inkw=1.2, inkc=pal[2], hi=0.3))
    for _ in range(40):
        px, py = L([(rnd.uniform(-26, 26), rnd.uniform(-150, 20))])[0]
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rnd.uniform(1, 2.6):.1f}" fill="{pal[2]}" opacity="0.5"/>')
    ex, ey = L([(-8, 10)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{14 * s:.1f}" fill="#F6E8C8" stroke="{pal[2]}" stroke-width="1.6"/>')
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{9 * s:.1f}" fill="#1A1A2A"/><circle cx="{ex - 3 * s:.1f}" cy="{ey - 3 * s:.1f}" r="{3 * s:.1f}" fill="#FFFFFF"/>')
    return "".join(out)


@design("twenty-thousand-leagues-under-the-sea")
def twenty_thousand_leagues():
    D = Doc2("sbc-tl")
    # riveted iron hull of the Nautilus' salon
    out = [f'<rect width="600" height="600" fill="#2E3A3E"/>']
    for k in range(5):
        y = k * 150
        out.append(f'<rect x="0" y="{y}" width="600" height="146" fill="{D.lin([(0, "#46565A"), (1, "#26302E")])}"/>')
        for j in range(16):
            out.append(f'<circle cx="{18 + j * 38}" cy="{y + 10}" r="4" fill="#5A6A6E" stroke="#1A2224" stroke-width="1"/>')
    cx, cy, R = 300, 276, 150
    # the view: deep water, light shafts, the giant squid, fish
    cid = D.clip(f'<circle cx="{cx}" cy="{cy}" r="{R}"/>')
    v = [f'<rect width="600" height="600" fill="{D.lin([(0, "#2A8AA8"), (0.5, "#145A78"), (1, "#062438")], 0, cy - R, 0, cy + R, "userSpaceOnUse")}"/>']
    for k in range(6):
        x0 = cx - 120 + k * 50
        v.append(f'<path d="M {x0} {cy - R} L {x0 + 30} {cy - R} L {x0 - 40} {cy + R} L {x0 - 90} {cy + R} Z" fill="#BFF2FF" opacity="0.07"/>')
    rnd = random.Random(3)
    for k in range(9):
        x = cx - 140 + k * 36
        h = rnd.uniform(80, 170)
        v.append(taper(catmull([(x, cy + R), (x + 10, cy + R - h * 0.4), (x - 6, cy + R - h * 0.7), (x + 8, cy + R - h)], 6), 9, 3, rnd.choice(["#2E6A4A", "#3E7A3A", "#1E5A40"]), 0.85))
    v.append(squid(D, cx + 60, cy - 30, 0.95, 4))
    for k in range(14):
        fx, fy = cx - 120 + rnd.uniform(0, 120), cy + rnd.uniform(-60, 90)
        v.append(f'<path d="{smooth_closed([(fx - 9, fy), (fx, fy - 4), (fx + 9, fy), (fx, fy + 4)])} M {fx - 9} {fy} l -6 -4 l 0 8 Z" fill="#C8E8F0" opacity="0.85"/>')
        v.append(f'<circle cx="{fx + 5:.1f}" cy="{fy - 1:.1f}" r="1" fill="#0A1A2A"/>')
    for _ in range(26):
        v.append(f'<circle cx="{cx + rnd.uniform(-R, R):.1f}" cy="{cy + rnd.uniform(-R, R):.1f}" r="{rnd.uniform(1.2, 4):.1f}" fill="none" stroke="#E8FAFF" stroke-width="1" opacity="0.6"/>')
    v.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{D.rad([(0, "#FFFFFF", 0), (0.7, "#000000", 0.05), (1, "#000814", 0.6)])}"/>')
    v.append(taper([(cx - 100, cy - 70), (cx - 70, cy - 112), (cx - 20, cy - 134)], 12, 3, "#FFFFFF", 0.25))
    out.append(f'<g {cid}>{"".join(v)}</g>')
    # brass porthole ring with bolts
    ring = smooth_closed(blob_pts(cx, cy, R + 36, R + 36, 1, 0.0, 48)) + " " + smooth_closed(blob_pts(cx, cy, R, R, 2, 0.0, 48)[::-1])
    out.append(f'<circle cx="{cx + 6}" cy="{cy + 10}" r="{R + 38}" fill="#000000" opacity="0.4"/>')
    out.append(f'<path d="{ring}" fill="{BRASS[1]}" fill-rule="evenodd"/>')
    out.append(f'<path d="{ring}" fill="{D.lin([(0, "#FFF0B0", 0.85), (0.5, "#C89A3A", 0), (1, "#4A2A08", 0.8)], 0, 0, 1, 1)}" fill-rule="evenodd"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R + 8}" fill="none" stroke="#6A4A14" stroke-width="2"/>')
    for k in range(16):
        a = math.radians(k * 22.5)
        bx, by = cx + math.cos(a) * (R + 22), cy + math.sin(a) * (R + 22)
        out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="6.5" fill="{BRASS[1]}" stroke="#4A2A08" stroke-width="1.2"/><circle cx="{bx - 1.6:.1f}" cy="{by - 1.6:.1f}" r="2.2" fill="#FFF2C0"/>')
    out.append(ink(smooth_closed(blob_pts(cx, cy, R + 36, R + 36, 1, 0.0, 48)), "#2A1A06", 1.8, 5, 1, 0.8))
    # engraved brass plate
    pl = rect_pts(110, 470, 490, 548, 20, 6, 0.4)
    out.append(painted(D, pl, BRASS, 6, sdir=(0.5, 0.8), sk=0.15, angle=0, n=20, inkw=1.6, hi=0.5))
    for x in (124, 476):
        out.append(f'<circle cx="{x}" cy="509" r="4.5" fill="{BRASS[2]}"/><path d="M {x - 3} 509 l 6 0" stroke="#FFF0B0" stroke-width="1"/>')
    out.append(f'<text x="300.6" y="503.8" text-anchor="middle" {SERIF_IT} font-size="{fit_size("Twenty Thousand Leagues", SERIF_IT, 34, 330)}" fill="#FFF4C8" opacity="0.7">Twenty Thousand Leagues</text>')
    out.append(tx(300, 502, "Twenty Thousand Leagues", SERIF_IT, 34, "#3A2408", max_w=330))
    out.append(tx(300, 532, "UNDER THE SEA · JULES VERNE", CINZEL, 17, "#3A2408", ls=3, max_w=320))
    out.append(tx(300, 92, "MOBILIS IN MOBILI", CINZEL, 20, "#D8C8A0", ls=8, max_w=320))
    return finish_b(D, out, 8, "#000000", 0.6)


# ================================================================ 28. the jungle book — a black panther on the moonlit bough
def panther(D, x, y, s, seed, rim="#9AC8FF"):
    """A black panther lying along a bough, head raised, one forepaw hanging, tail draped; faces left; y = top of bough."""
    def L(pts):
        return T(pts, x, y, s)
    col = "#0E0E16"
    out = []
    out.append(taper(catmull(L([(66, -10), (82, 20), (78, 60), (88, 96), (100, 104)]), 6), 13 * s, 6 * s, col))
    out.append(taper(catmull(L([(34, -10), (44, 14), (44, 30)]), 5), 16 * s, 11 * s, col))
    body = L([(-62, -6), (-60, -26), (-40, -38), (-6, -36), (30, -40), (56, -34), (72, -18), (70, -2), (40, 2), (-20, 2)])
    out.append(f'<path d="{smooth_closed(body)}" fill="{col}"/>')
    out.append(taper(catmull(L([(-48, -4), (-52, 24), (-50, 46)]), 5), 15 * s, 11 * s, col))
    out.append(f'<path d="{blob(*L([(-49, 50)])[0], 9 * s, 7 * s, seed, 0.1, 10)}" fill="{col}"/>')
    out.append(f'<path d="{blob(*L([(-80, -4)])[0], 16 * s, 7 * s, seed + 1, 0.1, 10)}" fill="{col}"/>')
    neck = L([(-58, -24), (-70, -40), (-80, -50), (-92, -42), (-80, -20), (-64, -8)])
    out.append(f'<path d="{smooth_closed(neck)}" fill="{col}"/>')
    head = L([(-74, -56), (-88, -66), (-104, -62), (-118, -50), (-120, -42), (-112, -36), (-96, -34), (-80, -38)])
    out.append(f'<path d="{smooth_closed(head)}" fill="{col}"/>')
    for e in ([(-80, -60), (-80, -74), (-90, -64)], [(-92, -64), (-96, -76), (-102, -64)]):
        out.append(f'<path d="{smooth_closed(L(e))}" fill="{col}"/>')
    # moonlight on the back, head and shoulder; faint rosettes in the black coat
    out.append(ink(smooth_open(L([(-118, -50), (-104, -62), (-88, -66), (-76, -58), (-62, -34), (-40, -38), (-6, -36), (30, -40), (56, -34), (72, -18)])), rim, 2.2 * s, seed, 1, 0.75))
    out.append(ink(smooth_open(L([(-60, -26), (-52, -6), (-52, 20)])), rim, 1.4 * s, seed + 1, 1, 0.4))
    rnd = random.Random(seed)
    for _ in range(26):
        px, py = L([(rnd.uniform(-50, 60), rnd.uniform(-32, -6))])[0]
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rnd.uniform(2.5, 4.5) * s:.1f}" fill="none" stroke="#2A2A3A" stroke-width="1.2" opacity="0.8"/>')
    for k, (ex, ey) in enumerate(((-102, -52), (-112, -50))):
        x_, y_ = L([(ex, ey)])[0]
        out.append(soft_glow(D, x_, y_, 9 * s, "#E8F27A", 0.6))
        out.append(f'<path d="{blob(x_, y_, 3.6 * s, 2.2 * s, seed + k, 0.05, 10, -10)}" fill="#E8F27A"/><path d="M {x_:.1f} {y_ - 2 * s:.1f} L {x_:.1f} {y_ + 2 * s:.1f}" stroke="#101008" stroke-width="1.4"/>')
    for k in range(3):
        out.append(pline(L([(-114, -40 + k * 2), (-136, -44 + k * 6)]), "#8A9AB8", 0.9, seed + k, 0.6, 1))
    return "".join(out)


@design("the-jungle-book")
def the_jungle_book():
    D = Doc2("sbc-jb")
    out = [sky(D, [(0, "#0A1E2A"), (0.5, "#14384A"), (1, "#0A2026")], 1, 600, ["#1E4A5A", "#08141A"], 40)]
    out.append(soft_glow(D, 488, 268, 160, "#DDEEFF", 0.4))
    out.append(f'<circle cx="488" cy="268" r="40" fill="#F2F6E8"/>')
    for (cx_, cy_, r_) in ((478, 258, 8), (500, 282, 6), (490, 246, 4)):
        out.append(f'<circle cx="{cx_}" cy="{cy_}" r="{r_}" fill="#D8DCC8" opacity="0.6"/>')
    from paint import conifer
    rnd = random.Random(2)
    for k in range(10):
        x = rnd.uniform(-20, 620)
        out.append(dab_crown(D, x, rnd.uniform(380, 440), rnd.uniform(50, 90), rnd.uniform(40, 70), [("#1E4A50", "#14343A", "#0A2026")], 30 + k, n=40, size=(8, 14), inkw=0))
    # hanging lianas
    for k in range(7):
        x = 40 + k * 86 + rnd.uniform(-20, 20)
        out.append(pline([(x, -10), (x + rnd.uniform(-10, 10), 120), (x + rnd.uniform(-14, 14), 200 + rnd.uniform(0, 80))], "#0E2A2A", 2.4, k, 0.9, 1))
    # big foreground leaves
    for k, (x, y, Lg, W, a) in enumerate(((20, 600, 220, 50, -70), (40, 610, 180, 44, -40), (600, 600, 230, 50, -110), (590, 610, 170, 40, -140), (300, 640, 120, 36, -95))):
        out.append(leaf_simple(D, x, y, Lg, W, a, ("#2E6A5A", "#174A40", "#082420"), 40 + k, inkw=1.2, inkc="#041410"))
    # the bough
    bough = catmull([(-20, 352), (120, 340), (260, 344), (400, 334), (520, 340), (620, 330)], 6)
    out.append(taper(bough, 48, 30, "#2A2420"))
    out.append(taper([(x, y - 12) for x, y in bough], 12, 8, "#4A6A6A", 0.5))
    out.append(taper([(x, y + 10) for x, y in bough], 10, 6, "#0A0806", 0.6))
    for k in range(12):
        x = 20 + k * 50
        out.append(f'<path d="{blob(x, 330 + rnd.uniform(-4, 4), 14, 5, k, 0.3, 10)}" fill="#3E6A4A" opacity="0.8"/>')
    out.append(panther(D, 330, 326, 1.35, 7))
    # lettering
    out.append(tx(300, 82, "RUDYARD KIPLING · 1894", CINZEL, 17, "#BFD8E0", ls=5, max_w=360))
    out.append(letters(D, 300, 142, "The Jungle Book", DMS, 64, "#E8F0C8", ["#F6FAE0", "#C8D8A0"], 8, max_w=440,
                       shadow="#041014", soff=(0.02, 0.04), angle=-40, wob=0.4))
    out.append(letters(D, 300, 524, "“We be of one blood, ye and I”", SERIF_IT, 36, "#F2F6E0", ["#FFFFFF", "#D8E8C0"], 9, max_w=450,
                       shadow="#041014", soff=(0.02, 0.05), angle=-40, wob=0.3))
    return finish_b(D, out, 10, "#000000", 0.5)


# ================================================================ 29. walden — a page from a field journal
def tape(D, cx, cy, w, h, ang, col="#E8D8A8", seed=1):
    pts = rot([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2 + 2, cy), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2), (cx - w / 2 - 2, cy)], cx, cy, ang)
    return f'<path d="{smooth_closed(jitter(pts, seed, 0.8))}" fill="{col}" opacity="0.75"/>'


@design("walden")
def walden():
    D = Doc2("sbc-wd")
    out = [paper(D.nid(), "#F2EAD6", FLECK, 1)]
    for k in range(18):
        out.append(f'<path d="M 0 {86 + k * 30} L 600 {86 + k * 30}" stroke="#A8C0D0" stroke-width="0.9" opacity="0.45"/>')
    out.append(f'<path d="M 74 0 L 74 600" stroke="#D88A8A" stroke-width="1.2" opacity="0.5"/>')
    out.append(tx(300, 82, "HENRY DAVID THOREAU · 1854", CINZEL, 16, "#5A4A3A", ls=4, max_w=380))
    # the painted vignette, taped in
    vx0, vy0, vx1, vy1 = 92, 104, 508, 384
    vp = rect_pts(vx0, vy0, vx1, vy1, 18, 2, 1.2)
    out.append(f'<path d="{smooth_closed(shift(vp, 5, 7))}" fill="#3A2A1A" opacity="0.2"/>')
    out.append(f'<path d="{smooth_closed(vp)}" fill="#FBF6EA"/>')
    cid = D.clip(f'<path d="{smooth_closed(rect_pts(vx0 + 10, vy0 + 10, vx1 - 10, vy1 - 10, 18, 3, 1.4))}"/>')
    sc = [sky(D, [(0, "#C8D8E2"), (0.6, "#F2E2C8"), (1, "#F8D8A8")], 4, 300, ["#FFFFFF", "#E8C8A8"], 30, y0=vy0)]
    sc.append(soft_glow(D, 380, 250, 120, "#FFE0A0", 0.5))
    from paint import conifer
    rnd = random.Random(5)
    for k in range(16):
        x = vx0 + k * 28 + rnd.uniform(-8, 8)
        c = mix("#3E5A48", "#6A8A70", rnd.uniform(0, 0.5))
        sc.append(conifer(x, 274, rnd.uniform(50, 90), c, k, width=0.32, light=lt(c, 0.2)))
    for k, (x, y, r, pal) in enumerate(((150, 248, 34, ("#F2B060", "#D8742A", "#8A3A10")), (470, 244, 30, ("#E87A4A", "#C0442A", "#7A1E10")), (230, 256, 22, ("#F6D070", "#D8A030", "#8A6010")))):
        sc.append(taper([(x, 280), (x, y)], 5, 3, "#4A3020"))
        sc.append(dab_crown(D, x, y, r, r * 0.8, [pal], 20 + k, n=40, size=(4, 7), inkw=0))
    # the cabin: shingled, a brick chimney with smoke, one window
    cbx, cbb = 330, 284
    sc.append(painted(D, rect_pts(cbx - 34, cbb - 34, cbx + 34, cbb, 10, 6, 0.4), ("#C8A07A", "#8A6040", "#4A3020"), 6, sk=0.12, angle=0, n=12, inkw=1.2, hi=0.3))
    for k in range(4):
        sc.append(f'<path d="M {cbx - 33} {cbb - 6 - k * 8} L {cbx + 33} {cbb - 6 - k * 8}" stroke="#5A3A20" stroke-width="0.9" opacity="0.6"/>')
    sc.append(painted(D, [(cbx - 42, cbb - 32), (cbx, cbb - 60), (cbx + 42, cbb - 32)], ("#8A7A6A", "#5A4A3E", "#2A221C"), 7, sk=0.15, angle=0, n=8, inkw=1.2, hi=0.3))
    sc.append(f'<rect x="{cbx + 14}" y="{cbb - 64}" width="9" height="20" fill="#9A4A2A"/>')
    sc.append(smoke([(cbx + 18, cbb - 66), (cbx + 24, cbb - 90), (cbx + 12, cbb - 112), (cbx + 30, cbb - 136)], 5, 14, "#FFFFFF", 0.5))
    sc.append(f'<rect x="{cbx - 22}" y="{cbb - 24}" width="12" height="12" fill="#FFD27A"/><rect x="{cbx + 6}" y="{cbb - 28}" width="12" height="28" fill="#4A3020"/>')
    sc.append(f'<rect x="{vx0}" y="282" width="{vx1 - vx0}" height="110" fill="{D.lin([(0, "#8AA8B8"), (1, "#5A7A8A")])}"/>')
    sc.append(f'<g transform="translate(0 564) scale(1 -1)" opacity="0.3">' + "".join(conifer(vx0 + k * 28, 282, 60, "#3E5A48", k, width=0.32) for k in range(16)) + '</g>')
    sc.append(strokes(D.nid(), f"M {vx0} 282 L {vx1} 282 L {vx1} 392 L {vx0} 392 Z", (vx0 - 40, 282, vx1, 392), ["#C8DCE2", "#4A6A7A", "#F2DCC0"], 7, n=40, angle=0, length=(30, 90), width=(1.5, 3.5), opacity=(0.2, 0.45)))
    sc.append(mist(D, 290, 26, 8, "#FFFFFF", 0.65))
    # a loon on the still water
    lx, ly = 210, 330
    sc.append(f'<path d="{smooth_closed([(lx - 20, ly), (lx - 8, ly - 7), (lx + 10, ly - 6), (lx + 16, ly - 14), (lx + 22, ly - 14), (lx + 30, ly - 11), (lx + 22, ly - 9), (lx + 18, ly - 2), (lx + 6, ly + 2), (lx - 14, ly + 2)])}" fill="#1A1E22"/>')
    for k in range(5):
        sc.append(f'<circle cx="{lx - 10 + k * 5}" cy="{ly - 3}" r="0.9" fill="#FFFFFF"/>')
    sc.append(f'<path d="M {lx - 30} {ly + 4} L {lx + 34} {ly + 4}" stroke="#E8F2F4" stroke-width="1.2" opacity="0.7"/>')
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(tape(D, vx0 + 12, vy0 + 6, 70, 22, -35, "#E2D2A0", 1))
    out.append(tape(D, vx1 - 12, vy0 + 6, 70, 22, 35, "#C8D8C0", 2))
    out.append(tape(D, vx1 - 10, vy1 - 6, 70, 22, -30, "#E2D2A0", 3))
    # pressed leaves gathered on the walk
    from gouache import maple_leaf, oak as oak_leaf
    out.append(maple_leaf(70, 410, 30, "#D86A2A", "#8A3010", -24, 4))
    out.append(oak_leaf(532, 410, 28, "#C89A3A", "#7A5A18", 30))
    # the line, in the writer's own words
    out.append(letters(D, 300, 452, "I went to the woods", SERIF_IT, 42, "#3A3A2A", ["#4A4A3A", "#2A2A1A"], 9, max_w=380, wob=0.3))
    out.append(letters(D, 300, 494, "because I wished to", SERIF_IT, 42, "#3A3A2A", ["#4A4A3A", "#2A2A1A"], 10, max_w=380, wob=0.3))
    out.append(letters(D, 300, 536, "live deliberately…", SERIF_IT, 42, "#3A3A2A", ["#4A4A3A", "#2A2A1A"], 11, max_w=380, wob=0.3))
    return finish_b(D, out, 12)


def singing_bird(D, x, y, s, seed):
    """A small brown songbird (sparrow-like) on a twig, head lifted and beak open, singing; faces right; (x, y) = feet."""
    def L(pts):
        return T(pts, x, y, s, False, -10)
    out = []
    brown = ("#D8BC98", "#9A7A58", "#4A3824")
    tail = L([(-26, -16), (-48, 0), (-52, 8), (-44, 8), (-24, -8)])
    out.append(painted(D, tail, brown, seed, sk=0.15, angle=170, n=8, inkw=1.2, hi=0.3))
    for leg in ([(-4, -10), (-6, 0)], [(6, -10), (8, 0)]):
        out.append(taper(L(leg), 2.4 * s, 1.8 * s, "#6A4A30"))
    body = L([(-32, -18), (-24, -34), (-6, -42), (12, -44), (24, -40), (30, -28), (26, -14), (12, -6), (-8, -6), (-24, -10)])
    out.append(painted(D, body, brown, seed + 1, sdir=(0.5, 0.7), sk=0.15, angle=-20, n=24, inkw=1.4, hi=0.4))
    breast = L([(30, -30), (26, -16), (12, -8), (0, -10), (10, -22), (22, -34)])
    out.append(painted(D, breast, ("#FFE2C0", "#F2B888", "#B8784A"), seed + 2, sk=0.12, n=8, inkw=0, hi=0.45))
    rnd = random.Random(seed)
    for _ in range(9):
        px, py = L([(rnd.uniform(4, 24), rnd.uniform(-30, -12))])[0]
        out.append(f'<path d="M {px:.1f} {py:.1f} l 1.6 3" stroke="#7A4A2A" stroke-width="{1.3 * s:.1f}" stroke-linecap="round" opacity="0.7"/>')
    wing = L([(-26, -24), (-6, -38), (12, -34), (10, -20), (-10, -12), (-28, -16)])
    out.append(painted(D, wing, ("#C8A880", "#7A5A3A", "#3A2814"), seed + 3, sk=0.15, angle=-10, n=12, inkw=1.2, hi=0.35))
    for k in range(4):
        out.append(pline(L([(-20 + k * 7, -30 + k * 2), (-8 + k * 7, -16 + k)]), "#3A2814", 1, seed + k, 0.6, 1))
        out.append(pline(L([(-18 + k * 7, -31 + k * 2), (-6 + k * 7, -17 + k)]), "#E8D0B0", 0.8, seed + k, 0.5, 1))
    head = L([(16, -42), (18, -54), (28, -60), (38, -58), (43, -51), (38, -43), (28, -40)])
    out.append(painted(D, head, brown, seed + 4, sk=0.15, angle=-30, n=10, inkw=1.3, hi=0.45))
    out.append(f'<path d="{smooth_closed(L([(20, -54), (28, -59), (38, -57), (32, -54)]))}" fill="#7A5236" opacity="0.7"/>')
    out.append(f'<path d="{pd(L([(41, -56), (54, -63), (44, -53)]))}" fill="#4A3A28"/>')
    out.append(f'<path d="{pd(L([(42, -51), (53, -48), (42, -48)]))}" fill="#4A3A28"/>')
    ex, ey = L([(33, -52)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.4 * s:.1f}" fill="#100804"/><circle cx="{ex + 0.8 * s:.1f}" cy="{ey - 0.8 * s:.1f}" r="{0.8 * s:.1f}" fill="#FFFFFF"/>')
    out.append(pline(L([(28, -48), (35, -48), (40, -46)]), "#F2E2C8", 1.2, seed, 0.8, 1))
    # the song, curling out into the wind
    for k in range(3):
        sx, sy = L([(58 + k * 8, -60 - k * 6)])[0]
        r = (14 + k * 10) * s
        out.append(f'<path d="M {sx:.1f} {sy:.1f} q {r * 0.4:.1f} {-r * 0.45:.1f} {r:.1f} {-r * 0.2:.1f}" stroke="#7A5A3A" stroke-width="{2.4 - k * 0.5:.1f}" fill="none" opacity="{0.85 - k * 0.2:.2f}" stroke-linecap="round"/>')
    return "".join(out)


# ================================================================ 30. "hope" is the thing with feathers — a small bird singing in the gale
@design("hope-is-the-thing-with-feathers")
def hope_feathers():
    D = Doc2("sbc-hp")
    out = [paper(D.nid(), "#F4EEE2", FLECK, 1)]
    # a storm wash breaking to light behind the bird
    sd_ = smooth_closed(blob_pts(300, 330, 250, 190, 2, 0.14, 22))
    out.append(f'<path d="{sd_}" fill="{D.lin([(0, "#6A7A98"), (0.6, "#9AA8BC"), (1, "#C8CCD4")], 0, 0, 1, 1)}" opacity="0.6"/>')
    out.append(strokes(D.nid(), sd_, (40, 140, 560, 520), ["#5A6A88", "#8A98B0", "#C8D0DC", "#4A5A78"], 3, n=140, angle=-60, length=(30, 90), width=(3, 9), opacity=(0.12, 0.3), curve=0.2))
    out.append(soft_glow(D, 400, 250, 170, "#FFF0C8", 0.75))
    out.append(soft_glow(D, 400, 250, 70, "#FFFFFF", 0.6))
    for k in range(6):
        a_ = math.radians(-160 + k * 22)
        out.append(taper([(400, 250), (400 + math.cos(a_) * 230, 250 + math.sin(a_) * 230)], 22, 2, "#FFF6DC", 0.12))
    rnd = random.Random(5)
    for _ in range(70):
        x, y = rnd.uniform(70, 540), rnd.uniform(170, 470)
        out.append(f'<path d="M {x:.1f} {y:.1f} l -10 18" stroke="#4A5A78" stroke-width="1.3" opacity="{rnd.uniform(0.2, 0.45):.2f}"/>')
    # wind-tossed branch with blossoms
    br = catmull([(560, 410), (470, 388), (380, 380), (290, 384), (210, 398), (140, 420)], 6)
    out.append(taper(br, 14, 4, "#4A3428"))
    out.append(taper(catmull([(380, 376), (340, 340), (300, 322)], 5), 6, 2, "#4A3428"))
    out.append(taper(catmull([(250, 388), (220, 430), (196, 452)], 5), 5, 2, "#4A3428"))
    for k, (x, y, a) in enumerate(((300, 322, -150), (196, 452, 120), (140, 420, 170), (470, 386, -60), (340, 344, -110), (420, 380, 70))):
        out.append(leaf_simple(D, x, y, 40, 11, a - 20, LEAF, 10 + k, inkw=1))
    for k, (x, y) in enumerate(((310, 318), (200, 446), (150, 414), (480, 378), (268, 386))):
        for j in range(5):
            aa = math.radians(j * 72 + k * 20)
            out.append(f'<path d="{blob(x + math.cos(aa) * 6, y + math.sin(aa) * 6, 6.5, 4.5, k * 9 + j, 0.12, 8, math.degrees(aa))}" fill="#FFFFFF" stroke="#E8A8B8" stroke-width="0.8"/>')
        out.append(f'<circle cx="{x}" cy="{y}" r="2.6" fill="#F6C83A"/>')
    # petals and one small feather carried off by the gale
    for k in range(9):
        x, y = rnd.uniform(90, 300), rnd.uniform(200, 320)
        out.append(f'<path d="{blob(x, y, 5, 3, 40 + k, 0.15, 8, rnd.uniform(0, 180))}" fill="#FFFFFF" stroke="#E8A8B8" stroke-width="0.7"/>')
    fx, fy = 150, 250
    out.append(painted(D, rot([(fx - 4, fy), (fx - 7, fy - 20), (fx - 2, fy - 36), (fx + 5, fy - 34), (fx + 7, fy - 16), (fx + 4, fy)], fx, fy, -50),
                       ("#F2DCC0", "#C8A07A", "#7A5A3A"), 50, sk=0.12, angle=-50, n=8, inkw=1, hi=0.4))
    out.append(pline(rot([(fx, fy + 6), (fx, fy - 36)], fx, fy, -50), "#7A5A3A", 1, 51, 0.8, 1))
    # the little bird, singing into the wind
    bx, by = 356, 378
    out.append(singing_bird(D, bx, by, 1.9, 60))
    # lettering
    out.append(letters(D, 300, 116, "“Hope” is the thing", SERIF_IT, 54, "#3A4A6A", ["#4A5A80", "#2A3450"], 70, max_w=440,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, wob=0.5))
    out.append(letters(D, 300, 168, "with feathers –", SERIF_IT, 54, "#3A4A6A", ["#4A5A80", "#2A3450"], 71, max_w=440,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, wob=0.5))
    out.append(ruled(300, 530, "EMILY DICKINSON", "#7A5A3A", font=CINZEL, size=18, ls=6, line_w=40, gap=14, max_w=320))
    return finish_b(D, out, 72)


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())
    if not only:
        # the folder holds exactly this set: clear out artwork for slugs that were dropped
        from common import ROOT
        for f in (ROOT / COL).glob("*.svg"):
            if f.stem not in DESIGNS:
                f.unlink()


if __name__ == "__main__":
    build(sys.argv[1:] or None)
