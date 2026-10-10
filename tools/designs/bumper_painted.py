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
from fall_gouache_a import (bbox, blooms, cast, catmull, finish, grass, hill, mix, painted, pline, qpts, ridge, shift, sky,
                            soft_glow, specks, steam_wisps, taper)
from fall_painted import Doc
from gouache import blob, blob_pts, ink, jitter, smooth_closed, smooth_open, strokes, wash
from poster import ANTON
from summer_gouache import (daisy, palm, puff_cloud, rot, seagull, sparkle, stripes_in, sun_disc, wave_lines)

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
    # cast shadow: three soft copies
    sx, sy, so = shadow
    for k, a in ((0.45, 0.5), (1.0, 0.45), (1.7, 0.22)):
        g.append(f'<path d="{od}" fill="#1A1008" opacity="{so * a:.2f}" transform="translate({sx * k:.1f} {sy * k:.1f})"/>')
    # vinyl margin
    g.append(f'<path d="{od}" fill="{vinyl}"/>')
    g.append(f'<path d="{od}" fill="{D.lin([(0, "#FFFFFF", 0.0), (1, "#B8A88A", 0.25)])}"/>')
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
    g.append(ink(od, edge_ink, 1.5, seed + 5, 1, 0.45))
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


def car_paint(D, d, box, pal, seed, sky_band=(0.1, 0.28), angle=0):
    """Glossy car paint: base gradient, broad sky reflection band, brush strokes along the panel."""
    light, base, dark = pal
    x0, y0, x1, y1 = box
    out = [f'<path d="{d}" fill="{D.lin([(0, light), (0.35, base), (1, dark)], 0, y0, 0, y1, "userSpaceOnUse")}"/>']
    out.append(strokes(D.nid(), d, (x0 - 60, y0, x1, y1), [light, dark, base], seed, n=int((x1 - x0) * (y1 - y0) / 700), angle=angle,
                       length=(40, 140), width=(3, 9), opacity=(0.1, 0.3), curve=0.06))
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
    return finish(D, out, 19, INK, 0.7)


