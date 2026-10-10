"""Halloween, painted edition: every magnet is a small gouache-style night painting — graded skies, real
moonlight and candlelight, glowing carved pumpkins, misty layers, rim-lit silhouettes — paired with designed
type. Cute-spooky and family friendly. Run: python3 halloween_painted.py [slug ...]"""
import math
import random
import sys
import zlib

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from paint import P, blobs, dots, glow, grass, lg, mist, rg, rough, y_on
from poster import ANTON

COL = "halloween"

# ---------------------------------------------------------------- palette
INK = "#120D18"        # night black with a violet cast
NIGHT = "#1C1430"
PURPLE = "#3B2357"
PLUM = "#5B2F72"
LILAC = "#9C86C4"
ORANGE = "#EE7F2D"
DEEP_OR = "#B9481A"
AMBER = "#FFB547"
CANDLE = "#FFE7A3"
SLIME = "#9BD14B"
SLIME_D = "#4D7A26"
BONE = "#F4EBD9"
BONE_D = "#D8C9AE"
MOONC = "#F8E9BC"


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


def bg(u, stops, x1=0, y1=0, x2=0, y2=1):
    return defs(lg(f"{u}-bg", stops, x1, y1, x2, y2)) + f'<rect width="600" height="600" fill="url(#{u}-bg)"/>'


def vignette(u, color="#05030A", strength=0.6, inner=0.55):
    return defs(rg(f"{u}-vig", [(inner, color, 0), (1, color, strength)], r=0.75)) + f'<rect width="600" height="600" fill="url(#{u}-vig)"/>'


def twinkle(x, y, r, col, op=1.0):
    k = r * 0.2
    return (f'<path d="M {x:.1f} {y - r:.1f} Q {x + k:.1f} {y - k:.1f} {x + r:.1f} {y:.1f} Q {x + k:.1f} {y + k:.1f} {x:.1f} {y + r:.1f} '
            f'Q {x - k:.1f} {y + k:.1f} {x - r:.1f} {y:.1f} Q {x - k:.1f} {y - k:.1f} {x:.1f} {y - r:.1f} Z" fill="{col}" opacity="{op:.2f}"/>')


def starfield(seed, n, box, col=BONE, tw=5, avoid=None, r=(0.6, 1.7)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = []
    while len(out) < n:
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if avoid and math.hypot(x - avoid[0], y - avoid[1]) < avoid[2]:
            continue
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(*r):.2f}" opacity="{rnd.uniform(0.35, 1):.2f}"/>')
    tws = []
    while len(tws) < tw:
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if avoid and math.hypot(x - avoid[0], y - avoid[1]) < avoid[2]:
            continue
        tws.append(twinkle(x, y, rnd.uniform(4, 8), col, rnd.uniform(0.7, 1)))
    return f'<g fill="{col}">' + "".join(out) + "</g>" + "".join(tws)


def word(x, y, s, font, size, fill, max_w=470, ls=0, anchor="middle", glow_col=None, glow_op=0.35, shadow=None,
         sdx=0, sdy=5, outline=None, ow=0, extra=""):
    """Designed type: optional soft glow, offset shadow and outline, auto-fitted to max_w."""
    size = fit_size(s, font, size, max_w, ls)
    if anchor == "middle" and ls:
        x += ls / 2
    a = f'text-anchor="{anchor}" {font} font-size="{size}"' + (f' letter-spacing="{ls}"' if ls else "")
    t = esc(s)
    out = []
    if glow_col:
        w = measure(s, font, size, ls)
        gx = x - (ls / 2 if anchor == "middle" and ls else 0)
        gx = gx if anchor == "middle" else (gx + w / 2 if anchor == "start" else gx - w / 2)
        uid = f"wg{zlib.crc32(f'{s}{x:.0f}{y:.0f}{glow_col}'.encode()):x}"
        out.append(mist(gx, y - size * 0.34, w * 0.62 + size * 0.2, size * 0.62, glow_col, uid, glow_op))
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" {a} fill="none" stroke="{glow_col}" stroke-width="{size * 0.07:.1f}" stroke-linejoin="round" opacity="{glow_op * 0.6:.2f}">{t}</text>')
    if shadow:
        st = f' stroke="{shadow}" stroke-width="{ow}" stroke-linejoin="round"' if outline else ""
        out.append(f'<text x="{x + sdx:.1f}" y="{y + sdy:.1f}" {a} fill="{shadow}"{st}>{t}</text>')
    if outline:
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" {a} fill="{fill}" stroke="{outline}" stroke-width="{ow}" stroke-linejoin="round" paint-order="stroke"{extra}>{t}</text>')
    else:
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" {a} fill="{fill}"{extra}>{t}</text>')
    return "".join(out)


def ruled(x, y, s, font, size, fill, ls=5, gap=14, line_w=40, sw=2, line=None, dots_end=True):
    """Small spaced label flanked by rules ending in diamonds."""
    w = measure(s, font, size, ls) - ls
    mid = y - size * 0.35
    lc = line or fill
    out = [word(x, y, s, font, size, fill, max_w=600, ls=ls)]
    for sgn in (-1, 1):
        a = x + sgn * (w / 2 + gap)
        b = a + sgn * line_w
        out.append(f'<line x1="{a:.1f}" y1="{mid:.1f}" x2="{b:.1f}" y2="{mid:.1f}" stroke="{lc}" stroke-width="{sw}"/>')
        if dots_end:
            out.append(f'<rect x="{b - 3.5:.1f}" y="{mid - 3.5:.1f}" width="7" height="7" transform="rotate(45 {b:.1f} {mid:.1f})" fill="{lc}"/>')
    return "".join(out)


def arc_word(s, cx, cy, r, font, size, fill, ls=0, uid="arc", top=True, outline=None, ow=0):
    d = f"M {cx - r} {cy} A {r} {r} 0 0 {1 if top else 0} {cx + r} {cy}"
    lsa = f' letter-spacing="{ls}"' if ls else ""
    st = f' stroke="{outline}" stroke-width="{ow}" stroke-linejoin="round" paint-order="stroke"' if outline else ""
    return (f'<defs><path id="{uid}" d="{d}" fill="none"/></defs>'
            f'<text {font} font-size="{size}"{lsa} fill="{fill}"{st} text-anchor="middle"><textPath href="#{uid}" startOffset="50%">{esc(s)}</textPath></text>')


def ribbon(u, cx, cy, w, h, col, dark, tail=34, fold=12):
    """Banner ribbon with notched tails folding behind."""
    l, r, t, b = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    out = []
    for sgn, edge in ((-1, l), (1, r)):
        e2 = edge + sgn * tail
        out.append(f'<polygon points="{P([(edge - sgn * 4, t + fold), (e2, t + fold), (e2 - sgn * 12, b + fold - h / 2), (e2, b + fold), (edge - sgn * 4, b + fold)])}" fill="{dark}"/>')
        out.append(f'<polygon points="{P([(edge, b), (edge - sgn * 2, b + fold), (edge + sgn * fold * 0.9, b + fold)])}" fill="#000" opacity="0.45"/>')
    out.append(defs(lg(f"{u}-rib", [(0, col), (0.55, col), (1, dark)])))
    out.append(f'<path d="M {l} {t} Q {cx} {t - 8} {r} {t} L {r} {b} Q {cx} {b - 8} {l} {b} Z" fill="url(#{u}-rib)"/>')
    out.append(f'<path d="M {l + 6} {t + 5} Q {cx} {t - 3} {r - 6} {t + 5}" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.25"/>')
    return "".join(out)


# ---------------------------------------------------------------- painted pieces
def moon(u, cx, cy, r, base=MOONC, shade="#D9B978", halo="#FFE9B0", halo_r=2.1, halo_op=0.5, seed=3):
    rnd = random.Random(seed)
    out = [defs(rg(f"{u}-mn", [(0, "#FFFBEA"), (0.55, base), (1, shade)], cx=0.4, cy=0.36, r=0.66),
                f'<clipPath id="{u}-mnc"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'),
           glow(cx, cy, r * halo_r, halo, f"{u}-mh", halo_op),
           f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{u}-mn)"/>',
           f'<g clip-path="url(#{u}-mnc)">']
    # maria (soft dark seas) and craters with lit rims
    for _ in range(5):
        a, d = rnd.uniform(0, 6.28), rnd.uniform(0.1, 0.6) * r
        rr = r * rnd.uniform(0.18, 0.34)
        out.append(f'<ellipse cx="{cx + d * math.cos(a):.1f}" cy="{cy + d * math.sin(a):.1f}" rx="{rr:.1f}" ry="{rr * 0.75:.1f}" fill="{shade}" opacity="0.32"/>')
    for _ in range(int(6 + r / 20)):
        a, d = rnd.uniform(0, 6.28), rnd.uniform(0, 0.85) * r
        rr = r * rnd.uniform(0.03, 0.09)
        x, y = cx + d * math.cos(a), cy + d * math.sin(a)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="{shade}" opacity="0.5"/>'
                   f'<path d="M {x + rr * 0.7:.1f} {y - rr * 0.7:.1f} A {rr} {rr} 0 0 1 {x + rr * 0.7:.1f} {y + rr * 0.7:.1f}" fill="none" stroke="#FFF8E0" stroke-width="{max(1, rr * 0.3):.1f}" opacity="0.6"/>')
    out.append(f'<circle cx="{cx + r * 0.25:.1f}" cy="{cy + r * 0.25:.1f}" r="{r:.1f}" fill="none" stroke="{shade}" stroke-width="{r * 0.35:.1f}" opacity="0.25"/>')
    out.append("</g>")
    return "".join(out)


def cloud_wisp(x, y, w, col, op=0.5, seed=1):
    rnd = random.Random(seed)
    out = []
    for i in range(7):
        t = i / 6
        out.append(f'<ellipse cx="{x + (t - 0.5) * w:.1f}" cy="{y + rnd.uniform(-3, 3):.1f}" rx="{w * rnd.uniform(0.12, 0.2):.1f}" ry="{rnd.uniform(4, 9):.1f}"/>')
    return f'<g fill="{col}" opacity="{op}">' + "".join(out) + "</g>"


def bat(cx, cy, s, fill="#140E1A", rim=None, rot=0, flap=0, eyes=None):
    """Scallop-winged bat; s = wingspan/2 (px). flap tilts the wings up (+) or down (-)."""
    k = s / 96
    wing = "M 6 -6 C 24 -22 48 -30 70 -28 L 96 -36 Q 88 -16 82 -6 Q 72 -14 62 -3 Q 52 -12 42 1 Q 30 -7 20 7 Q 13 2 6 6 Z"
    edge = "M 6 -6 C 24 -22 48 -30 70 -28 L 96 -36"
    out = [f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.1f}) scale({k:.3f})">']
    for sx in (1, -1):
        out.append(f'<g transform="scale({sx} 1) rotate({-flap})"><path d="{wing}" fill="{fill}"/>'
                   + (f'<path d="{edge}" fill="none" stroke="{rim}" stroke-width="{2.2 / k * 0.6:.1f}" stroke-linecap="round" opacity="0.8"/>' if rim else "")
                   + f'<path d="M 12 -8 L 40 0 M 30 -14 L 58 -2" stroke="{fill}" stroke-width="3" opacity="0.6"/></g>')
    out.append(f'<ellipse cx="0" cy="3" rx="11" ry="17" fill="{fill}"/><circle cx="0" cy="-12" r="9.5" fill="{fill}"/>'
               f'<path d="M -9 -15 L -7 -30 L -1 -19 Z M 9 -15 L 7 -30 L 1 -19 Z" fill="{fill}"/>')
    if rim:
        out.append(f'<path d="M -6 -29 L -8 -16 M 7 -29 L 9 -16" stroke="{rim}" stroke-width="{1.6 / k * 0.6:.1f}" opacity="0.7"/>')
    if eyes:
        out.append(f'<circle cx="-3.6" cy="-12" r="2.2" fill="{eyes}"/><circle cx="3.6" cy="-12" r="2.2" fill="{eyes}"/>')
    out.append("</g>")
    return "".join(out)


def gnarly_tree(x, base, h, seed, fill, depth=6, lean=0.0, spread=32, w0=None, rim=None, rim_side=1):
    """Recursive bare tree with tapering crooked limbs; rim paints a moonlit edge on one side."""
    rnd = random.Random(seed)
    segs, rims = [], []
    w0 = w0 or h * 0.075

    def limb(x0, y0, ang, L, w, d):
        if d == 0 or L < 3:
            return
        bend = rnd.uniform(-14, 14)
        a1 = math.radians(ang + bend * 0.5)
        mx, my = x0 + L * 0.5 * math.cos(a1), y0 + L * 0.5 * math.sin(a1)
        a2 = math.radians(ang + bend)
        x1, y1 = mx + L * 0.5 * math.cos(a2), my + L * 0.5 * math.sin(a2)
        w1 = w * 0.62
        nx, ny = -math.sin(math.radians(ang)), math.cos(math.radians(ang))
        pts = [(x0 + nx * w / 2, y0 + ny * w / 2), (mx + nx * (w + w1) / 4, my + ny * (w + w1) / 4), (x1 + nx * w1 / 2, y1 + ny * w1 / 2),
               (x1 - nx * w1 / 2, y1 - ny * w1 / 2), (mx - nx * (w + w1) / 4, my - ny * (w + w1) / 4), (x0 - nx * w / 2, y0 - ny * w / 2)]
        segs.append(f'<polygon points="{P(pts)}"/>')
        if w1 > 1.4:
            segs.append(f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="{w1 / 2:.1f}"/>')
        if rim and w > 2.5:
            side = pts[:3] if rim_side > 0 else pts[3:]
            rims.append(f'<polyline points="{P(side)}"/>')
        kids = 2 if rnd.random() < 0.75 else 3
        for i in range(kids):
            da = rnd.uniform(spread * 0.5, spread * 1.3) * (1 if i % 2 else -1) + rnd.uniform(-8, 8)
            limb(x1, y1, ang + da, L * rnd.uniform(0.62, 0.8), w1, d - 1)
        if rnd.random() < 0.3 and d > 2:
            limb(mx, my, ang + rnd.choice((-1, 1)) * rnd.uniform(50, 75), L * 0.45, w1 * 0.6, d - 2)

    # roots
    roots = (f'<path d="M {x - w0 * 1.6:.1f} {base:.1f} Q {x - w0 * 0.6:.1f} {base - w0 * 0.4:.1f} {x - w0 * 0.5:.1f} {base - w0 * 2:.1f} '
             f'L {x + w0 * 0.5:.1f} {base - w0 * 2:.1f} Q {x + w0 * 0.7:.1f} {base - w0 * 0.4:.1f} {x + w0 * 1.8:.1f} {base:.1f} Z"/>')
    limb(x, base, -90 + lean, h * 0.36, w0, depth)
    out = f'<g fill="{fill}">{roots}' + "".join(segs) + "</g>"
    if rim:
        out += f'<g fill="none" stroke="{rim}" stroke-width="1.6" stroke-linejoin="round" opacity="0.55">' + "".join(rims) + "</g>"
    return out


def tree_row(seed, line, n, hmin, hmax, fill, xmin=-20, xmax=620, depth=5):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        x = rnd.uniform(xmin, xmax)
        y = y_on(line, x)
        if y is None:
            continue
        out.append(gnarly_tree(x, y + 3, rnd.uniform(hmin, hmax), rnd.randrange(9999), fill, depth=depth, lean=rnd.uniform(-10, 10), spread=rnd.uniform(24, 36)))
    return "".join(out)


def hill(pts, seed, base, fill, amp=6, depth=4):
    line = rough(pts, seed, amp, depth)
    poly = line + [(line[-1][0], base), (line[0][0], base)]
    return f'<polygon points="{P(poly)}" fill="{fill}"/>', line


FACES = {
    "classic": [
        [(-0.29, -0.04), (-0.07, -0.04), (-0.17, -0.25)],
        [(0.29, -0.04), (0.07, -0.04), (0.17, -0.25)],
        [(-0.045, 0.08), (0.045, 0.08), (0, 0.0)],
        [(-0.34, 0.1), (-0.22, 0.17), (-0.17, 0.12), (-0.12, 0.18), (0.12, 0.18), (0.17, 0.12), (0.22, 0.17), (0.34, 0.1),
         (0.26, 0.28), (0.09, 0.35), (0.05, 0.29), (-0.01, 0.29), (-0.05, 0.35), (-0.24, 0.29)],
    ],
    "toothy": [
        [(-0.3, -0.02), (-0.06, -0.06), (-0.2, -0.22)],
        [(0.3, -0.02), (0.06, -0.06), (0.2, -0.22)],
        [(-0.04, 0.07), (0.04, 0.07), (0, 0.01)],
        [(-0.3, 0.12), (-0.18, 0.14), (-0.14, 0.2), (-0.1, 0.14), (0.1, 0.14), (0.14, 0.2), (0.18, 0.14), (0.3, 0.12),
         (0.2, 0.3), (0.06, 0.34), (0.03, 0.27), (-0.03, 0.27), (-0.06, 0.34), (-0.2, 0.3)],
    ],
    "sly": [
        [(-0.28, -0.08), (-0.06, -0.02), (-0.08, -0.12)],
        [(0.28, -0.08), (0.06, -0.02), (0.08, -0.12)],
        [(-0.035, 0.08), (0.035, 0.08), (0, 0.02)],
        [(-0.32, 0.06), (-0.16, 0.16), (0.16, 0.16), (0.32, 0.06), (0.2, 0.26), (0, 0.3), (-0.2, 0.26)],
    ],
}


def ell_pts(cx, cy, rx, ry, n=22):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def smile_pts(cx, cy, w, h, n=12):
    top = [(cx - w / 2 + w * i / n, cy + h * 0.35 * math.sin(math.pi * i / n)) for i in range(n + 1)]
    bot = [(cx + w / 2 - w * i / n, cy + h * math.sin(math.pi * i / n)) for i in range(n + 1)]
    return top + bot


FACES["cute"] = [ell_pts(-0.17, -0.1, 0.07, 0.1), ell_pts(0.17, -0.1, 0.07, 0.1), smile_pts(0, 0.1, 0.36, 0.2)]
FACES["boo"] = [ell_pts(-0.16, -0.08, 0.06, 0.11), ell_pts(0.16, -0.08, 0.06, 0.11), ell_pts(0, 0.2, 0.08, 0.1)]


def pumpkin(u, cx, cy, w, h, face=None, lit=True, ribs=5, skin=("#FFB35C", "#F07F28", "#B5461A"), stem=True,
            stem_lean=6, leaf=True, glow_r=None, seed=1, vine=True):
    """Painted pumpkin: shaded ribs, grooves, highlights, speckle; optional carved face with candlelight."""
    rnd = random.Random(seed)
    lt, md, dk = skin
    out = [defs(rg(f"{u}-rib", [(0, lt), (0.5, md), (1, dk)], cx=0.38, cy=0.32, r=0.75),
                lg(f"{u}-shd", [(0, dk, 0), (0.55, dk, 0), (1, "#4A1406", 0.55)]),
                lg(f"{u}-stem", [(0, "#A39A52"), (0.5, "#6E6A2E"), (1, "#3E3416")], 0, 0, 1, 0),
                rg(f"{u}-fire", [(0, "#FFFBE0"), (0.4, "#FFD460"), (1, "#F2861E")], cx=0.5, cy=0.6, r=0.7))]
    if face and lit:
        gr = glow_r or w * 1.05
        out.append(glow(cx, cy, gr, "#FF9A2E", f"{u}-pg", 0.42))
    if ribs == 5:
        spec = [(-0.33, 0.17, 0.44), (0.33, 0.17, 0.44), (-0.18, 0.2, 0.48), (0.18, 0.2, 0.48), (0, 0.22, 0.5)]
    else:
        spec = [(-0.36, 0.14, 0.4), (0.36, 0.14, 0.4), (-0.25, 0.16, 0.45), (0.25, 0.16, 0.45), (-0.12, 0.18, 0.49), (0.12, 0.18, 0.49), (0, 0.19, 0.5)]
    clip = "".join(f'<ellipse cx="{cx + dx * w:.1f}" cy="{cy + (0.5 - ry) * h * 0.25:.1f}" rx="{rx * w:.1f}" ry="{ry * h:.1f}"/>' for dx, rx, ry in spec)
    out.append(defs(f'<clipPath id="{u}-pc">{clip}</clipPath>'))
    for dx, rx, ry in spec:
        out.append(f'<ellipse cx="{cx + dx * w:.1f}" cy="{cy + (0.5 - ry) * h * 0.25:.1f}" rx="{rx * w:.1f}" ry="{ry * h:.1f}" fill="url(#{u}-rib)"/>')
    g = [f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" fill="url(#{u}-shd)"/>']
    # grooves between ribs and soft highlights on each rib
    xs = sorted(dx for dx, _, _ in spec)
    for a, b in zip(xs, xs[1:]):
        bx = cx + (a + b) / 2 * w
        bend = (a + b) / 2 * w * 0.25
        g.append(f'<path d="M {bx:.1f} {cy - h * 0.46:.1f} Q {bx + bend:.1f} {cy:.1f} {bx:.1f} {cy + h * 0.47:.1f}" fill="none" stroke="{dk}" stroke-width="{w * 0.016:.1f}" opacity="0.65" stroke-linecap="round"/>')
    for dx, rx, ry in spec:
        hx = cx + (dx - rx * 0.35) * w
        g.append(f'<path d="M {hx:.1f} {cy - h * 0.3:.1f} Q {hx - rx * w * 0.18:.1f} {cy - h * 0.05:.1f} {hx - rx * w * 0.05:.1f} {cy + h * 0.12:.1f}" fill="none" stroke="#FFE6B8" stroke-width="{w * 0.022:.1f}" stroke-linecap="round" opacity="0.32"/>')
    g.append(dots(int(w * 0.5), seed, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), "#7A2A0A", r=(0.5, 1.4), opacity=(0.15, 0.4)))
    out.append(f'<g clip-path="url(#{u}-pc)">' + "".join(g) + "</g>")
    if face:
        for pts in FACES[face]:
            ab = [(cx + x * w, cy + y * h) for x, y in pts]
            mx = sum(p[0] for p in ab) / len(ab)
            my = sum(p[1] for p in ab) / len(ab)
            out.append(f'<polygon points="{P(ab)}" fill="#5A1E06" stroke="#5A1E06" stroke-width="{w * 0.016:.1f}" stroke-linejoin="round"/>')
            if lit:
                out.append(f'<polygon points="{P(ab)}" fill="#F7C46A"/>')
                inner = [(mx + (x - mx) * 0.84, my + (y - my) * 0.84 + h * 0.014) for x, y in ab]
                out.append(f'<polygon points="{P(inner)}" fill="url(#{u}-fire)"/>')
            else:
                out.append(f'<polygon points="{P(ab)}" fill="#2A0E05"/>')
        if lit:
            # warm light kissing the skin around the face
            out.append(f'<g clip-path="url(#{u}-pc)">' + mist(cx, cy + h * 0.1, w * 0.42, h * 0.32, "#FFC46A", f"{u}-fk", 0.22) + "</g>")
    if stem:
        sw = w * 0.085
        sh = h * 0.24
        ty = cy - h * 0.47
        L = stem_lean
        out.append(f'<ellipse cx="{cx:.1f}" cy="{ty + 2:.1f}" rx="{sw * 0.9:.1f}" ry="{sw * 0.3:.1f}" fill="#5A4A1E"/>')
        out.append(f'<path d="M {cx - sw / 2:.1f} {ty + 2:.1f} C {cx - sw * 0.45:.1f} {ty - sh * 0.5:.1f} {cx - sw * 0.2 + L:.1f} {ty - sh:.1f} {cx + L:.1f} {ty - sh:.1f} '
                   f'L {cx + sw * 0.55 + L:.1f} {ty - sh * 0.92:.1f} C {cx + sw * 0.35 + L * 0.5:.1f} {ty - sh * 0.5:.1f} {cx + sw * 0.5:.1f} {ty - sh * 0.2:.1f} {cx + sw * 0.62:.1f} {ty + 2:.1f} Z" fill="url(#{u}-stem)"/>')
        out.append(f'<path d="M {cx - sw * 0.1:.1f} {ty:.1f} Q {cx + L * 0.4:.1f} {ty - sh * 0.5:.1f} {cx + sw * 0.18 + L:.1f} {ty - sh * 0.9:.1f}" fill="none" stroke="#C9C07A" stroke-width="{max(1.5, sw * 0.12):.1f}" opacity="0.6" stroke-linecap="round"/>')
        out.append(f'<ellipse cx="{cx + sw * 0.28 + L:.1f}" cy="{ty - sh * 0.96:.1f}" rx="{sw * 0.34:.1f}" ry="{sw * 0.14:.1f}" fill="#D6CB8E" transform="rotate(14 {cx + sw * 0.28 + L:.1f} {ty - sh * 0.96:.1f})"/>')
        if vine:
            vx, vy = cx + sw * 0.6, ty + 1
            out.append(f'<path d="M {vx:.1f} {vy:.1f} q {w * 0.08:.1f} {-h * 0.02:.1f} {w * 0.12:.1f} {-h * 0.1:.1f} q {w * 0.03:.1f} {-h * 0.08:.1f} {-w * 0.02:.1f} {-h * 0.07:.1f} q {-w * 0.03:.1f} {h * 0.02:.1f} {0:.1f} {h * 0.05:.1f}" fill="none" stroke="#5E7A2E" stroke-width="{max(1.6, w * 0.011):.1f}" stroke-linecap="round"/>')
        if leaf:
            lx, ly = cx - sw * 0.6, ty - 1
            s = w * 0.16
            out.append(defs(lg(f"{u}-lf", [(0, "#8FAE4A"), (1, "#3E5E22")], 0, 0, 1, 1)))
            out.append(f'<path d="M {lx:.1f} {ly:.1f} C {lx - s * 0.4:.1f} {ly - s * 0.55:.1f} {lx - s * 0.95:.1f} {ly - s * 0.5:.1f} {lx - s * 1.1:.1f} {ly - s * 0.2:.1f} '
                       f'C {lx - s * 0.9:.1f} {ly + s * 0.05:.1f} {lx - s * 0.4:.1f} {ly + s * 0.15:.1f} {lx:.1f} {ly:.1f} Z" fill="url(#{u}-lf)"/>'
                       f'<path d="M {lx:.1f} {ly:.1f} Q {lx - s * 0.5:.1f} {ly - s * 0.22:.1f} {lx - s * 1.02:.1f} {ly - s * 0.2:.1f}" fill="none" stroke="#C7D98A" stroke-width="1.5" opacity="0.7"/>')
    return "".join(out)


def ghost(u, cx, top, w, lean=0.0, face="happy", arms=True, glow_op=0.25, body=("#FFFFFF", "#F4EDF8", "#B6A6D4"), blush=True, flip=False):
    """Painted sheet ghost: luminous dome, lilac shade side, wavy drifting hem."""
    k = w / 100
    L = lean * 30
    path = (f"M -40 22 C -42 -14 -24 -50 0 -50 C 24 -50 42 -14 40 22 L {44 + L:.1f} 72 Q {36 + L:.1f} 64 {28 + L:.1f} 76 "
            f"Q {18 + L:.1f} 62 {8 + L:.1f} 78 Q {-2 + L:.1f} 64 {-12 + L:.1f} 78 Q {-22 + L:.1f} 64 {-32 + L:.1f} 76 Q {-40 + L:.1f} 66 {-46 + L:.1f} 74 Z")
    sx = -k if flip else k
    out = [defs(rg(f"{u}-gb", [(0, body[0]), (0.55, body[1]), (1, body[2])], cx=0.38, cy=0.3, r=0.8),
                f'<clipPath id="{u}-gc"><path d="{path}"/></clipPath>')]
    if glow_op:
        out.append(glow(cx, top + 50 * k, 95 * k, "#E8E0FF", f"{u}-gg", glow_op))
    out.append(f'<g transform="translate({cx:.1f} {top + 50 * k:.1f}) scale({sx:.3f} {k:.3f})">')
    if arms:
        out.append(f'<path d="M -36 10 C -48 8 -56 0 -58 -10 C -59 -16 -52 -18 -48 -13 C -44 -8 -40 -6 -36 -6 Z" fill="{body[1]}"/>'
                   f'<path d="M 36 12 C 48 14 56 8 60 0 C 62 -6 56 -9 52 -5 C 48 -1 42 0 36 -2 Z" fill="{body[2]}"/>')
    out.append(f'<path d="{path}" fill="url(#{u}-gb)"/>')
    out.append(f'<g clip-path="url(#{u}-gc)"><path d="M 26 -46 C 48 -10 46 40 {52 + L:.1f} 80 L 70 80 L 70 -60 Z" fill="{body[2]}" opacity="0.45"/>'
               f'<path d="M -30 60 Q 0 50 {30 + L:.1f} 64" fill="none" stroke="{body[2]}" stroke-width="6" opacity="0.35"/>'
               f'<path d="M -18 -2 Q -10 30 -16 66" fill="none" stroke="{body[2]}" stroke-width="3" opacity="0.3"/></g>')
    out.append('<ellipse cx="-16" cy="-34" rx="12" ry="7" transform="rotate(-30 -16 -34)" fill="#FFFFFF" opacity="0.85"/>')
    if face == "happy":
        out.append('<ellipse cx="-13" cy="-14" rx="5.2" ry="7.2" fill="#2A1E36"/><ellipse cx="13" cy="-14" rx="5.2" ry="7.2" fill="#2A1E36"/>'
                   '<circle cx="-11.5" cy="-16.5" r="1.8" fill="#FFF"/><circle cx="14.5" cy="-16.5" r="1.8" fill="#FFF"/>'
                   '<path d="M -6 0 Q 0 6 6 0" fill="none" stroke="#2A1E36" stroke-width="2.6" stroke-linecap="round"/>')
    elif face == "boo":
        out.append('<ellipse cx="-13" cy="-16" rx="5.2" ry="7.2" fill="#2A1E36"/><ellipse cx="13" cy="-16" rx="5.2" ry="7.2" fill="#2A1E36"/>'
                   '<circle cx="-11.5" cy="-18.5" r="1.8" fill="#FFF"/><circle cx="14.5" cy="-18.5" r="1.8" fill="#FFF"/>'
                   '<ellipse cx="0" cy="4" rx="6" ry="8" fill="#2A1E36"/><ellipse cx="0" cy="7" rx="3.4" ry="3.6" fill="#C2577A"/>')
    elif face == "sleepy":
        out.append('<path d="M -18 -14 Q -13 -9 -8 -14 M 8 -14 Q 13 -9 18 -14" fill="none" stroke="#2A1E36" stroke-width="2.6" stroke-linecap="round"/>'
                   '<path d="M -4 0 Q 0 3 4 0" fill="none" stroke="#2A1E36" stroke-width="2.2" stroke-linecap="round"/>')
    if blush and face:
        out.append('<ellipse cx="-22" cy="-4" rx="6" ry="3.4" fill="#F29AB4" opacity="0.6"/><ellipse cx="22" cy="-4" rx="6" ry="3.4" fill="#F29AB4" opacity="0.6"/>')
    out.append("</g>")
    return "".join(out)


def lantern(u, x, top, s=1.0, frame="#22181A", flame=True, glow_r=70, glow_op=0.55, handle=True):
    """Iron candle lantern; (x, top) is the top of the handle ring. 1.0 ~ 44 x 76 px."""
    out = [defs(rg(f"{u}-lg", [(0, "#FFF6CE"), (0.45, "#FFC75A"), (1, "#E07A22")], cx=0.5, cy=0.62, r=0.7))]
    gy = top + 44 * s
    out.append(glow(x, gy, glow_r * s, "#FFB547", f"{u}-lh", glow_op))
    out.append(f'<g transform="translate({x:.1f} {top:.1f}) scale({s:.3f})">')
    if handle:
        out.append(f'<circle cx="0" cy="6" r="6" fill="none" stroke="{frame}" stroke-width="3"/>')
    out.append(f'<path d="M -10 12 L 10 12 L 18 22 L -18 22 Z" fill="{frame}"/><rect x="-20" y="21" width="40" height="4" rx="1.5" fill="{frame}"/>'
               f'<rect x="-16" y="25" width="32" height="40" fill="url(#{u}-lg)"/>'
               f'<rect x="-5" y="46" width="10" height="17" rx="1.5" fill="#FFF4DC"/><rect x="1" y="46" width="4" height="17" fill="#E9D3A8"/>')
    if flame:
        out.append('<path d="M 0 32 Q 5 40 3.5 44 Q 0 47 -3.5 44 Q -5 40 0 32 Z" fill="#FFFFFF"/>')
    out.append(f'<g fill="{frame}"><rect x="-17" y="25" width="3" height="40"/><rect x="14" y="25" width="3" height="40"/><rect x="-1.2" y="25" width="2.4" height="40" opacity="0.8"/>'
               f'<rect x="-17" y="43" width="34" height="2" opacity="0.7"/><path d="M -21 65 L 21 65 L 17 74 L -17 74 Z"/></g>'
               '<path d="M -12 28 L -12 60" stroke="#FFFFFF" stroke-width="2" opacity="0.45"/></g>')
    return "".join(out)


def candle(u, x, base, h, w, wax=("#FFF6E2", "#EADBBE", "#BFA582"), lit=True, glow_r=None, drips=3, seed=1):
    rnd = random.Random(seed)
    top = base - h
    out = [defs(lg(f"{u}-cw", [(0, wax[0]), (0.55, wax[1]), (1, wax[2])], 0, 0, 1, 0),
                rg(f"{u}-cf", [(0, "#FFFFFF"), (0.35, "#FFF1A8"), (0.75, "#FFB13A"), (1, "#F07A1A", 0)], cx=0.5, cy=0.7, r=0.6))]
    if lit:
        out.append(glow(x, top - w * 0.6, glow_r or w * 4, "#FFC45A", f"{u}-cg", 0.55))
    out.append(f'<rect x="{x - w / 2:.1f}" y="{top:.1f}" width="{w:.1f}" height="{h:.1f}" fill="url(#{u}-cw)"/>')
    out.append(f'<ellipse cx="{x:.1f}" cy="{top:.1f}" rx="{w / 2:.1f}" ry="{w * 0.16:.1f}" fill="{wax[0]}"/>')
    for i in range(drips):
        dx = x - w / 2 + w * (i + 0.5) / drips + rnd.uniform(-2, 2)
        L = rnd.uniform(0.12, 0.4) * h
        dw = w * rnd.uniform(0.12, 0.2)
        out.append(f'<path d="M {dx - dw:.1f} {top:.1f} L {dx - dw:.1f} {top + L:.1f} A {dw:.1f} {dw:.1f} 0 0 0 {dx + dw:.1f} {top + L:.1f} L {dx + dw:.1f} {top:.1f} Z" fill="{wax[0]}"/>')
    out.append(f'<line x1="{x:.1f}" y1="{top:.1f}" x2="{x:.1f}" y2="{top - w * 0.3:.1f}" stroke="#2A1E16" stroke-width="{max(1.5, w * 0.06):.1f}" stroke-linecap="round"/>')
    if lit:
        fh = w * 1.1
        fy = top - w * 0.25
        out.append(f'<path d="M {x:.1f} {fy - fh:.1f} Q {x + w * 0.42:.1f} {fy - fh * 0.35:.1f} {x + w * 0.2:.1f} {fy - fh * 0.08:.1f} Q {x:.1f} {fy + fh * 0.06:.1f} {x - w * 0.2:.1f} {fy - fh * 0.08:.1f} Q {x - w * 0.42:.1f} {fy - fh * 0.35:.1f} {x:.1f} {fy - fh:.1f} Z" fill="url(#{u}-cf)"/>')
        out.append(f'<ellipse cx="{x:.1f}" cy="{fy - fh * 0.22:.1f}" rx="{w * 0.08:.1f}" ry="{fh * 0.14:.1f}" fill="#7A9AE0" opacity="0.6"/>')
    return "".join(out)


def falling_leaf(x, y, s, rot, col, vein="#FFE2B0"):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s / 20:.3f})">'
            f'<path d="M 0 -20 C 10 -12 12 4 0 20 C -12 4 -10 -12 0 -20 Z" fill="{col}"/>'
            f'<path d="M 0 -16 L 0 24 M 0 -4 L 6 -10 M 0 4 L -6 -2 M 0 10 L 6 4" stroke="{vein}" stroke-width="1.6" opacity="0.6" fill="none"/></g>')


