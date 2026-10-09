"""Places of the World: colorful poster magnets in the same style as the US Places collection."""
from common import save, esc, measure, fit_size, MONO, _FONT_FILES

ANTON = "font-family=\"Anton, Impact, sans-serif\""
_FONT_FILES[ANTON] = ("Anton-Regular.ttf", None)


def place(slug, name, sub, art, band, border, namec, subc):
    size = 100
    while size > 50 and measure(name, ANTON, size, 0.02 * size) > 540:
        size -= 2
    H = 0.9 * size + 10 + 26.4
    top = 449 + (151 - H) / 2
    ny = top + 0.81 * size
    sy = top + 0.9 * size + 10 + 13.2 + 7.7
    ssz = fit_size(sub, MONO, 22, 540, 4.8)
    body = (f'<rect width="600" height="600" fill="{band}"/>\n'
            f'<svg x="0" y="0" width="600" height="444" viewBox="0 0 600 444">\n{art.strip()}\n</svg>\n'
            f'<rect x="0" y="444" width="600" height="5" fill="{border}"/>\n'
            f'<text x="300" y="{ny:.1f}" text-anchor="middle" {ANTON} font-size="{size}" letter-spacing="{0.02 * size:.1f}" fill="{namec}">{esc(name)}</text>\n'
            f'<text x="300" y="{sy:.1f}" text-anchor="middle" {MONO} font-size="{ssz}" letter-spacing="4.8" fill="{subc}">{esc(sub)}</text>')
    save("world", slug, body)


def paris():
    roofs = ("M 0 330 L 0 300 L 30 300 L 30 286 L 40 286 L 40 300 L 70 300 Q 80 284 100 284 Q 120 284 130 300 L 170 300 L 170 280 L 180 280 L 180 300 L 210 300 L 210 318 "
             "L 390 318 L 390 296 L 420 296 Q 430 280 450 280 Q 470 280 480 296 L 510 296 L 510 282 L 520 282 L 520 296 L 560 296 Q 575 286 600 290 L 600 330 Z")
    return f"""
<rect width="600" height="444" fill="#F8D3C5"/>
<circle cx="300" cy="200" r="120" fill="#F4A28C"/>
<path d="{roofs}" fill="#E3A99B"/>
<rect x="0" y="328" width="600" height="60" fill="#D99586"/>
<g fill="#C6806F"><rect x="20" y="342" width="14" height="22"/><rect x="50" y="342" width="14" height="22"/><rect x="80" y="342" width="14" height="22"/><rect x="110" y="342" width="14" height="22"/><rect x="140" y="342" width="14" height="22"/><rect x="440" y="342" width="14" height="22"/><rect x="470" y="342" width="14" height="22"/><rect x="500" y="342" width="14" height="22"/><rect x="530" y="342" width="14" height="22"/><rect x="560" y="342" width="14" height="22"/></g>
<path d="M 226 392 Q 268 330 287 220 L 294 110 L 306 110 L 313 220 Q 332 330 374 392 L 344 392 Q 322 352 300 346 Q 278 352 256 392 Z" fill="#3D3A5C"/>
<rect x="246" y="312" width="108" height="10" fill="#3D3A5C"/>
<rect x="274" y="236" width="52" height="8" fill="#3D3A5C"/>
<rect x="289" y="160" width="22" height="6" fill="#3D3A5C"/>
<rect x="297" y="66" width="6" height="46" fill="#3D3A5C"/>
<g stroke="#F4A28C" stroke-width="2" opacity="0.6"><line x1="266" y1="306" x2="300" y2="250"/><line x1="334" y1="306" x2="300" y2="250"/><line x1="286" y1="230" x2="300" y2="172"/><line x1="314" y1="230" x2="300" y2="172"/></g>
<rect x="0" y="388" width="600" height="56" fill="#7FA6B8"/>
<g stroke="#B9D3DE" stroke-width="3" stroke-linecap="round"><line x1="60" y1="408" x2="110" y2="408"/><line x1="200" y1="420" x2="260" y2="420"/><line x1="380" y1="410" x2="430" y2="410"/><line x1="500" y1="426" x2="560" y2="426"/></g>
<g fill="#4F6B4A"><circle cx="60" cy="378" r="30"/><circle cx="110" cy="384" r="24"/><circle cx="500" cy="384" r="24"/><circle cx="548" cy="376" r="32"/></g>
"""


