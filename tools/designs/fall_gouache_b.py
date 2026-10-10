"""Fall, hand-painted (gouache / storybook) edition, part B: 15 of the Fall magnets repainted so they read as
real gouache illustrations - organic shapes, layered washes with pooled edges, brush strokes that follow each
form, warm-brown ink lines under the paint, brush-textured lettering, soft glows and paper grain.

Run from tools/designs:  python3 fall_gouache_b.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from gouache import blob, blob_pts, grain, ink, jitter, paper, smooth_closed, smooth_open, wash
from icons import MAPLE
from poster import ANTON

COL = "fall"

# ---------------------------------------------------------------- palette (warm, shared with part A)
INK = "#3A2418"
INK2 = "#5A3420"
PAPER = "#F4EAD8"
FLECK = "#8A6A4A"
CREAM = "#FBF3E4"
RUST = "#B8481E"
PUMP = "#E8792E"
MUST = "#E2A23A"
GOLD = "#F2C25A"
OLIVE = "#7A8A3E"
CRAN = "#A8321E"
PLUM = "#6B2E3A"
BARK = "#6E4A2A"

# (base, dark, light)
L_RED = ("#D9542C", "#9A2E18", "#F28E50")
L_ORANGE = ("#EE8A34", "#B8501C", "#F8BA62")
L_GOLD = ("#EDB740", "#B07A1C", "#F8DA7C")
L_CRAN = ("#B8382A", "#781C14", "#E06A4C")
L_OLIVE = ("#9AA048", "#5E6A28", "#CACA72")
L_BROWN = ("#B8783A", "#7A4A20", "#DCA464")
LEAF_PALS = (L_RED, L_ORANGE, L_GOLD, L_CRAN, L_OLIVE, L_BROWN)

# pumpkins: (body, dark, light, deep)
PK_OR = ("#E8792E", "#C2561E", "#F8A85A", "#8E3A12")
PK_DEEP = ("#D2602A", "#A8421A", "#EE8E4A", "#702A0E")
PK_CREAM = ("#F1E6D2", "#CDBB9C", "#FFFDF6", "#9A8466")
PK_GOLD = ("#E6A93A", "#BE7E1E", "#F6D06A", "#86561A")
PK_GREEN = ("#6E8250", "#4E6236", "#9AAE72", "#2E3E22")
PK_SAGE = ("#B8C0A0", "#8E9878", "#DDE2C8", "#5E6A50")
PK_PEACH = ("#EDB98A", "#CC9264", "#FAD9B4", "#9A6440")


def _f(v):
    return f"{v:.1f}"


class Ids:
    """Unique, slug-prefixed ids (pages inline many SVGs)."""

    def __init__(self, slug):
        self.p, self.n = "gb-" + slug, 0

    def __call__(self, tag="i"):
        self.n += 1
        return f"{self.p}-{tag}{self.n}"


# ---------------------------------------------------------------- gradients, glows, shadows
def lgrad(uid, stops, x1=0, y1=0, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a[0] if a else 1}"/>' for o, c, *a in stops)
    return f'<linearGradient id="{uid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def glow(u, cx, cy, r, color, op=0.6, ry=None):
    g = u("gl")
    return (f'<defs><radialGradient id="{g}"><stop offset="0" stop-color="{color}" stop-opacity="{op}"/>'
            f'<stop offset="0.55" stop-color="{color}" stop-opacity="{op * 0.4:.2f}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient></defs>'
            f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(r)}" ry="{_f(ry or r)}" fill="url(#{g})"/>')


def shadow(u, cx, cy, rx, ry, op=0.3, color="#2A1608"):
    return glow(u, cx, cy, rx, color, op, ry)


# ---------------------------------------------------------------- brush marks
def _n(v):
    t = f"{v:.1f}"
    return t[:-2] if t.endswith(".0") else t


def brush(box, colors, seed, n, angle=-90, length=(10, 30), width=(1.5, 4), opacity=(0.2, 0.5), curve=0.2, jit=12):
    """Tapered brush strokes scattered in a box. angle may be a function (x, y) -> degrees.
    Strokes are grouped by colour and (quantised) fill-opacity so each stays a short relative path."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    groups = {}
    for _ in range(int(n)):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        ang = angle(x, y) if callable(angle) else angle
        L, w = rnd.uniform(*length), rnd.uniform(*width)
        a = math.radians(ang + rnd.uniform(-jit, jit))
        dx, dy = L * math.cos(a), L * math.sin(a)
        nx, ny = -math.sin(a), math.cos(a)
        sx, sy = x - dx / 2, y - dy / 2
        bend = L * curve * rnd.uniform(-1, 1)
        mx, my = dx / 2 + nx * bend, dy / 2 + ny * bend
        col = rnd.choice(colors)
        op = round(rnd.uniform(*opacity) * 10) / 10 or 0.1
        groups.setdefault((col, op), []).append(
            f"M{_n(sx)} {_n(sy)}q{_n(mx + nx * w)} {_n(my + ny * w)} {_n(dx)} {_n(dy)}q{_n(mx - nx * w - dx)} {_n(my - ny * w - dy)} {_n(-dx)} {_n(-dy)}z")
    return "".join(f'<path fill="{c}" fill-opacity="{o}" d="{"".join(ds)}"/>' for (c, o), ds in groups.items())


def dabs(box, colors, seed, n, r=(2, 5), opacity=(0.5, 0.95), squash=0.7, clip=None):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(int(n)):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if clip and not clip(x, y):
            continue
        rr = rnd.uniform(*r)
        out.append(f'<ellipse cx="{_f(x)}" cy="{_f(y)}" rx="{_f(rr)}" ry="{_f(rr * rnd.uniform(squash, 1))}" '
                   f'transform="rotate({rnd.uniform(0, 180):.0f} {_f(x)} {_f(y)})" fill="{rnd.choice(colors)}" opacity="{rnd.uniform(*opacity):.2f}"/>')
    return "".join(out)


def form(u, d, box, base, dark, light, seed, angle=-90, n=None, length=None, width=None, tints=None, shade=(10, 8),
         shade_op=0.5, hi=None, hi_op=0.4, ink_w=2.2, ink_col=INK, ink_op=0.8, sop=(0.16, 0.42), curve=0.2, density=1.0,
         extra_in=""):
    """A painted object: wash fill, shadow crescent, brush strokes along the form, highlight, inked edge."""
    x0, y0, x1, y1 = box
    W, H = x1 - x0, y1 - y0
    m = min(W, H)
    n = n if n is not None else int(W * H / 140 * density)
    length = length or (m * 0.12, m * 0.42)
    width = width or (max(1.0, m * 0.012), max(2.2, m * 0.034))
    tints = tints or [light, dark, base]
    pid, cid = u("p"), u("c")
    rnd = random.Random(seed)
    use = lambda attrs: f'<use href="#{pid}" {attrs}/>'
    out = [f'<defs><path id="{pid}" d="{d}"/><clipPath id="{cid}"><use href="#{pid}"/></clipPath></defs>', use(f'fill="{base}"'),
           use(f'fill="{base}" opacity="0.35" transform="translate({rnd.uniform(-1, 1):.1f} {rnd.uniform(-1, 1):.1f})"'),
           f'<g clip-path="url(#{cid})">']
    if shade:
        sx, sy = shade
        out.append(use(f'fill="{dark}" opacity="{shade_op}"') + use(f'fill="{base}" transform="translate({-sx} {-sy})"') +
                   use(f'fill="{base}" opacity="0.45" transform="translate({-sx * 0.45:.1f} {-sy * 0.45:.1f})"'))
    out.append(brush((x0 - 6, y0 - 6, x1 + 6, y1 + 6), tints, seed, n, angle, length, width, sop, curve))
    if hi:
        hx, hy, hrx, hry = hi
        out.append(f'<path d="{blob(hx, hy, hrx, hry, seed + 3, 0.12, 12)}" fill="{light}" opacity="{hi_op}"/>')
        out.append(brush((hx - hrx, hy - hry, hx + hrx, hy + hry), [light, "#FFFFFF"], seed + 4, max(4, hrx * hry / 40), angle,
                         (length[0], length[1] * 0.7), width, (0.25, 0.55), curve))
    out.append(extra_in)
    out.append("</g>")
    if ink_w:
        out.append(use(f'fill="none" stroke="{ink_col}" stroke-width="{ink_w:.2f}" stroke-linejoin="round" stroke-linecap="round" opacity="{ink_op:.2f}"'))
        out.append(use(f'fill="none" stroke="{ink_col}" stroke-width="{ink_w * rnd.uniform(0.45, 0.7):.2f}" stroke-linejoin="round" opacity="{ink_op * 0.6:.2f}" '
                       f'transform="translate({rnd.uniform(-0.6, 0.6):.2f} {rnd.uniform(-0.6, 0.6):.2f})"'))
    return "".join(out)


def wobble_line(pts, seed, amt=1.2):
    return smooth_open(jitter(pts, seed, amt))


def hand_rule(x1, x2, y, col, w, seed, sag=0):
    pts = [(x1 + (x2 - x1) * t, y + sag * math.sin(math.pi * t)) for t in (0, 0.25, 0.5, 0.75, 1)]
    return ink(wobble_line(pts, seed, 0.9), col, w, seed, 2, 0.9)


def bg(u, base, tints, seed, fleck=FLECK, angle=-20, n=260, length=(60, 170), width=(6, 18), op=(0.05, 0.14), mottle=None):
    """Painted ground: paper tooth, broad brush strokes across the whole sheet, a few pooled washes."""
    out = [paper(u("pp"), base, fleck, seed, 1.2), brush((-40, -40, 640, 640), tints, seed + 1, n, angle, length, width, op, 0.15)]
    rnd = random.Random(seed + 2)
    for col in (mottle or tints[:2]):
        for _ in range(3):
            out.append(f'<path d="{blob(rnd.uniform(40, 560), rnd.uniform(40, 560), rnd.uniform(90, 200), rnd.uniform(70, 160), rnd.randint(0, 999), 0.14, 16)}" fill="{col}" opacity="{rnd.uniform(0.04, 0.09):.2f}"/>')
    return "".join(out)


def vignette(u, color, op=0.45, inner=0.6):
    g = u("vg")
    return (f'<defs><radialGradient id="{g}" cx="0.5" cy="0.5" r="0.72"><stop offset="{inner}" stop-color="{color}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="{op}"/></radialGradient></defs><rect width="600" height="600" fill="url(#{g})"/>')


def finish(u, color=INK, op=0.9, seed=9):
    return grain(u("gr"), color, seed, op)


# ---------------------------------------------------------------- lettering
def btext(u, x, y, s, font, size, fill, tints, seed, max_w=470, ls=0, anchor="middle", angle=-70, shadow=None,
          soff=(0.03, 0.04), edge=None, edge_w=0, rot=0, dens=1.0, hi=None, sop=(0.22, 0.55)):
    """Brush-textured lettering: base colour, visible strokes clipped to the glyphs, offset shadow, optional edge."""
    size = fit_size(s, font, size, max_w, ls)
    w = measure(s, font, size, ls)
    if anchor == "middle":
        xx, x0 = x + ls / 2, x - w / 2
    elif anchor == "start":
        xx, x0 = x, x
    else:
        xx, x0 = x, x - w
    lsa = f' letter-spacing="{ls}"' if ls else ""
    t = f'text-anchor="{anchor}" {font} font-size="{size}"{lsa}'
    cid = u("bt")
    out = [f'<g transform="rotate({rot} {_f(x)} {_f(y)})">' if rot else "<g>"]
    if edge:
        out.append(f'<text x="{_f(xx)}" y="{_f(y)}" {t} fill="{edge}" stroke="{edge}" stroke-width="{edge_w}" stroke-linejoin="round">{esc(s)}</text>')
    if shadow:
        out.append(f'<text x="{_f(xx + size * soff[0])}" y="{_f(y + size * soff[1])}" {t} fill="{shadow}">{esc(s)}</text>')
    out.append(f'<text x="{_f(xx)}" y="{_f(y)}" {t} fill="{fill}">{esc(s)}</text>')
    n = int(dens * 90 * w / size) + 20
    out.append(f'<clipPath id="{cid}"><text x="{_f(xx)}" y="{_f(y)}" {t}>{esc(s)}</text></clipPath><g clip-path="url(#{cid})">')
    out.append(brush((x0 - 8, y - size * 0.85, x0 + w + 8, y + size * 0.25), tints, seed, n, angle,
                     (size * 0.22, size * 0.62), (size * 0.025, size * 0.065), sop, 0.2))
    if hi:
        out.append(brush((x0, y - size * 0.8, x0 + w, y - size * 0.45), [hi], seed + 5, n * 0.25, -8,
                         (size * 0.1, size * 0.3), (size * 0.01, size * 0.03), (0.3, 0.6), 0.2))
    out.append("</g></g>")
    return "".join(out), size, w


def plain(x, y, s, font, size, fill, max_w=470, ls=0, anchor="middle", extra=""):
    size = fit_size(s, font, size, max_w, ls)
    xx = x + ls / 2 if (anchor == "middle" and ls) else x
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return f'<text x="{_f(xx)}" y="{_f(y)}" text-anchor="{anchor}" {font} font-size="{size}"{lsa} fill="{fill}"{extra}>{esc(s)}</text>'


def ruled(u, y, s, font, size, fill, seed, ls=5, line=None, line_w=42, gap=14, w=2.2, max_w=440):
    size = fit_size(s, font, size, max_w - 2 * (line_w + gap), ls)
    tw = measure(s, font, size, ls)
    ly = y - size * 0.34
    a, b = 300 - tw / 2 - gap, 300 + tw / 2 + gap
    return (plain(300, y, s, font, size, fill, max_w, ls) + hand_rule(a - line_w, a, ly, line or fill, w, seed) +
            hand_rule(b, b + line_w, ly, line or fill, w, seed + 1))