def maple_leaf(x, y, s, rot, col, vein="#FFD7A0"):
    pts = [(0, -1.0), (0.12, -0.62), (0.32, -0.74), (0.28, -0.40), (0.62, -0.60), (0.56, -0.30), (0.96, -0.32),
           (0.78, -0.08), (0.92, 0.06), (0.50, 0.22), (0.56, 0.42), (0.18, 0.32), (0.05, 0.46)]
    full = pts + [(-a, b) for a, b in reversed(pts[1:])]
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<polygon points="{P(full)}" fill="{col}"/><polygon points="{P([(0, -1.0)] + pts[1:] + [(0, 0.46)])}" fill="#000" opacity="0.14"/>'
            f'<path d="M 0 0.4 L 0 -0.85 M 0 0.3 L 0.8 -0.28 M 0 0.3 L -0.8 -0.28 M 0 0.6 L 0 1" stroke="{vein}" stroke-width="{2 / s:.3f}" opacity="0.6" fill="none"/></g>')


def ground_glow(cx, cy, rx, ry, color, uid, op=0.5):
    return mist(cx, cy, rx, ry, color, uid, op)


# ================================================================ designs
def d_boo():
    u = "hwboo"
    out = [bg(u, [(0, "#0D1230"), (0.45, "#24204E"), (0.8, "#3A2D62"), (1, "#2A2048")])]
    out.append(starfield(1, 70, (0, 0, 600, 300), avoid=(410, 150, 120)))
    out.append(moon(u, 410, 150, 74, halo_r=2.6, halo_op=0.45))
    out.append(cloud_wisp(380, 186, 190, "#8E7CB8", 0.45, 2) + cloud_wisp(480, 118, 120, "#8E7CB8", 0.3, 5))
    # far forest, hazy
    poly, far = hill([(-20, 380), (150, 368), (320, 378), (480, 366), (620, 376)], 2, 600, "#3E3468")
    out.append(tree_row(11, far, 16, 70, 130, "#3E3468", depth=5))
    out.append(poly)
    out.append(mist(300, 380, 420, 46, "#A898D0", f"{u}-m1", 0.45))
    # middle forest
    poly, midl = hill([(-20, 420), (180, 410), (400, 418), (620, 406)], 4, 600, "#271F44")
    out.append(tree_row(12, midl, 9, 120, 190, "#271F44", depth=6))
    out.append(poly)
    out.append(mist(300, 430, 380, 36, "#B8A8E0", f"{u}-m2", 0.35))
    # big framing tree on the left, rim-lit by the moon
    out.append(gnarly_tree(70, 470, 420, 77, "#120D1E", depth=7, lean=12, spread=30, w0=34, rim="#C8B8F0", rim_side=1))
    out.append(gnarly_tree(560, 470, 300, 21, "#120D1E", depth=6, lean=-14, spread=28, w0=24))
    # ground with glowing mushrooms and fallen leaves
    poly, gl = hill([(-20, 452), (200, 444), (420, 452), (620, 444)], 8, 600, "#160F24")
    out.append(poly)
    out.append(grass(120, 3, (-10, 440, 610, 470), ["#2E2448", "#3A2E58", "#221A36"], h=(6, 16), sw=2))
    for mx, my, s in ((176, 452, 1.0), (192, 455, 0.7), (458, 450, 0.85)):
        out.append(glow(mx, my - 8 * s, 26 * s, SLIME, f"{u}-sh{mx}", 0.5))
        out.append(f'<rect x="{mx - 2 * s:.1f}" y="{my - 12 * s:.1f}" width="{4 * s:.1f}" height="{12 * s:.1f}" fill="#E8F2C8"/>'
                   f'<path d="M {mx - 10 * s:.1f} {my - 11 * s:.1f} Q {mx:.1f} {my - 26 * s:.1f} {mx + 10 * s:.1f} {my - 11 * s:.1f} Z" fill="{SLIME}"/>'
                   f'<circle cx="{mx - 3 * s:.1f}" cy="{my - 17 * s:.1f}" r="{1.6 * s:.1f}" fill="#F4FFD8"/>')
    # the ghost and its swinging lantern
    out.append(mist(300, 438, 90, 12, "#D8CCFF", f"{u}-gs", 0.35))
    out.append(ghost(u, 292, 150, 190, lean=0.25, face="boo", glow_op=0.3))
    out.append(f'<path d="M 406 246 Q 403 262 404 282" stroke="#22181A" stroke-width="2.4" fill="none"/>')
    out.append(lantern(u, 404, 278, 0.82, glow_r=90, glow_op=0.6))
    # warm lantern light on the ghost's right side
    out.append(mist(372, 290, 40, 60, "#FFC46A", f"{u}-wl", 0.25))
    out.append(bat(214, 116, 26, "#160F22", rim="#C8B8F0", rot=-8, flap=6))
    out.append(bat(500, 92, 18, "#160F22", rim="#C8B8F0", rot=10, flap=-4))
    out.append(bat(358, 70, 14, "#160F22", rot=-4, flap=10))
    out.append(vignette(u, strength=0.55))
    out.append(word(300, 548, "BOO!", BEBAS, 150, BONE, max_w=420, ls=14, glow_col=LILAC, glow_op=0.4, shadow="#0A0614", sdy=6))
    return "\n".join(out)


def haunted_house(u, cx, base, s, body="#1A1226", rim="#E8D6A8", lit=("#FFD27A", "#FFB547", "#FFE6A0"), seed=4):
    """Victorian mansion silhouette: tower with witch-hat roof, mansard main block, gabled wing, porch, chimneys."""
    rnd = random.Random(seed)
    k = s
    X = lambda v: cx + v * k
    Y = lambda v: base - v * k
    parts = []
    # tower
    parts.append([(X(-70), Y(0)), (X(-70), Y(190)), (X(-82), Y(196)), (X(-46), Y(296)), (X(-10), Y(196)), (X(-22), Y(190)), (X(-22), Y(0))])
    # main block with mansard roof
    parts.append([(X(-30), Y(0)), (X(-30), Y(140)), (X(-38), Y(144)), (X(-24), Y(186)), (X(60), Y(186)), (X(74), Y(144)), (X(66), Y(140)), (X(66), Y(0))])
    # gabled wing on the right
    parts.append([(X(60), Y(0)), (X(60), Y(104)), (X(54), Y(104)), (X(98), Y(158)), (X(142), Y(104)), (X(136), Y(104)), (X(136), Y(0))])
    # porch roof and chimneys
    parts.append([(X(-34), Y(54)), (X(70), Y(54)), (X(78), Y(44)), (X(-40), Y(44))])
    parts.append([(X(30), Y(186)), (X(30), Y(214)), (X(44), Y(214)), (X(44), Y(186))])
    parts.append([(X(112), Y(130)), (X(112), Y(170)), (X(124), Y(170)), (X(124), Y(116))])
    out = [f'<g fill="{body}">' + "".join(f'<polygon points="{P(p)}"/>' for p in parts)
           + f'<rect x="{X(-34):.1f}" y="{Y(44):.1f}" width="{4 * k:.1f}" height="{44 * k:.1f}"/><rect x="{X(66):.1f}" y="{Y(44):.1f}" width="{4 * k:.1f}" height="{44 * k:.1f}"/>'
           + f'<rect x="{X(16):.1f}" y="{Y(44):.1f}" width="{4 * k:.1f}" height="{44 * k:.1f}"/></g>']
    # spire and finial
    out.append(f'<line x1="{X(-46):.1f}" y1="{Y(296):.1f}" x2="{X(-46):.1f}" y2="{Y(322):.1f}" stroke="{body}" stroke-width="{2.4 * k:.1f}"/><circle cx="{X(-46):.1f}" cy="{Y(312):.1f}" r="{3 * k:.1f}" fill="{body}"/>')
    # moonlit edges (moon behind-left)
    out.append(f'<g fill="none" stroke="{rim}" stroke-width="{1.8:.1f}" opacity="0.7" stroke-linejoin="round">'
               f'<polyline points="{P([(X(-82), Y(196)), (X(-46), Y(296))])}"/><polyline points="{P([(X(-38), Y(144)), (X(-24), Y(186)), (X(60), Y(186))])}"/>'
               f'<polyline points="{P([(X(54), Y(104)), (X(98), Y(158))])}"/><line x1="{X(-70):.1f}" y1="{Y(190):.1f}" x2="{X(-70):.1f}" y2="{Y(60):.1f}"/></g>')
    # trims: roof shingles hint, eaves
    out.append(f'<g stroke="#000" stroke-width="1.2" opacity="0.35">' + "".join(
        f'<line x1="{X(-32 + i * 0.3):.1f}" y1="{Y(150 + i):.1f}" x2="{X(68 - i * 0.3):.1f}" y2="{Y(150 + i):.1f}"/>' for i in range(0, 36, 8)) + "</g>")
    # windows: (x, y, w, h, arched)
    wins = [(-56, 120, 20, 30, True), (-56, 64, 20, 30, True), (-16, 90, 18, 28, False), (16, 90, 18, 28, False), (44, 90, 14, 28, False),
            (-4, 150, 14, 18, True), (30, 150, 14, 18, True), (80, 60, 16, 26, False), (108, 60, 16, 26, False), (92, 112, 12, 16, True),
            (-16, 12, 14, 24, False), (44, 12, 14, 24, False)]
    for i, (wx, wy, ww, wh, arch) in enumerate(wins):
        on = rnd.random() < 0.72
        col = rnd.choice(lit) if on else "#2E2440"
        x0, y0 = X(wx), Y(wy + wh)
        W, H = ww * k, wh * k
        if on:
            out.append(glow(x0 + W / 2, y0 + H / 2, max(W, H) * 1.3, "#FFB547", f"{u}-w{i}", 0.45))
        if arch:
            out.append(f'<path d="M {x0:.1f} {y0 + H:.1f} L {x0:.1f} {y0 + W / 2:.1f} A {W / 2:.1f} {W / 2:.1f} 0 0 1 {x0 + W:.1f} {y0 + W / 2:.1f} L {x0 + W:.1f} {y0 + H:.1f} Z" fill="{col}"/>')
        else:
            out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{W:.1f}" height="{H:.1f}" fill="{col}"/>')
        out.append(f'<g stroke="{body}" stroke-width="{max(1.2, 1.6 * k):.1f}"><line x1="{x0 + W / 2:.1f}" y1="{y0 + W * 0.2:.1f}" x2="{x0 + W / 2:.1f}" y2="{y0 + H:.1f}"/><line x1="{x0:.1f}" y1="{y0 + H * 0.55:.1f}" x2="{x0 + W:.1f}" y2="{y0 + H * 0.55:.1f}"/></g>')
        out.append(f'<rect x="{x0 - 2 * k:.1f}" y="{y0 + H:.1f}" width="{W + 4 * k:.1f}" height="{2.4 * k:.1f}" fill="{body}"/>')
    # front door, a little open
    dx0, dy0 = X(10), Y(36)
    out.append(glow(dx0 + 6 * k, dy0 + 18 * k, 34 * k, "#FFB547", f"{u}-dr", 0.5))
    out.append(f'<path d="M {dx0:.1f} {Y(0):.1f} L {dx0:.1f} {dy0 + 6 * k:.1f} A {7 * k:.1f} {7 * k:.1f} 0 0 1 {dx0 + 14 * k:.1f} {dy0 + 6 * k:.1f} L {dx0 + 14 * k:.1f} {Y(0):.1f} Z" fill="#FFC864"/>')
    out.append(f'<path d="M {dx0:.1f} {Y(0):.1f} L {dx0:.1f} {dy0 + 6 * k:.1f} L {dx0 + 8 * k:.1f} {dy0 + 9 * k:.1f} L {dx0 + 8 * k:.1f} {Y(0) + 1:.1f} Z" fill="{body}"/>')
    return "".join(out)


def d_spooky_season():
    u = "hwss"
    out = [bg(u, [(0, "#120E2C"), (0.4, "#2E1F52"), (0.7, "#5A2F6E"), (1, "#7A3A6A")])]
    out.append(starfield(2, 90, (0, 0, 600, 360), avoid=(300, 222, 175)))
    out.append(moon(u, 300, 222, 150, halo_r=1.75, halo_op=0.55, seed=7))
    out.append(cloud_wisp(196, 300, 220, "#A88EC8", 0.55, 3) + cloud_wisp(430, 158, 170, "#A88EC8", 0.4, 8) + cloud_wisp(470, 318, 120, "#C9A8D0", 0.35, 9))
    # bats spilling out of the tower
    rnd = random.Random(5)
    for i in range(9):
        t = i / 8
        bx = 236 - 140 * t + rnd.uniform(-14, 14)
        by = 120 - 50 * math.sin(t * 2.6) + rnd.uniform(-10, 10)
        out.append(bat(bx, by, 10 + 12 * t, "#160E22", rot=rnd.uniform(-20, 20), flap=rnd.uniform(-10, 14)))
    # distant hills
    poly, _ = hill([(-20, 400), (120, 384), (260, 398), (420, 380), (620, 394)], 3, 600, "#3A2450")
    out.append(poly)
    out.append(mist(300, 404, 400, 40, "#C49ACF", f"{u}-m1", 0.35))
    # the hill and the house
    poly, hl = hill([(-20, 470), (120, 420), (240, 386), (330, 380), (420, 394), (520, 430), (620, 452)], 6, 600, "#140E20", amp=4)
    out.append(haunted_house(u, 296, 392, 0.98))
    out.append(poly)
    # winding path with lanterns
    out.append(f'<path d="M 310 392 C 300 420 350 430 330 456 C 314 476 260 486 250 520 L 300 520 C 304 490 360 478 368 456 C 382 428 322 418 322 392 Z" fill="#3A2C3A"/>')
    out.append(f'<path d="M 310 392 C 300 420 350 430 330 456 C 314 476 260 486 250 520" fill="none" stroke="#6A5060" stroke-width="2" opacity="0.6"/>')
    for i, (lx, ly) in enumerate(((356, 430), (296, 474), (390, 466))):
        out.append(f'<line x1="{lx}" y1="{ly}" x2="{lx}" y2="{ly - 26}" stroke="#0E0A14" stroke-width="2.4"/>')
        out.append(glow(lx, ly - 30, 22, "#FFB547", f"{u}-pl{i}", 0.7) + f'<circle cx="{lx}" cy="{ly - 30}" r="3.4" fill="#FFE7A3"/>')
    # wrought iron fence along the brow
    fence = []
    for fx in range(120, 260, 11):
        fy = y_on(hl, fx) or 420
        fence.append(f'<line x1="{fx}" y1="{fy + 2:.1f}" x2="{fx}" y2="{fy - 24:.1f}"/><path d="M {fx - 3} {fy - 22:.1f} L {fx} {fy - 30:.1f} L {fx + 3} {fy - 22:.1f} Z" fill="#0E0A14"/>')
    out.append(f'<g stroke="#0E0A14" stroke-width="2.2">' + "".join(fence) + f'<path d="M 118 {(y_on(hl, 118) or 430) - 18:.1f} L 256 {(y_on(hl, 256) or 390) - 18:.1f}" fill="none"/></g>')
    # gnarled tree on the right, a crow
    out.append(gnarly_tree(556, 452, 230, 31, "#0E0A14", depth=6, lean=-18, spread=30, w0=18, rim="#E8D6A8", rim_side=-1))
    out.append(grass(140, 9, (-10, 420, 610, 470), ["#2A1E36", "#1E1628", "#3A2A44"], h=(6, 18), sw=2))
    out.append(pumpkin(u + "p1", 92, 462, 50, 36, face="classic", seed=3, leaf=False, vine=False, glow_r=64))
    out.append(pumpkin(u + "p2", 516, 470, 34, 25, face="cute", seed=4, leaf=False, vine=False, glow_r=44))
    # foreground band for type
    out.append(defs(lg(f"{u}-fg", [(0, "#0E0A14", 0), (0.35, "#0E0A14", 0.85), (1, "#0A0710", 1)])))
    out.append(f'<rect x="0" y="440" width="600" height="160" fill="url(#{u}-fg)"/>')
    out.append(vignette(u, strength=0.5))
    out.append(word(300, 486, "spooky", SERIF_IT, 86, BONE, max_w=420, glow_col="#E8B0FF", glow_op=0.25, shadow="#000", sdy=4))
    out.append(word(300, 546, "SEASON", BEBAS, 52, ORANGE, max_w=420, ls=18, glow_col=ORANGE, glow_op=0.2))
    return "\n".join(out)


