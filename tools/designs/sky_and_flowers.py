"""Night Sky and Birth Flowers, second edition: star-chart rings, a Milky Way band, botanical arches,
all type inside the print-safe area."""
import math
import pathlib
import random

from common import CINZEL, MONO, SERIF_IT, esc, fit_size, measure, save

# ---------------------------------------------------------------- Night Sky
NIGHT, STAR, GOLD = "#0E1116", "#F4F0E8", "#D9B26A"

C = {
    "aries": ("ARIES", "THE RAM", "MAR 21 – APR 19",
              [[(170, 180), (320, 230), (400, 272), (418, 318)]],
              [(170, 180, 4.5), (320, 230, 7.5), (400, 272, 5.5), (418, 318, 4)], (320, 230)),
    "taurus": ("TAURUS", "THE BULL", "APR 20 – MAY 20",
               [[(180, 320), (240, 300), (300, 280), (325, 255), (352, 232), (430, 140)], [(300, 280), (340, 295), (440, 250)]],
               [(180, 320, 4), (240, 300, 4), (300, 280, 5), (325, 255, 4), (352, 232, 4.5), (430, 140, 6), (340, 295, 7.5), (440, 250, 5),
                (195, 155, 2.6), (206, 148, 2.2), (212, 161, 2.8), (200, 169, 2.2), (188, 163, 2), (216, 150, 1.8)], (340, 295)),
    "gemini": ("GEMINI", "THE TWINS", "MAY 21 – JUN 20",
               [[(210, 120), (215, 190), (230, 270), (240, 340), (205, 365)], [(270, 110), (290, 185), (315, 265), (335, 330), (385, 350)],
                [(170, 170), (215, 190), (290, 185), (345, 170)]],
               [(210, 120, 6.5), (270, 110, 7.5), (215, 190, 4), (230, 270, 4.5), (240, 340, 5), (205, 365, 4), (290, 185, 4),
                (315, 265, 4.5), (335, 330, 5.5), (385, 350, 4), (170, 170, 3.5), (345, 170, 3.5)], (270, 110)),
    "cancer": ("CANCER", "THE CRAB", "JUN 21 – JUL 22",
               [[(240, 140), (300, 240), (370, 170)], [(300, 240), (300, 300), (265, 375)]],
               [(240, 140, 5), (300, 240, 5), (370, 170, 4.5), (300, 300, 4), (265, 375, 6.5)], (265, 375)),
    "leo": ("LEO", "THE LION", "JUL 23 – AUG 22",
            [[(230, 300), (225, 250), (245, 200), (285, 178), (318, 192), (322, 222)], [(225, 250), (370, 238), (430, 290), (360, 300), (230, 300)],
             [(370, 238), (360, 300)]],
            [(230, 300, 7.5), (225, 250, 5), (245, 200, 5.5), (285, 178, 4.5), (318, 192, 4), (322, 222, 3.5), (370, 238, 4.5), (430, 290, 6),
             (360, 300, 4.5)], (230, 300)),
    "virgo": ("VIRGO", "THE MAIDEN", "AUG 23 – SEP 22",
              [[(180, 140), (220, 200), (270, 230), (300, 290), (330, 360)], [(270, 230), (330, 200), (390, 150)],
               [(300, 290), (380, 300), (430, 280)], [(330, 200), (350, 250), (300, 290)]],
              [(180, 140, 4), (220, 200, 4.5), (270, 230, 5), (300, 290, 5), (330, 360, 7.5), (330, 200, 4.5), (390, 150, 4), (380, 300, 4.5),
               (430, 280, 4), (350, 250, 4)], (330, 360)),
    "libra": ("LIBRA", "THE SCALES", "SEP 23 – OCT 22",
              [[(240, 200), (320, 150), (380, 230), (300, 280), (240, 200)], [(240, 200), (200, 300), (215, 345)], [(380, 230), (400, 330)]],
              [(240, 200, 5.5), (320, 150, 7), (380, 230, 5), (300, 280, 4.5), (200, 300, 4), (215, 345, 4), (400, 330, 4.5)], (320, 150)),
    "scorpio": ("SCORPIO", "THE SCORPION", "OCT 23 – NOV 21",
                [[(150, 130), (170, 175), (160, 215)], [(170, 175), (220, 190), (255, 215), (285, 245), (300, 290), (305, 335), (330, 370),
                                                         (372, 380), (408, 365), (420, 335), (410, 312)]],
                [(150, 130, 4), (170, 175, 5), (160, 215, 4), (220, 190, 4.5), (255, 215, 8), (285, 245, 4.5), (300, 290, 4.5), (305, 335, 4),
                 (330, 370, 4.5), (372, 380, 4), (408, 365, 5), (420, 335, 5.5), (410, 312, 4)], (255, 215)),
    "sagittarius": ("SAGITTARIUS", "THE ARCHER", "NOV 22 – DEC 21",
                    [[(210, 280), (250, 230), (320, 230), (360, 280), (320, 330), (250, 330), (210, 280)], [(250, 230), (285, 180), (320, 230)],
                     [(210, 280), (160, 232)], [(360, 280), (410, 250), (425, 305), (360, 280)]],
                    [(210, 280, 5), (250, 230, 5), (320, 230, 5.5), (360, 280, 5), (320, 330, 7), (250, 330, 5), (285, 180, 4.5), (160, 232, 4),
                     (410, 250, 4), (425, 305, 4)], (320, 330)),
    "capricorn": ("CAPRICORN", "THE SEA-GOAT", "DEC 22 – JAN 19",
                  [[(170, 170), (250, 230), (380, 170), (430, 190), (350, 310), (260, 320), (200, 260), (170, 170)]],
                  [(170, 170, 5.5), (250, 230, 4), (380, 170, 4.5), (430, 190, 7), (350, 310, 4.5), (260, 320, 4.5), (200, 260, 4)], (430, 190)),
    "aquarius": ("AQUARIUS", "THE WATER-BEARER", "JAN 20 – FEB 18",
                 [[(150, 150), (220, 190), (280, 170), (330, 230), (300, 290), (350, 330), (420, 300)], [(280, 170), (300, 120), (355, 110)]],
                 [(150, 150, 4), (220, 190, 4.5), (280, 170, 7), (330, 230, 4.5), (300, 290, 4), (350, 330, 4.5), (420, 300, 4), (300, 120, 5),
                  (355, 110, 4)], (280, 170)),
    "pisces": ("PISCES", "THE FISH", "FEB 19 – MAR 20",
               [[(170, 140), (195, 155), (205, 180), (185, 195), (160, 185), (150, 160), (170, 140)], [(205, 180), (300, 270), (400, 360)],
                [(400, 360), (440, 240), (430, 140)], [(430, 140), (455, 115), (415, 105), (430, 140)]],
               [(170, 140, 3.5), (195, 155, 3.5), (205, 180, 4), (185, 195, 3.5), (160, 185, 3.5), (150, 160, 3.5), (300, 270, 4.5),
                (400, 360, 7), (440, 240, 4.5), (430, 140, 4), (455, 115, 3.5), (415, 105, 3.5)], (400, 360)),
}

