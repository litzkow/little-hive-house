# Little Hive House

Handmade fridge magnets and gifts. Website published with GitHub Pages from the `main` branch.

## How the site is built

- `designs/<collection>/<design>.svg` holds every magnet design (600 × 600, prints at 2 × 2 in).
- `tools/designs/*.py` generate the newer designs; `tools/catalog.py` lists the collections, titles and order.
- The website shows pre-rendered WebP copies in `assets/art/` (made by `tools/raster.py` with Playwright and the fonts in `tools/fonts/`; `build.py` runs it automatically and only redraws changed designs). The SVGs stay the print masters.
- `python3 tools/build.py` rebuilds every page (`index.html`, `shop.html`, `collections/*.html`, `photo-magnets.html`, `big-orders.html`, `404.html`).
- Shared styles and scripts live in `assets/`.

## Printing orders

- `python3 tools/frames.py` writes the photo frame styles (`assets/frames/`), used by the photo builder and the print tool.
- `python3 tools/print_sheet.py -o order.pdf places/chicago fall/cozy-season --frame polaroid --caption "Summer 2026" photo1.jpg photo2.jpg`
  makes a print-ready PDF: 12 magnets per US Letter page at 300 dpi, 2.5 in tiles (2 in face + wrap) with crop marks.
  Designs are `<collection>/<slug>`; `--frame` and `--caption` apply to the photos after them; `--copies N` repeats the order.
