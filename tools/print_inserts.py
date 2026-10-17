"""Printable inserts for the packages (print at home, US Letter):

  print-files/thank-you-cards.pdf   4 thank-you cards per sheet (4.25 x 5.5 in each), cut on the small marks
  print-files/kraft-labels.pdf      2 in round labels for Koala N-RLK2-25 / Avery 22807 sheets (3 x 4, 12 per sheet):
                                    page 1 alignment test (plain paper), page 2 a mix, then one page per design

Kraft labels print in one dark ink (light colours disappear on brown paper). Fonts come from tools/fonts.
Run: python3 tools/print_inserts.py"""
import math
import pathlib

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = pathlib.Path(__file__).resolve().parents[1]
FONTS = ROOT / "functions" / "fonts"
OUT = ROOT / "print-files"
IN = 72
INK, HONEY, MUTED, CREAM = HexColor("#2B2118"), HexColor("#E59A12"), HexColor("#6B5A48"), HexColor("#FFF6E5")
KRAFT_INK = HexColor("#24180F")

for name, file in (("Serif", "DMSerifDisplay-Regular.ttf"), ("Jost", "Jost-Medium.ttf"), ("Caveat", "Caveat-SemiBold.ttf"),
                   ("Script", "DancingScript-SemiBold.ttf"), ("Caps", "JosefinSans-Bold.ttf"), ("Garamond", "CormorantGaramond-SemiBoldItalic.ttf")):
    pdfmetrics.registerFont(TTFont(name, str(FONTS / file)))

# the logo: seven hexagons (assets/favicon / build.py LOGO), centred on (200, 67) in its own units
HEXES = [((200, 34), "h"), ((180.95, 67), "h"), ((219.05, 67), "s"), ((161.9, 100), "h"), ((200, 100), "i"), ((238.1, 100), "h")]


def logo(c, cx, cy, size, fill=HONEY, soft=HexColor("#F6D58A"), ink=INK, mono=None):
    """The hive logo, `size` = overall width in points."""
    k = size / 112.0
    for (hx, hy), kind in HEXES:
        x, y = cx + (hx - 200) * k, cy - (hy - 77) * k
        r = 20 * k
        p = c.beginPath()
        for i in range(6):
            a = math.radians(30 + 60 * i)
            px, py = x + r * math.cos(a), y + r * math.sin(a)
            (p.moveTo if i == 0 else p.lineTo)(px, py)
        p.close()
        col = mono or {"h": fill, "s": soft, "i": ink}[kind]
        c.setFillColor(col)
        c.drawPath(p, fill=1, stroke=0)
    # the little door in the middle hexagon
    c.setFillColor(HexColor("#FFFFFF") if not mono else HexColor("#C9A27A"))
    dx, dy = cx, cy - (100 - 77) * k
    c.roundRect(dx - 6 * k, dy - 15 * k, 12 * k, 17 * k, 6 * k, fill=1, stroke=0)


def arc_text(c, text, cx, cy, r, start_deg, font, size, color, spacing=1.0, inside=False):
    """Text along a circle, centred on start_deg (90 = top), reading clockwise (top) or counter-clockwise (bottom)."""
    c.setFillColor(color)
    widths = [pdfmetrics.stringWidth(ch, font, size) * spacing for ch in text]
    total = sum(widths)
    ang = total / r                          # radians covered
    sign = -1 if not inside else 1
    a = math.radians(start_deg) - sign * ang / 2
    for ch, w in zip(text, widths):
        mid = a + sign * (w / 2) / r
        x, y = cx + r * math.cos(mid), cy + r * math.sin(mid)
        c.saveState()
        c.translate(x, y)
        c.rotate(math.degrees(mid) + (-90 if not inside else 90))
        c.setFont(font, size)
        c.drawCentredString(0, 0, ch)
        c.restoreState()
        a += sign * w / r


def centred(c, text, x, y, font, size, color, max_w=None):
    while max_w and pdfmetrics.stringWidth(text, font, size) > max_w and size > 5:
        size -= 0.25
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawCentredString(x, y, text)


