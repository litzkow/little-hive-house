"""Photo magnet frames, second edition (Oct 2026): calmer, more professional, most of them with a caption.

The canvas is the printed picture: 600 units = IMAGE_IN (about 2.08 in) on the print sheet, the 2 in magnet face is
almost all of it, so every line, ornament and caption stays at least 26 units from the edge (the outer ~12 units
roll onto the rounded edge of the magnet).

Captions: each caption frame has a default style and the styles the customer may switch to in the builder:
  hand     handwritten (Caveat)              script   flowing script (Dancing Script)
  classic  elegant italic (Cormorant)        modern   small spaced capitals (Jost)
  mono     date-stamp digits (DM Mono), only on the "Date stamp" frame
frames.json carries, per caption, `style` (the default) and `styles` {key: font, size, min, upper, ls, family...},
so the builder, the admin and the print server just merge the chosen style over the caption.

Frames of the first edition that are not redrawn here stay on disk, hidden from the builder (`hidden: true`), so
orders and carts that use them still print. Run: python3 tools/frames_v2.py (then python3 tools/build.py)."""
import json
import math
import random
import re
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import frames as V1  # noqa: E402
from frames import Frame, rr, FONTS, OUT, GROUPS  # noqa: E402
import frame_art as A  # noqa: E402
from frame_art import f1, lgrad, rgrad  # noqa: E402

# style key -> (font key, size factor against the handwritten size, upper, letter-spacing in em)
STYLES = {
    "hand": ("caveat", 1.0, False, 0),
    "script": ("dancing", 0.84, False, 0),
    "classic": ("cormorant", 0.92, False, 0),
    "modern": ("jost", 0.5, True, 0.16),
    "mono": ("mono", 0.5, True, 0.04),
}
STYLE_NAMES = {"hand": "Handwritten", "script": "Script", "classic": "Classic", "modern": "Modern", "mono": "Date stamp"}
ALL = ("hand", "script", "classic", "modern")


def cap2(y, size, color, style="hand", allow=ALL, w=440, x=300, mx=24, ph="", label="Caption", rot=0, kicker=None):
    """A caption box; `size` is the handwritten size, the other styles scale from it."""
    return {"x": x, "y": y, "w": w, "base": size, "color": color, "rot": rot, "max": mx, "placeholder": ph, "label": label,
            "kicker": kicker, "style": style, "allow": list(allow)}


class F2(Frame):
    def meta(self):
        m = {"id": self.id, "name": self.name, "group": self.group, "window": [round(v, 1) for v in self.win], "shape": self.shape,
             "radius": self.r, "blurb": self.blurb, "caption": None, "v": 2}
        c = self.caption
        if c:
            styles = {}
            for key in c["allow"]:
                font, k, upper, ls = STYLES[key]
                size = round(c["base"] * k)
                _, fam, st, wt = FONTS[font]
                styles[key] = {"font": font, "family": fam, "style": st, "weight": wt, "size": size, "min": max(12, round(size * 0.55)),
                               "upper": upper, "ls": round(ls * size, 1), "name": STYLE_NAMES[key]}
            d = styles[c["style"]]
            out = {"x": c["x"], "y": c["y"], "w": c["w"], "color": c["color"], "rot": c["rot"], "max": c["max"],
                   "placeholder": c["placeholder"], "label": c["label"], "kicker": None,
                   "font": d["font"], "family": d["family"], "style": d["style"], "weight": d["weight"], "size": d["size"], "min": d["min"],
                   "upper": d["upper"], "ls": d["ls"], "default": c["style"], "styles": styles}
            if c.get("kicker"):
                k = dict(c["kicker"])
                _, kf, ks, kw = FONTS[k["font"]]
                k.update({"family": kf, "style": ks, "weight": kw})
                out["kicker"] = k
            m["caption"] = out
        return m


# ---------------------------------------------------------------- small drawing helpers
def bg(color):
    return f'<rect width="600" height="600" fill="{color}"/>'


