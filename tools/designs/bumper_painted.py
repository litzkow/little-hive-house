"""Bumper Stickers, hand-painted edition.

Thirty fridge magnets, each one a real vintage bumper sticker or retro decal stuck onto a painted scene: the
sticker is printed vinyl (white die-cut margin, slight sun fade, scuffs and chips, a gloss streak, often a
peeling corner) sitting on a gouache background (chrome bumpers, tailgates, wood-panel wagons, a rear window,
a dashboard, highways and parking lots). Each sticker carries designed retro type (Anton, Bebas, Josefin,
Playfair italic) and a small painted illustration. Repaints the ten original slugs (same words) and adds
twenty new ones.

Run from tools/designs:  python3 bumper_painted.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_gouache_a import (bbox, blooms, cast, catmull, dab_crown, finish, grass, hill, mix, painted, pline, qpts, ridge, shift, sky,
                            soft_glow, specks, steam_wisps)
from fall_gouache_a import taper as _taper
from fall_painted import Doc
from gouache import blob, blob_pts, ink, jitter, smooth_closed, smooth_open, strokes, wash
from poster import ANTON
from summer_gouache import (canoe, daisy, palm, puff_cloud, rot, seagull, sparkle, stripes_in, sun_disc, wave_lines)

COL = "bumper-stickers"
INK = "#3A2418"
VINYL = "#FFFDF6"

# (light, base, dark) palettes
RED = ("#F0705A", "#D23A2C", "#8A1A16")
CHERRY = ("#F2665A", "#C8282A", "#6E0E12")
CREAM = ("#FFFBF0", "#F6EDD8", "#C8B490")
MUSTARD = ("#FFD870", "#F2B430", "#B07A12")
NAVY = ("#4A6A9A", "#1F3A62", "#0C1C36")
TEAL = ("#7AD8CC", "#2AA59A", "#0E5E58")
MINT = ("#CFF2E0", "#8ED8BC", "#3A9A80")
PINK = ("#FFC2CC", "#F48AA0", "#B04A66")
CORAL = ("#FFA08A", "#FF6F59", "#C23C2E")
ORANGE = ("#FFC07A", "#FF8A2A", "#C0520E")
OLIVE = ("#B8C27A", "#7A8A3E", "#46521E")
PLUM = ("#A07AC0", "#5E3A86", "#2E1A4A")
SKY = ("#D4F0FF", "#86CDEB", "#3A8AB8")
WOOD = ("#E2B07A", "#B87A44", "#6E4422")
CHROME = ("#FFFFFF", "#C8D2DA", "#5A6470")
BLACK = ("#5A5260", "#2A2430", "#0E0A12")

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


def taper(pts, w0, w1, color, op=1.0, step=10):
    """Tapered brush mark; segments are densified first so the closed spline cannot overshoot the ends."""
    dense = [pts[0]]
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x2 - x1, y2 - y1) / step))
        dense += [(x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n) for i in range(1, n + 1)]
    return _taper(dense, w0, w1, color, op)


# ================================================================ geometry
def rrect(x0, y0, x1, y1, r, step=14):
    """Rounded rectangle outline as dense points (clockwise in screen space)."""
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    pts = []

    def edge(a, b):
        n = max(1, int(math.dist(a, b) / step))
        return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n)]

    def arc(cx, cy, a0):
        if r <= 0:
            return [(cx, cy)]
        return [(cx + r * math.cos(math.radians(a0 + k * 15)), cy + r * math.sin(math.radians(a0 + k * 15))) for k in range(6)]

    pts += edge((x0 + r, y0), (x1 - r, y0)) + arc(x1 - r, y0 + r, -90)
    pts += edge((x1, y0 + r), (x1, y1 - r)) + arc(x1 - r, y1 - r, 0)
    pts += edge((x1 - r, y1), (x0 + r, y1)) + arc(x0 + r, y1 - r, 90)
    pts += edge((x0, y1 - r), (x0, y0 + r)) + arc(x0 + r, y0 + r, 180)
    return pts


def oval(cx, cy, rx, ry, n=56):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def poly(corners, step=14):
    """Polygon with straight edges sampled densely (keeps edges straight under Catmull-Rom smoothing)."""
    out = []
    for k in range(len(corners)):
        a, b = corners[k], corners[(k + 1) % len(corners)]
        n = max(1, int(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n)]
    return out


def area(pts):
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1])) / 2


def offset(pts, m):
    """Offset a dense closed outline outward by m (vertex normals)."""
    sgn = 1 if area(pts) > 0 else -1
    n = len(pts)
    out = []
    for i in range(n):
        ax, ay = pts[i - 1]
        bx, by = pts[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy) or 1
        nx, ny = dy / L * sgn, -dx / L * sgn
        out.append((pts[i][0] + nx * m, pts[i][1] + ny * m))
    return out


def centroid(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2


def P(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def lpath(pts, close=True):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + (" Z" if close else "")


def _cap(pts, q, n):
    """Part of polygon on the + side of the line through q with normal n (Sutherland-Hodgman)."""
    def s(p):
        return (p[0] - q[0]) * n[0] + (p[1] - q[1]) * n[1]
    out = []
    for i in range(len(pts)):
        a, b = pts[i - 1], pts[i]
        sa, sb = s(a), s(b)
        if sb > 0:
            if sa <= 0:
                t = sa / (sa - sb)
                out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            out.append(b)
        elif sa > 0:
            t = sa / (sa - sb)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


# ================================================================ the sticker
def face_fill(D, d, pts, pal, seed, angle=0, fade=0.22, n=None):
    """Printed vinyl face: flat ink colour with a whisper of brush texture and a sun-faded corner."""
    light, base, dark = pal
    x0, y0, x1, y1 = bbox(pts)
    out = [f'<path d="{d}" fill="{base}"/>']
    out.append(strokes(D.nid(), d, (x0 - 20, y0 - 10, x1 + 20, y1 + 10), [light, dark, base], seed, n=n or int((x1 - x0) * (y1 - y0) / 900),
                       angle=angle, length=(30, 110), width=(3, 9), opacity=(0.05, 0.16), curve=0.08))
    if fade:
        g = D.lin([(0, "#FFFFFF", fade), (0.45, "#FFFFFF", 0), (1, dark, fade * 0.6)], 0, 0, 1, 1)
        out.append(f'<path d="{d}" fill="{g}"/>')
    return "".join(out)


def sticker(D, pts, face, content="", *, rot_=0, margin=9, vinyl=VINYL, shadow=(5, 8, 0.34), peel=None, seed=1,
            wear=1.0, gloss=0.11, edge_ink=INK, print_edge=None, top="", clip_content=True):
    """A vinyl sticker: cast shadow, white die-cut margin, printed face (clipped), content, wear, gloss, edge ink,
    and an optional peeling flap. peel = (angle_deg, depth): cut the outline where it reaches furthest along
    `angle` and fold that cap back."""
    cx, cy = centroid(pts)
    d = smooth_closed(pts)
    outer = offset(pts, margin)
    od = smooth_closed(outer)
    rnd = random.Random(seed)
    g = [f'<g transform="rotate({rot_} {cx:.1f} {cy:.1f})">']
    keep = ""
    flap = ""
    if peel:
        ang, depth = peel
        n = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
        mx = max(p[0] * n[0] + p[1] * n[1] for p in outer)
        q = (n[0] * (mx - depth), n[1] * (mx - depth))
        t = (-n[1], n[0])
        big = [(q[0] + t[0] * 3000, q[1] + t[1] * 3000), (q[0] - t[0] * 3000, q[1] - t[1] * 3000),
               (q[0] - t[0] * 3000 - n[0] * 3000, q[1] - t[1] * 3000 - n[1] * 3000), (q[0] + t[0] * 3000 - n[0] * 3000, q[1] + t[1] * 3000 - n[1] * 3000)]
        keep = D.clip(f'<polygon points="{P(big)}"/>')
        cap = _cap(outer, q, n)
        if len(cap) > 2:
            fl = []
            for p in cap:
                s_ = (p[0] - q[0]) * n[0] + (p[1] - q[1]) * n[1]
                fl.append((p[0] - n[0] * s_ * 1.82, p[1] - n[1] * s_ * 1.82))
            fd = lpath(fl)
            gx = D.lin([(0, "#FFFFFF"), (0.55, "#F1ECE2"), (1, "#CFC6B6")], q[0], q[1], q[0] - n[0] * depth, q[1] - n[1] * depth, "userSpaceOnUse")
            sx, sy = shadow[0] * 0.7, shadow[1] * 0.7
            flap = (f'<path d="{fd}" fill="#1A1008" opacity="0.28" transform="translate({sx:.1f} {sy:.1f})"/>'
                    f'<path d="{fd}" fill="{gx}"/>'
                    + ink(fd, INK, 1.6, seed + 7, 1, 0.55)
                    + f'<path d="M {cap[0][0]:.1f} {cap[0][1]:.1f} L {cap[-1][0]:.1f} {cap[-1][1]:.1f}" stroke="#FFFFFF" stroke-width="2" opacity="0.9"/>')
    g.append(f'<g {keep}>' if keep else "<g>")
    # cast shadow: three soft copies (margins drawn as round-joined strokes so concave cuts offset cleanly)
    sx, sy, so = shadow
    mw = 2 * margin
    for k, a in ((0.45, 0.5), (1.0, 0.45), (1.7, 0.22)):
        g.append(f'<path d="{d}" fill="#1A1008" stroke="#1A1008" stroke-width="{mw}" stroke-linejoin="round" opacity="{so * a:.2f}" transform="translate({sx * k:.1f} {sy * k:.1f})"/>')
    # die-cut edge line, then the vinyl margin
    g.append(f'<path d="{d}" fill="{edge_ink}" stroke="{edge_ink}" stroke-width="{mw + 3}" stroke-linejoin="round" opacity="0.42"/>')
    g.append(f'<path d="{d}" fill="{vinyl}" stroke="{vinyl}" stroke-width="{mw}" stroke-linejoin="round"/>')
    vg = D.lin([(0, "#FFFFFF", 0.0), (1, "#B8A88A", 0.25)])
    g.append(f'<path d="{d}" fill="{vg}" stroke="{vg}" stroke-width="{mw}" stroke-linejoin="round"/>')
    cid = D.clip(f'<path d="{d}"/>')
    g.append(f'<g {cid}>{face}{content if clip_content else ""}</g>')
    if not clip_content:
        g.append(content)
    if print_edge:
        g.append(ink(d, print_edge, 1.4, seed + 3, 1, 0.5))
    g.append(top)
    # wear: scratches, chips of missing ink, grime, clipped to the sticker
    oid = D.clip(f'<path d="{od}"/>')
    x0, y0, x1, y1 = bbox(outer)
    A = (x1 - x0) * (y1 - y0)
    w = []
    for _ in range(int(A / 2600 * wear)):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        L = rnd.uniform(5, 28)
        a = math.radians(rnd.choice([-35, -30, 150, 20, -150]) + rnd.uniform(-15, 15))
        w.append(f'<path d="M {x:.1f} {y:.1f} l {L * math.cos(a):.1f} {L * math.sin(a):.1f}" stroke="#FFFFFF" stroke-width="{rnd.uniform(0.8, 1.7):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.18, 0.45):.2f}"/>')
    for _ in range(int(A / 3200 * wear)):
        i = rnd.randrange(len(pts))
        px, py = pts[i]
        k = rnd.uniform(0, 1) ** 2
        x, y = px + (cx - px) * k * 0.25, py + (cy - py) * k * 0.25
        r = rnd.uniform(1, 3.6)
        w.append(f'<path d="{blob(x, y, r, r * rnd.uniform(0.5, 1), rnd.randint(0, 9999), 0.3, 7)}" fill="{vinyl}" opacity="{rnd.uniform(0.55, 0.95):.2f}"/>')
    for _ in range(int(A / 1800 * wear)):
        w.append(f'<circle cx="{rnd.uniform(x0, x1):.1f}" cy="{rnd.uniform(y0, y1):.1f}" r="{rnd.uniform(0.5, 1.3):.1f}" fill="#3A2A1A" opacity="{rnd.uniform(0.08, 0.25):.2f}"/>')
    if gloss:
        W = x1 - x0
        gb = [(x0 + W * 0.18, y0 - 40), (x0 + W * 0.30, y0 - 40), (x0 + W * 0.12, y1 + 40), (x0 - W * 0.0, y1 + 40)]
        gb2 = [(x0 + W * 0.34, y0 - 40), (x0 + W * 0.37, y0 - 40), (x0 + W * 0.19, y1 + 40), (x0 + W * 0.16, y1 + 40)]
        w.append(f'<polygon points="{P(gb)}" fill="#FFFFFF" opacity="{gloss:.2f}"/><polygon points="{P(gb2)}" fill="#FFFFFF" opacity="{gloss * 0.8:.2f}"/>')
    g.append(f'<g {oid}>{"".join(w)}</g>')
    g.append("</g>")
    g.append(flap)
    g.append("</g>")
    return "".join(g)


# ================================================================ lettering
def vt(D, x, y, s, font, size, fill, seed, max_w=470, ls=0, shadow=None, soff=(0.035, 0.05), outline=None, ow=0.12,
       tints=None, wob=0.35, rotate=0, hi=None, density=0.7, anchor="middle"):
    """Printed retro lettering: fixed glyph placement with a hint of hand wobble, optional thick outline (keyline)
    and an offset drop shadow in a second ink, filled with faint brush texture like worn screen print."""
    fs = fit_size(s, font, size, max_w, ls)
    W = measure(s, font, fs, ls)
    rnd = random.Random(seed)
    gx = x - W / 2 if anchor == "middle" else (x if anchor == "start" else x - W)
    x_mid = gx + W / 2
    glyphs = []
    for ch in s:
        adv = measure(ch, font, fs) + ls
        if ch != " ":
            r = rnd.uniform(-1.4, 1.4) * wob
            dy = rnd.uniform(-1, 1) * wob * fs / 70
            glyphs.append(f'<text x="{gx:.1f}" y="{y + dy:.1f}" {font} font-size="{fs}" transform="rotate({r:.2f} {gx + adv / 2:.1f} {y:.1f})">{esc(ch)}</text>')
        gx += adv
    G = "".join(glyphs)
    tr = f' transform="rotate({rotate} {x_mid:.1f} {y:.1f})"' if rotate else ""
    out = [f"<g{tr}>"]
    if shadow:
        sx, sy = fs * soff[0], fs * soff[1]
        if outline:
            out.append(f'<g fill="{shadow}" stroke="{shadow}" stroke-width="{fs * ow * 2:.1f}" stroke-linejoin="round" transform="translate({sx:.1f} {sy:.1f})">{G}</g>')
        else:
            out.append(f'<g fill="{shadow}" transform="translate({sx:.1f} {sy:.1f})">{G}</g>')
    if outline:
        out.append(f'<g fill="{outline}" stroke="{outline}" stroke-width="{fs * ow * 2:.1f}" stroke-linejoin="round">{G}</g>')
    out.append(f'<g fill="{fill}">{G}</g>')
    tints = tints or [mix(fill, "#FFFFFF", 0.3), mix(fill, "#000000", 0.18), fill]
    uid = D.nid()
    st = []
    for _ in range(int(W * fs / 260 * density) + 16):
        px, py = rnd.uniform(x_mid - W / 2 - 10, x_mid + W / 2 + 10), rnd.uniform(y - fs * 0.95, y + fs * 0.2)
        L = rnd.uniform(fs * 0.15, fs * 0.5)
        ww = rnd.uniform(fs * 0.02, fs * 0.06)
        a = math.radians(-60 + rnd.uniform(-12, 12))
        dx, dy = L * math.cos(a), L * math.sin(a)
        nx, ny = -math.sin(a), math.cos(a)
        mx, my = px + dx / 2, py + dy / 2
        st.append(f'<path d="M {px:.1f} {py:.1f} Q {mx + nx * ww:.1f} {my + ny * ww:.1f} {px + dx:.1f} {py + dy:.1f} Q {mx - nx * ww:.1f} {my - ny * ww:.1f} {px:.1f} {py:.1f} Z" '
                  f'fill="{rnd.choice(tints)}" opacity="{rnd.uniform(0.12, 0.35):.2f}"/>')
    if hi:
        for _ in range(int(len(s) * 2)):
            px, py = rnd.uniform(x_mid - W / 2, x_mid + W / 2), rnd.uniform(y - fs * 0.7, y - fs * 0.35)
            L = rnd.uniform(fs * 0.08, fs * 0.2)
            st.append(f'<path d="M {px:.1f} {py:.1f} l {L * 0.3:.1f} {-L:.1f}" stroke="{hi}" stroke-width="{max(1.2, fs * 0.016):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.25, 0.5):.2f}"/>')
    out.append(f'<clipPath id="{uid}">{G}</clipPath><g clip-path="url(#{uid})">{"".join(st)}</g>')
    out.append("</g>")
    return "".join(out)


def small(x, y, s, font, size, fill, max_w=400, ls=0, anchor="middle", extra=""):
    fs = fit_size(s, font, size, max_w, ls)
    xx = x + ls / 2 if (ls and anchor == "middle") else x
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return f'<text x="{xx:.1f}" y="{y:.1f}" text-anchor="{anchor}" {font} font-size="{fs}"{lsa} fill="{fill}"{extra}>{esc(s)}</text>'


def arc_label(D, s, cx, cy, r, font, size, fill, ls=0, top=True, max_len=None):
    """Text along a circular arc centred on (cx, cy)."""
    uid = D.nid()
    if top:
        d = f"M {cx - r:.1f} {cy:.1f} A {r:.1f} {r:.1f} 0 0 1 {cx + r:.1f} {cy:.1f}"
    else:
        d = f"M {cx - r:.1f} {cy:.1f} A {r:.1f} {r:.1f} 0 0 0 {cx + r:.1f} {cy:.1f}"
    fs = size
    if max_len:
        fs = fit_size(s, font, size, max_len, ls)
    lsa = f' letter-spacing="{ls}"' if ls else ""
    D.defs.append(f'<path id="{uid}" d="{d}" fill="none"/>')
    return f'<text {font} font-size="{fs}"{lsa} fill="{fill}" text-anchor="middle"><textPath href="#{uid}" startOffset="50%">{esc(s)}</textPath></text>'


def stars_row(cx, cy, n, r, gap, col, op=1.0):
    from common import star_points
    x0 = cx - (n - 1) * gap / 2
    return "".join(f'<polygon points="{star_points(x0 + i * gap, cy, r, r * 0.42)}" fill="{col}" opacity="{op}"/>' for i in range(n))


def star(cx, cy, r, col, op=1.0, rot_=-90):
    from common import star_points
    return f'<polygon points="{star_points(cx, cy, r, r * 0.42, 5, rot_)}" fill="{col}" opacity="{op}"/>'


def hbar(D, x0, x1, y, h, col, seed, op=1.0):
    """A printed rule/stripe with slightly irregular edges."""
    pts = poly([(x0, y), (x1, y), (x1, y + h), (x0, y + h)], 18)
    return f'<path d="{smooth_closed(jitter(pts, seed, 0.5))}" fill="{col}" opacity="{op}"/>'


# ================================================================ backgrounds
def chrome_bar(D, x0, y0, x1, y1, seed, sky_c="#BFE6F6", ground="#5A4636", r=None, horizon=0.5):
    """Close-up chrome bumper: mirror bands (sky above, bright horizon, dark ground below), streaks and sparkle."""
    r = r if r is not None else (y1 - y0) * 0.3
    pts = rrect(x0, y0, x1, y1, r, 20)
    d = smooth_closed(pts)
    h0 = horizon
    g = D.lin([(0, "#E8F0F4"), (0.05, "#FFFFFF"), (0.12, "#8FA6B6"), (h0 * 0.55, sky_c), (h0 - 0.04, "#EAF8FF"), (h0, "#FFFFFF"),
               (h0 + 0.03, "#3A2E28"), (h0 + 0.2, ground), (0.86, mix(ground, "#FFFFFF", 0.45)), (0.93, "#F4F4F4"), (1, "#6A6460")], 0, y0, 0, y1, "userSpaceOnUse")
    out = [f'<path d="{d}" fill="{g}"/>']
    out.append(strokes(D.nid(), d, (x0 - 40, y0, x1, y1), ["#FFFFFF", "#2A2420", sky_c], seed, n=int((x1 - x0) / 5), angle=0, length=(40, 160),
                       width=(1.5, 4), opacity=(0.08, 0.3), curve=0.04))
    # reflected shapes (trees / street) as soft dark blobs under the horizon line
    rnd = random.Random(seed)
    yh = y0 + (y1 - y0) * h0
    cid = D.clip(f'<path d="{d}"/>')
    refl = []
    for i in range(9):
        x = rnd.uniform(x0, x1)
        refl.append(f'<path d="{blob(x, yh - 6, rnd.uniform(20, 50), rnd.uniform(5, 12), seed + i, 0.2, 10)}" fill="#6A8A9A" opacity="0.35"/>')
    refl.append(f'<rect x="{x0}" y="{yh - 1.5:.1f}" width="{x1 - x0}" height="3" fill="#FFFFFF" opacity="0.9"/>')
    out.append(f'<g {cid}>{"".join(refl)}</g>')
    out.append(ink(d, "#2A2A30", 2.4, seed + 3, 2, 0.7))
    for x in (rnd.uniform(x0 + 60, x0 + 200), rnd.uniform(x1 - 200, x1 - 60)):
        out.append(sparkle(x, y0 + (y1 - y0) * 0.1, 9, "#FFFFFF", 0.95))
    return "".join(out)


def asphalt(D, y0, seed, base="#4A4650", cols=("#5E5A66", "#38343E", "#6A6672"), y1=600):
    d = f"M -10 {y0} L 610 {y0} L 610 {y1 + 10} L -10 {y1 + 10} Z"
    out = [f'<path d="{d}" fill="{base}"/>',
           strokes(D.nid(), d, (-60, y0, 610, y1), list(cols), seed, n=int((y1 - y0) * 0.8), angle=0, length=(30, 100), width=(2, 5), opacity=(0.15, 0.4), curve=0.05),
           specks(seed + 1, (0, y0, 600, y1), ["#8A8692", "#2A2630", "#A8A4B0"], int((y1 - y0) * 1.2), (0.6, 1.6), (0.3, 0.7))]
    return "".join(out)


def car_paint(D, d, box, pal, seed, sky_band=(0.1, 0.28), angle=0, tex=0.6):
    """Glossy car paint: base gradient, broad sky reflection band, brush strokes along the panel."""
    light, base, dark = pal
    x0, y0, x1, y1 = box
    out = [f'<path d="{d}" fill="{D.lin([(0, light), (0.35, base), (1, dark)], 0, y0, 0, y1, "userSpaceOnUse")}"/>']
    out.append(strokes(D.nid(), d, (x0 - 60, y0, x1, y1), [light, dark, base], seed, n=int((x1 - x0) * (y1 - y0) / 700 * tex), angle=angle,
                       length=(40, 140), width=(3, 9), opacity=(0.1 * tex, 0.3 * tex), curve=0.06))
    a, b = sky_band
    if b > a:
        H = y1 - y0
        cid = D.clip(f'<path d="{d}"/>')
        band = [(x0 - 20, y0 + H * a), (x1 + 20, y0 + H * (a - 0.03)), (x1 + 20, y0 + H * b), (x0 - 20, y0 + H * (b + 0.04))]
        out.append(f'<g {cid}><path d="{smooth_closed(jitter(poly(band, 40), seed, 2))}" fill="#FFFFFF" opacity="0.22"/>'
                   f'<path d="M {x0 - 20} {y0 + H * b:.1f} L {x1 + 20} {y0 + H * (b - 0.02):.1f}" stroke="#FFFFFF" stroke-width="3" opacity="0.35"/></g>')
    return "".join(out)


def tail_light(D, cx, cy, r, seed, lens=("#FF8A7A", "#E02A22", "#7A0A0A"), ring=True):
    out = [soft_glow(D, cx, cy, r * 1.9, "#FF5A3A", 0.35)]
    if ring:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r + 9}" fill="{D.lin([(0, "#FFFFFF"), (0.45, "#B8C4CC"), (0.55, "#6A7480"), (1, "#E8EEF2")])}"/>')
        out.append(ink(smooth_closed(oval(cx, cy, r + 9, r + 9, 40)), "#2A2A30", 2, seed, 1, 0.7))
    pts = oval(cx, cy, r, r, 40)
    out.append(painted(D, pts, lens, seed, sdir=(0.5, 0.6), sk=0.18, angle=-45, n=30, inkw=1.8, hi=0.4))
    for k in range(1, 4):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * k / 4:.1f}" fill="none" stroke="#FFB0A0" stroke-width="1.4" opacity="0.45"/>')
    out.append(taper([(cx - r * 0.6, cy - r * 0.2), (cx - r * 0.35, cy - r * 0.6)], r * 0.2, 2, "#FFFFFF", 0.75))
    return "".join(out)


# ================================================================ small painted illustrations
def diner_mug(D, cx, cy, s, seed, body=CREAM, stripe=RED, coffee=("#A0623A", "#5A2E16", "#2A1408"), steam=True):
    """A chunky diner mug, 3/4 view, with a red band, steaming coffee. s ~ half width."""
    out = [cast(D, cx + s * 0.1, cy + s * 1.02, s * 1.1, s * 0.16, strength=0.35, seed=seed)]
    handle = [(cx + s * 0.86, cy - s * 0.42), (cx + s * 1.42, cy - s * 0.48), (cx + s * 1.5, cy + s * 0.08), (cx + s * 1.1, cy + s * 0.56), (cx + s * 0.78, cy + s * 0.5),
              (cx + s * 0.8, cy + s * 0.3), (cx + s * 1.06, cy + s * 0.28), (cx + s * 1.18, cy - s * 0.06), (cx + s * 1.1, cy - s * 0.24), (cx + s * 0.86, cy - s * 0.2)]
    out.append(painted(D, handle, body, seed + 1, sdir=(0.6, 0.5), sk=0.18, angle=-60, n=10, inkw=2.2, hi=0.4))
    cup = ([(cx - s * 0.92, cy - s * 0.66)] + [(cx - s * 0.9 + s * 0.04 * t, cy - s * 0.4 + s * 1.2 * t) for t in (0.3, 0.6, 0.9)] +
           [(cx - s * 0.7, cy + s * 0.92), (cx, cy + s * 1.0), (cx + s * 0.7, cy + s * 0.92)] +
           [(cx + s * 0.86 - s * 0.04 * t, cy - s * 0.4 + s * 1.2 * t) for t in (0.9, 0.6, 0.3)] + [(cx + s * 0.92, cy - s * 0.66), (cx, cy - s * 0.56)])
    out.append(painted(D, cup, body, seed + 2, sdir=(0.7, 0.3), sk=0.2, angle=-90, n=30, inkw=0, hi=0.5))
    cid = D.clip(f'<path d="{smooth_closed(cup)}"/>')
    band = [(cx - s, cy + s * 0.02), (cx, cy + s * 0.12), (cx + s, cy + s * 0.02), (cx + s, cy + s * 0.3), (cx, cy + s * 0.4), (cx - s, cy + s * 0.3)]
    out.append(f'<g {cid}>' + painted(D, band, stripe, seed + 3, sdir=(0.7, 0.3), sk=0.2, angle=0, n=14, inkw=0, hi=0.3, edge=False) + '</g>')
    out.append(ink(smooth_closed(cup), INK, 2.4, seed + 4, 2, 0.85))
    rim = oval(cx, cy - s * 0.62, s * 0.92, s * 0.22, 30)
    out.append(painted(D, rim, body, seed + 5, sk=0, n=4, inkw=2.2, hi=0))
    out.append(painted(D, oval(cx, cy - s * 0.6, s * 0.76, s * 0.15, 30), coffee, seed + 6, sdir=(-0.3, -1), sk=0.25, angle=0, n=8, inkw=1.2, hi=0.3))
    out.append(f'<ellipse cx="{cx - s * 0.2:.1f}" cy="{cy - s * 0.64:.1f}" rx="{s * 0.22:.1f}" ry="{s * 0.04:.1f}" fill="#E8B88A" opacity="0.6"/>')
    out.append(taper([(cx - s * 0.66, cy + s * 0.7), (cx - s * 0.72, cy - s * 0.3)], s * 0.12, s * 0.04, "#FFFFFF", 0.7))
    if steam:
        out.append(steam_wisps(cx, cy - s * 0.85, s * 1.0, seed + 7, col="#FFFFFF", n=3, gap=s * 0.42, w=s * 0.13, op=0.85))
    return "".join(out)


def bulb_horn(D, cx, cy, s, seed, bulb=CHERRY, brass=MUSTARD, sound=True):
    """Old squeeze horn, side view: red rubber bulb on the left, brass neck, a flared trumpet bell to the right."""
    out = [cast(D, cx + s * 0.2, cy + s * 0.5, s * 1.4, s * 0.1, strength=0.3, seed=seed)]
    # flared cone (exponential flare)
    top, bot = [], []
    for i in range(15):
        t = i / 14
        x = cx - s * 0.32 + s * 1.45 * t
        w = s * (0.07 + 0.36 * t ** 2.6)
        top.append((x, cy - w))
        bot.append((x, cy + w))
    cone = top + bot[::-1]
    out.append(painted(D, cone, brass, seed + 1, sdir=(0, 1), sk=0.22, angle=0, n=26, inkw=2.2, hi=0.5, hik=0.14))
    mx = cx + s * 1.13
    mouth = oval(mx, cy, s * 0.1, s * 0.43, 28)
    out.append(painted(D, mouth, ("#E8B04A", "#9A6A1A", "#4A2E08"), seed + 3, sdir=(-1, 0), sk=0.3, n=6, inkw=2.2, hi=0.3))
    out.append(taper([(cx - s * 0.2, cy - s * 0.06), (cx + s * 0.5, cy - s * 0.12), (cx + s * 0.95, cy - s * 0.3)], 2, s * 0.06, "#FFF6C0", 0.85))
    # collar rings
    for x in (cx - s * 0.36, cx - s * 0.24):
        out.append(painted(D, rrect(x - s * 0.05, cy - s * 0.13, x + s * 0.05, cy + s * 0.13, 3, 5), brass, seed + int(x), sk=0.25, n=3, inkw=1.8, hi=0.4))
    bulb_pts = blob_pts(cx - s * 0.74, cy, s * 0.4, s * 0.34, seed + 5, 0.03, 22)
    out.append(painted(D, bulb_pts, bulb, seed + 5, sdir=(0.6, 0.6), sk=0.2, angle=-30, n=30, inkw=2.4, hi=0.45, curve=0.5))
    out.append(taper([(cx - s * 0.98, cy + s * 0.02), (cx - s * 0.86, cy - s * 0.2)], s * 0.08, 2, "#FFFFFF", 0.75))
    if sound:
        for k, (rr, op) in enumerate(((0.35, 0.95), (0.55, 0.75), (0.75, 0.55))):
            pts = [(mx + s * 0.1 + s * rr * math.cos(math.radians(a)), cy + s * rr * 1.3 * math.sin(math.radians(a))) for a in range(-45, 46, 9)]
            out.append(taper(pts, 1.5, s * 0.07, NAVY[2], op))
    return "".join(out)


def wheel(D, cx, cy, r, seed, tire="#2A2430", hub=("#FFFFFF", "#DCE2E8", "#7A8490"), cap=None):
    out = [painted(D, oval(cx, cy, r, r, 36), (mix(tire, "#FFFFFF", 0.2), tire, "#08060A"), seed, sk=0.15, n=10, inkw=2, hi=0.2)]
    out.append(painted(D, oval(cx, cy, r * 0.56, r * 0.56, 30), hub, seed + 1, sk=0.2, n=4, inkw=1.6, hi=0.5))
    if cap:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.18:.1f}" fill="{cap}"/>')
    return "".join(out)


def wood_panel(D, d, box, seed, pal=WOOD, horiz=True):
    """Wood-grain vinyl paneling: base wash, long grain strokes, knots."""
    light, base, dark = pal
    x0, y0, x1, y1 = box
    out = [f'<path d="{d}" fill="{base}"/>']
    out.append(strokes(D.nid(), d, (x0 - 80, y0, x1, y1), [light, dark, mix(base, dark, 0.5), "#F2C892"], seed, n=int((x1 - x0) * (y1 - y0) / 260),
                       angle=0 if horiz else -90, length=(60, 200), width=(1, 3.5), opacity=(0.25, 0.6), curve=0.03))
    rnd = random.Random(seed)
    cid = D.clip(f'<path d="{d}"/>')
    knots = []
    for i in range(int((x1 - x0) * (y1 - y0) / 30000) + 1):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        for k in range(3):
            knots.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{14 + k * 9}" ry="{4 + k * 3}" fill="none" stroke="{dark}" stroke-width="1.4" opacity="{0.45 - k * 0.1:.2f}"/>')
    # plank seams
    for k in range(1, 8):
        y = y0 + (y1 - y0) * k / 8 + rnd.uniform(-3, 3)
        knots.append(f'<path d="M {x0 - 10} {y:.1f} L {x1 + 10} {y + rnd.uniform(-2, 2):.1f}" stroke="{dark}" stroke-width="1.6" opacity="0.35"/>')
    out.append(f'<g {cid}>{"".join(knots)}</g>')
    return "".join(out)


def glass(D, d, box, seed, top="#BFE6F6", bot="#3A5A72", refl=True):
    x0, y0, x1, y1 = box
    out = [f'<path d="{d}" fill="{D.lin([(0, top), (1, bot)], 0, y0, 0, y1, "userSpaceOnUse")}"/>']
    if refl:
        cid = D.clip(f'<path d="{d}"/>')
        W = x1 - x0
        out.append(f'<g {cid}><polygon points="{P([(x0 + W * 0.15, y0 - 5), (x0 + W * 0.3, y0 - 5), (x0 + W * 0.18, y1 + 5), (x0 + W * 0.03, y1 + 5)])}" fill="#FFFFFF" opacity="0.28"/>'
                   f'<polygon points="{P([(x0 + W * 0.36, y0 - 5), (x0 + W * 0.4, y0 - 5), (x0 + W * 0.28, y1 + 5), (x0 + W * 0.24, y1 + 5)])}" fill="#FFFFFF" opacity="0.22"/></g>')
    return "".join(out)


# ================================================================ 1. I BRAKE FOR COFFEE — cherry-red fifties trunk, chrome bumper
@design("i-brake-for-coffee")
def i_brake_for_coffee():
    D = Doc("ibc")
    out = []
    body = "M -10 -10 L 610 -10 L 610 300 L -10 300 Z"
    out.append(car_paint(D, body, (0, 0, 600, 300), CHERRY, 3, sky_band=(0.06, 0.3)))
    win = smooth_closed(rrect(70, -60, 530, 60, 30))
    out.append(glass(D, win, (70, -60, 530, 60), 2, top="#CFE8F4", bot="#6A8AA8"))
    out.append(ink(win, "#3A0A0A", 2.6, 2, 1, 0.8) + taper([(80, 66), (520, 66)], 5, 5, "#E8EEF2", 0.9))
    # trunk lid crease and chrome trim with a little keyhole emblem
    out.append(taper([(-10, 112), (300, 106), (610, 112)], 8, 8, "#E8EEF2") + pline([(-10, 116), (300, 110), (610, 116)], "#6E0E12", 1.6, 4, 0.6, 1))
    out.append(taper([(-10, 108), (300, 102), (610, 108)], 2, 2, "#FFFFFF", 0.8))
    out.append(painted(D, oval(300, 178, 34, 22, 30), CHROME, 5, sdir=(0.4, 1), sk=0.25, n=6, inkw=2, hi=0.6))
    out.append(f'<path d="{blob(300, 180, 5, 8, 6, 0.05, 8)}" fill="#2A2430"/>')
    out.append(tail_light(D, 54, 196, 46, 7) + tail_light(D, 546, 196, 46, 8))
    out.append(soft_glow(D, 300, 40, 220, "#FFFFFF", 0.18))
    # road and bumper
    out.append(asphalt(D, 500, 9))
    out.append(f'<rect x="-10" y="500" width="620" height="40" fill="{D.lin([(0, "#0E0A10", 0.7), (1, "#0E0A10", 0)])}"/>')
    out.append(chrome_bar(D, -40, 252, 640, 522, 10, sky_c="#BCE4F4", ground="#5A3E30", r=60, horizon=0.36))
    # sticker
    pts = rrect(66, 282, 534, 494, 30)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, CREAM, 11)
    c = [f'<path d="{smooth_closed(rrect(80, 296, 520, 480, 20))}" fill="none" stroke="{CHERRY[1]}" stroke-width="5"/>',
         f'<path d="{smooth_closed(rrect(89, 305, 511, 471, 14))}" fill="none" stroke="{CHERRY[1]}" stroke-width="1.6"/>']
    c.append(f'<path d="{blob(164, 392, 70, 70, 12, 0.04, 18)}" fill="#F6D9A8" opacity="0.85"/>')
    c.append(diner_mug(D, 156, 408, 46, 13))
    c.append(vt(D, 372, 388, "I BRAKE", ANTON, 86, CHERRY[1], 14, max_w=262, ls=3, shadow="#3A1A10", soff=(0.03, 0.04)))
    c.append(stars_row(372, 404, 3, 6, 18, CHERRY[1]))
    c.append(hbar(D, 246, 334, 402.5, 3, CHERRY[1], 16) + hbar(D, 410, 498, 402.5, 3, CHERRY[1], 17))
    c.append(vt(D, 372, 456, "FOR COFFEE", BEBAS, 64, "#3A1A10", 15, max_w=262, ls=3))
    out.append(sticker(D, pts, face, "".join(c), rot_=-2.5, peel=(-38, 30), seed=18))
    # somebody left their coffee on the bumper again
    out.append(cast(D, 432, 262, 30, 6, strength=0.45))
    cup = [(406, 206), (458, 206), (450, 262), (414, 262)]
    out.append(painted(D, poly(cup, 8), ("#FFFFFF", "#F2EADC", "#B8A88A"), 21, sdir=(0.8, 0.2), sk=0.2, angle=-90, n=8, inkw=2, hi=0.5))
    out.append(painted(D, poly([(409, 224), (455, 224), (452, 246), (412, 246)], 8), ("#E8A060", "#C0703A", "#7A3E18"), 22, sk=0.2, n=6, inkw=1.6, hi=0.3))
    out.append(heart_path(D, 432, 236, 7, ("#FFFFFF", "#FFF4E0", "#C8B48A"), 24))
    out.append(painted(D, rrect(400, 196, 464, 208, 4, 8), ("#FFFFFF", "#E8E0D8", "#9A9088"), 23, sk=0.2, n=4, inkw=1.8, hi=0.4))
    out.append(steam_wisps(432, 190, 46, 24, col="#FFFFFF", n=2, gap=16, w=5, op=0.85))
    return finish(D, out, 19, INK, 0.7)


# ================================================================ 2. HONK IF YOU'RE HAPPY — mint pickup tailgate, sunny oval
@design("honk-if-youre-happy")
def honk_if_youre_happy():
    D = Doc("hih")
    out = [sky(D, [(0, "#5AC4F0"), (1, "#D8F4FF")], 3, 150, ["#FFFFFF", "#9ADCF6"], 20)]
    out.append(puff_cloud(D, 480, 96, 170, 4, op=0.95))
    out.append(hill(D, ridge([(-20, 126), (300, 112), (620, 128)], 3, 6), 150, ("#C8E8B0", "#9ACB80", "#6A9A58"), 3, inkw=0))
    # a bunch of balloons tied in the truck bed, bobbing above the tailgate
    for i, (bx, by, col) in enumerate(((112, 74, ("#FF9A8A", "#F2504A", "#9A1A1A")), (166, 56, ("#FFE89A", "#FFC93C", "#B07A12")), (214, 82, ("#9ADCF6", "#3AA0D8", "#1A5A8A")))):
        out.append(pline([(bx, by + 34), (bx + 4, by + 60), (168, 130)], "#FFFFFF", 1.6, i, 0.9, 1))
        out.append(painted(D, blob_pts(bx, by, 26, 32, 40 + i, 0.03, 18), col, 40 + i, sdir=(0.5, 0.6), sk=0.2, angle=-60, n=10, inkw=2, hi=0.45))
        out.append(f'<path d="M {bx - 4} {by + 32} L {bx + 4} {by + 32} L {bx} {by + 38} Z" fill="{col[2]}"/>')
        out.append(taper([(bx - 14, by - 8), (bx - 8, by - 20)], 5, 2, "#FFFFFF", 0.8))
    tg = "M -10 120 L 610 120 L 610 490 L -10 490 Z"
    out.append(car_paint(D, tg, (0, 120, 600, 490), MINT, 6, sky_band=(0.04, 0.12)))
    # top rail + stamped ridges
    out.append(painted(D, poly([(-10, 112), (610, 112), (610, 146), (-10, 146)], 30), ("#B8E8D4", "#6AC0A0", "#2E7A62"), 7, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=2, hi=0.5))
    for y in (172, 462):
        out.append(taper([(-10, y), (610, y)], 10, 10, "#5AA88C", 0.55) + taper([(-10, y - 5), (610, y - 5)], 3, 3, "#FFFFFF", 0.55))
    out.append(tail_light(D, 18, 290, 30, 8, ring=False) + tail_light(D, 582, 290, 30, 9, ring=False))
    out.append(asphalt(D, 556, 10, base="#6A6470"))
    out.append(chrome_bar(D, -40, 486, 640, 562, 11, r=18, horizon=0.45))
    # sticker: sunny oval
    cy = 320
    pts = oval(300, cy, 234, 146, 64)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#FFE98A", "#FFC93C", "#D98E12"), 12)
    ray = []
    for k in range(18):
        a = math.radians(k * 20 + 5)
        ray.append(f'<path d="M 300 {cy} L {300 + 400 * math.cos(a - 0.08):.1f} {cy + 400 * math.sin(a - 0.08):.1f} L {300 + 400 * math.cos(a + 0.08):.1f} {cy + 400 * math.sin(a + 0.08):.1f} Z" fill="#FFE27A" opacity="0.55"/>')
    face += "".join(ray)
    c = [f'<path d="{smooth_closed(oval(300, cy, 218, 130, 64))}" fill="none" stroke="{NAVY[1]}" stroke-width="5"/>',
         f'<path d="{smooth_closed(oval(300, cy, 208, 121, 64))}" fill="none" stroke="{NAVY[1]}" stroke-width="1.6" stroke-dasharray="2 9" stroke-linecap="round"/>']
    c.append(bulb_horn(D, 268, cy - 92, 52, 13))
    c.append(vt(D, 300, cy + 10, "HONK IF", ANTON, 84, NAVY[1], 14, max_w=330, ls=6, shadow="#FFFFFF", soff=(0.03, 0.035)))
    c.append(vt(D, 300, cy + 86, "YOU'RE HAPPY", ANTON, 74, CHERRY[1], 15, max_w=350, ls=3, shadow="#7A1A10", soff=(0.025, 0.03), wob=0.2))
    c.append(small(300, cy + 120, "beep beep!", SERIF_IT, 26, NAVY[1], max_w=200))
    c.append(star(222, cy + 112, 7, NAVY[1]) + star(378, cy + 112, 7, NAVY[1]))
    out.append(sticker(D, pts, face, "".join(c), rot_=3, peel=(200, 26), seed=16))
    return finish(D, out, 20, INK, 0.7)


# ================================================================ 3. MOM'S TAXI — die-cut taxi roof sign on a wood-panel wagon
def checker(D, x0, y0, x1, y1, sq, cols=("#1A1A1E", "#FFD23A")):
    out = []
    n = int(math.ceil((x1 - x0) / sq))
    rows = int(round((y1 - y0) / sq))
    for r in range(rows):
        for i in range(n):
            if (i + r) % 2 == 0:
                out.append(f'<rect x="{x0 + i * sq:.1f}" y="{y0 + r * sq:.1f}" width="{sq:.1f}" height="{sq:.1f}" fill="{cols[0]}"/>')
    return "".join(out)


@design("moms-taxi")
def moms_taxi():
    D = Doc("mt")
    out = []
    # rear window of the wagon (sky + suburban trees reflected) with a chrome frame
    win = smooth_closed(rrect(-20, -20, 620, 120, 24))
    out.append(glass(D, win, (0, 0, 600, 120), 3, top="#CDEBF8", bot="#6A94B0"))
    cid = D.clip(f'<path d="{win}"/>')
    kids = []
    # a soccer ball, a pink backpack and a stuffed bunny riding in the way-back
    kids.append(painted(D, rrect(70, 40, 190, 140, 26, 10), ("#FFB8CC", "#F27A9A", "#A83A5A"), 30, sdir=(0.3, 1), sk=0.18, angle=-90, n=14, inkw=2, hi=0.4))
    kids.append(painted(D, rrect(92, 70, 168, 116, 12, 8), ("#FFD0DC", "#F590AC", "#B04A6A"), 31, sk=0.18, n=6, inkw=1.8, hi=0.3))
    kids.append(f'<path d="M 100 44 Q 130 10 160 44" stroke="#A83A5A" stroke-width="8" fill="none"/>')
    bx, by, br = 270, 92, 42
    kids.append(painted(D, oval(bx, by, br, br, 30), ("#FFFFFF", "#F2F0EA", "#B8B0A6"), 32, sk=0.2, n=6, inkw=2, hi=0.4))
    kids.append(f'<path d="{lpath([(bx + 14 * math.cos(math.radians(a_)), by + 14 * math.sin(math.radians(a_))) for a_ in range(-90, 270, 72)])}" fill="#2A2430"/>')
    for a_ in range(-90, 270, 72):
        px, py = bx + 34 * math.cos(math.radians(a_ + 36)), by + 34 * math.sin(math.radians(a_ + 36))
        kids.append(f'<path d="{blob(px, py, 9, 8, a_ + 400, 0.1, 8)}" fill="#2A2430"/>')
    for ex in (420, 452):
        kids.append(painted(D, blob_pts(ex, 52, 12, 34, ex, 0.05, 14, (ex - 436) * 0.6), ("#FFFFFF", "#F2EEE6", "#B8B0A6"), ex, sk=0.2, n=4, inkw=1.8, hi=0.3))
        kids.append(f'<path d="{blob(ex, 56, 5, 22, ex + 1, 0.05, 10)}" fill="#F8C0CC"/>')
    kids.append(painted(D, blob_pts(436, 112, 44, 38, 33, 0.04, 18), ("#FFFFFF", "#F2EEE6", "#B8B0A6"), 33, sk=0.2, n=8, inkw=2, hi=0.3))
    kids.append(f'<circle cx="422" cy="104" r="4" fill="#2A2430"/><circle cx="450" cy="104" r="4" fill="#2A2430"/><path d="{blob(436, 116, 6, 4, 34, 0.1, 8)}" fill="#F27A9A"/>')
    kids.append(f'<polygon points="{P([(170, -20), (230, -20), (160, 130), (100, 130)])}" fill="#FFFFFF" opacity="0.2"/>')
    out.append(f'<g {cid}>{"".join(kids)}</g>')
    out.append(f'<path d="M -20 124 L 620 124" stroke="#E8EEF2" stroke-width="10"/><path d="M -20 120 L 620 120" stroke="#FFFFFF" stroke-width="2"/>')
    # cream body with a wood-grain panel
    body = "M -10 130 L 610 130 L 610 600 L -10 600 Z"
    out.append(car_paint(D, body, (0, 130, 600, 600), CREAM, 4, sky_band=(0.0, 0.04)))
    panel = smooth_closed(rrect(-30, 150, 630, 470, 10))
    out.append(wood_panel(D, panel, (-30, 150, 630, 470), 5))
    out.append(f'<path d="{panel}" fill="none" stroke="#E8DCC0" stroke-width="10"/>' + ink(panel, INK, 1.6, 6, 1, 0.5))
    out.append(tail_light(D, 22, 300, 26, 7, ring=False) + tail_light(D, 578, 300, 26, 8, ring=False))
    out.append(asphalt(D, 556, 9))
    out.append(chrome_bar(D, -40, 488, 640, 560, 10, r=18, horizon=0.45))
    # die-cut taxi-sign sticker
    corners = [(56, 290), (166, 290), (188, 166), (412, 166), (434, 290), (544, 290), (544, 470), (56, 470)]
    pts = []
    for k in range(len(corners)):
        a, b = corners[k], corners[(k + 1) % len(corners)]
        n = max(2, int(math.dist(a, b) / 12))
        for i in range(n):
            t = i / n
            if 0.06 < t < 0.94 or i == 0:
                pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#FFE680", "#FFD23A", "#C89A10"), 11)
    c = [checker(D, 40, 424, 560, 452, 14)]
    c.append(f'<path d="M 30 420 L 570 420" stroke="#1A1A1E" stroke-width="3"/><path d="M 30 456 L 570 456" stroke="#1A1A1E" stroke-width="3"/>')
    # roof-light cap: black panel with the "MOM'S" script
    cap = smooth_closed(jitter(poly([(196, 184), (404, 184), (420, 282), (180, 282)], 12), 12, 0.4))
    c.append(f'<path d="{cap}" fill="#1E1A22"/>' + f'<path d="{cap}" fill="none" stroke="#FFD23A" stroke-width="2" stroke-dasharray="1 7" stroke-linecap="round" transform="translate(0 0)"/>')
    c.append(vt(D, 300, 262, "Mom's", SERIF_IT, 84, "#FFD23A", 13, max_w=200, shadow="#C8282A", soff=(0.02, 0.035), wob=0.6))
    c.append(vt(D, 300, 408, "TAXI", ANTON, 128, "#1E1A22", 14, max_w=330, ls=14, shadow="#FFFFFF", soff=(0.025, 0.03)))
    c.append(small(300, 468, "", BEBAS, 20, "#1E1A22"))
    for x in (100, 500):
        c.append(f'<circle cx="{x}" cy="{360}" r="14" fill="#1E1A22"/>' + star(x, 360, 9, "#FFD23A"))
    out.append(sticker(D, pts, face, "".join(c), rot_=-2, peel=(-30, 34), seed=15))
    # tagline on a little white label beneath
    lpts = rrect(150, 492, 450, 534, 8)
    lab = smooth_closed(lpts)
    out.append(sticker(D, lpts, f'<path d="{lab}" fill="#FFFFFF"/>', small(300, 522, "NO REFUNDS · NO TIPS NEEDED", BEBAS, 26, "#1E1A22", max_w=270, ls=2),
                       rot_=1.5, margin=4, seed=16, wear=0.6, gloss=0.1))
    return finish(D, out, 17, INK, 0.7)



# ================================================================ more painted bits
def bolt(cx, cy, s, col, op=1.0, rot_=0):
    pts = [(-0.15, -1), (0.45, -1), (0.12, -0.15), (0.5, -0.15), (-0.3, 1), (-0.05, 0.12), (-0.45, 0.12)]
    pts = rot([(cx + x * s, cy + y * s) for x, y in pts], cx, cy, rot_)
    return f'<path d="{lpath(pts)}" fill="{col}" opacity="{op}" stroke-linejoin="round"/>'


def coffee_bean(D, cx, cy, s, seed, rot_=0):
    pts = rot(blob_pts(cx, cy, s, s * 0.68, seed, 0.04, 16), cx, cy, rot_)
    out = [painted(D, pts, ("#B07A4A", "#6A3E1E", "#2E180A"), seed, sdir=(0.5, 0.7), sk=0.2, angle=rot_, n=6, inkw=1.6, hi=0.4)]
    a = math.radians(rot_)
    c, s_ = math.cos(a), math.sin(a)
    seam = [(-0.8, 0.05), (-0.3, -0.12), (0.3, 0.12), (0.8, -0.05)]
    seam = [(cx + (x * c - y * s_) * s, cy + (x * s_ + y * c) * s) for x, y in seam]
    out.append(pline(seam, "#2A1206", max(1.6, s * 0.14), seed, 0.9, 1))
    return "".join(out)


def broom(D, x0, y0, x1, y1, seed, handle=WOOD, straw=("#FFE28A", "#E8B040", "#9A6A18"), tie=CHERRY):
    """A witch's broom lying along (x0,y0)->(x1,y1): long knobbly handle, fanned straw at (x1,y1)."""
    a = math.atan2(y1 - y0, x1 - x0)
    L = math.hypot(x1 - x0, y1 - y0)
    c, s_ = math.cos(a), math.sin(a)

    def T(u, v):
        return (x0 + u * c - v * s_, y0 + u * s_ + v * c)
    out = []
    hp = [T(0, -5), T(L * 0.68, -6.5), T(L * 0.68, 6.5), T(0, 5)]
    out.append(painted(D, poly(hp, 12), handle, seed, sdir=(0, 1), sk=0.25, angle=math.degrees(a), n=20, inkw=2, hi=0.4))
    out.append(f'<circle cx="{T(0, 0)[0]:.1f}" cy="{T(0, 0)[1]:.1f}" r="7" fill="{handle[1]}" stroke="{INK}" stroke-width="2"/>')
    sp = [T(L * 0.64, -10), T(L * 0.76, -16), T(L * 0.9, -30), T(L * 1.0, -42), T(L * 1.02, -10), T(L * 1.04, 12), T(L * 0.98, 40), T(L * 0.86, 26), T(L * 0.74, 14), T(L * 0.64, 10)]
    out.append(painted(D, sp, straw, seed + 1, sdir=(0.2, 1), sk=0.15, angle=math.degrees(a), n=40, slen=(10, 40), sw=(1, 2.4), sop=(0.4, 0.8), inkw=2, hi=0.3))
    rnd = random.Random(seed)
    for i in range(16):
        v0 = rnd.uniform(-10, 10)
        p0, p1 = T(L * 0.7, v0), T(L * rnd.uniform(0.95, 1.03), v0 * 3 + rnd.uniform(-6, 6))
        out.append(f'<path d="M {p0[0]:.1f} {p0[1]:.1f} L {p1[0]:.1f} {p1[1]:.1f}" stroke="{rnd.choice([straw[2], "#C8902A", "#FFF0B0"])}" stroke-width="1.4" opacity="0.8"/>')
    for u in (0.69, 0.73):
        out.append(painted(D, poly([T(L * u, -13), T(L * u + 10, -14), T(L * u + 10, 14), T(L * u, 13)], 6), tie, seed + int(u * 100), sk=0.2, n=3, inkw=1.6, hi=0.4))
    return "".join(out)


