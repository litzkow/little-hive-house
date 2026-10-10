"""Seasonal decorations for the website itself (not magnets): a garland under the header, a little painted
scene in the hero, and falling particles. Writes assets/decor/<season>-*.svg. The page picks the season from
the visitor's date (see the inline script in build.py)."""
import math
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent / "designs"))
from gouache import (acorn, blob, corn_stalk, hay_bale, ink, maple_leaf, oak, painted_pumpkin, smooth_closed,  # noqa: E402
                     strokes, wash)
from icons import P  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets" / "decor"
INK = "#3A2418"


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{body}</svg>'


def save(name, w, h, body):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.svg").write_text(svg(w, h, body), encoding="utf-8")


def scarecrow(uid):
    """Fall hero scene, 380 x 330: a friendly scarecrow with a crow, corn stalks, a hay bale and pumpkins."""
    o = []
    o.append(f'<ellipse cx="190" cy="318" rx="180" ry="12" fill="#3A2418" opacity="0.12"/>')
    o.append(corn_stalk(52, 318, 230, 3, lean=-0.05) + corn_stalk(78, 318, 260, 4, lean=0.03) + corn_stalk(330, 318, 240, 5, lean=0.06))
    # post and crossbar
    o.append('<path d="M 186 110 L 196 110 L 198 318 L 184 318 Z" fill="#8A6038"/><path d="M 190 110 L 196 110 L 198 318 L 192 318 Z" fill="#6E4A2A"/>')
    # arms: plaid flannel sleeves along the crossbar
    o.append('<defs><pattern id="' + uid + '-plaid" width="22" height="22" patternUnits="userSpaceOnUse" patternTransform="rotate(8)">'
             '<rect width="22" height="22" fill="#B8432E"/><rect width="22" height="7" y="7" fill="#7E2A1E" opacity="0.7"/>'
             '<rect width="7" height="22" x="7" fill="#7E2A1E" opacity="0.6"/><rect width="22" height="1.5" y="3" fill="#F2C46A" opacity="0.7"/>'
             '<rect width="1.5" height="22" x="17" fill="#F2C46A" opacity="0.7"/></pattern></defs>')
    sleeves = smooth_closed([(80, 128), (150, 116), (232, 116), (302, 126), (306, 150), (232, 146), (150, 146), (80, 154)])
    o.append(f'<path d="{sleeves}" fill="url(#{uid}-plaid)"/>')
    o.append(f'<path d="M 80 140 L 302 138 L 306 150 L 232 146 L 150 146 L 80 154 Z" fill="#3A1A10" opacity="0.18"/>')
    o.append(ink(sleeves, "#5A2216", 1.8, 2, 1, 0.6))
    # straw poking out of the cuffs
    rnd = random.Random(8)
    for cx_, sgn in ((80, -1), (304, 1)):
        o.append('<g stroke-linecap="round" stroke-width="2.2">' + "".join(
            f'<path d="M {cx_} {rnd.uniform(126, 152):.1f} l {sgn * rnd.uniform(10, 24):.1f} {rnd.uniform(-10, 12):.1f}" stroke="{rnd.choice(["#E6C26A", "#D2A24A", "#F2D88A"])}"/>' for _ in range(14)) + "</g>")
    # torso: shirt + overalls with a patch
    torso = smooth_closed([(156, 120), (226, 120), (236, 200), (232, 236), (150, 236), (146, 200)])
    o.append(f'<path d="{torso}" fill="url(#{uid}-plaid)"/>')
    bib = smooth_closed([(166, 168), (216, 168), (222, 238), (160, 238)])
    o.append(wash(bib, "#4A6E9A", 3, 2, 0.8, 0.5))
    legs = "M 156 226 L 226 226 L 230 300 L 202 300 L 192 262 L 182 300 L 152 300 Z"
    o.append(wash(legs, "#3E5E88", 4, 2, 0.8, 0.5))
    o.append(strokes(f"{uid}-den", legs + " " + bib, (148, 160, 234, 302), ["#2E4A70", "#6A8AB4", "#5A7AA4"], 6, n=70, angle=-88, length=(8, 22), width=(0.8, 2), opacity=(0.25, 0.5)))
    o.append('<path d="M 166 168 L 160 122 M 216 168 L 222 122" stroke="#3E5E88" stroke-width="7" stroke-linecap="round"/>')
    o.append('<circle cx="168" cy="174" r="3.4" fill="#E2C27A"/><circle cx="214" cy="174" r="3.4" fill="#E2C27A"/>')
    o.append('<rect x="198" y="252" width="20" height="18" rx="2" fill="#D98A3A" transform="rotate(-6 208 261)"/>'
             '<path d="M 199 254 l 18 -2 M 200 268 l 18 -2" stroke="#7A3A12" stroke-width="1" stroke-dasharray="2 2"/>')
    o.append(ink(torso, "#5A2216", 1.6, 5, 1, 0.5) + ink(legs, "#22344E", 1.6, 6, 1, 0.6))
    for lx in (166, 214):
        o.append('<g stroke-linecap="round" stroke-width="2.2">' + "".join(
            f'<path d="M {lx + rnd.uniform(-12, 12):.1f} 298 l {rnd.uniform(-6, 6):.1f} {rnd.uniform(8, 16):.1f}" stroke="{rnd.choice(["#E6C26A", "#D2A24A"])}"/>' for _ in range(9)) + "</g>")
    # burlap head with a stitched smile
    head = blob(191, 86, 30, 33, 21, 0.05)
    o.append(wash(head, "#D9B98A", 7, 2, 0.8, 0.5))
    o.append(strokes(f"{uid}-burlap", head, (158, 50, 224, 122), ["#B8945E", "#F0D8AA", "#A07A48"], 9, n=60, angle=0, length=(6, 16), width=(0.4, 1.0), opacity=(0.4, 0.8)))
    o.append(strokes(f"{uid}-burlap2", head, (158, 50, 224, 122), ["#B8945E", "#A07A48"], 10, n=40, angle=-90, length=(6, 16), width=(0.4, 1.0), opacity=(0.3, 0.6)))
    o.append(ink(head, "#7A5A32", 1.6, 8, 1, 0.6))
    o.append('<circle cx="180" cy="84" r="4.6" fill="#2A1A10"/><circle cx="202" cy="84" r="4.6" fill="#2A1A10"/>'
             '<circle cx="181.5" cy="82.5" r="1.4" fill="#FFF"/><circle cx="203.5" cy="82.5" r="1.4" fill="#FFF"/>'
             '<circle cx="174" cy="96" r="5" fill="#E8836A" opacity="0.45"/><circle cx="208" cy="96" r="5" fill="#E8836A" opacity="0.45"/>')
    o.append('<path d="M 178 99 Q 191 110 204 99" stroke="#3A2418" stroke-width="2" fill="none" stroke-linecap="round"/>'
             + "".join(f'<path d="M {x} {100 + (abs(x - 191) < 8) * 4} l 0 5" stroke="#3A2418" stroke-width="1.4"/>' for x in (181, 187, 195, 201)))
    o.append('<path d="M 166 114 Q 191 124 216 114" stroke="#8A6038" stroke-width="3" fill="none"/>')
    o.append('<g stroke-linecap="round" stroke-width="2">' + "".join(
        f'<path d="M {rnd.uniform(170, 212):.1f} 118 l {rnd.uniform(-6, 6):.1f} {rnd.uniform(4, 10):.1f}" stroke="{rnd.choice(["#E6C26A", "#D2A24A"])}"/>' for _ in range(12)) + "</g>")
    # straw hat
    brim = smooth_closed([(130, 62), (170, 52), (214, 52), (254, 62), (240, 70), (191, 68), (142, 70)])
    crown = smooth_closed([(166, 58), (168, 30), (190, 22), (214, 30), (216, 58)])
    o.append(wash(crown, "#D9A84E", 11, 2, 0.6, 0.5) + wash(brim, "#E6BC62", 12, 2, 0.6, 0.5))
    o.append(strokes(f"{uid}-hat", crown + " " + brim, (128, 18, 256, 72), ["#B8862E", "#F6D88A", "#A87628"], 13, n=70, angle=-4, length=(6, 18), width=(0.4, 1.2), opacity=(0.4, 0.8)))
    o.append('<path d="M 167 50 Q 191 56 215 50 L 216 58 Q 191 64 166 58 Z" fill="#7E2A1E"/>')
    o.append(ink(crown, "#8A5A22", 1.5, 14, 1, 0.6) + ink(brim, "#8A5A22", 1.5, 15, 1, 0.6))
    o.append(maple_leaf(206, 50, 9, "#E8792E", "#B9531E", rot=25, seed=3))
    # crow perched on the right arm
    o.append('<g transform="translate(268 116)">'
             '<path d="M -14 0 Q -18 -18 -2 -24 Q 8 -30 14 -24 Q 22 -26 26 -22 L 16 -18 Q 18 -6 8 0 Z" fill="#22202A"/>'
             '<path d="M -14 0 Q -26 4 -34 2 Q -24 -4 -16 -8 Z" fill="#22202A"/><path d="M -6 -12 Q 2 -4 10 -6" stroke="#4A4858" stroke-width="2" fill="none"/>'
             '<path d="M 22 -23 l 10 2 l -10 3 Z" fill="#E2A23A"/><circle cx="14" cy="-24" r="1.8" fill="#F6E6C6"/>'
             '<path d="M -2 0 l -2 4 M 4 0 l 2 4" stroke="#E2A23A" stroke-width="1.6"/></g>')
    # hay bale and pumpkins in front
    o.append(hay_bale(f"{uid}-hb", 214, 252, 130, 62, 31))
    o.append(painted_pumpkin(f"{uid}-p1", 284, 236, 70, 44, 41))
    o.append(painted_pumpkin(f"{uid}-p2", 120, 288, 92, 62, 42))
    o.append(painted_pumpkin(f"{uid}-p3", 196, 300, 50, 34, 43, body="#F1E6D2", dark="#C9B79A", light="#FFFFFF", stem="#6B5A2E"))
    o.append(painted_pumpkin(f"{uid}-p4", 58, 304, 42, 30, 44, body="#E2A23A", dark="#B87A1E", light="#F6CE6A"))
    o.append(maple_leaf(330, 312, 10, "#C9442E", "#8E2A1A", rot=-30, seed=5) + oak(160, 312, 9, "#D98A3A", "#9A5A1E", rot=60) + acorn(248, 316, 9, rot=20))
    return "".join(o)


