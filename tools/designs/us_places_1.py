"""American Places, batch 1: Chicago, Nashville, New Orleans, Charleston, Las Vegas, Seattle, Boston,
Philadelphia, Yellowstone, Yosemite."""
import math

from poster import poster
from scene import (P, birds, cloud, cypress, grass_tufts, hills, lighthouse, palm, pine, rays, ridge, round_tree,
                   sailboat, sky, sky_curved, snowcap, stars, streak, sun, water, windows)


def chicago():
    far = [(0, 300), (40, 300), (40, 270), (70, 270), (70, 286), (100, 286), (100, 250), (126, 250), (126, 292), (170, 292), (170, 262),
           (196, 262), (196, 300), (420, 300), (420, 258), (446, 258), (446, 284), (480, 284), (480, 240), (500, 240), (500, 290),
           (540, 290), (540, 266), (566, 266), (566, 300), (600, 300), (600, 360), (0, 360)]
    near = [(0, 360), (0, 318), (34, 318), (34, 296), (60, 296), (60, 330), (88, 330), (88, 276), (112, 276), (112, 320),
            (150, 320), (150, 288), (178, 288), (178, 330), (214, 330),
            # Willis Tower
            (214, 210), (232, 210), (232, 160), (250, 160), (250, 128), (272, 128), (272, 176), (288, 176), (288, 226), (300, 226),
            (300, 312), (330, 312), (330, 280), (352, 280),
            # Hancock (tapered)
            (356, 170), (388, 170), (394, 330),
            (420, 330), (420, 300), (450, 300), (450, 322), (470, 322), (470, 292), (500, 292), (500, 360)]
    lights = "".join(f'<rect x="{x}" y="{y}" width="3" height="4" fill="#F7C873"/>' for x, y in (
        (40, 304), (48, 312), (70, 300), (96, 290), (104, 304), (120, 300), (160, 300), (186, 310), (222, 230), (226, 260), (240, 180),
        (244, 220), (258, 150), (262, 200), (264, 240), (278, 196), (280, 250), (292, 240), (312, 320), (340, 296), (366, 200), (372, 240),
        (378, 290), (430, 312), (460, 330), (480, 306), (488, 320)))
    wheel_c, wheel_r = (496, 302), 42
    spokes = "".join(f'<line x1="{wheel_c[0]}" y1="{wheel_c[1]}" x2="{wheel_c[0] + wheel_r * math.cos(math.radians(a)):.1f}" y2="{wheel_c[1] + wheel_r * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 20))
    gond = "".join(f'<rect x="{wheel_c[0] + wheel_r * math.cos(math.radians(a)) - 4:.1f}" y="{wheel_c[1] + wheel_r * math.sin(math.radians(a)) - 3:.1f}" width="8" height="7" rx="2" fill="#E9707A"/>' for a in range(0, 360, 40))
    return f"""
{sky_curved([(0, "#E9B6C4"), (110, "#F4C7C3"), (200, "#F8D6B6"), (262, "#FBE4BA")])}
{sun(300, 292, 92, "#F6A26E", halo="#F7B98A")}
{streak(70, 120, 120, "#F6D1D4")}{streak(410, 96, 140, "#F6D1D4")}
{birds([(120, 160, 14), (146, 172, 10)], "#2E3456")}
<polygon points="{P(far)}" fill="#B98BA6"/>
<polygon points="{P(near)}" fill="#2E3456"/>
<g stroke="#2E3456" stroke-width="3"><line x1="256" y1="128" x2="256" y2="98"/><line x1="266" y1="128" x2="266" y2="104"/><line x1="366" y1="170" x2="366" y2="128"/><line x1="378" y1="170" x2="378" y2="134"/></g>
<g stroke="#4A5280" stroke-width="2"><line x1="360" y1="176" x2="388" y2="250"/><line x1="384" y1="176" x2="360" y2="250"/><line x1="362" y1="250" x2="392" y2="326"/><line x1="388" y1="250" x2="358" y2="326"/></g>
{lights}
<g stroke="#2E3456" stroke-width="2.5" fill="none"><circle cx="{wheel_c[0]}" cy="{wheel_c[1]}" r="{wheel_r}"/>{spokes}</g>
{gond}
<polygon points="{P([(490, 302), (502, 302), (520, 356), (506, 356)])}" fill="#2E3456"/><polygon points="{P([(490, 302), (502, 302), (486, 356), (472, 356)])}" fill="#2E3456"/>
<rect x="430" y="352" width="170" height="10" fill="#2E3456"/>
{water(360, "#3C5A80")}
<g fill="#F7C873" opacity="0.8">{"".join(f'<rect x="{x}" y="{y}" width="{w}" height="3" rx="1.5"/>' for x, y, w in ((240, 372, 30), (250, 386, 18), (262, 400, 26), (360, 376, 20), (366, 392, 14), (60, 380, 24), (470, 400, 30), (520, 374, 26)))}</g>
<g stroke="#5E7BA3" stroke-width="3" stroke-linecap="round"><line x1="30" y1="420" x2="80" y2="420"/><line x1="160" y1="432" x2="220" y2="432"/><line x1="400" y1="426" x2="450" y2="426"/></g>
{sailboat(130, 404, 58, "#F6EDE0", "#F6EDE0", "#E9B6C4")}
"""


def nashville():
    sky_ = sky_curved([(0, "#2B2A4C"), (130, "#5B3F6B"), (210, "#C9666B"), (262, "#F09A5F")])
    skyline = [(0, 360), (0, 300), (40, 300), (40, 280), (80, 280), (80, 310), (120, 310), (120, 262), (150, 262), (150, 300), (190, 300),
               (190, 276), (216, 276), (216, 320), (232, 320),
               # Batman building
               (232, 190), (246, 190), (246, 120), (251, 100), (256, 120), (256, 168), (290, 150), (324, 168), (324, 120), (329, 100), (334, 120),
               (334, 190), (348, 190), (348, 300), (380, 300), (380, 250), (410, 250), (410, 296), (446, 296), (446, 270), (476, 270), (476, 310),
               (520, 310), (520, 286), (560, 286), (560, 320), (600, 320), (600, 360)]
    lights = "".join(f'<rect x="{x}" y="{y}" width="4" height="5" fill="#F7C873"/>' for x, y in (
        (50, 300), (60, 310), (130, 280), (138, 300), (196, 290), (204, 300), (262, 200), (272, 210), (282, 180), (296, 190), (306, 210), (316, 196),
        (262, 240), (300, 250), (318, 270), (390, 270), (398, 286), (456, 290), (530, 300), (540, 310)))
    guitar = """
<g transform="translate(482 286) rotate(14) scale(0.8)">
<rect x="-7" y="-150" width="14" height="140" fill="#6B3E26"/>
<g fill="#E8E0D0">{frets}</g>
<rect x="-12" y="-186" width="24" height="40" rx="6" fill="#4A2A1A"/>
<g fill="#E9C46A"><circle cx="-12" cy="-176" r="3.5"/><circle cx="-12" cy="-162" r="3.5"/><circle cx="12" cy="-176" r="3.5"/><circle cx="12" cy="-162" r="3.5"/></g>
<path d="M 0 -20 C -40 -24 -48 18 -30 34 C -54 50 -52 112 0 112 C 52 112 54 50 30 34 C 48 18 40 -24 0 -20 Z" fill="#E8A33D"/>
<path d="M 0 -20 C 40 -24 48 18 30 34 C 54 50 52 112 0 112 C 20 100 26 60 14 40 C 30 18 20 -10 0 -20 Z" fill="#C9822A"/>
<circle cx="0" cy="34" r="15" fill="#2B1A12"/><circle cx="0" cy="34" r="19" fill="none" stroke="#6B3E26" stroke-width="3"/>
<rect x="-20" y="78" width="40" height="8" rx="3" fill="#2B1A12"/>
<g stroke="#F6EDE0" stroke-width="1">{strings}</g>
</g>""".format(frets="".join(f'<rect x="-7" y="{-140 + i * 16}" width="14" height="2"/>' for i in range(8)),
               strings="".join(f'<line x1="{-4.5 + i * 1.8:.1f}" y1="-150" x2="{-4.5 + i * 1.8:.1f}" y2="82"/>' for i in range(6)))
    notes = ('<g fill="#F6D58E"><path d="M 120 150 L 120 112 L 146 104 L 146 142" fill="none" stroke="#F6D58E" stroke-width="4"/><ellipse cx="114" cy="152" rx="9" ry="7"/><ellipse cx="140" cy="144" rx="9" ry="7"/>'
             '<path d="M 400 120 L 400 92" stroke="#F6D58E" stroke-width="4"/><ellipse cx="394" cy="122" rx="8" ry="6"/><path d="M 400 92 q 12 6 10 20" fill="none" stroke="#F6D58E" stroke-width="4"/></g>')
    bridge = ('<rect x="0" y="356" width="600" height="8" fill="#2A2238"/>'
              + "".join(f'<path d="M {x} 356 L {x + 30} 336 L {x + 60} 356" fill="none" stroke="#2A2238" stroke-width="3"/>' for x in range(0, 600, 60))
              + '<line x1="0" y1="336" x2="600" y2="336" stroke="#2A2238" stroke-width="3"/>')
    return f"""
{sky_}
{stars(4, 40, "#F6EDE0", box=(0, 40, 600, 150))}
{sun(300, 280, 70, "#F7B26A", halo="#F3A16B")}
{notes}
<polygon points="{P(skyline)}" fill="#1E1A30"/>
{lights}
{bridge}
{water(364, "#3A3358", "#6C5C8A", [(40, 390, 50), (200, 410, 60), (330, 384, 40), (90, 428, 40)])}
<g fill="#F7C873" opacity="0.7"><rect x="270" y="372" width="30" height="3"/><rect x="280" y="386" width="18" height="3"/><rect x="290" y="400" width="24" height="3"/></g>
{guitar}
"""


def new_orleans():
    def building(x, w, top, wall, trim, shutter, rail="#2B2B2B"):
        out = [f'<rect x="{x}" y="{top}" width="{w}" height="{400 - top}" fill="{wall}"/>',
               f'<rect x="{x - 3}" y="{top - 8}" width="{w + 6}" height="9" fill="{trim}"/>']
        for j, y in enumerate((top + 24, top + 104)):
            for i in range(3):
                wx = x + 14 + i * (w - 28) / 3 + ((w - 28) / 3 - 18) / 2
                out.append(f'<rect x="{wx:.1f}" y="{y}" width="18" height="44" fill="#3A2E2A"/>')
                out.append(f'<rect x="{wx - 8:.1f}" y="{y}" width="7" height="44" fill="{shutter}"/><rect x="{wx + 19:.1f}" y="{y}" width="7" height="44" fill="{shutter}"/>')
            # balcony with iron lace
            by = y + 50
            out.append(f'<rect x="{x - 6}" y="{by}" width="{w + 12}" height="5" fill="{rail}"/>')
            out.append(f'<rect x="{x - 6}" y="{by - 26}" width="{w + 12}" height="3" fill="{rail}"/>')
            out.append(f'<g stroke="{rail}" stroke-width="1.6">' + "".join(f'<line x1="{bx}" y1="{by - 24}" x2="{bx}" y2="{by}"/>' for bx in range(x - 4, x + w + 6, 6)) + "</g>")
            out.append(f'<g fill="none" stroke="{rail}" stroke-width="1.6">' + "".join(f'<circle cx="{bx + 3}" cy="{by - 12}" r="3"/>' for bx in range(x - 4, x + w + 2, 12)) + "</g>")
            out.append(f'<g fill="#4F7A3C">' + "".join(f'<path d="M {fx} {by + 5} q -8 14 -4 22 q 4 -6 4 -10 q 2 10 6 12 q 2 -12 -6 -24 Z"/>' for fx in (x + 10, x + w - 10)) + "</g>")
        out.append(f'<path d="M {x + w / 2 - 14} 400 L {x + w / 2 - 14} 370 Q {x + w / 2} 356 {x + w / 2 + 14} 370 L {x + w / 2 + 14} 400 Z" fill="#3A2E2A"/>')
        return "".join(out)
    cathedral = ('<g fill="#F3EEE4"><rect x="250" y="150" width="100" height="120"/><polygon points="250,150 300,120 350,150"/>'
                 '<rect x="232" y="110" width="26" height="160"/><polygon points="232,110 245,70 258,110"/>'
                 '<rect x="287" y="84" width="26" height="70"/><polygon points="287,84 300,40 313,84"/>'
                 '<rect x="342" y="110" width="26" height="160"/><polygon points="342,110 355,70 368,110"/></g>'
                 '<g fill="#9AA6B8"><polygon points="245,70 258,110 245,110"/><polygon points="300,40 313,84 300,84"/><polygon points="355,70 368,110 355,110"/></g>'
                 '<circle cx="300" cy="118" r="8" fill="#9AA6B8"/>')
    streetcar = ('<g transform="translate(330 352)"><rect x="0" y="0" width="230" height="58" rx="8" fill="#3E7A4A"/>'
                 '<rect x="-4" y="-8" width="238" height="12" rx="6" fill="#B8352E"/>'
                 + "".join(f'<rect x="{12 + i * 30}" y="10" width="22" height="20" rx="3" fill="#F6E7C1"/>' for i in range(7))
                 + '<rect x="0" y="36" width="230" height="5" fill="#E9C46A"/><line x1="115" y1="-8" x2="150" y2="-60" stroke="#2B2B2B" stroke-width="3"/>'
                 '<circle cx="40" cy="62" r="9" fill="#2B2B2B"/><circle cx="190" cy="62" r="9" fill="#2B2B2B"/></g>')
    lamp = ('<rect x="300" y="300" width="5" height="110" fill="#2B2B2B"/><path d="M 292 300 L 313 300 L 309 280 L 296 280 Z" fill="#2B2B2B"/>'
            '<rect x="297" y="284" width="11" height="13" fill="#F7C873"/>')
    return f"""
{sky_curved([(0, "#F6D9C2"), (160, "#F8E3C8")])}
{sun(460, 120, 46, "#F4B36B", halo="#F6C690")}
{birds([(120, 90, 14), (146, 102, 10)], "#4B2C64")}
<g transform="translate(0 58)">{cathedral}</g>
{building(10, 140, 190, "#E7B7C9", "#F6EFE0", "#4B7B6B")}
{building(160, 120, 210, "#F2D58A", "#F6EFE0", "#5B3A7A")}
{building(390, 130, 200, "#9FC6C0", "#F6EFE0", "#B8352E")}
{building(530, 120, 186, "#B7A6D9", "#F6EFE0", "#3E7A4A")}
<rect x="0" y="400" width="600" height="44" fill="#8A7E74"/>
<g stroke="#A4988D" stroke-width="2"><line x1="0" y1="414" x2="600" y2="414"/><line x1="0" y1="430" x2="600" y2="430"/></g>
{lamp}
{streetcar}
<g fill="#5B3A7A"><circle cx="40" cy="430" r="5"/><circle cx="52" cy="434" r="5"/></g><g fill="#E9C46A"><circle cx="64" cy="430" r="5"/></g><g fill="#3E7A4A"><circle cx="76" cy="434" r="5"/></g>
"""


def charleston():
    colors = [("#E9A9A0", "#B76D63"), ("#F3D483", "#C99A3A"), ("#A9CDE0", "#5E8FB0"), ("#BFD6A8", "#6E8F55"), ("#D6C0E6", "#8A6BB0"), ("#F6C7A1", "#C98250")]
    houses = []
    x = 0
    for i, (wall, dark) in enumerate(colors):
        w = 100
        top = 176 + (i % 2) * 22
        houses.append(f'<rect x="{x}" y="{top}" width="{w}" height="{390 - top}" fill="{wall}"/>')
        houses.append(f'<rect x="{x}" y="{top - 14}" width="{w}" height="16" fill="{dark}"/>')
        houses.append(f'<rect x="{x - 2}" y="{top + 2}" width="{w + 4}" height="5" fill="#FBF6EE"/>')
        houses.append(windows(x + 8, top + 18, w - 16, 150, 3, 2, "#FBF6EE", ww=18, wh=36))
        houses.append(windows(x + 12, top + 24, w - 24, 150, 3, 2, "#3F4B5A", ww=10, wh=26))
        houses.append(f'<rect x="{x + w / 2 - 12}" y="{340}" width="24" height="50" fill="#3F4B5A"/><rect x="{x + w / 2 - 16}" y="{336}" width="32" height="6" fill="#FBF6EE"/>')
        houses.append(f'<path d="M {x + w / 2 - 12} 340 A 12 12 0 0 1 {x + w / 2 + 12} 340 Z" fill="#FBF6EE"/>')
        x += w
    palmetto = palm(470, 420, 230, "#7A6A50", "#2F5D46", lean=-0.6, fronds=9)
    return f"""
{sky_curved([(0, "#CFE6EE"), (180, "#E4F0EC")])}
<g fill="#FBF6EE"><path d="M 470 96 A 34 34 0 1 0 506 140 A 26 26 0 1 1 470 96 Z"/></g>
{cloud(150, 110, 120, "#FFFFFF")}{cloud(340, 80, 90, "#FFFFFF")}
{"".join(houses)}
<rect x="0" y="388" width="600" height="56" fill="#B9A58E"/>
<g fill="#A69079">{"".join(f'<rect x="{x}" y="{y}" width="26" height="9" rx="4"/>' for y in (398, 414, 430) for x in range(-10 + (y % 3) * 12, 600, 34))}</g>
{palmetto}
<g fill="#4E7A52">{"".join(f'<circle cx="{x}" cy="384" r="{r}"/>' for x, r in ((30, 14), (52, 10), (230, 12), (252, 14), (360, 10), (380, 13)))}</g>
"""


def las_vegas():
    mtn = ridge([(0, 300), (80, 250), (150, 286), (230, 230), (300, 280), (380, 240), (460, 290), (540, 250), (600, 280)], 360, "#6B4A8C")
    towers = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{370 - y}" fill="{c}"/>' for x, y, w, c in (
        (40, 230, 40, "#3A2A5A"), (90, 200, 30, "#3A2A5A"), (130, 250, 50, "#2E2248"), (420, 210, 36, "#3A2A5A"), (466, 240, 50, "#2E2248"), (528, 190, 30, "#3A2A5A")))
    lit = "".join(f'<rect x="{x}" y="{y}" width="4" height="4" fill="{c}"/>' for x, y, c in (
        (48, 250, "#FF7AB6"), (60, 280, "#6FE3D7"), (100, 220, "#F7C873"), (106, 260, "#FF7AB6"), (146, 270, "#6FE3D7"), (160, 300, "#F7C873"),
        (430, 230, "#F7C873"), (440, 270, "#FF7AB6"), (480, 260, "#6FE3D7"), (500, 290, "#F7C873"), (536, 210, "#FF7AB6"), (540, 250, "#6FE3D7")))
    sign = """
<g transform="translate(300 250)">
<rect x="-6" y="40" width="12" height="96" fill="#C9C2D6"/>
<path d="M -110 -20 L 0 -70 L 110 -20 L 110 30 L 0 60 L -110 30 Z" fill="#FBF6EE"/>
<path d="M -100 -16 L 0 -60 L 100 -16 L 100 26 L 0 52 L -100 26 Z" fill="none" stroke="#E2384B" stroke-width="3"/>
<text x="0" y="-24" text-anchor="middle" font-family="'DM Mono', monospace" font-weight="500" font-size="15" letter-spacing="3" fill="#2E5EA8">WELCOME</text>
<text x="0" y="14" text-anchor="middle" font-family="Anton, Impact, sans-serif" font-size="34" letter-spacing="1" fill="#E2384B">LAS VEGAS</text>
<polygon points="{star}" fill="#F7C531"/>
</g>""".format(star=" ".join(f"{0 + (22 if i % 2 == 0 else 9) * math.cos(math.radians(-90 + i * 36)):.1f},{-88 + (22 if i % 2 == 0 else 9) * math.sin(math.radians(-90 + i * 36)):.1f}" for i in range(10)))
    bulbs = "".join(f'<circle cx="{300 + x:.1f}" cy="{250 + y:.1f}" r="3.2" fill="#F7C531"/>' for x, y in
                    [(-110 + i * 22, -20 - (i if i <= 5 else 10 - i) * 10) for i in range(11)] + [(-110 + i * 22, 30 + (i if i <= 5 else 10 - i) * 6) for i in range(11)])
    cactus = ('<g fill="#2F5D46"><rect x="96" y="330" width="22" height="90" rx="11"/><rect x="70" y="350" width="14" height="40" rx="7"/><rect x="70" y="378" width="34" height="12" rx="6"/>'
              '<rect x="128" y="340" width="14" height="36" rx="7"/><rect x="110" y="364" width="32" height="12" rx="6"/></g>')
    return f"""
{sky_curved([(0, "#1F1640"), (120, "#3A2468"), (220, "#8C3F7A"), (290, "#E2707A")])}
{stars(9, 60, "#FBF6EE", box=(0, 40, 600, 200))}
{mtn}
{towers}{lit}
{sign}{bulbs}
<rect x="0" y="370" width="600" height="74" fill="#E2A36B"/>
<path d="M 0 400 Q 300 380 600 404 L 600 444 L 0 444 Z" fill="#D18E57"/>
{cactus}
<g transform="translate(400 0)">{cactus.replace('fill="#2F5D46"', 'fill="#3B6E52"')}</g>
"""


