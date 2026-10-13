"""Copies the chosen first-version designs (tools/curation.py CLASSICS) from versions/v3/designs/ into
designs/<collection>/<slug>.svg so they build, render and print like every other design.
Run: python3 tools/import_classics.py"""
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from curation import CLASSICS  # noqa: E402

for (col, slug), (old_col, old_slug, _title) in CLASSICS.items():
    src = ROOT / "versions/v3/designs" / old_col / f"{old_slug}.svg"
    dst = ROOT / "designs" / col / f"{slug}.svg"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or dst.read_bytes() != src.read_bytes():
        shutil.copyfile(src, dst)
        print("copied", dst.relative_to(ROOT))
