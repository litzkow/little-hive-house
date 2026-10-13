"""Repaints the painted USA Places posters in the first-version palette the owners prefer: soft peach, sage, grey-blue
and cream, lighter shadows, and a light name band instead of the dark one.

Works on the finished SVG (no need to re-run the painters): every colour in the scene is moved in OKLCH space
(lifted, softened, dusk purples turned to peach in the light and to grey-blue in the shade), then the band, the thin
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
def soften(hexc):
    L, C, H = hex_to_oklch(hexc)
    if C < 0.02:                                   # greys, whites, near-blacks: lift and warm a touch
        L2 = 0.30 + 0.70 * L if L < 0.5 else L
        return oklch_to_hex(min(L2, 0.985), C + 0.008, 60 if C < 0.005 else H)
    # dusk purples / magentas: light ones go peach, dark ones go grey-blue (the old skies and waters)
    if 255 <= H or H < 12:
        H = _toward(H, 50 if L > 0.6 else 222, 0.9)
        C = C * 0.8
    elif 200 <= H < 255:                                   # blues -> the old soft grey-blue
        H = _toward(H, 218, 0.7)
        C = C * 0.75
    # lift the darks (the old posters had no deep shadows), soften the chroma
    L2 = 0.32 + 0.68 * L
    L2 = L2 + (0.9 - L2) * 0.15 if L2 < 0.9 else L2
    C2 = C * (0.78 if L2 > 0.7 else 0.66)
    return oklch_to_hex(min(L2, 0.985), C2, H)


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
