"""Frame styles for custom photo magnets. Writes assets/frames/<id>.svg (600x600 overlay: the frame with a
transparent window where the photo shows) and assets/frames/frames.json (used by the builder and the print tool).

Canvas: 600 units = the full printed square (2.5 in). The magnet face is the middle 480 (60..540); everything
outside wraps around the rounded edge. Mats and patterns bleed to 600, but every border line, ornament that
matters and caption stays inside 60..540.

Each frame has
  window   [x, y, w, h]  where the photo is placed (centre-cropped to this box); the overlay hides everything
                         outside the window's real shape (rect, rounded, hexagon, circle)
  caption  optional dict: where the customer's caption goes (x, y baseline, max width w, font, size, colour...)
  group    Classic / Modern / Elegant / Seasonal & Holidays / Kids & Fun

Run: python3 tools/frames.py   (then python3 tools/build.py)."""
import json
import math
import re
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).parent / "designs"))
from common import SERIF_IT, DMS, CINZEL, JOS, BEBAS, JOST, MONO, esc, fit_size, bee  # noqa: E402
from gouache import blob, wash, strokes, ink, smooth_closed, smooth_open, maple_leaf, oak, acorn  # noqa: E402
import frame_art as A  # noqa: E402
from frame_art import f1, lgrad, rgrad, GOLD, GOLD_SOFT  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets" / "frames"
GROUPS = ["Classic", "Modern", "Elegant", "Seasonal & Holidays", "Kids & Fun"]

# caption fonts: key -> (svg attrs for fit_size, css family, css style, css weight)
FONTS = {
    "serif": (SERIF_IT, "'Playfair Display', Georgia, serif", "italic", 700),
    "dms": (DMS, "'DM Serif Display', Georgia, serif", "normal", 400),
    "cinzel": (CINZEL, "Cinzel, 'Times New Roman', serif", "normal", 600),
    "jos": (JOS, "'Josefin Sans', sans-serif", "normal", 700),
    "bebas": (BEBAS, "'Bebas Neue', Impact, sans-serif", "normal", 400),
    "jost": (JOST, "Jost, sans-serif", "normal", 500),
    "mono": (MONO, "'DM Mono', ui-monospace, monospace", "normal", 500),
}


def rr(x, y, w, h, r):
    if r <= 0:
        return f"M {f1(x)} {f1(y)} H {f1(x + w)} V {f1(y + h)} H {f1(x)} Z"
    return (f"M {f1(x + r)} {f1(y)} H {f1(x + w - r)} A {r} {r} 0 0 1 {f1(x + w)} {f1(y + r)} V {f1(y + h - r)} A {r} {r} 0 0 1 {f1(x + w - r)} {f1(y + h)} "
            f"H {f1(x + r)} A {r} {r} 0 0 1 {f1(x)} {f1(y + h - r)} V {f1(y + r)} A {r} {r} 0 0 1 {f1(x + r)} {f1(y)} Z")


def hex_pts(cx, cy, R, flat=True):
    off = 0 if flat else -90
    return [(cx + R * math.cos(math.radians(off + 60 * i)), cy + R * math.sin(math.radians(off + 60 * i))) for i in range(6)]


def poly_d(pts):
    return "M " + " L ".join(f"{f1(x)} {f1(y)}" for x, y in pts) + " Z"


def win_d(shape, x, y, w, h, r=0, grow=0):
    """Path of the window shape, optionally grown outward by `grow` units."""
    if shape == "circle":
        cx, cy, R = x + w / 2, y + h / 2, w / 2 + grow
        return f"M {f1(cx - R)} {f1(cy)} A {f1(R)} {f1(R)} 0 1 0 {f1(cx + R)} {f1(cy)} A {f1(R)} {f1(R)} 0 1 0 {f1(cx - R)} {f1(cy)} Z"
    if shape == "hex":
        cx, cy = x + w / 2, y + h / 2
        return poly_d(hex_pts(cx, cy, w / 2 + grow / math.cos(math.radians(30))))
    return rr(x - grow, y - grow, w + 2 * grow, h + 2 * grow, max(0, r + grow) if r else 0)


class Frame:
    def __init__(self, fid, name, group, win, shape="rect", r=0, caption=None, blurb=""):
        self.id, self.name, self.group, self.win, self.shape, self.r = fid, name, group, win, shape, r
        self.caption, self.blurb = caption, blurb
        self.u = A.U(fid)
        self.parts = []

    def wd(self, grow=0):
        return win_d(self.shape, *self.win, r=self.r, grow=grow)

    def mat(self, *content):
        """Content clipped to everything outside the window (the mat)."""
        cid = self.u("mat")
        self.parts.append(f'<clipPath id="{cid}"><path d="M -10 -10 H 610 V 610 H -10 Z {self.wd()}" clip-rule="evenodd"/></clipPath>'
                          f'<g clip-path="url(#{cid})">{"".join(content)}</g>')

    def inwin(self, *content):
        """Content clipped to the window (drawn over the photo: shadows, glare)."""
        cid = self.u("win")
        self.parts.append(f'<clipPath id="{cid}"><path d="{self.wd()}"/></clipPath><g clip-path="url(#{cid})">{"".join(content)}</g>')

    def add(self, *content):
        self.parts.append("".join(content))

    def shadow(self, k=1.0, color="#1A1008"):
        """Soft inner shadow so the photo looks set into the mat."""
        d = self.wd()
        rings = "".join(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" opacity="{o * k:.3f}"/>'
                        for w, o in ((22, 0.03), (14, 0.04), (8, 0.06), (4, 0.08), (1.6, 0.16)))
        self.inwin(rings)

    def bevel(self, b=6, light="#FFFFFF", mid="#F1ECE2", dark="#DCD4C6", line=None):
        """Mat bevel: the cut core seen around the window, lit from the top left."""
        x, y, w, h = self.win
        X0, Y0, X1, Y1 = x - b, y - b, x + w + b, y + h + b
        sides = [((X0, Y0), (X1, Y0), (x + w, y), (x, y), light), ((X0, Y0), (x, y), (x, y + h), (X0, Y1), mid),
                 ((X1, Y0), (X1, Y1), (x + w, y + h), (x + w, y), dark), ((X0, Y1), (x, y + h), (x + w, y + h), (X1, Y1), dark)]
        out = "".join(f'<path d="{poly_d(pts[:4])}" fill="{pts[4]}"/>' for pts in sides)
        if line:
            out += f'<path d="{rr(X0, Y0, X1 - X0, Y1 - Y0, 0)}" fill="none" stroke="{line}" stroke-width="1"/>'
        self.add(out)

    def svg(self):
        return "".join(self.parts)

    def meta(self):
        m = {"id": self.id, "name": self.name, "group": self.group, "window": [round(v, 1) for v in self.win], "shape": self.shape,
             "radius": self.r, "blurb": self.blurb, "caption": None}
        if self.caption:
            c = dict(self.caption)
            attrs, fam, style, weight = FONTS[c["font"]]
            c.update({"family": fam, "style": style, "weight": weight})
            if c.get("kicker"):
                k = dict(c["kicker"])
                _, kf, ks, kw = FONTS[k["font"]]
                k.update({"family": kf, "style": ks, "weight": kw})
                c["kicker"] = k
            m["caption"] = c
        return m


def cap(y, w=380, size=44, font="serif", color="#3A2418", x=300, mn=20, upper=False, ls=0, rot=0, mx=24, ph="", label="Caption", kicker=None):
    return {"x": x, "y": y, "w": w, "size": size, "min": mn, "font": font, "color": color, "upper": upper, "ls": ls, "rot": rot,
            "max": mx, "placeholder": ph, "label": label, "kicker": kicker}


def caption_svg(f, text):
    """Caption text exactly as the builder draws it (fitted with real font metrics)."""
    c = f.get("caption")
    if not c or not text:
        return ""
    s = text.upper() if c["upper"] else text
    attrs = FONTS[c["font"]][0]
    size = max(c["min"], fit_size(s, attrs, c["size"], c["w"], c["ls"]))
    x = c["x"] + (c["ls"] / 2 if c["ls"] else 0)
    tr = f' transform="rotate({c["rot"]} {c["x"]} {c["y"]})"' if c["rot"] else ""
    ls = f' letter-spacing="{c["ls"]}"' if c["ls"] else ""
    out = f'<text x="{x:g}" y="{c["y"]}" text-anchor="middle" {attrs} font-size="{size}"{ls} fill="{c["color"]}"{tr}>{esc(s)}</text>'
    k = c.get("kicker")
    if k:
        kattrs = FONTS[k["font"]][0]
        kls = f' letter-spacing="{k["ls"]}"' if k.get("ls") else ""
        out = (f'<text x="{c["x"] + k.get("ls", 0) / 2:g}" y="{k["y"]}" text-anchor="middle" {kattrs} font-size="{k["size"]}"{kls} fill="{k["color"]}">{esc(k["text"])}</text>' + out)
    return out


# ================================================================ CLASSIC
def f_none():
    return Frame("none", "No border", "Classic", (0, 0, 600, 600), blurb="Your photo fills the whole magnet")


def f_white():
    f = Frame("white", "Crisp white mat", "Classic", (100, 100, 400, 400), blurb="Gallery-white mat with a hand-cut bevel")
    u = f.u
    g = u("wg")
    f.mat(f'<defs>{rgrad(g, [(0, "#FFFFFF"), (0.75, "#FBFAF7"), (1, "#F1EEE8")], 0.5, 0.45, 0.75)}</defs><rect width="600" height="600" fill="url(#{g})"/>',
          A.paper_tex(u("pt"), "#B8AE9C", 2, 0.5))
    # blind-embossed double rule (white highlight + soft shadow, no ink)
    for ins, wv in ((72, 1.6), (79, 1.0)):
        f.mat(f'<path d="{rr(ins + 1, ins + 1, 600 - 2 * ins, 600 - 2 * ins, 2)}" fill="none" stroke="#D9D2C4" stroke-width="{wv}" opacity="0.75"/>'
              f'<path d="{rr(ins, ins, 600 - 2 * ins, 600 - 2 * ins, 2)}" fill="none" stroke="#FFFFFF" stroke-width="{wv}"/>')
    f.shadow(1.2)
    f.bevel(7, "#FFFFFF", "#F6F2EA", "#E4DDCF")
    return f


