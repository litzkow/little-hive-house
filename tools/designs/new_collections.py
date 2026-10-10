"""Bee Kind (extra), Furry Friends, Brasil, Holidays and Home Notes."""
import math
from common import (save, text, heart, star_points, hexagon, bee, mug,
                    SERIF_IT, BEBAS, MONO, JOS, JOST)

HONEY, SOFT, INKB, CREAMB = "#F2A81D", "#F9D88A", "#2B2118", "#FFF6E5"


def sparkle(cx, cy, s, fill):
    return (f'<path d="M {cx} {cy - s} Q {cx} {cy} {cx + s} {cy} Q {cx} {cy} {cx} {cy + s} '
            f'Q {cx} {cy} {cx - s} {cy} Q {cx} {cy} {cx} {cy - s} Z" fill="{fill}"/>')


# ---------------------------------------------------------------- Bee Kind (extra)
def build_bees():
    save("bee-kind", "bees-knees", "\n".join([
        f'<rect width="600" height="600" fill="{CREAMB}"/>',
        f'<polygon points="{hexagon(500, 96, 26)}" fill="{SOFT}"/>',
        f'<polygon points="{hexagon(522, 136, 26)}" fill="{SOFT}"/>',
        bee(300, 214, 1.5, "c-knees"),
        text(300, 384, "you're the", JOST, 42, INKB),
        text(300, 466, "BEE'S KNEES", JOS, 70, INKB, ls=2),
    ]))
    save("bee-kind", "bee-mine", "\n".join([
        f'<rect width="600" height="600" fill="{SOFT}"/>',
        heart(118, 140, 22, INKB), heart(476, 300, 16, INKB), heart(508, 120, 12, INKB),
        bee(330, 214, 1.5, "c-mine", heart_fill="#C2343A"),
        text(300, 450, "bee mine", JOS, 104, INKB),
        text(300, 512, "LITTLE HIVE HOUSE", JOST, 16, INKB, ls=6),
    ]))
    save("bee-kind", "bee-brave", "\n".join([
        f'<rect width="600" height="600" fill="{INKB}"/>',
        f'<polygon points="{hexagon(96, 528, 22)}" fill="none" stroke="{HONEY}" stroke-width="3"/>',
        f'<polygon points="{hexagon(510, 110, 22)}" fill="none" stroke="{HONEY}" stroke-width="3"/>',
        bee(306, 214, 1.5, "c-brave", body=HONEY, ink=CREAMB, wing=INKB, eye=INKB),
        text(300, 450, "bee brave", JOS, 104, HONEY),
        text(300, 512, "LITTLE HIVE HOUSE", JOST, 16, CREAMB, ls=6),
    ]))
    save("bee-kind", "busy-bee", "\n".join([
        f'<rect width="600" height="600" fill="{HONEY}"/>',
        f'<g stroke="{INKB}" stroke-width="5" stroke-linecap="round">'
        '<line x1="90" y1="190" x2="190" y2="190"/><line x1="120" y1="226" x2="210" y2="226"/>'
        '<line x1="70" y1="262" x2="180" y2="262"/></g>',
        bee(330, 220, 1.5, "c-busy", body=CREAMB, flip=True),
        text(300, 450, "busy bee", JOS, 104, INKB),
        text(300, 512, "LITTLE HIVE HOUSE", JOST, 16, INKB, ls=6),
    ]))


# ---------------------------------------------------------------- Furry Friends
SAGE, PINE, TERRA, PAPER = "#DCE3D3", "#23302A", "#C8673E", "#F7F1E6"


def paw(cx, cy, s, fill):
    return "\n".join([
        f'<ellipse cx="{cx}" cy="{cy + 0.45 * s:.1f}" rx="{1.05 * s:.1f}" ry="{0.85 * s:.1f}" fill="{fill}"/>',
        f'<ellipse cx="{cx - 1.0 * s:.1f}" cy="{cy - 0.55 * s:.1f}" rx="{0.36 * s:.1f}" ry="{0.48 * s:.1f}" transform="rotate(-22 {cx - 1.0 * s:.1f} {cy - 0.55 * s:.1f})" fill="{fill}"/>',
        f'<ellipse cx="{cx - 0.4 * s:.1f}" cy="{cy - 1.15 * s:.1f}" rx="{0.38 * s:.1f}" ry="{0.5 * s:.1f}" fill="{fill}"/>',
        f'<ellipse cx="{cx + 0.4 * s:.1f}" cy="{cy - 1.15 * s:.1f}" rx="{0.38 * s:.1f}" ry="{0.5 * s:.1f}" fill="{fill}"/>',
        f'<ellipse cx="{cx + 1.0 * s:.1f}" cy="{cy - 0.55 * s:.1f}" rx="{0.36 * s:.1f}" ry="{0.48 * s:.1f}" transform="rotate(22 {cx + 1.0 * s:.1f} {cy - 0.55 * s:.1f})" fill="{fill}"/>',
    ])


