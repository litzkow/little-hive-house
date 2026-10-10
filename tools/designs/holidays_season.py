"""Fall, Halloween and Christmas, second edition: illustrated, framed and print-safe."""
import math

from common import BEBAS, JOS, JOST, MONO, SERIF_IT, heart, save, star_points
from icons import (acorn, bat, candy_cane, candy_corn, cat, cinnamon, crescent, ghost, gingerbread, holly, maple,
                   mug, oak_leaf, ornament, pumpkin, santa_hat, snowflake, spider, star_anise, string_lights,
                   web_corner, wheat, witch_hat, wrapped_candy, xmas_tree)
from layout import Art, Gap, T, frame, ruled_label, scatter, speckle, stack, arc_text

# ---------------------------------------------------------------- palette
RUST, MUSTARD, OLIVE, CREAM, BROWN, PLUM, ORANGE = "#B4532A", "#D9A23B", "#5E6B34", "#F6EDE0", "#4A2F1E", "#6B2E3A", "#E37B33"


def leaf_rain(colors, n, seed, avoid, size=(18, 30), opacity=1.0):
    def shape(x, y, r, k):
        col = colors[k % len(colors)]
        s = size[0] + (k * 7) % (size[1] - size[0])
        f = maple if k % 3 else oak_leaf
        return f'<g opacity="{opacity}">' + (f(x, y, s, col, vein=CREAM, rot=r) if f is maple else f(x, y, s * 0.9, col, vein=CREAM, rot=r)) + "</g>"
    return scatter(shape, n, seed, box=(82, 82, 518, 518), avoid=avoid, min_d=70)


