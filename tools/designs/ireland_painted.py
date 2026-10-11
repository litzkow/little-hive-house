"""Ireland, hand-painted (gouache / storybook) edition: 30 magnets for Irish-Americans, the Irish abroad and anyone
who has fallen for Ireland.

Same painted idiom as the Brasil and Italia sets (brasil_painted.py): warm paper, layered washes with pooled edges,
brush strokes that follow each form, a warm brown pen line, hand-placed brush lettering, soft light and paper grain.
Colour story: forty shades of field green, Atlantic slate blues, whitewash and golden thatch, turf browns, heather
purple, half-door red and firelight amber. English with Irish (Gaeilge) words where they belong, fadas included.
No brands, no leprechauns, no drink jokes.

Run from tools/designs:  python3 ireland_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (blooms, bbox, cast, dab_crown, finish, grass, hill, label, letters, mix, painted, pline,
                            ridge, ruled, shift, sky, soft_glow, specks, taper, qpts, catmull, steam_wisps)
from gouache import blob, blob_pts, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from poster import ANTON
from paint import rough
from summer_gouache import rot, rect_pts, poly_pts, puff_cloud, sparkle, wave_lines, sea, seagull
from brasil_painted import (Doc2, ell_pts, pd, shade_over, light_over, gingham, cloth, leaf_simple, bird_v, heart_d,
                            p_heart, steam, wood_planks, cup_saucer, stamp, branch, berries, finish_b)
import holidays_gouache as hg
import figures

COL = "ireland"
INK = "#3A2418"
FLECK = "#8A6A4A"
lt, dk = hg.lt, hg.dk

# (light, base, dark) gouache palettes
EMER = ("#7ACB8A", "#1E8A4E", "#0E4E2C")
FIELD = ("#B6D884", "#6EA84A", "#2E6A2A")
MOSS = ("#A8C878", "#6A9A48", "#3A5E26")
THATCH = ("#F4D88E", "#CC9C4C", "#7A5420")
WASHW = ("#FFFFFF", "#F1EDE3", "#B2B2AC")
STONE = ("#CFCDC4", "#93918A", "#4E4C48")
SLATE = ("#8A9AAE", "#4E5E74", "#26303E")
ATL = ("#7AA8CC", "#2E5E86", "#12304E")
HEATH = ("#D0A0D0", "#8E5A9E", "#4A2A5A")
RUST = ("#F08A6A", "#C83A2A", "#7A1A12")
TURF = ("#9A7652", "#5E4028", "#2A1A0E")
GOLD = ("#FFE8A0", "#E0B04A", "#8A6418")
CREAM = ("#FFFDF4", "#F4EAD6", "#C8B494")
WHITE = ("#FFFFFF", "#F4F0E8", "#B8B0A6")
WOOD = ("#D8A06A", "#A86A3A", "#5E3618")
PINE = ("#ECC890", "#C8965A", "#7A5228")
MAHOG = ("#9A5A3A", "#5E2E1A", "#2A120A")
NAVY = ("#4A6A9A", "#22406E", "#0E1E3E")
WOOL = ("#FFFBEE", "#EDE2C8", "#B8A682")
BLACKF = ("#5A524E", "#2A2422", "#100C0A")

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def P3(c, a=0.35, b=0.35):
    return (lt(c, a), c, dk(c, b))


def lerp(a, b, t):
    return a + (b - a) * t


def lerp2(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def quad(D, pts, col, op=1.0):
    return f'<path d="{pd(pts)}" fill="{col}" opacity="{op}"/>'


# ================================================================ ireland toolkit
def stone(D, cx, cy, rx, ry, seed, pal=STONE, rot_=0, lichen=True, inkw=1.0, light=(-0.6, -0.8), haze=0.0):
    """One field stone: a lumpy grey blob with a lit top, a shadowed base, grain and a few lichen spots."""
    rnd = random.Random(seed)
    hz = (lambda c: mix(c, "#C8D4DC", haze)) if haze else (lambda c: c)
    base = mix(pal[1], rnd.choice([pal[0], pal[2], "#A89A84", "#8A949A", "#B0A890", "#7E8890"]), rnd.uniform(0.0, 0.45))
    d = smooth_closed(jitter(blob_pts(cx, cy, rx, ry, seed, 0.16, 9, rot_), seed, min(rx, ry) * 0.12))
    out = [f'<path d="{d}" fill="{hz(base)}"/>']
    out.append(f'<path d="{blob(cx + light[0] * rx * 0.25, cy + light[1] * ry * 0.3, rx * 0.72, ry * 0.55, seed + 1, 0.15, 10, rot_)}" fill="{hz(lt(base, 0.35))}" opacity="0.75"/>')
    out.append(f'<path d="{blob(cx - light[0] * rx * 0.2, cy - light[1] * ry * 0.38, rx * 0.8, ry * 0.42, seed + 2, 0.15, 10, rot_)}" fill="{hz(dk(base, 0.35))}" opacity="0.55"/>')
    if lichen and rx > 5:
        for _ in range(rnd.randint(0, 3)):
            a = rnd.uniform(0, 6.28)
            out.append(f'<circle cx="{cx + math.cos(a) * rx * 0.5:.1f}" cy="{cy + math.sin(a) * ry * 0.5:.1f}" r="{rnd.uniform(0.8, max(1.0, rx * 0.12)):.1f}" '
                       f'fill="{hz(rnd.choice(["#E8D86A", "#F2EEDC", "#C8C890", "#E8B85A"]))}" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>')
    if inkw:
        out.append(ink(d, hz("#2E2A26"), inkw, seed, 1, 0.55))
    return "".join(out)


def stone_wall(D, x0, x1, base, top, seed, s=14, pal=STONE, haze=0.0, inkw=1.0, gap="#2E2A28", tops=True):
    """A dry-stone wall in elevation: courses of irregular stones with dark gaps and upright cope stones on top.
    `top` is a number or a function x -> y."""
    rnd = random.Random(seed)
    tf = top if callable(top) else (lambda x: top)
    sil = [(x0, base)] + [(x, tf(x) - s * 0.3) for x in range(int(x0), int(x1) + 1, 12)] + [(x1, base)]
    hz = (lambda c: mix(c, "#C8D4DC", haze)) if haze else (lambda c: c)
    out = [f'<path d="{smooth_closed(sil)}" fill="{hz(gap)}"/>']
    y = base - s * 0.45
    row = 0
    while True:
        x = x0 - rnd.uniform(0, s)
        placed = False
        while x < x1 + s:
            w = s * rnd.uniform(0.9, 1.9)
            h = s * rnd.uniform(0.55, 0.85)
            yy = y + rnd.uniform(-s * 0.08, s * 0.08)
            if yy - h * 0.3 > tf(x + w / 2):
                out.append(stone(D, x + w / 2, yy, w / 2 - 0.8, h / 2, seed * 101 + row * 37 + int(x), pal, rnd.uniform(-10, 10), inkw=inkw * 0.7, haze=haze))
                placed = True
            x += w
        if not placed:
            break
        y -= s * 0.62
        row += 1
    if tops:
        x = x0
        while x < x1:
            w = s * rnd.uniform(0.45, 0.8)
            yy = tf(x + w / 2)
            out.append(stone(D, x + w / 2, yy - s * 0.18, w / 2, s * rnd.uniform(0.45, 0.6), seed + int(x) * 3, pal, rnd.uniform(-14, 14), inkw=inkw * 0.7, haze=haze))
            x += w * rnd.uniform(0.85, 1.05)
    return "".join(out)


def persp_wall(D, near, far, h_near, h_far, seed, pal=STONE, rows=5, haze_far=0.5, inkw=1.0):
    """A dry-stone wall running away from the viewer: base from `near` to `far`, height shrinking with distance."""
    rnd = random.Random(seed)
    out = []
    # silhouette (dark gaps)
    sil = [near, far, (far[0], far[1] - h_far * 1.08), (near[0], near[1] - h_near * 1.08)]
    out.append(f'<path d="{pd(sil)}" fill="#2A2624"/>')
    items = []
    u = 0.0
    while u < 1.0:
        h = lerp(h_near, h_far, u)
        L = math.hypot(far[0] - near[0], far[1] - near[1])
        du = max(0.004, h / rows * rnd.uniform(1.2, 2.0) / L)
        for r in range(rows):
            v = (r + 0.5 + rnd.uniform(-0.1, 0.1)) / rows
            bx, by = lerp2(near, far, u + du / 2)
            cx, cy = bx, by - h * v
            sw = du * L * 0.55
            sh = h / rows * 0.55
            items.append((u, cx, cy, max(1.2, sw), max(0.9, sh), lerp(0, haze_far, u)))
        # cope stones
        bx, by = lerp2(near, far, u + du / 2)
        items.append((u - 0.0001, bx, by - h * 1.02, max(1.0, du * L * 0.32), max(1.0, h / rows * 0.6), lerp(0, haze_far, u)))
        u += du
    for k, (u, cx, cy, rx, ry, hz) in enumerate(sorted(items, key=lambda t: -t[0])):
        out.append(stone(D, cx, cy, rx, ry, seed * 7 + k, pal, rnd.uniform(-8, 8), lichen=rx > 6, inkw=inkw * 0.6 if rx > 4 else 0, haze=hz))
    return "".join(out)


def path_wall(D, base, heights, seed, pal=STONE, rows=4, haze_far=0.45, inkw=1.0, cap=True):
    """A dry-stone wall following a curving base line (near -> far) with a height at each base point. Stones are
    laid in courses whose size follows the local height, drawn far to near so the near stones overlap."""
    rnd = random.Random(seed)
    # resample by arc length
    pts, hs = [base[0]], [heights[0]]
    for (p, q), (ha, hb) in zip(zip(base, base[1:]), zip(heights, heights[1:])):
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        n = max(1, int(L / 3))
        for i in range(1, n + 1):
            t = i / n
            pts.append(lerp2(p, q, t))
            hs.append(lerp(ha, hb, t))
    N = len(pts)
    sil = pts + [(x, y - h * 1.06) for (x, y), h in zip(pts[::-1], hs[::-1])]
    out = [f'<path d="{smooth_closed(sil)}" fill="#2A2624"/>']
    items = []
    i = 0
    while i < N - 1:
        h = hs[i]
        rows = max(2, int(round(h / 13)))
        step = max(1, int(h / rows * rnd.uniform(1.3, 2.2) / 3))
        j = min(N - 1, i + step)
        (xa, ya), (xb, yb) = pts[i], pts[j]
        u = i / N
        for r in range(rows):
            v = (r + 0.5 + rnd.uniform(-0.12, 0.12)) / rows
            cx, cy = (xa + xb) / 2, (ya + yb) / 2 - h * v
            rx = max(1.0, math.hypot(xb - xa, yb - ya) * 0.55)
            ry = max(0.8, h / rows * 0.58)
            items.append((u, cx, cy, rx, ry))
        if cap:
            items.append((u - 1e-4, (xa + xb) / 2, (ya + yb) / 2 - h * 1.0, max(1.0, math.hypot(xb - xa, yb - ya) * 0.4), max(0.9, h / rows * 0.62)))
        i = j
    for k, (u, cx, cy, rx, ry) in enumerate(sorted(items, key=lambda t: -t[0])):
        out.append(stone(D, cx, cy, rx, ry, seed * 7 + k, pal, rnd.uniform(-10, 10), lichen=rx > 6, inkw=inkw * 0.6 if rx > 4 else 0, haze=lerp(0, haze_far, u)))
    return "".join(out)


def thatch(D, pts, seed, box, slope=-95, pal=THATCH, moss=True, n=None):
    """Golden straw thatch: wash, sun-to-eave gradient, straw strokes down the slope, weather streaks, moss."""
    d = smooth_closed(pts)
    x0, y0, x1, y1 = box
    out = [wash(d, pal[1], seed, 3, 1.0, 0.45, edge=pal[2], edge_w=1.6)]
    cid = D.clip(f'<path d="{d}"/>')
    rnd = random.Random(seed)
    g = D.lin([(0, pal[0], 0.55), (0.55, pal[1], 0), (1, "#4A3418", 0.5)], 0, y0, 0, y1, "userSpaceOnUse")
    inner = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{g}"/>']
    n = n or int((x1 - x0) * (y1 - y0) / 22)
    inner.append(strokes(D.nid(), d, (x0 - 10, y0 - 10, x1 + 10, y1 + 10), [pal[0], "#FFF0B8", pal[2], "#A87A38", "#E8C070"], seed,
                         n=n, angle=slope, length=(8, 22), width=(0.6, 1.6), opacity=(0.35, 0.8), curve=0.1))
    for _ in range(int((x1 - x0) / 14)):
        x = rnd.uniform(x0, x1)
        L = rnd.uniform(0.2, 0.5) * (y1 - y0)
        inner.append(taper([(x, y1 - L), (x + 1, y1 - L * 0.4), (x, y1 + 4)], 0.5, rnd.uniform(3, 7), "#5A4A3A", rnd.uniform(0.12, 0.28)))
    if moss:
        for _ in range(5):
            inner.append(f'<path d="{blob(rnd.uniform(x0 + 20, x1 - 20), rnd.uniform(y0 + (y1 - y0) * 0.4, y1 - 6), rnd.uniform(10, 22), rnd.uniform(4, 8), rnd.randint(0, 999), 0.3, 10)}" fill="#7A8A3A" opacity="{rnd.uniform(0.2, 0.4):.2f}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, "#5A3A14", 1.8, seed, 2, 0.6))
    return "".join(out)


def sheep(D, x, base, s, seed, flip=1, graze=False, mark="#2E6AC8", horns=True, face=BLACKF, wool=WOOL, haze=0.0):
    """A west-of-Ireland blackface ewe: a cloud of creamy wool, black speckled face and legs, curled horns and
    a farmer's raddle mark on her back. (x, base) = between the hooves; drawn facing right (flip=-1 for left)."""
    rnd = random.Random(seed)
    hz = (lambda c: mix(c, "#C8D8E0", haze)) if haze else (lambda c: c)
    o = [f'<ellipse cx="0" cy="1" rx="34" ry="4.5" fill="#1A2010" opacity="0.25"/>']
    # far legs (darker)
    for lx in (-16, 14):
        o.append(taper([(lx + 3, -20), (lx + 4, -8), (lx + 3, 0)], 5, 4, hz(dk(face[1], 0.3))))
    # body: wool blob + dabs
    bpts = blob_pts(0, -30, 33, 19, seed, 0.06, 18)
    o.append(f'<path d="{smooth_closed(bpts)}" fill="{hz(wool[2])}"/>')
    items = []
    for i in range(46):
        a = rnd.uniform(0, 6.28)
        r = math.sqrt(rnd.random()) * 0.92
        px, py = math.cos(a) * 31 * r, -30 + math.sin(a) * 17 * r
        lit = -(math.cos(a) * -0.5 + math.sin(a) * -0.85) * r
        col = wool[0] if lit > 0.25 else (wool[2] if lit < -0.35 else wool[1])
        items.append((lit, px, py, rnd.uniform(4.5, 7.5), col))
    for lit, px, py, rr, col in sorted(items):
        o.append(f'<path d="{blob(px, py, rr, rr * 0.82, rnd.randint(0, 9999), 0.22, 8)}" fill="{hz(col)}"/>')
        if rnd.random() < 0.35:
            o.append(f'<path d="M {px - rr * 0.5:.1f} {py:.1f} q {rr * 0.5:.1f} {-rr * 0.6:.1f} {rr:.1f} 0" stroke="{hz(wool[2])}" stroke-width="0.9" fill="none" opacity="0.7"/>')
    o.append(ink(smooth_closed(bpts), hz("#6A5A40"), 1.3, seed, 1, 0.55))
    if mark:
        o.append(f'<path d="{blob(-8, -40, 9, 5, seed + 3, 0.3, 10)}" fill="{hz(mark)}" opacity="0.8"/>')
    # near legs
    for lx in (-20, 10):
        o.append(taper([(lx, -18), (lx + 1, -8), (lx, 0)], 5.5, 4.5, hz(face[1])))
        o.append(f'<path d="M {lx - 1} -9 l 2 0" stroke="{hz(face[0])}" stroke-width="1.6" opacity="0.6"/>')
    # head
    if graze:
        hx, hy, ang = 33, -10, 60
    else:
        hx, hy, ang = 36, -40, 18
    head = rot([(hx - 8, hy - 6), (hx + 2, hy - 9), (hx + 14, hy - 4), (hx + 20, hy + 4), (hx + 16, hy + 9), (hx + 4, hy + 8), (hx - 7, hy + 5)], hx, hy, ang)
    neck = [(24, -42 if not graze else -34), (hx - 2, hy - 8), (hx + 2, hy + 8), (26, -22)]
    o.append(f'<path d="{smooth_closed(neck)}" fill="{hz(wool[1])}"/>')
    # ears
    for sg in (-1, 1):
        ex, ey = rot([(hx - 3, hy - 4 * sg)], hx, hy, ang)[0]
        o.append(f'<path d="{blob(ex - 4, ey - 2 + sg * 2, 7, 2.6, seed + 10 + sg, 0.1, 8, -20 * sg + (40 if graze else 0))}" fill="{hz(face[1])}"/>')
    o.append(painted(D, head, tuple(hz(c) for c in face), seed + 4, sdir=(0.4, 0.9), sk=0.15, angle=ang, n=6, inkw=1.0, inkop=0.5, hi=0.5, hik=0.12))
    # white speckles on the face, eye
    for _ in range(4):
        px, py = rot([(hx + rnd.uniform(0, 14), hy + rnd.uniform(-3, 5))], hx, hy, ang)[0]
        o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rnd.uniform(0.8, 1.6):.1f}" fill="{hz("#F2ECE0")}" opacity="0.8"/>')
    ex, ey = rot([(hx + 3, hy - 2)], hx, hy, ang)[0]
    o.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="2" fill="#E8C870"/><circle cx="{ex:.1f}" cy="{ey:.1f}" r="1" fill="#100804"/>')
    if horns:
        cx_, cy_ = rot([(hx - 4, hy - 7)], hx, hy, ang)[0]
        sp = [(cx_ + 7 * math.cos(math.radians(a)) * (1 - i * 0.07), cy_ + 7 * math.sin(math.radians(a)) * (1 - i * 0.07))
              for i, a in enumerate(range(-150, 220, 40))]
        o.append(taper(sp, 4.5, 1.8, hz("#C8B48A")))
        o.append(pline(sp, hz("#7A6440"), 0.9, seed, 0.7, 1))
    # tufted fleece edge highlights
    for _ in range(8):
        a = rnd.uniform(-2.8, -0.4)
        px, py = math.cos(a) * 31, -30 + math.sin(a) * 18
        o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rnd.uniform(1.5, 3):.1f}" fill="#FFFFFF" opacity="0.7"/>')
    return f'<g transform="translate({x:.1f} {base:.1f}) scale({s * flip:.3f} {s:.3f})">' + "".join(o) + "</g>"


def cottage_small(D, x, base, w, h, seed, roof="thatch", door=RUST, side=0.28, haze=0.0, smoke=True, lit=False):
    """A little whitewashed cottage in 3/4 view for the middle distance: thatch or slate roof, chimney, red door."""
    rnd = random.Random(seed)
    hz = (lambda c: mix(c, "#C8D8E4", haze)) if haze else (lambda c: c)
    out = []
    sw = w * side
    rh = h * 0.75
    out.append(quad(D, [(x + w, base), (x + w + sw, base - sw * 0.2), (x + w + sw, base - h - sw * 0.2), (x + w + sw / 2, base - h - rh - sw * 0.1), (x + w, base - h)], hz("#C8CCD0")))
    out.append(painted(D, rect_pts(x, base - h, x + w, base, 10, seed, 0.4), tuple(hz(c) for c in WASHW), seed, sdir=(1, 0.3), sk=0.05, angle=-80,
                       n=max(4, int(w * h / 150)), inkw=0.9, inkop=0.45, hi=0.2))
    rf = [(x - w * 0.04, base - h + 2), (x + w * 1.02, base - h + 2), (x + w + sw / 2 + 2, base - h - rh), (x + sw / 2 - 2, base - h - rh)]
    if roof == "thatch":
        out.append(thatch(D, rf, seed + 1, bbox(rf), pal=tuple(hz(c) for c in THATCH), moss=False, n=int(w * rh / 18)))
    else:
        out.append(painted(D, rf, tuple(hz(c) for c in SLATE), seed + 1, sdir=(0, 1), sk=0.15, angle=0, n=int(w / 4), inkw=0.9, inkop=0.5, hi=0.3))
        for k in range(1, 5):
            yy = base - h - rh * k / 5
            out.append(f'<path d="M {x + sw / 2 * k / 5:.1f} {yy:.1f} L {x + w + sw / 2 * k / 5:.1f} {yy:.1f}" stroke="{hz(SLATE[2])}" stroke-width="0.8" opacity="0.5"/>')
    cx = x + w + sw / 2 - 2
    out.append(painted(D, rect_pts(cx - w * 0.06, base - h - rh - h * 0.28, cx + w * 0.06, base - h - rh + 3, 6, seed + 2, 0.2), tuple(hz(c) for c in WASHW), seed + 2, sk=0.1, n=2, inkw=0.8, hi=0.3))
    if smoke:
        sy = base - h - rh - h * 0.3
        out.append(taper(catmull([(cx, sy), (cx + 6, sy - 10), (cx + 2, sy - 22), (cx + 14, sy - 34), (cx + 24, sy - 40)], 5), 4, 9, hz("#E8ECF0"), 0.55))
    # windows and door
    for wx in (x + w * 0.16, x + w * 0.66):
        glass = hz("#FFD27A") if lit else hz("#3A4450")
        out.append(f'<rect x="{wx:.1f}" y="{base - h * 0.68:.1f}" width="{w * 0.17:.1f}" height="{h * 0.34:.1f}" fill="{glass}" stroke="{hz("#FFFFFF")}" stroke-width="{max(0.8, w * 0.012):.1f}"/>')
        if lit:
            out.append(D.glow(wx + w * 0.085, base - h * 0.5, w * 0.3, "#FFC860", 0.4))
    out.append(f'<path d="{hg.org_rect(x + w * 0.43, base - h * 0.72, w * 0.15, h * 0.72, seed + 3, 0.3, 6, 1)}" fill="{hz(door[1])}"/>')
    return "".join(out)


def fuchsia_bell(D, x, y, s, seed, ang=0, pal_out=("#F86A7A", "#D8243E", "#7A0A1E"), pal_in=("#B87AD8", "#6A2A9A", "#3A0E5A")):
    """A hanging fuchsia flower (deora Dé): red sepals flared up, purple skirt, stamens dangling; (x, y) = stalk top."""
    o = []
    o.append(pline([(x, y), (x + 1, y + s * 0.5), (x, y + s)], "#7A2A2A", max(1, s * 0.08), seed, 0.9, 1))
    cx, cy = x, y + s * 1.25
    o.append(painted(D, blob_pts(cx, cy, s * 0.22, s * 0.38, seed, 0.05, 10), pal_out, seed, sk=0.15, n=3, inkw=0.8, hi=0.4))
    for sg in (-1, 1):
        sep = [(cx, cy + s * 0.25), (cx + sg * s * 0.55, cy + s * 0.3), (cx + sg * s * 0.85, cy + s * 0.15), (cx + sg * s * 0.4, cy + s * 0.45)]
        o.append(f'<path d="{smooth_closed(sep)}" fill="{pal_out[1]}"/>')
        o.append(f'<path d="{smooth_closed(sep)}" fill="none" stroke="{pal_out[2]}" stroke-width="0.8" opacity="0.6"/>')
    sk = [(cx - s * 0.3, cy + s * 0.4), (cx + s * 0.3, cy + s * 0.4), (cx + s * 0.34, cy + s * 0.85), (cx, cy + s * 0.95), (cx - s * 0.34, cy + s * 0.85)]
    o.append(painted(D, sk, pal_in, seed + 1, sk=0.18, angle=-90, n=4, inkw=0.8, hi=0.35))
    for dx in (-0.12, 0, 0.12):
        o.append(pline([(cx + dx * s, cy + s * 0.9), (cx + dx * s * 1.6, cy + s * 1.35)], "#E83A5A", max(0.8, s * 0.05), seed, 0.9, 1))
    return f'<g transform="rotate({ang} {x:.1f} {y:.1f})">' + "".join(o) + "</g>"


def fuchsia_bush(D, cx, cy, rx, ry, seed, nflowers=14):
    rnd = random.Random(seed)
    out = [dab_crown(D, cx, cy, rx, ry, [("#7AAA5A", "#3E7A3A", "#1A4A22"), ("#8ABA62", "#4A8A3E", "#22502A")], seed, n=int(rx * ry / 24), size=(4, 8), inkw=1.0)]
    for i in range(nflowers):
        a = rnd.uniform(0, 6.28)
        r = math.sqrt(rnd.random()) * 0.85
        out.append(fuchsia_bell(D, cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r - 6, rnd.uniform(12, 17), seed + i, rnd.uniform(-25, 25)))
    return "".join(out)


def turf_sod(D, cx, cy, w, h, seed, rot_=0, pal=TURF):
    """A brick of cut turf: fibrous dark-brown with a lighter cut face and root threads."""
    rnd = random.Random(seed)
    pts = rot(rect_pts(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, max(4, w / 4), seed, max(0.4, w * 0.04)), cx, cy, rot_)
    o = [painted(D, pts, pal, seed, sdir=(0.5, 0.9), sk=0.2, angle=rot_, n=max(3, int(w * h / 40)), slen=(w * 0.2, w * 0.6), sw=(0.6, 1.6),
                 cols=["#B08A60", "#3A2414", "#7A5A3A"], inkw=0.9, inkop=0.5, hi=0.3)]
    for _ in range(int(w / 6)):
        px, py = cx + rnd.uniform(-w / 2, w / 2), cy + rnd.uniform(-h / 2, h / 2)
        px, py = rot([(px, py)], cx, cy, rot_)[0]
        o.append(f'<path d="M {px:.1f} {py:.1f} l {rnd.uniform(-4, 4):.1f} {rnd.uniform(-2, 2):.1f}" stroke="#C8A878" stroke-width="0.7" opacity="0.6"/>')
    return "".join(o)


def flame_tongue(cx, base, w, h, lean, seed, cols=("#FF7A1A", "#FFB43A", "#FFE8A0"), op=0.92):
    """One licking flame: an S-curved tongue with a hotter core; lean = sideways drift of the tip."""
    rnd = random.Random(seed)
    o = []
    for k, (c, sc) in enumerate(zip(cols, (1.0, 0.68, 0.36))):
        ww, hh = w * sc, h * (0.55 + 0.45 * sc)
        pts = [(cx - ww / 2, base), (cx - ww * 0.55, base - hh * 0.3), (cx - ww * 0.2 + lean * 0.3, base - hh * 0.62),
               (cx + lean + rnd.uniform(-2, 2), base - hh), (cx + ww * 0.25 + lean * 0.4, base - hh * 0.55), (cx + ww * 0.55, base - hh * 0.25), (cx + ww / 2, base)]
        o.append(f'<path d="{smooth_closed(pts)}" fill="{c}" opacity="{op if k == 0 else 0.95}"/>')
    return "".join(o)


def turf_fire(D, cx, base, w, seed, flames=True):
    """An open turf fire: sods leaned together, glowing seams, licking flames, a bed of pale ash and embers."""
    rnd = random.Random(seed)
    o = [D.glow(cx, base - w * 0.3, w * 1.2, "#FF9A3A", 0.75)]
    o.append(f'<path d="{blob(cx, base - 4, w * 0.6, w * 0.09, seed, 0.12, 14)}" fill="#D8C8B8"/>')
    o.append(f'<path d="{blob(cx, base - 6, w * 0.42, w * 0.06, seed + 1, 0.15, 14)}" fill="#FF8A2A" opacity="0.8"/>')
    # back sods
    for k, (dx, a, hh) in enumerate(((-0.24, 18, 0.36), (0.22, -20, 0.36), (0.0, 2, 0.42))):
        o.append(turf_sod(D, cx + dx * w, base - w * hh / 2 - 2, w * 0.16, w * hh, seed + k, a, pal=("#6A3E22", "#3A2010", "#1A0C04")))
    if flames:
        for k in range(7):
            fx = cx + (k - 3) * w * 0.085 + rnd.uniform(-3, 3)
            fh = w * rnd.uniform(0.32, 0.62) * (1 - abs(k - 3) * 0.12)
            o.append(flame_tongue(fx, base - w * 0.12, w * rnd.uniform(0.12, 0.17), fh, rnd.uniform(-10, 10), seed + 10 + k))
    # front sods with glowing edges
    for k, (dx, a, hh) in enumerate(((-0.34, 24, 0.3), (0.34, -26, 0.3), (-0.12, 10, 0.26), (0.14, -8, 0.24))):
        x, y = cx + dx * w, base - w * hh / 2 - 1
        o.append(turf_sod(D, x, y, w * 0.15, w * hh, seed + 20 + k, a, pal=("#7A4A2A", "#3E2414", "#1A0E06")))
        e = rot([(x + w * 0.075 * (1 if dx < 0 else -1), y - w * hh * 0.45), (x + w * 0.075 * (1 if dx < 0 else -1), y + w * hh * 0.4)], x, y, a)
        o.append(taper(e, 3.5, 1.5, "#FF8A2A", 0.9))
        o.append(taper(e, 1.4, 0.6, "#FFE08A", 0.9))
    o.append(specks(seed, (cx - w * 0.5, base - 12, cx + w * 0.5, base), ["#FFD060", "#FF6A1A", "#FFF2B0"], 30, (0.8, 2.2), (0.6, 1)))
    for _ in range(10):
        o.append(f'<circle cx="{cx + rnd.uniform(-w * 0.3, w * 0.3):.1f}" cy="{base - w * rnd.uniform(0.5, 0.9):.1f}" r="{rnd.uniform(0.8, 1.6):.1f}" fill="#FFD27A" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>')
    return "".join(o)


def hen(D, x, base, s, seed, flip=1, pal=(("#E89A5A", "#B8562A", "#6A2A10"))):
    """A brown farmyard hen pecking about; (x, base) = feet."""
    o = [f'<ellipse cx="0" cy="1" rx="18" ry="3" fill="#1A2010" opacity="0.25"/>']
    for lx in (-3, 4):
        o.append(taper([(lx, -12), (lx + 1, 0)], 2.4, 2, "#E8A830"))
        o.append(f'<path d="M {lx - 4} 0 L {lx + 5} 0 M {lx + 1} 0 l 3 -2" stroke="#E8A830" stroke-width="1.6" stroke-linecap="round"/>')
    body = [(-24, -30), (-16, -18), (-4, -10), (10, -12), (18, -22), (20, -34), (14, -40), (4, -32), (-10, -32), (-20, -42), (-26, -40)]
    o.append(painted(D, body, pal, seed, sdir=(0.5, 0.8), sk=0.18, angle=-10, n=14, inkw=1.3, hi=0.4))
    for k in range(4):
        o.append(pline([(-18 + k * 6, -30 + k), (-10 + k * 6, -18 + k)], pal[2], 1.1, seed + k, 0.6, 1))
    o.append(painted(D, blob_pts(18, -40, 7, 7.5, seed + 1, 0.05, 10), pal, seed + 1, sk=0.15, n=3, inkw=1.1, hi=0.4))
    o.append(f'<path d="M 13 -46 q 3 -6 6 -2 q 3 -5 5 1 q 2 3 -2 4 Z" fill="#E0281E"/>')
    o.append(f'<path d="{blob(23, -35, 2.5, 3.5, seed + 2, 0.1, 8)}" fill="#E0281E"/>')
    o.append(f'<path d="M 24 -41 L 30 -39 L 24 -37 Z" fill="#E8B030"/>')
    o.append(f'<circle cx="20" cy="-42" r="1.3" fill="#100804"/>')
    return f'<g transform="translate({x:.1f} {base:.1f}) scale({s * flip:.3f} {s:.3f})">' + "".join(o) + "</g>"


def geranium_pot(D, cx, base, w, seed, flower=("#FF7A7A", "#E0283A", "#8A0A1A")):
    rnd = random.Random(seed)
    h = w * 0.8
    pot = [(cx - w / 2, base - h), (cx + w / 2, base - h), (cx + w * 0.38, base), (cx - w * 0.38, base)]
    o = [cast(D, cx + 4, base, w * 0.7, 5, strength=0.4, seed=seed)]
    o.append(dab_crown(D, cx, base - h - w * 0.35, w * 0.75, w * 0.45, [("#8ACB6A", "#3E8A3A", "#1A4E1E")], seed, n=26, size=(4, 7), inkw=0.9))
    for k in range(5):
        fx, fy = cx + rnd.uniform(-w * 0.55, w * 0.55), base - h - w * rnd.uniform(0.35, 0.8)
        o.append(dab_crown(D, fx, fy, w * 0.16, w * 0.13, [flower], seed + k, n=9, size=(2.5, 4), inkw=0, base=False))
    o.append(painted(D, poly_pts(pot, 8, seed, 0.4), ("#F0A07A", "#C8643C", "#7A3218"), seed, sdir=(0.9, 0.3), sk=0.18, angle=-90, n=6, inkw=1.2, hi=0.4))
    o.append(f'<path d="{hg.org_rect(cx - w / 2 - 2, base - h - 2, w + 4, w * 0.16, seed + 1, 0.3, 6, 1)}" fill="#D8724A"/>')
    return "".join(o)


def finish_ie(D, out, seed, color=INK, op=1.0):
    return finish_b(D, out, seed, color, op)


# ================================================================ 1. céad míle fáilte — the thatched cottage, half door open
@design("cead-mile-failte")
def cead_mile_failte():
    D = Doc2("ie-cm")
    out = [sky(D, [(0, "#B4D2E6"), (0.5, "#DDEAEC"), (1, "#F4EAD2")], 3, 600, ["#FFFFFF", "#A8C8DC", "#F2E6CC"], 70, angle=-4, sop=(0.06, 0.16))]
    out.append(puff_cloud(D, 520, 250, 120, 4, ("#FFFFFF", "#F6F4F0", "#C8D0DC")))
    out.append(puff_cloud(D, 70, 236, 100, 5, ("#FFFFFF", "#F6F4F0", "#C8D0DC")))
    # hills behind
    out.append(hill(D, ridge([(-10, 312), (110, 286), (250, 300), (390, 278), (610, 296)], 5, 8), 600, ("#B4C8D2", "#8AA4B4", "#62808E"), 5, inkw=0))
    out.append(hill(D, ridge([(-10, 352), (150, 330), (330, 344), (470, 324), (610, 338)], 6, 6), 600, ("#B8D48E", "#82AC62", "#4E7A3E"), 6, inkw=1, inkop=0.3))
    # little fields with walls on the hill
    for k, (a, b, yy) in enumerate(((0, 120, 346), (470, 600, 336))):
        out.append(pline([(a, yy), ((a + b) / 2, yy - 4), (b, yy - 2)], "#5A6A50", 2.2, 10 + k, 0.5, 1))
    out.append(hill(D, [(-10, 440), (200, 432), (400, 436), (610, 428)], 600, FIELD, 7, inkw=0, n=160))
    # ---- the cottage (front wall 96..416, eave 340, base 466; side gable recedes right)
    fx0, fx1, ey, by = 96, 416, 340, 466
    dvx, dvy = 84, -16
    apex = (fx1 + dvx / 2, ey + dvy / 2 - 82)
    # gable (shaded side)
    gable = [(fx1, by), (fx1 + dvx, by + dvy), (fx1 + dvx, ey + dvy), apex, (fx1, ey)]
    out.append(painted(D, poly_pts(gable, 14, 11, 0.5), ("#E2E2E0", "#C4C8CC", "#8A9098"), 11, sdir=(1, 0.2), sk=0.06, angle=-80, n=60, inkw=1.6, hi=0.15))
    # the cottage's cast shadow on the grass (sun from the left)
    out.append(quad(D, [(fx1 + dvx, by + dvy), (fx1 + dvx + 90, by + dvy + 10), (fx1 + 60, by + 14), (fx1, by)], "#1E3A1A", 0.22))
    out.append(quad(D, [(fx1, by - 12), (fx1 + dvx, by + dvy - 12), (fx1 + dvx, by + dvy), (fx1, by)], "#2E2E34", 0.9))
    gw = [(fx1 + 30, 382), (fx1 + 50, 378), (fx1 + 50, 410), (fx1 + 30, 414)]
    out.append(quad(D, gw, "#3A4450") + ink(pd(gw), "#F4F4F0", 2.4, 12, 1, 0.9))
    # front wall (lit)
    out.append(painted(D, rect_pts(fx0, ey, fx1, by, 18, 13, 0.6), WASHW, 13, sdir=(1, 0.2), sk=0.04, angle=-80, n=120, inkw=1.8, hi=0.2))
    out.append(quad(D, [(fx0, by - 12), (fx1, by - 12), (fx1, by), (fx0, by)], "#2E2E34", 0.9))
    rnd = random.Random(14)
    for _ in range(14):
        sx, sy = rnd.uniform(fx0 + 10, fx1 - 10), rnd.uniform(ey + 30, by - 20)
        out.append(f'<path d="{blob(sx, sy, rnd.uniform(6, 12), rnd.uniform(3, 6), rnd.randint(0, 999), 0.2, 8)}" fill="none" stroke="#C8C4B8" stroke-width="1" opacity="0.5"/>')
    g = D.lin([(0, "#3A3A48", 0.4), (1, "#3A3A48", 0)])
    out.append(f'<rect x="{fx0}" y="{ey}" width="{fx1 - fx0}" height="26" fill="{g}"/>')
    # windows: deep reveals, white sashes, little panes
    for wx in (128, 336):
        out.append(f'<path d="{hg.org_rect(wx - 4, 370, 58, 58, wx, 0.4, 8, 2)}" fill="#9AA0A8" opacity="0.6"/>')
        glass = D.lin([(0, "#7A90A8"), (0.5, "#3A4A5E"), (1, "#2A3240")])
        out.append(f'<rect x="{wx}" y="374" width="50" height="52" fill="{glass}"/>')
        out.append(f'<path d="M {wx + 6} 378 l 14 0 l -12 18 Z" fill="#FFFFFF" opacity="0.22"/>')
        out.append(f'<rect x="{wx}" y="374" width="50" height="52" fill="none" stroke="#FBFBF6" stroke-width="4"/>')
        for t in (1 / 3, 2 / 3):
            out.append(f'<path d="M {wx} {374 + 52 * t:.1f} L {wx + 50} {374 + 52 * t:.1f}" stroke="#FBFBF6" stroke-width="2.2"/>')
        out.append(f'<path d="M {wx + 25} 374 L {wx + 25} 426" stroke="#FBFBF6" stroke-width="2.2"/>')
        out.append(ink(pd([(wx, 374), (wx + 50, 374), (wx + 50, 426), (wx, 426)]), INK, 1.4, wx, 1, 0.6))
        out.append(f'<path d="{hg.org_rect(wx - 6, 426, 62, 6, wx + 1, 0.3, 8, 1)}" fill="#E8E4DC"/>' + ink(hg.org_rect(wx - 6, 426, 62, 6, wx + 1, 0.3, 8, 1), INK, 1, wx, 1, 0.5))
    # geraniums on the left sill
    out.append(geranium_pot(D, 153, 426, 26, 15))
    # the half door: upper leaf open onto a firelit kitchen, lower leaf closed
    dx0, dx1, dy0, dmid = 232, 282, 360, 414
    out.append(f'<path d="{hg.org_rect(dx0 - 6, dy0 - 6, dx1 - dx0 + 12, by - dy0 + 6, 16, 0.4, 8, 2)}" fill="#8A9098" opacity="0.5"/>')
    inside = D.rad([(0, "#FFB860"), (0.45, "#B8582A"), (1, "#2A1208")], 0.3, 0.9, 0.9)
    out.append(f'<rect x="{dx0}" y="{dy0}" width="{dx1 - dx0}" height="{dmid - dy0}" fill="{inside}"/>')
    # glimpses inside: dresser with plates, the hanging lamp
    out.append(f'<rect x="{dx0 + 26}" y="{dy0 + 10}" width="22" height="44" fill="#5A2A14" opacity="0.8"/>')
    for k in range(3):
        out.append(f'<circle cx="{dx0 + 31 + k * 6}" cy="{dy0 + 20}" r="2.8" fill="#E8E0D0" opacity="0.85"/><circle cx="{dx0 + 31 + k * 6}" cy="{dy0 + 20}" r="1.4" fill="#4A6AB0" opacity="0.8"/>')
    out.append(f'<path d="M {dx0 + 26} {dy0 + 30} l 22 0" stroke="#3A1A0A" stroke-width="2"/>')
    out.append(D.glow(dx0 + 12, dy0 + 18, 16, "#FFE6A0", 0.8))
    out.append(f'<path d="M {dx0} {dy0} L {dx0 + 8} {dy0 + 4} L {dx0 + 8} {dmid} L {dx0} {dmid} Z" fill="#7A1A12" opacity="0.6"/>')
    ld = rect_pts(dx0, dmid, dx1, by, 10, 17, 0.4)
    out.append(painted(D, ld, RUST, 17, sdir=(1, 0.3), sk=0.1, angle=-90, n=14, inkw=1.6, hi=0.35))
    for t in (0.25, 0.5, 0.75):
        out.append(pline([(dx0 + (dx1 - dx0) * t, dmid + 4), (dx0 + (dx1 - dx0) * t, by - 2)], "#7A1A12", 1.2, int(t * 99), 0.6, 1))
    out.append(painted(D, rect_pts(dx0 - 3, dmid - 4, dx1 + 3, dmid + 3, 10, 18, 0.3), ("#FF9A7A", "#D8483A", "#7A1A12"), 18, sk=0.15, angle=0, n=4, inkw=1.2, hi=0.4))
    out.append(f'<circle cx="{dx1 - 9}" cy="{dmid + 20}" r="2.6" fill="#2A2020"/>')
    # a black-and-white cat sitting on the half door
    cx, cb = 250, dmid - 4
    cat = [(cx - 12, cb), (cx - 13, cb - 14), (cx - 9, cb - 24), (cx - 2, cb - 28), (cx + 6, cb - 26), (cx + 10, cb - 16), (cx + 11, cb)]
    out.append(painted(D, cat, ("#5A5258", "#2A2428", "#100C0E"), 19, sk=0.1, angle=-90, n=5, inkw=1, hi=0.35))
    out.append(f'<path d="{blob(cx + 2, cb - 10, 5, 9, 20, 0.1, 8)}" fill="#F4F0E8"/>')
    hd = blob_pts(cx + 1, cb - 33, 8.5, 7.5, 21, 0.05, 10)
    out.append(painted(D, hd, ("#5A5258", "#2A2428", "#100C0E"), 21, sk=0.1, n=3, inkw=1, hi=0.35))
    for sg in (-1, 1):
        out.append(f'<path d="M {cx + 1 + sg * 3} {cb - 39} L {cx + 1 + sg * 8} {cb - 46} L {cx + 1 + sg * 8.5} {cb - 35} Z" fill="#2A2428"/>')
    out.append(f'<path d="{blob(cx + 1, cb - 30, 4, 3, 22, 0.1, 8)}" fill="#F4F0E8"/>')
    for sg in (-1, 1):
        out.append(f'<circle cx="{cx + 1 + sg * 3.3}" cy="{cb - 34}" r="1.5" fill="#E8D040"/>')
    out.append(taper([(cx + 10, cb - 2), (cx + 20, cb + 4), (cx + 22, cb + 16)], 4, 2.5, "#2A2428"))
    # ---- the thatch: front plane and the rolled gable edge
    roof = [(fx0 - 14, ey + 12), (fx0 + 40, ey + 14), (fx1 - 40, ey + 14), (fx1 + 12, ey + 12), (apex[0] + 6, apex[1] - 4), (apex[0] - 20, apex[1] - 8),
            (fx0 + dvx / 2 + 20, apex[1] - 8), (fx0 + dvx / 2 - 6, apex[1] - 4)]
    out.append(f'<path d="{smooth_closed(shift(roof, 0, 8))}" fill="#2A2A30" opacity="0.25"/>')
    out.append(thatch(D, roof, 23, bbox(roof)))
    gband = [(fx1 + 2, ey + 14), (apex[0] + 6, apex[1] - 6), (fx1 + dvx + 14, ey + dvy + 10), (fx1 + dvx + 2, ey + dvy + 16), (apex[0] - 2, apex[1] + 16), (fx1 + 14, ey + 16)]
    out.append(thatch(D, gband, 24, bbox(gband), slope=-60, moss=False))
    # ridge band with criss-cross scollops
    rb = [(fx0 + dvx / 2 - 6, apex[1] - 4), (apex[0] + 6, apex[1] - 4), (apex[0] + 2, apex[1] + 14), (fx0 + dvx / 2 - 2, apex[1] + 14)]
    out.append(painted(D, poly_pts(rb, 16, 25, 0.6), ("#FCE6A8", "#D8AC5C", "#8A6024"), 25, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=1.4, hi=0.4))
    for k in range(int((apex[0] - fx0 - dvx / 2) / 16)):
        x = fx0 + dvx / 2 + 6 + k * 16
        out.append(f'<path d="M {x} {apex[1] - 2} L {x + 12} {apex[1] + 12} M {x + 12} {apex[1] - 2} L {x} {apex[1] + 12}" stroke="#7A5420" stroke-width="1.6" opacity="0.7"/>')
    # rounded, sun-caught eave and its cut edge
    out.append(taper([(fx0 - 14, ey + 12), (fx0 + 150, ey + 15), (fx1 + 12, ey + 12)], 5, 5, "#8A6424", 0.8))
    for k in range(60):
        x = fx0 - 10 + k * 5.6
        out.append(f'<path d="M {x:.1f} {ey + 10} l 0.6 5" stroke="#5A3A14" stroke-width="1" opacity="0.6"/>')
    # chimneys
    for (cx0, cw, ctop, base_) in ((apex[0] - 12, 26, apex[1] - 44, apex[1] + 4), (fx0 + dvx / 2 + 6, 24, apex[1] - 34, apex[1] + 2)):
        out.append(painted(D, rect_pts(cx0, ctop, cx0 + cw, base_, 8, int(cx0), 0.4), WASHW, int(cx0), sdir=(1, 0.2), sk=0.12, angle=-90, n=6, inkw=1.4, hi=0.3))
        out.append(quad(D, [(cx0 + cw, ctop), (cx0 + cw + 7, ctop - 2), (cx0 + cw + 7, base_ - 2), (cx0 + cw, base_)], "#B4B8C0"))
        out.append(painted(D, rect_pts(cx0 - 3, ctop - 6, cx0 + cw + 9, ctop + 2, 8, int(cx0) + 1, 0.3), STONE, int(cx0) + 1, sk=0.15, angle=0, n=4, inkw=1.2, hi=0.4))
    # turf smoke drifting off on the breeze
    sx, sy = apex[0] + 1, apex[1] - 54
    for k in range(7):
        t = k / 6
        px, py = sx + 12 + t * 92, sy - 6 - t * 18 + math.sin(t * 5) * 4
        rr = 5 + t * 12
        out.append(f'<path d="{blob(px, py, rr * 1.3, rr * 0.8, 40 + k, 0.2, 10)}" fill="#9AA4B2" opacity="{0.5 - t * 0.38:.2f}"/>')
        out.append(f'<path d="{blob(px - 2, py - 2, rr * 0.9, rr * 0.5, 50 + k, 0.2, 10)}" fill="#F2F4F6" opacity="{0.55 - t * 0.4:.2f}"/>')
    # ---- foreground: flagged path, fuchsia hedge, a stone wall and a hen
    path = [(dx0 - 2, by), (dx1 + 2, by), (348, 610), (176, 610)]
    out.append(painted(D, poly_pts(path, 20, 26, 0.6), ("#D8D4C8", "#AEA89A", "#6A645A"), 26, sdir=(0, 1), sk=0.05, angle=0, n=30, inkw=0, hi=0.2))
    for k, yy in enumerate((482, 504, 532, 566)):
        t = (yy - by) / (610 - by)
        a, b = lerp(dx0, 176, t), lerp(dx1, 348, t)
        out.append(pline([(a + 2, yy), ((a + b) / 2, yy + 1), (b - 2, yy)], "#5A564E", 1.4, 27 + k, 0.6, 1))
        out.append(pline([((a + b) / 2 + (k % 2 - 0.5) * 20, yy), ((a + b) / 2 + (k % 2 - 0.5) * 24, yy + 22 + k * 6)], "#5A564E", 1.2, 31 + k, 0.5, 1))
    out.append(grass(32, (0, 440, 600, 600), ["#4E8A3A", "#86B85A", "#2E6A2A", "#A8D070"], n=260, h=(6, 16), w=1.6))
    rnd = random.Random(39)
    for _ in range(40):
        x, y = rnd.uniform(0, 600), rnd.uniform(472, 600)
        if 160 < x < 360 and y > 470:
            continue
        if rnd.random() < 0.55:
            for j in range(6):
                a = j * 1.047
                out.append(f'<circle cx="{x + math.cos(a) * 2.6:.1f}" cy="{y + math.sin(a) * 1.6:.1f}" r="1.5" fill="#FFFFFF"/>')
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.3" fill="#F2C21C"/>')
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.4" fill="#F6D21C"/><circle cx="{x - 0.6:.1f}" cy="{y - 0.6:.1f}" r="0.9" fill="#FFF6A0"/>')
    out.append(fuchsia_bush(D, 92, 520, 92, 50, 33, nflowers=18))
    out.append(stone_wall(D, 404, 620, 600, lambda x: 520 + (x - 404) * 0.08, 34, s=18))
    out.append(hen(D, 372, 548, 1.05, 35, flip=-1))
    out.append(geranium_pot(D, 304, 478, 24, 36, flower=("#FFA8C8", "#E8508A", "#8A1A4A")))
    # ---- lettering
    out.append(letters(D, 300, 136, "céad míle fáilte", SERIF_IT, 80, "#1E5A3A", ["#2E7A4E", "#0E3E24", "#3E8A5A"], 37, max_w=470,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#8ACB9A"))
    out.append(ruled(300, 182, "A HUNDRED THOUSAND WELCOMES", "#8A2A1A", font=JOS, size=20, ls=3, line_w=22, gap=10, max_w=380))
    return finish_ie(D, out, 38)


# ================================================================ 2. brown bread and tea — soda bread, butter and the pot in its cosy
def soda_loaf(D, cx, cy, w, h, seed, cut=True):
    """Round brown soda bread: domed crust with the deep cross cut, flour dusting, crackled crust."""
    rnd = random.Random(seed)
    pts = []
    for i in range(30):
        a = math.pi * 2 * i / 30
        r = 1 + 0.04 * math.sin(a * 4 + 0.5)
        x = cx + w / 2 * math.cos(a) * r
        y = cy + (h * 0.62 * math.sin(a) if math.sin(a) < 0 else h * 0.38 * math.sin(a)) * r
        pts.append((x, y))
    crust = ("#C8925A", "#8E5428", "#4A2610")
    o = [painted(D, pts, crust, seed, sdir=(0.6, 0.8), sk=0.2, angle=-30, n=90, slen=(10, 30), sw=(1.5, 4),
                 cols=["#D8A066", "#6A3A18", "#A86A34", "#E8B87A"], inkw=2, inkop=0.7, hi=0.45, hik=0.08, curve=0.4)]
    cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
    inner = []
    # oat flakes and bran on the crust
    for _ in range(70):
        a, r = rnd.uniform(0, 6.28), math.sqrt(rnd.random())
        x, y = cx + math.cos(a) * w * 0.48 * r, cy - h * 0.15 + math.sin(a) * h * 0.4 * r
        inner.append(f'<path d="{blob(x, y, rnd.uniform(1.5, 3.2), rnd.uniform(1, 1.8), rnd.randint(0, 999), 0.2, 6, rnd.uniform(0, 180))}" fill="{rnd.choice(["#F2D8A8", "#6A3A18", "#E8C890", "#3A1E0A"])}" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>')
    # flour dusting
    for _ in range(4):
        inner.append(f'<path d="{blob(cx + rnd.uniform(-w * 0.3, w * 0.3), cy - h * rnd.uniform(0.2, 0.45), rnd.uniform(14, 30), rnd.uniform(6, 12), rnd.randint(0, 999), 0.3, 10)}" fill="#FFF8EC" opacity="0.4"/>')
    inner.append(specks(seed + 1, (cx - w * 0.4, cy - h * 0.6, cx + w * 0.4, cy), ["#FFFFFF", "#FFF4E0"], 120, (0.6, 1.6), (0.4, 0.9)))
    out_cid = f'<g {cid}>{"".join(inner)}</g>'
    o.append(out_cid)
    # the cross: two deep cuts, opened, with pale inner crumb
    top = (cx, cy - h * 0.62)
    for (p0, p1) in (((cx - w * 0.44, cy - h * 0.08), (cx + w * 0.44, cy - h * 0.12)), ((cx + w * 0.02, cy - h * 0.6), (cx - w * 0.02, cy + h * 0.3))):
        mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - h * 0.18)
        line = qpts(p0, mid, p1, 14)
        o.append(taper([(x + 2, y + 3) for x, y in line], 10, 10, "#2A1206", 0.5))
        o.append(taper(line, 9, 9, "#E8C08A", 0.95))
        o.append(taper([(x - 1, y - 1.5) for x, y in line], 3, 3, "#FFF0D0", 0.8))
        o.append(taper([(x + 1, y + 3) for x, y in line], 2, 2, "#6A3A18", 0.8))
    # crackles
    for _ in range(9):
        a = rnd.uniform(-2.8, -0.3)
        x, y = cx + math.cos(a) * w * 0.35, cy + math.sin(a) * h * 0.45
        o.append(pline([(x, y), (x + rnd.uniform(-8, 8), y + rnd.uniform(-5, 5)), (x + rnd.uniform(-14, 14), y + rnd.uniform(-8, 8))], "#4A2410", 1.1, rnd.randint(0, 99), 0.6, 1))
    return "".join(o)


def bread_slice(D, cx, cy, w, h, seed, rot_=0):
    """A slice of round brown soda bread standing up: flat base, domed crust rim, nubbly crumb with oats and bran.
    (cx, cy) = middle of the base."""
    rnd = random.Random(seed)
    pts = [(cx - w / 2, cy), (cx - w * 0.5, cy - h * 0.3)] + [(cx - w / 2 * math.cos(math.radians(a)), cy - h * 0.3 - h * 0.7 * math.sin(math.radians(a))) for a in range(15, 166, 15)] + [(cx + w * 0.5, cy - h * 0.3), (cx + w / 2, cy)]
    pts = rot(pts, cx, cy, rot_)
    o = [painted(D, pts, ("#A86A3A", "#6E3C1C", "#3A1E0A"), seed, sk=0.12, n=8, inkw=1.6, hi=0.3)]
    inner_pts = [(cx + (x - cx) * 0.88, cy + (y - cy) * 0.9 - 2) for x, y in pts]
    o.append(f'<path d="{smooth_closed(inner_pts)}" fill="#C89A68"/>')
    cid = D.clip(f'<path d="{smooth_closed(inner_pts)}"/>')
    inner = [specks(seed + 1, (cx - w / 2, cy - h, cx + w / 2, cy), ["#8A5A30", "#E8C898", "#5A3418", "#F2DCB0"], int(w * h / 14), (0.8, 2.2), (0.5, 0.95))]
    for _ in range(12):
        x, y = cx + rnd.uniform(-w * 0.35, w * 0.35), cy - rnd.uniform(h * 0.1, h * 0.8)
        inner.append(f'<path d="{blob(x, y, rnd.uniform(1.5, 3), rnd.uniform(1, 2), rnd.randint(0, 999), 0.3, 6)}" fill="#5A3418" opacity="0.6"/>')
    inner.append(shade_over(D, smooth_closed(inner_pts), "#3A1A06", 0.3, 0, 0, 1, 1, 0.5))
    o.append(f'<g {cid}>{"".join(inner)}</g>')
    return "".join(o)


def brigid_cross(D, cx, cy, s, seed, rot_=0):
    """St Brigid's cross of plaited green-gold rushes: a woven square centre, four offset arms tied at the ends."""
    rnd = random.Random(seed)
    o = []
    rush = ["#D8C47A", "#B8A458", "#E8D890", "#A89048", "#C8B468"]
    w = s * 0.28
    for k in range(4):
        a = k * 90 + rot_
        # each arm: a bundle of strands from the centre outwards, offset sideways (pinwheel)
        strands = []
        for j in range(5):
            off = -w * 0.1 + j * w * 0.22
            p0 = (-w * 0.5, off)
            p1 = (s, off + rnd.uniform(-1, 1))
            strands.append((p0, p1, rush[j % len(rush)]))
        g = []
        g.append(f'<path d="M {-w * 0.5:.1f} {-w * 0.2:.1f} L {s:.1f} {-w * 0.2:.1f} L {s:.1f} {w * 1.0:.1f} L {-w * 0.5:.1f} {w * 1.0:.1f} Z" fill="#2A1A0A" opacity="0.25" transform="translate(3 4)"/>')
        for (p0, p1, c) in strands:
            g.append(taper([p0, ((p0[0] + p1[0]) / 2, p0[1] + 0.6), p1], w * 0.24, w * 0.2, c))
            g.append(f'<path d="M {p0[0]:.1f} {p0[1] - w * 0.06:.1f} L {p1[0]:.1f} {p1[1] - w * 0.06:.1f}" stroke="#FFF6C8" stroke-width="0.9" opacity="0.6"/>')
        g.append(ink(f"M {-w * 0.5:.1f} {-w * 0.22:.1f} L {s:.1f} {-w * 0.22:.1f} M {-w * 0.5:.1f} {w * 0.98:.1f} L {s:.1f} {w * 0.98:.1f}", "#6A5420", 1.2, seed + k, 1, 0.7))
        # tie and frayed tips
        g.append(f'<rect x="{s * 0.72:.1f}" y="{-w * 0.3:.1f}" width="{w * 0.28:.1f}" height="{w * 1.36:.1f}" fill="#7A3A1A"/>')
        for j in range(5):
            y = -w * 0.1 + j * w * 0.22
            g.append(taper([(s, y), (s + w * rnd.uniform(0.5, 0.9), y + rnd.uniform(-2, 2))], w * 0.2, 0.6, rush[j % 5]))
        o.append(f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({a:.1f})">{"".join(g)}</g>')
    # woven centre
    c = w * 1.25
    o.append(f'<path d="{hg.org_rect(cx - c / 2, cy - c / 2, c, c, seed, 0.4, 6, 1)}" fill="#C8B468"/>')
    for j in range(4):
        t = -c / 2 + (j + 0.5) * c / 4
        o.append(f'<path d="M {cx - c / 2:.1f} {cy + t:.1f} L {cx + c / 2:.1f} {cy + t:.1f}" stroke="#E8D890" stroke-width="{c / 5:.1f}" opacity="0.7"/>')
        o.append(f'<path d="M {cx + t:.1f} {cy - c / 2:.1f} L {cx + t:.1f} {cy + c / 2:.1f}" stroke="#A89048" stroke-width="1" opacity="0.7"/>')
    o.append(ink(hg.org_rect(cx - c / 2, cy - c / 2, c, c, seed, 0.4, 6, 1), "#6A5420", 1.4, seed, 1, 0.8))
    return "".join(o)


def tea_cosy(D, cx, base, w, h, seed, bands=(("#F08A7A", "#D23A2E", "#7A1410"), CREAM, EMER, CREAM, ("#F6D27A", "#E0A030", "#8A5A10"))):
    """A hand-knitted tea cosy over the pot: striped rib knit, a pom-pom, spout and handle poking out."""
    rnd = random.Random(seed)
    top = base - h
    # spout and handle of the brown pot
    sp = [(cx - w * 0.42, base - h * 0.38), (cx - w * 0.62, base - h * 0.6), (cx - w * 0.7, base - h * 0.72), (cx - w * 0.64, base - h * 0.76), (cx - w * 0.52, base - h * 0.62), (cx - w * 0.38, base - h * 0.5)]
    o = [cast(D, cx + 10, base, w * 0.62, 12, strength=0.45, seed=seed)]
    o.append(painted(D, sp, ("#A86A3A", "#6A3418", "#2E1408"), seed + 1, sk=0.2, angle=-60, n=6, inkw=1.6, hi=0.5))
    o.append(painted(D, [(cx + w * 0.4, base - h * 0.62), (cx + w * 0.62, base - h * 0.6), (cx + w * 0.64, base - h * 0.4), (cx + w * 0.42, base - h * 0.3), (cx + w * 0.42, base - h * 0.38), (cx + w * 0.54, base - h * 0.42), (cx + w * 0.54, base - h * 0.54), (cx + w * 0.4, base - h * 0.54)],
                     ("#A86A3A", "#6A3418", "#2E1408"), seed + 2, sk=0.2, n=5, inkw=1.6, hi=0.4))
    # cosy body
    body = [(cx - w / 2, base), (cx - w * 0.52, base - h * 0.45), (cx - w * 0.4, base - h * 0.82), (cx - w * 0.18, top + 4), (cx + w * 0.18, top + 4),
            (cx + w * 0.4, base - h * 0.82), (cx + w * 0.52, base - h * 0.45), (cx + w / 2, base)]
    d = smooth_closed(body)
    o.append(f'<path d="{d}" fill="{bands[0][1]}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    nb = len(bands)
    bh = h / nb
    for i, pal in enumerate(bands):
        y0 = top + i * bh
        inner.append(f'<path d="M {cx - w} {y0 + 3 * math.sin(i):.1f} Q {cx} {y0 + 10:.1f} {cx + w} {y0 + 3 * math.cos(i):.1f} L {cx + w} {y0 + bh + 12:.1f} L {cx - w} {y0 + bh + 12:.1f} Z" fill="{pal[1]}"/>')
    # rib knit columns: little V stitches
    cols_n = 14
    for j in range(cols_n + 1):
        u = j / cols_n - 0.5
        for i in range(int(h / 7)):
            y = top + 4 + i * 7
            yy = (y - top) / h
            x = cx + u * w * (0.55 + 0.45 * min(1, yy * 1.8)) * 1.05
            band = bands[min(nb - 1, int((y - top) / bh))]
            inner.append(f'<path d="M {x - 3:.1f} {y - 2:.1f} L {x:.1f} {y + 3:.1f} L {x + 3:.1f} {y - 2:.1f}" stroke="{band[0]}" stroke-width="1.6" fill="none" opacity="0.7" stroke-linecap="round"/>')
            inner.append(f'<path d="M {x - 3:.1f} {y:.1f} L {x:.1f} {y + 5:.1f}" stroke="{band[2]}" stroke-width="0.9" fill="none" opacity="0.35"/>')
    inner.append(shade_over(D, d, "#2A0E06", 0.45, 0, 0, 1, 0.3, 0.4))
    inner.append(light_over(D, d, "#FFFFFF", 0.3, 0, 0, 0.5, 0.5))
    o.append(f'<g {cid}>{"".join(inner)}</g>')
    o.append(ink(d, INK, 2, seed, 2, 0.7))
    # ribbed hem
    o.append(painted(D, rect_pts(cx - w * 0.51, base - 12, cx + w * 0.51, base + 2, 10, seed + 3, 0.4), bands[0], seed + 3, sk=0.15, angle=-90, n=30, sw=(1, 2), inkw=1.4, hi=0.3))
    # pom-pom
    o.append(dab_crown(D, cx, top - 6, 22, 18, [bands[-1], bands[0]], seed + 4, n=60, size=(2.5, 4.5), inkw=1.2))
    return "".join(o)


def butter_dish(D, cx, cy, w, seed):
    """A block of golden Irish butter on a white dish with a blue band, a knife resting with a curl on it."""
    o = [cast(D, cx + 8, cy + w * 0.2, w * 0.62, w * 0.14, strength=0.45, seed=seed)]
    dish = ell_pts(cx, cy, w / 2, w * 0.17, 0, 360, 30)
    o.append(painted(D, dish, WHITE, seed, sdir=(0.4, 1), sk=0.1, angle=0, n=10, inkw=1.6, hi=0.4))
    o.append(ink(smooth_closed(ell_pts(cx, cy - 2, w * 0.43, w * 0.13, 0, 360, 30)), "#2E5AB8", 2.4, seed, 1, 0.8))
    bw, bh, bd = w * 0.52, w * 0.18, w * 0.16
    x0, y0 = cx - bw / 2, cy - bh - 2
    topf = [(x0, y0), (x0 + bd * 0.6, y0 - bd * 0.5), (x0 + bw + bd * 0.6, y0 - bd * 0.5), (x0 + bw, y0)]
    o.append(painted(D, topf, ("#FFF4B0", "#F8DC6A", "#C8A030"), seed + 1, sk=0.05, angle=0, n=6, inkw=1.2, hi=0.5))
    o.append(painted(D, [(x0, y0), (x0 + bw, y0), (x0 + bw, y0 + bh), (x0, y0 + bh)], ("#FFE88A", "#F2C84A", "#B8901E"), seed + 2, sdir=(0.3, 1), sk=0.12, angle=0, n=6, inkw=1.4, hi=0.3))
    o.append(quad(D, [(x0 + bw, y0), (x0 + bw + bd * 0.6, y0 - bd * 0.5), (x0 + bw + bd * 0.6, y0 + bh - bd * 0.5), (x0 + bw, y0 + bh)], "#D8A830"))
    # a scraped curl
    o.append(taper(catmull([(x0 + bw * 0.25, y0 - bd * 0.25), (x0 + bw * 0.4, y0 - bd * 0.45), (x0 + bw * 0.55, y0 - bd * 0.3)], 5), 3, 5, "#FFF6C0", 0.95))
    # knife
    o.append(taper([(cx - w * 0.62, cy + w * 0.05), (cx - w * 0.2, cy - w * 0.06)], 7, 7, "#3A2A1E"))
    o.append(taper([(cx - w * 0.2, cy - w * 0.06), (cx + w * 0.05, cy - w * 0.12), (cx + w * 0.2, cy - w * 0.15)], 9, 3, "#D8DCE4"))
    o.append(taper([(cx - w * 0.18, cy - w * 0.08), (cx + w * 0.18, cy - w * 0.16)], 2, 1, "#FFFFFF", 0.9))
    o.append(f'<path d="{blob(cx + w * 0.08, cy - w * 0.135, 7, 3, seed + 3, 0.2, 8)}" fill="#F8DC6A"/>')
    return "".join(o)


@design("brown-bread-and-tea")
def brown_bread_and_tea():
    D = Doc2("ie-bb")
    out = [sky(D, [(0, "#3E6A5A"), (1, "#28483C")], 3, 600, ["#4E7E6A", "#1E3A30", "#5A8A74"], 120, angle=-80, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 470, 140, 380, "#FFE6B0", 0.35))
    out.append(blooms(9, ["#4E8A70", "#1E3A30", "#6A9A80"], 8, (0, 0, 600, 420), (90, 170), (0.08, 0.14)))
    # a little framed window light falling on the wall
    out.append(f'<path d="M 360 0 L 600 0 L 600 300 L 470 420 Z" fill="#FFF2C8" opacity="0.08"/>')
    out.append(wood_planks(D, 418, 600, 41, PINE, 3))
    out.append(f'<rect y="412" width="600" height="10" fill="#2A1A0A" opacity="0.55"/>')
    # breadboard
    out.append(cast(D, 368, 520, 210, 30, strength=0.5, seed=42))
    board = ell_pts(356, 488, 196, 54, 0, 360, 40)
    out.append(painted(D, shift(board, 0, 12), ("#B07A44", "#7A4A22", "#3A200A"), 43, sk=0, n=20, inkw=1.6, hi=0))
    out.append(painted(D, board, ("#F0C890", "#D49A5A", "#8A5A2A"), 44, sdir=(0.4, 1), sk=0.12, angle=-4, n=60, slen=(30, 90), sw=(1, 2.4), inkw=1.8, hi=0.35))
    for k in range(5):
        out.append(pline(ell_pts(356, 488, 60 + k * 26, 14 + k * 7, 200, 340, 12), "#A87038", 1.1, 45 + k, 0.45, 1))
    # crumbs
    out.append(specks(46, (220, 470, 500, 520), ["#7A4420", "#C8925A", "#4A2410"], 40, (0.8, 2.4), (0.6, 1)))
    # the loaf, a farl cut away, two slices leaning in front
    out.append(soda_loaf(D, 378, 432, 236, 136, 47))
    out.append(bread_slice(D, 286, 508, 112, 70, 48, rot_=-10))
    out.append(bread_slice(D, 318, 520, 112, 70, 49, rot_=-3))
    # St Brigid's cross over the table, a soft shadow behind it
    out.append(brigid_cross(D, 474, 290, 62, 58, rot_=8))
    # a buttered slice on the left, then the dish
    out.append(butter_dish(D, 148, 528, 160, 50))
    # the teapot in its cosy and a cup of milky tea
    out.append(tea_cosy(D, 150, 430, 168, 176, 51))
    out.append(cup_saucer(D, 520, 560, 70, 52, rim=("#5A86D8", "#1F4BA8", "#0C2462"), coffee="#A8703E"))
    out.append(f'<path d="{blob(512, 494, 14, 3, 53, 0.1, 8)}" fill="#D8A878" opacity="0.8"/>')
    out.append(steam(520, 486, 40, 54, "#FFFFFF", 2, 18, 5, 0.6))
    out.append(steam(150, 228, 34, 55, "#FFFFFF", 1, 18, 5, 0.0))
    # lettering
    out.append(letters(D, 300, 132, "brown bread", SERIF_IT, 104, "#FFF2D8", ["#FFFFFF", "#F2DCB4", "#FFE8C0"], 56, max_w=460,
                       shadow="#10241C", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 182, "AND A POT OF TEA", "#F6D27A", font=JOS, size=24, ls=6, line_w=34, gap=14))
    return finish_ie(D, out, 57)



# ================================================================ 3. the full Irish — Sunday fry from above
def plate_top(D, cx, cy, R, seed, rim=EMER):
    out = [cast(D, cx + 12, cy + 16, R + 8, R * 0.98, strength=0.45, seed=seed)]
    out.append(painted(D, ell_pts(cx, cy, R, R, 0, 360, 40)[:-1], WHITE, seed, sdir=(0.6, 0.7), sk=0.05, angle=-30, n=40, inkw=2, hi=0.4))
    out.append(f'<path d="{blob(cx, cy, R * 0.74, R * 0.74, seed + 1, 0.01, 30)}" fill="#EEEAE2"/>')
    out.append(ink(blob(cx, cy, R * 0.74, R * 0.74, seed + 1, 0.01, 30), "#C8C0B4", 1.4, seed, 1, 0.6))
    out.append(ink(smooth_closed(ell_pts(cx, cy, R * 0.9, R * 0.9, 0, 360, 40)[:-1]), rim[1], 3, seed + 2, 1, 0.85))
    out.append(ink(smooth_closed(ell_pts(cx, cy, R * 0.94, R * 0.94, 0, 360, 40)[:-1]), rim[1], 1.2, seed + 3, 1, 0.6))
    out.append(shade_over(D, smooth_closed(ell_pts(cx, cy, R, R, 0, 360, 40)[:-1]), "#3A2A2A", 0.16, 0, 0, 1, 1, 0.5))
    return "".join(out)


def fried_egg(D, cx, cy, r, seed, yolk_off=(0, 0)):
    rnd = random.Random(seed)
    o = []
    wpts = blob_pts(cx, cy, r, r * 0.86, seed, 0.16, 16, rnd.uniform(0, 90))
    o.append(f'<path d="{smooth_closed(shift(wpts, 2, 3))}" fill="#3A2A1A" opacity="0.18"/>')
    o.append(f'<path d="{smooth_closed(wpts)}" fill="#C8884A"/>')
    inner = [(cx + (x - cx) * 0.88, cy + (y - cy) * 0.88) for x, y in wpts]
    o.append(painted(D, inner, ("#FFFFFF", "#FBF8F0", "#D8D0C0"), seed + 1, sk=0.06, n=10, inkw=0, hi=0.5))
    o.append(f'<path d="{smooth_closed(wpts)}" fill="none" stroke="#8A4A1A" stroke-width="1.6" opacity="0.6"/>')
    for _ in range(6):
        a = rnd.uniform(0, 6.28)
        o.append(f'<circle cx="{cx + math.cos(a) * r * 0.86:.1f}" cy="{cy + math.sin(a) * r * 0.75:.1f}" r="{rnd.uniform(1.5, 3):.1f}" fill="#A8622A" opacity="0.6"/>')
    yx, yy = cx + yolk_off[0], cy + yolk_off[1]
    yr = r * 0.4
    o.append(f'<circle cx="{yx + 2:.1f}" cy="{yy + 3:.1f}" r="{yr:.1f}" fill="#C8A890" opacity="0.4"/>')
    o.append(painted(D, blob_pts(yx, yy, yr, yr, seed + 2, 0.03, 14), ("#FFD860", "#F6A21A", "#C0640A"), seed + 2, sdir=(0.6, 0.7), sk=0.25, n=6, inkw=1.2, inkop=0.5, hi=0.4))
    o.append(f'<path d="{blob(yx - yr * 0.35, yy - yr * 0.4, yr * 0.35, yr * 0.18, seed + 3, 0.1, 8, -30)}" fill="#FFFFFF" opacity="0.85"/>')
    return "".join(o)


def rasher(D, cx, cy, s, ang, seed):
    """Irish back rasher: round pink eye of loin with a curling streaky tail, fat rim, browned edges."""
    rnd = random.Random(seed)
    pts = [(-30, -6), (-22, -20), (-6, -24), (8, -18), (20, -12), (40, -12), (58, -6), (66, 4), (56, 12), (36, 10), (18, 14), (0, 22), (-20, 20), (-32, 8)]
    pts = rot([(cx + x * s, cy + y * s) for x, y in pts], cx, cy, ang)
    o = [f'<path d="{smooth_closed(shift(pts, 2, 3))}" fill="#3A1A0A" opacity="0.2"/>']
    o.append(painted(D, pts, ("#F8E8D2", "#EED2B0", "#B8865A"), seed, sk=0.1, n=8, inkw=1.4, inkop=0.6, hi=0.3))
    eye = rot([(cx + x * s, cy + y * s) for x, y in [(-24, -4), (-16, -15), (-2, -17), (10, -10), (12, 2), (2, 14), (-14, 14), (-24, 6)]], cx, cy, ang)
    o.append(painted(D, eye, ("#F49A8A", "#D8605A", "#8A2A26"), seed + 1, sk=0.15, angle=ang, n=12, inkw=0.9, inkop=0.5, hi=0.35))
    tail = rot([(cx + x * s, cy + y * s) for x, y in [(14, -6), (40, -6), (58, -1), (60, 5), (40, 4), (16, 6)]], cx, cy, ang)
    o.append(painted(D, tail, ("#F0A090", "#D06A60", "#8A3028"), seed + 2, sk=0.1, angle=ang, n=6, inkw=0, hi=0.3))
    for _ in range(10):
        x, y = rot([(cx + rnd.uniform(-28, 60) * s, cy + rnd.uniform(-18, 16) * s)], cx, cy, ang)[0]
        o.append(f'<path d="{blob(x, y, rnd.uniform(2, 4), rnd.uniform(1, 2), rnd.randint(0, 99), 0.3, 6, rnd.uniform(0, 180))}" fill="#A0582A" opacity="0.5"/>')
    return "".join(o)


def sausage(D, cx, cy, L, w, ang, seed):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    pts = []
    for i in range(13):
        t = i / 12
        pts.append((cx + ux * L * (t - 0.5) - uy * w / 2 * (1 - (2 * t - 1) ** 8) ** 0.5, cy + uy * L * (t - 0.5) + ux * w / 2 * (1 - (2 * t - 1) ** 8) ** 0.5))
    for i in range(13):
        t = 1 - i / 12
        pts.append((cx + ux * L * (t - 0.5) + uy * w / 2 * (1 - (2 * t - 1) ** 8) ** 0.5, cy + uy * L * (t - 0.5) - ux * w / 2 * (1 - (2 * t - 1) ** 8) ** 0.5))
    o = [f'<path d="{smooth_closed(shift(pts, 3, 4))}" fill="#3A1A0A" opacity="0.22"/>']
    o.append(painted(D, pts, ("#D88A4A", "#9A4E22", "#4A200A"), seed, sdir=(0.5, 0.8), sk=0.22, angle=ang, n=10, inkw=1.5, hi=0.35))
    o.append(taper([(cx - ux * L * 0.35 + uy * w * 0.22, cy - uy * L * 0.35 - ux * w * 0.22), (cx + ux * L * 0.3 + uy * w * 0.22, cy + uy * L * 0.3 - ux * w * 0.22)], 2.5, 2.5, "#FFE8C8", 0.7))
    for k in range(4):
        t = -0.3 + k * 0.2
        o.append(pline([(cx + ux * L * t - uy * w * 0.3, cy + uy * L * t + ux * w * 0.3), (cx + ux * L * (t + 0.05) + uy * w * 0.1, cy + uy * L * (t + 0.05) - ux * w * 0.1)], "#3A1606", 1.6, seed + k, 0.5, 1))
    return "".join(o)


def pudding(D, cx, cy, r, seed, black=True):
    rnd = random.Random(seed)
    if black:
        pal = ("#5A2A2E", "#2A1012", "#0E0406")
        fl = ["#F2E6D8", "#E8D8C0", "#C8A890"]
    else:
        pal = ("#F2E2C4", "#DCC49A", "#9A7A4E")
        fl = ["#8A6A40", "#FFF6E0", "#5A4430"]
    o = [f'<circle cx="{cx + 2}" cy="{cy + 3}" r="{r}" fill="#2A1206" opacity="0.25"/>']
    o.append(painted(D, blob_pts(cx, cy, r, r * 0.95, seed, 0.04, 14), pal, seed, sk=0.12, n=6, inkw=1.4, hi=0.25))
    o.append(ink(smooth_closed(blob_pts(cx, cy, r * 0.9, r * 0.86, seed, 0.04, 14)), "#5A2A10" if black else "#A8783A", 2.2, seed, 1, 0.6))
    for _ in range(int(r * 1.6)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * r * 0.82
        o.append(f'<path d="{blob(cx + math.cos(a) * rr, cy + math.sin(a) * rr, rnd.uniform(0.9, 2.2), rnd.uniform(0.7, 1.4), rnd.randint(0, 999), 0.3, 6, rnd.uniform(0, 180))}" fill="{rnd.choice(fl)}" opacity="{rnd.uniform(0.55, 0.95):.2f}"/>')
    return "".join(o)


def grilled_tomato(D, cx, cy, r, seed):
    rnd = random.Random(seed)
    o = [f'<circle cx="{cx + 2}" cy="{cy + 3}" r="{r}" fill="#3A0A06" opacity="0.25"/>']
    o.append(painted(D, blob_pts(cx, cy, r, r * 0.95, seed, 0.05, 16), ("#FF8A6A", "#D8281A", "#7A0A06"), seed, sk=0.15, n=8, inkw=1.5, hi=0.3))
    for k in range(5):
        a = k * 72 + 20
        px, py = cx + math.cos(math.radians(a)) * r * 0.5, cy + math.sin(math.radians(a)) * r * 0.5
        o.append(f'<path d="{blob(px, py, r * 0.24, r * 0.16, seed + k, 0.15, 8, a)}" fill="#F2A040" opacity="0.8"/>')
        for j in range(3):
            o.append(f'<circle cx="{px + rnd.uniform(-3, 3):.1f}" cy="{py + rnd.uniform(-2, 2):.1f}" r="1.3" fill="#FFF0B0"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.18:.1f}" fill="#F27A5A"/>')
    for k in range(3):
        o.append(taper([(cx - r * 0.7, cy - r * 0.4 + k * r * 0.4), (cx + r * 0.7, cy - r * 0.6 + k * r * 0.4)], 3, 3, "#3A0A04", 0.45))
    return "".join(o)


def mushroom_top(D, cx, cy, r, seed, ang=0):
    o = [painted(D, blob_pts(cx, cy, r, r * 0.8, seed, 0.08, 12, ang), ("#C8945A", "#8A5A30", "#4A2A12"), seed, sk=0.2, n=4, inkw=1.2, hi=0.45)]
    o.append(f'<path d="{blob(cx - r * 0.3, cy - r * 0.25, r * 0.35, r * 0.2, seed + 1, 0.1, 8)}" fill="#FFF2DC" opacity="0.6"/>')
    return "".join(o)


def baked_beans(D, cx, cy, rx, ry, seed):
    rnd = random.Random(seed)
    o = [f'<path d="{blob(cx, cy, rx, ry, seed, 0.15, 14)}" fill="#C8401E"/>']
    for _ in range(int(rx * ry / 9)):
        a, rr = rnd.uniform(0, 6.28), math.sqrt(rnd.random()) * 0.85
        x, y = cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr
        t = rnd.uniform(0, 180)
        o.append(f'<path d="{blob(x, y, 4.2, 2.8, rnd.randint(0, 999), 0.05, 8, t)}" fill="#E8742E" stroke="#8A2A0E" stroke-width="0.8"/>')
        o.append(f'<circle cx="{x - 1:.1f}" cy="{y - 1:.1f}" r="0.9" fill="#FFE0B0" opacity="0.9"/>')
    return "".join(o)


@design("the-full-irish")
def the_full_irish():
    D = Doc2("ie-fi")
    out = [wood_planks(D, 0, 600, 61, ("#B07A4E", "#7A4A28", "#3E220E"), 6, vertical=True)]
    out.append(soft_glow(D, 200, 200, 420, "#FFE6B0", 0.18))
    # linen cloth under the plate
    cl = rot([(80, 236), (540, 216), (560, 640), (100, 650)], 320, 420, -4)
    out.append(cloth(D, poly_pts(cl, 30, 62, 1.2), "#2E6A4A", 62, cell=16, rot_=-4, light=(0.0, 0.0, 1.0, 1.0),
                     folds=[((120, 300), (130, 420), (124, 560))]))
    cx, cy, R = 302, 380, 158
    out.append(plate_top(D, cx, cy, R, 63))
    # knife and fork
    out.append(taper([(96, 264), (96, 330)], 6, 6, "#C8CCD4"))
    for dx in (-6, -2, 2, 6):
        out.append(taper([(96 + dx, 236), (96 + dx * 0.6, 268)], 2.2, 2.6, "#D8DCE4"))
    out.append(taper([(96, 330), (98, 480)], 12, 10, "#E0E4EA") + ink(smooth_open([(96, 334), (98, 478)]), "#6A707A", 1, 64, 1, 0.5))
    out.append(taper([(510, 250), (506, 360)], 16, 10, "#E8ECF2") + taper([(506, 360), (508, 500)], 11, 11, "#3A2A1E"))
    out.append(taper([(514, 256), (511, 350)], 2, 1, "#FFFFFF", 0.9))
    # the fry
    out.append(rasher(D, 230, 296, 1.1, -24, 65))
    out.append(rasher(D, 222, 336, 1.05, -8, 66))
    out.append(fried_egg(D, 352, 290, 44, 67, (-6, -2)))
    out.append(fried_egg(D, 410, 350, 40, 68, (4, 2)))
    out.append(sausage(D, 206, 420, 92, 26, 62, 69))
    out.append(sausage(D, 240, 440, 92, 26, 70, 70))
    out.append(grilled_tomato(D, 410, 432, 30, 71))
    out.append(baked_beans(D, 306, 374, 40, 30, 72))
    for k, (x, y) in enumerate(((296, 482), (338, 492))):
        out.append(pudding(D, x, y, 22, 73 + k, True))
    for k, (x, y) in enumerate(((356, 448), (300, 444))):
        out.append(pudding(D, x, y, 21, 76 + k, False))
    for k, (x, y, a) in enumerate(((258, 384, 10), (272, 400, -20))):
        out.append(mushroom_top(D, x, y, 12, 80 + k, a))
    # a mug of tea, top right
    mx, my = 498, 560
    out.append(cast(D, mx + 8, my + 10, 48, 44, strength=0.45, seed=84))
    out.append(taper(catmull([(mx + 34, my - 14), (mx + 56, my - 6), (mx + 54, my + 18), (mx + 34, my + 20)], 5), 9, 9, "#E8E2D6"))
    out.append(painted(D, ell_pts(mx, my, 40, 40, 0, 360, 30)[:-1], ("#FFFFFF", "#ECE6DA", "#A8A094"), 85, sk=0.12, n=10, inkw=1.6, hi=0.4))
    out.append(f'<circle cx="{mx}" cy="{my}" r="31" fill="#A8703E"/><path d="{blob(mx - 8, my - 10, 12, 5, 86, 0.1, 8, -30)}" fill="#D8A878" opacity="0.8"/>')
    out.append(ink(smooth_closed(ell_pts(mx, my, 31, 31, 0, 360, 30)[:-1]), "#5A3A1A", 1.2, 87, 1, 0.6))
    out.append(steam(mx, my - 26, 36, 88, "#FFFFFF", 2, 16, 4, 0.6))
    # lettering
    out.append(letters(D, 300, 132, "the full Irish", SERIF_IT, 92, "#FFF2D8", ["#FFFFFF", "#F2DCB4", "#FFE8C0"], 89, max_w=470,
                       shadow="#2A1206", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 182, "A PROPER SUNDAY FRY", "#F6D27A", font=JOS, size=22, ls=6, line_w=30, gap=14))
    return finish_ie(D, out, 90)


# ================================================================ 4. sláinte — a snug by the turf fire, the words gilded on the mirror
def pint(D, cx, base, h, seed):
    """A pint of stout in a plain tulip glass: ruby-black body, a creamy head, glass highlights."""
    w = h * 0.42
    top = base - h
    glass = [(cx - w * 0.42, base), (cx - w * 0.46, base - h * 0.3), (cx - w * 0.5, base - h * 0.7), (cx - w * 0.47, top), (cx + w * 0.47, top),
             (cx + w * 0.5, base - h * 0.7), (cx + w * 0.46, base - h * 0.3), (cx + w * 0.42, base)]
    d = smooth_closed(glass)
    o = [cast(D, cx + 6, base, w * 0.65, 6, strength=0.5, seed=seed)]
    body = D.lin([(0, "#3A1408"), (0.5, "#140604"), (1, "#0A0302")], 0, 0, 1, 0)
    o.append(f'<path d="{d}" fill="{body}"/>')
    cid = D.clip(f'<path d="{d}"/>')
    inner = [f'<path d="M {cx - w * 0.5:.1f} {base - h * 0.6:.1f} Q {cx - w * 0.3:.1f} {base - h * 0.3:.1f} {cx - w * 0.4:.1f} {base:.1f} L {cx - w * 0.2:.1f} {base:.1f} Q {cx - w * 0.15:.1f} {base - h * 0.4:.1f} {cx - w * 0.35:.1f} {base - h * 0.7:.1f} Z" fill="#8A2A10" opacity="0.55"/>',
             f'<rect x="{cx - w}" y="{top - 2:.1f}" width="{2 * w:.1f}" height="{h * 0.17:.1f}" fill="#F4E4C4"/>',
             f'<rect x="{cx - w}" y="{top + h * 0.13:.1f}" width="{2 * w:.1f}" height="{h * 0.05:.1f}" fill="#C8A878" opacity="0.8"/>',
             taper([(cx - w * 0.36, top + h * 0.22), (cx - w * 0.4, base - h * 0.3), (cx - w * 0.32, base - 6)], 4, 2, "#FFFFFF", 0.35),
             taper([(cx + w * 0.3, top + h * 0.25), (cx + w * 0.34, base - h * 0.4)], 2, 1, "#FFD8A0", 0.4)]
    inner.append(specks(seed, (cx - w * 0.4, top + h * 0.22, cx + w * 0.4, base - 6), ["#5A2A14"], 10, (0.6, 1.2), (0.4, 0.7)))
    o.append(f'<g {cid}>{"".join(inner)}</g>')
    o.append(f'<path d="{smooth_closed(ell_pts(cx, top, w * 0.47, w * 0.1, 0, 360, 20)[:-1])}" fill="#FFF8E8"/>')
    o.append(ink(d, "#1A0A04", 1.4, seed, 1, 0.6))
    o.append(ink(smooth_closed(ell_pts(cx, top, w * 0.47, w * 0.1, 0, 360, 20)[:-1]), "#B8A080", 1, seed, 1, 0.6))
    return "".join(o)


@design("slainte")
def slainte():
    D = Doc2("ie-sl")
    # mahogany panelling
    out = [wood_planks(D, 0, 600, 101, MAHOG, 7, vertical=True)]
    for k in range(4):
        x = 20 + k * 150
        out.append(f'<path d="{hg.org_rect(x, 262, 120, 130, 102 + k, 0.4, 10, 3)}" fill="none" stroke="#1A0804" stroke-width="5" opacity="0.6"/>')
        out.append(f'<path d="{hg.org_rect(x + 3, 265, 120, 130, 106 + k, 0.4, 10, 3)}" fill="none" stroke="#B87A50" stroke-width="1.6" opacity="0.4"/>')
    out.append(soft_glow(D, 160, 420, 360, "#FF9A40", 0.45))
    # the gilded mirror
    mx0, my0, mx1, my1 = 66, 48, 534, 236
    frame = hg.org_rect(mx0 - 12, my0 - 12, mx1 - mx0 + 24, my1 - my0 + 24, 110, 0.5, 14, 4)
    out.append(f'<path d="{frame}" fill="#2A1206" transform="translate(4 6)" opacity="0.5"/>')
    out.append(painted(D, rect_pts(mx0 - 12, my0 - 12, mx1 + 12, my1 + 12, 20, 111, 0.6), ("#E8B868", "#A8722E", "#5A3410"), 111, sk=0.12, angle=0, n=50, inkw=2, hi=0.45))
    glass = D.lin([(0, "#2E3A3A"), (0.6, "#14201E"), (1, "#0A1210")], 0, 0, 0.3, 1)
    out.append(f'<rect x="{mx0}" y="{my0}" width="{mx1 - mx0}" height="{my1 - my0}" fill="{glass}"/>')
    out.append(D.glow(170, my1 - 10, 140, "#FF8A30", 0.25))
    for k in range(3):
        x = 120 + k * 140
        out.append(f'<path d="M {x} {my0} L {x + 40} {my0} L {x - 40} {my1} L {x - 80} {my1} Z" fill="#FFFFFF" opacity="0.045"/>')
    out.append(f'<rect x="{mx0 + 8}" y="{my0 + 8}" width="{mx1 - mx0 - 16}" height="{my1 - my0 - 16}" fill="none" stroke="#C89A4A" stroke-width="1.4" opacity="0.7"/>')
    for (x, y) in ((mx0 + 18, my0 + 18), (mx1 - 18, my0 + 18), (mx0 + 18, my1 - 18), (mx1 - 18, my1 - 18)):
        out.append(f'<path d="{smooth_closed(heart_d(x, y, 4))}" fill="#E0B050" opacity="0.8"/>' if False else sparkle(x, y, 7, "#E8C070", 0.85))
    gold = D.lin([(0, "#FFF0B0"), (0.45, "#F2C45A"), (0.55, "#C8902A"), (1, "#FFE08A")])
    out.append(letters(D, 300, 168, "Sláinte", DMS, 118, gold, ["#FFF6C8", "#C8902A", "#FFE08A"], 112, max_w=420,
                       shadow="#000000", soff=(0.02, 0.03), angle=-40, wob=0.4, inkc="#5A3A10", inkw=1.2, hi="#FFFFFF"))
    out.append(ruled(300, 212, "TO YOUR HEALTH", "#E8C070", font=CINZEL, size=20, ls=6, line_w=36, gap=12))
    # wall lamp
    out.append(D.glow(500, 300, 90, "#FFD88A", 0.55))
    out.append(taper([(500, 262), (500, 284)], 3, 3, "#B8862E"))
    out.append(painted(D, [(484, 284), (516, 284), (510, 312), (490, 312)], ("#FFF4D0", "#F6D48A", "#C8964A"), 113, sk=0.1, n=4, inkw=1.4, hi=0.5))
    # stone fireplace with the turf fire
    fp = rect_pts(40, 272, 286, 490, 18, 114, 0.6)
    out.append(painted(D, fp, ("#D8D2C4", "#A8A090", "#5A5448"), 114, sdir=(1, 0.3), sk=0.06, angle=-80, n=50, inkw=2, hi=0.2))
    rnd = random.Random(115)
    for j in range(7):
        for i in range(6):
            x = 40 + i * 42 + (j % 2) * 21
            y = 286 + j * 30
            if 76 < x < 250 and y > 318:
                continue
            out.append(f'<path d="{hg.org_rect(x + 2, y, 38, 26, 116 + i * 7 + j, 0.8, 8, 4)}" fill="none" stroke="#6A6458" stroke-width="1.4" opacity="0.55"/>')
    opening = [(76, 490), (76, 350), (100, 326), (226, 326), (250, 350), (250, 490)]
    out.append(f'<path d="{smooth_closed(opening)}" fill="{D.lin([(0, "#0E0604"), (0.7, "#3A1A0A"), (1, "#7A3A14")])}"/>')
    out.append(turf_fire(D, 163, 484, 150, 117))
    out.append(ink(smooth_closed(opening), "#2A1A10", 2, 118, 1, 0.8))
    # mantel shelf with a candle and a little clock
    out.append(painted(D, rect_pts(26, 258, 300, 278, 20, 119, 0.5), MAHOG, 119, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.8, hi=0.45))
    out.append(painted(D, [(214, 258), (214, 222), (226, 210), (244, 210), (256, 222), (256, 258)], MAHOG, 120, sk=0.2, n=6, inkw=1.4, hi=0.4))
    out.append(f'<circle cx="235" cy="232" r="12" fill="#F6EEDC" stroke="#C8902A" stroke-width="2.4"/>')
    out.append(f'<path d="M 235 232 L 235 224 M 235 232 L 241 234" stroke="#2A1A10" stroke-width="1.6" stroke-linecap="round"/>')
    out.append(painted(D, rect_pts(70, 222, 82, 258, 6, 121, 0.2), CREAM, 121, sk=0.12, n=3, inkw=1, hi=0.4))
    out.append(D.glow(76, 214, 40, "#FFD07A", 0.6))
    out.append(f'<path d="{smooth_closed([(76, 202), (80, 212), (76, 220), (72, 212)])}" fill="#FFC040"/>')
    out.append(f'<path d="{blob(76, 260, 16, 4, 122, 0.1, 8)}" fill="#C8902A"/>')
    # hearth and a creel of turf
    out.append(painted(D, rect_pts(30, 488, 300, 506, 20, 123, 0.5), STONE, 123, sdir=(0, 1), sk=0.15, angle=0, n=16, inkw=1.6, hi=0.3))
    out.append(cast(D, 90, 572, 70, 10, strength=0.5, seed=124))
    bk = [(36, 520), (148, 520), (138, 574), (46, 574)]
    for k in range(7):
        out.append(turf_sod(D, 52 + k * 13, 508 + (k % 2) * 4, 18, 34, 125 + k, -10 + k * 4))
    out.append(painted(D, poly_pts(bk, 12, 126, 0.6), ("#D8A86A", "#A87438", "#5A3814"), 126, sk=0.15, angle=0, n=10, inkw=1.6, hi=0.3))
    for k in range(4):
        out.append(pline([(40 + k, 532 + k * 12), (92, 534 + k * 12), (144 - k * 2, 532 + k * 12)], "#5A3814", 1.6, 127 + k, 0.7, 1))
    for k in range(7):
        out.append(pline([(48 + k * 15, 522), (50 + k * 14, 572)], "#7A4A1E", 1.2, 131 + k, 0.5, 1))
    # the table and two pints
    out.append(cast(D, 412, 586, 170, 18, strength=0.5, seed=140))
    tt = ell_pts(410, 520, 168, 40, 0, 360, 36)[:-1]
    out.append(painted(D, shift(tt, 0, 14), ("#7A3A1E", "#4A1E0E", "#200A04"), 141, sk=0, n=10, inkw=1.6, hi=0))
    out.append(painted(D, tt, ("#B86A3A", "#7A3A1E", "#3A1608"), 142, sdir=(0.3, 1), sk=0.12, angle=0, n=40, slen=(30, 80), inkw=1.8, hi=0.35))
    out.append(D.glow(330, 512, 90, "#FF9A40", 0.35))
    for k, (x, y) in enumerate(((364, 520), (452, 526))):
        out.append(f'<path d="{blob(x, y, 32, 9, 143 + k, 0.03, 16)}" fill="#F2E6CC"/>' + ink(blob(x, y, 32, 9, 143 + k, 0.03, 16), "#A8906A", 1, 143, 1, 0.6))
        out.append(f'<path d="{smooth_closed(heart_d(x, y, 3.2))}" fill="none"/>')
        out.append(pint(D, x, y + 2, 128, 145 + k))
    out.append(steam(250, 300, 0, 1, "#FFFFFF", 1, 1, 1, 0))
    return finish_ie(D, out, 150)


# ================================================================ 5. the Cliffs of Moher at sunset
def headland(D, T, tip_base, left_base, rise, seed, haze=0.0, lit=("#F6B07A", "#C8703E", "#5A2418"), land=("#C8D878", "#6E9A42", "#2E5226")):
    """One headland of the cliffs: a sheer face banded with flagstone and shale (lit by the low sun), sea-dark at
    its foot, and the green land above it running back and up toward the left.
    T = top edge points (left -> seaward tip)."""
    hz = (lambda c: mix(c, "#E0A8B8", haze)) if haze else (lambda c: c)
    rnd = random.Random(seed)
    face = T + [tip_base, left_base]
    d = pd(face)
    x0, y0, x1, y1 = bbox(face)
    out = [f'<path d="{d}" fill="{hz(lit[1])}"/>']
    cid = D.clip(f'<path d="{d}"/>')
    inner = []
    # horizontal strata: alternating bands of sandstone and shale following the cliff top
    ytop = max(p[1] for p in T)
    yb = y1
    y = 0.0
    k = 0
    while True:
        bh = rnd.uniform(4, 11) * (0.5 + 0.5 * (1 - haze))
        band = [(x, py + 4 + y) for x, py in T]
        if band[0][1] > yb + 10 and band[-1][1] > yb + 10:
            break
        col = rnd.choice([lit[0], dk(lit[1], 0.25), lit[1], "#7A3A2A", "#E8A070", "#9A5A48"])
        poly = band + [(x, py + bh) for x, py in band[::-1]]
        inner.append(f'<path d="{smooth_closed(jitter(poly, seed + k, 0.8))}" fill="{hz(col)}" opacity="{rnd.uniform(0.35, 0.75):.2f}"/>')
        inner.append(pline([(x, py + bh) for x, py in band], hz(lit[2]), rnd.uniform(0.8, 1.8), seed + k, 0.5, 1))
        y += bh
        k += 1
    inner.append(strokes(D.nid(), d, (x0, y0, x1, y1), [hz(lit[0]), hz(lit[2])], seed, n=int((x1 - x0) * (y1 - y0) / 400) + 6,
                         angle=-2, length=((x1 - x0) * 0.1, (x1 - x0) * 0.4), width=(1, 3), opacity=(0.15, 0.35), curve=0.05))
    for _ in range(int((x1 - x0) / 40) + 1):
        x = rnd.uniform(x0, x1)
        inner.append(taper([(x, y0), (x + rnd.uniform(-3, 3), (y0 + y1) / 2), (x + rnd.uniform(-4, 4), y1)], rnd.uniform(1, 3), rnd.uniform(0.5, 2), hz(lit[2]), rnd.uniform(0.2, 0.4)))
    g = D.lin([(0, "#2A0E1A", 0.5), (0.55, "#2A0E1A", 0.08), (1, "#FFE6B0", 0.3)], x0, 0, x1, 0, "userSpaceOnUse")
    inner.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{g}"/>')
    g2 = D.lin([(0, "#1A0A2A", 0), (0.55, "#1A0A2A", 0.05), (1, "#1A0A2A", 0.55)], 0, y0, 0, y1, "userSpaceOnUse")
    inner.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{g2}"/>')
    inner.append(taper([(tip_base[0] - 3, T[-1][1] + 2), (tip_base[0] - 4, (T[-1][1] + tip_base[1]) / 2), (tip_base[0] - 2, tip_base[1])], 5, 3, hz("#FFE0A8"), 0.5))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(ink(d, hz("#3A1410"), 1.3, seed, 1, 0.45))
    # land above
    tip = T[-1]
    lp = T[::-1] + [(T[0][0] - 10, T[0][1] - rise), (T[0][0] - 40, T[0][1] - rise)] if False else T + [(tip[0] - 24, tip[1] - rise * 0.25), (T[0][0] - 30, T[0][1] - rise)]
    out.append(hill(D, [(px, py - 0.01) for px, py in [lp[-1]] + T], max(p[1] for p in T) + 2, tuple(hz(c) for c in land), seed + 1, inkw=0) if False else "")
    ld = smooth_closed(lp)
    out.append(f'<path d="{ld}" fill="{hz(land[1])}"/>')
    lx0, ly0, lx1, ly1 = bbox(lp)
    g3 = D.lin([(0, hz(land[2]), 0.6), (0.6, hz(land[1]), 0), (1, hz(land[0]), 0.7)], lx0, ly0, lx1, ly1, "userSpaceOnUse")
    out.append(f'<path d="{ld}" fill="{g3}"/>')
    out.append(strokes(D.nid(), ld, (lx0, ly0, lx1, ly1), [hz(land[0]), hz(land[2]), hz("#E8D070")], seed + 2, n=int((lx1 - lx0) * (ly1 - ly0) / 120) + 6,
                       angle=-6, length=(10, 40), width=(1.5, 4), opacity=(0.2, 0.5)))
    out.append(taper(T, 3, 3, hz("#F6E08A"), 0.85))
    out.append(ink(smooth_open(T), hz("#2A3A1A"), 1.0, seed, 1, 0.4))
    return "".join(out)


@design("cliffs-of-moher")
def cliffs_of_moher():
    D = Doc2("ie-cl")
    out = [sky(D, [(0, "#5E6AA8"), (0.32, "#B886A8"), (0.62, "#F2A07A"), (1, "#FFD88A")], 3, 336, ["#FFFFFF", "#F2B89A", "#8A7AB0"], 60, angle=-2, sop=(0.05, 0.14))]
    out.append(soft_glow(D, 450, 318, 240, "#FFE8A0", 0.75))
    out.append(f'<circle cx="450" cy="316" r="24" fill="#FFF2C0"/>')
    rnd = random.Random(201)
    for k in range(9):
        y = rnd.uniform(205, 300)
        x = rnd.uniform(-40, 520)
        L = rnd.uniform(80, 200)
        out.append(taper([(x, y), (x + L * 0.5, y - 2), (x + L, y + 1)], 1, rnd.uniform(4, 9), rnd.choice(["#FFD0A0", "#F29A8A", "#C87A9A"]), 0.7))
    out.append(sea(D, 334, 600, [(0, "#F2B08A"), (0.25, "#B87A8A"), (1, "#2E3E6A")], 202, ["#FFD8A8", "#5A5A8A", "#E8A08A"], n=110))
    for _ in range(150):
        y = rnd.uniform(338, 600)
        spread = 14 + (y - 336) * 0.35
        x = 450 + rnd.gauss(0, spread * 0.45)
        L = rnd.uniform(4, 14) * (0.6 + (y - 336) / 260)
        out.append(f'<path d="M {x - L / 2:.1f} {y:.1f} L {x + L / 2:.1f} {y:.1f}" stroke="{rnd.choice(["#FFF2C0", "#FFD88A", "#FFFFFF"])}" stroke-width="{rnd.uniform(1.2, 2.6):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.5, 0.95):.2f}"/>')
    # headlands receding south, far to near
    specs = [([(300, 332), (370, 331), (412, 333)], (413, 343), (300, 344), 4, 0.78),
             ([(250, 326), (330, 324), (384, 327)], (386, 354), (250, 356), 6, 0.64),
             ([(190, 316), (290, 312), (338, 316)], (341, 378), (190, 382), 10, 0.5),
             ([(110, 300), (220, 296), (282, 304)], (288, 412), (110, 418), 16, 0.32)]
    for k, (T, tb, lb, rise, hz_) in enumerate(specs):
        out.append(headland(D, rough(T, 203 + k, 3, 3), tb, lb, rise, 203 + k, haze=hz_))
        out.append(wave_lines(210 + k, (lb[0] + 40, tb[1] - 3, tb[0] + 8, tb[1] + 3), ["#FFFFFF", "#FFE8D0"], int((tb[0] - lb[0]) / 10), L=(6, 16), w=2, amp=1.5))
    # O'Brien's tower on the second-nearest headland
    tx, tb_ = 232, 297
    out.append(painted(D, rect_pts(tx - 6, tb_ - 20, tx + 6, tb_ + 1, 5, 207, 0.3), ("#F6D8C0", "#B89A8A", "#6A5A5A"), 207, sk=0.2, n=3, inkw=1, hi=0.5))
    for k in range(3):
        out.append(f'<rect x="{tx - 6.5 + k * 4.6:.1f}" y="{tb_ - 24}" width="3" height="4" fill="#B89A8A"/>')
    # Branaunmore sea stack
    out.append(headland(D, [(300, 318), (309, 313), (317, 320)], (322, 414), (296, 416), 2, 205, haze=0.2))
    out.append(wave_lines(206, (288, 412, 330, 418), ["#FFFFFF"], 6, L=(6, 12), w=2, amp=1.5))
    # the near headland
    T4 = rough([(-30, 286), (90, 276), (170, 278), (204, 288)], 208, 5, 3)
    out.append(headland(D, T4, (212, 478), (-30, 484), 30, 208))
    out.append(wave_lines(209, (110, 472, 226, 480), ["#FFFFFF", "#FFE8D0"], 14, L=(8, 22), w=2.4, amp=2))
    # gulls
    for (x, y, sz) in ((350, 230, 9), (372, 246, 7), (300, 214, 6), (520, 262, 8), (160, 330, 7)):
        out.append(seagull(x, y, sz, "#3A2A48", 0.85))
    # foreground clifftop: grass, sea pinks and the flagstone fence along the path
    fg = rough([(-20, 476), (110, 494), (220, 536), (310, 616)], 210, 6, 3)
    out.append(hill(D, fg, 640, ("#C8DC80", "#5E9A3A", "#2A5A22"), 211, inkw=1.6, inkop=0.5, lit="#FFE08A"))
    for k in range(9):
        t = (k + 0.5) / 9
        bx, by = lerp(-6, 262, t), lerp(520, 622, t)
        h = lerp(36, 70, t)
        w = lerp(28, 40, t)
        slab = rect_pts(bx - w / 2, by - h, bx + w / 2, by, 8, 212 + k, 0.8)
        out.append(painted(D, slab, ("#C8C4BC", "#86847E", "#3E3E40"), 212 + k, sdir=(-0.6, 0.4), sk=0.14, angle=-90, n=10, inkw=1.6, hi=0.35))
        out.append(taper([(bx - w * 0.4, by - h * rnd.uniform(0.4, 0.7)), (bx + w * 0.3, by - h * rnd.uniform(0.4, 0.7))], 1.6, 1.2, "#5A5A5A", 0.45))
        out.append(taper([(bx + w / 2 - 2, by - h + 2), (bx + w / 2 - 2, by - 4)], 3, 2, "#FFC8A0", 0.55))
    out.append(grass(213, (0, 520, 290, 600), ["#2A5A22", "#6EA84A", "#A8D070"], n=90, h=(6, 14)))
    for k in range(12):
        x, y = rnd.uniform(10, 120 + (k % 4) * 20), rnd.uniform(494, 516 + k * 2)
        out.append(dab_crown(D, x, y, 7, 5, [("#FFC8E0", "#F27AAE", "#A8306A")], 220 + k, n=8, size=(2, 3.4), inkw=0, base=False))
    out.append(letters(D, 300, 128, "Cliffs of Moher", DMS, 82, "#3A1E4A", ["#5A2E6A", "#22102E", "#6A3A7A"], 214, max_w=470,
                       shadow="#FFD8B8", soff=(0.02, 0.03), angle=-40, wob=0.5))
    out.append(ruled(300, 174, "AILLTE AN MHOTHAIR · CO. CLARE", "#FFF4E0", font=JOS, size=19, ls=4, line_w=22, gap=10, max_w=390))
    return finish_ie(D, out, 215, op=0.8)


# ================================================================ 6. Irish traffic jam — sheep filling the boreen
def little_car(D, cx, base, w, seed, body=RUST):
    """A small hatchback seen from the front, waiting patiently."""
    h = w * 0.62
    o = [f'<ellipse cx="{cx:.1f}" cy="{base:.1f}" rx="{w * 0.6:.1f}" ry="{w * 0.08:.1f}" fill="#1A1A10" opacity="0.35"/>']
    for sg in (-1, 1):
        o.append(f'<rect x="{cx + sg * w * 0.36 - w * 0.08:.1f}" y="{base - h * 0.2:.1f}" width="{w * 0.16:.1f}" height="{h * 0.22:.1f}" rx="2" fill="#1A1A1E"/>')
    bd = [(cx - w * 0.5, base - h * 0.18), (cx - w * 0.5, base - h * 0.5), (cx - w * 0.36, base - h * 0.62), (cx - w * 0.28, base - h), (cx + w * 0.28, base - h), (cx + w * 0.36, base - h * 0.62), (cx + w * 0.5, base - h * 0.5), (cx + w * 0.5, base - h * 0.18)]
    o.append(painted(D, poly_pts(bd, 6, seed, 0.2), body, seed, sk=0.15, n=5, inkw=1, hi=0.4))
    o.append(quad(D, [(cx - w * 0.25, base - h * 0.95), (cx + w * 0.25, base - h * 0.95), (cx + w * 0.32, base - h * 0.64), (cx - w * 0.32, base - h * 0.64)], "#8AB0D0"))
    o.append(quad(D, [(cx - w * 0.2, base - h * 0.93), (cx - w * 0.05, base - h * 0.93), (cx - w * 0.16, base - h * 0.66), (cx - w * 0.28, base - h * 0.66)], "#FFFFFF", 0.4))
    for sg in (-1, 1):
        o.append(f'<circle cx="{cx + sg * w * 0.34:.1f}" cy="{base - h * 0.42:.1f}" r="{w * 0.07:.1f}" fill="#FFF6D0" stroke="#5A5A5A" stroke-width="0.8"/>')
    o.append(f'<rect x="{cx - w * 0.16:.1f}" y="{base - h * 0.45:.1f}" width="{w * 0.32:.1f}" height="{h * 0.1:.1f}" fill="#3A3A40"/>')
    o.append(f'<rect x="{cx - w * 0.44:.1f}" y="{base - h * 0.24:.1f}" width="{w * 0.88:.1f}" height="{h * 0.08:.1f}" fill="#C8CCD4"/>')
    return "".join(o)


@design("irish-traffic-jam")
def irish_traffic_jam():
    D = Doc2("ie-tj")
    out = [sky(D, [(0, "#9CC4E4"), (0.6, "#D8E8EE"), (1, "#F2EEDC")], 3, 340, ["#FFFFFF", "#B8D4E8"], 50, angle=-3, sop=(0.06, 0.14))]
    out.append(puff_cloud(D, 476, 246, 140, 301, ("#FFFFFF", "#F6F4F0", "#B8C4D4")))
    out.append(puff_cloud(D, 100, 256, 110, 302, ("#FFFFFF", "#F6F4F0", "#B8C4D4")))
    # the Twelve Bens-ish mountains, bog and fields
    out.append(hill(D, ridge([(-10, 300), (70, 258), (150, 282), (236, 228), (320, 270), (410, 246), (500, 280), (610, 262)], 303, 8), 360, ("#A8B4CC", "#7A88A8", "#4E5A7A"), 303, inkw=0))
    out.append(hill(D, ridge([(-10, 318), (200, 304), (400, 312), (610, 300)], 304, 4), 380, ("#B4A884", "#8A845A", "#5A5A3A"), 304, inkw=0))
    rnd = random.Random(305)
    bands = [(326, "#9CC062"), (338, "#7EB050"), (356, "#A8C870"), (380, "#6EA84A"), (412, "#8AB858")]
    for k, (y, c) in enumerate(bands):
        line = ridge([(-10, y + 4), (150, y), (300, y + 3), (450, y - 2), (610, y + 2)], 306 + k, 3)
        out.append(hill(D, line, 620, (lt(c, 0.25), c, dk(c, 0.3)), 306 + k, inkw=0, n=40))
        out.append(pline([(x, y_ - 1) for x, y_ in line], "#5A5A50", 1.2 + k * 0.5, 311 + k, 0.65, 1))
        out.append(pline([(x, y_ - 2.5) for x, y_ in line], "#F2F2EA", 0.6 + k * 0.3, 316 + k, 0.5, 1))
        for _ in range(3):
            x = rnd.uniform(20, 580)
            out.append(pline([(x, y + 1), (x + rnd.uniform(-20, 20), y + 18 + k * 8)], "#5A5A50", 1 + k * 0.4, rnd.randint(0, 99), 0.55, 1))
    out.append(cottage_small(D, 440, 344, 50, 24, 330, roof="slate", haze=0.1))
    out.append(cottage_small(D, 92, 336, 36, 17, 331, roof="thatch", haze=0.25))
    # life in the fields: hawthorns, gorse, grazing sheep
    for k, (x, y, r) in enumerate(((40, 372, 16), (566, 362, 14), (150, 352, 9), (520, 400, 20), (64, 420, 22))):
        out.append(taper([(x, y), (x + 2, y - r * 0.6)], 3, 2, "#4A3A2A"))
        out.append(dab_crown(D, x + 3, y - r * 0.9, r, r * 0.7, [("#8ABA5A", "#3E7A32", "#1E4A1E")], 370 + k, n=int(r * 2), size=(2.5, 5), inkw=0.8))
    for k in range(9):
        x, y = rnd.uniform(20, 580), rnd.uniform(332, 420)
        if 180 < x < 420:
            continue
        out.append(dab_crown(D, x, y, rnd.uniform(6, 12), rnd.uniform(3, 5), [("#FFE87A", "#E8C02A", "#A8801A"), ("#7A9A4A", "#4E6A2E", "#2A3A1A")], 380 + k, n=10, size=(1.5, 3), inkw=0, base=False))
    for k in range(10):
        x, y = rnd.uniform(10, 590), rnd.uniform(334, 430)
        if 170 < x < 430:
            continue
        sc = (y - 320) / 600
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{30 * sc:.1f}" ry="{18 * sc:.1f}" fill="#F6F0E0"/><circle cx="{x + 28 * sc:.1f}" cy="{y - 4 * sc:.1f}" r="{7 * sc:.1f}" fill="#2A2422"/>')
    # the boreen winds in from the bottom and away over a rise to the left
    cl = catmull([(300, 640), (330, 520), (300, 440), (250, 390), (236, 362)], 8)
    wid = [max(8, 1.3 * (y - 354)) for x, y in cl]
    L_, R_ = [], []
    for i, (x, y) in enumerate(cl):
        a_ = cl[max(i - 1, 0)]
        b_ = cl[min(i + 1, len(cl) - 1)]
        dx, dy = b_[0] - a_[0], b_[1] - a_[1]
        n_ = math.hypot(dx, dy) or 1
        nx, ny = -dy / n_, dx / n_
        L_.append((x - nx * wid[i] / 2, y - ny * wid[i] / 2 * 0.3))
        R_.append((x + nx * wid[i] / 2, y + ny * wid[i] / 2 * 0.3))
    road = L_ + R_[::-1]
    out.append(painted(D, road, ("#D2C8B0", "#A89C86", "#625A4E"), 332, sdir=(0, 1), sk=0.04, angle=-80, n=70, inkw=0, hi=0.2))
    crown = [(x - w * 0.05, y) for (x, y), w in zip(cl, wid)] + [(x + w * 0.05, y) for (x, y), w in zip(cl[::-1], wid[::-1])]
    out.append(f'<path d="{smooth_closed(crown)}" fill="#7EAE52"/>')
    out.append(f'<path d="{blob(200, 596, 46, 8, 334, 0.2, 12)}" fill="#A8C4DC" opacity="0.85"/><path d="{blob(192, 594, 24, 3, 335, 0.2, 10)}" fill="#FFFFFF" opacity="0.6"/>')
    out.append(specks(336, (120, 440, 480, 600), ["#6A6258", "#E8E0D0"], 60, (0.8, 2.2), (0.4, 0.8)))
    # walls along both edges (far to near), heights follow the road width
    out.append(path_wall(D, [(x - 4, y) for x, y in L_], [w * 0.26 for w in wid], 337))
    # the car stuck behind the flock and the farmer walking them on
    out.append(little_car(D, 238, 374, 20, 338))
    out.append(figures.person(316, 428, 40, "walk", -1, {"hat_kind": "cap", "hat": "#4A4A3A", "top_kind": "jacket", "top": "#4A5A3A", "bottom": "#3A3A44", "form": "m"}, seed=339, light=-1))
    flock = [(250, 392, 0.2, -1), (272, 402, 0.25, 1), (248, 414, 0.3, -1), (300, 432, 0.4, -1), (262, 446, 0.48, 1),
             (348, 470, 0.62, -1), (270, 492, 0.74, 1), (200, 552, 1.0, 1), (402, 560, 1.06, -1), (300, 604, 1.3, -1)]
    marks = ["#2E6AC8", "#D8384A", "#2E6AC8", "#2E6AC8", "#D8384A"]
    for k, (x, y, sc, f) in enumerate(flock):
        out.append(sheep(D, x, y, sc, 340 + k, flip=f, graze=(k == 4), mark=marks[k % len(marks)], haze=max(0, 0.3 - sc * 0.3)))
    out.append(path_wall(D, [(x + 4, y) for x, y in R_], [w * 0.26 for w in wid], 338))
    # foreground: montbretia and ferns at the wall foot, fuchsia on the right
    for k in range(9):
        x = 20 + k * 14 + rnd.uniform(-4, 4)
        y = 600 - k * 6
        for j in range(3):
            ang = -100 + rnd.uniform(-25, 25)
            L = rnd.uniform(40, 70)
            tip = (x + math.cos(math.radians(ang)) * L, y + math.sin(math.radians(ang)) * L)
            out.append(taper([(x, y), ((x + tip[0]) / 2 + 3, (y + tip[1]) / 2), tip], 4, 0.8, rnd.choice(["#3E7A32", "#5E9A3A", "#2A5A22"])))
        fx, fy = x + rnd.uniform(-8, 8), y - rnd.uniform(48, 70)
        for j in range(5):
            out.append(f'<path d="{blob(fx + j * 4, fy - j * 5, 3.6, 2.2, 390 + k * 9 + j, 0.2, 8, -40)}" fill="{["#FF8A2A", "#F26A1A", "#FFA040"][j % 3]}"/>')
        out.append(pline([(fx - 2, fy + 6), (fx + 8, fy - 12), (fx + 20, fy - 22)], "#3E6A2A", 1.4, 400 + k, 0.8, 1))
    out.append(fuchsia_bush(D, 548, 560, 70, 46, 410, nflowers=12))
    out.append(letters(D, 300, 128, "Irish traffic jam", SERIF_IT, 86, "#1E4A2E", ["#2E6A40", "#0E2E1A", "#3E7A4E"], 360, max_w=480,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#9AD0A8"))
    out.append(ruled(300, 176, "RUSH HOUR ON THE BOREEN", "#8A2A1A", font=JOS, size=21, ls=5, line_w=28, gap=12))
    return finish_ie(D, out, 361)


# ================================================================ 7. Connemara — a dapple-grey pony on the bog under the Twelve Bens
def limb(center, widths):
    """Closed outline around a centre polyline with a width at each point (for legs, necks, branches)."""
    n = len(center)
    L, R = [], []
    for i, (x, y) in enumerate(center):
        a_ = center[max(i - 1, 0)]
        b_ = center[min(i + 1, n - 1)]
        dx, dy = b_[0] - a_[0], b_[1] - a_[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = widths[i] / 2
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return L + R[::-1]


def pony(D, x, base, s, seed, flip=1, coat=("#F6F4F0", "#C4C4C6", "#72727A"), mane=("#9A9AA4", "#4A4A54", "#1E1E26")):
    """A Connemara pony side-on (facing right before flip), withers 100 units high: compact deep body, strong
    crested neck, neat head, dapple-grey coat with darker legs, a dark mane and tail lifting in the wind."""
    rnd = random.Random(seed)
    o = [f'<ellipse cx="-2" cy="1.5" rx="72" ry="6" fill="#1A1A10" opacity="0.3"/>']
    far = tuple(dk(c, 0.2) for c in coat)
    legc = ("#9A9AA2", "#6A6A74", "#3A3A44")
    # tail (behind the quarters), blowing back
    for k in range(7):
        off = (k - 3) * 1.8
        tl = catmull([(-52, -90), (-64, -84 + off), (-72, -64 + off), (-74, -40 + off * 0.6), (-84, -18 + off)], 6)
        o.append(taper(tl, 7 - k * 0.5, 1.4, [mane[1], mane[2], mane[0], mane[1], mane[2], mane[0], mane[1]][k], 0.92))
    # far legs: front stepping forward, hind under the body
    for ctr, ws in (([(44, -52), (48, -38), (52, -26), (55, -12), (58, -4), (60, 0)], (15, 12, 8.5, 7.4, 8.5, 9.5)),
                    ([(-30, -56), (-38, -40), (-42, -28), (-38, -12), (-35, -4), (-33, 0)], (21, 15, 10, 7.4, 8.5, 9.5))):
        o.append(painted(D, limb(ctr, ws), (far[0], far[1], legc[2]), seed + int(ctr[0][0]), sdir=(0.6, 0.3), sk=0.15, angle=-90, n=6, inkw=0.9, inkop=0.5, hi=0.2))
        o.append(f'<path d="{smooth_closed([(ctr[-1][0] - 5, 0.5), (ctr[-1][0] - 4, -4.5), (ctr[-1][0] + 4, -4.5), (ctr[-1][0] + 6, 0.5)])}" fill="#2A2424"/>')
    # neck and body
    neck = [(26, -98), (44, -114), (64, -134), (76, -142), (82, -134), (80, -118), (70, -96), (58, -66), (40, -64), (24, -80)]
    body = [(58, -66), (54, -52), (40, -46), (10, -43), (-24, -45), (-40, -52), (-54, -64), (-58, -78), (-52, -92), (-38, -99), (-20, -96), (0, -93), (26, -99), (48, -92), (60, -78)]
    o.append(painted(D, body, coat, seed, sdir=(0.3, 1), sk=0.14, angle=-10, n=46, slen=(8, 26), sw=(1, 3), inkw=1.3, inkop=0.6, hi=0.4))
    o.append(painted(D, neck, coat, seed + 1, sdir=(0.4, 1), sk=0.12, angle=-55, n=22, slen=(6, 18), sw=(1, 2.6), inkw=1.2, inkop=0.6, hi=0.4))
    head = [(72, -144), (80, -146), (88, -136), (98, -116), (106, -100), (106, -92), (98, -88), (90, -94), (80, -108), (72, -124)]
    o.append(painted(D, head, coat, seed + 2, sdir=(0.5, 0.8), sk=0.12, angle=-60, n=12, slen=(5, 14), sw=(1, 2.2), inkw=1.2, inkop=0.6, hi=0.45))
    # subtle dapples
    cid = D.clip(f'<path d="{smooth_closed(body)}"/><path d="{smooth_closed(neck)}"/>')
    dap = []
    for _ in range(46):
        px, py = rnd.uniform(-56, 56), rnd.uniform(-98, -48)
        r = rnd.uniform(2.2, 4.2)
        dap.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r + 1.2:.1f}" fill="{coat[2]}" opacity="0.12"/><circle cx="{px:.1f}" cy="{py:.1f}" r="{r * 0.8:.1f}" fill="{coat[0]}" opacity="0.4"/>')
    dap.append(shade_over(D, smooth_closed(body), "#1A1A2A", 0.5, 0, 0, 0, 1, 0.45))
    dap.append(f'<path d="{blob(40, -60, 18, 14, seed + 9, 0.2, 10)}" fill="#3A3A4A" opacity="0.18"/>')
    o.append(f'<g {cid}>{"".join(dap)}</g>')
    # near legs: forearm, knee, slender cannon, fetlock, pastern and hoof; darkening toward the ground
    for ctr, ws in (([(46, -62), (42, -44), (40, -30), (40, -26), (40, -12), (42, -6), (45, 0)], (19, 14, 10.5, 10, 7.6, 9, 9.5)),
                    ([(-38, -66), (-44, -48), (-50, -32), (-50, -27), (-46, -12), (-44, -6), (-42, 0)], (30, 20, 11, 9.6, 7.6, 9, 9.5))):
        lp = limb(ctr, ws)
        o.append(painted(D, lp, coat, seed + int(ctr[0][0]) + 50, sdir=(0.6, 0.3), sk=0.16, angle=-90, n=8, inkw=1.0, inkop=0.55, hi=0.35))
        lcid = D.clip(f'<path d="{smooth_closed(lp)}"/>')
        g = D.lin([(0, legc[1], 0), (0.45, legc[1], 0.15), (0.8, legc[1], 0.85), (1, legc[2], 0.9)], 0, -64, 0, 0, "userSpaceOnUse")
        o.append(f'<g {lcid}><rect x="{ctr[-1][0] - 20}" y="-66" width="40" height="66" fill="{g}"/></g>')
        o.append(f'<path d="{smooth_closed([(ctr[-1][0] - 5, 0.5), (ctr[-1][0] - 4, -5), (ctr[-1][0] + 4, -5), (ctr[-1][0] + 6.5, 0.5)])}" fill="#2A2424"/>')
    o.append(f'<path d="{blob(-46, -28, 3.5, 3, seed + 7, 0.1, 8)}" fill="{coat[0]}" opacity="0.6"/>')
    # face
    o.append(f'<path d="{blob(84, -126, 3.2, 2.6, seed + 3, 0.05, 10, 30)}" fill="#1A1210"/><circle cx="83.2" cy="-127" r="0.9" fill="#FFFFFF"/>')
    o.append(pline([(80, -130), (85, -131), (89, -127)], "#3A3434", 1.1, seed, 0.7, 1))
    o.append(painted(D, [(98, -104), (106, -98), (106, -91), (98, -88), (93, -94)], ("#9A98A0", "#6E6C74", "#3E3C44"), seed + 5, sk=0.1, n=2, inkw=0, hi=0.3))
    o.append(f'<path d="{blob(102, -98, 2.2, 1.4, seed + 4, 0.1, 8, 50)}" fill="#2A2424"/>')
    o.append(pline([(106, -92), (100, -90)], "#2A2424", 1, seed, 0.6, 1))
    o.append(pline([(74, -120), (82, -112), (90, -102)], "#8A8A92", 1, seed, 0.4, 1))
    for ex in ((72, -144), (77, -146)):
        o.append(f'<path d="M {ex[0] - 3} {ex[1] + 2} L {ex[0] - 1} {ex[1] - 12} L {ex[0] + 4} {ex[1] + 2} Z" fill="{coat[1]}" stroke="#4A4A54" stroke-width="0.9"/>')
    # mane over the crest and forelock, lifting back in the wind
    for k in range(18):
        t = k / 17
        mx, my = lerp(24, 74, t) + rnd.uniform(-1, 1), lerp(-100, -146, t) + rnd.uniform(-1, 1)
        L = rnd.uniform(10, 22)
        o.append(taper([(mx, my), (mx - L * 0.5, my + 2 + L * 0.15), (mx - L, my + L * 0.45)], 5, 1.2, rnd.choice(mane), 0.92))
    for k in range(4):
        o.append(taper([(76 + k, -146), (80 + k * 2, -138), (82 + k * 3, -130)], 3, 0.8, rnd.choice(mane), 0.9))
    return f'<g transform="translate({x:.1f} {base:.1f}) scale({s * flip:.3f} {s:.3f})">' + "".join(o) + "</g>"


def heather_clump(D, x, y, w, seed):
    rnd = random.Random(seed)
    o = [dab_crown(D, x, y - w * 0.25, w, w * 0.4, [("#7A8A4A", "#4E5A2E", "#2A321A")], seed, n=int(w * 1.2), size=(1.6, 3.2), inkw=0, base=False)]
    o.append(dab_crown(D, x, y - w * 0.4, w * 0.9, w * 0.32, [("#E8B0E0", "#B470B8", "#7A3A86"), ("#F2C8EC", "#C888C8", "#8A4A90")], seed + 1, n=int(w * 1.6), size=(1.2, 2.6), inkw=0, base=False))
    return "".join(o)


def heather(D, x, y, h, seed, cols=("#E8A8E0", "#B86AB8", "#7A3A8A")):
    rnd = random.Random(seed)
    o = []
    for k in range(5):
        a = -90 + rnd.uniform(-30, 30)
        L = h * rnd.uniform(0.6, 1)
        tip = (x + math.cos(math.radians(a)) * L, y + math.sin(math.radians(a)) * L)
        o.append(pline([(x, y), tip], "#5A4A3A", 1.2, seed + k, 0.8, 1))
        for j in range(6):
            t = 0.4 + j * 0.1
            px, py = lerp(x, tip[0], t), lerp(y, tip[1], t)
            o.append(f'<circle cx="{px + rnd.uniform(-2, 2):.1f}" cy="{py:.1f}" r="{rnd.uniform(1.4, 2.4):.1f}" fill="{rnd.choice(cols)}"/>')
    return "".join(o)


def bog_cotton(x, y, h, seed):
    rnd = random.Random(seed)
    o = [pline([(x, y), (x + rnd.uniform(-3, 3), y - h)], "#6A7A4A", 1.2, seed, 0.9, 1)]
    cx, cy = x + rnd.uniform(-3, 3), y - h
    for k in range(9):
        a = rnd.uniform(0, 6.28)
        o.append(f'<circle cx="{cx + math.cos(a) * 3:.1f}" cy="{cy - 3 + math.sin(a) * 3:.1f}" r="{rnd.uniform(2, 3.2):.1f}" fill="#FFFFFF" opacity="0.9"/>')
    return "".join(o)


@design("connemara")
def connemara():
    D = Doc2("ie-cn")
    out = [sky(D, [(0, "#4E6488"), (0.35, "#8EA2BC"), (0.7, "#D8DCD8"), (1, "#F2E6CC")], 3, 360, ["#FFFFFF", "#6A80A0", "#E8DCC8"], 70, angle=-4, sop=(0.06, 0.16))]
    out.append(soft_glow(D, 470, 230, 200, "#FFF2D0", 0.5))
    out.append(puff_cloud(D, 486, 262, 170, 501, ("#FFFFFF", "#E8ECF2", "#8A98B0"), rows=2))
    out.append(puff_cloud(D, 96, 266, 130, 502, ("#F2F4F8", "#D8DEE8", "#7A88A0"), rows=2))
    # the Twelve Bens: quartzite peaks, pale and bluish
    bens = ridge([(-10, 330), (40, 296), (90, 262), (130, 284), (170, 244), (220, 276), (262, 236), (310, 270), (350, 252), (400, 286), (450, 260), (520, 300), (610, 290)], 503, 6)
    out.append(hill(D, bens, 400, ("#C8D0DE", "#8E9AB4", "#5A6684"), 503, inkw=1, inkop=0.3, lit="#FFFFFF"))
    rnd = random.Random(504)
    for _ in range(10):
        x = rnd.uniform(40, 520)
        out.append(taper([(x, 286 + rnd.uniform(-6, 14)), (x + rnd.uniform(-6, 6), 318)], rnd.uniform(1, 2), rnd.uniform(2, 4), "#E8ECF4", 0.2))
    out.append(hill(D, ridge([(-10, 336), (160, 326), (330, 334), (470, 324), (610, 332)], 505, 3), 400, ("#9AA484", "#6E7A5A", "#46523A"), 505, inkw=0))
    # lough reflecting the sky
    lake = [(-10, 342), (610, 340), (610, 372), (-10, 376)]
    out.append(quad(D, lake, "#A8B8CC"))
    out.append(wave_lines(506, (0, 344, 600, 372), ["#FFFFFF", "#7A8AA8", "#E8ECF0"], 40, L=(20, 60), w=1.6, amp=1))
    # bog: browns, ochres and heather
    out.append(hill(D, ridge([(-10, 368), (180, 362), (400, 370), (610, 360)], 507, 4), 640, ("#B8A86A", "#8A7A44", "#4E4428"), 507, inkw=1, inkop=0.3))
    for k in range(6):
        y = 390 + k * 34
        out.append(strokes(D.nid(), f"M -10 {y} L 610 {y} L 610 {y + 30} L -10 {y + 30} Z", (-40, y, 610, y + 30), ["#7A8A3A", "#A88A4A", "#5A4A2A", "#8A6A9A"], 508 + k, n=50, angle=-2, length=(20, 70), width=(2, 6), opacity=(0.2, 0.5)))
    for k in range(5):
        x, y = rnd.uniform(20, 580), rnd.uniform(390, 470)
        out.append(f'<path d="{blob(x, y, rnd.uniform(16, 30), 4, 510 + k, 0.2, 10)}" fill="#B8C8D8" opacity="0.8"/>')
    for k in range(4):
        x, y = rnd.uniform(40, 560), rnd.uniform(410, 520)
        out.append(stone(D, x, y, rnd.uniform(14, 26), rnd.uniform(9, 14), 520 + k))
    for k in range(26):
        x, y = rnd.uniform(0, 600), rnd.uniform(390, 600)
        out.append(heather_clump(D, x, y, rnd.uniform(10, 24) * (0.6 + (y - 390) / 300), 530 + k))
    out.append(pony(D, 300, 534, 2.05, 540, flip=-1))
    for k in range(11):
        x, y = rnd.uniform(10, 590), rnd.uniform(528, 600)
        out.append(bog_cotton(x, y, rnd.uniform(18, 34), 560 + k))
    out.append(grass(580, (0, 530, 600, 600), ["#6A7A3A", "#9AAA5A", "#4A5A2A", "#B8A060"], n=120, h=(8, 20)))
    out.append(letters(D, 300, 128, "Connemara", SERIF_IT, 104, "#FFFAF0", ["#FFFFFF", "#E8ECF2", "#F2EAD8"], 590, max_w=440,
                       shadow="#2A3450", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 176, "PONY OF THE WILD WEST", "#FFF4D8", font=JOS, size=21, ls=6, line_w=30, gap=12))
    return finish_ie(D, out, 591)


# ================================================================ 8. puifín — a puffin on the Skelligs, a natural-history plate
def puffin(D, x, base, s, seed, flip=1, eels=True):
    """Atlantic puffin standing (facing right): plump black back and cap, white front, pale grey face,
    the striped parrot beak full of silver sand eels, bright orange feet."""
    rnd = random.Random(seed)
    o = [f'<ellipse cx="0" cy="1" rx="28" ry="3.5" fill="#1A2010" opacity="0.3"/>']
    blackp = ("#4A4A56", "#1E1E26", "#08080C")
    for fx in (-9, 7):
        foot = [(fx - 10, 0), (fx + 11, 0), (fx + 7, -3), (fx + 2, -11), (fx - 2, -11), (fx - 7, -3)]
        o.append(painted(D, foot, ("#FFB070", "#F2641A", "#A8360A"), seed + fx, sk=0.1, n=2, inkw=0.9, hi=0.4))
        for t in (-4, 2):
            o.append(pline([(fx + t * 0.4, -9), (fx + t * 1.6, -1)], "#B8460A", 0.8, seed, 0.7, 1))
    body = [(-22, -9), (-31, -34), (-29, -60), (-20, -78), (-2, -86), (16, -80), (27, -60), (29, -34), (21, -13), (6, -4), (-10, -3)]
    o.append(taper([(-26, -16), (-38, -8)], 9, 2, blackp[1]))
    o.append(painted(D, body, blackp, seed, sdir=(0.4, 0.8), sk=0.12, angle=-80, n=16, inkw=1.4, hi=0.35))
    front = [(8, -80), (22, -66), (28, -44), (24, -18), (12, -6), (0, -6), (-4, -30), (-2, -58)]
    o.append(painted(D, front, ("#FFFFFF", "#F2EEE8", "#B8B4B0"), seed + 1, sdir=(0.8, 0.4), sk=0.14, angle=-90, n=10, inkw=0, hi=0.3))
    wing = [(-26, -58), (-8, -64), (-2, -40), (-8, -16), (-18, -12), (-27, -30)]
    o.append(painted(D, wing, ("#3E3E4A", "#16161E", "#04040A"), seed + 2, sk=0.1, angle=-80, n=8, inkw=1, hi=0.3))
    for k in range(3):
        o.append(taper([(-20 + k * 5, -50 + k * 3), (-14 + k * 4, -20 + k * 2)], 1.4, 0.6, "#5A5A6A", 0.6))
    hd = blob_pts(6, -98, 21, 20, seed + 3, 0.04, 14)
    o.append(painted(D, hd, blackp, seed + 3, sk=0.1, n=4, inkw=1.3, hi=0.3))
    face = blob_pts(12, -95, 14.5, 13.5, seed + 4, 0.06, 12)
    o.append(painted(D, face, ("#FFFFFF", "#E8E6E4", "#A8A6A8"), seed + 4, sdir=(-0.5, 0.5), sk=0.18, n=4, inkw=0, hi=0.3))
    o.append(f'<path d="M 9 -107 L 12.5 -101 L 16 -107 Z" fill="#6A6A78"/><path d="M 12.5 -98 L 10 -91 L 16 -94 Z" fill="#6A6A78"/>')
    o.append(f'<circle cx="12.5" cy="-100.5" r="3.4" fill="#E0281E"/><circle cx="12.5" cy="-100.5" r="2.3" fill="#100808"/><circle cx="11.8" cy="-101.3" r="0.7" fill="#FFFFFF"/>')
    o.append(pline([(4, -88), (12, -84), (22, -86)], "#9A9AA4", 1, seed, 0.6, 1))
    beak = [(23, -111), (31, -109), (45, -99), (47, -95), (32, -85), (23, -86)]
    o.append(painted(D, beak, ("#FF9A5A", "#E8501E", "#9A2A0A"), seed + 5, sk=0.12, n=4, inkw=1.1, hi=0.4))
    o.append(f'<path d="{smooth_closed([(23, -111), (28, -110), (28, -86), (23, -86)])}" fill="#5A6A80"/>')
    o.append(f'<path d="{smooth_closed([(28, -110), (32, -109), (32, -85), (28, -86)])}" fill="#F6C83A"/>')
    for k in range(2):
        o.append(pline([(36 + k * 4, -105 + k * 2), (36 + k * 4, -90)], "#FFD8A0", 1.1, seed + k, 0.8, 1))
    o.append(pline([(31, -96), (40, -96), (47, -95)], "#5A1A0A", 1, seed, 0.8, 1))
    o.append(f'<path d="M 20 -98 l 3 0" stroke="#E8701E" stroke-width="2.6" stroke-linecap="round"/>')
    if eels:
        # sand eels held crosswise in the bill, both ends drooping
        for k, (lx, rx_, sag, dy) in enumerate(((12, 56, 20, 0), (16, 60, 26, 2), (10, 52, 28, 4))):
            mid = (36, -96 + dy * 0.4)
            left = catmull([mid, (lx + 12, -97 + dy * 0.6), (lx + 3, -92 + sag * 0.5 + dy), (lx, -96 + sag + dy)], 5)
            right = catmull([mid, (rx_ - 12, -97 + dy * 0.6), (rx_ - 3, -92 + sag * 0.5 + dy), (rx_, -96 + sag + dy)], 5)
            for half in (left, right):
                o.append(taper([(px + 0.4, py + 0.6) for px, py in half], 3.0, 0.8, "#4A6A78"))
                o.append(taper(half, 2.4, 0.6, "#D2DEE4"))
                o.append(taper([(px, py - 0.6) for px, py in half], 0.8, 0.3, "#FFFFFF", 0.9))
        o.append(painted(D, [(23, -111), (31, -109), (45, -99), (47, -95), (40, -95), (31, -100), (23, -100)], ("#FF9A5A", "#E8501E", "#9A2A0A"), seed + 6, sk=0.1, n=2, inkw=0.9, hi=0.4))
        o.append(f'<path d="{smooth_closed([(23, -111), (28, -110), (28, -100), (23, -100)])}" fill="#5A6A80"/><path d="{smooth_closed([(28, -110), (32, -109), (32, -100), (28, -100)])}" fill="#F6C83A"/>')
    return f'<g transform="translate({x:.1f} {base:.1f}) scale({s * flip:.3f} {s:.3f})">' + "".join(o) + "</g>"


def thrift(D, x, y, seed, n=5, h=26):
    """Sea pinks: a cushion of grassy leaves with round pink pom-pom flowers on wiry stems."""
    rnd = random.Random(seed)
    o = [f'<path d="{blob(x, y - 3, 16, 6, seed, 0.2, 10)}" fill="#5E8A3E"/>']
    o.append(grass(seed, (x - 14, y - 2, x + 14, y + 2), ["#4E7A32", "#7AAA4E"], n=20, h=(5, 10), w=1))
    for k in range(n):
        tx, ty = x + rnd.uniform(-14, 14), y - rnd.uniform(h * 0.7, h)
        o.append(pline([(x + rnd.uniform(-6, 6), y - 4), (tx, ty)], "#6A7A3A", 1.1, seed + k, 0.9, 1))
        o.append(dab_crown(D, tx, ty, 5.5, 5, [("#FFD0E4", "#F28AB8", "#B04878")], seed + k, n=10, size=(1.6, 2.6), inkw=0.6, base=True))
    return "".join(o)


@design("puffin")
def puffin_d():
    D = Doc2("ie-pf")
    out = [paper(D.nid(), "#F6EFDC", FLECK, 601)]
    out.append(blooms(602, ["#C8D8D0", "#E8D8B8"], 6, (60, 60, 540, 540), (100, 180), (0.06, 0.1)))
    # plate border
    out.append(f'<rect x="48" y="48" width="504" height="504" fill="none" stroke="#2E4A5A" stroke-width="2.4"/>')
    out.append(f'<rect x="56" y="56" width="488" height="488" fill="none" stroke="#2E4A5A" stroke-width="1"/>')
    for (x, y) in ((48, 48), (552, 48), (48, 552), (552, 552)):
        out.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#C8643C"/>')
    out.append(ruled(300, 92, "ÉIN NA hÉIREANN · Nº 4", "#2E4A5A", font=MONO, size=17, ls=3, line_w=40, gap=12))
    # oval vignette: the Skelligs at dawn
    cx, cy, rx, ry = 300, 252, 196, 146
    vd = smooth_closed(ell_pts(cx, cy, rx, ry, 0, 360, 48)[:-1])
    cid = D.clip(f'<path d="{vd}"/>')
    v = [sky(D, [(0, "#B8D4E4"), (0.6, "#F2E2D0"), (1, "#F8D8B8")], 3, 600, ["#FFFFFF", "#D8E4EC"], 40, sop=(0.05, 0.12))]
    v.append(puff_cloud(D, 200, 180, 100, 603, ("#FFFFFF", "#FFF6F0", "#D8C8D0")))
    v.append(sea(D, 300, 440, [(0, "#7AA8C0"), (1, "#2E5E7A")], 604, ["#FFFFFF", "#1E4A6A", "#A8D0E0"], n=60))
    # Skellig Michael: a jagged twin-peaked pyramid; Little Skellig to the left, white with gannets
    sm = ridge([(330, 302), (360, 230), (388, 178), (404, 206), (426, 168), (446, 220), (480, 302)], 605, 5)
    v.append(hill(D, sm, 305, ("#9AA0B0", "#6A7084", "#3A3E52"), 605, inkw=1.2, inkop=0.5, lit="#F8E0C8"))
    v.append(f'<path d="M 382 196 L 386 196" stroke="#F2EEE8" stroke-width="3"/>')
    ls = ridge([(150, 302), (176, 262), (196, 240), (214, 268), (236, 302)], 606, 3)
    v.append(hill(D, ls, 305, ("#D8DCE0", "#A8AEB8", "#6A7080"), 606, inkw=1, inkop=0.4))
    v.append(specks(607, (170, 248, 226, 300), ["#FFFFFF"], 40, (1, 1.8), (0.7, 1)))
    v.append(wave_lines(608, (140, 300, 490, 310), ["#FFFFFF"], 20, L=(8, 20), w=1.8, amp=1.5))
    for (bx, by, bs) in ((260, 200, 7), (290, 214, 5), (470, 150, 6)):
        v.append(seagull(bx, by, bs, "#3A4050", 0.8))
    out.append(f'<g {cid}>{"".join(v)}</g>')
    out.append(ink(vd, "#2E4A5A", 2.2, 609, 2, 0.8))
    # clifftop tuft in front, with sea pinks
    tuft = [(96, 440), (140, 394), (230, 380), (330, 376), (430, 384), (510, 412), (514, 448), (90, 456)]
    out.append(painted(D, tuft, ("#A8CC78", "#5E9A3E", "#2A5A22"), 610, sdir=(0.3, 1), sk=0.15, angle=-80, n=60, slen=(8, 20), sw=(1, 2.4), inkw=1.6, hi=0.35))
    out.append(grass(611, (110, 372, 500, 404), ["#4E7A32", "#7AAA4E", "#A8D070"], n=90, h=(6, 16)))
    for k, (x, y) in enumerate(((128, 424), (170, 402), (452, 406), (494, 430), (402, 392))):
        out.append(thrift(D, x, y, 612 + k))
    out.append(puffin(D, 296, 408, 2.55, 620, eels=False))
    # name
    out.append(letters(D, 300, 500, "Puifín", SERIF_IT, 64, "#1E3A4A", ["#2E5A6A", "#0E2230"], 621, max_w=300, wob=0.5))
    out.append(label(300, 530, "FRATERCULA ARCTICA · THE PUFFIN", MONO, 15, "#8A4A2A", ls=2, max_w=400))
    return finish_ie(D, out, 622)



# ================================================================ 9. spideog — a robin on the winter hawthorn
def robin_ie(D, x, base, s, seed, flip=1):
    """European robin, plump and round, perched (facing right before flip): orange-red face and breast edged in
    blue-grey, olive-brown back, buff-edged wing, white belly, big dark eye. (x, base) = toes on the perch."""
    rnd = random.Random(seed)
    o = []
    brown = ("#C8AA7C", "#8E6E48", "#4A341E")
    orange = ("#FFC890", "#F07434", "#A8400E")
    for lx in (-4, 8):
        o.append(taper([(lx, -16), (lx + 1, -6), (lx + 1, 0)], 2.6, 2.2, "#7A5A44"))
        o.append(f'<path d="M {lx - 6} 1 Q {lx} -3 {lx + 7} 1" stroke="#7A5A44" stroke-width="2" fill="none" stroke-linecap="round"/>')
    tail = [(-28, -38), (-52, -62), (-60, -58), (-56, -46), (-30, -24)]
    o.append(painted(D, tail, brown, seed, sk=0.15, angle=-135, n=6, inkw=1.2, hi=0.3))
    for k in range(3):
        o.append(pline([(-32, -32 + k * 2), (-54 + k * 2, -56 + k * 3)], brown[2], 0.9, seed + k, 0.5, 1))
    body = blob_pts(0, -42, 36, 32, seed, 0.03, 20, -10)
    o.append(painted(D, body, brown, seed + 1, sdir=(0.5, 0.8), sk=0.15, angle=-20, n=26, slen=(5, 14), sw=(1, 2.2), inkw=1.5, hi=0.35))
    head = blob_pts(20, -74, 21, 20, seed + 2, 0.04, 16)
    o.append(painted(D, head, brown, seed + 2, sk=0.15, angle=-20, n=10, inkw=1.4, hi=0.35))
    o.append(painted(D, [(-12, -32), (12, -32), (26, -22), (20, -12), (0, -10), (-16, -16)], ("#FFFFFF", "#F4EEE4", "#C8BCAC"), seed + 3, sk=0.1, n=4, inkw=0, hi=0.3))
    grey = [(26, -94), (36, -94), (46, -80), (44, -58), (34, -36), (18, -22), (6, -26), (10, -46), (14, -66), (18, -84)]
    o.append(f'<path d="{smooth_closed(shift(grey, -4, -1))}" fill="#A8B2C0"/>')
    breast = [(30, -95), (42, -92), (48, -80), (46, -60), (38, -40), (24, -24), (12, -26), (14, -44), (18, -62), (20, -80)]
    bd = smooth_closed(breast)
    o.append(painted(D, breast, orange, seed + 4, sdir=(-0.2, 0.9), sk=0.12, angle=-70, n=24, slen=(4, 10), sw=(0.8, 1.8), inkw=0, hi=0.0))
    cid = D.clip(f'<path d="{bd}"/>')
    g = D.lin([(0, "#FFE0B0", 0.65), (0.45, orange[1], 0), (1, "#8A2A0A", 0.5)], 0, -95, 0, -24, "userSpaceOnUse")
    feath = [f'<rect x="0" y="-100" width="60" height="80" fill="{g}"/>']
    for k in range(18):
        px, py = rnd.uniform(16, 46), rnd.uniform(-88, -30)
        feath.append(f'<path d="M {px - 3:.1f} {py:.1f} q 3 3 6 0" stroke="#C8501A" stroke-width="0.9" fill="none" opacity="0.6"/>')
    o.append(f'<g {cid}>{"".join(feath)}</g>')
    wing = [(-28, -48), (-6, -60), (10, -50), (6, -32), (-12, -24), (-30, -32)]
    o.append(painted(D, wing, ("#B8966A", "#7A5C3C", "#3E2C16"), seed + 5, sk=0.15, angle=-10, n=10, inkw=1.2, hi=0.3))
    for k in range(4):
        o.append(taper([(-24 + k * 7, -46 + k * 2), (-14 + k * 7, -30 + k)], 2, 0.8, "#E8D4A8", 0.75))
    o.append(f'<circle cx="28" cy="-80" r="5.2" fill="#140C08"/><circle cx="26.6" cy="-81.8" r="1.7" fill="#FFFFFF"/>')
    o.append(f'<path d="{smooth_closed([(44, -82), (56, -79), (44, -76)])}" fill="#3A2A1E"/>')
    o.append(pline([(-20, -66), (2, -74), (14, -86)], "#E8D8B8", 1.2, seed, 0.4, 1))
    return f'<g transform="translate({x:.1f} {base:.1f}) scale({s * flip:.3f} {s:.3f})">' + "".join(o) + "</g>"


def haw_cluster(D, x, y, seed, n=5, r=6.5):
    rnd = random.Random(seed)
    o = []
    for k in range(n):
        a = rnd.uniform(0, 6.28)
        bx, by = x + math.cos(a) * r * 1.3 * (k > 0), y + abs(math.sin(a)) * r * 1.1 * (k > 0) + 4
        o.append(pline([(x, y - 6), (bx, by - r * 0.6)], "#6A3A22", 1, seed + k, 0.8, 1))
        o.append(painted(D, blob_pts(bx, by, r * 0.85, r, seed + k, 0.05, 10), ("#FF8A6A", "#D2281E", "#7A0A0A"), seed + k, sdir=(0.6, 0.7), sk=0.25, n=3, inkw=0.9, hi=0.45))
        o.append(f'<circle cx="{bx:.1f}" cy="{by + r * 0.85:.1f}" r="1.4" fill="#3A1008"/>')
        o.append(f'<circle cx="{bx - r * 0.3:.1f}" cy="{by - r * 0.35:.1f}" r="{r * 0.22:.1f}" fill="#FFFFFF" opacity="0.75"/>')
    return "".join(o)


def haw_leaf(D, x, y, L, ang, seed, pal=("#E8C060", "#B8862A", "#6A4A14")):
    """A small lobed hawthorn leaf turning gold."""
    pts = []
    for i in range(15):
        t = i / 14
        w = L * 0.36 * math.sin(math.pi * t) ** 0.7 * (1 + 0.28 * math.sin(t * math.pi * 5))
        pts.append((t * L, -w))
    pts += [(t * L, w) for t, w in [(p[0] / L, -p[1] * 0.9) for p in pts[::-1]][1:-1]]
    pts = [(x + px * math.cos(math.radians(ang)) - py * math.sin(math.radians(ang)), y + px * math.sin(math.radians(ang)) + py * math.cos(math.radians(ang))) for px, py in pts]
    return painted(D, pts, pal, seed, sk=0.15, angle=ang, n=4, inkw=0.9, hi=0.35)


@design("spideog")
def spideog():
    D = Doc2("ie-sp")
    out = [sky(D, [(0, "#AFC2D6"), (0.55, "#E6E2E2"), (1, "#F6DCC4")], 3, 600, ["#FFFFFF", "#C8D4E4", "#F2D8C8"], 80, angle=-4, sop=(0.06, 0.14))]
    out.append(soft_glow(D, 380, 360, 260, "#FFF2DC", 0.6))
    out.append(blooms(701, ["#C8D4E4", "#F2D8C8", "#FFFFFF"], 8, (0, 180, 600, 600), (90, 160), (0.08, 0.14)))
    # a misty winter field far below: hedgerow, a five-bar gate
    out.append(hill(D, ridge([(-10, 470), (200, 458), (400, 466), (610, 452)], 702, 4), 640, ("#E2E6E2", "#C8D0CC", "#9AA4A0"), 702, inkw=0, n=30))
    for k in range(6):
        out.append(dab_crown(D, -20 + k * 120, 462 - (k % 2) * 6, 70, 18, [("#C0C8CC", "#A0AAB0", "#808A92")], 703 + k, n=26, size=(4, 8), inkw=0, base=False))
    for k in range(5):
        y = 488 + k * 7
        out.append(pline([(400, y), (520, y - 4)], "#9AA0A8", 2, 709 + k, 0.7, 1))
    for x in (400, 520):
        out.append(taper([(x, 482), (x, 530)], 5, 5, "#8A9098"))
    out.append(pline([(400, 516), (520, 486)], "#9AA0A8", 2, 715, 0.7, 1))
    out.append(f'<rect y="430" width="600" height="170" fill="{D.lin([(0, "#FFFFFF", 0), (0.4, "#F6F2F0", 0.5), (1, "#FFFFFF", 0.2)])}"/>')
    # the hawthorn branch, sweeping up from bottom left
    br = [(-20, 520), (80, 494), (170, 470), (260, 456), (350, 436), (440, 404), (540, 356), (620, 330)]
    ws = [32, 27, 23, 20, 17, 14, 11, 9]
    out.append(painted(D, limb(br, ws), ("#9A7A62", "#5E4434", "#2A1C14"), 704, sdir=(0.2, 1), sk=0.2, angle=-10, n=50, slen=(10, 30), sw=(1, 3), inkw=1.8, hi=0.4))
    out.append(specks(705, (0, 400, 600, 520), ["#B8C0A0", "#8A9A7A"], 30, (1, 2.4), (0.4, 0.8)))
    twigs = [[(110, 488), (96, 444), (74, 410), (56, 392)], [(330, 440), (350, 400), (380, 372)], [(430, 410), (452, 446), (486, 470)],
             [(200, 466), (214, 504), (206, 534)], [(500, 378), (520, 330), (546, 300)], [(250, 458), (240, 420), (216, 396)]]
    for k, tw in enumerate(twigs):
        out.append(painted(D, limb(tw, [10, 7, 5, 3][:len(tw)]), ("#9A7A62", "#5E4434", "#2A1C14"), 706 + k, sk=0.2, n=8, inkw=1.2, hi=0.3))
        for j in range(1, len(tw)):
            px, py = tw[j]
            out.append(f'<path d="M {px - 1:.1f} {py:.1f} l {6 if j % 2 else -6} -7 l {-3 if j % 2 else 3} 7 Z" fill="#3A2818"/>')
    for (x, y, a) in ((60, 506, -60), (150, 478, -110), (300, 446, 70), (390, 422, -120), (470, 390, -60)):
        out.append(f'<path d="M {x:.1f} {y:.1f} l {math.cos(math.radians(a)) * 12:.1f} {math.sin(math.radians(a)) * 12:.1f} l {math.cos(math.radians(a + 90)) * 3:.1f} {math.sin(math.radians(a + 90)) * 3:.1f} Z" fill="#3A2818"/>')
    for k, (x, y, a) in enumerate(((60, 396, -150), (382, 372, -40), (488, 470, 30), (206, 532, 80), (548, 300, -40), (216, 396, -130), (150, 496, 110))):
        out.append(haw_leaf(D, x, y, 28, a, 720 + k))
    for k, (x, y, n) in enumerate(((80, 412, 6), (362, 392, 7), (456, 450, 6), (212, 506, 6), (526, 326, 6), (236, 418, 5), (130, 494, 4),
                                    (58, 396, 4), (400, 380, 5), (480, 470, 4), (552, 304, 4), (190, 520, 4))):
        out.append(haw_cluster(D, x, y, 730 + k, n, r=7))
    out.append(robin_ie(D, 316, 446, 2.25, 740, flip=-1))
    out.append(specks(741, (0, 0, 600, 600), ["#FFFFFF"], 90, (1, 2.6), (0.6, 0.95)))
    out.append(letters(D, 300, 132, "spideog", SERIF_IT, 112, "#8A2A14", ["#B03A1E", "#6A1A0A", "#D0582E"], 742, max_w=380,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#F8A880"))
    out.append(ruled(300, 182, "WHEN ROBINS APPEAR, LOVED ONES ARE NEAR", "#3A4A5A", font=JOS, size=18, ls=2, line_w=14, gap=8, max_w=420))
    return finish_ie(D, out, 743)


# ================================================================ 10. the Aran Islands — a tarred currach on the limestone shore
def currach_up(D, x0, x1, gun_y, seed, h=46, bow_up=26):
    """An upturned currach resting on stones: tarred black canvas hull, keel line, an upswept bow at the right,
    the pale wooden gunwale along the bottom edge."""
    L = x1 - x0
    keel = [(x0 + 4, gun_y - h * 0.55), (x0 + L * 0.2, gun_y - h * 0.95), (x0 + L * 0.55, gun_y - h), (x0 + L * 0.85, gun_y - h * 0.95), (x1 - 8, gun_y - h * 0.8 - bow_up * 0.4), (x1 + 6, gun_y - bow_up - 6)]
    gun = [(x1 + 6, gun_y - bow_up - 6), (x1 - 6, gun_y - bow_up * 0.4), (x0 + L * 0.8, gun_y), (x0 + L * 0.3, gun_y + 2), (x0 + 2, gun_y - 2)]
    hull = keel + gun
    o = [cast(D, (x0 + x1) / 2 + 10, gun_y + 14, L * 0.55, 10, strength=0.5, seed=seed)]
    o.append(painted(D, hull, ("#5A6478", "#1E2028", "#08080C"), seed, sdir=(0.2, 1), sk=0.12, angle=-4, n=40, slen=(20, 60), sw=(1, 3), inkw=1.8, hi=0.45, hik=0.12))
    cid = D.clip(f'<path d="{smooth_closed(hull)}"/>')
    inner = [taper([(x0 + L * 0.1, gun_y - h * 0.72), (x0 + L * 0.5, gun_y - h * 0.84), (x0 + L * 0.85, gun_y - h * 0.8)], 3, 6, "#B8D0E8", 0.5)]
    for k in range(7):
        t = 0.1 + k * 0.12
        inner.append(pline([(x0 + L * t, gun_y - h * 0.9), (x0 + L * t + 4, gun_y - 2)], "#3A4458", 1.2, seed + k, 0.45, 1))
    o.append(f'<g {cid}>{"".join(inner)}</g>')
    o.append(taper([(x0 + 2, gun_y - 2), (x0 + L * 0.3, gun_y + 2), (x0 + L * 0.8, gun_y), (x1 - 6, gun_y - bow_up * 0.4), (x1 + 6, gun_y - bow_up - 6)], 6, 3, "#C8A06A"))
    o.append(pline([(x0 + 2, gun_y), (x0 + L * 0.3, gun_y + 4), (x0 + L * 0.8, gun_y + 2)], "#5A3A1A", 1.2, seed, 0.6, 1))
    return "".join(o)


def limestone(D, x0, y0, x1, y1, seed):
    """Aran / Burren limestone pavement in perspective: pale clints split by dark grikes into irregular slabs,
    with tufts and little flowers in the cracks."""
    rnd = random.Random(seed)
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#3A3836"/>']
    rows = []
    y = y0
    while y < y1 + 20:
        rows.append(y)
        y += 10 + (y - y0) * 0.28
    grid = []
    for j, y in enumerate(rows):
        step = 46 + (y - y0) * 0.9
        xs = []
        x = x0 - rnd.uniform(0, step)
        while x < x1 + step:
            xs.append(x)
            x += step * rnd.uniform(0.6, 1.4)
        grid.append([(xx + rnd.uniform(-6, 6), y + rnd.uniform(-2, 2) * (1 + j * 0.4)) for xx in xs])
    for j in range(len(grid) - 1):
        top, bot = grid[j], grid[j + 1]
        for i in range(len(top) - 1):
            a_, b_ = top[i], top[i + 1]
            # matching points on the lower row: nearest x
            c_ = min(bot, key=lambda p: abs(p[0] - b_[0]))
            d_ = min(bot, key=lambda p: abs(p[0] - a_[0]))
            if c_ == d_:
                continue
            cell = [a_, b_, c_, d_]
            cxm = sum(p[0] for p in cell) / 4
            cym = sum(p[1] for p in cell) / 4
            shrink = [(cxm + (px - cxm) * 0.9, cym + (py - cym) * 0.86) for px, py in cell]
            c = mix("#CAC8C0", rnd.choice(["#A8A69E", "#DCDAD2", "#BAB4A8", "#C4C8CA"]), rnd.uniform(0, 0.6))
            out.append(painted(D, poly_pts(shrink, 12, seed + j * 97 + i, 1.0), (lt(c, 0.3), c, dk(c, 0.3)), seed + j * 97 + i, sdir=(0.3, 1), sk=0.12, angle=-4, n=4, inkw=0.9, inkop=0.5, hi=0.4))
            if rnd.random() < 0.3:
                out.append(f'<circle cx="{cxm + rnd.uniform(-8, 8):.1f}" cy="{cym:.1f}" r="{2 + (cym - y0) * 0.03:.1f}" fill="#8A8A84" opacity="0.5"/>')
    return "".join(out)


@design("aran-islands")
def aran_islands():
    D = Doc2("ie-ar")
    out = [sky(D, [(0, "#7EB0DA"), (0.6, "#CDE2EE"), (1, "#F2F0E6")], 3, 340, ["#FFFFFF", "#A8C8E4"], 50, angle=-3, sop=(0.06, 0.14))]
    out.append(puff_cloud(D, 470, 236, 150, 801, ("#FFFFFF", "#F6F4F0", "#B8C4D4")))
    out.append(puff_cloud(D, 120, 258, 110, 802, ("#FFFFFF", "#F6F4F0", "#B8C4D4")))
    # the sea: turquoise over sand near the shore, deep Atlantic blue beyond
    out.append(sea(D, 318, 600, [(0, "#2E6A9A"), (0.4, "#3E8AAE"), (1, "#7ACCC8")], 803, ["#FFFFFF", "#1E4A7A", "#A8E0E0"], n=90, ticks=["#FFFFFF", "#D8F0F0"]))
    # the island across the sound: a long low hill of walled fields, cottages, a ruined castle
    isl = ridge([(150, 330), (240, 312), (340, 296), (430, 288), (520, 294), (610, 300)], 804, 4)
    out.append(hill(D, isl + [(610, 332)], 336, ("#B8CC8A", "#86A462", "#4E6A3A"), 804, inkw=1, inkop=0.4))
    rnd = random.Random(805)
    for k in range(10):
        y = 300 + k * 3.5
        out.append(pline([(max(160, 560 - k * 40), y + rnd.uniform(-1, 1)), (610, y)], "#E8ECE4", 1.1, 806 + k, 0.7, 1))
    for k in range(18):
        x = rnd.uniform(200, 600)
        out.append(pline([(x, 300 + rnd.uniform(-4, 4)), (x + rnd.uniform(-3, 3), 330)], "#E8ECE4", 0.9, 830 + k, 0.6, 1))
    for k, (x, y) in enumerate(((260, 320), (300, 316), (470, 300), (540, 304), (370, 310))):
        out.append(f'<rect x="{x}" y="{y - 6}" width="11" height="6" fill="#FFFFFF"/><path d="M {x - 1} {y - 6} L {x + 5.5} {y - 10} L {x + 12} {y - 6} Z" fill="{["#5A6474", "#D8B060"][k % 2]}"/>')
    out.append(painted(D, rect_pts(424, 270, 440, 290, 5, 850, 0.3), STONE, 850, sk=0.2, n=3, inkw=1, hi=0.4))
    for k in range(3):
        out.append(f'<rect x="{424 + k * 6}" y="266" width="3.4" height="5" fill="#93918A"/>')
    out.append(painted(D, rect_pts(172, 302, 180, 326, 4, 851, 0.2), WASHW, 851, sk=0.1, n=2, inkw=0.8, hi=0.3))
    out.append(f'<path d="M 171 302 L 176 296 L 181 302 Z" fill="#2A2A30"/>')
    out.append(wave_lines(852, (150, 330, 600, 340), ["#FFFFFF"], 30, L=(8, 20), w=1.6, amp=1))
    # a currach out on the water, three rowing
    cy_ = 392
    out.append(taper([(196, cy_ + 4), (230, cy_ + 6), (280, cy_ + 5)], 2, 1, "#FFFFFF", 0.6))
    out.append(painted(D, [(196, cy_ - 6), (210, cy_ + 2), (276, cy_ + 2), (290, cy_ - 10), (282, cy_ - 4), (204, cy_ - 4)], ("#5A6478", "#1E2028", "#08080C"), 853, sk=0.1, n=4, inkw=1, hi=0.4))
    for k in range(3):
        px = 220 + k * 20
        out.append(f'<path d="{blob(px, cy_ - 10, 4.5, 6, 854 + k, 0.1, 8)}" fill="#2A2A34"/><circle cx="{px}" cy="{cy_ - 19}" r="3.6" fill="#E8C0A0"/><path d="M {px - 4} {cy_ - 21} q 4 -4 8 0" fill="#3A2A20"/>')
        out.append(pline([(px + 2, cy_ - 8), (px + 14, cy_ + 8)], "#C8A06A", 1.6, 857 + k, 0.9, 1))
    # foreground: limestone shore, the upturned currach and its oars
    out.append(limestone(D, -10, 448, 610, 610, 860))
    shore = rough([(-10, 452), (150, 440), (320, 446), (470, 436), (610, 444)], 861, 6, 3)
    out.append(f'<path d="{smooth_open(shore)} L 610 470 L -10 470 Z" fill="#E8F6F2" opacity="0.6"/>')
    out.append(wave_lines(862, (-10, 432, 610, 446), ["#FFFFFF"], 40, L=(10, 30), w=2.4, amp=2))
    for k, (x, y) in enumerate(((144, 520), (420, 516))):
        out.append(stone(D, x, y, 26, 14, 870 + k))
    out.append(currach_up(D, 96, 476, 506, 871, h=58, bow_up=34))
    for k, (a, b) in enumerate((((476, 560), (556, 420)), ((496, 566), (570, 432)))):
        out.append(taper([a, b], 5, 4, "#B88A52"))
        out.append(taper([(a[0] - 1, a[1]), (b[0] - 1, b[1])], 1.6, 1.2, "#F2D8A8", 0.8))
    out.append(grass(880, (0, 560, 600, 600), ["#5E8A3A", "#86B04E"], n=30, h=(6, 12)))
    for k in range(5):
        x, y = rnd.uniform(20, 580), rnd.uniform(540, 590)
        out.append(dab_crown(D, x, y, 7, 4, [("#C8A8F0", "#8A6AD0", "#4A3A8A")], 890 + k, n=8, size=(1.8, 3), inkw=0, base=False))
    out.append(letters(D, 300, 130, "Aran Islands", SERIF_IT, 96, "#183A5A", ["#2A5A86", "#0C2440", "#3A6A96"], 895, max_w=470,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#A8C8E8"))
    out.append(ruled(300, 178, "OILEÁIN ÁRANN", "#8A3A1A", font=JOS, size=22, ls=8, line_w=40, gap=14))
    return finish_ie(D, out, 896)


# ================================================================ 11. it's baltic! — the Aran jumper laid out flat
def knit_moss(D, box, seed, step=7, col="#FFFFFF", shade="#9A8A66"):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    o = []
    j = 0
    y = y0
    while y < y1:
        x = x0 + (j % 2) * step / 2
        while x < x1:
            o.append(f'<circle cx="{x + 0.6:.1f}" cy="{y + 0.8:.1f}" r="1.7" fill="{shade}" opacity="0.45"/><circle cx="{x:.1f}" cy="{y:.1f}" r="1.3" fill="{col}" opacity="0.85"/>')
            x += step
        y += step * 0.8
        j += 1
    return "".join(o)


def knit_cable(D, cx, y0, y1, w, seed, period=34):
    """A raised rope cable: two strands twisting over one another, light on top, shadow beneath."""
    o = [f'<rect x="{cx - w / 2 - 3:.1f}" y="{y0:.1f}" width="{w + 6:.1f}" height="{y1 - y0:.1f}" fill="#8A7A56" opacity="0.35"/>']
    y = y0 - period / 2
    k = 0
    while y < y1:
        a = (cx - w / 2, y)
        b = (cx + w / 2, y + period)
        c1 = [(cx - w * 0.42, y), (cx - w * 0.2, y + period * 0.3), (cx + w * 0.2, y + period * 0.7), (cx + w * 0.42, y + period)]
        c2 = [(cx + w * 0.42, y), (cx + w * 0.2, y + period * 0.3), (cx - w * 0.2, y + period * 0.7), (cx - w * 0.42, y + period)]
        under, over = (c2, c1) if k % 2 == 0 else (c1, c2)
        for strand, op in ((under, 0.8), (over, 1.0)):
            pts = catmull(strand, 5)
            o.append(taper([(px + 1.5, py + 2) for px, py in pts], w * 0.42, w * 0.42, "#6A5A3A", 0.45 * op))
            o.append(taper(pts, w * 0.44, w * 0.44, "#F2E8D0" if op == 1 else "#D8CCAE"))
            o.append(taper([(px - w * 0.08, py - 1) for px, py in pts], w * 0.14, w * 0.1, "#FFFFFF", 0.75 * op))
            for t in range(1, len(pts) - 1, 2):
                px, py = pts[t]
                o.append(f'<path d="M {px - w * 0.14:.1f} {py - 2:.1f} L {px:.1f} {py + 2:.1f} L {px + w * 0.14:.1f} {py - 2:.1f}" stroke="#B8A880" stroke-width="0.9" fill="none" opacity="0.6"/>')
        y += period
        k += 1
    return "".join(o)


def knit_honeycomb(D, x0, x1, y0, y1, seed, cell=14):
    o = []
    cols = int((x1 - x0) / cell)
    rows = int((y1 - y0) / cell) + 1
    for j in range(rows):
        for i in range(cols):
            cx = x0 + (i + 0.5) * cell + (j % 2) * cell / 2
            cy = y0 + j * cell
            if cx > x1 - cell * 0.3:
                continue
            pts = [(cx - cell * 0.45, cy), (cx, cy - cell * 0.45), (cx + cell * 0.45, cy), (cx, cy + cell * 0.45)]
            o.append(f'<path d="{smooth_closed(pts)}" fill="#E2D6B8" stroke="#8A7A56" stroke-width="1.4" opacity="0.85"/>')
            o.append(f'<path d="M {cx - cell * 0.3:.1f} {cy - cell * 0.1:.1f} Q {cx:.1f} {cy - cell * 0.42:.1f} {cx + cell * 0.3:.1f} {cy - cell * 0.1:.1f}" stroke="#FFFFFF" stroke-width="1.3" fill="none" opacity="0.8"/>')
    return "".join(o)


def knit_diamond(D, cx, y0, y1, w, seed, period=70):
    o = []
    y = y0
    while y < y1:
        d = [(cx, y), (cx + w / 2, y + period / 2), (cx, y + period), (cx - w / 2, y + period / 2)]
        o.append(f'<path d="{pd(d)}" fill="none" stroke="#6A5A3A" stroke-width="7" opacity="0.35" transform="translate(1.5 2)"/>')
        o.append(f'<path d="{pd(d)}" fill="none" stroke="#F2E8D0" stroke-width="6.5" stroke-linejoin="round"/>')
        o.append(f'<path d="{pd(d)}" fill="none" stroke="#FFFFFF" stroke-width="1.6" opacity="0.7" transform="translate(-1.2 -1)"/>')
        o.append(knit_moss(D, (cx - w * 0.2, y + period * 0.32, cx + w * 0.2, y + period * 0.7), seed, 6))
        o.append(f'<circle cx="{cx + 1:.1f}" cy="{y + period / 2 + 2:.1f}" r="5" fill="#6A5A3A" opacity="0.35"/><circle cx="{cx:.1f}" cy="{y + period / 2:.1f}" r="4.6" fill="#F6EEDA"/><circle cx="{cx - 1.4:.1f}" cy="{y + period / 2 - 1.4:.1f}" r="1.6" fill="#FFFFFF"/>')
        y += period
    return "".join(o)


def ribbing(D, pts_box, seed, vertical=True, step=6):
    x0, y0, x1, y1 = pts_box
    o = []
    if vertical:
        x = x0
        while x < x1:
            o.append(f'<path d="M {x:.1f} {y0:.1f} L {x:.1f} {y1:.1f}" stroke="#8A7A56" stroke-width="1.8" opacity="0.5"/><path d="M {x + step / 2:.1f} {y0:.1f} L {x + step / 2:.1f} {y1:.1f}" stroke="#FFFFFF" stroke-width="1.6" opacity="0.6"/>')
            x += step
    return "".join(o)


@design("its-baltic")
def its_baltic():
    D = Doc2("ie-ib")
    out = [wood_planks(D, 0, 600, 901, ("#7A9AB0", "#4E6E86", "#26405A"), 6, vertical=True)]
    out.append(soft_glow(D, 300, 380, 360, "#FFF2D8", 0.3))
    # the jumper: body, sleeves out, crew neck
    body = [(160, 236), (232, 222), (264, 236), (336, 236), (368, 222), (440, 236), (448, 300), (446, 420), (452, 546), (148, 546), (154, 420), (152, 300)]
    sl_l = [(160, 236), (152, 300), (128, 360), (96, 430), (76, 474), (130, 494), (152, 446), (172, 372), (178, 330)]
    sl_r = [(440, 236), (448, 300), (472, 360), (504, 430), (524, 474), (470, 494), (448, 446), (428, 372), (422, 330)]
    out.append(cast(D, 308, 560, 230, 20, strength=0.45, seed=902))
    wool = ("#FFF8E8", "#EADFC4", "#A89670")
    for k, part in enumerate((sl_l, sl_r)):
        out.append(f'<path d="{smooth_closed(shift(part, 6, 8))}" fill="#14202E" opacity="0.35"/>')
        out.append(painted(D, part, wool, 903 + k, sdir=(0.3, 1), sk=0.08, angle=-60, n=20, inkw=1.8, hi=0.3))
        cid = D.clip(f'<path d="{smooth_closed(part)}"/>')
        g = [knit_moss(D, bbox(part), 904 + k, 7)]
        a_, b_ = ((170, 260), (104, 470)) if k == 0 else ((430, 260), (496, 470))
        ang = math.degrees(math.atan2(b_[1] - a_[1], b_[0] - a_[0])) - 90
        L = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
        g.append(f'<g transform="translate({a_[0]} {a_[1]}) rotate({ang:.1f})">{knit_cable(D, 0, 0, L, 18, 905 + k, 30)}</g>')
        out.append(f'<g {cid}>{"".join(g)}</g>')
    out.append(f'<path d="{smooth_closed(shift(body, 6, 8))}" fill="#14202E" opacity="0.35"/>')
    out.append(painted(D, body, wool, 906, sdir=(0.3, 1), sk=0.06, angle=-90, n=30, inkw=2, hi=0.3))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    g = [knit_moss(D, (148, 220, 452, 546), 907, 7)]
    g.append(f'<rect x="174" y="226" width="52" height="300" fill="#EADFC4"/><rect x="374" y="226" width="52" height="300" fill="#EADFC4"/>')
    g.append(knit_honeycomb(D, 176, 226, 236, 520, 908, 13))
    g.append(knit_honeycomb(D, 376, 426, 236, 520, 909, 13))
    for cx in (244, 356):
        g.append(knit_cable(D, cx, 226, 520, 24, 910 + cx, 32))
    g.append(f'<rect x="268" y="226" width="64" height="300" fill="#EADFC4"/>')
    g.append(knit_diamond(D, 300, 250, 520, 58, 912, 68))
    g.append(shade_over(D, smooth_closed(body), "#3A2A10", 0.3, 0, 0, 1, 1, 0.5))
    out.append(f'<g {cid}>{"".join(g)}</g>')
    # ribbed hem and cuffs
    hem = rect_pts(148, 516, 452, 548, 12, 913, 0.5)
    out.append(painted(D, hem, wool, 913, sk=0.1, n=6, inkw=1.6, hi=0.3) + f'<g {D.clip(f"<path d=\"{smooth_closed(hem)}\"/>")}>{ribbing(D, (148, 512, 452, 552), 914)}</g>')
    for k, cuff in enumerate(([(76, 474), (130, 494), (122, 516), (66, 498)], [(524, 474), (470, 494), (478, 516), (534, 498)])):
        out.append(painted(D, poly_pts(cuff, 8, 915 + k, 0.4), wool, 915 + k, sk=0.1, n=4, inkw=1.4, hi=0.3))
        x0_, y0_, x1_, y1_ = bbox(cuff)
        out.append(f'<g {D.clip(f"<path d=\"{smooth_closed(cuff)}\"/>")}><g transform="rotate({-60 if k == 0 else 60} {(x0_ + x1_) / 2:.1f} {(y0_ + y1_) / 2:.1f})">{ribbing(D, (x0_ - 30, y0_ - 30, x1_ + 30, y1_ + 30), 917)}</g></g>')
    neck = [(232, 222), (264, 236), (300, 244), (336, 236), (368, 222), (352, 214), (300, 226), (248, 214)]
    out.append(painted(D, neck, wool, 918, sk=0.12, n=6, inkw=1.6, hi=0.4))
    out.append(f'<path d="{smooth_closed([(250, 216), (300, 228), (350, 216), (330, 210), (300, 214), (270, 210)])}" fill="#5A6A7A" opacity="0.8"/>')
    out.append(f'<g {D.clip(f"<path d=\"{smooth_closed(neck)}\"/>")}>{ribbing(D, (228, 206, 372, 250), 919, step=5)}</g>')
    # a little wooden toggle tag
    out.append(painted(D, rect_pts(420, 256, 436, 272, 5, 920, 0.3), ("#E8B880", "#B07A40", "#5A3810"), 920, sk=0.15, n=2, inkw=1, hi=0.4))
    out.append(letters(D, 300, 132, "it's baltic!", SERIF_IT, 110, "#FFFAF0", ["#FFFFFF", "#E8F0F6", "#F2EAD8"], 921, max_w=440,
                       shadow="#14202E", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 182, "WRAP UP WARM, PET", "#F6D27A", font=JOS, size=22, ls=6, line_w=30, gap=12))
    return finish_ie(D, out, 922)


# ================================================================ 12. the Claddagh — the ring in its velvet box
def claddagh_ring(D, cx, cy, s, seed):
    """A gold Claddagh ring seen face-on, standing upright: crowned heart held by two hands, the band behind.
    (cx, cy) = centre of the heart; s = scale (1 = heart about 64 wide)."""
    gold = ("#FFF0A8", "#E2AE3A", "#8A5A10")
    o = []
    # band: the hoop behind (only its back arc shows below the face)
    band_c = (cx, cy + 58 * s)
    o.append(ink(smooth_open(ell_pts(band_c[0], band_c[1], 62 * s, 56 * s, -32, 212, 30)), "#5A3A08", 14 * s, seed, 1, 1))
    o.append(ink(smooth_open(ell_pts(band_c[0], band_c[1], 62 * s, 56 * s, -32, 212, 30)), gold[1], 11 * s, seed + 1, 1, 1))
    o.append(ink(smooth_open(ell_pts(band_c[0], band_c[1], 58 * s, 52 * s, 120, 200, 12)), gold[0], 3 * s, seed + 2, 1, 0.8))
    o.append(ink(smooth_open(ell_pts(band_c[0], band_c[1], 66 * s, 60 * s, -20, 80, 12)), "#8A5A10", 2 * s, seed + 3, 1, 0.6))
    # hands and cuffs
    for sg in (-1, 1):
        cuff = [(cx + sg * 64 * s, cy + 30 * s), (cx + sg * 50 * s, cy + 10 * s), (cx + sg * 40 * s, cy + 16 * s), (cx + sg * 52 * s, cy + 40 * s)]
        o.append(painted(D, cuff, gold, seed + 3 + sg, sdir=(0.5, 0.8), sk=0.2, n=4, inkw=1.4 * s, inkc="#5A3A08", hi=0.5))
        for k in range(3):
            t = 0.25 + k * 0.25
            a, b = lerp2(cuff[0], cuff[1], t), lerp2(cuff[3], cuff[2], t)
            o.append(pline([a, b], "#8A5A10", 1.2 * s, seed + k, 0.8, 1))
        hand = [(cx + sg * 50 * s, cy + 10 * s), (cx + sg * 38 * s, cy - 8 * s), (cx + sg * 30 * s, cy - 22 * s), (cx + sg * 20 * s, cy - 26 * s),
                (cx + sg * 12 * s, cy - 16 * s), (cx + sg * 16 * s, cy - 4 * s), (cx + sg * 16 * s, cy + 12 * s), (cx + sg * 22 * s, cy + 26 * s),
                (cx + sg * 32 * s, cy + 28 * s), (cx + sg * 40 * s, cy + 16 * s)]
        o.append(painted(D, hand, gold, seed + 6 + sg, sdir=(-0.4 * sg, 0.8), sk=0.2, n=6, inkw=1.4 * s, inkc="#5A3A08", hi=0.5))
        for k in range(3):
            fy = cy - 14 * s + k * 10 * s
            o.append(pline([(cx + sg * 16 * s, fy), (cx + sg * 30 * s, fy + 3 * s)], "#8A5A10", 1.2 * s, seed + k, 0.8, 1))
    # heart
    hp = heart_d(cx, cy + 4 * s, 30 * s)
    o.append(painted(D, hp, gold, seed + 9, sdir=(0.6, 0.8), sk=0.22, n=10, inkw=1.6 * s, inkc="#5A3A08", hi=0.55, hik=0.12))
    o.append(f'<path d="{blob(cx - 10 * s, cy - 6 * s, 8 * s, 4 * s, seed + 10, 0.2, 8, -30)}" fill="#FFFBE0" opacity="0.85"/>')
    # crown
    cw, ctop, cb = 30 * s, cy - 46 * s, cy - 22 * s
    crown = [(cx - cw, cb), (cx - cw * 1.08, ctop + 8 * s), (cx - cw * 0.55, ctop + 14 * s), (cx, ctop), (cx + cw * 0.55, ctop + 14 * s), (cx + cw * 1.08, ctop + 8 * s), (cx + cw, cb)]
    o.append(painted(D, poly_pts(crown, 6 * s, seed + 11, 0.3), gold, seed + 11, sdir=(0.5, 0.8), sk=0.18, n=6, inkw=1.4 * s, inkc="#5A3A08", hi=0.5))
    o.append(f'<path d="{hg.org_rect(cx - cw * 1.02, cb - 7 * s, cw * 2.04, 8 * s, seed + 12, 0.3, 6, 1)}" fill="{gold[1]}" stroke="#5A3A08" stroke-width="{1.2 * s:.1f}"/>')
    for k in range(5):
        o.append(f'<circle cx="{cx - cw * 0.8 + k * cw * 0.4:.1f}" cy="{cb - 3 * s:.1f}" r="{1.6 * s:.1f}" fill="{gold[0]}"/>')
    for (bx, by) in ((cx - cw * 1.08, ctop + 8 * s), (cx, ctop), (cx + cw * 1.08, ctop + 8 * s)):
        o.append(f'<circle cx="{bx:.1f}" cy="{by - 3 * s:.1f}" r="{4 * s:.1f}" fill="{gold[1]}" stroke="#5A3A08" stroke-width="{1.2 * s:.1f}"/><circle cx="{bx - 1.2 * s:.1f}" cy="{by - 4.2 * s:.1f}" r="{1.3 * s:.1f}" fill="#FFFBE0"/>')
    return "".join(o)


@design("claddagh")
def claddagh():
    D = Doc2("ie-cd")
    out = [sky(D, [(0, "#1E5A3E"), (1, "#0C2E1E")], 3, 600, ["#2E7A52", "#08200F", "#3E8A60"], 120, angle=-60, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 300, 360, 300, "#8AE0A8", 0.25))
    rnd = random.Random(1001)
    # open velvet ring box: satin-lined lid behind, cushion with the slot in front
    out.append(painted(D, poly_pts([(96, 196), (504, 196), (522, 440), (78, 440)], 20, 1002, 0.6), ("#3E9A6A", "#1E6A44", "#0A3A22"), 1002, sk=0.12, n=40, inkw=2, hi=0.3))
    out.append(painted(D, poly_pts([(116, 212), (484, 212), (500, 430), (100, 430)], 20, 1003, 0.6), ("#FFFDF4", "#F2E8D2", "#C0AE8A"), 1003, sdir=(0, 1), sk=0.06, angle=-80, n=30, inkw=1.4, hi=0.4))
    for k in range(6):
        x = 150 + k * 60
        out.append(taper([(x, 220), (x + 6, 320), (x - 4, 424)], 2, 7, "#D8C8A4", 0.5))
    out.append(soft_glow(D, 300, 320, 190, "#FFFFFF", 0.4))
    out.append(cast(D, 310, 590, 280, 20, strength=0.6, seed=1004))
    base = poly_pts([(70, 440), (530, 440), (546, 640), (54, 640)], 20, 1005, 0.6)
    out.append(painted(D, base, ("#3E9A6A", "#1E6A44", "#0A3A22"), 1005, sdir=(0.3, 1), sk=0.12, angle=-80, n=50, inkw=2, hi=0.35))
    cushion = [(96, 446), (504, 446), (500, 540), (100, 540)]
    out.append(painted(D, poly_pts(cushion, 20, 1006, 0.6), ("#2E8A5A", "#165A38", "#06301C"), 1006, sdir=(0, 1), sk=0.15, angle=0, n=40, inkw=1.4, hi=0.4))
    out.append(taper([(104, 452), (300, 458), (496, 452)], 3, 3, "#8AD8A8", 0.5))
    out.append(f'<path d="M 82 552 L 518 552" stroke="#E2AE3A" stroke-width="2.4" opacity="0.8"/>')
    out.append(f'<path d="{smooth_closed([(180, 486), (300, 494), (420, 486), (420, 500), (300, 508), (180, 500)])}" fill="#041A10"/>')
    # the ring standing in the slot
    out.append(claddagh_ring(D, 300, 318, 1.62, 1010))
    out.append(f'<path d="{smooth_closed([(190, 492), (300, 500), (410, 492), (410, 510), (300, 518), (190, 510)])}" fill="#165A38"/>')
    out.append(taper([(196, 494), (300, 502), (404, 494)], 2, 2, "#041A10", 0.9))
    for (x, y, r) in ((214, 262, 8), (392, 290, 6), (340, 232, 5)):
        out.append(sparkle(x, y, r, "#FFFFFF", 0.95))
    out.append(specks(1011, (40, 40, 560, 560), ["#E8C870"], 30, (0.8, 1.8), (0.3, 0.7)))
    out.append(letters(D, 300, 124, "the Claddagh", SERIF_IT, 92, "#F6D27A", ["#FFF0B0", "#C8902A", "#FFE08A"], 1012, max_w=450,
                       shadow="#06200F", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 170, "LOVE · LOYALTY · FRIENDSHIP", "#FFF4E0", font=JOS, size=19, ls=4, line_w=24, gap=10))
    out.append(letters(D, 300, 534, "grá · dílseacht · cairdeas", SERIF_IT, 34, "#F6D27A", ["#FFF0B0", "#C8902A"], 1013, max_w=330, wob=0.3))
    return finish_ie(D, out, 1014)



# ================================================================ 13. Éire — an illuminated initial in the manner of the old Irish gospel books
def _seg_x(p1, p2, p3, p4):
    d = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0])
    if abs(d) < 1e-9:
        return None
    t = ((p3[0] - p1[0]) * (p4[1] - p3[1]) - (p3[1] - p1[1]) * (p4[0] - p3[0])) / d
    u = ((p3[0] - p1[0]) * (p2[1] - p1[1]) - (p3[1] - p1[1]) * (p2[0] - p1[0])) / d
    if 0 < t < 1 and 0 < u < 1:
        return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1])), (p2[0] - p1[0], p2[1] - p1[1])
    return None


def plait(x0, y0, x1, y1, w, cols, edge="#1A0E06", k=2, hi="#FFF6D8"):
    """Interlace plait filling a horizontal band: k zigzag ribbons that cross alternately over and under, each
    ribbon outlined in dark ink with a pale highlight (the gap at each crossing reads as over/under)."""
    H = y1 - y0
    m = w * 0.75
    ya, yb = y0 + m, y1 - m
    span = yb - ya
    strands = []
    for i in range(k):
        ph = i * 2 * span / k
        pts = []
        x = x0 - 2 * span + ph
        up = True
        while x < x1 + 2 * span:
            pts.append((x, yb if up else ya))
            x += span
            up = not up
        strands.append(pts)
    out = []

    def draw(pts, col, cap="round"):
        d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts)
        return (f'<path d="{d}" fill="none" stroke="{edge}" stroke-width="{w + 3:.1f}" stroke-linejoin="round" stroke-linecap="{cap}"/>'
                f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w:.1f}" stroke-linejoin="round" stroke-linecap="{cap}"/>'
                f'<path d="{d}" fill="none" stroke="{hi}" stroke-width="{max(0.8, w * 0.18):.1f}" stroke-linejoin="round" stroke-linecap="{cap}" opacity="0.55" transform="translate(-0.6 -0.8)"/>')
    for i, pts in enumerate(strands):
        out.append(draw(pts, cols[i % len(cols)]))
    # redraw the over-strand at every crossing
    for i in range(k):
        for j in range(i + 1, k):
            for a in range(len(strands[i]) - 1):
                for b in range(len(strands[j]) - 1):
                    r = _seg_x(strands[i][a], strands[i][a + 1], strands[j][b], strands[j][b + 1])
                    if not r:
                        continue
                    (cx, cy), _ = r
                    par = (int(round((cx - x0) / span * 2)) + (1 if cy > (ya + yb) / 2 else 0)) % 2
                    si, sa = (i, a) if par == 0 else (j, b)
                    p, q = strands[si][sa], strands[si][sa + 1]
                    L = math.hypot(q[0] - p[0], q[1] - p[1])
                    ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L
                    hl = w * 1.15
                    out.append(draw([(cx - ux * hl, cy - uy * hl), (cx + ux * hl, cy + uy * hl)], cols[si % len(cols)], "butt"))
    return "".join(out)


def beast_head(x, y, s, flip=1, col="#E2A82E", inkc="#1A0E06"):
    """A zoomorphic terminal: a hound's head with a curled lappet and open jaws, in the Insular manner."""
    o = []
    head = [(0, 0), (10, -10), (26, -12), (40, -6), (46, 2), (34, 2), (26, 6), (36, 12), (30, 16), (14, 12), (2, 10)]
    pts = [(x + px * s * flip, y + py * s) for px, py in head]
    o.append(f'<path d="{smooth_closed(pts)}" fill="{col}" stroke="{inkc}" stroke-width="{2.2 * s:.1f}" stroke-linejoin="round"/>')
    o.append(f'<circle cx="{x + 18 * s * flip:.1f}" cy="{y - 4 * s:.1f}" r="{3 * s:.1f}" fill="#FFFFFF" stroke="{inkc}" stroke-width="{1.4 * s:.1f}"/><circle cx="{x + 18 * s * flip:.1f}" cy="{y - 4 * s:.1f}" r="{1.3 * s:.1f}" fill="{inkc}"/>')
    lap = [(x + (8 + 10 * math.cos(math.radians(a)) * (1 - i * 0.08)) * s * flip, y + (-14 + 10 * math.sin(math.radians(a)) * (1 - i * 0.08)) * s) for i, a in enumerate(range(90, 460, 40))]
    o.append(f'<path d="{smooth_open(lap)}" fill="none" stroke="{inkc}" stroke-width="{4.4 * s:.1f}" stroke-linecap="round"/><path d="{smooth_open(lap)}" fill="none" stroke="#C8302A" stroke-width="{2.4 * s:.1f}" stroke-linecap="round"/>')
    o.append(f'<path d="M {x + 34 * s * flip:.1f} {y + 2 * s:.1f} l {4 * s * flip:.1f} {3 * s:.1f}" stroke="{inkc}" stroke-width="{1.4 * s:.1f}"/>')
    return "".join(o)


def red_dots(path_pts, step, seed, r=2.2, col="#C8302A"):
    out = []
    acc = 0
    for (p, q) in zip(path_pts, path_pts[1:]):
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        t = 0
        while t < L:
            if acc <= 0:
                x, y = p[0] + (q[0] - p[0]) * t / L, p[1] + (q[1] - p[1]) * t / L
                out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}"/>')
                acc = step
            dt = min(acc, L - t) if acc > 0 else 0.5
            t += max(dt, 0.5)
            acc -= max(dt, 0.5)
    return "".join(out)


@design("eire")
def eire():
    D = Doc2("ie-ei")
    out = [paper(D.nid(), "#F0DEB4", "#8A6A3A", 1101)]
    out.append(blooms(1102, ["#D8B880", "#C8A068", "#E8D0A0"], 9, (0, 0, 600, 600), (100, 200), (0.08, 0.16)))
    out.append(f'<rect width="600" height="600" fill="{D.rad([(0, "#000000", 0), (0.7, "#5A3A10", 0.0), (1, "#5A3A10", 0.35)])}"/>')
    # knotwork border band
    cols = ["#E2A82E", "#2E6AA8", "#C8302A", "#3E8A5A"]
    bw = 30
    for (x0, y0, x1, y1, rotd) in ((58, 58, 542, 58 + bw, 0), (58, 542 - bw, 542, 542, 0)):
        cid = D.clip(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/>')
        out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#1A0E06"/>')
        out.append(f'<g {cid}>{plait(x0, y0, x1, y1, 7, cols[:2], k=2)}</g>')
    for (x0, x1) in ((58, 58 + bw), (542 - bw, 542)):
        cid = D.clip(f'<rect x="{x0}" y="{58 + bw}" width="{bw}" height="{484 - 2 * bw}"/>')
        out.append(f'<rect x="{x0}" y="{58 + bw}" width="{bw}" height="{484 - 2 * bw}" fill="#1A0E06"/>')
        out.append(f'<g {cid}><g transform="translate({x0 + bw} {58 + bw}) rotate(90)">{plait(0, 0, 484 - 2 * bw, bw, 7, cols[2:], k=2)}</g></g>')
    for (x, y) in ((58, 58), (542 - bw, 58), (58, 542 - bw), (542 - bw, 542 - bw)):
        out.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{bw}" fill="#E2A82E" stroke="#1A0E06" stroke-width="2.4"/>')
        out.append(f'<circle cx="{x + bw / 2}" cy="{y + bw / 2}" r="8" fill="#C8302A" stroke="#1A0E06" stroke-width="2"/><circle cx="{x + bw / 2}" cy="{y + bw / 2}" r="3" fill="#FFF0C0"/>')
    for (x0, y0, x1, y1) in ((56, 56, 544, 544), (56 + bw + 4, 56 + bw + 4, 544 - bw - 4, 544 - bw - 4)):
        out.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="none" stroke="#1A0E06" stroke-width="2.4"/>')
    # the great initial É: stem and three arms, filled with interlace on a dark ground
    stem = (112, 138, 168, 420)
    arms = [(112, 138, 290, 186), (112, 262, 256, 306), (112, 372, 300, 420)]
    shapes = [stem] + arms
    letter_d = " ".join(hg.org_rect(x0, y0, x1 - x0, y1 - y0, 1103 + i, 0.6, 12, 6) for i, (x0, y0, x1, y1) in enumerate(shapes))
    out.append(f'<path d="{letter_d}" fill="#1A0E06" transform="translate(4 5)" opacity="0.25"/>')
    out.append(f'<path d="{letter_d}" fill="#2A1A3A"/>')
    cid = D.clip(f'<path d="{letter_d}"/>')
    inner = [f'<g transform="translate(168 138) rotate(90)">{plait(0, 0, 282, 56, 9, ["#E2A82E", "#3E8A5A"], k=2)}</g>']
    for i, (x0, y0, x1, y1) in enumerate(arms):
        inner.append(plait(x0 + 40, y0, x1 + 10, y1, 8, [["#E2A82E", "#C8302A"], ["#2E6AA8", "#E2A82E"], ["#C8302A", "#3E8A5A"]][i], k=2))
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    out.append(f'<path d="{letter_d}" fill="none" stroke="#1A0E06" stroke-width="3.4"/>')
    out.append(f'<path d="{letter_d}" fill="none" stroke="#E2A82E" stroke-width="1.2" transform="translate(0 0)" opacity="0.0"/>')
    # red dotting around the letter (the old scribes' halo)
    for (x0, y0, x1, y1) in [(104, 130, 298, 130), (104, 130, 104, 428), (104, 428, 308, 428), (298, 130, 298, 194), (264, 254, 264, 314)]:
        out.append(red_dots([(x0, y0), (x1, y1)], 8, 1104))
    # spiral terminals at the arm ends
    for i, (x0, y0, x1, y1) in enumerate(arms):
        cx_, cy_ = x1 + 16, (y0 + y1) / 2
        sp = [(cx_ + (14 - j * 1.1) * math.cos(math.radians(j * 40)), cy_ + (14 - j * 1.1) * math.sin(math.radians(j * 40))) for j in range(12)]
        out.append(f'<circle cx="{cx_}" cy="{cy_}" r="18" fill="#E2A82E" stroke="#1A0E06" stroke-width="3"/>')
        out.append(f'<path d="{smooth_open(sp)}" fill="none" stroke="#1A0E06" stroke-width="2.6" stroke-linecap="round"/>')
        out.append(f'<circle cx="{cx_}" cy="{cy_}" r="3.2" fill="#C8302A"/>')
    # a hound biting the foot of the stem, a bird making the fada
    out.append(beast_head(118, 446, 1.3, 1, "#3E8A5A"))
    bx, by = 214, 104
    bird = [(bx - 26, by + 10), (bx - 10, by - 4), (bx + 8, by - 8), (bx + 22, by - 18), (bx + 30, by - 14), (bx + 22, by - 4), (bx + 6, by + 8), (bx - 14, by + 14)]
    out.append(f'<path d="{smooth_closed(bird)}" fill="#C8302A" stroke="#1A0E06" stroke-width="2.6"/>')
    out.append(f'<path d="M {bx + 30} {by - 14} l 10 -2 l -8 6 Z" fill="#E2A82E" stroke="#1A0E06" stroke-width="1.6"/>')
    out.append(f'<circle cx="{bx + 24}" cy="{by - 13}" r="2.2" fill="#FFF0C0" stroke="#1A0E06" stroke-width="1"/>')
    for k in range(3):
        out.append(f'<path d="M {bx - 12 + k * 9} {by + 2} q 4 -6 8 0" fill="none" stroke="#E2A82E" stroke-width="2"/>')
    out.append(f'<path d="M {bx - 26} {by + 10} q -12 4 -18 -6" fill="none" stroke="#1A0E06" stroke-width="3" stroke-linecap="round"/>')
    # "ire" in lapis blue with a gold shadow, red dots beneath
    out.append(letters(D, 400, 412, "ire", DMS, 230, "#1E3E8A", ["#2E5AB8", "#0E2260", "#3E6AC8"], 1105, max_w=210,
                       shadow="#E2A82E", soff=(0.02, 0.025), angle=-40, wob=0.4, inkc="#0A0A1A", inkw=1.4))
    out.append(red_dots([(320, 432), (490, 432)], 9, 1106))
    out.append(ruled(300, 482, "ISLAND OF SAINTS AND SCHOLARS", "#5A2A10", font=CINZEL, size=19, ls=3, line_w=18, gap=10, max_w=390))
    return finish_ie(D, out, 1107, color="#5A3A10")


# ================================================================ 14. cláirseach — the Irish harp by candlelight
def harp(D, seed):
    """A carved wire-strung Irish harp: slanted soundbox at the back, the curved neck, a bowed forepillar carved
    with knotwork, brass strings catching the light."""
    o = []
    wood = ("#E8A866", "#A8622E", "#4E2410")
    # geometry
    sb_bot, sb_top = (176, 534), (236, 214)
    pill_top, pill_bot = (432, 236), (384, 534)
    neck = catmull([(220, 208), (262, 196), (318, 222), (372, 236), (420, 218), (448, 222)], 8)
    o.append(cast(D, 290, 540, 170, 14, strength=0.5, seed=seed))
    # strings: from the neck down to the soundbox centre line
    n = 22
    sb_line = [lerp2((sb_bot[0] + 16, sb_bot[1] - 22), (sb_top[0] + 6, sb_top[1] + 20), t) for t in [i / (n - 1) for i in range(n)]]
    for i in range(n):
        t = i / (n - 1)
        top = neck[min(len(neck) - 1, int(lerp(len(neck) - 2, 1, t)))]
        top = (top[0], top[1] + 14)
        bot = sb_line[n - 1 - i] if False else lerp2((sb_bot[0] + 18, sb_bot[1] - 30), (sb_top[0] + 8, sb_top[1] + 24), 1 - t)
        col = "#C8302A" if i % 7 == 3 else ("#2E4A8A" if i % 7 == 0 else "#F2C86A")
        o.append(f'<path d="M {top[0]:.1f} {top[1]:.1f} L {bot[0]:.1f} {bot[1]:.1f}" stroke="{col}" stroke-width="1.6"/>')
        o.append(f'<path d="M {top[0] - 0.6:.1f} {top[1]:.1f} L {lerp(top[0], bot[0], 0.5) - 0.6:.1f} {lerp(top[1], bot[1], 0.5):.1f}" stroke="#FFF6D0" stroke-width="0.7" opacity="0.8"/>')
    # soundbox (with a carved rose of sound holes)
    sb = [(sb_bot[0] - 20, sb_bot[1]), (sb_bot[0] + 40, sb_bot[1]), (sb_top[0] + 18, sb_top[1] + 10), (sb_top[0] - 14, sb_top[1] + 4)]
    o.append(painted(D, poly_pts(sb, 14, seed + 1, 0.5), wood, seed + 1, sdir=(0.6, 0.3), sk=0.18, angle=-72, n=40, slen=(20, 60), sw=(1, 3), inkw=2, hi=0.45))
    sbface = [(sb_bot[0] + 4, sb_bot[1] - 6), (sb_bot[0] + 34, sb_bot[1] - 6), (sb_top[0] + 14, sb_top[1] + 16), (sb_top[0] - 4, sb_top[1] + 12)]
    o.append(f'<path d="{pd(sbface)}" fill="#C8803E" opacity="0.6"/>')
    for k, t in enumerate((0.3, 0.55, 0.78)):
        hx, hy = lerp2((sb_bot[0] + 18, sb_bot[1] - 20), (sb_top[0] + 6, sb_top[1] + 24), t)
        for j in range(3):
            a = math.radians(j * 120 - 90)
            o.append(f'<path d="{smooth_closed(heart_d(hx + math.cos(a) * 5, hy + math.sin(a) * 5, 4.2, j * 120))}" fill="#3A1A08"/>')
    # neck and pillar
    o.append(painted(D, limb(neck, [26, 24, 22, 22, 24, 26, 28, 30, 30, 28, 28, 26, 26, 24, 24, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22][:len(neck)]), wood, seed + 2, sdir=(0.3, 1), sk=0.18, angle=-10, n=30, inkw=2, hi=0.45))
    for k in range(0, len(neck), 3):
        x, y = neck[k]
        o.append(f'<circle cx="{x:.1f}" cy="{y + 8:.1f}" r="2.2" fill="#F2D28A" stroke="#4E2410" stroke-width="0.8"/>')
    pil = catmull([pill_top, (452, 300), (450, 400), (420, 480), pill_bot], 8)
    pw = [34, 32, 30, 28, 26, 26, 26, 26, 26, 26, 26, 27, 28, 28, 30, 30, 32, 32, 34, 34, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36][:len(pil)]
    pp = limb(pil, pw)
    o.append(painted(D, pp, wood, seed + 3, sdir=(0.7, 0.3), sk=0.2, angle=-80, n=40, inkw=2, hi=0.5))
    cid = D.clip(f'<path d="{smooth_closed(pp)}"/>')
    knot = []
    for k in range(len(pil) - 1):
        (xa, ya), (xb, yb) = pil[k], pil[k + 1]
        knot.append(f'<path d="M {xa - 7:.1f} {ya:.1f} Q {(xa + xb) / 2 + 9:.1f} {(ya + yb) / 2:.1f} {xb - 7:.1f} {yb:.1f}" stroke="#F2C88A" stroke-width="3" fill="none" opacity="0.7"/>')
        knot.append(f'<path d="M {xa + 7:.1f} {ya:.1f} Q {(xa + xb) / 2 - 9:.1f} {(ya + yb) / 2:.1f} {xb + 7:.1f} {yb:.1f}" stroke="#4E2410" stroke-width="2.4" fill="none" opacity="0.6"/>')
    o.append(f'<g {cid}>{"".join(knot)}</g>')
    # carved finial at the crown of the pillar
    o.append(painted(D, blob_pts(442, 222, 18, 16, seed + 4, 0.06, 12), wood, seed + 4, sk=0.2, n=6, inkw=1.8, hi=0.5))
    sp = [(442 + (10 - j * 0.8) * math.cos(math.radians(j * 45)), 222 + (10 - j * 0.8) * math.sin(math.radians(j * 45))) for j in range(12)]
    o.append(ink(smooth_open(sp), "#4E2410", 2, seed, 1, 0.8))
    # foot block
    o.append(painted(D, rect_pts(150, 528, 420, 546, 16, seed + 5, 0.5), wood, seed + 5, sdir=(0, 1), sk=0.2, angle=0, n=16, inkw=2, hi=0.4))
    return "".join(o)


@design("irish-harp")
def irish_harp():
    D = Doc2("ie-hp")
    out = [sky(D, [(0, "#2A4A8A"), (1, "#14244A")], 3, 600, ["#3A5AA0", "#0E1A3A", "#4A6AB0"], 110, angle=-80, sop=(0.08, 0.18))]
    # stencilled gold shamrocks on the wall
    rnd = random.Random(1201)
    for j in range(8):
        for i in range(8):
            x, y = i * 80 + (40 if j % 2 else 0), j * 76 + 20
            for a in (-90, 30, 150):
                out.append(f'<path d="{smooth_closed(heart_d(x + math.cos(math.radians(a)) * 6, y + math.sin(math.radians(a)) * 6, 6, a + 90))}" fill="#C8A040" opacity="0.13"/>')
    out.append(soft_glow(D, 120, 330, 300, "#FFC870", 0.45))
    # flagged floor
    out.append(f'<path d="M -10 520 L 610 520 L 610 610 L -10 610 Z" fill="#4A4038"/>')
    for k, y in enumerate((540, 572)):
        out.append(pline([(-10, y), (300, y + 1), (610, y)], "#2A221C", 2, 1202 + k, 0.8, 1))
    for x in range(-40, 640, 90):
        out.append(pline([(x, 520), (x - 20, 610)], "#2A221C", 1.6, 1210 + x, 0.7, 1))
    out.append(strokes(D.nid(), "M -10 520 L 610 520 L 610 610 L -10 610 Z", (-40, 520, 610, 610), ["#6A5E50", "#2A221C"], 1203, n=40, angle=-2, length=(30, 90), width=(2, 5), opacity=(0.2, 0.4)))
    # candle on a stool at left
    out.append(painted(D, rect_pts(56, 452, 130, 466, 10, 1204, 0.4), MAHOG, 1204, sk=0.2, angle=0, n=6, inkw=1.6, hi=0.4))
    for x in (64, 120):
        out.append(taper([(x, 466), (x - 2, 530)], 7, 6, "#3A1A0A"))
    out.append(painted(D, rect_pts(84, 386, 102, 452, 6, 1205, 0.3), CREAM, 1205, sk=0.12, n=4, inkw=1.2, hi=0.5))
    out.append(D.glow(93, 372, 70, "#FFD07A", 0.7))
    out.append(f'<path d="{smooth_closed([(93, 356), (99, 372), (93, 384), (87, 372)])}" fill="#FFC040"/><path d="{smooth_closed([(93, 366), (96, 375), (93, 382), (90, 375)])}" fill="#FFF4C0"/>')
    out.append(harp(D, 1206))
    out.append(letters(D, 300, 124, "cláirseach", SERIF_IT, 96, "#F6D27A", ["#FFF0B0", "#C8902A", "#FFE08A"], 1207, max_w=450,
                       shadow="#0A1430", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 170, "THE IRISH HARP", "#FFF4E0", font=JOS, size=21, ls=7, line_w=34, gap=12))
    return finish_ie(D, out, 1208)


# ================================================================ 15. seamróg — a pressed shamrock on a herbarium sheet
def trefoil(D, x, y, r, ang, seed, pal=("#8ACB6A", "#3E8A3A", "#1A4E1E"), n=3, chevron=True):
    """Clover leaf seen from above: n heart-shaped leaflets around (x, y), each with a pale chevron."""
    o = []
    for k in range(n):
        a = ang + k * 360 / n
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        lx, ly = x + ca * r * 0.55, y + sa * r * 0.55
        hp = heart_d(lx, ly, r * 0.55, a + 90)
        hp = [(px, py) for px, py in hp]
        o.append(painted(D, hp, pal, seed + k, sdir=(0.5, 0.8), sk=0.15, angle=a, n=5, inkw=1.0, inkop=0.6, hi=0.4))
        if chevron:
            m = (x + ca * r * 0.5, y + sa * r * 0.5)
            o.append(pline([(m[0] - sa * r * 0.22 + ca * r * 0.1, m[1] + ca * r * 0.22 + sa * r * 0.1), m, (m[0] + sa * r * 0.22 + ca * r * 0.1, m[1] - ca * r * 0.22 + sa * r * 0.1)], "#D8F0B8", max(1, r * 0.06), seed + k, 0.7, 1))
        o.append(pline([(x, y), (x + ca * r * 0.85, y + sa * r * 0.85)], pal[2], max(0.8, r * 0.04), seed, 0.5, 1))
    return "".join(o)


def clover_head(D, x, y, r, seed):
    rnd = random.Random(seed)
    o = []
    for k in range(14):
        a = rnd.uniform(0, 6.28)
        rr = math.sqrt(rnd.random()) * r
        o.append(f'<path d="{blob(x + math.cos(a) * rr, y + math.sin(a) * rr * 0.9, r * 0.35, r * 0.22, rnd.randint(0, 999), 0.2, 8, math.degrees(a))}" fill="{rnd.choice(["#FFE27A", "#F2C21C", "#E8A81A"])}" stroke="#8A6A10" stroke-width="0.6"/>')
    return "".join(o)


@design("seamrog")
def seamrog():
    D = Doc2("ie-sm")
    out = [paper(D.nid(), "#F4EEDC", FLECK, 1301)]
    out.append(blooms(1302, ["#D8DCC0", "#E8D8B8"], 6, (0, 0, 600, 600), (100, 200), (0.06, 0.1)))
    # herbarium sheet with a faint grid
    out.append(f'<rect x="70" y="66" width="460" height="470" fill="#FBF8EE" stroke="#C8BEA4" stroke-width="1.4"/>')
    out.append(f'<rect x="70" y="66" width="460" height="470" fill="#3A2A10" opacity="0.06" transform="translate(5 6)"/>')
    for k in range(1, 10):
        out.append(f'<path d="M {70 + k * 46} 66 L {70 + k * 46} 536" stroke="#D8E0D0" stroke-width="0.8"/>')
    # the pressed plant: creeping stems, trefoil leaves, little yellow clover heads
    rnd = random.Random(1303)
    stems = [[(196, 516), (214, 450), (236, 380), (262, 312), (280, 250)], [(204, 516), (176, 460), (140, 400), (118, 330)],
             [(212, 516), (270, 482), (330, 440), (366, 380), (380, 312)], [(200, 516), (236, 490), (300, 486), (352, 504)]]
    for k, st in enumerate(stems):
        out.append(ink(smooth_open(st), "#5E7A3A", 3, 1304 + k, 1, 0.95))
        out.append(ink(smooth_open([(px - 0.8, py) for px, py in st]), "#A8C878", 1, 1305 + k, 1, 0.8))
    for k, (x, y) in enumerate(((228, 300), (322, 392), (164, 410))):
        out.append(pline([(x, y + 30), (x + 4, y + 12), (x, y)], "#5E7A3A", 1.8, 1330 + k, 0.9, 1))
        out.append(clover_head(D, x, y, 11, 1333 + k))
    leaves = [(280, 244, 48, -20), (118, 322, 42, 10), (380, 304, 44, 40), (236, 384, 32, 60), (330, 440, 30, -30), (176, 460, 28, 30), (352, 504, 28, 0), (262, 316, 28, 100)]
    for k, (x, y, r, a) in enumerate(leaves):
        out.append(trefoil(D, x, y, r, a, 1310 + k * 3))
    for k in range(6):
        a = rnd.uniform(60, 120)
        out.append(pline([(204, 516), (204 + math.cos(math.radians(a)) * 14, 516 + math.sin(math.radians(a)) * 10), (204 + math.cos(math.radians(a)) * 30 + rnd.uniform(-8, 8), 516 + math.sin(math.radians(a)) * 18)], "#A88A5A", 1.2, 1340 + k, 0.8, 1))
    for k, (x, y, a) in enumerate(((226, 416, -30), (200, 500, 10), (318, 452, 20))):
        out.append(f'<g transform="rotate({a} {x} {y})"><rect x="{x - 22}" y="{y - 6}" width="44" height="12" fill="#F2E6C8" opacity="0.9" stroke="#C8B48A" stroke-width="0.8"/></g>')
    # glassine pocket with one four-leaf clover
    gx, gy = 408, 360
    out.append(f'<g transform="rotate(6 {gx + 50} {gy + 60})">')
    out.append(f'<path d="{hg.org_rect(gx, gy, 104, 118, 1350, 0.4, 10, 3)}" fill="#E8EEE8" opacity="0.7" stroke="#A8B4A8" stroke-width="1.2"/>')
    out.append(trefoil(D, gx + 52, gy + 56, 30, 45, 1351, pal=("#7ABF5A", "#2E7A32", "#144A1A"), n=4))
    out.append(pline([(gx + 52, gy + 60), (gx + 56, gy + 90), (gx + 50, gy + 108)], "#4E6A2E", 2, 1352, 0.9, 1))
    out.append(f'<path d="{hg.org_rect(gx, gy, 104, 118, 1350, 0.4, 10, 3)}" fill="#FFFFFF" opacity="0.25"/>')
    out.append(f'<path d="M {gx} {gy + 2} L {gx + 52} {gy + 26} L {gx + 104} {gy + 2}" fill="none" stroke="#A8B4A8" stroke-width="1.2"/>')
    out.append(label(gx + 52, gy + 140, "ádh mór!", SERIF_IT, 22, "#2E6A3A"))
    out.append("</g>")
    # specimen label card
    out.append(f'<rect x="100" y="94" width="196" height="62" fill="#FFFDF6" stroke="#5A4A2A" stroke-width="1.2"/>')
    out.append(label(198, 120, "TRIFOLIUM DUBIUM", MONO, 16, "#3A2A10", ls=1, max_w=180))
    out.append(label(198, 144, "Co. Mhaigh Eo · Márta", SERIF_IT, 17, "#7A4A2A", max_w=180))
    out.append(letters(D, 418, 170, "seamróg", SERIF_IT, 76, "#1E6A3A", ["#2E8A4E", "#0E4024", "#3E9A5A"], 1360, max_w=220,
                       shadow="#FFFFFF", soff=(0.015, 0.025), angle=-40, hi="#9AD0A8"))
    out.append(label(418, 206, "THE SHAMROCK", JOS, 19, "#8A3A1A", ls=5, max_w=200))
    return finish_ie(D, out, 1361)



# ================================================================ 16. Glendalough — the round tower rising out of the morning mist
def round_tower(D, cx, base, top, w0, w1, seed, haze=0.0):
    """An Irish round tower: tapering granite drum in courses, a door high above the ground, four little windows
    under the conical stone cap; lit from the left."""
    rnd = random.Random(seed)
    hz = (lambda c: mix(c, "#D8C8D8", haze)) if haze else (lambda c: c)
    o = []
    body = [(cx - w0 / 2, base), (cx - w1 / 2, top), (cx + w1 / 2, top), (cx + w0 / 2, base)]
    o.append(painted(D, poly_pts(body, 14, seed, 0.4), (hz("#E8E0D8"), hz("#AFA8A2"), hz("#5E5A5A")), seed, sdir=(1, 0), sk=0.28, angle=-90, n=30, inkw=1.6, hi=0.4))
    cid = D.clip(f'<path d="{pd(body)}"/>')
    inner = []
    y = base
    while y > top:
        t = (base - y) / (base - top)
        half = lerp(w0, w1, t) / 2
        inner.append(f'<path d="M {cx - half:.1f} {y:.1f} Q {cx:.1f} {y + 2:.1f} {cx + half:.1f} {y:.1f}" stroke="{hz("#6A6460")}" stroke-width="0.9" fill="none" opacity="0.6"/>')
        x = cx - half + rnd.uniform(0, 8)
        while x < cx + half:
            inner.append(f'<path d="M {x:.1f} {y:.1f} l 0 -5" stroke="{hz("#6A6460")}" stroke-width="0.8" opacity="0.45"/>')
            x += rnd.uniform(6, 12)
        y -= 6
    inner.append(f'<rect x="{cx}" y="{top}" width="{w0}" height="{base - top}" fill="{hz("#2A2440")}" opacity="0.22"/>')
    o.append(f'<g {cid}>{"".join(inner)}</g>')
    # door high up, windows under the cap
    dy = base - (base - top) * 0.13
    o.append(f'<path d="M {cx - 5:.1f} {dy:.1f} L {cx - 5:.1f} {dy - 14:.1f} Q {cx:.1f} {dy - 20:.1f} {cx + 5:.1f} {dy - 14:.1f} L {cx + 5:.1f} {dy:.1f} Z" fill="{hz("#2A2228")}"/>')
    for k, dx in enumerate((-0.25, 0.15)):
        o.append(f'<rect x="{cx + dx * w1 - 2:.1f}" y="{top + 10}" width="4" height="9" fill="{hz("#2A2228")}"/>')
    o.append(f'<rect x="{cx - 2:.1f}" y="{lerp(base, top, 0.55):.1f}" width="3.4" height="7" fill="{hz("#2A2228")}"/>')
    cap = [(cx - w1 / 2 - 2, top + 2), (cx, top - (base - top) * 0.15), (cx + w1 / 2 + 2, top + 2)]
    o.append(painted(D, cap, (hz("#C8C0BA"), hz("#8A8480"), hz("#4A4646")), seed + 1, sdir=(1, 0.2), sk=0.25, angle=-60, n=8, inkw=1.4, hi=0.45))
    return "".join(o)


def high_cross(D, x, base, h, seed, haze=0.0):
    hz = (lambda c: mix(c, "#D8C8D8", haze)) if haze else (lambda c: c)
    pal = (hz("#C8C4BC"), hz("#8A8680"), hz("#46423E"))
    w = h * 0.16
    o = [cast(D, x + 6, base, w * 1.6, 5, strength=0.4, seed=seed)]
    o.append(painted(D, rect_pts(x - w * 0.8, base - h * 0.12, x + w * 0.8, base, 6, seed, 0.4), pal, seed, sk=0.2, n=4, inkw=1.2, hi=0.3))
    o.append(painted(D, rect_pts(x - w / 2, base - h, x + w / 2, base - h * 0.1, 8, seed + 1, 0.4), pal, seed + 1, sdir=(1, 0), sk=0.25, angle=-90, n=8, inkw=1.4, hi=0.4))
    cy = base - h * 0.74
    ring = ell_pts(x, cy, w * 1.25, w * 1.25, 0, 360, 24)[:-1]
    inner = ell_pts(x, cy, w * 0.9, w * 0.9, 0, 360, 24)[:-1]
    o.append(f'<path d="{smooth_closed(ring)} {smooth_closed(inner)}" fill-rule="evenodd" fill="{pal[1]}" stroke="{pal[2]}" stroke-width="1.2"/>')
    o.append(painted(D, rect_pts(x - w * 1.7, cy - w * 0.42, x + w * 1.7, cy + w * 0.42, 8, seed + 2, 0.4), pal, seed + 2, sdir=(1, 0.3), sk=0.25, n=6, inkw=1.4, hi=0.4))
    o.append(f'<circle cx="{x:.1f}" cy="{cy:.1f}" r="{w * 0.3:.1f}" fill="{pal[2]}" opacity="0.5"/>')
    for k in range(3):
        yy = base - h * (0.2 + k * 0.14)
        o.append(f'<rect x="{x - w * 0.32:.1f}" y="{yy - w * 0.5:.1f}" width="{w * 0.64:.1f}" height="{w * 0.5:.1f}" fill="none" stroke="{pal[2]}" stroke-width="1" opacity="0.6"/>')
    return "".join(o)


@design("glendalough")
def glendalough():
    D = Doc2("ie-gl")
    out = [sky(D, [(0, "#9A8EC0"), (0.45, "#E8B8B8"), (0.8, "#F8DCB0"), (1, "#FFF0C8")], 3, 420, ["#FFFFFF", "#C8A8C8", "#F8D8B8"], 60, angle=-3, sop=(0.05, 0.12))]
    out.append(soft_glow(D, 300, 300, 220, "#FFF4D0", 0.6))
    # the glacial valley: far hills at its head, steep wooded sides
    out.append(hill(D, ridge([(120, 300), (220, 268), (300, 280), (380, 262), (480, 300)], 1401, 4), 420, ("#C8B8D0", "#A898B8", "#7A6A90"), 1401, inkw=0))
    out.append(f'<path d="M 120 330 L 480 330 L 480 360 L 120 360 Z" fill="#D8D0E0"/>')
    out.append(wave_lines(1402, (170, 332, 430, 356), ["#FFFFFF", "#B8A8C8"], 20, L=(20, 40), w=1.4, amp=1))
    for side in (-1, 1):
        x_out = 300 + side * 330
        line = ridge([(x_out, 170 if side < 0 else 190), (300 + side * 200, 240), (300 + side * 90, 340)], 1403 + side, 6)
        poly = line + [(300 + side * 90, 420), (x_out, 420)]
        g = D.lin([(0, "#3E6A4A"), (1, "#2A4A36")], 0, 0, 0, 1)
        out.append(f'<path d="{smooth_closed(poly)}" fill="{g}"/>')
        rnd = random.Random(1404 + side)
        for k in range(70):
            t = rnd.random()
            px = lerp(x_out, 300 + side * 90, t) + rnd.uniform(-10, 10)
            ytop = lerp(170 if side < 0 else 190, 340, t)
            py = rnd.uniform(ytop + 8, 420)
            out.append(dab_crown(D, px, py, rnd.uniform(8, 14), rnd.uniform(6, 10), [("#6A9A6A", "#3E6A4A", "#1E3A2A"), ("#8AAA6A", "#5A7A3E", "#2E4A22")], 1410 + k, n=7, size=(3, 6), inkw=0, base=False))
    out.append(f'<rect y="300" width="600" height="160" fill="{D.lin([(0, "#FFFFFF", 0), (0.5, "#FFF6EE", 0.55), (1, "#FFFFFF", 0)])}"/>')
    # monastic site: St Kevin's church with its little belfry, the tower, the graveyard
    out.append(hill(D, ridge([(-10, 448), (200, 440), (400, 446), (610, 436)], 1420, 3), 620, ("#A8C888", "#6E9A5A", "#3E6A3A"), 1420, inkw=0))
    cb = 480
    out.append(painted(D, rect_pts(154, cb - 62, 272, cb, 12, 1421, 0.5), ("#D8D0C8", "#A8A098", "#5E5854"), 1421, sdir=(1, 0.3), sk=0.12, angle=-90, n=20, inkw=1.6, hi=0.3))
    roof = [(148, cb - 60), (213, cb - 132), (278, cb - 60)]
    out.append(painted(D, poly_pts(roof, 12, 1422, 0.4), ("#B8B0A8", "#7A746E", "#3E3A38"), 1422, sdir=(1, 0.2), sk=0.2, angle=-50, n=16, inkw=1.6, hi=0.35))
    for k in range(5):
        out.append(pline([(160 + k * 4, cb - 64 - k * 13), (266 - k * 4, cb - 64 - k * 13)], "#5E5854", 1, 1423 + k, 0.5, 1))
    out.append(round_tower(D, 172, cb - 92, cb - 124, 15, 13, 1424))
    out.append(f'<path d="M 200 {cb} L 200 {cb - 30} Q 210 {cb - 40} 220 {cb - 30} L 220 {cb} Z" fill="#2A2228"/>')
    out.append(round_tower(D, 384, cb + 8, 232, 44, 34, 1425))
    for k, (x, h) in enumerate(((440, 40), (470, 30), (500, 46), (300, 34), (520, 28))):
        out.append(painted(D, rect_pts(x - 7, cb + 14 - h, x + 7, cb + 14, 6, 1430 + k, 0.4), STONE, 1430 + k, sk=0.2, n=3, inkw=1.1, hi=0.4))
    out.append(f'<rect y="440" width="600" height="60" fill="{D.lin([(0, "#FFFFFF", 0), (0.5, "#FFFFFF", 0.45), (1, "#FFFFFF", 0)])}"/>')
    # foreground: a ringed high cross, grass and a gate post
    out.append(hill(D, ridge([(-10, 520), (200, 512), (400, 520), (610, 506)], 1440, 3), 620, ("#B8D488", "#5E9A3E", "#2A5A22"), 1440, inkw=1.4, inkop=0.4))
    out.append(high_cross(D, 102, 570, 172, 1441))
    out.append(high_cross(D, 524, 548, 84, 1442, haze=0.1))
    out.append(grass(1443, (0, 520, 600, 600), ["#2A5A22", "#6EA84A", "#A8D070"], n=120, h=(6, 16)))
    for k in range(4):
        out.append(seagull(240 + k * 30, 230 + (k % 2) * 12, 6, "#4A3A5A", 0.7))
    out.append(letters(D, 300, 124, "Glendalough", DMS, 84, "#3A2A5A", ["#5A3E7A", "#22183A", "#6A4E8A"], 1444, max_w=460,
                       shadow="#FFF0E0", soff=(0.02, 0.03), angle=-40, wob=0.5))
    out.append(ruled(300, 168, "GLEANN DÁ LOCH · CO. WICKLOW", "#7A3A4A", font=JOS, size=19, ls=4, line_w=22, gap=10, max_w=390))
    return finish_ie(D, out, 1445, op=0.8)


# ================================================================ 17. Galway — painted shopfronts on Quay Street
def shopfront(D, x0, x1, roof, base, seed, wall, sign, sign_col, goods):
    rnd = random.Random(seed)
    o = []
    w = x1 - x0
    o.append(painted(D, rect_pts(x0, roof, x1, base, 16, seed, 0.5), P3(wall, 0.3, 0.3), seed, sdir=(1, 0.3), sk=0.06, angle=-90, n=int(w * (base - roof) / 150), inkw=1.6, hi=0.25))
    # cornice and chimney
    o.append(painted(D, rect_pts(x0 - 4, roof - 8, x1 + 4, roof + 2, 10, seed + 1, 0.4), ("#F2EEE4", "#D8D2C4", "#8A8478"), seed + 1, sk=0.2, angle=0, n=6, inkw=1.2, hi=0.4))
    cx_ = x0 + w * rnd.uniform(0.2, 0.7)
    o.append(painted(D, rect_pts(cx_, roof - 30, cx_ + 18, roof - 8, 6, seed + 2, 0.3), ("#E8A07A", "#B8603A", "#6A2A10"), seed + 2, sk=0.2, n=3, inkw=1, hi=0.3))
    for k in range(2):
        o.append(f'<rect x="{cx_ + 2 + k * 8}" y="{roof - 36}" width="5" height="7" fill="#8A4A2A"/>')
    # upper windows
    shop_top = base - 128
    rows = 2
    for j in range(rows):
        for i in range(2):
            wx = x0 + w * (0.18 + i * 0.4)
            wy = roof + 18 + j * (shop_top - roof - 20) / rows
            ww, wh = w * 0.26, (shop_top - roof - 20) / rows - 16
            o.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{ww:.1f}" height="{wh:.1f}" fill="#2E3A4A" stroke="#FBFBF6" stroke-width="3"/>')
            o.append(f'<path d="M {wx:.1f} {wy + wh / 2:.1f} L {wx + ww:.1f} {wy + wh / 2:.1f} M {wx + ww / 2:.1f} {wy:.1f} L {wx + ww / 2:.1f} {wy + wh:.1f}" stroke="#FBFBF6" stroke-width="1.6"/>')
            o.append(f'<path d="M {wx + 3:.1f} {wy + 3:.1f} l {ww * 0.3:.1f} 0 l {-ww * 0.25:.1f} {wh * 0.4:.1f} Z" fill="#FFFFFF" opacity="0.25"/>')
            o.append(f'<rect x="{wx - 3:.1f}" y="{wy + wh:.1f}" width="{ww + 6:.1f}" height="4" fill="#EEE8DC"/>')
            if j == 1 and rnd.random() < 0.6:
                for k in range(4):
                    o.append(f'<circle cx="{wx + 4 + k * ww / 4:.1f}" cy="{wy + wh - 2:.1f}" r="4" fill="{rnd.choice(["#E8304A", "#F6C21C", "#FFFFFF", "#E870A0"])}"/>')
    # shopfront: pilasters, fascia with gilt lettering, window and door
    sc = dk(sign_col, 0.1)
    o.append(painted(D, rect_pts(x0 + 2, shop_top, x1 - 2, base, 10, seed + 3, 0.4), P3(sc, 0.3, 0.3), seed + 3, sk=0.1, n=10, inkw=1.6, hi=0.3))
    o.append(painted(D, rect_pts(x0 + 4, shop_top + 4, x1 - 4, shop_top + 34, 10, seed + 4, 0.3), P3(dk(sign_col, 0.35), 0.25, 0.3), seed + 4, sk=0.1, angle=0, n=6, inkw=1.2, hi=0.3))
    fs = fit_size(sign, CINZEL, 22, w - 26, 2)
    o.append(f'<text x="{(x0 + x1) / 2 + 1.2:.1f}" y="{shop_top + 26.5:.1f}" text-anchor="middle" {CINZEL} font-size="{fs}" letter-spacing="2" fill="#2A1A0A">{esc(sign)}</text>')
    o.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{shop_top + 25:.1f}" text-anchor="middle" {CINZEL} font-size="{fs}" letter-spacing="2" fill="#F6D27A">{esc(sign)}</text>')
    wx0, wx1 = x0 + 10, x0 + w * 0.62
    o.append(f'<rect x="{wx0:.1f}" y="{shop_top + 42:.1f}" width="{wx1 - wx0:.1f}" height="{base - shop_top - 52:.1f}" fill="#F6E8C8"/>')
    o.append(D.glow((wx0 + wx1) / 2, base - 40, 40, "#FFE6A0", 0.5))
    o.append(goods(wx0, shop_top + 42, wx1, base - 10))
    o.append(f'<rect x="{wx0:.1f}" y="{shop_top + 42:.1f}" width="{wx1 - wx0:.1f}" height="{base - shop_top - 52:.1f}" fill="none" stroke="#FBFBF6" stroke-width="2.4"/>')
    o.append(f'<path d="M {wx0 + 4:.1f} {shop_top + 46:.1f} l 16 0 l -12 30 Z" fill="#FFFFFF" opacity="0.3"/>')
    dx0 = x0 + w * 0.68
    o.append(f'<path d="{hg.org_rect(dx0, shop_top + 42, w * 0.24, base - shop_top - 42, seed + 5, 0.3, 8, 1)}" fill="{dk(sign_col, 0.45)}"/>')
    o.append(f'<circle cx="{dx0 + w * 0.2:.1f}" cy="{base - 40:.1f}" r="2" fill="#F6D27A"/>')
    o.append(f'<path d="M {dx0 + 3:.1f} {shop_top + 60:.1f} Q {dx0 + w * 0.12:.1f} {shop_top + 46:.1f} {dx0 + w * 0.24 - 3:.1f} {shop_top + 60:.1f}" stroke="#F6D27A" stroke-width="1.4" fill="none"/>')
    return "".join(o)


@design("galway")
def galway():
    D = Doc2("ie-gw")
    out = [sky(D, [(0, "#7EB0DA"), (0.7, "#CDE2EE"), (1, "#F2F0E6")], 3, 420, ["#FFFFFF", "#A8C8E4"], 50, angle=-3, sop=(0.06, 0.14))]
    out.append(puff_cloud(D, 470, 214, 130, 1501, ("#FFFFFF", "#F6F4F0", "#B8C4D4")))
    out.append(puff_cloud(D, 120, 206, 100, 1502, ("#FFFFFF", "#F6F4F0", "#B8C4D4")))
    base = 512

    def bread(x0, y0, x1, y1):
        o = []
        for k in range(3):
            o.append(f'<path d="{blob(x0 + 14 + k * (x1 - x0 - 20) / 3, y1 - 16, 13, 10, 1510 + k, 0.1, 10)}" fill="#C8863E" stroke="#6A3A10" stroke-width="1"/>')
            o.append(f'<path d="M {x0 + 8 + k * (x1 - x0 - 20) / 3:.1f} {y1 - 18:.1f} l 12 0" stroke="#F2D8A8" stroke-width="1.4"/>')
        o.append(f'<path d="M {x0} {y1 - 34} L {x1} {y1 - 34}" stroke="#8A6A40" stroke-width="2"/>')
        for k in range(4):
            o.append(f'<circle cx="{x0 + 10 + k * (x1 - x0 - 16) / 4:.1f}" cy="{y1 - 42:.1f}" r="6" fill="#E8B060" stroke="#8A5A20" stroke-width="1"/>')
        return "".join(o)

    def books(x0, y0, x1, y1):
        rnd = random.Random(1520)
        o = []
        for row in (y1 - 4, y1 - 38):
            x = x0 + 4
            while x < x1 - 8:
                bw = rnd.uniform(5, 9)
                bh = rnd.uniform(22, 30)
                o.append(f'<rect x="{x:.1f}" y="{row - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{rnd.choice(["#C8302A", "#2E5A9A", "#2E7A4A", "#E8B040", "#6A3A7A", "#3A2A1A"])}"/>')
                x += bw + 1
            o.append(f'<path d="M {x0} {row} L {x1} {row}" stroke="#6A4A2A" stroke-width="2"/>')
        return "".join(o)

    def music(x0, y0, x1, y1):
        o = [f'<ellipse cx="{(x0 + x1) / 2 - 6:.1f}" cy="{y1 - 30:.1f}" rx="22" ry="22" fill="#E8D4A8" stroke="#6A3A10" stroke-width="3"/>']
        o.append(f'<path d="{smooth_closed([(x1 - 14, y0 + 10), (x1 - 4, y0 + 20), (x1 - 12, y1 - 14), (x1 - 24, y1 - 10), (x1 - 22, y0 + 30)])}" fill="#B8602A" stroke="#4A1A08" stroke-width="1.2"/>')
        return "".join(o)

    def tea(x0, y0, x1, y1):
        o = []
        for k in range(3):
            x = x0 + 12 + k * (x1 - x0 - 20) / 3
            o.append(f'<path d="M {x - 8:.1f} {y1 - 22:.1f} L {x + 8:.1f} {y1 - 22:.1f} L {x + 6:.1f} {y1 - 8:.1f} L {x - 6:.1f} {y1 - 8:.1f} Z" fill="#FFFFFF" stroke="#2E5AB8" stroke-width="1.4"/>')
        o.append(f'<path d="{blob((x0 + x1) / 2, y1 - 48, 16, 12, 1530, 0.05, 12)}" fill="#2E7A4A" stroke="#14401E" stroke-width="1.2"/>')
        return "".join(o)

    def knits(x0, y0, x1, y1):
        o = [f'<path d="M {x0 + 8} {y1 - 6} L {x0 + 10} {y0 + 24} L {x0 + 22} {y0 + 16} L {x1 - 22} {y0 + 16} L {x1 - 10} {y0 + 24} L {x1 - 8} {y1 - 6} Z" fill="#F2E8D0" stroke="#A89670" stroke-width="1.4"/>']
        for k in range(3):
            xx = x0 + 18 + k * (x1 - x0 - 36) / 2
            o.append(f'<path d="M {xx:.1f} {y0 + 22} L {xx:.1f} {y1 - 8}" stroke="#C8B890" stroke-width="3" stroke-dasharray="3 2"/>')
        return "".join(o)

    shops = [(-6, 112, 256, "#E85A4A", "BÁCÚS", "#2E5A3A", bread), (112, 228, 236, "#F2C24A", "LEABHAIR", "#2E3A6A", books),
             (228, 340, 250, "#4E86C8", "CEOL", "#7A1A1A", music), (340, 456, 230, "#5EA86A", "TAE", "#3A1A4A", tea),
             (456, 606, 252, "#E89AB0", "SIOPA", "#1E4A6A", knits)]
    for k, (a, b, roof, wall, sign, scol, goods) in enumerate(shops):
        out.append(shopfront(D, a, b, roof, base, 1540 + k * 10, wall, sign, scol, goods))
    # bunting criss-crossing the street
    rnd = random.Random(1590)
    for (x0, y0, x1, y1, sag) in ((-10, 268, 610, 280, 40),):
        n = 18
        for i in range(n):
            t0, t1 = i / n, (i + 0.8) / n
            p0 = (lerp(x0, x1, t0), lerp(y0, y1, t0) + sag * 4 * t0 * (1 - t0))
            p1 = (lerp(x0, x1, t1), lerp(y0, y1, t1) + sag * 4 * t1 * (1 - t1))
            tip = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + 22)
            col = ["#2E8A4E", "#FFFFFF", "#F2872A", "#E8304A", "#F6C21C", "#2E6AC8"][i % 6]
            out.append(f'<path d="{smooth_closed([p0, p1, tip])}" fill="{col}" stroke="#3A2A1A" stroke-width="0.8"/>')
        out.append(ink(smooth_open([(lerp(x0, x1, t), lerp(y0, y1, t) + sag * 4 * t * (1 - t)) for t in [i / 30 for i in range(31)]]), "#3A2A1A", 1.4, 1591, 1, 0.9))
    # the cobbled street and a few people
    out.append(f'<path d="M -10 {base} L 610 {base} L 610 610 L -10 610 Z" fill="#8A8278"/>')
    for j in range(7):
        y = base + 6 + j * (6 + j * 2)
        x = -10 + (j % 2) * 10
        while x < 610:
            ww = 16 + j * 3
            out.append(f'<path d="{blob(x, y, ww / 2 - 1, 3 + j * 0.8, 1600 + j * 50 + int(x), 0.15, 8)}" fill="{rnd.choice(["#A8A096", "#9A9288", "#B8B0A4"])}" stroke="#5A544C" stroke-width="0.8"/>')
            x += ww
    out.append(f'<rect y="{base}" width="600" height="8" fill="#C8C0B4"/>')
    out.append(figures.person(150, 572, 74, "walk", 1, {"top_kind": "coat", "top": "#2E5A8A", "bottom": "#3A3A44", "hair_style": "long", "hair": "#C86A2A", "form": "f"}, seed=1660, light=-1))
    out.append(figures.person(420, 566, 70, "walk", -1, {"top_kind": "jacket", "top": "#7A3A2A", "bottom": "#2A2A34", "hat_kind": "cap", "hat": "#3A3A3A", "form": "m"}, seed=1661, light=-1))
    out.append(figures.person(470, 572, 46, "child_walk", -1, {"top": "#F6C21C", "bottom": "#2E4A8A"}, seed=1662, light=-1))
    out.append(letters(D, 300, 128, "Galway", SERIF_IT, 116, "#183A5A", ["#2A5A86", "#0C2440", "#3A6A96"], 1663, max_w=360,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#A8C8E8"))
    out.append(ruled(300, 172, "GAILLIMH · CITY OF THE TRIBES", "#8A2A1A", font=JOS, size=19, ls=4, line_w=22, gap=10, max_w=390))
    return finish_ie(D, out, 1664)


# ================================================================ 18. ceol agus craic — fiddle, bodhrán and whistle on the session table
def fiddle(D, cx, cy, s, ang, seed):
    """A fiddle lying on the table: figure-of-eight body with purfling, f-holes, ebony fingerboard, bridge,
    tailpiece, strings, pegbox and scroll; amber varnish. Drawn with its long axis vertical, then rotated."""
    rh = [(0, -92), (24, -90), (42, -80), (48, -62), (46, -44), (38, -34), (32, -26), (30, -6), (32, 14), (40, 22), (52, 32), (58, 52), (56, 72), (44, 86), (24, 92), (0, 94)]
    pts = rh + [(-x, y) for x, y in rh[::-1][1:-1]]
    o = []
    o.append(f'<path d="{smooth_closed(shift(pts, 6, 8))}" fill="#1A0A04" opacity="0.35"/>')
    o.append(painted(D, pts, ("#F2A84E", "#B8601E", "#5A2408"), seed, sdir=(0.5, 0.6), sk=0.18, angle=-90, n=40, slen=(20, 60), sw=(0.8, 2), inkw=1.8, inkop=0.8, hi=0.5, hik=0.06))
    o.append(ink(smooth_closed([(x * 0.92, y * 0.94) for x, y in pts]), "#2A1006", 1.2, seed, 1, 0.7))
    for sg in (-1, 1):
        f = [(sg * 22, -14), (sg * 18, 0), (sg * 22, 14), (sg * 20, 28)]
        o.append(ink(smooth_open(f), "#1A0804", 3, seed + sg, 1, 1))
        o.append(f'<circle cx="{sg * 22}" cy="-15" r="2.4" fill="#1A0804"/><circle cx="{sg * 20}" cy="29" r="2.4" fill="#1A0804"/>')
    o.append(f'<path d="{smooth_closed([(-16, 50), (16, 50), (12, 88), (-12, 88)])}" fill="#1A1210"/>')
    o.append(f'<path d="{smooth_closed([(-22, 72), (-6, 76), (-8, 92), (-26, 88)])}" fill="#2A1A10"/>')
    o.append(f'<path d="{smooth_closed([(-9, -210), (9, -210), (9, 20), (-9, 20)])}" fill="#2A1A10"/>')
    o.append(f'<path d="M -6 -206 L -6 18" stroke="#5A4A3A" stroke-width="1.4" opacity="0.6"/>')
    o.append(f'<path d="{smooth_closed([(-18, 38), (18, 38), (16, 44), (-16, 44)])}" fill="#E8C890" stroke="#6A4A20" stroke-width="1"/>')
    for k in range(4):
        x = -6 + k * 4
        o.append(f'<path d="M {x * 1.4:.1f} 52 L {x:.1f} 41 L {x * 0.6:.1f} -226" stroke="#E8E4DC" stroke-width="0.9"/>')
    o.append(painted(D, [(-8, -210), (8, -210), (9, -248), (-9, -248)], ("#F2A84E", "#B8601E", "#5A2408"), seed + 1, sk=0.2, n=4, inkw=1.4, hi=0.4))
    for k in range(2):
        for sg in (-1, 1):
            o.append(f'<path d="{smooth_closed([(sg * 8, -222 - k * 14), (sg * 22, -224 - k * 14), (sg * 22, -216 - k * 14), (sg * 8, -216 - k * 14)])}" fill="#2A1A10"/>')
    sc = [(0 + (11 - j * 0.8) * math.cos(math.radians(j * 40 - 90)), -258 + (11 - j * 0.8) * math.sin(math.radians(j * 40 - 90))) for j in range(12)]
    o.append(painted(D, blob_pts(0, -258, 12, 12, seed + 2, 0.05, 12), ("#F2A84E", "#B8601E", "#5A2408"), seed + 2, sk=0.2, n=3, inkw=1.4, hi=0.4))
    o.append(ink(smooth_open(sc), "#5A2408", 1.6, seed, 1, 0.8))
    o.append(taper([(-30, -70), (-38, -40)], 4, 2, "#FFE8B8", 0.6))
    return f'<g transform="translate({cx} {cy}) rotate({ang}) scale({s})">' + "".join(o) + "</g>"


def bodhran(D, cx, cy, r, seed):
    rnd = random.Random(seed)
    o = [cast(D, cx + 14, cy + r * 1.02, r * 0.9, 12, strength=0.5, seed=seed)]
    rim = ell_pts(cx, cy, r, r * 1.02, 0, 360, 48)[:-1]
    o.append(f'<path d="{smooth_closed(shift(rim, 10, 4))}" fill="#6A3A18"/>')
    o.append(painted(D, rim, ("#E8B070", "#A8662E", "#5A2E10"), seed, sk=0.1, n=10, inkw=2, hi=0.4))
    face = ell_pts(cx, cy, r * 0.9, r * 0.92, 0, 360, 48)[:-1]
    o.append(painted(D, face, ("#FFF4DC", "#EED8AE", "#B89A6A"), seed + 1, sdir=(0.6, 0.6), sk=0.08, angle=-40, n=40, inkw=1.4, hi=0.4))
    cid = D.clip(f'<path d="{smooth_closed(face)}"/>')
    inner = []
    for _ in range(14):
        inner.append(f'<path d="{blob(cx + rnd.uniform(-r * 0.7, r * 0.7), cy + rnd.uniform(-r * 0.7, r * 0.7), rnd.uniform(10, 26), rnd.uniform(6, 16), rnd.randint(0, 999), 0.3, 10)}" fill="#C8A070" opacity="{rnd.uniform(0.1, 0.25):.2f}"/>')
    # a painted triskele in the middle
    for k in range(3):
        a0 = k * 120
        sp = [(cx + (4 + j * 2.6) * math.cos(math.radians(a0 + j * 28)), cy + (4 + j * 2.6) * math.sin(math.radians(a0 + j * 28))) for j in range(14)]
        inner.append(f'<path d="{smooth_open(sp)}" fill="none" stroke="#2E6A4A" stroke-width="6" stroke-linecap="round"/>')
    inner.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.62:.1f}" fill="none" stroke="#2E6A4A" stroke-width="3"/>')
    inner.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.68:.1f}" fill="none" stroke="#C8302A" stroke-width="1.6"/>')
    inner.append(f'<path d="{blob(cx - r * 0.35, cy - r * 0.4, r * 0.3, r * 0.15, seed + 5, 0.2, 10, -40)}" fill="#FFFFFF" opacity="0.35"/>')
    o.append(f'<g {cid}>{"".join(inner)}</g>')
    for k in range(30):
        a = math.radians(k * 12)
        o.append(f'<circle cx="{cx + math.cos(a) * r * 0.95:.1f}" cy="{cy + math.sin(a) * r * 0.97:.1f}" r="2.2" fill="#E8D8B0" stroke="#3A2A10" stroke-width="0.8"/>')
    return "".join(o)


@design("ceol-agus-craic")
def ceol_agus_craic():
    D = Doc2("ie-ce")
    out = [wood_planks(D, 0, 330, 1701, ("#4E7A5E", "#2E5440", "#14301E"), 8, vertical=True)]
    out.append(soft_glow(D, 140, 150, 300, "#FFD88A", 0.4))
    out.append(wood_planks(D, 330, 600, 1702, MAHOG, 4))
    out.append(f'<rect y="324" width="600" height="10" fill="#140804" opacity="0.6"/>')
    out.append(soft_glow(D, 300, 430, 300, "#FFB860", 0.25))
    # sheet of tunes under the fiddle
    sheet = rot([(80, 380), (300, 366), (312, 560), (92, 576)], 196, 470, -6)
    out.append(painted(D, poly_pts(sheet, 20, 1703, 0.6), ("#FFFDF4", "#F4ECD8", "#C8B894"), 1703, sk=0.06, n=10, inkw=1.2, hi=0.3))
    for k in range(5):
        for j in range(5):
            y = 404 + k * 32 + j * 4
            out.append(f'<path d="M {100 + k * 2} {y - k * 1.5:.1f} L {290 + k * 2} {y - 14 - k * 1.5:.1f}" stroke="#6A5A4A" stroke-width="0.7" opacity="0.6" transform="rotate(-6 196 470)"/>')
    rnd = random.Random(1704)
    for k in range(14):
        x, y = rnd.uniform(110, 280), rnd.uniform(400, 540)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="3" ry="2.2" fill="#3A2A1A" transform="rotate(-25 {x:.1f} {y:.1f})"/><path d="M {x + 2.6:.1f} {y:.1f} l 0 -12" stroke="#3A2A1A" stroke-width="1"/>')
    out.append(bodhran(D, 414, 362, 120, 1705))
    # tipper
    out.append(taper([(330, 560), (420, 520)], 8, 8, "#C8925A") + taper([(330, 560), (420, 520)], 2, 2, "#F2D2A0", 0.7))
    for (x, y) in ((328, 561), (422, 519)):
        out.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#B07A44" stroke="#5A3410" stroke-width="1"/>')
    # bow, under the fiddle
    out.append(taper([(76, 424), (500, 572)], 3.4, 2.6, "#5A2A10") + taper([(76, 430), (500, 578)], 1.4, 1.4, "#F2EEE4", 0.9))
    out.append(painted(D, rot(rect_pts(62, 416, 98, 432, 8, 1707, 0.3), 80, 424, 19), ("#3A2A20", "#1A1210", "#000000"), 1707, sk=0.1, n=2, inkw=1, hi=0.5))
    out.append(fiddle(D, 246, 470, 1.0, -40, 1706))
    # tin whistle
    out.append(taper([(360, 586), (560, 560)], 10, 10, "#D8DCE4"))
    out.append(taper([(360, 583), (560, 557)], 2.4, 2.4, "#FFFFFF", 0.8))
    out.append(taper([(340, 589), (372, 585)], 13, 12, "#2E6A4A"))
    for k in range(6):
        x = 420 + k * 18
        y = 578 - (x - 360) * 0.13
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="3" ry="2.4" fill="#2A2A30"/>')
    out.append(letters(D, 300, 130, "ceol agus craic", SERIF_IT, 92, "#FFF2D8", ["#FFFFFF", "#F2DCB4", "#FFE8C0"], 1708, max_w=470,
                       shadow="#0A1A10", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 178, "TUNES, TEA & GOOD COMPANY", "#F6D27A", font=JOS, size=20, ls=5, line_w=24, gap=10))
    return finish_ie(D, out, 1709)



# ================================================================ 19. may the road rise to meet you — the old blessing, a boreen to the sea
@design("may-the-road-rise")
def may_the_road_rise():
    D = Doc2("ie-mr")
    out = [paper(D.nid(), "#F6EEDA", FLECK, 1901)]
    out.append(blooms(1902, ["#D8E0C0", "#E8D8B8"], 6, (0, 0, 600, 600), (100, 200), (0.06, 0.1)))
    # arched vignette
    ax0, ax1, atop, abot = 108, 492, 2, 338
    r = (ax1 - ax0) / 2
    arch = [(ax0, abot), (ax0, atop + r)] + [(300 + r * math.cos(math.radians(a)), atop + r - r * 0.62 * math.sin(math.radians(a))) for a in range(180, -1, -10)] + [(ax1, atop + r), (ax1, abot)]
    arch = [(x, y) for x, y in arch]
    ad = pd(arch)
    cid = D.clip(f'<path d="{ad}"/>')
    v = [sky(D, [(0, "#9CC4E4"), (0.5, "#F2E2C8"), (1, "#FFD8A0")], 3, 600, ["#FFFFFF", "#F2C8A0"], 40, sop=(0.05, 0.12))]
    v.append(soft_glow(D, 380, 216, 120, "#FFF2C0", 0.8))
    v.append(f'<circle cx="380" cy="216" r="18" fill="#FFF6D0"/>')
    v.append(f'<path d="M 108 222 L 492 220 L 492 238 L 108 240 Z" fill="#7AA8C8"/>')
    v.append(wave_lines(1903, (300, 222, 492, 236), ["#FFFFFF", "#FFE8B0"], 20, L=(6, 16), w=1.4, amp=1))
    v.append(hill(D, ridge([(100, 236), (200, 226), (300, 240), (420, 230), (500, 238)], 1904, 3), 340, ("#A8C8A0", "#7AA470", "#4E7A4A"), 1904, inkw=0, n=30))
    v.append(hill(D, ridge([(100, 270), (230, 252), (360, 262), (500, 246)], 1905, 4), 340, ("#B8D88A", "#7AAE52", "#3E7A32"), 1905, inkw=1, inkop=0.3, n=40))
    v.append(hill(D, ridge([(100, 300), (250, 286), (400, 296), (500, 284)], 1906, 4), 340, ("#C8E08A", "#86B850", "#4A7A2E"), 1906, inkw=1, inkop=0.3, n=40))
    for k, y in enumerate((262, 276, 292, 310)):
        v.append(pline([(108, y + (k % 2) * 4), (300, y - 4), (492, y + 2)], "#5A6A50", 1.2 + k * 0.4, 1907 + k, 0.55, 1))
    # the winding road, narrowing to the sea
    ys = [346 - i * 4 for i in range(26)]
    def xc(y):
        t = (346 - y) / 100
        return 300 + 34 * math.sin(t * 5.2) * (1 - t * 0.5)
    def hw(y):
        return max(1.5, 46 * ((y - 244) / 102) ** 1.4)
    road = [(xc(y) - hw(y), y) for y in ys] + [(xc(y) + hw(y), y) for y in ys[::-1]]
    v.append(painted(D, road, ("#F2E2C0", "#D8C49A", "#9A8460"), 1911, sk=0.05, angle=-80, n=30, inkw=0.8, inkop=0.4, hi=0.3))
    for side in (-1, 1):
        v.append(pline([(xc(y) + side * (hw(y) + 2), y) for y in ys], "#6A6A60", 1.6, 1930 + side, 0.7, 1))
        v.append(pline([(xc(y) + side * (hw(y) + 2), y - 1.5) for y in ys], "#E8E8E0", 0.9, 1932 + side, 0.6, 1))
    v.append(cottage_small(D, 172, 270, 36, 18, 1912, roof="thatch", haze=0.1))
    v.append(cottage_small(D, 396, 256, 26, 13, 1913, roof="slate", haze=0.25, smoke=False))
    for k, (x, y) in enumerate(((140, 330), (460, 320), (420, 290), (210, 296))):
        v.append(dab_crown(D, x, y - 14, 18, 14, [("#8ABA5A", "#3E7A32", "#1E4A1E")], 1914 + k, n=24, size=(3, 6), inkw=0.8))
        v.append(taper([(x, y), (x + 1, y - 8)], 3, 2, "#4A3A2A"))
    for (x, y, sz) in ((250, 150, 7), (272, 160, 5)):
        v.append(seagull(x, y, sz, "#4A4A5A", 0.8))
    out.append(f'<g {cid}>{"".join(v)}</g>')
    out.append(ink(ad, "#5A3A1A", 2.6, 1915, 2, 0.8))
    out.append(f'<path d="{pd([(x + (1 if x > 300 else -1) * 8, y - (6 if y < abot else -6)) for x, y in arch])}" fill="none" stroke="#C8963A" stroke-width="1.6" opacity="0.8"/>')
    # keystone shamrock
    for k in range(3):
        a = -90 + k * 120
        out.append(painted(D, heart_d(300 + math.cos(math.radians(a)) * 9, atop + r * 0.38 + math.sin(math.radians(a)) * 9 - 4, 10, a + 90), EMER, 1916 + k, sk=0.15, n=3, inkw=1.2, hi=0.4))
    # the blessing
    out.append(letters(D, 300, 404, "May the road", SERIF_IT, 66, "#1E5A3A", ["#2E7A4E", "#0E3E24", "#3E8A5A"], 1917, max_w=430, wob=0.6, hi="#8ACB9A"))
    out.append(letters(D, 300, 468, "rise to meet you", SERIF_IT, 66, "#1E5A3A", ["#2E7A4E", "#0E3E24", "#3E8A5A"], 1918, max_w=440, wob=0.6, hi="#8ACB9A"))
    out.append(ruled(300, 512, "MAY THE WIND BE ALWAYS AT YOUR BACK", "#8A3A1A", font=JOS, size=17, ls=2, line_w=12, gap=8, max_w=420))
    return finish_ie(D, out, 1919)


# ================================================================ 20. a grand drying day — the washing out on the line
def garment(D, kind, x, y, w, h, sway, seed, col):
    """A piece of washing pegged at (x..x+w, y), blown sideways by `sway`."""
    rnd = random.Random(seed)
    o = []
    if kind == "sheet":
        pts = [(x, y), (x + w, y), (x + w + sway * 1.2, y + h * 0.5), (x + w + sway * 1.6, y + h), (x + w * 0.5 + sway * 1.5, y + h * 0.94), (x + sway * 1.3, y + h * 1.02), (x + sway * 0.6, y + h * 0.5)]
        o.append(painted(D, pts, col, seed, sdir=(0.4, 1), sk=0.12, angle=80, n=24, inkw=1.4, hi=0.4))
        cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
        o.append(f'<g {cid}>' + "".join(taper([(x + w * t + 4, y + 4), (x + w * t + sway * 0.8, y + h * 0.5), (x + w * t + sway * 1.4 - 6, y + h)], 3, 8, dk(col[1], 0.2), 0.35) for t in (0.3, 0.65)) + "</g>")
    elif kind == "jumper":
        pts = [(x, y), (x + w, y), (x + w + w * 0.5 + sway, y + h * 0.45), (x + w + w * 0.38 + sway, y + h * 0.56), (x + w + sway * 0.8, y + h * 0.4), (x + w + sway, y + h),
               (x + sway, y + h), (x + sway * 0.6, y + h * 0.4), (x - w * 0.36 + sway * 0.4, y + h * 0.56), (x - w * 0.5 + sway * 0.4, y + h * 0.45)]
        o.append(painted(D, pts, col, seed, sdir=(0.4, 1), sk=0.12, angle=-90, n=16, inkw=1.4, hi=0.35))
        for t in (0.3, 0.5, 0.7):
            o.append(pline([(x + w * t, y + 6), (x + w * t + sway * 0.8, y + h - 4)], dk(col[1], 0.3), 2, seed, 0.5, 1))
    elif kind == "towel":
        pts = [(x, y), (x + w, y), (x + w + sway, y + h), (x + sway, y + h)]
        o.append(painted(D, poly_pts(pts, 10, seed, 0.5), col, seed, sk=0.12, angle=-90, n=8, inkw=1.2, hi=0.35))
        for t in (0.2, 0.28, 0.75, 0.83):
            o.append(pline([(x + 2 + sway * t, y + h * t), (x + w - 2 + sway * t, y + h * t)], "#FFFFFF", 2.4, seed, 0.85, 1))
    elif kind == "shirt":
        pts = [(x, y), (x + w, y), (x + w + w * 0.4 + sway, y + h * 0.6), (x + w + w * 0.25 + sway, y + h * 0.68), (x + w + sway * 0.8, y + h * 0.45), (x + w + sway, y + h),
               (x + sway, y + h), (x + sway * 0.6, y + h * 0.45), (x - w * 0.25 + sway * 0.4, y + h * 0.68), (x - w * 0.4 + sway * 0.4, y + h * 0.6)]
        o.append(painted(D, pts, col, seed, sk=0.12, angle=-90, n=12, inkw=1.3, hi=0.35))
        cid = D.clip(f'<path d="{smooth_closed(pts)}"/>')
        o.append(f'<g {cid}>' + "".join(f'<path d="M {x - 20 + k * 7:.1f} {y} L {x - 20 + k * 7 + sway:.1f} {y + h}" stroke="#FFFFFF" stroke-width="2" opacity="0.7"/>' for k in range(int(w / 7) + 8)) + "</g>")
        o.append(pline([(x + w / 2, y + 2), (x + w / 2 + sway, y + h - 2)], dk(col[1], 0.3), 1.2, seed, 0.6, 1))
    elif kind == "socks":
        for k in range(2):
            sx = x + k * w * 0.6
            sp = [(sx, y), (sx + w * 0.34, y), (sx + w * 0.36 + sway * 0.6, y + h * 0.7), (sx + w * 0.7 + sway, y + h * 0.82), (sx + w * 0.66 + sway, y + h), (sx + sway * 0.6, y + h * 0.92)]
            o.append(painted(D, sp, col, seed + k, sk=0.12, n=4, inkw=1.1, hi=0.35))
            o.append(f'<rect x="{sx:.1f}" y="{y:.1f}" width="{w * 0.34:.1f}" height="5" fill="#FFFFFF" opacity="0.7"/>')
    elif kind == "dress":
        pts = [(x + w * 0.2, y), (x + w * 0.8, y), (x + w * 0.85 + sway * 0.4, y + h * 0.35), (x + w * 1.1 + sway, y + h), (x - w * 0.1 + sway, y + h), (x + w * 0.15 + sway * 0.4, y + h * 0.35)]
        o.append(painted(D, pts, col, seed, sk=0.12, n=8, inkw=1.2, hi=0.35))
        for _ in range(12):
            px, py = x + rnd.uniform(0.1, 0.9) * w + sway * 0.6, y + rnd.uniform(0.3, 0.9) * h
            o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2" fill="#FFFFFF" opacity="0.85"/>')
    # pegs
    for px in (x + 4, x + w - 4):
        o.append(f'<rect x="{px - 2.5:.1f}" y="{y - 8:.1f}" width="5" height="13" rx="1.5" fill="#D8A86A" stroke="#6A4A20" stroke-width="0.8"/>')
    return "".join(o)


@design("grand-drying-day")
def grand_drying_day():
    D = Doc2("ie-dd")
    out = [sky(D, [(0, "#6AA4D8"), (0.6, "#B8D8EE"), (1, "#EAF2F0")], 3, 420, ["#FFFFFF", "#8AB8E0"], 70, angle=-6, sop=(0.08, 0.18))]
    out.append(puff_cloud(D, 470, 236, 170, 2001, ("#FFFFFF", "#F6F6F4", "#A8B8CC")))
    out.append(puff_cloud(D, 130, 250, 120, 2002, ("#FFFFFF", "#F6F6F4", "#A8B8CC")))
    out.append(puff_cloud(D, 300, 290, 90, 2003, ("#FFFFFF", "#F6F6F4", "#A8B8CC")))
    for k in range(5):
        y = 210 + k * 26
        out.append(taper([(40 + k * 60, y), (120 + k * 60, y - 4)], 0.5, 2, "#FFFFFF", 0.6))
    out.append(hill(D, ridge([(-10, 380), (150, 360), (330, 372), (470, 352), (610, 366)], 2004, 5), 620, ("#A8C88A", "#7AA462", "#4E7A3E"), 2004, inkw=0))
    for k, y in enumerate((378, 394)):
        out.append(pline([(-10, y + 6), (200, y), (400, y + 4), (610, y - 2)], "#5A6A50", 1.6, 2005 + k, 0.5, 1))
    out.append(hill(D, ridge([(-10, 420), (200, 410), (420, 418), (610, 404)], 2006, 3), 620, ("#B8D888", "#6EA84A", "#2E6A2A"), 2006, inkw=1.4, inkop=0.4))
    # hedge at the back of the garden
    for k in range(7):
        out.append(dab_crown(D, -10 + k * 100, 418, 70, 30, [("#7AAA5A", "#3E7A3A", "#1A4A22")], 2007 + k, n=40, size=(4, 8), inkw=0.8))
    # the line, the pole and the house corner
    out.append(painted(D, rect_pts(60, 250, 70, 520, 10, 2010, 0.3), ("#B8B8BC", "#7A7A80", "#3A3A40"), 2010, sk=0.2, angle=-90, n=6, inkw=1.2, hi=0.4))
    out.append(painted(D, rect_pts(500, 196, 610, 560, 16, 2011, 0.4), WASHW, 2011, sdir=(1, 0.3), sk=0.06, angle=-90, n=30, inkw=1.8, hi=0.2))
    out.append(f'<rect x="520" y="280" width="60" height="80" fill="#3A4A5A" stroke="#FBFBF6" stroke-width="4"/>')
    out.append(f'<path d="M 520 320 L 580 320 M 550 280 L 550 360" stroke="#FBFBF6" stroke-width="2"/>')
    out.append(f'<path d="{smooth_closed([(494, 200), (610, 180), (610, 214), (494, 222)])}" fill="#5A6474"/>')
    line_pts = [(66, 262), (290, 300), (506, 284)]
    out.append(ink(smooth_open(line_pts), "#E8E8E0", 1.8, 2012, 1, 0.95))

    def on_line(x):
        return lerp(262, 300, x / 290) if x < 290 else lerp(300, 284, (x - 290) / 216)
    sway = 22
    items = [("sheet", 84, 70, 150, WHITE), ("jumper", 170, 60, 66, WOOL), ("towel", 248, 36, 64, RUST), ("shirt", 300, 52, 70, ("#A8C8F0", "#5A8AD0", "#2A4A8A")),
             ("socks", 370, 34, 46, ("#F6D27A", "#E0A030", "#8A5A10")), ("dress", 418, 52, 76, ("#FFB0C8", "#E8608A", "#9A2A4A"))]
    for k, (kind, x, w, h, col) in enumerate(items):
        y = on_line(x + w / 2) + 2
        out.append(garment(D, kind, x, y, w, h, sway, 2020 + k, col))
    # basket and peg bag on the grass
    out.append(cast(D, 214, 556, 66, 9, strength=0.4, seed=2030))
    bk = [(150, 506), (274, 506), (262, 556), (162, 556)]
    out.append(painted(D, poly_pts(bk, 12, 2031, 0.5), ("#E8C08A", "#B8864A", "#6A4A1A"), 2031, sk=0.15, angle=0, n=10, inkw=1.6, hi=0.35))
    for k in range(4):
        out.append(pline([(152 + k * 2, 516 + k * 10), (212, 518 + k * 10), (272 - k * 3, 516 + k * 10)], "#6A4A1A", 1.4, 2032 + k, 0.6, 1))
    out.append(f'<path d="{blob(212, 506, 56, 12, 2036, 0.2, 12)}" fill="#F6F2EA"/><path d="{blob(232, 500, 22, 9, 2037, 0.2, 10)}" fill="#E8604A"/>')
    out.append(grass(2038, (0, 470, 600, 600), ["#4E8A3A", "#86B85A", "#2E6A2A", "#A8D070"], n=180, h=(6, 16)))
    for k in range(20):
        x, y = random.Random(2039 + k).uniform(0, 600), random.Random(2060 + k).uniform(480, 600)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.4" fill="#FFFFFF"/><circle cx="{x:.1f}" cy="{y:.1f}" r="1.1" fill="#F2C21C"/>')
    out.append(letters(D, 300, 126, "a grand drying day", SERIF_IT, 76, "#1E4A7A", ["#2E5A9A", "#0E2A5A", "#3E6AAA"], 2040, max_w=480,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#A8C8F0"))
    out.append(ruled(300, 172, "GET THE WASHING OUT!", "#8A2A1A", font=JOS, size=21, ls=6, line_w=30, gap=12))
    return finish_ie(D, out, 2041)


# ================================================================ 21. it'll be grand — wellies at the door, rain and a rainbow
def welly(D, x, base, h, seed, col=("#7ABF6A", "#2E7A3A", "#144A1A"), flip=1):
    o = []
    pts = [(x - h * 0.16, base - h), (x + h * 0.14, base - h), (x + h * 0.16, base - h * 0.3), (x + h * 0.5, base - h * 0.2), (x + h * 0.56, base - h * 0.06),
           (x + h * 0.5, base), (x - h * 0.18, base), (x - h * 0.2, base - h * 0.2)]
    if flip < 0:
        pts = [(2 * x - px, py) for px, py in pts]
    o.append(cast(D, x + h * 0.15 * flip, base, h * 0.42, 5, strength=0.45, seed=seed))
    o.append(painted(D, pts, col, seed, sdir=(0.7, 0.4), sk=0.18, angle=-90, n=10, inkw=1.6, hi=0.55, hik=0.12))
    o.append(f'<path d="{smooth_closed([(px, py) for px, py in [(x - h * 0.2, base - h * 0.06), (x + h * 0.5 * flip, base - h * 0.06), (x + h * 0.5 * flip, base), (x - h * 0.2 * flip, base)]])}" fill="#2A1E14"/>')
    o.append(f'<path d="{blob(x + h * 0.15 * flip, base - h * 0.12, h * 0.3, h * 0.07, seed, 0.3, 10)}" fill="#6A4A2A" opacity="0.6"/>')
    o.append(f'<path d="{blob(x - h * 0.01, base - h * 0.99, h * 0.16, h * 0.035, seed + 1, 0.05, 12)}" fill="{col[2]}"/>')
    return "".join(o)


@design("itll-be-grand")
def itll_be_grand():
    D = Doc2("ie-gr")
    # inside: whitewashed wall around the doorway
    out = [sky(D, [(0, "#F6EEDC"), (1, "#E8DCC4")], 3, 600, ["#FFFFFF", "#D8C8A8"], 60, angle=-80, sop=(0.06, 0.14))]
    dx0, dx1, dy0, dy1 = 154, 446, 214, 520
    # the view outside: rain, fields, a rainbow
    cid = D.clip(f'<rect x="{dx0}" y="{dy0}" width="{dx1 - dx0}" height="{dy1 - dy0}"/>')
    v = [sky(D, [(0, "#8A98B0"), (0.6, "#C8D0D8"), (1, "#E8E8DC")], 3, 600, ["#FFFFFF", "#7A88A0"], 40, sop=(0.06, 0.14))]
    v.append(f'<rect x="{dx0}" y="{dy0}" width="{dx1 - dx0}" height="80" fill="#5E6A84" opacity="0.35"/>')
    for k, c in enumerate(("#E8584A", "#F29A3A", "#F6D24A", "#6AB85A", "#4A8AD0", "#7A5AB0")):
        rr = 240 - k * 9
        v.append(f'<path d="M {300 - rr} 420 A {rr} {rr * 0.86} 0 0 1 {300 + rr} 420" fill="none" stroke="{c}" stroke-width="9" opacity="0.55"/>')
    v.append(hill(D, ridge([(dx0 - 10, 370), (260, 356), (360, 366), (dx1 + 10, 350)], 2101, 4), 600, ("#A8C090", "#7A9A66", "#4E6A44"), 2101, inkw=0, n=30))
    v.append(hill(D, ridge([(dx0 - 10, 410), (300, 396), (dx1 + 10, 404)], 2102, 3), 600, ("#A8C878", "#6E9A48", "#3E6A2A"), 2102, inkw=0, n=30))
    for k, y in enumerate((376, 394, 420, 450)):
        v.append(pline([(dx0, y + k * 2), (300, y - 3), (dx1, y + 3)], "#4A5A44", 1.4 + k * 0.6, 2103 + k, 0.6, 1))
    v.append(cottage_small(D, 352, 370, 40, 20, 2107, roof="slate", haze=0.25))
    rnd = random.Random(2108)
    for _ in range(160):
        x, y = rnd.uniform(dx0, dx1), rnd.uniform(dy0, dy1)
        L = rnd.uniform(8, 18)
        v.append(f'<path d="M {x:.1f} {y:.1f} l {-L * 0.25:.1f} {L:.1f}" stroke="#FFFFFF" stroke-width="1.2" opacity="{rnd.uniform(0.35, 0.75):.2f}"/>')
    v.append(f'<rect x="{dx0}" y="460" width="{dx1 - dx0}" height="60" fill="#6E7A64"/>')
    v.append(f'<path d="{blob(300, 488, 80, 9, 2109, 0.2, 12)}" fill="#A8B8C8" opacity="0.8"/>')
    for _ in range(20):
        x, y = rnd.uniform(220, 380), rnd.uniform(482, 494)
        v.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="5" ry="1.6" fill="none" stroke="#FFFFFF" stroke-width="0.8" opacity="0.7"/>')
    out.append(f'<g {cid}>{"".join(v)}</g>')
    # deep reveal and the open half-door folded back
    out.append(f'<path d="{pd([(dx0 - 30, dy0 - 16), (dx1 + 30, dy0 - 16), (dx1, dy0), (dx0, dy0)])}" fill="#C8BCA4"/>')
    out.append(f'<path d="{pd([(dx0 - 30, dy0 - 16), (dx0, dy0), (dx0, dy1), (dx0 - 30, dy1 + 18)])}" fill="#D8CCB4"/>')
    out.append(f'<path d="{pd([(dx1 + 30, dy0 - 16), (dx1, dy0), (dx1, dy1), (dx1 + 30, dy1 + 18)])}" fill="#B8AC94"/>')
    door = [(dx1 + 6, dy0 + 8), (dx1 + 54, dy0 - 10), (dx1 + 54, dy1 + 20), (dx1 + 6, dy1 + 6)]
    out.append(painted(D, poly_pts(door, 14, 2110, 0.4), RUST, 2110, sdir=(1, 0.3), sk=0.1, angle=-90, n=16, inkw=1.6, hi=0.3))
    out.append(pline([(dx1 + 6, (dy0 + dy1) / 2 + 6), (dx1 + 54, (dy0 + dy1) / 2 - 2)], "#7A1A12", 2, 2111, 0.7, 1))
    out.append(ink(pd([(dx0, dy0), (dx1, dy0), (dx1, dy1), (dx0, dy1)]), "#5A4A3A", 2, 2112, 1, 0.8))
    # flagstone floor inside
    out.append(f'<path d="M -10 {dy1} L 610 {dy1} L 610 610 L -10 610 Z" fill="#8A8278"/>')
    for k, y in enumerate((540, 572)):
        out.append(pline([(-10, y), (300, y + 1), (610, y)], "#4A443C", 1.6, 2113 + k, 0.7, 1))
    for x in range(30, 600, 120):
        out.append(pline([(x, dy1), (x - 14, 610)], "#4A443C", 1.4, 2120 + x, 0.6, 1))
    out.append(f'<path d="{blob(200, 586, 60, 6, 2125, 0.2, 10)}" fill="#A8B8C8" opacity="0.6"/>')
    # wellies and a dripping umbrella
    out.append(welly(D, 106, 576, 110, 2126))
    out.append(welly(D, 160, 586, 110, 2127, flip=-1))
    # a furled red umbrella leaning against the reveal, dripping into a little puddle
    ua, ub = (470, 380), (520, 588)
    out.append(f'<path d="{blob(522, 592, 34, 5, 2128, 0.2, 10)}" fill="#A8B8C8" opacity="0.7"/>')
    canopy = [(ua[0] + 2, ua[1] + 6), (ua[0] + 18, ua[1] + 40), (ub[0] - 22, ub[1] - 62), (ub[0] - 14, ub[1] - 50), (ua[0] + 30, ua[1] + 30), (ua[0] + 8, ua[1] + 2)]
    out.append(taper([ua, (ub[0] - 2, ub[1] - 6)], 4, 3, "#3A2A1A"))
    out.append(painted(D, [(ua[0] + 6, ua[1] + 20), (ua[0] + 30, ua[1] + 24), (ub[0] - 10, ub[1] - 46), (ub[0] - 18, ub[1] - 40), (ub[0] - 30, ub[1] - 44)], ("#FF8A7A", "#D8283A", "#7A0A1A"), 2129, sdir=(0.8, 0.3), sk=0.2, angle=60, n=10, inkw=1.6, hi=0.45))
    for t in (0.35, 0.6, 0.82):
        p0 = lerp2((ua[0] + 18, ua[1] + 22), (ub[0] - 20, ub[1] - 44), t)
        out.append(pline([(p0[0] - 8, p0[1] - 4), (p0[0] + 8, p0[1] + 4)], "#7A0A1A", 1.4, 2130 + int(t * 10), 0.6, 1))
    out.append(taper([(ua[0] + 10, ua[1] + 26), (ub[0] - 24, ub[1] - 48)], 2, 1, "#FFC8C0", 0.6))
    out.append(f'<path d="M {ua[0]} {ua[1]} q -6 -14 -18 -10 q -8 4 -4 12" fill="none" stroke="#3A2A1A" stroke-width="5" stroke-linecap="round"/>')
    for k, (x, y) in enumerate(((ub[0] - 8, ub[1] - 26), (ub[0] + 4, ub[1] - 12), (ub[0] - 16, ub[1] - 8))):
        out.append(f'<path d="{smooth_closed([(x, y), (x + 2.6, y + 6), (x, y + 8), (x - 2.6, y + 6)])}" fill="#A8C8E8"/>')
    out.append(letters(D, 300, 128, "it'll be grand", SERIF_IT, 96, "#1E5A3A", ["#2E7A4E", "#0E3E24", "#3E8A5A"], 2130, max_w=460,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#8ACB9A"))
    out.append(ruled(300, 176, "AH SURE LOOK", "#8A2A1A", font=JOS, size=22, ls=8, line_w=40, gap=14))
    return finish_ie(D, out, 2131)



# ================================================================ 22. the kettle's on — a whistling kettle on the old range
def kettle(D, cx, base, w, seed, body=("#FF8A7A", "#D8382E", "#7A1410")):
    h = w * 0.62
    o = [cast(D, cx + 8, base, w * 0.6, 8, strength=0.5, seed=seed)]
    # spout
    sp = [(cx + w * 0.3, base - h * 0.45), (cx + w * 0.5, base - h * 0.75), (cx + w * 0.62, base - h * 1.05), (cx + w * 0.68, base - h * 1.0), (cx + w * 0.58, base - h * 0.7), (cx + w * 0.4, base - h * 0.25)]
    o.append(painted(D, sp, body, seed, sk=0.2, n=4, inkw=1.6, hi=0.45))
    o.append(painted(D, [(cx + w * 0.58, base - h * 1.12), (cx + w * 0.72, base - h * 1.04), (cx + w * 0.68, base - h * 0.96), (cx + w * 0.56, base - h * 1.02)], ("#F2F4F8", "#B4BAC4", "#5E6470"), seed + 1, sk=0.2, n=2, inkw=1.2, hi=0.5))
    bd = [(cx - w / 2, base), (cx - w * 0.52, base - h * 0.3), (cx - w * 0.4, base - h * 0.7), (cx - w * 0.2, base - h * 0.92), (cx + w * 0.2, base - h * 0.92), (cx + w * 0.4, base - h * 0.7), (cx + w * 0.52, base - h * 0.3), (cx + w / 2, base)]
    o.append(painted(D, bd, body, seed + 2, sdir=(0.7, 0.5), sk=0.22, angle=-60, n=24, inkw=2, hi=0.55, hik=0.1))
    o.append(f'<path d="{blob(cx - w * 0.24, base - h * 0.55, w * 0.07, h * 0.2, seed + 3, 0.1, 10, 20)}" fill="#FFFFFF" opacity="0.75"/>')
    o.append(f'<rect x="{cx - w / 2:.1f}" y="{base - 7:.1f}" width="{w:.1f}" height="7" fill="#2A2A30"/>')
    o.append(painted(D, ell_pts(cx, base - h * 0.92, w * 0.22, h * 0.06, 0, 360, 20)[:-1], ("#F2F4F8", "#B4BAC4", "#5E6470"), seed + 4, sk=0.1, n=3, inkw=1.2, hi=0.5))
    o.append(f'<circle cx="{cx:.1f}" cy="{base - h * 1.0:.1f}" r="{w * 0.04:.1f}" fill="#1A1A1E"/>')
    hd = [(cx - w * 0.3, base - h * 0.84), (cx - w * 0.26, base - h * 1.32), (cx + w * 0.26, base - h * 1.32), (cx + w * 0.3, base - h * 0.84)]
    o.append(ink(smooth_open(hd), "#1A1A1E", w * 0.07, seed, 1, 1))
    o.append(ink(smooth_open([(x - 1.5, y - 1.5) for x, y in hd[1:3]]), "#6A6A74", w * 0.015, seed, 1, 0.8))
    return "".join(o)


def mug(D, cx, base, w, seed, body=WHITE, motif=None, tea="#A8703E"):
    h = w * 1.05
    o = [cast(D, cx + 6, base, w * 0.6, 5, strength=0.45, seed=seed)]
    hp = [(cx + w * 0.48, base - h * 0.8), (cx + w * 0.82, base - h * 0.74), (cx + w * 0.8, base - h * 0.3), (cx + w * 0.48, base - h * 0.26)]
    o.append(ink(smooth_open(hp), body[2], w * 0.16, seed, 1, 1) + ink(smooth_open(hp), body[1], w * 0.1, seed + 1, 1, 1))
    bd = [(cx - w / 2, base - h), (cx + w / 2, base - h), (cx + w * 0.48, base - 4), (cx + w * 0.4, base), (cx - w * 0.4, base), (cx - w * 0.48, base - 4)]
    o.append(painted(D, poly_pts(bd, 8, seed, 0.3), body, seed + 2, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=8, inkw=1.5, hi=0.5))
    if motif == "shamrock":
        for k in range(3):
            a = -90 + k * 120
            o.append(f'<path d="{smooth_closed(heart_d(cx + math.cos(math.radians(a)) * w * 0.1, base - h * 0.5 + math.sin(math.radians(a)) * w * 0.1, w * 0.12, a + 90))}" fill="#2E8A4E"/>')
        o.append(pline([(cx, base - h * 0.48), (cx + 2, base - h * 0.3)], "#2E8A4E", 2, seed, 0.9, 1))
    elif motif == "stripes":
        for k in range(3):
            y = base - h * (0.3 + k * 0.18)
            o.append(f'<path d="M {cx - w * 0.49:.1f} {y:.1f} L {cx + w * 0.49:.1f} {y:.1f}" stroke="#2E5AB8" stroke-width="{w * 0.07:.1f}" opacity="0.85"/>')
    o.append(f'<path d="{smooth_closed(ell_pts(cx, base - h, w / 2, w * 0.12, 0, 360, 20)[:-1])}" fill="{body[1]}"/>')
    o.append(f'<path d="{smooth_closed(ell_pts(cx, base - h + 2, w / 2 - 4, w * 0.09, 0, 360, 20)[:-1])}" fill="{tea}"/>')
    o.append(ink(smooth_closed(ell_pts(cx, base - h, w / 2, w * 0.12, 0, 360, 20)[:-1]), INK, 1.2, seed, 1, 0.6))
    return "".join(o)


def tiles(D, y0, y1, seed, size=40, band=None):
    rnd = random.Random(seed)
    out = [f'<rect y="{y0}" width="600" height="{y1 - y0}" fill="#C8C4B8"/>']
    j = 0
    y = y0
    while y < y1:
        x = -size / 2 * (j % 2)
        while x < 600:
            c = "#F6F4EE" if not (band and band[0] <= j <= band[1]) else band[2]
            c = mix(c, rnd.choice(["#FFFFFF", "#E8E4DA"]), rnd.uniform(0, 0.5))
            out.append(f'<rect x="{x + 1.5:.1f}" y="{y + 1.5:.1f}" width="{size - 3}" height="{size * 0.5 - 3}" rx="3" fill="{c}"/>')
            out.append(f'<path d="M {x + 5:.1f} {y + 5:.1f} l {size * 0.4:.1f} 0" stroke="#FFFFFF" stroke-width="1.6" opacity="0.8"/>')
            x += size
        y += size * 0.5
        j += 1
    return "".join(out)


@design("the-kettles-on")
def the_kettles_on():
    D = Doc2("ie-ko")
    out = [tiles(D, 0, 400, 2201, 44, band=(15, 15, "#3E8A5A"))]
    out.append(soft_glow(D, 300, 260, 320, "#FFF4D8", 0.35))
    # a shelf with a tea caddy and a jug
    out.append('<g transform="translate(-300 0)">')
    out.append(painted(D, rect_pts(350, 236, 560, 248, 12, 2202, 0.4), PINE, 2202, sdir=(0, 1), sk=0.2, angle=0, n=8, inkw=1.4, hi=0.4))
    out.append(cast(D, 440, 236, 110, 5, strength=0.35, seed=2203))
    caddy = rect_pts(370, 168, 420, 236, 8, 2204, 0.3)
    out.append(painted(D, caddy, ("#5ABA7A", "#1E7A44", "#0A4022"), 2204, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=6, inkw=1.4, hi=0.45))
    out.append(f'<rect x="372" y="190" width="46" height="22" fill="#F6D27A"/>')
    out.append(label(395, 206, "TAE", CINZEL, 16, "#1E4A2A", ls=1))
    out.append(painted(D, rect_pts(366, 160, 424, 170, 6, 2205, 0.3), ("#F6D27A", "#C8962A", "#6A4A10"), 2205, sk=0.2, n=2, inkw=1.2, hi=0.4))
    jug = [(462, 236), (456, 200), (466, 176), (500, 172), (510, 196), (504, 236)]
    out.append(painted(D, jug, WHITE, 2206, sdir=(0.9, 0.3), sk=0.2, n=6, inkw=1.4, hi=0.5))
    out.append(ink(smooth_open([(504, 184), (524, 190), (520, 214), (506, 220)]), "#B8B0A6", 5, 2207, 1, 1))
    out.append(pline([(458, 210), (508, 210)], "#2E5AB8", 3, 2208, 0.9, 1))
    out.append("</g>")
    # the range: cream enamel, chrome rail, two oven doors
    rx0, rx1, rtop = 54, 546, 392
    out.append(cast(D, 300, 600, 280, 20, strength=0.5, seed=2209))
    out.append(painted(D, rect_pts(rx0, rtop, rx1, 640, 20, 2210, 0.5), ("#FFFAEE", "#EFE4CC", "#B8A884"), 2210, sdir=(1, 0.3), sk=0.06, angle=-90, n=40, inkw=2, hi=0.3))
    out.append(painted(D, rect_pts(rx0 - 8, rtop - 16, rx1 + 8, rtop + 4, 20, 2211, 0.4), ("#F2F4F8", "#B4BAC4", "#5E6470"), 2211, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.8, hi=0.5))
    for x0 in (90, 316):
        out.append(painted(D, rect_pts(x0, 470, x0 + 194, 640, 14, 2212 + x0, 0.4), ("#FFFDF6", "#F2E8D4", "#C0B08C"), 2212 + x0, sdir=(1, 0.3), sk=0.08, angle=-90, n=14, inkw=1.6, hi=0.3))
        out.append(taper([(x0 + 30, 492), (x0 + 164, 492)], 8, 8, "#C8CCD4") + taper([(x0 + 30, 490), (x0 + 164, 490)], 2, 2, "#FFFFFF", 0.9))
    out.append(taper([(rx0 + 10, 438), (rx1 - 10, 438)], 9, 9, "#C8CCD4") + taper([(rx0 + 10, 436), (rx1 - 10, 436)], 2.4, 2.4, "#FFFFFF", 0.9))
    for x in (rx0 + 14, rx1 - 14):
        out.append(f'<rect x="{x - 4}" y="428" width="8" height="18" rx="2" fill="#8A909A"/>')
    # tea towel over the rail
    tw = [(380, 432), (454, 432), (460, 520), (386, 524)]
    out.append(gingham(D, smooth_closed(poly_pts(tw, 10, 2213, 0.6)), "#C8302A", cell=10))
    out.append(ink(smooth_closed(poly_pts(tw, 10, 2213, 0.6)), INK, 1.6, 2213, 1, 0.7))
    out.append(f'<path d="{smooth_closed([(380, 432), (454, 432), (454, 446), (380, 446)])}" fill="#2A0E06" opacity="0.15"/>')
    # temperature gauge
    out.append(f'<circle cx="190" cy="414" r="12" fill="#FFFDF6" stroke="#8A909A" stroke-width="3"/><path d="M 190 414 L 197 407" stroke="#C8302A" stroke-width="2" stroke-linecap="round"/>')
    # hotplate lid (closed) and the kettle on the open plate
    kx = 352
    out.append(painted(D, ell_pts(kx, rtop - 14, 96, 14, 0, 360, 30)[:-1], ("#4A4A52", "#2A2A30", "#101014"), 2214, sk=0.1, n=4, inkw=1.4, hi=0.3))
    out.append(D.glow(kx, rtop - 20, 90, "#FF9A3A", 0.25))
    out.append(kettle(D, kx, rtop - 14, 176, 2215))
    # steam whistling from the spout
    sx, sy = kx + 176 * 0.66, rtop - 14 - 176 * 0.62 * 1.08
    for k in range(5):
        t = k / 4
        px, py = sx + 4 + t * 40, sy - 12 - t * 50
        rr = 6 + t * 16
        out.append(f'<path d="{blob(px + 2, py + 2, rr, rr * 0.7, 2216 + k, 0.2, 10)}" fill="#9AA8B8" opacity="{0.55 - t * 0.35:.2f}"/>')
        out.append(f'<path d="{blob(px, py, rr * 0.9, rr * 0.62, 2226 + k, 0.2, 10)}" fill="#FFFFFF" opacity="{0.9 - t * 0.5:.2f}"/>')
    for k, (dx, dy) in enumerate(((6, -14), (16, -6))):
        out.append(taper([(sx + 4, sy - 2), (sx + dx * 2, sy + dy * 2)], 1.4, 0.4, "#FFFFFF", 0.8))
    out.append(mug(D, 110, rtop - 16, 54, 2220, motif="shamrock"))
    out.append(mug(D, 184, rtop - 16, 50, 2221, body=("#FFE8A0", "#F2C24A", "#9A7A20"), motif="stripes"))
    out.append(letters(D, 300, 116, "the kettle's on", SERIF_IT, 90, "#1E5A3A", ["#2E7A4E", "#0E3E24", "#3E8A5A"], 2222, max_w=470,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#8ACB9A"))
    out.append(ruled(300, 160, "COME IN, SIT DOWN", "#8A2A1A", font=JOS, size=21, ls=6, line_w=30, gap=12))
    return finish_ie(D, out, 2223)


# ================================================================ 23. Granny's kitchen — the dresser with the good delft
def delft_plate(D, cx, cy, r, seed, blue="#2E5AB8"):
    rnd = random.Random(seed)
    o = [f'<circle cx="{cx + 2}" cy="{cy + 3}" r="{r}" fill="#2A1A0A" opacity="0.25"/>']
    o.append(painted(D, blob_pts(cx, cy, r, r, seed, 0.02, 20), WHITE, seed, sk=0.1, n=6, inkw=1.2, hi=0.4))
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.86:.1f}" fill="none" stroke="{blue}" stroke-width="{max(1.5, r * 0.08):.1f}"/>')
    for k in range(10):
        a = math.radians(k * 36)
        o.append(f'<path d="{blob(cx + math.cos(a) * r * 0.86, cy + math.sin(a) * r * 0.86, r * 0.08, r * 0.05, seed + k, 0.1, 6, k * 36)}" fill="{blue}"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.55:.1f}" fill="none" stroke="{blue}" stroke-width="1.2" opacity="0.7"/>')
    for k in range(5):
        a = math.radians(k * 72 + rnd.uniform(0, 20))
        o.append(f'<path d="{blob(cx + math.cos(a) * r * 0.25, cy + math.sin(a) * r * 0.25, r * 0.16, r * 0.08, seed + 20 + k, 0.2, 8, k * 72)}" fill="{blue}" opacity="0.85"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.08:.1f}" fill="{blue}"/>')
    o.append(f'<path d="{blob(cx - r * 0.4, cy - r * 0.45, r * 0.25, r * 0.1, seed + 30, 0.2, 8, -40)}" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(o)


def hanging_cup(D, x, y, w, seed, col="#2E5AB8"):
    o = [pline([(x, y), (x, y + 6)], "#8A6A3A", 1.6, seed, 1, 1)]
    o.append(ink(smooth_open([(x, y + 6), (x + w * 0.3, y + 8), (x + w * 0.32, y + 16)]), "#E8E4DC", 3, seed, 1, 1))
    cup = [(x - w * 0.2, y + 10), (x + w * 0.8, y + 12), (x + w * 0.7, y + w * 0.75), (x - w * 0.1, y + w * 0.72)]
    cup = rot(cup, x, y, 20)
    o.append(painted(D, cup, WHITE, seed, sk=0.2, n=3, inkw=1.2, hi=0.5))
    o.append(pline([lerp2(cup[0], cup[3], 0.35), lerp2(cup[1], cup[2], 0.35)], col, 2.2, seed, 0.9, 1))
    return "".join(o)


@design("grannys-kitchen")
def grannys_kitchen():
    D = Doc2("ie-gk")
    # sprigged wallpaper
    out = [paper(D.nid(), "#F2E2CC", "#8A6A4A", 2301)]
    rnd = random.Random(2302)
    for j in range(10):
        for i in range(9):
            x, y = i * 70 + (35 if j % 2 else 0), j * 64 + 20
            out.append(f'<path d="M {x - 6} {y + 6} q 6 -4 6 -12" stroke="#7A9A6A" stroke-width="1.4" fill="none" opacity="0.6"/>')
            out.append(f'<circle cx="{x}" cy="{y - 7}" r="4" fill="#D88A8A" opacity="0.55"/><circle cx="{x - 7}" cy="{y + 2}" r="2.6" fill="#8AA8D0" opacity="0.5"/>')
    out.append(soft_glow(D, 300, 300, 330, "#FFF4D8", 0.35))
    # the dresser
    dx0, dx1 = 84, 516
    green = ("#7ABA9A", "#3E7A5E", "#1E4A36")
    cream = ("#FFFAEC", "#F2E6CA", "#C0AE88")
    out.append(cast(D, 300, 600, 250, 16, strength=0.5, seed=2303))
    out.append(painted(D, rect_pts(dx0 + 10, 214, dx1 - 10, 440, 20, 2304, 0.5), ("#E8D4AE", "#C8AC7E", "#8A6A40"), 2304, sk=0.05, angle=-90, n=30, inkw=1.6, hi=0.2))
    for x in range(dx0 + 20, dx1 - 10, 22):
        out.append(f'<path d="M {x} 216 L {x} 438" stroke="#9A7A4E" stroke-width="1.2" opacity="0.5"/>')
    out.append(painted(D, rect_pts(dx0 - 8, 194, dx1 + 8, 216, 20, 2305, 0.4), green, 2305, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.8, hi=0.45))
    out.append(f'<path d="{smooth_closed([(dx0 - 14, 196), (dx1 + 14, 196), (dx1 + 6, 188), (dx0 - 6, 188)])}" fill="{green[1]}" stroke="{INK}" stroke-width="1.4"/>')
    for x0, x1 in ((dx0 - 4, dx0 + 16), (dx1 - 16, dx1 + 4)):
        out.append(painted(D, rect_pts(x0, 214, x1, 446, 10, 2306 + x0, 0.3), green, 2306 + x0, sdir=(1, 0), sk=0.2, angle=-90, n=10, inkw=1.6, hi=0.4))
    shelves = [292, 366]
    for k, y in enumerate(shelves):
        out.append(painted(D, rect_pts(dx0 + 14, y, dx1 - 14, y + 10, 20, 2310 + k, 0.4), cream, 2310 + k, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.4))
    # plates standing on the shelves, cups on hooks
    for row, (y, r, n) in enumerate(((268, 28, 6), (342, 26, 6))):
        for i in range(n):
            x = dx0 + 54 + i * (dx1 - dx0 - 100) / (n - 1)
            if row == 1 and i in (2, 3):
                continue
            out.append(delft_plate(D, x, y, r, 2320 + row * 10 + i, "#2E5AB8" if (i + row) % 3 else "#3E8A5A"))
        out.append(taper([(dx0 + 18, y + 18), (dx1 - 18, y + 18)], 3, 3, "#B89A6A"))
    # a jug and the radio on the middle shelf gap
    out.append(painted(D, [(270, 366), (266, 334), (276, 318), (300, 316), (308, 336), (304, 366)], WHITE, 2330, sk=0.2, n=4, inkw=1.4, hi=0.5))
    out.append(pline([(268, 344), (306, 344)], "#2E5AB8", 2.6, 2331, 0.9, 1))
    out.append(painted(D, rect_pts(316, 318, 372, 364, 8, 2332, 0.3), ("#E8A878", "#B86A3A", "#6A3410"), 2332, sk=0.15, n=6, inkw=1.4, hi=0.4))
    out.append(f'<rect x="322" y="326" width="28" height="30" rx="4" fill="#E8D8B0"/><circle cx="362" cy="336" r="5" fill="#3A2A1A"/><circle cx="362" cy="352" r="4" fill="#3A2A1A"/>')
    for k in range(6):
        out.append(f'<path d="M 326 {330 + k * 4} L 346 {330 + k * 4}" stroke="#8A6A3A" stroke-width="1"/>')
    for k, x in enumerate((130, 190, 410, 470)):
        out.append(hanging_cup(D, x, 302, 22, 2340 + k, "#2E5AB8" if k % 2 else "#C8302A"))
    # countertop and the cupboard below
    out.append(painted(D, rect_pts(dx0 - 14, 436, dx1 + 14, 456, 20, 2350, 0.4), PINE, 2350, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.8, hi=0.45))
    out.append(painted(D, rect_pts(dx0 - 4, 456, dx1 + 4, 640, 20, 2351, 0.5), green, 2351, sdir=(1, 0.3), sk=0.08, angle=-90, n=30, inkw=2, hi=0.3))
    for x0 in (dx0 + 12, 304):
        out.append(f'<path d="{hg.org_rect(x0, 474, 196, 120, 2352 + x0, 0.4, 10, 3)}" fill="none" stroke="#1E4A36" stroke-width="3"/>')
        out.append(f'<path d="{hg.org_rect(x0 + 12, 486, 172, 96, 2353 + x0, 0.4, 10, 3)}" fill="none" stroke="#A8D8B8" stroke-width="1.4" opacity="0.6"/>')
    for x in (284, 316):
        out.append(f'<circle cx="{x}" cy="530" r="6" fill="#E8C060" stroke="#6A4A10" stroke-width="1.2"/>')
    # on the counter: brown teapot, biscuit tin, a loaf under a cloth
    out.append(cast(D, 160, 440, 56, 6, strength=0.45, seed=2360))
    tp = [(118, 438), (114, 406), (130, 386), (190, 386), (204, 406), (200, 438)]
    out.append(painted(D, tp, ("#A86A3A", "#6A3418", "#2E1408"), 2361, sk=0.2, n=8, inkw=1.6, hi=0.5))
    out.append(painted(D, [(204, 412), (232, 388), (238, 392), (210, 424)], ("#A86A3A", "#6A3418", "#2E1408"), 2362, sk=0.2, n=2, inkw=1.2, hi=0.4))
    out.append(ink(smooth_open([(116, 398), (96, 404), (98, 424), (116, 428)]), "#6A3418", 6, 2363, 1, 1))
    out.append(painted(D, ell_pts(160, 386, 28, 6, 0, 360, 16)[:-1], ("#A86A3A", "#6A3418", "#2E1408"), 2364, sk=0.1, n=2, inkw=1.2, hi=0.4))
    out.append(f'<circle cx="160" cy="378" r="5" fill="#6A3418"/>')
    bt = rect_pts(330, 392, 420, 440, 10, 2365, 0.3)
    out.append(painted(D, bt, ("#E85A6A", "#B82A3A", "#6A0A16"), 2365, sk=0.2, n=8, inkw=1.4, hi=0.45))
    out.append(f'<rect x="336" y="404" width="78" height="22" fill="#F6D27A"/>')
    for k in range(5):
        out.append(f'<circle cx="{344 + k * 15}" cy="415" r="5" fill="#C8863E" stroke="#6A3A10" stroke-width="1"/>')
    out.append(painted(D, rect_pts(326, 384, 424, 394, 8, 2366, 0.3), ("#E8E4DC", "#B4BAC4", "#5E6470"), 2366, sk=0.2, n=3, inkw=1.2, hi=0.4))
    out.append(cloth(D, [(434, 440), (440, 404), (470, 390), (500, 396), (512, 420), (510, 440)], "#2E5AB8", 2367, cell=8))
    out.append(letters(D, 300, 118, "Granny's kitchen", SERIF_IT, 84, "#7A2A1A", ["#A03A22", "#5A1A0A", "#C0502E"], 2368, max_w=470,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#F2A888"))
    out.append(ruled(300, 162, "NOBODY LEAVES HUNGRY", "#2E5A3E", font=JOS, size=21, ls=5, line_w=26, gap=12))
    return finish_ie(D, out, 2369)


# ================================================================ 24. Mammy — a jam jar of hedgerow flowers on the windowsill
def foxglove(D, x, y, L, ang, seed, pal=("#F2B8E0", "#C85AA0", "#7A2A5A")):
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    o = [pline([(x, y), (x + ux * L, y + uy * L)], "#5E7A3A", 2.2, seed, 0.9, 1)]
    for k in range(9):
        t = 0.3 + k * 0.075
        px, py = x + ux * L * t, y + uy * L * t
        sg = 1 if k % 2 else -1
        bx, by = px - uy * sg * 8, py + ux * sg * 8
        bell = blob_pts(bx, by, 8 * (1.1 - t * 0.5), 5 * (1.1 - t * 0.5), seed + k, 0.08, 10, ang + 90 + sg * 20)
        o.append(painted(D, bell, pal, seed + k, sk=0.2, n=2, inkw=0.8, hi=0.4))
        o.append(f'<circle cx="{bx + uy * sg * 2:.1f}" cy="{by - ux * sg * 2:.1f}" r="1.2" fill="#5A1A3A"/>')
    for k in range(4):
        t = 0.92 + k * 0.02
        o.append(f'<circle cx="{x + ux * L * t:.1f}" cy="{y + uy * L * t:.1f}" r="{3 - k * 0.5:.1f}" fill="#8AAA5A"/>')
    return "".join(o)


def montbretia(D, x, y, L, ang, seed):
    a = math.radians(ang)
    pts = [(x, y), (x + math.cos(a) * L * 0.5, y + math.sin(a) * L * 0.5), (x + math.cos(a + 0.4) * L, y + math.sin(a + 0.4) * L)]
    pts = catmull(pts, 6)
    o = [ink(smooth_open(pts), "#5E7A3A", 1.6, seed, 1, 0.9)]
    for k in range(3, len(pts)):
        px, py = pts[k]
        o.append(f'<path d="{blob(px, py - 3, 4.5, 2.6, seed + k, 0.2, 8, ang - 30)}" fill="{["#FF8A2A", "#F26A1A", "#FFA040"][k % 3]}" stroke="#A8400A" stroke-width="0.6"/>')
    return "".join(o)


def daisy_head(D, x, y, r, seed):
    o = []
    for k in range(12):
        a = k * 30
        o.append(f'<path d="{blob(x + math.cos(math.radians(a)) * r * 0.6, y + math.sin(math.radians(a)) * r * 0.6, r * 0.42, r * 0.14, seed + k, 0.1, 6, a)}" fill="#FFFFFF" stroke="#C8C0B0" stroke-width="0.6"/>')
    o.append(f'<circle cx="{x}" cy="{y}" r="{r * 0.26:.1f}" fill="#F2C21C" stroke="#A8800A" stroke-width="0.8"/>')
    return "".join(o)


@design("mammy")
def mammy():
    D = Doc2("ie-mm")
    out = [sky(D, [(0, "#F2D8D2"), (1, "#E8C8C0")], 3, 600, ["#FFFFFF", "#D8A8A0"], 60, angle=-80, sop=(0.06, 0.12))]
    # window with a view of the fields
    wx0, wx1, wy0, wy1 = 96, 504, 214, 462
    cid = D.clip(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}"/>')
    v = [sky(D, [(0, "#9CC4E4"), (0.6, "#D8E8EE"), (1, "#F2EEDC")], 3, 600, ["#FFFFFF"], 30, sop=(0.05, 0.1))]
    v.append(puff_cloud(D, 410, 262, 110, 2401, ("#FFFFFF", "#F6F4F0", "#C0CCD8")))
    v.append(hill(D, ridge([(wx0, 360), (220, 342), (360, 356), (wx1, 340)], 2402, 4), 600, ("#A8C890", "#7AA466", "#4E7A44"), 2402, inkw=0, n=30))
    v.append(hill(D, ridge([(wx0, 400), (260, 386), (wx1, 392)], 2403, 3), 600, ("#B8D888", "#7AAE52", "#3E7A32"), 2403, inkw=0, n=30))
    for k, y in enumerate((366, 386, 410)):
        v.append(pline([(wx0, y + k * 3), (300, y - 2), (wx1, y + 2)], "#4A5A44", 1.4, 2404 + k, 0.5, 1))
    v.append(cottage_small(D, 180, 368, 40, 20, 2407, roof="thatch", haze=0.2))
    out.append(f'<g {cid}>{"".join(v)}</g>')
    for x in (wx0, (wx0 + wx1) / 2, wx1):
        out.append(f'<rect x="{x - 7:.1f}" y="{wy0}" width="14" height="{wy1 - wy0}" fill="#FBFBF6" stroke="#B8B0A6" stroke-width="1"/>')
    for y in (wy0, (wy0 + wy1) / 2):
        out.append(f'<rect x="{wx0}" y="{y - 6:.1f}" width="{wx1 - wx0}" height="12" fill="#FBFBF6" stroke="#B8B0A6" stroke-width="1"/>')
    # lace curtains
    for sg, x0 in ((1, 60), (-1, 540)):
        cur = [(x0, 200), (x0 + sg * 92, 200), (x0 + sg * 70, 300), (x0 + sg * 40, 420), (x0 + sg * 30, 470), (x0, 470)]
        out.append(f'<path d="{smooth_closed(cur)}" fill="#FFFFFF" opacity="0.85"/>')
        cc = D.clip(f'<path d="{smooth_closed(cur)}"/>')
        lace = []
        for j in range(14):
            for i in range(7):
                lace.append(f'<circle cx="{x0 + sg * (6 + i * 14 + (j % 2) * 7):.1f}" cy="{206 + j * 20}" r="4" fill="none" stroke="#D8C8C0" stroke-width="1.2"/>')
        out.append(f'<g {cc}>{"".join(lace)}</g>')
        out.append(ink(smooth_closed(cur), "#C8B8B0", 1.2, 2410 + sg, 1, 0.6))
    out.append(painted(D, rect_pts(40, 194, 560, 206, 20, 2412, 0.4), WOOD, 2412, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.4))
    # the sill
    out.append(painted(D, rect_pts(50, 462, 550, 486, 20, 2413, 0.5), ("#FFFDF6", "#F2EADA", "#B8AC94"), 2413, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.8, hi=0.4))
    out.append(f'<rect x="-10" y="486" width="620" height="124" fill="#E0B8B0"/>')
    out.append(painted(D, rect_pts(50, 462, 550, 486, 20, 2413, 0.5), ("#FFFDF6", "#F2EADA", "#B8AC94"), 2413, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=1.8, hi=0.4))
    out.append(strokes(D.nid(), "M -10 486 L 610 486 L 610 610 L -10 610 Z", (-40, 486, 610, 610), ["#F2D0C8", "#C89890"], 2414, n=40, angle=-80, length=(20, 60), width=(3, 8), opacity=(0.1, 0.25)))
    # the bouquet
    jx, jb = 300, 468
    out.append(f'<g transform="translate({jx} {jb}) scale(1.42) translate({-jx} {-jb})">')
    rnd = random.Random(2415)
    out.append(foxglove(D, jx - 10, jb - 80, 128, -106, 2416))
    out.append(foxglove(D, jx + 6, jb - 80, 116, -76, 2417, pal=("#F8D0EA", "#D888C0", "#8A4A7A")))
    for k, (a, L) in enumerate(((-150, 110), (-30, 110), (-130, 90), (-50, 96))):
        out.append(montbretia(D, jx, jb - 86, L, a, 2420 + k))
    for k, (a, L) in enumerate(((-120, 90), (-62, 96), (-96, 70))):
        tip = (jx + math.cos(math.radians(a)) * L, jb - 86 + math.sin(math.radians(a)) * L)
        out.append(pline([(jx, jb - 86), tip], "#5E7A3A", 1.6, 2425 + k, 0.9, 1))
        out.append(dab_crown(D, tip[0], tip[1], 18, 12, [("#FFFDF0", "#F2EAC8", "#C8B88A")], 2428 + k, n=30, size=(1.6, 3), inkw=0, base=False))
    for k, (dx, dy) in enumerate(((-56, -120), (52, -128), (-30, -150), (70, -100))):
        out.append(pline([(jx + dx * 0.2, jb - 86), (jx + dx, jb - 86 + dy * 0.3), (jx + dx, jb - 86 + dy * 0.6)], "#5E7A3A", 1.4, 2432 + k, 0.9, 1))
        out.append(daisy_head(D, jx + dx, jb - 86 + dy * 0.6, 14, 2436 + k))
    for k in range(5):
        a = rnd.uniform(-160, -20)
        L = rnd.uniform(60, 100)
        out.append(fuchsia_bell(D, jx + math.cos(math.radians(a)) * L, jb - 86 + math.sin(math.radians(a)) * L * 0.7, 14, 2440 + k, rnd.uniform(-20, 20)))
    for k in range(5):
        x, y = jx + rnd.uniform(-70, 70), jb - 86 - rnd.uniform(10, 60)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#F6D21C" stroke="#A8800A" stroke-width="0.8"/><circle cx="{x - 1.4:.1f}" cy="{y - 1.4:.1f}" r="1.6" fill="#FFF6B0"/>')
    for k, a in enumerate((-170, -10, -140, -40)):
        out.append(leaf_simple(D, jx, jb - 82, 60, 9, a, ("#8ABA5A", "#3E7A32", "#1E4A1E"), 2450 + k))
    # the jam jar with a ribbon
    jar = [(jx - 44, jb - 92), (jx + 44, jb - 92), (jx + 48, jb - 70), (jx + 50, jb - 8), (jx + 42, jb), (jx - 42, jb), (jx - 50, jb - 8), (jx - 48, jb - 70)]
    out.append(cast(D, jx + 10, jb + 1, 62, 4, strength=0.45, seed=2455))
    out.append(f'<path d="{smooth_closed(jar)}" fill="#D8ECE8" opacity="0.55"/>')
    out.append(f'<path d="{smooth_closed([(jx - 46, jb - 56), (jx + 46, jb - 56), (jx + 48, jb - 8), (jx + 40, jb - 2), (jx - 40, jb - 2), (jx - 48, jb - 8)])}" fill="#B8DCD8" opacity="0.5"/>')
    for k in range(6):
        out.append(pline([(jx - 30 + k * 12, jb - 90), (jx - 28 + k * 11, jb - 6)], "#4E7A32", 2, 2456 + k, 0.7, 1))
    out.append(ink(smooth_closed(jar), "#7A9A98", 1.6, 2462, 1, 0.8))
    out.append(taper([(jx - 36, jb - 80), (jx - 38, jb - 20)], 5, 2, "#FFFFFF", 0.8))
    out.append(painted(D, rect_pts(jx - 46, jb - 96, jx + 46, jb - 84, 10, 2463, 0.3), ("#E8F0F0", "#C8D8D8", "#8AA0A0"), 2463, sk=0.2, n=3, inkw=1.2, hi=0.5))
    out.append(taper([(jx - 48, jb - 72), (jx, jb - 70), (jx + 48, jb - 72)], 7, 7, "#C8302A"))
    out.append(painted(D, [(jx + 12, jb - 72), (jx + 34, jb - 86), (jx + 40, jb - 72), (jx + 34, jb - 58)], RUST, 2464, sk=0.15, n=2, inkw=1.1, hi=0.4))
    out.append(painted(D, [(jx + 12, jb - 72), (jx - 8, jb - 88), (jx - 14, jb - 72), (jx - 6, jb - 58)], RUST, 2465, sk=0.15, n=2, inkw=1.1, hi=0.4))
    out.append(taper([(jx + 10, jb - 70), (jx + 18, jb - 40)], 5, 3, "#C8302A") + taper([(jx + 10, jb - 70), (jx - 2, jb - 44)], 5, 3, "#C8302A"))
    out.append("</g>")
    out.append(letters(D, 300, 140, "Mammy", SERIF_IT, 128, "#9A2A3A", ["#C03A4E", "#6A1A24", "#D8586A"], 2466, max_w=380,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#F8A8B0"))
    out.append(ruled(300, 530, "A STÓR MO CHROÍ", "#6A2A3A", font=JOS, size=22, ls=6, line_w=34, gap=12))
    return finish_ie(D, out, 2467)



# ================================================================ 25. Lá Fhéile Pádraig — the parade passing down the main street
def tricolour(D, x, y, w, h, seed, wave=4, pole=True, pole_len=None):
    """The Irish tricolour (green, white, orange) on a pole, rippling; (x, y) = top of the pole."""
    o = []
    if pole:
        o.append(taper([(x, y), (x + 1, y + (pole_len or h * 2.6))], 3, 3, "#6A4A2A"))
        o.append(f'<circle cx="{x}" cy="{y - 2}" r="3" fill="#E8C060"/>')
    for k, c in enumerate(("#1E9A5A", "#FFFFFF", "#F28A2A")):
        x0, x1 = x + w * k / 3, x + w * (k + 1) / 3
        pts = []
        for i in range(7):
            t = i / 6
            xx = lerp(x0, x1, t)
            pts.append((xx, y + 2 + wave * math.sin((xx - x) / w * 6.28)))
        for i in range(7):
            t = 1 - i / 6
            xx = lerp(x0, x1, t)
            pts.append((xx, y + 2 + h + wave * math.sin((xx - x) / w * 6.28)))
        o.append(f'<path d="{pd(pts)}" fill="{c}"/>')
    o.append(f'<path d="M {x} {y + 2} L {x + w} {y + 2 + wave * math.sin(6.28)} L {x + w} {y + 2 + h} L {x} {y + 2 + h} Z" fill="none" stroke="#3A2A1A" stroke-width="0.9" opacity="0.5"/>')
    for i in range(3):
        xx = x + w * (i + 0.5) / 3
        o.append(f'<path d="M {xx:.1f} {y + 4:.1f} l 0 {h - 4:.1f}" stroke="#000000" stroke-width="{w * 0.08:.1f}" opacity="0.08"/>')
    return "".join(o)


@design("la-fheile-padraig")
def la_fheile_padraig():
    D = Doc2("ie-lp")
    out = [sky(D, [(0, "#8ABEE6"), (0.7, "#D4E8F2"), (1, "#F2F0E6")], 3, 400, ["#FFFFFF", "#A8C8E4"], 50, angle=-3, sop=(0.06, 0.14))]
    out.append(puff_cloud(D, 500, 214, 120, 2501, ("#FFFFFF", "#F6F4F0", "#B8C4D4")))
    # main street facades
    rnd = random.Random(2502)
    xs = [-10, 96, 196, 300, 404, 504, 610]
    walls = ["#F2C24A", "#E8F0E8", "#4E86C8", "#E85A4A", "#7ABA8A", "#F2E2C8"]
    for k in range(6):
        x0, x1 = xs[k], xs[k + 1]
        roof = 236 + rnd.randint(0, 28)
        out.append(painted(D, rect_pts(x0, roof, x1, 470, 16, 2503 + k, 0.4), P3(walls[k], 0.3, 0.3), 2503 + k, sdir=(1, 0.3), sk=0.06, angle=-90, n=20, inkw=1.4, hi=0.25))
        out.append(f'<path d="{smooth_closed([(x0 - 4, roof + 2), (x1 + 4, roof + 2), (x1 + 4, roof - 6), (x0 - 4, roof - 6)])}" fill="#5A6474"/>')
        for j in range(2):
            for i in range(2):
                wx = x0 + (x1 - x0) * (0.2 + i * 0.42)
                wy = roof + 24 + j * 64
                out.append(f'<rect x="{wx:.1f}" y="{wy}" width="{(x1 - x0) * 0.2:.1f}" height="38" fill="#2E3A4A" stroke="#FBFBF6" stroke-width="2.6"/>')
                if rnd.random() < 0.4:
                    out.append(tricolour(D, wx + 2, wy + 10, 22, 14, 2510 + k * 4 + i, wave=1.5, pole=False))
        out.append(f'<rect x="{x0 + 6}" y="404" width="{x1 - x0 - 12}" height="66" fill="{dk(walls[k], 0.45)}"/>')
        out.append(f'<rect x="{x0 + 14}" y="416" width="{(x1 - x0) * 0.5:.1f}" height="44" fill="#F6E8C8"/>')
    # bunting
    for (y0, y1, sag) in ((276, 290, 30), (318, 304, 26)):
        n = 22
        for i in range(n):
            t0, t1 = i / n, (i + 0.8) / n
            p0 = (lerp(-10, 610, t0), lerp(y0, y1, t0) + sag * 4 * t0 * (1 - t0))
            p1 = (lerp(-10, 610, t1), lerp(y0, y1, t1) + sag * 4 * t1 * (1 - t1))
            tip = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + 18)
            out.append(f'<path d="{smooth_closed([p0, p1, tip])}" fill="{["#1E9A5A", "#FFFFFF", "#F28A2A"][i % 3]}" stroke="#3A2A1A" stroke-width="0.7"/>')
        out.append(ink(smooth_open([(lerp(-10, 610, t), lerp(y0, y1, t) + sag * 4 * t * (1 - t)) for t in [i / 30 for i in range(31)]]), "#3A2A1A", 1.2, 2520 + y0, 1, 0.9))
    # street
    out.append(f'<path d="M -10 470 L 610 470 L 610 610 L -10 610 Z" fill="#9A948A"/>')
    out.append(strokes(D.nid(), "M -10 470 L 610 470 L 610 610 L -10 610 Z", (-40, 470, 610, 610), ["#B8B2A8", "#7A746A"], 2521, n=60, angle=-2, length=(30, 90), width=(2, 6), opacity=(0.2, 0.4)))
    out.append(f'<rect y="466" width="600" height="8" fill="#C8C2B6"/>')
    out.append(specks(2522, (0, 470, 600, 560), ["#1E9A5A", "#FFFFFF", "#F28A2A", "#F6D21C"], 60, (1.5, 3), (0.7, 1)))
    # the parade, marching right: flag bearer, the big drum, children with little flags
    base = 534
    out.append(tricolour(D, 112, 300, 96, 60, 2523, wave=6, pole_len=226))
    out.append(figures.person(108, base, 150, "walk", 1, {"top_kind": "coat", "top": "#2E5A3E", "bottom": "#2A2A34", "hair_style": "long", "hair": "#8A3A1A", "form": "f"}, seed=2524, light=-1))
    band = {"top_kind": "jacket", "top": "#1E7A4A", "bottom": "#F2EEE4", "hat_kind": "cap", "hat": "#1E5A3A", "form": "m"}
    out.append(figures.person(270, base, 156, "walk", 1, band, seed=2525, light=-1))
    dcx, dcy = 300, base - 82
    out.append(painted(D, ell_pts(dcx, dcy, 24, 42, 0, 360, 24)[:-1], ("#FFFFFF", "#F2EEE4", "#B8B0A6"), 2526, sk=0.2, n=5, inkw=1.6, hi=0.4))
    out.append(f'<path d="{smooth_closed(ell_pts(dcx, dcy, 24, 42, 0, 360, 24)[:-1])}" fill="none" stroke="#1E7A4A" stroke-width="5"/>')
    for k in range(6):
        a_ = math.radians(k * 60)
        out.append(f'<path d="M {dcx + math.cos(a_) * 22:.1f} {dcy + math.sin(a_) * 39:.1f} L {dcx + math.cos(a_ + 0.5) * 22:.1f} {dcy + math.sin(a_ + 0.5) * 39:.1f}" stroke="#E8C060" stroke-width="1.4"/>')
    for k in range(3):
        a_ = -90 + k * 120
        out.append(f'<path d="{smooth_closed(heart_d(dcx + math.cos(math.radians(a_)) * 7, dcy + math.sin(math.radians(a_)) * 9, 8, a_ + 90))}" fill="#1E9A5A"/>')
    out.append(taper([(dcx - 30, dcy - 30), (dcx - 6, dcy - 8)], 3, 3, "#E8D8B0"))
    out.append(f'<circle cx="{dcx - 30}" cy="{dcy - 30}" r="5" fill="#F2EEE4" stroke="#6A5A3A" stroke-width="1"/>')
    for k, (x, pal, hat) in enumerate(((410, {"top": "#1E9A5A", "bottom": "#2E4A8A", "hat_kind": "beanie", "hat": "#1E9A5A"}, None),
                                        (492, {"top": "#F28A2A", "bottom": "#2A2A34", "hair_style": "ponytail", "hair": "#E8B040", "form": "f"}, None))):
        out.append(tricolour(D, x + 10, base - 148, 38, 24, 2528 + k, wave=3, pole_len=70))
        out.append(figures.person(x, base, 96, "child_walk", 1, pal, seed=2527 + k * 2, light=-1))
    # the crowd at the kerb, from behind
    for k, (x, h, pal) in enumerate(((20, 230, {"top_kind": "coat", "top": "#2E5A8A", "hair_style": "bun", "hair": "#3A2A1A", "form": "f"}),
                                      (590, 236, {"top_kind": "coat", "top": "#8A2A3A", "hair_style": "long", "hair": "#C86A2A", "form": "f"}))):
        out.append(figures.person(x, 720, h, "stand_back", 1, pal, seed=2540 + k, light=-1))
    out.append(letters(D, 300, 126, "Lá Fhéile Pádraig", SERIF_IT, 84, "#1E6A3E", ["#2E8A4E", "#0E4024", "#3E9A5A"], 2545, max_w=480,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, hi="#9AD0A8"))
    out.append(ruled(300, 172, "HAPPY ST. PATRICK'S DAY · 17 MARCH", "#C8601A", font=JOS, size=18, ls=3, line_w=18, gap=10, max_w=400))
    return finish_ie(D, out, 2546)


# ================================================================ 26. Samhain — a carved turnip lantern on the wall, the fires lit on the hill
def turnip_lantern(D, cx, cy, r, seed):
    """A carved turnip (swede) lantern: knobbly, purple-topped fading to cream, root tail, leaf stubs, a fierce
    carved face glowing from the candle inside, the cut rind showing its thickness."""
    rnd = random.Random(seed)
    o = [D.glow(cx, cy, r * 3.2, "#FF9A3A", 0.6)]
    pts = blob_pts(cx, cy, r, r * 0.92, seed, 0.07, 22)
    d = smooth_closed(pts)
    o.append(f'<path d="{d}" fill="#EAD8A0"/>')
    cid = D.clip(f'<path d="{d}"/>')
    g = D.lin([(0, "#7A3A7A"), (0.32, "#A86A9A"), (0.5, "#E8D8A8"), (1, "#D8C080")], 0, cy - r, 0, cy + r, "userSpaceOnUse")
    inner = [f'<rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" fill="{g}"/>']
    inner.append(strokes(D.nid(), d, (cx - r, cy - r, cx + r, cy + r), ["#5A2A5A", "#F2E6C0", "#C8A870", "#8A4A8A"], seed, n=60, angle=-80, length=(10, 30), width=(1, 3), opacity=(0.15, 0.4), curve=0.4))
    inner.append(shade_over(D, d, "#1A0A1A", 0.5, 0, 0, 1, 0.6, 0.4))
    inner.append(f'<path d="{blob(cx - r * 0.4, cy - r * 0.4, r * 0.25, r * 0.12, seed + 1, 0.2, 8, -40)}" fill="#FFFFFF" opacity="0.35"/>')
    for _ in range(14):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(0.3, 0.9) * r
        inner.append(f'<path d="M {cx + math.cos(a) * rr:.1f} {cy + math.sin(a) * rr:.1f} l {rnd.uniform(-5, 5):.1f} {rnd.uniform(1, 4):.1f}" stroke="#6A4A3A" stroke-width="1" opacity="0.5"/>')
    o.append(f'<g {cid}>{"".join(inner)}</g>')
    o.append(ink(d, "#3A1A2A", 2, seed, 2, 0.75))
    # leaf stubs and root
    for k, a in enumerate((-110, -90, -70)):
        x0, y0 = cx + math.cos(math.radians(a)) * r * 0.2, cy - r * 0.9
        o.append(taper([(x0, y0), (x0 + math.cos(math.radians(a)) * 18, y0 + math.sin(math.radians(a)) * 22)], 6, 3, "#6A7A3A"))
    o.append(taper([(cx + 4, cy + r * 0.9), (cx + 10, cy + r * 1.2), (cx + 4, cy + r * 1.42)], 6, 1, "#C8A870"))
    # carved face: eyes, nose, jagged mouth, with rind and glow
    feats = [[(cx - r * 0.5, cy - r * 0.12), (cx - r * 0.3, cy - r * 0.42), (cx - r * 0.12, cy - r * 0.1)],
             [(cx + r * 0.12, cy - r * 0.1), (cx + r * 0.3, cy - r * 0.42), (cx + r * 0.5, cy - r * 0.12)],
             [(cx - r * 0.07, cy + r * 0.12), (cx, cy - r * 0.02), (cx + r * 0.07, cy + r * 0.12)]]
    mouth = [(cx - r * 0.56, cy + r * 0.26)]
    for k in range(7):
        t = (k + 1) / 8
        mouth.append((cx - r * 0.56 + r * 1.12 * t, cy + r * (0.26 if k % 2 else 0.36)))
    mouth += [(cx + r * 0.56, cy + r * 0.26), (cx + r * 0.38, cy + r * 0.56), (cx, cy + r * 0.64), (cx - r * 0.38, cy + r * 0.56)]
    feats.append(mouth)
    for f in feats:
        o.append(f'<path d="{pd(shift(f, -2, 2))}" fill="#F2E6C0"/>')
        o.append(f'<path d="{pd(f)}" fill="#FFB43A"/>')
        o.append(f'<path d="{pd([(x + (cx - x) * 0.15, y + (cy - y) * 0.15) for x, y in f])}" fill="#FFF0A0" opacity="0.8"/>')
    return "".join(o)


@design("samhain")
def samhain():
    D = Doc2("ie-sa")
    out = [sky(D, [(0, "#1E1A3E"), (0.5, "#4A2A5A"), (0.85, "#C8604A"), (1, "#F2A050")], 3, 470, ["#3A2A5A", "#6A3A6A", "#E8804A"], 70, angle=-3, sop=(0.06, 0.16))]
    out.append(specks(2601, (0, 0, 600, 240), ["#FFFFFF"], 50, (0.6, 1.6), (0.4, 1)))
    # crescent moon
    out.append(soft_glow(D, 470, 230, 80, "#FFF2C8", 0.5))
    out.append(f'<path d="M 470 196 A 34 34 0 1 0 470 264 A 26 30 0 1 1 470 196 Z" fill="#FFF4D0"/>')
    # hill with the Samhain bonfire and figures
    out.append(hill(D, ridge([(-10, 420), (120, 380), (250, 360), (380, 386), (610, 400)], 2602, 6), 620, ("#3A2A3A", "#241A26", "#100A12"), 2602, inkw=0))
    out.append(D.glow(240, 350, 120, "#FF8A2A", 0.7))
    for k in range(6):
        out.append(flame_tongue(240 + (k - 2.5) * 8, 362, 16, 40 + (k % 3) * 14, (k - 2.5) * 3, 2603 + k))
    for k in range(10):
        out.append(f'<circle cx="{240 + random.Random(2610 + k).uniform(-30, 30):.1f}" cy="{random.Random(2620 + k).uniform(280, 330):.1f}" r="1.4" fill="#FFD27A"/>')
    for k, x in enumerate((196, 214, 272, 290)):
        out.append(figures.person(x, 370 - (1 if k % 2 else 0), 22, "stand", -1 if x > 240 else 1, "silhouette:#120A14", seed=2630 + k, rim="#FF9A3A", light=1 if x < 240 else -1))
    # crows on a bare thorn tree
    out.append(painted(D, limb([(530, 420), (520, 360), (500, 320), (470, 290)], [12, 8, 5, 3]), ("#3A2A2A", "#1E1418", "#0A0608"), 2640, sk=0.1, n=4, inkw=0, hi=0.2))
    out.append(painted(D, limb([(520, 360), (548, 330), (566, 300)], [6, 4, 2]), ("#3A2A2A", "#1E1418", "#0A0608"), 2641, sk=0.1, n=2, inkw=0, hi=0.2))
    for (x, y) in ((476, 286), (560, 296)):
        out.append(f'<path d="{blob(x, y - 6, 8, 6, 2642 + x, 0.1, 10)}" fill="#0A0608"/><circle cx="{x + 6}" cy="{y - 12}" r="4" fill="#0A0608"/><path d="M {x + 9} {y - 12} l 5 1 l -5 2 Z" fill="#3A3030"/>')
    # stone wall in front, lantern on top, apples beside
    out.append(stone_wall(D, -20, 620, 640, 470, 2650, s=26, pal=("#8A8090", "#5A5060", "#2A2230"), inkw=1.0, gap="#141018"))
    out.append(f'<rect y="440" width="600" height="200" fill="{D.rad([(0, "#FF9A3A", 0.35), (1, "#FF9A3A", 0)], 0.5, 0.2, 0.6)}"/>')
    out.append(turnip_lantern(D, 300, 392, 84, 2651))
    for k, (x, y) in enumerate(((150, 452), (182, 458), (448, 456))):
        out.append(painted(D, blob_pts(x, y, 14, 13, 2652 + k, 0.05, 12), ("#FF8A6A", "#C8281E", "#6A0A0A"), 2652 + k, sdir=(-0.6, 0.6), sk=0.25, n=4, inkw=1.2, hi=0.45))
        out.append(taper([(x, y - 12), (x + 2, y - 20)], 2.4, 1.6, "#4A2A10"))
    out.append(letters(D, 300, 128, "Samhain", SERIF_IT, 116, "#FFB45A", ["#FFD27A", "#E8762A", "#FFE6A0"], 2660, max_w=400,
                       shadow="#100818", soff=(0.02, 0.035), angle=-40, hi="#FFF2C0"))
    out.append(ruled(300, 176, "WHERE HALLOWEEN BEGAN", "#F2D8E8", font=JOS, size=21, ls=6, line_w=26, gap=12))
    return finish_ie(D, out, 2661, color="#100818")


# ================================================================ 27. Nollaig shona — a candle in the cottage window
@design("nollaig-shona")
def nollaig_shona():
    D = Doc2("ie-ns")
    out = [sky(D, [(0, "#101A3A"), (1, "#24305A")], 3, 260, ["#1E2A5A", "#3A4A7A"], 40, angle=-3, sop=(0.06, 0.14))]
    out.append(specks(2701, (0, 0, 600, 230), ["#FFFFFF", "#FFF2C0"], 70, (0.6, 1.8), (0.5, 1)))
    for (x, y, r) in ((90, 60, 6), (520, 90, 7), (470, 200, 5), (120, 210, 5)):
        out.append(sparkle(x, y, r, "#FFF4D0", 0.9))
    # the thatch eave, frosted
    eave = [(-20, 218), (620, 210), (620, 262), (-20, 270)]
    out.append(thatch(D, eave, 2702, bbox(eave), pal=("#C8A870", "#8A6A3E", "#4A3418"), moss=False))
    out.append(taper([(-20, 262), (300, 258), (620, 254)], 8, 8, "#3A2A14", 0.8))
    out.append(taper([(-20, 216), (300, 210), (620, 206)], 6, 6, "#E8F0FF", 0.7))
    # whitewashed wall in moonlight
    out.append(painted(D, rect_pts(-20, 262, 620, 640, 30, 2703, 0.6), ("#E8ECF6", "#C4CAE0", "#7A84A8"), 2703, sdir=(1, 0.3), sk=0.04, angle=-80, n=60, inkw=0, hi=0.2))
    out.append(f'<rect y="262" width="600" height="40" fill="{D.lin([(0, "#1A2040", 0.5), (1, "#1A2040", 0)])}"/>')
    # deep-set window glowing
    wx0, wx1, wy0, wy1 = 176, 424, 306, 500
    out.append(D.glow(300, 404, 300, "#FFB860", 0.55))
    out.append(f'<path d="{pd([(wx0 - 22, wy0 - 16), (wx1 + 22, wy0 - 16), (wx1, wy0), (wx0, wy0)])}" fill="#9AA0C0"/>')
    out.append(f'<path d="{pd([(wx0 - 22, wy0 - 16), (wx0, wy0), (wx0, wy1), (wx0 - 22, wy1 + 14)])}" fill="#E8C898"/>')
    out.append(f'<path d="{pd([(wx1 + 22, wy0 - 16), (wx1, wy0), (wx1, wy1), (wx1 + 22, wy1 + 14)])}" fill="#D8B888"/>')
    inside = D.rad([(0, "#FFE6A0"), (0.5, "#E8964A"), (1, "#8A3A1A")], 0.5, 0.75, 0.75)
    out.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="{inside}"/>')
    # lace curtains inside, the candle on the sill
    for sg, x0 in ((1, wx0), (-1, wx1)):
        cur = [(x0, wy0), (x0 + sg * 54, wy0), (x0 + sg * 40, wy0 + 90), (x0 + sg * 22, wy1), (x0, wy1)]
        out.append(f'<path d="{smooth_closed(cur)}" fill="#FFF6E0" opacity="0.75"/>')
    cx, cb = 300, wy1 - 6
    out.append(painted(D, ell_pts(cx, cb, 28, 7, 0, 360, 20)[:-1], ("#FFE8A0", "#D8A84A", "#8A6418"), 2704, sk=0.1, n=3, inkw=1.2, hi=0.5))
    out.append(painted(D, rect_pts(cx - 11, cb - 108, cx + 11, cb - 4, 8, 2705, 0.3), ("#FF8A7A", "#D8283A", "#7A0A1A"), 2705, sdir=(0.9, 0.3), sk=0.2, angle=-90, n=6, inkw=1.4, hi=0.55))
    out.append(D.glow(cx, cb - 128, 70, "#FFF2B0", 0.9))
    out.append(f'<path d="{smooth_closed([(cx, cb - 150), (cx + 8, cb - 126), (cx, cb - 110), (cx - 8, cb - 126)])}" fill="#FFC040"/>')
    out.append(f'<path d="{smooth_closed([(cx, cb - 140), (cx + 4, cb - 124), (cx, cb - 114), (cx - 4, cb - 124)])}" fill="#FFFBE0"/>')
    out.append(f'<path d="M {cx} {cb - 108} l 0 -6" stroke="#2A1A10" stroke-width="1.6"/>')
    # window bars and frost
    out.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1 - wx0}" height="{wy1 - wy0}" fill="none" stroke="#2A3050" stroke-width="7"/>')
    for t in (1 / 3, 2 / 3):
        out.append(f'<path d="M {wx0 + (wx1 - wx0) * t:.1f} {wy0} L {wx0 + (wx1 - wx0) * t:.1f} {wy1}" stroke="#2A3050" stroke-width="4.4"/>')
    out.append(f'<path d="M {wx0} {(wy0 + wy1) / 2:.1f} L {wx1} {(wy0 + wy1) / 2:.1f}" stroke="#2A3050" stroke-width="4.4"/>')
    for (x, y) in ((wx0 + 6, wy0 + 6), (wx1 - 6, wy0 + 6)):
        out.append(f'<path d="{blob(x, y, 26, 18, 2706 + int(x), 0.3, 10)}" fill="#FFFFFF" opacity="0.45"/>')
    # sill outside with snow and holly
    out.append(painted(D, rect_pts(wx0 - 30, wy1 + 2, wx1 + 30, wy1 + 22, 16, 2707, 0.4), ("#E8ECF6", "#B8C0D8", "#6A7498"), 2707, sdir=(0, 1), sk=0.2, angle=0, n=10, inkw=1.4, hi=0.4))
    out.append(f'<path d="{smooth_closed([(wx0 - 30, wy1 + 4), (wx0, wy1 - 4), (300, wy1 - 2), (wx1, wy1 - 6), (wx1 + 30, wy1 + 4)])}" fill="#FFFFFF"/>')
    for k, (x, a) in enumerate(((wx0 + 8, -20), (wx0 + 40, -150), (wx1 - 30, -30), (wx1 - 4, -160))):
        out.append(leaf_simple(D, x, wy1 - 2, 40, 10, a, ("#5A9A5A", "#2E6A3A", "#143A1E"), 2710 + k))
    for k, (x, y) in enumerate(((wx0 + 22, wy1 - 8), (wx0 + 30, wy1 - 14), (wx0 + 14, wy1 - 14), (wx1 - 18, wy1 - 10), (wx1 - 10, wy1 - 16))):
        out.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#D8202A" stroke="#6A0A10" stroke-width="1"/><circle cx="{x - 1.5}" cy="{y - 1.5}" r="1.4" fill="#FFFFFF"/>')
    out.append(specks(2715, (0, 0, 600, 600), ["#FFFFFF"], 60, (1, 2.6), (0.6, 0.95)))
    out.append(letters(D, 300, 124, "Nollaig shona", SERIF_IT, 96, "#F6D27A", ["#FFF0B0", "#C8902A", "#FFE08A"], 2716, max_w=460,
                       shadow="#08102A", soff=(0.02, 0.035), angle=-40, hi="#FFFFFF"))
    out.append(ruled(300, 172, "A CANDLE TO LIGHT THE WAY HOME", "#E8ECFF", font=JOS, size=19, ls=4, line_w=22, gap=10, max_w=400))
    return finish_ie(D, out, 2717, color="#08102A")



# ================================================================ 28. go raibh maith agat — a brown-paper parcel with a big thank-you tag
def heather_sprig(D, x, y, L, ang, seed):
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    o = [pline([(x, y), (x + ux * L, y + uy * L)], "#6A4A2A", 1.6, seed, 0.9, 1)]
    for k in range(16):
        t = 0.25 + k * 0.045
        px, py = x + ux * L * t, y + uy * L * t
        sg = 1 if k % 2 else -1
        o.append(f'<circle cx="{px - uy * sg * 3:.1f}" cy="{py + ux * sg * 3:.1f}" r="{rnd.uniform(2, 3):.1f}" fill="{rnd.choice(["#E8A8E0", "#C878C8", "#A85AA8"])}"/>')
        if k % 3 == 0:
            o.append(f'<path d="M {px:.1f} {py:.1f} l {-uy * sg * 7:.1f} {ux * sg * 7:.1f}" stroke="#5E7A3A" stroke-width="1.4"/>')
    return "".join(o)


@design("go-raibh-maith-agat")
def go_raibh_maith_agat():
    D = Doc2("ie-gm")
    out = [wood_planks(D, 0, 600, 2801, ("#E8C898", "#C8A070", "#7A5A30"), 5)]
    out.append(soft_glow(D, 300, 260, 380, "#FFF6E0", 0.35))
    # the parcel in brown paper, tied with string
    pc = [(70, 250), (540, 226), (556, 560), (64, 580)]
    out.append(f'<path d="{pd(shift(pc, 10, 14))}" fill="#3A2410" opacity="0.3"/>')
    out.append(painted(D, poly_pts(pc, 24, 2802, 0.8), ("#E8C08A", "#C8965A", "#7A5428"), 2802, sdir=(0.4, 1), sk=0.05, angle=-30, n=60, slen=(20, 70), sw=(1, 3), inkw=1.8, hi=0.25))
    rnd = random.Random(2803)
    for _ in range(10):
        x0, y0 = rnd.uniform(80, 520), rnd.uniform(250, 560)
        out.append(taper([(x0, y0), (x0 + rnd.uniform(-60, 60), y0 + rnd.uniform(-20, 20))], 0.6, 1.6, "#9A6A38", 0.5))
    out.append(pline([(70, 250), (300, 300), (556, 560)], "#A87840", 1.4, 2804, 0.4, 1))
    # string: twisted red-and-white baker's twine crossing the parcel
    for (a, b) in (((60, 400), (560, 384)), ((312, 230), (318, 574))):
        out.append(taper([a, b], 5, 5, "#FFFFFF"))
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        for k in range(int(L / 8)):
            t = k / (L / 8)
            px, py = lerp2(a, b, t)
            out.append(f'<path d="M {px - 2:.1f} {py + 2:.1f} l 4 -4" stroke="#C8302A" stroke-width="2"/>')
    # sprig of heather and shamrock tucked under the knot
    out.append(heather_sprig(D, 318, 392, 120, -150, 2805))
    out.append(heather_sprig(D, 318, 392, 100, -120, 2806))
    out.append(trefoil(D, 356, 360, 24, 20, 2807))
    out.append(pline([(330, 390), (356, 360)], "#4E6A2E", 1.8, 2808, 0.9, 1))
    # bow
    for sg in (-1, 1):
        lp = [(316, 392), (316 + sg * 40, 372), (316 + sg * 52, 392), (316 + sg * 38, 410)]
        out.append(f'<path d="{smooth_closed(lp)}" fill="none" stroke="#FFFFFF" stroke-width="5"/>')
        out.append(f'<path d="{smooth_closed(lp)}" fill="none" stroke="#C8302A" stroke-width="2" stroke-dasharray="3 3"/>')
        out.append(taper([(316, 394), (316 + sg * 26, 430), (316 + sg * 36, 462)], 5, 4, "#FFFFFF"))
    out.append(f'<circle cx="316" cy="392" r="7" fill="#FFFFFF" stroke="#C8302A" stroke-width="2"/>')
    # the big manila tag on its string
    tg = rot([(118, 92), (452, 92), (494, 150), (494, 300), (118, 300)], 300, 196, -4)
    out.append(f'<path d="{pd(shift(tg, 8, 10))}" fill="#3A2410" opacity="0.28"/>')
    out.append(painted(D, poly_pts(tg, 20, 2809, 0.5), ("#FFF2C8", "#F2DCA0", "#B89A5A"), 2809, sdir=(0.4, 1), sk=0.05, angle=-4, n=40, inkw=1.8, hi=0.3))
    hx, hy = rot([(458, 150)], 300, 196, -4)[0]
    out.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="13" fill="#E8C060" stroke="#8A6418" stroke-width="2"/><circle cx="{hx:.1f}" cy="{hy:.1f}" r="6" fill="#6A4A20"/>')
    out.append(pline([(hx, hy), (hx + 26, hy + 50), (hx - 10, hy + 120), (322, 388)], "#F2E6CC", 2, 2810, 1, 1))
    out.append(f'<g transform="rotate(-4 300 196)">')
    out.append(letters(D, 286, 170, "go raibh", SERIF_IT, 66, "#1E5A3A", ["#2E7A4E", "#0E3E24", "#3E8A5A"], 2811, max_w=300, wob=0.6, hi="#8ACB9A"))
    out.append(letters(D, 286, 236, "maith agat", SERIF_IT, 66, "#1E5A3A", ["#2E7A4E", "#0E3E24", "#3E8A5A"], 2812, max_w=320, wob=0.6, hi="#8ACB9A"))
    out.append(ruled(286, 276, "THANK YOU, FROM THE HEART", "#8A2A1A", font=JOS, size=16, ls=3, line_w=14, gap=8, max_w=300))
    out.append("</g>")
    # postage stamp and a postmark on the parcel
    def harp_art(x0, y0, x1, y1):
        a = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#2E6A4A"/>']
        for k in range(3):
            aa = -90 + k * 120
            a.append(f'<path d="{smooth_closed(heart_d((x0 + x1) / 2 + math.cos(math.radians(aa)) * 9, (y0 + y1) / 2 - 4 + math.sin(math.radians(aa)) * 9, 10, aa + 90))}" fill="#F6E8C0"/>')
        a.append(f'<path d="M {(x0 + x1) / 2} {(y0 + y1) / 2} l 2 16" stroke="#F6E8C0" stroke-width="2.4"/>')
        a.append(label((x0 + x1) / 2, y1 - 6, "ÉIRE", JOS, 11, "#F6E8C0", ls=1))
        return "".join(a)
    out.append('<g transform="rotate(5 462 470)">' + stamp(D, 420, 424, 84, 96, 2813, harp_art) + "</g>")
    out.append(f'<circle cx="408" cy="512" r="30" fill="none" stroke="#3A3A5A" stroke-width="2" opacity="0.5"/>')
    for k in range(3):
        out.append(f'<path d="M 330 {494 + k * 12} q 10 -5 20 0 t 20 0 t 20 0" stroke="#3A3A5A" stroke-width="1.8" fill="none" opacity="0.45"/>')
    return finish_ie(D, out, 2814)


# ================================================================ 29. the bog road — a donkey bringing home the turf at evening
def donkey(D, x, base, s, seed, flip=1, coat=("#C8B8A8", "#8E8074", "#4A4038")):
    """A grey-brown donkey side-on (facing right before flip): long ears, pale muzzle and belly, the dark
    cross on the shoulders, wicker creels of turf slung across its back."""
    rnd = random.Random(seed)
    o = [f'<ellipse cx="-2" cy="1.5" rx="64" ry="5.5" fill="#1A1A10" opacity="0.3"/>']
    far = tuple(dk(c, 0.2) for c in coat)
    o.append(taper(catmull([(-50, -86), (-60, -70), (-62, -46), (-58, -36)], 5), 3, 2, coat[2]))
    o.append(f'<path d="{blob(-58, -32, 4, 7, seed, 0.2, 8)}" fill="#2A2420"/>')
    for ctr, ws in (([(40, -50), (44, -30), (48, -10), (50, 0)], (10, 8, 6, 7)), ([(-30, -56), (-38, -36), (-36, -12), (-34, 0)], (14, 10, 6, 7))):
        o.append(painted(D, limb(ctr, ws), far, seed + int(ctr[0][0]), sk=0.15, angle=-90, n=4, inkw=0.9, inkop=0.5, hi=0.2))
        o.append(f'<path d="{blob(ctr[-1][0] + 1, -2.5, 4.5, 2.8, seed, 0.1, 8)}" fill="#2A2424"/>')
    body = [(54, -64), (50, -48), (36, -44), (6, -42), (-26, -44), (-44, -52), (-54, -66), (-54, -82), (-44, -90), (-20, -88), (6, -86), (30, -90), (50, -84), (58, -74)]
    o.append(painted(D, body, coat, seed, sdir=(0.3, 1), sk=0.14, angle=-10, n=36, slen=(8, 24), sw=(1, 3), inkw=1.3, inkop=0.6, hi=0.35))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    o.append(f'<g {cid}><path d="{blob(0, -46, 40, 8, seed + 2, 0.2, 10)}" fill="#F2EAE0" opacity="0.7"/></g>')
    neck = [(30, -88), (46, -102), (62, -114), (72, -112), (74, -96), (66, -74), (52, -66)]
    o.append(painted(D, neck, coat, seed + 1, sk=0.12, angle=-55, n=14, inkw=1.2, inkop=0.6, hi=0.4))
    head = [(62, -118), (72, -122), (84, -112), (98, -96), (104, -86), (100, -78), (88, -78), (78, -88), (66, -100)]
    o.append(painted(D, head, coat, seed + 2, sk=0.12, angle=-50, n=10, inkw=1.2, inkop=0.6, hi=0.4))
    o.append(painted(D, [(92, -96), (104, -88), (102, -78), (88, -78), (86, -88)], ("#FFFFFF", "#ECE6DE", "#B8B0A6"), seed + 3, sk=0.1, n=2, inkw=0, hi=0.3))
    o.append(f'<path d="{blob(99, -86, 1.8, 1.2, seed, 0.1, 6, 40)}" fill="#2A2420"/>')
    o.append(f'<circle cx="78" cy="-106" r="2.8" fill="#1A1210"/><circle cx="77.3" cy="-106.8" r="0.8" fill="#FFFFFF"/>')
    o.append(f'<path d="{blob(78, -106, 5, 4, seed + 4, 0.1, 8)}" fill="none" stroke="#F2EAE0" stroke-width="1.4" opacity="0.7"/>')
    for k, (ex, ang) in enumerate(((64, -20), (70, 10))):
        ear = rot([(ex - 4, -116), (ex - 2, -150), (ex + 4, -152), (ex + 6, -118)], ex, -116, ang)
        o.append(painted(D, ear, coat if k else far, seed + 5 + k, sk=0.15, n=3, inkw=1.1, hi=0.3))
        o.append(f'<path d="{smooth_closed(rot([(ex - 1, -122), (ex, -144), (ex + 2, -122)], ex, -116, ang))}" fill="#2A2420" opacity="0.6"/>')
    for k in range(10):
        t = k / 9
        mx, my = lerp(32, 66, t), lerp(-90, -116, t)
        o.append(taper([(mx, my), (mx - 1, my - 7)], 3, 1, "#3A3028", 0.9))
    o.append(taper([(36, -90), (36, -62)], 4, 2, "#3A3028", 0.5))
    for ctr, ws in (([(46, -54), (42, -34), (42, -12), (44, 0)], (11, 8, 6, 7)), ([(-36, -58), (-44, -38), (-40, -12), (-38, 0)], (16, 11, 6, 7))):
        o.append(painted(D, limb(ctr, ws), coat, seed + 50 + int(ctr[0][0]), sk=0.15, angle=-90, n=5, inkw=1.0, inkop=0.55, hi=0.3))
        o.append(f'<path d="{blob(ctr[-1][0] + 1, -2.5, 4.8, 3, seed, 0.1, 8)}" fill="#2A2424"/>')
    # creels of turf slung over the back
    for k, (cx_, top_) in enumerate(((-6, -104),)):
        cr = [(cx_ - 34, top_ + 6), (cx_ + 34, top_ + 6), (cx_ + 30, top_ + 54), (cx_ - 28, top_ + 54)]
        for j in range(7):
            o.append(turf_sod(D, cx_ - 26 + j * 9, top_ + 4 - (j % 2) * 4, 12, 22, seed + 60 + j, -10 + j * 4))
        o.append(painted(D, poly_pts(cr, 8, seed + 70, 0.5), ("#E8C08A", "#B8864A", "#6A4A1A"), seed + 70, sk=0.15, angle=0, n=8, inkw=1.4, hi=0.35))
        for j in range(5):
            y = top_ + 12 + j * 9
            o.append(pline([(cx_ - 32 + j * 0.5, y), (cx_, y + 2), (cx_ + 32 - j * 0.6, y)], "#6A4A1A", 1.2, seed + j, 0.6, 1))
        for j in range(6):
            o.append(pline([(cx_ - 28 + j * 11, top_ + 8), (cx_ - 26 + j * 10.5, top_ + 52)], "#8A6430", 1, seed + 80 + j, 0.5, 1))
    return f'<g transform="translate({x:.1f} {base:.1f}) scale({s * flip:.3f} {s:.3f})">' + "".join(o) + "</g>"


def turf_footing(D, x, base, s, seed):
    o = [cast(D, x + 3, base, 16 * s, 3 * s, strength=0.4, seed=seed)]
    for k, (dx, a) in enumerate(((-6, 18), (6, -18), (0, 2))):
        o.append(turf_sod(D, x + dx * s, base - 12 * s, 7 * s, 22 * s, seed + k, a))
    return "".join(o)


@design("the-bog-road")
def the_bog_road():
    D = Doc2("ie-br")
    out = [sky(D, [(0, "#6A6AA8"), (0.4, "#D89AA0"), (0.75, "#F6C08A"), (1, "#FFE6A8")], 3, 360, ["#FFFFFF", "#E8A898", "#8A80B0"], 60, angle=-2, sop=(0.05, 0.14))]
    out.append(soft_glow(D, 420, 330, 200, "#FFF0C0", 0.7))
    rnd = random.Random(2901)
    for k in range(7):
        y = rnd.uniform(210, 300)
        x = rnd.uniform(-40, 500)
        out.append(taper([(x, y), (x + 80, y - 2), (x + 170, y + 1)], 1, rnd.uniform(4, 8), rnd.choice(["#FFD0A0", "#E89A9A", "#B88AB0"]), 0.65))
    out.append(hill(D, ridge([(-10, 332), (80, 296), (170, 316), (260, 286), (360, 318), (470, 300), (610, 326)], 2902, 6), 400, ("#8A7AA0", "#5E5280", "#3A3058"), 2902, inkw=0))
    out.append(hill(D, ridge([(-10, 352), (200, 344), (400, 350), (610, 342)], 2903, 3), 640, ("#B89A5A", "#8A6E3A", "#4E3E22"), 2903, inkw=0, n=60))
    # bog pools reflecting the sky
    for k, (x, y, w) in enumerate(((90, 380, 70), (480, 372, 90), (200, 404, 50), (420, 420, 60))):
        out.append(f'<path d="{blob(x, y, w, 7 + k, 2904 + k, 0.3, 14)}" fill="#E8B898"/><path d="{blob(x, y - 1, w * 0.85, 5 + k, 2924 + k, 0.3, 14)}" fill="#F6CCA8"/><path d="{blob(x - 6, y - 2, w * 0.5, 1.6, 2908 + k, 0.2, 10)}" fill="#FFF0D0" opacity="0.8"/>')
    for k in range(6):
        y = 380 + k * 34
        out.append(strokes(D.nid(), f"M -10 {y} L 610 {y} L 610 {y + 30} L -10 {y + 30} Z", (-40, y, 610, y + 30), ["#6A5A2A", "#A8864A", "#4A3A1A", "#8A6A9A"], 2910 + k, n=40, angle=-2, length=(20, 70), width=(2, 6), opacity=(0.2, 0.45)))
    # turf footings and a long clamp of turf
    for k in range(9):
        x, y = rnd.uniform(30, 570), rnd.uniform(370, 430)
        out.append(turf_footing(D, x, y, 0.55 + (y - 370) / 120, 2920 + k * 5))
    clamp = rect_pts(400, 404, 556, 440, 10, 2970, 0.6)
    for j in range(3):
        for i in range(12):
            out.append(turf_sod(D, 408 + i * 12.5, 432 - j * 12, 12, 10, 2971 + j * 20 + i, 0))
    out.append(f'<path d="{smooth_closed([(400, 402), (556, 400), (556, 398), (400, 400)])}" fill="#3A2414"/>')
    # the bog road, a cut bank of turf at its side
    road = [(-10, 600), (230, 600), (320, 470), (360, 400), (372, 360), (380, 360), (380, 400), (380, 470), (330, 600), (610, 610), (610, 640), (-10, 640)]
    rd = [(96, 612), (210, 524), (296, 450), (346, 394), (366, 358), (374, 358), (372, 392), (362, 450), (386, 524), (450, 612)]
    out.append(painted(D, rd, ("#E8D4A8", "#C8AC7A", "#7A6440"), 2980, sk=0.05, angle=-80, n=30, inkw=0.8, inkop=0.4, hi=0.3))
    out.append(specks(2981, (150, 380, 380, 600), ["#8A7448", "#F2E2C0"], 50, (0.8, 2), (0.4, 0.8)))
    out.append(taper([(110, 610), (218, 522), (300, 452), (350, 392)], 3, 1, "#6A5A3A", 0.5))
    # heather and bog cotton along the verges
    for k in range(26):
        x, y = rnd.uniform(0, 600), rnd.uniform(430, 600)
        if 100 < x < 440 and y > 470:
            continue
        out.append(heather_clump(D, x, y, rnd.uniform(12, 22) * (0.6 + (y - 430) / 250), 2990 + k))
    out.append(donkey(D, 250, 540, 1.75, 3020, flip=-1))
    for k in range(12):
        x, y = rnd.uniform(10, 590), rnd.uniform(520, 600)
        if 160 < x < 330:
            continue
        out.append(bog_cotton(x, y, rnd.uniform(18, 30), 3030 + k))
    out.append(grass(3050, (0, 520, 600, 600), ["#6A7A3A", "#9AAA5A", "#4A5A2A", "#B8A060"], n=110, h=(8, 20)))
    out.append(letters(D, 300, 128, "the bog road", SERIF_IT, 100, "#3A1E3E", ["#5A2E5E", "#22102A", "#6A3A6E"], 3051, max_w=440,
                       shadow="#FFE0C8", soff=(0.02, 0.03), angle=-40, hi="#C890C0"))
    out.append(ruled(300, 174, "TURF, HEATHER & BOG COTTON", "#FFF4E0", font=JOS, size=19, ls=4, line_w=22, gap=10, max_w=390))
    return finish_ie(D, out, 3052)


# ================================================================ 30. the Giant's Causeway — basalt columns stepping into the sea
@design("giants-causeway")
def giants_causeway():
    D = Doc2("ie-gc")
    out = [sky(D, [(0, "#5E7AA0"), (0.5, "#A8BED0"), (1, "#E8E6DC")], 3, 330, ["#FFFFFF", "#7A90B0", "#E8E2D6"], 60, angle=-4, sop=(0.06, 0.16))]
    out.append(puff_cloud(D, 460, 236, 170, 3101, ("#FFFFFF", "#E8ECF0", "#8A98B0")))
    out.append(soft_glow(D, 200, 250, 200, "#FFF6E0", 0.4))
    # the sea and the headlands of the Causeway coast
    out.append(sea(D, 318, 600, [(0, "#4E7A9A"), (1, "#1E4060")], 3102, ["#FFFFFF", "#123050", "#8AB8D0"], n=80, ticks=["#FFFFFF", "#C8E0EC"]))
    out.append(hill(D, ridge([(-10, 250), (60, 236), (140, 258), (210, 290), (250, 318)], 3103, 5) + [(250, 320)], 330, ("#7A6A5A", "#4E4238", "#2A221C"), 3103, inkw=1, inkop=0.4))
    out.append(f'<path d="{smooth_closed([(-10, 252), (60, 238), (140, 260), (130, 262), (60, 244), (-10, 258)])}" fill="#6E9A4A"/>')
    for k in range(8):
        x = 20 + k * 26
        out.append(pline([(x, 262 + k * 6), (x + 2, 318)], "#2A221C", 1.2, 3104 + k, 0.5, 1))
    # the columns: a hexagonal pavement, highest at the cliff foot, stepping down into the sea
    rnd = random.Random(3105)
    cells = []
    y = 322
    j = 0
    while y < 660:
        R = 12 + (y - 322) * 0.09
        for i in range(-3, 40):
            cx = i * R * 1.52 + (j % 2) * R * 0.76 - 20
            edge = 300 + (y - 330) * 0.95 + rnd.uniform(-20, 20)
            if cx > edge or cx < -40:
                continue
            hgt = max(4, 150 - cx * 0.42 - (y - 322) * 0.2 + rnd.uniform(-26, 26)) * (R / 26)
            cells.append((y, cx, hgt, R))
        y += R * 0.62
        j += 1
    for cy, cx, hgt, R in sorted(cells):
        tyc = cy - hgt
        top = [(cx + R * math.cos(math.radians(a)), tyc + R * 0.55 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
        top = [(x + rnd.uniform(-0.8, 0.8), y_ + rnd.uniform(-0.4, 0.4)) for x, y_ in top]
        bot = cy + R * 2
        for (a_, b_), shade in (((top[2], top[3]), "#2A2630"), ((top[1], top[2]), "#3E3844"), ((top[0], top[1]), "#4E4854")):
            face = [a_, b_, (b_[0], bot), (a_[0], bot)]
            out.append(f'<path d="{pd(face)}" fill="{shade}"/>')
        for k in range(1, int(hgt / (R * 0.9)) + 1):
            yy = tyc + k * R * 0.9
            out.append(f'<path d="M {top[3][0]:.1f} {yy:.1f} L {top[2][0]:.1f} {yy + R * 0.5:.1f} L {top[1][0]:.1f} {yy + R * 0.5:.1f} L {top[0][0]:.1f} {yy:.1f}" stroke="#14121A" stroke-width="0.8" fill="none" opacity="0.45"/>')
        c = mix("#8E847A", rnd.choice(["#AE9E8A", "#6E6660", "#9A8E80", "#BEB09C"]), rnd.uniform(0, 0.6))
        td = pd(top)
        out.append(f'<path d="{td}" fill="{c}"/>')
        out.append(f'<path d="{pd([(cx + (x - cx) * 0.75, y_ - 1) for x, y_ in top[3:] + top[:1]])}" fill="#FFFFFF" opacity="0.14"/>')
        if rnd.random() < 0.16:
            out.append(f'<path d="{blob(cx, tyc + 1, R * 0.55, R * 0.2, rnd.randint(0, 999), 0.2, 10)}" fill="#A8C4D8" opacity="0.85"/><path d="{blob(cx - 3, tyc, R * 0.25, R * 0.06, rnd.randint(0, 999), 0.2, 8)}" fill="#FFFFFF" opacity="0.8"/>')
        out.append(f'<path d="{td}" fill="none" stroke="#1E1A20" stroke-width="{max(0.8, R * 0.05):.1f}" stroke-linejoin="round"/>')
    # surf breaking on the outer columns
    for k in range(18):
        x, y = rnd.uniform(280, 600), rnd.uniform(340, 600)
        if x < 330 + (y - 330) * 0.9 - 10:
            continue
        out.append(f'<path d="{blob(x, y, rnd.uniform(8, 20), rnd.uniform(3, 6), 3110 + k, 0.3, 10)}" fill="#FFFFFF" opacity="{rnd.uniform(0.5, 0.9):.2f}"/>')
    out.append(wave_lines(3130, (300, 330, 600, 600), ["#FFFFFF"], 40, L=(10, 30), w=2.2, amp=2))
    for (x, y, sz) in ((360, 236, 8), (390, 250, 6), (140, 210, 7)):
        out.append(seagull(x, y, sz, "#2A3A4A", 0.85))
    out.append(letters(D, 300, 126, "Giant's Causeway", DMS, 76, "#1E2E4A", ["#2E4A6A", "#0E1A30", "#3E5A7A"], 3140, max_w=470,
                       shadow="#FFFFFF", soff=(0.018, 0.03), angle=-40, wob=0.5))
    out.append(ruled(300, 170, "CLOCHÁN AN AIFIR · CO. ANTRIM", "#7A2A1A", font=JOS, size=19, ls=4, line_w=22, gap=10, max_w=390))
    return finish_ie(D, out, 3141)


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