def snail(D, cx, cy, s, seed, shell=("#F6C27A", "#D98A3A", "#8A4A1A"), body=("#E8E0C0", "#BFB48A", "#7A6E4A"), flip=1):
    """Garden snail crawling right (flip=-1 for left): striped spiral shell, soft body, eye stalks."""
    g = f'<g transform="translate({cx} {cy}) scale({flip} 1) translate({-cx} {-cy})">'
    out = [g, cast(D, cx + s * 0.1, cy + s * 0.46, s * 1.25, s * 0.1, strength=0.3, seed=seed)]
    foot = [(cx - s * 1.0, cy + s * 0.42), (cx - s * 0.3, cy + s * 0.32), (cx + s * 0.6, cy + s * 0.3), (cx + s * 0.95, cy + s * 0.1), (cx + s * 1.1, cy - s * 0.22),
            (cx + s * 1.25, cy - s * 0.18), (cx + s * 1.22, cy + s * 0.2), (cx + s * 1.0, cy + s * 0.44), (cx + s * 0.2, cy + s * 0.48)]
    out.append(painted(D, foot, body, seed, sdir=(0, 1), sk=0.2, angle=0, n=16, inkw=2.2, hi=0.45))
    for k, (dx, h) in enumerate(((1.08, 0.55), (1.22, 0.5))):
        x, y = cx + s * dx, cy - s * 0.12
        tip = (x + s * 0.1 * (k + 0.5), y - s * h)
        out.append(pline([(x, y), ((x + tip[0]) / 2 - 2, (y + tip[1]) / 2), tip], body[2], max(2, s * 0.07), seed + k, 0.9, 1))
        out.append(f'<circle cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" r="{s * 0.07:.1f}" fill="{body[2]}"/><circle cx="{tip[0] + 1:.1f}" cy="{tip[1] - 1:.1f}" r="{s * 0.025:.1f}" fill="#FFFFFF"/>')
    out.append(pline([(cx + s * 1.13, cy + s * 0.02), (cx + s * 1.2, cy + s * 0.07), (cx + s * 1.25, cy + s * 0.02)], "#5A4A2A", 1.6, seed, 0.8, 1))
    sh = blob_pts(cx - s * 0.12, cy - s * 0.18, s * 0.62, s * 0.56, seed + 2, 0.02, 24)
    out.append(painted(D, sh, shell, seed + 2, sdir=(0.5, 0.7), sk=0.2, angle=-40, n=30, inkw=2.4, hi=0.45, curve=0.5))
    sp = []
    for i in range(60):
        t = i / 59
        a = t * 3.6 * math.pi
        r = s * 0.55 * (1 - t * 0.92)
        sp.append((cx - s * 0.1 + r * math.cos(a + 0.4), cy - s * 0.16 + r * 0.95 * math.sin(a + 0.4)))
    out.append(ink(smooth_open(sp), shell[2], max(2, s * 0.06), seed + 3, 2, 0.8))
    out.append(taper([(cx - s * 0.5, cy - s * 0.3), (cx - s * 0.32, cy - s * 0.6)], s * 0.08, 2, "#FFF6E0", 0.7))
    out.append("</g>")
    return "".join(out)


def sleeping_cat(D, cx, cy, s, seed, fur=("#FFC88A", "#F29A4A", "#B0601E"), pillow=("#FFFFFF", "#E8E0F8", "#A898C8")):
    """A ginger cat curled asleep on a little pillow."""
    out = [cast(D, cx, cy + s * 0.62, s * 1.2, s * 0.12, strength=0.3, seed=seed)]
    pl = [(cx - s * 1.1, cy + s * 0.2), (cx - s * 0.6, cy + s * 0.05), (cx + s * 0.6, cy + s * 0.05), (cx + s * 1.1, cy + s * 0.2),
          (cx + s * 1.15, cy + s * 0.5), (cx + s * 0.6, cy + s * 0.62), (cx - s * 0.6, cy + s * 0.62), (cx - s * 1.15, cy + s * 0.5)]
    out.append(painted(D, pl, pillow, seed, sdir=(0.3, 1), sk=0.2, angle=0, n=14, inkw=2, hi=0.4))
    bd = blob_pts(cx + s * 0.1, cy - s * 0.12, s * 0.8, s * 0.42, seed + 1, 0.03, 22)
    out.append(painted(D, bd, fur, seed + 1, sdir=(0.3, 1), sk=0.2, angle=-20, n=30, inkw=2.2, hi=0.4, curve=0.5))
    # stripes on the back
    for k in range(4):
        x = cx - s * 0.2 + k * s * 0.22
        out.append(pline([(x, cy - s * 0.5), (x + s * 0.05, cy - s * 0.32), (x + s * 0.02, cy - s * 0.18)], fur[2], max(2, s * 0.06), seed + k, 0.7, 1))
    # tail wrapping around the front
    tail = catmull([(cx + s * 0.85, cy + 0.0 * s), (cx + s * 0.6, cy + s * 0.26), (cx - s * 0.2, cy + s * 0.3), (cx - s * 0.62, cy + s * 0.18)], 6)
    out.append(taper(tail, s * 0.2, s * 0.14, fur[2], 0.95) + taper([(x, y - 2) for x, y in tail], s * 0.14, s * 0.1, fur[1], 1))
    hd = blob_pts(cx - s * 0.62, cy - s * 0.06, s * 0.34, s * 0.3, seed + 2, 0.03, 18)
    out.append(painted(D, hd, fur, seed + 2, sdir=(0.3, 1), sk=0.2, angle=-20, n=14, inkw=2.2, hi=0.45))
    for sg in (-1, 1):
        ex = cx - s * 0.62 + sg * s * 0.2
        ear = [(ex - s * 0.11, cy - s * 0.26), (ex + sg * s * 0.04, cy - s * 0.52), (ex + s * 0.11, cy - s * 0.24)]
        out.append(painted(D, ear, fur, seed + 3 + sg, sk=0.2, n=3, inkw=2, hi=0.3))
        out.append(f'<path d="M {ex - s * 0.05:.1f} {cy - s * 0.28:.1f} L {ex + sg * s * 0.03:.1f} {cy - s * 0.42:.1f} L {ex + s * 0.05:.1f} {cy - s * 0.27:.1f} Z" fill="#F4A0A0" opacity="0.8"/>')
        out.append(pline([(ex - s * 0.08, cy - s * 0.06), (ex, cy - s * 0.02), (ex + s * 0.08, cy - s * 0.06)], INK, max(1.6, s * 0.035), seed, 0.9, 1))
    out.append(f'<path d="{blob(cx - s * 0.62, cy + s * 0.06, s * 0.04, s * 0.03, seed, 0.1, 8)}" fill="#D86A6A"/>')
    for sg in (-1, 1):
        for k in (-1, 1):
            x = cx - s * 0.62 + sg * s * 0.16
            out.append(f'<path d="M {x:.1f} {cy + s * 0.08:.1f} l {sg * s * 0.24:.1f} {k * s * 0.04:.1f}" stroke="#FFFFFF" stroke-width="1.4" opacity="0.8"/>')
    return "".join(out)


def black_cat(D, cx, base, s, seed):
    """A sitting black cat seen from behind-ish, tail curled, moonlit rim and two glowing eyes looking back."""
    out = [cast(D, cx, base, s * 0.9, s * 0.12, strength=0.5, seed=seed)]
    body = [(cx - s * 0.62, base), (cx - s * 0.7, base - s * 0.5), (cx - s * 0.45, base - s * 1.1), (cx - s * 0.3, base - s * 1.3),
            (cx + s * 0.3, base - s * 1.3), (cx + s * 0.45, base - s * 1.1), (cx + s * 0.7, base - s * 0.5), (cx + s * 0.62, base)]
    out.append(f'<path d="{smooth_closed(body)}" fill="#141020"/>')
    head = blob_pts(cx, base - s * 1.55, s * 0.42, s * 0.36, seed, 0.03, 16)
    out.append(f'<path d="{smooth_closed(head)}" fill="#141020"/>')
    for sg in (-1, 1):
        out.append(f'<path d="M {cx + sg * s * 0.36:.1f} {base - s * 1.62:.1f} L {cx + sg * s * 0.34:.1f} {base - s * 2.04:.1f} L {cx + sg * s * 0.08:.1f} {base - s * 1.84:.1f} Z" fill="#141020"/>')
        out.append(f'<ellipse cx="{cx + sg * s * 0.16:.1f}" cy="{base - s * 1.58:.1f}" rx="{s * 0.09:.1f}" ry="{s * 0.06:.1f}" fill="#FFE070"/>'
                   f'<ellipse cx="{cx + sg * s * 0.16:.1f}" cy="{base - s * 1.58:.1f}" rx="{s * 0.025:.1f}" ry="{s * 0.055:.1f}" fill="#141020"/>')
    out.append(taper(catmull([(cx + s * 0.6, base - s * 0.08), (cx + s * 1.1, base - s * 0.1), (cx + s * 1.25, base - s * 0.5), (cx + s * 1.05, base - s * 0.8)], 6), s * 0.18, s * 0.1, "#141020"))
    out.append(ink(smooth_open([(cx + s * 0.3, base - s * 1.3), (cx + s * 0.45, base - s * 1.1), (cx + s * 0.7, base - s * 0.5)]), "#B8A8E8", 2, seed, 1, 0.7))
    out.append(ink(smooth_open([p for p in head if p[0] > cx][:6]), "#B8A8E8", 1.6, seed + 1, 1, 0.6))
    return "".join(out)


def crescent(cx, cy, r, ox, oy, r2, n=48):
    """Crescent: disc (cx,cy,r) minus disc (cx+ox, cy+oy, r2), as an outline."""
    outer = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    a = [p for p in outer if math.hypot(p[0] - cx - ox, p[1] - cy - oy) > r2]
    inner = [(cx + ox + r2 * math.cos(2 * math.pi * i / (n * 2)), cy + oy + r2 * math.sin(2 * math.pi * i / (n * 2))) for i in range(n * 2)]
    b = [p for p in inner if math.hypot(p[0] - cx, p[1] - cy) < r]
    # order: walk outer arc, then inner arc backwards
    ang = lambda p, c: math.atan2(p[1] - c[1], p[0] - c[0])
    base = ang((cx - ox, cy - oy), (0, 0)) if False else math.atan2(-oy, -ox)
    a.sort(key=lambda p: (ang(p, (cx, cy)) - base + 3 * math.pi) % (2 * math.pi))
    b.sort(key=lambda p: (ang(p, (cx + ox, cy + oy)) - base + 3 * math.pi) % (2 * math.pi), reverse=True)
    return a + b


def zzz(x, y, s, col, op=1.0):
    from common import BEBAS as B
    return "".join(f'<text x="{x + i * s * 0.7:.1f}" y="{y - i * s * 0.75:.1f}" {B} font-size="{s * (1 - i * 0.2):.1f}" fill="{col}" opacity="{op}" transform="rotate(-10 {x + i * s * 0.7:.1f} {y - i * s * 0.75:.1f})">Z</text>' for i in range(3))


def rivets(x0, x1, y, gap, col="#8A9098", hi="#FFFFFF"):
    out = []
    x = x0
    while x <= x1:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{col}"/><circle cx="{x - 0.8:.1f}" cy="{y - 0.8:.1f}" r="1" fill="{hi}" opacity="0.8"/>')
        x += gap
    return "".join(out)


def round_gauge(D, cx, cy, r, seed, face="#FFF6E0", needle_a=-30, ticks=9, ring=CHROME, label_txt=None):
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r + 10}" fill="{D.lin([(0, "#FFFFFF"), (0.5, "#9AA4AE"), (1, "#E8EEF2")])}"/>',
           ink(smooth_closed(oval(cx, cy, r + 10, r + 10, 40)), "#2A2A30", 2, seed, 1, 0.7)]
    out.append(painted(D, oval(cx, cy, r, r, 40), (face, mix(face, "#C8B898", 0.4), "#8A7A5A"), seed, sdir=(0.5, 0.7), sk=0.15, n=10, inkw=1.6, hi=0.4))
    for k in range(ticks):
        a = math.radians(150 + k * 240 / (ticks - 1))
        out.append(f'<path d="M {cx + r * 0.78 * math.cos(a):.1f} {cy + r * 0.78 * math.sin(a):.1f} L {cx + r * 0.92 * math.cos(a):.1f} {cy + r * 0.92 * math.sin(a):.1f}" stroke="#2A2430" stroke-width="3"/>')
    a = math.radians(needle_a)
    out.append(f'<path d="M {cx:.1f} {cy:.1f} L {cx + r * 0.8 * math.cos(a):.1f} {cy + r * 0.8 * math.sin(a):.1f}" stroke="#D23A2C" stroke-width="4" stroke-linecap="round"/>'
               f'<circle cx="{cx}" cy="{cy}" r="{r * 0.1:.1f}" fill="#2A2430"/>')
    out.append(f'<path d="M {cx - r * 0.7:.1f} {cy - r * 0.4:.1f} Q {cx - r * 0.4:.1f} {cy - r * 0.85:.1f} {cx + r * 0.1:.1f} {cy - r * 0.88:.1f}" stroke="#FFFFFF" stroke-width="{r * 0.08:.1f}" fill="none" opacity="0.5" stroke-linecap="round"/>')
    return "".join(out)


