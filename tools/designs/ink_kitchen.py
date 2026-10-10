"""Ink Cities (line-drawn skylines) and Kitchen Words (black & white type) — second batch."""
from common import save, text, frame, heart, mug, DMS, MONO, SERIF_IT, BEBAS

INK = "#1A1A1A"
PAPER = "#F4F0E8"


def windows(x, y0, y1, w, step=20):
    return [f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}"/>' for y in range(y0, y1 + 1, step)]


def ink(slug, name, sub, bold, fine=(), dashed=(), name_size=66):
    body = f"""
<rect width="600" height="600" fill="{PAPER}"/>
<rect x="26" y="26" width="548" height="548" rx="4" fill="none" stroke="{INK}" stroke-width="3"/>
<rect x="36" y="36" width="528" height="528" rx="2" fill="none" stroke="{INK}" stroke-width="1"/>
<g fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
{chr(10).join(bold)}
</g>
<g stroke="{INK}" stroke-width="1.5" stroke-linecap="round" fill="none">
{chr(10).join(fine)}
<g stroke-dasharray="6 6">{''.join(dashed)}</g>
</g>
<line x1="66" y1="420" x2="534" y2="420" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>
{text(300, 500, name, DMS, name_size, INK)}
{text(300, 542, sub, MONO, 17, INK, ls=5)}
"""
    save("ink-cities", slug, body)


CLOUD_L = '<path d="M 86 150 q 8 -20 30 -12 q 14 -22 38 -4 q 22 -4 22 16 Z"/>'
CLOUD_R = '<path d="M 430 110 q 8 -18 28 -10 q 13 -20 34 -4 q 20 -4 20 14 Z"/>'
BIRDS = '<path d="M 420 140 q 8 -8 16 0 q 8 -8 16 0"/><path d="M 466 116 q 6 -6 12 0 q 6 -6 12 0"/>'


