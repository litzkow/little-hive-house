"""Builds the TikTok Shop product photos (tiktok/img/<collection>/<n>.jpg), square, in the website's look.

Owners (Nov 2026): the TikTok shop as close as possible to the real site. So no Etsy lifestyle scenes here (those are
Etsy-only): the site's cream paper, its fonts and colors, the real designs in the site's order, numbered like the
"Design" options of the TikTok product.
  1      one magnet, big and clear on the cream paper (TikTok wants a single product, not a collage, as the main photo)
  2      the collection: its name, how many designs, nine designs as magnets
  2..    "Pick your design": every design, numbered, 16 per photo
  then   actual size (2 x 2 in) and "Good to know" with the shop's seal
TikTok takes 9 photos at most: a collection with more than 80 designs would lose its last guides (none has, Nov 2026).

Usage:  python3 tools/tiktok_photos.py [collection ...]      (then raise "imagesVersion" in functions/tiktok-photos.json)
"""
import json
import pathlib
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import etsy_photos as E  # noqa: E402  (fonts, colors, the magnet tiles, the cream paper)

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "tiktok" / "img"
S = 1600
PER = 16


def art(slug):
    return Image.open(ROOT / "assets" / "art" / f"{slug}.webp").convert("RGB")


def head(d, kicker, title, y=150, size=92):
    E.text_center(d, (S / 2, y), kicker.upper(), E.font("josefin", 34, 600), E.BROWN_SOFT, spacing=7)
    E.text_center(d, (S / 2, y + size + 10), title, E.font("josefin", size, 700), E.BROWN)


def hero(slug):
    im = E.cream_bg(S, S)
    big = ROOT / "assets" / "print" / f"{slug}.jpg"          # the 1200 px print file when there is one: sharper
    return E.drop_tile(im, Image.open(big).convert("RGB") if big.exists() else art(slug), S / 2, S / 2 - 20, 980, 0, shadow=0.26)


def cover(name, slugs, n):
    im = E.cream_bg(S, S)
    d = ImageDraw.Draw(im)
    head(d, "Little Hive House", name, y=150, size=104 if len(name) <= 18 else 84)
    E.text_center(d, (S / 2, 345), f"{n} designs  ·  2 x 2 in square fridge magnets", E.font("jost", 40, 420), E.BROWN_SOFT)
    show = slugs[:9]
    cols = 3 if len(show) >= 5 else len(show)
    rows = (len(show) + cols - 1) // cols
    size, gap = 285, 50
    top = 450 + (3 - rows) * (size + gap) / 2
    for i, slug in enumerate(show):
        r, c = divmod(i, cols)
        in_row = min(cols, len(show) - r * cols)
        x = S / 2 + (c - (in_row - 1) / 2) * (size + gap)
        y = top + r * (size + gap) + size / 2
        im = E.drop_tile(im, art(slug), x, y, size, 0, shadow=0.2)
    d = ImageDraw.Draw(im)
    E.text_center(d, (S / 2, S - 70), "Made by hand, to order", E.font("caveat", 56), "#C57A0A")
    return im


def guides(name, designs):
    pages = [designs[i:i + PER] for i in range(0, len(designs), PER)]
    out = []
    for p, page in enumerate(pages):
        im = E.cream_bg(S, S)
        d = ImageDraw.Draw(im)
        kick = f"{name}" + (f"  ({p + 1} of {len(pages)})" if len(pages) > 1 else "")
        head(d, kick, "Pick your design", y=130, size=80)
        cols, size, gx, gy = 4, 240, 345, 322
        rows = (len(page) + cols - 1) // cols
        top = 290 + (4 - rows) * gy / 2
        for i, (slug, dname) in enumerate(page):
            n = p * PER + i + 1
            r, c = divmod(i, cols)
            in_row = min(cols, len(page) - r * cols)
            x = S / 2 + (c - (in_row - 1) / 2) * gx
            y = top + r * gy + size / 2
            im = E.drop_tile(im, art(slug), x, y, size, 0, shadow=0.18)
            d = ImageDraw.Draw(im)
            num, f1, f2 = f"{n:02d}", E.font("jost", 27, 700), E.font("jost", 27, 450)
            label = dname if len(dname) <= 20 else dname[:19].rstrip() + "…"
            wn, wl = d.textlength(num + "  ", font=f1), d.textlength(label, font=f2)
            sx = x - (wn + wl) / 2
            d.text((sx, y + size / 2 + 42), num, font=f1, fill=E.HONEY, anchor="ls")
            d.text((sx + wn, y + size / 2 + 42), label, font=f2, fill=E.BROWN, anchor="ls")
        out.append(im)
    return out