def seattle():
    rainier = ridge([(60, 300), (190, 196), (230, 176), (262, 186), (400, 300)], 330, "#7E93B4")
    snow = '<polygon points="190,196 230,176 262,186 300,214 280,218 262,206 246,222 228,206 210,222 196,212 172,218" fill="#FFFFFF"/>'
    needle = ('<g fill="#F6EFE0">'
              '<path d="M 400 400 Q 418 320 424 206 L 432 206 Q 432 320 446 400 Z"/>'
              '<path d="M 470 400 Q 452 320 446 206 L 438 206 Q 442 320 456 400 Z"/>'
              '</g>'
              '<rect x="420" y="296" width="40" height="5" fill="#F6EFE0"/>'
              '<ellipse cx="435" cy="196" rx="62" ry="12" fill="#F6EFE0"/><ellipse cx="435" cy="200" rx="58" ry="7" fill="#C9C2B4"/>'
              '<path d="M 404 190 L 412 174 L 458 174 L 466 190 Z" fill="#E6B34A"/><ellipse cx="435" cy="174" rx="24" ry="5" fill="#F6EFE0"/>'
              '<rect x="433" y="110" width="4" height="64" fill="#F6EFE0"/><rect x="430" y="132" width="10" height="5" fill="#F6EFE0"/>')
    ferry = ('<g transform="translate(110 386)"><path d="M 0 0 L 150 0 L 138 18 L 10 18 Z" fill="#FBF6EE"/><rect x="18" y="-16" width="110" height="16" fill="#FBF6EE"/>'
             '<rect x="18" y="-4" width="110" height="4" fill="#2F6B4F"/>' + "".join(f'<rect x="{24 + i * 14}" y="-12" width="8" height="6" fill="#2F6B4F"/>' for i in range(8)) +
             '<rect x="56" y="-30" width="34" height="14" fill="#FBF6EE"/><rect x="66" y="-40" width="12" height="10" fill="#2F6B4F"/></g>')
    skyline = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{360 - y}" fill="#3F5F6B"/>' for x, y, w in (
        (300, 280, 30), (334, 250, 24), (362, 300, 26), (480, 270, 30), (514, 240, 22), (540, 290, 34), (576, 260, 24)))
    return f"""
{sky_curved([(0, "#BFDCE3"), (200, "#D7E9E6")])}
{cloud(110, 110, 120, "#FFFFFF")}{cloud(520, 90, 90, "#FFFFFF")}
{rainier}{snow}
{hills(326, 6, "#5E8C74", waves=4)}
{skyline}
{"".join(pine(x, 366, h, "#2F5D46", "#244A38") for x, h in ((30, 110), (64, 84), (562, 96), (590, 120), (270, 70)))}
{needle}
{water(362, "#3F7A86", "#77A9B0", [(30, 380, 50), (300, 420, 60), (480, 396, 50), (200, 434, 40)])}
{ferry}
"""


