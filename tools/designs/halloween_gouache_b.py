"""Halloween, hand-painted (gouache / storybook) edition, set B.

Every magnet is painted, not drawn: brushed night skies, moons with swirling halos, washes with pooled edges,
brush strokes clipped inside every shape and following its form, warm hand-inked outlines, candle and moon
glows, brush-textured lettering and paper grain on top. Cute-spooky and family friendly.

Palette shared with set A: inky purple-navy, pumpkin orange, candle gold, slime green accents, bone cream.

Run from tools/designs:  python3 halloween_gouache_b.py [slug ...]
"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from gouache import blob, blob_pts, ink, jitter, maple_leaf, painted_pumpkin, paper, smooth_closed, smooth_open, wash
from halloween_painted import FACES
from paint import P, lg, rg
from poster import ANTON

COL = "halloween"

# ---------------------------------------------------------------- palette
NIGHT = "#15122E"      # inky purple-navy
NAVY = "#221C44"
PURPLE = "#33275A"
PLUM = "#4E3270"
VIOLET = "#6E5398"
LILAC = "#A893D2"
MIST = "#CFC2EA"
PUMPKIN = "#E8792E"
PUMPKIN_D = "#B9531E"
PUMPKIN_L = "#F8A85A"
GOLD = "#F2B33D"
CANDLE = "#FFE29A"
SLIME = "#9BD14B"
SLIME_D = "#5C8A2A"
BONE = "#F3EAD6"
BONE_D = "#D8C8A8"
PAPER = "#F3E8D4"
INK = "#3A2418"        # warm brown pen line (paper pieces)
INKN = "#2A1830"       # plum-brown pen line (night pieces)
SIL = "#17111F"        # silhouette ink


def _f(v):
    return f"{v:.1f}"


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


def rect_d(x0, y0, x1, y1):
    return f"M {x0} {y0} L {x1} {y0} L {x1} {y1} L {x0} {y1} Z"


def glow(u, cx, cy, r, color, op=0.6, mid=0.4):
    return (defs(rg(u, [(0, color, op), (mid, color, op * 0.45), (1, color, 0)]))
            + f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="url(#{u})"/>')


def eglow(u, cx, cy, rx, ry, color, op=0.6):
    return (defs(rg(u, [(0, color, op), (0.5, color, op * 0.45), (1, color, 0)]))
            + f'<ellipse cx="{_f(cx)}" cy="{_f(cy)}" rx="{_f(rx)}" ry="{_f(ry)}" fill="url(#{u})"/>')


# ---------------------------------------------------------------- brushwork
def dab(x, y, L, w, a_deg, col, op, curve, rnd):
    a = math.radians(a_deg)
    dx, dy = L * math.cos(a), L * math.sin(a)
    nx, ny = -math.sin(a), math.cos(a)
    bend = L * curve * rnd.uniform(-1, 1)
    mx, my = x + dx / 2 + nx * bend, y + dy / 2 + ny * bend
    return (f'<path d="M {_f(x)} {_f(y)} Q {_f(mx + nx * w)} {_f(my + ny * w)} {_f(x + dx)} {_f(y + dy)} '
            f'Q {_f(mx - nx * w)} {_f(my - ny * w)} {_f(x)} {_f(y)} Z" fill="{col}" opacity="{op:.2f}"/>')


def dabs(colors, seed, box, n, angle=-80, length=(14, 40), width=(2, 6), opacity=(0.18, 0.5), curve=0.25, jit=12, keep=None):
    """Free tapered brush strokes. angle may be a number or f(x, y) -> degrees; keep(x, y) filters positions."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    tries = 0
    while len(out) < n and tries < n * 6:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if keep and not keep(x, y):
            continue
        a = angle(x, y) if callable(angle) else angle
        out.append(dab(x, y, rnd.uniform(*length), rnd.uniform(*width), a + rnd.uniform(-jit, jit), rnd.choice(colors),
                       rnd.uniform(*opacity), curve, rnd))
    return "".join(out)


def clip(u, ds):
    ds = [ds] if isinstance(ds, str) else ds
    return f'<clipPath id="{u}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</clipPath>"


def brush(u, ds, box, colors, seed, n=80, **kw):
    """Brush strokes clipped inside one or more shapes."""
    return clip(u, ds) + f'<g clip-path="url(#{u})">' + dabs(colors, seed, box, n, **kw) + "</g>"


def around(cx, cy, k=90):
    """Angle function: strokes run around a centre (k=90) or radiate from it (k=0)."""
    return lambda x, y: math.degrees(math.atan2(y - cy, x - cx)) + k


def body(u, d, box, base, tints, seed, n=None, angle=-80, length=None, width=None, opacity=(0.2, 0.5), curve=0.25,
         line=None, lw=2.4, edge=None, layers=3, spread=1.4, extra_clip=""):
    """The standard gouache treatment: layered wash, strokes following the form, hand-inked outline."""
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    n = n or int(max(30, bw * bh / 260))
    length = length or (max(6, min(bw, bh) * 0.12), max(14, min(bw, bh) * 0.4))
    width = width or (max(1.2, min(bw, bh) * 0.012), max(2.5, min(bw, bh) * 0.035))
    out = [wash(d, base, seed, layers, spread, 0.5, edge)]
    out.append(brush(f"{u}-b", d, (x0 - 10, y0 - 10, x1 + 10, y1 + 10), tints, seed + 1, n, angle=angle, length=length,
                     width=width, opacity=opacity, curve=curve))
    if extra_clip:
        out.append(extra_clip)
    if line:
        out.append(ink(d, line, lw, seed + 2, 2, 0.85))
    return "".join(out)


def shade_in(u, ds, inner, col, op=0.45):
    """Paint `inner` (svg) clipped by shape(s) ds — used for shade sides, rims, pooled colour."""
    return clip(u, ds) + f'<g clip-path="url(#{u})" opacity="{op}">' + inner + "</g>"


def rim_lit(u, d, dx, dy, col, w, op=0.7):
    """Rim light: the shape's outline offset towards the light, kept only inside the shape."""
    return (clip(u, d) + f'<g clip-path="url(#{u})"><path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" '
            f'opacity="{op}" transform="translate({dx} {dy})"/></g>')


def night_sky(u, seed, stops, tints, n=300, angle=-5, length=(50, 150), width=(4, 11), opacity=(0.1, 0.3), box=(0, 0, 600, 600)):
    x0, y0, x1, y1 = box
    return (defs(lg(f"{u}-sky", stops)) + f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{u}-sky)"/>'
            + dabs(tints, seed, (x0 - 80, y0 - 10, x1 + 10, y1 + 10), n, angle, length, width, opacity, 0.12, 8))


def swirl(cx, cy, r0, r1, colors, seed, n=60, width=(3, 9), arc=(40, 130), opacity=(0.15, 0.45), keep=None):
    """Tapered arcs circling a point — the brushed halo around a moon or a lamp."""
    rnd = random.Random(seed)
    out = []
    tries = 0
    while len(out) < n and tries < n * 5:
        tries += 1
        r = rnd.uniform(r0, r1)
        L = rnd.uniform(*arc)
        a0 = rnd.uniform(0, 2 * math.pi)
        da = L / r
        w = rnd.uniform(*width)
        mx, my = cx + r * math.cos(a0 + da / 2), cy + r * math.sin(a0 + da / 2)
        if keep and not keep(mx, my):
            continue
        k = 8
        outer = [(cx + (r + w / 2 * math.sin(math.pi * i / k)) * math.cos(a0 + da * i / k),
                  cy + (r + w / 2 * math.sin(math.pi * i / k)) * math.sin(a0 + da * i / k)) for i in range(k + 1)]
        inner = [(cx + (r - w / 2 * math.sin(math.pi * i / k)) * math.cos(a0 + da * i / k),
                  cy + (r - w / 2 * math.sin(math.pi * i / k)) * math.sin(a0 + da * i / k)) for i in range(k, -1, -1)]
        out.append(f'<path d="M {" L ".join(f"{_f(x)} {_f(y)}" for x, y in outer + inner[1:])} Z" fill="{rnd.choice(colors)}" '
                   f'opacity="{rnd.uniform(*opacity):.2f}"/>')
    return "".join(out)


def stars(seed, box, n, col=BONE, tw=4, keep=None, r=(0.8, 2.0), twr=(5, 9)):
    """Painted star dabs and a few hand-drawn four-point twinkles."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    while len(out) < n:
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if keep and not keep(x, y):
            continue
        rr = rnd.uniform(*r)
        out.append(f'<path d="{blob(x, y, rr, rr * rnd.uniform(0.7, 1), rnd.randrange(999), 0.2, 6)}" fill="{col}" opacity="{rnd.uniform(0.4, 1):.2f}"/>')
    k = 0
    while k < tw:
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if keep and not keep(x, y):
            continue
        k += 1
        out.append(twinkle(x, y, rnd.uniform(*twr), col, rnd.uniform(0.75, 1), rnd.randrange(999)))
    return "".join(out)


def twinkle(x, y, r, col, op=1.0, seed=1):
    rnd = random.Random(seed)
    pts = []
    for i in range(8):
        a = math.radians(-90 + 45 * i)
        rr = r * rnd.uniform(0.85, 1.1) if i % 2 == 0 else r * 0.22
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return f'<path d="{smooth_closed(pts)}" fill="{col}" opacity="{op:.2f}"/>'


def grain_over(u, seed=9, dark="#120A16", light="#FFFFFF", op=1.0):
    rnd = random.Random(seed)
    sp = "".join(f'<circle cx="{rnd.uniform(0, 80):.1f}" cy="{rnd.uniform(0, 80):.1f}" r="{rnd.uniform(0.3, 0.85):.2f}" '
                 f'fill="{rnd.choice([dark, light])}" opacity="{rnd.uniform(0.05, 0.16):.2f}"/>' for _ in range(70))
    fib = "".join(f'<path d="M {rnd.uniform(0, 80):.1f} {rnd.uniform(0, 80):.1f} q {rnd.uniform(-4, 4):.1f} {rnd.uniform(-2, 2):.1f} '
                  f'{rnd.uniform(-8, 8):.1f} {rnd.uniform(-3, 3):.1f}" stroke="{light}" stroke-width="0.5" fill="none" opacity="0.07"/>' for _ in range(8))
    return (defs(f'<pattern id="{u}" width="80" height="80" patternUnits="userSpaceOnUse">{sp}{fib}</pattern>')
            + f'<rect width="600" height="600" fill="url(#{u})" opacity="{op}"/>')


def paper_ground(u, base=PAPER, fleck="#8A6A4A", seed=5):
    return paper(u, base, fleck, seed, 1.2)


def backdrop(u, cx, cy, rx, ry, base, tints, seed, wobble=0.09, n=None, angle=-20, op=1.0):
    """Big loose painted blob behind a subject on paper (like a gouache swatch)."""
    d = blob(cx, cy, rx, ry, seed, wobble, 22)
    n = n or int(rx * ry / 120)
    return (f'<g opacity="{op}">' + wash(d, base, seed, 3, 5, 0.45)
            + brush(f"{u}-bd", d, (cx - rx * 1.2, cy - ry * 1.2, cx + rx * 1.2, cy + ry * 1.2), tints, seed + 1, n, angle=angle,
                    length=(rx * 0.15, rx * 0.5), width=(3, 9), opacity=(0.15, 0.4), curve=0.15)
            + "</g>")


# ---------------------------------------------------------------- lettering
def bword(u, x, y, s, font, size, fill, tints, seed, max_w=470, ls=0, anchor="middle", shadow=None, sd=0.045,
          outline=None, ow=0, angle=-12, density=1.0, bounce=0.0, rot=0.0, hi=None):
    """Brush-painted lettering: the word is the clip for real brush strokes, over a solid base and an offset shadow.
    bounce > 0 sets each letter individually with a small hand-lettered rise/fall and tilt."""
    size = fit_size(s, font, size, max_w, ls)
    w = measure(s, font, size, ls)
    if anchor == "middle":
        x0 = x - w / 2
    elif anchor == "end":
        x0 = x - w
    else:
        x0 = x
    rnd = random.Random(seed)
    glyphs = []
    if bounce or rot:
        cx = x0
        for i, ch in enumerate(s):
            cw = measure(ch, font, size)
            dy = bounce * size * math.sin(i * 1.9 + seed) * 0.06 if bounce else 0
            r = (rnd.uniform(-1, 1) * bounce * 5) if bounce else 0
            glyphs.append((ch, cx, cw, dy, r))
            cx += cw + ls
    attrs = f'{font} font-size="{size}"'

    def txt(dx, dy, extra):
        if glyphs:
            return "".join(f'<text x="{_f(gx + dx)}" y="{_f(y + gy + dy)}" {attrs} transform="rotate({gr:.1f} {_f(gx + cw / 2 + dx)} {_f(y + gy + dy)})"{extra}>{esc(ch)}</text>'
                           for ch, gx, cw, gy, gr in glyphs if ch != " ")
        lsa = f' letter-spacing="{ls}"' if ls else ""
        return f'<text x="{_f(x0 + dx)}" y="{_f(y + dy)}" {attrs}{lsa}{extra}>{esc(s)}</text>'

    out = [f'<g transform="rotate({rot} {_f(x)} {_f(y)})">' if rot else "<g>"]
    if shadow:
        out.append(txt(size * sd, size * sd * 1.1, f' fill="{shadow}"'))
    if outline:
        out.append(txt(0, 0, f' fill="{outline}" stroke="{outline}" stroke-width="{ow}" stroke-linejoin="round"'))
    out.append(txt(0, 0, f' fill="{fill}"'))
    n = int(w * size / 70 * density) + 20
    st = dabs(tints, seed, (x0 - size * 0.3, y - size * 0.95, x0 + w + 5, y + size * 0.15), n, angle,
              (size * 0.2, size * 0.6), (size * 0.025, size * 0.07), (0.22, 0.6), 0.2, 10)
    if hi:
        st += dabs([hi], seed + 7, (x0, y - size * 0.8, x0 + w, y - size * 0.45), int(w / 14), angle, (size * 0.1, size * 0.3),
                   (size * 0.012, size * 0.03), (0.35, 0.7), 0.2, 6)
    out.append(f'<clipPath id="{u}">{txt(0, 0, "")}</clipPath><g clip-path="url(#{u})">{st}</g>')
    out.append("</g>")
    return "".join(out)


def script(x, y, s, size, fill, max_w=470, font=SERIF_IT, ls=0, shadow=None, sd=(2, 3), anchor="middle", rot=0, extra=""):
    size = fit_size(s, font, size, max_w, ls)
    if anchor == "middle" and ls:
        x += ls / 2
    lsa = f' letter-spacing="{ls}"' if ls else ""
    tr = f' transform="rotate({rot} {_f(x)} {_f(y)})"' if rot else ""
    out = []
    if shadow:
        out.append(f'<text x="{_f(x + sd[0])}" y="{_f(y + sd[1])}" text-anchor="{anchor}" {font} font-size="{size}"{lsa} fill="{shadow}"{tr}>{esc(s)}</text>')
    out.append(f'<text x="{_f(x)}" y="{_f(y)}" text-anchor="{anchor}" {font} font-size="{size}"{lsa} fill="{fill}"{tr}{extra}>{esc(s)}</text>')
    return "".join(out)


def brush_rule(x0, x1, y, col, seed, w=3.0, op=0.8):
    """A hand-painted rule: a slightly wavy tapered stroke."""
    rnd = random.Random(seed)
    pts = [(x0 + (x1 - x0) * t, y + rnd.uniform(-1.2, 1.2)) for t in (0, 0.25, 0.5, 0.75, 1)]
    top = [(x, yy - w / 2 * math.sin(math.pi * i / 4) - 0.3) for i, (x, yy) in enumerate(pts)]
    bot = [(x, yy + w / 2 * math.sin(math.pi * i / 4) + 0.3) for i, (x, yy) in reversed(list(enumerate(pts)))]
    return f'<path d="{smooth_closed(top + bot)}" fill="{col}" opacity="{op}"/>'


def label(x, y, s, font, size, fill, ls=4, rule=None, gap=14, line_w=36, seed=1, max_w=470):
    """Small spaced label flanked by painted rules."""
    size = fit_size(s, font, size, max_w, ls)
    w = measure(s, font, size, ls) - ls
    out = [f'<text x="{_f(x + ls / 2)}" y="{_f(y)}" text-anchor="middle" {font} font-size="{size}" letter-spacing="{ls}" fill="{fill}">{esc(s)}</text>']
    if rule:
        mid = y - size * 0.36
        for sgn in (-1, 1):
            a = x + sgn * (w / 2 + gap)
            b = a + sgn * line_w
            out.append(brush_rule(min(a, b), max(a, b), mid, rule, seed + sgn, 3))
            out.append(f'<path d="{blob(b + sgn * 4, mid, 3, 3, seed, 0.2, 6)}" fill="{rule}"/>')
    return "".join(out)


# ---------------------------------------------------------------- painted pieces
def pmoon(u, cx, cy, r, seed, base="#F6DE9E", tints=("#FFF3CC", "#E9C373", "#FBE8B4", "#DDB060"), shade="#C4924A",
          halo="#FFE3A0", halo_r=2.1, halo_op=0.42, line="#B07E38", craters=7):
    rnd = random.Random(seed)
    d = blob(cx, cy, r, r, seed, 0.012, 26)
    out = [glow(f"{u}-mh", cx, cy, r * halo_r, halo, halo_op, 0.3), wash(d, base, seed, 3, 1.2, 0.5)]
    inner = [f'<path d="{blob(cx + r * 0.42, cy + r * 0.38, r * 1.05, r * 1.05, seed + 1, 0.02)}" fill="none" stroke="{shade}" stroke-width="{_f(r * 0.55)}" opacity="0.32"/>']
    for _ in range(4):
        a, dd = rnd.uniform(0, 6.28), rnd.uniform(0.15, 0.55) * r
        rr = r * rnd.uniform(0.16, 0.3)
        inner.append(f'<path d="{blob(cx + dd * math.cos(a), cy + dd * math.sin(a), rr, rr * 0.75, rnd.randrange(999), 0.12, 10)}" fill="{shade}" opacity="0.22"/>')
    inner.append(dabs(list(tints), seed + 3, (cx - r, cy - r, cx + r, cy + r), int(r * 1.3), around(cx, cy), (r * 0.15, r * 0.45),
                      (r * 0.015, r * 0.04), (0.2, 0.5), 0.1, 14))
    for _ in range(craters):
        a, dd = rnd.uniform(0, 6.28), rnd.uniform(0, 0.8) * r
        rr = r * rnd.uniform(0.035, 0.09)
        x, y = cx + dd * math.cos(a), cy + dd * math.sin(a)
        inner.append(f'<path d="{blob(x, y, rr, rr, rnd.randrange(999), 0.15, 8)}" fill="{shade}" opacity="0.4"/>'
                     f'<path d="M {_f(x - rr * 0.6)} {_f(y + rr * 0.9)} Q {_f(x + rr)} {_f(y + rr * 0.9)} {_f(x + rr * 0.95)} {_f(y - rr * 0.5)}" fill="none" '
                     f'stroke="#FFF6DA" stroke-width="{_f(max(1, rr * 0.3))}" opacity="0.65" stroke-linecap="round"/>')
    inner.append(f'<path d="M {_f(cx - r * 0.72)} {_f(cy + r * 0.1)} A {_f(r * 0.76)} {_f(r * 0.76)} 0 0 1 {_f(cx - r * 0.05)} {_f(cy - r * 0.72)}" '
                 f'fill="none" stroke="#FFFBEA" stroke-width="{_f(r * 0.05)}" stroke-linecap="round" opacity="0.55"/>')
    out.append(clip(f"{u}-mc", d) + f'<g clip-path="url(#{u}-mc)">' + "".join(inner) + "</g>")
    if line:
        out.append(ink(d, line, max(1.4, r * 0.012), seed, 2, 0.6))
    return "".join(out)


def cloud(u, x, y, w, h, seed, base, light, dark, tints=None, line=None, lw=2.0, op=1.0, k=6):
    """Storybook cloud: overlapping painted puffs, lit tops, a darker flat underside, one outer ink line."""
    rnd = random.Random(seed)
    puffs = []
    for i in range(k):
        t = (i + 0.5) / k
        r = h * (0.45 + 0.55 * math.sin(math.pi * t) ** 0.8) * rnd.uniform(0.8, 1.05)
        px = x - w / 2 + w * t + rnd.uniform(-w * 0.03, w * 0.03)
        puffs.append((px, y - r * 0.55, r))
    ds = [blob(px, py, r, r * 0.92, rnd.randrange(999), 0.04, 14) for px, py, r in puffs]
    ds.append(blob(x, y - h * 0.12, w * 0.5, h * 0.22, seed + 1, 0.03, 16))
    tints = tints or [light, dark, base]
    out = [f'<g opacity="{op}">']
    if line:
        out.append(f'<g fill="none" stroke="{line}" stroke-width="{lw * 2}" opacity="0.7">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    out.append(f'<g fill="{base}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    inner = [f'<path d="{blob(px - r * 0.18, py - r * 0.22, r * 0.72, r * 0.62, rnd.randrange(999), 0.06, 12)}" fill="{light}" opacity="0.55"/>' for px, py, r in puffs]
    inner.append(f'<rect x="{_f(x - w)}" y="{_f(y - h * 0.18)}" width="{_f(2 * w)}" height="{_f(h)}" fill="{dark}" opacity="0.55"/>')
    for px, py, r in puffs:
        inner.append(dabs(tints, rnd.randrange(999), (px - r, py - r, px + r, py + r), int(r * 0.6), around(px, py), (r * 0.15, r * 0.4),
                          (1.2, 3.2), (0.15, 0.4), 0.1, 8))
    out.append(clip(f"{u}-cl", ds) + f'<g clip-path="url(#{u}-cl)">' + "".join(inner) + "</g>")
    out.append("</g>")
    return "".join(out)


def puff_cloud(u, x, y, w, h, seed, base, tints, line=None, op=1.0, light=None):
    """Storybook cloud: a row of overlapping painted puffs with a flat-ish base."""
    rnd = random.Random(seed)
    pts = []
    k = 7
    for i in range(k + 1):
        t = i / k
        px = x - w / 2 + w * t
        bump = math.sin(math.pi * t) ** 0.7
        pts.append((px, y - h * (0.35 + 0.65 * bump) * rnd.uniform(0.75, 1.1)))
    top = smooth_open(pts)
    d = smooth_closed([(x - w / 2, y)] + pts + [(x + w / 2, y), (x + w * 0.2, y + h * 0.12), (x - w * 0.25, y + h * 0.1)])
    out = [f'<g opacity="{op}">', wash(d, base, seed, 2, 1, 0.5)]
    out.append(brush(f"{u}-cb", d, (x - w / 2, y - h, x + w / 2, y + h * 0.2), tints, seed, int(w * h / 90), angle=-4,
                     length=(w * 0.1, w * 0.3), width=(1.5, 4), opacity=(0.2, 0.5), curve=0.2))
    if light:
        out.append(f'<path d="{top}" fill="none" stroke="{light}" stroke-width="3" opacity="0.6" stroke-linecap="round" transform="translate(0 2)"/>')
    if line:
        out.append(ink(d, line, 1.6, seed, 1, 0.5))
    out.append("</g>")
    return "".join(out)


def limb_d(pts, w0, w1, seed=1):
    """Tapered organic limb along a polyline (for branches, twigs, stems)."""
    rnd = random.Random(seed)
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        nx, ny = -math.sin(ang), math.cos(ang)
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2 * rnd.uniform(0.88, 1.12)
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return smooth_closed(left + right[::-1])


def tree_ds(x, base, h, seed, depth=5, lean=0.0, spread=30, w0=None):
    """Bare spooky tree as a list of tapered limb paths."""
    rnd = random.Random(seed)
    ds = []
    w0 = w0 or h * 0.08

    def limb(x0, y0, ang, L, w, d):
        if d == 0 or L < 4:
            return
        pts = [(x0, y0)]
        a = ang
        for _ in range(3):
            a += rnd.uniform(-14, 14)
            px, py = pts[-1]
            pts.append((px + L / 3 * math.cos(math.radians(a)), py + L / 3 * math.sin(math.radians(a))))
        w1 = w * 0.6
        ds.append(limb_d(pts, w, max(0.8, w1), rnd.randrange(999)))
        x1, y1 = pts[-1]
        kids = 2 if rnd.random() < 0.7 else 3
        for i in range(kids):
            da = rnd.uniform(spread * 0.5, spread * 1.3) * (1 if i % 2 else -1)
            limb(x1, y1, a + da, L * rnd.uniform(0.6, 0.8), w1, d - 1)
        if rnd.random() < 0.35 and d > 2:
            mx, my = pts[1]
            limb(mx, my, a + rnd.choice((-1, 1)) * rnd.uniform(45, 70), L * 0.45, w * 0.5, d - 2)

    ds.append(smooth_closed([(x - w0 * 1.7, base + 2), (x - w0 * 0.55, base - w0 * 0.6), (x - w0 * 0.45, base - w0 * 2.4),
                             (x + w0 * 0.45, base - w0 * 2.4), (x + w0 * 0.6, base - w0 * 0.5), (x + w0 * 1.9, base + 2)]))
    limb(x, base - w0, -90 + lean, h * 0.36, w0, depth)
    return ds


def paint_tree(u, x, base, h, seed, fill=SIL, tints=("#2A2036", "#0E0A14", "#3A2C4A"), rim=None, rim_dx=-1.5, rim_dy=-1, **kw):
    ds = tree_ds(x, base, h, seed, **kw)
    out = [f'<g fill="{fill}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>"]
    out.append(brush(f"{u}-tb", ds, (x - h * 0.6, base - h, x + h * 0.6, base + 4), list(tints), seed, int(h * 1.2),
                     angle=-90, length=(6, 16), width=(1, 2.5), opacity=(0.3, 0.6), curve=0.2))
    if rim:
        out.append(clip(f"{u}-tr", ds) + f'<g clip-path="url(#{u}-tr)" fill="none" stroke="{rim}" stroke-width="2" opacity="0.6" '
                   f'transform="translate({rim_dx} {rim_dy})">' + "".join(f'<path d="{d}" transform="translate({-rim_dx * 2} {-rim_dy * 2})"/>' for d in ds) + "</g>")
    return "".join(out)


def grass_tufts(seed, box, n, colors, h=(8, 18), sw=1.8, op=0.9):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        for _k in range(3):
            hh = rnd.uniform(*h)
            out.append(f'<path d="M {_f(x)} {_f(y)} q {_f(rnd.uniform(-3, 3))} {_f(-hh / 2)} {_f(rnd.uniform(-6, 6))} {_f(-hh)}" stroke="{rnd.choice(colors)}"/>')
            x += rnd.uniform(-3, 3)
    return f'<g fill="none" stroke-width="{sw}" stroke-linecap="round" opacity="{op}">' + "".join(out) + "</g>"


def ghost(u, cx, top, w, h, seed, lean=0.0, face="smile", arms=(1, 1), base="#F7F1E6",
          tints=("#FFFFFF", "#E9DFF3", "#D3C5E8", "#FFF7EA"), shade="#B7A6D8", line=INKN, blush="#F2A0A8", lw=2.6,
          arm_up=(0, 0), look=(0, 0), scallops=3):
    """Painted storybook ghost. top = top of dome, h = full height to hem tips."""
    r = w / 2
    pts = []
    for i in range(9):
        a = math.radians(180 + 180 * i / 8)
        pts.append((cx + r * math.cos(a), top + r + r * math.sin(a) * 1.04))
    flare = 0.2

    def side(t, sgn):
        yy = top + r + (h - r) * t
        return (cx + sgn * r * (1 + flare * t + 0.07 * math.sin(math.pi * t)) + lean * (yy - top - r), yy)

    for t in (0.3, 0.58, 0.82):
        pts.append(side(t, 1))
    hy = top + h
    xr = cx + r * (1 + flare) + lean * (h - r)
    xl = cx - r * (1 + flare) + lean * (h - r)
    k = scallops
    for i in range(2 * k + 1):
        t = i / (2 * k)
        pts.append((xr + (xl - xr) * t, hy - (0 if i % 2 == 0 else h * 0.1) + (h * 0.02 if i in (0, 2 * k) else 0)))
    for t in (0.82, 0.58, 0.3):
        pts.append(side(t, -1))
    pts = jitter(pts, seed, w * 0.006)
    d = smooth_closed(pts)
    out = []
    # arms: little mitten nubs tucked behind the body edge
    arm_ds = []
    for sgn, on, up in ((-1, arms[0], arm_up[0]), (1, arms[1], arm_up[1])):
        if not on:
            continue
        ax, ay = side(0.45 - up * 0.08, sgn)
        th = math.radians(-22 + up * 70)      # direction the arm points, degrees above horizontal
        ax -= sgn * w * 0.03
        arm_ds.append(blob(ax + sgn * math.cos(th) * w * 0.1, ay - math.sin(th) * w * 0.1, w * 0.13, w * 0.072, seed + 50 + sgn, 0.05, 12,
                           rot=-sgn * math.degrees(th)))
    for i, ad in enumerate(arm_ds):
        out.append(body(f"{u}-a{i}", ad, (cx - w, top, cx + w, top + h), base, list(tints), seed + 10 + i, n=14,
                        angle=0, length=(6, 14), width=(1, 2.5), line=line, lw=lw * 0.85))
    out.append(wash(d, base, seed, 3, 1.2, 0.5))
    inner = [f'<path d="{blob(cx + r * 0.9 + lean * h * 0.5, top + h * 0.62, r * 0.75, h * 0.6, seed + 3, 0.08)}" fill="{shade}" opacity="0.5"/>',
             f'<path d="{blob(cx + lean * h, top + h * 1.02, r * 1.4, h * 0.14, seed + 4, 0.1)}" fill="{shade}" opacity="0.55"/>',
             dabs(list(tints), seed + 5, (cx - r * 1.3, top, cx + r * 1.3 + lean * h, top + h), int(w * h / 130), lambda x, y: -90 + lean * 40,
                  (h * 0.08, h * 0.3), (w * 0.012, w * 0.03), (0.12, 0.34), 0.2, 10),
             f'<path d="M {_f(cx - r * 0.62)} {_f(top + r * 0.75)} Q {_f(cx - r * 0.55)} {_f(top + r * 0.2)} {_f(cx - r * 0.05)} {_f(top + r * 0.12)}" '
             f'fill="none" stroke="#FFFFFF" stroke-width="{_f(w * 0.045)}" stroke-linecap="round" opacity="0.8"/>']
    out.append(clip(f"{u}-gc", d) + f'<g clip-path="url(#{u}-gc)">' + "".join(inner) + "</g>")
    out.append(ink(d, line, lw, seed, 2, 0.85))
    # face
    fx, fy = cx + look[0] * w * 0.08 + lean * r * 0.6, top + r * 1.02 + look[1] * w * 0.05
    ex = w * 0.17
    er = w * 0.068
    if face in ("smile", "oh", "sleepy", "happy"):
        for sgn in (-1, 1):
            exx = fx + sgn * ex
            if face in ("sleepy", "happy"):
                out.append(ink(f"M {_f(exx - er)} {_f(fy)} Q {_f(exx)} {_f(fy + (er if face == 'sleepy' else -er) * 1.2)} {_f(exx + er)} {_f(fy)}", line, w * 0.035, seed + sgn, 1, 1))
            else:
                out.append(f'<path d="{blob(exx, fy, er, er * 1.3, seed + sgn, 0.05, 12)}" fill="{line}"/>'
                           f'<circle cx="{_f(exx - er * 0.3)}" cy="{_f(fy - er * 0.45)}" r="{_f(er * 0.36)}" fill="#FFFFFF"/>'
                           f'<circle cx="{_f(exx + er * 0.3)}" cy="{_f(fy + er * 0.4)}" r="{_f(er * 0.15)}" fill="#FFFFFF" opacity="0.8"/>')
        if blush:
            for sgn in (-1, 1):
                out.append(f'<path d="{blob(fx + sgn * ex * 1.55, fy + er * 1.9, er * 1.0, er * 0.6, seed + 30 + sgn, 0.1, 10)}" fill="{blush}" opacity="0.55"/>')
        my = fy + er * 2.0
        if face == "oh":
            out.append(f'<path d="{blob(fx, my + er * 0.4, er * 0.6, er * 0.85, seed + 40, 0.08, 10)}" fill="{line}"/>'
                       f'<path d="{blob(fx, my + er * 0.75, er * 0.35, er * 0.3, seed + 41, 0.1, 8)}" fill="#E07A8A"/>')
        else:
            out.append(ink(f"M {_f(fx - er * 0.9)} {_f(my)} Q {_f(fx)} {_f(my + er * 1.3)} {_f(fx + er * 0.9)} {_f(my)}", line, w * 0.03, seed + 42, 1, 1))
    return "".join(out)


def jack(u, cx, cy, w, h, seed, face="classic", lit=True, body_c=PUMPKIN, dark=PUMPKIN_D, light=PUMPKIN_L, glow_r=None,
         glow_op=0.45, inner=("#FFF2B8", "#FFC94A", "#F08A1E"), leaf="#6E8A3E", stem="#6B5A2E"):
    """Painted jack-o'-lantern: gouache pumpkin with a candle-lit carved face."""
    out = []
    if lit and glow_r:
        out.append(glow(f"{u}-jg", cx, cy, glow_r, "#FFB547", glow_op, 0.35))
    out.append(painted_pumpkin(f"{u}-pp", cx, cy, w, h, seed, body_c, dark, light, stem, leaf))
    if face:
        shapes = FACES[face]
        ds = [smooth_closed([(cx + x * w * 0.95, cy + y * h * 1.0) for x, y in pts]) if len(pts) > 3 else
              "M " + " L ".join(f"{_f(cx + x * w * 0.95)} {_f(cy + y * h)}" for x, y in pts) + " Z" for pts in shapes]
        if lit:
            out.append(defs(rg(f"{u}-jf", [(0, inner[0]), (0.45, inner[1]), (1, inner[2])], cy=0.55, r=0.6)))
            for i, d in enumerate(ds):
                out.append(f'<path d="{d}" fill="url(#{u}-jf)" stroke="#7A2E10" stroke-width="{_f(max(1.4, w * 0.012))}" stroke-linejoin="round"/>')
                out.append(f'<path d="{d}" fill="none" stroke="#FFF4C8" stroke-width="{_f(max(1, w * 0.008))}" opacity="0.6" transform="translate(0 {_f(-w * 0.008)})"/>')
        else:
            for d in ds:
                out.append(f'<path d="{d}" fill="#4A1E0C" stroke="#7A2E10" stroke-width="1.6"/>')
    return "".join(out)


