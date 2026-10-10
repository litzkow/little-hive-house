"""Builds the Little Hive House site from designs/ and tools/catalog.py.

Run from anywhere:  python3 tools/build.py
Writes index.html, shop.html, photo-magnets.html, big-orders.html, 404.html and collections/*.html.
"""
import html
import pathlib
import re

import datetime

from catalog import BUNDLE, COLLECTIONS, FEATURED, GIFTS, PRICE, SEASONS, VOLUME, title_for

ROOT = pathlib.Path(__file__).resolve().parents[1]
DESIGNS = ROOT / "designs"
VERSION = "4"
E = html.escape

FONTS = ("https://fonts.googleapis.com/css2?family=Anton&family=Bebas+Neue&family=Cinzel:wght@600"
         "&family=DM+Mono:wght@500&family=DM+Serif+Display&family=Josefin+Sans:wght@600;700"
         "&family=Jost:wght@400;500;600&family=Playfair+Display:ital,wght@1,700&display=swap")

import raster  # noqa: E402
raster.main()

BY_SLUG = {c["slug"]: c for c in COLLECTIONS}
CUR = ' aria-current="page"'
TOTAL = sum(len(c["order"]) for c in COLLECTIONS)


class Page:
    """Keeps SVG ids unique across one page (several designs use clip paths)."""

    def __init__(self, prefix):
        self.p = prefix
        self.n = 0

    def svg(self, col, slug, cls="mag"):
        """Designs are shown as pre-rendered WebP (tools/raster.py); the SVGs stay the print masters."""
        self.n += 1
        lazy = ' loading="lazy"' if self.n > 6 else ""
        return (f'<img class="{cls}" src="{self.p}assets/art/{col}/{slug}.webp" width="600" height="600" alt=""'
                f'{lazy} decoding="async">')


LOGO = """<svg viewBox="138 8 124 118" aria-hidden="true">
        <polygon class="lg-honey" points="200,14 217.32,24 217.32,44 200,54 182.68,44 182.68,24"/>
        <polygon class="lg-honey" points="180.95,47 198.27,57 198.27,77 180.95,87 163.63,77 163.63,57"/>
        <polygon class="lg-soft" points="219.05,47 236.37,57 236.37,77 219.05,87 201.73,77 201.73,57"/>
        <polygon class="lg-honey" points="161.9,80 179.22,90 179.22,110 161.9,120 144.58,110 144.58,90"/>
        <polygon class="lg-ink" points="200,80 217.32,90 217.32,110 200,120 182.68,110 182.68,90"/>
        <polygon class="lg-honey" points="238.1,80 255.42,90 255.42,110 238.1,120 220.78,110 220.78,90"/>
        <path class="lg-bg" d="M 194 115 L 194 104 A 6 6 0 0 1 206 104 L 206 115 Z"/>
      </svg>"""


def seal(idp):
    return f"""<svg viewBox="80 6 240 240" role="img" aria-label="Little Hive House seal">
          <defs>
            <path id="{idp}-top" d="M 116 126 A 84 84 0 0 1 284 126" fill="none"/>
            <path id="{idp}-bot" d="M 106 126 A 94 94 0 0 0 294 126" fill="none"/>
          </defs>
          <circle class="lg-line" cx="200" cy="126" r="110" stroke-width="3"/>
          <circle class="lg-line" cx="200" cy="126" r="104" stroke-width="1"/>
          <circle class="lg-line" cx="200" cy="126" r="74" stroke-width="1.5"/>
          <text class="lg-ink" font-family="'Josefin Sans', sans-serif" font-weight="700" font-size="16" letter-spacing="4" text-anchor="middle"><textPath href="#{idp}-top" startOffset="50%">LITTLE HIVE HOUSE</textPath></text>
          <text class="lg-ink" font-family="'Josefin Sans', sans-serif" font-weight="700" font-size="11" letter-spacing="3" text-anchor="middle"><textPath href="#{idp}-bot" startOffset="50%">HANDMADE GIFTS · EST. 2026</textPath></text>
          <circle class="lg-honey" cx="111" cy="126" r="3.5"/>
          <circle class="lg-honey" cx="289" cy="126" r="3.5"/>
          <g transform="translate(200 126) scale(0.8) translate(-200 -75)">
            <polygon class="lg-honey" points="200,14 217.32,24 217.32,44 200,54 182.68,44 182.68,24"/>
            <polygon class="lg-honey" points="180.95,47 198.27,57 198.27,77 180.95,87 163.63,77 163.63,57"/>
            <polygon class="lg-soft" points="219.05,47 236.37,57 236.37,77 219.05,87 201.73,77 201.73,57"/>
            <polygon class="lg-honey" points="161.9,80 179.22,90 179.22,110 161.9,120 144.58,110 144.58,90"/>
            <polygon class="lg-ink" points="200,80 217.32,90 217.32,110 200,120 182.68,110 182.68,90"/>
            <polygon class="lg-honey" points="238.1,80 255.42,90 255.42,110 238.1,120 220.78,110 220.78,90"/>
            <path class="lg-bg" d="M 194 115 L 194 104 A 6 6 0 0 1 206 104 L 206 115 Z"/>
          </g>
        </svg>"""


