"""The picture at the top of each bulk-order page (assets/occasions/hero-<page>.webp, 1400 x 963): a fridge door with
example magnets from the design gallery (assets/occasions/<slug>.webp, tools/biz_designs.py). Needs google-chrome.
  python3 tools/hero_scenes.py"""
import pathlib, subprocess, tempfile
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OCC = ROOT / "assets" / "occasions"
W, H = 800, 550

DOOR = ("background:linear-gradient(100deg,#efeae2 0%,#fbfaf7 34%,#f3efe8 58%,#fdfcf9 80%,#f1ede6 100%);position:relative;overflow:hidden;")


def mag(slug, x, y, size, rot=0, z=1):
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:{size}px;height:{size}px;transform:rotate({rot}deg);z-index:{z};border-radius:3px;'
            f'background:url(file://{OCC}/{slug}.webp) center/cover;box-shadow:0 {size*.03:.1f}px {size*.07:.1f}px rgba(60,45,30,.30),0 1px 2px rgba(0,0,0,.2)"></div>')


def hero(name, mags):
    handle = ('<div style="position:absolute;right:26px;top:70px;width:15px;height:280px;border-radius:20px;'
              'background:linear-gradient(90deg,#d6d1c9,#f7f5f1 45%,#c6c0b7);box-shadow:-2px 3px 8px rgba(0,0,0,.12)"></div>')
    html = f'<!doctype html><html><head><meta charset="utf-8"><style>*{{margin:0;padding:0}}html,body{{width:{W}px;height:{H}px;overflow:hidden}}</style></head><body><div style="width:{W}px;height:{H}px;{DOOR}">{handle}{"".join(mag(*m) for m in mags)}</div></body></html>'
    tmp = pathlib.Path(tempfile.mkdtemp())
    (tmp / "p.html").write_text(html, encoding="utf-8")
    png = tmp / "o.png"
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--window-size={W},{H}", "--force-device-scale-factor=1.75", "--virtual-time-budget=2000", f"--screenshot={png}", f"file://{tmp / 'p.html'}"],
                   check=True, capture_output=True)
    Image.open(png).convert("RGB").resize((1400, 963), Image.LANCZOS).save(OCC / f"{name}.webp", quality=86, method=6)
    print(name)


if __name__ == "__main__":
    # three rows on a fridge door, slightly overlapping, a little tilt each: big ones in front
    hero("hero-personalize", [("p-pets-1", 34, 40, 200, -4), ("p-family-2", 248, 22, 180, 3), ("p-baby-2", 440, 36, 196, -2), ("p-kitchen-1", 612, 60, 150, 5),
                              ("p-grandparents-1", 70, 270, 196, 3), ("p-love-4", 282, 232, 178, -3, 2), ("p-home-1", 470, 262, 186, 2), ("p-travel-3", 640, 236, 130, -5),
                              ("p-faith-1", 640, 380, 140, 4)])
    hero("hero-business", [("pizza-night", 34, 40, 200, -4), ("dental-coupon", 248, 22, 180, 3), ("realtor-photo", 440, 36, 196, -2), ("cafe-punch", 610, 64, 150, 5),
                           ("clean-word", 70, 270, 196, 3), ("plumber-hazard", 282, 230, 178, -3, 2), ("medspa-qr", 470, 262, 186, 2), ("barber-badge", 640, 236, 130, -5),
                           ("lawn-useful", 640, 380, 140, 4)])
    hero("hero-weddings", [("wed-arch", 40, 40, 210, -3), ("wed-photo", 266, 24, 230, 2), ("wed-botanical", 516, 48, 200, -2),
                           ("wed-engaged", 90, 286, 190, 4), ("wed-qr", 300, 284, 180, -3), ("wed-bigdate", 500, 280, 196, 3)])
    hero("hero-graduation", [("grad-year-navy", 40, 40, 210, -3), ("grad-photo", 268, 24, 230, 2), ("college-pennant", 520, 46, 196, -2),
                             ("grad-polaroid", 86, 286, 190, 4), ("grad-party-qr", 300, 290, 176, -3), ("grad-year-black", 498, 280, 196, 3)])
    hero("hero-parties", [("party-birthday", 40, 40, 210, -3), ("party-baby-photo", 270, 24, 220, 2), ("party-retire", 512, 46, 200, -2),
                          ("party-kid", 86, 288, 186, 4), ("party-photo", 296, 284, 190, -3), ("party-fiesta", 506, 286, 190, 3)])
