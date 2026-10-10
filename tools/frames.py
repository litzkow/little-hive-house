"""Frame styles for custom photo magnets. Writes assets/frames/<id>.svg (600x600 overlay: the frame with a
transparent window where the photo shows) and assets/frames/frames.json (used by the builder and the print tool).

Coordinates follow the design canvas: 600 = the full printed square (2.5 in), the visible magnet face is the
inner ~520, so borders start well inside the 40 px wrap."""
import json
import math
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent / "designs"))
from common import heart, star_points  # noqa: E402
from gouache import maple_leaf, oak, acorn  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets" / "frames"


def rr(x, y, w, h, r):
    if r <= 0:
        return f"M {x} {y} H {x + w} V {y + h} H {x} Z"
    return (f"M {x + r} {y} H {x + w - r} A {r} {r} 0 0 1 {x + w} {y + r} V {y + h - r} A {r} {r} 0 0 1 {x + w - r} {y + h} "
            f"H {x + r} A {r} {r} 0 0 1 {x} {y + h - r} V {y + r} A {r} {r} 0 0 1 {x + r} {y} Z")


def holly_sprig(cx, cy, s, rot):
    leaf = "M 0 0 C 6 -8 14 -10 24 -6 C 20 -2 22 2 26 4 C 18 6 16 10 12 14 C 10 8 4 6 0 0 Z"
    return (f'<g transform="translate({cx} {cy}) rotate({rot}) scale({s})">'
            f'<path d="{leaf}" fill="#2F7A4A"/><path d="{leaf}" fill="#24603A" transform="scale(-1 1)"/>'
            f'<path d="M 0 0 L 22 2 M 0 0 L -22 2" stroke="#1B4A2C" stroke-width="1"/>'
            f'<circle cx="-3" cy="6" r="4.5" fill="#C2343A"/><circle cx="4" cy="8" r="4.5" fill="#D8404A"/><circle cx="0" cy="1" r="4.5" fill="#B82A30"/>'
            f'<circle cx="-4.5" cy="4.5" r="1.3" fill="#FFF" opacity=".7"/></g>')


