"""Ink Cities, second edition: the line drawings in art/ink/ with engraved hatching, a print-safe frame,
and each city's coordinates under its name."""
import pathlib
import re

from common import DMS, MONO, esc, fit_size, measure, save

INK, PAPER = "#1A1A1A", "#F4F0E8"
ART = pathlib.Path(__file__).parent / "art" / "ink"

CITIES = {
    "new-york": ("New York", "40.7128° N · 74.0060° W"),
    "paris": ("Paris", "48.8566° N · 2.3522° E"),
    "london": ("London", "51.5072° N · 0.1276° W"),
    "san-francisco": ("San Francisco", "37.7749° N · 122.4194° W"),
    "atlanta": ("Atlanta", "33.7490° N · 84.3880° W"),
    "rio": ("Rio de Janeiro", "22.9068° S · 43.1729° W"),
    "chicago": ("Chicago", "41.8781° N · 87.6298° W"),
    "seattle": ("Seattle", "47.6062° N · 122.3321° W"),
    "miami": ("Miami", "25.7617° N · 80.1918° W"),
    "nashville": ("Nashville", "36.1627° N · 86.7816° W"),
    "boston": ("Boston", "42.3601° N · 71.0589° W"),
    "rome": ("Rome", "41.9028° N · 12.4964° E"),
}


def hatch_rect(x, y, w, h, uid, spacing=7):
    """Diagonal engraving lines over the right part of a building."""
    hx = x + w * 0.62
    hw = w * 0.38
    lines = "".join(f'<line x1="{hx + i:.1f}" y1="{y + h + 4:.1f}" x2="{hx + i + h + 8:.1f}" y2="{y - 4:.1f}"/>'
                    for i in range(-int(h) - 10, int(hw) + 10, spacing))
    return (f'<clipPath id="{uid}"><rect x="{hx:.1f}" y="{y + 2:.1f}" width="{hw - 2:.1f}" height="{h - 2:.1f}"/></clipPath>'
            f'<g clip-path="url(#{uid})" stroke="{INK}" stroke-width="1.1" opacity="0.8">{lines}</g>')


def hatch_circle(cx, cy, r, uid, spacing=6):
    lines = "".join(f'<line x1="{cx - r:.1f}" y1="{y:.1f}" x2="{cx + r:.1f}" y2="{y:.1f}"/>'
                    for y in [cy - r + spacing * k for k in range(1, int(2 * r / spacing))])
    return (f'<clipPath id="{uid}"><circle cx="{cx}" cy="{cy}" r="{r - 3}"/></clipPath>'
            f'<g clip-path="url(#{uid})" stroke="{INK}" stroke-width="1.1" opacity="0.7">{lines}</g>')


def engrave(art, slug):
    extra = []
    bold = art.split("</g>", 1)[0]
    for k, m in enumerate(re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', bold)):
        x, y, w, h = map(float, m.groups())
        if h >= 40 and w >= 30 and y + h >= 400:
            extra.append(hatch_rect(x, y, w, h, f"{slug}-h{k}"))
    for k, m in enumerate(re.finditer(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"', bold)):
        cx, cy, r = map(float, m.groups())
        if 14 <= r <= 40:
            extra.append(hatch_circle(cx, cy, r, f"{slug}-c{k}", spacing=6 if r > 24 else 4.5))
    return "\n".join(extra)


def ground(y=420):
    ticks = "".join(f'<line x1="{x}" y1="{y + 5}" x2="{x - 7}" y2="{y + 13}"/>' for x in range(84, 528, 11))
    return f'<g stroke="{INK}" stroke-width="1.1" opacity="0.55">{ticks}</g>'


def build_ink():
    for slug, (name, coords) in CITIES.items():
        art = (ART / f"{slug}.svg").read_text(encoding="utf-8")
        size = fit_size(name, DMS, 66, 420)
        csz = fit_size(coords, MONO, 15, 380, 3)
        w = measure(coords, MONO, csz, 3)
        body = f"""
<rect width="600" height="600" fill="{PAPER}"/>
<rect x="40" y="40" width="520" height="520" rx="3" fill="none" stroke="{INK}" stroke-width="2.5"/>
<rect x="48" y="48" width="504" height="504" rx="2" fill="none" stroke="{INK}" stroke-width="1"/>
{engrave(art, slug)}
{art}
<line x1="66" y1="420" x2="534" y2="420" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>
{ground()}
<text x="300" y="{492 if size >= 60 else 490}" text-anchor="middle" {DMS} font-size="{size}" fill="{INK}">{esc(name)}</text>
<text x="301.5" y="524" text-anchor="middle" {MONO} font-size="{csz}" letter-spacing="3" fill="{INK}">{esc(coords)}</text>
<g stroke="{INK}" stroke-width="1.5"><line x1="{300 - w / 2 - 44:.1f}" y1="519" x2="{300 - w / 2 - 14:.1f}" y2="519"/><line x1="{300 + w / 2 + 14:.1f}" y1="519" x2="{300 + w / 2 + 44:.1f}" y2="519"/></g>
"""
        save("ink-cities", slug, body)


if __name__ == "__main__":
    print("legacy: Ink Cities are built by ink_engraved_*.py and City Sketches by ink_cities_fine.py / ink_cities_new.py")
