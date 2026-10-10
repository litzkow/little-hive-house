"""Fall, hand-painted (gouache / storybook) edition, set A.

Repaints 15 Fall magnets so they read as gouache on warm paper: organic shapes, layered washes with pooled
edges, brush strokes that follow each form, a warm brown pen line under the paint, brush-textured hand
lettering, soft glows and paper grain. Same slugs and words as fall_painted.py; new compositions.

Run from tools/designs:  python3 fall_gouache_a.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from fall_painted import Doc, MAPLE_R
from gouache import blob, blob_pts, grain, ink, jitter, paper, smooth_closed, smooth_open, strokes, wash
from paint import rough

COL = "fall"
INK = "#3A2418"        # warm brown pen line
PAPER = "#F4EAD8"
FLECK = "#8A6A4A"

# (light, base, dark) gouache palettes
RUST = ("#E8875A", "#C0532C", "#7E2E16")
PUMP = ("#F8A85A", "#E8792E", "#A8461A")
GOLD = ("#F6CE6A", "#E2A23A", "#A8701E")
CREAM = ("#FFFBF0", "#EFE3CB", "#BFA986")
SAGE = ("#B9C08E", "#7E8A54", "#4E5A30")
PLUM = ("#B0606A", "#7A3442", "#4A1A26")
BARK = ("#A07A56", "#6E4A2E", "#3E2614")

DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


# ================================================================ gouache toolkit
def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def shift(pts, dx, dy):
    return [(x + dx, y + dy) for x, y in pts]


def painted(D, pts, pal, seed, sdir=(0.7, 0.6), sk=0.16, angle=-90, n=None, slen=None, sw=None, sop=(0.16, 0.42),
            cols=None, inkc=INK, inkw=2.2, inkop=0.8, hi=0.45, hik=0.09, curve=0.2, edge=True):
    """One gouache-painted form: wash fill, shadow crescent away from the light, lit crescent, brush strokes
    following `angle`, and a hand-inked outline. pts = closed outline points."""
    light, base, dark = pal
    d = smooth_closed(pts)
    x0, y0, x1, y1 = bbox(pts)
    W, H = x1 - x0, y1 - y0
    out = [wash(d, base, seed, 3, max(0.6, W * 0.006), 0.45, edge=dark if edge else None, edge_w=max(1.2, W * 0.01))]
    cid = D.clip(f'<path d="{d}"/>')
    lx, ly = -sdir[0], -sdir[1]
    inner = []
    if sk:
        for k, op in ((sk, 0.42), (sk * 0.55, 0.3)):
            sp = shift(pts, lx * W * k, ly * H * k)
            inner.append(f'<path d="{d} {smooth_closed(sp)}" fill-rule="evenodd" fill="{dark}" opacity="{op}"/>')
    if hi:
        sp = shift(pts, -lx * W * hik, -ly * H * hik)
        inner.append(f'<path d="{d} {smooth_closed(sp)}" fill-rule="evenodd" fill="{light}" opacity="{hi}"/>')
    out.append(f'<g {cid}>{"".join(inner)}</g>')
    m = min(W, H)
    n = n or int(max(10, min(240, W * H / 90)))
    slen = slen or (0.12 * (H if abs(math.sin(math.radians(angle))) > 0.7 else W), 0.4 * (H if abs(math.sin(math.radians(angle))) > 0.7 else W))
    sw = sw or (max(0.6, m * 0.014), max(1.2, m * 0.04))
    out.append(strokes(D.nid(), d, (x0 - 4, y0 - 4, x1 + 4, y1 + 4), cols or [light, dark, base, light], seed + 1, n=n,
                       angle=angle, length=slen, width=sw, opacity=sop, curve=curve))
    if inkw:
        out.append(ink(d, inkc, inkw, seed + 2, 2, inkop))
    return "".join(out)


def pline(pts, color=INK, w=2.2, seed=1, op=0.85, passes=2):
    return ink(smooth_open(pts), color, w, seed, passes, op)


def taper(pts, w0, w1, color, op=1.0):
    """A tapered brush mark along a polyline (width w0 at start to w1 at end)."""
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = (w0 + (w1 - w0) * i / max(1, n - 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    d = smooth_closed(left + right[::-1])
    return f'<path d="{d}" fill="{color}" opacity="{op}"/>'


def letters(D, x, y, s, font, size, fill, cols, seed, ls=0, max_w=470, shadow=None, soff=(0.025, 0.04), angle=-70,
            wob=1.0, inkc=None, inkw=1.6, sop=(0.15, 0.45), density=1.0, hi=None, rot=0):
    """Hand-lettered brush word: each glyph placed by hand (tiny rotation / baseline drift), filled with
    visible brush strokes, a misregistered pen outline and an offset painted shadow."""
    fs = fit_size(s, font, size, max_w, ls)
    W = measure(s, font, fs, ls)
    rnd = random.Random(seed)
    gx = x - W / 2
    glyphs = []
    for ch in s:
        adv = measure(ch, font, fs) + ls
        if ch != " ":
            r = rnd.uniform(-2.2, 2.2) * wob
            dy = rnd.uniform(-1.2, 1.2) * wob * fs / 60
            cx = gx + adv / 2
            glyphs.append(f'<text x="{gx:.1f}" y="{y + dy:.1f}" {font} font-size="{fs}" transform="rotate({r:.1f} {cx:.1f} {y:.1f})">{esc(ch)}</text>')
        gx += adv
    G = "".join(glyphs)
    tr = f' transform="rotate({rot} {x} {y})"' if rot else ""
    out = [f'<g{tr}>']
    if shadow:
        out.append(f'<g fill="{shadow}" transform="translate({fs * soff[0]:.1f} {fs * soff[1]:.1f})">{G}</g>')
    out.append(f'<g fill="{fill}">{G}</g>')
    uid = D.nid()
    st = []
    n = int(W * fs / 200 * density) + 24
    for _ in range(n):
        px, py = rnd.uniform(x - W / 2 - 10, x + W / 2 + 10), rnd.uniform(y - fs * 0.95, y + fs * 0.25)
        L = rnd.uniform(fs * 0.12, fs * 0.42)
        ww = rnd.uniform(fs * 0.025, fs * 0.07)
        a = math.radians(angle + rnd.uniform(-12, 12))
        dx, dy = L * math.cos(a), L * math.sin(a)
        nx, ny = -math.sin(a), math.cos(a)
        mx, my = px + dx / 2, py + dy / 2
        st.append(f'<path d="M {px:.1f} {py:.1f} Q {mx + nx * ww:.1f} {my + ny * ww:.1f} {px + dx:.1f} {py + dy:.1f} Q {mx - nx * ww:.1f} {my - ny * ww:.1f} {px:.1f} {py:.1f} Z" '
                  f'fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*sop):.2f}"/>')
    if hi:
        for _ in range(int(len(s) * 2.5)):
            px, py = rnd.uniform(x - W / 2, x + W / 2), rnd.uniform(y - fs * 0.7, y - fs * 0.3)
            L = rnd.uniform(fs * 0.1, fs * 0.25)
            st.append(f'<path d="M {px:.1f} {py:.1f} l {L * 0.3:.1f} {-L:.1f}" stroke="{hi}" stroke-width="{max(1.2, fs * 0.018):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.25, 0.5):.2f}"/>')
    out.append(f'<clipPath id="{uid}">{G}</clipPath><g clip-path="url(#{uid})">{"".join(st)}</g>')
    if inkc:
        out.append(f'<g fill="none" stroke="{inkc}" stroke-width="{inkw}" stroke-linejoin="round" opacity="0.55" transform="translate(-0.8 -0.6)">{G}</g>')
    out.append("</g>")
    return "".join(out)


def label(x, y, s, font, size, fill, ls=0, max_w=420, extra=""):
    fs = fit_size(s, font, size, max_w, ls)
    xx = x + ls / 2 if ls else x
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return f'<text x="{xx:.1f}" y="{y:.1f}" text-anchor="middle" {font} font-size="{fs}"{lsa} fill="{fill}"{extra}>{esc(s)}</text>'


def ruled(x, y, s, fill, font=MONO, size=19, ls=5, line_w=38, gap=14, line=None, seed=3, max_w=380):
    fs = fit_size(s, font, size, max_w, ls)
    w = measure(s, font, fs, ls)
    mid = y - fs * 0.33
    lc = line or fill
    out = [label(x, y, s, font, fs, fill, ls, max_w)]
    for sg in (-1, 1):
        a = x + sg * (w / 2 + gap)
        b = x + sg * (w / 2 + gap + line_w)
        out.append(pline([(a, mid), ((a + b) / 2, mid + 1.2), (b, mid - 0.6)], lc, 2.2, seed + sg, 0.9))
    return "".join(out)


def sky(D, stops, seed, h=600, cols=None, n=70, angle=-3, sop=(0.06, 0.18), y0=0):
    """Painted sky: graded base + broad horizontal brush strokes + a few watercolour blooms."""
    g = D.lin(stops)
    out = [f'<rect y="{y0}" width="600" height="{h - y0}" fill="{g}"/>']
    if cols:
        d = f"M -10 {y0 - 10} L 610 {y0 - 10} L 610 {h + 10} L -10 {h + 10} Z"
        out.append(strokes(D.nid(), d, (-60, y0 - 10, 600, h), cols, seed, n=n, angle=angle, length=(80, 220), width=(5, 14), opacity=sop, curve=0.1))
    return "".join(out)


def blooms(seed, cols, n=6, box=(0, 0, 600, 600), r=(40, 110), op=(0.05, 0.12)):
    """Watercolour back-runs: soft irregular puddles with a slightly darker dried edge."""
    rnd = random.Random(seed)
    out = []
    x0, y0, x1, y1 = box
    for i in range(n):
        c = rnd.choice(cols)
        rr = rnd.uniform(*r)
        d = blob(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rr, rr * rnd.uniform(0.55, 0.9), seed * 31 + i, 0.16, 16, rnd.uniform(-30, 30))
        o = rnd.uniform(*op)
        out.append(f'<path d="{d}" fill="{c}" opacity="{o:.3f}"/><path d="{d}" fill="none" stroke="{c}" stroke-width="1.6" opacity="{o * 1.6:.3f}"/>')
    return "".join(out)


def hill(D, line, bottom, pal, seed, angle=-4, n=None, inkc=INK, inkw=2.0, inkop=0.6, sop=(0.12, 0.35), cols=None, lit=None):
    """Painted land mass below a rough top line."""
    light, base, dark = pal
    top = smooth_open(line)
    d = top + f" L {line[-1][0]:.1f} {bottom} L {line[0][0]:.1f} {bottom} Z"
    ys = [p[1] for p in line]
    out = [f'<path d="{d}" fill="{base}"/>']
    g = D.lin([(0, light, 0.55), (0.5, base, 0), (1, dark, 0.5)], 0, min(ys), 0, bottom, "userSpaceOnUse")
    out.append(f'<path d="{d}" fill="{g}"/>')
    n = n or int((line[-1][0] - line[0][0]) * (bottom - min(ys)) / 260)
    out.append(strokes(D.nid(), d, (line[0][0] - 40, min(ys) - 4, line[-1][0] + 10, bottom), cols or [light, dark, base], seed, n=n,
                       angle=angle, length=(20, 70), width=(2, 6), opacity=sop, curve=0.15))
    if lit:
        out.append(ink(top, lit, 3, seed + 4, 1, 0.5))
    if inkw:
        out.append(ink(top, inkc, inkw, seed + 5, 1, inkop))
    return "".join(out)


def ridge(pts, seed, amp=10, depth=4):
    return rough(pts, seed, amp, depth)


def dab_crown(D, cx, cy, rx, ry, pals, seed, n=60, size=(5, 11), light=(-0.6, -0.8), inkw=1.4, inkc=INK, base=True):
    """Tree crown painted as overlapping round dabs, lighter toward the light."""
    rnd = random.Random(seed)
    out = []
    if base:
        d = blob(cx, cy, rx, ry, seed, 0.14, 20)
        out.append(wash(d, pals[0][2], seed, 2, 1.2, 0.5))
    items = []
    for i in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        r = math.sqrt(rnd.random()) * 0.92
        x, y = cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r
        lt = -(math.cos(a) * light[0] + math.sin(a) * light[1]) * r      # -1 shadow .. 1 lit
        pal = rnd.choice(pals)
        col = pal[0] if lt > 0.3 else (pal[2] if lt < -0.35 else pal[1])
        s = rnd.uniform(*size)
        items.append((lt, x, y, s, col))
    for lt, x, y, s, col in sorted(items):
        out.append(f'<path d="{blob(x, y, s, s * 0.8, rnd.randint(0, 9999), 0.22, 8, rnd.uniform(0, 180))}" fill="{col}" opacity="{rnd.uniform(0.75, 1):.2f}"/>')
    if inkw:
        out.append(ink(blob(cx, cy, rx * 1.02, ry * 1.02, seed + 3, 0.16, 20), inkc, inkw, seed, 1, 0.45))
    return "".join(out)


def grass(seed, box, cols, n=120, h=(8, 20), w=1.6, lean=(-0.35, 0.35), op=(0.5, 0.95)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        hh = rnd.uniform(*h)
        l = rnd.uniform(*lean)
        out.append(f'<path d="M {x - w:.1f} {y:.1f} Q {x + l * hh * 0.4:.1f} {y - hh * 0.6:.1f} {x + l * hh:.1f} {y - hh:.1f} Q {x + l * hh * 0.4 + w * 0.3:.1f} {y - hh * 0.5:.1f} {x + w:.1f} {y:.1f} Z" '
                   f'fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*op):.2f}"/>')
    return "".join(out)


def soft_glow(D, cx, cy, r, color, strength=0.7):
    g = D.rad([(0, color, strength), (0.4, color, strength * 0.45), (1, color, 0)])
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{g}"/>'


def cast(D, cx, cy, rx, ry, color="#3A2418", strength=0.35, seed=1):
    g = D.rad([(0, color, strength), (0.65, color, strength * 0.6), (1, color, 0)])
    return f'<path d="{blob(cx, cy, rx, ry, seed, 0.05, 16)}" fill="{g}"/>'


def specks(seed, box, cols, n=40, r=(1, 3), op=(0.3, 0.8)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    return "".join(f'<circle cx="{rnd.uniform(x0, x1):.1f}" cy="{rnd.uniform(y0, y1):.1f}" r="{rnd.uniform(*r):.1f}" fill="{rnd.choice(cols)}" opacity="{rnd.uniform(*op):.2f}"/>' for _ in range(n))


# ---------------------------------------------------------------- painted leaves, pumpkins, acorns
LEAF_PALS = {"red": ("#E86A3E", "#C23A22", "#7A1E12"), "orange": ("#F8B050", "#E6772A", "#A8461A"),
             "gold": ("#FAD870", "#E8A93A", "#A8701E"), "plum": ("#C86A62", "#93384A", "#561A2A"),
             "olive": ("#C8C070", "#8E9244", "#56602A"), "brown": ("#D09A5A", "#A0662E", "#62381A")}


def _rot_pts(pts, cx, cy, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def leaf(D, kind, cx, cy, s, pal, rot=0, seed=1, inkw=None, vein="#FFE9C4", stem=True):
    """Painted leaf (maple / oak / slim): wash, darker half, strokes along the leaf, pale veins, pen outline.
    Tip points along `rot` (0 = up)."""
    if isinstance(pal, str):
        pal = LEAF_PALS[pal]
    light, base, dark = pal
    rnd = random.Random(seed)
    if kind == "maple":
        half = MAPLE_R
        pts = half + [(-x, y) for x, y in reversed(half[1:])]
        pts = [(cx + x * s, cy + y * s) for x, y in pts]
        halfp = [(cx, cy - s)] + [(cx + x * s, cy + y * s) for x, y in half[1:]] + [(cx, cy + 0.46 * s)]
        stem_p = [(cx, cy + 0.4 * s), (cx + 0.05 * s, cy + 0.7 * s), (cx - 0.04 * s, cy + 0.98 * s)]
        veins = [((cx, cy + 0.36 * s), (cx + tx * s * 0.45, cy + (ty * 0.45 + 0.18) * s), (cx + tx * s, cy + ty * s))
                 for tx, ty in ((0, -0.86), (0.84, -0.28), (-0.84, -0.28), (0.5, 0.2), (-0.5, 0.2))]
        poly = True
    elif kind == "oak":
        N = 48
        right, left = [], []
        for i in range(N + 1):
            t = i / N
            env = math.sin(math.pi * min(1.0, t * 1.02)) ** 0.75 * (0.22 + 0.22 * t)
            lobe = 0.55 + 0.45 * abs(math.sin(t * math.pi * 4.6 + 0.3))
            y = cy + s * (0.85 - 1.85 * t)
            right.append((cx + s * env * lobe, y))
            left.append((cx - s * env * lobe, y))
        pts = right + left[::-1]
        halfp = right + [(cx, cy - s), (cx, cy + 0.85 * s)]
        stem_p = [(cx, cy + 0.8 * s), (cx + 0.03 * s, cy + 0.98 * s), (cx - 0.04 * s, cy + 1.14 * s)]
        veins = [((cx, cy + 0.8 * s), (cx + 0.01 * s, cy), (cx, cy - 0.85 * s))]
        for k in range(4):
            t = 0.2 + k * 0.2
            yy = cy + s * (0.85 - 1.85 * t)
            for sg in (-1, 1):
                veins.append(((cx, yy + 0.06 * s), (cx + sg * 0.14 * s, yy), (cx + sg * 0.28 * s * (0.6 + t * 0.5), yy - 0.1 * s)))
        poly = True
    else:
        N = 22
        right, left = [], []
        for i in range(N + 1):
            t = i / N
            w = 0.36 * s * math.sin(math.pi * t) ** 0.8 * (1 - 0.25 * t)
            z = 0.035 * s if i % 2 else 0
            y = cy + s * (0.7 - 1.7 * t)
            right.append((cx + w + z, y))
            left.append((cx - w - z, y))
        pts = right + left[::-1]
        halfp = right
        stem_p = [(cx, cy + 0.7 * s), (cx + 0.03 * s, cy + 0.85 * s), (cx - 0.03 * s, cy + 1.0 * s)]
        veins = [((cx, cy + 0.7 * s), (cx + 0.02 * s, cy), (cx, cy - 0.85 * s))]
        for k in range(4):
            yy = cy + s * (0.4 - k * 0.27)
            for sg in (-1, 1):
                veins.append(((cx, yy), (cx + sg * 0.12 * s, yy - 0.06 * s), (cx + sg * 0.27 * s, yy - 0.2 * s)))
        poly = True
    pts = [(x + rnd.uniform(-0.012, 0.012) * s, y + rnd.uniform(-0.012, 0.012) * s) for x, y in pts]
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    out = [f'<g transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})">']
    if stem:
        out.append(ink(smooth_open(stem_p), dark, max(1.6, s * 0.06), seed, 1, 1))
    out.append(f'<path d="{d}" fill="{base}" stroke="{base}" stroke-width="{max(0.6, s * 0.02):.1f}" stroke-linejoin="round"/>')
    cid = D.clip(f'<path d="{d}"/>')
    hp = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in halfp) + " Z"
    blobs = "".join(f'<path d="{blob(cx + rnd.uniform(-0.5, 0.5) * s, cy + rnd.uniform(-0.6, 0.3) * s, s * rnd.uniform(0.15, 0.3), s * rnd.uniform(0.12, 0.25), rnd.randint(0, 999), 0.2, 10)}" fill="{rnd.choice([light, dark])}" opacity="{rnd.uniform(0.25, 0.5):.2f}"/>' for _ in range(3))
    st = []
    for _ in range(int(14 + s * 0.4)):
        px, py = cx + rnd.uniform(-0.9, 0.9) * s, cy + rnd.uniform(-1, 0.8) * s
        L = rnd.uniform(0.2, 0.5) * s
        ww = rnd.uniform(0.025, 0.06) * s
        a = math.atan2(py - (cy + 0.4 * s), px - cx) + rnd.uniform(-0.2, 0.2)
        dx, dy = L * math.cos(a), L * math.sin(a)
        nx, ny = -math.sin(a), math.cos(a)
        mx, my = px + dx / 2, py + dy / 2
        st.append(f'<path d="M {px:.1f} {py:.1f} Q {mx + nx * ww:.1f} {my + ny * ww:.1f} {px + dx:.1f} {py + dy:.1f} Q {mx - nx * ww:.1f} {my - ny * ww:.1f} {px:.1f} {py:.1f} Z" fill="{rnd.choice([light, dark, light])}" opacity="{rnd.uniform(0.2, 0.45):.2f}"/>')
    out.append(f'<g {cid}>{blobs}<path d="{hp}" fill="{dark}" opacity="0.32"/>{"".join(st)}</g>')
    vs = "".join(f'<path d="M {a[0]:.1f} {a[1]:.1f} Q {b[0]:.1f} {b[1]:.1f} {c[0]:.1f} {c[1]:.1f}"/>' for a, b, c in veins)
    out.append(f'<g fill="none" stroke="{vein}" stroke-width="{max(0.9, s * 0.03):.1f}" stroke-linecap="round" opacity="0.6">{vs}</g>')
    iw = inkw if inkw is not None else max(1.0, s * 0.045)
    if iw:
        out.append(ink(d, INK, iw, seed + 1, 1, 0.6))
    out.append("</g>")
    return "".join(out)


def pumpkin(D, cx, cy, w, h, pal=PUMP, seed=1, stem=("#A89A5A", "#6B5A2E", "#3E3418"), vine=True, leafc="olive", lobes=5,
            light=(-0.7, -0.6), inkw=None, cast_op=0.3, hi=True):
    """Gouache pumpkin: each lobe its own painted form (back lobes darker), vertical strokes following the
    ribs, dry-brush highlight, pen line, a twisted stem with a curling tendril."""
    lt, base, dark = pal
    out = []
    if cast_op:
        out.append(cast(D, cx + 0.08 * w, cy + 0.46 * h, 0.6 * w, 0.1 * h, strength=cast_op, seed=seed))
    if lobes == 5:
        L = [(-0.3, 0.24, 0.44, 1), (0.3, 0.24, 0.44, 1), (-0.15, 0.27, 0.49, 0), (0.15, 0.27, 0.49, 0), (0, 0.26, 0.5, 0)]
    else:
        L = [(-0.2, 0.31, 0.46, 1), (0.2, 0.31, 0.46, 1), (0, 0.29, 0.5, 0)]
    iw = inkw if inkw is not None else max(1.2, 0.016 * w)
    for k, (dx, rx, ry, back) in enumerate(L):
        pts = blob_pts(cx + dx * w, cy, rx * w, ry * h, seed + k * 7, 0.03, 18)
        # flatten the top & bottom slightly into each lobe's dimple
        side = -1 if dx < 0 else 1
        pal_k = (base, mix(base, dark, 0.45), mix(dark, "#2A1006", 0.4)) if back else pal
        out.append(painted(D, pts, pal_k, seed + k, sdir=(-light[0], -light[1]), sk=0.2 if back else 0.12, angle=-90,
                           n=int(w * h / 260) + 12, slen=(0.15 * h, 0.45 * h), sw=(0.01 * w, 0.028 * w), sop=(0.16, 0.42),
                           cols=[lt, dark, "#FFD9A0" if pal == PUMP else lt, base], inkw=iw, inkop=0.55, hi=0 if back else 0.35, hik=0.1, curve=0.3, edge=False))
    # front lobe crease shadows
    for dx in (-0.1, 0.1):
        out.append(ink(f"M {cx + dx * w:.1f} {cy - 0.42 * h:.1f} Q {cx + dx * 1.7 * w:.1f} {cy:.1f} {cx + dx * w:.1f} {cy + 0.46 * h:.1f}", dark, max(1.2, 0.02 * w), seed + 9, 1, 0.55))
    if hi:
        out.append(taper([(cx - 0.2 * w, cy - 0.3 * h), (cx - 0.25 * w, cy - 0.05 * h), (cx - 0.21 * w, cy + 0.2 * h)], max(2, 0.035 * w), 0.5, "#FFF3DC", 0.55))
        out.append(taper([(cx + 0.02 * w, cy - 0.34 * h), (cx + 0.06 * w, cy - 0.37 * h)], max(1.5, 0.02 * w), 0.5, "#FFF3DC", 0.5))
    # top dimple
    out.append(f'<path d="{blob(cx, cy - 0.42 * h, 0.12 * w, 0.045 * h, seed, 0.1, 10)}" fill="{dark}" opacity="0.7"/>')
    # stem
    sl, sb, sd = stem
    sx = cx + 0.01 * w
    sw_ = max(5, 0.08 * w)
    top = cy - 0.42 * h - 0.24 * h
    lean = 0.07 * w
    sp = [(sx - sw_ * 0.7, cy - 0.41 * h), (sx - sw_ * 0.45, cy - 0.5 * h), (sx - sw_ * 0.5 + lean * 0.6, top + 0.06 * h), (sx - sw_ * 0.45 + lean, top),
          (sx + sw_ * 0.5 + lean, top + 0.02 * h), (sx + sw_ * 0.45 + lean * 0.4, top + 0.1 * h), (sx + sw_ * 0.5, cy - 0.5 * h), (sx + sw_ * 0.8, cy - 0.41 * h)]
    out.append(painted(D, sp, stem, seed + 31, sdir=(1, 0), sk=0.25, angle=-80, n=14, slen=(0.05 * h, 0.15 * h), sw=(0.6, 1.6),
                       inkw=max(1.2, iw), inkop=0.8, hi=0.4, hik=0.15, edge=False))
    out.append(f'<path d="{blob(sx + lean, top + 0.012 * h, sw_ * 0.5, sw_ * 0.2, seed, 0.1, 10)}" fill="#D8CB98" stroke="{sd}" stroke-width="1" />')
    if vine:
        vc = LEAF_PALS[leafc][2]
        out.append(pline([(sx + sw_ * 0.6, cy - 0.46 * h), (sx + 0.14 * w, cy - 0.5 * h), (sx + 0.2 * w, cy - 0.6 * h), (sx + 0.15 * w, cy - 0.67 * h),
                          (sx + 0.11 * w, cy - 0.62 * h), (sx + 0.14 * w, cy - 0.58 * h)], vc, max(1.5, 0.014 * w), seed + 3, 0.9, 1))
        out.append(leaf(D, "slim", sx - 0.2 * w, cy - 0.52 * h, 0.15 * w, leafc, -64, seed + 5))
    return "".join(out)


def acorn(D, cx, cy, s, rot=0, seed=1):
    nut = blob_pts(cx, cy + 0.32 * s, 0.4 * s, 0.52 * s, seed, 0.03, 14)
    nut = [(x, y) if y < cy + 0.32 * s else (cx + (x - cx) * (1 - (y - cy - 0.32 * s) / (0.9 * s)), y + (y - cy - 0.32 * s) * 0.2) for x, y in nut]
    out = [f'<g transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})">',
           painted(D, nut, ("#E3B070", "#B9773A", "#6E3E18"), seed, sdir=(0.7, 0.4), sk=0.18, angle=-90, n=12,
                   slen=(0.15 * s, 0.4 * s), sw=(0.02 * s, 0.05 * s), inkw=max(1, 0.06 * s), hi=0.5, hik=0.12)]
    cap = [(cx - 0.52 * s, cy + 0.04 * s), (cx - 0.42 * s, cy - 0.2 * s), (cx - 0.18 * s, cy - 0.34 * s), (cx + 0.18 * s, cy - 0.34 * s),
           (cx + 0.42 * s, cy - 0.2 * s), (cx + 0.52 * s, cy + 0.04 * s), (cx + 0.2 * s, cy + 0.12 * s), (cx - 0.2 * s, cy + 0.12 * s)]
    out.append(painted(D, cap, ("#9A7448", "#6E4E2C", "#3E2814"), seed + 2, sdir=(0.7, 0.4), sk=0.15, angle=-20, n=10,
                       slen=(0.1 * s, 0.3 * s), sw=(0.02 * s, 0.05 * s), inkw=max(1, 0.06 * s), hi=0.3))
    cid = D.clip(f'<path d="{smooth_closed(cap)}"/>')
    hatch = "".join(f'<path d="M {cx - 0.6 * s + i * 0.13 * s:.1f} {cy + 0.12 * s:.1f} l {0.22 * s:.1f} {-0.46 * s:.1f} M {cx - 0.6 * s + i * 0.13 * s:.1f} {cy - 0.34 * s:.1f} l {0.22 * s:.1f} {0.46 * s:.1f}"/>' for i in range(11))
    out.append(f'<g {cid}><g stroke="#2E1C0E" stroke-width="{max(0.8, 0.035 * s):.1f}" opacity="0.45">{hatch}</g></g>')
    out.append(ink(f"M {cx:.1f} {cy - 0.32 * s:.1f} q {0.03 * s:.1f} {-0.18 * s:.1f} {0.15 * s:.1f} {-0.26 * s:.1f}", "#4A3018", max(1.4, 0.1 * s), seed, 1, 1))
    out.append("</g>")
    return "".join(out)


def falling(D, specs):
    """(kind, x, y, size, palette, rotation[, seed]) leaves caught mid-fall, with a faint motion trail."""
    out = []
    for i, sp in enumerate(specs):
        kind, x, y, s, pal, r = sp[:6]
        seed = sp[6] if len(sp) > 6 else i * 13 + 5
        out.append(leaf(D, kind, x, y, s, pal, r, seed))
    return "".join(out)


def leaf_hang(D, kind, ax, ay, s, pal, rot=180, seed=1, **kw):
    """Leaf whose stem end sits at (ax, ay); rot 180 = hanging straight down."""
    k = {"maple": 0.98, "oak": 1.14}.get(kind, 1.0) * s
    a = math.radians(rot)
    ox, oy = -k * math.sin(a), k * math.cos(a)
    return leaf(D, kind, ax - ox, ay - oy, s, pal, rot, seed, **kw)


def mini_pumpkin(x, y, sz, pal, seed, stem="#4A3A1A"):
    """Small distant pumpkin: three dabs, a highlight, a stem."""
    rnd = random.Random(seed)
    lt, base, dark = pal
    return (f'<path d="{blob(x, y, sz * 0.5, sz * 0.34, seed, 0.06, 10)}" fill="{dark}"/>'
            f'<path d="{blob(x + sz * 0.04, y - sz * 0.02, sz * 0.36, sz * 0.31, seed + 1, 0.08, 10)}" fill="{base}"/>'
            f'<path d="{blob(x - sz * 0.12, y - sz * 0.1, sz * 0.13, sz * 0.12, seed + 2, 0.15, 8)}" fill="{lt}" opacity="0.8"/>'
            f'<path d="M {x:.1f} {y - sz * 0.3:.1f} l {rnd.uniform(-1, 2):.1f} {-sz * 0.2:.1f}" stroke="{stem}" stroke-width="{max(1.4, sz * 0.09):.1f}" stroke-linecap="round"/>')


def apple(D, cx, cy, r, pal=("#F07A52", "#C8362A", "#7A1616"), seed=1, leafc="olive", blush="#F2C24A", light=(-0.7, -0.6), stem=True):
    pts = []
    for i in range(24):
        a = 2 * math.pi * i / 24
        k = 1 - 0.13 * max(0, -math.sin(a)) ** 6 * 2.2 + 0.03 * math.sin(3 * a)
        pts.append((cx + r * math.cos(a) * (1.02 - 0.08 * math.sin(a)), cy + r * 0.92 * math.sin(a) * k))
    # dent at the top
    pts = [(x, y + (r * 0.16 if abs(x - cx) < r * 0.2 and y < cy else 0) * (1 - abs(x - cx) / (r * 0.2))) for x, y in pts]
    out = [painted(D, jitter(pts, seed, r * 0.015), pal, seed, sdir=(-light[0], -light[1]), sk=0.2, angle=-60, n=int(r * 1.2),
                   slen=(0.2 * r, 0.6 * r), sw=(0.04 * r, 0.1 * r), cols=[pal[0], pal[2], blush, pal[0]], inkw=max(1.2, r * 0.05), hi=0.35, curve=0.4)]
    out.append(taper([(cx - 0.45 * r, cy - 0.35 * r), (cx - 0.55 * r, cy - 0.05 * r), (cx - 0.45 * r, cy + 0.2 * r)], max(2, 0.1 * r), 0.5, "#FFF6E6", 0.6))
    if stem:
        out.append(ink(f"M {cx:.1f} {cy - 0.7 * r:.1f} q {0.04 * r:.1f} {-0.3 * r:.1f} {0.18 * r:.1f} {-0.45 * r:.1f}", "#4A3018", max(1.6, 0.09 * r), seed, 1, 1))
        if leafc:
            out.append(leaf(D, "slim", cx + 0.38 * r, cy - 0.98 * r, 0.42 * r, leafc, 62, seed + 3))
    return "".join(out)


def ribbon(D, cx, cy, w, h, pal, seed=1, tail=40, drop=None, bend=6):
    """Painted banner with swallow-tail ends folded behind, slightly curved."""
    light, base, dark = pal
    drop = h * 0.35 if drop is None else drop
    l, r, t, b = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    out = []
    for sg in (-1, 1):
        e = l if sg < 0 else r
        o = e + sg * tail
        tp = [(e - sg * 12, t + drop), (o, t + drop + 2), (o - sg * h * 0.3, t + drop + h / 2), (o, b + drop - 2), (e - sg * 12, b + drop)]
        out.append(painted(D, tp, (base, dark, "#2A0E06"), seed + sg, sdir=(0, 1), sk=0.1, angle=0, n=16, inkw=1.8, hi=0, edge=False))
        out.append(f'<path d="M {e:.1f} {b - 1:.1f} L {e - sg * 12:.1f} {b + drop:.1f} L {e:.1f} {b + drop - 2:.1f} Z" fill="#2A0E06" opacity="0.6"/>')
    top = [(l + i * w / 8, t + bend * math.sin(math.pi * i / 8) * -1 + 0) for i in range(9)]
    bot = [(r - i * w / 8, b - bend * math.sin(math.pi * i / 8)) for i in range(9)]
    pts = top + bot
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    out.append(f'<path d="{d}" fill="{base}"/>')
    out.append(strokes(D.nid(), d, (l - 20, t - 10, r + 20, b + 10), [light, dark, base], seed, n=int(w / 3), angle=-2, length=(30, 90),
                       width=(2, 5), opacity=(0.15, 0.4), curve=0.05))
    out.append(ink(smooth_open(top), "#FFFFFF", 2, seed, 1, 0.25))
    out.append(ink(d, INK, 2, seed + 1, 2, 0.7))
    return "".join(out)


def finish(D, out, seed, color=INK, op=1.0):
    out.append(grain(D.nid(), color, seed, op))
    return D.render(out)


# ================================================================ 1. hello fall — a leafy branch, hand-lettered
@design("hello-fall")
def hello_fall():
    D = Doc("hf")
    out = [paper(D.nid(), "#F5E9D4", FLECK, 11)]
    out.append(blooms(3, ["#E9B47A", "#D98A5A", "#E8C890"], 7, (80, 160, 520, 520), (90, 170), (0.05, 0.1)))
    # a soft painted wash behind the lettering
    wd = blob(300, 400, 250, 150, 7, 0.1, 24)
    out.append(wash(wd, "#F2D2A6", 7, 3, 4, 0.4))
    out.append(strokes(D.nid(), wd, (40, 240, 560, 560), ["#EBC28E", "#F8E2C0", "#E3B07A"], 8, n=90, angle=-18, length=(40, 110), width=(5, 12), opacity=(0.18, 0.4)))
    # the branch, bowing across the top, with twigs
    br = [(-20, 92), (90, 104), (200, 98), (300, 112), (420, 100), (520, 90), (620, 74)]
    out.append(taper(br, 15, 6, "#5A3A22"))
    out.append(taper([(x, y - 2) for x, y in br], 5, 2, "#A07A56", 0.6))
    out.append(pline(br, INK, 2.2, 3, 0.7))
    twigs = [[(150, 101), (172, 124), (178, 146)], [(270, 108), (262, 132), (266, 152)], [(380, 104), (396, 128), (394, 150)],
             [(470, 95), (486, 116), (500, 134)], [(80, 103), (62, 124), (58, 140)]]
    for i, t in enumerate(twigs):
        out.append(taper(t, 5, 1.5, "#5A3A22"))
    # leaves standing up along the top of the branch
    up = [("slim", 236, 100, 26, "gold", -25), ("maple", 330, 108, 26, "orange", 10), ("slim", 118, 102, 22, "red", -40),
          ("maple", 452, 96, 26, "red", 20), ("oak", 548, 86, 22, "brown", 35), ("slim", 30, 96, 22, "olive", -30)]
    for i, (k, x, y, sz, p, r) in enumerate(up):
        out.append(leaf_hang(D, k, x, y, sz, p, r, 60 + i))
    hang = [("maple", 178, 146, 33, "red", 172), ("oak", 266, 152, 30, "gold", 186), ("maple", 394, 150, 33, "orange", 176),
            ("slim", 500, 134, 30, "olive", 196), ("maple", 58, 140, 32, "plum", 168)]
    for i, (k, x, y, sz, p, r) in enumerate(hang):
        out.append(leaf_hang(D, k, x, y, sz, p, r, 40 + i))
    out.append(pline([(330, 110), (334, 122), (336, 132)], "#4A3018", 2.4, 2) + pline([(120, 104), (118, 116), (116, 124)], "#4A3018", 2.2, 2))
    out.append(acorn(D, 338, 150, 20, -6, 5) + acorn(D, 116, 140, 17, 14, 6))
    # lettering
    out.append(letters(D, 300, 326, "hello", SERIF_IT, 128, "#5E2E18", ["#3E1C0C", "#7E4426", "#9A5A36"], 4, max_w=360,
                       shadow="#E2B07A", angle=-35, inkc=None))
    out.append(letters(D, 300, 482, "FALL", BEBAS, 216, "#C8541F", ["#E8792E", "#A8401A", "#F09A50", "#E06A28", "#B84A1C"], 5, ls=10, max_w=420,
                       shadow="#6E2A10", angle=-78, hi="#FFD9A8", inkc="#5A200C", inkw=1.8))
    out.append(ruled(300, 528, "SEPT · OCT · NOV", "#6E3A1E", size=20, ls=5, line_w=46))
    out.append(falling(D, [("maple", 90, 300, 24, "orange", -30), ("slim", 520, 300, 22, "red", 40), ("oak", 500, 520, 20, "gold", 60),
                           ("maple", 92, 500, 20, "red", 20)]))
    return finish(D, out, 9)


# ================================================================ 2. pumpkin patch — golden hour field, barn on the hill
@design("pumpkin-patch")
def pumpkin_patch():
    D = Doc("pp")
    out = [sky(D, [(0, "#F2C9A0"), (0.35, "#F6D9A8"), (0.6, "#F9E6B8")], 3, 420, ["#F8E2C0", "#EDB894", "#F6D08A"], 50)]
    out.append(soft_glow(D, 420, 320, 230, "#FFF2C8", 0.8))
    out.append(blooms(5, ["#E8A27A", "#F6D08A"], 5, (0, 0, 600, 260)))
    # far hills (pale, hazy) with dab trees
    l1 = ridge([(-20, 326), (120, 306), (260, 318), (400, 300), (620, 316)], 4, 14)
    out.append(hill(D, l1, 420, ("#D9B8B0", "#C8A0A0", "#A88290"), 4, inkw=1.2, inkop=0.35))
    for i, x in enumerate(range(10, 600, 34)):
        y = 322 + 6 * math.sin(x / 40)
        out.append(dab_crown(D, x, y - 6, 16, 11, [("#E8B890", "#D49880", "#B08088"), ("#E8C890", "#D8A880", "#B89080")], 70 + i, 14, (4, 7), inkw=0))
    # mid field with barn
    l2 = ridge([(-20, 356), (160, 344), (330, 352), (480, 340), (620, 350)], 8, 8)
    out.append(hill(D, l2, 600, ("#C8C27A", "#9AA055", "#5E6A34"), 8, angle=-2, inkw=1.8, lit="#FFF0B0"))
    # barn + silo
    bx, by = 140, 350
    out.append(cast(D, bx + 20, by + 2, 70, 8, strength=0.3))
    silo = [(bx + 60, by + 1), (bx + 60, by - 22), (bx + 60, by - 44), (bx + 60, by - 66), (bx + 78, by - 68), (bx + 96, by - 66), (bx + 96, by - 44),
            (bx + 96, by - 22), (bx + 96, by + 1), (bx + 78, by + 2)]
    out.append(painted(D, silo, ("#F0E4CE", "#D2C2A6", "#8A7A66"), 21, sdir=(1, 0), sk=0.3, angle=-90, n=18, slen=(10, 30), sw=(1, 2.4), inkw=1.6, hi=0.3))
    dome = [(bx + 58, by - 64), (bx + 62, by - 78), (bx + 78, by - 88), (bx + 94, by - 78), (bx + 98, by - 64), (bx + 78, by - 61)]
    out.append(painted(D, dome, ("#B8C0C8", "#7E8A96", "#4A525E"), 23, sdir=(1, 0.3), sk=0.25, angle=-30, n=8, inkw=1.6, hi=0.4))
    for yy in (by - 56, by - 40, by - 24):
        out.append(pline([(bx + 61, yy), (bx + 78, yy + 2), (bx + 95, yy)], "#8A7A66", 1.4, yy, 0.6, 1))
    wall = [(bx - 46, by + 2), (bx - 46, by - 40), (bx, by - 72), (bx + 46, by - 40), (bx + 46, by + 2)]
    out.append(painted(D, jitter(wall, 2, 1), ("#E0704E", "#B83A26", "#6E1A10"), 22, sdir=(-1, 0.2), sk=0.12, angle=-90, n=40, slen=(12, 30), sw=(1, 2.5), inkw=1.8, hi=0.25))
    roof = [(bx - 54, by - 36), (bx, by - 80), (bx + 54, by - 36), (bx + 48, by - 34), (bx, by - 72), (bx - 48, by - 34)]
    out.append(f'<path d="M {bx - 54} {by - 37} L {bx} {by - 80} L {bx + 54} {by - 37}" stroke="#4A3A34" stroke-width="7" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
    door = [(bx - 18, by + 2), (bx - 18, by - 32), (bx + 18, by - 32), (bx + 18, by + 2)]
    out.append(f'<path d="M {bx - 18} {by + 1} L {bx - 18} {by - 32} L {bx + 18} {by - 32} L {bx + 18} {by + 1} Z" fill="#F6EAD8"/>'
               f'<path d="M {bx - 14} {by - 2} L {bx - 14} {by - 28} L {bx + 14} {by - 28} L {bx + 14} {by - 2} Z" fill="#9A2E1E"/>')
    out.append(pline([(bx - 14, by - 28), (bx + 14, by - 2)], "#F6EAD8", 2.6, 5, 1, 1) + pline([(bx + 14, by - 28), (bx - 14, by - 2)], "#F6EAD8", 2.6, 6, 1, 1))
    out.append(f'<path d="M {bx - 8} {by - 56} L {bx + 8} {by - 56} L {bx + 8} {by - 44} L {bx - 8} {by - 44} Z" fill="#F6EAD8"/><path d="M {bx - 5} {by - 53} L {bx + 5} {by - 53} L {bx + 5} {by - 47} L {bx - 5} {by - 47} Z" fill="#3A2418"/>')
    out.append(taper([(bx - 76, by + 2), (bx - 75, by - 22)], 5, 2.5, "#4A3018"))
    out.append(dab_crown(D, bx - 76, by - 36, 30, 32, [("#F6C860", "#E2902E", "#A85A1E"), ("#F2A050", "#D0602A", "#8E3414")], 31, 46, (5, 9)))
    out.append(taper([(520, 346), (521, 316)], 6, 3, "#4A3018"))
    out.append(dab_crown(D, 520, 306, 34, 36, [("#F08A50", "#C8462A", "#7E2418"), ("#F6C860", "#E2902E", "#A85A1E")], 32, 50, (5, 9)))
    # rows of vines receding toward the barn, little pumpkins along them
    rnd = random.Random(12)
    for k in range(6):
        t = k / 5
        y = 366 + 200 * t ** 1.5
        sc = 0.18 + 0.8 * t ** 1.5
        wav = [(x, y + 3 * math.sin(x / 60 + k)) for x in range(-20, 640, 40)]
        out.append(pline(wav, "#56622E", 1.2 + 2.4 * sc, 60 + k, 0.5, 1))
        for x in range(-10, 620, int(22 + 50 * sc)):
            xx = x + rnd.uniform(-10, 10)
            yy = y + 3 * math.sin(xx / 60 + k)
            out.append(f'<path d="{blob(xx, yy - 2 * sc, 10 * sc + 3, 6 * sc + 2, rnd.randint(0, 999), 0.3, 8, rnd.uniform(-30, 30))}" fill="{rnd.choice(["#6E7E3A", "#8A9A48", "#55642C"])}" opacity="0.85"/>')
        x = rnd.uniform(-20, 20)
        while x < 620:
            sz = (14 + 46 * sc) * rnd.uniform(0.75, 1.15)
            yy = y + 3 * math.sin(x / 60 + k)
            if not (k >= 4 and 60 < x < 540):
                pal = rnd.choice([PUMP, PUMP, PUMP, GOLD, CREAM, RUST])
                if sz < 42:
                    out.append(mini_pumpkin(x, yy - sz * 0.25, sz, pal, rnd.randint(0, 999)))
                else:
                    out.append(pumpkin(D, x, yy - sz * 0.3, sz, sz * 0.66, pal, rnd.randint(0, 999), vine=False, inkw=1.2, cast_op=0.2, hi=False))
            x += sz * rnd.uniform(1.6, 3.2)
    # foreground: grass, big pumpkins, vine curls
    out.append(grass(14, (-10, 520, 610, 600), ["#5E6A34", "#7E8A44", "#A8A858", "#4A5428"], 160, (10, 26)))
    out.append(pumpkin(D, 300, 486, 196, 132, PUMP, 41, leafc="olive"))
    out.append(pumpkin(D, 128, 530, 118, 80, CREAM, 42, vine=False, leafc="sage" if False else "olive"))
    out.append(pumpkin(D, 470, 530, 108, 76, GOLD, 43, vine=True, leafc="olive"))
    out.append(pline([(-10, 560), (60, 548), (90, 566), (70, 580), (56, 570)], "#4E6A2A", 2.4, 4, 0.9, 1))
    out.append(leaf(D, "slim", 560, 570, 26, "olive", 70, 51) + leaf(D, "slim", 214, 576, 22, "olive", -70, 52))
    # birds over the sunset
    for bx_, by_, bs in ((360, 282, 7), (384, 272, 6), (404, 286, 5)):
        out.append(pline([(bx_ - bs, by_), (bx_ - bs * 0.5, by_ - bs * 0.6), (bx_, by_)], "#5A3A3A", 1.8, bx_, 0.8, 1) +
                   pline([(bx_, by_), (bx_ + bs * 0.5, by_ - bs * 0.6), (bx_ + bs, by_)], "#5A3A3A", 1.8, bx_ + 1, 0.8, 1))
    # lettering
    out.append(letters(D, 300, 120, "pumpkin", SERIF_IT, 100, "#7A2E14", ["#5A1E0A", "#9A4422", "#B85A30"], 6, max_w=380,
                       shadow="#FFF0D6", soff=(-0.02, -0.025), angle=-35))
    out.append(letters(D, 300, 242, "PATCH", BEBAS, 140, "#E26A28", ["#F49A4A", "#B8481A", "#FFB868", "#C8521E"], 7, ls=12, max_w=400,
                       shadow="#6E2A10", angle=-78, hi="#FFE2B0", inkc="#5A200C", inkw=1.8))
    return finish(D, out, 13)


# ================================================================ 3. harvest moon — a painted moon over the cornfield
def qpts(p0, p1, p2, n=8):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (i / n for i in range(n + 1))]


def corn_silhouette(x, base, h, col, seed, rim=None, lean=0.0, w=4.0, blades=7):
    """Corn stalk drawn as tapered brush marks: a stalk, arching leaf blades that droop at the tips, a tassel."""
    rnd = random.Random(seed)
    top = (x + lean * h, base - h)
    spine = qpts((x, base), (x + lean * h * 0.3, base - h * 0.5), top, 6)
    out = [taper(spine, w, w * 0.35, col)]
    if rim:
        out.append(pline([(px - w * 0.3, py) for px, py in spine[:-1]], rim, 1.2, seed, 0.55, 1))
    for i in range(blades):
        t = 0.16 + i * (0.7 / blades)
        px, py = x + lean * h * t, base - h * t
        side = 1 if (i + seed) % 2 else -1
        L = h * rnd.uniform(0.3, 0.46)
        rise = L * rnd.uniform(0.25, 0.5)
        tip = (px + side * L, py + L * rnd.uniform(0.1, 0.55))
        ctrl = (px + side * L * 0.45, py - rise)
        pts = qpts((px, py), ctrl, tip, 8)
        out.append(taper(pts, w * 2.5, 0.8, col))
        if rim and side < 0 and i % 3 == 0:
            out.append(pline(pts[1:5], rim, 1.4, seed + i, 0.45, 1))
    tz = [(top[0] - 7, top[1] - 13), (top[0] + 1, top[1] - 17), (top[0] + 8, top[1] - 11)]
    for tx, ty in tz:
        out.append(taper([top, ((top[0] + tx) / 2, (top[1] + ty) / 2 - 2), (tx, ty)], 2.6, 0.8, col))
    if seed % 3 == 0:
        ex, ey = x + lean * h * 0.48, base - h * 0.48
        out.append(f'<path d="{blob(ex + 6, ey, 4.5, 12, seed, 0.1, 10, 20)}" fill="{col}"/>')
    return "".join(out)


def corn_band(seed, y, h, col, x0=-20, x1=620):
    """A distant row of corn painted as one mass with a ragged, tasselled top."""
    rnd = random.Random(seed)
    top = []
    x = x0
    while x < x1:
        hh = h * rnd.uniform(0.6, 1.0)
        if rnd.random() < 0.55:
            top += [(x, y - hh * 0.6), (x + 2.5, y - hh), (x + 4, y - hh * 0.62)]
        else:
            top += [(x, y - hh * rnd.uniform(0.5, 0.7)), (x + 6, y - hh * rnd.uniform(0.55, 0.75))]
        x += rnd.uniform(8, 22)
    d = "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in top) + f" L {x1} {y + 40} L {x0} {y + 40} Z"
    out = [f'<path d="{d}" fill="{col}" stroke="{col}" stroke-width="1.5" stroke-linejoin="round"/>']
    for _ in range(int((x1 - x0) / 9)):
        px = rnd.uniform(x0, x1)
        py = y - h * rnd.uniform(0.3, 0.7)
        sd = rnd.choice((-1, 1))
        L = rnd.uniform(10, 18)
        out.append(taper(qpts((px, py), (px + sd * L * 0.5, py - 5), (px + sd * L, py + rnd.uniform(2, 7)), 5), 2.4, 0.5, col))
    return "".join(out)


@design("harvest-moon")
def harvest_moon():
    D = Doc("hm")
    out = [sky(D, [(0, "#1E1F3E"), (0.5, "#33284E"), (0.85, "#5A3550"), (1, "#6E3E4A")], 3, 600,
               ["#2C2C58", "#45306A", "#1A1A36", "#5A3A66"], 120, angle=-4, sop=(0.15, 0.4))]
    out.append(blooms(7, ["#6A4A8A", "#2A2A5A", "#8A5A7A"], 7, (0, 0, 600, 420), (60, 140), (0.08, 0.16)))
    rnd = random.Random(4)
    for _ in range(46):
        x, y = rnd.uniform(20, 580), rnd.uniform(20, 300)
        if math.hypot(x - 300, y - 340) < 170:
            continue
        r = rnd.uniform(0.8, 2.2)
        out.append(f'<path d="{blob(x, y, r, r, rnd.randint(0, 99), 0.2, 6)}" fill="#FBEFD0" opacity="{rnd.uniform(0.4, 0.95):.2f}"/>')
    for x, y in ((90, 90), (510, 120), (470, 250)):
        out.append(f'<path d="M {x} {y - 7} Q {x + 1} {y - 1} {x + 7} {y} Q {x + 1} {y + 1} {x} {y + 7} Q {x - 1} {y + 1} {x - 7} {y} Q {x - 1} {y - 1} {x} {y - 7} Z" fill="#FBEFD0" opacity="0.9"/>')
    # the moon: layered warm washes, crater blooms, curved strokes, glow
    mx, my, mr = 300, 352, 132
    out.append(soft_glow(D, mx, my, 290, "#F6C878", 0.45))
    out.append(soft_glow(D, mx, my, 190, "#FFE2A0", 0.5))
    mpts = blob_pts(mx, my, mr, mr, 9, 0.012, 40)
    out.append(painted(D, mpts, ("#FFF4D2", "#F6CF7E", "#D99A48"), 10, sdir=(0.6, 0.5), sk=0.1, angle=-30, n=200, slen=(30, 90),
                       sw=(3, 8), sop=(0.12, 0.35), cols=["#FFF2C8", "#F2C070", "#FBE2A0", "#E8AE5A"], inkc="#8A4E1E", inkw=2, inkop=0.5, hi=0.5, hik=0.08, curve=0.5))
    cid = D.clip(f'<path d="{smooth_closed(mpts)}"/>')
    maria = [(262, 306, 52, 34, -20), (350, 384, 56, 36, 15), (330, 300, 26, 18, 0), (246, 398, 30, 20, 30), (380, 320, 18, 14, 0)]
    cr = []
    for i, (x, y, rx, ry, r) in enumerate(maria):
        d = blob(x, y, rx, ry, 20 + i, 0.22, 16, r)
        cr.append(f'<path d="{d}" fill="#D89C52" opacity="0.22"/><path d="{d}" fill="none" stroke="#C88A40" stroke-width="2.5" opacity="0.18"/>')
    for i, (x, y, r) in enumerate([(300, 360, 7), (232, 344, 5), (366, 438, 6), (406, 360, 4)]):
        cr.append(f'<path d="{blob(x, y, r, r * 0.85, 50 + i, 0.15, 10)}" fill="none" stroke="#C0803A" stroke-width="1.8" opacity="0.45"/>'
                  f'<path d="{blob(x - 1, y - 1, r * 0.6, r * 0.5, 60 + i, 0.15, 8)}" fill="#FFF4D6" opacity="0.4"/>')
    out.append(f'<g {cid}>{"".join(cr)}</g>')
    # geese crossing the moon
    for x, y, s in ((228, 270, 11), (252, 258, 10), (276, 248, 9), (204, 284, 10), (180, 296, 8)):
        out.append(pline([(x - s, y + 2), (x - s * 0.4, y - s * 0.45), (x, y)], "#2A1E36", 2.6, x, 1, 1) +
                   pline([(x, y), (x + s * 0.5, y - s * 0.5), (x + s * 1.05, y + 1)], "#2A1E36", 2.4, x + 1, 1, 1))
    # far field band, softly lit
    l1 = ridge([(-20, 452), (200, 444), (400, 450), (620, 440)], 3, 5)
    out.append(hill(D, l1, 600, ("#7A5A6A", "#4E3A52", "#2E2238"), 3, inkw=0, sop=(0.15, 0.3)))
    # back rows of corn painted as masses, then a few tall rim-lit stalks in front
    out.append(corn_band(31, 462, 46, "#4A3656"))
    out.append(corn_band(32, 488, 62, "#36264A"))
    out.append(hill(D, ridge([(-20, 500), (300, 494), (620, 502)], 6, 4), 600, ("#3E2A44", "#2A1C30", "#180F1E"), 6, inkw=0, sop=(0.1, 0.25)))
    rnd = random.Random(8)
    xs = [-14, 30, 72, 470, 516, 560, 604, 158, 208, 392, 436, 250, 350]
    for i, x in enumerate(xs):
        mid = 190 < x < 410
        h = rnd.uniform(96, 130) if mid else rnd.uniform(170, 240)
        out.append(corn_silhouette(x + rnd.uniform(-6, 6), 612, h, "#1E1426", 200 + i, rim="#F2C070" if 150 < x < 450 else "#C08A60",
                                   lean=rnd.uniform(-0.1, 0.1), w=7 if not mid else 5, blades=7))
    # a lone pumpkin in the stubble, moonlit
    out.append(pumpkin(D, 116, 540, 128, 86, ("#E8925A", "#B4562A", "#5E2612"), 14, stem=("#8A7A50", "#4E4026", "#2A2014"), leafc="olive", cast_op=0.4,
                       light=(0.8, -0.6)))
    out.append(grass(19, (-10, 560, 610, 604), ["#2A1E2A", "#3A2A36", "#5A4040"], 120, (10, 24)))
    # lettering
    out.append(label(300, 104, "HARVEST", CINZEL, 50, "#FBEBD0", ls=16, max_w=420))
    out.append(letters(D, 300, 212, "moon", SERIF_IT, 132, "#F6C46A", ["#FFE0A0", "#D8963A", "#FFF0C8", "#E8AA50"], 8, max_w=340,
                       shadow="#1A1230", angle=-40, hi="#FFF6DC"))
    return finish(D, out, 21, "#F4E0C0", 0.8)


# ================================================================ 4. take the scenic route — a road winding through painted hills
def forest_band(D, line, bottom, pals, seed, size=(14, 22), density=1.0, ground=("#C89A5A", "#9A6A3A", "#6A4426"), inkw=1.0, rows=3):
    """A hillside covered in round autumn tree crowns, painted dab by dab (back rows first)."""
    rnd = random.Random(seed)
    out = [hill(D, line, bottom, ground, seed, inkw=0, sop=(0.1, 0.3))]
    xs0, xs1 = line[0][0], line[-1][0]
    items = []
    for r in range(rows):
        x = xs0 - 10
        while x < xs1 + 10:
            s = rnd.uniform(*size) * (1 + r * 0.15)
            yl = y_at(line, x)
            y = yl + s * 0.5 + r * size[1] * 0.9 + rnd.uniform(-3, 3)
            if y - s < bottom:
                items.append((y, x, s, rnd.choice(pals)))
            x += s * rnd.uniform(0.9, 1.4) / density
    for y, x, s, pal in sorted(items):
        lt, base, dk = pal
        sd = rnd.randint(0, 9999)
        out.append(f'<path d="{blob(x, y, s, s * 0.88, sd, 0.12, 12)}" fill="{base}"/>')
        out.append(f'<path d="{blob(x + s * 0.28, y + s * 0.3, s * 0.7, s * 0.55, sd + 1, 0.15, 10)}" fill="{dk}" opacity="0.55"/>')
        out.append(f'<path d="{blob(x - s * 0.3, y - s * 0.35, s * 0.45, s * 0.36, sd + 2, 0.2, 10)}" fill="{lt}" opacity="0.75"/>')
        for _ in range(3):
            out.append(f'<circle cx="{x + rnd.uniform(-0.6, 0.5) * s:.1f}" cy="{y + rnd.uniform(-0.6, 0.2) * s:.1f}" r="{s * rnd.uniform(0.08, 0.14):.1f}" fill="{lt}" opacity="0.8"/>')
        if inkw:
            out.append(f'<path d="{blob(x, y, s, s * 0.88, sd, 0.12, 12)}" fill="none" stroke="{INK}" stroke-width="{inkw}" opacity="0.35"/>')
    return "".join(out)


def y_at(line, x):
    for (x1, y1), (x2, y2) in zip(line, line[1:]):
        if x1 <= x <= x2:
            return y1 + (y2 - y1) * (x - x1) / ((x2 - x1) or 1)
    return line[0][1] if x < line[0][0] else line[-1][1]


def ribbon_path(center, widths):
    """Closed outline around a centreline with per-point half widths."""
    left, right = [], []
    n = len(center)
    for i, (x, y) in enumerate(center):
        a, b = center[max(i - 1, 0)], center[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = widths[i]
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left, right


def catmull(pts, n=8):
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out


def little_car(D, x, y, s, body=("#7FB8B0", "#3E8A84", "#1E4E4A"), flip=1):
    """Tiny vintage car, 3/4 rear view feel, (x, y) = ground centre."""
    k = s / 40
    g = f'<g transform="translate({x:.1f} {y:.1f}) scale({k * flip:.3f} {k:.3f})">'
    pts = [(-20, -6), (-21, -16), (-16, -20), (-12, -31), (12, -31), (16, -20), (21, -16), (20, -6)]
    out = [g, f'<ellipse cx="0" cy="0" rx="26" ry="4" fill="#2A1A10" opacity="0.35"/>',
           f'<path d="{blob(-13, -4, 5, 5, 1, 0.05, 8)}" fill="#2A1A10"/><path d="{blob(13, -4, 5, 5, 2, 0.05, 8)}" fill="#2A1A10"/>',
           painted(D, pts, body, 7, sdir=(1, 0.3), sk=0.2, angle=0, n=10, slen=(5, 14), sw=(0.8, 1.6), inkw=1.6, hi=0.4),
           '<path d="M -10 -28 L 10 -28 L 13 -20 L -13 -20 Z" fill="#E8EEF0" opacity="0.85"/>',
           '<path d="M -18 -14 L 18 -14" stroke="#F6EAD8" stroke-width="2"/>',
           '<circle cx="-15" cy="-10" r="2.4" fill="#F2483A"/><circle cx="15" cy="-10" r="2.4" fill="#F2483A"/>',
           '<path d="M -6 -40 L 6 -40 L 8 -32 L -8 -32 Z" fill="#C89A5A"/><path d="M -6 -36 L 6 -36" stroke="#6E4A2E" stroke-width="1.4"/>',
           "</g>"]
    return "".join(out)


@design("scenic-route")
def scenic_route():
    D = Doc("sr")
    out = [sky(D, [(0, "#B9CBD0"), (0.25, "#E6DCCB"), (0.5, "#F6DDB8")], 3, 340, ["#FFFFFF", "#DCC8B8", "#C8D4D6"], 40, sop=(0.08, 0.22))]
    out.append(soft_glow(D, 470, 250, 200, "#FFF0CC", 0.6))
    out.append(blooms(4, ["#FFFFFF", "#C8D0D8"], 4, (40, 30, 560, 200), (60, 120), (0.08, 0.15)))
    # far blue ridges
    l0 = ridge([(-20, 262), (90, 236), (190, 252), (300, 226), (420, 248), (520, 232), (620, 250)], 2, 16)
    out.append(hill(D, l0, 420, ("#C8C0D4", "#A8A4C0", "#8A86A8"), 2, inkw=1.2, inkop=0.3, sop=(0.08, 0.2)))
    l1 = ridge([(-20, 282), (140, 266), (280, 286), (430, 270), (620, 284)], 5, 10)
    out.append(forest_band(D, l1, 420, [("#E8B8A0", "#D09C8C", "#B08088"), ("#E8C8A0", "#D2AE8C", "#B8907E"), ("#D8C0B0", "#BFA6A0", "#A08890")], 5,
                           size=(8, 11), inkw=0, rows=2, ground=("#D8B8A8", "#C0A098", "#A08890")))
    # mid hills in full colour
    l2 = ridge([(-20, 318), (110, 302), (240, 322), (380, 306), (520, 316), (620, 300)], 7, 8)
    warm = [("#F6C060", "#E0902A", "#9A561A"), ("#F08A50", "#CC4E26", "#7E2A14"), ("#F8D878", "#E2B03A", "#A07A1E"),
            ("#C8C070", "#8E9244", "#56602A"), ("#E87A60", "#B8402E", "#6E1E18")]
    out.append(hill(D, l2, 620, ("#C8904A", "#9A6A3A", "#6A4426"), 7, inkw=0, sop=(0.1, 0.3)))
    rnd = random.Random(7)
    items = []
    y = 300.0
    while y < 640:
        sz = 9 + (y - 300) * 0.085
        x = -20 + rnd.uniform(0, sz)
        while x < 630:
            yy = y + rnd.uniform(-sz * 0.3, sz * 0.3)
            if yy > y_at(l2, x) + sz * 0.3:
                items.append((yy, x, sz * rnd.uniform(0.85, 1.15), rnd.choice(warm)))
            x += sz * rnd.uniform(1.2, 1.6)
        y += sz * 0.75
    for yy, x, sz, (lt, base, dk) in sorted(items):
        sd = rnd.randint(0, 9999)
        out.append(f'<path d="{blob(x, yy, sz, sz * 0.86, sd, 0.13, 12)}" fill="{base}"/>'
                   f'<path d="{blob(x + sz * 0.28, yy + sz * 0.3, sz * 0.7, sz * 0.5, sd + 1, 0.15, 10)}" fill="{dk}" opacity="0.5"/>'
                   f'<path d="{blob(x - sz * 0.3, yy - sz * 0.32, sz * 0.48, sz * 0.36, sd + 2, 0.2, 10)}" fill="{lt}" opacity="0.8"/>'
                   + "".join(f'<circle cx="{x + rnd.uniform(-0.6, 0.5) * sz:.1f}" cy="{yy + rnd.uniform(-0.6, 0.2) * sz:.1f}" r="{sz * rnd.uniform(0.08, 0.13):.1f}" fill="{lt}" opacity="0.8"/>' for _ in range(3))
                   + (f'<path d="{blob(x, yy, sz, sz * 0.86, sd, 0.13, 12)}" fill="none" stroke="{INK}" stroke-width="{0.6 + sz * 0.03:.1f}" opacity="0.35"/>' if sz > 14 else ""))
    # the road
    c = catmull([(300, 640), (318, 586), (372, 512), (350, 452), (282, 410), (284, 362), (330, 330), (352, 318)], 8)
    n = len(c)
    ws = [max(1.6, 96 * (max(0, cy - 308) / 332) ** 1.4) for cx, cy in c]
    L, R = ribbon_path(c, ws)
    road = smooth_closed(L + R[::-1])
    verge = smooth_closed(*[ribbon_path(c, [w * 1.18 + 2 for w in ws])[0] + ribbon_path(c, [w * 1.18 + 2 for w in ws])[1][::-1]])
    out.append(f'<path d="{verge}" fill="#C8A86A"/>')
    out.append(wash(road, "#5A4A50", 3, 3, 1, 0.5))
    out.append(strokes(D.nid(), road, (180, 300, 460, 612), ["#7A6A70", "#3E3036", "#8A7A80"], 9, n=140, angle=-60, length=(10, 40), width=(1.5, 4), opacity=(0.15, 0.4)))
    out.append(ink(smooth_open(L), INK, 1.8, 3, 1, 0.55) + ink(smooth_open(R), INK, 1.8, 4, 1, 0.55))
    # dashed centre line
    for i in range(2, n - 2, 3):
        a, b = c[i], c[i + 1]
        w = max(1.0, ws[i] * 0.06)
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {a[0] + (b[0] - a[0]) * 0.6:.1f} {a[1] + (b[1] - a[1]) * 0.6:.1f}" stroke="#F6D068" stroke-width="{w:.1f}" stroke-linecap="round" opacity="0.9"/>')
    # fallen leaves on the road edges
    rnd = random.Random(30)
    for _ in range(26):
        i = rnd.randrange(0, n // 2)
        px, py = c[i]
        side = rnd.choice((-1, 1))
        ww = ws[i] * rnd.uniform(0.6, 1.2) * side
        s = max(1.2, ws[i] * 0.05)
        out.append(f'<path d="{blob(px + ww, py + rnd.uniform(-3, 3), s * 1.4, s * 0.8, rnd.randint(0, 99), 0.2, 8, rnd.uniform(0, 180))}" fill="{rnd.choice(["#E8792E", "#C23A22", "#F2B84A"])}" opacity="0.8"/>')
    out.append(little_car(D, 336, 470, 36))
    # foreground: birches on the left, a red maple on the right
    for x, top, w in ((86, 330, 12), (120, 360, 9)):
        tr = [(x - w / 2, 612), (x - w / 2 + 2, top), (x + w / 2 + 1, top), (x + w / 2, 612)]
        out.append(painted(D, tr, ("#FFFFFF", "#EEE6DA", "#A89A8A"), x, sdir=(1, 0), sk=0.3, angle=-90, n=20, inkw=1.6, hi=0.3))
        for k in range(9):
            yy = top + 20 + k * 28 + rnd.uniform(-6, 6)
            out.append(f'<path d="M {x - w / 2 + 1:.1f} {yy:.1f} q {w * 0.3:.1f} -2 {w * 0.6:.1f} 0" stroke="#2E2420" stroke-width="2.4" stroke-linecap="round"/>')
    out.append(dab_crown(D, 84, 300, 64, 52, [("#FAD870", "#E8A93A", "#A8701E"), ("#F6C060", "#E0902A", "#9A561A")], 41, 90, (7, 12)))
    out.append(dab_crown(D, 540, 380, 72, 70, [("#F08A50", "#CC4E26", "#7E2A14"), ("#E87A60", "#B8402E", "#6E1E18")], 42, 110, (7, 13)))
    out.append(taper([(540, 612), (538, 470), (530, 430)], 14, 6, "#4A3018"))
    out.append(grass(43, (-10, 560, 250, 604), ["#8E9244", "#C8A050", "#6E7434"], 60, (10, 22)))
    out.append(falling(D, [("maple", 160, 236, 18, "gold", -20), ("slim", 470, 250, 16, "red", 30), ("maple", 520, 300, 16, "orange", 50)]))
    # lettering
    out.append(letters(D, 300, 100, "take the", SERIF_IT, 64, "#6E3A1E", ["#4A2410", "#8E4E2A"], 11, max_w=300, angle=-30))
    out.append(letters(D, 300, 196, "SCENIC ROUTE", BEBAS, 104, "#B8401E", ["#E06A28", "#9A3414", "#F08A40"], 12, ls=5, max_w=470,
                       shadow="#FFF4E0", soff=(0.03, 0.04), angle=-75, hi="#FFD9A8"))
    return finish(D, out, 31)


# ================================================================ 5. farmers market — a painted stall full of the harvest
def mum(D, cx, cy, r, pal, seed):
    rnd = random.Random(seed)
    lt, base, dk = pal
    out = [f'<path d="{blob(cx, cy + r * 0.2, r * 1.02, r * 0.8, seed, 0.1, 14)}" fill="#3E4A26"/>']
    heads = []
    for _ in range(int(r * 1.1)):
        a = rnd.uniform(0, 2 * math.pi)
        d = rnd.random() ** 0.55 * r * 0.9
        heads.append((cx + math.cos(a) * d, cy + math.sin(a) * d * 0.8, -math.cos(a) * 0.6 - math.sin(a) * 0.8))
    for x, y, lit in sorted(heads, key=lambda h: h[1]):
        col = lt if lit > 0.3 else (base if lit > -0.4 else dk)
        hr = rnd.uniform(5, 7.5)
        out.append(f'<path d="{blob(x, y, hr, hr * 0.9, rnd.randint(0, 999), 0.25, 9)}" fill="{dk}"/>'
                   f'<path d="{blob(x - 0.6, y - 0.8, hr * 0.75, hr * 0.65, rnd.randint(0, 999), 0.3, 9)}" fill="{col}"/>'
                   f'<circle cx="{x - 0.5:.1f}" cy="{y - 1:.1f}" r="{hr * 0.22:.1f}" fill="#F2C24A"/>')
    return "".join(out)


def pot(D, cx, top, w, h, pal=("#E89A6A", "#C0623A", "#7A3418"), seed=1):
    pts = [(cx - w / 2 - 4, top), (cx + w / 2 + 4, top), (cx + w / 2 + 4, top + 12), (cx + w / 2 - 3, top + 12), (cx + w * 0.38, top + h),
           (cx - w * 0.38, top + h), (cx - w / 2 + 3, top + 12), (cx - w / 2 - 4, top + 12)]
    return painted(D, pts, pal, seed, sdir=(1, 0.2), sk=0.18, angle=-90, n=24, inkw=1.8, hi=0.35) + pline([(cx - w / 2 - 2, top + 12), (cx + w / 2 + 2, top + 12)], "#7A3418", 1.6, seed, 0.6, 1)


def crate(D, x, y, w, h, seed, pal=("#E2B47A", "#C08A50", "#7A5230")):
    out = []
    for k in range(3):
        yy = y + k * h / 3
        p = [(x, yy + 1), (x + w, yy), (x + w, yy + h / 3 - 2), (x, yy + h / 3 - 1)]
        p = [p[0], ((p[0][0] + p[1][0]) / 2, p[0][1]), p[1], p[2], ((p[2][0] + p[3][0]) / 2, p[2][1]), p[3]]
        out.append(painted(D, p, pal, seed + k, sdir=(0.3, 1), sk=0.12, angle=-2, n=14, slen=(20, 60), sw=(1, 2.2), inkw=1.6, hi=0.3, edge=False))
    out.append(f'<path d="M {x + 5} {y} L {x + 5} {y + h} M {x + w - 5} {y} L {x + w - 5} {y + h}" stroke="#7A5230" stroke-width="5" opacity="0.6"/>')
    return "".join(out)


def jar(D, x, y, w, h, fill, lid, seed, lbl="#F6EAD8"):
    pts = [(x, y + 6), (x + w, y + 6), (x + w + 1, y + h * 0.5), (x + w, y + h), (x, y + h), (x - 1, y + h * 0.5)]
    out = [painted(D, pts, (mix(fill, "#FFFFFF", 0.35), fill, mix(fill, "#000000", 0.4)), seed, sdir=(1, 0), sk=0.2, angle=-90, n=8, inkw=1.4, hi=0.5, hik=0.15),
           f'<path d="{blob(x + w / 2, y + 4, w * 0.56, 5, seed, 0.05, 10)}" fill="{lid}"/>',
           f'<path d="{blob(x + w / 2, y + h * 0.58, w * 0.42, h * 0.16, seed + 1, 0.05, 10)}" fill="{lbl}" opacity="0.9"/>',
           f'<path d="M {x + 3:.1f} {y + 12:.1f} l 0 {h * 0.6:.1f}" stroke="#FFFFFF" stroke-width="2" opacity="0.5" stroke-linecap="round"/>']
    return "".join(out)


@design("farmers-market")
def farmers_market():
    D = Doc("fm")
    out = [paper(D.nid(), "#F2E6D0", FLECK, 21)]
    out.append(sky(D, [(0, "#C4D4D4"), (0.6, "#EADFCB", 0.6), (1, "#F2E6D0", 0)], 4, 470, ["#FFFFFF", "#B8CCCC"], 30, sop=(0.08, 0.2)))
    # street trees behind
    for i, (x, cy, pals) in enumerate(((44, 230, [("#F6C060", "#E0902A", "#9A561A")]), (556, 236, [("#F08A50", "#CC4E26", "#7E2A14")]),
                                       (150, 196, [("#F8D878", "#E2B03A", "#A07A1E")]), (450, 196, [("#C8C070", "#8E9244", "#56602A"), ("#F6C060", "#E0902A", "#9A561A")]))):
        out.append(taper([(x, 470), (x + 2, cy + 20)], 10, 5, "#5A4034"))
        out.append(dab_crown(D, x, cy, 66, 58, pals, 50 + i, 70, (7, 12), inkw=1.0))
    out.append(f'<rect y="150" width="600" height="330" fill="{D.lin([(0, "#F2E6D0", 0), (1, "#F2E6D0", 0.55)])}"/>')
    # ground: painted pavers
    gd = smooth_closed([(-20, 470), (300, 462), (620, 470), (620, 620), (-20, 620)])
    out.append(f'<path d="M -20 468 Q 300 458 620 468 L 620 620 L -20 620 Z" fill="#D8C2A2"/>')
    out.append(strokes(D.nid(), "M -20 468 Q 300 458 620 468 L 620 620 L -20 620 Z", (-60, 460, 620, 610), ["#C8AE8A", "#E8D6B8", "#B89A78"], 22, n=120, angle=0, length=(30, 80), width=(3, 7), opacity=(0.2, 0.45)))
    rnd = random.Random(3)
    for i, y in enumerate(range(476, 612, 22)):
        out.append(pline([(-10, y), (300, y - 2), (610, y)], "#A88A6A", 1.4, y, 0.5, 1))
        for x in range(-10 + (20 if i % 2 else 0), 610, 44):
            out.append(f'<path d="M {x + rnd.uniform(-2, 2):.1f} {y:.1f} l 0 22" stroke="#A88A6A" stroke-width="1.3" opacity="0.5"/>')
    # stall back wall and shelf
    wall = [(96, 236), (504, 236), (504, 420), (96, 420)]
    wall = [wall[0], (300, 236), wall[1], (504, 330), wall[2], (300, 420), wall[3], (96, 330)]
    out.append(painted(D, wall, ("#7A5236", "#5A3A26", "#3A2418"), 30, sdir=(0, 1), sk=0.1, angle=-90, n=120, slen=(30, 90), sw=(2, 5), inkw=2, hi=0))
    for x in range(140, 504, 44):
        out.append(pline([(x, 238), (x + 1, 330), (x, 418)], "#2A1810", 1.6, x, 0.5, 1))
    out.append(taper([(96, 312), (300, 314), (504, 312)], 8, 8, "#A0704A"))
    jars = [(118, "#E2A23A"), (150, "#9A2E22"), (182, "#E2A23A"), (214, "#C86A2A"), (360, "#9A2E22"), (392, "#E2A23A"), (424, "#7A3A4A"), (456, "#E2A23A")]
    for i, (x, f) in enumerate(jars):
        out.append(jar(D, x, 272, 24, 36, f, "#F2E6D0" if i % 2 else "#D8A848", 60 + i))
    # braided corn hanging in the middle
    for k, (x, r_) in enumerate(((268, -8), (300, 0), (332, 8))):
        cp = blob_pts(x, 290, 11, 32, 70 + k, 0.04, 14)
        out.append(f'<g transform="rotate({r_} {x} 250)">')
        out.append(pline([(x, 238), (x, 258)], "#C9A060", 2, k, 1, 1))
        out.append(painted(D, cp, [("#D86A4A", "#9A3A2A", "#5A1A14"), ("#F2C060", "#C98A2A", "#7A4E14"), ("#A86A8A", "#7A3A4A", "#4A1A2A")][k], 71 + k,
                           sdir=(1, 0), sk=0.2, angle=-90, n=10, inkw=1.4, hi=0.3))
        out.append(specks(80 + k, (x - 8, 266, x + 8, 316), ["#F2D27A", "#5A2A3A", "#E9B54A"], 26, (1.2, 2.2), (0.6, 0.9)))
        out.append(f'<path d="M {x} 260 q -18 6 -16 26 q 8 -14 16 -20 q 8 6 14 20 q 2 -20 -14 -26" fill="#EAD9A2" stroke="#A8864A" stroke-width="1"/>')
        out.append("</g>")
    # posts
    for x in (84, 504):
        out.append(painted(D, [(x, 150), (x + 14, 150), (x + 14, 300), (x + 14, 470), (x, 470), (x, 300)], ("#C08A58", "#8A5A34", "#4A2E1A"), x, sdir=(1, 0), sk=0.3,
                           angle=-90, n=30, inkw=1.8, hi=0.3))
    # awning: scalloped stripes
    aw_top, aw_bot = 172, 236
    stripes = []
    for i in range(9):
        x0 = 74 + i * 50.5
        col = ("#E8D8C0", "#D8C4A8", "#A8947A") if i % 2 else ("#D8604A", "#B83A2A", "#6E1A12")
        pts = [(x0 - 2, aw_top), (x0 + 50.5 + 2, aw_top), (x0 + 52.5, aw_bot - 6), (x0 + 38, aw_bot + 6), (x0 + 25, aw_bot + 10), (x0 + 12, aw_bot + 6), (x0 - 2, aw_bot - 6)]
        stripes.append(painted(D, pts, col, 90 + i, sdir=(0.3, 1), sk=0.15, angle=-90, n=14, slen=(10, 30), sw=(1.5, 3), inkw=1.6, inkop=0.6, hi=0.3, edge=False))
    out.append(cast(D, 300, 246, 230, 12, strength=0.35))
    out.append("".join(stripes))
    out.append(taper([(68, 174), (300, 170), (532, 174)], 7, 7, "#6E1A12"))
    # sign board
    out.append(cast(D, 300, 168, 230, 12, strength=0.3))
    board = [(76, 72), (300, 68), (524, 72), (528, 118), (524, 166), (300, 168), (76, 166), (72, 118)]
    out.append(painted(D, board, ("#5E7A5A", "#3E5A40", "#22362A"), 41, sdir=(0.5, 1), sk=0.12, angle=-2, n=140, slen=(30, 90), sw=(2, 5), inkw=2.4, hi=0.3))
    out.append(pline([(86, 84), (300, 80), (514, 84), (518, 118), (514, 158), (300, 160), (86, 158), (82, 118), (86, 84)], "#E8D8B0", 2, 5, 0.5, 1))
    out.append(letters(D, 300, 128, "FARMERS MARKET", BEBAS, 60, "#F6EAD0", ["#FFFFFF", "#E8D0A0", "#F6E2B8"], 13, ls=4, max_w=410, shadow="#1A2A1C", soff=(0.03, 0.05), angle=-75))
    out.append(label(300, 154, "FRESH · LOCAL · SEASONAL", MONO, 18, "#F2C860", ls=3, max_w=380))
    # crates on the counter
    out.append(cast(D, 300, 446, 240, 14, strength=0.35))
    for i, (x, w) in enumerate(((104, 128), (236, 128), (368, 128))):
        # produce first (sits in the crate, behind the front slats)
        if i == 0:
            for k, (ax, ay) in enumerate(((122, 368), (146, 362), (172, 366), (198, 360), (220, 368), (134, 380), (160, 378), (186, 380), (210, 380))):
                out.append(apple(D, ax, ay, 13, seed=100 + k, leafc=None, stem=k % 3 == 0))
        elif i == 1:
            out.append(pumpkin(D, 274, 364, 60, 42, PUMP, 110, vine=False, cast_op=0) + pumpkin(D, 330, 368, 52, 36, GOLD, 111, vine=False, cast_op=0))
        else:
            for k, (ax, ay, pal) in enumerate(((388, 372, ("#C8D07A", "#8E9A3A", "#4E5A1E")), (412, 364, ("#F6D070", "#D8A030", "#8A6014")),
                                                (440, 370, ("#F2A060", "#D0602A", "#7A2E12")), (468, 362, ("#C8D07A", "#8E9A3A", "#4E5A1E")),
                                                (480, 376, ("#F6D070", "#D8A030", "#8A6014")), (424, 382, ("#F2A060", "#D0602A", "#7A2E12")))):
                pts = [(ax - 13, ay + 4), (ax - 10, ay - 8), (ax - 2, ay - 18), (ax + 4, ay - 26), (ax + 8, ay - 20), (ax + 6, ay - 8), (ax + 13, ay + 2), (ax, ay + 10)]
                out.append(painted(D, pts, pal, 120 + k, sdir=(0.7, 0.6), sk=0.18, angle=-70, n=10, inkw=1.4, hi=0.4))
        out.append(crate(D, x, 384, w, 66, 130 + i * 5))
    # price tags
    for x, p in ((168, "$3"), (300, "$5"), (432, "$4")):
        out.append(f'<path d="{blob(x, 418, 22, 13, len(p) + x, 0.06, 12)}" fill="#F6EAD8" stroke="{INK}" stroke-width="1.6"/>'
                   + label(x, 425, p, JOST, 20, "#3A2418", max_w=60))
    # front: mum pots and pumpkins on the pavement
    out.append(pot(D, 112, 512, 70, 50, seed=140) + mum(D, 112, 494, 40, ("#F2A0C0", "#C8507A", "#7A1E40"), 141))
    out.append(pot(D, 488, 512, 70, 50, seed=142) + mum(D, 488, 494, 40, ("#F6C860", "#E09A2A", "#9A5A14"), 143))
    out.append(pumpkin(D, 246, 530, 96, 64, PUMP, 150, leafc="olive") + pumpkin(D, 356, 538, 76, 52, CREAM, 151, vine=False))
    out.append(pumpkin(D, 420, 548, 54, 38, GOLD, 152, vine=False))
    return finish(D, out, 33)


# ================================================================ 6. misty mornings — a buck in the meadow, dawn mist between the trees
def pine_dabs(x, base, h, col, seed, w=0.32):
    """Soft conifer painted as stacked dabs (for misty distances)."""
    rnd = random.Random(seed)
    out = [f'<path d="M {x - 1:.1f} {base:.1f} L {x:.1f} {base - h:.1f} L {x + 1:.1f} {base:.1f} Z" fill="{col}"/>']
    tiers = max(5, int(h / 7))
    for i in range(tiers):
        t = i / tiers
        yy = base - h * 0.1 - t * h * 0.88
        ww = h * w * (1 - t) * rnd.uniform(0.8, 1.1) + 2
        out.append(f'<path d="{blob(x + rnd.uniform(-1, 1), yy, ww, h * 0.06 + 1.5, rnd.randint(0, 999), 0.2, 8)}" fill="{col}"/>')
    return "".join(out)


def mist(D, y, h, seed, col="#FFFFFF", op=0.7, x0=-40, x1=640):
    rnd = random.Random(seed)
    g = D.lin([(0, col, 0), (0.5, col, op), (1, col, 0)])
    out = [f'<rect x="{x0}" y="{y - h / 2:.1f}" width="{x1 - x0}" height="{h:.1f}" fill="{g}"/>']
    for _ in range(int((x1 - x0) / 50)):
        cx = rnd.uniform(x0, x1)
        out.append(f'<path d="{blob(cx, y + rnd.uniform(-h * 0.2, h * 0.2), rnd.uniform(40, 110), h * rnd.uniform(0.15, 0.3), rnd.randint(0, 999), 0.2, 12)}" fill="{col}" opacity="{rnd.uniform(0.15, 0.35):.2f}"/>')
    return "".join(out)


def deer_pts(x, y, s, flip=1):
    from fall_painted import DEER
    return [(x + px * s * flip, y + py * s) for px, py in DEER]


@design("misty-mornings")
def misty_mornings():
    D = Doc("mm")
    out = [sky(D, [(0, "#B8B4CE"), (0.3, "#E0C6C4"), (0.55, "#F4D8BA"), (1, "#EEDCC0")], 3, 600, ["#FFFFFF", "#D8C0C8", "#F6E0C8"], 60, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 170, 296, 300, "#FFE6B8", 0.9))
    out.append(f'<path d="{blob(170, 296, 26, 26, 3, 0.03, 16)}" fill="#FFF6DE"/>')
    out.append(blooms(6, ["#FFFFFF", "#C8B8D0"], 5, (0, 0, 600, 240), (60, 120), (0.08, 0.14)))
    # three ridges of trees, each paler and bluer with distance, mist between
    rnd = random.Random(5)
    for layer, (base, col, hmin, hmax, step) in enumerate(((330, "#B8A8C0", 24, 46, 11), (372, "#9A8AA8", 34, 64, 14), (418, "#7A6A88", 44, 86, 17))):
        x = -10
        while x < 620:
            out.append(pine_dabs(x, base + rnd.uniform(-4, 6), rnd.uniform(hmin, hmax), col, rnd.randint(0, 9999)))
            x += rnd.uniform(step * 0.6, step * 1.3)
        out.append(f'<rect x="-10" y="{base - 2}" width="620" height="{90}" fill="{col}"/>')
        out.append(mist(D, base + 4, 46, 20 + layer, "#FBEFE6", 0.85))
    # warm autumn trees on the right edge catching the first light
    out.append(taper([(506, 470), (508, 360)], 9, 4, "#4A3030"))
    out.append(dab_crown(D, 506, 352, 56, 66, [("#F6B070", "#D8743A", "#8E3E2A"), ("#F8D088", "#E0A048", "#9A6430")], 61, 100, (7, 12), inkw=1))
    out.append(taper([(430, 462), (432, 400)], 6, 3, "#4A3030"))
    out.append(dab_crown(D, 432, 396, 36, 40, [("#F08A60", "#C8503A", "#7A2A2A")], 62, 50, (5, 9), inkw=1))
    # the meadow
    l = ridge([(-20, 456), (200, 448), (420, 458), (620, 450)], 8, 4)
    out.append(hill(D, l, 600, ("#D8C890", "#B4A66A", "#7E7444"), 8, angle=-3, inkw=0, sop=(0.15, 0.35)))
    out.append(mist(D, 462, 40, 30, "#FFF6EC", 0.7))
    # the buck, painted, rim-lit from the low sun on the left
    s = 1.5
    dx, dy = 226, 512
    dp = deer_pts(dx, dy, s)
    legs = [[(dx + 36 * s, dy - 36 * s), (dx + 38 * s, dy - 14 * s), (dx + 38 * s, dy)], [(dx + 72 * s, dy - 36 * s), (dx + 79 * s, dy - 20 * s), (dx + 80 * s, dy)]]
    for lg_ in legs:
        out.append(taper(lg_, 5 * s, 3 * s, "#4A2C1A"))
    out.append(cast(D, dx + 55 * s, dy + 2, 70 * s, 6, strength=0.3))
    out.append(painted(D, dp, ("#D8A27A", "#9A6440", "#4E2E1A"), 70, sdir=(0.8, 0.5), sk=0.12, angle=-10, n=60, slen=(8, 22), sw=(1, 2.5), inkw=2, hi=0.5, hik=0.06))
    out.append(f'<path d="{blob(dx + 10 * s, dy - 66 * s, 4 * s, 7 * s, 3, 0.1, 8, 30)}" fill="#F6EAD8" opacity="0.85"/>'
               f'<path d="{blob(dx - 9 * s, dy - 82 * s, 4 * s, 2.6 * s, 4, 0.1, 8)}" fill="#F6EAD8" opacity="0.85"/>')
    out.append(painted(D, [(dx + 8 * s, dy - 99 * s), (dx + 23 * s, dy - 113 * s), (dx + 26 * s, dy - 107 * s), (dx + 15 * s, dy - 95 * s)], ("#C08A60", "#7A4A2C", "#3E2214"), 71,
                       sdir=(1, 0), sk=0.2, angle=-40, n=4, inkw=1.4, hi=0.3))
    out.append(f'<circle cx="{dx - 14 * s:.1f}" cy="{dy - 84 * s:.1f}" r="{2.6 * s:.1f}" fill="#1E120A"/><circle cx="{dx - 2 * s:.1f}" cy="{dy - 90 * s:.1f}" r="{2 * s:.1f}" fill="#1E120A"/>')
    ant = [[(0, -99), (-2, -112), (6, -126), (24, -136)], [(3, -115), (-4, -128)], [(11, -125), (9, -141)], [(19, -132), (23, -146)]]
    for a in ant:
        out.append(pline([(dx + px * s, dy + py * s) for px, py in a], "#5A4634", 2.8, 72, 1, 1))
        out.append(pline([(dx + px * s + 2, dy + py * s - 1) for px, py in a], "#F2E2C4", 1.4, 73, 0.7, 1))
    rim = [(-14, -84), (-10, -90), (-2, -97), (8, -100)]
    chest = [(-2, -78), (6, -72), (14, -60), (20, -44), (23, -30)]
    out.append(pline([(dx + px * s - 1, dy + py * s) for px, py in rim], "#FFE2B0", 2.6, 74, 0.9, 1))
    out.append(pline([(dx + px * s - 1.5, dy + py * s) for px, py in chest], "#FFE2B0", 2.6, 75, 0.85, 1))
    out.append(f'<path d="M {dx + 96 * s:.1f} {dy - 62 * s:.1f} q {8 * s:.1f} {4 * s:.1f} {5 * s:.1f} {14 * s:.1f}" stroke="#F6EEE0" stroke-width="{4 * s:.1f}" fill="none" stroke-linecap="round"/>')
    # tall grass and seed heads in front, catching light
    out.append(grass(80, (-10, 520, 610, 604), ["#8E8A4A", "#B4A66A", "#D8C890", "#6E6A3A"], 220, (14, 40), w=1.4))
    for i in range(18):
        x = rnd.uniform(20, 580)
        y = rnd.uniform(540, 600)
        h = rnd.uniform(40, 80)
        out.append(pline([(x, y), (x + 3, y - h * 0.5), (x + rnd.uniform(-6, 8), y - h)], "#8A7A4A", 1.6, i, 0.9, 1))
        out.append(f'<path d="{blob(x + 2, y - h - 6, 3, 8, i, 0.1, 8, 10)}" fill="#C8A060"/>')
    out.append(mist(D, 560, 50, 40, "#FFF6EC", 0.35))
    # birds
    for bx, by, bs in ((404, 262, 8), (428, 250, 7), (446, 266, 6)):
        out.append(pline([(bx - bs, by), (bx - bs * 0.5, by - bs * 0.6), (bx, by)], "#6A5060", 1.8, bx, 0.8, 1) + pline([(bx, by), (bx + bs * 0.5, by - bs * 0.6), (bx + bs, by)], "#6A5060", 1.8, bx + 1, 0.8, 1))
    # lettering
    out.append(letters(D, 300, 132, "misty", SERIF_IT, 120, "#5A3A4E", ["#3E2236", "#7A5068", "#8A6078"], 14, max_w=330, shadow="#FFF4E8", soff=(-0.02, -0.025), angle=-35))
    out.append(letters(D, 300, 200, "MORNINGS", JOS, 54, "#A24A34", ["#C8603E", "#7E3420"], 15, ls=14, max_w=430, angle=-70, wob=0.5))
    return finish(D, out, 41, INK, 0.8)


# ================================================================ 7. pumpkin spice — a painted mug, whipped cream, spices
def sample_d(d, per=10):
    """Points along an absolute M/L/C/Q/Z path (for turning drawn outlines into paintable point lists)."""
    toks = d.replace(",", " ").split()
    pts, i, cur, cmd = [], 0, (0, 0), None
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd == "Z":
                continue
        if cmd in ("M", "L"):
            cur = (float(toks[i]), float(toks[i + 1]))
            pts.append(cur)
            i += 2
        elif cmd == "C":
            p1 = (float(toks[i]), float(toks[i + 1]))
            p2 = (float(toks[i + 2]), float(toks[i + 3]))
            p3 = (float(toks[i + 4]), float(toks[i + 5]))
            for k in range(1, per + 1):
                u = k / per
                pts.append(tuple((1 - u) ** 3 * cur[j] + 3 * (1 - u) ** 2 * u * p1[j] + 3 * (1 - u) * u * u * p2[j] + u ** 3 * p3[j] for j in (0, 1)))
            cur = p3
            i += 6
        elif cmd == "Q":
            p1 = (float(toks[i]), float(toks[i + 1]))
            p2 = (float(toks[i + 2]), float(toks[i + 3]))
            for k in range(1, per + 1):
                u = k / per
                pts.append(tuple((1 - u) ** 2 * cur[j] + 2 * (1 - u) * u * p1[j] + u * u * p2[j] for j in (0, 1)))
            cur = p2
            i += 4
        else:
            i += 1
    if len(pts) > 2 and math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]) < 1:
        pts.pop()
    return pts


def cinnamon_stick(D, x1, y1, x2, y2, w=16, seed=1):
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    L = math.hypot(x2 - x1, y2 - y1)
    pts = [(0, -w / 2), (L * 0.33, -w / 2 - 0.5), (L * 0.66, -w / 2 + 0.5), (L, -w / 2), (L, w / 2), (L * 0.66, w / 2 + 0.5), (L * 0.33, w / 2 - 0.5), (0, w / 2)]
    out = [f'<g transform="translate({x1:.1f} {y1:.1f}) rotate({ang:.1f})">',
           painted(D, pts, ("#D08A50", "#A65C2E", "#5A2C12"), seed, sdir=(0, 1), sk=0.25, angle=0, n=int(L / 3), slen=(L * 0.1, L * 0.4), sw=(0.6, 1.6), inkw=1.6, hi=0.45, hik=0.15)]
    for t in range(14, int(L) - 6, 19):
        out.append(pline([(t, -w / 2 + 1), (t + 2, 0), (t, w / 2 - 1)], "#5A2C12", 1.2, t, 0.5, 1))
    out.append(f'<path d="{blob(L, 0, w * 0.26, w * 0.5, seed, 0.05, 10)}" fill="#7A3E1C"/>')
    out.append(pline([(L, -w * 0.38), (L + w * 0.16, -w * 0.15), (L + w * 0.08, w * 0.3), (L - w * 0.06, w * 0.1), (L, -w * 0.05)], "#3E1A08", 1.6, seed, 0.9, 1))
    out.append("</g>")
    return "".join(out)


def anise(D, cx, cy, r, rot=0, seed=1):
    out = [f'<g transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})">']
    for i in range(8):
        a = math.radians(i * 45 - 90)
        px, py = cx + math.cos(a) * r * 0.52, cy + math.sin(a) * r * 0.52
        pts = _rot_pts(blob_pts(px, py, r * 0.2, r * 0.46, seed + i, 0.06, 10), px, py, i * 45)
        out.append(painted(D, pts, ("#C07A44", "#8A4A24", "#4A220E"), seed + i, sdir=(0.6, 0.6), sk=0.2, angle=i * 45 - 90, n=4, inkw=1.2, hi=0.3))
        sx, sy = cx + math.cos(a) * r * 0.5, cy + math.sin(a) * r * 0.5
        out.append(f'<path d="{blob(sx, sy, r * 0.07, r * 0.11, seed + i, 0.1, 8, i * 45)}" fill="#E8B060"/>')
    out.append(f'<path d="{blob(cx, cy, r * 0.15, r * 0.15, seed, 0.1, 8)}" fill="#4A220E"/></g>')
    return "".join(out)


def steam_wisps(cx, y, h, seed, col="#FFFFFF", n=3, gap=28, w=7, op=0.75):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        x0 = cx + (i - (n - 1) / 2) * gap
        a = rnd.uniform(10, 15) * (1 if i % 2 else -1)
        pts = [(x0, y), (x0 + a, y - h * 0.25), (x0 - a * 0.6, y - h * 0.55), (x0 + a * 0.5, y - h * 0.8), (x0 + a * 0.2, y - h)]
        pts = catmull(pts, 5)
        out.append(taper(pts, w, 0.8, col, op))
    return "".join(out)


@design("pumpkin-spice")
def pumpkin_spice():
    D = Doc("ps")
    out = [paper(D.nid(), "#F0C870", "#8A5A20", 31)]
    out.append(blooms(8, ["#F6DA90", "#E0A040", "#F8E4B0"], 8, (0, 0, 600, 600), (100, 200), (0.12, 0.22)))
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 600, 600), ["#F6D888", "#E2A848", "#F8E0A8"], 32, n=90,
                       angle=-25, length=(60, 160), width=(6, 14), opacity=(0.1, 0.25)))
    out.append(soft_glow(D, 300, 210, 260, "#FFF2C8", 0.6))
    # saucer
    out.append(cast(D, 310, 356, 180, 28, strength=0.35))
    sau = blob_pts(300, 340, 162, 32, 3, 0.015, 30)
    out.append(painted(D, sau, ("#FFFDF4", "#F2E6CE", "#B8A07A"), 4, sdir=(0.3, 1), sk=0.25, angle=0, n=60, slen=(30, 80), sw=(1.5, 3.5), inkw=2, hi=0.5))
    out.append(f'<path d="{blob(300, 334, 112, 18, 5, 0.03, 20)}" fill="#D8C4A0" opacity="0.6"/>')
    # small pumpkin behind on the left, cinnamon quills leaning on the right
    out.append(pumpkin(D, 138, 290, 116, 84, ("#F6A050", "#D9682A", "#8E3412"), 6, leafc="olive", cast_op=0.25))
    out.append(cinnamon_stick(D, 392, 338, 470, 212, 18, 7) + cinnamon_stick(D, 412, 342, 500, 234, 15, 8))
    # the mug: cream glaze, hand-painted rust band with diamonds and dots
    cx, top, w, h = 290, 210, 180, 128
    l, r, b = cx - w / 2, cx + w / 2, top + h
    hp = catmull([(r - 8, top + 24), (r + 44, top + 22), (r + 50, top + 64), (r + 30, top + 96), (r - 12, top + 98)], 6)
    out.append(taper(hp, 24, 20, "#A88A66"))
    out.append(taper(hp, 15, 12, "#F2E6CE"))
    out.append(ink(smooth_open(hp), "#FFFFFF", 3, 2, 1, 0.4))
    body = [(l, top), (cx - w * 0.25, top + 1), (cx, top + 2), (cx + w * 0.25, top + 1), (r, top), (r - 3, top + h * 0.45), (r - 9, b - 22), (r - 26, b),
            (cx, b + 2), (l + 26, b), (l + 9, b - 22), (l + 3, top + h * 0.45)]
    bd = smooth_closed(body)
    out.append(painted(D, body, ("#FFFDF4", "#F2E6CE", "#B8A07A"), 9, sdir=(1, 0.1), sk=0.22, angle=-90, n=110, slen=(20, 60), sw=(1.5, 4), inkw=2.4, hi=0.6, hik=0.07))
    cid = D.clip(f'<path d="{bd}"/>')
    by_ = top + 60
    band = [f'<path d="M {l - 10} {by_ - 1} Q {cx} {by_ + 5} {r + 10} {by_ - 1} L {r + 10} {by_ + 31} Q {cx} {by_ + 37} {l - 10} {by_ + 31} Z" fill="#B4532A"/>',
            strokes(D.nid(), f"M {l - 10} {by_ - 1} L {r + 10} {by_ - 1} L {r + 10} {by_ + 31} L {l - 10} {by_ + 31} Z", (l - 20, by_ - 4, r + 10, by_ + 34),
                    ["#D06A3A", "#8E3414"], 10, n=40, angle=-3, length=(20, 60), width=(2, 4), opacity=(0.2, 0.45))]
    for i, x in enumerate(range(int(l) + 12, int(r), 24)):
        yy = by_ + 15 + 2.5 * (1 - ((x - cx) / (w / 2)) ** 2)
        band.append(f'<path d="{blob(x, yy, 7, 9, 20 + i, 0.08, 8, 45)}" fill="#F6EAD6"/>')
        band.append(f'<circle cx="{x + 12}" cy="{yy:.1f}" r="2.4" fill="#F2C860"/>')
    band.append(f'<path d="M {l - 10} {by_ - 8} Q {cx} {by_ - 2} {r + 10} {by_ - 8}" stroke="#B4532A" stroke-width="3" fill="none"/>'
                f'<path d="M {l - 10} {by_ + 39} Q {cx} {by_ + 45} {r + 10} {by_ + 39}" stroke="#B4532A" stroke-width="3" fill="none"/>')
    band.append(f'<path d="{bd} {smooth_closed(shift(body, -w * 0.18, 0))}" fill-rule="evenodd" fill="#5A2A10" opacity="0.28"/>')
    out.append(f'<g {cid}>{"".join(band)}</g>')
    out.append(taper([(l + 22, top + 20), (l + 26, top + 60), (l + 30, b - 26)], 7, 2, "#FFFFFF", 0.55))
    # rim + coffee
    out.append(f'<path d="{blob(cx, top, w / 2 + 1, 15, 11, 0.01, 24)}" fill="#C8B08A"/>')
    out.append(f'<path d="{blob(cx, top + 2, w / 2 - 9, 10, 12, 0.02, 24)}" fill="#7A4626"/>')
    out.append(ink(blob(cx, top, w / 2 + 1, 15, 11, 0.01, 24), INK, 2, 3, 1, 0.6))
    # whipped cream, piled and swirled, dusted with cinnamon
    puffs = [(290, 202, 86, 20), (246, 190, 40, 22), (334, 190, 42, 22), (290, 182, 58, 24), (268, 164, 36, 20), (312, 162, 36, 20), (292, 144, 28, 18), (298, 126, 15, 14)]
    for i, (px, py, rx, ry) in enumerate(puffs):
        pts = blob_pts(px, py, rx, ry, 30 + i, 0.05, 16)
        out.append(painted(D, pts, ("#FFFFFF", "#FBF2E2", "#C8B494"), 30 + i, sdir=(0.6, 0.8), sk=0.22, angle=-15, n=12, slen=(rx * 0.3, rx * 0.8), sw=(1, 2.5),
                           cols=["#FFFFFF", "#E8D8BC"], inkw=1.6, inkop=0.5, hi=0.6, curve=0.5))
    rnd = random.Random(4)
    out.append(specks(4, (242, 128, 340, 200), ["#8A4422", "#A0582E"], 70, (0.8, 2.0), (0.4, 0.9)))
    out.append(steam_wisps(292, 112, 70, 2, "#FFFFFF", 3, 30, 7, 0.75))
    # star anise and cloves on the saucer
    out.append(anise(D, 186, 344, 28, 12, 40))
    for x, y, r_ in ((404, 358, 30), (428, 350, -20), (222, 364, 70)):
        out.append(f'<g transform="rotate({r_} {x} {y})">' + taper([(x, y + 7), (x, y - 6)], 4, 3, "#4A220E") + f'<path d="{blob(x, y - 9, 4.5, 4.5, x, 0.2, 8)}" fill="#5E2E14"/></g>')
    # lettering
    out.append(letters(D, 300, 452, "pumpkin spice", SERIF_IT, 86, "#5A2A14", ["#3E1A08", "#7E4426", "#8E5432"], 16, max_w=480, shadow="#F8E2A8", soff=(0.02, 0.03), angle=-35))
    out.append(ribbon(D, 300, 500, 360, 52, ("#D06A3A", "#B4532A", "#6E2A10"), 17, tail=42))
    out.append(letters(D, 300, 517, "& EVERYTHING NICE", BEBAS, 46, "#FBF0DC", ["#FFFFFF", "#F2D8B0"], 18, ls=4, max_w=320, angle=-70, wob=0.4))
    return finish(D, out, 51)


# ================================================================ 8. leaf me alone — a fox asleep in the leaf pile
@design("leaf-me-alone")
def leaf_me_alone():
    D = Doc("lma")
    out = [paper(D.nid(), "#E6E2C8", "#6E7450", 61)]
    out.append(blooms(9, ["#C8CCA0", "#F2EAD0", "#B8BE90"], 8, (0, 0, 600, 600), (100, 200), (0.12, 0.25)))
    out.append(soft_glow(D, 300, 430, 260, "#FFF6DA", 0.6))
    out.append(letters(D, 300, 128, "LEAF ME", JOS, 72, "#3E2A1C", ["#5A3E2A", "#2A1A10"], 21, ls=12, max_w=380, angle=-70, wob=0.5))
    out.append(letters(D, 300, 238, "alone", SERIF_IT, 124, "#B4532A", ["#D86A3A", "#8E3414", "#E88A4A"], 22, max_w=360, shadow="#8A9068", soff=(0.025, 0.04), angle=-35, hi="#FFD9B0"))
    out.append('<g transform="translate(300 520) scale(1.12) translate(-300 -520)">')
    out.append(cast(D, 300, 524, 260, 26, "#3A3A20", 0.4))
    # the leaf pile
    rnd = random.Random(5)
    items = []
    for _ in range(78):
        a = rnd.uniform(0, math.pi)
        dd = rnd.random() ** 0.6
        x = 300 + math.cos(a) * dd * 225 * (1 if rnd.random() < 0.5 else -1)
        y = 520 - math.sin(a) * dd * 50 + rnd.uniform(-4, 22)
        items.append((y, x, rnd.choice(("maple", "maple", "oak", "slim")), rnd.uniform(15, 24), rnd.choice(list(LEAF_PALS)), rnd.uniform(-180, 180)))
    for i, (y, x, k, sz, p, r) in enumerate(sorted(items)):
        out.append(leaf(D, k, x, y, sz, p, r, 300 + i, inkw=1.0))
    # the fox, curled up asleep
    fur = ("#F8B866", "#E27A34", "#9A3E16")
    body = sample_d("M 206 428 C 206 362 296 336 376 348 C 456 360 474 432 446 466 C 410 502 268 504 228 486 C 210 476 206 452 206 428 Z", 8)
    out.append(painted(D, body, fur, 70, sdir=(0.5, 0.9), sk=0.14, angle=-15, n=170, slen=(14, 40), sw=(1.5, 3.5),
                       cols=["#FFD090", "#C05A22", "#F6A050", "#A8461A"], inkw=2.4, hi=0.4, curve=0.4))
    out.append(taper(catmull([(250, 362), (300, 346), (360, 344), (404, 356)], 5), 5, 2, "#FFE2B0", 0.6))
    out.append(f'<path d="{blob(238, 480, 20, 10, 3, 0.08, 10)}" fill="#2E1E16"/>')
    tail = sample_d("M 446 452 C 476 482 446 520 382 522 C 300 526 216 516 160 494 C 136 484 138 464 160 462 C 226 474 316 482 380 474 C 420 470 438 462 446 452 Z", 8)
    out.append(painted(D, tail, ("#F6A858", "#DA6E2C", "#8E3412"), 71, sdir=(0.2, 1), sk=0.2, angle=-4, n=150, slen=(16, 44), sw=(1.5, 3.5),
                       cols=["#FFD090", "#B8501E", "#F6A050"], inkw=2.4, hi=0.4, curve=0.3))
    tcid = D.clip(f'<path d="{smooth_closed(tail)}"/>')
    tip = blob(160, 484, 62, 40, 72, 0.12, 14)
    out.append(f'<g {tcid}><path d="{tip}" fill="#FBF3E6"/>'
               + strokes(D.nid(), tip, (90, 440, 230, 530), ["#FFFFFF", "#D8C8B0"], 73, n=30, angle=-4, length=(10, 30), width=(1, 2.5), opacity=(0.3, 0.6))
               + "</g>")
    out.append(ink(smooth_closed(tail), INK, 2.2, 74, 1, 0.6))
    # head resting on the tail
    ear1 = [(172, 376), (160, 328), (208, 364)]
    out.append(painted(D, ear1, ("#5A3A2A", "#2E1E16", "#1A100A"), 75, sdir=(1, 0), sk=0.1, angle=-70, n=8, inkw=2, hi=0.3))
    out.append(f'<path d="M 172 368 L 166 340 L 192 364 Z" fill="#F6D8B0" opacity="0.8"/>')
    head = sample_d("M 254 402 C 250 372 222 358 196 362 C 172 366 156 382 148 402 L 120 436 C 114 446 122 454 132 452 L 170 454 C 200 464 240 452 254 424 Z", 8)
    out.append(painted(D, head, ("#FFC074", "#E57C36", "#A8461A"), 76, sdir=(0.5, 0.9), sk=0.14, angle=-160, n=70, slen=(8, 22), sw=(1.2, 2.6),
                       cols=["#FFD090", "#C05A22", "#F6A050"], inkw=2.4, hi=0.45))
    ear2 = [(208, 370), (228, 322), (246, 384)]
    out.append(painted(D, ear2, ("#5A3A2A", "#2E1E16", "#1A100A"), 77, sdir=(1, 0), sk=0.1, angle=-70, n=8, inkw=2, hi=0.3))
    out.append(f'<path d="M 214 366 L 227 336 L 238 374 Z" fill="#F6D8B0" opacity="0.85"/>')
    muzzle = sample_d("M 122 450 L 170 454 C 196 462 222 452 238 436 C 214 440 196 432 180 424 C 160 430 140 436 122 446 Z", 6)
    out.append(painted(D, muzzle, ("#FFFFFF", "#FBF3E6", "#D8C4A8"), 78, sdir=(0.3, 1), sk=0.2, angle=-170, n=14, inkw=1.6, inkop=0.5, hi=0.3))
    out.append(taper(catmull([(234, 404), (244, 418), (254, 414)], 4), 6, 2, "#FBF3E6", 0.8))
    out.append(f'<path d="{blob(122, 442, 7.5, 6, 79, 0.08, 10)}" fill="#2A1A14"/><path d="{blob(120, 440, 2.4, 1.6, 80, 0.1, 8)}" fill="#FFFFFF" opacity="0.6"/>')
    out.append(pline([(166, 408), (174, 415), (184, 417), (196, 410)], "#2A1A14", 3.2, 81, 1, 1))
    out.append(pline([(170, 413), (167, 419)], "#2A1A14", 2, 82, 1, 1) + pline([(178, 416), (177, 423)], "#2A1A14", 2, 83, 1, 1) + pline([(187, 416), (189, 422)], "#2A1A14", 2, 84, 1, 1))
    out.append(f'<path d="{blob(172, 432, 12, 6, 85, 0.1, 10)}" fill="#F08A6A" opacity="0.35"/>')
    # a leaf landed on the sleeper, more scattered on top of the pile
    out.append(leaf(D, "maple", 340, 350, 27, "gold", 24, 90))
    out.append(leaf(D, "oak", 442, 500, 22, "red", -70, 91) + leaf(D, "maple", 176, 512, 21, "plum", 140, 92) + leaf(D, "slim", 520, 496, 19, "gold", 70, 93))
    for i, (x, y, sz) in enumerate(((128, 366, 34), (110, 330, 28), (98, 298, 22))):
        out.append(letters(D, x, y, "z", SERIF_IT, sz, "#5A6038", ["#3E4426"], 95 + i, max_w=60, angle=-40))
    out.append("</g>")
    out.append(falling(D, [("maple", 500, 300, 20, "orange", 30), ("slim", 92, 250, 18, "gold", -30), ("oak", 510, 192, 20, "brown", 20)]))
    return finish(D, out, 61, "#3A3A20", 0.9)


# ================================================================ 9. happy fall, y'all — a red farm truck hauling pumpkins
def wheel(D, cx, cy, r, seed):
    out = [painted(D, blob_pts(cx, cy, r, r, seed, 0.02, 20), ("#5A4A44", "#2E2422", "#140E0C"), seed, sdir=(0.5, 0.8), sk=0.12, angle=-30, n=20, inkw=2, hi=0.3)]
    out.append(painted(D, blob_pts(cx, cy, r * 0.5, r * 0.5, seed + 1, 0.02, 16), ("#FFFDF4", "#EFE3CB", "#A8947A"), seed + 1, sdir=(0.6, 0.6), sk=0.2, angle=-40, n=8, inkw=1.6, hi=0.5))
    out.append(f'<path d="{blob(cx, cy, r * 0.2, r * 0.2, seed + 2, 0.05, 10)}" fill="#B83A2A"/>')
    for k in range(5):
        a = math.radians(k * 72 + 20)
        out.append(f'<circle cx="{cx + math.cos(a) * r * 0.34:.1f}" cy="{cy + math.sin(a) * r * 0.34:.1f}" r="{r * 0.04:.1f}" fill="#8A7A66"/>')
    return "".join(out)


@design("happy-fall-yall")
def happy_fall_yall():
    D = Doc("hfy")
    out = [sky(D, [(0, "#F2C8A0"), (0.35, "#F6D8AE"), (0.62, "#FAE6C0")], 3, 600, ["#FFF0D8", "#EEB894", "#F6D08A"], 50)]
    out.append(soft_glow(D, 440, 330, 230, "#FFF4D0", 0.8))
    out.append(blooms(11, ["#E8A27A", "#F6D08A", "#FFFFFF"], 6, (0, 0, 600, 300)))
    # far field and trees
    l1 = ridge([(-20, 372), (160, 360), (330, 368), (480, 356), (620, 366)], 4, 8)
    out.append(hill(D, l1, 600, ("#E8C27A", "#D0A050", "#9A6A2A"), 4, angle=-2, inkw=1.4, inkop=0.4))
    for i, (x, y, rx, pals) in enumerate(((70, 334, 40, [("#F08A50", "#CC4E26", "#7E2A14")]), (520, 330, 44, [("#F6C060", "#E0902A", "#9A561A"), ("#F08A50", "#CC4E26", "#7E2A14")]),
                                          (566, 348, 26, [("#C8C070", "#8E9244", "#56602A")]))):
        out.append(taper([(x, y + rx * 0.9), (x + 1, y + 6)], rx * 0.16, rx * 0.08, "#4A3018"))
        out.append(dab_crown(D, x, y, rx, rx * 0.95, pals, 80 + i, int(rx * 1.4), (5, 9)))
    # rows of stubble
    for k in range(6):
        y = 384 + k * k * 6 + k * 10
        out.append(pline([(-10, y), (300, y - 3), (610, y)], "#B8863A", 1.4 + k * 0.5, k, 0.5, 1))
    out.append(grass(5, (-10, 400, 610, 600), ["#C89A4A", "#E2BC6A", "#A87A34"], 120, (6, 16), w=1.2, op=(0.4, 0.8)))
    # the truck (faces left)
    out.append(cast(D, 300, 512, 240, 18, strength=0.42))
    # pumpkins & a hay bale in the bed, behind the bed wall
    from gouache import hay_bale
    out.append(hay_bale(D.nid(), 300, 362, 82, 52, 7))
    out.append(pumpkin(D, 418, 384, 82, 58, PUMP, 8, vine=False, cast_op=0, leafc="olive"))
    out.append(pumpkin(D, 470, 392, 56, 42, CREAM, 9, vine=False, cast_op=0))
    out.append(pumpkin(D, 380, 396, 50, 36, GOLD, 10, vine=False, cast_op=0))
    red = ("#E8604A", "#C0302A", "#6E1414")
    bed = [(286, 400), (390, 398), (502, 400), (506, 440), (502, 482), (390, 484), (286, 482), (284, 440)]
    out.append(painted(D, bed, red, 11, sdir=(0.3, 1), sk=0.12, angle=-2, n=60, slen=(20, 60), sw=(1.5, 3.5), inkw=2.4, hi=0.35))
    for y in (418, 444):
        out.append(pline([(292, y), (400, y + 1), (498, y)], "#6E1414", 2, y, 0.5, 1))
    cab = [(198, 482), (198, 400), (206, 346), (230, 330), (270, 330), (288, 342), (292, 400), (292, 482)]
    out.append(painted(D, cab, red, 12, sdir=(0.5, 0.8), sk=0.12, angle=-90, n=60, slen=(15, 40), sw=(1.5, 3.5), inkw=2.4, hi=0.4))
    win = [(214, 392), (218, 352), (234, 342), (268, 342), (278, 352), (280, 392)]
    out.append(painted(D, win, ("#F6F2E6", "#C8D8D8", "#7A9A9E"), 13, sdir=(1, 0.5), sk=0.2, angle=-40, n=12, inkw=2, hi=0.5))
    out.append(taper([(228, 384), (250, 348)], 6, 3, "#FFFFFF", 0.7) + taper([(244, 386), (262, 356)], 3, 1.5, "#FFFFFF", 0.6))
    out.append(pline([(282, 420), (270, 420)], "#3A1A10", 3, 1, 0.9, 1))
    hood = [(96, 482), (92, 444), (102, 414), (130, 400), (200, 396), (202, 440), (200, 482)]
    out.append(painted(D, hood, red, 14, sdir=(0.5, 0.8), sk=0.12, angle=-4, n=50, slen=(15, 45), sw=(1.5, 3.5), inkw=2.4, hi=0.4))
    for y in (424, 440, 456):
        out.append(pline([(160, y), (186, y)], "#6E1414", 2, y, 0.6, 1))
    # fenders over the wheels
    for fx, seed in ((168, 15), (432, 16)):
        fp = [(fx - 62, 486), (fx - 56, 452), (fx - 30, 430), (fx + 30, 430), (fx + 56, 452), (fx + 62, 486)]
        out.append(painted(D, fp, ("#D8504A", "#A8241E", "#5E0E0E"), seed, sdir=(0.4, 1), sk=0.15, angle=0, n=30, inkw=2.4, hi=0.45))
    out.append(wheel(D, 168, 492, 38, 20) + wheel(D, 432, 492, 38, 21))
    # grille, headlight, bumpers
    out.append(painted(D, [(84, 486), (82, 446), (96, 440), (100, 486)], ("#FFFDF4", "#D8D0C0", "#8A8070"), 22, sdir=(1, 0), sk=0.2, angle=-90, n=6, inkw=1.8, hi=0.4))
    for y in (452, 462, 472):
        out.append(pline([(86, y), (96, y)], "#6A6050", 1.6, y, 0.8, 1))
    out.append(soft_glow(D, 116, 432, 30, "#FFF2C0", 0.8))
    out.append(painted(D, blob_pts(116, 432, 11, 12, 23, 0.03, 12), ("#FFFFFF", "#FFF2C0", "#C8A860"), 23, sdir=(0.5, 0.5), sk=0.2, angle=-40, n=4, inkw=1.8, hi=0.6))
    out.append(taper([(70, 492), (100, 494), (126, 492)], 9, 9, "#D8D0C0") + pline([(70, 492), (126, 492)], INK, 1.6, 24, 0.6, 1))
    out.append(taper([(492, 490), (514, 490)], 8, 8, "#D8D0C0") + pline([(492, 490), (514, 490)], INK, 1.6, 25, 0.6, 1))
    out.append(pline([(298, 404), (298, 480)], "#6E1414", 2, 26, 0.6, 1))
    out.append(taper([(110, 404), (190, 400)], 3, 2, "#FFB0A0", 0.5) + taper([(296, 404), (490, 402)], 3, 2, "#FFB0A0", 0.5))
    # front: a bundle of corn stalks and pumpkins at the roadside
    from gouache import corn_stalk
    for i, (x, lean) in enumerate(((532, -0.06), (546, 0.02), (560, 0.08), (524, -0.12))):
        out.append(corn_stalk(x, 600, 150 + i * 8, 300 + i, lean))
    out.append(pumpkin(D, 84, 560, 96, 64, PUMP, 30, leafc="olive") + pumpkin(D, 170, 576, 64, 44, GOLD, 31, vine=False))
    out.append(pumpkin(D, 470, 574, 70, 48, CREAM, 32, vine=False))
    # lettering
    out.append(letters(D, 300, 128, "happy fall,", SERIF_IT, 96, "#6E2E16", ["#4A1C0A", "#8E4426", "#A0582E"], 33, max_w=430, shadow="#FFF2DC", soff=(-0.02, -0.025), angle=-35))
    out.append(letters(D, 300, 280, "Y'ALL", BEBAS, 180, "#C24E22", ["#E8792E", "#A8401A", "#F09A50", "#E06A28"], 34, ls=10, max_w=400,
                       shadow="#6E2A10", angle=-78, hi="#FFD9A8", inkc="#5A200C", inkw=1.8))
    return finish(D, out, 71)


# ================================================================ 10. whooo loves fall? — an owl in a knit scarf at sunset
def feather_rows(cx, cy, rx, ry, seed, col, rows=6, per=6, s=7, w=1.8, op=0.7):
    """Rows of little v-shaped feather marks, like a pen drawing of an owl's breast."""
    rnd = random.Random(seed)
    out = []
    for r in range(rows):
        t = (r + 0.5) / rows
        y = cy - ry + 2 * ry * t
        half = rx * math.sqrt(max(0.0, 1 - ((y - cy) / ry) ** 2)) * 0.82
        k = max(2, int(per * half / rx + 0.5))
        for i in range(k):
            x = cx - half + (2 * half) * (i + 0.5 + (0.5 if r % 2 else 0) * 0.5) / k
            if abs(x - cx) > half:
                continue
            ss = s * rnd.uniform(0.8, 1.15)
            out.append(pline([(x - ss, y - ss * 0.35), (x, y + ss * 0.45), (x + ss, y - ss * 0.35)], col, w, rnd.randint(0, 999), op, 1))
    return "".join(out)