def candle(u, x, base, h, w, seed, wax=BONE, tints=("#FFFFFF", "#E8D9BC", "#F9EFD8", "#D8C4A0"), line="#6A4A3A", lit=True,
           glow_r=None, glow_op=0.55, flame_h=None):
    """Painted pillar candle with drips and a glowing flame."""
    rnd = random.Random(seed)
    top = base - h
    pts = [(x - w / 2, base), (x - w / 2 - 1, top + h * 0.5)]
    # top rim with drips
    k = 5
    for i in range(k + 1):
        t = i / k
        px = x - w / 2 + w * t
        drip = rnd.uniform(0.05, 0.35) * h if (i in (1, 3, 4) and rnd.random() < 0.8) else 0
        if drip:
            pts += [(px - w * 0.06, top + 2), (px, top + drip), (px + w * 0.06, top + 2)]
        else:
            pts.append((px, top + rnd.uniform(-1.5, 1.5)))
    pts += [(x + w / 2 + 1, top + h * 0.5), (x + w / 2, base)]
    d = smooth_closed(jitter(pts, seed, 0.6))
    out = []
    fh = flame_h or w * 0.9
    fy = top - 3
    if lit:
        out.append(glow(f"{u}-cg", x, fy - fh * 0.4, glow_r or w * 3, "#FFD27A", glow_op, 0.3))
    out.append(body(f"{u}-cw", d, (x - w / 2, top, x + w / 2, base), wax, list(tints), seed, n=int(w * h / 50), angle=-90,
                    length=(h * 0.1, h * 0.4), width=(1, w * 0.06), line=line, lw=1.8))
    out.append(shade_in(f"{u}-cs", d, f'<rect x="{_f(x + w * 0.15)}" y="{_f(top - 10)}" width="{_f(w)}" height="{_f(h + 20)}" fill="#B49870"/>', "#000", 0.35))
    out.append(f'<path d="M {_f(x - w * 0.28)} {_f(top + h * 0.2)} L {_f(x - w * 0.3)} {_f(base - h * 0.15)}" stroke="#FFFFFF" stroke-width="{_f(w * 0.08)}" stroke-linecap="round" opacity="0.6"/>')
    out.append(f'<path d="M {_f(x)} {_f(top + 1)} q 1 -5 0 -9" stroke="#3A2418" stroke-width="2" fill="none" stroke-linecap="round"/>')
    if lit:
        fd = (f"M {_f(x)} {_f(fy - fh)} C {_f(x + fh * 0.12)} {_f(fy - fh * 0.6)} {_f(x + fh * 0.36)} {_f(fy - fh * 0.25)} {_f(x + fh * 0.2)} {_f(fy - fh * 0.05)} "
              f"Q {_f(x)} {_f(fy + fh * 0.1)} {_f(x - fh * 0.2)} {_f(fy - fh * 0.05)} C {_f(x - fh * 0.36)} {_f(fy - fh * 0.25)} {_f(x - fh * 0.1)} {_f(fy - fh * 0.6)} {_f(x)} {_f(fy - fh)} Z")
        out.append(defs(rg(f"{u}-fl", [(0, "#FFFFFF"), (0.35, "#FFF1A8"), (0.75, "#FFB52E"), (1, "#F07A1A")], cy=0.7, r=0.65)))
        out.append(f'<path d="{fd}" fill="url(#{u}-fl)"/>')
    return "".join(out)


def bat(u, cx, cy, s, seed, rot=0, flap=0.0, body_c=PLUM, wing=("#2C2148", "#1E1634"), rim=LILAC, face=True, line=INKN):
    """Small painted flying bat; s = half wingspan."""
    k = s / 96
    w_d = "M 8 -8 C 26 -26 52 -34 72 -30 L 96 -40 Q 90 -18 84 -6 Q 74 -15 63 -3 Q 52 -14 42 0 Q 30 -9 20 6 Q 13 1 8 6 Z"
    out = [f'<g transform="translate({_f(cx)} {_f(cy)}) rotate({rot}) scale({k:.3f})">']
    for sx in (1, -1):
        out.append(f'<g transform="scale({sx} 1) rotate({-flap * 20:.1f})">'
                   + wash(w_d, wing[0], seed, 2, 1.2, 0.5)
                   + brush(f"{u}-w{sx + 1}", w_d, (0, -45, 100, 10), [wing[1], "#3E3060", "#4A3A70"], seed + sx, 22, angle=-12,
                           length=(14, 34), width=(2, 4), opacity=(0.3, 0.6), curve=0.2)
                   + f'<path d="M 10 -6 L 42 0 M 22 -18 L 62 -3 M 40 -24 L 84 -6" stroke="{rim}" stroke-width="{1.6 / k * 0.5:.1f}" fill="none" opacity="0.45" stroke-linecap="round"/>'
                   + f'<path d="M 8 -8 C 26 -26 52 -34 72 -30 L 96 -40" stroke="{rim}" stroke-width="{2.2 / k * 0.5:.1f}" fill="none" opacity="0.7" stroke-linecap="round"/>'
                   + "</g>")
    bd = blob(0, 4, 14, 19, seed, 0.06, 12)
    hd = smooth_closed([(-12, -8), (-12, -22), (-9, -34), (-4, -24), (4, -24), (9, -34), (12, -22), (12, -8), (0, -2)])
    out.append(body(f"{u}-bb", bd, (-16, -16, 16, 24), body_c, ["#6A4A8E", "#3A2456", "#7A5AA0"], seed, n=18, angle=-90,
                    length=(4, 10), width=(1, 2), line=None))
    out.append(body(f"{u}-bh", hd, (-14, -36, 14, -2), body_c, ["#6A4A8E", "#3A2456", "#7A5AA0"], seed + 1, n=14, angle=-90,
                    length=(4, 9), width=(1, 2), line=None))
    if face:
        out.append('<circle cx="-4.5" cy="-14" r="2.6" fill="#FFF4D6"/><circle cx="4.5" cy="-14" r="2.6" fill="#FFF4D6"/>'
                   '<circle cx="-4" cy="-13.6" r="1.3" fill="#1A1020"/><circle cx="5" cy="-13.6" r="1.3" fill="#1A1020"/>')
    out.append("</g>")
    return "".join(out)


def web(u, cx, cy, spokes, rings, seed, col=BONE, sw=2.0, op=0.85, sag=0.18, dew=True, a0=0, a1=360):
    """Hand-inked spider web: wobbly spokes, sagging rings, a few dew dots."""
    rnd = random.Random(seed)
    angs = []
    n = len(spokes)
    for i in range(n):
        angs.append(math.radians(a0 + (a1 - a0) * i / max(1, n - (0 if a1 - a0 >= 360 else 1)) + rnd.uniform(-3, 3)))
    out = []
    for a, L in zip(angs, spokes):
        pts = [(cx + L * t * math.cos(a) + rnd.uniform(-1.5, 1.5), cy + L * t * math.sin(a) + rnd.uniform(-1.5, 1.5)) for t in (0, 0.35, 0.7, 1)]
        out.append(ink(smooth_open(pts), col, sw, rnd.randrange(999), 1, op))
    full = a1 - a0 >= 360
    for rr in rings:
        segs = n if full else n - 1
        for i in range(segs):
            j = (i + 1) % n
            a, b = angs[i], angs[j]
            ra, rb = min(rr, spokes[i]), min(rr, spokes[j])
            p0 = (cx + ra * math.cos(a), cy + ra * math.sin(a))
            p1 = (cx + rb * math.cos(b), cy + rb * math.sin(b))
            mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
            # sag towards the centre
            mx += (cx - mx) * sag
            my += (cy - my) * sag
            out.append(ink(f"M {_f(p0[0])} {_f(p0[1])} Q {_f(mx)} {_f(my)} {_f(p1[0])} {_f(p1[1])}", col, sw * 0.8, rnd.randrange(999), 1, op * 0.9))
            if dew and rnd.random() < 0.18:
                out.append(f'<circle cx="{_f((p0[0] + 2 * mx + p1[0]) / 4)}" cy="{_f((p0[1] + 2 * my + p1[1]) / 4)}" r="{_f(rnd.uniform(1.6, 2.8))}" fill="#FFFFFF" opacity="0.85"/>')
    return "".join(out)


def spider(u, cx, cy, r, seed, body_c="#3A2C4E", tints=("#5A4A70", "#241A32", "#6E5A88"), line=INKN, thread=None, thread_top=None,
           face=True, legs_c="#241A30"):
    """Cute painted spider hanging (optionally on a thread)."""
    out = []
    if thread is not None:
        out.append(ink(f"M {_f(cx)} {_f(thread_top)} L {_f(cx + 0.5)} {_f(cy - r)}", thread, 1.8, seed, 1, 0.9))
    for sgn in (-1, 1):
        for i, (a, L) in enumerate(((-40, 1.9), (-12, 2.1), (14, 2.0), (40, 1.7))):
            ax = math.radians(a)
            kx, ky = cx + sgn * r * 1.25 * math.cos(ax), cy + r * 1.0 * math.sin(ax) - r * 0.5
            ex, ey = cx + sgn * r * L * math.cos(ax), cy + r * L * 0.7 * math.sin(ax) + r * 0.55
            out.append(ink(f"M {_f(cx + sgn * r * 0.4)} {_f(cy + r * 0.05 * i)} Q {_f(kx)} {_f(ky - r * 0.4)} {_f(ex)} {_f(ey)}", legs_c, max(2, r * 0.13), seed + i, 1, 1))
    d = blob(cx, cy, r, r * 0.95, seed, 0.04, 14)
    out.append(body(f"{u}-sp", d, (cx - r, cy - r, cx + r, cy + r), body_c, list(tints), seed, n=int(r * 2), angle=around(cx, cy),
                    length=(r * 0.25, r * 0.6), width=(1, r * 0.08), line=line, lw=max(1.5, r * 0.06)))
    out.append(f'<path d="M {_f(cx - r * 0.55)} {_f(cy - r * 0.35)} Q {_f(cx - r * 0.3)} {_f(cy - r * 0.75)} {_f(cx + r * 0.15)} {_f(cy - r * 0.72)}" stroke="#C9B8EA" '
               f'stroke-width="{_f(r * 0.12)}" fill="none" stroke-linecap="round" opacity="0.6"/>')
    if face:
        er = r * 0.2
        for sgn in (-1, 1):
            ex = cx + sgn * r * 0.33
            out.append(f'<circle cx="{_f(ex)}" cy="{_f(cy + r * 0.02)}" r="{_f(er)}" fill="#FFF7E6"/><circle cx="{_f(ex + er * 0.15)}" cy="{_f(cy + r * 0.06)}" r="{_f(er * 0.55)}" fill="#1A1020"/>'
                       f'<circle cx="{_f(ex - er * 0.1)}" cy="{_f(cy - er * 0.2)}" r="{_f(er * 0.2)}" fill="#FFFFFF"/>')
        out.append(ink(f"M {_f(cx - r * 0.22)} {_f(cy + r * 0.42)} Q {_f(cx)} {_f(cy + r * 0.62)} {_f(cx + r * 0.22)} {_f(cy + r * 0.42)}", "#FFF4E0", max(1.4, r * 0.07), seed, 1, 0.9))
        for sgn in (-1, 1):
            out.append(f'<path d="{blob(cx + sgn * r * 0.58, cy + r * 0.38, r * 0.14, r * 0.09, seed + sgn, 0.1, 8)}" fill="#E890A8" opacity="0.6"/>')
    return "".join(out)


def leaf_fall(seed, box, n, cols=("#D9622A", "#E8A23A", "#B8442A", "#C9862E"), s=(9, 15), keep=None):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    while len(out) < n:
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if keep and not keep(x, y):
            continue
        c = rnd.choice(cols)
        out.append(maple_leaf(x, y, rnd.uniform(*s), c, "#7A2E14", rnd.uniform(-60, 60), rnd.randrange(999)))
    return "".join(out)


def plank(u, d, box, base, tints, seed, angle=0, grain_c="#3A2418", knots=1, line=INK, lw=2.0, n=None):
    """Painted wood: wash, long strokes along the grain, a few inked grain lines and knots."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = [body(f"{u}-pk", d, box, base, list(tints), seed, n=n or int((x1 - x0) * (y1 - y0) / 140), angle=angle,
                length=((x1 - x0) * 0.1, (x1 - x0) * 0.35) if angle == 0 else ((y1 - y0) * 0.1, (y1 - y0) * 0.35),
                width=(1.2, 3.5), opacity=(0.25, 0.6), curve=0.08, line=None)]
    g = []
    horiz = abs(angle) < 45
    for i in range(4):
        if horiz:
            yy = y0 + (y1 - y0) * (0.2 + 0.2 * i) + rnd.uniform(-3, 3)
            g.append(f"M {_f(x0 - 5)} {_f(yy)} C {_f(x0 + (x1 - x0) * 0.3)} {_f(yy + rnd.uniform(-4, 4))} {_f(x0 + (x1 - x0) * 0.6)} {_f(yy + rnd.uniform(-4, 4))} {_f(x1 + 5)} {_f(yy + rnd.uniform(-2, 2))}")
        else:
            xx = x0 + (x1 - x0) * (0.2 + 0.2 * i) + rnd.uniform(-2, 2)
            g.append(f"M {_f(xx)} {_f(y0 - 5)} C {_f(xx + rnd.uniform(-3, 3))} {_f(y0 + (y1 - y0) * 0.3)} {_f(xx + rnd.uniform(-3, 3))} {_f(y0 + (y1 - y0) * 0.6)} {_f(xx)} {_f(y1 + 5)}")
    kn = ""
    for _ in range(knots):
        kx, ky = rnd.uniform(x0 + 15, x1 - 15), rnd.uniform(y0 + 5, y1 - 5)
        kn += f'<path d="{blob(kx, ky, 5 if horiz else 3, 3 if horiz else 5, rnd.randrange(999), 0.15, 8)}" fill="none" stroke="{grain_c}" stroke-width="1.4" opacity="0.5"/>'
    out.append(clip(f"{u}-pg", d) + f'<g clip-path="url(#{u}-pg)" fill="none" stroke="{grain_c}" stroke-width="1.1" opacity="0.35">'
               + "".join(f'<path d="{p}"/>' for p in g) + "</g>" + f'<g clip-path="url(#{u}-pg)">{kn}</g>')
    if line:
        out.append(ink(d, line, lw, seed, 2, 0.8))
    return "".join(out)


def ground(u, pts, base_y, fill, tints, seed, angle=-3, n=None, line=None, rim=None):
    """Painted hill / ground mass from a top edge of points down to base_y."""
    d = smooth_open(pts) + f" L {_f(pts[-1][0])} {base_y} L {_f(pts[0][0])} {base_y} Z"
    x0 = min(p[0] for p in pts)
    x1 = max(p[0] for p in pts)
    y0 = min(p[1] for p in pts)
    out = [f'<path d="{d}" fill="{fill}"/>',
           brush(f"{u}-gr", d, (x0, y0 - 5, x1, base_y), list(tints), seed, n or int((x1 - x0) * (base_y - y0) / 180), angle=angle,
                 length=(20, 70), width=(2, 6), opacity=(0.2, 0.5), curve=0.1)]
    if rim:
        out.append(f'<path d="{smooth_open(pts)}" fill="none" stroke="{rim}" stroke-width="2.4" opacity="0.55" stroke-linecap="round" transform="translate(0 1.5)"/>')
    if line:
        out.append(ink(smooth_open(pts), line, 2, seed, 1, 0.6))
    return "".join(out)


# ================================================================ designs
DESIGNS = {}


def design(slug):
    def deco(fn):
        DESIGNS[slug] = fn
        return fn
    return deco


# ---------------------------------------------------------------- hang in there
def hanging_bat(u, fx, fy, s, seed, fur="#5E3E84", fur_t=("#7A5AA2", "#3E2660", "#8A6CB4", "#4A2E6E"), belly="#9A7CC0",
                wing="#2A1F48", wing_t=("#3C2E62", "#1C1434", "#4A3A74"), rim=LILAC, line="#1C1228"):
    out = []
    # feet gripping the branch
    for sgn in (-1, 1):
        out.append(ink(f"M {_f(fx + sgn * 6)} {_f(fy + 0.13 * s)} L {_f(fx + sgn * 7)} {_f(fy + 4)} q {_f(-sgn * 1)} -9 {_f(sgn * 8)} -10", line, 3.2, seed + sgn, 1, 1))
    bd = blob(fx, fy + 0.36 * s, 0.17 * s, 0.25 * s, seed, 0.05, 16)
    out.append(body(f"{u}-bd", bd, (fx - 0.2 * s, fy + 0.1 * s, fx + 0.2 * s, fy + 0.62 * s), fur, list(fur_t), seed, n=70, angle=90,
                    length=(0.03 * s, 0.08 * s), width=(1, 2.2), opacity=(0.35, 0.7), line=line, lw=2.2))
    out.append(f'<path d="{blob(fx, fy + 0.4 * s, 0.07 * s, 0.17 * s, seed + 1, 0.08, 12)}" fill="{belly}" opacity="0.75"/>')
    out.append(dabs(["#B9A0D8", "#7A5AA2"], seed + 2, (fx - 0.06 * s, fy + 0.25 * s, fx + 0.06 * s, fy + 0.55 * s), 26, 90, (4, 9), (0.8, 1.6), (0.4, 0.8), 0.3))
    # wings, folded like a cloak
    for sgn in (-1, 1):
        S = lambda dx, dy: (fx + sgn * dx * s, fy + dy * s)  # noqa: E731
        pts = [S(0.07, 0.13), S(0.2, 0.12), S(0.31, 0.15), S(0.36, 0.3), S(0.29, 0.36), S(0.35, 0.48), S(0.26, 0.53),
               S(0.28, 0.64), S(0.17, 0.62), S(0.1, 0.66), S(0.085, 0.5), S(0.1, 0.3)]
        d = smooth_closed(jitter(pts, seed + sgn, 1.0))
        out.append(body(f"{u}-w{sgn + 1}", d, (fx - 0.4 * s, fy + 0.1 * s, fx + 0.4 * s, fy + 0.7 * s), wing, list(wing_t), seed + 5 + sgn,
                        n=60, angle=lambda x, y: 70 if sgn < 0 else 110, length=(0.05 * s, 0.14 * s), width=(1.2, 3), opacity=(0.3, 0.6), line=line, lw=2.4))
        # finger bones and the lit upper edge
        bones = "".join(ink(f"M {_f(S(0.21, 0.14)[0])} {_f(S(0.21, 0.14)[1])} Q {_f(S(a, b)[0])} {_f(S(a, b)[1])} {_f(S(c, e)[0])} {_f(S(c, e)[1])}", rim, 1.6, seed + i, 1, 0.5)
                        for i, (a, b, c, e) in enumerate(((0.3, 0.25, 0.3, 0.36), (0.25, 0.4, 0.27, 0.52), (0.18, 0.5, 0.17, 0.61))))
        out.append(bones)
        out.append(ink(smooth_open([S(0.08, 0.135), S(0.2, 0.12), S(0.31, 0.15), S(0.355, 0.29)]), rim, 2.2, seed, 1, 0.7))
        cx_, cy_ = S(0.31, 0.15)
        out.append(ink(f"M {_f(cx_)} {_f(cy_)} q {_f(sgn * 4)} -6 {_f(sgn * 1)} -11", line, 2.4, seed, 1, 1))
    # head (hanging, so ears point down) with an upright cute face
    hy = fy + 0.73 * s
    ears = []
    for sgn in (-1, 1):
        ears.append(smooth_closed([(fx + sgn * 0.05 * s, hy + 0.1 * s), (fx + sgn * 0.17 * s, hy + 0.27 * s), (fx + sgn * 0.16 * s, hy + 0.06 * s)]))
    hd = blob(fx, hy, 0.165 * s, 0.15 * s, seed + 9, 0.04, 16)
    for i, e in enumerate(ears):
        out.append(body(f"{u}-e{i}", e, (fx - 0.2 * s, hy, fx + 0.2 * s, hy + 0.3 * s), fur, list(fur_t), seed + 20 + i, n=14, angle=90,
                        length=(4, 9), width=(1, 2), line=line, lw=2.2))
        out.append(f'<path d="{smooth_closed([(fx + (i * 2 - 1) * 0.08 * s, hy + 0.11 * s), (fx + (i * 2 - 1) * 0.15 * s, hy + 0.22 * s), (fx + (i * 2 - 1) * 0.145 * s, hy + 0.09 * s)])}" fill="#D99AB8" opacity="0.7"/>')
    out.append(body(f"{u}-hd", hd, (fx - 0.17 * s, hy - 0.16 * s, fx + 0.17 * s, hy + 0.16 * s), fur, list(fur_t), seed + 9, n=50,
                    angle=around(fx, hy, 0), length=(4, 9), width=(1, 2), opacity=(0.35, 0.7), line=line, lw=2.4))
    out.append(f'<path d="{blob(fx, hy - 0.04 * s, 0.11 * s, 0.07 * s, seed + 10, 0.06, 12)}" fill="{belly}" opacity="0.55"/>')
    er = 0.042 * s
    for sgn in (-1, 1):
        ex, ey = fx + sgn * 0.065 * s, hy - 0.01 * s
        out.append(f'<path d="{blob(ex, ey, er, er * 1.15, seed + sgn, 0.05, 12)}" fill="#1A1020"/>'
                   f'<circle cx="{_f(ex - er * 0.3)}" cy="{_f(ey - er * 0.4)}" r="{_f(er * 0.38)}" fill="#FFFFFF"/>'
                   f'<circle cx="{_f(ex + er * 0.35)}" cy="{_f(ey + er * 0.4)}" r="{_f(er * 0.16)}" fill="#FFFFFF" opacity="0.8"/>')
        out.append(f'<path d="{blob(fx + sgn * 0.115 * s, hy + 0.045 * s, 0.03 * s, 0.018 * s, seed + 3 + sgn, 0.1, 8)}" fill="#F29AB4" opacity="0.7"/>')
    my = hy + 0.05 * s
    out.append(ink(f"M {_f(fx - 0.03 * s)} {_f(my)} Q {_f(fx)} {_f(my + 0.03 * s)} {_f(fx + 0.03 * s)} {_f(my)}", line, 2.2, seed, 1, 1))
    out.append(f'<path d="M {_f(fx - 0.018 * s)} {_f(my + 0.008 * s)} l 2.4 5 l 2.4 -4.4 Z M {_f(fx + 0.018 * s)} {_f(my + 0.008 * s)} l -2.4 5 l -2.4 -4.4 Z" fill="#FFFFFF"/>')
    return "".join(out)


@design("hang-in-there")
def d_hang_in_there():
    u = "hgb-hit"
    out = [night_sky(u, 11, [(0, "#120F2A"), (0.5, "#241C46"), (0.8, "#36265A"), (1, "#1A1430")],
                     ["#2E2556", "#3B2E66", "#1A1636", "#4A3670", "#2A2050"], n=320)]
    mx, my, mr = 300, 262, 148
    out.append(swirl(mx, my, mr + 10, mr + 130, ["#5B4888", "#7A66A8", "#3E3170", "#4E3E80", "#C9A86A"], 12, n=110,
                     width=(3, 9), arc=(40, 120), opacity=(0.12, 0.38)))
    out.append(stars(13, (20, 20, 580, 420), 40, BONE, 6, keep=lambda x, y: math.hypot(x - mx, y - my) > mr + 30))
    out.append(pmoon(u, mx, my, mr, 14))
    # far clouds drifting across the moon's lower edge
    out.append(cloud(f"{u}-c2", 498, 372, 210, 46, 16, "#5A4790", "#9C88CC", "#2E2458", line="#1A1430"))
    out.append(cloud(f"{u}-c1", 104, 392, 240, 52, 15, "#4E3D82", "#8E7AC0", "#2A2050", line="#1A1430"))
    # branch across the top
    br = [(-30, 160), (60, 150), (160, 136), (250, 127), (330, 120), (420, 100), (510, 78), (630, 56)]
    ds = [limb_d(br, 40, 9, 17),
          limb_d([(150, 140), (138, 112), (118, 90), (104, 80)], 12, 3, 18),
          limb_d([(415, 104), (440, 78), (470, 58), (500, 48)], 11, 3, 19),
          limb_d([(505, 82), (535, 96), (560, 112)], 8, 2.5, 20),
          limb_d([(250, 128), (232, 112), (226, 98)], 7, 2, 21)]
    out.append(f'<g fill="{SIL}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    out.append(brush(f"{u}-br", ds, (-30, 40, 630, 180), ["#3A2C4C", "#0C0812", "#4A3A5E", "#2A1E36"], 22, 160, angle=-12,
                     length=(14, 40), width=(1.2, 3.5), opacity=(0.35, 0.7), curve=0.1))
    out.append(ink(smooth_open([(-30, 141), (60, 131), (160, 118), (250, 109), (330, 103), (420, 84), (510, 67), (630, 47)]), LILAC, 2.6, 23, 1, 0.55))
    for d in ds:
        out.append(ink(d, "#0A0610", 1.6, 24, 1, 0.8))
    out.append(maple_leaf(104, 74, 16, "#D9622A", "#7A2E14", -30, 1))
    out.append(maple_leaf(500, 42, 15, "#E8A23A", "#8A4A14", 20, 2))
    out.append(maple_leaf(560, 116, 13, "#B8442A", "#6A2010", 70, 3))
    out.append(maple_leaf(226, 94, 11, "#E8A23A", "#8A4A14", -10, 4))
    out.append(hanging_bat(u, 300, 116, 248, 25))
    out.append(leaf_fall(26, (60, 180, 540, 360), 3, keep=lambda x, y: abs(x - 300) > 90))
    # dark ground for the lettering
    out.append(defs(lg(f"{u}-fg", [(0, NIGHT, 0), (0.45, NIGHT, 0.75), (1, "#0E0B1E", 0.95)])) + f'<rect y="390" width="600" height="210" fill="url(#{u}-fg)"/>')
    out.append(script(300, 452, "hang in", 72, BONE, 420, shadow="#0A0714", sd=(2, 4)))
    out.append(bword(f"{u}-t", 300, 534, "THERE", ANTON, 90, GOLD, ["#FFE29A", "#E8792E", "#FFD06A", "#C9601E"], 27, max_w=400, ls=10,
                     shadow="#6A2A10", hi="#FFF2C0"))
    out.append(grain_over(f"{u}-gr", 28))
    return "".join(out)


# ---------------------------------------------------------------- small painted props
def candy_corn(u, x, y, s, rot, seed, line=INK):
    """Painted candy corn kernel; s = height."""
    pts = [(0, -0.5), (0.2, -0.2), (0.38, 0.22), (0.4, 0.42), (0, 0.5), (-0.4, 0.42), (-0.38, 0.22), (-0.2, -0.2)]
    d = smooth_closed(jitter([(x + px * s, y + py * s) for px, py in pts], seed, s * 0.01))
    inner = (f'<rect x="{_f(x - s)}" y="{_f(y - s)}" width="{_f(2 * s)}" height="{_f(2 * s)}" fill="#FFF6E2"/>'
             f'<rect x="{_f(x - s)}" y="{_f(y - 0.18 * s)}" width="{_f(2 * s)}" height="{_f(2 * s)}" fill="#F28A2E"/>'
             f'<rect x="{_f(x - s)}" y="{_f(y + 0.2 * s)}" width="{_f(2 * s)}" height="{_f(2 * s)}" fill="#F6C83E"/>'
             + dabs(["#FFFFFF", "#E06A1E", "#FFE07A", "#D9A02A"], seed, (x - s * 0.5, y - s * 0.5, x + s * 0.5, y + s * 0.5), 18, -90,
                    (s * 0.15, s * 0.4), (s * 0.02, s * 0.05), (0.25, 0.5), 0.2)
             + f'<path d="M {_f(x - s * 0.12)} {_f(y - s * 0.25)} L {_f(x - s * 0.24)} {_f(y + s * 0.3)}" stroke="#FFFFFF" stroke-width="{_f(s * 0.07)}" stroke-linecap="round" opacity="0.6"/>')
    return (f'<g transform="rotate({rot} {_f(x)} {_f(y)})">' + clip(f"{u}-cc", d) + f'<g clip-path="url(#{u}-cc)">{inner}</g>'
            + ink(d, line, max(1.4, s * 0.035), seed, 2, 0.75) + "</g>")


def wrapped_candy(u, x, y, s, rot, seed, col, stripe, line=INK):
    """Twist-wrapped candy; s = half length."""
    bd = blob(x, y, s * 0.45, s * 0.32, seed, 0.04, 12)
    ends = [smooth_closed([(x + sg * s * 0.38, y), (x + sg * s, y - s * 0.32), (x + sg * s * 0.92, y), (x + sg * s, y + s * 0.3)]) for sg in (-1, 1)]
    out = [f'<g transform="rotate({rot} {_f(x)} {_f(y)})">']
    for i, e in enumerate(ends):
        out.append(wash(e, col, seed + i, 2, 0.6, 0.5) + ink(e, line, 1.4, seed, 1, 0.6))
    out.append(wash(bd, col, seed, 2, 0.6, 0.5))
    out.append(shade_in(f"{u}-wc", bd, "".join(f'<path d="M {_f(x + k * s * 0.22 - s * 0.2)} {_f(y - s)} l {_f(s * 0.4)} {_f(2 * s)}" stroke="{stripe}" stroke-width="{_f(s * 0.1)}"/>' for k in range(-3, 4))
                        + f'<ellipse cx="{_f(x - s * 0.12)}" cy="{_f(y - s * 0.14)}" rx="{_f(s * 0.18)}" ry="{_f(s * 0.07)}" fill="#FFFFFF" opacity="0.7"/>', "#000", 0.9))
    out.append(ink(bd, line, 1.6, seed, 2, 0.7))
    out.append("</g>")
    return "".join(out)


def bow(u, cx, cy, s, seed, col=PUMPKIN, dark=PUMPKIN_D, light=PUMPKIN_L, line=INK, dots=None):
    """Painted hair bow; s = half width."""
    out = []
    for sg in (-1, 1):
        tail = smooth_closed([(cx + sg * s * 0.08, cy + s * 0.05), (cx + sg * s * 0.42, cy + s * 0.62), (cx + sg * s * 0.28, cy + s * 0.58),
                              (cx + sg * s * 0.2, cy + s * 0.7), (cx - sg * s * 0.04, cy + s * 0.12)])
        out.append(body(f"{u}-t{sg + 1}", tail, (cx - s, cy, cx + s, cy + s * 0.8), dark, [col, light], seed + sg, n=10, angle=60 * sg + 90,
                        length=(s * 0.1, s * 0.3), width=(1, 2), line=line, lw=1.8))
    for sg in (-1, 1):
        loop = smooth_closed([(cx + sg * s * 0.1, cy - s * 0.05), (cx + sg * s * 0.55, cy - s * 0.48), (cx + sg * s * 0.98, cy - s * 0.32),
                              (cx + sg * s * 0.95, cy + s * 0.22), (cx + sg * s * 0.55, cy + s * 0.32), (cx + sg * s * 0.1, cy + s * 0.08)])
        out.append(body(f"{u}-l{sg + 1}", loop, (cx - s, cy - s * 0.5, cx + s, cy + s * 0.4), col, [light, dark, "#FFD08A"], seed + 3 + sg,
                        n=24, angle=-20 * sg, length=(s * 0.15, s * 0.4), width=(1, s * 0.05), line=line, lw=2))
        out.append(shade_in(f"{u}-ls{sg + 1}", loop, f'<path d="{blob(cx + sg * s * 0.25, cy + s * 0.12, s * 0.3, s * 0.2, seed, 0.1, 10)}" fill="{dark}"/>', dark, 0.5))
        if dots:
            out.append(shade_in(f"{u}-ld{sg + 1}", loop, "".join(f'<circle cx="{_f(cx + sg * s * a)}" cy="{_f(cy + s * b)}" r="{_f(s * 0.07)}" fill="{dots}"/>'
                                                              for a, b in ((0.4, -0.2), (0.75, -0.1), (0.6, 0.12), (0.85, 0.12), (0.3, 0.05))), dots, 0.9))
    kn = blob(cx, cy, s * 0.17, s * 0.2, seed + 9, 0.08, 10)
    out.append(body(f"{u}-k", kn, (cx - s * 0.2, cy - s * 0.2, cx + s * 0.2, cy + s * 0.2), dark, [col, light], seed + 9, n=8, angle=-90,
                    length=(3, 6), width=(1, 2), line=line, lw=1.8))
    return "".join(out)


def pail(u, cx, cy, w, h, seed, handle_to=None, line=INK, candy=True):
    """Little jack-o'-lantern candy pail with treats peeking out."""
    out = [jack(f"{u}-j", cx, cy, w, h, seed, face="cute", lit=False, leaf="#6E8A3E")]
    rim_y = cy - 0.4 * h
    if candy:
        out.append(wrapped_candy(f"{u}-c1", cx - w * 0.12, rim_y - h * 0.06, w * 0.2, -20, seed, "#8E6AC0", "#C9B6EA", line))
        out.append(candy_corn(f"{u}-c2", cx + w * 0.14, rim_y - h * 0.1, h * 0.32, 18, seed + 1, line))
    out.append(f'<path d="{blob(cx, rim_y + 2, w * 0.36, h * 0.09, seed, 0.05, 12)}" fill="#5A2410"/>')
    out.append(ink(blob(cx, rim_y + 2, w * 0.36, h * 0.09, seed, 0.05, 12), "#7A3412", 2, seed, 1, 0.9))
    if handle_to:
        hx, hy = handle_to
        out.append(ink(f"M {_f(cx - w * 0.34)} {_f(rim_y + 2)} Q {_f(hx - w * 0.15)} {_f(hy - h * 0.2)} {_f(hx)} {_f(hy)} Q {_f(hx + w * 0.15)} {_f(hy - h * 0.2)} {_f(cx + w * 0.34)} {_f(rim_y + 2)}", line, 2.4, seed, 2, 0.9))
    return "".join(out)