def dog_face(cx, cy, ink, bg, sw=5):
    return "\n".join([
        f'<g fill="{bg}" stroke="{ink}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">',
        f'<ellipse cx="{cx}" cy="{cy}" rx="70" ry="64"/>',
        f'<path d="M {cx - 56} {cy - 44} Q {cx - 112} {cy - 36} {cx - 102} {cy + 30} Q {cx - 84} {cy + 44} {cx - 66} {cy + 4} Z"/>',
        f'<path d="M {cx + 56} {cy - 44} Q {cx + 112} {cy - 36} {cx + 102} {cy + 30} Q {cx + 84} {cy + 44} {cx + 66} {cy + 4} Z"/>',
        f'<ellipse cx="{cx}" cy="{cy + 26}" rx="28" ry="21"/>',
        f'<path d="M {cx} {cy + 24} L {cx} {cy + 34}" fill="none"/>',
        f'<path d="M {cx - 13} {cy + 36} Q {cx} {cy + 46} {cx + 13} {cy + 36}" fill="none"/>',
        "</g>",
        f'<g fill="{ink}"><circle cx="{cx - 24}" cy="{cy - 10}" r="7"/><circle cx="{cx + 24}" cy="{cy - 10}" r="7"/>'
        f'<ellipse cx="{cx}" cy="{cy + 16}" rx="11" ry="8"/></g>',
    ])


def cat_face(cx, cy, ink, bg, sw=5):
    return "\n".join([
        f'<g fill="{bg}" stroke="{ink}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">',
        f'<path d="M {cx - 64} {cy - 20} L {cx - 58} {cy - 92} L {cx - 14} {cy - 56} Z"/>',
        f'<path d="M {cx + 64} {cy - 20} L {cx + 58} {cy - 92} L {cx + 14} {cy - 56} Z"/>',
        f'<ellipse cx="{cx}" cy="{cy}" rx="72" ry="60"/>',
        f'<path d="M {cx - 14} {cy + 22} Q {cx - 7} {cy + 30} {cx} {cy + 20} Q {cx + 7} {cy + 30} {cx + 14} {cy + 22}" fill="none"/>',
        "</g>",
        f'<g stroke="{ink}" stroke-width="{sw * 0.6:g}" stroke-linecap="round">'
        f'<line x1="{cx - 30}" y1="{cy + 12}" x2="{cx - 92}" y2="{cy + 2}"/><line x1="{cx - 30}" y1="{cy + 20}" x2="{cx - 90}" y2="{cy + 26}"/>'
        f'<line x1="{cx + 30}" y1="{cy + 12}" x2="{cx + 92}" y2="{cy + 2}"/><line x1="{cx + 30}" y1="{cy + 20}" x2="{cx + 90}" y2="{cy + 26}"/></g>',
        f'<g fill="{ink}"><ellipse cx="{cx - 26}" cy="{cy - 8}" rx="7" ry="10"/><ellipse cx="{cx + 26}" cy="{cy - 8}" rx="7" ry="10"/>'
        f'<path d="M {cx - 8} {cy + 8} L {cx + 8} {cy + 8} L {cx} {cy + 17} Z"/></g>',
    ])


def bone(cx, cy, fill):
    return (f'<g fill="{fill}"><rect x="{cx - 84}" y="{cy - 15}" width="168" height="30"/>'
            f'<circle cx="{cx - 88}" cy="{cy - 17}" r="23"/><circle cx="{cx - 88}" cy="{cy + 17}" r="23"/>'
            f'<circle cx="{cx + 88}" cy="{cy - 17}" r="23"/><circle cx="{cx + 88}" cy="{cy + 17}" r="23"/></g>')