def paper(f, seed, fleck="#9A8E7A", density=0.6):
    return A.paper_tex(f.u("pt"), fleck, seed, density)


def hair(x, y, w, h, color, sw=1.2, r=0, op=1.0):
    return f'<path d="{rr(x, y, w, h, r)}" fill="none" stroke="{color}" stroke-width="{sw}" opacity="{op}"/>'


def gold_defs(gid):
    return "<defs>" + lgrad(gid, [(0, "#9C7430"), (0.3, "#E6C77E"), (0.55, "#B98E3E"), (0.8, "#EBD08C"), (1, "#8E6828")], 0, 0, 1, 1) + "</defs>"


def leaf(cx, cy, L, W, ang, fill, vein=None, op=1.0):
    """Almond leaf from its base (cx, cy), length L, width W, pointing at `ang` degrees."""
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    tx, ty = cx + ux * L, cy + uy * L
    c1 = (cx + ux * L * 0.45 + nx * W, cy + uy * L * 0.45 + ny * W)
    c2 = (cx + ux * L * 0.45 - nx * W, cy + uy * L * 0.45 - ny * W)
    d = f"M {f1(cx)} {f1(cy)} Q {f1(c1[0])} {f1(c1[1])} {f1(tx)} {f1(ty)} Q {f1(c2[0])} {f1(c2[1])} {f1(cx)} {f1(cy)} Z"
    out = f'<path d="{d}" fill="{fill}" opacity="{op}"/>'
    if vein:
        out += f'<path d="M {f1(cx)} {f1(cy)} L {f1(cx + ux * L * 0.85)} {f1(cy + uy * L * 0.85)}" stroke="{vein}" stroke-width="1" opacity="0.6"/>'
    return out


def sprig(x0, y0, length, ang, n, fill, stemc, L=26, W=8, seed=1, curve=0.18, vein=None):
    """A slim botanical sprig: a curved stem with leaves in pairs."""
    rnd = random.Random(seed)
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    ex, ey = x0 + ux * length, y0 + uy * length
    cxp, cyp = x0 + ux * length / 2 + nx * length * curve, y0 + uy * length / 2 + ny * length * curve
    out = [f'<path d="M {f1(x0)} {f1(y0)} Q {f1(cxp)} {f1(cyp)} {f1(ex)} {f1(ey)}" stroke="{stemc}" stroke-width="1.8" fill="none" stroke-linecap="round"/>']
    for i in range(n):
        t = 0.18 + 0.8 * i / max(1, n - 1)
        px = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cxp + t * t * ex
        py = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cyp + t * t * ey
        sc = 1 - 0.35 * t
        for side in (1, -1):
            la = ang + side * (48 + rnd.uniform(-6, 6))
            out.append(leaf(px, py, L * sc, W * sc, la, fill, vein))
    out.append(leaf(ex, ey, L * 0.8, W * 0.8, ang, fill, vein))
    return "".join(out)


def round_leaf_sprig(x0, y0, length, ang, n, fill, stemc, r=9, curve=0.2):
    """Eucalyptus: round leaves alternating along a curved stem."""
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    ex, ey = x0 + ux * length, y0 + uy * length
    cxp, cyp = x0 + ux * length / 2 + nx * length * curve, y0 + uy * length / 2 + ny * length * curve
    out = [f'<path d="M {f1(x0)} {f1(y0)} Q {f1(cxp)} {f1(cyp)} {f1(ex)} {f1(ey)}" stroke="{stemc}" stroke-width="1.6" fill="none"/>']
    for i in range(n):
        t = 0.12 + 0.86 * i / max(1, n - 1)
        px = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cxp + t * t * ex
        py = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cyp + t * t * ey
        side = 1 if i % 2 else -1
        rr_ = r * (1 - 0.3 * t)
        out.append(f'<ellipse cx="{f1(px + nx * side * rr_ * 0.9)}" cy="{f1(py + ny * side * rr_ * 0.9)}" rx="{f1(rr_)}" ry="{f1(rr_ * 0.82)}" fill="{fill}" opacity="0.92"/>')
    return "".join(out)