def f_instant():
    f = Frame("instant", "Instant photo", "Classic", (94, 90, 412, 344),
              caption=cap(494, 380, 46, "serif", "#2D3A6B", mn=24, rot=-2, mx=22, ph="Summer 2026", label="Handwritten caption"),
              blurb="The classic instant print, with a handwritten caption")
    u = f.u
    g = u("ig")
    f.mat(f'<defs>{lgrad(g, [(0, "#FDFCF8"), (1, "#F3F0E8")])}</defs><rect width="600" height="600" fill="url(#{g})"/>',
          A.paper_tex(u("pt"), "#A89C88", 7, 0.7),
          # faint gloss streak + the slight thickness of the print at the bottom
          '<path d="M 0 0 L 600 0 L 600 30 Q 300 46 0 18 Z" fill="#FFFFFF" opacity="0.5"/>')
    x, y, w, h = f.win
    f.shadow(1.0, "#000000")
    f.add(f'<path d="{rr(x, y, w, h, 0)}" fill="none" stroke="#2A2620" stroke-width="2.2" opacity="0.55"/>')
    # washi tape holding it to the fridge
    tu = u("tape")
    tape = f"M 238 66 L 360 60 L 366 108 L 244 116 Z"
    f.add(f'<g transform="rotate(-3 300 88)"><clipPath id="{tu}"><path d="{tape}"/></clipPath>'
          f'<path d="{tape}" fill="#F3C6C2" opacity="0.88"/>'
          f'<g clip-path="url(#{tu})">' + "".join(f'<path d="M {200 + k * 16} 50 l -30 80" stroke="#FFFFFF" stroke-width="5" opacity="0.45"/>' for k in range(14)) + "</g>"
          '<path d="M 238 66 l 3 6 -3 6 3 6 -3 6 3 6 -3 6 3 6 -1 4 M 360 60 l 3 6 -3 6 3 6 -3 6 3 6 -3 6 3 6 1 4" stroke="#FBF8F2" stroke-width="2" fill="none" opacity="0.6"/>'
          "</g>")
    return f


def f_gallery():
    f = Frame("gallery", "Black gallery mat", "Classic", (106, 106, 388, 388), blurb="Deep black mat with a bright white bevel")
    u = f.u
    g = u("bg")
    f.mat(f'<defs>{rgrad(g, [(0, "#2A2724"), (0.7, "#1C1A18"), (1, "#121110")], 0.45, 0.4, 0.8)}</defs><rect width="600" height="600" fill="url(#{g})"/>',
          A.grain_tex(u("gr"), "#FFFFFF", 4, 0.5))
    f.shadow(1.4, "#000000")
    f.bevel(9, "#FFFFFF", "#F2EFEA", "#C9C4BC")
    x, y, w, h = f.win
    f.add(f'<path d="{rr(x - 9, y - 9, w + 18, h + 18, 0)}" fill="none" stroke="#000000" stroke-width="1.2" opacity="0.5"/>')
    # a whisper of gold fillet inside the bevel
    f.add(f'<path d="{rr(x + 0.8, y + 0.8, w - 1.6, h - 1.6, 0)}" fill="none" stroke="#C9A24A" stroke-width="1.6"/>')
    return f


# ================================================================ MODERN
def f_rounded():
    f = Frame("rounded", "Rounded modern", "Modern", (104, 104, 392, 392), r=64, blurb="Soft sage with a cut-out arch and sunny shapes")
    u = f.u
    x, y, w, h = f.win
    f.mat('<rect width="600" height="600" fill="#C9D2BD"/>', A.mottle(3, ["#FFFFFF", "#7A8A6A"], 10, (0.03, 0.07)),
          # mid-century shapes peeking around the window
          '<circle cx="512" cy="96" r="70" fill="#E9B44C"/><circle cx="512" cy="96" r="70" fill="none" stroke="#F6D88E" stroke-width="2" stroke-dasharray="2 7" opacity="0.8"/>',
          '<circle cx="112" cy="488" r="84" fill="#D9805E"/><circle cx="112" cy="488" r="62" fill="none" stroke="#F2B49A" stroke-width="2"/>',
          '<path d="M 150 530 Q 190 506 230 530 T 310 530" stroke="#FBF5EA" stroke-width="5" fill="none" stroke-linecap="round" opacity="0.9"/>',
          A.paper_tex(u("pt"), "#4A5A3A", 11, 0.8))
    f.shadow(0.9)
    f.add(f'<path d="{win_d("rect", x, y, w, h, 64, grow=12)}" fill="none" stroke="#FBF5EA" stroke-width="3"/>')
    return f


def f_film():
    f = Frame("film", "Film strip", "Modern", (82, 128, 436, 344), blurb="A frame cut from a roll of 35mm film")
    u = f.u
    x, y, w, h = f.win
    holes = []
    for row_y in (82, 500):
        for k in range(14):
            hx = 36 + k * 38
            holes.append(f'<rect x="{hx}" y="{row_y}" width="22" height="18" rx="4" fill="#F1E9DA"/>'
                         f'<rect x="{hx}" y="{row_y}" width="22" height="3" rx="1.5" fill="#000" opacity="0.25"/>')
    edge = '<g font-family="\'DM Mono\', monospace" font-weight="500" font-size="17" fill="#E59A3A" letter-spacing="1">'
    edge += '<text x="96" y="120">24</text><text x="160" y="120">▸ 24A</text><text x="400" y="120">HIVE 200</text>'
    edge += '<text x="96" y="492">25</text><text x="160" y="492">▸ 25A</text><text x="416" y="492">◂ 2026</text></g>'
    f.mat('<rect width="600" height="600" fill="#161412"/>', A.grain_tex(u("gr"), "#FFFFFF", 8, 0.6),
          '<rect x="0" y="0" width="600" height="600" fill="#3A2A1A" opacity="0.18"/>', "".join(holes), edge)
    f.shadow(1.3, "#000000")
    f.add(f'<path d="{rr(x, y, w, h, 3)}" fill="none" stroke="#000" stroke-width="2"/>')
    return f


def perforated(x0, y0, x1, y1, r=7.5, step=22):
    """Stamp outline with semicircular perforation bites along each edge."""
    d = [f"M {f1(x0)} {f1(y0)}"]

    def edge(ax, ay, bx, by):
        L = math.hypot(bx - ax, by - ay)
        n = max(1, int(round(L / step)))
        ux, uy = (bx - ax) / L, (by - ay) / L
        seg = L / n
        for i in range(n):
            c = (i + 0.5) * seg
            p0 = (ax + ux * (c - r), ay + uy * (c - r))
            p1 = (ax + ux * (c + r), ay + uy * (c + r))
            d.append(f"L {f1(p0[0])} {f1(p0[1])} A {r} {r} 0 0 0 {f1(p1[0])} {f1(p1[1])}")
        d.append(f"L {f1(bx)} {f1(by)}")
    edge(x0, y0, x1, y0)
    edge(x1, y0, x1, y1)
    edge(x1, y1, x0, y1)
    edge(x0, y1, x0, y0)
    return " ".join(d) + " Z"


def f_stamp():
    f = Frame("stamp", "Postage stamp", "Modern", (102, 102, 396, 340),
              caption=cap(494, 330, 30, "jos", "#FBF5EA", mn=18, upper=True, ls=4, mx=20, ph="With love", label="Stamp text"),
              blurb="Perforated stamp with a postmark, on kraft paper")
    u = f.u
    x, y, w, h = f.win
    stamp = perforated(70, 70, 530, 530)
    rnd = random.Random(5)
    f.mat('<rect width="600" height="600" fill="#D9C2A0"/>', A.mottle(5, ["#FFFFFF", "#8A6A40"], 14, (0.04, 0.09)),
          A.paper_tex(u("kp"), "#6A4A2A", 3, 1.6),
          f'<path d="{stamp}" fill="#3A2414" opacity="0.18" transform="translate(4 6)"/>',
          f'<path d="{stamp}" fill="#FBF8F1"/>', A.paper_tex(u("sp"), "#A89C88", 9, 0.6).replace('<rect width="600" height="600"', f'<path d="{stamp}"').replace('"/>', '"/>', 1),
          f'<path d="{rr(88, 88, 424, 424, 0)}" fill="#B5402F"/>',
          f'<path d="{rr(94, 94, 412, 412, 0)}" fill="none" stroke="#F5DCC8" stroke-width="1.4"/>',
          f'<path d="{rr(88, 456, 424, 56, 0)}" fill="#9E3426"/>',
          "".join(f'<path d="M {px} 484 l 4 -8 4 8 -4 8 Z" fill="#F5DCC8"/>' for px in (108, 484)))
    f.shadow(1.0)
    f.add(f'<path d="{rr(x, y, w, h, 0)}" fill="none" stroke="#6A1E14" stroke-width="1.5"/>')
    # postmark: double ring with arc lettering + wavy cancellation lines
    pid = u("pm")
    pm = (f'<g opacity="0.72" fill="none" stroke="#2A2A3A">'
          f'<circle cx="452" cy="146" r="62" stroke-width="3"/><circle cx="452" cy="146" r="48" stroke-width="1.6"/>'
          + "".join(f'<path d="M {300 + k * 0} {120 + k * 14} q 18 -10 36 0 t 36 0 t 36 0 t 36 0" stroke-width="3" transform="translate(-20 0)"/>' for k in range(0))
          + "</g>")
    waves = "".join(f'<path d="M 268 {112 + k * 15} q 15 -9 30 0 t 30 0 t 30 0 t 30 0" stroke="#2A2A3A" stroke-width="3" fill="none" opacity="0.6"/>' for k in range(5))
    arcs = (f'<defs><path id="{pid}t" d="M 397 146 A 55 55 0 0 1 507 146"/><path id="{pid}b" d="M 401 146 A 51 51 0 0 0 503 146"/></defs>'
            f'<g font-family="\'Josefin Sans\', sans-serif" font-weight="700" fill="#2A2A3A" opacity="0.75">'
            f'<text font-size="16" letter-spacing="3" text-anchor="middle"><textPath href="#{pid}t" startOffset="50%">FIRST CLASS</textPath></text>'
            f'<text font-size="16" letter-spacing="3" text-anchor="middle" dy="13"><textPath href="#{pid}b" startOffset="50%">HOME MAIL</textPath></text>'
            f'<text x="452" y="153" font-size="20" text-anchor="middle" letter-spacing="1">★ ✦ ★</text></g>')
    f.add(waves, pm, arcs)
    return f