def cast_shadow(cx, cy, rx, ry, col="#3A2418", op=0.16, seed=1):
    return f'<path d="{blob(cx, cy, rx, ry, seed, 0.05, 14)}" fill="{col}" opacity="{op}"/>'


def mitten(u, x, y, w, rot, seed, base="#F7F1E6", tints=("#FFFFFF", "#E9DFF3", "#D3C5E8"), line="#3A2440"):
    """A ghost's little mitten hand, drawn on top of whatever it grips (w = the ghost's width)."""
    d = blob(x, y, w * 0.075, w * 0.058, seed, 0.06, 12, rot=rot)
    return (body(f"{u}-m", d, (x - 20, y - 20, x + 20, y + 20), base, list(tints), seed, n=10, angle=-90, length=(4, 9), width=(1, 2),
                 line=line, lw=2.2)
            + f'<path d="M {_f(x - w * 0.03)} {_f(y - w * 0.02)} q {_f(w * 0.02)} {_f(-w * 0.02)} {_f(w * 0.045)} {_f(-w * 0.01)}" stroke="#FFFFFF" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.8"/>')


@design("too-cute-to-spook")
def d_too_cute_to_spook():
    u = "hgb-tcs"
    out = [paper_ground(f"{u}-pp", PAPER, seed=31)]
    out.append(backdrop(u, 300, 300, 222, 178, "#E2D4EE", ["#D2C0E8", "#EEE4F6", "#C6B2E0", "#E9DDF2"], 32))
    out.append(stars(33, (90, 150, 510, 430), 14, "#B9A0D8", 0, r=(1.4, 2.6),
                     keep=lambda x, y: abs(x - 300) > 110 or y > 410))
    for x, y, r in ((128, 196, 11), (476, 186, 9), (118, 378, 7), (500, 330, 10)):
        out.append(twinkle(x, y, r, GOLD, 0.95, x))
    out.append(bat(f"{u}-b1", 160, 168, 38, 34, rot=-12, flap=0.3))
    out.append(bat(f"{u}-b2", 450, 140, 26, 35, rot=10, flap=-0.2))
    out.append(cast_shadow(300, 438, 92, 13, "#6A4C93", 0.22, 36))
    out.append(ghost(f"{u}-g", 292, 200, 196, 206, 37, lean=0.03, face="smile", arms=(1, 0), arm_up=(1, 0), line="#3A2440"))
    out.append(bow(f"{u}-bw", 262, 212, 38, 38, dots="#FFE2B0"))
    out.append(pail(f"{u}-pl", 440, 398, 82, 66, 39, handle_to=(416, 340)))
    out.append(mitten(f"{u}-mt", 412, 342, 196, 20, 45))
    out.append(candy_corn(f"{u}-cc1", 118, 330, 30, -24, 40))
    out.append(candy_corn(f"{u}-cc2", 148, 404, 24, 18, 41))
    out.append(wrapped_candy(f"{u}-wc", 498, 248, 18, 24, 42, "#9BD14B", "#E4F5BE"))
    out.append(script(300, 128, "too cute", 78, "#4A2E66", 400, shadow="#C9B2E0", sd=(2, 3)))
    out.append(bword(f"{u}-t", 300, 532, "TO SPOOK", ANTON, 84, PUMPKIN, ["#F8A85A", "#C9541A", "#FFC27A", "#E06A1E"], 43, max_w=410, ls=6,
                     shadow="#6A2A10", hi="#FFE2B0"))
    out.append(grain_over(f"{u}-gr", 44, dark="#5A3A2A", op=0.8))
    return "".join(out)


# ---------------------------------------------------------------- home sweet haunt
def lit_window(u, x, y, w, h, seed, arch=True, frame="#2A1A2E", glass=("#FFF2B8", "#FFC94A", "#E8862A"), cross=True, glow_r=None, peek=None):
    """Warm lit window: glow, gradient glass with brush strokes, inked frame and mullions."""
    if arch:
        d = (f"M {_f(x)} {_f(y + h)} L {_f(x)} {_f(y + w / 2)} A {_f(w / 2)} {_f(w / 2)} 0 0 1 {_f(x + w)} {_f(y + w / 2)} "
             f"L {_f(x + w)} {_f(y + h)} Z")
    else:
        d = smooth_closed(jitter([(x, y), (x + w / 2, y - 1), (x + w, y), (x + w + 1, y + h / 2), (x + w, y + h), (x + w / 2, y + h + 1), (x, y + h), (x - 1, y + h / 2)], seed, 0.6))
    out = [glow(f"{u}-wg", x + w / 2, y + h / 2, glow_r or w * 1.6, "#FFC24A", 0.5, 0.3),
           defs(rg(f"{u}-wf", [(0, glass[0]), (0.5, glass[1]), (1, glass[2])], cy=0.6, r=0.7)),
           f'<path d="{d}" fill="url(#{u}-wf)"/>',
           brush(f"{u}-wb", d, (x, y, x + w, y + h), ["#FFF6D0", "#F2A23A", "#FFE08A"], seed, int(w * h / 60), angle=-70,
                 length=(h * 0.15, h * 0.4), width=(1, 2.5), opacity=(0.25, 0.5))]
    if peek:
        out.append(peek)
    if cross:
        out.append(f'<path d="M {_f(x + w / 2)} {_f(y + 2)} L {_f(x + w / 2)} {_f(y + h)} M {_f(x)} {_f(y + h * 0.55)} L {_f(x + w)} {_f(y + h * 0.55)}" '
                   f'stroke="{frame}" stroke-width="{_f(max(2.4, w * 0.08))}" stroke-linecap="round"/>')
    out.append(ink(d, frame, max(3, w * 0.1), seed, 2, 0.95))
    out.append(f'<path d="{blob(x + w / 2, y + h + 3, w * 0.62, 4, seed, 0.1, 10)}" fill="{frame}"/>')
    return "".join(out)


def smoke(u, x, y, seed, n=6, col="#B9A8D8", dx=14, dy=-26, r0=9, grow=1.25, op=0.8):
    rnd = random.Random(seed)
    out = []
    r = r0
    for i in range(n):
        d = blob(x, y, r, r * 0.8, rnd.randrange(999), 0.12, 10)
        out.append(f'<path d="{d}" fill="{col}" opacity="{op * (1 - i / (n + 1)):.2f}"/>'
                   f'<path d="{blob(x - r * 0.2, y - r * 0.25, r * 0.55, r * 0.4, rnd.randrange(999), 0.1, 8)}" fill="#FFFFFF" opacity="{0.35 * (1 - i / n):.2f}"/>')
        x += dx * rnd.uniform(0.7, 1.3)
        y += dy * rnd.uniform(0.8, 1.1)
        r *= grow
    return "".join(out)


def picket_fence(u, x0, x1, base, h, seed, col=BONE_D, tints=("#FFFFFF", "#B8A688", "#E9DFC8"), line=INKN, gap=26, lean=4):
    rnd = random.Random(seed)
    out = []
    ds = []
    x = x0
    while x < x1:
        w = gap * 0.55
        t = rnd.uniform(-lean, lean)
        hh = h * rnd.uniform(0.85, 1.05)
        ds.append(smooth_closed([(x, base), (x + t * 0.3, base - hh * 0.8), (x + w / 2 + t, base - hh), (x + w + t * 0.3, base - hh * 0.8), (x + w, base)]))
        x += gap
    rails = [limb_d([(x0 - 6, base - h * 0.62), (x1 + 6, base - h * 0.6)], 6, 6, seed), limb_d([(x0 - 6, base - h * 0.25), (x1 + 6, base - h * 0.24)], 6, 6, seed + 1)]
    for d in rails:
        out.append(f'<path d="{d}" fill="{col}" opacity="0.85"/>' + ink(d, line, 1.4, seed, 1, 0.7))
    for i, d in enumerate(ds):
        out.append(f'<path d="{d}" fill="{col}"/>')
    out.append(brush(f"{u}-fb", ds, (x0, base - h * 1.1, x1 + gap, base), list(tints), seed, int((x1 - x0) * 0.8), angle=-90,
                     length=(h * 0.15, h * 0.4), width=(0.8, 2), opacity=(0.3, 0.6)))
    out.append(shade_in(f"{u}-fs", ds, f'<rect x="{x0}" y="{_f(base - h * 0.4)}" width="{x1 - x0 + gap}" height="{_f(h)}" fill="#6A5A7E"/>', "#000", 0.35))
    for d in ds:
        out.append(ink(d, line, 1.8, seed, 1, 0.85))
    return "".join(out)


def ragged_edge(pts, colors, seed, n=140, w=(3, 8), L=(14, 34), op=(0.35, 0.8), out_amt=4):
    """Dry-brush strokes laid along a closed outline so a painted swatch gets a brushed, deckled edge."""
    rnd = random.Random(seed)
    k = len(pts)
    res = []
    for _ in range(n):
        i = rnd.randrange(k)
        t = rnd.random()
        a, b = pts[i], pts[(i + 1) % k]
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        cx = sum(p[0] for p in pts) / k
        cy = sum(p[1] for p in pts) / k
        dd = math.hypot(x - cx, y - cy) or 1
        off = rnd.uniform(-out_amt * 2, out_amt)
        x += (x - cx) / dd * off
        y += (y - cy) / dd * off
        Ln = rnd.uniform(*L)
        x -= Ln / 2 * math.cos(math.radians(ang))
        y -= Ln / 2 * math.sin(math.radians(ang))
        res.append(dab(x, y, Ln, rnd.uniform(*w) / 2, ang + rnd.uniform(-6, 6), rnd.choice(colors), rnd.uniform(*op), 0.15, rnd))
    return "".join(res)


def clapboard(u, d, x0, x1, y0, y1, step, col, op=0.45, seed=1):
    rnd = random.Random(seed)
    lines = "".join(f'<path d="M {x0} {_f(y)} Q {_f((x0 + x1) / 2)} {_f(y + rnd.uniform(-1.5, 1.5))} {x1} {_f(y + rnd.uniform(-1, 1))}"/>'
                    for y in [y0 + step * i for i in range(int((y1 - y0) / step) + 1)])
    return clip(u, d) + f'<g clip-path="url(#{u})" fill="none" stroke="{col}" stroke-width="1.6" opacity="{op}">{lines}</g>'


def porch_lantern(u, x, y, s, seed):
    """Small hanging porch lantern with a lit flame (y = top of the bracket)."""
    body_d = smooth_closed([(x - 7 * s, y + 8 * s), (x + 7 * s, y + 8 * s), (x + 9 * s, y + 26 * s), (x, y + 30 * s), (x - 9 * s, y + 26 * s)])
    return (glow(f"{u}-lg", x, y + 18 * s, 34 * s, "#FFC24A", 0.6, 0.3)
            + ink(f"M {_f(x)} {_f(y)} L {_f(x)} {_f(y + 8 * s)}", "#1A1022", 2, seed, 1, 1)
            + defs(rg(f"{u}-lf", [(0, "#FFFFFF"), (0.4, "#FFE08A"), (1, "#F2A23A")], cy=0.6))
            + f'<path d="{body_d}" fill="url(#{u}-lf)"/>'
            + ink(body_d, "#1A1022", 2.2, seed, 2, 0.95)
            + f'<path d="M {_f(x - 10 * s)} {_f(y + 8 * s)} L {_f(x + 10 * s)} {_f(y + 8 * s)}" stroke="#1A1022" stroke-width="{_f(3 * s)}" stroke-linecap="round"/>'
            + f'<path d="M {_f(x)} {_f(y + 10 * s)} L {_f(x)} {_f(y + 28 * s)}" stroke="#1A1022" stroke-width="1.4" opacity="0.7"/>')


@design("home-sweet-haunt")
def d_home_sweet_haunt():
    u = "hgb-hsh"
    out = [paper_ground(f"{u}-pp", PAPER, seed=51)]
    out.append(backdrop(f"{u}-bk", 300, 300, 270, 230, "#E6DAEE", ["#DCCDEA", "#EFE6F5", "#D2C2E4"], 50, op=0.6))
    vpts = blob_pts(300, 284, 232, 170, 52, 0.05, 24)
    vd = smooth_closed(vpts)
    out.append(cast_shadow(306, 296, 236, 174, "#3A2A50", 0.18, 52))
    out.append(f'<path d="{vd}" fill="{NAVY}"/>')
    sky = (defs(lg(f"{u}-sk", [(0, "#1C1838"), (0.55, "#33275A"), (1, "#5A3E7E")]))
           + f'<rect width="600" height="600" fill="url(#{u}-sk)"/>'
           + dabs(["#2E2556", "#463A78", "#1A1636", "#5A4888"], 53, (40, 80, 560, 500), 180, -6, (30, 100), (3, 9), (0.15, 0.4), 0.12)
           + swirl(178, 214, 54, 130, ["#5B4888", "#7A66A8", "#C9A86A"], 54, 40, (2, 6), (30, 80), (0.15, 0.4))
           + stars(55, (70, 140, 530, 320), 26, BONE, 4, keep=lambda x, y: math.hypot(x - 178, y - 214) > 70)
           + pmoon(f"{u}-m", 178, 214, 44, 56, halo_r=2.6, halo_op=0.35))
    sky += ground(f"{u}-h1", [(40, 372), (140, 352), (260, 362), (380, 346), (480, 356), (580, 340)], 520, "#2A2248", ["#3A3060", "#1E1838", "#4A3E70"], 57)
    sky += paint_tree(f"{u}-tr", 478, 366, 170, 58, fill="#16101F", rim="#8A76B8", lean=8, spread=34, depth=5)
    H = []
    walls = smooth_closed(jitter([(206, 444), (209, 380), (212, 304), (300, 300), (390, 292), (392, 380), (396, 444), (300, 446)], 59, 1.2))
    roof = smooth_closed([(184, 312), (240, 248), (286, 182), (300, 160), (312, 150), (322, 160), (338, 196), (378, 252), (420, 304), (300, 300)])
    H.append(plank(f"{u}-ch", "M 350 238 L 348 196 L 382 192 L 386 262 Z", (348, 192, 386, 262), "#6A4440", ["#8A5A4A", "#3A2622", "#9A6A54"], 60, angle=-90, line=INKN, knots=0))
    H.append(f'<path d="M 344 198 L 388 192 L 388 184 L 344 190 Z" fill="#3A2630"/>')
    H.append(smoke(f"{u}-sm", 368, 176, 61, 6, "#A898CC", dx=18, dy=-22, r0=10))
    H.append(body(f"{u}-wl", walls, (206, 292, 396, 446), "#7A6496", ["#9A84B4", "#5E4A78", "#A893C4", "#6A5486"], 62, angle=0,
                  length=(20, 60), width=(1.5, 4), opacity=(0.25, 0.55), curve=0.06, line=None))
    H.append(clapboard(f"{u}-cb", walls, 200, 400, 314, 446, 12, "#3A2850", 0.55, 62))
    H.append(clapboard(f"{u}-cb2", walls, 200, 400, 315.5, 446, 12, "#C4B2E2", 0.3, 63))
    H.append(shade_in(f"{u}-wsh", walls, f'<path d="M 206 300 L 396 290 L 396 336 Q 300 326 206 340 Z" fill="#1A1228"/>'
                      f'<path d="M 360 290 L 400 290 L 400 450 L 372 450 Z" fill="#1A1228"/>', "#000", 0.45))
    H.append(ink(walls, INKN, 2.6, 62, 2, 0.85))
    H.append(body(f"{u}-rf", roof, (184, 150, 420, 312), "#33264A", ["#4A3A66", "#22182F", "#5A4878"], 63, angle=60, line=INKN, lw=2.8))
    sh = []
    for row in range(7):
        yy = 186 + row * 18
        for k in range(-8, 9):
            xx = 300 + k * 17 + (8 if row % 2 else 0)
            sh.append(f"M {xx - 8} {yy} q 8 9 16 0")
    H.append(clip(f"{u}-rfc", roof) + f'<g clip-path="url(#{u}-rfc)" fill="none" stroke="#7A66A0" stroke-width="1.6" opacity="0.55">'
             + "".join(f'<path d="{d}"/>' for d in sh) + "</g>")
    H.append(ink("M 186 314 Q 300 296 420 306", "#1A1022", 4, 64, 1, 0.9))
    H.append(rim_lit(f"{u}-rr", roof, -2, -2, "#B9A6E0", 3, 0.6))
    peek = ghost(f"{u}-pg", 302, 236, 26, 30, 65, face="smile", arms=(0, 0), line="#3A2440", lw=1.4, blush="#F2A0A8")
    H.append(lit_window(f"{u}-w0", 286, 228, 32, 34, 66, arch=True, cross=False, glow_r=48, peek=peek))
    H.append(lit_window(f"{u}-w1", 226, 336, 38, 48, 67, glow_r=60))
    H.append(lit_window(f"{u}-w2", 340, 332, 38, 48, 68, glow_r=60))
    door = "M 280 446 L 280 402 Q 280 378 302 378 Q 324 378 324 402 L 324 446 Z"
    H.append(glow(f"{u}-dg", 302, 420, 70, "#FFB547", 0.4))
    H.append(plank(f"{u}-dr", door, (280, 378, 324, 446), "#7A3A2A", ["#9A4E36", "#5A2618", "#B0603E"], 69, angle=-90, line="#1A1022", lw=2.6, knots=0))
    H.append(f'<circle cx="316" cy="414" r="2.6" fill="{GOLD}"/>')
    H.append(lit_window(f"{u}-w3", 293, 386, 18, 12, 70, arch=True, cross=False, glow_r=10))
    H.append(porch_lantern(f"{u}-pl", 268, 380, 0.8, 71))
    scene = (sky + "".join(H)
             + ground(f"{u}-fg", [(40, 448), (150, 440), (300, 446), (450, 436), (580, 444)], 520, "#2B3A2E", ["#3E5238", "#1E2A22", "#4A5E3C"], 71, rim="#7A9A58")
             + f'<path d="M 286 446 Q 270 476 236 520 L 330 520 Q 318 480 318 446 Z" fill="#B8A07A"/>'
             + dabs(["#D8C29A", "#8A7254", "#E9D8B4"], 72, (240, 446, 330, 520), 40, -10, (6, 16), (1, 2.5), (0.3, 0.6), 0.2, keep=lambda x, y: abs(x - (300 - (y - 446) * 0.6)) < 30 + (y - 446) * 0.3)
             + grass_tufts(75, (50, 446, 550, 490), 60, ["#4A6A3A", "#2A3A26", "#6A8A4A"])
             + "".join(painted_pumpkin(f"{u}-sp{i}", x, y, w, w * 0.8, 90 + i, *cols) for i, (x, y, w, cols) in enumerate((
                 (236, 452, 22, ("#E8D9BC", "#B8A07A", "#FFF6E2", "#6B5A2E", "#6E8A3E")), (372, 450, 18, ("#E8A23A", "#B9731E", "#F8C85A", "#6B5A2E", "#6E8A3E")))))
             )
    out.append(clip(f"{u}-vc", vd) + f'<g clip-path="url(#{u}-vc)"><g transform="translate(0 -28)">' + scene + "</g></g>")
    out.append(ragged_edge(vpts, [NAVY, "#2E2556", "#3A2E60"], 49, 170, w=(3, 8), L=(16, 40), op=(0.45, 0.9)))
    out.append(ink(vd, "#2A1E3E", 2, 52, 1, 0.35))
    out.append(jack(f"{u}-j1", 196, 436, 50, 42, 76, face="cute", glow_r=64))
    out.append(jack(f"{u}-j2", 412, 440, 40, 34, 77, face="classic", glow_r=52))
    out.append(leaf_fall(82, (120, 420, 480, 450), 2, keep=lambda x, y: abs(x - 300) > 60 and abs(x - 196) > 40 and abs(x - 412) > 40))
    out.append(bat(f"{u}-b1", 440, 126, 22, 78, rot=8, flap=0.2))
    out.append(bat(f"{u}-b2", 478, 152, 16, 79, rot=-10, flap=-0.3))
    out.append(script(300, 100, "home sweet", 60, "#3A2A5A", 380, shadow="#D9C8EA", sd=(2, 3)))
    out.append(bword(f"{u}-t", 300, 540, "HAUNT", ANTON, 92, PUMPKIN, ["#F8A85A", "#C9541A", "#FFC27A", "#E06A1E"], 80, max_w=330, ls=12,
                     shadow="#3A1A10", hi="#FFE2B0"))
    out.append(grain_over(f"{u}-gr", 81, dark="#5A3A2A", op=0.8))
    return "".join(out)


# ---------------------------------------------------------------- stay spooky
def crystal_ball(u, cx, cy, r, seed):
    out = [glow(f"{u}-bg", cx, cy, r * 1.9, "#9C7AE0", 0.45, 0.35)]
    d = blob(cx, cy, r, r, seed, 0.008, 28)
    inner = [defs(rg(f"{u}-bi", [(0, "#8E7AD8"), (0.5, "#4A3488"), (1, "#1E1640")], cx=0.45, cy=0.4, r=0.6)),
             f'<rect x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" fill="url(#{u}-bi)"/>',
             swirl(cx, cy, r * 0.2, r * 1.0, ["#B9A6F0", "#6A52B0", "#E0D4FF", "#3A2A70", "#9BD1C8"], seed, 70, (2, 7), (20, 80), (0.2, 0.5)),
             pmoon(f"{u}-bm", cx + r * 0.28, cy - r * 0.3, r * 0.2, seed + 1, halo_r=2.4, halo_op=0.5, line=None, craters=3),
             ground(f"{u}-bh", [(cx - r, cy + r * 0.45), (cx - r * 0.4, cy + r * 0.3), (cx + r * 0.2, cy + r * 0.4), (cx + r, cy + r * 0.28)], cy + r,
                    "#1A1230", ["#2A1E48", "#120C22"], seed + 2, n=30),
             paint_tree(f"{u}-bt", cx - r * 0.35, cy + r * 0.36, r * 0.75, seed + 3, fill="#120C1E", rim="#8A76C8", spread=34, depth=5),
             bat(f"{u}-b1", cx + r * 0.05, cy - r * 0.52, r * 0.1, seed + 4, rot=-8, face=False),
             bat(f"{u}-b2", cx + r * 0.5, cy + r * 0.0, r * 0.08, seed + 5, rot=12, face=False),
             stars(seed + 6, (cx - r * 0.8, cy - r * 0.8, cx + r * 0.8, cy + r * 0.1), 14, "#FFFFFF", 2, r=(0.6, 1.4), twr=(3, 5)),
             f'<path d="{blob(cx + r * 0.2, cy + r * 0.25, r * 1.1, r * 1.1, seed, 0.01, 20)}" fill="none" stroke="#120C26" stroke-width="{r * 0.35:.1f}" opacity="0.35"/>']
    out.append(clip(f"{u}-bc", d) + f'<g clip-path="url(#{u}-bc)">' + "".join(inner) + "</g>")
    out.append(f'<path d="M {_f(cx - r * 0.72)} {_f(cy - r * 0.1)} A {_f(r * 0.74)} {_f(r * 0.74)} 0 0 1 {_f(cx - r * 0.2)} {_f(cy - r * 0.7)}" fill="none" '
               f'stroke="#FFFFFF" stroke-width="{_f(r * 0.07)}" stroke-linecap="round" opacity="0.75"/>')
    out.append(f'<path d="{blob(cx - r * 0.52, cy - r * 0.52, r * 0.06, r * 0.05, seed, 0.1, 8)}" fill="#FFFFFF" opacity="0.9"/>')
    out.append(f'<path d="M {_f(cx + r * 0.5)} {_f(cy + r * 0.62)} A {_f(r * 0.8)} {_f(r * 0.8)} 0 0 0 {_f(cx + r * 0.78)} {_f(cy + r * 0.2)}" fill="none" '
               f'stroke="#FFD08A" stroke-width="{_f(r * 0.04)}" stroke-linecap="round" opacity="0.6"/>')
    out.append(ink(d, "#120A20", 3, seed, 2, 0.9))
    return "".join(out)


def brass_stand(u, cx, top, w, seed):
    """Ornate painted brass cradle for the crystal ball."""
    d = smooth_closed([(cx - w * 0.36, top), (cx - w * 0.3, top + w * 0.12), (cx - w * 0.2, top + w * 0.2), (cx - w * 0.28, top + w * 0.3),
                       (cx - w * 0.5, top + w * 0.36), (cx - w * 0.5, top + w * 0.42), (cx + w * 0.5, top + w * 0.42), (cx + w * 0.5, top + w * 0.36),
                       (cx + w * 0.28, top + w * 0.3), (cx + w * 0.2, top + w * 0.2), (cx + w * 0.3, top + w * 0.12), (cx + w * 0.36, top),
                       (cx, top + w * 0.04)])
    out = [body(f"{u}-st", d, (cx - w / 2, top, cx + w / 2, top + w * 0.42), "#C9963A", ["#F2CC6A", "#8A5A1E", "#FFE29A", "#A8742A"], seed,
                n=80, angle=0, length=(w * 0.05, w * 0.18), width=(1, 3), opacity=(0.3, 0.6), line="#3A2010", lw=2.6)]
    out.append(shade_in(f"{u}-ss", d, f'<rect x="{cx + w * 0.08}" y="{top}" width="{w}" height="{w}" fill="#5A3410"/>', "#000", 0.45))
    out.append(f'<path d="M {_f(cx - w * 0.44)} {_f(top + w * 0.385)} L {_f(cx + w * 0.3)} {_f(top + w * 0.385)}" stroke="#FFF0B8" stroke-width="2.4" opacity="0.6" stroke-linecap="round"/>')
    for k in (-0.3, -0.1, 0.1, 0.3):
        out.append(f'<path d="{blob(cx + k * w, top + w * 0.39, 3, 3, seed, 0.2, 6)}" fill="#7A4A14"/>')
    return "".join(out)