def actual_size(slug):
    im = E.cream_bg(S, S)
    size, cx, cy = 640, 640, 900
    im = E.drop_tile(im, art(slug), cx, cy, size, 0, shadow=0.24)
    d = ImageDraw.Draw(im)
    head(d, "Actual size", "2 x 2 inches (5 x 5 cm)", y=150, size=80)
    x0, x1, y0, y1 = cx - size / 2, cx + size / 2, cy - size / 2, cy + size / 2
    col, lab = E.BROWN, E.font("jost", 40, 600)
    d.line([(x0, y0 - 70), (x1, y0 - 70)], fill=col, width=4)
    d.line([(x0, y0 - 90), (x0, y0 - 50)], fill=col, width=4)
    d.line([(x1, y0 - 90), (x1, y0 - 50)], fill=col, width=4)
    tw = d.textlength("2 in", font=lab)
    d.rectangle([cx - tw / 2 - 18, y0 - 100, cx + tw / 2 + 18, y0 - 40], fill=im.getpixel((int(cx), int(y0 - 120))))
    d.text((cx, y0 - 56), "2 in", font=lab, fill=col, anchor="ms")
    d.line([(x1 + 70, y0), (x1 + 70, y1)], fill=col, width=4)
    d.line([(x1 + 50, y0), (x1 + 90, y0)], fill=col, width=4)
    d.line([(x1 + 50, y1), (x1 + 90, y1)], fill=col, width=4)
    d.rectangle([x1 + 40, cy - 50, x1 + 100, cy + 50], fill=im.getpixel((int(x1 + 120), int(cy))))
    d.text((x1 + 70, cy - 6), "2", font=lab, fill=col, anchor="ms")
    d.text((x1 + 70, cy + 38), "in", font=lab, fill=col, anchor="ms")
    dx, dy = x1 + 170, cy - 170
    d.text((dx, dy), "THE DETAILS", font=E.font("josefin", 30, 600), fill=E.BROWN_SOFT, anchor="ls")
    for i, line in enumerate(["2 x 2 inch square", "Square corners", "Glossy, wipe-clean", "Strong magnet back", "Pressed by hand"]):
        d.text((dx, dy + 66 + i * 56), line, font=E.font("jost", 36, 420), fill=E.BROWN, anchor="ls")
    E.text_center(d, (S / 2, S - 150), "Just right for a busy fridge", E.font("caveat", 64), "#C57A0A")
    return im


def good_to_know():
    im = E.cream_bg(S, S)
    d = ImageDraw.Draw(im)
    head(d, "Little Hive House", "Good to know", y=150, size=80)
    seal = Image.open(ROOT / "tools" / "etsy_shop" / "shop-icon.png").convert("RGB").resize((520, 520), Image.LANCZOS)
    m = Image.new("L", seal.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, seal.width - 1, seal.height - 1], fill=255)
    im.paste(seal, (int(S / 2 - 260), 330), m)
    d = ImageDraw.Draw(im)
    points = [("Made by hand, to order", "Printed, pressed and packed by us"),
              ("Ships in 1 to 2 business days", "With tracking"),
              ("Mix any designs", "Pick as many as you like, from any collection"),
              ("Ready to gift", "Each magnet in a protective sleeve")]
    y = 960
    for i, (t, sub) in enumerate(points):
        cx = 420
        d.ellipse([cx - 30, y - 42, cx + 30, y + 18], fill=E.HONEY)
        d.text((cx, y - 4), str(i + 1), font=E.font("josefin", 34, 700), fill="#FFFFFF", anchor="ms")
        d.text((cx + 60, y - 6), t, font=E.font("jost", 44, 600), fill=E.BROWN, anchor="ls")
        d.text((cx + 60, y + 44), sub, font=E.font("jost", 32, 400), fill=E.BROWN_SOFT, anchor="ls")
        y += 140
    return im


def build(l):
    names = [o for o in l["variations"][0]["options"]]
    designs = []
    for i, slug in enumerate(l["designs"]):
        label = names[i].split(" ", 1)[1] if " " in names[i] else names[i]
        designs.append((slug, label.replace(" ·", "").strip(" ·")))
    photos = [hero(l["designs"][0]), cover(l["name"], l["designs"], len(l["designs"]))] + guides(l["name"], designs)
    photos += [actual_size(l["designs"][0]), good_to_know()]
    photos = photos[:9]
    out = OUT / l["id"]
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.jpg"):
        old.unlink()
    for i, im in enumerate(photos):
        im.convert("RGB").save(out / f"{i + 1}.jpg", quality=84, optimize=True, progressive=True)
    return len(photos)


def main(only):
    data = json.loads((ROOT / "functions" / "etsy-listings.json").read_text())
    counts = {}
    for l in data["listings"]:
        if l["kind"] != "design" or (only and l["id"] not in only):
            continue
        counts[l["id"]] = build(l)
        print(l["id"], counts[l["id"]], flush=True)
    meta = ROOT / "functions" / "tiktok-photos.json"
    m = json.loads(meta.read_text()) if meta.exists() else {"imagesVersion": 0, "photos": {}}
    m["photos"].update(counts)
    m["imagesVersion"] = int(m.get("imagesVersion", 0)) + 1
    meta.write_text(json.dumps(m, indent=1) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