def f_postcard():
    f = Frame("postcard", "Travel postcard", "Modern", (98, 98, 404, 318),
              caption=cap(498, 330, 46, "dms", "#1F4E8C", mn=24, mx=20, ph="Lisbon", label="Place name",
                          kicker={"text": "GREETINGS FROM", "y": 452, "size": 17, "font": "jos", "color": "#B8432F", "ls": 5}),
              blurb="Airmail stripes, a little stamp and a postmark")
    u = f.u
    x, y, w, h = f.win
    # airmail stripes: diagonal red / cream / blue band around the edge
    sid = u("am")
    stripes = "".join(f'<path d="M {k * 34 - 600} 0 l 600 600 l 17 0 l -600 -600 Z" fill="{"#C8412E" if k % 2 else "#2F5C9E"}"/>' for k in range(0, 72))
    stripes = "".join(f'<path d="M {k * 48 - 600} 0 L {k * 48} 600 L {k * 48 + 20} 600 L {k * 48 - 580} 0 Z" fill="{("#C8412E", "#2F5C9E")[k % 2]}"/>' for k in range(0, 26))
    card = rr(86, 86, 428, 428, 6)
    f.mat('<rect width="600" height="600" fill="#FBF6EA"/>', stripes,
          f'<path d="{card}" fill="#3A2414" opacity="0.15" transform="translate(0 3)"/>',
          f'<path d="{card}" fill="#FBF5E6"/>', A.paper_tex(u("pp"), "#A89070", 4, 0.8),
          f'<path d="{rr(92, 92, 416, 416, 3)}" fill="none" stroke="#D8C8A8" stroke-width="1.2"/>')
    f.shadow(0.9)
    f.add(f'<path d="{rr(x, y, w, h, 0)}" fill="none" stroke="#FFFFFF" stroke-width="4"/>')
    # little stamp at the top-right corner, overlapping the photo
    st = perforated(424, 70, 512, 168, r=4, step=11)
    g = u("sk")
    f.add(f'<g transform="rotate(6 468 119)"><path d="{st}" fill="#3A2414" opacity="0.2" transform="translate(3 4)"/><path d="{st}" fill="#FBF8F1"/>'
          f'<defs>{lgrad(g, [(0, "#8CC4E0"), (0.6, "#F6D9A0"), (1, "#F2B26A")])}</defs>'
          f'<rect x="433" y="79" width="70" height="80" fill="url(#{g})"/>'
          '<circle cx="482" cy="104" r="11" fill="#FFF2C0"/>'
          '<path d="M 433 159 L 433 136 Q 450 124 466 134 T 503 128 L 503 159 Z" fill="#3E8A6A"/>'
          '<path d="M 433 159 L 433 146 Q 456 138 476 148 T 503 146 L 503 159 Z" fill="#2A6650"/>'
          '<path d="M 446 120 l 6 -3 6 3 M 456 112 l 5 -2 5 2" stroke="#3A3A4A" stroke-width="1.6" fill="none"/>'
          '<text x="440" y="96" font-family="\'Josefin Sans\', sans-serif" font-weight="700" font-size="16" fill="#B8432F">5¢</text></g>'
          '<g fill="none" stroke="#2A2A3A" opacity="0.6"><circle cx="420" cy="160" r="34" stroke-width="2.6"/>'
          + "".join(f'<path d="M 360 {146 + k * 12} q 12 -7 24 0 t 24 0" stroke-width="2.4"/>' for k in range(3)) + "</g>")
    return f


def f_honey():
    R = 210
    cx, cy = 300, 296
    f = Frame("honeycomb", "Honeycomb", "Modern", (cx - R, cy - R * math.sqrt(3) / 2, 2 * R, R * math.sqrt(3)), shape="hex",
              blurb="Our Little Hive House signature: painted honeycomb and a busy bee")
    u = f.u
    rnd = random.Random(11)
    cells = []
    s = 30  # cell circumradius, flat-top tiling
    gid, cap_g, hi = u("hc"), u("hk"), u("hh")
    defs = (f'<defs>{rgrad(gid, [(0, "#FCD777"), (0.55, "#F0A72A"), (1, "#B86A12")], 0.4, 0.35, 0.75)}'
            f'{rgrad(cap_g, [(0, "#FFF4CF"), (0.7, "#F8DE95"), (1, "#E2B252")], 0.4, 0.35, 0.8)}</defs>')
    for col in range(-1, 14):
        for row in range(-1, 14):
            hx = col * s * 1.5
            hy = row * s * math.sqrt(3) + (s * math.sqrt(3) / 2 if col % 2 else 0)
            pts = A.jitter(hex_pts(hx, hy, s - 3.2), col * 31 + row, 0.8)
            kind = rnd.random()
            fill = f"url(#{cap_g})" if kind < 0.3 else f"url(#{gid})"
            cells.append(f'<path d="{poly_d(pts)}" fill="{fill}"/>')
            if kind >= 0.3:
                cells.append(f'<path d="M {f1(hx - s * 0.45)} {f1(hy - s * 0.2)} Q {f1(hx - s * 0.3)} {f1(hy - s * 0.5)} {f1(hx + s * 0.05)} {f1(hy - s * 0.52)}" stroke="#FFF6DA" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.7"/>')
            else:
                cells.append(f'<ellipse cx="{f1(hx - s * 0.18)}" cy="{f1(hy - s * 0.2)}" rx="{f1(s * 0.22)}" ry="{f1(s * 0.12)}" fill="#FFFFFF" opacity="0.55"/>')
    f.mat('<rect width="600" height="600" fill="#E8B84E"/>', defs, "".join(cells),
          strokes(u("hs"), "M 0 0 H 600 V 600 H 0 Z", (0, 0, 600, 600), ["#FFF2C0", "#C98A1A", "#F6D27A"], 3, n=260, angle=-60, length=(20, 50), width=(1.5, 4), opacity=(0.06, 0.16)),
          A.grain_tex(u("g"), "#6A3A0A", 2, 0.8))
    f.shadow(1.1, "#5A2A00")
    # wax rim around the window
    f.add(f'<path d="{f.wd(grow=6)}" fill="none" stroke="#FBE7AE" stroke-width="10" stroke-linejoin="round"/>'
          f'<path d="{f.wd(grow=11)}" fill="none" stroke="#A8620E" stroke-width="2.4" stroke-linejoin="round"/>'
          f'<path d="{f.wd(grow=1)}" fill="none" stroke="#C98A1A" stroke-width="1.6" stroke-linejoin="round"/>')
    # a honey drip running over the top edge of the photo
    top_y = cy - R * math.sqrt(3) / 2
    dg = u("dr")
    drip = (f"M 170 {f1(top_y - 4)} L 236 {f1(top_y - 4)} C 232 {f1(top_y + 14)} 228 {f1(top_y + 22)} 226 {f1(top_y + 46)} "
            f"C 225 {f1(top_y + 62)} 210 {f1(top_y + 62)} 210 {f1(top_y + 46)} C 210 {f1(top_y + 30)} 204 {f1(top_y + 22)} 196 {f1(top_y + 22)} "
            f"C 190 {f1(top_y + 22)} 188 {f1(top_y + 34)} 186 {f1(top_y + 30)} C 184 {f1(top_y + 22)} 176 {f1(top_y + 12)} 170 {f1(top_y - 4)} Z")
    f.add(f'<defs>{lgrad(dg, [(0, "#E8961E"), (0.6, "#F2B23A"), (1, "#C26E0E")], 0, 0, 1, 0.3)}</defs>'
          f'<path d="{drip}" fill="#5A2A00" opacity="0.18" transform="translate(2 4)"/><path d="{drip}" fill="url(#{dg})" opacity="0.96"/>'
          f'<path d="M 214 {f1(top_y + 30)} Q 214 {f1(top_y + 46)} 218 {f1(top_y + 52)}" stroke="#FFF2C8" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.85"/>'
          f'<circle cx="190" cy="{f1(top_y + 6)}" r="3" fill="#FFF6DA" opacity="0.8"/>')
    # the house bee with a dotted flight loop, bottom-right corner
    f.add('<path d="M 352 512 C 400 534 450 512 434 486 C 420 464 392 490 420 504 C 446 516 466 496 474 478" stroke="#5A3A12" stroke-width="2.6" stroke-dasharray="1 8" stroke-linecap="round" fill="none" opacity="0.85"/>',
          f'<circle cx="494" cy="466" r="44" fill="#FFF6DA" opacity="0.35"/>',
          bee(496, 464, 0.46, u("bee"), flip=True, wing="#FFFFFF"))
    return f