def d_happy_halloween():
    u = "hwhh"
    out = [bg(u, [(0, "#1A0E1E"), (0.5, "#24122A"), (1, "#120A12")])]
    out.append(glow(300, 330, 330, "#FF8A2A", f"{u}-amb", 0.38))
    out.append(starfield(3, 40, (0, 0, 600, 200), col="#F8D9A8", tw=3, avoid=(300, 110, 110)))
    # wooden plank shelf / porch boards
    out.append(defs(lg(f"{u}-wd", [(0, "#6A3A22"), (1, "#2A140C")])))
    out.append(f'<rect x="0" y="420" width="600" height="180" fill="url(#{u}-wd)"/>')
    out.append('<g stroke="#1A0C06" stroke-width="2.4" opacity="0.7">' + "".join(f'<line x1="0" y1="{y}" x2="600" y2="{y}"/>' for y in (420, 462, 512, 570)) + "</g>")
    out.append('<g stroke="#A0603A" stroke-width="1.4" opacity="0.35" fill="none">' + "".join(
        f'<path d="M {x} {y} q 40 -3 80 0 t 80 0"/>' for x, y in ((20, 440), (240, 446), (420, 438), (80, 488), (330, 494), (150, 540), (400, 548))) + "</g>")
    out.append(ground_glow(300, 440, 260, 50, "#FFB04A", f"{u}-gl", 0.55))
    # candles and little gourds keeping the jack company
    out.append(candle(u + "c1", 110, 440, 70, 22, seed=2, glow_r=70))
    out.append(candle(u + "c2", 140, 446, 44, 18, seed=5, glow_r=50))
    out.append(candle(u + "c3", 474, 446, 58, 20, seed=8, glow_r=60))
    out.append(pumpkin(u + "g1", 526, 436, 64, 42, skin=("#F6E6C8", "#E0CCA8", "#A89070"), seed=9, leaf=False, stem_lean=4))
    # the hero jack-o'-lantern
    out.append(pumpkin(u + "pk", 300, 330, 330, 238, face="classic", seed=1, stem_lean=10, glow_r=300))
    out.append(f'<ellipse cx="300" cy="446" rx="160" ry="10" fill="#000" opacity="0.35"/>')
    # leaves on the boards and one falling
    for x, y, s, r, c in ((60, 456, 22, -30, "#C2531B"), (548, 470, 20, 40, "#D9A23B"), (88, 446, 14, 70, "#8A2A1A"), (392, 452, 13, -60, "#D9A23B")):
        out.append(maple_leaf(x, y, s, r, c))
    out.append(maple_leaf(498, 196, 18, 25, "#E07A2A"))
    out.append('<path d="M 486 176 q -14 -10 -6 -24" fill="none" stroke="#E8C08A" stroke-width="1.6" stroke-dasharray="2 6" opacity="0.6"/>')
    out.append(bat(124, 132, 28, "#120A12", rim="#FFB04A", rot=-10, flap=8))
    out.append(vignette(u, strength=0.6))
    out.append(arc_word("HAPPY", 300, 262, 158, BEBAS, 58, BONE, ls=12, uid=f"{u}-arc"))
    out.append(word(300, 548, "Halloween", SERIF_IT, 92, AMBER, max_w=440, glow_col="#FF8A2A", glow_op=0.35, shadow="#1A0A04", sdy=5))
    return "\n".join(out)


def kid(x, base, h, kind, fill="#120C16", rim="#FFC46A"):
    """Trick-or-treater seen from behind, backlit: kind = 'ghost' | 'witch' | 'cat'."""
    k = h / 100
    out = [f'<g transform="translate({x:.1f} {base:.1f}) scale({k:.3f})">']
    if kind == "ghost":
        out.append(f'<path d="M -22 -62 C -24 -86 -14 -100 0 -100 C 14 -100 24 -86 22 -62 L 28 -8 Q 20 -14 14 -6 Q 6 -14 0 -6 Q -8 -14 -14 -6 Q -20 -14 -28 -8 Z" fill="{fill}"/>'
                   f'<rect x="-12" y="-8" width="8" height="8" fill="{fill}"/><rect x="4" y="-8" width="8" height="8" fill="{fill}"/>'
                   f'<path d="M -22 -62 C -24 -86 -14 -100 0 -100" fill="none" stroke="{rim}" stroke-width="3" opacity="0.8"/>'
                   f'<path d="M -22 -60 L -28 -8" fill="none" stroke="{rim}" stroke-width="2.4" opacity="0.6"/>')
        out.append(f'<path d="M -26 -50 Q -40 -40 -36 -26" fill="none" stroke="{fill}" stroke-width="7" stroke-linecap="round"/>')
        out.append(f'<path d="M -48 -26 L -24 -26 L -27 -6 L -45 -6 Z" fill="{ORANGE}"/><path d="M -48 -26 Q -36 -40 -24 -26" fill="none" stroke="{fill}" stroke-width="2.4"/>'
                   f'<path d="M -48 -26 L -45 -6" stroke="#FFD9A0" stroke-width="2.4"/>')
    elif kind == "witch":
        out.append(f'<path d="M -16 -70 L 16 -70 L 22 -28 L 26 -6 L -26 -6 L -22 -28 Z" fill="{fill}"/>'
                   f'<circle cx="0" cy="-78" r="11" fill="{fill}"/>'
                   f'<ellipse cx="0" cy="-86" rx="24" ry="5" fill="{fill}"/><path d="M -12 -88 L 4 -126 L 10 -118 L 12 -88 Z" fill="{fill}"/>'
                   f'<rect x="-12" y="-6" width="8" height="6" fill="{fill}"/><rect x="4" y="-6" width="8" height="6" fill="{fill}"/>'
                   f'<path d="M -24 -86 L 24 -86 M -12 -88 L 4 -126" fill="none" stroke="{rim}" stroke-width="2.4" opacity="0.8"/>'
                   f'<path d="M -16 -70 L -26 -6" fill="none" stroke="{rim}" stroke-width="2.4" opacity="0.6"/>')
        out.append(f'<path d="M 18 -52 Q 34 -40 30 -24" fill="none" stroke="{fill}" stroke-width="7" stroke-linecap="round"/>'
                   f'<path d="M 20 -24 L 44 -24 L 41 -4 L 23 -4 Z" fill="{PLUM}"/><path d="M 20 -24 Q 32 -38 44 -24" fill="none" stroke="{fill}" stroke-width="2.4"/>'
                   f'<path d="M 44 -24 L 41 -4" stroke="#FFD9A0" stroke-width="2.4"/>')
    else:  # cat costume
        out.append(f'<path d="M -16 -64 L 16 -64 L 20 -8 L -20 -8 Z" fill="{fill}"/><circle cx="0" cy="-74" r="13" fill="{fill}"/>'
                   f'<path d="M -12 -82 L -10 -96 L -2 -86 Z M 12 -82 L 10 -96 L 2 -86 Z" fill="{fill}"/>'
                   f'<rect x="-11" y="-8" width="8" height="8" fill="{fill}"/><rect x="3" y="-8" width="8" height="8" fill="{fill}"/>'
                   f'<path d="M 16 -20 Q 34 -18 30 -40 Q 28 -50 36 -52" fill="none" stroke="{fill}" stroke-width="4" stroke-linecap="round"/>'
                   f'<path d="M -12 -84 L -10 -96 M -13 -74 A 13 13 0 0 1 -6 -86 M -16 -62 L -20 -8" fill="none" stroke="{rim}" stroke-width="2.2" opacity="0.75"/>')
    out.append("</g>")
    return "".join(out)


def d_trick_or_treat():
    u = "hwtt"
    out = [bg(u, [(0, "#0F0C26"), (0.6, "#2A1C46"), (1, "#3A2450")])]
    out.append(starfield(4, 50, (0, 0, 600, 200), tw=5))
    out.append(moon(u, 534, 66, 24, halo_r=2.8, halo_op=0.4, seed=4))
    # house facade with clapboard siding
    out.append(defs(lg(f"{u}-sd", [(0, "#4A3E6A"), (1, "#2A2244")], 0, 0, 1, 0),
                    lg(f"{u}-pr", [(0, "#6E4A3A"), (1, "#3A241C")]),
                    lg(f"{u}-dl", [(0, "#FFF2C6"), (0.6, "#FFC560"), (1, "#E8892A")], 0, 0, 1, 0)))
    out.append(f'<polygon points="20,600 20,190 300,120 580,190 580,600" fill="url(#{u}-sd)"/>')
    out.append(f'<polygon points="0,196 300,110 600,196 600,212 300,128 0,212" fill="#1A1428"/>')
    out.append('<g stroke="#1E1834" stroke-width="1.6" opacity="0.55">' + "".join(f'<line x1="20" y1="{y}" x2="580" y2="{y}"/>' for y in range(210, 600, 14)) + "</g>")
    # porch roof and posts
    out.append(f'<polygon points="40,268 560,268 580,286 20,286" fill="#1A1428"/><rect x="20" y="286" width="560" height="8" fill="#2E2440"/>')
    # windows flanking the door, warm inside
    for i, wx in enumerate((92, 420)):
        out.append(glow(wx + 44, 370, 90, "#FFB547", f"{u}-wg{i}", 0.35))
        out.append(f'<rect x="{wx}" y="320" width="88" height="104" fill="#FFCB6A"/><rect x="{wx}" y="320" width="88" height="104" fill="url(#{u}-dl)" opacity="0.7"/>'
                   f'<g stroke="#2A2038" stroke-width="5"><rect x="{wx}" y="320" width="88" height="104" fill="none"/><line x1="{wx + 44}" y1="320" x2="{wx + 44}" y2="424"/><line x1="{wx}" y1="372" x2="{wx + 88}" y2="372"/></g>'
                   f'<rect x="{wx - 8}" y="424" width="104" height="8" fill="#2A2038"/>')
    # a paper bat garland and cat silhouette in the left window
    out.append(f'<path d="M 108 424 L 108 404 Q 114 392 124 396 L 128 388 L 132 398 Q 142 404 138 424 Z" fill="#2A1A20"/>')
    out.append(f'<path d="M 138 418 Q 152 412 150 398" fill="none" stroke="#2A1A20" stroke-width="4" stroke-linecap="round"/>')
    # the door, open, light pouring out
    out.append(glow(300, 400, 170, "#FFB547", f"{u}-dg", 0.5))
    out.append(f'<rect x="246" y="300" width="108" height="170" fill="#2A2038"/><rect x="254" y="308" width="92" height="162" fill="url(#{u}-dl)"/>')
    out.append(f'<polygon points="254,308 290,316 290,462 254,470" fill="#5A2E2A"/><polygon points="258,320 284,324 284,380 258,382" fill="#6E3A30"/>'
               f'<circle cx="284" cy="398" r="3" fill="#E9B949"/>')
    # porch light
    out.append(glow(380, 318, 50, "#FFD27A", f"{u}-pl", 0.8) + f'<rect x="372" y="308" width="16" height="22" rx="3" fill="#FFE7A3" stroke="#1A1428" stroke-width="3"/>')
    # porch floor and steps
    out.append(f'<rect x="0" y="470" width="600" height="130" fill="url(#{u}-pr)"/>')
    for i, (y, w) in enumerate(((470, 220), (500, 280), (530, 340), (560, 400))):
        out.append(f'<rect x="{300 - w / 2}" y="{y}" width="{w}" height="30" fill="#5A3A2E"/><rect x="{300 - w / 2}" y="{y}" width="{w}" height="5" fill="#8A5A40"/>')
    out.append(f'<polygon points="254,470 346,470 420,600 180,600" fill="#FFC560" opacity="0.18"/>')
    # porch posts
    out.append('<rect x="40" y="286" width="16" height="190" fill="#1A1428"/><rect x="544" y="286" width="16" height="190" fill="#1A1428"/>')
    # pumpkins on the steps
    out.append(pumpkin(u + "p1", 152, 486, 78, 56, face="toothy", seed=5, leaf=False, glow_r=100))
    out.append(pumpkin(u + "p2", 450, 488, 86, 60, face="classic", seed=6, leaf=False, glow_r=110))
    out.append(pumpkin(u + "p3", 502, 520, 56, 40, face="cute", seed=7, leaf=False, vine=False, glow_r=70))
    out.append(pumpkin(u + "p4", 98, 526, 52, 38, seed=8, leaf=False, vine=False, face=None, skin=("#F6E6C8", "#E0CCA8", "#A89070")))
    # the trick-or-treaters on the steps, backlit
    out.append(kid(262, 524, 104, "ghost"))
    out.append(kid(336, 520, 112, "witch"))
    out.append(kid(300, 548, 80, "cat"))
    out.append(vignette(u, strength=0.5))
    # type panel above the porch
    out.append(ruled(300, 92, "OCTOBER 31", MONO, 18, CANDLE, ls=7))
    out.append(word(162, 186, "TRICK", BEBAS, 90, BONE, max_w=230, ls=4, shadow="#0A0614", sdy=5))
    out.append(word(294, 178, "or", SERIF_IT, 56, AMBER, max_w=80, glow_col=ORANGE, glow_op=0.3))
    out.append(word(430, 186, "TREAT", BEBAS, 90, BONE, max_w=230, ls=4, shadow="#0A0614", sdy=5))
    return "\n".join(out)



def black_cat(u, cx, base, s, fill="#120C16", rim="#C8B8F0", eye="#D9F05A", flip=False, tail_up=True):
    """Sitting black cat in profile facing right, head tipped up; rim light along the back."""
    sx = -s if flip else s
    body = "M -30 0 C -40 -20 -36 -48 -14 -60 C -4 -66 10 -64 16 -56 C 22 -40 26 -20 24 0 Z"
    back = "M -30 0 C -40 -20 -36 -48 -14 -60 C -8 -64 -2 -68 0 -74"
    out = [f'<g transform="translate({cx:.1f} {base:.1f}) scale({sx:.3f} {s:.3f})">']
    if tail_up:
        out.append(f'<path d="M -26 -4 C -54 -2 -66 -20 -60 -40 C -56 -54 -46 -56 -44 -66" fill="none" stroke="{fill}" stroke-width="8" stroke-linecap="round"/>'
                   f'<path d="M -62 -24 C -64 -36 -56 -52 -46 -58" fill="none" stroke="{rim}" stroke-width="1.6" opacity="0.7" stroke-linecap="round"/>')
    else:
        out.append(f'<path d="M -26 -2 C -40 4 -30 10 0 8 C 20 7 34 6 38 0" fill="none" stroke="{fill}" stroke-width="8" stroke-linecap="round"/>')
    out.append(f'<path d="{body}" fill="{fill}"/><ellipse cx="-16" cy="-14" rx="22" ry="16" fill="{fill}"/>'
               f'<rect x="6" y="-34" width="9" height="34" rx="4" fill="{fill}"/><rect x="15" y="-34" width="9" height="34" rx="4" fill="{fill}"/>'
               f'<ellipse cx="12" cy="-1" rx="7" ry="3" fill="{fill}"/><ellipse cx="21" cy="-1" rx="7" ry="3" fill="{fill}"/>'
               f'<circle cx="10" cy="-74" r="17" fill="{fill}"/><ellipse cx="24" cy="-70" rx="9" ry="7" fill="{fill}"/>'
               f'<path d="M -2 -84 L -2 -104 L 12 -90 Z M 12 -90 L 24 -104 L 26 -82 Z" fill="{fill}"/>')
    out.append(f'<path d="M 1 -98 L 6 -92" stroke="#7A4A6A" stroke-width="3" stroke-linecap="round" opacity="0.6"/>')
    out.append(f'<g fill="none" stroke="{rim}" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"><path d="{back}" stroke-width="2.2"/>'
               f'<path d="M -6 -80 L -2 -104 L 8 -94" stroke-width="1.8"/><path d="M -36 -10 C -38 -16 -38 -22 -36 -26" stroke-width="1.6"/></g>')
    out.append(f'<ellipse cx="18" cy="-76" rx="4.6" ry="3.4" fill="{eye}" transform="rotate(-12 18 -76)"/><ellipse cx="18.6" cy="-76" rx="1.2" ry="3" fill="#120C16"/>'
               f'<circle cx="16.8" cy="-77.4" r="1" fill="#FFFFFF"/><path d="M 31 -69 l 2 1.4" stroke="#C78AA0" stroke-width="2.4" stroke-linecap="round"/>'
               f'<g stroke="{rim}" stroke-width="0.9" opacity="0.7" stroke-linecap="round"><path d="M 28 -66 L 46 -70"/><path d="M 28 -64 L 46 -62"/><path d="M 27 -62 L 42 -56"/></g>')
    out.append("</g>")
    return "".join(out)


def stone_wall(u, top, seed, col=("#3A3046", "#2E2638", "#463A52"), mortar="#14101A", rim="#8A7AA8"):
    rnd = random.Random(seed)
    out = [f'<rect x="0" y="{top}" width="600" height="{600 - top}" fill="{mortar}"/>']
    y = top + 2
    row = 0
    while y < 600:
        h = rnd.uniform(26, 34)
        x = -rnd.uniform(0, 40)
        while x < 600:
            w = rnd.uniform(46, 84)
            out.append(f'<rect x="{x + 2:.1f}" y="{y:.1f}" width="{w - 4:.1f}" height="{h - 4:.1f}" rx="7" fill="{rnd.choice(col)}"/>')
            out.append(f'<path d="M {x + 6:.1f} {y + 3:.1f} L {x + w - 8:.1f} {y + 3:.1f}" stroke="{rim}" stroke-width="2" opacity="{0.45 - row * 0.1:.2f}" stroke-linecap="round"/>')
            x += w
        y += h
        row += 1
    out.append(dots(160, seed, (0, top, 600, 600), "#000", r=(0.6, 1.8), opacity=(0.2, 0.5)))
    return "".join(out)


def d_here_for_the_boos():
    u = "hwhb"
    out = [bg(u, [(0, "#0E1A2E"), (0.5, "#22284E"), (1, "#3A2A58")])]
    out.append(starfield(6, 60, (0, 0, 600, 380), tw=5, avoid=(470, 120, 80)))
    out.append(moon(u, 476, 122, 46, halo_r=3.0, halo_op=0.4, seed=11))
    # ghosts drifting past on a breeze, with swooshes
    for (a, b, c, d) in (("M 60 250", "C 160 300 240 150 330 190", "", ""),):
        pass
    out.append('<g fill="none" stroke="#E8E0FF" stroke-linecap="round" opacity="0.35">'
               '<path d="M 70 300 C 140 330 200 250 262 262" stroke-width="3" stroke-dasharray="1 9"/>'
               '<path d="M 240 196 C 300 210 320 140 380 150" stroke-width="3" stroke-dasharray="1 9"/>'
               '<path d="M 330 286 C 380 300 410 250 452 252" stroke-width="3" stroke-dasharray="1 9"/></g>')
    out.append(ghost(u + "a", 316, 106, 104, lean=-0.5, face="happy", glow_op=0.3))
    out.append(ghost(u + "b", 440, 208, 84, lean=-0.6, face="boo", glow_op=0.25))
    out.append(ghost(u + "c", 532, 128, 56, lean=-0.7, face="happy", arms=False, glow_op=0.2))
    # stone garden wall, a pumpkin, the cat watching the show
    out.append(stone_wall(u, 404, 3))
    out.append(defs(lg(f"{u}-cap", [(0, "#5A4A6A"), (1, "#2E2438")])))
    out.append(f'<rect x="0" y="392" width="600" height="18" fill="url(#{u}-cap)"/><rect x="0" y="392" width="600" height="3" fill="#9A88B8" opacity="0.6"/>')
    out.append(pumpkin(u + "pk", 162, 340, 150, 108, seed=12, stem_lean=-6, leaf=True))
    out.append(f'<ellipse cx="162" cy="394" rx="80" ry="6" fill="#000" opacity="0.4"/>')
    out.append(black_cat(u, 152, 292, 1.32, rim="#B8C8F0"))
    out.append(pumpkin(u + "p2", 286, 372, 56, 40, face="cute", seed=13, leaf=False, glow_r=80))
    # ivy over the wall
    rnd = random.Random(4)
    ivy = []
    for i in range(16):
        x = 380 + i * 14 + rnd.uniform(-4, 4)
        y = 398 + abs(math.sin(i * 0.7)) * 26
        ivy.append(f'<path d="M {x:.1f} {y:.1f} c -6 -4 -8 -12 0 -14 c 8 2 6 10 0 14 Z" fill="{rnd.choice(["#3E5A2E", "#4E6E36", "#2E4422"])}" transform="rotate({rnd.uniform(-50, 50):.0f} {x:.1f} {y:.1f})"/>')
    out.append(f'<path d="M 372 398 C 420 420 470 404 520 426 C 560 440 590 420 610 432" fill="none" stroke="#2E4422" stroke-width="2"/>' + "".join(ivy))
    out.append(defs(lg(f"{u}-fg", [(0, "#0A0712", 0), (0.4, "#0A0712", 0.7), (1, "#0A0712", 0.9)])))
    out.append(f'<rect x="0" y="420" width="600" height="180" fill="url(#{u}-fg)"/>')
    out.append(vignette(u, strength=0.5))
    out.append(word(300, 474, "here for the", SERIF_IT, 50, BONE, max_w=420, shadow="#000", sdy=3))
    out.append(word(300, 546, "BOOS", BEBAS, 92, "#FFFFFF", max_w=400, ls=22, glow_col="#D8CCFF", glow_op=0.35, shadow="#0A0614", sdy=5))
    return "\n".join(out)


def witch_hat(u, cx, base, s, rot=0, hat=("#3A2E4A", "#1E1628", "#0C0812"), band=("#7A3E9A", "#4A1E66"), buckle="#E9B949"):
    """Crooked felt witch hat with a bent tip, purple band and brass buckle; (cx, base) = brim centre."""
    cone = "M -52 -10 C -46 -60 -30 -112 -8 -150 C 4 -170 34 -178 52 -158 C 34 -160 18 -150 18 -126 C 24 -88 40 -40 54 -10 Q 0 2 -52 -10 Z"
    out = [defs(lg(f"{u}-hc", [(0, hat[0]), (0.45, hat[1]), (1, hat[2])], 0, 0, 1, 0),
                rg(f"{u}-hb", [(0, hat[0]), (0.7, hat[1]), (1, hat[2])], cx=0.4, cy=0.3, r=0.7),
                lg(f"{u}-hbd", [(0, band[0]), (1, band[1])]),
                f'<clipPath id="{u}-hcc"><path d="{cone}"/></clipPath>'),
           f'<g transform="translate({cx:.1f} {base:.1f}) rotate({rot:.1f}) scale({s:.3f})">',
           f'<ellipse cx="0" cy="0" rx="104" ry="24" fill="url(#{u}-hb)"/>',
           f'<path d="M -100 4 Q 0 34 100 4 Q 0 22 -100 4 Z" fill="#000" opacity="0.4"/>',
           f'<path d="{cone}" fill="url(#{u}-hc)"/>',
           f'<g clip-path="url(#{u}-hcc)"><path d="M -60 -6 C -50 -60 -40 -100 -14 -150" fill="none" stroke="#7A6A90" stroke-width="5" opacity="0.5"/>'
           f'<path d="M -40 -70 Q -10 -64 24 -74 M -30 -104 Q -6 -98 18 -106" fill="none" stroke="#000" stroke-width="3" opacity="0.3"/>'
           f'<rect x="-30" y="-96" width="22" height="20" fill="#5A3A2E" transform="rotate(-8 -19 -86)"/>'
           f'<path d="M -28 -94 l 18 -2 M -28 -78 l 18 -3 M -29 -94 l 1 16 M -11 -97 l 1 17" stroke="#E9C88A" stroke-width="1.6" stroke-dasharray="3 3" opacity="0.8"/></g>',
           f'<path d="M -52 -10 Q 0 2 54 -10 L 49 -36 Q 0 -26 -47 -36 Z" fill="url(#{u}-hbd)"/>',
           f'<path d="M -48 -33 Q 0 -23 50 -33" fill="none" stroke="#C89AE0" stroke-width="2" opacity="0.6"/>',
           f'<rect x="-14" y="-34" width="28" height="24" rx="3" fill="none" stroke="{buckle}" stroke-width="5"/>',
           f'<rect x="-14" y="-34" width="28" height="24" rx="3" fill="none" stroke="#FFF4C8" stroke-width="1.4" opacity="0.7" transform="translate(-1 -1)"/>',
           f'<ellipse cx="-40" cy="-6" rx="40" ry="5" fill="#FFFFFF" opacity="0.08"/>',
           f'<path d="M -98 -2 Q -60 -20 0 -22" fill="none" stroke="#8A7AA8" stroke-width="2.4" opacity="0.5"/>',
           "</g>"]
    return "".join(out)


