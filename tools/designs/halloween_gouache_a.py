"""Halloween, gouache edition (set A): the Halloween magnets repainted by hand, like a storybook gouache
illustration -- night skies laid in with visible brush strokes, moon and candlelight glowing through layered
washes, inked silhouettes, dry-brush highlights, lettering filled with brush texture, paper grain on top.
Cute-spooky and family friendly. Run: python3 halloween_gouache_a.py [slug ...]"""
import math
import random
import sys

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure, save
from gouache import blob, blob_pts, grain, hay_bale, ink, jitter, painted_pumpkin, paper, smooth_closed, smooth_open, strokes, wash
from paint import P, lg, rg, rough, y_on
from poster import ANTON
from halloween_painted import FACES, bat, crow, gnarly_tree

COL = "halloween"

# ---------------------------------------------------------------- shared palette (kept in step with set B)
NIGHT0 = "#120E26"     # inky purple-navy, deepest
NIGHT1 = "#1E1840"
NIGHT2 = "#2E2560"
VIOLET = "#46377A"
DUSK = "#6B5196"
LILAC = "#A994D2"
SIL = "#150F22"        # painted silhouette
SIL2 = "#211832"
INKN = "#0B0714"       # night ink line
INKB = "#3A2418"       # warm brown ink (paper pieces)
PUMP = "#E8792E"
PUMP_D = "#B9531E"
PUMP_L = "#F8A85A"
GOLD = "#FFC24A"
CANDLE = "#FFE7A3"
FLAME = "#FFF6D6"
SLIME = "#9BD14B"
SLIME_D = "#5C8A2C"
BONE = "#F3E8D2"
BONE_D = "#D9C9A8"
MOON = "#F7E7B8"


# ---------------------------------------------------------------- colour helpers
def _rgb(c):
    c = c.lstrip("#")
    return [int(c[i:i + 2], 16) for i in (0, 2, 4)]


def _hex(v):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(x)))) for x in v)


def mix(a, b, t):
    A, B = _rgb(a), _rgb(b)
    return _hex([A[i] + (B[i] - A[i]) * t for i in range(3)])


def lighten(c, t):
    return mix(c, "#FFFFFF", t)


def darken(c, t):
    return mix(c, "#000000", t)


def grad_at(stops, t):
    t = max(0.0, min(1.0, t))
    for (o1, c1), (o2, c2) in zip(stops, stops[1:]):
        if o1 <= t <= o2:
            return mix(c1, c2, (t - o1) / max(1e-6, o2 - o1))
    return stops[-1][1] if t > stops[-1][0] else stops[0][1]


def vary(c, rnd, amt=0.12):
    k = rnd.uniform(-amt, amt)
    c = lighten(c, k) if k > 0 else darken(c, -k)
    # a whisper of hue drift, like pigment that was not fully mixed
    drift = rnd.choice(["#7A5AB0", "#3A5A9A", "#9A5A8A", "#5A4A9A"])
    return mix(c, drift, rnd.uniform(0, 0.08))


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


# ---------------------------------------------------------------- brush marks
def _lens(x, y, L, w, a, bend, color, op):
    dx, dy = L * math.cos(a), L * math.sin(a)
    nx, ny = -math.sin(a), math.cos(a)
    mx, my = x + dx / 2 + nx * bend, y + dy / 2 + ny * bend
    return (f'<path d="M {x:.1f} {y:.1f} Q {mx + nx * w:.1f} {my + ny * w:.1f} {x + dx:.1f} {y + dy:.1f} '
            f'Q {mx - nx * w:.1f} {my - ny * w:.1f} {x:.1f} {y:.1f} Z" fill="{color}" opacity="{op:.2f}"/>')


def sky(u, stops, seed, box=(0, 0, 600, 600), n=420, angle=-4, length=(40, 140), width=(4, 12), op=(0.22, 0.55),
        swirl=None, amt=0.12):
    """Painted night sky: graded wash, then hundreds of brush strokes whose colour is sampled from the
    gradient at their own height (so the paint stays coherent), optionally swirling round a moon."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = [defs(lg(f"{u}-sk", stops), f'<clipPath id="{u}-skc"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath>'),
           f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="url(#{u}-sk)"/><g clip-path="url(#{u}-skc)">']
    for _ in range(n):
        x, y = rnd.uniform(x0 - 60, x1), rnd.uniform(y0 - 6, y1 + 6)
        col = vary(grad_at(stops, (y - y0) / max(1, y1 - y0)), rnd, amt * rnd.uniform(0.6, 1.4))
        a = math.radians(angle + rnd.uniform(-9, 9))
        L = rnd.uniform(*length)
        if swirl:
            sx, sy, r0, r1, tint = swirl
            dd = math.hypot(x - sx, y - sy)
            if r0 < dd < r1:
                a = math.atan2(y - sy, x - sx) + math.pi / 2 + rnd.uniform(-0.15, 0.15)
                L *= 0.7
                col = mix(col, tint, 0.22 * (1 - (dd - r0) / (r1 - r0)))
        out.append(_lens(x, y, L, rnd.uniform(*width), a, L * rnd.uniform(-0.12, 0.12), col, rnd.uniform(*op)))
    out.append("</g>")
    return "".join(out)


def tex(u, d, colors, seed, box, n=None, angle=-90, length=(10, 30), width=(1.5, 4.5), op=(0.2, 0.5), curve=0.2):
    if n is None:
        n = min(360, int((box[2] - box[0]) * (box[3] - box[1]) / 260))
    return strokes(u, d, box, colors, seed, n=max(8, n), angle=angle, length=length, width=width, opacity=op, curve=curve)


def inside(u, d, content):
    return f'<clipPath id="{u}"><path d="{d}"/></clipPath><g clip-path="url(#{u})">{content}</g>'


def pshape(u, d, base, tints, seed, box, angle=-90, n=None, length=(10, 30), width=(1.5, 4.5), op=(0.2, 0.5), curve=0.2,
           line=None, lw=2.2, shade=None, light=None):
    """A painted object: wash fill, form-following strokes in related tints, optional shade/light side, ink line.
    shade/light = (color, opacity, dx, dy): an offset copy of the shape clipped inside it, so one side darkens."""
    out = [wash(d, base, seed, 2, 0.9, 0.5)]
    if shade or light:
        g = []
        for spec in (shade, light):
            if spec:
                c, o, dx, dy = spec
                g.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{abs(dx) + abs(dy):.1f}" opacity="{o}" transform="translate({dx} {dy})"/>')
                g.append(f'<path d="{d}" fill="{c}" opacity="{o * 0.5:.2f}" transform="translate({dx * 1.6:.1f} {dy * 1.6:.1f})"/>')
        out.append(inside(f"{u}-sd", d, "".join(g)))
    out.append(tex(f"{u}-tx", d, tints, seed + 1, box, n, angle, length, width, op, curve))
    if line:
        out.append(ink(d, line, lw, seed + 2, 2, 0.85))
    return "".join(out)


def hpath(pts, seed, amt=1.0, closed=True):
    """Hand-drawn polyline: corners stay corners, each edge bows a little like a pen line."""
    rnd = random.Random(seed)
    pts = [(x + rnd.uniform(-amt * 0.5, amt * 0.5), y + rnd.uniform(-amt * 0.5, amt * 0.5)) for x, y in pts]
    seq = pts + [pts[0]] if closed else pts
    d = [f"M {seq[0][0]:.1f} {seq[0][1]:.1f}"]
    for (xa, ya), (xb, yb) in zip(seq, seq[1:]):
        L = math.hypot(xb - xa, yb - ya) or 1
        nx, ny = -(yb - ya) / L, (xb - xa) / L
        b = rnd.uniform(-1, 1) * amt * min(1.6, L / 40)
        d.append(f"Q {(xa + xb) / 2 + nx * b:.1f} {(ya + yb) / 2 + ny * b:.1f} {xb:.1f} {yb:.1f}")
    return " ".join(d) + (" Z" if closed else "")


def soft(cx, cy, rx, ry, color, u, strength=0.8, mid=0.45):
    return (defs(rg(u, [(0, color, strength), (mid, color, strength * 0.45), (1, color, 0)])) +
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#{u})"/>')


def pglow(u, cx, cy, r, color, strength=0.8, seed=1, rings=2):
    """Painted glow: a soft radial wash plus a couple of uneven blob halos, like glazes laid round a light."""
    out = [soft(cx, cy, r, r, color, f"{u}-g", strength)]
    for i in range(rings):
        k = 0.45 + i * 0.25
        out.append(f'<path d="{blob(cx, cy, r * k, r * k * 0.96, seed + i, 0.14, 14)}" fill="{color}" opacity="{0.035 + 0.02 * (rings - i):.3f}"/>')
    return "".join(out)


def twinkle(x, y, r, col, op=1.0, rot=0):
    k = r * 0.18
    return (f'<path d="M {x:.1f} {y - r:.1f} Q {x + k:.1f} {y - k:.1f} {x + r * 0.9:.1f} {y:.1f} Q {x + k:.1f} {y + k:.1f} {x:.1f} {y + r * 1.05:.1f} '
            f'Q {x - k:.1f} {y + k:.1f} {x - r * 0.85:.1f} {y:.1f} Q {x - k:.1f} {y - k:.1f} {x:.1f} {y - r:.1f} Z" fill="{col}" opacity="{op:.2f}" '
            f'transform="rotate({rot:.0f} {x:.1f} {y:.1f})"/>')


def stars(seed, n, box, col=CANDLE, tw=6, avoid=(), r=(0.8, 2.2), twr=(4, 8)):
    """Painted stars: uneven dabs of light, a few four-point twinkles, each with a faint halo."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box

    def ok(x, y):
        return all(math.hypot(x - ax, y - ay) > ar for ax, ay, ar in avoid)

    out = []
    k = 0
    while k < n:
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if not ok(x, y):
            continue
        k += 1
        rr = rnd.uniform(*r)
        out.append(f'<path d="{blob(x, y, rr, rr * rnd.uniform(0.7, 1), rnd.randrange(999), 0.2, 7)}" fill="{col}" opacity="{rnd.uniform(0.45, 1):.2f}"/>')
    k = 0
    while k < tw:
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if not ok(x, y):
            continue
        k += 1
        rr = rnd.uniform(*twr)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr * 1.4:.1f}" fill="{col}" opacity="0.12"/>' + twinkle(x, y, rr, col, rnd.uniform(0.8, 1), rnd.uniform(-10, 10)))
    return "".join(out)


def moon(u, cx, cy, r, seed, base=MOON, shade="#D8BC7E", hi="#FFFBEA", halo="#FFE9B0", halo_r=1.75, halo_op=0.42, line="#B8955A"):
    """Gouache moon: layered halo glazes, an uneven disc, curved strokes, soft seas and a pooled edge."""
    rnd = random.Random(seed)
    d = blob(cx, cy, r, r, seed, 0.018, 24)
    out = [pglow(f"{u}-h", cx, cy, r * halo_r, halo, halo_op, seed, rings=3),
           soft(cx, cy, r * 1.18, r * 1.18, halo, f"{u}-hc", 0.45, 0.7)]
    out.append(wash(d, base, seed, 2, 0.8, 0.6))
    g = [soft(cx - r * 0.25, cy - r * 0.3, r * 0.9, r * 0.9, hi, f"{u}-lit", 0.7)]
    for _ in range(5):
        a, dd = rnd.uniform(0, 6.28), rnd.uniform(0.1, 0.62) * r
        g.append(f'<path d="{blob(cx + dd * math.cos(a), cy + dd * math.sin(a), r * rnd.uniform(0.16, 0.32), r * rnd.uniform(0.12, 0.24), rnd.randrange(999), 0.15, 12)}" fill="{shade}" opacity="{rnd.uniform(0.25, 0.42):.2f}"/>')
    for _ in range(int(5 + r / 18)):
        a, dd = rnd.uniform(0, 6.28), rnd.uniform(0, 0.85) * r
        rr = r * rnd.uniform(0.03, 0.08)
        x, y = cx + dd * math.cos(a), cy + dd * math.sin(a)
        g.append(f'<path d="{blob(x, y, rr, rr * 0.85, rnd.randrange(999), 0.12, 9)}" fill="{shade}" opacity="0.55"/>'
                 f'<path d="M {x - rr * 0.8:.1f} {y + rr * 0.5:.1f} q {rr * 0.8:.1f} {rr * 0.7:.1f} {rr * 1.6:.1f} 0" stroke="{hi}" stroke-width="{max(1, rr * 0.35):.1f}" fill="none" opacity="0.7" stroke-linecap="round"/>')
    # curved brush strokes that follow the sphere
    for _ in range(int(r * 1.1)):
        a = rnd.uniform(0, 6.28)
        dd = rnd.uniform(0.1, 0.95) * r
        x, y = cx + dd * math.cos(a), cy + dd * math.sin(a)
        L = rnd.uniform(0.15, 0.4) * r
        g.append(_lens(x, y, L, rnd.uniform(0.012, 0.03) * r, a + math.pi / 2, L * 0.15, rnd.choice([hi, shade, base, "#EED39A"]), rnd.uniform(0.2, 0.5)))
    g.append(f'<path d="{d}" fill="none" stroke="{shade}" stroke-width="{r * 0.3:.1f}" opacity="0.35" transform="translate({r * 0.12:.1f} {r * 0.14:.1f})"/>')
    out.append(inside(f"{u}-mc", d, "".join(g)))
    out.append(ink(d, line, max(1.4, r * 0.016), seed, 2, 0.45))
    return "".join(out)


def cloud(u, cx, cy, w, h, seed, col, hi, op=0.85, rim=None):
    """Wispy painted cloud: a soft glaze, then long horizontal brush strokes stacked thicker in the middle,
    lit along the top edge, frayed at the ends (dry brush)."""
    rnd = random.Random(seed)
    out = [f'<g opacity="{op}">', soft(cx, cy, w * 0.55, h * 1.4, col, f"{u}-cg", 0.5)]
    for _ in range(int(w / 4)):
        t = rnd.uniform(-1, 1)
        x = cx + t * w / 2 - rnd.uniform(0, 40)
        y = cy + rnd.uniform(-h, h) * (1 - abs(t) * 0.6)
        L = rnd.uniform(30, 90) * (1 - abs(t) * 0.5)
        top = y < cy - h * 0.3
        c = rnd.choice([hi, lighten(hi, 0.2)]) if top else rnd.choice([col, lighten(col, 0.1), darken(col, 0.12), mix(col, hi, 0.4)])
        out.append(_lens(x, y, L, rnd.uniform(1.5, 4.5), math.radians(rnd.uniform(-4, 4)), rnd.uniform(-2, 2), c, rnd.uniform(0.3, 0.7)))
    out.append("</g>")
    return "".join(out)


def hill(u, pts, seed, base_y, col, tints, rim=None, amp=6, depth=4, rim_w=3, n=None):
    """Painted ground mass with a rough top edge, sloping strokes and an optional moonlit rim."""
    line = rough(pts, seed, amp, depth)
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in line) + f" L {line[-1][0]:.1f} {base_y} L {line[0][0]:.1f} {base_y} Z"
    ys = [y for _, y in line]
    box = (line[0][0] - 20, min(ys) - 10, line[-1][0] + 20, base_y)
    out = [f'<path d="{d}" fill="{col}"/>', tex(u, d, tints, seed, box, n or 220, angle=-4, length=(20, 60), width=(2, 6), op=(0.25, 0.6), curve=0.15)]
    if rim:
        out.append(ink(smooth_open(line), rim, rim_w, seed, 2, 0.6))
    return "".join(out), line


def tree(x, base, h, seed, fill=SIL, rim=None, lean=0, spread=30, depth=6, rim_side=1):
    return gnarly_tree(x, base, h, seed, fill, depth=depth, lean=lean, spread=spread, rim=rim, rim_side=rim_side)


# ---------------------------------------------------------------- lettering
def ptext(u, x, y, s, font, size, fill, tints, seed, max_w=470, ls=0, anchor="middle", angle=-75, shadow=None,
          sd=(0.03, 0.045), glow=None, glow_op=0.35, outline=None, ow=0, hi=None, density=1.0, rot=0, lens=(0.25, 0.7),
          widths=(0.025, 0.07)):
    """Hand-painted lettering: optional glow, an offset shadow, a base coat, then visible brush strokes clipped
    inside the letters and a dry-brush highlight. The size is auto-fitted with real font metrics."""
    size = fit_size(s, font, size, max_w, ls)
    w = measure(s, font, size, ls)
    xx = x + ls / 2 if anchor == "middle" and ls else x
    left = xx - w / 2 if anchor == "middle" else (xx if anchor == "start" else xx - w)
    a = f'text-anchor="{anchor}" {font} font-size="{size}"' + (f' letter-spacing="{ls}"' if ls else "")
    t = esc(s)
    out = []
    if glow:
        out.append(soft(left + w / 2, y - size * 0.35, w * 0.62 + size * 0.3, size * 0.75, glow, f"{u}-gl", glow_op))
    if shadow:
        out.append(f'<text x="{xx + size * sd[0]:.1f}" y="{y + size * sd[1]:.1f}" {a} fill="{shadow}"'
                   + (f' stroke="{shadow}" stroke-width="{ow}" stroke-linejoin="round"' if outline else "") + f'>{t}</text>')
    if outline:
        out.append(f'<text x="{xx:.1f}" y="{y:.1f}" {a} fill="{outline}" stroke="{outline}" stroke-width="{ow}" stroke-linejoin="round">{t}</text>')
    out.append(f'<text x="{xx:.1f}" y="{y:.1f}" {a} fill="{fill}">{t}</text>')
    rnd = random.Random(seed)
    st = []
    n = int(w * size / 190 * density) + 20
    for _ in range(n):
        px, py = rnd.uniform(left - size * 0.3, left + w + size * 0.1), rnd.uniform(y - size * 0.95, y + size * 0.25)
        L = rnd.uniform(size * lens[0], size * lens[1])
        aa = math.radians(angle + rnd.uniform(-10, 10))
        st.append(_lens(px, py, L, rnd.uniform(size * widths[0], size * widths[1]) / 2, aa, L * rnd.uniform(-0.1, 0.1), rnd.choice(tints), rnd.uniform(0.25, 0.6)))
    if hi:
        for _ in range(int(w / 8)):
            px, py = rnd.uniform(left, left + w), rnd.uniform(y - size * 0.75, y - size * 0.45)
            L = rnd.uniform(size * 0.12, size * 0.3)
            st.append(_lens(px, py, L, size * 0.012, math.radians(angle + rnd.uniform(-6, 6)), 0, hi, rnd.uniform(0.35, 0.7)))
    out.append(f'<clipPath id="{u}-tc"><text x="{xx:.1f}" y="{y:.1f}" {a}>{t}</text></clipPath><g clip-path="url(#{u}-tc)">{"".join(st)}</g>')
    g = "".join(out)
    return f'<g transform="rotate({rot} {x} {y})">{g}</g>' if rot else g


def arc_text(u, s, cx, cy, r, font, size, fill, tints, seed, ls=0, top=True, shadow=None, angle=-90, hi=None, max_deg=150):
    """Letters set one by one on an arc (works inside clipPaths, unlike textPath), then brush-textured."""
    while True:
        widths = [measure(ch, font, size) for ch in s]
        total = sum(widths) + ls * (len(s) - 1)
        if math.degrees(total / r) <= max_deg or size <= 12:
            break
        size -= 1
    ang = -total / 2 / r
    glyphs = []
    for ch, cw in zip(s, widths):
        mid = ang + cw / 2 / r
        if top:
            px, py, rot = cx + r * math.sin(mid), cy - r * math.cos(mid), math.degrees(mid)
        else:
            px, py, rot = cx - r * math.sin(mid), cy + r * math.cos(mid), -math.degrees(mid)
        glyphs.append((esc(ch), px, py, rot))
        ang += (cw + ls) / r
    a = f'text-anchor="middle" {font} font-size="{size}"'

    def layer(fill_attr, dx=0.0, dy=0.0):
        return "".join(f'<text x="{px + dx:.1f}" y="{py + dy:.1f}" {a}{fill_attr} transform="rotate({rot:.1f} {px + dx:.1f} {py + dy:.1f})">{ch}</text>'
                       for ch, px, py, rot in glyphs)

    out = []
    if shadow:
        out.append(layer(f' fill="{shadow}"', size * 0.03, size * 0.045))
    out.append(layer(f' fill="{fill}"'))
    rnd = random.Random(seed)
    ys = [py for _, _, py, _ in glyphs]
    xs = [px for _, px, _, _ in glyphs]
    st = []
    for _ in range(int(len(s) * 30)):
        px, py = rnd.uniform(min(xs) - size, max(xs) + size), rnd.uniform(min(ys) - size * 1.1, max(ys) + size * 0.4)
        L = rnd.uniform(size * 0.25, size * 0.7)
        st.append(_lens(px, py, L, rnd.uniform(size * 0.015, size * 0.035), math.radians(angle + rnd.uniform(-10, 10)), 0, rnd.choice(tints), rnd.uniform(0.25, 0.6)))
    if hi:
        for _ in range(len(s) * 4):
            px, py = rnd.uniform(min(xs) - size * 0.4, max(xs) + size * 0.4), rnd.uniform(min(ys) - size * 0.8, max(ys) - size * 0.3)
            st.append(_lens(px, py, size * 0.2, size * 0.012, math.radians(angle), 0, hi, 0.5))
    out.append(f'<clipPath id="{u}-ac">{layer("")}</clipPath><g clip-path="url(#{u}-ac)">{"".join(st)}</g>')
    return "".join(out), size


def label(x, y, s, font, size, fill, ls=4, max_w=440, shadow=None, op=1.0):
    size = fit_size(s, font, size, max_w, ls)
    xx = x + ls / 2 if ls else x
    a = f'text-anchor="middle" {font} font-size="{size}"' + (f' letter-spacing="{ls}"' if ls else "")
    sh = f'<text x="{xx + 1.2:.1f}" y="{y + 1.8:.1f}" {a} fill="{shadow}">{esc(s)}</text>' if shadow else ""
    return sh + f'<text x="{xx:.1f}" y="{y:.1f}" {a} fill="{fill}" opacity="{op}">{esc(s)}</text>'


def ruled(x, y, s, font, size, fill, ls=5, gap=14, line_w=42, seed=1, max_w=440, shadow=None):
    """Small spaced label between two hand-drawn rules with painted diamond ends."""
    size = fit_size(s, font, size, max_w, ls)
    w = measure(s, font, size, ls) - ls
    mid = y - size * 0.34
    out = [label(x, y, s, font, size, fill, ls, 600, shadow)]
    for sgn in (-1, 1):
        a = x + sgn * (w / 2 + gap)
        b = a + sgn * line_w
        out.append(ink(hpath([(a, mid), (b, mid)], seed + sgn, 0.6, False), fill, 2.2, seed, 1, 0.95))
        out.append(f'<path d="{blob(b + sgn * 3, mid, 4.2, 4.2, seed + 3 * sgn, 0.1, 4, 45)}" fill="{fill}"/>')
    return "".join(out)