# ================================================================ 4. POWERED BY COFFEE & CHAOS — battery decal on a retro dashboard
@design("powered-by-coffee")
def powered_by_coffee():
    D = Doc("pbc")
    out = [sky(D, [(0, "#FF9A6A"), (0.5, "#FFD08A"), (1, "#FFF0C8")], 3, 200, ["#FFE0B0", "#FFB080"], 20)]
    out.append(sun_disc(D, 420, 150, 30, ("#FFFCE0", "#FFE87A", "#FFB43A"), 4, glow_r=3))
    out.append(hill(D, ridge([(-20, 150), (200, 132), (420, 150), (620, 138)], 5, 8), 200, ("#C8B0C0", "#9A8AA8", "#6A5A80"), 5, inkw=0))
    out.append(hill(D, ridge([(-20, 172), (300, 160), (620, 176)], 6, 6), 200, ("#9AB88A", "#6A9A6A", "#3E6A4A"), 6, inkw=0))
    out.append(f'<path d="M 300 158 L 380 200 L 220 200 Z" fill="#6A6474"/><path d="M 300 160 L 304 200 L 298 200 Z" fill="#FFE27A" opacity="0.8"/>')
    # windshield frame + rear-view mirror
    out.append(taper([(-10, 4), (610, 4)], 18, 18, "#2A2630") + taper([(-10, 196), (610, 196)], 14, 14, "#2A2630"))
    out.append(painted(D, rrect(240, -20, 360, 36, 14), BLACK, 7, sk=0.2, n=8, inkw=2, hi=0.3))
    out.append(glass(D, smooth_closed(rrect(250, -10, 350, 26, 10)), (250, -10, 350, 26), 8, top="#FFE0B0", bot="#9A7A6A"))
    # the dashboard: painted teal metal with a chrome strip and two gauges
    dash = "M -10 200 L 610 200 L 610 610 L -10 610 Z"
    out.append(car_paint(D, dash, (0, 200, 600, 600), TEAL, 9, sky_band=(0.0, 0.08)))
    out.append(taper([(-10, 208), (610, 208)], 12, 12, "#0E3E3A", 0.5))
    out.append(taper([(-10, 478), (610, 478)], 14, 14, "#E8EEF2") + taper([(-10, 474), (610, 474)], 3, 3, "#FFFFFF", 0.9) + pline([(-10, 486), (610, 486)], "#2A2A30", 1.6, 10, 0.6, 1))
    out.append(round_gauge(D, 120, 560, 70, 11, needle_a=-60) + round_gauge(D, 480, 560, 70, 12, needle_a=-150))
    out.append(painted(D, rrect(240, 510, 360, 600, 10), ("#3A3640", "#24202A", "#0E0A12"), 13, sk=0.2, n=10, inkw=2, hi=0.2))
    for k in range(6):
        out.append(f'<path d="M 256 {528 + k * 12} L 344 {528 + k * 12}" stroke="#8A8494" stroke-width="3" opacity="0.7"/>')
    # battery sticker (die-cut with the + terminal)
    def arc_(cx_, cy_, r_, a0, a1, n=5):
        return [(cx_ + r_ * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy_ + r_ * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

    def seg(p, q, step=14):
        n = max(1, int(math.dist(p, q) / step))
        return [(p[0] + (q[0] - p[0]) * i / n, p[1] + (q[1] - p[1]) * i / n) for i in range(n)]
    pts = (seg((96, 232), (476, 232)) + arc_(476, 262, 30, -90, 0) + seg((506, 262), (506, 296))
           + seg((506, 296), (532, 296), 10) + arc_(532, 308, 12, -90, 0, 3) + seg((544, 308), (544, 368)) + arc_(532, 368, 12, 0, 90, 3)
           + seg((532, 380), (506, 380), 10) + seg((506, 380), (506, 414)) + arc_(476, 414, 30, 0, 90)
           + seg((476, 444), (96, 444)) + arc_(96, 414, 30, 90, 180) + seg((66, 414), (66, 262)) + arc_(96, 262, 30, 180, 270)[:-1])
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#3E8A5E", "#1F5E3B", "#0E3420"), 14)
    c = [f'<path d="{smooth_closed(rrect(82, 248, 490, 428, 20))}" fill="none" stroke="#F2C230" stroke-width="3"/>']
    # charge cells along the bottom: coffee beans
    c.append(vt(D, 286, 300, "POWERED BY", JOS, 40, "#FFF4D8", 15, max_w=330, ls=7))
    c.append(vt(D, 286, 384, "COFFEE", ANTON, 98, "#F2C230", 16, max_w=330, ls=6, shadow="#0E3420", soff=(0.03, 0.04)))
    c.append(vt(D, 330, 422, "& chaos", SERIF_IT, 50, "#FF8A6A", 17, max_w=200, shadow="#0E3420", soff=(0.025, 0.035), rotate=-6))
    c.append(f'<path d="{smooth_closed(rrect(507, 290, 560, 386, 8, 8))}" fill="#F2C230"/>'
             + strokes(D.nid(), smooth_closed(rrect(507, 290, 560, 386, 8, 8)), (480, 290, 560, 386), ["#FFE07A", "#B07A12"], 30, n=20, angle=-90, length=(20, 50), width=(2, 4), opacity=(0.2, 0.4)))
    c.append('<path d="M 525 324 L 525 352 M 511 338 L 539 338" stroke="#1F5E3B" stroke-width="7" stroke-linecap="round"/>')
    c.append('<path d="M 92 338 L 112 338" stroke="#F2C230" stroke-width="7" stroke-linecap="round"/>')
    for i, x in enumerate((150, 176)):
        pass
    c.append(bolt(112, 282, 15, "#F2C230", 0.95, 10) + bolt(462, 282, 15, "#F2C230", 0.95, 10))
    for i, (x, y, a) in enumerate(((114, 400, -30), (462, 404, 20))):
        c.append(coffee_bean(D, x, y, 15, 20 + i, a))
    out.append(sticker(D, pts, face, "".join(c), rot_=-3, peel=(140, 30), seed=18))
    # a paper coffee cup on the dash, steaming
    cup = [(538, 420), (588, 420), (582, 480), (544, 480)]
    out.append(cast(D, 564, 482, 34, 6, strength=0.4))
    out.append(painted(D, poly(cup, 8), ("#FFFFFF", "#F2EADC", "#B8A88A"), 21, sdir=(0.8, 0.2), sk=0.2, angle=-90, n=8, inkw=2, hi=0.5))
    out.append(painted(D, poly([(541, 440), (585, 440), (583, 462), (543, 462)], 8), ("#E8A060", "#C0703A", "#7A3E18"), 22, sk=0.2, n=6, inkw=1.6, hi=0.3))
    out.append(painted(D, rrect(532, 410, 594, 422, 4, 8), ("#FFFFFF", "#E8E0D8", "#9A9088"), 23, sk=0.2, n=4, inkw=1.8, hi=0.4))
    out.append(steam_wisps(562, 404, 50, 24, col="#FFFFFF", n=2, gap=16, w=5, op=0.8))
    return finish(D, out, 25, INK, 0.7)


# ================================================================ 5. MY OTHER CAR IS A BROOM — black tail-fin car under a full moon
@design("my-other-car-is-a-broom")
def my_other_car_is_a_broom():
    from halloween_gouache_a import moon, stars, pbat
    D = Doc("moc")
    out = [sky(D, [(0, "#1A1030"), (0.6, "#3A2058"), (1, "#5A3070")], 3, 230, ["#4A2A6A", "#2A1A44"], 30)]
    out.append(stars(4, 40, (0, 0, 600, 200), col="#FFF2C8", tw=5, avoid=((470, 92, 80),)))
    out.append(moon("moc-m", 470, 92, 56, 5))
    out.append(pbat(140, 84, 44, rot=-10) + pbat(260, 132, 26, rot=12, flap=0.4) + pbat(350, 62, 20, rot=-6))
    # glossy black car body with a tail fin and moon reflection
    body = smooth_closed([(-20, 250), (60, 214), (150, 204), (450, 204), (560, 160), (600, 150), (620, 150), (620, 620), (-20, 620)])
    out.append(car_paint(D, body, (0, 150, 600, 600), ("#5A4A7A", "#1E1830", "#0A0812"), 6, sky_band=(0.04, 0.16)))
    out.append(soft_glow(D, 470, 250, 90, "#FFF2C8", 0.25))
    out.append(taper([(-20, 252), (60, 216), (150, 206), (450, 206), (560, 162), (610, 152)], 4, 4, "#B8A8E8", 0.6))
    out.append(tail_light(D, 568, 214, 26, 7, lens=("#FFB070", "#F2601A", "#8A2A06")) + tail_light(D, 36, 270, 22, 8, lens=("#FFB070", "#F2601A", "#8A2A06")))
    out.append(asphalt(D, 548, 9, base="#2A2434", cols=("#3A3448", "#1A1622", "#4A4458")))
    out.append(chrome_bar(D, -40, 486, 640, 556, 10, sky_c="#6A5A9A", ground="#2A1E30", r=20, horizon=0.45))
    # pennant-ended orange sticker
    pts = poly([(56, 262), (544, 262), (522, 361), (544, 460), (56, 460), (78, 361)], 12)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#FFB070", "#F07A22", "#A8460A"), 11)
    c = [f'<path d="{smooth_closed(poly([(80, 278), (520, 278), (502, 361), (520, 444), (80, 444), (98, 361)], 12))}" fill="none" stroke="#1E1830" stroke-width="3" stroke-dasharray="3 8" stroke-linecap="round"/>']
    c.append(vt(D, 300, 320, "MY OTHER CAR", BEBAS, 56, "#1E1830", 12, max_w=360, ls=6))
    c.append(vt(D, 300, 400, "IS A BROOM", ANTON, 84, "#1E1830", 13, max_w=348, ls=4, shadow="#FFD8A0", soff=(0.025, 0.035)))
    c.append(small(300, 436, "witchy & proud", SERIF_IT, 26, "#1E1830", max_w=220))
    c.append(star(118, 326, 9, "#1E1830") + star(482, 326, 9, "#1E1830") + star(106, 300, 5, "#1E1830") + star(494, 300, 5, "#1E1830"))
    out.append(black_cat(D, 196, 212, 34, 17))
    over = broom(D, 300, 486, 70, 470, 14)
    out.append(sticker(D, pts, face, "".join(c), rot_=2, peel=(-130, 28), seed=15))
    out.append(over)
    return finish(D, out, 16, "#1A1030", 0.6)


# ================================================================ 6. NORMAL IS BORING — scalloped groovy decal on a seventies van
@design("normal-is-boring")
def normal_is_boring():
    D = Doc("nib")
    out = []
    side = "M -10 -10 L 610 -10 L 610 610 L -10 610 Z"
    out.append(car_paint(D, side, (0, 0, 600, 600), ("#C8A8E8", "#8E68C0", "#4A2E7A"), 3, sky_band=(0.03, 0.1)))
    # groovy flowing stripes across the van side
    for k, (col, off) in enumerate((("#FF8A3A", 0), ("#FFC93C", 34), ("#FF5FA2", 68))):
        top = [(x, 420 + off + 40 * math.sin(x / 95 + 0.6)) for x in range(-20, 641, 20)]
        bot = [(x, y + 30) for x, y in top][::-1]
        out.append(painted(D, top + bot, (mix(col, "#FFFFFF", 0.3), col, mix(col, "#000000", 0.3)), 4 + k, sk=0.1, angle=0, n=30, inkw=1.6, hi=0.3, edge=False))
    for k, (col, off) in enumerate((("#FF8A3A", 0), ("#FFC93C", 34), ("#FF5FA2", 68))):
        top = [(x, 40 + off + 30 * math.sin(x / 95 + 2.6)) for x in range(-20, 641, 20)]
        bot = [(x, y + 30) for x, y in top][::-1]
        out.append(painted(D, top + bot, (mix(col, "#FFFFFF", 0.3), col, mix(col, "#000000", 0.3)), 14 + k, sk=0.1, angle=0, n=30, inkw=1.6, hi=0.3, edge=False))
    out.append(rivets(10, 600, 572, 40, "#6A4A9A", "#E8D8FF"))
    # scalloped sticker
    pts = []
    cx, cy, rx, ry = 300, 300, 240, 140
    for i in range(240):
        a = 2 * math.pi * i / 240
        k = 1 + 0.045 * abs(math.sin(a * 9)) ** 0.6
        pts.append((cx + rx * k * math.cos(a) * 1.0, cy + ry * k * math.sin(a)))
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#FFC8DA", "#FF8FB1", "#C04A7A"), 11)
    face += stripes_in(D, d, (40, 150, 560, 450), 0, [16, 16], ["#FFA8C4", None], 12, 0.0)
    c = [f'<path d="{smooth_closed(oval(cx, cy, 226, 126, 64))}" fill="none" stroke="#4B2C64" stroke-width="3"/>']
    for i, (x, y, r_, sd) in enumerate(((128, 226, 22, 13), (470, 228, 18, 14), (150, 384, 14, 15), (456, 376, 20, 16))):
        c.append(daisy(D, x, y, r_, sd, n=9, petal=("#FFFFFF", "#FFF8EE", "#D8C8D8"), center=("#FFEB8A", "#FFC93C", "#D98E12")))
    c.append(vt(D, 300, 300, "NORMAL", ANTON, 118, "#4B2C64", 17, max_w=300, ls=6, outline="#FFFFFF", ow=0.06, shadow="#2E1A44", soff=(0.04, 0.05)))
    c.append(vt(D, 300, 366, "IS BORING", BEBAS, 64, "#4B2C64", 18, max_w=250, ls=8))
    c.append(small(300, 404, "stay weird", SERIF_IT, 30, "#FFFFFF", max_w=200))
    out.append(sticker(D, pts, face, "".join(c), rot_=-4, peel=(30, 24), seed=19))
    return finish(D, out, 20, INK, 0.6)


# ================================================================ 7. GOOD THINGS TAKE TIME — a real snail crossing the sticker
@design("good-things-take-time")
def good_things_take_time():
    D = Doc("gtt")
    out = [sky(D, [(0, "#9AD4F0"), (0.7, "#FFF0C8"), (1, "#FFE0A8")], 3, 330, ["#FFFFFF", "#C8E8F8"], 30)]
    out.append(puff_cloud(D, 140, 90, 170, 4, op=0.95) + puff_cloud(D, 480, 120, 130, 5, op=0.9))
    out.append(hill(D, ridge([(-20, 200), (180, 176), (380, 196), (620, 170)], 5, 10), 600, ("#C8DCA0", "#9AB878", "#6A8A50"), 5, inkw=0))
    out.append(hill(D, ridge([(-20, 250), (260, 226), (620, 250)], 6, 8), 600, ("#A8C878", "#7AA058", "#4A6E36"), 6, inkw=1.4, inkop=0.3))
    # a winding country road
    road = smooth_closed([(250, 236), (270, 236), (330, 330), (520, 470), (640, 560), (640, 620), (420, 620), (380, 520), (290, 360)])
    out.append(f'<path d="{road}" fill="#C8B490"/>' + strokes(D.nid(), road, (200, 230, 640, 620), ["#E8D8B8", "#A08A6A"], 7, n=60, angle=30, length=(20, 60), width=(2, 4), opacity=(0.2, 0.4)))
    out.append(hill(D, ridge([(-20, 470), (300, 452), (620, 470)], 8, 6), 600, ("#9AC86A", "#6A9A48", "#3E6A2E"), 8, inkw=1.4, inkop=0.3))
    out.append(grass(9, (0, 470, 600, 600), ["#4E8A36", "#7AB04A", "#3A6A2A", "#A8D070"], 260, (10, 24)))
    rnd = random.Random(10)
    for i in range(40):
        x, y = rnd.uniform(0, 600), rnd.uniform(480, 600)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(2.5, 4.5):.1f}" fill="{rnd.choice(["#FFFFFF", "#FFE04A", "#F48AA0", "#C8A0F0"])}"/>')
    # fence posts
    for i, x in enumerate((40, 110, 180)):
        out.append(painted(D, poly([(x - 6, 250 - i * 6), (x + 6, 250 - i * 6), (x + 6, 300 - i * 4), (x - 6, 300 - i * 4)], 8), WOOD, 11 + i, sk=0.2, n=4, inkw=1.6, hi=0.3))
    out.append(pline([(30, 262), (190, 246)], WOOD[2], 3, 12, 0.8, 1) + pline([(30, 280), (190, 264)], WOOD[2], 3, 13, 0.8, 1))
    # olive oval sticker
    pts = oval(300, 370, 238, 136, 64)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#F8F0DC", "#F2E8D0", "#C8B48A"), 14)
    c = [f'<path d="{smooth_closed(oval(300, 370, 224, 122, 64))}" fill="none" stroke="{OLIVE[1]}" stroke-width="6"/>',
         f'<path d="{smooth_closed(oval(300, 370, 214, 112, 64))}" fill="none" stroke="{OLIVE[1]}" stroke-width="1.6"/>']
    c.append(vt(D, 300, 362, "GOOD THINGS", ANTON, 74, OLIVE[2], 15, max_w=360, ls=4, shadow="#E8A848", soff=(0.025, 0.035)))
    c.append(vt(D, 300, 430, "TAKE TIME", BEBAS, 70, "#C0532C", 16, max_w=300, ls=8))
    c.append(small(300, 292, "— slow down, friend —", SERIF_IT, 26, OLIVE[2], max_w=260))
    for x in (170, 430):
        c.append(f'<path d="{blob(x, 444, 9, 4, x, 0.1, 8)}" fill="{OLIVE[1]}" transform="rotate(-30 {x} 444)"/>')
    out.append(sticker(D, pts, face, "".join(c), rot_=-3, seed=17))
    # the snail on the sticker's top edge, with a glistening trail behind it
    trail = [(186, 246), (230, 238), (276, 234), (318, 234)]
    out.append(taper(trail, 2, 8, "#FFFFFF", 0.55) + taper([(x, y + 2) for x, y in trail], 1, 3, "#C8D8E8", 0.5))
    out.append(snail(D, 360, 214, 46, 18))
    return finish(D, out, 21, INK, 0.7)


# ================================================================ 8. WORK HARD NAP HARDER — riveted camper at night, sleeping cat
@design("work-hard-nap-harder")
def work_hard_nap_harder():
    from halloween_gouache_a import stars
    D = Doc("whn")
    out = [sky(D, [(0, "#0E1A3A"), (1, "#2A3A6A")], 3, 140, ["#2A3A6A", "#0E1A3A"], 20)]
    out.append(stars(4, 30, (0, 0, 600, 120), col="#FFF2C8", tw=4))
    # crescent moon
    out.append(soft_glow(D, 500, 66, 110, "#FFE9B0", 0.35))
    out.append(f'<path d="{lpath(crescent(500, 66, 40, 18, -12, 36))}" fill="#FFF0C0"/>')
    # aluminium camper skin: curved top, vertical seams, rivets
    skin = smooth_closed([(-20, 160), (100, 120), (300, 108), (500, 120), (620, 160), (620, 620), (-20, 620)])
    out.append(car_paint(D, skin, (0, 108, 600, 600), ("#FFFBF0", "#F2E6CC", "#B8A27A"), 5, sky_band=(0.02, 0.12)))
    belt = "M -10 488 L 610 488 L 610 548 L -10 548 Z"
    out.append(painted(D, poly([(-10, 488), (610, 488), (610, 548), (-10, 548)], 30), TEAL, 51, sdir=(0, 1), sk=0.15, angle=0, n=30, inkw=1.8, hi=0.3))
    out.append(taper([(-10, 482), (610, 482)], 6, 6, "#E8EEF2") + taper([(-10, 554), (610, 554)], 6, 6, "#E8EEF2"))
    cid = D.clip(f'<path d="{skin}"/>')
    seams = "".join(f'<path d="M {x} 100 L {x} 610" stroke="#A89470" stroke-width="2" opacity="0.6"/><path d="M {x + 3} 100 L {x + 3} 610" stroke="#FFFFFF" stroke-width="1.5" opacity="0.6"/>' for x in (130, 300, 470))
    out.append(f'<g {cid}>{seams}{rivets(10, 600, 150, 26, "#B8A27A")}</g>')
    # a string of warm cafe lights along the roofline
    lights = [(x, 128 + 22 * math.sin(math.pi * ((x + 20) % 210) / 210)) for x in range(-20, 640, 12)]
    out.append(pline(lights, "#3A3020", 2, 6, 0.9, 1))
    for i, x in enumerate(range(-10, 620, 42)):
        y = 128 + 22 * math.sin(math.pi * ((x + 20) % 210) / 210) + 10
        col = ("#FFE9A0", "#FFB870", "#FFD0E0")[i % 3]
        out.append(soft_glow(D, x, y + 6, 30, "#FFD27A", 0.45))
        out.append(f'<path d="{blob(x, y + 6, 6, 9, i, 0.05, 10)}" fill="{col}" stroke="#8A6A3A" stroke-width="1.2"/>'
                   f'<rect x="{x - 3}" y="{y - 6}" width="6" height="6" fill="#3A3020"/>')
    out.append(asphalt(D, 560, 7, base="#1E2236", cols=("#2A3048", "#141828", "#343A54")))
    # navy sticker
    pts = rrect(62, 196, 538, 476, 34)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, NAVY, 11)
    c = [f'<path d="{smooth_closed(rrect(78, 212, 522, 460, 22))}" fill="none" stroke="#F6EFE0" stroke-width="3" stroke-dasharray="2 9" stroke-linecap="round"/>']
    c.append(f'<path d="{smooth_closed(oval(160, 340, 86, 86))}" fill="#2E4E80"/>')
    c.append(sleeping_cat(D, 166, 350, 72, 12))
    c.append(zzz(196, 268, 32, "#FFE9B0"))
    c.append(vt(D, 370, 314, "WORK HARD", BEBAS, 82, "#F6EFE0", 13, max_w=270, ls=4))
    c.append(hbar(D, 248, 492, 330, 4, "#F2C230", 14))
    c.append(vt(D, 370, 420, "NAP HARDER", ANTON, 84, "#F2C230", 15, max_w=270, ls=3, shadow="#0C1C36", soff=(0.03, 0.04)))
    for x, y, r_ in ((100, 240, 6), (230, 440, 5), (500, 236, 5)):
        c.append(star(x, y, r_, "#FFE9B0"))
    out.append(sticker(D, pts, face, "".join(c), rot_=2.5, peel=(-140, 30), seed=16))
    return finish(D, out, 17, INK, 0.6)



def beach_umbrella(D, cx, top, r, seed, cols=("#FF5FA2", "#FFFFFF"), pole_h=None, tilt=-8):
    """Side-view striped beach umbrella: domed canopy with scalloped hem, wooden pole."""
    pole_h = pole_h or r * 1.3
    out = [f'<g transform="rotate({tilt} {cx} {top + pole_h})">']
    out.append(pline([(cx, top), (cx, top + pole_h)], WOOD[2], max(2.5, r * 0.06), seed, 1, 1))
    n = 6
    for i in range(n):
        a0, a1 = math.pi + math.pi * i / n, math.pi + math.pi * (i + 1) / n
        p0 = (cx + r * math.cos(a0), top + r * 0.18 + r * 0.55 * math.sin(a0))
        p1 = (cx + r * math.cos(a1), top + r * 0.18 + r * 0.55 * math.sin(a1))
        mid = (cx + r * 0.25 * math.cos((a0 + a1) / 2), top - r * 0.48)
        hem = ((p0[0] + p1[0]) / 2, top + r * 0.3)
        pts = [p0, (mid[0] + (p0[0] - p1[0]) * 0.1, top - r * 0.3), (cx, top - r * 0.52), (mid[0] - (p0[0] - p1[0]) * 0.1, top - r * 0.3), p1, hem]
        col = cols[i % len(cols)]
        out.append(f'<path d="M {p0[0]:.1f} {p0[1]:.1f} Q {cx + (p0[0] - cx) * 0.55:.1f} {top - r * 0.55:.1f} {cx:.1f} {top - r * 0.55:.1f} '
                   f'Q {cx + (p1[0] - cx) * 0.55:.1f} {top - r * 0.55:.1f} {p1[0]:.1f} {p1[1]:.1f} Q {hem[0]:.1f} {hem[1]:.1f} {p0[0]:.1f} {p0[1]:.1f} Z" fill="{col}" stroke="{INK}" stroke-width="1.6" stroke-opacity="0.6"/>')
    out.append(f'<path d="M {cx - r:.1f} {top + r * 0.18:.1f} Q {cx:.1f} {top - r * 1.05:.1f} {cx + r:.1f} {top + r * 0.18:.1f}" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.4"/>')
    out.append(f'<circle cx="{cx}" cy="{top - r * 0.56:.1f}" r="{max(2.5, r * 0.06):.1f}" fill="{WOOD[2]}"/>')
    out.append("</g>")
    return "".join(out)


def taco(D, cx, cy, s, seed):
    """Crunchy taco, side view: folded golden shell, lettuce ruffle, tomato, cheese."""
    out = [cast(D, cx, cy + s * 0.5, s * 1.1, s * 0.1, strength=0.3, seed=seed)]
    # back half of shell
    back = [(cx - s, cy + s * 0.35)] + [(cx + s * math.cos(math.radians(a)), cy + s * 0.35 - s * 0.95 * math.sin(math.radians(a))) for a in range(170, 9, -16)] + [(cx + s, cy + s * 0.35)]
    out.append(painted(D, back, ("#FFE08A", "#E8B040", "#A8701A"), seed, sk=0.15, n=10, inkw=2, hi=0.3))
    # fillings poking above the shell rim
    rnd = random.Random(seed)
    for i in range(14):
        a = math.radians(160 - i * 10.5)
        x, y = cx + s * 0.88 * math.cos(a), cy + s * 0.3 - s * 0.86 * math.sin(a)
        out.append(f'<path d="{blob(x, y - s * 0.08, s * 0.16, s * 0.1, seed + i, 0.35, 10, math.degrees(-a) + 90)}" fill="{["#7AC84A", "#4E9A36", "#9ADB6A"][i % 3]}" stroke="#2E6A22" stroke-width="1.2"/>')
    for i in range(5):
        a = math.radians(150 - i * 28)
        x, y = cx + s * 0.78 * math.cos(a), cy + s * 0.28 - s * 0.78 * math.sin(a)
        out.append(painted(D, oval(x, y, s * 0.13, s * 0.09, 16), ("#FF8A7A", "#E8423A", "#9A1A1A"), seed + 20 + i, sk=0.2, n=3, inkw=1.4, hi=0.4))
    for i in range(8):
        a = math.radians(160 - i * 19)
        x, y = cx + s * 0.8 * math.cos(a), cy + s * 0.26 - s * 0.8 * math.sin(a)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {rnd.uniform(-8, 8):.1f} {rnd.uniform(4, 12):.1f}" stroke="#FFC93C" stroke-width="{s * 0.06:.1f}" stroke-linecap="round"/>')
    # front half of shell
    front = [(cx - s * 1.02, cy + s * 0.36)] + [(cx + s * 1.02 * math.cos(math.radians(a)), cy + s * 0.36 - s * 0.62 * math.sin(math.radians(a))) for a in range(176, 4, -12)] + [(cx + s * 1.02, cy + s * 0.36), (cx, cy + s * 0.5)]
    out.append(painted(D, front, ("#FFE89A", "#F2C04A", "#B0781A"), seed + 1, sdir=(0.3, 1), sk=0.2, angle=-20, n=26, inkw=2.4, hi=0.4))
    for i in range(12):
        x, y = cx + rnd.uniform(-0.8, 0.8) * s, cy + rnd.uniform(-0.1, 0.35) * s
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s * 0.025:.1f}" fill="#B0781A" opacity="0.6"/>')
    return "".join(out)


def minivan(D, cx, base, s, seed, body=SKY, flip=1):
    """Little family minivan, side view, facing right. s ~ half length."""
    g = f'<g transform="translate({cx} {base}) scale({flip} 1) translate({-cx} {-base})">'
    k = s
    pts = [(cx - k, base - k * 0.22), (cx - k * 0.98, base - k * 0.78), (cx - k * 0.9, base - k * 0.86), (cx + k * 0.28, base - k * 0.86),
           (cx + k * 0.66, base - k * 0.5), (cx + k * 0.96, base - k * 0.42), (cx + k * 1.0, base - k * 0.22)]
    out = [g, cast(D, cx, base, k * 1.1, k * 0.08, strength=0.35, seed=seed)]
    out.append(painted(D, poly(pts, 10), body, seed, sdir=(0.2, 1), sk=0.15, angle=0, n=20, inkw=2.2, hi=0.4))
    for x0, x1 in ((-0.88, -0.48), (-0.42, -0.02), (0.04, 0.3)):
        wp = poly([(cx + k * x0, base - k * 0.78), (cx + k * (x1 if x1 < 0.25 else 0.24), base - k * 0.78), (cx + k * (x1 + 0.2 if x1 > 0.25 else x1), base - k * 0.52), (cx + k * x0, base - k * 0.52)], 8)
        out.append(glass(D, smooth_closed(wp), bbox(wp), seed, top="#E8FAFF", bot="#7AB8D8"))
        out.append(ink(smooth_closed(wp), INK, 1.6, seed, 1, 0.7))
    out.append(taper([(cx - k * 0.98, base - k * 0.36), (cx + k * 0.98, base - k * 0.36)], 4, 4, "#FFFFFF", 0.7))
    out.append(f'<circle cx="{cx + k * 0.94:.1f}" cy="{base - k * 0.3:.1f}" r="{k * 0.05:.1f}" fill="#FFF6C0" stroke="{INK}" stroke-width="1.2"/>')
    for x in (-0.6, 0.6):
        out.append(wheel(D, cx + k * x, base - k * 0.16, k * 0.18, seed + int(x * 10)))
    out.append("</g>")
    return "".join(out)


def rain(seed, box, n=120, col="#E8F0FF"):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        L = rnd.uniform(14, 34)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {-L * 0.18:.1f} {L:.1f}" stroke="{col}" stroke-width="{rnd.uniform(1, 2):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.3, 0.7):.2f}"/>')
    return "".join(out)


def droplets(D, seed, box, n=30, rr=(2, 6)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(*rr)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 1.15:.1f}" fill="#FFFFFF" opacity="0.18"/>'
                   f'<path d="M {x - r * 0.5:.1f} {y + r * 0.6:.1f} q {r * 0.5:.1f} {r * 0.5:.1f} {r:.1f} 0" stroke="#FFFFFF" stroke-width="1.2" fill="none" opacity="0.6"/>'
                   f'<circle cx="{x - r * 0.35:.1f}" cy="{y - r * 0.4:.1f}" r="{r * 0.25:.1f}" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


def papel_picado(D, y, seed, cols=("#FF5FA2", "#FFC93C", "#2AA59A", "#FF8A2A", "#8A5AD0"), w=74):
    out = [pline([(-10, y), (300, y + 10), (610, y)], "#5A4A3A", 2, seed, 0.9, 1)]
    rnd = random.Random(seed)
    for i, x in enumerate(range(-20, 620, w + 6)):
        yy = y + 10 * math.sin(math.pi * (x + w / 2 + 10) / 620) + 1
        c = cols[i % len(cols)]
        flag = poly([(x, yy), (x + w, yy), (x + w, yy + 52), (x + w * 0.75, yy + 60), (x + w * 0.5, yy + 52), (x + w * 0.25, yy + 60), (x, yy + 52)], 10)
        out.append(painted(D, flag, (mix(c, "#FFFFFF", 0.3), c, mix(c, "#000000", 0.3)), seed + i, sk=0.1, n=6, inkw=1.2, hi=0.3, edge=False))
        for k in range(3):
            out.append(f'<path d="{blob(x + w * (0.25 + 0.25 * k), yy + 22 + (k % 2) * 10, 6, 6, i * 3 + k, 0.2, 8)}" fill="#FFF4E0" opacity="0.85"/>')
    return "".join(out)


# ================================================================ 9. DO MORE OF WHAT MAKES YOU HAPPY — sunrise die-cut over a beach at dusk
@design("do-more-of-what-makes-you-happy")
def do_more():
    D = Doc("dmw")
    out = [sky(D, [(0, "#FF7A8A"), (0.45, "#FFA870"), (0.8, "#FFD88A")], 3, 380, ["#FFC0A0", "#FF8A8A", "#FFE0B0"], 40)]
    out.append(puff_cloud(D, 470, 96, 180, 4, ("#FFE0D0", "#FFA0A0", "#C86A8A"), op=0.9) + puff_cloud(D, 110, 140, 140, 5, ("#FFE0D0", "#FFA0A0", "#C86A8A"), op=0.85))
    out.append(f'<rect y="380" width="600" height="80" fill="{D.lin([(0, "#3A9AC0"), (1, "#1E6A9A")])}"/>' + wave_lines(6, (0, 386, 600, 456), ["#9AF0EC", "#FFFFFF", "#FFC0A0"], 40))
    out.append(hill(D, ridge([(-20, 452), (300, 444), (620, 456)], 7, 4), 600, ("#FFF0CE", "#F6D9A0", "#C9A066"), 7, inkw=0))
    out.append(specks(8, (0, 460, 600, 600), ["#C9A066", "#FFFFFF"], 120, (0.6, 1.6)))
    out.append(palm(D, (30, 640), (70, 300), 9, [(-150, 0.9), (-120, 0.85), (-90, 0.7), (-55, 0.85), (-20, 1.0), (5, 0.95), (-185, 0.8)], L=100, sil="#5A2A4A", rim="#FFB08A",
                    leaf_cols=["#5A2A4A", "#6A3456", "#5A2A4A"], width=18))
    out.append(palm(D, (590, 640), (540, 330), 10, [(-160, 1.0), (-185, 0.95), (-130, 0.8), (-95, 0.75), (-60, 0.85), (-25, 0.9)], L=90, sil="#5A2A4A", rim="#FFB08A",
                    leaf_cols=["#5A2A4A", "#6A3456", "#5A2A4A"], width=16))
    # surfboard stuck in the sand
    from summer_gouache import surfboard
    out.append(surfboard(D, 400, 600, 520, 46, ("#BFF4EE", "#5AD0C8", "#1F8A84"), "#FF6F59", 11, -78))
    # sticker: a retro striped sunset half-disc sitting on a rounded base
    sc, sr = (300, 330), 206
    arc = [(sc[0] + sr * math.cos(math.radians(a_)), sc[1] + sr * math.sin(math.radians(a_))) for a_ in range(180, 361, 6)]
    base = rrect(58, 316, 542, 484, 30, 12)
    pts = [(58, 340)] + [p for p in arc if p[0] > 70 and p[0] < 530] + [(542, 340)] + [p for p in base if p[1] > 340]
    pts = arc[:1] and ([(58, 344), (64, 330)] + [p for p in arc if 96 < p[0] < 504] + [(536, 330), (542, 344)] + [p for p in base if p[1] > 345])
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, CORAL, 12, fade=0.15)
    sun = smooth_closed(arc + [(sc[0] + sr, sc[1] + 2), (sc[0] - sr, sc[1] + 2)])
    sun_g = D.lin([(0, "#FFF2A8"), (0.45, "#FFD23A"), (1, "#FF9A3A")], 0, sc[1] - sr, 0, sc[1], "userSpaceOnUse")
    c = [f'<path d="{sun}" fill="{sun_g}"/>']
    c.append(strokes(D.nid(), sun, (sc[0] - sr - 40, sc[1] - sr, sc[0] + sr, sc[1]), ["#FFF6C8", "#FFB43A"], 13, n=60, angle=-20, length=(20, 60), width=(2, 6), opacity=(0.15, 0.4)))
    # the classic sunset stripes cut across the lower half of the sun
    for k, (y, h) in enumerate(((246, 7), (270, 10), (296, 13))):
        c.append(f'<rect x="60" y="{y}" width="480" height="{h}" fill="{CORAL[1]}"/>')
    c.append(f'<path d="{smooth_closed([(sc[0] + (sr - 14) * math.cos(math.radians(a_)), sc[1] + (sr - 14) * math.sin(math.radians(a_))) for a_ in range(180, 361, 6)])}" fill="none" stroke="#FFF4E0" stroke-width="2.5" stroke-dasharray="2 8" stroke-linecap="round" opacity="0.9"/>')
    c.append(vt(D, 300, 214, "do more of what", SERIF_IT, 50, "#A82A2A", 14, max_w=310, wob=0.3, density=0.3))
    c.append(hbar(D, 70, 530, 330, 3, "#FFF4E0", 15))
    c.append(vt(D, 300, 378, "MAKES YOU", BEBAS, 40, "#5A1A2A", 16, max_w=250, ls=12, wob=0.15, density=0.3))
    c.append(vt(D, 300, 468, "HAPPY", ANTON, 82, "#FFF4E0", 17, max_w=300, ls=12, shadow="#A82A2A", soff=(0.03, 0.04)))
    c.append(star(116, 420, 9, "#FFF4E0") + star(484, 420, 9, "#FFF4E0") + star(140, 448, 5, "#FFF4E0") + star(460, 448, 5, "#FFF4E0"))
    out.append(sticker(D, pts, face, "".join(c), rot_=-2, peel=(20, 26), seed=17))
    return finish(D, out, 18, INK, 0.6)


def sunflower(D, cx, cy, r, seed):
    """Lighter-weight painted sunflower: two rings of two-tone petals with an inked vein, seeded disc."""
    rnd = random.Random(seed)
    out = []
    for layer, (n, rr, off, pal) in enumerate(((22, 1.0, 0, ("#FFE060", "#F2B21A", "#C8740A")), (20, 0.86, 8, ("#FFEA7A", "#FFC21A", "#D8860A")))):
        for i in range(n):
            a = math.radians(i * 360 / n + off + rnd.uniform(-4, 4))
            L = r * rr * rnd.uniform(0.9, 1.05)
            pts = []
            for j in range(9):
                t = j / 8
                pts.append((r * 0.36 + L * 0.62 * t, L * 0.13 * math.sin(math.pi * t) ** 0.8))
            c, s_ = math.cos(a), math.sin(a)
            outline = [(cx + c * d - s_ * w, cy + s_ * d + c * w) for d, w in pts] + [(cx + c * d + s_ * w, cy + s_ * d - c * w) for d, w in pts[::-1]]
            half = [(cx + c * d - s_ * w, cy + s_ * d + c * w) for d, w in pts] + [(cx + c * d, cy + s_ * d) for d, w in pts[::-1]]
            out.append(f'<path d="{smooth_closed(outline)}" fill="{pal[1]}" stroke="{pal[2]}" stroke-width="1.2" stroke-opacity="0.6"/>'
                       f'<path d="{smooth_closed(half)}" fill="{pal[2] if layer == 0 else pal[0]}" opacity="0.35"/>')
            out.append(f'<path d="M {cx + c * r * 0.42:.1f} {cy + s_ * r * 0.42:.1f} L {cx + c * (r * 0.36 + L * 0.5):.1f} {cy + s_ * (r * 0.36 + L * 0.5):.1f}" stroke="{pal[2]}" stroke-width="1" opacity="0.5"/>')
    disc = blob_pts(cx, cy, r * 0.42, r * 0.42, seed, 0.02, 20)
    out.append(painted(D, disc, ("#A8682A", "#6A3A16", "#2E1608"), seed + 99, sk=0.15, n=8, inkw=2, hi=0.2))
    golden = math.pi * (3 - math.sqrt(5))
    for i in range(90):
        rr = r * 0.38 * math.sqrt(i / 90)
        a = i * golden
        col = "#E8A040" if rr < r * 0.12 else ("#3A1E0A" if i % 3 else "#8A5A2A")
        out.append(f'<circle cx="{cx + rr * math.cos(a):.1f}" cy="{cy + rr * math.sin(a):.1f}" r="{max(1.4, 3 * (0.5 + rr / (r * 0.8))):.1f}" fill="{col}" opacity="0.85"/>')
    return "".join(out)


# ================================================================ 10. BE THE GOOD — teal heart sticker over a sunflower field
@design("be-the-good")
def be_the_good():
    D = Doc("btg")
    out = [sky(D, [(0, "#7FD3F0"), (0.7, "#D4F4FF"), (1, "#FFF6D8")], 3, 300, ["#FFFFFF", "#A8E0F4"], 30)]
    out.append(puff_cloud(D, 380, 84, 200, 4, op=0.95))
    # a heart-shaped kite riding the breeze, bow tail fluttering
    tail = catmull([(126, 120), (150, 160), (132, 196), (160, 230)], 6)
    out.append(pline(tail, "#5A4A3A", 1.6, 3, 0.8, 1))
    for i, k in enumerate(range(3, len(tail) - 1, 4)):
        x, y = tail[k]
        col = ("#FFC93C", "#2AA59A", "#F27A9A", "#7A5AD0")[i % 4]
        out.append(f'<path d="{lpath([(x - 9, y - 6), (x, y), (x - 9, y + 6)])}" fill="{col}"/><path d="{lpath([(x + 9, y - 6), (x, y), (x + 9, y + 6)])}" fill="{col}"/>')
    out.append(pline([(126, 104), (260, 240)], "#FFFFFF", 1.4, 4, 0.8, 1))
    out.append(heart_path(D, 120, 88, 30, CORAL, 5))
    out.append(pline([(120, 64), (120, 116)], "#A83A2A", 1.4, 6, 0.6, 1) + pline([(94, 84), (146, 84)], "#A83A2A", 1.4, 7, 0.6, 1))
    out.append(hill(D, ridge([(-20, 200), (300, 188), (620, 204)], 5, 6), 600, ("#C8E0A0", "#9AC078", "#6A9050"), 5, inkw=0))
    rnd = random.Random(6)
    for i in range(46):
        x, y = rnd.uniform(-10, 610), rnd.uniform(205, 250)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(4, 7):.1f}" fill="#FFC21A"/><circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="#6A3A16"/>')
    out.append(hill(D, ridge([(-20, 250), (300, 240), (620, 252)], 7, 4), 600, ("#9AC86A", "#5E9A40", "#2E5E26"), 7, inkw=0))
    for i, (x, y, r_) in enumerate(((60, 300, 58), (548, 290, 62), (40, 540, 70), (560, 548, 66), (300, 580, 50))):
        out.append(pline([(x, y + r_ * 0.5), (x + 4, y + 160)], "#3E7A2E", 7, i, 1, 1))
        out.append(sunflower(D, x, y, r_, 10 + i))
    pts = rrect(64, 226, 536, 466, 40)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#7AD8D0", "#1FA6A6", "#0E6A6A"), 12)
    c = [f'<path d="{smooth_closed(rrect(78, 240, 522, 452, 28))}" fill="none" stroke="#F6EFE0" stroke-width="5"/>']
    # heart with sun rays
    hx, hy = 176, 342
    for k in range(12):
        a = math.radians(k * 30)
        c.append(taper([(hx + 62 * math.cos(a), hy + 62 * math.sin(a)), (hx + 82 * math.cos(a), hy + 82 * math.sin(a))], 6, 2, "#FFE27A", 0.95))
    hp = []
    for i in range(48):
        t = 2 * math.pi * i / 48
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        hp.append((hx + x * 3.2, hy + y * 3.2 + 4))
    c.append(painted(D, hp, CORAL, 13, sdir=(0.5, 0.7), sk=0.18, angle=-40, n=30, inkw=2.4, hi=0.45, curve=0.5))
    c.append(taper([(hx - 30, hy - 14), (hx - 20, hy - 30)], 7, 2, "#FFFFFF", 0.7))
    c.append(vt(D, 384, 296, "BE THE", JOS, 50, "#F6EFE0", 14, max_w=220, ls=10))
    c.append(vt(D, 384, 398, "GOOD", ANTON, 120, "#FFE27A", 15, max_w=250, ls=8, shadow="#0E5050", soff=(0.03, 0.04)))
    c.append(small(384, 432, "pass it on", SERIF_IT, 26, "#F6EFE0", max_w=200))
    out.append(sticker(D, pts, face, "".join(c), rot_=3, peel=(35, 28), seed=16))
    return finish(D, out, 17, INK, 0.6)


