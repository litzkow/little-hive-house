"""Art printed straight onto the kraft A7 envelopes (5.25 x 7.25 in, Marathon / MOS A7 Kraft, self-seal) that go inside
the shipping mailer. Printed on the FRONT (the side without the flap), lying down: the PDF page is 7.25 x 5.25 in.

Inkjet on brown kraft: there is no white ink and light colours sink into the paper, so everything is dark brown ink
(KRAFT_INK) with a deep honey accent, in lines and type, no big solid areas (they soak, smear and curl the paper).
Nothing within 0.4 in of the edges (the printer's margin and the envelope's seams).

Run: python3 tools/envelopes.py            -> print-files/envelope-<name>.pdf, one per design
     python3 tools/envelopes.py --preview  -> also PNG previews on a kraft background (scratch, for choosing)
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from reportlab.lib.colors import HexColor  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402

import print_inserts as P  # noqa: E402

IN = 72
W, H = 7.25 * IN, 5.25 * IN
INK = P.KRAFT_INK
HONEY = HexColor("#A8640A")        # honey that still reads on kraft (the shop's #E59A12 turns muddy and faint)
SOFT = HexColor("#5A4330")         # a lighter brown for small print
M = 0.4 * IN                       # keep clear of the edges


def caps(c, text, x, y, size, color=INK, spacing=1.6, font="Caps"):
    c.saveState()
    t = c.beginText()
    t.setFont(font, size)
    t.setCharSpace(spacing)
    w = pdfmetrics.stringWidth(text, font, size) + spacing * (len(text) - 1)
    t.setTextOrigin(x - w / 2, y)
    t.setFillColor(color)
    t.textOut(text)
    c.drawText(t)
    c.restoreState()


def centred(c, text, x, y, font, size, color=INK):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawCentredString(x, y, text)


def hexagon(c, x, y, r, stroke=INK, width=0.8, fill=None):
    p = c.beginPath()
    for i in range(6):
        a = math.radians(30 + 60 * i)
        (p.moveTo if i == 0 else p.lineTo)(x + r * math.cos(a), y + r * math.sin(a))
    p.close()
    c.setStrokeColor(stroke)
    c.setLineWidth(width)
    if fill is not None:
        c.setFillColor(fill)
    c.drawPath(p, fill=1 if fill is not None else 0, stroke=1)


def bee(c, x, y, s, angle=0, color=INK, stripe=HONEY):
    """A small line-art bee, s = body length in points, flying towards `angle` degrees."""
    c.saveState()
    c.translate(x, y)
    c.rotate(angle)
    c.setStrokeColor(color)
    c.setLineWidth(max(0.6, s * 0.06))
    # wings
    c.setFillColor(HexColor("#00000000"))
    c.ellipse(-s * 0.18, s * 0.18, s * 0.22, s * 0.62, fill=0, stroke=1)
    c.ellipse(s * 0.02, s * 0.16, s * 0.42, s * 0.52, fill=0, stroke=1)
    # body
    c.ellipse(-s * 0.5, -s * 0.24, s * 0.5, s * 0.24, fill=0, stroke=1)
    c.setStrokeColor(stripe)
    c.setLineWidth(max(0.8, s * 0.09))
    for dx in (-0.16, 0.06):
        c.line(s * dx, -s * 0.21, s * dx, s * 0.21)
    # head + stinger
    c.setFillColor(color)
    c.circle(s * 0.5, 0, s * 0.11, fill=1, stroke=0)
    c.setStrokeColor(color)
    c.setLineWidth(max(0.6, s * 0.05))
    c.line(-s * 0.5, 0, -s * 0.62, 0)
    c.restoreState()


def dotted_path(c, pts, color=SOFT, dot=0.9, gap=5.5):
    """Dots along a smooth path through pts (a bee's flight)."""
    c.setFillColor(color)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / gap))
        for i in range(n):
            t = i / n
            c.circle(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, dot, fill=1, stroke=0)