# ---------------------------------------------------------------- painted pieces
def jack(u, cx, cy, w, h, seed, face="classic", lit=True, glow_r=None, glow_op=0.55, night=True, leaf="#6E8A3E",
         body=None, dark=None, light=None):
    """Gouache jack-o'-lantern: the painted pumpkin, then carved holes with a thick cut wall and candlelight
    glowing out of them, light spilling onto the skin and the ground."""
    body = body or ("#E06C26" if night else PUMP)
    dark = dark or ("#9A3A12" if night else PUMP_D)
    light = light or ("#F7A04E" if night else PUMP_L)
    out = []
    if lit and face:
        out.append(pglow(f"{u}-pg", cx, cy + h * 0.05, glow_r or w * 1.15, "#FF9A2E", glow_op, seed))
    out.append(painted_pumpkin(f"{u}-pp", cx, cy, w, h, seed, body=body, dark=dark, light=light, leaf=leaf))
    if night:
        # moonlit night: the far side of the pumpkin sinks into shadow
        d = blob(cx, cy, 0.56 * w, 0.5 * h, seed, 0.03, 22)
        out.append(inside(f"{u}-ns", d, f'<path d="{blob(cx + w * 0.42, cy + h * 0.3, w * 0.5, h * 0.55, seed + 5, 0.1)}" fill="#3A0E14" opacity="0.32"/>'))
    if face:
        rnd = random.Random(seed + 40)
        defs_ = defs(rg(f"{u}-fire", [(0, "#FFFDF0"), (0.35, "#FFE27A"), (0.75, "#FFB23A"), (1, "#F07A1E")], cx=0.5, cy=0.62, r=0.7))
        out.append(defs_)
        for i, pts in enumerate(FACES[face]):
            ab = [(cx + x * w, cy + y * h) for x, y in pts]
            closed = hpath(ab, seed + i, 1.0) if len(ab) < 10 else smooth_closed(jitter(ab, seed + i, 0.6))
            out.append(f'<path d="{closed}" fill="#4A1606" stroke="#4A1606" stroke-width="{w * 0.02:.1f}" stroke-linejoin="round"/>')
            if lit:
                mx = sum(p[0] for p in ab) / len(ab)
                my = sum(p[1] for p in ab) / len(ab)
                inner = [(mx + (x - mx) * 0.86, my + (y - my) * 0.86 + h * 0.018) for x, y in ab]
                di = hpath(inner, seed + i + 9, 0.6) if len(ab) < 10 else smooth_closed(inner)
                out.append(f'<path d="{di}" fill="url(#{u}-fire)"/>')
                flick = "".join(_lens(rnd.uniform(mx - w * 0.08, mx + w * 0.06), rnd.uniform(my - h * 0.04, my + h * 0.04), w * rnd.uniform(0.04, 0.09),
                                      w * 0.006, math.radians(rnd.uniform(-100, -80)), 1, rnd.choice(["#FFFFFF", "#FFF3B0", "#FFC24A"]), rnd.uniform(0.35, 0.7)) for _ in range(5))
                out.append(inside(f"{u}-fl{i}", di, flick))
            else:
                out.append(f'<path d="{closed}" fill="#24090A"/>')
        if lit:
            d = blob(cx, cy, 0.56 * w, 0.5 * h, seed, 0.03, 22)
            out.append(inside(f"{u}-wk", d, soft(cx, cy + h * 0.12, w * 0.44, h * 0.34, "#FFC46A", f"{u}-wkg", 0.28)))
    return "".join(out)


def ghost_path(lean=0.0, hem=5):
    L = lean * 30
    hm = []
    xs = [44 + L, 28 + L, 8 + L, -12 + L, -32 + L, -46 + L]
    ys = [72, 76, 78, 78, 76, 74]
    seg = f"M -40 22 C -42 -14 -24 -50 0 -50 C 24 -50 42 -14 40 22 L {xs[0]:.1f} {ys[0]}"
    for i in range(1, len(xs)):
        midx = (xs[i - 1] + xs[i]) / 2
        hm.append(f"Q {midx:.1f} {ys[i] - 14} {xs[i]:.1f} {ys[i]}")
    return seg + " " + " ".join(hm) + " Z"


def pghost(u, cx, top, w, seed, face="happy", lean=0.0, arms=True, flip=False, glow_op=0.35, body=("#FBF7FF", "#E4DAF2", "#A898CC"),
           line="#4A3A6A", wave=0):
    """Gouache sheet ghost: luminous wash, lilac shade side, curving strokes, a soft inked edge and a sweet face."""
    k = w / 100
    d = ghost_path(lean)
    rnd = random.Random(seed)
    out = []
    if glow_op:
        out.append(pglow(f"{u}-gg", cx, top + 50 * k, 105 * k, "#E8E0FF", glow_op, seed))
    sx = -k if flip else k
    g = [f'<g transform="translate({cx:.1f} {top + 50 * k:.1f}) scale({sx:.3f} {k:.3f})">']
    if arms:
        la = "M -36 10 C -48 8 -56 0 -58 -10 C -59 -16 -52 -18 -48 -13 C -44 -8 -40 -6 -36 -6 Z"
        ra = "M 36 12 C 48 14 56 8 60 0 C 62 -6 56 -9 52 -5 C 48 -1 42 0 36 -2 Z" if not wave else "M 36 4 C 46 -2 52 -14 52 -26 C 52 -33 59 -33 60 -26 C 62 -10 52 6 36 10 Z"
        g.append(f'<path d="{la}" fill="{body[1]}"/><path d="{ra}" fill="{body[1]}"/>')
        g.append(ink(la, line, 2.2 / k, seed, 1, 0.6) + ink(ra, line, 2.2 / k, seed + 1, 1, 0.6))
    g.append(wash(d, body[0], seed, 2, 0.8, 0.5))
    sh = (f'<path d="M 22 -48 C 46 -10 44 40 {50 + lean * 30:.1f} 82 L 80 82 L 80 -60 Z" fill="{body[2]}" opacity="0.5"/>'
          f'<path d="M -48 52 Q 0 40 {52 + lean * 30:.1f} 58 L 60 90 L -60 90 Z" fill="{body[2]}" opacity="0.28"/>')
    st = "".join(_lens(rnd.uniform(-44, 40), rnd.uniform(-50, 70), rnd.uniform(14, 34), rnd.uniform(1.2, 3), math.radians(rnd.uniform(-100, -76)),
                       rnd.uniform(-3, 3), rnd.choice(["#FFFFFF", body[1], body[2], "#F4ECDC"]), rnd.uniform(0.25, 0.55)) for _ in range(70))
    hi = '<path d="M -26 -30 Q -24 -42 -12 -46" stroke="#FFFFFF" stroke-width="6" fill="none" stroke-linecap="round" opacity="0.9"/>'
    g.append(inside(f"{u}-gc", d, sh + st + hi))
    g.append(ink(d, line, 2.6 / k, seed + 3, 2, 0.7))
    eye = "#251A34"
    if face == "happy":
        g.append(f'<path d="{blob(-13, -14, 5.4, 7.4, seed + 1, 0.06, 10)}" fill="{eye}"/><path d="{blob(13, -14, 5.4, 7.4, seed + 2, 0.06, 10)}" fill="{eye}"/>'
                 '<circle cx="-11.6" cy="-16.8" r="1.9" fill="#FFF"/><circle cx="14.4" cy="-16.8" r="1.9" fill="#FFF"/>'
                 + ink("M -6 0 Q 0 7 6 0", eye, 2.8, seed, 1, 1))
    elif face == "boo":
        g.append(f'<path d="{blob(-13, -16, 5.4, 7.4, seed + 1, 0.06, 10)}" fill="{eye}"/><path d="{blob(13, -16, 5.4, 7.4, seed + 2, 0.06, 10)}" fill="{eye}"/>'
                 '<circle cx="-11.6" cy="-18.8" r="1.9" fill="#FFF"/><circle cx="14.4" cy="-18.8" r="1.9" fill="#FFF"/>'
                 f'<path d="{blob(0, 4, 6.4, 8.4, seed + 3, 0.08, 10)}" fill="{eye}"/><path d="{blob(0, 7.5, 3.4, 3.6, seed + 4, 0.1, 8)}" fill="#C2577A"/>')
    elif face == "sleepy":
        g.append(ink("M -18 -14 Q -13 -9 -8 -14 M 8 -14 Q 13 -9 18 -14", eye, 2.8, seed, 1, 1) + ink("M -4 0 Q 0 3 4 0", eye, 2.2, seed, 1, 1))
    elif face == "wink":
        g.append(f'<path d="{blob(-13, -14, 5.4, 7.4, seed + 1, 0.06, 10)}" fill="{eye}"/><circle cx="-11.6" cy="-16.8" r="1.9" fill="#FFF"/>'
                 + ink("M 8 -13 Q 13 -18 18 -13", eye, 2.8, seed, 1, 1) + ink("M -6 0 Q 0 7 6 0", eye, 2.8, seed, 1, 1))
    if face:
        g.append('<ellipse cx="-22" cy="-4" rx="6.4" ry="3.6" fill="#F29AB4" opacity="0.6"/><ellipse cx="22" cy="-4" rx="6.4" ry="3.6" fill="#F29AB4" opacity="0.6"/>')
    g.append("</g>")
    out.append("".join(g))
    return "".join(out)


def pcandle(u, x, base, h, w, seed, wax=BONE, wax_d="#BFA582", lit=True, glow_r=None, glow_op=0.6, drips=3, line=INKB):
    """Painted candle: uneven wax column with drips, vertical strokes, shade side, a glowing teardrop flame."""
    rnd = random.Random(seed)
    top = base - h
    pts = [(x - w / 2, base), (x - w / 2 - 0.5, top + w * 0.1)]
    ds = sorted(rnd.uniform(0.15, 0.85) for _ in range(drips))
    rim = []
    for t in ds:
        px = x - w / 2 + w * t
        L = rnd.uniform(0.12, 0.42) * h
        dw = w * rnd.uniform(0.1, 0.16)
        rim.append((px - dw, top + w * 0.08))
        rim.append((px - dw * 0.8, top + L))
        rim.append((px, top + L + dw))
        rim.append((px + dw * 0.8, top + L))
        rim.append((px + dw, top + w * 0.08))
    edge = [(x - w / 2, top), (x - w * 0.2, top - w * 0.06), (x + w * 0.2, top - w * 0.06), (x + w / 2, top)]
    full = [(x - w / 2, base)] + [edge[0]] + edge[1:] + [(x + w / 2 + 0.5, top + w * 0.1), (x + w / 2, base)]
    d = smooth_closed(full) if False else hpath(full, seed, 0.6)
    out = []
    if lit:
        out.append(pglow(f"{u}-cg", x, top - w * 0.8, glow_r or w * 4.2, "#FFC45A", glow_op, seed))
    out.append(pshape(u, d, wax, [lighten(wax, 0.4), wax_d, mix(wax, wax_d, 0.5), "#FFFFFF"], seed, (x - w, top - 5, x + w, base),
                      angle=-90, length=(h * 0.15, h * 0.4), width=(w * 0.03, w * 0.08), op=(0.25, 0.55),
                      shade=(wax_d, 0.7, w * 0.22, 0)))
    # wax drips in front: lit and rounded
    for t in ds:
        px = x - w / 2 + w * t
        L = rnd.uniform(0.12, 0.38) * h
        dw = w * rnd.uniform(0.09, 0.14)
        dd = f"M {px - dw:.1f} {top:.1f} L {px - dw:.1f} {top + L:.1f} Q {px:.1f} {top + L + dw * 2.2:.1f} {px + dw:.1f} {top + L:.1f} L {px + dw:.1f} {top:.1f} Z"
        out.append(f'<path d="{dd}" fill="{lighten(wax, 0.35)}" opacity="0.9"/><path d="M {px - dw * 0.4:.1f} {top + 2:.1f} L {px - dw * 0.4:.1f} {top + L:.1f}" stroke="#FFFFFF" stroke-width="{max(1, dw * 0.5):.1f}" opacity="0.6" stroke-linecap="round"/>')
    out.append(f'<path d="{blob(x, top, w / 2, w * 0.13, seed + 4, 0.05, 12)}" fill="{lighten(wax, 0.3)}"/>')
    out.append(ink(d, line, max(1.4, w * 0.045), seed + 1, 2, 0.55))
    out.append(ink(f"M {x:.1f} {top:.1f} q {w * 0.04:.1f} {-w * 0.15:.1f} {-w * 0.02:.1f} {-w * 0.3:.1f}", "#2A1E16", max(1.6, w * 0.06), seed, 1, 1))
    if lit:
        fh, fy = w * 1.15, top - w * 0.24
        out.append(defs(rg(f"{u}-cf", [(0, "#FFFFFF"), (0.35, "#FFF3B0"), (0.8, "#FFB33A"), (1, "#F07A1A", 0.6)], cx=0.5, cy=0.72, r=0.62)))
        fd = (f"M {x:.1f} {fy - fh:.1f} Q {x + w * 0.46:.1f} {fy - fh * 0.38:.1f} {x + w * 0.22:.1f} {fy - fh * 0.06:.1f} "
              f"Q {x:.1f} {fy + fh * 0.08:.1f} {x - w * 0.22:.1f} {fy - fh * 0.06:.1f} Q {x - w * 0.44:.1f} {fy - fh * 0.38:.1f} {x:.1f} {fy - fh:.1f} Z")
        out.append(f'<path d="{fd}" fill="url(#{u}-cf)"/>')
        out.append(f'<path d="{blob(x, fy - fh * 0.2, w * 0.08, fh * 0.13, seed, 0.1, 8)}" fill="#7A9AE0" opacity="0.55"/>')
    return "".join(out)


def pbat(cx, cy, s, rot=0, flap=0, fill=SIL, rim=LILAC, eyes=None):
    return bat(cx, cy, s, fill=fill, rim=rim, rot=rot, flap=flap, eyes=eyes)


def window(u, x, y, w, h, seed, lit=("#FFE38A", "#FFB547"), frame=SIL, arch=False, glow_op=0.35, figure=None):
    """A lit window painted by hand: warm wash, flicker strokes, mullions, a little glow spilling out."""
    rnd = random.Random(seed)
    if arch:
        pts = [(x, y + h), (x, y + w / 2)] + [(x + w / 2 - w / 2 * math.cos(math.pi * i / 6), y + w / 2 - w / 2 * math.sin(math.pi * i / 6)) for i in range(1, 6)] + [(x + w, y + w / 2), (x + w, y + h)]
        d = hpath(pts, seed, 0.5)
    else:
        d = hpath([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], seed, 0.6)
    out = []
    if glow_op:
        out.append(soft(x + w / 2, y + h / 2, w * 1.5, h * 1.2, lit[1], f"{u}-wg", glow_op))
    inner = [soft(x + w * 0.4, y + h * 0.55, w * 0.8, h * 0.7, "#FFF6D0", f"{u}-wl", 0.8)]
    inner.append(f'<rect x="{x:.1f}" y="{y + h * 0.62:.1f}" width="{w:.1f}" height="{h * 0.4:.1f}" fill="{lit[1]}" opacity="0.35"/>')
    inner += [_lens(rnd.uniform(x, x + w), rnd.uniform(y, y + h), min(h * 0.3, 26), min(w * 0.04, 2.6), math.radians(-90 + rnd.uniform(-8, 8)), 0, rnd.choice([lit[1], "#FFF6D6", "#FFE38A"]), rnd.uniform(0.15, 0.32)) for _ in range(min(16, int(w * h / 60) + 3))]
    if figure:
        inner.append(figure)
    out.append(f'<path d="{d}" fill="{lit[0]}"/>' + inside(f"{u}-wi", d, "".join(inner)))
    mw = max(1.6, w * 0.08)
    out.append(ink(f"M {x + w / 2:.1f} {y + (w / 2 if arch else 0):.1f} L {x + w / 2:.1f} {y + h:.1f} M {x:.1f} {y + h * 0.5:.1f} L {x + w:.1f} {y + h * 0.5:.1f}", frame, mw, seed, 1, 0.9))
    out.append(ink(d, frame, mw * 1.1, seed + 1, 1, 0.9))
    return "".join(out)


def finish(u, seed=9, vign=0.5, vcol="#06030C", grain_op=0.9, gcol="#000000"):
    out = []
    if vign:
        out.append(defs(rg(f"{u}-vg", [(0.55, vcol, 0), (1, vcol, vign)], r=0.78)) + f'<rect width="600" height="600" fill="url(#{u}-vg)"/>')
    out.append(grain(f"{u}-gr", gcol, seed, grain_op))
    return "".join(out)



