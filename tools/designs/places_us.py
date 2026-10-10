"""American Places: the original poster illustrations (art/places/*.svg) in the print-safe poster layout."""
import json
import pathlib
from poster import poster

ART = pathlib.Path(__file__).parent / "art" / "places"


def build_places():
    meta = json.loads((ART / "meta.json").read_text(encoding="utf-8"))
    for slug, m in meta.items():
        poster("places", slug, m["name"], m["sub"], (ART / f"{slug}.svg").read_text(encoding="utf-8"),
               m["band"], m["rule"], m["namec"], m["subc"])


if __name__ == "__main__":
    build_places()
