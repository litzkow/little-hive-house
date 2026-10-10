"""Night Sky (zodiac constellations) and Birth Flowers (flower of the month) — the second half of each set."""
import math
from common import save, text, CINZEL, MONO, SERIF_IT

# ---------------------------------------------------------------- Night Sky
BG_STARS = [(60, 80, 1.6), (130, 58, 1.1), (210, 22, 1.2), (300, 28, 1.3), (470, 30, 1.1), (522, 72, 1.7),
            (562, 150, 1.2), (76, 206, 1.3), (42, 320, 1.7), (562, 300, 1.4), (526, 420, 1.2), (88, 432, 1.5),
            (40, 540, 1.4), (170, 566, 1.2), (432, 572, 1.4), (562, 520, 1.2)]


def sky(slug, name, dates, lines, stars, bright):
    bg = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in BG_STARS)
    poly = "\n".join('<polyline points="' + " ".join(f"{x},{y}" for x, y in ln) + '"/>' for ln in lines)
    st = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in stars)
    bx, by = bright
    size = 54 if len(name) <= 6 else 50 if len(name) <= 8 else 46
    ls = 12 if len(name) <= 8 else 10
    body = f"""
<rect width="600" height="600" fill="#0E1116"/>
<g fill="#F4F0E8" opacity="0.55">{bg}</g>
<circle cx="300" cy="235" r="190" fill="none" stroke="#D9B26A" stroke-width="1.5" opacity="0.6"/>
<circle cx="300" cy="235" r="178" fill="none" stroke="#D9B26A" stroke-width="1" opacity="0.4" stroke-dasharray="2 8"/>
<g fill="none" stroke="#F4F0E8" stroke-opacity="0.55" stroke-width="2" stroke-linejoin="round">
{poly}
</g>
<circle cx="{bx}" cy="{by}" r="17" fill="#D9B26A" opacity="0.22"/>
<g fill="#F4F0E8">{st}</g>
{text(300, 488, name, CINZEL, size, "#D9B26A", ls=ls)}
<text x="300" y="534" text-anchor="middle" {MONO} font-size="18" letter-spacing="4" fill="#F4F0E8" opacity="0.8">{dates}</text>
"""
    save("night-sky", slug, body)


def build_sky():
    sky("cancer", "CANCER", "JUN 21 – JUL 22",
        [[(240, 140), (300, 240), (370, 170)], [(300, 240), (300, 300), (265, 375)]],
        [(240, 140, 5), (300, 240, 5), (370, 170, 4.5), (300, 300, 4), (265, 375, 6.5)], (265, 375))
    sky("virgo", "VIRGO", "AUG 23 – SEP 22",
        [[(180, 140), (220, 200), (270, 230), (300, 290), (330, 360)], [(270, 230), (330, 200), (390, 150)],
         [(300, 290), (380, 300), (430, 280)], [(330, 200), (350, 250), (300, 290)]],
        [(180, 140, 4), (220, 200, 4.5), (270, 230, 5), (300, 290, 5), (330, 360, 7.5), (330, 200, 4.5),
         (390, 150, 4), (380, 300, 4.5), (430, 280, 4), (350, 250, 4)], (330, 360))
    sky("libra", "LIBRA", "SEP 23 – OCT 22",
        [[(240, 200), (320, 150), (380, 230), (300, 280), (240, 200)], [(240, 200), (200, 300), (215, 345)],
         [(380, 230), (400, 330)]],
        [(240, 200, 5.5), (320, 150, 7), (380, 230, 5), (300, 280, 4.5), (200, 300, 4), (215, 345, 4), (400, 330, 4.5)],
        (320, 150))
    sky("capricorn", "CAPRICORN", "DEC 22 – JAN 19",
        [[(170, 170), (250, 230), (380, 170), (430, 190), (350, 310), (260, 320), (200, 260), (170, 170)]],
        [(170, 170, 5.5), (250, 230, 4), (380, 170, 4.5), (430, 190, 7), (350, 310, 4.5), (260, 320, 4.5), (200, 260, 4)],
        (430, 190))
    sky("aquarius", "AQUARIUS", "JAN 20 – FEB 18",
        [[(150, 150), (220, 190), (280, 170), (330, 230), (300, 290), (350, 330), (420, 300)],
         [(280, 170), (300, 120), (355, 110)]],
        [(150, 150, 4), (220, 190, 4.5), (280, 170, 7), (330, 230, 4.5), (300, 290, 4), (350, 330, 4.5),
         (420, 300, 4), (300, 120, 5), (355, 110, 4)], (280, 170))
    sky("pisces", "PISCES", "FEB 19 – MAR 20",
        [[(170, 140), (195, 155), (205, 180), (185, 195), (160, 185), (150, 160), (170, 140)],
         [(205, 180), (300, 270), (400, 360)], [(400, 360), (440, 240), (430, 140)],
         [(430, 140), (455, 115), (415, 105), (430, 140)]],
        [(170, 140, 3.5), (195, 155, 3.5), (205, 180, 4), (185, 195, 3.5), (160, 185, 3.5), (150, 160, 3.5),
         (300, 270, 4.5), (400, 360, 7), (440, 240, 4.5), (430, 140, 4), (455, 115, 3.5), (415, 105, 3.5)],
        (400, 360))