NAV = [("shop.html", "Shop all", "shop"), ("collections/index.html", "Collections", "collections"),
       ("photo-magnets.html", "Photo magnets", "photo"), ("big-orders.html", "Big orders", "big")]


def head(pg, title, desc, path):
    full = "Little Hive House" if title is None else f"{title} · Little Hive House"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(full)}</title>
<meta name="description" content="{E(desc)}">
<meta name="theme-color" content="#FFF6E5">
<link rel="canonical" href="https://littlehivehouse.com/{path}">
<meta property="og:title" content="{E(full)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<link rel="icon" href="{pg.p}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{pg.p}assets/site.css?v={VERSION}">
</head>
<body>
"""


def header(pg, active):
    links = "\n".join(
        f'      <a href="{pg.p}{href}"{CUR if key == active else ""}>{label}</a>'
        for href, label, key in NAV)
    mobile = "\n".join(f'      <a href="{pg.p}{href}">{label}</a>' for href, label, _ in NAV)
    subs = "\n".join(f'      <a class="sub" href="{pg.p}collections/{c["slug"]}.html">{E(c["name"])}</a>' for c in COLLECTIONS)
    return f"""<a class="visually-hidden" href="#main">Skip to content</a>
<div class="strip"><span>Free US shipping on orders over $35</span><span class="dot" aria-hidden="true">·</span><span>Handmade in small batches</span></div>

<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{pg.p}index.html" aria-label="Little Hive House home">
      {LOGO}
      <span>Little Hive House</span>
    </a>
    <nav class="nav" aria-label="Main">
{links}
      <button type="button" class="menu-btn" id="menu-btn" aria-expanded="false" aria-controls="mobile-menu">
        <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M2 4h14M2 9h14M2 14h14"/></svg><span class="menu-label">Menu</span>
      </button>
      <button type="button" class="cart-btn" data-open-cart aria-haspopup="dialog">
        Cart <span class="cart-count" data-cart-count>0</span>
      </button>
    </nav>
  </div>
  <div class="mobile-menu" id="mobile-menu" hidden>
    <nav class="wrap" aria-label="Mobile">
{mobile}
{subs}
    </nav>
  </div>
</header>
"""


def tabs_links(pg, active):
    items = [f'<a class="tab" href="{pg.p}shop.html"{CUR if active == "all" else ""}>All <small>{TOTAL}</small></a>']
    for c in COLLECTIONS:
        cur = ' aria-current="page"' if c["slug"] == active else ""
        items.append(f'<a class="tab" href="{pg.p}collections/{c["slug"]}.html"{cur}>{E(c["name"])} <small>{len(c["order"])}</small></a>')
    return f"""<div class="tabs-bar">
  <nav class="wrap tabs" aria-label="Collections">
    {chr(10).join("    " + i for i in items).strip()}
  </nav>
</div>
"""


def tabs_filters():
    items = [f'<button type="button" class="tab" data-filter="all" aria-pressed="true">All <small>{TOTAL}</small></button>']
    for c in COLLECTIONS:
        items.append(f'<button type="button" class="tab" data-filter="{c["slug"]}" aria-pressed="false">{E(c["name"])} <small>{len(c["order"])}</small></button>')
    return f"""<div class="tabs-bar">
  <div class="wrap tabs" role="group" aria-label="Filter by collection">
    {chr(10).join("    " + i for i in items).strip()}
  </div>
</div>
"""


def product(pg, col, slug, show_col=True):
    t = title_for(col, slug)
    href = f'{pg.p}collections/{col["slug"]}.html'
    meta = (f'<p class="col"><a href="{href}">{E(col["name"])}</a></p>' if show_col
            else '<p class="spec">2 × 2 in magnet</p>')
    search = E(f'{t} {col["name"]} {col["tag"]}'.lower())
    return f"""<li class="product" data-collection="{col["slug"]}" data-search="{search}">
  <button type="button" class="product-art" data-view aria-label="See {E(t)} larger">{pg.svg(col["slug"], slug)}</button>
  <div class="product-info">
    <h3>{E(t)}</h3>
    {meta}
    <p class="price">${PRICE}</p>
  </div>
  <button type="button" class="btn btn-small" data-add="{col["slug"]}/{slug}" data-name="{E(t)}" data-collection="{E(col["name"])}" data-href="{href}">Add to cart</button>
