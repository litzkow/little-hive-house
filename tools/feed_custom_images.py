"""assets/feed/custom/<id>.jpg (1200 x 1200): the square picture of each kind of business (biz-<kind>) and each
Personalize theme (pz-<theme>) for the Google / Instagram product list (build.py write_google_feed): four of its designs,
2 x 2, on cream. Uses the 600 px drawings tools/etsy_custom.py makes (or makes them).  python3 tools/feed_custom_images.py"""
import pathlib
import sys

from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import biz_designs as B          # noqa: E402
import design_kits as K          # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "feed" / "custom"
ART = pathlib.Path("/tmp/lhh-etsy-custom")


def picture(fid, designs):
    seen, pick = set(), []
    for d in designs:
        if d["row"] not in seen:
            seen.add(d["row"]); pick.append(d)
    pick = (pick + [d for d in designs if d not in pick])[:4]
    ART.mkdir(exist_ok=True)
    todo = [d for d in pick if not (ART / f"{d['slug']}.png").exists()]
    if todo:
        B.render_batch(todo, size=600, out=ART, ext="png")
    im = Image.new("RGB", (1200, 1200), "#FFF6E5")
    for i, d in enumerate(pick):
        t = Image.open(ART / f"{d['slug']}.png").convert("RGB").resize((560, 560), Image.LANCZOS)
        im.paste(t, (26 + (i % 2) * 588, 26 + (i // 2) * 588))
    im.save(OUT / f"{fid}.jpg", quality=86, optimize=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for k in K.K:
        picture(f"biz-{k['key']}", [d for d in B.DESIGNS if d["set"] == k["key"]])
    for key, meta in B.SETS.items():
        if meta["page"] == "personalize":
            picture(f"pz-{key[2:]}", [d for d in B.DESIGNS if d["set"] == key])
    print(len(list(OUT.glob("*.jpg"))), "pictures")


if __name__ == "__main__":
    main()