def fall_garland():
    """Seamless 320 x 74 tile: twine with hanging leaves and acorns."""
    o = ['<path d="M 0 10 C 80 34 240 34 320 10" stroke="#8A6A42" stroke-width="2.2" fill="none"/>',
         '<path d="M 0 10 C 80 34 240 34 320 10" stroke="#C9A878" stroke-width="0.8" fill="none" stroke-dasharray="3 3"/>']
    def y_at(x):
        t = x / 320
        return (1 - t) ** 3 * 10 + 3 * (1 - t) ** 2 * t * 34 + 3 * (1 - t) * t * t * 34 + t ** 3 * 10
    items = [(26, "maple", "#E8792E", "#B9531E"), (78, "oak", "#B8862E", "#7A5418"), (124, "acorn", None, None),
             (166, "maple", "#C9442E", "#8E2A1A"), (214, "maple", "#E2A23A", "#A8701A"), (262, "oak", "#8A9A3E", "#5A6A22"), (300, "acorn", None, None)]
    for k, (x, kind, c, d) in enumerate(items):
        y = y_at(x)
        if kind == "maple":
            o.append(f'<path d="M {x} {y} l 0 8" stroke="#8A6A42" stroke-width="1"/>' + maple_leaf(x, y + 22, 14, c, d, rot=(-1) ** k * 12 + 180, seed=k))
        elif kind == "oak":
            o.append(f'<path d="M {x} {y} l 0 6" stroke="#8A6A42" stroke-width="1"/>' + oak(x, y + 22, 14, c, d, rot=(-1) ** k * 10 + 180))
        else:
            o.append(f'<path d="M {x} {y} l 0 6" stroke="#8A6A42" stroke-width="1"/>' + acorn(x, y + 14, 11, rot=180 + (-1) ** k * 8))
    return "".join(o)


def particles_fall():
    for i, (c, d) in enumerate((("#E8792E", "#B9531E"), ("#C9442E", "#8E2A1A"), ("#E2A23A", "#A8701A"))):
        save(f"fall-leaf{i + 1}", 40, 40, maple_leaf(20, 20, 15, c, d, seed=i))
    save("fall-leaf4", 40, 40, oak(20, 18, 15, "#B8862E", "#7A5418", rot=20))


def build():
    save("fall-scene", 380, 330, scarecrow("sc"))
    save("fall-garland", 320, 74, fall_garland())
    particles_fall()


if __name__ == "__main__":
    build()