def boston():
    def brownstone(x, w, top, wall, trim):
        return (f'<rect x="{x}" y="{top}" width="{w}" height="{400 - top}" fill="{wall}"/><rect x="{x - 3}" y="{top - 8}" width="{w + 6}" height="10" fill="{trim}"/>'
                f'<path d="M {x + 8} {top + 40} L {x + 8} {top + 150} L {x + 52} {top + 150} L {x + 52} {top + 40} Q {x + 30} {top + 24} {x + 8} {top + 40} Z" fill="{wall}" stroke="{trim}" stroke-width="4"/>'
                + windows(x + 10, top + 46, 40, 100, 2, 2, "#2E3A4A", ww=12, wh=30)
                + windows(x + 60, top + 30, w - 64, 130, 1, 3, "#2E3A4A", ww=16, wh=26)
                + f'<rect x="{x + 62}" y="{350}" width="22" height="50" fill="#1F2F4D"/><path d="M {x + 58} 350 A 15 15 0 0 1 {x + 88} 350 Z" fill="{trim}"/>'
                + f'<g stroke="#2B2B2B" stroke-width="2">' + "".join(f'<line x1="{x + 56 + i * 6}" y1="{386 + i * 4}" x2="{x + 56 + i * 6}" y2="400"/>' for i in range(4)) + "</g>")
    steeple = ('<g fill="#FBF6EE"><rect x="282" y="150" width="36" height="90"/><rect x="288" y="104" width="24" height="48"/><polygon points="288,104 300,40 312,104"/></g>'
               '<rect x="296" y="120" width="8" height="18" rx="4" fill="#2E3A4A"/><rect x="292" y="170" width="16" height="26" rx="8" fill="#2E3A4A"/>'
               '<rect x="276" y="148" width="48" height="6" fill="#C9C2B4"/><rect x="284" y="102" width="32" height="5" fill="#C9C2B4"/>')
    lamp = ('<rect x="290" y="300" width="5" height="100" fill="#2B2B2B"/><path d="M 282 300 L 303 300 L 299 278 L 286 278 Z" fill="#2B2B2B"/><rect x="287" y="282" width="11" height="14" fill="#F7C873"/>')
    return f"""
{sky_curved([(0, "#CADBE6"), (170, "#E3E9EA")])}
{cloud(140, 100, 110, "#FFFFFF")}{cloud(470, 120, 120, "#FFFFFF")}
{birds([(400, 70, 14), (426, 82, 10)], "#1F2F4D")}
<g transform="translate(300 240) scale(0.75) translate(-300 -240)">{steeple}</g>
<rect x="210" y="236" width="180" height="170" fill="#7A3F30"/>{windows(214, 240, 172, 120, 5, 3, "#E9C9A0", ww=12, wh=18)}
{brownstone(0, 110, 200, "#A9553C", "#E9DCC8")}{brownstone(108, 104, 214, "#8E4632", "#E9DCC8")}
{brownstone(386, 104, 210, "#9A4B36", "#E9DCC8")}{brownstone(488, 112, 196, "#A9553C", "#E9DCC8")}
{lamp}
<rect x="0" y="398" width="600" height="46" fill="#7E7368"/>
<g fill="#958A7E">{"".join(f'<rect x="{x}" y="{y}" width="24" height="8" rx="3"/>' for y in (406, 420, 434) for x in range(-8 + (y % 3) * 10, 600, 30))}</g>
<g fill="#4E7A52"><circle cx="230" cy="396" r="16"/><circle cx="370" cy="396" r="16"/><circle cx="214" cy="400" r="10"/><circle cx="386" cy="400" r="10"/></g>
"""