@design("whooo-loves-fall")
def whooo_loves_fall():
    D = Doc("wlf")
    out = [sky(D, [(0, "#3A2A4A"), (0.28, "#6A3A56"), (0.5, "#B8606A"), (0.68, "#EE9A62"), (0.8, "#F6C47A"), (1, "#F6C47A")], 3, 600,
               ["#4A3458", "#8A4A62", "#D07A6A", "#F2B070"], 110, angle=-3, sop=(0.08, 0.22))]
    out.append(blooms(4, ["#8A4A6A", "#F2A070", "#5A3A5A"], 7, (0, 0, 600, 420), (70, 150), (0.08, 0.14)))
    out.append(soft_glow(D, 300, 360, 300, "#FFD898", 0.75))
    out.append(soft_glow(D, 300, 372, 150, "#FFF0C8", 0.6))
    rnd = random.Random(6)
    for _ in range(26):
        x, y = rnd.uniform(30, 570), rnd.uniform(24, 200)
        if 200 < x < 400 and y > 150:
            continue
        r = rnd.uniform(0.8, 2)
        out.append(f'<path d="{blob(x, y, r, r, rnd.randint(0, 99), 0.2, 6)}" fill="#FBEFD0" opacity="{rnd.uniform(0.4, 0.9):.2f}"/>')
    # distant treeline in dusk plum
    for layer, (base, cols, hh) in enumerate(((452, [("#B8707A", "#9A5468", "#7A3E56")], 26), (480, [("#8A4A62", "#6E3650", "#4E2440")], 34))):
        x = -20
        while x < 640:
            out.append(dab_crown(D, x, base - hh * 0.4, hh * rnd.uniform(0.8, 1.3), hh * rnd.uniform(0.7, 1.0), cols, 400 + layer * 50 + int(x), 12, (5, 9), inkw=0))
            x += rnd.uniform(28, 46)
        out.append(f'<rect x="-10" y="{base - 6}" width="620" height="140" fill="{cols[0][2]}"/>')
    out.append(hill(D, ridge([(-20, 506), (200, 498), (420, 508), (620, 500)], 7, 5), 610, ("#5A2E46", "#3E1E34", "#260F20"), 7, inkw=0, sop=(0.1, 0.3)))
    # the branch, entering from the left, with oak leaves and acorns
    br = [(-30, 448), (80, 436), (190, 430), (300, 426), (410, 420), (500, 408), (560, 392), (640, 372)]
    out.append(taper(br, 30, 10, "#4A2E1E"))
    out.append(strokes(D.nid(), smooth_closed([(x, y - 12) for x, y in br] + [(x, y + 12) for x, y in br[::-1]]), (-30, 360, 640, 470),
                       ["#7A5236", "#2E1A10", "#9A6E48"], 8, n=70, angle=-4, length=(20, 60), width=(1, 2.4), opacity=(0.3, 0.7), curve=0.1))
    out.append(taper([(x, y - 9) for x, y in br[:6]], 6, 2, "#C88A5A", 0.55))
    out.append(pline(br, INK, 2.2, 3, 0.7))
    out.append(taper([(470, 414), (512, 384), (536, 360)], 9, 3, "#4A2E1E") + taper([(120, 434), (96, 404), (82, 384)], 8, 3, "#4A2E1E"))
    for i, (k, x, y, sz, p, r) in enumerate((("oak", 536, 356, 34, "gold", 18), ("oak", 82, 380, 32, "red", -24), ("oak", 160, 428, 26, "orange", -70),
                                              ("oak", 452, 418, 28, "red", 64), ("maple", 520, 398, 24, "orange", 120))):
        out.append(leaf_hang(D, k, x, y, sz, p, r, 30 + i))
    out.append(acorn(D, 228, 432, 18, -6, 7) + acorn(D, 404, 426, 18, 10, 8))
    # the owl
    cx = 300
    body = sample_d("M 300 186 C 366 186 402 236 404 300 C 408 368 384 422 300 426 C 216 422 192 368 196 300 C 198 236 234 186 300 186 Z", 10)
    ow = ("#D09A62", "#9A643A", "#4E2E18")
    out.append(cast(D, 300, 428, 110, 9, strength=0.4))
    for sg in (-1, 1):
        tuft = [(cx + sg * 58, 204), (cx + sg * 84, 156), (cx + sg * 98, 166), (cx + sg * 96, 226)]
        out.append(painted(D, tuft, ow, 40 + sg, sdir=(0.5, 0.8), sk=0.15, angle=-70 if sg < 0 else -110, n=10, inkw=2.2, hi=0.3))
    out.append(painted(D, body, ow, 42, sdir=(0.6, 0.7), sk=0.13, angle=-90, n=160, slen=(10, 30), sw=(1.2, 3), curve=0.4,
                       cols=["#E8B880", "#7A4A28", "#B87A48", "#F0C890"], inkw=2.6, hi=0.4))
    # breast with feather marks
    bp = blob_pts(cx, 360, 66, 62, 43, 0.04, 18)
    out.append(painted(D, bp, ("#FBEBD0", "#EFD3A8", "#C8A070"), 44, sdir=(0.6, 0.7), sk=0.12, angle=-90, n=40, inkw=0, hi=0.4))
    out.append(feather_rows(cx, 364, 62, 54, 45, "#8A5A34", rows=5, per=6, s=7, w=2))
    # wings folded at the sides, scalloped
    for sg, seed in ((-1, 50), (1, 51)):
        wp = sample_d(f"M {cx + sg * 72} 286 C {cx + sg * 104} 300 {cx + sg * 110} 360 {cx + sg * 96} 404 C {cx + sg * 88} 420 {cx + sg * 70} 418 {cx + sg * 64} 400 C {cx + sg * 58} 360 {cx + sg * 60} 310 {cx + sg * 72} 286 Z", 8)
        out.append(painted(D, wp, ("#B07A48", "#7A4A26", "#3E2210"), seed, sdir=(-sg * 0.3, 0.8), sk=0.15, angle=-80, n=40, inkw=2.2, hi=0.35))
        for j in range(4):
            y = 314 + j * 24
            x = cx + sg * (78 + j * 3)
            out.append(pline([(x - sg * 12, y), (x, y + 10), (x + sg * 12, y + 4)], "#F0C890", 2, seed + j, 0.55, 1))
    # facial disc: two overlapping painted rounds, radial strokes
    for sg in (-1, 1):
        fp = blob_pts(cx + sg * 36, 262, 50, 46, 60 + sg, 0.03, 18)
        out.append(painted(D, fp, ("#FFF0D6", "#F0D4A8", "#C89A68"), 61 + sg, sdir=(0, 1), sk=0.1, angle=-90, n=0 or 6, inkw=0, hi=0.3))
    fcid = D.clip(f'<path d="{smooth_closed(blob_pts(cx - 36, 262, 50, 46, 59, 0.03, 18))}"/><path d="{smooth_closed(blob_pts(cx + 36, 262, 50, 46, 61, 0.03, 18))}"/>')
    rays = []
    for sg in (-1, 1):
        for a in range(0, 360, 14):
            ra = math.radians(a)
            rays.append(f'<path d="M {cx + sg * 36 + math.cos(ra) * 30:.1f} {262 + math.sin(ra) * 28:.1f} L {cx + sg * 36 + math.cos(ra) * 52:.1f} {262 + math.sin(ra) * 48:.1f}"/>')
    out.append(f'<g {fcid}><g stroke="#C89A68" stroke-width="1.6" opacity="0.55">{"".join(rays)}</g></g>')
    out.append(ink(smooth_closed(blob_pts(cx - 36, 262, 50, 46, 59, 0.03, 18)), "#7A4A26", 2, 62, 1, 0.6))
    out.append(ink(smooth_closed(blob_pts(cx + 36, 262, 50, 46, 61, 0.03, 18)), "#7A4A26", 2, 63, 1, 0.6))
    # brow V
    for sg in (-1, 1):
        out.append(taper([(cx + sg * 8, 240), (cx + sg * 22, 226), (cx + sg * 44, 222), (cx + sg * 66, 232)], 3, 7, "#7A4A26", 0.85))
        out.append(taper([(cx + sg * 12, 236), (cx + sg * 28, 225), (cx + sg * 48, 223)], 2, 3, "#FFF4E0", 0.7))
    # eyes: big amber irises, dark pupils, wet highlights
    for sg in (-1, 1):
        ex = cx + sg * 36
        out.append(f'<path d="{blob(ex, 264, 30, 30, 70 + sg, 0.02, 16)}" fill="#3A2214"/>')
        ip = blob_pts(ex, 264, 26, 26, 71 + sg, 0.02, 16)
        out.append(painted(D, ip, ("#FFD870", "#F2A632", "#B8661A"), 72 + sg, sdir=(0.3, 1), sk=0.14, angle=-60, n=14, inkw=0, hi=0.5))
        out.append(f'<path d="{blob(ex + sg * 2, 266, 13, 14, 73 + sg, 0.04, 12)}" fill="#1A0E08"/>')
        out.append(f'<path d="{blob(ex - 7, 256, 5.5, 4.5, 74 + sg, 0.1, 8)}" fill="#FFFFFF" opacity="0.95"/><path d="{blob(ex + 8, 274, 2.5, 2, 75, 0.1, 8)}" fill="#FFFFFF" opacity="0.7"/>')
    # beak
    beak = [(cx - 11, 286), (cx + 11, 286), (cx + 2, 314), (cx - 2, 314)]
    out.append(painted(D, beak, ("#F6D07A", "#D89A3A", "#8A5A1A"), 76, sdir=(1, 0.4), sk=0.2, angle=-90, n=5, inkw=1.8, hi=0.4))
    # a hand-knit scarf: ribbed band and a fringed tail over the right side
    sc = ("#E2683A", "#B8401E", "#6E1E0E")
    band = sample_d("M 228 318 C 262 340 338 340 372 318 C 378 332 376 346 370 352 C 336 372 264 372 230 352 C 222 344 222 330 228 318 Z", 8)
    out.append(painted(D, band, sc, 80, sdir=(0, 1), sk=0.18, angle=-90, n=50, slen=(6, 16), sw=(1, 2.4), inkw=2.2, hi=0.35))
    scid = D.clip(f'<path d="{smooth_closed(band)}"/>')
    ribs = "".join(f'<path d="M {x} 320 Q {x + (x - 300) * 0.04:.1f} 345 {x} 372"/>' for x in range(234, 372, 10))
    out.append(f'<g {scid}><g stroke="#7E2410" stroke-width="2" fill="none" opacity="0.4">{ribs}</g></g>')
    tail = sample_d("M 334 350 C 350 372 352 404 344 438 L 382 446 C 386 404 380 368 362 346 Z", 8)
    out.append(painted(D, tail, sc, 81, sdir=(1, 0.2), sk=0.2, angle=-95, n=26, inkw=2.2, hi=0.3))
    for j in range(3):
        y = 372 + j * 22
        out.append(pline([(346 + j * 0.5, y), (364, y + 4), (380 - j, y + 1)], "#F6D8A8", 3, 82 + j, 0.75, 1))
    for j in range(7):
        x = 345 + j * 5.6
        out.append(pline([(x, 440 + j * 0.9), (x + 1, 456 + (j % 2) * 3)], "#B8401E", 2.6, 90 + j, 0.95, 1))
    # talons gripping the branch
    for sg in (-1, 1):
        fx = cx + sg * 34
        for t in (-9, 0, 9):
            out.append(taper([(fx + t, 414), (fx + t * 1.2, 426), (fx + t * 1.3 + sg, 434)], 7, 2.4, "#E8B052"))
            out.append(pline([(fx + t * 1.2, 426), (fx + t * 1.3 + sg, 434)], "#5A3A10", 1.6, int(fx + t), 0.7, 1))
    # a leaf drifting past, more leaves falling
    out.append(falling(D, [("maple", 96, 250, 24, "gold", -28), ("slim", 512, 238, 22, "red", 36), ("maple", 520, 150, 18, "orange", 12)]))
    # lettering
    out.append(letters(D, 300, 140, "whooo", SERIF_IT, 120, "#FBE6C8", ["#FFF4E0", "#E8C49A", "#FFFFFF", "#F2D2A8"], 21, max_w=330,
                       shadow="#2A1630", angle=-35, hi="#FFFFFF"))
    out.append(letters(D, 300, 534, "LOVES FALL?", BEBAS, 88, "#F6B84A", ["#FFD27A", "#E2902E", "#FFE2A0", "#E8A23A"], 22, ls=8, max_w=440,
                       shadow="#1E0E1A", angle=-78, hi="#FFF0C8"))
    return finish(D, out, 23, "#F4E0C0", 0.75)