# ================================================================ 11. MY OTHER CAR IS A MINIVAN — stuck on a little red wagon
@design("my-other-car-is-a-minivan")
def my_other_car_is_a_minivan():
    D = Doc("mom")
    out = [sky(D, [(0, "#8ED8F8"), (1, "#E0F6FF")], 3, 220, ["#FFFFFF", "#B8E8FA"], 20)]
    out.append(puff_cloud(D, 470, 80, 160, 4, op=0.95))
    # white picket fence and a hedge
    out.append(f'<path d="{blob(300, 210, 420, 60, 5, 0.05, 20)}" fill="#4E8A3E"/>')
    for i, x in enumerate(range(-10, 620, 44)):
        pk = poly([(x, 236), (x + 13, 210), (x + 26, 236), (x + 26, 330), (x, 330)], 8)
        out.append(painted(D, pk, ("#FFFFFF", "#F2EEE6", "#B8B0A6"), 6 + i, sk=0.15, n=4, inkw=1.4, hi=0.3))
    out.append(painted(D, poly([(-10, 252), (610, 252), (610, 266), (-10, 266)], 30), ("#FFFFFF", "#F2EEE6", "#B8B0A6"), 30, sk=0.15, n=10, inkw=1.4, hi=0.3))
    out.append(hill(D, [(-20, 320), (300, 316), (620, 322)], 600, ("#9AD06A", "#6AAE48", "#3E7A2E"), 7, inkw=0))
    out.append(grass(8, (0, 330, 600, 600), ["#4E8A36", "#7AB04A", "#3A6A2A", "#A8D070"], 220, (8, 18)))
    # toys peeking over the wagon rim: a ball and a teddy ear
    bb = oval(470, 222, 44, 44, 30)
    out.append(painted(D, bb, ("#FFFFFF", "#F6F0E8", "#C8B8A8"), 9, sk=0.2, n=8, inkw=2, hi=0.45))
    cidb = D.clip(f'<path d="{smooth_closed(bb)}"/>')
    segs = "".join(f'<path d="M 470 222 L {470 + 70 * math.cos(math.radians(a_)):.1f} {222 + 70 * math.sin(math.radians(a_)):.1f} A 70 70 0 0 1 {470 + 70 * math.cos(math.radians(a_ + 42)):.1f} {222 + 70 * math.sin(math.radians(a_ + 42)):.1f} Z" fill="{c_}" opacity="0.92"/>'
                   for a_, c_ in ((-110, "#E8423A"), (10, "#2E8AD0"), (130, "#FFC93C")))
    out.append(f'<g {cidb}>{segs}<circle cx="456" cy="206" r="9" fill="#FFFFFF" opacity="0.6"/></g>' + ink(smooth_closed(bb), INK, 2, 9, 1, 0.7))
    out.append(painted(D, blob_pts(140, 224, 40, 34, 10, 0.03, 18), ("#E8B47A", "#C0864A", "#7A4E26"), 10, sk=0.2, n=10, inkw=2, hi=0.4))
    for sg in (-1, 1):
        out.append(painted(D, oval(140 + sg * 30, 196, 13, 13, 16), ("#E8B47A", "#C0864A", "#7A4E26"), 11, sk=0.2, n=3, inkw=1.8, hi=0.3))
    out.append(f'<circle cx="128" cy="220" r="3.5" fill="{INK}"/><circle cx="152" cy="220" r="3.5" fill="{INK}"/><path d="{blob(140, 234, 12, 9, 12, 0.05, 10)}" fill="#F2D8B0"/><circle cx="140" cy="231" r="3" fill="{INK}"/>')
    # red wagon body
    wag = poly([(28, 246), (572, 246), (556, 486), (44, 486)], 14)
    out.append(cast(D, 300, 548, 300, 22, strength=0.4))
    out.append(painted(D, wag, ("#FF7A6A", "#E0322A", "#8A1414"), 13, sdir=(0.3, 1), sk=0.12, angle=0, n=60, inkw=2.6, hi=0.35))
    out.append(painted(D, poly([(18, 236), (582, 236), (582, 256), (18, 256)], 20), ("#FF8A7A", "#C82A22", "#7A1010"), 14, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=2.2, hi=0.5))
    for x in (130, 470):
        out.append(painted(D, poly([(x - 30, 486), (x + 30, 486), (x + 20, 506), (x - 20, 506)], 8), BLACK, 15, sk=0.2, n=4, inkw=1.6, hi=0.3))
        out.append(wheel(D, x, 528, 46, 16 + x, cap="#E0322A"))
    # handle
    out.append(pline([(572, 440), (610, 470)], "#2A2430", 8, 17, 1, 1))
    # sticker
    pts = rrect(78, 276, 522, 460, 22)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, CREAM, 18)
    c = [hbar(D, 60, 540, 276, 22, NAVY[1], 19), hbar(D, 60, 540, 438, 22, NAVY[1], 20)]
    c.append(stars_row(300, 288, 9, 6, 52, "#FFFFFF"))
    c.append(stars_row(300, 450, 9, 6, 52, "#FFFFFF"))
    c.append(minivan(D, 164, 410, 70, 21))
    c.append(vt(D, 380, 352, "MY OTHER CAR", BEBAS, 54, NAVY[1], 22, max_w=250, ls=3))
    c.append(vt(D, 380, 414, "IS A MINIVAN", ANTON, 56, "#E0322A", 23, max_w=262, ls=1, shadow=NAVY[1], soff=(0.025, 0.035)))
    out.append(sticker(D, pts, face, "".join(c), rot_=-2, peel=(-150, 26), seed=24))
    return finish(D, out, 25, INK, 0.6)


# ================================================================ 12. I'D RATHER BE AT THE BEACH — a sunny decal on a car in the rain
@design("id-rather-be-at-the-beach")
def id_rather_be_at_the_beach():
    D = Doc("irb")
    out = []
    body = "M -10 -10 L 610 -10 L 610 610 L -10 610 Z"
    out.append(car_paint(D, body, (0, 0, 600, 600), ("#9AAAC0", "#5A6A86", "#2A3448"), 3, sky_band=(0.02, 0.14)))
    # rear window across the top, streaming with rain
    win = smooth_closed(rrect(40, -40, 560, 140, 40))
    out.append(glass(D, win, (40, -40, 560, 140), 4, top="#8A9AB0", bot="#3A4A64"))
    cid = D.clip(f'<path d="{win}"/>')
    out.append(f'<g {cid}>' + droplets(D, 5, (40, 0, 560, 140), 40, (2, 6)) + "".join(
        f'<path d="M {x} 0 q 3 40 -2 80 q -2 30 2 60" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.3"/>' for x in (120, 210, 330, 470)) + '</g>')
    out.append(ink(win, "#1A1E2A", 3, 6, 1, 0.8))
    out.append(tail_light(D, 20, 230, 36, 7, ring=False) + tail_light(D, 580, 230, 36, 8, ring=False))
    out.append(droplets(D, 9, (0, 140, 600, 600), 60, (2, 7)))
    out.append(asphalt(D, 548, 10, base="#3A3E4A", cols=("#4A4E5A", "#2A2E3A", "#5A5E6A")))
    out.append(f'<path d="{blob(300, 580, 260, 18, 11, 0.05, 16)}" fill="#E83A2A" opacity="0.18"/>')
    out.append(chrome_bar(D, -40, 486, 640, 552, 12, sky_c="#8A98AA", ground="#3A3A44", r=20, horizon=0.45))
    out.append(rain(13, (0, 0, 600, 600), 70))
    # sticker: a vintage postcard panel of sunshine
    pts = rrect(58, 196, 542, 452, 26)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#FFFFFF", "#FFF4E0", "#D8C8A8"), 14)
    panel = rrect(80, 218, 262, 430, 16)
    pd = smooth_closed(panel)
    pc = D.clip(f'<path d="{pd}"/>')
    scene = [sky(D, [(0, "#3AB8F0"), (1, "#C8F0FF")], 15, 340, None)]
    scene.append(sun_disc(D, 216, 262, 24, ("#FFFCE0", "#FFE87A", "#FFB43A"), 16, glow_r=2.4))
    scene.append(f'<rect x="70" y="330" width="210" height="40" fill="{D.lin([(0, "#1FB5B0"), (1, "#0E7A9A")])}"/>' + wave_lines(17, (80, 334, 262, 366), ["#FFFFFF", "#9AF0EC"], 14, (10, 24), 1.6))
    scene.append(f'<path d="M 70 372 Q 170 360 280 376 L 280 440 L 70 440 Z" fill="#F6D9A0"/>')
    scene.append(beach_umbrella(D, 150, 340, 46, 18, pole_h=60, tilt=-10))
    scene.append(seagull(214, 300, 9, "#3A4048") + seagull(234, 290, 6, "#3A4048"))
    out_panel = f'<g {pc}>{"".join(scene)}</g>' + ink(pd, INK, 2.2, 19, 1, 0.8)
    c = [out_panel]
    c.append(vt(D, 402, 276, "I'D RATHER BE", JOS, 40, "#1E6A9A", 20, max_w=240, ls=3))
    c.append(vt(D, 402, 338, "AT THE", BEBAS, 54, "#FF6F59", 21, max_w=240, ls=14, density=0.4))
    c.append(vt(D, 402, 426, "BEACH", ANTON, 86, "#1E6A9A", 22, max_w=240, ls=8, shadow="#FFC93C", soff=(0.03, 0.04)))
    c.append(hbar(D, 292, 512, 292, 3, "#FFC93C", 23))
    out.append(sticker(D, pts, face, "".join(c), rot_=-2.5, peel=(30, 28), seed=24))
    out.append(droplets(D, 25, (60, 200, 540, 450), 26, (2, 5)))
    return finish(D, out, 26, INK, 0.6)


# ================================================================ 13. HONK IF YOU LOVE TACOS — on a taco truck under papel picado
@design("honk-if-you-love-tacos")
def honk_if_you_love_tacos():
    D = Doc("hlt")
    out = []
    body = "M -10 -10 L 610 -10 L 610 610 L -10 610 Z"
    out.append(car_paint(D, body, (0, 0, 600, 600), ("#7AE0D4", "#22A89A", "#0E5E58"), 3, sky_band=(0.12, 0.22)))
    # serving window & striped awning at the top
    out.append(painted(D, poly([(120, -10), (480, -10), (480, 120), (120, 120)], 20), ("#3A3440", "#24202A", "#0E0A12"), 4, sk=0.2, n=10, inkw=2.4, hi=0.2))
    out.append(soft_glow(D, 300, 60, 160, "#FFD27A", 0.4))
    aw = poly([(90, -10), (510, -10), (530, 70), (70, 70)], 20)
    out.append(stripes_in(D, smooth_closed(aw), (70, -10, 530, 70), 0, [42, 42], ["#FF6F59", "#FFF4E0"], 5))
    for i, x in enumerate(range(70, 531, 46)):
        out.append(f'<path d="M {x} 68 Q {x + 23} 96 {x + 46} 68 Z" fill="{"#FF6F59" if i % 2 == 0 else "#FFF4E0"}" stroke="{INK}" stroke-width="1.6" stroke-opacity="0.6"/>')
    out.append(ink(smooth_closed(aw), INK, 2, 6, 1, 0.6))
    out.append(papel_picado(D, 128, 7))
    # stripe along the truck & wheel-arch
    out.append(taper([(-10, 520), (610, 520)], 24, 24, "#FFC93C") + taper([(-10, 536), (610, 536)], 6, 6, "#FF6F59"))
    out.append(asphalt(D, 566, 8, base="#5A5664"))
    # sticker: sunny yellow with a big taco breaking out of the top-left corner
    pts = rrect(62, 236, 538, 490, 32)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#FFF0A0", "#FFD23A", "#D8960A"), 9)
    face += "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#FFE680" opacity="0.8"/>' for x in range(70, 540, 28) for y in range(244, 490, 28) if (x // 28 + y // 28) % 2 == 0)
    c = [f'<path d="{smooth_closed(rrect(76, 250, 524, 476, 22))}" fill="none" stroke="#C0320E" stroke-width="4"/>']
    c.append(vt(D, 384, 320, "HONK IF YOU", BEBAS, 60, "#5A1E0A", 10, max_w=250, ls=3))
    c.append(vt(D, 384, 384, "love", SERIF_IT, 70, "#C0320E", 11, max_w=200, shadow="#FFF4E0", soff=(0.02, 0.03)))
    c.append(vt(D, 384, 458, "TACOS!", ANTON, 74, "#5A1E0A", 12, max_w=250, ls=8, shadow="#FF8A2A", soff=(0.03, 0.04)))
    c.append(star(310, 366, 8, "#C0320E") + star(458, 366, 8, "#C0320E"))
    c.append(f'<path d="{blob(160, 420, 70, 40, 31, 0.1, 14)}" fill="#FFE680" opacity="0.9"/>')
    c.append(small(160, 428, "extra salsa", SERIF_IT, 30, "#C0320E", max_w=124))
    out.append(sticker(D, pts, face, "".join(c), rot_=2, peel=(-35, 26), seed=13))
    out.append(taco(D, 166, 322, 92, 14))
    for k, (dx, dy) in enumerate(((-104, -58), (-120, -22), (-92, -90))):
        out.append(taper([(166 + dx, 322 + dy), (166 + dx - 18, 322 + dy - 8)], 5, 1.5, "#FFFFFF", 0.9))
    return finish(D, out, 15, INK, 0.6)



def note(x, y, s, col, kind=1, op=1.0, rot_=0):
    """Music note: kind 1 = eighth, 2 = beamed pair."""
    out = [f'<g transform="rotate({rot_} {x} {y})" opacity="{op}">']
    if kind == 1:
        out.append(f'<ellipse cx="{x}" cy="{y}" rx="{s * 0.34:.1f}" ry="{s * 0.25:.1f}" transform="rotate(-25 {x} {y})" fill="{col}"/>')
        out.append(f'<path d="M {x + s * 0.3:.1f} {y - s * 0.05:.1f} L {x + s * 0.3:.1f} {y - s * 1.1:.1f} Q {x + s * 0.5:.1f} {y - s * 0.8:.1f} {x + s * 0.8:.1f} {y - s * 0.7:.1f}" stroke="{col}" stroke-width="{s * 0.12:.1f}" fill="none" stroke-linecap="round"/>')
    else:
        for dx in (0, s * 0.8):
            out.append(f'<ellipse cx="{x + dx:.1f}" cy="{y:.1f}" rx="{s * 0.3:.1f}" ry="{s * 0.22:.1f}" transform="rotate(-25 {x + dx:.1f} {y})" fill="{col}"/>')
            out.append(f'<path d="M {x + dx + s * 0.27:.1f} {y - s * 0.05:.1f} L {x + dx + s * 0.27:.1f} {y - s * 1.0:.1f}" stroke="{col}" stroke-width="{s * 0.11:.1f}"/>')
        out.append(f'<path d="M {x + s * 0.27:.1f} {y - s * 1.0:.1f} L {x + s * 1.07:.1f} {y - s * 1.12:.1f}" stroke="{col}" stroke-width="{s * 0.2:.1f}"/>')
    out.append("</g>")
    return "".join(out)


def kid_head(D, cx, cy, s, seed, hair="#4A2A1A", skin=("#F8D8B8", "#E8B48A", "#A8704A"), mouth=True, pig=False, bob=False):
    out = []
    if pig:
        for sg in (-1, 1):
            out.append(f'<path d="{blob(cx + sg * s * 0.95, cy - s * 0.1, s * 0.3, s * 0.42, seed + sg, 0.1, 10, sg * 20)}" fill="{hair}"/>')
    hd = blob_pts(cx, cy, s * 0.8, s * 0.86, seed, 0.03, 18)
    out.append(painted(D, hd, skin, seed, sdir=(0.4, 0.6), sk=0.15, n=6, inkw=1.8, hi=0.35))
    hair_pts = [(cx - s * 0.84, cy + (0.3 if bob else -0.05) * s), (cx - s * 0.8, cy - s * 0.6), (cx - s * 0.2, cy - s * 0.98), (cx + s * 0.5, cy - s * 0.86),
                (cx + s * 0.86, cy + (0.3 if bob else -0.15) * s), (cx + s * 0.5, cy - s * 0.45), (cx, cy - s * 0.5), (cx - s * 0.5, cy - s * 0.4)]
    out.append(painted(D, hair_pts, (mix(hair, "#FFFFFF", 0.3), hair, mix(hair, "#000000", 0.4)), seed + 1, sk=0.15, n=8, inkw=1.6, hi=0.3))
    for sg in (-1, 1):
        out.append(f'<path d="M {cx + sg * s * 0.32 - s * 0.1:.1f} {cy - s * 0.02:.1f} q {s * 0.1:.1f} {-s * 0.1:.1f} {s * 0.2:.1f} 0" stroke="{INK}" stroke-width="{max(1.6, s * 0.07):.1f}" fill="none" stroke-linecap="round"/>')
        out.append(f'<circle cx="{cx + sg * s * 0.5:.1f}" cy="{cy + s * 0.2:.1f}" r="{s * 0.12:.1f}" fill="#F48A8A" opacity="0.5"/>')
    if mouth:
        out.append(f'<path d="{blob(cx, cy + s * 0.38, s * 0.18, s * 0.2, seed + 2, 0.05, 10)}" fill="#8A2A2A"/>')
    return "".join(out)


def pretzel(D, cx, cy, s, seed, rot_=0):
    pal = ("#E8A060", "#B8642A", "#6A3410")
    path = [(-0.1, 0.55), (-0.55, 0.3), (-0.75, -0.2), (-0.5, -0.6), (-0.1, -0.55), (0.15, -0.1), (0.4, 0.5),
            (0.35, 0.55), (-0.4, 0.5), (-0.15, -0.1), (0.1, -0.55), (0.5, -0.6), (0.75, -0.2), (0.55, 0.3), (0.1, 0.55)]
    pts = rot([(cx + x * s, cy + y * s) for x, y in path], cx, cy, rot_)
    sm = catmull(pts, 6)
    out = [taper(sm, s * 0.26, s * 0.26, pal[2]), taper(sm, s * 0.2, s * 0.2, pal[1]), taper([(x - 1.5, y - 2) for x, y in sm], s * 0.07, s * 0.07, pal[0], 0.8)]
    rnd = random.Random(seed)
    for i in range(0, len(sm), 3):
        x, y = sm[i]
        out.append(f'<rect x="{x + rnd.uniform(-4, 4):.1f}" y="{y + rnd.uniform(-4, 4):.1f}" width="3" height="3" fill="#FFFFFF" opacity="0.9" transform="rotate({rnd.uniform(0, 90):.0f} {x:.1f} {y:.1f})"/>')
    return "".join(out)


def cookie(D, cx, cy, r, seed):
    out = [painted(D, blob_pts(cx, cy, r, r * 0.96, seed, 0.06, 20), ("#F2C88A", "#D8A060", "#9A6A30"), seed, sdir=(0.5, 0.7), sk=0.18, n=14, inkw=2, hi=0.4)]
    rnd = random.Random(seed)
    for i in range(7):
        a, d = rnd.uniform(0, 6.28), rnd.uniform(0.1, 0.7) * r
        out.append(f'<path d="{blob(cx + d * math.cos(a), cy + d * math.sin(a), r * 0.12, r * 0.1, seed + i, 0.15, 8)}" fill="#4A2A14"/>')
    return "".join(out)


def dog_head(D, cx, cy, s, seed, fur=("#F8D49A", "#E0A85A", "#9A6420"), ear=("#D8A060", "#B07032", "#6A3A12")):
    """Happy golden dog face, front view, tongue out."""
    out = []
    for sg in (-1, 1):
        ep = [(cx + sg * s * 0.55, cy - s * 0.62), (cx + sg * s * 0.98, cy - s * 0.5), (cx + sg * s * 1.08, cy + s * 0.1), (cx + sg * s * 0.92, cy + s * 0.5),
              (cx + sg * s * 0.7, cy + s * 0.36), (cx + sg * s * 0.58, cy - s * 0.1)]
        out.append(painted(D, ep, ear, seed + sg, sdir=(0, 1), sk=0.2, angle=-90, n=14, inkw=2.2, hi=0.35))
    hd = blob_pts(cx, cy - s * 0.05, s * 0.72, s * 0.78, seed, 0.03, 22)
    out.append(painted(D, hd, fur, seed, sdir=(0.3, 0.8), sk=0.15, angle=-90, n=30, inkw=2.4, hi=0.4))
    mz = blob_pts(cx, cy + s * 0.36, s * 0.42, s * 0.3, seed + 3, 0.04, 16)
    out.append(painted(D, mz, ("#FFF4E0", "#F8E2C0", "#C8A880"), seed + 3, sk=0.15, n=8, inkw=1.6, hi=0.3))
    # tongue
    tp = [(cx - s * 0.12, cy + s * 0.5), (cx + s * 0.12, cy + s * 0.5), (cx + s * 0.14, cy + s * 0.78), (cx, cy + s * 0.88), (cx - s * 0.14, cy + s * 0.78)]
    out.append(painted(D, tp, ("#FFA0B0", "#F26A80", "#A83048"), seed + 4, sk=0.2, n=4, inkw=1.8, hi=0.4))
    out.append(pline([(cx, cy + s * 0.55), (cx, cy + s * 0.75)], "#A83048", 1.6, seed, 0.7, 1))
    out.append(pline([(cx - s * 0.3, cy + s * 0.44), (cx - s * 0.12, cy + s * 0.52), (cx, cy + s * 0.42), (cx + s * 0.12, cy + s * 0.52), (cx + s * 0.3, cy + s * 0.44)], INK, max(2, s * 0.05), seed, 0.9, 1))
    out.append(f'<path d="{blob(cx, cy + s * 0.24, s * 0.16, s * 0.11, seed + 5, 0.05, 10)}" fill="#2A1A14"/><ellipse cx="{cx - s * 0.05:.1f}" cy="{cy + s * 0.2:.1f}" rx="{s * 0.05:.1f}" ry="{s * 0.025:.1f}" fill="#FFFFFF" opacity="0.7"/>')
    for sg in (-1, 1):
        ex, ey = cx + sg * s * 0.28, cy - s * 0.1
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{s * 0.09:.1f}" fill="#2A1A14"/><circle cx="{ex - s * 0.03:.1f}" cy="{ey - s * 0.03:.1f}" r="{s * 0.03:.1f}" fill="#FFFFFF"/>')
        out.append(f'<path d="M {ex - s * 0.1:.1f} {ey - s * 0.2:.1f} q {s * 0.1:.1f} {-s * 0.06:.1f} {s * 0.2:.1f} 0" stroke="{fur[2]}" stroke-width="2" fill="none"/>')
    out.append(taper([(cx - s * 0.4, cy - s * 0.5), (cx - s * 0.15, cy - s * 0.68)], s * 0.08, 2, "#FFF4D8", 0.6))
    return "".join(out)


def house(D, x, base, w, h, seed, wall=("#FFF4E0", "#E8D8B8", "#A8946A"), roof=("#8AA0C0", "#4A6280", "#22344A"), door="#2AA59A"):
    out = [painted(D, poly([(x, base - h), (x + w, base - h), (x + w, base), (x, base)], 16), wall, seed, sdir=(1, 0.2), sk=0.1, angle=0, n=20, inkw=2, hi=0.3)]
    out.append(painted(D, poly([(x - 18, base - h + 4), (x + w / 2, base - h - h * 0.55), (x + w + 18, base - h + 4)], 16), roof, seed + 1, sdir=(0.3, 1), sk=0.15, angle=-30, n=20, inkw=2, hi=0.3))
    for i, wx in enumerate((x + w * 0.12, x + w * 0.62)):
        wp = poly([(wx, base - h * 0.75), (wx + w * 0.24, base - h * 0.75), (wx + w * 0.24, base - h * 0.42), (wx, base - h * 0.42)], 8)
        out.append(glass(D, smooth_closed(wp), bbox(wp), seed, top="#CFEFFF", bot="#6A9AB8") + ink(smooth_closed(wp), INK, 1.6, seed + i, 1, 0.8))
        out.append(f'<rect x="{wx - 4:.1f}" y="{base - h * 0.42:.1f}" width="{w * 0.24 + 8:.1f}" height="5" fill="#FFFFFF"/>')
    out.append(painted(D, poly([(x + w * 0.42, base - h * 0.55), (x + w * 0.58, base - h * 0.55), (x + w * 0.58, base), (x + w * 0.42, base)], 8), (mix(door, "#FFFFFF", 0.3), door, mix(door, "#000000", 0.4)), seed + 3, sk=0.15, n=6, inkw=1.6, hi=0.3))
    return "".join(out)


def table_lamp(D, cx, base, s, seed):
    out = [painted(D, oval(cx, base - s * 0.5, s * 0.22, s * 0.3, 20), ("#9AE0D8", "#2AA59A", "#0E5E58"), seed, sk=0.2, n=6, inkw=1.8, hi=0.4)]
    out.append(pline([(cx, base - s * 0.8), (cx, base - s * 1.0)], "#C8A040", 3, seed, 1, 1))
    out.append(painted(D, poly([(cx - s * 0.22, base - s * 1.42), (cx + s * 0.22, base - s * 1.42), (cx + s * 0.4, base - s * 0.98), (cx - s * 0.4, base - s * 0.98)], 8),
                       ("#FFF0D0", "#F2D8A0", "#B89858"), seed + 1, sk=0.15, n=6, inkw=1.8, hi=0.4))
    out.append(painted(D, poly([(cx - s * 0.2, base - s * 0.2), (cx + s * 0.2, base - s * 0.2), (cx + s * 0.24, base), (cx - s * 0.24, base)], 6), ("#9AE0D8", "#2AA59A", "#0E5E58"), seed + 2, sk=0.2, n=3, inkw=1.6, hi=0.3))
    return "".join(out)


# ================================================================ 14. CAUTION: KIDS SINGING — hazard-striped decal under a window full of singers
@design("caution-kids-singing")
def caution_kids_singing():
    D = Doc("cks")
    out = []
    body = "M -10 -10 L 610 -10 L 610 610 L -10 610 Z"
    out.append(car_paint(D, body, (0, 0, 600, 600), ("#E8667A", "#C83A52", "#6E1428"), 3, sky_band=(0.3, 0.36)))
    win = smooth_closed(rrect(48, -40, 552, 186, 46))
    out.append(glass(D, win, (48, -40, 552, 186), 4, top="#BFE6F8", bot="#5A88A8", refl=False))
    cid = D.clip(f'<path d="{win}"/>')
    kids = [kid_head(D, 150, 150, 46, 5, hair="#3A2214", pig=True), kid_head(D, 300, 140, 52, 6, hair="#E8B060"), kid_head(D, 450, 152, 44, 7, hair="#6A3A1A", bob=True)]
    for x in (150, 300, 450):
        kids.append(f'<path d="{blob(x, 214, 60, 30, x, 0.05, 12)}" fill="{["#FFC93C", "#2AA59A", "#8A5AD0"][(x // 150) - 1]}"/>')
    kids.append(f'<polygon points="{P([(48 + 60, -40), (48 + 140, -40), (48 + 70, 186), (48 - 10, 186)])}" fill="#FFFFFF" opacity="0.2"/>')
    out.append(f'<g {cid}>{"".join(kids)}</g>')
    out.append(ink(win, "#2A1A20", 3, 8, 1, 0.8))
    for i, (x, y, k, r_) in enumerate(((96, 46, 1, -10), (220, 34, 2, 8), (380, 40, 1, 12), (512, 60, 2, -6), (250, 80, 1, -4))):
        out.append(note(x, y, 30, "#FFFFFF", k, 0.95, r_))
    out.append(tail_light(D, 18, 300, 30, 9, ring=False) + tail_light(D, 582, 300, 30, 10, ring=False))
    out.append(asphalt(D, 556, 11))
    out.append(chrome_bar(D, -40, 490, 640, 560, 12, r=20, horizon=0.45))
    # caution sticker with hazard-striped ends
    pts = rrect(54, 232, 546, 462, 20)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#FFEA80", "#FFD21A", "#C8960A"), 13)
    for x0 in (40, 474):
        band = smooth_closed(poly([(x0, 220), (x0 + 86, 220), (x0 + 86, 480), (x0, 480)], 20))
        face += stripes_in(D, band, (x0, 220, x0 + 86, 480), 35, [22, 22], ["#1E1A22", None], 14)
    c = [f'<path d="M 126 232 L 126 462 M 474 232 L 474 462" stroke="#1E1A22" stroke-width="4"/>']
    c.append(vt(D, 300, 318, "CAUTION", ANTON, 86, "#1E1A22", 15, max_w=320, ls=10))
    c.append(hbar(D, 150, 450, 334, 5, "#1E1A22", 16))
    c.append(vt(D, 300, 398, "KIDS SINGING", BEBAS, 62, "#C83A52", 17, max_w=320, ls=4, shadow="#1E1A22", soff=(0.025, 0.035)))
    c.append(note(196, 440, 22, "#1E1A22", 1, 1, -8) + note(388, 440, 22, "#1E1A22", 2, 1, 6))
    c.append(small(300, 444, "at full volume", SERIF_IT, 26, "#1E1A22", max_w=150))
    out.append(sticker(D, pts, face, "".join(c), rot_=-1.5, peel=(-150, 24), seed=18))
    return finish(D, out, 19, INK, 0.6)


# ================================================================ 15. POWERED BY SNACKS — ticket decal on a retro tin lunchbox
@design("powered-by-snacks")
def powered_by_snacks():
    D = Doc("pbs")
    out = [f'<rect width="600" height="600" fill="#F2E6CC"/>']
    # gingham tablecloth
    out.append(stripes_in(D, "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (0, 0, 600, 600), 0, [30, 30], ["#E8505A", None], 3, 0.0))
    for k in range(0, 620, 60):
        out.append(f'<rect x="{k}" y="0" width="30" height="600" fill="#E8505A" opacity="0.45"/><rect x="0" y="{k}" width="600" height="30" fill="#E8505A" opacity="0.45"/>')
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, 0, 600, 600), ["#FFFFFF", "#B83040"], 4, n=160, angle=0, length=(30, 90), width=(2, 5), opacity=(0.06, 0.18)))
    # lunchbox: handle, lid seam, latch
    out.append(cast(D, 312, 552, 290, 30, strength=0.45))
    out.append(pline([(220, 118), (230, 70), (370, 70), (380, 118)], "#2A2430", 16, 5, 1, 1) + pline([(222, 114), (232, 74), (368, 74), (378, 114)], "#6A6474", 6, 6, 0.8, 1))
    box = rrect(40, 112, 560, 540, 30)
    out.append(painted(D, box, ("#7AB8F0", "#2E6AC0", "#14347A"), 7, sdir=(0.4, 1), sk=0.08, angle=0, n=60, inkw=2.6, hi=0.35))
    out.append(taper([(52, 176), (548, 176)], 6, 6, "#14347A", 0.6) + taper([(52, 172), (548, 172)], 2, 2, "#FFFFFF", 0.5))
    out.append(painted(D, rrect(270, 150, 330, 198, 8), CHROME, 8, sk=0.2, n=6, inkw=2, hi=0.6))
    for x, y in ((64, 140), (536, 140), (64, 516), (536, 516)):
        out.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#C8D2DA" stroke="{INK}" stroke-width="1.4"/>')
    # other stickers already on the box
    out.append(sticker(D, oval(104, 500, 42, 26, 30), f'<rect x="40" y="460" width="130" height="80" fill="#FFC93C"/>', star(104, 500, 14, "#E8423A"), rot_=-12, margin=5, seed=9, wear=0.5, gloss=0.1, shadow=(2, 3, 0.25)))
    hp = [(510 + 16 * math.sin(2 * math.pi * i / 40) ** 3, 228 - (13 * math.cos(2 * math.pi * i / 40) - 5 * math.cos(4 * math.pi * i / 40) - 2 * math.cos(6 * math.pi * i / 40) - math.cos(8 * math.pi * i / 40))) for i in range(40)]
    hp = [(510 + (x - 510) * 1.6, 228 + (y - 228) * 1.6) for x, y in hp]
    out.append(sticker(D, hp, f'<rect x="470" y="190" width="80" height="80" fill="#FF5FA2"/>', "", rot_=14, margin=5, seed=10, wear=0.5, gloss=0.1, shadow=(2, 3, 0.25)))
    # notched ticket sticker
    x0, y0, x1, y1, nr = 64, 226, 536, 470, 26
    pts = []
    for (cx_, cy_, a0) in ((x0, y0, 0), (x1, y0, 90), (x1, y1, 180), (x0, y1, 270)):
        pts += [(cx_ + nr * math.cos(math.radians(a0 + k * 10)), cy_ + nr * math.sin(math.radians(a0 + k * 10))) for k in range(10)]
    pts2 = []
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        pts2.append(a)
        if i % 10 == 9:
            n = int(math.dist(a, b) / 14)
            pts2 += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(1, n)]
    pts = pts2
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#FFE0A0", "#FF8A2A", "#B8520E"), 11)
    c = [f'<path d="M 144 230 L 144 466" stroke="#FFF4E0" stroke-width="3" stroke-dasharray="6 7"/>']
    c.append(pretzel(D, 104, 300, 34, 12, -14) + cookie(D, 104, 398, 30, 13))
    c.append(vt(D, 340, 304, "POWERED BY", JOS, 46, "#FFF4E0", 14, max_w=330, ls=8))
    c.append(vt(D, 340, 422, "SNACKS", ANTON, 124, "#3A1A0A", 15, max_w=340, ls=8, outline="#FFF4E0", ow=0.05, shadow="#B8520E", soff=(0.035, 0.045)))
    c.append(bolt(500, 300, 18, "#FFF4E0", 1, 12) + bolt(180, 300, 18, "#FFF4E0", 1, -12))
    out.append(sticker(D, pts, face, "".join(c), rot_=-2.5, peel=(-30, 24), seed=16))
    for i, (x, y) in enumerate(((560, 590), (30, 590), (590, 40))):
        out.append(f'<path d="{blob(x, y, 7, 5, i, 0.3, 8)}" fill="#D8A060"/>')
    return finish(D, out, 17, INK, 0.6)