# ---------------------------------------------------------------- leaves
def _leaf_shape(kind, cx, cy, s, seed):
    rnd = random.Random(seed)
    if kind == "maple":
        pts = MAPLE + [(-x, y) for x, y in reversed(MAPLE[1:])]
        pts = [(cx + x * s + rnd.uniform(-0.5, 0.5), cy + y * s + rnd.uniform(-0.5, 0.5)) for x, y in pts]
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
        base = (cx, cy + 0.36 * s)
        tips = [(cx + tx * s, cy + ty * s) for tx, ty in ((0, -0.86), (0.82, -0.3), (-0.82, -0.3), (0.5, 0.2), (-0.5, 0.2))]
        return d, base, tips, (cx, cy + 0.44 * s)
    if kind == "oak":
        pts = []
        for i in range(0, 360, 8):
            a = math.radians(i)
            wob = 1 + 0.22 * math.sin(a * 6) if 18 < i < 342 else 1
            pts.append((cx + 0.42 * s * math.sin(a) * wob, cy - s * math.cos(a) * 0.9))
        d = smooth_closed(jitter(pts, seed, 0.5))
        base = (cx, cy + 0.85 * s)
        tips = [(cx, cy - 0.85 * s)] + [(cx + sd * 0.4 * s, cy + t * s) for t in (-0.5, -0.1, 0.3) for sd in (-1, 1)]
        return d, base, tips, (cx, cy + 0.9 * s)
    if kind == "birch":   # round-ish serrated leaf
        pts = []
        for i in range(0, 360, 10):
            a = math.radians(i)
            r = s * (0.55 + 0.45 * abs(math.cos(a / 2)) ** 1.5) * (1 + (0.05 if (i // 10) % 2 else 0))
            pts.append((cx + 0.62 * r * math.sin(a), cy - r * math.cos(a) * 0.95))
        d = smooth_closed(pts)
        base = (cx, cy + 0.6 * s)
        tips = [(cx, cy - 0.9 * s)] + [(cx + sd * 0.45 * s, cy + t * s) for t in (-0.45, -0.05) for sd in (-1, 1)]
        return d, base, tips, (cx, cy + 0.62 * s)
    # elm / willow: slim almond leaf
    wd = 0.36 * s
    pts = [(cx, cy - s)]
    for t in (0.15, 0.35, 0.55, 0.75, 0.92):
        y = cy - s + 2 * s * t * 0.92
        hw = wd * math.sin(math.pi * min(1, t * 1.05)) ** 0.8
        pts.append((cx + hw, y))
    pts.append((cx, cy + 0.85 * s))
    for t in (0.92, 0.75, 0.55, 0.35, 0.15):
        y = cy - s + 2 * s * t * 0.92
        hw = wd * math.sin(math.pi * min(1, t * 1.05)) ** 0.8
        pts.append((cx - hw, y))
    d = smooth_closed(jitter(pts, seed, 0.4))
    base = (cx, cy + 0.85 * s)
    tips = [(cx, cy - 0.9 * s)] + [(cx + sd * 0.3 * s, cy + t * s) for t in (-0.5, -0.1, 0.3) for sd in (-1, 1)]
    return d, base, tips, (cx, cy + 0.85 * s)


def leaf(u, kind, cx, cy, s, rot, pal, seed, detail=True, inkc=None, vein=None, stem=True):
    base_c, dark, light = pal
    d, base, tips, stem_pt = _leaf_shape(kind, cx, cy, s, seed)
    pid, cid = u("lp"), u("lf")
    out = [f'<g transform="rotate({rot:.0f} {_f(cx)} {_f(cy)})"><defs><path id="{pid}" d="{d}"/><clipPath id="{cid}"><use href="#{pid}"/></clipPath></defs>',
           f'<use href="#{pid}" fill="{base_c}"/><g clip-path="url(#{cid})">']
    out.append(f'<rect x="{_f(cx)}" y="{_f(cy - 1.2 * s)}" width="{_f(1.2 * s)}" height="{_f(2.4 * s)}" fill="{dark}" opacity="0.32"/>')
    if detail and s >= 11:
        fan = (lambda x, y: math.degrees(math.atan2(y - base[1], x - base[0]))) if kind in ("maple", "birch") else -90
        out.append(brush((cx - s, cy - s, cx + s, cy + s), [light, dark, base_c, light], seed, s * 1.5, fan,
                         (s * 0.25, s * 0.7), (max(0.7, s * 0.035), max(1.4, s * 0.08)), (0.2, 0.5), 0.15))
        out.append(f'<path d="{blob(cx - 0.25 * s, cy - 0.25 * s, 0.25 * s, 0.35 * s, seed, 0.2, 10)}" fill="{light}" opacity="0.3"/>')
    out.append("</g>")
    vw = max(0.7, s * 0.04)
    vc = vein or light
    if s >= 9:
        if kind in ("maple", "birch"):
            veins = "".join(f"M {_f(base[0])} {_f(base[1])} Q {_f((base[0] + tx) / 2 + 1)} {_f((base[1] + ty) / 2)} {_f(tx)} {_f(ty)} " for tx, ty in tips)
        else:
            veins = f"M {_f(base[0])} {_f(base[1])} L {_f(cx)} {_f(cy - 0.88 * s)} " + "".join(
                f"M {_f(cx)} {_f(ty + 0.18 * s)} Q {_f((cx + tx) / 2)} {_f(ty + 0.1 * s)} {_f(tx)} {_f(ty)} " for tx, ty in tips[1:])
        out.append(f'<path d="{veins}" fill="none" stroke="{vc}" stroke-width="{vw:.2f}" stroke-linecap="round" opacity="0.75"/>')
    out.append(f'<use href="#{pid}" fill="none" stroke="{inkc or dark}" stroke-width="{max(0.9, s * 0.045):.2f}" stroke-linejoin="round" opacity="0.8"/>')
    if stem:
        out.append(ink(f"M {_f(stem_pt[0])} {_f(stem_pt[1] - 2)} q {s * 0.05:.1f} {s * 0.25:.1f} {-s * 0.08:.1f} {s * 0.45:.1f}",
                       inkc or dark, max(1.1, s * 0.07), seed + 1, 1, 0.95))
    out.append("</g>")
    return "".join(out)


def scatter_leaves(u, specs, seed=0, detail=True):
    """specs: (kind, x, y, size, rot, pal)"""
    return "".join(leaf(u, k, x, y, s, r, p, seed + i * 7, detail) for i, (k, x, y, s, r, p) in enumerate(specs))


# ---------------------------------------------------------------- painted objects
def pumpkin(u, cx, cy, w, h, seed, pal=PK_OR, leaf_on=True, curl=True, stem=("#8A7A44", "#4E3E1E", "#B8A868"),
            leafc=("#6E8A3E", "#46602A", "#9AB45E"), inkc=None, cast=True, lobes=5, stem_h=0.3, stem_lean=1):
    body, dark, light, deep = pal
    inkc = inkc or deep
    out = []
    if cast:
        out.append(shadow(u, cx + 0.06 * w, cy + 0.47 * h, 0.6 * w, 0.1 * h, 0.35))
    outline = blob(cx, cy, 0.5 * w, 0.5 * h, seed, 0.025, 24)
    if lobes == 5:
        spec = [(-0.3, 0.24, 0.46, dark), (0.3, 0.24, 0.46, dark), (-0.15, 0.26, 0.5, body), (0.15, 0.26, 0.5, body), (0, 0.22, 0.5, body)]
        ribs = (-0.3, -0.11, 0.11, 0.3)
    else:
        spec = [(-0.2, 0.3, 0.48, dark), (0.2, 0.3, 0.48, body), (0, 0.24, 0.5, body)]
        ribs = (-0.14, 0.14)
    out.append(f'<path d="{outline}" fill="{dark}"/>')
    for k, (dx, rx, ry, col) in enumerate(spec):
        out.append(wash(blob(cx + dx * w, cy, rx * w, ry * h, seed + k, 0.03, 16), col, seed + k, 2, 0.8, 0.5))
    cid = u("pk")
    gid = u("pg")
    out.append(f'<defs><radialGradient id="{gid}" cx="{_f(cx + 0.32 * w)}" cy="{_f(cy + 0.28 * h)}" r="{_f(0.62 * w)}" gradientUnits="userSpaceOnUse">'
               f'<stop offset="0" stop-color="{deep}" stop-opacity="0.55"/><stop offset="1" stop-color="{deep}" stop-opacity="0"/></radialGradient></defs>')
    out.append(f'<clipPath id="{cid}"><path d="{outline}"/></clipPath><g clip-path="url(#{cid})">')
    curve_ang = (lambda x, y: -90 + (x - cx) / (0.5 * w) * 28 * (1 if y < cy else -1))
    out.append(brush((cx - 0.55 * w, cy - 0.55 * h, cx + 0.55 * w, cy + 0.55 * h), [light, dark, light, deep, body], seed,
                     w * h / 90, curve_ang, (0.14 * h, 0.42 * h), (max(1, 0.01 * w), max(2, 0.026 * w)), (0.16, 0.42), 0.12, 8))
    out.append(f'<rect x="{_f(cx - w)}" y="{_f(cy - h)}" width="{_f(2 * w)}" height="{_f(2 * h)}" fill="url(#{gid})"/>')
    out.append(f'<path d="{blob(cx - 0.2 * w, cy - 0.12 * h, 0.08 * w, 0.26 * h, seed + 5, 0.15, 10)}" fill="{light}" opacity="0.45"/>')
    out.append("</g>")
    for dx in ribs:
        out.append(ink(f"M {_f(cx + dx * w)} {_f(cy - 0.42 * h)} Q {_f(cx + dx * 1.5 * w)} {_f(cy)} {_f(cx + dx * w)} {_f(cy + 0.46 * h)}",
                       inkc, max(1.1, 0.014 * w), seed + 7, 1, 0.55))
    out.append(f'<path d="M {_f(cx - 0.21 * w)} {_f(cy - 0.28 * h)} Q {_f(cx - 0.3 * w)} {_f(cy - 0.02 * h)} {_f(cx - 0.22 * w)} {_f(cy + 0.22 * h)}" '
               f'stroke="#FFF1D8" stroke-width="{max(1.4, 0.022 * w):.1f}" fill="none" stroke-linecap="round" stroke-dasharray="{0.1 * h:.0f} {0.03 * h:.0f} {0.2 * h:.0f} 400" opacity="0.5"/>')
    out.append(ink(outline, inkc, max(1.3, 0.016 * w), seed + 3, 2, 0.75))
    # stem
    sw = max(5, 0.07 * w)
    sh = stem_h * h
    sx = cx - 0.02 * w
    top = cy - 0.44 * h
    sd = smooth_closed([(sx - sw * 0.6, top + 4), (sx - sw * 0.5, top - sh * 0.5), (sx - sw * 0.2 + stem_lean * sw * 0.6, top - sh),
                        (sx + sw * 0.8 + stem_lean * sw * 0.7, top - sh + 2), (sx + sw * 0.5, top - sh * 0.45), (sx + sw * 0.7, top + 4)])
    out.append(f'<path d="{blob(cx, top + 2, 0.16 * w, 0.05 * h, seed + 8, 0.1, 12)}" fill="{deep}" opacity="0.6"/>')
    out.append(form(u, sd, (sx - sw, top - sh, sx + sw * 1.5, top + 4), stem[0], stem[1], stem[2], seed + 9, -90,
                    n=max(8, sh * 1.2), shade=(2, 0), ink_w=max(1.1, 0.012 * w), ink_col=stem[1]))
    if curl:
        cx0, cy0 = sx + sw * 0.6, top - sh * 0.3
        out.append(ink(f"M {_f(cx0)} {_f(cy0)} q {0.14 * w:.1f} {-0.02 * h:.1f} {0.16 * w:.1f} {-0.16 * h:.1f} "
                       f"q {0.01 * w:.1f} {-0.1 * h:.1f} {-0.07 * w:.1f} {-0.08 * h:.1f} q {-0.05 * w:.1f} {0.02 * h:.1f} {-0.02 * w:.1f} {0.06 * h:.1f}",
                       leafc[1], max(1.1, 0.011 * w), seed + 10, 1, 0.9))
    if leaf_on:
        lx, ly = sx - 0.16 * w, top - 0.02 * h
        lf = blob(lx, ly, 0.13 * w, 0.055 * w, seed + 11, 0.14, 12, rot=12)
        out.append(form(u, lf, (lx - 0.14 * w, ly - 0.07 * w, lx + 0.14 * w, ly + 0.07 * w), leafc[0], leafc[1], leafc[2], seed + 12,
                        10, n=w * 0.3, shade=(0, 2), ink_w=max(1, 0.01 * w), ink_col=leafc[1]))
        out.append(f'<path d="M {_f(lx + 0.12 * w)} {_f(ly + 0.02 * w)} Q {_f(lx)} {_f(ly - 0.01 * w)} {_f(lx - 0.11 * w)} {_f(ly - 0.03 * w)}" '
                   f'stroke="{leafc[1]}" stroke-width="{max(0.8, 0.008 * w):.1f}" fill="none"/>')
    return "".join(out)


def apple(u, cx, cy, r, seed, pal=("#D2382A", "#8E1E16", "#F2805A"), blush="#F2C24A", rot=0, leaf_on=True, cast=False, inkc="#5A1A10"):
    body, dark, light = pal
    pts = []
    for i in range(24):
        a = 2 * math.pi * i / 24
        k = 1 - 0.13 * max(0, math.cos(a + math.pi / 2)) ** 6 - 0.04 * math.sin(2 * a) ** 2
        pts.append((cx + r * 1.02 * math.cos(a) * k, cy + r * 0.95 * math.sin(a) * k + (0.06 * r if math.sin(a) > 0 else 0)))
    d = smooth_closed(jitter(pts, seed, r * 0.015))
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    if cast:
        out.append(shadow(u, cx + r * 0.15, cy + r * 0.95, r * 1.1, r * 0.22, 0.35))
    ring = lambda x, y: math.degrees(math.atan2(y - cy, x - cx)) + 90
    out.append(form(u, d, (cx - r, cy - r, cx + r, cy + r), body, dark, light, seed, ring, n=r * r / 14, shade=(r * 0.22, r * 0.16),
                    shade_op=0.6, hi=(cx - 0.38 * r, cy - 0.32 * r, 0.18 * r, 0.26 * r), hi_op=0.5, ink_w=max(1.1, r * 0.04), ink_col=inkc,
                    tints=[light, dark, blush, body], sop=(0.15, 0.4), curve=0.4))
    out.append(f'<path d="{blob(cx - 0.32 * r, cy - 0.36 * r, 0.07 * r, 0.14 * r, seed + 2, 0.1, 8, rot=25)}" fill="#FFF6E8" opacity="0.85"/>')
    out.append(ink(f"M {_f(cx)} {_f(cy - 0.78 * r)} q {0.04 * r:.1f} {-0.3 * r:.1f} {0.16 * r:.1f} {-0.42 * r:.1f}", "#4A2A14", max(1.6, r * 0.09), seed + 3, 1, 1))
    if leaf_on:
        out.append(leaf(u, "elm", cx + 0.34 * r, cy - 1.06 * r, 0.32 * r, 62, L_OLIVE, seed + 4, r > 18, stem=False))
    out.append("</g>")
    return "".join(out)


def sparkle(x, y, s, col="#FFF4D6", op=0.9):
    return (f'<path d="M {_f(x)} {_f(y - s)} Q {_f(x + s * 0.15)} {_f(y - s * 0.15)} {_f(x + s)} {_f(y)} Q {_f(x + s * 0.15)} {_f(y + s * 0.15)} '
            f'{_f(x)} {_f(y + s)} Q {_f(x - s * 0.15)} {_f(y + s * 0.15)} {_f(x - s)} {_f(y)} Q {_f(x - s * 0.15)} {_f(y - s * 0.15)} {_f(x)} {_f(y - s)} Z" '
            f'fill="{col}" opacity="{op}"/>')


def heart_path(cx, cy, s):
    k = s / 16
    return (f"M {cx:.1f} {cy + 18 * k:.1f} C {cx - 30 * k:.1f} {cy - 2 * k:.1f} {cx - 24 * k:.1f} {cy - 24 * k:.1f} {cx - 8 * k:.1f} {cy - 20 * k:.1f} "
            f"Q {cx - 2 * k:.1f} {cy - 18 * k:.1f} {cx:.1f} {cy - 12 * k:.1f} Q {cx + 2 * k:.1f} {cy - 18 * k:.1f} {cx + 8 * k:.1f} {cy - 20 * k:.1f} "
            f"C {cx + 24 * k:.1f} {cy - 24 * k:.1f} {cx + 30 * k:.1f} {cy - 2 * k:.1f} {cx:.1f} {cy + 18 * k:.1f} Z")


def painted_heart(u, cx, cy, s, pal, seed):
    d = heart_path(cx, cy, s)
    return form(u, d, (cx - s * 1.6, cy - s * 1.5, cx + s * 1.6, cy + s * 1.2), pal[0], pal[1], pal[2], seed, -60, n=s * 4,
                shade=(s * 0.18, s * 0.14), ink_w=max(1, s * 0.08), ink_col=pal[1])


DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


# ================================================================ oh my gourd
@design("oh-my-gourd")
def oh_my_gourd():
    u = Ids("oh-my-gourd")
    o = [bg(u, "#5A2636", ["#6E3446", "#4A1C2C", "#7E4050", "#3E1626"], 11, fleck="#E8C8B8", angle=-25)]
    o.append(glow(u, 300, 330, 250, "#E08A5A", 0.42, 210))
    o.append(vignette(u, "#240A12", 0.55))
    # a painted table top / ground the stack sits on
    tbl = smooth_closed([(-20, 412), (150, 400), (300, 404), (460, 398), (620, 410), (620, 620), (-20, 620)])
    o.append(form(u, tbl, (-20, 396, 620, 620), "#3E1A26", "#2A0E18", "#5A2A38", 12, -4, n=140, shade=None, ink_w=0,
                  length=(40, 120), width=(2, 6)))
    o.append(f'<path d="M -10 408 Q 150 396 300 402 T 610 406" stroke="#8A4A50" stroke-width="2" fill="none" opacity="0.5"/>')
    # side gourds
    o.append(pumpkin(u, 126, 388, 112, 72, 31, PK_GREEN, leaf_on=False, curl=False, lobes=3, inkc="#22301A"))
    o.append(pumpkin(u, 478, 390, 100, 68, 32, PK_GOLD, leaf_on=False, curl=True, lobes=3))
    # the stack
    o.append(pumpkin(u, 300, 350, 262, 132, 21, PK_OR, leaf_on=False, curl=False, stem_h=0.12))
    o.append(pumpkin(u, 302, 262, 180, 86, 22, PK_CREAM, leaf_on=False, curl=False, stem_h=0.14, inkc="#7A6448"))
    o.append(pumpkin(u, 304, 198, 108, 60, 23, PK_SAGE, leaf_on=True, curl=True, stem_h=0.4, inkc="#4A5640"))
    # leaves resting and falling
    o.append(scatter_leaves(u, [("maple", 196, 414, 24, -30, L_RED), ("oak", 408, 418, 20, 70, L_BROWN),
                                ("maple", 82, 268, 19, 20, L_GOLD), ("elm", 516, 262, 18, -40, L_ORANGE),
                                ("maple", 508, 166, 15, 35, L_CRAN), ("birch", 92, 180, 14, -20, L_GOLD)], 40))
    for x, y, s in ((470, 106, 6), (128, 112, 5), (548, 340, 5), (56, 350, 4)):
        o.append(sparkle(x, y, s, "#F6D9A8", 0.7))
    t, _, _ = btext(u, 300, 136, "oh my", SERIF_IT, 104, "#F6E4CC", ["#FFF4E2", "#E6C8A8", "#F2D6B6"], 3, max_w=330,
                    angle=-35, shadow="#2A0C16", soff=(0.02, 0.05))
    o.append(t)
    t, _, _ = btext(u, 300, 530, "GOURD!", BEBAS, 132, "#EAA93A", ["#F6C860", "#C8841E", "#FFD98A", "#B8701A"], 4, max_w=400,
                    ls=6, angle=-78, shadow="#22080F", soff=(0.025, 0.04), hi="#FFF0C0")
    o.append(t)
    o.append(finish(u, "#F0D8C8", 0.6))
    return "".join(o)


# ================================================================ autumn leaves & pumpkins please
@design("autumn-leaves-pumpkins-please")
def autumn_leaves():
    u = Ids("autumn-leaves-pumpkins-please")
    o = [bg(u, "#3E4A2C", ["#4A5834", "#34401E", "#566440", "#2E3818"], 12, fleck="#E8DCC0", angle=30)]
    o.append(vignette(u, "#1A2010", 0.5))
    cx, cy = 300, 290
    o.append(glow(u, cx, cy, 240, "#F2C27A", 0.35))
    disc = blob(cx, cy, 176, 172, 5, 0.025, 28)
    o.append(form(u, disc, (cx - 180, cy - 176, cx + 180, cy + 176), "#F6EBD6", "#E2CCAA", "#FFF8EA", 6, -25, n=260,
                  shade=(10, 12), shade_op=0.35, length=(30, 90), width=(3, 8), sop=(0.08, 0.22), ink_w=2.2, ink_col="#6A4A2A"))
    # wreath: leaves around the ring, overlapping, slanting clockwise
    rnd = random.Random(7)
    kinds = ["maple", "oak", "elm", "maple", "birch", "maple", "elm"]
    specs = []
    N = 34
    for i in range(N):
        a = -math.pi / 2 + 2 * math.pi * i / N
        if 0.95 < a % (2 * math.pi) < 2.2:   # leave room for the pumpkins at the bottom
            continue
        for layer in (0, 1):
            rr = 200 + (14 if layer else -6) + rnd.uniform(-6, 6)
            aa = a + (0.08 if layer else 0)
            x, y = cx + rr * math.cos(aa), cy + rr * math.sin(aa)
            rot = math.degrees(aa) + 90 + 50 + rnd.uniform(-20, 20)
            s = rnd.uniform(22, 30) if layer == 0 else rnd.uniform(18, 24)
            specs.append((rnd.choice(kinds), x, y, s, rot, rnd.choice(LEAF_PALS)))
    rnd.shuffle(specs)
    o.append(scatter_leaves(u, specs, 100))
    # berries and acorns tucked in
    for i in range(10):
        a = -math.pi / 2 + 2 * math.pi * (i + 0.5) / 10 + 0.1
        if 0.9 < a % (2 * math.pi) < 2.3:
            continue
        bx, by = cx + 212 * math.cos(a), cy + 212 * math.sin(a)
        for j in range(3):
            px, py = bx + 7 * math.cos(j * 2.1 + i), by + 7 * math.sin(j * 2.1 + i)
            o.append(f'<circle cx="{_f(px)}" cy="{_f(py)}" r="5.2" fill="#B02A22"/><circle cx="{_f(px)}" cy="{_f(py)}" r="5.2" fill="none" stroke="#5A1010" stroke-width="1.2" opacity="0.8"/>'
                     f'<circle cx="{_f(px - 1.6)}" cy="{_f(py - 1.8)}" r="1.5" fill="#FFD8C8" opacity="0.9"/>')
    # pumpkins at the base of the wreath
    o.append(pumpkin(u, 228, 478, 96, 64, 51, PK_CREAM, leaf_on=False, curl=False, inkc="#7A6448"))
    o.append(pumpkin(u, 384, 482, 88, 58, 52, PK_GOLD, leaf_on=False, curl=True, lobes=3))
    o.append(pumpkin(u, 304, 488, 128, 82, 53, PK_OR, leaf_on=True, curl=True))
    # lettering inside the disc
    t, _, _ = btext(u, cx, 236, "autumn leaves", SERIF_IT, 50, "#5A2E18", ["#7A4224", "#3E1E0E", "#8E5430"], 13, max_w=300, angle=-30)
    o.append(t)
    t, s2, w2 = btext(u, cx, 318, "& PUMPKINS", BEBAS, 84, "#C2501E", ["#E8792E", "#9A3A12", "#F29A4A", "#B8481A"], 14, max_w=310,
                      ls=3, angle=-75, shadow="#E8C8A0", soff=(0.03, 0.045))
    o.append(t)
    t, _, _ = btext(u, cx, 384, "please", SERIF_IT, 62, "#5A2E18", ["#7A4224", "#3E1E0E", "#8E5430"], 15, max_w=240, angle=-30)
    o.append(t)
    o.append(hand_rule(cx - 50, cx + 50, 404, "#B8481E", 2.2, 3, 3))
    o.append(finish(u, INK, 0.7))
    return "".join(o)


# ================================================================ scarf season
def plaid_fill(box, base, bands, seed, rot=0, cx=300, cy=300):
    """bands: list of (color, width, spacing, offset, opacity) applied both directions."""
    x0, y0, x1, y1 = box
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})"><rect x="{x0 - 200}" y="{y0 - 200}" width="{x1 - x0 + 400}" height="{y1 - y0 + 400}" fill="{base}"/>']
    for col, w, sp, off, op in bands:
        k = x0 - 200 + off
        while k < x1 + 200:
            out.append(f'<rect x="{_f(k)}" y="{y0 - 200}" width="{w}" height="{y1 - y0 + 400}" fill="{col}" opacity="{op}"/>')
            k += sp
        k = y0 - 200 + off
        while k < y1 + 200:
            out.append(f'<rect x="{x0 - 200}" y="{_f(k)}" width="{x1 - x0 + 400}" height="{w}" fill="{col}" opacity="{op}"/>')
            k += sp
    out.append("</g>")
    return "".join(out)


@design("scarf-season")
def scarf_season():
    u = Ids("scarf-season")
    o = [bg(u, "#F3E6CF", ["#EAD6B4", "#F8EEDC", "#E2C9A2"], 21, angle=-15)]
    o.append(glow(u, 300, 380, 250, "#F2B878", 0.4))
    # wind-blown leaves behind
    o.append(scatter_leaves(u, [("maple", 92, 300, 26, -25, L_ORANGE), ("oak", 118, 430, 21, 60, L_GOLD), ("elm", 76, 520, 17, 75, L_CRAN),
                                ("birch", 508, 258, 16, -30, L_OLIVE), ("maple", 486, 556, 15, 30, L_RED), ("maple", 528, 330, 13, 15, L_GOLD)], 60))
    for i, (x0, y0) in enumerate(((150, 250), (440, 300), (430, 470))):
        o.append(ink(wobble_line([(x0, y0), (x0 + 30, y0 - 8), (x0 + 60, y0 - 4), (x0 + 70, y0 - 16), (x0 + 60, y0 - 24)], i, 0.5), "#C9A27A", 1.8, i, 1, 0.6))
    fox, fdark, flight, finc = "#D8682C", "#A8441A", "#F29A52", "#5A2410"
    # body / shoulders (bleeds off the bottom)
    body = smooth_closed([(232, 380), (200, 432), (166, 520), (150, 640), (450, 640), (434, 520), (400, 432), (368, 380)])
    o.append(form(u, body, (150, 380, 450, 640), fox, fdark, flight, 70, -100, shade=(-18, 0), shade_op=0.45, ink_w=2.4, ink_col=finc))
    chest = blob(300, 560, 82, 110, 71, 0.06, 16)
    o.append(form(u, chest, (218, 450, 382, 670), "#FBF0DE", "#E6CFB0", "#FFFFFF", 72, -90, n=90, shade=(-8, 0), ink_w=0))
    # head
    R = [(300, 262), (328, 262), (346, 254), (384, 212), (392, 206), (398, 214), (404, 280), (420, 316), (440, 346), (448, 354),
         (412, 362), (372, 392), (300, 406)]
    head = smooth_closed(R + [(600 - x, y) for x, y in reversed(R[1:-1])])
    o.append(form(u, head, (152, 206, 448, 406), fox, fdark, flight, 73, lambda x, y: math.degrees(math.atan2(y - 330, x - 300)) + 90,
                  n=420, shade=(-14, 10), shade_op=0.4, hi=(262, 284, 40, 22), hi_op=0.35, ink_w=2.6, ink_col=finc,
                  length=(10, 30), width=(1.4, 3.4)))
    for sgn in (1, -1):
        ear = smooth_closed([(300 + sgn * 52, 262), (300 + sgn * 86, 224), (300 + sgn * 96, 276)])
        o.append(form(u, ear, (300 + min(sgn * 52, sgn * 96), 222, 300 + max(sgn * 52, sgn * 96), 278), "#5A2A18", "#3A1A0E", "#8A4A2A", 74 + sgn,
                      -90, n=20, shade=None, ink_w=0))
        o.append(brush((300 + min(sgn * 58, sgn * 90), 250, 300 + max(sgn * 58, sgn * 90), 276), ["#FBF0DE", "#F6DCC0"], 75 + sgn, 14, -90 + sgn * 25,
                       (8, 16), (1, 2.2), (0.6, 0.9), 0.3))
    mask = smooth_closed([(300, 366), (334, 348), (372, 338), (412, 346), (446, 354), (410, 364), (372, 392), (300, 404),
                          (228, 392), (190, 364), (154, 354), (188, 346), (228, 338), (266, 348)])
    o.append(form(u, mask, (154, 336, 446, 406), "#FBF0DE", "#E2C8A8", "#FFFFFF", 76, lambda x, y: -90 + (x - 300) * 0.4, n=160,
                  shade=(0, 6), shade_op=0.35, ink_w=1.4, ink_col="#B8835A", ink_op=0.6, length=(6, 16), width=(1, 2.4)))
    # cheek fluff tufts
    for sgn in (1, -1):
        o.append(ink(f"M {300 + sgn * 146} 354 l {sgn * 10} 4 M {300 + sgn * 140} 360 l {sgn * 10} 8", "#E8D2B4", 2, 77, 1, 0.9))
    # face
    for sgn in (1, -1):
        ex = 300 + sgn * 44
        o.append(ink(f"M {ex - 17} 328 Q {ex} {310} {ex + 17} 328", "#2A140A", 4.2, 78 + sgn, 2, 1))
        o.append(ink(f"M {ex + sgn * 17} 328 l {sgn * 6} -5", "#2A140A", 2.2, 79, 1, 1))
        o.append(f'<path d="{blob(300 + sgn * 70, 356, 18, 9, 80 + sgn, 0.1, 10)}" fill="#E8705A" opacity="0.4"/>')
    o.append(form(u, blob(300, 368, 14, 9.5, 81, 0.06, 12), (286, 358, 314, 378), "#3A1E14", "#1E0E08", "#6A4A3A", 82, -30, n=10,
                  shade=None, hi=(295, 364, 4, 2.5), hi_op=0.7, ink_w=0))
    o.append(ink("M 300 377 q 1 9 -10 12 M 300 377 q -1 9 10 12", "#3A1E14", 2.2, 83, 1, 0.9))
    # scarf: wrap, knot and two tails blowing to the right
    bands = [("#2E4A3A", 15, 60, 6, 0.75), ("#1E2E3A", 6, 60, 28, 0.6), ("#E8B04A", 3, 60, 44, 0.9), ("#F6E6CF", 2, 30, 18, 0.35)]
    base = "#B8322A"
    wrap = smooth_closed([(190, 384), (240, 398), (300, 404), (360, 398), (410, 384), (418, 410), (410, 434), (360, 452), (300, 460),
                          (240, 452), (190, 434), (182, 410)])
    tailA = smooth_closed([(346, 440), (388, 436), (404, 480), (414, 522), (370, 528), (360, 480)])
    tailB = smooth_closed([(374, 438), (410, 446), (458, 482), (480, 506), (448, 530), (404, 492)])
    knot = blob(380, 444, 30, 25, 7, 0.08, 16, rot=-10)
    o.append(shadow(u, 300, 470, 130, 18, 0.25))
    parts = [(tailA, -6, (340, 430, 420, 532)), (tailB, -40, (370, 432, 486, 536)), (wrap, 0, (180, 380, 420, 462)), (knot, 30, (348, 418, 412, 470))]
    for k, (d, rot, box) in enumerate(parts):
        cid = u("sc")
        o.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath><g clip-path="url(#{cid})">')
        o.append(plaid_fill(box, base, bands, k, rot, (box[0] + box[2]) / 2, (box[1] + box[3]) / 2))
        ang = -90 + rot if k < 2 else (0 if k == 2 else 40)
        o.append(brush(box, ["#E26A50", "#7A1A16", "#F6E6CF", "#2E4A3A"], 30 + k, (box[2] - box[0]) * (box[3] - box[1]) / 60, ang,
                       (6, 16), (1, 2.4), (0.15, 0.4), 0.3))
        g = u("sg")
        if k == 2:
            o.append(f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3A0A08" stop-opacity="0.35"/>'
                     f'<stop offset="0.35" stop-color="#FFF0D8" stop-opacity="0.15"/><stop offset="1" stop-color="#3A0A08" stop-opacity="0.45"/></linearGradient></defs>')
            for t in (0.3, 0.55, 0.8):   # soft folds
                o.append(ink(wobble_line([(184, 386 + 60 * t), (300, 400 + 62 * t), (416, 386 + 60 * t)], k, 1), "#5A1010", 1.8, k, 1, 0.3))
        else:
            o.append(f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFF0D8" stop-opacity="0.2"/>'
                     f'<stop offset="0.5" stop-color="#FFF0D8" stop-opacity="0"/><stop offset="1" stop-color="#3A0A08" stop-opacity="0.45"/></linearGradient></defs>')
        o.append(f'<rect x="{box[0] - 10}" y="{box[1] - 10}" width="{box[2] - box[0] + 20}" height="{box[3] - box[1] + 20}" fill="url(#{g})"/>')
        o.append("</g>")
        o.append(ink(d, "#4A120E", 2.4, 50 + k, 2, 0.85))
    rnd = random.Random(5)
    for (x0, y0, x1, y1) in ((370, 528, 414, 522), (448, 530, 480, 506)):
        for t in range(8):
            fx, fy = x0 + (x1 - x0) * t / 7, y0 + (y1 - y0) * t / 7
            col = rnd.choice(["#B8322A", "#2E4A3A", "#B8322A", "#E8B04A"])
            o.append(f'<path d="M {_f(fx)} {_f(fy - 2)} q {rnd.uniform(2, 6):.1f} 8 {rnd.uniform(4, 10):.1f} {rnd.uniform(13, 18):.1f}" stroke="{col}" stroke-width="3.2" stroke-linecap="round" fill="none"/>')
    t, _, _ = btext(u, 300, 140, "SCARF", JOS, 110, "#3A2418", ["#5A3420", "#2A1608", "#6E4430"], 16, max_w=420, ls=16, angle=-80,
                    shadow="#E2C49A", soff=(0.025, 0.04))
    o.append(t)
    t, _, _ = btext(u, 300, 204, "season", SERIF_IT, 74, "#B8322A", ["#D2483A", "#8E1E16", "#E26A50"], 17, max_w=280, angle=-35,
                    shadow="#F6E6CF", soff=(0.02, 0.03))
    o.append(t)
    o.append(finish(u))
    return "".join(o)


# ---------------------------------------------------------------- landscape helpers
def hill(u, pts, bottom, base, dark, light, seed, angle=-4, n=None, ink_w=0, shade=None, **kw):
    d = smooth_open(pts) + f" L {pts[-1][0]} {bottom} L {pts[0][0]} {bottom} Z"
    ys = [p[1] for p in pts]
    box = (pts[0][0], min(ys) - 4, pts[-1][0], bottom)
    return form(u, d, box, base, dark, light, seed, angle, n=n, shade=shade, ink_w=ink_w, length=kw.pop("length", (20, 70)),
                width=kw.pop("width", (2, 5)), **kw)


def fruit_tree(u, x, base, r, seed, greens=("#6E8A3E", "#4A6228", "#9AB45E"), fruit=8, fruitc=("#D2382A", "#FFD8C8"), detail=True,
               trunk=("#7A5232", "#4A3018", "#A07A52"), inkc=INK, ink_op=0.75):
    rnd = random.Random(seed)
    out = []
    tw = r * 0.11
    tr = smooth_closed([(x - tw, base), (x - tw * 0.7, base - r * 0.6), (x - r * 0.38, base - r * 1.05), (x - r * 0.3, base - r * 1.12),
                        (x, base - r * 0.8), (x + r * 0.32, base - r * 1.14), (x + r * 0.4, base - r * 1.06), (x + tw * 0.7, base - r * 0.6), (x + tw, base)])
    out.append(form(u, tr, (x - r * 0.4, base - r * 1.15, x + r * 0.4, base), trunk[0], trunk[1], trunk[2], seed, -90,
                    n=r * 0.8 if detail else 6, shade=(tw * 0.6, 0), ink_w=max(1, r * 0.03) if detail else 0, ink_col=inkc))
    cy = base - r * 1.5
    puffs = [(-0.55, 0.18, 0.48), (0.55, 0.15, 0.5), (-0.22, -0.32, 0.56), (0.28, -0.28, 0.54), (0, 0.18, 0.6)]
    d = " ".join(blob(x + dx * r, cy + dy * r, rr * r * 1.05, rr * r, seed + i, 0.07, 14) for i, (dx, dy, rr) in enumerate(puffs))
    ring = lambda px, py: math.degrees(math.atan2(py - cy, px - x)) + 90
    fr = []
    for i in range(fruit):
        a = rnd.uniform(0, 2 * math.pi)
        rr = rnd.uniform(0.15, 0.85) * r
        fx, fy = x + rr * math.cos(a) * 1.05, cy + rr * math.sin(a) * 0.75 + r * 0.05
        ar = max(1.6, r * 0.075)
        fr.append(f'<circle cx="{_f(fx)}" cy="{_f(fy)}" r="{_f(ar)}" fill="{fruitc[0]}"/>')
        if detail:
            fr.append(f'<circle cx="{_f(fx - ar * 0.3)}" cy="{_f(fy - ar * 0.35)}" r="{_f(ar * 0.35)}" fill="{fruitc[1]}" opacity="0.8"/>')
    if detail:
        out.append(f'<path d="{d}" fill="none" stroke="{inkc}" stroke-width="{max(1.6, r * 0.05):.1f}" opacity="{ink_op}" stroke-linejoin="round"/>')
    out.append(form(u, d, (x - r * 1.1, cy - r * 0.95, x + r * 1.1, cy + r * 0.8), greens[0], greens[1], greens[2], seed + 1, ring,
                    n=r * r / 9 if detail else r * r / 14, shade=(r * 0.1, r * 0.14), shade_op=0.6, hi=(x - r * 0.35, cy - r * 0.4, r * 0.3, r * 0.2),
                    hi_op=0.35, ink_w=0, length=(r * 0.08, r * 0.22),
                    width=(max(0.8, r * 0.025), max(1.4, r * 0.06)), curve=0.5, extra_in="".join(fr)))
    return "".join(out)


def deckle(u, d_pts, color, seed, w=(4, 10)):
    """Dry-brush strokes in the paper colour along a vignette edge so it frays like a painted spot illustration."""
    rnd = random.Random(seed)
    out = []
    n = len(d_pts)
    for i in range(n):
        x0, y0 = d_pts[i]
        x1, y1 = d_pts[(i + 1) % n]
        for _ in range(3):
            t = rnd.random()
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
            out.append(brush((x - 2, y - 2, x + 2, y + 2), [color], rnd.randint(0, 9999), 1, ang, (14, 34), w, (0.7, 1), 0.2, 6))
    return "".join(out)


def bushel(u, cx, top, w, h, seed, fill=None, wood=("#C8954E", "#8E5E2A", "#E6BC7A")):
    """Wooden bushel basket: back rim, contents (fill), tapered slatted body and hoops."""
    out = [shadow(u, cx + 10, top + h + 2, w * 0.55, 12, 0.35)]
    rx, ry = w / 2, w * 0.12
    out.append(f'<ellipse cx="{cx}" cy="{top}" rx="{rx}" ry="{ry}" fill="#5A3A1A"/>')
    out.append(fill or "")
    bw = w * 0.36
    body = smooth_closed([(cx - rx, top), (cx - rx * 0.92, top + h * 0.5), (cx - bw, top + h), (cx, top + h + 6), (cx + bw, top + h),
                          (cx + rx * 0.92, top + h * 0.5), (cx + rx, top), (cx, top + ry)])
    slats = []
    for i in range(11):
        t = -1 + 2 * i / 10
        xt, xb = cx + t * rx * 0.98, cx + t * bw
        slats.append(f'<path d="M {_f(xt)} {top - 4} L {_f(xb)} {top + h + 8}" stroke="#6E441E" stroke-width="1.6" opacity="0.6"/>')
    out.append(form(u, body, (cx - rx, top, cx + rx, top + h + 6), wood[0], wood[1], wood[2], seed, -90, n=w * h / 70, shade=(w * 0.08, 0),
                    shade_op=0.55, ink_w=2.2, ink_col="#4A2A10", length=(h * 0.2, h * 0.6), width=(1, 3), extra_in="".join(slats)))
    for t in (0.06, 0.55):
        yy = top + h * t + (ry * 0.8 if t < 0.1 else 0)
        half = rx * (1 - t * 0.35)
        hoop = smooth_open([(cx - half - 2, yy - ry * 0.2), (cx, yy + ry * 0.75), (cx + half + 2, yy - ry * 0.2)])
        out.append(f'<path d="{hoop}" stroke="#6A3E18" stroke-width="10" fill="none" stroke-linecap="round"/>'
                   f'<path d="{hoop}" stroke="#A8743A" stroke-width="4" fill="none" stroke-linecap="round" transform="translate(0 -2)" opacity="0.8"/>')
    return "".join(out)


# ================================================================ apple picking
@design("apple-picking")
def apple_picking():
    u = Ids("apple-picking")
    o = [bg(u, PAPER, ["#EADBC0", "#F8F0E0", "#E6D2B0"], 31, angle=-10)]
    # the painted vignette
    vp = blob_pts(300, 382, 246, 166, 9, 0.05, 30)
    vd = smooth_closed(vp)
    cid = u("vig")
    o.append(f'<clipPath id="{cid}"><path d="{vd}"/></clipPath><g clip-path="url(#{cid})">')
    sky = u("sky")
    o.append(f'<defs>{lgrad(sky, [(0, "#B9D2D8"), (0.6, "#E9E4CC"), (1, "#F6DFAE")])}</defs><rect x="40" y="200" width="520" height="160" fill="url(#{sky})"/>')
    o.append(brush((40, 210, 560, 330), ["#FFFFFF", "#CFE0E2", "#F6E8C8"], 32, 60, -4, (40, 100), (3, 8), (0.1, 0.25), 0.1))
    for cx_, cy_, w_ in ((170, 252, 70), (420, 238, 90)):
        o.append(f'<path d="{blob(cx_, cy_, w_, w_ * 0.28, cx_, 0.18, 14)}" fill="#FFFFFF" opacity="0.75"/>'
                 f'<path d="{blob(cx_ + 8, cy_ + 6, w_ * 0.7, w_ * 0.14, cx_ + 1, 0.2, 12)}" fill="#E4D8C8" opacity="0.6"/>')
    o.append(glow(u, 470, 270, 120, "#FFF2C8", 0.6))
    o.append(hill(u, [(40, 318), (150, 300), (260, 312), (380, 296), (480, 306), (560, 300)], 560, "#A8B88A", "#8A9A72", "#C8D2A8", 33, n=60))
    rnd = random.Random(34)
    for x in range(70, 560, 30):   # far orchard rows
        o.append(fruit_tree(u, x + rnd.uniform(-6, 6), 330 + rnd.uniform(-3, 3), 11, 400 + x, ("#8E9E62", "#6E7E48", "#B0BC80"), 3,
                            ("#C86A4A", "#FFFFFF"), False, ("#8A7A62", "#6A5A42", "#A89A82")))
    o.append(hill(u, [(40, 344), (180, 336), (320, 346), (460, 334), (560, 342)], 560, "#9AAE62", "#6E8440", "#C2CC82", 35, n=120))
    for x in range(56, 560, 54):
        o.append(fruit_tree(u, x + rnd.uniform(-8, 8), 380 + rnd.uniform(-4, 4), 20, 500 + x, ("#7A9446", "#55702E", "#A8BC66"), 6, detail=False))
    o.append(hill(u, [(40, 392), (200, 384), (360, 396), (560, 386)], 560, "#88A04E", "#5E7A34", "#B4C474", 36, n=240, length=(10, 30), width=(1, 3), angle=-80))
    # the big tree with the ladder
    o.append(shadow(u, 470, 486, 90, 12, 0.3))
    o.append(fruit_tree(u, 462, 484, 74, 37, fruit=18))
    for k in range(1, 8):
        t = k / 8
        o.append(ink(f"M {_f(384 + 40 * t)} {_f(500 - 196 * t)} L {_f(416 + 42 * t)} {_f(500 - 196 * t)}", "#7A4A20", 5, k, 1, 1))
    for x0, x1 in ((384, 424), (416, 458)):
        o.append(ink(f"M {x0} 500 L {x1} 304", "#5A3A1A", 9, x0, 1, 1) + ink(f"M {x0 - 1} 500 L {x1 - 1} 304", "#C8904E", 4.5, x0 + 1, 1, 1))
    o.append(shadow(u, 404, 502, 30, 5, 0.35))
    o.append(brush((40, 440, 560, 560), ["#5E7A34", "#9AB45E", "#46602A", "#C2CC82"], 38, 340, -90, (6, 16), (0.8, 2), (0.3, 0.7), 0.4, 20))
    for x, y in ((318, 498), (360, 512), (512, 506), (96, 470)):
        o.append(apple(u, x, y, 9, x, leaf_on=False, cast=True))
    o.append("</g>")
    o.append(deckle(u, vp, PAPER, 39))
    # bushel of apples breaking the frame
    pile = []
    for i, (dx, dy, r) in enumerate(((-52, -6, 26), (52, -4, 25), (-20, -24, 27), (24, -26, 27), (0, -4, 26), (-60, 14, 24), (60, 14, 24),
                                     (2, -50, 26))):
        pal = ("#D2382A", "#8E1E16", "#F2805A") if i % 3 else ("#C8402A", "#7A1E16", "#F09060")
        pile.append(apple(u, 200 + dx, 432 + dy, r, 60 + i, pal, rot=dx * 0.2, leaf_on=(i == 7)))
    o.append(bushel(u, 200, 438, 190, 96, 61, "".join(pile)))
    o.append(scatter_leaves(u, [("elm", 88, 512, 15, 70, L_OLIVE), ("elm", 316, 532, 13, -60, L_GOLD)], 70))
    t, _, _ = btext(u, 300, 150, "APPLE PICKING", ANTON, 92, "#B8302A", ["#D2483A", "#8E1E16", "#E26A50", "#A8281E"], 40, max_w=470,
                    ls=3, angle=-78, shadow="#5A1A10", soff=(0.02, 0.04))
    o.append(t)
    o.append(ruled(u, 188, "FRESH FROM THE ORCHARD", MONO, 18, "#5A3420", 41, ls=3, line="#B8302A", line_w=30, gap=10, max_w=470))
    o.append(finish(u))
    return "".join(o)


# ================================================================ falling for you
def heart_poly(cx, cy, w, n=60):
    k = w / 32
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * k, cy - y * k))
    return pts