# ================================================================ 2. HONK IF YOU'RE HAPPY — mint pickup tailgate, sunny oval
@design("honk-if-youre-happy")
def honk_if_youre_happy():
    D = Doc("hih")
    out = [sky(D, [(0, "#5AC4F0"), (1, "#D8F4FF")], 3, 90, ["#FFFFFF", "#9ADCF6"], 20)]
    out.append(puff_cloud(D, 470, 70, 170, 4, op=0.95) + puff_cloud(D, 120, 56, 120, 5, op=0.9))
    # potted plants peeking out of the truck bed
    for i, (x, s_) in enumerate(((110, 1.0), (200, 0.8), (430, 0.9))):
        for k in range(7):
            a = math.radians(-160 + k * 23)
            out.append(f'<path d="{blob(x + math.cos(a) * 26 * s_, 74 + math.sin(a) * 30 * s_, 18 * s_, 9 * s_, i * 10 + k, 0.2, 10, math.degrees(a))}" fill="{["#3FA548", "#2E8A3E", "#6ACB5A"][k % 3]}"/>')
    tg = "M -10 70 L 610 70 L 610 480 L -10 480 Z"
    out.append(car_paint(D, tg, (0, 70, 600, 480), MINT, 6, sky_band=(0.04, 0.12)))
    # top rail + stamped ridges
    out.append(painted(D, poly([(-10, 62), (610, 62), (610, 96), (-10, 96)], 30), ("#B8E8D4", "#6AC0A0", "#2E7A62"), 7, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=2, hi=0.5))
    for y in (130, 440):
        out.append(taper([(-10, y), (610, y)], 10, 10, "#5AA88C", 0.55) + taper([(-10, y - 5), (610, y - 5)], 3, 3, "#FFFFFF", 0.55))
    out.append(tail_light(D, 18, 240, 30, 8, ring=False) + tail_light(D, 582, 240, 30, 9, ring=False))
    out.append(asphalt(D, 540, 10, base="#6A6470"))
    out.append(chrome_bar(D, -40, 470, 640, 548, 11, r=18, horizon=0.45))
    # sticker: sunny oval
    pts = oval(300, 296, 262, 150, 64)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#FFE98A", "#FFC93C", "#D98E12"), 12)
    ray = []
    for k in range(18):
        a = math.radians(k * 20 + 5)
        ray.append(f'<path d="M 300 296 L {300 + 400 * math.cos(a - 0.08):.1f} {296 + 400 * math.sin(a - 0.08):.1f} L {300 + 400 * math.cos(a + 0.08):.1f} {296 + 400 * math.sin(a + 0.08):.1f} Z" fill="#FFE27A" opacity="0.55"/>')
    face += "".join(ray)
    c = [f'<path d="{smooth_closed(oval(300, 296, 246, 134, 64))}" fill="none" stroke="{NAVY[1]}" stroke-width="5"/>',
         f'<path d="{smooth_closed(oval(300, 296, 236, 125, 64))}" fill="none" stroke="{NAVY[1]}" stroke-width="1.6" stroke-dasharray="2 9" stroke-linecap="round"/>']
    c.append(bulb_horn(D, 268, 206, 54, 13))
    c.append(vt(D, 300, 306, "HONK IF", ANTON, 84, NAVY[1], 14, max_w=330, ls=6, shadow="#FFFFFF", soff=(0.03, 0.035)))
    c.append(vt(D, 300, 384, "YOU'RE HAPPY", ANTON, 76, CHERRY[1], 15, max_w=372, ls=2, shadow=NAVY[1], soff=(0.03, 0.04)))
    c.append(small(300, 420, "beep beep!", SERIF_IT, 26, NAVY[1], max_w=200))
    c.append(star(222, 412, 7, NAVY[1]) + star(378, 412, 7, NAVY[1]))
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
    for i, x in enumerate((60, 150, 470, 560)):
        out.append(f'<path d="{blob(x, 110, 50, 36, i, 0.18, 14)}" fill="#4E7A6A" opacity="0.55"/>')
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
    body = rrect(66, 232, 506, 444, 30)
    nub = [(504, 300), (540, 300), (540, 376), (504, 376)]
    pts = body[:]
    # splice the nub into the right edge
    pts = [p for p in body if not (p[0] >= 505.9 and 296 < p[1] < 380)]
    idx = next(i for i, p in enumerate(pts) if p[0] >= 505.9 and p[1] >= 380)
    nub_pts = poly([(506, 300), (530, 300), (536, 306), (536, 370), (530, 376), (506, 376)], 10)[:-1]
    nub_pts = [(506, 296)] + [(x, y) for x, y in poly([(534, 296), (544, 306), (544, 370), (534, 380)], 8)] + [(506, 380)]
    pts = pts[:idx] + nub_pts + pts[idx:]
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#3E8A5E", "#1F5E3B", "#0E3420"), 14)
    c = [f'<path d="{smooth_closed(rrect(82, 248, 490, 428, 20))}" fill="none" stroke="#F2C230" stroke-width="3"/>']
    # charge cells along the bottom: coffee beans
    c.append(vt(D, 286, 300, "POWERED BY", JOS, 40, "#FFF4D8", 15, max_w=330, ls=7))
    c.append(vt(D, 286, 384, "COFFEE", ANTON, 98, "#F2C230", 16, max_w=330, ls=6, shadow="#0E3420", soff=(0.03, 0.04)))
    c.append(vt(D, 330, 422, "& chaos", SERIF_IT, 50, "#FF8A6A", 17, max_w=200, shadow="#0E3420", soff=(0.025, 0.035), rotate=-6))
    c.append(f'<text x="522" y="352" text-anchor="middle" {ANTON} font-size="44" fill="#F2C230">+</text>')
    c.append(f'<text x="100" y="352" text-anchor="middle" {ANTON} font-size="44" fill="#F2C230">−</text>')
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
    c.append(vt(D, 300, 400, "IS A BROOM", ANTON, 84, "#1E1830", 13, max_w=400, ls=4, shadow="#FFD8A0", soff=(0.025, 0.035)))
    c.append(small(300, 436, "witchy & proud", SERIF_IT, 26, "#1E1830", max_w=220))
    c.append(star(118, 326, 9, "#1E1830") + star(482, 326, 9, "#1E1830") + star(106, 300, 5, "#1E1830") + star(494, 300, 5, "#1E1830"))
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
    pts = oval(300, 370, 252, 138, 64)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#F8F0DC", "#F2E8D0", "#C8B48A"), 14)
    c = [f'<path d="{smooth_closed(oval(300, 370, 238, 124, 64))}" fill="none" stroke="{OLIVE[1]}" stroke-width="6"/>',
         f'<path d="{smooth_closed(oval(300, 370, 228, 114, 64))}" fill="none" stroke="{OLIVE[1]}" stroke-width="1.6"/>']
    c.append(vt(D, 300, 362, "GOOD THINGS", ANTON, 74, OLIVE[2], 15, max_w=380, ls=4, shadow="#E8A848", soff=(0.025, 0.035)))
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
    # a warm lit rear window with gingham curtains
    wp = rrect(200, 120, 400, 186, 18)
    out.append(soft_glow(D, 300, 150, 170, "#FFD27A", 0.4))
    out.append(painted(D, rrect(190, 110, 410, 196, 24), CHROME, 6, sdir=(0.3, 1), sk=0.2, n=10, inkw=2, hi=0.5))
    out.append(glass(D, smooth_closed(wp), (200, 120, 400, 186), 6, top="#FFE8A0", bot="#F2A040"))
    for sg in (-1, 1):
        cp = [(300 + sg * 98, 122), (300 + sg * 56, 122), (300 + sg * 66, 150), (300 + sg * 90, 184), (300 + sg * 98, 184)]
        out.append(painted(D, cp, ("#FFC0C0", "#E86A6A", "#9A2A2A"), 7 + sg, sk=0.15, angle=-90, n=8, inkw=1.4, hi=0.3))
    out.append(pline([(204, 124), (396, 124)], "#9A2A2A", 3, 8, 0.8, 1))
    out.append(asphalt(D, 560, 7, base="#1E2236", cols=("#2A3048", "#141828", "#343A54")))
    # navy sticker
    pts = rrect(62, 196, 538, 476, 34)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, NAVY, 11)
    c = [f'<path d="{smooth_closed(rrect(78, 212, 522, 460, 22))}" fill="none" stroke="#F6EFE0" stroke-width="3" stroke-dasharray="2 9" stroke-linecap="round"/>']
    c.append(f'<path d="{smooth_closed(oval(160, 336, 76, 76))}" fill="#2E4E80"/>')
    c.append(sleeping_cat(D, 160, 340, 62, 12))
    c.append(zzz(208, 268, 30, "#FFE9B0"))
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
    # sticker: stadium pill with a rising sun die-cut on top
    pill = rrect(56, 236, 544, 494, 129, 12)
    sun_c = (300, 238)
    pts = [p for p in pill if not (p[1] < 246 and abs(p[0] - 300) < 84)]
    i0 = next(i for i, p in enumerate(pts) if p[1] < 246 and p[0] > 300 + 84 - 1)
    arc_pts = [(300 + 92 * math.cos(math.radians(a)), 238 + 92 * math.sin(math.radians(a))) for a in range(-14, -167, -8)]
    arc_pts = [(300 + 92 * math.cos(math.radians(a)), 238 + 92 * math.sin(math.radians(a))) for a in range(-166, -13, 8)]
    # insert the dome between the pill's top-left and top-right portions
    left = [p for p in pts if p[1] < 246 and p[0] < 300]
    pts2 = []
    inserted = False
    for p in pill:
        if p[1] < 246 and abs(p[0] - 300) < 90:
            if not inserted:
                pts2 += arc_pts
                inserted = True
            continue
        pts2.append(p)
    pts = pts2
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, CORAL, 12)
    rays = "".join(f'<path d="M 300 250 L {300 + 400 * math.cos(math.radians(a - 4)):.1f} {250 + 400 * math.sin(math.radians(a - 4)):.1f} L {300 + 400 * math.cos(math.radians(a + 4)):.1f} {250 + 400 * math.sin(math.radians(a + 4)):.1f} Z" fill="#FF8A72" opacity="0.6"/>' for a in range(-180, 1, 18))
    c = [rays, sun_disc(D, 300, 236, 62, ("#FFF6C0", "#FFD23A", "#F29A2A"), 13, glow_r=1.6)]
    c.append(f'<path d="{smooth_closed(rrect(72, 252, 528, 478, 113, 12))}" fill="none" stroke="#FFF4E0" stroke-width="3" stroke-dasharray="2 9" stroke-linecap="round"/>')
    c.append(vt(D, 300, 332, "do more of what", SERIF_IT, 58, "#FFF4E0", 14, max_w=360, shadow="#A82A2A", soff=(0.02, 0.035)))
    c.append(vt(D, 300, 380, "MAKES YOU", BEBAS, 48, "#5A1A2A", 15, max_w=240, ls=10))
    c.append(vt(D, 300, 464, "HAPPY", ANTON, 84, "#FFF4E0", 16, max_w=260, ls=10, shadow="#A82A2A", soff=(0.03, 0.04)))
    c.append(star(150, 430, 8, "#FFF4E0") + star(450, 430, 8, "#FFF4E0") + star(172, 454, 5, "#FFF4E0") + star(428, 454, 5, "#FFF4E0"))
    out.append(sticker(D, pts, face, "".join(c), rot_=-2, peel=(10, 26), seed=17))
    return finish(D, out, 18, INK, 0.6)