# ================================================================ 11. cozy season — a thatched cottage glowing at dusk
def smoke(D, pts, w0, w1, seed, col="#E8DCE6", op=0.55):
    """Chimney smoke: a few soft tapered curls that thin out and fade as they drift."""
    rnd = random.Random(seed)
    path = catmull(pts, 6)
    out = []
    for k in range(3):
        off = [(x + rnd.uniform(-2, 2) + k * 2, y + (k - 1) * (3 + i * 0.25)) for i, (x, y) in enumerate(path)]
        n = len(off)
        cut = off[: n - k * 5] if k else off
        out.append(taper(cut, w0 * (1 - 0.2 * k), w1 * (0.6 + 0.2 * k), col, op * (0.55 - 0.12 * k)))
    return "".join(out)


def glow_window(D, pts, seed, frame="#4A2E1E", glass=("#FFF2B8", "#FFD068", "#E8963A"), bars=True):
    x0, y0, x1, y1 = bbox(pts)
    out = [painted(D, pts, glass, seed, sdir=(0, 1), sk=0.12, angle=-90, n=10, inkw=0, hi=0.6, hik=0.12)]
    if bars:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        out.append(pline([(cx, y0 + 1), (cx + 0.5, y1 - 1)], frame, 3, seed, 1, 1) + pline([(x0 + 1, cy), (x1 - 1, cy + 0.5)], frame, 3, seed + 1, 1, 1))
    out.append(ink(smooth_closed(pts), frame, 3.2, seed + 2, 2, 0.95))
    return "".join(out)