# ================================================================ ELEGANT
def flourish_corner(gid, scale=1.0):
    """Gold filigree for the top-left corner (in a 0..170 box, origin at the corner)."""
    s = scale
    paths = [
        # scroll along the top rule
        "M 30 30 C 60 26 92 26 120 34 C 140 40 150 54 142 64 C 134 74 118 70 118 58 C 118 50 126 46 132 50",
        # scroll along the left rule
        "M 30 30 C 26 60 26 92 34 120 C 40 140 54 150 64 142 C 74 134 70 118 58 118 C 50 118 46 126 50 132",
        # inner curl
        "M 30 30 C 52 52 66 58 82 56 C 96 54 100 42 92 38 C 84 34 78 42 84 46",
        "M 30 30 C 52 52 58 66 56 82 C 54 96 42 100 38 92 C 34 84 42 78 46 84",
    ]
    out = "".join(f'<path d="{d}" fill="none" stroke="url(#{gid})" stroke-width="{3.2 * s:.1f}" stroke-linecap="round"/>' for d in paths)
    out += "".join(f'<path d="{d}" fill="none" stroke="#FFF2C4" stroke-width="{1.0 * s:.1f}" stroke-linecap="round" opacity="0.55" transform="translate(-0.8 -0.8)"/>' for d in paths[:2])
    # leaf tips and a diamond at the corner
    out += f'<path d="M 30 18 L 42 30 L 30 42 L 18 30 Z" fill="url(#{gid})" stroke="#8A6420" stroke-width="1"/>'
    for (x, y, a) in ((104, 30, 0), (30, 104, 90), (70, 70, 45)):
        out += f'<path d="M {x} {y} q 8 -7 16 0 q -8 7 -16 0 Z" fill="url(#{gid})" transform="rotate({a} {x} {y})"/>'
    out += f'<circle cx="64" cy="64" r="4" fill="url(#{gid})"/>'
    return out


def f_goldline():
    f = Frame("gold-cream", "Gold line on cream", "Elegant", (110, 110, 380, 380), blurb="Fine double gold rule with filigree corners")
    u = f.u
    gid = u("gd")
    f.mat(f'<rect width="600" height="600" fill="#F7F0E1"/>', A.mottle(6, ["#FFFFFF", "#C9A86A"], 12, (0.03, 0.07)), A.paper_tex(u("pp"), "#9C8460", 6, 0.9))
    defs = f'<defs>{lgrad(gid, GOLD, 0, 0, 600, 600, user=True)}</defs>'
    rules = (f'<path d="{rr(74, 74, 452, 452, 0)}" fill="none" stroke="url(#{gid})" stroke-width="3.4"/>'
             f'<path d="{rr(83, 83, 434, 434, 0)}" fill="none" stroke="url(#{gid})" stroke-width="1.4"/>')
    corners = "".join(f'<g transform="{t}">{flourish_corner(gid)}</g>' for t in
                      ("translate(44 44)", "translate(556 44) scale(-1 1)", "translate(44 556) scale(1 -1)", "translate(556 556) scale(-1 -1)"))
    # cover the rules under the corner ornaments with cream so the filigree reads cleanly
    pads = "".join(f'<rect x="{x}" y="{y}" width="34" height="34" fill="#F7F0E1"/>' for x, y in ((57, 57), (509, 57), (57, 509), (509, 509)))
    # small centre ornaments on each side
    mids = "".join(f'<g transform="rotate({a} 300 300)"><path d="M 284 78 Q 300 64 316 78 Q 300 92 284 78 Z" fill="url(#{gid})" stroke="#8A6420" stroke-width="0.8"/>'
                   f'<circle cx="300" cy="78" r="3" fill="#FFF2C4"/></g>' for a in (0, 90, 180, 270))
    f.shadow(0.8)
    f.add(defs, rules, pads, corners, mids,
          f'<path d="{rr(110 - 6, 110 - 6, 392, 392, 0)}" fill="none" stroke="url(#{gid})" stroke-width="2.4"/>')
    return f


def f_lace():
    f = Frame("lace", "Scalloped lace", "Elegant", (122, 122, 356, 356), r=4, blurb="Heirloom white lace on dusty rose")
    u = f.u
    x, y, w, h = f.win
    bg = "#D9A3A8"
    # outer scalloped edge of the lace band
    X0, X1 = 72, 528
    n = 12
    step = (X1 - X0) / n
    r = step / 2
    d = [f"M {X0} {X0}"]
    for side in range(4):
        for i in range(n):
            if side == 0:
                p = (X0 + (i + 1) * step, X0)
            elif side == 1:
                p = (X1, X0 + (i + 1) * step)
            elif side == 2:
                p = (X1 - (i + 1) * step, X1)
            else:
                p = (X0, X1 - (i + 1) * step)
            d.append(f"A {f1(r)} {f1(r)} 0 0 0 {f1(p[0])} {f1(p[1])}")
    band = " ".join(d) + " Z"
    holes = []
    # eyelet ring between scallops and the inner edge
    for side in range(4):
        for i in range(n):
            t = X0 + (i + 0.5) * step
            for (px, py) in {0: [(t, X0 + 6)], 1: [(X1 - 6, t)], 2: [(t, X1 - 6)], 3: [(X0 + 6, t)]}[side]:
                holes.append(f'<circle cx="{f1(px)}" cy="{f1(py)}" r="4.2" fill="{bg}"/>')
    # petal motifs midway in the band
    mot = []
    mid = (X0 + 26 + x - 8) / 2
    for i in range(9):
        t = X0 + 40 + i * (X1 - X0 - 80) / 8
        for (px, py) in ((t, mid), (t, 600 - mid), (mid, t), (600 - mid, t)):
            mot.append("".join(f'<ellipse cx="{f1(px + 6 * math.cos(math.radians(a)))}" cy="{f1(py + 6 * math.sin(math.radians(a)))}" rx="4.6" ry="2.2" '
                               f'transform="rotate({a} {f1(px + 6 * math.cos(math.radians(a)))} {f1(py + 6 * math.sin(math.radians(a)))})" fill="{bg}" opacity="0.85"/>' for a in (0, 90, 180, 270)))
            mot.append(f'<circle cx="{f1(px)}" cy="{f1(py)}" r="1.8" fill="{bg}"/>')
    # inner edge row of small holes
    inner = []
    for i in range(30):
        t = x - 10 + i * (w + 20) / 29
        for (px, py) in ((t, y - 10), (t, y + h + 10), (x - 10, t), (x + w + 10, t)):
            inner.append(f'<circle cx="{f1(px)}" cy="{f1(py)}" r="2" fill="{bg}"/>')
    picots = "".join(f'<circle cx="{f1(px)}" cy="{f1(py)}" r="2.4" fill="#FFFDF8"/>' for px, py in
                     [(X0 + i * step, X0 - r - 2) for i in range(n + 1)] + [(X0 + i * step, X1 + r + 2) for i in range(n + 1)] +
                     [(X0 - r - 2, X0 + i * step) for i in range(n + 1)] + [(X1 + r + 2, X0 + i * step) for i in range(n + 1)])
    lace = (f'<path d="{band}" fill="#5A2A30" opacity="0.18" transform="translate(2 4)"/>'
            f'<path d="{band}" fill="#FFFDF8"/>' + picots + "".join(holes) + "".join(mot) + "".join(inner) +
            "".join(f'<path d="{rr(X0 + k, X0 + k, X1 - X0 - 2 * k, X1 - X0 - 2 * k, 0)}" fill="none" stroke="{bg}" stroke-width="1" opacity="0.5" stroke-dasharray="2 4"/>' for k in (16,)))
    f.mat(f'<rect width="600" height="600" fill="{bg}"/>', A.linen_tex(u("ln"), "#8A4A50", 2, 0.12), lace,
          A.paper_tex(u("lp"), "#B89A9A", 8, 0.6))
    f.shadow(0.9, "#3A1418")
    f.add(f'<path d="{rr(x - 2, y - 2, w + 4, h + 4, 6)}" fill="none" stroke="#E9CFC9" stroke-width="2"/>')
    # satin bow at the top centre
    bw = u("bow")
    f.add(f'<defs>{lgrad(bw, [(0, "#F4D3D6"), (0.5, "#E3A6AE"), (1, "#C9808A")], 0, 0, 0, 1)}</defs>'
          '<path d="M 300 104 C 270 80 238 78 236 100 C 234 122 268 122 300 108 Z" fill="url(#' + bw + ')" stroke="#B0646E" stroke-width="1.4"/>'
          '<path d="M 300 104 C 330 80 362 78 364 100 C 366 122 332 122 300 108 Z" fill="url(#' + bw + ')" stroke="#B0646E" stroke-width="1.4"/>'
          '<path d="M 296 110 L 276 150 L 286 146 L 290 156 L 302 112 Z" fill="url(#' + bw + ')" stroke="#B0646E" stroke-width="1.2"/>'
          '<path d="M 304 110 L 324 150 L 314 146 L 310 156 L 298 112 Z" fill="url(#' + bw + ')" stroke="#B0646E" stroke-width="1.2"/>'
          '<ellipse cx="300" cy="106" rx="9" ry="8" fill="#E3A6AE" stroke="#B0646E" stroke-width="1.4"/>'
          '<path d="M 248 96 Q 262 90 280 100 M 352 96 Q 338 90 320 100" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.7" stroke-linecap="round"/>')
    return f