def japan():
    def tier(cx, y, w, h, roof):
        return (f'<rect x="{cx - w / 2 + 6}" y="{y}" width="{w - 12}" height="{h}" fill="#9E2F2A"/>'
                f'<path d="M {cx - w / 2 - 14} {y} Q {cx} {y - 10} {cx + w / 2 + 14} {y} L {cx + w / 2 - 4} {y - roof} L {cx - w / 2 + 4} {y - roof} Z" fill="#3A2A2A"/>')
    pagoda = "".join(tier(140, y, w, 24, 12) for y, w in ((376, 84), (340, 74), (304, 64), (268, 54), (232, 44)))
    blossoms = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x, y, r, c in (
        (470, 40, 26, "#F2A7B8"), (510, 70, 30, "#F7C6D0"), (560, 50, 34, "#F2A7B8"), (590, 100, 28, "#F7C6D0"),
        (540, 110, 22, "#F2A7B8"), (450, 84, 18, "#F7C6D0"), (30, 30, 30, "#F7C6D0"), (70, 10, 26, "#F2A7B8")))
    return f"""
<rect width="600" height="444" fill="#F6E3C8"/>
<circle cx="420" cy="150" r="58" fill="#D8483B"/>
<path d="M 40 370 L 250 150 Q 300 122 350 150 L 560 370 Z" fill="#6D84A6"/>
<path d="M 250 150 Q 300 122 350 150 L 384 186 L 360 178 L 342 196 L 322 180 L 300 198 L 280 180 L 260 196 L 242 178 L 216 186 Z" fill="#FFFFFF"/>
<path d="M 0 360 Q 150 330 300 352 Q 450 372 600 344 L 600 444 L 0 444 Z" fill="#7E9B6B"/>
<path d="M 0 400 Q 200 380 400 404 Q 500 414 600 396 L 600 444 L 0 444 Z" fill="#5E7A54"/>
<path d="M 600 70 Q 520 80 460 120" fill="none" stroke="#5A3A2E" stroke-width="7" stroke-linecap="round"/>
<path d="M 0 40 Q 40 50 80 30" fill="none" stroke="#5A3A2E" stroke-width="6" stroke-linecap="round"/>
{blossoms}
{pagoda}
<rect x="137" y="190" width="6" height="34" fill="#3A2A2A"/>
"""


def santorini():
    houses = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#F7F4EE"/><rect x="{x + w - 12}" y="{y}" width="12" height="{h}" fill="#DCE3E8"/>'
                     f'<rect x="{x + 10}" y="{y + 14}" width="12" height="16" rx="2" fill="#2559A8"/>'
                     for x, y, w, h in ((40, 250, 90, 70), (120, 220, 80, 100), (190, 250, 70, 80), (330, 236, 90, 90),
                                        (410, 210, 100, 120), (500, 246, 80, 90), (90, 300, 100, 60), (260, 280, 100, 70), (440, 290, 110, 60)))
    return f"""
<rect width="600" height="444" fill="#CFE8F2"/>
<circle cx="470" cy="90" r="40" fill="#FFD27A"/>
<path d="M 0 300 Q 100 270 200 290 Q 320 310 420 284 Q 520 262 600 280 L 600 380 L 0 380 Z" fill="#C9A57E"/>
{houses}
<path d="M 236 250 A 34 34 0 0 1 304 250 Z" fill="#2559A8"/><rect x="236" y="250" width="68" height="40" fill="#F7F4EE"/><rect x="268" y="206" width="4" height="12" fill="#F7F4EE"/>
<path d="M 520 246 A 26 26 0 0 1 572 246 Z" fill="#2559A8"/>
<rect x="352" y="186" width="34" height="50" fill="#F7F4EE"/><path d="M 352 186 A 17 17 0 0 1 386 186 Z" fill="#2559A8"/><rect x="362" y="198" width="14" height="18" rx="7" fill="#C9A57E"/>
<rect x="0" y="370" width="600" height="74" fill="#2E7FB8"/>
<g stroke="#8CC3E3" stroke-width="3" stroke-linecap="round"><line x1="40" y1="392" x2="100" y2="392"/><line x1="180" y1="410" x2="250" y2="410"/><line x1="340" y1="396" x2="400" y2="396"/><line x1="470" y1="418" x2="540" y2="418"/></g>
<path d="M 380 404 L 440 404 L 430 416 L 390 416 Z" fill="#F7F4EE"/><path d="M 410 404 L 410 376 L 428 400 Z" fill="#F7F4EE"/>
"""


