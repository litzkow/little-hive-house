"""Seasonal decorations for the website itself (not magnets): a garland under the header, a little painted
scene in the hero, and falling particles. Writes assets/decor/<season>-*.svg. The page picks the season from
the visitor's date (see the inline script in build.py). The fall set is painted in decor_ab.py; the other
seasons live in decor_seasons.py."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent / "designs"))
sys.path.insert(0, str(pathlib.Path(__file__).parent))

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets" / "decor"
INK = "#3A2418"


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{body}</svg>'


def save(name, w, h, body):
    import decor_ab
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.svg").write_text(svg(w, h, decor_ab.compact(body)), encoding="utf-8")


def build():
    import decor_ab
    save("fall-scene", 380, 330, decor_ab.fall_scene())
    save("fall-garland", 320, 74, decor_ab.fall_garland())
    for name, body in decor_ab.fall_particles().items():
        save(name, 40, 40, body)


if __name__ == "__main__":
    build()