def philadelphia():
    hall = ('<rect x="150" y="250" width="300" height="140" fill="#B85C3E"/>'
            '<rect x="146" y="244" width="308" height="8" fill="#F3EEE4"/>'
            '<polygon points="150,244 450,244 430,226 170,226" fill="#5A4A44"/>'
            + windows(156, 258, 288, 126, 9, 2, "#F3EEE4", ww=16, wh=38)
            + windows(160, 262, 280, 118, 9, 2, "#3A4A5A", ww=10, wh=30)
            + '<rect x="262" y="140" width="76" height="250" fill="#B85C3E"/>'
              '<rect x="258" y="134" width="84" height="8" fill="#F3EEE4"/>'
              '<rect x="272" y="80" width="56" height="58" fill="#F3EEE4"/><rect x="268" y="76" width="64" height="6" fill="#D9D2C4"/>'
              '<circle cx="300" cy="110" r="16" fill="#FBF6EE" stroke="#3A4A5A" stroke-width="3"/>'
              '<g stroke="#3A4A5A" stroke-width="2.5" stroke-linecap="round"><line x1="300" y1="110" x2="300" y2="99"/><line x1="300" y1="110" x2="308" y2="114"/></g>'
              '<rect x="280" y="50" width="40" height="30" fill="#F3EEE4"/><path d="M 280 50 Q 300 30 320 50 Z" fill="#F3EEE4"/><rect x="298" y="14" width="4" height="26" fill="#D9D2C4"/>'
              '<rect x="286" y="56" width="10" height="18" rx="5" fill="#3A4A5A"/><rect x="304" y="56" width="10" height="18" rx="5" fill="#3A4A5A"/>'
              '<rect x="284" y="300" width="32" height="90" fill="#3A4A5A"/><path d="M 280 300 A 20 20 0 0 1 320 300 Z" fill="#F3EEE4"/>'
              + windows(266, 150, 68, 130, 1, 2, "#F3EEE4", ww=22, wh=40))
    bell = ('<g transform="translate(480 330)"><path d="M -30 40 Q -32 0 -18 -20 Q 0 -34 18 -20 Q 32 0 30 40 Z" fill="#8C6A3A"/>'
            '<rect x="-34" y="38" width="68" height="8" rx="3" fill="#6B4E2A"/><rect x="-4" y="-34" width="8" height="12" fill="#6B4E2A"/>'
            '<path d="M 4 -10 L -2 10 L 6 26" fill="none" stroke="#3A2A1A" stroke-width="2.5"/><path d="M -14 -6 Q -18 12 -16 30" fill="none" stroke="#B48A52" stroke-width="4" stroke-linecap="round"/></g>'
            '<rect x="440" y="376" width="80" height="14" fill="#F3EEE4"/>')
    return f"""
{sky_curved([(0, "#CFE0EA"), (180, "#E8EEE6")])}
{cloud(110, 110, 120, "#FFFFFF")}{cloud(500, 90, 100, "#FFFFFF")}
{birds([(420, 140, 14), (446, 152, 10)], "#3A4A5A")}
<g transform="translate(300 390) scale(0.8) translate(-300 -390)">{hall}</g>
{round_tree(80, 392, 46, "#4E7A52", "#3E6643")}{round_tree(130, 396, 32, "#5E8C5E", "#4E7A52")}
{round_tree(560, 394, 40, "#4E7A52", "#3E6643")}
<rect x="0" y="388" width="600" height="56" fill="#7FA36A"/>
<polygon points="270,388 330,388 360,444 240,444" fill="#D9CDB8"/>
{bell}
"""