def build_pets():
    save("furry-friends", "dog-mom", "\n".join([
        f'<rect width="600" height="600" fill="{SAGE}"/>',
        dog_face(300, 200, PINE, SAGE),
        heart(300, 108, 14, TERRA),
        text(300, 440, "DOG MOM", BEBAS, 140, PINE, ls=8),
        text(300, 500, "EST. WITH LOVE", MONO, 16, PINE, ls=6),
    ]))
    save("furry-friends", "cat-mom", "\n".join([
        f'<rect width="600" height="600" fill="{TERRA}"/>',
        cat_face(300, 214, PAPER, TERRA),
        text(300, 440, "CAT MOM", BEBAS, 140, PAPER, ls=8),
        text(300, 500, "EST. WITH LOVE", MONO, 16, PAPER, ls=6),
    ]))
    save("furry-friends", "good-boy", "\n".join([
        f'<rect width="600" height="600" fill="{PAPER}"/>',
        bone(300, 176, PINE),
        text(300, 362, "good", SERIF_IT, 104, PINE),
        text(300, 524, "BOY", BEBAS, 180, TERRA, ls=10),
    ]))
    save("furry-friends", "crazy-cat-lady", "\n".join([
        f'<rect width="600" height="600" fill="{PINE}"/>',
        f'<g transform="translate(100 64) scale(0.55)">{cat_face(180, 180, PAPER, PINE, sw=7)}</g>',
        f'<g transform="translate(200 50) scale(0.55)">{cat_face(180, 180, PAPER, PINE, sw=7)}</g>',
        f'<g transform="translate(300 64) scale(0.55)">{cat_face(180, 180, PAPER, PINE, sw=7)}</g>',
        text(300, 336, "crazy", SERIF_IT, 88, PAPER),
        text(300, 470, "CAT LADY", BEBAS, 134, TERRA, ls=8),
    ]))
    save("furry-friends", "adopt-dont-shop", "\n".join([
        f'<rect width="600" height="600" fill="{SAGE}"/>',
        paw(300, 182, 62, PINE),
        text(300, 420, "ADOPT", BEBAS, 140, PINE, ls=10),
        text(300, 500, "don't shop", SERIF_IT, 72, TERRA),
    ]))
    save("furry-friends", "who-rescued-who", "\n".join([
        f'<rect width="600" height="600" fill="{PAPER}"/>',
        heart(300, 192, 92, TERRA),
        paw(300, 196, 30, PAPER),
        text(300, 392, "who rescued", SERIF_IT, 66, PINE),
        text(300, 520, "WHO?", BEBAS, 150, PINE, ls=10),
    ]))


# ---------------------------------------------------------------- Brasil
GREEN, YELLOW, BLUE, CREAM, COFFEE = "#1F5E3B", "#F2C230", "#1E3A6E", "#FAF3E3", "#4A2E1F"