def pip(poly, x, y):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


@design("falling-for-you")
def falling_for_you():
    u = Ids("falling-for-you")
    o = [bg(u, "#F6E8D4", ["#F0D8BC", "#FAF0E2", "#EBCDB0"], 41, angle=-20)]
    o.append(glow(u, 300, 200, 250, "#F6B07A", 0.42))
    # soft ground mound
    o.append(shadow(u, 300, 384, 210, 20, 0.18))
    gr = smooth_closed(jitter([(96, 384), (180, 366), (300, 360), (420, 366), (504, 384), (420, 394), (300, 398), (180, 394)], 42, 2))
    o.append(form(u, gr, (96, 358, 504, 398), "#C2A066", "#8A7040", "#E2C88E", 43, -8, n=150, shade=(0, 5), length=(8, 22), width=(0.8, 2.2),
                  ink_w=1.8, ink_col="#7A5A2A", ink_op=0.55))
    # trunk and branches
    trunk = smooth_closed([(284, 372), (288, 320), (272, 286), (244, 254), (252, 248), (290, 280), (296, 236), (304, 236), (308, 282),
                           (344, 252), (350, 260), (316, 300), (410, 292), (414, 300), (318, 322), (318, 372)])
    o.append(form(u, trunk, (244, 236, 414, 372), "#7A5232", "#4A3018", "#A8805A", 44, -90, n=140, shade=(8, 0), ink_w=2.4, ink_col=INK,
                  length=(10, 30), width=(1, 3)))
    o.append(painted_heart(u, 302, 346, 7, ("#C8402A", "#7A1E16", "#E8705A"), 45))
    # swing from the right branch
    o.append(ink("M 378 296 L 375 352 M 402 294 L 405 350", "#6A4A2A", 2, 46, 1, 1))
    seat = smooth_closed([(362, 350), (418, 348), (420, 357), (360, 359)])
    o.append(form(u, seat, (360, 346, 420, 360), "#B8783A", "#7A4A20", "#DCA464", 47, 0, n=12, shade=(0, 3), ink_w=1.6))
    # heart-shaped crown painted from hundreds of leaf dabs
    hp = heart_poly(300, 178, 296)
    hd = smooth_closed(hp)
    o.append(f'<path d="{hd}" fill="#C25A2A" opacity="0.9"/>')
    o.append(f'<path d="{hd}" fill="#8E2A1A" opacity="0.18" transform="translate(4 5)"/>')
    rnd = random.Random(48)
    cols_dark = ["#9A2E18", "#A8401E", "#8E2A1A", "#B8481E"]
    cols_mid = ["#D9542C", "#E8792E", "#C8402A", "#EE8A34", "#D2602A"]
    cols_lit = ["#F2A84A", "#F6C860", "#F8BA62", "#FFD98A", "#EDB740"]
    groups = {}
    for layer, cols, n, off, sz in ((0, cols_dark, 170, (8, 10), (7, 11)), (1, cols_mid, 260, (0, 0), (6, 10)), (2, cols_lit, 150, (-12, -14), (5, 9))):
        for _ in range(n):
            x, y = rnd.uniform(140, 460), rnd.uniform(60, 340)
            if not pip(hp, x - off[0] * 0.6, y - off[1] * 0.6):
                continue
            if layer == 2 and ((x - 245) / 1.3) ** 2 + (y - 140) ** 2 > 95 ** 2 and rnd.random() < 0.75:
                continue
            sz_ = rnd.uniform(*sz)
            a = math.radians(rnd.uniform(0, 180))
            ca, sa = math.cos(a) * sz_, math.sin(a) * sz_
            px, py = -sa * 0.7, ca * 0.7
            groups.setdefault(rnd.choice(cols), []).append(
                f"M{_n(x - ca)} {_n(y - sa)}q{_n(ca + px)} {_n(sa + py)} {_n(2 * ca)} {_n(2 * sa)}q{_n(-ca - px)} {_n(-sa - py)} {_n(-2 * ca)} {_n(-2 * sa)}z")
    o.append("".join(f'<path fill="{c}" fill-opacity="0.92" d="{"".join(v)}"/>' for c, v in groups.items()))
    o.append(ink(hd, "#7A2A12", 1.6, 49, 1, 0.3))
    o.append(brush((160, 70, 300, 200), ["#FFE2A0"], 49, 26, -40, (8, 18), (0.8, 1.8), (0.4, 0.7), 0.3))
    # a few full leaves on the rim + drifting down
    o.append(scatter_leaves(u, [("maple", 168, 116, 18, -20, L_ORANGE), ("maple", 436, 100, 17, 25, L_RED), ("birch", 214, 262, 13, 30, L_GOLD),
                                ("maple", 462, 300, 19, 40, L_GOLD), ("elm", 514, 226, 16, -50, L_RED), ("maple", 118, 280, 17, -35, L_CRAN),
                                ("oak", 82, 176, 15, 20, L_ORANGE), ("maple", 512, 140, 14, 10, L_ORANGE), ("elm", 470, 362, 12, 70, L_ORANGE)], 50))
    pile = []
    for i in range(22):
        x = rnd.uniform(170, 440)
        y = 372 + rnd.uniform(-6, 8) - 8 * math.cos((x - 300) / 150)
        pile.append(("maple" if i % 3 else "elm", x, y, rnd.uniform(8, 11), rnd.uniform(0, 360), rnd.choice(LEAF_PALS)))
    o.append(scatter_leaves(u, pile, 80, detail=False))
    o.append(f'<path d="M 462 318 C 512 336 440 352 488 372" stroke="#B8783A" stroke-width="2" stroke-dasharray="1 7" stroke-linecap="round" fill="none"/>')
    t, s1, w1 = btext(u, 300, 478, "falling", SERIF_IT, 116, "#5A2A18", ["#7A3A20", "#3E1A0E", "#8E4A2A", "#A8502A"], 51, max_w=360,
                      angle=-35, shadow="#EBC8A0", soff=(0.02, 0.035))
    o.append(t)
    fy = 536
    t, s2, w2 = btext(u, 300, fy, "FOR YOU", JOS, 36, "#B8481E", ["#D2602A", "#8E3A12"], 52, max_w=220, ls=12, angle=-80)
    o.append(t)
    for sgn in (-1, 1):
        o.append(painted_heart(u, 300 + sgn * (w2 / 2 + 30), fy - 13, 11, ("#C8402A", "#7A1E16", "#E8705A"), 53 + sgn))
    o.append(finish(u))
    return "".join(o)


