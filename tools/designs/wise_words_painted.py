"""Wise Words, hand-painted (gouache / storybook) edition: 30 magnets of great thinkers and their words.

Each magnet pairs one short, genuinely famous, public-domain line (ancient philosophers in standard old
translations, authors who died long before 1955) with a rich painted illustration of its IDEA, never a portrait:
a Roman garden sundial for Carpe diem, a river with stepping stones for Heraclitus, a mountain path for Lao Tzu.
The thinker's name and dates run as a small engraved line. Typography is classical and engraved (Cinzel capitals,
Playfair italic, DM Serif), and every piece has its own layout: temple front, papyrus, almanac page, fresco panel,
seed packet, printer's device, illuminated page, hanging-scroll landscape, letter, flat lay...

Painted in the house gouache idiom (warm paper, layered washes with pooled edges, brush strokes following the
form, a warm brown pen line, soft light, grain on top). Colour story: marble and parchment creams, terracotta,
Pompeian red, ochre gold, olive and laurel greens, Aegean and lapis blues.

Run from tools/designs:  python3 wise_words_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ridge, ruled, shift, sky, soft_glow, specks, taper, catmull, steam_wisps)
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines, sea
from storybook_classics_painted import (Doc2, ell_pts, pd, T, shade_over, light_over, tx, gilt, gilt_fill, laurel, fleuron,
                                        flourish, candle, quill, inkwell, book3, rule_frame, stars_field, rose_bloom,
                                        leaf_simple, songbird, compass_rose, meander, bird_v, cloth_bg, marbled)
from italia_painted import olive_leaf, olive_branch, olive, cypress, umbrella_pine, lemon_it
from japan_painted import jpine, hanko
import holidays_gouache as hg

COL = "wise-words"
INK = "#3A2418"
FLECK = "#8A6A4A"

lt, dk = hg.lt, hg.dk

# (light, base, dark) gouache palettes
MARBLE = ("#FFFFFF", "#EEE8DC", "#A89E8E")
TRAVERTINE = ("#FBF0DA", "#E2CFA8", "#9A8460")
TERRACOTTA = ("#F0A47A", "#C8643A", "#76301A")
POMPEII = ("#E07A62", "#A8302A", "#5A1210")
OCHRE = ("#F8D488", "#DCA040", "#8E5E18")
GOLD = ("#FBE7A4", "#D9A945", "#8A6020")
BRONZE = ("#E8C08A", "#A8743A", "#5A3A16")
OLIVE = ("#C6CEA2", "#8A9858", "#46522A")
LAUREL = ("#9CC07A", "#4E7E3E", "#22401E")
AEGEAN = ("#7AB8E0", "#2E6EA8", "#123A66")
LAPIS = ("#5A72C0", "#22357E", "#0C1640")
PARCH = ("#FFF8E6", "#F0E2C2", "#C2A878")
WOOD = ("#C8925E", "#8E5A30", "#4E2E14")
DARKWOOD = ("#8A5A3A", "#4E2E1A", "#24140A")
STONE = ("#D8D2C6", "#A49C90", "#5E5850")
BRASS = ("#F6DC8A", "#C89A3A", "#7A5418")

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def finish_w(D, out, seed, color=INK, op=1.0):
    return finish(D, out, seed, color, op)


# ================================================================ toolkit
def byline(y, s, fill, size=18, ls=4, max_w=420, x=300, op=None):
    """The small engraved 'NAME · DATES' line."""
    return tx(x, y, s, CINZEL, size, fill, ls=ls, max_w=max_w, op=op)


def carved(D, x, y, s, font, size, fill, ls=0, max_w=460, anchor="middle", hi="#FFFFFF", sh="#2A1A0A", hop=0.55, sop=0.5):
    """Letters cut into stone: a dark shadow on the upper-left inner edge, a light lip on the lower-right."""
    fs = fit_size(s, font, size, max_w, ls)
    xx = x + ls / 2 if (ls and anchor == "middle") else x
    lsa = f' letter-spacing="{ls}"' if ls else ""

    def t(dx, dy, f, op=1):
        return f'<text x="{xx + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}" {font} font-size="{fs}"{lsa} fill="{f}" opacity="{op}">{esc(s)}</text>'
    k = max(0.8, fs * 0.03)
    return t(k, k, hi, hop) + t(-k * 0.6, -k * 0.6, sh, sop) + t(0, 0, fill)


def lines(D, x, y0, gap, rows, font, size, fill, max_w=440, ls=0, shadow=None, soff=(1.5, 2)):
    """Several centred lines that share ONE size (the largest that fits every row)."""
    fs = min(fit_size(r, font, size, max_w, ls) for r in rows)
    out = []
    for i, r in enumerate(rows):
        if shadow:
            out.append(tx(x + soff[0], y0 + i * gap + soff[1], r, font, fs, shadow, ls=ls, max_w=max_w + 50))
        out.append(tx(x, y0 + i * gap, r, font, fs, fill, ls=ls, max_w=max_w + 50))
    return "".join(out)


def gilt_lines(D, x, y0, gap, rows, font, size, max_w=440, ls=0, pal="gold", deboss="#1A0C04", seed=1, dop=0.6):
    fs = min(fit_size(r, font, size, max_w, ls) for r in rows)
    return "".join(gilt(D, x, y0 + i * gap, r, font, fs, ls=ls, max_w=max_w + 50, pal=pal, deboss=deboss, seed=seed + i, dop=dop)
                   for i, r in enumerate(rows))


def cyl(D, x0, x1, y0, y1, pal, light=-1, op=0.85):
    """Horizontal cylinder shading over a vertical band (columns, scroll rolls)."""
    if light < 0:
        stops = [(0, pal[1], op * 0.5), (0.18, pal[0], op), (0.45, pal[1], 0), (0.82, pal[2], op * 0.75), (1, dk(pal[2], 0.2), op)]
    else:
        stops = [(0, dk(pal[2], 0.2), op), (0.18, pal[2], op * 0.75), (0.55, pal[1], 0), (0.82, pal[0], op), (1, pal[1], op * 0.5)]
    g = D.lin(stops, x0, 0, x1, 0, "userSpaceOnUse")
    return g


# ---------------------------------------------------------------- hand-drawn Greek capitals (none of the fonts carry them)
_GREEK = {
    "Γ": (0.56, [[(0, 1), (0, 0), (0.56, 0)]]),
    "Ν": (0.66, [[(0, 1), (0, 0), (0.66, 1), (0.66, 0)]]),
    "Ι": (0.12, [[(0.06, 0), (0.06, 1)]]),
    "Σ": (0.62, [[(0.62, 0.02), (0, 0.02), (0.34, 0.5), (0, 0.98), (0.62, 0.98)]]),
    "Ε": (0.56, [[(0.56, 0), (0, 0), (0, 1), (0.56, 1)], [(0, 0.5), (0.44, 0.5)]]),
    "Α": (0.72, [[(0, 1), (0.36, 0), (0.72, 1)], [(0.15, 0.62), (0.57, 0.62)]]),
    "Υ": (0.7, [[(0, 0), (0.35, 0.48), (0.7, 0)], [(0.35, 0.48), (0.35, 1)]]),
    "Τ": (0.66, [[(0, 0), (0.66, 0)], [(0.33, 0), (0.33, 1)]]),
    "Π": (0.66, [[(0, 1), (0, 0), (0.66, 0), (0.66, 1)]]),
    "Η": (0.66, [[(0, 0), (0, 1)], [(0.66, 0), (0.66, 1)], [(0, 0.5), (0.66, 0.5)]]),
    "Κ": (0.62, [[(0, 0), (0, 1)], [(0.62, 0), (0.05, 0.55)], [(0.24, 0.38), (0.62, 1)]]),
    "Ρ": (0.56, [[(0, 1), (0, 0), (0.38, 0), (0.56, 0.12), (0.56, 0.36), (0.38, 0.5), (0, 0.5)]]),
    "Λ": (0.68, [[(0, 1), (0.34, 0), (0.68, 1)]]),
    "Μ": (0.8, [[(0, 1), (0, 0), (0.4, 0.75), (0.8, 0), (0.8, 1)]]),
}


def _round_glyph(ch):
    pts = [(0.36 + 0.36 * math.cos(math.radians(a)), 0.5 + 0.5 * math.sin(math.radians(a))) for a in range(0, 361, 15)]
    if ch == "Ο":
        return 0.72, [pts]
    if ch == "Θ":
        return 0.72, [pts, [(0.18, 0.5), (0.54, 0.5)]]
    if ch == "Ω":
        arc = [(0.38 + 0.36 * math.cos(math.radians(a)), 0.46 + 0.44 * math.sin(math.radians(a))) for a in range(130, 411, 14)]
        return 0.76, [[(0.0, 1.0), (0.24, 1.0)] + [arc[0]], arc, [arc[-1], (0.52, 1.0), (0.76, 1.0)]]
    return None


def greek(x, y, s, h, col, sw=None, ls=0.32, anchor="middle"):
    """Polylines for a Greek capital inscription; (x, y) = baseline; h = cap height. Returns (list of polylines, width)."""
    glyphs = []
    for ch in s:
        if ch == " ":
            glyphs.append((0.4, []))
            continue
        g = _round_glyph(ch) or _GREEK[ch]
        glyphs.append(g)
    W = sum(w for w, _ in glyphs) * h + ls * h * (len(glyphs) - 1)
    gx = x - W / 2 if anchor == "middle" else x
    polys = []
    for w, ps in glyphs:
        for p in ps:
            polys.append([(gx + px * h, y - h + py * h) for px, py in p])
        gx += w * h + ls * h
    return polys, W


def greek_carved(x, y, s, h, fill, hi="#FFF6E0", sh="#2A1608", sw=None):
    polys, W = greek(x, y, s, h, fill)
    sw = sw or h * 0.16
    out = []
    for dx, dy, c, w, op in ((sw * 0.25, sw * 0.25, hi, sw, 0.6), (-sw * 0.15, -sw * 0.15, sh, sw, 0.5), (0, 0, fill, sw * 0.85, 1)):
        for p in polys:
            out.append(f'<path d="{pd([(px + dx, py + dy) for px, py in p], False)}" fill="none" stroke="{c}" stroke-width="{w:.1f}" '
                       f'stroke-linecap="square" stroke-linejoin="miter" opacity="{op}"/>')
    return "".join(out)


# ---------------------------------------------------------------- shared painted pieces
def doric_column(D, cx, top, bottom, w, seed, pal=MARBLE, light=-1, flutes=8, cap=True, worn=0.0):
    """A fluted Doric column: shaft with a slight entasis, echinus and abacus, cylinder shading and flute lines."""
    rnd = random.Random(seed)
    w0, w1 = w, w * 0.8
    cap_h = w * 0.42 if cap else 0
    st, sb = top + cap_h, bottom
    L = [(cx - w0 / 2, sb), (cx - w0 * 0.505, sb - (sb - st) * 0.4), (cx - w1 / 2, st)]
    R = [(cx + w1 / 2, st), (cx + w0 * 0.505, sb - (sb - st) * 0.4), (cx + w0 / 2, sb)]
    shaft = L + R
    d = smooth_closed(jitter(shaft, seed, 0.4))
    out = [f'<path d="{d}" fill="{pal[1]}"/>']
    out.append(f'<path d="{d}" fill="{cyl(D, cx - w0 / 2, cx + w0 / 2, 0, 0, pal, light)}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    for k in range(1, flutes):
        t = k / flutes
        xb, xt = cx - w0 / 2 + w0 * t, cx - w1 / 2 + w1 * t
        side = (t - 0.5) * 2 * (-light)
        c = pal[2] if side > -0.2 else lt(pal[2], 0.3)
        inner.append(pline([(xb, sb), (xb + (xt - xb) * 0.6, sb - (sb - st) * 0.6), (xt, st)], c, 1.3, seed + k, 0.4 + 0.25 * max(0, side), 1))
        inner.append(pline([(xb + 1.6 * light * -1, sb), (xt + 1.6 * light * -1, st)], pal[0], 1.0, seed + k + 20, 0.35, 1))
    for _ in range(int((sb - st) / 7)):
        yy = rnd.uniform(st, sb)
        inner.append(f'<path d="M {cx + rnd.uniform(-w0 / 2, w0 / 2):.1f} {yy:.1f} l {rnd.uniform(-3, 3):.1f} {rnd.uniform(4, 14):.1f}" stroke="{pal[2]}" stroke-width="{rnd.uniform(0.6, 1.4):.1f}" opacity="{rnd.uniform(0.15, 0.35):.2f}"/>')
    if worn:
        for _ in range(int(worn * 6)):
            inner.append(f'<path d="{blob(cx + rnd.uniform(-w0 / 2, w0 / 2), rnd.uniform(st, sb), rnd.uniform(3, 8), rnd.uniform(2, 5), rnd.randint(1, 999), 0.3, 8)}" fill="{pal[2]}" opacity="0.3"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, INK, 1.3, seed, 1, 0.45))
    if cap:
        ech = [(cx - w1 / 2, st + 1), (cx - w * 0.62, top + cap_h * 0.42), (cx + w * 0.62, top + cap_h * 0.42), (cx + w1 / 2, st + 1)]
        out.append(painted(D, ech + [(cx, st + 3)], pal, seed + 3, sdir=(-light, 0.6), sk=0.18, angle=0, n=8, inkw=1.2, inkop=0.45, hi=0.4))
        ab = rect_pts(cx - w * 0.66, top, cx + w * 0.66, top + cap_h * 0.44, 10, seed + 4, 0.3)
        out.append(painted(D, ab, pal, seed + 5, sdir=(-light, 0.8), sk=0.15, angle=0, n=6, inkw=1.2, inkop=0.45, hi=0.4))
        out.append(f'<path d="M {cx - w * 0.6:.1f} {top + cap_h * 0.5:.1f} L {cx + w * 0.6:.1f} {top + cap_h * 0.5:.1f}" stroke="{pal[2]}" stroke-width="1.6" opacity="0.6"/>')
    return "".join(out)


def stone_block(D, x0, y0, x1, y1, pal, seed, light=(-0.6, -0.8), cracks=1, n=None, inkw=1.4):
    pts = rect_pts(x0, y0, x1, y1, 16, seed, 0.6)
    out = [painted(D, pts, pal, seed, sdir=(-light[0], -light[1]), sk=0.08, angle=0, n=n or int((x1 - x0) * (y1 - y0) / 260) + 6,
                   slen=(10, 40), sw=(1, 3), inkw=inkw, inkop=0.5, hi=0.3, hik=0.05)]
    rnd = random.Random(seed)
    for _ in range(cracks):
        cx_ = rnd.uniform(x0 + 10, x1 - 10)
        out.append(pline([(cx_, y0 + 2), (cx_ + rnd.uniform(-6, 6), (y0 + y1) / 2), (cx_ + rnd.uniform(-10, 10), y0 + (y1 - y0) * rnd.uniform(0.6, 0.95))],
                         pal[2], 1.0, seed + 7, 0.5, 1))
    out.append(specks(seed + 3, (x0 + 2, y0 + 2, x1 - 2, y1 - 2), [pal[2], pal[0]], int((x1 - x0) * (y1 - y0) / 500) + 4, (0.6, 1.6), (0.2, 0.5)))
    return "".join(out)


def scroll_roll(D, cx, cy, L, r, ang, seed, pal=PARCH, tag=None, knob=DARKWOOD):
    """A rolled papyrus / parchment scroll lying at an angle, with wooden end knobs and an optional tag."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    p0, p1 = (cx - ux * L / 2, cy - uy * L / 2), (cx + ux * L / 2, cy + uy * L / 2)
    body = [(p0[0] + nx * r, p0[1] + ny * r), (p1[0] + nx * r, p1[1] + ny * r), (p1[0] - nx * r, p1[1] - ny * r), (p0[0] - nx * r, p0[1] - ny * r)]
    out = [cast(D, cx + 6, cy + r * 0.9, L * 0.55, r * 0.5, strength=0.45, seed=seed)]
    d = smooth_closed(body)
    out.append(f'<path d="{pd(body)}" fill="{pal[1]}"/>')
    g = D.lin([(0, pal[0], 1), (0.35, pal[1], 1), (0.85, pal[2], 1), (1, dk(pal[2], 0.25), 1)],
              cx + nx * r, cy + ny * r, cx - nx * r, cy - ny * r, "userSpaceOnUse")
    g = D.lin([(0, dk(pal[2], 0.15)), (0.2, pal[2]), (0.55, pal[1]), (0.8, pal[0]), (1, pal[1])],
              cx + nx * r, cy + ny * r, cx - nx * r, cy - ny * r, "userSpaceOnUse")
    out.append(f'<path d="{pd(body)}" fill="{g}"/>')
    out.append(strokes(D.nid(), pd(body), bbox(body), [pal[0], pal[2]], seed, n=int(L / 4), angle=ang, length=(L * 0.1, L * 0.3), width=(0.5, 1.2), opacity=(0.2, 0.45)))
    # rolled end showing the spiral
    for p, sgn in ((p0, -1), (p1, 1)):
        e = ell_pts(p[0], p[1], r * 0.42, r, 0, 360, 20)
        e = [(p[0] + (x - p[0]) * ux * 1 + (y - p[1]) * 0, p[1] + (x - p[0]) * uy + (y - p[1])) for x, y in e]
        e = rot(ell_pts(p[0], p[1], r * 0.4, r, 0, 360, 20), p[0], p[1], ang)
        out.append(f'<path d="{smooth_closed(e)}" fill="{lt(pal[1], 0.2)}"/>')
        sp = [(p[0] + math.cos(t) * r * 0.08 * t * 0.4, p[1] + math.sin(t) * r * 0.08 * t) for t in [i * 0.6 for i in range(1, 14)]]
        out.append(pline(rot(sp, p[0], p[1], ang), pal[2], 1.0, seed, 0.6, 1))
        out.append(ink(smooth_closed(e), INK, 1.1, seed, 1, 0.55))
        if knob:
            kx, ky = p[0] + ux * sgn * r * 0.5, p[1] + uy * sgn * r * 0.5
            out.append(painted(D, blob_pts(kx, ky, r * 0.32, r * 0.42, seed + 3, 0.05, 12, ang), knob, seed + 4, sk=0.2, n=4, inkw=1, hi=0.5))
    out.append(ink(pd(body), INK, 1.3, seed + 1, 1, 0.5))
    if tag:
        tx_, ty_ = cx + ux * L * 0.15 + nx * r, cy + uy * L * 0.15 + ny * r
        tp = rot(rect_pts(tx_ - 10, ty_ + 2, tx_ + 10, ty_ + 26, 6, seed, 0.3), tx_, ty_, ang + 8)
        out.append(pline([(tx_, ty_ - 2), (tx_ + 1, ty_ + 4)], "#8A2A1A", 1.6, seed, 0.9, 1))
        out.append(painted(D, tp, tag, seed + 5, sk=0.15, n=4, inkw=1, hi=0.3))
    return "".join(out)


def oil_lamp(D, cx, base, s, seed, body=TERRACOTTA, lit=True, glow_r=200):
    """Greek terracotta oil lamp (lychnos): round body with a filling hole, a long nozzle to the right, ring handle."""
    out = []
    if lit:
        fx, fy = cx + 62 * s, base - 30 * s
        out.append(soft_glow(D, fx, fy - 20 * s, glow_r, "#FFB040", 0.55))
        out.append(soft_glow(D, fx, fy - 18 * s, glow_r * 0.35, "#FFE0A0", 0.6))
    out.append(cast(D, cx + 10 * s, base, 80 * s, 9 * s, strength=0.55, seed=seed))
    # ring handle (behind, left)
    hp = [(cx - 40 * s, base - 22 * s), (cx - 66 * s, base - 30 * s), (cx - 66 * s, base - 48 * s), (cx - 44 * s, base - 40 * s)]
    out.append(ink(smooth_open(hp), body[2], 9 * s, seed, 1, 1))
    out.append(ink(smooth_open(hp), body[1], 5 * s, seed + 1, 1, 1))
    # nozzle
    nz = [(cx + 20 * s, base - 30 * s), (cx + 56 * s, base - 34 * s), (cx + 70 * s, base - 30 * s), (cx + 72 * s, base - 22 * s), (cx + 58 * s, base - 16 * s), (cx + 22 * s, base - 10 * s)]
    out.append(painted(D, nz, body, seed + 2, sdir=(0.3, 1), sk=0.2, angle=0, n=10, inkw=1.6, hi=0.35))
    # body: squat disc
    bd = [(cx - 50 * s, base - 22 * s), (cx - 44 * s, base - 38 * s), (cx, base - 46 * s), (cx + 44 * s, base - 38 * s), (cx + 50 * s, base - 22 * s),
          (cx + 40 * s, base - 6 * s), (cx, base - 1 * s), (cx - 40 * s, base - 6 * s)]
    out.append(painted(D, bd, body, seed + 3, sdir=(0.6, 0.8), sk=0.18, angle=-10, n=26, inkw=1.8, hi=0.45))
    # discus (top) with a red-figure palmette band
    top = ell_pts(cx, base - 36 * s, 38 * s, 8 * s, 0, 360, 24)
    out.append(f'<path d="{smooth_closed(top)}" fill="{dk(body[1], 0.25)}"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, base - 36 * s, 26 * s, 5 * s, 0, 360, 20))}" fill="{body[2]}"/>')
    out.append(f'<circle cx="{cx - 4 * s:.1f}" cy="{base - 36 * s:.1f}" r="{3.6 * s:.1f}" fill="#1A0A04"/>')
    band = smooth_open(ell_pts(cx, base - 22 * s, 47 * s, 14 * s, 10, 170, 16))
    out.append(f'<path d="{band}" fill="none" stroke="#1A0E08" stroke-width="{7 * s:.1f}" opacity="0.85"/>')
    for k in range(9):
        a = math.radians(18 + k * 18)
        px, py = cx + math.cos(a) * 47 * s, base - 22 * s + math.sin(a) * 14 * s
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{1.8 * s:.1f}" fill="{body[0]}"/>')
    out.append(taper([(cx - 34 * s, base - 30 * s), (cx - 16 * s, base - 40 * s), (cx + 10 * s, base - 42 * s)], 3 * s, 1, "#FFE8CC", 0.6))
    if lit:
        fx, fy = cx + 66 * s, base - 31 * s
        out.append(f'<path d="M {fx:.1f} {fy - 34 * s:.1f} C {fx + 9 * s:.1f} {fy - 16 * s:.1f} {fx + 10 * s:.1f} {fy:.1f} {fx:.1f} {fy + 2 * s:.1f} C {fx - 10 * s:.1f} {fy:.1f} {fx - 7 * s:.1f} {fy - 16 * s:.1f} {fx:.1f} {fy - 34 * s:.1f} Z" fill="#FFA830"/>')
        out.append(f'<path d="M {fx:.1f} {fy - 22 * s:.1f} C {fx + 5 * s:.1f} {fy - 11 * s:.1f} {fx + 5 * s:.1f} {fy - 1 * s:.1f} {fx:.1f} {fy:.1f} C {fx - 5 * s:.1f} {fy - 1 * s:.1f} {fx - 5 * s:.1f} {fy - 11 * s:.1f} {fx:.1f} {fy - 22 * s:.1f} Z" fill="#FFF2C0"/>')
        out.append(f'<ellipse cx="{fx:.1f}" cy="{fy - 1:.1f}" rx="{3 * s:.1f}" ry="{4 * s:.1f}" fill="#5A7AE0" opacity="0.55"/>')
    return "".join(out)


def swallow(D, x, y, s, seed, ang=0, flip=False, glide=True):
    """Barn swallow in flight: glossy steel-blue back, rust throat, cream belly, long forked tail streamers."""
    def L(pts):
        return T(pts, x, y, s, flip, ang)
    back = ("#5A7AB8", "#1E2E5E", "#0A1028")
    out = []
    # far wing
    fw = L([(-2, -2), (-14, -26), (-34, -46), (-52, -58), (-40, -36), (-18, -10)])
    out.append(painted(D, fw, ("#3A4E80", "#14204A", "#060A1C"), seed, sk=0.12, angle=-130, n=10, inkw=1.0, inkc="#05060E", hi=0.2))
    # tail streamers
    for k, tip in enumerate(((-74, -10), (-72, 12))):
        tp = L([(-24, -3 + k * 4), (-46, -4 + k * 6), (tip[0], tip[1])])
        out.append(taper(tp, 7 * s, 0.6, back[1]))
    # body
    body = L([(-28, -4), (-10, -9), (8, -9), (20, -6), (27, -1), (20, 4), (6, 8), (-12, 7), (-28, 3)])
    out.append(painted(D, body, back, seed + 1, sdir=(0.2, 1), sk=0.15, angle=0, n=14, inkw=1.2, inkc="#05060E", hi=0.35))
    belly = L([(-20, 3), (-4, 7.5), (10, 7), (18, 3), (6, 1), (-12, 1)])
    out.append(f'<path d="{smooth_closed(belly)}" fill="#F6EEDC"/>')
    throat = L([(14, 0), (22, -2), (26, 1), (20, 5), (12, 5)])
    out.append(f'<path d="{smooth_closed(throat)}" fill="#C8542A"/>')
    out.append(f'<path d="{pd(L([(26, -2.5), (32, -0.5), (26, 1.2)]))}" fill="#14100C"/>')
    ex, ey = L([(21, -3.5)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.7 * s:.1f}" fill="#000"/><circle cx="{ex + 0.5 * s:.1f}" cy="{ey - 0.6 * s:.1f}" r="{0.55 * s:.1f}" fill="#FFF"/>')
    # near wing
    nw = L([(0, -4), (-6, 14), (-22, 38), (-44, 60), (-30, 30), (-14, 4)]) if not glide else L([(2, -2), (-10, 14), (-28, 34), (-52, 50), (-32, 22), (-14, 0)])
    out.append(painted(D, nw, back, seed + 2, sk=0.12, angle=130, n=12, inkw=1.0, inkc="#05060E", hi=0.35))
    for j in range(4):
        a, b = L([(-14 - j * 8, 6 + j * 8)])[0], L([(-24 - j * 8, 20 + j * 8)])[0]
        out.append(pline([a, b], "#6A86C0", 0.9, seed + j, 0.5, 1))
    return "".join(out)


# ================================================================ 1. carpe diem — a sundial in a Roman garden, morning
def sundial(D, cx, top, seed, R=96, h=150):
    """Stone sundial on a short fluted column: elliptical dial plate (seen from above at a slant) with hour lines
    and Roman numerals on its far half, a bronze gnomon and the morning shadow it casts."""
    out = []
    ry = R * 0.36
    sh_top, sh_bot = top + ry + 22, top + h
    # long morning shadow of the whole sundial across the lawn (sun low on the left)
    out.append(f'<path d="{smooth_closed([(cx - 10, sh_bot + 6), (cx + 120, sh_bot + 24), (cx + 250, sh_bot + 36), (cx + 260, sh_bot + 52), (cx + 110, sh_bot + 40), (cx - 6, sh_bot + 18)])}" fill="#2A3A14" opacity="0.28"/>')
    out.append(cast(D, cx + 10, sh_bot + 8, 80, 12, strength=0.4, seed=seed))
    sh = [(cx - 28, sh_top), (cx + 28, sh_top), (cx + 32, sh_bot - 18), (cx - 32, sh_bot - 18)]
    out.append(f'<path d="{pd(sh)}" fill="{TRAVERTINE[1]}"/>')
    out.append(f'<path d="{pd(sh)}" fill="{cyl(D, cx - 32, cx + 32, 0, 0, TRAVERTINE, -1, 0.95)}"/>')
    for k in range(1, 7):
        xx = cx - 28 + k * 8
        out.append(pline([(xx, sh_top + 4), (xx + (k - 3.5) * 0.6, sh_bot - 20)], TRAVERTINE[2], 1.3, seed + k, 0.5, 1))
        out.append(pline([(xx - 2, sh_top + 4), (xx - 2 + (k - 3.5) * 0.6, sh_bot - 20)], "#FFFFFF", 0.9, seed + k + 9, 0.35, 1))
    # ivy climbing the shaft
    rnd = random.Random(seed)
    iv = [(cx + 18, sh_bot - 18), (cx + 6, sh_bot - 40), (cx - 14, sh_bot - 58), (cx - 6, sh_top + 20)]
    out.append(pline(iv, "#4A5A22", 1.6, seed, 0.9, 1))
    for k in range(9):
        t = k / 8
        px = iv[0][0] + (iv[-1][0] - iv[0][0]) * t + rnd.uniform(-8, 8)
        py = iv[0][1] + (iv[-1][1] - iv[0][1]) * t
        out.append(leaf_simple(D, px, py, rnd.uniform(9, 13), rnd.uniform(5, 7), rnd.uniform(-160, -20), LAUREL, seed + 30 + k, vein=False, inkw=0.7))
    out.append(ink(pd(sh), INK, 1.3, seed, 1, 0.45))
    out.append(stone_block(D, cx - 46, sh_bot - 20, cx + 46, sh_bot - 4, TRAVERTINE, seed + 3, cracks=0))
    out.append(stone_block(D, cx - 58, sh_bot - 6, cx + 58, sh_bot + 10, TRAVERTINE, seed + 4, cracks=1))
    cap = [(cx - 38, sh_top - 2), (cx - 48, top + ry + 6), (cx + 48, top + ry + 6), (cx + 38, sh_top - 2), (cx, sh_top + 2)]
    out.append(painted(D, cap, TRAVERTINE, seed + 5, sdir=(1, 0.5), sk=0.2, angle=0, n=10, inkw=1.3, hi=0.4))
    # dial plate: thickness, then the top face
    edge = [(cx + R, top)] + ell_pts(cx, top + 11, R, ry, 0, 180, 20) + [(cx - R, top)]
    out.append(f'<path d="{pd(edge)}" fill="{TRAVERTINE[2]}"/>')
    out.append(f'<path d="{pd(edge)}" fill="{cyl(D, cx - R, cx + R, 0, 0, TRAVERTINE, -1, 0.7)}"/>')
    face = ell_pts(cx, top, R, ry, 0, 360, 36)[:-1]
    out.append(painted(D, face, ("#FFF8E8", "#EEE0C0", "#B8A27A"), seed + 6, sdir=(0.7, 0.6), sk=0.08, angle=0, n=30, inkw=1.6, hi=0.35))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, R * 0.9, ry * 0.9, 0, 360, 36))}" fill="none" stroke="{BRONZE[2]}" stroke-width="1.4" opacity="0.6"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, R * 0.64, ry * 0.64, 0, 360, 36))}" fill="none" stroke="{BRONZE[2]}" stroke-width="1.0" opacity="0.45"/>')
    nums = ["VI", "VII", "VIII", "IX", "X", "XI", "XII", "I", "II", "III", "IIII", "V", "VI"]
    hub = (cx, top + ry * 0.3)
    for i, n in enumerate(nums):
        a = math.radians(180 + i * 15)
        ex, ey = cx + math.cos(a) * R * 0.88, top + math.sin(a) * ry * 0.88
        out.append(f'<path d="M {hub[0]:.1f} {hub[1]:.1f} L {ex:.1f} {ey:.1f}" stroke="{BRONZE[2]}" stroke-width="1.0" opacity="0.45"/>')
        nx_, ny_ = cx + math.cos(a) * R * 0.77, top + math.sin(a) * ry * 0.77 + 3
        out.append(f'<text x="{nx_:.1f}" y="{ny_:.1f}" text-anchor="middle" {CINZEL} font-size="10" fill="#5A3A1A" transform="translate({nx_:.1f} {ny_:.1f}) scale(1 0.66) translate({-nx_:.1f} {-ny_:.1f})">{n}</text>')
    # gnomon shadow pointing toward VIII-IX (morning, sun in the east = right)... sun is on the left here, so shadow falls right
    sa = math.radians(180 + 9 * 15 + 3)
    out.append(f'<path d="{pd([(hub[0] - 2, hub[1]), (cx + math.cos(sa) * R * 0.86, top + math.sin(sa) * ry * 0.86), (hub[0] + 5, hub[1] + 1)])}" fill="#3A2A18" opacity="0.45"/>')
    far = (cx + 1, top - ry * 0.62)
    apex = (cx - 1, hub[1] - R * 0.5)
    gn = [(hub[0] - 3, hub[1] + 1), apex, (apex[0] + 4, apex[1] + 2), (far[0] + 3, far[1]), far]
    out.append(f'<path d="{pd([(hub[0] + 2, hub[1] + 2), (apex[0] + 5, apex[1] + 3), (far[0] + 5, far[1] + 1)])}" fill="{BRONZE[2]}"/>')
    out.append(painted(D, [(hub[0] - 3, hub[1] + 1), apex, (far[0], far[1])], BRONZE, seed + 7, sdir=(1, 0.4), sk=0.2, angle=-60, n=8, inkw=1.3, hi=0.5))
    out.append(pline([(apex[0] + 1, apex[1] + 3), (far[0] - 1, far[1] - 1)], "#FFE8B0", 1.6, seed, 0.8, 1))
    return "".join(out)


def pompeii_column(D, cx, top, bottom, w, seed):
    """Peristyle column as in Pompeii: white fluted stucco above, red-painted lower third, simple capital."""
    out = [doric_column(D, cx, top, bottom, w, seed, pal=("#FFFBF2", "#EFE6D6", "#AA9C86"), light=-1, flutes=5)]
    y0 = bottom - (bottom - top) * 0.36
    band = [(cx - w * 0.5 - 0.6, bottom), (cx - w * 0.51, y0), (cx + w * 0.51, y0), (cx + w * 0.5 + 0.6, bottom)]
    out.append(f'<path d="{pd(band)}" fill="#B8382A"/>')
    out.append(f'<path d="{pd(band)}" fill="{cyl(D, cx - w / 2, cx + w / 2, 0, 0, ("#E8705A", "#B8382A", "#6A1410"), -1, 0.9)}"/>')
    return "".join(out)


@design("carpe-diem")
def carpe_diem():
    D = Doc2("ww-cd")
    out = [sky(D, [(0, "#8EBCD8"), (0.45, "#CFE2E2"), (0.75, "#F8E8C6"), (1, "#FBE2B8")], 3, 600,
               ["#FFFFFF", "#F8E2C0", "#B8D4E0"], 50)]
    out.append(soft_glow(D, 110, 250, 260, "#FFF2C8", 0.8))
    out.append(blooms(4, ["#F2D2A0", "#C8DCE4"], 5, (0, 0, 600, 260)))
    out.append(puff_cloud(D, 470, 236, 120, 5, pal=("#FFFFFF", "#FBF2E8", "#D8C8C8"), rows=2))
    # trees standing behind the villa roof
    for k, (x, h) in enumerate(((52, 120), (84, 96), (520, 110), (552, 128))):
        out.append(cypress(D, x, 300, h, 70 + k, pal=("#7EA08A", "#4E7462", "#2A4A3E"), light=-1))
    out.append(umbrella_pine(D, 410, 290, 96, 8, pal=("#8AAA84", "#5E8264", "#365442"), trunk="#7A5A44", light=-1))
    out.append(umbrella_pine(D, 210, 290, 76, 9, pal=("#9AB894", "#6A8E70", "#42604C"), trunk="#7A5A44", light=-1))
    # the far side of the peristyle: tiled roof, Pompeian-red wall with panels, and a colonnade
    WT = 254
    out.append(f'<path d="{pd([(-10, WT), (610, WT), (610, 362), (-10, 362)])}" fill="#A8382C"/>')
    out.append(strokes(D.nid(), pd([(-10, WT), (610, WT), (610, 362), (-10, 362)]), (-40, WT, 610, 362), ["#C84A38", "#8A2A20", "#B84030"], 6,
                       n=90, angle=-85, length=(20, 60), width=(3, 8), opacity=(0.2, 0.45)))
    for k in range(5):
        x0 = 18 + k * 120
        out.append(f'<path d="{hg.org_rect(x0, 276, 84, 56, 7 + k, 0.4, 12, 1)}" fill="none" stroke="#F2C64A" stroke-width="1.8" opacity="0.8"/>')
        out.append(f'<path d="{hg.org_rect(x0 + 8, 284, 68, 40, 17 + k, 0.4, 12, 1)}" fill="#C8503C" opacity="0.6"/>')
        cxp = x0 + 42
        out.append(pline([(cxp - 16, 314), (cxp, 296), (cxp + 16, 314)], "#F2C64A", 1.4, k, 0.7, 1))
        out.append(f'<circle cx="{cxp}" cy="{304}" r="3" fill="#F2C64A" opacity="0.8"/>')
    out.append(f'<path d="M -10 338 L 610 338 L 610 364 L -10 364 Z" fill="#2A1814" opacity="0.85"/>')
    out.append(f'<path d="{pd([(-10, WT), (610, WT), (610, 300), (-10, 300)])}" fill="{D.lin([(0, "#1A0806", 0.6), (1, "#1A0806", 0)])}"/>')
    roof = [(-20, 236), (620, 236), (620, 256), (-20, 256)]
    out.append(painted(D, roof, TERRACOTTA, 8, sdir=(0, 1), sk=0.25, angle=-90, n=60, slen=(6, 14), sw=(2, 4), inkw=1.4, hi=0.4))
    for k in range(32):
        x = -10 + k * 20
        out.append(f'<path d="M {x} 238 q 10 -6 20 0" fill="none" stroke="{TERRACOTTA[2]}" stroke-width="1.6" opacity="0.7"/>')
        out.append(f'<path d="{pd([(x + 5, 256), (x + 10, 246), (x + 15, 256)])}" fill="{TERRACOTTA[0]}" opacity="0.9"/>')
    for k, x in enumerate((36, 132, 228, 324, 420, 516)):
        out.append(f'<path d="{pd([(x + 6, 364), (x + 40, 364), (x + 26, 262), (x + 8, 262)])}" fill="#3A1410" opacity="0.3"/>')
        out.append(pompeii_column(D, x, 256, 364, 20, 80 + k))
    # garden: lawn, clipped box borders, roses, a marble fountain basin
    lawn = [(-20, 362), (620, 362), (620, 600), (-20, 600)]
    out.append(f'<path d="{pd(lawn)}" fill="#86AE52"/>')
    out.append(strokes(D.nid(), pd(lawn), (-20, 362, 620, 600), ["#C2DA8A", "#4A7030", "#9AC064"], 10, n=260, angle=-80, length=(6, 16), width=(1, 2.4), opacity=(0.3, 0.6)))
    out.append(f'<path d="{pd(lawn)}" fill="{D.lin([(0, "#2A3A14", 0.25), (0.25, "#2A3A14", 0), (1, "#FFF2C0", 0.12)])}"/>')
    for k, (x0, x1, y) in enumerate(((-20, 220, 392), (330, 620, 392))):
        hd = rect_pts(x0, y - 18, x1, y + 6, 18, 30 + k, 1.4)
        out.append(painted(D, hd, ("#7AAE5E", "#3E6E36", "#1A3E1C"), 31 + k, sdir=(0.4, 1), sk=0.25, angle=-80, n=110, slen=(3, 8),
                           sw=(1.2, 2.6), inkw=1.1, inkop=0.45, hi=0.4))
        rnd = random.Random(33 + k)
        for _ in range(8):
            out.append(rose_bloom(D, rnd.uniform(x0 + 14, x1 - 14), y - 18 + rnd.uniform(-2, 4), rnd.uniform(5, 7), rnd.randint(1, 999),
                                  pal=rnd.choice([("#FFD0D8", "#F07A90", "#A83050"), ("#FFF4E8", "#F8E0D0", "#C8A090")])))
    # lemon trees in terracotta pots flanking the walk
    for k, (x, y, sc) in enumerate(((236, 394, 1.0), (364, 394, 1.0))):
        pot = [(x - 17 * sc, y - 34 * sc), (x + 17 * sc, y - 34 * sc), (x + 12 * sc, y), (x - 12 * sc, y)]
        out.append(cast(D, x + 14, y, 26, 5, strength=0.4, seed=k))
        out.append(painted(D, pot, TERRACOTTA, 40 + k, sdir=(0.8, 0.3), sk=0.22, n=10, inkw=1.2, hi=0.45))
        out.append(f'<path d="{pd([(x - 19, y - 36), (x + 19, y - 36), (x + 19, y - 29), (x - 19, y - 29)])}" fill="{TERRACOTTA[1]}"/>')
        out.append(pline([(x - 19, y - 29), (x + 19, y - 29)], TERRACOTTA[2], 1.4, k, 0.7, 1))
        out.append(taper([(x, y - 34), (x + 1, y - 62)], 4, 2.5, "#6A4A2A"))
        out.append(dab_crown(D, x, y - 84, 30, 28, [("#A8D07A", "#4A863E", "#1E4A22")], 50 + k, n=110, size=(3, 6), light=(-0.8, -0.5), inkw=1.0))
        rnd = random.Random(60 + k)
        for j in range(7):
            a_ = rnd.uniform(0, 6.28)
            out.append(lemon_it(D, x + math.cos(a_) * rnd.uniform(6, 24), y - 84 + math.sin(a_) * rnd.uniform(6, 20), 4.4, 60 + j + k * 9, leaf=False))
    # gravel path from the viewer to the colonnade
    path = [(250, 380), (350, 380), (470, 610), (130, 610)]
    out.append(painted(D, path, ("#F8EED8", "#E6D6B6", "#B4A07E"), 12, sdir=(0, 1), sk=0.04, angle=0, n=90, slen=(4, 12), sw=(1, 2.4), inkw=0, hi=0.2))
    out.append(specks(13, (150, 390, 460, 600), ["#9A8664", "#FFFFFF", "#C2AE88"], 220, (0.8, 2.2), (0.3, 0.8)))
    out.append(ink(smooth_open([(250, 380), (190, 490), (130, 610)]), "#6A7A3A", 1.6, 14, 1, 0.5))
    out.append(ink(smooth_open([(350, 380), (410, 490), (470, 610)]), "#6A7A3A", 1.6, 15, 1, 0.5))
    rnd = random.Random(140)
    for k in range(16):
        t = k / 15
        for sg, (x0, x1) in ((-1, (250, 130)), (1, (350, 470))):
            x = x0 + (x1 - x0) * t + sg * 8
            y = 386 + 224 * t
            if y > 470 and sg < 0 and x < 200:
                continue
            sz = 0.5 + 0.9 * t
            for j in range(5):
                out.append(taper([(x + j * 2 * sz - 4 * sz, y), (x + (j - 2) * 3 * sz, y - 14 * sz)], 2 * sz, 0.6, "#5E7A3A"))
                out.append(f'<ellipse cx="{x + (j - 2) * 3 * sz:.1f}" cy="{y - 15 * sz:.1f}" rx="{1.6 * sz:.1f}" ry="{4 * sz:.1f}" fill="{rnd.choice(["#9A7AD0", "#7A5AB8", "#B89AE0"])}"/>')
    # marble fountain basin on the left
    fx, fy = 120, 456
    out.append(cast(D, fx + 10, fy + 30, 92, 12, strength=0.35, seed=16))
    bowl = ell_pts(fx, fy, 84, 22, 0, 180, 18) + [(fx - 84, fy - 2)]
    out.append(painted(D, [(fx - 84, fy), (fx + 84, fy), (fx + 72, fy + 30), (fx - 72, fy + 30)], MARBLE, 17, sdir=(1, 0.3), sk=0.18, n=20, inkw=1.4, hi=0.4))
    out.append(f'<path d="{smooth_closed(ell_pts(fx, fy, 84, 20, 0, 360, 30))}" fill="#E8E2D6"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(fx, fy + 1, 76, 16, 0, 360, 30))}" fill="#6AA8C8"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(fx, fy + 1, 76, 16, 0, 360, 30))}" fill="{D.lin([(0, "#2A5A7A", 0.5), (1, "#BFE6F2", 0.5)])}"/>')
    out.append(wave_lines(18, (fx - 60, fy - 8, fx + 60, fy + 10), ["#FFFFFF", "#D8F0F8"], n=14, L=(10, 22), w=1.4, amp=1.5))
    out.append(ink(smooth_closed(ell_pts(fx, fy, 84, 20, 0, 360, 30)), INK, 1.3, 19, 1, 0.5))
    out.append(painted(D, rect_pts(fx - 7, fy - 40, fx + 7, fy, 6, 20, 0.3), MARBLE, 21, sk=0.2, n=4, inkw=1.1, hi=0.5))
    out.append(painted(D, ell_pts(fx, fy - 42, 20, 6, 0, 360, 16)[:-1], MARBLE, 22, sk=0.2, n=4, inkw=1.1, hi=0.5))
    for sg in (-1, 1):
        out.append(taper(catmull([(fx, fy - 52), (fx + sg * 16, fy - 66), (fx + sg * 34, fy - 40), (fx + sg * 44, fy - 4)], 5), 3.2, 1.6, "#E8F6FC", 0.85))
    out.append(taper([(fx, fy - 46), (fx + 1, fy - 70)], 4, 1.2, "#FFFFFF", 0.9))
    for k in range(6):
        out.append(sparkle(fx + random.Random(k).uniform(-50, 50), fy - random.Random(k + 9).uniform(0, 12), 3.5, "#FFFFFF", 0.9))
    # foreground: acanthus and flowers bottom-left
    for k, (x, y, a, L) in enumerate(((20, 600, -70, 70), (50, 600, -100, 62), (-4, 590, -40, 56), (80, 604, -120, 48))):
        out.append(leaf_simple(D, x, y, L, L * 0.28, a, ("#A8C87A", "#5E8E44", "#2A5222"), 40 + k, inkw=1.0))
    rnd = random.Random(15)
    for _ in range(24):
        x, y = rnd.uniform(0, 110), rnd.uniform(520, 590)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(2.2, 3.4):.1f}" fill="{rnd.choice(["#F6A8B8", "#FFFFFF", "#F6D25A"])}"/>')
    # the sundial
    out.append(sundial(D, 448, 418, 16, R=84, h=112))
    # a butterfly
    bx, by = 330, 420
    for sg in (-1, 1):
        out.append(painted(D, [(bx, by), (bx + sg * 14, by - 12), (bx + sg * 18, by - 2), (bx + sg * 6, by + 4)], ("#FFE08A", "#F2A62A", "#A8600E"), 90 + sg, sk=0.15, n=4, inkw=0.9, hi=0.4))
        out.append(painted(D, [(bx, by + 1), (bx + sg * 11, by + 6), (bx + sg * 8, by + 12), (bx + sg * 2, by + 6)], ("#FFE08A", "#F2A62A", "#A8600E"), 92 + sg, sk=0.15, n=3, inkw=0.9, hi=0.4))
    out.append(pline([(bx, by - 6), (bx, by + 8)], INK, 2, 93, 0.9, 1))
    # lettering
    out.append(letters(D, 300, 146, "Carpe diem", SERIF_IT, 118, "#8A3418", ["#6A2410", "#A8462A", "#C8643A"], 101, max_w=470,
                       shadow="#FFF4DC", angle=-35, inkc=None))
    out.append(ruled(300, 192, "SEIZE THE DAY", "#5A3A1A", font=CINZEL, size=21, ls=7, line_w=48, gap=16))
    out.append(f'<path d="{blob(232, 530, 140, 20, 5, 0.08, 18)}" fill="#F8F0DC" opacity="0.75"/>')
    out.append(tx(232, 537, "HORACE · 65–8 BC", CINZEL, 19, "#4A2A12", ls=5, max_w=270))
    return finish_w(D, out, 102)


# ================================================================ 2. know thyself — the temple front at Delphi
@design("know-thyself")
def know_thyself():
    D = Doc2("ww-kt")
    out = [sky(D, [(0, "#3E6EA8"), (0.45, "#8AB4D8"), (0.8, "#F2D8B0"), (1, "#F6CC98")], 3, 600, ["#FFFFFF", "#B8D0E8", "#6A94C8"], 40)]
    # the Phaedriades cliffs of Parnassus rising behind, glowing in late sun
    for k, (pts, sd) in enumerate((([(-20, 30), (30, 60), (70, 40), (120, 90), (150, 140), (170, 250), (-20, 250)], 1),
                                    ([(430, 250), (450, 140), (490, 80), (540, 50), (580, 70), (620, 40), (620, 250)], -1))):
        pts = ridge(pts, 3 + k, 8, 3)
        d = smooth_closed(pts)
        out.append(f'<path d="{d}" fill="#D49A74"/>')
        x0, y0, x1, y1 = bbox(pts)
        out.append(f'<path d="{d}" fill="{D.lin([(0, "#FFE2C0", 0.5), (1, "#8A5A48", 0.5)], 0.5 - sd * 0.5, 0, 0.5 + sd * 0.5, 0.3)}"/>')
        out.append(strokes(D.nid(), d, (x0, y0, x1, y1), ["#A86A50", "#FFE4C8", "#C88464", "#7A4A3A"], 5 + k, n=90, angle=-88, length=(16, 50), width=(1.2, 3.4), opacity=(0.25, 0.55)))
        out.append(f'<path d="{d}" fill="#9AB4D8" opacity="0.28"/>')
        out.append(ink(d, "#7A4A3A", 1.2, 6 + k, 1, 0.35))
    for k, (x, y) in enumerate(((60, 112), (520, 108), (96, 160))):
        out.append(bird_v(x, y, 6, "#3A2A30", 0.7))
    # interior of the cella: dark with the glow of the eternal fire
    out.append(f'<rect x="70" y="248" width="460" height="230" fill="#2A160E"/>')
    out.append(soft_glow(D, 300, 420, 190, "#FF9A3A", 0.55))
    out.append(soft_glow(D, 300, 430, 70, "#FFD890", 0.6))
    # back wall blocks (faint coursing) and the tripod over the fire
    for j in range(8):
        out.append(f'<path d="M 70 {262 + j * 28} L 530 {262 + j * 28}" stroke="#5A3220" stroke-width="1.2" opacity="0.45"/>')
    tx0 = 300
    for sg in (-1, 0, 1):
        out.append(taper([(tx0 + sg * 6, 400), (tx0 + sg * 26, 452)], 4, 3, "#C8903A"))
    out.append(painted(D, ell_pts(tx0, 398, 28, 9, 0, 360, 18)[:-1], ("#F6D28A", "#C8903A", "#7A5018"), 7, sk=0.2, n=6, inkw=1.2, hi=0.5))
    out.append(steam_wisps(tx0, 388, 120, 8, "#FFE8D0", 3, 18, 6, 0.4))
    # six Doric columns
    xs = [100 + i * 80 for i in range(6)]
    cid = D.clip('<rect x="70" y="248" width="460" height="230"/>')
    out.append(f'<g {cid}>' + "".join(f'<path d="{pd([(x + 26, 478), (x + 58, 478), (x + 70, 250), (x + 40, 250)])}" fill="#000" opacity="0.3"/>' for x in xs) + '</g>')
    for i, x in enumerate(xs):
        out.append(doric_column(D, x, 236, 474, 46, 20 + i, pal=("#FFFBF2", "#EADFC8", "#8E7E64"), light=-1, worn=1.0))
    # entablature: architrave (Greek inscription), frieze (triglyphs + the hero), cornice, pediment
    out.append(stone_block(D, 52, 196, 548, 238, ("#FFF6E2", "#EADCBE", "#A8946E"), 30, cracks=2))
    out.append(greek_carved(300, 228, "ΓΝΩΘΙ ΣΕΑΥΤΟΝ", 22, "#7A5A3A", hi="#FFFBEE", sh="#3A2410"))
    out.append(stone_block(D, 46, 126, 554, 196, ("#FFF4DC", "#E6D6B4", "#A08A62"), 31, cracks=2))
    for x in (60, 528):
        out.append(f'<path d="{hg.org_rect(x, 130, 14, 62, x, 0.3, 8, 1)}" fill="#D2C09A"/>')
        for j in range(1, 3):
            out.append(f'<path d="M {x + j * 4.6:.1f} 132 L {x + j * 4.6:.1f} 190" stroke="#8A7650" stroke-width="1.6"/>')
    out.append(carved(D, 300, 180, "KNOW THYSELF", CINZEL, 48, "#7A3A22", ls=5, max_w=440, hi="#FFF8E8", sh="#3A1A08"))
    cor = rect_pts(34, 114, 566, 130, 20, 32, 0.4)
    out.append(painted(D, cor, ("#FFFAEE", "#E8DCC0", "#9A8664"), 32, sdir=(0.2, 1), sk=0.25, angle=0, n=20, inkw=1.4, hi=0.5))
    for k in range(26):
        x = 44 + k * 20
        out.append(f'<rect x="{x}" y="128" width="10" height="5" fill="#8A7650" opacity="0.6"/>')
    ped = [(30, 116), (300, 46), (570, 116)]
    out.append(painted(D, ped, ("#FFF6E6", "#E8DABE", "#A08A6A"), 33, sdir=(0.3, 1), sk=0.12, angle=0, n=30, inkw=1.6, hi=0.4))
    tym = [(78, 110), (300, 62), (522, 110)]
    out.append(f'<path d="{pd(tym)}" fill="#C8B490" opacity="0.65"/>')
    out.append(f'<path d="{pd(tym)}" fill="{D.lin([(0, "#000", 0), (1, "#000", 0.22)])}"/>')
    # laurel wreath carved in the tympanum
    out.append(laurel(D, [(258, 96), (282, 76), (300, 72)], 9, ("#E8DCC0", "#B8A47E", "#7A6644"), 34, side=1, inkw=0.6))
    out.append(laurel(D, [(342, 96), (318, 76), (300, 72)], 9, ("#E8DCC0", "#B8A47E", "#7A6644"), 35, side=-1, inkw=0.6))
    out.append(f'<circle cx="300" cy="94" r="7" fill="#B8A47E"/><circle cx="300" cy="94" r="3.5" fill="#E8DCC0"/>')
    # stylobate steps
    for k, (y0, y1, x0, x1) in enumerate(((474, 500, 40, 560), (500, 528, 20, 580), (528, 600, 0, 600))):
        out.append(stone_block(D, x0, y0, x1, y1, ("#FFF2D8", "#E2CEA8", "#9A8460"), 40 + k, cracks=3, n=50))
        out.append(f'<path d="M {x0} {y1 - 3} L {x1} {y1 - 3} L {x1} {y1 + 6} L {x0} {y1 + 6} Z" fill="#5A4022" opacity="0.25"/>')
    out.append(grass(44, (10, 520, 120, 532), ["#7A9A4A", "#A8C070", "#5A7A3A"], n=24, h=(6, 14)))
    out.append(grass(45, (470, 494, 560, 504), ["#7A9A4A", "#A8C070", "#5A7A3A"], n=18, h=(6, 12)))
    out.append(byline(556, "THE DELPHIC MAXIM · TEMPLE OF APOLLO", "#4A2E14", size=18, ls=3, max_w=430))
    # a laurel branch hanging in from the left edge
    out.append(laurel(D, [(-10, 300), (30, 330), (56, 380), (64, 420)], 20, LAUREL, 50, side=1, inkw=0.9))
    return finish_w(D, out, 51)


# ================================================================ 3. the unexamined life — an oil lamp and scrolls at night
@design("the-unexamined-life")
def unexamined_life():
    D = Doc2("ww-ul")
    out = [f'<rect width="600" height="600" fill="#24140E"/>']
    out.append(blooms(3, ["#5A3420", "#3A2014", "#6A4026"], 8, (0, 0, 600, 600), (90, 180), (0.2, 0.4)))
    out.append(soft_glow(D, 360, 270, 330, "#E88A3A", 0.42))
    # a painted frieze on the wall: meander band and a red-figure owl panel
    out.append(f'<rect x="0" y="66" width="600" height="34" fill="#8A3A1E" opacity="0.55"/>')
    out.append(meander(4, 600, 72, 22, "#1A0A06", 3.2))
    out.append(f'<path d="M 0 104 L 600 104" stroke="#C88A50" stroke-width="2" opacity="0.4"/>')
    # table top
    tbl = [(-20, 392), (620, 384), (620, 600), (-20, 600)]
    out.append(painted(D, tbl, ("#8A5A36", "#5A3620", "#2A160A"), 4, sdir=(0, 1), sk=0.05, angle=-2, n=120, slen=(40, 120), sw=(1, 3), inkw=0, hi=0.2))
    out.append(soft_glow(D, 380, 400, 260, "#FFB060", 0.25))
    out.append(pline([(-10, 392), (300, 388), (610, 384)], "#E8A060", 2, 5, 0.5, 1))
    # a leather scroll-bucket (capsa) full of rolled papyri, back left
    cx0, cw, ctop, cbot = 132, 64, 286, 392
    out.append(cast(D, cx0 + 14, cbot, 80, 9, strength=0.55, seed=6))
    body = [(cx0 - cw, ctop), (cx0 + cw, ctop), (cx0 + cw - 4, cbot - 6), (cx0, cbot + 4), (cx0 - cw + 4, cbot - 6)]
    out.append(f'<path d="{smooth_closed(body)}" fill="#7A4A28"/>')
    out.append(f'<path d="{smooth_closed(body)}" fill="{cyl(D, cx0 - cw, cx0 + cw, 0, 0, ("#C08A58", "#7A4A28", "#2E1608"), 1, 0.95)}"/>')
    out.append(strokes(D.nid(), smooth_closed(body), (cx0 - cw, ctop, cx0 + cw, cbot), ["#A8743E", "#3A1E0C"], 6, n=40, angle=-90, length=(10, 30), width=(1, 3), opacity=(0.2, 0.4)))
    for yy in (ctop + 22, cbot - 26):
        out.append(f'<path d="{smooth_open(ell_pts(cx0, yy, cw - 1, 10, 0, 180, 16))}" fill="none" stroke="#C8903A" stroke-width="5"/>')
        out.append(f'<path d="{smooth_open(ell_pts(cx0, yy, cw - 1, 10, 0, 180, 16))}" fill="none" stroke="#FFE0A0" stroke-width="1.4" opacity="0.6"/>')
    out.append(ink(smooth_closed(body), INK, 1.5, 7, 1, 0.6))
    out.append(f'<path d="{smooth_closed(ell_pts(cx0, ctop, cw, 13, 0, 360, 24))}" fill="#3A2010"/>')
    rnd = random.Random(7)
    for k, (dx, dy, r) in enumerate(((-38, -4, 12), (-12, -8, 13), (16, -6, 12), (40, -2, 11), (-26, 4, 11), (2, 2, 12), (28, 5, 11))):
        x, y = cx0 + dx, ctop + dy - 10
        e = ell_pts(x, y, r, r * 0.55, 0, 360, 16)
        out.append(f'<path d="{pd([(x - r, y), (x - r, y + 22), (x + r, y + 22), (x + r, y)])}" fill="#D8C094"/>')
        out.append(f'<path d="{pd([(x - r, y), (x - r, y + 22), (x + r, y + 22), (x + r, y)])}" fill="{cyl(D, x - r, x + r, 0, 0, ("#FFF0CC", "#D8C094", "#8A6A3A"), -1)}"/>')
        out.append(f'<path d="{smooth_closed(e)}" fill="#F4E4BE"/>')
        sp = [(x + math.cos(t) * t * r * 0.065, y + math.sin(t) * t * r * 0.036) for t in [i * 0.5 for i in range(1, 27)]]
        out.append(pline(sp, "#9A7A4A", 0.9, 7 + k, 0.8, 1))
        out.append(ink(smooth_closed(e), INK, 1.1, 8 + k, 1, 0.6))
        if k in (1, 3, 5):
            tx_, ty_ = x + r * 0.7, y + 2
            out.append(pline([(tx_, ty_), (tx_ + 4, ty_ + 14)], "#C8402A", 1.4, k, 0.9, 1))
            out.append(painted(D, rect_pts(tx_ - 2, ty_ + 12, tx_ + 12, ty_ + 28, 4, k, 0.3), ("#F6E2B8", "#E2C890", "#9A7A4A"), 9 + k, n=3, inkw=0.8))
    # wax tablet and stylus, right
    wt = [(430, 372), (548, 362), (556, 398), (438, 408)]
    out.append(painted(D, wt, ("#B88A5A", "#8A5A30", "#4A2A10"), 10, sdir=(0.3, 1), sk=0.15, angle=-5, n=14, inkw=1.4, hi=0.3))
    wx = [(444, 376), (538, 368), (544, 394), (450, 402)]
    out.append(f'<path d="{smooth_closed(wx)}" fill="#2A1A10"/>')
    for j in range(3):
        out.append(pline([(452, 382 + j * 7), (490, 380 + j * 7), (528, 377 + j * 7)], "#C8A060", 1.2, 11 + j, 0.7, 1))
    out.append(taper([(420, 350), (520, 330)], 3, 1.5, "#D8C8A0"))
    # olive sprig
    out.append(olive_branch(D, [(196, 396), (226, 384), (256, 390)], 12, olives=((0.6, 1, ("#7A6A8A", "#3A2A4A", "#1A0E22")),), w=2.5, leaves=8, L=(18, 26)))
    # the lamp
    out.append(oil_lamp(D, 316, 388, 1.5, 13, glow_r=250))
    # the unrolled papyrus in front carrying the line
    px0, px1, py0, py1 = 70, 530, 430, 540
    sheet = rect_pts(px0, py0, px1, py1, 18, 14, 0.9)
    out.append(f'<path d="{smooth_closed(shift(sheet, 6, 10))}" fill="#000" opacity="0.4"/>')
    out.append(painted(D, sheet, ("#FFF4D6", "#EEDCAE", "#B89A68"), 15, sdir=(0.2, 1), sk=0.04, angle=-2, n=90, slen=(30, 90), sw=(0.6, 1.6), inkw=0, hi=0.2))
    cid = D.clip(f'<path d="{smooth_closed(sheet)}"/>')
    fib = []
    rnd = random.Random(16)
    for j in range(30):
        y = py0 + j * 3.8
        fib.append(f'<path d="M {px0} {y:.1f} L {px1} {y + rnd.uniform(-1, 1):.1f}" stroke="#C8AE78" stroke-width="0.8" opacity="0.35"/>')
    for j in range(40):
        x = px0 + j * 11.5
        fib.append(f'<path d="M {x:.1f} {py0} L {x + rnd.uniform(-1, 1):.1f} {py1}" stroke="#C8AE78" stroke-width="0.7" opacity="0.25"/>')
    fib.append(f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" fill="{D.lin([(0, "#FFC060", 0.2), (0.5, "#FFC060", 0), (1, "#3A2010", 0.25)], 1, 0, 0, 0)}"/>')
    out.append(f'<g {cid}>{"".join(fib)}</g>')
    out.append(ink(smooth_closed(sheet), INK, 1.4, 17, 1, 0.5))
    for x, sg in ((px0, -1), (px1, 1)):
        out.append(scroll_roll(D, x + sg * 4, (py0 + py1) / 2, py1 - py0 + 14, 13, 90, 18 + sg, knob=DARKWOOD))
    out.append(lines(D, 300, 478, 44, ["The unexamined life", "is not worth living."], SERIF_IT, 40, "#2A140A", max_w=400))
    # name above
    out.append(gilt(D, 300, 168, "SOCRATES", CINZEL, 46, ls=12, max_w=360, seed=19, deboss="#0A0402"))
    out.append(tx(300, 200, "c. 470–399 BC · PLATO, APOLOGY", CINZEL, 17, "#E8C890", ls=3, max_w=360))
    return finish_w(D, out, 20, "#000000", 0.5)


# ================================================================ 4. the same river twice — stepping stones across a morning river
def river_stone(D, cx, cy, rx, ry, seed, pal=("#D8CCB4", "#9A8E7A", "#4E463A"), moss=True, flow=1):
    """A rounded river boulder half in the water: lit dry top, dark wet band at the waterline, moss, foam and
    ripples around it (current flowing toward +x if flow=1)."""
    out = []
    rnd = random.Random(seed)
    # ripples / wake downstream and foam upstream
    for k in range(3):
        out.append(f'<path d="{smooth_open(ell_pts(cx + flow * rx * 0.15 * k, cy + ry * 0.35, rx * (1.15 + 0.28 * k), ry * (0.42 + 0.12 * k), 200, 340, 12))}" fill="none" stroke="#FFFFFF" stroke-width="{1.8 - k * 0.4:.1f}" opacity="{0.55 - k * 0.12:.2f}"/>')
    out.append(f'<path d="{blob(cx, cy + ry * 0.45, rx * 1.12, ry * 0.32, seed, 0.1, 14)}" fill="#1A2A30" opacity="0.35"/>')
    pts = blob_pts(cx, cy, rx, ry, seed, 0.08, 18)
    pts = [(x, min(y, cy + ry * 0.45)) for x, y in pts]
    out.append(painted(D, pts, pal, seed + 1, sdir=(0.5, 0.9), sk=0.18, angle=-20, n=int(rx * 0.8) + 8, slen=(rx * 0.15, rx * 0.5),
                       sw=(1, max(1.4, rx * 0.06)), inkw=1.4, inkop=0.55, hi=0.45, hik=0.1))
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    inner = [f'<rect x="{cx - rx * 1.2:.1f}" y="{cy + ry * 0.05:.1f}" width="{rx * 2.4:.1f}" height="{ry:.1f}" fill="#2A2A26" opacity="0.45"/>',
             f'<path d="{blob(cx - rx * 0.3, cy - ry * 0.45, rx * 0.4, ry * 0.18, seed + 2, 0.2, 10)}" fill="#FFFFFF" opacity="0.35"/>']
    if moss:
        for _ in range(int(rx * 0.6)):
            a = rnd.uniform(3.4, 6.0)
            r_ = rnd.uniform(0.3, 0.95)
            inner.append(f'<circle cx="{cx + math.cos(a) * rx * r_:.1f}" cy="{cy + math.sin(a) * ry * r_ * 0.9:.1f}" r="{rnd.uniform(1, 2.6):.1f}" fill="{rnd.choice(["#7A9A3A", "#9AB84A", "#5A7A2A"])}" opacity="0.8"/>')
    for _ in range(int(rx * 0.3)):
        inner.append(f'<circle cx="{cx + rnd.uniform(-rx, rx):.1f}" cy="{cy + rnd.uniform(-ry, ry):.1f}" r="{rnd.uniform(0.6, 1.6):.1f}" fill="{rnd.choice([pal[2], "#FFFFFF"])}" opacity="0.4"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    # foam collar at the waterline (upstream side brighter)
    out.append(taper(catmull([(cx - rx * 1.05, cy + ry * 0.42), (cx - rx * 0.4, cy + ry * 0.58), (cx + rx * 0.4, cy + ry * 0.55), (cx + rx * 1.02, cy + ry * 0.4)], 6),
                     max(2, ry * 0.12), max(1, ry * 0.05), "#FFFFFF", 0.85))
    for k in range(4):
        out.append(f'<circle cx="{cx - flow * rx * rnd.uniform(0.8, 1.2):.1f}" cy="{cy + ry * rnd.uniform(0.3, 0.6):.1f}" r="{rnd.uniform(1, 2.4):.1f}" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


def heron(D, x, base, s, seed, flip=False):
    """Grey heron standing in the shallows: S-neck, dagger bill, black crest plume, long legs."""
    def L(pts):
        return T(pts, x, base, s, flip)
    out = [f'<path d="{blob(x, base + 1, 16 * s, 2.4 * s, seed, 0.1, 10)}" fill="#FFFFFF" opacity="0.4"/>']
    for k, dx in enumerate((-3, 4)):
        out.append(pline(L([(dx, 0), (dx + 1, -16), (dx - 1, -30)]), "#5A4A3A", max(1.4, 1.6 * s), seed + k, 0.95, 1))
    body = L([(-16, -48), (-6, -56), (10, -58), (18, -52), (12, -38), (-4, -30), (-14, -34), (-26, -38)])
    out.append(painted(D, body, ("#E6E8EA", "#9AA0A8", "#4E545E"), seed + 2, sdir=(0.3, 1), sk=0.2, angle=-10, n=12, inkw=1.1, inkc="#2A2E36", hi=0.5))
    out.append(taper(L([(-12, -46), (-22, -38), (-30, -32)]), 3 * s, 0.8, "#3A3E48"))
    neck = L([(12, -56), (18, -66), (12, -76), (14, -86)])
    out.append(taper(neck, 6 * s, 4 * s, "#D8DCE0"))
    out.append(pline(L([(16, -60), (19, -67), (14, -76)]), "#3A3E48", 1.2, seed, 0.6, 1))
    head = L([(10, -86), (16, -91), (22, -88), (18, -83), (12, -82)])
    out.append(f'<path d="{smooth_closed(head)}" fill="#F2F2F0"/>')
    out.append(f'<path d="{pd(L([(20, -89), (38, -86), (20, -85)]))}" fill="#E8B23A"/>')
    out.append(taper(L([(12, -89), (2, -90), (-6, -86)]), 2 * s, 0.5, "#1A1A22"))
    ex, ey = L([(17, -88)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{max(0.8, 0.9 * s):.1f}" fill="#1A1A22"/>')
    return "".join(out)


@design("the-same-river-twice")
def same_river_twice():
    D = Doc2("ww-rt")
    out = [sky(D, [(0, "#9CC0D8"), (0.3, "#D4E2E2"), (0.48, "#FBE8C8")], 3, 330, ["#FFFFFF", "#F2DCC0", "#C0D6E2"], 40)]
    out.append(soft_glow(D, 470, 280, 220, "#FFF0C0", 0.85))
    out.append(puff_cloud(D, 110, 236, 120, 4, pal=("#FFFFFF", "#FAF2EA", "#D8CCD0"), rows=2))
    out.append(puff_cloud(D, 520, 222, 80, 5, pal=("#FFFFFF", "#FAF2EA", "#D8CCD0"), rows=2))
    for k, (x, y) in enumerate(((380, 238), (398, 246), (360, 250))):
        out.append(bird_v(x, y, 5, "#4A4A5A", 0.7))
    # far blue hills and wooded middle ground
    l1 = ridge([(-20, 280), (90, 258), (210, 274), (330, 252), (450, 270), (620, 258)], 5, 8)
    out.append(hill(D, l1, 340, ("#C8D6DC", "#AABEC8", "#90A4B0"), 6, inkw=0, n=30, sop=(0.1, 0.25)))
    l2 = ridge([(-20, 300), (120, 286), (250, 300), (380, 288), (620, 296)], 7, 6)
    out.append(hill(D, l2, 360, ("#A8BCA4", "#86A08A", "#5E7A66"), 8, inkw=0, n=30))
    for k, (x, y, rx) in enumerate(((40, 296, 70), (180, 300, 40), (560, 292, 70), (440, 296, 36))):
        out.append(dab_crown(D, x, y, rx, 16, [("#9AB49A", "#7A9680", "#566E5C")], 9 + k, n=70, size=(4, 7), inkw=0))
    # far bank meadow
    fb = [(-20, 300), (620, 296), (620, 420), (-20, 420)]
    out.append(f'<path d="{pd(fb)}" fill="#9ABA62"/>')
    out.append(strokes(D.nid(), pd(fb), (-40, 296, 620, 420), ["#C8DC8A", "#7A9A4A", "#B0CC74"], 11, n=150, angle=-4, length=(14, 40), width=(1.5, 3.5), opacity=(0.3, 0.6)))
    # the river: winds out of the far right, sweeps across the foreground from right to left
    top_bank = [(640, 318), (560, 322), (500, 334), (470, 352), (420, 372), (300, 392), (160, 398), (40, 404), (-40, 408)]
    near_bank = [(-40, 540), (80, 534), (220, 538), (360, 530), (480, 512), (560, 470), (600, 420), (640, 330)]
    riv = top_bank + near_bank
    rd = smooth_closed(riv)
    out.append(f'<path d="{rd}" fill="{D.lin([(0, "#F6EAD0"), (0.2, "#BCD8E0"), (0.55, "#6E9EB2"), (1, "#2E6070")], 0, 310, 0, 540, "userSpaceOnUse")}"/>')
    cid = D.clip(f'<path d="{rd}"/>')
    rnd = random.Random(12)
    inner = [soft_glow(D, 520, 340, 120, "#FFF6D8", 0.75)]
    # reflections of far trees and bank
    inner.append(f'<path d="{blob(300, 408, 330, 10, 3, 0.2, 18)}" fill="#5E7A4A" opacity="0.3"/>')
    for _ in range(220):
        y = 320 + (rnd.random() ** 1.1) * 220
        k = (y - 320) / 220
        L_ = 8 + k * 46
        x = rnd.uniform(-20, 620)
        inner.append(f'<path d="M {x:.1f} {y:.1f} q {-L_ / 2:.1f} {-1.5 - k * 3:.1f} {-L_:.1f} 0" stroke="{rnd.choice(["#FFFFFF", "#DFF0F4", "#2E5A6A", "#8AC0CE", "#1E4A5A"])}" stroke-width="{0.8 + k * 1.6:.1f}" fill="none" opacity="{rnd.uniform(0.3, 0.75):.2f}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(smooth_open(top_bank), "#4E6A3A", 1.6, 13, 1, 0.55))
    # pebbled far shore and tall grasses on the far bank
    out.append(specks(14, (-10, 398, 420, 410), ["#D8CCB4", "#9A8E7A", "#FFFFFF"], 60, (1.2, 2.6), (0.6, 0.95)))
    out.append(grass(15, (-10, 392, 620, 404), ["#6A8A3A", "#9AB85A", "#4E6E2E"], n=120, h=(8, 20)))
    # willow on the far bank, left of centre, trailing toward the water
    wx, wy = 120, 396
    out.append(taper(catmull([(wx, wy), (wx + 4, wy - 50), (wx - 2, wy - 96)], 5), 13, 6, "#6A4E36"))
    for k in range(34):
        a = rnd.uniform(-2.8, -0.3)
        sx, sy = wx + math.cos(a) * 54, wy - 108 + math.sin(a) * 30
        L_ = rnd.uniform(50, 96)
        pts = [(sx, sy), (sx + math.cos(a) * 14, sy - 6), (sx + math.cos(a) * 22 + rnd.uniform(-4, 4), sy + L_ * 0.5), (sx + math.cos(a) * 24, sy + L_)]
        out.append(taper(catmull(pts, 4), rnd.uniform(5, 9), 1.5, rnd.choice(["#8AB05A", "#6A9442", "#A8C870", "#4E7A34"]), 0.85))
    out.append(dab_crown(D, wx, wy - 112, 64, 30, [("#B8D47A", "#7AA24A", "#4A7230")], 15, n=130, size=(4, 8), light=(0.7, -0.6), inkw=1.0))
    # heron on the far shore
    out.append(heron(D, 400, 384, 0.95, 16, flip=True))
    # near bank: grass, wildflowers, bottom edge
    nb = near_bank + [(640, 620), (-40, 620)]
    out.append(painted(D, nb[:-2][::1] + [(640, 640), (-40, 640)], ("#B8D47A", "#7AA24A", "#3E6626"), 17, sdir=(0, 1), sk=0.04, angle=-80, n=160,
                       slen=(6, 18), sw=(1, 2.6), inkw=1.4, inkop=0.5, hi=0.25))
    out.append(grass(18, (-10, 528, 620, 600), ["#5E8A3A", "#8AB45A", "#3E6626", "#A8C870"], n=160, h=(10, 28)))
    for _ in range(40):
        x, y = rnd.uniform(0, 600), rnd.uniform(548, 598)
        if 200 < x < 400:
            continue
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(2, 3.4):.1f}" fill="{rnd.choice(["#FFFFFF", "#F6D25A", "#F6A8C0", "#B8A0E0"])}"/>')
    # reeds and cattails, near right
    for k, (x, y) in enumerate(((520, 520), (546, 508), (566, 492), (500, 528))):
        out.append(taper([(x, y), (x + 3, y - 92)], 2.6, 1.6, "#5E7A34"))
        out.append(f'<path d="{blob(x + 3, y - 96, 4, 14, 31 + k, 0.1, 10)}" fill="#6A3A1E"/>')
        out.append(taper(catmull([(x - 2, y), (x - 14, y - 50), (x - 30, y - 70)], 4), 4, 0.8, "#7A9A44"))
    # stepping stones from the viewer's feet out to the far bank
    stones = [(334, 410, 18, 10), (304, 430, 24, 13), (264, 456, 31, 17), (306, 486, 39, 21), (250, 520, 48, 25)]
    for k, (x, y, rx, ry) in enumerate(stones):
        out.append(river_stone(D, x, y, rx, ry, 20 + k, flow=-1))
    big = blob_pts(214, 588, 96, 40, 29, 0.07, 20)
    out.append(cast(D, 230, 600, 110, 16, strength=0.4, seed=29))
    out.append(painted(D, big, ("#EADFC6", "#ACA084", "#5A5040"), 30, sdir=(0.5, 1), sk=0.2, angle=-12, n=70, inkw=1.6, hi=0.5, hik=0.12))
    out.append(specks(32, (140, 560, 300, 600), ["#7A9A3A", "#9AB84A", "#5A7A2A"], 40, (1, 2.6), (0.6, 0.9)))
    out.append(grass(31, (110, 566, 330, 600), ["#7A9A3A", "#9AB84A", "#5E8A3A"], n=40, h=(8, 18)))
    # lettering
    out.append(lines(D, 300, 110, 50, ["No man ever steps in", "the same river twice."], SERIF_IT, 44, "#1E3E5A", max_w=460))
    out.append(byline(196, "AFTER HERACLITUS · c. 535–475 BC", "#4A3A2A", size=17, ls=3, max_w=420))
    return finish_w(D, out, 40)


# ================================================================ 5. a single step — a mountain path on a hanging scroll
def karst(D, cx, base, w, h, seed, pal, haze=0.0, lean=0.0, texture=True):
    """A tall shan-shui peak: rounded shoulders, axe-cut vertical texture strokes, a lit side."""
    rnd = random.Random(seed)
    n = 14
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        y = base - h * t
        hw = w / 2 * (1 - t ** 1.8) ** 0.7 * rnd.uniform(0.9, 1.08) + 3
        xc = cx + lean * h * t
        left.append((xc - hw, y))
        right.append((xc + hw * rnd.uniform(0.85, 1.05), y))
    pts = left + right[::-1]
    hz = (lambda c: mix(c, "#E8E6DA", haze)) if haze else (lambda c: c)
    pl = (hz(pal[0]), hz(pal[1]), hz(pal[2]))
    out = [painted(D, pts, pl, seed, sdir=(1, 0.2), sk=0.16, angle=-92, n=int(w * h / 140) + 10, slen=(h * 0.05, h * 0.2), sw=(1, 3),
                   inkw=1.1 if not haze else 0, inkop=0.45, hi=0.35, hik=0.08)]
    if texture:
        cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
        tx_ = []
        for _ in range(int(h / 6)):
            x = cx + rnd.uniform(-w / 2, w / 2) + lean * h * 0.5
            y = base - rnd.uniform(0, h)
            tx_.append(f'<path d="M {x:.1f} {y:.1f} q {rnd.uniform(-3, 3):.1f} {rnd.uniform(6, 14):.1f} {rnd.uniform(-2, 4):.1f} {rnd.uniform(12, 26):.1f}" stroke="{hz(pal[2])}" stroke-width="{rnd.uniform(1, 2.2):.1f}" fill="none" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>')
        for _ in range(int(h / 14)):
            x = cx + rnd.uniform(-w / 2.4, w / 2.4) + lean * h * 0.5
            y = base - rnd.uniform(0, h * 0.95)
            tx_.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.5, 3):.1f}" fill="{hz("#3E5A3A")}" opacity="0.7"/>')
        out.append(f'<g {cid}>{"".join(tx_)}</g>')
    return "".join(out)


def mist_band(D, cx, cy, rx, ry, op=0.85, col="#FBF6EA"):
    g = D.rad([(0, col, op), (0.6, col, op * 0.7), (1, col, 0)])
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{g}"/>'


def traveller(x, base, s, seed, robe="#3E5A7A", hat="#D8B46A"):
    """A tiny wanderer seen from behind: straw hat, robe, bundle, staff."""
    out = [f'<ellipse cx="{x + 2 * s:.1f}" cy="{base:.1f}" rx="{9 * s:.1f}" ry="{2 * s:.1f}" fill="#2A1A10" opacity="0.3"/>']
    out.append(pline([(x + 9 * s, base), (x + 11 * s, base - 30 * s)], "#5A3A20", max(1.2, 1.4 * s), seed, 0.95, 1))
    robe_p = [(x - 6 * s, base - 22 * s), (x + 6 * s, base - 22 * s), (x + 8 * s, base), (x - 8 * s, base)]
    out.append(f'<path d="{smooth_closed(robe_p)}" fill="{robe}"/>')
    out.append(f'<path d="{smooth_closed([(x, base - 22 * s), (x + 6 * s, base - 22 * s), (x + 8 * s, base), (x + 1 * s, base)])}" fill="#1A2A3A" opacity="0.4"/>')
    out.append(f'<path d="{blob(x - 1 * s, base - 21 * s, 5 * s, 4 * s, seed, 0.1, 8)}" fill="#C8A060"/>')
    out.append(f'<path d="{pd([(x - 10 * s, base - 26 * s), (x, base - 34 * s), (x + 10 * s, base - 26 * s)])}" fill="{hat}"/>')
    out.append(f'<path d="{pd([(x - 10 * s, base - 26 * s), (x, base - 34 * s), (x + 10 * s, base - 26 * s)], False)}" fill="none" stroke="#7A5A2A" stroke-width="0.9"/>')
    return "".join(out)


def pavilion(D, cx, base, s, seed, col=("#F08A6A", "#C83A28", "#7A1A10")):
    out = []
    for dx in (-12, 12):
        out.append(f'<rect x="{cx + dx * s - 1.5 * s:.1f}" y="{base - 16 * s:.1f}" width="{3 * s:.1f}" height="{16 * s:.1f}" fill="{col[1]}"/>')
    roof = [(cx - 24 * s, base - 14 * s), (cx - 18 * s, base - 18 * s), (cx - 6 * s, base - 28 * s), (cx + 6 * s, base - 28 * s), (cx + 18 * s, base - 18 * s), (cx + 24 * s, base - 14 * s), (cx, base - 18 * s)]
    out.append(f'<path d="{smooth_closed(roof)}" fill="#3A3A42"/>')
    out.append(f'<path d="M {cx - 16 * s:.1f} {base:.1f} L {cx + 16 * s:.1f} {base:.1f}" stroke="#8A7A6A" stroke-width="{2 * s:.1f}"/>')
    return "".join(out)


@design("a-single-step")
def a_single_step():
    D = Doc2("ww-ss")
    # plain plaster wall behind the hanging scroll
    out = [paper(D.nid(), "#E8DCC4", FLECK, 3, 1.2)]
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFF8E8", 0.5), (1, "#5A3A20", 0.3)], cx=0.5, cy=0.4, r=0.8)}"/>')
    # the scroll: brocade mount, silk paper, painting, lower panel
    X0, X1, TOP, BOT = 74, 526, 34, 572
    out.append(f'<path d="{pd([(X0 + 8, TOP + 8), (X1 + 10, TOP + 8), (X1 + 10, BOT + 8), (X0 + 8, BOT + 8)])}" fill="#3A2418" opacity="0.2"/>')
    mount = hg.org_rect(X0, TOP, X1 - X0, BOT - TOP, 2, 0.5, 14, 1)
    out.append(f'<path d="{mount}" fill="#6A7A5A"/>')
    pat = D.pattern(26, 26, '<rect width="26" height="26" fill="#6A7A5A"/><path d="M 13 3 l 4 10 l -4 10 l -4 -10 Z" fill="#8A9A70" opacity="0.6"/>'
                    '<circle cx="0" cy="0" r="3" fill="#C8B070" opacity="0.6"/><circle cx="26" cy="26" r="3" fill="#C8B070" opacity="0.6"/>')
    out.append(f'<path d="{mount}" fill="{pat}"/>')
    silk = hg.org_rect(X0 + 16, TOP + 44, X1 - X0 - 32, BOT - TOP - 82, 3, 0.4, 12, 0.6)
    out.append(f'<path d="{silk}" fill="#F6EEDA"/>')
    out.append(f'<path d="{silk}" fill="{D.lin([(0, "#E8D8B0", 0.4), (1, "#FFFFFF", 0)])}"/>')
    # the painting
    px0, py0, px1, py1 = X0 + 28, TOP + 56, X1 - 28, 384
    cid = D.clip(f'<path d="{hg.org_rect(px0, py0, px1 - px0, py1 - py0, 4, 0.3, 10, 0.5)}"/>')
    art = [f'<rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" fill="{D.lin([(0, "#E8E4D0"), (0.6, "#F6EEDA"), (1, "#F2E8D0")])}"/>']
    art.append(soft_glow(D, 380, 150, 120, "#FFE8C0", 0.6))
    art.append(f'<circle cx="400" cy="140" r="18" fill="#E8805A" opacity="0.75"/>')
    # far peaks (pale), then middle peaks, then the near cliff with the path
    for k, (x, b, w, h, lean) in enumerate(((150, 300, 70, 190, 0.05), (232, 290, 60, 150, -0.06), (430, 300, 90, 210, -0.04), (520, 290, 60, 140, 0.08))):
        art.append(karst(D, x, b, w, h, 10 + k, ("#C8D0C4", "#A8B4AC", "#7A8A84"), haze=0.35, lean=lean, texture=True))
    art.append(mist_band(D, 300, 290, 280, 36, 0.95))
    for k, (x, b, w, h, lean) in enumerate(((168, 380, 110, 200, 0.06), (400, 380, 150, 250, -0.05))):
        art.append(karst(D, x, b, w, h, 20 + k, ("#9AB89A", "#4E7A5E", "#1E3E2E"), lean=lean))
    # waterfall from the right peak
    art.append(taper(catmull([(372, 210), (368, 250), (370, 300), (366, 340)], 4), 8, 12, "#FFFFFF", 0.9))
    art.append(taper(catmull([(374, 214), (371, 262), (372, 330)], 4), 2.5, 3, "#C8E0E8", 0.9))
    # pavilion on the right summit, pines on the ledges
    art.append(pavilion(D, 396, 134, 1.0, 30))
    for k, (x, y, h_, lean) in enumerate(((356, 168, 26, -0.4), (450, 190, 22, 0.5), (140, 214, 22, -0.3), (198, 240, 18, 0.4))):
        art.append(jpine(D, x, y, h_, 40 + k, lean=lean, inkw=0.6))
    art.append(mist_band(D, 280, 352, 300, 30, 0.9))
    # the zigzag path climbing from the foot to the pavilion
    path = [(258, 396), (238, 372), (282, 350), (250, 326), (300, 300), (318, 268), (348, 240), (360, 206), (382, 176), (394, 140)]
    art.append(taper(catmull(path, 6), 12, 3, "#E8D8B0", 0.95))
    art.append(pline(catmull(path, 6), "#8A6A40", 1.0, 41, 0.55, 1))
    for i in range(len(path) - 1):
        (xa, ya), (xb, yb) = path[i], path[i + 1]
        for t in (0.3, 0.7):
            x, y = xa + (xb - xa) * t, ya + (yb - ya) * t
            w_ = 6 - i * 0.45
            art.append(f'<path d="M {x - w_:.1f} {y:.1f} L {x + w_:.1f} {y - 0.6:.1f}" stroke="#8A6A40" stroke-width="1" opacity="0.6"/>')
    # near rocks and a gnarled pine at bottom left
    art.append(karst(D, 120, 400, 140, 70, 50, ("#B8A884", "#7A6A4E", "#3E3426"), lean=0.1))
    art.append(karst(D, 470, 400, 160, 56, 51, ("#B8A884", "#7A6A4E", "#3E3426"), lean=-0.1))
    art.append(jpine(D, 116, 344, 60, 52, lean=0.5, inkw=0.8))
    art.append(traveller(272, 392, 1.25, 53))
    out.append(f'<g {cid}>{"".join(art)}</g>')
    out.append(ink(hg.org_rect(px0, py0, px1 - px0, py1 - py0, 4, 0.3, 10, 0.5), "#8A7A5A", 1.2, 5, 1, 0.6))
    # the words on the lower silk
    out.append(hanko(D, px1 - 22, py1 - 22, 22, 54, col="#C8281E", paper_c="#F2E8D0"))
    out.append(lines(D, 300, 428, 38, ["A journey of a thousand miles", "begins with a single step."], SERIF_IT, 31, "#2A2A2A", max_w=400))
    out.append(byline(506, "LAO TZU · 6TH CENTURY BC", "#7A2A1A", size=17, ls=3, max_w=300))
    out.append(ink(mount, INK, 1.2, 6, 1, 0.5))
    # staves top and bottom, hanging cord
    out.append(f'<path d="M 270 {TOP - 4} L 300 6 L 330 {TOP - 4}" stroke="#4A3018" stroke-width="2" fill="none"/>')
    out.append(f'<path d="{hg.org_rect(X0 - 2, TOP - 6, X1 - X0 + 4, 10, 7, 0.3, 8, 2)}" fill="#3A2418"/>')
    out.append(f'<path d="{hg.org_rect(X0 - 6, BOT - 8, X1 - X0 + 12, 14, 8, 0.3, 8, 4)}" fill="#2A1A10"/>')
    for sg in (-1, 1):
        k_ = blob(300 + sg * ((X1 - X0) / 2 + 14), BOT - 1, 9, 10, 9 + sg, 0.1, 10)
        out.append(f'<path d="{k_}" fill="#E8D8B8"/>' + ink(k_, INK, 1.1, 10, 1, 0.6))
    return finish_w(D, out, 60)


# ================================================================ 6. well done — an almanac page: the kite and key in the storm
def kite(D, cx, cy, s, seed, ang=-12):
    """Franklin's silk-handkerchief kite: a cross of cedar sticks, a pointed wire at the top, a ribbon tail."""
    pts = rot([(cx, cy - 46 * s), (cx + 34 * s, cy - 6 * s), (cx, cy + 46 * s), (cx - 34 * s, cy - 6 * s)], cx, cy, ang)
    out = [painted(D, pts, ("#FFF6E2", "#EAD8B4", "#A8885A"), seed, sdir=(0.8, 0.5), sk=0.15, angle=-60, n=16, inkw=1.6, hi=0.4)]
    a, b, c, d_ = pts
    out.append(pline([a, c], "#6A4A2A", 1.8, seed, 0.85, 1) + pline([b, d_], "#6A4A2A", 1.8, seed + 1, 0.85, 1))
    out.append(f'<path d="{pd([a, b, (cx, cy)])}" fill="#C8A878" opacity="0.25"/>')
    ax, ay = a
    out.append(pline([(ax, ay), (ax + 2, ay - 14 * s)], "#3A3A3A", 1.6, seed, 1, 1))
    return "".join(out), c


@design("well-done")
def well_done():
    D = Doc2("ww-wd")
    out = [paper(D.nid(), "#F2E6CC", FLECK, 7, 1.4)]
    out.append(blooms(8, ["#D8B888", "#C8A070", "#E8D0A0"], 9, (0, 0, 600, 600), (40, 120), (0.06, 0.14)))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFFFFF", 0), (0.7, "#8A5A2A", 0.05), (1, "#5A3A1A", 0.35)], r=0.75)}"/>')
    rnd = random.Random(8)
    for _ in range(14):
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 580)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(2, 6):.1f}" fill="#A8743A" opacity="{rnd.uniform(0.08, 0.2):.2f}"/>')
    # printer's border: thick-thin rules and a row of type ornaments
    out.append(rule_frame(D, 36, 36, 564, 564, "#3A2A1A", 3, 7, 1.2, seed=9))
    for k in range(17):
        for (x, y) in ((70 + k * 28.2, 58), (70 + k * 28.2, 548)):
            out.append(fleuron(x, y, 5.5, "#3A2A1A", 90 if y < 100 else -90, 0.8))
    out.append(tx(300, 102, "POOR RICHARD · 1737", CINZEL, 22, "#2A1A0E", ls=6, max_w=380))
    out.append(pline([(150, 114), (300, 115), (450, 114)], "#2A1A0E", 1.4, 10, 0.8, 1))
    # the oval vignette: a summer thunderstorm, the kite and the key
    ocx, ocy, orx, ory = 300, 230, 186, 102
    oval = ell_pts(ocx, ocy, orx, ory, 0, 360, 40)[:-1]
    od = smooth_closed(oval)
    cid = D.clip(f'<path d="{od}"/>')
    sc = [f'<rect x="100" y="120" width="400" height="220" fill="{D.lin([(0, "#3A4458"), (0.5, "#6A7488"), (1, "#C8B898")])}"/>']
    sc.append(soft_glow(D, 360, 200, 120, "#FFF2C8", 0.5))
    for k, (x, y, w) in enumerate(((180, 160, 160), (330, 150, 190), (440, 190, 140), (240, 210, 170))):
        sc.append(puff_cloud(D, x, y, w, 20 + k, pal=("#8A92A8", "#4E5670", "#262C40"), rows=3))
    # lightning bolt
    bolt = [(392, 176), (380, 214), (394, 216), (372, 266), (402, 222), (388, 220), (404, 186)]
    sc.append(soft_glow(D, 388, 220, 70, "#FFFFFF", 0.6))
    sc.append(f'<path d="{pd(bolt)}" fill="#FFF8D8"/>')
    sc.append(pline([(380, 214), (360, 232), (352, 252)], "#FFF8D8", 1.6, 21, 0.9, 1))
    # rain
    for _ in range(90):
        x, y = rnd.uniform(110, 500), rnd.uniform(130, 330)
        sc.append(f'<path d="M {x:.1f} {y:.1f} l -4 12" stroke="#D8E0EC" stroke-width="1" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>')
    # fields, a shed and a hedge
    land = [(100, 300), (220, 292), (330, 298), (500, 290), (500, 340), (100, 340)]
    sc.append(painted(D, land, ("#9AA870", "#5E6E3E", "#2E3A1E"), 22, sk=0.05, angle=-4, n=40, inkw=0))
    sc.append(f'<path d="{pd([(176, 300), (176, 280), (192, 270), (208, 280), (208, 300)])}" fill="#4A3A2E"/>')
    sc.append(f'<rect x="186" y="286" width="7" height="9" fill="#FFD27A"/>')
    sc.append(dab_crown(D, 440, 288, 40, 12, [("#6A7A4E", "#3E4A2E", "#1E2618")], 23, n=40, size=(3, 6), inkw=0))
    k_svg, tail = kite(D, 250, 166, 0.95, 24)
    sc.append(k_svg)
    # ribbon tail
    tp = [tail, (tail[0] + 10, tail[1] + 22), (tail[0] - 4, tail[1] + 40), (tail[0] + 8, tail[1] + 62)]
    sc.append(pline(tp, "#5A3A2A", 1.2, 25, 0.9, 1))
    for t in (0.25, 0.5, 0.75):
        i = int(t * (len(tp) - 1))
        x, y = tp[i][0] + (tp[i + 1][0] - tp[i][0]) * (t * 3 - i), tp[i][1] + (tp[i + 1][1] - tp[i][1]) * (t * 3 - i)
        sc.append(f'<path d="{pd([(x, y), (x - 7, y - 4), (x - 6, y + 4)])}" fill="#C8382A"/><path d="{pd([(x, y), (x + 7, y - 4), (x + 6, y + 4)])}" fill="#C8382A"/>')
    # the string, the key
    string = [(256, 176), (212, 250), (170, 300), (128, 340)]
    sc.append(pline(catmull(string, 6), "#2A2018", 1.4, 26, 0.9, 1))
    kx, ky = 186, 284
    sc.append(f'<circle cx="{kx}" cy="{ky}" r="7" fill="none" stroke="#C89A3A" stroke-width="3.4"/>')
    sc.append(taper([(kx + 4, ky + 6), (kx + 14, ky + 24)], 3.4, 3, "#C89A3A"))
    sc.append(f'<path d="{pd([(kx + 11, ky + 18), (kx + 18, ky + 15), (kx + 19, ky + 19), (kx + 13, ky + 22)])}" fill="#C89A3A"/>')
    sc.append(sparkle(kx - 4, ky - 6, 9, "#FFF6C8", 0.95))
    out.append(f'<g {cid}>{"".join(sc)}</g>')
    out.append(f'<path d="{od}" fill="none" stroke="#2A1A0E" stroke-width="3"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(ocx, ocy, orx + 8, ory + 8, 0, 360, 40)[:-1])}" fill="none" stroke="#2A1A0E" stroke-width="1.2"/>')
    for sg in (-1, 1):
        out.append(fleuron(ocx + sg * (orx + 22), ocy, 9, "#3A2A1A", 90 * sg, 0.9))
    # the maxim, set like an almanac headline
    out.append(tx(300, 404, "Well done", DMS, 76, "#1E140C", max_w=420))
    out.append(ruled(300, 442, "is better than", "#7A2A1A", font=SERIF_IT, size=28, ls=0, line_w=60, gap=16))
    out.append(tx(300, 502, "well said.", DMS, 76, "#1E140C", max_w=420))
    out.append(byline(536, "BENJAMIN FRANKLIN · 1706–1790", "#4A2E18", size=17, ls=3, max_w=400))
    return finish_w(D, out, 30)


# ================================================================ 7. one swallow — a red-figure Greek plate
def arc_text(D, cx, cy, r, s, font, size, fill, ls=0, top=True, max_len=None):
    """Text set along a circular arc (top: reads clockwise over the top; bottom: reads left-to-right under)."""
    pid = D.nid()
    if top:
        d = f"M {cx - r:.1f} {cy:.1f} A {r:.1f} {r:.1f} 0 0 1 {cx + r:.1f} {cy:.1f}"
    else:
        d = f"M {cx - r:.1f} {cy:.1f} A {r:.1f} {r:.1f} 0 0 0 {cx + r:.1f} {cy:.1f}"
    D.defs.append(f'<path id="{pid}" d="{d}"/>')
    if max_len:
        size = fit_size(s, font, size, max_len, ls)
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return f'<text {font} font-size="{size}"{lsa} fill="{fill}"><textPath href="#{pid}" startOffset="50%" text-anchor="middle">{esc(s)}</textPath></text>'


def palmette(cx, cy, s, col, ang=0):
    out = []
    for k in range(7):
        a = math.radians(-90 + (k - 3) * 24 + ang)
        L = s * (1 - abs(k - 3) * 0.12)
        tip = (cx + math.cos(a) * L, cy + math.sin(a) * L)
        out.append(taper([(cx, cy), ((cx + tip[0]) / 2, (cy + tip[1]) / 2), tip], s * 0.06, s * 0.16, col))
    out.append(f'<path d="{smooth_open(ell_pts(cx, cy + s * 0.15, s * 0.35, s * 0.2, 200, 340, 8))}" fill="none" stroke="{col}" stroke-width="{s * 0.06:.1f}"/>')
    return "".join(out)


@design("one-swallow")
def one_swallow():
    D = Doc2("ww-os")
    # an Aegean-blue limewashed wall
    out = [f'<rect width="600" height="600" fill="#2E6E9A"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 610, 610), ["#3E80AE", "#245A84", "#4A8AB8", "#1E4E76"], 1,
                       n=260, angle=-70, length=(40, 120), width=(6, 16), opacity=(0.15, 0.35)))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFFFFF", 0.12), (0.6, "#000", 0), (1, "#0A1A2A", 0.45)], r=0.75)}"/>')
    cx, cy, R = 300, 300, 262
    # plate shadow and body
    out.append(f'<circle cx="{cx + 14}" cy="{cy + 18}" r="{R + 2}" fill="#0A1A2A" opacity="0.45"/>')
    rimp = blob_pts(cx, cy, R, R, 2, 0.006, 60)
    out.append(painted(D, rimp, ("#F6B07A", "#D8743E", "#8A3A16"), 3, sdir=(0.6, 0.8), sk=0.05, angle=-30, n=120, inkw=1.6, inkc="#3A1608", hi=0.3))
    # black-glazed outer band with a reserved meander ring
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R - 10}" fill="#1A0E0A"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R - 52}" fill="#D27040"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R - 52}" fill="{D.rad([(0, "#E88A50"), (0.8, "#D27040"), (1, "#A8501E")])}"/>')
    # inscription ring (black letters on terracotta)
    out.append(arc_text(D, cx, cy + 6, R - 84, "ONE SWALLOW DOES NOT MAKE A SUMMER", CINZEL, 30, "#1A0E0A", ls=2.5, top=True, max_len=(R - 84) * 2.9))
    out.append(arc_text(D, cx, cy - 6, R - 66, "ARISTOTLE · 384–322 BC", CINZEL, 21, "#1A0E0A", ls=3, top=False, max_len=(R - 66) * 1.5))
    # tondo: black ground, red-figure swallow over barley
    TR = R - 118
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{TR + 6}" fill="none" stroke="#1A0E0A" stroke-width="3"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{TR}" fill="#160C08"/>')
    cid = D.clip(f'<circle cx="{cx}" cy="{cy}" r="{TR}"/>')
    td = []
    tc = "#E07E48"
    # barley ears rising from the bottom
    for k, (x0, ang) in enumerate(((250, -100), (282, -86), (318, -78), (346, -64))):
        a = math.radians(ang)
        stem = [(x0, cy + TR), (x0 + math.cos(a) * 60, cy + TR + math.sin(a) * 60), (x0 + math.cos(a) * 110, cy + TR + math.sin(a) * 110)]
        td.append(pline(stem, tc, 2.2, 30 + k, 1, 1))
        ex, ey = stem[-1]
        for j in range(7):
            t = j / 7
            px, py = ex + math.cos(a) * 34 * t, ey + math.sin(a) * 34 * t
            for sg in (-1, 1):
                aa = a + sg * 0.5
                td.append(f'<path d="{blob(px + math.cos(aa) * 4, py + math.sin(aa) * 4, 5, 2.4, 31 + j * 2 + k, 0.1, 8, math.degrees(aa))}" fill="{tc}"/>')
                td.append(pline([(px + math.cos(aa) * 6, py + math.sin(aa) * 6), (px + math.cos(aa - sg * 0.3) * 22, py + math.sin(aa - sg * 0.3) * 22)], tc, 0.9, j, 0.9, 1))
    # the sun rosette
    sx, sy = 352, 236
    td.append(f'<circle cx="{sx}" cy="{sy}" r="11" fill="{tc}"/>')
    for k in range(12):
        a = math.radians(k * 30)
        td.append(pline([(sx + math.cos(a) * 15, sy + math.sin(a) * 15), (sx + math.cos(a) * 22, sy + math.sin(a) * 22)], tc, 2.2, k, 1, 1))
    # the swallow: reserved terracotta figure with black relief-line detail
    sw_ = 1.55
    bx, by = 262, 286

    def L(pts):
        return T(pts, bx, by, sw_, False, -14)
    shapes = [L([(-2, -2), (-14, -26), (-34, -46), (-52, -58), (-40, -36), (-18, -10)]),
              L([(-28, -4), (-10, -9), (8, -9), (20, -6), (27, -1), (20, 4), (6, 8), (-12, 7), (-28, 3)]),
              L([(2, -2), (-10, 14), (-28, 34), (-52, 50), (-32, 22), (-14, 0)])]
    for k, tip in enumerate(((-74, -10), (-72, 12))):
        td.append(taper(L([(-24, -3 + k * 4), (-46, -4 + k * 6), tip]), 7 * sw_, 0.8, tc))
    for k, sh in enumerate(shapes):
        td.append(f'<path d="{smooth_closed(sh)}" fill="{tc}"/>')
    for k, sh in enumerate(shapes):
        td.append(ink(smooth_closed(sh), "#1A0E0A", 1.6, 40 + k, 1, 0.9))
    for j in range(5):
        for wing, base_ in ((0, (-14, -12)), (2, (-12, 6))):
            a_, b_ = L([(base_[0] - j * 7, base_[1] + (j * 8 if wing else -j * 8))])[0], L([(base_[0] - j * 7 - 12, base_[1] + (j * 8 + 14 if wing else -j * 8 - 14))])[0]
            td.append(pline([a_, b_], "#1A0E0A", 1.1, j + wing, 0.85, 1))
    td.append(pline(L([(10, -1), (20, 1), (26, 0)]), "#1A0E0A", 1.2, 50, 0.9, 1))
    ex, ey = L([(21, -3.5)])[0]
    td.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="2.6" fill="#1A0E0A"/>')
    td.append(f'<path d="{pd(L([(26, -2.5), (33, -0.5), (26, 1.2)]))}" fill="{tc}" stroke="#1A0E0A" stroke-width="1"/>')
    # dilute-glaze shading lines on the belly (as vase painters did)
    for j in range(4):
        td.append(pline(L([(-16 + j * 8, 4), (-12 + j * 8, 6)]), "#8A4A22", 1.2, 60 + j, 0.8, 1))
    out.append(f'<g {cid}>{"".join(td)}</g>')
    # meander ring between tondo and inscription
    for k in range(40):
        a0 = math.radians(k * 9)
        r0, r1 = TR + 12, TR + 24
        p = [(cx + math.cos(a0) * r0, cy + math.sin(a0) * r0), (cx + math.cos(a0) * r1, cy + math.sin(a0) * r1),
             (cx + math.cos(a0 + 0.1) * r1, cy + math.sin(a0 + 0.1) * r1), (cx + math.cos(a0 + 0.1) * (r0 + 6), cy + math.sin(a0 + 0.1) * (r0 + 6))]
        out.append(f'<path d="{pd(p, False)}" fill="none" stroke="#1A0E0A" stroke-width="2"/>')
    # a reserved wreath of dots on the outer black band
    for k in range(72):
        a = math.radians(k * 5)
        out.append(f'<circle cx="{cx + math.cos(a) * (R - 31):.1f}" cy="{cy + math.sin(a) * (R - 31):.1f}" r="3" fill="#D27040"/>')
    # glaze sheen and a chip on the rim
    out.append(taper(catmull([(cx - R * 0.72, cy - R * 0.4), (cx - R * 0.5, cy - R * 0.66), (cx - R * 0.18, cy - R * 0.82)], 6), 10, 2, "#FFFFFF", 0.22))
    out.append(taper(catmull([(cx + R * 0.66, cy + R * 0.5), (cx + R * 0.42, cy + R * 0.72)], 6), 6, 1, "#FFFFFF", 0.15))
    out.append(f'<path d="{blob(cx + R * 0.68, cy - R * 0.7, 9, 6, 7, 0.2, 10)}" fill="#E8A070"/>')
    return finish_w(D, out, 70, "#000000", 0.5)


# ================================================================ 8. the soul is dyed — dawn over the sea through a marble arch
def tabula_ansata(D, cx, cy, w, h, seed, pal=BRONZE):
    """Roman bronze plaque with dovetail 'handles' on each side."""
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    ear = h * 0.42
    pts = [(x0, y0), (x1, y0), (x1, cy - h * 0.18), (x1 + ear, cy - h * 0.42), (x1 + ear * 0.8, cy), (x1 + ear, cy + h * 0.42), (x1, cy + h * 0.18),
           (x1, y1), (x0, y1), (x0, cy + h * 0.18), (x0 - ear, cy + h * 0.42), (x0 - ear * 0.8, cy), (x0 - ear, cy - h * 0.42), (x0, cy - h * 0.18)]
    out = [f'<path d="{pd(shift(pts, 4, 6))}" fill="#2A1A0A" opacity="0.45"/>']
    out.append(f'<path d="{pd(pts)}" fill="#5A3A1E"/>')
    out.append(f'<path d="{pd(pts)}" fill="{D.lin([(0, "#8A6030"), (0.45, "#5A3A1A"), (1, "#3A2410")])}"/>')
    out.append(strokes(D.nid(), pd(pts), bbox(pts), ["#9A7040", "#2A1A0A", "#4A7060"], seed, n=70, angle=-4, length=(20, 60), width=(1, 3), opacity=(0.12, 0.3)))
    inner = rect_pts(x0 + 10, y0 + 10, x1 - 10, y1 - 10, 20, seed, 0.3)
    out.append(f'<path d="{pd(inner)}" fill="none" stroke="#D8B060" stroke-width="2" opacity="0.8"/>')
    out.append(f'<path d="{pd(pts)}" fill="none" stroke="#E8C070" stroke-width="2.2" opacity="0.7"/>')
    rnd = random.Random(seed)
    for _ in range(14):     # verdigris spots
        out.append(f'<path d="{blob(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(3, 9), rnd.uniform(2, 5), rnd.randint(1, 99), 0.3, 8)}" fill="#5A9A84" opacity="{rnd.uniform(0.2, 0.45):.2f}"/>')
    for sx in (x0 - ear * 0.55, x1 + ear * 0.55):
        out.append(f'<circle cx="{sx:.1f}" cy="{cy:.1f}" r="4.5" fill="#E8C070"/><circle cx="{sx - 1:.1f}" cy="{cy - 1:.1f}" r="2" fill="#FFF0C0"/>')
    return "".join(out)


@design("the-soul-is-dyed")
def soul_is_dyed():
    D = Doc2("ww-sd")
    # the view: a dawn sky and sea, dyed rose and gold
    out = [sky(D, [(0, "#4A4E8E"), (0.3, "#9A7AB0"), (0.48, "#EE9AA0"), (0.6, "#FFC890"), (0.66, "#FFE2A8")], 3, 420,
               ["#FFFFFF", "#F8B8B0", "#C8A0D0", "#FFD8A0"], 70)]
    HZ = 330
    out.append(soft_glow(D, 300, HZ, 230, "#FFE2A0", 0.85))
    for k, (x, y, w) in enumerate(((180, 170, 140), (420, 140, 160), (300, 230, 120), (500, 250, 90), (110, 250, 90))):
        out.append(puff_cloud(D, x, y, w, 10 + k, pal=("#FFE0C8", "#F2A8A8", "#A878A0"), rows=1, op=0.85))
    out.append(f'<path d="{smooth_closed(ell_pts(300, HZ, 36, 36, 180, 360, 20) + [(336, HZ), (264, HZ)])}" fill="#FFF2C0"/>')
    out.append(f'<circle cx="300" cy="{HZ}" r="36" fill="none" stroke="#FFE0A0" stroke-width="5" opacity="0.4"/>')
    # islands on the horizon
    for k, pts in enumerate(([(80, HZ), (120, HZ - 16), (160, HZ - 10), (200, HZ)], [(380, HZ), (420, HZ - 12), (470, HZ - 20), (520, HZ)])):
        out.append(f'<path d="{smooth_closed(pts)}" fill="#8A6A9A" opacity="0.8"/>')
    sea_d = f"M -10 {HZ} L 610 {HZ} L 610 430 L -10 430 Z"
    out.append(f'<path d="{sea_d}" fill="{D.lin([(0, "#F6B49A"), (0.4, "#B8789A"), (1, "#5A4A80")])}"/>')
    rnd = random.Random(4)
    gl = []
    for _ in range(140):
        y = HZ + 2 + rnd.random() ** 1.3 * 100
        k = (y - HZ) / 100
        spread = 20 + k * 120
        x = 300 + rnd.gauss(0, spread * 0.5)
        L_ = 6 + k * 30
        gl.append(f'<path d="M {x - L_ / 2:.1f} {y:.1f} L {x + L_ / 2:.1f} {y:.1f}" stroke="{rnd.choice(["#FFF4C8", "#FFE0A0", "#FFFFFF"])}" stroke-width="{1 + k * 2:.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
    for _ in range(90):
        y = HZ + 2 + rnd.random() * 100
        x = rnd.uniform(-10, 610)
        gl.append(f'<path d="M {x:.1f} {y:.1f} l {8 + (y - HZ) * 0.3:.1f} 0" stroke="{rnd.choice(["#4A3A70", "#E8A0A0", "#FFD0B0"])}" stroke-width="1.4" opacity="0.4"/>')
    out.append("".join(gl))
    # a small sailing ship and gulls
    sx, sy = 448, HZ + 22
    out.append(f'<path d="{pd([(sx - 18, sy), (sx + 18, sy), (sx + 12, sy + 6), (sx - 14, sy + 6)])}" fill="#3A2A4A"/>')
    out.append(f'<path d="{pd([(sx - 1, sy - 2), (sx - 1, sy - 34), (sx + 16, sy - 6)])}" fill="#4A3A5A"/>')
    out.append(f'<path d="{pd([(sx - 3, sy - 2), (sx - 3, sy - 28), (sx - 16, sy - 6)])}" fill="#5A4A6A"/>')
    for x, y in ((210, 270), (232, 262), (380, 250)):
        out.append(bird_v(x, y, 7, "#3A2A4A", 0.8))
    # the marble wall and its arch
    cx, spring, R = 300, 226, 160
    SILL = 404
    wall = f"M -10 -10 L 610 -10 L 610 610 L -10 610 Z M {cx - R} {SILL + 2} L {cx - R} {spring} A {R} {R} 0 0 1 {cx + R} {spring} L {cx + R} {SILL + 2} Z"
    out.append(f'<path d="{wall}" fill="#E8DCC4" fill-rule="evenodd"/>')
    out.append(f'<path d="{wall}" fill-rule="evenodd" fill="{D.lin([(0, "#FFE8C8", 0.5), (0.5, "#E8DCC4", 0), (1, "#8A7A64", 0.35)])}"/>')
    cid = D.clip(f'<path d="{wall}" clip-rule="evenodd"/>')
    blk = []
    for j in range(16):
        y = j * 40
        off = (j % 2) * 60
        blk.append(f'<path d="M -10 {y} L 610 {y}" stroke="#B8A888" stroke-width="1.4" opacity="0.55"/>')
        for i in range(-1, 6):
            x = off + i * 120
            blk.append(f'<path d="M {x} {y} L {x} {y + 40}" stroke="#B8A888" stroke-width="1.4" opacity="0.55"/>')
    blk.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-40, -10, 610, 610), ["#FFFFFF", "#C8B898", "#F6EAD0"], 5, n=200, angle=-80,
                       length=(10, 40), width=(2, 5), opacity=(0.12, 0.3)))
    blk.append(soft_glow(D, 300, 420, 260, "#FFC890", 0.35))
    out.append(f'<g {cid}>{"".join(blk)}</g>')
    # voussoirs and keystone around the arch, pilasters at the sides
    for k in range(13):
        a0, a1 = math.radians(180 + k * 180 / 13), math.radians(180 + (k + 1) * 180 / 13)
        r0, r1 = R, R + 30
        p = [(cx + math.cos(a0) * r0, spring + math.sin(a0) * r0), (cx + math.cos(a0) * r1, spring + math.sin(a0) * r1),
             (cx + math.cos(a1) * r1, spring + math.sin(a1) * r1), (cx + math.cos(a1) * r0, spring + math.sin(a1) * r0)]
        out.append(f'<path d="{pd(p)}" fill="{mix("#F2E8D4", "#D8CAB0", (k % 3) / 3)}"/>')
        out.append(strokes(D.nid(), pd(p), bbox(p), ["#FFFFFF", "#BCAA88"], 20 + k, n=8, angle=math.degrees(a0) + 90, length=(6, 16), width=(1, 2.4), opacity=(0.2, 0.45)))
        out.append(ink(pd(p), "#8A7656", 1.2, 20 + k, 1, 0.6))
        out.append(pline([p[0], p[3]], "#5A4630", 1.6, k, 0.5, 1))
    kp = [(cx - 13, spring - R + 2), (cx + 13, spring - R + 2), (cx + 21, spring - R - 36), (cx - 21, spring - R - 36)]
    out.append(f'<path d="{pd(kp)}" fill="#F6EEDC"/>')
    out.append(f'<path d="{pd([(cx - 9, spring - R - 4), (cx + 9, spring - R - 4), (cx + 14, spring - R - 30), (cx - 14, spring - R - 30)])}" fill="none" stroke="#B8A888" stroke-width="1.4"/>')
    out.append(ink(pd(kp), "#8A7656", 1.3, 40, 1, 0.65))
    for sg in (-1, 1):
        x0 = cx + sg * R
        pil = rect_pts(min(x0, x0 + sg * 34), spring - 4, max(x0, x0 + sg * 34), SILL, 12, 41 + sg, 0.4)
        out.append(painted(D, pil, ("#FFF6E6", "#EADFC8", "#A8987C"), 42 + sg, sdir=(-sg, 0.2), sk=0.12, angle=-90, n=14, inkw=1.2, inkop=0.45, hi=0.3))
        cap = rect_pts(min(x0, x0 + sg * 44) - sg * 0, spring - 16, max(x0, x0 + sg * 44), spring - 2, 8, 44 + sg, 0.3)
        out.append(painted(D, cap, ("#FFF8EE", "#EEE2CC", "#A8987C"), 45 + sg, sdir=(0, 1), sk=0.25, n=4, inkw=1.2, hi=0.4))
    # deep sill, with warm light falling on it, a scroll and a potted myrtle
    top_s = [(cx - R - 40, SILL - 6), (cx + R + 40, SILL - 6), (cx + R + 52, SILL + 10), (cx - R - 52, SILL + 10)]
    out.append(f'<path d="{pd(top_s)}" fill="#F6ECDA"/>')
    out.append(f'<path d="{pd(top_s)}" fill="{D.lin([(0, "#FFD8A0", 0.55), (1, "#FFD8A0", 0)], 0.5, 0, 0.5, 1)}"/>')
    front_s = [(cx - R - 52, SILL + 10), (cx + R + 52, SILL + 10), (cx + R + 52, SILL + 26), (cx - R - 52, SILL + 26)]
    out.append(f'<path d="{pd(front_s)}" fill="#D2C4A8"/>')
    out.append(strokes(D.nid(), pd(front_s), bbox(front_s), ["#FFFFFF", "#A8987C"], 50, n=40, angle=0, length=(20, 50), width=(1, 2), opacity=(0.2, 0.4)))
    out.append(f'<path d="{pd([(cx - R - 52, SILL + 26), (cx + R + 52, SILL + 26), (cx + R + 52, SILL + 34), (cx - R - 52, SILL + 34)])}" fill="#3A2A18" opacity="0.25"/>')
    out.append(ink(pd(top_s), "#8A7656", 1.3, 51, 1, 0.6) + ink(pd(front_s), "#8A7656", 1.3, 52, 1, 0.6))
    out.append(scroll_roll(D, 382, SILL - 6, 100, 9, -4, 51, knob=DARKWOOD, tag=("#F6E2B8", "#E2C890", "#9A7A4A")))
    px, py = 204, SILL + 2
    out.append(painted(D, [(px - 20, py - 34), (px + 20, py - 34), (px + 15, py), (px - 15, py)], TERRACOTTA, 52, sdir=(0.8, 0.3), sk=0.22, n=10, inkw=1.2, hi=0.4))
    out.append(dab_crown(D, px, py - 60, 30, 28, [("#9AB87A", "#4A7A44", "#22442A")], 53, n=120, size=(2.5, 5), light=(0.2, -0.9), inkw=0.9))
    for j in range(6):
        out.append(f'<circle cx="{px + random.Random(j).uniform(-20, 20):.1f}" cy="{py - 60 + random.Random(j + 7).uniform(-18, 14):.1f}" r="2.2" fill="#FFFFFF"/>')
    # the bronze plaque with the words
    out.append(tabula_ansata(D, 300, 484, 390, 88, 60))
    out.append(gilt_lines(D, 300, 475, 36, ["THE SOUL IS DYED", "BY THE THOUGHTS"], CINZEL, 30, max_w=340, ls=4, seed=61, deboss="#140A02"))
    out.append(byline(552, "MARCUS AURELIUS · 121–180", "#4A3420", size=18, ls=4, max_w=360))
    return finish_w(D, out, 62)


# ================================================================ 9. festina lente — the dolphin and the anchor, under the sea
def tube_outline(spine, widths):
    """Closed outline around a polyline spine with per-point widths."""
    left, right = [], []
    n = len(spine)
    for i, (x, y) in enumerate(spine):
        a, b = spine[max(i - 1, 0)], spine[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = widths[i] / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left, right


def dolphin(D, spine_ctrl, s, seed, pal=(("#B8D0E0", "#5E7E9A", "#2A3E56")), belly="#F2F0E8"):
    """A bottlenose dolphin along a curved spine (control points from beak tip to tail): rostrum, melon, dorsal fin,
    flipper, pale belly on the 'right' side of the spine, flukes."""
    sp = catmull(spine_ctrl, 8)
    n = len(sp)
    ws = []
    for i in range(n):
        t = i / (n - 1)
        if t < 0.04:
            w = 0.2 + t / 0.04 * 0.25
        elif t < 0.1:
            w = 0.45 + (t - 0.04) / 0.06 * 0.35
        elif t < 0.35:
            w = 0.8 + (t - 0.1) / 0.25 * 0.2
        else:
            w = 1.0 * (1 - (t - 0.35) / 0.65) ** 1.1 + 0.1
        ws.append(w * 50 * s)
    left, right = tube_outline(sp, ws)
    body = left + right[::-1]
    out = [painted(D, body, pal, seed, sdir=(0.2, 1), sk=0.12, angle=-20, n=60, slen=(10, 30), sw=(1, 2.6), inkw=1.6, inkc="#14202E", hi=0.4)]
    # belly: a pale strip along the right side
    bl = [(x * 0.28 + rx * 0.72, y * 0.28 + ry * 0.72) for (x, y), (rx, ry) in zip(left, right)]
    belly_pts = right[2:int(n * 0.62)] + bl[2:int(n * 0.62)][::-1]
    out.append(f'<path d="{smooth_closed(belly_pts)}" fill="{belly}" opacity="0.75"/>')
    # dorsal fin on the left side around t=0.4, flipper near t=0.18 on the right side
    i = int(n * 0.42)
    (x0, y0), (x1, y1) = sp[i], sp[i + 3]
    a = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(a), math.cos(a)
    bx, by = left[i]
    fin = [(bx - math.cos(a) * 10 * s, by - math.sin(a) * 10 * s), (bx + nx * 28 * s + math.cos(a) * 12 * s, by + ny * 28 * s + math.sin(a) * 12 * s),
           (bx + math.cos(a) * 18 * s, by + math.sin(a) * 18 * s)]
    out.append(painted(D, fin, pal, seed + 1, sk=0.15, n=6, inkw=1.4, inkc="#14202E", hi=0.3))
    i = int(n * 0.2)
    (x0, y0), (x1, y1) = sp[i], sp[i + 2]
    a = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(a), math.cos(a)
    fx, fy = right[i]
    fl = [(fx, fy), (fx - nx * 24 * s + math.cos(a) * 18 * s, fy - ny * 24 * s + math.sin(a) * 18 * s), (fx + math.cos(a) * 14 * s, fy + math.sin(a) * 14 * s)]
    out.append(painted(D, fl, pal, seed + 2, sk=0.15, n=4, inkw=1.3, inkc="#14202E", hi=0.3))
    # flukes
    (x0, y0), (x1, y1) = sp[-3], sp[-1]
    a = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(a), math.cos(a)
    tx_, ty_ = x1, y1
    fk = [(tx_ - math.cos(a) * 4, ty_ - math.sin(a) * 4), (tx_ + nx * 30 * s + math.cos(a) * 14 * s, ty_ + ny * 30 * s + math.sin(a) * 14 * s),
          (tx_ + math.cos(a) * 8 * s, ty_ + math.sin(a) * 8 * s), (tx_ - nx * 30 * s + math.cos(a) * 14 * s, ty_ - ny * 30 * s + math.sin(a) * 14 * s)]
    out.append(painted(D, fk, pal, seed + 3, sk=0.15, n=6, inkw=1.4, inkc="#14202E", hi=0.3))
    # eye, mouth line, blowhole
    i = int(n * 0.1)
    ex, ey = sp[i][0] * 0.55 + left[i][0] * 0.45, sp[i][1] * 0.55 + left[i][1] * 0.45
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.6 * s:.1f}" fill="#0A1018"/><circle cx="{ex + 0.8 * s:.1f}" cy="{ey - 0.8 * s:.1f}" r="{0.9 * s:.1f}" fill="#FFFFFF"/>')
    mi = int(n * 0.06)
    out.append(pline([sp[1], (sp[mi][0] * 0.6 + right[mi][0] * 0.4, sp[mi][1] * 0.6 + right[mi][1] * 0.4)], "#14202E", 1.4, seed, 0.8, 1))
    # highlight along the back
    out.append(taper([(x * 0.55 + sx * 0.45, y * 0.55 + sy * 0.45) for (x, y), (sx, sy) in list(zip(left, sp))[int(n * 0.12):int(n * 0.55):3]], 4 * s, 1, "#FFFFFF", 0.5))
    return "".join(out)


def anchor(D, cx, top, h, seed, pal=(("#8A8E96", "#4A4E58", "#1E2028")), rust="#9A5A2E"):
    """Old iron anchor: ring, wooden stock, shank, curved arms with flukes. Returns (svg, shank x)."""
    out = []
    # ring
    out.append(f'<circle cx="{cx}" cy="{top + 14}" r="16" fill="none" stroke="{pal[2]}" stroke-width="8"/>')
    out.append(f'<circle cx="{cx}" cy="{top + 14}" r="16" fill="none" stroke="{pal[0]}" stroke-width="2.4" opacity="0.6"/>')
    # shank
    sh = rect_pts(cx - 9, top + 28, cx + 9, top + h - 20, 14, seed, 0.3)
    out.append(painted(D, sh, pal, seed, sdir=(1, 0.1), sk=0.25, angle=-90, n=18, inkw=1.4, inkc="#0A0A10", hi=0.4))
    # arms
    base = (cx, top + h - 24)
    for sg in (-1, 1):
        arm = catmull([base, (cx + sg * 50, top + h - 20), (cx + sg * 92, top + h - 56), (cx + sg * 102, top + h - 92)], 6)
        out.append(taper(arm, 22, 12, pal[1]))
        out.append(taper([(x, y - 4) for x, y in arm], 6, 3, pal[0], 0.5))
        out.append(pline(arm, "#0A0A10", 1.4, seed + sg, 0.5, 1))
        tip = arm[-1]
        fluke = [(tip[0] - sg * 4, tip[1] + 18), (tip[0] + sg * 22, tip[1] - 6), (tip[0] + sg * 4, tip[1] - 26), (tip[0] - sg * 14, tip[1] - 4)]
        out.append(painted(D, fluke, pal, seed + 5 + sg, sk=0.2, n=6, inkw=1.4, inkc="#0A0A10", hi=0.4))
    out.append(painted(D, blob_pts(base[0], base[1] + 6, 16, 10, seed + 8, 0.05, 12), pal, seed + 9, sk=0.2, n=4, inkw=1.3, inkc="#0A0A10", hi=0.4))
    # wooden stock across the top of the shank, with iron bands
    st = rect_pts(cx - 92, top + 42, cx + 92, top + 62, 16, seed + 10, 0.4)
    out.append(painted(D, st, WOOD, seed + 11, sdir=(0.2, 1), sk=0.25, angle=0, n=20, inkw=1.4, hi=0.4))
    for x in (cx - 76, cx - 16, cx + 16, cx + 76):
        out.append(f'<rect x="{x - 3}" y="{top + 40}" width="6" height="24" fill="{pal[2]}"/>')
    rnd = random.Random(seed)
    for _ in range(26):
        out.append(f'<circle cx="{cx + rnd.uniform(-8, 8):.1f}" cy="{top + rnd.uniform(70, h - 30):.1f}" r="{rnd.uniform(1, 3):.1f}" fill="{rust}" opacity="{rnd.uniform(0.35, 0.7):.2f}"/>')
    return "".join(out)


@design("festina-lente")
def festina_lente():
    D = Doc2("ww-fl")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#3E9AB0"), (0.45, "#1E6A88"), (1, "#0E3A54")])}"/>']
    out.append(soft_glow(D, 300, 0, 380, "#C8F0F0", 0.55))
    # god rays
    rnd = random.Random(2)
    for k in range(9):
        x = 60 + k * 62 + rnd.uniform(-20, 20)
        out.append(f'<path d="{pd([(x - 14, -10), (x + 14, -10), (x + 60 + k * 4, 610), (x - 30 + k * 4, 610)])}" fill="#E8FFFF" opacity="{rnd.uniform(0.04, 0.1):.2f}"/>')
    out.append(wave_lines(3, (0, 6, 600, 40), ["#E8FFFF", "#9AD8E8"], n=30, L=(30, 70), w=2, amp=3))
    # sea floor: sand, rocks, weed
    fl = ridge([(-20, 506), (120, 494), (260, 506), (400, 496), (620, 504)], 4, 6)
    out.append(hill(D, fl, 620, ("#F2DCA8", "#C8A86E", "#7A6440"), 5, inkw=1.2, inkop=0.4, n=60))
    out.append(specks(6, (0, 500, 600, 600), ["#FFF2D0", "#8A6A40"], 120, (0.8, 2.2), (0.4, 0.8)))
    for k, (x, h_, c) in enumerate(((60, 160, "#3E8A5A"), (90, 110, "#5AA06A"), (520, 140, "#3E8A5A"), (548, 190, "#2E7048"), (500, 90, "#6AB07A"))):
        pts = [(x + math.sin(t * 0.08 + k) * 12, 512 - t) for t in range(0, h_, 10)]
        out.append(taper(pts, 10, 3, c, 0.9))
        out.append(taper([(px + 3, py) for px, py in pts], 3, 1, "#A8E0B0", 0.5))
    for k, (x, y, r) in enumerate(((84, 512, 26), (530, 510, 30), (482, 506, 14))):
        out.append(painted(D, blob_pts(x, y, r, r * 0.6, 7 + k, 0.1, 14), ("#8AA0A8", "#4E6470", "#1E2E36"), 8 + k, sk=0.2, n=10, inkw=1.2, hi=0.4))
    # small fish
    for k, (x, y, s_, f) in enumerate(((120, 300, 1.0, 1), (148, 318, 0.8, 1), (470, 220, 0.9, -1), (500, 240, 0.7, -1))):
        body = T([(-10, 0), (0, -5), (10, -1), (14, 0), (10, 2), (0, 5)], x, y, s_, f < 0)
        out.append(f'<path d="{smooth_closed(body)}" fill="#F2C24A"/>')
        out.append(f'<path d="{pd(T([(-9, 0), (-16, -5), (-15, 5)], x, y, s_, f < 0))}" fill="#E8A03A"/>')
    # bubbles rising from the dolphin
    for k in range(14):
        bx, by = 350 + rnd.uniform(-20, 30), 220 - k * 12 + rnd.uniform(-4, 4)
        r = rnd.uniform(2, 5)
        out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{r:.1f}" fill="none" stroke="#E8FFFF" stroke-width="1.2" opacity="0.7"/><circle cx="{bx - r * 0.3:.1f}" cy="{by - r * 0.3:.1f}" r="{r * 0.3:.1f}" fill="#FFFFFF" opacity="0.8"/>')
    # the emblem: dolphin coiled round the anchor's shank
    spine = [(190, 410), (214, 380), (252, 352), (300, 334), (344, 322), (372, 298), (370, 268), (344, 254), (304, 254), (270, 264)]
    dol = dolphin(D, spine, 1.0, 20)
    out.append(cast(D, 300, 508, 120, 10, "#0A2030", 0.5, 21))
    out.append(dol)
    out.append(anchor(D, 300, 214, 300, 22))
    front = D.clip('<path d="M 270 296 L 336 296 L 336 372 L 270 372 Z"/>')
    out.append(f'<g {front}>{dol}</g>')
    # lettering
    out.append(gilt(D, 300, 116, "Festina lente", SERIF_IT, 84, max_w=460, seed=30, deboss="#04161E", pal="pale"))
    out.append(ruled(300, 160, "MAKE HASTE SLOWLY", "#E8F6F2", font=CINZEL, size=20, ls=6, line_w=36, gap=14))
    out.append(byline(540, "AUGUSTUS CAESAR · 63 BC – AD 14", "#2A1E10", size=17, ls=3, max_w=420))
    return finish_w(D, out, 31, "#0A1A24", 0.5)


# ================================================================ 10. life speeds by — an hourglass on the sill, swifts racing past
def hourglass(D, cx, top, h, w, seed, frame=WOOD, sand=("#FCE6A8", "#E2B460", "#9A6A24"), fill=0.62):
    """Turned-wood hourglass: two discs, three posts, a pinched glass with sand running into a cone below."""
    out = [cast(D, cx + 16, top + h + 2, w * 0.9, 9, strength=0.45, seed=seed)]
    disc_h = h * 0.07
    gy0, gy1 = top + disc_h, top + h - disc_h
    mid = (gy0 + gy1) / 2
    gw = w * 0.42
    # back post
    out.append(painted(D, rect_pts(cx - 4, gy0, cx + 4, gy1, 20, seed, 0.3), frame, seed, sk=0.25, angle=-90, n=6, inkw=1.0, hi=0.3))
    # glass outline
    half = []
    for i in range(21):
        t = i / 20
        y = gy0 + 4 + (gy1 - gy0 - 8) * t
        u = abs(t - 0.5) * 2
        r = 5 + (gw - 5) * (math.sin(u * math.pi / 2) ** 0.9) * (1 - 0.25 * u ** 6)
        half.append((cx + r, y))
    glass = half + [(2 * cx - x, y) for x, y in half[::-1]]
    gd = smooth_closed(glass)
    out.append(f'<path d="{gd}" fill="#E8F2F4" opacity="0.35"/>')
    cid = D.clip(f'<path d="{gd}"/>')
    inner = []
    # sand left in the upper bulb (a dished surface), the falling stream, the cone below
    top_level = gy0 + (mid - gy0) * (1 - fill * 0.55)
    inner.append(f'<path d="M {cx - gw:.1f} {top_level:.1f} Q {cx:.1f} {top_level + 16:.1f} {cx + gw:.1f} {top_level:.1f} L {cx + gw:.1f} {mid:.1f} L {cx - gw:.1f} {mid:.1f} Z" fill="{sand[1]}"/>')
    inner.append(f'<path d="M {cx - gw:.1f} {top_level:.1f} Q {cx:.1f} {top_level + 16:.1f} {cx + gw:.1f} {top_level:.1f}" stroke="{sand[0]}" stroke-width="3" fill="none"/>')
    inner.append(f'<path d="M {cx - 1.4:.1f} {mid:.1f} L {cx + 1.4:.1f} {mid:.1f} L {cx + 1.2:.1f} {gy1 - 30:.1f} L {cx - 1.2:.1f} {gy1 - 30:.1f} Z" fill="{sand[1]}"/>')
    cone_top = gy1 - 34
    inner.append(f'<path d="M {cx - gw - 4:.1f} {gy1:.1f} Q {cx - gw * 0.4:.1f} {gy1 - 10:.1f} {cx:.1f} {cone_top:.1f} Q {cx + gw * 0.4:.1f} {gy1 - 10:.1f} {cx + gw + 4:.1f} {gy1:.1f} Z" fill="{sand[1]}"/>')
    inner.append(f'<path d="M {cx:.1f} {cone_top:.1f} Q {cx + gw * 0.4:.1f} {gy1 - 10:.1f} {cx + gw + 4:.1f} {gy1:.1f} L {cx + gw:.1f} {gy1:.1f} Z" fill="{sand[2]}" opacity="0.4"/>')
    inner.append(specks(seed, (cx - gw, top_level, cx + gw, gy1), [sand[0], sand[2]], 40, (0.5, 1.2), (0.4, 0.8)))
    inner.append(f'<path d="{gd}" fill="{cyl(D, cx - gw, cx + gw, 0, 0, ("#FFFFFF", "#D8E8EC", "#7A9AA4"), -1, 0.35)}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(gd, "#6A8A94", 1.3, seed, 1, 0.6))
    out.append(taper([(cx - gw * 0.62, gy0 + 16), (cx - gw * 0.8, gy0 + 40), (cx - gw * 0.5, mid - 16)], 4, 1.5, "#FFFFFF", 0.8))
    out.append(taper([(cx - gw * 0.6, mid + 20), (cx - gw * 0.82, gy1 - 40)], 4, 1.5, "#FFFFFF", 0.7))
    # front posts
    for sg in (-1, 1):
        px_ = cx + sg * (gw + 10)
        post = []
        for i in range(9):
            t = i / 8
            y = gy0 + (gy1 - gy0) * t
            r = 4 + 2.4 * abs(math.sin(t * math.pi * 3))
            post.append((px_ + r, y))
        post = post + [(2 * px_ - x, y) for x, y in post[::-1]]
        out.append(painted(D, post, frame, seed + 3 + sg, sdir=(1, 0.2), sk=0.25, angle=-90, n=8, inkw=1.1, hi=0.45))
    # discs top and bottom
    for y0 in (top, gy1):
        dk_ = rect_pts(cx - w / 2, y0, cx + w / 2, y0 + disc_h, 12, seed + int(y0), 0.3)
        out.append(painted(D, dk_, frame, seed + 7 + int(y0), sdir=(0.4, 1), sk=0.25, angle=0, n=10, inkw=1.3, hi=0.45))
        out.append(f'<path d="M {cx - w / 2 + 4:.1f} {y0 + disc_h * 0.45:.1f} L {cx + w / 2 - 4:.1f} {y0 + disc_h * 0.45:.1f}" stroke="{frame[2]}" stroke-width="1.2" opacity="0.6"/>')
    return "".join(out)


def swift(x, y, s, ang=0, col="#2A2430", trail=True):
    """A common swift in fast flight: scythe wings, short forked tail, with speed lines behind."""
    pts = T([(-2, 0), (-14, -6), (-34, -14), (-50, -16), (-30, -6), (-8, 2), (-30, 8), (-50, 18), (-34, 14), (-14, 6), (-4, 2), (6, 1), (10, 0), (6, -2)], x, y, s, False, ang)
    out = [f'<path d="{smooth_closed(pts)}" fill="{col}"/>']
    out.append(f'<path d="{pd(T([(-6, 0), (-16, -4), (-12, 0), (-16, 4)], x, y, s, False, ang))}" fill="{col}"/>')
    if trail:
        for k, dy in enumerate((-6, 0, 6)):
            a, b = T([(-58, dy * 1.4), (-100 - k * 14, dy * 1.8)], x, y, s, False, ang)
            out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round" opacity="0.6"/>')
    return "".join(out)


@design("life-speeds-by")
def life_speeds_by():
    D = Doc2("ww-ls")
    # warm ochre plaster wall
    out = [f'<rect width="600" height="600" fill="#D8A868"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 610, 610), ["#E8BC7A", "#C08A4A", "#F0C88A", "#B8803E"], 2,
                       n=260, angle=-62, length=(30, 90), width=(5, 14), opacity=(0.15, 0.35)))
    out.append(blooms(3, ["#C8884A", "#F2CC90"], 8, (0, 0, 600, 600), (60, 140), (0.08, 0.15)))
    # the window opening
    wx0, wx1, wy0, wy1 = 120, 480, 216, 452
    win = f"M {wx0} {wy1} L {wx0} {wy0 + 40} Q {wx0} {wy0} {wx0 + 40} {wy0} L {wx1 - 40} {wy0} Q {wx1} {wy0} {wx1} {wy0 + 40} L {wx1} {wy1} Z"
    cid = D.clip(f'<path d="{win}"/>')
    v = [f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="{D.lin([(0, "#7AB0DA"), (0.6, "#CDE2EA"), (1, "#F6E2B8")])}"/>']
    v.append(soft_glow(D, 420, 330, 140, "#FFF4D0", 0.7))
    for k, (x, y, w_) in enumerate(((200, 262, 130), (390, 248, 110))):
        v.append(puff_cloud(D, x, y, w_, 5 + k, pal=("#FFFFFF", "#F6F2EC", "#C8C8D4"), rows=2))
        v.append(f'<path d="M {x + w_ * 0.6:.1f} {y - 4:.1f} l 50 0 M {x + w_ * 0.6:.1f} {y + 6:.1f} l 70 0" stroke="#FFFFFF" stroke-width="2" opacity="0.6"/>')
    l1 = ridge([(100, 382), (200, 366), (300, 376), (420, 360), (500, 372)], 6, 6)
    v.append(hill(D, l1, 460, ("#B8C8B0", "#98AE9A", "#78907E"), 7, inkw=0, n=20))
    l2 = ridge([(100, 410), (220, 398), (340, 408), (500, 396)], 8, 5)
    v.append(hill(D, l2, 460, ("#C8D08A", "#9AAE5E", "#6A7E3A"), 9, inkw=0, n=24))
    for k, x in enumerate((150, 172, 440, 458)):
        v.append(cypress(D, x, 412, 70 + (k % 2) * 14, 10 + k, pal=("#6A8A5A", "#3E5E3A", "#1E3220"), light=1))
    v.append(umbrella_pine(D, 380, 404, 64, 14, light=1))
    # swifts screaming past
    for k, (x, y, s_, a) in enumerate(((236, 300, 1.0, -8), (316, 284, 0.8, -4), (352, 322, 0.65, 2), (200, 340, 0.6, -14))):
        v.append(swift(x, y, s_, a))
    out.append(f'<g {cid}>{"".join(v)}</g>')
    # window reveal (deep wall), shutters folded back
    out.append(f'<path d="{win}" fill="none" stroke="#A87038" stroke-width="10" opacity="0.55"/>')
    out.append(ink(win, INK, 2, 15, 1, 0.6))
    for sg, x0 in ((-1, wx0), (1, wx1)):
        sh = [(x0, wy0 + 30), (x0 + sg * 56, wy0 + 24), (x0 + sg * 56, wy1 + 4), (x0, wy1)]
        out.append(painted(D, sh, ("#7AB0A0", "#3E7A6A", "#1E4A40"), 16 + sg, sdir=(sg, 0.2), sk=0.12, angle=-90, n=30, inkw=1.4, hi=0.3))
        for j in range(8):
            y = wy0 + 40 + j * 24
            out.append(pline([(x0 + sg * 6, y), (x0 + sg * 50, y - 2)], "#1E4A40", 1.6, j, 0.6, 1))
    # stone sill
    sill = [(wx0 - 24, wy1 - 4), (wx1 + 24, wy1 - 4), (wx1 + 30, wy1 + 8), (wx0 - 30, wy1 + 8)]
    out.append(f'<path d="{pd(sill)}" fill="#F6E8CC"/>')
    sf = [(wx0 - 30, wy1 + 8), (wx1 + 30, wy1 + 8), (wx1 + 30, wy1 + 24), (wx0 - 30, wy1 + 24)]
    out.append(f'<path d="{pd(sf)}" fill="#D2BC94"/>')
    out.append(strokes(D.nid(), pd(sf), bbox(sf), ["#FFFFFF", "#A8946E"], 18, n=40, angle=0, length=(20, 60), width=(1, 2), opacity=(0.2, 0.4)))
    out.append(ink(pd(sill), "#8A7050", 1.3, 18, 1, 0.6) + ink(pd(sf), "#8A7050", 1.3, 19, 1, 0.6))
    out.append(f'<path d="{pd([(wx0 - 30, wy1 + 22), (wx1 + 30, wy1 + 22), (wx1 + 30, wy1 + 30), (wx0 - 30, wy1 + 30)])}" fill="#5A3A1A" opacity="0.3"/>')
    # the letter on the sill, the hourglass
    out.append(scroll_roll(D, 206, wy1 - 8, 110, 10, 6, 19, knob=DARKWOOD, tag=("#F6E2B8", "#E2C890", "#9A7A4A")))
    out.append(f'<path d="{blob(232, wy1 - 4, 9, 7, 20, 0.15, 10)}" fill="#B8302A"/>')
    out.append(hourglass(D, 372, 254, 196, 108, 21))
    out.append(soft_glow(D, 370, 400, 70, "#FFF0C0", 0.25))
    # lettering on the wall above
    out.append(lines(D, 300, 108, 50, ["While we are postponing,", "life speeds by."], SERIF_IT, 46, "#4A1E0E", max_w=460))
    out.append(byline(186, "SENECA · c. 4 BC – AD 65", "#5A2E12", size=18, ls=4, max_w=360))
    out.append(byline(536, "LETTERS TO LUCILIUS · I", "#5A2E12", size=17, ls=4, max_w=360))
    return finish_w(D, out, 22)


# ================================================================ 11. omnia vincit amor — doves on a bronze bowl, a Pompeian fresco
def dove(D, x, y, s, seed, flip=False, pose="perch", head_down=0.0):
    """White dove: plump body, small head, folded wing with grey primaries, coral feet, dark eye."""
    def L(pts):
        return T(pts, x, y, s, flip)
    pal = ("#FFFFFF", "#ECEAE6", "#9A9CA8")
    out = []
    tail = L([(-26, 2), (-48, 10), (-52, 18), (-30, 14)])
    out.append(painted(D, tail, pal, seed, sk=0.2, n=6, inkw=1.2, inkc="#5A5A66", hi=0.3))
    body = L([(-30, 4), (-18, -12), (4, -16), (18, -10), (22, 2), (12, 14), (-8, 16), (-24, 12)])
    out.append(painted(D, body, pal, seed + 1, sdir=(0.3, 1), sk=0.2, angle=-20, n=16, inkw=1.4, inkc="#5A5A66", hi=0.5))
    hd = -10 + head_down * 26
    neck = L([(8, -12), (18, -18 + hd * 0.5), (22, -26 + hd), (30, -26 + hd), (32, -18 + hd), (22, -4)])
    out.append(painted(D, neck, pal, seed + 2, sk=0.15, n=6, inkw=1.3, inkc="#5A5A66", hi=0.5))
    out.append(f'<path d="{pd(L([(31, -22 + hd), (39, -19 + hd), (31, -18 + hd)]))}" fill="#C8907A"/>')
    ex, ey = L([(26, -22 + hd)])[0]
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{1.8 * s:.1f}" fill="#2A1A1A"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="{2.8 * s:.1f}" fill="none" stroke="#E8B0A0" stroke-width="1"/>')
    wing = L([(-26, 0), (-8, -12), (10, -8), (6, 4), (-14, 8)])
    out.append(painted(D, wing, ("#FFFFFF", "#E2E2E4", "#8A8C98"), seed + 3, sk=0.2, angle=0, n=8, inkw=1.2, inkc="#5A5A66", hi=0.4))
    for j in range(4):
        a, b = L([(-22 + j * 6, 2 + j)])[0], L([(-32 + j * 4, 8 + j)])[0]
        out.append(pline([a, b], "#8A8C98", 1.1, j, 0.6, 1))
    if pose == "perch":
        for dx in (-2, 6):
            out.append(pline(L([(dx, 14), (dx + 1, 22)]), "#D86A5A", 2.2 * s, seed, 1, 1))
    return "".join(out)


@design("omnia-vincit-amor")
def omnia_vincit_amor():
    D = Doc2("ww-ov")
    # Pompeian red field with fresco texture
    out = [f'<rect width="600" height="600" fill="#A42A22"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 610, 610), ["#C23A2E", "#8A2018", "#B83428", "#D24A3A"], 3,
                       n=300, angle=-70, length=(30, 90), width=(6, 16), opacity=(0.15, 0.35)))
    out.append(blooms(4, ["#6A1410", "#D85A44"], 10, (0, 0, 600, 600), (50, 130), (0.1, 0.2)))
    # black frame bands with fine gold lines (third-style wall)
    for (x0, y0, x1, y1, w) in ((0, 0, 600, 600, 34),):
        band = f"M -10 -10 L 610 -10 L 610 610 L -10 610 Z M {x0 + w} {y0 + w} L {x1 - w} {y0 + w} L {x1 - w} {y1 - w} L {x0 + w} {y1 - w} Z"
        out.append(f'<path d="{band}" fill="#1A1210" fill-rule="evenodd"/>')
    out.append(rule_frame(D, 46, 46, 554, 554, "#E8B84A", 2.0, 0, 0, seed=4))
    # candelabrum stems up the sides
    for sg in (-1, 1):
        x = 300 + sg * 230
        out.append(pline([(x, 520), (x, 90)], "#E8B84A", 2.2, 5 + sg, 0.85, 1))
        for k in range(5):
            y = 120 + k * 90
            out.append(f'<path d="{smooth_closed(ell_pts(x, y, 9, 3.5, 0, 360, 12))}" fill="#E8B84A"/>')
            out.append(leaf_simple(D, x, y + 30, 16, 5, -90 + sg * 40, ("#C8D88A", "#7A9A4A", "#3E5A22"), 6 + k, vein=False, inkw=0.6))
            out.append(leaf_simple(D, x, y + 30, 16, 5, -90 - sg * 40, ("#C8D88A", "#7A9A4A", "#3E5A22"), 7 + k, vein=False, inkw=0.6))
    # central panel (white ground vignette with a garland swag)
    px0, py0, px1, py1 = 108, 96, 492, 372
    panel = hg.org_rect(px0, py0, px1 - px0, py1 - py0, 8, 0.5, 14, 2)
    out.append(f'<path d="{panel}" fill="#F4ECDA"/>')
    out.append(f'<path d="{panel}" fill="{D.rad([(0, "#FFFFFF", 0.5), (1, "#C8B08A", 0.4)], r=0.7)}"/>')
    cid = D.clip(f'<path d="{panel}"/>')
    inner = []
    # garland of myrtle and roses swagged across the top
    sw_pts = catmull([(px0, py0 + 14), (200, py0 + 64), (300, py0 + 76), (400, py0 + 64), (px1, py0 + 14)], 8)
    rnd = random.Random(9)
    inner.append(taper(sw_pts, 4, 4, "#4A6A2E"))
    for i, (x, y) in enumerate(sw_pts[::2]):
        for _ in range(3):
            a = rnd.uniform(0, 360)
            inner.append(leaf_simple(D, x + rnd.uniform(-4, 4), y + rnd.uniform(-4, 4), rnd.uniform(12, 18), 5, a, ("#B8D08A", "#5E8A44", "#2A4A22"), i * 3 + _, vein=False, inkw=0.5))
    for k, t in enumerate((0.2, 0.5, 0.8)):
        x, y = sw_pts[int(t * (len(sw_pts) - 1))]
        inner.append(rose_bloom(D, x, y + 4, 11, 20 + k, pal=("#FFC8D0", "#E86A80", "#9A2A44")))
    for x in (px0 + 6, px1 - 6):
        inner.append(pline([(x, py0 + 14), (x + (8 if x < 300 else -8), py0 + 60)], "#C8382A", 2.2, 3, 0.9, 1))
    # bronze bowl on a little stand, water inside, two doves on the rim
    bx, by = 300, 296
    inner.append(cast(D, bx + 8, by + 52, 140, 12, strength=0.35, seed=12))
    inner.append(painted(D, rect_pts(bx - 12, by + 20, bx + 12, by + 46, 6, 13, 0.3), BRONZE, 14, sk=0.2, n=4, inkw=1.2, hi=0.4))
    inner.append(painted(D, ell_pts(bx, by + 48, 36, 7, 0, 360, 18)[:-1], BRONZE, 15, sk=0.2, n=4, inkw=1.2, hi=0.4))
    bowl = ell_pts(bx, by - 4, 100, 18, 0, 180, 20) + [(bx - 100, by - 4)]
    bowl = [(bx + 124, by - 4)] + [(bx + 104, by + 18), (bx + 60, by + 30), (bx, by + 33), (bx - 60, by + 30), (bx - 104, by + 18)] + [(bx - 124, by - 4)]
    inner.append(painted(D, bowl, ("#F8D498", "#C08A40", "#6A4416"), 16, sdir=(0.8, 0.6), sk=0.2, angle=0, n=20, inkw=1.4, hi=0.5))
    inner.append(f'<path d="{smooth_closed(ell_pts(bx, by - 4, 124, 19, 0, 360, 30))}" fill="#E8C070"/>')
    inner.append(f'<path d="{smooth_closed(ell_pts(bx, by - 3, 112, 14, 0, 360, 30))}" fill="#7AB0C0"/>')
    inner.append(f'<path d="{smooth_closed(ell_pts(bx, by - 3, 112, 14, 0, 360, 30))}" fill="{D.lin([(0, "#3A6A80", 0.6), (1, "#CFEAF0", 0.4)])}"/>')
    inner.append(wave_lines(17, (bx - 90, by - 9, bx + 80, by + 4), ["#FFFFFF"], n=10, L=(10, 22), w=1.2, amp=1))
    inner.append(ink(smooth_closed(ell_pts(bx, by - 4, 124, 19, 0, 360, 30)), "#6A4416", 1.4, 18, 1, 0.6))
    for k in range(10):
        a = math.radians(20 + k * 16)
        inner.append(f'<circle cx="{bx + math.cos(a) * 112:.1f}" cy="{by + 10 + math.sin(a) * 18:.1f}" r="2.4" fill="#FFE8A0" opacity="0.8"/>')
    inner.append(dove(D, bx - 74, by - 34, 1.5, 30, flip=False, head_down=0.9))
    inner.append(dove(D, bx + 78, by - 40, 1.5, 31, flip=True, head_down=0.0))
    # scattered rose petals on the ground line
    for k in range(7):
        inner.append(f'<path d="{blob(bx - 150 + k * 50 + rnd.uniform(-10, 10), by + 58 + rnd.uniform(-4, 6), 6, 3.5, 70 + k, 0.2, 8, rnd.uniform(0, 180))}" fill="#E86A80" opacity="0.85"/>')
    # a third dove fluttering down
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(panel, "#1A1210", 2.6, 19, 1, 0.8))
    out.append(rule_frame(D, px0 - 10, py0 - 10, px1 + 10, py1 + 10, "#E8B84A", 1.6, 0, 0, seed=20))
    # fresco cracks and losses
    for k in range(6):
        x, y = rnd.uniform(60, 540), rnd.uniform(60, 540)
        out.append(pline([(x, y), (x + rnd.uniform(-20, 20), y + rnd.uniform(10, 30)), (x + rnd.uniform(-30, 30), y + rnd.uniform(30, 60))], "#5A140E", 1, k, 0.5, 1))
    for k in range(4):
        out.append(f'<path d="{blob(rnd.uniform(40, 560), rnd.uniform(40, 560), rnd.uniform(4, 10), rnd.uniform(3, 7), k, 0.3, 10)}" fill="#E8D0B0" opacity="0.5"/>')
    # lettering in the red field
    out.append(letters(D, 300, 452, "Omnia vincit amor", SERIF_IT, 60, "#FBEFD8", ["#FFFFFF", "#F2D8B0", "#E8C090"], 40, max_w=420,
                       shadow="#4A0A08", angle=-30, inkc=None, wob=0.4))
    out.append(ruled(300, 492, "LOVE CONQUERS ALL", "#F2C860", font=CINZEL, size=19, ls=6, line_w=34, gap=12))
    out.append(byline(526, "VIRGIL · 70–19 BC", "#F6E2C0", size=17, ls=5, max_w=300))
    return finish_w(D, out, 41, "#2A0A06", 0.6)


# ================================================================ 12. il faut cultiver notre jardin — a seed packet on the potting bench
def cabbage(D, cx, cy, r, seed, pal=(("#C8E0A0", "#7AA65A", "#3E6A34"))):
    rnd = random.Random(seed)
    out = [cast(D, cx + 3, cy + r * 0.6, r * 1.1, r * 0.3, strength=0.35, seed=seed)]
    for k in range(7):
        a = math.radians(k * 51 + rnd.uniform(-10, 10))
        out.append(painted(D, blob_pts(cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.35, r * 0.62, r * 0.42, seed + k, 0.12, 12, math.degrees(a)),
                           pal, seed + k, sk=0.15, n=4, inkw=0.9, hi=0.3))
    out.append(painted(D, blob_pts(cx, cy - r * 0.1, r * 0.5, r * 0.42, seed + 9, 0.05, 12), ("#E8F4C8", "#B8D88A", "#6A9A4A"), seed + 9, sk=0.2, n=6, inkw=1.0, hi=0.5))
    out.append(pline([(cx - r * 0.2, cy - r * 0.3), (cx + r * 0.1, cy - r * 0.05)], "#6A9A4A", 1, seed, 0.6, 1))
    return "".join(out)


def watering_can(D, x, base, s, seed, pal=(("#C8D8D8", "#7A9A9A", "#3A5050"))):
    def L(pts):
        return T(pts, x, base, s)
    out = [cast(D, x + 4 * s, base, 40 * s, 5 * s, strength=0.4, seed=seed)]
    body = L([(-24, 0), (-26, -38), (24, -38), (26, 0)])
    out.append(painted(D, body, pal, seed, sdir=(1, 0.2), sk=0.22, angle=-90, n=10, inkw=1.3, hi=0.45))
    out.append(taper(L([(20, -12), (44, -40), (52, -50)]), 6 * s, 3.5 * s, pal[1]))
    out.append(painted(D, L([(48, -54), (60, -48), (56, -40), (46, -46)]), pal, seed + 1, sk=0.2, n=4, inkw=1.1, hi=0.4))
    out.append(ink(smooth_open(L([(-20, -38), (-14, -60), (14, -60), (20, -38)])), pal[2], 3.4 * s, seed, 1, 1))
    for j in range(3):
        out.append(f'<path d="M {L([(-24, -10 - j * 10)])[0][0]:.1f} {L([(0, -10 - j * 10)])[0][1]:.1f} L {L([(24, 0)])[0][0]:.1f} {L([(0, -10 - j * 10)])[0][1]:.1f}" stroke="{pal[2]}" stroke-width="1" opacity="0.35"/>')
    return "".join(out)


@design("cultivate-our-garden")
def cultivate_garden():
    D = Doc2("ww-cg")
    # potting bench of weathered boards
    from brasil_painted import wood_planks
    out = [wood_planks(D, 0, 600, 3, pal=("#C8A884", "#9A7A58", "#5A4430"), n=5, vertical=True)]
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFFFFF", 0), (0.7, "#2A1A0A", 0.1), (1, "#2A1A0A", 0.45)], r=0.75)}"/>')
    # spilled soil and seeds, twine, a trowel at the top-right
    rnd = random.Random(4)
    out.append(f'<path d="{blob(520, 560, 70, 30, 5, 0.25, 16)}" fill="#4A3020" opacity="0.7"/>')
    out.append(specks(6, (450, 520, 600, 600), ["#2A1A0E", "#6A4A2E"], 60, (1, 3), (0.5, 0.9)))
    # the packet, tipped a little
    ang = -3
    G = f'<g transform="rotate({ang} 300 300)">'
    pk = rect_pts(96, 64, 504, 540, 24, 7, 0.6)
    out.append(G + f'<path d="{pd(shift(pk, 8, 10))}" fill="#1A0E04" opacity="0.4"/></g>')
    inner = [painted(D, pk, ("#FFFAEC", "#F4E8CC", "#C8B088"), 8, sdir=(0.3, 1), sk=0.04, angle=-80, n=60, inkw=1.4, hi=0.2)]
    # top flap and header band
    inner.append(f'<path d="{pd([(100, 68), (500, 68), (500, 104), (100, 104)])}" fill="#2E5A3A"/>')
    inner.append(f'<path d="{pd([(100, 104), (500, 104), (500, 110), (100, 110)])}" fill="#C8A040"/>')
    inner.append(tx(300, 95, "CANDIDE · GARDEN SEEDS · 1759", CINZEL, 18, "#F6EAD0", ls=3, max_w=380))
    # the garden vignette
    vx0, vy0, vx1, vy1 = 122, 124, 478, 344
    vd = hg.org_rect(vx0, vy0, vx1 - vx0, vy1 - vy0, 9, 0.4, 14, 2)
    vc = D.clip(f'<path d="{vd}"/>')
    v = [f'<rect x="{vx0}" y="{vy0}" width="{vx1 - vx0}" height="{vy1 - vy0}" fill="{D.lin([(0, "#A8D0E8"), (0.6, "#F2EAD0")])}"/>']
    v.append(soft_glow(D, 420, 160, 80, "#FFF4C0", 0.8))
    v.append(f'<circle cx="420" cy="160" r="16" fill="#FFE07A"/>')
    l1 = ridge([(110, 214), (220, 200), (330, 210), (490, 198)], 3, 5)
    v.append(hill(D, l1, 360, ("#B8CCA0", "#94AE80", "#6A8A60"), 4, inkw=0, n=20))
    # a little house with a red roof and poplars
    hx = 360
    v.append(f'<path d="{pd([(hx - 30, 214), (hx + 30, 214), (hx + 30, 186), (hx - 30, 186)])}" fill="#F6EEDC"/>')
    v.append(f'<path d="{pd([(hx - 36, 188), (hx, 168), (hx + 36, 188)])}" fill="#C8583A"/>')
    for j in range(3):
        v.append(f'<rect x="{hx - 22 + j * 16}" y="194" width="6" height="9" fill="#5A7A9A"/>')
    for k, x in enumerate((300, 316, 412)):
        v.append(cypress(D, x, 214, 46, 20 + k, pal=("#8AAA6A", "#5A7A44", "#2E4A28"), light=1, w=12))
    # rows of the kitchen garden in perspective
    soil = [(110, 222), (490, 222), (490, 360), (110, 360)]
    v.append(f'<path d="{pd(soil)}" fill="#8A6040"/>')
    for k in range(7):
        y = 230 + k * 18 + k * k * 1.6
        v.append(f'<path d="M 110 {y:.1f} L 490 {y:.1f}" stroke="#6A4428" stroke-width="{2 + k * 0.6:.1f}" opacity="0.6"/>')
        n_ = 9 - k // 2
        for j in range(n_ + 2):
            x = 120 + j * (380 / n_) + (k % 2) * 12
            r = 5 + k * 2.2
            if k in (5, 6):
                v.append(cabbage(D, x, y + 6, r, 30 + k * 10 + j))
            elif k in (2, 3):
                v.append(f'<path d="{blob(x, y + 2, r * 0.9, r * 0.6, k * 9 + j, 0.2, 10)}" fill="{["#9ACB6A", "#7AB050"][j % 2]}"/>')
            elif k == 4:
                v.append(f'<path d="{blob(x, y, r * 0.8, r * 0.7, k * 9 + j, 0.25, 10)}" fill="#A84A8A" opacity="0.85"/>')
                v.append(f'<path d="{blob(x, y - 2, r * 0.5, r * 0.4, k * 9 + j + 1, 0.25, 10)}" fill="#C8E0A0"/>')
            else:
                v.append(f'<path d="{blob(x, y, r * 0.7, r * 0.5, k * 9 + j, 0.2, 10)}" fill="#6A9A44"/>')
    # bean poles and sunflowers on the left, the watering can
    for k, x in enumerate((140, 166, 192)):
        v.append(pline([(x, 330), (x + 8, 236)], "#7A5A3A", 2.4, k, 1, 1))
        for j in range(6):
            v.append(leaf_simple(D, x + 4 + (j % 2) * 4, 320 - j * 15, 12, 5, -150 + (j % 2) * 120, LAUREL, 40 + k * 7 + j, vein=False, inkw=0.6))
    for k, (x, h_) in enumerate(((454, 120), (474, 100))):
        v.append(pline([(x, 344), (x - 2, 344 - h_)], "#5A7A34", 3, k, 1, 1))
        for j in range(12):
            a = math.radians(j * 30)
            v.append(f'<path d="{blob(x - 2 + math.cos(a) * 11, 344 - h_ + math.sin(a) * 11, 7, 3, j, 0.1, 8, j * 30)}" fill="#F6C21C"/>')
        v.append(f'<circle cx="{x - 2}" cy="{344 - h_}" r="7" fill="#6A3A1A"/>')
        v.append(leaf_simple(D, x, 300, 18, 8, -20 - k * 140, LAUREL, 50 + k, inkw=0.6))
    v.append(watering_can(D, 248, 352, 0.9, 60))
    inner.append(f'<g {vc}>{"".join(v)}</g>')
    inner.append(ink(vd, INK, 1.8, 10, 1, 0.7))
    inner.append(f'<path d="{hg.org_rect(vx0 - 6, vy0 - 6, vx1 - vx0 + 12, vy1 - vy0 + 12, 11, 0.4, 14, 3)}" fill="none" stroke="#2E5A3A" stroke-width="1.6"/>')
    # words
    inner.append(lines(D, 300, 398, 46, ["Il faut cultiver", "notre jardin."], SERIF_IT, 46, "#24482E", max_w=380))
    inner.append(tx(300, 472, "WE MUST CULTIVATE OUR GARDEN", CINZEL, 17, "#8A4A22", ls=2, max_w=360))
    inner.append(pline([(160, 486), (300, 487), (440, 486)], "#C8A040", 1.6, 12, 0.9, 1))
    inner.append(byline(514, "VOLTAIRE · 1694–1778", "#2E3A2A", size=18, ls=4, max_w=300))
    out.append(G + "".join(inner) + "</g>")
    # a trowel lying across the corner of the packet
    tw = rot([(452, 520), (520, 452), (536, 466), (468, 534)], 494, 493, 0)
    out.append(G + "</g>")
    out.append(painted(D, [(470, 548), (512, 500), (560, 470), (528, 524)], ("#D8DEE4", "#9AA4AE", "#4E5660"), 13, sk=0.2, n=8, inkw=1.4, hi=0.5))
    out.append(taper([(560, 470), (590, 440)], 12, 10, "#8A5A30"))
    return finish_w(D, out, 14)


# ================================================================ 13. hitch your wagon to a star — a farm wagon at dusk
def wheel(D, cx, cy, r, seed, rim=("#8A8E96", "#4A4E58", "#1E2028"), wood=WOOD, spokes=12):
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{wood[2]}" stroke-width="{r * 0.16:.1f}"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{wood[1]}" stroke-width="{r * 0.1:.1f}"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{r * 1.06:.1f}" fill="none" stroke="{rim[2]}" stroke-width="{r * 0.07:.1f}"/>']
    for k in range(spokes):
        a = math.radians(k * 360 / spokes + seed * 7)
        out.append(taper([(cx + math.cos(a) * r * 0.16, cy + math.sin(a) * r * 0.16), (cx + math.cos(a) * r * 0.95, cy + math.sin(a) * r * 0.95)],
                         r * 0.09, r * 0.06, wood[1]))
    out.append(painted(D, blob_pts(cx, cy, r * 0.2, r * 0.2, seed, 0.02, 12), wood, seed, sk=0.2, n=4, inkw=1.2, hi=0.5))
    out.append(f'<path d="{smooth_open(ell_pts(cx, cy, r * 1.0, r * 1.0, 200, 300, 10))}" fill="none" stroke="#FFC890" stroke-width="{r * 0.04:.1f}" opacity="0.7"/>')
    return "".join(out)


@design("hitch-your-wagon-to-a-star")
def hitch_wagon():
    D = Doc2("ww-hw")
    out = [sky(D, [(0, "#1E2050"), (0.3, "#3E3A78"), (0.52, "#8A5A8A"), (0.66, "#E88A6A"), (0.74, "#F8C07A")], 3, 470,
               ["#4A4A8A", "#A86A9A", "#F2A07A"], 70)]
    out.append(stars_field(4, (0, 0, 600, 220), 90))
    out.append(stars_field(5, (0, 0, 600, 140), 30, r=(1.2, 2.2)))
    # the evening star
    SX, SY = 470, 112
    out.append(soft_glow(D, SX, SY, 120, "#FFF2C8", 0.6))
    out.append(soft_glow(D, SX, SY, 40, "#FFFFFF", 0.9))
    out.append(sparkle(SX, SY, 34, "#FFFBEA", 1.0))
    out.append(sparkle(SX, SY, 18, "#FFFFFF", 1.0))
    # rolling hills, a farmhouse with a lit window, a fence
    l1 = ridge([(-20, 380), (110, 352), (260, 372), (400, 348), (620, 366)], 3, 8)
    out.append(hill(D, l1, 600, ("#6A5A7A", "#4A3E5E", "#2A223A"), 4, inkw=0, n=40, lit="#F2A07A"))
    hx = 470
    out.append(f'<path d="{pd([(hx - 26, 362), (hx + 26, 362), (hx + 26, 340), (hx - 26, 340)])}" fill="#2A2238"/>')
    out.append(f'<path d="{pd([(hx - 32, 342), (hx, 322), (hx + 32, 342)])}" fill="#22182E"/>')
    out.append(f'<rect x="{hx - 12}" y="346" width="8" height="8" fill="#FFD27A"/>')
    out.append(soft_glow(D, hx - 8, 350, 24, "#FFC860", 0.6))
    l2 = ridge([(-20, 432), (160, 418), (330, 430), (500, 412), (620, 422)], 7, 6)
    out.append(hill(D, l2, 620, ("#5A4A3A", "#3A2E28", "#1E1814"), 8, inkw=0, n=60, lit="#F8B07A",
                    cols=["#6A5A40", "#2A2018", "#4A3A2E"]))
    for k in range(7):
        x = 420 + k * 32
        y = 416 - k * 1.2
        out.append(taper([(x, y + 26), (x + 1, y - 4)], 4, 3, "#2A1E16"))
    out.append(pline([(416, 402), (620, 394)], "#3A2A20", 2, 9, 0.9, 1) + pline([(416, 412), (620, 404)], "#3A2A20", 2, 10, 0.9, 1))
    # the wagon (side view, facing right), its tongue lifted toward the star
    wx, wy = 230, 432
    out.append(cast(D, wx + 10, wy + 46, 150, 10, "#0A0608", 0.5, 11))
    out.append(wheel(D, wx - 74, wy + 10, 38, 12))
    bed = [(wx - 130, wy - 52), (wx + 96, wy - 52), (wx + 90, wy), (wx - 124, wy)]
    out.append(f'<path d="{pd(bed)}" fill="#9A3E28"/>')
    out.append(f'<path d="{pd(bed)}" fill="{D.lin([(0, "#E8905A", 0.6), (0.4, "#9A3E28", 0), (1, "#3A120A", 0.6)])}"/>')
    out.append(strokes(D.nid(), pd(bed), bbox(bed), ["#C8784A", "#6A2414", "#B85A38"], 13, n=50, angle=0, length=(20, 60), width=(1, 3), opacity=(0.2, 0.45)))
    out.append(ink(pd(bed), INK, 1.6, 13, 2, 0.75))
    for j in range(1, 4):
        out.append(pline([(wx - 128, wy - 52 + j * 13), (wx + 94, wy - 52 + j * 13)], "#4A1A10", 1.4, j, 0.6, 1))
    for x in (wx - 100, wx - 20, wx + 60):
        out.append(f'<rect x="{x}" y="{wy - 54}" width="6" height="56" fill="#3A1A10" opacity="0.75"/>')
    out.append(pline([(wx - 130, wy - 52), (wx + 96, wy - 52)], "#FFC890", 2, 14, 0.6, 1))
    # hay heaped in the bed
    hay = [(wx - 126, wy - 52), (wx - 100, wy - 72), (wx - 40, wy - 82), (wx + 20, wy - 78), (wx + 70, wy - 66), (wx + 92, wy - 52)]
    out.append(painted(D, hay, ("#FCE2A0", "#E2B05A", "#9A6A24"), 15, sdir=(0.3, 1), sk=0.15, angle=-20, n=40, slen=(8, 20), sw=(0.8, 1.6), inkw=1.2, hi=0.45))
    out.append(grass(16, (wx - 120, wy - 84, wx + 86, wy - 56), ["#FCE2A0", "#E2B05A", "#C89040"], n=40, h=(6, 14), w=1))
    out.append(wheel(D, wx + 62, wy + 18, 30, 17))
    out.append(wheel(D, wx - 74, wy + 10, 38, 18))
    # tongue rising up and the golden rope looping to the star
    tongue = [(wx + 88, wy - 6), (wx + 130, wy - 40), (wx + 168, wy - 84)]
    out.append(taper(tongue, 9, 6, "#5A3420"))
    out.append(taper([(x, y - 2) for x, y in tongue], 2.4, 1.6, "#E8A070", 0.6))
    rope = catmull([(wx + 168, wy - 84), (wx + 200, wy - 160), (wx + 260, wy - 210), (SX - 30, SY + 70), (SX - 6, SY + 10)], 10)
    out.append(taper(rope, 3.2, 2.2, "#E8B84A", 0.95))
    out.append(pline(rope, "#FFF2B8", 1, 19, 0.7, 1))
    for k in range(5):
        i = int(len(rope) * (0.2 + k * 0.15))
        out.append(sparkle(rope[i][0] + 6, rope[i][1], 5, "#FFF2C8", 0.8))
    # lantern hanging from the bed, fireflies
    lx, ly = wx - 130, wy - 30
    out.append(pline([(lx, wy - 50), (lx - 6, ly)], "#2A1A10", 1.4, 20, 1, 1))
    out.append(soft_glow(D, lx - 6, ly + 12, 44, "#FFC860", 0.6))
    out.append(painted(D, rect_pts(lx - 14, ly, lx + 2, ly + 22, 6, 21, 0.3), ("#FFF2B0", "#FFD060", "#B8781A"), 22, sk=0.15, n=4, inkw=1.3, hi=0.5))
    rnd = random.Random(23)
    for _ in range(18):
        x, y = rnd.uniform(40, 580), rnd.uniform(440, 520)
        out.append(soft_glow(D, x, y, 7, "#FFF29A", 0.7) + f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" fill="#FFFBD0"/>')
    out.append(grass(24, (-10, 540, 620, 610), ["#2A2018", "#4A3A2A", "#1A140E"], n=200, h=(10, 30)))
    # lettering, cream on the dark field
    out.append(lines(D, 300, 498, 0, ["Hitch your wagon to a star."], SERIF_IT, 44, "#FFF4DC", max_w=470, shadow="#120A10"))
    out.append(byline(536, "RALPH WALDO EMERSON · 1803–1882", "#F2C88A", size=17, ls=3, max_w=420))
    return finish_w(D, out, 25, "#0A0610", 0.5)


# ================================================================ 14. i cannot live without books — a wall of shelves and a placard
BOOK_COLS = [("#D0706A", "#8E2A2A", "#4E1014"), ("#7FAE86", "#2E6A48", "#163A26"), ("#6A82B8", "#24386A", "#0E1A3A"),
             ("#F2CF6E", "#D2A033", "#8A6418"), ("#A8789A", "#5E3050", "#2E1426"), ("#C8A07A", "#8A6040", "#4A3020"),
             ("#E8DCC0", "#C8B48A", "#7A6440"), ("#5E9A9A", "#2A6262", "#123434")]


def book_spine(D, x, base, w, h, pal, seed, lean=0, bands=True, label=None):
    """A standing book seen spine-on: cloth/leather colour, raised bands, gilt rules, head cap highlight."""
    pts = [(x, base), (x + w, base), (x + w, base - h), (x, base - h)]
    if lean:
        pts = rot(pts, x + (w if lean > 0 else 0), base, lean)
    d = pd(pts)
    out = [f'<path d="{d}" fill="{pal[1]}"/>']
    out.append(f'<path d="{d}" fill="{cyl(D, x, x + w, 0, 0, pal, -1, 0.8)}"/>' if not lean else "")
    out.append(strokes(D.nid(), d, bbox(pts), [pal[0], pal[2]], seed, n=max(4, int(h / 12)), angle=-90 + lean, length=(h * 0.15, h * 0.4), width=(0.8, 2), opacity=(0.15, 0.35)))
    if bands:
        rnd = random.Random(seed)
        ys = [0.12, 0.24, 0.76, 0.88] if rnd.random() < 0.5 else [0.15, 0.85]
        for t in ys:
            a, b = rot([(x + 1, base - h * t), (x + w - 1, base - h * t)], x + (w if lean > 0 else 0), base, lean) if lean else [(x + 1, base - h * t), (x + w - 1, base - h * t)]
            out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#E8C060" stroke-width="1.6" opacity="0.85"/>')
        if rnd.random() < 0.6 and not lean:
            out.append(f'<rect x="{x + w * 0.2:.1f}" y="{base - h * 0.62:.1f}" width="{w * 0.6:.1f}" height="{h * 0.14:.1f}" fill="{pal[2]}" opacity="0.8"/>')
            out.append(f'<rect x="{x + w * 0.2:.1f}" y="{base - h * 0.62:.1f}" width="{w * 0.6:.1f}" height="{h * 0.14:.1f}" fill="none" stroke="#E8C060" stroke-width="1"/>')
    out.append(ink(d, "#1A0E08", 1.1, seed, 1, 0.55))
    return "".join(out)


def shelf_row(D, y, x0, x1, seed, h=(80, 120), skip=()):
    """Fill a shelf from x0 to x1 with standing books (some leaning), returns svg."""
    rnd = random.Random(seed)
    out = []
    x = x0
    while x < x1:
        if any(a <= x <= b for a, b in skip):
            x += 6
            continue
        w = rnd.uniform(16, 30)
        hh = rnd.uniform(*h)
        pal = rnd.choice(BOOK_COLS)
        out.append(book_spine(D, x, y, w, hh, pal, rnd.randint(1, 9999)))
        x += w + rnd.uniform(0, 1.5)
    return "".join(out)


def shelf_board(D, y, seed, x0=-10, x1=610):
    out = [f'<path d="{pd([(x0, y), (x1, y), (x1, y + 16), (x0, y + 16)])}" fill="#6A4026"/>']
    out.append(strokes(D.nid(), pd([(x0, y), (x1, y), (x1, y + 16), (x0, y + 16)]), (x0 - 40, y, x1, y + 16), ["#8A5A36", "#4A2A16", "#A8744A"], seed, n=40, angle=0, length=(40, 120), width=(1, 2.4), opacity=(0.25, 0.5)))
    out.append(f'<path d="M {x0} {y + 1} L {x1} {y + 1}" stroke="#C8925E" stroke-width="2" opacity="0.7"/>')
    out.append(f'<path d="{pd([(x0, y + 16), (x1, y + 16), (x1, y + 26), (x0, y + 26)])}" fill="#1A0E06" opacity="0.5"/>')
    return "".join(out)


@design("i-cannot-live-without-books")
def without_books():
    D = Doc2("ww-bk")
    out = [f'<rect width="600" height="600" fill="#2A160C"/>']
    out.append(soft_glow(D, 300, 300, 360, "#E8A060", 0.25))
    # upper shelf
    out.append(shelf_row(D, 176, -14, 614, 3, h=(92, 128), skip=((380, 470),)))
    # a little globe and a stack lying flat in the gap
    gx, gy = 424, 128
    out.append(painted(D, blob_pts(gx, gy, 30, 30, 4, 0.01, 24), ("#E8DCB0", "#C8B07A", "#7A6440"), 5, sdir=(0.7, 0.6), sk=0.2, n=16, inkw=1.3, hi=0.5))
    for k, pts in enumerate(([(gx - 20, gy - 10), (gx - 4, gy - 20), (gx + 6, gy - 6), (gx - 8, gy + 8)], [(gx + 4, gy + 4), (gx + 22, gy - 2), (gx + 20, gy + 18), (gx + 6, gy + 20)])):
        out.append(f'<path d="{smooth_closed(pts)}" fill="#8AA06A" opacity="0.8"/>')
    out.append(f'<path d="{smooth_open(ell_pts(gx, gy, 36, 36, 120, 400, 20))}" fill="none" stroke="#C89A3A" stroke-width="3"/>')
    out.append(painted(D, [(gx - 16, 176), (gx + 16, 176), (gx + 8, 162), (gx - 8, 162)], BRASS, 6, sk=0.2, n=4, inkw=1, hi=0.5))
    out.append(taper([(gx, 162), (gx, 160 - 6)], 3, 3, "#C89A3A"))
    out.append(shelf_board(D, 176, 7))
    # lower shelf
    out.append(shelf_row(D, 538, -14, 614, 8, h=(96, 130), skip=((90, 210),)))
    for k in range(4):
        pal = BOOK_COLS[(k * 3) % len(BOOK_COLS)]
        y0 = 538 - (k + 1) * 18
        bp = rect_pts(96 + k * 3, y0, 204 - k * 2, y0 + 18, 12, 10 + k, 0.4)
        out.append(painted(D, bp, pal, 11 + k, sdir=(0.2, 1), sk=0.12, angle=0, n=8, inkw=1.2, inkc="#1A0E08", hi=0.35))
        out.append(f'<path d="M {104 + k * 3} {y0 + 4} L {104 + k * 3} {y0 + 14}" stroke="#E8C060" stroke-width="1.4"/>')
    # spectacles resting on the stack
    sx_, sy_ = 150, 538 - 72 - 8
    for dx in (-16, 16):
        out.append(f'<ellipse cx="{sx_ + dx}" cy="{sy_}" rx="13" ry="7" fill="#DDEEF4" opacity="0.35" stroke="#B8902E" stroke-width="2"/>')
    out.append(f'<path d="M {sx_ - 3} {sy_ - 1} q 3 -4 6 0" stroke="#B8902E" stroke-width="2" fill="none"/>')
    out.append(pline([(sx_ + 29, sy_ - 2), (sx_ + 50, sy_ + 4)], "#B8902E", 1.6, 12, 1, 1))
    out.append(shelf_board(D, 538, 13))
    # the placard in the middle shelf space
    pcx, py0, py1 = 300, 214, 400
    out.append(f'<path d="{pd([(48, py0 + 8), (560, py0 + 8), (560, py1 + 10), (48, py1 + 10)])}" fill="#000" opacity="0.4"/>')
    frame = rect_pts(40, py0, 560, py1, 20, 14, 0.3)
    out.append(painted(D, frame, ("#C8925E", "#8E5A30", "#4E2E14"), 15, sdir=(0.4, 1), sk=0.2, angle=0, n=40, inkw=1.6, hi=0.4))
    card = rect_pts(56, py0 + 14, 544, py1 - 14, 20, 16, 0.4)
    out.append(painted(D, card, ("#FFFAEA", "#F2E6C8", "#C8B08A"), 17, sdir=(0.3, 1), sk=0.05, angle=-5, n=60, inkw=1.2, hi=0.3))
    out.append(rule_frame(D, 68, py0 + 26, 532, py1 - 26, "#8E2A2A", 1.6, 5, 0.9, seed=18))
    for x in (66, 534):
        for y in (py0 + 24, py1 - 24):
            out.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#C8A048"/><circle cx="{x - 1}" cy="{y - 1}" r="1.6" fill="#FFF0B8"/>')
    out.append(tx(pcx, 290, "I cannot live", DMS, 62, "#2A1810", max_w=440))
    out.append(tx(pcx, 356, "without books.", SERIF_IT, 58, "#8E2A2A", max_w=440))
    out.append(flourish(pcx, 378, 120, "#8E2A2A", 1.6))
    # brass label on the bottom shelf edge
    lbl = rect_pts(170, 543, 430, 567, 10, 19, 0.2)
    out.append(painted(D, lbl, BRASS, 20, sdir=(0.3, 1), sk=0.25, angle=0, n=10, inkw=1.2, hi=0.5))
    out.append(tx(300, 560, "THOMAS JEFFERSON · 1743–1826", CINZEL, 16, "#3A2408", ls=2, max_w=244))
    return finish_w(D, out, 21, "#000000", 0.5)


# ================================================================ 15. que sais-je? — a balance in Montaigne's tower library
@design("que-sais-je")
def que_sais_je():
    D = Doc2("ww-qs")
    # the round tower room: curved plaster wall, painted ceiling beams, a deep window
    out = [f'<rect width="600" height="600" fill="#E8D6B4"/>']
    out.append(f'<rect width="600" height="600" fill="{D.lin([(0, "#3A2414", 0.5), (0.25, "#3A2414", 0), (0.75, "#3A2414", 0), (1, "#3A2414", 0.55)], 0, 0, 1, 0)}"/>')
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 610, 610), ["#F2E2C4", "#C8B08A", "#FFF2DA"], 2,
                       n=180, angle=-80, length=(20, 60), width=(4, 10), opacity=(0.15, 0.3)))
    # the great beam with its painted sentences (Montaigne had maxims lettered on his library beams)
    bm = [(-10, 14), (610, 14), (610, 64), (-10, 64)]
    out.append(painted(D, bm, ("#9A6A40", "#6A4024", "#2E1A0C"), 3, sdir=(0.2, 1), sk=0.2, angle=0, n=40, inkw=1.4, hi=0.25))
    for y_ in (24, 54):
        out.append(pline([(-10, y_), (300, y_ + 1), (610, y_)], "#C8925E", 1.6, y_, 0.55, 1))
    for x_ in (150, 450):
        out.append(f'<path d="{blob(x_, 39, 9, 6, x_, 0.2, 10)}" fill="#3A2010" opacity="0.6"/>')
    out.append(f'<path d="M -10 64 L 610 64 L 610 72 L -10 72 Z" fill="#1A0C04" opacity="0.35"/>')
    # curved shelves at the sides with books
    for sg in (-1, 1):
        x0 = 0 if sg < 0 else 452
        for y in (230, 360):
            out.append(shelf_row(D, y, x0 - 10, x0 + 158, 20 + y + sg, h=(70, 96)))
            out.append(shelf_board(D, y, 30 + y + sg, x0 - 10, x0 + 158))
    # window behind, light falling in
    wx = 300
    win = f"M {wx - 60} 300 L {wx - 60} 150 Q {wx} 96 {wx + 60} 150 L {wx + 60} 300 Z"
    out.append(f'<path d="{win}" fill="{D.lin([(0, "#BCD8EC"), (1, "#F6EAD0")])}"/>')
    out.append(puff_cloud(D, wx - 10, 190, 70, 7, pal=("#FFFFFF", "#F6F2EC", "#C8C8D4"), rows=1))
    out.append(hill(D, ridge([(wx - 70, 270), (wx, 256), (wx + 70, 266)], 8, 4), 310, ("#B8C890", "#8AA060", "#5A7040"), 9, inkw=0, n=10))
    for x in (wx - 20, wx + 20):
        out.append(f'<path d="M {x} 140 L {x} 300" stroke="#4A2C16" stroke-width="3"/>')
    out.append(f'<path d="M {wx - 60} 220 L {wx + 60} 220" stroke="#4A2C16" stroke-width="3"/>')
    out.append(f'<path d="{win}" fill="none" stroke="#6A4024" stroke-width="12" opacity="0.6"/>')
    out.append(ink(win, INK, 1.8, 10, 1, 0.6))
    out.append(f'<path d="{pd([(wx - 60, 300), (wx + 60, 300), (wx + 170, 470), (wx - 110, 470)])}" fill="#FFF2C8" opacity="0.22"/>')
    # the table
    tb = [(-20, 420), (620, 420), (620, 610), (-20, 610)]
    out.append(painted(D, tb, ("#B07A4A", "#7A4A28", "#3A2010"), 11, sdir=(0, 1), sk=0.04, angle=-2, n=80, slen=(40, 120), sw=(1, 3), inkw=0, hi=0.2))
    out.append(f'<path d="M -10 420 L 610 420" stroke="#E0A870" stroke-width="2.4" opacity="0.6"/>')
    out.append(f'<path d="{pd([(120, 420), (480, 420), (520, 470), (80, 470)])}" fill="#FFF2C8" opacity="0.12"/>')
    # the balance: pillar, beam perfectly level, two pans on chains
    bx, btop = 300, 236
    out.append(cast(D, bx + 10, 424, 90, 9, strength=0.5, seed=12))
    base = [(bx - 46, 424), (bx + 46, 424), (bx + 32, 404), (bx - 32, 404)]
    out.append(painted(D, base, BRASS, 13, sdir=(0.8, 0.5), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.5))
    post = rect_pts(bx - 6, btop + 6, bx + 6, 406, 10, 14, 0.2)
    out.append(painted(D, post, BRASS, 15, sdir=(1, 0.1), sk=0.3, angle=-90, n=8, inkw=1.2, hi=0.55))
    for y in (300, 360):
        out.append(painted(D, ell_pts(bx, y, 11, 4, 0, 360, 12)[:-1], BRASS, 16 + y, sk=0.2, n=3, inkw=1, hi=0.5))
    BL = 150
    beam = rect_pts(bx - BL, btop - 4, bx + BL, btop + 4, 14, 17, 0.2)
    out.append(painted(D, beam, BRASS, 18, sdir=(0.3, 1), sk=0.3, angle=0, n=10, inkw=1.3, hi=0.55))
    out.append(painted(D, [(bx - 12, btop + 4), (bx, btop - 26), (bx + 12, btop + 4)], BRASS, 19, sk=0.2, n=4, inkw=1.2, hi=0.5))
    out.append(f'<circle cx="{bx}" cy="{btop}" r="5" fill="#7A5418"/>')
    PY = 360
    for sg in (-1, 1):
        ex = bx + sg * (BL - 6)
        out.append(f'<circle cx="{ex}" cy="{btop}" r="4" fill="#7A5418"/>')
        for dx in (-34, 0, 34):
            out.append(pline([(ex, btop + 2), (ex + dx, PY - 4)], "#8A6420", 1.4, int(ex + dx), 0.95, 1))
        pan = [(ex - 46, PY - 4), (ex + 46, PY - 4), (ex + 34, PY + 12), (ex - 34, PY + 12)]
        out.append(painted(D, pan, BRASS, 20 + sg, sdir=(0.5, 1), sk=0.25, angle=0, n=8, inkw=1.3, hi=0.5))
        out.append(f'<path d="{smooth_closed(ell_pts(ex, PY - 4, 46, 7, 0, 360, 20))}" fill="#E8C06A"/>')
        out.append(ink(smooth_closed(ell_pts(ex, PY - 4, 46, 7, 0, 360, 20)), "#7A5418", 1.2, 22 + sg, 1, 0.7))
    # on the left pan: a thick book; on the right: a single white feather. Level.
    lx = bx - BL + 6
    out.append(book3(D, lx - 34, PY - 30, 68, 18, 10, 23, cover=("#D0706A", "#8E2A2A", "#4E1014")))
    rx_ = bx + BL - 6
    fpts = [(rx_ - 40, PY - 6), (rx_ - 10, PY - 18), (rx_ + 30, PY - 22), (rx_ + 42, PY - 16), (rx_ + 10, PY - 8)]
    out.append(painted(D, fpts, ("#FFFFFF", "#F2EEE6", "#B8B0A0"), 24, sk=0.15, angle=-20, n=20, slen=(4, 10), sw=(0.5, 1), inkw=1.0, hi=0.5))
    out.append(pline([(rx_ - 44, PY - 4), (rx_ - 10, PY - 13), (rx_ + 40, PY - 19)], "#9A9080", 1.2, 25, 0.9, 1))
    # lettering
    out.append(ruled(300, 446, "WHAT DO I KNOW?", "#F2D8A8", font=CINZEL, size=19, ls=6, line_w=36, gap=14))
    out.append(letters(D, 300, 508, "Que sais-je?", SERIF_IT, 66, "#FBEFD8", ["#FFFFFF", "#F2DCB0"], 30, max_w=430,
                       shadow="#1A0C04", angle=-35, inkc=None, wob=0.5))
    out.append(byline(540, "MICHEL DE MONTAIGNE · 1533–1592", "#E8C890", size=16, ls=3, max_w=400))
    return finish_w(D, out, 32)


# ================================================================ 16. cogito, ergo sum — a Dutch room: window light, honeycomb wax, a notebook
def delft_tile(D, x, y, s, seed, motif=0):
    rnd = random.Random(seed)
    out = [f'<path d="{hg.org_rect(x + 1, y + 1, s - 2, s - 2, seed, 0.3, 6, 1.5)}" fill="#F6F2EA"/>']
    c = "#2A4A9A"
    for (cx, cy) in ((x + 3, y + 3), (x + s - 3, y + 3), (x + 3, y + s - 3), (x + s - 3, y + s - 3)):
        out.append(f'<path d="{pd([(cx - 3, cy), (cx, cy - 3), (cx + 3, cy), (cx, cy + 3)])}" fill="{c}" opacity="0.8"/>')
    m = motif % 3
    cx, cy = x + s / 2, y + s / 2
    if m == 0:      # a little boat
        out.append(f'<path d="{pd([(cx - 8, cy + 3), (cx + 8, cy + 3), (cx + 5, cy + 7), (cx - 5, cy + 7)])}" fill="{c}"/>')
        out.append(f'<path d="{pd([(cx, cy + 2), (cx, cy - 9), (cx + 7, cy + 1)])}" fill="{c}" opacity="0.8"/>')
    elif m == 1:    # a windmill
        out.append(f'<path d="{pd([(cx - 3, cy + 8), (cx + 3, cy + 8), (cx + 2, cy - 2), (cx - 2, cy - 2)])}" fill="{c}"/>')
        for a in (45, 135, 225, 315):
            out.append(pline([(cx, cy - 2), (cx + math.cos(math.radians(a)) * 8, cy - 2 + math.sin(math.radians(a)) * 8)], c, 1.6, a, 1, 1))
    else:           # a flower
        for a in range(0, 360, 72):
            out.append(f'<circle cx="{cx + math.cos(math.radians(a)) * 4:.1f}" cy="{cy + math.sin(math.radians(a)) * 4:.1f}" r="2.6" fill="{c}"/>')
    out.append(f'<path d="{hg.org_rect(x + 1, y + 1, s - 2, s - 2, seed, 0.3, 6, 1.5)}" fill="none" stroke="#B8C0D0" stroke-width="0.8"/>')
    return "".join(out)


def honeycomb(D, cx, cy, w, h, seed):
    """A slab of honeycomb wax: golden hexagon cells, some capped, glistening honey."""
    rnd = random.Random(seed)
    outline = blob_pts(cx, cy, w / 2, h / 2, seed, 0.08, 16)
    d = smooth_closed(outline)
    out = [cast(D, cx + 8, cy + h * 0.45, w * 0.55, h * 0.18, strength=0.45, seed=seed)]
    out.append(f'<path d="{d}" fill="#E8A830"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    r = 7.5
    for j in range(-8, 9):
        for i in range(-12, 13):
            x = cx + i * r * 1.73 + (j % 2) * r * 0.866
            y = cy + j * r * 1.5 * 0.62
            hexp = [(x + math.cos(math.radians(30 + 60 * k)) * r * 0.86, y + math.sin(math.radians(30 + 60 * k)) * r * 0.86 * 0.62) for k in range(6)]
            capped = rnd.random() < 0.35
            inner.append(f'<path d="{pd(hexp)}" fill="{"#F8D88A" if capped else rnd.choice(["#D88A1E", "#E8A030", "#C87A14"])}" stroke="#FFE8A8" stroke-width="1.2"/>')
            if not capped and rnd.random() < 0.4:
                inner.append(f'<circle cx="{x - 1.5:.1f}" cy="{y - 1:.1f}" r="1.3" fill="#FFF6D0" opacity="0.8"/>')
    inner.append(f'<path d="{d}" fill="{D.lin([(0, "#FFF4C0", 0.35), (0.5, "#FFF4C0", 0), (1, "#6A3A08", 0.4)], 0, 0, 1, 1)}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, "#7A4A0E", 1.4, seed, 1, 0.7))
    # a drip of honey
    out.append(f'<path d="{blob(cx + w * 0.3, cy + h * 0.5, 7, 4, seed + 3, 0.2, 10)}" fill="#E89A20" opacity="0.9"/>')
    return "".join(out)


def bee_p(D, x, y, s, seed, ang=-10):
    def L(pts):
        return T(pts, x, y, s, False, ang)
    out = []
    for k, wpts in enumerate(([(0, -4), (-8, -18), (4, -20), (6, -6)], [(2, -4), (12, -16), (18, -8), (8, -2)])):
        out.append(f'<path d="{smooth_closed(L(wpts))}" fill="#E8F4FA" opacity="0.75" stroke="#6A7A8A" stroke-width="0.8"/>')
    body = L([(-12, 0), (-4, -6), (8, -5), (14, 0), (8, 5), (-4, 6)])
    out.append(f'<path d="{smooth_closed(body)}" fill="#F2B22A"/>')
    for dx in (-4, 4):
        out.append(f'<path d="{pd(L([(dx, -6), (dx + 3, -6), (dx + 3, 6), (dx, 6)]))}" fill="#2A1A10"/>')
    out.append(f'<circle cx="{L([(16, 0)])[0][0]:.1f}" cy="{L([(16, 0)])[0][1]:.1f}" r="{4 * s:.1f}" fill="#2A1A10"/>')
    out.append(ink(smooth_closed(body), "#2A1A10", 1, seed, 1, 0.8))
    return "".join(out)


def turkish_carpet(D, d, seed):
    """Oriental table carpet as in Dutch interiors: madder red ground, indigo and ochre medallions, a border."""
    c = 56
    m = (f'<rect width="{c}" height="{c}" fill="#9A2A22"/>'
         f'<path d="M {c / 2} 6 L {c - 8} {c / 2} L {c / 2} {c - 6} L 8 {c / 2} Z" fill="#22305A"/>'
         f'<path d="M {c / 2} 16 L {c - 18} {c / 2} L {c / 2} {c - 16} L 18 {c / 2} Z" fill="#D8A040"/>'
         f'<circle cx="{c / 2}" cy="{c / 2}" r="5" fill="#9A2A22"/>'
         f'<circle cx="0" cy="0" r="7" fill="#E8D0A0"/><circle cx="{c}" cy="0" r="7" fill="#E8D0A0"/><circle cx="0" cy="{c}" r="7" fill="#E8D0A0"/><circle cx="{c}" cy="{c}" r="7" fill="#E8D0A0"/>')
    pat = D.pattern(c, c, m, transform="skewX(-8)")
    return f'<path d="{d}" fill="{pat}"/>'


@design("cogito-ergo-sum")
def cogito():
    D = Doc2("ww-ce")
    # lime-washed wall, lit from the window on the left
    out = [f'<rect width="600" height="600" fill="#E2DAC8"/>']
    out.append(f'<rect width="600" height="600" fill="{D.lin([(0, "#FFF6E2", 0.8), (0.45, "#E2DAC8", 0), (1, "#7A6E5E", 0.5)], 0, 0, 1, 0.3)}"/>')
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 610, 400), ["#F2EAD8", "#C8BEA8", "#FFFFFF"], 2,
                       n=160, angle=-75, length=(30, 80), width=(4, 10), opacity=(0.12, 0.28)))
    # the leaded window
    wx0, wx1, wy0, wy1 = 34, 172, 70, 360
    out.append(f'<path d="{pd([(wx0 - 10, wy0 - 10), (wx1 + 10, wy0 - 10), (wx1 + 10, wy1 + 8), (wx0 - 10, wy1 + 8)])}" fill="#6A5038"/>')
    out.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="{D.lin([(0, "#E8F2F6"), (1, "#C8DCE4")])}"/>')
    out.append(soft_glow(D, (wx0 + wx1) / 2, 180, 140, "#FFFFFF", 0.7))
    cid = D.clip(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}"/>')
    lead = []
    for k in range(-14, 16):
        lead.append(f'<path d="M {wx0 + k * 20} {wy0} l 160 280 M {wx0 + k * 20} {wy0} l -160 280" stroke="#5A5048" stroke-width="1.4" opacity="0.7"/>')
    lead.append(f'<path d="M {wx0} {(wy0 + wy1) / 2} L {wx1} {(wy0 + wy1) / 2}" stroke="#4A3A2A" stroke-width="5"/>')
    lead.append(f'<path d="M {(wx0 + wx1) / 2} {wy0} L {(wx0 + wx1) / 2} {wy1}" stroke="#4A3A2A" stroke-width="5"/>')
    out.append(f'<g {cid}>{"".join(lead)}</g>')
    # the light falling across wall and table
    out.append(f'<path d="{pd([(wx1, wy0), (wx1, wy1), (430, 600), (600, 600), (600, 420)])}" fill="#FFF6D8" opacity="0.18"/>')
    # Delft tile skirting
    for i in range(14):
        out.append(delft_tile(D, -6 + i * 44, 372, 44, 10 + i, i))
    out.append(f'<path d="M -10 372 L 610 372" stroke="#8A7A64" stroke-width="2"/>')
    # table with its carpet, falling in folds at the front
    top = [(-20, 430), (620, 418), (620, 470), (-20, 482)]
    cd = pd([(-20, 416), (620, 404), (620, 620), (-20, 620)])
    out.append(turkish_carpet(D, cd, 11))
    out.append(f'<path d="{cd}" fill="{D.lin([(0, "#FFF2C8", 0.25), (0.3, "#000", 0), (1, "#1A0806", 0.55)])}"/>')
    for k in range(8):
        x = 20 + k * 80
        out.append(taper([(x, 476), (x + 6, 540), (x + 2, 610)], 18, 24, "#1A0806", 0.28))
        out.append(taper([(x + 20, 476), (x + 26, 540), (x + 22, 610)], 6, 8, "#FFE8C8", 0.15))
    out.append(pline([(-10, 470), (300, 464), (610, 458)], "#E8C890", 1.6, 12, 0.5, 1))
    out.append(f'<path d="{pd([(-20, 404), (620, 392), (620, 420), (-20, 432)])}" fill="#000" opacity="0.0"/>')
    # objects: pewter plate with honeycomb, a brass candlestick, an open notebook with a curve, dividers, a bee
    out.append(cast(D, 168, 452, 96, 14, strength=0.45, seed=13))
    out.append(painted(D, ell_pts(160, 440, 90, 22, 0, 360, 28)[:-1], ("#E8ECF0", "#A8B0B8", "#5A6068"), 14, sdir=(0.7, 0.6), sk=0.15, n=12, inkw=1.4, hi=0.55))
    out.append(f'<path d="{smooth_closed(ell_pts(160, 440, 68, 15, 0, 360, 24))}" fill="#8A9298" opacity="0.4"/>')
    out.append(honeycomb(D, 160, 430, 116, 46, 15))
    out.append(bee_p(D, 236, 384, 1.2, 16, -20))
    out.append(pline([(214, 394), (196, 404), (184, 398)], "#5A5A5A", 1, 17, 0.5, 1))
    # notebook (open) with Cartesian axes and a parabola
    nb = [(276, 452), (436, 440), (462, 492), (290, 506)]
    out.append(f'<path d="{pd(shift(nb, 5, 7))}" fill="#000" opacity="0.35"/>')
    lp, rp = [(276, 452), (364, 446), (374, 500), (290, 506)], [(364, 446), (436, 440), (462, 492), (374, 500)]
    for k, pg in enumerate((lp, rp)):
        out.append(painted(D, pg, ("#FFFCF2", "#F2EAD4", "#C8B898"), 18 + k, sdir=(0.3, 1), sk=0.06, angle=-4, n=8, inkw=1.2, hi=0.3))
    ax0, ay0 = 296, 494
    out.append(pline([(ax0, ay0), (360, 490)], "#3A2A1A", 1.4, 20, 0.9, 1) + pline([(ax0 + 6, ay0 + 2), (296, 458)], "#3A2A1A", 1.4, 21, 0.9, 1))
    par = [(300 + t * 3.4, 492 - (t - 9) ** 2 * 0.38 + 0) for t in range(0, 19)]
    par = [(x, y - 0.0) for x, y in par]
    out.append(pline([(x, min(y, 492)) for x, y in par], "#8E2A2A", 1.4, 22, 0.9, 1))
    for j in range(5):
        out.append(f'<path d="M {380 + j * 2} {456 + j * 8} l {60 - j * 2} -4" stroke="#8A7A64" stroke-width="1" opacity="0.6"/>')
    # dividers lying across the page
    out.append(pline([(410, 498), (452, 448)], "#7A7A80", 2.2, 23, 1, 1) + pline([(422, 502), (452, 448)], "#7A7A80", 2.2, 24, 1, 1))
    out.append(f'<circle cx="452" cy="448" r="4" fill="#C8A040"/>')
    # brass candlestick, unlit, with a thin curl of smoke
    out.append(candle(D, 520, 444, 70, 25, w=16, flame=False, holder=BRASS))
    out.append(steam_wisps(520, 360, 60, 26, "#8A8A8A", 1, 10, 3, 0.4))
    # lettering on the wall
    out.append(lines(D, 380, 150, 72, ["Cogito,", "ergo sum."], SERIF_IT, 76, "#2A2A3A", max_w=380))
    out.append(ruled(380, 264, "I THINK, THEREFORE I AM", "#2A4A9A", font=CINZEL, size=18, ls=3, line_w=22, gap=10, max_w=330))
    out.append(byline(300, "RENÉ DESCARTES · 1596–1650", "#5A4A3A", size=16, ls=3, max_w=330, x=380))
    return finish_w(D, out, 27)


# ================================================================ 17. eureka! — the overflowing bath and the golden crown
@design("eureka")
def eureka():
    D = Doc2("ww-eu")
    # warm plastered bath-house wall with a painted key band
    out = [f'<rect width="600" height="600" fill="#E8B898"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 610, 610), ["#F2C8A8", "#D8987A", "#F8D8BC"], 2,
                       n=200, angle=-70, length=(30, 90), width=(5, 12), opacity=(0.15, 0.3)))
    out.append(soft_glow(D, 300, 330, 300, "#FFF2DC", 0.35))
    out.append(f'<rect x="-10" y="268" width="620" height="30" fill="#2A4A5A"/>')
    out.append(meander(-4, 610, 272, 22, "#E8D8B8", 2.6))
    out.append(f'<rect x="-10" y="298" width="620" height="44" fill="#C8806A" opacity="0.55"/>')
    # pebble-mosaic floor
    FY = 340
    fl = [(-20, FY), (620, FY), (620, 620), (-20, 620)]
    out.append(f'<path d="{pd(fl)}" fill="#F2EAD8"/>')
    rnd = random.Random(3)
    dots = []
    for j in range(36):
        y = FY + 3 + j * 7.2 + j * j * 0.05
        for i in range(72):
            x = -20 + i * 9 + (j % 2) * 4.5 + rnd.uniform(-1, 1)
            c = "#1E1A18" if j in (2, 3) else rnd.choice(["#F6F0E2", "#E8DCC4", "#EFE6D2", "#D8CCB4"])
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{2.2 + j * 0.06:.1f}" fill="{c}"/>')
    out.append("".join(dots))
    out.append(f'<path d="{pd(fl)}" fill="{D.lin([(0, "#3A2A1A", 0.3), (0.25, "#3A2A1A", 0), (1, "#3A2A1A", 0.12)])}"/>')
    # the marble tub, side-on: fluted front like a sarcophagus, lion-paw feet
    tx0, tx1, ty0, ty1 = 112, 470, 356, 482
    tcx = (tx0 + tx1) / 2
    out.append(cast(D, tcx + 10, ty1 + 10, 220, 16, strength=0.4, seed=4))
    for x in (tx0 + 26, tx1 - 26):
        out.append(painted(D, blob_pts(x, ty1 + 4, 22, 12, int(x), 0.1, 12), MARBLE, int(x) + 1, sk=0.2, n=4, inkw=1.2, hi=0.4))
        for k in range(3):
            out.append(pline([(x - 12 + k * 10, ty1 + 6), (x - 12 + k * 10, ty1 + 14)], "#8A8070", 1.2, k, 0.7, 1))
    front = [(tx0, ty0), (tx1, ty0), (tx1 + 6, ty0 + 40), (tx1 - 8, ty1), (tx0 + 8, ty1), (tx0 - 6, ty0 + 40)]
    out.append(painted(D, front, ("#FFFFFF", "#ECE6DA", "#9A9080"), 5, sdir=(0.6, 0.4), sk=0.12, angle=-90, n=40, inkw=1.8, hi=0.35))
    cid = D.clip(f'<path d="{smooth_closed(front)}"/>')
    fl_ = []
    for k in range(16):
        x = tx0 + 30 + k * 20
        if tcx - 46 < x < tcx + 46:
            continue
        sgn = 1 if x < tcx else -1
        fl_.append(f'<path d="M {x:.1f} {ty0 + 20} q {sgn * 14:.1f} {(ty1 - ty0) * 0.35:.1f} 0 {(ty1 - ty0) * 0.55:.1f} t 0 {(ty1 - ty0) * 0.3:.1f}" stroke="#A89E8C" stroke-width="3" fill="none" opacity="0.6"/>')
        fl_.append(f'<path d="M {x + 3:.1f} {ty0 + 20} q {sgn * 14:.1f} {(ty1 - ty0) * 0.35:.1f} 0 {(ty1 - ty0) * 0.55:.1f} t 0 {(ty1 - ty0) * 0.3:.1f}" stroke="#FFFFFF" stroke-width="1.6" fill="none" opacity="0.6"/>')
    out.append(f'<g {cid}>{"".join(fl_)}</g>')
    # a lion-head spout medallion in the middle of the front
    out.append(painted(D, blob_pts(tcx, ty0 + 62, 30, 30, 6, 0.02, 20), GOLD, 7, sk=0.2, n=10, inkw=1.4, hi=0.5))
    for k in range(14):
        a = math.radians(k * 360 / 14)
        out.append(f'<path d="{blob(tcx + math.cos(a) * 24, ty0 + 62 + math.sin(a) * 24, 7, 4, k, 0.2, 8, math.degrees(a))}" fill="#B8862A"/>')
    for k in range(8):
        a = math.radians(k * 45)
        out.append(f'<path d="{blob(tcx + math.cos(a) * 8, ty0 + 62 + math.sin(a) * 8, 7, 3.6, k + 40, 0.1, 8, k * 45)}" fill="#F6D27A"/>')
    out.append(f'<circle cx="{tcx}" cy="{ty0 + 62}" r="5" fill="#8A5A14"/>')
    # rim and the heaving water above it
    rim = rect_pts(tx0 - 10, ty0 - 12, tx1 + 10, ty0 + 4, 20, 8, 0.4)
    out.append(painted(D, rim, ("#FFFFFF", "#F2EEE6", "#A8A090"), 9, sdir=(0.2, 1), sk=0.25, angle=0, n=16, inkw=1.6, hi=0.5))
    water = [(tx0 - 4, ty0 - 12), (tx0 + 30, ty0 - 24), (tx0 + 80, ty0 - 18), (tx0 + 130, ty0 - 36), (tx0 + 170, ty0 - 22), (tx0 + 220, ty0 - 40), (tx0 + 270, ty0 - 24),
             (tx0 + 320, ty0 - 30), (tx1 + 4, ty0 - 12)]
    wd = smooth_open(water) + f" L {tx1 + 4} {ty0 - 10} L {tx0 - 4} {ty0 - 10} Z"
    out.append(f'<path d="{wd}" fill="#5ABCC8"/>')
    out.append(f'<path d="{wd}" fill="{D.lin([(0, "#BFF0F0", 0.8), (1, "#1E7A8C", 0.4)])}"/>')
    out.append(ink(smooth_open(water), "#2A7A8A", 1.4, 10, 1, 0.6))
    out.append(taper([(x, y + 3) for x, y in catmull(water, 4)], 3, 2, "#FFFFFF", 0.7))
    # sheets of water spilling over the rim and down the front
    for k, (x, w_) in enumerate(((tx0 + 40, 30), (tx0 + 130, 46), (tx0 + 236, 38), (tx1 - 46, 30))):
        sheet = [(x - w_ / 2, ty0 - 12), (x + w_ / 2, ty0 - 12), (x + w_ / 2 + 4, ty0 + 30), (x + w_ / 2 - 2, ty1 + 6), (x - w_ / 2 + 2, ty1 + 6), (x - w_ / 2 - 3, ty0 + 30)]
        out.append(f'<path d="{smooth_closed(sheet)}" fill="#8AD8E0" opacity="0.55"/>')
        for j in range(4):
            xx = x - w_ / 2 + 4 + j * (w_ - 8) / 3
            out.append(pline([(xx, ty0 - 8), (xx + 2, ty0 + 40), (xx, ty1)], "#FFFFFF", 1.4, k * 9 + j, 0.6, 1))
        for j in range(3):
            out.append(f'<path d="{blob(x + rnd.uniform(-w_ / 2, w_ / 2), ty1 + rnd.uniform(8, 20), 3, 4, k * 7 + j, 0.1, 8)}" fill="#BFF0F4"/>')
    # the spreading puddle
    pud = blob(tcx, ty1 + 34, 250, 24, 11, 0.12, 22)
    out.append(f'<path d="{pud}" fill="#8AD4DC" opacity="0.6"/>')
    out.append(wave_lines(12, (tcx - 200, ty1 + 20, tcx + 200, ty1 + 50), ["#FFFFFF"], n=14, L=(16, 40), w=1.4, amp=1.5))
    # flying droplets over the tub
    for k in range(36):
        x = rnd.uniform(tx0, tx1)
        y = ty0 - 30 - rnd.random() ** 1.5 * 80
        r = rnd.uniform(2, 5)
        out.append(f'<path d="{blob(x, y, r, r * 1.2, k, 0.1, 8)}" fill="#BFF0F4"/><circle cx="{x - r * 0.3:.1f}" cy="{y - r * 0.4:.1f}" r="{r * 0.35:.1f}" fill="#FFFFFF"/>')
    # the golden crown on a stool at right
    sx_, sy_ = 526, 404
    out.append(cast(D, sx_ + 6, sy_ + 72, 46, 7, strength=0.4, seed=19))
    out.append(painted(D, rect_pts(sx_ - 32, sy_, sx_ + 32, sy_ + 72, 10, 20, 0.4), MARBLE, 21, sdir=(1, 0.3), sk=0.2, angle=-90, n=10, inkw=1.3, hi=0.4))
    out.append(painted(D, ell_pts(sx_, sy_, 40, 10, 0, 360, 20)[:-1], MARBLE, 22, sk=0.2, n=6, inkw=1.3, hi=0.5))
    out.append(soft_glow(D, sx_, sy_ - 16, 60, "#FFE8A0", 0.6))
    for sg in (-1, 1):
        pts = [(sx_ + sg * 4, sy_ - 2), (sx_ + sg * 28, sy_ - 6), (sx_ + sg * 32, sy_ - 22), (sx_ + sg * 16, sy_ - 34)]
        out.append(laurel(D, pts, 12, GOLD, 23 + sg, side=sg, inkw=0.8, berries="#FFF0A0"))
    out.append(sparkle(sx_ + 22, sy_ - 30, 10, "#FFFFFF", 1))
    out.append(sparkle(sx_ - 24, sy_ - 14, 6, "#FFFFFF", 0.9))
    # his himation flung over a stool at left, sandals kicked off, wet footprints running out of the picture
    st = rect_pts(28, 396, 92, 468, 10, 30, 0.4)
    out.append(painted(D, st, WOOD, 31, sdir=(1, 0.3), sk=0.2, angle=-90, n=10, inkw=1.3, hi=0.4))
    him = [(14, 380), (70, 372), (104, 386), (100, 430), (86, 470), (60, 450), (36, 474), (20, 440)]
    out.append(painted(D, him, ("#FFFFFF", "#F2EADA", "#B0A48E"), 32, sdir=(0.6, 0.6), sk=0.2, angle=-80, n=24, inkw=1.3, hi=0.4))
    for pts in (((40, 390), (46, 430), (40, 462)), ((70, 388), (78, 432), (70, 458))):
        out.append(pline(list(pts), "#B0A48E", 1.8, 33, 0.7, 1))
    out.append(pline([(18, 392), (100, 390)], "#4A6A9A", 3, 34, 0.8, 1))
    for k, (x, y, a) in enumerate(((70, 520, -20), (106, 534, 25))):
        sd = rot(blob_pts(x, y, 22, 9, 70 + k, 0.08, 14), x, y, a)
        out.append(painted(D, sd, ("#C8925E", "#8E5A30", "#4E2E14"), 71 + k, sk=0.2, n=4, inkw=1.2, hi=0.4))
        out.append(pline(rot([(x - 7, y - 8), (x - 2, y + 8)], x, y, a), "#4E2E14", 2, k, 0.9, 1) + pline(rot([(x + 7, y - 8), (x + 4, y + 8)], x, y, a), "#4E2E14", 2, k + 2, 0.9, 1))
    for k in range(5):
        fx_, fy_ = 400 + k * 46, 568 - k * 7 + (k % 2) * 16
        side = 1 if k % 2 else -1
        out.append(f'<path d="{blob(fx_, fy_, 11, 5, 80 + k, 0.12, 12, -6)}" fill="#6AB4C0" opacity="0.7"/>')
        out.append(f'<path d="{blob(fx_ - 9, fy_ + 0.5, 5, 4, 90 + k, 0.1, 8)}" fill="#6AB4C0" opacity="0.7"/>')
        for t, (tx_, ty_, r_) in enumerate(((14, -4 * side, 2.6), (15.5, -1 * side, 2.1), (15.5, 1.8 * side, 1.9), (14.5, 4.2 * side, 1.7), (12.5, 6.2 * side, 1.5))):
            out.append(f'<circle cx="{fx_ + tx_:.1f}" cy="{fy_ + ty_:.1f}" r="{r_:.1f}" fill="#6AB4C0" opacity="0.7"/>')
    # lettering
    out.append(letters(D, 300, 154, "Eureka!", SERIF_IT, 128, "#C88A1E", ["#E8B040", "#A8680E", "#F6CE6A", "#D8961E"], 30, max_w=440,
                       shadow="#6A2A10", angle=-60, hi="#FFF0B0", inkc="#6A3A08", inkw=1.4))
    out.append(ruled(300, 200, "I HAVE FOUND IT!", "#3A1A0A", font=CINZEL, size=20, ls=6, line_w=40, gap=14))
    out.append(byline(236, "ARCHIMEDES · c. 287–212 BC", "#3A1A0A", size=17, ls=4, max_w=360))
    return finish_w(D, out, 31)


# ================================================================ 18. the shoulders of giants — a telescope on a stack of great books
@design("shoulders-of-giants")
def shoulders_of_giants():
    D = Doc2("ww-sg")
    # a celestial chart engraved in gold on deep blue paper
    out = [f'<rect width="600" height="600" fill="{D.rad([(0, "#2A3E7A"), (1, "#0E1636")], cx=0.6, cy=0.4, r=0.8)}"/>']
    out.append(blooms(3, ["#3A5294", "#14204A"], 8, (0, 0, 600, 600), (80, 160), (0.15, 0.3)))
    gc = "#D8B460"
    ccx, ccy = 470, 250
    for k, (rx, ry) in enumerate(((60, 40), (110, 74), (170, 116), (240, 164), (320, 220))):
        out.append(f'<ellipse cx="{ccx}" cy="{ccy}" rx="{rx}" ry="{ry}" fill="none" stroke="{gc}" stroke-width="1.2" opacity="0.55" transform="rotate(-18 {ccx} {ccy})"/>')
    out.append(f'<circle cx="{ccx}" cy="{ccy}" r="13" fill="#F6C24A"/>' + soft_glow(D, ccx, ccy, 50, "#FFE08A", 0.6))
    for k in range(16):
        a = math.radians(k * 22.5)
        out.append(pline([(ccx + math.cos(a) * 16, ccy + math.sin(a) * 16), (ccx + math.cos(a) * 24, ccy + math.sin(a) * 24)], "#F6C24A", 1.6, k, 0.9, 1))
    for k, (rx, ry, ang, r, col) in enumerate(((60, 40, 200, 4, "#C8A07A"), (110, 74, 130, 6, "#E8C88A"), (170, 116, 250, 5, "#D8705A"), (240, 164, 210, 11, "#E8B87A"))):
        a = math.radians(ang)
        x0, y0 = math.cos(a) * rx, math.sin(a) * ry
        t = math.radians(-18)
        px_, py_ = ccx + x0 * math.cos(t) - y0 * math.sin(t), ccy + x0 * math.sin(t) + y0 * math.cos(t)
        out.append(f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="{r}" fill="{col}"/>')
        if k == 3:
            out.append(f'<ellipse cx="{px_:.1f}" cy="{py_:.1f}" rx="22" ry="6" fill="none" stroke="#F2D8A0" stroke-width="2.4" transform="rotate(-18 {px_:.1f} {py_:.1f})"/>')
    out.append(stars_field(4, (0, 0, 600, 420), 90, cols=("#FFFFFF", "#FFF2C8"), r=(0.6, 1.6)))
    for pts in (((70, 230), (100, 210), (140, 222), (160, 196), (200, 206)), ((360, 70), (390, 96), (430, 90), (450, 120))):
        out.append(pline(list(pts), gc, 1, 5, 0.5, 1))
        for x, y in pts:
            out.append(sparkle(x, y, 5, "#FFF6D0", 0.95))
    # degree ring ticks along the edge
    for k in range(60):
        x = k * 10
        out.append(f'<path d="M {x} 0 l 0 {8 if k % 5 else 14}" stroke="{gc}" stroke-width="1" opacity="0.6"/>')
    # the table and the stack of great books
    out.append(f'<path d="M -10 512 L 610 512 L 610 610 L -10 610 Z" fill="#3A2214"/>')
    out.append(strokes(D.nid(), "M -10 512 L 610 512 L 610 610 L -10 610 Z", (-40, 512, 610, 610), ["#5A3A22", "#24140A"], 7, n=40, angle=0, length=(60, 160), width=(1, 3), opacity=(0.3, 0.5)))
    out.append(f'<path d="M -10 512 L 610 512" stroke="#8A5A36" stroke-width="2"/>')
    names = ["EUCLID", "PTOLEMY", "COPERNICUS", "KEPLER", "GALILEO"]
    pals = [("#D0706A", "#8E2A2A", "#4E1014"), ("#7FAE86", "#2E6A48", "#163A26"), ("#C8A07A", "#7A5030", "#3E2414"), ("#6A82B8", "#24386A", "#0E1A3A"), ("#A8789A", "#5E3050", "#2E1426")]
    y = 512
    for k, (nm, pal) in enumerate(zip(names, pals)):
        h = 30 - k * 1.5
        w = 380 - k * 34
        x0 = 300 - w / 2 + (k % 2) * 10 - 5
        y0 = y - h
        # spine facing us
        sp = [(x0, y0), (x0 + w, y0), (x0 + w, y), (x0, y)]
        out.append(f'<path d="{pd(shift(sp, 4, 3))}" fill="#000" opacity="0.4"/>')
        out.append(f'<path d="{pd(sp)}" fill="{pal[1]}"/>')
        out.append(f'<path d="{pd(sp)}" fill="{D.lin([(0, pal[0], 0.7), (0.5, pal[1], 0), (1, pal[2], 0.8)])}"/>')
        out.append(strokes(D.nid(), pd(sp), bbox(sp), [pal[0], pal[2]], 8 + k, n=20, angle=0, length=(30, 80), width=(1, 2), opacity=(0.15, 0.35)))
        for bx_ in (x0 + 18, x0 + w - 18):
            out.append(f'<path d="M {bx_} {y0 + 2} L {bx_} {y - 2}" stroke="#E8C060" stroke-width="2"/>')
        out.append(gilt(D, 300 + (k % 2) * 10 - 5, y - h * 0.26, nm, CINZEL, min(20, h * 0.62), ls=4, max_w=w - 60, seed=9 + k, wear=False))
        out.append(ink(pd(sp), "#0A0604", 1.2, k, 1, 0.6))
        # top board edge of each book (a sliver seen from above)
        top = [(x0 + 4, y0 - 5), (x0 + w - 2, y0 - 5), (x0 + w, y0), (x0, y0)]
        out.append(f'<path d="{pd(top)}" fill="{pal[0]}"/>')
        y = y0 - 5
    # the brass telescope on its little tripod, aimed at the ringed planet
    tx0, ty0 = 300, y
    for dx in (-26, 4, 30):
        out.append(taper([(tx0, ty0 - 46), (tx0 + dx, ty0)], 4, 3, "#6A4A2A"))
    ang = math.radians(-34)
    ux, uy = math.cos(ang), math.sin(ang)
    nx, ny = -uy, ux
    c0 = (tx0 - ux * 70, ty0 - 50 - uy * 70)
    segs = [(0, 70, 13), (70, 130, 11), (130, 176, 9)]
    for k, (a, b, r) in enumerate(segs):
        p = [(c0[0] + ux * a + nx * r, c0[1] + uy * a + ny * r), (c0[0] + ux * b + nx * r, c0[1] + uy * b + ny * r),
             (c0[0] + ux * b - nx * r, c0[1] + uy * b - ny * r), (c0[0] + ux * a - nx * r, c0[1] + uy * a - ny * r)]
        out.append(f'<path d="{pd(p)}" fill="#C8963A"/>')
        g = D.lin([(0, "#FFF0B0"), (0.35, "#E8B850"), (1, "#6A4410")], c0[0] + nx * r, c0[1] + ny * r, c0[0] - nx * r, c0[1] - ny * r, "userSpaceOnUse")
        out.append(f'<path d="{pd(p)}" fill="{g}"/>')
        out.append(ink(pd(p), "#3A2408", 1.2, k, 1, 0.7))
        bx_, by_ = c0[0] + ux * b, c0[1] + uy * b
        out.append(f'<path d="{pd([(bx_ + nx * (r + 2), by_ + ny * (r + 2)), (bx_ - nx * (r + 2), by_ - ny * (r + 2)), (bx_ - nx * (r + 2) - ux * 5, by_ - ny * (r + 2) - uy * 5), (bx_ + nx * (r + 2) - ux * 5, by_ + ny * (r + 2) - uy * 5)])}" fill="#8A5A1A"/>')
    ex, ey = c0[0] + ux * 176, c0[1] + uy * 176
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="4" ry="10" fill="#1A2A4A" transform="rotate({math.degrees(ang):.1f} {ex:.1f} {ey:.1f})"/>')
    out.append(f'<circle cx="{c0[0] - ux * 4:.1f}" cy="{c0[1] - uy * 4:.1f}" r="5" fill="#3A2408"/>')
    # an apple beside the telescope
    from fall_gouache_a import apple
    out.append(apple(D, 196, ty0 - 16, 16, seed=40))
    # lettering
    out.append(lines(D, 300, 96, 42, ["If I have seen further,", "it is by standing on", "the shoulders of giants."], SERIF_IT, 38, "#FBEFD2", max_w=440, shadow="#0A0E24"))
    out.append(byline(542, "ISAAC NEWTON · 1643–1727", "#E8C890", size=17, ls=4, max_w=340))
    return finish_w(D, out, 41, "#000000", 0.5)


# ================================================================ 19. ars longa, vita brevis — tulips, a palette and brushes
def tulip(D, x, y, L, ang, seed, pal=(("#FF9A8A", "#E2403A", "#8A1414")), open_=0.0, stem_c="#5E8A3A"):
    """Tulip head at the end of a curved stem from (x, y) toward ang; open_ 0..1 splays the petals."""
    a = math.radians(ang)
    hx, hy = x + math.cos(a) * L, y + math.sin(a) * L
    mid = (x + math.cos(a) * L * 0.5 + math.sin(a) * L * 0.08, y + math.sin(a) * L * 0.5 - math.cos(a) * L * 0.08)
    out = [taper(catmull([(x, y), mid, (hx, hy)], 6), 4, 3, stem_c)]
    s = 24
    tilt = ang + 90
    for k, (dx, w, col) in enumerate(((-0.5 - open_ * 0.3, 0.55, pal[2]), (0.5 + open_ * 0.3, 0.55, pal[1]), (0, 0.62, pal[1]))):
        pts = rot([(hx + dx * s * 0.6 - w * s * 0.5, hy), (hx + dx * s * 0.6 - w * s * 0.45, hy - s * 0.9), (hx + dx * s * (0.6 + open_ * 0.4), hy - s * 1.35),
                   (hx + dx * s * 0.6 + w * s * 0.45, hy - s * 0.9), (hx + dx * s * 0.6 + w * s * 0.5, hy)], hx, hy, tilt)
        out.append(painted(D, pts, (pal[0], col, pal[2]), seed + k, sdir=(0.6, 0.6), sk=0.18, angle=tilt - 90, n=8, inkw=1.2, hi=0.45))
    return "".join(out), (hx, hy)


@design("ars-longa")
def ars_longa():
    D = Doc2("ww-al")
    out = [f'<rect width="600" height="600" fill="#9AB0A0"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 610, 610), ["#AEC4B2", "#82988A", "#B8CCBC", "#748A7C"], 2,
                       n=260, angle=-65, length=(30, 90), width=(6, 16), opacity=(0.15, 0.35)))
    out.append(soft_glow(D, 180, 260, 280, "#FFF6DC", 0.45))
    # a framed little landscape on the wall (the art that outlives us)
    fx0, fy0, fx1, fy1 = 392, 272, 520, 356
    out.append(f'<path d="{pd([(fx0 + 6, fy0 + 8), (fx1 + 6, fy0 + 8), (fx1 + 6, fy1 + 8), (fx0 + 6, fy1 + 8)])}" fill="#2A3A30" opacity="0.35"/>')
    out.append(painted(D, rect_pts(fx0, fy0, fx1, fy1, 14, 3, 0.2), GOLD, 4, sk=0.2, angle=0, n=16, inkw=1.3, hi=0.5))
    out.append(f'<rect x="{fx0 + 10}" y="{fy0 + 10}" width="{fx1 - fx0 - 20}" height="{fy1 - fy0 - 20}" fill="{D.lin([(0, "#B8D4E8"), (1, "#F2E2B8")])}"/>')
    out.append(hill(D, ridge([(fx0 + 10, fy1 - 34), (fx0 + 60, fy1 - 46), (fx1 - 10, fy1 - 36)], 5, 4), fy1 - 10, ("#A8C080", "#7A9A50", "#4A6A30"), 6, inkw=0, n=10))
    out.append(cypress(D, fx0 + 40, fy1 - 12, 40, 7, w=10))
    # the table with a linen drape
    tb = [(-20, 400), (620, 392), (620, 620), (-20, 620)]
    out.append(painted(D, tb, ("#FFFAF0", "#EEE6D6", "#B8AC98"), 8, sdir=(0, 1), sk=0.04, angle=-3, n=60, inkw=1.2, hi=0.2))
    for k in range(6):
        x = 40 + k * 110
        out.append(taper([(x, 404), (x + 10, 500), (x, 610)], 14, 22, "#8A7E6A", 0.18))
    # stoneware jug of tulips, a fallen petal
    jx, jb = 170, 512
    out.append(cast(D, jx + 18, jb, 70, 12, strength=0.4, seed=9))
    jug = [(jx - 36, jb - 4), (jx - 48, jb - 60), (jx - 30, jb - 110), (jx - 22, jb - 128), (jx + 22, jb - 128), (jx + 30, jb - 110), (jx + 48, jb - 60), (jx + 36, jb - 4), (jx, jb + 2)]
    out.append(painted(D, jug, ("#8AA8D8", "#3A5A9A", "#18284A"), 10, sdir=(0.9, 0.3), sk=0.22, angle=-90, n=24, inkw=1.6, hi=0.45))
    out.append(ink(f"M {jx + 40} {jb - 110} q 40 10 30 50 q -6 20 -24 22", "#18284A", 6, 11, 1, 1))
    for k, y in enumerate((jb - 96, jb - 40)):
        out.append(pline([(jx - 44, y), (jx, y + 6), (jx + 44, y)], "#E8E2D0", 2, k, 0.7, 1))
    stems = [(-64, 92, ("#FFB0C0", "#E8607A", "#9A2440"), 0.2), (-100, 96, ("#FFE08A", "#F2B02A", "#A86E0A"), 0.0), (-82, 100, ("#FF9A8A", "#E2403A", "#8A1414"), 0.1),
             (-122, 84, ("#FFF4E8", "#F2E2D4", "#B8A090"), 0.4), (-46, 80, ("#FF9A8A", "#E2403A", "#8A1414"), 0.6), (-140, 70, ("#FFB0C0", "#E8607A", "#9A2440"), 0.9)]
    heads = []
    for k, (ang, L, pal, op) in enumerate(stems):
        svg, h = tulip(D, jx + (k - 2.5) * 4, jb - 124, L, ang, 20 + k * 5, pal, op)
        heads.append(svg)
    for k, (ang, L, w) in enumerate(((-122, 74, 13), (-58, 80, 15), (-152, 58, 11))):
        out.append(leaf_simple(D, jx, jb - 120, L, w, ang, ("#B8D88A", "#5E8A3A", "#2E4A1E"), 30 + k, inkw=1))
    out.append("".join(heads))
    for k, (x, y, a) in enumerate(((262, 512, 20), (232, 528, -40))):
        out.append(painted(D, rot([(x - 14, y), (x - 4, y - 10), (x + 14, y - 6), (x + 6, y + 6)], x, y, a), ("#FFB0C0", "#E8607A", "#9A2440"), 40 + k, sk=0.2, n=4, inkw=1, hi=0.5))
    # palette with paint and brushes in a jar, right
    px_, py_ = 430, 494
    pal_pts = [(px_ - 110, py_ - 10), (px_ - 70, py_ - 44), (px_ + 20, py_ - 54), (px_ + 100, py_ - 34), (px_ + 120, py_ + 4), (px_ + 70, py_ + 34), (px_ - 30, py_ + 38), (px_ - 100, py_ + 22)]
    out.append(cast(D, px_ + 10, py_ + 36, 120, 12, strength=0.35, seed=50))
    out.append(painted(D, pal_pts, ("#E8C08A", "#C08A50", "#7A5028"), 51, sdir=(0.5, 1), sk=0.15, angle=-10, n=30, inkw=1.6, hi=0.4))
    out.append(f'<path d="{blob(px_ - 60, py_ + 4, 16, 11, 52, 0.1, 12)}" fill="#EEE6D6"/>')
    rnd = random.Random(53)
    for k, (dx, dy, c) in enumerate(((-30, -30, "#E2403A"), (10, -38, "#F2B02A"), (50, -30, "#3A5A9A"), (84, -10, "#5E8A3A"), (70, 16, "#FFFFFF"), (20, 20, "#E8607A"), (-20, 16, "#7A4A2A"))):
        out.append(painted(D, blob_pts(px_ + dx, py_ + dy, 12, 8, 54 + k, 0.25, 10), (lt(c, 0.4), c, dk(c, 0.35)), 55 + k, sk=0.2, n=4, inkw=0.8, hi=0.6))
    out.append(pline([(px_ - 40, py_ - 4), (px_ - 10, py_ + 2), (px_ + 30, py_ - 8)], "#E2403A", 3, 60, 0.7, 1))
    jx2, jb2 = 528, 420
    out.append(painted(D, [(jx2 - 22, jb2), (jx2 - 24, jb2 - 50), (jx2 + 24, jb2 - 50), (jx2 + 22, jb2)], TERRACOTTA, 61, sdir=(0.9, 0.3), sk=0.22, n=10, inkw=1.3, hi=0.4))
    for k, (a, L, tip) in enumerate(((-100, 120, "#E2403A"), (-84, 132, "#3A5A9A"), (-70, 110, "#F2B02A"))):
        ax = math.radians(a)
        b0 = (jx2 + (k - 1) * 8, jb2 - 44)
        b1 = (b0[0] + math.cos(ax) * L, b0[1] + math.sin(ax) * L)
        out.append(taper([b0, b1], 5, 3, "#8A5A30"))
        fer = (b0[0] + math.cos(ax) * (L - 4), b0[1] + math.sin(ax) * (L - 4))
        out.append(taper([fer, (fer[0] + math.cos(ax) * 16, fer[1] + math.sin(ax) * 16)], 5, 5, "#C8C8D0"))
        out.append(taper([(fer[0] + math.cos(ax) * 16, fer[1] + math.sin(ax) * 16), (fer[0] + math.cos(ax) * 34, fer[1] + math.sin(ax) * 34)], 6, 1, tip))
    # lettering
    out.append(tx(300, 112, "Ars longa,", DMS, 84, "#22382E", max_w=460))
    out.append(tx(300, 184, "vita brevis", SERIF_IT, 76, "#8A2A2A", max_w=460))
    out.append(ruled(300, 220, "ART IS LONG, LIFE IS SHORT", "#22382E", font=CINZEL, size=17, ls=3, line_w=30, gap=12, max_w=380))
    out.append(byline(248, "HIPPOCRATES · c. 460–370 BC", "#4A3E2E", size=16, ls=4, max_w=340))
    return finish_w(D, out, 62)


# ================================================================ 20. gutta cavat lapidem — a drip in the grotto, a stone worn hollow
def maidenhair(D, x, y, L, ang, seed, col=(("#B8E08A", "#6AAA4A", "#2E6A2A"))):
    """Maidenhair fern frond: a dark wiry stem with fan-shaped leaflets."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    pts = [(x + math.cos(a) * L * t + math.sin(a) * L * 0.15 * t * t, y + math.sin(a) * L * t - math.cos(a) * L * 0.15 * t * t) for t in [i / 8 for i in range(9)]]
    out = [pline(pts, "#2A1A12", 1.3, seed, 0.9, 1)]
    for i, (px, py) in enumerate(pts[1:], 1):
        for sg in (-1, 1):
            b = a + sg * 1.1 + rnd.uniform(-0.2, 0.2)
            fx, fy = px + math.cos(b) * 8, py + math.sin(b) * 8
            r = 6.5 * (1 - i / 12)
            fan = [(px, py)] + [(fx + math.cos(b + t) * r, fy + math.sin(b + t) * r) for t in (-1.2, -0.6, 0, 0.6, 1.2)]
            out.append(f'<path d="{smooth_closed(fan)}" fill="{rnd.choice(col[:2])}" opacity="0.95"/>')
    return "".join(out)


def fern_frond(D, x, y, L, ang, seed, pal=(("#B8DC8A", "#6AA04A", "#2E5A26"))):
    """Arching sword-fern frond: a curved rachis with paired, tapering leaflets."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    pts = [(x + math.cos(a) * L * t + math.sin(a) * L * 0.25 * t * t, y + math.sin(a) * L * t - math.cos(a) * L * 0.25 * t * t * (1 if math.cos(a) > 0 else -1)) for t in [i / 10 for i in range(11)]]
    out = [pline(pts, pal[2], 1.6, seed, 0.9, 1)]
    for i in range(1, 10):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        d = math.atan2(y1 - y0, x1 - x0)
        ln = L * 0.24 * (1 - i / 11) + 4
        for sg in (-1, 1):
            b = d + sg * 1.0
            tip = (x0 + math.cos(b) * ln, y0 + math.sin(b) * ln)
            mid = (x0 + math.cos(b) * ln * 0.5 + math.cos(d) * 2, y0 + math.sin(b) * ln * 0.5 + math.sin(d) * 2)
            out.append(taper([(x0, y0), mid, tip], 4.6 * (1 - i / 14), 0.6, rnd.choice(pal[:2]), 0.95))
    return "".join(out)


def water_drop(D, x, y, r, seed, stretch=1.5):
    pts = [(x, y - r * stretch * 1.4)] + [(x + math.cos(math.radians(a)) * r, y + math.sin(math.radians(a)) * r) for a in range(-30, 211, 20)]
    d = smooth_closed(pts)
    g = D.lin([(0, "#E8FCFF"), (0.6, "#7AC8DA"), (1, "#2A7A90")])
    return (f'<path d="{d}" fill="{g}" opacity="0.92"/>' + ink(d, "#1E5A6A", 1.0, seed, 1, 0.6) +
            f'<path d="{blob(x - r * 0.35, y - r * 0.2, r * 0.22, r * 0.4, seed, 0.1, 8, -20)}" fill="#FFFFFF" opacity="0.9"/>')


@design("gutta-cavat-lapidem")
def gutta():
    D = Doc2("ww-gc")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#2A3A32"), (0.6, "#1A2620"), (1, "#0E1612")])}"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 610, 610), ["#3E5248", "#22302A", "#4A5E50", "#1A2420"], 2,
                       n=240, angle=-84, length=(30, 100), width=(4, 12), opacity=(0.2, 0.45)))
    # a shaft of daylight from the grotto mouth
    out.append(f'<path d="{pd([(60, -10), (200, -10), (420, 610), (230, 610)])}" fill="#E8F6E0" opacity="0.08"/>')
    out.append(f'<path d="{pd([(100, -10), (160, -10), (360, 610), (290, 610)])}" fill="#FFFFFF" opacity="0.06"/>')
    out.append(soft_glow(D, 300, 380, 220, "#C8E8D0", 0.25))
    # back walls: rock masses with moss
    for k, (pts, pal) in enumerate((([(-20, 120), (90, 160), (140, 300), (100, 420), (-20, 460)], ("#6A7A70", "#3E4E46", "#1E2A24")),
                                     ([(620, 110), (500, 170), (470, 300), (520, 430), (620, 470)], ("#6A7A70", "#3E4E46", "#1E2A24")))):
        out.append(painted(D, pts, pal, 3 + k, sdir=(1 - 2 * k, 0.3), sk=0.15, angle=-80, n=60, inkw=1.4, inkop=0.4, hi=0.25))
        out.append(specks(4 + k, bbox(pts), ["#7A9A4A", "#5A7A3A"], 24, (1.4, 3), (0.35, 0.6)))
    # ferns on the side ledges
    for k, (x, y, L, a) in enumerate(((100, 300, 80, -150), (96, 320, 70, 172), (110, 350, 64, -176), (498, 290, 80, -30), (504, 320, 74, 8), (490, 260, 64, -62))):
        out.append(fern_frond(D, x, y, L, a, 10 + k))
    # the overhanging ledge, dripping
    ledge = [(-20, -10), (620, -10), (620, 120), (520, 140), (420, 150), (340, 168), (310, 180), (290, 182), (260, 168), (180, 150), (80, 136), (-20, 120)]
    out.append(painted(D, ledge, ("#7A8A80", "#4A5A52", "#22302A"), 20, sdir=(0.2, -1), sk=0.12, angle=-6, n=100, inkw=1.6, inkop=0.5, hi=0.3))
    out.append(dab_crown(D, 150, 140, 90, 12, [("#9ABA5A", "#6A8A3A", "#3E5A26")], 21, n=70, size=(3, 6), inkw=0, base=False))
    out.append(dab_crown(D, 450, 132, 100, 12, [("#9ABA5A", "#6A8A3A", "#3E5A26")], 22, n=70, size=(3, 6), inkw=0, base=False))
    for k, x in enumerate((140, 220, 380, 460)):
        y = 150 + (6 if k % 2 else -4)
        out.append(taper([(x, y - 6), (x + 2, y + 18 + k * 4)], 4, 1, "#9AB0A8", 0.6))
    out.append(taper([(300, 176), (300, 190)], 6, 2, "#B8E0E8", 0.9))
    # the drops falling
    for k, (y, r) in enumerate(((210, 6.5), (262, 7.5), (316, 8.5))):
        out.append(water_drop(D, 300, y, r, 30 + k, 1.4 + k * 0.1))
    # the boulder with a smooth hollow worn into its top, splash crown and ripples
    i0 = len(out)
    bx, by = 300, 440
    bould = [(150, 520), (164, 440), (210, 396), (300, 380), (392, 394), (440, 436), (456, 520)]
    out.append(cast(D, bx + 10, 522, 190, 14, "#000", 0.5, 40))
    out.append(painted(D, bould, ("#B8BCB0", "#7A8076", "#3A3E38"), 41, sdir=(0.6, 0.8), sk=0.15, angle=-20, n=90, inkw=1.6, inkop=0.5, hi=0.4))
    cid = D.clip(f'<path d="{smooth_closed(bould)}"/>')
    inn = [specks(42, (150, 380, 456, 520), ["#E8ECE4", "#5A5E56", "#9AB85A"], 120, (0.8, 2.6), (0.35, 0.8))]
    for k in range(5):
        inn.append(pline([(170 + k * 60, 470 + k * 6), (200 + k * 60, 486 + k * 4), (230 + k * 60, 480)], "#4A4E46", 1.2, 43 + k, 0.4, 1))
    out.append(f'<g {cid}>{"".join(inn)}</g>')
    hol = ell_pts(bx, by - 46, 64, 15, 0, 360, 30)[:-1]
    out.append(f'<path d="{smooth_closed(hol)}" fill="#3A403A"/>')
    out.append(f'<path d="{smooth_closed(ell_pts(bx, by - 44, 58, 12, 0, 360, 30))}" fill="{D.lin([(0, "#1E5A6A"), (1, "#8ACCDA")])}"/>')
    for k in range(3):
        out.append(f'<ellipse cx="{bx}" cy="{by - 44}" rx="{14 + k * 14}" ry="{3 + k * 3}" fill="none" stroke="#E8FCFF" stroke-width="{1.6 - k * 0.3:.1f}" opacity="{0.9 - k * 0.2:.2f}"/>')
    out.append(f'<path d="{smooth_open(ell_pts(bx, by - 46, 66, 17, 0, 180, 20))}" fill="none" stroke="#D8DCD0" stroke-width="2.6" opacity="0.8"/>')
    crown = [(bx - 16, by - 44)] + [(bx + math.cos(math.radians(a)) * 16, by - 52 + math.sin(math.radians(a)) * 4) for a in range(180, 361, 30)] + [(bx + 16, by - 44)]
    out.append(f'<path d="{smooth_closed(crown)}" fill="#BFF0F4" opacity="0.7"/>')
    for k in range(7):
        a = math.radians(-165 + k * 25)
        x1, y1 = bx + math.cos(a) * 18, by - 58 + math.sin(a) * 8
        out.append(taper([(bx + math.cos(a) * 12, by - 48), (x1, y1)], 2.6, 1.2, "#E8FCFF", 0.9))
        out.append(f'<circle cx="{x1 + math.cos(a) * 5:.1f}" cy="{y1 - 5:.1f}" r="{2.4 - (k % 2) * 0.6:.1f}" fill="#E8FCFF"/>')
    # overflow trickle and the pool at its foot
    out.append(taper(catmull([(354, by - 38), (372, by - 10), (380, by + 30), (386, 516)], 5), 5, 3, "#9AD8E4", 0.75))
    out[i0:] = ['<g transform="translate(0 -30)">' + "".join(out[i0:]) + '</g>']
    pool = blob(300, 540, 320, 62, 44, 0.06, 22)
    out.append(f'<path d="{pool}" fill="{D.lin([(0, "#2A5A64"), (1, "#0E2A30")])}"/>')
    out.append(wave_lines(45, (20, 552, 580, 600), ["#6AA8B4", "#2A5A64"], n=20, L=(20, 50), w=1.4, amp=1))
    for k in range(3):
        out.append(f'<ellipse cx="386" cy="488" rx="{10 + k * 12}" ry="{3 + k * 3}" fill="none" stroke="#9AD8E4" stroke-width="1.2" opacity="{0.7 - k * 0.2:.2f}"/>')
    # lettering, cream on the dark pool / rock
    out.append(letters(D, 300, 98, "Gutta cavat lapidem", SERIF_IT, 56, "#F2EEDC", ["#FFFFFF", "#D8E8D8"], 50, max_w=450,
                       shadow="#0A120E", angle=-40, inkc=None, wob=0.4))
    out.append(byline(511, "DRIPPING WATER HOLLOWS OUT STONE", "#E8F2E4", size=17, ls=2, max_w=420))
    out.append(byline(540, "OVID · 43 BC – AD 17", "#B8D0C0", size=16, ls=5, max_w=330))
    return finish_w(D, out, 51, "#000000", 0.5)


# ================================================================ 21. a thing of beauty — an English garden wreath
def sweet_pea(D, x, y, r, seed, col=(("#F6D0F0", "#C870C0", "#7A2A7A")), rot_=0):
    out = []
    back = rot(blob_pts(x, y - r * 0.2, r, r * 0.8, seed, 0.12, 12), x, y, rot_)
    out.append(painted(D, back, col, seed, sk=0.15, n=4, inkw=0.9, hi=0.4))
    front = rot(blob_pts(x + r * 0.15, y + r * 0.35, r * 0.55, r * 0.45, seed + 1, 0.1, 10), x, y, rot_)
    out.append(painted(D, front, (lt(col[0], 0.3), col[0], col[1]), seed + 1, sk=0.15, n=3, inkw=0.8, hi=0.5))
    return "".join(out)


def forget_me_not(x, y, r, col="#7AA8E8"):
    out = []
    for k in range(5):
        a = math.radians(k * 72 - 90)
        out.append(f'<circle cx="{x + math.cos(a) * r * 0.55:.1f}" cy="{y + math.sin(a) * r * 0.55:.1f}" r="{r * 0.5:.1f}" fill="{col}"/>')
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.3:.1f}" fill="#FFE07A"/>')
    return "".join(out)


@design("a-thing-of-beauty")
def thing_of_beauty():
    D = Doc2("ww-tb")
    out = [paper(D.nid(), "#FBF4E6", FLECK, 21, 1.0)]
    out.append(blooms(22, ["#F6D8D8", "#E8E8C8", "#F2DCE8"], 8, (60, 60, 540, 540), (80, 160), (0.06, 0.12)))
    cx, cy, R = 300, 300, 214
    rnd = random.Random(23)

    def on_ring(deg, dr=0):
        a = math.radians(deg)
        return cx + math.cos(a) * (R + dr), cy + math.sin(a) * (R + dr)

    # fullness of the wreath along the ring: two heavy crescents (lower left, upper right)
    def full(deg):
        d1 = abs(((deg - 135) + 180) % 360 - 180)
        d2 = abs(((deg + 45) + 180) % 360 - 180)
        return 0.45 + 0.55 * max(math.exp(-(d1 / 60) ** 2), math.exp(-(d2 / 50) ** 2))

    # twining stems
    for k in range(3):
        ring = [on_ring(a, 6 * math.sin(math.radians(a * 3 + k * 60))) for a in range(0, 361, 8)]
        out.append(pline(ring, "#5E7A3A", 2.2 - k * 0.4, 24 + k, 0.8, 1))
    # leaves, many, in two greens plus silvery round eucalyptus
    for k in range(240):
        deg = rnd.uniform(0, 360)
        f = full(deg)
        if rnd.random() > f:
            continue
        x, y = on_ring(deg, rnd.uniform(-34, 34) * f)
        tang = deg + 90 + rnd.choice([-40, 40, 140, -140]) + rnd.uniform(-20, 20)
        if rnd.random() < 0.2:
            for j in range(3):
                out.append(painted(D, blob_pts(x + j * 6, y + j * 5, 7, 6, 200 + k * 3 + j, 0.05, 10), ("#DCE8DC", "#9AB4A4", "#5A746A"), 300 + k + j, sk=0.2, n=2, inkw=0.7, hi=0.4))
        else:
            out.append(leaf_simple(D, x, y, rnd.uniform(20, 32) * (0.7 + 0.4 * f), rnd.uniform(6, 10), tang,
                                   rnd.choice([("#B8D88A", "#5E8A3A", "#2E4A1E"), ("#C8DCA0", "#7A9A4A", "#3E5A26"), ("#A8C88A", "#4E7A3E", "#22401E")]), 25 + k, vein=True, inkw=0.8))
    # forget-me-nots and tiny buds scattered in
    for k in range(60):
        deg = rnd.uniform(0, 360)
        if rnd.random() > full(deg):
            continue
        x, y = on_ring(deg, rnd.uniform(-30, 30))
        out.append(forget_me_not(x, y, rnd.uniform(4.5, 6.5), rnd.choice(["#7AA8E8", "#8AB8F0", "#A8C8F8"])))
    # sweet peas and roses: big blooms in the crescents, smaller ones linking them
    blooms_ = [(120, "rose", 34, 0), (150, "rose", 28, 1), (98, "pea", 18, 0), (172, "pea", 16, 1), (135, "rose", 22, 2), (196, "bud", 12, 0), (80, "bud", 11, 0),
               (-45, "rose", 32, 1), (-20, "rose", 24, 0), (-70, "pea", 17, 0), (0, "pea", 15, 1), (-52, "rose", 18, 2), (24, "bud", 11, 0), (-96, "bud", 11, 0),
               (250, "rose", 16, 2), (40, "rose", 15, 1), (225, "pea", 13, 1), (60, "pea", 12, 0)]
    for k, (deg, kind, size, pc) in enumerate(blooms_):
        x, y = on_ring(deg, rnd.uniform(-8, 8))
        if kind == "rose":
            pal = [("#FFD0D8", "#F07A90", "#A83050"), ("#FFF6EA", "#F6DCC8", "#C89A80"), ("#FFE4B0", "#F2B060", "#B0702A")][pc]
            out.append(cast(D, x + 4, y + 6, size * 1.05, size * 0.9, "#5A3A2A", 0.2, 40 + k))
            out.append(rose_bloom(D, x, y, size, 40 + k, pal=pal, rot_=deg))
        elif kind == "pea":
            out.append(sweet_pea(D, x, y, size, 60 + k, col=[("#F6D0F0", "#C870C0", "#7A2A7A"), ("#FFE0E8", "#F2A0B8", "#B05070")][pc], rot_=deg))
        else:
            out.append(painted(D, rot(blob_pts(x, y, size * 0.6, size, 80 + k, 0.1, 10), x, y, deg + 90), ("#FFD0D8", "#F07A90", "#A83050"), 80 + k, sk=0.2, n=3, inkw=0.8, hi=0.4))
            out.append(leaf_simple(D, x, y + 2, size * 0.9, 4, deg + 90 + 160, ("#B8D88A", "#5E8A3A", "#2E4A1E"), 90 + k, vein=False, inkw=0.6))
    # a bee and a blue butterfly visiting
    from summer_gouache import honeybee
    out.append(honeybee(D, 470, 120, 0.85, 90, -20))
    bx, by = 112, 150
    for sg in (-1, 1):
        out.append(painted(D, [(bx, by), (bx + sg * 16, by - 14), (bx + sg * 20, by - 2), (bx + sg * 7, by + 4)], ("#C8E0FF", "#6A9AE0", "#2A4A9A"), 91 + sg, sk=0.15, n=4, inkw=0.9, hi=0.4))
        out.append(painted(D, [(bx, by + 1), (bx + sg * 12, by + 7), (bx + sg * 9, by + 14), (bx + sg * 2, by + 7)], ("#C8E0FF", "#6A9AE0", "#2A4A9A"), 93 + sg, sk=0.15, n=3, inkw=0.9, hi=0.4))
    out.append(pline([(bx, by - 7), (bx, by + 9)], INK, 2, 95, 0.9, 1))
    # the line, inside the wreath
    out.append(tx(cx, 244, "A thing of beauty", SERIF_IT, 40, "#8A2A3A", max_w=270))
    out.append(tx(cx, 302, "is a joy", SERIF_IT, 56, "#2E4A26", max_w=300))
    out.append(tx(cx, 360, "for ever.", SERIF_IT, 56, "#2E4A26", max_w=300))
    out.append(flourish(cx, 384, 110, "#9A7A5A", 1.6))
    out.append(byline(416, "JOHN KEATS · 1795–1821", "#6A4A3A", size=16, ls=3, max_w=260))
    return finish_w(D, out, 96)


# ================================================================ 22. to thine own self be true — a compass on an old sea chart
@design("to-thine-own-self-be-true")
def thine_own_self():
    D = Doc2("ww-ts")
    out = [paper(D.nid(), "#EEDDB8", FLECK, 31, 1.4)]
    out.append(blooms(32, ["#D8B888", "#C8A070", "#E8D0A0"], 10, (0, 0, 600, 600), (40, 120), (0.08, 0.16)))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFFFFF", 0), (0.7, "#8A5A2A", 0.08), (1, "#5A3A1A", 0.45)], r=0.75)}"/>')
    # an old chart: coastline, soundings, rhumb lines radiating from a wind rose
    rnd = random.Random(33)
    coast = ridge([(-20, 300), (60, 280), (100, 320), (140, 300), (170, 360), (130, 420), (180, 470), (140, 540), (200, 620)], 34, 12)
    land = coast + [(-20, 620)]
    out.append(f'<path d="{smooth_closed(land)}" fill="#E2C890" opacity="0.8"/>')
    for k in range(4):
        out.append(f'<path d="{smooth_open([(x + 8 + k * 7, y) for x, y in coast])}" fill="none" stroke="#7A9AA8" stroke-width="1" opacity="{0.6 - k * 0.12:.2f}"/>')
    out.append(ink(smooth_open(coast), "#6A4A2A", 1.6, 35, 1, 0.8))
    for k in range(5):
        x, y = rnd.uniform(20, 120), rnd.uniform(340, 560)
        out.append(f'<path d="M {x:.1f} {y:.1f} l 5 -8 l 5 8" fill="none" stroke="#6A4A2A" stroke-width="1.2"/>')
    for k in range(28):
        x, y = rnd.uniform(220, 580), rnd.uniform(300, 580)
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="Georgia, serif" font-size="9" fill="#6A5A40" opacity="0.6">{rnd.randint(4, 40)}</text>')
    rcx, rcy = 300, 392
    for k in range(32):
        a = math.radians(k * 11.25)
        out.append(f'<path d="M {rcx} {rcy} L {rcx + math.cos(a) * 520:.1f} {rcy + math.sin(a) * 520:.1f}" stroke="{["#8A2A1A", "#2A4A6A", "#6A5A40"][k % 3]}" stroke-width="0.9" opacity="0.35"/>')
    out.append(tall_ship_s(470, 300, 0.9))
    # a rosemary sprig ("for remembrance") and a quill lying on the chart
    rp = catmull([(60, 560), (110, 520), (170, 500), (220, 492)], 6)
    out.append(taper(rp, 3, 2, "#6A5A3A"))
    for k, (x, y) in enumerate(rp[1::2]):
        for sg in (-1, 1):
            out.append(taper([(x, y), (x + sg * 6 + 8, y + sg * 14 - 6)], 3.4, 1, "#5E7A5A"))
            out.append(taper([(x, y), (x + sg * 6 + 8, y + sg * 14 - 6)], 1.2, 0.4, "#B8C8B0", 0.7))
    out.append(quill(D, 470, 560, 560, 380, 36, w=22))
    # the compass: a turned wooden bowl with a brass bezel, card and needle pointing true north
    ccx, ccy, R = 300, 400, 124
    out.append(cast(D, ccx + 14, ccy + 18, R * 1.08, R * 1.02, "#2A1A0A", 0.55, 37))
    out.append(painted(D, blob_pts(ccx, ccy, R + 14, R + 14, 38, 0.004, 48), ("#C8925E", "#8E5A30", "#3E200C"), 39, sdir=(0.6, 0.8), sk=0.1, angle=-40, n=40, inkw=1.6, hi=0.4))
    out.append(f'<circle cx="{ccx}" cy="{ccy}" r="{R + 2}" fill="none" stroke="#C89A3A" stroke-width="9"/>')
    out.append(f'<circle cx="{ccx}" cy="{ccy}" r="{R + 2}" fill="none" stroke="#FFF0B0" stroke-width="2" opacity="0.6" stroke-dasharray="40 30"/>')
    out.append(f'<circle cx="{ccx}" cy="{ccy}" r="{R - 3}" fill="#F8F0DC"/>')
    out.append(f'<circle cx="{ccx}" cy="{ccy}" r="{R - 3}" fill="{D.rad([(0, "#FFFFFF", 0.3), (1, "#C8A878", 0.4)])}"/>')
    for k in range(72):
        a = math.radians(k * 5 - 90)
        r0 = R - (16 if k % 9 == 0 else 10)
        out.append(f'<path d="M {ccx + math.cos(a) * r0:.1f} {ccy + math.sin(a) * r0:.1f} L {ccx + math.cos(a) * (R - 5):.1f} {ccy + math.sin(a) * (R - 5):.1f}" stroke="#3A2A1A" stroke-width="{1.6 if k % 9 == 0 else 0.8}"/>')
    out.append(compass_rose(ccx, ccy, R * 0.66, "#3A2A1A", "#B8302A", "#E8D2A0").replace(f'<text x="{ccx}" y="{ccy - R * 0.66 - 6:.1f}"', '<text x="-999" y="-999"'))
    for lbl, a in (("N", -90), ("E", 0), ("S", 90), ("W", 180)):
        x, y = ccx + math.cos(math.radians(a)) * (R - 30), ccy + math.sin(math.radians(a)) * (R - 30) + 7
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" {CINZEL} font-size="20" fill="#8A1A10">{lbl}</text>')
    # the needle
    out.append(f'<path d="{pd([(ccx, ccy - R + 34), (ccx + 10, ccy), (ccx, ccy + 10), (ccx - 10, ccy)])}" fill="#B8302A"/>')
    out.append(f'<path d="{pd([(ccx, ccy - R + 34), (ccx + 10, ccy), (ccx, ccy)])}" fill="#7A1A10"/>')
    out.append(f'<path d="{pd([(ccx, ccy + R - 34), (ccx + 9, ccy), (ccx, ccy - 8), (ccx - 9, ccy)])}" fill="#2A3A5A"/>')
    out.append(f'<circle cx="{ccx}" cy="{ccy}" r="7" fill="#C89A3A"/><circle cx="{ccx - 2}" cy="{ccy - 2}" r="2.5" fill="#FFF0B0"/>')
    out.append(taper(catmull([(ccx - R * 0.66, ccy - R * 0.4), (ccx - R * 0.42, ccy - R * 0.66), (ccx - R * 0.1, ccy - R * 0.8)], 6), 9, 2, "#FFFFFF", 0.45))
    # lettering
    out.append(tx(300, 96, "This above all:", SERIF_IT, 30, "#6A2A1A", max_w=360))
    out.append(lines(D, 300, 152, 50, ["to thine own self", "be true."], SERIF_IT, 50, "#2A1A0E", max_w=430))
    out.append(f'<path d="{hg.org_rect(160, 522, 280, 28, 40, 0.5, 14, 3)}" fill="#F6E8C8" opacity="0.85"/>')
    out.append(byline(542, "WILLIAM SHAKESPEARE · HAMLET", "#3A2410", size=16, ls=2, max_w=270))
    return finish_w(D, out, 41)


def tall_ship_s(x, y, s, col="#5A3418", sail="#F6ECD4"):
    from storybook_classics_painted import tall_ship
    return tall_ship(x, y, s, col, sail)


# ================================================================ 23. such stuff as dreams — cloud castles over a moonlit isle
@design("such-stuff-as-dreams")
def such_stuff():
    D = Doc2("ww-dr")
    out = [sky(D, [(0, "#2A2858"), (0.35, "#5A4A8A"), (0.6, "#B880A8"), (0.75, "#F2B0A8")], 3, 440, ["#6A5A9A", "#C890B8", "#F8C8C0"], 70)]
    out.append(stars_field(4, (0, 0, 600, 260), 90))
    MX, MY = 470, 236
    out.append(soft_glow(D, MX, MY, 160, "#FFF2D8", 0.55))
    out.append(f'<circle cx="{MX}" cy="{MY}" r="40" fill="#FFF6E2"/>')
    out.append(f'<circle cx="{MX + 14}" cy="{MY - 6}" r="36" fill="#7A5A98" opacity="0.0"/>')
    for k, (x, y, r) in enumerate(((MX - 12, MY - 8, 7), (MX + 10, MY + 10, 9), (MX + 14, MY - 16, 5))):
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#E8D8C8" opacity="0.6"/>')
    # a castle built of cloud, glowing at the rims
    cc = ("#FFF4F0", "#E8C8E0", "#9A7AB0")
    for k, (x, y, w_, rows) in enumerate(((170, 340, 230, 3), (320, 356, 220, 3), (240, 296, 140, 2))):
        out.append(puff_cloud(D, x, y, w_, 10 + k, pal=cc, rows=rows))
    for k, (x, top, w_) in enumerate(((166, 236, 40), (226, 206, 50), (290, 250, 38), (340, 270, 34))):
        body = [(x - w_ / 2, 300), (x - w_ / 2 - 4, top + 30), (x - w_ / 2 + 6, top), (x + w_ / 2 - 6, top), (x + w_ / 2 + 4, top + 30), (x + w_ / 2, 300)]
        out.append(painted(D, body, ("#FFF6F8", "#E2CCE6", "#9A7AB0"), 20 + k, sdir=(-0.8, 0.3), sk=0.22, angle=-90, n=12, inkw=1.0, inkc="#8A6AA0", hi=0.6))
        for j in range(3):
            out.append(f'<path d="{hg.org_rect(x - w_ / 2 - 2 + j * (w_ / 2 - 3), top - 9, w_ * 0.26, 10, 30 + k * 3 + j, 0.3, 6, 1)}" fill="#F6E8F4"/>')
        out.append(f'<path d="M {x - w_ / 2 - 4} {top} L {x + w_ / 2 + 4} {top}" stroke="#B898C8" stroke-width="2"/>')
        for j, wy in enumerate((top + 22, top + 52)):
            out.append(soft_glow(D, x, wy + 6, 12, "#FFD890", 0.6))
            out.append(f'<rect x="{x - 4}" y="{wy}" width="8" height="13" rx="4" fill="#FFE8A8"/>')
        out.append(pline([(x, top - 9), (x, top - 34)], "#8A6AA0", 1.4, k, 1, 1))
        out.append(f'<path d="{pd([(x, top - 34), (x + 16, top - 30), (x, top - 25)])}" fill="#F27A9A"/>')
    out.append(puff_cloud(D, 250, 380, 330, 14, pal=cc, rows=1))
    # the sea and an island with a lone tree, the moon path
    HZ = 430
    out.append(f'<path d="M -10 {HZ} L 610 {HZ} L 610 610 L -10 610 Z" fill="{D.lin([(0, "#8A6A9A"), (1, "#2A2448")])}"/>')
    rnd = random.Random(5)
    for _ in range(120):
        y = HZ + rnd.random() ** 1.2 * 200
        k = (y - HZ) / 200
        x = MX + rnd.gauss(0, 20 + k * 60)
        out.append(f'<path d="M {x - 4 - k * 14:.1f} {y:.1f} L {x + 4 + k * 14:.1f} {y:.1f}" stroke="#FFF2D8" stroke-width="{1 + k * 1.6:.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    out.append(wave_lines(6, (0, HZ + 6, 600, 600), ["#B898C8", "#4A3A6A"], n=60, L=(20, 60), w=1.4, amp=1.5))
    isl = [(30, HZ + 4), (60, HZ - 30), (110, HZ - 52), (160, HZ - 40), (200, HZ - 12), (230, HZ + 4)]
    out.append(painted(D, isl, ("#6A5A7A", "#3A2E4A", "#1A1428"), 7, sdir=(-0.6, 0.6), sk=0.15, angle=-10, n=20, inkw=1.2, hi=0.3))
    out.append(ink(smooth_open(isl[1:4]), "#E8C8D8", 1.4, 8, 1, 0.5))
    out.append(taper([(120, HZ - 50), (126, HZ - 92), (134, HZ - 110)], 5, 2, "#1A1428"))
    out.append(dab_crown(D, 136, HZ - 118, 22, 14, [("#4A3E5A", "#2A2238", "#140E1E")], 9, n=40, size=(3, 5), inkw=0))
    # a small ship asleep at anchor, its lantern lit
    sx_, sy_ = 330, HZ + 66
    out.append(f'<path d="{pd([(sx_ - 34, sy_), (sx_ + 34, sy_), (sx_ + 24, sy_ + 10), (sx_ - 26, sy_ + 10)])}" fill="#1A1428"/>')
    for mx, h in ((-10, 56), (12, 46)):
        out.append(pline([(sx_ + mx, sy_), (sx_ + mx, sy_ - h)], "#1A1428", 2, mx, 1, 1))
        out.append(pline([(sx_ + mx - 14, sy_ - h * 0.75), (sx_ + mx + 14, sy_ - h * 0.75)], "#1A1428", 1.4, mx + 3, 1, 1))
    out.append(soft_glow(D, sx_ + 30, sy_ - 4, 20, "#FFD27A", 0.8) + f'<circle cx="{sx_ + 30}" cy="{sy_ - 4}" r="2.4" fill="#FFF2B0"/>')
    out.append(f'<path d="{pd([(sx_ - 30, sy_ + 12), (sx_ + 30, sy_ + 12), (sx_ + 20, sy_ + 40), (sx_ - 20, sy_ + 40)])}" fill="#1A1428" opacity="0.3"/>')
    # lettering
    out.append(lines(D, 300, 96, 48, ["We are such stuff", "as dreams are made on."], SERIF_IT, 46, "#FFF0E6", max_w=470, shadow="#120A20"))
    out.append(byline(170, "WILLIAM SHAKESPEARE · THE TEMPEST", "#E8C8E8", size=16, ls=2, max_w=400))
    return finish_w(D, out, 50, "#0A0614", 0.5)


# ================================================================ 24. the love which moves the sun — an illuminated page
@design("the-love-which-moves-the-sun")
def love_moves_sun():
    D = Doc2("ww-lm")
    out = [paper(D.nid(), "#F6ECD4", FLECK, 61, 1.2)]
    out.append(blooms(62, ["#E8D4A8", "#F2E2C0"], 8, (0, 0, 600, 600), (60, 140), (0.08, 0.14)))
    # gilt border bands with painted vine scrolls in lapis, vermilion and green
    gold = D.lin([(0, "#FFF0B0"), (0.4, "#E8BE5A"), (0.6, "#A87A28"), (1, "#F6DC90")], 0, 0, 1, 1)
    for (x0, y0, x1, y1) in ((26, 26, 574, 44), (26, 556, 574, 574), (26, 26, 44, 574), (556, 26, 574, 574)):
        out.append(f'<path d="{hg.org_rect(x0, y0, x1 - x0, y1 - y0, int(x0 + y0), 0.4, 14, 1)}" fill="{gold}"/>')
    out.append(rule_frame(D, 50, 50, 550, 550, "#2A3A8A", 2.2, 0, 0, seed=63))
    rnd = random.Random(64)
    vine = []
    for side in range(4):
        for k in range(12):
            t = (k + 0.5) / 12
            if side == 0:
                x, y = 40 + t * 520, 35
            elif side == 1:
                x, y = 40 + t * 520, 565
            elif side == 2:
                x, y = 35, 40 + t * 520
            else:
                x, y = 565, 40 + t * 520
            c = ["#2A4A9A", "#C8382A", "#3A7A4A"][k % 3]
            vine.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.2" fill="{c}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="1.6" fill="#FFF6D0"/>')
    out.append("".join(vine))
    # the miniature: the heavens as Dante's spheres, the sun among them, gold leaf beyond the stars
    mcx, mcy, MR = 300, 222, 150
    out.append(f'<circle cx="{mcx}" cy="{mcy}" r="{MR + 10}" fill="{gold}"/>')
    out.append(ink(smooth_closed(ell_pts(mcx, mcy, MR + 10, MR + 10, 0, 360, 40)[:-1]), "#6A4A14", 1.6, 65, 1, 0.8))
    for k in range(40):
        a = math.radians(k * 9)
        out.append(f'<circle cx="{mcx + math.cos(a) * (MR + 4):.1f}" cy="{mcy + math.sin(a) * (MR + 4):.1f}" r="1.6" fill="#7A5418"/>')
    rings = [(MR, "#1E2A7A"), (MR * 0.86, "#2A3A9A"), (MR * 0.72, "#3A4AA8"), (MR * 0.58, "#4A62B8"), (MR * 0.44, "#6A82C8"), (MR * 0.3, "#8EA8D8"), (MR * 0.17, "#B8D0E8")]
    for k, (r, c) in enumerate(rings):
        out.append(f'<circle cx="{mcx}" cy="{mcy}" r="{r:.1f}" fill="{c}"/>')
        out.append(f'<circle cx="{mcx}" cy="{mcy}" r="{r:.1f}" fill="none" stroke="#E8C060" stroke-width="1.6"/>')
    out.append(stars_field(66, (mcx - MR, mcy - MR, mcx + MR, mcy + MR), 0))
    for k in range(40):
        a = rnd.uniform(0, 6.28)
        r = rnd.uniform(MR * 0.88, MR * 0.98)
        out.append(sparkle(mcx + math.cos(a) * r, mcy + math.sin(a) * r, rnd.uniform(2.5, 4.5), "#FFE8A0", 0.95))
    # earth at the centre, planets on their spheres, the sun on the fourth
    out.append(f'<circle cx="{mcx}" cy="{mcy}" r="{MR * 0.1:.1f}" fill="#4A8A5A"/><path d="{blob(mcx - 3, mcy - 2, 7, 5, 67, 0.2, 10)}" fill="#C8A060"/>')
    pl = [(1, 210, 5, "#E8E8F0"), (2, 320, 5, "#D8C8A8"), (3, 40, 6, "#F2E2C8"), (5, 150, 6, "#D8604A"), (6, 270, 7, "#E8C890")]
    for (i, ang, r, c) in pl:
        rr = (rings[-i - 1][0] + rings[-i][0]) / 2 if i < 6 else rings[1][0] * 0.93
        a = math.radians(ang)
        out.append(f'<circle cx="{mcx + math.cos(a) * rr:.1f}" cy="{mcy + math.sin(a) * rr:.1f}" r="{r}" fill="{c}" stroke="#2A1A08" stroke-width="0.8"/>')
    sa = math.radians(-50)
    sr = (rings[3][0] + rings[2][0]) / 2
    sx_, sy_ = mcx + math.cos(sa) * sr, mcy + math.sin(sa) * sr
    out.append(soft_glow(D, sx_, sy_, 40, "#FFE08A", 0.8))
    out.append(f'<circle cx="{sx_:.1f}" cy="{sy_:.1f}" r="13" fill="#F6C83A" stroke="#A86A10" stroke-width="1.4"/>')
    for k in range(12):
        a = math.radians(k * 30)
        out.append(taper([(sx_ + math.cos(a) * 15, sy_ + math.sin(a) * 15), (sx_ + math.cos(a) * 23, sy_ + math.sin(a) * 23)], 3, 0.6, "#E8A82A"))
    # a white rose of the empyrean at the top of the miniature
    out.append(rose_bloom(D, mcx, mcy - MR - 4, 16, 68, pal=("#FFFFFF", "#F6EEE6", "#C8B4A8")))
    for sg in (-1, 1):
        out.append(leaf_simple(D, mcx + sg * 12, mcy - MR - 2, 22, 7, -90 + sg * 70, ("#B8D88A", "#5E8A3A", "#2E4A1E"), 69 + sg, inkw=0.8))
    # the line, with the first words in red as in a rubric
    out.append(tx(300, 444, "The Love which moves", SERIF_IT, 40, "#A8281E", max_w=440))
    out.append(tx(300, 490, "the sun and the other stars.", SERIF_IT, 40, "#1E2458", max_w=440))
    out.append(flourish(300, 512, 150, "#C89A3A", 1.6))
    out.append(byline(538, "DANTE ALIGHIERI · 1265–1321", "#5A3A1A", size=16, ls=3, max_w=360))
    return finish_w(D, out, 70)


# ================================================================ 25. learning without thought — the scholar's desk from above
def ink_stone(D, x, y, w, h, seed):
    out = [f'<path d="{pd(shift(rect_pts(x, y, x + w, y + h, 12, seed, 0.3), 6, 8))}" fill="#000" opacity="0.4"/>']
    out.append(painted(D, rect_pts(x, y, x + w, y + h, 12, seed, 0.3), ("#5A5A62", "#2E2E36", "#141418"), seed, sdir=(0.5, 1), sk=0.15, n=20, inkw=1.2, inkc="#000", hi=0.3))
    out.append(f'<path d="{hg.org_rect(x + 10, y + 10, w - 20, h - 20, seed + 1, 0.3, 10, 6)}" fill="#24242C"/>')
    out.append(f'<path d="{blob(x + w / 2, y + h * 0.28, w * 0.3, h * 0.12, seed + 2, 0.1, 12)}" fill="#08080C"/>')
    out.append(f'<path d="{blob(x + w / 2 - 8, y + h * 0.25, w * 0.08, h * 0.03, seed + 3, 0.1, 8)}" fill="#FFFFFF" opacity="0.4"/>')
    return "".join(out)


def bamboo_book(D, x, y, n, w, h, seed, ang=0):
    """Bamboo slips (jiandu) laid side by side, tied with two cords."""
    out = []
    rnd = random.Random(seed)
    for k in range(n):
        sx = x + k * (w + 1.5)
        pts = rot(rect_pts(sx, y, sx + w, y + h, 20, seed + k, 0.2), x, y, ang)
        out.append(painted(D, pts, ("#F2E0A8", "#D8B870", "#9A7A3A"), seed + k, sdir=(1, 0.1), sk=0.2, angle=-90 + ang, n=6, inkw=0.9, inkc="#6A4A1A", hi=0.4))
        for j in range(rnd.randint(4, 7)):
            cy_ = y + 14 + j * (h - 28) / 7
            a, b = rot([(sx + w * 0.3, cy_), (sx + w * 0.7, cy_ + 3)], x, y, ang)
            out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#2A1A0A" stroke-width="2" opacity="0.65"/>')
    for t in (0.22, 0.78):
        a, b = rot([(x - 4, y + h * t), (x + n * (w + 1.5) + 4, y + h * t)], x, y, ang)
        out.append(pline([a, b], "#7A3A1A", 2.2, seed + int(t * 10), 0.9, 1))
    return "".join(out)


@design("learning-without-thought")
def learning_without_thought():
    D = Doc2("ww-lt")
    # dark rosewood desk with grain
    from brasil_painted import wood_planks
    out = [wood_planks(D, 0, 600, 4, pal=("#8A4A30", "#5A2A1A", "#2A120A"), n=4)]
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#FFE8C8", 0.12), (0.7, "#000", 0.05), (1, "#000", 0.45)], cx=0.45, cy=0.4, r=0.8)}"/>')
    # a sheet of xuan paper in the middle, weighted by a carved paperweight
    sh = rect_pts(108, 128, 492, 470, 20, 5, 0.6)
    out.append(f'<path d="{pd(shift(sh, 6, 9))}" fill="#000" opacity="0.4"/>')
    out.append(painted(D, sh, ("#FFFCF2", "#F6EEDA", "#C8B898"), 6, sdir=(0.3, 1), sk=0.03, angle=-5, n=40, inkw=1.0, hi=0.2))
    rnd = random.Random(7)
    out.append(specks(8, (110, 130, 490, 468), ["#C8B898", "#E8DCC0"], 80, (0.5, 1.6), (0.3, 0.6)))
    for k in range(1, 5):
        out.append(f'<path d="M {108 + k * 76.8:.1f} 132 L {108 + k * 76.8:.1f} 466" stroke="#D8C8A8" stroke-width="0.8" opacity="0.6"/>')
    out.append(painted(D, rect_pts(124, 112, 476, 136, 12, 9, 0.3), ("#6A8A7A", "#2E5A4A", "#123428"), 10, sdir=(0.3, 1), sk=0.2, angle=0, n=16, inkw=1.2, hi=0.4))
    out.append(tx(300, 130, "THE ANALECTS · II.15", CINZEL, 16, "#E8F0E0", ls=4, max_w=320))
    # the words in ink
    out.append(lines(D, 300, 198, 38, ["Learning without thought", "is labour lost;"], SERIF_IT, 34, "#1A1A1E", max_w=350))
    out.append(lines(D, 300, 306, 38, ["thought without learning", "is perilous."], SERIF_IT, 34, "#1A1A1E", max_w=350))
    out.append(hanko(D, 440, 430, 30, 12, col="#C8281E", paper_c="#F6EEDA"))
    out.append(byline(436, "CONFUCIUS · 551–479 BC", "#5A2A1A", size=17, ls=4, max_w=300, x=270))
    # ink stone with ink stick, brush on a mountain-shaped rest, a celadon cup of tea, plum blossoms, bamboo slips
    out.append(ink_stone(D, 22, 490, 120, 90, 13))
    out.append(painted(D, rot(rect_pts(150, 520, 172, 586, 10, 14, 0.3), 160, 550, 18), ("#3A3A42", "#1A1A20", "#08080C"), 15, sk=0.2, n=6, inkw=1, inkc="#000", hi=0.3))
    out.append(f'<path d="{pd(rot([(150, 520), (172, 520), (172, 532), (150, 532)], 160, 550, 18))}" fill="#C89A3A" opacity="0.8"/>')
    br = [(196, 510), (238, 478), (262, 506), (286, 476), (330, 510)]
    out.append(painted(D, br + [(330, 518), (196, 518)], ("#C8D8C8", "#8AA898", "#3E5A4A"), 16, sdir=(0.4, 1), sk=0.2, n=10, inkw=1.2, hi=0.4))
    bb = [(176, 494), (362, 470)]
    out.append(taper(bb, 9, 7, "#A87A3A"))
    for k in range(5):
        out.append(f'<path d="M {200 + k * 30} {491 - k * 4} l 2 6" stroke="#6A4A1A" stroke-width="1.6"/>')
    out.append(taper([(362, 470), (384, 467), (404, 470)], 10, 1, "#141418"))
    tcx, tcy = 520, 530
    out.append(cast(D, tcx + 6, tcy + 8, 52, 46, "#000", 0.5, 17))
    out.append(painted(D, blob_pts(tcx, tcy, 48, 46, 18, 0.02, 24), ("#D8ECD8", "#9AC0A8", "#4E7A64"), 19, sdir=(0.6, 0.8), sk=0.15, n=12, inkw=1.3, hi=0.5))
    out.append(f'<circle cx="{tcx}" cy="{tcy}" r="38" fill="#C8A040"/>')
    out.append(f'<circle cx="{tcx}" cy="{tcy}" r="38" fill="{D.rad([(0, "#E8C060"), (1, "#8A6A1A")])}"/>')
    out.append(f'<path d="{blob(tcx - 12, tcy - 12, 10, 5, 20, 0.2, 10, -30)}" fill="#FFFFFF" opacity="0.6"/>')
    out.append(steam_wisps(tcx, tcy - 30, 50, 21, "#FFFFFF", 2, 16, 4, 0.5))
    out.append(bamboo_book(D, 500, 120, 5, 14, 210, 22, ang=8))
    from japan_painted import bark_branch, ume_flower
    out.append(bark_branch(D, [(-10, 140), (40, 120), (80, 80), (96, 40)], 7, 3, 23))
    out.append(bark_branch(D, [(40, 120), (70, 136), (96, 130)], 4, 2, 24))
    for k, (x, y, r) in enumerate(((84, 82, 10), (64, 108, 9), (96, 130, 9), (30, 132, 8), (96, 46, 8), (48, 90, 6))):
        out.append(ume_flower(D, x, y, r, 25 + k, rot_=k * 20))
    return finish_w(D, out, 30, "#000000", 0.5)


# ================================================================ 26. the heart has its reasons — a heart drawn by compass, bursting into bloom
@design("the-heart-has-its-reasons")
def heart_reasons():
    D = Doc2("ww-hr")
    out = [paper(D.nid(), "#F4EBD8", FLECK, 71, 1.2)]
    out.append(blooms(72, ["#E8D4B0", "#F2E2C8"], 8, (0, 0, 600, 600), (60, 140), (0.08, 0.14)))
    # faint graph ruling of a geometer's notebook
    for k in range(0, 620, 24):
        out.append(f'<path d="M {k} 0 L {k} 600" stroke="#9AB0C0" stroke-width="0.7" opacity="0.35"/>')
        out.append(f'<path d="M 0 {k} L 600 {k}" stroke="#9AB0C0" stroke-width="0.7" opacity="0.35"/>')
    # construction: two circles, the tangents meeting at the point, arcs and labels in pencil
    c1, c2, r = (250, 310), (350, 310), 62
    tip = (300, 446)
    pen = "#5A5A62"
    for c in (c1, c2):
        out.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="{r}" fill="none" stroke="{pen}" stroke-width="1.2" opacity="0.7"/>')
        out.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="2.4" fill="{pen}"/>')
    out.append(pline([(160, 310), (440, 310)], pen, 1, 73, 0.55, 1))
    out.append(pline([(300, 220), (300, 470)], pen, 1, 74, 0.55, 1))
    out.append(pline([(c1[0] - r * 0.98, 322), tip], pen, 1.1, 75, 0.6, 1) + pline([(c2[0] + r * 0.98, 322), tip], pen, 1.1, 76, 0.6, 1))
    out.append(f'<path d="{smooth_open(ell_pts(tip[0], tip[1], 150, 150, 230, 310, 14))}" fill="none" stroke="{pen}" stroke-width="1" opacity="0.5"/>')
    for lbl, (x, y) in (("A", (c1[0] - 8, c1[1] + 18)), ("B", (c2[0] + 6, c2[1] + 18)), ("C", (tip[0] + 10, tip[1] + 10))):
        out.append(f'<text x="{x}" y="{y}" {SERIF_IT} font-size="18" fill="{pen}" opacity="0.85">{lbl}</text>')
    # the heart itself in red gouache (spilling a little past its lines)
    hp = []
    for i in range(60):
        t = i / 60 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        hp.append((300 + x * 7.6, 350 + y * 7.6))
    out.append(cast(D, 312, 440, 110, 14, "#5A2A1A", 0.25, 77))
    out.append(painted(D, hp, ("#F2808A", "#D02A3A", "#7A0E1A"), 78, sdir=(0.5, 0.8), sk=0.16, angle=-55, n=90, slen=(10, 30), sw=(1.4, 3.4), inkw=1.6, hi=0.45, hik=0.08))
    # the geometer's construction drawn over the paint: circles, tangents, the arc that finds the point
    for c in (c1, c2):
        out.append(f'<circle cx="{c[0]}" cy="{c[1]}" r="{r}" fill="none" stroke="#FFFFFF" stroke-width="1.3" opacity="0.55" stroke-dasharray="6 4"/>')
    out.append(pline([(c1[0] - r * 0.98, 322), tip], "#FFFFFF", 1.2, 113, 0.5, 1) + pline([(c2[0] + r * 0.98, 322), tip], "#FFFFFF", 1.2, 114, 0.5, 1))
    out.append(f'<circle cx="{tip[0]}" cy="{tip[1]}" r="3" fill="{pen}"/>')
    # blossoms bursting out of the top of the heart and over its edge
    rnd = random.Random(79)
    for k, (x, y, r, pal) in enumerate(((246, 262, 26, ("#FFD0D8", "#F07A90", "#A83050")), (318, 248, 30, ("#FFF4E8", "#F6DCC8", "#C89A80")), (370, 276, 22, ("#FFD0D8", "#F07A90", "#A83050")),
                                         (210, 300, 18, ("#FFE4B0", "#F2B060", "#B0702A")), (284, 220, 16, ("#FFE4B0", "#F2B060", "#B0702A")), (396, 312, 16, ("#FFF4E8", "#F6DCC8", "#C89A80")))):
        for j in range(2):
            a = rnd.uniform(-160, -20)
            out.append(leaf_simple(D, x, y, r * 1.2, r * 0.42, a, ("#B8D88A", "#5E8A3A", "#2E4A1E"), 80 + k * 3 + j, inkw=0.9))
    for k, (x, y, r, pal) in enumerate(((246, 262, 26, ("#FFD0D8", "#F07A90", "#A83050")), (318, 248, 30, ("#FFF4E8", "#F6DCC8", "#C89A80")), (370, 276, 22, ("#FFD0D8", "#F07A90", "#A83050")),
                                         (210, 300, 18, ("#FFE4B0", "#F2B060", "#B0702A")), (284, 220, 16, ("#FFE4B0", "#F2B060", "#B0702A")), (396, 312, 16, ("#FFF4E8", "#F6DCC8", "#C89A80")))):
        out.append(rose_bloom(D, x, y, r, 90 + k, pal=pal, rot_=k * 40))
    for k in range(18):
        x, y = rnd.uniform(200, 410), rnd.uniform(210, 330)
        out.append(forget_me_not(x, y, rnd.uniform(4, 6)))
    for k in range(6):
        x, y = rnd.uniform(170, 440), rnd.uniform(150, 230)
        out.append(painted(D, rot(blob_pts(x, y, 6, 3.4, 100 + k, 0.2, 8), x, y, rnd.uniform(0, 180)), ("#FFD0D8", "#F07A90", "#A83050"), 100 + k, sk=0.2, n=2, inkw=0.6, hi=0.4))
    # the brass dividers lying across the page, and a pencil
    dv = (470, 470)
    for a, L in ((-112, 150), (-128, 152)):
        e = (dv[0] + math.cos(math.radians(a)) * L, dv[1] + math.sin(math.radians(a)) * L)
        out.append(taper([dv, e], 7, 2, "#B8862A"))
        out.append(taper([(dv[0] + math.cos(math.radians(a)) * L * 0.85, dv[1] + math.sin(math.radians(a)) * L * 0.85), e], 2.4, 0.6, "#4A4A52"))
    out.append(painted(D, blob_pts(dv[0], dv[1], 11, 11, 110, 0.02, 14), BRASS, 111, sk=0.2, n=4, inkw=1.2, hi=0.5))
    out.append(taper([(dv[0] + 4, dv[1] + 8), (dv[0] + 12, dv[1] + 30)], 6, 5, "#B8862A"))
    pc = [(96, 520), (250, 470)]
    out.append(taper(pc, 9, 9, "#E8B830"))
    out.append(taper([(250, 470), (268, 464)], 9, 1, "#E8D0A8") + taper([(262, 466), (268, 464)], 2.5, 0.5, "#2A2A2A"))
    out.append(taper([(90, 522), (100, 519)], 9, 9, "#D8909A"))
    # lettering
    out.append(lines(D, 300, 98, 46, ["The heart has its reasons,", "which reason does not know."], SERIF_IT, 38, "#7A1420", max_w=460))
    out.append(byline(538, "BLAISE PASCAL · 1623–1662", "#3A3A4A", size=17, ls=4, max_w=330, x=340))
    return finish_w(D, out, 112)


# ================================================================ 27. heaven is under our feet — a still pond mirroring the sky
@design("heaven-under-our-feet")
def heaven_under_feet():
    D = Doc2("ww-hf")
    HZ = 300
    out = [sky(D, [(0, "#6AA0D0"), (0.6, "#B8D4E8"), (1, "#F2E8D8")], 3, HZ, ["#FFFFFF", "#9AC0E0", "#D8E8F2"], 40)]
    clouds = [(140, 120, 150), (410, 90, 130), (330, 190, 110), (90, 220, 80), (520, 200, 90)]
    for k, (x, y, w_) in enumerate(clouds):
        out.append(puff_cloud(D, x, y, w_, 10 + k, pal=("#FFFFFF", "#F6F4EE", "#C8CCD8"), rows=2))
    # far shore woods in autumn colour, a few white pines
    sh = ridge([(-20, 268), (100, 252), (220, 262), (340, 246), (460, 258), (620, 250)], 4, 8)
    pals = [("#F2B060", "#D8782A", "#8A3E12"), ("#F8D070", "#E0A030", "#9A6A10"), ("#E87A5A", "#B8402A", "#6A1A0E"), ("#A8B860", "#6A7A3A", "#3A4A1E")]
    trees = []
    for k in range(34):
        x = -10 + k * 19 + random.Random(k).uniform(-6, 6)
        y = 272 + random.Random(k + 50).uniform(-4, 6)
        rx = random.Random(k + 9).uniform(14, 22)
        trees.append(dab_crown(D, x, y - rx * 0.8, rx, rx * 1.1, [pals[k % 4], pals[(k + 1) % 4]], 20 + k, n=40, size=(3, 6), light=(-0.6, -0.7), inkw=0))
    for k, x in enumerate((120, 380, 520)):
        trees.append(cypress(D, x, 284, 70, 60 + k, pal=("#5A7A5A", "#2E4A3A", "#142A20"), light=-1, w=18))
    out.append("".join(trees))
    out.append(f'<path d="M -10 {HZ - 12} L 610 {HZ - 12} L 610 {HZ + 2} L -10 {HZ + 2} Z" fill="#5A4A2A" opacity="0.6"/>')
    # the pond: the whole sky and shore again, mirrored and a touch deeper
    mir = [f'<g transform="translate(0 {2 * HZ}) scale(1 -1)">']
    mir.append(f'<rect x="-10" y="-10" width="620" height="{HZ + 10}" fill="{D.lin([(0, "#4A80B0"), (0.6, "#9AC0DA"), (1, "#D8E2E0")])}"/>')
    for k, (x, y, w_) in enumerate(clouds):
        mir.append(puff_cloud(D, x, y, w_, 10 + k, pal=("#F2F6FA", "#E2E8EE", "#A8B4C4"), rows=2))
    mir.append("".join(trees))
    mir.append("</g>")
    out.append("".join(mir))
    out.append(f'<rect x="-10" y="{HZ}" width="620" height="{620 - HZ}" fill="{D.lin([(0, "#1E3A50", 0.1), (1, "#0E2234", 0.35)])}"/>')
    rnd = random.Random(7)
    for _ in range(70):
        y = HZ + 6 + rnd.random() * 290
        x = rnd.uniform(-10, 610)
        L_ = 20 + (y - HZ) * 0.3
        out.append(f'<path d="M {x:.1f} {y:.1f} l {L_:.1f} 0" stroke="#FFFFFF" stroke-width="1.2" opacity="{rnd.uniform(0.15, 0.4):.2f}"/>')
    # a canoe resting on the water, its reflection; water-lily pads in the near corner; a loon
    cx_, cy_ = 420, 392
    can = [(cx_ - 80, cy_ - 6), (cx_ - 40, cy_ + 4), (cx_ + 40, cy_ + 4), (cx_ + 82, cy_ - 8), (cx_ + 60, cy_ + 10), (cx_ - 60, cy_ + 12)]
    out.append(painted(D, can, ("#E8905A", "#B8502A", "#6A2410"), 30, sdir=(0.3, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.45))
    out.append(f'<path d="{smooth_closed([(x, 2 * cy_ + 20 - y) for x, y in can])}" fill="#B8502A" opacity="0.35"/>')
    out.append(taper([(cx_ - 20, cy_ - 2), (cx_ + 60, cy_ - 20)], 3, 2, "#6A4A2A"))
    out.append(f'<path d="{blob(cx_ + 64, cy_ - 22, 8, 3, 31, 0.1, 8, -14)}" fill="#6A4A2A"/>')
    for k in range(3):
        out.append(f'<ellipse cx="{cx_}" cy="{cy_ + 14}" rx="{96 + k * 26}" ry="{6 + k * 3}" fill="none" stroke="#FFFFFF" stroke-width="1" opacity="{0.45 - k * 0.12:.2f}"/>')
    lx, ly = 150, 356
    out.append(f'<path d="{blob(lx, ly, 18, 6, 32, 0.1, 10)}" fill="#1A1A20"/>')
    out.append(f'<path d="{blob(lx + 16, ly - 8, 6, 5, 33, 0.1, 8)}" fill="#1A1A20"/>' + f'<path d="M {lx + 21} {ly - 8} l 8 1" stroke="#1A1A20" stroke-width="2.4"/>')
    for k in range(10):
        out.append(f'<circle cx="{lx - 12 + k * 2.6:.1f}" cy="{ly - 1 + (k % 2) * 2:.1f}" r="1" fill="#FFFFFF"/>')
    for k in range(3):
        out.append(f'<ellipse cx="{lx}" cy="{ly + 6}" rx="{28 + k * 16}" ry="{3 + k * 2}" fill="none" stroke="#FFFFFF" stroke-width="1" opacity="{0.4 - k * 0.1:.2f}"/>')
    for k, (x, y, r) in enumerate(((54, 560, 30), (110, 586, 24), (20, 512, 20), (520, 572, 28), (566, 528, 18))):
        pad = blob_pts(x, y, r, r * 0.4, 40 + k, 0.05, 16)
        out.append(painted(D, pad, ("#9AC870", "#4E8A3A", "#22501E"), 41 + k, sk=0.2, n=6, inkw=1.1, hi=0.4))
        out.append(pline([(x, y), (x + r * 0.9, y - r * 0.2)], "#22501E", 1.6, k, 0.8, 1))
    from japan_painted import water_lily
    out.append(water_lily(D, 66, 552, 18, 50))
    out.append(water_lily(D, 530, 562, 14, 51))
    # lettering: over the sky, and the byline written on the sky's reflection
    out.append(lines(D, 300, 88, 48, ["Heaven is under our feet", "as well as over our heads."], SERIF_IT, 42, "#1E3A5E", max_w=470, shadow="#FFFFFF", soff=(1.2, 1.6)))
    out.append(f'<path d="{blob(300, 527, 210, 18, 60, 0.08, 18)}" fill="#F2F6FA" opacity="0.55"/>')
    out.append(byline(533, "HENRY DAVID THOREAU · WALDEN", "#1E3A5E", size=17, ls=3, max_w=380))
    return finish_w(D, out, 61)


# ================================================================ 28. no man is free — at the helm, the storm breaking
def helm(D, cx, cy, R, seed, spokes=8, rot_=8):
    """A ship's wheel: rim of joined felloes, turned spokes with handles, a brass hub."""
    out = [cast(D, cx + 10, cy + 14, R * 1.15, R * 1.1, "#0A0A10", 0.35, seed)]
    for k in range(spokes):
        a = math.radians(rot_ + k * 360 / spokes)
        x0, y0 = cx + math.cos(a) * R * 0.18, cy + math.sin(a) * R * 0.18
        x1, y1 = cx + math.cos(a) * R * 1.32, cy + math.sin(a) * R * 1.32
        # turned spoke: thin at hub, bead, handle
        out.append(taper([(x0, y0), (cx + math.cos(a) * R * 0.6, cy + math.sin(a) * R * 0.6), (cx + math.cos(a) * R, cy + math.sin(a) * R)], R * 0.07, R * 0.05, "#7A4A28"))
        hp = [(cx + math.cos(a) * R * (1.05 + t * 0.27), cy + math.sin(a) * R * (1.05 + t * 0.27)) for t in (0, 0.3, 0.6, 1)]
        out.append(taper(hp, R * 0.06, R * 0.075, "#8A5A30"))
        out.append(f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="{R * 0.045:.1f}" fill="#8A5A30"/>')
        out.append(taper([(cx + math.cos(a) * R * 0.35, cy + math.sin(a) * R * 0.35), (cx + math.cos(a) * R * 0.9, cy + math.sin(a) * R * 0.9)], R * 0.02, R * 0.015, "#E8B888", 0.6))
    rim_o, rim_i = R * 1.0, R * 0.86
    d = smooth_closed(ell_pts(cx, cy, rim_o, rim_o, 0, 360, 48)[:-1]) + " " + smooth_closed(ell_pts(cx, cy, rim_i, rim_i, 360, 0, 48)[:-1])
    out.append(f'<path d="{d}" fill="#8A5230" fill-rule="evenodd"/>')
    out.append(f'<path d="{d}" fill-rule="evenodd" fill="{D.lin([(0, "#E8A878", 0.6), (0.5, "#8A5230", 0), (1, "#2A1408", 0.6)], 0, 0, 1, 1)}"/>')
    out.append(strokes(D.nid(), d, (cx - R, cy - R, cx + R, cy + R), ["#B87A48", "#5A3018"], seed, n=60, angle=45, length=(10, 30), width=(1, 2.4), opacity=(0.2, 0.4)))
    for k in range(spokes):
        a = math.radians(rot_ + 22.5 + k * 360 / spokes)
        out.append(pline([(cx + math.cos(a) * rim_i, cy + math.sin(a) * rim_i), (cx + math.cos(a) * rim_o, cy + math.sin(a) * rim_o)], "#2A1408", 1.6, k, 0.7, 1))
    out.append(ink(d, "#2A1408", 1.4, seed, 1, 0.6))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R * 0.93:.1f}" fill="none" stroke="#C89A3A" stroke-width="{R * 0.03:.1f}"/>')
    out.append(painted(D, blob_pts(cx, cy, R * 0.22, R * 0.22, seed + 1, 0.01, 20), BRASS, seed + 2, sdir=(0.6, 0.8), sk=0.2, n=8, inkw=1.4, hi=0.6))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R * 0.1:.1f}" fill="#7A5418"/><circle cx="{cx - R * 0.04:.1f}" cy="{cy - R * 0.04:.1f}" r="{R * 0.04:.1f}" fill="#FFF0B0"/>')
    return "".join(out)


@design("master-of-himself")
def master_of_himself():
    D = Doc2("ww-mh")
    HZ = 330
    out = [sky(D, [(0, "#3A4A5E"), (0.4, "#6A7A8A"), (0.75, "#E8C890"), (1, "#F8E0A8")], 3, HZ, ["#8A9AAA", "#4A5A6A", "#E8D0A0"], 60)]
    # the storm clouds breaking, sun rays through the gap
    out.append(soft_glow(D, 400, 250, 200, "#FFF0C0", 0.8))
    for k in range(7):
        a = math.radians(70 + k * 9)
        out.append(f'<path d="{pd([(400, 230), (400 + math.cos(a) * 500 - 20, 230 + math.sin(a) * 500), (400 + math.cos(a) * 500 + 20, 230 + math.sin(a) * 500)])}" fill="#FFF6D8" opacity="0.12"/>')
    out.append(f'<rect width="600" height="230" fill="{D.lin([(0, "#161C28", 0.9), (0.7, "#1E2634", 0.5), (1, "#1E2634", 0)])}"/>')
    for k, (x, y, w_, pal) in enumerate(((110, 286, 240, ("#8A96A8", "#4E5A6E", "#262E3E")), (500, 276, 220, ("#8A96A8", "#4E5A6E", "#262E3E")),
                                         (330, 312, 110, ("#FFE8C0", "#E0B888", "#9A7A5A")))):
        out.append(puff_cloud(D, x, y, w_, 10 + k, pal=pal, rows=3))
    # the sea, choppy, with a glittering path under the light
    out.append(f'<path d="M -10 {HZ} L 610 {HZ} L 610 610 L -10 610 Z" fill="{D.lin([(0, "#7A9AA8"), (0.4, "#3E6070"), (1, "#1A3040")])}"/>')
    out.append(wave_lines(20, (0, HZ + 4, 600, 600), ["#A8C8D0", "#1A3040", "#E8F0F0"], n=110, L=(16, 50), w=2.2, amp=4))
    rnd = random.Random(21)
    for _ in range(50):
        y = HZ + 4 + rnd.random() ** 1.3 * 120
        x = 400 + rnd.gauss(0, 20 + (y - HZ) * 0.5)
        out.append(f'<path d="M {x - 6:.1f} {y:.1f} l 12 0" stroke="#FFF2C8" stroke-width="2" stroke-linecap="round" opacity="0.8"/>')
    out.append(f'<path d="{pd([(140, HZ), (150, HZ - 8), (160, HZ)])}" fill="#2A3040"/>')
    for x, y in ((220, 240), (240, 230), (520, 260)):
        out.append(bird_v(x, y, 7, "#2A3040", 0.8))
    # the deck rail across the bottom, the coil of rope, and the great wheel
    deck = [(-20, 520), (620, 506), (620, 620), (-20, 620)]
    out.append(painted(D, deck, ("#B8865A", "#7A4E2E", "#3A2210"), 22, sdir=(0, 1), sk=0.05, angle=-2, n=60, inkw=1.4, hi=0.25))
    for k in range(5):
        out.append(pline([(-20, 540 + k * 18), (620, 526 + k * 18)], "#3A2210", 1.4, k, 0.5, 1))
    rope = []
    for k in range(5):
        rope.append(f'<ellipse cx="96" cy="{548 - k * 4}" rx="{60 - k * 9}" ry="{18 - k * 2.5}" fill="none" stroke="#D8B878" stroke-width="7"/>')
        rope.append(f'<ellipse cx="96" cy="{548 - k * 4}" rx="{60 - k * 9}" ry="{18 - k * 2.5}" fill="none" stroke="#8A6A38" stroke-width="7" stroke-dasharray="3 5" opacity="0.6"/>')
    out.append("".join(rope))
    out.append(taper([(440, 524), (444, 400)], 30, 26, "#5A3420"))
    out.append(taper([(430, 524), (434, 400)], 8, 6, "#9A6A44", 0.6))
    out.append(helm(D, 444, 398, 112, 23, rot_=12))
    # lettering, top over the stormy sky
    out.append(lines(D, 300, 92, 48, ["No man is free who is", "not master of himself."], SERIF_IT, 44, "#FFF6E2", max_w=470, shadow="#0A0E16"))
    out.append(byline(176, "EPICTETUS · c. 50–135", "#F2DCA8", size=18, ls=5, max_w=300))
    return finish_w(D, out, 24, "#000000", 0.5)


# ================================================================ 29. philosophy begins in wonder — the owl of Athena at dusk
def little_owl(D, x, y, s, seed):
    """Athene noctua perched, face turned up toward the sky: speckled brown, white brows, yellow eyes."""
    def L(pts):
        return T(pts, x, y, s)
    pal = ("#C8A07A", "#8A6440", "#4A3420")
    out = []
    body = L([(-30, 0), (-34, -40), (-24, -70), (0, -80), (24, -70), (34, -40), (30, 0), (14, 14), (-14, 14)])
    out.append(painted(D, body, pal, seed, sdir=(0.6, 0.6), sk=0.18, angle=-90, n=40, slen=(6, 14), sw=(1, 2.4), inkw=1.6, hi=0.4))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    rnd = random.Random(seed)
    sp = []
    for _ in range(70):
        px, py = L([(rnd.uniform(-30, 30), rnd.uniform(-76, 10))])[0]
        sp.append(f'<path d="{blob(px, py, 2.6 * s, 1.8 * s, rnd.randint(1, 999), 0.2, 8)}" fill="#F6ECD8" opacity="0.85"/>')
    belly = L([(-16, -30), (16, -30), (20, 0), (0, 12), (-20, 0)])
    sp.append(f'<path d="{smooth_closed(belly)}" fill="#E8D8B8" opacity="0.6"/>')
    for j in range(5):
        sp.append(pline(L([(-14 + j * 6, -24), (-12 + j * 6, 4)]), "#8A6440", 2.4, j, 0.55, 1))
    out.append(f'<g {cid}>{"".join(sp)}</g>')
    # wing edges
    for sg in (-1, 1):
        w_ = L([(sg * 22, -56), (sg * 34, -30), (sg * 30, 6), (sg * 18, -20)])
        out.append(painted(D, w_, ("#B8906A", "#7A5432", "#3A2614"), seed + 3 + sg, sk=0.15, n=10, inkw=1.2, hi=0.3))
    # head tilted up: facial disc, brows, eyes
    head = L([(-26, -66), (-24, -96), (0, -110), (24, -96), (26, -66), (0, -58)])
    out.append(painted(D, head, pal, seed + 5, sdir=(0.6, 0.6), sk=0.15, angle=-60, n=20, inkw=1.5, hi=0.4))
    for sg in (-1, 1):
        ex, ey = L([(sg * 11, -88)])[0]
        out.append(f'<path d="{blob(ex, ey + 2 * s, 11 * s, 8 * s, seed + 7 + sg, 0.1, 12)}" fill="#F6EEDC"/>')
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{7 * s:.1f}" fill="#F6C83A"/>')
        out.append(f'<circle cx="{ex + 0.5 * s:.1f}" cy="{ey - 1.4 * s:.1f}" r="{3.8 * s:.1f}" fill="#120A04"/>')
        out.append(f'<circle cx="{ex - 1.6 * s:.1f}" cy="{ey - 3 * s:.1f}" r="{1.4 * s:.1f}" fill="#FFFFFF"/>')
        out.append(taper(L([(sg * 4, -96), (sg * 12, -100), (sg * 22, -96)]), 3 * s, 1, "#FFFBEE", 0.9))
    out.append(f'<path d="{pd(L([(-3, -84), (3, -84), (0, -76)]))}" fill="#C8B070"/>')
    # feet on the branch
    for dx in (-10, 8):
        for t in (-4, 0, 4):
            out.append(pline(L([(dx, 10), (dx + t, 18)]), "#6A5A3A", 1.6 * s, seed + dx, 0.9, 1))
    for k in range(20):
        px, py = L([(rnd.uniform(-22, 22), rnd.uniform(-104, -70))])[0]
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{1 * s:.1f}" fill="#F6ECD8" opacity="0.8"/>')
    return "".join(out)


@design("philosophy-begins-in-wonder")
def begins_in_wonder():
    D = Doc2("ww-bw")
    out = [sky(D, [(0, "#1E2E5A"), (0.4, "#4A5A8A"), (0.7, "#C8909A"), (0.85, "#F2C090")], 3, 600, ["#3A4A7A", "#A88AA8", "#F2B890"], 70)]
    out.append(stars_field(4, (0, 0, 600, 300), 80))
    for x, y, r in ((120, 150, 7), (170, 96, 5), (90, 230, 4), (250, 60, 4), (60, 90, 5)):
        out.append(sparkle(x, y, r, "#FFF6DA", 1))
    # a slim crescent moon, upper left (the owl looks up at it)
    mx, my = 140, 170
    out.append(soft_glow(D, mx, my, 90, "#FFF2D0", 0.5))
    cres = f"M {mx - 4} {my - 34} A 34 34 0 1 0 {mx - 4} {my + 34} A 26 30 0 1 1 {mx - 4} {my - 34} Z"
    out.append(f'<path d="{cres}" fill="#FFF6DE"/>')
    # the Acropolis far below on its hill, the Parthenon catching the last light
    hl = ridge([(-20, 470), (120, 452), (220, 430), (300, 422), (380, 432), (480, 452), (620, 464)], 5, 6)
    out.append(hill(D, hl, 620, ("#7A6A8A", "#4E425E", "#2A2238"), 6, inkw=0, n=40, lit="#F2B890"))
    px, pb = 300, 424
    out.append(f'<path d="{pd([(px - 52, pb), (px + 52, pb), (px + 52, pb - 4), (px - 52, pb - 4)])}" fill="#E8C0A0"/>')
    for k in range(8):
        x = px - 46 + k * 13
        out.append(f'<rect x="{x}" y="{pb - 26}" width="5" height="22" fill="#F2D0B0"/>')
    out.append(f'<path d="{pd([(px - 54, pb - 26), (px + 54, pb - 26), (px + 54, pb - 32), (px - 54, pb - 32)])}" fill="#F2D0B0"/>')
    out.append(f'<path d="{pd([(px - 54, pb - 32), (px, pb - 44), (px + 54, pb - 32)])}" fill="#E8C0A0"/>')
    out.append(soft_glow(D, px, pb - 20, 70, "#FFD8A8", 0.3))
    l2 = ridge([(-20, 500), (160, 488), (320, 500), (480, 484), (620, 494)], 7, 6)
    out.append(hill(D, l2, 620, ("#4A3E58", "#2E2638", "#18121E"), 8, inkw=0, n=40))
    for k in range(10):
        x = 20 + k * 62
        out.append(cypress(D, x, 506 - (k % 3) * 4, 40 + (k % 4) * 8, 9 + k, pal=("#3A3448", "#22202E", "#12101A"), light=1, w=11))
    # the olive branch crossing from the right, silver leaves, a few olives; the owl upon it
    br = [(640, 330), (560, 340), (470, 356), (380, 362), (300, 352)]
    out.append(olive_branch(D, br, 10, olives=((0.3, 1, ("#5A5A7A", "#2A2A44", "#12121E")), (0.55, -1, ("#5A5A7A", "#2A2A44", "#12121E")), (0.8, 1, ("#5A5A7A", "#2A2A44", "#12121E"))),
                            w=9, leaves=22, pal=("#D8E0D0", "#8A9A80", "#3E4A3A"), L=(32, 46)))
    out.append(little_owl(D, 430, 344, 1.25, 20))
    # lettering
    out.append(tx(363, 99, "Philosophy", SERIF_IT, 64, "#0A0618", max_w=400, op=0.6))
    out.append(tx(360, 96, "Philosophy", SERIF_IT, 64, "#FFF4E2", max_w=400))
    out.append(tx(362, 152, "begins in wonder.", SERIF_IT, 44, "#0A0618", max_w=400, op=0.6))
    out.append(tx(360, 150, "begins in wonder.", SERIF_IT, 44, "#FFE2C0", max_w=400))
    out.append(byline(536, "PLATO · c. 428–348 BC", "#F2D8C0", size=17, ls=5, max_w=300))
    return finish_w(D, out, 40, "#000000", 0.5)


# ================================================================ 30. per aspera ad astra — a night climb under the Milky Way
def sextant(D, cx, cy, s, seed, ang=-20):
    """A brass sextant lying on its side: the graduated arc, the triangular frame, index arm, mirrors and eyepiece."""
    def L(pts):
        return T(pts, cx, cy, s, False, ang)
    out = [cast(D, cx + 10, cy + 40 * s, 110 * s, 22 * s, "#000", 0.45, seed)]
    apex = (0, -90)
    arc = [(math.cos(math.radians(a)) * 100, -90 + math.sin(math.radians(a)) * 100) for a in range(60, 121, 4)]
    frame = [apex, arc[0], arc[-1]]
    gl = D.lin([(0, "#FFF0B0"), (0.5, "#D8A845"), (1, "#7A5418")])
    for a, b in ((apex, arc[0]), (apex, arc[-1]), (apex, (0, 6))):
        out.append(taper(L([a, b]), 7 * s, 6 * s, "#B8862A"))
        out.append(taper(L([a, b]), 2 * s, 1.6 * s, "#FFE8A0", 0.7))
    out.append(taper(L(arc), 12 * s, 12 * s, "#C89A3A"))
    out.append(taper(L(arc), 5 * s, 5 * s, "#F2E2B8"))
    for k, (x, y) in enumerate(arc):
        a, b = L([(x, y - 2)])[0], L([(x * 0.94, -90 + (y + 90) * 0.94 - 2)])[0]
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#3A2408" stroke-width="1"/>')
    # index arm swung across, mirrors, eyepiece telescope
    out.append(taper(L([apex, (30, 8)]), 6 * s, 4 * s, "#8A6020"))
    out.append(painted(D, L([(-10, -80), (10, -80), (10, -64), (-10, -64)]), ("#D8E8F0", "#8AA8B8", "#3A5A6A"), seed + 1, sk=0.2, n=3, inkw=1, hi=0.6))
    out.append(painted(D, L([(-32, -40), (-14, -40), (-14, -26), (-32, -26)]), ("#D8E8F0", "#8AA8B8", "#3A5A6A"), seed + 2, sk=0.2, n=3, inkw=1, hi=0.6))
    out.append(taper(L([(-50, -46), (20, -50)]), 9 * s, 7 * s, "#C89A3A"))
    out.append(taper(L([(-50, -46), (20, -50)]), 3 * s, 2 * s, "#FFF0B0", 0.6))
    out.append(f'<circle cx="{L([apex])[0][0]:.1f}" cy="{L([apex])[0][1]:.1f}" r="{6 * s:.1f}" fill="#E8C060"/>')
    return "".join(out)


@design("per-aspera-ad-astra")
def per_aspera():
    D = Doc2("ww-pa")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#070A1E"), (0.5, "#142048"), (0.8, "#2A3A6A"), (1, "#3A4A78")])}"/>']
    # the Milky Way: a diagonal band of glow and dust
    band = [(-40, 380), (140, 250), (330, 140), (520, 40), (660, -20)]
    for w_, c, op in ((180, "#6A6AA8", 0.12), (110, "#B8B8E0", 0.12), (50, "#FFFFFF", 0.12)):
        out.append(taper(catmull(band, 6), w_, w_, c, op))
    rnd = random.Random(3)
    for _ in range(260):
        t = rnd.random()
        i = min(len(band) - 2, int(t * (len(band) - 1)))
        u = t * (len(band) - 1) - i
        x = band[i][0] + (band[i + 1][0] - band[i][0]) * u + rnd.gauss(0, 40)
        y = band[i][1] + (band[i + 1][1] - band[i][1]) * u + rnd.gauss(0, 40)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.4, 1.3):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.3, 0.9):.2f}"/>')
    for k in range(6):
        x, y = rnd.uniform(0, 600), rnd.uniform(0, 400)
        out.append(f'<path d="{blob(x, y, 30, 8, 10 + k, 0.4, 12, -35)}" fill="#1A1430" opacity="0.4"/>')
    out.append(stars_field(4, (0, 0, 600, 420), 120))
    for x, y, r in ((470, 110, 9), (110, 90, 7), (520, 230, 6), (80, 300, 6), (300, 64, 5), (400, 300, 6)):
        out.append(soft_glow(D, x, y, r * 3, "#DCE6FF", 0.5) + sparkle(x, y, r, "#FFFFFF", 1))
    # a shooting star
    out.append(taper([(560, 160), (490, 196), (420, 226)], 3, 0.4, "#FFFFFF", 0.9))
    # the mountain: steep rocky ridge rising from lower left to a summit at right, with a winding trail
    mt = [(-20, 600), (-20, 520), (80, 488), (180, 452), (260, 410), (330, 360), (380, 318), (420, 292), (446, 286), (470, 300), (520, 330), (620, 360), (620, 600)]
    out.append(painted(D, mt, ("#5A6A9A", "#2E3A60", "#121A30"), 5, sdir=(-0.8, 0.4), sk=0.12, angle=-60, n=120, slen=(14, 40), sw=(1.4, 3.6), inkw=1.6, inkc="#05070F", hi=0.25))
    out.append(ink(smooth_open(mt[2:12]), "#A8B8E8", 1.6, 6, 1, 0.45))
    cid = D.clip(f'<path d="{smooth_closed(mt)}"/>')
    rk = []
    for _ in range(40):
        x, y = rnd.uniform(0, 600), rnd.uniform(320, 600)
        rk.append(pline([(x, y), (x + rnd.uniform(10, 30), y - rnd.uniform(4, 16)), (x + rnd.uniform(20, 50), y - rnd.uniform(0, 8))], "#0A0E1E", 1.6, rnd.randint(1, 99), 0.55, 1))
    out.append(f'<g {cid}>{"".join(rk)}</g>')
    trail = [(120, 560), (200, 520), (170, 488), (250, 456), (232, 428), (300, 400), (290, 372), (350, 344), (372, 318), (420, 296), (446, 288)]
    out.append(pline(catmull(trail, 6), "#8A9AC8", 1.6, 7, 0.6, 1))
    # a summit cairn with a little flag
    out.append(painted(D, [(436, 288), (456, 288), (452, 276), (440, 276)], ("#8A96B8", "#4A5678", "#1E2640"), 8, sk=0.2, n=3, inkw=1, hi=0.4))
    out.append(pline([(446, 276), (446, 248)], "#C8C8D8", 1.4, 9, 1, 1))
    out.append(f'<path d="{pd([(446, 248), (464, 253), (446, 258)])}" fill="#E8604A"/>')
    # the climber with a lantern partway up
    lx, ly = 300, 398
    out.append(soft_glow(D, lx + 8, ly - 18, 40, "#FFC860", 0.7))
    out.append(f'<path d="{pd([(lx - 5, ly), (lx + 5, ly), (lx + 6, ly - 18), (lx, ly - 24), (lx - 6, ly - 18)])}" fill="#141828"/>')
    out.append(f'<circle cx="{lx}" cy="{ly - 28}" r="4.5" fill="#141828"/>')
    out.append(f'<path d="{pd([(lx - 8, ly - 22), (lx - 2, ly - 22), (lx - 2, ly - 8), (lx - 9, ly - 8)])}" fill="#2A2A40"/>')
    out.append(pline([(lx + 5, ly - 18), (lx + 9, ly - 12)], "#141828", 1.8, 10, 1, 1))
    out.append(f'<rect x="{lx + 6}" y="{ly - 12}" width="6" height="8" fill="#FFE08A"/>')
    out.append(pline([(lx - 8, ly), (lx - 12, ly - 30)], "#3A3020", 1.4, 11, 1, 1))
    # the brass sextant resting on a rock in the foreground
    out.append(painted(D, [(-20, 600), (-20, 530), (60, 512), (170, 520), (230, 560), (240, 610)], ("#4A5478", "#262E4A", "#0E1224"), 12, sdir=(-0.6, 0.6), sk=0.15, angle=-20, n=30, inkw=1.6, hi=0.3))
    out.append(soft_glow(D, 110, 528, 80, "#FFE8A0", 0.18))
    out.append(sextant(D, 110, 568, 0.82, 13, ang=-16))
    # lettering
    out.append(gilt(D, 300, 132, "Per aspera", SERIF_IT, 78, max_w=440, seed=20, deboss="#03040C", pal="pale"))
    out.append(gilt(D, 300, 210, "ad astra", SERIF_IT, 78, max_w=440, seed=21, deboss="#03040C", pal="pale"))
    out.append(ruled(300, 250, "THROUGH HARDSHIPS TO THE STARS", "#DCE4FF", font=CINZEL, size=16, ls=3, line_w=24, gap=10, max_w=420))
    out.append(byline(538, "A LATIN MOTTO", "#C8D0F0", size=16, ls=6, max_w=300, x=400))
    return finish_w(D, out, 22, "#000000", 0.5)


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())
    if not only:
        from common import ROOT
        for f in (ROOT / COL).glob("*.svg"):
            if f.stem not in DESIGNS:
                f.unlink()


if __name__ == "__main__":
    build(sys.argv[1:] or None)
