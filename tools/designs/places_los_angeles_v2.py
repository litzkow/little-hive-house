"""Los Angeles, v2: Santa Monica Pier at golden hour, seen from the beach to the south.

The Ferris wheel and the roller coaster stand on the long wooden pier, the sun drops toward the sea on the left,
the Santa Monica Mountains fade into the haze behind, tall fan palms frame the right, and a cyclist rolls along the
beach bike path. Daylight palette of the first-version posters (cream and peach sky, teal sea, sage palms), light
name band. Writes the SVG to the scratchpad (designs/ stays untouched until the owners approve)."""
import math
import pathlib
import random
import sys

from paint import P, blobs, dots, glow, lg, mist, rg, rough, streaks, y_on
import figures as F
import poster as PST

OUT = pathlib.Path("/tmp/claude-0/-home-claude-little-hive-house/126373fb-bcff-5469-8b97-3f0485f13186/scratchpad/new-places")
U = "la2"
SUN = (118, 214)
HZ = 266            # sea horizon


def defs(*items):
    return "<defs>" + "".join(items) + "</defs>"


def poly(pts, fill, extra=""):
    return f'<polygon points="{P(pts)}" fill="{fill}"{extra}/>'


# ---------------------------------------------------------------- pieces
def streak_cloud(cx, cy, w, h, seed, body="#F6CBA4", lit="#FFF1DE", belly="#EFA982", op=1.0):
    """Long flat golden-hour cloud: lens of soft puffs, a lit crown and a warm underside toward the sun."""
    rnd = random.Random(seed)
    puffs = []
    n = max(6, int(w / 9))
    for i in range(n):
        t = (i + rnd.uniform(-0.3, 0.3)) / (n - 1)
        env = math.sin(math.pi * min(1, max(0, t))) ** 0.7
        r = h * (0.35 + 0.65 * env) * rnd.uniform(0.75, 1.1)
        puffs.append((cx + (t - 0.5) * w, cy - r * 0.35, r))
    b = "".join(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 1.6:.1f}" ry="{r:.1f}"/>' for x, y, r in puffs)
    li = "".join(f'<ellipse cx="{x - r * 0.4:.1f}" cy="{y - r * 0.35:.1f}" rx="{r * 1.1:.1f}" ry="{r * 0.5:.1f}"/>' for x, y, r in puffs if rnd.random() < 0.75)
    return (f'<g opacity="{op}"><g fill="{belly}"><ellipse cx="{cx:.1f}" cy="{cy + h * 0.15:.1f}" rx="{w * 0.5:.1f}" ry="{h * 0.35:.1f}"/></g>'
            f'<g fill="{body}">{b}</g><g fill="{lit}" opacity="0.8">{li}</g>'
            f'<path d="M {cx - w * 0.48:.1f} {cy + h * 0.32:.1f} Q {cx:.1f} {cy + h * 0.62:.1f} {cx + w * 0.46:.1f} {cy + h * 0.3:.1f}" fill="none" stroke="#FFE2B0" stroke-width="1.6" opacity="0.7"/></g>')