def tarot(u, cx, cy, w, rot, seed, sym="moon", face="#F3E6C8", back="#4E2A6E", line="#1A0E2A"):
    """Small painted tarot card lying on the cloth, with a gold moon or star."""
    h = w * 1.6
    d = smooth_closed(jitter([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], seed, 0.6))
    d = f"M {_f(cx - w / 2)} {_f(cy - h / 2)} L {_f(cx + w / 2)} {_f(cy - h / 2)} L {_f(cx + w / 2)} {_f(cy + h / 2)} L {_f(cx - w / 2)} {_f(cy + h / 2)} Z"
    inner = f"M {_f(cx - w * 0.38)} {_f(cy - h * 0.42)} L {_f(cx + w * 0.38)} {_f(cy - h * 0.42)} L {_f(cx + w * 0.38)} {_f(cy + h * 0.42)} L {_f(cx - w * 0.38)} {_f(cy + h * 0.42)} Z"
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">', f'<path d="{d}" fill="#0A0614" opacity="0.4" transform="translate(3 4)"/>',
           body(f"{u}-c", d, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), face, ["#FFFFFF", "#D8C4A0"], seed, n=10, angle=-80, length=(6, 14), width=(1, 2), line=line, lw=1.8),
           f'<path d="{inner}" fill="{back}"/>' + ink(inner, GOLD, 1.4, seed, 1, 0.9)]
    if sym == "moon":
        out.append(f'<path d="{crescent_d(cx - w * 0.04, cy - h * 0.06, w * 0.2, w * 0.12)}" fill="{GOLD}"/>')
    else:
        out.append(twinkle(cx, cy - h * 0.06, w * 0.24, GOLD, 1, seed))
    for k in (-1, 1):
        out.append(f'<circle cx="{_f(cx + k * w * 0.18)}" cy="{_f(cy + h * 0.28)}" r="1.6" fill="{GOLD}"/>')
    out.append("</g>")
    return "".join(out)


@design("stay-spooky")
def d_stay_spooky():
    u = "hgb-ssp"
    out = [night_sky(u, 91, [(0, "#140F28"), (0.55, "#2A1E4A"), (1, "#3A2558")], ["#2A2050", "#3A2A62", "#1A1434", "#4A3470"], n=280, angle=-80,
                     length=(40, 120))]
    out.append(stars(92, (30, 30, 570, 300), 30, BONE, 5, keep=lambda x, y: math.hypot(x - 300, y - 228) > 160))
    # velvet table cloth with folds
    cloth = smooth_open([(-20, 376), (120, 368), (300, 372), (480, 366), (620, 374)]) + " L 620 620 L -20 620 Z"
    out.append(body(f"{u}-cl", cloth, (-20, 360, 620, 620), "#4E2A6E", ["#6A3E8E", "#2E1848", "#7A4E9E", "#3A2058"], 93, n=260, angle=-88,
                    length=(40, 120), width=(3, 8), opacity=(0.2, 0.45), curve=0.1))
    out.append(defs(lg(f"{u}-cf", [(0, "#000000", 0), (1, "#0A0614", 0.55)])) + f'<rect y="380" width="600" height="220" fill="url(#{u}-cf)"/>')
    out.append(ink(smooth_open([(-20, 376), (120, 368), (300, 372), (480, 366), (620, 374)]), "#B48AD8", 2.6, 94, 1, 0.5))
    # candles
    out.append(candle(f"{u}-c1", 100, 404, 128, 34, 95, glow_r=130, glow_op=0.5))
    out.append(candle(f"{u}-c2", 152, 410, 78, 28, 96, glow_r=90))
    out.append(candle(f"{u}-c3", 498, 406, 104, 32, 97, glow_r=120, glow_op=0.5))
    out.append(cast_shadow(300, 394, 120, 12, "#0A0614", 0.5, 98))
    out.append(brass_stand(f"{u}-bs", 300, 334, 190, 99))
    out.append(crystal_ball(f"{u}-cb", 300, 228, 122, 100))
    out.append(tarot(f"{u}-tc1", 424, 374, 40, -14, 104, "moon"))
    out.append(tarot(f"{u}-tc2", 452, 380, 40, 8, 105, "star"))
    out.append(twinkle(196, 300, 9, CANDLE, 0.9, 106) + twinkle(410, 318, 7, CANDLE, 0.9, 107) + twinkle(214, 150, 6, "#E0D4FF", 0.9, 108))
    out.append(label(300, 446, "STAY", JOS, 40, BONE, ls=16, rule=GOLD, line_w=48, seed=101))
    out.append(script(300, 530, "spooky", 128, "#3A1E5A", 440, shadow=None))
    out.append(bword(f"{u}-t", 300, 524, "spooky", SERIF_IT, 128, "#D9C6F6", ["#FFFFFF", "#B9A0E8", "#EEE4FF", "#9C82D2"], 102, max_w=440,
                     shadow="#1A0E2A", angle=-60, hi="#FFFFFF"))
    out.append(grain_over(f"{u}-gr", 103))
    return "".join(out)


# ---------------------------------------------------------------- the witch is in
def potion(u, cx, base, w, h, seed, liquid=("#C6F27A", SLIME, "#3E6A1E"), shape="round", cork="#B88A5A", level=0.6, label_c=None, glow_op=0.35):
    """Painted glass potion bottle with glowing liquid, cork, glints."""
    neck_w = w * 0.3
    if shape == "round":
        bd = smooth_closed([(cx - neck_w / 2, base - h), (cx - neck_w / 2, base - h * 0.62), (cx - w / 2, base - h * 0.32), (cx - w * 0.45, base - h * 0.04),
                            (cx, base + 1), (cx + w * 0.45, base - h * 0.04), (cx + w / 2, base - h * 0.32), (cx + neck_w / 2, base - h * 0.62), (cx + neck_w / 2, base - h)])
    elif shape == "tall":
        bd = smooth_closed([(cx - neck_w / 2, base - h), (cx - neck_w / 2, base - h * 0.78), (cx - w / 2, base - h * 0.62), (cx - w / 2, base - h * 0.05),
                            (cx, base + 1), (cx + w / 2, base - h * 0.05), (cx + w / 2, base - h * 0.62), (cx + neck_w / 2, base - h * 0.78), (cx + neck_w / 2, base - h)])
    else:  # flask
        bd = smooth_closed([(cx - neck_w / 2, base - h), (cx - neck_w / 2, base - h * 0.6), (cx - w / 2, base - h * 0.05), (cx, base + 1),
                            (cx + w / 2, base - h * 0.05), (cx + neck_w / 2, base - h * 0.6), (cx + neck_w / 2, base - h)])
    ly = base - h * level
    out = [glow(f"{u}-pg", cx, base - h * 0.3, w * 1.3, liquid[1], glow_op, 0.35)]
    out.append(f'<path d="{bd}" fill="#2A2440" opacity="0.55"/>')
    liq = (defs(lg(f"{u}-lq", [(0, liquid[0]), (0.6, liquid[1]), (1, liquid[2])]))
           + f'<path d="M {_f(cx - w)} {_f(ly)} Q {_f(cx)} {_f(ly + 4)} {_f(cx + w)} {_f(ly)} L {_f(cx + w)} {_f(base + 4)} L {_f(cx - w)} {_f(base + 4)} Z" fill="url(#{u}-lq)"/>'
           + dabs([liquid[0], liquid[2], "#FFFFFF"], seed, (cx - w / 2, ly, cx + w / 2, base), int(w * 0.6), -90, (h * 0.08, h * 0.25), (1, 2.5), (0.2, 0.5), 0.2)
           + "".join(f'<circle cx="{_f(cx + random.Random(seed + i).uniform(-w * 0.3, w * 0.3))}" cy="{_f(ly + (base - ly) * random.Random(seed + i * 3).uniform(0.2, 0.85))}" '
                     f'r="{_f(random.Random(seed + i * 7).uniform(1.2, 3))}" fill="none" stroke="#FFFFFF" stroke-width="1" opacity="0.7"/>' for i in range(5))
           + f'<path d="M {_f(cx - w)} {_f(ly)} Q {_f(cx)} {_f(ly + 4)} {_f(cx + w)} {_f(ly)}" stroke="{liquid[0]}" stroke-width="2.4" fill="none"/>')
    out.append(clip(f"{u}-pc", bd) + f'<g clip-path="url(#{u}-pc)">{liq}'
               + f'<path d="{blob(cx + w * 0.3, base - h * 0.3, w * 0.25, h * 0.4, seed, 0.1, 10)}" fill="#0A0614" opacity="0.25"/></g>')
    if label_c:
        lb = blob(cx, base - h * 0.28, w * 0.28, h * 0.1, seed + 3, 0.06, 10)
        out.append(wash(lb, label_c, seed, 2, 0.5, 0.5) + ink(lb, "#3A2418", 1.2, seed, 1, 0.7))
    out.append(f'<path d="M {_f(cx - w * 0.3)} {_f(base - h * 0.42)} Q {_f(cx - w * 0.36)} {_f(base - h * 0.2)} {_f(cx - w * 0.24)} {_f(base - h * 0.08)}" '
               f'stroke="#FFFFFF" stroke-width="{_f(max(2, w * 0.07))}" fill="none" stroke-linecap="round" opacity="0.75"/>')
    out.append(f'<path d="M {_f(cx - neck_w * 0.2)} {_f(base - h * 0.95)} L {_f(cx - neck_w * 0.2)} {_f(base - h * 0.7)}" stroke="#FFFFFF" stroke-width="2" opacity="0.6" stroke-linecap="round"/>')
    out.append(ink(bd, "#120A1A", 2.2, seed, 2, 0.9))
    ck = blob(cx, base - h - neck_w * 0.3, neck_w * 0.55, neck_w * 0.45, seed + 5, 0.08, 10)
    out.append(body(f"{u}-ck", ck, (cx - neck_w, base - h - neck_w, cx + neck_w, base - h), cork, ["#D9AE76", "#8A6038"], seed + 5, n=10, angle=-90,
                    length=(3, 7), width=(1, 2), line="#3A2418", lw=1.6))
    return "".join(out)


def herbs(u, x, top, L, seed, col=("#7A8A4A", "#5A6A34", "#9AA864"), twine="#C9A26A"):
    """Bundle of drying herbs hanging upside down from a twine loop."""
    rnd = random.Random(seed)
    out = [ink(f"M {_f(x)} {_f(top)} L {_f(x + 1)} {_f(top + L * 0.25)}", twine, 2, seed, 1, 0.9)]
    stems = []
    for i in range(9):
        a = math.radians(90 + rnd.uniform(-22, 22))
        ll = L * rnd.uniform(0.6, 0.85)
        sx, sy = x + rnd.uniform(-3, 3), top + L * 0.25
        ex, ey = sx + ll * math.cos(a), sy + ll * math.sin(a)
        stems.append((sx, sy, ex, ey))
        out.append(ink(f"M {_f(sx)} {_f(sy)} Q {_f((sx + ex) / 2 + rnd.uniform(-4, 4))} {_f((sy + ey) / 2)} {_f(ex)} {_f(ey)}", "#5A4A2A", 1.4, seed + i, 1, 0.9))
        for k in range(5):
            t = 0.35 + k * 0.14
            px, py = sx + (ex - sx) * t, sy + (ey - sy) * t
            for sg in (-1, 1):
                out.append(f'<path d="{blob(px + sg * 4, py + 3, 5, 2.4, rnd.randrange(999), 0.15, 8, rot=sg * 60 + 90)}" fill="{rnd.choice(col)}" opacity="0.95"/>')
    # lavender-ish tips
    for sx, sy, ex, ey in stems[::2]:
        out.append(f'<path d="{blob(ex, ey + 4, 3, 7, rnd.randrange(999), 0.15, 8)}" fill="#8A6AB8"/>')
    out.append(f'<path d="{blob(x, top + L * 0.27, 7, 4, seed, 0.1, 8)}" fill="{twine}"/>' + ink(blob(x, top + L * 0.27, 7, 4, seed, 0.1, 8), "#5A3A1A", 1.2, seed, 1, 0.8))
    return "".join(out)


def book_stack(u, cx, base, seed, books=(("#5A2E6E", "#3A1A4E", 96, 20), ("#2E5A4A", "#1A3A2E", 84, 17), ("#8A3A2A", "#5A2216", 72, 15)),
               line="#1A0E10", pages="#EFE2C4", band=GOLD):
    """A small stack of painted spell books lying flat."""
    rnd = random.Random(seed)
    out = []
    y = base
    for i, (col, dark, w, h) in enumerate(books):
        x = cx + rnd.uniform(-6, 6)
        d = smooth_closed(jitter([(x - w / 2, y), (x - w / 2 - 1, y - h / 2), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2 + 1, y - h / 2), (x + w / 2, y)], seed + i, 0.5))
        out.append(body(f"{u}-b{i}", d, (x - w / 2, y - h, x + w / 2, y), col, [dark, col, "#FFFFFF"], seed + i, n=16, angle=0,
                        length=(w * 0.15, w * 0.4), width=(1, 2.2), opacity=(0.15, 0.35), line=line, lw=2))
        pg = f"M {_f(x + w / 2 - 2)} {_f(y - h + 3)} L {_f(x + w / 2 + 4)} {_f(y - h + 4)} L {_f(x + w / 2 + 4)} {_f(y - 3)} L {_f(x + w / 2 - 2)} {_f(y - 3)} Z"
        out.append(f'<path d="{pg}" fill="{pages}"/>' + "".join(f'<path d="M {_f(x + w / 2 - 1)} {_f(y - h + 3 + k * (h - 6) / 4)} l 5 0" stroke="#B8A27A" stroke-width="0.8"/>' for k in range(1, 4)))
        out.append(f'<path d="M {_f(x - w * 0.32)} {_f(y - h + 1)} L {_f(x - w * 0.32)} {_f(y - 1)} M {_f(x - w * 0.22)} {_f(y - h + 1)} L {_f(x - w * 0.22)} {_f(y - 1)}" stroke="{band}" stroke-width="2.4" opacity="0.9"/>')
        out.append(f'<path d="M {_f(x - w / 2 + 4)} {_f(y - h + 3)} L {_f(x + w / 2 - 6)} {_f(y - h + 3)}" stroke="#FFFFFF" stroke-width="1.6" opacity="0.35" stroke-linecap="round"/>')
        y -= h
    return "".join(out)


@design("the-witch-is-in")
def d_the_witch_is_in():
    u = "hgb-twi"
    out = []
    # dark painted plank wall
    out.append(f'<rect width="600" height="600" fill="#2A1E30"/>')
    for i, x in enumerate(range(-20, 620, 92)):
        d = rect_d(x, -10, x + 90, 610)
        out.append(plank(f"{u}-wp{i}", d, (x, -10, x + 90, 610), ["#2E2236", "#33263C", "#281C2E"][i % 3], ["#3E3048", "#1E1424", "#463656"], 110 + i,
                         angle=-90, grain_c="#120A16", knots=2, line="#120A16", lw=2.4, n=110))
    out.append(glow(f"{u}-amb", 300, 250, 340, "#FFB547", 0.22, 0.3))
    # shelf with potions and a candle
    out.append(cast_shadow(300, 214, 270, 10, "#0A0610", 0.6, 111))
    shelf = smooth_closed([(36, 186), (300, 182), (564, 186), (566, 204), (300, 206), (34, 204)])
    out.append(plank(f"{u}-sh", shelf, (34, 182, 566, 206), "#7A5236", ["#9A6E48", "#5A3A22", "#B0845A"], 112, line="#1A0E10", lw=2.4))
    for x in (90, 510):
        br = smooth_closed([(x - 10, 204), (x + 10, 204), (x + 8, 216), (x - 2, 240), (x - 8, 236)])
        out.append(plank(f"{u}-br{x}", br, (x - 10, 204, x + 10, 240), "#5A3A22", ["#7A5236", "#3A2214"], x, angle=-90, line="#1A0E10", lw=2, knots=0))
    out.append(potion(f"{u}-p1", 104, 184, 62, 88, 113, shape="round", liquid=("#D9B8FF", "#9A6AE0", "#4A2A8A"), label_c="#EFE2C4"))
    out.append(potion(f"{u}-p2", 172, 184, 40, 118, 114, shape="tall", liquid=("#D8FF9A", SLIME, SLIME_D), glow_op=0.45))
    out.append(potion(f"{u}-p3", 228, 184, 46, 62, 115, shape="flask", liquid=("#FFD08A", PUMPKIN, PUMPKIN_D)))
    out.append(candle(f"{u}-cn", 300, 184, 70, 26, 116, glow_r=110, glow_op=0.55))
    out.append(potion(f"{u}-p4", 372, 184, 52, 100, 117, shape="tall", liquid=("#9AE8E0", "#3AB8A8", "#1A6A62"), label_c="#EFE2C4"))
    out.append(potion(f"{u}-p5", 438, 184, 56, 76, 118, shape="round", liquid=("#FFB8C8", "#E0608A", "#8A2A4A")))
    out.append(potion(f"{u}-p6", 500, 184, 36, 90, 119, shape="flask", liquid=("#D8FF9A", SLIME, SLIME_D)))
    # drying herbs above, a corner web
    out.append(herbs(f"{u}-h1", 262, -6, 70, 120))
    out.append(herbs(f"{u}-h2", 338, -6, 64, 121, col=("#8A7A4A", "#6A5A34", "#A89A64")))
    out.append(web(f"{u}-wb", 600, 0, [150, 170, 160, 140], [40, 75, 110, 140], 122, col="#D8CCE8", sw=1.6, op=0.6, a0=90, a1=180))
    # lower shelf: a lit jack-o'-lantern, spell books and a stubby candle
    out.append(cast_shadow(300, 560, 300, 8, "#0A0610", 0.6, 140))
    shelf2 = smooth_closed([(-10, 544), (300, 540), (610, 544), (610, 572), (300, 574), (-10, 572)])
    out.append(plank(f"{u}-sh2", shelf2, (-10, 540, 610, 574), "#7A5236", ["#9A6E48", "#5A3A22", "#B0845A"], 141, line="#1A0E10", lw=2.4))
    out.append(jack(f"{u}-jk", 126, 516, 74, 58, 142, face="classic", glow_r=110, glow_op=0.5))
    out.append(book_stack(f"{u}-bk", 470, 542, 143))
    out.append(candle(f"{u}-cn2", 404, 542, 40, 22, 144, glow_r=80, glow_op=0.5))
    out.append(spider(f"{u}-sp", 548, 112, 11, 145, thread="#D8CCE8", thread_top=40))
    # hanging sign
    out.append(f'<circle cx="300" cy="256" r="5" fill="#8A7A6A"/><circle cx="299" cy="255" r="2" fill="#E8DCC8"/>')
    out.append(ink("M 150 308 L 300 256 L 450 308", "#C9A26A", 3, 123, 2, 0.95))
    out.append(cast_shadow(306, 394, 210, 84, "#05030A", 0.45, 124))
    sign = smooth_closed(jitter([(98, 306), (300, 300), (502, 306), (508, 384), (502, 466), (300, 472), (98, 466), (92, 384)], 125, 1.5))
    out.append(plank(f"{u}-sg", sign, (92, 300, 508, 472), "#C79A62", ["#DDB37A", "#A87A46", "#E8C48E", "#B8864E"], 126, grain_c="#5A3A1A", knots=2, line="#2A1608", lw=3))
    out.append(ink(smooth_closed(jitter([(112, 318), (300, 313), (488, 318), (493, 384), (488, 454), (300, 459), (112, 454), (107, 384)], 127, 1.2)), "#7A5028", 2, 127, 1, 0.55))
    for x, y in ((150, 306), (450, 306)):
        out.append(f'<circle cx="{x}" cy="{y + 12}" r="4.5" fill="#3A2A20"/><circle cx="{x - 1}" cy="{y + 11}" r="1.6" fill="#C9B8A0"/>')
    out.append(script(300, 384, "the witch", 76, "#3A1E10", 370, shadow="#F2D8A8", sd=(1.5, 2)))
    out.append(bword(f"{u}-t", 300, 448, "IS IN", ANTON, 62, "#4E2A6E", ["#6A3E8E", "#2E1848", "#7A4E9E", "#3A2058"], 128, max_w=240, ls=14,
                     shadow="#E8C48E", sd=0.03))
    for sg in (-1, 1):
        out.append(twinkle(300 + sg * 150, 428, 11, "#4E2A6E", 0.95, 129 + sg))
        out.append(twinkle(300 + sg * 176, 414, 6, "#B8864E", 0.95, 131 + sg))
    out.append(grain_over(f"{u}-gr", 132))
    return "".join(out)


# ---------------------------------------------------------------- creep it real
def sock_spider(u, cx, cy, r, seed, body_c="#3E2E58", tints=("#5A4A78", "#241A36", "#6E5A90", "#2E2246"), line="#120A1A",
                sock=PUMPKIN, stripe="#5A2E7A", shoe="#1A1222", thread=BONE, thread_top=None, treat=True):
    """Cute painted spider in striped socks and little boots, waving its top legs, holding a candy corn."""
    out = []
    if thread_top is not None:
        out.append(ink(f"M {_f(cx)} {_f(thread_top)} Q {_f(cx + 2)} {_f((thread_top + cy - r) / 2)} {_f(cx)} {_f(cy - r * 0.9)}", thread, 2.2, seed, 2, 0.9))
    # legs: (hip angle, knee offset, foot offset) per side, in units of r
    legs = [((0.55, -0.45), (1.25, -1.15), (1.55, -1.55)),
            ((0.75, -0.15), (1.65, -0.55), (2.05, -0.3)),
            ((0.75, 0.15), (1.6, 0.25), (1.9, 0.85)),
            ((0.55, 0.45), (1.1, 0.95), (1.2, 1.55))]
    rnd = random.Random(seed)
    for sgn in (-1, 1):
        for i, (h, k, f) in enumerate(legs):
            hx, hy = cx + sgn * h[0] * r, cy + h[1] * r
            kx, ky = cx + sgn * k[0] * r, cy + k[1] * r
            fx, fy = cx + sgn * f[0] * r, cy + f[1] * r
            thigh = f"M {_f(hx)} {_f(hy)} Q {_f((hx + kx) / 2)} {_f(min(hy, ky) - r * 0.25)} {_f(kx)} {_f(ky)}"
            shin = f"M {_f(kx)} {_f(ky)} Q {_f((kx + fx) / 2 + sgn * r * 0.08)} {_f((ky + fy) / 2)} {_f(fx)} {_f(fy)}"
            lw = r * 0.2
            out.append(f'<path d="{thigh}" fill="none" stroke="{body_c}" stroke-width="{_f(lw)}" stroke-linecap="round"/>')
            out.append(f'<path d="{thigh}" fill="none" stroke="#6E5A90" stroke-width="{_f(lw * 0.3)}" stroke-linecap="round" opacity="0.6" transform="translate(0 {_f(-lw * 0.2)})"/>')
            out.append(f'<path d="{shin}" fill="none" stroke="{line}" stroke-width="{_f(lw * 1.25)}" stroke-linecap="round"/>')
            out.append(f'<path d="{shin}" fill="none" stroke="{sock}" stroke-width="{_f(lw)}" stroke-linecap="butt"/>')
            out.append(f'<path d="{shin}" fill="none" stroke="{stripe}" stroke-width="{_f(lw)}" stroke-dasharray="{_f(r * 0.13)} {_f(r * 0.13)}"/>')
            out.append(f'<path d="{shin}" fill="none" stroke="#FFFFFF" stroke-width="{_f(lw * 0.22)}" opacity="0.35" transform="translate({_f(-sgn * lw * 0.2)} {_f(-lw * 0.2)})"/>')
            ang = math.degrees(math.atan2(fy - ky, fx - kx))
            bt = blob(fx + math.cos(math.radians(ang)) * r * 0.06, fy + math.sin(math.radians(ang)) * r * 0.06, r * 0.17, r * 0.12, seed + i * 3 + sgn, 0.08, 10, rot=ang)
            out.append(f'<path d="{bt}" fill="{shoe}"/>' + f'<path d="{blob(fx - r * 0.03, fy - r * 0.05, r * 0.05, r * 0.03, seed + i, 0.1, 6)}" fill="#FFFFFF" opacity="0.5"/>')
            out.append(ink(thigh, line, max(1.2, lw * 0.18), seed + i, 1, 0.5))
    d = blob(cx, cy, r, r * 0.96, seed, 0.035, 16)
    out.append(body(f"{u}-sb", d, (cx - r, cy - r, cx + r, cy + r), body_c, list(tints), seed, n=int(r * 2.2), angle=around(cx, cy),
                    length=(r * 0.2, r * 0.55), width=(1, r * 0.07), opacity=(0.25, 0.55), line=line, lw=max(1.8, r * 0.06)))
    out.append(dabs(["#7A6AA0", "#4A3A66"], seed + 4, (cx - r * 0.7, cy - r * 0.8, cx + r * 0.7, cy - r * 0.1), int(r * 0.8), around(cx, cy, 0),
                    (r * 0.06, r * 0.14), (0.6, 1.2), (0.4, 0.8), 0.3))
    out.append(f'<path d="M {_f(cx - r * 0.6)} {_f(cy - r * 0.38)} Q {_f(cx - r * 0.38)} {_f(cy - r * 0.8)} {_f(cx + r * 0.1)} {_f(cy - r * 0.78)}" stroke="#C9B8EA" '
               f'stroke-width="{_f(r * 0.1)}" fill="none" stroke-linecap="round" opacity="0.6"/>')
    er = r * 0.24
    for sgn in (-1, 1):
        ex, ey = cx + sgn * r * 0.34, cy - r * 0.05
        out.append(f'<path d="{blob(ex, ey, er, er * 1.08, seed + sgn, 0.04, 12)}" fill="#FFF7E6"/>' + ink(blob(ex, ey, er, er * 1.08, seed + sgn, 0.04, 12), line, 1.4, seed, 1, 0.6)
                   + f'<circle cx="{_f(ex + sgn * er * 0.1)}" cy="{_f(ey + er * 0.12)}" r="{_f(er * 0.6)}" fill="#1A1020"/>'
                   f'<circle cx="{_f(ex - er * 0.1)}" cy="{_f(ey - er * 0.15)}" r="{_f(er * 0.22)}" fill="#FFFFFF"/>'
                   f'<circle cx="{_f(ex + er * 0.25)}" cy="{_f(ey + er * 0.35)}" r="{_f(er * 0.1)}" fill="#FFFFFF"/>')
        out.append(f'<path d="{blob(cx + sgn * r * 0.62, cy + r * 0.34, r * 0.14, r * 0.08, seed + sgn, 0.1, 8)}" fill="#F29AB4" opacity="0.65"/>')
    my = cy + r * 0.38
    out.append(ink(f"M {_f(cx - r * 0.2)} {_f(my)} Q {_f(cx)} {_f(my + r * 0.22)} {_f(cx + r * 0.2)} {_f(my)}", "#FFF4E0", max(1.6, r * 0.06), seed, 1, 0.95))
    out.append(f'<path d="M {_f(cx - r * 0.1)} {_f(my + r * 0.07)} l {_f(r * 0.04)} {_f(r * 0.1)} l {_f(r * 0.04)} {_f(-r * 0.09)} Z" fill="#FFFFFF"/>')
    return "".join(out)


def crescent_d(cx, cy, r, off, r2=None, n=24):
    """Crescent moon opening to the right (lit limb on the left)."""
    r2 = r2 or r * 0.92
    outer = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in [90 + 180 * i / n for i in range(n + 1)]]
    inner = []
    for i in range(n + 1):
        y = cy - r + 2 * r * i / n
        dy = y - cy
        if abs(dy) >= r2:
            x = cx + off
        else:
            x = cx + off - math.sqrt(r2 * r2 - dy * dy)
        inner.append((x, y))
    return "M " + " L ".join(f"{_f(x)} {_f(y)}" for x, y in outer + inner) + " Z"


@design("creep-it-real")
def d_creep_it_real():
    u = "hgb-cir"
    out = [night_sky(u, 201, [(0, "#100C24"), (0.5, "#1E1A40"), (0.78, "#2C2450"), (1, "#16122C")],
                     ["#2A2250", "#36306A", "#1A1636", "#3E3470", "#243A3E"], n=300)]
    out.append(eglow(f"{u}-sg", 300, 470, 380, 170, "#6FA83A", 0.22))
    mx, my = 452, 142
    out.append(swirl(mx, my, 70, 170, ["#5B4888", "#7A66A8", "#3E3170", "#C9A86A"], 202, 60, (2, 7), (30, 90), (0.12, 0.34)))
    out.append(stars(203, (20, 20, 580, 360), 40, BONE, 6, keep=lambda x, y: math.hypot(x - mx, y - my) > 90))
    out.append(pmoon(f"{u}-mn", mx, my, 66, 204, halo_r=2.4, halo_op=0.4))
    out.append(cloud(f"{u}-cl", 500, 206, 170, 34, 205, "#4E3D82", "#8E7AC0", "#2A2050", line="#1A1430", op=0.95, k=5))
    # gnarled branches in both top corners that anchor the web
    ds = [limb_d([(-30, 40), (40, 52), (110, 60), (170, 56)], 26, 8, 206), limb_d([(60, 50), (80, 20), (96, -10)], 9, 3, 207),
          limb_d([(130, 58), (150, 84), (176, 96)], 8, 2.5, 208),
          limb_d([(630, 300), (580, 290), (540, 300)], 22, 7, 209), limb_d([(590, 292), (560, 262), (546, 240)], 8, 2.5, 210)]
    out.append(f'<g fill="{SIL}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    out.append(brush(f"{u}-br", ds, (-30, -10, 630, 320), ["#3A2C4C", "#0C0812", "#4A3A5E"], 211, 120, angle=-8, length=(12, 34), width=(1.2, 3),
                     opacity=(0.35, 0.7), curve=0.1))
    out.append(ink(smooth_open([(-30, 30), (40, 40), (110, 48), (170, 46)]), LILAC, 2.2, 212, 1, 0.5))
    # the web
    hub = (268, 196)
    out.append(web(f"{u}-wb", hub[0], hub[1], [186, 200, 210, 196, 178, 150, 150, 170, 190, 176, 172], [26, 50, 76, 102, 130, 158, 184], 213,
                   col="#EDE6F6", sw=2.2, op=0.88, sag=0.16, dew=True))
    # glinting dew on the web, catching moonlight
    rnd = random.Random(214)
    for _ in range(14):
        a, rr = rnd.uniform(0, 6.28), rnd.uniform(40, 180)
        x, y = hub[0] + rr * math.cos(a), hub[1] + rr * math.sin(a)
        if y > 380:
            continue
        out.append(glow(f"{u}-dw{_}", x, y, 7, "#FFF4C8", 0.7, 0.3) + f'<circle cx="{_f(x)}" cy="{_f(y)}" r="2.2" fill="#FFFFFF"/>')
    # spider, dangling on its thread from the hub
    for (ax, ay), (bx, by) in (((96, 120), (40, 52)), ((140, 72), (150, 58)), ((440, 210), (560, 262)), ((150, 330), (60, 392))):
        out.append(ink(f"M {ax} {ay} Q {(ax + bx) / 2:.1f} {(ay + by) / 2 + 6:.1f} {bx} {by}", "#EDE6F6", 1.8, ax, 1, 0.7))
    out.append(sock_spider(f"{u}-sp", 268, 318, 40, 215, body_c="#4E3C70", tints=("#6E5A96", "#33264E", "#8470AA", "#3E2E5E"), thread_top=hub[1]))
    # painted graveyard hill with little tombstones and a jack
    out.append(ground(f"{u}-hl", [(-20, 400), (100, 388), (220, 398), (380, 384), (500, 392), (620, 380)], 620, "#1A1530", ["#2A2246", "#100C20", "#342A54"],
                      216, rim="#7A68B0"))
    for x, b, w, h, rot in ((86, 396, 34, 44, -8), (520, 394, 30, 38, 6)):
        d = smooth_closed(jitter([(x - w / 2, b), (x - w / 2, b - h * 0.6), (x - w * 0.3, b - h * 0.92), (x, b - h), (x + w * 0.3, b - h * 0.92), (x + w / 2, b - h * 0.6), (x + w / 2, b)], x, 1))
        out.append(f'<g transform="rotate({rot} {x} {b})">' + body(f"{u}-ts{x}", d, (x - w / 2, b - h, x + w / 2, b), "#5A5270", ["#7A7294", "#3A3450", "#8A82A4"], x, n=20,
                                                                angle=-90, line="#0E0A18", lw=2) + rim_lit(f"{u}-tr{x}", d, -2, -2, "#B9A6E0", 2.4, 0.6)
                   + f'<path d="M {x - 6} {b - h * 0.55} l 12 0 M {x} {b - h * 0.7} l 0 16" stroke="#2A2440" stroke-width="2.4" opacity="0.6"/></g>')
    out.append(jack(f"{u}-jk", 160, 382, 44, 36, 220, face="sly", glow_r=70))
    out.append(grass_tufts(217, (0, 384, 600, 404), 50, ["#2A3A2E", "#3A5232", "#1A2420"], h=(6, 14)))
    out.append(defs(lg(f"{u}-fg", [(0, NIGHT, 0), (0.35, NIGHT, 0.55), (1, "#0A0816", 0.9)])) + f'<rect y="404" width="600" height="196" fill="url(#{u}-fg)"/>')
    out.append(script(300, 456, "creep it", 74, BONE, 380, shadow="#05030A", sd=(2, 4)))
    out.append(eglow(f"{u}-tg", 300, 504, 200, 50, "#FF8A2A", 0.22))
    out.append(bword(f"{u}-t", 300, 540, "REAL", ANTON, 96, PUMPKIN, ["#F8A85A", "#C9541A", "#FFC27A", "#E06A1E"], 218, max_w=340, ls=22,
                     shadow="#3A1408", hi="#FFE2B0"))
    out.append(grain_over(f"{u}-gr", 219))
    return "".join(out)


