"""World Places: colorful travel posters (drawn on a 600 x 444 canvas, top 40 px trimmed by the poster layout)."""
import math
from poster import poster


def P(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def ripples(spec, color, sw=3):
    return f'<g stroke="{color}" stroke-width="{sw}" stroke-linecap="round">' + "".join(
        f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}"/>' for x, y, w in spec) + "</g>"


def birds(spec, color):
    return "".join(f'<path d="M {x} {y} q {s * 0.5} {-s * 0.5} {s} 0 q {s * 0.5} {-s * 0.5} {s} 0" fill="none" stroke="{color}" stroke-width="2.4" stroke-linecap="round"/>'
                   for x, y, s in spec)


def cloud_band(x, y, w, h, color):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{color}"/>'


# ---------------------------------------------------------------- Paris
def paris():
    navy, lat = "#3B3858", "#57537A"
    roof_l = ("M 0 330 L 0 296 L 22 296 L 22 284 L 30 284 L 30 296 L 60 296 Q 70 278 92 278 Q 114 278 124 296 L 150 296 L 150 282 "
              "L 158 282 L 158 296 L 196 296 L 196 316 L 214 316 L 214 330 Z")
    roof_r = ("M 386 330 L 386 314 L 404 314 L 404 292 L 432 292 Q 442 276 462 276 Q 482 276 492 292 L 520 292 L 520 280 L 528 280 "
              "L 528 292 L 566 292 Q 582 282 600 286 L 600 330 Z")
    sacre = ('<g fill="#E7B3A4"><rect x="470" y="236" width="60" height="44"/><path d="M 474 238 Q 500 188 526 238 Z"/>'
             '<rect x="497" y="178" width="6" height="18"/><path d="M 458 254 Q 470 232 482 254 Z"/><path d="M 518 254 Q 530 232 542 254 Z"/></g>')
    windows = "".join(f'<rect x="{x}" y="{y}" width="7" height="11" rx="1" fill="#EEC2B5"/>'
                      for y in (304, 318) for x in list(range(10, 200, 18)) + list(range(398, 596, 18)))
    tower = (f'<path fill-rule="evenodd" fill="{navy}" d="M 210 392 C 250 352 270 300 283 236 L 291 112 L 309 112 L 317 236 '
             f'C 330 300 350 352 390 392 Z M 244 392 Q 300 326 356 392 Z M 279 296 L 321 296 L 311 250 L 289 250 Z"/>'
             f'<rect x="246" y="296" width="108" height="12" rx="2" fill="{navy}"/>'
             f'<rect x="240" y="292" width="120" height="5" fill="{navy}"/>'
             f'<rect x="273" y="238" width="54" height="9" rx="2" fill="{navy}"/>'
             f'<rect x="284" y="160" width="32" height="7" rx="2" fill="{navy}"/>'
             f'<rect x="291" y="146" width="18" height="14" fill="{navy}"/>'
             f'<rect x="297" y="92" width="6" height="56" fill="{navy}"/><rect x="299" y="66" width="2" height="28" fill="{navy}"/>')
    lattice = (f'<g stroke="{lat}" stroke-width="1.6">'
               '<line x1="232" y1="380" x2="262" y2="330"/><line x1="226" y1="350" x2="268" y2="372"/>'
               '<line x1="368" y1="380" x2="338" y2="330"/><line x1="374" y1="350" x2="332" y2="372"/>'
               '<line x1="262" y1="290" x2="282" y2="256"/><line x1="266" y1="258" x2="286" y2="286"/>'
               '<line x1="338" y1="290" x2="318" y2="256"/><line x1="334" y1="258" x2="314" y2="286"/>'
               '<line x1="286" y1="232" x2="296" y2="176"/><line x1="314" y1="232" x2="304" y2="176"/>'
               '<line x1="288" y1="204" x2="312" y2="204"/><line x1="290" y1="186" x2="310" y2="186"/></g>')
    trees = ('<g fill="#4F6B4A"><circle cx="40" cy="364" r="34"/><circle cx="92" cy="372" r="26"/><circle cx="512" cy="372" r="26"/><circle cx="566" cy="362" r="36"/></g>'
             '<g fill="#5F7D57"><circle cx="30" cy="354" r="20"/><circle cx="86" cy="364" r="14"/><circle cx="520" cy="362" r="14"/><circle cx="556" cy="350" r="20"/></g>')
    lamps = "".join(f'<rect x="{x}" y="346" width="3" height="34" fill="{navy}"/><rect x="{x - 4}" y="336" width="11" height="12" rx="2" fill="{navy}"/><rect x="{x - 1}" y="339" width="5" height="6" fill="#FBE2A6"/>'
                    for x in (150, 448))
    boat = ('<path d="M 96 414 L 236 414 Q 232 426 220 428 L 108 428 Q 98 424 96 414 Z" fill="#F6EFE0"/>'
            f'<rect x="112" y="404" width="104" height="11" rx="3" fill="#F6EFE0"/><rect x="96" y="418" width="140" height="3" fill="{navy}"/>'
            + "".join(f'<rect x="{x}" y="406" width="9" height="6" rx="1" fill="#8FB3C2"/>' for x in range(118, 210, 14)))
    return f"""
<rect width="600" height="444" fill="#F9D9C6"/>
<rect y="0" width="600" height="150" fill="#F7CBB7"/>
<circle cx="300" cy="226" r="128" fill="#F6B49E"/>
<circle cx="300" cy="226" r="112" fill="#F4A28C"/>
{cloud_band(60, 128, 170, 14, "#FCE6DA")}{cloud_band(390, 112, 150, 12, "#FCE6DA")}{cloud_band(420, 140, 90, 10, "#FCE6DA")}
{birds([(118, 84, 14), (146, 98, 10), (430, 76, 12)], navy)}
{sacre}
<path d="{roof_l}" fill="#E3A99B"/><path d="{roof_r}" fill="#E3A99B"/>
<rect x="0" y="328" width="600" height="56" fill="#D99586"/>
{windows}
<g fill="#C9806F">{"".join(f'<rect x="{x}" y="340" width="12" height="20" rx="6"/>' for x in list(range(14, 200, 26)) + list(range(400, 596, 26)))}</g>
{tower}
{lattice}
<rect x="0" y="380" width="600" height="12" fill="#C98775"/>
<g fill="#B87565">{"".join(f'<rect x="{x}" y="380" width="22" height="4"/>' for x in range(0, 600, 28))}</g>
{trees}{lamps}
<rect x="0" y="392" width="600" height="52" fill="#8FB3C2"/>
<path d="M 256 392 L 344 392 L 330 420 L 270 420 Z" fill="#7FA3B3"/>
{ripples([(30, 402, 40), (150, 438, 50), (300, 432, 40), (400, 404, 60), (520, 424, 44)], "#B9D3DE")}
{boat}
"""


# ---------------------------------------------------------------- Japan
def japan():
    def eave(cx, y, half):
        return (f'<path d="M {cx - half - 16} {y - 6} Q {cx - half} {y + 2} {cx - half + 10} {y + 2} L {cx + half - 10} {y + 2} '
                f'Q {cx + half} {y + 2} {cx + half + 16} {y - 6} L {cx + half - 4} {y - 14} L {cx - half + 4} {y - 14} Z" fill="#3A2A2A"/>')
    pagoda = []
    cx = 132
    for i, (y, half) in enumerate(((388, 44), (352, 39), (316, 34), (280, 29), (244, 24))):
        pagoda.append(f'<rect x="{cx - half + 8}" y="{y}" width="{2 * half - 16}" height="22" fill="#B23A30"/>')
        pagoda.append(f'<rect x="{cx - half + 8}" y="{y + 16}" width="{2 * half - 16}" height="6" fill="#8E2C25"/>')
        pagoda.append(f'<g fill="#F3E3C8">' + "".join(f'<rect x="{cx - half + 14 + k * 12}" y="{y + 4}" width="6" height="10"/>' for k in range(int((2 * half - 28) / 12) + 1)) + '</g>')
        pagoda.append(eave(cx, y, half + 4))
    pagoda.append(f'<rect x="{cx - 2}" y="196" width="4" height="40" fill="#E2B857"/>')
    pagoda.append("".join(f'<rect x="{cx - 6}" y="{y}" width="12" height="2.5" fill="#E2B857"/>' for y in (204, 212, 220, 228)))
    pagoda.append(f'<circle cx="{cx}" cy="194" r="4" fill="#E2B857"/>')

    def bloom(cx, cy, r):
        out = []
        for k, (dx, dy, rr, col) in enumerate(((0, 0, 1, "#F2A7B8"), (-0.6, 0.3, 0.75, "#F7C6D0"), (0.6, 0.25, 0.8, "#EE8FA5"),
                                                (-0.2, -0.5, 0.7, "#F7C6D0"), (0.35, -0.45, 0.6, "#F2A7B8"))):
            out.append(f'<circle cx="{cx + dx * r:.1f}" cy="{cy + dy * r:.1f}" r="{rr * r:.1f}" fill="{col}"/>')
        return "".join(out)
    petals = "".join(f'<ellipse cx="{x}" cy="{y}" rx="4" ry="2.4" transform="rotate({a} {x} {y})" fill="#F2A7B8"/>'
                     for x, y, a in ((250, 120, 30), (330, 300, -20), (390, 220, 50), (200, 260, 10), (470, 330, -40), (90, 150, 20)))
    return f"""
<rect width="600" height="444" fill="#F7E6CC"/>
<circle cx="440" cy="128" r="52" fill="#D8483B"/>
<path d="M 30 360 L 238 156 Q 300 118 362 156 L 570 360 Z" fill="#5F7BA3"/>
<path d="M 300 132 Q 330 136 362 156 L 570 360 L 300 360 Z" fill="#4E6890"/>
<path d="M 238 156 Q 300 118 362 156 L 396 190 L 372 182 L 356 202 L 334 186 L 314 208 L 296 188 L 276 206 L 260 186 L 238 200 L 226 186 L 204 190 Z" fill="#FFFFFF"/>
<path d="M 300 132 Q 330 136 362 156 L 396 190 L 372 182 L 356 202 L 334 186 L 314 208 L 300 192 Z" fill="#E4EAF2"/>
<g stroke="#C9D5E4" stroke-width="2" fill="none"><path d="M 280 150 L 266 180"/><path d="M 320 150 L 338 182"/></g>
{cloud_band(150, 236, 200, 16, "#FBF1E2")}{cloud_band(330, 254, 170, 14, "#FBF1E2")}{cloud_band(90, 262, 120, 12, "#FBF1E2")}
<path d="M 0 312 Q 120 286 260 302 Q 420 318 600 292 L 600 444 L 0 444 Z" fill="#8FA6BF"/>
<path d="M 0 338 {"".join(f"q 15 -16 30 0 " for _ in range(20))} L 600 444 L 0 444 Z" fill="#6F8E62"/>
<path d="M 0 372 Q 140 350 260 384 Q 380 412 600 376 L 600 444 L 0 444 Z" fill="#55724C"/>
{"".join(pagoda)}
<path d="M 600 60 Q 540 70 486 112 M 540 76 Q 520 54 500 50" fill="none" stroke="#5A3A2E" stroke-width="7" stroke-linecap="round"/>
<path d="M 0 74 Q 34 86 70 60 M 40 80 Q 58 102 84 106" fill="none" stroke="#5A3A2E" stroke-width="6" stroke-linecap="round"/>
{bloom(560, 50, 34)}{bloom(500, 92, 26)}{bloom(590, 112, 28)}{bloom(470, 126, 18)}
{bloom(36, 52, 32)}{bloom(80, 94, 24)}{bloom(6, 110, 26)}
<path d="M 600 444 L 600 330 Q 560 300 520 330 Q 500 350 470 360 Q 440 380 430 444 Z" fill="#4A6642"/>
<path d="M 520 444 Q 518 400 540 370" fill="none" stroke="#5A3A2E" stroke-width="8" stroke-linecap="round"/>
{bloom(540, 360, 30)}{bloom(500, 384, 22)}{bloom(584, 380, 26)}
{petals}
"""


# ---------------------------------------------------------------- Santorini
def santorini():
    white, shade, blue, pink = "#FBF7F0", "#EAD9CB", "#2E5EA8", "#D9467A"

    def house(x, y, w, h, door=True):
        out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{white}"/>',
               f'<rect x="{x + w - 14}" y="{y}" width="14" height="{h}" fill="{shade}"/>',
               f'<rect x="{x - 2}" y="{y - 4}" width="{w + 4}" height="5" rx="2" fill="{white}"/>']
        if door:
            out.append(f'<path d="M {x + 12} {y + h} L {x + 12} {y + h - 22} Q {x + 20} {y + h - 32} {x + 28} {y + h - 22} L {x + 28} {y + h} Z" fill="{blue}"/>')
        out.append(f'<rect x="{x + w - 34}" y="{y + 12}" width="12" height="14" rx="2" fill="{blue}"/>')
        return "".join(out)

    def dome(cx, base, r):
        return (f'<rect x="{cx - r}" y="{base}" width="{2 * r}" height="{r + 6}" fill="{white}"/>'
                f'<path d="M {cx - r} {base} A {r} {r} 0 0 1 {cx + r} {base} Z" fill="{blue}"/>'
                f'<path d="M {cx + r * 0.2:.1f} {base - r * 0.98:.1f} A {r} {r} 0 0 1 {cx + r} {base} L {cx + r * 0.45:.1f} {base} Z" fill="#244C8C"/>'
                f'<rect x="{cx - 1.5}" y="{base - r - 14}" width="3" height="14" fill="{white}"/><rect x="{cx - 5}" y="{base - r - 10}" width="10" height="3" fill="{white}"/>')
    village = "".join([
        house(30, 262, 80, 56), house(100, 232, 76, 60), house(160, 270, 70, 56), house(60, 300, 96, 50), house(230, 296, 90, 52),
        house(300, 262, 72, 48), house(150, 318, 84, 40), house(330, 312, 80, 42), house(400, 300, 66, 46, door=False),
    ])
    windmill = ('<rect x="40" y="196" width="34" height="58" fill="#FBF7F0"/><rect x="62" y="196" width="12" height="58" fill="#EAD9CB"/>'
                '<path d="M 36 198 Q 57 168 78 198 Z" fill="#B98060"/>'
                + "".join(f'<line x1="57" y1="186" x2="{57 + 46 * math.cos(math.radians(a)):.1f}" y2="{186 + 46 * math.sin(math.radians(a)):.1f}" stroke="#7A5638" stroke-width="2.5"/>'
                          f'<polygon points="{P([(57 + 20 * math.cos(math.radians(a)), 186 + 20 * math.sin(math.radians(a))), (57 + 44 * math.cos(math.radians(a)), 186 + 44 * math.sin(math.radians(a))), (57 + 44 * math.cos(math.radians(a + 14)), 186 + 44 * math.sin(math.radians(a + 14))), (57 + 22 * math.cos(math.radians(a + 18)), 186 + 22 * math.sin(math.radians(a + 18)))])}" fill="#FBF7F0" opacity="0.85"/>'
                          for a in range(0, 360, 60)))
    bougain = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x, y, r, c in (
        (112, 300, 12, pink), (124, 292, 9, "#E8679A"), (226, 316, 11, pink), (238, 308, 8, "#E8679A"), (316, 304, 10, pink),
        (30, 312, 10, "#E8679A"), (398, 296, 9, pink)))
    return f"""
<rect width="600" height="444" fill="#F6C28B"/>
<path d="M 0 150 Q 300 132 600 150 L 600 444 L 0 444 Z" fill="#F5AE84"/>
<path d="M 0 230 Q 300 214 600 230 L 600 444 L 0 444 Z" fill="#F1937E"/>
<circle cx="470" cy="300" r="44" fill="#FFE3A3"/>
{cloud_band(330, 170, 160, 10, "#F8C79B")}{cloud_band(420, 194, 120, 8, "#F8C79B")}
{birds([(360, 120, 12), (384, 132, 9)], "#7A3E46")}
<rect x="0" y="300" width="600" height="144" fill="#3E6E9E"/>
{ripples([(440, 314, 60), (452, 330, 40), (430, 348, 74), (448, 368, 44), (460, 388, 30)], "#F5A97F", 4)}
{ripples([(40, 410, 60), (220, 430, 40), (300, 392, 50)], "#6E95BE", 3)}
<path d="M 0 444 L 0 250 Q 60 236 120 222 Q 200 204 260 240 Q 330 262 400 276 Q 440 286 470 330 L 520 444 Z" fill="#A86F4C"/>
<path d="M 0 380 Q 120 360 240 384 Q 360 404 470 380 L 500 444 L 0 444 Z" fill="#94603F"/>
<path d="M 0 344 Q 100 330 200 350 Q 300 368 430 352" fill="none" stroke="#B98060" stroke-width="5"/>
{windmill}
{village}
{dome(204, 244, 26)}{dome(286, 260, 22)}{dome(380, 280, 18)}
<rect x="344" y="226" width="30" height="40" fill="{white}"/><path d="M 344 226 A 15 15 0 0 1 374 226 Z" fill="{blue}"/>
<path d="M 351 254 L 351 240 Q 359 230 367 240 L 367 254 Z" fill="#A86F4C"/>
{bougain}
<path d="M 506 384 L 568 384 L 558 396 L 516 396 Z" fill="#F6EFE0"/><path d="M 536 384 L 536 344 L 558 380 Z" fill="#F6EFE0"/><path d="M 534 384 L 534 352 L 516 380 Z" fill="#F6EFE0" opacity="0.8"/>
"""