</li>"""


def col_card(pg, col):
    fan = "".join(f'<span class="m">{pg.svg(col["slug"], s, cls="fan-svg")}</span>' for s in col["order"][:3])
    return f"""<li><a class="col-card" href="{pg.p}collections/{col["slug"]}.html">
  <div class="fan" aria-hidden="true">{fan}</div>
  <div class="col-body">
    <h3>{E(col["name"])}</h3>
    <p>{E(col["tag"])} · {len(col["order"])} designs</p>
    <span class="more">Shop the collection →</span>
  </div>
</a></li>"""


def deal():
    return f'<span class="deal">Any {BUNDLE[0]} designs for ${BUNDLE[1]}</span>'


def vol_badge():
    n, pct = VOLUME[-1]
    return f'<span class="deal alt">{pct}% off {n}+ magnets</span>'


def footer(pg):
    cols = "\n".join(f'          <li><a href="{pg.p}collections/{c["slug"]}.html">{E(c["name"])}</a></li>' for c in COLLECTIONS)
    return f"""<footer>
  <div class="wrap">
    <div class="foot-cols">
      <div class="brandcol">
        {LOGO.replace('aria-hidden="true"', 'aria-hidden="true" class="foot-logo"')}
        <p>Handmade fridge magnets and little gifts, printed and pressed by hand in small batches.</p>
      </div>
      <div>
        <h2>Shop</h2>
        <ul>
          <li><a href="{pg.p}shop.html">All designs</a></li>
          <li><a href="{pg.p}collections/index.html">Collections</a></li>
          <li><a href="{pg.p}photo-magnets.html">Photo magnets</a></li>
          <li><a href="{pg.p}big-orders.html">Big orders</a></li>
        </ul>
      </div>
      <div>
        <h2>Collections</h2>
        <ul>
{cols}
        </ul>
      </div>
      <div>
        <h2>Help</h2>
        <ul>
          <li><a href="mailto:support@littlehivehouse.com">support@littlehivehouse.com</a></li>
          <li><a href="{pg.p}big-orders.html#faq">Shipping &amp; orders</a></li>
          <li><a href="{pg.p}index.html#about">About us</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span>© 2026 Little Hive House</span>
      <span>Shipping $4.95 · free on US orders over $35</span>
    </div>
  </div>
</footer>
"""


def chrome_end(pg, extra_js=()):
    scripts = "\n".join(f'<script src="{pg.p}assets/{s}?v={VERSION}"></script>' for s in ("site.js",) + tuple(extra_js))
    return f"""
<div class="scrim" id="scrim" hidden></div>
<aside class="drawer" id="drawer" role="dialog" aria-modal="true" aria-labelledby="cart-title" hidden>
  <div class="drawer-head">
    <h2 id="cart-title">Your cart</h2>
    <button type="button" class="icon-btn" id="close-cart" aria-label="Close cart">
      <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 3l12 12M15 3L3 15"/></svg>
    </button>
  </div>
  <ul class="lines" id="lines"></ul>
  <div class="empty-cart" id="empty-cart">
    <p>Your cart is empty.</p>
    <a class="btn btn-small" href="{pg.p}shop.html" id="empty-shop">Shop all designs</a>
  </div>
  <div class="totals" id="totals" hidden>
    <div><span>Subtotal</span><span id="t-sub">$0</span></div>
    <div class="discount" id="t-disc-row" hidden><span>Any {BUNDLE[0]} designs for ${BUNDLE[1]}</span><span id="t-disc">−$0</span></div>
    <div class="discount" id="t-vol-row" hidden><span id="t-vol-label">Big order discount</span><span id="t-vol">−$0</span></div>
    <div><span>Shipping</span><span id="t-ship">$4.95</span></div>
    <div class="grand"><span>Total</span><span id="t-total">$0</span></div>
    <p class="ship-note" id="ship-note"></p>
    <p class="ship-note" id="vol-note" hidden></p>
    <button type="button" class="btn btn-honey" id="checkout" disabled>Checkout opens soon</button>
  </div>
</aside>

<dialog class="qv" id="quick-view" aria-labelledby="qv-title">
  <div class="qv-grid">
    <div class="qv-art" id="qv-art"></div>
    <div class="qv-info">
      <button type="button" class="icon-btn qv-close" id="qv-close" aria-label="Close">
        <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 3l12 12M15 3L3 15"/></svg>
      </button>
      <a class="eyebrow" id="qv-col" href="#">Collection</a>
      <h2 id="qv-title">Magnet</h2>
      <p class="price">${PRICE}</p>
      <ul>
        <li>2 × 2 inch square magnet with rounded corners</li>
        <li>Glossy, scratch-resistant front and a strong magnet back</li>
        <li>Printed, pressed and packed by hand</li>
        <li>{deal().replace('<span class="deal">', '').replace('</span>', '')}, mix any collections</li>
      </ul>
      <button type="button" class="btn btn-honey" id="qv-add">Add to cart</button>
    </div>
  </div>
</dialog>