RC, RR = (300, 232), 168


def tx(p):
    x, y = p
    return 300 + (x - 300) * 0.86, RC[1] + (y - 245) * 0.86


def milky_way(seed):
    rnd = random.Random(seed)
    dots = []
    for _ in range(260):
        t = rnd.uniform(-0.15, 1.15)
        off = rnd.gauss(0, 34)
        x = 40 + t * 520 + off * 0.7
        y = 560 - t * 520 + off * 0.7
        if 0 <= x <= 600 and 0 <= y <= 600:
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.5, 1.6):.1f}"/>')
    return f'<g fill="{STAR}" opacity="0.32">' + "".join(dots) + "</g>"


def field(seed):
    rnd = random.Random(seed * 7 + 3)
    dots = []
    while len(dots) < 46:
        x, y = rnd.uniform(10, 590), rnd.uniform(10, 590)
        if math.hypot(x - RC[0], y - RC[1]) < RR + 6 and y < 410:
            continue
        if 70 < x < 530 and 420 < y < 540:
            continue
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(0.8, 2.0):.1f}"/>')
    return f'<g fill="{STAR}" opacity="0.6">' + "".join(dots) + "</g>"


def ring():
    out = [f'<circle cx="{RC[0]}" cy="{RC[1]}" r="{RR}" fill="none" stroke="{GOLD}" stroke-width="1.6" opacity="0.75"/>',
           f'<circle cx="{RC[0]}" cy="{RC[1]}" r="{RR - 22}" fill="none" stroke="{GOLD}" stroke-width="1" opacity="0.35" stroke-dasharray="2 7"/>']
    ticks = []
    for a in range(0, 360, 5):
        L = 10 if a % 30 == 0 else 5
        r1, r2 = RR, RR - L
        ra = math.radians(a)
        ticks.append(f'<line x1="{RC[0] + r1 * math.cos(ra):.1f}" y1="{RC[1] + r1 * math.sin(ra):.1f}" x2="{RC[0] + r2 * math.cos(ra):.1f}" y2="{RC[1] + r2 * math.sin(ra):.1f}"/>')
    out.append(f'<g stroke="{GOLD}" stroke-width="1.2" opacity="0.7">' + "".join(ticks) + "</g>")
    for a in (0, 90, 180, 270):
        ra = math.radians(a)
        x, y = RC[0] + (RR + 1) * math.cos(ra), RC[1] + (RR + 1) * math.sin(ra)
        out.append(f'<rect x="{x - 4:.1f}" y="{y - 4:.1f}" width="8" height="8" transform="rotate(45 {x:.1f} {y:.1f})" fill="{GOLD}"/>')
    return "\n".join(out)


def sparkle(x, y, s, col):
    return (f'<path d="M {x:.1f} {y - s:.1f} Q {x:.1f} {y:.1f} {x + s:.1f} {y:.1f} Q {x:.1f} {y:.1f} {x:.1f} {y + s:.1f} Q {x:.1f} {y:.1f} {x - s:.1f} {y:.1f} Q {x:.1f} {y:.1f} {x:.1f} {y - s:.1f} Z" fill="{col}"/>')