def fan_palm(x, base, h, seed, lean=0.0, R=None, sun=-1, crown=("#46703F", "#5E8A52", "#6F9A55", "#7C9B74"),
             lit="#C9CF8A", trunk=("#B58A62", "#7E5A44", "#E6C08E"), skirt="#B48660"):
    """Mexican fan palm (Washingtonia robusta): very tall thin trunk, a skirt of dry fronds under a small round crown
    of fan leaves. sun = -1 when the light comes from the left."""
    rnd = random.Random(seed)
    tx, ty = x + lean * h, base - h
    cx1, cy1 = x + lean * h * 0.15, base - h * 0.55
    R = R or h * 0.085
    w0, w1 = max(2.4, h * 0.022), max(1.6, h * 0.012)

    def pt(t, off):
        bx = (1 - t) ** 2 * x + 2 * t * (1 - t) * cx1 + t * t * tx
        by = (1 - t) ** 2 * base + 2 * t * (1 - t) * cy1 + t * t * ty
        dx = 2 * (1 - t) * (cx1 - x) + 2 * t * (tx - cx1)
        dy = 2 * (1 - t) * (cy1 - base) + 2 * t * (ty - cy1)
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = w0 + (w1 - w0) * t
        if t < 0.06:
            w *= 1 + (0.06 - t) * 9
        return bx + nx * w * off, by + ny * w * off

    N = 40
    left = [pt(i / N, -1) for i in range(N + 1)]
    right = [pt(i / N, 1) for i in range(N + 1)]
    mid = [pt(i / N, 0.15 * sun) for i in range(N + 1)]
    out = [poly(left + right[::-1], trunk[1])]
    # lit half of the trunk toward the sun
    lit_side = left if sun < 0 else right
    out.append(poly(lit_side + mid[::-1], trunk[0]))
    out.append(f'<polyline points="{P(lit_side[2:-2])}" fill="none" stroke="{trunk[2]}" stroke-width="{max(1.2, w1 * 0.7):.1f}" opacity="0.8"/>')
    # growth rings
    rings = []
    for i in range(2, N, 1):
        t = i / N + rnd.uniform(-0.008, 0.008)
        a, b = pt(t, -0.9), pt(t, 0.9)
        rings.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f}"/>')
    out.append(f'<g stroke="#5A3E30" stroke-width="0.9" opacity="0.35">{"".join(rings)}</g>')
    # dry-frond skirt hanging under the crown
    sk = []
    sw = R * 0.55
    top = ty + R * 0.1
    bot = ty + R * 1.05
    pts = [(tx - sw * 0.6, top)]
    for i in range(9):
        t = i / 8
        pts.append((tx - sw + 2 * sw * t + rnd.uniform(-1, 1), bot + rnd.uniform(-R * 0.25, R * 0.15) - abs(t - 0.5) * R * 0.3))
    pts.append((tx + sw * 0.6, top))
    sk.append(poly(pts, skirt))
    for i in range(9):
        xx = tx - sw * 0.8 + 1.6 * sw * i / 8
        sk.append(f'<path d="M {xx:.1f} {top + 1:.1f} q {rnd.uniform(-1.5, 1.5):.1f} {(bot - top) * 0.5:.1f} {rnd.uniform(-2, 2):.1f} {(bot - top) * rnd.uniform(0.7, 1):.1f}" '
                  f'stroke="{rnd.choice(["#8A6446", "#D8B080", "#7A5A40"])}" stroke-width="{rnd.uniform(1, 1.8):.1f}" fill="none" opacity="0.8"/>')
    lx = tx + sun * sw * 0.55
    sk.append(f'<path d="M {lx:.1f} {top + 1:.1f} q {sun * 2:.1f} {(bot - top) * 0.5:.1f} {sun * 1:.1f} {(bot - top) * 0.85:.1f}" stroke="#F2D29A" stroke-width="2" fill="none" opacity="0.75"/>')
    out.append("".join(sk))
    # fan fronds: back (dark) first, then front, lit fronds toward the sun
    fronds = []
    for i in range(12):                                   # back layer, all round, shaded
        fronds.append((-200 + i * 22 + rnd.uniform(-6, 6), 0))
    for i in range(13):                                   # main layer, upper half and sides
        fronds.append((-185 + i * 15.8 + rnd.uniform(-5, 5), 1))
    for a in (-150, -112, -70, -30, 18, 162, 50, 128):    # front layer, shorter, spreading toward us
        fronds.append((a + rnd.uniform(-8, 8), 2))
    for a, layer in fronds:
        ar = math.radians(a)
        down = math.sin(ar) > 0.2
        Lp = R * rnd.uniform(0.28, 0.4) * (0.7 if layer == 2 else 1)
        px, py = tx + Lp * math.cos(ar), ty + Lp * math.sin(ar) * 0.75
        Rf = R * rnd.uniform(0.6, 0.76) * (0.8 if layer == 2 else 1) * (0.9 if down else 1)
        spread = math.radians(rnd.uniform(30, 40))
        n = 11
        edge, tips = [], []
        sag = R * (0.22 if not down else 0.45) * (0.5 + abs(math.cos(ar)))
        for j in range(n + 1):
            t = j / n
            aa = ar - spread + 2 * spread * t
            rr = Rf * (1 if j % 2 == 0 else rnd.uniform(0.84, 0.92))
            ex, ey = px + rr * math.cos(aa), py + rr * math.sin(aa) * 0.8
            ey += (rr / Rf) ** 2 * sag
            edge.append((ex, ey))
            if j % 2 == 0 and rnd.random() < 0.7:        # split leaflet tips drooping off the fan edge
                tl = R * rnd.uniform(0.1, 0.2)
                tips.append(f'<path d="M {ex:.1f} {ey:.1f} q {math.cos(aa) * tl * 0.6:.1f} {tl * 0.2:.1f} {math.cos(aa) * tl * 0.8:.1f} {tl:.1f}"/>')
        side = math.cos(ar) * sun          # >0 -> frond points toward the sun
        if layer == 0:
            col = crown[0]
        elif layer == 1:
            col = crown[1] if side < -0.3 else crown[2]
        else:
            col = crown[2] if side < 0 else crown[3]
        fronds_svg = [f'<path d="M {tx:.1f} {ty:.1f} L {px:.1f} {py:.1f}" stroke="{crown[0]}" stroke-width="1.3"/>',
                      poly([(px, py)] + edge, col),
                      f'<g stroke="{col}" stroke-width="1.1" stroke-linecap="round">{"".join(tips)}</g>']
        # pleats radiating from the hastula
        for j in range(1, n, 2):
            ex, ey = edge[j]
            fronds_svg.append(f'<path d="M {px:.1f} {py:.1f} L {ex:.1f} {ey:.1f}" stroke="{crown[0]}" stroke-width="0.7" opacity="0.5"/>')
        if side > 0.1 and layer:
            k0 = 0 if sun < 0 else n - 4
            fronds_svg.append(poly([(px, py)] + edge[k0:k0 + 5], lit, ' opacity="0.7"'))
        out.append("".join(fronds_svg))
    # a few dates / dark heart in the crown centre
    out.append(f'<ellipse cx="{tx:.1f}" cy="{ty + 1:.1f}" rx="{R * 0.22:.1f}" ry="{R * 0.16:.1f}" fill="{crown[0]}"/>')
    return f'<g fill="none">{"".join(out)}</g>'