<div class="toast" id="toast" role="status" aria-live="polite" hidden></div>
{scripts}
</body>
</html>
"""


def write(path, content):
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")


def in_season(md, start, end):
    return start <= md <= end if start <= end else (md >= start or md <= end)


def contrast_text(bg, a, b):
    def lum(h):
        h = h.lstrip("#")
        r, g, bb = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(bb)
    def ratio(x, y):
        l1, l2 = sorted((lum(x), lum(y)), reverse=True)
        return (l1 + 0.05) / (l2 + 0.05)
    return a if ratio(bg, a) >= ratio(bg, b) else b


def spotlight(pg, season, sid):
    start, end, title, eyebrow, blurb, colslug, picks, (bg, fg, acc) = season
    col = BY_SLUG[colslug]
    items = "\n".join(product(pg, BY_SLUG[c], s) for c, s in picks)
    btn_fg = contrast_text(acc, bg, fg)
    return f"""<section class="spot" id="spotlight" data-season="{start}_{end}" style="--spot-bg:{bg};--spot-fg:{fg};--spot-acc:{acc};--spot-btn:{btn_fg}" aria-labelledby="{sid}">
  <div class="wrap spot-grid">
    <div class="spot-copy">
      <p class="eyebrow">In season now · {E(eyebrow)}</p>
      <h2 id="{sid}">{E(title)}</h2>
      <p>{E(blurb)}</p>
      <a class="btn spot-btn" href="{pg.p}collections/{colslug}.html">Shop {E(col["name"])}</a>
    </div>
    <ul class="products spot-products">
{items}
    </ul>
  </div>
</section>"""


def spotlight_block(pg):
    today = datetime.date.today().strftime("%m-%d")
    current = next(se for se in SEASONS if in_season(today, se[0], se[1]))
    out = [spotlight(pg, current, "spot-now")]
    for k, se in enumerate(SEASONS):
        out.append(f'<template data-start="{se[0]}" data-end="{se[1]}">{spotlight(pg, se, f"spot-{k}")}</template>')
    return "\n".join(out)


def gift_cards(pg):
    return "\n".join(f'''        <li><a class="gift" href="{pg.p}{href}"><strong>{E(t)}</strong><span>{E(line)}</span><span class="more">Shop the gift →</span></a></li>'''
                     for t, line, href in GIFTS)


# ---------------------------------------------------------------- pages
def page_home():
    pg = Page("")
    cards = "\n".join(col_card(pg, c) for c in COLLECTIONS)
    feat = "\n".join(product(pg, BY_SLUG[c], s) for c, s in FEATURED)
    body = f"""{header(pg, "home")}
<main id="main">
  <section class="hero">
    <div class="wrap hero-grid">
      <div>
        <p class="eyebrow">Handmade gifts &amp; paper goods</p>
        <h1>Little things for the fridge, <em>made by hand.</em></h1>
        <p class="lede">{TOTAL} original magnet designs in {len(COLLECTIONS)} collections, plus custom magnets made from your own photos. Each one is printed, pressed and packed in our little house.</p>
        <div class="hero-actions">
          <a class="btn" href="shop.html">Shop all designs</a>
          <a class="btn btn-ghost" href="photo-magnets.html">Make photo magnets</a>
        </div>
      </div>
      <div class="seal">
        {seal("hero")}
      </div>
    </div>
  </section>