# ---------------------------------------------------------------- full moon club
def painted_wolf(u, x, base, s, seed, fill="#120E1E", tints=("#2A2240", "#0A0612", "#3A3054"), rim="#E8D8A8"):
    """Howling wolf, sitting in profile facing right: smoothed silhouette, fur strokes, moon rim light."""
    body_pts = [(-66, 0), (-78, -20), (-77, -46), (-66, -64), (-52, -80), (-40, -100), (-32, -118), (-27, -134), (-23, -148), (-25, -160),
                (-30, -180), (-30, -180), (-14, -167), (-4, -171), (8, -183), (21, -196), (33, -208), (33, -208), (38, -204), (29, -196), (24, -191),
                (33, -186), (33, -186), (22, -178), (13, -165), (9, -151), (15, -143), (9, -135), (16, -125), (11, -115), (17, -98), (16, -72),
                (18, -40), (19, -10), (31, -6), (32, 0), (32, 0), (4, 0), (4, 0), (5, -28), (-2, -42), (-10, -22), (-2, -6), (-2, 0), (-2, 0)]
    tail = [(-62, -4), (-86, -2), (-108, -8), (-124, -20), (-120, -30), (-108, -26), (-92, -22), (-76, -24), (-64, -26)]
    T = lambda pts: [(x + px * s, base + py * s) for px, py in pts]  # noqa: E731
    bd = smooth_closed(jitter(T(body_pts), seed, 0.4))
    td = smooth_closed(jitter(T(tail), seed + 1, 0.6))
    out = [f'<path d="{td}" fill="{fill}" stroke="{fill}" stroke-width="{_f(3 * s)}" stroke-linejoin="round"/>',
           f'<path d="{bd}" fill="{fill}" stroke="{fill}" stroke-width="{_f(2 * s)}" stroke-linejoin="round"/>']
    out.append(brush(f"{u}-wf", [bd, td], (x - 110 * s, base - 170 * s, x + 40 * s, base), list(tints), seed, int(s * 140), angle=-100,
                     length=(8 * s, 22 * s), width=(1, 2.4 * s), opacity=(0.35, 0.7), curve=0.25))
    out.append(rim_lit(f"{u}-rl", bd, -1.8, 1.4, rim, 2.6, 0.75))
    out.append(ink(smooth_open(T(tail[2:7])), rim, 1.8, seed, 1, 0.6))
    out.append(dabs([rim], seed + 5, (x + 6 * s, base - 150 * s, x + 18 * s, base - 100 * s), 8, 150, (5 * s, 10 * s), (0.6, 1.2), (0.3, 0.6), 0.3))
    ex, ey = T([(10, -178)])[0]
    out.append(f'<path d="M {_f(ex - 3 * s)} {_f(ey)} q {_f(3 * s)} {_f(-2.5 * s)} {_f(6 * s)} 0" stroke="{rim}" stroke-width="{_f(1.6 * s)}" fill="none" stroke-linecap="round"/>')
    return "".join(out)


def pine(u, x, base, h, seed, fill="#141A2A", rim=None):
    """Small painted fir silhouette with ragged tiers."""
    rnd = random.Random(seed)
    pts = [(x, base - h)]
    tiers = 6
    for i in range(1, tiers + 1):
        t = i / tiers
        w = h * 0.3 * t + rnd.uniform(-1.5, 1.5)
        y = base - h + h * t * 0.92
        pts.append((x + w, y))
        if i < tiers:
            pts.append((x + w * 0.45, y - h * 0.03))
    rpts = [(2 * x - px, py) for px, py in reversed(pts[1:])]
    pts = pts + [(x + 2, base), (x - 2, base)] + rpts
    d = "M " + " L ".join(f"{_f(px)} {_f(py)}" for px, py in jitter(pts, seed, 0.8)) + " Z"
    out = f'<path d="{d}" fill="{fill}"/>'
    if rim:
        out += ink(smooth_open([(x, base - h)] + [p for p in pts[1:12:2]]), rim, 1.4, seed, 1, 0.5)
    return out


@design("full-moon-club")
def d_full_moon_club():
    u = "hgb-fmc"
    # flannel-plaid ground, painted
    out = [f'<rect width="600" height="600" fill="#1C2236"/>']
    pl = []
    for k in range(-1, 9):
        pl.append(f'<rect x="{k * 80 + 10}" y="0" width="34" height="600" fill="#2A3150" opacity="0.7"/>')
        pl.append(f'<rect x="0" y="{k * 80 + 10}" width="600" height="34" fill="#2A3150" opacity="0.7"/>')
        pl.append(f'<rect x="{k * 80 + 52}" y="0" width="4" height="600" fill="#6E5398" opacity="0.5"/>')
        pl.append(f'<rect x="0" y="{k * 80 + 52}" width="600" height="4" fill="#6E5398" opacity="0.5"/>')
    out.append("".join(pl))
    out.append(dabs(["#2E3654", "#141A2C", "#3A4266", "#232A44"], 230, (-40, -20, 620, 620), 380, lambda x, y: -90 if int(x * 7 + y * 3) % 2 else 0,
                    (20, 50), (2, 5), (0.15, 0.35), 0.08, 3))
    out.append(eglow(f"{u}-vg", 300, 300, 420, 420, "#000000", 0.0))
    cx, cy, R = 300, 300, 236
    # badge ring
    ring = blob(cx, cy, R, R, 231, 0.012, 32)
    out.append(cast_shadow(cx + 6, cy + 9, R, R, "#05030A", 0.5, 231))
    out.append(body(f"{u}-rg", ring, (cx - R, cy - R, cx + R, cy + R), "#4A2E6A", ["#6A4A8E", "#33204E", "#7A5AA2", "#3E2660"], 232, n=260,
                    angle=around(cx, cy), length=(24, 60), width=(2, 6), opacity=(0.2, 0.5), curve=0.05, line="#120A1E", lw=3))
    out.append(ink(blob(cx, cy, R - 10, R - 10, 233, 0.01, 32), "#C9A86A", 2.4, 233, 1, 0.75))
    # inner scene
    ri = 172
    sd = blob(cx, cy, ri, ri, 234, 0.008, 32)
    sc = [defs(lg(f"{u}-sk", [(0, "#16183A"), (0.6, "#2E2C5E"), (1, "#4A3E78")])), f'<rect x="{cx - ri}" y="{cy - ri}" width="{2 * ri}" height="{2 * ri}" fill="url(#{u}-sk)"/>',
          dabs(["#2A2A58", "#3A3870", "#1A1A40", "#4A4682"], 235, (cx - ri - 60, cy - ri, cx + ri, cy + ri), 160, -4, (30, 90), (3, 8), (0.15, 0.38), 0.1),
          stars(236, (cx - ri, cy - ri, cx + ri, cy + 40), 26, BONE, 4, keep=lambda x, y: math.hypot(x - 330, y - 262) > 110),
          pmoon(f"{u}-mn", 330, 262, 92, 237, halo_r=1.8, halo_op=0.45),
          ground(f"{u}-h1", [(cx - ri, 372), (200, 360), (300, 368), (400, 352), (cx + ri, 362)], cy + ri, "#1E2240", ["#2A3058", "#141832"], 239)]
    for i, (x, h) in enumerate(((150, 74), (172, 52), (412, 66), (436, 88), (460, 56), (194, 40))):
        sc.append(pine(f"{u}-pn{i}", x, 372 - (i % 2) * 4, h, 240 + i, fill="#151A30", rim="#6A70A8"))
    rock = smooth_closed(jitter([(170, 480), (190, 420), (226, 394), (284, 382), (338, 386), (372, 404), (396, 480)], 246, 2))
    sc.append(body(f"{u}-rk", rock, (170, 382, 396, 480), "#3A3E60", ["#4E5278", "#22263E", "#5E6288"], 247, angle=-30, length=(10, 30), width=(1.5, 4),
                   line="#0A0A16", lw=2.4))
    sc.append(shade_in(f"{u}-rs", rock, f'<path d="M 170 430 Q 280 410 400 440 L 400 490 L 170 490 Z" fill="#14162A"/>', "#000", 0.6))
    sc.append(rim_lit(f"{u}-rr", rock, 1, 3, "#E8D8A8", 3, 0.55))
    sc.append(dabs(["#6E7298", "#2A2E4A"], 249, (190, 390, 380, 440), 26, -20, (6, 16), (1, 2), (0.4, 0.7), 0.2))
    sc.append(painted_wolf(f"{u}-wf", 292, 388, 0.92, 248))
    sc.append(mist_band(f"{u}-ms", cx - ri, 452, 2 * ri, 24, 249, op=0.22))
    out.append(clip(f"{u}-sc", sd) + f'<g clip-path="url(#{u}-sc)">' + "".join(sc) + "</g>")
    out.append(ink(sd, "#120A1E", 3.2, 250, 2, 0.9))
    out.append(ink(blob(cx, cy, ri + 6, ri + 6, 251, 0.01, 32), BONE_D, 1.8, 251, 1, 0.6))
    # lettering around the ring
    fs = fit_size("FULL MOON CLUB", BEBAS, 50, math.pi * 204 * 0.62, 10)
    out.append(arc_word("FULL MOON CLUB", cx, cy, 196, BEBAS, fs, "#2A1440", ls=10, uid=f"{u}-a1s", dy=2.5))
    out.append(arc_word("FULL MOON CLUB", cx, cy, 196, BEBAS, fs, BONE, ls=10, uid=f"{u}-a1"))
    out.append(arc_word("HOWL · SINCE · DUSK", cx, cy, 214, MONO, 21, "#E8D8FF", ls=5, uid=f"{u}-a2", top=False))
    for sg in (-1, 1):
        out.append(twinkle(cx + sg * 204, cy + 6, 11, GOLD, 1, 252 + sg))
    out.append(grain_over(f"{u}-gr", 253))
    return "".join(out)


def arc_word(s, cx, cy, r, font, size, fill, ls=0, uid="arc", top=True, dy=0):
    """Text on an arc. top=True reads along the top; bottom text sits outside-in so it reads upright."""
    if top:
        d = f"M {_f(cx - r)} {_f(cy + dy)} A {r} {r} 0 0 1 {_f(cx + r)} {_f(cy + dy)}"
    else:
        r2 = r - size * 0.72
        d = f"M {_f(cx - r2)} {_f(cy + dy)} A {r2} {r2} 0 0 0 {_f(cx + r2)} {_f(cy + dy)}"
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return (defs(f'<path id="{uid}" d="{d}" fill="none"/>')
            + f'<text {font} font-size="{size:.1f}"{lsa} fill="{fill}" text-anchor="middle"><textPath href="#{uid}" startOffset="50%">{esc(s)}</textPath></text>')


def mist_band(u, x, y, w, h, seed, col="#C9C2E8", op=0.35):
    rnd = random.Random(seed)
    out = []
    for _ in range(9):
        px = x + rnd.uniform(0, w)
        out.append(f'<path d="{blob(px, y + rnd.uniform(-h / 2, h / 2), rnd.uniform(40, 90), rnd.uniform(6, 12), rnd.randrange(999), 0.1, 12)}" fill="{col}" '
                   f'opacity="{rnd.uniform(op * 0.4, op):.2f}"/>')
    return "".join(out)


# ---------------------------------------------------------------- ghouls' night out
def bulb_string(u, x0, y0, x1, y1, sag, n, seed, cols=(GOLD, PUMPKIN, SLIME, "#B08AE0", "#FFE29A"), wire="#1A1422", glow_on=True, r=7):
    """A swag of painted party bulbs with soft glows."""
    rnd = random.Random(seed)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    out = [ink(f"M {_f(x0)} {_f(y0)} Q {_f(mx)} {_f(my + sag)} {_f(x1)} {_f(y1)}", wire, 2.4, seed, 2, 0.95)]
    for i in range(n):
        t = (i + 0.5) / n
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * (my + sag) + t * t * y1
        c = cols[i % len(cols)]
        if glow_on:
            out.append(glow(f"{u}-g{i}", x, y + r * 1.4, r * 4.2, c, 0.55, 0.3))
        b = blob(x, y + r * 1.5, r * 0.75, r * 1.05, seed + i, 0.05, 10)
        out.append(f'<rect x="{_f(x - r * 0.4)}" y="{_f(y)}" width="{_f(r * 0.8)}" height="{_f(r * 0.6)}" rx="1" fill="{wire}"/>')
        out.append(f'<path d="{b}" fill="{c}"/>' + f'<path d="{blob(x - r * 0.22, y + r * 1.3, r * 0.25, r * 0.45, seed + i, 0.1, 8)}" fill="#FFFFFF" opacity="0.75"/>'
                   + ink(b, "#2A1830", 1.2, seed + i, 1, 0.5))
    return "".join(out)


def party_hat(u, cx, base, w, h, rot, seed, col=SLIME, dark=SLIME_D, dots="#FFE29A", pom=PUMPKIN, line=INKN):
    d = smooth_closed([(cx - w / 2, base), (cx - w * 0.1, base - h * 0.7), (cx, base - h), (cx + w * 0.1, base - h * 0.7), (cx + w / 2, base), (cx, base + h * 0.06)])
    inner = (dabs([dark, "#C6F27A", col], seed, (cx - w / 2, base - h, cx + w / 2, base), 18, -70, (h * 0.15, h * 0.4), (1, 2.4), (0.3, 0.6), 0.1)
             + "".join(f'<path d="M {_f(cx - w)} {_f(base - h * k)} Q {_f(cx)} {_f(base - h * k + h * 0.12)} {_f(cx + w)} {_f(base - h * k)}" stroke="{PUMPKIN}" stroke-width="{_f(h * 0.07)}" fill="none"/>'
                       for k in (0.18, 0.5))
             + "".join(f'<circle cx="{_f(cx + dx * w)}" cy="{_f(base - dy * h)}" r="{_f(w * 0.05)}" fill="{dots}"/>' for dx, dy in ((-0.2, 0.32), (0.15, 0.36), (0.02, 0.66), (0.24, 0.1), (-0.3, 0.06))))
    pm = blob(cx, base - h - w * 0.06, w * 0.14, w * 0.14, seed, 0.15, 10)
    return (f'<g transform="rotate({rot} {_f(cx)} {_f(base)})"><path d="{d}" fill="{col}"/>' + clip(f"{u}-ph", d) + f'<g clip-path="url(#{u}-ph)">{inner}</g>'
            + ink(d, line, 2, seed, 2, 0.85) + f'<path d="{pm}" fill="{pom}"/>' + ink(pm, line, 1.4, seed, 1, 0.7) + "</g>")