# ================================================================ sunflower fields
def sunflower(u, cx, cy, r, seed, tilt=1.0, rot=0, detail=True, petal=("#F2B826", "#C8841E", "#FFE07A"), disc=("#5A3418", "#2E1A0C", "#8A5A2A")):
    rnd = random.Random(seed)
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)}) translate({_f(cx)} {_f(cy)}) scale(1 {tilt}) translate({_f(-cx)} {_f(-cy)})">']
    radial = lambda x, y: math.degrees(math.atan2(y - cy, x - cx))
    for ring, (n, L, wd, col, dk) in enumerate(((17, 1.0, 0.24, petal[1], "#9A5E12"), (19, 0.9, 0.22, petal[0], petal[1]))):
        ds = []
        for i in range(n):
            a = 2 * math.pi * (i + ring * 0.5) / n + rnd.uniform(-0.07, 0.07)
            L2 = r * L * rnd.uniform(0.88, 1.06)
            ca, sa = math.cos(a), math.sin(a)
            nx, ny = -sa, ca
            b = r * 0.34
            w = r * wd * rnd.uniform(0.85, 1.1)
            pts = [(cx + ca * b + nx * w * 0.35, cy + sa * b + ny * w * 0.35), (cx + ca * (b + L2) * 0.6 + nx * w * 0.55, cy + sa * (b + L2) * 0.6 + ny * w * 0.55),
                   (cx + ca * L2, cy + sa * L2), (cx + ca * (b + L2) * 0.6 - nx * w * 0.5, cy + sa * (b + L2) * 0.6 - ny * w * 0.5),
                   (cx + ca * b - nx * w * 0.35, cy + sa * b - ny * w * 0.35)]
            ds.append(smooth_closed(pts))
        d = " ".join(ds)
        if detail:
            out.append(form(u, d, (cx - r, cy - r, cx + r, cy + r), col, dk, petal[2], seed + ring, radial, n=r * r / 10, shade=None,
                            ink_w=max(0.8, r * 0.016), ink_col="#8A5210", ink_op=0.7, length=(r * 0.15, r * 0.45), width=(0.8, max(1.4, r * 0.03)),
                            tints=[petal[2], dk, col, "#FFF0B0"], sop=(0.2, 0.5), curve=0.1))
        else:
            out.append(f'<path d="{d}" fill="{col}"/>')
    dr = r * 0.4
    dd = blob(cx, cy, dr, dr, seed, 0.03, 16)
    out.append(form(u, dd, (cx - dr, cy - dr, cx + dr, cy + dr), disc[0], disc[1], disc[2], seed + 1,
                    lambda x, y: math.degrees(math.atan2(y - cy, x - cx)) + 90, n=dr * dr / 6 if detail else 4, shade=(dr * 0.15, dr * 0.18),
                    ink_w=max(0.8, r * 0.02) if detail else 0, ink_col="#2E1A0C", length=(dr * 0.1, dr * 0.3), width=(0.6, max(1, dr * 0.05))))
    if detail:
        g1, g2 = [], []
        for i in range(int(dr * 2.2)):
            rr = dr * 0.9 * math.sqrt(i / (dr * 2.2))
            a = i * 2.39996
            (g1 if i % 3 else g2).append(f"M{_n(cx + rr * math.cos(a))} {_n(cy + rr * math.sin(a))}h0")
        sw = max(1.4, dr * 0.09)
        out.append(f'<path d="{"".join(g1)}" stroke="#C8944A" stroke-width="{sw:.1f}" stroke-linecap="round" opacity="0.75"/>'
                   f'<path d="{"".join(g2)}" stroke="#1E0E06" stroke-width="{sw:.1f}" stroke-linecap="round" opacity="0.75"/>')
        out.append(f'<path d="{blob(cx - dr * 0.3, cy - dr * 0.35, dr * 0.28, dr * 0.18, seed + 2, 0.2, 10)}" fill="#C8944A" opacity="0.35"/>')
    out.append("</g>")
    return "".join(out)


def mini_sunflower(x, y, s, rnd, tilt=0.8):
    cols = ["#F2B826", "#E8A41E", "#F6C84A", "#EBAE2A"]
    ps = []
    n = 9
    for i in range(n):
        a = 2 * math.pi * i / n + rnd.uniform(-0.15, 0.15)
        px, py = x + math.cos(a) * s * 0.62, y + math.sin(a) * s * 0.62 * tilt
        ps.append(f'<ellipse cx="{_n(px)}" cy="{_n(py)}" rx="{_n(s * 0.42)}" ry="{_n(s * 0.2)}" transform="rotate({math.degrees(math.atan2(math.sin(a) * tilt, math.cos(a))):.0f} {_n(px)} {_n(py)})"/>')
    return (f'<g fill="{rnd.choice(cols)}">{"".join(ps)}</g><ellipse cx="{_n(x)}" cy="{_n(y)}" rx="{_n(s * 0.36)}" ry="{_n(s * 0.36 * tilt)}" fill="#5A3418"/>'
            f'<circle cx="{_n(x - s * 0.1)}" cy="{_n(y - s * 0.1)}" r="{_n(s * 0.12)}" fill="#8A5A2A" opacity="0.7"/>')


def sf_leaf(u, x, y, s, rot, seed):
    d = smooth_closed([(x, y), (x + s * 0.5, y - s * 0.32), (x + s, y - s * 0.12), (x + s * 1.18, y + s * 0.02), (x + s * 0.98, y + s * 0.12),
                       (x + s * 0.5, y + s * 0.3)])
    return (f'<g transform="rotate({rot} {x} {y})">' +
            form(u, d, (x, y - s * 0.35, x + s * 1.2, y + s * 0.32), "#6E8A3E", "#46602A", "#A8BC66", seed, -10, n=s * 1.4, shade=(0, s * 0.08),
                 ink_w=1.6, ink_col="#34461E", length=(s * 0.15, s * 0.4), width=(1, 2.4)) +
            f'<path d="M {x} {y} Q {_f(x + s * 0.55)} {_f(y - s * 0.05)} {_f(x + s * 1.1)} {_f(y + s * 0.02)}" stroke="#D2DC9A" stroke-width="1.6" fill="none" opacity="0.6"/></g>')


@design("sunflower-fields")
def sunflower_fields():
    u = Ids("sunflower-fields")
    sky = u("sky")
    o = [f'<defs>{lgrad(sky, [(0, "#E6DCC8"), (0.4, "#F6DCA8"), (0.75, "#F6C470"), (1, "#EEA44A")])}</defs><rect width="600" height="600" fill="url(#{sky})"/>']
    o.append(paper(u("pp"), "#F6DCA8", FLECK, 51, 1.0).replace('<rect width="600" height="600" fill="#F6DCA8"/>', ""))
    o.append(brush((-20, -20, 620, 330), ["#FFF4DE", "#F2C880", "#F8E2B8", "#E8B060"], 52, 180, -6, (60, 160), (5, 14), (0.08, 0.2), 0.1))
    o.append(glow(u, 300, 318, 260, "#FFF2C8", 0.85, 170))
    o.append(f'<path d="{blob(300, 316, 46, 46, 53, 0.02, 20)}" fill="#FFF6DC" opacity="0.95"/>')
    for cx_, cy_, w_ in ((104, 252, 80), (500, 236, 70), (190, 216, 50)):
        o.append(f'<path d="{blob(cx_, cy_, w_, w_ * 0.18, cx_, 0.2, 14)}" fill="#FFF0D0" opacity="0.6"/>'
                 f'<path d="{blob(cx_ + 6, cy_ + 5, w_ * 0.8, w_ * 0.1, cx_ + 1, 0.2, 12)}" fill="#E8A86A" opacity="0.35"/>')
    o.append(hill(u, [(-20, 318), (90, 300), (200, 314), (330, 304), (460, 296), (620, 312)], 400, "#C8A08A", "#A8848A", "#E6C4A8", 54, n=60,
                  length=(30, 80)))
    o.append(hill(u, [(-20, 332), (120, 322), (260, 330), (400, 320), (620, 330)], 400, "#8A8A4A", "#6A6A34", "#B0A862", 55, n=80))
    rnd = random.Random(56)
    o.append(dabs((-10, 324, 610, 334), ["#5E6A30", "#4A5626", "#7A7A3A"], 57, 120, (3, 7), (0.7, 1), 0.6))
    field = smooth_open([(-20, 340), (300, 336), (620, 340)]) + " L 620 620 L -20 620 Z"
    o.append(form(u, field, (-20, 336, 620, 620), "#7A8A3A", "#4A5A22", "#A8B05A", 58, -90, n=500, shade=None, ink_w=0, length=(8, 24), width=(1, 3)))
    # receding rows of heads: dabs far away, little painted heads closer, leaves between
    for row in range(10):
        t = row / 9
        y = 342 + 118 * t ** 1.5
        sz = 2.2 + 10 * t ** 1.4
        x = -10 + rnd.uniform(0, sz * 2)
        lv, hd = [], []
        while x < 610:
            yy = y + rnd.uniform(-3, 3) * (1 + t * 2)
            if rnd.random() < 0.85:
                if t < 0.35:
                    hd.append(f'<ellipse cx="{_n(x)}" cy="{_n(yy)}" rx="{_n(sz)}" ry="{_n(sz * 0.75)}" fill="{rnd.choice(["#F2B826", "#E8A41E", "#F6C84A"])}"/>')
                else:
                    lv.append(f'<path d="M{_n(x)} {_n(yy)}l0 {_n(sz * 2.6)}" stroke="#4A5A22" stroke-width="{_n(max(1, sz * 0.16))}"/>')
                    hd.append(mini_sunflower(x, yy, sz * 1.25, rnd, rnd.uniform(0.6, 0.95)))
            if t >= 0.35:
                lx = x + rnd.uniform(-sz, sz)
                lv.append(f'<ellipse cx="{_n(lx)}" cy="{_n(yy + sz * 1.6)}" rx="{_n(sz * 0.9)}" ry="{_n(sz * 0.4)}" transform="rotate({rnd.uniform(-30, 30):.0f} {_n(lx)} {_n(yy + sz * 1.6)})" '
                          f'fill="{rnd.choice(["#5E7A34", "#4A6228", "#7A9446"])}"/>')
            x += sz * 2.3 + rnd.uniform(0, sz * 1.4)
        o.append("".join(lv) + "".join(hd))
    o.append(glow(u, 300, 340, 300, "#FFE2A0", 0.35, 40))
    # foreground: stems, leaves, three big painted sunflowers
    for x0, y0, x1, y1 in ((150, 420, 140, 640), (460, 448, 470, 640), (80, 560, 70, 640)):
        o.append(ink(f"M {x0} {y0} Q {x0 - 10} {(y0 + y1) / 2} {x1} {y1}", "#4A6228", 9, x0, 1, 1) + ink(f"M {x0 + 2} {y0} Q {x0 - 6} {(y0 + y1) / 2} {x1 + 2} {y1}", "#8AA44E", 2.5, x0, 1, 0.8))
    o.append(sf_leaf(u, 146, 520, 92, -20, 60) + sf_leaf(u, 140, 560, 80, 200, 61) + sf_leaf(u, 466, 540, 84, -30, 62) + sf_leaf(u, 464, 580, 70, 195, 63))
    o.append(sunflower(u, 466, 438, 70, 64, 0.95, 12))
    o.append(sunflower(u, 150, 420, 84, 65, 1.0, -8))
    o.append(sunflower(u, 300, 522, 44, 66, 0.9, 4))
    # bees / birds
    o.append(ink("M 404 272 q 7 -6 14 0 q 7 -6 14 0 M 436 288 q 5 -4 10 0 q 5 -4 10 0 M 150 280 q 6 -5 12 0 q 6 -5 12 0", "#7A4A2A", 2, 67, 1, 0.8))
    t, _, w1 = btext(u, 300, 144, "SUNFLOWER", BEBAS, 128, "#4A2A14", ["#6A3E20", "#2E1A0C", "#7A4A28"], 68, max_w=460, ls=4, angle=-78,
                     shadow="#F6E2B8", soff=(0.02, 0.035))
    o.append(t)
    t, s2, w2 = btext(u, 300, 202, "FIELDS", BEBAS, 58, "#A8501A", ["#C8682A", "#8A3E12"], 69, max_w=200, ls=14, angle=-78)
    o.append(t)
    for sgn in (-1, 1):
        a = 300 + sgn * (w2 / 2 + 18)
        o.append(hand_rule(a, a + sgn * 70, 184, "#A8501A", 2.4, 70 + sgn))
        o.append(sunflower(u, a + sgn * 84, 184, 9, 71 + sgn, 1, 0, False))
    o.append(plain(300, 238, "GOLDEN HOUR · EARLY FALL", MONO, 18, "#6A3E20", 400, 3))
    o.append(finish(u, INK, 0.6))
    return "".join(o)



# ---------------------------------------------------------------- more painted pieces
def steam(x, y, h, seed, col="#FFFFFF", n=3, gap=16, w=4, op=0.65):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        sx = x + (i - (n - 1) / 2) * gap
        pts = [(sx, y), (sx - 6, y - h * 0.3), (sx + 6, y - h * 0.62), (sx - 2, y - h)]
        out.append(f'<path d="{wobble_line(pts, seed + i, 1.5)}" stroke="{col}" stroke-width="{w * rnd.uniform(0.8, 1.1):.1f}" fill="none" stroke-linecap="round" opacity="{op}"/>')
    return "".join(out)


def mug(u, cx, top, w, h, seed, glaze=("#F4EAD8", "#CDBB9C", "#FFFFFF"), band=None, side=1, drink="#7A4626"):
    out = [shadow(u, cx + 6, top + h + 2, w * 0.7, 7, 0.35)]
    hx = cx + side * w * 0.5
    handle = f"M {_f(hx - side * 3)} {_f(top + h * 0.22)} q {side * w * 0.42:.1f} {-h * 0.04:.1f} {side * w * 0.3:.1f} {h * 0.36:.1f} q {-side * w * 0.06:.1f} {h * 0.22:.1f} {-side * w * 0.3:.1f} {h * 0.2:.1f}"
    out.append(f'<path d="{handle}" stroke="{glaze[1]}" stroke-width="{w * 0.13:.1f}" fill="none" stroke-linecap="round"/>' + ink(handle, INK, 1.6, seed, 1, 0.6))
    d = smooth_closed([(cx - w / 2, top), (cx + w / 2, top), (cx + w * 0.48, top + h * 0.7), (cx + w * 0.38, top + h), (cx - w * 0.38, top + h), (cx - w * 0.48, top + h * 0.7)])
    extra = ""
    if band:
        extra = f'<rect x="{_f(cx - w)}" y="{_f(top + h * 0.42)}" width="{_f(2 * w)}" height="{_f(h * 0.2)}" fill="{band}" opacity="0.9"/>'
    out.append(form(u, d, (cx - w / 2, top, cx + w / 2, top + h), glaze[0], glaze[1], glaze[2], seed, -90, n=w * h / 30, shade=(w * 0.14, 0),
                    shade_op=0.5, ink_w=1.8, extra_in=extra))
    out.append(f'<ellipse cx="{cx}" cy="{_f(top + 1)}" rx="{_f(w / 2 - 1)}" ry="{_f(w * 0.12)}" fill="{glaze[1]}"/>'
               f'<ellipse cx="{cx}" cy="{_f(top + 2.5)}" rx="{_f(w / 2 - 5)}" ry="{_f(w * 0.09)}" fill="{drink}"/>'
               f'<ellipse cx="{cx}" cy="{_f(top + 1)}" rx="{_f(w / 2 - 1)}" ry="{_f(w * 0.12)}" fill="none" stroke="{INK}" stroke-width="1.6" opacity="0.7"/>')
    return "".join(out)


def board(u, x0, y0, x1, y1, seed, col, dark, light, point=None, inkc=INK):
    """Painted wooden plank; point='r' or 'l' makes an arrow end."""
    h = y1 - y0
    if point == "r":
        pts = [(x0, y0), (x1 - h * 0.45, y0), (x1, (y0 + y1) / 2), (x1 - h * 0.45, y1), (x0, y1)]
    elif point == "l":
        pts = [(x0 + h * 0.45, y0), (x1, y0), (x1, y1), (x0 + h * 0.45, y1), (x0, (y0 + y1) / 2)]
    else:
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    rnd = random.Random(seed)
    pts = [(x + rnd.uniform(-1.5, 1.5), y + rnd.uniform(-1.5, 1.5)) for x, y in pts]
    d = "M " + " L ".join(f"{_f(x)} {_f(y)}" for x, y in pts) + " Z"
    grain_ = "".join(f'<path d="{wobble_line([(x0, y0 + h * t), ((x0 + x1) / 2, y0 + h * t + rnd.uniform(-3, 3)), (x1, y0 + h * t)], seed + k, 1)}" '
                     f'stroke="{dark}" stroke-width="1.2" fill="none" opacity="0.35"/>' for k, t in enumerate((0.22, 0.5, 0.78)))
    knot = f'<ellipse cx="{_f(rnd.uniform(x0 + 30, x1 - 30))}" cy="{_f(y0 + h * 0.6)}" rx="6" ry="3" fill="none" stroke="{dark}" stroke-width="1.2" opacity="0.5"/>'
    return (shadow(u, (x0 + x1) / 2 + 6, y1 + 4, (x1 - x0) * 0.5, 6, 0.25) +
            form(u, d, (x0, y0, x1, y1), col, dark, light, seed, -2, n=(x1 - x0) * h / 50, shade=(0, h * 0.14), shade_op=0.5,
                 length=(20, 60), width=(1, 3), ink_w=2.2, ink_col=inkc, extra_in=grain_ + knot))


def nail(x, y):
    return f'<circle cx="{x}" cy="{y}" r="3" fill="#5A4A3A"/><circle cx="{x - 0.8}" cy="{y - 0.8}" r="1.1" fill="#D8C8B0"/>'


def hay(u, x, y, w, h, seed):
    d = smooth_closed([(x, y + 4), (x + w * 0.5, y - 2), (x + w, y + 4), (x + w + 3, y + h * 0.5), (x + w, y + h), (x + w * 0.5, y + h + 2), (x, y + h), (x - 3, y + h * 0.5)])
    rnd = random.Random(seed)
    twine = "".join(f'<path d="M {_f(x + w * t)} {y - 2} q 3 {h / 2:.1f} 0 {h + 4:.1f}" stroke="#7A4E22" stroke-width="3" fill="none"/>' for t in (0.28, 0.72))
    out = [shadow(u, x + w / 2 + 6, y + h + 3, w * 0.6, 7, 0.3),
           form(u, d, (x, y, x + w, y + h), "#E2B65A", "#A8742A", "#F6DA8A", seed, -4, n=w * h / 18, shade=(0, h * 0.18), shade_op=0.5,
                tints=["#C9933A", "#F6DA8A", "#A8742A", "#FFF0B8"], length=(8, 22), width=(0.6, 1.6), sop=(0.4, 0.85), ink_w=1.8, ink_col="#7A4E22",
                extra_in=twine)]
    tufts = "".join(f"M{_n(x + rnd.uniform(0, w))} {_n(y + rnd.choice([1, h - 1]))}l{_n(rnd.uniform(-7, 7))} {_n(rnd.uniform(-6, 6))}" for _ in range(28))
    out.append(f'<path d="{tufts}" stroke="#D9A847" stroke-width="1.3" stroke-linecap="round"/>')
    return "".join(out)


def wheat(u, x0, y0, x1, y1, seed, n=8, col=("#E9BE5E", "#B8862E", "#F8DC8E")):
    """A wheat stalk from (x0, y0) base to (x1, y1) tip, grains painted along the top third."""
    out = [ink(f"M {x0} {y0} Q {_f((x0 + x1) / 2 + 4)} {_f((y0 + y1) / 2)} {x1} {y1}", "#B8903E", 2.4, seed, 1, 1)]
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    for i in range(n):
        t = 0.62 + 0.38 * i / n
        px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        for sd in (-1, 1):
            a = math.radians(ang + sd * 28)
            gx, gy = px + math.cos(a) * 6, py + math.sin(a) * 6
            out.append(f'<ellipse cx="{_f(gx)}" cy="{_f(gy)}" rx="7" ry="3.4" transform="rotate({ang + sd * 28:.0f} {_f(gx)} {_f(gy)})" fill="{col[i % 2]}" stroke="#8A5E1E" stroke-width="0.9"/>')
            out.append(f'<path d="M {_f(gx)} {_f(gy)} l {_f(math.cos(a) * 14)} {_f(math.sin(a) * 14)}" stroke="#D8B060" stroke-width="0.9" opacity="0.8"/>')
    out.append(f'<ellipse cx="{x1}" cy="{y1}" rx="6.5" ry="3.2" transform="rotate({ang:.0f} {x1} {y1})" fill="{col[2]}" stroke="#8A5E1E" stroke-width="0.9"/>')
    return "".join(out)


def knit_vs(box, color, dx=9, dy=7, op=0.5, sw=1.4):
    x0, y0, x1, y1 = box
    d = []
    y = y0
    while y < y1:
        x = x0
        while x < x1:
            d.append(f"M{_n(x)} {_n(y)}l{_n(dx / 2)} {_n(dy * 0.8)}l{_n(dx / 2)} {_n(-dy * 0.8)}")
            x += dx
        y += dy
    return f'<path d="{"".join(d)}" stroke="{color}" stroke-width="{sw}" fill="none" stroke-linejoin="round" opacity="{op}"/>'


