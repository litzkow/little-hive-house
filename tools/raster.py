"""Pre-renders every design SVG to assets/art/<collection>/<slug>.webp (600 px) for the website.
Only redraws files whose SVG is newer than the WebP. The SVGs stay the print masters."""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
DESIGNS, OUT, FONTS = ROOT / "designs", ROOT / "assets" / "art", ROOT / "tools" / "fonts"


def main(force=False):
    jobs = []
    for svg in sorted(DESIGNS.glob("*/*.svg")):
        webp = OUT / svg.parent.name / f"{svg.stem}.webp"
        if force or not webp.exists() or webp.stat().st_mtime < svg.stat().st_mtime:
            webp.parent.mkdir(parents=True, exist_ok=True)
            jobs.append((svg, webp))
    if not jobs:
        print("art up to date")
        return
    with tempfile.TemporaryDirectory() as tmp:
        spec = [(str(s), os.path.join(tmp, f"{i}.png")) for i, (s, _) in enumerate(jobs)]
        pathlib.Path(tmp, "jobs.json").write_text(json.dumps(spec))
        npm_root = subprocess.check_output(["npm", "root", "-g"]).decode().strip()
        subprocess.run(["node", str(ROOT / "tools" / "raster.js"), os.path.join(tmp, "jobs.json"), str(FONTS)],
                       check=True, env={**os.environ, "NODE_PATH": npm_root})
        for (svg, webp), (_, png) in zip(jobs, spec):
            Image.open(png).convert("RGB").save(webp, "WEBP", quality=86, method=6)
    print(f"rendered {len(jobs)} designs")


if __name__ == "__main__":
    main("--force" in sys.argv)