# ---------------------------------------------------------------- Birth Flowers
INK = "#222222"
ARCH_FILL = "#F1ECE2"


def flower(slug, month, name, art):
    body = f"""
<rect width="600" height="600" fill="#FAF8F3"/>
<path d="M 120 470 L 120 230 A 180 180 0 0 1 480 230 L 480 470 Z" fill="{ARCH_FILL}" stroke="{INK}" stroke-width="2.5"/>
{art}
{text(300, 530, month, SERIF_IT, 50, INK)}
{text(300, 566, name.upper(), MONO, 16, INK, ls=6)}
"""
    save("birth-flowers", slug, body)


def line_group(paths, sw=3):
    return (f'<g fill="none" stroke="{INK}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">\n'
            + "\n".join(paths) + "\n</g>")


def petal_ring(cx, cy, n, dist, rx, ry, offset=0, sw=2.5):
    out = [f'<g fill="{ARCH_FILL}" stroke="{INK}" stroke-width="{sw}">']
    for k in range(n):
        a = offset + k * 360 / n
        out.append(f'<ellipse cx="{cx}" cy="{cy - dist}" rx="{rx}" ry="{ry}" transform="rotate({a:g} {cx} {cy})"/>')
    out.append("</g>")
    return "\n".join(out)


def pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def carnation():
    cx, cy = 300, 222
    pts = []
    n = 22
    for i in range(n + 1):
        deg = 195 + i * 150 / n
        r = 80 if i % 2 == 0 else 63
        pts.append(pt(cx, cy, r, deg))
    crown = "M 284 254 " + " ".join(f"L {x:.1f} {y:.1f}" for x, y in pts) + " L 316 254 Z"
    inner = []
    for i in range(15):
        deg = 212 + i * 116 / 14
        r = 52 if i % 2 == 0 else 40
        inner.append(pt(cx, cy, r, deg))
    inner_d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in inner)
    return "\n".join([
        line_group(['<path d="M 300 300 Q 296 390 300 466"/>',
                    '<path d="M 299 372 Q 256 352 236 318"/>',
                    '<path d="M 300 412 Q 346 394 368 360"/>',
                    '<path d="M 300 440 Q 268 432 250 410"/>']),
        f'<path d="{crown}" fill="{ARCH_FILL}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>',
        f'<path d="{inner_d}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>',
        f'<path d="M 282 252 L 289 300 L 311 300 L 318 252 Z" fill="{ARCH_FILL}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>',
        line_group(['<path d="M 292 262 L 296 296"/>', '<path d="M 308 262 L 304 296"/>'], 1.5),
    ])


def violet():
    cx, cy = 300, 220
    petals = [(-36, 26, 36), (36, 26, 36), (-110, 24, 32), (110, 24, 32), (180, 34, 30)]
    out = [line_group(['<path d="M 300 250 Q 310 360 300 466"/>',
                       '<path d="M 300 420 Q 240 410 228 380 Q 226 360 246 362 Q 262 352 272 372 Q 284 396 300 420 Z"/>',
                       '<path d="M 302 440 Q 362 430 374 400 Q 376 380 356 382 Q 340 372 330 392 Q 318 416 302 440 Z"/>'])]
    out.append(f'<g fill="{ARCH_FILL}" stroke="{INK}" stroke-width="3">')
    for deg, rx, ry in petals:
        out.append(f'<ellipse cx="{cx}" cy="{cy - ry - 2}" rx="{rx}" ry="{ry}" transform="rotate({deg} {cx} {cy})"/>')
    out.append("</g>")
    out.append(line_group(['<line x1="300" y1="232" x2="300" y2="262"/>', '<line x1="294" y1="232" x2="286" y2="258"/>',
                           '<line x1="306" y1="232" x2="314" y2="258"/>'], 1.5))
    out.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="{INK}"/>')
    return "\n".join(out)


def larkspur():
    out = [line_group(['<path d="M 300 466 Q 296 300 300 112"/>',
                       '<path d="M 300 446 Q 252 430 232 404"/>', '<path d="M 268 432 Q 262 412 248 398"/>',
                       '<path d="M 300 430 Q 346 414 366 388"/>', '<path d="M 332 418 Q 340 400 352 390"/>'])]
    florets = [(384, -1, 13), (352, 1, 13), (322, -1, 12), (293, 1, 12), (266, -1, 11), (240, 1, 10),
               (216, -1, 9), (194, 1, 8), (174, -1, 7)]
    for y, side, s in florets:
        fx = 300 + side * (14 + s * 0.9)
        out.append(line_group([f'<line x1="300" y1="{y + 6}" x2="{fx:.1f}" y2="{y}"/>'], 2))
        out.append(petal_ring(round(fx, 1), y, 5, s * 0.9, round(s * 0.45, 1), s, offset=side * 18, sw=2))
        out.append(f'<circle cx="{fx:.1f}" cy="{y}" r="{max(2.5, s * 0.25):.1f}" fill="{INK}"/>')
    out.append(f'<g fill="{ARCH_FILL}" stroke="{INK}" stroke-width="2">'
               '<ellipse cx="305" cy="156" rx="4" ry="6"/><ellipse cx="296" cy="142" rx="4" ry="6"/>'
               '<ellipse cx="303" cy="128" rx="3.5" ry="5"/><ellipse cx="300" cy="114" rx="3" ry="4.5"/></g>')
    return "\n".join(out)


