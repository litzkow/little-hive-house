"""Builds the Etsy listing photos (etsy/img/<listing>/<n>.jpg) and keeps functions/etsy-listings.json in step with the site.

Rules from the owners (Nov 2026):
- the magnets are the real designs, exactly as on the site, in the site's order (collections/<slug>.html: the designs
  shown first, then the "See more" ones), numbered the same way in the Etsy menu and in the design guide photos;
- a magnet is a 2 x 2 in square with square (not rounded) corners, shown at its real size next to real things;
- lifestyle photos: a background photo made by an image AI (tools/etsy_scenes/, no products in it) that suits the
  collection, with the real magnet artwork laid on top here (shadows, thickness, the scene's own light over them).

Usage:  CHROME=/usr/bin/google-chrome NODE_PATH=<dir with playwright> python3 tools/etsy_photos.py [listing ...]
Then raise "imagesVersion" in functions/etsy-listings.json (this script does it) and publish from the Hive Admin.
"""
import html as htmlmod
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCENES = ROOT / "tools" / "etsy_scenes"
FONTS = ROOT / "tools" / "fonts"
OUT = ROOT / "etsy" / "img"
LISTINGS = ROOT / "functions" / "etsy-listings.json"
CACHE = pathlib.Path(tempfile.gettempdir()) / "lhh-etsy-art"

CREAM, CREAM_LIGHT, HONEY, BROWN, BROWN_SOFT, LINES = "#FFF6E5", "#FFFCF4", "#F2A81D", "#2B2118", "#6A5845", "#E8D6B3"
W, H = 3000, 2250            # the guide and detail photos, 4:3
LW, LH = 2560, 1440          # lifestyle photos: the whole AI scene (1280 x 720), nothing around it cut off
BIGGER = 1.45                # owners: the magnets a bit bigger than true scale, so they read well in the photo

# Which scene suits which collection; crop = the part of the 1280 x 720 scene shown (all of it, so the props around
# stay whole); inch = pixels per inch in the scene (from the cup / mug next to the magnets), times BIGGER.
FULL = (0, 0, 1280, 720)
# one scene per collection (owners: never the same background twice); light = where the shadows fall
_SCENES = {  # name: (pixels per inch in the scene, from the cup or mug in it)
    "linen": 67, "latin": 62, "europe": 66, "christmas": 70, "horror": 66,
    "mexico": 66, "puerto-rico": 64, "philippines": 60, "ireland": 64, "americana": 62, "india": 64, "korea": 64,
    "japan": 62, "greece": 62, "france": 64, "places": 62, "world": 60, "ink": 64, "sketch": 62, "fall": 66,
    "halloween": 66, "holidays": 62, "summer": 58, "pets": 64, "kitchen": 64, "fairy": 64, "myth": 62, "night": 64,
    "flowers": 64, "library": 64, "artist": 62, "wise": 64, "bee": 66, "brasil": 64, "italia": 64,
    "retro": 64, "family": 64, "gift": 64, "garden": 62,
}
SCENE = {k: {"file": f"bg-{k}.jpg", "crop": FULL, "inch": v, "light": (1, 0.6)} for k, v in _SCENES.items()}
# the fridge door: the window and the plant stay in; the door is wide, so the magnets get more help to read
SCENE["fridge"] = {"file": "bg-fridge.jpg", "crop": (0, 40, 1100, 659), "inch": 50, "light": (1, 0.35)}
COLLECTION_SCENE = {
    "places": "places", "world": "world", "ink-cities": "ink", "city-sketches": "sketch", "fall": "fall",
    "halloween": "halloween", "christmas": "christmas", "holidays": "holidays", "summer": "summer",
    "americana": "americana", "mexico": "mexico", "ireland": "ireland", "italia": "italia", "puerto-rico": "puerto-rico",
    "philippines": "philippines", "india": "india", "korea": "korea", "japan": "japan", "brasil": "brasil",
    "greece": "greece", "france": "france", "bee-kind": "bee", "furry-friends": "pets", "kitchen-words": "kitchen",
    "bumper-stickers": "retro", "night-sky": "night", "great-masters": "artist", "horror": "horror",
    "mythology": "myth", "home-notes": "linen", "birth-flowers": "flowers", "storybook-classics": "library",
    "fairy-tales": "fairy", "wise-words": "wise",
}
PHOTO_SCENE = {"photo-magnets": "gift", "pet-photo-magnets": "garden", "family-photo-magnets": "family"}
# photo-magnet listings: sample customer magnets (assets/showcase, made with the real print renderer)
PHOTO_SETS = {
    "photo-magnets": (["family-1", "travel-1", "wedding-1", "baby-1", "graduation-1"],
                      ["family-2", "travel-2", "wedding-2", "baby-2", "graduation-2", "travel-3"]),
    "pet-photo-magnets": (["pets-1", "pets-2", "pets-3"], ["pets-2", "pets-3", "pets-1"]),
    "family-photo-magnets": (["family-1", "family-2", "family-3", "baby-2"],
                             ["family-3", "baby-1", "family-2", "graduation-3", "family-1", "baby-3"]),
}


