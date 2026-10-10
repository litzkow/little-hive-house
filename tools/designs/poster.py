"""Poster layout v2 for American Places and World Places.

The art fills the top 404 px (cropped from a 600x444 drawing, top edge trimmed), then a 5 px rule and a
color band. Name and subtitle sit inside the print-safe area (40 px from every edge) because the outer edge of
the paper wraps around the magnet shell.
"""
from common import save, esc, measure, fit_size, MONO, _FONT_FILES

ANTON = "font-family=\"Anton, Impact, sans-serif\""
_FONT_FILES[ANTON] = ("Anton-Regular.ttf", None)
ART_H = 404


def poster(collection, slug, name, sub, art, band, rule, namec, subc, name_max=90):
    size = name_max
    while size > 40 and measure(name, ANTON, size, 0.03 * size) > 500:
        size -= 1
    cap = 0.735 * size
    ssz = fit_size(sub, MONO, 19, 500, 4.2)
    total = cap + 18 + ssz * 0.7
    top = ART_H + 5 + (556 - ART_H - 5 - total) / 2
    ny = top + cap
    sy = ny + 18 + ssz * 0.7
    body = (f'<rect width="600" height="600" fill="{band}"/>\n'
            f'<svg x="0" y="0" width="600" height="{ART_H}" viewBox="0 0 600 444" preserveAspectRatio="xMidYMax slice">\n{art.strip()}\n</svg>\n'
            f'<rect x="0" y="{ART_H}" width="600" height="5" fill="{rule}"/>\n'
            f'<text x="{300 + 0.015 * size:.1f}" y="{ny:.1f}" text-anchor="middle" {ANTON} font-size="{size}" letter-spacing="{0.03 * size:.1f}" fill="{namec}">{esc(name)}</text>\n'
            f'<text x="302" y="{sy:.1f}" text-anchor="middle" {MONO} font-size="{ssz}" letter-spacing="4.2" fill="{subc}">{esc(sub)}</text>')
    save(collection, slug, body)