# ================================================================ rainy days & good books
@design("rainy-days-good-books")
def rainy_days():
    u = Ids("rainy-days-good-books")
    o = [bg(u, "#EEE2CC", ["#E4D4B8", "#F6ECDC", "#DCC8A6"], 81, angle=-80, length=(80, 200))]
    for x in range(-10, 620, 36):   # painted wallpaper stripes
        o.append(f'<path d="{wobble_line([(x, -10), (x + 2, 300), (x, 610)], x, 1.5)}" stroke="#D8C2A0" stroke-width="10" fill="none" opacity="0.35"/>')
    o.append(glow(u, 300, 220, 230, "#FFF2D8", 0.5))
    # window: arched frame, rainy world outside
    outer = "M 150 324 L 150 184 A 150 112 0 0 1 450 184 L 450 324 Z"
    inner = "M 166 318 L 166 186 A 134 96 0 0 1 434 186 L 434 318 Z"
    cid = u("win")
    sky = u("sky")
    o.append(form(u, outer, (150, 72, 450, 324), "#E8DCC4", "#B8A47E", "#FFF8EA", 82, -90, n=120, shade=(-6, 0), ink_w=2.4))
    o.append(f'<defs>{lgrad(sky, [(0, "#7E929C"), (0.55, "#A8B4B2"), (1, "#C8C2AE")])}<clipPath id="{cid}"><path d="{inner}"/></clipPath></defs>')
    o.append(f'<g clip-path="url(#{cid})"><rect x="160" y="80" width="280" height="250" fill="url(#{sky})"/>')
    o.append(brush((160, 80, 440, 240), ["#6E828C", "#98A8AE", "#B8C2C2"], 83, 50, -10, (30, 80), (6, 14), (0.15, 0.35), 0.1))
    rnd = random.Random(84)
    o.append(f'<path d="{smooth_open([(160, 250), (230, 236), (310, 246), (380, 232), (440, 244)])} L 440 330 L 160 330 Z" fill="#8E9A98" opacity="0.6"/>')
    tcols = ["#C8703A", "#B8481E", "#D89A4A", "#A86A3A", "#9A8A3A", "#D2602A"]
    for i, x in enumerate(range(166, 450, 30)):
        ty = 270 + rnd.uniform(-8, 6)
        rr = rnd.uniform(15, 21)
        o.append(f'<path d="M {x} {_f(ty + rr * 0.6)} l 0 {_f(26)}" stroke="#5A4A44" stroke-width="3" opacity="0.6"/>')
        o.append(form(u, blob(x, ty, rr, rr * 1.15, 300 + i, 0.1, 12), (x - rr, ty - rr * 1.2, x + rr, ty + rr * 1.2), tcols[i % len(tcols)], "#7A3A1A",
                      "#F2C27A", 310 + i, -60, n=14, shade=(4, 4), shade_op=0.4, ink_w=0, sop=(0.2, 0.45)))
    o.append(brush((160, 262, 440, 300), ["#C8D2D4", "#E6ECEC"], 86, 20, -2, (40, 100), (4, 9), (0.25, 0.45), 0.1))
    o.append(f'<path d="M 160 298 Q 300 288 440 300 L 440 330 L 160 330 Z" fill="#6E7E5E" opacity="0.75"/>')
    rain = "".join(f"M{_n(x)} {_n(y)}l{_n(-4)} {_n(L)}" for x, y, L in ((rnd.uniform(160, 450), rnd.uniform(70, 320), rnd.uniform(10, 24)) for _ in range(120)))
    o.append(f'<path d="{rain}" stroke="#EEF2F2" stroke-width="1.5" stroke-linecap="round" opacity="0.55"/>')
    drops = []
    for _ in range(26):
        x, y, r = rnd.uniform(172, 430), rnd.uniform(110, 300), rnd.uniform(2.4, 4.6)
        drops.append(f'<path d="M {_f(x)} {_f(y - r * 1.6)} Q {_f(x + r)} {_f(y - r * 0.2)} {_f(x)} {_f(y + r)} Q {_f(x - r)} {_f(y - r * 0.2)} {_f(x)} {_f(y - r * 1.6)} Z" fill="#DCE6E8" opacity="0.7"/>'
                     f'<path d="M {_f(x)} {_f(y + r)} q {_f(r * 0.9)} {_f(-r * 0.2)} {_f(r * 0.6)} {_f(-r * 1.2)}" stroke="#5E727C" stroke-width="1" fill="none" opacity="0.6"/>'
                     f'<circle cx="{_f(x - r * 0.3)}" cy="{_f(y - r * 0.2)}" r="{_f(r * 0.3)}" fill="#FFFFFF" opacity="0.9"/>')
        if rnd.random() < 0.35:
            drops.append(f'<path d="M {_f(x)} {_f(y + r)} q 1 18 -1 {rnd.uniform(20, 46):.0f}" stroke="#DCE6E8" stroke-width="1.6" fill="none" opacity="0.5"/>')
    o.append("".join(drops))
    o.append("</g>")
    for d in ("M 297 90 L 297 318 L 303 318 L 303 90 Z", "M 166 214 L 434 214 L 434 220 L 166 220 Z"):
        o.append(form(u, d, (166, 90, 434, 318), "#E8DCC4", "#B8A47E", "#FFF8EA", 86, -90, n=20, shade=None, ink_w=1.6))
    # an autumn vine draped over the arch, trailing down the left side
    vine = []
    for k in range(0, 41):
        a = math.radians(184 + k * 172 / 40)
        vine.append((300 + 162 * math.cos(a), 186 + 124 * math.sin(a) + 6 * math.sin(k * 0.9)))
    trail = [(140, 196), (134, 236), (140, 272), (132, 304)]
    o.append(ink(smooth_open(vine), "#6A5A2A", 2.6, 87, 2, 0.9) + ink(smooth_open([vine[0]] + trail), "#6A5A2A", 2.2, 88, 1, 0.9))
    specs = []
    for k, (x, y) in enumerate(vine[::2] + trail[1:]):
        specs.append((rnd.choice(["maple", "elm", "maple", "birch"]), x + rnd.uniform(-4, 4), y + rnd.uniform(-2, 8), rnd.uniform(10, 14),
                      rnd.uniform(140, 220), LEAF_PALS[k % len(LEAF_PALS)]))
    o.append(scatter_leaves(u, specs, 89))
    # a furled umbrella leaning by the window, dripping
    ug = [f'<g transform="rotate(10 490 260)">']
    ug.append(ink("M 490 196 L 490 168 Q 490 150 474 150 Q 460 150 460 164", "#4A2A14", 7, 90, 1, 1) +
              ink("M 490 196 L 490 168 Q 490 150 474 150 Q 460 150 460 164", "#B8844A", 3, 91, 1, 0.9))
    can = smooth_closed([(490, 192), (506, 214), (512, 252), (502, 300), (492, 334), (488, 334), (478, 300), (468, 252), (474, 214)])
    folds = "".join(f'<path d="{wobble_line([(490, 194), (490 + dx * 0.6, 260), (490, 332)], int(dx) + 50, 0.6)}" stroke="#1E2E3A" stroke-width="1.6" fill="none" opacity="0.5"/>' for dx in (-14, -5, 6, 14))
    ug.append(form(u, can, (468, 190, 512, 336), "#3E5566", "#22323E", "#6E8894", 92, -90, n=60, shade=(8, 0), shade_op=0.5, hi=(480, 240, 4, 26), hi_op=0.5,
                   ink_w=2, ink_col="#1A2630", extra_in=folds +
                   '<path d="M 466 262 Q 490 270 514 262 L 514 272 Q 490 280 466 272 Z" fill="#C2702E"/><circle cx="502" cy="270" r="2.4" fill="#F2D27A"/>'))
    ug.append('<path d="M 490 334 L 490 346" stroke="#4A2A14" stroke-width="3" stroke-linecap="round"/></g>')
    o.append("".join(ug))
    # sill with books, mug, pumpkin
    o.append(board(u, 118, 318, 482, 340, 91, "#B8844A", "#7A5228", "#DCAC6E"))
    books = [(150, 290, 300, 318, "#A8402A", "#6E2014", "#D2684A"), (162, 266, 288, 290, "#5E7A5A", "#3A5238", "#88A47E"),
             (156, 246, 276, 266, "#D9A23B", "#A8701E", "#F2C86A")]
    for i, (x0, y0, x1, y1, c, dk, lt) in enumerate(books):
        d = smooth_closed([(x0, y0 + 2), (x1 - 2, y0), (x1, y1 - 2), (x0 + 2, y1)]) if False else f"M {x0} {y0 + 2} Q {x0} {y0} {x0 + 4} {y0} L {x1 - 4} {y0} Q {x1} {y0} {x1} {y0 + 3} L {x1} {y1 - 2} Q {x1} {y1} {x1 - 4} {y1} L {x0 + 4} {y1} Q {x0} {y1} {x0} {y1 - 3} Z"
        pages = f'<rect x="{x1 - 14}" y="{y0 + 3}" width="12" height="{y1 - y0 - 6}" fill="#F6EEDC"/><path d="M {x1 - 13} {y0 + 7} l 10 0 M {x1 - 13} {y0 + 11} l 10 0 M {x1 - 13} {y0 + 15} l 10 0" stroke="#C8B89A" stroke-width="0.8"/>'
        bands = f'<rect x="{x0 + 18}" y="{y0}" width="5" height="{y1 - y0}" fill="#F2D27A" opacity="0.85"/><rect x="{x0 + 28}" y="{y0}" width="2" height="{y1 - y0}" fill="#F2D27A" opacity="0.85"/>'
        o.append(form(u, d, (x0, y0, x1, y1), c, dk, lt, 92 + i, 0, n=(x1 - x0) * (y1 - y0) / 30, shade=(0, 4), ink_w=1.8, extra_in=pages + bands))
    o.append(mug(u, 214, 214, 48, 32, 95, band="#A8402A"))
    o.append(steam(214, 204, 46, 96, "#FFFFFF", 2, 14, 3.4, 0.8))
    o.append(pumpkin(u, 386, 298, 84, 52, 97, PK_OR, leaf_on=True, curl=True))
    o.append(form(u, "M 334 318 L 336 290 L 350 290 L 352 318 Z", (334, 284, 352, 318), "#F4EAD8", "#C8B494", "#FFFFFF", 98, -90, n=8, shade=(3, 0), ink_w=1.4))
    o.append(glow(u, 343, 270, 40, "#FFD890", 0.7) + f'<path d="{blob(343, 280, 4, 8, 99, 0.1, 8)}" fill="#F6B840"/><path d="{blob(343, 282, 2, 4, 99, 0.1, 8)}" fill="#FFF4C8"/>'
             + '<path d="M 343 290 l 0 -5" stroke="#3A2418" stroke-width="1.4"/>')
    t, _, _ = btext(u, 300, 438, "rainy days", SERIF_IT, 104, "#3E5566", ["#56707E", "#2A3E4C", "#6E8894"], 100, max_w=430, angle=-35,
                    shadow="#D8C4A2", soff=(0.02, 0.035))
    o.append(t)
    t, s2, w2 = btext(u, 300, 500, "& GOOD BOOKS", JOS, 36, "#B8481E", ["#D2602A", "#8E3A12"], 101, max_w=300, ls=8, angle=-80)
    o.append(t)
    for sgn in (-1, 1):
        a = 300 + sgn * (w2 / 2 + 14)
        o.append(hand_rule(a, a + sgn * 44, 487, "#B8481E", 2.2, 102 + sgn))
    o.append(scatter_leaves(u, [("maple", 92, 470, 16, -20, L_ORANGE), ("elm", 510, 462, 14, 50, L_GOLD), ("oak", 530, 530, 13, 20, L_RED)], 103))
    o.append(finish(u))
    return "".join(o)


# ================================================================ give thanks
@design("give-thanks")
def give_thanks():
    u = Ids("give-thanks")
    o = [bg(u, "#F4E6D0", ["#ECD6B6", "#FAF0E0", "#E6CCA8"], 111, angle=-25)]
    o.append(glow(u, 300, 260, 250, "#F6BE7A", 0.45))
    cx, cy = 300, 286
    # fanned tail feathers, three layers
    layers = [(170, 34, ["#A8401E", "#8E3A1A", "#B8501E"], ("#F2D49A", "#3A2418")), (140, 32, ["#C8802E", "#D9A23B", "#B8702A"], ("#F6E6C8", "#5A3420")),
              (112, 30, ["#7A4A28", "#8A5A30", "#6E7A3A"], ("#E8B860", "#3A2418"))]
    rnd = random.Random(112)
    for li, (L, wd, cols, (tip, band)) in enumerate(layers):
        n = 13 - li * 2
        for i in range(n):
            a = math.radians(-172 + 164 * i / (n - 1) + rnd.uniform(-2, 2))
            ca, sa = math.cos(a), math.sin(a)
            nx, ny = -sa, ca
            tx, ty = cx + ca * L, cy + sa * L
            pts = [(cx + nx * 6, cy + ny * 6), (cx + ca * L * 0.55 + nx * wd * 0.55, cy + sa * L * 0.55 + ny * wd * 0.55),
                   (cx + ca * L * 0.92 + nx * wd * 0.42, cy + sa * L * 0.92 + ny * wd * 0.42), (tx, ty),
                   (cx + ca * L * 0.92 - nx * wd * 0.42, cy + sa * L * 0.92 - ny * wd * 0.42),
                   (cx + ca * L * 0.55 - nx * wd * 0.55, cy + sa * L * 0.55 - ny * wd * 0.55), (cx - nx * 6, cy - ny * 6)]
            d = smooth_closed(pts)
            c = cols[i % len(cols)]
            bx, by = cx + ca * L * 0.8, cy + sa * L * 0.8
            extra = (f'<circle cx="{_f(tx)}" cy="{_f(ty)}" r="{_f(L * 0.13)}" fill="{tip}"/>'
                     f'<path d="M {_f(bx + nx * wd)} {_f(by + ny * wd)} L {_f(bx - nx * wd)} {_f(by - ny * wd)}" stroke="{band}" stroke-width="{wd * 0.2:.1f}" opacity="0.8"/>'
                     f'<path d="M {_f(cx + ca * L * 0.6 + nx * wd)} {_f(cy + sa * L * 0.6 + ny * wd)} L {_f(cx + ca * L * 0.6 - nx * wd)} {_f(cy + sa * L * 0.6 - ny * wd)}" stroke="{tip}" stroke-width="{wd * 0.12:.1f}" opacity="0.7"/>')
            o.append(form(u, d, (min(cx, tx) - wd, min(cy, ty) - wd, max(cx, tx) + wd, max(cy, ty) + wd), c, "#5A2A12", "#F2B870", 113 + li * 20 + i,
                          math.degrees(a), n=L * wd / 30, shade=(nx * 3, ny * 3), shade_op=0.35, ink_w=1.8, ink_col="#4A2412",
                          length=(L * 0.1, L * 0.3), width=(0.8, 2.2), extra_in=extra))
            o.append(f'<path d="M {_f(cx)} {_f(cy)} L {_f(cx + ca * L * 0.86)} {_f(cy + sa * L * 0.86)}" stroke="#3A1E0E" stroke-width="1.4" opacity="0.6"/>')
    # wheat and pumpkins at the feet
    for sgn in (-1, 1):
        for k, (dx, dy) in enumerate(((60, -150), (90, -130), (40, -160))):
            o.append(wheat(u, 300 + sgn * 140, 400, 300 + sgn * (140 + dx * 0.6 - 20), 400 + dy, 120 + k + sgn))
    # body
    body = blob(cx, cy + 22, 82, 86, 130, 0.04, 22)
    o.append(form(u, body, (cx - 84, cy - 66, cx + 84, cy + 110), "#7A4A28", "#4A2A14", "#A8784A", 131, lambda x, y: math.degrees(math.atan2(y - cy, x - cx)) + 90,
                  n=260, shade=(16, 10), shade_op=0.55, hi=(cx - 30, cy - 10, 26, 20), ink_w=2.4, length=(8, 22), width=(1, 3)))
    sc = []
    for row in range(5):
        for k in range(-3, 4):
            x = cx + k * 20 + (10 if row % 2 else 0)
            y = cy + 10 + row * 18
            if (x - cx) ** 2 / 70 ** 2 + (y - cy - 22) ** 2 / 76 ** 2 < 0.8:
                sc.append(f"M{_n(x - 9)} {_n(y)}q9 12 18 0")
    o.append(f'<path d="{"".join(sc)}" stroke="#C8945A" stroke-width="2.2" fill="none" opacity="0.6"/>')
    # wings
    for sgn in (-1, 1):
        w_ = smooth_closed([(cx + sgn * 40, cy - 6), (cx + sgn * 82, cy + 30), (cx + sgn * 74, cy + 82), (cx + sgn * 56, cy + 70), (cx + sgn * 50, cy + 40)])
        o.append(form(u, w_, (cx + min(sgn * 40, sgn * 82), cy - 6, cx + max(sgn * 40, sgn * 82), cy + 84), "#8E5A30", "#5A3418", "#B88A54", 132 + sgn, -70 * sgn,
                      n=40, shade=(sgn * 4, 4), ink_w=1.8, extra_in=f'<path d="M {cx + sgn * 56} {cy + 30} l {sgn * 12} 30 M {cx + sgn * 64} {cy + 26} l {sgn * 10} 30" stroke="#E8B860" stroke-width="2" opacity="0.6"/>'))
    # neck & head
    neck = smooth_closed([(cx - 18, cy - 30), (cx - 22, cy - 70), (cx - 26, cy - 100), (cx, cy - 122), (cx + 26, cy - 100), (cx + 20, cy - 66), (cx + 18, cy - 30)])
    o.append(form(u, neck, (cx - 28, cy - 124, cx + 28, cy - 28), "#8E5A30", "#5A3418", "#B88A54", 134, -90, n=40, shade=(6, 0), ink_w=0))
    head = blob(cx, cy - 104, 32, 32, 135, 0.05, 16)
    o.append(form(u, head, (cx - 32, cy - 136, cx + 32, cy - 72), "#C8A07A", "#9A7454", "#EAD0B0", 136, -90, n=50, shade=(6, 6), shade_op=0.4,
                  ink_w=2.2))
    o.append(f'<path d="{blob(cx + 5, cy - 80, 7, 13, 137, 0.12, 12, rot=-8)}" fill="#C8302A"/>'
             + ink(blob(cx + 5, cy - 80, 7, 13, 137, 0.12, 12, rot=-8), "#6A1410", 1.6, 138, 1, 0.8)
             + f'<path d="{blob(cx + 3, cy - 84, 2.2, 5, 139, 0.1, 8)}" fill="#F08070" opacity="0.7"/>')
    o.append(form(u, f"M {cx - 8} {cy - 100} L {cx + 12} {cy - 98} L {cx + 2} {cy - 84} Z", (cx - 8, cy - 100, cx + 12, cy - 84), "#F2B03A", "#C8801E", "#FFD878",
                  140, 0, n=6, shade=(0, 2), ink_w=1.4))
    for sgn in (-1, 1):
        ex = cx + sgn * 14
        o.append(f'<circle cx="{ex}" cy="{cy - 112}" r="7" fill="#FFFFFF"/><circle cx="{ex + 1}" cy="{cy - 111}" r="4.2" fill="#2A140A"/>'
                 f'<circle cx="{ex - 0.5}" cy="{cy - 113}" r="1.5" fill="#FFFFFF"/>' + ink(f"M {ex - 7} {cy - 112} a 7 7 0 0 1 14 0", INK, 1.5, 141, 1, 0.8))
        o.append(f'<ellipse cx="{cx + sgn * 22}" cy="{cy - 96}" rx="6" ry="4" fill="#E8705A" opacity="0.45"/>')
    o.append(ink(f"M {cx - 26} 404 l -2 14 m 2 -14 l 8 12 m -8 -12 l -12 8 M {cx + 26} 404 l 2 14 m -2 -14 l -8 12 m 8 -12 l 12 8", "#C8701E", 3.6, 142, 1, 1))
    o.append(shadow(u, 300, 420, 120, 10, 0.25))
    o.append(pumpkin(u, 168, 396, 78, 52, 143, PK_OR, leaf_on=False, curl=True))
    o.append(pumpkin(u, 434, 400, 66, 44, 144, PK_CREAM, leaf_on=False, curl=False, inkc="#7A6448"))
    o.append(scatter_leaves(u, [("maple", 102, 404, 18, -20, L_RED), ("oak", 500, 404, 16, 60, L_GOLD), ("maple", 92, 140, 15, 20, L_ORANGE),
                                ("elm", 512, 168, 14, -40, L_CRAN)], 145))
    t, _, _ = btext(u, 300, 484, "give thanks", SERIF_IT, 100, "#5A2A18", ["#7A3A20", "#3E1A0E", "#8E4A2A"], 146, max_w=440, angle=-35,
                    shadow="#E8C49A", soff=(0.02, 0.035))
    o.append(t)
    o.append(ruled(u, 530, "HAPPY THANKSGIVING", MONO, 18, "#8E3A12", 147, ls=4, line_w=34, gap=12))
    o.append(finish(u))
    return "".join(o)


# ================================================================ stick with me
@design("stick-with-me")
def stick_with_me():
    u = Ids("stick-with-me")
    o = [bg(u, "#2E4A50", ["#3A5A60", "#24393E", "#46666A", "#1E3236"], 151, fleck="#E8DCC0", angle=-30)]
    o.append(glow(u, 300, 300, 260, "#E8A05A", 0.4))
    o.append(vignette(u, "#0E1C20", 0.55))
    # parchment square
    pap = smooth_closed(jitter([(150, 400), (300, 376), (462, 392), (470, 446), (310, 470), (136, 452)], 152, 3))
    o.append(form(u, pap, (136, 376, 470, 470), "#F2E6CE", "#C8B28A", "#FFFAF0", 153, -10, n=120, shade=(6, 6), shade_op=0.3, ink_w=1.6,
                  ink_col="#8A7050", length=(20, 60)))
    o.append(shadow(u, 304, 432, 120, 18, 0.4))
    # caramel puddle
    pud = blob(304, 428, 116, 22, 154, 0.12, 20)
    o.append(form(u, pud, (188, 406, 420, 450), "#C8802E", "#8A4A16", "#F2B860", 155, 0, n=60, shade=(0, 4), ink_w=1.8, ink_col="#5A2A0A"))
    # stick
    o.append(form(u, "M 293 210 L 296 92 Q 302 86 308 92 L 309 210 Z", (292, 86, 310, 210), "#E8D2A8", "#B89A6A", "#FFF4DC", 156, -90, n=30, shade=(4, 0),
                  ink_w=1.8, length=(10, 40), width=(0.6, 1.6)))
    # the apple and its caramel coat
    cx, cy, r = 300, 300, 112
    o.append(apple(u, cx, cy, r, 157, ("#C8302A", "#7A1414", "#F07050"), leaf_on=False, inkc="#4A1008"))
    rnd = random.Random(158)
    base_y = cy + 6
    pts = [(cx - r - 12, base_y - 30)]
    x = cx - r
    while x < cx + r:
        edge = math.sqrt(max(0, 1 - ((x - cx) / r) ** 2))
        if rnd.random() < 0.6:
            w = rnd.uniform(14, 22)
            depth = rnd.uniform(22, 64) * (0.4 + 0.6 * edge)
            yb = base_y - 22 * (1 - edge) + rnd.uniform(-4, 4)
            pts += [(x, yb), (x + w * 0.12, yb + depth * 0.55), (x + w / 2, yb + depth), (x + w * 0.88, yb + depth * 0.55), (x + w, yb)]
            x += w + rnd.uniform(4, 10)
        else:
            x += rnd.uniform(10, 18)
            pts.append((x, base_y - 22 * (1 - edge) + rnd.uniform(-5, 5)))
    pts.append((cx + r + 12, base_y - 30))
    car = smooth_open(pts) + f" L {cx + r + 12} {cy - r - 30} L {cx - r - 12} {cy - r - 30} Z"
    acid = u("ac")
    apts = []
    for i in range(24):
        a = 2 * math.pi * i / 24
        k = 1 - 0.13 * max(0, math.cos(a + math.pi / 2)) ** 6 - 0.04 * math.sin(2 * a) ** 2
        apts.append((cx + (r + 3) * 1.02 * math.cos(a) * k, cy + (r + 3) * 0.95 * math.sin(a) * k + (0.06 * r if math.sin(a) > 0 else 0)))
    o.append(f'<path d="{car}" fill="#3A0A04" opacity="0.25" transform="translate(3 6)" clip-path="url(#{acid})"/>')
    o.append(f'<clipPath id="{acid}"><path d="{smooth_closed(apts)}"/></clipPath><g clip-path="url(#{acid})">')
    nuts = dabs((cx - r, base_y - 46, cx + r, base_y + 10), ["#F2DCA8", "#D8B070", "#FFF0C8", "#B8884A"], 159, 110, (2.2, 4.6), (0.85, 1), 0.5)
    o.append(form(u, car, (cx - r - 10, cy - r - 30, cx + r + 10, base_y + 70), "#C8802E", "#7A3E10", "#F6C878", 160,
                  lambda x, y: math.degrees(math.atan2(y - cy, x - cx)) + 90, n=380, shade=(26, 16), shade_op=0.6, hi=(cx - 46, cy - 62, 34, 18),
                  hi_op=0.55, ink_w=2.2, ink_col="#4A2208", length=(10, 40), width=(1.2, 3.6), curve=0.4, extra_in=nuts))
    o.append("</g>")
    o.append(f'<path d="M {cx - 84} {cy - 40} Q {cx - 96} {cy - 6} {cx - 86} {cy + 26}" stroke="#FFF2D0" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.7"/>')
    o.append(f'<path d="M {cx - 74} {cy + 66} q 10 14 26 20" stroke="#FFD8C8" stroke-width="4" fill="none" stroke-linecap="round" opacity="0.6"/>')
    # gingham bow on the stick
    gid, gcl = u("gh"), u("gc")
    o.append(f'<defs><pattern id="{gid}" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(20)"><rect width="10" height="10" fill="#FBF3E4"/>'
             f'<rect width="5" height="10" fill="#C8302A" opacity="0.55"/><rect width="10" height="5" fill="#C8302A" opacity="0.55"/></pattern></defs>')
    bow = [smooth_closed([(302, 176), (258, 150), (250, 178), (262, 196)]), smooth_closed([(304, 176), (348, 150), (356, 178), (344, 196)]),
           smooth_closed([(298, 182), (276, 222), (288, 226), (302, 190)]), smooth_closed([(306, 182), (330, 220), (318, 226), (304, 190)])]
    for i, d in enumerate(bow):
        o.append(f'<path d="{d}" fill="url(#{gid})"/>' + f'<path d="{d}" fill="#7A1414" opacity="0.15" transform="translate(2 3)"/>' + ink(d, "#6A1410", 1.8, 161 + i, 2, 0.85))
    o.append(f'<path d="{blob(303, 180, 10, 9, 165, 0.1, 10)}" fill="url(#{gid})"/>' + ink(blob(303, 180, 10, 9, 165, 0.1, 10), "#6A1410", 1.8, 166, 2, 0.85))
    for x, y, s in ((120, 150, 7), (488, 132, 6), (500, 300, 5), (98, 330, 5), (452, 210, 4)):
        o.append(sparkle(x, y, s, "#F6D9A8", 0.75))
    o.append(scatter_leaves(u, [("maple", 104, 236, 20, -25, L_ORANGE), ("oak", 496, 250, 18, 50, L_GOLD), ("elm", 490, 400, 14, 70, L_RED)], 167))
    sa, sb = 100, 82
    wa, wb = measure("stick", SERIF_IT, sa), measure("WITH ME", BEBAS, sb, 6)
    k = min(1, 460 / (wa + 22 + wb))
    sa, sb = int(sa * k), int(sb * k)
    wa, wb = measure("stick", SERIF_IT, sa), measure("WITH ME", BEBAS, sb, 6)
    x0 = 300 - (wa + 22 + wb) / 2
    t, _, _ = btext(u, x0, 522, "stick", SERIF_IT, sa, "#FBEBD2", ["#FFF6E6", "#E8D2B4"], 168, max_w=480, anchor="start", angle=-35,
                    shadow="#0E2024", soff=(0.025, 0.04))
    o.append(t)
    t, _, _ = btext(u, x0 + wa + 22, 522, "WITH ME", BEBAS, sb, "#F2B94A", ["#F6CE6A", "#C8841E", "#FFE08A"], 169, max_w=480, ls=6, anchor="start",
                    angle=-78, shadow="#0E2024", soff=(0.025, 0.04))
    o.append(t)
    o.append(finish(u, "#E8DCC0", 0.6))
    return "".join(o)