def yellowstone():
    rings = "".join(f'<ellipse cx="300" cy="400" rx="{rx}" ry="{ry}" fill="{c}"/>' for rx, ry, c in (
        (300, 64, "#C96A2E"), (250, 52, "#E59A3A"), (200, 42, "#E9C94A"), (150, 32, "#9CC27A"), (110, 24, "#4FA7B8"), (66, 14, "#2F7EA6")))
    plume = ('<g fill="#FFFFFF"><ellipse cx="300" cy="300" rx="30" ry="70"/><circle cx="286" cy="226" r="34"/><circle cx="318" cy="200" r="38"/>'
             '<circle cx="290" cy="164" r="30"/><circle cx="330" cy="150" r="26"/><circle cx="306" cy="122" r="24"/></g>'
             '<g fill="#E8EEF2"><circle cx="330" cy="214" r="22"/><circle cx="340" cy="158" r="16"/><ellipse cx="312" cy="300" rx="14" ry="56"/></g>')
    bison = ('<g transform="translate(470 352)" fill="#3A2A20"><path d="M 0 0 Q 4 -36 36 -40 Q 66 -44 82 -24 Q 96 -26 100 -6 L 96 10 L 84 10 L 82 30 L 74 30 L 72 12 L 30 12 L 28 30 L 20 30 L 18 10 Q 2 10 0 0 Z"/>'
             '<path d="M 82 -24 Q 108 -30 112 -6 Q 108 6 96 4 Z"/><path d="M 104 -18 q 6 -8 2 -14" fill="none" stroke="#F3E6CF" stroke-width="2"/></g>')
    return f"""
{sky_curved([(0, "#A9D4DF"), (210, "#CBE5E2")])}
{ridge([(0, 250), (90, 190), (170, 232), (260, 176), (350, 236), (440, 186), (520, 230), (600, 200)], 330, "#7E99A8")}
{snowcap((260, 176), (236, 192), (288, 196), "#FFFFFF", drop=18)}{snowcap((440, 186), (414, 204), (466, 206), "#FFFFFF", drop=18)}
{"".join(pine(x, 340, h, "#2F5D46", "#244A38") for x, h in ((20, 100), (52, 80), (84, 110), (116, 76), (500, 90), (536, 110), (570, 84)))}
<rect x="0" y="330" width="600" height="114" fill="#D9C7A7"/>
{rings}
{plume}
<g fill="#FFFFFF" opacity="0.6"><circle cx="120" cy="330" r="14"/><circle cx="130" cy="316" r="10"/><circle cx="470" cy="320" r="10"/></g>
{bison}
"""