# ---------- fonts ----------
def font(name, size, weight=None):
    path = {"josefin": "JosefinSans[wght].ttf", "jost": "Jost[wght].ttf", "caveat": "Caveat-SemiBold.ttf"}[name]
    f = ImageFont.truetype(str(FONTS / path), size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def text_center(d, xy, s, f, fill, spacing=0):
    if spacing:
        widths = [d.textlength(ch, font=f) + spacing for ch in s]
        x = xy[0] - (sum(widths) - spacing) / 2
        for ch, w in zip(s, widths):
            d.text((x, xy[1]), ch, font=f, fill=fill, anchor="ls")
            x += w
    else:
        d.text(xy, s, font=f, fill=fill, anchor="ms")


# ---------- the designs, as on the site ----------
def site_designs(col):
    """[(slug, name)] in the order the site shows them; a "-classic" design whose name repeats gets " Classic"."""
    h = (ROOT / "collections" / f"{col}.html").read_text()
    seen, out = set(), []
    for slug, name in re.findall(r'data-add="%s/([a-z0-9-]+)" data-name="([^"]*)"' % re.escape(col), h):
        if slug not in seen:
            seen.add(slug)
            out.append([slug, htmlmod.unescape(name)])
    names = [n for _, n in out]
    for d in out:
        if d[0].endswith("-classic") and names.count(d[1]) > 1:
            d[1] += " Classic"
    return [tuple(d) for d in out]


def option_name(i, name, limit=20):
    """Etsy menu entry: "07 Pão de Queijo", cut at a word to Etsy's 20 characters."""
    s = f"{i:02d} {name}"
    if len(s) <= limit:
        return s
    words, cut = s.split(" "), ""
    for w in words:
        if len(cut) + len(w) + (1 if cut else 0) > limit:
            break
        cut = f"{cut} {w}" if cut else w
    small = {"de", "do", "da", "dos", "das", "com", "a", "e", "é", "o", "the", "of", "and", "to", "for", "in", "y", "la",
             "el", "los", "las", "di", "del", "della", "is", "my", "on", "at", "an", "with", "your", "you", "me", "&"}
    parts = cut.split(" ")
    while len(parts) > 2 and (parts[-1].lower().strip(",") in small or parts[-1] in ("é", "&")):
        parts.pop()
    return " ".join(parts).rstrip(" ,&-–—:;")


def render_art(col, slugs):
    """Design SVGs -> 1200 px PNGs (cached), drawn by Chromium with the shop's fonts (tools/raster.js)."""
    out = CACHE / col
    out.mkdir(parents=True, exist_ok=True)
    jobs = [[str(ROOT / "designs" / col / f"{s}.svg"), str(out / f"{s}.png")] for s in slugs
            if not (out / f"{s}.png").exists()]
    if jobs:
        jf = out / "jobs.json"
        jf.write_text(json.dumps(jobs))
        subprocess.run(["node", str(ROOT / "tools" / "raster.js"), str(jf), str(FONTS), "2"], check=True)
    return {s: out / f"{s}.png" for s in slugs}


# ---------- a real-looking magnet in a scene ----------
def _shade_map(bg):
    L = np.asarray(bg.convert("L").filter(ImageFilter.GaussianBlur(radius=max(bg.size) / 90)), dtype=np.float32)
    return np.clip(L / max(np.percentile(L, 70), 1), 0.55, 1.15)


def magnet_face(img, size):
    art = img.convert("RGB").resize((size, size), Image.LANCZOS)
    a = np.asarray(art, dtype=np.float32) / 255.0
    yy, xx = np.mgrid[0:size, 0:size] / size
    sheen = np.exp(-(((xx * 0.8 + yy * 0.6) - 0.35) ** 2) / 0.02) * 0.06      # light on the glossy front
    a = a + sheen[..., None] * (1 - a)
    edge = np.minimum(np.minimum(xx, 1 - xx), np.minimum(yy, 1 - yy))
    a = a * (0.94 + 0.06 * np.clip(edge / 0.025, 0, 1))[..., None]
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def lifestyle(scene, magnets, seed=1, shadow=0.42, size_out=(LW, LH)):
    """magnets: [(PIL image, cx, cy, angle)] with cx, cy as fractions of the photo; the size is 2 in, real scale."""
    sc = SCENE[scene]
    rng = np.random.default_rng(seed)
    x0c, y0c, x1c, y1c = sc["crop"]
    bg = Image.open(SCENES / sc["file"]).convert("RGB").crop(sc["crop"]).resize(size_out, Image.LANCZOS)
    bg = bg.filter(ImageFilter.UnsharpMask(radius=2, percent=40, threshold=2))
    Wo, Ho = size_out
    size = int(round(2 * sc["inch"] * BIGGER * Wo / (x1c - x0c)))
    light = sc["light"]
    shade = _shade_map(bg)
    canvas = np.asarray(bg, dtype=np.float32)
    for img, fx, fy, angle in magnets:
        tile = magnet_face(img, size)
        mask = Image.new("L", (size, size), 255)
        rt = tile.rotate(angle, resample=Image.BICUBIC, expand=True)
        rm = mask.rotate(angle, resample=Image.BICUBIC, expand=True)
        x0, y0 = int(fx * Wo - rt.width / 2), int(fy * Ho - rt.height / 2)
        for off, blur, strength in ((size * 0.035, size * 0.045, shadow), (size * 0.008, size * 0.008, 0.35)):
            sh = Image.new("L", (Wo, Ho), 0)
            sh.paste(rm, (int(x0 + light[0] * off), int(y0 + light[1] * off)), rm)
            sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(blur)), dtype=np.float32) / 255.0
            canvas *= (1 - sh * strength)[..., None]
        t = max(2, int(size * 0.012))                         # the magnet's thickness, on the side away from the light
        side = Image.new("L", (Wo, Ho), 0)
        for k in range(1, t + 1):
            side.paste(rm, (int(x0 + light[0] * k), int(y0 + light[1] * k)), rm)
        sd = np.asarray(side, dtype=np.float32)[..., None] / 255.0
        edge_col = np.asarray(tile, dtype=np.float32)[[0, -1], :, :].reshape(-1, 3).mean(0) * 0.5 + 18
        canvas = canvas * (1 - sd) + (edge_col * (shade ** 0.85)[..., None]) * sd
        layer = Image.new("RGB", (Wo, Ho)); layer.paste(rt, (x0, y0))
        m = Image.new("L", (Wo, Ho), 0); m.paste(rm, (x0, y0))
        lay = np.asarray(layer, dtype=np.float32) * (shade ** 0.85)[..., None]
        mm = np.asarray(m, dtype=np.float32)[..., None] / 255.0
        canvas = canvas * (1 - mm) + lay * mm
    canvas = np.clip(canvas + rng.normal(0, 2.0, canvas.shape[:2])[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(canvas)


def mag_frac(scene, size_out=(LW, LH)):
    """The magnet's size as a fraction of the photo's width and height."""
    sc = SCENE[scene]
    x0, y0, x1, y1 = sc["crop"]
    px = 2 * sc["inch"] * BIGGER / (x1 - x0) * size_out[0]
    return px / size_out[0], px / size_out[1]


def grid_spots(n, cx, cy, gap_x, gap_y, seed):
    """Up to 6 magnets in a loose grid (2 rows), each a little turned, like set down by hand."""
    rng = np.random.default_rng(seed)
    cols = 3 if n > 4 else 2 if n > 1 else 1
    rows = (n + cols - 1) // cols
    spots = []
    for i in range(n):
        r, c = divmod(i, cols)
        in_row = min(cols, n - r * cols)
        x = cx + (c - (in_row - 1) / 2) * gap_x + rng.uniform(-0.008, 0.008)
        y = cy + (r - (rows - 1) / 2) * gap_y + rng.uniform(-0.012, 0.012)
        spots.append((x, y, float(rng.uniform(-4.5, 4.5))))
    return spots


def fridge_spots(n, seed):
    """Magnets put up on a fridge door: not in a grid, a little crooked."""
    rng = np.random.default_rng(seed)
    base = [(0.44, 0.24), (0.68, 0.22), (0.58, 0.55), (0.83, 0.48), (0.43, 0.79), (0.71, 0.81)]
    return [(x + rng.uniform(-0.02, 0.02), y + rng.uniform(-0.02, 0.02), float(rng.uniform(-3.5, 3.5)))
            for x, y in base[:n]]


# ---------- studio photos (cream background) ----------
def cream_bg(w=W, h=H):
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / w) ** 2 + ((yy - h * 0.42) / h) ** 2)
    a = np.array([255, 250, 238], dtype=np.float32)
    b = np.array([248, 234, 205], dtype=np.float32)
    t = np.clip(r / 0.75, 0, 1)[..., None]
    return Image.fromarray((a * (1 - t) + b * t).astype(np.uint8))