def stones(u, box, seed, cols=("#4A4060", "#3E3552", "#544A6A", "#463C5C"), mortar="#17111F", rim="#9A8AC0", rows=(26, 34), widths=(44, 84), rim_op=0.5, tints=None):
    """Painted stone wall: every stone a hand-cut shape with its own strokes, a lit top edge, dark mortar."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{mortar}"/>']
    y = y0 + 2
    k = 0
    st = []
    while y < y1:
        h = rnd.uniform(*rows)
        x = x0 - rnd.uniform(0, 40)
        while x < x1:
            w = rnd.uniform(*widths)
            c = rnd.choice(cols)
            d = smooth_closed(jitter([(x + 3, y + 3), (x + w / 2, y + 2), (x + w - 3, y + 3), (x + w - 2, y + h / 2), (x + w - 3, y + h - 3), (x + w / 2, y + h - 2), (x + 3, y + h - 3), (x + 2, y + h / 2)], seed + k, 1.4))
            out.append(f'<path d="{d}" fill="{c}"/>')
            tt = tints or [lighten(c, 0.12), darken(c, 0.15), lighten(c, 0.25)]
            st.append(inside(f"{u}-s{k}", d, "".join(_lens(rnd.uniform(x, x + w), rnd.uniform(y, y + h), rnd.uniform(10, 26), rnd.uniform(1, 2.6), math.radians(rnd.uniform(-10, 10)), 1,
                                                          rnd.choice(tt), rnd.uniform(0.3, 0.6)) for _ in range(int(w / 7)))
                             + f'<path d="{d}" fill="none" stroke="#000" stroke-width="5" opacity="0.25" transform="translate(2 3)"/>'))
            st.append(f'<path d="M {x + 7:.1f} {y + 4.5:.1f} Q {x + w / 2:.1f} {y + 3:.1f} {x + w - 9:.1f} {y + 4.5:.1f}" stroke="{rim}" stroke-width="2" fill="none" opacity="{rim_op:.2f}" stroke-linecap="round"/>')
            x += w
            k += 1
        y += h
    return "".join(out) + "".join(st)


def flames(u, cx, base, w, h, seed, n=7):
    """Painted campfire flames: layered tongues from deep red to gold to white, each with brush streaks."""
    rnd = random.Random(seed)
    out = [pglow(f"{u}-fg", cx, base - h * 0.35, w * 1.1, "#FF8A2A", 0.6, seed)]
    for layer, (col, k, hk) in enumerate([("#C8381A", 1.0, 1.0), ("#F07A22", 0.8, 0.82), ("#FFC23A", 0.56, 0.6), ("#FFF2B0", 0.3, 0.36)]):
        for i in range(n if layer < 2 else n - 2):
            t = (i + 0.5) / (n if layer < 2 else n - 2) - 0.5
            fx = cx + t * w * k + rnd.uniform(-4, 4)
            fh = h * hk * (1 - abs(t) * 0.9) * rnd.uniform(0.75, 1.1)
            fw = w * k / n * 1.5
            lean = rnd.uniform(-0.25, 0.25) * fh
            d = (f"M {fx - fw / 2:.1f} {base:.1f} C {fx - fw * 0.6:.1f} {base - fh * 0.45:.1f} {fx + lean * 0.4:.1f} {base - fh * 0.7:.1f} {fx + lean:.1f} {base - fh:.1f} "
                 f"C {fx + fw * 0.2 + lean * 0.3:.1f} {base - fh * 0.6:.1f} {fx + fw * 0.7:.1f} {base - fh * 0.4:.1f} {fx + fw / 2:.1f} {base:.1f} Z")
            out.append(f'<path d="{d}" fill="{col}" opacity="0.92"/>')
    return "".join(out)


def logs(u, cx, base, w, seed):
    out = []
    for i, (dx, rot, L) in enumerate([(-0.18, 14, 0.75), (0.18, -14, 0.75), (0, 0, 0.6)]):
        x, y = cx + dx * w, base - 8 - (i == 2) * 4
        d = blob(x, y, L * w / 2, 10, seed + i, 0.05, 14, rot)
        out.append(pshape(f"{u}-l{i}", d, "#4A2E1E", ["#6A4430", "#2E1A10", "#8A5A3A"], seed + i, (x - w / 2, y - 14, x + w / 2, y + 14), angle=rot, length=(14, 30), width=(1, 2.4), line="#1A0E08", lw=1.6))
        ex = x + math.cos(math.radians(rot)) * L * w / 2 * (1 if i != 1 else -1)
        out.append(f'<path d="{blob(ex, y + math.sin(math.radians(rot)) * L * w / 2 * (1 if i != 1 else -1), 7, 9, seed + i, 0.08, 10)}" fill="#C8955A"/>')
    return "".join(out)


def rooftops(u, base, seed, fill=SIL, lit=("#FFE38A", "#FFB547"), rim="#9C8AC8", spire_x=None):
    """A storybook village skyline: gables, chimneys, a little spire, warm windows at random."""
    rnd = random.Random(seed)
    out = []
    x = -20
    k = 0
    while x < 620:
        w = rnd.uniform(56, 96)
        h = rnd.uniform(40, 90)
        roof = rnd.uniform(24, 46)
        top = base - h
        pts = [(x, 600), (x, top), (x + w / 2, top - roof), (x + w, top), (x + w, 600)]
        d = hpath(pts, seed + k, 1.0)
        out.append(f'<path d="{d}" fill="{fill}"/>')
        out.append(ink(hpath([(x, top), (x + w / 2, top - roof), (x + w, top)], seed + k, 0.8, False), rim, 2, seed + k, 1, 0.55))
        if rnd.random() < 0.6:
            cxh = x + w * rnd.uniform(0.62, 0.8)
            ch_top = top - roof * 0.7 - 12
            out.append(f'<path d="{hpath([(cxh, top - roof * 0.2), (cxh, ch_top), (cxh + 11, ch_top), (cxh + 11, top - roof * 0.5)], seed + k + 50, 0.5)}" fill="{fill}"/>')
        for wy in (top + 14, top + 44):
            for wx in (x + w * 0.22, x + w * 0.6):
                if wy + 18 < 600 and rnd.random() < 0.45:
                    out.append(window(f"{u}-w{k}{int(wx)}{int(wy)}", wx, wy, 11, 15, rnd.randrange(999), lit=lit, frame=fill, glow_op=0.25))
        x += w - rnd.uniform(4, 14)
        k += 1
    if spire_x:
        sx = spire_x
        pts = [(sx - 18, 600), (sx - 18, base - 110), (sx, base - 190), (sx + 18, base - 110), (sx + 18, 600)]
        out.append(f'<path d="{hpath(pts, seed + 99, 0.8)}" fill="{fill}"/>' + ink(hpath(pts[1:4], seed + 98, 0.6, False), rim, 2, seed, 1, 0.6))
        out.append(window(f"{u}-sp", sx - 6, base - 96, 12, 20, seed, lit=lit, frame=fill, arch=True, glow_op=0.3))
    return "".join(out)


def witch_sil(cx, cy, s, fill=SIL, rim="#FFE9B0", rot=-8, cat=True):
    """Witch riding a broomstick in silhouette, flying right: billowing cape and hair, hat flopping back in the
    wind, one hand on the stick, a pointed boot; straw bristles painted and lit by the moon; a cat rides behind."""
    out = [f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot}) scale({s:.3f})">']
    rnd = random.Random(4)

    def by(x):  # broom centre line
        return 18 + (x + 118) * (-24 / 268)
    br = "M -112 12 C -138 2 -166 -10 -190 -8 C -182 6 -186 24 -198 40 C -172 44 -140 34 -112 26 Z"
    out.append(f'<path d="{br}" fill="#6A4A2A"/>')
    out.append(inside("gabrm-wsbr", br, "".join(_lens(-112 - rnd.uniform(0, 10), 18 + rnd.uniform(-9, 9), rnd.uniform(40, 86), rnd.uniform(0.8, 2), math.radians(180 + rnd.uniform(-14, 14)), 0,
                                                rnd.choice(["#C8955A", "#E8C07A", "#8A6038", "#FFE2A0"]), rnd.uniform(0.4, 0.85)) for _ in range(70))))
    out.append(ink(br, "#2A1A0C", 1.6, 4, 1, 0.7))
    out.append(f'<path d="M -114 8 Q -110 18 -112 30" stroke="#3A2414" stroke-width="6" fill="none" stroke-linecap="round"/>')
    out.append(f'<path d="M -118 {by(-118):.1f} L 150 {by(150):.1f}" stroke="{fill}" stroke-width="7" stroke-linecap="round"/>'
               f'<circle cx="150" cy="{by(150):.1f}" r="5" fill="{fill}"/>')
    if cat:
        from halloween_painted import black_cat
        out.append(black_cat("gabrm-wscat", -84, by(-84) - 2, 0.36, fill=fill, rim=rim, eye="#D9F05A"))
    # cape billowing back from the shoulders, ragged hem
    cape = ("M 4 -70 C -20 -78 -48 -74 -72 -64 C -88 -58 -102 -60 -120 -66 C -112 -56 -108 -50 -112 -42 C -100 -46 -94 -42 -96 -32 "
            "C -86 -38 -76 -34 -74 -24 C -54 -32 -30 -32 -8 -34 Z")
    out.append(f'<path d="{cape}" fill="{fill}"/>')
    # dress draped over the stick, hem streaming back
    out.append(f'<path d="M -6 -38 C -18 -20 -36 0 -62 16 Q -50 20 -54 30 Q -40 24 -34 34 Q -24 24 -14 32 Q -4 24 6 32 Q 12 24 18 28 C 16 4 12 -18 10 -38 Z" fill="{fill}"/>')
    # leg and pointed boot reaching forward
    out.append(f'<path d="M 6 16 C 22 22 34 26 46 28 C 54 28 60 24 64 18 Q 68 26 60 32 C 52 38 38 38 24 36 C 16 34 8 32 4 30 Z" fill="{fill}"/>')
    # torso leaning into the ride
    out.append(f'<path d="M -8 -34 C -12 -50 -8 -64 2 -72 C 12 -76 20 -68 18 -58 C 16 -48 12 -40 10 -34 Z" fill="{fill}"/>')
    # arm reaching to the stick
    out.append(ink(f"M 8 -62 Q 30 -42 40 {by(40) - 4:.1f}", fill, 9, 5, 1, 1) + f'<circle cx="42" cy="{by(42) - 3:.1f}" r="5.5" fill="{fill}"/>')
    # head, nose, chin, hair streaming back
    out.append(f'<circle cx="14" cy="-84" r="11" fill="{fill}"/><path d="M 22 -90 L 38 -82 L 23 -79 Z M 18 -75 L 24 -70 L 14 -73 Z" fill="{fill}"/>'
               f'<path d="M 6 -90 C -14 -94 -34 -86 -58 -90 C -46 -80 -26 -78 4 -80 Z" fill="{fill}"/>'
               f'<path d="M 4 -82 C -16 -78 -32 -70 -52 -72 C -40 -64 -20 -66 2 -74 Z" fill="{fill}"/>')
    # hat: tilted brim, cone flopping back in the wind
    out.append(f'<ellipse cx="14" cy="-94" rx="30" ry="5.5" transform="rotate(-10 14 -94)" fill="{fill}"/>'
               f'<path d="M -2 -94 C -4 -112 -10 -128 -20 -138 C -28 -146 -40 -150 -50 -146 C -40 -138 -28 -126 -16 -116 C -4 -106 14 -100 28 -98 Z" fill="{fill}"/>')
    # moonlight on the rims (lit from behind)
    out.append(ink("M -2 -94 C -4 -112 -10 -128 -20 -138 C -28 -146 -40 -150 -50 -146", rim, 2.2, 3, 1, 0.8))
    out.append(ink("M 4 -70 C -20 -78 -48 -74 -72 -64 C -88 -58 -102 -60 -120 -66", rim, 2, 4, 1, 0.65))
    out.append(ink("M 2 -72 C 12 -76 20 -68 18 -58", rim, 1.8, 5, 1, 0.6))
    out.append(ink("M 6 -90 C -14 -94 -34 -86 -58 -90", rim, 1.6, 6, 1, 0.55))
    out.append(ink("M 46 28 C 54 28 60 24 64 18", rim, 1.6, 7, 1, 0.6))
    out.append(ink(f"M -16 -98 L 44 -108", rim, 1.6, 8, 1, 0.5))
    out.append("</g>")
    return "".join(out)


# ================================================================ designs
def d_spooky_season():
    u = "gaspk"
    o = [sky(u, [(0, NIGHT0), (0.45, NIGHT2), (0.8, "#5A3E86"), (1, "#7A5A9A")], 11, swirl=(300, 214, 136, 200, "#C9B6E8"))]
    o.append(stars(12, 46, (20, 20, 580, 330), avoid=[(300, 214, 165)]))
    o.append(moon(u, 300, 214, 128, 21))
    o.append(cloud(u + "c1", 148, 270, 210, 16, 4, "#4A3A7A", "#9C8AC8", 0.75))
    o.append(cloud(u + "c2", 478, 172, 150, 13, 5, "#4A3A7A", "#B8A6DC", 0.6))
    # bats leaving the house
    for i, (bx, by, bs, br) in enumerate([(392, 104, 20, -12), (434, 80, 14, 8), (352, 74, 11, -4), (474, 116, 10, 14), (196, 100, 12, -18)]):
        o.append(pbat(bx, by, bs, br, flap=(i % 3) * 8 - 6))
    # far hill + the crooked house on its crest
    h1, l1 = hill(u + "h1", [(-20, 360), (120, 340), (260, 318), (360, 322), (470, 346), (620, 338)], 7, 600, "#2A2050",
                  ["#3A2E66", "#2E2458", "#463A72"], rim="#B8A6DC", amp=5)
    o.append(h1)
    o.append(haunted_house(u + "hs", 300, 330, 0.95, 17))
    o.append(tree(452, 352, 176, 33, SIL, rim="#B8A6DC", lean=8, spread=30, depth=6))
    o.append(tree(126, 346, 112, 41, SIL, rim="#B8A6DC", lean=-10, spread=28, depth=5))
    fence = []
    rnd = random.Random(3)
    for i in range(18):
        x = 150 + i * 17
        if 244 < x < 358:
            continue
        y = y_on(l1, x) or 340
        fence.append(f'M {x:.1f} {y + 4:.1f} L {x + rnd.uniform(-1, 1):.1f} {y - 18 + rnd.uniform(-3, 2):.1f}')
    o.append(ink(" ".join(fence), SIL, 3.2, 5, 1, 1))
    o.append(ink(f"M 146 {y_on(l1, 146) - 11:.1f} L 244 {y_on(l1, 244) - 11:.1f} M 358 {y_on(l1, 358) - 11:.1f} L 444 {y_on(l1, 444) - 11:.1f}", SIL, 2.4, 6, 1, 1))
    # path winding down from the door
    pd = "M 292 334 C 280 360 330 372 312 396 C 296 420 250 430 236 470 L 330 470 C 340 440 372 420 360 396 C 350 374 312 362 308 334 Z"
    o.append(f'<path d="{pd}" fill="#3E3270" opacity="0.8"/>')
    # foreground hill with pumpkins at the sides
    h2, l2 = hill(u + "h2", [(-20, 446), (140, 432), (300, 446), (460, 428), (620, 440)], 9, 600, "#17112A",
                  ["#241A3E", "#1E1636", "#2E2448"], rim="#7A68A8", amp=4)
    o.append(h2)
    o.append(jack(u + "j1", 92, 424, 74, 54, 31, "classic", glow_r=95))
    o.append(jack(u + "j3", 140, 440, 36, 26, 33, None, lit=False))
    o.append(jack(u + "j2", 510, 420, 64, 48, 32, "sly", glow_r=85))
    o.append(soft(300, 600, 360, 120, "#05030C", u + "fb", 0.6))
    o.append(ptext(u + "t1", 300, 500, "spooky", SERIF_IT, 132, BONE, ["#FFFFFF", "#E6D8C0", "#D2C2E6", "#FFF4DC"], 51,
                   max_w=350, angle=-58, shadow=INKN, glow="#C9B6E8", glow_op=0.22, hi="#FFFFFF"))
    o.append(ptext(u + "t2", 300, 540, "SEASON", BEBAS, 40, PUMP_L, ["#FFC07A", PUMP, "#FFD9A0"], 52, max_w=260, ls=16, shadow=INKN))
    o.append(finish(u, 3))
    return "".join(o)


def haunted_house(u, cx, base, s, seed, body=SIL, rim="#C8B6E8"):
    """Crooked storybook manor: leaning towers, steep roofs, a sagging porch, warm windows at random."""
    def T(pts):
        return [(cx + x * s, base + y * s) for x, y in pts]

    rnd = random.Random(seed)
    out = []
    parts = [
        T([(-96, 0), (-96, -92), (-60, -122), (-24, -92), (-24, 0)]),                    # left wing
        T([(-30, 0), (-34, -140), (-50, -140), (-6, -228), (10, -222), (42, -140), (30, -140), (30, 0)]),  # tall tower
        T([(24, 0), (24, -100), (14, -100), (60, -150), (106, -100), (96, -100), (96, 0)]),  # right gable
        T([(70, -108), (68, -150), (82, -150), (82, -116)]),                                # chimney
        T([(-118, 0), (-114, -40), (118, -40), (114, 0)]),                                   # porch base
    ]
    for i, pts in enumerate(parts):
        d = hpath(pts, seed + i, 0.8)
        out.append(f'<path d="{d}" fill="{body}"/>')
        bx = (min(p[0] for p in pts) - 4, min(p[1] for p in pts) - 4, max(p[0] for p in pts) + 4, max(p[1] for p in pts) + 4)
        boards = "".join(f'<path d="M {bx[0]:.1f} {yy:.1f} L {bx[2]:.1f} {yy + rnd.uniform(-1.2, 1.2):.1f}" stroke="#30264C" stroke-width="1.4" opacity="0.8"/>'
                         for yy in [bx[1] + k * 7 * s for k in range(1, int((bx[3] - bx[1]) / (7 * s)))])
        out.append(inside(f"{u}-b{i}", d, boards))
        out.append(tex(f"{u}-t{i}", d, ["#3A2E58", "#1E1630", "#463A68", "#2A2042"], seed + i, bx,
                       n=int((bx[2] - bx[0]) * (bx[3] - bx[1]) / 90), angle=-90, length=(8, 22), width=(1.2, 3), op=(0.3, 0.6)))
        out.append(ink(d, INKN, 2.2, seed + i, 1, 0.8))
    # moonlit rims on the roof edges facing the moon (behind = above)
    rims = [T([(-96, -92), (-60, -122), (-24, -92)]), T([(-50, -140), (-6, -228), (10, -222), (42, -140)]), T([(14, -100), (60, -150), (106, -100)])]
    for i, r in enumerate(rims):
        out.append(ink(hpath(r, seed + 20 + i, 0.6, False), rim, 2.2, seed + i, 2, 0.75))
    # porch roof + posts
    out.append(ink(hpath(T([(-124, -40), (124, -44)]), seed, 0.8, False), rim, 2, seed, 1, 0.5))
    out.append(ink(" ".join(hpath(T([(px, -40), (px + rnd.uniform(-2, 2), 0)]), seed + int(px), 0.6, False) for px in (-104, -60, 60, 104)), "#2E2448", 2.2, seed, 1, 1))
    # windows
    wins = [(-80, -80, 14, 22, False), (-50, -80, 14, 22, False), (-12, -196, 12, 20, True), (-14, -128, 16, 26, True), (-14, -88, 16, 26, False),
            (46, -128, 16, 22, False), (72, -86, 14, 22, False), (40, -86, 14, 22, False)]
    for i, (wx, wy, ww, wh, arch) in enumerate(wins):
        x0, y0 = cx + wx * s, base + wy * s
        if rnd.random() < 0.82:
            out.append(window(f"{u}-w{i}", x0, y0, ww * s, wh * s, seed + i, arch=arch, glow_op=0.3))
        else:
            out.append(f'<path d="{hpath([(x0, y0), (x0 + ww * s, y0), (x0 + ww * s, y0 + wh * s), (x0, y0 + wh * s)], seed + i, 0.5)}" fill="#3A2E5A"/>')
    # front door glowing
    dx0 = cx - 10 * s
    out.append(window(f"{u}-dr", dx0, base - 30 * s, 20 * s, 30 * s, seed + 77, lit=("#FFCF6A", "#F59A3A"), arch=True, glow_op=0.4))
    return "".join(out)


def d_boo():
    u = "gaboo"
    o = [sky(u, [(0, "#0E0B22"), (0.5, "#241C4A"), (0.85, "#3E2E6A"), (1, "#4A3878")], 61, swirl=(452, 140, 66, 130, "#CDBCEB"))]
    o.append(stars(62, 40, (20, 20, 580, 300), avoid=[(452, 140, 100)]))
    o.append(moon(u, 452, 140, 64, 63, halo_r=2.1))
    for i, (x, hh, sd) in enumerate([(70, 300, 64), (170, 230, 65), (520, 260, 66), (420, 200, 67), (600, 230, 68), (-10, 240, 69)]):
        o.append(tree(x, 470, hh, sd, "#2A2150" if i < 2 else "#2E2458", lean=(-1) ** i * 8, spread=28, depth=5))
    o.append(soft(300, 440, 420, 90, "#8A78B8", u + "ms", 0.45))
    h1, l1 = hill(u + "h1", [(-20, 452), (160, 440), (330, 450), (620, 434)], 7, 600, "#1C1534", ["#2A2148", "#231B3E", "#352A56"], rim="#9C8AC8", amp=4)
    o.append(h1)
    for i, (x, w_, h_, tl) in enumerate([(96, 34, 46, -6), (494, 30, 40, 7), (534, 22, 30, -4)]):
        y = y_on(l1, x) + 8
        d = hpath([(x - w_ / 2, y), (x - w_ / 2, y - h_ * 0.7)] + [(x - w_ / 2 * math.cos(math.pi * k / 6), y - h_ * 0.7 - w_ / 2 * math.sin(math.pi * k / 6)) for k in range(1, 6)] + [(x + w_ / 2, y - h_ * 0.7), (x + w_ / 2, y)], 80 + i, 0.6)
        o.append(f'<g transform="rotate({tl} {x} {y})">' + pshape(f"{u}-ts{i}", d, "#6E6688", ["#8A82A6", "#5A5276", "#9C94B8"], 80 + i, (x - w_, y - h_ - 10, x + w_, y),
                                                                  angle=-90, length=(6, 16), width=(1.2, 3), shade=("#3A3452", 0.6, 4, 0), line=INKN, lw=2) + "</g>")
    o.append(soft(300, 444, 100, 14, "#05030C", u + "gs", 0.5))
    o.append(pghost(u + "g", 296, 128, 186, 70, face="boo", lean=0.25, glow_op=0.45, wave=1))
    rnd = random.Random(5)
    gr = "".join(f'M {x:.1f} {462 + rnd.uniform(-4, 8):.1f} q {rnd.uniform(-3, 3):.1f} {-rnd.uniform(5, 9):.1f} {rnd.uniform(-5, 5):.1f} {-rnd.uniform(10, 18):.1f} ' for x in [rnd.uniform(-10, 610) for _ in range(90)])
    o.append(f'<path d="{gr}" stroke="#2E2650" stroke-width="2.2" fill="none" stroke-linecap="round"/>')
    o.append(soft(300, 580, 380, 110, "#05030C", u + "fb", 0.55))
    o.append(ptext(u + "t", 300, 538, "BOO!", ANTON, 140, BONE, ["#FFFFFF", "#E8DCC4", "#D6C8EC", "#FFF6E0"], 72, max_w=360, ls=8,
                   angle=-84, shadow=INKN, glow="#D6C8F0", glow_op=0.3, hi="#FFFFFF"))
    o.append(finish(u, 4))
    return "".join(o)


def d_happy_halloween():
    """Paper-ground piece (matches the approved 'hello pumpkin' look): big painted jack-o'-lantern on warm paper."""
    u = "gahh"
    o = [paper(u + "-p", "#F2E6D0", "#7A5232", 14)]
    # a dusky painted swatch behind the pumpkin, ragged dry-brush rim
    wd = blob(300, 318, 214, 176, 15, 0.035, 30)
    o.append(wash(wd, "#3A2E5E", 15, 3, 3, 0.4))
    o.append(tex(u + "-wb", wd, ["#4A3C74", "#2E2450", "#5A4A86", "#262046"], 16, (60, 130, 540, 500), n=300, angle=-12, length=(30, 90), width=(4, 10), op=(0.25, 0.55)))
    rnd = random.Random(3)
    rim = []
    for i in range(90):
        a = 2 * math.pi * i / 90 + rnd.uniform(-0.03, 0.03)
        rr = rnd.uniform(0.96, 1.04)
        x, y = 300 + 214 * rr * math.cos(a), 318 + 176 * rr * math.sin(a)
        rim.append(_lens(x, y, rnd.uniform(14, 34), rnd.uniform(1.5, 4), a + math.pi / 2, 2, rnd.choice(["#3A2E5E", "#4A3C74", "#2E2450"]), rnd.uniform(0.3, 0.7)))
    o.append("".join(rim))
    o.append(stars(17, 22, (120, 160, 480, 290), avoid=[(300, 330, 130)], tw=5, twr=(4, 7)))
    o.append(moon(u + "m", 432, 206, 26, 9, halo_r=2.2))
    o.append(pbat(178, 206, 16, -10) + pbat(212, 184, 10, 8))
    o.append(pglow(u + "mg", 300, 350, 200, "#FFB547", 0.5, 18))
    o.append(jack(u + "j", 300, 352, 236, 166, 19, "classic", glow_r=1, glow_op=0.0, night=False))
    o.append(pcandle(u + "c1", 132, 450, 76, 22, 20))
    o.append(pcandle(u + "c2", 164, 452, 46, 18, 21))
    o.append(pcandle(u + "c3", 462, 452, 62, 20, 22))
    o.append(jack(u + "j2", 506, 442, 58, 42, 23, None, lit=False, night=False, body="#F1E6D2", dark="#C9B79A", light="#FFFFFF"))
    o.append(ptext(u + "t1", 300, 132, "Happy", SERIF_IT, 92, "#4A2A5E", ["#2E1A40", "#6A4A86", "#5A3A70"], 24, max_w=320, angle=-55, shadow="#E2B47A"))
    o.append(ptext(u + "t2", 300, 534, "HALLOWEEN", BEBAS, 92, "#D2602A", ["#E8792E", "#9A3E14", "#F29A4A", "#B8481A"], 25, max_w=430, ls=6, angle=-80, shadow="#5A2410"))
    o.append(grain(u + "-gr", INKB, 5, 0.9))
    return "".join(o)



def d_broom_with_a_view():
    u = "gabrm"
    o = [sky(u, [(0, NIGHT0), (0.4, "#251E50"), (0.75, "#3E2F6E"), (1, "#56407E")], 81, swirl=(300, 286, 150, 250, "#D8C8F0"), n=460)]
    o.append(stars(82, 50, (20, 20, 580, 420), avoid=[(300, 286, 190), (300, 120, 60)]))
    o.append(moon(u, 300, 286, 150, 83, halo_r=1.6))
    o.append(cloud(u + "c1", 172, 352, 230, 14, 7, "#4A3A7A", "#C8B6E8", 0.7))
    o.append(cloud(u + "c2", 470, 236, 180, 12, 8, "#4A3A7A", "#D8C8F0", 0.55))
    # witch crossing the moon, sparkle trail behind the broom
    rnd = random.Random(9)
    trail = "".join(f'<path d="{blob(x, y, r, r, rnd.randrange(999), 0.2, 7)}" fill="{rnd.choice([CANDLE, GOLD, "#FFFFFF"])}" opacity="{rnd.uniform(0.4, 0.95):.2f}"/>'
                    for x, y, r in [(150 - i * 13 + rnd.uniform(-5, 5), 330 + i * 5 + rnd.uniform(-9, 9), rnd.uniform(1, 2.6)) for i in range(9)])
    o.append(trail + twinkle(118, 352, 7, CANDLE) + twinkle(76, 372, 5, CANDLE, 0.8))
    o.append(witch_sil(318, 300, 1.2))
    o.append(pbat(470, 150, 16, 10, 6) + pbat(506, 178, 10, -8) + pbat(110, 196, 12, -14))
    # village below
    o.append(soft(300, 520, 420, 90, "#8A70B0", u + "hz", 0.4))
    o.append(rooftops(u + "rt", 516, 84, spire_x=470))
    o.append(soft(300, 610, 360, 110, "#05030C", u + "fb", 0.7))
    o.append(ptext(u + "t1", 300, 136, "BROOM", BEBAS, 104, BONE, ["#FFFFFF", "#E8DCC4", "#D2C4EA"], 85, max_w=330, ls=18, shadow=INKN, hi="#FFFFFF"))
    o.append(ptext(u + "t2", 300, 540, "with a view", SERIF_IT, 70, GOLD, ["#FFE38A", "#F59A3A", "#FFF3C0", "#E8A030"], 86, max_w=360, angle=-58, shadow=INKN, glow="#FFB547", glow_op=0.3))
    o.append(finish(u, 5))
    return "".join(o)


def black_cat_on_broom(x, y, s=0.42):
    from halloween_painted import black_cat
    return black_cat("gabrmcat", x, y, s, fill=SIL, rim="#FFE9B0", eye="#D9F05A")


def d_haunted_hotel():
    u = "gahot"
    o = [sky(u, [(0, NIGHT0), (0.5, "#2A2156"), (1, "#3A2C66")], 91, n=300)]
    o.append(stars(92, 26, (20, 20, 580, 160), avoid=[(510, 70, 50)]))
    o.append(moon(u, 510, 70, 34, 93, halo_r=2.6))
    # the hotel facade: mansard roof with dormers, clapboard walls painted in dusky violet
    roof = hpath([(-10, 236), (36, 120), (564, 120), (610, 236)], 94, 1.4)
    o.append(pshape(u + "rf", roof, "#2A2040", ["#3A2E58", "#1E1630", "#463A6A"], 94, (-10, 110, 610, 240), angle=-70, length=(10, 24), width=(1.4, 3.2), n=260, line=INKN))
    rnd = random.Random(95)
    sh = "".join(f'<path d="M {x:.1f} {y:.1f} q 7 6 14 0" stroke="#4A3E70" stroke-width="1.6" fill="none" opacity="0.7"/>'
                 for y in range(132, 236, 11) for x in [rnd.uniform(-10, 600) for _ in range(30)])
    o.append(inside(u + "-sh", roof, sh))
    o.append(ink(hpath([(36, 120), (564, 120)], 96, 1, False), "#B8A6DC", 2.4, 96, 1, 0.7))
    # iron cresting along the roof ridge
    o.append(ink(" ".join(f"M {x} 120 L {x} 106 M {x - 4} 110 L {x} 104 L {x + 4} 110" for x in range(48, 560, 26)), SIL, 2.2, 97, 1, 1))
    wall = hpath([(0, 236), (600, 236), (600, 600), (0, 600)], 98, 1)
    o.append(pshape(u + "wl", wall, "#3E3462", ["#4A4072", "#342A56", "#564C80", "#2E2650"], 98, (0, 230, 600, 600), angle=-90, length=(16, 40), width=(2, 5), n=300))
    o.append(inside(u + "-cb", wall, "".join(f'<path d="M 0 {y} Q 300 {y + rnd.uniform(-2, 2):.1f} 600 {y + rnd.uniform(-1.5, 1.5):.1f}" stroke="#251E40" stroke-width="2" fill="none" opacity="0.7"/>' for y in range(250, 600, 15))))
    o.append(f'<rect x="0" y="236" width="600" height="10" fill="{SIL}"/>')
    # windows: a ghost peeking out, a candle, a cat, the warm lobby door
    o.append(window(u + "w1", 72, 376, 78, 104, 101, glow_op=0.35, figure=pghost(u + "wg", 111, 404, 50, 3, face="happy", arms=False, glow_op=0)))
    o.append(window(u + "w2", 450, 376, 78, 104, 102, glow_op=0.35, figure=pcandle(u + "wc", 489, 470, 30, 12, 7, glow_op=0.4)))
    o.append(f'<path d="M 68 480 L 154 480 L 160 490 L 62 490 Z" fill="{SIL}"/><path d="M 446 480 L 532 480 L 538 490 L 440 490 Z" fill="{SIL}"/>')
    from halloween_painted import black_cat
    o.append(black_cat(u + "cat", 504, 480, 0.36, fill=SIL, rim="#FFD27A", eye="#D9F05A", flip=True))
    o.append(pglow(u + "dg", 300, 520, 160, "#FFB547", 0.45, 103))
    o.append(window(u + "dr", 246, 430, 108, 190, 104, lit=("#FFD27A", "#F59A3A"), arch=True, glow_op=0.0))
    # striped awning over the door
    aw = hpath([(222, 434), (378, 434), (392, 468), (208, 468)], 105, 0.8)
    o.append(f'<path d="{aw}" fill="#7A2E3A"/>' + inside(u + "-aw", aw, "".join(f'<path d="M {x} 430 L {x + 6} 470 L {x + 22} 470 L {x + 16} 430 Z" fill="{BONE}" opacity="0.85"/>' for x in range(214, 392, 34))))
    o.append(ink(aw, INKN, 2, 105, 1, 0.8) + "".join(f'<path d="{blob(x, 470, 9, 5, x, 0.1, 8)}" fill="#7A2E3A"/>' for x in range(216, 392, 17)))
    # jack-o'-lanterns by the door
    o.append(jack(u + "j1", 192, 548, 66, 48, 106, "toothy", glow_r=80))
    o.append(jack(u + "j2", 410, 552, 58, 42, 107, "cute", glow_r=72))
    # the hanging sign, chains from the porch roof above
    o.append(ink("M 132 -4 L 132 92 M 468 -4 L 468 92", "#1A1426", 4, 108, 1, 1))
    o.append("".join(f'<ellipse cx="{x}" cy="{y}" rx="3.4" ry="5.5" fill="none" stroke="#8A7AA8" stroke-width="1.6"/>' for x in (132, 468) for y in range(4, 92, 10)))
    board = hpath([(84, 96), (300, 82), (516, 96), (522, 268), (78, 268)], 109, 1.2)
    o.append(f'<path d="{board}" fill="#000" opacity="0.35" transform="translate(5 8)"/>')
    o.append(pshape(u + "bd", board, "#3A2418", ["#5A3A24", "#2A180E", "#6E4A2E", "#4A2E1A"], 109, (76, 80, 524, 270), angle=-2, length=(30, 80), width=(1.5, 4), n=260, line="#1A0E08", lw=2.6))
    inner = hpath([(98, 108), (300, 96), (502, 108), (506, 256), (94, 256)], 110, 0.8)
    o.append(ink(inner, GOLD, 2.6, 110, 2, 0.85))
    o.append("".join(f'<circle cx="{x}" cy="{y}" r="3.2" fill="#C8A060"/>' for x, y in ((92, 104), (508, 104), (92, 260), (508, 260))))
    o.append(soft(300, 160, 200, 60, SLIME, u + "-sg", 0.25))
    o.append(ptext(u + "t1", 300, 176, "Haunted", SERIF_IT, 92, "#C6F27A", ["#E6FFB0", SLIME, "#B8E86A", "#FFFFFF"], 111, max_w=360, angle=-58, shadow="#0E1A06",
                   glow=SLIME, glow_op=0.3, hi="#FFFFFF"))
    o.append(ptext(u + "t2", 300, 240, "HOTEL", BEBAS, 62, GOLD, ["#FFE38A", "#E8A030", "#FFF3C0"], 112, max_w=260, ls=22, shadow="#1A0E08"))
    o.append(twinkle(132, 222, 7, GOLD) + twinkle(468, 222, 7, GOLD))
    # little 'no vacancy' plaque swinging under the sign
    o.append(ink("M 236 268 L 240 292 M 364 268 L 360 292", "#1A1426", 2.4, 113, 1, 1))
    pl = hpath([(214, 290), (386, 290), (386, 326), (214, 326)], 114, 0.8)
    o.append(f'<g transform="rotate(-3 300 308)">' + pshape(u + "pl", pl, "#1E1630", ["#2A2040", "#16101F"], 114, (210, 286, 390, 330), angle=0, length=(20, 40), width=(1, 2.4), n=40, line="#8A7AA8", lw=1.6)
             + ptext(u + "t3", 300, 317, "NO VACANCY", BEBAS, 26, "#FF8A9A", ["#FFC2CC", "#FF6A80"], 115, max_w=150, ls=4, glow="#FF4A6A", glow_op=0.3) + "</g>")
    o.append(pbat(64, 330, 14, -12) + pbat(548, 340, 12, 10))
    o.append(finish(u, 6, vign=0.45))
    return "".join(o)