{spotlight_block(pg)}
{tabs_links(pg, None)}
  <section id="collections">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="eyebrow">Shop by collection</p>
          <h2>Find your kind of magnet</h2>
        </div>
        <p>Travel posters, black and white skylines, seasonal favorites, star signs, birth flowers and more. {deal()} {vol_badge()}</p>
      </div>
      <ul class="col-grid">
{cards}
      </ul>
    </div>
  </section>

  <section class="tight">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="eyebrow">Fresh from the hive</p>
          <h2>A few of our favorites</h2>
        </div>
        <a class="btn btn-ghost btn-small" href="shop.html">See all {TOTAL} designs</a>
      </div>
      <div class="fridge">
        <ul class="products four">
{feat}
        </ul>
      </div>
    </div>
  </section>

  <section class="tight">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="eyebrow">Gift guide</p>
          <h2>Not sure what to get?</h2>
        </div>
        <p>Small enough for a card, sweet enough to keep for years.</p>
      </div>
      <ul class="gift-grid">
{gift_cards(pg)}
      </ul>
    </div>
  </section>

  <section class="tight">
    <div class="wrap">
      <div class="band honey">
        <div>
          <p class="eyebrow">Custom</p>
          <h2>Your photos, on the fridge</h2>
          <p>Upload your favorite pictures and we turn them into a set of glossy 2 × 2 inch magnets. Packs of 4 to 50, and you can mix them with any of our designs.</p>
          <div class="actions"><a class="btn" href="photo-magnets.html">Make photo magnets</a></div>
        </div>
        <div class="band-art" aria-hidden="true">{photo_tiles()}</div>
      </div>
    </div>
  </section>

  <section class="tight">
    <div class="wrap">
      <div class="band dark">
        <div>
          <p class="eyebrow">Big orders</p>
          <h2>Weddings, businesses and parties</h2>
          <p>Favors with your names and date, magnets with your logo, a photo for every guest. We design it, you approve it, we press every piece by hand.</p>
          <div class="actions"><a class="btn" href="big-orders.html">See packages</a></div>
        </div>
        <ul class="occasions">
          <li><strong>Weddings</strong><span>From 25 magnets</span></li>
          <li><strong>Business</strong><span>From 50 magnets</span></li>
          <li><strong>Parties</strong><span>From 20 magnets</span></li>
          <li><strong>Teams</strong><span>From 12 magnets</span></li>
        </ul>
      </div>
    </div>
  </section>

  <section class="about" id="about">
    <div class="wrap about-grid">
      <div>
        <p class="eyebrow">About us</p>
        <h2 style="font-size:clamp(30px,4vw,44px);margin-top:10px">A little house that works like a hive</h2>
        <p>Little Hive House is a husband-and-wife studio near Atlanta, Georgia, with Brazilian roots. We draw every design ourselves, then print, press and pack each magnet at home, one small batch at a time.</p>
        <p>We started with the places we love and kept going: skylines, stars, flowers, bees and the little words that make a kitchen feel like home.</p>
      </div>
      <ul class="values">
        <li><strong>Made by hand</strong><span>Printed, pressed and packed by us.</span></li>
        <li><strong>Drawn in house</strong><span>Every design is our own artwork.</span></li>
        <li><strong>2 × 2 inches</strong><span>Strong magnet backs, glossy fronts.</span></li>
        <li><strong>Gift ready</strong><span>Packed in kraft boxes with our seal.</span></li>
      </ul>
    </div>
  </section>
</main>
{footer(pg)}"""
    write("index.html", head(pg, None, f"Handmade fridge magnets: {TOTAL} original designs in {len(COLLECTIONS)} collections, plus custom photo magnets and big orders for weddings and businesses.", "") + body + chrome_end(pg))


def photo_tiles():
    tones = [("#F6CBA4", "#EE8A4E"), ("#C9DDE8", "#5C8FB0"), ("#DCE3D3", "#6E8B62"),
             ("#F3D9D3", "#C2706A"), ("#F9D88A", "#C98B2E"), ("#E7E2D8", "#7A6A58")]
    out = []
    for bg, fg in tones:
        out.append(f'<svg class="ph" viewBox="0 0 60 60"><rect width="60" height="60" fill="{bg}"/>'
                   f'<circle cx="42" cy="18" r="7" fill="{fg}" opacity=".7"/>'
                   f'<path d="M0 50 L18 30 L30 42 L40 34 L60 52 L60 60 L0 60 Z" fill="{fg}"/></svg>')
    return "".join(out)


def page_shop():
    pg = Page("")
    items = "\n".join(product(pg, c, s) for c in COLLECTIONS for s in c["order"])
    body = f"""{header(pg, "shop")}
<main id="main">
  <div class="wrap page-head">
    <ol class="crumbs"><li><a href="index.html">Home</a></li><li aria-current="page">Shop all</li></ol>
    <h1>All designs</h1>
    <p class="lede">Every magnet in the shop, {TOTAL} designs in {len(COLLECTIONS)} collections. Pick a collection or search for a city, a sign or a saying.</p>
    <div class="head-row">
      <label class="search"><span class="visually-hidden">Search designs</span>
        <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="8.5" cy="8.5" r="6"/><path d="M13 13l5 5"/></svg>
        <input type="search" id="search" placeholder="Search designs" autocomplete="off">
      </label>
      {deal()} {vol_badge()}
      <span class="count" id="result-count" aria-live="polite">{TOTAL} designs</span>
    </div>
  </div>
{tabs_filters()}
  <section class="tight">
    <div class="wrap">
      <div class="fridge">
        <ul class="products four" id="all-products">
{items}
        </ul>
        <p class="empty-results" id="no-results" hidden>No designs match that search. Try a city, a zodiac sign or a word like “coffee”.</p>
      </div>
    </div>
  </section>
</main>
{footer(pg)}"""
    write("shop.html", head(pg, "Shop all designs", f"All {TOTAL} Little Hive House magnet designs. Filter by collection or search.", "shop.html") + body + chrome_end(pg))


def page_collections_index():
    pg = Page("../")
    cards = "\n".join(col_card(pg, c) for c in COLLECTIONS)
    body = f"""{header(pg, "collections")}
<main id="main">
  <div class="wrap page-head">
    <ol class="crumbs"><li><a href="../index.html">Home</a></li><li aria-current="page">Collections</li></ol>
    <h1>Collections</h1>
    <p class="lede">{len(COLLECTIONS)} collections, from colorful travel posters to black and white skylines. Mix any of them: {BUNDLE[0]} designs for ${BUNDLE[1]}.</p>
  </div>
{tabs_links(pg, None)}
  <section class="tight">
    <div class="wrap">
      <ul class="col-grid">
{cards}
      </ul>
    </div>
  </section>