def yosemite():
    halfdome = ('<path d="M 300 330 L 300 150 Q 340 104 400 120 Q 470 140 520 230 L 560 330 Z" fill="#B9AFA6"/>'
                '<path d="M 300 330 L 300 150 Q 320 132 340 128 L 338 330 Z" fill="#9C928A"/>'
                '<path d="M 400 120 Q 470 140 520 230 L 560 330 L 470 330 Q 470 220 400 120 Z" fill="#CFC6BC"/>')
    elcap = ('<path d="M 40 330 L 60 160 Q 80 120 130 126 Q 170 132 186 200 L 210 330 Z" fill="#A79D94"/>'
             '<path d="M 130 126 Q 170 132 186 200 L 210 330 L 160 330 Q 168 210 130 126 Z" fill="#C2B9AF"/>')
    falls = ('<path d="M 236 140 L 250 140 L 252 250 L 238 250 Z" fill="#E8F2F5"/><path d="M 238 250 L 252 250 L 256 330 L 236 330 Z" fill="#DCEAF0"/>'
             '<ellipse cx="246" cy="330" rx="20" ry="7" fill="#FFFFFF"/>'
             '<path d="M 210 330 L 222 150 Q 236 128 270 130 L 290 330 Z" fill="#8E8580"/>'
             '<path d="M 236 140 L 250 140 L 252 250 L 238 250 Z" fill="#E8F2F5"/>')
    return f"""
{sky_curved([(0, "#F4C79A"), (120, "#F7D8B0"), (220, "#F9E6C8")])}
{sun(440, 100, 40, "#F8B470", halo="#F9C690")}
{birds([(160, 90, 14), (186, 100, 10)], "#4A3A30")}
{elcap}
{falls}
{halfdome}
{hills(320, 6, "#6E8F5E", waves=3)}
{"".join(pine(x, 380, h, "#2F5D46", "#244A38") for x, h in ((20, 120), (60, 96), (96, 130), (140, 90), (440, 100), (480, 130), (520, 96), (566, 124)))}
<rect x="0" y="372" width="600" height="72" fill="#8DAF6E"/>
<path d="M 160 444 Q 240 400 300 404 Q 380 410 430 444 Z" fill="#6FA0B4"/>
<g stroke="#A9CBD8" stroke-width="3" stroke-linecap="round"><line x1="250" y1="422" x2="290" y2="422"/><line x1="320" y1="432" x2="360" y2="432"/></g>
{grass_tufts([(60, 420), (110, 430), (480, 424), (530, 432)], "#5E8C4E")}
"""