def build_brasil():
    save("brasil", "saudade", "\n".join([
        f'<rect width="600" height="600" fill="{GREEN}"/>',
        f'<rect x="30" y="30" width="540" height="540" rx="4" fill="none" stroke="{YELLOW}" stroke-width="2"/>',
        text(300, 290, "saudade", SERIF_IT, 112, CREAM),
        text(300, 354, "(n.) a deep longing for", MONO, 20, CREAM, ls=2),
        text(300, 386, "someone you love", MONO, 20, CREAM, ls=2),
        heart(300, 462, 28, YELLOW),
    ]))
    rays = "".join(
        f'<line x1="{300 + 74 * math.cos(math.radians(a)):.1f}" y1="{196 + 74 * math.sin(math.radians(a)):.1f}" '
        f'x2="{300 + 100 * math.cos(math.radians(a)):.1f}" y2="{196 + 100 * math.sin(math.radians(a)):.1f}"/>'
        for a in range(0, 360, 30))
    save("brasil", "bom-dia", "\n".join([
        f'<rect width="600" height="600" fill="{YELLOW}"/>',
        f'<circle cx="300" cy="196" r="56" fill="none" stroke="{GREEN}" stroke-width="7"/>',
        f'<g stroke="{GREEN}" stroke-width="7" stroke-linecap="round">{rays}</g>',
        text(300, 444, "BOM DIA", BEBAS, 150, GREEN, ls=8),
        text(300, 504, "GOOD MORNING", MONO, 18, GREEN, ls=6),
    ]))
    save("brasil", "cafe-com-leite", "\n".join([
        f'<rect width="600" height="600" fill="{CREAM}"/>',
        mug(292, 124, COFFEE),
        text(300, 414, "CAFÉ", BEBAS, 150, COFFEE, ls=8),
        text(300, 494, "com leite", SERIF_IT, 78, COFFEE),
    ]))
    save("brasil", "tamo-junto", "\n".join([
        f'<rect width="600" height="600" fill="{BLUE}"/>',
        f'<g fill="none" stroke="{YELLOW}" stroke-width="9"><circle cx="266" cy="192" r="58"/><circle cx="334" cy="192" r="58"/></g>',
        text(300, 424, "TAMO", BEBAS, 150, CREAM, ls=8),
        text(300, 500, "junto", SERIF_IT, 86, YELLOW),
    ]))
    stars = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in
                    ((276, 272, 3.5), (300, 292, 3), (324, 278, 3.5), (288, 306, 2.5), (316, 304, 2.5), (262, 292, 2.5)))
    save("brasil", "brasil", "\n".join([
        f'<rect width="600" height="600" fill="{GREEN}"/>',
        f'<polygon points="300,72 474,248 300,424 126,248" fill="{YELLOW}"/>',
        f'<circle cx="300" cy="248" r="82" fill="{BLUE}"/>',
        f'<path d="M 220 230 Q 300 204 380 262" fill="none" stroke="{CREAM}" stroke-width="12"/>',
        f'<g fill="{CREAM}">{stars}</g>',
        text(300, 528, "BRASIL", BEBAS, 120, CREAM, ls=14),
    ]))
    save("brasil", "cafune", "\n".join([
        f'<rect width="600" height="600" fill="{CREAM}"/>',
        f'<rect x="30" y="30" width="540" height="540" rx="4" fill="none" stroke="{GREEN}" stroke-width="2"/>',
        text(300, 228, "cafuné", SERIF_IT, 108, GREEN),
        text(300, 282, "/ka·fu·NEH/", MONO, 20, GREEN, ls=3),
        text(300, 362, "(n.) running your fingers", JOST, 30, COFFEE),
        text(300, 402, "through the hair of", JOST, 30, COFFEE),
        text(300, 442, "someone you love", JOST, 30, COFFEE),
        heart(300, 500, 20, YELLOW),
    ]))