</main>
{footer(pg)}"""
    write("collections/index.html", head(pg, "Collections", "Browse every Little Hive House magnet collection.", "collections/") + body + chrome_end(pg))


def page_collection(col):
    pg = Page("../")
    items = "\n".join(product(pg, col, s, show_col=False) for s in col["order"])
    idx = COLLECTIONS.index(col)
    others = [COLLECTIONS[(idx + k) % len(COLLECTIONS)] for k in (1, 2, 3)]
    more = "\n".join(col_card(pg, c) for c in others)
    body = f"""{header(pg, "collections")}
<main id="main">
  <div class="wrap page-head">
    <ol class="crumbs"><li><a href="../index.html">Home</a></li><li><a href="index.html">Collections</a></li><li aria-current="page">{E(col["name"])}</li></ol>
    <p class="eyebrow">{E(col["tag"])}</p>
    <h1>{E(col["name"])}</h1>
    <p class="lede">{E(col["blurb"])}</p>
    <div class="head-row">{deal()} {vol_badge()}<span class="count">{len(col["order"])} designs · ${PRICE} each</span></div>
  </div>
{tabs_links(pg, col["slug"])}
  <section class="tight">
    <div class="wrap">
      <div class="fridge">
        <ul class="products">
{items}
        </ul>
      </div>
    </div>
  </section>
  <section class="tight">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="eyebrow">Keep exploring</p>
          <h2>More collections</h2>
        </div>
        <a class="btn btn-ghost btn-small" href="index.html">All collections</a>
      </div>
      <ul class="col-grid">
{more}
      </ul>
    </div>
  </section>
</main>
{footer(pg)}"""
    write(f"collections/{col['slug']}.html",
          head(pg, f"{col['name']} magnets", f"{col['name']}: {col['blurb']}", f"collections/{col['slug']}.html") + body + chrome_end(pg))


def page_photo():
    pg = Page("")
    body = f"""{header(pg, "photo")}
<main id="main">
  <div class="wrap page-head">
    <ol class="crumbs"><li><a href="index.html">Home</a></li><li aria-current="page">Photo magnets</li></ol>
    <h1>Your photos, on the fridge</h1>
    <p class="lede">Glossy 2 × 2 inch magnets made from your own pictures. Kids, pets, trips, grandparents: everyone gets a spot on the fridge.</p>
  </div>
  <section class="tight" id="custom">
    <div class="wrap custom-grid">
      <div>
        <ol class="steps">
          <li><div><h3>Upload your photos</h3><p>Pick your favorite pictures from your phone or computer. Bright, sharp photos print best.</p></div></li>
          <li><div><h3>Choose a pack</h3><p>4 to 50 square magnets, each 2 × 2 inches with a glossy finish. Mix them with any of our designs in the same order.</p></div></li>
          <li><div><h3>We make and ship them</h3><p>We print, press and pack every magnet by hand, then send them to your door.</p></div></li>
        </ol>
        <p class="note">Professional photos belong to the photographer. Only upload pictures you took yourself or have permission to print.</p>
      </div>

      <form class="builder" id="builder" novalidate>
        <fieldset>
          <legend>Pack size</legend>
          <div class="packs">
            <div class="pack"><input type="radio" name="pack" id="pack-4" value="4" data-price="14"><label for="pack-4"><strong>4 magnets</strong><span>$14</span></label></div>
            <div class="pack"><input type="radio" name="pack" id="pack-9" value="9" data-price="25" checked><label for="pack-9"><strong>9 magnets</strong><span>$25</span></label></div>
            <div class="pack"><input type="radio" name="pack" id="pack-16" value="16" data-price="40"><label for="pack-16"><strong>16 magnets</strong><span>$40</span></label></div>
            <div class="pack"><input type="radio" name="pack" id="pack-25" value="25" data-price="65"><label for="pack-25"><strong>25 magnets</strong><span>$65</span></label></div>
            <div class="pack"><input type="radio" name="pack" id="pack-50" value="50" data-price="120"><label for="pack-50"><strong>50 magnets</strong><span>$120</span></label></div>
          </div>
        </fieldset>
        <div>
          <p class="label">Photos</p>
          <label class="drop" id="drop" for="photos">
            <strong>Add photos</strong>
            <span>Tap to choose, or drag them here</span>
          </label>
          <input class="visually-hidden" type="file" id="photos" accept="image/*" multiple>
        </div>
        <div>
          <div class="thumbs" id="thumbs" aria-live="polite"></div>
          <p class="counter" id="counter" style="margin-top:10px">0 of 9 photos added</p>
          <p class="res-note" id="res-note" hidden></p>
        </div>
        <div>
          <label class="label" for="notes">Notes for us (optional)</label>
          <textarea id="notes" placeholder="Names, dates or anything we should know"></textarea>
        </div>
        <label class="check" for="rights">
          <input type="checkbox" id="rights">
          <span>I took these photos or have permission to print them.</span>
        </label>
        <div class="builder-foot">
          <span class="builder-total" id="builder-total">$25</span>
          <button type="submit" class="btn btn-honey" id="add-custom" disabled>Add to cart</button>
        </div>
      </form>
    </div>
  </section>

  <section class="tight">
    <div class="wrap">
      <div class="section-head"><div><p class="eyebrow">Good to know</p><h2>Photo magnet questions</h2></div></div>
      <div class="faq">
        <details><summary>What size are the magnets?</summary><p>Each magnet is a 2 × 2 inch square with rounded corners, a glossy front and a strong magnet back.</p></details>
        <details><summary>Which photos work best?</summary><p>Use the original photo from your camera roll. Screenshots and photos saved from chat apps are often too small and print blurry; the builder warns you when a photo looks too small.</p></details>
        <details><summary>Will you crop my photos?</summary><p>Yes, every photo is cropped to a square. Tell us in the notes if someone must stay in the frame and we will crop around them.</p></details>
        <details><summary>How long does it take?</summary><p>Most packs ship within 3 to 5 business days. Shipping is $4.95 and free on US orders over $35.</p></details>
        <details><summary>Can I mix my photos with your designs?</summary><p>Yes. Add photo packs and any designs from the <a href="shop.html">shop</a> to the same cart. Orders with 20 or more magnets get 10% off automatically, 50 or more get 20% off and 100 or more get 25% off.</p></details>
        <details><summary>Need a custom design for an event?</summary><p>See our <a href="big-orders.html">big order packages</a> for weddings, parties, teams and businesses.</p></details>
      </div>
    </div>
  </section>