def drop_tile(canvas, img, x, y, size, angle=0.0, shadow=0.22):
    """A square magnet on the cream background: sharp corners, soft shadow below."""
    tile = magnet_face(img, size)
    rt = tile.rotate(angle, resample=Image.BICUBIC, expand=True)
    rm = Image.new("L", (size, size), 255).rotate(angle, resample=Image.BICUBIC, expand=True)
    x0, y0 = int(x - rt.width / 2), int(y - rt.height / 2)
    sh = Image.new("L", canvas.size, 0)
    sh.paste(rm, (x0 + int(size * 0.02), y0 + int(size * 0.045)), rm)
    sh = sh.filter(ImageFilter.GaussianBlur(size * 0.05))
    c = np.asarray(canvas, dtype=np.float32) * (1 - np.asarray(sh, dtype=np.float32)[..., None] / 255.0 * shadow)
    canvas = Image.fromarray(c.astype(np.uint8))
    canvas.paste(rt, (x0, y0), rm)
    return canvas


def header(d, kicker, title, y=170):
    text_center(d, (W / 2, y), kicker.upper(), font("josefin", 46, 600), BROWN_SOFT, spacing=9)
    text_center(d, (W / 2, y + 125), title, font("josefin", 112, 700), BROWN)


def design_charts(name, designs, arts):
    """"Pick your design" guides: every design, numbered in the site's order, 6 x 4 per photo."""
    per = 24
    pages = [designs[i:i + per] for i in range(0, len(designs), per)]
    out = []
    for p, page in enumerate(pages):
        im = cream_bg()
        d = ImageDraw.Draw(im)
        kick = f"{name} collection" + (f"  ({p + 1} of {len(pages)})" if len(pages) > 1 else "")
        header(d, kick, "Pick your design", y=150)
        cols, size, gx, gy, top = 6, 330, 455, 470, 420
        left = (W - (cols - 1) * gx) / 2
        for i, (slug, dname) in enumerate(page):
            n = p * per + i + 1
            r, c = divmod(i, cols)
            x, y = left + c * gx, top + r * gy + size / 2
            im = drop_tile(im, Image.open(arts[slug]), x, y, size, 0, shadow=0.18)
            d = ImageDraw.Draw(im)
            num, f1, f2 = f"{n:02d}", font("jost", 34, 700), font("jost", 34, 450)
            label = dname if len(dname) <= 24 else dname[:23].rstrip() + "…"
            wn, wl = d.textlength(num + "  ", font=f1), d.textlength(label, font=f2)
            sx = x - (wn + wl) / 2
            d.text((sx, y + size / 2 + 62), num, font=f1, fill=HONEY, anchor="ls")
            d.text((sx + wn, y + size / 2 + 62), label, font=f2, fill=BROWN, anchor="ls")
        out.append(im)
    return out