def d_trick_or_treat():
    u = "gatot"
    o = [sky(u, [(0, "#0F0C26"), (1, "#2A1E4A")], 121, box=(0, 0, 600, 240), n=160)]
    o.append(stars(122, 30, (20, 16, 580, 120), avoid=[(520, 80, 40)], tw=4))
    o.append(moon(u, 520, 80, 24, 123, halo_r=2.6))
    # house facade, roof eave, clapboards
    wall = hpath([(-10, 210), (300, 140), (610, 210), (610, 600), (-10, 600)], 124, 1.2)
    o.append(pshape(u + "wl", wall, "#4A3E6E", ["#56497E", "#3A3060", "#62568C", "#2E2652"], 124, (-10, 140, 610, 600), angle=-90, length=(16, 40), width=(2, 5), n=320))
    rnd = random.Random(125)
    o.append(inside(u + "-cb", wall, "".join(f'<path d="M -10 {y} Q 300 {y + rnd.uniform(-2, 2):.1f} 610 {y + rnd.uniform(-1.5, 1.5):.1f}" stroke="#2A2248" stroke-width="2" fill="none" opacity="0.65"/>' for y in range(214, 600, 14))))
    eave = hpath([(-10, 196), (300, 122), (610, 196), (610, 214), (300, 142), (-10, 214)], 126, 1)
    o.append(f'<path d="{eave}" fill="{SIL}"/>' + ink(hpath([(-10, 196), (300, 122), (610, 196)], 126, 1, False), "#9C8AC8", 2.2, 126, 1, 0.6))
    # porch roof
    pr = hpath([(30, 262), (570, 262), (592, 284), (8, 284)], 127, 1)
    o.append(f'<path d="{pr}" fill="{SIL}"/>' + ink(hpath([(30, 262), (570, 262)], 128, 0.8, False), "#9C8AC8", 2, 128, 1, 0.6))
    # windows, warm
    o.append(window(u + "w1", 80, 318, 92, 108, 129, glow_op=0.35, figure=f'<path d="M 96 426 L 96 404 Q 102 392 112 396 L 116 386 L 120 398 Q 130 404 126 426 Z" fill="#3A1E22"/>'))
    o.append(window(u + "w2", 428, 318, 92, 108, 130, glow_op=0.35))
    for wx in (72, 420):
        o.append(f'<path d="{hpath([(wx, 426), (wx + 108, 426), (wx + 112, 436), (wx - 4, 436)], wx, 0.6)}" fill="{SIL}"/>')
    # bat garland
    o.append(ink("M 430 330 Q 474 350 518 330", "#2A1E36", 1.6, 131, 1, 0.9) + pbat(452, 342, 9, 8) + pbat(476, 346, 9, 0) + pbat(500, 340, 9, -8))
    # the open door with light pouring out
    o.append(pglow(u + "dg", 300, 392, 190, "#FFB547", 0.55, 132))
    o.append(f'<path d="{hpath([(240, 296), (360, 296), (360, 472), (240, 472)], 133, 0.8)}" fill="{SIL}"/>')
    o.append(window(u + "dr", 250, 306, 100, 166, 134, lit=("#FFD98A", "#F59A3A"), glow_op=0.0))
    door = hpath([(250, 306), (288, 316), (288, 462), (250, 472)], 135, 0.6)
    o.append(pshape(u + "dd", door, "#6A2E2A", ["#8A3E34", "#4A1E1C", "#9A4A3E"], 135, (246, 300, 292, 476), angle=-90, length=(20, 50), width=(1.5, 3.5), n=60, line=INKN, lw=1.8))
    o.append(f'<circle cx="283" cy="398" r="3.4" fill="{GOLD}"/>')
    # porch lamp
    o.append(pglow(u + "pl", 388, 316, 50, "#FFD27A", 0.8, 136) + f'<path d="{hpath([(380, 304), (396, 304), (398, 330), (378, 330)], 137, 0.5)}" fill="{CANDLE}"/>' + ink(hpath([(380, 304), (396, 304), (398, 330), (378, 330)], 137, 0.5), INKN, 2.6, 137, 1, 1))
    # porch posts
    for px in (40, 546):
        post = hpath([(px, 284), (px + 14, 284), (px + 14, 600), (px, 600)], px, 0.6)
        o.append(pshape(u + f"po{px}", post, SIL2, ["#2E2448", "#16101F"], px, (px - 2, 280, px + 16, 600), angle=-90, length=(20, 50), width=(1, 2.5), n=30, line=INKN, lw=1.6))
    # floor + steps, light spilling down
    fl = hpath([(-10, 472), (610, 472), (610, 600), (-10, 600)], 138, 1)
    o.append(pshape(u + "fl", fl, "#4A2E26", ["#5E3A2E", "#3A221C", "#6E4636"], 138, (-10, 470, 610, 600), angle=0, length=(30, 80), width=(1.5, 3.5), n=160))
    for i, (y, w) in enumerate(((476, 210), (504, 268), (532, 326), (560, 384))):
        st = hpath([(300 - w / 2, y), (300 + w / 2, y), (300 + w / 2, y + 28), (300 - w / 2, y + 28)], 140 + i, 0.8)
        o.append(pshape(u + f"st{i}", st, "#6A4234", ["#7E5040", "#4E3024", "#8E6048"], 140 + i, (300 - w / 2, y, 300 + w / 2, y + 28), angle=0, length=(30, 70), width=(1.2, 3), n=50, line=INKN, lw=1.6))
        o.append(ink(f"M {300 - w / 2 + 3:.1f} {y + 3} L {300 + w / 2 - 3:.1f} {y + 3}", "#C8906A", 2.4, 140 + i, 1, 0.75))
    o.append(f'<path d="M 250 472 L 350 472 L 430 600 L 170 600 Z" fill="#FFC560" opacity="0.16"/>')
    # pumpkins on the steps
    o.append(jack(u + "p1", 150, 484, 76, 54, 141, "toothy", glow_r=95))
    o.append(jack(u + "p2", 452, 486, 82, 58, 142, "classic", glow_r=100))
    o.append(jack(u + "p3", 504, 528, 54, 40, 143, "cute", glow_r=70))
    o.append(jack(u + "p4", 96, 528, 50, 36, 144, None, lit=False, body="#F1E6D2", dark="#B9A68A", light="#FFFFFF"))
    # trick-or-treaters, backlit
    from halloween_painted import kid
    o.append(kid(258, 532, 102, "ghost", fill=SIL, rim="#FFC46A"))
    o.append(kid(340, 528, 110, "witch", fill=SIL, rim="#FFC46A"))
    o.append(kid(300, 556, 78, "cat", fill=SIL, rim="#FFC46A"))
    o.append(finish(u, 7, vign=0.4))
    # type over the night sky
    o.append(ruled(300, 84, "OCTOBER 31", MONO, 18, CANDLE, ls=7, seed=145, shadow=INKN))
    o.append(ptext(u + "t1", 168, 192, "TRICK", BEBAS, 92, BONE, ["#FFFFFF", "#E6D8C0", "#D2C4EA"], 146, max_w=230, ls=4, shadow=INKN, hi="#FFFFFF"))
    o.append(ptext(u + "t2", 300, 180, "or", SERIF_IT, 58, GOLD, ["#FFE38A", "#F59A3A"], 147, max_w=70, angle=-58, shadow=INKN, glow="#FF9A2E", glow_op=0.35))
    o.append(ptext(u + "t3", 432, 192, "TREAT", BEBAS, 92, BONE, ["#FFFFFF", "#E6D8C0", "#D2C4EA"], 148, max_w=230, ls=4, shadow=INKN, hi="#FFFFFF"))
    return "".join(o)


def bottle_path(cx, base, w, h, neck_w, neck_h):
    """Squat apothecary bottle: round shoulders, short neck with a lip."""
    l, r = cx - w / 2, cx + w / 2
    top = base - h
    sh = top + neck_h
    nl, nr = cx - neck_w / 2, cx + neck_w / 2
    return (f"M {l + 14:.1f} {base:.1f} Q {l:.1f} {base:.1f} {l:.1f} {base - 16:.1f} L {l:.1f} {sh + w * 0.24:.1f} "
            f"C {l:.1f} {sh + 6:.1f} {nl - 6:.1f} {sh + 10:.1f} {nl:.1f} {sh:.1f} L {nl:.1f} {top + 14:.1f} "
            f"L {nl - 7:.1f} {top + 8:.1f} L {nl - 6:.1f} {top:.1f} L {nr + 6:.1f} {top:.1f} L {nr + 7:.1f} {top + 8:.1f} L {nr:.1f} {top + 14:.1f} "
            f"L {nr:.1f} {sh:.1f} C {nr + 6:.1f} {sh + 10:.1f} {r:.1f} {sh + 6:.1f} {r:.1f} {sh + w * 0.24:.1f} L {r:.1f} {base - 16:.1f} "
            f"Q {r:.1f} {base:.1f} {r - 14:.1f} {base:.1f} Z")