# ---------------------------------------------------------------- Rome
def rome():
    stone, shade, dark, light = "#DDA06A", "#C9875A", "#9C5532", "#EBB987"
    out = ['<rect width="600" height="444" fill="#F7DCAE"/>', '<circle cx="230" cy="170" r="130" fill="#F0A65E"/>',
           cloud_band(380, 96, 150, 12, "#FBE7C6"), cloud_band(430, 120, 100, 10, "#FBE7C6"),
           birds([(420, 160, 12), (446, 172, 9)], "#7A2E22")]
    body = ("M 90 380 L 90 236 Q 120 222 160 218 L 160 200 Q 300 182 440 200 L 440 214 L 470 220 L 470 250 L 500 256 L 500 288 L 520 292 L 520 380 Z")
    out.append(f'<path d="{body}" fill="{stone}"/>')
    out.append(f'<path d="M 400 196 Q 430 200 440 200 L 440 214 L 470 220 L 470 250 L 500 256 L 500 288 L 520 292 L 520 380 L 400 380 Z" fill="{shade}"/>')
    for y, h in ((326, 44), (272, 40), (222, 36)):
        for x in range(104, 500, 36):
            if y == 222 and (x < 168 or x > 420):
                continue
            if y == 272 and x > 470:
                continue
            out.append(f'<path d="M {x} {y + h} L {x} {y + 12} Q {x + 11} {y} {x + 22} {y + 12} L {x + 22} {y + h} Z" fill="{dark}"/>')
            out.append(f'<rect x="{x + 25}" y="{y + 4}" width="7" height="{h - 4}" fill="{light}"/>')
        out.append(f'<rect x="90" y="{y + h}" width="430" height="7" fill="{shade}"/>')
    for x in range(176, 430, 30):
        out.append(f'<rect x="{x}" y="196" width="12" height="16" fill="{dark}"/>')
    out.append(f'<path d="M 90 236 L 90 380 L 104 380 L 104 248 Z" fill="{shade}"/>')
    out.append('<rect x="0" y="378" width="600" height="66" fill="#CDB58C"/>')
    out.append('<path d="M 0 400 Q 300 390 600 404 L 600 444 L 0 444 Z" fill="#BFA478"/>')
    out.append('<g fill="#3E5A3A"><ellipse cx="30" cy="290" rx="14" ry="72"/><ellipse cx="56" cy="306" rx="11" ry="58"/></g>')

    def pine(x, base, top, w):
        cx, cy = x + 22, top + 10
        return (f'<path d="M {x} {base} Q {x + 8} {(base + top) / 2} {cx} {cy}" fill="none" stroke="#5A3A2E" stroke-width="7" stroke-linecap="round"/>'
                f'<path d="M {cx} {cy} L {cx - w * 0.5:.1f} {cy - 6}" stroke="#5A3A2E" stroke-width="4" stroke-linecap="round"/>'
                f'<path d="M {cx + 2} {cy} L {cx + w * 0.45:.1f} {cy - 8}" stroke="#5A3A2E" stroke-width="4" stroke-linecap="round"/>'
                f'<path d="M {cx - w} {cy - 4} Q {cx - w} {cy - 30} {cx - w * 0.6:.1f} {cy - 34} Q {cx - w * 0.3:.1f} {cy - 54} {cx} {cy - 46} '
                f'Q {cx + w * 0.35:.1f} {cy - 58} {cx + w * 0.66:.1f} {cy - 38} Q {cx + w} {cy - 32} {cx + w} {cy - 4} Q {cx} {cy + 6} {cx - w} {cy - 4} Z" fill="#41603F"/>'
                f'<path d="M {cx - w * 0.75:.1f} {cy - 12} Q {cx} {cy - 2} {cx + w * 0.8:.1f} {cy - 12} Q {cx + w * 0.8:.1f} {cy - 4} {cx} {cy + 2} Q {cx - w * 0.8:.1f} {cy - 4} {cx - w * 0.75:.1f} {cy - 12} Z" fill="#33502F"/>'
                f'<path d="M {cx - w * 0.55:.1f} {cy - 32} Q {cx - w * 0.2:.1f} {cy - 46} {cx + w * 0.1:.1f} {cy - 40}" fill="none" stroke="#5B7E55" stroke-width="5" stroke-linecap="round"/>')
    out.append(pine(530, 410, 250, 62))
    out.append(pine(60, 420, 300, 46))
    vespa = ('<g transform="translate(386 386)"><circle cx="0" cy="26" r="11" fill="#2B2B2B"/><circle cx="58" cy="26" r="11" fill="#2B2B2B"/>'
             '<circle cx="0" cy="26" r="4" fill="#CDB58C"/><circle cx="58" cy="26" r="4" fill="#CDB58C"/>'
             '<path d="M -10 22 Q -8 4 14 2 L 34 2 Q 42 -14 52 -16 L 56 -16 L 58 -8 Q 70 4 70 22 Z" fill="#C8322E"/>'
             '<rect x="14" y="-6" width="24" height="7" rx="3" fill="#5A3A2E"/><path d="M 50 -16 L 46 -32 L 56 -34" fill="none" stroke="#2B2B2B" stroke-width="3" stroke-linecap="round"/>'
             '<circle cx="64" cy="4" r="3" fill="#FBE7C6"/></g>')
    out.append(vespa)
    return "\n".join(out)


