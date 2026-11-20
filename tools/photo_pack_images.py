"""Square pictures of the photo-magnet packs for the shop catalogs (Instagram/Facebook, Google): the pack size on top
and that many sample photo magnets on cream, like the real thing laid out on a table. Run by build.py; writes
assets/feed/photo-pack-<n>.jpg (1200 x 1200) only when missing or when this file changes."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CREAM, INK, MUTED, HONEY = (255, 246, 229), (43, 33, 24), (106, 88, 69), (242, 168, 29)
SAMPLES = ["family-1", "pets-1", "wedding-1", "baby-1", "travel-1", "graduation-1", "family-2", "pets-2", "wedding-2",
           "baby-2", "travel-2", "graduation-2", "family-3", "pets-3", "wedding-3", "baby-3", "travel-3", "graduation-3"]


def font(name, size, weight=None):
    f = ImageFont.truetype(str(ROOT / "tools/fonts" / name), size)
    if weight:
        try: f.set_variation_by_axes([weight])
        except Exception: pass
    return f


def pack_image(n, out):
    W = 1200
    im = Image.new("RGB", (W, W), CREAM)
    d = ImageDraw.Draw(im)
    title = font("JosefinSans[wght].ttf", 76, 700)
    sub = font("Jost[wght].ttf", 36, 400)
    t = f"PACK OF {n}"
    tw = d.textlength(t, font=title) + 6 * (len(t) - 1)
    x = (W - tw) / 2
    for ch in t:                              # wide letter spacing, as on the site
        d.text((x, 70), ch, font=title, fill=INK)
        x += d.textlength(ch, font=title) + 6
    s = "your photos as 2 × 2 in fridge magnets"
    d.text(((W - d.textlength(s, font=sub)) / 2, 170), s, font=sub, fill=MUTED)
    d.rectangle([W / 2 - 40, 232, W / 2 + 40, 236], fill=HONEY)
    cols = {4: 2, 9: 3, 16: 4, 25: 5}.get(n, 6)
    rows = cols if n <= 25 else 5
    shown = cols * rows
    top, bottom, side, gap = 280, (130 if n > shown else 70), 90, 22 if cols <= 4 else 16
    cell = min((W - 2 * side - gap * (cols - 1)) / cols, (W - top - bottom - gap * (rows - 1)) / rows)
    gw, gh = cols * cell + gap * (cols - 1), rows * cell + gap * (rows - 1)
    ox, oy = (W - gw) / 2, top + (W - top - bottom - gh) / 2
    shadow = Image.new("L", (W, W), 0)
    sd = ImageDraw.Draw(shadow)
    tiles = []
    for i in range(shown):
        r, c = divmod(i, cols)
        px, py = int(ox + c * (cell + gap)), int(oy + r * (cell + gap))
        sd.rectangle([px + 4, py + 8, px + int(cell) + 4, py + int(cell) + 8], fill=90)
        k = (i + 2 * r) % len(SAMPLES)       # each row starts further on: no row repeats the one above it
        tiles.append((px, py, SAMPLES[(k * 7) % len(SAMPLES)]))
    shadow = shadow.filter(ImageFilter.GaussianBlur(9))
    im.paste((150, 120, 80), (0, 0), shadow.point(lambda v: int(v * 0.55)))
    for px, py, name in tiles:
        ph = Image.open(ROOT / f"assets/showcase/{name}.webp").convert("RGB").resize((int(cell), int(cell)), Image.LANCZOS)
        im.paste(ph, (px, py))
    if n > shown:
        note = font("Jost[wght].ttf", 34, 500)
        m = f"+ {n - shown} more"
        d = ImageDraw.Draw(im)
        bw = d.textlength(m, font=note) + 40
        y0 = W - bottom + 34
        d.rounded_rectangle([(W - bw) / 2, y0, (W + bw) / 2, y0 + 54], 27, fill=INK)
        d.text(((W - bw) / 2 + 20, y0 + 6), m, font=note, fill=CREAM)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "JPEG", quality=88, optimize=True, progressive=True)


def ensure(packs):
    """assets/feed/photo-pack-<n>.jpg for each pack size; returns {n: path relative to the site}."""
    me = Path(__file__).stat().st_mtime
    res = {}
    for n in packs:
        rel = f"assets/feed/photo-pack-{n}.jpg"
        out = ROOT / rel
        if not out.exists() or out.stat().st_mtime < me:
            pack_image(n, out)
        res[n] = rel
    return res


if __name__ == "__main__":
    import sys
    for n in (int(a) for a in sys.argv[1:] or ["4", "9", "16", "25", "50"]):
        pack_image(n, Path(f"/tmp/photo-pack-{n}.jpg"))