def build_sky():
    for k, (slug, (name, latin, dates, lines, stars, bright)) in enumerate(C.items()):
        poly = "\n".join('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in map(tx, ln)) + '"/>' for ln in lines)
        st = "".join(f'<circle cx="{tx((x, y))[0]:.1f}" cy="{tx((x, y))[1]:.1f}" r="{r * 0.9:.1f}"/>' for x, y, r in stars)
        bx, by = tx(bright)
        size = fit_size(name, CINZEL, 50, 420, 10)
        body = f"""
<rect width="600" height="600" fill="{NIGHT}"/>
{milky_way(k + 1)}
{field(k + 1)}
{ring()}
<g fill="none" stroke="{STAR}" stroke-opacity="0.55" stroke-width="1.8" stroke-linejoin="round">
{poly}
</g>
<circle cx="{bx:.1f}" cy="{by:.1f}" r="22" fill="{GOLD}" opacity="0.12"/><circle cx="{bx:.1f}" cy="{by:.1f}" r="13" fill="{GOLD}" opacity="0.22"/>
<g fill="{STAR}">{st}</g>
{sparkle(bx, by, 17, STAR)}
<text x="{300 + 5:.0f}" y="458" text-anchor="middle" {CINZEL} font-size="{size}" letter-spacing="10" fill="{GOLD}">{esc(name)}</text>
<text x="303" y="486" text-anchor="middle" {MONO} font-size="14" letter-spacing="6" fill="{GOLD}" opacity="0.85">{esc(latin)}</text>
<text x="302" y="520" text-anchor="middle" {MONO} font-size="17" letter-spacing="4" fill="{STAR}" opacity="0.85">{esc(dates)}</text>
"""
        save("night-sky", slug, body)


# ---------------------------------------------------------------- Birth Flowers
INK, ARCH, PAPER = "#222222", "#F1ECE2", "#FAF8F3"
ART = pathlib.Path(__file__).parent / "art" / "flowers"
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]


def sprig(x, y, flip=False):
    s = -1 if flip else 1
    leaves = "".join(f'<ellipse cx="{x + s * dx:.1f}" cy="{y - dy:.1f}" rx="9" ry="4" transform="rotate({s * ang} {x + s * dx:.1f} {y - dy:.1f})" fill="{INK}"/>'
                     for dx, dy, ang in ((8, 8, -30), (16, 18, -40), (8, 26, 40), (20, 32, -50), (12, 40, 30)))
    return f'<path d="M {x} {y} Q {x + s * 14} {y - 24} {x + s * 18} {y - 46}" fill="none" stroke="{INK}" stroke-width="2"/>{leaves}'


def build_flowers():
    rnd = random.Random(5)
    speck = "".join(f'<circle cx="{rnd.uniform(8, 592):.1f}" cy="{rnd.uniform(8, 592):.1f}" r="{rnd.uniform(0.8, 1.8):.1f}"/>' for _ in range(70))
    for f in sorted(ART.glob("*.svg")):
        slug = f.stem
        month, flower = slug.split("-", 1)
        num = MONTHS.index(month) + 1
        flower_name = f"{num:02d} · " + flower.replace("-", " ").upper()
        art = f.read_text(encoding="utf-8")
        fsz = fit_size(flower_name, MONO, 15, 300, 5)
        fw = measure(flower_name, MONO, fsz, 5)
        body = f"""
<rect width="600" height="600" fill="{PAPER}"/>
<g fill="{INK}" opacity="0.1">{speck}</g>
<path d="M 118 452 L 118 256 A 182 182 0 0 1 482 256 L 482 452 Z" fill="{ARCH}" stroke="{INK}" stroke-width="2.5"/>
<path d="M 128 444 L 128 256 A 172 172 0 0 1 472 256 L 472 444 Z" fill="none" stroke="{INK}" stroke-width="1" opacity="0.6"/>
<g transform="translate(19.2 -3) scale(0.936)">
{art}
</g>
<line x1="96" y1="452" x2="504" y2="452" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>
<text x="300" y="500" text-anchor="middle" {SERIF_IT} font-size="{fit_size(month.title(), SERIF_IT, 48, 360)}" fill="{INK}">{month.title()}</text>
<text x="{302.5:.1f}" y="528" text-anchor="middle" {MONO} font-size="{fsz}" letter-spacing="5" fill="{INK}">{esc(flower_name)}</text>
<g stroke="{INK}" stroke-width="1.4"><line x1="{300 - fw / 2 - 40:.1f}" y1="523" x2="{300 - fw / 2 - 14:.1f}" y2="523"/><line x1="{300 + fw / 2 + 14:.1f}" y1="523" x2="{300 + fw / 2 + 40:.1f}" y2="523"/></g>
"""
        save("birth-flowers", slug, body)


if __name__ == "__main__":
    # build_sky()  # superseded by night_sky_painted.py
    build_flowers()