# ---------------------------------------------------------------- London
def london():
    gold, stone, dark, slate = "#E2B857", "#C9A06A", "#A9804B", "#3E4A52"
    out = ['<rect width="600" height="444" fill="#D9E4EA"/>',
           '<g fill="#FFFFFF"><ellipse cx="110" cy="106" rx="64" ry="20"/><ellipse cx="150" cy="92" rx="42" ry="22"/><ellipse cx="480" cy="120" rx="60" ry="18"/><ellipse cx="510" cy="108" rx="34" ry="18"/></g>',
           birds([(380, 90, 14), (406, 102, 10)], "#3E4A52")]
    # Victoria Tower (left) and the long Palace facade
    out.append(f'<rect x="20" y="170" width="70" height="200" fill="{dark}"/><g fill="{slate}">' + "".join(f'<rect x="{x}" y="156" width="6" height="16"/>' for x in (20, 40, 64, 84)) + '</g>')
    out.append(f'<rect x="0" y="250" width="600" height="130" fill="{stone}"/>')
    out.append(f'<g fill="{dark}">' + "".join(f'<rect x="{x}" y="236" width="6" height="18"/><path d="M {x - 1} 236 L {x + 3} 226 L {x + 7} 236 Z"/>' for x in range(4, 600, 28) if not 214 < x < 340) + '</g>')
    out.append(f'<g fill="{dark}">' + "".join(f'<path d="M {x} 318 L {x} 278 Q {x + 7} 268 {x + 14} 278 L {x + 14} 318 Z"/>' for x in range(10, 600, 26) if not 210 < x < 340) + '</g>')
    out.append(f'<rect x="0" y="330" width="600" height="6" fill="{dark}"/>')
    out.append(f'<g fill="{dark}" opacity="0.8">' + "".join(f'<rect x="{x}" y="344" width="10" height="20" rx="5"/>' for x in range(12, 600, 26)) + '</g>')
    # Elizabeth Tower
    out.append(f'<rect x="232" y="132" width="96" height="248" fill="{stone}"/>')
    out.append(f'<rect x="312" y="132" width="16" height="248" fill="{dark}"/>')
    out.append(f'<g fill="{dark}">' + "".join(f'<rect x="{x}" y="230" width="8" height="140" rx="4"/>' for x in (246, 266, 286, 300)) + '</g>')
    out.append(f'<rect x="226" y="124" width="108" height="14" fill="{dark}"/>')
    out.append(f'<rect x="240" y="88" width="80" height="38" fill="{stone}"/><g fill="{dark}">' + "".join(f'<path d="M {x} 124 L {x} 104 Q {x + 6} 96 {x + 12} 104 L {x + 12} 124 Z"/>' for x in (250, 268, 286, 304)) + '</g>')
    out.append(f'<path d="M 236 90 L 280 52 L 324 90 Z" fill="{slate}"/><path d="M 280 52 L 324 90 L 296 90 Z" fill="#2E3940"/>')
    out.append(f'<rect x="278" y="36" width="4" height="18" fill="{gold}"/><circle cx="280" cy="36" r="4" fill="{gold}"/>')
    out.append(f'<g fill="{gold}"><rect x="234" y="84" width="4" height="10"/><rect x="322" y="84" width="4" height="10"/></g>')
    out.append(f'<rect x="242" y="146" width="76" height="76" fill="{gold}"/>')
    out.append('<circle cx="280" cy="184" r="32" fill="#F6EFE0"/><circle cx="280" cy="184" r="32" fill="none" stroke="#2E3940" stroke-width="3"/>')
    out.append('<g stroke="#2E3940" stroke-width="2">' + "".join(f'<line x1="{280 + 26 * math.cos(math.radians(a)):.1f}" y1="{184 + 26 * math.sin(math.radians(a)):.1f}" x2="{280 + 30 * math.cos(math.radians(a)):.1f}" y2="{184 + 30 * math.sin(math.radians(a)):.1f}"/>' for a in range(0, 360, 30)) + '</g>')
    out.append('<g stroke="#2E3940" stroke-width="4" stroke-linecap="round"><line x1="280" y1="184" x2="280" y2="162"/><line x1="280" y1="184" x2="296" y2="192"/></g>')
    # Westminster Bridge, river and bus
    out.append('<rect x="0" y="380" width="600" height="64" fill="#6E8794"/>')
    out.append('<rect x="0" y="366" width="600" height="14" fill="#3F6E5A"/><g fill="#6E8794">' + "".join(f'<path d="M {x} 380 Q {x + 30} 366 {x + 60} 380 Z"/>' for x in range(-20, 600, 80)) + '</g>')
    out.append('<g fill="#3F6E5A">' + "".join(f'<rect x="{x}" y="350" width="4" height="16"/><circle cx="{x + 2}" cy="348" r="4"/>' for x in range(40, 600, 80)) + '</g>')
    out.append(ripples([(40, 404, 50), (180, 430, 60), (330, 410, 40), (470, 434, 50)], "#9DB3BE"))
    bus = ('<g transform="translate(372 290)"><rect x="0" y="0" width="186" height="78" rx="10" fill="#C8322E"/>'
           '<rect x="0" y="36" width="186" height="5" fill="#9E2420"/>'
           + "".join(f'<rect x="{x}" y="8" width="22" height="18" rx="3" fill="#F6EFE0"/><rect x="{x}" y="46" width="22" height="16" rx="3" fill="#F6EFE0"/>' for x in range(12, 180, 30))
           + '<rect x="8" y="64" width="40" height="6" rx="2" fill="#F6EFE0"/>'
           '<circle cx="36" cy="80" r="12" fill="#2B2B2B"/><circle cx="150" cy="80" r="12" fill="#2B2B2B"/><circle cx="36" cy="80" r="5" fill="#9DA4A8"/><circle cx="150" cy="80" r="5" fill="#9DA4A8"/></g>')
    out.append(bus)
    booth = ('<g transform="translate(120 286)"><rect x="0" y="0" width="40" height="84" rx="4" fill="#C8322E"/><rect x="-2" y="-6" width="44" height="10" rx="4" fill="#C8322E"/>'
             '<rect x="4" y="6" width="32" height="7" fill="#F6EFE0"/>' + "".join(f'<rect x="{6 + i * 10}" y="{18 + j * 12}" width="8" height="10" fill="#F6EFE0" opacity="0.85"/>' for i in range(3) for j in range(4)) + '</g>')
    out.append(booth)
    return "\n".join(out)