def build_fall():
    # hello fall
    save("fall", "hello-fall", "\n".join([
        f'<rect width="600" height="600" fill="{CREAM}"/>', speckle(RUST, 70, 3, opacity=0.18),
        leaf_rain([MUSTARD, OLIVE, PLUM], 6, 11, (150, 70, 450, 540), opacity=0.9),
        frame(RUST),
        stack([Art(170, lambda y: maple(300, y + 92, 84, RUST, vein=CREAM, shade="#9C4523")), Gap(22),
               T("hello", SERIF_IT, 96, BROWN), Gap(14), T("FALL", BEBAS, 160, RUST, ls=14), Gap(22),
               ruled_label("SWEATER SEASON", BROWN, size=15, ls=5)]),
    ]))
    # pumpkin spice
    save("fall", "pumpkin-spice", "\n".join([
        f'<rect width="600" height="600" fill="{MUSTARD}"/>', speckle(BROWN, 60, 5, opacity=0.12),
        frame(BROWN),
        stack([Art(178, lambda y: cinnamon(330, y + 40, 456, y + 150) + cinnamon(350, y + 30, 476, y + 132)
                   + pumpkin(286, y + 100, 196, 150, base=ORANGE) + star_anise(164, y + 140, 34)), Gap(18),
               T("pumpkin spice", SERIF_IT, 78, BROWN), Gap(10),
               T("& EVERYTHING NICE", BEBAS, 66, CREAM, ls=5), Gap(18),
               ruled_label("FRESHLY BAKED", BROWN, size=14, ls=5)]),
    ]))
    # sweater weather: fair isle bands
    def fair_isle(y):
        out = [f'<rect x="0" y="{y}" width="600" height="86" fill="{RUST}"/>']
        out += [f'<polygon points="{x},{y + 43} {x + 12},{y + 31} {x + 24},{y + 43} {x + 12},{y + 55}" fill="{CREAM}"/>' for x in range(-6, 610, 30)]
        out += [f'<circle cx="{x + 12}" cy="{y + 43}" r="3" fill="{RUST}"/>' for x in range(-6, 610, 30)]
        out += [f'<path d="M {x} {y + 14} l 7 -7 l 7 7" fill="none" stroke="{MUSTARD}" stroke-width="3"/>' for x in range(0, 600, 14)]
        out += [f'<path d="M {x} {y + 72} l 7 7 l 7 -7" fill="none" stroke="{MUSTARD}" stroke-width="3"/>' for x in range(0, 600, 14)]
        return "".join(out)
    save("fall", "sweater-weather", "\n".join([
        f'<rect width="600" height="600" fill="{OLIVE}"/>', fair_isle(36), fair_isle(478),
        stack([T("SWEATER", BEBAS, 150, CREAM, ls=10), Gap(10), T("weather", SERIF_IT, 104, MUSTARD), Gap(16),
               ruled_label("BUNDLE UP", CREAM, size=15, ls=6)], top=130, bottom=470),
    ]))
    # cozy season
    save("fall", "cozy-season", "\n".join([
        f'<rect width="600" height="600" fill="{BROWN}"/>', speckle(CREAM, 60, 9, opacity=0.08),
        leaf_rain([RUST, MUSTARD, OLIVE], 5, 4, (150, 60, 450, 540), size=(16, 26)),
        frame(MUSTARD),
        stack([Art(170, lambda y: mug(286, y + 52, CREAM, BROWN, band=RUST, band2=MUSTARD, w=150, h=116)), Gap(26),
               T("COZY", BEBAS, 140, CREAM, ls=12), Gap(12), T("season", SERIF_IT, 88, MUSTARD), Gap(16),
               ruled_label("BLANKETS · BOOKS · COCOA", CREAM, size=13, ls=3, line_w=24)]),
    ]))
    # falling for you
    def falling(y):
        out = []
        for (x0, y0, x1, y1, col, s, r) in ((150, y - 6, 196, y + 70, RUST, 40, -24), (300, y - 20, 290, y + 104, MUSTARD, 46, 12), (444, y, 410, y + 66, PLUM, 38, 30)):
            out.append(f'<path d="M {x0} {y0} Q {x0 + 40} {(y0 + y1) / 2} {x1} {y1 - 36}" fill="none" stroke="{BROWN}" stroke-width="2" stroke-dasharray="2 8" stroke-linecap="round" opacity="0.6"/>')
            out.append(maple(x1, y1, s, col, vein=CREAM, rot=r))
        return "".join(out)
    save("fall", "falling-for-you", "\n".join([
        f'<rect width="600" height="600" fill="{CREAM}"/>', speckle(RUST, 60, 21, opacity=0.15), frame(RUST),
        stack([Art(150, falling), Gap(26), T("falling", SERIF_IT, 108, BROWN), Gap(14), T("FOR YOU", BEBAS, 112, RUST, ls=12),
               Gap(18), Art(30, lambda y: heart(300, y + 14, 18, RUST))]),
    ]))
    # harvest
    def bundle(y):
        stalks = "".join(wheat(300 + dx * 0.15, y + 196, y + 12 + abs(dx) * 0.4, CREAM, lean=dx) for dx in (-96, -48, 0, 48, 96))
        return stalks + f'<path d="M 262 {y + 150} Q 300 {y + 168} 338 {y + 150}" fill="none" stroke="{MUSTARD}" stroke-width="12" stroke-linecap="round"/>' \
                        f'<path d="M 300 {y + 158} q -30 26 -40 52 M 300 {y + 158} q 26 24 32 50" fill="none" stroke="{MUSTARD}" stroke-width="7" stroke-linecap="round"/>'
    save("fall", "harvest", "\n".join([
        f'<rect width="600" height="600" fill="{RUST}"/>', speckle(BROWN, 70, 13, opacity=0.18), frame(MUSTARD),
        stack([Art(214, bundle), Gap(24), T("HARVEST", BEBAS, 126, CREAM, ls=12), Gap(16),
               T("gather & give thanks", SERIF_IT, 48, MUSTARD)]),
    ]))
    # oh my gourd
    def gourds(y):
        return (pumpkin(220, y + 110, 170, 128, base=ORANGE) + pumpkin(392, y + 120, 140, 108, base=MUSTARD, dark="#B9832A", light="#EFC46A")
                + pumpkin(306, y + 150, 112, 80, base="#F3E6CF", dark="#DCCBAE", light="#FFFFFF"))
    save("fall", "oh-my-gourd", "\n".join([
        f'<rect width="600" height="600" fill="{PLUM}"/>', speckle(CREAM, 60, 31, opacity=0.08), frame(MUSTARD),
        stack([Art(196, gourds), Gap(20), T("oh my", SERIF_IT, 92, CREAM), Gap(14), T("GOURD!", BEBAS, 140, MUSTARD, ls=12)]),
    ]))
    # autumn is calling
    garland = lambda y: "".join(maple(300 + 150 * math.sin(math.radians(a)), y + 30 - 26 * math.cos(math.radians(a)), 24, c, vein=CREAM, rot=a)
                                for a, c in zip((-60, -30, 0, 30, 60), (OLIVE, MUSTARD, RUST, MUSTARD, PLUM)))
    save("fall", "autumn-is-calling", "\n".join([
        f'<rect width="600" height="600" fill="{CREAM}"/>', speckle(BROWN, 60, 17, opacity=0.14), frame(BROWN),
        arc_text("LEAVES ARE FALLING", 300, 330, 220, MONO, 22, BROWN, ls=7, uid="aut-arc"),
        stack([T("AUTUMN", BEBAS, 150, RUST, ls=12), Gap(18), T("is calling", SERIF_IT, 80, BROWN), Gap(34), Art(60, garland)],
              top=150, bottom=520),
    ]))