# ================================================================ 16. DOG ON BOARD — diamond window sign with a suction cup
@design("dog-on-board")
def dog_on_board():
    D = Doc("dob")
    out = []
    win = "M -10 -10 L 610 -10 L 610 610 L -10 610 Z"
    out.append(glass(D, win, (0, 0, 600, 600), 3, top="#7A9AB0", bot="#22303E", refl=False))
    # reflection of trees and sky in the rear window
    out.append(f'<path d="M -10 -10 L 610 -10 L 610 180 Q 300 240 -10 170 Z" fill="#CFEAF8" opacity="0.35"/>')
    rnd = random.Random(4)
    for i in range(10):
        x = rnd.uniform(0, 600)
        out.append(f'<path d="{blob(x, 190 + rnd.uniform(-20, 20), rnd.uniform(40, 80), rnd.uniform(30, 50), i, 0.2, 14)}" fill="#3E5A50" opacity="0.4"/>')
    # nose smudges and paw prints left on the inside of the glass
    for i, (px, py, rr) in enumerate(((488, 470, 0.9), (530, 520, 0.8), (76, 500, 0.75))):
        out.append(f'<g opacity="0.22" fill="#FFFFFF">' + f'<path d="{blob(px, py, 13 * rr, 11 * rr, i, 0.1, 10)}"/>'
                   + "".join(f'<path d="{blob(px + dx * rr, py + dy * rr, 5 * rr, 6 * rr, i * 7 + k, 0.1, 8)}"/>' for k, (dx, dy) in enumerate(((-14, -14), (-5, -21), (5, -21), (14, -14)))) + "</g>")
    out.append(f'<path d="{blob(520, 410, 34, 16, 6, 0.3, 12)}" fill="#FFFFFF" opacity="0.14"/>')
    out.append(f'<polygon points="{P([(80, -10), (200, -10), (40, 610), (-80, 610)])}" fill="#FFFFFF" opacity="0.12"/>')
    out.append(f'<polygon points="{P([(230, -10), (260, -10), (100, 610), (70, 610)])}" fill="#FFFFFF" opacity="0.1"/>')
    # rubber seal + painted body at the bottom
    out.append(painted(D, poly([(-10, 552), (610, 552), (610, 610), (-10, 610)], 30), ("#FFE08A", "#F2B430", "#B07A12"), 7, sdir=(0, 1), sk=0.15, angle=0, n=20, inkw=0, hi=0.4))
    out.append(taper([(-10, 548), (610, 548)], 12, 12, "#1A1A1E"))
    # suction cup & string
    out.append(pline([(300, 56), (300, 92)], "#E8E0D0", 2.4, 8, 1, 1))
    out.append(f'<path d="{blob(300, 46, 22, 16, 9, 0.05, 14)}" fill="#E8F4FF" opacity="0.55" stroke="#FFFFFF" stroke-width="2"/>')
    out.append(f'<circle cx="300" cy="46" r="6" fill="#FFFFFF" opacity="0.7"/>')
    # diamond sign
    cx, cy, R = 300, 316, 222
    corners = [(cx, cy - R), (cx + R, cy), (cx, cy + R), (cx - R, cy)]
    pts = []
    for k in range(4):
        a, b, c_ = corners[k - 1], corners[k], corners[(k + 1) % 4]
        rr = 26
        def towards(p, q, t):
            L = math.dist(p, q)
            return (p[0] + (q[0] - p[0]) * t / L, p[1] + (q[1] - p[1]) * t / L)
        p0, p1 = towards(b, a, rr * 1.4), towards(b, c_, rr * 1.4)
        for i in range(7):
            t = i / 6
            pts.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * b[0] + t * t * p1[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * b[1] + t * t * p1[1]))
        q0 = p1
        q1 = towards(c_, b, rr * 1.4)
        n = int(math.dist(q0, q1) / 14)
        pts += [(q0[0] + (q1[0] - q0[0]) * j / n, q0[1] + (q1[1] - q0[1]) * j / n) for j in range(1, n)]
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#FFEA80", "#FFD21A", "#C8960A"), 10)
    inner = [(cx, cy - R + 22), (cx + R - 22, cy), (cx, cy + R - 22), (cx - R + 22, cy)]
    c = [f'<path d="{smooth_closed(poly(inner, 14))}" fill="none" stroke="#1E1A22" stroke-width="5" stroke-linejoin="round"/>']
    c.append(f'<path d="{blob(300, 196, 70, 62, 11, 0.05, 16)}" fill="#FFE680"/>')
    c.append(dog_head(D, 300, 190, 56, 12))
    c.append(vt(D, 300, 352, "DOG", ANTON, 112, "#1E1A22", 13, max_w=250, ls=12))
    c.append(vt(D, 300, 406, "ON BOARD", BEBAS, 50, "#1E1A22", 14, max_w=196, ls=5))
    c.append(small(300, 442, "woof!", SERIF_IT, 26, "#C0320E", max_w=100))
    out.append(sticker(D, pts, face, "".join(c), rot_=4, margin=0, vinyl="#FFD21A", shadow=(6, 10, 0.4), seed=15, wear=0.8, edge_ink="#5A3A0A"))
    return finish(D, out, 16, INK, 0.5)


# ================================================================ 17. THIS CAR STOPS AT ALL YARD SALES — parked by a yard sale
@design("this-car-stops-at-all-yard-sales")
def this_car_stops_at_all_yard_sales():
    D = Doc("tcs")
    out = [sky(D, [(0, "#8ED8F8"), (1, "#E8F8FF")], 3, 200, ["#FFFFFF", "#B8E8FA"], 20)]
    out.append(puff_cloud(D, 120, 54, 150, 4, op=0.95))
    # shade tree, cottage with a porch, bunting strung between them
    out.append(pline([(520, 196), (516, 120)], "#5A3A20", 12, 4, 1, 1))
    out.append(dab_crown(D, 520, 92, 78, 62, [("#9ACB6A", "#5E9A40", "#2E6A2A")], 5, n=90, size=(7, 12), inkw=1.2))
    out.append(house(D, 150, 196, 240, 108, 7, wall=("#FFF0E0", "#F6D8C0", "#B88A6A"), roof=("#6A8AB8", "#3A5A88", "#1A2E50"), door="#E8423A"))
    for x in (176, 304):
        out.append(painted(D, poly([(x, 190), (x + 60, 190), (x + 56, 200), (x + 4, 200)], 8), WOOD, x, sk=0.2, n=3, inkw=1.4, hi=0.3))
        for k in range(4):
            out.append(f'<circle cx="{x + 10 + k * 13}" cy="186" r="5" fill="{["#F27A9A", "#FFC93C", "#FFFFFF", "#F27A9A"][k]}"/>')
    flags = [(170, 112), (260, 130), (350, 138), (440, 128), (500, 112)]
    out.append(pline(flags, "#5A4A3A", 1.6, 5, 0.9, 1))
    sm = catmull(flags, 6)
    for i in range(1, len(sm) - 1, 3):
        x, y = sm[i]
        out.append(f'<path d="{lpath([(x - 9, y), (x + 9, y + 1), (x, y + 20)])}" fill="{["#E8423A", "#FFC93C", "#2AA59A", "#7A5AD0"][i % 4]}" stroke="#3A2A1A" stroke-width="1" stroke-opacity="0.5"/>')
    out.append(hill(D, [(-20, 196), (300, 192), (620, 198)], 600, ("#9AD06A", "#6AAE48", "#3E7A2E"), 8, inkw=0))
    out.append(grass(9, (0, 200, 600, 236), ["#4E8A36", "#7AB04A", "#A8D070"], 120, (5, 10)))
    # the sale: table with lamp, books and a vase; a rocking chair; a box of odds and ends; the sign
    out.append(painted(D, poly([(286, 196), (440, 196), (440, 206), (286, 206)], 12), ("#FFFFFF", "#F2EEE6", "#B8B0A6"), 9, sk=0.15, n=6, inkw=1.6, hi=0.3))
    out.append(pline([(296, 206), (292, 236)], INK, 3, 10, 0.9, 1) + pline([(430, 206), (434, 236)], INK, 3, 11, 0.9, 1))
    out.append(table_lamp(D, 312, 196, 42, 12))
    for i, (x, w_, col) in enumerate(((350, 12, "#E8423A"), (362, 11, "#2AA59A"), (373, 13, "#F2B430"))):
        out.append(painted(D, poly([(x, 196 - 28 + i * 3), (x + w_, 196 - 28 + i * 3), (x + w_, 196), (x, 196)], 6), (mix(col, "#FFFFFF", 0.3), col, mix(col, "#000000", 0.3)), 13 + i, sk=0.15, n=3, inkw=1.2, hi=0.3))
    out.append(painted(D, blob_pts(414, 184, 11, 13, 16, 0.05, 12), ("#FFC0D0", "#F48AA0", "#B04A66"), 16, sk=0.2, n=4, inkw=1.4, hi=0.4))
    out.append(daisy(D, 410, 162, 8, 17, n=8) + daisy(D, 422, 168, 7, 18, n=8))
    # a teddy bear for sale, sitting on the grass
    out.append(painted(D, blob_pts(96, 218, 20, 18, 19, 0.05, 14), ("#E8B47A", "#C0864A", "#7A4E26"), 19, sk=0.2, n=4, inkw=1.6, hi=0.4))
    out.append(painted(D, blob_pts(96, 186, 16, 15, 20, 0.04, 14), ("#E8B47A", "#C0864A", "#7A4E26"), 20, sk=0.2, n=4, inkw=1.6, hi=0.4))
    for sg in (-1, 1):
        out.append(f'<circle cx="{96 + sg * 12}" cy="174" r="6" fill="#C0864A" stroke="#7A4E26" stroke-width="1.4"/>')
    out.append(f'<circle cx="91" cy="184" r="2" fill="{INK}"/><circle cx="101" cy="184" r="2" fill="{INK}"/><path d="{blob(96, 192, 5, 4, 21, 0.1, 8)}" fill="#F2D8B0"/>')
    out.append(f'<path d="M 86 202 L 106 202 L 96 210 Z" fill="#E8423A"/>')
    out.append(painted(D, poly([(446, 210), (500, 210), (504, 238), (442, 238)], 8), ("#E8C08A", "#C8944E", "#7A5428"), 22, sk=0.15, n=4, inkw=1.6, hi=0.3))
    out.append(pline([(560, 240), (560, 170)], WOOD[2], 4, 23, 1, 1))
    sp = poly([(512, 132), (596, 132), (596, 178), (512, 178)], 10)
    out.append(painted(D, sp, ("#FFFFFF", "#FFF4E0", "#C8B490"), 24, sk=0.1, n=6, inkw=2, hi=0.3))
    out.append(small(554, 152, "YARD", BEBAS, 20, "#E8423A", max_w=80, ls=2) + small(554, 172, "SALE", BEBAS, 20, "#E8423A", max_w=80, ls=2))
    # the car: sage-green trunk with chrome bumper (seen from behind at the curb)
    car = smooth_closed([(-20, 284), (40, 238), (140, 224), (460, 224), (560, 238), (620, 284), (620, 620), (-20, 620)])
    out.append(car_paint(D, car, (0, 224, 600, 600), ("#C8DCB8", "#8EAE88", "#4A6A4A"), 21, sky_band=(0.04, 0.14)))
    out.append(taper([(-20, 286), (40, 240), (140, 226), (460, 226), (560, 240), (620, 286)], 4, 4, "#FFFFFF", 0.6))
    out.append(painted(D, oval(300, 300, 30, 18, 24), CHROME, 25, sk=0.25, n=4, inkw=1.8, hi=0.6))
    out.append(tail_light(D, 46, 304, 24, 22) + tail_light(D, 554, 304, 24, 23))
    out.append(asphalt(D, 548, 24))
    out.append(chrome_bar(D, -40, 352, 640, 548, 25, r=40, horizon=0.38))
    # long, classic 3:1 bumper sticker
    pts = rrect(60, 372, 540, 526, 12)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#4A9A6A", "#1F6E46", "#0E3E26"), 26)
    c = [hbar(D, 60, 540, 372, 10, "#F2C230", 27), hbar(D, 60, 540, 516, 10, "#F2C230", 28)]
    c.append(vt(D, 300, 440, "THIS CAR STOPS", ANTON, 66, "#FFF4E0", 29, max_w=440, ls=4, shadow="#0E3E26", soff=(0.03, 0.04)))
    c.append(vt(D, 300, 498, "AT ALL YARD SALES", BEBAS, 52, "#F2C230", 30, max_w=420, ls=6))
    c.append(star(84, 462, 8, "#F2C230") + star(516, 462, 8, "#F2C230"))
    out.append(sticker(D, pts, face, "".join(c), rot_=1.5, peel=(-160, 22), seed=31))
    return finish(D, out, 32, INK, 0.6)


# ================================================================ 18. ROAD TRIP READY — on the back of a two-tone camper van at a pine campsite
@design("road-trip-ready")
def road_trip_ready():
    from summer_gouache import pine_sil
    D = Doc("rtr")
    out = [sky(D, [(0, "#3A4A8A"), (0.5, "#C86A8A"), (1, "#FFB070")], 3, 260, ["#FFB0A0", "#7A6AA8"], 30)]
    for i, x in enumerate(range(-20, 640, 34)):
        h = 150 + (i * 37 % 60)
        out.append(pine_sil(x, 270, h, "#2A2A48", i))
    for i, x in enumerate(range(0, 640, 52)):
        h = 110 + (i * 23 % 40)
        out.append(pine_sil(x + 14, 280, h, "#1E1E36", 50 + i))
    # van rear: orange lower, cream upper, rounded roof, two rear windows, ladder, roof bags
    van = smooth_closed([(-20, 160), (40, 110), (120, 92), (480, 92), (560, 110), (620, 160), (620, 620), (-20, 620)])
    out.append(car_paint(D, van, (0, 92, 600, 600), CREAM, 4, sky_band=(0.03, 0.08)))
    out.append(painted(D, poly([(-20, 300), (620, 300), (620, 620), (-20, 620)], 30), ORANGE, 5, sdir=(0, 1), sk=0.08, angle=0, n=60, inkw=2.2, hi=0.3))
    out.append(taper([(-20, 300), (620, 300)], 8, 8, "#FFFFFF", 0.7))
    for x0 in (66, 330):
        wp = rrect(x0, 132, x0 + 204, 230, 22)
        out.append(painted(D, rrect(x0 - 8, 124, x0 + 212, 238, 28), BLACK, 6, sk=0.2, n=6, inkw=2, hi=0.3))
        out.append(glass(D, smooth_closed(wp), (x0, 132, x0 + 204, 230), 7, top="#FFC0A0", bot="#5A4A7A"))
    out.append(painted(D, poly([(150, 60), (450, 60), (470, 96), (130, 96)], 14), ("#5AA0D0", "#2A6A9A", "#123A5A"), 8, sk=0.15, n=10, inkw=2, hi=0.3))
    out.append(painted(D, poly([(180, 30), (300, 30), (310, 62), (170, 62)], 12), ("#E8C870", "#C09A3A", "#7A5A1A"), 9, sk=0.15, n=8, inkw=2, hi=0.3))
    for y in range(110, 560, 46):
        out.append(taper([(556, y), (596, y)], 5, 5, "#C8D2DA"))
    out.append(pline([(556, 96), (556, 560)], "#8A949E", 6, 10, 1, 1) + pline([(596, 96), (596, 560)], "#8A949E", 6, 11, 1, 1))
    out.append(tail_light(D, 30, 470, 22, 12) + tail_light(D, 30, 410, 14, 13, lens=("#FFE0A0", "#F2A030", "#9A5A0A")))
    out.append(asphalt(D, 566, 14, base="#3A3448"))
    out.append(chrome_bar(D, -40, 522, 640, 572, 15, sky_c="#E8A8A0", ground="#3A2A30", r=14, horizon=0.45))
    # pennant sticker
    pts = poly([(58, 268), (424, 268), (534, 372), (424, 476), (58, 476)], 12)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#4A6AB0", "#22408A", "#0E1E4E"), 16)
    face += f'<rect x="40" y="250" width="90" height="240" fill="#F2C230"/>' + "".join(f'<rect x="40" y="{250 + k * 30}" width="90" height="15" fill="#E8792E"/>' for k in range(8))
    c = [f'<path d="M 130 268 L 130 476" stroke="#0E1E4E" stroke-width="4"/>']
    # little sunset-mountain emblem on the pennant band
    em = [sun_disc(D, 86, 352, 22, ("#FFFCE0", "#FFE87A", "#FFB43A"), 17, glow_r=0.01, strokes_n=6)]
    c += em
    c.append(f'<path d="M 52 400 L 76 368 L 90 384 L 104 362 L 128 400 Z" fill="#0E1E4E"/>')
    c.append(vt(D, 290, 360, "ROAD TRIP", ANTON, 88, "#FFF4E0", 18, max_w=300, ls=4, shadow="#0E1E4E", soff=(0.03, 0.04)))
    c.append(vt(D, 286, 436, "ready!", SERIF_IT, 70, "#F2C230", 19, max_w=220, shadow="#0E1E4E", soff=(0.02, 0.035), rotate=-5))
    c.append(star(446, 336, 8, "#F2C230") + star(464, 372, 6, "#F2C230") + star(446, 408, 8, "#F2C230"))
    out.append(sticker(D, pts, face, "".join(c), rot_=-3, seed=20))
    return finish(D, out, 21, INK, 0.6)


# ================================================================ new-format helpers
def emboss(x, y, s, font, size, fill, max_w, ls=0, depth=1.0, hi="#FFFFFF", lo="#0A1428", anchor="middle"):
    """Stamped (embossed) plate lettering: soft drop below-right, a bright lip above-left, then the paint."""
    fs = fit_size(s, font, size, max_w, ls)
    xx = x + ls / 2 if (ls and anchor == "middle") else x
    lsa = f' letter-spacing="{ls}"' if ls else ""
    t = lambda dx, dy, col, op, extra="": (f'<text x="{xx + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}" {font} font-size="{fs}"{lsa} '
                                           f'fill="{col}" opacity="{op}"{extra}>{esc(s)}</text>')
    k = fs / 100 * depth
    return (t(4 * k, 5 * k, lo, 0.28) + t(2.2 * k, 2.8 * k, lo, 0.35) + t(-1.6 * k, -1.8 * k, hi, 0.9)
            + t(0, 0, fill, 1) + t(-0.6 * k, -0.8 * k, hi, 0.12))


def screw(D, cx, cy, r, seed, head=CHROME):
    out = [f'<circle cx="{cx + 1.5:.1f}" cy="{cy + 2:.1f}" r="{r + 1:.1f}" fill="#1A1008" opacity="0.35"/>',
           f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{D.lin([(0, head[0]), (0.55, head[1]), (1, head[2])], 0, 0, 1, 1)}"/>',
           ink(smooth_closed(oval(cx, cy, r, r, 18)), "#2A2A30", 1.4, seed, 1, 0.7)]
    a = random.Random(seed).uniform(0, 180)
    c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
    out.append(f'<path d="M {cx - c * r * 0.7:.1f} {cy - s_ * r * 0.7:.1f} L {cx + c * r * 0.7:.1f} {cy + s_ * r * 0.7:.1f}" stroke="#3A3A44" stroke-width="{max(1.6, r * 0.22):.1f}" stroke-linecap="round"/>')
    out.append(f'<circle cx="{cx - r * 0.35:.1f}" cy="{cy - r * 0.4:.1f}" r="{r * 0.22:.1f}" fill="#FFFFFF" opacity="0.8"/>')
    return "".join(out)


def rust(D, pts_box, seed, n=10, col=("#C8742A", "#8A3E12", "#5A2408"), r=(2, 7), op=(0.35, 0.8), corners=None):
    """Little rust blooms and drips near given anchor points."""
    rnd = random.Random(seed)
    out = []
    for (x, y) in (corners or []):
        for _ in range(n):
            rr = rnd.uniform(*r)
            px, py = x + rnd.uniform(-14, 14), y + rnd.uniform(-10, 10)
            out.append(f'<path d="{blob(px, py, rr, rr * rnd.uniform(0.5, 0.9), rnd.randint(0, 9999), 0.3, 9)}" fill="{rnd.choice(col)}" opacity="{rnd.uniform(*op):.2f}"/>')
        out.append(taper([(x, y), (x + rnd.uniform(-2, 2), y + rnd.uniform(18, 34))], 3.5, 0.6, col[1], 0.45))
    return "".join(out)


def suitcase_luggage(D, seed):
    """A packed rear window: suitcases, a striped beach ball and a pillow pressed against the glass."""
    out = []
    out.append(painted(D, rrect(40, 40, 230, 150, 14), ("#E8A878", "#C0703A", "#6E3A18"), seed, sdir=(0.3, 1), sk=0.15, angle=0, n=30, inkw=2, hi=0.35))
    out.append(pline([(40, 70), (230, 70)], "#6E3A18", 2.4, seed, 0.7, 1) + pline([(40, 120), (230, 120)], "#6E3A18", 2.4, seed + 1, 0.7, 1))
    out.append(painted(D, rrect(118, 26, 152, 44, 6), ("#8A5A3A", "#5A3418", "#2A1408"), seed + 2, sk=0.2, n=4, inkw=1.6, hi=0.3))
    out.append(painted(D, rrect(380, 30, 560, 150, 18), ("#9ADCD0", "#3AA898", "#1A5E54"), seed + 3, sdir=(0.3, 1), sk=0.15, angle=-90, n=30, inkw=2, hi=0.35))
    for x in range(400, 560, 26):
        out.append(pline([(x, 36), (x, 148)], "#1A5E54", 1.6, x, 0.4, 1))
    # a rolled plaid sleeping bag with two straps
    sb = rrect(250, 56, 372, 146, 40, 10)
    sbd = smooth_closed(sb)
    out.append(plaid(D, sbd, (250, 56, 372, 146), "#3A7A5A", [("#1E3A2A", 0, 14), ("#F2C230", 22, 3)], seed + 4, sq=28, op=0.7))
    out.append(ink(sbd, INK, 2, seed + 4, 1, 0.7))
    out.append(painted(D, oval(354, 101, 18, 44, 20), ("#7AB89A", "#3A7A5A", "#1E3A2A"), seed + 5, sk=0.2, n=4, inkw=1.8, hi=0.3))
    sp_ = [(354 + 12 * math.cos(math.radians(a_)) * (1 - a_ / 1400), 101 + 30 * math.sin(math.radians(a_)) * (1 - a_ / 1400)) for a_ in range(0, 700, 30)]
    out.append(pline(sp_, "#1E3A2A", 1.6, seed + 6, 0.7, 1))
    for x in (282, 330):
        out.append(painted(D, poly([(x - 7, 52), (x + 7, 52), (x + 7, 150), (x - 7, 150)], 12), ("#B07A4A", "#7A4A24", "#3E220E"), x, sk=0.2, n=3, inkw=1.4, hi=0.3))
    bb = oval(238, 62, 40, 40, 30)
    out.append(painted(D, bb, ("#FFFFFF", "#F6F0E8", "#C8B8A8"), seed + 6, sk=0.18, n=6, inkw=2, hi=0.4))
    cid = D.clip(f'<path d="{smooth_closed(bb)}"/>')
    segs = "".join(f'<path d="M 238 62 L {238 + 60 * math.cos(math.radians(a)):.1f} {62 + 60 * math.sin(math.radians(a)):.1f} A 60 60 0 0 1 {238 + 60 * math.cos(math.radians(a + 40)):.1f} {62 + 60 * math.sin(math.radians(a + 40)):.1f} Z" fill="{c}"/>'
                   for a, c in ((-100, "#E8423A"), (20, "#2E8AD0"), (140, "#FFC93C")))
    out.append(f'<g {cid}>{segs}</g>' + ink(smooth_closed(bb), INK, 2, seed + 7, 1, 0.7))
    return "".join(out)


# ================================================================ 19. ARE WE THERE YET — embossed vanity plate on a butter-yellow wagon
@design("are-we-there-yet")
def are_we_there_yet():
    D = Doc("awt")
    out = []
    body = "M -10 -10 L 610 -10 L 610 610 L -10 610 Z"
    out.append(car_paint(D, body, (0, 0, 600, 600), ("#FFE9A8", "#F2C450", "#B88420"), 3, sky_band=(0.24, 0.3), tex=0.45))
    # rear window crammed with luggage
    win = smooth_closed(rrect(20, -40, 580, 150, 34))
    out.append(glass(D, win, (20, -40, 580, 150), 4, top="#CFE8F2", bot="#7A9AB0", refl=False))
    cid = D.clip(f'<path d="{win}"/>')
    out.append(f'<g {cid}>{suitcase_luggage(D, 5)}'
               f'<polygon points="{P([(90, -40), (170, -40), (80, 150), (0, 150)])}" fill="#FFFFFF" opacity="0.22"/>'
               f'<polygon points="{P([(196, -40), (214, -40), (124, 150), (106, 150)])}" fill="#FFFFFF" opacity="0.18"/></g>')
    out.append(ink(win, "#2A2010", 3, 6, 1, 0.8))
    out.append(taper([(-10, 168), (610, 168)], 9, 9, "#E8EEF2") + taper([(-10, 165), (610, 165)], 2.5, 2.5, "#FFFFFF", 0.9) + pline([(-10, 173), (610, 173)], "#7A5410", 1.4, 6, 0.6, 1))
    # tall wraparound tail lights at the edges
    for x0, x1, sd in ((-30, 34, 7), (566, 630, 8)):
        lp = rrect(x0, 200, x1, 430, 22, 10)
        out.append(painted(D, rrect(x0 - 6, 194, x1 + 6, 436, 26, 10), CHROME, sd, sk=0.2, n=6, inkw=2, hi=0.5))
        out.append(painted(D, lp, ("#FF8A7A", "#D8261E", "#6E0A0A"), sd + 1, sdir=(0, 1), sk=0.2, angle=-90, n=12, inkw=1.8, hi=0.35))
        for y in range(220, 420, 22):
            out.append(f'<path d="M {x0} {y} L {x1} {y}" stroke="#FF9A8A" stroke-width="1.6" opacity="0.5"/>')
        out.append(soft_glow(D, (x0 + x1) / 2, 315, 70, "#FF5A3A", 0.2))
    # recessed plate pocket
    pocket = smooth_closed(rrect(48, 190, 552, 466, 26))
    out.append(f'<path d="{pocket}" fill="#E2AE3A"/>')
    out.append(f'<path d="{pocket}" fill="{D.lin([(0, "#7A4E08", 0.6), (0.16, "#7A4E08", 0.0), (0.85, "#FFE9A8", 0.0), (1, "#FFF4D0", 0.6)])}"/>')
    out.append(ink(pocket, "#5A3A08", 2, 9, 1, 0.6))
    out.append(soft_glow(D, 300, 196, 120, "#FFF6E0", 0.35))
    # chrome bumper and road
    out.append(asphalt(D, 548, 10))
    out.append(chrome_bar(D, -40, 484, 640, 556, 11, sky_c="#CFE8F2", ground="#5A4A36", r=20, horizon=0.42))
    # ---- the plate
    x0, y0, x1, y1 = 74, 214, 526, 442
    plate = rrect(x0, y0, x1, y1, 16, 10)
    pd = smooth_closed(plate)
    pc = D.clip(f'<path d="{pd}"/>')
    g = [f'<path d="{pd}" fill="#1A1008" opacity="0.35" transform="translate(6 9)"/>',
         f'<path d="{pd}" fill="{D.lin([(0, "#FFFFFF"), (0.55, "#F2F0EA"), (1, "#D8DCE2")])}"/>']
    sc = [f'<rect x="{x0}" y="{y0 + 112}" width="{x1 - x0}" height="{y1 - y0 - 112}" fill="{D.lin([(0, "#FFE8C0"), (1, "#F8C890")])}" opacity="0.75"/>']
    sc.append(sun_disc(D, 300, y0 + 186, 44, ("#FFFCE0", "#FFD86A", "#F2A23A"), 12, glow_col="#FFE8A0", glow_r=2.6, strokes_n=20))
    sc.append(hill(D, ridge([(x0 - 10, y0 + 190), (200, y0 + 166), (330, y0 + 184), (x1 + 10, y0 + 160)], 13, 8), y1 + 10, ("#C8DCC8", "#9EBEA8", "#6A8A78"), 13, inkw=0, sop=(0.08, 0.2)))
    sc.append(hill(D, ridge([(x0 - 10, y0 + 206), (300, y0 + 196), (x1 + 10, y0 + 210)], 14, 5), y1 + 10, ("#B8D0B0", "#86AE8A", "#4E7A5A"), 14, inkw=0, sop=(0.08, 0.2)))
    for i, x in enumerate((112, 136, 470, 494)):
        sc.append(pine_tree_small(x, y0 + 200 + (i % 2) * 6, 34 + (i % 2) * 8, "#5A7E66", i))
    g.append(f'<g {pc} opacity="0.85">{"".join(sc)}</g>')
    # rolled rim
    g.append(f'<path d="{smooth_closed(rrect(x0 + 9, y0 + 9, x1 - 9, y1 - 9, 10, 10))}" fill="none" stroke="#FFFFFF" stroke-width="3.5" opacity="0.9"/>')
    g.append(f'<path d="{smooth_closed(rrect(x0 + 11, y0 + 11, x1 - 11, y1 - 11, 9, 10))}" fill="none" stroke="#1F3A62" stroke-width="3"/>')
    g.append(f'<path d="{smooth_closed(rrect(x0 + 13.5, y0 + 13.5, x1 - 13.5, y1 - 13.5, 8, 10))}" fill="none" stroke="#0A1428" stroke-width="1.4" opacity="0.35"/>')
    # header script, main stamped words, county strip
    g.append(vt(D, 300, y0 + 66, "Are we", SERIF_IT, 50, "#C8282A", 21, max_w=220, wob=0.2, density=0.4))
    g.append(emboss(300, y0 + 168, "THERE YET?", BEBAS, 126, "#1F3A62", 400, ls=4))
    g.append(small(300, y1 - 22, "BACKSEAT COUNTY", BEBAS, 22, "#1F3A62", max_w=220, ls=6))
    # registration stickers in the top corners
    for (cx, cy, txt, col, rr) in ((x0 + 64, y0 + 46, "NOPE", "#FF8A2A", -4), (x1 - 64, y0 + 46, "'26", "#2AA59A", 3)):
        sp = rrect(cx - 40, cy - 18, cx + 40, cy + 18, 5, 8)
        g.append(sticker(D, sp, f'<path d="{smooth_closed(sp)}" fill="{col}"/>',
                         small(cx, cy + 8.5, txt, BEBAS, 25, "#FFFFFF", max_w=66, ls=2), rot_=rr, margin=0, shadow=(1, 1.5, 0.3), seed=int(cx), wear=0.8, gloss=0.12))
    # bolts
    for bx, by in ((x0 + 74, y1 - 30), (x1 - 74, y1 - 30)):
        g.append(screw(D, bx, by, 9, int(bx)))
    # dents, scratches, a little road grime along the bottom
    wear_ = []
    rnd = random.Random(22)
    for _ in range(40):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        L = rnd.uniform(6, 30)
        a = math.radians(rnd.uniform(-30, 30) + rnd.choice([0, 180]))
        wear_.append(f'<path d="M {x:.1f} {y:.1f} l {L * math.cos(a):.1f} {L * math.sin(a):.1f}" stroke="#FFFFFF" stroke-width="1.1" opacity="{rnd.uniform(0.2, 0.5):.2f}"/>')
    wear_.append(f'<rect x="{x0}" y="{y1 - 40}" width="{x1 - x0}" height="40" fill="{D.lin([(0, "#6A5A40", 0), (1, "#6A5A40", 0.3)])}"/>')
    wear_.append(specks(23, (x0, y1 - 40, x1, y1), ["#5A4A30", "#8A7A5A"], 60, (0.6, 1.6), (0.2, 0.5)))
    W = x1 - x0
    wear_.append(f'<polygon points="{P([(x0 + W * 0.62, y0 - 10), (x0 + W * 0.74, y0 - 10), (x0 + W * 0.6, y1 + 10), (x0 + W * 0.48, y1 + 10)])}" fill="#FFFFFF" opacity="0.14"/>')
    g.append(f'<g {pc}>{"".join(wear_)}</g>')
    g.append(ink(pd, "#2A2A30", 2, 24, 1, 0.75))
    out.append(f'<g transform="rotate(-1.2 300 328)">{"".join(g)}</g>')
    return finish(D, out, 25, INK, 0.6)


def donut(D, cx, cy, r, seed, icing=("#FFC2D4", "#F47AA0", "#B03A66"), dough=("#F6C88A", "#D8964E", "#8A5220"), sprinkle=True, bite=None):
    """Top-down iced ring donut: dough ring, wavy icing with drips, glossy highlight, rainbow sprinkles."""
    out = [cast(D, cx + r * 0.08, cy + r * 0.12, r * 1.08, r * 1.0, strength=0.35, seed=seed)]
    ring = blob_pts(cx, cy, r, r * 0.96, seed, 0.03, 30)
    hole = blob_pts(cx + r * 0.02, cy - r * 0.02, r * 0.3, r * 0.28, seed + 1, 0.05, 16)
    d = smooth_closed(ring) + " " + smooth_closed(hole[::-1])
    out.append(f'<path d="{d}" fill-rule="evenodd" fill="{dough[1]}"/>')
    cid = D.clip(f'<path d="{d}" fill-rule="evenodd"/>')
    out.append(f'<g {cid}><circle cx="{cx - r * 0.3:.1f}" cy="{cy - r * 0.3:.1f}" r="{r * 0.9:.1f}" fill="{dough[0]}" opacity="0.5"/>'
               f'<circle cx="{cx + r * 0.4:.1f}" cy="{cy + r * 0.45:.1f}" r="{r * 0.8:.1f}" fill="{dough[2]}" opacity="0.35"/></g>')
    rnd = random.Random(seed)
    ic = []
    for i in range(44):
        a = 2 * math.pi * i / 44
        k = 0.8 + 0.06 * math.sin(a * 7 + seed) + (0.1 if rnd.random() < 0.18 else 0)
        ic.append((cx + r * k * math.cos(a), cy + r * 0.96 * k * math.sin(a)))
    ih = blob_pts(cx + r * 0.02, cy - r * 0.02, r * 0.42, r * 0.4, seed + 2, 0.08, 16)
    di = smooth_closed(ic) + " " + smooth_closed(ih[::-1])
    out.append(f'<path d="{di}" fill-rule="evenodd" fill="{icing[1]}"/>')
    cid2 = D.clip(f'<path d="{di}" fill-rule="evenodd"/>')
    out.append(f'<g {cid2}><circle cx="{cx - r * 0.35:.1f}" cy="{cy - r * 0.35:.1f}" r="{r * 0.75:.1f}" fill="{icing[0]}" opacity="0.6"/>'
               f'<circle cx="{cx + r * 0.5:.1f}" cy="{cy + r * 0.5:.1f}" r="{r * 0.7:.1f}" fill="{icing[2]}" opacity="0.3"/></g>')
    out.append(ink(di, icing[2], max(1.2, r * 0.02), seed + 3, 1, 0.6))
    out.append(taper([(cx - r * 0.62, cy + r * 0.05), (cx - r * 0.55, cy - r * 0.35), (cx - r * 0.3, cy - r * 0.6)], 2, r * 0.07, "#FFFFFF", 0.7))
    if sprinkle:
        cols = ["#FFFFFF", "#FFD23A", "#2AA59A", "#7A5AD0", "#FF6F59", "#5AB8F0"]
        for i in range(int(r * 0.7)):
            a = rnd.uniform(0, 2 * math.pi)
            rr = rnd.uniform(0.5, 0.74) * r
            x, y = cx + rr * math.cos(a), cy + rr * 0.96 * math.sin(a)
            b = rnd.uniform(0, math.pi)
            L = r * 0.05
            out.append(f'<path d="M {x - L * math.cos(b):.1f} {y - L * math.sin(b):.1f} L {x + L * math.cos(b):.1f} {y + L * math.sin(b):.1f}" stroke="{rnd.choice(cols)}" stroke-width="{max(2, r * 0.035):.1f}" stroke-linecap="round"/>')
    out.append(ink(smooth_closed(ring), dough[2], max(1.4, r * 0.025), seed + 4, 1, 0.7))
    out.append(ink(smooth_closed(hole), dough[2], max(1.2, r * 0.02), seed + 5, 1, 0.6))
    return "".join(out)


def twine(D, pts, seed, col=("#F6E6C8", "#D8B88A", "#8A6A3A"), w=5):
    sm = catmull(pts, 8)
    out = [taper([(x + 2, y + 3) for x, y in sm], w + 1, w + 1, "#1A1008", 0.25), taper(sm, w, w, col[1])]
    for i in range(0, len(sm) - 1, 2):
        x, y = sm[i]
        x2, y2 = sm[i + 1]
        out.append(f'<path d="M {x:.1f} {y - w * 0.4:.1f} L {x2:.1f} {y2 + w * 0.4:.1f}" stroke="{col[2]}" stroke-width="1.2" opacity="0.6"/>')
    out.append(taper([(x - 1, y - 1.5) for x, y in sm], w * 0.3, w * 0.3, col[0], 0.7))
    return "".join(out)