# ================================================================ sweater weather
def folded_sweater(u, cx, top, w, h, seed, base, dark, light, kind, collar=False):
    x0, x1 = cx - w / 2, cx + w / 2
    d = smooth_closed(jitter([(x0 + 10, top), (cx, top - 3), (x1 - 10, top), (x1 + 2, top + h * 0.3), (x1, top + h - 6), (cx, top + h + 2), (x0, top + h - 6),
                              (x0 - 2, top + h * 0.3)], seed, 1.2))
    extra = []
    if kind == "cable":
        extra.append(knit_vs((x0, top + 4, x1, top + h), dark, 9, 7, 0.45))
        for k in (-0.28, 0, 0.28):
            xx = cx + k * w
            ropes = "".join(f"M{_n(xx - 8)} {_n(top + 6 + j * 14)}q8 7 16 14M{_n(xx + 8)} {_n(top + 6 + j * 14)}q-8 7 -16 14" for j in range(int(h / 14) + 1))
            extra.append(f'<rect x="{_f(xx - 13)}" y="{top}" width="26" height="{h}" fill="{light}" opacity="0.35"/>'
                         f'<path d="{ropes}" stroke="{dark}" stroke-width="3.2" fill="none" stroke-linecap="round" opacity="0.7"/>'
                         f'<path d="{ropes}" stroke="#FFF4D8" stroke-width="1.2" fill="none" opacity="0.5" transform="translate(-1 -1)"/>')
    elif kind == "fairisle":
        extra.append(knit_vs((x0, top + 4, x1, top + h), dark, 9, 7, 0.3))
        yb = top + h * 0.3
        extra.append(f'<rect x="{x0 - 5}" y="{_f(yb)}" width="{w + 10}" height="{_f(h * 0.4)}" fill="#B8402A" opacity="0.9"/>')
        dia = "".join(f"M{_n(x)} {_n(yb + h * 0.2)}l7 -7l7 7l-7 7z" for x in range(int(x0), int(x1), 18))
        dots_ = "".join(f"M{_n(x)} {_n(yb + 5)}h0M{_n(x)} {_n(yb + h * 0.4 - 5)}h0" for x in range(int(x0) + 9, int(x1), 9))
        extra.append(f'<path d="{dia}" fill="#F6EEDC"/><path d="{dots_}" stroke="#2E4A3A" stroke-width="4" stroke-linecap="round"/>')
        extra.append(knit_vs((x0, yb, x1, yb + h * 0.4), "#7A1A10", 9, 7, 0.35))
    else:
        rib = "".join(f"M{_n(x)} {top}l0 {h}" for x in range(int(x0), int(x1), 8))
        extra.append(f'<path d="{rib}" stroke="{dark}" stroke-width="2.6" opacity="0.45"/><path d="{rib}" stroke="{light}" stroke-width="1.2" opacity="0.4" transform="translate(3 0)"/>')
    # sleeve fold line + hem band
    extra.append(f'<path d="M {_f(x0 + w * 0.2)} {top + 2} q -6 {h * 0.5:.1f} 0 {h:.1f} M {_f(x1 - w * 0.2)} {top + 2} q 6 {h * 0.5:.1f} 0 {h:.1f}" stroke="{dark}" stroke-width="2" fill="none" opacity="0.5"/>')
    extra.append(f'<rect x="{x0 - 5}" y="{_f(top + h - 12)}" width="{w + 10}" height="14" fill="{dark}" opacity="0.35"/>'
                 + "".join(f'<path d="M {x} {_f(top + h - 12)} l 0 14" stroke="{dark}" stroke-width="1.6" opacity="0.5"/>' for x in range(int(x0), int(x1), 6)))
    out = [form(u, d, (x0, top, x1, top + h), base, dark, light, seed, 0, n=w * h / 40, shade=(0, h * 0.18), shade_op=0.45,
                length=(10, 30), width=(1, 3), ink_w=2.2, extra_in="".join(extra))]
    if collar:
        cd = f"M {cx - 50} {top + 1} Q {cx} {top + 46} {cx + 50} {top + 1} L {cx + 34} {top + 1} Q {cx} {top + 28} {cx - 34} {top + 1} Z"
        ribs = "".join(f"M {_f(cx + 42 * math.sin(a))} {_f(top + 1 + 6 * math.cos(a) + 20 * (1 - abs(math.sin(a))) * 0.9)} l {_f(-8 * math.sin(a))} {_f(10 + 4 * math.cos(a))} "
                       for a in [math.radians(t) for t in range(-80, 81, 10)])
        out.append(form(u, cd, (cx - 50, top, cx + 50, top + 26), dark, "#5A3A10", base, seed + 1, -90, n=30, shade=None, ink_w=1.8,
                        extra_in=f'<path d="{ribs}" stroke="#5A3A10" stroke-width="1.6" opacity="0.45"/>'))
        out.append(f'<path d="M {cx - 34} {top + 2} Q {cx} {top + 28} {cx + 34} {top + 2}" stroke="#2A1608" stroke-width="5" fill="none" opacity="0.25"/>')
    return "".join(out)


@design("sweater-weather")
def sweater_weather():
    u = Ids("sweater-weather")
    o = [bg(u, "#5E6B34", ["#6A7840", "#4E5A28", "#7A8648", "#46521F"], 171, fleck="#F0E6C8", angle=-20)]
    o.append(glow(u, 300, 380, 260, "#E8C070", 0.4))
    o.append(vignette(u, "#262E10", 0.45))
    o.append(shadow(u, 304, 508, 190, 18, 0.45))
    o.append(folded_sweater(u, 300, 432, 320, 70, 172, "#B8502A", "#7A2E14", "#E07A4A", "rib"))
    o.append(folded_sweater(u, 296, 362, 296, 72, 173, "#F1E6D2", "#B8A27E", "#FFFFFF", "fairisle"))
    o.append(folded_sweater(u, 302, 294, 272, 70, 174, "#E2A23A", "#A8701E", "#F6CE6A", "cable", collar=True))
    o.append(mug(u, 488, 446, 54, 48, 175, ("#B8502A", "#7A2E14", "#E07A4A"), band="#F1E6D2", side=1))
    o.append(steam(488, 436, 56, 176, "#FFF6E0", 2, 14, 3.6, 0.8))
    o.append(pumpkin(u, 104, 476, 82, 54, 177, PK_CREAM, leaf_on=False, curl=True, inkc="#7A6448"))
    o.append(scatter_leaves(u, [("maple", 160, 506, 18, -30, L_RED), ("oak", 430, 520, 16, 60, L_GOLD), ("maple", 520, 330, 17, 25, L_ORANGE),
                                ("elm", 82, 340, 15, -40, L_GOLD), ("maple", 74, 250, 12, 15, L_CRAN), ("birch", 528, 248, 12, -30, L_GOLD)], 178))
    t, _, _ = btext(u, 300, 176, "SWEATER", BEBAS, 150, "#F6EAD2", ["#FFF6E4", "#E2D2B4", "#F0E0C4"], 179, max_w=440, ls=6, angle=-80,
                    shadow="#2E3612", soff=(0.025, 0.04))
    o.append(t)
    t, _, _ = btext(u, 300, 250, "weather", SERIF_IT, 80, "#F2BE4A", ["#F6D06A", "#C8901E", "#FFE08A"], 180, max_w=300, angle=-35,
                    shadow="#2E3612", soff=(0.02, 0.04))
    o.append(t)
    o.append(finish(u, "#F0E6C8", 0.6))
    return "".join(o)


# ================================================================ pick your own
@design("pick-your-own")
def pick_your_own():
    u = Ids("pick-your-own")
    sky = u("sky")
    o = [f'<defs>{lgrad(sky, [(0, "#A8C4CC"), (0.6, "#E4E0C8"), (1, "#F4D8A4")])}</defs><rect width="600" height="600" fill="url(#{sky})"/>']
    o.append(paper(u("pp"), "#000", FLECK, 181, 1.0).replace('<rect width="600" height="600" fill="#000"/>', ""))
    o.append(brush((-20, -20, 620, 330), ["#FFFFFF", "#C4D8DC", "#F6E8C8"], 182, 140, -5, (50, 140), (5, 12), (0.1, 0.22), 0.1))
    for cx_, cy_, w_ in ((110, 104, 70), (500, 82, 60), (470, 200, 48)):
        o.append(f'<path d="{blob(cx_, cy_, w_, w_ * 0.3, cx_, 0.2, 14)}" fill="#FFFFFF" opacity="0.8"/>'
                 f'<path d="{blob(cx_ + 6, cy_ + 7, w_ * 0.7, w_ * 0.14, cx_ + 1, 0.2, 12)}" fill="#D8D0C8" opacity="0.6"/>')
    o.append(hill(u, [(-20, 312), (120, 290), (260, 304), (420, 286), (620, 300)], 420, "#A8B08A", "#8A9270", "#C8CCA8", 183, n=60))
    rnd = random.Random(184)
    o.append(dabs((-10, 296, 610, 316), ["#D8843A", "#B8481E", "#E8B04A", "#8A6A3A", "#9AA048"], 185, 160, (6, 12), (0.6, 0.9), 0.7))
    # little red barn on the left
    o.append(form(u, "M 46 330 L 46 300 L 70 284 L 94 300 L 94 330 Z", (46, 284, 94, 330), "#B8402A", "#7A2014", "#D8604A", 186, -90, n=20, shade=(6, 0), ink_w=1.6)
             + '<path d="M 44 301 L 70 282 L 96 301" stroke="#F4EAD8" stroke-width="3" fill="none"/><path d="M 62 330 l 0 -16 l 16 0 l 0 16 M 62 314 l 16 16 M 78 314 l -16 16" stroke="#F4EAD8" stroke-width="1.8" fill="none"/>')
    field = smooth_open([(-20, 326), (300, 318), (620, 326)]) + " L 620 620 L -20 620 Z"
    o.append(form(u, field, (-20, 318, 620, 620), "#B8A050", "#8A7434", "#D8C478", 187, -4, n=300, shade=None, ink_w=0, length=(20, 60), width=(1.5, 4)))
    # pumpkin rows receding: leafy vine rows, pumpkins growing larger towards us
    for row in range(8):
        t = row / 7
        y = 334 + 186 * t ** 1.35
        sz = 4 + 19 * t ** 1.3
        o.append(f'<path d="{wobble_line([(-20, y + sz * 0.3), (300, y + sz * 0.2), (620, y + sz * 0.3)], row, 2)}" stroke="#5E7A34" stroke-width="{max(1.5, sz * 0.3):.1f}" fill="none" opacity="0.75"/>')
        o.append(dabs((-20, y - sz * 0.1, 620, y + sz * 0.6), ["#5E7A34", "#7A9446", "#4A6228", "#9AAE5A"], 400 + row, 40 + 30 * (1 - t), (sz * 0.35, sz * 0.7),
                      (0.6, 0.95), 0.55))
        x = rnd.uniform(-10, 30)
        while x < 620:
            c = rnd.choice([PK_OR, PK_DEEP, PK_OR, PK_CREAM, PK_GOLD])
            pd = blob(x, y, sz * 0.8, sz * 0.55, int(x) + row, 0.06, 10)
            o.append(f'<path d="{pd}" fill="{c[0]}"/>')
            if sz >= 9:
                o.append(f'<path d="{blob(x + sz * 0.25, y + sz * 0.1, sz * 0.5, sz * 0.4, int(x) + row + 1, 0.08, 10)}" fill="{c[1]}" opacity="0.6"/>'
                         f'<path d="M{_n(x - sz * 0.3)} {_n(y - sz * 0.45)}q{_n(-sz * 0.2)} {_n(sz * 0.45)} 0 {_n(sz * 0.9)}M{_n(x + sz * 0.3)} {_n(y - sz * 0.45)}q{_n(sz * 0.2)} {_n(sz * 0.45)} 0 {_n(sz * 0.9)}" '
                         f'stroke="{c[3]}" stroke-width="{max(0.8, sz * 0.06):.1f}" fill="none" opacity="0.6"/>'
                         f'<path d="M{_n(x - sz * 0.45)} {_n(y - sz * 0.15)}q{_n(-sz * 0.05)} {_n(sz * 0.2)} {_n(sz * 0.05)} {_n(sz * 0.3)}" stroke="{c[2]}" stroke-width="{max(1, sz * 0.08):.1f}" fill="none" stroke-linecap="round"/>'
                         f'<path d="{pd}" fill="none" stroke="{c[3]}" stroke-width="{max(0.8, sz * 0.05):.1f}" opacity="0.7"/>')
            o.append(f'<path d="M{_n(x)} {_n(y - sz * 0.5)}l1 {_n(-sz * 0.3)}" stroke="#5A4A22" stroke-width="{max(1, sz * 0.12):.1f}" stroke-linecap="round"/>')
            x += sz * 3.0 + rnd.uniform(0, sz * 3)
    o.append(brush((-20, 470, 620, 620), ["#8A7434", "#D8C478", "#6E8A3E", "#B8A050"], 199, 260, -90, (8, 20), (0.8, 2), (0.3, 0.7), 0.4, 25))
    # signpost
    for px in (226, 374):
        o.append(form(u, f"M {px - 8} 152 L {px + 8} 150 L {px + 9} 470 L {px - 9} 472 Z", (px - 9, 150, px + 9, 472), "#8A6A44", "#5A3E22", "#B8946A", px, -90,
                      n=60, shade=(5, 0), ink_w=2, length=(20, 60), width=(1, 2.5)))
        o.append(shadow(u, px + 10, 474, 26, 5, 0.35))
    o.append(board(u, 132, 156, 468, 236, 188, "#B8402A", "#7A2014", "#D8604A"))
    o.append(board(u, 182, 256, 470, 306, 189, "#F1E2C4", "#B89A6A", "#FFF8E8", point="r"))
    o.append(board(u, 130, 322, 418, 372, 190, "#5E7A3A", "#3A5222", "#88A45E", point="l"))
    for x, y in ((150, 172), (450, 172), (150, 220), (450, 220), (226, 281), (374, 281), (226, 347), (374, 347)):
        o.append(nail(x, y))
    t, _, _ = btext(u, 300, 220, "PICK YOUR OWN", BEBAS, 72, "#FBF0DC", ["#FFFFFF", "#E8D6B8"], 191, max_w=300, ls=3, angle=-80,
                    shadow="#5A1410", soff=(0.02, 0.04))
    o.append(t)
    t, _, _ = btext(u, 312, 297, "PUMPKINS", BEBAS, 46, "#D2602A", ["#E8792E", "#A8401A"], 192, max_w=220, ls=4, angle=-80)
    o.append(t)
    t, _, _ = btext(u, 286, 363, "APPLES", BEBAS, 46, "#FBF0DC", ["#FFFFFF", "#E8D6B8"], 193, max_w=220, ls=4, angle=-80, shadow="#2A3A12",
                    soff=(0.02, 0.04))
    o.append(t)
    # crow on the sign
    crow = smooth_closed([(150, 156), (160, 130), (176, 118), (190, 112), (200, 116), (196, 126), (186, 136), (192, 156)])
    o.append(form(u, crow, (150, 110, 200, 156), "#2A2430", "#120E16", "#5A5266", 194, -60, n=30, shade=(4, 4), ink_w=0))
    o.append('<path d="M 199 117 l 12 3 l -11 4 Z" fill="#E8A030"/><circle cx="192" cy="117" r="2" fill="#F6E6C8"/>'
             '<path d="M 150 156 l -16 -4 l 4 10 Z" fill="#2A2430"/><path d="M 168 156 l 0 6 M 180 156 l 0 6" stroke="#E8A030" stroke-width="2"/>')
    # foreground: hay bale, pumpkins, apple crate
    o.append(hay(u, 58, 440, 136, 72, 195))
    o.append(pumpkin(u, 460, 476, 132, 86, 196, PK_OR))
    o.append(pumpkin(u, 360, 506, 74, 48, 197, PK_CREAM, leaf_on=False, inkc="#7A6448"))
    for i, (x, y) in enumerate(((232, 510), (254, 518), (220, 524))):
        o.append(apple(u, x, y, 13, 198 + i, leaf_on=(i == 0), cast=True))
    o.append(finish(u, INK, 0.7))
    return "".join(o)