# ---------------------------------------------------------------- Cairo
def cairo():
    def pyramid(apex_x, apex_y, base_l, base_r, base_y, lit, shade):
        out = [f'<polygon points="{P([(base_l, base_y), (apex_x, apex_y), (base_r, base_y)])}" fill="{lit}"/>',
               f'<polygon points="{P([(apex_x, apex_y), (base_r, base_y), (apex_x + (base_r - apex_x) * 0.25, base_y)])}" fill="{shade}"/>']
        h = base_y - apex_y
        for k in range(1, 9):
            y = apex_y + h * k / 9
            t = k / 9
            out.append(f'<line x1="{apex_x - (apex_x - base_l) * t:.1f}" y1="{y:.1f}" x2="{apex_x + (base_r - apex_x) * t:.1f}" y2="{y:.1f}" stroke="{shade}" stroke-width="1.4" opacity="0.55"/>')
        out.append(f'<polygon points="{P([(apex_x, apex_y), (apex_x - 9, apex_y + 12), (apex_x + 9, apex_y + 12)])}" fill="#F3D7A1"/>')
        return "".join(out)
    sphinx = ('<g transform="translate(70 318)"><path d="M 0 52 L 6 30 Q 30 20 70 24 L 108 26 Q 118 26 120 40 L 124 52 Z" fill="#C98F55"/>'
              '<path d="M 96 26 L 96 -6 Q 98 -22 112 -24 Q 126 -22 128 -6 L 130 30 L 96 30 Z" fill="#C98F55"/>'
              '<path d="M 92 -4 Q 112 -30 134 -4 L 138 26 L 130 26 L 128 0 L 98 0 L 96 26 L 88 26 Z" fill="#B67C44"/>'
              '<g stroke="#9E6A38" stroke-width="2">' + "".join(f'<line x1="89" y1="{y}" x2="97" y2="{y}"/><line x1="129" y1="{y}" x2="137" y2="{y}"/>' for y in range(2, 26, 5)) + '</g>'
              '<rect x="104" y="6" width="16" height="3" fill="#7A4E2A"/><path d="M 120 52 L 150 52 L 150 46 L 124 46 Z" fill="#C98F55"/></g>')

    def camel(x, y, s):
        return (f'<g transform="translate({x} {y}) scale({s})" fill="#5B3A22"><path d="M 0 0 Q 4 -16 18 -18 Q 26 -30 36 -18 Q 44 -26 52 -14 Q 58 -6 60 -2 L 70 -12 L 72 -30 L 82 -32 L 80 -22 L 76 -6 Q 68 6 60 8 L 58 34 L 53 34 L 52 12 L 22 12 L 20 34 L 15 34 L 14 10 Q 4 8 0 0 Z"/>'
                f'<path d="M 28 -22 L 30 -40 Q 36 -46 40 -40 L 40 -20 Z"/></g>')
    palms = "".join(f'<path d="M {x} 400 Q {x + 4} 360 {x - 4} 320" fill="none" stroke="#6B4A2E" stroke-width="6" stroke-linecap="round"/>'
                    + "".join(f'<path d="M {x - 4} 320 Q {x - 4 + dx * 0.6} {320 + dy * 0.6 - 12} {x - 4 + dx} {320 + dy} Q {x - 4 + dx * 0.5} {320 + dy * 0.5} {x - 4} 324 Z" fill="#5B7A3A"/>'
                              for dx, dy in ((-38, 10), (-30, -14), (0, -26), (30, -14), (40, 10)))
                    for x in (520, 556))
    return f"""
<rect width="600" height="444" fill="#FBDDA5"/>
<rect y="0" width="600" height="120" fill="#F9D194"/>
<circle cx="430" cy="214" r="118" fill="#F6A55A"/>
<circle cx="430" cy="214" r="100" fill="#F28C38"/>
{ripples([(330, 170, 80), (460, 150, 90), (500, 190, 70)], "#FBDDA5", 4)}
{birds([(140, 120, 14), (168, 132, 10)], "#5B3A22")}
{pyramid(470, 222, 400, 560, 340, "#D9A35F", "#B97E3E")}
{pyramid(300, 120, 140, 460, 340, "#E0AC66", "#B97E3E")}
{pyramid(150, 246, 80, 220, 340, "#D9A35F", "#B97E3E")}
<path d="M 0 330 Q 150 304 300 330 Q 450 356 600 318 L 600 444 L 0 444 Z" fill="#E8B977"/>
{camel(360, 342, 0.8)}{camel(430, 350, 0.7)}
{sphinx}
<path d="M 0 392 Q 200 362 400 390 Q 500 404 600 376 L 600 444 L 0 444 Z" fill="#DDA766"/>
{palms}
<path d="M 0 424 Q 200 410 400 428 L 400 444 L 0 444 Z" fill="#D29A5A"/>
"""