def book(u, x, y, w, h, cover, dark, band="#E9B949", pages="#EFE2C4", rot=0):
    """Closed book lying flat, seen from the spine side; (x, y) top-left before rotation."""
    cxr, cyr = x + w / 2, y + h / 2
    out = [defs(lg(f"{u}", [(0, cover), (0.5, cover), (1, dark)]))]
    out.append(f'<g transform="rotate({rot} {cxr:.1f} {cyr:.1f})">')
    out.append(f'<rect x="{x + 6:.1f}" y="{y + 3:.1f}" width="{w - 6:.1f}" height="{h - 6:.1f}" fill="{pages}"/>')
    out.append(f'<g stroke="#C8B48E" stroke-width="1">' + "".join(f'<line x1="{x + 8:.1f}" y1="{y + 3 + i * (h - 6) / 7:.1f}" x2="{x + w:.1f}" y2="{y + 3 + i * (h - 6) / 7:.1f}"/>' for i in range(1, 7)) + "</g>")
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w * 0.975:.1f}" height="{h:.1f}" rx="4" fill="url(#{u})"/>')
    for t in (0.12, 0.2, 0.8, 0.88):
        out.append(f'<rect x="{x + w * t:.1f}" y="{y:.1f}" width="{w * 0.02:.1f}" height="{h:.1f}" fill="{band}" opacity="0.85"/>')
    out.append(f'<rect x="{x + w * 0.34:.1f}" y="{y + h * 0.25:.1f}" width="{w * 0.32:.1f}" height="{h * 0.5:.1f}" rx="2" fill="none" stroke="{band}" stroke-width="1.6" opacity="0.8"/>')
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w * 0.975:.1f}" height="3" fill="#FFFFFF" opacity="0.2"/>')
    out.append("</g>")
    return "".join(out)


def bottle(u, cx, base, w, h, liquid=("#C6F27A", SLIME, "#3E6A1E"), glass="#BFE6D8", cork="#B88A5A", neck=0.32, round_=True, glow_op=0.5, fill_level=0.62, label=None):
    """Glass potion bottle with glowing liquid, cork, highlights; round_ = round flask else tall square."""
    nw = w * neck
    nh = h * 0.24
    top = base - h
    if round_:
        r = w / 2
        bcy = base - r
        shape = (f"M {cx - nw / 2:.1f} {top + nh * 0.25:.1f} L {cx - nw / 2:.1f} {bcy - r * 0.86:.1f} A {r:.1f} {r:.1f} 0 1 0 {cx + nw / 2:.1f} {bcy - r * 0.86:.1f} "
                 f"L {cx + nw / 2:.1f} {top + nh * 0.25:.1f} Z")
    else:
        shoulder = top + nh
        shape = (f"M {cx - nw / 2:.1f} {top + nh * 0.25:.1f} L {cx - nw / 2:.1f} {shoulder:.1f} Q {cx - w / 2:.1f} {shoulder:.1f} {cx - w / 2:.1f} {shoulder + w * 0.25:.1f} "
                 f"L {cx - w / 2:.1f} {base - 4:.1f} Q {cx - w / 2:.1f} {base:.1f} {cx - w / 2 + 4:.1f} {base:.1f} L {cx + w / 2 - 4:.1f} {base:.1f} Q {cx + w / 2:.1f} {base:.1f} {cx + w / 2:.1f} {base - 4:.1f} "
                 f"L {cx + w / 2:.1f} {shoulder + w * 0.25:.1f} Q {cx + w / 2:.1f} {shoulder:.1f} {cx + nw / 2:.1f} {shoulder:.1f} L {cx + nw / 2:.1f} {top + nh * 0.25:.1f} Z")
    ly = base - (h - nh) * fill_level
    out = [defs(f'<clipPath id="{u}-bc"><path d="{shape}"/></clipPath>',
                lg(f"{u}-lq", [(0, liquid[0]), (0.5, liquid[1]), (1, liquid[2])]),
                lg(f"{u}-gl", [(0, "#FFFFFF", 0.35), (0.3, glass, 0.12), (0.8, glass, 0.08), (1, "#000000", 0.3)], 0, 0, 1, 0))]
    if glow_op:
        out.append(glow(cx, (ly + base) / 2, w * 1.3, liquid[1], f"{u}-bgw", glow_op))
    out.append(f'<path d="{shape}" fill="#1A1622" opacity="0.55"/>')
    out.append(f'<g clip-path="url(#{u}-bc)"><rect x="{cx - w:.1f}" y="{ly:.1f}" width="{w * 2:.1f}" height="{base - ly + 2:.1f}" fill="url(#{u}-lq)"/>'
               f'<ellipse cx="{cx:.1f}" cy="{ly:.1f}" rx="{w / 2:.1f}" ry="{max(2, w * 0.06):.1f}" fill="{liquid[0]}"/>'
               + "".join(f'<circle cx="{cx + (i * 37 % 10 - 5) * w * 0.06:.1f}" cy="{ly + (base - ly) * (0.2 + 0.15 * i):.1f}" r="{max(1.2, w * (0.03 + 0.01 * (i % 3))):.1f}" fill="#FFFFFF" opacity="0.5"/>' for i in range(5))
               + f'<rect x="{cx - w:.1f}" y="{top:.1f}" width="{w * 2:.1f}" height="{h:.1f}" fill="url(#{u}-gl)"/></g>')
    out.append(f'<path d="{shape}" fill="none" stroke="#E8F4F0" stroke-width="{max(1.5, w * 0.03):.1f}" opacity="0.45"/>')
    out.append(f'<path d="M {cx - w * 0.3:.1f} {base - h * 0.5:.1f} Q {cx - w * 0.36:.1f} {base - h * 0.25:.1f} {cx - w * 0.24:.1f} {base - h * 0.1:.1f}" fill="none" stroke="#FFFFFF" stroke-width="{max(2, w * 0.07):.1f}" stroke-linecap="round" opacity="0.6"/>')
    out.append(f'<rect x="{cx - nw * 0.62:.1f}" y="{top + nh * 0.18:.1f}" width="{nw * 1.24:.1f}" height="{max(3, nh * 0.16):.1f}" rx="2" fill="#D8E8E0" opacity="0.7"/>')
    out.append(f'<path d="M {cx - nw * 0.42:.1f} {top + nh * 0.3:.1f} L {cx - nw * 0.5:.1f} {top - nh * 0.2:.1f} Q {cx:.1f} {top - nh * 0.32:.1f} {cx + nw * 0.5:.1f} {top - nh * 0.2:.1f} L {cx + nw * 0.42:.1f} {top + nh * 0.3:.1f} Z" fill="{cork}"/>'
               f'<path d="M {cx + nw * 0.1:.1f} {top - nh * 0.2:.1f} L {cx + nw * 0.42:.1f} {top + nh * 0.3:.1f}" stroke="#6E4A2A" stroke-width="{max(1.5, nw * 0.12):.1f}" opacity="0.5"/>')
    if label:
        lw, lh = w * 0.62, h * 0.24
        ly0 = base - h * (0.42 if round_ else 0.5)
        out.append(f'<rect x="{cx - lw / 2:.1f}" y="{ly0:.1f}" width="{lw:.1f}" height="{lh:.1f}" rx="2" fill="#EFE2C4"/>'
                   f'<rect x="{cx - lw / 2 + 3:.1f}" y="{ly0 + 3:.1f}" width="{lw - 6:.1f}" height="{lh - 6:.1f}" fill="none" stroke="#6A3A2A" stroke-width="1.2"/>'
                   + label(cx, ly0 + lh / 2))
    return "".join(out)


def d_witch_please():
    u = "hwwp"
    out = [bg(u, [(0, "#0E1A12"), (0.55, "#1E3A1E"), (1, "#0C140C")])]
    out.append(glow(300, 330, 330, "#9BD14B", f"{u}-amb", 0.3))
    out.append(starfield(8, 50, (0, 0, 600, 300), col="#E8F4C8", tw=6))
    # shelf / tabletop
    out.append(defs(lg(f"{u}-tb", [(0, "#4A2E22"), (1, "#1A0E0A")])))
    out.append(f'<rect x="0" y="492" width="600" height="108" fill="url(#{u}-tb)"/><rect x="0" y="492" width="600" height="4" fill="#8A5A3A"/>')
    out.append(ground_glow(300, 494, 260, 30, "#C8F07A", f"{u}-tg", 0.35))
    # stacked spellbooks
    out.append(book(u + "b1", 150, 446, 300, 48, "#5A2E6E", "#2E1440", rot=0))
    out.append(book(u + "b2", 172, 404, 252, 44, "#2E5A3A", "#163020", rot=-2))
    out.append(book(u + "b3", 186, 368, 220, 38, "#8A3A2A", "#4A1A12", rot=1.5))
    # the hat, set at a jaunty angle
    out.append(witch_hat(u, 296, 366, 1.32, rot=-6))
    # candle and a little potion
    out.append(candle(u + "cd", 492, 494, 104, 30, seed=4, glow_r=120))
    out.append(bottle(u + "bt", 108, 494, 56, 96, round_=True, glow_op=0.55))
    # a spider on its silk from the top
    out.append(f'<line x1="470" y1="0" x2="470" y2="262" stroke="#D8E8C8" stroke-width="1.6" opacity="0.7"/>')
    out.append(spider(u, 470, 276, 18))
    out.append(vignette(u, strength=0.55))
    out.append(word(300, 152, "WITCH", BEBAS, 132, BONE, max_w=420, ls=14, shadow="#050A05", sdy=6))
    out.append(word(300, 222, "please", SERIF_IT, 78, SLIME, max_w=360, glow_col=SLIME, glow_op=0.35))
    return "\n".join(out)


def spider(u, cx, cy, r, body=("#5A4A6E", "#2A2036", "#120C1A"), eye="#FFFFFF", smile=True, legs="#1A1222"):
    """Round fuzzy cartoon spider with big eyes; r = abdomen radius."""
    out = [defs(rg(f"{u}-sp", [(0, body[0]), (0.6, body[1]), (1, body[2])], cx=0.38, cy=0.32, r=0.7))]
    k = r / 18
    for sgn in (-1, 1):
        for i, (a, b) in enumerate(((-30, -50), (-8, -20), (12, 14), (30, 46))):
            x0, y0 = cx + sgn * 10 * k, cy + (i - 1.5) * 5 * k
            kx, ky = cx + sgn * 30 * k, cy + (i - 1.5) * 9 * k - 14 * k
            ex, ey = cx + sgn * 40 * k, cy + (i - 1.5) * 13 * k + 6 * k
            out.append(f'<path d="M {x0:.1f} {y0:.1f} Q {kx:.1f} {ky:.1f} {ex:.1f} {ey:.1f}" fill="none" stroke="{legs}" stroke-width="{max(2.2, 3.2 * k):.1f}" stroke-linecap="round"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="url(#{u}-sp)"/>')
    out.append(dots(int(r * 2), int(cx), (cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7), "#8A7AA8", r=(0.5, 1.1), opacity=(0.3, 0.6)))
    out.append(f'<ellipse cx="{cx - r * 0.38:.1f}" cy="{cy - r * 0.42:.1f}" rx="{r * 0.28:.1f}" ry="{r * 0.16:.1f}" transform="rotate(-30 {cx - r * 0.38:.1f} {cy - r * 0.42:.1f})" fill="#FFFFFF" opacity="0.4"/>')
    for sgn in (-1, 1):
        out.append(f'<circle cx="{cx + sgn * r * 0.32:.1f}" cy="{cy - r * 0.02:.1f}" r="{r * 0.26:.1f}" fill="{eye}"/>'
                   f'<circle cx="{cx + sgn * r * 0.32 + r * 0.04:.1f}" cy="{cy + r * 0.04:.1f}" r="{r * 0.14:.1f}" fill="#120C1A"/>'
                   f'<circle cx="{cx + sgn * r * 0.32 + r * 0.08:.1f}" cy="{cy - r * 0.02:.1f}" r="{r * 0.05:.1f}" fill="#FFFFFF"/>')
    if smile:
        out.append(f'<path d="M {cx - r * 0.2:.1f} {cy + r * 0.38:.1f} Q {cx:.1f} {cy + r * 0.56:.1f} {cx + r * 0.2:.1f} {cy + r * 0.38:.1f}" fill="none" stroke="{eye}" stroke-width="{max(1.5, r * 0.08):.1f}" stroke-linecap="round"/>')
    return "".join(out)


def web(u, cx, cy, spokes, rings, seed, col="#E8E0F0", sw=1.6, dew=True, clip=None):
    """Orb web: spokes = list of (angle_deg, length); rings sag toward the hub between spokes."""
    rnd = random.Random(seed)
    sp = sorted(spokes)
    out = []
    for a, L in sp:
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + L * math.cos(math.radians(a)):.1f}" y2="{cy + L * math.sin(math.radians(a)):.1f}"/>')
    ring_paths = []
    drops = []
    for r in rings:
        segs = []
        for (a1, L1), (a2, L2) in zip(sp, sp[1:] + sp[:1]):
            if r > L1 * 0.97 or r > L2 * 0.97:
                continue
            if (a2 - a1) % 360 > 100:
                continue
            r1 = r * rnd.uniform(0.96, 1.04)
            r2 = r * rnd.uniform(0.96, 1.04)
            p1 = (cx + r1 * math.cos(math.radians(a1)), cy + r1 * math.sin(math.radians(a1)))
            p2 = (cx + r2 * math.cos(math.radians(a2)), cy + r2 * math.sin(math.radians(a2)))
            am = math.radians((a1 + ((a2 - a1) % 360) / 2))
            sag = r * 0.86
            q = (cx + sag * math.cos(am), cy + sag * math.sin(am))
            segs.append(f'M {p1[0]:.1f} {p1[1]:.1f} Q {q[0]:.1f} {q[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}')
            if dew and rnd.random() < 0.35:
                t = rnd.uniform(0.3, 0.7)
                dx = (1 - t) ** 2 * p1[0] + 2 * (1 - t) * t * q[0] + t * t * p2[0]
                dy = (1 - t) ** 2 * p1[1] + 2 * (1 - t) * t * q[1] + t * t * p2[1]
                drops.append((dx, dy, rnd.uniform(1.8, 3.4)))
        ring_paths.append(" ".join(segs))
    out.append(f'<path d="{" ".join(ring_paths)}"/>')
    g = f'<g fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round"' + (f' clip-path="url(#{clip})"' if clip else "") + ">" + "".join(out) + "</g>"
    dd = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#DCEFFF" opacity="0.85"/><circle cx="{x - r * 0.35:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.35:.1f}" fill="#FFFFFF"/>' for x, y, r in drops)
    return g, dd


def d_creep_it_real():
    u = "hwcr"
    out = [bg(u, [(0, "#1A1030"), (0.55, "#24163C"), (1, "#0E0A16")])]
    out.append(starfield(9, 60, (0, 0, 600, 420), tw=4, avoid=(372, 196, 150)))
    out.append(moon(u, 372, 196, 128, halo_r=1.9, halo_op=0.45, seed=15))
    # a crooked branch across the top, the web strung between it and the frame
    out.append(gnarly_tree(612, 120, 520, 5, "#0C0812", depth=5, lean=-80, spread=18, w0=26))
    out.append(defs(f'<clipPath id="{u}-mc"><circle cx="372" cy="196" r="128"/></clipPath>'))
    spokes = [(a, L) for a, L in ((-170, 240), (-140, 250), (-112, 230), (-84, 200), (-52, 240), (-20, 280), (8, 300), (36, 260), (64, 230), (92, 220), (122, 230), (150, 250))]
    g, dd = web(u, 300, 210, spokes, [16, 30, 46, 64, 84, 106, 130, 156, 184, 214, 246], 7, col="#E2D8F0", sw=1.6)
    out.append(g)
    g2, _ = web(u, 300, 210, spokes, [16, 30, 46, 64, 84, 106, 130, 156, 184, 214, 246], 7, col="#3A2A50", sw=1.8, dew=False, clip=f"{u}-mc")
    out.append(g2)
    out.append(dd)
    # the spider, dropping in to say hi
    out.append(f'<line x1="300" y1="210" x2="300" y2="318" stroke="#E2D8F0" stroke-width="1.8"/>')
    out.append(spider(u, 300, 336, 22))
    out.append(defs(lg(f"{u}-fg", [(0, "#0A0712", 0), (0.45, "#0A0712", 0.85), (1, "#0A0712", 1)])))
    out.append(f'<rect x="0" y="380" width="600" height="220" fill="url(#{u}-fg)"/>')
    out.append(vignette(u, strength=0.5))
    out.append(word(300, 452, "creep it", SERIF_IT, 76, BONE, max_w=400, shadow="#000", sdy=4))
    out.append(word(300, 548, "REAL", BEBAS, 124, ORANGE, max_w=420, ls=24, glow_col="#FF8A2A", glow_op=0.3, shadow="#1A0A04", sdy=6))
    return "\n".join(out)


def d_stay_spooky():
    u = "hwsy"
    out = [bg(u, [(0, "#160E26"), (0.6, "#2A1640"), (1, "#120A1C")])]
    out.append(starfield(10, 50, (0, 0, 600, 260), col="#E8D8FF", tw=5, avoid=(300, 236, 170)))
    # draped velvet table cloth with gold fringe
    out.append(defs(lg(f"{u}-vel", [(0, "#6A2E7E"), (0.6, "#3E1650"), (1, "#1E0A28")]),
                    rg(f"{u}-ball", [(0, "#E8D8FF"), (0.25, "#A88AE0"), (0.6, "#5A3A9A"), (0.88, "#2A1650"), (1, "#140A28")], cx=0.45, cy=0.4, r=0.6),
                    lg(f"{u}-brass", [(0, "#F6D78A"), (0.5, "#B8862E"), (1, "#5A3A12")], 0, 0, 1, 0),
                    '<clipPath id="hwsy-bc"><circle cx="300" cy="250" r="138"/></clipPath>'))
    out.append(f'<path d="M -10 420 Q 150 404 300 410 Q 450 404 610 420 L 610 600 L -10 600 Z" fill="url(#{u}-vel)"/>')
    out.append('<g fill="none" stroke="#1A0822" stroke-width="5" opacity="0.5">' + "".join(
        f'<path d="M {x} 430 Q {x + 10} 500 {x - 6} 600"/>' for x in (40, 120, 200, 400, 480, 560)) + "</g>")
    out.append('<g fill="none" stroke="#9A5AB0" stroke-width="3" opacity="0.35">' + "".join(
        f'<path d="M {x + 12} 432 Q {x + 22} 500 {x + 8} 600"/>' for x in (40, 120, 200, 400, 480, 560)) + "</g>")
    # glow of the ball on the cloth
    out.append(ground_glow(300, 420, 220, 34, "#B88AFF", f"{u}-tg", 0.55))
    # candles either side
    out.append(candle(u + "c1", 104, 430, 96, 28, seed=3, glow_r=110))
    out.append(candle(u + "c2", 140, 434, 60, 22, seed=6, glow_r=70))
    out.append(candle(u + "c3", 494, 432, 80, 26, seed=9, glow_r=100))
    # brass claw stand
    out.append('<g transform="translate(0 -18)">')
    out.append(f'<path d="M 214 432 Q 300 446 386 432 L 370 410 Q 300 420 230 410 Z" fill="url(#{u}-brass)"/>'
               f'<path d="M 236 412 Q 300 360 364 412 L 350 380 Q 300 350 250 380 Z" fill="url(#{u}-brass)"/>'
               f'<path d="M 214 432 Q 300 446 386 432" fill="none" stroke="#FFF0C0" stroke-width="2" opacity="0.6"/>')
    for x in (246, 300, 354):
        out.append(f'<path d="M {x - 10} 404 Q {x} 384 {x + 10} 404 Q {x} 398 {x - 10} 404 Z" fill="#E8C060"/>')
    # the crystal ball with a tiny moonlit night inside
    out.append(glow(300, 250, 230, "#B88AFF", f"{u}-bglow", 0.5))
    out.append('<circle cx="300" cy="250" r="138" fill="url(#hwsy-ball)"/>')
    inner = [moon(u + "i", 330, 210, 34, halo_r=2.4, halo_op=0.55, seed=2),
             starfield(12, 30, (170, 120, 430, 300), col="#FFFFFF", tw=3)]
    for i, (x, y, rr, op) in enumerate(((260, 300, 120, 0.45), (340, 330, 110, 0.4), (300, 270, 80, 0.3))):
        inner.append(mist(x, y, rr, rr * 0.45, "#E0C8FF", f"{u}-sw{i}", op))
    inner.append(bat(250, 186, 18, "#1A0E2A", rot=-12, flap=8) + bat(286, 160, 11, "#1A0E2A", rot=8, flap=-6))
    inner.append(gnarly_tree(212, 360, 150, 3, "#1A0E2A", depth=5, lean=10, spread=30))
    poly, _ = hill([(150, 344), (260, 330), (380, 340), (460, 330)], 2, 400, "#1A0E2A")
    inner.append(poly)
    inner.append('<path d="M 186 300 C 220 250 290 330 340 290 C 380 260 410 300 420 280" fill="none" stroke="#FFFFFF" stroke-width="3" opacity="0.25" stroke-linecap="round"/>')
    out.append('<g clip-path="url(#hwsy-bc)">' + "".join(inner) + "</g>")
    # glass: rim darkening, reflections
    out.append(defs(rg(f"{u}-rim", [(0.7, "#000", 0), (1, "#0A0418", 0.6)])))
    out.append(f'<circle cx="300" cy="250" r="138" fill="url(#{u}-rim)"/>')
    out.append('<path d="M 196 206 A 112 112 0 0 1 300 136" fill="none" stroke="#FFFFFF" stroke-width="14" stroke-linecap="round" opacity="0.5"/>'
               '<path d="M 210 236 A 96 96 0 0 1 216 214" fill="none" stroke="#FFFFFF" stroke-width="8" stroke-linecap="round" opacity="0.4"/>'
               '<ellipse cx="358" cy="352" rx="34" ry="8" transform="rotate(-28 358 352)" fill="#E8D8FF" opacity="0.35"/>'
               '<circle cx="300" cy="250" r="138" fill="none" stroke="#E8D8FF" stroke-width="2" opacity="0.45"/>')
    out.append("</g>")
    out.append(vignette(u, strength=0.5))
    out.append(word(300, 462, "STAY", BEBAS, 50, BONE, max_w=300, ls=26, shadow="#0A0418", sdy=3))
    out.append(word(300, 532, "spooky", SERIF_IT, 70, "#E2C8FF", max_w=380, glow_col="#B88AFF", glow_op=0.35, shadow="#0A0418", sdy=3))
    return "\n".join(out)



def neon(x, y, s, font, size, color, ls=0, max_w=470, core="#FFFFFF", dim=1.0, uid=None):
    """Neon tube lettering: halo, coloured tube, hot white core."""
    size = fit_size(s, font, size, max_w, ls)
    w = measure(s, font, size, ls)
    xx = x + (ls / 2 if ls else 0)
    a = f'text-anchor="middle" {font} font-size="{size}"' + (f' letter-spacing="{ls}"' if ls else "")
    t = esc(s)
    out = [mist(x, y - size * 0.35, w * 0.62 + size * 0.3, size * 0.75, color, uid or f"ne{zlib.crc32(f'{s}{x:.0f}{y:.0f}'.encode()):x}", 0.45 * dim),
           f'<text x="{xx:.1f}" y="{y:.1f}" {a} fill="none" stroke="{color}" stroke-width="{size * 0.16:.1f}" stroke-linejoin="round" opacity="{0.28 * dim:.2f}">{t}</text>',
           f'<text x="{xx:.1f}" y="{y:.1f}" {a} fill="none" stroke="{color}" stroke-width="{size * 0.065:.1f}" stroke-linejoin="round" opacity="{dim:.2f}">{t}</text>',
           f'<text x="{xx:.1f}" y="{y:.1f}" {a} fill="none" stroke="{core}" stroke-width="{size * 0.022:.1f}" stroke-linejoin="round" opacity="{0.9 * dim:.2f}">{t}</text>']
    return "".join(out)


def brick_wall(seed, top=0, col=("#2A1E2E", "#24192A", "#30222F", "#1F1624"), mortar="#120C14"):
    rnd = random.Random(seed)
    out = [f'<rect x="0" y="{top}" width="600" height="{600 - top}" fill="{mortar}"/>']
    bh, bw = 22, 52
    for r, y in enumerate(range(top, 600, bh)):
        off = (r % 2) * bw / 2
        for i in range(-1, 13):
            x = i * bw - off
            out.append(f'<rect x="{x + 1.5:.1f}" y="{y + 1.5}" width="{bw - 3}" height="{bh - 3}" rx="2" fill="{rnd.choice(col)}"/>')
    out.append(dots(260, seed, (0, top, 600, 600), "#000", r=(0.6, 1.6), opacity=(0.2, 0.5)))
    return "".join(out)


def d_haunted_hotel():
    u = "hwhh2"
    out = [brick_wall(21)]
    out.append(defs(lg(f"{u}-sky", [(0, "#0C0A1E"), (1, "#1E1436")])))
    # sign glow washing the bricks
    out.append(glow(300, 290, 360, "#9BD14B", f"{u}-wg", 0.28))
    out.append(glow(300, 380, 260, "#FF8A2A", f"{u}-wo", 0.25))
    # brackets
    out.append('<g fill="#3A3240"><rect x="140" y="40" width="10" height="100"/><rect x="450" y="40" width="10" height="100"/>'
               '<rect x="120" y="36" width="50" height="10" rx="3"/><rect x="430" y="36" width="50" height="10" rx="3"/></g>')
    # the sign board
    out.append(defs(lg(f"{u}-bd", [(0, "#22183A"), (1, "#120C22")])))
    out.append('<rect x="68" y="128" width="464" height="296" rx="28" fill="#0A0612" opacity="0.6" transform="translate(8 10)"/>')
    out.append(ghost(u, 478, 70, 70, lean=0.2, face="happy", arms=True, glow_op=0.3))
    out.append(f'<rect x="68" y="128" width="464" height="296" rx="28" fill="url(#{u}-bd)" stroke="#3A2E4A" stroke-width="6"/>')
    # bulbs around the edge
    bulbs = []
    for i in range(30):
        t = i / 30
        per = 2 * (440 + 272)
        d = t * per
        if d < 440:
            x, y = 80 + d, 140
        elif d < 712:
            x, y = 520, 140 + d - 440
        elif d < 1152:
            x, y = 520 - (d - 712), 412
        else:
            x, y = 80, 412 - (d - 1152)
        on = i % 7 != 3
        bulbs.append(glow(x, y, 14, "#FFC45A", f"{u}-bl{i}", 0.7) if on else "")
        bulbs.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="{"#FFF0B8" if on else "#5A4A3A"}"/>')
    out.append("".join(bulbs))
    # inner neon frame tube
    out.append('<rect x="100" y="160" width="400" height="232" rx="16" fill="none" stroke="#B070E0" stroke-width="10" opacity="0.25"/>'
               '<rect x="100" y="160" width="400" height="232" rx="16" fill="none" stroke="#C890F0" stroke-width="4"/>'
               '<rect x="100" y="160" width="400" height="232" rx="16" fill="none" stroke="#FFFFFF" stroke-width="1.4" opacity="0.8"/>')
    out.append(neon(300, 262, "Haunted", SERIF_IT, 96, "#A8F05A", max_w=360, uid=f"{u}-n1"))
    out.append(neon(300, 370, "HOTEL", BEBAS, 112, "#FF9A3A", ls=18, max_w=340, uid=f"{u}-n2"))
    # tiny stars either side of HOTEL
    for x in (132, 468):
        out.append(twinkle(x, 330, 12, "#FFE7A3"))
    # chains and the hanging vacancy box
    out.append('<g stroke="#5A5060" stroke-width="3" stroke-dasharray="5 3"><line x1="200" y1="424" x2="200" y2="452"/><line x1="400" y1="424" x2="400" y2="452"/></g>')
    out.append(f'<rect x="150" y="452" width="300" height="74" rx="10" fill="#120C1A" stroke="#3A2E4A" stroke-width="4"/>')
    out.append(neon(208, 506, "NO", BEBAS, 46, "#FF4A6A", ls=2, uid=f"{u}-n3"))
    out.append(neon(340, 506, "VACANCY", BEBAS, 46, "#FF8AB0", ls=4, dim=0.35, uid=f"{u}-n4"))
    # a bat perched on the board, a little ghost peeking from behind the corner
    out.append(bat(118, 104, 34, "#0E0A14", rim="#A8F05A", flap=24, eyes="#FFD25E", rot=-6))
    out.append(vignette(u, strength=0.6))
    return "\n".join(out)