# ---------------------------------------------------------------- pieces for the last four
def rot_pt(x, y, cx, cy, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c


def coil(pts, loops, r, seed, col="#5A3418", hi="#E8B860", w=3.6):
    """Coiled telephone cord along a smooth polyline: little loops travelling along the path."""
    rnd = random.Random(seed)
    # resample the guide path
    path = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        for k in range(30):
            t = k / 30
            path.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    path.append(pts[-1])
    n = len(path)
    out = []
    for i in range(n * 6):
        t = i / (n * 6 - 1)
        j = min(n - 2, int(t * (n - 1)))
        f = t * (n - 1) - j
        x = path[j][0] + (path[j + 1][0] - path[j][0]) * f
        y = path[j][1] + (path[j + 1][1] - path[j][1]) * f
        ph = 2 * math.pi * loops * t
        out.append((x + r * math.cos(ph) * 0.55, y + r * math.sin(ph)))
    d = "M " + " L ".join(f"{_f(x)} {_f(y)}" for x, y in out)
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{hi}" stroke-width="{w * 0.35:.1f}" stroke-linecap="round" stroke-dasharray="3 6" opacity="0.7" transform="translate(-0.8 -0.8)"/>')


def flame(u, x, y, s, seed):
    d = f"M {_f(x)} {_f(y - 2.2 * s)} Q {_f(x + 1.1 * s)} {_f(y - 0.6 * s)} {_f(x + 0.8 * s)} {_f(y + 0.2 * s)} Q {_f(x)} {_f(y + 0.9 * s)} {_f(x - 0.8 * s)} {_f(y + 0.2 * s)} Q {_f(x - 1.1 * s)} {_f(y - 0.6 * s)} {_f(x)} {_f(y - 2.2 * s)} Z"
    di = f"M {_f(x)} {_f(y - 1.1 * s)} Q {_f(x + 0.55 * s)} {_f(y - 0.2 * s)} {_f(x + 0.4 * s)} {_f(y + 0.25 * s)} Q {_f(x)} {_f(y + 0.6 * s)} {_f(x - 0.4 * s)} {_f(y + 0.25 * s)} Q {_f(x - 0.55 * s)} {_f(y - 0.2 * s)} {_f(x)} {_f(y - 1.1 * s)} Z"
    return (glow(u, x, y - 0.6 * s, 7 * s, "#FFC86A", 0.55) + glow(u, x, y - 0.6 * s, 2.6 * s, "#FFF0C0", 0.8) +
            f'<path d="{d}" fill="#F6A63A"/><path d="{di}" fill="#FFF4CC"/>' +
            f'<path d="M {_f(x)} {_f(y + 0.5 * s)} l 0 {_f(0.8 * s)}" stroke="#2A1608" stroke-width="{max(1.2, s * 0.22):.1f}" stroke-linecap="round"/>')


def taper_candle(u, x, base, h, seed, wax=("#F4EAD8", "#C8B494", "#FFFFFF"), holder=("#C8963E", "#7A5418", "#F6D88A")):
    out = []
    # brass candlestick: foot, stem knobs, drip cup
    hc, hd, hl = holder
    foot = blob(x, base, 30, 8, seed, 0.04, 14)
    out.append(shadow(u, x + 6, base + 4, 40, 6, 0.4))
    out.append(form(u, foot, (x - 32, base - 9, x + 32, base + 9), hc, hd, hl, seed, 0, n=20, shade=(0, 3), ink_w=1.6, ink_col="#4A2A08"))
    stem = smooth_closed([(x - 6, base - 4), (x - 5, base - 20), (x - 12, base - 28), (x - 6, base - 36), (x - 5, base - 48), (x - 14, base - 54),
                          (x + 14, base - 54), (x + 5, base - 48), (x + 6, base - 36), (x + 12, base - 28), (x + 5, base - 20), (x + 6, base - 4)])
    out.append(form(u, stem, (x - 14, base - 56, x + 14, base), hc, hd, hl, seed + 1, -90, n=20, shade=(4, 0), shade_op=0.6,
                    hi=(x - 4, base - 30, 2, 18), hi_op=0.8, ink_w=1.4, ink_col="#4A2A08"))
    cup = blob(x, base - 56, 18, 5, seed + 2, 0.05, 12)
    out.append(form(u, cup, (x - 20, base - 62, x + 20, base - 50), hc, hd, hl, seed + 3, 0, n=8, shade=(0, 2), ink_w=1.4, ink_col="#4A2A08"))
    top = base - 58 - h
    body = smooth_closed([(x - 8, base - 58), (x - 8, top + 6), (x - 5, top), (x + 5, top + 1), (x + 8, top + 6), (x + 8, base - 58)])
    drip = f'<path d="M {_f(x + 2)} {_f(top + 2)} q 3 10 1 {h * 0.3:.1f} q 0 6 -3 0 q -1 -10 -3 -{h * 0.2:.1f} Z" fill="{wax[2]}" opacity="0.8"/>'
    out.append(form(u, body, (x - 8, top, x + 8, base - 58), wax[0], wax[1], wax[2], seed + 4, -90, n=h * 0.4, shade=(5, 0), shade_op=0.6,
                    ink_w=1.4, ink_col="#8A6A44", extra_in=drip))
    out.append(flame(u, x, top - 4, 6.5, seed + 5))
    return "".join(out)


def lattice_pie(u, cx, cy, rx, ry, seed):
    out = [shadow(u, cx + 8, cy + ry + 8, rx * 1.1, ry * 0.5, 0.45)]
    # tin + crust rim
    tin = blob(cx, cy + ry * 0.35, rx * 1.02, ry * 1.1, seed, 0.02, 20)
    out.append(form(u, tin, (cx - rx, cy - ry, cx + rx, cy + ry * 1.4), "#A8B0B4", "#6A7276", "#E2E8EA", seed, 0, n=20, shade=(0, 6), ink_w=1.8,
                    ink_col="#3A4246"))
    rim = blob(cx, cy, rx, ry, seed + 1, 0.025, 22)
    out.append(form(u, rim, (cx - rx, cy - ry, cx + rx, cy + ry), "#E2A452", "#A8641E", "#F6D08A", seed + 2, lambda x, y: math.degrees(math.atan2(y - cy, x - cx)) + 90,
                    n=rx * ry / 12, shade=(0, 5), ink_w=2, ink_col="#6A3A10"))
    fill = blob(cx, cy, rx * 0.84, ry * 0.76, seed + 3, 0.03, 20)
    strips = []
    for k in range(-3, 4):
        x = cx + k * rx * 0.24
        strips.append(f'<path d="M {_f(x - 6)} {_f(cy - ry)} L {_f(x - 6)} {_f(cy + ry)} L {_f(x + 6)} {_f(cy + ry)} L {_f(x + 6)} {_f(cy - ry)} Z"/>')
    vstrips = "".join(strips)
    hstr = "".join(f'<path d="M {_f(cx - rx)} {_f(cy + k * ry * 0.3 - 4)} L {_f(cx + rx)} {_f(cy + k * ry * 0.3 - 4)} L {_f(cx + rx)} {_f(cy + k * ry * 0.3 + 4)} L {_f(cx - rx)} {_f(cy + k * ry * 0.3 + 4)} Z"/>'
                   for k in range(-2, 3))
    out.append(form(u, fill, (cx - rx, cy - ry, cx + rx, cy + ry), "#9A2A22", "#5A1010", "#C8503A", seed + 4, 0, n=40, shade=(0, -4), ink_w=0,
                    extra_in=f'<g fill="#E8AE5E" stroke="#8A4A14" stroke-width="1.2">{hstr}{vstrips}</g>'
                             f'<g fill="#FBE0A8" opacity="0.45" transform="translate(-2 -1.5)">{vstrips}</g>'))
    out.append(f'<path d="{rim}" fill="none" stroke="#F6D08A" stroke-width="3" stroke-dasharray="4 7" opacity="0.6"/>')
    return "".join(out)


def pear(u, cx, cy, s, seed, pal=("#C8B040", "#8A7A1E", "#ECDC7A"), rot=0, blush="#D8703A"):
    d = smooth_closed([(cx, cy - s), (cx + 0.32 * s, cy - 0.7 * s), (cx + 0.38 * s, cy - 0.2 * s), (cx + 0.62 * s, cy + 0.3 * s), (cx + 0.52 * s, cy + 0.72 * s),
                       (cx, cy + 0.86 * s), (cx - 0.52 * s, cy + 0.72 * s), (cx - 0.62 * s, cy + 0.3 * s), (cx - 0.38 * s, cy - 0.2 * s), (cx - 0.3 * s, cy - 0.7 * s)])
    bl = f'<path d="{blob(cx + 0.25 * s, cy + 0.35 * s, 0.3 * s, 0.35 * s, seed, 0.1, 10)}" fill="{blush}" opacity="0.35"/>'
    return (f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">' +
            form(u, d, (cx - 0.62 * s, cy - s, cx + 0.62 * s, cy + 0.86 * s), pal[0], pal[1], pal[2], seed, lambda x, y: math.degrees(math.atan2(y - cy, x - cx)) + 90,
                 n=s * s / 10, shade=(0.12 * s, 0.08 * s), shade_op=0.55, hi=(cx - 0.25 * s, cy + 0.1 * s, 0.1 * s, 0.25 * s), hi_op=0.55, ink_w=max(1.2, s * 0.03),
                 ink_col="#4A3A10", extra_in=bl) +
            ink(f"M {_f(cx)} {_f(cy - 0.95 * s)} q 2 {-0.2 * s:.1f} {0.1 * s:.1f} {-0.32 * s:.1f}", "#4A2A14", max(2, s * 0.06), seed + 1, 1, 1) +
            "</g>")


def grapes(u, cx, cy, s, seed, pal=("#6B2E4A", "#3A1028", "#A86080")):
    rnd = random.Random(seed)
    out = []
    rows = [(0, 4), (1, 4), (2, 3), (3, 3), (4, 2), (5, 1)]
    berries = []
    for r, n in rows:
        for i in range(n):
            x = cx + (i - (n - 1) / 2) * s * 0.92 + rnd.uniform(-2, 2)
            y = cy + r * s * 0.8 + rnd.uniform(-2, 2)
            berries.append((x, y))
    for x, y in reversed(berries):
        bd = blob(x, y, s * 0.55, s * 0.58, int(x * 7 + y), 0.04, 12)
        out.append(form(u, bd, (x - s * 0.6, y - s * 0.6, x + s * 0.6, y + s * 0.6), pal[0], pal[1], pal[2], int(x + y), -60, n=6,
                        shade=(s * 0.14, s * 0.12), shade_op=0.6, ink_w=1.2, ink_col="#2A0818"))
        out.append(f'<ellipse cx="{_f(x - s * 0.2)}" cy="{_f(y - s * 0.22)}" rx="{_f(s * 0.14)}" ry="{_f(s * 0.1)}" fill="#F2D6E2" opacity="0.75"/>')
    out.append(ink(f"M {_f(cx)} {_f(cy - s * 0.4)} q 2 -10 -6 -18", "#5A3A1A", 3, seed, 1, 1))
    return "".join(out)


def corn_ear(u, x0, y0, x1, y1, seed, w=22):
    """An ear of corn from base (x0, y0) to tip (x1, y1) with husks peeled back at the base."""
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
    L = math.hypot(x1 - x0, y1 - y0)
    out = [f'<g transform="translate({_f(x0)} {_f(y0)}) rotate({ang:.1f})">']
    cob = smooth_closed([(0, -w * 0.45), (L * 0.5, -w * 0.52), (L * 0.9, -w * 0.32), (L, 0), (L * 0.9, w * 0.32), (L * 0.5, w * 0.52), (0, w * 0.45)])
    kern = []
    rnd = random.Random(seed)
    for i in range(int(L / 7)):
        xx = 4 + i * 7
        half = w * 0.5 * math.sin(math.pi * min(1, (xx / L) * 0.9 + 0.12)) ** 0.6
        for j in range(-2, 3):
            yy = j * half * 0.4
            kern.append(f'<ellipse cx="{_f(xx + (j % 2) * 3.5)}" cy="{_f(yy)}" rx="3.4" ry="{_f(max(1.6, half * 0.17))}" fill="{rnd.choice(["#F2C24A", "#E8A93A", "#F6D46A", "#D88A2A", "#B8401E"])}"/>')
    out.append(form(u, cob, (0, -w * 0.55, L, w * 0.55), "#E8B040", "#A8701E", "#F8DA7C", seed, 0, n=10, shade=(0, w * 0.18), shade_op=0.5, ink_w=1.6,
                    ink_col="#6A4010", extra_in="".join(kern)))
    for sgn in (-1, 1):
        husk = smooth_closed([(-6, 0), (L * 0.2, sgn * w * 0.3), (L * 0.42, sgn * w * 0.95), (L * 0.3, sgn * w * 0.85), (L * 0.08, sgn * w * 0.55), (-10, sgn * 4)])
        out.append(form(u, husk, (-10, -w, L * 0.42, w), "#D8C48A", "#9A8650", "#F2E6B8", seed + sgn, 10 * sgn, n=14, shade=(0, sgn * 3), ink_w=1.4,
                        ink_col="#6A5A2A"))
    out.append("</g>")
    return "".join(out)


# ================================================================ autumn is calling
@design("autumn-is-calling")
def autumn_is_calling():
    u = Ids("autumn-is-calling")
    o = [bg(u, "#F5E3CD", ["#EDD3B4", "#FAEEDD", "#E8C8A4"], 201, angle=-18)]
    # painted blob behind the phone, like the reference spot illustrations
    spot = blob(300, 392, 222, 150, 202, 0.07, 22)
    o.append(form(u, spot, (78, 242, 522, 542), "#EFC49A", "#E2A878", "#F8DCBC", 203, -12, n=160, shade=None, ink_w=0, length=(30, 90),
                  width=(3, 9), sop=(0.1, 0.3)))
    o.append(glow(u, 300, 380, 230, "#FFE6C0", 0.5))
    o.append(shadow(u, 304, 506, 170, 16, 0.4))
    # coiled cord from the base to the lifted handset
    o.append(coil([(178, 470), (120, 476), (96, 430), (108, 376), (150, 344)], 15, 9, 204))
    # base
    gold, gdark, glite = "#E6A93A", "#A8681A", "#F8D477"
    body = smooth_closed([(170, 504), (430, 504), (448, 470), (424, 404), (384, 366), (300, 354), (216, 366), (176, 404), (152, 470)])
    o.append(form(u, body, (152, 352, 448, 506), gold, gdark, glite, 205, lambda x, y: -90 + (x - 300) * 0.25, n=260, shade=(-26, -6), shade_op=0.5,
                  hi=(232, 404, 22, 30), hi_op=0.5, ink_w=2.6, ink_col="#5A3410", length=(10, 34), width=(1.2, 3.4)))
    plinth = smooth_closed([(158, 490), (442, 490), (452, 506), (446, 516), (154, 516), (148, 506)])
    o.append(form(u, plinth, (148, 488, 452, 516), "#B8741E", "#7A4410", "#D8A050", 206, 0, n=40, shade=(0, 4), ink_w=2.2, ink_col="#4A2A08"))
    # dial
    dcx, dcy = 300, 440
    dial = blob(dcx, dcy, 66, 50, 207, 0.015, 24)
    o.append(form(u, dial, (dcx - 68, dcy - 52, dcx + 68, dcy + 52), "#F6ECDA", "#C8B08A", "#FFFFFF", 208, lambda x, y: math.degrees(math.atan2(y - dcy, x - dcx)) + 90,
                  n=70, shade=(-8, -6), shade_op=0.45, ink_w=2.2, ink_col="#5A3410"))
    for i in range(10):
        a = math.radians(-60 - i * 27)
        hx, hy = dcx + 46 * math.cos(a), dcy + 34 * math.sin(a)
        o.append(f'<ellipse cx="{_f(hx)}" cy="{_f(hy)}" rx="9.5" ry="8" fill="#C27A2A"/><ellipse cx="{_f(hx + 1.5)}" cy="{_f(hy + 1.5)}" rx="7" ry="5.6" fill="#7A3E12"/>'
                 f'<ellipse cx="{_f(hx)}" cy="{_f(hy)}" rx="9.5" ry="8" fill="none" stroke="#5A3410" stroke-width="1.4"/>'
                 f'<ellipse cx="{_f(hx - 2.5)}" cy="{_f(hy - 2.5)}" rx="2.4" ry="1.6" fill="#FFF0D0" opacity="0.8"/>')
    o.append(ink(f"M {dcx + 50} {dcy + 26} q 8 6 16 2", "#7A7A7A", 4, 209, 1, 1))
    hub = blob(dcx, dcy, 22, 17, 210, 0.03, 14)
    o.append(form(u, hub, (dcx - 24, dcy - 19, dcx + 24, dcy + 19), "#E8D6B8", "#B89A6A", "#FFFAF0", 211, 0, n=10, shade=(-3, -3), ink_w=1.6, ink_col="#5A3410"))
    o.append(leaf(u, "maple", dcx, dcy - 1, 10, 0, L_RED, 212, detail=False))
    # cradle prongs
    for px in (234, 366):
        prong = smooth_closed([(px - 9, 366), (px - 8, 342), (px - 2, 334), (px + 4, 336), (px + 9, 346), (px + 9, 366)])
        o.append(form(u, prong, (px - 10, 332, px + 10, 368), gold, gdark, glite, px, -90, n=10, shade=(3, 0), ink_w=1.8, ink_col="#5A3410"))
    # the lifted, ringing handset
    hs = [(148, 354), (140, 330), (150, 306), (178, 294), (236, 289), (300, 286), (364, 289), (422, 294), (450, 306), (460, 330), (452, 354),
          (426, 360), (404, 352), (394, 332), (366, 318), (300, 314), (234, 318), (206, 332), (196, 352), (174, 360)]
    hs = [rot_pt(x, y - 34, 300, 300, -7) for x, y in hs]
    hd = smooth_closed(hs)
    o.append(f'<path d="{hd}" fill="#3A2418" opacity="0.18" transform="translate(6 22)"/>')
    o.append(form(u, hd, (136, 236, 464, 330), gold, gdark, glite, 213, -4, n=190, shade=(0, -8), shade_op=0.5, hi=(250, 262, 60, 5), hi_op=0.6,
                  ink_w=2.6, ink_col="#5A3410", length=(14, 44), width=(1.2, 3.4)))
    for ex, ey in (rot_pt(172, 324, 300, 300, -7), rot_pt(428, 324, 300, 300, -7)):
        o.append(f'<ellipse cx="{_f(ex)}" cy="{_f(ey)}" rx="22" ry="5" fill="#7A4410" opacity="0.45" transform="rotate(-7 {_f(ex)} {_f(ey)})"/>'
                 f'<path d="M {_f(ex - 14)} {_f(ey - 12)} q 14 -6 28 0" stroke="#FFE6A8" stroke-width="2.4" fill="none" stroke-linecap="round" opacity="0.6" transform="rotate(-7 {_f(ex)} {_f(ey)})"/>')
    # ring marks
    for sgn in (-1, 1):
        bx = 300 + sgn * 186
        for k, rr in enumerate((16, 30)):
            o.append(ink(f"M {_f(bx + sgn * rr * 0.2)} {_f(242 - rr)} Q {_f(bx + sgn * (rr * 0.85))} 252 {_f(bx + sgn * rr * 0.2)} {_f(262 + rr)}", "#B8481E", 3.2 - k * 0.6,
                         214 + k + sgn, 2, 0.85))
    # leaves swirling out with the ring, and a wind trail
    o.append(scatter_leaves(u, [("maple", 506, 446, 22, 25, L_RED), ("oak", 96, 290, 18, -35, L_GOLD), ("elm", 524, 296, 16, 60, L_ORANGE),
                                ("maple", 82, 520, 15, -20, L_ORANGE), ("birch", 474, 518, 13, 30, L_GOLD), ("maple", 112, 226, 13, 40, L_CRAN),
                                ("elm", 490, 214, 12, -50, L_OLIVE)], 216))
    t, _, _ = btext(u, 300, 150, "AUTUMN", ANTON, 120, "#B8481E", ["#D2602A", "#8E3A12", "#E8792E", "#A8401A"], 217, max_w=420, ls=8, angle=-78,
                    shadow="#6E2A10", soff=(0.025, 0.04), hi="#FFD8A8")
    o.append(t)
    t, _, _ = btext(u, 300, 220, "is calling", SERIF_IT, 70, "#4A2A14", ["#6A3E20", "#2E1A0C", "#7A4A28"], 218, max_w=320, angle=-35,
                    shadow="#F2D2AE", soff=(0.02, 0.035))
    o.append(t)
    o.append(finish(u))
    return "".join(o)


# ================================================================ boots & blankets
def boot(u, ox, oy, s, seed, leather=("#8A5230", "#56301A", "#C0804E"), sock=("#F1E6D2", "#C8B494", "#FFFFFF"), lace="#B8322A", dim=0.0):
    """Lace-up leather boot in side view, toe pointing left; (ox, oy) = heel-bottom corner."""
    P = lambda x, y: (ox + x * s, oy + y * s)
    shape = [P(-176, -6), P(-182, -28), P(-166, -54), P(-132, -66), P(-110, -82), P(-100, -106), P(-98, -150), P(-96, -182), P(-12, -188),
             P(-6, -150), P(-10, -112), P(-2, -70), P(4, -28), P(2, -4)]
    d = smooth_closed(shape)
    lc, ld, ll = leather
    if dim:
        lc, ld, ll = ld, "#3A1E0E", lc
    out = [form(u, d, (ox - 184 * s, oy - 190 * s, ox + 6 * s, oy), lc, ld, ll, seed, lambda x, y: -90 if x > ox - 100 * s else -15, n=s * s * 220,
                shade=(-12 * s, -6 * s), shade_op=0.55, hi=(ox - 146 * s, oy - 50 * s, 20 * s, 7 * s), hi_op=0.55, ink_w=2.4, ink_col="#2E1608",
                length=(8 * s, 30 * s), width=(1.2, 3.2))]
    # toe cap seam, heel counter, pull tab
    out.append(ink(f"M {_f(ox - 140 * s)} {_f(oy - 62 * s)} Q {_f(ox - 124 * s)} {_f(oy - 32 * s)} {_f(ox - 134 * s)} {_f(oy - 8 * s)}", "#3A1E0E", 1.8, seed + 1, 1, 0.7))
    out.append(ink(f"M {_f(ox - 100 * s)} {_f(oy - 104 * s)} Q {_f(ox - 60 * s)} {_f(oy - 96 * s)} {_f(ox - 8 * s)} {_f(oy - 110 * s)}", "#3A1E0E", 1.6, seed + 6, 1, 0.5))
    out.append(ink(f"M {_f(ox - 2 * s)} {_f(oy - 70 * s)} Q {_f(ox - 40 * s)} {_f(oy - 66 * s)} {_f(ox - 52 * s)} {_f(oy - 8 * s)}", "#3A1E0E", 1.8, seed + 2, 1, 0.6))
    # sole and heel
    sole = smooth_closed([P(-182, -16), P(-100, -11), P(4, -11), P(6, 6), P(-56, 6), P(-58, 2), P(-176, 2), P(-186, -6)])
    out.append(form(u, sole, (ox - 188 * s, oy - 16 * s, ox + 6 * s, oy + 6 * s), "#3E2A1C", "#1E120A", "#6A5038", seed + 3, 0, n=12, shade=None,
                    ink_w=1.4, ink_col="#1A0E06"))
    out.append(f'<path d="M {_f(ox - 176 * s)} {_f(oy - 4 * s)} L {_f(ox - 6 * s)} {_f(oy - 4 * s)}" stroke="#E2C8A0" stroke-width="1.4" stroke-dasharray="3 3" opacity="0.6"/>')
    # laces: hooks up the front with criss-cross
    pts = []
    for k in range(7):
        t = k / 6
        x = ox + (-112 + 16 * t) * s
        y = oy + (-82 - 92 * t) * s
        pts.append((x, y))
    cross = "".join(f"M {_f(pts[k][0] - 4)} {_f(pts[k][1])} L {_f(pts[k + 1][0] + 10 * s)} {_f(pts[k + 1][1])} M {_f(pts[k][0] + 10 * s)} {_f(pts[k][1])} L {_f(pts[k + 1][0] - 4)} {_f(pts[k + 1][1])} "
                    for k in range(6))
    out.append(f'<path d="{cross}" stroke="{lace}" stroke-width="2.8" stroke-linecap="round" fill="none"/>')
    out.append("".join(f'<circle cx="{_f(x - 4)}" cy="{_f(y)}" r="2.6" fill="#E8C878" stroke="#5A3A10" stroke-width="1"/>' for x, y in pts))
    bx, by = pts[-1]
    out.append(ink(f"M {_f(bx)} {_f(by)} q -18 -14 -24 -2 q 4 8 24 2 q 16 -14 22 -2 q -4 8 -22 2 M {_f(bx)} {_f(by)} q -8 10 -16 20 M {_f(bx)} {_f(by)} q 2 12 -4 24",
                   lace, 2.6, seed + 4, 1, 1))
    # knit sock cuff folded over the top
    cuff = smooth_closed([P(-104, -160), P(-106, -196), P(-60, -202), P(-4, -196), P(0, -160), P(-50, -166)])
    rib = "".join(f"M {_f(ox + (-106 + i * 7) * s)} {_f(oy - 204 * s)} l 0 {46 * s:.1f} " for i in range(16))
    out.append(form(u, cuff, (ox - 108 * s, oy - 204 * s, ox + 2 * s, oy - 158 * s), sock[0], sock[1], sock[2], seed + 5, -90, n=30, shade=(0, -5), shade_op=0.4,
                    ink_w=2, ink_col="#7A6448", extra_in=f'<path d="{rib}" stroke="{sock[1]}" stroke-width="2" opacity="0.7"/>'
                                                       f'<path d="M {_f(ox - 110 * s)} {_f(oy - 176 * s)} L {_f(ox + 4 * s)} {_f(oy - 176 * s)}" stroke="#B8322A" stroke-width="{5 * s:.1f}" opacity="0.85"/>'))
    return "".join(out)


def folded_blanket(u, x0, y0, x1, y1, seed, kind):
    w, h = x1 - x0, y1 - y0
    d = smooth_closed(jitter([(x0 + 8, y0), ((x0 + x1) / 2, y0 - 3), (x1 - 8, y0), (x1 + 3, y0 + h * 0.5), (x1 - 4, y1), ((x0 + x1) / 2, y1 + 2), (x0 + 4, y1),
                              (x0 - 3, y0 + h * 0.5)], seed, 1.2))
    extra = []
    if kind == "plaid":
        extra.append(plaid_fill((x0, y0, x1, y1), "#B8402A", [("#3E5A3A", 12, 46, 4, 0.7), ("#2A2A3A", 4, 46, 24, 0.55), ("#F2C24A", 3, 46, 36, 0.85),
                                                             ("#F6E6CF", 2, 23, 14, 0.3)], seed, 0, (x0 + x1) / 2, (y0 + y1) / 2))
        base, dark, light = "#B8402A", "#6E1E12", "#E07050"
    elif kind == "knit":
        extra.append(knit_vs((x0, y0, x1, y1), "#B8A27E", 9, 7, 0.55))
        for k in (0.25, 0.5, 0.75):
            xx = x0 + w * k
            ropes = "".join(f"M{_n(xx - 7)} {_n(y0 + 4 + j * 12)}q7 6 14 12M{_n(xx + 7)} {_n(y0 + 4 + j * 12)}q-7 6 -14 12" for j in range(int(h / 12) + 1))
            extra.append(f'<path d="{ropes}" stroke="#B8A27E" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.8"/>')
        base, dark, light = "#F1E6D2", "#B8A27E", "#FFFFFF"
    else:  # sage wool with blanket-stitch edge
        base, dark, light = "#8E9A6A", "#5E6A40", "#B8C290"
        extra.append(f'<path d="{"".join(f"M{_n(x)} {_n(y0 + 6)}l0 {_n(h - 12)}" for x in range(int(x0) + 6, int(x1), 5))}" stroke="{dark}" stroke-width="1.2" opacity="0.35"/>')
        extra.append(f'<path d="{wobble_line([(x0, y0 + 9), ((x0 + x1) / 2, y0 + 7), (x1, y0 + 9)], seed, 0.6)}" stroke="#F1E6D2" stroke-width="2.4" fill="none" stroke-dasharray="7 6" stroke-linecap="round"/>'
                     f'<path d="{wobble_line([(x0, y1 - 9), ((x0 + x1) / 2, y1 - 8), (x1, y1 - 9)], seed + 1, 0.6)}" stroke="#F1E6D2" stroke-width="2.4" fill="none" stroke-dasharray="7 6" stroke-linecap="round"/>')
    # folded front edge: lighter roll + shadow under it
    extra.append(f'<path d="M {x0 - 4} {_f(y0 + h * 0.18)} Q {_f((x0 + x1) / 2)} {_f(y0 + h * 0.08)} {x1 + 4} {_f(y0 + h * 0.18)} L {x1 + 4} {_f(y0 - 6)} L {x0 - 4} {_f(y0 - 6)} Z" fill="{light}" opacity="0.3"/>'
                 f'<path d="M {x0 - 4} {_f(y1 - h * 0.18)} Q {_f((x0 + x1) / 2)} {_f(y1 - h * 0.06)} {x1 + 4} {_f(y1 - h * 0.18)} L {x1 + 4} {_f(y1 + 6)} L {x0 - 4} {_f(y1 + 6)} Z" fill="#2A1608" opacity="0.18"/>')
    out = [form(u, d, (x0, y0, x1, y1), base, dark, light, seed, 0, n=w * h / 50, shade=(0, h * 0.14), shade_op=0.35, length=(10, 30), width=(1, 2.6),
                ink_w=2.2, extra_in="".join(extra))]
    # fringe on the right edge
    if kind != "sage":
        rnd = random.Random(seed)
        fr = "".join(f"M{_n(x1 - 1)} {_n(y0 + 5 + i * (h - 10) / 7)}q{_n(rnd.uniform(5, 9))} {_n(rnd.uniform(-2, 3))} {_n(rnd.uniform(10, 15))} {_n(rnd.uniform(2, 6))}" for i in range(8))
        out.append(f'<path d="{fr}" stroke="{base}" stroke-width="3" stroke-linecap="round" fill="none"/><path d="{fr}" stroke="{dark}" stroke-width="1" fill="none" opacity="0.6"/>')
    return "".join(out)


def braided_rug(u, cx, cy, rx, ry, seed):
    cols = ["#B8402A", "#E2A23A", "#5E7A4A", "#F1E6D2", "#8A5230", "#C8702E"]
    out = [shadow(u, cx, cy + 6, rx * 1.02, ry * 1.1, 0.35)]
    rnd = random.Random(seed)
    for k in range(9):
        f = 1 - k / 9.5
        col = cols[k % len(cols)]
        d = blob(cx, cy, rx * f, ry * f, seed + k, 0.012, 26)
        out.append(f'<path d="{d}" fill="{col}"/>')
        out.append(f'<path d="{blob(cx, cy, rx * (f - 0.05), ry * (f - 0.05), seed + k, 0.012, 26)}" fill="none" stroke="#2A1608" stroke-width="{max(1.0, 5 * f):.1f}" '
                   f'stroke-dasharray="{4 * f + 2:.1f} {3 * f + 2:.1f}" opacity="0.28"/>')
    out.append(brush((cx - rx, cy - ry, cx + rx, cy + ry), ["#FFF6E4", "#2A1608"], seed, 120, -2, (6, 16), (0.8, 1.8), (0.08, 0.2), 0.4))
    return "".join(out)


@design("boots-and-blankets")
def boots_and_blankets():
    u = Ids("boots-and-blankets")
    o = [bg(u, "#E6B75E", ["#EEC676", "#D8A44A", "#F2D08A", "#CC9440"], 221, fleck="#5A3A1A", angle=-82, length=(80, 200))]
    o.append(glow(u, 300, 360, 260, "#FFE6B0", 0.45))
    # painted wainscot / floor line
    floor = smooth_open([(-20, 452), (300, 446), (620, 452)]) + " L 620 620 L -20 620 Z"
    o.append(form(u, floor, (-20, 444, 620, 620), "#9A6A3A", "#6A4420", "#C08E5A", 222, -2, n=260, shade=None, ink_w=0, length=(50, 140), width=(2, 5),
                  extra_in="".join(f'<path d="{wobble_line([(-20, y), (300, y - 2), (620, y)], int(y), 1.2)}" stroke="#4A2A10" stroke-width="2" fill="none" opacity="0.45"/>'
                                   for y in (488, 532, 580))))
    o.append(f'<path d="{smooth_open([(-20, 452), (300, 446), (620, 452)])}" stroke="#4A2A10" stroke-width="3" fill="none" opacity="0.6"/>')
    o.append(braided_rug(u, 300, 498, 252, 46, 223))
    # stack of folded blankets on the left
    o.append(shadow(u, 214, 490, 128, 12, 0.45))
    o.append(folded_blanket(u, 96, 430, 330, 488, 224, "plaid"))
    o.append(folded_blanket(u, 108, 378, 318, 432, 225, "knit"))
    o.append(folded_blanket(u, 120, 332, 306, 380, 226, "sage"))
    # boots on the right
    o.append(shadow(u, 420, 500, 100, 10, 0.5))
    o.append(boot(u, 512, 486, 0.86, 227, dim=1))
    o.append(boot(u, 482, 498, 0.9, 228))
    # small details: leaves tracked in, an acorn, a tiny pumpkin on the blankets
    o.append(pumpkin(u, 214, 314, 70, 44, 229, PK_OR, leaf_on=True, curl=True))
    o.append(scatter_leaves(u, [("maple", 88, 512, 17, -20, L_RED), ("oak", 520, 520, 15, 60, L_BROWN), ("elm", 310, 528, 12, 80, L_GOLD),
                                ("maple", 92, 300, 15, 25, L_ORANGE), ("birch", 512, 290, 13, -30, L_CRAN)], 230))
    t, _, _ = btext(u, 300, 156, "BOOTS", ANTON, 130, "#4A2412", ["#6A3A1E", "#2E1608", "#7A4A28"], 231, max_w=380, ls=12, angle=-80,
                    shadow="#F6DCA0", soff=(0.025, 0.04), hi="#C08A5A")
    o.append(t)
    t, _, _ = btext(u, 300, 236, "& blankets", SERIF_IT, 78, "#8E2A16", ["#A8381E", "#6E1E0E", "#C04A2A"], 232, max_w=380, angle=-35,
                    shadow="#F6DCA0", soff=(0.02, 0.035))
    o.append(t)
    o.append(finish(u, INK, 0.7))
    return "".join(o)


# ================================================================ gather together
@design("gather-together")
def gather_together():
    u = Ids("gather-together")
    o = [bg(u, "#3E2820", ["#4A3026", "#32201A", "#56382C", "#2A1A14"], 241, fleck="#E8D0B0", angle=-20)]
    o.append(glow(u, 300, 300, 300, "#F2A050", 0.38))
    o.append(vignette(u, "#140A06", 0.55))
    # tablecloth: top surface in gentle perspective, then the drop with folds
    top = smooth_closed([(52, 382), (300, 376), (548, 382), (640, 470), (300, 476), (-40, 470)])
    o.append(form(u, top, (-40, 374, 640, 478), "#EEDFC4", "#C8B08A", "#FFF8EA", 242, -2, n=260, shade=(0, -8), shade_op=0.3, ink_w=0,
                  length=(40, 120), width=(2, 5)))
    drop = smooth_open([(-40, 470), (300, 476), (640, 470)]) + " L 640 640 L -40 640 Z"
    folds = "".join(f'<path d="{wobble_line([(x, 474), (x + 4, 540), (x - 2, 620)], x, 1.5)}" stroke="#A8906A" stroke-width="8" fill="none" opacity="0.35"/>'
                    for x in range(20, 600, 46))
    o.append(form(u, drop, (-40, 470, 640, 640), "#E6D4B6", "#B89E78", "#F8EEDA", 243, -90, n=200, shade=None, ink_w=0, length=(30, 90), width=(2, 5),
                  extra_in=folds))
    o.append(f'<path d="{smooth_open([(-40, 470), (300, 476), (640, 470)])}" stroke="#8A6A44" stroke-width="2.4" fill="none" opacity="0.6"/>')
    # runner down the middle, hanging over the front
    run = smooth_closed([(262, 378), (338, 378), (372, 474), (370, 620), (230, 620), (228, 474)])
    rc = u("rc")
    o.append(f'<clipPath id="{rc}"><path d="{run}"/></clipPath>')
    o.append(f'<g clip-path="url(#{rc})">' + plaid_fill((220, 370, 380, 630), "#A8401E", [("#6E2A12", 10, 40, 4, 0.6), ("#E2A23A", 3, 40, 28, 0.85),
                                                                                          ("#F6E6CF", 2, 20, 12, 0.3)], 244, 0, 300, 500) +
             brush((220, 370, 380, 630), ["#2A1006", "#F6C890"], 245, 90, -90, (10, 30), (1, 2.4), (0.1, 0.3), 0.3) +
             f'<rect x="220" y="470" width="160" height="12" fill="#2A1006" opacity="0.25"/></g>')
    o.append(ink(run, "#4A1A08", 2, 246, 1, 0.7))
    rnd = random.Random(247)
    fr = "".join(f"M{_n(x)} 619l{_n(rnd.uniform(-2, 2))} 14" for x in range(232, 370, 5))
    o.append(f'<path d="{fr}" stroke="#E2A23A" stroke-width="2" opacity="0.8"/>')
    # warm light pooled on the cloth
    o.append(glow(u, 300, 430, 260, "#FFD890", 0.35, 60))
    # garland along the back of the table
    gl = []
    for i in range(22):
        x = 64 + i * 22 + rnd.uniform(-4, 4)
        y = 384 + rnd.uniform(-4, 3)
        gl.append((rnd.choice(["maple", "oak", "elm", "maple"]), x, y, rnd.uniform(11, 15), rnd.uniform(-80, 80), rnd.choice(LEAF_PALS)))
    o.append(scatter_leaves(u, gl, 248, detail=True))
    for i in range(9):
        bx = 90 + i * 52 + rnd.uniform(-8, 8)
        for j in range(3):
            px, py = bx + 5 * math.cos(j * 2.1 + i), 388 + 5 * math.sin(j * 2.1 + i)
            o.append(f'<circle cx="{_f(px)}" cy="{_f(py)}" r="4.4" fill="#B02A22" stroke="#5A1010" stroke-width="1"/><circle cx="{_f(px - 1.3)}" cy="{_f(py - 1.4)}" r="1.3" fill="#FFD8C8"/>')
    # candles
    o.append(taper_candle(u, 176, 420, 92, 249))
    o.append(taper_candle(u, 424, 420, 80, 250))
    o.append(taper_candle(u, 300, 404, 112, 251))
    # pie front and centre, little pumpkins and pears around
    o.append(lattice_pie(u, 300, 446, 86, 26, 252))
    o.append(pumpkin(u, 104, 440, 92, 58, 253, PK_CREAM, leaf_on=False, curl=True, inkc="#7A6448"))
    o.append(pumpkin(u, 496, 442, 96, 62, 254, PK_OR, leaf_on=True, curl=False))
    o.append(pear(u, 200, 450, 26, 255, rot=-12))
    o.append(apple(u, 404, 462, 16, 256, leaf_on=False, cast=True))
    o.append(acorn_g(u, 236, 470, 9, -20))
    t, s1, w1 = btext(u, 300, 156, "gather", SERIF_IT, 130, "#F6E4CC", ["#FFF4E2", "#E6C8A8", "#F2D6B6"], 257, max_w=400, angle=-35,
                      shadow="#140A06", soff=(0.02, 0.045))
    o.append(t)
    t, s2, w2 = btext(u, 300, 218, "TOGETHER", JOS, 38, "#E9B54A", ["#F6CE6A", "#C8901E"], 258, max_w=320, ls=16, angle=-80)
    o.append(t)
    for sgn in (-1, 1):
        a = 300 + sgn * (w2 / 2 + 16)
        o.append(hand_rule(a, a + sgn * 46, 205, "#E9B54A", 2.2, 259 + sgn))
    o.append(finish(u, "#E8D0B0", 0.55))
    return "".join(o)


def acorn_g(u, cx, cy, s, rot=0):
    nut = blob(cx, cy + 0.3 * s, 0.42 * s, 0.55 * s, 3, 0.04)
    cap = f"M {_f(cx - 0.55 * s)} {_f(cy)} Q {_f(cx)} {_f(cy - 0.62 * s)} {_f(cx + 0.55 * s)} {_f(cy)} Q {_f(cx)} {_f(cy + 0.18 * s)} {_f(cx - 0.55 * s)} {_f(cy)} Z"
    return (f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">' +
            form(u, nut, (cx - 0.45 * s, cy - 0.3 * s, cx + 0.45 * s, cy + 0.9 * s), "#B9773A", "#7A4A20", "#E2AA6A", int(cx), -90, n=6, shade=(0.1 * s, 0),
                 ink_w=1.2, ink_col="#3A2010") +
            form(u, cap, (cx - 0.55 * s, cy - 0.4 * s, cx + 0.55 * s, cy + 0.1 * s), "#6E4A2A", "#4A2E16", "#9A7448", int(cy), 0, n=5, shade=None, ink_w=1.2,
                 ink_col="#2A1608") +
            ink(f"M {_f(cx)} {_f(cy - 0.3 * s)} q {0.05 * s:.1f} {-0.2 * s:.1f} {0.16 * s:.1f} {-0.26 * s:.1f}", "#3A2010", max(1.4, s * 0.12), 1, 1, 1) + "</g>")


# ================================================================ harvest
def cornucopia(u, seed):
    """Woven horn of plenty: mouth opening to the right, tail curling up on the left."""
    spine = [(386, 300), (330, 318), (262, 334), (196, 334), (146, 314), (118, 280), (122, 246), (146, 228), (168, 234)]
    rad = [94, 84, 70, 54, 40, 28, 18, 10, 4]
    # resample spine smoothly
    S = []
    for i in range(len(spine) - 1):
        for k in range(8):
            t = k / 8
            x = spine[i][0] + (spine[i + 1][0] - spine[i][0]) * t
            y = spine[i][1] + (spine[i + 1][1] - spine[i][1]) * t
            S.append((x, y, rad[i] + (rad[i + 1] - rad[i]) * t))
    S.append((*spine[-1], rad[-1]))
    # smooth with a small moving average
    S2 = []
    for i in range(len(S)):
        a, b = max(0, i - 3), min(len(S), i + 4)
        S2.append(tuple(sum(p[j] for p in S[a:b]) / (b - a) for j in range(3)))
    S = S2
    left, right, ribs = [], [], []
    for i in range(len(S)):
        x, y, r = S[i]
        x2, y2, _ = S[min(i + 1, len(S) - 1)]
        x1, y1, _ = S[max(i - 1, 0)]
        tx, ty = x2 - x1, y2 - y1
        L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        left.append((x + nx * r, y + ny * r))
        right.append((x - nx * r, y - ny * r))
        ribs.append(((x + nx * r, y + ny * r), (x - nx * r, y - ny * r), (x, y), (tx / L, ty / L), r))
    outline = smooth_closed(left + list(reversed(right)))
    out = [shadow(u, 270, 404, 190, 16, 0.5)]
    weave = []
    for i in range(1, len(ribs) - 2, 3):
        (ax, ay), (bx, by), (cx, cy), (dx, dy), r = ribs[i]
        bulge = r * 0.45
        mx, my = cx - dx * bulge, cy - dy * bulge
        weave.append(f'<path d="M {_f(ax)} {_f(ay)} Q {_f(mx)} {_f(my)} {_f(bx)} {_f(by)}" stroke="#5A3410" stroke-width="{max(1.4, r * 0.05):.1f}" fill="none" opacity="0.7"/>')
        weave.append(f'<path d="M {_f(ax)} {_f(ay)} Q {_f(mx)} {_f(my)} {_f(bx)} {_f(by)}" stroke="#F6D08A" stroke-width="{max(1, r * 0.03):.1f}" fill="none" opacity="0.5" transform="translate(-2 -1)"/>')
        # diagonal plaits between ribs
        if i + 3 < len(ribs):
            (a2x, a2y), (b2x, b2y), _, _, r2 = ribs[i + 3]
            for k in range(1, 8):
                t = k / 8
                p1 = (ax + (bx - ax) * t, ay + (by - ay) * t)
                p2 = (a2x + (b2x - a2x) * t, a2y + (b2y - a2y) * t)
                sgn = 1 if (i // 3 + k) % 2 else -1
                weave.append(f'<path d="M {_f(p1[0])} {_f(p1[1])} Q {_f((p1[0] + p2[0]) / 2 + sgn * 3)} {_f((p1[1] + p2[1]) / 2 - sgn * 3)} {_f(p2[0])} {_f(p2[1])}" '
                             f'stroke="{"#8A5A22" if sgn > 0 else "#E8B868"}" stroke-width="{max(1.2, r * 0.07):.1f}" fill="none" stroke-linecap="round" opacity="0.55"/>')
    out.append(form(u, outline, (100, 200, 400, 410), "#C8903E", "#7A4A18", "#EEC27A", seed, lambda x, y: -60, n=200, shade=(0, -16), shade_op=0.5,
                    hi=(250, 300, 70, 10), hi_op=0.35, ink_w=2.6, ink_col="#4A2A08", length=(8, 22), width=(1, 3), extra_in="".join(weave)))
    # mouth: dark inside with a braided rim
    mouth = blob(392, 300, 28, 96, seed + 1, 0.03, 20, rot=-14)
    out.append(f'<path d="{mouth}" fill="#3A2008"/>' + f'<path d="{blob(398, 300, 18, 82, seed + 2, 0.05, 16, rot=-14)}" fill="#1E1004" opacity="0.6"/>')
    out.append(f'<path d="{mouth}" fill="none" stroke="#8A5A22" stroke-width="13"/><path d="{mouth}" fill="none" stroke="#E8B868" stroke-width="9" stroke-dasharray="7 5" opacity="0.9"/>'
               f'<path d="{mouth}" fill="none" stroke="#4A2A08" stroke-width="1.6" opacity="0.8" transform="translate(-6 0)"/>')
    return "".join(out)


@design("harvest")
def harvest():
    u = Ids("harvest")
    o = [bg(u, "#9C4220", ["#A84C26", "#8A3618", "#B85A30", "#7A2E12"], 261, fleck="#F6D8B0", angle=-25)]
    o.append(glow(u, 320, 300, 270, "#F6B256", 0.55))
    o.append(vignette(u, "#3A1206", 0.5))
    o.append('<g transform="translate(-16 0)">')
    # wheat fanning out behind the mouth
    for k, (dx, dy) in enumerate(((-30, -170), (0, -186), (34, -176), (64, -150), (88, -118), (-58, -146), (16, -160))):
        o.append(wheat(u, 400, 300, 400 + dx, 300 + dy, 262 + k, n=7))
    o.append(corn_ear(u, 404, 300, 470, 156, 270, 26))
    o.append(cornucopia(u, 271))
    # produce tumbling out of the mouth
    o.append(pear(u, 466, 286, 40, 273, rot=18))
    o.append(pumpkin(u, 452, 372, 136, 90, 274, PK_OR, leaf_on=True, curl=True))
    o.append(grapes(u, 392, 352, 14, 272))
    o.append(apple(u, 362, 386, 26, 275, cast=True))
    o.append(apple(u, 314, 398, 20, 276, ("#B8402A", "#7A1E16", "#E8805A"), rot=-20, leaf_on=False, cast=True))
    o.append(pumpkin(u, 506, 412, 56, 38, 277, PK_GOLD, leaf_on=False, curl=False, lobes=3))
    o.append(scatter_leaves(u, [("maple", 252, 410, 20, -20, L_GOLD), ("oak", 208, 406, 16, 70, L_BROWN), ("maple", 520, 222, 15, 30, L_RED),
                                ("elm", 108, 360, 15, -40, L_GOLD), ("maple", 92, 150, 13, 20, L_ORANGE)], 278))
    o.append("</g>")
    for x, y, s in ((96, 110, 6), (520, 110, 5), (140, 420, 4)):
        o.append(sparkle(x, y, s, "#FBDDA8", 0.7))
    t, _, _ = btext(u, 300, 492, "HARVEST", CINZEL, 96, "#FBEBD2", ["#FFF6E6", "#E8D2B4", "#F6E0C0"], 279, max_w=450, ls=8, angle=-78,
                    shadow="#4A1406", soff=(0.025, 0.045))
    o.append(t)
    o.append(ruled(u, 534, "gather & give thanks", SERIF_IT, 38, "#F6C860", 280, ls=0, line="#F6C860", line_w=34, gap=14, w=2.2))
    o.append(finish(u, "#F6D8B0", 0.55))
    return "".join(o)


def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:] or None)