def d_eye_of_newt():
    u = "ganewt"
    o = [sky(u, [(0, "#1E1428"), (0.6, "#2E1E30"), (1, "#3A2630")], 151, n=320, angle=-80, length=(40, 120), amt=0.14)]
    o.append(pglow(u + "cg", 112, 300, 300, "#FFB547", 0.35, 152, rings=3))
    from halloween_painted import spider, web
    wg, wd = web(u + "wb", 600, 0, [(a, 230 - abs(a - 135) * 0.8) for a in range(92, 182, 13)], list(range(34, 220, 30)), 153, col="#B8A890", sw=1.6)
    o.append(f'<g opacity="0.4">{wg}</g>{wd}')
    o.append(ink("M 488 -4 L 488 290", "#B8A890", 1.5, 153, 1, 0.7) + spider(u + "sp", 488, 302, 12, body=("#7A6A8E", "#3A2E4E", "#1A1226")))
    # shelf
    sh = hpath([(-10, 500), (610, 494), (610, 532), (-10, 538)], 153, 1)
    o.append(pshape(u + "sh", sh, "#5A3624", ["#6E4430", "#3E2416", "#8A5A3A"], 153, (-10, 490, 610, 540), angle=0, length=(40, 100), width=(1.2, 3), n=120, line="#1A0E08"))
    o.append(ink("M -10 500 L 610 494", "#E8B070", 2.4, 154, 1, 0.6))
    o.append(f'<rect x="0" y="536" width="600" height="64" fill="#140C14"/>' + tex(u + "-ub", "M 0 536 L 600 536 L 600 600 L 0 600 Z", ["#2A1A1E", "#0E080C"], 155, (0, 536, 600, 600), n=60, angle=0))
    # candle on the left
    o.append(pcandle(u + "c", 104, 498, 150, 34, 156, glow_r=150, glow_op=0.55))
    o.append(f'<path d="{blob(104, 498, 40, 7, 157, 0.08)}" fill="#8A6A3A"/><path d="{blob(104, 494, 34, 6, 158, 0.08)}" fill="#B8955A"/>')
    # small jar on the right with a floating eyeball in slime
    jar = hpath([(452, 498), (452, 420), (446, 412), (446, 402), (530, 402), (530, 412), (524, 420), (524, 498)], 159, 0.6)
    o.append(pglow(u + "jg", 488, 456, 80, SLIME, 0.35, 160))
    o.append(f'<path d="{jar}" fill="#2E4A2A"/>')
    liquid = hpath([(454, 496), (454, 436), (522, 436), (522, 496)], 161, 0.5)
    o.append(f'<path d="{liquid}" fill="{SLIME}" opacity="0.85"/>' + tex(u + "-lq", liquid, ["#C6F27A", "#6FA83A", "#E6FFB0"], 162, (450, 430, 526, 500), n=40, angle=-90, length=(8, 20), width=(1, 3)))
    o.append(f'<circle cx="486" cy="468" r="15" fill="{BONE}"/><circle cx="491" cy="466" r="7" fill="#5A8ACA"/><circle cx="492" cy="466" r="3.4" fill="#120C16"/><circle cx="489" cy="463" r="1.6" fill="#FFF"/>'
             + ink("M 473 474 q 4 2 6 -1 M 474 462 q 5 0 6 3", "#C2577A", 1.2, 163, 1, 0.8))
    o.append("".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#E6FFB0" stroke-width="1.4" opacity="0.8"/>' for x, y, r in ((468, 446, 3), (508, 452, 2.4), (500, 486, 2.2))))
    o.append(f'<path d="{jar}" fill="#BFE6D8" opacity="0.12"/>' + ink("M 462 424 L 462 488", "#FFFFFF", 3, 164, 1, 0.45) + ink(jar, "#0E1A10", 2, 165, 2, 0.8))
    o.append(f'<path d="{hpath([(442, 390), (534, 390), (534, 404), (442, 404)], 166, 0.6)}" fill="#7A5A3A"/>' + ink(hpath([(442, 390), (534, 390), (534, 404), (442, 404)], 166, 0.6), "#1A0E08", 1.6, 166, 1, 0.8))
    # the big bottle
    bd = bottle_path(300, 498, 250, 372, 64, 76)
    o.append(f'<path d="{blob(300, 500, 140, 9, 167, 0.05)}" fill="#000" opacity="0.4"/>')
    o.append(pshape(u + "bt", bd, "#2E5A3E", ["#3E7050", "#1E4030", "#4E8A5E", "#2A4E36"], 167, (170, 120, 430, 500), angle=-90, length=(30, 80), width=(2, 6), n=200,
                    shade=("#0E2418", 0.7, 26, 0), line="#0A1A10", lw=2.8))
    o.append(inside(u + "-bl", bd, soft(196, 300, 60, 160, "#FFC870", u + "-blg", 0.35)))
    o.append(ink("M 196 260 Q 190 340 198 460", "#FFFFFF", 6, 168, 1, 0.45) + ink("M 212 206 Q 220 200 230 196", "#FFFFFF", 4, 169, 1, 0.5) + ink("M 404 280 L 404 440", "#9AD0A8", 3, 170, 1, 0.4))
    # cork and twine
    cork = hpath([(270, 106), (330, 106), (326, 140), (274, 140)], 171, 0.6)
    o.append(pshape(u + "ck", cork, "#B88A5A", ["#D8AA72", "#8A6038", "#E8C090"], 171, (268, 100, 332, 142), angle=-90, length=(6, 14), width=(1, 2), n=30, line="#3A2010", lw=1.8))
    o.append(f'<path d="{blob(300, 106, 30, 6, 172, 0.06)}" fill="#E0B47E"/>')
    o.append(ink("M 266 150 Q 300 158 334 150 M 268 156 Q 300 164 332 156", "#C8A878", 2.4, 173, 1, 0.9) + ink("M 330 154 Q 352 172 348 198", "#C8A878", 2, 174, 1, 0.9))
    tag = hpath([(334, 198), (364, 190), (372, 222), (342, 230)], 175, 0.5)
    o.append(pshape(u + "tg", tag, BONE, ["#FFFFFF", BONE_D], 175, (330, 186, 376, 234), angle=-80, n=12, line=INKB, lw=1.4) + f'<circle cx="345" cy="202" r="2.4" fill="#3A2418"/>'
             + f'<text x="354" y="220" text-anchor="middle" {DMS} font-size="16" fill="#7A2E1E" transform="rotate(-14 354 220)">13</text>')
    # the paper label
    lab = hpath([(196, 248), (404, 242), (408, 462), (192, 468)], 176, 1.2)
    o.append(f'<path d="{lab}" fill="#000" opacity="0.3" transform="translate(4 5)"/>')
    o.append(pshape(u + "lb", lab, "#F2E6CC", ["#FFFFFF", "#E2D2B0", "#EADCBC", "#D8C49E"], 176, (190, 236, 410, 462), angle=-6, length=(20, 60), width=(2, 5), n=120,
                    shade=("#B89A6E", 0.35, 6, 6), line=INKB, lw=2))
    o.append(ink(hpath([(206, 258), (394, 253), (397, 452), (203, 457)], 177, 0.8), "#7A2E1E", 2, 177, 1, 0.85) + ink(hpath([(212, 264), (388, 259), (391, 446), (209, 451)], 178, 0.6), "#7A2E1E", 1, 178, 1, 0.6))
    o.append(label(300, 284, "APOTHECARY · NO.13", MONO, 16, "#5A3A2A", ls=1, max_w=176))
    o.append(ptext(u + "t1", 300, 340, "EYE", CINZEL, 62, "#2A1A24", ["#4A2A3A", "#1A0E16", "#3A2030"], 179, max_w=150, ls=8, angle=-80))
    o.append(ptext(u + "t2", 300, 368, "of", SERIF_IT, 34, "#7A2E1E", ["#9A3E2A", "#5A1E10"], 180, max_w=60, angle=-58))
    o.append(ptext(u + "t3", 300, 414, "NEWT", CINZEL, 56, "#2A1A24", ["#4A2A3A", "#1A0E16", "#3A2030"], 181, max_w=170, ls=6, angle=-80))
    o.append(ink("M 236 424 L 364 422", "#7A2E1E", 1.6, 182, 1, 0.8))
    o.append(label(300, 446, "LOCALLY SOURCED", MONO, 16, "#5A3A2A", ls=1.5, max_w=170))
    o.append(newt(u + "nw", 300, 488, 0.9))
    o.append(finish(u, 8, vign=0.5))
    return "".join(o)


def newt(u, cx, cy, s, body="#E8792E", belly="#FFC24A", spots="#5A1E10"):
    """A small painted newt curling along the shelf (cute, orange, spotted)."""
    def T(x, y):
        return cx + x * s, cy + y * s
    spine = [T(-110, 4), T(-80, -6), T(-40, -2), T(0, -8), T(40, -4), T(70, -10), T(96, -6)]
    widths = [1, 2.4, 5, 8, 8.5, 7, 6]
    left, right = [], []
    for i, (x, y) in enumerate(spine):
        x2, y2 = spine[min(i + 1, len(spine) - 1)]
        x1, y1 = spine[max(i - 1, 0)]
        L = math.hypot(x2 - x1, y2 - y1) or 1
        nx, ny = -(y2 - y1) / L, (x2 - x1) / L
        left.append((x + nx * widths[i] * s, y + ny * widths[i] * s))
        right.append((x - nx * widths[i] * s, y - ny * widths[i] * s))
    hx, hy = T(106, -7)
    pts = left + [T(104, 2), T(114, -4), T(112, -14), T(100, -16)] + right[::-1]
    d = smooth_closed(pts)
    out = []
    for lx, ly, dx, dy in ((-24, 2, -8, 12), (-20, -10, -10, -10), (52, -2, 8, 12), (56, -14, 10, -8)):
        x0, y0 = T(lx, ly)
        out.append(ink(f"M {x0:.1f} {y0:.1f} q {dx * s * 0.6:.1f} {dy * s * 0.2:.1f} {dx * s:.1f} {dy * s:.1f}", body, 4 * s, int(lx), 1, 1))
        out.append("".join(f'<circle cx="{x0 + dx * s + ex * s:.1f}" cy="{y0 + dy * s + ey * s:.1f}" r="{1.6 * s:.1f}" fill="{body}"/>' for ex, ey in ((-2, 1), (0, 2.4), (2, 1))))
    out.append(pshape(u, d, body, [belly, "#F59A48", "#C8581E"], 7, (cx - 120 * s, cy - 24 * s, cx + 120 * s, cy + 14 * s), angle=0, length=(8, 20), width=(1, 2), n=50, line="#5A1E10", lw=1.4))
    rnd = random.Random(3)
    out.append("".join(f'<circle cx="{x:.1f}" cy="{y + rnd.uniform(-2, 2) * s:.1f}" r="{rnd.uniform(1.2, 2.2) * s:.1f}" fill="{spots}" opacity="0.8"/>' for x, y in spine[2:6]))
    ex, ey = T(104, -10)
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{3 * s:.1f}" fill="#1A0E08"/><circle cx="{ex + 0.8 * s:.1f}" cy="{ey - 0.9 * s:.1f}" r="{1 * s:.1f}" fill="#FFF"/>')
    mx, my = T(110, -3)
    out.append(ink(f"M {mx - 6 * s:.1f} {my:.1f} q {3 * s:.1f} {2 * s:.1f} {6 * s:.1f} 0", "#5A1E10", 1.2, 2, 1, 0.9))
    return "".join(out)



# ---------------------------------------------------------------- more painted pieces (set A, part 2)
def cauldron(u, cx, rim_y, w, h, seed, brew=SLIME, brew_d=SLIME_D, brew_l="#E6FFB0"):
    """Gouache iron cauldron: round belly, rolled rim, shade side, fire-lit underside, a glowing brew that
    bubbles over the lip and drips down the iron."""
    rnd = random.Random(seed)
    l, r = cx - w / 2, cx + w / 2
    base = rim_y + h
    out = []
    # stubby legs (behind the belly)
    for lx in (cx - w * 0.3, cx + w * 0.3):
        leg = hpath([(lx - 12, base - 20), (lx + 12, base - 20), (lx + 9, base + 22), (lx + 16, base + 30), (lx - 16, base + 30), (lx - 9, base + 22)], seed + int(lx), 0.8)
        out.append(f'<path d="{leg}" fill="#1A1422"/>' + ink(leg, INKN, 2, seed, 1, 0.8))
    body = smooth_closed([(l + 8, rim_y), (l - w * 0.07, rim_y + h * 0.36), (l + w * 0.05, rim_y + h * 0.78), (cx - w * 0.2, base),
                          (cx + w * 0.2, base), (r - w * 0.05, rim_y + h * 0.78), (r + w * 0.07, rim_y + h * 0.36), (r - 8, rim_y)])
    out.append(pshape(f"{u}-bd", body, "#2C2638", ["#3A3248", "#1A1424", "#4A4060", "#241E30"], seed, (l - w * 0.1, rim_y, r + w * 0.1, base + 4),
                      angle=0, length=(30, 80), width=(2, 6), n=170, op=(0.3, 0.6), curve=0.35, shade=("#08060E", 0.6, w * 0.09, 0)))
    lit = (soft(cx, base + 6, w * 0.55, h * 0.42, "#FF8A2A", f"{u}-fl", 0.55)
           + soft(cx - w * 0.28, rim_y + h * 0.18, w * 0.32, h * 0.3, brew, f"{u}-gl", 0.28)
           + f'<path d="M {l + w * 0.06:.1f} {rim_y + h * 0.25:.1f} Q {l + w * 0.0:.1f} {rim_y + h * 0.5:.1f} {l + w * 0.12:.1f} {rim_y + h * 0.78:.1f}" stroke="#D8CCF0" stroke-width="7" fill="none" stroke-linecap="round" opacity="0.28"/>'
           + f'<path d="M {l + w * 0.1:.1f} {rim_y + h * 0.3:.1f} Q {l + w * 0.06:.1f} {rim_y + h * 0.48:.1f} {l + w * 0.13:.1f} {rim_y + h * 0.66:.1f}" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round" opacity="0.4"/>')
    out.append(inside(f"{u}-lt", body, lit))
    out.append(ink(body, INKN, 2.8, seed + 3, 2, 0.85))
    # rolled rim and the brew inside it
    rim = blob(cx, rim_y, w / 2 + 12, 22, seed + 4, 0.02, 24)
    out.append(f'<path d="{rim}" fill="#3A3248"/>' + ink(rim, INKN, 2.6, seed + 4, 1, 0.9))
    out.append(defs(rg(f"{u}-bw", [(0, brew_l), (0.45, brew), (1, brew_d)], cy=0.4, r=0.65)))
    surf = blob(cx, rim_y + 1, w / 2 - 6, 13, seed + 5, 0.03, 22)
    out.append(f'<path d="{surf}" fill="url(#{u}-bw)"/>')
    out.append(inside(f"{u}-sf", surf, "".join(_lens(rnd.uniform(l, r - 30), rim_y + rnd.uniform(-12, 10), rnd.uniform(20, 50), rnd.uniform(1, 2.6), math.radians(rnd.uniform(-4, 4)), 1,
                                                      rnd.choice([brew_l, "#FFFFFF", brew_d]), rnd.uniform(0.25, 0.6)) for _ in range(40))))
    # front lip lit by the brew
    out.append(ink(f"M {l - 6:.1f} {rim_y + 4:.1f} Q {cx:.1f} {rim_y + 36:.1f} {r + 6:.1f} {rim_y + 4:.1f}", "#C6F27A", 3, seed + 6, 1, 0.55))
    out.append(ink(f"M {l + 4:.1f} {rim_y - 8:.1f} Q {cx:.1f} {rim_y - 30:.1f} {r - 4:.1f} {rim_y - 8:.1f}", "#7A6A9A", 2.4, seed + 7, 1, 0.6))
    # bubbles breaking the surface and rising
    bub = []
    for i in range(12):
        bx = cx + rnd.uniform(-0.34, 0.34) * w
        by = rim_y - rnd.uniform(0, 6) - (rnd.uniform(16, 80) if i > 5 else 0)
        br = rnd.uniform(5, 11) if i <= 5 else rnd.uniform(3, 7)
        d = blob(bx, by, br, br * 0.92, seed + 20 + i, 0.08, 10)
        bub.append(f'<path d="{d}" fill="{brew}" opacity="{0.95 if i <= 5 else 0.7}"/>' + ink(d, brew_d, 1.6, seed + i, 1, 0.8)
                   + f'<path d="M {bx - br * 0.5:.1f} {by - br * 0.1:.1f} q {br * 0.15:.1f} {-br * 0.45:.1f} {br * 0.55:.1f} {-br * 0.5:.1f}" stroke="#FFFFFF" stroke-width="{max(1.2, br * 0.22):.1f}" fill="none" stroke-linecap="round" opacity="0.85"/>')
    out.append("".join(bub))
    # overflow drips running down the iron
    for i, (t, L) in enumerate(((-0.33, 26), (-0.12, 50), (0.2, 34), (0.38, 14))):
        x = cx + t * w
        y0 = rim_y + 8 + (1 - abs(t) * 2) * 14
        dw = rnd.uniform(6, 8.5)
        dd = (f"M {x - dw - 6:.1f} {y0 - 12:.1f} Q {x - dw:.1f} {y0 - 4:.1f} {x - dw:.1f} {y0 + 4:.1f} L {x - dw * 0.8:.1f} {y0 + L:.1f} "
              f"Q {x:.1f} {y0 + L + dw * 2:.1f} {x + dw * 0.8:.1f} {y0 + L:.1f} L {x + dw:.1f} {y0 + 4:.1f} Q {x + dw:.1f} {y0 - 4:.1f} {x + dw + 6:.1f} {y0 - 12:.1f} Z")
        out.append(f'<path d="{dd}" fill="{brew}"/>' + ink(dd, brew_d, 1.6, seed + 30 + i, 1, 0.75)
                   + f'<path d="M {x - dw * 0.35:.1f} {y0 + 2:.1f} L {x - dw * 0.3:.1f} {y0 + L - 2:.1f}" stroke="{brew_l}" stroke-width="2.2" stroke-linecap="round" opacity="0.8"/>')
    return "".join(out)


def vapor(u, cx, y0, w, h, seed, cols=("#E6FFB0", "#C6F27A", "#FFFFFF", "#9BD14B"), n=9):
    """Curling painted steam: long tapering wisps that wander upward."""
    rnd = random.Random(seed)
    out = [soft(cx, y0 - h * 0.45, w * 0.7, h * 0.65, SLIME, f"{u}-vg", 0.3)]
    for i in range(n):
        x = cx + rnd.uniform(-0.4, 0.4) * w
        pts = []
        ph = rnd.uniform(0, 6.28)
        amp = rnd.uniform(12, 26)
        top = y0 - h * rnd.uniform(0.55, 1.0)
        for k in range(8):
            t = k / 7
            pts.append((x + math.sin(ph + t * 5.2) * amp * (0.4 + t), y0 - (y0 - top) * t))
        path = smooth_open(pts)
        wd = rnd.uniform(4, 10)
        out.append(f'<path d="{path}" stroke="{rnd.choice(cols)}" stroke-width="{wd:.1f}" fill="none" stroke-linecap="round" opacity="{rnd.uniform(0.14, 0.3):.2f}"/>')
        out.append(f'<path d="{path}" stroke="#FFFFFF" stroke-width="{wd * 0.3:.1f}" fill="none" stroke-linecap="round" opacity="{rnd.uniform(0.12, 0.3):.2f}"/>')
    return "".join(out)


def toadstool(u, x, base, h, seed, cap="#C8402A", cap_l="#E86A4A", lean=0):
    w = h * 1.1
    stem = smooth_closed([(x - w * 0.14, base), (x - w * 0.11, base - h * 0.62), (x + w * 0.11 + lean, base - h * 0.62), (x + w * 0.15, base)])
    out = [f'<ellipse cx="{x:.1f}" cy="{base:.1f}" rx="{w * 0.36:.1f}" ry="{h * 0.07:.1f}" fill="#000" opacity="0.3"/>',
           pshape(f"{u}-st", stem, BONE, ["#FFFFFF", BONE_D, "#E8DCC4"], seed, (x - w * 0.2, base - h * 0.7, x + w * 0.2, base), angle=-90, n=14,
                  length=(h * 0.15, h * 0.35), width=(0.8, 2), shade=("#A8987E", 0.6, w * 0.05, 0), line=INKB, lw=1.6)]
    capd = (f"M {x - w / 2 + lean:.1f} {base - h * 0.56:.1f} C {x - w * 0.46 + lean:.1f} {base - h * 1.08:.1f} {x + w * 0.46 + lean:.1f} {base - h * 1.08:.1f} "
            f"{x + w / 2 + lean:.1f} {base - h * 0.56:.1f} Q {x + lean:.1f} {base - h * 0.66:.1f} {x - w / 2 + lean:.1f} {base - h * 0.56:.1f} Z")
    out.append(pshape(f"{u}-cp", capd, cap, [cap_l, "#8A2A1A", "#F08A5A"], seed + 1, (x - w / 2 + lean, base - h * 1.1, x + w / 2 + lean, base - h * 0.5),
                      angle=-30, n=30, length=(h * 0.15, h * 0.4), width=(1, 2.6), shade=("#6A1A10", 0.55, w * 0.08, h * 0.04), line="#4A140C", lw=1.8))
    rnd = random.Random(seed)
    for _ in range(5):
        a = rnd.uniform(-0.8, 0.8)
        dx, dy = math.sin(a) * w * 0.32, -math.cos(a) * h * 0.3
        out.append(f'<path d="{blob(x + lean + dx, base - h * 0.74 + dy * 0.9, w * 0.05, w * 0.04, rnd.randrange(99), 0.15, 8)}" fill="{BONE}"/>')
    return "".join(out)


def flask(u, cx, base, w, h, seed, liquid=("#C89AF0", "#8A4AC8", "#5A2A8A"), glow_op=0.45, level=0.55, cork="#B88A5A", line=INKN):
    """Round-bellied potion flask with a glowing liquid, cork and glass highlights."""
    rnd = random.Random(seed)
    r = w / 2
    cy = base - r
    nw = w * 0.26
    top = base - h
    d = (f"M {cx - nw / 2:.1f} {top + h * 0.1:.1f} L {cx - nw / 2:.1f} {cy - r * 0.8:.1f} "
         f"C {cx - r * 1.05:.1f} {cy - r * 0.6:.1f} {cx - r * 1.1:.1f} {base:.1f} {cx:.1f} {base:.1f} "
         f"C {cx + r * 1.1:.1f} {base:.1f} {cx + r * 1.05:.1f} {cy - r * 0.6:.1f} {cx + nw / 2:.1f} {cy - r * 0.8:.1f} L {cx + nw / 2:.1f} {top + h * 0.1:.1f} Z")
    out = []
    if glow_op:
        out.append(pglow(f"{u}-fg", cx, cy, w * 1.3, liquid[1], glow_op, seed))
    out.append(f'<ellipse cx="{cx:.1f}" cy="{base + 1:.1f}" rx="{r * 0.9:.1f}" ry="{max(3, r * 0.12):.1f}" fill="#000" opacity="0.35"/>')
    out.append(f'<path d="{d}" fill="#2A2440" opacity="0.55"/>')
    ly = base - w * level
    out.append(defs(rg(f"{u}-lq", [(0, liquid[0]), (0.6, liquid[1]), (1, liquid[2])], cy=0.65, r=0.7)))
    liq = f'<rect x="{cx - w:.1f}" y="{ly:.1f}" width="{2 * w:.1f}" height="{w:.1f}" fill="url(#{u}-lq)"/>'
    liq += "".join(f'<circle cx="{cx + rnd.uniform(-r * 0.6, r * 0.6):.1f}" cy="{rnd.uniform(ly + 4, base - 4):.1f}" r="{rnd.uniform(1.2, 2.8):.1f}" fill="none" stroke="{liquid[0]}" stroke-width="1.2" opacity="0.9"/>' for _ in range(5))
    liq += f'<path d="M {cx - w:.1f} {ly:.1f} Q {cx:.1f} {ly + 4:.1f} {cx + w:.1f} {ly:.1f}" stroke="{liquid[0]}" stroke-width="2.4" fill="none" opacity="0.9"/>'
    out.append(inside(f"{u}-in", d, liq))
    out.append(inside(f"{u}-hl", d, f'<path d="M {cx - r * 0.62:.1f} {cy - r * 0.2:.1f} Q {cx - r * 0.7:.1f} {cy + r * 0.3:.1f} {cx - r * 0.42:.1f} {cy + r * 0.62:.1f}" stroke="#FFFFFF" stroke-width="{max(2, w * 0.06):.1f}" fill="none" stroke-linecap="round" opacity="0.6"/>'
                                         f'<path d="M {cx - nw * 0.2:.1f} {top + h * 0.14:.1f} L {cx - nw * 0.2:.1f} {cy - r * 0.9:.1f}" stroke="#FFFFFF" stroke-width="{max(1.4, w * 0.035):.1f}" opacity="0.5"/>'))
    out.append(ink(d, line, max(1.6, w * 0.035), seed, 2, 0.85))
    ck = hpath([(cx - nw * 0.62, top - h * 0.04), (cx + nw * 0.62, top - h * 0.04), (cx + nw * 0.52, top + h * 0.13), (cx - nw * 0.52, top + h * 0.13)], seed, 0.4)
    out.append(pshape(f"{u}-ck", ck, cork, ["#D8AA72", "#8A6038"], seed, (cx - nw, top - h * 0.06, cx + nw, top + h * 0.15), angle=-90, n=10, length=(3, 8), width=(0.6, 1.4), line="#3A2010", lw=1.4))
    return "".join(out)


def plantern(u, x, base, s, seed, glow_r=120, glow_op=0.6, frame=SIL, rim="#B8A6DC"):
    """Iron cage lantern with a candle burning inside; base = bottom of its foot. s=1 -> about 40 x 80 px."""
    w, h = 40 * s, 52 * s
    gb = base - 8 * s
    top = gb - h
    out = [pglow(f"{u}-lg", x, top + h * 0.5, glow_r, "#FFC45A", glow_op, seed)]
    glass = hpath([(x - w * 0.4, top), (x + w * 0.4, top), (x + w * 0.34, gb), (x - w * 0.34, gb)], seed, 0.4)
    inner = soft(x, top + h * 0.6, w * 0.6, h * 0.6, "#FFFFFF", f"{u}-lw", 0.85)
    fh = h * 0.42
    fy = gb - h * 0.22
    inner += (f'<path d="{blob(x, gb - h * 0.1, w * 0.12, h * 0.14, seed, 0.05, 10)}" fill="{BONE}"/>'
              f'<path d="M {x:.1f} {fy - fh:.1f} Q {x + w * 0.16:.1f} {fy - fh * 0.4:.1f} {x + w * 0.08:.1f} {fy:.1f} Q {x:.1f} {fy + 3:.1f} {x - w * 0.08:.1f} {fy:.1f} Q {x - w * 0.16:.1f} {fy - fh * 0.4:.1f} {x:.1f} {fy - fh:.1f} Z" fill="#FFF6D6"/>')
    out.append(f'<path d="{glass}" fill="#FFD27A"/>' + inside(f"{u}-gi", glass, inner))
    lw = max(1.8, 3 * s)
    out.append(ink(f"M {x:.1f} {top:.1f} L {x:.1f} {gb:.1f}", frame, lw * 0.8, seed, 1, 0.9))
    out.append(ink(glass, frame, lw * 1.2, seed + 1, 1, 1))
    roof = hpath([(x - w * 0.58, top + 2), (x, top - h * 0.38), (x + w * 0.58, top + 2)], seed + 2, 0.5)
    out.append(f'<path d="{roof}" fill="{frame}"/>' + ink(hpath([(x - w * 0.58, top + 2), (x, top - h * 0.38)], seed + 3, 0.4, False), rim, 1.8, seed, 1, 0.7))
    out.append(f'<circle cx="{x:.1f}" cy="{top - h * 0.46:.1f}" r="{5 * s:.1f}" fill="none" stroke="{frame}" stroke-width="{lw:.1f}"/>')
    foot = hpath([(x - w * 0.46, gb), (x + w * 0.46, gb), (x + w * 0.3, base), (x - w * 0.3, base)], seed + 4, 0.4)
    out.append(f'<path d="{foot}" fill="{frame}"/>')
    return "".join(out)


def owl(u, cx, cy, s, seed, body="#7A5236", tints=("#9A6E4A", "#5A3A24", "#B88A5E", "#6A4630"), belly="#E9D2A6", face="#F3E2C0",
        iris="#FFB531", sleepy=False, head_tilt=0, wing="#5E3E28"):
    """Gouache owl: feathered egg body, heart-shaped face disk, huge amber eyes, folded wings, talons.
    (cx, cy) is the middle of the body; s=1 -> about 140 x 210 px."""
    rnd = random.Random(seed)
    g = [f'<g transform="translate({cx:.1f} {cy:.1f}) scale({s:.3f})">']
    bodyd = smooth_closed([(0, -96), (44, -88), (66, -50), (66, 6), (56, 60), (28, 92), (0, 98), (-28, 92), (-56, 60), (-66, 6), (-66, -50), (-44, -88)])
    tufts = (f'<path d="M -50 -70 C -60 -96 -62 -112 -54 -124 C -44 -108 -30 -96 -20 -88 Z" fill="{body}"/>'
             f'<path d="M 50 -70 C 60 -96 62 -112 54 -124 C 44 -108 30 -96 20 -88 Z" fill="{body}"/>')
    g.append(tufts + ink("M -50 -70 C -60 -96 -62 -112 -54 -124 C -44 -108 -30 -96 -20 -88 M 50 -70 C 60 -96 62 -112 54 -124 C 44 -108 30 -96 20 -88", INKB, 2.2, seed, 1, 0.8))
    g.append(pshape(f"{u}-b", bodyd, body, list(tints), seed, (-70, -100, 70, 100), angle=-90, n=120, length=(10, 26), width=(1.4, 3.4), op=(0.3, 0.6),
                    shade=("#2A1A10", 0.45, 12, 6)))
    # belly with chevron feather marks
    bel = blob(0, 34, 40, 56, seed + 1, 0.05, 16)
    g.append(pshape(f"{u}-bl", bel, belly, ["#FFF4DC", "#D8BC8A", "#C8A876"], seed + 1, (-44, -24, 44, 92), angle=-90, n=40, length=(6, 14), width=(1, 2.2)))
    ch = []
    for row in range(5):
        yy = 2 + row * 15
        for col in range(-2, 3):
            xx = col * 15 + (7 if row % 2 else 0)
            if abs(xx) > 34 - row * 2:
                continue
            ch.append(f"M {xx - 5:.1f} {yy:.1f} Q {xx:.1f} {yy + 5:.1f} {xx + 5:.1f} {yy:.1f}")
    g.append(inside(f"{u}-blc", bel, ink(" ".join(ch), "#8A5A36", 2, seed, 1, 0.75)))
    # folded wings with scalloped feather rows
    for sx in (-1, 1):
        wd = smooth_closed([(sx * 40, -40), (sx * 70, -10), (sx * 72, 40), (sx * 56, 86), (sx * 40, 92), (sx * 34, 40), (sx * 34, -10)])
        g.append(pshape(f"{u}-w{sx + 1}", wd, wing, ["#7A5236", "#3E2818", "#8A6040"], seed + 3 + sx, (sx * 30 - 45, -45, sx * 30 + 45, 95), angle=-80, n=40,
                        length=(10, 24), width=(1, 2.6), line=INKB, lw=2))
        sc = " ".join(f"M {sx * 38:.1f} {yy:.1f} Q {sx * 54:.1f} {yy + 10:.1f} {sx * 68:.1f} {yy - 2:.1f}" for yy in (4, 26, 48, 70))
        g.append(inside(f"{u}-wc{sx + 1}", wd, ink(sc, "#E2C08A", 1.8, seed, 1, 0.55)))
    g.append(ink(bodyd, INKB, 2.6, seed + 5, 2, 0.8))
    # face disk (two overlapping lobes), eyes, beak
    g.append(f'<g transform="rotate({head_tilt} 0 -50)">')
    fd = smooth_closed([(0, -78), (22, -86), (46, -76), (54, -52), (44, -28), (22, -18), (0, -12), (-22, -18), (-44, -28), (-54, -52), (-46, -76), (-22, -86)])
    g.append(pshape(f"{u}-fd", fd, face, ["#FFFFFF", "#E2CCA0", "#F8EED8"], seed + 6, (-58, -90, 58, -10), angle=0, n=40, length=(8, 18), width=(1, 2.2),
                    shade=("#C8A878", 0.5, 0, 6), line="#A07A50", lw=1.6))
    rays = " ".join(f"M {sx * 25 + 23 * math.cos(a) * 1.0:.1f} {-50 + 23 * math.sin(a):.1f} L {sx * 25 + 31 * math.cos(a):.1f} {-50 + 31 * math.sin(a):.1f}"
                    for sx in (-1, 1) for a in [math.radians(t) for t in range(0, 360, 24)])
    g.append(inside(f"{u}-fr", fd, ink(rays, "#C8A070", 1.2, seed, 1, 0.6)))
    for sx in (-1, 1):
        ex = sx * 25
        if sleepy:
            g.append(ink(f"M {ex - 13} -50 Q {ex} -40 {ex + 13} -50", "#2A1A10", 3.4, seed, 1, 1) + ink(f"M {ex - 10} -45 l -3 4 M {ex} -42 l 0 5 M {ex + 10} -45 l 3 4", "#2A1A10", 1.6, seed, 1, 0.8))
            continue
        g.append(f'<path d="{blob(ex, -50, 21, 21, seed + 10 + sx, 0.03, 14)}" fill="#3A2414"/>')
        g.append(defs(rg(f"{u}-ir{sx + 1}", [(0, "#FFE9A0"), (0.55, iris), (1, "#C8701A")], cy=0.6, r=0.6)))
        g.append(f'<circle cx="{ex}" cy="-50" r="17" fill="url(#{u}-ir{sx + 1})"/>')
        g.append(f'<circle cx="{ex + sx * 1.5:.1f}" cy="-49" r="9.5" fill="#120A08"/><circle cx="{ex - 4:.1f}" cy="-55" r="4.2" fill="#FFFFFF"/><circle cx="{ex + 5:.1f}" cy="-44" r="1.8" fill="#FFFFFF" opacity="0.8"/>')
        g.append(ink(f"M {ex - 19} -58 Q {ex} -74 {ex + 19} -58", "#5A3A24", 2.6, seed + sx, 1, 0.8))
    beak = "M -7 -36 Q 0 -40 7 -36 Q 3 -24 0 -18 Q -3 -24 -7 -36 Z"
    g.append(f'<path d="{beak}" fill="#E8A040"/>' + ink(beak, "#6A3A10", 1.6, seed, 1, 0.9) + '<path d="M -3 -34 q 1 6 3 10" stroke="#FFE2A0" stroke-width="1.6" fill="none" opacity="0.8"/>')
    g.append('<ellipse cx="-40" cy="-34" rx="7" ry="4" fill="#F29AB4" opacity="0.45"/><ellipse cx="40" cy="-34" rx="7" ry="4" fill="#F29AB4" opacity="0.45"/>')
    g.append("</g>")
    # feet gripping the branch: three plump toes with dark curved claws
    for sx in (-1, 1):
        for k in (-8, 0, 8):
            tx = sx * 22 + k
            g.append(f'<path d="{blob(tx, 98, 4.6, 7, seed + k + sx, 0.08, 10)}" fill="#E8A040"/>' + ink(f"M {tx - 3:.1f} 104 q 3 6 6 2", "#2A1A10", 2.2, seed + k, 1, 1))
    g.append("</g>")
    return "".join(g)


def branch(u, pts, w0, w1, seed, col="#3A2618", tints=("#5A3A24", "#24160C", "#6E4A30"), rim=None):
    """Painted tapered branch along a polyline with bark strokes and an optional moonlit top edge."""
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        x2, y2 = pts[min(i + 1, n - 1)]
        x1, y1 = pts[max(i - 1, 0)]
        L = math.hypot(x2 - x1, y2 - y1) or 1
        nx, ny = -(y2 - y1) / L, (x2 - x1) / L
        ww = (w0 + (w1 - w0) * i / (n - 1)) / 2
        left.append((x + nx * ww, y + ny * ww))
        right.append((x - nx * ww, y - ny * ww))
    d = smooth_closed(left + right[::-1])
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    box = (min(xs) - w0, min(ys) - w0, max(xs) + w0, max(ys) + w0)
    ang = math.degrees(math.atan2(pts[-1][1] - pts[0][1], pts[-1][0] - pts[0][0]))
    out = pshape(u, d, col, list(tints), seed, box, angle=ang, n=int((box[2] - box[0]) / 2.2), length=(14, 40), width=(1, 3), op=(0.35, 0.7), curve=0.1, line="#120A06", lw=2.2)
    if rim:
        out += ink(smooth_open(right), rim, 2.4, seed, 1, 0.65)
    return out


def pleaf(cx, cy, s, rot, fill, dark, seed):
    """Small painted autumn leaf (elm-ish oval with a vein)."""
    d = blob(cx, cy, s, s * 0.5, seed, 0.1, 12, rot)
    a = math.radians(rot)
    return (f'<path d="{d}" fill="{fill}"/><path d="{d}" fill="none" stroke="{dark}" stroke-width="1.4" opacity="0.7"/>'
            f'<path d="M {cx - s * math.cos(a) * 1.25:.1f} {cy - s * math.sin(a) * 1.25:.1f} L {cx + s * math.cos(a) * 0.9:.1f} {cy + s * math.sin(a) * 0.9:.1f}" stroke="{dark}" stroke-width="1.3" opacity="0.8"/>')


def night_stalk(x, base, h, seed, lean=0, col="#2A1C24", leafc=("#3A2830", "#30202A", "#45323A"), rim=None):
    rnd = random.Random(seed)
    top = (x + lean * h, base - h)
    out = [ink(smooth_open([(x, base), (x + lean * h * 0.4, base - h * 0.5), top]), col, 5, seed, 1, 1)]
    for i in range(8):
        t = 0.16 + i * 0.1
        px, py = x + lean * h * t, base - h * t
        side = 1 if i % 2 else -1
        L = h * rnd.uniform(0.24, 0.36)
        tip = (px + side * L, py + L * rnd.uniform(0.15, 0.6))
        mid = (px + side * L * 0.5, py - L * 0.28)
        d = f"M {px:.1f} {py:.1f} Q {mid[0]:.1f} {mid[1] - 5:.1f} {tip[0]:.1f} {tip[1]:.1f} Q {mid[0]:.1f} {mid[1] + 6:.1f} {px:.1f} {py + 7:.1f} Z"
        out.append(f'<path d="{d}" fill="{rnd.choice(leafc)}"/>')
        if rim:
            out.append(f'<path d="M {px:.1f} {py:.1f} Q {mid[0]:.1f} {mid[1] - 5:.1f} {tip[0]:.1f} {tip[1]:.1f}" stroke="{rim}" stroke-width="1.3" fill="none" opacity="0.55"/>')
    out.append(f'<path d="M {top[0]:.1f} {top[1]:.1f} l -7 -16 M {top[0]:.1f} {top[1]:.1f} l 2 -18 M {top[0]:.1f} {top[1]:.1f} l 9 -13" stroke="{col}" stroke-width="2.4" stroke-linecap="round"/>')
    return "".join(out)


def fireflies(seed, n, box, cols=(SLIME, "#E6FFB0", GOLD, CANDLE), avoid=()):
    rnd = random.Random(seed)
    out = []
    k = 0
    while k < n:
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        if any(math.hypot(x - ax, y - ay) < ar for ax, ay, ar in avoid):
            continue
        k += 1
        c = rnd.choice(cols)
        r = rnd.uniform(1.8, 3.4)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 4:.1f}" fill="{c}" opacity="0.1"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 2:.1f}" fill="{c}" opacity="0.22"/>'
                   f'<path d="{blob(x, y, r, r * 0.8, rnd.randrange(999), 0.15, 7)}" fill="{c}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.4:.1f}" fill="#FFFFFF"/>')
    return "".join(out)