def f_floral():
    f = Frame("floral", "Watercolour peonies", "Elegant", (104, 104, 392, 392), blurb="Hand-painted peonies and garden roses")
    u = f.u
    x, y, w, h = f.win
    f.mat('<rect width="600" height="600" fill="#FBF6EF"/>', A.mottle(9, ["#F6D9DC", "#E8EEDF", "#FFFFFF"], 14, (0.04, 0.1)), A.paper_tex(u("pp"), "#A08A7A", 9, 1.0))
    f.shadow(0.8)
    f.add(ink(rr(x - 7, y - 7, w + 14, h + 14, 2), "#C98C92", 1.6, 4, 2, 0.8))
    lv = ("#8FAE8A", "#5E7E5E", "#C6DCC0")
    tl, br = [], []
    # top-left: big peony, rose, buds, leaves sweeping along both edges
    for (bx, by, L, W, ang, sd) in ((150, 120, 118, 38, -8, 1), (128, 140, 110, 36, 92, 2), (176, 108, 80, 26, -40, 3), (110, 176, 84, 26, 120, 4),
                                    (210, 98, 70, 22, 6, 5), (98, 214, 66, 22, 84, 6)):
        tl.append(A.painted_leaf(u, bx, by, L, W, ang, lv[0] if sd % 2 else "#A3BE96", lv[1], lv[2], sd, bend=0.4, inkc="#4E6A4E"))
    tl.append(A.filler_sprig(u, 160, 150, 120, -18, 7))
    tl.append(A.filler_sprig(u, 150, 160, 120, 108, 8))
    tl.append(A.rose2(u, 200, 170, 40, 21))
    tl.append(A.peony2(u, 126, 126, 70, 11))
    tl.append(A.bud(u, 262, 112, 15, 70, 31))
    tl.append(A.bud(u, 110, 262, 14, -20, 32, fill="#F2A7B5", dark="#C9667E"))
    for (bx, by, L, W, ang, sd) in ((452, 478, 104, 34, 172, 41), (486, 440, 92, 30, -112, 42), (420, 494, 70, 22, 160, 43), (494, 420, 66, 22, -110, 44)):
        br.append(A.painted_leaf(u, bx, by, L, W, ang, "#A3BE96" if sd % 2 else lv[0], lv[1], lv[2], sd, bend=-0.4, inkc="#4E6A4E"))
    br.append(A.filler_sprig(u, 460, 470, 100, 196, 47))
    br.append(A.peony2(u, 476, 476, 54, 51, pal=("#D27E6E", "#F2B0A0", "#FBDCD2", "#FFF6F2")))
    br.append(A.rose2(u, 418, 474, 28, 52))
    br.append(A.bud(u, 360, 492, 12, -110, 53))
    f.add("".join(tl), "".join(br))
    return f


def f_eucalyptus():
    f = Frame("eucalyptus", "Eucalyptus wreath", "Elegant", (108, 104, 384, 384), shape="circle", blurb="A painted silver-dollar eucalyptus wreath")
    u = f.u
    cx, cy, R = 300, 296, 192
    f.mat('<rect width="600" height="600" fill="#F4F1EA"/>', A.mottle(4, ["#FFFFFF", "#C8D6CC"], 14, (0.1, 0.22)), A.linen_tex(u("ln"), "#9AA096", 6, 0.1), A.paper_tex(u("pp"), "#8A9A8A", 4, 0.6))
    f.shadow(0.9)
    f.add(f'<circle cx="{cx}" cy="{cy}" r="{R + 7}" fill="none" stroke="#B9A47A" stroke-width="1.8"/>'
          f'<circle cx="{cx}" cy="{cy}" r="{R + 13}" fill="none" stroke="#B9A47A" stroke-width="0.9" stroke-dasharray="1 5" stroke-linecap="round"/>')
    rnd = random.Random(8)
    tones = ["#8FAE9C", "#9DB5A6", "#7E9E8C", "#A8BFB0", "#86A493"]

    def arc_pts(a0, a1, rad, n=8, wob=8):
        pts = []
        for i in range(n):
            t = i / (n - 1)
            a = math.radians(a0 + (a1 - a0) * t)
            rr_ = rad + math.sin(t * math.pi) * rnd.uniform(-wob, wob)
            pts.append((cx + rr_ * math.cos(a), cy + rr_ * math.sin(a)))
        return pts
    stems = []
    # lower-left crescent (heavy) and upper-right crescent (lighter), stems overlapping like a real garland
    for k, (a0, a1, rad, lr) in enumerate(((205, 120, R + 4, (11, 22)), (95, 175, R + 10, (10, 20)), (150, 232, R - 2, (10, 19)),
                                            (70, 128, R + 2, (9, 17)), (250, 200, R + 12, (8, 15)),
                                            (-70, 5, R + 6, (10, 20)), (25, -40, R + 2, (9, 18)), (-95, -45, R + 10, (8, 15)))):
        stems.append(A.euca_stem(u, arc_pts(a0, a1, rad), 20 + k, leaf_r=lr, every=0.085, fill=rnd.choice(tones)))
    # seeded eucalyptus sprigs poking out
    seeds = []
    for a in (110, 140, 185, 222, -20, -55):
        bx, by = cx + (R + 6) * math.cos(math.radians(a)), cy + (R + 6) * math.sin(math.radians(a))
        for j in range(5):
            aa = math.radians(a + rnd.uniform(-25, 25))
            d = rnd.uniform(14, 34)
            px, py = bx + d * math.cos(aa), by + d * math.sin(aa)
            seeds.append(f'<path d="M {f1(bx)} {f1(by)} L {f1(px)} {f1(py)}" stroke="#7A8A6A" stroke-width="1.1"/>'
                         f'<circle cx="{f1(px)}" cy="{f1(py)}" r="{rnd.uniform(2.6, 3.6):.1f}" fill="#6E8A74" stroke="#4E6A56" stroke-width="0.7"/>')
    # blush garden roses and white berries nestled bottom-left, a small rose top-right
    acc = []
    for a, rr_, r_, sd, fill, dark, light in ((136, R + 4, 34, 70, "#F2C4BC", "#C98A80", "#FFF0EA"), (162, R + 14, 22, 71, "#F6D8CC", "#D0988A", "#FFF4EE"),
                                              (114, R + 16, 18, 72, "#EBB0AC", "#B8746E", "#FFE4E0"), (-28, R + 8, 22, 73, "#F2C4BC", "#C98A80", "#FFF0EA")):
        acc.append(A.rose2(u, cx + rr_ * math.cos(math.radians(a)), cy + rr_ * math.sin(math.radians(a)), r_, sd, pal=(dark, fill, light, "#FFF8F4")))
    for a in (124, 150, 176, 100, -12, -40):
        bx, by = cx + (R + 26) * math.cos(math.radians(a)), cy + (R + 26) * math.sin(math.radians(a))
        acc.append(A.berry(u, bx, by, 4.6, "#FBF8F2", "#B8B0A0", "#FFFFFF"))
    f.add("".join(seeds), "".join(stems), "".join(acc))
    return f


def f_wedding():
    f = Frame("wedding", "Linen & gold leaf", "Elegant", (100, 96, 400, 326),
              caption=cap(494, 360, 42, "serif", "#8A6420", mn=22, mx=26, ph="Ana & Leo · 06.14.26", label="Names and date"),
              blurb="Ivory linen, torn gold leaf and your names")
    u = f.u
    x, y, w, h = f.win
    gid = u("gl")
    f.mat('<rect width="600" height="600" fill="#F6F0E4"/>', A.linen_tex(u("ln"), "#A8987A", 5, 0.2), A.mottle(2, ["#FFFFFF", "#D8C8A8"], 12, (0.05, 0.12)))
    f.add(f'<defs>{lgrad(gid, GOLD, 0, 0, 1, 1)}</defs>')
    flakes = [A.gold_leaf_patch(u, 104, 98, 44, 30, 3, gid, rot=-30, flecks=16), A.gold_leaf_patch(u, 150, 84, 16, 10, 4, gid, rot=10, flecks=4),
              A.gold_leaf_patch(u, 86, 150, 12, 9, 5, gid, rot=60, flecks=4),
              A.gold_leaf_patch(u, 498, 404, 34, 24, 6, gid, rot=-60, flecks=14), A.gold_leaf_patch(u, 520, 352, 12, 9, 7, gid, rot=20, flecks=3)]
    f.shadow(0.8)
    f.add(f'<path d="{rr(x - 6, y - 6, w + 12, h + 12, 0)}" fill="none" stroke="url(#{gid})" stroke-width="2.2"/>',
          "".join(flakes),
          f'<path d="M 230 452 H 370" stroke="url(#{gid})" stroke-width="1.4" opacity="0.8"/><path d="M 300 446 l 5 6 -5 6 -5 -6 Z" fill="url(#{gid})"/>')
    return f


def moulding_side(gid, outer, inner, side):
    """One mitred side (0 top, 1 right, 2 bottom, 3 left) of a square band between insets outer..inner."""
    a, b = outer, inner
    pts = {0: [(a, a), (600 - a, a), (600 - b, b), (b, b)], 1: [(600 - a, a), (600 - a, 600 - a), (600 - b, 600 - b), (600 - b, b)],
           2: [(600 - a, 600 - a), (a, 600 - a), (b, 600 - b), (600 - b, 600 - b)], 3: [(a, 600 - a), (a, a), (b, b), (b, 600 - b)]}[side]
    return f'<path d="{poly_d(pts)}" fill="url(#{gid})"/>'