# ---------------------------------------------------------------- Holidays
def build_holidays():
    pine, cream, gold = "#1E4D3A", "#F6EFE0", "#E9B949"
    snow = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in
                   ((80, 90, 4), (150, 250, 3), (520, 80, 3), (480, 220, 4), (90, 400, 3), (530, 420, 3), (210, 60, 2.5), (400, 70, 2.5)))
    save("christmas", "merry-and-bright", "\n".join([
        f'<rect width="600" height="600" fill="{pine}"/>',
        f'<g fill="{cream}" opacity="0.7">{snow}</g>',
        f'<polygon points="{star_points(300, 160, 64, 27)}" fill="{gold}"/>',
        text(300, 344, "merry", SERIF_IT, 104, cream),
        text(300, 474, "& BRIGHT", BEBAS, 124, gold, ls=8),
    ]))
    black, orange = "#151515", "#E8833A"
    ghost = ("M 236 320 L 236 190 Q 236 112 300 112 Q 364 112 364 190 L 364 320 "
             "q -10.7 -18 -21.3 0 t -21.3 0 t -21.3 0 t -21.3 0 t -21.3 0 t -21.5 0 Z")
    save("halloween", "boo", "\n".join([
        f'<rect width="600" height="600" fill="{black}"/>',
        f'<path d="{ghost}" fill="{cream}"/>',
        f'<g fill="{black}"><ellipse cx="278" cy="196" rx="9" ry="14"/><ellipse cx="322" cy="196" rx="9" ry="14"/>'
        '<ellipse cx="300" cy="244" rx="10" ry="14"/></g>',
        f'<g fill="none" stroke="{orange}" stroke-width="4" stroke-linecap="round">'
        '<path d="M 120 130 q 14 -14 28 0 q 14 -14 28 0"/><path d="M 430 190 q 12 -12 24 0 q 12 -12 24 0"/></g>',
        text(300, 512, "BOO!", BEBAS, 176, orange, ls=12),
    ]))
    paper, rust, brown = "#F6EDE0", "#B4532A", "#5A3A22"
    leaf = "M 300 256 Q 252 186 300 104 Q 348 186 300 256 Z"
    save("holidays", "thankful", "\n".join([
        f'<rect width="600" height="600" fill="{paper}"/>',
        f'<path d="{leaf}" fill="#D98A3D" transform="rotate(-42 300 256)"/>',
        f'<path d="{leaf}" fill="{rust}" transform="rotate(42 300 256)"/>',
        f'<path d="{leaf}" fill="{brown}"/>',
        f'<g stroke="{paper}" stroke-width="3" stroke-linecap="round"><line x1="300" y1="250" x2="300" y2="128"/>'
        '<line x1="300" y1="250" x2="300" y2="128" transform="rotate(-42 300 256)"/>'
        '<line x1="300" y1="250" x2="300" y2="128" transform="rotate(42 300 256)"/></g>',
        text(300, 404, "thankful", SERIF_IT, 106, brown),
        text(300, 474, "GIVE THANKS", MONO, 18, rust, ls=8),
    ]))
    pink, red = "#F4C7C3", "#C2343A"
    save("holidays", "xoxo", "\n".join([
        f'<rect width="600" height="600" fill="{pink}"/>',
        heart(210, 150, 22, red), heart(300, 138, 30, red), heart(390, 150, 22, red),
        text(300, 404, "XOXO", BEBAS, 210, red, ls=12),
        text(300, 488, "with love", SERIF_IT, 64, red),
    ]))
    navy, gold2 = "#1D2B44", "#E2B857"
    flute = (f'<path d="M -22 -92 L 22 -92 L 14 0 Q 0 10 -14 0 Z" fill="none" stroke="{gold2}" stroke-width="5" stroke-linejoin="round"/>'
             f'<path d="M -19 -60 L 19 -60 L 14 0 Q 0 10 -14 0 Z" fill="{gold2}" opacity="0.55"/>'
             f'<line x1="0" y1="6" x2="0" y2="70" stroke="{gold2}" stroke-width="5"/>'
             f'<ellipse cx="0" cy="72" rx="26" ry="6" fill="none" stroke="{gold2}" stroke-width="5"/>')
    save("holidays", "cheers", "\n".join([
        f'<rect width="600" height="600" fill="{navy}"/>',
        f'<g transform="translate(262 214) rotate(-14)">{flute}</g>',
        f'<g transform="translate(338 214) rotate(14)">{flute}</g>',
        f'<g stroke="{cream}" stroke-width="4" stroke-linecap="round"><line x1="300" y1="78" x2="300" y2="96"/>'
        '<line x1="272" y1="86" x2="282" y2="100"/><line x1="328" y1="86" x2="318" y2="100"/></g>',
        sparkle(150, 130, 14, gold2), sparkle(460, 300, 12, gold2), sparkle(130, 330, 9, cream),
        text(300, 436, "CHEERS", BEBAS, 150, gold2, ls=10),
        text(300, 504, "to the new year", SERIF_IT, 52, cream),
    ]))
    navy2, red2 = "#1F2F4D", "#B23A3A"
    stars = "".join(f'<polygon points="{star_points(x, 104, 20, 8.5)}"/>' for x in (180, 240, 300, 360, 420))
    save("holidays", "happy-4th", "\n".join([
        f'<rect width="600" height="600" fill="{paper}"/>',
        f'<g fill="{navy2}">{stars}</g>',
        text(300, 268, "HAPPY", BEBAS, 130, navy2, ls=10),
        text(300, 424, "4th", SERIF_IT, 170, red2),
        text(300, 500, "OF JULY", MONO, 22, navy2, ls=10),
    ]))


# ---------------------------------------------------------------- Home Notes
def laurel(cx, y, ink):
    out = []
    for side in (-1, 1):
        x0, y0, xc, yc, x1, y1 = cx + side * 8, y + 70, cx + side * 150, y + 70, cx + side * 186, y - 40
        out.append(f'<path d="M {x0} {y0} Q {xc} {yc} {x1} {y1}" fill="none" stroke="{ink}" stroke-width="4" stroke-linecap="round"/>')
        for i in range(1, 10):
            t = i / 10
            px = (1 - t) ** 2 * x0 + 2 * t * (1 - t) * xc + t * t * x1
            py = (1 - t) ** 2 * y0 + 2 * t * (1 - t) * yc + t * t * y1
            dx = 2 * (1 - t) * (xc - x0) + 2 * t * (x1 - xc)
            dy = 2 * (1 - t) * (yc - y0) + 2 * t * (y1 - yc)
            ang = math.degrees(math.atan2(dy, dx))
            for k in (-1, 1):
                out.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="17" ry="6.5" fill="{ink}" '
                           f'transform="rotate({ang + k * 40:.1f} {px:.1f} {py:.1f}) translate(14 0)"/>')
    return "\n".join(out)


