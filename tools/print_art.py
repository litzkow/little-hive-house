"""Print-resolution renders of every design the shop shows: assets/print/<collection>/<slug>.jpg, 1200 px (about
580 ppi on the printed 2.08 in picture), drawn by Chromium with the real fonts (tools/raster.js, scale 2).
The print server (functions/printsheet.js) uses these and falls back to the 600 px website WebP.
Only (re)renders files that are missing or older than their SVG. Run: python3 tools/print_art.py [--force]"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from catalog import COLLECTIONS  # noqa: E402

DESIGNS, OUT, FONTS = ROOT / "designs", ROOT / "assets" / "print", ROOT / "tools" / "fonts"


def main(force=False):
    jobs = []
    for c in COLLECTIONS:
        for slug in c["order"]:
            svg, jpg = DESIGNS / c["slug"] / f"{slug}.svg", OUT / c["slug"] / f"{slug}.jpg"
            if svg.exists() and (force or not jpg.exists() or jpg.stat().st_mtime < svg.stat().st_mtime):
                jobs.append((svg, jpg))
    if not jobs:
        print("print art up to date")
        return
    with tempfile.TemporaryDirectory() as tmp:
        spec = [(str(s), os.path.join(tmp, f"{i}.png")) for i, (s, _) in enumerate(jobs)]
        pathlib.Path(tmp, "jobs.json").write_text(json.dumps(spec))
        npm_root = subprocess.check_output(["npm", "root", "-g"]).decode().strip()
        subprocess.run(["node", str(ROOT / "tools" / "raster.js"), os.path.join(tmp, "jobs.json"), str(FONTS), "2"],
                       check=True, env={**os.environ, "NODE_PATH": npm_root})
        for (_, jpg), (_, png) in zip(jobs, spec):
            jpg.parent.mkdir(parents=True, exist_ok=True)
            Image.open(png).convert("RGB").save(jpg, "JPEG", quality=90, optimize=True, progressive=True)
    print(f"rendered {len(jobs)} print files")


if __name__ == "__main__":
    main("--force" in sys.argv)
