"""Pre-renders every design SVG to assets/art/<collection>/<slug>.webp (600 px) for the website.
Only redraws files whose SVG is newer than the WebP. The SVGs stay the print masters.

Also writes the email thumbnails (emails can't show WebP or SVG reliably):
  assets/email/thumbs/<collection>/<slug>.jpg  240 px JPG of every design render
  assets/email/thumbs/frames/<frame-id>.jpg     240 px JPG of every photo frame over the sample photo
Each one is only (re)made when it is missing or older than its source."""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
DESIGNS, OUT, FONTS = ROOT / "designs", ROOT / "assets" / "art", ROOT / "tools" / "fonts"
FRAMES, THUMBS = ROOT / "assets" / "frames", ROOT / "assets" / "email" / "thumbs"
THUMB_PX = 240


def _stale(src, dst, force=False):
    return force or not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime


def _rasterize(svgs, tmp):
    """SVG files -> transparent 600 px PNG paths (same order), drawn by Chromium with the real fonts."""
    spec = [(str(s), os.path.join(tmp, f"{i}.png")) for i, s in enumerate(svgs)]
    pathlib.Path(tmp, "jobs.json").write_text(json.dumps(spec))
    npm_root = subprocess.check_output(["npm", "root", "-g"]).decode().strip()
    subprocess.run(["node", str(ROOT / "tools" / "raster.js"), os.path.join(tmp, "jobs.json"), str(FONTS)],
                   check=True, env={**os.environ, "NODE_PATH": npm_root})
    return [png for _, png in spec]


def _save_thumb(img, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    img = img.convert("RGB").resize((THUMB_PX, THUMB_PX), Image.LANCZOS)
    img.save(dst, "JPEG", quality=84, optimize=True, progressive=True)


def email_thumbs(force=False):
    """240 px JPGs for emails from the WebP/PNG renders, plus photo-frame previews. Only missing/outdated ones."""
    made = 0
    for src in sorted(list(OUT.glob("*/*.webp")) + list(OUT.glob("*/*.png"))):
        dst = THUMBS / src.parent.name / f"{src.stem}.jpg"
        if _stale(src, dst, force):
            with Image.open(src) as im:
                _save_thumb(im, dst)
            made += 1
    sample = FRAMES / "sample.svg"
    frames = [f for f in sorted(FRAMES.glob("*.svg")) if f.stem != "sample"]
    todo = [f for f in frames if _stale(f, THUMBS / "frames" / f"{f.stem}.jpg", force)
            or (sample.exists() and _stale(sample, THUMBS / "frames" / f"{f.stem}.jpg"))]
    if todo and sample.exists():
        try:
            with tempfile.TemporaryDirectory() as tmp:
                pngs = _rasterize([sample] + todo, tmp)
                with Image.open(pngs[0]) as base:
                    photo = base.convert("RGBA")
                for f, png in zip(todo, pngs[1:]):
                    with Image.open(png) as fr:
                        _save_thumb(Image.alpha_composite(photo, fr.convert("RGBA")), THUMBS / "frames" / f"{f.stem}.jpg")
                    made += 1
        except (OSError, subprocess.CalledProcessError) as e:  # no Chromium here: keep the old frame thumbs
            print(f"frame thumbs skipped ({e})")
    print(f"email thumbs: {made} written" if made else "email thumbs up to date")


def main(force=False):
    jobs = []
    for svg in sorted(DESIGNS.glob("*/*.svg")):
        webp = OUT / svg.parent.name / f"{svg.stem}.webp"
        if force or not webp.exists() or webp.stat().st_mtime < svg.stat().st_mtime:
            webp.parent.mkdir(parents=True, exist_ok=True)
            jobs.append((svg, webp))
    if not jobs:
        print("art up to date")
    else:
        with tempfile.TemporaryDirectory() as tmp:
            for (svg, webp), png in zip(jobs, _rasterize([s for s, _ in jobs], tmp)):
                Image.open(png).convert("RGB").save(webp, "WEBP", quality=86, method=6)
        print(f"rendered {len(jobs)} designs")
    email_thumbs(force)


if __name__ == "__main__":
    main("--force" in sys.argv)