# ---------------------------------------------------------------- Sydney
def sydney():
    def sail(x0, x1, top_x, top_y, base, face, shade):
        return (f'<path d="M {x0} {base} Q {x0 + 6} {top_y + 30} {top_x} {top_y} Q {x1 - 10} {top_y + 60} {x1} {base} Z" fill="{face}"/>'
                f'<path d="M {top_x} {top_y} Q {x1 - 10} {top_y + 60} {x1} {base} L {top_x + (x1 - top_x) * 0.45:.1f} {base} Q {top_x + 6} {top_y + 50} {top_x} {top_y} Z" fill="{shade}"/>'
                + "".join(f'<path d="M {top_x} {top_y} Q {x0 + (x1 - x0) * t + 4:.1f} {(top_y + base) / 2:.1f} {x0 + (x1 - x0) * t:.1f} {base}" fill="none" stroke="#D8CFC0" stroke-width="1.3"/>' for t in (0.3, 0.55, 0.8)))
    sails = "".join([sail(150, 238, 222, 220, 338, "#FBF8F2", "#E6E0D4"), sail(214, 300, 286, 190, 338, "#FBF8F2", "#E6E0D4"),
                     sail(282, 352, 344, 222, 338, "#FBF8F2", "#E6E0D4"), sail(338, 400, 392, 252, 338, "#FBF8F2", "#E6E0D4"),
                     sail(386, 436, 430, 274, 338, "#FBF8F2", "#E6E0D4")])
    arch_pts = lambda r, k: [(450 + r * math.cos(math.radians(a)), 300 - k * r * math.sin(math.radians(a))) for a in range(0, 181, 6)]
    outer, inner = arch_pts(170, 0.9), arch_pts(146, 0.9)
    truss = "".join(f'<line x1="{outer[i][0]:.1f}" y1="{outer[i][1]:.1f}" x2="{inner[i + 1][0]:.1f}" y2="{inner[i + 1][1]:.1f}"/>' for i in range(len(outer) - 1))
    hangers = "".join(f'<line x1="{x}" y1="{300 - 0.9 * math.sqrt(max(0, 146 ** 2 - (x - 450) ** 2)):.1f}" x2="{x}" y2="300"/>' for x in range(320, 590, 20))
    skyline = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{300 - y}" fill="#9CC4D6"/>' for x, y, w in (
        (20, 240, 26), (50, 210, 22), (76, 226, 30), (110, 196, 20), (134, 230, 26), (470, 220, 24), (520, 236, 30), (556, 206, 22)))
    return f"""
<rect width="600" height="444" fill="#BFE3EF"/>
<circle cx="120" cy="110" r="46" fill="#FFC857"/>
<g fill="#FFFFFF"><ellipse cx="420" cy="92" rx="60" ry="18"/><ellipse cx="452" cy="80" rx="36" ry="18"/></g>
{birds([(240, 120, 12), (264, 130, 9)], "#3B4A5A")}
{skyline}
<polyline points="{P(outer)}" fill="none" stroke="#3B4A5A" stroke-width="8"/>
<polyline points="{P(inner)}" fill="none" stroke="#3B4A5A" stroke-width="4"/>
<g stroke="#3B4A5A" stroke-width="2">{truss}</g>
<g stroke="#3B4A5A" stroke-width="1.6">{hangers}</g>
<rect x="270" y="296" width="330" height="9" fill="#3B4A5A"/>
<rect x="268" y="252" width="34" height="62" fill="#C9B79C"/><rect x="290" y="252" width="12" height="62" fill="#B3A285"/>
<rect x="598" y="252" width="34" height="62" fill="#C9B79C"/>
<rect x="120" y="334" width="340" height="24" fill="#D9C7A7"/>
<g fill="#C4B08E">{"".join(f'<rect x="{x}" y="340" width="20" height="3"/>' for x in range(130, 450, 30))}</g>
{sails}
<rect x="0" y="356" width="600" height="88" fill="#2C6E9B"/>
{ripples([(40, 380, 60), (200, 404, 60), (380, 386, 40), (500, 420, 60), (120, 428, 40)], "#8CC3E3")}
<g transform="translate(470 368)"><path d="M 0 16 L 96 16 L 86 30 L 10 30 Z" fill="#2F6B4F"/><rect x="14" y="2" width="66" height="15" rx="3" fill="#F2E7C9"/>
{"".join(f'<rect x="{x}" y="6" width="8" height="6" fill="#2F6B4F"/>' for x in range(20, 76, 12))}<rect x="40" y="-8" width="10" height="11" fill="#2F6B4F"/></g>
<path d="M 60 404 L 120 404 L 110 416 L 70 416 Z" fill="#FBF8F2"/><path d="M 92 404 L 92 362 L 114 400 Z" fill="#FBF8F2"/>
"""


