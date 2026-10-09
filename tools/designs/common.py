"""Shared helpers for generating Little Hive House magnet designs (600x600 SVG, prints at 2x2 in)."""
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2] / "designs"

SERIF_IT = "font-family=\"'Playfair Display', Georgia, serif\" font-style=\"italic\" font-weight=\"700\""
BEBAS = "font-family=\"'Bebas Neue', Impact, sans-serif\""
MONO = "font-family=\"'DM Mono', ui-monospace, monospace\" font-weight=\"500\""
DMS = "font-family=\"'DM Serif Display', Georgia, serif\""
CINZEL = "font-family=\"Cinzel, 'Times New Roman', serif\" font-weight=\"600\""
JOS = "font-family=\"'Josefin Sans', sans-serif\" font-weight=\"700\""
JOST = "font-family=\"Jost, sans-serif\" font-weight=\"500\""


def save(collection, slug, body):
    d = ROOT / collection
    d.mkdir(parents=True, exist_ok=True)
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600">\n' + body.strip() + "\n</svg>\n"
    (d / f"{slug}.svg").write_text(svg)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, font, size, fill, ls=0, anchor="middle", extra=""):
    # letter-spacing adds trailing space after the last glyph; nudge centered text right by half of it
    if anchor == "middle" and ls:
        x = x + ls / 2
    ls_attr = f' letter-spacing="{ls}"' if ls else ""
    return f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}" {font} font-size="{size}"{ls_attr} fill="{fill}"{extra}>{esc(s)}</text>'


def heart(cx, cy, s, fill):
    """Small solid heart centred near (cx, cy); s is the half width."""
    k = s / 16
    p = (f"M {cx:g} {cy + 18 * k:g} C {cx - 30 * k:g} {cy - 2 * k:g} {cx - 24 * k:g} {cy - 24 * k:g} {cx - 8 * k:g} {cy - 20 * k:g} "
         f"Q {cx - 2 * k:g} {cy - 18 * k:g} {cx:g} {cy - 12 * k:g} Q {cx + 2 * k:g} {cy - 18 * k:g} {cx + 8 * k:g} {cy - 20 * k:g} "
         f"C {cx + 24 * k:g} {cy - 24 * k:g} {cx + 30 * k:g} {cy - 2 * k:g} {cx:g} {cy + 18 * k:g} Z")
    return f'<path d="{p}" fill="{fill}"/>'


