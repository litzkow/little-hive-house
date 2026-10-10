"""Print-ready sheets for an order: ready-made designs and customer photos (each with its own frame and
caption) laid out 12 per US Letter page at 300 dpi, with crop marks. Each tile is 2.5 in (the 2 in magnet face
plus the paper that wraps around the edge).

Examples:
  python3 tools/print_sheet.py -o order-1042.pdf places/chicago fall/cozy-season fall/cozy-season
  python3 tools/print_sheet.py -o photos.pdf --frame instant --caption "Summer 2026" ~/Downloads/IMG_*.jpg
  python3 tools/print_sheet.py -o mix.pdf christmas/believe --frame holly photo1.jpg --frame none photo2.jpg
  python3 tools/print_sheet.py -o order-1043.pdf --order order-1043.json --photos ~/Downloads/order-1043/

Arguments are designs (<collection>/<slug>) or photo files. --frame/--caption apply to the photos that follow
them, so every photo can have its own frame. A photo can also carry its own: photo.jpg@frame or
"photo.jpg@frame@Caption text".

--order reads the per-photo list the website records with each photo pack (the "photos" array of the cart line,
or the "Photo 1: ..." lines of the order notes saved as JSON):
  {"count": 9, "photos": [{"file": "IMG_1201.jpg", "frame": "instant", "caption": "Summer 2026"},
                          {"file": "IMG_1202.jpg", "frame": "holly", "caption": ""}]}
Photo files are looked up in --photos (default: next to the JSON). If the pack holds more magnets than photos,
the photos repeat in order to fill it (as promised on the site) unless --no-fill.
Add --copies N to repeat everything N times. List the frames with --frames.
"""
import argparse
import base64
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageOps

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from frames import caption_svg  # noqa: E402

FRAMES = {f["id"]: f for f in json.loads((ROOT / "assets/frames/frames.json").read_text(encoding="utf-8"))}
ALIASES = {"classic": "white", "polaroid": "instant", "honey": "honeycomb", "scallop": "lace", "autumn": "fall", "starry": "baby"}
DPI = 300
TILE = int(2.5 * DPI)          # 750 px
COLS, ROWS = 3, 4
PAGE_W, PAGE_H = int(8.5 * DPI), int(11 * DPI)
PHOTO_EXT = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".gif", ".bmp", ".tif", ".tiff")


def frame_of(fid):
    fid = ALIASES.get(fid, fid)
    if fid not in FRAMES:
        raise SystemExit(f"unknown frame '{fid}'. Frames: {', '.join(FRAMES)}")
    return FRAMES[fid]


def photo_svg(path, frame_id, caption=""):
    """One magnet: the photo centre-cropped into the frame's window, the frame on top, then the caption."""
    f = frame_of(frame_id)
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    x, y, w, h = f["window"]
    # crop the photo to the window's aspect ratio (centre crop) at print resolution (plus a little headroom)
    target = (int(w * TILE / 600 * 1.25), int(h * TILE / 600 * 1.25))
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
    im.save(buf, "JPEG", quality=93)
    data = base64.b64encode(buf.getvalue()).decode()
    inner = ""
    if f["id"] != "none":
        frame_svg = (ROOT / "assets/frames" / f'{f["id"]}.svg').read_text(encoding="utf-8")
        inner = frame_svg.split(">", 1)[1].rsplit("</svg>", 1)[0]
    cap = caption_svg(f, (caption or "").strip()[: (f["caption"] or {}).get("max", 40)]) if f["caption"] else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600">'
            f'<rect width="600" height="600" fill="#FFFFFF"/>'
            f'<image href="data:image/jpeg;base64,{data}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>'
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


def from_order(path, photos_dir, fill=True):
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    lines = data["photos"] if isinstance(data, dict) else data
    base = pathlib.Path(photos_dir).expanduser() if photos_dir else pathlib.Path(path).resolve().parent
    out = []
    for p in lines:
        fp = base / p["file"]
        if not fp.exists():
            raise SystemExit(f"photo not found: {fp}")
        out.append(photo_svg(fp, p.get("frame", "none"), p.get("caption", "")))
    count = data.get("count") if isinstance(data, dict) else None
    if fill and count and out and len(out) < count:
        out = [out[i % len(out)] for i in range(count)]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--out")
    ap.add_argument("--copies", type=int, default=1)
    ap.add_argument("--order", help="per-photo order JSON (file, frame, caption for each photo)")
    ap.add_argument("--photos", help="folder with the order's photo files")
    ap.add_argument("--no-fill", action="store_true", help="do not repeat photos to fill the pack size")
    ap.add_argument("--frames", action="store_true", help="list the frame ids and exit")
    ap.add_argument("--frame", action="append", help=argparse.SUPPRESS)
    ap.add_argument("--caption", action="append", help=argparse.SUPPRESS)
    ap.add_argument("items", nargs="*")
    args, _unknown = ap.parse_known_args()
    if args.frames:
        for f in FRAMES.values():
            print(f'{f["id"]:<14} {f["group"]:<20} {f["name"]}' + ("  (caption)" if f["caption"] else ""))
        return
    if not args.out:
        ap.error("-o/--out is required")
    items = from_order(args.order, args.photos, not args.no_fill) if args.order else []
    # walk the raw argv so --frame/--caption apply to the photos after them
    frame, caption = "none", ""
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-o", "--out", "--copies", "--order", "--photos"):
            i += 2
            continue
        if a.startswith("--") and "=" in a:
            k, v = a.split("=", 1)
            if k == "--frame":
                frame = v
            elif k == "--caption":
                caption = v
            i += 1
            continue
        if a in ("--frame", "--caption"):
            if a == "--frame":
                frame = argv[i + 1]
            else:
                caption = argv[i + 1]
            i += 2
            continue
        if a.startswith("-"):
            i += 1
            continue
        name, own_frame, own_cap = a, None, None
        if "@" in a and not pathlib.Path(os.path.expanduser(a)).exists():
            name, own_frame, *rest = a.split("@")
            own_cap = rest[0] if rest else ""
        p = pathlib.Path(os.path.expanduser(name))
        if p.suffix.lower() in PHOTO_EXT and p.exists():
            items.append(photo_svg(p, own_frame or frame, caption if own_cap is None else own_cap))
        else:
            svg = ROOT / "designs" / f"{name}.svg"
            if not svg.exists():
                raise SystemExit(f"not a photo or design: {a}")
            items.append(svg.read_text(encoding="utf-8"))
        i += 1
    if not items:
        ap.error("nothing to print")
    items = items * args.copies
    pages = sheets(render(items))
    pages[0].save(args.out, "PDF", resolution=DPI, save_all=True, append_images=pages[1:])
    print(f"{args.out}: {len(items)} magnets on {len(pages)} page(s)")


if __name__ == "__main__":
    main()