def f_ornate():
    f = Frame("ornate", "Vintage ornate gold", "Elegant", (118, 118, 364, 364), blurb="Carved baroque gold frame with a linen liner")
    u = f.u
    x, y, w, h = f.win
    out = []
    # moulding profile from the paper edge inward: (outer, inner, stops) — light from the top left
    profile = [(0, 66, [(0, "#5A3A10"), (1, "#8A6420")]),
               (66, 74, [(0, "#F6E3A4"), (0.5, "#D9AE55"), (1, "#8A6420")]),
               (74, 92, [(0, "#7A5418"), (0.35, "#C99A3E"), (0.7, "#F4DC95"), (1, "#B8892E")]),
               (92, 98, [(0, "#6A4A14"), (1, "#3A2408")]),
               (98, 104, [(0, "#F4DC95"), (1, "#A67A2A")])]
    defs = []
    for k, (a, b, stops) in enumerate(profile):
        for side in range(4):
            gid = u("mg")
            light = side in (0, 3)
            st = [(o, c) for o, c in stops]
            if not light:  # shadow sides: darken
                st = [(o, A_dark(c)) for o, c in st]
            # gradient runs across the band, from outer edge to inner edge
            if side == 0:
                g = lgrad(gid, st, 0, a, 0, b, user=True)
            elif side == 2:
                g = lgrad(gid, st, 0, 600 - a, 0, 600 - b, user=True)
            elif side == 3:
                g = lgrad(gid, st, a, 0, b, 0, user=True)
            else:
                g = lgrad(gid, st, 600 - a, 0, 600 - b, 0, user=True)
            defs.append(g)
            out.append(moulding_side(gid, a, b, side))
    # bead-and-reel along the cove
    beads = []
    for i in range(34):
        t = 80 + i * (440 / 33)
        for (px, py) in ((t, 95), (t, 505), (95, t), (505, t)):
            beads.append(f'<circle cx="{f1(px)}" cy="{f1(py)}" r="2.6" fill="#F6E3A4" stroke="#6A4A14" stroke-width="0.8"/>')
    # linen liner between gold and photo
    liner = (f'<path d="M 104 104 H 496 V 496 H 104 Z {rr(x, y, w, h, 0)}" fill="#EFE6D2" fill-rule="evenodd"/>')
    gid = u("og")
    defs.append(lgrad(gid, GOLD, 0, 0, 1, 1))
    f.mat("<defs>" + "".join(defs) + "</defs>", "".join(out), A.grain_tex(u("g"), "#3A2408", 6, 0.8), "".join(beads), liner,
          A.linen_tex(u("ln"), "#A8987A", 3, 0.18).replace('<rect width="600" height="600"', '<path d="M 104 104 H 496 V 496 H 104 Z ' + rr(x, y, w, h, 0) + '" fill-rule="evenodd"'))
    f.shadow(1.0)
    f.add(f'<path d="{rr(x - 1, y - 1, w + 2, h + 2, 0)}" fill="none" stroke="#B8892E" stroke-width="2"/>')
    # carved corner cartouches: shell fan + C-scrolls + acanthus tips
    corner = (
        f'<path d="M 62 62 L 140 62 C 128 70 120 78 116 92 C 106 84 96 82 86 86 C 82 96 84 106 92 116 C 78 120 70 128 62 140 Z" fill="url(#{gid})" stroke="#5A3A10" stroke-width="1.4"/>'
        + "".join(f'<path d="M 66 66 L {f1(66 + 62 * math.cos(math.radians(a)))} {f1(66 + 62 * math.sin(math.radians(a)))}" stroke="#6A4A14" stroke-width="1.6" opacity="0.7"/>' for a in (12, 28, 45, 62, 78))
        + f'<path d="M 116 92 C 132 96 140 112 130 120 C 122 126 112 118 118 110" fill="none" stroke="url(#{gid})" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="M 92 116 C 96 132 112 140 120 130 C 126 122 118 112 110 118" fill="none" stroke="url(#{gid})" stroke-width="5" stroke-linecap="round"/>'
        f'<path d="M 116 92 C 132 96 140 112 130 120 C 122 126 112 118 118 110" fill="none" stroke="#5A3A10" stroke-width="1" stroke-linecap="round"/>'
        f'<path d="M 92 116 C 96 132 112 140 120 130 C 126 122 118 112 110 118" fill="none" stroke="#5A3A10" stroke-width="1" stroke-linecap="round"/>'
        f'<path d="M 140 62 C 160 58 176 66 182 78 C 170 74 160 76 152 82" fill="url(#{gid})" stroke="#5A3A10" stroke-width="1.2"/>'
        f'<path d="M 62 140 C 58 160 66 176 78 182 C 74 170 76 160 82 152" fill="url(#{gid})" stroke="#5A3A10" stroke-width="1.2"/>'
        f'<circle cx="76" cy="76" r="7" fill="#F6E3A4" stroke="#5A3A10" stroke-width="1.4"/><circle cx="74" cy="74" r="2.4" fill="#FFFFFF" opacity="0.8"/>')
    corners = "".join(f'<g transform="{t}">{corner}</g>' for t in ("", "translate(600 0) scale(-1 1)", "translate(0 600) scale(1 -1)", "translate(600 600) scale(-1 -1)"))
    # centre cartouche on each side
    mid = (f'<path d="M 270 66 C 280 82 292 86 300 86 C 308 86 320 82 330 66 C 318 72 310 70 300 64 C 290 70 282 72 270 66 Z" fill="url(#{gid})" stroke="#5A3A10" stroke-width="1.2"/>'
           f'<ellipse cx="300" cy="78" rx="6" ry="5" fill="#F6E3A4" stroke="#5A3A10" stroke-width="1"/>')
    mids = "".join(f'<g transform="rotate({a} 300 300)">{mid}</g>' for a in (0, 90, 180, 270))
    f.add(corners, mids)
    return f


def A_dark(c):
    c = c.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    k = 0.72
    return f"#{int(r * k):02X}{int(g * k):02X}{int(b * k):02X}"


# ================================================================ SEASONAL & HOLIDAYS
def painted_mat(f, base, flecks, seed):
    u = f.u
    f.mat(f'<rect width="600" height="600" fill="{base}"/>', A.mottle(seed, flecks, 16, (0.04, 0.1)), A.paper_tex(u("pp"), "#8A6A4A", seed, 1.1))


def textured_maple(u, cx, cy, s, fill, dark, light, rot, seed):
    from icons import MAPLE
    pts = MAPLE + [(-px, py) for px, py in reversed(MAPLE[1:])]
    d = "M " + " L ".join(f"{f1(cx + px * s)} {f1(cy + py * s)}" for px, py in pts) + " Z"
    return (f'<g transform="rotate({rot} {f1(cx)} {f1(cy)})">'
            f'<path d="{d}" fill="#3A1A08" opacity="0.15" transform="translate(3 5)"/>'
            + maple_leaf(cx, cy, s, fill, dark, 0, seed, vein=light)
            + strokes(u("mp"), d, (cx - s, cy - s, cx + s, cy + s), [light, dark, "#FFD08A"], seed, n=int(s * 1.2), angle=-90, length=(s * 0.2, s * 0.5), width=(1, 2.6), opacity=(0.15, 0.4))
            + "</g>")


def f_fall():
    f = Frame("fall", "Painted fall leaves", "Seasonal & Holidays", (104, 104, 392, 392), r=4, blurb="Gouache maple, oak and acorns")
    u = f.u
    x, y, w, h = f.win
    painted_mat(f, "#F6ECDB", ["#F2C88A", "#FFFFFF", "#E8A86A"], 12)
    rnd = random.Random(3)
    # scattered little leaves drifting on the mat
    f.mat("".join(textured_maple(u, px, py, rnd.uniform(9, 13), c, d, "#FFE2B8", rnd.uniform(-40, 40), i)
                  for i, (px, py, c, d) in enumerate(((300, 80, "#E2A23A", "#A8701A"), (520, 300, "#D8642E", "#9E3A16"), (80, 330, "#C9442E", "#8E2A1A"),
                                                     (420, 76, "#E8792E", "#B9531E"), (176, 524, "#E2A23A", "#A8701A")))))
    f.shadow(0.9)
    f.add(ink(rr(x - 7, y - 7, w + 14, h + 14, 6), "#7A4A22", 1.8, 2, 2, 0.75))
    def cluster(sd, big=1.0):
        rnd2 = random.Random(sd)
        out = [A.stem([(84, 210), (104, 150), (150, 104), (210, 84)], "#6B4A2E", 3, sd)]
        # back layer: long olive / gold leaves fanning out of the corner
        for k, (ang, L) in enumerate(((-12, 110), (102, 110), (20, 92), (70, 92), (45, 80))):
            col = rnd2.choice([("#8A9A3E", "#5A6A22", "#C8D68A"), ("#C99A3E", "#8A6420", "#F2D28A"), ("#B86A2E", "#7A4418", "#F2B88A")])
            out.append(A.painted_leaf(u, 104, 104, L * big, 30 * big, ang, col[0], col[1], col[2], sd + k, bend=0.25 * (1 if k % 2 else -1), inkc="#4A3412"))
        # front layer: maples in reds, oranges and golds
        for k, (dx, dy, sz, rot_, cols) in enumerate(((60, 22, 38, 30, ("#C9442E", "#8E2A1A")), (22, 62, 38, -60, ("#E8792E", "#B9531E")),
                                                    (44, 44, 34, -15, ("#E2A23A", "#A8701A")), (98, 16, 26, 55, ("#D8642E", "#9E3A16")),
                                                    (14, 100, 26, -95, ("#C9442E", "#8E2A1A")))):
            out.append(textured_maple(u, 84 + dx, 84 + dy, sz * big, cols[0], cols[1], "#FFE2B8", rot_, sd + 10 + k))
        out += [acorn(150, 150, 22, rot=-35), acorn(126, 168, 18, rot=10), acorn(170, 126, 17, rot=-70)]
        for bx, by in ((186, 112), (194, 124), (180, 126), (112, 186), (124, 194)):
            out.append(A.berry(u, bx, by, 5.5, "#B8322A", "#6A1410", "#F07A5A"))
        return "".join(out)
    tl = ['<g transform="translate(72 72) scale(1.32) translate(-72 -72)">', cluster(1), "</g>"]
    br = ['<g transform="rotate(180 300 300) translate(72 72) scale(1.18) translate(-72 -72)">', cluster(40, 0.95), "</g>"]
    f.add("".join(tl), "".join(br))
    return f


