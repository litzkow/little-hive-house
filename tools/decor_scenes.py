"""Writes the hero scenes from the painted decor modules (decor_ab: fall..winter, decor_cd: newyear..summer).
Run: python3 tools/decor_scenes.py   (scenes only; garlands and particles stay as they are)."""
import pathlib
import decor_ab
import decor_cd

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets" / "decor"


def svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{body}</svg>'


if __name__ == "__main__":
    for mod, names in ((decor_ab, ["fall", "halloween", "thanksgiving", "christmas", "winter"]),
                       (decor_cd, ["newyear", "valentine", "stpatricks", "spring", "summer", "july4"])):
        for n in names:
            fn = getattr(mod, f"{n}_scene", None)
            if not fn:
                print("no scene function for", n)
                continue
            (OUT / f"{n}-scene.svg").write_text(svg(380, 330, decor_ab.compact(fn())), encoding="utf-8")
            print("wrote", n)