def size_photo(img, note="Actual size is\njust right for\na busy fridge", details=None):
    """One magnet with its 2 in x 2 in measure and the details."""
    im = cream_bg()
    size, cx, cy = 1000, 1240, 1170
    im = drop_tile(im, img, cx, cy, size, 0, shadow=0.24)
    d = ImageDraw.Draw(im)
    x0, x1, y0, y1 = cx - size / 2, cx + size / 2, cy - size / 2, cy + size / 2
    col = BROWN
    # measure lines
    d.line([(x0, y0 - 110), (x1, y0 - 110)], fill=col, width=5)
    d.line([(x0, y0 - 140), (x0, y0 - 80)], fill=col, width=5)
    d.line([(x1, y0 - 140), (x1, y0 - 80)], fill=col, width=5)
    lab = font("jost", 60, 600)
    tw = d.textlength("2 in", font=lab)
    bgc = lambda x, y: im.getpixel((int(x), int(y)))           # the paper colour right there, to clear the line under a label
    d.rectangle([cx - tw / 2 - 25, y0 - 150, cx + tw / 2 + 25, y0 - 70], fill=bgc(cx, y0 - 190))
    d.text((cx, y0 - 88), "2 in", font=lab, fill=col, anchor="ms")
    d.line([(x1 + 110, y0), (x1 + 110, y1)], fill=col, width=5)
    d.line([(x1 + 80, y0), (x1 + 140, y0)], fill=col, width=5)
    d.line([(x1 + 80, y1), (x1 + 140, y1)], fill=col, width=5)
    d.rectangle([x1 + 70, cy - 70, x1 + 150, cy + 70], fill=bgc(x1 + 180, cy))
    d.text((x1 + 110, cy - 8), "2", font=lab, fill=col, anchor="ms")
    d.text((x1 + 110, cy + 52), "in", font=lab, fill=col, anchor="ms")
    # handwritten note
    cav = font("caveat", 84)
    for i, line in enumerate(note.split("\n")):
        d.text((x0 - 120, cy - 120 + i * 92), line, font=cav, fill="#C57A0A", anchor="rs")
    # details
    dx, dy = x1 + 300, cy - 260
    d.text((dx, dy), "THE DETAILS", font=font("josefin", 40, 600), fill=BROWN_SOFT, anchor="ls")
    details = details or ["2 x 2 inch square (5 cm)", "Square corners", "Glossy, wipe-clean front",
                          "Strong magnet back", "Printed and pressed by hand"]
    for i, line in enumerate(details):
        d.text((dx, dy + 95 + i * 78), line, font=font("jost", 50, 420), fill=BROWN, anchor="ls")
    return im