# ---------------------------------------------------------------- Venice
def venice():
    def palazzo(x, w, top, fill, trim, shutter):
        out = [f'<rect x="{x}" y="{top}" width="{w}" height="{330 - top}" fill="{fill}"/>',
               f'<rect x="{x - 3}" y="{top - 6}" width="{w + 6}" height="8" fill="{trim}"/>']
        cols = max(1, (w - 16) // 24)
        for j, y in enumerate(range(top + 22, 296, 44)):
            for i in range(cols):
                wx = x + 12 + i * 24
                out.append(f'<path d="M {wx} {y + 28} L {wx} {y + 8} Q {wx + 6} {y - 2} {wx + 12} {y + 8} L {wx + 12} {y + 28} Z" fill="#4A3A34"/>')
                out.append(f'<rect x="{wx - 3}" y="{y + 8}" width="3" height="20" fill="{shutter}"/><rect x="{wx + 12}" y="{y + 8}" width="3" height="20" fill="{shutter}"/>')
            if j == 1:
                out.append(f'<rect x="{x + 8}" y="{y + 28}" width="{w - 16}" height="4" fill="{trim}"/>')
                out.append(f'<g fill="{trim}">' + "".join(f'<rect x="{bx}" y="{y + 32}" width="2" height="8"/>' for bx in range(x + 10, x + w - 8, 6)) + "</g>")
        out.append(f'<path d="M {x + w / 2 - 14} 330 L {x + w / 2 - 14} 310 Q {x + w / 2} 296 {x + w / 2 + 14} 310 L {x + w / 2 + 14} 330 Z" fill="#2F2622"/>')
        return "".join(out)

    def chimney(x, top, fill):
        return f'<rect x="{x}" y="{top}" width="8" height="16" fill="{fill}"/><path d="M {x - 6} {top} L {x + 14} {top} L {x + 10} {top - 14} L {x - 2} {top - 14} Z" fill="{fill}"/>'
    blds = [(0, 118, 150, "#E3A15A", "#F6E3C8", "#3F6E5A"), (118, 96, 120, "#C9634B", "#F6E3C8", "#3F6E5A"),
            (214, 84, 172, "#F0C987", "#FBF1E2", "#8C2F39"), (380, 104, 128, "#D97B6B", "#F6E3C8", "#3F6E5A"),
            (484, 116, 160, "#E8B26A", "#FBF1E2", "#8C2F39")]
    out = ['<rect width="600" height="444" fill="#FCE3C6"/>', '<circle cx="300" cy="120" r="70" fill="#F8C98F"/>',
           cloud_band(70, 80, 140, 12, "#FDEFDD"), cloud_band(420, 64, 120, 10, "#FDEFDD"),
           # Santa Maria della Salute in the distance
           '<g fill="#E6D7BE"><rect x="262" y="150" width="76" height="60"/><path d="M 268 152 Q 300 96 332 152 Z"/><rect x="294" y="96" width="12" height="16"/><path d="M 292 98 Q 300 84 308 98 Z"/></g>',
           birds([(180, 120, 12), (204, 132, 9)], "#8C2F39")]
    for x, w, top, f, trim, sh in blds:
        out.append(palazzo(x, w, top, f, trim, sh))
    out += [chimney(30, 144, "#B5704A"), chimney(150, 114, "#9E4F3B"), chimney(420, 98, "#B55F51"), chimney(540, 110, "#B5704A")]
    out.append('<rect x="0" y="326" width="600" height="118" fill="#3F8C8C"/>')
    refl = "".join(f'<path d="M {x} {y} q 6 4 12 0 t 12 0 t 12 0" fill="none" stroke="{c}" stroke-width="4" stroke-linecap="round" opacity="0.7"/>'
                   for x, y, c in ((20, 344, "#E3A15A"), (140, 352, "#C9634B"), (250, 342, "#F0C987"), (410, 350, "#D97B6B"), (520, 344, "#E8B26A"),
                                   (60, 372, "#E3A15A"), (300, 366, "#F0C987"), (470, 376, "#D97B6B")))
    out.append(refl)
    out.append("".join(f'<rect x="{x}" y="262" width="9" height="130" fill="#FFFFFF"/>' + "".join(f'<rect x="{x}" y="{y}" width="9" height="11" fill="#2E5EA8"/>' for y in range(266, 392, 22))
                       + f'<circle cx="{x + 4.5}" cy="260" r="6" fill="#2E5EA8"/>' for x in (36, 66)))
    gondola = ('<path d="M 150 404 Q 300 426 448 398 Q 458 386 470 376 L 476 380 Q 466 392 462 404 Q 300 440 146 412 Q 132 404 126 390 L 132 388 Q 138 400 150 404 Z" fill="#1E1E1E"/>'
               '<path d="M 462 380 L 482 368 M 466 386 L 486 376 M 468 392 L 488 384" stroke="#C9C2B4" stroke-width="3" stroke-linecap="round"/>'
               '<rect x="230" y="394" width="40" height="12" rx="3" fill="#8C2F39"/>'
               '<g><rect x="332" y="346" width="18" height="44" fill="#F6EFE0"/>' + "".join(f'<rect x="332" y="{y}" width="18" height="4" fill="#1F2F4D"/>' for y in (350, 358, 366, 374)) +
               '<rect x="332" y="388" width="18" height="16" fill="#1E1E1E"/><circle cx="341" cy="336" r="9" fill="#E8C4A0"/>'
               '<ellipse cx="341" cy="328" rx="14" ry="3" fill="#E9C46A"/><rect x="333" y="320" width="16" height="8" rx="2" fill="#E9C46A"/><rect x="333" y="325" width="16" height="2.5" fill="#8C2F39"/></g>'
               '<line x1="356" y1="342" x2="392" y2="430" stroke="#6B4A2E" stroke-width="4" stroke-linecap="round"/>')
    out.append(gondola)
    out.append(ripples([(80, 432, 40), (500, 424, 50), (220, 438, 30)], "#7BB8B5"))
    return "\n".join(out)


def build_world():
    poster("world", "paris", "PARIS", "FRANCE · CITY OF LIGHT", paris(), "#3B3858", "#F4A28C", "#FFF1E8", "#F4A28C")
    poster("world", "japan", "JAPAN", "MOUNT FUJI · HONSHU", japan(), "#8E2C25", "#F2A7B8", "#FFF4EE", "#F7C6D0")
    poster("world", "santorini", "SANTORINI", "GREECE · CYCLADES", santorini(), "#244C8C", "#F5AE84", "#FFFFFF", "#F6C28B")
    poster("world", "rome", "ROME", "ITALIA · EST. 753 BC", rome(), "#7A2E22", "#F0A65E", "#FCEBD5", "#F0A65E")
    poster("world", "london", "LONDON", "ENGLAND · UNITED KINGDOM", london(), "#1F3A5F", "#C8322E", "#F6EFE0", "#E2B857")
    poster("world", "cairo", "CAIRO", "EGYPT · PYRAMIDS OF GIZA", cairo(), "#5B3A22", "#F28C38", "#FCEBD5", "#F9C98A")
    poster("world", "sydney", "SYDNEY", "AUSTRALIA · HARBOUR CITY", sydney(), "#22577A", "#FFC857", "#FFFFFF", "#FFC857")
    poster("world", "venice", "VENICE", "ITALIA · LA SERENISSIMA", venice(), "#8C2F39", "#F2C46D", "#FDF0E0", "#F2C46D")


if __name__ == "__main__":
    build_world()