@design("cozy-season")
def cozy_season():
    D = Doc("cz")
    out = [sky(D, [(0, "#2A2E52"), (0.25, "#463E66"), (0.5, "#8A5A78"), (0.68, "#D88272"), (0.8, "#F2B07A"), (1, "#F2B07A")], 3, 600,
               ["#3A3A62", "#6A4A70", "#B06A78", "#E8A07A"], 110, angle=-3, sop=(0.08, 0.2))]
    out.append(blooms(5, ["#5A4A7A", "#C07080", "#3A3A62"], 6, (0, 0, 600, 360), (70, 140), (0.08, 0.14)))
    rnd = random.Random(2)
    for _ in range(34):
        x, y = rnd.uniform(30, 570), rnd.uniform(20, 240)
        r = rnd.uniform(0.8, 2)
        out.append(f'<path d="{blob(x, y, r, r, rnd.randint(0, 99), 0.2, 6)}" fill="#FFF2D8" opacity="{rnd.uniform(0.35, 0.9):.2f}"/>')
    for x, y in ((84, 84), (520, 260), (470, 70)):
        out.append(f'<path d="M {x} {y - 7} Q {x + 1} {y - 1} {x + 7} {y} Q {x + 1} {y + 1} {x} {y + 7} Q {x - 1} {y + 1} {x - 7} {y} Q {x - 1} {y - 1} {x} {y - 7} Z" fill="#FFF2D8" opacity="0.9"/>')
    # rolling hills behind, the last of the light on their crests
    out.append(hill(D, ridge([(-20, 390), (120, 368), (260, 384), (420, 362), (620, 380)], 4, 10), 600, ("#A87080", "#7A4E68", "#4E3048"), 4, inkw=1.2, inkop=0.35, lit="#FFC890"))
    for i, x in enumerate(range(-10, 620, 26)):
        y = 384 + 8 * math.sin(x / 50)
        if 150 < x < 450:
            continue
        out.append(dab_crown(D, x, y - 6, 14, 12, [("#B87A70", "#8A5468", "#5E3850")], 300 + i, 12, (4, 7), inkw=0))
    # ground
    l = ridge([(-20, 470), (160, 462), (300, 468), (460, 458), (620, 466)], 6, 4)
    out.append(hill(D, l, 610, ("#B88E5E", "#866244", "#4E3828"), 6, angle=-3, inkw=1.4, inkop=0.4, sop=(0.15, 0.35)))
    for _ in range(150):
        x, y = rnd.uniform(-10, 610), rnd.uniform(470, 600)
        if 200 < x < 400 and y < 480:
            continue
        sz = 2.5 + (y - 460) / 30
        out.append(f'<path d="{blob(x, y, sz, sz * 0.55, rnd.randint(0, 9999), 0.25, 7, rnd.uniform(-40, 40))}" fill="{rnd.choice(["#E8783A", "#C8442A", "#F2A848", "#9A3A22", "#D8A040"])}" opacity="{rnd.uniform(0.55, 0.95):.2f}"/>')
    # trees either side, crowns lit warm on the inner edge by the windows
    out.append(taper([(106, 470), (110, 400), (104, 340)], 16, 7, "#3E2A22") + taper([(110, 410), (138, 372)], 6, 2, "#3E2A22"))
    out.append(dab_crown(D, 112, 318, 66, 76, [("#F2A458", "#C8622E", "#7A3020"), ("#F6C868", "#D8903A", "#8A5420")], 41, 130, (8, 14), light=(0.8, -0.3), inkw=1.2))
    out.append(taper([(500, 466), (496, 410), (504, 360)], 14, 6, "#3E2A22"))
    out.append(dab_crown(D, 500, 336, 58, 66, [("#E8785A", "#B83E2E", "#6E1E1E"), ("#F2A458", "#C8622E", "#7A3020")], 42, 110, (8, 13), light=(-0.8, -0.3), inkw=1.2))
    # the cottage: plaster walls, a fat thatched roof, a stone chimney
    out.append(cast(D, 304, 474, 150, 12, strength=0.45))
    wall = jitter([(186, 474), (186, 356), (414, 356), (414, 474)], 3, 1.2)
    out.append(painted(D, wall, ("#F6E6C8", "#E2C8A4", "#9A7E68"), 50, sdir=(0.6, 0.3), sk=0.1, angle=-90, n=70, slen=(10, 30), sw=(1.2, 3), inkw=2.4, hi=0.3))
    wcid = D.clip(f'<path d="{smooth_closed(wall)}"/>')
    stones = []
    for i, (sx, sy) in enumerate(((196, 464), (222, 468), (392, 462), (404, 444), (196, 440), (410, 466), (250, 470), (360, 470))):
        stones.append(f'<path d="{blob(sx, sy, rnd.uniform(9, 14), rnd.uniform(6, 9), 60 + i, 0.12, 10)}" fill="#B8A08A" stroke="#6E5A4A" stroke-width="1.6"/>')
    out.append(f'<g {wcid}>{"".join(stones)}</g>')
    # chimney behind the roof ridge
    ch = jitter([(372, 312), (370, 236), (408, 234), (410, 312)], 4, 1)
    out.append(painted(D, ch, ("#C89078", "#9A5E4A", "#5A3028"), 51, sdir=(0.8, 0.2), sk=0.18, angle=-90, n=24, inkw=2.2, hi=0.3))
    chc = D.clip(f'<path d="{smooth_closed(ch)}"/>')
    bricks = "".join(f'<path d="M 360 {y} L 420 {y}"/>' for y in range(244, 312, 11)) + "".join(
        f'<path d="M {x + (5 if (k % 2) else 0)} {244 + k * 11} l 0 11"/>' for k in range(6) for x in range(372, 410, 13))
    out.append(f'<g {chc}><g stroke="#5A3028" stroke-width="1.4" opacity="0.5">{bricks}</g></g>')
    out.append(painted(D, jitter([(364, 240), (364, 228), (414, 228), (414, 240)], 5, 0.8), ("#B07A68", "#7A4A3C", "#4A2820"), 52, sdir=(0.8, 0.5), sk=0.2, angle=0, n=6, inkw=2, hi=0.3))
    out.append(smoke(D, [(388, 228), (386, 216), (398, 210), (424, 208), (452, 214), (482, 211), (508, 202), (528, 192)], 14, 4, 53, "#EADCE8", 0.75))
    roof = [(160, 372), (164, 340), (186, 304), (226, 280), (300, 268), (374, 280), (414, 304), (436, 340), (440, 372), (380, 380), (300, 382), (220, 380)]
    out.append(painted(D, roof, ("#E8BC6E", "#C08A44", "#6E4A22"), 54, sdir=(0.5, 0.8), sk=0.12, angle=-100, n=200, slen=(10, 30), sw=(0.8, 2),
                       cols=["#F2D088", "#8A5A2A", "#D8A858", "#A8742E"], inkw=2.6, hi=0.35, curve=0.15))
    # thatch combing rows and a fringed eave
    rcid = D.clip(f'<path d="{smooth_closed(roof)}"/>')
    rows = "".join(f'<path d="M 150 {y} Q 300 {y - 22 + (y - 300) * 0.1:.0f} 450 {y}"/>' for y in (306, 328, 352))
    out.append(f'<g {rcid}><g stroke="#7A4E22" stroke-width="2" fill="none" opacity="0.45">{rows}</g></g>')
    fr = "".join(f'<path d="M {x:.1f} {374 + 6 * math.sin(x / 9):.1f} l {rnd.uniform(-2, 2):.1f} {rnd.uniform(8, 14):.1f}"/>' for x in [166 + i * 5.5 for i in range(50)])
    out.append(f'<g stroke="#9A6A30" stroke-width="2" stroke-linecap="round" opacity="0.85">{fr}</g>')
    # eyebrow dormer with a round glowing window
    out.append(soft_glow(D, 300, 322, 70, "#FFD878", 0.55))
    out.append(painted(D, [(256, 340), (264, 312), (300, 298), (336, 312), (344, 340), (300, 344)], ("#F0C878", "#C89A50", "#7A5428"), 55, sdir=(0, 1), sk=0.15, angle=-90, n=30, inkw=2.2, hi=0.3))
    out.append(glow_window(D, blob_pts(300, 326, 17, 15, 56, 0.02, 14), 56))
    # windows and door, glowing; light spilling on the ground
    for x in (236, 364):
        out.append(soft_glow(D, x, 420, 74, "#FFD070", 0.55))
    out.append(soft_glow(D, 300, 500, 120, "#FFC860", 0.35))
    for x, seed in ((236, 60), (364, 61)):
        wp = jitter([(x - 26, 440), (x - 26, 396), (x + 26, 396), (x + 26, 440)], seed, 0.8)
        out.append(glow_window(D, wp, seed))
        # window box of mums
        out.append(painted(D, jitter([(x - 32, 444), (x + 32, 444), (x + 30, 458), (x - 30, 458)], seed, 0.6), ("#8A5A3A", "#6A4028", "#3A2014"), seed + 5, sdir=(0, 1), sk=0.2, angle=0, n=8, inkw=1.8, hi=0.3))
        out.append(dab_crown(D, x, 440, 34, 9, [("#F6B04A", "#D8742A", "#8A3A16"), ("#E86A4A", "#B83A2A", "#6E1A12")], seed + 7, 34, (4, 6), inkw=0, base=False))
        out.append(pline([(x - 30, 396), (x + 30, 396)], "#4A2E1E", 4, seed, 1, 1))
    door = [(278, 474), (278, 412), (284, 398), (300, 392), (316, 398), (322, 412), (322, 474)]
    out.append(painted(D, door, ("#C0603A", "#8E3A22", "#4E1A10"), 62, sdir=(0.7, 0.2), sk=0.15, angle=-90, n=20, inkw=2.4, hi=0.3))
    for x in (290, 300, 310):
        out.append(pline([(x, 400 if x == 300 else 404), (x, 470)], "#4E1A10", 1.4, x, 0.5, 1))
    out.append(f'<path d="{blob(313, 438, 2.8, 2.8, 63, 0.1, 8)}" fill="#F2C870"/>')
    out.append(glow_window(D, blob_pts(300, 414, 9, 8, 64, 0.02, 12), 64, bars=False))
    # lantern by the door
    out.append(soft_glow(D, 340, 404, 34, "#FFE08A", 0.85))
    out.append(painted(D, jitter([(334, 412), (334, 398), (346, 398), (346, 412)], 65, 0.4), ("#FFF6C8", "#FFD870", "#C88A2A"), 65, sdir=(0, 1), sk=0.1, angle=-90, n=3, inkw=1.8, hi=0.4))
    out.append(pline([(332, 397), (340, 390), (348, 397)], "#2E1A10", 2, 66, 1, 1) + pline([(340, 390), (340, 384)], "#2E1A10", 2, 67, 1, 1))
    # stepping-stone path, light pooled on it
    for i in range(6):
        t = i / 5
        y = 484 + 112 * t ** 1.2
        w = 18 + 26 * t
        x = 300 + 14 * math.sin(i * 1.3) * t
        sp = blob(x, y, w, 6 + 7 * t, 70 + i, 0.12, 12)
        out.append(f'<path d="{sp}" fill="#D8BC98"/><path d="{sp}" fill="#FFE2A0" opacity="{0.5 - 0.35 * t:.2f}"/>')
        out.append(ink(sp, "#4E3A2E", 1.6, 70 + i, 1, 0.55))
    # firewood stack and pumpkins
    for r_, (y, n0) in enumerate(((462, 5), (448, 4), (434, 3))):
        for j in range(n0):
            lx = 136 + j * 13 + r_ * 6.5
            lg = blob_pts(lx, y, 7, 7, 80 + r_ * 9 + j, 0.05, 10)
            out.append(painted(D, lg, ("#E8C08A", "#C8945A", "#6E4A2A"), 80 + j + r_ * 9, sdir=(0.5, 0.5), sk=0.15, angle=-30, n=3, inkw=1.6, hi=0.3))
            out.append(f'<path d="{blob(lx, y, 3.4, 3.4, 90 + j, 0.1, 8)}" fill="none" stroke="#8A5A2A" stroke-width="1.2"/>')
    out.append(pumpkin(D, 238, 500, 70, 48, PUMP, 91, leafc="olive", cast_op=0.35))
    out.append(pumpkin(D, 378, 504, 56, 40, GOLD, 92, vine=False, cast_op=0.35))
    out.append(pumpkin(D, 418, 514, 40, 30, CREAM, 93, vine=False, cast_op=0.35))
    out.append(grass(14, (-10, 470, 610, 610), ["#5A4630", "#7A6040", "#3E2E22", "#9A7A50"], 160, (10, 24)))
    out.append(falling(D, [("maple", 150, 540, 18, "orange", 40), ("oak", 470, 556, 18, "red", -50), ("slim", 520, 520, 16, "gold", 80),
                           ("maple", 78, 520, 16, "red", -20), ("maple", 214, 256, 16, "gold", -30)]))
    # lettering
    out.append(letters(D, 300, 148, "cozy", DMS, 156, "#FFF0D8", ["#FFFFFF", "#F2D8B0", "#FFF6E6", "#E8C8A0"], 31, max_w=340,
                       shadow="#1E1A36", soff=(0.02, 0.035), angle=-35, hi="#FFFFFF"))
    out.append(ruled(300, 230, "SEASON", "#F6C46A", font=JOS, size=30, ls=14, line_w=44, gap=16))
    return finish(D, out, 33, "#F4E0C0", 0.7)