# ---------------------------------------------------------------- Halloween
BLACK, PUMPKIN, PURPLE, LIME, BONE, MOON = "#151515", "#E8833A", "#3E2654", "#86A85A", "#F6EFE0", "#F3D27A"


def stars_field(color, seed, n=40, avoid=None):
    return speckle(color, n, seed, r=(1, 2.4), opacity=0.7, avoid=avoid)


def build_halloween():
    save("halloween", "boo", "\n".join([
        f'<rect width="600" height="600" fill="{BLACK}"/>', stars_field(BONE, 2),
        bat(128, 130, 34, "#2E2E2E", eyes=MOON), bat(480, 176, 28, "#2E2E2E", eyes=MOON),
        frame(PUMPKIN),
        stack([Art(244, lambda y: ghost(300, y + 6, 150)), Gap(16), T("BOO!", BEBAS, 168, PUMPKIN, ls=14)]),
    ]))
    save("halloween", "happy-halloween", "\n".join([
        f'<rect width="600" height="600" fill="{BLACK}"/>', stars_field(BONE, 7),
        f'<circle cx="300" cy="224" r="150" fill="{PUMPKIN}" opacity="0.12"/><circle cx="300" cy="224" r="118" fill="{PUMPKIN}" opacity="0.12"/>',
        frame(PUMPKIN),
        stack([Art(214, lambda y: pumpkin(300, y + 124, 250, 180, base=PUMPKIN, dark="#C4601F", light="#F6A25A", face="#FFD25E")), Gap(22),
               T("HAPPY", BEBAS, 92, BONE, ls=16), Gap(4), T("halloween", SERIF_IT, 92, PUMPKIN)]),
    ]))
    def candies(y):
        return (candy_corn(214, y + 70, 46, -18) + candy_corn(386, y + 80, 46, 16) + candy_corn(300, y + 40, 56, 0)
                + wrapped_candy(240, y + 150, 50, PURPLE, BONE, -12) + wrapped_candy(364, y + 150, 50, BLACK, PUMPKIN, 10))
    save("halloween", "trick-or-treat", "\n".join([
        f'<rect width="600" height="600" fill="{PUMPKIN}"/>', speckle(BLACK, 60, 4, opacity=0.08), frame(BLACK),
        stack([Art(180, candies), Gap(18), T("TRICK", BEBAS, 116, BLACK, ls=12), Gap(2), T("or", SERIF_IT, 56, BONE), Gap(8),
               T("TREAT", BEBAS, 116, BLACK, ls=12)]),
    ]))
    def night(y):
        house = (f'<g fill="{BLACK}"><path d="M 360 {y + 200} L 360 {y + 120} L 400 {y + 86} L 440 {y + 120} L 440 {y + 200} Z"/>'
                 f'<rect x="420" y="{y + 70}" width="12" height="34"/><path d="M 380 {y + 200} L 380 {y + 146} L 420 {y + 146} L 420 {y + 200} Z"/></g>'
                 f'<rect x="392" y="{y + 126}" width="12" height="14" fill="{MOON}"/><rect x="404" y="{y + 160}" width="10" height="14" fill="{MOON}"/>')
        tree = f'<path d="M 170 {y + 200} L 176 {y + 110} L 150 {y + 76} M 176 {y + 130} L 206 {y + 96} L 222 {y + 100} M 174 {y + 104} L 182 {y + 70}" fill="none" stroke="{BLACK}" stroke-width="7" stroke-linecap="round"/>'
        hill = f'<path d="M 90 {y + 204} Q 300 {y + 170} 510 {y + 204} Z" fill="{BLACK}"/>'
        return crescent(300, y + 76, 66, MOON, PURPLE, crater="#E2BE5E") + bat(220, y + 40, 26, BLACK) + bat(392, y + 20, 20, BLACK) + tree + house + hill
    save("halloween", "spooky-season", "\n".join([
        f'<rect width="600" height="600" fill="{PURPLE}"/>', stars_field(BONE, 12), frame(MOON),
        stack([Art(204, night), Gap(22), T("spooky", SERIF_IT, 110, BONE), Gap(2), T("SEASON", BEBAS, 104, PUMPKIN, ls=16)]),
    ]))
    save("halloween", "here-for-the-boos", "\n".join([
        f'<rect width="600" height="600" fill="{PUMPKIN}"/>', speckle(BLACK, 50, 14, opacity=0.08), frame(BLACK),
        stack([Art(214, lambda y: cat(258, y + 214, 104, BLACK) + ghost(398, y + 60, 74, arms=False)), Gap(20),
               T("here for the", SERIF_IT, 64, BLACK), Gap(6), T("BOOS", BEBAS, 140, BONE, ls=16)]),
    ]))
    save("halloween", "witch-please", "\n".join([
        f'<rect width="600" height="600" fill="{LIME}"/>', speckle(BLACK, 50, 18, opacity=0.08), frame(BLACK),
        f'<polygon points="{star_points(140, 150, 14, 6)}" fill="{MOON}"/><polygon points="{star_points(468, 128, 10, 4)}" fill="{MOON}"/><polygon points="{star_points(492, 200, 7, 3)}" fill="{MOON}"/>',
        stack([Art(200, lambda y: witch_hat(300, y + 186, 96, band=PURPLE)), Gap(26), T("WITCH", BEBAS, 150, BLACK, ls=14), Gap(4),
               T("please", SERIF_IT, 90, BONE)]),
    ]))
    save("halloween", "creep-it-real", "\n".join([
        f'<rect width="600" height="600" fill="{BLACK}"/>', stars_field(BONE, 15, n=26),
        f'<g opacity="0.55">{web_corner(BONE, 250, 1.8)}</g>',
        f'<g transform="translate(600 0) scale(-1 1)" opacity="0.35">{web_corner(BONE, 170, 1.4)}</g>',
        f'<line x1="430" y1="0" x2="430" y2="160" stroke="{BONE}" stroke-width="1.6"/>', spider(430, 176, 26, PUMPKIN, BONE),
        frame(PUMPKIN),
        stack([T("creep it", SERIF_IT, 104, BONE), Gap(4), T("REAL", BEBAS, 176, PUMPKIN, ls=18)], top=230, bottom=540),
    ]))
    save("halloween", "stay-spooky", "\n".join([
        f'<rect width="600" height="600" fill="{PURPLE}"/>', stars_field(BONE, 22), frame(PUMPKIN),
        stack([Art(170, lambda y: ghost(184, y + 54, 86, arms=False) + ghost(300, y + 4, 120) + ghost(416, y + 60, 80, arms=False)),
               Gap(26), T("STAY", BEBAS, 132, PUMPKIN, ls=16), Gap(4), T("spooky", SERIF_IT, 100, BONE)]),
    ]))