</main>
{footer(pg)}"""
    write("photo-magnets.html", head(pg, "Custom photo magnets", "Custom 2 × 2 inch photo magnets from your own pictures. Packs of 4, 9 or 16.", "photo-magnets.html") + body + chrome_end(pg, ("custom.js",)))


PACKAGES = [
    ("Weddings & save the dates", "Weddings", "Favors with your names and date, or save-the-date photo magnets for every guest.",
     [(25, 55), (50, 95), (100, 175), (150, 250)], 100),
    ("Business & real estate", "Business", "Your logo or listing on the fridge all year. A favorite closing gift for realtors and a cheap, lasting ad for small businesses.",
     [(50, 90), (100, 160), (250, 350), (500, 650)], 100),
    ("Parties & events", "Party or event", "Birthdays, baby showers, graduations, reunions and memorials. A keepsake every guest takes home.",
     [(20, 45), (40, 80), (75, 140)], 40),
    ("Teams & schools", "Team or school", "A magnet for every player, student or teacher, with their photo, name and number.",
     [(12, 30), (20, 48), (30, 69)], 20),
]


def page_big():
    pg = Page("")
    cards = []
    for title, key, desc, tiers, pick in PACKAGES:
        rows = "".join(f"<tr><td>{n} magnets</td><td>${p}</td><td>${p / n:.2f} each</td></tr>" for n, p in tiers)
        cards.append(f"""<li class="pkg">
          <h3>{E(title)}</h3>
          <p>{E(desc)}</p>
          <table class="tiers"><thead><tr><th scope="col">Pack</th><th scope="col">Price</th><th scope="col">Per magnet</th></tr></thead><tbody>{rows}</tbody></table>
          <button type="button" class="btn btn-small" data-pkg="{E(key)}" data-qty="{pick}">Request this package</button>
        </li>""")
    options = "<option>Mix &amp; match</option>" + "".join(f"<option>{E(k)}</option>" for _, k, _, _, _ in PACKAGES) + "<option>Something else</option>"
    vol_rows = "".join(f"<li><strong>{n}+ magnets</strong><span>{pct}% off the whole order</span></li>" for n, pct in reversed(VOLUME))
    body = f"""{header(pg, "big")}