def star_points(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return " ".join(pts)


def hexagon(cx, cy, r):
    pts = []
    for i in range(6):
        a = math.radians(-90 + 60 * i)
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return " ".join(pts)


def frame(bg, ink, inset=30, width=2):
    return (f'<rect width="600" height="600" fill="{bg}"/>\n'
            f'<rect x="{inset}" y="{inset}" width="{600 - 2 * inset}" height="{600 - 2 * inset}" rx="4" fill="none" stroke="{ink}" stroke-width="{width}"/>')


def bee(tx, ty, scale, clip_id, body="#F2A81D", ink="#2B2118", wing="#FFFFFF", eye="#FFF6E5",
        flip=False, crown=False, antennae=True, heart_fill=None):
    """The house bumblebee. Head faces left unless flip=True."""
    sx = -scale if flip else scale
    parts = [f'<g transform="translate({tx:g} {ty:g}) scale({sx:g} {scale:g})">',
             f'<defs><clipPath id="{clip_id}"><ellipse cx="0" cy="0" rx="58" ry="40"/></clipPath></defs>',
             f'<ellipse cx="-14" cy="-44" rx="24" ry="38" transform="rotate(-25 -14 -44)" fill="{wing}" stroke="{ink}" stroke-width="5"/>',
             f'<ellipse cx="18" cy="-44" rx="22" ry="34" transform="rotate(22 18 -44)" fill="{wing}" stroke="{ink}" stroke-width="5"/>',
             f'<path d="M 56 -7 L 80 0 L 56 7 Z" fill="{ink}"/>',
             f'<ellipse cx="0" cy="0" rx="58" ry="40" fill="{body}"/>',
             f'<g clip-path="url(#{clip_id})"><rect x="-16" y="-50" width="16" height="100" fill="{ink}"/><rect x="16" y="-50" width="16" height="100" fill="{ink}"/></g>',
             f'<ellipse cx="0" cy="0" rx="58" ry="40" fill="none" stroke="{ink}" stroke-width="5"/>']
    if antennae and not crown:
        parts += [f'<path d="M -66 -22 Q -74 -48 -90 -50" fill="none" stroke="{ink}" stroke-width="4" stroke-linecap="round"/>',
                  f'<path d="M -52 -24 Q -50 -50 -36 -58" fill="none" stroke="{ink}" stroke-width="4" stroke-linecap="round"/>',
                  f'<circle cx="-90" cy="-50" r="5" fill="{ink}"/>',
                  f'<circle cx="-36" cy="-58" r="5" fill="{ink}"/>']
    parts.append(f'<circle cx="-62" cy="0" r="26" fill="{ink}"/>')
    if crown:
        parts += [f'<path d="M -82 -22 L -85 -50 L -73 -37 L -62 -56 L -51 -37 L -39 -50 L -42 -22 Z" fill="{ink}" stroke="{eye}" stroke-width="2.5" stroke-linejoin="round"/>',
                  f'<circle cx="-62" cy="-33" r="3.5" fill="{eye}"/>']
    parts += [f'<circle cx="-70" cy="-6" r="5" fill="{eye}"/>',
              f'<path d="M -78 9 Q -70 16 -62 9" fill="none" stroke="{eye}" stroke-width="3" stroke-linecap="round"/>']
    if heart_fill:
        parts.append(heart(-104, 22, 14, heart_fill))
    parts.append("</g>")
    return "\n".join(parts)


def mug(cx, top, ink, sw=5, fill="none", steam=True, heart_fill=None):
    """Line-art mug about 140 wide, 120 tall, top edge at `top`."""
    l, r = cx - 70, cx + 70
    b = top + 112
    out = [f'<g fill="none" stroke="{ink}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">',
           f'<path d="M {l} {top} L {r} {top} L {r - 12} {b - 14} Q {r - 16} {b} {r - 32} {b} L {l + 32} {b} Q {l + 16} {b} {l + 12} {b - 14} Z" fill="{fill}"/>',
           f'<path d="M {r - 2} {top + 20} Q {r + 40} {top + 20} {r + 36} {top + 52} Q {r + 32} {top + 82} {r - 8} {top + 82}"/>']
    if steam:
        for dx in (-30, 0, 30):
            out.append(f'<path d="M {cx + dx} {top - 14} q -10 -12 0 -24 t 0 -24"/>')
    out.append("</g>")
    if heart_fill:
        out.append(heart(cx - 4, top + 52, 16, heart_fill))
    return "\n".join(out)


# ---------------------------------------------------------------- text measuring (for auto-fitting type)
FONT_DIR = pathlib.Path(__file__).resolve().parents[1] / "fonts"
_FONT_FILES = {BEBAS: ("BebasNeue-Regular.ttf", None), MONO: ("DMMono-Medium.ttf", None),
               SERIF_IT: ("PlayfairDisplay-Italic[wght].ttf", 700), JOS: ("JosefinSans[wght].ttf", 700),
               JOST: ("Jost[wght].ttf", 500), CINZEL: ("Cinzel[wght].ttf", 600), DMS: ("DMSerifDisplay-Regular.ttf", None)}
_cache = {}


def _metrics(font):
    if font not in _cache:
        from fontTools.ttLib import TTFont
        name, wght = _FONT_FILES[font]
        f = TTFont(FONT_DIR / name)
        if wght and "fvar" in f:
            from fontTools.varLib import instancer
            f = instancer.instantiateVariableFont(f, {"wght": wght})
        _cache[font] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
    return _cache[font]


def measure(s, font, size, ls=0):
    cmap, hmtx, upm = _metrics(font)
    w = 0
    for ch in s:
        g = cmap.get(ord(ch))
        w += hmtx[g][0] if g else upm * 0.5
    return w * size / upm + ls * max(0, len(s) - 1)


def fit_size(s, font, size, max_w, ls=0):
    """Largest size <= `size` whose width fits in max_w."""
    while size > 10 and measure(s, font, size, ls) > max_w:
        size -= 1
    return size


def ftext(x, y, s, font, size, fill, max_w=500, ls=0, anchor="middle", extra=""):
    return text(x, y, s, font, fit_size(s, font, size, max_w, ls), fill, ls=ls, anchor=anchor, extra=extra)
