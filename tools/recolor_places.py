"""Repaints the painted USA Places posters in the first-version palette the owners prefer: peach and cream skies, teal,
sage, terracotta, coral and gold, and a light name band instead of the dark one.

Works on the finished SVG (no need to re-run the painters): every colour in the scene is moved in OKLCH space
(dusk purples turned to peach in the light and teal-slate in the shade, then each colour pulled onto the
nearest first-version colour, keeping the painting's own light and shade), then the band, the thin
rule and the two lines of text get the new light band colours.

  python3 tools/recolor_places.py <slug> [<slug>...] [--band cream|soft] [--out DIR]
Without --out the SVG in designs/places/ is replaced (the original is kept once as designs/places/_painted/<slug>.svg)."""
import argparse
import math
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLACES = ROOT / "designs" / "places"
KEEP = PLACES / "_painted"


# ---------------------------------------------------------------- colour maths (sRGB <-> OKLab)
def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gam(c):
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def hex_to_oklch(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    r, g, b = (_lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))
    l_ = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m_ = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def oklch_to_hex(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    for _ in range(20):   # pull chroma in until it fits sRGB
        l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
        m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
        s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
        r = 4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_
        g = -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_
        bl = -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_
        if all(-0.002 <= v <= 1.002 for v in (r, g, bl)):
            break
        a, b = a * 0.9, b * 0.9
    return "#" + "".join(f"{round(_gam(v) * 255):02X}" for v in (r, g, bl))


def _toward(h, target, k):
    d = (target - h + 540) % 360 - 180
    return (h + d * k) % 360


# ---------------------------------------------------------------- the first-version look
# Colours of the first-version USA posters (versions/v3/designs/places): warm creams and peach skies, pale aqua,
# teal water, sage and olive greens, terracotta, coral, golden sun. No dusk purples.
OLD = """4A3A2A 4F5D34 4F93A3 5A2E2A 7E3B2C A9502F C65F37 D27447 D9864F E6995F E9925A EFC198 F4A15A F8E6CC F9DDB0
1E9AB0 2F7A4F 3BB8C4 4DC2CC 6A7C4E 7C8F5C 95A86E F6C453 F6E2B8 FF7A59 FFB45C FFE6BE FFF1DE 155C6B 1A8F96 1F7A5C
2BB3B0 2E8C6C 5B4A33 8A6A4A 9A7A58 E6CB98 FF6F61 FF8A6E FFD25E FFE1C7 FFF2DE 2D4A5C 3D6F8E 3F8573 4F9783 5E8A52
5FA996 7FA36B 86AECA A8957F B3A28C BFAE98 CDBDA8 E06C4B E7B9A6 F2A784 F4EDE4 F7D7C4 F7E9DD 12613F 1E7FA0 1F5B45
245A4E 2E6B5E 3D8A77 3F8B6B 4A3826 4E9C79 6B4E35 7CC6D8 EDA978 F2E9DA FBD38B FF8A5B FFD23F FFF1D0 1E3D4F 2F6E86
6E8F6A 7FB1C4 8FA97F 9E3420 A99F94 C8452C CFE3E8 F5C26B 1E2B25 1F3B2D 23402F 2B3B2E 33583F 3F6A4A 7C9B74 A7BC9F
C3E5E6 C6D4BC E4D1B4 E5CFA8 EE8A4E F2B48A F6CBA4 FAF2E4 FBE2A2 134B5A 2B4A55 2E8FA6 2F6B4F 3C7B5B 6F9A55 7CC4D2
A9DBE6 B08D57 B8352A D9442F E3E8EA EFD8AA F4E8D4 FFD36E FFE9A8 23314F 5A3E36 86A872 9AA6B2 C9D1DA D6D0C4 DCE8F2
E8E1D2 E8E2D6""".split()


def _lab(L, C, H):
    return L, C * math.cos(math.radians(H)), C * math.sin(math.radians(H))


_PAL = [_lab(*hex_to_oklch(h)) for h in OLD]


def soften(hexc):
    """Keep the light and shade of the painting, move every colour onto the first-version palette."""
    L, C, H = hex_to_oklch(hexc)
    if C < 0.015:                                        # whites, greys, near-blacks stay (warmed a hair)
        return oklch_to_hex(L, C, 70 if C < 0.004 else H)
    # dusk purples and violets do not exist in the old posters: light ones become peach/cream sky,
    # dark ones the old teal-slate
    if 265 <= H or H < 5:
        H = 62 if L > 0.62 else 215
    elif 240 <= H < 265:
        H = 225
    _, a, b = _lab(L, C, H)
    near = min(_PAL, key=lambda p: 0.35 * (p[0] - L) ** 2 + (p[1] - a) ** 2 + (p[2] - b) ** 2)
    L2 = L * 0.85 + near[0] * 0.15
    a2, b2 = a * 0.25 + near[1] * 0.75, b * 0.25 + near[2] * 0.75
    return oklch_to_hex(L2, math.hypot(a2, b2), math.degrees(math.atan2(b2, a2)) % 360)


BANDS = {   # name band: (band, rule, name, subtitle)
    "cream": ("#F7ECDC", "#E9B48A", "#4A2E24", "#B5653D"),
    "peach": ("#F4D2B4", "#E39A6C", "#4A2E24", "#9E4E2E"),
    "sage": ("#D3DCC4", "#9DB08A", "#2F3B2C", "#5E7350"),
    "greyblue": ("#C8D7DE", "#8FAAB8", "#24343E", "#4E6E80"),
}

HEX = re.compile(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b")


def recolor(svg, band):
    head, rest = svg.split("\n", 1)
    rest = re.sub(r'^<rect width="600" height="600" fill="#[0-9A-Fa-f]+"/>', "", rest, count=1)
    i = rest.rfind("</svg>", 0, rest.rfind("</svg>"))          # end of the nested scene
    scene, tail = rest[:i], rest[i:]
    cache = {}
    scene = HEX.sub(lambda m: cache.setdefault(m.group(0).upper(), soften(m.group(0))), scene)
    bg, rule, namec, subc = BANDS[band]
    tail = re.sub(r'(<rect x="0" y="\d+" width="600" height="5" fill=")#[0-9A-Fa-f]+', r"\g<1>" + rule, tail, count=1)
    texts = list(re.finditer(r'(<text [^>]*fill=")(#[0-9A-Fa-f]+)', tail))
    for k, m in reversed(list(enumerate(texts))):
        tail = tail[:m.start(2)] + (namec if k == 0 else subc) + tail[m.end(2):]
    return f'{head}\n<rect width="600" height="600" fill="{bg}"/>\n{scene}{tail}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slugs", nargs="+")
    ap.add_argument("--band", default="cream", choices=list(BANDS))
    ap.add_argument("--out")
    a = ap.parse_args()
    for slug in a.slugs:
        src = KEEP / f"{slug}.svg" if (KEEP / f"{slug}.svg").exists() else PLACES / f"{slug}.svg"
        svg = recolor(src.read_text(encoding="utf-8"), a.band)
        if a.out:
            out = pathlib.Path(a.out) / f"{slug}-{a.band}.svg"
        else:
            KEEP.mkdir(exist_ok=True)
            if not (KEEP / f"{slug}.svg").exists():
                shutil.copyfile(PLACES / f"{slug}.svg", KEEP / f"{slug}.svg")
            out = PLACES / f"{slug}.svg"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg, encoding="utf-8")
        print("wrote", out)


if __name__ == "__main__":
    main()