def curve(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
        out.append((a[0] * p0[0] + a[1] * p1[0] + a[2] * p2[0] + a[3] * p3[0], a[0] * p0[1] + a[1] * p1[1] + a[2] * p2[1] + a[3] * p3[1]))
    return out


def seal(c, x, y, scale=1.0):
    """The round shop seal from the stickers (print_inserts.lab_seal), any size."""
    c.saveState()
    c.translate(x, y)
    c.scale(scale, scale)
    P.lab_seal(c, 0, 0)
    c.restoreState()


# ------------------------------------------------------------------ the designs
def d_seal(c, name=None):
    """1 · Seal: the round shop seal, a line of italic and the shop's line underneath."""
    seal(c, W / 2, H * 0.6, 1.05)
    centred(c, "A little something sweet is inside", W / 2, H * 0.27, "Garamond", 17)
    c.setStrokeColor(HONEY)
    c.setLineWidth(0.9)
    c.line(W / 2 - 0.45 * IN, H * 0.215, W / 2 + 0.45 * IN, H * 0.215)
    caps(c, "HANDMADE FRIDGE MAGNETS  ·  LITTLEHIVEHOUSE.COM", W / 2, M + 4, 6.4, SOFT, 1.5)


def d_hello(c, name=None):
    """2 · Hello from the hive: big script, a bee's dotted flight and the little logo."""
    centred(c, "Hello from the hive!", W / 2, H * 0.5, "Script", 44)
    pts = curve((M + 0.25 * IN, H * 0.24), (W * 0.45, H * 0.02), (W * 0.98, H * 0.18), (W - M - 0.62 * IN, H * 0.68))
    dotted_path(c, pts)
    bee(c, W - M - 0.66 * IN, H * 0.77, 26, angle=24)
    P.logo(c, M + 0.42 * IN, H - M - 0.38 * IN, 0.62 * IN, mono=INK)
    caps(c, "LITTLE HIVE HOUSE", M + 1.62 * IN, H - M - 0.44 * IN, 8.2, INK, 1.9)
    caps(c, "PRINTED, PRESSED & PACKED BY HAND", W / 2, H * 0.31, 7, SOFT, 1.6)
    caps(c, "LITTLEHIVEHOUSE.COM", W / 2, M + 4, 6.6, SOFT, 1.8)


def stamp(c, x, y, w, h):
    """A postage stamp with a perforated edge and the hive in it."""
    c.setStrokeColor(INK)
    c.setLineWidth(0.9)
    c.rect(x, y, w, h, fill=0, stroke=1)
    c.setFillColor(INK)
    step = 6
    for i in range(int(w / step) + 1):
        for yy in (y, y + h):
            c.circle(x + i * step, yy, 1.4, fill=1, stroke=0)
    for i in range(int(h / step) + 1):
        for xx in (x, x + w):
            c.circle(xx, y + i * step, 1.4, fill=1, stroke=0)
    c.setLineWidth(0.5)
    c.rect(x + 5, y + 5, w - 10, h - 10, fill=0, stroke=1)
    P.logo(c, x + w / 2, y + h * 0.58, w * 0.5, mono=INK)
    caps(c, "FROM THE HIVE", x + w / 2, y + 12, 5.8, INK, 1.2)
    caps(c, "2026", x + w / 2, y + h - 17, 6, HONEY, 1.4)


def postmark(c, x, y, r):
    c.setStrokeColor(SOFT)
    c.setLineWidth(0.8)
    c.circle(x, y, r, fill=0, stroke=1)
    c.circle(x, y, r - 5, fill=0, stroke=1)
    P.arc_text(c, "LITTLE HIVE HOUSE", x, y, r - 13, 90, "Caps", 6.4, SOFT, spacing=1.2)
    P.arc_text(c, "HANDMADE", x, y, r - 7.5, 270, "Caps", 6, SOFT, spacing=1.2, inside=True)
    centred(c, "with love", x, y - 3, "Caveat", 12, SOFT)
    for k in range(4):                               # the wavy cancel lines
        yy = y + 12 - k * 8
        pts = [(x + r + 6 + i * 3, yy + 2.2 * math.sin(i / 2.2)) for i in range(34)]
        c.setStrokeColor(SOFT)
        c.setLineWidth(0.7)
        pth = c.beginPath()
        pth.moveTo(*pts[0])
        for p in pts[1:]:
            pth.lineTo(*p)
        c.drawPath(pth, fill=0, stroke=1)


def d_stamp(c, name=None):
    """3 · Special delivery: a hive postage stamp and postmark, and a line to write their name by hand."""
    sw, sh = 1.05 * IN, 1.25 * IN
    stamp(c, W - M - sw, H - M - sh, sw, sh)
    postmark(c, W - M - sw - 1.95 * IN, H - M - 0.55 * IN, 0.5 * IN)
    c.setFont("Serif", 30)
    c.setFillColor(INK)
    c.drawString(M + 0.1 * IN, H * 0.42, "Special delivery")
    c.setFont("Caveat", 17)
    c.setFillColor(HONEY)
    c.drawString(M + 0.12 * IN, H * 0.42 - 26, "happy little things inside, handle with love")
    c.setFont("Caps", 8)
    c.setFillColor(INK)
    c.drawString(M + 0.12 * IN, H * 0.17 + 3, "FOR")
    c.setStrokeColor(INK)
    c.setLineWidth(0.7)
    c.line(M + 0.5 * IN, H * 0.17, W * 0.62, H * 0.17)
    if name:
        c.setFont("Script", 22)
        c.drawString(M + 0.62 * IN, H * 0.17 + 4, name)
    caps(c, "LITTLEHIVEHOUSE.COM", W - M - 1.05 * IN, M + 4, 6.4, SOFT, 1.6)


def d_comb(c, name=None):
    """4 · Honeycomb: a corner of honeycomb with two bees, and "Open me, sweet things inside"."""
    r = 0.33 * IN
    dx, dy = r * math.sqrt(3), r * 1.5
    for row in range(5):
        for col in range(6):
            x = M + r + col * dx + (dx / 2 if row % 2 else 0)
            y = M + r + row * dy
            if col + row > 5 or x > W * 0.52 or y > H * 0.78:
                continue
            honey = (col, row) in ((1, 0), (0, 2), (2, 1))
            hexagon(c, x, y, r, INK, 0.9 if not honey else 1.1, fill=HONEY if honey else None)
    bee(c, W * 0.47, H * 0.5, 22, angle=18)
    bee(c, W * 0.38, H * 0.64, 16, angle=-12)
    c.setFont("Serif", 38)
    c.setFillColor(INK)
    c.drawRightString(W - M - 0.1 * IN, H * 0.56, "Open me!")
    c.setFont("Garamond", 19)
    c.drawRightString(W - M - 0.1 * IN, H * 0.56 - 30, "sweet things inside")
    caps(c, "LITTLE HIVE HOUSE  ·  HANDMADE", W - M - 1.3 * IN, H - M - 0.2 * IN, 7, SOFT, 1.7)


def d_name(c, name=None):
    """5 · Made just for: the customer's first name in script (the app fills it in for each order)."""
    name = name or "Ana"
    caps(c, "MADE JUST FOR", W / 2, H * 0.66, 10, HONEY, 3)
    size = 54
    while pdfmetrics.stringWidth(name, "Script", size) > W - 2.4 * IN and size > 28:
        size -= 2
    centred(c, name, W / 2, H * 0.43, "Script", size)
    for side in (-1, 1):
        c.setStrokeColor(INK)
        c.setLineWidth(0.7)
        x0 = W / 2 + side * 0.5 * IN
        c.line(x0, H * 0.33, x0 + side * 1.4 * IN, H * 0.33)
    hexagon(c, W / 2, H * 0.33, 4.2, INK, 0.8, fill=HONEY)
    P.logo(c, W / 2, H - M - 0.32 * IN, 0.5 * IN, mono=INK)
    centred(c, "with love, from our little house to your fridge", W / 2, H * 0.21, "Garamond", 14, SOFT)
    caps(c, "LITTLE HIVE HOUSE", W / 2, M + 4, 6.8, INK, 2.2)


def flourish(c, x, y, s, flip=1):
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    p = c.beginPath()
    p.moveTo(x, y)
    p.curveTo(x + flip * s * 0.4, y + s * 0.5, x + flip * s * 0.9, y - s * 0.2, x + flip * s * 1.2, y + s * 0.15)
    c.drawPath(p, fill=0, stroke=1)
    c.circle(x + flip * s * 1.24, y + s * 0.17, 1.6, fill=0, stroke=1)


def d_label(c, name=None):
    """6 · Vintage label: a framed label with double rules, the shop name and 'fridge magnets inside'."""
    bw, bh = 4.6 * IN, 2.7 * IN
    x, y = (W - bw) / 2, (H - bh) / 2
    c.setStrokeColor(INK)
    c.setLineWidth(1.3)
    c.roundRect(x, y, bw, bh, 14, fill=0, stroke=1)
    c.setLineWidth(0.5)
    c.roundRect(x + 6, y + 6, bw - 12, bh - 12, 10, fill=0, stroke=1)
    P.logo(c, W / 2, y + bh - 0.6 * IN, 0.55 * IN, mono=INK)
    c.setFont("Cinzel", 25) if "Cinzel" in pdfmetrics.getRegisteredFontNames() else c.setFont("Serif", 25)
    c.setFillColor(INK)
    c.drawCentredString(W / 2, y + bh * 0.42, "Little Hive House")
    caps(c, "EST. 2026  ·  HANDMADE IN SMALL BATCHES", W / 2, y + bh * 0.42 - 20, 6.6, HONEY, 1.6)
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(W / 2 - 1.2 * IN, y + bh * 0.25, W / 2 + 1.2 * IN, y + bh * 0.25)
    centred(c, "Handle with love  ·  fridge magnets inside", W / 2, y + 0.32 * IN, "Garamond", 14, INK)
    fy = y + bh - 0.6 * IN
    flourish(c, W / 2 - 0.55 * IN, fy, 0.5 * IN, -1)
    flourish(c, W / 2 + 0.55 * IN, fy, 0.5 * IN, 1)


def d_monogram(c, name=None):
    """7 · Monogram: LHH in a thin hexagon, the name and a line under it."""
    cx, cy, r = W / 2, H * 0.6, 0.78 * IN
    hexagon(c, cx, cy, r, INK, 1.2)
    hexagon(c, cx, cy, r - 5, INK, 0.5)
    P.logo(c, cx, cy + 6, 0.62 * IN, mono=INK)
    caps(c, "LHH", cx, cy - 0.46 * IN, 9, INK, 3, font="Cinzel")
    caps(c, "LITTLE HIVE HOUSE", W / 2, H * 0.27, 10, INK, 3.2, font="Cinzel")
    c.setStrokeColor(HONEY)
    c.setLineWidth(0.8)
    c.line(W / 2 - 0.35 * IN, H * 0.225, W / 2 + 0.35 * IN, H * 0.225)
    centred(c, "handmade fridge magnets, made for you", W / 2, H * 0.155, "Garamond", 13, SOFT)


def leaf(c, x, y, ang, s):
    c.saveState()
    c.translate(x, y)
    c.rotate(ang)
    p = c.beginPath()
    p.moveTo(0, 0)
    p.curveTo(s * 0.35, s * 0.28, s * 0.75, s * 0.25, s, 0)
    p.curveTo(s * 0.75, -s * 0.25, s * 0.35, -s * 0.28, 0, 0)
    c.setStrokeColor(INK)
    c.setLineWidth(0.7)
    c.drawPath(p, fill=0, stroke=1)
    c.setLineWidth(0.4)
    c.line(s * 0.08, 0, s * 0.85, 0)
    c.restoreState()


def wreath(c, cx, cy, r):
    """Two laurel branches meeting at the bottom, open at the top."""
    for side in (-1, 1):
        c.setStrokeColor(INK)
        c.setLineWidth(0.8)
        p = c.beginPath()
        pts = []
        for i in range(31):
            a = math.radians(-90 + side * (8 + i * 5.2))
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        c.drawPath(p, fill=0, stroke=1)
        for i in range(2, 31, 3):
            a = -90 + side * (8 + i * 5.2)
            x, y = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
            tang = a + side * 90
            leaf(c, x, y, tang + side * 35, 11)
            leaf(c, x, y, tang - side * 35 + 180 + side * 180, 9)
    c.setFillColor(HONEY)
    c.circle(cx, cy - r, 2.4, fill=1, stroke=0)


def d_wreath(c, name=None):
    """8 · Laurel: a thin laurel wreath around "Handmade for you"."""
    cx, cy = W / 2, H * 0.52
    wreath(c, cx, cy, 1.35 * IN)
    P.logo(c, cx, cy + 1.3 * IN, 0.5 * IN, mono=INK)
    centred(c, "Handmade", cx, cy + 6, "Script", 34)
    centred(c, "for you", cx, cy - 20, "Garamond", 18)
    caps(c, "LITTLE HIVE HOUSE", cx, cy - 0.78 * IN, 7.4, INK, 2.4)
    caps(c, "LITTLEHIVEHOUSE.COM", W / 2, M + 2, 6.2, SOFT, 1.8)


def d_words(c, name=None):
    """9 · Words only: "from our little house to your fridge", set like letterpress."""
    P.logo(c, W / 2, H * 0.8, 0.5 * IN, mono=INK)
    caps(c, "FROM OUR LITTLE HOUSE", W / 2, H * 0.64, 12, INK, 4, font="Cinzel")
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(W / 2 - 1.6 * IN, H * 0.58, W / 2 - 0.2 * IN, H * 0.58)
    c.line(W / 2 + 0.2 * IN, H * 0.58, W / 2 + 1.6 * IN, H * 0.58)
    hexagon(c, W / 2, H * 0.58, 4, INK, 0.7, fill=HONEY)
    centred(c, "to your fridge", W / 2, H * 0.43, "Garamond", 46)
    caps(c, "LITTLE HIVE HOUSE  ·  EST. 2026", W / 2, H * 0.27, 7.4, HONEY, 2.2)
    caps(c, "HANDMADE IN SMALL BATCHES", W / 2, M + 4, 6.4, SOFT, 1.8)


def d_tag(c, name=None):
    """10 · Gift tag: a luggage tag with a string, the order number on it (the app fills it in)."""
    tw, th = 4.2 * IN, 2.35 * IN
    x, y = (W - tw) / 2 + 0.25 * IN, (H - th) / 2
    cut = 0.45 * IN
    c.setStrokeColor(INK)
    c.setLineWidth(1.1)
    p = c.beginPath()
    p.moveTo(x + cut, y)
    p.lineTo(x + tw, y)
    p.lineTo(x + tw, y + th)
    p.lineTo(x + cut, y + th)
    p.lineTo(x, y + th - cut)
    p.lineTo(x, y + cut)
    p.close()
    c.drawPath(p, fill=0, stroke=1)
    hx, hy = x + 0.32 * IN, y + th / 2
    c.circle(hx, hy, 6, fill=0, stroke=1)
    c.setLineWidth(0.5)
    c.circle(hx, hy, 9.5, fill=0, stroke=1)
    c.setStrokeColor(SOFT)                           # the string
    c.setLineWidth(0.8)
    q = c.beginPath()
    q.moveTo(hx, hy + 6)
    q.curveTo(hx - 0.5 * IN, hy + 0.9 * IN, M + 0.2 * IN, H * 0.55, M + 0.05 * IN, H * 0.86)
    c.drawPath(q, fill=0, stroke=1)
    tx = x + 0.75 * IN
    caps(c, "HANDMADE WITH CARE", tx + 1.55 * IN, y + th - 0.42 * IN, 7.4, HONEY, 2.2)
    P.logo(c, tx + 0.2 * IN, y + th / 2 + 5, 0.4 * IN, mono=INK)
    c.setFont("Cinzel", 18)
    c.setFillColor(INK)
    c.drawString(tx + 0.5 * IN, y + th / 2 - 1, "Little Hive House")
    c.setStrokeColor(INK)
    c.setLineWidth(0.6)
    c.line(tx + 0.35 * IN, y + 0.62 * IN, tx + 2.75 * IN, y + 0.62 * IN)
    c.setFont("Caps", 7)
    c.drawString(tx + 0.35 * IN, y + 0.38 * IN, "ORDER NO.")
    c.setFont("Garamond", 15)
    c.drawString(tx + 1.05 * IN, y + 0.36 * IN, name or "LHH-1002")


def corner(c, x, y, sx, sy, s):
    c.setStrokeColor(INK)
    c.setLineWidth(1.0)
    c.line(x, y, x + sx * s, y)
    c.line(x, y, x, y + sy * s)
    c.setLineWidth(0.5)
    c.line(x + sx * 5, y + sy * 5, x + sx * s * 0.62, y + sy * 5)
    c.line(x + sx * 5, y + sy * 5, x + sx * 5, y + sy * s * 0.62)
    hexagon(c, x + sx * 11, y + sy * 11, 3.2, INK, 0.6, fill=HONEY)


def d_corners(c, name=None):
    """11 · Corners: art-deco corners and "With love" in script, very quiet."""
    s = 0.62 * IN
    for (x, y, sx, sy) in ((M, M, 1, 1), (W - M, M, -1, 1), (M, H - M, 1, -1), (W - M, H - M, -1, -1)):
        corner(c, x, y, sx, sy, s)
    P.logo(c, W / 2, H * 0.72, 0.5 * IN, mono=INK)
    centred(c, "With love", W / 2, H * 0.5, "Script", 46)
    caps(c, "LITTLE HIVE HOUSE", W / 2, H * 0.36, 9, INK, 3.4, font="Cinzel")
    centred(c, "a little box of happy is inside", W / 2, H * 0.28, "Garamond", 13, SOFT)


# the ones the owners chose (Nov 2026); the other functions above are the ideas they passed on
DESIGNS = [("label", d_label), ("wreath", d_wreath), ("words", d_words), ("corners", d_corners)]


def register():
    if "Cinzel" not in pdfmetrics.getRegisteredFontNames():
        from reportlab.pdfbase.ttfonts import TTFont
        pdfmetrics.registerFont(TTFont("Cinzel", str(P.FONTS / "Cinzel-SemiBold.ttf")))


def build(key, fn, name=None, path=None):
    register()
    P.OUT.mkdir(exist_ok=True)
    path = path or P.OUT / f"envelope-{key}.pdf"
    c = canvas.Canvas(str(path), pagesize=(W, H))
    c.setTitle(f"Envelope · {key} · Little Hive House")
    c.setAuthor("Little Hive House")
    fn(c, name)
    c.showPage()
    c.save()
    return path


if __name__ == "__main__":
    for key, fn in DESIGNS:
        print(build(key, fn))
