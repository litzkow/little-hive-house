"""Japan, hand-painted (gouache / storybook) edition: 30 magnets for Japanese families abroad, Japan-loving
travellers and anyone who loves Japanese everyday culture.

Same idiom as the Brasil set: warm washi-paper ground, layered washes with pooled edges, brush strokes that follow
each form, a warm brown pen line, hand-placed brush lettering, soft light and paper grain. Lettering is romaji or
English (the site fonts carry no Japanese glyphs); the only Japanese character is 山 ("mountain"), painted as
carved strokes on the red hanko seals (fuji-san, nami, the matcha scroll). Colour story: vermilion (shu), indigo (ai), matcha green,
sakura pink, sumi black and gold leaf on cream washi.

Run from tools/designs:  python3 japan_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ridge, ruled, shift, sky, soft_glow, specks, taper, catmull, steam_wisps)
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash, maple_leaf
from poster import ANTON
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines, bite_out
from brasil_painted import (Doc2, ell_pts, pd, shade_over, light_over, leaf_simple, branch, wood_planks, heart_d,
                            steam, finish_b, gingham, bird_v, stamp)
import holidays_gouache as hg
import figures

COL = "japan"
INK = "#3A2418"
SUMI_INK = "#2A2220"
FLECK = "#8A6A4A"

# (light, base, dark) gouache palettes
SHU = ("#F4876A", "#D8402A", "#8A1A12")        # vermilion
AKA = ("#F07A6A", "#C8281E", "#7A0E0E")        # lacquer red
AI = ("#6A84C0", "#27407A", "#101C40")         # indigo
MATCHA = ("#C2D884", "#7E9E3A", "#3E5A1A")
SAKURA = ("#FFE8EE", "#F6B8C8", "#CC6E8A")
GOLD = ("#FFE8A0", "#D8A848", "#8A6418")
SUMI = ("#5E5654", "#2A2420", "#100C0A")
HINOKI = ("#F4DAAE", "#DDB078", "#9A6A38")     # pale cypress wood
DARKWOOD = ("#9A6A44", "#5E3820", "#2A160A")
RICE = ("#FFFFFF", "#F7F3EA", "#B8B2A8")
NORI = ("#3E4E40", "#1C2820", "#0A100C")
TATAMI = ("#E6DAA0", "#CDB878", "#8C7C44")
PINE = ("#6E9A5A", "#2E5A3A", "#123020")
STONE = ("#C8C4BC", "#8E8A84", "#4E4A46")
CREAM = ("#FFFDF6", "#F4EAD6", "#C8B494")
WHITE = ("#FFFFFF", "#F4F0E8", "#B8B0A6")
MIKAN = ("#FFC060", "#F28A1E", "#B0500A")
WASHI = "#F4EAD6"

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


lt, dk = hg.lt, hg.dk


# ================================================================ japan toolkit
def densify(pts, step=12, closed=True):
    out = []
    m = len(pts)
    for i in range(m if closed else m - 1):
        (ax, ay), (bx, by) = pts[i], pts[(i + 1) % m]
        n = max(1, int(math.hypot(bx - ax, by - ay) / step))
        for k in range(n):
            out.append((ax + (bx - ax) * k / n, ay + (by - ay) * k / n))
    if not closed:
        out.append(pts[-1])
    return out


def round_poly(corners, r, n=5):
    """Polygon with rounded corners, as a point list (feed to smooth_closed / painted)."""
    out = []
    m = len(corners)

    def tow(a, b, d):
        L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        d = min(d, L * 0.45)
        return (a[0] + (b[0] - a[0]) * d / L, a[1] + (b[1] - a[1]) * d / L)

    for i in range(m):
        p, q, s = corners[i], corners[i - 1], corners[(i + 1) % m]
        rr = r[i] if isinstance(r, (list, tuple)) else r
        a, b = tow(p, q, rr), tow(p, s, rr)
        for k in range(n + 1):
            t = k / n
            out.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * p[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * p[1] + t * t * b[1]))
    return densify(out, 14)


def clipped(D, d, inner):
    return f'<g {D.clip(f"<path d=\"{d}\"/>")}>{"".join(inner) if isinstance(inner, list) else inner}</g>'


def tatami(D, y0, y1, seed, x0=0, x1=600, pal=TATAMI, heri=None, heri_y=None, vertical=False):
    """Woven rush mat: graded base, fine weave lines, darker rush flecks; optional cloth border (heri)."""
    rnd = random.Random(seed)
    d = pd([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    out = [f'<path d="{d}" fill="{pal[1]}"/>',
           f'<path d="{d}" fill="{D.lin([(0, pal[0], 0.5), (1, pal[2], 0.35)], 0, y0, 0, y1, "userSpaceOnUse")}"/>']
    lines = []
    step = 5.5
    if vertical:
        x = x0
        while x < x1:
            c = rnd.choice([pal[0], pal[2], lt(pal[0], 0.2)])
            lines.append(f'<path d="M {x:.1f} {y0} L {x + rnd.uniform(-1, 1):.1f} {y1}" stroke="{c}" stroke-width="{rnd.uniform(1, 2.2):.1f}" opacity="{rnd.uniform(0.25, 0.6):.2f}"/>')
            x += step * rnd.uniform(0.8, 1.2)
    else:
        y = y0
        while y < y1:
            c = rnd.choice([pal[0], pal[2], lt(pal[0], 0.2)])
            lines.append(f'<path d="M {x0} {y:.1f} L {x1} {y + rnd.uniform(-1, 1):.1f}" stroke="{c}" stroke-width="{rnd.uniform(1, 2.2) * (0.6 + 0.6 * (y - y0) / max(1, y1 - y0)):.1f}" opacity="{rnd.uniform(0.25, 0.6):.2f}"/>')
            y += step * (0.6 + 0.8 * (y - y0) / max(1, y1 - y0)) * rnd.uniform(0.8, 1.2)
    out.append(clipped(D, d, lines))
    out.append(strokes(D.nid(), d, (x0 - 40, y0, x1, y1), [pal[0], pal[2], lt(pal[1], 0.3)], seed, n=int((x1 - x0) * (y1 - y0) / 500) + 10,
                       angle=-90 if vertical else 0, length=(30, 90), width=(1, 3), opacity=(0.12, 0.3), curve=0.05))
    if heri:
        hy = heri_y if heri_y is not None else y0
        hd = pd([(x0, hy), (x1, hy), (x1, hy + 16), (x0, hy + 16)])
        out.append(f'<path d="{hd}" fill="{heri[1]}"/>')
        for k in range(int((x1 - x0) / 22) + 1):
            hx = x0 + k * 22
            out.append(f'<path d="M {hx} {hy + 8} l 6 -4 l 6 4 l -6 4 Z" fill="{heri[0]}" opacity="0.55"/>')
        out.append(f'<path d="M {x0} {hy + 1} L {x1} {hy + 1}" stroke="{heri[2]}" stroke-width="1.6" opacity="0.6"/>')
        out.append(f'<path d="M {x0} {hy + 15} L {x1} {hy + 15}" stroke="{heri[2]}" stroke-width="1.6" opacity="0.6"/>')
    return "".join(out)


def long_leaf(D, x, y, L, W, ang, pal, seed, veins=2, inkw=1.4, curl=0.06):
    """Bamboo (sasa) leaf: long lance with parallel veins, from base (x, y) toward `ang`."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    right, left = [], []
    for i in range(17):
        t = i / 16
        w = W * (math.sin(math.pi * min(1, t * 1.6)) if t < 0.31 else (1 - (t - 0.31) / 0.69) ** 0.9) * 0.5
        bend = curl * L * t * t
        px, py = x + ux * L * t + nx * bend, y + uy * L * t + ny * bend
        right.append((px + nx * w, py + ny * w))
        left.append((px - nx * w, py - ny * w))
    pts = right + left[::-1][1:-1]
    out = [painted(D, pts, pal, seed, sdir=(nx, ny), sk=0.12, angle=ang, n=int(L * W / 70) + 8, slen=(L * 0.1, L * 0.3),
                   sw=(0.8, max(1.2, W * 0.06)), inkw=inkw, inkop=0.55, hi=0.3, hik=0.08)]
    for sg in [0] + [s * k for k in range(1, veins + 1) for s in (-1, 1)]:
        off = sg * W * 0.13
        vp = [(x + ux * L * t + nx * (curl * L * t * t + off * (1 - t)), y + uy * L * t + ny * (curl * L * t * t + off * (1 - t))) for t in (0.04, 0.4, 0.75, 0.97)]
        out.append(pline(vp, lt(pal[0], 0.35) if sg == 0 else dk(pal[1], 0.15), 1.6 if sg == 0 else 1.0, seed + int(sg * 7), 0.7 if sg == 0 else 0.45, 1))
    return "".join(out)


def chopsticks(D, x0, y0, x1, y1, seed, pal=HINOKI, w=9, gap=11, tip_col=None):
    """A pair of tapered chopsticks lying side by side from (x0, y0) (thick end) to (x1, y1) (tips)."""
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    out = [taper([(x0 + nx * gap * 0.5 + 6, y0 + ny * gap * 0.5 + 9), (x1 + 6, y1 + 9)], w * 1.3, w * 0.6, "#2A1608", 0.22)]
    for k, s in enumerate((-0.5, 0.5)):
        a = (x0 + nx * gap * s, y0 + ny * gap * s)
        b = (x1 + nx * gap * s * 0.4, y1 + ny * gap * s * 0.4)
        out.append(taper([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), b], w, w * 0.42, pal[2]))
        out.append(taper([(a[0] - nx * 0.8, a[1] - ny * 0.8), b], w * 0.8, w * 0.3, pal[1]))
        out.append(taper([(a[0] - nx * w * 0.22, a[1] - ny * w * 0.22), (b[0] - nx * 1, b[1] - ny * 1)], w * 0.28, 0.6, pal[0], 0.85))
        if tip_col:
            tb = (a[0] + (b[0] - a[0]) * 0.78, a[1] + (b[1] - a[1]) * 0.78)
            out.append(taper([tb, b], w * 0.62, w * 0.36, tip_col, 1))
    return "".join(out)


def sakura_flower(D, cx, cy, r, seed, rot_=0, pal=SAKURA, inkw=0.9, center="#C84A6A", tilt=1.0):
    """Five notched cherry petals, deeper pink at the heart, a crown of stamens."""
    rnd = random.Random(seed)
    out = []
    for i in range(5):
        a = rot_ + i * 72 + rnd.uniform(-5, 5)
        L = r * rnd.uniform(0.92, 1.05)
        loc = [(0, 0), (-0.3, -0.3), (-0.44, -0.66), (-0.3, -0.96), (-0.1, -1.0), (0, -0.86), (0.1, -1.0), (0.3, -0.96), (0.44, -0.66), (0.3, -0.3)]
        pts = [(cx + (x * L) * math.cos(math.radians(a)) - (y * L) * math.sin(math.radians(a)),
                cy + ((x * L) * math.sin(math.radians(a)) + (y * L) * math.cos(math.radians(a))) * tilt) for x, y in loc]
        out.append(painted(D, pts, pal, seed + i, sdir=(0.5, 0.8), sk=0.1, angle=a - 90, n=5, slen=(r * 0.2, r * 0.5), sw=(0.6, max(1, r * 0.08)),
                           inkw=inkw, inkc="#B0587A", inkop=0.5, hi=0.4, hik=0.1))
        # petal veins
        out.append(pline([(cx, cy), (cx + math.cos(math.radians(a - 90)) * L * 0.6, cy + math.sin(math.radians(a - 90)) * L * 0.6 * tilt)], dk(pal[1], 0.1), max(0.6, r * 0.03), seed + i, 0.35, 1))
    out.append(f'<path d="{blob(cx, cy, r * 0.32, r * 0.32 * tilt, seed, 0.2, 10)}" fill="{center}" opacity="0.75"/>')
    for i in range(9):
        a = math.radians(rot_ + i * 40 + rnd.uniform(-8, 8))
        L = r * rnd.uniform(0.38, 0.52)
        ex, ey = cx + math.cos(a) * L, cy + math.sin(a) * L * tilt
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {ex:.1f} {ey:.1f}" stroke="#E8789A" stroke-width="{max(0.7, r * 0.035):.1f}" stroke-linecap="round"/>'
                   f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{max(1, r * 0.055):.1f}" fill="#F2C24A"/>')
    return "".join(out)


def sakura_petal(D, x, y, s, ang, seed, pal=SAKURA, op=0.95):
    loc = [(0, 0.5), (-0.38, 0.1), (-0.32, -0.38), (-0.1, -0.5), (0, -0.38), (0.1, -0.5), (0.32, -0.38), (0.38, 0.1)]
    pts = [(x + (px * s) * math.cos(math.radians(ang)) - (py * s) * math.sin(math.radians(ang)),
            y + (px * s) * math.sin(math.radians(ang)) + (py * s) * math.cos(math.radians(ang))) for px, py in loc]
    d = smooth_closed(pts)
    return (f'<g opacity="{op}"><path d="{d}" fill="{pal[1]}"/>'
            f'<path d="{blob(x, y + s * 0.1, s * 0.12, s * 0.22, seed, 0.1, 8, ang)}" fill="{pal[2]}" opacity="0.35"/>'
            f'<path d="{blob(x - s * 0.1, y - s * 0.15, s * 0.14, s * 0.1, seed + 1, 0.1, 8, ang)}" fill="{pal[0]}" opacity="0.7"/>'
            + ink(d, "#C0607E", max(0.6, s * 0.04), seed, 1, 0.45) + "</g>")


def ume_flower(D, cx, cy, r, seed, rot_=0, pal=("#FFFFFF", "#FBE8EC", "#D898A8"), center="#E8A040", stamen="#C8325A", inkw=0.9):
    """Plum blossom: five round petals, long stamens with gold tips."""
    rnd = random.Random(seed)
    out = []
    for i in range(5):
        a = math.radians(rot_ + i * 72)
        px, py = cx + math.cos(a) * r * 0.55, cy + math.sin(a) * r * 0.55
        out.append(painted(D, blob_pts(px, py, r * 0.5, r * 0.47, seed + i, 0.05, 12, math.degrees(a)), pal, seed + i, sdir=(0.5, 0.8), sk=0.12,
                           angle=math.degrees(a), n=4, inkw=inkw, inkc=dk(pal[2], 0.2), inkop=0.5, hi=0.4))
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.22:.1f}" fill="{center}"/>')
    for i in range(10):
        a = math.radians(rot_ + i * 36 + rnd.uniform(-6, 6))
        L = r * rnd.uniform(0.55, 0.75)
        ex, ey = cx + math.cos(a) * L, cy + math.sin(a) * L
        out.append(f'<path d="M {cx:.1f} {cy:.1f} Q {cx + math.cos(a) * L * 0.5 + 1:.1f} {cy + math.sin(a) * L * 0.5:.1f} {ex:.1f} {ey:.1f}" stroke="{stamen}" stroke-width="{max(0.7, r * 0.04):.1f}" fill="none"/>'
                   f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{max(1, r * 0.06):.1f}" fill="#F2C24A"/>')
    return "".join(out)


def bark_branch(D, pts, w0, w1, seed, pal=("#7A5A4E", "#4A3230", "#24161A"), lenticels=True):
    """Cherry / plum bark: dark tapered limb, lit upper edge, horizontal lenticel marks."""
    out = [taper(pts, w0, w1, pal[1])]
    out.append(taper([(x, y - w0 * 0.18) for x, y in pts], w0 * 0.35, w1 * 0.3, pal[0], 0.55))
    out.append(taper([(x, y + w0 * 0.24) for x, y in pts], w0 * 0.3, w1 * 0.25, pal[2], 0.5))
    if lenticels:
        rnd = random.Random(seed)
        n = len(pts)
        for i in range(1, n - 1):
            x, y = pts[i]
            w = w0 + (w1 - w0) * i / n
            if rnd.random() < 0.7:
                dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
                L = math.hypot(dx, dy) or 1
                nx, ny = -dy / L, dx / L
                c = (x + nx * w * rnd.uniform(-0.25, 0.25), y + ny * w * rnd.uniform(-0.25, 0.25))
                out.append(f'<path d="M {c[0] - nx * w * 0.2:.1f} {c[1] - ny * w * 0.2:.1f} l {nx * w * 0.4:.1f} {ny * w * 0.4:.1f}" stroke="{lt(pal[0], 0.3)}" stroke-width="{max(1, w * 0.1):.1f}" stroke-linecap="round" opacity="0.6" transform="rotate(90 {c[0]:.1f} {c[1]:.1f})"/>')
    out.append(ink(smooth_open(pts), pal[2], 1.2, seed, 1, 0.35))
    return "".join(out)


def enso(cx, cy, r, seed, col=SUMI_INK, w=22, a0=-70, sweep=320, op=0.9, paper_c=WASHI):
    """A zen brush circle: one loaded stroke that thins and goes dry at the end."""
    rnd = random.Random(seed)
    pts = []
    n = 60
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + sweep * t)
        rr = r * (1 + 0.03 * math.sin(t * 7 + seed) + 0.04 * t)
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    out = [taper(pts[:8], w * 0.5, w * 1.1, col, op)]
    out.append(taper(pts[6:], w * 1.1, w * 0.35, col, op))
    # dry-brush gaps: thin paper-coloured streaks along the stroke, more toward the end
    for k in range(9):
        off = rnd.uniform(-0.35, 0.35) * w
        s0 = rnd.randint(int(n * 0.35), int(n * 0.75))
        seg = pts[s0:]
        seg = [(x + (x - cx) / r * off, y + (y - cy) / r * off) for x, y in seg]
        out.append(taper(seg, 0.6, rnd.uniform(1.5, 3.5), paper_c, rnd.uniform(0.5, 0.9)))
    # ink pooled at the start
    out.append(f'<path d="{blob(pts[1][0], pts[1][1], w * 0.62, w * 0.55, seed, 0.15, 10)}" fill="{col}" opacity="{op}"/>')
    return "".join(out)


def jpine(D, x, base, h, seed, pal=PINE, lean=0.2, trunk=("#9A6A4A", "#5A3A26", "#2A160A"), pads=None, haze=0.0, inkw=1.0):
    """Japanese black pine: a leaning, twisting trunk carrying flat cloud-pruned needle pads."""
    rnd = random.Random(seed)
    hz = (lambda c: mix(c, "#B8C4D8", haze)) if haze else (lambda c: c)
    top = (x + lean * h, base - h)
    tp = catmull([(x, base), (x + lean * h * 0.15 + h * 0.05, base - h * 0.35), (x + lean * h * 0.7 - h * 0.05, base - h * 0.7), top], 6)
    out = [taper(tp, h * 0.09, h * 0.03, hz(trunk[1]))]
    out.append(taper([(px - h * 0.012, py) for px, py in tp], h * 0.03, h * 0.01, hz(trunk[0]), 0.6))
    pads = pads or [(0.45, -1, 0.42), (0.62, 1, 0.38), (0.8, -1, 0.3), (1.0, 0, 0.36)]
    for k, (t, side, L) in enumerate(pads):
        i = min(len(tp) - 1, int(t * (len(tp) - 1)))
        bx, by = tp[i]
        ex, ey = bx + side * L * h * 0.75, by - h * 0.05 * rnd.uniform(0.2, 1)
        if side:
            out.append(taper(catmull([(bx, by), ((bx + ex) / 2, by - h * 0.06), (ex, ey)], 4), h * 0.035, h * 0.012, hz(trunk[1])))
        pw, ph = L * h * 0.55, h * 0.1
        cx, cy = ex, ey - ph * 0.3
        d = blob(cx, cy, pw, ph, seed + k, 0.14, 18)
        out.append(f'<path d="{d}" fill="{hz(pal[2])}"/>')
        dabs = [f'<path d="{blob(cx - pw * 0.05, cy - ph * 0.25, pw * 0.85, ph * 0.62, seed + k + 40, 0.18, 14)}" fill="{hz(pal[1])}"/>']
        for j in range(int(pw * 1.6)):
            px, py = cx + rnd.uniform(-pw, pw) * 0.95, cy + rnd.uniform(-ph, ph * 0.6)
            up = (cy - py) / ph
            c = hz(pal[0]) if up > 0.3 else (hz(pal[1]) if up > -0.3 else hz(dk(pal[2], 0.2)))
            L2 = rnd.uniform(3, 7)
            a2 = rnd.uniform(-1.2, 1.2)
            dabs.append(f'<path d="M {px:.1f} {py:.1f} l {math.sin(a2) * L2:.1f} {-abs(math.cos(a2)) * L2:.1f}" stroke="{c}" stroke-width="{rnd.uniform(1.1, 2):.1f}" stroke-linecap="round" opacity="0.85"/>')
        dabs.append(f'<path d="{blob(cx - pw * 0.1, cy - ph * 0.55, pw * 0.6, ph * 0.22, seed + k + 60, 0.2, 10)}" fill="{hz(lt(pal[0], 0.2))}" opacity="0.45"/>')
        out.append(clipped(D, d, dabs))
        # needle fringe along the top edge
        for j in range(int(pw / 3)):
            px = cx - pw * 0.85 + j * 6 + rnd.uniform(-2, 2)
            py = cy - ph * math.sqrt(max(0, 1 - ((px - cx) / pw) ** 2)) + 2
            out.append(f'<path d="M {px:.1f} {py:.1f} l {rnd.uniform(-2, 2):.1f} {-rnd.uniform(2, 5):.1f}" stroke="{hz(pal[0])}" stroke-width="1.2" stroke-linecap="round" opacity="0.8"/>')
        if inkw:
            out.append(ink(d, INK, inkw, seed + k, 1, 0.3))
    return "".join(out)


def pagoda(D, cx, base, h, seed, tiers=5, body=SHU, roof=("#6A6A72", "#2E2C34", "#121018"), haze=0.0, inkw=1.0, rim=None):
    """Five-storey pagoda: vermilion storeys shrinking upward, deep upturned eaves, a bronze spire (sorin)."""
    hz = (lambda c: mix(c, "#C8B8D0", haze)) if haze else (lambda c: c)
    out = []
    spire = h * 0.2
    sh = (h - spire) / tiers
    w0 = h * 0.24
    y = base
    out.append(f'<path d="{pd([(cx - w0 * 0.75, base), (cx + w0 * 0.75, base), (cx + w0 * 0.68, base - sh * 0.18), (cx - w0 * 0.68, base - sh * 0.18)])}" fill="{hz("#8A8478")}"/>')
    y -= sh * 0.18
    for t in range(tiers):
        w = w0 * (1 - 0.1 * t)
        bh = sh * (0.42 if t == 0 else 0.36)
        # storey body
        bd = pd([(cx - w * 0.5, y), (cx + w * 0.5, y), (cx + w * 0.5, y - bh), (cx - w * 0.5, y - bh)])
        out.append(f'<path d="{bd}" fill="{hz(body[1])}"/>')
        out.append(f'<path d="{pd([(cx + w * 0.12, y), (cx + w * 0.5, y), (cx + w * 0.5, y - bh), (cx + w * 0.12, y - bh)])}" fill="{hz(body[2])}" opacity="0.45"/>')
        for k in (-0.3, 0, 0.3):
            out.append(f'<path d="M {cx + k * w:.1f} {y:.1f} L {cx + k * w:.1f} {y - bh:.1f}" stroke="{hz(body[2])}" stroke-width="{max(0.8, w * 0.035):.1f}" opacity="0.7"/>')
        out.append(f'<path d="M {cx - w * 0.5:.1f} {y - bh * 0.35:.1f} L {cx + w * 0.5:.1f} {y - bh * 0.35:.1f}" stroke="{hz("#F6E8D0")}" stroke-width="{max(0.8, w * 0.03):.1f}" opacity="0.8"/>')
        y -= bh
        # eave: wide, thin at the tips, sweeping up
        rw = w * 1.02
        up = sh * 0.2
        rh = sh * 0.34
        rf = [(cx - rw, y - up), (cx - rw * 0.8, y - up * 0.1), (cx - rw * 0.4, y + up * 0.1), (cx + rw * 0.4, y + up * 0.1), (cx + rw * 0.8, y - up * 0.1), (cx + rw, y - up),
              (cx + rw * 0.62, y - rh * 0.6), (cx + w * 0.32, y - rh), (cx - w * 0.32, y - rh), (cx - rw * 0.62, y - rh * 0.6)]
        rd = smooth_closed(rf)
        out.append(f'<path d="{rd}" fill="{hz(roof[1])}"/>')
        out.append(f'<path d="{smooth_closed([(cx - rw, y - up), (cx - rw * 0.4, y + up * 0.1), (cx + rw * 0.4, y + up * 0.1), (cx + rw, y - up), (cx + rw * 0.4, y - up * 0.2), (cx - rw * 0.4, y - up * 0.2)])}" fill="{hz(roof[2])}" opacity="0.8"/>')
        out.append(f'<path d="{smooth_open([(cx - rw * 0.66, y - rh * 0.58), (cx - w * 0.3, y - rh * 0.92), (cx, y - rh * 0.95)])}" stroke="{hz(rim or roof[0])}" stroke-width="{max(1, w * 0.04):.1f}" fill="none" opacity="0.7"/>')
        if inkw:
            out.append(ink(rd, hz(INK), inkw, seed + t, 1, 0.5))
        y -= rh * 0.85
    # spire with rings
    out.append(f'<path d="M {cx:.1f} {y + 2:.1f} L {cx:.1f} {y - spire:.1f}" stroke="{hz("#5A4A30")}" stroke-width="{max(1.4, h * 0.012):.1f}"/>')
    for k in range(9):
        ry = y - spire * 0.18 - k * spire * 0.07
        out.append(f'<path d="M {cx - h * 0.018:.1f} {ry:.1f} L {cx + h * 0.018:.1f} {ry:.1f}" stroke="{hz("#B8903A")}" stroke-width="{max(1, h * 0.007):.1f}"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{y - spire:.1f}" r="{max(1.2, h * 0.01):.1f}" fill="{hz("#D8A848")}"/>')
    return "".join(out)


def hanko(D, cx, cy, s, seed, glyph="yama", col="#C8281E", paper_c=WASHI, rot_=-3):
    """Red seal stamp with the character carved out in white (painted strokes, not a font)."""
    rnd = random.Random(seed)
    half = s / 2
    out = [f'<g transform="rotate({rot_} {cx} {cy})">',
           f'<path d="{hg.org_rect(cx - half, cy - half, s, s, seed, 0.8, 8, s * 0.08)}" fill="{col}" opacity="0.92"/>']
    k = s / 100
    if glyph == "yama":   # 山: tall centre stroke, left stroke turning along the base, right stroke
        strokes_ = [[(50, 14), (50, 80)],
                    [(22, 36), (22, 80), (78, 80)],
                    [(78, 36), (78, 80)]]
    else:
        strokes_ = []
    for sk in strokes_:
        p = [(cx - half + x * k, cy - half + y * k) for x, y in sk]
        out.append(f'<path d="{pd(p, False)}" stroke="{paper_c}" stroke-width="{s * 0.11:.1f}" fill="none" stroke-linecap="square" stroke-linejoin="miter"/>')
    # inner border, and missed-ink specks that make it look stamped
    out.append(f'<path d="{hg.org_rect(cx - half + s * 0.07, cy - half + s * 0.07, s * 0.86, s * 0.86, seed + 1, 0.5, 8, 2)}" stroke="{paper_c}" stroke-width="{s * 0.035:.1f}" fill="none" opacity="0.85"/>')
    for _ in range(int(s * 0.5)):
        out.append(f'<circle cx="{cx + rnd.uniform(-half, half):.1f}" cy="{cy + rnd.uniform(-half, half):.1f}" r="{rnd.uniform(0.4, 1.4):.1f}" fill="{paper_c}" opacity="{rnd.uniform(0.3, 0.8):.2f}"/>')
    out.append("</g>")
    return "".join(out)


def seigaiha(D, d, box, R, cols, line, seed, rings=4, lw=None):
    """Blue-wave pattern (overlapping fans of concentric rings), clipped into path d."""
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    items = []
    row = 0
    y = y0 - R
    lw = lw or max(1.2, R * 0.08)
    while y < y1 + R:
        off = (row % 2) * R
        x = x0 - 2 * R + off
        while x < x1 + 2 * R:
            c = cols[(row + int((x - x0) / (2 * R))) % len(cols)]
            items.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{R:.1f}" fill="{c}"/>')
            for k in range(1, rings):
                items.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{R * (1 - k / rings):.1f}" fill="none" stroke="{line}" stroke-width="{lw:.1f}" opacity="{rnd.uniform(0.7, 0.95):.2f}"/>')
            items.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{R:.1f}" fill="none" stroke="{line}" stroke-width="{lw:.1f}"/>')
            x += 2 * R
        y += R * 0.5
        row += 1
    return clipped(D, d, items)


def shippo(D, d, r, col, sw=1.6, op=0.6, bg=None):
    """Seven-treasures pattern: interlocking circles."""
    pat = D.pattern(2 * r, 2 * r, (f'<rect width="{2 * r}" height="{2 * r}" fill="{bg}"/>' if bg else "")
                    + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}" opacity="{op}"/>'
                              for x, y in ((0, 0), (2 * r, 0), (0, 2 * r), (2 * r, 2 * r), (r, r))))
    return f'<path d="{d}" fill="{pat}"/>'


def chochin(D, cx, top, w, h, seed, pal=AKA, lit=True, cap="#1E1A1A", glow_c="#FFB860", band=None, haze=0.0):
    """Paper lantern: ribbed glowing body between black lacquer caps, a hanging cord above."""
    hz = (lambda c: mix(c, "#8A7AA0", haze)) if haze else (lambda c: c)
    out = []
    if lit:
        out.append(soft_glow(D, cx, top + h * 0.55, w * 1.6, glow_c, 0.5))
    out.append(f'<path d="M {cx:.1f} {top - h * 0.3:.1f} L {cx:.1f} {top:.1f}" stroke="{hz(cap)}" stroke-width="{max(1.2, w * 0.04):.1f}"/>')
    capw, caph = w * 0.62, h * 0.09
    body = [(cx - capw / 2, top + caph)] + [(cx + math.cos(math.radians(a)) * w / 2, top + h / 2 + math.sin(math.radians(a)) * (h / 2 - caph)) for a in range(-150, -29, 15)][::-1]
    body = []
    for i in range(25):
        t = i / 24
        yy = top + caph + (h - 2 * caph) * t
        ww = capw / 2 + (w / 2 - capw / 2) * math.sin(math.pi * t) ** 0.7
        body.append((cx + ww, yy))
    body = body + [(2 * cx - x, y) for x, y in body[::-1]]
    bd = smooth_closed(body)
    lp = (hz(lt(pal[1], 0.45)), hz(lt(pal[1], 0.15)), hz(pal[2])) if lit else tuple(hz(c) for c in pal)
    out.append(f'<path d="{bd}" fill="{lp[1]}"/>')
    inner = []
    if lit:
        inner.append(f'<ellipse cx="{cx:.1f}" cy="{top + h * 0.5:.1f}" rx="{w * 0.36:.1f}" ry="{h * 0.36:.1f}" fill="{D.rad([(0, hz("#FFF2C0"), 0.95), (1, hz("#FFF2C0"), 0)])}"/>')
    if band:
        inner.append(f'<rect x="{cx - w:.1f}" y="{top + h * 0.38:.1f}" width="{2 * w:.1f}" height="{h * 0.24:.1f}" fill="{hz(band)}" opacity="0.9"/>')
    for k in range(1, 9):
        yy = top + caph + (h - 2 * caph) * k / 9
        inner.append(f'<path d="M {cx - w:.1f} {yy:.1f} Q {cx:.1f} {yy + h * 0.035:.1f} {cx + w:.1f} {yy:.1f}" stroke="{lp[2]}" stroke-width="{max(0.8, h * 0.012):.1f}" fill="none" opacity="0.45"/>')
    inner.append(shade_over(D, bd, "#1A0404", 0.5, 0, 0, 1, 0, 0.45))
    inner.append(light_over(D, bd, "#FFFFFF", 0.3, 0, 0, 0.5, 0, 0.5))
    out.append(clipped(D, bd, inner))
    out.append(ink(bd, hz(INK), max(1, w * 0.025), seed, 1, 0.5))
    for yy, sg in ((top, 1), (top + h - caph, -1)):
        cd = hg.org_rect(cx - capw / 2, yy, capw, caph, seed + int(yy), 0.4, 8, 1.5)
        out.append(f'<path d="{cd}" fill="{hz(cap)}"/>')
        out.append(f'<path d="M {cx - capw / 2 + 2:.1f} {yy + caph * 0.3:.1f} L {cx + capw / 2 - 2:.1f} {yy + caph * 0.3:.1f}" stroke="#FFFFFF" stroke-width="1" opacity="0.3"/>')
    return "".join(out)


def round_dish(D, cx, cy, rx, ry, seed, glaze=WHITE, rim=AI, depth=8):
    """Small porcelain dish seen at an angle, with an indigo-painted rim."""
    out = [cast(D, cx + 6, cy + depth + 2, rx * 1.05, ry * 0.9, strength=0.35, seed=seed)]
    outer = ell_pts(cx, cy, rx, ry, 0, 360, 28)
    side = ell_pts(cx, cy + depth, rx * 0.92, ry * 0.92, 0, 180, 14) + ell_pts(cx, cy, rx, ry, 180, 0, 14)[::-1][::-1]
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy + depth * 0.7, rx * 0.95, ry, 0, 360, 28))}" fill="{glaze[2]}"/>')
    out.append(painted(D, outer, glaze, seed, sdir=(0.6, 0.8), sk=0.08, angle=0, n=10, inkw=1.4, hi=0.4))
    out.append(ink(smooth_closed(ell_pts(cx, cy, rx * 0.86, ry * 0.84, 0, 360, 28)), rim[1], max(1.6, rx * 0.05), seed + 1, 1, 0.85))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, cy + ry * 0.06, rx * 0.72, ry * 0.68, 0, 360, 28))}" fill="{glaze[2]}" opacity="0.18"/>')
    return "".join(out)


# ================================================================ 1. onigiri — three rice balls on a bamboo leaf
def onigiri(D, cx, base, w, h, seed, nori=True, topping=None, bite=None, light=(-0.6, -0.8)):
    """Rice ball: rounded triangle of grains (each one drawn), soft blue shadow side, nori band at the base."""
    rnd = random.Random(seed)
    A, B, C = (cx, base - h), (cx + w / 2, base), (cx - w / 2, base)
    pts = jitter(round_poly([A, B, C], [w * 0.2, w * 0.26, w * 0.26], 6), seed, 0.8)
    if bite:
        pts = bite_out(pts, *bite)
    d = smooth_closed(pts)
    out = [cast(D, cx + 10, base + 2, w * 0.6, 11, strength=0.45, seed=seed)]
    out.append(f'<path d="{d}" fill="#F6F2EA"/>')
    inner = [shade_over(D, d, "#5A6080", 0.5, 0.1, 0, 0.95, 0.9, 0.3)]
    cy = base - h * 0.45
    for _ in range(int(w * h / 26)):
        x, y = rnd.uniform(cx - w / 2, cx + w / 2), rnd.uniform(base - h, base)
        lit = -((x - cx) / w * light[0] * 2 + (y - cy) / h * light[1] * 2)
        col = rnd.choice(["#FFFFFF", "#FFFEFA"]) if lit > -0.2 else rnd.choice(["#F4F2EE", "#ECEAE6", "#E2E2E4"])
        sc = "#DAD4CA" if lit > 0 else "#BCBAC2"
        inner.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(3.6, 4.6):.1f}" ry="{rnd.uniform(1.9, 2.4):.1f}" fill="{col}" stroke="{sc}" stroke-width="0.7" '
                     f'opacity="{rnd.uniform(0.75, 1):.2f}" transform="rotate({rnd.uniform(0, 180):.0f} {x:.1f} {y:.1f})"/>')
    inner.append(f'<path d="{blob(cx - w * 0.14, base - h * 0.62, w * 0.12, h * 0.16, seed + 3, 0.2, 10, 30)}" fill="#FFFFFF" opacity="0.55"/>')
    if bite:
        bx, by, br = bite
        gx, gy = cx - bx, base - h * 0.4 - by
        gl = math.hypot(gx, gy) or 1
        sx, sy = bx + gx / gl * br * 1.05, by + gy / gl * br * 1.05
        inner.append(f'<path d="{blob(sx, sy, br * 0.62, br * 0.48, seed + 5, 0.2, 12)}" fill="#F08A5A"/>')
        inner.append(f'<path d="{blob(sx + 3, sy + 3, br * 0.4, br * 0.3, seed + 6, 0.2, 10)}" fill="#D8603A" opacity="0.6"/>')
        for _ in range(18):
            fx, fy = sx + rnd.uniform(-br * 0.5, br * 0.5), sy + rnd.uniform(-br * 0.35, br * 0.35)
            inner.append(f'<path d="M {fx:.1f} {fy:.1f} l {rnd.uniform(3, 7):.1f} {rnd.uniform(-2, 2):.1f}" stroke="{rnd.choice(["#FFC0A0", "#D8603A", "#FFE0D0"])}" stroke-width="1.6" stroke-linecap="round"/>')
    if nori:
        nw = w * 0.5
        nd = hg.org_poly([(cx - nw / 2, base - h * 0.4), (cx + nw / 2, base - h * 0.42), (cx + nw / 2 + 4, base + 6), (cx - nw / 2 - 4, base + 6)], seed + 9, 1.2, 10, 3)
        nori_i = [f'<path d="{nd}" fill="{NORI[1]}"/>',
                  strokes(D.nid(), nd, (cx - nw, base - h * 0.45, cx + nw, base + 8), [NORI[0], "#2E3E30", NORI[2], "#4A5A40"], seed + 10, n=40, angle=-80,
                          length=(8, 24), width=(1, 3), opacity=(0.25, 0.6), curve=0.3),
                  f'<path d="{blob(cx - nw * 0.25, base - h * 0.25, nw * 0.08, h * 0.12, seed + 11, 0.2, 8)}" fill="#8A9A8A" opacity="0.35"/>',
                  f'<path d="M {cx - nw / 2:.1f} {base - h * 0.4:.1f} L {cx + nw / 2:.1f} {base - h * 0.42:.1f}" stroke="#0A0E0A" stroke-width="2" opacity="0.6"/>']
        inner.append(clipped(D, nd, nori_i))
    if topping == "sesame":
        for _ in range(26):
            x, y = cx + rnd.uniform(-w * 0.3, w * 0.3), base - h * rnd.uniform(0.45, 0.85)
            inner.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="2.4" ry="1.3" fill="#1A1410" transform="rotate({rnd.uniform(0, 180):.0f} {x:.1f} {y:.1f})"/>')
    out.append(clipped(D, d, inner))
    out.append(ink(d, "#7A6E64", 1.6, seed + 2, 2, 0.6))
    if topping == "ume":
        ux, uy = cx + 2, base - h * 0.66
        up = blob_pts(ux, uy, w * 0.11, w * 0.1, seed + 20, 0.1, 14)
        out.append(painted(D, up, ("#F06A6A", "#C0202E", "#6A0A14"), seed + 20, sdir=(0.6, 0.8), sk=0.22, angle=-40, n=10, inkw=1.4, hi=0.35))
        for k in range(4):
            a = rnd.uniform(0, 6.28)
            out.append(pline([(ux + math.cos(a) * w * 0.03, uy + math.sin(a) * w * 0.03), (ux + math.cos(a) * w * 0.08, uy + math.sin(a) * w * 0.07)], "#6A0A14", 1.2, seed + k, 0.6, 1))
        out.append(f'<circle cx="{ux - w * 0.04:.1f}" cy="{uy - w * 0.04:.1f}" r="{w * 0.022:.1f}" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


@design("onigiri")
def onigiri_d():
    D = Doc2("jp-og")
    out = [paper(D.nid(), "#F4EAD2", FLECK, 101)]
    out.append(blooms(4, ["#C8DCB0", "#B8D0A0", "#E8E0C0"], 6, (60, 60, 540, 420), (120, 200), (0.12, 0.2)))
    out.append(soft_glow(D, 300, 360, 260, "#FFF2C8", 0.5))
    # hinoki cutting board, seen at a slant
    top = [(30, 436), (570, 418), (590, 494), (18, 520)]
    out.append(cast(D, 310, 532, 300, 26, strength=0.4, seed=2))
    out.append(f'<path d="{pd([(18, 520), (590, 494), (590, 516), (20, 544)])}" fill="{HINOKI[2]}"/>')
    out.append(painted(D, densify(top, 30), HINOKI, 103, sdir=(0.3, 1), sk=0.08, angle=-3, n=60, slen=(40, 120), sw=(1, 2.4), inkw=1.8, hi=0.4))
    for k in range(7):
        y = 430 + k * 12
        out.append(pline([(50 + k * 2, y), (300, y - 6 + k * 0.5), (560 - k * 3, y - 12)], HINOKI[2], 1.1, 104 + k, 0.35, 1))
    # bamboo leaves under the rice balls
    out.append(long_leaf(D, 60, 490, 480, 104, -9, ("#9ACB6A", "#3E8A3A", "#1A4A1E"), 105, veins=3))
    out.append(long_leaf(D, 120, 510, 340, 72, -22, ("#B8DA80", "#5AA040", "#245A22"), 106, veins=2))
    # three onigiri; the front one has had a bite taken, showing the salmon inside
    out.append(onigiri(D, 190, 462, 186, 168, 110, topping="ume"))
    out.append(onigiri(D, 412, 456, 186, 166, 111, topping="sesame"))
    fw, fh, fb = 212, 192, 520
    t = 0.3
    bx, by = 300 + fw / 2 * t + 8, fb - fh + fh * t - 4
    out.append(onigiri(D, 300, fb, fw, fh, 112, bite=(bx + 14, by - 6, 34)))
    # little dish of takuan
    out.append(round_dish(D, 500, 548, 46, 17, 113))
    for k, (x, y, a) in enumerate(((486, 544, -10), (502, 540, 6), (516, 546, 18))):
        sl = rot([(x - 13, y), (x - 9, y - 9), (x + 9, y - 9), (x + 13, y), (x, y + 2)], x, y, a)
        out.append(painted(D, sl, ("#FFF2A0", "#F2CC3A", "#B08A10"), 114 + k, sdir=(0.5, 1), sk=0.15, angle=0, n=4, inkw=1, hi=0.4))
    # chopsticks resting at the front left
    out.append(chopsticks(D, 64, 566, 250, 546, 115, w=8, gap=10))
    # lettering
    out.append(letters(D, 300, 170, "onigiri", SERIF_IT, 132, "#2E5A2A", ["#3E7A3A", "#1A3A1A", "#5A8A40"], 116, max_w=400,
                       shadow="#DCE8C8", soff=(0.02, 0.035), angle=-40, hi="#A8D080"))
    out.append(ruled(300, 220, "PACKED WITH LOVE", "#B8402A", font=JOS, size=22, ls=8, line_w=40, gap=14))
    return finish_b(D, out, 117)


# ================================================================ 2. ramen — a steaming bowl from above
def raimon_band(cx, cy, R0, R1, n, col, w):
    """The red 'thunder' meander that runs round a ramen bowl's rim, bent into the ring."""
    unit = [(0.08, 0.15), (0.92, 0.15), (0.92, 0.88), (0.22, 0.88), (0.22, 0.38), (0.72, 0.38), (0.72, 0.66), (0.44, 0.66)]
    out = []
    for k in range(n):
        a0 = 2 * math.pi * k / n
        a1 = 2 * math.pi * (k + 1) / n
        pts = []
        for (u0, v0), (u1, v1) in zip(unit, unit[1:]):
            for j in range(6):
                t = j / 6
                u, v = u0 + (u1 - u0) * t, v0 + (v1 - v0) * t
                a = a0 + (a1 - a0) * u
                r = R0 + (R1 - R0) * v
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        u, v = unit[-1]
        pts.append((cx + (R0 + (R1 - R0) * v) * math.cos(a0 + (a1 - a0) * u), cy + (R0 + (R1 - R0) * v) * math.sin(a0 + (a1 - a0) * u)))
        out.append(f'<path d="{pd(pts, False)}" stroke="{col}" stroke-width="{w}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
    return "".join(out)


def chashu(D, cx, cy, r, seed, rot_=0):
    rnd = random.Random(seed)
    pts = blob_pts(cx, cy, r, r * 0.86, seed, 0.07, 16, rot_)
    d = smooth_closed(pts)
    out = [f'<path d="{blob(cx + 3, cy + 4, r, r * 0.86, seed, 0.07, 16, rot_)}" fill="#3A1A08" opacity="0.35"/>',
           f'<path d="{d}" fill="#8A4A24"/>']
    inner = [f'<path d="{blob(cx, cy, r * 0.84, r * 0.72, seed + 1, 0.1, 14, rot_)}" fill="#E8B8A0"/>',
             f'<path d="{blob(cx + r * 0.1, cy + r * 0.05, r * 0.6, r * 0.5, seed + 2, 0.15, 12, rot_)}" fill="#D8907A" opacity="0.8"/>']
    # spiral of fat rolled through the meat
    sp = [(cx + math.cos(t) * r * 0.08 * t, cy + math.sin(t) * r * 0.07 * t) for t in [i * 0.35 for i in range(28)]]
    inner.append(taper(sp, 1.5, 4.5, "#FFF0E0", 0.85))
    for _ in range(14):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0.2, 0.75) * r
        inner.append(f'<path d="M {cx + math.cos(a) * rr:.1f} {cy + math.sin(a) * rr:.1f} l {rnd.uniform(-5, 5):.1f} {rnd.uniform(-3, 3):.1f}" stroke="#B86A50" stroke-width="1.2" opacity="0.6"/>')
    inner.append(f'<path d="{blob(cx - r * 0.3, cy - r * 0.35, r * 0.35, r * 0.12, seed + 3, 0.2, 10, -25)}" fill="#FFFFFF" opacity="0.4"/>')
    out.append(clipped(D, d, inner))
    out.append(ink(d, "#3A1A08", 1.4, seed, 1, 0.6))
    return "".join(out)


def egg_half(D, cx, cy, rx, ry, rot_, seed):
    pts = rot(blob_pts(cx, cy, rx, ry, seed, 0.03, 18), cx, cy, rot_)
    d = smooth_closed(pts)
    out = [f'<path d="{blob(cx + 3, cy + 4, rx, ry, seed, 0.03, 16, rot_)}" fill="#3A2008" opacity="0.3"/>',
           f'<path d="{d}" fill="#F4E2C8"/>']
    yx, yy = cx + math.cos(math.radians(rot_)) * rx * 0.08, cy + math.sin(math.radians(rot_)) * rx * 0.08
    inner = [f'<path d="{d}" fill="none" stroke="#C88A50" stroke-width="{rx * 0.22:.1f}" opacity="0.55"/>',
             f'<path d="{blob(yx, yy, rx * 0.5, ry * 0.58, seed + 1, 0.06, 14, rot_)}" fill="#F2A21E"/>',
             f'<path d="{blob(yx, yy, rx * 0.36, ry * 0.42, seed + 2, 0.1, 12, rot_)}" fill="#E8701A"/>',
             f'<path d="{blob(yx - rx * 0.1, yy - ry * 0.12, rx * 0.14, ry * 0.12, seed + 3, 0.1, 8)}" fill="#FFE0A0" opacity="0.85"/>']
    out.append(clipped(D, d, inner))
    out.append(ink(d, "#8A5A30", 1.3, seed, 1, 0.6))
    return "".join(out)


def naruto(D, cx, cy, r, seed):
    pts = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        rr = r * (1 + 0.07 * math.cos(a * 12))
        pts.append((cx + rr * math.cos(a), cy + rr * 0.92 * math.sin(a)))
    d = smooth_closed(pts)
    sp = [(cx + math.cos(t) * r * 0.07 * t, cy + math.sin(t) * r * 0.065 * t) for t in [i * 0.3 for i in range(42)]]
    return (f'<path d="{blob(cx + 3, cy + 3, r, r * 0.9, seed, 0.05, 14)}" fill="#3A2008" opacity="0.3"/>'
            f'<path d="{d}" fill="#FFFBF4"/>' + taper(sp, 1.5, 4.5, "#F0648A", 0.95)
            + f'<path d="{blob(cx - r * 0.35, cy - r * 0.35, r * 0.3, r * 0.15, seed, 0.2, 8, -30)}" fill="#FFFFFF" opacity="0.6"/>'
            + ink(d, "#B8A898", 1.2, seed, 1, 0.7))


@design("ramen")
def ramen():
    D = Doc2("jp-rm")
    out = [wood_planks(D, 0, 600, 201, DARKWOOD, 5)]
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#000000", 0), (0.7, "#000000", 0.15), (1, "#000000", 0.45)], 0.5, 0.55, 0.75)}"/>')
    out.append(soft_glow(D, 300, 380, 300, "#FFD890", 0.3))
    cx, cy, R = 300, 378, 168
    out.append(cast(D, cx + 16, cy + 20, R + 14, R + 8, strength=0.55, seed=3))
    # bowl rim: white glaze, red thunder meander
    rim = smooth_closed(ell_pts(cx, cy, R, R, 0, 360, 48))
    out.append(painted(D, ell_pts(cx, cy, R, R, 0, 360, 48), ("#FFFFFF", "#F6F0E6", "#C0B4A4"), 204, sdir=(0.6, 0.8), sk=0.06, angle=-40, n=50, inkw=2, hi=0.4))
    out.append(raimon_band(cx, cy, R - 30, R - 8, 22, "#C8281E", 3.2))
    out.append(ink(smooth_closed(ell_pts(cx, cy, R - 6, R - 6, 0, 360, 48)), "#C8281E", 2, 205, 1, 0.8))
    out.append(ink(smooth_closed(ell_pts(cx, cy, R - 32, R - 32, 0, 360, 48)), "#C8281E", 2, 206, 1, 0.8))
    # broth
    Rb = R - 38
    bd = smooth_closed(ell_pts(cx, cy, Rb, Rb, 0, 360, 48))
    rnd = random.Random(207)
    broth = [f'<path d="{bd}" fill="{D.rad([(0, "#E8B464"), (0.7, "#C8823A"), (1, "#8A4A1A")], 0.42, 0.4, 0.62)}"/>']
    # noodles curling up at the lower left
    for k in range(26):
        y0 = cy + rnd.uniform(-10, 110)
        x0 = cx - Rb - 10
        pts = []
        for j in range(16):
            t = j / 15
            x = x0 + t * Rb * rnd.uniform(1.1, 1.5)
            y = y0 + math.sin(t * 14 + k) * 5 + t * rnd.uniform(-30, 20)
            pts.append((x, y))
        c = rnd.choice(["#F6D88A", "#EEC870", "#FFE8A8", "#D8B060"])
        broth.append(f'<path d="{smooth_open(pts)}" stroke="#A8783A" stroke-width="5.4" fill="none" opacity="0.5"/>'
                     f'<path d="{smooth_open(pts)}" stroke="{c}" stroke-width="3.8" fill="none"/>')
    # oil droplets
    for _ in range(60):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * Rb
        x, y, s = cx + math.cos(a) * rr, cy + math.sin(a) * rr, rnd.uniform(1.5, 5)
        broth.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s:.1f}" fill="#FFE2A0" opacity="0.35"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{s:.1f}" fill="none" stroke="#FFF4D0" stroke-width="0.8" opacity="0.7"/>')
    broth.append(f'<path d="{bd}" fill="none" stroke="#5A2A0A" stroke-width="12" opacity="0.35"/>')
    out.append(clipped(D, bd, broth))
    # nori sheets tucked against the back of the bowl
    for k, (x, y, a, c) in enumerate(((236, 236, -14, "#1C2820"), (300, 226, 6, "#22302A"))):
        nd = hg.org_poly(rot([(x - 34, y - 46), (x + 34, y - 46), (x + 34, y + 42), (x - 34, y + 42)], x, y, a), 210 + k, 1, 10, 2)
        out.append(f'<path d="{nd}" fill="{c}"/>')
        out.append(strokes(D.nid(), nd, (x - 50, y - 60, x + 50, y + 60), ["#3E5040", "#0A100C", "#4A5A44"], 211 + k, n=30, angle=-80 + a, length=(10, 30), width=(1, 3), opacity=(0.25, 0.6)))
        out.append(ink(nd, "#0A0E0A", 1.2, 212 + k, 1, 0.6))
    # chashu, eggs, naruto, menma, scallions
    out.append(chashu(D, 372, 300, 48, 220, 10))
    out.append(chashu(D, 406, 352, 44, 221, -20))
    out.append(egg_half(D, 254, 330, 36, 28, -30, 222))
    out.append(egg_half(D, 300, 316, 36, 28, 15, 223))
    out.append(naruto(D, 360, 430, 26, 224))
    for k in range(6):
        x, y = 410 + k * 7 + rnd.uniform(-3, 3), 410 + k * 6
        md = hg.org_poly(rot([(x - 6, y - 22), (x + 6, y - 22), (x + 5, y + 22), (x - 5, y + 22)], x, y, 30 + rnd.uniform(-10, 10)), 230 + k, 0.6, 8, 2)
        out.append(f'<path d="{md}" fill="{rnd.choice(["#D8A860", "#C8964E", "#E2B872"])}"/>' + ink(md, "#7A5020", 1, 231 + k, 1, 0.6))
        out.append(f'<path d="M {x:.1f} {y - 18:.1f} L {x + 1:.1f} {y + 18:.1f}" stroke="#A87838" stroke-width="0.9" opacity="0.7" transform="rotate(30 {x:.1f} {y:.1f})"/>')
    for _ in range(46):
        a, rr = rnd.uniform(-1.6, 1.8), rnd.uniform(0.15, 0.7) * Rb
        x, y = cx - 10 + math.cos(a) * rr * 0.6, cy + 30 + math.sin(a) * rr * 0.55
        r = rnd.uniform(3.5, 6)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{rnd.choice(["#6AB040", "#4A9A30", "#8AC860"])}"/>'
                   f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.5:.1f}" fill="#E8F4C8"/>'
                   f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="none" stroke="#2E6A20" stroke-width="0.8" opacity="0.6"/>')
    out.append(specks(240, (250, 360, 360, 460), ["#FFF6E0", "#F2E2B8"], 30, (1, 1.8), (0.7, 1)))
    # steam over the bowl
    out.append(steam(300, 330, 110, 241, "#FFFFFF", 3, 40, 9, 0.35))
    # renge spoon and chopsticks on a rest
    sp = [(98, 508), (112, 470), (138, 448), (160, 452), (162, 476), (146, 500), (120, 520)]
    out.append(cast(D, 136, 520, 50, 14, strength=0.4, seed=5))
    out.append(painted(D, sp, ("#FFFFFF", "#F6F0E6", "#C0B4A4"), 242, sdir=(0.6, 0.8), sk=0.15, angle=-50, n=10, inkw=1.6, hi=0.4))
    out.append(taper([(116, 512), (92, 548), (80, 566)], 14, 9, "#F0E8DC"))
    out.append(ink(smooth_open([(116, 512), (92, 548), (80, 566)]), "#C0B4A4", 1.2, 243, 1, 0.6))
    out.append(f'<path d="{blob(140, 476, 14, 10, 244, 0.1, 10, -40)}" fill="#C8281E" opacity="0.15"/>')
    out.append(f'<path d="{hg.org_rect(494, 474, 32, 12, 245, 0.4, 6, 4)}" fill="#3A3436"/>')
    out.append(chopsticks(D, 520, 560, 486, 236, 246, pal=("#E86A50", "#B8301E", "#5A0E08"), w=9, gap=12, tip_col="#E8D4B0"))
    # lettering
    out.append(letters(D, 300, 132, "ramen", SERIF_IT, 118, "#FFF0D0", ["#FFFFFF", "#F2DCB4", "#FFE8C0"], 247, max_w=320,
                       shadow="#1A0A04", soff=(0.02, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(label(300, 176, "SLURPING IS POLITE HERE", MONO, 18, "#F6C25A", ls=3))
    return finish_b(D, out, 248, "#FFFFFF", 0.5)


def kakejiku(D, cx, top, bottom, w, seed, art, mount=("#C8D0A0", "#7E8A5A", "#3E4A2A"), paper_c="#FBF6EA"):
    """Hanging scroll: cord and hook, brocade mount, paper panel with `art(x0, y0, x1, y1)`, a roller with knobs."""
    out = [f'<path d="M {cx - 16:.1f} {top:.1f} L {cx:.1f} {top - 26:.1f} L {cx + 16:.1f} {top:.1f}" stroke="#5A3A20" stroke-width="1.6" fill="none"/>',
           f'<circle cx="{cx:.1f}" cy="{top - 27:.1f}" r="2.5" fill="#5A3A20"/>',
           f'<path d="{pd([(cx - w / 2 + 6, top + 6), (cx + w / 2 + 8, top + 6), (cx + w / 2 + 8, bottom + 6), (cx - w / 2 + 6, bottom + 6)])}" fill="#3A2418" opacity="0.15"/>']
    md = hg.org_rect(cx - w / 2, top, w, bottom - top, seed, 0.6, 12, 1)
    out.append(f'<path d="{md}" fill="{mount[1]}"/>')
    out.append(shippo(D, md, 7, mount[0], 1, 0.45))
    x0, y0, x1, y1 = cx - w / 2 + 12, top + 40, cx + w / 2 - 12, bottom - 50
    out.append(f'<path d="{pd([(cx - w / 2, top + 30), (cx + w / 2, top + 30), (cx + w / 2, top + 36), (cx - w / 2, top + 36)])}" fill="{mount[2]}" opacity="0.7"/>')
    out.append(f'<path d="{pd([(cx - w / 2, y1 + 12), (cx + w / 2, y1 + 12), (cx + w / 2, y1 + 18), (cx - w / 2, y1 + 18)])}" fill="{mount[2]}" opacity="0.7"/>')
    pdd = hg.org_rect(x0, y0, x1 - x0, y1 - y0, seed + 1, 0.4, 10, 0.5)
    out.append(f'<path d="{pdd}" fill="{paper_c}"/>')
    out.append(art(x0, y0, x1, y1))
    out.append(ink(md, INK, 1.2, seed + 2, 1, 0.5))
    # top stave and bottom roller
    out.append(f'<path d="{hg.org_rect(cx - w / 2 - 2, top - 4, w + 4, 8, seed + 3, 0.3, 8, 2)}" fill="#3A2418"/>')
    out.append(f'<path d="{hg.org_rect(cx - w / 2 - 4, bottom - 5, w + 8, 10, seed + 4, 0.3, 8, 3)}" fill="#2A1A10"/>')
    for sg in (-1, 1):
        out.append(f'<path d="{blob(cx + sg * (w / 2 + 9), bottom, 6, 7, seed + 5 + sg, 0.1, 10)}" fill="#E8D8B8"/>' + ink(blob(cx + sg * (w / 2 + 9), bottom, 6, 7, seed + 5 + sg, 0.1, 10), INK, 1, seed, 1, 0.6))
    return "".join(out)


# ================================================================ 3. matcha — a tea bowl, whisk and scoop on tatami
def chawan(D, cx, rim_y, rx, h, seed, glaze=("#6A5A50", "#3A2E2A", "#1A1210"), drip=("#E8D8B8", "#C8B088", "#8A7050"), tea=MATCHA):
    """Hand-thrown tea bowl: uneven rim, iron glaze with a pale drip band, foamy matcha surface."""
    ry = rx * 0.26
    rnd = random.Random(seed)
    body = ell_pts(cx, rim_y, rx, ry, 0, 180, 16)
    body = [(cx + rx, rim_y)] + [(cx + rx * 0.98, rim_y + h * 0.4), (cx + rx * 0.82, rim_y + h * 0.82), (cx + rx * 0.4, rim_y + h), (cx - rx * 0.4, rim_y + h),
                                  (cx - rx * 0.82, rim_y + h * 0.82), (cx - rx * 0.98, rim_y + h * 0.4), (cx - rx, rim_y)]
    out = [cast(D, cx + 14, rim_y + h + 4, rx * 1.1, 14, strength=0.5, seed=seed)]
    # foot ring
    out.append(painted(D, rect_pts(cx - rx * 0.34, rim_y + h - 6, cx + rx * 0.34, rim_y + h + 10, 14, seed, 0.6), ("#D8B890", "#A8805A", "#5A3A20"), seed + 9,
                       sdir=(1, 0.3), sk=0.2, angle=0, n=8, inkw=1.4, hi=0.3))
    out.append(painted(D, jitter(body, seed, 1.5), glaze, seed, sdir=(0.9, 0.2), sk=0.2, angle=-80, n=60, slen=(10, 30), sw=(1, 3.5),
                       cols=[glaze[0], glaze[2], "#8A6A50", "#4A3A34"], inkw=2, hi=0.35, hik=0.06))
    bd = smooth_closed(jitter(body, seed, 1.5))
    # pale glaze drip band near the rim
    band = [(cx - rx, rim_y)] + [(cx - rx + 2 * rx * t, rim_y + ry * math.sin(math.pi * t) + 12 + 10 * math.sin(t * 19 + seed) + (24 if 0.3 < t < 0.36 or 0.62 < t < 0.66 else 0)) for t in [i / 30 for i in range(31)]] + [(cx + rx, rim_y)]
    out.append(clipped(D, bd, [f'<path d="{smooth_closed(band)}" fill="{drip[1]}" opacity="0.9"/>',
                               strokes(D.nid(), smooth_closed(band), (cx - rx, rim_y, cx + rx, rim_y + 60), [drip[0], drip[2]], seed + 3, n=30, angle=-85, length=(6, 18), width=(1, 3), opacity=(0.3, 0.6)),
                               shade_over(D, bd, "#0A0604", 0.55, 0, 0, 1, 0.2, 0.5),
                               taper([(cx - rx * 0.78, rim_y + h * 0.3), (cx - rx * 0.7, rim_y + h * 0.65)], 7, 2, "#FFFFFF", 0.35)]))
    # rim and matcha
    rd = smooth_closed(jitter(ell_pts(cx, rim_y, rx, ry, 0, 360, 36), seed + 4, 1.2))
    out.append(f'<path d="{rd}" fill="{drip[1]}"/>')
    td = smooth_closed(ell_pts(cx, rim_y + 2, rx * 0.9, ry * 0.78, 0, 360, 36))
    foam = [f'<path d="{td}" fill="{D.rad([(0, "#D8EA9A"), (0.6, tea[1]), (1, tea[2])], 0.45, 0.4, 0.6)}"/>']
    for _ in range(120):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.9
        x, y = cx + math.cos(a) * rx * 0.9 * rr, rim_y + 2 + math.sin(a) * ry * 0.78 * rr
        foam.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.6, 2):.1f}" fill="{rnd.choice(["#EEF8C8", "#B8D070", "#F6FFE0"])}" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    foam.append(f'<path d="{blob(cx - rx * 0.15, rim_y, rx * 0.35, ry * 0.3, seed + 6, 0.2, 12)}" fill="#F2FAD0" opacity="0.45"/>')
    out.append(clipped(D, td, foam))
    out.append(ink(td, tea[2], 1.2, seed + 5, 1, 0.5))
    out.append(ink(rd, INK, 2, seed + 7, 2, 0.75))
    return "".join(out)


def chasen(D, cx, base, h, seed):
    """Bamboo tea whisk standing on its tines: a node-ringed handle above a bulb of fine curved tines."""
    rnd = random.Random(seed)
    out = [cast(D, cx + 8, base + 2, h * 0.32, 8, strength=0.4, seed=seed)]
    bw = h * 0.27
    bulb_top = base - h * 0.62
    bulb = [(cx, bulb_top)]
    pts = []
    for i in range(21):
        t = i / 20
        y = bulb_top + (base - bulb_top) * t
        w = h * 0.05 + (bw - h * 0.05) * math.sin(math.pi * min(1, t * 0.95)) ** 0.8 if t < 0.85 else bw * (1 - (t - 0.85) * 1.2)
        pts.append((cx + w, y))
    shape = pts + [(2 * cx - x, y) for x, y in pts[::-1]]
    d = smooth_closed(shape)
    out.append(f'<path d="{d}" fill="#E8D4A8"/>')
    tines = []
    for k in range(40):
        u = -1 + 2 * k / 39
        line = [(cx + u * h * 0.05, bulb_top)]
        for i in range(1, 11):
            t = i / 10
            y = bulb_top + (base - bulb_top) * t
            w = bw * (math.sin(math.pi * min(1, t * 0.95)) ** 0.8 if t < 0.85 else (1 - (t - 0.85) * 1.2))
            line.append((cx + u * max(h * 0.05 * (1 - t), w), y))
        c = rnd.choice(["#C8A870", "#F6E6C0", "#B8925A", "#E8D0A0"])
        tines.append(f'<path d="{smooth_open(line)}" stroke="{c}" stroke-width="1.3" fill="none" opacity="0.9"/>')
    # inner curled tines
    for k in range(12):
        u = -0.5 + k / 11
        tines.append(f'<path d="M {cx + u * h * 0.04:.1f} {bulb_top + h * 0.06:.1f} Q {cx + u * bw * 0.9:.1f} {base - h * 0.32:.1f} {cx + u * bw * 0.3:.1f} {base - h * 0.2:.1f}" stroke="#9A7A48" stroke-width="1.1" fill="none" opacity="0.8"/>')
    tines.append(shade_over(D, d, "#3A2008", 0.45, 0, 0, 1, 0, 0.4))
    out.append(clipped(D, d, tines))
    out.append(ink(d, "#7A5A30", 1.4, seed, 1, 0.6))
    # handle with a binding thread and a bamboo node
    hl = [(cx - h * 0.055, bulb_top + 4), (cx - h * 0.05, base - h), (cx + h * 0.05, base - h), (cx + h * 0.055, bulb_top + 4)]
    out.append(painted(D, densify(hl, 10), ("#F6E6C0", "#D8BC88", "#8A6A3A"), seed + 2, sdir=(1, 0), sk=0.25, angle=-90, n=12, inkw=1.4, hi=0.5))
    out.append(f'<path d="M {cx - h * 0.055:.1f} {base - h * 0.78:.1f} Q {cx:.1f} {base - h * 0.765:.1f} {cx + h * 0.055:.1f} {base - h * 0.78:.1f}" stroke="#8A6A3A" stroke-width="2.2" fill="none"/>')
    out.append(f'<path d="{hg.org_rect(cx - h * 0.06, bulb_top - 2, h * 0.12, h * 0.05, seed + 3, 0.3, 6, 1)}" fill="#1E1A1A"/>')
    return "".join(out)


def nerikiri(D, cx, cy, r, seed, pal=SAKURA):
    """A sculpted sweet: five-lobed blossom of pink bean paste, lines pressed into it, a yellow centre."""
    pts = []
    for i in range(60):
        a = 2 * math.pi * i / 60
        rr = r * (0.86 + 0.14 * abs(math.cos(a * 2.5)))
        pts.append((cx + rr * math.cos(a - math.pi / 2), cy + rr * 0.62 * math.sin(a - math.pi / 2)))
    out = [cast(D, cx + 4, cy + r * 0.5, r * 1.1, r * 0.3, strength=0.4, seed=seed)]
    side = [(x, y + r * 0.35) for x, y in pts]
    out.append(f'<path d="{smooth_closed(side)}" fill="{pal[2]}"/>')
    out.append(painted(D, pts, pal, seed, sdir=(0.5, 0.8), sk=0.12, angle=-30, n=10, inkw=1.2, inkc="#A84A6A", hi=0.5))
    for i in range(5):
        a = 2 * math.pi * i / 5 - math.pi / 2
        out.append(pline([(cx + math.cos(a) * r * 0.2, cy + math.sin(a) * r * 0.12), (cx + math.cos(a) * r * 0.8, cy + math.sin(a) * r * 0.5)], "#C8607E", 1.4, seed + i, 0.7, 1))
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.14:.1f}" fill="#F6C83A"/>')
    return "".join(out)


@design("matcha")
def matcha():
    D = Doc2("jp-mc")
    out = [paper(D.nid(), "#F2E8D4", FLECK, 301)]
    out.append(blooms(5, ["#D8E4B0", "#E8DCC0", "#C8D8A0"], 6, (60, 60, 540, 420), (120, 200), (0.1, 0.18)))
    # tatami floor with its indigo cloth border
    out.append(tatami(D, 418, 600, 302, heri=("#4A64A0", "#1E2E5A", "#0E163A"), heri_y=418))
    out.append(f'<rect y="434" width="600" height="10" fill="#3A2A10" opacity="0.18"/>')
    # a hanging scroll with a brushed enso in the alcove
    out.append(kakejiku(D, 112, 240, 406, 90, 303, art=lambda x0, y0, x1, y1: enso((x0 + x1) / 2, (y0 + y1) / 2 - 10, (x1 - x0) * 0.36, 303, SUMI_INK, 7, a0=-58, sweep=318, op=0.88, paper_c="#FBF6EA")
                       + hanko(D, x1 - 12, y1 - 18, 12, 312)))
    out.append(soft_glow(D, 320, 380, 230, "#FFF6D8", 0.45))
    # sweet on a black lacquer plate
    pl = [(80, 500), (196, 486), (214, 520), (94, 536)]
    out.append(cast(D, 150, 532, 80, 12, strength=0.45, seed=4))
    out.append(painted(D, densify(pl, 20), ("#5A4A48", "#1E1616", "#060404"), 304, sdir=(0.3, 1), sk=0.1, angle=-5, n=14, inkw=1.4, hi=0.35))
    out.append(f'<path d="M 84 504 L 196 490" stroke="#C8382A" stroke-width="2" opacity="0.7"/>')
    out.append(nerikiri(D, 146, 496, 32, 305))
    # the bowl, then the whisk standing beside it
    out.append(chawan(D, 318, 380, 120, 106, 306, glaze=("#A0705A", "#5E3628", "#2A140E")))
    out.append(chasen(D, 482, 478, 156, 307))
    # bamboo scoop lying in front
    sc = [(300, 548), (420, 528), (432, 526), (440, 532), (428, 538), (420, 536), (302, 556)]
    out.append(cast(D, 372, 550, 80, 7, strength=0.35, seed=6))
    out.append(painted(D, sc, ("#F6E6C0", "#D8BC88", "#8A6A3A"), 308, sdir=(0.3, 1), sk=0.2, angle=-10, n=8, inkw=1.3, hi=0.5))
    out.append(f'<path d="M 358 540 q 2 4 0 8" stroke="#8A6A3A" stroke-width="1.6" fill="none"/>')
    out.append(f'<path d="{blob(432, 531, 6, 3, 309, 0.1, 8)}" fill="#7E9E3A"/>')
    # lettering
    out.append(letters(D, 300, 150, "matcha", SERIF_IT, 128, "#3E5A1A", ["#5A7A2A", "#2A4010", "#7E9E3A"], 310, max_w=390,
                       shadow="#E2E8C8", soff=(0.02, 0.035), angle=-40, hi="#C2D884"))
    out.append(ruled(300, 196, "ONE CUP, ONE MOMENT", "#8A3A20", font=JOS, size=20, ls=6, line_w=30, gap=12))
    return finish_b(D, out, 311)


# ================================================================ 4. sakura — a blossoming branch against a spring sky
@design("sakura")
def sakura():
    D = Doc2("jp-sk")
    out = [sky(D, [(0, "#BCD8EC"), (0.6, "#E8EEF0"), (1, "#FBEFE8")], 401, 600, ["#D8E8F4", "#FFFFFF", "#F6E0E6"], 70, angle=-4, sop=(0.08, 0.2))]
    out.append(blooms(6, ["#F6C8D4", "#FFFFFF", "#F2B8C8"], 9, (0, 0, 600, 600), (60, 140), (0.12, 0.24)))
    rnd = random.Random(402)
    # far blossoms, out of focus
    for _ in range(40):
        x, y, r = rnd.uniform(-20, 620), rnd.uniform(0, 330), rnd.uniform(10, 28)
        out.append(f'<path d="{blob(x, y, r, r * 0.9, rnd.randint(0, 999), 0.2, 10)}" fill="{rnd.choice(["#FBD8E2", "#F6C4D2", "#FFE8EE"])}" opacity="{rnd.uniform(0.3, 0.6):.2f}"/>')
    # the branch: a main limb from the upper left, twigs reaching down and right
    main = catmull([(-30, 70), (90, 108), (220, 120), (340, 156), (460, 176), (560, 220), (640, 226)], 6)
    tw1 = catmull([(220, 120), (250, 180), (300, 236), (330, 300)], 6)
    tw2 = catmull([(400, 166), (430, 120), (470, 86)], 5)
    tw3 = catmull([(110, 110), (120, 170), (102, 230)], 5)
    tw4 = catmull([(470, 180), (500, 250), (488, 310)], 5)
    tw5 = catmull([(360, 160), (392, 220), (410, 276), (398, 336)], 5)
    out.append(bark_branch(D, main, 30, 14, 403))
    for k, t in enumerate((tw1, tw2, tw3, tw4, tw5)):
        out.append(bark_branch(D, t, 12, 4, 404 + k))
    # blossoms clustered along the wood
    spots = [(60, 96, 30), (150, 92, 32), (176, 140, 28), (238, 102, 34), (272, 168, 30), (300, 222, 32), (330, 290, 30), (308, 270, 22),
             (360, 140, 30), (418, 140, 26), (448, 98, 30), (482, 74, 22), (512, 206, 32), (494, 262, 30), (486, 312, 26), (560, 194, 28),
             (120, 196, 28), (96, 236, 24), (390, 190, 26), (210, 150, 22), (404, 252, 26), (412, 300, 24), (390, 340, 22), (436, 280, 18)]
    for k, (x, y, r) in enumerate(spots):
        out.append(sakura_flower(D, x, y, r, 410 + k * 7, rnd.uniform(0, 72), tilt=rnd.uniform(0.75, 1)))
    # buds and fresh red-green leaves
    for k, (x, y, a) in enumerate(((198, 72, -60), (330, 120, -80), (536, 246, 40), (276, 250, 120), (82, 270, 110), (430, 210, 60))):
        bp = rot([(x, y - 9), (x + 6, y), (x, y + 8), (x - 6, y)], x, y, a)
        out.append(painted(D, bp, ("#FFC0D0", "#E86A8A", "#A8304E"), 600 + k, sk=0.2, n=4, inkw=1, hi=0.4))
        out.append(leaf_simple(D, x, y + 6, 26, 7, a + 100, ("#C8B060", "#8A7A30", "#4A4010"), 620 + k, vein=False, inkw=0.8))
    # petals drifting down
    for k in range(18):
        x, y = rnd.uniform(70, 530), rnd.uniform(320, 540)
        if 120 < x < 480 and 380 < y < 520:
            continue
        out.append(sakura_petal(D, x, y, rnd.uniform(9, 14), rnd.uniform(0, 360), 700 + k))
    for k, (x, y) in enumerate(((90, 400), (520, 380), (140, 520), (470, 540), (300, 350), (210, 380), (400, 360))):
        out.append(sakura_petal(D, x, y, 12, rnd.uniform(0, 360), 740 + k))
    # lettering
    out.append(letters(D, 300, 468, "sakura", SERIF_IT, 140, "#C2406A", ["#E0668C", "#9A2448", "#F08AAA"], 760, max_w=400,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#FFD0DC"))
    out.append(ruled(300, 514, "HANAMI SEASON", "#5A6A8A", font=JOS, size=22, ls=9, line_w=40, gap=14))
    return finish_b(D, out, 761, "#5A3A4A", 0.7)


# ================================================================ 5. fuji-san — dawn over the lake, a pagoda among pines
def fuji_shape(c, top, base, half_top=34, spread=400, p=1.9):
    """Fuji's profile: a short notched summit plateau and concave slopes. Returns (outline points, slope fn)."""
    def f(x):
        dx = abs(x - c)
        if dx <= half_top:
            return top
        t = min(1, (dx - half_top) / spread)
        return top + (base - top) * (1 - (1 - t) ** p)
    xs = [c - half_top - spread * (1 - i / 24) for i in range(25)]
    left = [(x, f(x)) for x in xs]
    summit = [(c - half_top + 12, top - 3), (c - 10, top + 2), (c + 4, top - 3), (c + 18, top + 1)]
    right = [(2 * c - x, y) for x, y in left[::-1]]
    return left + summit + right, f


def fuji_snow(c, top, f, seed, half=170, depth=62):
    """Snow cap: follows the summit, its lower edge torn into long fingers running down the gullies."""
    rnd = random.Random(seed)
    edge = []
    n = 46
    for i in range(n + 1):
        x = c - half + 2 * half * i / n
        dx = abs(x - c) / half
        tri = abs(((i * 0.5) % 2) - 1)            # triangle wave -> alternating fingers
        d = depth * (1 - 0.55 * dx) + (tri * 46 + rnd.uniform(0, 14)) * (1 - 0.6 * dx)
        edge.append((x, f(x) + max(4, d * (1 - dx * 0.8))))
    upper = [(x, f(x)) for x in [c - half + 2 * half * i / 30 for i in range(31)]]
    upper = [(x, y - (2 if abs(x - c) < 34 else 0)) for x, y in upper]
    return upper + edge[::-1]


@design("fuji-san")
def fuji_san():
    D = Doc2("jp-fj")
    out = [sky(D, [(0, "#6A8AC8"), (0.38, "#E8B8C8"), (0.62, "#FFD8B0"), (1, "#FFE8C8")], 501, 400, ["#F6C8D0", "#FFFFFF", "#C8B0D8"], 80, angle=-2, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 470, 340, 220, "#FFF0B0", 0.6))
    rnd = random.Random(502)
    for k, (x, y, w) in enumerate(((110, 252, 220), (500, 236, 200), (440, 316, 260), (80, 330, 170))):
        out.append(f'<path d="{blob(x, y, w / 2, 7, 503 + k, 0.2, 14)}" fill="#FFF0EC" opacity="0.75"/><path d="{blob(x + 10, y + 5, w / 2.4, 4, 504 + k, 0.2, 14)}" fill="#D8A0B8" opacity="0.45"/>')
    c, top, base = 300, 206, 398
    fuji, f = fuji_shape(c, top, base, 34, 420, 1.9)
    fd = smooth_closed(fuji + [(760, 440), (-160, 440)])
    out.append(f'<path d="{fd}" fill="{D.lin([(0, "#8A94C8"), (0.55, "#5E6CAA"), (1, "#7A84B8")])}"/>')
    inner = [f'<path d="{smooth_closed([(c + 6, top), (760, base), (760, 440), (c + 60, 440)])}" fill="#2A3470" opacity="0.32"/>',
             f'<path d="{smooth_closed([(c - 6, top), (-160, base), (-160, 300)])}" fill="#F8C8C8" opacity="0.18"/>',
             strokes(D.nid(), fd, (-60, top, 660, 440), ["#9AA0D0", "#4A5490", "#B8B0D8"], 505, n=140, angle=-72, length=(20, 70), width=(1.5, 4), opacity=(0.15, 0.4))]
    # ridges running down from the snow
    for k in range(9):
        x0 = c - 150 + k * 38
        inner.append(taper([(x0, f(x0) + 50), (x0 + (x0 - c) * 0.35, f(x0) + 110), (x0 + (x0 - c) * 0.6, base)], 3, 1, "#3A4482", 0.35))
    sn = fuji_snow(c, top, f, 506)
    sd = smooth_closed(sn)
    inner.append(f'<path d="{sd}" fill="#FCF8F6"/>')
    inner.append(clipped(D, sd, [f'<path d="{smooth_closed([(c + 4, top - 10), (c + 240, 330), (c + 240, 420), (c + 20, 420)])}" fill="#B4B8E2" opacity="0.65"/>',
                                 f'<path d="{smooth_closed([(c - 240, 320), (c - 20, top - 10), (c - 4, 320)])}" fill="#FFDCD4" opacity="0.6"/>',
                                 strokes(D.nid(), sd, (c - 200, top - 4, c + 200, 330), ["#FFFFFF", "#C8C8E8", "#FFE8E4"], 507, n=70, angle=-78, length=(14, 40), width=(1, 3), opacity=(0.25, 0.6))]))
    inner.append(ink(smooth_open(sn[31:]), "#8A90C8", 1.2, 508, 1, 0.45))
    out.append(clipped(D, fd, inner))
    out.append(ink(smooth_open(fuji), "#3A3A6A", 1.6, 509, 1, 0.5))
    # lake with Fuji's reflection broken by ripples
    out.append(f'<rect y="396" width="600" height="204" fill="{D.lin([(0, "#E8C8C8"), (0.3, "#A8B4D8"), (1, "#4A5A98")])}"/>')
    refl = [(x, 2 * 398 - y) for x, y in fuji]
    out.append(f'<path d="{smooth_closed(refl + [(760, 396), (-160, 396)])}" fill="#7A84B8" opacity="0.5"/>')
    out.append(f'<path d="{smooth_closed([(x, 2 * 398 - y) for x, y in sn])}" fill="#F2E8F0" opacity="0.45"/>')
    out.append(wave_lines(510, (0, 404, 600, 590), ["#FFFFFF", "#E8D8F0", "#C8D0E8"], 70, (20, 60), 2.2, 2, (0.35, 0.7)))
    out.append(wave_lines(511, (0, 410, 600, 590), ["#3A4A88", "#2A3470"], 40, (20, 50), 2, 2, (0.3, 0.6)))
    hl = ridge([(-20, 400), (140, 390), (300, 402), (440, 392), (620, 400)], 512, 5, 3)
    out.append(hill(D, hl, 406, ("#8A9AB8", "#6A7AA0", "#4A5A80"), 513, inkw=0, n=20))
    # left headland with pines and the pagoda
    lh = ridge([(-20, 318), (70, 306), (160, 336), (220, 392), (262, 432)], 514, 8, 3)
    shore = [(250, 452), (200, 486), (130, 520), (50, 548), (-20, 560)]
    land = [(-40, 330)] + lh + shore + [(-40, 600)]
    out.append(painted(D, land, ("#6A8A72", "#3A5A4E", "#1E3A30"), 515, sdir=(1, 0.4), sk=0.06, angle=-10, n=120, slen=(20, 60), sw=(2, 5), inkw=1.6, hi=0.25))
    out.append(f'<path d="{smooth_closed([(x, 2 * 452 - y + 20) for x, y in shore[::-1]] + shore)}" fill="#1E3A30" opacity="0.25"/>')
    out.append(taper([(262, 440), (200, 482), (120, 518), (40, 548)], 3, 2, "#FFFFFF", 0.35))
    out.append(pagoda(D, 128, 360, 210, 517, haze=0.04))
    for k, (x, b, h, ln) in enumerate(((44, 344, 92, 0.3), (196, 396, 66, -0.25), (78, 462, 120, 0.35), (20, 380, 70, 0.2))):
        out.append(jpine(D, x, b, h, 520 + k, lean=ln, haze=0.12 if k != 2 else 0))
    # reeds at the near shore, a little boat
    out.append(grass(530, (380, 560, 600, 600), ["#2A3A3A", "#3A4A40", "#4A5A48"], 70, (20, 50), 2, (-0.2, 0.3)))
    out.append(f'<path d="M 360 488 Q 394 500 428 488 L 422 497 Q 394 507 366 497 Z" fill="#3A2A2A"/>')
    out.append(f'<path d="M 396 490 L 398 462" stroke="#3A2A2A" stroke-width="1.6"/>' + taper([(366, 502), (428, 502)], 1.5, 1.5, "#FFFFFF", 0.4))
    out.append(figures.person(404, 492, 18, "stand", -1, "silhouette:#3A2A2A", seed=3))
    for x, y, s_ in ((396, 222, 8), (420, 210, 6), (438, 232, 7)):
        out.append(bird_v(x, y, s_, "#4A3A5A", 0.8))
    # lettering and seal
    out.append(letters(D, 280, 134, "fuji-san", SERIF_IT, 104, "#2E3A78", ["#3E4E90", "#1E2A5A", "#5A6AA8"], 540, max_w=360,
                       shadow="#FFF0E8", soff=(0.02, 0.035), angle=-40, hi="#A8B8E8"))
    out.append(label(280, 174, "3,776 M · FIRST LIGHT", MONO, 17, "#8A3A3A", ls=4))
    out.append(hanko(D, 494, 112, 42, 541))
    return finish_b(D, out, 542, "#3A3A5A", 0.7)


# ================================================================ 6. daruma — one eye painted in, a wish made
def daruma_doll(D, cx, cy, rx, ry, seed, eyes=1):
    out = [cast(D, cx + 14, cy + ry * 0.95, rx * 1.05, 16, strength=0.5, seed=seed)]
    pts = [(cx + rx * math.cos(a) * (1 - 0.1 * max(0, -math.sin(a))), cy + ry * math.sin(a) + (ry * 0.08 * math.sin(a) if math.sin(a) > 0 else 0))
           for a in [2 * math.pi * i / 40 for i in range(40)]]
    pts = [(x, min(y, cy + ry * 0.92)) for x, y in pts]
    d = smooth_closed(pts)
    out.append(painted(D, pts, ("#F07060", "#D02A22", "#7A0A0E"), seed, sdir=(0.7, 0.5), sk=0.14, angle=-60, n=80, slen=(20, 60), sw=(2, 5), inkw=2.4, hi=0.45, hik=0.08))
    inner = []
    # gold belly ornaments: scrolling clouds
    for sg in (-1, 1):
        for k in range(3):
            sx, sy = cx + sg * rx * (0.42 + 0.1 * k), cy + ry * (0.38 + 0.12 * k)
            sp = [(sx + sg * math.cos(t) * 3 * t, sy + math.sin(t) * 2.6 * t) for t in [i * 0.4 for i in range(16)]]
            inner.append(taper(sp, 1.5, 4, "#F2C24A", 0.95))
    inner.append(f'<path d="{smooth_open([(cx - rx * 0.6, cy + ry * 0.62), (cx, cy + ry * 0.74), (cx + rx * 0.6, cy + ry * 0.62)])}" stroke="#F2C24A" stroke-width="5" fill="none"/>')
    inner.append(f'<path d="{smooth_open([(cx - rx * 0.66, cy + ry * 0.72), (cx, cy + ry * 0.84), (cx + rx * 0.66, cy + ry * 0.72)])}" stroke="#F2C24A" stroke-width="2.4" fill="none" stroke-dasharray="2 6"/>')
    inner.append(shade_over(D, d, "#3A0004", 0.45, 0, 0, 1, 1, 0.45))
    out.append(clipped(D, d, inner))
    # white face
    fx, fy = cx, cy - ry * 0.22
    face = blob_pts(fx, fy, rx * 0.56, ry * 0.42, seed + 1, 0.03, 20)
    fd = smooth_closed(face)
    out.append(painted(D, face, ("#FFFFFF", "#FBF2E6", "#D8C8B0"), seed + 1, sdir=(0.6, 0.6), sk=0.1, angle=-50, n=16, inkw=2, hi=0.3))
    # gold border around the face
    out.append(ink(fd, "#E8A82A", 4, seed + 2, 1, 1))
    out.append(ink(fd, "#8A5A0A", 1.2, seed + 3, 1, 0.6))
    # eyebrows (cranes): thick sweeping sumi strokes feathered at the outer ends
    rnd = random.Random(seed + 11)
    for sg in (-1, 1):
        br = [(fx + sg * rx * 0.06, fy - ry * 0.16), (fx + sg * rx * 0.2, fy - ry * 0.32), (fx + sg * rx * 0.36, fy - ry * 0.34), (fx + sg * rx * 0.5, fy - ry * 0.2)]
        out.append(taper(catmull(br, 5), rx * 0.06, rx * 0.025, SUMI_INK, 0.95))
        for k in range(5):
            t = 0.45 + k * 0.1
            px, py = fx + sg * rx * (0.06 + 0.44 * t), fy - ry * (0.16 + 0.3 * math.sin(math.pi * t * 0.9))
            out.append(taper([(px, py), (px + sg * rx * 0.05, py - ry * 0.07)], rx * 0.025, 0.6, SUMI_INK, 0.85))
        # eyes
        ex, ey = fx + sg * rx * 0.24, fy - ry * 0.02
        er = rx * 0.14
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{er:.1f}" fill="#FFFFFF"/>')
        out.append(ink(smooth_closed(ell_pts(ex, ey, er, er, 0, 360, 20)), SUMI_INK, 3.2, seed + 4 + sg, 1, 0.9))
        if (sg < 0 and eyes >= 1) or (sg > 0 and eyes >= 2):
            out.append(f'<path d="{blob(ex + 1, ey + 1, er * 0.68, er * 0.68, seed + 6, 0.1, 12)}" fill="{SUMI_INK}"/>')
            out.append(f'<circle cx="{ex - er * 0.25:.1f}" cy="{ey - er * 0.28:.1f}" r="{er * 0.16:.1f}" fill="#FFFFFF" opacity="0.85"/>')
        # beard (turtle): a fan of curved brush strokes framing each cheek
        for k in range(7):
            t = k / 6
            x0 = fx + sg * rx * (0.12 + 0.3 * t)
            y0 = fy + ry * (0.12 + 0.08 * math.sin(math.pi * t))
            out.append(taper([(x0, y0), (x0 + sg * rx * 0.05, y0 + ry * 0.1), (x0 + sg * rx * (0.02 + 0.06 * t), y0 + ry * 0.2)], rx * 0.032, 0.8, "#2E2826", 0.85))
    # nose and mustache, small red mouth
    out.append(f'<path d="{blob(fx, fy + ry * 0.1, rx * 0.045, rx * 0.035, seed + 7, 0.1, 8)}" fill="#D84A3A"/>')
    for sg in (-1, 1):
        out.append(taper(catmull([(fx + sg * rx * 0.01, fy + ry * 0.17), (fx + sg * rx * 0.1, fy + ry * 0.13), (fx + sg * rx * 0.19, fy + ry * 0.2), (fx + sg * rx * 0.22, fy + ry * 0.27)], 4), rx * 0.055, rx * 0.01, SUMI_INK, 0.92))
    out.append(taper([(fx - rx * 0.05, fy + ry * 0.29), (fx, fy + ry * 0.32), (fx + rx * 0.05, fy + ry * 0.29)], 3, 3, "#B8302A", 0.9))
    return "".join(out)


@design("daruma")
def daruma():
    D = Doc2("jp-dr")
    out = [paper(D.nid(), "#F2E2C2", FLECK, 601)]
    out.append(blooms(6, ["#E8C890", "#F2D8A8", "#D8B070"], 7, (40, 40, 560, 460), (120, 200), (0.12, 0.2)))
    out.append(soft_glow(D, 300, 360, 260, "#FFF2C8", 0.5))
    # a wooden shelf
    out.append(wood_planks(D, 516, 600, 602, HINOKI, 2))
    out.append(f'<rect y="510" width="600" height="10" fill="#7A4A22" opacity="0.6"/>')
    # small second daruma (blank eyes) behind, for a wish not yet made
    out.append(daruma_doll(D, 476, 466, 58, 62, 603, eyes=0))
    out.append(daruma_doll(D, 286, 380, 150, 158, 604, eyes=1))
    # the brush that painted the eye, and its ink stone
    ist = [(410, 534), (524, 526), (530, 560), (414, 568)]
    out.append(cast(D, 470, 568, 66, 8, strength=0.4, seed=5))
    out.append(painted(D, densify(ist, 16), ("#6A6A70", "#2E2E34", "#121216"), 605, sdir=(0.3, 1), sk=0.15, angle=0, n=12, inkw=1.4, hi=0.35))
    out.append(f'<path d="{blob(482, 544, 34, 9, 606, 0.1, 12)}" fill="#0A0A0E"/><path d="{blob(474, 541, 12, 3, 607, 0.2, 8)}" fill="#FFFFFF" opacity="0.4"/>')
    out.append(taper([(70, 570), (200, 548), (300, 540)], 12, 9, "#B8803A"))
    out.append(taper([(70, 570), (200, 548)], 4, 3, "#E8C080", 0.6))
    out.append(taper([(296, 540), (316, 537), (342, 538)], 12, 1, SUMI_INK))
    out.append(f'<path d="M 288 535 L 288 547" stroke="#5A3A1A" stroke-width="3"/>')
    # lettering
    out.append(letters(D, 300, 140, "daruma", SERIF_IT, 128, "#B8241E", ["#D8402A", "#8A140E", "#E8604A"], 608, max_w=380,
                       shadow="#FFF6E0", soff=(0.02, 0.035), angle=-40, hi="#FFB8A0"))
    out.append(label(300, 186, "FALL SEVEN TIMES, STAND UP EIGHT", JOS, 19, "#3A2A20", ls=3, max_w=440))
    return finish_b(D, out, 609)


# ================================================================ 7. maneki-neko — the beckoning cat on its cushion
def koban(D, cx, cy, rx, ry, seed, rot_=0):
    """Oval gold coin with the hammered horizontal lines of an old koban."""
    pts = rot(ell_pts(cx, cy, rx, ry, 0, 360, 30), cx, cy, rot_)
    d = smooth_closed(pts)
    out = [painted(D, pts, ("#FFF0A8", "#E8B838", "#9A6A10"), seed, sdir=(0.6, 0.8), sk=0.16, angle=-40, n=14, inkw=1.6, inkc="#7A4A08", hi=0.5)]
    lines = []
    for k in range(-5, 6):
        y = cy + k * ry * 0.15
        lines.append(f'<path d="M {cx - rx:.1f} {y:.1f} L {cx + rx:.1f} {y:.1f}" stroke="#B8860E" stroke-width="{max(1, rx * 0.03):.1f}" opacity="0.55"/>')
    lines.append(f'<path d="{smooth_closed(rot(ell_pts(cx, cy, rx * 0.84, ry * 0.88, 0, 360, 30), cx, cy, rot_))}" fill="none" stroke="#9A6A10" stroke-width="1.4" opacity="0.6"/>')
    for sg in (-1, 1):
        lines.append(f'<path d="{hg.org_rect(cx - rx * 0.16, cy + sg * ry * 0.5 - ry * 0.1, rx * 0.32, ry * 0.2, seed + sg, 0.3, 6, 2)}" fill="none" stroke="#9A6A10" stroke-width="1.2" opacity="0.7"/>')
    out.append(f'<g transform="rotate({rot_} {cx} {cy})">' + clipped(D, smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, 30)), lines) + "</g>")
    out.append(f'<path d="{blob(cx - rx * 0.4, cy - ry * 0.45, rx * 0.18, ry * 0.12, seed + 3, 0.2, 8, -30)}" fill="#FFFFFF" opacity="0.6"/>')
    return "".join(out)


def ceramic(D, pts, seed, sdir=(0.7, 0.4), n=20, inkw=2):
    """Glazed white porcelain: cool blue-grey shadow side and crisp specular highlights."""
    return painted(D, pts, ("#FFFFFF", "#F8F4EE", "#B4B8CC"), seed, sdir=sdir, sk=0.16, angle=-70, n=n, cols=["#FFFFFF", "#DCDCE8", "#FFFFFF"],
                   inkw=inkw, inkc="#5A4A48", inkop=0.7, hi=0.6, hik=0.08)


@design("maneki-neko")
def maneki_neko():
    D = Doc2("jp-mn")
    out = [sky(D, [(0, "#C83A2A"), (1, "#8A1A14")], 701, 600, ["#D8503A", "#7A1410", "#E06A4A"], 90, angle=-70, sop=(0.08, 0.18))]
    out.append(seigaiha(D, "M 0 0 L 600 0 L 600 600 L 0 600 Z", (0, 0, 600, 600), 34, ["#B8301E", "#A82A1A"], "#E8A040", 702, rings=4, lw=1.4))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#C8301E", 0.85), (0.55, "#C8301E", 0.55), (1, "#5A0A08", 0.6)], 0.5, 0.52, 0.7)}"/>')
    out.append(soft_glow(D, 300, 360, 260, "#FFD890", 0.45))
    rnd = random.Random(703)
    cx = 300
    out.append('<g transform="translate(300 548) scale(0.88) translate(-300 -548)">')
    # zabuton cushion with tassels
    cu = [(120, 492), (480, 492), (520, 540), (80, 540)]
    out.append(cast(D, 300, 548, 240, 18, "#2A0404", 0.6, 704))
    out.append(painted(D, round_poly(cu, 16), ("#9A6AD0", "#5A2A98", "#2A0E50"), 705, sdir=(0.3, 1), sk=0.15, angle=0, n=40, inkw=2, hi=0.35))
    for k in range(5):
        x = 140 + k * 80
        out.append(pline([(x, 500), (x - 4 + k * 2, 534)], "#E8B838", 1.4, 706 + k, 0.6, 1))
    for x, y in ((92, 538), (508, 538)):
        out.append(f'<path d="{blob(x, y + 12, 7, 12, int(x), 0.1, 8)}" fill="#E8B838"/>' + ink(blob(x, y + 12, 7, 12, int(x), 0.1, 8), "#7A4A08", 1, 1, 1, 0.6))
    # body
    body = [(cx, 330), (cx + 70, 344), (cx + 104, 400), (cx + 116, 470), (cx + 104, 506), (cx - 104, 506), (cx - 116, 470), (cx - 104, 400), (cx - 70, 344)]
    out.append(ceramic(D, body, 707, n=30))
    bd = smooth_closed(body)
    out.append(clipped(D, bd, [f'<path d="{blob(cx + 60, 450, 40, 34, 708, 0.2, 12)}" fill="#E8902A" opacity="0.85"/>',
                               f'<path d="{blob(cx - 84, 416, 22, 30, 709, 0.2, 12)}" fill="#2A2420" opacity="0.85"/>',
                               shade_over(D, bd, "#3A3A6A", 0.35, 0, 0, 1, 0.3, 0.5)]))
    # hind paws
    for sg in (-1, 1):
        out.append(ceramic(D, blob_pts(cx + sg * 70, 500, 30, 14, 710 + sg, 0.05, 12), 711 + sg, n=6, inkw=1.6))
        for k in (-1, 0, 1):
            out.append(pline([(cx + sg * 70 + k * 9, 498), (cx + sg * 70 + k * 9, 508)], "#8A7A78", 1.2, 712, 0.7, 1))
    # raised paw (the cat's left) beckoning beside the head
    arm = [(cx + 62, 380), (cx + 92, 340), (cx + 112, 280), (cx + 128, 232), (cx + 150, 224), (cx + 158, 244), (cx + 140, 300), (cx + 116, 372), (cx + 92, 400)]
    out.append(ceramic(D, arm, 713, n=16))
    pw = blob_pts(cx + 140, 220, 26, 24, 714, 0.05, 14)
    out.append(ceramic(D, pw, 715, n=8, inkw=1.8))
    for k in (-1, 0, 1):
        out.append(pline([(cx + 140 + k * 9, 202), (cx + 140 + k * 8, 214)], "#8A7A78", 1.4, 716 + k, 0.7, 1))
    out.append(f'<path d="{blob(cx + 140, 226, 9, 7, 717, 0.1, 8)}" fill="#F4A0A8"/>')
    # head
    head = [(cx - 96, 268), (cx - 88, 222), (cx - 50, 196), (cx, 190), (cx + 50, 196), (cx + 88, 222), (cx + 96, 268), (cx + 80, 312), (cx + 40, 336), (cx - 40, 336), (cx - 80, 312)]
    for sg in (-1, 1):
        ear = [(cx + sg * 84, 230), (cx + sg * 92, 160), (cx + sg * 40, 200)]
        out.append(ceramic(D, ear, 718 + sg, n=6, inkw=1.8))
        out.append(f'<path d="{smooth_closed([(cx + sg * 80, 222), (cx + sg * 86, 176), (cx + sg * 52, 202)])}" fill="#F4A0A8"/>')
    out.append(ceramic(D, head, 720, n=26))
    hd = smooth_closed(head)
    out.append(clipped(D, hd, [f'<path d="{blob(cx + 62, 216, 38, 30, 721, 0.2, 12)}" fill="#E8902A" opacity="0.9"/>',
                               f'<path d="{blob(cx - 70, 206, 26, 22, 722, 0.2, 12)}" fill="#2A2420" opacity="0.88"/>']))
    # face: big gold eyes, red brows, pink nose, the little w mouth, whiskers
    for sg in (-1, 1):
        ex, ey = cx + sg * 40, 262
        out.append(f'<path d="{blob(ex, ey, 17, 18, 723 + sg, 0.05, 12)}" fill="#F6C83A"/>')
        out.append(f'<path d="{blob(ex, ey + 1, 6, 15, 724 + sg, 0.05, 10)}" fill="#1A1210"/>')
        out.append(f'<circle cx="{ex - 5:.1f}" cy="{ey - 7:.1f}" r="3.6" fill="#FFFFFF"/>')
        out.append(ink(blob(ex, ey, 17, 18, 723 + sg, 0.05, 12), "#1A1210", 2.4, 725, 1, 0.9))
        out.append(taper([(ex - sg * 14, ey - 30), (ex + sg * 4, ey - 36), (ex + sg * 16, ey - 30)], 2, 5, "#C8281E", 0.9))
        for k in range(3):
            out.append(taper([(cx + sg * 30, 296 + k * 6), (cx + sg * 64, 290 + k * 9), (cx + sg * 92, 286 + k * 13)], 2, 0.6, "#3A2A28", 0.75))
    out.append(f'<path d="{smooth_closed([(cx - 8, 284), (cx + 8, 284), (cx, 294)])}" fill="#E86A7A"/>')
    out.append(pline([(cx - 14, 300), (cx - 7, 306), (cx, 298), (cx + 7, 306), (cx + 14, 300)], "#3A2A28", 2, 726, 0.9, 1))
    # red collar, gold bell
    col = [(cx - 74, 334), (cx, 352), (cx + 74, 334), (cx + 76, 346), (cx, 366), (cx - 76, 346)]
    out.append(painted(D, col, AKA, 727, sdir=(0.3, 1), sk=0.2, angle=0, n=10, inkw=1.6, hi=0.4))
    for k in range(8):
        x = cx - 64 + k * 18
        out.append(f'<circle cx="{x:.1f}" cy="{344 + 10 * math.sin((k + 0.5) / 8 * math.pi) * 0.9:.1f}" r="1.8" fill="#F6D27A" opacity="0.8"/>')
    bp = blob_pts(cx, 376, 17, 16, 728, 0.04, 14)
    out.append(painted(D, bp, ("#FFF0A8", "#E8B838", "#9A6A10"), 728, sdir=(0.6, 0.8), sk=0.2, n=8, inkw=1.6, inkc="#7A4A08", hi=0.5))
    out.append(f'<path d="M {cx - 15} 374 L {cx + 15} 374" stroke="#7A4A08" stroke-width="1.6"/><circle cx="{cx}" cy="382" r="3" fill="#5A3408"/><path d="M {cx} 382 L {cx} 391" stroke="#5A3408" stroke-width="1.8"/>')
    # the other paw holding a koban against the chest
    out.append(koban(D, cx - 46, 438, 38, 56, 729, -10))
    out.append(ceramic(D, blob_pts(cx - 30, 412, 24, 20, 730, 0.05, 12), 731, n=6, inkw=1.8))
    for k in (-1, 0, 1):
        out.append(pline([(cx - 30 + k * 8, 396), (cx - 28 + k * 7, 406)], "#8A7A78", 1.3, 732 + k, 0.7, 1))
    # coins on the cushion, sparkles
    out.append(koban(D, 166, 500, 18, 12, 733, 0))
    out.append(koban(D, 440, 506, 16, 11, 734, 14))
    out.append("</g>")
    for x, y, r in ((480, 226, 9), (128, 300, 7), (500, 400, 7), (96, 420, 6), (196, 236, 5)):
        out.append(sparkle(x, y, r, "#FFE8A0", 0.95))
    # lettering
    out.append(letters(D, 300, 128, "maneki-neko", SERIF_IT, 100, "#FFF2D8", ["#FFFFFF", "#F6DCB0", "#FFE8C0"], 735, max_w=450,
                       shadow="#5A0A08", soff=(0.02, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 166, "BECKONING GOOD LUCK", "#F6C85A", font=JOS, size=19, ls=6, line_w=30, gap=12))
    return finish_b(D, out, 736, "#3A0A08", 0.7)


# ================================================================ 8. koi — two carp circling in a lily pond, seen from above
def koi(D, spine, W, seed, kind="kohaku"):
    """A koi from above: body built around a curved spine (head first), scale net, patches, fins and a flowing tail."""
    rnd = random.Random(seed)
    pts = catmull(spine, 6)
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        t = i / (n - 1)
        a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        if t < 0.3:
            w = W * 0.5 * (0.55 + 0.45 * math.sin(math.pi * 0.5 * t / 0.3)) * (math.sqrt(max(0, t / 0.06)) if t < 0.06 else 1)
        else:
            u = (t - 0.3) / 0.7
            w = W * 0.5 * (0.12 + 0.88 * (1 - u) ** 1.5)
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    body = left + right[::-1]
    d = smooth_closed(body)
    out = [f'<path d="{smooth_closed([(x + 14, y + 18) for x, y in body])}" fill="#0A2A28" opacity="0.3"/>']
    # tail fin: two soft lobes fanning from the tail
    tx, ty = pts[-1]
    px, py = pts[-6]
    ang = math.atan2(ty - py, tx - px)
    fin_c = {"kohaku": ("#FFFFFF", "#F6EEE8", "#C8B8B8"), "ogon": ("#FFF0A8", "#F2C040", "#B88010"), "showa": ("#FFFFFF", "#F0E8E4", "#B8A8A8")}[kind]
    for sg in (-1, 1):
        a = ang + sg * 0.55
        tip = (tx + math.cos(a) * W * 1.15, ty + math.sin(a) * W * 1.15)
        mid = (tx + math.cos(ang) * W * 0.62, ty + math.sin(ang) * W * 0.62)
        fp = [(tx - math.cos(ang) * 6, ty - math.sin(ang) * 6), (tx + math.cos(ang + sg * 0.35) * W * 0.7, ty + math.sin(ang + sg * 0.35) * W * 0.7), tip,
              (tx + math.cos(ang + sg * 0.3) * W * 0.85, ty + math.sin(ang + sg * 0.3) * W * 0.85), mid]
        out.append(f'<path d="{smooth_closed(fp)}" fill="{fin_c[1]}" opacity="0.7"/>' + ink(smooth_closed(fp), fin_c[2], 1, seed + sg, 1, 0.45))
        for k in range(6):
            aa = ang + sg * (0.08 + k * 0.09)
            out.append(pline([(tx, ty), (tx + math.cos(aa) * W * 0.95, ty + math.sin(aa) * W * 0.95)], fin_c[2], 0.9, seed + k, 0.45, 1))
    # pectoral fins
    i = int(n * 0.24)
    for sg, side in ((1, left), (-1, right)):
        bx, by = side[i]
        hx, hy = pts[i]
        ox, oy = bx - hx, by - hy
        ol = math.hypot(ox, oy) or 1
        bk = pts[min(n - 1, i + 7)]
        bdx, bdy = bk[0] - hx, bk[1] - hy
        bl = math.hypot(bdx, bdy) or 1
        fx, fy = bx + ox / ol * W * 0.42 + bdx / bl * W * 0.32, by + oy / ol * W * 0.42 + bdy / bl * W * 0.32
        fp = [(bx, by), (bx + ox / ol * W * 0.3, by + oy / ol * W * 0.3), (fx, fy), (fx + bdx / bl * W * 0.12 - ox / ol * W * 0.1, fy + bdy / bl * W * 0.12 - oy / ol * W * 0.1), (side[i + 4][0], side[i + 4][1])]
        out.append(f'<path d="{smooth_closed(fp)}" fill="{fin_c[1]}" opacity="0.75"/>' + ink(smooth_closed(fp), fin_c[2], 1, seed, 1, 0.5))
        for k in range(3):
            out.append(pline([(bx, by), (fx + (k - 1) * 4, fy + (k - 1) * 4)], fin_c[2], 0.8, seed + k, 0.4, 1))
    base = {"kohaku": ("#FFFFFF", "#FBF6F0", "#C8B8B4"), "ogon": ("#FFF2A0", "#F2BE38", "#B07A10"), "showa": ("#FFFFFF", "#F6F0EC", "#B8ACA8")}[kind]
    out.append(painted(D, body, base, seed, sdir=(0.5, 0.8), sk=0.12, angle=math.degrees(ang), n=30, inkw=1.6, inkc="#5A3A30", inkop=0.6, hi=0.4))
    inner = []
    if kind in ("kohaku", "showa"):
        for k, t in enumerate((0.12, 0.38, 0.62)):
            j = int(t * (n - 1))
            x, y = pts[j]
            inner.append(f'<path d="{blob(x + rnd.uniform(-4, 4), y + rnd.uniform(-4, 4), W * rnd.uniform(0.32, 0.45), W * rnd.uniform(0.25, 0.4), seed + k, 0.3, 12, rnd.uniform(0, 180))}" fill="#E0381E"/>')
    if kind == "showa":
        for k, t in enumerate((0.25, 0.5, 0.78)):
            j = int(t * (n - 1))
            x, y = pts[j]
            inner.append(f'<path d="{blob(x + rnd.uniform(-6, 6), y + rnd.uniform(-6, 6), W * 0.25, W * 0.16, seed + 9 + k, 0.35, 12, rnd.uniform(0, 180))}" fill="#1A1414"/>')
    # scale net
    for i2 in range(3, n - 3, 2):
        x, y = pts[i2]
        for sg in (-0.25, 0.0, 0.25):
            lx, ly = left[i2]
            sx, sy = x + (lx - x) * sg * 2.6, y + (ly - y) * sg * 2.6
            inner.append(f'<path d="M {sx - 3:.1f} {sy:.1f} q 3 3 6 0" stroke="{dk(base[1], 0.25)}" stroke-width="0.9" fill="none" opacity="0.45" transform="rotate({math.degrees(ang):.0f} {sx:.1f} {sy:.1f})"/>')
    inner.append(taper(pts[2:int(n * 0.7)], 3, 1, "#FFFFFF", 0.55))
    out.append(clipped(D, d, inner))
    # head: eyes and barbels
    hx, hy = pts[0]
    nx_, ny_ = pts[1][0] - hx, pts[1][1] - hy
    hl = math.hypot(nx_, ny_) or 1
    ux, uy = -nx_ / hl, -ny_ / hl
    for sg, side in ((1, left), (-1, right)):
        ex, ey = side[2]
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="3" fill="#1A1414"/>')
        bx, by = side[0]
        out.append(pline([(bx, by), (bx + ux * 8 + (bx - hx) * 0.3, by + uy * 8 + (by - hy) * 0.3)], "#C8A8A0", 1.2, seed, 0.8, 1))
    return "".join(out)


def lily_pad(D, cx, cy, r, ang, seed, pal=("#9AD07A", "#4E9A4A", "#1E5A2A")):
    pts = []
    for i in range(40):
        a = math.radians(ang + 14 + i * 332 / 39)
        rr = r * (1 + 0.04 * math.sin(i * 1.3 + seed))
        pts.append((cx + rr * math.cos(a), cy + rr * 0.9 * math.sin(a)))
    pts.append((cx, cy))
    out = [f'<path d="{smooth_closed([(x + 8, y + 10) for x, y in pts])}" fill="#0A2A28" opacity="0.28"/>']
    out.append(painted(D, pts, pal, seed, sdir=(0.5, 0.8), sk=0.1, angle=ang, n=int(r * 0.6), inkw=1.4, inkc="#1E4A22", hi=0.35))
    for k in range(9):
        a = math.radians(ang + 30 + k * 36)
        out.append(pline([(cx, cy), (cx + math.cos(a) * r * 0.85, cy + math.sin(a) * r * 0.78)], pal[0], 1.1, seed + k, 0.5, 1))
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.3, r * 0.22, r * 0.1, seed, 0.2, 8, -20)}" fill="#FFFFFF" opacity="0.35"/>')
    return "".join(out)


def water_lily(D, cx, cy, r, seed, pal=("#FFE8F0", "#F4A8C4", "#C85A84")):
    out = []
    rnd = random.Random(seed)
    for ring, (n, L, op) in enumerate(((10, 1.0, 1), (8, 0.75, 1), (6, 0.5, 1))):
        for i in range(n):
            a = math.radians(i * 360 / n + ring * 17 + rnd.uniform(-6, 6))
            tip = (cx + math.cos(a) * r * L, cy + math.sin(a) * r * L * 0.85)
            nx, ny = -math.sin(a), math.cos(a)
            w = r * 0.18 * L
            pts = [(cx + nx * w * 0.4, cy + ny * w * 0.4), (cx + math.cos(a) * r * L * 0.55 + nx * w, cy + math.sin(a) * r * L * 0.5 + ny * w), tip,
                   (cx + math.cos(a) * r * L * 0.55 - nx * w, cy + math.sin(a) * r * L * 0.5 - ny * w), (cx - nx * w * 0.4, cy - ny * w * 0.4)]
            out.append(painted(D, pts, pal if ring < 2 else (lt(pal[0], 0.3), lt(pal[1], 0.3), pal[1]), seed + ring * 20 + i, sdir=(0.5, 0.8), sk=0.15, angle=math.degrees(a), n=3,
                               inkw=0.8, inkc=pal[2], inkop=0.5, hi=0.4))
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.18:.1f}" fill="#F6C83A"/>')
    out.append(specks(seed, (cx - r * 0.15, cy - r * 0.15, cx + r * 0.15, cy + r * 0.15), ["#E89A1A", "#FFF0A0"], 10, (1, 1.8), (0.8, 1)))
    return "".join(out)


@design("koi")
def koi_pond():
    D = Doc2("jp-ko")
    out = [f'<rect width="600" height="600" fill="{D.rad([(0, "#5AA8A0"), (0.6, "#2E7A78"), (1, "#14484E")], 0.45, 0.4, 0.75)}"/>']
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 600, 600), ["#7AC8B8", "#1E5A5E", "#8AD0C0"], 801, n=140, angle=-10, length=(60, 180), width=(4, 12), opacity=(0.06, 0.16), curve=0.3))
    rnd = random.Random(802)
    # pebbles on the pond floor, deep and blurred
    for _ in range(70):
        x, y, r = rnd.uniform(0, 600), rnd.uniform(0, 600), rnd.uniform(6, 18)
        out.append(f'<path d="{blob(x, y, r, r * 0.75, rnd.randint(0, 999), 0.15, 10)}" fill="{rnd.choice(["#3E8A84", "#246A6A", "#5A9A90"])}" opacity="{rnd.uniform(0.25, 0.5):.2f}"/>')
    # caustic light web
    for _ in range(40):
        x, y = rnd.uniform(0, 600), rnd.uniform(0, 600)
        out.append(f'<path d="M {x:.1f} {y:.1f} q {rnd.uniform(10, 30):.1f} {rnd.uniform(-12, 12):.1f} {rnd.uniform(30, 60):.1f} {rnd.uniform(-6, 6):.1f}" stroke="#C8F0E0" stroke-width="{rnd.uniform(1, 2.4):.1f}" fill="none" opacity="{rnd.uniform(0.15, 0.35):.2f}"/>')
    # two koi circling each other
    ring = lambda angs, r=176: [(300 + r * math.cos(math.radians(a)), 304 + r * 0.92 * math.sin(math.radians(a))) for a in angs]
    out.append(koi(D, ring((-22, -50, -78, -106, -132, -150)), 66, 803, "kohaku"))
    out.append(koi(D, ring((158, 130, 102, 74, 48, 30)), 62, 804, "ogon"))
    # ripple rings
    for x, y, r in ((520, 140, 26), (120, 140, 20), (470, 470, 18)):
        for k in range(3):
            out.append(f'<ellipse cx="{x}" cy="{y}" rx="{r + k * 12}" ry="{(r + k * 12) * 0.6:.1f}" fill="none" stroke="#E8FFF8" stroke-width="{2 - k * 0.5:.1f}" opacity="{0.5 - k * 0.14:.2f}"/>')
    # lily pads and a flower floating above
    out.append(lily_pad(D, 70, 80, 70, 40, 805))
    out.append(lily_pad(D, 548, 300, 46, 200, 806, ("#B8D888", "#6AAA4A", "#2A6A2A")))
    out.append(lily_pad(D, 520, 530, 74, 120, 807))
    out.append(lily_pad(D, 72, 530, 50, -60, 808, ("#B8D888", "#6AAA4A", "#2A6A2A")))
    out.append(lily_pad(D, 540, 64, 40, 160, 812, ("#B8D888", "#6AAA4A", "#2A6A2A")))
    out.append(water_lily(D, 492, 516, 40, 809))
    out.append(water_lily(D, 96, 90, 30, 810, ("#FFFFFF", "#F6E8F0", "#C8A0B8")))
    for k in range(7):
        out.append(sakura_petal(D, rnd.uniform(180, 420), rnd.uniform(400, 470) if k % 2 else rnd.uniform(60, 110), 10, rnd.uniform(0, 360), 811 + k, op=0.85))
    # lettering
    out.append(letters(D, 300, 318, "koi", SERIF_IT, 168, "#FFF6E8", ["#FFFFFF", "#F2E0C8", "#FFF0D8"], 820, max_w=280,
                       shadow="#0E3A3A", soff=(0.02, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 362, "SWIM UPSTREAM", "#FFE0A0", font=JOS, size=19, ls=6, line_w=18, gap=10))
    return finish_b(D, out, 821, "#FFFFFF", 0.5)


# ================================================================ 9. ganbatte! — carp streamers flying high on Children's Day
def koinobori(D, x0, y0, L, H, seed, pal, scale_c, eye_c="#F6C83A", wave=10, phase=0.0):
    """Carp streamer: a cloth tube flying from its mouth ring at (x0, y0) (top of the mouth), rippling in the wind."""
    rnd = random.Random(seed)
    n = 40
    top, bot, mid = [], [], []
    for i in range(n + 1):
        t = i / n
        x = x0 + L * t
        cy = y0 + H / 2 + wave * math.sin(2 * math.pi * t * 1.3 + phase) * t + 10 * t
        h = H * (1 - 0.32 * t) if t < 0.86 else H * (1 - 0.32 * 0.86) * (1 - (t - 0.86) * 2.5)
        mid.append((x, cy))
        top.append((x, cy - h / 2))
        bot.append((x, cy + h / 2))
    # forked tail
    tx, ty = mid[-1]
    tail_top = [(tx + L * 0.08, ty - H * 0.42), (tx + L * 0.03, ty - H * 0.05)]
    tail_bot = [(tx + L * 0.03, ty + H * 0.05), (tx + L * 0.09, ty + H * 0.4)]
    outline = top + tail_top + [(tx - L * 0.02, ty)] + tail_bot + bot[::-1]
    d = smooth_closed(outline)
    out = [painted(D, outline, pal, seed, sdir=(0.2, 1), sk=0.14, angle=0, n=50, slen=(20, 60), sw=(1.5, 4), inkw=2, hi=0.4, hik=0.1)]
    inner = []
    # scales: rows of arcs opening toward the tail
    for row in range(-2, 3):
        for i in range(8, 35, 3):
            t = i / n
            x, cy = mid[i]
            h = top[i][1] - cy
            y = cy + row * (-h) * 0.38 + (i % 2) * 6
            r = H * 0.13 * (1 - 0.3 * t)
            inner.append(f'<path d="M {x:.1f} {y - r:.1f} A {r:.1f} {r:.1f} 0 0 1 {x:.1f} {y + r:.1f}" stroke="{scale_c}" stroke-width="{max(1.4, r * 0.22):.1f}" fill="none" opacity="0.85"/>')
            inner.append(f'<path d="M {x - r * 0.35:.1f} {y - r * 0.6:.1f} A {r * 0.7:.1f} {r * 0.7:.1f} 0 0 1 {x - r * 0.35:.1f} {y + r * 0.6:.1f}" stroke="{lt(pal[1], 0.3)}" stroke-width="1" fill="none" opacity="0.5"/>')
    # belly lighter, gill line
    inner.append(f'<path d="{smooth_open([(x, y - 2) for x, y in bot])} L {bot[-1][0]:.1f} {bot[-1][1] + 20:.1f} L {bot[0][0]:.1f} {bot[0][1] + 20:.1f} Z" fill="{lt(pal[1], 0.5)}" opacity="0.35"/>')
    gx, gy = mid[6]
    inner.append(f'<path d="M {gx:.1f} {top[6][1]:.1f} Q {gx + H * 0.22:.1f} {gy:.1f} {gx:.1f} {bot[6][1]:.1f}" stroke="{scale_c}" stroke-width="3" fill="none"/>')
    inner.append(f'<path d="M {gx + 4:.1f} {top[6][1]:.1f} Q {gx + H * 0.26:.1f} {gy:.1f} {gx + 4:.1f} {bot[6][1]:.1f}" stroke="{pal[2]}" stroke-width="1.6" fill="none" opacity="0.6"/>')
    # wind creases
    for i in (14, 22, 30):
        x = mid[i][0]
        inner.append(f'<path d="M {x:.1f} {top[i][1]:.1f} Q {x + 6:.1f} {mid[i][1]:.1f} {x - 2:.1f} {bot[i][1]:.1f}" stroke="{pal[2]}" stroke-width="5" fill="none" opacity="0.18"/>')
    out.append(clipped(D, d, inner))
    # tail stripes
    for k in range(3):
        out.append(pline([(tx + 2, ty - 4 * k), (tx + L * 0.07, ty - H * 0.36 + k * 6)], scale_c, 1.4, seed + k, 0.7, 1))
        out.append(pline([(tx + 2, ty + 4 * k), (tx + L * 0.08, ty + H * 0.36 - k * 6)], scale_c, 1.4, seed + k + 5, 0.7, 1))
    # eye
    ex, ey = mid[3][0] + 4, mid[3][1] - H * 0.08
    er = H * 0.2
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{er:.1f}" fill="#FFFFFF"/>')
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{er * 0.7:.1f}" fill="{eye_c}"/>')
    out.append(f'<circle cx="{ex + er * 0.12:.1f}" cy="{ey:.1f}" r="{er * 0.4:.1f}" fill="#141010"/>')
    out.append(f'<circle cx="{ex - er * 0.15:.1f}" cy="{ey - er * 0.25:.1f}" r="{er * 0.14:.1f}" fill="#FFFFFF"/>')
    out.append(ink(smooth_closed(ell_pts(ex, ey, er, er, 0, 360, 20)), "#141010", 1.6, seed, 1, 0.8))
    # mouth ring
    mx, my = x0, y0 + H / 2
    out.append(f'<ellipse cx="{mx:.1f}" cy="{my:.1f}" rx="{H * 0.12:.1f}" ry="{H * 0.5:.1f}" fill="{pal[2]}"/>')
    out.append(f'<ellipse cx="{mx:.1f}" cy="{my:.1f}" rx="{H * 0.12:.1f}" ry="{H * 0.5:.1f}" fill="none" stroke="#F6EEDC" stroke-width="4"/>')
    out.append(f'<path d="M {mx:.1f} {y0:.1f} L {mx - 14:.1f} {y0 - 6:.1f}" stroke="#4A3A2A" stroke-width="1.4"/>')
    return "".join(out)


@design("ganbatte")
def ganbatte():
    D = Doc2("jp-gb")
    out = [sky(D, [(0, "#3E86D0"), (0.6, "#8CC4EC"), (1, "#D8EEF6")], 901, 600, ["#6AA8E0", "#FFFFFF", "#A8D4F0"], 70, angle=-6, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 520, 80, 200, "#FFFBE0", 0.6))
    out.append(puff_cloud(D, 460, 410, 260, 902))
    out.append(puff_cloud(D, 150, 120, 150, 903, op=0.85, rows=1))
    out.append(puff_cloud(D, 560, 300, 120, 904, op=0.8, rows=1))
    # green hills and a farmhouse roof far below
    hl = ridge([(-20, 420), (140, 404), (300, 418), (460, 398), (620, 414)], 905, 8, 3)
    out.append(hill(D, hl, 600, ("#9ACB7A", "#5A9A4A", "#2E6A2A"), 906, inkw=1.4, n=90))
    for k, (x, r) in enumerate(((190, 18), (226, 14), (380, 16), (412, 22), (446, 15), (540, 18))):
        y = hl[min(len(hl) - 1, int(x / 640 * len(hl)))][1]
        out.append(dab_crown(D, x, y - r * 0.6, r, r * 0.8, [("#8AC070", "#4E8A40", "#2A5A26")], 907 + k, n=26, size=(3, 6), inkw=0))
    # the pole, arrow wheel and five-colour streamer
    px = 96
    out.append(taper([(px, 470), (px, 300), (px, 66)], 10, 6, "#C8A070"))
    out.append(taper([(px - 2, 470), (px - 2, 66)], 3, 2, "#F6E0B8", 0.7))
    out.append(ink(smooth_open([(px + 4, 470), (px + 3, 66)]), "#7A5030", 1.4, 910, 1, 0.5))
    for k in range(6):
        a = math.radians(k * 60 + 15)
        out.append(pline([(px, 70), (px + math.cos(a) * 22, 70 + math.sin(a) * 9)], "#5A3A20", 2, 911 + k, 0.9, 1))
        out.append(f'<path d="{blob(px + math.cos(a) * 22, 70 + math.sin(a) * 9, 5, 3, 912 + k, 0.1, 6, math.degrees(a))}" fill="#C8281E"/>')
    out.append(f'<circle cx="{px}" cy="58" r="7" fill="#E8B838"/><circle cx="{px - 2}" cy="56" r="2.4" fill="#FFF6C8"/>')
    cols = ["#2E6AC8", "#FFFFFF", "#D8382E", "#F6C21C", "#2E9A4A"]
    for k, c in enumerate(cols):
        y0 = 84 + k * 6.5
        pts = [(px + 4 + t * 330, y0 + 10 * math.sin(t * 7 + 1) * t + t * 8) for t in [i / 24 for i in range(25)]]
        out.append(taper(pts, 7, 5, c, 1))
    out.append(ink(smooth_open([(px + 4 + t * 330, 84 + 10 * math.sin(t * 7 + 1) * t + t * 8 - 3) for t in [i / 24 for i in range(25)]]), INK, 1, 913, 1, 0.4))
    # father, mother and child carp
    out.append(koinobori(D, px + 6, 132, 400, 82, 914, ("#4A4E5E", "#1E2230", "#08080E"), "#E8C878", wave=12, phase=0.4))
    out.append(koinobori(D, px + 6, 228, 330, 68, 915, ("#FF8A6A", "#E0402A", "#8A140E"), "#FFE0A0", wave=10, phase=1.4))
    out.append(koinobori(D, px + 6, 314, 250, 54, 916, ("#7AB0F0", "#2E6AC8", "#10307A"), "#FFFFFF", wave=8, phase=2.2))
    for x, y in ((530, 150), (556, 168)):
        out.append(bird_v(x, y, 7, "#3A4A6A", 0.8))
    # lettering
    out.append(letters(D, 300, 500, "ganbatte!", SERIF_IT, 116, "#C8281E", ["#E04A30", "#8A140E", "#F06A4A"], 917, max_w=430,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFB8A0"))
    out.append(ruled(300, 538, "YOU'VE GOT THIS", "#FFFFFF", font=JOS, size=20, ls=7, line_w=30, gap=12))
    return finish_b(D, out, 918, "#1A3A6A", 0.6)


# ================================================================ 10. itadakimasu — a packed bento from above
def tamagoyaki(D, x, y, w, h, seed, rot_=0):
    pts = rot(round_poly([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)], 7), x, y, rot_)
    d = smooth_closed(pts)
    out = [f'<path d="{smooth_closed([(px + 3, py + 4) for px, py in pts])}" fill="#3A1A08" opacity="0.3"/>',
           painted(D, pts, ("#FFF2A8", "#F6CE4A", "#C8901A"), seed, sdir=(0.5, 0.8), sk=0.1, angle=rot_, n=10, inkw=1.4, inkc="#9A6A10", hi=0.4)]
    sp = rot([(x + math.cos(t) * w * 0.035 * t, y + math.sin(t) * h * 0.035 * t) for t in [i * 0.35 for i in range(36)]], x, y, rot_)
    out.append(taper(sp, 1.2, 2.2, "#E8B030", 0.9))
    out.append(clipped(D, d, [f'<path d="{blob(x + w * 0.3, y - h * 0.4, w * 0.2, h * 0.12, seed, 0.3, 8)}" fill="#C88A30" opacity="0.45"/>']))
    return "".join(out)


def karaage(D, cx, cy, r, seed):
    rnd = random.Random(seed)
    pts = blob_pts(cx, cy, r, r * 0.82, seed, 0.16, 18)
    d = smooth_closed(pts)
    out = [f'<path d="{blob(cx + 4, cy + 5, r, r * 0.8, seed, 0.16, 16)}" fill="#3A1A08" opacity="0.3"/>',
           painted(D, pts, ("#F6C870", "#D08A2E", "#7A4410"), seed, sdir=(0.6, 0.8), sk=0.2, angle=-40, n=20, inkw=1.4, inkc="#5A2A08", hi=0.4)]
    cr = []
    for _ in range(int(r * 1.6)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.8
        cr.append(f'<path d="{blob(x, y, rnd.uniform(1.5, 4), rnd.uniform(1, 3), rnd.randint(0, 999), 0.3, 6)}" fill="{rnd.choice(["#FFE0A0", "#A8601A", "#F2B860"])}" opacity="0.7"/>')
    out.append(clipped(D, d, cr))
    return "".join(out)


def tako_sausage(D, cx, cy, s, seed, rot_=0):
    out = []
    legs = []
    for k in range(6):
        a = math.radians(rot_ + 40 + k * 20)
        base = (cx + math.cos(a) * s * 0.3, cy + math.sin(a) * s * 0.3)
        tip = (cx + math.cos(a) * s * 0.95, cy + math.sin(a) * s * 0.95)
        curl = (tip[0] + math.cos(a + 1.6) * s * 0.2, tip[1] + math.sin(a + 1.6) * s * 0.2)
        legs.append(taper([base, tip, curl], s * 0.2, s * 0.08, "#E8603A"))
    out.append("".join(legs))
    hd = rot(blob_pts(cx, cy, s * 0.42, s * 0.42, seed, 0.05, 14), cx, cy, rot_)
    out.append(painted(D, hd, ("#FF9A7A", "#E8503A", "#9A2010"), seed, sdir=(0.6, 0.8), sk=0.2, n=8, inkw=1.3, inkc="#7A1A0A", hi=0.45))
    for sg in (-1, 1):
        out.append(f'<ellipse cx="{cx + sg * s * 0.14:.1f}" cy="{cy - s * 0.05:.1f}" rx="{s * 0.05:.1f}" ry="{s * 0.07:.1f}" fill="#1A1010"/>')
    return "".join(out)


def broccoli(D, cx, cy, r, seed):
    rnd = random.Random(seed)
    out = [taper([(cx + r * 0.2, cy + r * 0.2), (cx + r * 0.9, cy + r * 0.8)], r * 0.5, r * 0.35, "#A8C878")]
    out.append(f'<path d="{blob(cx + 3, cy + 4, r, r * 0.9, seed, 0.15, 14)}" fill="#1E3A10" opacity="0.3"/>')
    for _ in range(int(r * 2.6)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.9
        lit = -(math.cos(a) * 0.6 + math.sin(a) * 0.8) * rr / r
        c = rnd.choice(["#8AC860", "#A8D878"]) if lit > 0.2 else (rnd.choice(["#2E6A20", "#1E4A14"]) if lit < -0.3 else rnd.choice(["#4E8A30", "#5A9A3A"]))
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(2.4, 4.4):.1f}" fill="{c}"/>')
    return "".join(out)


def cherry_tomato(D, cx, cy, r, seed):
    pts = blob_pts(cx, cy, r, r * 0.95, seed, 0.04, 14)
    out = [f'<path d="{blob(cx + 3, cy + 4, r, r, seed, 0.04, 12)}" fill="#3A0A04" opacity="0.3"/>',
           painted(D, pts, ("#FF8A6A", "#E8301E", "#8A0A06"), seed, sdir=(0.6, 0.8), sk=0.22, n=8, inkw=1.2, inkc="#6A0A04", hi=0.45)]
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.35, r * 0.22, r * 0.14, seed, 0.2, 8, -30)}" fill="#FFFFFF" opacity="0.75"/>')
    for k in range(5):
        a = math.radians(k * 72 - 90)
        out.append(taper([(cx, cy - r * 0.15), (cx + math.cos(a) * r * 0.42, cy - r * 0.15 + math.sin(a) * r * 0.3)], 3, 1, "#3E7A2A", 0.95))
    return "".join(out)


def lettuce(D, cx, cy, w, h, seed, rot_=0):
    pts = []
    for i in range(36):
        a = 2 * math.pi * i / 36
        rr = 1 + 0.12 * math.sin(a * 9 + seed)
        pts.append((cx + w / 2 * rr * math.cos(a), cy + h / 2 * rr * math.sin(a)))
    pts = rot(pts, cx, cy, rot_)
    out = [painted(D, pts, ("#C8EA90", "#7EBE4A", "#3E7A22"), seed, sdir=(0.5, 0.8), sk=0.12, angle=rot_, n=16, inkw=1.2, inkc="#2E5A18", hi=0.4)]
    for k in range(5):
        a = math.radians(rot_ - 60 + k * 30)
        out.append(pline([(cx, cy + h * 0.2), (cx + math.cos(a) * w * 0.4, cy + math.sin(a) * h * 0.45)], "#E8F6C8", 1.2, seed + k, 0.6, 1))
    return "".join(out)


@design("itadakimasu")
def itadakimasu():
    D = Doc2("jp-it")
    out = [paper(D.nid(), "#F6EEDC", FLECK, 1001)]
    # indigo checked cloth under the box
    cloth_d = pd([(-10, 236), (610, 222), (610, 610), (-10, 610)])
    out.append(gingham(D, cloth_d, "#27407A", "#F8F4EA", 20, 0, 0.5))
    out.append(strokes(D.nid(), cloth_d, (-40, 220, 610, 610), ["#FFFFFF", "#1E2E5A"], 1002, n=80, angle=-3, length=(30, 90), width=(1, 3), opacity=(0.08, 0.2)))
    out.append(pline([(-10, 236), (300, 230), (610, 222)], "#1E2E5A", 3, 1003, 0.6, 1))
    out.append(f'<g transform="rotate(-3 300 360)">')
    out.append(cast(D, 318, 380, 230, 160, "#0A1030", 0.45, 1004))
    # lacquer box: black outer, red inside, a divider
    bx0, by0, bx1, by1 = 96, 214, 504, 492
    outer = round_poly([(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)], 22)
    out.append(painted(D, outer, ("#5A4A4A", "#1E1616", "#060404"), 1005, sdir=(0.6, 0.8), sk=0.06, angle=0, n=40, inkw=2, hi=0.3))
    out.append(ink(smooth_closed(round_poly([(bx0 + 4, by0 + 4), (bx1 - 4, by0 + 4), (bx1 - 4, by1 - 4), (bx0 + 4, by1 - 4)], 18)), "#C8A050", 1.6, 1006, 1, 0.7))
    inner_r = [(bx0 + 14, by0 + 14), (bx1 - 14, by0 + 14), (bx1 - 14, by1 - 14), (bx0 + 14, by1 - 14)]
    out.append(f'<path d="{smooth_closed(round_poly(inner_r, 12))}" fill="#A8241A"/>')
    out.append(f'<path d="{smooth_closed(round_poly(inner_r, 12))}" fill="{D.lin([(0, "#000000", 0.35), (0.15, "#000000", 0), (1, "#000000", 0)], 0, 0, 0, 1)}"/>')
    # rice compartment
    rice = round_poly([(bx0 + 20, by0 + 20), (262, by0 + 20), (262, by1 - 20), (bx0 + 20, by1 - 20)], 10)
    rd = smooth_closed(rice)
    out.append(f'<path d="{rd}" fill="#F6F2EA"/>')
    rnd = random.Random(1007)
    grains = []
    for _ in range(520):
        x, y = rnd.uniform(bx0 + 18, 266), rnd.uniform(by0 + 18, by1 - 18)
        grains.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(3.4, 4.4):.1f}" ry="{rnd.uniform(1.8, 2.3):.1f}" fill="{rnd.choice(["#FFFFFF", "#FBF8F2", "#EEEAE4"])}" stroke="#D4CEC4" stroke-width="0.6" transform="rotate({rnd.uniform(0, 180):.0f} {x:.1f} {y:.1f})"/>')
    grains.append(shade_over(D, rd, "#5A5A70", 0.3, 0, 0, 1, 1, 0.5))
    for _ in range(40):
        x, y = rnd.uniform(130, 236), rnd.uniform(260, 300)
        grains.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="2.2" ry="1.2" fill="#1A1410" transform="rotate({rnd.uniform(0, 180):.0f} {x:.1f} {y:.1f})"/>')
    out.append(clipped(D, rd, grains))
    up = blob_pts(178, 382, 24, 22, 1008, 0.1, 14)
    out.append(painted(D, up, ("#F06A6A", "#C0202E", "#6A0A14"), 1008, sdir=(0.6, 0.8), sk=0.22, angle=-40, n=10, inkw=1.4, hi=0.35))
    out.append(f'<circle cx="170" cy="374" r="4" fill="#FFFFFF" opacity="0.8"/>')
    # divider
    out.append(f'<path d="{hg.org_rect(264, by0 + 14, 8, by1 - by0 - 28, 1009, 0.3, 10, 1)}" fill="#1E1616"/>')
    # right side: lettuce, tamagoyaki, karaage / sausages, broccoli, tomatoes
    out.append(lettuce(D, 390, 320, 230, 110, 1010, -6))
    for k, (x, y, a) in enumerate(((310, 268, 4), (350, 262, -2), (392, 270, 6))):
        out.append(tamagoyaki(D, x, y, 40, 54, 1011 + k, a))
    out.append(karaage(D, 450, 288, 36, 1015))
    out.append(karaage(D, 462, 352, 32, 1016))
    out.append(karaage(D, 410, 340, 30, 1017))
    out.append(tako_sausage(D, 314, 418, 50, 1018, 10))
    out.append(tako_sausage(D, 372, 446, 44, 1019, -20))
    out.append(broccoli(D, 446, 424, 30, 1020))
    out.append(cherry_tomato(D, 470, 466, 20, 1021))
    out.append(cherry_tomato(D, 318, 362, 18, 1022))
    out.append(cherry_tomato(D, 300, 468, 17, 1023))
    out.append("</g>")
    # chopsticks along the bottom
    out.append(f'<path d="{hg.org_rect(470, 528, 22, 10, 1024, 0.4, 6, 4)}" fill="#C8281E"/>')
    out.append(chopsticks(D, 110, 548, 500, 528, 1025, w=9, gap=11))
    # lettering
    out.append(letters(D, 300, 118, "itadakimasu", SERIF_IT, 100, "#A8241A", ["#C8402A", "#7A140E", "#E06A4A"], 1026, max_w=460,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFB8A0"))
    out.append(ruled(300, 162, "LET'S EAT!", "#27407A", font=JOS, size=22, ls=9, line_w=40, gap=14))
    return finish_b(D, out, 1027)


# ================================================================ 11. omiyage — a gift wrapped in a furoshiki
def nanten(D, x, y, seed, n=9, ang=-120):
    """A sprig of nandina: red berries on fine stalks with narrow, red-tipped leaves (an auspicious gift touch)."""
    rnd = random.Random(seed)
    out = []
    for k in range(5):
        a = ang + (k - 2) * 26
        out.append(leaf_simple(D, x, y, rnd.uniform(36, 50), 7, a, ("#B8C870", "#5A8A3A", "#2A4A1A") if k % 2 else ("#E8A070", "#B8502A", "#6A2010"), seed + k, vein=False, inkw=0.9))
    for k in range(n):
        a = math.radians(ang + 180 + rnd.uniform(-50, 50))
        L = rnd.uniform(10, 26)
        bx, by = x + math.cos(a) * L, y + math.sin(a) * L
        out.append(pline([(x, y), (bx, by)], "#6A5A2A", 1, seed + k, 0.8, 1))
        out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="5.2" fill="#D8241E"/><circle cx="{bx + 1.2:.1f}" cy="{by + 1.2:.1f}" r="3.4" fill="#8A0A0A" opacity="0.45"/>'
                   f'<circle cx="{bx - 1.6:.1f}" cy="{by - 1.6:.1f}" r="1.5" fill="#FFFFFF" opacity="0.85"/>')
    return "".join(out)


@design("omiyage")
def omiyage():
    D = Doc2("jp-om")
    out = [paper(D.nid(), "#F6E4DC", "#8A5A4A", 1101)]
    out.append(blooms(6, ["#F2C8C0", "#E8B0A8", "#FFE8E0"], 7, (40, 40, 560, 560), (120, 200), (0.12, 0.2)))
    out.append(soft_glow(D, 300, 380, 260, "#FFF6E8", 0.6))
    out.append('<g transform="translate(310 512) scale(1.16) translate(-310 -506)">')
    out.append(cast(D, 320, 506, 220, 22, "#5A2A2A", 0.5, 1102))
    pat_cols = ["#24386E", "#203266"]
    # the wrapped box in three-quarter view: front, right side, top
    front = round_poly([(150, 346), (418, 346), (420, 500), (148, 500)], 14)
    side = round_poly([(418, 346), (470, 316), (470, 468), (420, 500)], 10)
    top = round_poly([(150, 346), (418, 346), (470, 316), (204, 316)], 10)
    for pts, sh, sd in ((side, 0.45, (1, 0)), (front, 0.18, (0.6, 0.5)), (top, 0.0, (0.4, 1))):
        d = smooth_closed(pts)
        out.append(f'<path d="{d}" fill="{pat_cols[0]}"/>')
        out.append(seigaiha(D, d, bbox(pts), 15, pat_cols, "#F2EEE4", 1103, rings=3, lw=1.3))
        g = [f'<path d="{d}" fill="#0A1030" opacity="{sh}"/>'] if sh else []
        if pts is top:
            g.append(f'<path d="{d}" fill="#FFFFFF" opacity="0.12"/>')
        out.append(clipped(D, d, g + [shade_over(D, d, "#0A1030", 0.35, 0, 0, 1, 1, 0.5)]))
        out.append(ink(d, "#101838", 1.8, 1104, 1, 0.7))
    # soft tension folds running up to the knot
    kx, ky = 312, 318
    for a, b, c in (((168, 488), (230, 420), (kx - 34, ky + 18)), ((404, 490), (366, 420), (kx + 30, ky + 18))):
        out.append(taper([a, b, c], 16, 4, "#060A20", 0.22))
        out.append(taper([(a[0] - 8, a[1]), (b[0] - 8, b[1]), (c[0] - 6, c[1])], 6, 1, "#C8D0E8", 0.22))
    out.append(pline([(150, 346), (284, 348), (418, 346)], "#C8D0E8", 1.6, 1105, 0.4, 1))
    # the knot and its two broad, flaring ears
    for sg in (-1, 1):
        ear = [(kx + sg * 4, ky - 16), (kx + sg * 40, ky - 40), (kx + sg * 92, ky - 60), (kx + sg * 136, ky - 54), (kx + sg * 118, ky - 30),
               (kx + sg * 80, ky - 8), (kx + sg * 40, ky + 10), (kx + sg * 12, ky + 14)]
        d = smooth_closed(ear)
        out.append(f'<path d="{d}" fill="{pat_cols[0]}"/>')
        out.append(seigaiha(D, d, bbox(ear), 13, pat_cols, "#F2EEE4", 1106 + sg, rings=3, lw=1.2))
        out.append(clipped(D, d, [f'<path d="{d}" fill="#FFFFFF" opacity="{0.12 if sg < 0 else 0}"/>',
                                  shade_over(D, d, "#0A1030", 0.6, 0.5 + sg * 0.5, 0, 0.5 - sg * 0.5, 1, 0.35),
                                  taper([(kx + sg * 20, ky - 8), (kx + sg * 60, ky - 40), (kx + sg * 112, ky - 62)], 2, 8, "#060A20", 0.3),
                                  taper([(kx + sg * 30, ky + 2), (kx + sg * 76, ky - 24), (kx + sg * 120, ky - 50)], 5, 1, "#FFFFFF", 0.25)]))
        out.append(ink(d, "#101838", 1.8, 1108 + sg, 1, 0.75))
    knot = blob_pts(kx, ky, 46, 30, 1110, 0.12, 16)
    kd = smooth_closed(knot)
    out.append(f'<path d="{kd}" fill="{pat_cols[0]}"/>')
    out.append(seigaiha(D, kd, bbox(knot), 12, pat_cols, "#F2EEE4", 1111, rings=3, lw=1.2))
    out.append(clipped(D, kd, [shade_over(D, kd, "#0A1030", 0.55, 0, 0, 1, 1, 0.3),
                               taper([(kx - 30, ky - 4), (kx - 6, ky - 16), (kx + 20, ky - 14)], 2, 6, "#060A20", 0.45),
                               taper([(kx - 26, ky + 8), (kx, ky + 2), (kx + 30, ky + 10)], 2, 6, "#060A20", 0.4)]))
    out.append(ink(kd, "#101838", 2, 1112, 1, 0.8))
    # a sprig of nandina tucked in the knot
    out.append(nanten(D, kx - 30, ky - 16, 1113))
    out.append('</g>')
    # little gold sparkles
    for x, y, r in ((120, 270, 9), (504, 270, 8), (96, 440, 6), (520, 430, 7), (300, 222, 6)):
        out.append(sparkle(x, y, r, "#E8B838", 0.9))
    # lettering
    out.append(letters(D, 300, 140, "omiyage", SERIF_IT, 120, "#24386E", ["#3A5290", "#14244E", "#4A62A0"], 1114, max_w=400,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#A8B8E8"))
    out.append(ruled(300, 184, "A LITTLE SOMETHING FROM JAPAN", "#B8402A", font=JOS, size=17, ls=4, line_w=22, gap=10, max_w=400))
    return finish_b(D, out, 1115)


# ================================================================ 12. sento — the neighbourhood bathhouse, Fuji on the wall
def oke(D, cx, base, rx, h, seed, water=True, towel=False):
    """Hinoki wash bucket: stave body, two hoops, water inside; optional folded towel on the rim."""
    rnd = random.Random(seed)
    ry = rx * 0.3
    top = base - h
    body = [(cx - rx, top)] + [(cx - rx * 0.9, base - 4), (cx - rx * 0.6, base + ry * 0.5), (cx + rx * 0.6, base + ry * 0.5), (cx + rx * 0.9, base - 4), (cx + rx, top)] + ell_pts(cx, top, rx, ry, 0, 180, 12)[::-1][1:-1]
    body = [(cx - rx, top), (cx - rx * 0.9, base - 4), (cx - rx * 0.6, base + ry * 0.55), (cx + rx * 0.6, base + ry * 0.55), (cx + rx * 0.9, base - 4), (cx + rx, top)] + [(x, y) for x, y in ell_pts(cx, top, rx, ry, 0, 180, 12)][1:-1]
    d = smooth_closed(body)
    out = [cast(D, cx + 10, base + ry * 0.5, rx * 1.2, 10, strength=0.4, seed=seed)]
    out.append(painted(D, body, HINOKI, seed, sdir=(0.9, 0.2), sk=0.2, angle=-90, n=30, inkw=1.8, hi=0.45))
    st = []
    for k in range(-5, 6):
        x = cx + k * rx * 0.18
        st.append(f'<path d="M {x:.1f} {top:.1f} L {cx + (x - cx) * 0.9:.1f} {base + ry * 0.5:.1f}" stroke="{HINOKI[2]}" stroke-width="1.2" opacity="0.6"/>')
    out.append(clipped(D, d, st + [shade_over(D, d, "#3A1A08", 0.4, 0, 0, 1, 0, 0.5)]))
    for t in (0.25, 0.78):
        y = top + h * t
        w = rx * (1 - 0.1 * t)
        hp = [(cx - w, y - 4)] + ell_pts(cx, y, w, ry * 0.9, 180, 0, 14)[::-1][::-1] + [(cx + w, y + 4)]
        hp = ell_pts(cx, y, w, ry * 0.9, 0, 180, 14)
        out.append(taper(hp, 7, 7, "#B8702E"))
        out.append(taper([(x, yy - 2) for x, yy in hp], 2, 2, "#F6C080", 0.7))
    rim = smooth_closed(ell_pts(cx, top, rx, ry, 0, 360, 28))
    out.append(f'<path d="{rim}" fill="{HINOKI[2]}"/>')
    inside = smooth_closed(ell_pts(cx, top + 2, rx * 0.9, ry * 0.75, 0, 360, 28))
    out.append(f'<path d="{inside}" fill="{"#7ACAD0" if water else "#C89A60"}"/>')
    if water:
        out.append(f'<path d="{blob(cx - rx * 0.2, top, rx * 0.4, ry * 0.25, seed, 0.2, 10)}" fill="#E8FFFF" opacity="0.6"/>')
    out.append(ink(rim, INK, 1.6, seed + 1, 1, 0.7))
    if towel:
        tw = [(cx - rx * 0.2, top - 6), (cx + rx * 0.7, top - 2), (cx + rx * 1.02, top + 4), (cx + rx * 1.05, top + h * 0.55), (cx + rx * 0.8, top + h * 0.6), (cx + rx * 0.78, top + 10), (cx - rx * 0.2, top + 6)]
        out.append(painted(D, tw, WHITE, seed + 3, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=14, inkw=1.4, hi=0.4))
        out.append(pline([(cx + rx * 0.85, top + 14), (cx + rx * 0.9, top + h * 0.5)], "#4A7AC8", 2, seed, 0.8, 1))
    return "".join(out)


@design("sento")
def sento():
    D = Doc2("jp-se")
    # the mural: bright painted sky, Fuji, sea with sails, pines
    out = [sky(D, [(0, "#2E7ACC"), (0.55, "#6AB0E8"), (1, "#C8E6F4")], 1201, 336, ["#4A90D8", "#FFFFFF", "#8AC4EC"], 60, angle=-3, sop=(0.08, 0.2))]
    out.append(puff_cloud(D, 120, 262, 150, 1202, rows=1))
    out.append(puff_cloud(D, 494, 252, 150, 1203, rows=1))
    c, top, base = 320, 196, 300
    fuji, f = fuji_shape(c, top, base, 26, 250, 1.8)
    fd = smooth_closed(fuji + [(700, 330), (-100, 330)])
    out.append(f'<path d="{fd}" fill="{D.lin([(0, "#5A78C0"), (1, "#3A58A0")])}"/>')
    sn = fuji_snow(c, top, f, 1204, half=110, depth=40)
    out.append(clipped(D, fd, [f'<path d="{smooth_closed([(c + 4, top), (700, base), (700, 340), (c + 40, 340)])}" fill="#1E3070" opacity="0.3"/>',
                               f'<path d="{smooth_closed(sn)}" fill="#FFFFFF"/>',
                               f'<path d="{smooth_closed([(c + 4, top - 6), (c + 160, 270), (c + 20, 300)])}" fill="#B8C8EC" opacity="0.6"/>',
                               strokes(D.nid(), fd, (0, top, 600, 330), ["#7A98D8", "#2A4888", "#FFFFFF"], 1205, n=60, angle=-75, length=(14, 40), width=(1.5, 3.5), opacity=(0.15, 0.4))]))
    out.append(ink(smooth_open(fuji), "#1E3070", 1.6, 1206, 1, 0.5))
    out.append(f'<rect y="290" width="600" height="46" fill="{D.lin([(0, "#2E7ACC"), (1, "#1E5AA8")])}"/>')
    out.append(wave_lines(1207, (0, 296, 600, 334), ["#FFFFFF", "#A8D8F8"], 40, (14, 34), 2, 2, (0.5, 0.9)))
    for x, s_ in ((150, 1.0), (470, 0.8)):
        out.append(f'<path d="M {x - 18 * s_} 306 Q {x} {312} {x + 18 * s_} 306 L {x + 14 * s_} 314 L {x - 14 * s_} 314 Z" fill="#5A3A2A"/>'
                   f'<path d="M {x - 2} 304 L {x - 2} {304 - 30 * s_} Q {x + 14 * s_} {304 - 16 * s_} {x + 12 * s_} 304 Z" fill="#FFF6E8"/>')
    out.append(jpine(D, 20, 336, 150, 1208, lean=0.5, pads=[(0.45, 1, 0.4), (0.7, 1, 0.5), (0.95, 1, 0.4)]))
    out.append(jpine(D, 590, 336, 130, 1209, lean=-0.5, pads=[(0.5, -1, 0.4), (0.8, -1, 0.45), (1.0, 0, 0.3)]))
    # tile grout over the whole mural wall
    grout = "".join(f'<path d="M {x} 0 L {x} 336" stroke="#FFFFFF" stroke-width="1.6" opacity="0.28"/>' for x in range(0, 601, 40))
    grout += "".join(f'<path d="M 0 {y} L 600 {y}" stroke="#FFFFFF" stroke-width="1.6" opacity="0.28"/>' for y in range(16, 337, 40))
    out.append(grout)
    # bath: water surface, tiled rim and front
    out.append(f'<rect y="336" width="600" height="52" fill="{D.lin([(0, "#8AD0D8"), (1, "#3E9AAA")])}"/>')
    out.append(wave_lines(1210, (0, 340, 600, 384), ["#FFFFFF", "#C8F0F0"], 40, (20, 50), 2, 2, (0.4, 0.8)))
    out.append(f'<rect y="336" width="600" height="6" fill="#1E4A70" opacity="0.35"/>')
    rim = hg.org_rect(-10, 382, 620, 16, 1211, 0.6, 20, 2)
    out.append(painted(D, densify([(-10, 382), (610, 382), (610, 398), (-10, 398)], 40), STONE, 1211, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=1.6, hi=0.4))
    tiles = []
    rnd = random.Random(1212)
    for y in range(398, 456, 14):
        for x in range(-7 if (y // 14) % 2 else 0, 600, 14):
            tiles.append(f'<rect x="{x + 1}" y="{y + 1}" width="12" height="12" rx="2" fill="{rnd.choice(["#3E86C8", "#5A9AD8", "#2E6AB0", "#6AAEE0"])}"/>')
    out.append(f'<rect y="398" width="600" height="58" fill="#E8F0F4"/>' + "".join(tiles))
    out.append(f'<rect y="398" width="600" height="58" fill="{D.lin([(0, "#000000", 0.25), (1, "#000000", 0)])}"/>')
    # floor: pale mosaic in perspective, wet sheen
    out.append(f'<rect y="456" width="600" height="144" fill="#E6E8EA"/>')
    vy = -300
    for k in range(-12, 13):
        x0 = 300 + k * 52
        out.append(f'<path d="M {300 + (x0 - 300) * (456 - vy) / (600 - vy):.1f} 456 L {x0:.1f} 600" stroke="#B8BEC6" stroke-width="1.6"/>')
    y, hgt = 456, 18
    while y < 600:
        out.append(f'<path d="M 0 {y:.1f} L 600 {y:.1f}" stroke="#B8BEC6" stroke-width="1.6"/>')
        y += hgt
        hgt *= 1.18
    out.append(f'<path d="{blob(300, 520, 200, 30, 1213, 0.2, 16)}" fill="#FFFFFF" opacity="0.45"/>')
    out.append(f'<rect y="456" width="600" height="144" fill="{D.lin([(0, "#5A6A80", 0.25), (1, "#5A6A80", 0)])}"/>')
    # steam rising off the water over the mural
    for k, x in enumerate((110, 470)):
        out.append(steam(x, 352, 90, 1214 + k, "#FFFFFF", 2, 34, 9, 0.22))
    out.append(mist_band(D, 334, 50, 1218, op=0.45))
    # buckets, a stool, soap
    out.append(oke(D, 150, 540, 58, 62, 1219, water=True, towel=True))
    out.append(oke(D, 236, 514, 38, 40, 1220, water=False))
    st = [(388, 506), (512, 500), (514, 516), (390, 522)]
    out.append(cast(D, 456, 560, 70, 9, strength=0.35, seed=1221))
    out.append(painted(D, [(398, 520), (412, 520), (412, 560), (398, 560)], HINOKI, 1222, sk=0.25, n=6, inkw=1.4, hi=0.3))
    out.append(painted(D, [(492, 516), (506, 516), (506, 556), (492, 556)], HINOKI, 1223, sk=0.25, n=6, inkw=1.4, hi=0.3))
    out.append(painted(D, densify(st, 20), HINOKI, 1224, sdir=(0.3, 1), sk=0.12, angle=0, n=14, inkw=1.6, hi=0.45))
    out.append(painted(D, round_poly([(440, 488), (476, 486), (478, 500), (442, 502)], 6), ("#FFFFFF", "#F2F8E8", "#B8C8A8"), 1225, sk=0.2, n=4, inkw=1.2, hi=0.5))
    # lettering on the mural sky
    out.append(letters(D, 300, 142, "sento", SERIF_IT, 126, "#FFFFFF", ["#FFFFFF", "#E8F4FC", "#F6FBFF"], 1226, max_w=360,
                       shadow="#163E80", soff=(0.02, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 180, "SCRUB FIRST, THEN SOAK", "#FFFFFF", font=JOS, size=19, ls=5, line_w=24, gap=12, line="#FFF2B0"))
    return finish_b(D, out, 1227, "#1E3050", 0.6)


def mist_band(D, y, h, seed, col="#FFFFFF", op=0.55):
    rnd = random.Random(seed)
    return "".join(f'<path d="{blob(rnd.uniform(-20, 620), y + rnd.uniform(-h * 0.3, h * 0.3), rnd.uniform(60, 140), rnd.uniform(10, 22), rnd.randint(0, 999), 0.2, 12)}" fill="{col}" opacity="{rnd.uniform(op * 0.4, op):.2f}"/>' for _ in range(12))


# ================================================================ 13. kyoto — a lantern-lit alley at dusk
def kimono_back(D, x, base, h, seed, kimono=("#9AB8E0", "#5A7AB8", "#2A4078"), obi=("#F6D27A", "#D8A030", "#8A5A10"), umbrella=AKA, flip=1, tint=None):
    """A woman in kimono seen from behind: hair in a bun, obi tied in a drum bow, a paper umbrella on her shoulder."""
    tn = (lambda c: mix(c, tint[0], tint[1])) if tint else (lambda c: c)
    k = h / 100
    P = lambda px, py: (x + px * k * flip, base + py * k)
    out = [f'<ellipse cx="{x:.1f}" cy="{base:.1f}" rx="{14 * k:.1f}" ry="{3 * k:.1f}" fill="#000000" opacity="0.3"/>']
    body = [P(-13, -74), P(13, -74), P(16, -50), P(14, -20), P(10, -2), P(-10, -2), P(-14, -20), P(-16, -50)]
    out.append(painted(D, body, tuple(tn(c) for c in kimono), seed, sdir=(1, 0.3), sk=0.2, angle=-90, n=12, inkw=1, inkop=0.5, hi=0.3))
    rnd = random.Random(seed)
    for _ in range(10):
        px, py = P(rnd.uniform(-12, 12), rnd.uniform(-70, -8))
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{1.3 * k:.1f}" fill="{tn("#FFFFFF")}" opacity="0.8"/>')
    # obi and its drum bow
    out.append(painted(D, [P(-15, -60), P(15, -60), P(15, -48), P(-15, -48)], tuple(tn(c) for c in obi), seed + 1, sk=0.2, angle=0, n=4, inkw=0.8, hi=0.3))
    out.append(painted(D, [P(-11, -64), P(11, -64), P(12, -42), P(-12, -42)], tuple(tn(c) for c in obi), seed + 2, sk=0.25, angle=-90, n=4, inkw=0.9, hi=0.35))
    out.append(f'<path d="{pd([P(-12, -52), P(12, -52)], False)}" stroke="{tn("#C8402A")}" stroke-width="{1.4 * k:.1f}"/>')
    # feet in white tabi and geta
    for sx in (-5, 5):
        fx, fy = P(sx, -1)
        out.append(f'<rect x="{fx - 3 * k:.1f}" y="{fy - 1 * k:.1f}" width="{6 * k:.1f}" height="{3 * k:.1f}" fill="#F6F0E6"/>')
    # neck and hair
    out.append(f'<path d="{blob(*P(0, -77), 4 * k, 4 * k, seed + 3, 0.1, 8)}" fill="{tn("#F2D2B4")}"/>')
    out.append(f'<path d="{blob(*P(0, -85), 8.5 * k, 8 * k, seed + 4, 0.08, 12)}" fill="#1A1414"/>')
    out.append(f'<path d="{blob(*P(0, -95), 6 * k, 4.6 * k, seed + 5, 0.08, 10)}" fill="#1A1414"/>')
    out.append(f'<path d="{pd([P(3, -95), P(10, -100)], False)}" stroke="{tn("#E8B838")}" stroke-width="{1.2 * k:.1f}"/>')
    # wagasa on the right shoulder
    cx_, cy_ = P(10, -104)
    ang = -18 * flip
    R = 30 * k
    canopy = rot([(cx_ - R, cy_ + R * 0.32), (cx_ - R * 0.6, cy_ - R * 0.2), (cx_, cy_ - R * 0.42), (cx_ + R * 0.6, cy_ - R * 0.2), (cx_ + R, cy_ + R * 0.32), (cx_, cy_ + R * 0.12)], cx_, cy_, ang)
    out.append(painted(D, canopy, tuple(tn(c) for c in umbrella), seed + 6, sdir=(0.3, 1), sk=0.2, angle=0, n=8, inkw=1, hi=0.35))
    for t in (-0.7, -0.35, 0, 0.35, 0.7):
        a, b = rot([(cx_, cy_ - R * 0.4), (cx_ + R * t, cy_ + R * 0.24 - abs(t) * R * 0.06)], cx_, cy_, ang)
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{tn("#F6E0C0")}" stroke-width="{0.8 * k:.1f}" opacity="0.7"/>')
    hx, hy = rot([(cx_, cy_ + R * 0.12)], cx_, cy_, ang)[0]
    out.append(f'<path d="M {hx:.1f} {hy:.1f} L {P(4, -60)[0]:.1f} {P(4, -60)[1]:.1f}" stroke="#3A2418" stroke-width="{1.4 * k:.1f}"/>')
    return "".join(out)


@design("kyoto")
def kyoto():
    D = Doc2("jp-ky")
    VX, VY, F = 300, 338, 300

    def Pt(X, Y, z):
        return (VX + X * F / z, VY + Y * F / z)

    out = [sky(D, [(0, "#1E2458"), (0.45, "#5A3A78"), (0.75, "#D8708A"), (1, "#F6B07A")], 1301, 360, ["#3A3A78", "#7A4A8A", "#E88A8A"], 60, angle=-3, sop=(0.06, 0.16))]
    rnd = random.Random(1302)
    for _ in range(26):
        out.append(f'<circle cx="{rnd.uniform(60, 540):.1f}" cy="{rnd.uniform(20, 160):.1f}" r="{rnd.uniform(0.6, 1.6):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    out.append(soft_glow(D, 300, 340, 160, "#FFC890", 0.5))
    # Yasaka-style pagoda closing the street
    out.append(pagoda(D, 300, 352, 196, 1303, body=("#7A4A5A", "#4A2A3E", "#2A1426"), roof=("#5A4A6A", "#2A2238", "#140E1E"), rim="#E8A090"))
    # street paving
    road = [Pt(-1, 1, 0.5), Pt(1, 1, 0.5), Pt(1, 1, 12), Pt(-1, 1, 12)]
    out.append(f'<path d="{pd(road)}" fill="{D.lin([(0, "#6A5A6A"), (1, "#2A2232")], 0, 0, 0, 1)}"/>')
    pav = []
    z = 0.6
    while z < 12:
        a, b = Pt(-1, 1, z), Pt(1, 1, z)
        pav.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#1A1420" stroke-width="{max(0.6, 3 / z):.1f}" opacity="0.6"/>')
        off = 0.25 if int(z * 3) % 2 else 0
        for X in (-0.75, -0.25, 0.25, 0.75):
            p1, p2 = Pt(X + off * 0.5, 1, z), Pt(X + off * 0.5, 1, z * 1.18)
            pav.append(f'<path d="M {p1[0]:.1f} {p1[1]:.1f} L {p2[0]:.1f} {p2[1]:.1f}" stroke="#1A1420" stroke-width="{max(0.5, 2.4 / z):.1f}" opacity="0.5"/>')
        z *= 1.18
    out.append(clipped(D, pd(road), pav))
    # buildings, far to near, on both sides
    for side in (-1, 1):
        for i in range(9, -1, -1):
            z0, z1 = 0.62 + i * 0.9, 0.62 + (i + 1) * 0.9
            X = side
            seed = 1310 + i * 7 + (side > 0) * 100
            haze = min(0.5, i * 0.06)
            wall = mix("#E8D2B0", "#5A4A6A", haze + 0.25)
            wood = mix("#5A3420", "#2A2034", haze)
            up = [Pt(X, -0.78, z0), Pt(X, -0.78, z1), Pt(X, -0.2, z1), Pt(X, -0.2, z0)]
            low = [Pt(X, -0.12, z0), Pt(X, -0.12, z1), Pt(X, 1, z1), Pt(X, 1, z0)]
            out.append(f'<path d="{pd(up)}" fill="{wall}"/>')
            # upper slit windows (mushiko)
            for t in (0.25, 0.55):
                a, b = Pt(X, -0.62, z0 + (z1 - z0) * t), Pt(X, -0.36, z0 + (z1 - z0) * (t + 0.22))
                c, d_ = Pt(X, -0.62, z0 + (z1 - z0) * (t + 0.22)), Pt(X, -0.36, z0 + (z1 - z0) * t)
                win = [a, c, b, d_]
                out.append(f'<path d="{pd(win)}" fill="{mix("#FFC870", "#5A3A50", haze)}"/>')
                for u in range(1, 5):
                    q1 = Pt(X, -0.62, z0 + (z1 - z0) * (t + 0.22 * u / 5))
                    q2 = Pt(X, -0.36, z0 + (z1 - z0) * (t + 0.22 * u / 5))
                    out.append(f'<path d="M {q1[0]:.1f} {q1[1]:.1f} L {q2[0]:.1f} {q2[1]:.1f}" stroke="{wood}" stroke-width="{max(0.8, 4 / z0):.1f}"/>')
            # ground floor: warm-lit lattice (koshi)
            out.append(f'<path d="{pd(low)}" fill="{mix("#6A3A22", "#2A1E30", haze)}"/>')
            glow_pts = [Pt(X, 0.0, z0 + 0.12), Pt(X, 0.0, z1 - 0.12), Pt(X, 0.8, z1 - 0.12), Pt(X, 0.8, z0 + 0.12)]
            out.append(f'<path d="{pd(glow_pts)}" fill="{mix("#FFB050" if i % 2 else "#F29A40", "#5A3A4A", haze * 0.9)}" opacity="{0.95 if i % 4 != 2 else 0.5}"/>')
            zz = z0
            while zz < z1:
                a, b = Pt(X, -0.12, zz), Pt(X, 1, zz)
                out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{wood}" stroke-width="{max(0.9, 9 / zz):.1f}"/>')
                zz += 0.06
            for Y in (-0.12, 0.35, 1):
                a, b = Pt(X, Y, z0), Pt(X, Y, z1)
                out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{wood}" stroke-width="{max(1, 8 / z0):.1f}"/>')
            # posts
            for zz in (z0, z1):
                a, b = Pt(X, -0.8, zz), Pt(X, 1, zz)
                out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{wood}" stroke-width="{max(1.2, 14 / zz):.1f}"/>')
            # small first-floor eave and the main eave above
            for (Yw, Ye, Xe) in ((-0.2, -0.08, 0.88), (-0.95, -0.76, 0.76)):
                ev = [Pt(X, Yw, z0), Pt(X, Yw, z1), Pt(X * Xe, Ye, z1), Pt(X * Xe, Ye, z0)]
                out.append(f'<path d="{pd(ev)}" fill="{mix("#3A3444", "#2A2238", haze)}"/>')
                for u in range(0, 8):
                    zz = z0 + (z1 - z0) * u / 8
                    a, b = Pt(X, Yw, zz), Pt(X * Xe, Ye, zz)
                    out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="#1A1620" stroke-width="{max(0.6, 3 / zz):.1f}" opacity="0.7"/>')
                a, b = Pt(X * Xe, Ye, z0), Pt(X * Xe, Ye, z1)
                out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}" stroke="{mix("#C8A0B0", "#4A3A5A", haze)}" stroke-width="{max(0.8, 5 / z0):.1f}" opacity="0.7"/>')
            # roof mass above the eave
            rf = [Pt(X, -0.95, z0), Pt(X, -0.95, z1), Pt(X * 1.4, -1.25, z1), Pt(X * 1.4, -1.25, z0)]
            out.append(f'<path d="{pd(rf)}" fill="{mix("#2A2236", "#3A3050", haze)}"/>')
            # noren in some doorways
            if i % 3 == 1:
                zn = z0 + (z1 - z0) * 0.3
                for u in range(3):
                    za, zb = zn + u * 0.1, zn + (u + 1) * 0.1 - 0.012
                    nr = [Pt(X * 0.995, -0.1, za), Pt(X * 0.995, -0.1, zb), Pt(X * 0.995, 0.32, zb), Pt(X * 0.995, 0.32, za)]
                    out.append(f'<path d="{pd(nr)}" fill="{mix("#27407A" if side < 0 else "#8A2A2A", "#2A2238", haze)}"/>')
    # paper lanterns along the eaves, glowing, and their reflections on wet stone
    for side in (-1, 1):
        for i in range(8, -1, -1):
            zl = 1.0 + i * 0.9
            lx, ly = Pt(side * 0.82, -0.04, zl)
            sz = 0.2 * F / zl
            if sz < 4:
                continue
            gx, gy = Pt(side * 0.84, 1, zl)
            out.append(f'<ellipse cx="{gx:.1f}" cy="{gy + sz * 0.6:.1f}" rx="{sz * 0.5:.1f}" ry="{sz * 1.4:.1f}" fill="{D.rad([(0, "#FFB860", 0.55), (1, "#FFB860", 0)])}"/>')
            out.append(chochin(D, lx, ly, sz * 0.62, sz, 1340 + i + (side > 0) * 20, pal=("#FFB0A0", "#E83A2A", "#8A1A12"), glow_c="#FFB060", haze=min(0.4, i * 0.05)))
    # figures: a woman in kimono with her umbrella, a couple further up
    out.append(kimono_back(D, 268, Pt(0, 1, 3.1)[1], 0.85 * F / 3.1, 1360, tint=("#5A3A6A", 0.12)))
    for k, (X, z, col) in enumerate(((0.3, 6.0, "#3A3A5A"), (0.42, 6.2, "#4A3A4A"))):
        bx, by = Pt(X, 1, z)
        out.append(figures.person(bx, by, 0.85 * F / z, "walk", -1, f"silhouette:{col}", seed=1370 + k))
    # wet sheen on the stones
    for side in (-1, 1):
        for zz in (1.2, 1.9, 2.8):
            a, b = Pt(side * 0.75, 1, zz), Pt(side * 0.75, 1, zz + 0.5)
            out.append(taper([a, b], 30 / zz, 8 / zz, "#FFB860", 0.18))
    # lettering
    out.append(letters(D, 300, 140, "kyoto", SERIF_IT, 104, "#FFF0DA", ["#FFFFFF", "#F6D8C0", "#FFE8D0"], 1390, max_w=330,
                       shadow="#1A1238", soff=(0.02, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 176, "LANTERNS AT DUSK", "#FFC890", font=JOS, size=18, ls=6, line_w=22, gap=10))
    return finish_b(D, out, 1391, "#1A1228", 0.6)


# ================================================================ 14. miyajima — the great torii standing in the sea at sunset
def torii(D, cx, base, w, h, seed, pal=SHU, kasagi="#1E1A1E", haze=0.0, refl=False):
    """Ryobu-style torii: two main pillars braced by four short posts, a sweeping black-capped lintel, a straight tie beam."""
    hz = (lambda c: mix(c, "#E88A6A", haze)) if haze else (lambda c: c)
    out = []
    pw = w * 0.07
    lx, rx = cx - w * 0.3, cx + w * 0.3
    top = base - h
    # support posts with their little roofs
    for px in (lx, rx):
        for sg in (-1, 1):
            sx = px + sg * w * 0.13
            sp = [(sx - pw * 0.32, base), (sx - pw * 0.28, base - h * 0.48), (sx + pw * 0.28, base - h * 0.48), (sx + pw * 0.32, base)]
            out.append(painted(D, sp, tuple(hz(c) for c in pal), seed + int(sx), sdir=(1, 0), sk=0.3, angle=-90, n=4, inkw=1, hi=0.3))
            out.append(f'<path d="{pd([(sx - pw * 0.55, base - h * 0.48), (sx + pw * 0.55, base - h * 0.48), (sx + pw * 0.4, base - h * 0.52), (sx - pw * 0.4, base - h * 0.52)])}" fill="{hz(kasagi)}"/>')
        out.append(f'<path d="{pd([(px - w * 0.13, base - h * 0.4), (px + w * 0.13, base - h * 0.4), (px + w * 0.13, base - h * 0.37), (px - w * 0.13, base - h * 0.37)])}" fill="{hz(pal[1])}"/>')
    # main pillars
    for px in (lx, rx):
        mp = [(px - pw * 0.6, base), (px - pw * 0.5, top + h * 0.1), (px + pw * 0.5, top + h * 0.1), (px + pw * 0.6, base)]
        out.append(painted(D, mp, tuple(hz(c) for c in pal), seed + int(px) + 3, sdir=(1, 0), sk=0.32, angle=-90, n=10, inkw=1.4, hi=0.4, hik=0.12))
        out.append(f'<path d="{pd([(px - pw * 0.62, base - 4), (px + pw * 0.62, base - 4), (px + pw * 0.62, base + 2), (px - pw * 0.62, base + 2)])}" fill="{hz("#1A1416")}"/>')
    # nuki tie beam
    ny = top + h * 0.3
    out.append(painted(D, [(lx - w * 0.16, ny), (rx + w * 0.16, ny), (rx + w * 0.16, ny + h * 0.06), (lx - w * 0.16, ny + h * 0.06)], tuple(hz(c) for c in pal), seed + 7, sdir=(0, 1), sk=0.3, angle=0, n=8, inkw=1.2, hi=0.35))
    # central strut with a blank plaque
    out.append(f'<path d="{pd([(cx - pw * 0.35, top + h * 0.08), (cx + pw * 0.35, top + h * 0.08), (cx + pw * 0.35, ny), (cx - pw * 0.35, ny)])}" fill="{hz(pal[1])}"/>')
    out.append(painted(D, [(cx - pw * 0.8, top + h * 0.1), (cx + pw * 0.8, top + h * 0.1), (cx + pw * 0.8, top + h * 0.26), (cx - pw * 0.8, top + h * 0.26)], (hz("#4A4A5A"), hz("#1E1E2A"), hz("#0A0A10")), seed + 8, sk=0.1, n=3, inkw=0.8, hi=0.2))
    out.append(f'<rect x="{cx - pw * 0.8:.1f}" y="{top + h * 0.1:.1f}" width="{pw * 1.6:.1f}" height="{h * 0.16:.1f}" fill="none" stroke="{hz("#E8B838")}" stroke-width="{max(1, w * 0.006):.1f}"/>')
    # shimaki (vermilion) under the kasagi (black), ends sweeping up
    L = w * 0.62
    def beam(y0, th, lift, col, pal_=None):
        pts = []
        for i in range(21):
            t = -1 + 2 * i / 20
            pts.append((cx + L * t, y0 - lift * abs(t) ** 3))
        bot = [(x, y + th * (1 - 0.35 * abs((x - cx) / L) ** 2)) for x, y in pts[::-1]]
        return pts + bot
    sh = beam(top + h * 0.1, h * 0.05, h * 0.06, pal[1])
    out.append(painted(D, sh, tuple(hz(c) for c in pal), seed + 9, sdir=(0, 1), sk=0.25, angle=0, n=10, inkw=1.2, hi=0.3))
    kb = beam(top + h * 0.04, h * 0.07, h * 0.1, kasagi)
    out.append(painted(D, kb, (hz("#5A5460"), hz(kasagi), hz("#000000")), seed + 10, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.2, hi=0.3))
    return "".join(out)


@design("miyajima")
def miyajima():
    D = Doc2("jp-mj")
    out = [sky(D, [(0, "#3A2A6A"), (0.4, "#B84A6A"), (0.7, "#F2885A"), (1, "#FFD08A")], 1401, 420, ["#7A3A7A", "#F2A07A", "#FFD8A0"], 70, angle=-2, sop=(0.08, 0.18))]
    rnd = random.Random(1402)
    for k, (x, y, w) in enumerate(((120, 220, 240), (480, 200, 220), (380, 300, 300), (130, 330, 200))):
        out.append(f'<path d="{blob(x, y, w / 2, 8, 1403 + k, 0.2, 14)}" fill="#FFB890" opacity="0.6"/><path d="{blob(x + 12, y + 5, w / 2.4, 4, 1404 + k, 0.2, 14)}" fill="#8A3A6A" opacity="0.45"/>')
    # the sun setting between the pillars
    out.append(soft_glow(D, 300, 392, 210, "#FFE8A0", 0.8))
    out.append(f'<circle cx="300" cy="392" r="30" fill="#FFF2C8"/><circle cx="300" cy="392" r="30" fill="#FFD890" opacity="0.5"/>')
    # Misen's ridges on the far shore
    for k, (pts, col, base) in enumerate((([(-20, 392), (90, 356), (190, 380), (300, 366), (420, 340), (520, 372), (620, 360)], ("#9A6A9A", "#7A4A82", "#5A3A6A"), 420),
                                           ([(-20, 404), (120, 392), (260, 408), (380, 396), (500, 404), (620, 396)], ("#6A4A7A", "#4A3260", "#2A1A40"), 420))):
        out.append(hill(D, ridge(pts, 1405 + k, 6, 3), base, col, 1407 + k, inkw=0, n=30))
    # the sea
    out.append(f'<rect y="418" width="600" height="182" fill="{D.lin([(0, "#E88A6A"), (0.35, "#8A4A7A"), (1, "#2A1E4E")])}"/>')
    for k in range(40):
        y = 424 + k * k * 0.11
        w = 20 + k * 2.2
        out.append(f'<path d="M {300 - w / 2 + rnd.uniform(-10, 10):.1f} {y:.1f} l {w * rnd.uniform(0.4, 1):.1f} 0" stroke="#FFE8B0" stroke-width="{1.2 + k * 0.06:.1f}" opacity="{0.85 - k * 0.015:.2f}" stroke-linecap="round"/>')
    out.append(wave_lines(1410, (0, 426, 600, 590), ["#F6A88A", "#C86A8A", "#FFD0A0"], 70, (16, 50), 2, 2, (0.3, 0.7)))
    # the torii and its broken reflection
    tor = torii(D, 300, 470, 380, 276, 1411)
    out.append(f'<g transform="translate(0 940) scale(1 -1)" opacity="0.35">{torii(D, 300, 470, 380, 276, 1412, haze=0.3)}</g>')
    for k in range(18):
        y = 476 + k * 7
        out.append(f'<path d="M 0 {y} L 600 {y}" stroke="#2A1E4E" stroke-width="2" opacity="0.35"/>')
    out.append(tor)
    out.append(f'<path d="M 60 470 L 540 470" stroke="#FFE0B0" stroke-width="1.6" opacity="0.4"/>')
    # near rocks with a stone lantern and a deer watching
    rk = [(-20, 520), (40, 500), (110, 506), (170, 530), (210, 560), (230, 600), (-20, 600)]
    out.append(painted(D, rk, ("#6A5A6A", "#3A2E3E", "#1A121E"), 1413, sdir=(-0.6, 0.6), sk=0.15, angle=-20, n=30, inkw=1.6, hi=0.4))
    out.append(taper([(40, 502), (110, 508), (170, 532)], 3, 2, "#FFB890", 0.6))
    out.append(toro(D, 74, 506, 104, 1414))
    out.append(deer_sil(150, 520, 1.0, "#2A1E2E", rim="#FFB890"))
    # lettering
    out.append(letters(D, 300, 130, "miyajima", SERIF_IT, 108, "#FFF2DC", ["#FFFFFF", "#FFE0C8", "#FFF0E0"], 1420, max_w=400,
                       shadow="#3A1A4A", soff=(0.02, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 168, "THE GATE IN THE SEA", "#FFD8A0", font=JOS, size=18, ls=6, line_w=24, gap=10))
    return finish_b(D, out, 1421, "#2A1A3A", 0.6)


def toro(D, cx, base, h, seed, pal=("#A89CA0", "#6A5E64", "#2E2830"), lit=True):
    """Stone lantern: wide foot, round post, platform, glowing fire box, broad roof with turned-up corners, jewel finial."""
    k = h / 100
    out = [f'<ellipse cx="{cx + 6:.1f}" cy="{base:.1f}" rx="{30 * k:.1f}" ry="{5 * k:.1f}" fill="#000000" opacity="0.3"/>']
    parts = [((-22, 0), (22, 0), (18, -10), (-18, -10)),        # foot
             ((-7, -10), (7, -10), (6, -44), (-6, -44)),          # post
             ((-20, -44), (20, -44), (16, -52), (-16, -52)),      # platform
             ((-13, -52), (13, -52), (13, -70), (-13, -70))]      # fire box
    for i, pp in enumerate(parts):
        pts = [(cx + x * k, base + y * k) for x, y in pp]
        out.append(painted(D, densify(pts, 8), pal, seed + i, sdir=(1, 0.2), sk=0.25, angle=-90, n=6, inkw=1.2, hi=0.35))
    if lit:
        out.append(soft_glow(D, cx, base - 61 * k, 40 * k, "#FFC870", 0.6))
        out.append(f'<path d="{pd([(cx - 7 * k, base - 56 * k), (cx + 7 * k, base - 56 * k), (cx + 7 * k, base - 67 * k), (cx - 7 * k, base - 67 * k)])}" fill="#FFE0A0"/>')
        out.append(f'<path d="M {cx:.1f} {base - 56 * k:.1f} L {cx:.1f} {base - 67 * k:.1f}" stroke="{pal[2]}" stroke-width="{1.4 * k:.1f}"/>')
    roof = [(cx - 30 * k, base - 72 * k), (cx - 24 * k, base - 74 * k), (cx - 8 * k, base - 86 * k), (cx + 8 * k, base - 86 * k), (cx + 24 * k, base - 74 * k), (cx + 30 * k, base - 72 * k), (cx + 22 * k, base - 69 * k), (cx - 22 * k, base - 69 * k)]
    out.append(painted(D, roof, pal, seed + 9, sdir=(0.6, 0.8), sk=0.2, angle=0, n=6, inkw=1.3, hi=0.4))
    out.append(painted(D, blob_pts(cx, base - 91 * k, 5 * k, 6 * k, seed + 10, 0.05, 10), pal, seed + 10, sk=0.25, n=3, inkw=1, hi=0.4))
    out.append(f'<path d="{blob(cx, base - 98 * k, 2.4 * k, 3.6 * k, seed + 11, 0.05, 8)}" fill="{pal[1]}"/>')
    return "".join(out)


def deer_sil(x, base, s, col, rim=None, flip=1):
    """Sika deer standing, looking out to sea (painted silhouette with a rim of sunset light)."""
    k = s
    P = lambda px, py: (x + px * k * flip, base + py * k)
    body = [P(-24, -44), P(14, -46), P(22, -40), P(24, -30), P(20, -26), P(18, 0), P(15, 0), P(14, -24), P(-14, -24), P(-16, 0), P(-19, 0), P(-22, -26), P(-27, -36)]
    neck = [P(14, -46), P(20, -64), P(26, -70), P(34, -66), P(30, -60), P(24, -40)]
    out = [f'<path d="{smooth_closed(body)}" fill="{col}"/>', f'<path d="{smooth_closed(neck)}" fill="{col}"/>']
    for lx in (-8, 8):
        out.append(f'<path d="{pd([P(lx - 1.5, -26), P(lx + 1.5, -26), P(lx + 1, 0), P(lx - 1, 0)])}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed([P(25, -72), P(32, -76), P(40, -68), P(36, -64), P(28, -64)])}" fill="{col}"/>')
    out.append(f'<path d="{smooth_closed([P(24, -72), P(18, -80), P(22, -74)])}" fill="{col}"/>')
    out.append(f'<path d="{pd([P(-26, -42), P(-31, -36)], False)}" stroke="{col}" stroke-width="{3 * k:.1f}" stroke-linecap="round"/>')
    if rim:
        out.append(f'<path d="{smooth_open([P(-24, -44), P(14, -46), P(20, -64), P(26, -70), P(32, -76), P(40, -68)])}" stroke="{rim}" stroke-width="{1.6 * k:.1f}" fill="none" opacity="0.8"/>')
    return "".join(out)


# ================================================================ 15. onsen — a snow monkey soaking in a steaming spring
def snow_monkey(D, cx, cy, s, seed):
    """Japanese macaque up to its shoulders in hot water: soft grey-brown fur ruff framing a red face, eyes closed in bliss,
    a little cap of snow on its head."""
    rnd = random.Random(seed)
    k = s
    out = []
    # shoulders / arms resting at the waterline
    body = blob_pts(cx, cy + 70 * k, 104 * k, 52 * k, seed, 0.06, 22)
    out.append(painted(D, body, ("#C8B8A0", "#8E7E6A", "#4A3E34"), seed, sdir=(0.6, 0.6), sk=0.18, angle=-80, n=40, slen=(8 * k, 20 * k), sw=(1, 2.4),
                       cols=["#D8CCB8", "#6E6050", "#A89880"], inkw=1.2, inkop=0.4, hi=0.3))
    # head with a soft ruff (wider at the cheeks)
    head = []
    for i in range(40):
        a = 2 * math.pi * i / 40
        rx = 66 * k * (1 + 0.1 * math.cos(2 * a) ** 2)
        ry = 60 * k
        wob = 1 + 0.035 * math.sin(a * 11 + seed)
        head.append((cx + rx * wob * math.cos(a), cy - 4 * k + ry * wob * math.sin(a)))
    hd = smooth_closed(head)
    out.append(f'<path d="{hd}" fill="#A2927C"/>')
    fur = [shade_over(D, hd, "#2E2418", 0.4, 0, 0, 1, 1, 0.45), light_over(D, hd, "#F2E8D8", 0.45, 0, 0, 0.7, 0.7, 0.5)]
    for _ in range(int(700 * k)):
        a = rnd.uniform(0, 2 * math.pi)
        rr = math.sqrt(rnd.uniform(0.15, 1)) * 66 * k
        x, y = cx + math.cos(a) * rr, cy - 4 * k + math.sin(a) * rr * 0.92
        L = rnd.uniform(5, 10) * k
        lit = -(math.cos(a) * 0.6 + math.sin(a) * 0.8)
        c = rnd.choice(["#E8DCC8", "#D6C8B0"]) if lit > 0.35 else (rnd.choice(["#6E6050", "#7A6C5A"]) if lit < -0.35 else rnd.choice(["#B2A28A", "#C0B098", "#9A8A74"]))
        fa = a + rnd.uniform(-0.3, 0.3) + 0.25
        fur.append(taper([(x, y), (x + math.cos(fa) * L * 0.5, y + math.sin(fa) * L * 0.5 + 1), (x + math.cos(fa) * L, y + math.sin(fa) * L + 2)], 2.0 * k, 0.5, c, rnd.uniform(0.5, 0.85)))
    out.append(clipped(D, hd, fur))
    # soft fringe along the outline
    for i in range(0, 40, 2):
        x, y = head[i]
        a = math.atan2(y - cy, x - cx) + 0.3
        out.append(taper([(x, y), (x + math.cos(a) * 7 * k, y + math.sin(a) * 7 * k + 2 * k)], 3 * k, 0.5, "#A2927C", 0.9))
    out.append(ink(hd, "#5A4A3A", 1.2, seed + 3, 1, 0.3))
    # small ears half-hidden in the fur
    for sg in (-1, 1):
        out.append(f'<path d="{blob(cx + sg * 50 * k, cy - 4 * k, 9 * k, 11 * k, seed + 4 + sg, 0.1, 10)}" fill="#D88A80"/>'
                   f'<path d="{blob(cx + sg * 51 * k, cy - 3 * k, 5 * k, 7 * k, seed + 5 + sg, 0.1, 8)}" fill="#A85A54"/>')
    # the face: red, heart-shaped, a little muzzle
    face = [(cx, cy - 24 * k), (cx + 18 * k, cy - 30 * k), (cx + 32 * k, cy - 18 * k), (cx + 34 * k, cy + 2 * k), (cx + 26 * k, cy + 24 * k), (cx + 12 * k, cy + 38 * k),
            (cx, cy + 41 * k), (cx - 12 * k, cy + 38 * k), (cx - 26 * k, cy + 24 * k), (cx - 34 * k, cy + 2 * k), (cx - 32 * k, cy - 18 * k), (cx - 18 * k, cy - 30 * k)]
    fd = smooth_closed(face)
    out.append(f'<path d="{fd}" fill="#E8766C"/>')
    out.append(clipped(D, fd, [f'<path d="{blob(cx - 10 * k, cy - 14 * k, 22 * k, 12 * k, seed + 6, 0.2, 10)}" fill="#FFB0A0" opacity="0.6"/>',
                               f'<path d="{blob(cx, cy + 20 * k, 20 * k, 16 * k, seed + 7, 0.1, 12)}" fill="#F29488" opacity="0.8"/>',
                               shade_over(D, fd, "#7A1E1E", 0.45, 0, 0, 1, 1, 0.45),
                               strokes(D.nid(), fd, (cx - 36 * k, cy - 32 * k, cx + 36 * k, cy + 42 * k), ["#FFB8A8", "#C04A44"], seed + 8, n=24, angle=-80, length=(6 * k, 14 * k), width=(1, 2.4), opacity=(0.2, 0.45))]))
    out.append(ink(fd, "#8A3A34", 1.4, seed + 9, 1, 0.55))
    # brow ridge and closed eyes
    out.append(taper(catmull([(cx - 30 * k, cy - 12 * k), (cx - 14 * k, cy - 18 * k), (cx, cy - 14 * k), (cx + 14 * k, cy - 18 * k), (cx + 30 * k, cy - 12 * k)], 4), 5 * k, 4 * k, "#B84A44", 0.55))
    for sg in (-1, 1):
        ex, ey = cx + sg * 13 * k, cy - 6 * k
        out.append(taper([(ex - 8 * k, ey), (ex, ey + 3.5 * k), (ex + 8 * k, ey)], 2.6 * k, 2.6 * k, "#3A1414", 0.95))
        out.append(taper([(ex - 6 * k, ey + 6 * k), (ex + 5 * k, ey + 6 * k)], 1.2 * k, 0.6, "#B84A44", 0.5))
    # nose and contented mouth
    for sg in (-1, 1):
        out.append(f'<ellipse cx="{cx + sg * 3.2 * k:.1f}" cy="{cy + 12 * k:.1f}" rx="{1.8 * k:.1f}" ry="{1.3 * k:.1f}" fill="#5A1A1A"/>')
    out.append(taper([(cx - 9 * k, cy + 25 * k), (cx, cy + 28 * k), (cx + 9 * k, cy + 25 * k)], 1.8 * k, 1.8 * k, "#6A2222", 0.9))
    # snow on the crown
    sn = [(cx - 40 * k, cy - 44 * k), (cx - 20 * k, cy - 66 * k), (cx + 12 * k, cy - 70 * k), (cx + 40 * k, cy - 50 * k), (cx + 30 * k, cy - 42 * k), (cx + 4 * k, cy - 50 * k), (cx - 24 * k, cy - 42 * k)]
    out.append(painted(D, sn, ("#FFFFFF", "#F4F6FC", "#B8C0E0"), seed + 10, sdir=(0.3, 1), sk=0.25, angle=0, n=8, inkw=1.2, inkc="#8A90B8", hi=0.4))
    return "".join(out)


def snow_rock(D, cx, cy, rx, ry, seed, snow=True):
    rp = blob_pts(cx, cy, rx, ry, seed, 0.12, 16)
    out = [painted(D, rp, ("#8A8494", "#55505E", "#2A2632"), seed, sdir=(0.6, 0.7), sk=0.2, angle=-30, n=int(rx * 0.4) + 6, inkw=1.6, hi=0.35)]
    if snow:
        cap = [(x, y) for x, y in rp if y < cy - ry * 0.05]
        cap = sorted(cap, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
        if len(cap) > 3:
            sp = [(x, y - 4) for x, y in cap] + [(cap[-1][0] - 4, cap[-1][1] + 8), (cx, cy - ry * 0.2), (cap[0][0] + 4, cap[0][1] + 8)]
            out.append(painted(D, sp, ("#FFFFFF", "#F2F4FA", "#B0B8DC"), seed + 1, sdir=(0.3, 1), sk=0.25, angle=0, n=8, inkw=1.2, inkc="#8A90B8", hi=0.4))
    return "".join(out)


@design("onsen")
def onsen():
    D = Doc2("jp-on")
    out = [sky(D, [(0, "#8A9AC0"), (0.6, "#C8D0E4"), (1, "#E8ECF4")], 1501, 600, ["#A8B4D4", "#FFFFFF", "#D8DCEC"], 70, angle=-4, sop=(0.08, 0.2))]
    # snowy forest behind
    for k, (col, base, h, dens) in enumerate((("#9AA6C4", 330, 110, 0.9), ("#5E6E8E", 360, 130, 0.7))):
        rnd = random.Random(1502 + k)
        for _ in range(int(16 * dens)):
            x = rnd.uniform(-20, 620)
            hh = h * rnd.uniform(0.7, 1.2)
            out.append(hg.fir(D, x, base + rnd.uniform(-10, 10), hh, hh * 0.42, 1503 + k * 50 + _, cols=(dk(col, 0.2), col, lt(col, 0.2)), tiers=4, snow=True, ink_c=None, trunk=False))
    out.append(f'<rect y="330" width="600" height="80" fill="{D.lin([(0, "#E8ECF4", 0), (1, "#E8ECF4", 0.9)])}"/>')
    # snowbank around the pool
    bank = ridge([(-20, 372), (140, 360), (300, 372), (460, 356), (620, 368)], 1504, 6, 3)
    out.append(f'<path d="{smooth_open(bank)} L 620 600 L -20 600 Z" fill="#F2F4FA"/>')
    out.append(ink(smooth_open(bank), "#9AA0C8", 1.6, 1505, 1, 0.5))
    # the pool
    pool = blob_pts(300, 470, 290, 84, 1506, 0.05, 30)
    pd_ = smooth_closed(pool)
    out.append(f'<path d="{pd_}" fill="{D.lin([(0, "#5AA8B4"), (1, "#2E7484")])}"/>')
    out.append(clipped(D, pd_, [wave_lines(1507, (0, 400, 600, 560), ["#C8F0F4", "#FFFFFF"], 40, (20, 50), 2, 2, (0.3, 0.6)),
                                f'<path d="{blob(300, 420, 280, 20, 1508, 0.1, 16)}" fill="#1E5A6A" opacity="0.4"/>']))
    # the monkey, then the water over its shoulders
    out.append(snow_monkey(D, 300, 364, 1.42, 1509))
    wl = 448
    water = [(150, wl), (300, wl + 4), (450, wl), (450, 560), (150, 560)]
    out.append(clipped(D, pd_, [f'<path d="{pd([(0, wl), (600, wl), (600, 600), (0, 600)])}" fill="#3E8E9C" opacity="0.88"/>',
                                f'<path d="{blob(300, wl + 20, 100, 22, 1510, 0.1, 14)}" fill="#7A6A5A" opacity="0.35"/>',
                                wave_lines(1511, (120, wl + 4, 480, 540), ["#C8F0F4", "#FFFFFF"], 30, (20, 50), 2, 2, (0.4, 0.7))]))
    for kk in range(3):
        out.append(f'<ellipse cx="300" cy="{wl + 2}" rx="{110 + kk * 26}" ry="{8 + kk * 4}" fill="none" stroke="#E8FFFF" stroke-width="{2 - kk * 0.5:.1f}" opacity="{0.6 - kk * 0.15:.2f}"/>')
    # rocks around the rim
    for k, (x, y, rx, ry) in enumerate(((40, 470, 70, 42), (120, 540, 70, 36), (500, 534, 80, 38), (566, 464, 60, 40), (300, 574, 120, 30), (150, 418, 44, 22), (470, 414, 50, 24))):
        out.append(snow_rock(D, x, y, rx, ry, 1520 + k))
    # steam and falling snow
    for k, x in enumerate((140, 230, 380, 470)):
        out.append(steam(x, 420, 120, 1530 + k, "#FFFFFF", 2, 30, 10, 0.32))
    out.append(hg.flakes(1535, 120, (0, 0, 600, 600), (1.2, 3.6), "#FFFFFF", (0.6, 1.0), avoid=((100, 60, 500, 200),)))
    # lettering
    out.append(letters(D, 300, 132, "onsen", SERIF_IT, 132, "#2E3A6A", ["#3E4E88", "#1E2A50", "#5A6AA8"], 1536, max_w=360,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#A8B8E8"))
    out.append(ruled(300, 176, "SNOW OUTSIDE, WARM INSIDE", "#B8402A", font=JOS, size=18, ls=5, line_w=22, gap=10))
    return finish_b(D, out, 1537, "#2A2A4A", 0.6)


# ================================================================ 16. furin — a glass wind chime under the eaves in summer
def asagao(D, cx, cy, r, seed, pal=("#B8B0F0", "#5A4AC8", "#2A1E7A"), rot_=0, tilt=1.0):
    """Morning glory seen from the front: a pleated trumpet with a white star throat."""
    pts = []
    for i in range(50):
        a = 2 * math.pi * i / 50
        rr = r * (1 + 0.05 * math.cos(a * 5))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * tilt))
    pts = rot(pts, cx, cy, rot_)
    out = [painted(D, pts, pal, seed, sdir=(0.5, 0.8), sk=0.1, angle=-40, n=14, inkw=1.2, inkc=pal[2], inkop=0.5, hi=0.35)]
    d = smooth_closed(pts)
    inner = [f'<path d="{d}" fill="{D.rad([(0, "#FFFFFF", 1), (0.3, "#FFFFFF", 0.85), (0.55, pal[0], 0.3), (1, pal[1], 0)])}"/>']
    for i in range(5):
        a = math.radians(rot_ + i * 72 - 90)
        inner.append(taper([(cx, cy), (cx + math.cos(a) * r, cy + math.sin(a) * r * tilt)], r * 0.18, r * 0.04, "#FFFFFF", 0.7))
        inner.append(pline([(cx + math.cos(a + 0.62) * r * 0.3, cy + math.sin(a + 0.62) * r * 0.3 * tilt), (cx + math.cos(a + 0.62) * r, cy + math.sin(a + 0.62) * r * tilt)], pal[2], 1, seed + i, 0.35, 1))
    out.append(clipped(D, d, inner))
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.1:.1f}" fill="#F6E8A0"/>')
    return "".join(out)


def heart_leaf(D, x, y, s, ang, seed, pal=("#A8D878", "#4E9A3A", "#1E5A1E")):
    pts = rot([(x + px * s, y + py * s) for px, py in heart_d(0, 0, 1)], x, y, ang)
    pts = [(px, py) for px, py in pts]
    return painted(D, pts, pal, seed, sdir=(0.5, 0.8), sk=0.12, angle=ang - 90, n=8, inkw=1.2, inkc="#1E4A1A", hi=0.35) + \
        pline([(x, y - s * 0.5), (x + math.sin(math.radians(-ang)) * 0, y + s * 0.9)], pal[0], 1, seed, 0.6, 1)


@design("furin")
def furin():
    D = Doc2("jp-fr")
    out = [sky(D, [(0, "#3A8AD8"), (0.6, "#8AC8F0"), (1, "#D8F0F8")], 1601, 600, ["#5AA0E0", "#FFFFFF", "#B0DCF4"], 70, angle=-4, sop=(0.08, 0.2))]
    out.append(puff_cloud(D, 400, 430, 330, 1602))
    out.append(puff_cloud(D, 90, 300, 150, 1603, op=0.9, rows=1))
    # eave across the top: tiled roof edge, rafter ends and a wooden beam
    out.append(f'<path d="M -10 -10 L 610 -10 L 610 46 L -10 64 Z" fill="#3A3A4A"/>')
    for k in range(16):
        x = -10 + k * 42
        out.append(f'<path d="{blob(x + 20, 52 - k * 1.1, 22, 10, 1604 + k, 0.08, 12)}" fill="#55556A"/>' + f'<path d="{blob(x + 16, 48 - k * 1.1, 12, 4, 1605 + k, 0.1, 8)}" fill="#8A8AA0" opacity="0.6"/>')
    beam = [(-10, 64), (610, 46), (610, 78), (-10, 96)]
    out.append(painted(D, densify(beam, 40), DARKWOOD, 1606, sdir=(0, 1), sk=0.25, angle=-2, n=40, inkw=1.6, hi=0.3))
    for k in range(7):
        x = 20 + k * 92
        y = 96 - x * 0.03
        out.append(painted(D, round_poly([(x - 12, y - 4), (x + 12, y - 4), (x + 12, y + 16), (x - 12, y + 16)], 3), HINOKI, 1607 + k, sk=0.25, n=4, inkw=1, hi=0.4))
    # bamboo screen and morning glories climbing at the right
    for k in range(3):
        x = 500 + k * 34
        out.append(taper([(x, 610), (x + 2, 300), (x, 110)], 9, 8, "#B8A060"))
        for y in (180, 300, 420, 540):
            out.append(f'<path d="M {x - 5} {y} L {x + 5} {y}" stroke="#7A6A30" stroke-width="2"/>')
    vine = catmull([(540, 600), (520, 500), (548, 420), (518, 340), (540, 260), (514, 180), (530, 120)], 6)
    out.append(pline(vine, "#3E7A2A", 2.4, 1610, 0.9, 1))
    for k, (t, sg) in enumerate(((0.15, 1), (0.3, -1), (0.48, 1), (0.62, -1), (0.8, 1), (0.92, -1))):
        x, y = vine[int(t * (len(vine) - 1))]
        out.append(heart_leaf(D, x + sg * 22, y, 20, sg * 30 + 180, 1611 + k))
    out.append(asagao(D, 470, 250, 34, 1620))
    out.append(asagao(D, 540, 380, 30, 1621, ("#F6B0D0", "#D8408A", "#8A1A4A"), 20))
    out.append(asagao(D, 486, 484, 28, 1622, ("#A8C8F8", "#3A6AD0", "#1A307A"), -10))
    # the furin: glass bell with goldfish painted inside, glass clapper, paper strip in the breeze
    fx, ftop = 250, 150
    out.append(pline([(fx, 90), (fx, 128)], "#5A4A3A", 2.4, 1630, 0.9, 1))
    out.append('<g transform="translate(250 112) scale(1.4) translate(-250 -150)">')
    out.append(soft_glow(D, fx, 210, 120, "#FFFFFF", 0.35))
    bell = [(fx, ftop - 2)]
    for i in range(1, 21):
        t = i / 20
        bell.append((fx + 54 * math.sin(math.pi / 2 * t) ** 0.9, ftop + 92 * (1 - math.cos(math.pi / 2 * t)) ** 1.1 + 2))
    bell = bell + [(fx + 60, ftop + 96), (fx - 60, ftop + 96)] + [(2 * fx - x, y) for x, y in bell[::-1][:-1]]
    bd = smooth_closed(bell)
    out.append(f'<path d="{bd}" fill="#E8F6FF" opacity="0.55"/>')
    glass = [f'<path d="{bd}" fill="{D.lin([(0, "#FFFFFF", 0.6), (0.5, "#C8E8FA", 0.2), (1, "#7AB8E0", 0.45)], 0, 0, 1, 0)}"/>']
    # goldfish and water weed painted on the inside of the glass
    for k, (gx, gy, a, sz) in enumerate(((fx - 22, ftop + 50, -10, 1.0), (fx + 24, ftop + 70, 170, 0.8))):
        body = rot(blob_pts(gx, gy, 13 * sz, 7 * sz, 1631 + k, 0.05, 12), gx, gy, a)
        glass.append(f'<path d="{smooth_closed(body)}" fill="#E8382A"/>')
        tail = rot([(gx + 10 * sz, gy), (gx + 24 * sz, gy - 10 * sz), (gx + 20 * sz, gy), (gx + 24 * sz, gy + 10 * sz)], gx, gy, a)
        glass.append(f'<path d="{smooth_closed(tail)}" fill="#F26A4A" opacity="0.85"/>')
        ex, ey = rot([(gx - 7 * sz, gy - 2 * sz)], gx, gy, a)[0]
        glass.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="1.6" fill="#1A1010"/>')
    for k in range(3):
        x0 = fx - 30 + k * 26
        glass.append(taper(catmull([(x0, ftop + 96), (x0 + 6, ftop + 76), (x0 - 4, ftop + 60)], 4), 4, 1, "#3E9A4A", 0.75))
    glass.append(taper([(fx - 40, ftop + 30), (fx - 48, ftop + 60), (fx - 46, ftop + 86)], 2, 6, "#FFFFFF", 0.85))
    glass.append(taper([(fx - 20, ftop + 12), (fx - 30, ftop + 28)], 2, 4, "#FFFFFF", 0.8))
    out.append(clipped(D, bd, glass))
    out.append(ink(bd, "#4A7A9A", 1.6, 1632, 1, 0.6))
    out.append(f'<ellipse cx="{fx}" cy="{ftop + 96}" rx="60" ry="9" fill="none" stroke="#5A8AAA" stroke-width="2.6" opacity="0.8"/>')
    out.append(f'<ellipse cx="{fx}" cy="{ftop + 96}" rx="60" ry="9" fill="none" stroke="#FFFFFF" stroke-width="1" opacity="0.8" transform="translate(-1 -1)"/>')
    # clapper and tanzaku
    out.append(pline([(fx, ftop + 30), (fx, ftop + 128)], "#5A4A3A", 1.4, 1633, 0.9, 1))
    out.append(f'<path d="{blob(fx, ftop + 96, 5, 7, 1634, 0.1, 8)}" fill="#A8E0F0"/><circle cx="{fx - 1.5}" cy="{ftop + 93}" r="1.6" fill="#FFFFFF"/>')
    tz = [(fx - 11, ftop + 126), (fx + 11, ftop + 126), (fx + 26, ftop + 160), (fx + 42, ftop + 180), (fx + 24, ftop + 184), (fx + 8, ftop + 162)]
    out.append(painted(D, tz, ("#FFF6D8", "#F6D88A", "#C89A3A"), 1635, sdir=(0.9, 0.2), sk=0.18, angle=-75, n=12, inkw=1.4, hi=0.4))
    for k in range(2):
        out.append(f'<path d="{blob(fx + 6 + k * 14, ftop + 142 + k * 20, 3, 4.5, 1636 + k, 0.2, 8, 20)}" fill="#E8603A" opacity="0.8"/>')
    for k, (x, y) in enumerate(((fx + 56, ftop + 150), (fx + 70, ftop + 170), (fx + 84, ftop + 140))):
        out.append(pline([(x, y), (x + 14, y - 4)], "#FFFFFF", 2, 1640 + k, 0.7, 1))
    out.append('</g>')
    # lettering
    out.append(letters(D, 250, 508, "furin", SERIF_IT, 122, "#1E4A8A", ["#2E5AA8", "#14306A", "#4A7AC8"], 1650, max_w=340,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#A8C8F0"))
    out.append(ruled(250, 538, "THE SOUND OF SUMMER", "#C8402A", font=JOS, size=19, ls=5, line_w=24, gap=10))
    return finish_b(D, out, 1651, "#1A3050", 0.6)


# ================================================================ 17. kazoku — a family of kokeshi dolls
def kokeshi(D, cx, base, h, seed, body=("#F6E2B8", "#E8C890", "#A88050"), motif="kiku", col=AKA, hair="bob", band="#2E8A4A"):
    """Turned-wood kokeshi: round head with painted hair and a sleepy smile, a cylinder body painted with flowers."""
    rnd = random.Random(seed)
    hr = h * 0.2
    hy = base - h + hr
    bw = h * 0.17
    btop = hy + hr * 0.82
    out = [cast(D, cx + 8, base, bw * 1.5, 7, strength=0.45, seed=seed)]
    bp = [(cx - bw * 0.92, btop), (cx + bw * 0.92, btop), (cx + bw, btop + (base - btop) * 0.4), (cx + bw * 1.04, base - 4), (cx + bw * 0.9, base), (cx - bw * 0.9, base),
          (cx - bw * 1.04, base - 4), (cx - bw, btop + (base - btop) * 0.4)]
    out.append(painted(D, densify(bp, 12), body, seed, sdir=(1, 0.2), sk=0.22, angle=-90, n=24, inkw=1.6, hi=0.45))
    bd = smooth_closed(densify(bp, 12))
    inner = []
    # lathe rings (rokuro lines) top and bottom
    for y, c, w in ((btop + 6, col[1], 4), (btop + 13, band, 2.4), (base - 10, col[1], 4), (base - 17, band, 2.4)):
        inner.append(f'<path d="M {cx - bw * 1.1:.1f} {y:.1f} Q {cx:.1f} {y + 4:.1f} {cx + bw * 1.1:.1f} {y:.1f}" stroke="{c}" stroke-width="{w}" fill="none"/>')
    mid_y = (btop + base) / 2 + 4
    if motif == "kiku":
        for j in range(16):
            a = math.radians(j * 22.5)
            inner.append(taper([(cx + math.cos(a) * bw * 0.15, mid_y + math.sin(a) * bw * 0.15), (cx + math.cos(a) * bw * 0.72, mid_y + math.sin(a) * bw * 0.72)], bw * 0.16, bw * 0.06, col[1], 0.95))
        inner.append(f'<circle cx="{cx:.1f}" cy="{mid_y:.1f}" r="{bw * 0.16:.1f}" fill="#F6C83A"/>')
        for sg in (-1, 1):
            inner.append(leaf_simple(D, cx + sg * bw * 0.5, mid_y + bw * 0.7, bw * 0.6, bw * 0.16, 90 + sg * 50, ("#8ACB7A", band, "#145A2A"), seed + sg, vein=False, inkw=0))
    elif motif == "ume":
        for k, (dx, dy, r) in enumerate(((-0.35, -0.6, 0.34), (0.35, 0.1, 0.4), (-0.3, 0.75, 0.3))):
            fx, fy = cx + dx * bw, mid_y + dy * bw
            for j in range(5):
                a = math.radians(j * 72 + k * 20)
                inner.append(f'<circle cx="{fx + math.cos(a) * r * bw * 0.55:.1f}" cy="{fy + math.sin(a) * r * bw * 0.55:.1f}" r="{r * bw * 0.45:.1f}" fill="{col[1]}"/>')
            inner.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{r * bw * 0.25:.1f}" fill="#F6C83A"/>')
    elif motif == "stripes":
        for j in range(7):
            y = btop + 22 + j * (base - btop - 44) / 6
            inner.append(f'<path d="M {cx - bw * 1.1:.1f} {y:.1f} Q {cx:.1f} {y + 4:.1f} {cx + bw * 1.1:.1f} {y:.1f}" stroke="{col[1] if j % 2 else band}" stroke-width="3" fill="none"/>')
        inner.append(f'<path d="{blob(cx, mid_y, bw * 0.4, bw * 0.4, seed, 0.1, 10)}" fill="#FFFFFF" opacity="0.9"/>')
        for j in range(5):
            a = math.radians(j * 72)
            inner.append(f'<circle cx="{cx + math.cos(a) * bw * 0.2:.1f}" cy="{mid_y + math.sin(a) * bw * 0.2:.1f}" r="{bw * 0.16:.1f}" fill="#F08AA8"/>')
    inner.append(shade_over(D, bd, "#3A1A08", 0.35, 0, 0, 1, 0, 0.5))
    out.append(clipped(D, bd, inner))
    # head
    head = blob_pts(cx, hy, hr * 1.05, hr, seed + 2, 0.03, 20)
    out.append(painted(D, head, body, seed + 2, sdir=(0.9, 0.4), sk=0.18, angle=-60, n=12, inkw=1.6, hi=0.45))
    hd = smooth_closed(head)
    hair_p = []
    if hair == "bob":
        hair_p.append(f'<path d="{smooth_closed([(cx - hr * 1.1, hy + hr * 0.4), (cx - hr * 1.0, hy - hr * 0.8), (cx, hy - hr * 1.15), (cx + hr * 1.0, hy - hr * 0.8), (cx + hr * 1.1, hy + hr * 0.4), (cx + hr * 0.72, hy + hr * 0.42), (cx + hr * 0.7, hy - hr * 0.2), (cx, hy - hr * 0.32), (cx - hr * 0.7, hy - hr * 0.2), (cx - hr * 0.72, hy + hr * 0.42)])}" fill="#1E1614"/>')
    elif hair == "bun":
        hair_p.append(f'<path d="{smooth_closed([(cx - hr * 1.1, hy - hr * 0.1), (cx - hr * 0.9, hy - hr * 0.85), (cx, hy - hr * 1.15), (cx + hr * 0.9, hy - hr * 0.85), (cx + hr * 1.1, hy - hr * 0.1), (cx + hr * 0.6, hy - hr * 0.4), (cx, hy - hr * 0.55), (cx - hr * 0.6, hy - hr * 0.4)])}" fill="#1E1614"/>')
        for sg in (-1, 1):
            hair_p.append(f'<path d="{blob(cx + sg * hr * 0.92, hy + hr * 0.15, hr * 0.12, hr * 0.32, seed + sg, 0.1, 8)}" fill="#1E1614"/>')
    else:   # short, with a cap of hair and two side tufts
        hair_p.append(f'<path d="{smooth_closed([(cx - hr * 1.05, hy - hr * 0.2), (cx - hr * 0.85, hy - hr * 0.85), (cx, hy - hr * 1.12), (cx + hr * 0.85, hy - hr * 0.85), (cx + hr * 1.05, hy - hr * 0.2), (cx + hr * 0.5, hy - hr * 0.55), (cx, hy - hr * 0.62), (cx - hr * 0.5, hy - hr * 0.55)])}" fill="#1E1614"/>')
    hair_p.append(f'<path d="{blob(cx - hr * 0.3, hy - hr * 0.78, hr * 0.32, hr * 0.1, seed, 0.2, 8, -15)}" fill="#6A5A60" opacity="0.6"/>')
    out.append(clipped(D, hd, hair_p))
    out.append(ink(hd, INK, 1.6, seed + 3, 1, 0.6))
    if hair == "bun":
        out.append(painted(D, blob_pts(cx, hy - hr * 1.2, hr * 0.42, hr * 0.32, seed + 4, 0.05, 12), ("#4A3E3E", "#1E1614", "#0A0606"), seed + 4, sk=0.2, n=4, inkw=1, hi=0.3))
        out.append(f'<path d="M {cx - hr * 0.42:.1f} {hy - hr * 1.12:.1f} Q {cx:.1f} {hy - hr * 1.0:.1f} {cx + hr * 0.42:.1f} {hy - hr * 1.12:.1f}" stroke="{col[1]}" stroke-width="{max(2, hr * 0.12):.1f}" fill="none"/>')
    # face: sleepy crescent eyes, red lips, rosy cheeks
    for sg in (-1, 1):
        ex, ey = cx + sg * hr * 0.34, hy + hr * 0.08
        out.append(taper([(ex - hr * 0.16, ey), (ex, ey + hr * 0.07), (ex + hr * 0.16, ey)], max(1.6, hr * 0.06), max(1.2, hr * 0.04), "#1E1614", 0.95))
        out.append(taper([(ex - hr * 0.14, ey - hr * 0.2), (ex + hr * 0.14, ey - hr * 0.22)], max(1, hr * 0.03), 0.6, "#1E1614", 0.8))
        out.append(f'<ellipse cx="{cx + sg * hr * 0.55:.1f}" cy="{hy + hr * 0.38:.1f}" rx="{hr * 0.14:.1f}" ry="{hr * 0.09:.1f}" fill="#F28A8A" opacity="0.65"/>')
    out.append(f'<path d="{blob(cx, hy + hr * 0.5, hr * 0.07, hr * 0.05, seed + 5, 0.1, 8)}" fill="#D8241E"/>')
    return "".join(out)


def shoji(D, x0, y0, x1, y1, seed, cols=4, rows=6, frame=HINOKI, glow="#FFF2D0"):
    out = [f'<path d="{pd([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])}" fill="{glow}"/>']
    out.append(f'<path d="{pd([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])}" fill="{D.rad([(0, "#FFFFFF", 0.6), (1, "#E8C890", 0.4)], 0.45, 0.4, 0.8)}"/>')
    for i in range(1, cols):
        x = x0 + (x1 - x0) * i / cols
        out.append(f'<path d="M {x:.1f} {y0} L {x:.1f} {y1}" stroke="{frame[1]}" stroke-width="5"/>')
    for j in range(1, rows):
        y = y0 + (y1 - y0) * j / rows
        out.append(f'<path d="M {x0} {y:.1f} L {x1} {y:.1f}" stroke="{frame[1]}" stroke-width="5"/>')
    return "".join(out)


@design("kazoku")
def kazoku():
    D = Doc2("jp-kz")
    out = [paper(D.nid(), "#F2E6D0", FLECK, 1701)]
    # glowing shoji behind, wooden posts
    out.append(shoji(D, 40, 216, 560, 486, 1702, cols=6, rows=4))
    rnd = random.Random(1703)
    out.append(strokes(D.nid(), pd([(40, 216), (560, 216), (560, 470), (40, 470)]), (40, 216, 560, 470), ["#FFFFFF", "#E8D0A8"], 1704, n=60, angle=-80, length=(20, 60), width=(2, 6), opacity=(0.08, 0.18)))
    # maple leaf shadow on the paper
    for k, (x, y, sz, a) in enumerate(((120, 280, 20, 10), (150, 320, 16, -20), (470, 260, 18, 30))):
        out.append(f'<g opacity="0.18">{maple_leaf(x, y, sz, "#7A5A4A", "#7A5A4A", a, 1705 + k)}</g>')
    for x in (36, 564):
        out.append(painted(D, densify([(x - 14, 196), (x + 14, 196), (x + 14, 490), (x - 14, 490)], 30), DARKWOOD, 1706 + x, sdir=(1, 0), sk=0.25, angle=-90, n=16, inkw=1.4, hi=0.3))
    out.append(painted(D, densify([(10, 196), (590, 196), (590, 216), (10, 216)], 40), DARKWOOD, 1708, sdir=(0, 1), sk=0.25, angle=0, n=20, inkw=1.4, hi=0.3))
    # shelf
    out.append(wood_planks(D, 486, 600, 1709, HINOKI, 2))
    out.append(f'<rect y="482" width="600" height="8" fill="#5A3A1A" opacity="0.6"/>')
    out.append(soft_glow(D, 300, 400, 230, "#FFF6D8", 0.5))
    # papa, mama, the big kid and the little one
    out.append(kokeshi(D, 150, 528, 300, 1710, motif="stripes", col=AI, hair="short", band="#C8402A"))
    out.append(kokeshi(D, 296, 528, 262, 1711, motif="kiku", col=AKA, hair="bun", band="#2E8A4A"))
    out.append(kokeshi(D, 420, 528, 190, 1712, motif="ume", col=("#F6B0C8", "#E8608A", "#A0285A"), hair="bob", band="#3A7AC8"))
    out.append(kokeshi(D, 508, 528, 128, 1713, motif="kiku", col=("#FFD07A", "#F2A21E", "#A86A0A"), hair="bob", band="#C8402A"))
    # lettering
    out.append(letters(D, 300, 146, "kazoku", SERIF_IT, 112, "#9A241E", ["#C8402A", "#7A140E", "#E06A4A"], 1720, max_w=380,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFB8A0"))
    out.append(ruled(300, 184, "FAMILY, ALWAYS", "#2E3A6A", font=JOS, size=20, ls=8, line_w=32, gap=12))
    return finish_b(D, out, 1721)


# ================================================================ 18. wan wan! — a shiba on the engawa in autumn
def shiba(D, cx, base, s, seed):
    """Red shiba inu sitting facing us: triangle ears, white urajiro cheeks and chest, a happy open mouth, curled tail."""
    k = s
    P = lambda x, y: (cx + x * k, base + y * k)
    L = lambda pts: [P(x, y) for x, y in pts]
    RED = ("#F2A868", "#D8783A", "#8A4018")
    CRM = ("#FFFFFF", "#FBF2E4", "#C8B49A")
    out = [cast(D, cx + 10 * k, base + 2, 120 * k, 12 * k, strength=0.45, seed=seed)]
    # curled tail peeking over the right hip
    tail = L([(62, -86), (92, -110), (112, -96), (108, -66), (90, -54), (78, -70), (94, -82), (84, -94), (70, -84)])
    out.append(painted(D, tail, RED, seed, sdir=(0.6, 0.6), sk=0.2, angle=-60, n=14, inkw=1.6, hi=0.4))
    out.append(taper(L([(80, -88), (98, -96), (104, -80)]), 6 * k, 2 * k, CRM[1], 0.9))
    # body / haunches
    body = L([(-52, -150), (52, -150), (74, -100), (88, -40), (84, -6), (56, 0), (-56, 0), (-84, -6), (-88, -40), (-74, -100)])
    out.append(painted(D, body, RED, seed + 1, sdir=(0.7, 0.4), sk=0.18, angle=-80, n=40, slen=(8, 24), sw=(1.2, 3), inkw=2, hi=0.45))
    # white chest and front legs
    chest = L([(-36, -156), (36, -156), (40, -110), (30, -60), (26, -4), (6, 0), (0, -60), (-6, 0), (-26, -4), (-30, -60), (-40, -110)])
    out.append(painted(D, chest, CRM, seed + 2, sdir=(0.7, 0.4), sk=0.15, angle=-90, n=26, inkw=1.6, hi=0.3))
    for sg in (-1, 1):
        out.append(pline(L([(sg * 3, -70), (sg * 2, -4)]), "#C8B49A", 1.6, seed + sg, 0.7, 1))
        for t in (-6, 0, 6):
            out.append(pline(L([(sg * 15 + t, -6), (sg * 15 + t, 0)]), "#B8A48A", 1.2, seed + t, 0.7, 1))
    # collar with a tag
    out.append(taper(L([(-40, -152), (0, -142), (40, -152)]), 9 * k, 9 * k, "#2E5AA8"))
    out.append(f'<path d="{blob(*P(0, -134), 7 * k, 8 * k, seed + 3, 0.05, 10)}" fill="#E8B838"/>' + ink(blob(*P(0, -134), 7 * k, 8 * k, seed + 3, 0.05, 10), "#7A4A08", 1.2, seed, 1, 0.6))
    # head
    head = L([(-58, -214), (-46, -248), (-18, -262), (18, -262), (46, -248), (58, -214), (54, -180), (32, -156), (0, -150), (-32, -156), (-54, -180)])
    for sg in (-1, 1):
        ear = L([(sg * 24, -252), (sg * 50, -300), (sg * 60, -238)])
        out.append(painted(D, ear, RED, seed + 4 + sg, sdir=(0.6, 0.6), sk=0.2, angle=-80, n=6, inkw=1.6, hi=0.35))
        out.append(f'<path d="{smooth_closed(L([(sg * 32, -250), (sg * 49, -288), (sg * 54, -244)]))}" fill="#F6D8C0"/>')
    out.append(painted(D, head, RED, seed + 6, sdir=(0.6, 0.6), sk=0.15, angle=-60, n=30, inkw=2, hi=0.45))
    # white urajiro: cheeks, muzzle, eyebrow dots
    mz = L([(-44, -200), (-24, -210), (0, -204), (24, -210), (44, -200), (48, -178), (30, -160), (0, -154), (-30, -160), (-48, -178)])
    out.append(painted(D, mz, CRM, seed + 7, sdir=(0.6, 0.6), sk=0.12, angle=-40, n=12, inkw=0, hi=0.3))
    for sg in (-1, 1):
        out.append(f'<path d="{blob(*P(sg * 20, -238), 7 * k, 4.5 * k, seed + 8 + sg, 0.1, 8)}" fill="#FBF2E4"/>')
        ex, ey = P(sg * 22, -222)
        out.append(f'<path d="{blob(ex, ey, 7 * k, 7.5 * k, seed + 10 + sg, 0.05, 10)}" fill="#1A1210"/>')
        out.append(f'<circle cx="{ex - 2 * k:.1f}" cy="{ey - 3 * k:.1f}" r="{2.2 * k:.1f}" fill="#FFFFFF"/>')
        out.append(taper(L([(sg * 14, -228), (sg * 22, -231), (sg * 30, -227)]), 1.6 * k, 1, "#5A2A10", 0.7))
    # nose and smiling open mouth with a pink tongue
    out.append(f'<path d="{blob(*P(0, -194), 9 * k, 6.5 * k, seed + 12, 0.05, 10)}" fill="#1A1210"/>')
    out.append(f'<circle cx="{P(-3, -196)[0]:.1f}" cy="{P(-3, -196)[1]:.1f}" r="{2 * k:.1f}" fill="#FFFFFF" opacity="0.7"/>')
    out.append(pline(L([(0, -188), (0, -180)]), "#1A1210", 2 * k, seed, 0.9, 1))
    mouth = L([(-20, -182), (-10, -176), (0, -180), (10, -176), (20, -182), (12, -166), (0, -162), (-12, -166)])
    out.append(f'<path d="{smooth_closed(mouth)}" fill="#5A1A14"/>')
    out.append(f'<path d="{smooth_closed(L([(-9, -170), (9, -170), (8, -160), (0, -156), (-8, -160)]))}" fill="#F27A88"/>')
    out.append(pline(L([(-22, -183), (-10, -177), (0, -181), (10, -177), (22, -183)]), "#1A1210", 2 * k, seed + 13, 0.9, 1))
    # fur ticks along the edges
    rnd = random.Random(seed)
    for _ in range(40):
        a = rnd.uniform(0, 2 * math.pi)
        x, y = P(math.cos(a) * 56, -206 + math.sin(a) * 52)
        out.append(pline([(x, y), (x + math.cos(a) * 5 * k, y + math.sin(a) * 5 * k)], "#B85A20", 1, seed + _, 0.5, 1))
    return "".join(out)


def kaki(D, cx, cy, r, seed):
    """Persimmon: flattened orange globe, four-leaf green calyx."""
    pts = blob_pts(cx, cy, r, r * 0.84, seed, 0.04, 16)
    out = [painted(D, pts, ("#FFB860", "#F07A1E", "#A8400A"), seed, sdir=(0.6, 0.8), sk=0.2, n=8, inkw=1.2, inkc="#7A3008", hi=0.45)]
    for j in range(4):
        a = math.radians(j * 90 + 45)
        out.append(f'<path d="{blob(cx + math.cos(a) * r * 0.25, cy - r * 0.62 + math.sin(a) * r * 0.12, r * 0.28, r * 0.12, seed + j, 0.1, 8, math.degrees(a))}" fill="#5A7A2A"/>')
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.25, r * 0.18, r * 0.1, seed, 0.2, 8, -30)}" fill="#FFFFFF" opacity="0.6"/>')
    return "".join(out)


@design("wan-wan")
def wan_wan():
    D = Doc2("jp-ww")
    out = [sky(D, [(0, "#9ACBE8"), (0.7, "#E8F0E8"), (1, "#F6EED8")], 1801, 360, ["#B8DCF0", "#FFFFFF"], 50, angle=-3, sop=(0.08, 0.18))]
    # garden: soft hills of foliage, a persimmon tree heavy with fruit
    out.append(dab_crown(D, 110, 300, 170, 90, [("#E8A050", "#C8602A", "#7A3A14"), ("#F2C060", "#D89A2A", "#8A5A10")], 1802, n=170, size=(8, 15), inkw=0))
    out.append(dab_crown(D, 520, 290, 150, 100, [("#9AC070", "#5A8A3A", "#2E5A22"), ("#B8C870", "#7A9A3A", "#3E5A1A")], 1803, n=160, size=(8, 15), inkw=0))
    out.append(taper(catmull([(430, 370), (440, 290), (480, 230), (540, 200)], 5), 14, 6, "#5A3A26"))
    out.append(taper(catmull([(466, 254), (420, 214), (380, 200)], 5), 7, 3, "#5A3A26"))
    for k, (x, y, r) in enumerate(((390, 212, 16), (430, 238, 18), (498, 222, 17), (536, 250, 15), (460, 286, 16), (372, 246, 14))):
        out.append(kaki(D, x, y, r, 1804 + k))
    for k, (x, y, a) in enumerate(((410, 200, -30), (480, 206, 20), (450, 254, 160), (516, 230, 60))):
        out.append(leaf_simple(D, x, y, 30, 10, a, ("#B8A040", "#8A6A20", "#4A3A10"), 1810 + k, vein=False, inkw=0.9))
    # shoji wall at the left edge and the veranda
    out.append(shoji(D, -10, 120, 110, 382, 1815, cols=2, rows=5))
    out.append(painted(D, densify([(104, 110), (122, 110), (122, 392), (104, 392)], 30), DARKWOOD, 1816, sdir=(1, 0), sk=0.25, angle=-90, n=10, inkw=1.4, hi=0.3))
    out.append(wood_planks(D, 380, 600, 1817, ("#D8A878", "#A8703E", "#5A3418"), 5))
    out.append(f'<rect y="376" width="600" height="8" fill="#3A2210" opacity="0.6"/>')
    out.append(f'<rect y="384" width="600" height="216" fill="{D.lin([(0, "#3A1A08", 0.15), (1, "#3A1A08", 0)])}"/>')
    # fallen maple leaves on the boards
    for k, (x, y, sz, a) in enumerate(((120, 520, 16, 20), (480, 548, 14, -40), (530, 470, 12, 70), (90, 446, 11, -10))):
        out.append(maple_leaf(x, y, sz, "#D8402A", "#8A1A10", a, 1818 + k))
    # a cup of tea left on the veranda
    out.append(painted(D, [(456, 470), (500, 470), (496, 506), (460, 506)], ("#E8E0C8", "#B8A880", "#6A5A3A"), 1822, sdir=(1, 0.2), sk=0.25, angle=-90, n=8, inkw=1.4, hi=0.4))
    out.append(f'<ellipse cx="478" cy="470" rx="22" ry="5" fill="#8AA040"/>' + ink(smooth_closed(ell_pts(478, 470, 22, 5, 0, 360, 16)), INK, 1.2, 1823, 1, 0.6))
    out.append(steam(478, 462, 34, 1824, "#FFFFFF", 2, 14, 4, 0.6))
    # the dog
    out.append(shiba(D, 290, 526, 1.12, 1825))
    # lettering
    out.append(letters(D, 300, 126, "wan wan!", SERIF_IT, 100, "#9A3A12", ["#C8602A", "#7A2A0A", "#E08A4A"], 1830, max_w=380,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFC8A0"))
    out.append(label(300, 160, "WOOF, IN JAPANESE", JOS, 18, "#2E4A6A", ls=6))
    return finish_b(D, out, 1831)


# ================================================================ 19. tsuru — a red-crowned crane on a gold-leaf screen
def red_crowned_crane(D, ox, oy, s, seed):
    """Tancho standing, facing left, one wing lifted: white plumage, black neck and drooping black secondaries,
    red crown. (ox, oy) = feet."""
    k = s
    P = lambda x, y: (ox + x * k, oy + y * k)
    L = lambda pts: [P(x, y) for x, y in pts]
    rnd = random.Random(seed)
    WH = ("#FFFFFF", "#F6F2EA", "#B8B4C0")
    out = [f'<ellipse cx="{ox + 6:.1f}" cy="{oy + 2:.1f}" rx="{60 * k:.1f}" ry="{6 * k:.1f}" fill="#3A2408" opacity="0.25"/>']
    # legs
    for dx, bend in ((-10, -4), (14, 6)):
        out.append(taper(L([(dx, -150), (dx + bend, -80), (dx - 2, -4)]), 5 * k, 3.6 * k, "#3A3A44"))
        out.append(taper(L([(dx - 2, -2), (dx - 20, 2)]), 3 * k, 1.5 * k, "#3A3A44"))
        out.append(taper(L([(dx - 2, -2), (dx + 12, 3)]), 3 * k, 1.5 * k, "#3A3A44"))
    # raised far wing behind the body: white coverts, fingered white primaries, a band of black secondaries
    wing = L([(-30, -214), (-6, -262), (40, -306), (96, -336), (150, -344), (176, -334), (168, -318), (182, -306), (166, -294), (176, -280), (150, -272),
              (126, -252), (92, -232), (56, -212)])
    out.append(painted(D, wing, WH, seed, sdir=(0.6, 0.6), sk=0.12, angle=-35, n=26, inkw=1.6, inkc="#5A5048", hi=0.35))
    for j in range(8):
        t = j / 7
        bx, by = P(40 + 100 * t, -238 - 50 * t)
        ex, ey = P(64 + 100 * t + 6, -206 - 46 * t + 4)
        out.append(taper([(bx, by), ((bx + ex) / 2 + 2, (by + ey) / 2), (ex, ey)], 13 * k, 3, "#18161E", 0.95))
    for j in range(5):
        out.append(pline(L([(150 + j * 4, -340 + j * 12), (180 - j * 2, -332 + j * 13)]), "#C8C4D0", 1.2, seed + j, 0.6, 1))
    for j in range(6):
        out.append(pline(L([(0 + j * 22, -248 - j * 15), (24 + j * 22, -264 - j * 14)]), "#D8D4DC", 1.2, seed + j, 0.5, 1))
    # body
    body = L([(-80, -230), (-40, -250), (30, -244), (90, -214), (110, -190), (80, -160), (20, -146), (-40, -156), (-80, -186)])
    out.append(painted(D, body, WH, seed + 1, sdir=(0.5, 0.8), sk=0.18, angle=-10, n=30, inkw=1.8, inkc="#5A5048", hi=0.35))
    # drooping black secondaries (the 'tail')
    for j in range(9):
        t = j / 8
        bx, by = P(40 + 50 * t, -214 + 20 * t)
        ex, ey = P(100 + 40 * t + rnd.uniform(-4, 4), -160 + 26 * t + rnd.uniform(-4, 4))
        out.append(taper([(bx, by), ((bx + ex) / 2 + 6, (by + ey) / 2), (ex, ey)], 12 * k, 2, "#18161E", 0.95))
    # neck: black throat, white nape, small head with red crown and a long bill
    neck_b = L([(-78, -222), (-102, -268), (-110, -318), (-100, -356), (-82, -368), (-72, -352), (-82, -318), (-72, -276), (-46, -236)])
    out.append(painted(D, neck_b, ("#4A4A56", "#1E1C24", "#08080C"), seed + 2, sdir=(0.8, 0.3), sk=0.1, angle=-80, n=12, inkw=1.4, inkc="#08080C", hi=0.25))
    nape = L([(-80, -352), (-76, -366), (-66, -360), (-70, -330), (-60, -292), (-46, -252), (-56, -246), (-74, -292)])
    out.append(painted(D, nape, WH, seed + 3, sdir=(0.8, 0.3), sk=0.1, angle=-80, n=6, inkw=0.8, inkc="#5A5048", hi=0.2))
    head = L([(-100, -360), (-96, -374), (-84, -380), (-72, -374), (-70, -362), (-82, -356), (-96, -352)])
    out.append(painted(D, head, ("#4A4A56", "#1E1C24", "#08080C"), seed + 4, sk=0.1, n=4, inkw=1, hi=0.2))
    out.append(f'<path d="{blob(*P(-84, -377), 9 * k, 4.5 * k, seed + 5, 0.1, 8)}" fill="#E8282A"/>')
    out.append(f'<path d="{smooth_closed(L([(-76, -368), (-66, -364), (-68, -354), (-76, -358)]))}" fill="#FFFFFF"/>')
    bill = L([(-98, -368), (-150, -360), (-152, -357), (-98, -358)])
    out.append(painted(D, bill, ("#C8C8A0", "#8A8A6A", "#4A4A3A"), seed + 6, sk=0.2, n=4, inkw=1, hi=0.3))
    out.append(f'<circle cx="{P(-92, -367)[0]:.1f}" cy="{P(-92, -367)[1]:.1f}" r="{2 * k:.1f}" fill="#F6E8C0"/>')
    return "".join(out)


def origami_crane(D, cx, cy, s, seed, pal=("#FFB0B8", "#E8505A", "#8A1A24")):
    """Folded paper crane: flat faceted body, two wings raised, pointed neck and tail, a creased head."""
    P = lambda x, y: (cx + x * s, cy + y * s)
    faces = [([(-8, 0), (0, -14), (8, 0), (0, 16)], pal[1]),                 # body front
             ([(0, -14), (8, 0), (34, -48)], pal[0]),                        # right wing front face
             ([(0, -14), (-8, 0), (-30, -52)], lt(pal[0], 0.2)),             # left wing
             ([(-8, 0), (0, 16), (-40, -18)], pal[2]),                       # neck lower face
             ([(-40, -18), (-8, 0), (-30, -8)], pal[1]),
             ([(8, 0), (0, 16), (44, -14)], dk(pal[1], 0.1)),                # tail
             ([(-40, -18), (-50, -10), (-42, -12)], pal[2])]                 # head fold
    out = [f'<ellipse cx="{cx + 4:.1f}" cy="{cy + 20 * s:.1f}" rx="{30 * s:.1f}" ry="{4 * s:.1f}" fill="#3A2408" opacity="0.25"/>']
    for pts, c in faces:
        pp = [P(x, y) for x, y in pts]
        out.append(f'<path d="{pd(pp)}" fill="{c}" stroke="{pal[2]}" stroke-width="{max(0.8, s * 0.06):.1f}" stroke-linejoin="round"/>')
    out.append(f'<path d="{pd([P(0, -14), P(0, 16)], False)}" stroke="{lt(pal[0], 0.5)}" stroke-width="{max(0.8, s * 0.05):.1f}" opacity="0.7"/>')
    return "".join(out)


@design("tsuru")
def tsuru():
    D = Doc2("jp-ts")
    out = [f'<rect width="600" height="600" fill="{D.lin([(0, "#F2D07A"), (0.5, "#E2B454"), (1, "#C8963A")], 0, 0, 1, 1)}"/>']
    rnd = random.Random(1901)
    # gold leaf squares, each laid slightly differently
    for y in range(-10, 610, 58):
        for x in range(-10 + (0 if (y // 58) % 2 else 29), 610, 58):
            c = rnd.choice(["#F6D886", "#E8C062", "#F2CC70", "#DAB050", "#FFE29A"])
            out.append(f'<rect x="{x}" y="{y}" width="58" height="58" fill="{c}" opacity="0.55"/><rect x="{x}" y="{y}" width="58" height="58" fill="none" stroke="#B8862E" stroke-width="0.8" opacity="0.35"/>')
    out.append(specks(1902, (0, 0, 600, 600), ["#FFF2C0", "#B8862E", "#FFFFFF"], 160, (0.6, 2), (0.3, 0.8)))
    # rinpa stream: silver-blue water with swirling lines across the lower half
    st = catmull([(-20, 470), (120, 440), (260, 470), (400, 450), (620, 470)], 8)
    sb = catmull([(620, 560), (420, 540), (260, 570), (100, 548), (-20, 566)], 8)
    sd = smooth_closed(st + sb)
    out.append(f'<path d="{sd}" fill="#5A7090"/>')
    sw = []
    for row in range(5):
        for k in range(9):
            x0 = -30 + k * 76 + row * 22
            y0 = 466 + row * 18
            sw.append(f'<path d="M {x0} {y0} q 18 -14 36 0 q 10 8 0 14 q -8 4 -10 -4" stroke="#C8D4E4" stroke-width="2.2" fill="none" opacity="0.75"/>')
    out.append(clipped(D, sd, sw))
    out.append(ink(smooth_open(st), "#2A3A58", 2, 1903, 1, 0.6))
    out.append(ink(smooth_open(sb), "#2A3A58", 2, 1904, 1, 0.6))
    # malachite bank with reeds at the bottom right
    bank = [(380, 600), (420, 560), (500, 540), (620, 536), (620, 600)]
    out.append(painted(D, bank, ("#6AAA7A", "#2E7A5A", "#14483A"), 1905, sdir=(0.3, 1), sk=0.15, angle=-10, n=20, inkw=1.6, hi=0.3))
    out.append(grass(1906, (420, 520, 600, 560), ["#2E6A4A", "#1E4A34", "#4E8A5A"], 30, (24, 60), 2.4, (-0.3, 0.1)))
    # the crane, and a folded paper crane beside the stream
    out.append(red_crowned_crane(D, 394, 518, 0.82, 1907))
    out.append(origami_crane(D, 160, 400, 2.3, 1908))
    out.append(origami_crane(D, 246, 486, 1.2, 1909, ("#FFF0B0", "#E8B838", "#8A6418")))
    out.append(origami_crane(D, 96, 500, 0.9, 1913, ("#B8D0F0", "#4A7AC8", "#1A3A7A")))
    # lettering
    out.append(letters(D, 300, 140, "tsuru", SERIF_IT, 120, "#1E1A1E", ["#3A3440", "#0A080C", "#4A4450"], 1910, max_w=330,
                       shadow="#FFF2C0", soff=(0.02, 0.035), angle=-40, hi="#8A8090"))
    out.append(ruled(300, 178, "A THOUSAND CRANES FOR LUCK", "#8A1A1A", font=JOS, size=17, ls=4, line_w=20, gap=10, max_w=400))
    return finish_b(D, out, 1912, "#5A3A08", 0.6)


# ================================================================ 20. mejiro — a naturalist's plate: white-eye on plum blossom
def mejiro_bird(D, ox, oy, s, seed, flip=1):
    """Japanese white-eye perched, facing right: olive-green back, yellow throat, a bold white eye-ring. (ox, oy) = feet."""
    k = s
    P = lambda x, y: (ox + x * k * flip, oy + y * k)
    L = lambda pts: [P(x, y) for x, y in pts]
    GR = ("#C8D870", "#8AA032", "#4A5A14")
    out = []
    tail = L([(-40, -40), (-96, -10), (-100, 0), (-88, 2), (-36, -24)])
    out.append(painted(D, tail, ("#9AA05A", "#5E6A2A", "#2E3810"), seed, sdir=(0.3, 1), sk=0.2, angle=170, n=8, inkw=1.4, hi=0.3))
    body = L([(-50, -56), (-20, -86), (20, -96), (52, -84), (64, -60), (54, -30), (24, -12), (-14, -12), (-44, -28)])
    out.append(painted(D, body, GR, seed + 1, sdir=(0.4, 0.9), sk=0.18, angle=170, n=30, inkw=1.6, inkc="#3A4010", hi=0.4))
    belly = L([(-30, -30), (10, -40), (50, -52), (58, -38), (34, -16), (-10, -12)])
    out.append(painted(D, belly, ("#FFFFF4", "#EAE4D0", "#B8AE90"), seed + 2, sdir=(0.3, 1), sk=0.15, angle=0, n=10, inkw=0, hi=0.3))
    out.append(f'<path d="{smooth_closed(L([(34, -56), (56, -58), (62, -46), (44, -42)]))}" fill="#C8A890" opacity="0.6"/>')
    wing = L([(-34, -64), (0, -82), (30, -72), (20, -52), (-20, -40), (-56, -30)])
    out.append(painted(D, wing, ("#AABA5A", "#6E7E24", "#36400C"), seed + 3, sdir=(0.4, 0.9), sk=0.2, angle=170, n=12, inkw=1.4, hi=0.3))
    for j in range(4):
        out.append(pline(L([(-30 + j * 10, -54 + j * 2), (-52 + j * 6, -34)]), "#3A4410", 1.2, seed + j, 0.6, 1))
    head = L([(30, -96), (48, -118), (72, -120), (88, -104), (86, -84), (66, -72), (44, -76)])
    out.append(painted(D, head, GR, seed + 4, sdir=(0.4, 0.9), sk=0.15, angle=-30, n=10, inkw=1.6, inkc="#3A4010", hi=0.4))
    throat = L([(60, -80), (84, -88), (84, -74), (66, -64), (54, -66)])
    out.append(painted(D, throat, ("#FFF6A0", "#F2D840", "#A89010"), seed + 5, sk=0.15, n=5, inkw=0, hi=0.4))
    ex, ey = P(68, -100)
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{8.5 * k:.1f}" fill="#FFFFFF"/>')
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{8.5 * k:.1f}" fill="none" stroke="#C8C8B8" stroke-width="1"/>')
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{5 * k:.1f}" fill="#2A1A10"/><circle cx="{ex - 1.6 * k * flip:.1f}" cy="{ey - 1.6 * k:.1f}" r="{1.6 * k:.1f}" fill="#FFFFFF"/>')
    bk = L([(84, -102), (104, -98), (84, -94)])
    out.append(f'<path d="{smooth_closed(bk)}" fill="#3A3436"/>')
    for dx in (0, 16):
        fx, fy = P(dx, -12)
        out.append(taper([(fx, fy), (fx + 2 * flip, fy + 10 * k)], 3.4 * k, 2.4 * k, "#5A5A6A"))
        out.append(taper([(fx - 6 * k * flip, fy + 12 * k), (fx + 8 * k * flip, fy + 12 * k)], 2.4 * k, 1.6 * k, "#5A5A6A"))
    return "".join(out)


@design("mejiro")
def mejiro():
    D = Doc2("jp-mj2")
    out = [paper(D.nid(), "#F2EAD8", FLECK, 2001)]
    out.append(blooms(6, ["#E8D0D8", "#D8E0C0", "#F0E0C8"], 6, (100, 120, 500, 460), (110, 180), (0.12, 0.2)))
    out.append(f'<rect x="50" y="50" width="500" height="500" fill="none" stroke="#7A2A3A" stroke-width="2.2"/>')
    out.append(f'<rect x="58" y="58" width="484" height="484" fill="none" stroke="#7A2A3A" stroke-width="1.2" opacity="0.7"/>')
    for x, y in ((50, 50), (550, 50), (50, 550), (550, 550)):
        out.append(f'<path d="{blob(x, y, 7, 7, x + y, 0.1, 8)}" fill="#C8606A"/>')
    out.append(ruled(300, 94, "BIRDS OF JAPAN · Nº 3", "#7A2A3A", font=MONO, size=16, ls=4, line_w=26, gap=10))
    # the plum branch: gnarled, angular, with blossoms and fat buds
    main = catmull([(60, 420), (150, 400), (220, 360), (300, 356), (380, 330), (450, 300), (540, 250)], 6)
    out.append(bark_branch(D, main, 20, 8, 2002, pal=("#6A5048", "#3A2A26", "#1A1210")))
    for k, tw in enumerate((catmull([(220, 360), (200, 300), (230, 240), (214, 190)], 5), catmull([(380, 330), (410, 380), (470, 410)], 5),
                             catmull([(450, 300), (470, 240), (500, 200)], 5), catmull([(150, 400), (120, 450), (130, 480)], 5))):
        out.append(bark_branch(D, tw, 8, 3, 2003 + k, pal=("#6A5048", "#3A2A26", "#1A1210")))
    for k, (x, y, r) in enumerate(((214, 196, 15), (230, 250, 17), (196, 300, 14), (470, 406, 16), (500, 204, 15), (124, 470, 14), (90, 410, 15), (540, 252, 13), (270, 366, 13))):
        out.append(ume_flower(D, x, y, r, 2010 + k, k * 23, pal=("#FFFFFF", "#FCE4EA", "#D890A4") if k % 3 else ("#FFD8E0", "#F4A0B4", "#C05A78")))
    for k, (x, y) in enumerate(((236, 222), (476, 228), (420, 384), (160, 392), (340, 352))):
        out.append(f'<path d="{blob(x, y, 5.5, 7, 2020 + k, 0.1, 8)}" fill="#E06A84"/>' + ink(blob(x, y, 5.5, 7, 2020 + k, 0.1, 8), "#8A2A44", 1, k, 1, 0.6))
    # the white-eye, singing on the branch
    out.append(mejiro_bird(D, 330, 352, 1.35, 2030))
    # caption
    out.append(letters(D, 300, 492, "Mejiro", SERIF_IT, 62, "#3E5A1A", ["#5A7A2A", "#2A4010"], 2031, max_w=300, angle=-40, wob=0.6))
    out.append(label(300, 522, "ZOSTEROPS JAPONICUS", MONO, 16, "#7A2A3A", ls=4))
    return finish_b(D, out, 2032)


# ================================================================ 21. arigatou — a gift envelope tied with mizuhiki
def cord_band(pts, w, strands, cols, shadow=True):
    """Several thin paper cords running side by side along a path (one colour per strand)."""
    out = []
    sm = pts
    for j in range(strands):
        off = (j - (strands - 1) / 2) * w
        q = []
        for i in range(len(sm)):
            a, b = sm[max(0, i - 1)], sm[min(len(sm) - 1, i + 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            Ln = math.hypot(dx, dy) or 1
            q.append((sm[i][0] - dy / Ln * off, sm[i][1] + dx / Ln * off))
        if shadow:
            out.append(f'<path d="{smooth_open(q)}" stroke="#3A1008" stroke-width="{w * 1.25:.1f}" fill="none" opacity="0.25" transform="translate(1.4 1.8)"/>')
        out.append(f'<path d="{smooth_open(q)}" stroke="{dk(cols[j % len(cols)], 0.25)}" stroke-width="{w * 1.05:.1f}" fill="none" stroke-linecap="round"/>')
        out.append(f'<path d="{smooth_open(q)}" stroke="{cols[j % len(cols)]}" stroke-width="{w * 0.7:.1f}" fill="none" stroke-linecap="round"/>')
    return "".join(out)


def mizuhiki(D, cx, cy, w, seed, red=("#E8302A", "#D8241E", "#F04A3A"), white=("#FFFFFF", "#F2EEE8", "#FFFFFF"), x0=None, x1=None):
    """Awaji knot in paper cord, red half and white half: a three-lobed pretzel (two loops up, one down) sitting on the
    band that wraps the envelope, its two ends trailing down. Built from a mirrored trefoil so both halves match."""
    sw = w * 0.017
    sc = w * 0.085
    def pt(t):
        x = math.sin(t) + 2 * math.sin(2 * t)
        y = -(math.cos(t) - 2 * math.cos(2 * t))
        return (cx + x * sc, cy + (y - 0.6) * sc * 0.82)
    out = []
    if x0 is not None:
        out.append(cord_band([(x0, cy), (cx, cy + 1)], sw, 5, red))
        out.append(cord_band([(cx, cy + 1), (x1, cy)], sw, 5, white))
    n = 90
    # draw in an order that alternates over / under at the crossings: halves split into thirds
    red_pts = [pt(-math.pi + 0.18 + (math.pi - 0.18) * i / n) for i in range(n + 1)]
    white_pts = [pt(0 + (math.pi - 0.18) * i / n) for i in range(n + 1)]
    thirds = lambda P: (P[:31], P[30:61], P[60:])
    r1, r2, r3 = thirds(red_pts)
    w1, w2, w3 = thirds(white_pts)
    for seg, cols in ((r1, red), (w3, white), (r2, red), (w1, white), (w2, white), (r3, red)):
        out.append(cord_band(seg, sw, 5, cols))
    # the ends trail down and outward
    a, b = pt(-math.pi + 0.18), pt(math.pi - 0.18)
    out.append(cord_band([a, (a[0] - w * 0.06, a[1] + w * 0.12), (a[0] - w * 0.12, a[1] + w * 0.32)], sw, 5, red))
    out.append(cord_band([b, (b[0] + w * 0.06, b[1] + w * 0.12), (b[0] + w * 0.12, b[1] + w * 0.32)], sw, 5, white))
    return "".join(out)


@design("arigatou")
def arigatou():
    D = Doc2("jp-ar")
    out = [paper(D.nid(), "#F4ECDC", FLECK, 2101)]
    out.append(shippo(D, "M 0 0 L 600 0 L 600 600 L 0 600 Z", 30, "#D8C8A8", 1.2, 0.45))
    out.append(blooms(6, ["#F2D0D0", "#E8D8C0", "#FFE8E0"], 7, (40, 40, 560, 560), (120, 200), (0.12, 0.2)))
    out.append(soft_glow(D, 300, 380, 240, "#FFFFFF", 0.6))
    # the envelope, tilted a little on the table
    out.append('<g transform="translate(300 384) scale(0.98) rotate(-6) translate(-300 -380)">')
    env = round_poly([(214, 210), (386, 210), (386, 548), (214, 548)], 6)
    out.append(cast(D, 316, 556, 110, 12, strength=0.35, seed=2102))
    out.append(f'<path d="{pd([(220, 216), (392, 216), (392, 554), (220, 554)])}" fill="#3A2408" opacity="0.15"/>')
    out.append(painted(D, env, ("#FFFFFF", "#FBF8F0", "#D8D0C0"), 2103, sdir=(0.7, 0.4), sk=0.06, angle=-90, n=30, inkw=1.6, inkc="#8A7A68", hi=0.3))
    # folded flap lines and washi fibres
    out.append(pline([(214, 236), (300, 230), (386, 236)], "#C8BEB0", 1.4, 2104, 0.7, 1))
    out.append(pline([(244, 210), (244, 548)], "#E0D8CC", 1.2, 2105, 0.7, 1))
    rnd = random.Random(2106)
    for _ in range(30):
        x, y = rnd.uniform(220, 380), rnd.uniform(214, 544)
        out.append(f'<path d="M {x:.1f} {y:.1f} q {rnd.uniform(-4, 4):.1f} {rnd.uniform(-3, 3):.1f} {rnd.uniform(-10, 10):.1f} {rnd.uniform(-4, 4):.1f}" stroke="#C8BEB0" stroke-width="0.8" fill="none" opacity="0.6"/>')
    # noshi ornament at the top right
    nx, ny = 356, 252
    out.append(painted(D, [(nx - 10, ny - 30), (nx + 10, ny - 22), (nx + 12, ny + 22), (nx - 8, ny + 28)], ("#FFFFFF", "#F6F0E6", "#C8BEB0"), 2107, sk=0.2, n=4, inkw=1, hi=0.3))
    out.append(painted(D, [(nx - 6, ny - 26), (nx + 6, ny - 20), (nx + 6, ny + 18), (nx - 4, ny + 22)], ("#FF8A7A", "#D8241E", "#7A0A0A"), 2108, sk=0.2, n=4, inkw=0.8, hi=0.3))
    out.append(f'<path d="M {nx - 1} {ny - 18} L {nx + 1} {ny + 14}" stroke="#F6C83A" stroke-width="3"/>')
    # band of cord with the awaji knot
    out.append(mizuhiki(D, 300, 368, 250, 2109, x0=214, x1=386))
    out.append("</g>")
    # plum blossoms scattered around
    for k, (x, y, r) in enumerate(((112, 300, 16), (150, 360, 11), (476, 268, 14), (500, 470, 17), (96, 500, 12), (458, 540, 10))):
        out.append(ume_flower(D, x, y, r, 2110 + k, k * 20, pal=("#FFE0E8", "#F6A8BC", "#C85A7A")))
    # lettering
    out.append(letters(D, 300, 142, "arigatou", SERIF_IT, 116, "#B8241E", ["#D8402A", "#8A140E", "#E8604A"], 2120, max_w=420,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFB8A0"))
    out.append(ruled(300, 184, "THANK YOU, TRULY", "#2E3A6A", font=JOS, size=20, ls=7, line_w=30, gap=12))
    return finish_b(D, out, 2121)


# ================================================================ 22. kawaii — hanami dango with little faces
def dango_skewer(D, x0, y0, x1, y1, r, seed, cols=(("#FFD0DC", "#F6A0B8", "#C8607E"), ("#FFFFFF", "#F8F4EE", "#C8C0B8"), ("#D8F0B0", "#A8D078", "#5A8A3A")), faces=(0, 1, 2)):
    """A skewer of three soft rice dumplings (pink, white, green), each with a tiny face."""
    rnd = random.Random(seed)
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    out = [taper([(x0 - ux * 10, y0 - uy * 10), (x1, y1)], 6, 5, "#C8A060"), taper([(x0 - ux * 10, y0 - uy * 10), (x1, y1)], 2, 2, "#F2D8A0", 0.8)]
    for i, pal in enumerate(cols):
        cx, cy = x0 + ux * (r * 1.02 + i * r * 1.86), y0 + uy * (r * 1.02 + i * r * 1.86)
        pts = blob_pts(cx, cy, r, r * 0.96, seed + i, 0.03, 18)
        out.append(f'<path d="{blob(cx + 4, cy + 6, r, r * 0.9, seed + i, 0.03, 14)}" fill="#8A3A4A" opacity="0.18"/>')
        out.append(painted(D, pts, pal, seed + i, sdir=(0.5, 0.8), sk=0.14, angle=-40, n=14, sop=(0.1, 0.3), inkw=1.6, inkc=dk(pal[2], 0.2), inkop=0.6, hi=0.5, hik=0.1))
        out.append(f'<path d="{blob(cx - r * 0.38, cy - r * 0.42, r * 0.26, r * 0.14, seed + i + 9, 0.2, 8, -35)}" fill="#FFFFFF" opacity="0.8"/>')
        if i in faces:
            fy = cy + r * 0.08
            for sg in (-1, 1):
                out.append(f'<ellipse cx="{cx + sg * r * 0.28:.1f}" cy="{fy - r * 0.04:.1f}" rx="{r * 0.075:.1f}" ry="{r * 0.1:.1f}" fill="#2A1A1E"/>')
                out.append(f'<circle cx="{cx + sg * r * 0.28 - r * 0.025:.1f}" cy="{fy - r * 0.08:.1f}" r="{r * 0.03:.1f}" fill="#FFFFFF"/>')
                out.append(f'<ellipse cx="{cx + sg * r * 0.46:.1f}" cy="{fy + r * 0.14:.1f}" rx="{r * 0.12:.1f}" ry="{r * 0.07:.1f}" fill="#F2788E" opacity="0.6"/>')
            if i == 1:
                out.append(f'<path d="{blob(cx, fy + r * 0.16, r * 0.09, r * 0.08, seed, 0.1, 8)}" fill="#C8405A"/>')
            else:
                out.append(pline([(cx - r * 0.1, fy + r * 0.12), (cx - r * 0.05, fy + r * 0.18), (cx, fy + r * 0.13), (cx + r * 0.05, fy + r * 0.18), (cx + r * 0.1, fy + r * 0.12)], "#2A1A1E", max(1.4, r * 0.035), seed, 0.9, 1))
    return "".join(out)


@design("kawaii")
def kawaii():
    D = Doc2("jp-kw")
    out = [paper(D.nid(), "#FBE0E6", "#A85A6A", 2201)]
    rnd = random.Random(2202)
    # soft candy stripes and a scatter of petals
    for k in range(-4, 12):
        x = k * 70
        out.append(f'<path d="M {x} -20 L {x + 34} -20 L {x - 166} 620 L {x - 200} 620 Z" fill="#FFFFFF" opacity="0.32"/>')
    out.append(blooms(5, ["#F6B8C8", "#FFFFFF", "#F8D0DC"], 8, (0, 0, 600, 600), (100, 180), (0.12, 0.2)))
    for k in range(16):
        x, y = rnd.uniform(60, 540), rnd.uniform(230, 560)
        out.append(sakura_petal(D, x, y, rnd.uniform(9, 13), rnd.uniform(0, 360), 2203 + k, op=0.8))
    # little plate
    out.append(cast(D, 312, 520, 200, 26, "#8A3A4A", 0.3, 2220))
    pl = ell_pts(300, 500, 196, 50, 0, 360, 40)
    out.append(painted(D, pl, ("#FFFFFF", "#F6F2F2", "#C8B8C0"), 2221, sdir=(0.3, 1), sk=0.1, angle=0, n=20, inkw=1.8, inkc="#8A6A78", hi=0.4))
    out.append(ink(smooth_closed(ell_pts(300, 500, 176, 42, 0, 360, 40)), "#E8889E", 3, 2222, 1, 0.8))
    out.append(ink(smooth_closed(ell_pts(300, 502, 120, 26, 0, 360, 40)), "#D8C8D0", 1.4, 2223, 1, 0.8))
    # a sakura leaf under the skewers
    out.append(long_leaf(D, 150, 500, 280, 80, -12, ("#B8D888", "#6AA048", "#2E5A22"), 2224, veins=2))
    # three skewers fanned out
    out.append(dango_skewer(D, 150, 272, 316, 504, 44, 2230, faces=(0, 2)))
    out.append(dango_skewer(D, 300, 236, 300, 508, 46, 2231, faces=(0, 1, 2)))
    out.append(dango_skewer(D, 452, 272, 286, 504, 44, 2232, faces=(1,)))
    for x, y, r in ((98, 240, 9), (510, 232, 10), (80, 420, 7), (530, 400, 8), (210, 210, 6), (390, 206, 6)):
        out.append(sparkle(x, y, r, "#FFFFFF", 0.95))
    # lettering
    out.append(letters(D, 300, 146, "kawaii", SERIF_IT, 116, "#D8406A", ["#F06A8E", "#A8204A", "#FF8AAA"], 2240, max_w=380,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFD0DC"))
    out.append(ruled(300, 188, "TOO CUTE TO EAT", "#5A8A3A", font=JOS, size=20, ls=7, line_w=30, gap=12))
    return finish_b(D, out, 2241, "#6A2A3A", 0.6)


# ================================================================ 23. tadaima — shoes off at the genkan, slippers waiting
def shoe_pair(D, cx, cy, L, W, seed, pal, kind="leather", gap=None):
    """A pair of shoes seen from above at an angle, toes toward us, neatly side by side."""
    gap = gap if gap is not None else W * 1.25
    out = []
    for sg in (-1, 1):
        x = cx + sg * gap / 2
        pts = []
        for i in range(30):
            a = 2 * math.pi * i / 30
            # rounder toe at the bottom, narrower heel at top
            ry = L / 2
            rx = W / 2 * (1.0 if math.sin(a) > 0 else 0.84) * (1 - 0.12 * math.cos(a) * sg)
            pts.append((x + rx * math.cos(a), cy + ry * math.sin(a)))
        out.append(f'<path d="{blob(x + 6, cy + 8, W * 0.55, L * 0.52, seed + sg, 0.05, 14)}" fill="#1A1414" opacity="0.25"/>')
        out.append(painted(D, pts, pal, seed + sg, sdir=(0.7, 0.6), sk=0.2, angle=-90, n=14, inkw=1.6, hi=0.45, hik=0.1))
        opening = blob_pts(x - sg * W * 0.02, cy - L * 0.16, W * 0.3, L * 0.24, seed + sg + 5, 0.05, 14)
        out.append(f'<path d="{smooth_closed(opening)}" fill="{"#E8DCC8" if kind != "kids" else "#F6F0E8"}"/>')
        out.append(f'<path d="{smooth_closed(opening)}" fill="{D.lin([(0, "#000000", 0.45), (1, "#000000", 0)])}"/>')
        out.append(ink(smooth_closed(opening), pal[2], 1.6, seed, 1, 0.8))
        if kind == "kids":
            for j in range(3):
                y = cy + L * 0.1 + j * L * 0.09
                out.append(f'<path d="M {x - W * 0.22:.1f} {y:.1f} L {x + W * 0.22:.1f} {y:.1f}" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round"/>')
            out.append(f'<path d="{smooth_open([(x - W * 0.48, cy + L * 0.25), (x, cy + L * 0.5), (x + W * 0.48, cy + L * 0.25)])}" stroke="#FFFFFF" stroke-width="4" fill="none"/>')
        elif kind == "leather":
            out.append(f'<path d="{blob(x - W * 0.15, cy + L * 0.28, W * 0.12, L * 0.08, seed, 0.2, 8)}" fill="#FFFFFF" opacity="0.5"/>')
            out.append(pline([(x - W * 0.3, cy + L * 0.08), (x, cy + L * 0.14), (x + W * 0.3, cy + L * 0.08)], pal[2], 1.2, seed, 0.6, 1))
        else:   # flats with a little bow
            out.append(f'<path d="{blob(x, cy + L * 0.12, W * 0.16, W * 0.08, seed, 0.1, 8)}" fill="#F6E0C0"/>')
    return "".join(out)


def slipper_pair(D, cx, cy, L, W, seed, pal):
    """House slippers set side by side on the step, toes toward the door: a long sole, a cloth band over the toe."""
    out = []
    for sg in (-1, 1):
        x = cx + sg * W * 0.62
        sole = []
        for i in range(28):
            a = 2 * math.pi * i / 28
            rx = W / 2 * (1.0 if math.sin(a) > 0 else 0.82)
            sole.append((x + rx * math.cos(a), cy + L / 2 * math.sin(a)))
        out.append(f'<path d="{smooth_closed([(px + 5, py + 6) for px, py in sole])}" fill="#1A1414" opacity="0.22"/>')
        out.append(painted(D, sole, ("#FFFFFF", "#EEE6DA", "#A89A88"), seed + sg, sdir=(0.6, 0.7), sk=0.12, angle=-90, n=8, inkw=1.4, hi=0.3))
        out.append(f'<path d="{smooth_closed([(px, py) for px, py in sole if py < cy - L * 0.05])}" fill="#D8CCBC" opacity="0.5"/>')
        band = [(x - W * 0.54, cy + L * 0.0), (x - W * 0.48, cy + L * 0.32), (x, cy + L * 0.5), (x + W * 0.48, cy + L * 0.32), (x + W * 0.54, cy + L * 0.0), (x, cy - L * 0.06)]
        out.append(painted(D, band, pal, seed + sg + 3, sdir=(0.6, 0.7), sk=0.2, angle=0, n=8, inkw=1.4, hi=0.4))
        out.append(pline([(x - W * 0.45, cy + L * 0.02), (x, cy - L * 0.03), (x + W * 0.45, cy + L * 0.02)], lt(pal[0], 0.4), 1.6, seed, 0.8, 1))
        for j in range(3):
            out.append(f'<circle cx="{x + (j - 1) * W * 0.22:.1f}" cy="{cy + L * 0.2:.1f}" r="{W * 0.05:.1f}" fill="#FFFFFF" opacity="0.7"/>')
    return "".join(out)


@design("tadaima")
def tadaima():
    D = Doc2("jp-td")
    # warm plaster wall
    out = [paper(D.nid(), "#F2E2C6", FLECK, 2301)]
    out.append(f'<rect width="600" height="340" fill="{D.rad([(0, "#FFF4DC", 0.8), (1, "#D8B888", 0.5)], 0.5, 0.35, 0.7)}"/>')
    out.append(strokes(D.nid(), "M 0 0 L 600 0 L 600 340 L 0 340 Z", (-40, 0, 600, 340), ["#FFFFFF", "#D8B888", "#E8CCA0"], 2302, n=90, angle=-75, length=(30, 90), width=(3, 9), opacity=(0.06, 0.16)))
    # doorway to the hall with an indigo noren
    out.append(f'<path d="{pd([(206, 196), (394, 196), (394, 340), (206, 340)])}" fill="#4A2E1E"/>')
    out.append(f'<path d="{pd([(206, 196), (394, 196), (394, 340), (206, 340)])}" fill="{D.lin([(0, "#FFC870", 0.5), (1, "#FFC870", 0)], 0, 1, 0, 0)}"/>')
    for x in (198, 394):
        out.append(painted(D, densify([(x, 186), (x + 10, 186), (x + 10, 340), (x, 340)], 20), DARKWOOD, 2303 + x, sdir=(1, 0), sk=0.25, angle=-90, n=8, inkw=1.2, hi=0.3))
    out.append(painted(D, densify([(190, 182), (410, 182), (410, 196), (190, 196)], 30), DARKWOOD, 2305, sdir=(0, 1), sk=0.25, angle=0, n=10, inkw=1.2, hi=0.3))
    for k, (x0, x1) in enumerate(((210, 298), (302, 390))):
        nr = [(x0, 198), (x1, 198), (x1 + (2 if k else -2), 292), (x0 + (2 if k else -2), 294)]
        out.append(painted(D, densify(nr, 20), AI, 2306 + k, sdir=(0.8, 0.4), sk=0.15, angle=-90, n=16, inkw=1.4, hi=0.3))
        for j in range(4):
            out.append(pline([(x0 + 10 + j * 22, 204), (x0 + 12 + j * 22, 288)], "#1A2650", 2, 2308 + j, 0.35, 1))
    # a white circle crest across both panels
    out.append(f'<circle cx="300" cy="240" r="22" fill="none" stroke="#F6F0E4" stroke-width="5"/>')
    out.append(f'<path d="{smooth_closed([(300, 226), (312, 240), (300, 254), (288, 240)])}" fill="#F6F0E4"/>')
    # a small shelf with an ikebana sprig, an umbrella stand
    out.append(painted(D, densify([(436, 288), (556, 288), (556, 300), (436, 300)], 20), DARKWOOD, 2310, sdir=(0, 1), sk=0.25, angle=0, n=8, inkw=1.2, hi=0.3))
    out.append(painted(D, [(484, 288), (510, 288), (506, 252), (488, 252)], ("#8AB0D0", "#3A6A9A", "#1A3A5A"), 2311, sdir=(1, 0.2), sk=0.25, angle=-90, n=6, inkw=1.2, hi=0.4))
    out.append(pline([(496, 254), (484, 220), (470, 200)], "#4A3A22", 1.6, 2312, 0.9, 1))
    out.append(pline([(498, 254), (508, 214), (522, 196)], "#4A3A22", 1.6, 2313, 0.9, 1))
    for k, (x, y) in enumerate(((470, 200), (484, 218), (522, 196), (510, 214))):
        out.append(ume_flower(D, x, y, 8, 2314 + k, k * 30, pal=("#FFE0E8", "#F6A8BC", "#C85A7A"), inkw=0.6))
    # folded paper umbrella standing in a glazed pot
    ub = [(98, 300), (104, 214), (110, 196), (116, 214), (122, 300)]
    out.append(painted(D, ub, AKA, 2319, sdir=(1, 0.2), sk=0.3, angle=-90, n=8, inkw=1.2, hi=0.4))
    for k in range(3):
        out.append(pline([(102 + k * 6, 296), (108 + k * 2, 206)], "#7A0E0E", 1, 2320 + k, 0.5, 1))
    out.append(f'<path d="M 110 196 L 110 176 q 0 -10 -9 -8" stroke="#3A2418" stroke-width="3.2" fill="none" stroke-linecap="round"/>')
    out.append(f'<path d="{hg.org_rect(100, 236, 20, 8, 2321, 0.3, 6, 2)}" fill="#F6E0C0"/>')
    pot = [(70, 340), (150, 340), (146, 300), (156, 286), (64, 286), (74, 300)]
    out.append(painted(D, pot, ("#8AB0C8", "#3A6A88", "#163A50"), 2318, sdir=(1, 0.2), sk=0.25, angle=-90, n=12, inkw=1.4, hi=0.4))
    out.append(pline([(72, 304), (110, 308), (148, 304)], "#E8F0F4", 1.6, 2322, 0.6, 1))
    # raised hall floor with the slippers waiting, then the step's face
    out.append(wood_planks(D, 340, 404, 2320, ("#E0B080", "#B87A44", "#6A3E1A"), 1, vertical=True, x0=0, x1=600, gaps=True) if False else "")
    floor = pd([(0, 338), (600, 338), (600, 404), (0, 404)])
    out.append(f'<path d="{floor}" fill="#B8783E"/>')
    out.append(strokes(D.nid(), floor, (-40, 338, 600, 404), ["#E0B080", "#8A5022", "#D8A060"], 2321, n=60, angle=0, length=(40, 120), width=(1, 2.4), opacity=(0.2, 0.45)))
    out.append(f'<path d="{blob(300, 360, 220, 12, 2322, 0.1, 14)}" fill="#FFE0A8" opacity="0.4"/>')
    out.append(slipper_pair(D, 210, 370, 62, 28, 2323, ("#7A9ACB", "#3A5A9A", "#1A2E5A")))
    out.append(slipper_pair(D, 352, 370, 60, 27, 2324, ("#F6A8B8", "#D8607E", "#8A2A44")))
    out.append(slipper_pair(D, 470, 374, 44, 20, 2325, ("#F6D27A", "#E8A830", "#8A5A10")))
    step = pd([(0, 404), (600, 404), (600, 436), (0, 436)])
    out.append(f'<path d="{step}" fill="#4A2810"/>')
    out.append(strokes(D.nid(), step, (-40, 404, 600, 436), ["#7A4A22", "#2A1406"], 2326, n=30, angle=0, length=(60, 140), width=(1, 2.4), opacity=(0.2, 0.45)))
    out.append(f'<path d="M 0 405 L 600 405" stroke="#F2C890" stroke-width="2" opacity="0.6"/>')
    # stone tataki with the family's shoes, toes to the door
    tk = pd([(0, 436), (600, 436), (600, 600), (0, 600)])
    out.append(f'<path d="{tk}" fill="#8A8682"/>')
    out.append(specks(2327, (0, 436, 600, 600), ["#5A5654", "#B8B4AE", "#6E6A66"], 300, (0.6, 1.8), (0.4, 0.8)))
    out.append(f'<path d="{tk}" fill="{D.lin([(0, "#000000", 0.35), (0.3, "#000000", 0)])}"/>')
    out.append(shoe_pair(D, 152, 512, 96, 38, 2328, ("#7A5A4A", "#3E2418", "#1A0E08"), "leather"))
    out.append(shoe_pair(D, 300, 520, 82, 32, 2329, ("#E8A890", "#B85A48", "#6A2418"), "flats"))
    out.append(shoe_pair(D, 434, 528, 60, 28, 2330, ("#8AC0F0", "#3A7AC8", "#1A3A7A"), "kids"))
    # lettering
    out.append(letters(D, 300, 136, "tadaima", SERIF_IT, 120, "#6A2E14", ["#8A4422", "#4A1E0A", "#A85A30"], 2340, max_w=400,
                       shadow="#FFF6E4", soff=(0.02, 0.035), angle=-40, hi="#E8A880"))
    out.append(label(300, 170, "I'M HOME!", JOS, 20, "#27407A", ls=8))
    return finish_b(D, out, 2341)


# ================================================================ 24. wabi-sabi — a bowl mended with gold
def kintsugi_bowl(D, cx, rim_y, rx, h, seed):
    rnd = random.Random(seed)
    ry = rx * 0.24
    body = [(cx + rx, rim_y), (cx + rx * 0.97, rim_y + h * 0.42), (cx + rx * 0.78, rim_y + h * 0.84), (cx + rx * 0.36, rim_y + h), (cx - rx * 0.36, rim_y + h),
            (cx - rx * 0.78, rim_y + h * 0.84), (cx - rx * 0.97, rim_y + h * 0.42), (cx - rx, rim_y)]
    body = body + ell_pts(cx, rim_y, rx, ry, 180, 360, 16)[1:-1][::-1][::-1]
    body = [(cx + rx, rim_y), (cx + rx * 0.97, rim_y + h * 0.42), (cx + rx * 0.78, rim_y + h * 0.84), (cx + rx * 0.36, rim_y + h), (cx - rx * 0.36, rim_y + h),
            (cx - rx * 0.78, rim_y + h * 0.84), (cx - rx * 0.97, rim_y + h * 0.42), (cx - rx, rim_y)] + [(x, y) for x, y in ell_pts(cx, rim_y, rx, ry, 0, 180, 16)][1:-1]
    body = jitter(body, seed, 1.6)
    d = smooth_closed(body)
    out = [cast(D, cx + 20, rim_y + h + 6, rx * 1.2, 16, "#000000", 0.6, seed)]
    out.append(painted(D, rect_pts(cx - rx * 0.32, rim_y + h - 4, cx + rx * 0.32, rim_y + h + 14, 14, seed, 0.6), ("#C8B090", "#8A7050", "#4A3820"), seed + 1, sdir=(1, 0.3), sk=0.2, angle=0, n=6, inkw=1.2, hi=0.3))
    out.append(painted(D, body, ("#E8E4D4", "#B8BCA8", "#5E6658"), seed + 2, sdir=(0.9, 0.2), sk=0.2, angle=-80, n=50, slen=(10, 30), sw=(1, 3.5),
                       cols=["#F2EEE2", "#8A9282", "#D0D4C0", "#6A7262"], inkw=2, inkc="#2A2A24", hi=0.4, hik=0.06))
    inner = []
    # crackle in the glaze
    for _ in range(40):
        x, y = rnd.uniform(cx - rx, cx + rx), rnd.uniform(rim_y, rim_y + h)
        inner.append(pline([(x, y), (x + rnd.uniform(-10, 10), y + rnd.uniform(-8, 8)), (x + rnd.uniform(-14, 14), y + rnd.uniform(-10, 10))], "#5A6052", 0.7, rnd.randint(0, 999), 0.35, 1))
    # iron-brown glaze pooling at the foot
    inner.append(f'<path d="{smooth_closed([(cx - rx, rim_y + h * 0.7), (cx + rx, rim_y + h * 0.66), (cx + rx, rim_y + h + 20), (cx - rx, rim_y + h + 20)])}" fill="#6A4A30" opacity="0.55"/>')
    inner.append(shade_over(D, d, "#0A0A08", 0.55, 0, 0, 1, 0.2, 0.45))
    # the gold seams: branching, irregular, catching the light
    seams = [[(cx - rx * 0.62, rim_y + ry * 0.2), (cx - rx * 0.5, rim_y + h * 0.3), (cx - rx * 0.56, rim_y + h * 0.55), (cx - rx * 0.4, rim_y + h * 0.8), (cx - rx * 0.32, rim_y + h + 4)],
             [(cx - rx * 0.5, rim_y + h * 0.32), (cx - rx * 0.2, rim_y + h * 0.4), (cx + rx * 0.06, rim_y + h * 0.36), (cx + rx * 0.2, rim_y + h * 0.5), (cx + rx * 0.5, rim_y + h * 0.48), (cx + rx * 0.98, rim_y + h * 0.4)],
             [(cx + rx * 0.2, rim_y + h * 0.5), (cx + rx * 0.16, rim_y + h * 0.7), (cx + rx * 0.3, rim_y + h * 0.86), (cx + rx * 0.26, rim_y + h + 4)],
             [(cx + rx * 0.3, rim_y + ry * 0.4), (cx + rx * 0.34, rim_y + h * 0.18), (cx + rx * 0.5, rim_y + h * 0.48)]]
    for sm in seams:
        p2 = catmull(jitter(sm, seed + len(sm), 3), 4)
        inner.append(taper(p2, 6, 4, "#8A5A0A", 0.9))
        inner.append(taper(p2, 4.4, 3, "#E8B838"))
        inner.append(taper([(x - 0.8, y - 1) for x, y in p2], 1.6, 1, "#FFF2B0", 0.9))
    out.append(clipped(D, d, inner))
    # rim and the inside of the bowl
    rim = smooth_closed(jitter(ell_pts(cx, rim_y, rx, ry, 0, 360, 36), seed + 3, 1.2))
    out.append(f'<path d="{rim}" fill="#D8D8C8"/>')
    inside = smooth_closed(ell_pts(cx, rim_y + 3, rx * 0.92, ry * 0.76, 0, 360, 36))
    out.append(f'<path d="{inside}" fill="{D.rad([(0, "#8A9282"), (0.7, "#6A7262"), (1, "#3E443A")], 0.5, 0.3, 0.7)}"/>')
    out.append(clipped(D, inside, [taper(catmull([(cx - rx * 0.3, rim_y - ry * 0.6), (cx - rx * 0.2, rim_y + 2), (cx - rx * 0.36, rim_y + ry * 0.8)], 4), 5, 3.5, "#E8B838"),
                                   taper(catmull([(cx - rx * 0.3, rim_y - ry * 0.6), (cx - rx * 0.2, rim_y + 2), (cx - rx * 0.36, rim_y + ry * 0.8)], 4), 1.4, 1, "#FFF2B0", 0.9)]))
    out.append(ink(rim, "#2A2A24", 2, seed + 4, 2, 0.7))
    # gold where the seam crosses the rim
    for x in (cx - rx * 0.62, cx + rx * 0.3):
        out.append(f'<path d="{blob(x, rim_y + ry * 0.92 if x < cx else rim_y + ry * 0.95, 5, 3, seed, 0.1, 8)}" fill="#F2C84A"/>')
    return "".join(out)


def camellia(D, cx, cy, r, seed, pal=("#F06A6A", "#C8202A", "#6A0A12")):
    rnd = random.Random(seed)
    out = []
    for ring, (n, L, off) in enumerate(((5, 1.0, 0), (5, 0.7, 36))):
        for i in range(n):
            a = math.radians(i * 72 + off + rnd.uniform(-8, 8))
            px, py = cx + math.cos(a) * r * 0.45 * L, cy + math.sin(a) * r * 0.4 * L
            pts = blob_pts(px, py, r * 0.5 * L, r * 0.42 * L, seed + ring * 10 + i, 0.08, 14, math.degrees(a))
            out.append(painted(D, pts, pal if ring == 0 else (lt(pal[0], 0.1), pal[1], pal[2]), seed + ring * 10 + i, sdir=(0.5, 0.8), sk=0.18, angle=math.degrees(a), n=6,
                               inkw=1, inkc=pal[2], inkop=0.5, hi=0.35))
    for i in range(26):
        a = rnd.uniform(0, 6.28)
        rr = rnd.uniform(0.05, 0.28) * r
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {cx + math.cos(a) * rr:.1f} {cy + math.sin(a) * rr:.1f}" stroke="#FFF2C0" stroke-width="1.4"/>'
                   f'<circle cx="{cx + math.cos(a) * rr:.1f}" cy="{cy + math.sin(a) * rr:.1f}" r="2.2" fill="#F6C83A"/>')
    return "".join(out)


@design("wabi-sabi")
def wabi_sabi():
    D = Doc2("jp-wb")
    out = [sky(D, [(0, "#2A2E3A"), (1, "#14161E")], 2401, 600, ["#3A3E4C", "#0E1016", "#4A4E5C"], 80, angle=-70, sop=(0.06, 0.14))]
    out.append(soft_glow(D, 280, 330, 300, "#F6E0B0", 0.22))
    out.append(blooms(6, ["#4A4E5C", "#2A2E3A"], 6, (60, 60, 540, 540), (120, 200), (0.1, 0.18)))
    # low wooden board
    bd = [(40, 470), (560, 458), (580, 520), (20, 536)]
    out.append(f'<path d="{pd([(20, 536), (580, 520), (580, 540), (22, 558)])}" fill="#1A0E08"/>')
    out.append(painted(D, densify(bd, 30), ("#7A5238", "#4A2E1C", "#1E1008"), 2402, sdir=(0.3, 1), sk=0.1, angle=-2, n=60, slen=(40, 120), sw=(1, 2.4), inkw=1.6, hi=0.3))
    out.append(kintsugi_bowl(D, 270, 330, 142, 150, 2403))
    # a single camellia, fallen, with its leaves
    out.append(leaf_simple(D, 446, 498, 90, 28, -20, ("#5A8A5A", "#1E4A2A", "#0A2414"), 2404))
    out.append(leaf_simple(D, 446, 498, 72, 22, -165, ("#5A8A5A", "#1E4A2A", "#0A2414"), 2405))
    out.append(camellia(D, 450, 490, 52, 2406))
    out.append(f'<path d="{blob(530, 506, 13, 8, 2407, 0.1, 10, 20)}" fill="#C8202A"/>' + ink(blob(530, 506, 13, 8, 2407, 0.1, 10, 20), "#6A0A12", 1, 1, 1, 0.5))
    # lettering
    out.append(letters(D, 300, 134, "wabi-sabi", SERIF_IT, 116, "#F6EAD4", ["#FFFFFF", "#E8D8B8", "#FFF6E4"], 2410, max_w=420,
                       shadow="#000000", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 176, "BEAUTIFULLY IMPERFECT", "#E8B838", font=JOS, size=20, ls=6, line_w=26, gap=12))
    return finish_b(D, out, 2411, "#FFFFFF", 0.4)


# ================================================================ 25. nami — a woodblock-style wave (an original print)
def foam_curl(x, y, ang, s, seed, col="#FBF6EA", line="#1E3A6A"):
    """A Rinpa-style foam scroll: a tapering stroke that winds into a small spiral, outlined in blue."""
    a0 = math.radians(ang)
    pts = []
    for i in range(30):
        t = i / 29
        r = s * (1 - t * 0.85)
        a = a0 + t * 4.2
        pts.append((x + math.cos(a) * r * 0.9 + math.cos(a0) * s * 0.3 * (1 - t), y + math.sin(a) * r * 0.9 + math.sin(a0) * s * 0.3 * (1 - t)))
    return taper(pts, s * 0.42, s * 0.08, line, 1) + taper(pts, s * 0.3, s * 0.04, col, 1)


def chidori(x, y, s, flip=1, col="#FBF6EA", ink_c="#1E3A6A"):
    """Plover in flight as on old textiles: a round body and two swept wings."""
    P = lambda px, py: (x + px * s * flip, y + py * s)
    body = [P(-8, 0), P(-2, -6), P(8, -5), P(12, 0), P(6, 5), P(-4, 5)]
    w1 = [P(-2, -4), P(-14, -20), P(-6, -16), P(4, -4)]
    w2 = [P(2, -2), P(18, -16), P(12, -6), P(6, 2)]
    out = ""
    for poly in (w1, w2, body):
        d = smooth_closed(poly)
        out += f'<path d="{d}" fill="{col}" stroke="{ink_c}" stroke-width="{max(1.2, s * 0.12):.1f}" stroke-linejoin="round"/>'
    bx, by = P(12, -1)
    out += f'<path d="M {bx:.1f} {by:.1f} l {4 * s * flip:.1f} 1" stroke="{ink_c}" stroke-width="{max(1.2, s * 0.14):.1f}"/>'
    ex, ey = P(7, -2)
    out += f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{max(0.9, s * 0.12):.1f}" fill="{ink_c}"/>'
    return out


def foam_claw(x, y, ang, s, seed, col="#FBF6EA", line="#1E3A6A"):
    """A curl of foam ending in three to four little fingers, pointing along `ang`."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    out = []
    n = rnd.randint(3, 4)
    for j in range(n):
        off = (j - (n - 1) / 2) * s * 0.34
        bx, by = x + nx * off, y + ny * off
        tip = (bx + ux * s * (0.9 - abs(off) / s * 0.4), by + uy * s * (0.9 - abs(off) / s * 0.4))
        hook = (tip[0] + nx * s * 0.25 + ux * s * 0.05, tip[1] + ny * s * 0.25 + uy * s * 0.05)
        out.append(taper([(bx, by), ((bx + tip[0]) / 2 + nx * s * 0.08, (by + tip[1]) / 2 + ny * s * 0.08), tip, hook], s * 0.3, s * 0.05, col, 1))
    return f'<g stroke="{line}" stroke-width="0">{"".join(out)}</g>'


@design("nami")
def nami():
    D = Doc2("jp-nm")
    PAPER = "#F2E6CA"
    PRUSS = ("#5A82B8", "#1E3A6A", "#0E1E3A")
    out = [paper(D.nid(), PAPER, FLECK, 2501)]
    # the print: bokashi sky graded from prussian blue to bare paper
    out.append(f'<rect x="0" y="0" width="600" height="470" fill="{D.lin([(0, "#2E4E80"), (0.35, "#8AA8C8"), (0.62, PAPER), (1, PAPER)])}"/>')
    rnd = random.Random(2502)
    for k in range(60):
        y = rnd.uniform(0, 470)
        out.append(f'<path d="M 0 {y:.1f} L 600 {y + rnd.uniform(-2, 2):.1f}" stroke="#FFFFFF" stroke-width="{rnd.uniform(0.6, 1.6):.1f}" opacity="{rnd.uniform(0.05, 0.14):.2f}"/>')
    # low red sun and a far island
    out.append(f'<circle cx="122" cy="300" r="40" fill="#D8402A" opacity="0.92"/>')
    out.append(f'<path d="{smooth_closed([(20, 392), (70, 368), (120, 362), (170, 380), (196, 392)])}" fill="#6A7A9A" opacity="0.7"/>')
    # sea surface far away
    out.append(f'<rect x="0" y="390" width="600" height="80" fill="#4A6A9A"/>')
    for k in range(10):
        y = 396 + k * 7
        out.append(f'<path d="M 0 {y} Q 150 {y - 3} 300 {y} T 600 {y}" stroke="#A8C0D8" stroke-width="1.4" fill="none" opacity="0.6"/>')
    # the great wave rising from the right, curling over to the left
    sil = [(640, 480), (640, 330), (590, 270), (520, 214), (440, 178), (370, 166), (312, 176), (266, 202), (238, 238), (230, 274), (244, 300), (266, 306),
           (284, 296), (292, 276), (308, 270), (322, 290), (322, 330), (304, 382), (260, 428), (190, 456), (100, 470), (-20, 474), (-20, 480)]
    wd = smooth_closed(sil)
    out.append(f'<path d="{wd}" fill="{PRUSS[1]}"/>')
    flow = [f'<path d="{wd}" fill="{D.lin([(0, PRUSS[0], 0.35), (0.6, PRUSS[1], 0), (1, PRUSS[2], 0.4)], 0, 0, 1, 1)}"/>']
    # bands of lighter blue following the wave's body
    for j in range(1, 9):
        t = j / 9
        band = [(640 - 40 * t, 340 + 120 * t), (560 - 20 * t, 280 + 60 * t), (470 - 10 * t, 228 + 30 * t), (390 - 10 * t, 212 + 22 * t), (340 - 6 * t, 240 + 20 * t), (330 - 20 * t, 300 + 30 * t), (300 - 40 * t, 380 + 30 * t), (200 - 60 * t, 440 + 20 * t)]
        flow.append(f'<path d="{smooth_open(band)}" stroke="{PRUSS[0] if j % 2 else "#A8C4E0"}" stroke-width="{3.2 - t * 1.2:.1f}" fill="none" opacity="0.75"/>')
    flow.append(strokes(D.nid(), wd, (180, 160, 640, 480), [PRUSS[0], PRUSS[2]], 2503, n=60, angle=-30, length=(20, 60), width=(1.5, 4), opacity=(0.12, 0.3)))
    out.append(clipped(D, wd, flow))
    # white foam along the crest and lip
    lip = catmull([(560, 262), (500, 214), (440, 184), (370, 172), (312, 182), (270, 206), (244, 240), (236, 274), (250, 296)], 4)
    out.append(taper(lip, 14, 10, "#FBF6EA"))
    for i in range(0, len(lip) - 1, 3):
        x, y = lip[i]
        x2, y2 = lip[i + 1]
        ang = math.degrees(math.atan2(y2 - y, x2 - x)) - 100
        out.append(foam_curl(x, y, ang, 18 + 5 * math.sin(i), 2504 + i))
    out.append(ink(wd, "#0A1428", 2.2, 2505, 1, 0.8))
    # mist flung ahead of the lip
    for _ in range(26):
        a_ = rnd.uniform(math.radians(170), math.radians(260))
        rr = rnd.uniform(20, 70)
        x, y = 262 + math.cos(a_) * rr, 236 + math.sin(a_) * rr * 0.8
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(1.4, 3.4):.1f}" fill="#FBF6EA" stroke="#1E3A6A" stroke-width="0.6"/>')
    # a flight of plovers over the sea
    for k, (x, y, sz) in enumerate(((150, 196, 1.6), (196, 150, 1.35), (106, 148, 1.2), (236, 108, 1.05), (88, 226, 1.0))):
        out.append(chidori(x, y, sz, 1 if k % 2 else -1))
    # a smaller wave in front
    sw = [(-20, 470), (40, 440), (110, 428), (170, 442), (196, 470), (-20, 480)]
    out.append(f'<path d="{smooth_closed(sw)}" fill="#3A6AA0"/>')
    for j in range(1, 4):
        out.append(f'<path d="{smooth_open([(0, 470 - j * 2), (50, 448 + j * 5), (110, 440 + j * 6), (170, 452 + j * 4)])}" stroke="#8AB0D8" stroke-width="1.6" fill="none" opacity="0.7"/>')
    out.append(taper(catmull([(30, 448), (80, 432), (130, 432), (172, 446)], 4), 6, 4, "#FBF6EA"))
    for k, (x, y) in enumerate(((70, 436), (116, 430), (156, 440))):
        out.append(foam_curl(x, y, -150 + k * 10, 10, 2520 + k))
    # print border, cartouche with the subtitle, the margin below
    out.append(f'<rect x="0" y="470" width="600" height="130" fill="{PAPER}"/>')
    out.append(specks(2525, (0, 470, 600, 600), [FLECK, "#FFFFFF"], 60, (0.5, 1.4), (0.2, 0.5)))
    out.append(f'<path d="M 0 470 L 600 470" stroke="#1E3A6A" stroke-width="3"/>')
    cx0, cy0, cw, ch = 360, 70, 168, 42
    out.append(f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" fill="#F6E8B8" stroke="#C8402A" stroke-width="3"/>')
    out.append(f'<rect x="{cx0 + 5}" y="{cy0 + 5}" width="{cw - 10}" height="{ch - 10}" fill="none" stroke="#C8402A" stroke-width="1"/>')
    out.append(label(cx0 + cw / 2, cy0 + 27, "RIDE THE WAVE", MONO, 16, "#1E3A6A", ls=2, max_w=cw - 20))
    out.append(letters(D, 300, 536, "nami", SERIF_IT, 92, "#1E3A6A", ["#2E5A90", "#0E1E3A"], 2526, max_w=300, shadow="#D8C8A8", soff=(0.015, 0.03), angle=-40, hi="#8AA8D0"))
    out.append(hanko(D, 470, 512, 30, 2527))
    return finish_b(D, out, 2528)


# ================================================================ 26. konbanwa — a vending machine glowing on a quiet night street
def vending_machine(D, x0, y0, w, h, seed, body=("#FFFFFF", "#E8ECF0", "#8A94A8"), accent="#C8281E"):
    """A street vending machine (no brand): lit display of cans and bottles, buttons, coin panel, take-out slot."""
    rnd = random.Random(seed)
    side = w * 0.16
    out = [f'<path d="{pd([(x0 + w, y0), (x0 + w + side, y0 + side * 0.4), (x0 + w + side, y0 + h - side * 0.2), (x0 + w, y0 + h)])}" fill="#5A6070"/>']
    out.append(f'<path d="{pd([(x0 + w, y0), (x0 + w + side, y0 + side * 0.4), (x0 + w + side, y0 + h - side * 0.2), (x0 + w, y0 + h)])}" fill="{D.lin([(0, "#000000", 0.1), (1, "#000000", 0.45)], 0, 0, 1, 0)}"/>')
    out.append(painted(D, densify([(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)], 30), body, seed, sdir=(1, 0.3), sk=0.06, angle=-90, n=20, inkw=2, inkc="#2A2E3A", hi=0.2))
    out.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h * 0.06:.1f}" fill="{accent}"/>')
    # lit display window
    dx0, dy0, dw, dh = x0 + w * 0.07, y0 + h * 0.09, w * 0.86, h * 0.5
    out.append(f'<rect x="{dx0:.1f}" y="{dy0:.1f}" width="{dw:.1f}" height="{dh:.1f}" fill="#F4FAFF"/>')
    rows, cols = 3, 6
    can_cols = [("#E8302A", "#FFFFFF"), ("#2E6AC8", "#FFFFFF"), ("#F6C21C", "#1A1A1A"), ("#1E8A4A", "#F6E8C0"), ("#3A2A1A", "#E8B838"), ("#F28A1E", "#FFFFFF"),
                ("#8AC8E8", "#2E5A8A"), ("#FFFFFF", "#C8281E"), ("#6A3A8A", "#F6C8E8")]
    for r in range(rows):
        sy = dy0 + 8 + r * dh / rows
        cell_h = dh / rows
        out.append(f'<rect x="{dx0:.1f}" y="{sy + cell_h * 0.62:.1f}" width="{dw:.1f}" height="3" fill="#C8D0DC"/>')
        for c in range(cols):
            cx = dx0 + (c + 0.5) * dw / cols
            col, band = rnd.choice(can_cols)
            cw_, ch_ = dw / cols * 0.6, cell_h * 0.5
            if (r + c) % 3 == 0:   # a bottle
                bp = [(cx - cw_ * 0.4, sy + cell_h * 0.6), (cx + cw_ * 0.4, sy + cell_h * 0.6), (cx + cw_ * 0.4, sy + cell_h * 0.3), (cx + cw_ * 0.15, sy + cell_h * 0.18), (cx + cw_ * 0.12, sy + cell_h * 0.08),
                      (cx - cw_ * 0.12, sy + cell_h * 0.08), (cx - cw_ * 0.15, sy + cell_h * 0.18), (cx - cw_ * 0.4, sy + cell_h * 0.3)]
                out.append(f'<path d="{smooth_closed(bp)}" fill="{lt(col, 0.3)}" stroke="#5A6070" stroke-width="0.8"/>')
                out.append(f'<rect x="{cx - cw_ * 0.4:.1f}" y="{sy + cell_h * 0.36:.1f}" width="{cw_ * 0.8:.1f}" height="{cell_h * 0.12:.1f}" fill="{band}"/>')
            else:
                out.append(f'<rect x="{cx - cw_ / 2:.1f}" y="{sy + cell_h * 0.6 - ch_:.1f}" width="{cw_:.1f}" height="{ch_:.1f}" rx="2" fill="{col}" stroke="#5A6070" stroke-width="0.8"/>')
                out.append(f'<rect x="{cx - cw_ / 2:.1f}" y="{sy + cell_h * 0.6 - ch_ * 0.6:.1f}" width="{cw_:.1f}" height="{ch_ * 0.2:.1f}" fill="{band}" opacity="0.9"/>')
            out.append(f'<rect x="{cx - cw_ * 0.32:.1f}" y="{sy + cell_h * 0.6 - ch_ + 2:.1f}" width="{cw_ * 0.14:.1f}" height="{ch_ - 4:.1f}" fill="#FFFFFF" opacity="0.5"/>')
            # price tag and button
            out.append(f'<rect x="{cx - 8:.1f}" y="{sy + cell_h * 0.66:.1f}" width="16" height="6" fill="#1A1A1A"/><rect x="{cx - 6:.1f}" y="{sy + cell_h * 0.67:.1f}" width="12" height="4" fill="{"#7AF0A0" if rnd.random() < 0.75 else "#FF6A5A"}"/>')
            out.append(f'<rect x="{cx - 6:.1f}" y="{sy + cell_h * 0.78:.1f}" width="12" height="5" rx="2" fill="#E8ECF0" stroke="#8A94A8" stroke-width="0.8"/>')
    out.append(f'<rect x="{dx0:.1f}" y="{dy0:.1f}" width="{dw:.1f}" height="{dh:.1f}" fill="{D.lin([(0, "#FFFFFF", 0.35), (0.4, "#FFFFFF", 0), (1, "#8AC8F0", 0.15)], 0, 0, 1, 1)}"/>')
    out.append(f'<rect x="{dx0:.1f}" y="{dy0:.1f}" width="{dw:.1f}" height="{dh:.1f}" fill="none" stroke="#2A2E3A" stroke-width="2"/>')
    # lower panel: coin slot, return lever, take-out flap
    py0 = y0 + h * 0.63
    out.append(f'<rect x="{x0 + w * 0.62:.1f}" y="{py0:.1f}" width="{w * 0.3:.1f}" height="{h * 0.14:.1f}" rx="3" fill="#C8CED8" stroke="#5A6070" stroke-width="1"/>')
    out.append(f'<rect x="{x0 + w * 0.7:.1f}" y="{py0 + 8:.1f}" width="{w * 0.04:.1f}" height="{h * 0.05:.1f}" fill="#1A1A1A"/>')
    out.append(f'<rect x="{x0 + w * 0.68:.1f}" y="{py0 + h * 0.09:.1f}" width="{w * 0.18:.1f}" height="8" fill="#1A1A1A"/>')
    out.append(f'<circle cx="{x0 + w * 0.84:.1f}" cy="{py0 + 14:.1f}" r="5" fill="#E8ECF0" stroke="#5A6070"/>')
    out.append(f'<rect x="{x0 + w * 0.1:.1f}" y="{py0 + 6:.1f}" width="{w * 0.44:.1f}" height="{h * 0.1:.1f}" rx="3" fill="{accent}" opacity="0.85"/>')
    for k in range(3):
        out.append(f'<path d="M {x0 + w * 0.14 + k * w * 0.13:.1f} {py0 + 14:.1f} l {w * 0.08:.1f} 0" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.8"/>')
    out.append(f'<rect x="{x0 + w * 0.08:.1f}" y="{y0 + h * 0.82:.1f}" width="{w * 0.84:.1f}" height="{h * 0.12:.1f}" rx="4" fill="#1A1E28"/>')
    out.append(f'<rect x="{x0 + w * 0.1:.1f}" y="{y0 + h * 0.83:.1f}" width="{w * 0.8:.1f}" height="{h * 0.05:.1f}" rx="3" fill="#3A404E"/>')
    return "".join(out)


def sitting_cat(D, x, base, s, seed, col=("#5A5056", "#2A2428", "#100C0E"), rim="#BFF0FF", flip=1):
    k = s
    P = lambda px, py: (x + px * k * flip, base + py * k)
    L = lambda pts: [P(px, py) for px, py in pts]
    out = [f'<ellipse cx="{x:.1f}" cy="{base:.1f}" rx="{30 * k:.1f}" ry="{5 * k:.1f}" fill="#000000" opacity="0.35"/>']
    tail = L([(18, -4), (40, -2), (52, -16), (48, -22), (40, -10), (20, -10)])
    out.append(f'<path d="{smooth_closed(tail)}" fill="{col[1]}"/>')
    body = L([(-16, -2), (-20, -30), (-12, -56), (4, -62), (18, -50), (22, -22), (20, -2)])
    out.append(painted(D, body, col, seed, sdir=(-0.8 * flip, 0.3), sk=0.2, angle=-90, n=10, inkw=1, hi=0.3))
    head = L([(-12, -60), (-14, -76), (-10, -90), (-4, -80), (6, -80), (12, -90), (16, -76), (14, -60), (2, -54)])
    out.append(painted(D, head, col, seed + 1, sdir=(-0.8 * flip, 0.3), sk=0.2, angle=-90, n=6, inkw=1, hi=0.3))
    for sg in (-1, 1):
        ex, ey = P(1 + sg * 6, -70)
        out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{2.6 * k:.1f}" ry="{3.2 * k:.1f}" fill="#D8F070"/><ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{0.8 * k:.1f}" ry="{2.6 * k:.1f}" fill="#101010"/>')
    if rim:
        out.append(pline(L([(-12, -90), (-14, -76), (-12, -60), (-20, -30), (-16, -2)]) if flip > 0 else L([(16, -76), (14, -60), (22, -22), (20, -2)]), rim, 1.8 * k, seed, 0.75, 1))
    return "".join(out)


@design("konbanwa")
def konbanwa():
    D = Doc2("jp-kb")
    out = [sky(D, [(0, "#0E1430"), (0.6, "#24305A"), (1, "#3A3A6A")], 2601, 420, ["#1E2650", "#0A0E24", "#2E3A6A"], 60, angle=-3, sop=(0.06, 0.16))]
    rnd = random.Random(2602)
    for _ in range(70):
        out.append(f'<circle cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(0, 300):.1f}" r="{rnd.uniform(0.6, 1.8):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.4, 1):.2f}"/>')
    out.append(soft_glow(D, 506, 222, 80, "#FFF6D8", 0.25))
    out.append(f'<circle cx="506" cy="222" r="18" fill="#FFF6D8"/><circle cx="515" cy="216" r="16" fill="#1E2852"/>')
    # rooftops and a house with one lit window
    out.append(f'<path d="{pd([(-10, 300), (140, 300), (190, 262), (380, 262), (430, 300), (610, 300), (610, 420), (-10, 420)])}" fill="#1A1E36"/>')
    out.append(f'<path d="{pd([(-10, 300), (140, 300), (190, 262), (380, 262), (430, 300), (610, 300)], False)}" stroke="#4A5280" stroke-width="2" fill="none"/>')
    out.append(f'<rect x="60" y="324" width="40" height="30" fill="#FFC870" opacity="0.9"/><path d="M 80 324 L 80 354 M 60 339 L 100 339" stroke="#1A1E36" stroke-width="3"/>')
    out.append(soft_glow(D, 80, 339, 50, "#FFC870", 0.35))
    # utility pole and its tangle of wires
    out.append(taper([(150, 520), (150, 300), (154, 60)], 14, 10, "#3A3E52"))
    for y in (110, 150):
        out.append(f'<path d="M 112 {y} L 192 {y - 2}" stroke="#2A2E40" stroke-width="5"/>')
    out.append(painted(D, [(160, 170), (186, 170), (186, 206), (160, 206)], ("#7A8098", "#4A5068", "#22263A"), 2603, sk=0.2, n=4, inkw=1, hi=0.3))
    for k, (y0, y1, sag) in enumerate(((110, 160, 30), (112, 190, 40), (150, 220, 34), (150, 236, 26), (196, 250, 20))):
        out.append(f'<path d="M -10 {y0 + 20 + k * 6} Q 70 {y0 + 40} 150 {y0}" stroke="#141828" stroke-width="1.6" fill="none"/>')
        out.append(f'<path d="M 154 {y0} Q 380 {(y0 + y1) / 2 + sag} 610 {y1}" stroke="#141828" stroke-width="1.6" fill="none"/>')
    # block wall behind the machine
    wall = pd([(-10, 330), (610, 330), (610, 470), (-10, 470)])
    out.append(f'<path d="{wall}" fill="#5A5E70"/>')
    for r in range(7):
        y = 330 + r * 20
        out.append(f'<path d="M -10 {y} L 610 {y}" stroke="#3A3E50" stroke-width="2"/>')
        for c in range(14):
            x = -10 + c * 46 + (23 if r % 2 else 0)
            out.append(f'<path d="M {x} {y} L {x} {y + 20}" stroke="#3A3E50" stroke-width="2"/>')
    # asphalt
    out.append(f'<rect y="470" width="600" height="130" fill="#262A36"/>')
    out.append(specks(2604, (0, 470, 600, 600), ["#3A3E4C", "#16181E"], 200, (0.6, 1.6), (0.4, 0.8)))
    out.append(f'<path d="M -10 560 L 610 548" stroke="#C8C8C0" stroke-width="5" opacity="0.6"/>')
    # the light spilling out of the machine
    out.append(f'<path d="{blob(354, 500, 230, 50, 2605, 0.1, 16)}" fill="{D.rad([(0, "#E8F8FF", 0.6), (1, "#E8F8FF", 0)])}"/>')
    out.append(soft_glow(D, 350, 330, 230, "#D8F2FF", 0.5))
    out.append(vending_machine(D, 262, 218, 168, 268, 2606))
    out.append(f'<path d="{pd([(262, 486), (430, 486), (456, 480), (288, 480)])}" fill="#000000" opacity="0.3"/>')
    # moths circling the light
    for _ in range(12):
        x, y = rnd.uniform(240, 470), rnd.uniform(190, 260)
        out.append(f'<path d="M {x - 3:.1f} {y:.1f} L {x:.1f} {y - 2:.1f} L {x + 3:.1f} {y:.1f}" stroke="#F6F0D8" stroke-width="1.6" fill="none" opacity="0.8"/>')
    # the night cat, lit from the machine
    out.append(sitting_cat(D, 488, 492, 1.0, 2607, flip=-1))
    # lettering
    out.append(letters(D, 300, 132, "konbanwa", SERIF_IT, 112, "#FFF2D8", ["#FFFFFF", "#F2E2C8", "#FFF6E8"], 2610, max_w=420,
                       shadow="#070A18", soff=(0.02, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 172, "GOOD EVENING", "#9AD8F8", font=JOS, size=20, ls=8, line_w=30, gap=12))
    return finish_b(D, out, 2611, "#FFFFFF", 0.4)


# ================================================================ 27. osechi — the New Year feast in lacquer boxes
def osechi_items(D, x0, y0, S, seed):
    """Plan view of one tier, a 3x3 grid of New Year dishes (to be squashed into perspective by the caller)."""
    rnd = random.Random(seed)
    c = S / 3
    out = []
    # dividers
    for i in (1, 2):
        out.append(f'<rect x="{x0 + i * c - 2:.1f}" y="{y0:.1f}" width="4" height="{S:.1f}" fill="#7A0E0E"/>')
        out.append(f'<rect x="{x0:.1f}" y="{y0 + i * c - 2:.1f}" width="{S:.1f}" height="4" fill="#7A0E0E"/>')
    cell = lambda i, j: (x0 + (i + 0.5) * c, y0 + (j + 0.5) * c)
    # (0,0) black beans in a little dish
    cx, cy = cell(0, 0)
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{c * 0.4:.1f}" fill="#F6F0E6" stroke="#C8B8A8" stroke-width="2"/>')
    for _ in range(26):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0, c * 0.3)
        bx, by = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        out.append(f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="6" ry="4.6" fill="#140E14" transform="rotate({rnd.uniform(0, 180):.0f} {bx:.1f} {by:.1f})"/><circle cx="{bx - 1.6:.1f}" cy="{by - 1.6:.1f}" r="1.4" fill="#FFFFFF" opacity="0.7"/>')
    # (1,0) datemaki spirals
    cx, cy = cell(1, 0)
    for k in range(3):
        dx = (k - 1) * c * 0.3
        out.append(f'<rect x="{cx + dx - c * 0.14:.1f}" y="{cy - c * 0.38:.1f}" width="{c * 0.28:.1f}" height="{c * 0.76:.1f}" rx="4" fill="#F6CC4A" stroke="#A86A10" stroke-width="1.6"/>')
        sp = [(cx + dx + math.cos(t) * 1.6 * t * 0.9, cy + math.sin(t) * 1.6 * t * 1.6) for t in [i * 0.4 for i in range(26)]]
        out.append(taper(sp, 1, 2.4, "#B8782A", 0.85))
        for j in range(5):
            out.append(f'<path d="M {cx + dx - c * 0.14:.1f} {cy - c * 0.3 + j * c * 0.15:.1f} l 5 0" stroke="#8A5A10" stroke-width="2"/>')
    # (2,0) red and white kamaboko
    cx, cy = cell(2, 0)
    for k in range(5):
        dx = (k - 2) * c * 0.16
        col = "#F07A8A" if k % 2 == 0 else "#FFFFFF"
        out.append(f'<path d="M {cx + dx - c * 0.07:.1f} {cy + c * 0.34:.1f} L {cx + dx - c * 0.07:.1f} {cy - c * 0.2:.1f} Q {cx + dx:.1f} {cy - c * 0.4:.1f} {cx + dx + c * 0.07:.1f} {cy - c * 0.2:.1f} L {cx + dx + c * 0.07:.1f} {cy + c * 0.34:.1f} Z" fill="{col}" stroke="#C8A8A8" stroke-width="1.2"/>')
        out.append(f'<path d="M {cx + dx - c * 0.07:.1f} {cy - c * 0.16:.1f} Q {cx + dx:.1f} {cy - c * 0.34:.1f} {cx + dx + c * 0.07:.1f} {cy - c * 0.16:.1f}" stroke="#E8384A" stroke-width="3" fill="none"/>')
    # (0,1) shrimp
    cx, cy = cell(0, 1)
    for k in range(2):
        sx, sy = cx - c * 0.05 + k * c * 0.1, cy - c * 0.15 + k * c * 0.3
        segs = [(sx + math.cos(a) * c * 0.26, sy + math.sin(a) * c * 0.2) for a in [math.radians(200 - i * 30) for i in range(8)]]
        out.append(taper(segs, c * 0.18, c * 0.06, "#E8502A"))
        for i in range(1, 7):
            px, py = segs[i]
            out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{c * 0.06:.1f}" fill="none" stroke="#FFC8A0" stroke-width="1.2" opacity="0.8"/>')
        tx, ty = segs[-1]
        out.append(f'<path d="{smooth_closed([(tx, ty), (tx + 10, ty - 12), (tx + 16, ty + 4)])}" fill="#C8301A"/>')
        hx, hy = segs[0]
        out.append(f'<path d="M {hx:.1f} {hy:.1f} q -20 -10 -30 6" stroke="#C8301A" stroke-width="1.6" fill="none"/>')
    # (1,1) kuri kinton: golden mash with chestnuts
    cx, cy = cell(1, 1)
    out.append(f'<path d="{blob(cx, cy, c * 0.4, c * 0.36, seed, 0.12, 14)}" fill="#F6C83A"/>')
    for k in range(3):
        a = k * 2.1
        out.append(f'<path d="{blob(cx + math.cos(a) * c * 0.16, cy + math.sin(a) * c * 0.14, c * 0.13, c * 0.11, seed + k, 0.1, 10)}" fill="#F2A21E" stroke="#B8700A" stroke-width="1.2"/>')
    out.append(f'<path d="{blob(cx - c * 0.15, cy - c * 0.15, c * 0.1, c * 0.05, seed, 0.2, 8)}" fill="#FFF2B0" opacity="0.8"/>')
    # (2,1) lotus root slices
    cx, cy = cell(2, 1)
    for k, (dx, dy) in enumerate(((-0.14, -0.12), (0.14, 0.0), (-0.08, 0.18))):
        rx_, ry_ = cx + dx * c, cy + dy * c
        out.append(f'<circle cx="{rx_:.1f}" cy="{ry_:.1f}" r="{c * 0.2:.1f}" fill="#F6EEDC" stroke="#C8B08A" stroke-width="1.4"/>')
        for j in range(7):
            a = j * 2 * math.pi / 7
            out.append(f'<circle cx="{rx_ + math.cos(a) * c * 0.12:.1f}" cy="{ry_ + math.sin(a) * c * 0.12:.1f}" r="{c * 0.035:.1f}" fill="#A8885A"/>')
        out.append(f'<circle cx="{rx_:.1f}" cy="{ry_:.1f}" r="{c * 0.03:.1f}" fill="#A8885A"/>')
    # (0,2) carrots cut as plum flowers and snow peas
    cx, cy = cell(0, 2)
    for k, (dx, dy) in enumerate(((-0.15, -0.1), (0.14, -0.14), (0.0, 0.16))):
        fx, fy = cx + dx * c, cy + dy * c
        for j in range(5):
            a = math.radians(j * 72 - 90)
            out.append(f'<circle cx="{fx + math.cos(a) * c * 0.08:.1f}" cy="{fy + math.sin(a) * c * 0.08:.1f}" r="{c * 0.07:.1f}" fill="#F27A1E"/>')
        out.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="{c * 0.05:.1f}" fill="#FFB060"/>')
    for k in range(2):
        out.append(f'<path d="{blob(cx + c * 0.22, cy + c * (0.06 + k * 0.16), c * 0.16, c * 0.05, seed + k, 0.1, 10, -20)}" fill="#6ABA3A" stroke="#2E6A1A" stroke-width="1"/>')
    # (1,2) kazunoko: golden herring roe
    cx, cy = cell(1, 2)
    for k in range(2):
        kd = blob(cx + (k - 0.5) * c * 0.3, cy, c * 0.14, c * 0.32, seed + 9 + k, 0.06, 12)
        out.append(f'<path d="{kd}" fill="#F2D86A" stroke="#B8962A" stroke-width="1.2"/>')
        for j in range(8):
            yy = cy - c * 0.26 + j * c * 0.07
            out.append(f'<path d="M {cx + (k - 0.5) * c * 0.3 - c * 0.1:.1f} {yy:.1f} l {c * 0.2:.1f} 2" stroke="#C8A83A" stroke-width="1" opacity="0.8"/>')
    # (2,2) tazukuri: candied little sardines
    cx, cy = cell(2, 2)
    for _ in range(14):
        a = rnd.uniform(0, 6.28)
        fx, fy = cx + rnd.uniform(-c * 0.3, c * 0.3), cy + rnd.uniform(-c * 0.3, c * 0.3)
        out.append(taper([(fx, fy), (fx + math.cos(a) * 14, fy + math.sin(a) * 14)], 4, 1.2, "#8A6A4A"))
        out.append(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="1.2" fill="#FFFFFF"/>')
    out.append(specks(seed + 50, (cx - c * 0.4, cy - c * 0.4, cx + c * 0.4, cy + c * 0.4), ["#F6E8C0"], 20, (0.8, 1.4), (0.8, 1)))
    return "".join(out)


@design("osechi")
def osechi():
    D = Doc2("jp-os")
    out = [sky(D, [(0, "#B8241E"), (1, "#7A0E0E")], 2701, 600, ["#C8382A", "#6A0A0A", "#D84A3A"], 90, angle=-70, sop=(0.06, 0.16))]
    out.append(seigaiha(D, "M 0 0 L 600 0 L 600 600 L 0 600 Z", (0, 0, 600, 600), 30, ["#A81E18", "#9A1A14"], "#D8A848", 2702, rings=4, lw=1.2))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#B8241E", 0.8), (0.6, "#B8241E", 0.5), (1, "#4A0606", 0.6)], 0.5, 0.55, 0.72)}"/>')
    out.append(soft_glow(D, 300, 380, 280, "#FFD890", 0.4))
    # pine sprig and plum behind the box
    pb = catmull([(-20, 300), (60, 280), (120, 250), (170, 236)], 6)
    out.append(bark_branch(D, pb, 14, 6, 2703, pal=("#6A5048", "#3A2A26", "#1A1210")))
    out.append(bark_branch(D, catmull([(60, 280), (80, 236), (70, 210)], 5), 6, 3, 2704, pal=("#6A5048", "#3A2A26", "#1A1210")))
    for k, (x, y, r) in enumerate(((168, 234, 13), (120, 250, 14), (76, 232, 12), (70, 208, 11), (34, 290, 13), (98, 284, 10))):
        out.append(ume_flower(D, x, y, r, 2705 + k * 3, k * 25))
    out.append(pd([(0, 0)]) and "")
    # the stacked jubako: a front face per tier, the open top tier in perspective
    S, x0, top = 300, 150, 254
    sq = 0.56
    out.append(cast(D, 312, 552, 210, 22, "#2A0404", 0.55, 2706))
    for t, y in enumerate((top + S * sq + 64, top + S * sq)):
        fr = [(x0 - 4, y), (x0 + S + 4, y), (x0 + S + 4, y + 64), (x0 - 4, y + 64)]
        out.append(painted(D, densify(fr, 30), ("#4A3A3A", "#1A1212", "#050303"), 2707 + t, sdir=(0.6, 0.6), sk=0.1, angle=0, n=20, inkw=1.6, hi=0.3))
        out.append(f'<path d="M {x0 - 4} {y + 4} L {x0 + S + 4} {y + 4}" stroke="#D8A848" stroke-width="2.4"/>')
        out.append(f'<path d="M {x0 - 4} {y + 60} L {x0 + S + 4} {y + 60}" stroke="#D8A848" stroke-width="1.4" opacity="0.7"/>')
        for sg in (-1, 1):
            out.append(f'<path d="{blob(300 + sg * 90, y + 32, 16, 14, 2709 + t + sg, 0.1, 10)}" fill="none" stroke="#D8A848" stroke-width="1.6" opacity="0.7"/>')
        out.append(f'<path d="{smooth_closed([(300, y + 18), (312, y + 32), (300, y + 46), (288, y + 32)])}" fill="#D8A848" opacity="0.8"/>')
    # top tier rim and its contents seen from above at a slant
    rim = [(x0 - 6, top - 6), (x0 + S + 6, top - 6), (x0 + S + 6, top + S * sq + 6), (x0 - 6, top + S * sq + 6)]
    out.append(f'<path d="{pd(rim)}" fill="#120C0C"/>')
    out.append(f'<path d="{pd(rim)}" fill="none" stroke="#D8A848" stroke-width="2"/>')
    out.append(f'<g transform="translate(0 {top}) scale(1 {sq}) translate(0 {-top})">')
    out.append(f'<rect x="{x0}" y="{top}" width="{S}" height="{S}" fill="#A8160E"/>')
    out.append(osechi_items(D, x0, top, S, 2712))
    out.append("</g>")
    out.append(f'<rect x="{x0}" y="{top}" width="{S}" height="{S * sq:.1f}" fill="{D.lin([(0, "#000000", 0.3), (0.2, "#000000", 0)])}"/>')
    # celebration chopsticks in a red and white paper sleeve
    sl = [(372, 552), (540, 524), (544, 540), (376, 568)]
    out.append(cast(D, 470, 560, 100, 9, "#2A0404", 0.4, 2713))
    out.append(painted(D, sl, ("#FFFFFF", "#F6F0E6", "#C8B8A8"), 2714, sdir=(0.3, 1), sk=0.2, angle=-9, n=8, inkw=1.4, hi=0.3))
    out.append(f'<path d="{pd([(470, 536), (490, 533), (494, 549), (474, 552)])}" fill="#C8281E"/>')
    out.append(pline([(380, 556), (540, 529)], "#D8A848", 1.4, 2715, 0.8, 1))
    for x, y, r in ((96, 120, 9), (504, 208, 8), (520, 420, 7), (80, 440, 8), (300, 214, 6)):
        out.append(sparkle(x, y, r, "#FFE8A0", 0.9))
    # lettering
    out.append(letters(D, 300, 148, "osechi", SERIF_IT, 110, "#FFF0D0", ["#FFFFFF", "#F6DCB0", "#FFE8C0"], 2720, max_w=380,
                       shadow="#4A0606", soff=(0.02, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 188, "A NEW YEAR, LAYER BY LAYER", "#F6C85A", font=JOS, size=17, ls=4, line_w=22, gap=10, max_w=400))
    return finish_b(D, out, 2721, "#3A0A08", 0.6)


# ================================================================ 28. irasshaimase! — the tanuki welcoming you at the shop door
def tanuki_statue(D, cx, base, s, seed):
    """Shigaraki tanuki: straw hat, big round eyes, a fat belly, sake flask in one paw and a ledger in the other."""
    k = s
    P = lambda x, y: (cx + x * k, base + y * k)
    L = lambda pts: [P(x, y) for x, y in pts]
    GL = ("#C89060", "#8A5430", "#3E2010")      # glaze
    out = [cast(D, cx + 14 * k, base, 130 * k, 14 * k, strength=0.55, seed=seed)]
    # bushy tail behind, low on the right
    out.append(painted(D, L([(60, -40), (110, -60), (136, -30), (120, 0), (70, -6)]), GL, seed, sdir=(0.6, 0.6), sk=0.2, angle=-20, n=12, inkw=1.6, hi=0.35))
    # feet
    for sg in (-1, 1):
        out.append(painted(D, blob_pts(*P(sg * 40, -10), 34 * k, 16 * k, seed + sg, 0.06, 12), GL, seed + 2 + sg, sdir=(0.6, 0.6), sk=0.2, n=8, inkw=1.6, hi=0.35))
    # body and the big pale belly
    body = L([(-84, -200), (-60, -228), (0, -236), (60, -228), (84, -200), (100, -130), (96, -60), (70, -14), (0, -4), (-70, -14), (-96, -60), (-100, -130)])
    out.append(painted(D, body, GL, seed + 4, sdir=(0.7, 0.5), sk=0.16, angle=-70, n=50, slen=(14, 40), sw=(1.5, 4), inkw=2.2, hi=0.45, hik=0.08))
    belly = blob_pts(*P(0, -100), 76 * k, 82 * k, seed + 5, 0.03, 22)
    out.append(painted(D, belly, ("#FFE8C8", "#EAC898", "#A8784A"), seed + 5, sdir=(0.6, 0.6), sk=0.18, angle=-60, n=24, inkw=1.8, hi=0.5, hik=0.1))
    out.append(f'<path d="{blob(*P(-30, -140), 22 * k, 30 * k, seed + 6, 0.2, 10, -20)}" fill="#FFFFFF" opacity="0.35"/>')
    out.append(f'<circle cx="{P(0, -96)[0]:.1f}" cy="{P(0, -96)[1]:.1f}" r="{4 * k:.1f}" fill="#8A5430"/>')
    # glaze drips running down the shoulders
    for x in (-80, -60, 66, 84):
        out.append(taper(L([(x, -200), (x - 2, -170), (x + 1, -150)]), 6 * k, 2 * k, "#5A3018", 0.6))
    # arms: sake flask on our left, ledger on our right
    out.append(painted(D, L([(-96, -170), (-120, -120), (-116, -96), (-92, -100), (-80, -150)]), GL, seed + 7, sdir=(0.6, 0.6), sk=0.2, angle=-80, n=10, inkw=1.6, hi=0.35))
    flask = L([(-148, -132), (-140, -168), (-130, -174), (-128, -190), (-118, -190), (-116, -174), (-104, -168), (-96, -132), (-104, -96), (-140, -96)])
    out.append(painted(D, flask, ("#FFFFFF", "#F2EEE6", "#B8B0A6"), seed + 8, sdir=(0.7, 0.4), sk=0.18, angle=-90, n=12, inkw=1.6, hi=0.5))
    out.append(f'<path d="{blob(*P(-122, -128), 10 * k, 14 * k, seed + 9, 0.1, 10)}" fill="#27407A" opacity="0.8"/>')
    out.append(taper(L([(-140, -160), (-122, -150), (-104, -160)]), 3 * k, 3 * k, "#8A5A2A", 0.9))
    out.append(painted(D, blob_pts(*P(-110, -110), 16 * k, 14 * k, seed + 10, 0.06, 10), GL, seed + 10, sk=0.2, n=4, inkw=1.4, hi=0.35))
    out.append(painted(D, L([(96, -170), (120, -120), (116, -96), (92, -100), (80, -150)]), GL, seed + 11, sdir=(0.6, 0.6), sk=0.2, angle=-80, n=10, inkw=1.6, hi=0.35))
    book = L([(98, -148), (140, -156), (146, -98), (104, -90)])
    out.append(painted(D, book, ("#F6EAC8", "#E2C890", "#8A6A3A"), seed + 12, sdir=(0.7, 0.4), sk=0.15, angle=-90, n=8, inkw=1.6, hi=0.4))
    for j in range(5):
        out.append(pline(L([(108 + j * 0.5, -140 + j * 9), (136 + j * 0.8, -146 + j * 9)]), "#8A6A3A", 1.1, seed + j, 0.6, 1))
    out.append(painted(D, blob_pts(*P(110, -108), 16 * k, 14 * k, seed + 13, 0.06, 10), GL, seed + 13, sk=0.2, n=4, inkw=1.4, hi=0.35))
    # head: broad cheeks, a raccoon-dog mask of dark fur round the eyes, a pale pointed muzzle
    head = L([(-74, -262), (-66, -300), (-36, -322), (0, -326), (36, -322), (66, -300), (74, -262), (60, -236), (30, -222), (0, -218), (-30, -222), (-60, -236)])
    for sg in (-1, 1):
        ear = blob_pts(*P(sg * 50, -318), 14 * k, 13 * k, seed + 15 + sg, 0.06, 10)
        out.append(painted(D, ear, ("#6A4028", "#3A2010", "#1A0C04"), seed + 15 + sg, sk=0.2, n=4, inkw=1.4, hi=0.3))
    out.append(painted(D, head, GL, seed + 16, sdir=(0.7, 0.5), sk=0.15, angle=-60, n=24, inkw=2, hi=0.45))
    # cheek ruffs (pale) and the dark mask band
    for sg in (-1, 1):
        out.append(painted(D, blob_pts(*P(sg * 48, -244), 26 * k, 18 * k, seed + 30 + sg, 0.1, 12, sg * 20), ("#FFE8C8", "#EAC898", "#A8784A"), seed + 30 + sg, sk=0.12, n=6, inkw=0, hi=0.3))
        mask = L([(sg * 6, -262), (sg * 24, -290), (sg * 52, -290), (sg * 66, -262), (sg * 50, -248), (sg * 22, -250)])
        out.append(painted(D, mask, ("#4A2A18", "#24120A", "#0A0402"), seed + 32 + sg, sk=0.15, angle=0, n=6, inkw=0, hi=0.25))
    muzzle = L([(-24, -262), (0, -268), (24, -262), (22, -238), (0, -226), (-22, -238)])
    out.append(painted(D, muzzle, ("#FFF0D8", "#F2D8B0", "#B8925A"), seed + 17, sdir=(0.6, 0.6), sk=0.12, angle=-60, n=8, inkw=1.2, hi=0.4))
    out.append(taper(L([(0, -320), (0, -296), (0, -268)]), 10 * k, 4 * k, "#FFE8C8", 0.6))
    for sg in (-1, 1):
        ex, ey = P(sg * 36, -272)
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{12 * k:.1f}" fill="#FFFFFF"/>')
        out.append(f'<circle cx="{ex + sg * 1.5 * k:.1f}" cy="{ey + 1:.1f}" r="{6.6 * k:.1f}" fill="#1A0E08"/>')
        out.append(f'<circle cx="{ex - 2 * k:.1f}" cy="{ey - 3 * k:.1f}" r="{2.4 * k:.1f}" fill="#FFFFFF"/>')
        out.append(ink(smooth_closed(ell_pts(ex, ey, 12 * k, 12 * k, 0, 360, 16)), "#0A0402", 1.6, seed, 1, 0.8))
    out.append(f'<path d="{blob(*P(0, -252), 9 * k, 6.5 * k, seed + 20, 0.08, 10)}" fill="#1A0E08"/>')
    out.append(f'<circle cx="{P(-3, -254)[0]:.1f}" cy="{P(-3, -254)[1]:.1f}" r="{1.8 * k:.1f}" fill="#FFFFFF" opacity="0.7"/>')
    out.append(pline(L([(0, -246), (0, -240)]), "#5A2A10", 2 * k, seed, 0.9, 1))
    out.append(pline(L([(-16, -238), (-8, -232), (0, -236), (8, -232), (16, -238)]), "#5A2A10", 2.2 * k, seed + 21, 0.9, 1))
    # straw hat
    brim = ell_pts(*P(0, -318), 92 * k, 22 * k, 0, 360, 30)
    out.append(painted(D, brim, ("#F2D890", "#D8B060", "#8A6A2A"), seed + 22, sdir=(0.3, 1), sk=0.2, angle=0, n=20, inkw=1.8, hi=0.4))
    dome = [P(-58, -322), P(-50, -350), P(-24, -368), P(24, -368), P(50, -350), P(58, -322), P(0, -314)]
    out.append(painted(D, dome, ("#F6E0A0", "#DCB868", "#8A6A2A"), seed + 23, sdir=(0.6, 0.6), sk=0.2, angle=-90, n=16, inkw=1.8, hi=0.45))
    for j in range(7):
        a = -60 + j * 20
        out.append(pline([P(math.sin(math.radians(a)) * 56, -322), P(math.sin(math.radians(a)) * 20, -366)], "#A8843A", 1.2, seed + j, 0.6, 1))
    return "".join(out)


@design("irasshaimase")
def irasshaimase():
    D = Doc2("jp-ir")
    # shop front: dark wooden lattice, a noren in the doorway, a red lantern
    out = [f'<rect width="600" height="600" fill="#3A2216"/>']
    wall = pd([(0, 0), (600, 0), (600, 470), (0, 470)])
    out.append(f'<path d="{wall}" fill="{D.lin([(0, "#5A3420"), (1, "#3A2012")])}"/>')
    for k in range(40):
        x = k * 15
        out.append(f'<path d="M {x} 220 L {x} 470" stroke="#24120A" stroke-width="6"/>')
    out.append(f'<path d="{pd([(0, 220), (600, 220), (600, 470), (0, 470)])}" fill="{D.lin([(0, "#FFB860", 0.45), (1, "#FFB860", 0.15)])}"/>')
    out.append(strokes(D.nid(), wall, (-40, 0, 600, 470), ["#7A4A2E", "#24120A"], 2801, n=80, angle=-88, length=(40, 120), width=(1, 3), opacity=(0.15, 0.35)))
    out.append(painted(D, densify([(-10, 200), (610, 200), (610, 224), (-10, 224)], 40), DARKWOOD, 2802, sdir=(0, 1), sk=0.25, angle=0, n=20, inkw=1.4, hi=0.3))
    # noren across the door (left), lantern on the right
    for j in range(4):
        x0 = 20 + j * 62
        nr = [(x0, 226), (x0 + 58, 226), (x0 + 60, 360), (x0 + 2, 362)]
        out.append(painted(D, densify(nr, 20), AI, 2803 + j, sdir=(0.8, 0.4), sk=0.15, angle=-90, n=12, inkw=1.2, hi=0.3))
    for j in range(5):
        a = math.radians(j * 72 - 90)
        out.append(f'<circle cx="{144 + math.cos(a) * 15:.1f}" cy="{292 + math.sin(a) * 15:.1f}" r="13" fill="#F6F0E4"/>')
    out.append(f'<circle cx="144" cy="292" r="7" fill="{AI[1]}"/>')
    out.append(chochin(D, 520, 238, 64, 104, 2808, pal=("#FFB0A0", "#E83A2A", "#8A1A12"), glow_c="#FFB060"))
    # gravel at the threshold, a stepping stone
    gr = pd([(0, 470), (600, 470), (600, 600), (0, 600)])
    out.append(f'<path d="{gr}" fill="#9A9288"/>')
    rnd = random.Random(2809)
    pebbles = []
    for _ in range(420):
        x, y = rnd.uniform(-5, 605), rnd.uniform(468, 605)
        r = rnd.uniform(2, 5) * (0.6 + (y - 470) / 260)
        pebbles.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 0.7:.1f}" fill="{rnd.choice(["#C8C0B4", "#ADA59A", "#E2DCD2", "#8A8278"])}"/>')
    out.append("".join(pebbles))
    out.append(f'<path d="{gr}" fill="{D.lin([(0, "#3A2010", 0.35), (0.4, "#3A2010", 0)])}"/>')
    out.append(painted(D, blob_pts(480, 520, 70, 20, 2810, 0.1, 16), STONE, 2810, sdir=(0.6, 0.8), sk=0.2, angle=0, n=14, inkw=1.4, hi=0.4))
    out.append(painted(D, blob_pts(110, 560, 60, 16, 2812, 0.1, 16), STONE, 2812, sdir=(0.6, 0.8), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.4))
    # the tanuki
    out.append(tanuki_statue(D, 290, 538, 1.0, 2811))
    # lettering on the dark beam area above the shop
    out.append(letters(D, 300, 116, "irasshaimase!", SERIF_IT, 92, "#FFF0D0", ["#FFFFFF", "#F6DCB0", "#FFE8C0"], 2820, max_w=460,
                       shadow="#140804", soff=(0.02, 0.04), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 158, "WELCOME IN", "#FFB860", font=JOS, size=20, ls=8, line_w=34, gap=12))
    return finish_b(D, out, 2821, "#FFFFFF", 0.35)


# ================================================================ 29. mochi — strawberry daifuku, cut open, with tea
def daifuku_half(D, cx, cy, r, seed, ang=0):
    """Strawberry daifuku cut in half: soft white mochi skin, a ring of red bean paste, a strawberry heart."""
    rnd = random.Random(seed)
    out = [f'<path d="{blob(cx + 6, cy + r * 0.85, r * 1.1, r * 0.22, seed, 0.05, 12)}" fill="#2A1A10" opacity="0.3"/>']
    outer = rot(blob_pts(cx, cy, r, r * 0.92, seed, 0.03, 22), cx, cy, ang)
    out.append(painted(D, outer, ("#FFFFFF", "#F8F4EE", "#C8C0C0"), seed, sdir=(0.6, 0.8), sk=0.12, angle=-40, n=12, sop=(0.1, 0.3), inkw=1.6, inkc="#8A7A78", hi=0.5))
    anko = rot(blob_pts(cx, cy + r * 0.04, r * 0.8, r * 0.74, seed + 1, 0.04, 20), cx, cy, ang)
    ad = smooth_closed(anko)
    out.append(f'<path d="{ad}" fill="#5A2A2E"/>')
    out.append(clipped(D, ad, [specks(seed + 2, (cx - r, cy - r, cx + r, cy + r), ["#7A3E40", "#3A1418", "#8A5050"], int(r * 3), (0.8, 2.4), (0.5, 0.9))]))
    # strawberry cross-section: red rim, pale streaks fanning out, seeds at the edge
    sb = [(cx, cy + r * 0.6), (cx - r * 0.5, cy + r * 0.05), (cx - r * 0.46, cy - r * 0.35), (cx - r * 0.2, cy - r * 0.52), (cx, cy - r * 0.42), (cx + r * 0.2, cy - r * 0.52), (cx + r * 0.46, cy - r * 0.35), (cx + r * 0.5, cy + r * 0.05)]
    sb = rot(sb, cx, cy, ang)
    sd = smooth_closed(sb)
    out.append(f'<path d="{sd}" fill="#E8283A"/>')
    inner = [f'<path d="{smooth_closed(rot([(cx, cy + r * 0.42), (cx - r * 0.34, cy + r * 0.02), (cx - r * 0.3, cy - r * 0.26), (cx, cy - r * 0.26), (cx + r * 0.3, cy - r * 0.26), (cx + r * 0.34, cy + r * 0.02)], cx, cy, ang))}" fill="#FF8A8A"/>']
    for j in range(9):
        a = math.radians(-90 + (j - 4) * 18 + ang)
        inner.append(taper([(cx, cy + r * 0.2), (cx + math.cos(a) * r * 0.45, cy + r * 0.2 + math.sin(a) * r * 0.55)], r * 0.06, r * 0.02, "#FFE0E0", 0.8))
    inner.append(f'<path d="{blob(cx, cy - r * 0.02, r * 0.1, r * 0.22, seed, 0.1, 8, ang)}" fill="#FFF0F0" opacity="0.9"/>')
    out.append(clipped(D, sd, inner))
    for j in range(12):
        t = j / 11
        p = sb[int(t * (len(sb) - 1))]
        out.append(f'<ellipse cx="{p[0] + rnd.uniform(-2, 2):.1f}" cy="{p[1] + rnd.uniform(-2, 2):.1f}" rx="1.4" ry="2" fill="#F6E070"/>')
    out.append(ink(sd, "#8A0A18", 1.2, seed, 1, 0.6))
    out.append(f'<path d="{blob(cx - r * 0.5, cy - r * 0.62, r * 0.25, r * 0.08, seed + 3, 0.2, 8, -30)}" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


def daifuku_whole(D, cx, cy, r, seed, pal=("#FFFFFF", "#F8F4EE", "#C8C0C0"), dust=True):
    pts = blob_pts(cx, cy, r, r * 0.74, seed, 0.03, 20)
    pts = [(x, min(y, cy + r * 0.5)) for x, y in pts]
    out = [f'<path d="{blob(cx + 6, cy + r * 0.5, r * 1.05, r * 0.18, seed, 0.05, 12)}" fill="#2A1A10" opacity="0.3"/>',
           painted(D, pts, pal, seed, sdir=(0.6, 0.8), sk=0.14, angle=-30, n=12, sop=(0.1, 0.3), inkw=1.6, inkc=dk(pal[2], 0.2), hi=0.55, hik=0.1)]
    if dust:
        out.append(specks(seed + 1, (cx - r * 0.7, cy - r * 0.6, cx + r * 0.7, cy + r * 0.3), ["#FFFFFF"], int(r), (0.6, 1.6), (0.6, 1)))
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.42, r * 0.28, r * 0.1, seed + 2, 0.2, 8, -20)}" fill="#FFFFFF" opacity="0.85"/>')
    return "".join(out)


def sakura_mochi(D, cx, cy, s, seed):
    """Pink mochi wrapped in a salted cherry leaf."""
    out = [f'<path d="{blob(cx + 6, cy + 30 * s, 60 * s, 10 * s, seed, 0.05, 12)}" fill="#2A1A10" opacity="0.3"/>']
    body = blob_pts(cx, cy, 52 * s, 32 * s, seed, 0.04, 18, -8)
    out.append(painted(D, body, SAKURA, seed, sdir=(0.6, 0.8), sk=0.15, angle=-20, n=10, inkw=1.4, inkc="#A84A6A", hi=0.5))
    out.append(specks(seed + 1, (cx - 40 * s, cy - 24 * s, cx + 40 * s, cy + 20 * s), ["#FFFFFF", "#E8889E"], 30, (0.8, 1.8), (0.5, 0.9)))
    lf = [(cx - 20 * s, cy + 34 * s), (cx - 50 * s, cy + 6 * s), (cx - 30 * s, cy - 26 * s), (cx + 20 * s, cy - 34 * s), (cx + 58 * s, cy - 12 * s), (cx + 40 * s, cy + 22 * s), (cx + 10 * s, cy + 6 * s)]
    out.append(painted(D, lf, ("#A8B860", "#6A7A2A", "#34400E"), seed + 2, sdir=(0.6, 0.8), sk=0.18, angle=-20, n=14, inkw=1.4, inkc="#2A3008", hi=0.35))
    out.append(pline([(cx - 20 * s, cy + 30 * s), (cx + 6 * s, cy - 6 * s), (cx + 50 * s, cy - 14 * s)], "#C8D088", 1.4, seed, 0.7, 1))
    for j in range(5):
        a = j * 0.5
        out.append(pline([(cx - 10 * s + j * 12 * s, cy + 16 * s - j * 9 * s), (cx - 24 * s + j * 12 * s, cy + 2 * s - j * 9 * s)], "#C8D088", 0.9, seed + j, 0.5, 1))
    return "".join(out)


@design("mochi")
def mochi():
    D = Doc2("jp-mo")
    out = [paper(D.nid(), "#E6E2D2", "#6A6A5A", 2901)]
    out.append(blooms(6, ["#D0D8C0", "#E8E0D0", "#C8D0B8"], 7, (40, 40, 560, 500), (120, 200), (0.12, 0.2)))
    out.append(soft_glow(D, 300, 360, 260, "#FFF8E8", 0.55))
    out.append('<g transform="translate(300 508) scale(1.14) translate(-300 -520)">')
    # dark wooden tray
    tr = [(40, 420), (560, 404), (584, 506), (20, 526)]
    out.append(cast(D, 310, 540, 290, 22, strength=0.45, seed=2902))
    out.append(f'<path d="{pd([(20, 526), (584, 506), (584, 528), (22, 548)])}" fill="#1E120A"/>')
    out.append(painted(D, densify(tr, 30), ("#7A5236", "#4A2E1C", "#1E1008"), 2903, sdir=(0.3, 1), sk=0.1, angle=-2, n=60, slen=(40, 120), sw=(1, 2.4), inkw=1.6, hi=0.3))
    # a pale kaishi paper under the sweets
    kp = [(140, 420), (430, 404), (470, 470), (150, 494)]
    out.append(painted(D, densify(kp, 30), ("#FFFFFF", "#F6F2EA", "#C8C0B0"), 2904, sdir=(0.3, 1), sk=0.08, angle=-2, n=14, inkw=1.2, hi=0.3))
    out.append(daifuku_whole(D, 212, 404, 62, 2905))
    out.append(daifuku_half(D, 306, 420, 62, 2906, ang=-6))
    out.append(daifuku_half(D, 402, 424, 56, 2907, ang=10))
    out.append(sakura_mochi(D, 140, 486, 0.86, 2908))
    # a cup of green tea
    cx, top = 452, 318
    out.append(painted(D, [(cx - 44, top), (cx + 44, top), (cx + 40, top + 90), (cx + 30, top + 100), (cx - 30, top + 100), (cx - 40, top + 90)], ("#C8C0A8", "#8A8068", "#4A4230"), 2909,
                       sdir=(1, 0.3), sk=0.25, angle=-90, n=16, inkw=1.6, hi=0.4))
    out.append(pline([(cx - 42, top + 30), (cx, top + 34), (cx + 42, top + 30)], "#3A5A2A", 3, 2910, 0.8, 1))
    out.append(f'<path d="{smooth_closed(ell_pts(cx, top, 44, 10, 0, 360, 20))}" fill="#9AB040"/>' + ink(smooth_closed(ell_pts(cx, top, 44, 10, 0, 360, 20)), INK, 1.4, 2911, 1, 0.6))
    out.append(steam(cx, top - 6, 60, 2912, "#FFFFFF", 2, 18, 5, 0.6))
    # a cherry blossom fallen on the tray
    out.append(sakura_flower(D, 500, 474, 14, 2913, 20))
    out.append("</g>")
    # lettering
    out.append(letters(D, 300, 150, "mochi", SERIF_IT, 114, "#5A2A2E", ["#7A3E40", "#3A1418", "#8A5050"], 2920, max_w=340,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#E8A8A8"))
    out.append(ruled(300, 188, "SOFT, SWEET & SQUISHY", "#C8283A", font=JOS, size=19, ls=5, line_w=26, gap=12))
    return finish_b(D, out, 2921)


# ================================================================ 30. kotatsu — winter afternoons under the quilt, mikan on the table
def mikan(D, cx, cy, r, seed, leaf=False):
    pts = blob_pts(cx, cy, r, r * 0.88, seed, 0.03, 16)
    out = [f'<path d="{blob(cx + 3, cy + r * 0.8, r * 0.9, r * 0.2, seed, 0.05, 10)}" fill="#3A1A08" opacity="0.25"/>',
           painted(D, pts, MIKAN, seed, sdir=(0.6, 0.8), sk=0.2, angle=-40, n=10, inkw=1.3, inkc="#7A3008", hi=0.45)]
    out.append(specks(seed, (cx - r * 0.8, cy - r * 0.7, cx + r * 0.8, cy + r * 0.7), ["#C8600A", "#FFD080"], int(r * 1.4), (0.6, 1.2), (0.4, 0.8)))
    out.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.38, r * 0.2, r * 0.12, seed + 1, 0.2, 8, -30)}" fill="#FFFFFF" opacity="0.6"/>')
    out.append(f'<path d="{blob(cx + r * 0.05, cy - r * 0.72, r * 0.12, r * 0.08, seed + 2, 0.2, 8)}" fill="#4A6A1A"/>')
    if leaf:
        out.append(leaf_simple(D, cx + r * 0.1, cy - r * 0.78, r * 1.1, r * 0.3, -30, ("#8AB858", "#3E7A2A", "#1A4A14"), seed + 3, inkw=1))
    return "".join(out)


def peeled_mikan(D, cx, cy, r, seed):
    out = [f'<path d="{blob(cx + 3, cy + r * 0.5, r * 1.6, r * 0.3, seed, 0.05, 12)}" fill="#3A1A08" opacity="0.25"/>']
    for j in range(5):
        a = math.radians(j * 72 - 90)
        tip = (cx + math.cos(a) * r * 1.6, cy + math.sin(a) * r * 1.0)
        pp = [(cx + math.cos(a - 0.5) * r * 0.6, cy + math.sin(a - 0.5) * r * 0.4), tip, (cx + math.cos(a + 0.5) * r * 0.6, cy + math.sin(a + 0.5) * r * 0.4)]
        out.append(painted(D, pp, MIKAN, seed + j, sdir=(0.6, 0.8), sk=0.15, n=4, inkw=1.1, inkc="#7A3008", hi=0.3))
        out.append(f'<path d="{smooth_closed([(x + (cx - x) * 0.15, y + (cy - y) * 0.15) for x, y in pp])}" fill="#FFF0D0" opacity="0.7"/>')
    for j in range(8):
        a = math.radians(j * 45)
        seg = rot(blob_pts(cx + math.cos(a) * r * 0.32, cy + math.sin(a) * r * 0.22, r * 0.34, r * 0.18, seed + 10 + j, 0.05, 10), cx + math.cos(a) * r * 0.32, cy + math.sin(a) * r * 0.22, math.degrees(a))
        out.append(painted(D, seg, ("#FFD080", "#F6A030", "#B0600A"), seed + 10 + j, sk=0.15, n=3, inkw=0.9, inkc="#9A4A08", hi=0.4))
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.12:.1f}" fill="#FFF0D0"/>')
    return "".join(out)


@design("kotatsu")
def kotatsu():
    D = Doc2("jp-kt")
    # room: plaster wall, a window full of falling snow, tatami below
    out = [paper(D.nid(), "#EEE0C6", FLECK, 3001)]
    win = (380, 40, 600, 270)
    out.append(f'<rect x="{win[0]}" y="{win[1]}" width="{win[2] - win[0]}" height="{win[3] - win[1]}" fill="{D.lin([(0, "#8A9AC0"), (1, "#D8E0EC")])}"/>')
    out.append(hg.far_trees(D, 250, 3002, "#7A88A8", n=10, h=(40, 80), x=(380, 620), snow=True))
    out.append(f'<rect x="{win[0]}" y="236" width="{win[2] - win[0]}" height="34" fill="#F4F6FA"/>')
    out.append(hg.flakes(3003, 40, win, (1.2, 3), "#FFFFFF", (0.7, 1)))
    for x in (380, 490):
        out.append(painted(D, densify([(x - 6, 30), (x + 6, 30), (x + 6, 280), (x - 6, 280)], 30), HINOKI, 3004 + x, sdir=(1, 0), sk=0.25, angle=-90, n=8, inkw=1.2, hi=0.3))
    out.append(painted(D, densify([(370, 270), (610, 270), (610, 284), (370, 284)], 30), HINOKI, 3006, sdir=(0, 1), sk=0.25, angle=0, n=8, inkw=1.2, hi=0.3))
    out.append(f'<path d="M 380 156 L 600 156" stroke="{HINOKI[1]}" stroke-width="5"/>')
    out.append(tatami(D, 330, 600, 3007, pal=("#E2D49A", "#C8B470", "#8A7A44")))
    out.append(f'<rect y="326" width="600" height="8" fill="#5A3A1A" opacity="0.5"/>')
    # the quilt draped from the table to the floor
    quilt = [(110, 320), (490, 312), (548, 400), (560, 520), (520, 548), (300, 560), (80, 552), (40, 520), (54, 400)]
    qd = smooth_closed(quilt)
    out.append(cast(D, 310, 560, 280, 24, strength=0.4, seed=3008))
    out.append(f'<path d="{qd}" fill="#C8402A"/>')
    pat = []
    rnd = random.Random(3009)
    for y in range(300, 580, 34):
        for x in range(20, 600, 34):
            xx, yy = x + (17 if (y // 34) % 2 else 0), y
            for j in range(5):
                a = math.radians(j * 72)
                pat.append(f'<circle cx="{xx + math.cos(a) * 5:.1f}" cy="{yy + math.sin(a) * 5:.1f}" r="4" fill="#F6E8D0" opacity="0.85"/>')
            pat.append(f'<circle cx="{xx}" cy="{yy}" r="2.4" fill="#F2B83A"/>')
    for a, b, c in (((150, 330), (130, 440), (110, 550)), ((300, 320), (300, 440), (290, 560)), ((450, 318), (480, 440), (500, 548)), ((230, 324), (200, 450), (190, 556)), ((380, 318), (400, 440), (410, 552))):
        pat.append(taper([a, b, c], 6, 18, "#4A0A06", 0.25))
        pat.append(taper([(a[0] - 10, a[1]), (b[0] - 12, b[1]), (c[0] - 14, c[1])], 3, 8, "#FFD8C8", 0.18))
    pat.append(shade_over(D, qd, "#2A0404", 0.45, 0, 0, 1, 1, 0.45))
    out.append(clipped(D, qd, pat))
    out.append(ink(qd, "#5A0A06", 2, 3010, 2, 0.7))
    # tabletop
    tt = [(100, 300), (500, 290), (512, 322), (90, 334)]
    out.append(f'<path d="{pd([(90, 334), (512, 322), (512, 334), (90, 346)])}" fill="#5A3418"/>')
    out.append(painted(D, densify(tt, 30), ("#E8B880", "#C08A50", "#7A4E22"), 3011, sdir=(0.3, 1), sk=0.1, angle=-2, n=30, inkw=1.6, hi=0.4))
    # a basket of mikan, one peeled, a cup of tea
    bk = ell_pts(300, 300, 96, 26, 0, 180, 16)
    out.append(painted(D, [(204, 290)] + bk + [(396, 290)], ("#E8C890", "#B8884A", "#6A4A20"), 3012, sdir=(0.3, 1), sk=0.2, angle=0, n=14, inkw=1.4, hi=0.3))
    for k, (x, y, r) in enumerate(((246, 266, 26), (300, 262, 28), (354, 268, 26), (274, 236, 25), (328, 234, 26))):
        out.append(mikan(D, x, y, r, 3013 + k, leaf=(k == 4)))
    out.append(painted(D, [(204, 290)] + ell_pts(300, 290, 96, 14, 0, 180, 16) + [(396, 290)], ("#E8C890", "#B8884A", "#6A4A20"), 3020, sdir=(0.3, 1), sk=0.2, angle=0, n=8, inkw=1.4, hi=0.3))
    out.append(peeled_mikan(D, 160, 304, 16, 3021))
    out.append(painted(D, [(430, 260), (470, 260), (467, 300), (433, 300)], ("#E8E0C8", "#B8A880", "#6A5A3A"), 3022, sdir=(1, 0.2), sk=0.25, angle=-90, n=8, inkw=1.4, hi=0.4))
    out.append(pline([(432, 276), (468, 276)], "#27407A", 3, 3023, 0.8, 1))
    out.append(f'<ellipse cx="450" cy="260" rx="20" ry="5" fill="#8AA040"/>')
    out.append(steam(450, 252, 40, 3024, "#FFFFFF", 2, 14, 4, 0.6))
    out.append('<g transform="translate(0 -14)">')
    # the cat asleep, half under the quilt
    cat = [(150, 548), (170, 512), (200, 498), (236, 504), (262, 530), (266, 556)]
    out.append(painted(D, cat, ("#FFC890", "#E8903A", "#9A5418"), 3025, sdir=(0.6, 0.8), sk=0.2, angle=-60, n=14, inkw=1.6, hi=0.4))
    for sg in (-1, 1):
        ex = 210 + sg * 26
        out.append(f'<path d="{smooth_closed([(ex - 12, 506), (ex + sg * 4, 482), (ex + 12, 504)])}" fill="#E8903A"/>' + ink(smooth_closed([(ex - 12, 506), (ex + sg * 4, 482), (ex + 12, 504)]), INK, 1.2, 3026, 1, 0.6))
        out.append(f'<path d="{smooth_closed([(ex - 6, 503), (ex + sg * 3, 490), (ex + 7, 502)])}" fill="#F6B0A0"/>')
    for x in (196, 226):
        out.append(taper([(x - 8, 522), (x, 526), (x + 8, 522)], 2.2, 2.2, "#3A1A08", 0.95))
    out.append(f'<path d="{smooth_closed([(206, 532), (216, 532), (211, 538)])}" fill="#E86A7A"/>')
    for k in range(3):
        out.append(f'<path d="M {180 + k * 14} 512 l 4 -8" stroke="#9A5418" stroke-width="2.4" stroke-linecap="round"/>')
    out.append(f'<path d="{blob(272, 550, 22, 9, 3027, 0.1, 10)}" fill="#FFE8C8"/>' + ink(blob(272, 550, 22, 9, 3027, 0.1, 10), INK, 1.2, 3028, 1, 0.6))
    out.append('</g>')
    # lettering on the wall
    out.append(letters(D, 214, 130, "kotatsu", SERIF_IT, 104, "#A8301E", ["#C8402A", "#7A140E", "#E06A4A"], 3030, max_w=276,
                       shadow="#FFFFFF", soff=(0.02, 0.035), angle=-40, hi="#FFB8A0"))
    out.append(label(214, 172, "MIKAN SEASON", JOS, 20, "#27407A", ls=7, max_w=280))
    return finish_b(D, out, 3031)


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
