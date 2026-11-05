"""The shop's logo magnet as one picture per colour, for "Print together" in Hive Admin (functions/printsheet.js):
assets/print/_shop/logo-cream.jpg and logo-honey.jpg, 1200 px for the 2 in face, drawn exactly like
print-files/logo-magnets.pdf (tools/print_inserts.py logo_magnet). Needs pdftoppm. Run: python3 tools/logo_faces.py"""
import pathlib
import subprocess
import tempfile

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

import print_inserts as P

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "print" / "_shop"
FACE = 2 * P.IN          # the picture is drawn at the 2.02 in size and scaled to the 2 in face, like every design tile


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    variants = (
        ("cream", P.CREAM, dict(), P.INK, P.MUTED, P.HONEY),
        ("honey", HexColor("#F2A81D"), dict(fill=P.INK, soft=HexColor("#5A4026"), ink=HexColor("#FFF6E5")), P.INK, HexColor("#4A3520"), P.INK),
    )
    with tempfile.TemporaryDirectory() as tmp:
        for name, bg, kw, ink, sub, link in variants:
            pdf = pathlib.Path(tmp, f"{name}.pdf")
            c = canvas.Canvas(str(pdf), pagesize=(P.MAG_IMG, P.MAG_IMG))
            P.logo_magnet(c, 0, 0, bg, kw, ink, sub, link)
            c.showPage()
            c.save()
            dpi = 1200 / (P.MAG_IMG / 72)
            subprocess.run(["pdftoppm", "-png", "-r", f"{dpi:.3f}", "-singlefile", str(pdf), str(pathlib.Path(tmp, name))], check=True)
            im = Image.open(pathlib.Path(tmp, f"{name}.png")).convert("RGB").resize((1200, 1200), Image.LANCZOS)
            im.save(OUT / f"logo-{name}.jpg", "JPEG", quality=92, optimize=True)
            print(OUT / f"logo-{name}.jpg")


if __name__ == "__main__":
    main()