def d_witches_brew():
    u = "hwwb"
    out = [bg(u, [(0, "#0E0A18"), (0.6, "#1A1426"), (1, "#0C0A10")])]
    # stone wall behind
    out.append(stone_wall(u, 0, 8, col=("#221C2A", "#1C1724", "#2A2232"), mortar="#0C0A10", rim="#5A7A3A"))
    out.append(defs(lg(f"{u}-dk", [(0, "#0C0A12", 0.85), (0.4, "#0C0A12", 0.55), (1, "#0C0A12", 0.2)])))
    out.append(f'<rect width="600" height="600" fill="url(#{u}-dk)"/>')
    out.append(glow(300, 320, 300, "#9BD14B", f"{u}-amb", 0.45))
    # floor
    out.append(defs(lg(f"{u}-fl", [(0, "#2A2430"), (1, "#100C14")])))
    out.append(f'<rect x="0" y="470" width="600" height="130" fill="url(#{u}-fl)"/>')
    out.append('<g stroke="#000" stroke-width="2" opacity="0.5">' + "".join(f'<line x1="{x}" y1="470" x2="{300 + (x - 300) * 1.8:.0f}" y2="600"/>' for x in range(-60, 680, 70)) + '<line x1="0" y1="520" x2="600" y2="520"/></g>')
    out.append(glow(300, 488, 150, "#FF7A1A", f"{u}-fg", 0.7))
    # the cauldron
    out.append(defs(rg(f"{u}-irn", [(0, "#5A5A66"), (0.45, "#2A2A34"), (1, "#0A0A10")], cx=0.35, cy=0.3, r=0.75),
                    rg(f"{u}-brw", [(0, "#F2FFB0"), (0.4, "#B8F050"), (1, "#4E8A1E")], cx=0.5, cy=0.5, r=0.6)))
    out.append('<path d="M 196 452 L 180 492 L 196 492 L 214 458 Z M 404 452 L 420 492 L 404 492 L 386 458 Z" fill="#14141A"/>')
    out.append(f'<path d="M 150 316 C 140 400 200 470 300 470 C 400 470 460 400 450 316 Z" fill="url(#{u}-irn)"/>')
    out.append('<path d="M 160 340 C 166 400 210 448 270 460" fill="none" stroke="#8A9A7A" stroke-width="5" opacity="0.35" stroke-linecap="round"/>')
    out.append('<path d="M 446 330 C 444 400 400 456 330 466" fill="none" stroke="#9BD14B" stroke-width="4" opacity="0.35" stroke-linecap="round"/>')
    # rim
    out.append(f'<ellipse cx="300" cy="316" rx="160" ry="36" fill="#1A1A22"/>')
    out.append(f'<ellipse cx="300" cy="318" rx="140" ry="27" fill="url(#{u}-brw)"/>')
    out.append(f'<ellipse cx="300" cy="316" rx="160" ry="36" fill="none" stroke="#4A4A56" stroke-width="10"/>')
    out.append(f'<path d="M 142 316 A 158 34 0 0 1 458 316" fill="none" stroke="#C8F07A" stroke-width="3" opacity="0.65"/>')
    # drips over the lip
    for x, L in ((206, 30), (238, 52), (366, 40), (402, 24)):
        out.append(f'<path d="M {x - 7} 340 L {x - 7} {340 + L} A 7 7 0 0 0 {x + 7} {340 + L} L {x + 7} 340 Z" fill="#9BD14B"/><circle cx="{x - 2}" cy="{340 + L - 2}" r="2.2" fill="#F2FFB0"/>')
    # fire licking up in front of the cauldron's belly, logs and embers
    out.append(f'<path d="M 190 420 C 220 466 380 466 410 420 C 400 460 360 472 300 472 C 240 472 200 460 190 420 Z" fill="#FF8A2A" opacity="0.35"/>')
    rnd2 = random.Random(9)
    for fx, fh, c in ((222, 56, "#E8601A"), (250, 86, "#FF8A2A"), (278, 72, "#FFB23A"), (304, 104, "#FF9A2A"), (330, 80, "#FFB23A"), (356, 92, "#FF8A2A"), (382, 58, "#E8601A")):
        lean = rnd2.uniform(-10, 10)
        out.append(f'<path d="M {fx - 18} 500 C {fx - 22} {500 - fh * 0.45} {fx - 6 + lean} {500 - fh * 0.7} {fx + lean} {500 - fh} C {fx + 6 + lean} {500 - fh * 0.62} {fx + 22} {500 - fh * 0.5} {fx + 17} 500 Z" fill="{c}" opacity="0.92"/>'
                   f'<path d="M {fx - 8} 500 C {fx - 10} {500 - fh * 0.3} {fx + lean * 0.5} {500 - fh * 0.45} {fx + lean * 0.5} {500 - fh * 0.58} C {fx + 6} {500 - fh * 0.32} {fx + 9} {500 - fh * 0.2} {fx + 8} 500 Z" fill="#FFF0A8"/>')
    out.append('<path d="M 206 500 L 394 484 L 398 498 L 210 514 Z" fill="#4A2A18"/><path d="M 210 484 L 390 504 L 386 516 L 204 498 Z" fill="#5A341E"/>'
               '<ellipse cx="394" cy="491" rx="5" ry="7" fill="#C08A5A"/><ellipse cx="206" cy="491" rx="5" ry="7" fill="#C08A5A"/>'
               '<path d="M 230 496 L 260 494 M 300 500 L 340 496" stroke="#FF8A2A" stroke-width="2" opacity="0.8"/>')
    out.append(dots(30, 4, (200, 360, 400, 440), "#FFC45A", r=(1, 2.2), opacity=(0.6, 1)))
    # bubbles on the surface
    rnd = random.Random(3)
    for i in range(14):
        bx, by = rnd.uniform(186, 414), rnd.uniform(304, 330)
        if ((bx - 300) / 136) ** 2 + ((by - 318) / 25) ** 2 > 0.8:
            continue
        br = rnd.uniform(5, 14)
        out.append(f'<circle cx="{bx:.1f}" cy="{by - br * 0.4:.1f}" r="{br:.1f}" fill="#C8F07A" stroke="#E8FFC0" stroke-width="1.6"/>'
                   f'<circle cx="{bx - br * 0.35:.1f}" cy="{by - br * 0.8:.1f}" r="{br * 0.28:.1f}" fill="#FFFFFF" opacity="0.8"/>')
    # a wooden spoon in the brew
    out.append('<path d="M 372 318 L 452 184" stroke="#6A4628" stroke-width="10" stroke-linecap="round"/><path d="M 372 318 L 452 184" stroke="#A8784A" stroke-width="3" stroke-linecap="round" transform="translate(-2 0)" opacity="0.7"/>')
    # green steam rising, with floating sparkles and bubbles
    out.append(defs(lg(f"{u}-st", [(0, "#4E8A2E"), (0.5, "#9BD14B"), (1, "#E8FFC0")], 200, 0, 380, 0, units="userSpaceOnUse")))
    out.append(f'<g opacity="0.42">{puff(u, 296, 304, 250, 4, r0=14, r1=40, drift=-30, n=30, grad=f"{u}-st", hi="#F2FFD8")}</g>')
    for i in range(10):
        bx, by, br = rnd.uniform(180, 420), rnd.uniform(200, 290), rnd.uniform(3, 9)
        out.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{br:.1f}" fill="none" stroke="#D8FF9A" stroke-width="1.6" opacity="0.8"/><circle cx="{bx - br * 0.3:.1f}" cy="{by - br * 0.3:.1f}" r="{br * 0.25:.1f}" fill="#FFF"/>')
    for i in range(8):
        out.append(twinkle(rnd.uniform(160, 440), rnd.uniform(190, 290), rnd.uniform(4, 8), "#F2FFD8", 0.9))
    out.append(vignette(u, strength=0.55))
    out.append(word(300, 124, "witches'", SERIF_IT, 76, BONE, max_w=380, shadow="#000", sdy=4))
    out.append(word(300, 218, "BREW", BEBAS, 120, SLIME, max_w=420, ls=22, glow_col=SLIME, glow_op=0.35, shadow="#0A1404", sdy=6))
    return "\n".join(out)


def puff(u, cx, base, top, seed, r0=10, r1=50, drift=40, n=50, grad=None, hi="#FFFFFF", hi_op=0.5):
    """Rising steam built from clusters of puffs (adapted from places_painted.puff_column)."""
    rnd = random.Random(seed)
    body, lights = [], []
    for i in range(n):
        t = (i / (n - 1)) ** 0.85
        y = base - (base - top) * t
        r = r0 + (r1 - r0) * t ** 0.9
        x = cx + drift * math.sin(t * 3.2) * t
        for _ in range(3):
            a = rnd.uniform(0, 2 * math.pi)
            d = rnd.uniform(0.2, 0.7) * r
            rr = r * rnd.uniform(0.3, 0.5)
            px, py = x + d * math.cos(a), y + d * math.sin(a) * 0.8
            body.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{rr:.1f}"/>')
            if math.sin(a) < 0.2:
                lights.append(f'<circle cx="{px + rr * 0.2:.1f}" cy="{py - rr * 0.25:.1f}" r="{rr * 0.55:.1f}"/>')
    return f'<g fill="url(#{grad})">' + "".join(body) + "</g>" + f'<g fill="{hi}" opacity="{hi_op}">' + "".join(lights) + "</g>"


def rooftops(seed, base, fill, lit=("#FFD27A", "#FFB547"), y0=None):
    """Little town silhouette: gables, a church spire, chimneys, random lit windows."""
    rnd = random.Random(seed)
    out = []
    x = -10
    while x < 610:
        w = rnd.uniform(40, 74)
        h = rnd.uniform(36, 70)
        roof = rnd.uniform(16, 30)
        t = base - h
        out.append(f'<polygon points="{P([(x, base + 60), (x, t), (x + w / 2, t - roof), (x + w, t), (x + w, base + 60)])}" fill="{fill}"/>')
        if rnd.random() < 0.5:
            out.append(f'<rect x="{x + w * 0.7:.1f}" y="{t - roof * 0.8:.1f}" width="7" height="{roof * 0.6:.1f}" fill="{fill}"/>')
        for i in range(rnd.randint(1, 3)):
            if rnd.random() < 0.65:
                wx, wy = x + rnd.uniform(8, w - 18), t + rnd.uniform(8, h - 20)
                out.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="9" height="11" fill="{rnd.choice(lit)}"/>')
        x += w + rnd.uniform(-6, 4)
    return "".join(out)


def d_broom_with_a_view():
    u = "hwbv"
    out = [bg(u, [(0, "#0C0A26"), (0.5, "#24204E"), (1, "#4A2E5E")])]
    out.append(starfield(14, 80, (0, 0, 600, 420), tw=6, avoid=(300, 270, 180)))
    out.append(moon(u, 300, 272, 160, halo_r=1.6, halo_op=0.55, seed=21))
    out.append(cloud_wisp(160, 360, 240, "#9A88C0", 0.5, 4) + cloud_wisp(470, 140, 160, "#9A88C0", 0.35, 6))
    # sparkle trail behind the broom
    rnd = random.Random(8)
    for i in range(22):
        t = i / 21
        x = 160 - 120 * t + rnd.uniform(-8, 8)
        y = 300 + 70 * t * t + rnd.uniform(-10, 10)
        out.append(twinkle(x, y, 3 + 6 * (1 - t), "#FFE7A3", 0.9 - 0.5 * t))
    # broom: handle, binding, bristles
    out.append(defs(lg(f"{u}-br", [(0, "#E8C070"), (1, "#8A5A22")])))
    out.append(f'<g transform="rotate(-14 300 300)">')
    out.append('<rect x="186" y="294" width="290" height="9" rx="4.5" fill="#120C16"/>')
    out.append(f'<path d="M 190 290 L 120 270 Q 90 296 120 326 L 190 308 Z" fill="#120C16"/>')
    out.append('<g stroke="#2A1E26" stroke-width="2.4" stroke-linecap="round">' + "".join(
        f'<line x1="186" y1="{292 + i * 2.2:.1f}" x2="{118 - abs(i - 4) * 3}" y2="{266 + i * 7.6:.1f}"/>' for i in range(9)) + "</g>")
    out.append('<rect x="182" y="288" width="12" height="22" rx="3" fill="#120C16"/>')
    out.append("</g>")
    # the cat in a little witch hat riding along, scarf streaming
    out.append(f'<g transform="rotate(-14 300 300)">')
    out.append(f'<path d="M 300 222 C 260 214 220 232 186 214 C 210 210 236 198 268 204 Z" fill="{ORANGE}"/>'
               f'<path d="M 300 226 C 266 230 236 250 204 244 C 226 236 250 220 276 214 Z" fill="{DEEP_OR}"/>')
    out.append(black_cat(u, 300, 296, 1.2, rim="#F8E9BC", eye="#D9F05A", tail_up=False))
    out.append('<ellipse cx="314" cy="186" rx="30" ry="6" fill="#120C16"/>'
               '<path d="M 298 186 C 300 160 306 140 318 124 C 324 116 336 116 342 122 C 330 124 324 132 324 146 C 326 160 328 176 332 186 Z" fill="#120C16"/>'
               f'<path d="M 299 182 Q 315 186 331 182 L 330 175 Q 315 179 300 175 Z" fill="{PLUM}"/>'
               '<path d="M 342 122 C 334 116 322 118 316 128" fill="none" stroke="#F8E9BC" stroke-width="1.6" opacity="0.7"/>')
    out.append("</g>")
    # little town below
    out.append(rooftops(5, 520, "#120C1C"))
    out.append(f'<polygon points="420,520 420,420 436,386 452,420 452,520" fill="#120C1C"/><line x1="436" y1="386" x2="436" y2="366" stroke="#120C1C" stroke-width="3"/>')
    out.append('<rect x="430" y="426" width="12" height="18" rx="6" fill="#FFD27A"/>')
    out.append(mist(300, 500, 380, 40, "#7A6AA8", f"{u}-tm", 0.35))
    out.append(defs(lg(f"{u}-fg", [(0, "#0A0712", 0), (0.4, "#0A0712", 0.9), (1, "#0A0712", 1)])))
    out.append(f'<rect x="0" y="470" width="600" height="130" fill="url(#{u}-fg)"/>')
    out.append(bat(476, 90, 16, "#120C1C", rot=8, flap=10) + bat(512, 116, 11, "#120C1C", rot=-6, flap=-6))
    out.append(vignette(u, strength=0.45))
    out.append(word(300, 118, "BROOM", BEBAS, 80, BONE, max_w=380, ls=20, shadow="#0A0614", sdy=5))
    out.append(word(300, 544, "with a view", SERIF_IT, 64, AMBER, max_w=420, glow_col=ORANGE, glow_op=0.3, shadow="#000", sdy=3))
    return "\n".join(out)


def hay_bale(u, x, y, w, h, seed):
    rnd = random.Random(seed)
    out = [defs(lg(f"{u}-hay", [(0, "#E8C878"), (0.5, "#C89A48"), (1, "#7A5A28")]),
                f'<clipPath id="{u}-hc"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/></clipPath>'),
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="url(#{u}-hay)"/>']
    strokes = []
    for _ in range(int(w * h / 60)):
        sx, sy = rnd.uniform(x, x + w), rnd.uniform(y, y + h)
        L = rnd.uniform(8, 20)
        a = rnd.uniform(-0.5, 0.5)
        strokes.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{sx + L * math.cos(a):.1f}" y2="{sy + L * math.sin(a):.1f}" stroke="{rnd.choice(["#F6DC90", "#A87A38", "#8A6028", "#FFE8A8"])}"/>')
    out.append(f'<g clip-path="url(#{u}-hc)" stroke-width="1.6" stroke-linecap="round" opacity="0.8">' + "".join(strokes) + "</g>")
    for t in (0.25, 0.75):
        out.append(f'<rect x="{x + w * t - 3:.1f}" y="{y}" width="6" height="{h}" fill="#6A4A22" opacity="0.7"/>')
    # stray straws
    out.append('<g stroke="#E8C878" stroke-width="2" stroke-linecap="round">' + "".join(
        f'<line x1="{x + rnd.uniform(0, w):.1f}" y1="{y + 2:.1f}" x2="{x + rnd.uniform(0, w):.1f}" y2="{y - rnd.uniform(6, 14):.1f}"/>' for _ in range(14)) + "</g>")
    return "".join(out)


def corn_stalk(x, base, h, fill, seed):
    """Dry corn stalk silhouette: thin cane, long arching ribbon leaves, a tassel on top."""
    rnd = random.Random(seed)
    tip = x + rnd.uniform(-8, 8)
    out = [f'<path d="M {x - 2.5} {base} Q {x + 2:.1f} {base - h * 0.5:.1f} {tip:.1f} {base - h:.1f} L {tip + 2:.1f} {base - h:.1f} Q {x + 5:.1f} {base - h * 0.5:.1f} {x + 2.5} {base} Z" fill="{fill}"/>']
    for i in range(7):
        t = 0.18 + i * 0.11
        y = base - h * t
        xx = x + (tip - x) * t
        sgn = 1 if (i + seed) % 2 else -1
        L = h * rnd.uniform(0.28, 0.42) * (1 - t * 0.4)
        out.append(f'<path d="M {xx:.1f} {y:.1f} Q {xx + sgn * L * 0.45:.1f} {y - L * 0.55:.1f} {xx + sgn * L:.1f} {y - L * 0.05 + rnd.uniform(0, L * 0.4):.1f} '
                   f'Q {xx + sgn * L * 0.5:.1f} {y - L * 0.38:.1f} {xx:.1f} {y + 5:.1f} Z" fill="{fill}"/>')
    out.append(f'<g stroke="{fill}" stroke-width="2" stroke-linecap="round" fill="none">' + "".join(
        f'<path d="M {tip:.1f} {base - h:.1f} q {d * 4:.1f} -10 {d * 9:.1f} -14"/>' for d in (-2, -1, 0, 1, 2)) + "</g>")
    if rnd.random() < 0.5:
        ey = base - h * 0.5
        out.append(f'<ellipse cx="{x + 7:.1f}" cy="{ey:.1f}" rx="5" ry="14" transform="rotate(20 {x + 7:.1f} {ey:.1f})" fill="{fill}"/>')
    return "".join(out)


def d_glow_getter():
    u = "hwgg"
    out = [bg(u, [(0, "#0A1424"), (0.55, "#1A2238"), (1, "#24182A")])]
    out.append(starfield(16, 50, (0, 0, 600, 260), tw=4))
    # corn field silhouettes behind
    rnd = random.Random(3)
    for i in range(22):
        x = -10 + i * 29 + rnd.uniform(-6, 6)
        out.append(corn_stalk(x, 470, rnd.uniform(170, 250), "#0E1420" if i % 2 else "#141A2A", i))
    out.append(mist(300, 430, 420, 50, "#5A6A9A", f"{u}-mm", 0.35))
    # ground
    out.append(defs(lg(f"{u}-gd", [(0, "#2A1E1E"), (1, "#0E0A0C")])))
    out.append(f'<path d="M -10 470 Q 300 456 610 470 L 610 600 L -10 600 Z" fill="url(#{u}-gd)"/>')
    out.append(ground_glow(300, 470, 300, 60, "#FF9A3A", f"{u}-gg", 0.5))
    # hay bale and three jack-o'-lanterns with different personalities
    out.append(hay_bale(u, 110, 408, 380, 92, 5))
    out.append(f'<ellipse cx="300" cy="502" rx="196" ry="8" fill="#000" opacity="0.4"/>')
    out.append(pumpkin(u + "a", 186, 362, 140, 100, face="sly", seed=21, leaf=False, stem_lean=-6, glow_r=150))
    out.append(pumpkin(u + "c", 418, 368, 124, 88, face="cute", seed=23, leaf=True, stem_lean=8, glow_r=140, skin=("#FFC36A", "#F29236", "#B85A1E")))
    out.append(pumpkin(u + "b", 300, 316, 180, 130, face="toothy", seed=22, stem_lean=10, glow_r=200, ribs=7))
    out.append(pumpkin(u + "d", 80, 488, 60, 44, seed=24, leaf=False, vine=False, skin=("#F6E6C8", "#E0CCA8", "#A89070")))
    out.append(pumpkin(u + "e", 530, 494, 50, 36, seed=25, leaf=False, vine=False))
    # fireflies
    for i in range(16):
        fx, fy = rnd.uniform(70, 530), rnd.uniform(200, 420)
        out.append(glow(fx, fy, 12, "#E8F07A", f"{u}-ff{i}", 0.8) + f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="2" fill="#FFFFE0"/>')
    out.append(vignette(u, strength=0.55))
    out.append(word(300, 160, "GLOW", BEBAS, 132, AMBER, max_w=380, ls=20, glow_col="#FF8A2A", glow_op=0.45, shadow="#1A0A04", sdy=6))
    out.append(word(300, 222, "getter", SERIF_IT, 72, BONE, max_w=300, shadow="#000", sdy=3))
    return "\n".join(out)



# ---------------------------------------------------------------- candy
def candy_corn(x, y, s, rot=0):
    """Painted candy corn: x, y = centre, s = height."""
    k = s / 60
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f})">'
            '<path d="M -4 -30 Q 0 -34 4 -30 L 24 22 Q 26 30 16 30 L -16 30 Q -26 30 -24 22 Z" fill="#FFF4DC"/>'
            '<path d="M -12 -2 L 12 -2 L 24 22 Q 26 30 16 30 L -16 30 Q -26 30 -24 22 Z" fill="#F28A22"/>'
            '<path d="M -18 14 L 18 14 L 24 22 Q 26 30 16 30 L -16 30 Q -26 30 -24 22 Z" fill="#FFC93A"/>'
            '<path d="M 4 -30 L 24 22 Q 26 30 16 30 L 10 30 Q 18 26 14 16 Z" fill="#000" opacity="0.14"/>'
            '<path d="M -4 -24 L -14 10" stroke="#FFFFFF" stroke-width="3.4" stroke-linecap="round" opacity="0.6"/></g>')


def wrapped(x, y, s, rot, col, stripe, dark=None):
    """Twist-wrapped candy: s = body length."""
    k = s / 60
    dark = dark or "#000"
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f})">'
            f'<path d="M -28 0 L -50 -16 Q -46 0 -50 16 Z M 28 0 L 50 -16 Q 46 0 50 16 Z" fill="{col}"/>'
            f'<path d="M -28 0 L -50 16 Q -46 8 -44 0 Z M 28 0 L 50 16 Q 46 8 44 0 Z" fill="{dark}" opacity="0.25"/>'
            f'<ellipse cx="0" cy="0" rx="30" ry="18" fill="{col}"/>'
            f'<path d="M -16 -16 Q -8 0 -16 16 M 0 -18 Q 8 0 0 18 M 16 -16 Q 24 0 16 16" stroke="{stripe}" stroke-width="5" fill="none"/>'
            f'<path d="M -26 6 Q 0 26 26 6 Q 0 18 -26 6 Z" fill="{dark}" opacity="0.22"/>'
            '<ellipse cx="-10" cy="-8" rx="10" ry="4" fill="#FFFFFF" opacity="0.5"/></g>')


def lollipop(x, y, r, rot, a, b, stick_len=2.2):
    k = r / 20
    sw = "".join(f'<path d="M 0 0 Q {8 * math.cos(math.radians(t)):.1f} {8 * math.sin(math.radians(t)):.1f} {20 * math.cos(math.radians(t + 60)):.1f} {20 * math.sin(math.radians(t + 60)):.1f}" stroke="{b}" stroke-width="5" fill="none"/>' for t in range(0, 360, 72))
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f})">'
            f'<rect x="-2.5" y="14" width="5" height="{20 * stick_len:.0f}" rx="2" fill="#F4EEE4"/>'
            f'<circle cx="0" cy="0" r="20" fill="{a}"/>{sw}<circle cx="0" cy="0" r="20" fill="none" stroke="#000" stroke-width="2" opacity="0.15"/>'
            '<ellipse cx="-7" cy="-8" rx="7" ry="4" transform="rotate(-30 -7 -8)" fill="#FFFFFF" opacity="0.55"/></g>')