# ================================================================ designs (part 2)
def d_witches_brew():
    u = "gabrew"
    o = [stones(u + "wl", (0, 0, 600, 520), 301, cols=("#3A3250", "#332B48", "#41385A", "#2E2742"), mortar="#120E1C", rim="#8A7AB0", rows=(30, 40), widths=(54, 96), rim_op=0.35)]
    o.append(f'<rect width="600" height="520" fill="{NIGHT0}" opacity="0.25"/>')
    o.append(soft(300, 330, 330, 250, SLIME, u + "-wg", 0.3))
    o.append(soft(300, 520, 260, 120, "#FF8A2A", u + "-wo", 0.35))
    o.append(defs(lg(u + "-tv", [(0, INKN, 0.85), (0.32, INKN, 0.35), (0.5, INKN, 0)])) + f'<rect width="600" height="600" fill="url(#{u}-tv)"/>')
    # flagstone floor lit by the fire
    o.append(stones(u + "fl", (0, 516, 600, 600), 302, cols=("#3A2C34", "#33262E", "#42323A"), mortar="#120A10", rim="#E89A5A", rows=(30, 40), widths=(70, 130), rim_op=0.4))
    o.append(soft(300, 540, 280, 70, "#FF9A3A", u + "-fg", 0.4))
    # fire and logs under the pot
    o.append(flames(u + "fi", 300, 534, 104, 118, 303))
    for k, (rot, dy) in enumerate(((-9, 0), (9, 2))):
        ld = blob(300, 540 + dy, 92, 11, 304 + k, 0.03, 18, rot)
        o.append(pshape(f"{u}-lg{k}", ld, "#4A2E1E", ["#6A4430", "#2E1A10", "#8A5A3A"], 304 + k, (200, 520, 400, 560), angle=rot, n=50, length=(16, 40), width=(1, 2.4),
                        line="#1A0E08", lw=1.8))
        for sx in (-1, 1):
            ex = 300 + sx * 88 * math.cos(math.radians(rot))
            ey = 540 + dy + sx * 88 * math.sin(math.radians(rot))
            o.append(f'<path d="{blob(ex, ey, 7, 11, 304 + k + sx, 0.06, 10)}" fill="#D8A86A"/><ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="3.4" ry="6" fill="none" stroke="#8A5A2A" stroke-width="1.4"/>'
                     + ink(blob(ex, ey, 7, 11, 304 + k + sx, 0.06, 10), "#1A0E08", 1.6, k, 1, 0.8))
    o.append(soft(300, 534, 60, 14, "#FFE27A", u + "-emb", 0.7))
    o.append(cauldron(u + "cd", 300, 330, 236, 168, 305))
    # wooden spoon resting in the brew
    o.append(ink("M 352 326 L 452 214", "#5A3A22", 12, 306, 1, 1) + ink("M 350 322 L 448 212", "#B07A48", 4, 307, 1, 0.8))
    o.append(f'<path d="{blob(458, 206, 13, 20, 308, 0.05, 12, 42)}" fill="#8A5A34"/>' + ink(blob(458, 206, 13, 20, 308, 0.05, 12, 42), "#2A160A", 2, 308, 1, 0.9))
    o.append(f'<ellipse cx="352" cy="328" rx="14" ry="4" fill="none" stroke="#E6FFB0" stroke-width="2" opacity="0.8"/>')
    o.append(vapor(u + "vp", 290, 314, 210, 150, 309))
    o.append(stars(310, 0, (200, 190, 400, 300), col="#E6FFB0", tw=4, twr=(5, 8)))
    # a toadstool cluster and a potion on the floor
    o.append(toadstool(u + "ts1", 104, 536, 60, 311) + toadstool(u + "ts2", 138, 540, 38, 312, lean=4))
    o.append(flask(u + "fk", 498, 540, 52, 84, 313))
    o.append(ptext(u + "t1", 300, 116, "witches’", SERIF_IT, 80, BONE, ["#FFFFFF", "#E6D8C0", "#D6E8C0"], 314, max_w=360, angle=-58, shadow=INKN, hi="#FFFFFF"))
    o.append(ptext(u + "t2", 300, 222, "BREW", BEBAS, 128, "#B8E86A", ["#E6FFB0", SLIME, "#7AB83A", "#D6FF9A"], 315, max_w=400, ls=24, shadow="#0A1404",
                   glow=SLIME, glow_op=0.35, hi="#FFFFFF"))
    o.append(finish(u, 11, vign=0.45))
    return "".join(o)


def d_enter_if_you_dare():
    u = "gaent"
    o = [sky(u, [(0, NIGHT0), (0.45, "#261E52"), (0.8, "#3E2F6E"), (1, "#4A3A78")], 321, swirl=(300, 300, 84, 160, "#CDBCEB"))]
    o.append(stars(322, 40, (20, 20, 580, 380), avoid=[(300, 300, 120)]))
    o.append(moon(u, 300, 300, 80, 323, halo_r=1.9))
    o.append(cloud(u + "c1", 190, 350, 200, 12, 324, "#4A3A7A", "#C8B6E8", 0.6))
    # the cemetery beyond the gate
    h1, l1 = hill(u + "h1", [(-20, 420), (150, 404), (300, 410), (460, 400), (620, 414)], 325, 600, "#2A2052", ["#3A2E66", "#2E2458", "#463A72"], rim="#B8A6DC", amp=4)
    o.append(h1)
    o.append(tree(196, y_on(l1, 196) + 4, 156, 326, SIL, rim="#B8A6DC", lean=-6, spread=30, depth=6))
    o.append(tree(412, y_on(l1, 412) + 4, 120, 327, SIL, rim="#B8A6DC", lean=8, spread=28, depth=5))
    # little crypt at the end of the path
    cr = hpath([(270, 410), (270, 372), (300, 352), (330, 372), (330, 410)], 328, 0.6)
    o.append(f'<path d="{cr}" fill="{SIL2}"/>' + ink(hpath([(270, 372), (300, 352), (330, 372)], 329, 0.4, False), "#B8A6DC", 1.8, 329, 1, 0.7))
    o.append(window(u + "cw", 292, 384, 16, 26, 330, lit=("#FFCF6A", "#F59A3A"), arch=True, glow_op=0.35))
    rnd = random.Random(331)
    for i, x in enumerate((168, 236, 368, 440, 228, 392)):
        y = y_on(l1, x) + 6 + (i > 3) * 14
        w_, h_ = rnd.uniform(14, 22), rnd.uniform(20, 30)
        d = hpath([(x - w_ / 2, y), (x - w_ / 2, y - h_ * 0.7)] + [(x - w_ / 2 * math.cos(math.pi * k / 6), y - h_ * 0.7 - w_ / 2 * math.sin(math.pi * k / 6)) for k in range(1, 6)] + [(x + w_ / 2, y - h_ * 0.7), (x + w_ / 2, y)], 332 + i, 0.5)
        o.append(f'<path d="{d}" fill="#4A4266"/>' + inside(f"{u}-tb{i}", d, f'<path d="{d}" fill="#1E1834" transform="translate(4 0)" opacity="0.7"/>') + ink(d, INKN, 1.6, i, 1, 0.8))
    # path running from the crypt to the viewer
    pth = "M 290 412 C 286 430 266 450 240 476 L 196 600 L 404 600 L 360 476 C 334 450 314 430 310 412 Z"
    o.append(pshape(u + "pt", pth, "#4E4478", ["#5E5488", "#3E3666", "#6E64A0"], 333, (190, 408, 410, 600), angle=0, n=160, length=(10, 30), width=(1.5, 4)))
    o.append(cloud(u + "mist", 300, 470, 560, 16, 334, "#8A7AB8", "#C8B6E8", 0.55))
    # foreground ground either side of the path
    fg = hpath([(-10, 486), (180, 480), (180, 600), (-10, 600)], 335, 1)
    fg2 = hpath([(420, 480), (610, 486), (610, 600), (420, 600)], 336, 1)
    for k, d in enumerate((fg, fg2)):
        o.append(pshape(f"{u}-fg{k}", d, "#1A1430", ["#241C40", "#120E22", "#2E2450"], 337 + k, (-10, 476, 610, 600), angle=-4, n=90, length=(20, 60), width=(2, 5)))
    # ---- the gate
    lb = []
    for x in range(150, 300, 18):
        lb.append(f"M {x} 476 L {x} 296")
    rb = []
    for i in range(6):
        t = i / 5
        x = 304 + 108 * t
        lb.append(f"M {x:.1f} {476 - 12 * t:.1f} L {x:.1f} {300 + 12 * t:.1f}")
    bars = " ".join(lb)
    rails = "M 140 318 L 300 318 M 140 458 L 300 458 M 304 320 L 412 330 M 304 456 L 412 446 M 140 300 L 300 300 M 304 302 L 412 312"
    o.append(ink(bars, SIL, 5.2, 338, 1, 1) + ink(rails, SIL, 6, 339, 1, 1))
    o.append(ink(" ".join(f"M {x - 1.5} 474 L {x - 1.5} 300" for x in range(150, 300, 18)), "#8A7AB8", 1.4, 340, 1, 0.55))
    tips = "".join(f'<path d="M {x - 5} 300 L {x} 284 L {x + 5} 300 Z" fill="{SIL}"/>' for x in range(150, 300, 18))
    tips += "".join(f'<path d="M {304 + 108 * i / 5 - 4.5:.1f} {302 + 12 * i / 5:.1f} L {304 + 108 * i / 5:.1f} {288 + 12 * i / 5:.1f} L {304 + 108 * i / 5 + 4.5:.1f} {302 + 12 * i / 5:.1f} Z" fill="{SIL}"/>' for i in range(6))
    o.append(tips)
    # scrolls on the middle band
    sc = []
    for x0 in (168, 222, 276):
        sc.append(f"M {x0 - 16} 400 C {x0 - 16} 380 {x0 + 8} 380 {x0 + 8} 394 C {x0 + 8} 402 {x0 - 4} 402 {x0 - 4} 396")
        sc.append(f"M {x0 + 16} 380 C {x0 + 16} 400 {x0 - 8} 400 {x0 - 8} 386 C {x0 - 8} 378 {x0 + 4} 378 {x0 + 4} 384")
    for x0 in (330, 384):
        sc.append(f"M {x0 - 12} 400 C {x0 - 12} 382 {x0 + 6} 382 {x0 + 6} 394 C {x0 + 6} 400 {x0 - 3} 400 {x0 - 3} 395")
    o.append(ink(" ".join(sc), SIL, 3.4, 341, 1, 1))
    o.append(ink("M 140 372 L 300 372 M 140 408 L 300 408 M 304 374 L 412 378 M 304 406 L 412 406", SIL, 3, 342, 1, 1))
    # the fixed arch with ironwork and ENTER over it
    R0, R1, cy = 170, 132, 318
    outer = f"M {300 - 162} {cy - math.sqrt(R0 ** 2 - 162 ** 2):.1f} A {R0} {R0} 0 0 1 {300 + 162} {cy - math.sqrt(R0 ** 2 - 162 ** 2):.1f}"
    inner = f"M {300 - math.sqrt(R1 ** 2 - 18 ** 2):.1f} 300 A {R1} {R1} 0 0 1 {300 + math.sqrt(R1 ** 2 - 18 ** 2):.1f} 300"
    o.append(ink(outer, SIL, 7, 343, 1, 1) + ink(inner, SIL, 5, 344, 1, 1))
    rad = []
    for a in range(-64, 66, 16):
        ar = math.radians(a)
        rad.append(f"M {300 + R1 * math.sin(ar):.1f} {cy - R1 * math.cos(ar):.1f} L {300 + R0 * math.sin(ar):.1f} {cy - R0 * math.cos(ar):.1f}")
    o.append(ink(" ".join(rad), SIL, 3.4, 345, 1, 1))
    o.append(ink(outer, "#B8A6DC", 2, 346, 1, 0.55))
    curls = "".join(f'<circle cx="{300 + (R0 + R1) / 2 * math.sin(math.radians(a)):.1f}" cy="{cy - (R0 + R1) / 2 * math.cos(math.radians(a)):.1f}" r="6" fill="none" stroke="{SIL}" stroke-width="3"/>' for a in range(-56, 60, 16))
    o.append(curls)
    # stone pillars with lanterns
    for k, (x0, x1) in enumerate(((62, 140), (460, 538))):
        pd = hpath([(x0, 268), (x1, 268), (x1, 610), (x0, 610)], 350 + k, 0.8)
        o.append(inside(f"{u}-pl{k}", pd, stones(f"{u}-ps{k}", (x0 - 4, 266, x1 + 4, 610), 351 + k, cols=("#5A5276", "#4E4668", "#625A80", "#544C70"), mortar="#1A1428", rim="#C8B6E8",
                                                  rows=(26, 32), widths=(30, 46), rim_op=0.55)
                                       + f'<rect x="{x0 if k else x1 - 22}" y="266" width="22" height="344" fill="#0E0A18" opacity="0.4"/>'))
        o.append(ink(pd, INKN, 2.4, 352 + k, 1, 0.9))
        cap = hpath([(x0 - 10, 252), (x1 + 10, 252), (x1 + 6, 272), (x0 - 6, 272)], 353 + k, 0.6)
        o.append(pshape(f"{u}-cp{k}", cap, "#7A7098", ["#9A90B8", "#5A5276", "#ACA2C8"], 354 + k, (x0 - 12, 248, x1 + 12, 274), angle=0, n=30, length=(10, 30), width=(1, 2.6),
                        line=INKN, lw=2))
        o.append(plantern(f"{u}-ln{k}", (x0 + x1) / 2, 252, 1.05, 355 + k, glow_r=120))
    o.append(pbat(250, 232, 16, -12) + pbat(350, 222, 12, 10) + pbat(520, 104, 20, 8, -4) + pbat(84, 120, 17, -10))
    o.append(soft(300, 620, 360, 110, "#05030C", u + "fb", 0.55))
    arc, _ = arc_text(u + "ar", "ENTER", 300, cy, R0 + 12, CINZEL, 60, BONE, ["#FFFFFF", "#E6D8C0", "#D2C4EA"], 357, ls=12, top=True, shadow=INKN, hi="#FFFFFF", max_deg=82)
    o.append(arc)
    o.append(ptext(u + "t2", 300, 522, "if you dare", SERIF_IT, 74, GOLD, ["#FFE38A", "#F59A3A", "#FFF3C0", "#E8A030"], 358, max_w=330, angle=-58, shadow=INKN,
                   glow="#05030C", glow_op=0.55, hi="#FFFFFF"))
    o.append(finish(u, 12, vign=0.45))
    return "".join(o)


def d_whooos_there():
    u = "gaowl"
    o = [sky(u, [(0, NIGHT0), (0.5, "#2A2258"), (0.85, "#3A2E6A"), (1, "#2A2050")], 401, swirl=(300, 212, 150, 250, "#D8C8F0"), n=460)]
    o.append(stars(402, 46, (20, 20, 580, 420), avoid=[(300, 212, 190)]))
    o.append(moon(u, 300, 212, 152, 403, halo_r=1.55))
    o.append(cloud(u + "c1", 120, 300, 200, 13, 404, "#4A3A7A", "#C8B6E8", 0.65))
    o.append(cloud(u + "c2", 500, 150, 170, 11, 405, "#4A3A7A", "#D8C8F0", 0.5))
    # gnarled branch across the moon
    o.append(branch(u + "br", [(-20, 384), (100, 372), (220, 360), (330, 352), (440, 340), (540, 322), (620, 300)], 34, 12, 406, rim="#D8C8F0"))
    o.append(branch(u + "tw1", [(470, 336), (510, 300), (530, 262)], 9, 3, 407, rim="#D8C8F0"))
    o.append(branch(u + "tw2", [(120, 372), (90, 340), (78, 312)], 9, 3, 408, rim="#D8C8F0"))
    for i, (x, y, s, rot, c) in enumerate(((534, 250, 17, -70, "#D9622A"), (506, 288, 16, 200, "#E8A23A"), (544, 290, 15, 30, "#B8442A"), (76, 300, 16, -110, "#C9862E"),
                                           (104, 330, 15, 170, "#D9622A"), (62, 334, 14, 120, "#E8A23A"), (580, 312, 15, 60, "#C9862E"))):
        o.append(pleaf(x, y, s, rot, c, "#5A1E10", 410 + i))
    o.append(pleaf(72, 430, 13, 30, "#E8A23A", "#5A1E10", 420) + pleaf(532, 404, 12, -40, "#D9622A", "#5A1E10", 421))
    o.append(owl(u + "o1", 262, 248, 1.0, 411))
    o.append(owl(u + "o2", 404, 296, 0.5, 412, sleepy=True, head_tilt=8, body="#8A6244"))
    o.append(pbat(90, 126, 20, -12) + pbat(510, 84, 15, 8))
    o.append(soft(300, 600, 380, 150, "#05030C", u + "fb", 0.65))
    o.append(ptext(u + "t1", 300, 474, "whooo’s", SERIF_IT, 84, BONE, ["#FFFFFF", "#E6D8C0", "#D2C4EA"], 413, max_w=360, angle=-58, shadow=INKN, hi="#FFFFFF"))
    o.append(ptext(u + "t2", 300, 536, "THERE?", BEBAS, 70, GOLD, ["#FFE38A", "#F59A3A", "#FFF3C0"], 414, max_w=300, ls=18, shadow=INKN, glow="#FF9A2E", glow_op=0.25))
    o.append(finish(u, 13, vign=0.45))
    return "".join(o)


def d_glow_getter():
    u = "gaglow"
    o = [sky(u, [(0, "#120C24"), (0.55, "#24183E"), (0.85, "#3E2440"), (1, "#5A2E36")], 501, n=380)]
    o.append(stars(502, 34, (20, 20, 580, 300), tw=4, avoid=[(300, 170, 150)]))
    o.append(soft(300, 420, 360, 200, "#FF8A2A", u + "-hz", 0.35))
    # corn stalks either side
    for i, (x, h, ln) in enumerate(((40, 330, 0.06), (92, 270, -0.04), (14, 220, 0.1), (560, 320, -0.06), (510, 260, 0.05), (590, 230, -0.1))):
        o.append(night_stalk(x, 520, h, 503 + i, lean=ln, rim="#E89A5A"))
    # field and the hay bale stage
    fld, fl = hill(u + "fd", [(-20, 486), (200, 478), (400, 484), (620, 476)], 510, 600, "#2A1A22", ["#3A2430", "#20141A", "#4A2E34"], rim="#C87A4A", amp=3)
    o.append(fld)
    o.append(hay_bale(u + "hb", 148, 404, 304, 92, 511))
    hb = smooth_closed([(148, 408), (300, 402), (452, 408), (455, 450), (452, 496), (300, 498), (148, 496), (145, 450)])
    rnd = random.Random(520)
    straw = "".join(_lens(rnd.uniform(140, 450), rnd.uniform(404, 500), rnd.uniform(12, 30), rnd.uniform(0.7, 1.6), math.radians(rnd.uniform(-12, 12)), 1.5,
                          rnd.choice(["#FFE08A", "#C98A3A", "#8A5A22", "#F2C060", "#6A4018"]), rnd.uniform(0.45, 0.9)) for _ in range(420))
    o.append(inside(u + "-hbs", hb, f'<rect x="140" y="400" width="320" height="110" fill="#5A3414" opacity="0.2"/>' + straw
                    + defs(lg(u + "-hbd", [(0, "#1A0A06", 0), (1, "#1A0A06", 0.55)])) + f'<rect x="140" y="430" width="320" height="80" fill="url(#{u}-hbd)"/>'
                    + soft(148, 450, 60, 70, "#120808", u + "-hbl", 0.45) + soft(452, 450, 60, 70, "#120808", u + "-hbr", 0.45)
                    + soft(300, 406, 200, 30, "#FFD27A", u + "-hbg", 0.5)))
    o.append(ink("M 222 404 q 3 46 0 94 M 378 404 q 3 46 0 94", "#5A3414", 3, 521, 1, 0.8))
    o.append(f'<g stroke="#E8B860" stroke-width="1.6" stroke-linecap="round" opacity="0.9">' + "".join(
        f'<path d="M {x:.1f} {404 + rnd.uniform(-2, 3):.1f} l {rnd.uniform(-9, 9):.1f} {rnd.uniform(-9, -2):.1f}"/>' for x in [rnd.uniform(150, 450) for _ in range(34)]) + "</g>")
    o.append(jack(u + "j1", 196, 372, 118, 84, 512, "sly", glow_r=140, glow_op=0.5))
    o.append(jack(u + "j3", 410, 376, 104, 76, 513, "cute", glow_r=130, glow_op=0.5))
    o.append(jack(u + "j2", 302, 330, 196, 140, 514, "toothy", glow_r=230, glow_op=0.6, night=False))
    o.append(jack(u + "g1", 104, 520, 62, 44, 515, None, lit=False, body="#F1E6D2", dark="#B9A68A", light="#FFFFFF"))
    o.append(jack(u + "g2", 500, 524, 56, 40, 516, "classic", glow_r=70))
    o.append(fireflies(517, 22, (60, 230, 540, 480), avoid=[(302, 330, 110), (196, 372, 60), (410, 376, 56)]))
    o.append(soft(300, 620, 360, 110, "#05030C", u + "fb", 0.55))
    o.append(ptext(u + "t1", 300, 166, "GLOW", BEBAS, 140, GOLD, ["#FFE38A", "#F59A3A", "#FFF3C0", "#FFB547"], 518, max_w=360, ls=22, shadow="#2A1004",
                   glow="#FF8A2A", glow_op=0.45, hi="#FFFFFF"))
    o.append(ptext(u + "t2", 300, 236, "getter", SERIF_IT, 76, BONE, ["#FFFFFF", "#E6D8C0", "#FFE8C8"], 519, max_w=280, angle=-58, shadow=INKN, hi="#FFFFFF"))
    o.append(finish(u, 14, vign=0.45))
    return "".join(o)