def f_holly():
    f = Frame("holly", "Christmas holly", "Seasonal & Holidays", (104, 104, 392, 392), r=4, blurb="Painted holly, pine and red berries")
    u = f.u
    x, y, w, h = f.win
    painted_mat(f, "#F7F1E4", ["#E8D8B8", "#FFFFFF", "#D8E4D0"], 14)
    # candy-stripe ribbon border (inked) around the window
    rid = u("rb")
    f.shadow(0.9)
    f.add(f'<path d="{rr(x - 10, y - 10, w + 20, h + 20, 8)}" fill="none" stroke="#C2343A" stroke-width="5"/>'
          f'<path d="{rr(x - 10, y - 10, w + 20, h + 20, 8)}" fill="none" stroke="#FBF5EA" stroke-width="5" stroke-dasharray="7 9"/>'
          + ink(rr(x - 10, y - 10, w + 20, h + 20, 8), "#7A1A20", 0.8, 3, 1, 0.5))

    def cluster(cxx, cyy, flip, seed):
        sgn = 1 if not flip else -1
        out = []
        for k, (ang, L) in enumerate(((-10, 150), (100, 150), (40, 120), (-40, 100), (130, 100))):
            a = ang if not flip else ang + 180
            out.append(A.pine_sprig(u, cxx, cyy, L, a, seed + k))
        out.append(A.pinecone(u, cxx + sgn * 70, cyy + sgn * 64, 30, -30 if not flip else 150, seed + 9))
        for k, (ang, L) in enumerate(((10, 76), (70, 72), (-30, 62), (115, 60))):
            a = ang if not flip else ang + 180
            out.append(A.holly_leaf(u, cxx + sgn * 20, cyy + sgn * 20, L, a, seed + 20 + k))
        for (dx, dy, r) in ((22, 14, 9), (34, 26, 8.5), (16, 32, 8), (40, 8, 7), (8, 18, 7)):
            out.append(A.berry(u, cxx + sgn * dx, cyy + sgn * dy, r))
        return "".join(out)
    f.add(cluster(96, 96, False, 1), cluster(504, 504, True, 40))
    # a sprinkle of snow dots on the mat
    rnd = random.Random(2)
    f.mat("".join(f'<circle cx="{rnd.uniform(64, 536):.0f}" cy="{rnd.choice([rnd.uniform(64, 94), rnd.uniform(506, 536)]):.0f}" r="{rnd.uniform(1.6, 3):.1f}" fill="#C2343A" opacity="0.35"/>' for _ in range(24)))
    return f


def f_snow():
    f = Frame("snowflakes", "Snowflakes", "Seasonal & Holidays", (106, 106, 388, 388), r=14, blurb="Winter blue with hand-drawn snowflakes")
    u = f.u
    x, y, w, h = f.win
    g = u("sg")
    rnd = random.Random(7)
    dots = "".join(f'<circle cx="{rnd.uniform(0, 600):.0f}" cy="{rnd.uniform(0, 600):.0f}" r="{rnd.uniform(1.2, 3.2):.1f}" fill="#FFFFFF" opacity="{rnd.uniform(0.4, 0.95):.2f}"/>' for _ in range(110))
    f.mat(f'<defs>{lgrad(g, [(0, "#2D4A86"), (0.55, "#4A70B0"), (1, "#7FA2D6")])}</defs><rect width="600" height="600" fill="url(#{g})"/>',
          strokes(u("ws"), "M 0 0 H 600 V 600 H 0 Z", (0, 0, 600, 600), ["#FFFFFF", "#9CB8E8", "#2A4078"], 4, n=220, angle=-20, length=(30, 80), width=(2, 6), opacity=(0.04, 0.12)),
          dots,
          # soft snowdrift along the bottom
          f'<path d="M 0 548 Q 80 522 160 540 T 320 534 T 480 540 T 600 528 V 600 H 0 Z" fill="#FFFFFF" opacity="0.9"/>'
          f'<path d="M 0 560 Q 100 540 200 556 T 400 552 T 600 546" stroke="#C8D8F2" stroke-width="3" fill="none"/>')
    f.shadow(1.0, "#0A1A3A")
    f.add(f'<path d="{rr(x - 5, y - 5, w + 10, h + 10, 18)}" fill="none" stroke="#FFFFFF" stroke-width="5"/>'
          f'<path d="{rr(x - 12, y - 12, w + 24, h + 24, 24)}" fill="none" stroke="#DCE8FA" stroke-width="1.4" stroke-dasharray="1 6" stroke-linecap="round"/>')
    flakes = [(92, 96, 34, 0, 0), (152, 74, 16, 12, 1), (74, 158, 18, 20, 1), (510, 512, 32, 8, 1), (448, 528, 15, 0, 0), (528, 446, 17, 15, 0),
              (510, 90, 22, 10, 0), (90, 508, 20, 5, 1), (300, 78, 12, 0, 1), (300, 522, 12, 20, 0), (78, 300, 11, 0, 0), (522, 300, 11, 10, 1)]
    f.add("".join(A.snowflake(cx_, cy_, r_, "#FFFFFF", "#1A2E5E", rot=rt, kind=k) for cx_, cy_, r_, rt, k in flakes))
    f.add("".join(A.sparkle(px, py, rr_, "#FFFFFF", 0.95) for px, py, rr_ in ((130, 118, 6), (470, 140, 5), (138, 470, 5), (474, 474, 7), (212, 76, 5), (388, 524, 5))))
    return f


def f_hearts():
    f = Frame("hearts", "Hearts & confetti", "Seasonal & Holidays", (106, 106, 388, 388), r=14, blurb="Painted hearts and confetti on blush")
    u = f.u
    x, y, w, h = f.win
    painted_mat(f, "#F9E1E2", ["#FFFFFF", "#F2B8C0", "#FBEDE6"], 21)
    cols = ["#E2546A", "#F29AA8", "#E9B949", "#FFFFFF", "#C2344E", "#F6C6A8"]
    win_test = lambda px, py: (x - 14 < px < x + w + 14 and y - 14 < py < y + h + 14)
    f.mat(A.confetti(5, (64, 64, 536, 536), 70, cols, avoid=win_test))
    f.shadow(0.9, "#4A1020")
    f.add(f'<path d="{rr(x - 5, y - 5, w + 10, h + 10, 18)}" fill="none" stroke="#FFFFFF" stroke-width="5"/>')
    hs = [(96, 100, 34, "#E2546A", "#A8283E", -14), (150, 80, 18, "#F29AA8", "#D0607A", 12), (78, 160, 16, "#C2344E", "#801A2E", -24), (140, 132, 12, "#F6C6A8", "#D88E6E", 10),
          (504, 500, 32, "#E2546A", "#A8283E", 14), (450, 520, 17, "#F29AA8", "#D0607A", -10), (522, 446, 15, "#C2344E", "#801A2E", 22), (462, 470, 11, "#F6C6A8", "#D88E6E", -8),
          (510, 92, 14, "#F29AA8", "#D0607A", 16), (92, 508, 13, "#E2546A", "#A8283E", -16)]
    f.add("".join(A.painted_heart(u, cx_, cy_, s, i, c, d, "#FFD0D8", rot=rt) for i, (cx_, cy_, s, c, d, rt) in enumerate(hs)))
    f.add("".join(A.sparkle(px, py, r_, "#E9B949") for px, py, r_ in ((186, 92, 7), (92, 206, 6), (414, 508, 7), (508, 398, 6))))
    return f


def f_tropical():
    f = Frame("tropical", "Tropical leaves", "Seasonal & Holidays", (104, 104, 392, 392), r=6, blurb="Painted monstera, palms and hibiscus")
    u = f.u
    x, y, w, h = f.win
    painted_mat(f, "#F8EBD6", ["#FFFFFF", "#F6C9A0", "#DDEBCF"], 33)
    f.shadow(0.9)
    f.add(f'<path d="{rr(x - 6, y - 6, w + 12, h + 12, 10)}" fill="none" stroke="#E07A5F" stroke-width="2"/>')
    tl = [A.palm_frond(u, 60, 70, 210, 12, 1, curl=0.18, n=13), A.palm_frond(u, 64, 66, 200, 78, 2, curl=-0.18, n=13),
          A.monstera(u, 40, 40, 170, 42, 3), A.hibiscus(u, 186, 176, 34, 10, 4)]
    br = [A.palm_frond(u, 548, 540, 190, 195, 5, curl=0.18, n=12), A.palm_frond(u, 544, 536, 180, 255, 6, curl=-0.2, n=12),
          A.monstera(u, 566, 566, 150, 222, 7, fill="#3A8A60", dark="#205A3E", light="#7CC09A"),
          A.hibiscus(u, 430, 448, 26, 40, 8, fill="#F6A04A", dark="#C8642A", light="#FFD0A0")]
    f.add("".join(tl), "".join(br))
    return f


def f_grad():
    f = Frame("graduation", "Graduation", "Kids & Fun", (100, 100, 400, 314),
              caption=cap(490, 270, 44, "serif", "#F2D589", mn=22, mx=20, ph="Class of 2026", label="Caption"),
              blurb="Mortarboard, gold laurel and your year")
    u = f.u
    x, y, w, h = f.win
    g = u("ng")
    gid = u("gl")
    f.mat(f'<defs>{rgrad(g, [(0, "#2C3A62"), (1, "#141B30")], 0.5, 0.4, 0.8)}</defs><rect width="600" height="600" fill="url(#{g})"/>',
          A.grain_tex(u("gr"), "#FFFFFF", 3, 0.6))
    f.add(f'<defs>{lgrad(gid, GOLD, 0, 0, 600, 600, user=True)}</defs>')
    rnd = random.Random(4)
    f.mat("".join(A.sparkle(rnd.uniform(66, 534), rnd.choice([rnd.uniform(66, 92), rnd.uniform(420, 534)]), rnd.uniform(3, 6), "#F2D589", rnd.uniform(0.4, 0.9)) for _ in range(16)))
    f.shadow(1.1, "#000000")
    f.add(f'<path d="{rr(x - 6, y - 6, w + 12, h + 12, 0)}" fill="none" stroke="url(#{gid})" stroke-width="2.6"/>'
          f'<path d="{rr(x - 12, y - 12, w + 24, h + 24, 0)}" fill="none" stroke="url(#{gid})" stroke-width="1"/>')
    # laurel branches cradling the caption
    left = [(206, 530), (168, 524), (132, 506), (106, 478), (92, 446)]
    right = [(600 - px, py) for px, py in left]
    f.add(A.laurel(u, left, 3, leaf_l=22, gold_id=gid, dark="#8A6420"), A.laurel(u, right, 4, leaf_l=22, gold_id=gid, dark="#8A6420"))
    f.add(A.mortarboard(u, 140, 118, 78, -16, 5))
    return f