def frames():
    F = []

    def add(fid, name, bg, win, r=0, decor="", caption=False, note=""):
        x, y, w, h = win
        body = (f'<path d="M 0 0 H 600 V 600 H 0 Z {rr(x, y, w, h, r)}" fill="{bg}" fill-rule="evenodd"/>' + decor)
        F.append({"id": fid, "name": name, "window": [x, y, w, h], "radius": r, "caption": caption, "note": note, "svg": body})

    add("none", "No border", "none", (0, 0, 600, 600), note="Your photo fills the whole magnet")
    add("classic", "Classic white", "#FFFFFF", (74, 74, 452, 452),
        decor='<path d="' + rr(74, 74, 452, 452, 0) + '" fill="none" stroke="#E8E2D6" stroke-width="2"/>')
    add("polaroid", "Instant photo", "#FBF8F2", (78, 72, 444, 384), caption=True,
        decor='<path d="' + rr(78, 72, 444, 384, 0) + '" fill="none" stroke="#E4DDD0" stroke-width="2"/>', note="Add a short caption")
    add("rounded", "Soft corners", "#FFF6E5", (80, 80, 440, 440), r=46)
    hexes = "".join(f'<polygon points="{" ".join(f"{cx + 11 * math.cos(math.radians(-90 + 60 * i)):.1f},{cy + 11 * math.sin(math.radians(-90 + 60 * i)):.1f}" for i in range(6))}" fill="{c}"/>'
                    for cx, cy, c in ((92, 92, "#F2A81D"), (110, 82, "#F9D88A"), (508, 518, "#F2A81D"), (490, 528, "#F9D88A")))
    add("honey", "Honey line", "#FFF6E5", (92, 92, 416, 416),
        decor='<path d="' + rr(80, 80, 440, 440, 6) + '" fill="none" stroke="#F2A81D" stroke-width="3"/>'
              '<path d="' + rr(86, 86, 428, 428, 4) + '" fill="none" stroke="#F2A81D" stroke-width="1.2"/>' + hexes)
    add("gallery", "Gallery black", "#1E1A18", (96, 96, 408, 408),
        decor='<path d="' + rr(88, 88, 424, 424, 0) + '" fill="none" stroke="#C9A24A" stroke-width="2"/>')
    # scalloped lace edge around the window
    sc = []
    x, y, w, h, n = 92, 92, 416, 416, 13
    step = w / n
    for side in range(4):
        for i in range(n):
            t0 = i * step + step / 2
            if side == 0:
                cx, cy = x + t0, y
            elif side == 1:
                cx, cy = x + w, y + t0
            elif side == 2:
                cx, cy = x + w - t0, y + h
            else:
                cx, cy = x, y + h - t0
            sc.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{step / 2:.1f}" fill="#F6D6DC"/>')
    add("scallop", "Pink scallop", "#F6D6DC", (102, 102, 396, 396),
        decor="".join(sc) + "".join(f'<circle cx="{cx}" cy="{cy}" r="3" fill="#E7A4B2"/>' for cx, cy in ((70, 70), (530, 70), (70, 530), (530, 530))))
    holes = "".join(f'<rect x="{x0}" y="{y0}" width="22" height="16" rx="3" fill="#F4EFE6"/>' for x0 in range(62, 540, 40) for y0 in (52, 532))
    add("film", "Film strip", "#151414", (52, 86, 496, 428), decor=holes)
    rnd = random.Random(4)
    leaves = (maple_leaf(86, 92, 30, "#E8792E", "#B9531E", rot=-30, seed=1) + maple_leaf(130, 70, 22, "#C9442E", "#8E2A1A", rot=20, seed=2)
              + oak(70, 140, 20, "#B8862E", "#7A5418", rot=-60) + acorn(120, 118, 13, rot=-20)
              + maple_leaf(514, 508, 30, "#E2A23A", "#A8701A", rot=150, seed=3) + maple_leaf(470, 532, 22, "#E8792E", "#B9531E", rot=200, seed=4)
              + oak(532, 462, 20, "#8A9A3E", "#5A6A22", rot=120))
    add("autumn", "Autumn leaves", "#FBF3E6", (84, 84, 432, 432), r=8, decor=leaves)
    holly = holly_sprig(94, 94, 1.6, -40) + holly_sprig(506, 506, 1.6, 140) + holly_sprig(506, 94, 1.1, 40) + holly_sprig(94, 506, 1.1, -140)
    add("holly", "Holly & berries", "#FBF6EE", (84, 84, 432, 432), r=8,
        decor='<path d="' + rr(76, 76, 448, 448, 12) + '" fill="none" stroke="#C2343A" stroke-width="2.5" stroke-dasharray="10 7"/>' + holly)
    hearts = "".join(heart(cx, cy, s, c) for cx, cy, s, c in ((88, 90, 18, "#E2546A"), (120, 70, 11, "#F29AA8"), (66, 124, 10, "#F29AA8"),
                                                           (512, 512, 18, "#E2546A"), (480, 532, 11, "#F29AA8"), (534, 478, 10, "#F29AA8")))
    add("hearts", "Little hearts", "#FFF0F2", (84, 84, 432, 432), r=12, decor=hearts)
    stars = "".join(f'<polygon points="{star_points(rnd.uniform(48, 552), rnd.choice([rnd.uniform(46, 80), rnd.uniform(520, 554)]), r_ := rnd.uniform(3, 7), r_ * 0.45)}" fill="#F6E2A8" opacity="{rnd.uniform(.6, 1):.2f}"/>' for _ in range(26))
    stars += "".join(f'<polygon points="{star_points(rnd.choice([rnd.uniform(46, 80), rnd.uniform(520, 554)]), rnd.uniform(80, 520), r_ := rnd.uniform(3, 6), r_ * 0.45)}" fill="#F6E2A8" opacity="{rnd.uniform(.6, 1):.2f}"/>' for _ in range(18))
    add("starry", "Starry night", "#1C2448", (88, 88, 424, 424), r=10,
        decor=stars + '<path d="' + rr(84, 84, 432, 432, 12) + '" fill="none" stroke="#F6E2A8" stroke-width="1.5"/>')
    return F


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    meta = []
    for f in frames():
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600">{f["svg"]}</svg>'
        (OUT / f'{f["id"]}.svg').write_text(svg, encoding="utf-8")
        meta.append({k: f[k] for k in ("id", "name", "window", "radius", "caption", "note")})
    (OUT / "frames.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"wrote {len(meta)} frames")
    return meta


if __name__ == "__main__":
    build()