# ================================================================ 20. 0.0 — a euro oval on the lid of a donut box
@design("zero-point-zero")
def zero_point_zero():
    D = Doc("zpz")
    out = []
    table = "M -10 -10 L 610 -10 L 610 610 L -10 610 Z"
    out.append(wood_panel(D, table, (-10, -10, 610, 610), 3, pal=("#E8C49A", "#C8966A", "#7A5236")))
    # bakery box lid (top view), a bit rotated, with the front flap and corner folds
    lid = poly([(36, 46), (566, 30), (580, 560), (24, 574)], 16)
    out.append(cast(D, 310, 330, 300, 300, strength=0.35, seed=4))
    out.append(painted(D, lid, ("#FFE4EA", "#F8C8D4", "#C88A9E"), 5, sdir=(0.5, 0.8), sk=0.06, angle=-2, n=120, inkw=2.4, hi=0.3,
                       slen=(40, 120), sw=(2, 6), sop=(0.08, 0.22)))
    out.append(pline([(46, 96), (558, 82)], "#C88A9E", 2, 6, 0.6, 1) + pline([(40, 520), (574, 508)], "#C88A9E", 2, 7, 0.6, 1))
    for (x, y) in ((36, 46), (566, 30), (580, 560), (24, 574)):
        out.append(f'<path d="{blob(x + (30 if x < 300 else -30), y + (30 if y < 300 else -30), 18, 14, x + y, 0.2, 10)}" fill="#C88A9E" opacity="0.25"/>')
    # printed scallop border on the lid
    rnd = random.Random(7)
    for i in range(28):
        t = i / 27
        for (ax, ay), (bx, by) in (((56, 64), (546, 50)), ((44, 546), (560, 534))):
            x, y = ax + (bx - ax) * t, ay + (by - ay) * t
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#E89AB0" opacity="0.7"/>')
    # a coffee ring and a few crumbs
    out.append(f'<path d="{blob(118, 470, 54, 50, 8, 0.03, 30)}" fill="none" stroke="#A8724A" stroke-width="5" opacity="0.22"/>'
               f'<path d="{blob(116, 472, 50, 46, 9, 0.04, 30)}" fill="none" stroke="#A8724A" stroke-width="2" opacity="0.3"/>')
    out.append(specks(10, (380, 440, 580, 580), ["#D8964E", "#8A5220", "#F6C88A"], 26, (1.5, 3.5), (0.6, 0.95)))
    # twine across the lid, tied in a bow up in the corner
    out.append(twine(D, [(-10, 128), (200, 122), (420, 114), (610, 108)], 11))
    out.append(twine(D, [(520, -10), (522, 200), (528, 420), (532, 610)], 12))
    for sg in (-1, 1):
        loop = [(522, 114), (522 + sg * 26, 88), (522 + sg * 44, 96), (522 + sg * 34, 122), (522, 116)]
        out.append(twine(D, loop, 13 + sg, w=4))
    out.append(twine(D, [(522, 118), (500, 150), (494, 176)], 16, w=4) + twine(D, [(522, 118), (548, 152), (560, 170)], 17, w=4))
    out.append(f'<path d="{blob(522, 116, 9, 8, 13, 0.2, 10)}" fill="#D8B88A" stroke="#8A6A3A" stroke-width="1.6"/>')
    # the euro oval
    cx, cy = 282, 314
    pts = oval(cx, cy, 214, 148, 72)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#FFFFFF", "#FBFAF6", "#D8D2C8"), 16, fade=0.08)
    c = [f'<path d="{smooth_closed(oval(cx, cy, 196, 130, 72))}" fill="none" stroke="#141218" stroke-width="7"/>']
    c.append(vt(D, cx, cy + 60, "0.0", ANTON, 156, "#141218", 17, max_w=280, ls=6, wob=0.15, density=0.35))
    c.append(small(cx, cy + 100, "and proud of it", SERIF_IT, 28, "#141218", max_w=200))
    c.append(small(cx, cy - 84, "MILES", BEBAS, 26, "#141218", max_w=120, ls=8))
    c.append(hbar(D, cx - 120, cx - 52, cy - 93, 2.5, "#141218", 30) + hbar(D, cx + 52, cx + 120, cy - 93, 2.5, "#141218", 31))
    out.append(sticker(D, pts, face, "".join(c), rot_=-5, peel=(160, 26), seed=18, wear=0.8))
    # a pink sprinkle donut parked on the lid (bite taken), crumbs
    out.append(donut(D, 466, 476, 74, 19))
    out.append(sparkle(116, 130, 10, "#FFFFFF", 0.9) + sparkle(520, 386, 7, "#FFFFFF", 0.8))
    return finish(D, out, 20, INK, 0.6)


def stitch(pts, col, seed, dash="7 6", w=2.2, op=0.8):
    return f'<path d="{smooth_open(pts)}" fill="none" stroke="{col}" stroke-width="{w}" stroke-dasharray="{dash}" stroke-linecap="round" opacity="{op}"/>'


def buckle(D, cx, cy, w, h, seed, metal=("#FFF0B0", "#D8A83A", "#7A5A12")):
    outer = rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 5, 6)
    inner = rrect(cx - w / 2 + 6, cy - h / 2 + 6, cx + w / 2 - 6, cy + h / 2 - 6, 3, 6)
    d = smooth_closed(outer) + " " + smooth_closed(inner[::-1])
    return (f'<path d="{d}" fill-rule="evenodd" fill="#1A1008" opacity="0.3" transform="translate(2 3)"/>'
            f'<path d="{d}" fill-rule="evenodd" fill="{D.lin([(0, metal[0]), (0.5, metal[1]), (1, metal[2])], 0, 0, 1, 1)}"/>'
            + ink(d, "#3A2A08", 1.6, seed, 1, 0.7)
            + f'<path d="M {cx:.1f} {cy - h / 2 + 4:.1f} L {cx:.1f} {cy + h / 2 - 4:.1f}" stroke="{metal[1]}" stroke-width="4" stroke-linecap="round"/>')


def mini_sticker_palm(D, cx, cy, r, seed, rot_=0):
    """Round souvenir sticker: sunset, sea and a palm silhouette."""
    pts = oval(cx, cy, r, r, 40)
    d = smooth_closed(pts)
    face = (f'<path d="{d}" fill="{D.lin([(0, "#FF8A6A"), (0.55, "#FFC870"), (0.56, "#2AA59A"), (1, "#0E5E58")])}"/>'
            + f'<circle cx="{cx:.1f}" cy="{cy + r * 0.08:.1f}" r="{r * 0.36:.1f}" fill="#FFF0A0" opacity="0.95"/>'
            + f'<rect x="{cx - r:.1f}" y="{cy + r * 0.1:.1f}" width="{2 * r:.1f}" height="{r:.1f}" fill="#1F7E78"/>'
            + "".join(f'<path d="M {cx - r * 0.5 + k * r * 0.25:.1f} {cy + r * (0.25 + 0.12 * (k % 2)):.1f} l {r * 0.18:.1f} 0" stroke="#FFF0C0" stroke-width="2" opacity="0.8"/>' for k in range(4)))
    palm_ = (pline([(cx + r * 0.4, cy + r * 0.9), (cx + r * 0.35, cy + r * 0.2), (cx + r * 0.18, cy - r * 0.42)], "#2A1A2A", max(2.5, r * 0.08), seed, 1, 1)
             + "".join(taper([(cx + r * 0.18, cy - r * 0.42), (cx + r * 0.18 + r * 0.5 * math.cos(math.radians(a)), cy - r * 0.42 + r * 0.42 * math.sin(math.radians(a)))], r * 0.12, 1, "#2A1A2A")
                       for a in (-170, -130, -60, -20, 20, 160)))
    return sticker(D, pts, face, palm_, rot_=rot_, margin=6, shadow=(2, 3, 0.3), seed=seed, wear=0.9, gloss=0.1)


# ================================================================ 21. NEXT EXIT ADVENTURE — highway guide-sign decal on a vintage suitcase
@design("next-exit-adventure")
def next_exit_adventure():
    D = Doc("nea")
    out = [f'<rect width="600" height="600" fill="#E8DCC4"/>']
    out.append(stripes_in(D, "M -10 -10 L 610 -10 L 610 90 L -10 90 Z", (0, -10, 600, 90), 0, [18, 18], ["#D8C8A8", None], 2, 0.8))
    # leather handle at the top
    out.append(pline([(210, 92), (214, 34), (386, 34), (390, 92)], "#4A2A14", 22, 3, 1, 1) + pline([(214, 88), (218, 40), (382, 40), (386, 88)], "#8A5A30", 12, 4, 0.9, 1))
    out.append(taper([(226, 44), (300, 40), (370, 44)], 3, 3, "#E8B88A", 0.7))
    for x in (212, 388):
        out.append(painted(D, rrect(x - 22, 70, x + 22, 104, 6, 6), ("#FFF0B0", "#D8A83A", "#7A5A12"), x, sk=0.2, n=4, inkw=1.8, hi=0.5))
    # the case: rounded hard shell, mustard vinyl with a pebbled texture
    case = smooth_closed(rrect(12, 84, 588, 660, 46, 16))
    out.append(cast(D, 300, 620, 340, 60, strength=0.3))
    out.append(car_paint(D, case, (12, 84, 588, 640), ("#F6C878", "#E0A04A", "#9A6420"), 5, sky_band=(0.0, 0.0), tex=0.6))
    cid = D.clip(f'<path d="{case}"/>')
    rnd = random.Random(6)
    peb = "".join(f'<circle cx="{rnd.uniform(0, 600):.1f}" cy="{rnd.uniform(84, 600):.1f}" r="{rnd.uniform(0.8, 2):.1f}" fill="{rnd.choice(["#FFE0A8", "#9A6420"])}" opacity="{rnd.uniform(0.15, 0.4):.2f}"/>' for _ in range(500))
    out.append(f'<g {cid}>{peb}</g>')
    out.append(f'<path d="{smooth_closed(rrect(28, 100, 572, 640, 34, 16))}" fill="none" stroke="#7A4E18" stroke-width="2.4" stroke-dasharray="8 6" opacity="0.6"/>')
    out.append(ink(case, "#5A3A10", 2.6, 7, 1, 0.8))
    # brass corner guards
    for (x, y, a) in ((12, 84, 0), (588, 84, 90)):
        cg = [(x, y + 64), (x, y + 20), (x + (20 if a == 0 else -20), y), (x + (64 if a == 0 else -64), y), (x + (64 if a == 0 else -64), y + 16), (x + (24 if a == 0 else -24), y + 24), (x + (16 if a == 0 else -16), y + 64)]
        out.append(painted(D, cg, ("#FFF0B0", "#D8A83A", "#7A5A12"), x + 3, sk=0.2, n=6, inkw=2, hi=0.5))
        out.append(f'<circle cx="{x + (14 if a == 0 else -14)}" cy="{y + 14}" r="3" fill="#7A5A12"/>')
    # leather straps with buckles
    for x in (96, 504):
        sp = poly([(x - 24, 84), (x + 24, 84), (x + 24, 610), (x - 24, 610)], 30)
        out.append(painted(D, sp, ("#B07A4A", "#7A4A24", "#3E220E"), x, sdir=(1, 0.1), sk=0.15, angle=-90, n=30, inkw=2, hi=0.3))
        out.append(stitch([(x - 17, 90), (x - 17, 610)], "#E8C08A", x) + stitch([(x + 17, 90), (x + 17, 610)], "#E8C08A", x + 1))
        out.append(buckle(D, x, 150, 62, 46, x + 2))
    # other travel stickers already on the case
    out.append(mini_sticker_palm(D, 482, 528, 50, 8, rot_=12))
    tag = rrect(56, 470, 196, 556, 8, 10)
    out.append(sticker(D, tag, f'<path d="{smooth_closed(tag)}" fill="#F6EFE0"/>' + stripes_in(D, smooth_closed(tag), bbox(tag), 0, [10, 10], ["#E8423A", None, "#1F3A62", None], 9),
                       f'<rect x="76" y="488" width="100" height="50" fill="#F6EFE0"/>' + small(126, 522, "AIR MAIL", BEBAS, 26, "#1F3A62", max_w=90, ls=2),
                       rot_=-8, margin=5, shadow=(2, 3, 0.3), seed=10, wear=0.9, gloss=0.1))
    # ---- the guide sign decal: panel + exit tab
    tab = rrect(318, 168, 506, 236, 12, 10)
    panel = rrect(70, 222, 530, 456, 22, 12)
    # union outline: walk panel, splice tab on top edge
    pts = [p for p in panel if not (p[1] < 223 and 312 < p[0] < 512)]
    i0 = next(i for i, p in enumerate(pts) if p[1] < 223 and p[0] >= 512)
    tab_top = [(318, 232)] + [p for p in tab if p[1] < 222] + [(506, 232)]
    tab_top = sorted([p for p in tab if p[1] < 222], key=lambda p: p[0])
    pts = pts[:i0] + [(318, 222)] + tab_top + [(506, 222)] + pts[i0:]
    d = smooth_closed(pts)
    green = ("#3A9A64", "#1A6A40", "#0C3E24")
    face = face_fill(D, d, pts, green, 11, fade=0.16)
    c = [f'<path d="{smooth_closed(rrect(82, 234, 518, 444, 14, 12))}" fill="none" stroke="#F6F6EE" stroke-width="5"/>',
         f'<path d="{smooth_closed(rrect(330, 180, 494, 238, 7, 10))}" fill="none" stroke="#F6F6EE" stroke-width="4.5"/>',
         f'<path d="M 330 234 L 494 234" stroke="{green[1]}" stroke-width="8"/>']
    c.append(small(412, 222, "EXIT 1", JOS, 38, "#F6F6EE", max_w=140, ls=3))
    c.append(vt(D, 300, 300, "NEXT EXIT", JOS, 44, "#F6F6EE", 12, max_w=300, ls=6, wob=0.15, density=0.3))
    c.append(vt(D, 300, 382, "ADVENTURE", JOS, 82, "#F6F6EE", 13, max_w=400, ls=3, wob=0.15, density=0.3))
    # up-right exit arrow and the distance
    ax, ay = 420, 418
    c.append(f'<path d="M {ax - 46} {ay + 22} L {ax + 14} {ay - 14}" stroke="#F6F6EE" stroke-width="10" stroke-linecap="round"/>'
             f'<path d="M {ax + 30} {ay - 24} L {ax - 2} {ay - 26} L {ax + 18} {ay + 2} Z" fill="#F6F6EE" stroke="#F6F6EE" stroke-width="5" stroke-linejoin="round"/>')
    c.append(small(190, 432, "½ MILE", JOS, 34, "#F6F6EE", max_w=150, ls=2))
    out.append(sticker(D, pts, face, "".join(c), rot_=-3, peel=(30, 30), seed=14))
    return finish(D, out, 15, INK, 0.6)