# ---------------------------------------------------------------- set A, part 3 pieces
def scarecrow(u, cx, top, seed, rim="#FFC890"):
    """Gouache scarecrow on a post, backlit at dusk: straw hat, stitched burlap face with button eyes,
    plaid shirt with straw bursting from the cuffs, patched overalls, dangling legs."""
    rnd = random.Random(seed)
    out = []
    # post
    post = hpath([(cx - 8, top + 60), (cx + 8, top + 60), (cx + 9, top + 340), (cx - 9, top + 340)], seed, 0.6)
    out.append(pshape(f"{u}-po", post, "#5A3A24", ["#7A5236", "#3A2416", "#8A6040"], seed, (cx - 10, top + 60, cx + 10, top + 340), angle=-90, n=30, length=(20, 50), width=(1, 2.4), line="#1A0E08", lw=1.8))

    def straw(x, y, ang, n=12, L=(14, 26), spread=40):
        return "".join(f'<path d="M {x:.1f} {y:.1f} l {math.cos(math.radians(ang + d)) * l:.1f} {math.sin(math.radians(ang + d)) * l:.1f}" stroke="{rnd.choice(["#E8C060", "#F6DA8A", "#C9933A", "#FFE9A8"])}" '
                       f'stroke-width="{rnd.uniform(1.6, 2.8):.1f}" stroke-linecap="round"/>'
                       for d, l in [(rnd.uniform(-spread, spread), rnd.uniform(*L)) for _ in range(n)])
    # legs (overalls) with straw at the ankles
    for k, lx in enumerate((cx - 22, cx + 22)):
        leg = hpath([(lx - 17, top + 192), (lx + 17, top + 192), (lx + 16 + k * 2, top + 272), (lx - 16 + k * 2, top + 272)], seed + 10 + k, 0.8)
        out.append(straw(lx + k * 2, top + 272, 90 + (k * 2 - 1) * 10, 12, (10, 22), 34))
        out.append(pshape(f"{u}-lg{k}", leg, "#3E5A7A", ["#4E6E92", "#2E445E", "#5A7AA0"], seed + 10 + k, (lx - 20, top + 188, lx + 20, top + 276), angle=-90, n=30,
                          length=(10, 24), width=(1.2, 2.6), line="#14202E", lw=1.8, shade=("#1E2E44", 0.5, 6 * (k * 2 - 1), 0)))
    pt = hpath([(cx - 34, top + 232), (cx - 14, top + 230), (cx - 13, top + 250), (cx - 33, top + 252)], seed + 12, 0.6)
    out.append(f'<path d="{pt}" fill="#D9822E"/>' + ink(pt, "#5A2A10", 1.4, seed, 1, 0.9) + ink(f"M {cx - 31} {top + 236} l 15 0 M {cx - 31} {top + 247} l 15 -1", "#FFE2B0", 1, seed, 1, 0.8))
    # shirt with arms out wide, straw at the cuffs
    sh = smooth_closed([(cx - 134, top + 112), (cx - 92, top + 104), (cx - 48, top + 96), (cx, top + 93), (cx + 48, top + 96), (cx + 92, top + 102), (cx + 134, top + 108),
                        (cx + 138, top + 128), (cx + 136, top + 146), (cx + 92, top + 140), (cx + 52, top + 142), (cx + 48, top + 174), (cx + 52, top + 204), (cx, top + 208),
                        (cx - 52, top + 204), (cx - 48, top + 174), (cx - 52, top + 144), (cx - 92, top + 144), (cx - 136, top + 150), (cx - 139, top + 132)])
    out.append(straw(cx - 138, top + 130, 180, 20, (16, 32), 42) + straw(cx + 138, top + 126, 0, 20, (16, 32), 42))
    plaid = []
    for x in range(int(cx - 150), int(cx + 150), 22):
        plaid.append(f'<rect x="{x}" y="{top + 90}" width="7" height="120" fill="#6A1E18" opacity="0.5"/><rect x="{x + 11}" y="{top + 90}" width="2" height="120" fill="#F2C060" opacity="0.55"/>')
    for y in range(int(top + 96), int(top + 210), 22):
        plaid.append(f'<rect x="{cx - 150}" y="{y}" width="300" height="7" fill="#6A1E18" opacity="0.45"/><rect x="{cx - 150}" y="{y + 11}" width="300" height="2" fill="#F2C060" opacity="0.5"/>')
    out.append(f'<path d="{sh}" fill="#B23E2A"/>' + inside(f"{u}-pl", sh, "".join(plaid) + tex(f"{u}-sht", sh, ["#D2583A", "#8A2A1C", "#E07050"], seed + 3, (cx - 140, top + 92, cx + 140, top + 206),
                                                                                       n=160, angle=0, length=(12, 30), width=(1.2, 3))
                                                    + f'<path d="{sh}" fill="none" stroke="#3A0E0A" stroke-width="12" opacity="0.35" transform="translate(4 6)"/>'))
    out.append(ink(sh, "#3A140C", 2.4, seed + 4, 2, 0.85))
    out.append(ink(f"M {cx - 120} {top + 116} q 8 10 4 24 M {cx - 86} {top + 110} q 6 14 2 30 M {cx + 84} {top + 106} q 6 14 2 30 M {cx + 118} {top + 112} q 8 10 4 26 "
                   f"M {cx - 40} {top + 160} q 14 6 30 2 M {cx + 12} {top + 186} q 14 4 30 -4", "#5A1A10", 1.8, seed + 8, 1, 0.6))
    # overall bib + straps + buttons
    bib = hpath([(cx - 34, top + 144), (cx + 34, top + 144), (cx + 40, top + 206), (cx - 40, top + 206)], seed + 5, 0.8)
    out.append(pshape(f"{u}-bib", bib, "#3E5A7A", ["#4E6E92", "#2E445E", "#5A7AA0"], seed + 5, (cx - 42, top + 140, cx + 42, top + 210), angle=-90, n=30, length=(10, 22), width=(1.2, 2.6),
                      line="#14202E", lw=1.8))
    out.append(ink(f"M {cx - 28} {top + 146} L {cx - 22} {top + 98} M {cx + 28} {top + 146} L {cx + 22} {top + 98}", "#3E5A7A", 7, seed, 1, 1))
    out.append(f'<circle cx="{cx - 27}" cy="{top + 150}" r="4.4" fill="{GOLD}"/><circle cx="{cx + 27}" cy="{top + 150}" r="4.4" fill="{GOLD}"/>')
    out.append(straw(cx, top + 96, -90, 14, (8, 16), 70))
    # burlap head
    hd = blob(cx, top + 62, 38, 40, seed + 6, 0.05, 16)
    out.append(pshape(f"{u}-hd", hd, "#D8B07A", ["#E8C48E", "#B88A56", "#F2D6A6", "#A87A48"], seed + 6, (cx - 42, top + 20, cx + 42, top + 104), angle=-80, n=60,
                      length=(6, 16), width=(1, 2.2), line="#5A3A1E", lw=2, shade=("#8A5A30", 0.45, 8, 4)))
    weave = " ".join(f"M {cx - 40} {top + 30 + k * 7} L {cx + 40} {top + 30 + k * 7}" for k in range(11)) + " " + " ".join(f"M {cx - 40 + k * 7} {top + 20} L {cx - 40 + k * 7} {top + 104}" for k in range(12))
    out.append(inside(f"{u}-wv", hd, f'<path d="{weave}" stroke="#A87A48" stroke-width="0.9" opacity="0.45"/>'))
    for ex in (cx - 14, cx + 14):
        out.append(f'<circle cx="{ex}" cy="{top + 56}" r="7.4" fill="#2A1A10"/><circle cx="{ex - 2.4}" cy="{top + 53.6}" r="2.2" fill="#FFF"/>'
                   f'<path d="M {ex - 3} {top + 56} l 6 0 M {ex} {top + 53} l 0 6" stroke="#5A3A24" stroke-width="1"/>')
    out.append(f'<ellipse cx="{cx - 24}" cy="{top + 70}" rx="7" ry="4.4" fill="#E2788A" opacity="0.55"/><ellipse cx="{cx + 24}" cy="{top + 70}" rx="7" ry="4.4" fill="#E2788A" opacity="0.55"/>')
    out.append(ink(f"M {cx - 18} {top + 76} Q {cx} {top + 90} {cx + 18} {top + 76}", "#3A2414", 2.4, seed, 1, 1)
               + ink(" ".join(f"M {cx + t:.1f} {top + 78 + 6 - abs(t) * 0.25:.1f} l 0 -9" for t in (-12, -4, 4, 12)), "#3A2414", 1.6, seed, 1, 0.9))
    out.append(ink(f"M {cx - 22} {top + 100} Q {cx} {top + 106} {cx + 22} {top + 100}", "#8A5A2A", 3, seed, 1, 0.9))
    # straw hat with a band and a tucked leaf
    br = blob(cx, top + 28, 74, 13, seed + 7, 0.04, 18, -4)
    cr = smooth_closed([(cx - 38, top + 26), (cx - 34, top), (cx - 16, top - 22), (cx + 14, top - 24), (cx + 34, top - 6), (cx + 38, top + 24)])
    for k, d in enumerate((br, cr)):
        out.append(pshape(f"{u}-ht{k}", d, "#D9A84A", ["#F2C866", "#B8862E", "#FFE08A", "#A87422"], seed + 7 + k, (cx - 80, top - 30, cx + 80, top + 44), angle=-6 if k == 0 else -20,
                          n=60, length=(10, 24), width=(1, 2.2), line="#6A4210", lw=1.8, shade=("#8A5A1A", 0.4, 6, 4)))
    band = hpath([(cx - 37, top + 8), (cx + 37, top + 6), (cx + 38, top + 20), (cx - 38, top + 22)], seed + 9, 0.6)
    out.append(inside(f"{u}-bd", cr, f'<path d="{band}" fill="#7A1E1A"/>'))
    out.append(pleaf(cx + 26, top + 6, 12, -50, "#E8792E", "#7A2E10", seed + 3))
    # dusk rim light down the right-hand edges (moon behind)
    out.append(ink(f"M {cx + 32} {top - 8} Q {cx + 40} {top + 10} {cx + 38} {top + 24} M {cx + 36} {top + 46} Q {cx + 40} {top + 66} {cx + 30} {top + 90}", rim, 2, seed, 1, 0.55))
    return "".join(out)


def phat(u, cx, base, s, seed, felt="#3A2C52", tints=("#4E3E6E", "#251A38", "#5E4C80", "#30243F"), band="#5C8A2C", buckle=GOLD, rot=0, line=INKN):
    """Gouache witch hat: wide floppy brim, tall crown bending over at the tip, felt strokes, band and buckle."""
    def T(pts):
        return [(cx + x * s, base + y * s) for x, y in pts]
    out = [f'<g transform="rotate({rot} {cx} {base})">']
    brim = blob(cx, base, 112 * s, 24 * s, seed, 0.03, 20)
    out.append(f'<ellipse cx="{cx:.1f}" cy="{base + 18 * s:.1f}" rx="{104 * s:.1f}" ry="{10 * s:.1f}" fill="#000" opacity="0.18"/>')
    out.append(pshape(f"{u}-br", brim, felt, list(tints), seed, (cx - 116 * s, base - 28 * s, cx + 116 * s, base + 28 * s), angle=0, n=70, length=(14, 40), width=(1.2, 3), line=line, lw=2.4))
    crown = smooth_closed(T([(-52, -6), (-42, -60), (-26, -112), (-8, -150), (14, -176), (42, -186), (64, -176), (56, -168), (38, -164), (20, -146), (14, -112), (26, -60), (52, -6)]))
    out.append(pshape(f"{u}-cr", crown, felt, list(tints), seed + 1, (cx - 60 * s, base - 190 * s, cx + 70 * s, base), angle=-80, n=110, length=(14, 36), width=(1.2, 3.2),
                      shade=("#120A1C", 0.55, 14 * s, 0), line=line, lw=2.4))
    bnd = hpath(T([(-60, -40), (60, -40), (60, -12), (-60, -12)]), seed + 2, 0.4)
    out.append(inside(f"{u}-bn", crown, pshape(f"{u}-bnd", bnd, band, [lighten(band, 0.25), darken(band, 0.25)], seed + 2, (cx - 62 * s, base - 42 * s, cx + 62 * s, base - 10 * s),
                                                angle=0, n=30, length=(10, 24), width=(1, 2.4)) + f'<path d="{bnd}" fill="#000" opacity="0.25" transform="translate({10 * s:.1f} 0)"/>'))
    bk = hpath(T([(-12, -40), (10, -40), (10, -12), (-12, -12)]), seed + 3, 0.3)
    bki = hpath(T([(-6, -34), (4, -34), (4, -18), (-6, -18)]), seed + 4, 0.3)
    out.append(f'<path d="{bk} {bki}" fill="{buckle}" fill-rule="evenodd"/>' + ink(bk, "#7A5010", 1.6, seed, 1, 0.9) + ink(f"M {cx - 10 * s:.1f} {base - 37 * s:.1f} L {cx - 10 * s:.1f} {base - 16 * s:.1f}", "#FFF3C0", 1.4, seed, 1, 0.8))
    # front lip of the brim over the crown base
    out.append(inside(f"{u}-fl", f"M {cx - 130 * s:.1f} {base - 2 * s:.1f} L {cx + 130 * s:.1f} {base - 2 * s:.1f} L {cx + 130 * s:.1f} {base + 40 * s:.1f} L {cx - 130 * s:.1f} {base + 40 * s:.1f} Z",
                      f'<path d="{brim}" fill="{felt}"/>' + tex(f"{u}-flt", brim, list(tints), seed + 5, (cx - 116 * s, base - 4, cx + 116 * s, base + 28 * s), n=40, angle=0, length=(14, 40), width=(1.2, 3))))
    out.append(ink(brim, line, 2.4, seed + 6, 1, 0.9))
    out.append(ink(f"M {cx - 96 * s:.1f} {base + 8 * s:.1f} Q {cx:.1f} {base + 26 * s:.1f} {cx + 96 * s:.1f} {base + 8 * s:.1f}", "#9C8AC8", 2, seed, 1, 0.5))
    out.append(ink(smooth_open(T([(-44, -50), (-30, -104), (-12, -142)])), "#9C8AC8", 2, seed, 1, 0.45))
    out.append("</g>")
    return "".join(out)


def pbook(u, x, y, w, h, seed, cover="#5A2E72", tints=("#6E3E8A", "#3E1A52", "#7E4E9A"), pages="#F2E6CC", band=GOLD, rot=0):
    """Closed book lying flat seen from the spine side: cover, page block peeking out, gilt bands."""
    out = [f'<g transform="rotate({rot} {x + w / 2:.1f} {y + h / 2:.1f})">']
    pg = hpath([(x + 6, y + 4), (x + w + 2, y + 5), (x + w + 2, y + h - 5), (x + 6, y + h - 4)], seed, 0.4)
    out.append(f'<path d="{pg}" fill="{pages}"/>' + ink(" ".join(f"M {x + 10} {y + 6 + k * (h - 12) / 6:.1f} L {x + w} {y + 6 + k * (h - 12) / 6:.1f}" for k in range(1, 6)), "#C8B490", 1, seed, 1, 0.8))
    cv = hpath([(x, y), (x + w - 10, y), (x + w - 10, y + 5), (x + 8, y + 6), (x + 8, y + h - 6), (x + w - 10, y + h - 5), (x + w - 10, y + h), (x, y + h)], seed + 1, 0.5)
    cv = hpath([(x, y), (x + w * 0.86, y), (x + w * 0.86, y + h), (x, y + h)], seed + 1, 0.5)
    out.append(pshape(f"{u}-cv", cv, cover, list(tints), seed + 1, (x, y, x + w, y + h), angle=0, n=40, length=(14, 40), width=(1, 2.6), line=INKN, lw=2,
                      shade=(darken(cover, 0.4), 0.5, 0, h * 0.18)))
    for bx in (x + w * 0.12, x + w * 0.7):
        out.append(f'<rect x="{bx:.1f}" y="{y + 2:.1f}" width="{w * 0.05:.1f}" height="{h - 4:.1f}" fill="{band}" opacity="0.9"/>')
    out.append(f'<path d="{blob(x + w * 0.42, y + h / 2, w * 0.13, h * 0.24, seed, 0.08, 10)}" fill="none" stroke="{band}" stroke-width="1.8"/>')
    out.append("</g>")
    return "".join(out)


def candy_corn(x, y, s, rot, seed):
    d = f"M 0 -20 C 6 -20 16 6 17 14 C 18 20 -18 20 -17 14 C -16 6 -6 -20 0 -20 Z"
    rnd = random.Random(seed)
    st = "".join(_lens(rnd.uniform(-16, 12), rnd.uniform(-18, 18), rnd.uniform(6, 14), rnd.uniform(0.8, 1.6), math.radians(-90 + rnd.uniform(-10, 10)), 0, rnd.choice(["#FFFFFF", "#C8581E", "#E8A020"]), 0.35) for _ in range(10))
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<clipPath id="gacandy-cc{seed}"><path d="{d}"/></clipPath><g clip-path="url(#gacandy-cc{seed})"><rect x="-20" y="-22" width="40" height="44" fill="#FFF6E2"/>'
            f'<rect x="-20" y="-8" width="40" height="14" fill="#F07A22"/><rect x="-20" y="6" width="40" height="16" fill="#FFC23A"/>{st}'
            f'<path d="M -6 -14 Q -10 0 -12 12" stroke="#FFFFFF" stroke-width="2.4" fill="none" opacity="0.6" stroke-linecap="round"/></g>'
            f'<path d="{d}" fill="none" stroke="{INKB}" stroke-width="{2 / max(s, 0.4):.1f}" stroke-linejoin="round" opacity="0.8"/></g>')


def wrapped_candy(x, y, s, rot, seed, col="#C2577A", stripe="#FFE2EC"):
    body = blob(0, 0, 16, 11, seed, 0.05, 14)
    ends = "M -14 -2 L -30 -12 Q -26 0 -30 12 L -14 2 Z M 14 -2 L 30 -12 Q 26 0 30 12 L 14 2 Z"
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<path d="{ends}" fill="{lighten(col, 0.25)}"/><path d="{ends}" fill="none" stroke="{INKB}" stroke-width="1.6" opacity="0.7" stroke-linejoin="round"/>'
            f'<path d="M -26 -6 L -18 -2 M -26 6 L -18 2 M 26 -6 L 18 -2 M 26 6 L 18 2" stroke="{darken(col, 0.3)}" stroke-width="1.4" opacity="0.6"/>'
            f'<path d="{body}" fill="{col}"/><clipPath id="gacandy-wc{seed}"><path d="{body}"/></clipPath><g clip-path="url(#gacandy-wc{seed})">'
            + "".join(f'<path d="M {k} -14 L {k + 10} 14" stroke="{stripe}" stroke-width="3.4" opacity="0.85"/>' for k in range(-24, 20, 9))
            + f'<ellipse cx="4" cy="6" rx="16" ry="8" fill="#000" opacity="0.18"/></g><path d="M -9 -5 Q -2 -9 6 -7" stroke="#FFFFFF" stroke-width="2.2" fill="none" stroke-linecap="round" opacity="0.8"/>'
            f'<path d="{body}" fill="none" stroke="{INKB}" stroke-width="1.8" opacity="0.8"/></g>')


def lollipop(x, y, s, rot, seed, cols=("#9A5AC8", "#FFF2F8")):
    sw = "".join(f'<path d="M 0 0 m {-k * 2.2:.1f} 0 a {k * 2.2:.1f} {k * 2.2:.1f} 0 0 1 {k * 4.4:.1f} 0" stroke="{cols[k % 2]}" stroke-width="2.6" fill="none"/>'
                 f'<path d="M 0 0 m {k * 2.2 + 1.1:.1f} 0 a {k * 2.2 + 1.1:.1f} {k * 2.2 + 1.1:.1f} 0 0 1 {-(k * 4.4 + 2.2):.1f} 0" stroke="{cols[(k + 1) % 2]}" stroke-width="2.6" fill="none"/>' for k in range(1, 7))
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<path d="M 0 14 L 0 46" stroke="#F4EBD9" stroke-width="4.4" stroke-linecap="round"/><path d="M 0 14 L 0 46" stroke="{INKB}" stroke-width="1" opacity="0.4" transform="translate(1.6 0)"/>'
            f'<circle r="15.5" fill="{cols[0]}"/>{sw}<circle r="15.5" fill="none" stroke="{INKB}" stroke-width="1.8" opacity="0.8"/>'
            f'<path d="M -9 -6 Q -6 -11 0 -12" stroke="#FFFFFF" stroke-width="2.4" fill="none" stroke-linecap="round" opacity="0.8"/></g>')


def ribbon_banner(u, cx, cy, w, h, seed, col="#E06C26", dark="#9A3A12", tints=("#F29A4A", "#C8501A", "#FFB86A"), tail=46, drop=18):
    """Painted ribbon banner: a gently curved band with folded, notched tails behind."""
    l, r = cx - w / 2, cx + w / 2
    out = []
    for sx in (-1, 1):
        e = l if sx < 0 else r
        t = hpath([(e - sx * 8, cy - h / 2 + drop), (e + sx * tail, cy - h / 2 + drop), (e + sx * (tail - 16), cy + drop), (e + sx * tail, cy + h / 2 + drop), (e - sx * 8, cy + h / 2 + drop)], seed + sx, 0.6)
        out.append(pshape(f"{u}-t{sx + 1}", t, dark, [darken(dark, 0.2), col], seed + sx, (e - 20 - tail, cy - h, e + 20 + tail, cy + h + drop), angle=0, n=30, length=(10, 24), width=(1, 2.4), line=INKB, lw=2))
        fold = hpath([(e - sx * 2, cy + h / 2 - 4), (e - sx * 2, cy + h / 2 + drop), (e - sx * 20, cy + h / 2)], seed + 5 + sx, 0.3)
        out.append(f'<path d="{fold}" fill="{darken(dark, 0.35)}"/>')
    band = (f"M {l:.1f} {cy - h / 2:.1f} Q {cx:.1f} {cy - h / 2 - 18:.1f} {r:.1f} {cy - h / 2:.1f} L {r:.1f} {cy + h / 2:.1f} Q {cx:.1f} {cy + h / 2 - 18:.1f} {l:.1f} {cy + h / 2:.1f} Z")
    out.append(pshape(f"{u}-bd", band, col, list(tints), seed, (l, cy - h, r, cy + h), angle=0, n=110, length=(16, 46), width=(1.2, 3), line=INKB, lw=2.4,
                      shade=(dark, 0.45, 0, 7)))
    out.append(ink(f"M {l + 10:.1f} {cy - h / 2 + 7:.1f} Q {cx:.1f} {cy - h / 2 - 11:.1f} {r - 10:.1f} {cy - h / 2 + 7:.1f}", "#FFE2B8", 1.6, seed, 1, 0.7))
    out.append(ink(f"M {l + 10:.1f} {cy + h / 2 - 7:.1f} Q {cx:.1f} {cy + h / 2 - 25:.1f} {r - 10:.1f} {cy + h / 2 - 7:.1f}", "#FFE2B8", 1.6, seed + 1, 1, 0.7))
    return "".join(out)