# ================================================================ KIDS & FUN
def f_birthday():
    f = Frame("birthday", "Birthday balloons", "Kids & Fun", (100, 140, 400, 290),
              caption=cap(496, 300, 44, "dms", "#3A2E6A", x=280, mn=22, mx=22, ph="Happy 5th, Mia!", label="Birthday message"),
              blurb="Bunting, balloons and confetti for the big day")
    u = f.u
    x, y, w, h = f.win
    cols = ["#F2A81D", "#E2546A", "#4FA3D9", "#7BC47F", "#B07BD8", "#F27E3A"]
    painted_mat(f, "#FFF8EC", ["#FFFFFF", "#FBE3C8", "#E3F0F8"], 41)
    win_test = lambda px, py: (x - 10 < px < x + w + 10 and y - 10 < py < y + h + 10) or (110 < px < 450 and 446 < py < 524)
    f.mat(A.confetti(9, (64, 64, 536, 536), 60, cols, avoid=win_test))
    f.shadow(0.9)
    f.add(f'<path d="{rr(x - 6, y - 6, w + 12, h + 12, 6)}" fill="none" stroke="#3A2E6A" stroke-width="2" opacity="0.8"/>')
    flag_cols = [("#E2546A", "#A8283E"), ("#F2A81D", "#B8780A"), ("#4FA3D9", "#2A6E9E"), ("#7BC47F", "#3E8A44"), ("#B07BD8", "#7A48A0")]
    f.add(A.bunting(u, 62, 538, 72, 22, 9, flag_cols, 3, flag_h=40))
    bal = [(470, 386, 38, "#E2546A", "#9E2A40", "#FFB0BC"), (512, 324, 32, "#4FA3D9", "#2A6E9E", "#BFE4FA"), (430, 330, 30, "#F2A81D", "#B8780A", "#FFE29A")]
    knot = (500, 532)
    f.add("".join(A.balloon(u, bx, by, r, c, d, l, i, string_to=knot) for i, (bx, by, r, c, d, l) in enumerate(bal)))
    f.add('<path d="M 492 532 q 8 -6 16 0 q -4 8 -8 4 q -4 4 -8 -4 Z" fill="#E2546A"/>')
    return f


def f_baby():
    f = Frame("baby", "Sweet dreams baby", "Kids & Fun", (104, 100, 392, 318), r=34,
              caption=cap(492, 320, 44, "serif", "#5A6A9A", mn=22, mx=22, ph="Welcome, Olivia", label="Baby's name"),
              blurb="Pastel sky, a sleepy moon, stars and clouds")
    u = f.u
    x, y, w, h = f.win
    g = u("bg")
    f.mat(f'<defs>{lgrad(g, [(0, "#E6E4F6"), (0.5, "#F8E6EC"), (1, "#E2EEF8")])}</defs><rect width="600" height="600" fill="url(#{g})"/>',
          A.mottle(17, ["#FFFFFF", "#F2D0DC", "#D0E0F2"], 14, (0.15, 0.3)), A.paper_tex(u("pp"), "#8A8AA8", 17, 0.7))
    rnd = random.Random(6)
    stars = []
    for _ in range(26):
        px, py = rnd.uniform(66, 534), rnd.uniform(66, 534)
        if x - 16 < px < x + w + 16 and y - 16 < py < y + h + 16:
            continue
        if 160 < px < 440 and py > 440:
            continue
        stars.append(A.soft_star(px, py, rnd.uniform(3.5, 7), rnd.choice(["#F6D27A", "#FFFFFF", "#F2B8C8"])))
    f.mat("".join(stars))
    f.shadow(0.7, "#3A3A6A")
    f.add(f'<path d="{rr(x - 6, y - 6, w + 12, h + 12, 40)}" fill="none" stroke="#FFFFFF" stroke-width="6"/>'
          f'<path d="{rr(x - 14, y - 14, w + 28, h + 28, 48)}" fill="none" stroke="#B8C4E6" stroke-width="1.8" stroke-dasharray="2 7" stroke-linecap="round"/>')
    f.add(A.moon(u, 116, 110, 44, 3, rot=-30))
    f.add(A.painted_star(u, 178, 82, 12, 1), A.painted_star(u, 82, 178, 9, 2), A.painted_star(u, 494, 96, 11, 3))
    f.add(A.cloud(u, 494, 422, 120, 5), A.cloud(u, 104, 440, 104, 6, shade="#F2D6E0"))
    # tiny dangling stars from the top-right like a mobile
    for i, (px, ln) in enumerate(((430, 40), (462, 62), (494, 30))):
        f.add(f'<path d="M {px} 66 V {66 + ln}" stroke="#B8C4E6" stroke-width="1.4"/>', A.painted_star(u, px, 74 + ln, 8, 10 + i))
    return f


def f_sports():
    f = Frame("sports", "Team spirit", "Kids & Fun", (100, 100, 400, 314),
              caption=cap(502, 400, 64, "bebas", "#FFFFFF", mn=28, upper=True, ls=3, mx=18, ph="Mia #12", label="Name and number"),
              blurb="Varsity stripes and stars, with a name and number")
    u = f.u
    x, y, w, h = f.win
    g = u("ng")
    # mesh-knit texture
    mesh = "".join(f'<circle cx="{(i % 30) * 20 + (10 if (i // 30) % 2 else 0)}" cy="{(i // 30) * 17}" r="2.2" fill="#000" opacity="0.18"/>' for i in range(30 * 36))
    f.mat(f'<defs>{lgrad(g, [(0, "#22356A"), (1, "#152246")])}</defs><rect width="600" height="600" fill="url(#{g})"/>', mesh,
          # athletic stripes framing the photo (white / red / white)
          f'<path d="{rr(x - 22, y - 22, w + 44, h + 44, 0)}" fill="none" stroke="#FFFFFF" stroke-width="6"/>'
          f'<path d="{rr(x - 13, y - 13, w + 26, h + 26, 0)}" fill="none" stroke="#D63A3A" stroke-width="8"/>'
          f'<path d="{rr(x - 5, y - 5, w + 10, h + 10, 0)}" fill="none" stroke="#FFFFFF" stroke-width="4"/>')
    f.shadow(1.0, "#000")
    f.add("".join(A.soft_star(px, 76, r_, "#FFFFFF") for px, r_ in ((260, 9), (300, 12), (340, 9))))
    # name banner
    f.add('<path d="M 96 452 H 504 L 520 486 L 504 520 H 96 L 80 486 Z" fill="#D63A3A"/>'
          '<path d="M 96 452 H 504 L 520 486 L 504 520 H 96 L 80 486 Z" fill="none" stroke="#FFFFFF" stroke-width="3"/>'
          '<path d="M 104 460 H 496" stroke="#FFFFFF" stroke-width="1" opacity="0.4"/>')
    f.caption["y"] = 508
    return f


# ---------------------------------------------------------------- registry
BUILDERS = [f_none, f_white, f_instant, f_gallery,
            f_rounded, f_film, f_stamp, f_postcard, f_honey,
            f_goldline, f_lace, f_floral, f_eucalyptus, f_wedding, f_ornate,
            f_fall, f_holly, f_snow, f_hearts, f_tropical,
            f_birthday, f_baby, f_sports, f_grad]


def frames():
    return [b() for b in BUILDERS]


def sample_scene():
    """Stand-in picture for the frame teaser on the photo page (before the customer adds photos)."""
    rnd = random.Random(2)
    out = ['<defs>' + lgrad("smp-sky", [(0, "#7FB8D8"), (0.55, "#F6D9A0"), (1, "#F2A86A")]) + rgrad("smp-sun", [(0, "#FFF6D0"), (0.4, "#FFE6A0", 0.9), (1, "#FFE6A0", 0)]) + '</defs>',
           '<rect width="600" height="600" fill="url(#smp-sky)"/><circle cx="410" cy="300" r="170" fill="url(#smp-sun)"/><circle cx="410" cy="300" r="56" fill="#FFF4D2"/>',
           '<path d="M 0 360 Q 120 300 240 340 T 470 320 T 600 330 V 600 H 0 Z" fill="#9AB4C8" opacity="0.8"/>',
           '<path d="M 0 410 Q 150 360 300 400 T 600 380 V 600 H 0 Z" fill="#6E9A6A"/>',
           '<path d="M 0 470 Q 200 430 380 470 T 600 450 V 600 H 0 Z" fill="#4E7E4A"/>']
    for _ in range(70):
        x, y = rnd.uniform(0, 600), rnd.uniform(470, 600)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(3, 7):.1f}" fill="{rnd.choice(["#F6D27A", "#FFFFFF", "#F29AA8", "#E8792E"])}"/>')
    out.append('<path d="M 150 300 q 10 -8 20 0 q 10 -8 20 0 M 220 260 q 8 -6 16 0 q 8 -6 16 0" stroke="#3A3A4A" stroke-width="3" fill="none"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600">{"".join(out)}</svg>'


def build(only=None):
    OUT.mkdir(parents=True, exist_ok=True)
    meta = []
    keep = set()
    for f in frames():
        m = f.meta()
        meta.append(m)
        keep.add(f"{f.id}.svg")
        if only and f.id not in only:
            continue
        body = re.sub(r"(\d+\.\d)\d+", r"\1", f.svg())          # one decimal is plenty at 600 units
        body = re.sub(r"(?<=[ ,\"(])(-?\d+)\.0(?=[ ,\")A-Za-z])", r"\1", body)
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">{body}</svg>'
        (OUT / f"{f.id}.svg").write_text(svg, encoding="utf-8")
    (OUT / "sample.svg").write_text(sample_scene(), encoding="utf-8")
    keep.add("sample.svg")
    for old in OUT.glob("*.svg"):
        if old.name not in keep:
            old.unlink()
    meta.sort(key=lambda m: GROUPS.index(m["group"]))
    (OUT / "frames.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(meta)} frames")
    return meta


if __name__ == "__main__":
    build(set(sys.argv[1:]) or None)