def ferris_wheel(cx, cy, R, deck):
    """The pier's Ferris wheel seen from the south: double rim with lattice ties, spokes, coloured gondolas, A-frame
    legs. Light from the left: cream lit edges on a steel-blue structure."""
    steel, steel_d, lit = "#6E8C9A", "#4E6C7C", "#FFF1DE"
    out = []
    # back legs (behind the wheel)
    for dx in (-0.46, 0.46):
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {cx + dx * R * 1.04:.1f} {deck:.1f}" stroke="{steel_d}" stroke-width="3" stroke-linecap="round" opacity="0.8"/>')
    # rear rim, a touch offset (depth)
    out.append(f'<circle cx="{cx + 3:.1f}" cy="{cy + 1:.1f}" r="{R:.1f}" fill="none" stroke="{steel_d}" stroke-width="1.6" opacity="0.55"/>')
    # spokes
    sp = []
    for i in range(24):
        a = math.radians(i * 15 + 4)
        sp.append(f'<path d="M {cx:.1f} {cy:.1f} L {cx + R * math.cos(a):.1f} {cy + R * math.sin(a):.1f}"/>')
    out.append(f'<g stroke="{steel}" stroke-width="1.2" opacity="0.9">{"".join(sp)}</g>')
    # lattice between the two front rims
    ties = []
    for i in range(72):
        a0, a1 = math.radians(i * 5), math.radians(i * 5 + 5)
        r0, r1 = (R, R - 5) if i % 2 == 0 else (R - 5, R)
        ties.append(f'<path d="M {cx + r0 * math.cos(a0):.1f} {cy + r0 * math.sin(a0):.1f} L {cx + r1 * math.cos(a1):.1f} {cy + r1 * math.sin(a1):.1f}"/>')
    out.append(f'<g stroke="{steel}" stroke-width="1.1">{"".join(ties)}</g>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="none" stroke="{steel}" stroke-width="2.6"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R - 5:.1f}" fill="none" stroke="{steel}" stroke-width="1.8"/>')
    # sun-lit arc on the left side of both rims
    for r, sw in ((R, 1.8), (R - 5, 1.2)):
        a0, a1 = math.radians(110), math.radians(250)
        out.append(f'<path d="M {cx + r * math.cos(a0):.1f} {cy + r * math.sin(a0):.1f} A {r:.1f} {r:.1f} 0 0 1 {cx + r * math.cos(a1):.1f} {cy + r * math.sin(a1):.1f}" '
                   f'fill="none" stroke="{lit}" stroke-width="{sw}" opacity="0.9"/>')
    # inner hub ring
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R * 0.2:.1f}" fill="none" stroke="{steel}" stroke-width="1.6"/>')
    # gondolas hanging from the rim
    cols = ["#FF7A59", "#F6C453", "#2E8FA6", "#F28CB1", "#FFD25E", "#C65F37", "#4F93A3", "#FF8A6E"]
    for i in range(20):
        a = math.radians(i * 18 + 9)
        gx, gy = cx + R * math.cos(a), cy + R * math.sin(a)
        c = cols[i % len(cols)]
        out.append(f'<path d="M {gx:.1f} {gy:.1f} L {gx:.1f} {gy + 3:.1f}" stroke="{steel_d}" stroke-width="1.2"/>'
                   f'<rect x="{gx - 3.6:.1f}" y="{gy + 3:.1f}" width="7.2" height="6.4" rx="1.6" fill="{c}"/>'
                   f'<rect x="{gx - 3.6:.1f}" y="{gy + 3:.1f}" width="2.4" height="6.4" rx="1" fill="#FFF1DE" opacity="0.5"/>'
                   f'<rect x="{gx - 3.6:.1f}" y="{gy + 3:.1f}" width="7.2" height="1.8" rx="0.9" fill="#FFF7EA" opacity="0.85"/>')
    # front A-frame legs and hub
    for dx in (-0.5, 0.5):
        x2 = cx + dx * R * 1.1
        out.append(f'<path d="M {cx:.1f} {cy:.1f} L {x2:.1f} {deck:.1f}" stroke="{steel}" stroke-width="3.6" stroke-linecap="round"/>')
        out.append(f'<path d="M {cx - 1:.1f} {cy:.1f} L {x2 - 1.2:.1f} {deck:.1f}" stroke="{lit}" stroke-width="1.2" opacity="0.8"/>')
    out.append(f'<path d="M {cx - R * 0.33:.1f} {cy + R * 0.66:.1f} L {cx + R * 0.33:.1f} {cy + R * 0.66:.1f}" stroke="{steel}" stroke-width="2"/>')
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.6" fill="{steel_d}"/><circle cx="{cx - 1.2:.1f}" cy="{cy - 1.2:.1f}" r="2" fill="{lit}" opacity="0.8"/>')
    return "".join(out)


def coaster(x0, x1, deck_at, profile, seed):
    """Steel family coaster beside the wheel: a rear loop of track, the front track over slim white supports and a
    little train cresting a hill. profile = [(x, y)] of the front track."""
    rnd = random.Random(seed)
    out = []
    back = [(x, y + 8) for x, y in rough([(x0 + 14, profile[0][1] - 6)] + [(x, y - 4) for x, y in profile[2:-1]] + [(x1 - 4, profile[-1][1] - 10)], seed, 3, 2)]
    sup = []
    for line, op in ((back, 0.55), (profile, 1.0)):
        x = line[0][0] + 3
        while x < line[-1][0] - 2:
            y = y_on(line, x)
            if y is not None:
                sup.append(f'<path d="M {x:.1f} {y + 2:.1f} L {x:.1f} {deck_at(x):.1f}" opacity="{op}"/>')
            x += 5 if op == 1 else 8
    out.append(f'<g stroke="#E9E2D4" stroke-width="1.6">{"".join(sup)}</g>')
    # cross bracing
    br = []
    x = profile[0][0] + 3
    while x < profile[-1][0] - 9:
        y = y_on(profile, x)
        y2 = y_on(profile, x + 7)
        if y is not None and y2 is not None and deck_at(x) - y > 14:
            br.append(f'<path d="M {x:.1f} {y + 4:.1f} L {x + 7:.1f} {deck_at(x + 7) - 2:.1f}"/>')
        x += 7
    out.append(f'<g stroke="#CFC6B6" stroke-width="0.9" opacity="0.8">{"".join(br)}</g>')
    # rear track
    out.append(f'<polyline points="{P(back)}" fill="none" stroke="#E6995F" stroke-width="2.4" stroke-linejoin="round" opacity="0.75"/>')
    # front track: rail pair (lit top rail, shaded lower rail)
    out.append(f'<polyline points="{P([(x, y + 2.2) for x, y in profile])}" fill="none" stroke="#C65F37" stroke-width="2.2" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{P(profile)}" fill="none" stroke="#FF7A59" stroke-width="2.8" stroke-linejoin="round"/>')
    out.append(f'<polyline points="{P([(x, y - 0.9) for x, y in profile])}" fill="none" stroke="#FFC9A8" stroke-width="0.9" stroke-linejoin="round" opacity="0.9"/>')
    return "".join(out)