def choc_bar(x, y, s, rot, wrap="#6A2E7E", foil="#D8D2E0"):
    k = s / 60
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({k:.3f})">'
            '<rect x="-30" y="-16" width="60" height="32" rx="3" fill="#5A341E"/>'
            '<g stroke="#3A2010" stroke-width="2"><line x1="-10" y1="-16" x2="-10" y2="16"/><line x1="10" y1="-16" x2="10" y2="16"/><line x1="-30" y1="0" x2="30" y2="0"/></g>'
            '<rect x="-28" y="-14" width="16" height="2.4" fill="#8A5A3A"/>'
            f'<path d="M 2 -18 L 34 -18 L 34 18 L 2 18 L 8 10 L 0 4 L 8 -4 L 0 -10 Z" fill="{foil}"/>'
            f'<path d="M 12 -18 L 34 -18 L 34 18 L 12 18 Z" fill="{wrap}"/><rect x="12" y="-6" width="22" height="12" fill="{ORANGE}"/>'
            '<rect x="12" y="-18" width="22" height="4" fill="#FFFFFF" opacity="0.25"/></g>')


def gumball(x, y, r, col):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}"/><circle cx="{x + r * 0.2:.1f}" cy="{y + r * 0.25:.1f}" r="{r * 0.8:.1f}" fill="#000" opacity="0.12"/>'
            f'<circle cx="{x - r * 0.35:.1f}" cy="{y - r * 0.35:.1f}" r="{r * 0.3:.1f}" fill="#FFFFFF" opacity="0.6"/>')


def candy_pail(u, cx, base, w, h):
    """Plastic jack-o'-lantern trick-or-treat pail; returns (back, front) so candy can sit between."""
    top = base - h
    body = (f"M {cx - w * 0.42:.1f} {top:.1f} C {cx - w * 0.56:.1f} {top + h * 0.3:.1f} {cx - w * 0.56:.1f} {base - h * 0.15:.1f} {cx - w * 0.36:.1f} {base:.1f} "
            f"L {cx + w * 0.36:.1f} {base:.1f} C {cx + w * 0.56:.1f} {base - h * 0.15:.1f} {cx + w * 0.56:.1f} {top + h * 0.3:.1f} {cx + w * 0.42:.1f} {top:.1f} Z")
    back = [defs(lg(f"{u}-pl", [(0, "#FFB25A"), (0.45, "#F07F22"), (1, "#A8400E")], 0, 0, 1, 0)),
            f'<path d="M {cx - w * 0.44:.1f} {top + 6:.1f} C {cx - w * 0.4:.1f} {top - h * 0.75:.1f} {cx + w * 0.4:.1f} {top - h * 0.75:.1f} {cx + w * 0.44:.1f} {top + 6:.1f}" fill="none" stroke="#141018" stroke-width="{w * 0.035:.1f}" stroke-linecap="round"/>',
            f'<ellipse cx="{cx:.1f}" cy="{top:.1f}" rx="{w * 0.42:.1f}" ry="{h * 0.1:.1f}" fill="#7A2E0A"/>']
    front = [f'<path d="{body}" fill="url(#{u}-pl)"/>',
             f'<g fill="none" stroke="#B8501A" stroke-width="{w * 0.014:.1f}" opacity="0.7"><path d="M {cx - w * 0.2:.1f} {top + 4:.1f} Q {cx - w * 0.3:.1f} {top + h * 0.5:.1f} {cx - w * 0.18:.1f} {base - 2:.1f}"/><path d="M {cx + w * 0.2:.1f} {top + 4:.1f} Q {cx + w * 0.3:.1f} {top + h * 0.5:.1f} {cx + w * 0.18:.1f} {base - 2:.1f}"/></g>',
             f'<path d="M {cx - w * 0.42:.1f} {top:.1f} A {w * 0.42:.1f} {h * 0.1:.1f} 0 0 0 {cx + w * 0.42:.1f} {top:.1f}" fill="none" stroke="#FFC47A" stroke-width="{w * 0.03:.1f}"/>']
    fy = top + h * 0.5
    for sgn in (-1, 1):
        ex = cx + sgn * w * 0.18
        front.append(f'<polygon points="{P([(ex - w * 0.08, fy - h * 0.02), (ex + w * 0.08, fy - h * 0.02), (ex + sgn * w * 0.02, fy - h * 0.2)])}" fill="#1A1016"/>')
    front.append(f'<path d="M {cx - w * 0.26:.1f} {fy + h * 0.08:.1f} Q {cx:.1f} {fy + h * 0.36:.1f} {cx + w * 0.26:.1f} {fy + h * 0.08:.1f} Q {cx:.1f} {fy + h * 0.2:.1f} {cx - w * 0.26:.1f} {fy + h * 0.08:.1f} Z" fill="#1A1016"/>')
    front.append(f'<path d="M {cx - w * 0.4:.1f} {top + h * 0.2:.1f} Q {cx - w * 0.46:.1f} {top + h * 0.5:.1f} {cx - w * 0.36:.1f} {base - h * 0.15:.1f}" fill="none" stroke="#FFE0B0" stroke-width="{w * 0.03:.1f}" stroke-linecap="round" opacity="0.5"/>')
    return "".join(back), "".join(front)


def scallop_circle(cx, cy, r, n, depth, fill, extra=""):
    pts = []
    for i in range(n * 6):
        a = 2 * math.pi * i / (n * 6)
        rr = r - depth * (0.5 - 0.5 * math.cos(n * a)) ** 2
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return f'<polygon points="{P(pts)}" fill="{fill}"{extra}/>'


def d_official_candy_inspector():
    u = "hwci"
    out = [bg(u, [(0, "#2A1640"), (1, "#160A24")])]
    # scattered candy wallpaper
    rnd = random.Random(7)
    pat = []
    for i in range(40):
        x, y = rnd.uniform(-10, 610), rnd.uniform(-10, 610)
        if math.hypot(x - 300, y - 300) < 250:
            continue
        r = rnd.uniform(-60, 60)
        kind = i % 4
        if kind == 0:
            pat.append(candy_corn(x, y, 30, r))
        elif kind == 1:
            pat.append(wrapped(x, y, 30, r, rnd.choice([ORANGE, SLIME, "#B070E0"]), BONE))
        elif kind == 2:
            pat.append(gumball(x, y, 8, rnd.choice([ORANGE, SLIME, "#B070E0", BONE])))
        else:
            pat.append(twinkle(x, y, 7, AMBER))
    out.append('<g opacity="0.55">' + "".join(pat) + "</g>")
    # the badge: scalloped rim, gold ring, deep centre
    out.append(defs(rg(f"{u}-gold", [(0, "#FFE8A0"), (0.6, "#E0A83A"), (1, "#9A6418")], cx=0.4, cy=0.35, r=0.7),
                    rg(f"{u}-ctr", [(0, "#5A3478"), (0.7, "#2E1A44"), (1, "#1A0E28")], cx=0.5, cy=0.4, r=0.6)))
    out.append('<g transform="translate(300 286) scale(0.9) translate(-300 -298)">')
    out.append(scallop_circle(306, 306, 262, 28, 14, "#0A0612", ' opacity="0.5"'))
    out.append(scallop_circle(300, 298, 262, 28, 14, f"url(#{u}-gold)"))
    out.append(f'<circle cx="300" cy="298" r="232" fill="{BONE}"/><circle cx="300" cy="298" r="226" fill="none" stroke="#9A6418" stroke-width="3"/>')
    out.append(f'<circle cx="300" cy="298" r="168" fill="url(#{u}-ctr)"/><circle cx="300" cy="298" r="168" fill="none" stroke="#9A6418" stroke-width="5"/>'
               f'<circle cx="300" cy="298" r="160" fill="none" stroke="{AMBER}" stroke-width="1.6" stroke-dasharray="2 6" opacity="0.8"/>')
    out.append(arc_word("OFFICIAL", 300, 298, 186, BEBAS, 50, "#2A1640", ls=12, uid=f"{u}-a1"))
    for x in (110, 490):
        out.append(f'<polygon points="{P([(x, 278), (x + 6, 292), (x + 20, 292), (x + 9, 300), (x + 13, 314), (x, 306), (x - 13, 314), (x - 9, 300), (x - 20, 292), (x - 6, 292)])}" fill="{ORANGE}"/>')
    # the overflowing pail inside the badge
    inner = []
    back, front = candy_pail(u, 300, 410, 170, 120)
    inner.append(glow(300, 300, 150, "#FF9A3A", f"{u}-pg", 0.35))
    inner.append(back)
    pile = [lollipop(244, 210, 20, -24, "#B070E0", BONE), lollipop(352, 206, 18, 18, SLIME, BONE),
            choc_bar(300, 254, 66, -8), candy_corn(262, 262, 40, -20), candy_corn(338, 258, 38, 24),
            wrapped(232, 284, 48, 12, ORANGE, BONE, "#7A2E0A"), wrapped(370, 282, 46, -20, "#B070E0", BONE), gumball(300, 286, 12, SLIME),
            gumball(272, 292, 9, ORANGE), gumball(330, 294, 10, BONE), candy_corn(300, 214, 34, 4)]
    inner += pile
    inner.append(front)
    # spilled candy at the base
    inner += [candy_corn(196, 404, 32, -70), wrapped(410, 402, 40, 30, SLIME, BONE, "#2E4A10"), gumball(222, 412, 9, "#B070E0"), candy_corn(388, 418, 26, 60)]
    out.append(defs(f'<clipPath id="{u}-cc"><circle cx="300" cy="298" r="164"/></clipPath>'))
    out.append(f'<g clip-path="url(#{u}-cc)">' + "".join(inner) + "</g>")
    # ribbon across the bottom
    out.append("</g>")
    out.append(ribbon(u, 300, 452, 400, 70, ORANGE, DEEP_OR, tail=36, fold=14))
    out.append(word(300, 474, "CANDY INSPECTOR", BEBAS, 52, "#1A0E24", max_w=350, ls=5))
    return "\n".join(out)


def owl(u, cx, base, s, body=("#B88A5A", "#7A5232", "#3E2818"), disc=("#F2E2C2", "#C8A878"), eye="#FFC23A", blink=False):
    """Painted barn-brown owl perched; (cx, base) = feet. s = 1 -> ~200 px tall."""
    k = s
    out = [defs(rg(f"{u}-ob", [(0, body[0]), (0.6, body[1]), (1, body[2])], cx=0.4, cy=0.35, r=0.7),
                lg(f"{u}-ow", [(0, body[1]), (1, body[2])], 0, 0, 1, 0),
                rg(f"{u}-od", [(0, "#FFF8E8"), (0.7, disc[0]), (1, disc[1])], cx=0.5, cy=0.45, r=0.6),
                rg(f"{u}-oe", [(0, "#FFF2A0"), (0.55, eye), (1, "#C86A10")], cx=0.45, cy=0.4, r=0.6)),
           f'<g transform="translate({cx:.1f} {base:.1f}) scale({k:.3f})">']
    body_p = "M -62 -20 C -78 -80 -70 -150 -40 -176 C -20 -192 20 -192 40 -176 C 70 -150 78 -80 62 -20 C 40 0 -40 0 -62 -20 Z"
    out.append(f'<path d="M -20 -6 L -26 14 L -8 10 Z M 20 -6 L 26 14 L 8 10 Z" fill="{body[2]}"/>')
    out.append(f'<path d="{body_p}" fill="url(#{u}-ob)"/>')
    out.append(defs(f'<clipPath id="{u}-oc"><path d="{body_p}"/></clipPath>'))
    # chest feathers: rows of little chevrons
    feathers = []
    for row in range(7):
        y = -104 + row * 14
        for i in range(-3 + (row % 2) * 0, 4):
            x = i * 15 + (row % 2) * 7.5
            if abs(x) > 44 - row * 2:
                continue
            feathers.append(f'<path d="M {x - 5:.1f} {y:.1f} Q {x:.1f} {y + 6:.1f} {x + 5:.1f} {y:.1f}"/>')
    out.append(f'<ellipse cx="0" cy="-70" rx="46" ry="60" fill="#F2E2C2" opacity="0.55"/>')
    out.append(f'<g fill="none" stroke="{body[1]}" stroke-width="2.4" stroke-linecap="round">' + "".join(feathers) + "</g>")
    # wings
    for sgn in (-1, 1):
        out.append(f'<g transform="scale({sgn} 1)"><path d="M 44 -150 C 76 -120 82 -60 66 -14 C 60 -2 46 0 40 -10 C 52 -50 50 -110 44 -150 Z" fill="url(#{u}-ow)"/>'
                   f'<g stroke="{body[0]}" stroke-width="2" fill="none" opacity="0.6"><path d="M 50 -120 Q 62 -90 58 -50"/><path d="M 58 -110 Q 70 -80 66 -40"/></g>'
                   + "".join(f'<path d="M {48 + (j % 2) * 8} {-128 + j * 18} q 5 4 10 0" stroke="{disc[1]}" stroke-width="2" fill="none" opacity="0.7"/>' for j in range(6)) + "</g>")
    # ear tufts and head
    out.append(f'<path d="M -46 -168 L -58 -206 L -26 -182 Z M 46 -168 L 58 -206 L 26 -182 Z" fill="{body[1]}"/>'
               f'<path d="M -46 -168 L -58 -206 L -40 -190" fill="none" stroke="{body[0]}" stroke-width="2.4"/>')
    # facial disc: two overlapping rounds
    out.append(f'<path d="M 0 -122 C -14 -110 -54 -112 -58 -146 C -60 -176 -28 -186 0 -168 C 28 -186 60 -176 58 -146 C 54 -112 14 -110 0 -122 Z" fill="url(#{u}-od)"/>'
               f'<path d="M 0 -122 C -14 -110 -54 -112 -58 -146 C -60 -176 -28 -186 0 -168 C 28 -186 60 -176 58 -146 C 54 -112 14 -110 0 -122 Z" fill="none" stroke="{body[1]}" stroke-width="3"/>')
    for sgn in (-1, 1):
        ex = sgn * 25
        if blink and sgn > 0:
            out.append(f'<path d="M {ex - 14} -146 Q {ex} -136 {ex + 14} -146" fill="none" stroke="#2A1A10" stroke-width="4" stroke-linecap="round"/>')
            continue
        out.append(f'<circle cx="{ex}" cy="-147" r="18" fill="#2A1A10"/><circle cx="{ex}" cy="-147" r="15.5" fill="url(#{u}-oe)"/>'
                   f'<circle cx="{ex + 1}" cy="-146" r="8.5" fill="#120A06"/><circle cx="{ex - 4}" cy="-152" r="4" fill="#FFFFFF"/><circle cx="{ex + 5}" cy="-141" r="1.8" fill="#FFFFFF" opacity="0.8"/>')
    out.append('<path d="M -6 -136 L 6 -136 L 0 -118 Z" fill="#E8A040"/><path d="M 0 -136 L 6 -136 L 0 -118 Z" fill="#B8701A"/>')
    # feet
    out.append('<g fill="#E8A040">' + "".join(f'<path d="M {x - 3} -6 L {x - 4} 6 Q {x} 10 {x + 4} 6 L {x + 3} -6 Z"/>' for x in (-26, -16, -6, 6, 16, 26)) + "</g>")
    out.append("</g>")
    return "".join(out)


def d_whooos_there():
    u = "hwow"
    out = [bg(u, [(0, "#0A1830"), (0.55, "#1E2A4A"), (1, "#2A1E3A")])]
    out.append(starfield(22, 70, (0, 0, 600, 420), tw=5, avoid=(330, 210, 170)))
    out.append(moon(u, 330, 210, 150, halo_r=1.7, halo_op=0.5, seed=31, base="#F6E4B8"))
    out.append(cloud_wisp(160, 140, 200, "#7A88B8", 0.4, 11) + cloud_wisp(500, 300, 160, "#7A88B8", 0.35, 13))
    # the branch the owl perches on, coming in from the left
    out.append(defs(lg(f"{u}-br", [(0, "#4A3428"), (1, "#1A100C")])))
    out.append(f'<path d="M -20 392 C 120 380 240 390 380 372 C 440 364 500 340 540 316 L 546 326 C 508 352 450 380 384 390 C 250 408 120 404 -20 418 Z" fill="url(#{u}-br)"/>')
    out.append('<path d="M -20 394 C 120 382 240 392 380 374 C 440 366 500 342 540 318" fill="none" stroke="#C8B08A" stroke-width="2" opacity="0.5"/>')
    out.append('<path d="M 430 370 C 460 330 470 300 500 276 M 150 396 C 130 360 110 350 80 338" fill="none" stroke="#2A1A12" stroke-width="7" stroke-linecap="round"/>')
    out.append('<path d="M 470 320 L 494 300 M 100 345 L 76 350" stroke="#2A1A12" stroke-width="4" stroke-linecap="round"/>')
    for x, y, r, c in ((498, 270, -20, "#C2531B"), (78, 330, 30, "#D9A23B"), (520, 300, 50, "#8A2A1A"), (60, 352, -40, "#E07A2A"), (470, 294, 10, "#D9A23B")):
        out.append(maple_leaf(x, y, 15, r, c))
    out.append(maple_leaf(124, 470, 13, 60, "#D9A23B"))
    out.append(owl(u, 286, 396, 1.36))
    out.append(owl(u + "b", 444, 360, 0.56, body=("#9A8A7A", "#6A5A4E", "#3A2E28"), blink=True))
    out.append(defs(lg(f"{u}-fg", [(0, "#0A0712", 0), (0.4, "#0A0712", 0.85), (1, "#0A0712", 1)])))
    out.append(f'<rect x="0" y="420" width="600" height="180" fill="url(#{u}-fg)"/>')
    out.append(vignette(u, strength=0.45))
    out.append(word(300, 486, "whooo's", SERIF_IT, 70, BONE, max_w=380, shadow="#000", sdy=3))
    out.append(word(300, 550, "THERE?", BEBAS, 76, AMBER, max_w=380, ls=18, glow_col="#FF9A3A", glow_op=0.25))
    return "\n".join(out)