def build():
    poster("places", "chicago", "CHICAGO", "ILLINOIS · EST. 1837", chicago(), "#2E3456", "#F6A26E", "#FBEDE4", "#F4C7C3")
    poster("places", "nashville", "NASHVILLE", "TENNESSEE · MUSIC CITY", nashville(), "#1E1A30", "#E8A33D", "#FBEDE4", "#F6D58E")
    poster("places", "new-orleans", "NEW ORLEANS", "LOUISIANA · EST. 1718", new_orleans(), "#4B2C64", "#E9C46A", "#FBF1E2", "#E9C46A")
    poster("places", "charleston", "CHARLESTON", "SOUTH CAROLINA · EST. 1670", charleston(), "#2F5D46", "#E9A9A0", "#FBF6EE", "#F3D483")
    poster("places", "las-vegas", "LAS VEGAS", "NEVADA · USA", las_vegas(), "#1F1640", "#FF7AB6", "#FBF6EE", "#6FE3D7")
    poster("places", "seattle", "SEATTLE", "WASHINGTON · EMERALD CITY", seattle(), "#24504A", "#E6B34A", "#F6EFE0", "#BFDCE3")
    poster("places", "boston", "BOSTON", "MASSACHUSETTS · EST. 1630", boston(), "#1F2F4D", "#A9553C", "#F6EFE0", "#E9C9A0")
    poster("places", "philadelphia", "PHILADELPHIA", "PENNSYLVANIA · EST. 1682", philadelphia(), "#5A2A22", "#F3EEE4", "#FBF1E2", "#E9C9A0")
    poster("places", "yellowstone", "YELLOWSTONE", "WYOMING · NATIONAL PARK", yellowstone(), "#3A4A3A", "#E59A3A", "#F6EFE0", "#E9C94A")
    poster("places", "yosemite", "YOSEMITE", "CALIFORNIA · NATIONAL PARK", yosemite(), "#3E4A3A", "#F4C79A", "#F6EFE0", "#F4C79A")


if __name__ == "__main__":
    build()