def train(line, xs, cols):
    out = []
    for x, c in zip(xs, cols):
        y = y_on(line, x)
        y2 = y_on(line, x + 2)
        ang = math.degrees(math.atan2(y2 - y, 2))
        out.append(f'<g transform="translate({x:.1f} {y - 1.2:.1f}) rotate({ang:.1f})"><rect x="-4.2" y="-5.6" width="8.4" height="5.6" rx="1.4" fill="{c}"/>'
                   f'<rect x="-4.2" y="-5.6" width="8.4" height="1.6" rx="0.8" fill="#FFF1DE" opacity="0.6"/>'
                   f'<circle cx="-1" cy="-7.4" r="1.6" fill="#3A2A22"/><circle cx="2.2" cy="-7.2" r="1.5" fill="#5B4A33"/></g>')
    return "".join(out)


def lifeguard_tower(x, base, k):
    """Santa Monica style lifeguard tower: a pale-blue hut on four posts with a front ramp; light from the left."""
    s = k
    out = [f'<g transform="translate({x:.1f} {base:.1f}) scale({s:.3f})">',
           '<ellipse cx="26" cy="1" rx="40" ry="3.4" fill="#B97A50" opacity="0.35"/>',
           # posts and braces
           '<g stroke="#E8DCCB" stroke-width="3"><path d="M -14 0 L -14 -28 M 14 0 L 14 -28"/></g>',
           '<g stroke="#B9AE9E" stroke-width="2.4"><path d="M -9 0 L -9 -28 M 18 0 L 18 -28"/></g>',
           '<path d="M -14 -6 L 14 -24 M 14 -6 L -14 -24" stroke="#CFC4B2" stroke-width="1.6"/>',
           # ramp down to the sand (to the right)
           '<path d="M 18 -26 L 62 0 L 66 0 L 22 -26 Z" fill="#D9CDBA"/><path d="M 18 -26 L 62 0" stroke="#F7EEDF" stroke-width="1.6"/>',
           '<g stroke="#B9AE9E" stroke-width="1.2">' + "".join(f'<path d="M {22 + i * 6.6:.1f} {-23.5 + i * 3.9:.1f} L {26 + i * 6.6:.1f} {-23.5 + i * 3.9:.1f}"/>' for i in range(6)) + "</g>",
           '<path d="M 22 -34 L 62 -8" stroke="#F7EEDF" stroke-width="1.4"/><path d="M 62 -8 L 62 0" stroke="#F7EEDF" stroke-width="1.4"/>',
           # deck
           '<rect x="-22" y="-31" width="46" height="4" fill="#F4ECDD"/><rect x="-22" y="-28" width="46" height="1.6" fill="#B9AE9E"/>',
           # hut body: lit left face, shaded right face
           '<path d="M -18 -31 L -18 -56 L 16 -56 L 16 -31 Z" fill="#7FC0D2"/>',
           '<path d="M 6 -31 L 6 -56 L 16 -56 L 16 -31 Z" fill="#5E9DB2"/>',
           '<path d="M -18 -31 L -18 -56 L -13 -56 L -13 -31 Z" fill="#B8E4EC"/>',
           # window band and frame
           '<rect x="-15" y="-51" width="19" height="9" fill="#2E6F82"/><rect x="-15" y="-51" width="19" height="2" fill="#E9F6F6" opacity="0.6"/>',
           '<path d="M -8.5 -51 L -8.5 -42 M -2 -51 L -2 -42" stroke="#E9F6F6" stroke-width="1"/>',
           '<rect x="8" y="-50" width="5" height="8" fill="#3E7F92"/>',
           # roof
           '<path d="M -22 -56 L 20 -56 L 17 -61 L -19 -61 Z" fill="#F7EEDF"/><path d="M 2 -56 L 20 -56 L 17 -61 L 2 -61 Z" fill="#D9CDBA"/>',
           # rescue buoy, flag
           '<rect x="-21" y="-46" width="3.2" height="12" rx="1.4" fill="#FF7A59"/>',
           '<path d="M 18 -61 L 18 -78" stroke="#E8DCCB" stroke-width="1.6"/><path d="M 18 -78 L 29 -75 L 18 -71 Z" fill="#F6C453"/>',
           "</g>"]
    return "".join(out)


def pier_house(x, w, base, h, wall, roof, seed, lit_w=0.32, roof_h=None, cupola=False):
    rnd = random.Random(seed)
    roof_h = roof_h or h * 0.45
    out = [f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{wall}"/>',
           f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w * lit_w:.1f}" height="{h:.1f}" fill="#FFF1DE" opacity="0.45"/>',
           f'<rect x="{x + w * 0.8:.1f}" y="{base - h:.1f}" width="{w * 0.2:.1f}" height="{h:.1f}" fill="#B98E78" opacity="0.35"/>']
    out.append(poly([(x - 2, base - h), (x + w * 0.5, base - h - roof_h), (x + w + 2, base - h)], roof))
    out.append(poly([(x + w * 0.5, base - h - roof_h), (x + w + 2, base - h), (x + w * 0.5, base - h)], "#7E3B2C", ' opacity="0.35"'))
    # windows / arches
    n = max(1, int(w / 7))
    for i in range(n):
        wx = x + (i + 0.5) * w / n
        out.append(f'<rect x="{wx - 1.6:.1f}" y="{base - h * 0.62:.1f}" width="3.2" height="{h * 0.36:.1f}" rx="1.4" fill="#7E5A4A" opacity="0.75"/>')
    if cupola:
        cx = x + w * 0.5
        top = base - h - roof_h
        out.append(f'<rect x="{cx - 3:.1f}" y="{top - 6:.1f}" width="6" height="7" fill="{wall}"/><path d="M {cx - 4.5:.1f} {top - 6:.1f} L {cx:.1f} {top - 11:.1f} L {cx + 4.5:.1f} {top - 6:.1f} Z" fill="{roof}"/>')
    return "".join(out)