# ================================================================ 10. BE THE GOOD — teal heart sticker over a sunflower field
@design("be-the-good")
def be_the_good():
    from summer_gouache import sunflower
    D = Doc("btg")
    out = [sky(D, [(0, "#7FD3F0"), (0.7, "#D4F4FF"), (1, "#FFF6D8")], 3, 300, ["#FFFFFF", "#A8E0F4"], 30)]
    out.append(puff_cloud(D, 300, 80, 220, 4, op=0.95))
    out.append(hill(D, ridge([(-20, 200), (300, 188), (620, 204)], 5, 6), 600, ("#C8E0A0", "#9AC078", "#6A9050"), 5, inkw=0))
    rnd = random.Random(6)
    for i in range(46):
        x, y = rnd.uniform(-10, 610), rnd.uniform(205, 250)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(4, 7):.1f}" fill="#FFC21A"/><circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="#6A3A16"/>')
    out.append(hill(D, ridge([(-20, 250), (300, 240), (620, 252)], 7, 4), 600, ("#9AC86A", "#5E9A40", "#2E5E26"), 7, inkw=0))
    for i, (x, y, r_) in enumerate(((60, 300, 58), (548, 290, 62), (40, 540, 70), (560, 548, 66), (300, 580, 50))):
        out.append(pline([(x, y + r_ * 0.5), (x + 4, y + 160)], "#3E7A2E", 7, i, 1, 1))
        out.append(sunflower(D, x, y, r_, 10 + i))
    pts = rrect(64, 236, 536, 452, 40)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#7AD8D0", "#1FA6A6", "#0E6A6A"), 12)
    c = [f'<path d="{smooth_closed(rrect(78, 250, 522, 438, 28))}" fill="none" stroke="#F6EFE0" stroke-width="5"/>']
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
    c.append(vt(D, 384, 300, "BE THE", JOS, 50, "#F6EFE0", 14, max_w=220, ls=10))
    c.append(vt(D, 384, 402, "GOOD", ANTON, 120, "#FFE27A", 15, max_w=250, ls=8, shadow="#0E5050", soff=(0.03, 0.04)))
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
    out.append(painted(D, oval(470, 222, 44, 44, 30), ("#FFE27A", "#FFC93C", "#D98E12"), 9, sk=0.2, n=10, inkw=2, hi=0.45))
    out.append(f'<path d="M 434 210 Q 470 238 506 210" stroke="#E8423A" stroke-width="7" fill="none"/>')
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
    c.append(vt(D, 402, 282, "I'D RATHER BE", JOS, 40, "#1E6A9A", 20, max_w=240, ls=3))
    c.append(vt(D, 402, 352, "AT THE", BEBAS, 62, "#FF6F59", 21, max_w=240, ls=14))
    c.append(vt(D, 402, 424, "BEACH", ANTON, 90, "#1E6A9A", 22, max_w=240, ls=8, shadow="#FFC93C", soff=(0.03, 0.04)))
    c.append(hbar(D, 292, 512, 298, 3, "#FFC93C", 23))
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
    # the real dog behind the glass, nose smudge
    out.append(f'<g opacity="0.55">{dog_head(D, 500, 470, 70, 5, fur=("#C8A070", "#9A7040", "#5A3A18"), ear=("#9A7040", "#7A5028", "#4A2A10"))}</g>')
    out.append(f'<path d="{blob(500, 500, 30, 14, 6, 0.3, 12)}" fill="#FFFFFF" opacity="0.18"/>')
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
    c.append(f'<path d="{blob(300, 222, 74, 66, 11, 0.05, 16)}" fill="#FFE680"/>')
    c.append(dog_head(D, 300, 214, 62, 12))
    c.append(vt(D, 300, 370, "DOG", ANTON, 118, "#1E1A22", 13, max_w=230, ls=12))
    c.append(vt(D, 300, 428, "ON BOARD", BEBAS, 56, "#1E1A22", 14, max_w=230, ls=6))
    c.append(small(300, 468, "woof woof!", SERIF_IT, 26, "#C0320E", max_w=130))
    out.append(sticker(D, pts, face, "".join(c), rot_=4, margin=0, vinyl="#FFD21A", shadow=(6, 10, 0.4), seed=15, wear=0.8, edge_ink="#5A3A0A"))
    return finish(D, out, 16, INK, 0.5)