def rpts(x0, y0, x1, y1, step=18, seed=0, j=0.6):
    """Points around a rectangle (dense enough that the smoothed outline stays straight-sided)."""
    def edge(a, b):
        n = max(2, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        return [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
    c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    pts = []
    for i in range(4):
        pts += edge(c[i], c[(i + 1) % 4])
    return jitter(pts, seed, j) if j else pts


# ================================================================ 12. cat nap season — a tabby asleep on the sunny windowsill
@design("cat-nap-season")
def cat_nap_season():
    D = Doc("cns")
    out = [paper(D.nid(), "#E2B8A4", "#7A4A3A", 71)]
    out.append(blooms(11, ["#D8A090", "#EECAB4", "#C88A7A"], 8, (0, 0, 600, 600), (90, 180), (0.12, 0.22)))
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 610 L -10 610 Z", (-60, -10, 600, 600), ["#EDC6B2", "#D49C88", "#F2D4C0"], 72, n=110,
                       angle=-88, length=(60, 160), width=(5, 12), opacity=(0.1, 0.24), curve=0.08))
    # little painted wallpaper sprigs
    rnd = random.Random(73)
    for gy in range(30, 620, 74):
        for gx in range(20 + (37 if (gy // 74) % 2 else 0), 620, 74):
            x, y = gx + rnd.uniform(-4, 4), gy + rnd.uniform(-4, 4)
            a = rnd.uniform(-30, 30)
            out.append(f'<g transform="rotate({a:.0f} {x:.0f} {y:.0f})" opacity="0.5"><path d="M {x} {y + 9} Q {x + 1} {y} {x} {y - 9}" stroke="#B87A64" stroke-width="1.6" fill="none"/>'
                       f'<path d="{blob(x - 4, y - 2, 4, 2.2, rnd.randint(0, 99), 0.1, 8, -30)}" fill="#C88A70"/><path d="{blob(x + 4, y + 2, 4, 2.2, rnd.randint(0, 99), 0.1, 8, 30)}" fill="#C88A70"/></g>')
    # window: arched opening with the autumn garden outside
    win = "M 168 352 L 168 176 C 168 116 232 86 300 86 C 368 86 432 116 432 176 L 432 352 Z"
    wcid = D.clip(f'<path d="{win}"/>')
    view = [sky(D, [(0, "#B8D0CC"), (0.5, "#EEE0B8"), (1, "#F6D49A")], 74, 360, ["#FFFFFF", "#D8E4D8", "#F8E4B8"], 30, sop=(0.08, 0.2), y0=80)]
    view.append(soft_glow(D, 380, 250, 160, "#FFF4D0", 0.8))
    view.append(hill(D, ridge([(150, 300), (240, 290), (330, 298), (450, 286)], 5, 6), 360, ("#E8B87A", "#C88A50", "#8A5A30"), 75, inkw=1.2, inkop=0.35))
    for i, x in enumerate(range(170, 440, 22)):
        view.append(dab_crown(D, x, 290 + 4 * math.sin(x / 30), 14, 12, [("#F6C070", "#E08A3A", "#A8521E"), ("#F2905A", "#C85A32", "#8A3020")], 500 + i, 12, (4, 7), inkw=0))
    view.append(hill(D, ridge([(150, 330), (300, 324), (450, 332)], 6, 4), 360, ("#C8B070", "#A08A50", "#6E5E34"), 76, inkw=0))
    view.append(taper([(150, 150), (220, 160), (280, 140), (330, 150)], 12, 4, "#5A3A28"))
    for i, (k, x, y, sz, p, r) in enumerate((("maple", 200, 166, 22, "red", 170), ("maple", 252, 156, 22, "orange", 190), ("oak", 300, 152, 20, "gold", 176),
                                              ("maple", 172, 150, 20, "gold", -10), ("slim", 230, 142, 18, "red", 20))):
        view.append(leaf_hang(D, k, x, y, sz, p, r, 510 + i))
    view.append(falling(D, [("maple", 370, 130, 16, "orange", 30), ("slim", 400, 200, 14, "red", -40), ("oak", 330, 236, 14, "gold", 60), ("maple", 200, 250, 14, "red", -20)]))
    out.append(f'<g {wcid}>{"".join(view)}</g>')
    # glass sheen
    out.append(f'<g {wcid}><path d="M 190 300 L 260 100 L 290 100 L 220 300 Z" fill="#FFFFFF" opacity="0.18"/><path d="M 330 340 L 400 140 L 412 140 L 342 340 Z" fill="#FFFFFF" opacity="0.14"/></g>')
    # the frame and mullions, painted cream wood with a pen line
    out.append(f'<path d="{win}" fill="none" stroke="#5A3A2C" stroke-width="26" opacity="0.18" transform="translate(4 5)"/>')
    out.append(f'<path d="{win}" fill="none" stroke="#F6EEDC" stroke-width="22"/>')
    out.append(ink(win, "#B8A48A", 6, 77, 1, 0.35))
    out.append(ink("M 157 356 L 157 176 C 157 106 226 74 300 74 C 374 74 443 106 443 176 L 443 356", INK, 2.2, 78, 1, 0.75))
    out.append(ink("M 179 352 L 179 176 C 179 124 238 97 300 97 C 362 97 421 124 421 176 L 421 352", INK, 1.8, 79, 1, 0.6))
    mcid = D.clip(f'<path d="M 179 352 L 179 176 C 179 124 238 97 300 97 C 362 97 421 124 421 176 L 421 352 Z"/>')
    out.append(f'<g {mcid}><path d="M 295 80 L 305 80 L 305 360 L 295 360 Z M 160 217 L 440 217 L 440 227 L 160 227 Z" fill="#F6EEDC"/>'
               + pline([(295, 98), (295, 352)], INK, 1.4, 80, 0.5, 1) + pline([(305, 98), (305, 352)], INK, 1.4, 81, 0.5, 1)
               + pline([(172, 217), (428, 217)], INK, 1.4, 82, 0.5, 1) + pline([(172, 227), (428, 227)], INK, 1.4, 83, 0.5, 1) + "</g>")
    # curtains on a rod, tied back
    out.append(taper([(104, 72), (496, 72)], 6, 6, "#6E4A2E") + f'<path d="{blob(102, 72, 8, 8, 1, 0.05, 10)}" fill="#6E4A2E"/><path d="{blob(498, 72, 8, 8, 2, 0.05, 10)}" fill="#6E4A2E"/>')
    cur = ("#F6CC6A", "#DE9E3A", "#8E5A1E")
    for sg, seed in ((-1, 120), (1, 121)):
        def X(x):
            return 300 + sg * (x - 300)
        cp = [(X(110), 74), (X(150), 74), (X(196), 76), (X(206), 120), (X(196), 200), (X(170), 252), (X(180), 300), (X(196), 344), (X(150), 350), (X(110), 346),
              (X(118), 300), (X(140), 252), (X(124), 200), (X(112), 120)]
        out.append(painted(D, cp, cur, seed, sdir=(sg * 0.6, 0.4), sk=0.14, angle=-90, n=60, slen=(20, 60), sw=(1.5, 3.5), inkw=2.2, hi=0.35))
        ccp = D.clip(f'<path d="{smooth_closed(cp)}"/>')
        folds = "".join(pline([(X(x), 78), (X(x + 6), 160), (X(158 + (x - 150) * 0.2), 252), (X(x - 4), 344)], "#8E5A1E", 2, seed + x, 0.45, 1) for x in (134, 162, 186))
        checks = "".join(f'<path d="M {X(100)} {y} L {X(210)} {y + 4}" stroke="#FFF2D0" stroke-width="3" opacity="0.35"/>' for y in range(96, 350, 26))
        out.append(f'<g {ccp}>{checks}{folds}</g>')
        out.append(painted(D, jitter([(X(132), 244), (X(184), 248), (X(186), 262), (X(130), 258)], seed, 0.8), ("#E2785A", "#B8442E", "#6E1E14"), seed + 3, sdir=(0, 1), sk=0.2, angle=0, n=6, inkw=1.8, hi=0.3))
    # sunbeam falling through onto the sill and wall
    out.append(f'<path d="M 168 352 L 432 352 L 470 600 L 250 600 Z" fill="{D.lin([(0, "#FFF0C8", 0.32), (1, "#FFF0C8", 0)])}"/>')
    # sill
    out.append(cast(D, 300, 392, 210, 14, "#5A2E24", 0.35))
    out.append(painted(D, jitter([(118, 350), (200, 350), (300, 350), (400, 350), (482, 350), (498, 364), (400, 364), (300, 364), (200, 364), (102, 364)], 84, 0.6), ("#F8EEDC", "#E8D8BC", "#A8927A"), 84, sdir=(0, 1), sk=0.1, angle=0, n=30, inkw=2.2, hi=0.4))
    out.append(painted(D, rpts(102, 364, 498, 386, 16, 85), ("#E8D8BC", "#D2BEA0", "#8A7660"), 85, sdir=(0, -1), sk=0.15, angle=0, n=40, inkw=2.2, hi=0.2))
    # knitted cushion (plaid)
    cush = blob_pts(300, 340, 150, 22, 86, 0.04, 20)
    out.append(painted(D, cush, ("#E2785A", "#B8442E", "#6E1E14"), 86, sdir=(0, 1), sk=0.2, angle=0, n=40, inkw=2.2, hi=0.3))
    ccid = D.clip(f'<path d="{smooth_closed(cush)}"/>')
    plaid = "".join(f'<path d="M {x} 310 L {x + 6} 372" stroke="#F6D8A8" stroke-width="3" opacity="0.5"/><path d="M {x + 10} 310 L {x + 16} 372" stroke="#5A1A10" stroke-width="2" opacity="0.4"/>' for x in range(150, 460, 30))
    plaid += "".join(f'<path d="M 140 {y} Q 300 {y + 3} 460 {y}" stroke="#F6D8A8" stroke-width="3" fill="none" opacity="0.45"/>' for y in (332, 348))
    out.append(f'<g {ccid}>{plaid}</g>')
    # yarn ball and needles, a little pumpkin
    out.append(painted(D, blob_pts(140, 334, 20, 19, 87, 0.03, 14), ("#9AB8B0", "#5E8A82", "#2E524C"), 87, sdir=(0.6, 0.6), sk=0.15, angle=-30, n=6, inkw=2, hi=0.4))
    ycid = D.clip(f'<path d="{smooth_closed(blob_pts(140, 334, 20, 19, 87, 0.03, 14))}"/>')
    out.append(f'<g {ycid}>' + "".join(pline([(120 + k * 6, 316 + k * 2), (140 + k * 2, 334), (128 + k * 7, 354)], "#2E524C", 1.6, 88 + k, 0.6, 1) for k in range(6)) + "</g>")
    out.append(pline([(112, 312), (176, 342)], "#C8A060", 3.2, 89, 1, 1) + pline([(118, 340), (172, 306)], "#C8A060", 3.2, 90, 1, 1))
    out.append(pline([(158, 346), (190, 352), (214, 346)], "#5E8A82", 2, 91, 0.9, 1))
    out.append(pumpkin(D, 462, 334, 46, 32, PUMP, 92, vine=False, cast_op=0.3))
    # the cat: a grey tabby loaf, head resting on its paws, facing right
    fur = ("#D8D2D0", "#A49C9E", "#5E5660")
    stripe = "#4E4650"
    body = sample_d("M 196 340 C 182 300 214 254 290 250 C 352 247 392 262 404 296 C 410 318 404 336 396 342 Z", 10)
    out.append(painted(D, body, fur, 93, sdir=(0.4, 0.9), sk=0.13, angle=-160, n=110, slen=(10, 28), sw=(1.2, 2.8), curve=0.4,
                       cols=["#F0ECEA", "#7E7680", "#C8C0C2", "#8E8690"], inkw=2.4, hi=0.5))
    bcid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    st = []
    for i, x in enumerate(range(222, 392, 24)):
        st.append(taper([(x + 4, 248), (x - 2, 270), (x + 4, 292), (x + 2, 306)], 9, 2, stripe, 0.55))
    out.append(f'<g {bcid}>{"".join(st)}</g>')
    out.append(taper(catmull([(232, 262), (290, 252), (350, 254), (388, 268)], 5), 5, 2, "#FFF6E8", 0.7))
    # tail wrapped round the front
    tail = catmull([(206, 330), (230, 350), (290, 356), (340, 352), (362, 344)], 6)
    out.append(taper(tail, 24, 12, fur[1]) + taper([(x, y - 3) for x, y in tail], 8, 3, "#E8E2E0", 0.6))
    for t in (0.2, 0.45, 0.7):
        i = int(t * (len(tail) - 1))
        x, y = tail[i]
        out.append(pline([(x - 2, y - 10), (x + 3, y), (x - 1, y + 9)], stripe, 3, 94 + i, 0.75, 1))
    out.append(f'<path d="{blob(364, 344, 9, 7, 95, 0.1, 10)}" fill="{stripe}"/>')
    out.append(ink(smooth_open(tail), INK, 1.4, 96, 1, 0.3))
    # paws peeking under the chin
    for px, seed in ((404, 97), (432, 98)):
        out.append(painted(D, blob_pts(px, 340, 15, 9, seed, 0.05, 12), ("#FFFFFF", "#F2ECE6", "#B8B0AE"), seed, sdir=(0, 1), sk=0.15, angle=0, n=4, inkw=1.8, hi=0.3))
        out.append(pline([(px - 4, 344), (px - 3, 348)], "#8A8288", 1.2, seed, 0.7, 1) + pline([(px + 3, 344), (px + 4, 348)], "#8A8288", 1.2, seed + 1, 0.7, 1))
    # head
    for ear, seed in (([(372, 284), (370, 238), (404, 264)], 99), ([(420, 262), (448, 242), (450, 286)], 100)):
        out.append(painted(D, ear, fur, seed, sdir=(0.5, 0.8), sk=0.15, angle=-80, n=6, inkw=2.2, hi=0.3))
    out.append(f'<path d="M 376 276 L 374 248 L 396 266 Z" fill="#E8A8A0" opacity="0.8"/><path d="M 426 264 L 444 250 L 444 280 Z" fill="#E8A8A0" opacity="0.8"/>')
    head = blob_pts(412, 302, 46, 40, 101, 0.03, 18)
    out.append(painted(D, head, fur, 101, sdir=(0.4, 0.9), sk=0.12, angle=-90, n=40, slen=(6, 16), sw=(1, 2.2), cols=["#F0ECEA", "#7E7680", "#C8C0C2"], inkw=2.4, hi=0.5))
    out.append(taper([(400, 266), (404, 280)], 5, 2, stripe, 0.7) + taper([(412, 264), (412, 282)], 5, 2, stripe, 0.7) + taper([(424, 266), (420, 280)], 5, 2, stripe, 0.7))
    for sg in (-1, 1):
        out.append(taper([(412 + sg * 44, 300), (412 + sg * 34, 304), (412 + sg * 26, 306)], 5, 1.5, stripe, 0.6))
    out.append(painted(D, blob_pts(414, 322, 22, 15, 102, 0.06, 14), ("#FFFFFF", "#F4EEEA", "#C0B8B6"), 102, sdir=(0, 1), sk=0.12, angle=0, n=4, inkw=0, hi=0.3))
    for ex in (394, 432):
        out.append(pline([(ex - 10, 300), (ex - 4, 306), (ex + 4, 306), (ex + 10, 300)], "#2A2228", 2.8, ex, 1, 1))
        out.append(pline([(ex - 9, 301), (ex - 14, 297)], "#2A2228", 1.6, ex + 1, 0.8, 1))
    out.append(f'<path d="M 408 314 L 420 314 L 414 321 Z" fill="#D8807A" stroke="#7A3A3A" stroke-width="1.2" stroke-linejoin="round"/>')
    out.append(pline([(414, 321), (414, 326), (407, 330)], "#4A3A40", 1.6, 103, 0.9, 1) + pline([(414, 326), (421, 330)], "#4A3A40", 1.6, 104, 0.9, 1))
    for sg in (-1, 1):
        for k in (-1, 0, 1):
            out.append(pline([(414 + sg * 16, 322 + k * 4), (414 + sg * 36, 318 + k * 7), (414 + sg * 52, 316 + k * 10)], "#FFFFFF", 1.4, 105 + k, 0.75, 1))
    out.append(f'<path d="{blob(384, 316, 9, 5, 106, 0.1, 8)}" fill="#F2A0A0" opacity="0.4"/><path d="{blob(444, 316, 9, 5, 107, 0.1, 8)}" fill="#F2A0A0" opacity="0.4"/>')
    # a stray leaf has landed on the sleeper
    out.append(leaf(D, "maple", 300, 258, 18, "orange", -24, 108))
    # zzz drifting up into the window
    for i, (x, y, sz) in enumerate(((386, 236, 36), (362, 200, 30), (344, 166, 24))):
        out.append(letters(D, x, y, "z", SERIF_IT, sz, "#6E3A4A", ["#4A2030"], 110 + i, max_w=60, angle=-40, shadow="#FFF6E8", soff=(0.04, 0.05)))
    # lettering on the wall below
    out.append(letters(D, 300, 480, "cat nap", SERIF_IT, 118, "#6E2E3A", ["#4A1A24", "#8E4450", "#A0545E"], 112, max_w=400,
                       shadow="#F6DCCB", soff=(-0.02, -0.025), angle=-35))
    out.append(letters(D, 300, 538, "SEASON", BEBAS, 60, "#C0602E", ["#E07A3A", "#9E4420", "#F09A50"], 113, ls=18, max_w=380, angle=-78, wob=0.5, hi="#FFD9B0"))
    return finish(D, out, 75, INK, 0.8)


# ================================================================ 13. save room for pie — a lattice apple pie, steaming on gingham
def dense(corners, step=14):
    pts = []
    n = len(corners)
    for i in range(n):
        a, b = corners[i], corners[(i + 1) % n]
        k = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        pts += [(a[0] + (b[0] - a[0]) * j / k, a[1] + (b[1] - a[1]) * j / k) for j in range(k)]
    return pts


def solve2(n1, c1, n2, c2):
    det = n1[0] * n2[1] - n1[1] * n2[0]
    return ((c1 * n2[1] - c2 * n1[1]) / det, (n1[0] * c2 - n2[0] * c1) / det)


@design("save-room-for-pie")
def save_room_for_pie():
    D = Doc("pie")
    out = [paper(D.nid(), "#F2DEB4", "#8A6A3A", 81)]
    out.append(blooms(12, ["#F6E6C0", "#E2BE84", "#EAD0A0"], 8, (0, 0, 600, 360), (90, 170), (0.14, 0.24)))
    out.append(strokes(D.nid(), "M -10 -10 L 610 -10 L 610 340 L -10 340 Z", (-60, -10, 600, 340), ["#F8E8C8", "#E2C08A", "#F0D6A6"], 82, n=80,
                       angle=-6, length=(60, 160), width=(5, 12), opacity=(0.12, 0.26), curve=0.08))
    out.append(soft_glow(D, 300, 380, 260, "#FFF4D8", 0.7))
    # gingham tablecloth in perspective
    ty = 338
    cloth = f"M -10 {ty} L 610 {ty} L 610 610 L -10 610 Z"
    ccid = D.clip(f'<path d="{cloth}"/>')
    g = [f'<path d="{cloth}" fill="#FBF0DC"/>']
    vx, vy = 300, -520
    for k in range(-24, 25):
        bx = 300 + k * 30
        w0, w1 = 7, 15
        pts = [(vx + (bx - w0 - vx) * (ty - vy) / (610 - vy) * 1, ty), (vx + (bx + w0 - vx) * (ty - vy) / (610 - vy), ty), (bx + w1, 610), (bx - w1, 610)] if k % 2 == 0 else None
        if pts:
            g.append(f'<path d="M {pts[0][0]:.1f} {pts[0][1]} L {pts[1][0]:.1f} {pts[1][1]} L {pts[2][0]:.1f} 610 L {pts[3][0]:.1f} 610 Z" fill="#C8402E" opacity="0.42"/>')
    y, h = ty, 9
    while y < 610:
        g.append(f'<path d="M -10 {y:.1f} L 610 {y + 1:.1f} L 610 {y + h:.1f} L -10 {y + h - 1:.1f} Z" fill="#C8402E" opacity="0.42"/>')
        y += h * 2
        h *= 1.16
    g.append(strokes(D.nid(), cloth, (-60, ty, 600, 610), ["#FFFFFF", "#A8301E", "#F6E0C8"], 83, n=110, angle=-4, length=(30, 90), width=(2, 6), opacity=(0.08, 0.22), curve=0.1))
    g.append(f'<rect x="-10" y="{ty}" width="620" height="60" fill="{D.lin([(0, "#6E2A18", 0.25), (1, "#6E2A18", 0)])}"/>')
    out.append(f'<g {ccid}>{"".join(g)}</g>')
    out.append(pline([(-10, ty), (200, ty + 1), (400, ty - 1), (610, ty)], INK, 2.2, 84, 0.6))
    # apples and a cinnamon bundle behind the pie
    out.append(cast(D, 116, 392, 50, 9, strength=0.35) + apple(D, 112, 362, 34, seed=85))
    out.append(cast(D, 168, 384, 34, 7, strength=0.3) + apple(D, 166, 368, 24, pal=("#F6D070", "#D8A030", "#8A5A12"), seed=86, leafc=None, blush="#E86A3A"))
    out.append(cinnamon_stick(D, 446, 380, 528, 352, 14, 87) + cinnamon_stick(D, 452, 392, 536, 372, 14, 88))
    out.append(anise(D, 494, 398, 16, 10, 89))
    # the pie
    cx, cy, rx, ry = 300, 420, 176, 78
    out.append(cast(D, 312, 482, 200, 26, "#5A1E10", 0.4))
    dish = sample_d(f"M {cx - rx - 6} {cy} C {cx - rx + 2} {cy + 50} {cx - 100} {cy + ry + 34} {cx} {cy + ry + 36} C {cx + 100} {cy + ry + 34} {cx + rx - 2} {cy + 50} {cx + rx + 6} {cy} Z", 10)
    out.append(painted(D, dish, ("#A8CCC4", "#6E9C96", "#2E5A56"), 90, sdir=(0.6, 0.6), sk=0.15, angle=-10, n=50, inkw=2.4, hi=0.4))
    dcid = D.clip(f'<path d="{smooth_closed(dish)}"/>')
    out.append(f'<g {dcid}>' + "".join(pline([(x, cy + 28 + 30 * (1 - ((x - cx) / rx) ** 2) ** 0.5), (x + 6, cy + 46 + 30 * (1 - ((x - cx) / rx) ** 2) ** 0.5)], "#F6EEDC", 3, x, 0.7, 1)
                                        for x in range(cx - 150, cx + 160, 22)) + "</g>")
    # baked crust wall above the dish, then the filling
    crust = ("#F8CF80", "#D8913E", "#7A4214")
    wallp = sample_d(f"M {cx - rx - 2} {cy - 4} C {cx - rx} {cy + 30} {cx - 100} {cy + ry + 12} {cx} {cy + ry + 14} C {cx + 100} {cy + ry + 12} {cx + rx} {cy + 30} {cx + rx + 2} {cy - 4} Z", 10)
    out.append(painted(D, wallp, crust, 89, sdir=(0.5, 0.6), sk=0.18, angle=-90, n=60, slen=(6, 16), sw=(1, 2.4), inkw=2, hi=0.3))
    filling = blob_pts(cx, cy, rx - 20, ry - 10, 91, 0.01, 30)
    out.append(painted(D, filling, ("#F2A050", "#C0581E", "#6E1E08"), 91, sdir=(0.3, 1), sk=0.15, angle=-20, n=80, inkw=0, hi=0.4))
    rnd = random.Random(92)
    out.append("".join(f'<path d="{blob(cx + rnd.uniform(-130, 130), cy + rnd.uniform(-44, 44), rnd.uniform(5, 10), rnd.uniform(3, 6), rnd.randint(0, 999), 0.2, 8)}" fill="{rnd.choice(["#FFE2A0", "#B85A1A", "#F0B050"])}" opacity="0.7"/>' for _ in range(40)))
    # woven lattice: strips in the pie's plane, mapped into perspective
    def P(u, v):
        return (cx + u * (rx - 14), cy + v * (ry - 6))
    lat = []
    dirs = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in (45, -45)]
    offs = [-0.66, -0.22, 0.22, 0.66]
    W = 0.13
    strip_pts = {}
    for di, d in enumerate(dirs):
        n_ = (-d[1], d[0])
        for oi, c in enumerate(offs):
            corners = [(c * n_[0] + t * d[0] + s_ * W * n_[0], c * n_[1] + t * d[1] + s_ * W * n_[1]) for t, s_ in ((-1.6, -1), (1.6, -1), (1.6, 1), (-1.6, 1))]
            scr = [P(u, v) for u, v in corners]
            strip_pts[(di, oi)] = scr
    sang = [math.degrees(math.atan2(d[1] * ry, d[0] * rx)) for d in dirs]
    for di in (0, 1):
        for oi in range(4):
            lat.append(painted(D, dense(strip_pts[(di, oi)], 10), crust, 100 + di * 10 + oi, sdir=(0.3, 1), sk=0.2, angle=sang[di], n=40,
                               slen=(10, 30), sw=(1, 2.4), inkw=1.8, inkop=0.6, hi=0.5, hik=0.2))
    # over-under: re-lay direction-0 strips at alternate crossings
    for oi, c0 in enumerate(offs):
        for oj, c1 in enumerate(offs):
            if (oi + oj) % 2:
                continue
            n0 = (-dirs[0][1], dirs[0][0])
            n1 = (-dirs[1][1], dirs[1][0])
            cs = [solve2(n0, c0 + a * W * 1.0, n1, c1 + b * W * 1.35) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            # extend slightly along strip 0 so the crossing reads as on-top
            scr = [P(u, v) for u, v in cs]
            lat.append(painted(D, dense(scr, 6), crust, 130 + oi * 4 + oj, sdir=(0.3, 1), sk=0.2, angle=sang[0], n=8, slen=(6, 14), sw=(1, 2), inkw=1.8, inkop=0.6, hi=0.5, hik=0.2))
    lcid = D.clip(f'<path d="{smooth_closed(blob_pts(cx, cy, rx - 8, ry - 3, 93, 0.0, 30))}"/>')
    out.append(f'<g {lcid}>{"".join(lat)}</g>')
    # sugar sparkle on the lattice
    out.append(specks(94, (cx - 140, cy - 50, cx + 140, cy + 50), ["#FFFFFF", "#FFF6DC"], 70, (0.8, 1.6), (0.5, 0.95)))
    # crimped rim: a crust band, then a ring of fluted bumps round the edge, back ones first
    ring = blob(cx, cy, rx - 2, ry - 1, 139, 0.0, 30) + " " + smooth_closed(blob_pts(cx, cy, rx - 26, ry - 14, 138, 0.0, 30)[::-1])
    out.append(f'<path d="{ring}" fill="{crust[1]}" fill-rule="evenodd"/>')
    bumps = []
    N = 30
    for i in range(N):
        a = 2 * math.pi * i / N
        x, y = cx + math.cos(a) * (rx - 4), cy + math.sin(a) * (ry - 1)
        bumps.append((y, x, i))
    for y, x, i in sorted(bumps):
        r = 17 + 3 * (y - cy) / ry
        lit = (y - cy) / ry
        bp = blob_pts(x, y, r, r * 0.72, 140 + i, 0.06, 10)
        out.append(painted(D, bp, crust, 140 + i, sdir=(0.3, 1), sk=0.2, angle=-90, n=4, inkw=1.5, inkop=0.55, hi=0.55 if lit > -0.5 else 0.3, hik=0.18))
    # steam
    out.append(steam_wisps(300, 392, 110, 95, "#FFFFFF", 3, 54, 9, 0.7))
    # leaves and a fork on the cloth
    out.append(falling(D, [("maple", 92, 524, 26, "red", -30), ("oak", 512, 520, 24, "gold", 50), ("slim", 140, 562, 18, "orange", 70)]))
    out.append(acorn(D, 470, 552, 20, 24, 97))
    # lettering
    out.append(letters(D, 300, 122, "save room", SERIF_IT, 104, "#6E2414", ["#4A140A", "#8E3A22", "#A04A2E"], 98, max_w=420,
                       shadow="#FFF4DC", soff=(-0.02, -0.025), angle=-35))
    out.append(letters(D, 300, 254, "FOR PIE", BEBAS, 146, "#D8642A", ["#F08A40", "#B04A1A", "#FFB060", "#C8561E"], 99, ls=12, max_w=400,
                       shadow="#6E2410", angle=-78, hi="#FFE2B0", inkc="#5A200C", inkw=1.8))
    return finish(D, out, 81, INK, 0.8)


# ================================================================ 14. cider mill — red mill, turning wheel, and a hand-painted roadside sign
def water_wheel(D, cx, cy, r, seed):
    out = []
    wood = ("#C89A68", "#8E6038", "#4A2E16")
    # paddles round the rim
    for i in range(16):
        a = math.radians(i * 22.5 + 6)
        c, s_ = math.cos(a), math.sin(a)
        pts = [(cx + c * (r - 4) - s_ * 7, cy + s_ * (r - 4) + c * 7), (cx + c * (r + 16) - s_ * 7, cy + s_ * (r + 16) + c * 7),
               (cx + c * (r + 16) + s_ * 7, cy + s_ * (r + 16) - c * 7), (cx + c * (r - 4) + s_ * 7, cy + s_ * (r - 4) - c * 7)]
        out.append(painted(D, dense(pts, 5), wood, seed + i, sdir=(0.6, 0.6), sk=0.2, angle=math.degrees(a), n=3, inkw=1.6, hi=0.3))
    ring = blob(cx, cy, r + 2, r + 2, seed, 0.0, 28) + " " + smooth_closed(blob_pts(cx, cy, r - 10, r - 10, seed + 1, 0.0, 28)[::-1])
    out.append(f'<path d="{ring}" fill="{wood[1]}" fill-rule="evenodd"/>')
    out.append(strokes(D.nid(), ring, (cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4), [wood[0], wood[2]], seed, n=40, angle=0, length=(10, 30), width=(1, 2.4), opacity=(0.2, 0.5), clip_extra=' fill-rule="evenodd"'))
    out.append(ink(blob(cx, cy, r + 2, r + 2, seed, 0.0, 28), INK, 2, seed, 1, 0.75) + ink(blob(cx, cy, r - 10, r - 10, seed + 1, 0.0, 28), INK, 1.6, seed + 1, 1, 0.6))
    for i in range(8):
        a = math.radians(i * 45 + 20)
        out.append(taper([(cx, cy), (cx + math.cos(a) * (r - 8), cy + math.sin(a) * (r - 8))], 7, 5, wood[1]))
        out.append(pline([(cx + math.cos(a) * 12, cy + math.sin(a) * 12), (cx + math.cos(a) * (r - 10), cy + math.sin(a) * (r - 10))], wood[2], 1.2, seed + i, 0.6, 1))
    out.append(painted(D, blob_pts(cx, cy, 14, 14, seed + 3, 0.04, 12), wood, seed + 3, sdir=(0.6, 0.6), sk=0.2, angle=-30, n=4, inkw=1.8, hi=0.4))
    out.append(f'<path d="{blob(cx, cy, 5, 5, seed, 0.1, 8)}" fill="#2E1A0C"/>')
    return "".join(out)


@design("cider-mill")
def cider_mill():
    D = Doc("cm")
    out = [sky(D, [(0, "#A8C4C8"), (0.35, "#E8DCC0"), (0.6, "#F6D4A0"), (1, "#F6D4A0")], 3, 600, ["#FFFFFF", "#C8D8D4", "#F6DEB0"], 60, sop=(0.08, 0.2))]
    out.append(soft_glow(D, 470, 170, 220, "#FFF0C8", 0.85))
    out.append(blooms(14, ["#FFFFFF", "#E8C8A0"], 5, (0, 0, 600, 240), (60, 120), (0.08, 0.14)))
    # puffy painted clouds
    for i, (x, y, w) in enumerate(((120, 186, 70), (520, 112, 56))):
        for k in range(6):
            out.append(f'<path d="{blob(x - w * 0.6 + k * w * 0.24, y - (10 if k in (2, 3) else 0) - (6 if k in (1, 4) else 0), w * 0.28, w * 0.22, 600 + i * 9 + k, 0.1, 12)}" fill="#FFFBF2" opacity="0.85"/>')
        out.append(f'<path d="{blob(x, y + 6, w * 0.75, w * 0.14, 620 + i, 0.08, 14)}" fill="#E8D4C0" opacity="0.6"/>')
    # far hills of autumn trees
    l1 = ridge([(-20, 286), (120, 266), (260, 282), (420, 260), (620, 276)], 4, 10)
    out.append(hill(D, l1, 420, ("#E2CCC4", "#C8AAB0", "#9A8090"), 4, inkw=1, inkop=0.3))
    rnd = random.Random(5)
    for i, x in enumerate(range(-10, 620, 22)):
        y = 280 + 8 * math.sin(x / 45)
        out.append(dab_crown(D, x, y - 6, 15, 12, [("#F2B07A", "#D88A5A", "#A86448"), ("#F6CC88", "#E0A860", "#A87848"), ("#E89A80", "#C06A58", "#8A4A48")], 700 + i, 12, (4, 7), inkw=0))
    l2 = ridge([(-20, 380), (150, 372), (330, 384), (620, 374)], 6, 5)
    out.append(hill(D, l2, 610, ("#C8C27A", "#9AA055", "#5E6A34"), 6, angle=-2, inkw=1.8, lit="#FFF0B0"))
    out.append(grass(43, (-10, 450, 610, 610), ["#6E7E3A", "#8A9A48", "#4E5A28", "#A8A858"], 160, (10, 24)))
    # the mill: long red wall, slate roof, white trim
    out.append(cast(D, 380, 384, 130, 8, strength=0.35))
    wall = rpts(262, 272, 486, 382, 16, 30, 0.8)
    out.append(painted(D, wall, ("#E87050", "#B8402A", "#6A1A10"), 30, sdir=(0.8, 0.2), sk=0.1, angle=-90, n=70, slen=(14, 36), sw=(1, 2.4), inkw=2.4, hi=0.25))
    wcid = D.clip(f'<path d="{smooth_closed(wall)}"/>')
    battens = "".join(pline([(x, 272), (x + 0.5, 382)], "#7A2014", 1.6, x, 0.5, 1) for x in range(272, 486, 13))
    out.append(f'<g {wcid}>{battens}</g>')
    roof = [(244, 278), (284, 216), (464, 216), (504, 278)]
    out.append(painted(D, dense(roof, 14), ("#8A96A0", "#5E6A76", "#2E3640"), 31, sdir=(0.6, 0.8), sk=0.12, angle=-4, n=50, slen=(14, 36), sw=(1, 2.4), inkw=2.4, hi=0.35))
    rcid = D.clip(f'<path d="{smooth_closed(dense(roof, 14))}"/>')
    out.append(f'<g {rcid}>' + "".join(pline([(230, y), (520, y + 1)], "#2E3640", 1.4, y, 0.45, 1) for y in range(230, 280, 11)) + "</g>")
    out.append(pline([(240, 279), (508, 279)], "#F6EEDC", 4, 32, 1, 1))
    # cupola vent on the ridge
    out.append(painted(D, dense([(360, 216), (360, 192), (392, 192), (392, 216)], 8), ("#F6EEDC", "#E2D6C0", "#8A7E6A"), 33, sdir=(1, 0), sk=0.2, angle=-90, n=6, inkw=1.8, hi=0.3))
    out.append(painted(D, dense([(354, 194), (376, 176), (398, 194)], 8), ("#8A96A0", "#5E6A76", "#2E3640"), 34, sdir=(1, 0.5), sk=0.2, angle=0, n=4, inkw=1.8, hi=0.3))
    out.append(pline([(376, 176), (376, 162)], INK, 1.8, 35, 1, 1) + pline([(368, 166), (386, 162)], INK, 1.8, 36, 1, 1))
    # windows and the big door
    for x in (360, 436):
        out.append(painted(D, dense([(x - 16, 306), (x + 16, 306), (x + 16, 338), (x - 16, 338)], 8), ("#F6EEDC", "#E6DAC4", "#8A7E6A"), x, sdir=(0, 1), sk=0, angle=0, n=4, inkw=2, hi=0))
        out.append(f'<path d="M {x - 11} 311 L {x + 11} 311 L {x + 11} 333 L {x - 11} 333 Z" fill="#4A3030"/><path d="M {x - 11} 311 L {x + 1} 311 L {x - 11} 324 Z" fill="#FFE2A0" opacity="0.55"/>')
        out.append(pline([(x, 311), (x, 333)], "#F6EEDC", 2.4, x, 1, 1) + pline([(x - 11, 322), (x + 11, 322)], "#F6EEDC", 2.4, x + 1, 1, 1))
    door = dense([(392, 382), (392, 344), (426, 344), (426, 382)], 8)
    out.append(painted(D, door, ("#F6EEDC", "#E6DAC4", "#8A7E6A"), 37, sdir=(0, 1), sk=0, angle=0, n=4, inkw=2, hi=0))
    out.append(f'<path d="M 396 380 L 396 348 L 422 348 L 422 380 Z" fill="#8E2A1A"/>' + pline([(396, 348), (422, 380)], "#F6EEDC", 2.4, 38, 1, 1) + pline([(422, 348), (396, 380)], "#F6EEDC", 2.4, 39, 1, 1))
    # apple tree on the left, heavy with fruit
    out.append(taper([(112, 392), (116, 330), (106, 290)], 16, 7, "#5A3A28") + taper([(114, 330), (146, 296)], 6, 2, "#5A3A28"))
    out.append(dab_crown(D, 116, 272, 76, 64, [("#B8C070", "#7E8A40", "#46521E"), ("#D8C468", "#A89238", "#5E5020"), ("#9AB060", "#6A7E36", "#3A4A1A")], 40, 150, (8, 13), light=(0.7, -0.6), inkw=0))
    for _ in range(22):
        a, rr = rnd.uniform(0, 2 * math.pi), math.sqrt(rnd.random()) * 0.85
        x, y = 116 + math.cos(a) * 70 * rr, 272 + math.sin(a) * 58 * rr
        out.append(f'<path d="{blob(x, y, 5.5, 5, rnd.randint(0, 999), 0.08, 8)}" fill="#D8302A"/><path d="{blob(x - 1.6, y - 1.6, 1.8, 1.4, rnd.randint(0, 999), 0.1, 6)}" fill="#FFD8C0" opacity="0.8"/>')
    # stream running from the wheel toward us
    st = sample_d("M -20 396 C 80 388 170 386 240 384 C 300 384 320 392 330 398 C 300 420 200 428 120 436 C 60 442 0 446 -20 446 Z", 10)
    out.append(painted(D, st, ("#C8E4E8", "#7EAAB8", "#3E6A7A"), 41, sdir=(0, 1), sk=0.12, angle=-2, n=60, slen=(20, 60), sw=(1, 2.4), cols=["#FFFFFF", "#5E8A9A", "#A8D0D8"], inkw=1.8, inkop=0.5, hi=0.4))
    for i in range(10):
        x, y = rnd.uniform(0, 300), rnd.uniform(398, 436)
        out.append(pline([(x, y), (x + rnd.uniform(14, 30), y + 0.6)], "#FFFFFF", 1.8, 900 + i, 0.75, 1))
    out.append(grass(42, (-10, 380, 250, 396), ["#6E7E3A", "#8A9A48", "#4E5A28"], 60, (6, 14)))
    # the wheel, turning in the stream, with splash
    out.append(water_wheel(D, 262, 318, 66, 50))
    for i in range(14):
        a = math.radians(rnd.uniform(200, 340))
        x, y = 262 + math.cos(a) * 30 + rnd.uniform(-30, 30), 392 + rnd.uniform(-10, 4)
        out.append(f'<path d="{blob(x, y, rnd.uniform(3, 8), rnd.uniform(2, 4), rnd.randint(0, 999), 0.2, 8)}" fill="#FFFFFF" opacity="{rnd.uniform(0.6, 0.95):.2f}"/>')
    for x in (226, 248, 270, 292):
        out.append(pline([(x, 360), (x + 2, 378), (x - 1, 392)], "#E8F4F6", 2, x, 0.7, 1))
    # roadside sign on posts with chains: the name painted on the board
    for px in (138, 462):
        out.append(painted(D, rpts(px - 9, 416, px + 9, 612, 18, px, 0.6), ("#A07A56", "#6E4A2E", "#3E2614"), px, sdir=(1, 0), sk=0.2, angle=-90, n=20, inkw=2, hi=0.3))
    out.append(painted(D, rpts(112, 404, 488, 420, 16, 43, 0.6), ("#A07A56", "#6E4A2E", "#3E2614"), 43, sdir=(0, 1), sk=0.2, angle=0, n=30, inkw=2, hi=0.3))
    for px in (160, 440):
        for k in range(3):
            out.append(f'<path d="{blob(px, 425 + k * 7, 2.6, 4, 44 + k, 0.05, 8)}" fill="none" stroke="#3A3030" stroke-width="1.8"/>')
    out.append(cast(D, 304, 560, 200, 10, strength=0.25))
    board = rpts(98, 444, 502, 550, 16, 45, 1.0)
    out.append(painted(D, board, ("#B04A30", "#8A2E1C", "#4A140A"), 45, sdir=(0.3, 1), sk=0.12, angle=-2, n=120, slen=(30, 90), sw=(1.2, 3), inkw=2.6, hi=0.3, curve=0.05))
    bcid = D.clip(f'<path d="{smooth_closed(board)}"/>')
    grainl = "".join(pline([(90, y), (300, y + rnd.uniform(-2, 2)), (510, y + rnd.uniform(-1, 1))], "#4A140A", 1.2, int(y), 0.35, 1) for y in range(452, 550, 9))
    out.append(f'<g {bcid}>{grainl}</g>')
    out.append(ink(smooth_closed(rpts(106, 452, 494, 542, 12, 46, 0.4)), "#F6E2B8", 2.2, 46, 1, 0.6))
    for x, y in ((113, 459), (487, 459), (113, 535), (487, 535)):
        out.append(f'<circle cx="{x}" cy="{y}" r="2.6" fill="#3A2418"/>')
    out.append(letters(D, 300, 508, "CIDER MILL", BEBAS, 74, "#FBEBD0", ["#FFFFFF", "#F2D8B0", "#FFF6E6"], 47, ls=10, max_w=360,
                       shadow="#3A0E06", angle=-70, wob=0.6))
    out.append(label(300, 533, "APPLE CIDER & DONUTS", MONO, 18, "#F6CE7A", ls=4, max_w=350))
    # apples spilling at the foot of the posts
    for i, (x, y, r, pal) in enumerate(((64, 566, 22, None), (100, 578, 18, ("#F6D070", "#D8A030", "#8A5A12")), (520, 570, 22, None), (552, 582, 18, ("#B8D070", "#8AA03A", "#4E6A1A")))):
        out.append(apple(D, x, y, r, pal or ("#F07A52", "#C8362A", "#7A1616"), 950 + i, leafc="olive" if i in (0, 2) else None))
    # birds and lettering in the sky
    for bx_, by_, bs in ((170, 236, 7), (190, 226, 6), (208, 238, 5)):
        out.append(pline([(bx_ - bs, by_), (bx_ - bs * 0.5, by_ - bs * 0.6), (bx_, by_)], "#5A3A3A", 1.8, bx_, 0.8, 1) +
                   pline([(bx_, by_), (bx_ + bs * 0.5, by_ - bs * 0.6), (bx_ + bs, by_)], "#5A3A3A", 1.8, bx_ + 1, 0.8, 1))
    out.append(letters(D, 300, 130, "fresh pressed", SERIF_IT, 84, "#8E2A1A", ["#6E1A0E", "#B04030", "#C8503A"], 48, max_w=440,
                       shadow="#FFF4E0", soff=(-0.02, -0.025), angle=-35))
    return finish(D, out, 91, INK, 0.8)


# ================================================================ 15. forage — a wicker basket of the woods' best, in dappled light
def porcini(D, cx, base, w, h, seed, rot=0):
    """Fat-stemmed bolete: bulbous cream stem with a net texture, glossy brown bun cap."""
    out = [f'<g transform="rotate({rot} {cx} {base})">']
    stem = sample_d(f"M {cx - w * 0.22} {base - h * 0.55} C {cx - w * 0.34} {base - h * 0.3} {cx - w * 0.38} {base - h * 0.04} {cx - w * 0.2} {base} "
                    f"C {cx - w * 0.05} {base + h * 0.03} {cx + w * 0.12} {base + h * 0.03} {cx + w * 0.22} {base} "
                    f"C {cx + w * 0.38} {base - h * 0.06} {cx + w * 0.32} {base - h * 0.32} {cx + w * 0.2} {base - h * 0.55} Z", 8)
    out.append(painted(D, stem, ("#FFF6E2", "#EAD6B4", "#A88A62"), seed, sdir=(0.7, 0.3), sk=0.18, angle=-90, n=14, inkw=1.8, hi=0.45))
    out.append(specks(seed, (cx - w * 0.25, base - h * 0.5, cx + w * 0.25, base - h * 0.05), ["#B89A70"], 18, (0.8, 1.6), (0.4, 0.7)))
    cap = sample_d(f"M {cx - w * 0.52} {base - h * 0.5} C {cx - w * 0.54} {base - h * 0.95} {cx - w * 0.2} {base - h * 1.08} {cx} {base - h * 1.08} "
                   f"C {cx + w * 0.24} {base - h * 1.08} {cx + w * 0.56} {base - h * 0.95} {cx + w * 0.52} {base - h * 0.5} "
                   f"C {cx + w * 0.3} {base - h * 0.44} {cx - w * 0.3} {base - h * 0.44} {cx - w * 0.52} {base - h * 0.5} Z", 8)
    out.append(painted(D, cap, ("#C8865A", "#8E4E28", "#4A2210"), seed + 1, sdir=(0.6, 0.6), sk=0.12, angle=-20, n=26, inkw=2, hi=0.45, curve=0.5))
    out.append(taper([(cx - w * 0.34, base - h * 0.78), (cx - w * 0.16, base - h * 0.96), (cx + w * 0.06, base - h * 1.0)], max(2, w * 0.06), 1, "#FFE2C0", 0.6))
    out.append(pline([(cx - w * 0.46, base - h * 0.5), (cx, base - h * 0.45), (cx + w * 0.46, base - h * 0.5)], "#E8C880", max(1.4, w * 0.03), seed, 0.8, 1))
    out.append("</g>")
    return "".join(out)


def chanterelle(D, cx, base, s, seed, rot=0):
    """Golden funnel with a wavy rim and decurrent ridges."""
    rnd = random.Random(seed)
    top = base - s
    rim = [(cx - s * 0.62 + k * s * 1.24 / 8, top + (s * 0.08 if k % 2 else 0) + rnd.uniform(-2, 2)) for k in range(9)]
    pts = [(cx - s * 0.1, base), (cx - s * 0.16, base - s * 0.4)] + rim + [(cx + s * 0.16, base - s * 0.4), (cx + s * 0.1, base)]
    out = [f'<g transform="rotate({rot} {cx} {base})">',
           painted(D, pts, ("#FFD878", "#EFA232", "#A8601A"), seed, sdir=(0.6, 0.4), sk=0.15, angle=-90, n=16, inkw=1.8, hi=0.45)]
    for k in range(-3, 4):
        out.append(pline([(cx + k * s * 0.15, top + s * 0.12), (cx + k * s * 0.06, base - s * 0.45), (cx + k * s * 0.02, base - s * 0.18)], "#B86A1A", 1.3, seed + k, 0.55, 1))
    rimp = [(x, y + 1) for x, y in rim]
    out.append(f'<path d="{smooth_closed(rimp + [(cx + s * 0.4, top + s * 0.22), (cx - s * 0.4, top + s * 0.22)])}" fill="#FFE8A8" opacity="0.6"/>')
    out.append("</g>")
    return "".join(out)


def fern(D, x, y, L, ang, seed, col=("#9AB060", "#6A8236", "#3A4E1A"), n=12):
    """A fern frond: curving rachis with paired, shrinking leaflets."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    out = []
    pts = []
    for i in range(n + 1):
        t = i / n
        bend = 0.25 * t * t
        aa = a + bend
        pts.append((x + math.cos(a) * L * t + math.cos(aa + 1.57) * L * 0.15 * t * t, y + math.sin(a) * L * t + math.sin(aa + 1.57) * L * 0.15 * t * t))
    out.append(pline(pts, col[2], 2.2, seed, 0.9, 1))
    for i in range(1, n):
        t = i / n
        px, py = pts[i]
        qx, qy = pts[i + 1]
        da = math.atan2(qy - py, qx - px)
        ll = L * 0.22 * (1 - t) + 4
        for sg in (-1, 1):
            la = da + sg * 1.05
            c = rnd.choice(col[:2])
            tip = (px + math.cos(la) * ll, py + math.sin(la) * ll)
            mid = (px + math.cos(la) * ll * 0.5, py + math.sin(la) * ll * 0.5)
            nx, ny = -math.sin(la) * ll * 0.18, math.cos(la) * ll * 0.18
            out.append(f'<path d="M {px:.1f} {py:.1f} Q {mid[0] + nx:.1f} {mid[1] + ny:.1f} {tip[0]:.1f} {tip[1]:.1f} Q {mid[0] - nx:.1f} {mid[1] - ny:.1f} {px:.1f} {py:.1f} Z" fill="{c}" stroke="{col[2]}" stroke-width="0.9" stroke-opacity="0.6"/>')
    return "".join(out)


def blackberry(cx, cy, r, seed):
    rnd = random.Random(seed)
    out = []
    for k in range(9):
        a = rnd.uniform(0, 2 * math.pi)
        d = math.sqrt(rnd.random()) * r * 0.62
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.4:.1f}" fill="#2A1430" stroke="#14060E" stroke-width="1"/>'
                   f'<circle cx="{x - r * 0.12:.1f}" cy="{y - r * 0.14:.1f}" r="{r * 0.11:.1f}" fill="#C8A0D0" opacity="0.8"/>')
    return "".join(out)


@design("forage")
def forage():
    D = Doc("fg")
    out = [sky(D, [(0, "#5E7244"), (0.45, "#46583A"), (1, "#2C3824")], 3, 600, ["#6E8450", "#3A4A2E", "#7E9058"], 120, angle=-70, sop=(0.08, 0.2))]
    out.append(blooms(15, ["#A8B868", "#2A3620", "#C8C070"], 9, (0, 0, 600, 600), (70, 150), (0.08, 0.16)))
    # light shafts through the canopy
    for i, (x, w) in enumerate(((150, 60), (260, 36), (420, 70))):
        g = D.lin([(0, "#FFF2C0", 0.28), (1, "#FFF2C0", 0)])
        out.append(f'<path d="M {x} -10 L {x + w} -10 L {x + w + 160} 610 L {x + 120} 610 Z" fill="{g}"/>')
    rnd = random.Random(16)
    for _ in range(60):
        x, y = rnd.uniform(0, 600), rnd.uniform(0, 600)
        out.append(f'<path d="{blob(x, y, rnd.uniform(3, 9), rnd.uniform(3, 8), rnd.randint(0, 999), 0.2, 8)}" fill="#F6E8A0" opacity="{rnd.uniform(0.06, 0.18):.2f}"/>')
    # ferns and saplings in the dark margins
    out.append(fern(D, -10, 470, 190, -58, 20, ("#6E8A44", "#4E6830", "#26341A"), 14) + fern(D, 610, 470, 180, -122, 21, ("#6E8A44", "#4E6830", "#26341A"), 14))
    out.append(fern(D, 30, 560, 150, -40, 22) + fern(D, 570, 566, 150, -140, 23))
    # forest floor
    l = ridge([(-20, 494), (160, 486), (330, 496), (480, 484), (620, 494)], 6, 4)
    out.append(hill(D, l, 610, ("#8A7A44", "#5E5230", "#2E2614"), 6, angle=-3, inkw=1.4, inkop=0.4))
    for _ in range(120):
        x, y = rnd.uniform(-10, 610), rnd.uniform(492, 600)
        sz = 3 + (y - 480) / 26
        out.append(f'<path d="{blob(x, y, sz, sz * 0.55, rnd.randint(0, 9999), 0.25, 7, rnd.uniform(-40, 40))}" fill="{rnd.choice(["#D8783A", "#B8442A", "#E8A848", "#8A3A22", "#C8A040", "#7E8A40"])}" opacity="{rnd.uniform(0.6, 0.95):.2f}"/>')
    out.append(grass(24, (-10, 486, 610, 520), ["#7E9A48", "#5E7836", "#A8B860"], 70, (6, 16)))
    # basket: back rim and handle first
    cx, rim_y = 300, 392
    out.append(cast(D, 300, 538, 200, 18, "#14180C", 0.55))
    handle = catmull([(150, rim_y), (170, 300), (300, 262), (430, 300), (450, rim_y)], 8)
    out.append(taper(handle, 18, 18, "#8E6034") + taper([(x, y - 3) for x, y in handle], 6, 6, "#D8A860", 0.6))
    for k in range(0, len(handle) - 1, 2):
        x, y = handle[k]
        out.append(pline([(x - 6, y - 6), (x + 6, y + 6)], "#5A3A1A", 1.6, k, 0.6, 1))
    out.append(ink(smooth_open(handle), INK, 1.6, 30, 1, 0.4))
    backrim = blob_pts(cx, rim_y, 170, 30, 31, 0.0, 28)
    out.append(f'<path d="{smooth_closed(backrim)}" fill="#8E6034"/>')
    out.append(strokes(D.nid(), smooth_closed(backrim), (120, 356, 480, 426), ["#C08A44", "#5A3A1A", "#D8A860"], 32, n=60, angle=-2, length=(14, 40), width=(1.5, 3), opacity=(0.3, 0.6)))
    # contents heaped above the rim: ferns, oak leaves, then mushrooms, berries, acorns
    out.append(fern(D, 200, 388, 150, -128, 40, ("#9AB060", "#6A8236", "#3A4E1A"), 13) + fern(D, 400, 388, 140, -54, 41, ("#B8C070", "#7E8A40", "#46521E"), 13))
    out.append(leaf(D, "oak", 166, 350, 36, "red", -58, 42) + leaf(D, "oak", 444, 346, 34, "gold", 62, 43) + leaf(D, "maple", 300, 318, 32, "orange", 4, 44))
    out.append(leaf(D, "maple", 206, 340, 28, "gold", -30, 57) + leaf(D, "maple", 404, 336, 28, "red", 34, 58))
    out.append(chanterelle(D, 168, 404, 46, 48, -26) + chanterelle(D, 436, 404, 48, 49, 22) + chanterelle(D, 312, 392, 44, 59, 6))
    out.append(porcini(D, 232, 404, 112, 104, 45, -10))
    out.append(porcini(D, 370, 406, 92, 84, 46, 12))
    out.append(chanterelle(D, 300, 412, 54, 47, -4) + chanterelle(D, 140, 412, 34, 66, -40) + chanterelle(D, 466, 412, 34, 67, 36))
    out.append(blackberry(186, 404, 12, 51) + blackberry(206, 412, 11, 52) + blackberry(432, 410, 12, 53) + blackberry(412, 416, 10, 68))
    out.append(acorn(D, 270, 404, 20, -14, 55) + acorn(D, 338, 408, 18, 20, 56))
    # basket front: woven body painted over everything below the rim
    body = sample_d(f"M {cx - 174} {rim_y} C {cx - 168} {rim_y + 60} {cx - 140} {rim_y + 130} {cx - 100} {rim_y + 140} C {cx - 40} {rim_y + 150} {cx + 40} {rim_y + 150} {cx + 100} {rim_y + 140} "
                    f"C {cx + 140} {rim_y + 130} {cx + 168} {rim_y + 60} {cx + 174} {rim_y} C {cx + 100} {rim_y + 34} {cx - 100} {rim_y + 34} {cx - 174} {rim_y} Z", 10)
    wick = ("#E8BC74", "#C08A44", "#6E4A1E")
    out.append(painted(D, body, wick, 60, sdir=(0.6, 0.5), sk=0.16, angle=-4, n=20, inkw=0, hi=0.3))
    bcid = D.clip(f'<path d="{smooth_closed(body)}"/>')
    weave = []
    row = 0
    y = rim_y + 22
    while y < rim_y + 156:
        for k in range(-9, 10):
            x = cx + k * 22 + (11 if row % 2 else 0)
            shrink = 1 - 0.18 * ((y - rim_y) / 150)
            xx = cx + (x - cx) * shrink
            cell = blob(xx, y, 11 * shrink, 7, 70 + row * 20 + k, 0.08, 10)
            weave.append(f'<path d="{cell}" fill="{random.Random(row * 31 + k).choice([wick[0], wick[1], "#D8A860"])}"/>'
                         f'<path d="M {xx - 9 * shrink:.1f} {y - 2:.1f} Q {xx:.1f} {y - 6:.1f} {xx + 9 * shrink:.1f} {y - 2:.1f}" stroke="#FFF0C8" stroke-width="1.6" fill="none" opacity="0.5"/>')
        y += 15
        row += 1
    stakes = "".join(pline([(cx + k * 22 * 1.0, rim_y + 18), (cx + k * 22 * 0.82, rim_y + 156)], "#6E4A1E", 2.2, 80 + k, 0.55, 1) for k in range(-9, 10))
    shade = f'<path d="{smooth_closed(body)}" fill="{D.lin([(0, "#2A1A08", 0), (0.6, "#2A1A08", 0.1), (1, "#2A1A08", 0.45)])}"/>'
    sideshade = f'<path d="{smooth_closed(body)}" fill="{D.lin([(0, "#2A1A08", 0.35), (0.25, "#2A1A08", 0), (0.75, "#2A1A08", 0), (1, "#2A1A08", 0.4)], 0, 0, 1, 0)}"/>'
    out.append(f'<g {bcid}>{"".join(weave)}{stakes}{shade}{sideshade}</g>')
    out.append(ink(smooth_closed(body), INK, 2.4, 61, 2, 0.8))
    # braided rim
    rimf = catmull([(cx - 176, rim_y), (cx - 100, rim_y + 26), (cx, rim_y + 32), (cx + 100, rim_y + 26), (cx + 176, rim_y)], 10)
    out.append(taper(rimf, 18, 18, "#B07A3A"))
    for k in range(0, len(rimf) - 1):
        x, y = rimf[k]
        out.append(f'<path d="{blob(x, y, 8, 6, 90 + k, 0.1, 8, 30)}" fill="{"#E8BC74" if k % 2 else "#D0A058"}" stroke="#6E4A1E" stroke-width="1.3"/>')
    # a mushroom and berries spilled on the moss
    out.append(chanterelle(D, 504, 540, 34, 62, 26) + porcini(D, 96, 540, 50, 46, 63, -14))
    out.append(blackberry(472, 548, 9, 64))
    out.append(leaf(D, "maple", 150, 560, 22, "red", 30, 65))
    # lettering
    out.append(letters(D, 300, 168, "forage", DMS, 150, "#F6ECD2", ["#FFFFFF", "#E8DCB8", "#FFF6E0", "#D8CCA8"], 70, max_w=420,
                       shadow="#141C10", soff=(0.02, 0.035), angle=-35, hi="#FFFFFF"))
    out.append(ruled(300, 222, "WANDER · GATHER · SAVOR", "#F2C860", size=18, ls=4, line_w=30, gap=12))
    return finish(D, out, 17, "#F4E8C0", 0.7)


# ---------------------------------------------------------------- build
def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