def felt(D, d, box, cols, seed, n=None, L=(3, 8), w=(0.7, 1.4), op=(0.25, 0.6)):
    """Felt nap: lots of tiny fibres at random angles, clipped to the shape."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    n = n or int((x1 - x0) * (y1 - y0) / 45)
    cid = D.clip(f'<path d="{d}"/>')
    fs = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        a = rnd.uniform(0, math.pi)
        l = rnd.uniform(*L)
        fs.append(f'<path d="M {x:.1f} {y:.1f} l {l * math.cos(a):.1f} {l * math.sin(a):.1f}" stroke="{rnd.choice(cols)}" stroke-width="{rnd.uniform(*w):.1f}" opacity="{rnd.uniform(*op):.2f}" stroke-linecap="round"/>')
    return f'<g {cid}>{"".join(fs)}</g>'


def road_map(D, seed):
    """An unfolded paper road map: panels with fold creases, parks, lakes, a river, highways, back roads, towns."""
    rnd = random.Random(seed)
    out = [f'<rect x="-10" y="-10" width="620" height="620" fill="#F4ECD8"/>']
    # parks and lakes
    for i, (x, y, rx, ry) in enumerate(((90, 110, 110, 70), (520, 210, 90, 120), (150, 520, 120, 60), (430, 540, 70, 50))):
        out.append(wash(blob(x, y, rx, ry, seed + i, 0.18, 16), "#CFE0B0", seed + i, 2, 2, 0.4, edge="#8AAA6A", edge_w=1.4))
        out.append(specks(seed + i, (x - rx * 0.6, y - ry * 0.6, x + rx * 0.6, y + ry * 0.6), ["#7A9A5A"], 14, (1.2, 2.2), (0.4, 0.7)))
    for i, (x, y, rx, ry) in enumerate(((300, 70, 70, 34), (560, 420, 60, 40), (40, 330, 44, 70))):
        out.append(wash(blob(x, y, rx, ry, seed + 10 + i, 0.2, 16), "#A8D4E8", seed + 10 + i, 2, 1.5, 0.4, edge="#5A9AC0", edge_w=1.6))
    out.append(ink(smooth_open([(330, 80), (380, 140), (360, 210), (420, 260), (470, 330), (540, 400)]), "#6AAAD0", 4, seed, 1, 0.8))
    # thin back roads
    for i in range(16):
        p0 = (rnd.uniform(-20, 620), rnd.uniform(-20, 620))
        pts = [p0]
        for _ in range(4):
            pts.append((pts[-1][0] + rnd.uniform(-120, 120), pts[-1][1] + rnd.uniform(-120, 120)))
        out.append(ink(smooth_open(pts), "#B8A890", 1.4, seed + 20 + i, 1, 0.7))
    # yellow state roads, red highways with a white casing
    for i, pts in enumerate(([(-20, 180), (160, 220), (330, 170), (620, 250)], [(120, -20), (180, 200), (260, 380), (240, 620)], [(-20, 460), (200, 440), (380, 480), (620, 430)])):
        out.append(ink(smooth_open(pts), "#FFFFFF", 7, seed + 40 + i, 1, 1) + ink(smooth_open(pts), "#F2C230", 4, seed + 41 + i, 1, 1))
    for i, pts in enumerate(([(-20, 300), (150, 320), (320, 290), (470, 330), (620, 300)], [(420, -20), (440, 160), (400, 330), (460, 620)])):
        out.append(ink(smooth_open(pts), "#FFFFFF", 10, seed + 50 + i, 1, 1) + ink(smooth_open(pts), "#D8382A", 6, seed + 51 + i, 1, 1))
    # towns
    for i in range(14):
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 580)
        r = rnd.choice([3, 4, 6])
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{"#F2C230" if r == 6 else "#FFFFFF"}" stroke="#3A3028" stroke-width="1.6"/>')
    # fold creases: 3 x 3 panels, alternating light
    for k in (200, 400):
        out.append(f'<path d="M {k} -10 L {k + 2} 610" stroke="#8A7A5A" stroke-width="2" opacity="0.3"/><path d="M {k + 3} -10 L {k + 5} 610" stroke="#FFFFFF" stroke-width="2" opacity="0.6"/>')
        out.append(f'<path d="M -10 {k} L 610 {k - 2}" stroke="#8A7A5A" stroke-width="2" opacity="0.3"/><path d="M -10 {k + 3} L 610 {k + 1}" stroke="#FFFFFF" stroke-width="2" opacity="0.6"/>')
    for i in range(3):
        for j in range(3):
            if (i + j) % 2:
                out.append(f'<rect x="{i * 200}" y="{j * 200}" width="200" height="200" fill="{D.lin([(0, "#6A5A3A", 0.0), (1, "#6A5A3A", 0.08)], 0, 0, 1, 1)}"/>')
    return "".join(out)


def pencil(D, x0, y0, x1, y1, seed, body=("#FFE07A", "#F2B42A", "#A8740A")):
    a = math.atan2(y1 - y0, x1 - x0)
    L = math.hypot(x1 - x0, y1 - y0)
    c, s_ = math.cos(a), math.sin(a)

    def T(u, v):
        return (x0 + u * c - v * s_, y0 + u * s_ + v * c)
    w = 11
    out = [f'<path d="{lpath([T(4, w + 4), T(L * 0.9, w + 4), T(L + 4, 4), T(4, 6)])}" fill="#1A1008" opacity="0.18"/>']
    out.append(painted(D, poly([T(L * 0.1, -w), T(L * 0.82, -w), T(L * 0.82, w), T(L * 0.1, w)], 14), body, seed, sdir=(0, 1), sk=0.2, angle=math.degrees(a), n=16, inkw=1.8, hi=0.4))
    out.append(f'<path d="M {T(L * 0.1, 0)[0]:.1f} {T(L * 0.1, 0)[1]:.1f} L {T(L * 0.82, 0)[0]:.1f} {T(L * 0.82, 0)[1]:.1f}" stroke="{body[2]}" stroke-width="1.4" opacity="0.6"/>')
    out.append(painted(D, [T(L * 0.82, -w), T(L * 0.97, -2), T(L, 0), T(L * 0.97, 2), T(L * 0.82, w)], ("#FFF0D8", "#EAC8A0", "#A8865A"), seed + 1, sk=0.2, n=4, inkw=1.6, hi=0.3))
    out.append(f'<path d="{lpath([T(L * 0.95, -3.5), T(L, 0), T(L * 0.95, 3.5)])}" fill="#3A3438"/>')
    out.append(painted(D, poly([T(L * 0.04, -w), T(L * 0.1, -w), T(L * 0.1, w), T(L * 0.04, w)], 6), CHROME, seed + 2, sk=0.2, n=3, inkw=1.4, hi=0.5))
    out.append(painted(D, poly([T(-L * 0.02, -w + 1), T(L * 0.04, -w), T(L * 0.04, w), T(-L * 0.02, w - 1)], 6), ("#FFB0B8", "#F27A8A", "#A83A4A"), seed + 3, sk=0.2, n=3, inkw=1.6, hi=0.4))
    return "".join(out)


def pennant_letters(D, s, x, cy, h_at, cap_ratio, font, fill, outline, shadow, side, ls=3, end=None, cap_max=80, gap=7, margin=12):
    """Classic pennant lettering: each letter sized to the local height of the tapering felt, scaled so the
    word ends at `end`."""
    def lay(k):
        gx, gl = x, []
        for ch in s:
            cap = min(cap_max, max(12, k * h_at(gx + 20) - margin))
            for _ in range(3):
                size = cap / cap_ratio
                adv = measure(ch, font, size) + ls
                cap = min(cap_max, max(12, k * (h_at(gx + adv) - gap) - margin))
            size = cap / cap_ratio
            adv = measure(ch, font, size) + ls
            base = cy - gap if side < 0 else cy + gap + cap
            gl.append((gx, base, size, ch))
            gx += adv
        return gl, gx
    lo, hi = 0.2, 1.0
    for _ in range(30):
        mid = (lo + hi) / 2
        _, e = lay(mid)
        if end is None or e <= end:
            lo = mid
        else:
            hi = mid
    glyphs, ex = lay(lo)
    G = "".join(f'<text x="{gx:.1f}" y="{gy:.1f}" {font} font-size="{sz:.1f}">{esc(ch)}</text>' for gx, gy, sz, ch in glyphs)
    return (f'<g fill="{shadow}" transform="translate(3 4)">{G}</g>'
            f'<g fill="{outline}" stroke="{outline}" stroke-width="7" stroke-linejoin="round">{G}</g>'
            f'<g fill="{fill}">{G}</g>'), ex


def rosette(D, cx, cy, r, seed, gold=("#FFF0A0", "#E8B840", "#8A6210"), ribbon=("#E87070", "#C8282A", "#6E0E12")):
    out = []
    for sg in (-1, 1):
        tail = [(cx + sg * r * 0.2, cy + r * 0.4), (cx + sg * r * 0.62, cy + r * 1.55), (cx + sg * r * 0.42, cy + r * 1.38), (cx + sg * r * 0.3, cy + r * 1.6), (cx + sg * r * 0.0, cy + r * 0.5)]
        out.append(painted(D, tail, ribbon, seed + sg, sdir=(0, 1), sk=0.18, angle=-80, n=8, inkw=1.8, hi=0.35))
    pts = []
    for i in range(48):
        a = 2 * math.pi * i / 48
        rr = r * (1 if i % 2 == 0 else 0.9)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    out.append(f'<path d="{lpath(pts)}" fill="#1A1008" opacity="0.3" transform="translate(3 4)"/>')
    out.append(f'<path d="{lpath(pts)}" fill="{D.lin([(0, gold[0]), (0.5, gold[1]), (1, gold[2])], 0, 0, 1, 1)}"/>')
    out.append(ink(lpath(pts), gold[2], 1.6, seed, 1, 0.8))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.74:.1f}" fill="{gold[1]}" stroke="{gold[2]}" stroke-width="2"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.66:.1f}" fill="none" stroke="#FFF6C8" stroke-width="1.6" stroke-dasharray="2 4" opacity="0.9"/>')
    out.append(taper([(cx - r * 0.5, cy - r * 0.2), (cx - r * 0.3, cy - r * 0.52)], r * 0.1, 2, "#FFFFFF", 0.7))
    return "".join(out)


# ================================================================ 22. CERTIFIED BACKSEAT DRIVER — felt pennant decal on an unfolded road map
@design("certified-backseat-driver")
def certified_backseat_driver():
    from fontTools.ttLib import TTFont
    D = Doc("cbd")
    out = [road_map(D, 3)]
    # marker route, a coffee ring and a pencil
    route = [(90, 560), (160, 520), (230, 548), (300, 520)]
    out.append(f'<path d="{smooth_open(route)}" fill="none" stroke="#D8382A" stroke-width="4" stroke-dasharray="10 8" stroke-linecap="round" opacity="0.85"/>')
    out.append(f'<path d="{blob(520, 92, 52, 48, 4, 0.03, 30)}" fill="none" stroke="#A8724A" stroke-width="5" opacity="0.2"/>')
    out.append(pencil(D, 410, 586, 590, 470, 5))
    # ---- the pennant
    bx0, bx1, ytop, ybot, tipx = 60, 122, 150, 450, 540
    cy = (ytop + ybot) / 2
    H = (ybot - ytop) / 2
    h_at = lambda x: H * (tipx - x) / (tipx - bx1) if x > bx1 else H
    pts = poly([(bx0, ytop), (bx1, ytop), (tipx, cy), (bx1, ybot), (bx0, ybot)], 10)
    d = smooth_closed(jitter(pts, 3, 0.4))
    maroon = ("#B0384A", "#7E1A2E", "#4A0A18")
    face = f'<path d="{d}" fill="{maroon[1]}"/>'
    face += felt(D, d, bbox(pts), [maroon[0], maroon[2], "#9A2A3C"], 6)
    band = smooth_closed(poly([(bx0 - 10, ytop - 10), (bx1, ytop - 10), (bx1, ybot + 10), (bx0 - 10, ybot + 10)], 12))
    face += f'<path d="{band}" fill="#F2E6CC"/>' + felt(D, band, (bx0 - 10, ytop - 10, bx1, ybot + 10), ["#FFFFFF", "#C8B48A", "#E0D0B0"], 7)
    face += f'<g fill="{maroon[1]}">' + "".join(f'<path d="{blob(89, y, 9, 9, int(y), 0.1, 10)}"/>' for y in range(184, 440, 48)) + "</g>"
    c = [stitch([(bx1 + 6, ytop + 6), (bx1 + 6, ybot - 6)], "#F2E6CC", 8, dash="6 5", w=2),
         stitch([(bx1 + 10, ytop + 10), (tipx - 22, cy - 2)], "#E8B840", 9, dash="6 6", w=2),
         stitch([(bx1 + 10, ybot - 10), (tipx - 22, cy + 2)], "#E8B840", 10, dash="6 6", w=2)]
    f = TTFont(str(__import__("common").FONT_DIR / "Anton-Regular.ttf")) if (__import__("common").FONT_DIR / "Anton-Regular.ttf").exists() else None
    cap_ratio = (f["OS/2"].sCapHeight / f["head"].unitsPerEm) if f else 0.73
    t1, _ = pennant_letters(D, "BACKSEAT", 140, cy, h_at, cap_ratio, ANTON, "#FFF4DE", "#E8B840", maroon[2], -1, end=460, cap_max=200, gap=7)
    t2, _ = pennant_letters(D, "DRIVER", 146, cy, h_at, cap_ratio, ANTON, "#FFF4DE", "#E8B840", maroon[2], 1, end=420, cap_max=200, gap=9)
    c.append(t1 + t2)
    out.append(sticker(D, pts, face, "".join(c), rot_=-6, margin=8, seed=12, wear=0.7, gloss=0.08))
    # the gold CERTIFIED seal stuck over the corner
    sx, sy = 156, 486
    out.append(rosette(D, sx, sy, 62, 13))
    out.append(small(sx, sy + 7, "CERTIFIED", BEBAS, 21, "#5A3A08", max_w=84, ls=1.5))
    out.append(star(sx, sy - 20, 7, "#5A3A08") + star(sx - 24, sy - 16, 4.5, "#5A3A08") + star(sx + 24, sy - 16, 4.5, "#5A3A08"))
    out.append(small(sx, sy + 30, "100%", BEBAS, 18, "#5A3A08", max_w=60, ls=1))
    return finish(D, out, 14, INK, 0.6)


def plaid(D, d, box, base, bands, seed, sq=48, op=0.55):
    """Buffalo / tartan check: two crossing band sets over a base colour, clipped to the shape."""
    x0, y0, x1, y1 = box
    cid = D.clip(f'<path d="{d}"/>')
    out = [f'<g {cid}><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{base}"/>']
    for col, off, w in bands:
        x = x0 + off
        while x < x1:
            out.append(f'<rect x="{x:.1f}" y="{y0}" width="{w}" height="{y1 - y0}" fill="{col}" opacity="{op}"/>')
            x += sq
        y = y0 + off
        while y < y1:
            out.append(f'<rect x="{x0}" y="{y:.1f}" width="{x1 - x0}" height="{w}" fill="{col}" opacity="{op}"/>')
            y += sq
    out.append(strokes(D.nid(), d, (x0 - 40, y0, x1, y1), ["#FFFFFF", "#000000"], seed, n=int((x1 - x0) * (y1 - y0) / 500), angle=45, length=(4, 10), width=(0.8, 1.6), opacity=(0.06, 0.16)))
    out.append("</g>")
    return "".join(out)


def badge_scene(D, cx, cy, r, seed):
    """Inside of a round adventure badge: dawn sky, layered blue mountains, pine ridge, lake and a canoe."""
    out = [sky(D, [(0, "#FF9A6A"), (0.45, "#FFD49A"), (1, "#FFF2D0")], seed, 600, ["#FFE0B0", "#FFB890"], 30)]
    out.append(sun_disc(D, cx + r * 0.3, cy - r * 0.42, r * 0.17, ("#FFFCE8", "#FFE890", "#FFC060"), seed + 1, glow_col="#FFF0B0", glow_r=2.6, strokes_n=14))
    for i, (col, yb, amp, sd) in enumerate((("#B898B8", -0.05, 0.42, 3), ("#7A7AA8", 0.12, 0.3, 4), ("#4A5A88", 0.26, 0.2, 5))):
        pk = [(cx - r * 1.2, cy + r * (yb + 0.2)), (cx - r * 0.6, cy + r * (yb - amp)), (cx - r * 0.2, cy + r * (yb - amp * 0.3)),
              (cx + r * 0.25, cy + r * (yb - amp * 0.9)), (cx + r * 0.8, cy + r * (yb - amp * 0.2)), (cx + r * 1.2, cy + r * (yb + 0.1))]
        out.append(hill(D, ridge(pk, seed + sd, 6, 4), cy + r * 1.2, (mix(col, "#FFFFFF", 0.25), col, mix(col, "#000000", 0.3)), seed + sd, inkw=0, sop=(0.1, 0.25)))
        if i == 0:
            for (px, py) in ((cx - r * 0.6, cy + r * (yb - amp)), (cx + r * 0.25, cy + r * (yb - amp * 0.9))):
                out.append(f'<path d="M {px - r * 0.1:.1f} {py + r * 0.08:.1f} L {px:.1f} {py:.1f} L {px + r * 0.09:.1f} {py + r * 0.07:.1f} L {px + r * 0.03:.1f} {py + r * 0.1:.1f} L {px - r * 0.03:.1f} {py + r * 0.06:.1f} Z" fill="#FFFFFF" opacity="0.85"/>')
    out.append(f'<rect x="{cx - r * 1.1:.1f}" y="{cy + r * 0.38:.1f}" width="{r * 2.2:.1f}" height="{r:.1f}" fill="{D.lin([(0, "#7AA8C8"), (1, "#3A6A9A")])}"/>')
    out.append(wave_lines(seed + 6, (cx - r, cy + r * 0.42, cx + r, cy + r * 0.9), ["#FFFFFF", "#FFD8A8", "#A8D0E8"], 22, (r * 0.08, r * 0.2), 1.6))
    for k in range(6):
        y = cy + r * (0.47 + k * 0.07)
        w = r * (0.16 - k * 0.018)
        out.append(taper([(cx + r * 0.3 - w, y), (cx + r * 0.3 + w, y)], 2.5, 2.5, "#FFF0B8", 0.75))
    for i in range(16):
        x = cx - r * 1.05 + i * r * 0.14
        out.append(pine_tree_small(x, cy + r * 0.42, r * (0.22 + 0.14 * ((i * 7) % 5) / 4), "#1E3A3A", i + seed))
    for i in range(6):
        x = cx + r * (0.5 + i * 0.1)
        out.append(pine_tree_small(x, cy + r * 0.44, r * (0.3 + 0.08 * (i % 3)), "#16302E", i + seed + 30))
    out.append(canoe(D, cx - r * 0.42, cx - r * 0.02, cy + r * 0.64, r * 0.05, seed + 7, pal=("#FF8A6A", "#D8452A", "#7A1E0E")))
    out.append(f'<path d="{blob(cx - r * 0.22, cy + r * 0.56, r * 0.05, r * 0.08, seed, 0.1, 10)}" fill="#2E4A6A"/>')
    out.append(f'<circle cx="{cx - r * 0.22:.1f}" cy="{cy + r * 0.45:.1f}" r="{r * 0.035:.1f}" fill="#F2C8A0"/>'
               f'<path d="M {cx - r * 0.26:.1f} {cy + r * 0.44:.1f} Q {cx - r * 0.22:.1f} {cy + r * 0.39:.1f} {cx - r * 0.18:.1f} {cy + r * 0.44:.1f} Z" fill="#E8423A"/>')
    out.append(pline([(cx - r * 0.34, cy + r * 0.5), (cx - r * 0.1, cy + r * 0.74)], "#6A4A2A", 2.4, seed, 1, 1))
    out.append(seagull(cx - r * 0.3, cy - r * 0.38, r * 0.06, "#4A3A48") + seagull(cx - r * 0.18, cy - r * 0.46, r * 0.04, "#4A3A48"))
    return "".join(out)


def pine_cone(D, cx, cy, s, seed, rot_=0):
    out = [f'<g transform="rotate({rot_} {cx} {cy})">', cast(D, cx + 3, cy + s * 0.9, s * 0.6, s * 0.14, strength=0.35, seed=seed)]
    out.append(painted(D, blob_pts(cx, cy, s * 0.48, s * 0.9, seed, 0.04, 18), ("#B07A4A", "#7A4A24", "#3E220E"), seed, sk=0.2, n=6, inkw=1.8, hi=0.3))
    for row in range(7):
        y = cy - s * 0.75 + row * s * 0.24
        w = s * 0.48 * math.sin(math.pi * (row + 0.7) / 7.6)
        for k in range(-2, 3):
            x = cx + k * w * 0.42 + (row % 2) * w * 0.2
            if abs(x - cx) < w:
                out.append(f'<path d="M {x - s * 0.12:.1f} {y:.1f} Q {x:.1f} {y + s * 0.2:.1f} {x + s * 0.12:.1f} {y:.1f}" fill="#9A6234" stroke="#3E220E" stroke-width="1.4"/>')
    out.append("</g>")
    return "".join(out)


# ================================================================ 23. ADVENTURE AWAITS — round badge on a green camp cooler
@design("adventure-awaits")
def adventure_awaits():
    D = Doc("aaw")
    out = []
    # plaid blanket behind, the cooler's lid edge across the top
    out.append(plaid(D, "M -10 -10 L 610 -10 L 610 120 L -10 120 Z", (-10, -10, 610, 120), "#C83A2A", [("#2A1A14", 0, 24), ("#E85A44", 30, 6)], 3, sq=48, op=0.6))
    cooler = "M -10 70 L 610 70 L 610 610 L -10 610 Z"
    out.append(cast(D, 300, 80, 360, 20, strength=0.4))
    out.append(car_paint(D, cooler, (0, 70, 600, 600), ("#7AB08A", "#3E7A56", "#1A4A30"), 4, sky_band=(0.04, 0.1), tex=0.7))
    # lid lip, ribbed panel, white rope handle, chrome latch
    out.append(painted(D, poly([(-10, 64), (610, 64), (610, 114), (-10, 114)], 30), ("#F6F0E2", "#E8DCC4", "#A8987A"), 5, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=2, hi=0.5))
    out.append(taper([(-10, 118), (610, 118)], 6, 6, "#0E2A1A", 0.5))
    for y in (520, 548, 576):
        out.append(taper([(-10, y), (610, y)], 9, 9, "#2A5E40", 0.8) + taper([(-10, y - 4), (610, y - 4)], 2.5, 2.5, "#9ACCAA", 0.7))
    out.append(painted(D, rrect(256, 86, 344, 152, 10, 8), CHROME, 6, sdir=(0.3, 1), sk=0.2, n=8, inkw=2, hi=0.6))
    out.append(f'<path d="{smooth_closed(rrect(286, 126, 314, 162, 6, 6))}" fill="#9AA4AE" stroke="#2A2A30" stroke-width="1.6"/>')
    for sg in (-1, 1):
        x = 300 + sg * 262
        out.append(painted(D, rrect(x - 14, 136, x + 14, 170, 6, 6), CHROME, 7 + sg, sk=0.2, n=4, inkw=1.8, hi=0.5))
        out.append(pline([(x, 168), (x + sg * 6, 240), (x + sg * 2, 320)], "#F6F0E2", 9, 8 + sg, 1, 1) + pline([(x, 168), (x + sg * 6, 240), (x + sg * 2, 320)], "#B8A88A", 2, 9 + sg, 0.5, 1))
    # scuffs on the cooler body
    rnd = random.Random(8)
    sc = "".join(f'<path d="M {(x := rnd.uniform(0, 600)):.1f} {(y := rnd.uniform(130, 500)):.1f} l {rnd.uniform(8, 30):.1f} {rnd.uniform(-4, 4):.1f}" stroke="#CFE8D8" stroke-width="1.4" opacity="{rnd.uniform(0.2, 0.5):.2f}"/>' for _ in range(40))
    out.append(sc)
    # ---- the round badge
    cx, cy, R = 300, 338, 196
    pts = oval(cx, cy, R, R, 80)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#F6EFDC", "#EFE3C8", "#B8A27A"), 10, fade=0.1)
    ri = R - 60
    cid = D.clip(f'<circle cx="{cx}" cy="{cy}" r="{ri}"/>')
    c = [f'<circle cx="{cx}" cy="{cy}" r="{R - 8}" fill="none" stroke="#1E3A3A" stroke-width="4"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{ri + 6}" fill="#1E3A3A"/>',
         f'<g {cid}>{badge_scene(D, cx, cy, ri, 11)}</g>',
         f'<circle cx="{cx}" cy="{cy}" r="{ri}" fill="none" stroke="#1E3A3A" stroke-width="5"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{ri + 4}" fill="none" stroke="#E8A040" stroke-width="2"/>']
    c.append(arc_label(D, "ADVENTURE", cx, cy, R - 48, ANTON, 36, "#1E3A3A", ls=7, top=True))
    c.append(arc_label(D, "AWAITS", cx, cy, R - 21, ANTON, 34, "#C0532C", ls=10, top=False))
    for sg in (-1, 1):
        c.append(star(cx + sg * (R - 34), cy, 9, "#C0532C"))
    out.append(sticker(D, pts, face, "".join(c), rot_=-4, peel=(150, 24), seed=19, wear=0.8))
    # pine cones and needles dropped on the lid
    out.append(pine_cone(D, 520, 520, 40, 13, rot_=60) + pine_cone(D, 470, 560, 30, 14, rot_=110))
    for i in range(10):
        x, y = 70 + rnd.uniform(-30, 60), 520 + rnd.uniform(-20, 50)
        a = rnd.uniform(0, math.pi)
        out.append(f'<path d="M {x:.1f} {y:.1f} l {28 * math.cos(a):.1f} {28 * math.sin(a):.1f}" stroke="{rnd.choice(["#4E6A3A", "#7A5A2A"])}" stroke-width="2" stroke-linecap="round"/>')
    return finish(D, out, 15, INK, 0.6)


def banner(D, cx, cy, w, h, pal, seed, tail=46, drop=14, notch=16, arch=10):
    """A ribbon banner: arched centre band, folded-back tails with V notches, darker fold shadows."""
    light, base, dark = pal
    x0, x1 = cx - w / 2, cx + w / 2
    out = []
    for sg in (-1, 1):
        xe = x0 if sg < 0 else x1
        t_in = xe - sg * 8
        t_out = xe + sg * tail
        tp = [(t_in, cy - h / 2 + drop), (t_out, cy - h / 2 + drop + 4), (t_out - sg * notch, cy + drop + 2), (t_out, cy + h / 2 + drop), (t_in, cy + h / 2 + drop)]
        out.append(painted(D, tp, (base, dark, mix(dark, "#000000", 0.3)), seed + sg, sdir=(0, 1), sk=0.15, angle=0, n=10, inkw=2, hi=0.2))
        fold = [(xe, cy + h / 2 - arch * 0.2), (t_in, cy + h / 2 + drop), (xe, cy + h / 2 + drop - 2)]
        out.append(f'<path d="{lpath(fold)}" fill="{mix(dark, "#000000", 0.45)}"/>')
    top = [(x0 + w * t, cy - h / 2 - arch * math.sin(math.pi * t)) for t in [i / 20 for i in range(21)]]
    bot = [(x0 + w * t, cy + h / 2 - arch * math.sin(math.pi * t)) for t in [i / 20 for i in range(20, -1, -1)]]
    band = top + bot
    out.append(painted(D, band, pal, seed, sdir=(0, 1), sk=0.12, angle=0, n=30, inkw=2.2, hi=0.3))
    out.append(taper([(x0 + 10, cy - h / 2 + 7 - arch * 0.1), (cx, cy - h / 2 + 7 - arch), (x1 - 10, cy - h / 2 + 7 - arch * 0.1)], 2, 2, light, 0.6))
    return "".join(out), band


def lure(D, x, y, s, seed):
    """Red and white bobber on a line."""
    out = [pline([(x, -10), (x + 2, y - s * 0.9)], "#E8E8E8", 1.4, seed, 0.8, 1)]
    out.append(painted(D, oval(x, y - s * 0.35, s * 0.5, s * 0.42, 24), ("#FFFFFF", "#F2F0EA", "#B8B0A6"), seed, sk=0.2, n=4, inkw=1.8, hi=0.5))
    out.append(painted(D, [(x - s * 0.5, y - s * 0.3)] + [(x + s * 0.5 * math.cos(math.radians(a)), y - s * 0.3 + s * 0.6 * math.sin(math.radians(a))) for a in range(180, -1, -15)][::-1] + [(x + s * 0.5, y - s * 0.3)],
                       ("#FF8A7A", "#E02A22", "#7A0A0A"), seed + 1, sk=0.2, n=4, inkw=1.8, hi=0.4))
    out.append(pline([(x, y - s * 0.9), (x, y - s * 0.7)], "#2A2430", 3, seed, 1, 1) + pline([(x, y + s * 0.3), (x, y + s * 0.5)], "#2A2430", 2, seed, 1, 1))
    out.append(taper([(x - s * 0.3, y - s * 0.45), (x - s * 0.15, y - s * 0.62)], s * 0.08, 1.5, "#FFFFFF", 0.8))
    return "".join(out)


def trout(D, cx, cy, s, seed, rot_=0, flip=1):
    """A leaping rainbow trout, side view."""
    out = [f'<g transform="translate({cx} {cy}) rotate({rot_}) scale({flip} 1) translate({-cx} {-cy})">']
    body = [(cx - s, cy), (cx - s * 0.6, cy - s * 0.28), (cx, cy - s * 0.34), (cx + s * 0.55, cy - s * 0.2), (cx + s * 0.8, cy - s * 0.04),
            (cx + s * 0.8, cy + s * 0.06), (cx + s * 0.55, cy + s * 0.2), (cx, cy + s * 0.3), (cx - s * 0.6, cy + s * 0.22)]
    tail = [(cx - s * 0.9, cy), (cx - s * 1.3, cy - s * 0.32), (cx - s * 1.2, cy), (cx - s * 1.3, cy + s * 0.3)]
    out.append(painted(D, tail, ("#B8C890", "#7A9058", "#3E5028"), seed + 1, sk=0.15, n=4, inkw=1.6, hi=0.3))
    out.append(painted(D, body, ("#D8E0B0", "#9AAA70", "#4E5E30"), seed, sdir=(0, 1), sk=0.18, angle=0, n=14, inkw=2, hi=0.4))
    cid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    out.append(f'<g {cid}><path d="M {cx - s:.1f} {cy + s * 0.02:.1f} Q {cx:.1f} {cy + s * 0.1:.1f} {cx + s * 0.8:.1f} {cy:.1f} L {cx + s * 0.8:.1f} {cy + s * 0.4:.1f} L {cx - s:.1f} {cy + s * 0.4:.1f} Z" fill="#FFF0D8" opacity="0.8"/>'
               f'<path d="M {cx - s:.1f} {cy - s * 0.04:.1f} Q {cx:.1f} {cy + s * 0.06:.1f} {cx + s * 0.7:.1f} {cy - s * 0.04:.1f}" stroke="#F27A8A" stroke-width="{s * 0.1:.1f}" fill="none" opacity="0.8"/></g>')
    out.append(specks(seed, (cx - s * 0.7, cy - s * 0.25, cx + s * 0.4, cy), ["#3E4A28"], 14, (1, 2), (0.6, 0.9)))
    out.append(f'<circle cx="{cx + s * 0.55:.1f}" cy="{cy - s * 0.06:.1f}" r="{s * 0.06:.1f}" fill="#1A1A14"/><circle cx="{cx + s * 0.54:.1f}" cy="{cy - s * 0.08:.1f}" r="{s * 0.02:.1f}" fill="#FFFFFF"/>')
    out.append(pline([(cx - s * 0.1, cy - s * 0.32), (cx - s * 0.3, cy - s * 0.5), (cx - s * 0.45, cy - s * 0.3)], "#4E5E30", 2, seed, 0.9, 1))
    out.append("</g>")
    return "".join(out)


# ================================================================ 24. GONE FISHING — vintage shield water-slide decal on a rowboat
@design("gone-fishing")
def gone_fishing():
    D = Doc("gfi")
    out = []
    # weathered lapstrake planks, pale blue paint flaking off the wood
    for i, y in enumerate(range(-20, 600, 74)):
        pl = poly([(-10, y), (610, y + 6), (610, y + 80), (-10, y + 74)], 40)
        out.append(wood_panel(D, smooth_closed(pl), (-10, y, 610, y + 80), 3 + i, pal=("#D8B888", "#B08A5A", "#6A4E30")))
        paint = smooth_closed(jitter(poly([(-10, y + 4), (610, y + 10), (610, y + 76), (-10, y + 70)], 30), i, 3))
        out.append(f'<path d="{paint}" fill="#8EC0CC"/>')
        out.append(strokes(D.nid(), paint, (-60, y, 610, y + 80), ["#B8DCE4", "#5A8E9C", "#A8D0DA"], 10 + i, n=120, angle=0, length=(30, 110), width=(2, 6), opacity=(0.2, 0.5), curve=0.05))
        rnd = random.Random(20 + i)
        for _ in range(3):
            fx, fy = rnd.uniform(0, 600), rnd.uniform(y + 14, y + 62)
            out.append(f'<path d="{blob(fx, fy, rnd.uniform(10, 34), rnd.uniform(4, 10), rnd.randint(0, 999), 0.35, 10)}" fill="#B08A5A"/>'
                       + ink(blob(fx, fy, rnd.uniform(10, 34), rnd.uniform(4, 10), rnd.randint(0, 999), 0.35, 10), "#E8F4F6", 1.2, i, 1, 0.5))
        out.append(taper([(-10, y + 74), (610, y + 80)], 5, 5, "#2A3A40", 0.45) + taper([(-10, y + 3), (610, y + 9)], 2, 2, "#FFFFFF", 0.5))
        out.append(rivets(40 + (i % 2) * 140, 600, y + 72, 280, "#6A5A4A", "#E8D8C0"))
    # bobber hanging into the frame top-right
    out.append(lure(D, 520, 86, 34, 30))
    # ---- shield decal
    top_y, side_y, tip = 136, 380, (300, 532)
    corners = [(112, top_y + 22), (134, top_y), (232, top_y), (300, top_y - 22), (368, top_y), (466, top_y), (488, top_y + 22)]
    right = [(488, side_y)] + [(488 - (488 - 300) * t ** 1.4, side_y + (tip[1] - side_y) * math.sin(t * math.pi / 2)) for t in [i / 10 for i in range(1, 11)]]
    left = [(112 + (300 - 112) * t ** 1.4, side_y + (tip[1] - side_y) * math.sin(t * math.pi / 2)) for t in [i / 10 for i in range(10, 0, -1)]] + [(112, side_y)]
    pts = poly(corners, 12)[:-1] if False else []
    for k in range(len(corners) - 1):
        a, b = corners[k], corners[k + 1]
        n = max(1, int(math.dist(a, b) / 12))
        pts += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n)]
    pts += [(488, y) for y in range(top_y + 22, side_y, 14)] + right[:-1] + left[1:] + [(112, y) for y in range(side_y, top_y + 22, -14)]
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#F6EBD0", "#EFE0BE", "#B89A6A"), 11, fade=0.12)
    scene = [sky(D, [(0, "#F28A5A"), (0.45, "#FFC07A"), (0.7, "#FFE2A8")], 12, 600, ["#FFD0A0", "#F2A07A"], 30)]
    scene.append(sun_disc(D, 360, 286, 46, ("#FFFCE0", "#FFE070", "#FFB040"), 13, glow_col="#FFE8A0", glow_r=2.4, strokes_n=16))
    scene.append(hill(D, ridge([(80, 290), (180, 262), (260, 284), (380, 258), (520, 286)], 14, 8), 600, ("#A87A9A", "#7A5A80", "#4A3A5A"), 14, inkw=0))
    for i in range(18):
        x = 96 + i * 22 + (i % 3) * 4
        scene.append(pine_tree_small(x, 304, 30 + (i * 13) % 26, "#3A2E4A", i + 40))
    scene.append(f'<rect x="80" y="302" width="440" height="240" fill="{D.lin([(0, "#E89A7A"), (0.4, "#8A6A9A"), (1, "#3A4A7A")])}"/>')
    for k in range(7):
        w = 60 - k * 7
        scene.append(taper([(360 - w, 312 + k * 9), (360 + w, 312 + k * 9)], 3, 3, "#FFE8A8", 0.75))
    scene.append(wave_lines(15, (100, 330, 500, 420), ["#FFD8B0", "#B8A8D0"], 26, (14, 34), 1.6))
    # rowboat with a fisherman, line arcing out to a leaping trout
    scene.append(f'<path d="M 166 340 L 262 340 L 250 356 L 178 356 Z" fill="#2A2238"/>')
    scene.append(f'<path d="{blob(206, 326, 10, 15, 16, 0.1, 10)}" fill="#2A2238"/><circle cx="206" cy="306" r="7" fill="#2A2238"/>'
                 f'<path d="M 196 302 Q 206 290 218 302 Z" fill="#2A2238"/><path d="M 192 304 L 222 300" stroke="#2A2238" stroke-width="3"/>')
    scene.append(pline([(214, 318), (262, 262)], "#2A2238", 2.6, 17, 1, 1))
    scene.append(f'<path d="M 262 262 Q 300 250 312 312" stroke="#2A2238" stroke-width="1.4" fill="none" opacity="0.8"/>')
    scene.append(taper([(150, 358), (280, 360)], 2, 2, "#FFE8C8", 0.5))
    scene.append(trout(D, 314, 330, 26, 18, rot_=-30, flip=-1))
    scene.append(f'<path d="M 296 352 q 18 -6 36 0" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.8"/>')
    cid = D.clip(f'<path d="{smooth_closed(offset(pts, -16))}"/>')
    scene.append(f'<rect x="60" y="398" width="480" height="200" fill="#F2E4C4"/>')
    scene.append(strokes(D.nid(), "M 60 398 L 540 398 L 540 600 L 60 600 Z", (20, 398, 540, 600), ["#FFF6E0", "#D8C49A"], 25, n=40, angle=0, length=(30, 90), width=(2, 6), opacity=(0.1, 0.3)))
    c = [f'<g {cid}>{"".join(scene)}</g>',
         ink(smooth_closed(offset(pts, -16)), "#5A3A1A", 3, 19, 1, 0.9),
         f'<path d="{smooth_closed(offset(pts, -8))}" fill="none" stroke="#C0532C" stroke-width="3"/>']
    c.append(small(300, 202, "ESTABLISHED: TODAY", BEBAS, 22, "#5A3A1A", max_w=230, ls=4))
    c.append(hbar(D, 190, 410, 210, 2.5, "#5A3A1A", 20))
    out.append(sticker(D, pts, face, "".join(c), rot_=3, seed=21, wear=1.1))
    # banner across the shield (printed as part of the decal), then the lettering
    b, band = banner(D, 300, 408, 400, 84, ("#3A6A9A", "#1F4A78", "#0E2648"), 22, tail=50, drop=14, arch=12)
    out.append(f'<g transform="rotate(3 300 334)">{b}' + vt(D, 300, 418, "GONE FISHING", ANTON, 58, "#FFF4DE", 23, max_w=360, ls=4, shadow="#0E2648", soff=(0.03, 0.04))
               + small(300, 484, "back whenever", SERIF_IT, 27, "#5A3A1A", max_w=170) + "</g>")
    return finish(D, out, 24, INK, 0.6)


def brick_wall(D, seed, y0=-10, y1=610, bh=34, bw=82, cols=("#C8664A", "#B4523A", "#D87A5A", "#A8463A", "#C25E48"), mortar="#E8D8C4"):
    rnd = random.Random(seed)
    out = [f'<rect x="-10" y="{y0}" width="620" height="{y1 - y0}" fill="{mortar}"/>']
    row = 0
    y = y0
    while y < y1:
        x = -10 - (bw / 2 if row % 2 else 0)
        while x < 610:
            w = bw - 6
            pts = rrect(x + 3, y + 3, x + w, y + bh - 3, 3, 12)
            col = rnd.choice(cols)
            d = smooth_closed(jitter(pts, rnd.randint(0, 999), 0.8))
            out.append(f'<path d="{d}" fill="{col}"/>')
            out.append(f'<path d="{d}" fill="{D.lin([(0, "#FFFFFF", 0.12), (0.5, "#FFFFFF", 0), (1, "#3A1A10", 0.18)], key="brk")}"/>')
            for _ in range(3):
                sx, sy = rnd.uniform(x + 6, x + w - 6), rnd.uniform(y + 6, y + bh - 8)
                out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{rnd.uniform(0.8, 2):.1f}" fill="{rnd.choice(["#7A3020", "#F2A080"])}" opacity="0.5"/>')
            x += bw
        y += bh
        row += 1
    return "".join(out)


def rose(D, cx, cy, r, seed, pal=("#FFC0CC", "#F27A96", "#A83A5A")):
    out = [painted(D, blob_pts(cx, cy, r, r * 0.92, seed, 0.08, 14), pal, seed, sdir=(0.4, 0.7), sk=0.2, n=6, inkw=1.6, hi=0.4, inkc=pal[2])]
    for k, rr in enumerate((0.7, 0.45, 0.22)):
        a0 = seed * 40 + k * 70
        out.append(f'<path d="M {cx + r * rr * math.cos(math.radians(a0)):.1f} {cy + r * rr * math.sin(math.radians(a0)):.1f} A {r * rr:.1f} {r * rr:.1f} 0 1 1 {cx + r * rr * math.cos(math.radians(a0 + 250)):.1f} {cy + r * rr * math.sin(math.radians(a0 + 250)):.1f}" '
                   f'stroke="{pal[2]}" stroke-width="{max(1.4, r * 0.1):.1f}" fill="none" stroke-linecap="round" opacity="0.7"/>')
    return "".join(out)


def ivy_leaf(D, cx, cy, s, ang, seed, pal=("#8AC070", "#4E8A3E", "#24502A")):
    pts = rot(blob_pts(cx + s * 0.5 * math.cos(math.radians(ang)), cy + s * 0.5 * math.sin(math.radians(ang)), s * 0.55, s * 0.3, seed, 0.08, 12, ang), cx, cy, 0)
    out = painted(D, pts, pal, seed, sk=0.2, angle=ang, n=3, inkw=1.4, hi=0.35, inkc=pal[2])
    out += pline([(cx, cy), (cx + s * 0.9 * math.cos(math.radians(ang)), cy + s * 0.9 * math.sin(math.radians(ang)))], pal[2], 1.2, seed, 0.7, 1)
    return out


def rose_vine(D, pts, seed, n_leaves=18, n_roses=5, pal=("#FFC0CC", "#F27A96", "#A83A5A")):
    rnd = random.Random(seed)
    sm = catmull(pts, 8)
    out = [taper(sm, 5, 2, "#4A3A20", 0.9)]
    for i in range(n_leaves):
        x, y = sm[int(rnd.uniform(0.05, 0.98) * (len(sm) - 1))]
        out.append(ivy_leaf(D, x, y, rnd.uniform(18, 28), rnd.uniform(0, 360), seed + i))
    for i in range(n_roses):
        x, y = sm[int((i + 0.5) / n_roses * (len(sm) - 1))]
        out.append(rose(D, x + rnd.uniform(-8, 8), y + rnd.uniform(-8, 8), rnd.uniform(14, 20), seed + 50 + i, pal))
    return "".join(out)


# ================================================================ 25. GRANDMA PARKING ONLY — vintage tin sign on a rose-covered brick wall
@design("grandma-parking-only")
def grandma_parking_only():
    D = Doc("gpo")
    out = [brick_wall(D, 3)]
    out.append(soft_glow(D, 120, 60, 420, "#FFF0D0", 0.35))
    out.append(f'<rect width="600" height="600" fill="{D.lin([(0, "#FFF0D8", 0.0), (0.6, "#3A1A10", 0.0), (1, "#3A1A10", 0.25)])}"/>')
    # the tin sign: portrait, rolled edge, four screws, rust blooms
    x0, y0, x1, y1 = 140, 62, 460, 538
    sp = rrect(x0, y0, x1, y1, 20, 12)
    sd = smooth_closed(sp)
    g = [f'<path d="{sd}" fill="#1A0A04" opacity="0.4" transform="translate(9 12)"/>',
         f'<path d="{sd}" fill="#1A0A04" opacity="0.2" transform="translate(16 20)"/>',
         f'<path d="{sd}" fill="#F6EEDC"/>']
    cid = D.clip(f'<path d="{sd}"/>')
    inner = [strokes(D.nid(), sd, (x0 - 40, y0, x1, y1), ["#FFFFFF", "#D8C8A8", "#E8DCC4"], 4, n=160, angle=-90, length=(30, 120), width=(2, 6), opacity=(0.1, 0.3), curve=0.05)]
    inner.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="96" fill="#C8282A"/>')
    inner.append(strokes(D.nid(), f"M {x0} {y0} L {x1} {y0} L {x1} {y0 + 96} L {x0} {y0 + 96} Z", (x0 - 40, y0, x1, y0 + 96), ["#E84A40", "#8A1414"], 5, n=50, angle=0, length=(20, 90), width=(2, 5), opacity=(0.15, 0.4)))
    inner.append(f'<rect x="{x0}" y="{y1 - 70}" width="{x1 - x0}" height="70" fill="#1F3A62"/>')
    g.append(f'<g {cid}>{"".join(inner)}</g>')
    g.append(f'<path d="{smooth_closed(rrect(x0 + 12, y0 + 12, x1 - 12, y1 - 12, 12, 12))}" fill="none" stroke="#1F3A62" stroke-width="3"/>')
    g.append(vt(D, 300, y0 + 74, "RESERVED", BEBAS, 58, "#FFF4E0", 5, max_w=240, ls=8, wob=0.1, density=0.3))
    g.append(heart_path(D, 300, y0 + 132, 20, ("#FF8A9A", "#E8423A", "#8A1414"), 6))
    g.append(vt(D, 300, y0 + 226, "GRANDMA", ANTON, 86, "#C8282A", 7, max_w=266, ls=2, shadow="#1F3A62", soff=(0.025, 0.035), wob=0.15))
    g.append(vt(D, 300, y0 + 282, "PARKING ONLY", BEBAS, 50, "#1F3A62", 8, max_w=262, ls=4, wob=0.1, density=0.3))
    g.append(hbar(D, 190, 410, y0 + 304, 3, "#C8282A", 9))
    g.append(small(300, y0 + 346, "all others will be", SERIF_IT, 30, "#1F3A62", max_w=240))
    g.append(vt(D, 300, y0 + 404, "SPOILED", ANTON, 64, "#C8282A", 10, max_w=240, ls=6, wob=0.15))
    g.append(small(300, y1 - 26, "WITH COOKIES", BEBAS, 30, "#FFF4E0", max_w=220, ls=6))
    # rust and chips around the edges and the screw holes
    holes = [(x0 + 30, y0 + 30), (x1 - 30, y0 + 30), (x0 + 30, y1 - 30), (x1 - 30, y1 - 30)]
    g.append(f'<g {cid}>' + rust(D, None, 11, n=8, corners=holes) + rust(D, None, 12, n=5, corners=[(x0 + 4, 300), (x1 - 4, 220), (300, y1 - 2)]) + "</g>")
    for hx, hy in holes:
        g.append(screw(D, hx, hy, 8, int(hx + hy)))
    rnd = random.Random(13)
    scr = "".join(f'<path d="M {(x := rnd.uniform(x0, x1)):.1f} {(y := rnd.uniform(y0, y1)):.1f} l {rnd.uniform(-20, 20):.1f} {rnd.uniform(-6, 6):.1f}" stroke="#FFFFFF" stroke-width="1.2" opacity="{rnd.uniform(0.2, 0.5):.2f}"/>' for _ in range(40))
    g.append(f'<g {cid}>{scr}<polygon points="{P([(x0 + 60, y0 - 10), (x0 + 120, y0 - 10), (x0 + 20, y1 + 10), (x0 - 40, y1 + 10)])}" fill="#FFFFFF" opacity="0.12"/></g>')
    g.append(f'<path d="{smooth_closed(rrect(x0 + 3, y0 + 3, x1 - 3, y1 - 3, 18, 12))}" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.5"/>')
    g.append(ink(sd, "#3A2A20", 2.4, 14, 1, 0.75))
    out.append(f'<g transform="rotate(2 300 300)">{"".join(g)}</g>')
    # climbing roses over the corner of the sign
    out.append(rose_vine(D, [(-20, 600), (40, 470), (70, 360), (60, 240), (110, 130), (190, 60), (260, 20)], 15, n_leaves=26, n_roses=6))
    out.append(rose_vine(D, [(620, 560), (560, 500), (530, 420), (556, 330)], 16, n_leaves=12, n_roses=3))
    return finish(D, out, 17, INK, 0.6)


def magnet_dot(D, cx, cy, r, pal, seed):
    return (f'<circle cx="{cx + 2:.1f}" cy="{cy + 3:.1f}" r="{r:.1f}" fill="#1A1008" opacity="0.3"/>'
            + painted(D, oval(cx, cy, r, r, 24), pal, seed, sdir=(0.5, 0.7), sk=0.22, n=4, inkw=1.6, hi=0.5)
            + f'<circle cx="{cx - r * 0.35:.1f}" cy="{cy - r * 0.35:.1f}" r="{r * 0.22:.1f}" fill="#FFFFFF" opacity="0.8"/>')


def kid_drawing(D, x0, y0, w, h, seed, rot_=0):
    """Crayon drawing on paper: a sun, a house, a stick family and grass."""
    rnd = random.Random(seed)
    cx, cy = x0 + w / 2, y0 + h / 2
    out = [f'<g transform="rotate({rot_} {cx} {cy})">']
    pp = rrect(x0, y0, x0 + w, y0 + h, 2, 20)
    out.append(f'<path d="{smooth_closed(pp)}" fill="#1A1008" opacity="0.25" transform="translate(4 6)"/>')
    out.append(f'<path d="{smooth_closed(jitter(pp, seed, 0.6))}" fill="#FFFDF6"/>')
    for k in range(1, 6):
        out.append(f'<path d="M {x0 + 6} {y0 + h * k / 6:.1f} L {x0 + w - 6} {y0 + h * k / 6:.1f}" stroke="#A8C8E8" stroke-width="1" opacity="0.6"/>')

    def crayon(pts, col, w_=4):
        return f'<path d="{smooth_open(jitter(pts, rnd.randint(0, 999), 1.2))}" fill="none" stroke="{col}" stroke-width="{w_}" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>'
    sx, sy = x0 + w * 0.8, y0 + h * 0.2
    out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{w * 0.08:.1f}" fill="#FFD23A" opacity="0.9"/>')
    for k in range(8):
        a = math.radians(k * 45)
        out.append(crayon([(sx + w * 0.11 * math.cos(a), sy + w * 0.11 * math.sin(a)), (sx + w * 0.16 * math.cos(a), sy + w * 0.16 * math.sin(a))], "#F2A20A", 3))
    hx, hy = x0 + w * 0.3, y0 + h * 0.78
    out.append(crayon([(hx - w * 0.14, hy), (hx - w * 0.14, hy - h * 0.26), (hx + w * 0.14, hy - h * 0.26), (hx + w * 0.14, hy), (hx - w * 0.14, hy)], "#E8423A"))
    out.append(crayon([(hx - w * 0.18, hy - h * 0.24), (hx, hy - h * 0.44), (hx + w * 0.18, hy - h * 0.24)], "#3A6AD0"))
    out.append(crayon([(hx - w * 0.03, hy), (hx - w * 0.03, hy - h * 0.12), (hx + w * 0.04, hy - h * 0.12), (hx + w * 0.04, hy)], "#7A4A24", 3))
    for i, (px, col) in enumerate(((0.58, "#7A5AD0"), (0.7, "#E8423A"), (0.8, "#2AA59A"))):
        fx = x0 + w * px
        hh = h * (0.2 if i < 2 else 0.14)
        fy = hy
        out.append(f'<circle cx="{fx:.1f}" cy="{fy - hh - w * 0.03:.1f}" r="{w * 0.03:.1f}" fill="none" stroke="{col}" stroke-width="3"/>')
        out.append(crayon([(fx, fy - hh), (fx, fy - hh * 0.4)], col, 3) + crayon([(fx - w * 0.03, fy), (fx, fy - hh * 0.4), (fx + w * 0.03, fy)], col, 3)
                   + crayon([(fx - w * 0.04, fy - hh * 0.75), (fx + w * 0.04, fy - hh * 0.75)], col, 3))
    out.append(crayon([(x0 + 8, y0 + h * 0.86), (x0 + w * 0.5, y0 + h * 0.84), (x0 + w - 8, y0 + h * 0.87)], "#4EAA3E", 6))
    out.append("</g>")
    return "".join(out)


def letter_magnet(D, x, y, ch, col, seed, size=54, rot_=0):
    return (f'<g transform="rotate({rot_} {x} {y})">'
            f'<text x="{x + 3}" y="{y + 4}" text-anchor="middle" {ANTON} font-size="{size}" fill="#1A1008" opacity="0.3">{ch}</text>'
            f'<text x="{x}" y="{y}" text-anchor="middle" {ANTON} font-size="{size}" fill="{col}" stroke="{mix(col, "#000000", 0.35)}" stroke-width="2">{ch}</text>'
            f'<text x="{x - 2}" y="{y - 2}" text-anchor="middle" {ANTON} font-size="{size}" fill="none" stroke="#FFFFFF" stroke-width="1.4" opacity="0.5">{ch}</text></g>')


# ================================================================ 26. IF YOU CAN READ THIS — a bumper strip stuck on a retro fridge door
@design("if-you-can-read-this")
def if_you_can_read_this():
    D = Doc("iyc")
    out = []
    door = "M -10 -10 L 610 -10 L 610 610 L -10 610 Z"
    out.append(car_paint(D, door, (0, 0, 600, 600), ("#D8F2EA", "#A8DCCC", "#5A9A8A"), 3, sky_band=(0.0, 0.0), angle=-90, tex=0.5))
    out.append(f'<rect width="600" height="600" fill="{D.lin([(0, "#FFFFFF", 0.0), (0.12, "#FFFFFF", 0.35), (0.2, "#FFFFFF", 0.0), (0.75, "#2A5A50", 0.0), (1, "#2A5A50", 0.2)], 0, 0, 1, 0)}"/>')
    # chrome lever handle on the right edge, a chrome trim strip across the top
    out.append(taper([(-10, 34), (610, 34)], 14, 14, "#E8EEF2") + taper([(-10, 30), (610, 30)], 3, 3, "#FFFFFF", 0.9) + pline([(-10, 42), (610, 42)], "#3A6A60", 1.4, 3, 0.5, 1))
    for y in (110, 290):
        out.append(painted(D, rrect(566, y - 14, 620, y + 14, 8, 6), CHROME, y, sdir=(0.3, 1), sk=0.2, n=4, inkw=2, hi=0.6))
    hb = rrect(548, 96, 584, 304, 18, 10)
    out.append(f'<path d="{smooth_closed(hb)}" fill="#1A1008" opacity="0.28" transform="translate(-10 12)"/>')
    out.append(painted(D, hb, CHROME, 4, sdir=(1, 0.1), sk=0.25, angle=-90, n=14, inkw=2.2, hi=0.6))
    out.append(taper([(558, 112), (556, 200), (558, 290)], 4, 4, "#FFFFFF", 0.9) + taper([(576, 120), (578, 280)], 3, 3, "#5A6470", 0.5))
    # stuff on the door: a crayon drawing, letter magnets, a grocery list
    out.append(kid_drawing(D, 64, 66, 190, 150, 5, rot_=-5))
    out.append(magnet_dot(D, 158, 72, 13, ("#FFB0B8", "#F27A8A", "#A83A4A"), 6))
    lp = rrect(332, 74, 500, 236, 2, 20)
    out.append(f'<g transform="rotate(4 416 155)"><path d="{smooth_closed(lp)}" fill="#1A1008" opacity="0.22" transform="translate(4 6)"/>'
               f'<path d="{smooth_closed(jitter(lp, 7, 0.5))}" fill="#FFF6C8"/>'
               + "".join(f'<path d="M 344 {116 + k * 30} L 488 {116 + k * 30}" stroke="#E8C870" stroke-width="1.2"/>' for k in range(4))
               + small(416, 108, "groceries", SERIF_IT, 24, "#C8282A", max_w=140)
               + small(350, 140, "milk", SERIF_IT, 22, "#2A3A6A", anchor="start") + small(350, 170, "eggs", SERIF_IT, 22, "#2A3A6A", anchor="start")
               + small(350, 200, "snacks!!!", SERIF_IT, 22, "#2A3A6A", anchor="start")
               + f'<path d="M 344 132 L 396 136" stroke="#2A3A6A" stroke-width="2"/></g>')
    out.append(magnet_dot(D, 416, 80, 12, ("#FFE89A", "#F2C230", "#A8740A"), 8))
    out.append(letter_magnet(D, 120, 556, "H", "#E8423A", 9, 58, -8) + letter_magnet(D, 162, 552, "I", "#2E8AD0", 10, 58, 6) + letter_magnet(D, 196, 560, "!", "#FFC93C", 11, 58, 12))
    # ---- the bumper strip
    pts = rrect(52, 286, 548, 470, 14)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#FFFDF4", "#FBF4E2", "#D8C8A8"), 12, fade=0.12)
    c = [hbar(D, 40, 560, 286, 16, "#2E5AA8", 13), hbar(D, 40, 560, 454, 16, "#2E5AA8", 14),
         hbar(D, 40, 560, 306, 4, "#E8423A", 15), hbar(D, 40, 560, 444, 4, "#E8423A", 16)]
    c.append(vt(D, 300, 352, "IF YOU CAN READ THIS", BEBAS, 52, "#2E5AA8", 17, max_w=430, ls=5, wob=0.15, density=0.3))
    c.append(vt(D, 300, 418, "CLOSE THE FRIDGE!", ANTON, 70, "#E8423A", 18, max_w=440, ls=2, shadow="#2E5AA8", soff=(0.025, 0.035), wob=0.2))
    out.append(sticker(D, pts, face, "".join(c), rot_=-2.5, peel=(-150, 24), seed=19))
    # label-maker tape under the sticker
    tp = rrect(242, 500, 534, 538, 3, 10)
    tape = (f'<path d="{smooth_closed(tp)}" fill="#D8302A"/>' + strokes(D.nid(), smooth_closed(tp), (200, 500, 540, 538), ["#F25A50", "#8A1414"], 21, n=30, angle=0, length=(20, 60), width=(1, 3), opacity=(0.15, 0.4))
            + emboss(388, 527, "WE'RE NOT COOLING THE KITCHEN", BEBAS, 24, "#FFFFFF", 272, ls=2, depth=0.6, hi="#FFB0A8", lo="#4A0A08"))
    out.append(sticker(D, tp, tape, "", rot_=-1.5, margin=0, shadow=(2, 3, 0.3), seed=22, wear=0.5, gloss=0.15))
    return finish(D, out, 20, INK, 0.5)


def wrench(D, x0, y0, x1, y1, seed, metal=CHROME):
    a = math.atan2(y1 - y0, x1 - x0)
    L = math.hypot(x1 - x0, y1 - y0)
    c, s_ = math.cos(a), math.sin(a)

    def T(u, v):
        return (x0 + u * c - v * s_, y0 + u * s_ + v * c)
    out = [painted(D, poly([T(L * 0.12, -8), T(L * 0.88, -8), T(L * 0.88, 8), T(L * 0.12, 8)], 14), metal, seed, sdir=(0, 1), sk=0.2, angle=math.degrees(a), n=10, inkw=2, hi=0.5)]
    for u, open_ in ((0, True), (L, False)):
        p = T(u, 0)
        r = 22 if open_ else 18
        if open_:
            jaw = [T(u - 20, -10), T(u - 18, -24), T(u + 4, -26), T(u + 22, -14), T(u + 24, 14), T(u + 4, 26), T(u - 18, 24), T(u - 20, 10), T(u - 2, 8), T(u - 2, -8)]
            out.append(painted(D, jaw, metal, seed + 1, sk=0.2, n=6, inkw=2, hi=0.5))
        else:
            out.append(painted(D, oval(p[0], p[1], r, r, 20), metal, seed + 2, sk=0.2, n=6, inkw=2, hi=0.5))
            out.append(f'<path d="{lpath([(p[0] + 9 * math.cos(math.radians(k * 60)), p[1] + 9 * math.sin(math.radians(k * 60))) for k in range(6)])}" fill="#5A4A3A"/>')
    return "".join(out)


def pegboard(D, seed, y1=210, base=("#E8C89A", "#D2AE7A", "#9A7A4E")):
    d = f"M -10 -10 L 610 -10 L 610 {y1} L -10 {y1} Z"
    out = [f'<path d="{d}" fill="{base[1]}"/>', strokes(D.nid(), d, (-60, -10, 610, y1), [base[0], base[2]], seed, n=80, angle=0, length=(40, 120), width=(2, 6), opacity=(0.1, 0.3))]
    for y in range(14, y1, 28):
        for x in range(14, 600, 28):
            out.append(f'<circle cx="{x}" cy="{y}" r="3.2" fill="#6A4E2E" opacity="0.7"/>')
    return "".join(out)


# ================================================================ 27. RUNNING ON DAD JOKES — fuel-gauge decal on a red metal toolbox
@design("running-on-dad-jokes")
def running_on_dad_jokes():
    D = Doc("rdj")
    out = [pegboard(D, 3)]
    # tools hung on the pegboard
    out.append(wrench(D, 70, 40, 230, 120, 4))
    out.append(pline([(330, 26), (330, 40)], "#5A4A3A", 3, 5, 1, 1))
    out.append(painted(D, rrect(318, 40, 342, 104, 8, 8), ("#FFB070", "#F07A22", "#A8460A"), 6, sk=0.2, n=6, inkw=1.8, hi=0.5))
    out.append(painted(D, poly([(326, 104), (334, 104), (333, 176), (327, 176)], 8), CHROME, 7, sk=0.2, n=4, inkw=1.6, hi=0.5))
    out.append(painted(D, oval(470, 76, 46, 46, 30), ("#FFE07A", "#F2B42A", "#A8740A"), 8, sk=0.2, n=8, inkw=2, hi=0.4))
    out.append(f'<circle cx="470" cy="76" r="20" fill="#3A3438"/><circle cx="470" cy="76" r="9" fill="#D2AE7A"/>')
    out.append(small(470, 66, "", BEBAS, 10, "#3A3438"))
    # red toolbox: lid with a long handle, latch, drawer seams
    out.append(cast(D, 300, 160, 340, 30, strength=0.45))
    lid = "M -10 150 L 610 150 L 610 236 L -10 236 Z"
    out.append(car_paint(D, lid, (0, 150, 600, 236), ("#FF7A6A", "#D8302A", "#7A1010"), 9, sky_band=(0.1, 0.3), tex=0.6))
    out.append(painted(D, rrect(170, 118, 430, 146, 12, 10), BLACK, 10, sdir=(0, 1), sk=0.2, n=10, inkw=2, hi=0.3))
    out.append(taper([(184, 124), (416, 124)], 3, 3, "#8A8494", 0.8))
    body = "M -10 236 L 610 236 L 610 610 L -10 610 Z"
    out.append(car_paint(D, body, (0, 236, 600, 600), ("#FF7A6A", "#D8302A", "#7A1010"), 11, sky_band=(0.02, 0.08), tex=0.6))
    out.append(taper([(-10, 238), (610, 238)], 6, 6, "#4A0808", 0.6) + taper([(-10, 244), (610, 244)], 2.5, 2.5, "#FF9A8A", 0.6))
    out.append(painted(D, rrect(272, 222, 328, 262, 8, 8), CHROME, 12, sk=0.2, n=6, inkw=2, hi=0.6))
    for y in (500, 560):
        out.append(taper([(-10, y), (610, y)], 5, 5, "#4A0808", 0.55) + taper([(-10, y + 4), (610, y + 4)], 2, 2, "#FF9A8A", 0.5))
        out.append(painted(D, rrect(250, y + 14, 350, y + 30, 8, 8), CHROME, y, sk=0.2, n=4, inkw=1.6, hi=0.6))
    rnd = random.Random(13)
    out.append("".join(f'<path d="M {rnd.uniform(0, 600):.1f} {rnd.uniform(250, 600):.1f} l {rnd.uniform(6, 26):.1f} {rnd.uniform(-3, 3):.1f}" stroke="#FFC0B0" stroke-width="1.4" opacity="{rnd.uniform(0.2, 0.5):.2f}"/>' for _ in range(36)))
    # ---- the gauge decal
    pts = rrect(64, 276, 536, 486, 26)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, BLACK, 14, fade=0.14)
    c = [f'<path d="{smooth_closed(rrect(78, 290, 522, 472, 16))}" fill="none" stroke="#F2C230" stroke-width="3"/>']
    gx, gy, gr = 172, 410, 78
    c.append(f'<path d="M {gx - gr - 12} {gy} A {gr + 12} {gr + 12} 0 0 1 {gx + gr + 12} {gy} Z" fill="#FFF4DE"/>')
    c.append(f'<path d="M {gx - gr - 12} {gy} A {gr + 12} {gr + 12} 0 0 1 {gx + gr + 12} {gy}" fill="none" stroke="#F2C230" stroke-width="4"/>')
    for k in range(9):
        a = math.radians(180 + k * 22.5)
        r0 = gr - (14 if k % 2 == 0 else 8)
        c.append(f'<path d="M {gx + r0 * math.cos(a):.1f} {gy + r0 * math.sin(a):.1f} L {gx + gr * math.cos(a):.1f} {gy + gr * math.sin(a):.1f}" stroke="#1E1A22" stroke-width="{3.5 if k % 2 == 0 else 2}" stroke-linecap="round"/>')
    c.append(f'<path d="M {gx + (gr - 2) * math.cos(math.radians(315)):.1f} {gy + (gr - 2) * math.sin(math.radians(315)):.1f} A {gr - 2} {gr - 2} 0 0 1 {gx + gr - 2} {gy}" fill="none" stroke="#2AA59A" stroke-width="7"/>')
    c.append(f'<path d="M {gx - gr + 2} {gy} A {gr - 2} {gr - 2} 0 0 1 {gx + (gr - 2) * math.cos(math.radians(202)):.1f} {gy + (gr - 2) * math.sin(math.radians(202)):.1f}" fill="none" stroke="#E8423A" stroke-width="7"/>')
    c.append(small(gx - gr + 22, gy - 8, "E", ANTON, 26, "#E8423A") + small(gx + gr - 22, gy - 8, "F", ANTON, 26, "#1E1A22"))
    na = math.radians(-14)
    c.append(f'<path d="M {gx - 6 * math.sin(na):.1f} {gy + 6 * math.cos(na):.1f} L {gx + (gr - 10) * math.cos(na):.1f} {gy + (gr - 10) * math.sin(na):.1f} L {gx + 6 * math.sin(na):.1f} {gy - 6 * math.cos(na):.1f} Z" fill="#E8423A"/>')
    c.append(f'<circle cx="{gx}" cy="{gy}" r="11" fill="#1E1A22"/><circle cx="{gx - 3}" cy="{gy - 3}" r="3" fill="#FFFFFF" opacity="0.6"/>')
    c.append(small(gx, gy + 40, "ALWAYS FULL", BEBAS, 22, "#F2C230", max_w=150, ls=3))
    # fuel pump pictogram inside the dial
    px, py = gx - 4, gy - 50
    c.append(f'<path d="M {px - 9} {py} L {px + 7} {py} L {px + 7} {py + 26} L {px - 9} {py + 26} Z" fill="#1E1A22"/><path d="M {px - 6} {py + 4} L {px + 4} {py + 4} L {px + 4} {py + 11} L {px - 6} {py + 11} Z" fill="#FFF4DE"/>'
             f'<path d="M {px + 7} {py + 5} L {px + 14} {py + 11} L {px + 14} {py + 24}" stroke="#1E1A22" stroke-width="3" fill="none" stroke-linecap="round"/>')
    c.append(vt(D, 392, 342, "RUNNING ON", BEBAS, 46, "#FFF4DE", 15, max_w=250, ls=6, wob=0.15, density=0.3))
    c.append(vt(D, 392, 424, "DAD JOKES", ANTON, 78, "#F2C230", 16, max_w=256, ls=2, shadow="#7A1010", soff=(0.03, 0.04)))
    c.append(small(392, 456, "no refills needed", SERIF_IT, 24, "#FFF4DE", max_w=220))
    out.append(sticker(D, pts, face, "".join(c), rot_=-2, peel=(-35, 26), seed=17))
    return finish(D, out, 18, INK, 0.6)


def winged_heart(D, cx, cy, s, seed, pal=("#FF8A9A", "#E8423A", "#8A1414"), wing=("#FFFFFF", "#F2EADC", "#B8A88A")):
    out = []
    for sg in (-1, 1):
        for k in range(4):
            L = s * (1.25 - k * 0.2)
            y = cy - s * 0.25 + k * s * 0.18
            fp = [(cx + sg * s * 0.55, y), (cx + sg * (s * 0.55 + L * 0.5), y - s * 0.32 + k * s * 0.04), (cx + sg * (s * 0.55 + L), y - s * 0.22 + k * s * 0.1),
                  (cx + sg * (s * 0.55 + L * 0.7), y + s * 0.06), (cx + sg * s * 0.55, y + s * 0.16)]
            out.append(painted(D, fp, wing, seed + k * 3 + sg, sdir=(0, 1), sk=0.18, angle=-10 * sg, n=3, inkw=1.6, hi=0.3))
    out.append(heart_path(D, cx, cy, s * 0.8, pal, seed + 20))
    out.append(taper([(cx - s * 0.42, cy - s * 0.22), (cx - s * 0.25, cy - s * 0.42)], s * 0.1, 2, "#FFFFFF", 0.8))
    return "".join(out)


# ================================================================ 28. FREE HUGS · FULL SERVICE — porcelain sign decal on a vintage gas pump
@design("free-hugs-full-service")
def free_hugs_full_service():
    D = Doc("fhf")
    out = [sky(D, [(0, "#6EC4EC"), (0.7, "#C8ECFA"), (1, "#FFF2D8")], 3, 600, ["#FFFFFF", "#9AD8F2"], 40)]
    out.append(puff_cloud(D, 90, 120, 160, 4, op=0.95) + puff_cloud(D, 530, 210, 130, 5, op=0.9))
    # station canopy edge and a tiny sign pole in the distance
    out.append(painted(D, poly([(-10, -10), (610, -10), (610, 36), (-10, 52)], 30), ("#FFFFFF", "#F2EEE6", "#B8B0A6"), 6, sdir=(0, 1), sk=0.2, angle=0, n=20, inkw=2, hi=0.4))
    out.append(stripes_in(D, smooth_closed(poly([(-10, 30), (610, 16), (610, 34), (-10, 50)], 30)), (-10, 14, 610, 52), -2, [40, 40], ["#E8423A", None], 7))
    out.append(hill(D, [(-20, 470), (300, 466), (620, 472)], 610, ("#D8C8A8", "#B8A888", "#7A6A4E"), 8, inkw=0))
    out.append(specks(9, (0, 476, 600, 600), ["#8A7A5A", "#FFFFFF", "#5A4A3A"], 260, (1, 2.6), (0.3, 0.7)))
    # the pump: rounded cream body with a red cap, chrome-framed meter window
    body = smooth_closed([(116, 610), (112, 150), (130, 86), (196, 60), (404, 60), (470, 86), (488, 150), (484, 610)])
    out.append(cast(D, 330, 590, 260, 26, strength=0.4))
    out.append(car_paint(D, body, (112, 60, 488, 610), ("#FFFBF0", "#F2E6CC", "#B8A27A"), 10, sky_band=(0.0, 0.0), angle=-90, tex=0.6))
    cid = D.clip(f'<path d="{body}"/>')
    out.append(f'<g {cid}><rect x="100" y="40" width="400" height="76" fill="#D8302A"/>'
               f'<rect x="100" y="112" width="400" height="8" fill="#FFFFFF"/>'
               f'<rect x="100" y="40" width="400" height="80" fill="{D.lin([(0, "#FFFFFF", 0.3), (0.3, "#FFFFFF", 0), (0.85, "#3A0A08", 0.0), (1, "#3A0A08", 0.3)], 0, 0, 1, 0)}"/>'
               f'<rect x="100" y="40" width="400" height="600" fill="{D.lin([(0, "#3A2A10", 0.25), (0.15, "#3A2A10", 0.0), (0.82, "#3A2A10", 0.0), (1, "#3A2A10", 0.3)], 0, 0, 1, 0)}"/></g>')
    out.append(ink(body, "#3A2A20", 2.6, 11, 1, 0.8))
    # little window with number drums
    wp = rrect(200, 132, 400, 188, 10, 8)
    out.append(painted(D, rrect(192, 124, 408, 196, 14, 8), CHROME, 12, sdir=(0.3, 1), sk=0.2, n=8, inkw=2, hi=0.6))
    out.append(f'<path d="{smooth_closed(wp)}" fill="#1E1A22"/>')
    for i, dgt in enumerate("0001"):
        x = 232 + i * 46
        out.append(f'<rect x="{x - 18}" y="138" width="36" height="44" rx="4" fill="#FFF6E0"/>'
                   + small(x, 172, dgt, BEBAS, 36, "#1E1A22", max_w=30))
    out.append(f'<polygon points="{P([(210, 132), (250, 132), (226, 188), (200, 188)])}" fill="#FFFFFF" opacity="0.25"/>')
    # hose curling out of a chrome collar on the side
    out.append(pline([(484, 286), (532, 300), (566, 380), (560, 480), (520, 610)], "#1E1A22", 16, 13, 1, 1) + pline([(486, 282), (530, 294), (560, 372)], "#6A6474", 4, 14, 0.6, 1))
    out.append(painted(D, rrect(470, 268, 500, 304, 6, 6), CHROME, 15, sk=0.2, n=4, inkw=1.8, hi=0.5))
    # ---- round porcelain sign decal
    cx, cy, R = 300, 378, 172
    pts = oval(cx, cy, R, R, 80)
    d = smooth_closed(pts)
    face = f'<path d="{d}" fill="#C8282A"/>' + f'<path d="{d}" fill="{D.rad([(0, "#E8423A"), (0.8, "#C8282A"), (1, "#8A1414")])}"/>'
    c = [f'<circle cx="{cx}" cy="{cy}" r="{R - 50}" fill="#FFF6E2"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{R - 50}" fill="{D.rad([(0, "#FFFFFF", 0.6), (0.7, "#FFFFFF", 0), (1, "#C8B48A", 0.4)], fx=0.35, fy=0.3)}"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{R - 50}" fill="none" stroke="#1F3A62" stroke-width="5"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{R - 8}" fill="none" stroke="#FFF6E2" stroke-width="3"/>']
    c.append(arc_label(D, "FULL SERVICE", cx, cy, R - 42, ANTON, 31, "#FFF6E2", ls=6, top=True))
    c.append(arc_label(D, "OPEN 24 HOURS", cx, cy, R - 18, BEBAS, 30, "#FFF6E2", ls=6, top=False))
    for sg in (-1, 1):
        c.append(star(cx + sg * (R - 29), cy, 10, "#FFF6E2"))
    c.append(winged_heart(D, cx, cy - 60, 34, 18))
    c.append(vt(D, cx, cy + 2, "FREE", BEBAS, 50, "#1F3A62", 19, max_w=170, ls=10, wob=0.1, density=0.3))
    c.append(vt(D, cx, cy + 88, "HUGS", ANTON, 80, "#C8282A", 20, max_w=200, ls=6, shadow="#1F3A62", soff=(0.025, 0.035), wob=0.15))
    # porcelain chips: bare dark steel showing through near the edge
    rnd = random.Random(21)
    for _ in range(9):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(R - 14, R - 4)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        r_ = rnd.uniform(2, 6)
        c.append(f'<path d="{blob(x, y, r_, r_ * 0.7, rnd.randint(0, 999), 0.3, 8)}" fill="#2A2430" opacity="0.85"/>'
                 f'<path d="{blob(x, y, r_ + 1.5, r_ * 0.7 + 1.5, rnd.randint(0, 999), 0.3, 8)}" fill="none" stroke="#FFF6E2" stroke-width="1" opacity="0.6"/>')
    out.append(sticker(D, pts, face, "".join(c), rot_=0, margin=8, seed=22, wear=0.7, gloss=0.16))
    return finish(D, out, 23, INK, 0.6)


def union_decal(D, shapes, margin=9, shadow=(5, 8, 0.32), vinyl=VINYL, edge=INK):
    """Die-cut margin around several overlapping shapes at once (stroke trick unions the outline)."""
    G = "".join(f'<path d="{d}"/>' for d in shapes)
    sx, sy, so = shadow
    out = []
    for k, a in ((0.45, 0.5), (1.0, 0.45), (1.7, 0.22)):
        out.append(f'<g fill="#1A1008" stroke="#1A1008" stroke-width="{2 * margin}" stroke-linejoin="round" opacity="{so * a:.2f}" transform="translate({sx * k:.1f} {sy * k:.1f})">{G}</g>')
    out.append(f'<g fill="{edge}" stroke="{edge}" stroke-width="{2 * margin + 3}" stroke-linejoin="round" opacity="0.4">{G}</g>')
    out.append(f'<g fill="{vinyl}" stroke="{vinyl}" stroke-width="{2 * margin}" stroke-linejoin="round">{G}</g>')
    return "".join(out)


def wing_shape(rx, ry, side, span=150, lift=60, depth=74, n=6):
    """One classic emblem wing: smooth leading edge sweeping up and out, scalloped feather tips below.
    Returns (outline points, list of inner feather-row polylines)."""
    tip = (rx + side * span, ry - lift)
    top = [(rx, ry - 18), (rx + side * span * 0.35, ry - lift * 0.55 - 14), (rx + side * span * 0.75, ry - lift * 0.95 - 4), tip]
    top = catmull(top, 6)
    # scallops: walk from tip back to the root along a lower curve
    low = []
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        p0 = (tip[0] - side * span * t0 * 1.0, tip[1] + depth * (t0 ** 0.8) + 4)
        p1 = (tip[0] - side * span * t1 * 1.0, tip[1] + depth * (t1 ** 0.8) + 4)
        mid = ((p0[0] + p1[0]) / 2 + side * 6, (p0[1] + p1[1]) / 2 + 16 + 4 * t0)
        low += [p0, (mid[0] + side * 4, mid[1] - 2), mid, (mid[0] - side * 6, mid[1] - 4)]
    low.append((rx, ry + depth * 0.7))
    pts = top + low[1:]
    rows = []
    for k, f in enumerate((0.38, 0.66)):
        row = []
        for i in range(n + 1):
            t = i / n
            x = tip[0] - side * span * t
            y = tip[1] + depth * (t ** 0.8) * f + 4 + (lift * 0.3) * (1 - f) * t
            row.append((x, y))
        rows.append(row)
    return pts, rows


# ================================================================ 29. SUNDAY DRIVER — winged emblem decal on a powder-blue convertible
@design("sunday-driver")
def sunday_driver():
    D = Doc("sdr")
    out = [sky(D, [(0, "#8ED2F2"), (0.6, "#DDF3FB"), (1, "#FFF2D2")], 3, 260, ["#FFFFFF", "#B8E6F8"], 30)]
    out.append(puff_cloud(D, 460, 70, 170, 4, op=0.95))
    out.append(hill(D, ridge([(-20, 168), (200, 150), (420, 166), (620, 148)], 5, 8), 300, ("#C8E0A8", "#9AC07A", "#6A9050"), 5, inkw=0))
    for i, (x, r_) in enumerate(((60, 40), (140, 30), (500, 46), (580, 34))):
        out.append(dab_crown(D, x, 150 - r_ * 0.6, r_, r_ * 0.85, [("#9ACB6A", "#5E9A40", "#2E6A2A")], 6 + i, n=40, size=(6, 10), inkw=1))
        out.append(pline([(x, 150), (x, 176)], "#5A3A20", 5, i, 1, 1))
    out.append(hill(D, ridge([(-20, 196), (300, 186), (620, 200)], 7, 5), 300, ("#B0D488", "#7AAE58", "#4A7A36"), 7, inkw=1.2, inkop=0.3))
    # cockpit: cream seat back, a happy dog riding along, picnic basket
    out.append(painted(D, rrect(110, 150, 330, 270, 40, 12), ("#FFF6E2", "#F2E2C2", "#B8A27A"), 8, sdir=(0.3, 1), sk=0.15, angle=-90, n=20, inkw=2.2, hi=0.4))
    for x in range(140, 320, 36):
        out.append(pline([(x, 160), (x, 262)], "#C8B48A", 2, x, 0.6, 1))
    out.append(dog_head(D, 226, 166, 46, 9))
    out.append(painted(D, poly([(370, 200), (500, 200), (490, 270), (380, 270)], 12), ("#E8C08A", "#C8944E", "#7A5428"), 10, sdir=(0.3, 1), sk=0.15, angle=0, n=20, inkw=2, hi=0.3))
    for y in (214, 230, 246, 262):
        out.append(pline([(374, y), (496, y)], "#7A5428", 1.6, y, 0.5, 1))
    out.append(f'<path d="M 384 202 Q 435 150 486 202" stroke="#7A5428" stroke-width="7" fill="none"/>')
    out.append(stripes_in(D, smooth_closed(poly([(392, 196), (470, 196), (466, 212), (396, 212)], 10)), (392, 186, 470, 214), 45, [8, 8], ["#E8423A", "#FFFFFF"], 11))
    # the door: powder blue with a chrome spear, rounded rear fender and a whitewall
    door = smooth_closed([(-20, 262), (560, 262), (612, 290), (620, 620), (-20, 620)])
    out.append(car_paint(D, door, (0, 262, 600, 600), ("#D8EEF8", "#9ACCE6", "#4A7EA0"), 12, sky_band=(0.04, 0.16), tex=0.6))
    out.append(taper([(-20, 268), (560, 268), (612, 296)], 10, 10, "#E8EEF2") + taper([(-20, 264), (560, 264)], 3, 3, "#FFFFFF", 0.9))
    out.append(taper([(-20, 520), (300, 512), (560, 500), (600, 492)], 14, 4, "#E8EEF2") + taper([(-20, 516), (300, 508), (560, 497)], 3, 1, "#FFFFFF", 0.9))
    out.append(pline([(80, 290), (80, 500)], "#3A6A8A", 2, 13, 0.5, 1))
    out.append(painted(D, rrect(96, 300, 140, 314, 6, 6), CHROME, 14, sk=0.2, n=3, inkw=1.6, hi=0.5))
    # ---- the winged emblem
    cx, cy = 300, 384
    ov = oval(cx, cy, 138, 100, 60)
    shapes = [smooth_closed(ov)]
    wings = []
    for side in (-1, 1):
        wp, rows = wing_shape(cx + side * 114, cy - 14, side, span=124, lift=56, depth=84, n=5)
        shapes.append(smooth_closed(wp))
        wings.append((wp, rows, side))
    g = [union_decal(D, shapes, margin=8)]
    gold = ("#FFE89A", "#E8B840", "#9A6A10")
    for i, (wp, rows, side) in enumerate(wings):
        g.append(painted(D, wp, gold, 20 + i, sdir=(-side * 0.3, 1), sk=0.14, angle=-8 * side, n=30, inkw=2, hi=0.45, inkc="#7A4E08"))
        cid = D.clip(f'<path d="{smooth_closed(wp)}"/>')
        rr = []
        for k, row in enumerate(rows):
            for j in range(len(row) - 1):
                a_, b_ = row[j], row[j + 1]
                m = ((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2 + 10)
                rr.append(f'<path d="M {a_[0]:.1f} {a_[1]:.1f} Q {m[0]:.1f} {m[1]:.1f} {b_[0]:.1f} {b_[1]:.1f}" stroke="#9A6A10" stroke-width="2" fill="none" opacity="0.7"/>')
            for j in range(len(row)):
                x, y = row[j]
                rr.append(f'<path d="M {x:.1f} {y:.1f} l {side * 26:.1f} {-20 - k * 6:.1f}" stroke="#9A6A10" stroke-width="1.4" opacity="0.45"/>')
        g.append(f'<g {cid}>{"".join(rr)}</g>')
        g.append(taper(catmull([(cx + side * 110, cy - 26), (cx + side * 160, cy - 50), (cx + side * 212, cy - 62)], 4), 4, 1, "#FFF6D0", 0.8))
    face = face_fill(D, smooth_closed(ov), ov, ("#22406A", "#1F3A62", "#0C1C36"), 21, fade=0.12)
    g.append(f'<path d="{smooth_closed(ov)}" fill="#1F3A62"/>' + face)
    g.append(f'<path d="{smooth_closed(oval(cx, cy, 126, 88, 60))}" fill="none" stroke="#E8B840" stroke-width="3"/>')
    g.append(vt(D, cx, cy - 6, "Sunday", SERIF_IT, 70, "#FFF4DE", 22, max_w=214, wob=0.3, density=0.3, shadow="#0C1C36", soff=(0.02, 0.03)))
    g.append(vt(D, cx, cy + 58, "Driver", SERIF_IT, 70, "#E8B840", 23, max_w=214, wob=0.3, density=0.3, shadow="#0C1C36", soff=(0.02, 0.03)))
    g.append(sparkle(cx - 96, cy - 50, 9, "#FFF4DE") + sparkle(cx + 98, cy + 44, 7, "#FFF4DE"))
    b, _ = banner(D, cx, cy + 114, 240, 46, ("#F2705A", "#D23A2C", "#8A1A16"), 24, tail=34, drop=10, arch=8, notch=12)
    g.append(b + small(cx, cy + 118, "IN NO HURRY", BEBAS, 32, "#FFF4DE", max_w=200, ls=6))
    # wear + gloss on the whole decal
    rnd = random.Random(25)
    g.append("".join(f'<path d="M {(x := rnd.uniform(110, 490)):.1f} {(y := rnd.uniform(300, 470)):.1f} l {rnd.uniform(-14, 14):.1f} {rnd.uniform(-8, 8):.1f}" stroke="#FFFFFF" stroke-width="1.1" opacity="{rnd.uniform(0.15, 0.4):.2f}"/>' for _ in range(30)))
    out.append(f'<g transform="rotate(-3 300 380)">{"".join(g)}</g>')
    # a whitewall tyre peeking under the fender, road
    out.append(asphalt(D, 572, 26, base="#6A6470"))
    return finish(D, out, 27, INK, 0.6)


def compass_rose(D, cx, cy, r, seed, light="#F2E6CC", accent="#F28A3A", dark="#1E1C20"):
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r * 0.92:.1f}" fill="none" stroke="{light}" stroke-width="3"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{r * 0.8:.1f}" fill="none" stroke="{light}" stroke-width="1.6" stroke-dasharray="2 6"/>']
    for k in range(8):
        a = math.radians(k * 45 - 90)
        L = r * (0.86 if k % 2 == 0 else 0.5)
        w = r * (0.16 if k % 2 == 0 else 0.11)
        tip = (cx + L * math.cos(a), cy + L * math.sin(a))
        l = (cx + w * math.cos(a - math.pi / 2), cy + w * math.sin(a - math.pi / 2))
        rr = (cx + w * math.cos(a + math.pi / 2), cy + w * math.sin(a + math.pi / 2))
        out.append(f'<path d="{lpath([(cx, cy), l, tip])}" fill="{accent if k == 0 else light}"/>')
        out.append(f'<path d="{lpath([(cx, cy), tip, rr])}" fill="{mix(accent, "#000000", 0.3) if k == 0 else mix(light, "#000000", 0.35)}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.07:.1f}" fill="{dark}" stroke="{light}" stroke-width="2"/>')
    return "".join(out)


# ================================================================ 30. DON'T FOLLOW ME, I'M LOST TOO — spare tyre cover on a dusty SUV
@design("dont-follow-me-im-lost-too")
def dont_follow_me():
    D = Doc("dfm")
    out = []
    gate = "M -10 -10 L 610 -10 L 610 610 L -10 610 Z"
    out.append(car_paint(D, gate, (0, 0, 600, 600), ("#E8D8B0", "#C8B07A", "#7A6440"), 3, sky_band=(0.02, 0.1), tex=0.6))
    # dust kicked up along the lower half and mud flecks
    out.append(f'<rect y="300" width="600" height="300" fill="{D.lin([(0, "#A8885A", 0.0), (1, "#8A6A40", 0.45)])}"/>')
    out.append(specks(4, (0, 420, 600, 600), ["#6A4A28", "#8A6A40", "#5A3A1A"], 140, (1, 4), (0.3, 0.8)))
    # rear window strip at the top: reflection of a desert road
    win = smooth_closed(rrect(30, -40, 570, 70, 20))
    out.append(glass(D, win, (30, -40, 570, 70), 5, top="#F2C890", bot="#8A6A7A", refl=True))
    out.append(ink(win, "#2A2010", 3, 6, 1, 0.8))
    for x0, x1, sd in ((-30, 26, 7), (574, 630, 8)):
        out.append(painted(D, rrect(x0, 120, x1, 340, 14, 10), ("#FF8A7A", "#D8261E", "#6E0A0A"), sd, sdir=(0, 1), sk=0.2, angle=-90, n=10, inkw=2, hi=0.35))
        out.append(painted(D, rrect(x0, 340, x1, 390, 10, 8), ("#FFF6E0", "#F2E2C2", "#B8A27A"), sd + 1, sk=0.2, n=4, inkw=1.8, hi=0.4))
    # carrier bracket behind the wheel
    out.append(painted(D, poly([(200, 300), (400, 300), (400, 340), (200, 340)], 20), BLACK, 9, sk=0.2, n=8, inkw=2, hi=0.3))
    # ---- spare tyre + printed cover
    cx, cy, R = 300, 316, 236
    out.append(cast(D, cx + 14, cy + 22, R + 10, R + 6, strength=0.5))
    tire = oval(cx, cy, R + 14, R + 14, 90)
    out.append(f'<path d="{smooth_closed(tire)}" fill="#2A2628"/>')
    for k in range(48):
        a = math.radians(k * 7.5)
        p0 = (cx + (R + 2) * math.cos(a), cy + (R + 2) * math.sin(a))
        p1 = (cx + (R + 15) * math.cos(a + 0.03), cy + (R + 15) * math.sin(a + 0.03))
        out.append(f'<path d="M {p0[0]:.1f} {p0[1]:.1f} L {p1[0]:.1f} {p1[1]:.1f}" stroke="#4A4448" stroke-width="5" stroke-linecap="round"/>')
    out.append(ink(smooth_closed(tire), "#0E0A0C", 2.4, 10, 1, 0.8))
    cov = oval(cx, cy, R, R, 90)
    cd = smooth_closed(cov)
    out.append(f'<path d="{cd}" fill="#1E1C22"/>')
    out.append(f'<path d="{cd}" fill="{D.rad([(0, "#4A4652", 0.0), (0.75, "#4A4652", 0.0), (0.92, "#6A6672", 0.5), (1, "#0E0C10", 0.6)], fx=0.4, fy=0.35)}"/>')
    out.append(strokes(D.nid(), cd, (cx - R - 40, cy - R, cx + R, cy + R), ["#5A5664", "#0E0C10"], 11, n=200, angle=-30, length=(30, 90), width=(2, 6), opacity=(0.06, 0.18)))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{R - 10}" fill="none" stroke="#8A8494" stroke-width="2" stroke-dasharray="6 5" opacity="0.8"/>')
    cream, orange = "#F2E6CC", "#F28A3A"
    pr = [f'<circle cx="{cx}" cy="{cy}" r="{R - 26}" fill="none" stroke="{cream}" stroke-width="4"/>',
          f'<circle cx="{cx}" cy="{cy}" r="{R - 86}" fill="none" stroke="{cream}" stroke-width="4"/>']
    pr.append(arc_label(D, "DON'T FOLLOW ME", cx, cy, R - 74, ANTON, 44, cream, ls=5, top=True))
    pr.append(arc_label(D, "I'M LOST TOO", cx, cy, R - 40, ANTON, 44, orange, ls=7, top=False))
    for sg in (-1, 1):
        pr.append(star(cx + sg * (R - 56), cy, 11, orange))
    pr.append(compass_rose(D, cx, cy - 26, 84, 12, light=cream, accent=orange))
    # a wandering dashed trail that loops and ends in a question mark
    trail = [(cx - 96, cy + 92), (cx - 56, cy + 108), (cx - 16, cy + 86), (cx - 36, cy + 64), (cx - 58, cy + 86), (cx - 6, cy + 116), (cx + 44, cy + 104), (cx + 70, cy + 90)]
    pr.append(f'<path d="{smooth_open(trail)}" fill="none" stroke="{orange}" stroke-width="3.5" stroke-dasharray="7 6" stroke-linecap="round"/>')
    pr.append(small(cx + 90, cy + 108, "?", ANTON, 38, orange))
    # print wear: cracked, faded ink flecks
    rnd = random.Random(13)
    pr.append("".join(f'<path d="{blob(rnd.uniform(cx - R, cx + R), rnd.uniform(cy - R, cy + R), rnd.uniform(1, 3), rnd.uniform(0.6, 1.5), rnd.randint(0, 999), 0.3, 7)}" fill="#1E1C22" opacity="0.9"/>' for _ in range(160)))
    out.append(f'<g {D.clip(f"<path d=\"{cd}\"/>")}>{"".join(pr)}</g>')
    out.append(f'<polygon points="{P([(cx - R * 0.6, cy - R * 1.1), (cx - R * 0.35, cy - R * 1.1), (cx - R * 0.9, cy + R * 1.1), (cx - R * 1.15, cy + R * 1.1)])}" fill="#FFFFFF" opacity="0.07" {D.clip(f"<path d=\"{cd}\"/>")}/>')
    out.append(ink(cd, "#0E0C10", 2.4, 14, 1, 0.8))
    return finish(D, out, 15, INK, 0.6)


def heart_path(D, cx, cy, s, pal, seed):
    hp = []
    for i in range(48):
        t = 2 * math.pi * i / 48
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        hp.append((cx + x * s / 16, cy + y * s / 16))
    return painted(D, hp, pal, seed, sdir=(0.5, 0.7), sk=0.18, angle=-40, n=12, inkw=1.8, hi=0.45, curve=0.5)


def pine_tree_small(x, base, h, col, seed):
    from summer_gouache import pine_sil
    return pine_sil(x, base, h, col, seed)


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