def frame_chart():
    h = (ROOT / "photo-magnets.html").read_text()
    frames = json.loads(re.search(r"window.LHH_FRAMES=(\{.*?\});window", h, re.S).group(1))
    vis = [(f["id"], f["name"]) for f in frames["list"] if not f.get("hidden")]
    im = cream_bg()
    d = ImageDraw.Draw(im)
    header(d, f"{len(vis)} frames, captions optional", "Pick a frame style", y=150)
    cols, size, gx, gy, top = 8, 270, 345, 430, 420
    rows = (len(vis) + cols - 1) // cols
    for i, (fid, fname) in enumerate(vis):
        r, c = divmod(i, cols)
        in_row = min(cols, len(vis) - r * cols)
        x = W / 2 + (c - (in_row - 1) / 2) * gx
        y = top + r * gy + size / 2
        im = drop_tile(im, Image.open(ROOT / "assets" / "email" / "thumbs" / "frames" / f"{fid}.jpg"), x, y, size, 0, shadow=0.18)
        d = ImageDraw.Draw(im)
        d.text((x, y + size / 2 + 58), fname, font=font("jost", 32, 500), fill=BROWN, anchor="ms")
    text_center(d, (W / 2, top + rows * gy + 90), "Tell us your frame and caption in the personalization box, or leave it to us.",
                font("jost", 44, 400), BROWN_SOFT)
    return im


def pack_chart(packs):
    im = cream_bg()
    d = ImageDraw.Draw(im)
    header(d, "One photo per magnet, repeat any you like", "Choose your pack", y=150)
    colors = ["#F9D88A", "#F3E7CF", "#E8D6B3", "#F2A81D", "#9C8B78", "#6A5845"]
    rng = np.random.default_rng(3)
    box, gap = 400, 120
    n = len(packs)
    left = W / 2 - ((n - 1) * (box + gap)) / 2
    for i, k in enumerate(packs):
        side = int(round(k ** 0.5)) if int(round(k ** 0.5)) ** 2 == k else int(np.ceil(k ** 0.5))
        rows = int(np.ceil(k / side))
        cell = box / max(side, rows)
        cx, top = left + i * (box + gap), 820
        x0 = cx - side * cell / 2
        for j in range(k):
            r, c = divmod(j, side)
            col = colors[int(rng.integers(0, len(colors)))]
            d.rectangle([x0 + c * cell + 3, top + r * cell + 3, x0 + (c + 1) * cell - 3, top + (r + 1) * cell - 3], fill=col)
        d.text((cx, top + box + 150), str(k), font=font("josefin", 96, 700), fill=BROWN, anchor="ms")
        d.text((cx, top + box + 220), "magnets", font=font("jost", 46, 400), fill=BROWN_SOFT, anchor="ms")
    text_center(d, (W / 2, 1830), "Upload a different photo for each magnet, or repeat your favorites.", font("jost", 50, 400), BROWN_SOFT)
    text_center(d, (W / 2, 1920), "Square, 2 x 2 in, with square corners", font("caveat", 74), "#C57A0A")
    return im