def build_ink():
    # Chicago: Willis Tower and the John Hancock Center
    ink("chicago", "Chicago", "ILLINOIS · USA",
        [CLOUD_L, BIRDS,
         '<path d="M 262 420 L 262 210 L 280 210 L 280 160 L 298 160 L 298 125 L 322 125 L 322 175 L 338 175 L 338 420"/>',
         '<line x1="304" y1="125" x2="304" y2="70"/>', '<line x1="316" y1="125" x2="316" y2="84"/>',
         '<path d="M 378 420 L 388 180 L 422 180 L 432 420 Z"/>',
         '<line x1="398" y1="180" x2="398" y2="122"/>', '<line x1="412" y1="180" x2="412" y2="132"/>',
         '<rect x="200" y="300" width="50" height="120"/>', '<rect x="140" y="340" width="50" height="80"/>',
         '<rect x="84" y="372" width="46" height="48"/>', '<rect x="446" y="318" width="44" height="102"/>',
         '<rect x="500" y="362" width="34" height="58"/>'],
        ['<line x1="280" y1="214" x2="280" y2="410"/>', '<line x1="298" y1="166" x2="298" y2="410"/>',
         '<line x1="322" y1="180" x2="322" y2="410"/>',
         '<line x1="389" y1="184" x2="427" y2="300"/>', '<line x1="421" y1="184" x2="383" y2="300"/>',
         '<line x1="383" y1="300" x2="430" y2="414"/>', '<line x1="427" y1="300" x2="380" y2="414"/>'],
        windows(210, 320, 400, 30) + windows(150, 360, 400, 30) + windows(454, 338, 400, 28))

    # Seattle: the Space Needle with Mount Rainier
    ink("seattle", "Seattle", "WASHINGTON · USA",
        ['<circle cx="120" cy="140" r="30"/>', CLOUD_R,
         '<path d="M 66 420 L 150 300 Q 175 262 195 262 Q 215 262 240 300 L 296 392"/>',
         '<path d="M 150 300 L 165 312 L 178 296 L 192 314 L 206 296 L 222 308 L 240 300"/>',
         '<path d="M 330 420 Q 352 330 354 214"/>', '<path d="M 390 420 Q 368 330 366 214"/>',
         '<line x1="345" y1="300" x2="375" y2="300"/>',
         '<ellipse cx="360" cy="200" rx="58" ry="12"/>', '<path d="M 330 196 L 338 182 L 382 182 L 390 196"/>',
         '<ellipse cx="360" cy="182" rx="22" ry="5"/>', '<line x1="360" y1="177" x2="360" y2="96"/>',
         '<ellipse cx="360" cy="214" rx="18" ry="4"/>',
         '<rect x="430" y="330" width="46" height="90"/>', '<rect x="486" y="360" width="46" height="60"/>'],
        ['<line x1="352" y1="232" x2="368" y2="300"/>', '<line x1="368" y1="232" x2="352" y2="300"/>',
         '<line x1="348" y1="300" x2="372" y2="410"/>', '<line x1="372" y1="300" x2="346" y2="410"/>'],
        windows(438, 346, 400, 26) + windows(494, 378, 400, 22))

    # Miami: an art deco hotel between two palms
    palm_l = ['<path d="M 140 420 Q 150 330 128 260"/>', '<path d="M 128 260 Q 90 240 70 262"/>',
              '<path d="M 128 260 Q 100 220 82 226"/>', '<path d="M 128 260 Q 140 220 168 214"/>',
              '<path d="M 128 260 Q 170 246 182 270"/>', '<path d="M 128 260 Q 130 236 120 206"/>']
    palm_r = ['<path d="M 460 420 Q 450 330 472 260"/>', '<path d="M 472 260 Q 510 240 530 262"/>',
              '<path d="M 472 260 Q 500 220 518 226"/>', '<path d="M 472 260 Q 460 220 432 214"/>',
              '<path d="M 472 260 Q 430 246 418 270"/>', '<path d="M 472 260 Q 470 236 480 206"/>']
    ink("miami", "Miami", "FLORIDA · USA",
        ['<circle cx="300" cy="96" r="30"/>'] + palm_l + palm_r +
        ['<rect x="220" y="230" width="160" height="190"/>',
         '<path d="M 270 230 L 270 200 L 290 200 L 290 172 L 310 172 L 310 200 L 330 200 L 330 230"/>',
         '<line x1="300" y1="172" x2="300" y2="140"/>',
         '<path d="M 286 420 L 286 392 Q 300 376 314 392 L 314 420"/>',
         '<circle cx="246" cy="252" r="8"/>', '<circle cx="354" cy="252" r="8"/>'],
        ['<line x1="220" y1="276" x2="380" y2="276"/>', '<line x1="220" y1="318" x2="380" y2="318"/>',
         '<line x1="220" y1="360" x2="380" y2="360"/>', '<line x1="300" y1="200" x2="300" y2="230"/>'],
        windows(236, 292, 300, 44) + windows(318, 292, 300, 44) + windows(236, 334, 342, 44) + windows(318, 334, 342, 44))

    # Nashville: the "Batman" building, a guitar and music notes
    ink("nashville", "Nashville", "TENNESSEE · USA",
        ['<path d="M 200 150 L 200 118 L 222 112 L 222 144"/>',
         '<path d="M 130 404 C 90 404 88 360 106 344 C 92 326 100 296 130 296 C 160 296 168 326 154 344 C 172 360 170 404 130 404 Z"/>',
         '<circle cx="130" cy="336" r="9"/>', '<rect x="124" y="214" width="12" height="82"/>',
         '<rect x="121" y="186" width="18" height="28" rx="3"/>',
         '<rect x="268" y="210" width="64" height="210"/>', '<path d="M 268 210 L 300 172 L 332 210"/>',
         '<rect x="268" y="112" width="10" height="98"/>', '<rect x="322" y="112" width="10" height="98"/>',
         '<path d="M 268 112 L 273 88 L 278 112"/>', '<path d="M 322 112 L 327 88 L 332 112"/>',
         '<rect x="200" y="300" width="50" height="120"/>', '<rect x="360" y="282" width="50" height="138"/>',
         '<rect x="420" y="332" width="46" height="88"/>', '<rect x="476" y="362" width="50" height="58"/>'],
        ['<line x1="128" y1="196" x2="128" y2="372"/>', '<line x1="132" y1="196" x2="132" y2="372"/>',
         '<line x1="118" y1="372" x2="142" y2="372"/>',
         '<line x1="286" y1="224" x2="286" y2="410"/>', '<line x1="300" y1="224" x2="300" y2="410"/>',
         '<line x1="314" y1="224" x2="314" y2="410"/>'],
        windows(210, 320, 400, 26) + windows(370, 300, 400, 25) + windows(428, 350, 400, 25))

    # Boston: Back Bay brownstones and a gas lamp
    bold = ['<line x1="100" y1="420" x2="100" y2="300"/>', '<path d="M 90 300 L 110 300 L 106 284 L 94 284 Z"/>',
            '<line x1="100" y1="284" x2="100" y2="276"/>', '<circle cx="500" cy="372" r="30"/>',
            '<line x1="500" y1="402" x2="500" y2="420"/>', CLOUD_R]
    fine = []
    for i, top in enumerate((236, 256, 236)):
        x0 = 135 + i * 110
        bold += [f'<rect x="{x0}" y="{top}" width="110" height="{420 - top}"/>',
                 f'<rect x="{x0 + 76}" y="{top - 22}" width="14" height="22"/>',
                 f'<rect x="{x0 + 14}" y="{top + 30}" width="42" height="100"/>',
                 f'<rect x="{x0 + 68}" y="{top + 36}" width="28" height="36"/>',
                 f'<path d="M {x0 + 66} 420 L {x0 + 66} 382 Q {x0 + 82} 364 {x0 + 98} 382 L {x0 + 98} 420"/>']
        fine += [f'<line x1="{x0}" y1="{top + 12}" x2="{x0 + 110}" y2="{top + 12}"/>',
                 f'<line x1="{x0 + 28}" y1="{top + 30}" x2="{x0 + 28}" y2="{top + 130}"/>',
                 f'<line x1="{x0 + 42}" y1="{top + 30}" x2="{x0 + 42}" y2="{top + 130}"/>',
                 f'<line x1="{x0 + 14}" y1="{top + 80}" x2="{x0 + 56}" y2="{top + 80}"/>',
                 f'<line x1="{x0 + 82}" y1="{top + 36}" x2="{x0 + 82}" y2="{top + 72}"/>',
                 f'<rect x="{x0 + 14}" y="{top + 148}" width="42" height="26"/>']
    ink("boston", "Boston", "MASSACHUSETTS · USA", bold, fine)

    # Rome: the Colosseum
    bold = ['<circle cx="480" cy="118" r="30"/>', CLOUD_L,
            '<path d="M 90 420 L 90 250 Q 250 226 400 236 L 400 252 L 440 256 L 440 290 L 480 296 L 510 300 L 510 420"/>',
            '<line x1="90" y1="300" x2="510" y2="300"/>', '<line x1="90" y1="360" x2="510" y2="360"/>']
    fine = []
    for x in range(104, 500, 40):
        bold.append(f'<path d="M {x} 420 L {x} 386 Q {x + 14} 370 {x + 28} 386 L {x + 28} 420"/>')
        bold.append(f'<path d="M {x} 356 L {x} 328 Q {x + 14} 314 {x + 28} 328 L {x + 28} 356"/>')
        if x < 390:
            fine.append(f'<rect x="{x + 8}" y="{262}" width="12" height="22"/>')
    ink("rome", "Rome", "ITALIA", bold, fine)


