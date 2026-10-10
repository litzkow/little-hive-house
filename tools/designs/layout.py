"""Composition helpers for the type-led magnets: vertical stacking inside the print-safe area,
decorative frames, background textures and fitted text lines.

Print-safe: the paper wraps around the magnet edge, so text and key art stay inside 60..540.
"""
import math
import random

from common import BEBAS, CINZEL, DMS, JOS, JOST, MONO, SERIF_IT, esc, fit_size, measure

SAFE_L, SAFE_R, SAFE_T, SAFE_B = 60, 540, 60, 540
ASC = {BEBAS: 0.70, SERIF_IT: 0.80, MONO: 0.70, JOS: 0.70, JOST: 0.70, CINZEL: 0.70, DMS: 0.72}
DESC = {SERIF_IT: 0.20, JOST: 0.18, JOS: 0.12, DMS: 0.20}


class T:
    """A text line: fits itself to max_w, knows its height."""

    def __init__(self, s, font, size, fill, ls=0, max_w=430, weight=None, opacity=None):
        self.s, self.font, self.fill, self.ls = s, font, fill, ls
        self.size = fit_size(s, font, size, max_w, ls)
        self.h = ASC.get(font, 0.7) * self.size
        if font == SERIF_IT:
            self.desc = 0.26 * self.size          # italic f, z and friends dip below the baseline
        else:
            self.desc = DESC.get(font, 0) * self.size if any(c in s for c in "gjpqy,;()") else 0
        self.opacity = opacity

    def svg(self, y_top):
        x = 300 + (self.ls / 2 if self.ls else 0)
        ls = f' letter-spacing="{self.ls}"' if self.ls else ""
        op = f' opacity="{self.opacity}"' if self.opacity is not None else ""
        return (f'<text x="{x:g}" y="{y_top + self.h:.1f}" text-anchor="middle" {self.font} font-size="{self.size}"{ls} '
                f'fill="{self.fill}"{op}>{esc(self.s)}</text>')

    def width(self):
        return measure(self.s, self.font, self.size, self.ls)


class Art:
    """A block of art drawn by fn(y_top) with a known height."""

    def __init__(self, h, fn):
        self.h, self.fn, self.desc = h, fn, 0

    def svg(self, y_top):
        return self.fn(y_top)


class Gap:
    def __init__(self, h):
        self.h, self.desc = h, 0

    def svg(self, y_top):
        return ""


def stack(items, top=SAFE_T, bottom=SAFE_B, shift=0):
    """Center the items vertically between top and bottom."""
    total = sum(i.h for i in items) + sum(i.desc for i in items[:-1])
    y = top + (bottom - top - total) / 2 + shift
    out = []
    for i in items:
        out.append(i.svg(y))
        y += i.h + i.desc
    return "\n".join(o for o in out if o)


def ruled_label(s, fill, size=17, ls=6, line=None, gap=16, line_w=46):
    """Small caps label flanked by two short rules; returns an Art block."""
    t = T(s, MONO, size, fill, ls=ls, max_w=360)
    w = t.width()
    lc = line or fill

    def fn(y):
        mid = y + t.h / 2
        x0 = 300 - w / 2 - gap
        x1 = 300 + w / 2 + gap
        return (t.svg(y) + f'<line x1="{x0 - line_w:.1f}" y1="{mid:.1f}" x2="{x0:.1f}" y2="{mid:.1f}" stroke="{lc}" stroke-width="2"/>'
                f'<line x1="{x1:.1f}" y1="{mid:.1f}" x2="{x1 + line_w:.1f}" y2="{mid:.1f}" stroke="{lc}" stroke-width="2"/>')
    return Art(t.h, fn)


def frame(color, inset=44, double=True, corners=True, sw=2):
    out = [f'<rect x="{inset}" y="{inset}" width="{600 - 2 * inset}" height="{600 - 2 * inset}" rx="3" fill="none" stroke="{color}" stroke-width="{sw}"/>']
    if double:
        i2 = inset + 7
        out.append(f'<rect x="{i2}" y="{i2}" width="{600 - 2 * i2}" height="{600 - 2 * i2}" rx="2" fill="none" stroke="{color}" stroke-width="1" opacity="0.7"/>')
    if corners:
        for cx in (inset, 600 - inset):
            for cy in (inset, 600 - inset):
                out.append(f'<rect x="{cx - 5}" y="{cy - 5}" width="10" height="10" transform="rotate(45 {cx} {cy})" fill="{color}"/>')
    return "\n".join(out)


def speckle(color, n=90, seed=1, r=(1.2, 2.6), opacity=0.35, avoid=None):
    rnd = random.Random(seed)
    dots = []
    while len(dots) < n:
        x, y = rnd.uniform(8, 592), rnd.uniform(8, 592)
        if avoid and avoid[0] < x < avoid[2] and avoid[1] < y < avoid[3]:
            continue
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(*r):.1f}"/>')
    return f'<g fill="{color}" opacity="{opacity}">' + "".join(dots) + "</g>"


def scatter(shape_fn, n, seed, box=(10, 10, 590, 590), avoid=None, min_d=60):
    """Place n copies of shape_fn(x, y, rot, k) without overlapping each other or the `avoid` box."""
    rnd = random.Random(seed)
    pts, tries = [], 0
    while len(pts) < n and tries < 5000:
        tries += 1
        x, y = rnd.uniform(box[0], box[2]), rnd.uniform(box[1], box[3])
        if avoid and avoid[0] < x < avoid[2] and avoid[1] < y < avoid[3]:
            continue
        if any(math.hypot(x - a, y - b) < min_d for a, b in pts):
            continue
        pts.append((x, y))
    return "".join(shape_fn(x, y, rnd.uniform(-40, 40), k) for k, (x, y) in enumerate(pts))


def stripes_bg(c1, c2, w=24, angle=0):
    n = int(900 / w) + 2
    rects = "".join(f'<rect x="{-150 + i * 2 * w}" y="-150" width="{w}" height="900" fill="{c2}"/>' for i in range(n))
    return f'<rect width="600" height="600" fill="{c1}"/><g transform="rotate({angle} 300 300)">{rects}</g>'


def arc_text(s, cx, cy, r, font, size, fill, ls=0, uid="arc", top=True):
    """Text on an arc (top=True: reads along the top of a circle)."""
    if top:
        d = f"M {cx - r} {cy} A {r} {r} 0 0 1 {cx + r} {cy}"
    else:
        d = f"M {cx - r} {cy} A {r} {r} 0 0 0 {cx + r} {cy}"
    lsa = f' letter-spacing="{ls}"' if ls else ""
    return (f'<defs><path id="{uid}" d="{d}" fill="none"/></defs>'
            f'<text {font} font-size="{size}"{lsa} fill="{fill}" text-anchor="middle"><textPath href="#{uid}" startOffset="50%">{esc(s)}</textPath></text>')