# ---------- per listing ----------
def build(listing, keep_last):
    lid = listing["id"]
    out = OUT / lid
    photos = []
    if listing["kind"] == "design":
        designs = site_designs(lid)
        arts = render_art(lid, [s for s, _ in designs])
        imgs = [Image.open(arts[s]) for s, _ in designs]
        sc = COLLECTION_SCENE[lid]
        first = imgs[:6]
        fx, fy = mag_frac(sc)
        photos.append(lifestyle(sc, [(im, x, y, a) for im, (x, y, a) in zip(first, grid_spots(len(first), 0.52, 0.52, fx * 1.2, fy * 1.2, 7))], seed=3))
        nxt = imgs[6:11] if len(imgs) >= 11 else imgs[-5:]
        photos.append(lifestyle("fridge", [(im, x, y, a) for im, (x, y, a) in zip(nxt, fridge_spots(len(nxt), 5))], seed=4, shadow=0.3))
        photos += design_charts(listing["name"], designs, arts)
        photos.append(size_photo(imgs[0]))
        listing["variations"][0]["options"] = [option_name(i + 1, n) for i, (_, n) in enumerate(designs)]
    else:
        a, b = PHOTO_SETS[lid]
        sh = lambda k: Image.open(ROOT / "assets" / "showcase" / f"{k}.webp")
        fl = [sh(k) for k in b]          # the cover: on the table, close enough to see the photos
        fx, fy = mag_frac(PHOTO_SCENE[lid])
        photos.append(lifestyle(PHOTO_SCENE[lid], [(im, x, y, ang) for im, (x, y, ang) in zip(fl, grid_spots(len(fl), 0.52, 0.52, fx * 1.2, fy * 1.2, 9))], seed=6))
        fr = [sh(k) for k in a]
        photos.append(lifestyle("fridge", [(im, x, y, ang) for im, (x, y, ang) in zip(fr, fridge_spots(len(fr), 2))], seed=5, shadow=0.3))
        photos.append(frame_chart())
        packs = [int(o.split()[0]) for o in listing["variations"][0]["options"]]
        photos.append(pack_chart(packs))
        photos.append(size_photo(sh(a[0]), details=["2 x 2 inch square (5 cm)", "Square corners", "Glossy, wipe-clean front",
                                                    "Strong magnet back", "Your photo, touched up by hand"]))
    photos.append(keep_last)                       # "Good to know" / "How it works" with the logo: unchanged
    out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.jpg"):
        f.unlink()
    for i, p in enumerate(photos):
        p = p.convert("RGB")
        if p.size[0] < 2000:
            p = p.resize((W, H), Image.LANCZOS)
        p.save(out / f"{i + 1}.jpg", quality=90, optimize=True, progressive=True)
    listing["images"] = len(photos)
    return len(photos)


def main(only):
    data = json.loads(LISTINGS.read_text())
    for l in data["listings"]:
        if only and l["id"] not in only:
            continue
        last = Image.open(ROOT / "tools" / "etsy_shop" / ("how-it-works-photo.jpg" if l["kind"] == "photo" else "good-to-know.jpg")).convert("RGB")
        n = build(l, last)
        l["description"] = l["description"].replace("magnets with rounded corners", "magnets with square corners") \
                                           .replace("magnet with rounded corners", "magnet with square corners")
        print(l["id"], n, "photos", len(l["variations"][0]["options"]), "options", flush=True)
    if os.environ.get("BUMP", "1") == "1":
        data["imagesVersion"] = int(data.get("imagesVersion", 1)) + 1
    LISTINGS.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