def build_home():
    ink = "#3A2E2A"
    save("home-notes", "love-you-more", "\n".join([
        '<rect width="600" height="600" fill="#F3D9D3"/>',
        text(300, 246, "love you", SERIF_IT, 98, ink),
        text(300, 448, "MORE", BEBAS, 196, ink, ls=12),
        heart(300, 512, 18, "#C2343A"),
    ]))
    save("home-notes", "blessed", "\n".join([
        '<rect width="600" height="600" fill="#DCE3D3"/>',
        text(300, 294, "blessed", SERIF_IT, 128, ink),
        laurel(300, 410, ink),
    ]))
    save("home-notes", "family", "\n".join([
        '<rect width="600" height="600" fill="#D6E4EE"/>',
        f'<g fill="none" stroke="{ink}" stroke-width="6" stroke-linejoin="round"><path d="M 300 80 L 382 150 L 382 236 L 218 236 L 218 150 Z"/>'
        '<rect x="284" y="190" width="32" height="46"/></g>',
        heart(300, 150, 14, "#C2343A"),
        text(300, 428, "FAMILY", BEBAS, 150, ink, ls=12),
        text(300, 500, "our favorite people", SERIF_IT, 48, ink),
    ]))
    save("home-notes", "grandmas-kitchen", "\n".join([
        '<rect width="600" height="600" fill="#F6EDE0"/>',
        f'<g fill="none" stroke="{ink}" stroke-width="5" stroke-linejoin="round"><rect x="210" y="150" width="180" height="40" rx="18"/>'
        '<rect x="166" y="162" width="44" height="16" rx="8"/><rect x="390" y="162" width="44" height="16" rx="8"/></g>',
        heart(300, 110, 16, "#C2343A"),
        text(300, 336, "Grandma's", SERIF_IT, 88, ink),
        text(300, 466, "KITCHEN", BEBAS, 140, ink, ls=10),
        text(300, 520, "MADE WITH LOVE", MONO, 16, ink, ls=6),
    ]))
    rays = "".join(
        f'<line x1="{300 + 92 * math.cos(math.radians(a)):.1f}" y1="{250 + 92 * math.sin(math.radians(a)):.1f}" '
        f'x2="{300 + 120 * math.cos(math.radians(a)):.1f}" y2="{250 + 120 * math.sin(math.radians(a)):.1f}"/>'
        for a in range(200, 341, 20))
    save("home-notes", "hello-sunshine", "\n".join([
        '<rect width="600" height="600" fill="#F7E7A9"/>',
        f'<path d="M 226 250 A 74 74 0 0 1 374 250 Z" fill="#E9A23B" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>',
        f'<g stroke="{ink}" stroke-width="5" stroke-linecap="round">{rays}<line x1="160" y1="250" x2="440" y2="250"/></g>',
        text(300, 382, "hello", SERIF_IT, 98, ink),
        text(300, 500, "SUNSHINE", BEBAS, 124, ink, ls=8),
    ]))
    save("home-notes", "choose-joy", "\n".join([
        '<rect width="600" height="600" fill="#F5D5B8"/>',
        sparkle(130, 146, 22, ink), sparkle(506, 330, 16, ink), sparkle(104, 440, 12, ink), sparkle(476, 110, 10, ink),
        text(300, 232, "choose", SERIF_IT, 102, ink),
        text(300, 476, "JOY", BEBAS, 250, ink, ls=14),
    ]))


if __name__ == "__main__":
    # Legacy: superseded by the painted/gouache/ink generators (kitchen_ink.py, holidays_gouache.py, summer_gouache.py, ...).
    # Only the builds below that no newer generator replaces are kept.
    build_bees()
    build_pets()
    build_brasil()
    # build_holidays()
    build_home()