<main id="main">
  <div class="wrap page-head">
    <ol class="crumbs"><li><a href="index.html">Home</a></li><li aria-current="page">Big orders</li></ol>
    <h1>Big orders, made by hand</h1>
    <p class="lede">Wedding favors, save the dates, logo magnets and party keepsakes. Every package includes a custom design with your names, date, logo or photos, and a proof to approve before we print.</p>
  </div>
  <section class="tight">
    <div class="wrap">
      <div class="band dark" style="margin-bottom:28px">
        <div>
          <p class="eyebrow">Mix &amp; match</p>
          <h2>Mix anything you like</h2>
          <p>One from the bees, one from the cities, a few from Christmas and a stack of your own photos. Put any mix of designs and photo packs in your cart and the discount is applied automatically.</p>
          <div class="actions"><a class="btn" href="shop.html">Shop designs</a><a class="btn btn-ghost" style="color:inherit;border-color:currentColor" href="photo-magnets.html">Add your photos</a></div>
        </div>
        <ul class="occasions">{vol_rows}<li><strong>Any 3 designs</strong><span>for $12, always</span></li></ul>
      </div>
      <ul class="pkg-grid">
        {chr(10).join(cards)}
      </ul>
    </div>
  </section>

  <section class="tight">
    <div class="wrap">
      <div class="section-head"><div><p class="eyebrow">Every package includes</p><h2>No setup fees, no surprises</h2></div></div>
      <ul class="included">
        <li><strong>Custom design</strong><span>We design it with your names, date, logo or photos.</span></li>
        <li><strong>A proof first</strong><span>You approve the design before we print a single magnet.</span></li>
        <li><strong>Mix and match</strong><span>Use several photos or designs in one order.</span></li>
        <li><strong>Free US shipping</strong><span>Every package ships free.</span></li>
      </ul>
    </div>
  </section>

  <section class="tight" id="request">
    <div class="wrap">
      <div class="section-head"><div><p class="eyebrow">Request a quote</p><h2>Tell us about your order</h2></div><p>We reply within one business day with ideas, a price and a timeline.</p></div>
      <form class="quote" id="quote">
        <div class="field"><label for="q-name">Your name</label><input id="q-name" name="name" required autocomplete="name"></div>
        <div class="field"><label for="q-email">Email</label><input id="q-email" name="email" type="email" required autocomplete="email"></div>
        <div class="field"><label for="q-occasion">Occasion</label><select id="q-occasion" name="occasion">{options}</select></div>
        <div class="field"><label for="q-qty">How many magnets</label><input id="q-qty" name="quantity" type="number" min="10" step="1" value="50" required inputmode="numeric"></div>
        <div class="field"><label for="q-date">Date you need them</label><input id="q-date" name="date" type="date"></div>
        <div class="field full"><label for="q-msg">Your idea</label><textarea id="q-msg" name="message" placeholder="Names, date, colors, a logo or photos you want to use…"></textarea></div>
        <div class="full" style="display:flex;flex-wrap:wrap;gap:14px;align-items:center">
          <button type="submit" class="btn btn-honey">Send request</button>
          <span class="hint">This opens your email app with your request filled in.</span>
        </div>
        <p class="full note" id="quote-done" hidden>Your email app should open now. If it doesn't, write to us at <a href="mailto:support@littlehivehouse.com">support@littlehivehouse.com</a>.</p>
      </form>
    </div>
  </section>

  <section class="tight" id="faq">
    <div class="wrap">
      <div class="section-head"><div><p class="eyebrow">Questions</p><h2>Orders &amp; shipping</h2></div></div>
      <div class="faq">
        <details><summary>How long do big orders take?</summary><p>Most big orders ship 7 to 10 business days after you approve the proof. Need them sooner? Ask us and we will tell you honestly if we can make it.</p></details>
        <details><summary>Can I use your designs instead of my own?</summary><p>Yes. Any design from the shop can be ordered in bulk at package prices, and we can add your names or date to most of them.</p></details>
        <details><summary>Do you have envelopes for save the dates?</summary><p>Yes, kraft envelopes can be added for $0.25 each. Postage is not included.</p></details>
        <details><summary>How much is shipping?</summary><p>Shipping in the US is $4.95 and free on orders over $35, so every big order ships free.</p></details>
        <details><summary>What is the smallest order?</summary><p>Packages start at 12 magnets. For smaller sets, use our <a href="photo-magnets.html">photo magnet packs</a> or the <a href="shop.html">shop</a>.</p></details>
      </div>
    </div>
  </section>
</main>
{footer(pg)}"""
    write("big-orders.html", head(pg, "Big orders", "Custom magnet packages for weddings, businesses, parties, teams and schools. Custom design and proof included.", "big-orders.html") + body + chrome_end(pg, ("quote.js",)))


def page_404():
    pg = Page("/")
    body = f"""{header(pg, None)}
<main id="main">
  <div class="wrap page-head" style="padding-bottom:80px">
    <p class="eyebrow">Page not found</p>
    <h1>This page flew off the fridge.</h1>
    <p class="lede">The link may be old. Try the shop or one of our collections.</p>
    <div class="hero-actions" style="margin-top:24px"><a class="btn" href="/shop.html">Shop all designs</a><a class="btn btn-ghost" href="/collections/index.html">Collections</a></div>
  </div>
</main>
{footer(pg)}"""
    write("404.html", head(pg, "Page not found", "Page not found.", "404.html") + body + chrome_end(pg))


if __name__ == "__main__":
    page_home()
    page_shop()
    page_collections_index()
    for c in COLLECTIONS:
        page_collection(c)
    page_photo()
    page_big()
    page_404()
    print(f"built {TOTAL} designs in {len(COLLECTIONS)} collections")