def rome():
    arches = "".join(f'<rect x="{x}" y="{y}" width="22" height="36" rx="11" fill="#A85A32"/>'
                     for y, xs in ((330, range(120, 480, 34)), (276, range(120, 480, 34)), (226, range(120, 420, 34)))
                     for x in xs)
    return f"""
<rect width="600" height="444" fill="#F7D9A8"/>
<circle cx="300" cy="170" r="130" fill="#EFA35A"/>
<path d="M 100 380 L 100 214 Q 280 186 420 196 L 420 214 L 460 220 L 460 254 L 500 262 L 500 380 Z" fill="#D9935A"/>
<rect x="100" y="262" width="400" height="6" fill="#C17A45"/><rect x="100" y="316" width="400" height="6" fill="#C17A45"/>
{arches}
<rect x="0" y="376" width="600" height="68" fill="#C9B38A"/>
<g fill="#3F5A3A"><ellipse cx="50" cy="300" rx="20" ry="90"/><ellipse cx="80" cy="320" rx="16" ry="70"/><ellipse cx="540" cy="300" rx="20" ry="92"/><ellipse cx="568" cy="326" rx="15" ry="64"/></g>
<rect x="0" y="400" width="600" height="44" fill="#B79F74"/>
"""


def london():
    windows = "".join(f'<rect x="{x}" y="358" width="22" height="16" rx="3" fill="#F6EFE0"/>'
                      f'<rect x="{x}" y="394" width="22" height="16" rx="3" fill="#F6EFE0"/>' for x in range(330, 520, 30))
    return f"""
<rect width="600" height="444" fill="#D7E3EA"/>
<g fill="#FFFFFF"><ellipse cx="120" cy="80" rx="60" ry="20"/><ellipse cx="160" cy="68" rx="40" ry="22"/><ellipse cx="470" cy="110" rx="56" ry="18"/></g>
<rect x="0" y="250" width="600" height="140" fill="#A87C4C"/>
<g fill="#8E6538"><rect x="20" y="236" width="10" height="20"/><rect x="80" y="236" width="10" height="20"/><rect x="140" y="236" width="10" height="20"/><rect x="410" y="236" width="10" height="20"/><rect x="470" y="236" width="10" height="20"/><rect x="530" y="236" width="10" height="20"/></g>
<g fill="#8E6538">{"".join(f'<rect x="{x}" y="276" width="12" height="40" rx="6"/>' for x in range(20, 600, 34) if not 220 < x < 330)}</g>
<rect x="236" y="120" width="88" height="270" fill="#B98D57"/>
<rect x="228" y="110" width="104" height="16" fill="#A87C4C"/>
<path d="M 240 110 L 280 30 L 320 110 Z" fill="#8E6538"/>
<rect x="277" y="10" width="6" height="24" fill="#8E6538"/>
<circle cx="280" cy="168" r="30" fill="#F6EFE0"/><circle cx="280" cy="168" r="30" fill="none" stroke="#8E6538" stroke-width="4"/>
<g stroke="#3A2A20" stroke-width="4" stroke-linecap="round"><line x1="280" y1="168" x2="280" y2="148"/><line x1="280" y1="168" x2="294" y2="174"/></g>
<g fill="#8E6538"><rect x="252" y="220" width="10" height="150" rx="5"/><rect x="298" y="220" width="10" height="150" rx="5"/></g>
<rect x="0" y="380" width="600" height="64" fill="#6E7C86"/>
<rect x="316" y="340" width="226" height="86" rx="12" fill="#C8322E"/>
{windows}
<rect x="316" y="380" width="226" height="6" fill="#9E2420"/>
<circle cx="356" cy="428" r="14" fill="#2B2B2B"/><circle cx="500" cy="428" r="14" fill="#2B2B2B"/>
"""