# ---------------------------------------------------------------- Kitchen Words
BLACK = "#161616"
CREAM = "#F4F0E8"


def kitchen(slug, dark, inner):
    bg, fg = (BLACK, CREAM) if dark else (CREAM, BLACK)
    save("kitchen-words", slug, frame(bg, fg) + "\n" + inner(fg, bg))


def build_kitchen():
    kitchen("life-happens-coffee-helps", True, lambda fg, bg: "\n".join([
        text(300, 172, "life happens,", SERIF_IT, 66, fg),
        text(300, 348, "COFFEE", BEBAS, 168, fg, ls=6),
        text(300, 432, "helps", SERIF_IT, 80, fg),
        mug(296, 470, fg, sw=4, steam=False).replace('width="4"', 'width="4" transform="translate(150 235) scale(0.5)"'),
    ]))
    def taco(fg, bg):
        import math
        lettuce = []
        for i in range(25):
            a = math.radians(188 + i * 164 / 24)
            r = 100 if i % 2 == 0 else 112
            lettuce.append(f"{300 + r * math.cos(a):.1f} {262 + r * math.sin(a):.1f}")
        return "\n".join([
            f'<g fill="none" stroke="{fg}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">',
            '<path d="M ' + " L ".join(lettuce) + '"/>',
            '<path d="M 206 262 A 94 94 0 0 1 394 262 Z" fill="' + bg + '"/>',
            '<path d="M 228 262 A 72 72 0 0 1 372 262"/>', '</g>',
            f'<g fill="{fg}"><circle cx="252" cy="160" r="6"/><circle cx="300" cy="146" r="6"/><circle cx="348" cy="160" r="6"/></g>',
            text(300, 418, "TACO", BEBAS, 160, fg, ls=8),
            text(300, 500, "tuesday", SERIF_IT, 80, fg),
        ])
    kitchen("taco-tuesday", False, taco)
    kitchen("eat-cake", True, lambda fg, bg: "\n".join([
        f'<g fill="none" stroke="{fg}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">',
        '<rect x="220" y="170" width="160" height="82" rx="6"/>',
        '<path d="M 220 188 q 10 16 20 0 t 20 0 t 20 0 t 20 0 t 20 0 t 20 0 t 20 0 t 20 0"/>',
        '<line x1="196" y1="266" x2="404" y2="266"/>', '<rect x="294" y="122" width="12" height="48" rx="3"/>', '</g>',
        f'<path d="M 300 92 Q 314 108 300 118 Q 286 108 300 92 Z" fill="{fg}"/>',
        text(300, 382, "eat", SERIF_IT, 96, fg),
        text(300, 522, "CAKE", BEBAS, 160, fg, ls=8),
    ]))
    kitchen("gather", False, lambda fg, bg: "\n".join([
        text(300, 222, "GATHER", BEBAS, 160, fg, ls=8),
        f'<line x1="150" y1="258" x2="226" y2="258" stroke="{fg}" stroke-width="2"/>',
        f'<line x1="374" y1="258" x2="450" y2="258" stroke="{fg}" stroke-width="2"/>',
        text(300, 265, "AROUND", MONO, 20, fg, ls=6),
        text(300, 326, "the table", SERIF_IT, 50, fg),
        f'<g fill="none" stroke="{fg}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">',
        '<line x1="160" y1="450" x2="440" y2="450"/>', '<line x1="184" y1="450" x2="184" y2="520"/>',
        '<line x1="416" y1="450" x2="416" y2="520"/>',
        '<ellipse cx="236" cy="440" rx="32" ry="7"/>', '<ellipse cx="364" cy="440" rx="32" ry="7"/>',
        '<path d="M 290 446 L 288 420 Q 288 410 300 410 Q 312 410 312 420 L 310 446 Z"/>',
        '<path d="M 300 410 L 300 376"/>', '<path d="M 300 396 Q 286 386 282 372"/>', '<path d="M 300 388 Q 314 380 318 366"/>',
        '</g>',
    ]))
    kitchen("pizza-love-language", True, lambda fg, bg: "\n".join([
        f'<g fill="none" stroke="{fg}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">',
        '<path d="M 226 118 Q 300 94 374 118 L 300 286 Z"/>', '<path d="M 234 134 Q 300 112 366 134"/>', '</g>',
        f'<g fill="{fg}"><circle cx="276" cy="166" r="13"/><circle cx="322" cy="184" r="13"/><circle cx="298" cy="228" r="11"/></g>',
        text(300, 444, "PIZZA", BEBAS, 160, fg, ls=8),
        text(300, 510, "is my love language", SERIF_IT, 46, fg),
    ]))
    kitchen("stay-cozy", False, lambda fg, bg: "\n".join([
        mug(290, 132, fg, heart_fill=fg),
        text(300, 412, "STAY", BEBAS, 150, fg, ls=8),
        text(300, 500, "cozy", SERIF_IT, 96, fg),
    ]))


if __name__ == "__main__":
    # Legacy: superseded by the painted/gouache/ink generators (kitchen_ink.py, holidays_gouache.py, summer_gouache.py, ...).
    # Only the builds below that no newer generator replaces are kept.
    # build_kitchen()