def wrap(text, font, size, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(t, font, size) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ================================================================ thank-you cards
CARD_W, CARD_H = 4.25 * IN, 5.5 * IN
BODY = ("Thank you for supporting our little family business. Every magnet in this package was printed, pressed and "
        "packed by hand by the two of us, at home, one small batch at a time. It means the world to us that our work "
        "gets a spot on your fridge.")
ASK = "Love how they turned out? A review or a photo of your fridge helps a small shop more than you know."


def card(c, x0, y0):
    W, H = CARD_W, CARD_H
    cx = x0 + W / 2
    m = 0.32 * IN
    # thin honey frame inside the card
    c.setStrokeColor(HexColor("#EBC67A"))
    c.setLineWidth(0.8)
    c.roundRect(x0 + m, y0 + m, W - 2 * m, H - 2 * m, 10, fill=0, stroke=1)
    top = y0 + H - m
    logo(c, cx, top - 0.52 * IN, 0.5 * IN)
    c.setFont("Caps", 6.4)
    c.setFillColor(MUTED)
    c.drawCentredString(cx, top - 0.98 * IN, "L I T T L E   H I V E   H O U S E")
    centred(c, "Thank you", cx, top - 1.62 * IN, "Serif", 40, INK)
    centred(c, "from our family to yours", cx, top - 1.95 * IN, "Caveat", 15, HexColor("#B9770E"))
    y = top - 2.36 * IN
    for line in wrap(BODY, "Jost", 8.6, W - 2 * m - 0.36 * IN):
        centred(c, line, cx, y, "Jost", 8.6, INK)
        y -= 12.4
    y -= 6
    for line in wrap(ASK, "Jost", 7.6, W - 2 * m - 0.7 * IN):
        centred(c, line, cx, y, "Jost", 7.6, MUTED)
        y -= 10.6
    # signature + QR
    qsize = 0.62 * IN
    w = qr.QrCodeWidget("https://littlehivehouse.com/")
    b = w.getBounds()
    d = Drawing(qsize, qsize, transform=[qsize / (b[2] - b[0]), 0, 0, qsize / (b[3] - b[1]), 0, 0])
    w.barFillColor = INK
    d.add(w)
    qx, qy = x0 + W - m - 0.2 * IN - qsize, y0 + m + 0.2 * IN
    renderPDF.draw(d, c, qx, qy)
    c.setFont("Jost", 6.2)
    c.setFillColor(MUTED)
    c.drawCentredString(qx + qsize / 2, qy - 7, "littlehivehouse.com")
    c.setFont("Caveat", 17)
    c.setFillColor(INK)
    c.drawString(x0 + m + 0.24 * IN, y0 + m + 0.52 * IN, "With love,")
    c.setFont("Caveat", 21)
    c.drawString(x0 + m + 0.24 * IN, y0 + m + 0.25 * IN, "the Little Hive family")


def cut_marks(c):
    c.setStrokeColor(HexColor("#9A9A9A"))
    c.setLineWidth(0.4)
    L = 0.18 * IN
    for x in (0, 4.25 * IN, 8.5 * IN):
        for y in (0, 11 * IN):
            pass
    # marks on the page edges where the two cuts go (middle of each side) + a cross in the centre
    mx, my = 4.25 * IN, 5.5 * IN
    for x1, y1, x2, y2 in ((mx, 0.05 * IN, mx, 0.05 * IN + L), (mx, 11 * IN - 0.05 * IN - L, mx, 11 * IN - 0.05 * IN),
                           (0.05 * IN, my, 0.05 * IN + L, my), (8.5 * IN - 0.05 * IN - L, my, 8.5 * IN - 0.05 * IN, my),
                           (mx - L / 2, my, mx + L / 2, my), (mx, my - L / 2, mx, my + L / 2)):
        c.line(x1, y1, x2, y2)


def thank_you_cards():
    OUT.mkdir(exist_ok=True)
    path = OUT / "thank-you-cards.pdf"
    c = canvas.Canvas(str(path), pagesize=(8.5 * IN, 11 * IN))
    c.setTitle("Thank-you cards · Little Hive House")
    c.setAuthor("Little Hive House")
    for x0, y0 in ((0, 5.5 * IN), (4.25 * IN, 5.5 * IN), (0, 0), (4.25 * IN, 0)):
        card(c, x0, y0)
    cut_marks(c)
    c.showPage()
    c.save()
    return path


# ================================================================ kraft round labels (Avery 22807 layout)
D = 2 * IN
LEFT, TOP = 0.625 * IN, 0.625 * IN
PITCH_X, PITCH_Y = 2.625 * IN, (2 + 7 / 12) * IN


def label_centres():
    out = []
    for r in range(4):
        for col in range(3):
            out.append((LEFT + D / 2 + col * PITCH_X, 11 * IN - (TOP + D / 2 + r * PITCH_Y)))
    return out


def lab_seal(c, x, y):
    k = KRAFT_INK
    c.setStrokeColor(k)
    c.setLineWidth(1.1)
    c.circle(x, y, 0.86 * IN, fill=0, stroke=1)
    c.setLineWidth(0.5)
    c.circle(x, y, 0.62 * IN, fill=0, stroke=1)
    arc_text(c, "LITTLE HIVE HOUSE", x, y, 0.69 * IN, 90, "Caps", 8.6, k, spacing=1.32)
    arc_text(c, "HANDMADE GIFTS", x, y, 0.765 * IN, 270, "Caps", 7.4, k, spacing=1.32, inside=True)
    for side in (1, -1):
        c.setFillColor(k)
        c.circle(x + side * 0.735 * IN, y, 2.2, fill=1, stroke=0)
    logo(c, x, y + 2, 0.66 * IN, mono=k)


def lab_thanks(c, x, y):
    k = KRAFT_INK
    c.setStrokeColor(k)
    c.setLineWidth(0.6)
    c.circle(x, y, 0.86 * IN, fill=0, stroke=1)
    centred(c, "Thank you", x, y + 2, "Script", 24, k)
    c.setFont("Caps", 5.8)
    c.setFillColor(k)
    c.drawCentredString(x, y - 0.22 * IN, "F O R  S H O P P I N G  S M A L L")
    logo(c, x, y + 0.42 * IN, 0.2 * IN, mono=k)
    c.setLineWidth(0.5)
    c.line(x - 0.28 * IN, y - 0.42 * IN, x + 0.28 * IN, y - 0.42 * IN)


def heart_path(c, x, y, s):
    p = c.beginPath()
    p.moveTo(x, y - s * 0.35)
    p.curveTo(x - s * 0.9, y + s * 0.25, x - s * 0.45, y + s * 0.85, x, y + s * 0.4)
    p.curveTo(x + s * 0.45, y + s * 0.85, x + s * 0.9, y + s * 0.25, x, y - s * 0.35)
    p.close()
    return p


def lab_handmade(c, x, y):
    k = KRAFT_INK
    c.setStrokeColor(k)
    c.setLineWidth(0.6)
    c.setDash(2, 2.2)
    c.circle(x, y, 0.84 * IN, fill=0, stroke=1)
    c.setDash()
    centred(c, "handmade", x, y + 0.04 * IN, "Caveat", 30, k)
    c.setFont("Caps", 7.2)
    c.setFillColor(k)
    c.drawCentredString(x, y - 0.26 * IN, "W I T H   L O V E")
    c.setFillColor(k)
    c.drawPath(heart_path(c, x, y + 0.42 * IN, 8), fill=1, stroke=0)


def lab_gift(c, x, y):
    k = KRAFT_INK
    c.setStrokeColor(k)
    c.setLineWidth(1.0)
    c.circle(x, y, 0.86 * IN, fill=0, stroke=1)
    c.setLineWidth(0.4)
    c.circle(x, y, 0.8 * IN, fill=0, stroke=1)
    c.setFont("Caps", 7)
    c.setFillColor(k)
    c.drawCentredString(x, y + 0.3 * IN, "A   L I T T L E")
    centred(c, "gift", x, y - 0.08 * IN, "Garamond", 34, k)
    c.setFont("Caps", 7)
    c.drawCentredString(x, y - 0.36 * IN, "F O R   Y O U")


DESIGNS = [("Seal", lab_seal), ("Thank you", lab_thanks), ("Handmade", lab_handmade), ("Gift", lab_gift)]


def kraft_labels():
    OUT.mkdir(exist_ok=True)
    path = OUT / "kraft-labels.pdf"
    c = canvas.Canvas(str(path), pagesize=(8.5 * IN, 11 * IN))
    c.setTitle("Kraft round labels (Avery 22807 layout) · Little Hive House")
    c.setAuthor("Little Hive House")
    centres = label_centres()
    # page 1: alignment test on plain paper
    c.setStrokeColor(HexColor("#C0392B"))
    c.setLineWidth(0.6)
    for x, y in centres:
        c.circle(x, y, D / 2, fill=0, stroke=1)
        c.line(x - 6, y, x + 6, y)
        c.line(x, y - 6, x, y + 6)
    c.setFillColor(INK)
    c.setFont("Jost", 9)
    c.drawCentredString(4.25 * IN, 0.3 * IN, "Test page: print on PLAIN paper, hold it against a label sheet in front of a window: the red circles should sit on the labels.")
    c.showPage()
    # page 2: a mix (3 of each), then one page per design
    for i, (x, y) in enumerate(centres):
        DESIGNS[i // 3][1](c, x, y)
    c.showPage()
    for _, fn in DESIGNS:
        for x, y in centres:
            fn(c, x, y)
        c.showPage()
    c.save()
    return path


if __name__ == "__main__":
    print(thank_you_cards())
    print(kraft_labels())