def cairo():
    return """
<rect width="600" height="444" fill="#F9D9A0"/>
<circle cx="420" cy="230" r="120" fill="#F28C38"/>
<polygon points="140,340 300,140 460,340" fill="#D9A35F"/><polygon points="300,140 460,340 330,340" fill="#B97E3E"/>
<polygon points="400,340 490,226 580,340" fill="#D9A35F"/><polygon points="490,226 580,340 500,340" fill="#B97E3E"/>
<polygon points="40,340 110,250 180,340" fill="#D9A35F"/><polygon points="110,250 180,340 120,340" fill="#B97E3E"/>
<path d="M 0 330 Q 150 300 300 330 Q 450 360 600 320 L 600 444 L 0 444 Z" fill="#E8B977"/>
<path d="M 0 380 Q 200 350 400 380 Q 500 396 600 370 L 600 444 L 0 444 Z" fill="#DDA766"/>
<path d="M 120 410 L 126 372 Q 120 352 134 342 Q 150 330 168 344 Q 178 330 192 340 Q 204 350 206 366 L 220 360 L 228 336 L 238 334 L 236 350 L 222 376 L 214 410 L 206 410 L 204 384 L 180 384 L 176 410 L 168 410 L 166 384 L 140 384 L 136 410 L 128 410 L 130 384 Z" fill="#5B3A22"/>
<g fill="#5B7A3A"><path d="M 520 420 Q 524 380 516 340 L 522 340 Q 532 380 528 420 Z" fill="#6B4A2E"/><path d="M 519 340 Q 490 320 470 334 Q 494 330 519 344 Z"/><path d="M 519 340 Q 550 318 572 330 Q 548 330 519 346 Z"/><path d="M 519 340 Q 510 310 492 300 Q 516 318 521 340 Z"/><path d="M 519 340 Q 534 308 552 302 Q 530 320 521 342 Z"/></g>
"""


def sydney():
    sails = "".join(f'<path d="M {x} 340 Q {x + 10} {y + 40} {x + w} {y} Q {x + w - 6} {y + 70} {x + w + 16} 340 Z" fill="{c}"/>'
                    for x, y, w, c in ((150, 230, 70, "#FAF7F0"), (210, 200, 80, "#ECE6DA"), (290, 220, 70, "#FAF7F0"),
                                       (350, 250, 60, "#ECE6DA"), (400, 272, 50, "#FAF7F0")))
    return f"""
<rect width="600" height="444" fill="#BFE1EE"/>
<circle cx="110" cy="110" r="46" fill="#FFC857"/>
<path d="M 300 300 Q 450 120 600 300" fill="none" stroke="#3B4A5A" stroke-width="14"/>
<path d="M 330 300 Q 450 160 570 300" fill="none" stroke="#3B4A5A" stroke-width="4"/>
<g stroke="#3B4A5A" stroke-width="3">{"".join(f'<line x1="{x}" y1="{300 - (1 - ((x - 450) / 150) ** 2) * 180 * 0.9:.0f}" x2="{x}" y2="300"/>' for x in range(340, 580, 24))}</g>
<rect x="300" y="290" width="300" height="10" fill="#3B4A5A"/>
<rect x="120" y="336" width="340" height="26" fill="#D9C7A7"/>
{sails}
<rect x="0" y="360" width="600" height="84" fill="#2C6E9B"/>
<g stroke="#8CC3E3" stroke-width="3" stroke-linecap="round"><line x1="40" y1="384" x2="100" y2="384"/><line x1="200" y1="404" x2="260" y2="404"/><line x1="380" y1="390" x2="440" y2="390"/><line x1="500" y1="414" x2="560" y2="414"/></g>
"""