def d_eye_of_newt():
    u = "hwen"
    out = [bg(u, [(0, "#14100E"), (1, "#0A0808")])]
    out.append(glow(90, 140, 260, "#FFB547", f"{u}-cg", 0.35))
    out.append(candle(u + "cd", 70, 256, 120, 26, seed=5, glow_r=110))
    out.append('<path d="M -10 300 C 20 300 40 290 52 272" fill="none" stroke="#2A2220" stroke-width="6" stroke-linecap="round"/>'
               '<path d="M 40 256 L 100 256 L 92 268 L 48 268 Z" fill="#3A302A"/><ellipse cx="70" cy="256" rx="30" ry="5" fill="#5A4A3A"/>'
               '<path d="M 44 256 L 96 256" stroke="#FFC45A" stroke-width="1.6" opacity="0.6"/>')
    # the big green bottle
    out.append('<g transform="translate(30 66) scale(0.9)">')
    out.append(defs(lg(f"{u}-gls", [(0, "#2E5A3A"), (0.25, "#4E8A5A"), (0.6, "#1E3E2A"), (1, "#0A1A10")], 0, 0, 1, 0),
                    lg(f"{u}-pp", [(0, "#F6EBCF"), (0.6, "#EAD8AE"), (1, "#C8A870")], 0, 0, 1, 1)))
    out.append('<path d="M 250 60 L 250 120 C 250 150 120 160 112 230 L 104 640 L 496 640 L 488 230 C 480 160 350 150 350 120 L 350 60 Z" fill="url(#hwen-gls)"/>')
    out.append('<path d="M 136 250 C 140 190 210 170 246 156" fill="none" stroke="#B8F0C8" stroke-width="10" stroke-linecap="round" opacity="0.4"/>'
               '<path d="M 130 290 L 126 600" stroke="#B8F0C8" stroke-width="12" stroke-linecap="round" opacity="0.25"/>'
               '<path d="M 470 270 L 474 600" stroke="#FFC45A" stroke-width="5" stroke-linecap="round" opacity="0.25"/>')
    out.append('<rect x="240" y="58" width="120" height="16" rx="6" fill="#3E6A4A"/>'
               '<path d="M 254 60 L 248 16 Q 300 6 352 16 L 346 60 Z" fill="#A8784A"/><path d="M 300 12 L 300 60" stroke="#7A5232" stroke-width="2" opacity="0.4"/>'
               '<path d="M 250 52 Q 300 44 350 52" stroke="#E8D8B0" stroke-width="4" fill="none"/>')
    # twine and a tag
    out.append('<path d="M 254 64 Q 230 90 214 128" fill="none" stroke="#D8C08A" stroke-width="2.4"/>'
               f'<g transform="rotate(-18 200 150)"><path d="M 176 126 L 214 126 L 224 140 L 224 180 L 176 180 Z" fill="{BONE}"/><circle cx="214" cy="137" r="3.4" fill="#2A1E16"/>'
               f'<text x="198" y="166" text-anchor="middle" {CINZEL} font-size="22" fill="#6A2A1A">13</text></g>')
    # the label
    lab = [(130, 236), (470, 236), (470, 236), (470, 540), (130, 540)]
    out.append('<path d="M 140 226 L 460 226 Q 460 244 476 244 L 476 520 Q 460 520 460 538 L 140 538 Q 140 520 124 520 L 124 244 Q 140 244 140 226 Z" fill="#000" opacity="0.35" transform="translate(4 6)"/>')
    out.append(f'<path d="M 140 226 L 460 226 Q 460 244 476 244 L 476 520 Q 460 520 460 538 L 140 538 Q 140 520 124 520 L 124 244 Q 140 244 140 226 Z" fill="url(#{u}-pp)"/>')
    out.append(blobs(10, 4, (140, 240, 460, 530), ["#C8A060", "#B88A50"], r=(14, 40), opacity=(0.08, 0.18), squash=0.8))
    out.append('<path d="M 150 238 L 450 238 Q 450 254 464 254 L 464 510 Q 450 510 450 526 L 150 526 Q 150 510 136 510 L 136 254 Q 150 254 150 238 Z" fill="none" stroke="#5A2A1A" stroke-width="2.4"/>'
               '<path d="M 156 246 L 444 246 Q 444 260 456 260 L 456 504 Q 444 504 444 518 L 156 518 Q 156 504 144 504 L 144 260 Q 156 260 156 246 Z" fill="none" stroke="#5A2A1A" stroke-width="1.2"/>')
    out.append(ruled(300, 282, "APOTHECARY · NO.13", MONO, 18, "#5A2A1A", ls=2, line_w=14, gap=8))
    out.append(word(300, 346, "EYE", CINZEL, 66, "#3E1A10", max_w=300, ls=10))
    out.append(word(300, 376, "of", SERIF_IT, 36, "#8A3A1A", max_w=100))
    out.append(word(300, 436, "NEWT", CINZEL, 66, "#3E1A10", max_w=300, ls=10))
    # a tiny painted newt curling along the bottom of the label
    out.append(defs(lg(f"{u}-nw", [(0, "#F2A03A"), (1, "#C8601A")])))
    out.append(f'<path d="M 214 482 C 240 464 270 470 296 476 C 330 484 360 478 384 466 C 392 462 400 466 396 472 C 380 488 340 496 300 490 C 270 486 240 484 220 494 C 214 498 206 490 214 482 Z" fill="url(#{u}-nw)"/>'
               '<ellipse cx="392" cy="468" rx="12" ry="8" fill="#E8902A"/><circle cx="396" cy="464" r="2.6" fill="#1A0E06"/><circle cx="397" cy="463" r="0.9" fill="#FFF"/>'
               '<g stroke="#C8601A" stroke-width="3" stroke-linecap="round"><path d="M 360 480 L 366 494 M 330 486 L 324 498 M 270 480 L 274 494 M 246 482 L 238 494"/></g>'
               + "".join(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#3E1A08" opacity="0.7"/>' for x, y in ((240, 484), (276, 478), (310, 484), (346, 482), (372, 474))))
    out.append(word(300, 514, "LOCALLY SOURCED", MONO, 18, "#5A2A1A", ls=4, max_w=300))
    # wax seal
    out.append(defs(rg(f"{u}-wx", [(0, "#C84AE0"), (0.6, "#7A2A9A"), (1, "#3A0E4A")], cx=0.4, cy=0.35, r=0.7)))
    out.append(scallop_circle(462, 492, 34, 9, 5, f"url(#{u}-wx)"))
    out.append(f'<circle cx="462" cy="492" r="22" fill="none" stroke="#3A0E4A" stroke-width="2" opacity="0.6"/>'
               f'<polygon points="{P([(462, 476), (466, 487), (478, 487), (468, 494), (472, 506), (462, 499), (452, 506), (456, 494), (446, 487), (458, 487)])}" fill="#E8A8F8" opacity="0.6"/>')
    out.append("</g>")
    out.append(vignette(u, strength=0.5))
    return "\n".join(out)


def d_the_witch_is_in():
    u = "hwwi"
    out = [bg(u, [(0, "#1A1424"), (1, "#0E0A14")])]
    out.append(defs(lg(f"{u}-wd", [(0, "#7A4A2A"), (1, "#3A2012")])))
    # back wall planks
    out.append('<g stroke="#000" stroke-width="2" opacity="0.4">' + "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="600"/>' for x in range(30, 600, 76)) + "</g>")
    out.append(glow(300, 200, 340, "#9BD14B", f"{u}-amb", 0.2))
    # shelf
    out.append(f'<rect x="0" y="282" width="600" height="20" fill="url(#{u}-wd)"/><rect x="0" y="282" width="600" height="3" fill="#C08A5A"/>'
               '<rect x="0" y="302" width="600" height="10" fill="#000" opacity="0.35"/>'
               '<path d="M 60 302 L 60 340 L 96 302 Z M 540 302 L 540 340 L 504 302 Z" fill="#4A2A18"/>')
    # potions of every shape and colour on the shelf
    potions = [(92, 282, 64, 96, ("#E8C8FF", "#B070E0", "#4A1E7A"), True, 0.7),
               (166, 282, 46, 150, ("#C6F27A", SLIME, "#3E6A1E"), False, 0.6),
               (236, 282, 58, 82, ("#FFE0A0", "#FF9A3A", "#A8400E"), True, 0.75),
               (366, 282, 50, 128, ("#A8E0FF", "#4AA8E0", "#1A4A7A"), False, 0.5),
               (436, 282, 70, 104, ("#FFB8D0", "#E0508A", "#7A1A3E"), True, 0.6),
               (512, 282, 40, 120, ("#C6F27A", SLIME, "#3E6A1E"), False, 0.8)]
    for i, (x, b, w, h, liq, rnd_, lvl) in enumerate(potions):
        out.append(bottle(f"{u}-p{i}", x, b, w, h, liquid=liq, round_=rnd_, fill_level=lvl, glow_op=0.4))
    # a candle in the middle, a cobweb corner
    out.append(candle(u + "cd", 300, 282, 74, 24, seed=11, glow_r=110))
    g, dd = web(u, 0, 0, [(10, 170), (30, 180), (50, 176), (70, 168), (88, 150)], [20, 42, 66, 92, 120, 150], 3, col="#D8D0E0", sw=1.4, dew=False)
    out.append(f'<g opacity="0.6">{g}</g>')
    # dried herbs hanging from the top
    for hx, L in ((120, 60), (470, 74)):
        out.append(f'<line x1="{hx}" y1="0" x2="{hx}" y2="{L}" stroke="#C8B08A" stroke-width="2"/>')
        rnd = random.Random(hx)
        out.append('<g stroke-linecap="round">' + "".join(
            f'<path d="M {hx} {L} q {rnd.uniform(-20, 20):.1f} {rnd.uniform(20, 40):.1f} {rnd.uniform(-30, 30):.1f} {rnd.uniform(50, 80):.1f}" stroke="{rnd.choice(["#6A7A3A", "#8A8A4A", "#5A6A2E"])}" stroke-width="3" fill="none"/>' for _ in range(9)) + "</g>")
        out.append(f'<rect x="{hx - 7}" y="{L - 4}" width="14" height="10" rx="2" fill="#A8505A"/>')
    # hanging sign on twine from a nail
    out.append('<circle cx="300" cy="330" r="5" fill="#8A8A90"/><path d="M 170 396 L 300 330 L 430 396" fill="none" stroke="#D8C08A" stroke-width="3"/>')
    out.append(defs(lg(f"{u}-sg", [(0, "#C89A62"), (1, "#8A5A30")])))
    out.append('<rect x="98" y="396" width="404" height="152" rx="14" fill="#000" opacity="0.4" transform="translate(6 8)"/>')
    out.append(f'<rect x="98" y="396" width="404" height="152" rx="14" fill="url(#{u}-sg)"/>')
    out.append('<g stroke="#6A4020" stroke-width="1.6" fill="none" opacity="0.5">' + "".join(
        f'<path d="M 104 {y} q 100 {(-1) ** i * 4} 200 0 t 196 0"/>' for i, y in enumerate((412, 438, 466, 494, 522, 538))) + "</g>")
    out.append('<rect x="110" y="408" width="380" height="128" rx="8" fill="none" stroke="#5A3418" stroke-width="2.4" opacity="0.6"/>')
    for x, y in ((122, 420), (478, 420), (122, 524), (478, 524)):
        out.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#4A3A30"/><circle cx="{x - 1}" cy="{y - 1}" r="1.4" fill="#C8B8A8"/>')
    out.append(word(300, 466, "the witch", SERIF_IT, 58, "#2A1408", max_w=340))
    out.append(word(300, 524, "IS IN", BEBAS, 60, PLUM, max_w=300, ls=16))
    out.append(twinkle(196, 506, 9, PLUM) + twinkle(404, 506, 9, PLUM))
    rnd = random.Random(12)
    out.append("".join(twinkle(rnd.uniform(70, 530), rnd.uniform(150, 270), rnd.uniform(3, 6), "#FFF2C8", rnd.uniform(0.5, 0.9)) for _ in range(10)))
    out.append(vignette(u, strength=0.5))
    return "\n".join(out)



def tombstone(u, x, base, w, h, kind="round", col=("#9A94A8", "#6A6478", "#3A3648"), moss=True, seed=1, tilt=0):
    rnd = random.Random(seed)
    top = base - h
    if kind == "round":
        d = f"M {x - w / 2:.1f} {base:.1f} L {x - w / 2:.1f} {top + w / 2:.1f} A {w / 2:.1f} {w / 2:.1f} 0 0 1 {x + w / 2:.1f} {top + w / 2:.1f} L {x + w / 2:.1f} {base:.1f} Z"
    elif kind == "cross":
        a = w * 0.18
        d = (f"M {x - a:.1f} {base:.1f} L {x - a:.1f} {top + h * 0.42:.1f} L {x - w / 2:.1f} {top + h * 0.42:.1f} L {x - w / 2:.1f} {top + h * 0.22:.1f} L {x - a:.1f} {top + h * 0.22:.1f} "
             f"L {x - a:.1f} {top:.1f} L {x + a:.1f} {top:.1f} L {x + a:.1f} {top + h * 0.22:.1f} L {x + w / 2:.1f} {top + h * 0.22:.1f} L {x + w / 2:.1f} {top + h * 0.42:.1f} L {x + a:.1f} {top + h * 0.42:.1f} L {x + a:.1f} {base:.1f} Z")
    else:  # peaked
        d = f"M {x - w / 2:.1f} {base:.1f} L {x - w / 2:.1f} {top + w * 0.3:.1f} L {x:.1f} {top:.1f} L {x + w / 2:.1f} {top + w * 0.3:.1f} L {x + w / 2:.1f} {base:.1f} Z"
    out = [defs(lg(f"{u}", [(0, col[0]), (0.6, col[1]), (1, col[2])], 0, 0, 1, 0), f'<clipPath id="{u}-c"><path d="{d}"/></clipPath>'),
           f'<g transform="rotate({tilt} {x:.1f} {base:.1f})">',
           f'<path d="{d}" fill="url(#{u})"/>',
           f'<g clip-path="url(#{u}-c)">']
    if kind != "cross":
        out.append(f'<path d="M {x - w * 0.28:.1f} {top + h * 0.42:.1f} L {x + w * 0.28:.1f} {top + h * 0.42:.1f} M {x - w * 0.22:.1f} {top + h * 0.55:.1f} L {x + w * 0.22:.1f} {top + h * 0.55:.1f}" stroke="{col[2]}" stroke-width="{max(1.5, w * 0.04):.1f}" opacity="0.6"/>')
        out.append(f'<path d="M {x - w * 0.1:.1f} {top + h * 0.2:.1f} L {x + w * 0.1:.1f} {top + h * 0.2:.1f} M {x:.1f} {top + h * 0.12:.1f} L {x:.1f} {top + h * 0.32:.1f}" stroke="{col[2]}" stroke-width="{max(1.5, w * 0.05):.1f}" opacity="0.5"/>')
    if moss:
        out.append(blobs(int(4 + w / 8), seed, (x - w / 2, base - h * 0.25, x + w / 2, base), ["#4E6A2E", "#6A8A3A", "#3E5A26"], r=(w * 0.06, w * 0.16), opacity=(0.5, 0.9)))
    out.append(f'<path d="M {x + w * 0.1:.1f} {top + h * 0.1:.1f} l {w * 0.06:.1f} {h * 0.12:.1f} l {-w * 0.05:.1f} {h * 0.08:.1f}" stroke="{col[2]}" stroke-width="1.6" fill="none" opacity="0.7"/>')
    out.append("</g>")
    out.append(f'<path d="{d}" fill="none" stroke="#E8E0F0" stroke-width="1.6" opacity="0.25"/>')
    out.append("</g>")
    return "".join(out)


def d_enter_if_you_dare():
    u = "hwed"
    out = [bg(u, [(0, "#0E1226"), (0.5, "#262648"), (1, "#3A3456")])]
    out.append(starfield(30, 60, (0, 0, 600, 300), tw=4, avoid=(300, 250, 110)))
    out.append(moon(u, 300, 250, 92, halo_r=2.4, halo_op=0.5, seed=41))
    # the graveyard beyond the gate, receding into mist
    poly, far = hill([(-20, 380), (200, 370), (420, 376), (620, 368)], 5, 600, "#3A3658")
    out.append(tree_row(17, far, 10, 80, 140, "#3A3658", depth=5))
    out.append(poly)
    out.append(mist(300, 382, 420, 50, "#B8B0D8", f"{u}-m1", 0.45))
    for i, (x, b, w, h, k, c) in enumerate(((216, 412, 30, 46, "round", ("#8A86A8", "#6A6688", "#4A4668")), (360, 410, 26, 52, "cross", ("#8A86A8", "#6A6688", "#4A4668")),
                                            (300, 420, 36, 50, "peaked", ("#8A86A8", "#6A6688", "#4A4668")), (420, 424, 34, 48, "round", ("#9A94A8", "#6A6478", "#4A4658")),
                                            (180, 432, 40, 56, "round", ("#9A94A8", "#6A6478", "#3A3648")))):
        out.append(tombstone(f"{u}-t{i}", x, b, w, h, k, col=c, seed=i, tilt=(i % 3 - 1) * 4))
    out.append(mist(300, 430, 400, 40, "#C8C0E8", f"{u}-m2", 0.4))
    # ground and path through the gate
    out.append(defs(lg(f"{u}-gd", [(0, "#2A2638"), (1, "#0E0C16")])))
    out.append(f'<rect x="0" y="430" width="600" height="170" fill="url(#{u}-gd)"/>')
    out.append('<path d="M 270 430 L 330 430 L 420 600 L 180 600 Z" fill="#4A4258" opacity="0.7"/>')
    out.append(dots(80, 3, (190, 440, 410, 600), "#2A2236", r=(2, 5), opacity=(0.4, 0.8)))
    # stone pillars with lanterns
    out.append(defs(lg(f"{u}-st", [(0, "#8A8098"), (0.5, "#5A5268"), (1, "#2E2838")], 0, 0, 1, 0)))
    for i, px in enumerate((96, 504)):
        out.append(f'<rect x="{px - 34}" y="250" width="68" height="300" fill="url(#{u}-st)"/>')
        out.append('<g stroke="#1E1828" stroke-width="2" opacity="0.6">' + "".join(
            f'<line x1="{px - 34}" y1="{y}" x2="{px + 34}" y2="{y}"/><line x1="{px + (-10 if (y // 34) % 2 else 12)}" y1="{y}" x2="{px + (-10 if (y // 34) % 2 else 12)}" y2="{y + 34}"/>' for y in range(270, 550, 34)) + "</g>")
        out.append(f'<rect x="{px - 42}" y="236" width="84" height="18" fill="#6A6278"/><rect x="{px - 42}" y="236" width="84" height="4" fill="#B8B0C8"/>')
        out.append(lantern(f"{u}-l{i}", px, 160, 1.0, glow_r=110, glow_op=0.6, handle=True))
        out.append(f'<rect x="{px - 18}" y="232" width="36" height="6" fill="#1E1828"/>')
        # warm light on pillar faces
        out.append(mist(px, 290, 40, 60, "#FFB547", f"{u}-lp{i}", 0.25))
    # the iron gate, one leaf ajar
    bars = []
    for i, x in enumerate(range(146, 456, 18)):
        if 296 < x < 304:
            continue
        top = 200 + 60 * (1 - ((x - 300) / 160) ** 2) * -1 + 60
        bars.append(f'<line x1="{x}" y1="{top:.1f}" x2="{x}" y2="520"/>'
                    f'<path d="M {x - 5} {top + 4:.1f} L {x} {top - 12:.1f} L {x + 5} {top + 4:.1f} Z" fill="#0E0A14" stroke="none"/>')
    out.append('<g stroke="#0E0A14" stroke-width="5">' + "".join(bars) + "</g>")
    out.append('<g fill="none" stroke="#0E0A14" stroke-width="6"><path d="M 140 300 Q 300 200 460 300"/><line x1="140" y1="330" x2="460" y2="330"/><line x1="140" y1="490" x2="460" y2="490"/>'
               '<line x1="140" y1="250" x2="140" y2="524"/><line x1="460" y1="250" x2="460" y2="524"/><line x1="300" y1="236" x2="300" y2="524"/></g>')
    # scroll curls in the band
    curls = "".join(f'<path d="M {x} 330 c 0 -16 18 -16 18 -4 c 0 8 -10 8 -10 2"/><path d="M {x + 36} 330 c 0 -16 -18 -16 -18 -4 c 0 8 10 8 10 2"/>' for x in (150, 222, 306, 378))
    out.append(f'<g fill="none" stroke="#0E0A14" stroke-width="4">{curls}</g>')
    out.append('<g fill="none" stroke="#FFB547" stroke-width="1.6" opacity="0.5"><path d="M 140 300 Q 220 250 300 236"/><line x1="142" y1="252" x2="142" y2="520"/><line x1="458" y1="252" x2="458" y2="520"/></g>')
    # iron arch plate with the word
    out.append(f'<path d="M 150 200 Q 300 120 450 200 L 450 216 Q 300 140 150 216 Z" fill="#0E0A14"/>')
    out.append(arc_word("ENTER", 300, 330, 196, CINZEL, 62, BONE, ls=14, uid=f"{u}-arc", outline="#0E0A14", ow=8))
    out.append(bat(300, 118, 18, "#0E0A14", rim="#C8C0E8", flap=12))
    # front mist rolling across
    out.append(mist(160, 530, 260, 50, "#C8C0E8", f"{u}-m3", 0.4) + mist(460, 540, 240, 46, "#C8C0E8", f"{u}-m4", 0.35))
    out.append(vignette(u, strength=0.5))
    out.append(word(300, 520, "if you dare", SERIF_IT, 70, AMBER, max_w=400, glow_col="#1A0E24", glow_op=0.6, shadow="#0A0614", sdy=4))
    return "\n".join(out)


def d_home_sweet_haunt():
    u = "hwhs"
    out = [bg(u, [(0, "#101830"), (0.55, "#2A2A52"), (1, "#3E2E5A")])]
    out.append(starfield(33, 70, (0, 0, 600, 300), tw=5, avoid=(470, 230, 70)))
    out.append(moon(u, 476, 236, 50, halo_r=2.8, halo_op=0.45, seed=51))
    # forest clearing
    poly, far = hill([(-20, 400), (160, 386), (360, 396), (620, 384)], 6, 600, "#2A2848")
    out.append(tree_row(18, far, 12, 90, 160, "#2A2848", depth=5))
    out.append(poly)
    out.append(mist(300, 400, 400, 40, "#8A80B8", f"{u}-m1", 0.35))
    out.append(defs(lg(f"{u}-gd", [(0, "#24203A"), (1, "#0E0C18")])))
    out.append(f'<path d="M -20 430 Q 300 410 620 430 L 620 600 L -20 600 Z" fill="url(#{u}-gd)"/>')
    # the crooked cottage
    out.append(defs(lg(f"{u}-wl", [(0, "#8A7A8A"), (1, "#4A3E52")], 0, 0, 1, 0),
                    lg(f"{u}-rf", [(0, "#4A2E5A"), (1, "#1E1228")]),
                    rg(f"{u}-win", [(0, "#FFF4C0"), (0.6, "#FFC45A"), (1, "#E07A22")])))
    out.append(glow(300, 400, 220, "#FFB547", f"{u}-hg", 0.3))
    out.append('<path d="M 196 470 L 202 352 L 404 344 L 410 470 Z" fill="url(#hwhs-wl)"/>')
    # timber frame
    out.append('<g stroke="#2A1E26" stroke-width="7" stroke-linecap="round"><path d="M 202 352 L 404 344"/><path d="M 200 410 L 408 404"/><path d="M 252 350 L 250 470"/><path d="M 356 346 L 360 470"/><path d="M 204 360 L 250 404 M 404 352 L 358 400"/></g>')
    # chimney with curling smoke
    out.append('<path d="M 352 300 L 350 230 L 382 228 L 386 300 Z" fill="#6A4A4A"/><rect x="344" y="222" width="46" height="12" fill="#4A3434"/>')
    out.append(f'<g opacity="0.55">{puff(u, 366, 214, 70, 7, r0=8, r1=26, drift=40, n=24, grad=f"{u}-smk", hi="#E8E0F0")}</g>')
    out.append(defs(lg(f"{u}-smk", [(0, "#6A6488"), (1, "#C8C0E0")], 0, 0, 1, 0)))
    # drooping witch-hat roof with shingles
    roof = "M 176 362 C 196 330 230 290 262 250 C 280 228 290 196 300 160 C 304 190 330 200 340 214 C 370 260 410 320 430 352 C 360 368 250 370 176 362 Z"
    out.append(f'<path d="{roof}" fill="url(#{u}-rf)"/>')
    out.append(defs(f'<clipPath id="{u}-rc"><path d="{roof}"/></clipPath>'))
    sh = []
    for row, y in enumerate(range(200, 372, 14)):
        for x in range(150 + (row % 2) * 9, 450, 18):
            sh.append(f'<path d="M {x} {y} q 9 10 18 0"/>')
    out.append(f'<g clip-path="url(#{u}-rc)" fill="none" stroke="#120A1A" stroke-width="2" opacity="0.55">' + "".join(sh) + "</g>")
    out.append('<path d="M 300 160 C 304 190 330 200 340 214 C 370 260 410 320 430 352" fill="none" stroke="#C8B8F0" stroke-width="2" opacity="0.6"/>')
    out.append('<path d="M 300 160 C 310 146 330 142 340 150" fill="none" stroke="#2A1838" stroke-width="7" stroke-linecap="round"/>')
    # windows: round attic window, two cottage windows, round door
    out.append(glow(300, 300, 50, "#FFB547", f"{u}-aw", 0.55) + f'<circle cx="300" cy="300" r="20" fill="url(#{u}-win)"/><path d="M 300 280 L 300 320 M 280 300 L 320 300" stroke="#2A1E26" stroke-width="4"/><circle cx="300" cy="300" r="20" fill="none" stroke="#2A1E26" stroke-width="5"/>')
    for i, (wx, wy) in enumerate(((216, 418), (372, 414))):
        out.append(glow(wx + 14, wy + 16, 46, "#FFB547", f"{u}-wg{i}", 0.5))
        out.append(f'<rect x="{wx}" y="{wy}" width="30" height="34" rx="4" fill="url(#{u}-win)"/><path d="M {wx + 15} {wy} L {wx + 15} {wy + 34} M {wx} {wy + 17} L {wx + 30} {wy + 17}" stroke="#2A1E26" stroke-width="3.4"/>'
                   f'<rect x="{wx}" y="{wy}" width="30" height="34" rx="4" fill="none" stroke="#2A1E26" stroke-width="4"/><rect x="{wx - 4}" y="{wy + 34}" width="38" height="6" fill="#5A3A2E"/>')
    out.append(f'<path d="M 280 470 L 280 432 A 24 24 0 0 1 328 432 L 328 470 Z" fill="#5A2E3A"/><path d="M 286 470 L 286 434 A 18 18 0 0 1 322 434 L 322 470 Z" fill="#7A3A46"/>'
               f'<circle cx="314" cy="448" r="3" fill="#E9B949"/><path d="M 304 418 L 304 470" stroke="#5A2E3A" stroke-width="2"/>')
    # door lantern, broom leaning, pumpkins, path, cat on the roof ridge
    out.append(lantern(f"{u}-ln", 262, 410, 0.42, glow_r=80, glow_op=0.6, handle=False))
    out.append('<path d="M 418 474 L 446 380" stroke="#6A4628" stroke-width="5" stroke-linecap="round"/><path d="M 410 476 L 426 444 L 438 448 L 432 482 Z" fill="#C8A060"/>'
               '<g stroke="#8A6A3A" stroke-width="1.6"><path d="M 416 474 L 428 450 M 422 478 L 432 452 M 428 480 L 436 454"/></g>')
    out.append('<path d="M 280 470 C 270 500 250 520 230 600 L 330 600 C 330 540 336 500 328 470 Z" fill="#3E3448"/>')
    out.append(dots(40, 7, (240, 480, 330, 600), "#2A2236", r=(3, 6), opacity=(0.5, 0.9)))
    out.append(pumpkin(u + "p1", 150, 496, 62, 44, face="classic", seed=31, leaf=False, vine=False, glow_r=80))
    out.append(pumpkin(u + "p2", 474, 500, 72, 50, face="cute", seed=32, leaf=True, glow_r=90))
    out.append(pumpkin(u + "p3", 524, 512, 40, 30, seed=33, leaf=False, vine=False, skin=("#F6E6C8", "#E0CCA8", "#A89070")))
    out.append(black_cat(u, 400, 340, 0.42, rim="#E8E0FF"))
    # crooked picket fence
    fence = []
    for i, x in enumerate(list(range(70, 180, 22)) + list(range(452, 560, 22))):
        tilt = ((i * 37) % 9 - 4)
        fence.append(f'<g transform="rotate({tilt} {x} 500)"><path d="M {x - 6} 500 L {x - 6} 456 L {x} 446 L {x + 6} 456 L {x + 6} 500 Z" fill="#4A4058"/><path d="M {x - 6} 456 L {x} 446" stroke="#C8B8F0" stroke-width="1.4" opacity="0.6"/></g>')
    out.append("".join(fence) + '<g stroke="#4A4058" stroke-width="5"><line x1="60" y1="470" x2="186" y2="468"/><line x1="442" y1="468" x2="566" y2="472"/></g>')
    out.append(grass(120, 5, (-10, 470, 610, 520), ["#2E2846", "#3A3456", "#221E36"], h=(6, 16), sw=2))
    out.append(bat(130, 250, 18, "#120C1C", rot=-10, flap=8) + bat(176, 224, 12, "#120C1C", rot=6, flap=-4))
    out.append(defs(lg(f"{u}-fg", [(0, "#0A0712", 0), (0.4, "#0A0712", 0.8), (1, "#0A0712", 1)])))
    out.append(f'<rect x="0" y="0" width="600" height="160" fill="url(#{u}-fg)" transform="rotate(180 300 80)"/>')
    out.append(defs(lg(f"{u}-bt", [(0, "#0A0712", 0), (0.5, "#0A0712", 0.75), (1, "#0A0712", 0.95)])))
    out.append(f'<rect x="0" y="480" width="600" height="120" fill="url(#{u}-bt)"/>')
    out.append(vignette(u, strength=0.45))
    out.append(word(300, 114, "home sweet", SERIF_IT, 62, BONE, max_w=400, shadow="#000", sdy=3))
    out.append(word(300, 548, "HAUNT", BEBAS, 74, AMBER, max_w=400, ls=26, glow_col="#FF9A3A", glow_op=0.3, shadow="#0A0614", sdy=4))
    return "\n".join(out)


def cute_bat(u, cx, feet_y, s, fur=("#9A7AB8", "#5A4072", "#2A1C40"), wing=("#2E2244", "#120A1E"), rim="#D8C8FF"):
    """Fluffy bat hanging upside down by its toes from (cx, feet_y), wings folded like a cloak; s = 1 -> ~190 px."""
    out = [defs(rg(f"{u}-fur", [(0, fur[0]), (0.6, fur[1]), (1, fur[2])], cx=0.45, cy=0.6, r=0.7),
                lg(f"{u}-wg", [(0, wing[0]), (1, wing[1])], 0, 0, 1, 0),
                lg(f"{u}-wg2", [(0, wing[1]), (1, wing[0])], 0, 0, 1, 0),
                rg(f"{u}-ear", [(0, "#F0A8C0"), (1, "#8A4A6A")]))]
    # drawn directly in hanging orientation: toes at y=0, head at the bottom
    g = ['<g stroke="#1A1028" stroke-width="5" stroke-linecap="round" fill="none"><path d="M -10 14 L -12 -2 Q -12 -8 -6 -8"/><path d="M 10 14 L 12 -2 Q 12 -8 6 -8"/></g>']
    # body between the wings
    g.append(f'<ellipse cx="0" cy="70" rx="34" ry="58" fill="url(#{u}-fur)"/>')
    g.append(dots(50, 5, (-26, 20, 26, 120), "#D8C0F0", r=(0.6, 1.5), opacity=(0.3, 0.7)))
    # folded wings: scalloped edges at the top (they hang down from the wrists)
    for sgn, grad in ((-1, f"{u}-wg"), (1, f"{u}-wg2")):
        w = (f"M {sgn * 6} 22 C {sgn * 40} 6 {sgn * 66} 18 {sgn * 72} 44 Q {sgn * 62} 38 {sgn * 58} 50 Q {sgn * 66} 66 {sgn * 66} 86 "
             f"Q {sgn * 56} 82 {sgn * 54} 96 Q {sgn * 58} 116 {sgn * 48} 134 C {sgn * 36} 150 {sgn * 20} 146 {sgn * 14} 128 C {sgn * 22} 100 {sgn * 22} 60 {sgn * 6} 22 Z")
        g.append(f'<path d="{w}" fill="url(#{grad})"/>')
        g.append(f'<g stroke="#5A4878" stroke-width="2.2" fill="none" opacity="0.8"><path d="M {sgn * 70} 44 L {sgn * 20} 118"/><path d="M {sgn * 64} 84 L {sgn * 22} 122"/><path d="M {sgn * 50} 130 L {sgn * 24} 124"/></g>')
        g.append(f'<path d="M {sgn * 6} 22 C {sgn * 40} 6 {sgn * 66} 18 {sgn * 72} 44" fill="none" stroke="{rim}" stroke-width="2.2" opacity="0.7"/>')
        g.append(f'<circle cx="{sgn * 70}" cy="44" r="3.4" fill="#1A1028"/>')
    # head at the bottom, upside down: ears point down, smile reads as a frown flipped
    g.append(f'<path d="M -30 150 L -46 206 L -8 174 Z M 30 150 L 46 206 L 8 174 Z" fill="{fur[2]}"/>'
             f'<path d="M -28 158 L -38 194 L -14 174 Z M 28 158 L 38 194 L 14 174 Z" fill="url(#{u}-ear)"/>')
    g.append(f'<ellipse cx="0" cy="150" rx="42" ry="36" fill="url(#{u}-fur)"/>')
    g.append('<path d="M -40 140 Q -30 112 0 114 Q 30 112 40 140" fill="none" stroke="#D8C0F0" stroke-width="2" opacity="0.5"/>')
    g.append('<ellipse cx="-15" cy="156" rx="9.5" ry="11" fill="#1A1024"/><ellipse cx="15" cy="156" rx="9.5" ry="11" fill="#1A1024"/>'
             '<circle cx="-12" cy="160" r="3.6" fill="#FFFFFF"/><circle cx="18" cy="160" r="3.6" fill="#FFFFFF"/>'
             '<circle cx="-17" cy="152" r="1.6" fill="#FFFFFF" opacity="0.8"/><circle cx="13" cy="152" r="1.6" fill="#FFFFFF" opacity="0.8"/>'
             '<path d="M -4 138 L 4 138 L 0 134 Z" fill="#E88AA8"/>'
             '<path d="M -11 132 Q 0 124 11 132" fill="none" stroke="#1A1024" stroke-width="2.6" stroke-linecap="round"/>'
             '<path d="M -6 130 L -4 124 L -2 130" fill="#FFFFFF"/>'
             '<ellipse cx="-27" cy="140" rx="7" ry="4" fill="#F29AB4" opacity="0.6"/><ellipse cx="27" cy="140" rx="7" ry="4" fill="#F29AB4" opacity="0.6"/>')
    out.append(f'<g transform="translate({cx:.1f} {feet_y:.1f}) scale({s:.3f})">' + "".join(g) + "</g>")
    return "".join(out)


def d_hang_in_there():
    u = "hwhi"
    out = [bg(u, [(0, "#1A1036"), (0.55, "#2E1E4E"), (1, "#3A2246")])]
    out.append(starfield(35, 70, (0, 0, 600, 440), tw=6, avoid=(300, 270, 160)))
    out.append(moon(u, 300, 268, 150, halo_r=1.7, halo_op=0.45, seed=61))
    out.append(cloud_wisp(470, 370, 200, "#8A70B0", 0.45, 3) + cloud_wisp(120, 330, 160, "#8A70B0", 0.35, 5))
    # the branch: crooked, from the left edge, with a few leaves
    out.append(defs(lg(f"{u}-br", [(0, "#5A3E34"), (1, "#20140E")])))
    out.append(f'<path d="M -20 108 C 100 100 200 120 320 112 C 400 106 470 80 560 54 L 566 66 C 480 96 410 124 322 130 C 200 138 100 124 -20 134 Z" fill="url(#{u}-br)"/>')
    out.append('<path d="M -20 108 C 100 100 200 120 320 112 C 400 106 470 80 560 54" fill="none" stroke="#C8A88A" stroke-width="2" opacity="0.45"/>')
    out.append('<path d="M 420 98 C 450 70 470 50 500 40 M 160 116 C 150 90 130 80 110 76" fill="none" stroke="#2A1A12" stroke-width="6" stroke-linecap="round"/>')
    for x, y, r, c in ((112, 74, -30, "#D9A23B"), (500, 40, 30, "#C2531B"), (470, 110, 160, "#8A2A1A"), (90, 136, 150, "#E07A2A")):
        out.append(maple_leaf(x, y, 14, r, c))
    out.append(cute_bat(u, 300, 120, 1.36))
    out.append(maple_leaf(124, 330, 13, 40, "#D9A23B"))
    out.append('<path d="M 132 312 q 14 -14 4 -34" fill="none" stroke="#E8C08A" stroke-width="1.6" stroke-dasharray="2 6" opacity="0.6"/>')
    out.append(defs(lg(f"{u}-fg", [(0, "#0A0712", 0), (0.4, "#0A0712", 0.8), (1, "#0A0712", 1)])))
    out.append(f'<rect x="0" y="400" width="600" height="200" fill="url(#{u}-fg)"/>')
    out.append(vignette(u, strength=0.45))
    out.append(word(300, 478, "hang in", SERIF_IT, 66, BONE, max_w=380, shadow="#000", sdy=3))
    out.append(word(300, 548, "THERE", BEBAS, 76, "#D8B8FF", max_w=400, ls=26, glow_col="#B88AFF", glow_op=0.3, shadow="#0A0614", sdy=4))
    return "\n".join(out)


def d_ghouls_night_out():
    u = "hwgn"
    out = [bg(u, [(0, "#0C1028"), (0.5, "#24204A"), (1, "#3A2A50")])]
    out.append(starfield(36, 60, (0, 0, 600, 300), tw=5, avoid=(300, 262, 80)))
    out.append(moon(u, 300, 262, 56, halo_r=2.8, halo_op=0.5, seed=71))
    # a little old street receding to the moon: two rows of houses
    out.append(defs(lg(f"{u}-rd", [(0, "#4A4060"), (1, "#16121E")])))
    out.append('<polygon points="292,352 308,352 600,600 0,600" fill="url(#hwgn-rd)"/>')
    # cobbles
    rnd = random.Random(4)
    cob = []
    for row in range(16):
        t = row / 15
        y = 356 + (600 - 356) * t ** 1.6
        half = 8 + 300 * t ** 1.6
        n = int(4 + 18 * t)
        for i in range(n):
            x = 300 - half + (2 * half) * (i + 0.5 + (row % 2) * 0.5) / n
            cob.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{half / n * 0.8:.1f}" ry="{2 + 8 * t ** 1.6:.1f}" fill="#5A5070" opacity="{0.25 + 0.3 * t:.2f}"/>')
    out.append("".join(cob))
    for sgn in (-1, 1):
        rows = []
        for k in range(6):
            t0, t1 = k / 6, (k + 1) / 6
            z0, z1 = 0.12 + 0.88 * t0 ** 1.5, 0.12 + 0.88 * t1 ** 1.5
            x0, x1 = 300 + sgn * (10 + 300 * z0), 300 + sgn * (10 + 300 * z1)
            b0, b1 = 352 + 248 * z0, 352 + 248 * z1
            h0, h1 = 50 + 300 * z0, 50 + 300 * z1
            col = ["#2A2240", "#241C38", "#30264A"][k % 3]
            out.append(f'<polygon points="{P([(x0, b0), (x0, b0 - h0), (x1, b1 - h1), (x1, b1)])}" fill="{col}"/>')
            out.append(f'<polygon points="{P([(x0, b0 - h0), (x1, b1 - h1), (x1, b1 - h1 + 6 + 10 * z1), (x0, b0 - h0 + 6 + 10 * z0)])}" fill="#4A3E66" opacity="0.8"/>')
            if k % 2 == 0:
                cxm = x0 + (x1 - x0) * 0.6
                cy_ = b0 + (b1 - b0) * 0.6 - (h0 + (h1 - h0) * 0.6)
                cw = abs(x1 - x0) * 0.12
                out.append(f'<rect x="{cxm - cw / 2:.1f}" y="{cy_ - cw * 1.6:.1f}" width="{cw:.1f}" height="{cw * 1.7:.1f}" fill="{col}"/>')
            # glowing doorway at street level
            tt = 0.5
            dx_ = x0 + (x1 - x0) * tt
            db = b0 + (b1 - b0) * tt
            dh = (h0 + (h1 - h0) * tt) * 0.15
            dw = abs(x1 - x0) * 0.26
            if k % 2:
                out.append(glow(dx_, db - dh / 2, dh, "#FFB547", f"{u}-d{sgn + 1}{k}", 0.4) + f'<rect x="{dx_ - dw / 2:.1f}" y="{db - dh:.1f}" width="{dw:.1f}" height="{dh:.1f}" fill="#FFB860"/>')
            for j in range(2):
                for f in range(2):
                    tt = 0.25 + 0.45 * j
                    xx = x0 + (x1 - x0) * tt
                    bb = b0 + (b1 - b0) * tt
                    hh = h0 + (h1 - h0) * tt
                    ww = abs(x1 - x0) * 0.16
                    wy = bb - hh * (0.35 + 0.32 * f)
                    on = rnd.random() < 0.6
                    out.append(f'<rect x="{xx - ww / 2:.1f}" y="{wy:.1f}" width="{ww:.1f}" height="{ww * 1.3:.1f}" fill="{"#FFC864" if on else "#1A1428"}"/>')
                    if on:
                        out.append(glow(xx, wy + ww * 0.6, ww * 1.8, "#FFB547", f"{u}-w{sgn + 1}{k}{j}{f}", 0.35))
    # string lights across the street
    for i, (y, sag) in enumerate(((150, 40), (210, 30))):
        pts = [(x, y + sag * (1 - ((x - 300) / 300) ** 2)) for x in range(0, 601, 20)]
        out.append(f'<polyline points="{P(pts)}" fill="none" stroke="#120C1A" stroke-width="2"/>')
        for j, (x, yy) in enumerate(pts[1::2]):
            c = [ORANGE, SLIME, "#B070E0", AMBER][(j + i) % 4]
            out.append(glow(x, yy + 7, 14, c, f"{u}-sl{i}{j}", 0.6) + f'<ellipse cx="{x}" cy="{yy + 7:.1f}" rx="3.6" ry="5.4" fill="{c}"/><circle cx="{x - 1}" cy="{yy + 5:.1f}" r="1.4" fill="#FFF"/>')
    # the ghouls out on the town, each with a light
    out.append(mist(300, 470, 300, 40, "#C8C0E8", f"{u}-gm", 0.3))
    out.append(ghost(u + "c", 410, 312, 74, lean=0.3, face="happy", arms=True, glow_op=0.2))
    out.append(lantern(u + "lc", 458, 352, 0.42, glow_r=60))
    out.append(ghost(u + "b", 176, 300, 104, lean=0.35, face="boo", arms=True, glow_op=0.25, flip=True))
    out.append(candle(u + "cb", 110, 376, 24, 10, seed=3, glow_r=44))
    out.append(ghost(u + "a", 300, 318, 140, lean=0.35, face="happy", arms=True, glow_op=0.3))
    out.append(f'<path d="M 386 384 Q 394 390 394 398" stroke="#22181A" stroke-width="2" fill="none"/>')
    out.append(lantern(u + "la", 394, 396, 0.62, glow_r=80))
    # party hat on the front ghoul
    out.append(f'<path d="M 278 326 L 302 270 L 322 328 Z" fill="{SLIME}"/><path d="M 290 300 L 314 302 M 284 316 L 318 318" stroke="#FFFFFF" stroke-width="3" opacity="0.7"/><circle cx="302" cy="268" r="6.5" fill="{AMBER}"/>')
    out.append(defs(lg(f"{u}-fg", [(0, "#0A0712", 0), (0.4, "#0A0712", 0.8), (1, "#0A0712", 1)])))
    out.append(f'<rect x="0" y="0" width="600" height="160" fill="url(#{u}-fg)" transform="rotate(180 300 80)"/>')
    out.append(f'<rect x="0" y="470" width="600" height="130" fill="url(#{u}-fg)"/>')
    out.append(vignette(u, strength=0.5))
    out.append(word(300, 116, "ghouls'", SERIF_IT, 66, BONE, max_w=400, shadow="#000", sdy=3))
    out.append(word(300, 548, "NIGHT OUT", BEBAS, 66, AMBER, max_w=440, ls=16, glow_col="#FF9A3A", glow_op=0.3, shadow="#0A0614", sdy=4))
    return "\n".join(out)


def scarecrow(u, cx, base, s):
    """Friendly scarecrow on a post: straw hat, button eyes, patched plaid shirt, straw cuffs."""
    out = [defs(lg(f"{u}-sh", [(0, "#C2531B"), (1, "#7A2A10")], 0, 0, 1, 0), lg(f"{u}-ht", [(0, "#E8C070"), (1, "#9A6A2A")]))]
    g = [f'<rect x="-6" y="-250" width="12" height="250" fill="#5A3A22"/><rect x="-120" y="-196" width="240" height="11" fill="#5A3A22"/>']
    # straw tufts at the cuffs
    for sgn in (-1, 1):
        g.append('<g stroke="#E8C070" stroke-width="3" stroke-linecap="round">' + "".join(
            f'<line x1="{sgn * 104}" y1="{-192 + j * 3}" x2="{sgn * (118 + (j % 3) * 6)}" y2="{-200 + j * 7}"/>' for j in range(5)) + "</g>")
    # shirt
    g.append(f'<path d="M -104 -204 L -40 -214 L 40 -214 L 104 -204 L 104 -178 L 46 -176 L 50 -86 Q 0 -78 -50 -86 L -46 -176 L -104 -178 Z" fill="url(#{u}-sh)"/>')
    g.append('<g stroke="#4A1A08" stroke-width="2.4" opacity="0.6">' + "".join(f'<line x1="{x}" y1="-214" x2="{x}" y2="-84"/>' for x in range(-40, 50, 16))
             + "".join(f'<line x1="-104" y1="{y}" x2="104" y2="{y}"/>' for y in (-198, -186)) + "".join(f'<line x1="-48" y1="{y}" x2="48" y2="{y}"/>' for y in range(-170, -86, 18)) + "</g>")
    g.append('<rect x="18" y="-150" width="26" height="24" fill="#5A7A3A" transform="rotate(8 31 -138)"/><path d="M 20 -148 l 22 0 M 20 -130 l 22 0" stroke="#E8D8A8" stroke-width="1.6" stroke-dasharray="3 3" transform="rotate(8 31 -138)"/>')
    g.append('<g stroke="#E8C070" stroke-width="3" stroke-linecap="round">' + "".join(f'<line x1="{x}" y1="-86" x2="{x + (x % 7) - 3}" y2="-66"/>' for x in range(-44, 48, 8)) + "</g>")
    # sack head
    g.append('<ellipse cx="0" cy="-244" rx="38" ry="36" fill="#E2C89A"/><ellipse cx="10" cy="-240" rx="28" ry="30" fill="#C8A878" opacity="0.4"/>'
             '<circle cx="-13" cy="-248" r="6" fill="#2A1A10"/><circle cx="13" cy="-248" r="6" fill="#2A1A10"/>'
             '<path d="M -12 -254 l 2 2 m 24 -2 l 2 2" stroke="#FFF" stroke-width="2"/>'
             '<path d="M -16 -228 Q 0 -218 16 -228" fill="none" stroke="#2A1A10" stroke-width="2.6"/>'
             '<path d="M -12 -230 l 0 4 M -4 -226 l 0 4 M 4 -226 l 0 4 M 12 -230 l 0 4" stroke="#2A1A10" stroke-width="1.6"/>'
             '<path d="M -4 -240 L 4 -240 L 0 -234 Z" fill="#E07A2A"/>'
             '<path d="M -20 -210 Q 0 -202 20 -210 L 16 -200 Q 0 -196 -16 -200 Z" fill="#8A6A3A"/>')
    # hat
    g.append(f'<ellipse cx="0" cy="-272" rx="62" ry="12" fill="url(#{u}-ht)"/><path d="M -32 -274 Q -30 -312 0 -314 Q 30 -312 32 -274 Z" fill="url(#{u}-ht)"/>'
             f'<path d="M -32 -282 Q 0 -276 32 -282 L 32 -274 Q 0 -268 -32 -274 Z" fill="{PLUM}"/>'
             '<g stroke="#8A5A22" stroke-width="1.4" opacity="0.6">' + "".join(f'<line x1="{x}" y1="-310" x2="{x * 1.1:.0f}" y2="-276"/>' for x in range(-24, 30, 8)) + "</g>")
    out.append(f'<g transform="translate({cx:.1f} {base:.1f}) scale({s:.3f})">' + "".join(g) + "</g>")
    return "".join(out)


def crow(x, y, s, flip=False, fill="#140E14"):
    sx = -s if flip else s
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({sx:.3f} {s:.3f})">'
            f'<path d="M -20 -4 C -16 -18 0 -22 10 -14 L 22 -16 L 12 -10 C 12 0 4 6 -6 6 L -26 10 Z" fill="{fill}"/>'
            f'<path d="M -2 -14 C -10 -8 -14 0 -22 6 C -10 4 0 -2 6 -8 Z" fill="#2A2230"/><circle cx="8" cy="-14" r="1.6" fill="#E8E0C8"/>'
            f'<path d="M -2 6 L -4 12 M 4 4 L 4 12" stroke="{fill}" stroke-width="2"/></g>')


def d_happy_haunting():
    u = "hwhp"
    out = [bg(u, [(0, "#2A1A48"), (0.35, "#8A3A5A"), (0.65, "#E8723A"), (0.85, "#F6B060"), (1, "#F8C878")])]
    out.append(starfield(37, 30, (0, 0, 600, 140), tw=3))
    # the harvest moon rising, huge and orange
    out.append(moon(u, 300, 336, 128, base="#FFC878", shade="#E8904A", halo="#FFD28A", halo_r=1.9, halo_op=0.55, seed=81))
    out.append(cloud_wisp(150, 250, 220, "#C8607A", 0.5, 3) + cloud_wisp(480, 200, 180, "#C8607A", 0.4, 9))
    # distant farm: barn, silo, trees
    poly, far = hill([(-20, 400), (150, 392), (330, 398), (620, 388)], 7, 600, "#5A2A3E")
    out.append(poly)
    out.append('<g fill="#3E1A2E"><polygon points="430,396 430,350 462,326 494,350 494,396"/><rect x="498" y="320" width="26" height="76"/><ellipse cx="511" cy="320" rx="13" ry="8"/></g>'
               '<rect x="454" y="368" width="16" height="28" fill="#FFC864"/><path d="M 454 368 L 470 396 M 470 368 L 454 396" stroke="#3E1A2E" stroke-width="2"/>')
    out.append(tree_row(19, far, 6, 50, 90, "#4A1E34", xmin=-20, xmax=200, depth=5))
    # pumpkin field in rows
    out.append(defs(lg(f"{u}-fd", [(0, "#4A2A2A"), (1, "#1A0E10")])))
    out.append(f'<rect x="0" y="400" width="600" height="200" fill="url(#{u}-fd)"/>')
    out.append('<g fill="none" stroke="#2E4A1E" stroke-width="3" opacity="0.8">' + "".join(
        f'<path d="M -10 {y} C 150 {y - 6} 450 {y + 6} 610 {y}"/>' for y in (414, 436, 466, 504)) + "</g>")
    rnd = random.Random(8)
    for i in range(14):
        row = i % 4
        y = (418, 440, 470, 508)[row]
        x = rnd.uniform(20, 580)
        if 250 < x < 350 and row > 1:
            continue
        w = (16, 24, 34, 48)[row]
        out.append(pumpkin(f"{u}-f{i}", x, y - w * 0.3, w, w * 0.72, seed=i, leaf=row > 1, vine=False, stem_lean=3))
    out.append(grass(160, 6, (-10, 400, 610, 600), ["#3E5A26", "#5A6A2E", "#2E3E1E", "#7A6A2E"], h=(6, 16), sw=2))
    # the scarecrow and his crow friends
    out.append(scarecrow(u, 300, 520, 1.0))
    out.append(crow(208, 324, 1.4) + crow(380, 318, 1.3, flip=True) + crow(404, 314, 1.1, flip=True))
    out.append('<g fill="none" stroke="#2A1A2A" stroke-width="2.4" stroke-linecap="round"><path d="M 120 190 q 8 -6 15 0 q 7 -6 15 0"/><path d="M 470 140 q 6 -5 11 0 q 5 -5 11 0"/></g>')
    out.append(pumpkin(u + "fr", 160, 520, 88, 62, face="classic", seed=91, glow_r=100))
    out.append(pumpkin(u + "fr2", 452, 528, 70, 50, face="sly", seed=92, glow_r=90, leaf=False))
    out.append(defs(lg(f"{u}-tp", [(0, "#1A0E30", 0.75), (1, "#1A0E30", 0)])))
    out.append(f'<rect width="600" height="200" fill="url(#{u}-tp)"/>')
    out.append(vignette(u, "#1A0810", strength=0.5))
    out.append(word(300, 110, "happy", SERIF_IT, 62, BONE, max_w=360, shadow="#1A0A1A", sdy=3))
    out.append(word(300, 198, "HAUNTING", BEBAS, 88, "#FFE0A8", max_w=460, ls=12, shadow="#4A1A2A", sdy=5))
    return "\n".join(out)


def wolf(x, base, s, fill="#0E0C1A", rim=None):
    """Howling wolf sitting in profile facing right, muzzle raised to the moon."""
    body = [(-50, 0), (-58, -26), (-54, -54), (-44, -74), (-34, -92), (-28, -110), (-26, -124), (-30, -150), (-16, -134),
            (-6, -138), (6, -140), (18, -150), (30, -164), (36, -166), (34, -158), (26, -148), (32, -146), (24, -140),
            (14, -134), (10, -124), (14, -116), (8, -108), (14, -100), (8, -92), (14, -84), (12, -70), (14, -40), (16, -8),
            (26, -6), (28, 0), (4, 0), (2, -30), (-4, -2), (-12, 0)]
    tail = [(-48, -4), (-64, -2), (-80, -6), (-96, -4), (-104, -10), (-94, -14), (-84, -12), (-70, -16), (-56, -14)]
    out = (f'<g transform="translate({x:.1f} {base:.1f}) scale({s:.3f})"><polygon points="{P(tail)}" fill="{fill}" stroke="{fill}" stroke-width="3" stroke-linejoin="round"/>'
           f'<polygon points="{P(body)}" fill="{fill}" stroke="{fill}" stroke-width="2" stroke-linejoin="round"/>')
    if rim:
        out += f'<polyline points="{P(body[1:13])}" fill="none" stroke="{rim}" stroke-width="{2.2 / s:.2f}" opacity="0.85" stroke-linejoin="round"/>'
    return out + "</g>"


def d_full_moon_club():
    u = "hwfm"
    out = [bg(u, [(0, "#0E1A2A"), (1, "#081018")])]
    # tartan-ish twill outside the patch
    out.append('<g stroke="#1E2E44" stroke-width="10" opacity="0.5">' + "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="600"/><line x1="0" y1="{x}" x2="600" y2="{x}"/>' for x in range(20, 600, 60)) + "</g>")
    out.append('<g stroke="#3A2A50" stroke-width="3" opacity="0.6">' + "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="600"/><line x1="0" y1="{x}" x2="600" y2="{x}"/>' for x in range(50, 600, 60)) + "</g>")
    # the embroidered patch
    out.append('<circle cx="304" cy="306" r="248" fill="#000" opacity="0.45"/>')
    out.append(f'<circle cx="300" cy="300" r="248" fill="{PLUM}"/><circle cx="300" cy="300" r="248" fill="none" stroke="#2E1640" stroke-width="10"/>')
    out.append('<circle cx="300" cy="300" r="242" fill="none" stroke="#C8A0E0" stroke-width="2.4" stroke-dasharray="6 5" opacity="0.8"/>')
    out.append(f'<circle cx="300" cy="300" r="186" fill="#1A2440"/>')
    out.append(defs(f'<clipPath id="{u}-pc"><circle cx="300" cy="300" r="186"/></clipPath>',
                    lg(f"{u}-sky", [(0, "#0E1830"), (0.6, "#2A3A6A"), (1, "#4A4A7A")])))
    inner = [f'<rect x="100" y="100" width="400" height="400" fill="url(#{u}-sky)"/>',
             starfield(41, 40, (110, 110, 490, 340), tw=4, avoid=(320, 270, 104)),
             moon(u, 320, 270, 96, halo_r=1.6, halo_op=0.5, seed=91)]
    poly, rl = hill([(100, 420), (200, 404), (300, 410), (420, 396), (500, 404)], 3, 520, "#14182A")
    inner.append(tree_row(12, rl, 12, 50, 90, "#14182A", xmin=100, xmax=500, depth=4))
    from paint import conifer
    for i, x in enumerate((128, 152, 172, 452, 474)):
        inner.append(conifer(x, 430, 80 + (i * 17) % 40, "#10142A", i))
    inner.append(poly)
    # rocky outcrop and the howling wolf, moon-rimmed
    inner.append('<path d="M 170 500 L 196 410 Q 230 380 280 384 L 330 396 L 360 440 L 380 500 Z" fill="#1E2236"/>'
                 '<path d="M 196 410 Q 230 380 280 384 L 330 396" fill="none" stroke="#C8C0E0" stroke-width="2" opacity="0.6"/>'
                 '<path d="M 240 420 L 260 470 M 300 410 L 320 460" stroke="#0E1020" stroke-width="3" opacity="0.6"/>')
    inner.append(wolf(268, 390, 0.98, rim="#F8E9BC"))
    inner.append(mist(300, 460, 200, 30, "#8A90C8", f"{u}-m", 0.35))
    out.append(f'<g clip-path="url(#{u}-pc)">' + "".join(inner) + "</g>")
    out.append('<circle cx="300" cy="300" r="186" fill="none" stroke="#F4EBD9" stroke-width="6"/><circle cx="300" cy="300" r="194" fill="none" stroke="#2E1640" stroke-width="3"/>')
    # stitched lettering around the ring
    out.append(arc_word("FULL MOON CLUB", 300, 300, 206, BEBAS, 46, BONE, ls=10, uid=f"{u}-a1"))
    out.append(arc_word("HOWL · SINCE · DUSK", 300, 300, 230, MONO, 20, "#E8C8FF", ls=5, uid=f"{u}-a2", top=False))
    for a in (-8, 188):
        x, y = 300 + 218 * math.cos(math.radians(a)), 300 + 218 * math.sin(math.radians(a))
        out.append(twinkle(x, y, 10, AMBER))
    return "\n".join(out)


BUILD = {
    "boo": d_boo,
    "spooky-season": d_spooky_season,
    "happy-halloween": d_happy_halloween,
    "trick-or-treat": d_trick_or_treat,
    "here-for-the-boos": d_here_for_the_boos,
    "witch-please": d_witch_please,
    "creep-it-real": d_creep_it_real,
    "stay-spooky": d_stay_spooky,
    "haunted-hotel": d_haunted_hotel,
    "witches-brew": d_witches_brew,
    "broom-with-a-view": d_broom_with_a_view,
    "glow-getter": d_glow_getter,
    "official-candy-inspector": d_official_candy_inspector,
    "whooos-there": d_whooos_there,
    "eye-of-newt": d_eye_of_newt,
    "the-witch-is-in": d_the_witch_is_in,
    "enter-if-you-dare": d_enter_if_you_dare,
    "home-sweet-haunt": d_home_sweet_haunt,
    "hang-in-there": d_hang_in_there,
    "ghouls-night-out": d_ghouls_night_out,
    "happy-haunting": d_happy_haunting,
    "full-moon-club": d_full_moon_club,
}


def build(only=None):
    for slug, fn in BUILD.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:])