def candy_pail(u, cx, cy, w, h, seed):
    """Plastic jack-o'-lantern candy pail, overflowing."""
    rnd = random.Random(seed)
    out = []
    top = cy - h / 2
    out.append(ink(f"M {cx - w * 0.44:.1f} {top + 8:.1f} C {cx - w * 0.5:.1f} {top - h * 0.9:.1f} {cx + w * 0.5:.1f} {top - h * 0.9:.1f} {cx + w * 0.44:.1f} {top + 8:.1f}", "#1A1226", 5, seed, 1, 1))
    # candy heap behind the rim
    heap = []
    for i in range(9):
        a = rnd.uniform(-0.4, 0.4)
        px, py = cx + a * w * 1.05, top - rnd.uniform(4, 22) + abs(a) * 26
        k = i % 3
        if k == 0:
            heap.append(candy_corn(px, py, rnd.uniform(0.75, 0.95), rnd.uniform(-40, 40), seed + 300 + i))
        elif k == 1:
            heap.append(wrapped_candy(px, py, rnd.uniform(0.75, 0.95), rnd.uniform(-30, 30), seed + 300 + i, rnd.choice(["#C2577A", "#5A8ACA", SLIME_D, "#9A5AC8"])))
        else:
            heap.append(lollipop(px, py - 14, 0.85, rnd.uniform(-30, 30), seed + 300 + i, rnd.choice([("#9A5AC8", "#FFF2F8"), ("#E8792E", "#FFF6E2"), ("#5AA83A", "#F4FFE0")])))
    out.append("".join(heap))
    body = smooth_closed([(cx - w * 0.5, top + 4), (cx, top - 2), (cx + w * 0.5, top + 4), (cx + w * 0.54, cy + h * 0.1), (cx + w * 0.42, cy + h * 0.46),
                          (cx, cy + h / 2 + 2), (cx - w * 0.42, cy + h * 0.46), (cx - w * 0.54, cy + h * 0.1)])
    out.append(pshape(f"{u}-pb", body, "#F07A22", ["#FFA24A", "#C8501A", "#FFB86A", "#E06C26"], seed, (cx - w * 0.6, top - 4, cx + w * 0.6, cy + h / 2 + 4), angle=-90, n=80,
                      length=(10, 30), width=(1.4, 3.4), shade=("#9A3A12", 0.5, w * 0.08, 0), line="#5A1E08", lw=2.4))
    for dx in (-0.22, 0.22):
        out.append(ink(f"M {cx + dx * w:.1f} {top + 6:.1f} Q {cx + dx * 1.4 * w:.1f} {cy:.1f} {cx + dx * w:.1f} {cy + h * 0.46:.1f}", "#C8501A", 2, seed, 1, 0.6))
    rim = blob(cx, top + 3, w * 0.5, h * 0.07, seed + 1, 0.03, 16)
    out.append(f'<path d="{rim}" fill="#E06C26"/>' + ink(rim, "#5A1E08", 2, seed, 1, 0.9))
    # cute carved face (printed on the pail)
    for ex in (cx - w * 0.17, cx + w * 0.17):
        out.append(f'<path d="M {ex - w * 0.08:.1f} {cy - h * 0.02:.1f} L {ex:.1f} {cy - h * 0.2:.1f} L {ex + w * 0.08:.1f} {cy - h * 0.02:.1f} Z" fill="#2A0E06"/>')
    out.append(f'<path d="M {cx - w * 0.28:.1f} {cy + h * 0.1:.1f} Q {cx:.1f} {cy + h * 0.42:.1f} {cx + w * 0.28:.1f} {cy + h * 0.1:.1f} Q {cx:.1f} {cy + h * 0.24:.1f} {cx - w * 0.28:.1f} {cy + h * 0.1:.1f} Z" fill="#2A0E06"/>')
    out.append(f'<path d="M {cx - w * 0.3:.1f} {top + h * 0.2:.1f} Q {cx - w * 0.4:.1f} {cy:.1f} {cx - w * 0.32:.1f} {cy + h * 0.3:.1f}" stroke="#FFE2B8" stroke-width="{max(2, w * 0.03):.1f}" fill="none" stroke-linecap="round" opacity="0.7"/>')
    return "".join(out)


def magnifier(u, cx, cy, r, ang, seed, inner=""):
    """Brass magnifying glass; inner = svg drawn magnified inside the lens."""
    a = math.radians(ang)
    hx, hy = cx + math.cos(a) * r * 1.05, cy + math.sin(a) * r * 1.05
    ex, ey = cx + math.cos(a) * r * 2.4, cy + math.sin(a) * r * 2.4
    out = [ink(f"M {hx:.1f} {hy:.1f} L {ex:.1f} {ey:.1f}", "#3A1E10", r * 0.34, seed, 1, 1), ink(f"M {hx:.1f} {hy:.1f} L {ex:.1f} {ey:.1f}", "#8A4A2A", r * 0.24, seed, 1, 1),
           ink(f"M {hx + (ex - hx) * 0.2:.1f} {hy + (ey - hy) * 0.2:.1f} L {ex - (ex - hx) * 0.1:.1f} {ey - (ey - hy) * 0.1:.1f}", "#C87A4A", r * 0.06, seed, 1, 0.8)]
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#E8F4FF" opacity="0.92"/>')
    out.append(inside(f"{u}-ln", f"M {cx - r:.1f} {cy:.1f} a {r:.1f} {r:.1f} 0 1 0 {2 * r:.1f} 0 a {r:.1f} {r:.1f} 0 1 0 {-2 * r:.1f} 0 Z", inner
                      + f'<path d="M {cx - r * 0.6:.1f} {cy - r * 0.2:.1f} Q {cx - r * 0.5:.1f} {cy - r * 0.6:.1f} {cx - r * 0.1:.1f} {cy - r * 0.7:.1f}" stroke="#FFFFFF" stroke-width="{r * 0.1:.1f}" fill="none" stroke-linecap="round" opacity="0.8"/>'))
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="#B8862E" stroke-width="{r * 0.16:.1f}"/>'
               f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 1.08:.1f}" fill="none" stroke="#5A3A10" stroke-width="2"/><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.92:.1f}" fill="none" stroke="#5A3A10" stroke-width="1.4"/>'
               + ink(f"M {cx - r * 0.7:.1f} {cy - r * 0.7:.1f} A {r:.1f} {r:.1f} 0 0 1 {cx + r * 0.4:.1f} {cy - r * 0.92:.1f}", "#FFE9A8", 2, seed, 1, 0.7))
    return "".join(out)


# ================================================================ designs (part 3)
def d_happy_haunting():
    u = "gahaunt"
    o = [sky(u, [(0, "#1E1438"), (0.32, "#4A2858"), (0.55, "#9A4A5E"), (0.72, "#E07A4A"), (0.82, "#F6B060")], 601, box=(0, 0, 600, 480), n=420, amt=0.1)]
    o.append(stars(602, 22, (20, 16, 580, 120), tw=3))
    o.append(moon(u, 300, 344, 122, 603, base="#FFCC80", shade="#E8904A", hi="#FFF0C8", halo="#FFD28A", halo_r=1.7, halo_op=0.5, line="#C8704A"))
    o.append(cloud(u + "c1", 120, 250, 220, 12, 604, "#B8586A", "#F6B08A", 0.7))
    o.append(cloud(u + "c2", 500, 220, 180, 11, 605, "#B8586A", "#F6B08A", 0.6))
    # distant farm: hill, barn, a few bare trees
    h1, l1 = hill(u + "h1", [(-20, 418), (160, 408), (330, 414), (620, 402)], 606, 600, "#4A2238", ["#5A2A42", "#3A1A2E", "#6A3248"], rim="#F6A070", amp=3)
    o.append(h1)
    bx = 470
    by = y_on(l1, bx) + 4
    barn = hpath([(bx - 30, by), (bx - 30, by - 34), (bx, by - 58), (bx + 30, by - 34), (bx + 30, by)], 607, 0.6)
    o.append(f'<path d="{barn}" fill="#2E1424"/>' + ink(hpath([(bx - 30, by - 34), (bx, by - 58), (bx + 30, by - 34)], 608, 0.4, False), "#F6A070", 1.8, 608, 1, 0.6))
    o.append(f'<path d="{hpath([(bx + 34, by), (bx + 34, by - 62), (bx + 54, by - 62), (bx + 54, by)], 609, 0.5)}" fill="#2E1424"/><path d="{blob(bx + 44, by - 62, 10, 7, 609, 0.05, 10)}" fill="#2E1424"/>')
    o.append(window(u + "bw", bx - 7, by - 30, 14, 18, 610, lit=("#FFCF6A", "#F59A3A"), frame="#2E1424", glow_op=0.35))
    for i, (x, h) in enumerate(((70, 110), (118, 80), (540, 90))):
        o.append(tree(x, y_on(l1, x) + 4, h, 611 + i, "#2E1424", rim="#F6A070", lean=(-1) ** i * 6, spread=28, depth=5))
    # the pumpkin patch in rows, shrinking into the distance
    fd = f"M -10 430 L 610 422 L 610 600 L -10 600 Z"
    o.append(pshape(u + "fd", fd, "#3A1E28", ["#4A2632", "#2A141C", "#5A3038"], 612, (-10, 420, 610, 600), angle=-2, n=240, length=(20, 60), width=(2, 5)))
    o.append(defs(lg(u + "-fdd", [(0, "#120812", 0), (1, "#120812", 0.6)])) + '<rect x="0" y="420" width="600" height="180" fill="url(#gahaunt-fdd)"/>')
    rnd = random.Random(613)
    for row, (y, sc) in enumerate(((440, 0.28), (462, 0.4), (490, 0.56))):
        o.append(ink(f"M -10 {y + 6} C 160 {y} 440 {y + 10} 610 {y + 2}", "#3E5A26", 2.4 + row, 614 + row, 1, 0.8))
        x = rnd.uniform(-10, 30)
        while x < 600:
            if not (240 < x < 360 and row == 2):
                o.append(painted_pumpkin(f"{u}-pp{row}{int(x)}", x, y + 2, 90 * sc, 64 * sc, rnd.randrange(999), body="#D86A2A", dark="#8A3412", light="#F29A4A", leaf="#4E6A2E"))
            x += rnd.uniform(80, 130) * (0.6 + sc)
    o.append(scarecrow(u + "sc", 300, 232, 615))
    o.append(crow(198, 318, 1.7, flip=True, fill="#1A0E18") + crow(476, 266, 1.3, flip=True, fill="#1A0E18"))
    o.append(pbat(140, 190, 16, -10) + pbat(456, 150, 12, 8))
    o.append(jack(u + "j1", 110, 520, 98, 70, 616, "classic", glow_r=120, night=False))
    o.append(jack(u + "j2", 492, 528, 82, 58, 617, "sly", glow_r=100, night=False))
    o.append(soft(300, 640, 380, 120, "#05030C", u + "fb", 0.5))
    o.append(ptext(u + "t1", 300, 94, "happy", SERIF_IT, 70, BONE, ["#FFFFFF", "#F6E2C8", "#E8D2E6"], 618, max_w=300, angle=-58, shadow="#1A0A1A", hi="#FFFFFF"))
    o.append(ptext(u + "t2", 300, 190, "HAUNTING", BEBAS, 80, "#FFD08A", ["#FFE8B8", "#F6A050", "#FFF3D6", "#F2B868"], 619, max_w=440, ls=12, shadow="#2A0E1E", hi="#FFFFFF"))
    o.append(finish(u, 15, vign=0.4, vcol="#0A0410"))
    return "".join(o)


def d_witch_please():
    u = "gawp"
    o = [paper(u + "-p", "#F2E8D4", "#6A5A3A", 21)]
    wd = blob(300, 236, 236, 150, 22, 0.05, 26)
    o.append(wash(wd, "#C9DE9A", 22, 3, 3, 0.4))
    o.append(tex(u + "-sw", wd, ["#B8D27A", "#DDEBB8", "#A8C66A", "#E8F2CC"], 23, (50, 80, 550, 400), n=300, angle=-14, length=(30, 90), width=(4, 10), op=(0.25, 0.55)))
    rnd = random.Random(24)
    rim = []
    for i in range(80):
        a = 2 * math.pi * i / 80 + rnd.uniform(-0.03, 0.03)
        rr = rnd.uniform(0.96, 1.04)
        rim.append(_lens(300 + 236 * rr * math.cos(a), 236 + 150 * rr * math.sin(a), rnd.uniform(14, 34), rnd.uniform(1.5, 4), a + math.pi / 2, 2, rnd.choice(["#B8D27A", "#A8C66A", "#C9DE9A"]), rnd.uniform(0.3, 0.7)))
    o.append("".join(rim))
    # stars and a crescent on the swatch
    o.append(twinkle(96, 136, 9, "#E8A030") + twinkle(508, 120, 7, "#E8A030") + twinkle(530, 318, 8, "#E8A030") + twinkle(72, 330, 6, "#E8A030"))
    cres = "M 486 196 A 26 26 0 1 0 512 236 A 20 20 0 1 1 486 196 Z"
    o.append(f'<path d="{cres}" fill="#F2C866"/>' + ink(cres, "#A8741A", 1.6, 25, 1, 0.8))
    # still life: books, the hat, a potion and a candle
    o.append(f'<ellipse cx="300" cy="520" rx="210" ry="14" fill="#3A2418" opacity="0.16"/>')
    o.append(pbook(u + "b1", 196, 476, 216, 42, 26, cover="#3E6A3A", tints=("#4E7E48", "#2A4A28", "#5E8E58")))
    o.append(pbook(u + "b2", 208, 440, 190, 38, 27, cover="#6A3A86", tints=("#7E4E9A", "#4A2462", "#8E5EAA"), rot=-2))
    o.append(phat(u + "h", 302, 434, 0.96, 28, rot=-4))
    o.append(flask(u + "fk", 120, 522, 64, 104, 29, liquid=("#E6FFB0", SLIME, SLIME_D), glow_op=0.25))
    o.append(pcandle(u + "cd", 484, 522, 92, 30, 30, glow_op=0.35))
    o.append(twinkle(176, 404, 6, "#E8A030") + twinkle(420, 366, 5, "#E8A030") + twinkle(560, 450, 6, "#E8A030"))
    o.append(ptext(u + "t1", 300, 196, "WITCH", BEBAS, 150, "#3A2350", ["#4E3270", "#2A1640", "#5E4280", "#24123A"], 31, max_w=420, ls=14, shadow="#8ABE4A", angle=-80))
    o.append(ptext(u + "t2", 288, 272, "please", SERIF_IT, 88, "#3E6A1E", ["#5C8A2C", "#2E5214", "#6E9E3A"], 32, max_w=280, angle=-58, shadow="#F2E8D4", rot=-5))
    o.append(grain(u + "-gr", INKB, 6, 0.9))
    return "".join(o)


def d_official_candy_inspector():
    u = "gacandy"
    o = [sky(u, [(0, "#24163E"), (0.5, "#30204E"), (1, "#24163E")], 701, n=380, angle=-30, length=(30, 100), amt=0.1)]
    rnd = random.Random(702)
    sc = []
    for i in range(30):
        while True:
            x, y = rnd.uniform(-10, 610), rnd.uniform(-10, 610)
            if math.hypot(x - 300, y - 268) > 222 and not (30 < x < 570 and 404 < y < 500):
                break
        k = i % 3
        if k == 0:
            sc.append(candy_corn(x, y, rnd.uniform(0.8, 1.1), rnd.uniform(0, 360), 800 + i))
        elif k == 1:
            sc.append(wrapped_candy(x, y, rnd.uniform(0.8, 1.05), rnd.uniform(0, 360), 800 + i, rnd.choice(["#C2577A", "#5A8ACA", SLIME_D, "#9A5AC8", "#E8792E"])))
        else:
            sc.append(lollipop(x, y, rnd.uniform(0.8, 1.0), rnd.uniform(0, 360), 800 + i, rnd.choice([("#9A5AC8", "#FFF2F8"), ("#E8792E", "#FFF6E2"), ("#5AA83A", "#F4FFE0"), ("#C2577A", "#FFE2EC")])))
    o.append(f'<g opacity="0.9">{"".join(sc)}</g>')
    o.append(soft(300, 268, 300, 300, "#FFB547", u + "-bg", 0.22))
    # rosette badge
    R = 214
    pts = []
    for i in range(96):
        a = 2 * math.pi * i / 96
        rr = R * (1 + 0.045 * math.cos(24 * a)) * (1 + rnd.uniform(-0.004, 0.004))
        pts.append((300 + rr * math.cos(a), 268 + rr * math.sin(a)))
    ros = smooth_closed(pts)
    o.append(f'<path d="{ros}" fill="#000" opacity="0.35" transform="translate(6 9)"/>')
    rays = "".join(_lens(300 + math.cos(a) * R * 0.78, 268 + math.sin(a) * R * 0.78, R * 0.26, 2.2, a, 0, rnd.choice(["#FFD27A", "#C8701A", "#FFE9A8"]), rnd.uniform(0.3, 0.6))
                   for a in [rnd.uniform(0, 6.28) for _ in range(160)])
    o.append(f'<path d="{ros}" fill="#F2A23A"/>' + inside(u + "-ro", ros, rays + f'<path d="{ros}" fill="none" stroke="#9A4A10" stroke-width="16" opacity="0.35" transform="translate(5 7)"/>'))
    o.append(ink(ros, "#5A2A08", 2.6, 703, 2, 0.85))
    disc = blob(300, 268, 168, 168, 704, 0.008, 30)
    o.append(pshape(u + "dc", disc, "#F6ECD6", ["#FFFFFF", "#EADCBC", "#FFF8EA", "#E2D2B0"], 705, (130, 98, 470, 438), angle=-30, n=200, length=(20, 60), width=(2, 5),
                    shade=("#C8B08A", 0.4, 6, 8), line="#7A4A1A", lw=2.4))
    o.append(ink(blob(300, 268, 156, 156, 706, 0.006, 30), "#C8501A", 2, 706, 1, 0.8))
    o.append("".join(f'<circle cx="{300 + 146 * math.cos(math.radians(a)):.1f}" cy="{268 + 146 * math.sin(math.radians(a)):.1f}" r="2.2" fill="#C8501A"/>' for a in range(0, 360, 9)))
    arc, _ = arc_text(u + "of", "OFFICIAL", 300, 268, 112, BEBAS, 50, "#3A2350", ["#4E3270", "#2A1640", "#5E4280"], 707, ls=10, top=True, max_deg=150)
    o.append(arc)
    o.append(twinkle(176, 262, 9, "#E8792E") + twinkle(424, 262, 9, "#E8792E"))
    o.append(pglow(u + "pg", 300, 300, 120, "#FFB547", 0.35, 708))
    o.append(candy_pail(u + "pl", 296, 312, 128, 104, 709))
    mag_inner = candy_corn(384, 330, 1.7, 18, 899)
    o.append(magnifier(u + "mg", 384, 330, 34, 52, 710, inner=f'<rect x="340" y="290" width="90" height="90" fill="#F6ECD6"/>' + mag_inner))
    o.append(ribbon_banner(u + "rb", 300, 452, 432, 70, 711))
    o.append(ptext(u + "t1", 300, 468, "CANDY INSPECTOR", BEBAS, 50, BONE, ["#FFFFFF", "#FFE8C8", "#F6D8B0"], 712, max_w=370, ls=4, shadow="#5A1E08", angle=-80))
    o.append(label(300, 540, "EST. OCTOBER 31", MONO, 18, CANDLE, ls=4, shadow=INKN))
    o.append(finish(u, 16, vign=0.4))
    return "".join(o)


def d_here_for_the_boos():
    u = "gaboos"
    o = [sky(u, [(0, NIGHT0), (0.5, "#261E52"), (0.85, "#3A2C6A"), (1, "#46387A")], 901, swirl=(456, 300, 74, 150, "#CDBCEB"))]
    o.append(stars(902, 40, (20, 20, 580, 420), avoid=[(456, 300, 110)]))
    o.append(moon(u, 456, 300, 72, 903, halo_r=2.0))
    o.append(cloud(u + "c1", 150, 330, 220, 12, 904, "#4A3A7A", "#C8B6E8", 0.6))
    o.append(tree(574, 446, 230, 905, SIL, rim="#B8A6DC", lean=-10, spread=30, depth=6))
    # garden wall with a lit cap
    o.append(stones(u + "wl", (0, 436, 600, 600), 906, cols=("#4A4266", "#3E3758", "#544A70", "#463E62"), mortar="#14101F", rim="#B8A6DC", rows=(30, 38), widths=(60, 110), rim_op=0.5))
    cap = hpath([(-10, 428), (610, 424), (610, 446), (-10, 450)], 907, 1)
    o.append(pshape(u + "cp", cap, "#6A6290", ["#7E76A4", "#544C78", "#8E86B4"], 907, (-10, 420, 610, 452), angle=0, n=120, length=(20, 60), width=(1.2, 3), line=INKN, lw=2))
    o.append(ink("M -10 429 L 610 425", "#D8C8F0", 2, 908, 1, 0.6))
    # ivy trailing over the wall
    rnd = random.Random(909)
    iv = []
    for x0 in (36, 300, 420):
        pts = [(x0 + k * 8 + rnd.uniform(-4, 4), 440 + k * 12 + math.sin(k) * 6) for k in range(7)]
        iv.append(ink(smooth_open(pts), "#2E4A2A", 2, x0, 1, 1))
        for k, (x, y) in enumerate(pts[1:]):
            iv.append(pleaf(x + (-1) ** k * 8, y, 8, (-1) ** k * 40 + 90, "#3E6A3A", "#1A2E18", x0 + k))
    o.append("".join(iv))
    o.append(soft(300, 600, 360, 100, "#05030C", u + "fb", 0.5))
    # the cat on its pumpkin, watching the show
    o.append(jack(u + "jk", 164, 386, 150, 104, 910, "classic", glow_r=170, glow_op=0.55))
    from halloween_painted import black_cat
    o.append(black_cat(u + "cat", 168, 346, 1.0, fill=SIL, rim="#FFD9A0", eye="#D9F05A"))
    o.append(jack(u + "j2", 508, 422, 56, 40, 911, "cute", glow_r=70))
    # the boos
    o.append(pghost(u + "g1", 330, 238, 104, 912, face="happy", lean=-0.4, glow_op=0.35, wave=1))
    o.append(pghost(u + "g2", 464, 286, 78, 913, face="boo", lean=-0.5, glow_op=0.3))
    o.append(pghost(u + "g3", 506, 200, 50, 914, face="wink", lean=-0.6, arms=False, glow_op=0.25))
    o.append(stars(915, 0, (300, 220, 560, 420), col="#FFFFFF", tw=5, twr=(4, 7)))
    o.append(ptext(u + "t1", 300, 104, "here for the", SERIF_IT, 64, BONE, ["#FFFFFF", "#E6D8C0", "#D2C4EA"], 916, max_w=380, angle=-58, shadow=INKN, hi="#FFFFFF"))
    o.append(ptext(u + "t2", 300, 214, "BOOS", BEBAS, 124, "#FFFFFF", ["#FFFFFF", "#E8E0FF", "#D2C4EA", "#F4F0FF"], 917, max_w=380, ls=26, shadow=INKN,
                   glow="#D8CCFF", glow_op=0.3, hi="#FFFFFF"))
    o.append(finish(u, 17, vign=0.45))
    return "".join(o)

BUILD = {
    "haunted-hotel": d_haunted_hotel,
    "broom-with-a-view": d_broom_with_a_view,
    "trick-or-treat": d_trick_or_treat,
    "eye-of-newt": d_eye_of_newt,
    "spooky-season": d_spooky_season,
    "boo": d_boo,
    "happy-halloween": d_happy_halloween,
    "witches-brew": d_witches_brew,
    "enter-if-you-dare": d_enter_if_you_dare,
    "whooos-there": d_whooos_there,
    "glow-getter": d_glow_getter,
    "happy-haunting": d_happy_haunting,
    "witch-please": d_witch_please,
    "official-candy-inspector": d_official_candy_inspector,
    "here-for-the-boos": d_here_for_the_boos,
}


def build(only=None):
    for slug, fn in BUILD.items():
        if only and slug not in only:
            continue
        save(COL, slug, fn())


if __name__ == "__main__":
    build(sys.argv[1:])