def venice():
    def building(x, w, top, fill, win):
        wins = "".join(f'<rect x="{x + 14 + i * 26}" y="{top + 24 + j * 52}" width="14" height="30" rx="7" fill="{win}"/>'
                       for i in range(max(1, (w - 14) // 26)) for j in range(3) if top + 24 + j * 52 + 30 < 320)
        return f'<rect x="{x}" y="{top}" width="{w}" height="{330 - top}" fill="{fill}"/><rect x="{x}" y="{top}" width="{w}" height="8" fill="#FFFFFF" opacity="0.35"/>{wins}'
    bl = "".join(building(x, w, t, f, "#5A3A2E") for x, w, t, f in (
        (0, 120, 140, "#E3A15A"), (120, 100, 110, "#C9634B"), (220, 90, 160, "#F0C987"), (380, 110, 120, "#D97B6B"), (490, 110, 150, "#E8B26A")))
    return f"""
<rect width="600" height="444" fill="#FBE3C4"/>
{bl}
<rect x="310" y="210" width="70" height="120" fill="#B9CFC4"/><path d="M 310 210 A 35 35 0 0 1 380 210 Z" fill="#8FB0A2"/>
<rect x="0" y="326" width="600" height="118" fill="#3F8C8C"/>
<g fill="#5BA3A0" opacity="0.8"><rect x="20" y="346" width="80" height="6" rx="3"/><rect x="150" y="372" width="60" height="6" rx="3"/><rect x="400" y="360" width="90" height="6" rx="3"/><rect x="250" y="420" width="70" height="6" rx="3"/></g>
<g><rect x="520" y="250" width="10" height="150" fill="#FFFFFF"/>{"".join(f'<rect x="520" y="{y}" width="10" height="12" fill="#C8322E"/>' for y in range(256, 400, 24))}</g>
<path d="M 150 396 Q 300 418 450 392 Q 456 380 466 372 L 470 376 Q 462 388 460 398 Q 300 432 146 404 Q 136 398 132 386 L 138 384 Q 142 394 150 396 Z" fill="#1E1E1E"/>
<path d="M 330 392 L 330 340 L 340 330 L 350 340 L 350 392 Z" fill="#1E1E1E"/><circle cx="340" cy="322" r="9" fill="#1E1E1E"/><rect x="328" y="312" width="24" height="5" fill="#C8322E"/>
<line x1="356" y1="300" x2="384" y2="420" stroke="#5A3A2E" stroke-width="4"/>
"""


def build_world():
    place("paris", "PARIS", "FRANCE · CITY OF LIGHT", paris(), "#3D3A5C", "#F4A28C", "#FFF1E8", "#F4A28C")
    place("japan", "JAPAN", "MOUNT FUJI · HONSHU", japan(), "#9E2F2A", "#F2A7B8", "#FFF4EE", "#F2A7B8")
    place("santorini", "SANTORINI", "GREECE · CYCLADES", santorini(), "#2559A8", "#FFFFFF", "#FFFFFF", "#CFE8F2")
    place("rome", "ROME", "ITALIA · EST. 753 BC", rome(), "#7A2E22", "#EFA35A", "#FCEBD5", "#EFA35A")
    place("london", "LONDON", "ENGLAND · UNITED KINGDOM", london(), "#1F3A5F", "#C8322E", "#F6EFE0", "#D7E3EA")
    place("cairo", "CAIRO", "EGYPT · THE PYRAMIDS OF GIZA", cairo(), "#5B3A22", "#F28C38", "#FCEBD5", "#F9D9A0")
    place("sydney", "SYDNEY", "AUSTRALIA · HARBOUR CITY", sydney(), "#2C6E9B", "#FFC857", "#FFFFFF", "#FFC857")
    place("venice", "VENICE", "ITALIA · LA SERENISSIMA", venice(), "#8C2F39", "#F2C46D", "#FDF0E0", "#F2C46D")


if __name__ == "__main__":
    build_world()
