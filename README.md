# Little Hive House

Handmade fridge magnets and gifts. Website published with GitHub Pages from the `main` branch.

## How the site is built

- `designs/<collection>/<design>.svg` holds every magnet design (600 × 600, prints at 2 × 2 in).
- `tools/designs/*.py` generate the newer designs; `tools/catalog.py` lists the collections, titles and order.
- The website shows pre-rendered WebP copies in `assets/art/` (made by `tools/raster.py` with Playwright and the fonts in `tools/fonts/`; `build.py` runs it automatically and only redraws changed designs). The SVGs stay the print masters.
- `python3 tools/build.py` rebuilds every page (`index.html`, `shop.html`, `collections/*.html`, `photo-magnets.html`, `big-orders.html`, `404.html`).
- Shared styles and scripts live in `assets/`.