# ---------------------------------------------------------------- Christmas
RED, PINE, IVORY, GOLD, NIGHT, GREEN2 = "#B8312F", "#1E4D3A", "#FBF6EE", "#E9B949", "#1F3550", "#2F7A57"


def snow(seed, n=60, color=IVORY, opacity=0.6, avoid=None):
    return speckle(color, n, seed, r=(1.4, 3.6), opacity=opacity, avoid=avoid)


def build_christmas():
    save("christmas", "merry-and-bright", "\n".join([
        f'<rect width="600" height="600" fill="{PINE}"/>', snow(3, 50, opacity=0.35),
        string_lights(62, "#122E22", [GOLD, RED, IVORY, "#7FC4C0"], amp=30, x0=10, x1=590, n=11),
        frame(GOLD, inset=40),
        stack([Art(110, lambda y: f'<polygon points="{star_points(300, y + 56, 56, 23)}" fill="{GOLD}"/>'
                   + "".join(f'<line x1="{300 + 70 * math.cos(math.radians(a)):.1f}" y1="{y + 56 + 70 * math.sin(math.radians(a)):.1f}" x2="{300 + 86 * math.cos(math.radians(a)):.1f}" y2="{y + 56 + 86 * math.sin(math.radians(a)):.1f}" stroke="{GOLD}" stroke-width="4" stroke-linecap="round"/>' for a in range(-90, 270, 45))),
               Gap(30), T("merry", SERIF_IT, 112, IVORY), Gap(6), T("& BRIGHT", BEBAS, 120, GOLD, ls=10)], top=110),
    ]))
    save("christmas", "merry-christmas", "\n".join([
        f'<rect width="600" height="600" fill="{PINE}"/>', snow(5, 70, opacity=0.4), frame(GOLD),
        stack([Art(236, lambda y: xmas_tree(300, y + 16, 98, green=GREEN2, dark="#246349")), Gap(22),
               T("merry", SERIF_IT, 84, IVORY), Gap(2), T("CHRISTMAS", BEBAS, 100, GOLD, ls=8)]),
    ]))
    save("christmas", "ho-ho-ho", "\n".join([
        f'<rect width="600" height="600" fill="{RED}"/>', snow(8, 70, opacity=0.45), frame(IVORY),
        stack([Art(150, lambda y: santa_hat(290, y + 136, 100)), Gap(26), T("HO HO HO!", BEBAS, 140, IVORY, ls=10), Gap(16),
               ruled_label("MERRY CHRISTMAS", GOLD, size=16, ls=6)]),
    ]))
    def village(y):
        out = [f'<path d="M 60 {y + 200} Q 200 {y + 160} 300 {y + 182} Q 420 {y + 204} 540 {y + 170} L 540 {y + 220} L 60 {y + 220} Z" fill="{IVORY}"/>']
        for x, w, h, roof in ((140, 60, 60, RED), (226, 74, 80, "#2F5E8A"), (330, 64, 64, GREEN2), (420, 56, 54, RED)):
            base = y + 196
            out.append(f'<rect x="{x}" y="{base - h}" width="{w}" height="{h}" fill="#F0E2CF"/>'
                       f'<path d="M {x - 8} {base - h + 2} L {x + w / 2} {base - h - 34} L {x + w + 8} {base - h + 2} Z" fill="{roof}"/>'
                       f'<path d="M {x - 8} {base - h + 2} L {x + w / 2} {base - h - 34} L {x + w + 8} {base - h + 2} L {x + w / 2} {base - h - 22} Z" fill="{IVORY}"/>'
                       f'<rect x="{x + w / 2 - 8}" y="{base - 24}" width="16" height="24" fill="#6B4A2E"/>'
                       f'<rect x="{x + 8}" y="{base - h + 14}" width="12" height="12" fill="{GOLD}"/><rect x="{x + w - 20}" y="{base - h + 14}" width="12" height="12" fill="{GOLD}"/>')
        return snowflake(300, y + 50, 52, IVORY, 5) + snowflake(160, y + 30, 22, IVORY, 3) + snowflake(446, y + 36, 26, IVORY, 3) + "".join(out)
    save("christmas", "let-it-snow", "\n".join([
        f'<rect width="600" height="600" fill="{NIGHT}"/>', snow(13, 90, opacity=0.55), frame(IVORY),
        stack([Art(222, village), Gap(22), T("let it", SERIF_IT, 88, IVORY), Gap(2), T("SNOW", BEBAS, 132, IVORY, ls=18)]),
    ]))
    def cocoa(y):
        marsh = "".join(f'<rect x="{x}" y="{y + yy}" width="26" height="22" rx="6" fill="{IVORY}" stroke="#E6D7C3" stroke-width="2" transform="rotate({r} {x + 13} {y + yy + 11})"/>'
                        for x, yy, r in ((232, 36, -12), (262, 28, 8), (292, 36, -4), (322, 30, 14)))
        return mug(290, y + 52, IVORY, "#5A2A22", band=RED, band2=IVORY, coffee="#6B3A2A") + marsh + candy_cane(356, y + 0, 92, w=10, rot=18)
    save("christmas", "hot-cocoa-season", "\n".join([
        f'<rect width="600" height="600" fill="{RED}"/>', snow(17, 60, opacity=0.4), frame(GOLD),
        stack([Art(176, cocoa), Gap(24), T("hot cocoa", SERIF_IT, 92, IVORY), Gap(4), T("SEASON", BEBAS, 112, GOLD, ls=14)]),
    ]))
    def checklist(y):
        box = lambda yy, checked: (f'<rect x="150" y="{yy - 46}" width="54" height="54" rx="8" fill="none" stroke="{PINE}" stroke-width="6"/>' +
                                   (f'<path d="M 160 {yy - 20} L 176 {yy - 2} L 214 {yy - 60}" fill="none" stroke="{RED}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>' if checked else ""))
        return (box(y + 64, False) + f'<text x="232" y="{y + 64}" {BEBAS} font-size="92" letter-spacing="4" fill="{PINE}">NAUGHTY</text>'
                + box(y + 176, True) + f'<text x="232" y="{y + 176}" {BEBAS} font-size="92" letter-spacing="4" fill="{RED}">NICE</text>')
    save("christmas", "naughty-or-nice", "\n".join([
        f'<rect width="600" height="600" fill="{IVORY}"/>', speckle(RED, 50, 23, opacity=0.12), frame(PINE),
        holly(118, 112, 54) , candy_cane(470, 70, 120, w=11, rot=14),
        stack([T("DEAR SANTA,", MONO, 24, PINE, ls=6), Gap(20), Art(190, checklist), Gap(8), T("(mostly)", SERIF_IT, 52, PINE)], top=110),
    ]))
    def hanging(y):
        return (ornament(170, y + 120, 34, RED, GOLD, hook=40) + ornament(300, y + 92, 44, GOLD, RED, kind="zig", hook=40)
                + ornament(430, y + 128, 32, "#2F5E8A", IVORY, kind="dots", hook=40))
    save("christmas", "joy-to-the-world", "\n".join([
        f'<rect width="600" height="600" fill="{NIGHT}"/>', snow(29, 70, opacity=0.4),
        hanging(0),
        frame(GOLD),
        stack([T("JOY", BEBAS, 220, IVORY, ls=24), Gap(8), T("to the world", SERIF_IT, 74, GOLD)], top=230, bottom=540),
    ]))
    save("christmas", "feliz-natal", "\n".join([
        f'<rect width="600" height="600" fill="{IVORY}"/>', speckle(GREEN2, 50, 31, opacity=0.12),
        frame(RED),
        stack([Art(150, lambda y: gingerbread(206, y + 96, 92) + holly(300, y + 120, 46) + f'<polygon points="{star_points(410, y + 80, 52, 21)}" fill="{GOLD}"/>'),
               Gap(28), T("feliz", SERIF_IT, 104, PINE), Gap(4), T("NATAL", BEBAS, 150, RED, ls=16)]),
    ]))


if __name__ == "__main__":
    build_fall()
    build_halloween()
    build_christmas()