def sparkler(u, x, y, L, ang, seed):
    """Little hand sparkler: a wire with a starburst of painted sparks at the tip."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    tx, ty = x + L * math.cos(a), y + L * math.sin(a)
    out = [ink(f"M {_f(x)} {_f(y)} L {_f(tx)} {_f(ty)}", "#8A8296", 2.4, seed, 1, 1), glow(f"{u}-sg", tx, ty, 34, "#FFE29A", 0.75, 0.25)]
    for _ in range(20):
        b = rnd.uniform(0, 6.28)
        r0, r1 = rnd.uniform(2, 6), rnd.uniform(10, 22)
        out.append(f'<path d="M {_f(tx + r0 * math.cos(b))} {_f(ty + r0 * math.sin(b))} L {_f(tx + r1 * math.cos(b))} {_f(ty + r1 * math.sin(b))}" '
                   f'stroke="{rnd.choice(["#FFFFFF", "#FFE29A", GOLD])}" stroke-width="{rnd.uniform(1.2, 2.2):.1f}" stroke-linecap="round" opacity="{rnd.uniform(0.6, 1):.2f}"/>')
    out.append(twinkle(tx, ty, 7, "#FFFFFF", 1, seed))
    return "".join(out)


def rooftops_painted(u, base, seed, fill="#141026", lit=("#FFD27A", "#FFB547"), rim="#6A5A98"):
    """Row of painted gabled rooftops with chimneys and a few warm windows."""
    rnd = random.Random(seed)
    out = []
    x = -20
    ds = []
    wins = []
    while x < 620:
        w = rnd.uniform(60, 96)
        h = rnd.uniform(40, 80)
        roof = rnd.uniform(18, 34)
        top = base - h
        ds.append(smooth_closed(jitter([(x, base + 40), (x, top), (x + w / 2, top - roof), (x + w, top), (x + w, base + 40)], rnd.randrange(999), 0.8)))
        if rnd.random() < 0.6:
            cxh = x + w * rnd.uniform(0.6, 0.8)
            ds.append(f"M {_f(cxh)} {_f(top - roof * 0.3)} L {_f(cxh)} {_f(top - roof - 10)} L {_f(cxh + 9)} {_f(top - roof - 10)} L {_f(cxh + 9)} {_f(top)} Z")
        for k in range(rnd.randint(1, 3)):
            wx, wy = x + rnd.uniform(10, w - 22), top + rnd.uniform(10, h - 14)
            wins.append((wx, wy))
        x += w - 2
    out.append(f'<g fill="{fill}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    out.append(brush(f"{u}-rb", ds, (-20, base - 140, 620, base + 40), ["#221A36", "#0C0816", "#2C2442"], seed, 140, angle=-90, length=(8, 24), width=(1.2, 3),
                     opacity=(0.3, 0.6)))
    for i, (wx, wy) in enumerate(wins):
        if rnd.random() < 0.75:
            out.append(glow(f"{u}-wg{i}", wx + 6, wy + 7, 16, lit[1], 0.4, 0.3) + f'<path d="{blob(wx + 6, wy + 7, 5, 7, i, 0.08, 8)}" fill="{rnd.choice(lit)}"/>'
                       + f'<path d="M {_f(wx + 6)} {_f(wy + 1)} L {_f(wx + 6)} {_f(wy + 13)}" stroke="{fill}" stroke-width="1.4"/>')
    return "".join(out)


@design("ghouls-night-out")
def d_ghouls_night_out():
    u = "hgb-gno"
    out = [night_sky(u, 260, [(0, "#110D26"), (0.5, "#221C48"), (0.85, "#3A2A5E"), (1, "#2A2048")],
                     ["#2A2250", "#3A2E66", "#1A1636", "#4A3A74"], n=300)]
    out.append(stars(261, (20, 20, 580, 300), 36, BONE, 6, keep=lambda x, y: math.hypot(x - 104, y - 226) > 70))
    out.append(swirl(104, 226, 50, 120, ["#5B4888", "#7A66A8", "#C9A86A"], 262, 30, (2, 6), (30, 80), (0.12, 0.3)))
    out.append(pmoon(f"{u}-mn", 104, 226, 40, 263, halo_r=2.6, halo_op=0.35))
    out.append(rooftops_painted(f"{u}-rt", 470, 264, fill="#1E1736"))
    lane = smooth_closed([(-20, 468), (620, 468), (620, 620), (-20, 620)])
    out.append(body(f"{u}-ln", lane, (-20, 468, 620, 620), "#2A2240", ["#3A3052", "#1A142C", "#46395E"], 265, n=120, angle=0, length=(30, 80), width=(2, 5)))
    out.append(eglow(f"{u}-lg", 300, 470, 300, 60, "#FFB547", 0.32))
    out.append(bulb_string(f"{u}-s1", -20, 170, 620, 150, 34, 12, 266))
    out.append(cast_shadow(140, 466, 54, 8, "#05030A", 0.5, 268) + cast_shadow(300, 472, 74, 10, "#05030A", 0.5, 269) + cast_shadow(462, 466, 50, 8, "#05030A", 0.5, 270))
    # pumpkin balloon held by the little ghost on the right
    out.append(ink("M 524 372 Q 512 330 516 268", "#E8DCC8", 1.6, 281, 1, 0.9))
    bl = blob(516, 236, 26, 30, 282, 0.05, 16)
    out.append(body(f"{u}-bl", bl, (490, 206, 542, 266), PUMPKIN, ["#F8A85A", "#C9541A", "#FFC27A"], 282, n=30, angle=-90, line="#5A2410", lw=2))
    out.append(f'<path d="M 506 222 Q 504 236 510 248" stroke="#FFE2B8" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.8"/>'
               f'<path d="M 512 266 l 4 6 l 4 -6 Z" fill="{PUMPKIN_D}"/>' + ink("M 516 208 q 2 -8 8 -10", "#4A6228", 2.4, 283, 1, 1))
    out.append(ghost(f"{u}-g1", 140, 312, 100, 128, 271, lean=-0.06, face="oh", arms=(1, 1), arm_up=(0, 1), line="#2A1830", base="#F1EAF8"))
    out.append(sparkler(f"{u}-sk", 182, 340, 38, -62, 272))
    out.append(mitten(f"{u}-m1", 182, 342, 100, -40, 273))
    out.append(ghost(f"{u}-g3", 462, 316, 96, 124, 274, lean=0.05, face="happy", arms=(1, 1), arm_up=(1, 1), line="#2A1830", base="#FFF6EA"))
    out.append(ghost(f"{u}-g2", 300, 254, 140, 180, 275, lean=0.0, face="smile", arms=(1, 1), arm_up=(0, 0), line="#2A1830"))
    out.append(party_hat(f"{u}-h2", 306, 268, 44, 60, 10, 276))
    out.append(party_hat(f"{u}-h1", 134, 322, 32, 44, -16, 277, col="#B08AE0", dark="#6E5398"))
    out.append(party_hat(f"{u}-h3", 468, 326, 30, 42, 14, 278, col=PUMPKIN, dark=PUMPKIN_D, pom=SLIME))
    out.append(script(300, 128, "ghouls'", 74, BONE, 300, shadow="#05030A", sd=(2, 4)))
    out.append(defs(lg(f"{u}-fg", [(0, NIGHT, 0), (0.4, NIGHT, 0.55), (1, "#0A0816", 0.85)])) + f'<rect y="470" width="600" height="130" fill="url(#{u}-fg)"/>')
    out.append(bword(f"{u}-t", 300, 540, "NIGHT OUT", ANTON, 72, GOLD, ["#FFE29A", "#E8792E", "#FFD06A", "#C9601E"], 279, max_w=430, ls=8,
                     shadow="#3A1A08", hi="#FFF2C0"))
    out.append(grain_over(f"{u}-gr", 280))
    return "".join(out)


# ================================================================ new designs
# ---------------------------------------------------------------- purrfectly spooky
def front_cat(u, cx, base, H, seed, fur="#1E1830", tints=("#2E2648", "#120E1C", "#3A3058", "#251E3A"), rim="#FFCF7A", line="#0C0814",
              eye=("#E8FF9A", SLIME, "#4E7A1E"), bow=PUMPKIN, bow_d=PUMPKIN_D, tail_side=1):
    """Cute black cat sitting face-on: painted fur, moonlit rim, big glowing eyes, a ribbon collar with a bell."""
    S = lambda pts: [(cx + x * H, base + y * H) for x, y in pts]  # noqa: E731
    out = []
    ts = tail_side
    tail = limb_d(S([(0.26 * ts, -0.06), (0.42 * ts, -0.08), (0.52 * ts, -0.2), (0.5 * ts, -0.36), (0.42 * ts, -0.44), (0.36 * ts, -0.4)]), H * 0.085, H * 0.04, seed + 1)
    out.append(body(f"{u}-tl", tail, (cx - H * 0.6, base - H * 0.5, cx + H * 0.6, base), fur, list(tints), seed + 1, n=26, angle=around(cx + 0.42 * ts * H, base - 0.24 * H),
                    length=(H * 0.04, H * 0.1), width=(1, 2.2), opacity=(0.35, 0.7), line=line, lw=2))
    out.append(rim_lit(f"{u}-tr", tail, -1.5 * ts, 2, rim, 2.6, 0.7))
    bd = smooth_closed(jitter(S([(-0.3, 0), (-0.35, -0.12), (-0.31, -0.3), (-0.21, -0.48), (-0.12, -0.56), (0.12, -0.56), (0.21, -0.48), (0.31, -0.3),
                                 (0.35, -0.12), (0.3, 0), (0, 0.01)]), seed, H * 0.004))
    out.append(body(f"{u}-bd", bd, (cx - H * 0.36, base - H * 0.58, cx + H * 0.36, base), fur, list(tints), seed, n=int(H * 0.9), angle=-90,
                    length=(H * 0.04, H * 0.11), width=(1, 2.4), opacity=(0.35, 0.7), curve=0.3, line=line, lw=2.4))
    out.append(rim_lit(f"{u}-br", bd, 0, 2.4, rim, 3, 0.7))
    # front legs and paws
    for sg in (-1, 1):
        out.append(ink(smooth_open(S([(0.13 * sg, -0.36), (0.12 * sg, -0.2), (0.11 * sg, -0.04)])), "#3A3058", 2.2, seed + sg, 1, 0.8))
        pw = blob(cx + 0.07 * sg * H, base - 0.025 * H, 0.075 * H, 0.04 * H, seed + 5 + sg, 0.06, 10)
        out.append(f'<path d="{pw}" fill="{fur}"/>' + ink(pw, line, 1.8, seed, 1, 0.8)
                   + f'<path d="M {_f(cx + 0.07 * sg * H - 0.03 * H)} {_f(base - 0.05 * H)} q {_f(0.03 * H)} {_f(-0.012 * H)} {_f(0.06 * H)} 0" stroke="{rim}" stroke-width="1.8" fill="none" opacity="0.6" stroke-linecap="round"/>')
    # head with ears
    hd = smooth_closed(jitter(S([(-0.26, -0.66), (-0.25, -0.8), (-0.26, -0.99), (-0.26, -0.99), (-0.1, -0.87), (0, -0.885), (0.1, -0.87), (0.26, -0.99), (0.26, -0.99),
                                 (0.25, -0.8), (0.26, -0.66), (0.2, -0.53), (0, -0.48), (-0.2, -0.53)]), seed + 2, H * 0.003))
    out.append(body(f"{u}-hd", hd, (cx - H * 0.28, base - H, cx + H * 0.28, base - H * 0.47), fur, list(tints), seed + 2, n=int(H * 0.5),
                    angle=around(cx, base - 0.68 * H, 0), length=(H * 0.03, H * 0.08), width=(1, 2), opacity=(0.35, 0.7), line=line, lw=2.4))
    out.append(rim_lit(f"{u}-hr", hd, 0, 2.4, rim, 3, 0.75))
    for sg in (-1, 1):
        ear = smooth_closed(S([(0.2 * sg, -0.82), (0.235 * sg, -0.95), (0.12 * sg, -0.87)]))
        out.append(f'<path d="{ear}" fill="#8A4E7A" opacity="0.75"/>')
    # eyes
    er = 0.07 * H
    for sg in (-1, 1):
        ex, ey = cx + sg * 0.11 * H, base - 0.7 * H
        ed = smooth_closed([(ex - er * 1.15, ey + er * 0.1), (ex - er * 0.4, ey - er * 0.95), (ex + er * 0.6, ey - er * 0.85), (ex + er * 1.15, ey - er * 0.05),
                            (ex + er * 0.4, ey + er * 0.95), (ex - er * 0.6, ey + er * 0.85)])
        out.append(glow(f"{u}-eg{sg + 1}", ex, ey, er * 2.4, eye[1], 0.35, 0.3))
        out.append(defs(rg(f"{u}-ef{sg + 1}", [(0, eye[0]), (0.6, eye[1]), (1, eye[2])], cy=0.4)))
        out.append(f'<path d="{ed}" fill="url(#{u}-ef{sg + 1})"/>' + ink(ed, line, 1.8, seed, 1, 0.9))
        out.append(f'<ellipse cx="{_f(ex + sg * er * 0.05)}" cy="{_f(ey + er * 0.05)}" rx="{_f(er * 0.42)}" ry="{_f(er * 0.82)}" fill="#0C0814"/>'
                   f'<circle cx="{_f(ex - er * 0.3)}" cy="{_f(ey - er * 0.38)}" r="{_f(er * 0.26)}" fill="#FFFFFF"/>'
                   f'<circle cx="{_f(ex + er * 0.3)}" cy="{_f(ey + er * 0.35)}" r="{_f(er * 0.12)}" fill="#FFFFFF" opacity="0.8"/>')
        out.append(f'<path d="{blob(cx + sg * 0.17 * H, base - 0.6 * H, 0.045 * H, 0.025 * H, seed + sg, 0.1, 8)}" fill="#E07AA0" opacity="0.5"/>')
        for k, dy in enumerate((-0.012, 0.01)):
            out.append(ink(f"M {_f(cx + sg * 0.12 * H)} {_f(base + (dy - 0.6) * H)} Q {_f(cx + sg * 0.25 * H)} {_f(base + (dy - 0.61 - k * 0.01) * H)} {_f(cx + sg * 0.36 * H)} {_f(base + (dy - 0.6 + k * 0.03) * H)}",
                           "#CFC2EA", 1.5, seed + k, 1, 0.75))
    nx, ny = cx, base - 0.625 * H
    out.append(f'<path d="M {_f(nx - 0.022 * H)} {_f(ny)} L {_f(nx + 0.022 * H)} {_f(ny)} L {_f(nx)} {_f(ny + 0.02 * H)} Z" fill="#E88AAE"/>')
    out.append(ink(f"M {_f(nx - 0.035 * H)} {_f(ny + 0.04 * H)} Q {_f(nx - 0.017 * H)} {_f(ny + 0.055 * H)} {_f(nx)} {_f(ny + 0.025 * H)} Q {_f(nx + 0.017 * H)} {_f(ny + 0.055 * H)} {_f(nx + 0.035 * H)} {_f(ny + 0.04 * H)}",
                   "#CFC2EA", 1.6, seed, 1, 0.9))
    # ribbon collar, bow and bell
    cy_ = base - 0.52 * H
    out.append(ink(f"M {_f(cx - 0.17 * H)} {_f(cy_ - 0.01 * H)} Q {_f(cx)} {_f(cy_ + 0.05 * H)} {_f(cx + 0.17 * H)} {_f(cy_ - 0.01 * H)}", bow, H * 0.03, seed, 1, 1))
    out.append(bow_tie(f"{u}-bw", cx - 0.07 * H, cy_ + 0.015 * H, 0.08 * H, seed, bow, bow_d))
    bl = blob(cx + 0.03 * H, cy_ + 0.06 * H, 0.03 * H, 0.03 * H, seed + 9, 0.05, 10)
    out.append(f'<path d="{bl}" fill="{GOLD}"/>' + ink(bl, "#6A4A10", 1.4, seed, 1, 0.9)
               + f'<circle cx="{_f(cx + 0.02 * H)}" cy="{_f(cy_ + 0.05 * H)}" r="{_f(0.009 * H)}" fill="#FFF6D0"/>')
    return "".join(out)


def bow_tie(u, cx, cy, s, seed, col, dark, line=INKN):
    out = []
    for sg in (-1, 1):
        lp = smooth_closed([(cx + sg * s * 0.1, cy), (cx + sg * s * 0.8, cy - s * 0.5), (cx + sg * s, cy - s * 0.1), (cx + sg * s * 0.85, cy + s * 0.45), (cx + sg * s * 0.1, cy + s * 0.08)])
        out.append(body(f"{u}-{sg + 1}", lp, (cx - s, cy - s * 0.5, cx + s, cy + s * 0.5), col, [PUMPKIN_L, dark], seed + sg, n=8, angle=-20 * sg,
                        length=(s * 0.2, s * 0.5), width=(1, 1.6), line=line, lw=1.6))
    kn = blob(cx, cy, s * 0.2, s * 0.25, seed, 0.08, 8)
    return "".join(out) + f'<path d="{kn}" fill="{dark}"/>' + ink(kn, line, 1.4, seed, 1, 0.8)


def corn_silhouette(u, x, base, h, seed, fill="#1A1430", rim="#6A5A98", lean=0.0):
    """Dry corn stalk silhouette with drooping painted leaves."""
    rnd = random.Random(seed)
    top = (x + lean * h, base - h)
    ds = [limb_d([(x, base), (x + lean * h * 0.5, base - h * 0.5), top], 6, 2.5, seed)]
    for i in range(6):
        t = 0.18 + i * 0.13
        px, py = x + lean * h * t, base - h * t
        sg = 1 if i % 2 else -1
        L = h * rnd.uniform(0.25, 0.36)
        ds.append(limb_d([(px, py), (px + sg * L * 0.5, py - L * 0.3), (px + sg * L, py + L * rnd.uniform(0.05, 0.4))], 6, 1, seed + i))
    out = f'<g fill="{fill}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>"
    out += ink(smooth_open([(x - 2, base), (x + lean * h * 0.5 - 2, base - h * 0.5), (top[0] - 1, top[1])]), rim, 1.4, seed, 1, 0.5)
    return out


@design("purrfectly-spooky")
def d_purrfectly_spooky():
    u = "hgb-pfs"
    out = [night_sky(u, 301, [(0, "#120E28"), (0.55, "#2A1E4E"), (0.85, "#4A2E60"), (1, "#5A3460")],
                     ["#2A2050", "#3A2A62", "#1A1434", "#4A3470", "#5A3A6E"], n=300)]
    mx, my, mr = 300, 242, 128
    out.append(swirl(mx, my, mr + 8, mr + 120, ["#6A4A88", "#8A5A88", "#4E3A7A", "#C98A5A", "#E0A060"], 302, 100, (3, 9), (40, 120), (0.12, 0.36)))
    out.append(stars(303, (20, 20, 580, 440), 40, BONE, 6, keep=lambda x, y: math.hypot(x - mx, y - my) > mr + 26))
    out.append(pmoon(f"{u}-mn", mx, my, mr, 304, base="#F6BE6A", tints=("#FFE0A0", "#E89A4A", "#FFD08A", "#D8843A"), shade="#C06A2E",
                     halo="#FFB060", halo_r=1.9, halo_op=0.45, line="#A85A24"))
    out.append(bat(f"{u}-b1", 154, 166, 30, 305, rot=-14, flap=0.3))
    out.append(bat(f"{u}-b2", 456, 150, 22, 306, rot=10, flap=-0.2))
    out.append(bat(f"{u}-b3", 498, 214, 16, 307, rot=18, flap=0.1))
    # hills with a pumpkin patch and corn silhouettes
    out.append(corn_silhouette(f"{u}-cs1", 70, 430, 190, 308, lean=0.06))
    out.append(corn_silhouette(f"{u}-cs2", 112, 436, 150, 309, lean=-0.04))
    out.append(corn_silhouette(f"{u}-cs3", 532, 432, 184, 310, lean=-0.06))
    out.append(corn_silhouette(f"{u}-cs4", 492, 440, 140, 311, lean=0.05))
    out.append(ground(f"{u}-hl", [(-20, 420), (100, 404), (220, 414), (300, 406), (420, 412), (520, 398), (620, 410)], 620, "#1E1636",
                      ["#2E244A", "#120C22", "#3A2E58"], 312, rim="#C98A5A"))
    for i, (x, y, w) in enumerate(((96, 426, 46), (514, 422, 40), (160, 440, 30), (450, 444, 28))):
        out.append(painted_pumpkin(f"{u}-pp{i}", x, y, w, w * 0.72, 313 + i, "#C9602A", "#8A3A16", "#E8863A", "#4A3E22", "#4E6A2E"))
    # the big pumpkin seat and the cat
    out.append(glow(f"{u}-pg", 300, 390, 160, "#FF9A40", 0.25, 0.4))
    out.append(cast_shadow(300, 446, 116, 12, "#05030A", 0.5, 317))
    out.append(painted_pumpkin(f"{u}-big", 300, 388, 196, 118, 318))
    out.append(front_cat(f"{u}-cat", 296, 340, 212, 319))
    # lettering
    fs = fit_size("PURRFECTLY", BEBAS, 52, 330, 10)
    out.append(arc_word("PURRFECTLY", mx, my, mr + 18, BEBAS, fs, "#2A1440", ls=10, uid=f"{u}-a1s", dy=2.5))
    out.append(arc_word("PURRFECTLY", mx, my, mr + 18, BEBAS, fs, BONE, ls=10, uid=f"{u}-a1"))
    out.append(defs(lg(f"{u}-fg", [(0, NIGHT, 0), (0.5, NIGHT, 0.6), (1, "#0A0816", 0.85)])) + f'<rect y="440" width="600" height="160" fill="url(#{u}-fg)"/>')
    out.append(bword(f"{u}-t", 300, 528, "spooky", SERIF_IT, 100, PUMPKIN_L, ["#FFD08A", "#E8792E", "#FFE2B0", "#C9601E"], 320, max_w=380,
                     shadow="#2A0E04", angle=-60, hi="#FFF2C0"))
    out.append(grain_over(f"{u}-gr", 321))
    return "".join(out)


# ---------------------------------------------------------------- wrap it up
def mummy(u, cx, base, H, seed, wrap="#F1E6CF", tints=("#FFFFFF", "#E2D2B2", "#F8F0DC", "#CDBB96"), gap="#8A7A62", line="#3A2A2A",
          eye_band="#2A1A2E", wave=True):
    """Chibi mummy: bean body wrapped in painted bandage bands, a dark eye gap with big cute eyes, stubby arms and feet."""
    W = H * 0.62
    out = []
    rnd = random.Random(seed)
    # feet
    for sg in (-1, 1):
        ft = blob(cx + sg * W * 0.22, base - H * 0.02, W * 0.17, H * 0.055, seed + sg, 0.06, 10)
        out.append(body(f"{u}-ft{sg + 1}", ft, (cx - W, base - H * 0.1, cx + W, base), wrap, list(tints), seed + sg, n=8, angle=0, length=(4, 10), width=(1, 2),
                        line=line, lw=2))
    bd = smooth_closed(jitter([(cx - W * 0.5, base - H * 0.06), (cx - W * 0.54, base - H * 0.4), (cx - W * 0.5, base - H * 0.7), (cx - W * 0.36, base - H * 0.9),
                               (cx, base - H), (cx + W * 0.36, base - H * 0.9), (cx + W * 0.5, base - H * 0.7), (cx + W * 0.54, base - H * 0.4),
                               (cx + W * 0.5, base - H * 0.06), (cx, base - H * 0.03)], seed, H * 0.004))
    out.append(cast_shadow(cx, base, W * 0.6, H * 0.04, "#3A2418", 0.18, seed))
    out.append(f'<path d="{bd}" fill="{wrap}"/>')
    inner = []
    y = base - H * 1.02
    k = 0
    face_y = base - H * 0.68
    while y < base:
        hband = H * rnd.uniform(0.075, 0.095)
        tilt = rnd.uniform(-0.12, 0.12) * W
        col = rnd.choice([wrap, "#E6D6B8", "#F8F0DE", "#DCCBA8"])
        pts = [(cx - W, y - tilt), (cx, y + rnd.uniform(-2, 2)), (cx + W, y + tilt), (cx + W, y + tilt + hband), (cx, y + hband + rnd.uniform(-2, 2)), (cx - W, y - tilt + hband)]
        dd = smooth_closed(pts)
        inner.append(f'<path d="{dd}" fill="{col}"/>')
        inner.append(dabs(list(tints), seed + k, (cx - W * 0.6, y - abs(tilt) - 4, cx + W * 0.6, y + hband + abs(tilt)), 14, math.degrees(math.atan2(tilt, W)),
                          (W * 0.1, W * 0.35), (0.8, 2), (0.3, 0.6), 0.1))
        inner.append(ink(f"M {_f(cx - W)} {_f(y - tilt + hband)} Q {_f(cx)} {_f(y + hband + 2)} {_f(cx + W)} {_f(y + tilt + hband)}", gap, 2.4, seed + k, 1, 0.85))
        inner.append(f'<path d="M {_f(cx - W)} {_f(y - tilt + hband + 3)} Q {_f(cx)} {_f(y + hband + 5)} {_f(cx + W)} {_f(y + tilt + hband + 3)}" stroke="#B8A482" stroke-width="5" fill="none" opacity="0.45"/>')
        y += hband * 0.92
        k += 1
    # shading: shadow side and a soft underside
    inner.append(f'<path d="{blob(cx + W * 0.45, base - H * 0.45, W * 0.3, H * 0.6, seed + 3, 0.08)}" fill="#A8967A" opacity="0.35"/>')
    inner.append(f'<path d="{blob(cx, base + H * 0.02, W * 0.7, H * 0.12, seed + 4, 0.08)}" fill="#A8967A" opacity="0.35"/>')
    # eye gap
    eg = smooth_closed([(cx - W * 0.6, face_y - H * 0.06), (cx, face_y - H * 0.075), (cx + W * 0.6, face_y - H * 0.04), (cx + W * 0.6, face_y + H * 0.07),
                        (cx, face_y + H * 0.085), (cx - W * 0.6, face_y + H * 0.06)])
    inner.append(f'<path d="{eg}" fill="{eye_band}"/>')
    inner.append(dabs(["#3E2A48", "#1A0E20"], seed + 6, (cx - W * 0.6, face_y - H * 0.07, cx + W * 0.6, face_y + H * 0.08), 16, 0, (8, 20), (1, 2.4), (0.3, 0.6), 0.1))
    out.append(clip(f"{u}-mc", bd) + f'<g clip-path="url(#{u}-mc)">' + "".join(inner) + "</g>")
    # a bandage flap crossing over the eye gap
    fl = smooth_closed([(cx - W * 0.56, face_y + H * 0.05), (cx - W * 0.1, face_y - H * 0.0), (cx + W * 0.05, face_y + H * 0.06), (cx - W * 0.5, face_y + H * 0.12)])
    out.append(ink(bd, line, 2.6, seed, 2, 0.85))
    # eyes: one big, one a little smaller, both shining
    for sg, rr in ((-1, 0.07), (1, 0.085)):
        ex, ey = cx + sg * W * 0.2, face_y + H * 0.005
        r = H * rr * 0.62
        out.append(f'<circle cx="{_f(ex)}" cy="{_f(ey)}" r="{_f(r * 1.25)}" fill="#FFF8EA"/>'
                   f'<circle cx="{_f(ex + r * 0.12)}" cy="{_f(ey + r * 0.12)}" r="{_f(r * 0.8)}" fill="#1A0E1A"/>'
                   f'<circle cx="{_f(ex - r * 0.2)}" cy="{_f(ey - r * 0.3)}" r="{_f(r * 0.32)}" fill="#FFFFFF"/>'
                   f'<circle cx="{_f(ex + r * 0.4)}" cy="{_f(ey + r * 0.4)}" r="{_f(r * 0.14)}" fill="#FFFFFF"/>')
    for sg in (-1, 1):
        out.append(f'<path d="{blob(cx + sg * W * 0.34, face_y + H * 0.13, W * 0.08, H * 0.025, seed + sg, 0.1, 8)}" fill="#F2A0A8" opacity="0.65"/>')
    out.append(ink(f"M {_f(cx - W * 0.05)} {_f(face_y + H * 0.12)} Q {_f(cx)} {_f(face_y + H * 0.15)} {_f(cx + W * 0.05)} {_f(face_y + H * 0.12)}", line, 2, seed, 1, 0.9))
    return "".join(out), W, face_y


def bandage_arm(u, pts, w0, w1, seed, wrap="#F1E6CF", line="#3A2A2A", gap="#8A7A62"):
    d = limb_d(pts, w0, w1, seed)
    rnd = random.Random(seed)
    x0, x1 = min(p[0] for p in pts) - w0, max(p[0] for p in pts) + w0
    y0, y1 = min(p[1] for p in pts) - w0, max(p[1] for p in pts) + w0
    wraps = "".join(f'<path d="M {_f(px - w0 * 0.8 + rnd.uniform(-2, 2))} {_f(py - w0 * 0.9)} l {_f(w0 * 0.6)} {_f(w0 * 1.8)}" stroke="{gap}" stroke-width="1.4" opacity="0.6"/>'
                    for px, py in [(pts[0][0] + (pts[-1][0] - pts[0][0]) * t, pts[0][1] + (pts[-1][1] - pts[0][1]) * t) for t in (0.2, 0.45, 0.7, 0.9)])
    return (body(f"{u}-a", d, (x0, y0, x1, y1), wrap, ["#FFFFFF", "#E2D2B2", "#CDBB96"], seed, n=14, angle=0, length=(4, 10), width=(1, 2))
            + clip(f"{u}-ac", d) + f'<g clip-path="url(#{u}-ac)">{wraps}</g>' + ink(d, line, 2.2, seed, 2, 0.85))


@design("wrap-it-up")
def d_wrap_it_up():
    u = "hgb-wiu"
    out = [paper_ground(f"{u}-pp", PAPER, seed=341)]
    out.append(backdrop(f"{u}-bk", 300, 326, 238, 196, "#DDEBC4", ["#CFE2AE", "#E6F0D2", "#BFD89A", "#E0ECCA"], 342, op=0.9))
    out.append(stars(343, (80, 220, 520, 500), 12, "#9AB86A", 0, r=(1.4, 2.6), keep=lambda x, y: abs(x - 300) > 120))
    for x, y, r in ((108, 300, 10), (500, 260, 8), (480, 470, 11), (120, 470, 7)):
        out.append(twinkle(x, y, r, GOLD, 0.95, x))
    # the bandage banner: unrolls from the mummy's raised hand across the top, carrying the words
    cl = [(40, 168), (150, 150), (270, 146), (380, 140), (448, 156), (470, 206), (444, 270)]
    cline = smooth_open(cl)
    # build the strip by offsetting the centre line
    def offs(pts, o):
        res = []
        for i, (x, y) in enumerate(pts):
            a = pts[max(i - 1, 0)]
            b = pts[min(i + 1, len(pts) - 1)]
            ang = math.atan2(b[1] - a[1], b[0] - a[0])
            res.append((x - math.sin(ang) * o, y + math.cos(ang) * o))
        return res
    dense = []
    for i in range(len(cl) - 1):
        for t in range(8):
            tt = t / 8
            dense.append((cl[i][0] + (cl[i + 1][0] - cl[i][0]) * tt, cl[i][1] + (cl[i + 1][1] - cl[i][1]) * tt))
    dense.append(cl[-1])
    # smooth the dense line a little (moving average)
    sm = [dense[0]] + [((dense[i - 1][0] + dense[i][0] * 2 + dense[i + 1][0]) / 4, (dense[i - 1][1] + dense[i][1] * 2 + dense[i + 1][1]) / 4) for i in range(1, len(dense) - 1)] + [dense[-1]]
    taper = lambda i: 46 - 22 * max(0, (i - len(sm) * 0.62) / (len(sm) * 0.38))  # noqa: E731
    top_e = [offs(sm, -taper(i))[i] for i in range(len(sm))]
    bot_e = [offs(sm, taper(i))[i] for i in range(len(sm))]
    rnd = random.Random(344)
    top_e = [(x, y + rnd.uniform(-1.2, 1.2)) for x, y in top_e]
    bot_e = [(x, y + rnd.uniform(-1.2, 1.2)) for x, y in bot_e]
    # frayed start at the left
    fray = [(top_e[0][0] - 6, top_e[0][1] + 8), (top_e[0][0] + 4, top_e[0][1] + 22), (top_e[0][0] - 10, top_e[0][1] + 36),
            (top_e[0][0] + 2, top_e[0][1] + 52), (top_e[0][0] - 8, top_e[0][1] + 70)]
    strip = "M " + " L ".join(f"{_f(x)} {_f(y)}" for x, y in top_e + bot_e[::-1] + fray[::-1]) + " Z"
    out.append(f'<path d="{strip}" fill="#3A2418" opacity="0.15" transform="translate(5 8)"/>')
    out.append(body(f"{u}-st", strip, (20, 80, 540, 300), "#F1E6CF", ["#FFFFFF", "#E2D2B2", "#F8F0DC", "#CDBB96"], 345, n=170, angle=lambda x, y: -8 if x < 400 else 60,
                    length=(18, 50), width=(1.2, 3), opacity=(0.3, 0.6), curve=0.1, line="#5A4030", lw=2.4))
    out.append(shade_in(f"{u}-ss", strip, "".join(f'<path d="M {_f(x - 10)} {_f(y - 60)} l 22 120" stroke="#A8967A" stroke-width="2" opacity="0.8"/>'
                                                  for x, y in sm[::5]), "#000", 0.5))
    for i, (x0, y0) in enumerate(fray):
        out.append(ink(f"M {_f(x0)} {_f(y0)} l {_f(-10 - i % 2 * 6)} {_f(rnd.uniform(-3, 3))}", "#CDBB96", 1.8, 346 + i, 1, 0.8))
    # lettering along the strip
    path_d = smooth_open([(x, y + 19) for x, y in sm[:int(len(sm) * 0.66)]])
    out.append(defs(f'<path id="{u}-tp" d="{path_d}"/>'))
    for dx, dy, col in ((2.5, 3, "#E2B48A"), (0, 0, "#4E2A6E")):
        out.append(f'<text {ANTON} font-size="58" letter-spacing="7" fill="{col}" text-anchor="middle" transform="translate({dx} {dy})">'
                   f'<textPath href="#{u}-tp" startOffset="52%">WRAP IT UP</textPath></text>')
    # mummy
    m, W, fy = mummy(f"{u}-m", 300, 492, 220, 347)
    arm_l = bandage_arm(f"{u}-al", [(300 - W * 0.42, 492 - 220 * 0.42), (300 - W * 0.75, 492 - 220 * 0.36), (300 - W * 0.95, 492 - 220 * 0.42)], 30, 24, 348)
    arm_r = bandage_arm(f"{u}-ar", [(300 + W * 0.42, 492 - 220 * 0.46), (396, 344), (434, 292)], 30, 24, 349)
    out.append(arm_l + arm_r + m)
    # the hand holding the strip end
    hand = blob(440, 282, 17, 15, 350, 0.08, 10)
    out.append(body(f"{u}-hd", hand, (420, 264, 460, 300), "#F1E6CF", ["#FFFFFF", "#E2D2B2"], 350, n=8, angle=0, length=(4, 9), width=(1, 2), line="#3A2A2A", lw=2.2))
    out.append(ink("M 428 276 q 8 -4 16 0 M 430 286 q 8 -4 16 0", "#8A7A62", 1.4, 350, 1, 0.7))
    # candy at the mummy's feet
    out.append(pail(f"{u}-pl", 168, 452, 62, 50, 359, handle_to=(170, 402)))
    hand = blob(170, 402, 15, 13, 360, 0.08, 10)
    out.append(body(f"{u}-hl", hand, (154, 388, 186, 416), "#F1E6CF", ["#FFFFFF", "#E2D2B2"], 360, n=8, angle=0, length=(4, 9), width=(1, 2), line="#3A2A2A", lw=2.2))
    out.append(candy_corn(f"{u}-c1", 112, 498, 28, -20, 351))
    out.append(candy_corn(f"{u}-c2", 228, 500, 22, 16, 352))
    out.append(wrapped_candy(f"{u}-w1", 438, 482, 20, 16, 353, "#8E6AC0", "#C9B6EA"))
    out.append(wrapped_candy(f"{u}-w2", 470, 452, 16, -30, 354, PUMPKIN, "#FFD08A"))
    out.append(spider(f"{u}-sp", 120, 330, 14, 355, thread="#5A4030", thread_top=230))
    out.append(label(300, 540, "MUMMY'S LITTLE MONSTER", JOS, 20, "#4E2A6E", ls=4, rule=PUMPKIN, line_w=28, seed=356, max_w=360))
    out.append(grain_over(f"{u}-gr", 357, dark="#5A3A2A", op=0.8))
    return "".join(out)


# ---------------------------------------------------------------- sweet & spooky
def caramel_apple(u, cx, cy, r, seed, rot=0, coat=("#C9822E", "#E8A84E", "#9A5A1E", "#F2C27A"), apple=("#B8322A", "#D8503A", "#7A1E1A"),
                  topping="nuts", ribbon=PUMPKIN, ribbon_d=PUMPKIN_D, line=INK):
    """Caramel (or candy) apple on a stick: glossy coating with a drippy hem, apple peeking below, topping, gingham-ish bow."""
    rnd = random.Random(seed)
    out = [f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">']
    # stick
    st = limb_d([(cx, cy - r * 0.7), (cx + 1, cy - r * 1.35), (cx + 2, cy - r * 1.9)], r * 0.16, r * 0.13, seed)
    out.append(plank(f"{u}-st", st, (cx - r * 0.1, cy - r * 1.95, cx + r * 0.1, cy - r * 0.7), "#D8B98A", ["#E8D0A8", "#B8955E"], seed, angle=-90, knots=0, line=line, lw=1.8))
    # apple body
    ad = smooth_closed(jitter([(cx - r * 0.95, cy - r * 0.2), (cx - r * 0.7, cy - r * 0.82), (cx - r * 0.15, cy - r * 0.86), (cx, cy - r * 0.72),
                               (cx + r * 0.15, cy - r * 0.86), (cx + r * 0.7, cy - r * 0.82), (cx + r * 0.95, cy - r * 0.2), (cx + r * 0.75, cy + r * 0.62),
                               (cx + r * 0.25, cy + r * 0.85), (cx, cy + r * 0.78), (cx - r * 0.25, cy + r * 0.85), (cx - r * 0.75, cy + r * 0.62)], seed, r * 0.01))
    out.append(body(f"{u}-ap", ad, (cx - r, cy - r, cx + r, cy + r), apple[0], [apple[1], apple[2], "#E8704A"], seed, n=int(r * 1.2), angle=-90,
                    length=(r * 0.2, r * 0.6), width=(1, r * 0.05), line=None))
    # coating with a drippy lower edge
    rim = [(cx - r * 0.98, cy - r * 0.2), (cx - r * 0.72, cy - r * 0.86), (cx, cy - r * 0.78), (cx + r * 0.72, cy - r * 0.86), (cx + r * 0.98, cy - r * 0.2)]
    hem = []
    k = 9
    for i in range(k + 1):
        t = i / k
        x = cx + r * 0.96 - 1.92 * r * t
        base_y = cy + r * (0.2 + 0.25 * math.sin(math.pi * t))
        drip = r * rnd.uniform(0.12, 0.42) if i % 2 == 1 else rnd.uniform(-0.03, 0.04) * r
        hem.append((x, base_y + drip))
    cd = smooth_closed(rim + hem)
    cdj = smooth_closed(jitter(rim + hem, seed + 1, r * 0.01))
    out.append(defs(rg(f"{u}-cg", [(0, coat[3]), (0.55, coat[0]), (1, coat[2])], cx=0.38, cy=0.3, r=0.75)))
    out.append(f'<path d="{cdj}" fill="url(#{u}-cg)"/>')
    out.append(brush(f"{u}-cb", cdj, (cx - r, cy - r, cx + r, cy + r * 0.8), [coat[1], coat[2], coat[3], coat[0]], seed + 2, int(r * 1.5),
                     angle=around(cx, cy - r * 0.2), length=(r * 0.15, r * 0.5), width=(1, r * 0.05), opacity=(0.25, 0.55), curve=0.15))
    if topping == "nuts":
        tp = "".join(f'<path d="{blob(cx + rnd.uniform(-0.85, 0.85) * r, cy + r * rnd.uniform(0.0, 0.42), r * rnd.uniform(0.04, 0.08), r * rnd.uniform(0.03, 0.06), rnd.randrange(999), 0.2, 6)}" '
                     f'fill="{rnd.choice(["#E8D0A0", "#C99A5A", "#F2E2BE", "#A8743A"])}"/>' for _ in range(int(r * 1.1)))
    else:
        tp = "".join(f'<path d="M {_f(x := cx + rnd.uniform(-0.85, 0.85) * r)} {_f(y := cy + r * rnd.uniform(-0.7, 0.45))} l {_f(rnd.uniform(-1, 1) * r * 0.08)} {_f(rnd.uniform(-1, 1) * r * 0.08)}" '
                     f'stroke="{rnd.choice([PUMPKIN, SLIME, "#FFE29A", "#FFFFFF", "#F28AB0"])}" stroke-width="{_f(r * 0.04)}" stroke-linecap="round"/>' for _ in range(int(r * 1.2)))
    out.append(clip(f"{u}-tc", cdj) + f'<g clip-path="url(#{u}-tc)">{tp}</g>')
    out.append(f'<path d="M {_f(cx - r * 0.62)} {_f(cy - r * 0.45)} Q {_f(cx - r * 0.7)} {_f(cy - r * 0.1)} {_f(cx - r * 0.55)} {_f(cy + r * 0.15)}" stroke="#FFF6E0" '
               f'stroke-width="{_f(r * 0.09)}" fill="none" stroke-linecap="round" opacity="0.85"/>'
               f'<path d="{blob(cx - r * 0.3, cy - r * 0.6, r * 0.08, r * 0.05, seed, 0.1, 8)}" fill="#FFFFFF" opacity="0.85"/>')
    out.append(ink(ad, line, 2.2, seed, 1, 0.7) + ink(cd, "#6A3A10", 2.2, seed + 3, 2, 0.8))
    # bow on the stick
    out.append(bow(f"{u}-bw", cx, cy - r * 0.98, r * 0.42, seed + 4, col=ribbon, dark=ribbon_d, light="#FFD08A", line=line, dots="#FFF2D8"))
    out.append("</g>")
    return "".join(out)


def drip_word(u, x, y, s, font, size, fill, tints, seed, max_w, drips, shadow=None, hi=None):
    """Brush lettering with caramel drips hanging from the baseline."""
    size2 = fit_size(s, font, size, max_w)
    w = measure(s, font, size2)
    x0 = x - w / 2
    rnd = random.Random(seed)
    dr = []
    for t, L in drips:
        dx = x0 + w * t
        ww = size2 * rnd.uniform(0.05, 0.075)
        dr.append(smooth_closed([(dx - ww, y - size2 * 0.12), (dx + ww, y - size2 * 0.12), (dx + ww * 0.9, y + L * 0.6), (dx + ww * 1.1, y + L), (dx, y + L + ww * 1.2),
                                 (dx - ww * 1.1, y + L), (dx - ww * 0.9, y + L * 0.6)]))
    out = []
    if shadow:
        out.append(f'<g fill="{shadow}" transform="translate({_f(size2 * 0.03)} {_f(size2 * 0.04)})">' + "".join(f'<path d="{d}"/>' for d in dr) + "</g>")
    out.append(f'<g fill="{fill}">' + "".join(f'<path d="{d}"/>' for d in dr) + "</g>")
    out.append(bword(u, x, y, s, font, size, fill, tints, seed, max_w=max_w, shadow=shadow, hi=hi, angle=-60))
    for i, d in enumerate(dr):
        out.append(brush(f"{u}-d{i}", d, (x0, y - 10, x0 + w, y + 80), tints, seed + i, 6, angle=90, length=(6, 16), width=(1, 2.4), opacity=(0.3, 0.6)))
    for t, L in drips:
        dx = x0 + w * t
        out.append(f'<path d="M {_f(dx - size2 * 0.02)} {_f(y + L * 0.2)} L {_f(dx - size2 * 0.02)} {_f(y + L * 0.8)}" stroke="#FFF2D0" stroke-width="{_f(size2 * 0.018)}" stroke-linecap="round" opacity="0.8"/>')
    return "".join(out)


@design("sweet-and-spooky")
def d_sweet_and_spooky():
    u = "hgb-sas"
    out = [paper_ground(f"{u}-pp", PAPER, seed=401)]
    out.append(backdrop(f"{u}-bk", 300, 384, 236, 168, "#F6D9B8", ["#F2CCA0", "#FAE6CE", "#EEC08E", "#F8DFC2"], 402, op=0.95))
    # checked tablecloth corner peeking in at the bottom
    out.append(stars(403, (70, 260, 530, 520), 12, "#E8A86A", 0, r=(1.4, 2.6), keep=lambda x, y: abs(x - 300) > 150))
    for x, y, r in ((96, 300, 10), (512, 330, 9), (500, 520, 8)):
        out.append(twinkle(x, y, r, PURPLE, 0.85, x))
    out.append(cast_shadow(300, 506, 196, 16, "#3A2418", 0.18, 404))
    # candy apples
    out.append(caramel_apple(f"{u}-a2", 392, 418, 70, 405, rot=10, coat=("#6E3E9A", "#8E5EBA", "#3E1E5E", "#B08AE0"), apple=("#7A2A3A", "#9A3A4A", "#4A1420"),
                             topping="sprinkles", ribbon=SLIME, ribbon_d=SLIME_D))
    out.append(caramel_apple(f"{u}-a1", 248, 412, 88, 406, rot=-6))
    # caramel puddles at their feet
    for x, y, rx in ((248, 492, 74), (398, 488, 56)):
        out.append(f'<path d="{blob(x, y, rx, 9, x, 0.1, 14)}" fill="#C9822E" opacity="0.9"/>' + ink(blob(x, y, rx, 9, x, 0.1, 14), "#6A3A10", 1.6, x, 1, 0.6))
    # candy corn pile and wrapped sweets
    for i, (x, y, sz, rt) in enumerate(((132, 486, 34, -30), (164, 498, 30, 20), (112, 506, 26, 60), (474, 498, 30, 12), (500, 478, 26, -40), (156, 466, 26, 4))):
        out.append(candy_corn(f"{u}-cc{i}", x, y, sz, rt, 407 + i))
    out.append(wrapped_candy(f"{u}-w1", 330, 512, 20, -8, 414, PUMPKIN, "#FFD08A"))
    out.append(wrapped_candy(f"{u}-w2", 470, 444, 16, 30, 415, "#9BD14B", "#E4F5BE"))
    out.append(bat(f"{u}-bt", 470, 290, 26, 416, rot=12, flap=0.2))
    # lettering
    out.append(drip_word(f"{u}-t", 300, 178, "sweet", SERIF_IT, 150, "#C9822E", ["#E8A84E", "#9A5A1E", "#F2C27A", "#B8701E"], 417, 400,
                         [(0.08, 30), (0.36, 18), (0.61, 34), (0.86, 24)], shadow="#5A2E0E", hi="#FFE8B8"))
    out.append(label(300, 266, "& SPOOKY", JOS, 40, "#4E2A6E", ls=12, rule=PUMPKIN, line_w=48, seed=418))
    out.append(grain_over(f"{u}-gr", 419, dark="#5A3A2A", op=0.8))
    return "".join(out)


# ---------------------------------------------------------------- just chillin'
def bone_d(x0, y0, x1, y1, w, seed):
    """A cartoon bone between two points: a shaft with two knobbly ends."""
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang), math.cos(ang)
    pts = []
    L = math.hypot(x1 - x0, y1 - y0)
    for (px, py), sg in (((x0, y0), -1), ((x1, y1), 1)):
        pass
    sh = limb_d([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2), (x1, y1)], w, w * 0.9, seed)
    knobs = []
    for (px, py) in ((x0, y0), (x1, y1)):
        for sg in (-1, 1):
            knobs.append(blob(px + nx * sg * w * 0.45, py + ny * sg * w * 0.45, w * 0.62, w * 0.62, seed + sg, 0.06, 10))
    return [sh] + knobs


def paint_bones(u, ds, box, seed, base=BONE, tints=("#FFFFFF", "#E2D6BE", "#F8F0DE"), line="#2A1830", lw=2.2, shade="#B8A888"):
    out = [f'<g fill="{base}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>"]
    out.append(brush(f"{u}-pb", ds, box, list(tints) + [shade], seed, 40, angle=-20, length=(5, 14), width=(1, 2.2), opacity=(0.3, 0.6)))
    out.append(f'<g fill="none" stroke="{line}" stroke-width="{lw}" opacity="0.8" stroke-linejoin="round">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    out.append(f'<g fill="{base}">' + "".join(f'<path d="{d}"/>' for d in ds) + "</g>")
    out.append(brush(f"{u}-pb2", ds, box, list(tints) + [shade], seed + 1, 30, angle=-20, length=(5, 14), width=(1, 2.2), opacity=(0.3, 0.6)))
    return "".join(out)


def rocking_chair(u, cx, seat_y, w, seed, wood="#7A4A2E", tints=("#9A6440", "#5A321E", "#B07A50"), line="#1A0E10"):
    """Front view rocking chair: tall spindle back, arms, seat, legs on curved rockers. Returns (back, front) layers."""
    back = []
    top = seat_y - w * 1.15
    bd = smooth_closed([(cx - w * 0.46, seat_y), (cx - w * 0.48, top + w * 0.1), (cx - w * 0.3, top - w * 0.02), (cx, top - w * 0.06),
                        (cx + w * 0.3, top - w * 0.02), (cx + w * 0.48, top + w * 0.1), (cx + w * 0.46, seat_y)])
    # back panel: two posts, a curved crest rail and spindles (holes between)
    posts = [limb_d([(cx + sg * w * 0.46, seat_y + w * 0.05), (cx + sg * w * 0.47, top + w * 0.3), (cx + sg * w * 0.45, top - w * 0.02)], w * 0.08, w * 0.07, seed + sg) for sg in (-1, 1)]
    crest = limb_d([(cx - w * 0.48, top + w * 0.06), (cx, top - w * 0.04), (cx + w * 0.48, top + w * 0.06)], w * 0.13, w * 0.13, seed + 3)
    sp = [limb_d([(cx + t * w, seat_y), (cx + t * w * 1.02, top + w * 0.08)], w * 0.045, w * 0.04, seed + 10 + i) for i, t in enumerate((-0.27, -0.09, 0.09, 0.27))]
    back.append(plank(f"{u}-bk", " ".join(sp), (cx - w / 2, top, cx + w / 2, seat_y), wood, list(tints), seed, angle=-90, knots=0, line=line, lw=1.8, n=40))
    for i, d in enumerate(posts + [crest]):
        back.append(plank(f"{u}-p{i}", d, (cx - w / 2, top - w * 0.1, cx + w / 2, seat_y), wood, list(tints), seed + i, angle=-90 if i < 2 else 0, knots=0, line=line, lw=2))
    front = []
    # legs & rockers
    for sg in (-1, 1):
        lg_ = limb_d([(cx + sg * w * 0.4, seat_y), (cx + sg * w * 0.42, seat_y + w * 0.42)], w * 0.07, w * 0.06, seed + 20 + sg)
        front.append(plank(f"{u}-lg{sg + 1}", lg_, (cx - w / 2, seat_y, cx + w / 2, seat_y + w * 0.5), wood, list(tints), seed + 20, angle=-90, knots=0, line=line, lw=1.8))
    rk = limb_d([(cx - w * 0.75, seat_y + w * 0.36), (cx - w * 0.35, seat_y + w * 0.46), (cx + w * 0.35, seat_y + w * 0.46), (cx + w * 0.75, seat_y + w * 0.36)], w * 0.07, w * 0.07, seed + 30)
    front.append(plank(f"{u}-rk", rk, (cx - w * 0.8, seat_y + w * 0.3, cx + w * 0.8, seat_y + w * 0.55), "#6A3E24", list(tints), seed + 30, knots=0, line=line, lw=2))
    # arm rests
    for sg in (-1, 1):
        ar = limb_d([(cx + sg * w * 0.42, seat_y - w * 0.38), (cx + sg * w * 0.56, seat_y - w * 0.36), (cx + sg * w * 0.62, seat_y - w * 0.3)], w * 0.09, w * 0.08, seed + 40 + sg)
        pst = limb_d([(cx + sg * w * 0.56, seat_y - w * 0.32), (cx + sg * w * 0.52, seat_y)], w * 0.06, w * 0.06, seed + 42 + sg)
        front.append(plank(f"{u}-ap{sg + 1}", pst, (cx - w, seat_y - w * 0.4, cx + w, seat_y), wood, list(tints), seed + 42, angle=-90, knots=0, line=line, lw=1.8))
        front.append(plank(f"{u}-ar{sg + 1}", ar, (cx - w, seat_y - w * 0.45, cx + w, seat_y - w * 0.25), wood, list(tints), seed + 40, knots=0, line=line, lw=1.8))
    return "".join(back), "".join(front)


def skeleton_cozy(u, cx, seat_y, s, seed, blanket=(PUMPKIN, PUMPKIN_D, "#4E2A6E", "#FFE2B0"), line="#2A1830"):
    """Friendly seated skeleton: skull with a grin, ribs, arm bones around a steaming mug, plaid blanket on the lap."""
    out = []
    # spine & ribs
    sp_top, sp_bot = seat_y - s * 1.0, seat_y - s * 0.2
    ribs = []
    for i in range(4):
        y = sp_top + s * 0.14 + i * s * 0.13
        ww = s * (0.34 - i * 0.03)
        for sg in (-1, 1):
            ribs.append(limb_d([(cx, y), (cx + sg * ww * 0.7, y - s * 0.03), (cx + sg * ww, y + s * 0.06), (cx + sg * ww * 0.85, y + s * 0.11)], s * 0.055, s * 0.04, seed + i * 2 + sg))
    spine = [blob(cx, sp_top + i * s * 0.1, s * 0.05, s * 0.04, seed + 30 + i, 0.08, 8) for i in range(9)]
    clav = [limb_d([(cx, sp_top + s * 0.06), (cx + sg * s * 0.2, sp_top + s * 0.02), (cx + sg * s * 0.36, sp_top + s * 0.06)], s * 0.05, s * 0.05, seed + 40 + sg) for sg in (-1, 1)]
    pel = blob(cx, sp_bot + s * 0.06, s * 0.3, s * 0.1, seed + 45, 0.08, 14)
    out.append(paint_bones(f"{u}-tor", spine + ribs + clav + [pel], (cx - s * 0.5, sp_top - 10, cx + s * 0.5, sp_bot + s * 0.2), seed, line=line))
    # blanket over the lap, plaid
    bl = smooth_closed(jitter([(cx - s * 0.5, seat_y - s * 0.24), (cx - s * 0.22, seat_y - s * 0.33), (cx + s * 0.05, seat_y - s * 0.28), (cx + s * 0.3, seat_y - s * 0.33),
                               (cx + s * 0.55, seat_y - s * 0.2), (cx + s * 0.7, seat_y + s * 0.18), (cx + s * 0.82, seat_y + s * 0.74), (cx + s * 0.5, seat_y + s * 0.62),
                               (cx + s * 0.2, seat_y + s * 0.68), (cx - s * 0.12, seat_y + s * 0.6), (cx - s * 0.42, seat_y + s * 0.67), (cx - s * 0.66, seat_y + s * 0.6),
                               (cx - s * 0.64, seat_y + s * 0.15)], seed + 50, 1))
    plaid = []
    for k in range(-6, 7):
        plaid.append(f'<path d="M {_f(cx + k * s * 0.12)} {_f(seat_y - s * 0.4)} L {_f(cx + k * s * 0.12 + s * 0.05)} {_f(seat_y + s * 0.8)}" stroke="{blanket[2]}" stroke-width="{_f(s * 0.035)}" opacity="0.75"/>')
        plaid.append(f'<path d="M {_f(cx - s)} {_f(seat_y - s * 0.2 + k * s * 0.12)} Q {_f(cx)} {_f(seat_y - s * 0.16 + k * s * 0.12)} {_f(cx + s)} {_f(seat_y - s * 0.22 + k * s * 0.12)}" stroke="{blanket[2]}" stroke-width="{_f(s * 0.035)}" opacity="0.6"/>')
        plaid.append(f'<path d="M {_f(cx + k * s * 0.12 + s * 0.06)} {_f(seat_y - s * 0.4)} L {_f(cx + k * s * 0.12 + s * 0.11)} {_f(seat_y + s * 0.8)}" stroke="{blanket[3]}" stroke-width="{_f(s * 0.01)}" opacity="0.7"/>')
    folds = "".join(f'<path d="M {_f(cx + t * s)} {_f(seat_y - s * 0.12)} Q {_f(cx + t * s * 1.2 + s * 0.04)} {_f(seat_y + s * 0.25)} {_f(cx + t * s * 1.4 - s * 0.02)} {_f(seat_y + s * 0.66)}" stroke="#3A1408" stroke-width="{_f(s * 0.08)}" fill="none" opacity="0.3"/>'
                    for t in (-0.3, 0.02, 0.32))
    folds += f'<path d="M {_f(cx - s * 0.7)} {_f(seat_y - s * 0.05)} Q {_f(cx)} {_f(seat_y + s * 0.02)} {_f(cx + s * 0.7)} {_f(seat_y - s * 0.02)}" stroke="#3A1408" stroke-width="{_f(s * 0.1)}" fill="none" opacity="0.22"/>'
    folds += f'<path d="M {_f(cx - s * 0.45)} {_f(seat_y - s * 0.2)} Q {_f(cx)} {_f(seat_y - s * 0.25)} {_f(cx + s * 0.45)} {_f(seat_y - s * 0.18)}" stroke="#FFD08A" stroke-width="{_f(s * 0.03)}" fill="none" opacity="0.5"/>'
    out.append(body(f"{u}-bl", bl, (cx - s * 0.7, seat_y - s * 0.3, cx + s * 0.7, seat_y + s * 0.66), blanket[0], [blanket[1], "#F8A85A", blanket[0]], seed + 51,
                    n=60, angle=-80, length=(s * 0.08, s * 0.25), width=(1, 3), line=None))
    out.append(clip(f"{u}-blc", bl) + f'<g clip-path="url(#{u}-blc)">' + "".join(plaid) + folds + "</g>")
    out.append(ink(bl, "#5A2410", 2.4, seed + 51, 2, 0.85))
    rnd = random.Random(seed)
    hem = [(cx + s * 0.82, seat_y + s * 0.74), (cx + s * 0.5, seat_y + s * 0.62), (cx + s * 0.2, seat_y + s * 0.68), (cx - s * 0.12, seat_y + s * 0.6),
           (cx - s * 0.42, seat_y + s * 0.67), (cx - s * 0.66, seat_y + s * 0.6)]
    fr = ""
    for i in range(len(hem) - 1):
        for t in (0.15, 0.4, 0.65, 0.9):
            hx, hy = hem[i][0] + (hem[i + 1][0] - hem[i][0]) * t, hem[i][1] + (hem[i + 1][1] - hem[i][1]) * t
            fr += f'<path d="M {_f(hx)} {_f(hy - 1)} l {_f(rnd.uniform(-2, 2))} {_f(s * 0.07)}"/>'
    out.append(f'<g stroke="{blanket[0]}" stroke-width="2.4" stroke-linecap="round">{fr}</g>')
    # feet peeking out
    for sg in (-1, 1):
        ft = bone_d(cx + sg * s * 0.18, seat_y + s * 0.7, cx + sg * s * 0.28, seat_y + s * 0.74, s * 0.06, seed + 60 + sg)
        out.append(paint_bones(f"{u}-ft{sg + 1}", ft, (cx - s, seat_y + s * 0.6, cx + s, seat_y + s * 0.85), seed + 60, line=line, lw=1.8))
    # arms reaching to the mug in the middle
    mx, my = cx + s * 0.04, seat_y - s * 0.42
    arm = []
    for sg in (-1, 1):
        sh = (cx + sg * s * 0.36, sp_top + s * 0.08)
        el = (cx + sg * s * 0.46, sp_top + s * 0.42)
        arm += bone_d(sh[0], sh[1], el[0], el[1], s * 0.065, seed + 70 + sg)
        arm += bone_d(el[0], el[1], mx + sg * s * 0.16, my + s * 0.02, s * 0.055, seed + 72 + sg)
    out.append(paint_bones(f"{u}-arm", arm, (cx - s * 0.6, sp_top, cx + s * 0.6, my + s * 0.2), seed + 70, line=line))
    # mug
    mw, mh = s * 0.3, s * 0.26
    mug = smooth_closed([(mx - mw / 2, my - mh / 2), (mx + mw / 2, my - mh / 2), (mx + mw * 0.46, my + mh / 2), (mx, my + mh * 0.54), (mx - mw * 0.46, my + mh / 2)])
    out.append(ink(f"M {_f(mx + mw * 0.45)} {_f(my - mh * 0.25)} q {_f(mw * 0.35)} {_f(mh * 0.05)} {_f(mw * 0.02)} {_f(mh * 0.5)}", "#8A2E3A", s * 0.05, seed, 1, 1))
    out.append(body(f"{u}-mg", mug, (mx - mw / 2, my - mh / 2, mx + mw / 2, my + mh / 2), "#B8394A", ["#D8586A", "#8A2E3A", "#E87A8A"], seed + 80, n=18, angle=-90,
                    length=(4, 12), width=(1, 2.4), line=line, lw=2))
    out.append(f'<path d="{blob(mx, my - mh / 2, mw * 0.46, mh * 0.12, seed, 0.05, 10)}" fill="#5A2E1A"/>'
               + "".join(f'<path d="{blob(mx + dx * mw, my - mh / 2 - mh * 0.04, mw * 0.08, mw * 0.07, seed + i, 0.1, 8)}" fill="#FFF6EA"/>' for i, dx in enumerate((-0.15, 0.08, 0.2))))
    out.append(f'<path d="M {_f(mx - mw * 0.3)} {_f(my - mh * 0.2)} L {_f(mx - mw * 0.3)} {_f(my + mh * 0.3)}" stroke="#FFFFFF" stroke-width="2.4" opacity="0.55" stroke-linecap="round"/>')
    # finger bones wrapping the mug
    for sg in (-1, 1):
        for k in range(3):
            fx, fy = mx + sg * mw * 0.42, my - mh * 0.15 + k * mh * 0.22
            fd = blob(fx, fy, s * 0.045, s * 0.028, seed + k + sg * 5, 0.1, 8)
            out.append(f'<path d="{fd}" fill="{BONE}"/>' + ink(fd, line, 1.4, seed, 1, 0.8))
    # steam
    for k, dx in enumerate((-0.08, 0.06)):
        x0 = mx + dx * s
        out.append(ink(f"M {_f(x0)} {_f(my - mh * 0.7)} q {_f(-s * 0.05)} {_f(-s * 0.08)} 0 {_f(-s * 0.16)} q {_f(s * 0.05)} {_f(-s * 0.08)} 0 {_f(-s * 0.16)}", "#F3EAD6", 3, seed + k, 1, 0.55))
    # skull
    hy = sp_top - s * 0.24
    sk = smooth_closed(jitter([(cx - s * 0.28, hy + s * 0.02), (cx - s * 0.26, hy - s * 0.2), (cx - s * 0.1, hy - s * 0.32), (cx + s * 0.1, hy - s * 0.32),
                               (cx + s * 0.26, hy - s * 0.2), (cx + s * 0.28, hy + s * 0.02), (cx + s * 0.2, hy + s * 0.14), (cx + s * 0.14, hy + s * 0.26),
                               (cx - s * 0.14, hy + s * 0.26), (cx - s * 0.2, hy + s * 0.14)], seed + 90, s * 0.004))
    out.append(body(f"{u}-sk", sk, (cx - s * 0.3, hy - s * 0.34, cx + s * 0.3, hy + s * 0.28), BONE, ["#FFFFFF", "#E2D6BE", "#F8F0DE"], seed + 90, n=40,
                    angle=around(cx, hy, 0), length=(4, 12), width=(1, 2.4), line=line, lw=2.4))
    out.append(shade_in(f"{u}-sks", sk, f'<path d="{blob(cx + s * 0.22, hy + s * 0.05, s * 0.16, s * 0.3, seed, 0.1)}" fill="#B8A888"/>', "#000", 0.45))
    out.append(f'<path d="M {_f(cx - s * 0.18)} {_f(hy - s * 0.22)} Q {_f(cx - s * 0.1)} {_f(hy - s * 0.3)} {_f(cx + s * 0.02)} {_f(hy - s * 0.29)}" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.8"/>')
    for sg in (-1, 1):
        ex, ey = cx + sg * s * 0.11, hy - s * 0.02
        ed = blob(ex, ey, s * 0.085, s * 0.095, seed + sg, 0.06, 12)
        out.append(f'<path d="{ed}" fill="#2A1830"/>' + f'<circle cx="{_f(ex - s * 0.02)}" cy="{_f(ey - s * 0.03)}" r="{_f(s * 0.028)}" fill="#FFFFFF"/>'
                   f'<circle cx="{_f(ex + s * 0.03)}" cy="{_f(ey + s * 0.03)}" r="{_f(s * 0.012)}" fill="#FFFFFF" opacity="0.8"/>')
        out.append(f'<path d="{blob(cx + sg * s * 0.2, hy + s * 0.1, s * 0.05, s * 0.03, seed + sg, 0.1, 8)}" fill="#F2A0A8" opacity="0.55"/>')
    out.append(f'<path d="M {_f(cx)} {_f(hy + s * 0.07)} l {_f(-s * 0.03)} {_f(s * 0.05)} l {_f(s * 0.06)} 0 Z" fill="#2A1830"/>')
    out.append(ink(f"M {_f(cx - s * 0.13)} {_f(hy + s * 0.16)} Q {_f(cx)} {_f(hy + s * 0.24)} {_f(cx + s * 0.13)} {_f(hy + s * 0.16)}", line, 2.2, seed, 1, 0.9))
    out.append("".join(ink(f"M {_f(cx + t * s)} {_f(hy + s * 0.17 + abs(t) * -0.1 * s + 0.03 * s)} l 0 {_f(s * 0.045)}", line, 1.4, seed, 1, 0.7) for t in (-0.07, 0, 0.07)))
    return "".join(out)


@design("just-chillin")
def d_just_chillin():
    u = "hgb-jch"
    out = [night_sky(u, 431, [(0, "#100C24"), (0.6, "#221C46"), (1, "#3A2A5A")], ["#2A2250", "#36306A", "#1A1636", "#3E3470"], n=260)]
    out.append(stars(432, (20, 20, 580, 300), 30, BONE, 5, keep=lambda x, y: math.hypot(x - 460, y - 110) > 70))
    out.append(swirl(460, 110, 46, 120, ["#5B4888", "#7A66A8", "#C9A86A"], 433, 30, (2, 6), (30, 80), (0.12, 0.34)))
    out.append(pmoon(f"{u}-mn", 460, 110, 42, 434, halo_r=2.6, halo_op=0.4))
    # porch: a beam overhead, posts, railing, and boards
    out.append(plank(f"{u}-bm", rect_d(-10, -10, 610, 40), (-10, -10, 610, 40), "#3A2A3E", ["#4A3A50", "#2A1E2E", "#5A4A60"], 435, line="#120A16", lw=2.4, knots=1))
    for i, x in enumerate((34, 566)):
        out.append(plank(f"{u}-po{i}", rect_d(x - 18, 30, x + 18, 470), (x - 18, 30, x + 18, 470), "#3A2A3E", ["#4A3A50", "#2A1E2E", "#5A4A60"], 436 + i,
                         angle=-90, line="#120A16", lw=2.4, knots=1))
    rail_top = 300
    for x in range(60, 560, 34):
        out.append(f'<path d="{limb_d([(x, rail_top), (x, 420)], 12, 12, x)}" fill="#2E2236"/>' + ink(limb_d([(x, rail_top), (x, 420)], 12, 12, x), "#120A16", 1.6, x, 1, 0.8)
                   + f'<path d="M {x - 3} {rail_top + 6} L {x - 3} 414" stroke="#5A4A70" stroke-width="2" opacity="0.6"/>')
    out.append(plank(f"{u}-rl", rect_d(40, rail_top - 12, 560, rail_top + 4), (40, rail_top - 12, 560, rail_top + 4), "#3E2E46", ["#52405A", "#2A1E30"], 438, line="#120A16", lw=2))
    flo = smooth_closed([(-10, 416), (610, 416), (610, 610), (-10, 610)])
    out.append(plank(f"{u}-fl", flo, (-10, 416, 610, 610), "#4A3440", ["#5A4250", "#2E2028", "#6A5060"], 439, line=None, knots=2))
    for k in range(6):
        y = 430 + k * 30
        out.append(f'<path d="M -10 {y} L 610 {y + 2}" stroke="#1A1018" stroke-width="2" opacity="0.6"/>')
    # warm lantern on the post
    out.append(glow(f"{u}-wl", 300, 330, 320, "#FFB547", 0.28, 0.35))
    out.append(porch_lantern(f"{u}-lt", 92, 132, 1.6, 440))
    # chair, skeleton, blanket
    out.append(cast_shadow(300, 466, 170, 14, "#05030A", 0.55, 441))
    back, front = rocking_chair(f"{u}-ch", 300, 364, 214, 442)
    out.append(back)
    out.append(skeleton_cozy(f"{u}-sk", 300, 360, 160, 443))
    out.append(front)
    out.append(jack(f"{u}-jk", 476, 440, 66, 54, 444, face="cute", glow_r=96))
    out.append(painted_pumpkin(f"{u}-p2", 524, 456, 34, 26, 445, "#E8D9BC", "#B8A07A", "#FFF6E2"))
    out.append(leaf_fall(446, (380, 440, 420, 460), 1))
    # lettering
    out.append(defs(lg(f"{u}-fg", [(0, NIGHT, 0), (0.45, NIGHT, 0.7), (1, "#0A0816", 0.92)])) + f'<rect y="440" width="600" height="160" fill="url(#{u}-fg)"/>')
    out.append(script(150, 470, "just", 52, GOLD, 200, shadow="#05030A", sd=(2, 3), rot=-10))
    out.append(bword(f"{u}-t", 316, 538, "chillin'", DMS, 104, "#DDEFF2", ["#FFFFFF", "#A8D8E0", "#EAF6F8", "#8EC4D2"], 447, max_w=380,
                     shadow="#0A0614", angle=-30, hi="#FFFFFF"))
    out.append(grain_over(f"{u}-gr", 448))
    return "".join(out)


# ---------------------------------------------------------------- carve out some fun
def seed_d(x, y, s, rot, seed):
    return blob(x, y, s * 0.5, s * 0.3, seed, 0.06, 10, rot=rot)


def seeds(seed, box, n, s=(7, 10), keep=None, col="#F6EAC8", line="#B8955E"):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    k = 0
    while k < n:
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if keep and not keep(x, y):
            continue
        k += 1
        d = seed_d(x, y, rnd.uniform(*s), rnd.uniform(0, 180), rnd.randrange(999))
        out.append(f'<path d="{d}" fill="{col}"/>' + f'<path d="{d}" fill="none" stroke="{line}" stroke-width="1.1" opacity="0.8"/>')
    return "".join(out)


def carving_pumpkin(u, cx, cy, w, h, seed):
    """A pumpkin halfway through carving: lid off, a glowing cut eye, the rest of the face sketched in marker."""
    out = [painted_pumpkin(f"{u}-pp", cx, cy, w, h, seed, stem="none", leaf="none")]
    # cover the stem area with the open top
    ty = cy - h * 0.4
    hole = blob(cx, ty, w * 0.22, h * 0.09, seed + 1, 0.05, 14)
    rim = blob(cx, ty + 1, w * 0.25, h * 0.11, seed + 2, 0.05, 14)
    out.append(f'<path d="{rim}" fill="#F8C86A"/>' + dabs(["#FFE09A", "#E8A040"], seed, (cx - w * 0.25, ty - h * 0.1, cx + w * 0.25, ty + h * 0.1), 14, 0, (6, 14), (1, 2), (0.4, 0.7), 0.2))
    out.append(defs(rg(f"{u}-hg", [(0, "#FFD27A"), (0.5, "#C9601E"), (1, "#5A1E0A")], cy=0.7)))
    out.append(f'<path d="{hole}" fill="url(#{u}-hg)"/>' + ink(rim, "#7A3412", 1.8, seed, 1, 0.8) + ink(hole, "#5A1E0A", 1.6, seed, 1, 0.8))
    out.append(glow(f"{u}-tg", cx, ty - 6, w * 0.3, "#FFC24A", 0.45, 0.3))
    # pulp strings draped over the rim
    rnd = random.Random(seed)
    for k in range(5):
        x = cx + rnd.uniform(-w * 0.2, w * 0.2)
        out.append(ink(f"M {_f(x)} {_f(ty + 2)} q {_f(rnd.uniform(-8, 8))} {_f(h * 0.08)} {_f(rnd.uniform(-4, 4))} {_f(h * rnd.uniform(0.12, 0.22))}", "#F2A23A", 2.4, seed + k, 1, 0.9))
        out.append(f'<path d="{seed_d(x + rnd.uniform(-6, 6), ty + h * rnd.uniform(0.08, 0.18), 7, rnd.uniform(0, 180), k)}" fill="#F6EAC8"/>')
    # carved left eye, glowing
    ex, ey = cx - w * 0.17, cy - h * 0.06
    eye = smooth_closed([(ex - w * 0.1, ey + h * 0.08), (ex, ey - h * 0.13), (ex + w * 0.1, ey + h * 0.08)])
    out.append(glow(f"{u}-eg", ex, ey, w * 0.18, "#FFC24A", 0.5, 0.3))
    out.append(defs(rg(f"{u}-ef", [(0, "#FFF6C8"), (0.5, "#FFC94A"), (1, "#E8761E")], cy=0.7)))
    out.append(f'<path d="{eye}" fill="url(#{u}-ef)" stroke="#7A2E10" stroke-width="2.2" stroke-linejoin="round"/>')
    out.append(f'<path d="{eye}" fill="none" stroke="#F8C86A" stroke-width="3" transform="translate(-2 2)" opacity="0.7"/>')
    # sketched right eye and smile, dashed marker
    ex2 = cx + w * 0.17
    eye2 = smooth_closed([(ex2 - w * 0.1, ey + h * 0.08), (ex2, ey - h * 0.13), (ex2 + w * 0.1, ey + h * 0.08)])
    mouth = smooth_closed([(cx - w * 0.26, cy + h * 0.1), (cx - w * 0.1, cy + h * 0.17), (cx, cy + h * 0.12), (cx + w * 0.1, cy + h * 0.17), (cx + w * 0.26, cy + h * 0.1),
                           (cx + w * 0.14, cy + h * 0.3), (cx, cy + h * 0.34), (cx - w * 0.14, cy + h * 0.3)])
    for d in (eye2, mouth):
        out.append(f'<path d="{d}" fill="none" stroke="#3A1A10" stroke-width="2.4" stroke-dasharray="7 5" stroke-linecap="round" opacity="0.85"/>')
    return "".join(out)


def lid(u, cx, cy, w, seed):
    d = blob(cx, cy, w / 2, w * 0.2, seed, 0.05, 14)
    under = blob(cx, cy + 2, w * 0.4, w * 0.13, seed + 1, 0.06, 12)
    return (cast_shadow(cx + 4, cy + w * 0.2, w * 0.5, w * 0.08, "#1A0A04", 0.35, seed)
            + body(f"{u}-ld", d, (cx - w / 2, cy - w * 0.2, cx + w / 2, cy + w * 0.2), PUMPKIN, [PUMPKIN_L, PUMPKIN_D], seed, n=20, angle=-90, length=(4, 10), width=(1, 2.4),
                   line="#7A3412", lw=2)
            + f'<path d="{under}" fill="#F8C86A"/>' + dabs(["#FFE09A", "#E8A040", "#F2A23A"], seed, (cx - w * 0.4, cy - 6, cx + w * 0.4, cy + 10), 14, 0, (5, 12), (1, 2), (0.4, 0.8), 0.3)
            + ink(f"M {_f(cx - w * 0.1)} {_f(cy + 4)} q {_f(-6)} 10 {_f(-2)} 16", "#F2A23A", 2.2, seed, 1, 0.9)
            + f'<path d="M {_f(cx - 4)} {_f(cy - w * 0.16)} q -2 {_f(-w * 0.2)} {_f(w * 0.12)} {_f(-w * 0.28)} l 5 6 q {_f(-w * 0.1)} {_f(w * 0.06)} {_f(-w * 0.06)} {_f(w * 0.24)} Z" fill="#6B5A2E"/>'
            + ink(f"M {_f(cx - 4)} {_f(cy - w * 0.16)} q -2 {_f(-w * 0.2)} {_f(w * 0.12)} {_f(-w * 0.28)}", "#3A2A10", 1.6, seed, 1, 0.8))


def scoop(u, x, y, L, ang, seed):
    """Wooden-handled carving scoop with a dab of pulp."""
    a = math.radians(ang)
    hx, hy = x + L * 0.55 * math.cos(a), y + L * 0.55 * math.sin(a)
    tx, ty = x + L * math.cos(a), y + L * math.sin(a)
    handle = limb_d([(x, y), ((x + hx) / 2, (y + hy) / 2), (hx, hy)], 14, 11, seed)
    shaft = limb_d([(hx, hy), (tx, ty)], 5, 5, seed + 1)
    bowl_ = blob(tx + 10 * math.cos(a), ty + 10 * math.sin(a), 16, 11, seed + 2, 0.06, 12, rot=ang)
    return (cast_shadow((x + tx) / 2 + 4, (y + ty) / 2 + 10, L * 0.5, 6, "#1A0A04", 0.3, seed)
            + plank(f"{u}-h", handle, (min(x, hx) - 10, min(y, hy) - 10, max(x, hx) + 10, max(y, hy) + 10), "#B07A4A", ["#C9965E", "#8A5A2E"], seed, angle=ang, knots=0, line="#3A1A10", lw=1.8)
            + f'<path d="{shaft}" fill="#B8B4C4"/>' + ink(shaft, "#3A3448", 1.4, seed, 1, 0.8)
            + body(f"{u}-b", bowl_, (tx - 30, ty - 30, tx + 30, ty + 30), "#C9C4D4", ["#FFFFFF", "#8A8498"], seed + 2, n=10, angle=ang, length=(4, 10), width=(1, 2), line="#3A3448", lw=1.8)
            + f'<path d="{blob(tx + 10 * math.cos(a), ty + 10 * math.sin(a), 9, 6, seed + 3, 0.15, 10)}" fill="#F2A23A"/>')


def bowl(u, cx, cy, w, seed, col="#5A6E8A", dark="#34445E", light="#8AA0BC"):
    rim = blob(cx, cy, w / 2, w * 0.14, seed, 0.03, 16)
    bd = smooth_closed([(cx - w / 2, cy), (cx - w * 0.42, cy + w * 0.24), (cx - w * 0.2, cy + w * 0.36), (cx + w * 0.2, cy + w * 0.36), (cx + w * 0.42, cy + w * 0.24), (cx + w / 2, cy)])
    return (cast_shadow(cx + 4, cy + w * 0.36, w * 0.45, 7, "#1A0A04", 0.35, seed)
            + body(f"{u}-bw", bd, (cx - w / 2, cy, cx + w / 2, cy + w * 0.36), col, [light, dark], seed, n=24, angle=0, length=(6, 16), width=(1, 2.6), line="#1A1422", lw=2)
            + "".join(f'<path d="M {_f(cx + t * w)} {_f(cy + w * 0.06)} l 0 {_f(w * 0.24 * (1 - abs(t) * 1.4))}" stroke="#FFE2B0" stroke-width="3" opacity="0.6" stroke-linecap="round"/>' for t in (-0.2, 0, 0.2))
            + f'<path d="{rim}" fill="#E8A040"/>' + seeds(seed, (cx - w * 0.4, cy - w * 0.1, cx + w * 0.4, cy + w * 0.06), 16, (8, 11), keep=lambda x, y: ((x - cx) / (w * 0.45)) ** 2 + ((y - cy) / (w * 0.12)) ** 2 < 1)
            + ink(rim, "#1A1422", 2, seed, 1, 0.85))


@design("carve-out-some-fun")
def d_carve_out_some_fun():
    u = "hgb-cof"
    # cosy kitchen wall at night, lit by candles
    out = [f'<rect width="600" height="600" fill="#2E1E2E"/>']
    out.append(dabs(["#3A2638", "#24162A", "#463044", "#2A1A2C"], 501, (-40, -20, 620, 420), 260, -88, (30, 90), (3, 9), (0.2, 0.45), 0.08))
    # little window with the moon
    win = smooth_closed(jitter([(232, 350), (232, 262), (246, 236), (300, 222), (354, 236), (368, 262), (368, 350)], 502, 1))
    sky = (defs(lg(f"{u}-ws", [(0, "#1E1A44"), (1, "#3A2A62")])) + f'<rect x="220" y="216" width="160" height="140" fill="url(#{u}-ws)"/>'
           + stars(503, (240, 236, 362, 330), 10, BONE, 2, r=(0.6, 1.4), twr=(3, 5)) + pmoon(f"{u}-mn", 334, 262, 20, 504, halo_r=2.2, halo_op=0.45, craters=3)
           + paint_tree(f"{u}-wt", 254, 352, 80, 505, fill="#120C1E", spread=30, depth=4))
    out.append(clip(f"{u}-wc", win) + f'<g clip-path="url(#{u}-wc)">{sky}</g>')
    out.append(ink(win, "#120A16", 7, 506, 1, 1) + ink(win, "#6A4A5E", 2.4, 507, 1, 0.6))
    out.append(f'<path d="M 300 224 L 300 350 M 232 290 L 368 290" stroke="#120A16" stroke-width="5"/>')
    # warm light pooling on the wall
    out.append(glow(f"{u}-wg", 300, 380, 360, "#FFB547", 0.32, 0.35))
    # wooden table top
    top = smooth_closed([(-20, 360), (300, 352), (620, 360), (620, 620), (-20, 620)])
    out.append(plank(f"{u}-tb", top, (-20, 352, 620, 620), "#8A5A36", ["#A8744A", "#6A4026", "#B88A5A", "#7A4E2E"], 509, line=None, knots=3, n=260))
    for k in range(5):
        y = 380 + k * 46
        out.append(f'<path d="M -20 {y} Q 300 {y + 4} 620 {y - 2}" stroke="#3A1E10" stroke-width="2.2" opacity="0.45"/>')
    out.append(ink("M -20 360 Q 300 352 620 360", "#FFD8A0", 2.6, 510, 1, 0.5))
    out.append(eglow(f"{u}-tg", 300, 440, 300, 110, "#FFC24A", 0.3))
    # newspaper under the work
    npp = smooth_closed(jitter([(150, 392), (450, 380), (480, 520), (130, 534)], 511, 2))
    out.append(body(f"{u}-np", npp, (130, 380, 480, 534), "#E8E0CE", ["#F6F0E2", "#D2C8B2"], 511, n=30, angle=-4, length=(20, 50), width=(1, 3), line="#7A6A54", lw=1.6))
    out.append(clip(f"{u}-npc", npp) + f'<g clip-path="url(#{u}-npc)" stroke="#9A8C74" stroke-width="2" opacity="0.5">'
               + "".join(f'<path d="M {x0} {y} L {x0 + 120} {y - 3}"/>' for x0 in (160, 300) for y in range(410, 530, 9)) + "</g>")
    # candles and a finished jack glowing at the back
    out.append(candle(f"{u}-c1", 92, 384, 96, 30, 512, glow_r=130, glow_op=0.55))
    out.append(candle(f"{u}-c2", 130, 388, 58, 24, 513, glow_r=80))
    out.append(jack(f"{u}-jk", 492, 352, 96, 76, 514, face="classic", glow_r=140, glow_op=0.5))
    # the pumpkin being carved, its lid, the scoop and seeds
    out.append(cast_shadow(300, 478, 120, 14, "#1A0A04", 0.35, 515))
    out.append(carving_pumpkin(f"{u}-cp", 300, 416, 210, 128, 516))
    out.append(lid(f"{u}-ld", 150, 474, 70, 517))
    out.append(scoop(f"{u}-sc", 392, 520, 110, -18, 518))
    out.append(bowl(f"{u}-bw", 486, 470, 92, 519))
    out.append(seeds(520, (140, 470, 520, 540), 18, keep=lambda x, y: not (360 < x < 520 and y < 520) and abs(x - 150) > 40))
    # lettering
    out.append(label(300, 94, "CARVE OUT", CINZEL, 44, BONE, ls=10, rule=GOLD, line_w=40, seed=521))
    out.append(bword(f"{u}-t", 300, 196, "some fun!", SERIF_IT, 100, PUMPKIN_L, ["#FFD08A", "#E8792E", "#FFE2B0", "#C9601E"], 522, max_w=400,
                     shadow="#1A0A04", angle=-60, hi="#FFF2C0"))
    out.append(grain_over(f"{u}-gr", 523))
    return "".join(out)


# ---------------------------------------------------------------- nevermore
def raven(u, x, base, s, seed, fill="#141020", tints=("#2A2440", "#0A0812", "#33305A", "#1E1A30"), sheen="#7A86C8", rim="#E8D6A8", eye=GOLD):
    """Raven perched on a ledge, facing left, head turned slightly to the viewer; painted feathers with blue-violet sheen."""
    S = lambda pts: [(x + px * s, base + py * s) for px, py in pts]  # noqa: E731
    out = []
    tail = smooth_closed(jitter(S([(18, -30), (44, -6), (62, 16), (52, 20), (40, 12), (20, -8)]), seed, 0.4))
    bd = smooth_closed(jitter(S([(-26, -56), (-30, -40), (-24, -16), (-8, -2), (14, -4), (30, -20), (34, -38), (26, -60), (12, -72), (-6, -76), (-20, -70)]), seed + 1, 0.4))
    head = smooth_closed(jitter(S([(-34, -84), (-30, -100), (-16, -108), (0, -104), (6, -92), (2, -78), (-14, -72), (-30, -74)]), seed + 2, 0.3))
    beak = smooth_closed(S([(-30, -96), (-58, -92), (-64, -88), (-50, -84), (-30, -82)]))
    wing = smooth_closed(jitter(S([(-10, -66), (14, -66), (32, -50), (42, -22), (52, -2), (36, -6), (20, -14), (2, -30), (-8, -48)]), seed + 3, 0.4))
    for i, d in enumerate((tail, bd, head)):
        out.append(body(f"{u}-p{i}", d, (x - 70 * s, base - 110 * s, x + 70 * s, base + 25 * s), fill, list(tints), seed + i, n=int(30 * s), angle=-60 + i * 30,
                        length=(5 * s, 14 * s), width=(1, 2.2 * s), opacity=(0.35, 0.7), line="#05030A", lw=2))
    # throat hackles
    out.append(dabs(["#2A2440", "#05030A"], seed + 7, (x - 34 * s, base - 82 * s, x - 18 * s, base - 64 * s), 10, 100, (6 * s, 12 * s), (0.8, 1.8), (0.6, 0.9), 0.3))
    out.append(body(f"{u}-wg", wing, (x - 12 * s, base - 70 * s, x + 54 * s, base), "#1A1630", ["#2E2A50", "#0A0812", "#3E3A6A"], seed + 4, n=int(26 * s), angle=40,
                    length=(8 * s, 18 * s), width=(1, 2.4 * s), opacity=(0.35, 0.7), line="#05030A", lw=2))
    # feather tips on the wing
    for k in range(5):
        fx, fy = x + (10 + k * 8) * s, base + (-30 + k * 6) * s
        out.append(ink(f"M {_f(fx)} {_f(fy)} q {_f(6 * s)} {_f(2 * s)} {_f(10 * s)} {_f(9 * s)}", sheen, 1.6, seed + k, 1, 0.55))
    out.append(body(f"{u}-bk", beak, (x - 66 * s, base - 98 * s, x - 28 * s, base - 80 * s), "#2A2630", ["#4A4658", "#14121A"], seed + 5, n=8, angle=180,
                    length=(4 * s, 10 * s), width=(1, 2), line="#05030A", lw=1.8))
    out.append(ink(smooth_open(S([(-60, -90), (-44, -89), (-32, -89)])), "#6A6680", 1.2, seed, 1, 0.8))
    # moonlit rim along back and head
    out.append(ink(smooth_open(S([(-30, -100), (-16, -108), (0, -104), (6, -92)])), rim, 2.4, seed, 1, 0.75))
    out.append(ink(smooth_open(S([(12, -72), (26, -60), (34, -38), (42, -22), (52, -2)])), rim, 2.2, seed, 1, 0.65))
    out.append(ink(smooth_open(S([(-60, -92), (-46, -94), (-32, -97)])), rim, 1.6, seed, 1, 0.6))
    # sheen strokes
    out.append(dabs([sheen], seed + 8, (x - 20 * s, base - 70 * s, x + 20 * s, base - 20 * s), 8, -60, (6 * s, 14 * s), (0.6, 1.4), (0.3, 0.6), 0.3))
    # eye with a catchlight
    ex, ey = x - 20 * s, base - 94 * s
    out.append(f'<circle cx="{_f(ex)}" cy="{_f(ey)}" r="{_f(4.2 * s)}" fill="{eye}"/><circle cx="{_f(ex - 0.8 * s)}" cy="{_f(ey)}" r="{_f(2.4 * s)}" fill="#0A0812"/>'
               f'<circle cx="{_f(ex - 1.8 * s)}" cy="{_f(ey - 1.4 * s)}" r="{_f(1 * s)}" fill="#FFFFFF"/>')
    # feet gripping
    for k, fx in enumerate((-8, 6)):
        out.append(ink(f"M {_f(x + fx * s)} {_f(base - 4 * s)} l {_f(-1 * s)} {_f(8 * s)} m {_f(-5 * s)} 0 l {_f(10 * s)} 0", "#3A3440", 2.2, seed + k, 1, 1))
    return "".join(out)


def gothic_window(u, cx, top, w, h, seed, stone="#4A4458", tints=("#5E5870", "#2E2A3A", "#6E6880", "#3A3448"), line="#0E0A16"):
    """Stone pointed-arch window with Y tracery and leaded panes glowing from candlelight inside."""
    out = []
    by = top + h
    ow = w + 56
    spring = top + w * 0.62
    outer = smooth_closed([(cx - ow / 2, by + 24), (cx - ow / 2, spring), (cx - ow * 0.36, top + w * 0.06), (cx, top - 30), (cx + ow * 0.36, top + w * 0.06),
                           (cx + ow / 2, spring), (cx + ow / 2, by + 24)])
    # pointed arch from two arcs
    inner = (f"M {_f(cx - w / 2)} {_f(by)} L {_f(cx - w / 2)} {_f(spring)} A {_f(w * 0.95)} {_f(w * 0.95)} 0 0 1 {_f(cx)} {_f(top)} "
             f"A {_f(w * 0.95)} {_f(w * 0.95)} 0 0 1 {_f(cx + w / 2)} {_f(spring)} L {_f(cx + w / 2)} {_f(by)} Z")
    out.append(body(f"{u}-st", outer, (cx - ow / 2, top - 30, cx + ow / 2, by + 24), stone, list(tints), seed, n=200, angle=-80, length=(10, 30), width=(2, 5), line=line, lw=2.6))
    # stone blocks (voussoirs) around the arch
    blocks = []
    for k in range(-5, 6):
        a = math.radians(-90 + k * 15)
        r0, r1 = w * 0.5 + 4, w * 0.5 + 26
        bx, byy = cx, spring
        blocks.append(f"M {_f(cx + r0 * math.cos(a) * 1.0)} {_f(spring - 6 + r0 * math.sin(a) * 1.25)} L {_f(cx + r1 * math.cos(a))} {_f(spring - 6 + r1 * math.sin(a) * 1.22)}")
    for y in range(int(spring + 30), int(by + 20), 34):
        for sg in (-1, 1):
            blocks.append(f"M {_f(cx + sg * (w / 2 + 2))} {y} L {_f(cx + sg * (ow / 2))} {y}")
    out.append(clip(f"{u}-sc", outer) + f'<g clip-path="url(#{u}-sc)" stroke="{line}" stroke-width="2" opacity="0.55" fill="none">' + "".join(f'<path d="{d}"/>' for d in blocks) + "</g>")
    out.append(rim_lit(f"{u}-sr", outer, 2, 2, "#B8B0D8", 3, 0.5))
    # glowing glass
    out.append(glow(f"{u}-gg", cx, by - h * 0.35, w * 1.3, "#FFB547", 0.45, 0.35))
    out.append(defs(rg(f"{u}-gl", [(0, "#FFF2B8"), (0.45, "#FFC94A"), (1, "#C9601E")], cy=0.72, r=0.8)))
    out.append(f'<path d="{inner}" fill="url(#{u}-gl)"/>')
    out.append(brush(f"{u}-gb", inner, (cx - w / 2, top, cx + w / 2, by), ["#FFF6D0", "#F2A23A", "#FFE08A", "#E8862A"], seed + 1, 90, angle=-75, length=(10, 30), width=(1, 3), opacity=(0.2, 0.5)))
    # a few coloured panes
    rnd = random.Random(seed)
    panes = []
    for i in range(10):
        px, py = cx + rnd.uniform(-w * 0.4, w * 0.4), top + rnd.uniform(h * 0.15, h * 0.85)
        panes.append(f'<path d="{blob(px, py, w * 0.07, w * 0.09, rnd.randrange(999), 0.1, 6)}" fill="{rnd.choice(["#B05ACB", "#E8762E", "#9BD14B", "#C9302A"])}" opacity="0.35"/>')
    out.append(clip(f"{u}-pc", inner) + f'<g clip-path="url(#{u}-pc)">' + "".join(panes)
               # leading: diamond lattice
               + "".join(f'<path d="M {_f(cx - w + k * 22)} {_f(top - 20)} l {w * 1.2:.1f} {h * 1.2:.1f}" stroke="#2A1A10" stroke-width="1.6" opacity="0.55"/>' for k in range(0, int(w * 2.4 / 22)))
               + "".join(f'<path d="M {_f(cx + w - k * 22)} {_f(top - 20)} l {-w * 1.2:.1f} {h * 1.2:.1f}" stroke="#2A1A10" stroke-width="1.6" opacity="0.55"/>' for k in range(0, int(w * 2.4 / 22)))
               + "</g>")
    # tracery: central mullion splitting into a Y, plus a small rose
    tr = (f"M {_f(cx)} {_f(by)} L {_f(cx)} {_f(spring + 10)} M {_f(cx)} {_f(spring + 10)} Q {_f(cx - w * 0.22)} {_f(spring - w * 0.12)} {_f(cx - w * 0.3)} {_f(top + w * 0.3)} "
          f"M {_f(cx)} {_f(spring + 10)} Q {_f(cx + w * 0.22)} {_f(spring - w * 0.12)} {_f(cx + w * 0.3)} {_f(top + w * 0.3)}")
    out.append(f'<path d="{tr}" stroke="{stone}" stroke-width="10" fill="none" stroke-linecap="round"/>' + ink(tr, line, 2.2, seed, 1, 0.7))
    rose = blob(cx, top + w * 0.36, w * 0.11, w * 0.11, seed, 0.02, 14)
    out.append(f'<path d="{rose}" fill="#E8762E" opacity="0.6"/><path d="{rose}" fill="none" stroke="{stone}" stroke-width="7"/>' + ink(rose, line, 2, seed, 1, 0.7))
    out.append(ink(inner, line, 3, seed, 2, 0.95))
    # sill
    sill = smooth_closed([(cx - ow / 2 - 14, by + 4), (cx + ow / 2 + 14, by + 4), (cx + ow / 2 + 10, by + 26), (cx - ow / 2 - 10, by + 26)])
    out.append(body(f"{u}-sl", sill, (cx - ow / 2 - 14, by, cx + ow / 2 + 14, by + 26), "#5E5870", list(tints), seed + 3, n=40, angle=0, length=(10, 30), width=(1.5, 4),
                    line=line, lw=2.4))
    out.append(ink(f"M {_f(cx - ow / 2 - 12)} {_f(by + 6)} L {_f(cx + ow / 2 + 12)} {_f(by + 6)}", "#C9C2E8", 2.2, seed, 1, 0.6))
    return "".join(out)


def ivy(u, pts, seed, leaf=("#4E6A3E", "#3A5230", "#6A8A4A"), line="#1A2414"):
    rnd = random.Random(seed)
    out = [ink(smooth_open(pts), "#3A3020", 2.4, seed, 1, 0.9)]
    for i in range(len(pts) - 1):
        for t in (0.3, 0.75):
            x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t
            y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t
            sg = rnd.choice((-1, 1))
            lx, ly = x + sg * 10, y + rnd.uniform(-4, 6)
            d = smooth_closed([(x, y), (lx - 6, ly - 8), (lx + sg * 8, ly - 6), (lx + sg * 10, ly + 2), (lx, ly + 8)])
            out.append(f'<path d="{d}" fill="{rnd.choice(leaf)}"/>' + ink(d, line, 1.2, seed + i, 1, 0.6))
    return "".join(out)


@design("nevermore")
def d_nevermore():
    u = "hgb-nvm"
    # night sky above a stone wall
    out = [night_sky(u, 531, [(0, "#0E0C22"), (0.6, "#1E1A40"), (1, "#2E2450")], ["#221C46", "#2E2858", "#14102C", "#38306A"], n=260)]
    out.append(stars(532, (20, 20, 580, 200), 26, BONE, 4))
    # stone wall
    wall = rect_d(-10, 60, 610, 610)
    out.append(body(f"{u}-wl", wall, (-10, 60, 610, 610), "#2E2A3E", ["#3A3650", "#1E1A2C", "#46425C"], 533, n=260, angle=-4, length=(30, 80), width=(3, 8), opacity=(0.2, 0.45)))
    rnd = random.Random(534)
    bricks = []
    for row, y in enumerate(range(60, 600, 40)):
        off = 0 if row % 2 else 40
        bricks.append(f"M -10 {y} L 610 {y + rnd.uniform(-1, 1):.1f}")
        for x in range(-40 + off, 640, 80):
            bricks.append(f"M {x + rnd.uniform(-2, 2):.1f} {y} L {x + rnd.uniform(-2, 2):.1f} {y + 40}")
    out.append(f'<g stroke="#120E1C" stroke-width="2.4" opacity="0.7" fill="none">' + "".join(f'<path d="{d}"/>' for d in bricks) + "</g>")
    out.append(f'<g stroke="#5A5478" stroke-width="1.4" opacity="0.4" fill="none" transform="translate(0 2)">' + "".join(f'<path d="{d}"/>' for d in bricks[::3]) + "</g>")
    out.append(defs(lg(f"{u}-wf", [(0, "#0A0816", 0.75), (0.25, "#0A0816", 0), (1, "#0A0816", 0)])) + f'<rect y="60" width="600" height="540" fill="url(#{u}-wf)"/>')
    out.append(gothic_window(f"{u}-gw", 300, 150, 196, 270, 535))
    out.append(ivy(f"{u}-iv", [(610, 140), (560, 170), (536, 230), (530, 300), (540, 360)], 536))
    out.append(ivy(f"{u}-iv2", [(-10, 410), (40, 430), (70, 400), (80, 350)], 537))
    out.append(candle(f"{u}-c1", 352, 418, 44, 18, 538, glow_r=60, glow_op=0.4))
    out.append(raven(f"{u}-rv", 236, 422, 1.25, 539))
    # lettering: a quiet label above the window, the hero word below
    out.append(label(300, 86, "QUOTH THE RAVEN", JOS, 24, GOLD, ls=8, rule=GOLD, line_w=30, seed=540))
    out.append(defs(lg(f"{u}-fg", [(0, "#0A0816", 0), (0.4, "#0A0816", 0.7), (1, "#05030A", 0.9)])) + f'<rect y="452" width="600" height="148" fill="url(#{u}-fg)"/>')
    fs = fit_size("NEVERMORE", CINZEL, 70, 440, 6)
    out.append(bword(f"{u}-t", 300, 528, "NEVERMORE", CINZEL, fs, BONE, ["#FFFFFF", "#D8C8A8", "#F8F0DE", "#B8A888"], 541, max_w=440, ls=6,
                     shadow="#05030A", angle=-80, hi="#FFFFFF"))
    out.append(grain_over(f"{u}-gr", 542))
    return "".join(out)


# ---------------------------------------------------------------- witch way?
def arrow_sign(u, cx, cy, w, h, point, seed, wood="#B8864E", tints=("#D8A86A", "#8A5A2E", "#E8C48E", "#A8743E"), rot=0):
    """Hand-cut wooden arrow board; point = 1 (right) or -1 (left)."""
    tip = w * 0.14
    x0, x1 = cx - w / 2, cx + w / 2
    if point > 0:
        pts = [(x0, cy - h / 2), (x1 - tip, cy - h / 2), (x1, cy), (x1 - tip, cy + h / 2), (x0, cy + h / 2), (x0 + 6, cy)]
    else:
        pts = [(x1, cy - h / 2), (x0 + tip, cy - h / 2), (x0, cy), (x0 + tip, cy + h / 2), (x1, cy + h / 2), (x1 - 6, cy)]
    d = "M " + " L ".join(f"{_f(x)} {_f(y)}" for x, y in jitter(pts, seed, 1.2)) + " Z"
    return (f'<g transform="rotate({rot} {_f(cx)} {_f(cy)})">' + f'<path d="{d}" fill="#05030A" opacity="0.35" transform="translate(5 7)"/>'
            + plank(f"{u}-pl", d, (x0, cy - h / 2, x1, cy + h / 2), wood, list(tints), seed, grain_c="#5A3A1A", knots=1, line="#2A1608", lw=2.6)
            + "".join(f'<circle cx="{_f(nx)}" cy="{_f(cy)}" r="3.4" fill="#3A2A20"/><circle cx="{_f(nx - 1)}" cy="{_f(cy - 1)}" r="1.2" fill="#C9B8A0"/>'
                      for nx in (x0 + 12 + (tip if point < 0 else 0), x1 - 12 - (tip if point > 0 else 0))) + "</g>"), d


@design("witch-way")
def d_witch_way():
    u = "hgb-wwy"
    out = [night_sky(u, 561, [(0, "#120E28"), (0.55, "#2A1E4E"), (0.85, "#4A3068"), (1, "#5A3A6A")], ["#2A2050", "#3A2A62", "#1A1434", "#4A3470"], n=280)]
    out.append(stars(562, (20, 20, 580, 360), 34, BONE, 5, keep=lambda x, y: math.hypot(x - 128, y - 136) > 70))
    out.append(swirl(128, 136, 54, 140, ["#5B4888", "#7A66A8", "#C9A86A"], 563, 40, (2, 7), (30, 90), (0.12, 0.34)))
    out.append(pmoon(f"{u}-mn", 128, 136, 50, 564, halo_r=2.6, halo_op=0.4))
    out.append(bat(f"{u}-b1", 470, 96, 24, 565, rot=10, flap=0.2))
    out.append(bat(f"{u}-b2", 512, 128, 16, 566, rot=-12, flap=-0.2))
    # far hills and a tiny haunted house on the horizon
    out.append(ground(f"{u}-h1", [(-20, 380), (120, 360), (260, 372), (400, 350), (520, 362), (620, 352)], 620, "#2A2248", ["#3A3060", "#1E1838", "#4A3E70"], 567))
    hh = "M 456 358 L 456 330 L 474 314 L 492 330 L 492 358 Z M 486 322 L 486 308 L 491 308 L 491 326 Z M 492 340 L 512 340 L 512 358 L 492 358 Z M 488 342 L 502 330 L 516 342 Z"
    out.append(f'<path d="{hh}" fill="#16101F"/>' + glow(f"{u}-hg", 474, 338, 16, "#FFB547", 0.5, 0.3)
               + f'<path d="M 470 334 L 470 344 L 478 344 L 478 334 Z M 500 346 L 500 352 L 506 352 L 506 346 Z" fill="{GOLD}"/>')
    out.append(paint_tree(f"{u}-tr", 54, 392, 140, 568, fill="#16101F", rim="#8A76B8", lean=-6, spread=34, depth=5))
    # pumpkin patch foreground
    out.append(ground(f"{u}-h2", [(-20, 446), (120, 432), (300, 440), (460, 428), (620, 440)], 620, "#1E2A26", ["#2A3A30", "#121C18", "#34483A"], 569, rim="#7A9A58"))
    out.append(grass_tufts(570, (0, 430, 600, 470), 50, ["#3A5232", "#2A3A26", "#5A7A44"]))
    # the signpost
    post = limb_d([(300, 470), (302, 300), (298, 128)], 22, 18, 571)
    out.append(cast_shadow(300, 470, 60, 8, "#05030A", 0.5, 572))
    out.append(plank(f"{u}-po", post, (286, 120, 316, 472), "#6A4630", ["#8A5E40", "#4A2E1E", "#9A6E4E"], 573, angle=-90, knots=2, line="#1A0E08", lw=2.4))
    # boards
    s1, d1 = arrow_sign(f"{u}-a1", 300, 190, 400, 92, 1, 574, rot=-3)
    s2, d2 = arrow_sign(f"{u}-a2", 262, 292, 230, 56, -1, 575, wood="#A8743E", rot=4)
    s3, d3 = arrow_sign(f"{u}-a3", 344, 366, 210, 52, 1, 576, wood="#C99A5E", rot=-5)
    out.append(s3 + s2 + s1)
    out.append(f'<g transform="rotate(-3 300 190)">' + bword(f"{u}-t", 290, 222, "WITCH WAY?", ANTON, 74, "#3A1E10", ["#5A2E18", "#2A1408", "#6A3A20"], 577,
                                                              max_w=320, ls=4, shadow="#E8C48E", sd=0.03) + "</g>")
    out.append(f'<g transform="rotate(4 262 292)">' + bword(f"{u}-t2", 272, 308, "CANDY", BEBAS, 46, "#4E2A6E", ["#6A3E8E", "#2E1848"], 578, max_w=150, ls=6) + "</g>")
    out.append(f'<g transform="rotate(-5 344 366)">' + bword(f"{u}-t3", 334, 381, "SPELLS", BEBAS, 44, "#4E2A6E", ["#6A3E8E", "#2E1848"], 579, max_w=140, ls=6) + "</g>")
    # witch hat on the post top, a crow on the big arrow, a lantern hanging below
    out.append(witch_hat_painted(f"{u}-wh", 300, 142, 92, 580))
    out.append(raven(f"{u}-cr", 462, 146, 0.62, 581, eye="#FFE29A"))
    out.append(ink("M 196 318 L 196 330", "#1A0E08", 2.4, 582, 1, 1))
    out.append(porch_lantern(f"{u}-lt", 196, 326, 1.1, 583))
    # pumpkins around the post
    out.append(jack(f"{u}-j1", 218, 448, 72, 58, 584, face="cute", glow_r=100))
    out.append(painted_pumpkin(f"{u}-p1", 392, 456, 54, 40, 585))
    out.append(painted_pumpkin(f"{u}-p2", 432, 466, 34, 26, 586, "#E8D9BC", "#B8A07A", "#FFF6E2"))
    out.append(painted_pumpkin(f"{u}-p3", 122, 470, 40, 30, 587, "#E8A23A", "#B9731E", "#F8C85A"))
    out.append(defs(lg(f"{u}-fg", [(0, NIGHT, 0), (0.5, NIGHT, 0.5), (1, "#0A0816", 0.8)])) + f'<rect y="476" width="600" height="124" fill="url(#{u}-fg)"/>')
    out.append(label(300, 532, "THIS WAY TO THE MAGIC", JOS, 22, BONE, ls=5, rule=GOLD, line_w=30, seed=588, max_w=400))
    out.append(grain_over(f"{u}-gr", 589))
    return "".join(out)


def witch_hat_painted(u, cx, base, w, seed, hat="#2E2244", tints=("#4A3A66", "#1A1228", "#5A4878"), band=PUMPKIN, buckle=GOLD, line="#0A0612"):
    """Crumpled witch hat with a bent tip, an orange band and a gold buckle; base = brim centre."""
    brim = blob(cx, base, w * 0.6, w * 0.13, seed, 0.04, 18)
    cone = smooth_closed([(cx - w * 0.3, base - 2), (cx - w * 0.2, base - w * 0.4), (cx - w * 0.06, base - w * 0.72), (cx + w * 0.08, base - w * 0.9),
                          (cx + w * 0.3, base - w * 0.98), (cx + w * 0.4, base - w * 0.9), (cx + w * 0.2, base - w * 0.84), (cx + w * 0.12, base - w * 0.6),
                          (cx + w * 0.2, base - w * 0.3), (cx + w * 0.3, base - 2)])
    out = [body(f"{u}-br", brim, (cx - w * 0.6, base - w * 0.13, cx + w * 0.6, base + w * 0.13), hat, list(tints), seed, n=30, angle=0, length=(8, 24), width=(1.5, 3.5), line=line, lw=2.4),
           body(f"{u}-cn", cone, (cx - w * 0.3, base - w, cx + w * 0.4, base), hat, list(tints), seed + 1, n=50, angle=-70, length=(8, 24), width=(1.5, 3.5), line=line, lw=2.4),
           rim_lit(f"{u}-rl", cone, -2, 2, "#B9A6E0", 3, 0.6)]
    bd = smooth_closed([(cx - w * 0.29, base - 4), (cx - w * 0.26, base - w * 0.16), (cx + w * 0.25, base - w * 0.16), (cx + w * 0.29, base - 4)])
    out.append(body(f"{u}-bd", bd, (cx - w * 0.3, base - w * 0.18, cx + w * 0.3, base), band, [PUMPKIN_L, PUMPKIN_D], seed + 2, n=12, angle=0, length=(6, 16), width=(1, 2.4),
                    line=line, lw=1.8))
    bk = f"M {_f(cx - w * 0.07)} {_f(base - w * 0.15)} L {_f(cx + w * 0.07)} {_f(base - w * 0.15)} L {_f(cx + w * 0.07)} {_f(base - w * 0.02)} L {_f(cx - w * 0.07)} {_f(base - w * 0.02)} Z"
    out.append(f'<path d="{bk}" fill="none" stroke="{buckle}" stroke-width="{_f(w * 0.03)}" stroke-linejoin="round"/>')
    out.append(f'<path d="M {_f(cx - w * 0.55)} {_f(base + w * 0.02)} Q {_f(cx)} {_f(base + w * 0.12)} {_f(cx + w * 0.55)} {_f(base + w * 0.02)}" stroke="#7A66A0" stroke-width="2.4" fill="none" opacity="0.6"/>')
    return "".join(out)


def build(only=None):
    for slug, fn in DESIGNS.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:])