def umbrella(x, base, k):
    """Beach umbrella with coral and cream panels, lit from the left, a towel and its shadow on the sand."""
    out = [f'<g transform="translate({x:.1f} {base:.1f}) scale({k:.3f})">',
           '<path d="M -6 2 L 40 10 L 30 14 L -14 6 Z" fill="#B97A50" opacity="0.3"/>',
           '<path d="M -26 4 L 4 -2 L 18 6 L -12 12 Z" fill="#2E8FA6"/><path d="M -22 5 L 6 -0.5 M -18 8 L 10 2.5" stroke="#FFF1DE" stroke-width="1.6"/>',
           '<path d="M 2 4 L 6 -36" stroke="#F7EEDF" stroke-width="1.8"/>']
    cx, cy, r = 6, -34, 24
    cols = ["#FF7A59", "#FFF1DE"]
    can = [f'<g transform="rotate(-12 {cx} {cy})">']
    n = 8
    rim = [(cx + r * math.cos(math.pi * i / n), cy + 0.28 * r * math.sin(math.pi * i / n)) for i in range(n + 1)][::-1]
    apex = (cx, cy - 13)
    for i in range(n):
        p0, p1 = rim[i], rim[i + 1]
        c = cols[i % 2]
        can.append(f'<path d="M {apex[0]} {apex[1]} L {p0[0]:.1f} {p0[1]:.1f} Q {(p0[0] + p1[0]) / 2:.1f} {(p0[1] + p1[1]) / 2 + 3.2:.1f} {p1[0]:.1f} {p1[1]:.1f} Z" fill="{c}"/>')
    # shade on the far (right) half of the cone, light along the left
    can.append(f'<path d="M {apex[0]} {apex[1]} L {rim[n // 2 + 1][0]:.1f} {rim[n // 2 + 1][1]:.1f} L {cx + r:.1f} {cy:.1f} Z" fill="#7E3B2C" opacity="0.2"/>')
    can.append(f'<path d="M {apex[0]} {apex[1]} L {cx - r:.1f} {cy:.1f}" stroke="#FFF7EA" stroke-width="1.4" opacity="0.85"/>')
    can.append(f'<circle cx="{apex[0]}" cy="{apex[1] - 1}" r="1.8" fill="#C65F37"/></g>')
    out += can
    out.append("</g>")
    return "".join(out)