def poppy():
    out = [line_group(['<path d="M 300 278 Q 280 370 300 466"/>',
                       '<path d="M 294 380 Q 350 350 360 300"/>',
                       '<path d="M 296 430 Q 250 420 236 392 L 250 396 L 244 380 L 260 388 L 262 374 Q 280 400 296 420"/>'])]
    out.append(f'<g fill="{ARCH_FILL}" stroke="{INK}" stroke-width="3">'
               '<circle cx="252" cy="194" r="54"/><circle cx="348" cy="194" r="54"/>'
               '<circle cx="270" cy="238" r="56"/><circle cx="330" cy="238" r="56"/>'
               '<ellipse cx="360" cy="286" rx="11" ry="16" transform="rotate(20 360 286)"/></g>')
    out.append(line_group(['<path d="M 250 252 Q 262 262 278 258"/>', '<path d="M 350 252 Q 338 262 322 258"/>'], 2))
    rays = []
    for k in range(14):
        x1, y1 = pt(300, 216, 22, k * 360 / 14)
        x2, y2 = pt(300, 216, 32, k * 360 / 14)
        rays.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
    out.append(line_group(rays, 2.5))
    out.append(f'<circle cx="300" cy="216" r="17" fill="{INK}"/>')
    return "\n".join(out)


def chrysanthemum():
    out = [line_group(['<path d="M 300 272 Q 304 370 300 466"/>',
                       '<path d="M 300 404 Q 270 380 250 390 Q 236 372 222 380 Q 228 400 250 404 Q 270 412 300 404"/>',
                       '<path d="M 302 434 Q 330 414 350 422 Q 362 404 378 410 Q 372 430 350 434 Q 330 440 302 434"/>'])]
    out.append(petal_ring(300, 220, 20, 46, 7, 24))
    out.append(petal_ring(300, 220, 16, 30, 6, 18, offset=11))
    out.append(petal_ring(300, 220, 10, 15, 5, 11, offset=18))
    out.append(f'<circle cx="300" cy="220" r="6" fill="{INK}"/>')
    return "\n".join(out)


def holly_leaf(bx, by, deg, length=146, width=38):
    a = math.radians(deg)
    d = (math.cos(a), math.sin(a))
    n = (-math.sin(a), math.cos(a))
    steps = 6

    def p(t, side, f):
        w = width * (math.sin(math.pi * t) ** 0.8) * f
        return bx + d[0] * length * t + n[0] * w * side, by + d[1] * length * t + n[1] * w * side

    right, left = [], []
    for i in range(1, steps):
        right += [p(i / steps, 1, 1.18), p((i + 0.5) / steps, 1, 0.72)]
        left += [p(i / steps, -1, 1.18), p((i + 0.5) / steps, -1, 0.72)]
    tip = (bx + d[0] * length, by + d[1] * length)
    pts = [(bx, by)] + right + [tip] + left[::-1]
    dd = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    rib = f'<line x1="{bx}" y1="{by}" x2="{tip[0]:.1f}" y2="{tip[1]:.1f}"/>'
    return f'<path d="{dd}" fill="{ARCH_FILL}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>', rib


def holly():
    leaves, ribs = [], []
    for deg in (-150, -30, 70):
        lf, rb = holly_leaf(300, 250, deg)
        leaves.append(lf)
        ribs.append(rb)
    out = ["\n".join(leaves), line_group(ribs, 2)]
    for x, y in ((284, 244), (314, 238), (300, 268)):
        out.append(f'<circle cx="{x}" cy="{y}" r="18" fill="{INK}"/><circle cx="{x - 5}" cy="{y - 5}" r="3.5" fill="{ARCH_FILL}"/>')
    return "\n".join(out)


def build_flowers():
    flower("january-carnation", "January", "Carnation", carnation())
    flower("february-violet", "February", "Violet", violet())
    flower("july-larkspur", "July", "Larkspur", larkspur())
    flower("august-poppy", "August", "Poppy", poppy())
    flower("november-chrysanthemum", "November", "Chrysanthemum", chrysanthemum())
    flower("december-holly", "December", "Holly", holly())


if __name__ == "__main__":
    pass  # superseded by sky_and_flowers.py
