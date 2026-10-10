"""Home-screen icons for the admin app (admin/manifest.webmanifest), drawn from the logo's hive mark.

Writes admin/icons/icon-192.png, icon-512.png (purpose "any maskable": the seal stays inside the 80 % safe zone) and
apple-touch-icon.png (180 px, iPhone). Honey background, the cream seal with an ink ring, and the six hexes from
assets/favicon.svg. Pillow only; drawn 4x and scaled down for smooth edges. Called by build.py when an icon is missing;
run `python3 tools/admin_icons.py --force` to redraw."""
import pathlib
import sys

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "admin" / "icons"
HONEY, SOFT, INK, CREAM = "#F2A81D", "#F9D88A", "#2B2118", "#FFF6E5"

# assets/favicon.svg (viewBox 138 8 124 118): (fill, points) of the six hexes, and the door arch on the ink one
HEXES = [
    (HONEY, [(200, 14), (217.32, 24), (217.32, 44), (200, 54), (182.68, 44), (182.68, 24)]),
    (HONEY, [(180.95, 47), (198.27, 57), (198.27, 77), (180.95, 87), (163.63, 77), (163.63, 57)]),
    (SOFT, [(219.05, 47), (236.37, 57), (236.37, 77), (219.05, 87), (201.73, 77), (201.73, 57)]),
    (HONEY, [(161.9, 80), (179.22, 90), (179.22, 110), (161.9, 120), (144.58, 110), (144.58, 90)]),
    (INK, [(200, 80), (217.32, 90), (217.32, 110), (200, 120), (182.68, 110), (182.68, 90)]),
    (HONEY, [(238.1, 80), (255.42, 90), (255.42, 110), (238.1, 120), (220.78, 110), (220.78, 90)]),
]
MARK_CX, MARK_CY, MARK_W = 200.0, 67.0, 110.84


def draw(size):
    s = size * 4
    img = Image.new("RGBA", (s, s), HONEY)
    d = ImageDraw.Draw(img)
    c = s / 2
    r = s * 0.34                       # seal radius: inside the maskable safe zone (40 % of the size)
    d.ellipse([c - r, c - r, c + r, c + r], fill=CREAM)
    ring = max(2, s * 0.012)
    d.ellipse([c - r + ring * 1.6, c - r + ring * 1.6, c + r - ring * 1.6, c + r - ring * 1.6], outline=INK, width=int(ring))
    k = (r * 1.18) / MARK_W            # the hive mark fills about 60 % of the seal
    tx = lambda x: c + (x - MARK_CX) * k
    ty = lambda y: c + (y - MARK_CY) * k + r * 0.02
    stroke = max(1, int(s * 0.004))
    for fill, pts in HEXES:
        d.polygon([(tx(x), ty(y)) for x, y in pts], fill=fill, outline=INK if fill != INK else None, width=stroke)
    # door: a rectangle with a round top (M194 115 L194 104 A6 6 0 0 1 206 104 L206 115 Z)
    d.rectangle([tx(194), ty(104), tx(206), ty(115)], fill=CREAM)
    d.pieslice([tx(194), ty(98), tx(206), ty(110)], 180, 360, fill=CREAM)
    return img.resize((size, size), Image.LANCZOS).convert("RGB")


def main(force=False):
    OUT.mkdir(parents=True, exist_ok=True)
    made = 0
    for name, px in (("icon-192.png", 192), ("icon-512.png", 512), ("apple-touch-icon.png", 180)):
        dst = OUT / name
        if force or not dst.exists():
            draw(px).save(dst, "PNG", optimize=True)
            made += 1
    return made


if __name__ == "__main__":
    print(f"admin icons: {main(force='--force' in sys.argv)} written")