# ================================================================ 17. THIS CAR STOPS AT ALL YARD SALES — parked by a yard sale
@design("this-car-stops-at-all-yard-sales")
def this_car_stops_at_all_yard_sales():
    D = Doc("tcs")
    out = [sky(D, [(0, "#8ED8F8"), (1, "#E8F8FF")], 3, 200, ["#FFFFFF", "#B8E8FA"], 20)]
    out.append(puff_cloud(D, 130, 50, 150, 4, op=0.95))
    out.append(dab_tree(D, 520, 120, 80, 5) if False else "")
    out.append(f'<path d="{blob(530, 120, 90, 80, 5, 0.12, 18)}" fill="#3E7A3A"/><path d="{blob(510, 100, 60, 50, 6, 0.15, 16)}" fill="#5E9A4A"/>')
    out.append(house(D, 150, 214, 260, 120, 7))
    out.append(hill(D, [(-20, 210), (300, 206), (620, 212)], 600, ("#9AD06A", "#6AAE48", "#3E7A2E"), 8, inkw=0))
    # yard sale: table with a lamp, books, a vase; hand-painted sign on a stake
    out.append(painted(D, poly([(300, 200), (470, 200), (470, 212), (300, 212)], 12), ("#FFFFFF", "#F2EEE6", "#B8B0A6"), 9, sk=0.15, n=6, inkw=1.6, hi=0.3))
    out.append(pline([(310, 212), (306, 250)], INK, 3, 10, 0.9, 1) + pline([(460, 212), (464, 250)], INK, 3, 11, 0.9, 1))
    out.append(table_lamp(D, 330, 200, 50, 12))
    for i, (x, w_, col) in enumerate(((372, 14, "#E8423A"), (386, 12, "#2AA59A"), (398, 16, "#F2B430"))):
        out.append(painted(D, poly([(x, 200 - 34 + i * 3), (x + w_, 200 - 34 + i * 3), (x + w_, 200), (x, 200)], 6), (mix(col, "#FFFFFF", 0.3), col, mix(col, "#000000", 0.3)), 13 + i, sk=0.15, n=3, inkw=1.4, hi=0.3))
    out.append(painted(D, blob_pts(442, 186, 14, 16, 16, 0.05, 12), ("#FFC0D0", "#F48AA0", "#B04A66"), 16, sk=0.2, n=4, inkw=1.6, hi=0.4))
    out.append(daisy(D, 436, 160, 9, 17, n=8) + daisy(D, 450, 166, 8, 18, n=8))
    out.append(pline([(530, 252), (530, 186)], WOOD[2], 4, 19, 1, 1))
    sp = poly([(480, 150), (580, 150), (580, 196), (480, 196)], 10)
    out.append(painted(D, sp, ("#FFFFFF", "#FFF4E0", "#C8B490"), 20, sk=0.1, n=6, inkw=2, hi=0.3))
    out.append(small(530, 172, "YARD", BEBAS, 22, "#E8423A", max_w=90, ls=2) + small(530, 192, "SALE", BEBAS, 22, "#E8423A", max_w=90, ls=2))
    # the car: sage-green trunk with chrome bumper (seen from behind at the curb)
    car = smooth_closed([(-20, 300), (40, 254), (140, 240), (460, 240), (560, 254), (620, 300), (620, 620), (-20, 620)])
    out.append(car_paint(D, car, (0, 240, 600, 600), ("#C8DCB8", "#8EAE88", "#4A6A4A"), 21, sky_band=(0.04, 0.14)))
    out.append(taper([(-20, 302), (40, 256), (140, 242), (460, 242), (560, 256), (620, 302)], 4, 4, "#FFFFFF", 0.6))
    out.append(tail_light(D, 46, 330, 24, 22) + tail_light(D, 554, 330, 24, 23))
    out.append(asphalt(D, 572, 24))
    out.append(chrome_bar(D, -40, 380, 640, 570, 25, r=40, horizon=0.38))
    # long, classic 3:1 bumper sticker
    pts = rrect(60, 398, 540, 552, 12)
    d = smooth_closed(pts)
    face = face_fill(D, d, pts, ("#4A9A6A", "#1F6E46", "#0E3E26"), 26)
    c = [hbar(D, 60, 540, 398, 10, "#F2C230", 27), hbar(D, 60, 540, 542, 10, "#F2C230", 28)]
    c.append(vt(D, 300, 466, "THIS CAR STOPS", ANTON, 66, "#FFF4E0", 29, max_w=440, ls=4, shadow="#0E3E26", soff=(0.03, 0.04)))
    c.append(vt(D, 300, 524, "AT ALL YARD SALES", BEBAS, 52, "#F2C230", 30, max_w=420, ls=6))
    c.append(star(84, 488, 8, "#F2C230") + star(516, 488, 8, "#F2C230"))
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
    pts = poly([(58, 268), (430, 268), (548, 372), (430, 476), (58, 476)], 12)
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
    c.append(star(452, 336, 8, "#F2C230") + star(470, 372, 6, "#F2C230") + star(452, 408, 8, "#F2C230"))
    out.append(sticker(D, pts, face, "".join(c), rot_=-3, seed=20))
    return finish(D, out, 21, INK, 0.6)


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
