"""Print-ready sheets for an order: ready-made designs and customer photos (with the frame and caption they
picked) laid out 12 per US Letter page at 300 dpi, with crop marks. Each tile is 2.5 in (the 2 in magnet face
plus the paper that wraps around the edge).

Examples:
  python3 tools/print_sheet.py -o order-1042.pdf places/chicago fall/cozy-season fall/cozy-season
  python3 tools/print_sheet.py -o photos.pdf --frame polaroid --caption "Summer 2026" ~/Downloads/IMG_*.jpg
  python3 tools/print_sheet.py -o mix.pdf christmas/believe --frame holly photo1.jpg photo2.jpg

Arguments are designs (<collection>/<slug>) or photo files; --frame/--caption apply to the photos that follow.
Add --copies N to repeat everything N times.
"""
import argparse
import base64
import io
import json
import os
import pathlib
import subprocess
import tempfile

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
FRAMES = {f["id"]: f for f in json.loads((ROOT / "assets/frames/frames.json").read_text(encoding="utf-8"))}
DPI = 300
TILE = int(2.5 * DPI)          # 750 px
COLS, ROWS = 3, 4
PAGE_W, PAGE_H = int(8.5 * DPI), int(11 * DPI)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def photo_svg(path, frame_id, caption):
    f = FRAMES[frame_id]
    im = Image.open(path)
    im = im.convert("RGB")
    x, y, w, h = f["window"]
    # crop the photo to the window's aspect ratio (centre crop) at print resolution
    target = (int(w * TILE / 600), int(h * TILE / 600))
    iw, ih = im.size
    ar_t, ar_i = target[0] / target[1], iw / ih
    if ar_i > ar_t:
        nw = int(ih * ar_t)
        im = im.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else:
        nh = int(iw / ar_t)
        im = im.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
    im = im.resize(target, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=92)
    data = base64.b64encode(buf.getvalue()).decode()
    frame_svg = (ROOT / "assets/frames" / f"{frame_id}.svg").read_text(encoding="utf-8")
    inner = frame_svg.split(">", 1)[1].rsplit("</svg>", 1)[0] if frame_id != "none" else ""
    r = f["radius"]
    clip = f'<clipPath id="win"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/></clipPath>'
    cap = ""
    if f["caption"] and caption:
        cap = (f'<text x="300" y="{y + h + (600 - y - h) * 0.52:.0f}" text-anchor="middle" font-family="\'Playfair Display\', Georgia, serif" '
               f'font-style="italic" font-weight="700" font-size="38" fill="#3A2418">{esc(caption)}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600"><defs>{clip}</defs>'
            f'<rect width="600" height="600" fill="#FFFFFF"/>'
            f'<image href="data:image/jpeg;base64,{data}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" clip-path="url(#win)"/>'
            f'{inner}{cap}</svg>')


def render(svgs):
    """Render 600-unit SVG strings to 750 px PNGs with the site's fonts."""
    with tempfile.TemporaryDirectory() as tmp:
        jobs = []
        for i, s in enumerate(svgs):
            src = os.path.join(tmp, f"{i}.svg")
            pathlib.Path(src).write_text(s, encoding="utf-8")
            jobs.append((src, os.path.join(tmp, f"{i}.png")))
        pathlib.Path(tmp, "jobs.json").write_text(json.dumps(jobs))
        npm_root = subprocess.check_output(["npm", "root", "-g"]).decode().strip()
        subprocess.run(["node", str(ROOT / "tools/raster.js"), os.path.join(tmp, "jobs.json"), str(ROOT / "tools/fonts"), str(TILE / 600)],
                       check=True, env={**os.environ, "NODE_PATH": npm_root})
        return [Image.open(p).convert("RGB").copy() for _, p in jobs]


def sheets(tiles):
    pages = []
    mx = (PAGE_W - COLS * TILE) // 2
    my = (PAGE_H - ROWS * TILE) // 2
    for start in range(0, len(tiles), COLS * ROWS):
        page = Image.new("RGB", (PAGE_W, PAGE_H), "white")
        d = ImageDraw.Draw(page)
        for k, t in enumerate(tiles[start:start + COLS * ROWS]):
            c, r = k % COLS, k // COLS
            x, y = mx + c * TILE, my + r * TILE
            page.paste(t.resize((TILE, TILE)), (x, y))
        # crop marks on the outer grid lines
        for c in range(COLS + 1):
            x = mx + c * TILE
            d.line([x, my - 60, x, my - 15], fill="black", width=2)
            d.line([x, my + ROWS * TILE + 15, x, my + ROWS * TILE + 60], fill="black", width=2)
        for r in range(ROWS + 1):
            y = my + r * TILE
            d.line([mx - 60, y, mx - 15, y], fill="black", width=2)
            d.line([mx + COLS * TILE + 15, y, mx + COLS * TILE + 60, y], fill="black", width=2)
        pages.append(page)
    return pages


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--copies", type=int, default=1)
    ap.add_argument("items", nargs="+")
    args, rest = ap.parse_known_args()
    # walk the raw argv so --frame/--caption apply to the photos after them
    import sys
    frame, caption, items = "none", "", []
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-o", "--out", "--copies"):
            i += 2
            continue
        if a == "--frame":
            frame = argv[i + 1]
            i += 2
            continue
        if a == "--caption":
            caption = argv[i + 1]
            i += 2
            continue
        p = pathlib.Path(os.path.expanduser(a))
        if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp", ".heic") and p.exists():
            items.append(photo_svg(p, frame, caption))
        else:
            svg = ROOT / "designs" / f"{a}.svg"
            if not svg.exists():
                raise SystemExit(f"not a photo or design: {a}")
            items.append(svg.read_text(encoding="utf-8"))
        i += 1
    items = items * args.copies
    pages = sheets(render(items))
    pages[0].save(args.out, "PDF", resolution=DPI, save_all=True, append_images=pages[1:])
    print(f"{args.out}: {len(items)} magnets on {len(pages)} page(s)")


if __name__ == "__main__":
    main()