def heart(cx, cy, s, fill, op=1.0):
    d = (f"M {f1(cx)} {f1(cy + s * 0.35)} C {f1(cx - s * 0.9)} {f1(cy - s * 0.25)} {f1(cx - s * 0.45)} {f1(cy - s * 0.85)} {f1(cx)} {f1(cy - s * 0.4)} "
         f"C {f1(cx + s * 0.45)} {f1(cy - s * 0.85)} {f1(cx + s * 0.9)} {f1(cy - s * 0.25)} {f1(cx)} {f1(cy + s * 0.35)} Z")
    return f'<path d="{d}" fill="{fill}" opacity="{op}"/>'


def star(cx, cy, r, fill, op=1.0, k=0.45):
    pts = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        rad = r if i % 2 == 0 else r * k
        pts.append(f"{f1(cx + rad * math.cos(a))},{f1(cy + rad * math.sin(a))}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" opacity="{op}"/>'


def holly_leaf(cx, cy, L, ang, fill):
    """Flat holly leaf with soft points, from the base."""
    a = math.radians(ang)
    ux, uy, nx, ny = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    pts = []
    for i in range(0, 7):
        t = i / 6
        w = math.sin(math.pi * t) * L * 0.34 * (1.18 if i % 2 else 0.8)
        pts.append((cx + ux * L * t + nx * w, cy + uy * L * t + ny * w))
    for i in range(5, 0, -1):
        t = i / 6
        w = math.sin(math.pi * t) * L * 0.34 * (1.18 if i % 2 else 0.8)
        pts.append((cx + ux * L * t - nx * w, cy + uy * L * t - ny * w))
    d = "M " + " L ".join(f"{f1(x)} {f1(y)}" for x, y in pts) + " Z"
    return (f'<path d="{d}" fill="{fill}" stroke="{fill}" stroke-width="2" stroke-linejoin="round"/>'
            f'<path d="M {f1(cx)} {f1(cy)} L {f1(cx + ux * L * 0.9)} {f1(cy + uy * L * 0.9)}" stroke="#FFFFFF" stroke-width="1" opacity="0.35"/>')


def write_meta_order(metas):
    order = {g: i for i, g in enumerate(GROUPS)}
    return sorted(metas, key=lambda m: (m.get("hidden", False), order.get(m["group"], 99)))


# ================================================================ CLASSIC
def n_none():
    return F2("none", "Full photo", "Classic", (0, 0, 600, 600), blurb="Your photo fills the whole magnet")


def n_border():
    f = F2("border", "Thin white border", "Classic", (30, 30, 540, 540), blurb="A slim white edge, like a printed photo")
    f.mat(bg("#FFFFFF"), paper(f, 11, "#B9B2A6", 0.3))
    return f


def n_gallery():
    f = F2("gallery", "Gallery mat", "Classic", (82, 82, 436, 436), blurb="A wide white mat with a fine rule, like a framed print")
    f.mat(bg("#FCFBF8"), paper(f, 12, "#B2A898", 0.4), hair(58, 58, 484, 484, "#CFC8BB", 1.1))
    f.shadow(0.8)
    return f


def n_label():
    f = F2("label", "Gallery with caption", "Classic", (70, 62, 460, 400),
           caption=cap2(536, 64, "#3B3632", "modern", w=440, mx=26, ph="Lake house · 2026", label="Caption"),
           blurb="White mat with a short caption underneath")
    f.mat(bg("#FCFBF8"), paper(f, 13, "#B2A898", 0.4))
    f.shadow(0.7)
    return f


def n_instant():
    f = F2("instant", "Instant print", "Classic", (52, 50, 496, 414),
           caption=cap2(540, 66, "#2E3550", "hand", w=460, mx=22, ph="Summer 2026", label="Caption", rot=-1.5),
           blurb="A clean instant print with a caption in the thick bottom border")
    f.mat(bg("#FBFAF6"), paper(f, 14, "#A89C88", 0.5),
          '<path d="M 0 0 H 600 V 22 Q 300 34 0 14 Z" fill="#FFFFFF" opacity="0.55"/>')
    x, y, w, h = f.win
    f.shadow(0.9, "#000000")
    f.add(hair(x, y, w, h, "#2A2620", 1.4, op=0.35))
    return f


def n_band():
    f = F2("band", "Name band", "Classic", (0, 0, 600, 470),
           caption=cap2(552, 70, "#3A2A1C", "classic", w=480, mx=24, ph="The Silvas · Lisbon", label="Caption"),
           blurb="Full photo with a cream name band, like our poster magnets")
    f.mat(bg("#F4ECDD"), paper(f, 15, "#A8946E", 0.6), '<rect y="470" width="600" height="3" fill="#E2D3B5"/>',
          '<path d="M 252 492 H 348" stroke="#C9A866" stroke-width="1.4"/>')
    return f


# ================================================================ MODERN
def n_arch():
    f = F2("arch", "Arch", "Modern", (116, 50, 368, 420), shape="arch",
           caption=cap2(540, 64, "#5A4636", "script", w=440, mx=24, ph="Our little one", label="Caption"),
           blurb="Photo in a soft arch on warm sand")
    f.mat(bg("#EFE5D6"), paper(f, 16, "#9E8A6C", 0.5))
    f.add(f'<path d="{f.wd(10)}" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.9"/>')
    return f


def n_circle():
    f = F2("circle", "Circle", "Modern", (130, 48, 340, 340), shape="circle",
           caption=cap2(482, 64, "#3E4A3A", "classic", w=460, mx=24, ph="Bento", label="Caption"),
           blurb="A round photo on soft sage")
    f.mat(bg("#DCE3D4"), paper(f, 17, "#6E7E64", 0.4))
    f.add(f'<path d="{f.wd(9)}" fill="none" stroke="#FFFFFF" stroke-width="2.2"/>')
    f.add('<path d="M 262 516 H 338" stroke="#8A9A80" stroke-width="1.2"/>')
    return f


def n_film():
    f = F2("film", "Film frame", "Modern", (44, 78, 512, 392),
           caption=cap2(562, 60, "#E9A23B", "modern", allow=("modern", "hand"), w=420, mx=22, ph="Golden hour", label="Caption"),
           blurb="A 35 mm negative frame, sprockets and all")
    holes = "".join(f'<rect x="{30 + i * 49}" y="{y}" width="26" height="28" rx="4" fill="#F2EEE6"/>' for i in range(12) for y in (34, 488))
    f.mat(bg("#141210"), holes)
    return f


def n_datestamp():
    f = F2("datestamp", "Date stamp", "Modern", (0, 0, 600, 600),
           caption=cap2(552, 92, "#FF7A1A", "mono", allow=("mono",), x=410, w=300, mx=10, ph="10 17 26", label="Date"),
           blurb="Full photo with an orange date in the corner, like an old film camera")
    # a soft shade behind the date so it reads on any photo
    g = f.u("v")
    f.add(f'<defs>{rgrad(g, [(0, "#000000", 0.62), (0.6, "#000000", 0.3), (1, "#000000", 0)], 0.5, 0.5, 0.5)}</defs><ellipse cx="410" cy="536" rx="220" ry="80" fill="url(#{g})"/>')
    return f


def n_postcard():
    f = F2("postcard", "Postcard", "Modern", (36, 36, 528, 420),
           caption=cap2(556, 68, "#22406E", "script", allow=("script", "classic", "hand", "modern"), w=470, mx=20, ph="Lisbon", label="Place",
                        kicker={"text": "GREETINGS FROM", "y": 496, "size": 17, "font": "jost", "color": "#B4483C", "ls": 4}),
           blurb="A travel postcard with a little stamp and the place you visited")
    f.mat(bg("#FBF7EE"), paper(f, 18, "#A89878", 0.5))
    # airmail edge: thin diagonal stripes along the very bottom
    u = f.u("air")
    f.mat(f'<defs><pattern id="{u}" width="36" height="36" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
          f'<rect width="12" height="36" fill="#C8463C"/><rect x="18" width="12" height="36" fill="#2F5A9A"/></pattern></defs>'
          f'<rect x="0" y="582" width="600" height="18" fill="url(#{u})" opacity="0.9"/>')
    # stamp in the top right corner of the photo
    sx, sy, sw, sh = 452, 52, 84, 100
    perf = "".join(f'<circle cx="{f1(sx + i * sw / 7)}" cy="{f1(yy)}" r="4.2" fill="#FBF7EE"/>' for i in range(8) for yy in (sy, sy + sh)) + \
        "".join(f'<circle cx="{f1(xx)}" cy="{f1(sy + i * sh / 8)}" r="4.2" fill="#FBF7EE"/>' for i in range(9) for xx in (sx, sx + sw))
    f.add(f'<g opacity="0.97"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="#FBF7EE"/>{perf}'
          f'<rect x="{sx + 9}" y="{sy + 9}" width="{sw - 18}" height="{sh - 18}" fill="#7FB3C9"/>'
          f'<circle cx="{sx + 56}" cy="{sy + 34}" r="11" fill="#F6C65B"/>'
          f'<path d="M {sx + 9} {sy + 66} q 14 -10 28 0 t 28 0 t 10 0 V {sy + sh - 9} H {sx + 9} Z" fill="#2F5A9A"/>'
          f'<path d="M {sx + 9} {sy + 74} q 14 -8 28 0 t 28 0 t 10 0" stroke="#FFFFFF" stroke-width="2" fill="none" opacity="0.7"/></g>'
          f'<g fill="none" stroke="#3A3A3A" stroke-width="1.6" opacity="0.55"><circle cx="{sx - 6}" cy="{sy + 60}" r="26"/>'
          f'<path d="M {sx - 60} {sy + 48} q 12 -6 24 0 t 24 0 M {sx - 60} {sy + 60} q 12 -6 24 0 t 24 0 M {sx - 60} {sy + 72} q 12 -6 24 0 t 24 0"/></g>')
    return f


# ================================================================ ELEGANT
def n_gold():
    f = F2("gold-cream", "Gold line", "Elegant", (78, 70, 444, 392),
           caption=cap2(538, 66, "#7A5A2A", "classic", w=440, mx=24, ph="Forever & always", label="Caption"),
           blurb="Ivory mat with a fine double gold line")
    g = f.u("g")
    x, y, w, h = f.win
    f.mat(bg("#F8F2E6"), paper(f, 19, "#A08A62", 0.5), gold_defs(g),
          f'<path d="{rr(x - 14, y - 14, w + 28, h + 28, 0)}" fill="none" stroke="url(#{g})" stroke-width="2.4"/>'
          f'<path d="{rr(x - 21, y - 21, w + 42, h + 42, 0)}" fill="none" stroke="url(#{g})" stroke-width="0.9"/>')
    f.shadow(0.6)
    return f


def n_wedding():
    f = F2("wedding", "Wedding", "Elegant", (84, 64, 432, 384),
           caption=cap2(532, 70, "#6E5326", "script", w=376, mx=26, ph="Ana & Leo · 06.14.26", label="Names and date"),
           blurb="Soft linen, a gold rule and little laurel sprigs for your names and date")
    g = f.u("g")
    x, y, w, h = f.win
    f.mat(bg("#F6F1E8"), A.linen_tex(f.u("ln"), "#B8A88A", 4, 0.12), gold_defs(g),
          f'<path d="{rr(x - 12, y - 12, w + 24, h + 24, 0)}" fill="none" stroke="url(#{g})" stroke-width="1.6"/>')
    laurel = sprig(98, 556, 56, 196, 4, "#B99A55", "#A88A48", L=15, W=5, seed=3, curve=-0.12) + \
        sprig(502, 556, 56, -16, 4, "#B99A55", "#A88A48", L=15, W=5, seed=4, curve=0.12)
    f.add(laurel)
    f.shadow(0.6)
    return f


def n_botanical():
    f = F2("botanical", "Botanical", "Elegant", (74, 70, 452, 392),
           caption=cap2(540, 64, "#3F5244", "classic", w=430, mx=24, ph="Grandma's garden", label="Caption"),
           blurb="Cream mat with eucalyptus sprigs in two corners")
    f.mat(bg("#F5F1E7"), paper(f, 20, "#8A8A6A", 0.5))
    f.shadow(0.6)
    f.add(round_leaf_sprig(40, 150, 150, -70, 9, "#93AE9C", "#7A8E7E", r=11, curve=0.2),
          round_leaf_sprig(56, 120, 110, -35, 7, "#B5C8B8", "#7A8E7E", r=9, curve=-0.2),
          sprig(566, 300, 140, 96, 5, "#7E9C86", "#6E8470", L=22, W=7, seed=6, curve=-0.15))
    return f


def n_deco():
    f = F2("deco", "Art deco", "Elegant", (86, 82, 428, 380),
           caption=cap2(540, 64, "#D8B76E", "modern", allow=("modern", "classic", "script"), w=420, mx=24, ph="The Roaring Twenties", label="Caption"),
           blurb="Deep navy with gold art deco corners")
    g = f.u("g")
    x, y, w, h = f.win
    corners = []
    for cx, cy, sx, sy in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        for k, ln in ((14, 44), (22, 30), (30, 18)):
            corners.append(f'<path d="M {f1(cx - sx * k)} {f1(cy - sy * k + sy * ln)} V {f1(cy - sy * k)} H {f1(cx - sx * k + sx * ln)}" '
                           f'fill="none" stroke="url(#{g})" stroke-width="1.6"/>')
        corners.append(f'<path d="M {f1(cx - sx * 34)} {f1(cy - sy * 34)} l {f1(sx * 6)} {f1(-sy * 0)} l {f1(-sx * 6)} {f1(sy * 6)} Z" fill="url(#{g})" transform="rotate(45 {f1(cx - sx * 34)} {f1(cy - sy * 34)})"/>')
    f.mat(bg("#1C2638"), paper(f, 21, "#9AA6C0", 0.4), gold_defs(g),
          f'<path d="{rr(x - 6, y - 6, w + 12, h + 12, 0)}" fill="none" stroke="url(#{g})" stroke-width="1.2"/>', "".join(corners))
    return f


# ================================================================ SEASONAL & HOLIDAYS
def n_holly():
    f = F2("holly", "Holiday", "Seasonal & Holidays", (70, 62, 460, 400),
           caption=cap2(538, 66, "#8E2A26", "script", w=430, mx=24, ph="Merry Christmas 2026", label="Caption"),
           blurb="Cream mat with a sprig of holly and a festive caption")
    f.mat(bg("#FAF6EE"), paper(f, 22, "#A8946E", 0.5))
    f.shadow(0.6)
    sprig_ = (holly_leaf(92, 86, 56, 200, "#2F6247") + holly_leaf(92, 86, 50, 250, "#3B7556") + holly_leaf(92, 86, 46, 160, "#2A5A40") +
              "".join(f'<circle cx="{cx}" cy="{cy}" r="8.5" fill="#C23B33"/><circle cx="{cx - 2.5}" cy="{cy - 2.5}" r="2.4" fill="#FFFFFF" opacity="0.55"/>'
                      for cx, cy in ((96, 92), (110, 82), (100, 106))))
    f.add(sprig_)
    f.add("".join(star(cx, cy, r, "#C9A34E", 0.9) for cx, cy, r in ((508, 536, 7), (92, 536, 7))))
    return f


def n_fall():
    from gouache import maple_leaf
    f = F2("fall", "Autumn", "Seasonal & Holidays", (70, 62, 460, 400),
           caption=cap2(538, 66, "#7A3E1E", "hand", w=430, mx=24, ph="Pumpkin patch 2026", label="Caption"),
           blurb="Warm cream with a few falling leaves")
    f.mat(bg("#F7EEDD"), paper(f, 23, "#A07A4E", 0.5))
    f.shadow(0.6)
    f.add(maple_leaf(528, 76, 34, "#C8642E", "#9C4520", rot=28, seed=2),
          maple_leaf(490, 50, 20, "#E0A23A", "#B87A22", rot=-18, seed=3),
          maple_leaf(72, 84, 26, "#B5482A", "#8A3018", rot=-30, seed=4))
    return f


def n_hearts():
    f = F2("hearts", "Love", "Seasonal & Holidays", (74, 66, 452, 392), r=18,
           caption=cap2(534, 66, "#A23E52", "script", w=420, mx=24, ph="Happy Valentine's Day", label="Caption"),
           blurb="Blush pink with tiny hearts, for Valentine's and anniversaries")
    f.mat(bg("#F6E3E0"), paper(f, 24, "#B88A86", 0.4))
    f.add(f'<path d="{f.wd(8)}" fill="none" stroke="#FFFFFF" stroke-width="2"/>')
    f.add(heart(66, 534, 13, "#D46A7E"), heart(534, 534, 13, "#D46A7E"), heart(88, 556, 7, "#E9A3AE"), heart(512, 556, 7, "#E9A3AE"))
    return f


def n_snow():
    f = F2("snowflakes", "Winter", "Seasonal & Holidays", (70, 62, 460, 400),
           caption=cap2(538, 66, "#2F4A6E", "classic", w=430, mx=24, ph="First snow · 2026", label="Caption"),
           blurb="Icy blue with a few fine snowflakes")
    f.mat(bg("#E6EEF4"), paper(f, 25, "#7E94AC", 0.4))
    f.shadow(0.5)
    rnd = random.Random(5)
    flakes = "".join(A.snowflake(x, y, r, "#FFFFFF", "#8AA4C2", sw=1.6, rot=rnd.uniform(0, 30), kind=rnd.randint(0, 1))
                     for x, y, r in ((48, 48, 14), (552, 70, 11), (40, 300, 9), (560, 330, 12), (60, 560, 10), (548, 560, 13)))
    f.add(flakes)
    return f


# ================================================================ KIDS & FUN
def n_birthday():
    f = F2("birthday", "Birthday", "Kids & Fun", (70, 62, 460, 400),
           caption=cap2(538, 68, "#3A2E5A", "hand", w=440, mx=22, ph="Happy 5th, Mia!", label="Caption"),
           blurb="White with soft confetti, for birthday parties")
    f.mat(bg("#FFFDF8"))
    x, y, w, h = f.win
    avoid = (lambda px, py: (x - 14 < px < x + w + 14 and y - 14 < py < y + h + 14) or (90 < px < 510 and 494 < py < 572))
    f.mat(A.confetti(7, (24, 24, 576, 576), 70, ["#F6B6C4", "#9FD3E0", "#F8D57E", "#B8A6E6", "#9ED8B4"], avoid=avoid, size=(6, 12)))
    f.shadow(0.5)
    return f


def n_baby():
    f = F2("baby", "Sweet dreams", "Kids & Fun", (126, 52, 348, 404), shape="arch",
           caption=cap2(534, 66, "#5E6A8A", "script", w=440, mx=22, ph="Welcome, Olivia", label="Name"),
           blurb="Soft blue with a little moon and stars, for new babies")
    f.mat(bg("#E8EEF4"), paper(f, 26, "#8A9AB0", 0.4))
    f.add(f'<path d="{f.wd(9)}" fill="none" stroke="#FFFFFF" stroke-width="2"/>')
    f.add('<path d="M 76 102 a 26 26 0 1 0 30 34 a 20 20 0 1 1 -30 -34 Z" fill="#F4D58A"/>',
          star(520, 90, 9, "#F4D58A"), star(498, 132, 5, "#F4D58A"), star(86, 196, 5, "#F4D58A"), star(530, 220, 6, "#F4D58A"))
    return f


def n_graduation():
    f = F2("graduation", "Graduation", "Kids & Fun", (70, 62, 460, 400),
           caption=cap2(540, 64, "#E2C47E", "modern", allow=("modern", "classic", "script"), w=440, mx=20, ph="Class of 2026", label="Caption"),
           blurb="Navy and gold, for the big day")
    g = f.u("g")
    x, y, w, h = f.win
    cap_icon = ('<g transform="translate(300 492)"><path d="M -22 0 L 0 -9 L 22 0 L 0 9 Z" fill="url(#G)"/>'
                '<path d="M -12 4 V 11 Q 0 17 12 11 V 4" fill="url(#G)"/><path d="M 16 2 V 14" stroke="url(#G)" stroke-width="1.5"/></g>').replace("#G", "#" + g)
    f.mat(bg("#1E2C47"), paper(f, 27, "#8A9AC0", 0.4), gold_defs(g),
          f'<path d="{rr(x - 10, y - 10, w + 20, h + 20, 0)}" fill="none" stroke="url(#{g})" stroke-width="1.6"/>', cap_icon)
    return f


def n_sports():
    f = F2("sports", "Team", "Kids & Fun", (0, 0, 600, 600),
           caption=cap2(548, 84, "#FFFFFF", "modern", allow=("modern", "hand"), w=480, mx=18, ph="Mia #12", label="Name and number"),
           blurb="Full photo with a bold team band across the bottom")
    f.add('<path d="M 0 486 L 600 450 V 600 H 0 Z" fill="#1F4E9A"/><path d="M 0 474 L 600 438 V 450 L 0 486 Z" fill="#F2B53A"/>')
    return f


BUILDERS = [n_none, n_border, n_gallery, n_label, n_instant, n_band,
            n_arch, n_circle, n_film, n_datestamp, n_postcard,
            n_gold, n_wedding, n_botanical, n_deco,
            n_holly, n_fall, n_hearts, n_snow,
            n_birthday, n_baby, n_graduation, n_sports]


def clean_svg(body):
    body = re.sub(r"(\d+\.\d)\d+", r"\1", body)
    body = re.sub(r"(?<=[ ,\"(])(-?\d+)\.0(?=[ ,\")A-Za-z])", r"\1", body)
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">{body}</svg>'


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    new = [b() for b in BUILDERS]
    ids = {f.id for f in new}
    metas = []
    for f in new:
        (OUT / f"{f.id}.svg").write_text(clean_svg(f.svg()), encoding="utf-8")
        metas.append(f.meta())
    # first-edition frames not redrawn: kept for old orders and carts, hidden from the builder
    for f in V1.frames():
        if f.id in ids:
            continue
        (OUT / f"{f.id}.svg").write_text(clean_svg(f.svg()), encoding="utf-8")
        m = f.meta()
        m["hidden"] = True
        metas.append(m)
    (OUT / "sample.svg").write_text(V1.sample_scene(), encoding="utf-8")
    keep = {f"{m['id']}.svg" for m in metas} | {"sample.svg"}
    for old in OUT.glob("*.svg"):
        if old.name not in keep:
            old.unlink()
    metas = write_meta_order(metas)
    (OUT / "frames.json").write_text(json.dumps(metas, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(new)} frames (+{len(metas) - len(new)} hidden)")
    return metas


if __name__ == "__main__":
    build()