# ---------------------------------------------------------------- the scene
def los_angeles():
    u = U
    out = [defs(
        lg(f"{u}-sky", [(0, "#6FBCCF"), (0.24, "#A4D6DE"), (0.46, "#E2E4CC"), (0.66, "#F9E2B8"), (0.85, "#F9D6AA"), (1, "#F6C49C")], 0, 40, 0, HZ, units="userSpaceOnUse"),
        lg(f"{u}-far", [(0, "#9DB7C2"), (0.6, "#BFCBC6"), (1, "#E9CFB4")], 0, 180, 0, HZ, units="userSpaceOnUse"),
        lg(f"{u}-mid", [(0, "#7C9B8E"), (1, "#AEB89A")], 0, 205, 0, HZ + 4, units="userSpaceOnUse"),
        lg(f"{u}-sea", [(0, "#E4D9C2"), (0.08, "#A9D2D2"), (0.35, "#4F9DB0"), (0.7, "#2E8FA6"), (1, "#56B2BC")], 0, HZ, 0, 352, units="userSpaceOnUse"),
        lg(f"{u}-wet", [(0, "#E6D3BE"), (1, "#EFC9A4")]),
        lg(f"{u}-sand", [(0, "#F6D6A4"), (0.45, "#F0C796"), (1, "#E3A877")], 0, 330, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-path", [(0, "#E6D9C8"), (1, "#D4C3AE")], 0, 370, 0, 444, units="userSpaceOnUse"),
        lg(f"{u}-glit", [(0, "#FFE7A6", 0.0), (0.5, "#FFE7A6", 0.9), (1, "#FFE7A6", 0.0)], 0, 0, 1, 0),
    )]
    out.append(f'<rect width="600" height="444" fill="url(#{u}-sky)"/>')
    # warm wash of light around the low sun
    out.append(glow(SUN[0], SUN[1], 300, "#FFD9A0", f"{u}-wash", 0.55))
    out.append(glow(SUN[0], SUN[1], 90, "#FFE2A0", f"{u}-halo", 0.75))
    out.append(f'<circle cx="{SUN[0]}" cy="{SUN[1]}" r="22" fill="#F6C453"/>'
               f'<circle cx="{SUN[0] - 1.5}" cy="{SUN[1] - 1.5}" r="18" fill="#FFD25E"/>'
               f'<circle cx="{SUN[0] - 5}" cy="{SUN[1] - 5}" r="9" fill="#FFE9A8" opacity="0.85"/>')
    # golden-hour clouds, lit from the sun side
    out.append(streak_cloud(300, 104, 210, 15, 3, op=0.95))
    out.append(streak_cloud(498, 148, 150, 11, 4, op=0.9))
    out.append(streak_cloud(150, 150, 120, 9, 5, body="#F9D2A8", op=0.85))
    out.append(streak_cloud(430, 196, 110, 7, 6, body="#F7D3B0", lit="#FFF4E6", op=0.8))
    out.append(streak_cloud(40, 184, 90, 7, 7, body="#F9D6AC", op=0.8))

    # Santa Monica Mountains: far range, highest to the right, falling toward the Malibu coast on the left
    far = rough([(-10, 250), (40, 244), (90, 246), (150, 236), (205, 230), (250, 218), (300, 222), (350, 206), (400, 212),
                 (450, 196), (500, 202), (560, 188), (610, 194)], 21, 7, 4)
    out.append(poly(far + [(610, HZ + 2), (-10, HZ + 2)], f"url(#{u}-far)"))
    cid = f"{u}-farc"
    g = []
    rnd = random.Random(22)
    peaks = [far[i] for i in range(1, len(far) - 1) if far[i][1] < far[i - 1][1] and far[i][1] < far[i + 1][1] and 0 < far[i][0] < 610]
    for px_, py_ in peaks:
        if (HZ - py_) < 24:
            continue
        # shadow side of each spur, away from the low western sun, folding down to the right
        d = (HZ - py_)
        ex = px_ + d * rnd.uniform(1.0, 1.5)
        g.append(f'<path d="M {px_:.1f} {py_:.1f} Q {px_ + d * 0.35:.1f} {py_ + d * 0.45:.1f} {ex:.1f} {HZ + 4} L {px_ + d * 0.2:.1f} {HZ + 4} Q {px_ + d * 0.12:.1f} {py_ + d * 0.5:.1f} {px_:.1f} {py_:.1f} Z" fill="#8FA7B2" opacity="0.3"/>')
        g.append(f'<path d="M {px_ - 1:.1f} {py_ + 1:.1f} q {-d * 0.2:.1f} {d * 0.4:.1f} {-d * 0.5:.1f} {d * 0.8:.1f}" stroke="#F8E2C4" stroke-width="1.6" opacity="0.45"/>')
    out.append(f'<clipPath id="{cid}"><polygon points="{P(far + [(610, HZ + 2), (-10, HZ + 2)])}"/></clipPath><g clip-path="url(#{cid})" fill="none">' + "".join(g) + "</g>")
    out.append(f'<polyline points="{P(far)}" fill="none" stroke="#FBE6CB" stroke-width="1.4" opacity="0.7"/>')
    # nearer foothills / Pacific Palisades bluffs on the right reaching down to the sea
    mid = rough([(180, HZ + 1), (240, 258), (300, 250), (360, 242), (420, 238), (480, 230), (540, 234), (610, 226)], 31, 5, 4)
    out.append(poly(mid + [(610, HZ + 4), (180, HZ + 4)], f"url(#{u}-mid)"))
    out.append(f'<polyline points="{P(mid[:24])}" fill="none" stroke="#E9DDBA" stroke-width="1.4" opacity="0.6"/>')
    rnd = random.Random(32)
    out.append("".join(f'<ellipse cx="{(xx := rnd.uniform(220, 610)):.1f}" cy="{(y_on(mid, xx) or HZ) + rnd.uniform(3, 12):.1f}" rx="{rnd.uniform(2, 5):.1f}" ry="{rnd.uniform(1.2, 2.4):.1f}" '
                       f'fill="{rnd.choice(["#7A9A88", "#6F8E7E", "#9AAE96"])}" opacity="0.8"/>' for _ in range(70)))
    out.append("".join(f'<rect x="{(xx := rnd.uniform(380, 600)):.1f}" y="{HZ - rnd.uniform(5, 12):.1f}" width="{rnd.uniform(2, 4):.1f}" height="{rnd.uniform(1.6, 3):.1f}" fill="#F4E8D8" opacity="0.8"/>' for _ in range(26)))
    out.append(mist(300, HZ - 2, 420, 14, "#F7E2C6", f"{u}-hz", 0.7))

    # the Pacific
    out.append(f'<rect x="-10" y="{HZ}" width="620" height="100" fill="url(#{u}-sea)"/>')
    rnd = random.Random(41)
    sw = []
    for _ in range(140):
        y = rnd.uniform(HZ + 3, 350)
        d = (y - HZ) / 80
        sw.append(f'<rect x="{rnd.uniform(-10, 600):.1f}" y="{y:.1f}" width="{rnd.uniform(6, 22) * (0.4 + d * 1.6):.1f}" height="{0.9 + d * 0.9:.1f}" rx="0.6" '
                  f'fill="{rnd.choice(["#CFEDEC", "#A9DBE6", "#FFF1DE"])}" opacity="{rnd.uniform(0.25, 0.6):.2f}"/>')
    out.append("".join(sw))
    out.append(blobs(16, 42, (0, 300, 600, 340), ["#2E8FA6", "#3E8C9C"], r=(18, 40), opacity=(0.18, 0.3), squash=0.16))
    # sun glitter path
    rnd = random.Random(43)
    gl = []
    y = HZ + 1
    while y < 352:
        d = (y - HZ) / 86
        half = 8 + d * 34
        for _ in range(2 + int(d * 4)):
            ww = rnd.uniform(3, 10) * (0.5 + d)
            gl.append(f'<rect x="{SUN[0] + rnd.uniform(-half, half) - ww / 2:.1f}" y="{y:.1f}" width="{ww:.1f}" height="{1 + d:.1f}" rx="0.6" fill="{rnd.choice(["#FFE7A6", "#FFF4D6", "#FFD25E"])}" opacity="{rnd.uniform(0.55, 0.95):.2f}"/>')
        y += rnd.uniform(1.8, 3.6) * (0.6 + d)
    out.append("".join(gl))
    out.append(f'<ellipse cx="{SUN[0]}" cy="{HZ + 3}" rx="60" ry="3" fill="#FFE7A6" opacity="0.7"/>')

    # ---------------- the pier
    xl, xr, yl, yr = 150, 640, 279, 301

    def deck(x):
        return yl + (yr - yl) * (x - xl) / (xr - xl)

    def thick(x):
        t = (x - xl) / (xr - xl)
        return 3.2 + 5.5 * t

    def shore(x):
        return 352 - 0.048 * x

    def water(x):
        t = (x - xl) / (xr - xl)
        return min(deck(x) + thick(x) + 8 + 24 * t, shore(x) + 1)

    # pilings (bents), back row hazier, with reflections
    pil, refl = [], []
    x = xl + 2
    while x < 612:
        t = (x - xl) / (xr - xl)
        y0, y1 = deck(x) + thick(x), water(x)
        w = 1.2 + 1.6 * t
        pil.append(f'<rect x="{x + 2 + 2 * t:.1f}" y="{y0:.1f}" width="{w * 0.8:.1f}" height="{y1 - y0:.1f}" fill="#8E7462" opacity="0.65"/>')
        pil.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{y1 - y0:.1f}" fill="#6A5040"/>')
        pil.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{w * 0.4:.1f}" height="{y1 - y0:.1f}" fill="#E2B58A" opacity="0.8"/>')
        if y1 < shore(x) - 2:
            refl.append(f'<path d="M {x + w / 2:.1f} {y1 + 1:.1f} q 1.5 {(4 + 8 * t):.1f} -0.5 {(8 + 14 * t):.1f}" stroke="#4E6C70" stroke-width="{w * 0.8:.1f}" opacity="0.35"/>')
        x += 6 + 10 * t
    # cross bracing between bents
    br = []
    x = xl + 2
    while x < 600:
        t = (x - xl) / (xr - xl)
        step = 6 + 10 * t
        y0, y1 = deck(x) + thick(x), water(x)
        br.append(f'<path d="M {x:.1f} {y0 + 1:.1f} L {x + step:.1f} {y0 + (y1 - y0) * 0.6:.1f} M {x + step:.1f} {y0 + 1:.1f} L {x:.1f} {y0 + (y1 - y0) * 0.6:.1f}"/>')
        x += step
    out.append(f'<g fill="none">{"".join(refl)}</g>')
    out.append(f'<g stroke="#7A604E" stroke-width="0.9" opacity="0.55" fill="none">{"".join(br)}</g>')
    out.append("".join(pil))

    # buildings along the pier (carousel house near the shore, arcades, the little cafe at the far end)
    out.append(pier_house(158, 22, deck(169), 9, "#F7E1C8", "#C65F37", 1, roof_h=4))
    out.append(pier_house(470, 26, deck(483), 15, "#F9DDB0", "#C65F37", 3, roof_h=6))
    out.append(pier_house(530, 54, deck(557), 22, "#FFF1DE", "#C65F37", 4, roof_h=11, cupola=True))
    out.append(pier_house(500, 24, deck(512), 12, "#F6CBA4", "#B5573A", 5, roof_h=5))

    # coaster and wheel
    def deck_top(x):
        return deck(x)
    prof = [(366, deck(366) - 3), (378, 262), (392, 232), (398, 229), (404, 233), (420, 268), (430, 274), (442, 252), (452, 246), (462, 252),
            (476, 270), (486, 264), (496, 258), (506, 262), (516, 276), (526, deck(526) - 4)]
    # smooth the profile
    sm = []
    for (x1, y1), (x2, y2) in zip(prof, prof[1:]):
        for i in range(6):
            t = i / 6
            sm.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * (3 * t * t - 2 * t * t * t)))
    sm.append(prof[-1])
    out.append(coaster(366, 526, deck_top, sm, 7))
    out.append(train(sm, [446, 455, 464, 473], ["#F6C453", "#2E8FA6", "#FF7A59", "#F6C453"]))
    WX, WY, WR = 316, 206, 66
    out.append(ferris_wheel(WX, WY, WR, deck(WX) - 1))

    # deck slab, railing, lamps, tiny strollers
    top = [(x, deck(x)) for x in (xl, 640)]
    out.append(poly([(xl, deck(xl)), (640, deck(640)), (640, deck(640) + thick(640)), (xl, deck(xl) + thick(xl))], "#8A6A55"))
    out.append(poly([(xl, deck(xl)), (640, deck(640)), (640, deck(640) + 2.2), (xl, deck(xl) + 1.2)], "#F2D3AE"))
    out.append(f'<path d="M {xl} {deck(xl) - 3:.1f} L 640 {deck(640) - 6:.1f}" stroke="#F7EEDF" stroke-width="1.3" opacity="0.9"/>')
    rail = []
    x = xl + 3
    while x < 600:
        t = (x - xl) / (xr - xl)
        rail.append(f'<path d="M {x:.1f} {deck(x):.1f} L {x:.1f} {deck(x) - 3 - 3 * t:.1f}"/>')
        x += 4 + 6 * t
    out.append(f'<g stroke="#F7EEDF" stroke-width="0.9" opacity="0.8">{"".join(rail)}</g>')
    for x in (190, 232, 274, 360, 440, 520):
        t = (x - xl) / (xr - xl)
        hh = 9 + 10 * t
        out.append(f'<path d="M {x} {deck(x):.1f} L {x} {deck(x) - hh:.1f}" stroke="#4E6C7C" stroke-width="1.4"/><circle cx="{x}" cy="{deck(x) - hh:.1f}" r="{1.4 + t:.1f}" fill="#FFF4D6"/>')
    rnd = random.Random(61)
    for x in (200, 214, 222, 246, 258, 288, 298, 352, 420, 436):
        t = (x - xl) / (xr - xl)
        out.append(F.person(x, deck(x) - 0.5, 8 + 7 * t, "tiny", rnd.choice([1, -1]), None, seed=x, rim="#FFE2B0", light=-1, shadow=0))

    # shoreline: surf, wet sand mirror, dry sand
    shore_pts = [(x, shore(x) + 2 * math.sin(x / 37)) for x in range(-10, 621, 10)]
    out.append(poly(shore_pts + [(610, 444), (-10, 444)], f"url(#{u}-wet)"))
    # sun reflection on the wet sand
    out.append(f'<ellipse cx="{SUN[0] + 14}" cy="{shore(SUN[0]) + 7}" rx="46" ry="5" fill="#FFE7A6" opacity="0.6"/>')
    rnd = random.Random(71)
    foam = []
    for k, (dy, sw_, op) in enumerate(((-12, 2.2, 0.75), (-4, 2.8, 0.95), (1, 1.6, 0.7))):
        pts = [(x, y + dy + rnd.uniform(-1, 1)) for x, y in shore_pts]
        d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        out.append(f'<path d="{d}" fill="none" stroke="#FFFDF6" stroke-width="{sw_}" stroke-linecap="round" stroke-dasharray="{rnd.randint(30, 60)} {rnd.randint(6, 18)}" opacity="{op}"/>')
    out.append(dots(60, 72, (-10, 322, 600, 346), "#FFFFFF", r=(0.6, 1.6), opacity=(0.4, 0.9)))

    dry = [(x, shore(x) + 12 + 3 * math.sin(x / 53 + 1)) for x in range(-10, 621, 10)]
    out.append(poly(dry + [(610, 444), (-10, 444)], f"url(#{u}-sand)"))
    # wind ripples and footprints on the sand
    rnd = random.Random(73)
    rip = []
    for _ in range(70):
        x = rnd.uniform(-10, 600)
        y = rnd.uniform(dry[0][1] + 6, 444)
        L = rnd.uniform(8, 22) * (0.6 + (y - 350) / 100)
        rip.append(f'<path d="M {x:.1f} {y:.1f} q {L / 2:.1f} {-2:.1f} {L:.1f} 0" stroke="{rnd.choice(["#E2B482", "#FFF1DE"])}" stroke-width="1.2" opacity="{rnd.uniform(0.35, 0.7):.2f}"/>')
    out.append(f'<g fill="none" stroke-linecap="round">{"".join(rip)}</g>')
    out.append(dots(220, 74, (-10, 360, 610, 444), "#C99A6A", r=(0.5, 1.3), opacity=(0.3, 0.7)))

    # long shadows of the palms reaching to the right across the sand
    for bx, by in ((500, 400), (540, 446), (586, 424)):
        out.append(poly([(bx - 3, by), (bx + 3, by), (bx + 150, by + 60), (bx + 138, by + 62)], "#C88E60", ' opacity="0.28"'))
    # a striped beach umbrella and towel halfway down the sand
    out.append(umbrella(132, 378, 1.0))

    # beach bike path sweeping across the foreground
    def path_c(x):
        return 430 - 0.075 * (x + 10) + 10 * math.sin((x + 10) / 190)

    def path_w(x):
        return 30 - 0.022 * (x + 10)
    up = [(x, path_c(x) - path_w(x) / 2) for x in range(-10, 621, 10)]
    lo = [(x, path_c(x) + path_w(x) / 2) for x in range(-10, 621, 10)]
    out.append(poly([(x, y + 2.5) for x, y in up] + lo[::-1], "#C9A47C", ' opacity="0.5"'))
    out.append(poly(up + lo[::-1], f"url(#{u}-path)"))
    out.append(f'<polyline points="{P(up)}" fill="none" stroke="#FFF7EA" stroke-width="1.4" opacity="0.8"/>')
    out.append(f'<polyline points="{P([(x, y + 1) for x, y in lo])}" fill="none" stroke="#B8987A" stroke-width="1.4" opacity="0.6"/>')
    cl = [(x, path_c(x)) for x in range(-10, 621, 4)]
    out.append(f'<polyline points="{P(cl)}" fill="none" stroke="#F6C453" stroke-width="1.8" stroke-dasharray="9 7"/>')
    out.append(dots(60, 75, (-10, 380, 610, 440), "#F2CFA0", r=(0.6, 1.4), opacity=(0.4, 0.8)))

    # lifeguard tower near the water
    out.append(lifeguard_tower(214, 358, 0.86))

    # a couple walking along the water's edge, and a jogger
    out.append(F.person(438, 343, 30, "couple", 1, {"season": "beach"}, seed=88, rim="#FFE2B0", light=-1, shadow=0.18))
    out.append(F.person(78, 352, 26, "jog", -1, {"season": "beach", "top": "#FF7A59"}, seed=91, rim="#FFE2B0", light=-1, shadow=0.18))

    # cyclist on the bike path, riding toward the sun
    cx_ = 330
    out.append(poly([(cx_ - 18, path_c(cx_) + 4), (cx_ + 18, path_c(cx_) + 4), (cx_ + 70, path_c(cx_) + 16), (cx_ + 36, path_c(cx_) + 16)], "#A88464", ' opacity="0.35"'))
    out.append(F.person(cx_, path_c(cx_) + 4, 60, "cyclist", -1, {"top": "#2E8FA6", "top_kind": "tee", "bottom_kind": "shorts", "bottom": "#3A2A22",
                                                              "hair_style": "ponytail", "form": "f", "accent": "#FF7A59", "skin": "#B87A52", "hair": "#2E1E16"},
                        seed=330, rim="#FFE2B0", light=-1, shadow=0))

    # tall fan palms: the right-hand grove that frames the pier, one more on the left
    out.append(fan_palm(48, 432, 262, 101, lean=0.05, crown=("#4A6E43", "#5E8A52", "#6F9A55", "#86A46A")))
    out.append(fan_palm(586, 424, 318, 102, lean=-0.03))
    out.append(fan_palm(540, 446, 352, 103, lean=0.02))
    out.append(fan_palm(500, 400, 208, 104, lean=-0.04, crown=("#577A4E", "#6F9070", "#7C9B74", "#94AE84"), lit="#D6D29A"))

    # gulls
    out.append('<g fill="none" stroke="#5B4A33" stroke-width="1.8" stroke-linecap="round">'
               '<path d="M 214 132 q 6 -5 12 0 q 6 -5 12 0"/><path d="M 246 150 q 4 -3.5 8 0 q 4 -3.5 8 0"/><path d="M 420 118 q 3.5 -3 7 0 q 3.5 -3 7 0"/></g>')
    return "\n".join(out)


BUILD = {
    "los-angeles": (los_angeles, "LOS ANGELES", "CALIFORNIA · USA", "#F4D4CE", "#DE958A", "#4E2A2A", "#A04A44"),
}


def build(out_dir=OUT):
    out_dir.mkdir(parents=True, exist_ok=True)

    def save(collection, slug, body):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600">\n' + body.strip() + "\n</svg>\n"
        (out_dir / f"{slug}.svg").write_text(svg, encoding="utf-8")

    PST.save = save
    for slug, (fn, name, sub, band, rule, namec, subc) in BUILD.items():
        PST.poster("places", slug, name, sub, fn(), band, rule, namec, subc)


if __name__ == "__main__":
    build(pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else OUT)
