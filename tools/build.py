"""Builds the Little Hive House site from designs/ and tools/catalog.py.

Run from anywhere:  python3 tools/build.py
Writes index.html, shop.html, photo-magnets.html, big-orders.html, 404.html and collections/*.html.
"""
import html
import json
import pathlib
import re

import datetime

from catalog import ALL_COLLECTIONS, BUNDLE, COLLECTIONS, FEATURED, GIFTS, GROUPS, HERITAGE_ALL, MORE_COLLECTIONS, PRICE, SALE, SEASONAL, SEASONS, VOLUME, title_for
BY_SLUG = {c["slug"]: c for c in COLLECTIONS}
PARENT = {ch: g for g in GROUPS for ch in g["children"]}


def top_level():
    """Collections as browsed: each group stands in for its children, at the place of its first child."""
    out, seen = [], set()
    for c in COLLECTIONS:
        g = PARENT.get(c["slug"])
        if not g:
            out.append(c)
        elif g["slug"] not in seen:
            seen.add(g["slug"]); out.append(g)
    return out


def group_kids(g):
    return [BY_SLUG[s] for s in g["children"] if s in BY_SLUG]

ROOT = pathlib.Path(__file__).resolve().parents[1]
DESIGNS = ROOT / "designs"
VERSION = "62"
E = html.escape

FONTS = ("https://fonts.googleapis.com/css2?family=Anton&family=Bebas+Neue&family=Cinzel:wght@500;600"
         "&family=DM+Mono:wght@500&family=DM+Serif+Display&family=Josefin+Sans:wght@600;700;800"
         "&family=Jost:wght@400;500;600;700&family=Playfair+Display:ital,wght@1,700"
         "&family=Caveat:wght@600&family=Dancing+Script:wght@600&family=Cormorant+Garamond:ital,wght@1,600&display=swap")

import raster  # noqa: E402
raster.main()
import print_art  # noqa: E402
print_art.main()   # 1200 px print files of the designs on sale (functions/printsheet.js)

# Site decoration season by date (inclusive MMDD ranges); the spotlight uses catalog.SEASONS.
DECOR = [(1226, 1231, "newyear"), (101, 103, "newyear"), (104, 131, "winter"), (201, 214, "valentine"), (215, 229, "winter"),
         (301, 317, "stpatricks"), (318, 531, "spring"), (601, 621, "summer"), (622, 704, "july4"), (705, 831, "summer"),
         (901, 1014, "fall"), (1015, 1031, "halloween"), (1101, 1127, "thanksgiving"), (1128, 1225, "christmas")]
DECOR_JS = "[" + ",".join(f"[{a},{b},'{c}']" for a, b, c in DECOR) + "]"

BY_SLUG = {c["slug"]: c for c in COLLECTIONS}
CUR = ' aria-current="page"'
def count(c):
    """Every design of a collection: the first ones and the ones behind "See more"."""
    return len(c["order"]) + len(more_of(c))


TOTAL = None   # set below, once more_of() exists


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
       ("photo-magnets.html", "Photo magnets", "photo"), ("personalize.html", "Personalize", "personalize"), ("business.html", "For business", "business"), ("big-orders.html", "Bulk orders", "big"),
       ("shipping.html", "Shipping", "shipping"), ("suggestions.html", "Share an idea", "ideas")]


BIZ_LINKS = (("business.html", "Your business", "clean-word"), ("weddings.html", "Weddings", "wed-arch"),
             ("graduation.html", "Graduation", "grad-year-navy"), ("parties.html", "Parties & events", "party-birthday"))
BRIEFCASE = ('<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" aria-hidden="true">'
             '<rect x="2.5" y="6" width="15" height="10.5" rx="2"/><path d="M7 6V4.6c0-.6.4-1 1-1h4c.6 0 1 .4 1 1V6M2.5 10.5h15"/></svg>')


def biz_menu(pg):
    """The box for companies and events inside the mobile menu."""
    links = "".join(f'<a href="{pg.p}{h}">{E(n)}</a>' for h, n, _ in BIZ_LINKS)
    return f"""      <div class="menu-biz">
        <a class="menu-biz-main" href="{pg.p}business.html">{BRIEFCASE}<span><strong>For business &amp; events</strong><small>Bulk pricing, your logo, from 25 magnets</small></span></a>
        <div class="menu-biz-links">{links}<a href="{pg.p}big-orders.html">All bulk orders</a></div>
      </div>"""


def biz_row(pg):
    """A slim row under the two doors on the home page: the four bulk pages."""
    cards = "".join(f'<li><a href="{pg.p}{h}">{occ_img(pg, im, size=600, lazy=False)}<span>{E(n)}</span></a></li>' for h, n, im in BIZ_LINKS)
    return f"""      <div class="biz-row">
        <div class="biz-row-head">
          <p class="eyebrow">{BRIEFCASE} For business &amp; events</p>
          <p>Your logo or names on every magnet, bulk prices from 25 pieces. <a href="{pg.p}big-orders.html">All bulk orders →</a></p>
        </div>
        <ul>{cards}</ul>
      </div>"""


def idea_strip(pg, lead="Don’t see your favorite?", text="Tell us the place, the pet or the saying and we might draw it next."):
    """A dashed call-out that sends people to the ideas box (suggestions.html)."""
    return f"""      <div class="idea-strip">
        <p><strong>{lead}</strong> {text}</p>
        <a class="btn btn-small" href="{pg.p}suggestions.html">Share an idea</a>
      </div>"""


IDEA_ART = (("places", "savannah"), ("furry-friends", "dog-mom"), ("kitchen-words", "but-first-coffee"),
            ("bee-kind", "bee-kind"), ("world", "santorini"))



# The site's languages: (code, name in that language, <html lang>). English is the page itself; every other one is a
# dictionary, assets/i18n-<code>.js, built by tools/i18n_build.py from tools/i18n/<code>-*.json. A language goes live
# (detected from the phone, listed in the menu) as soon as its dictionary file exists.
LANGS_ALL = [("en", "English", "en"), ("es", "Español", "es"), ("pt", "Português", "pt-BR"), ("zh", "中文", "zh-Hans"),
             ("fil", "Tagalog", "fil"), ("vi", "Tiếng Việt", "vi"), ("fr", "Français", "fr"), ("ko", "한국어", "ko"),
             ("ru", "Русский", "ru"), ("ar", "العربية", "ar")]
LANGS = [l for l in LANGS_ALL if l[0] == "en" or (ROOT / "assets" / f"i18n-{l[0]}.js").exists()]


def i18n_version():
    """Changes whenever the translator or a dictionary changes, so phones fetch the new one."""
    import hashlib
    h = hashlib.sha1()
    for f in ["i18n.js"] + [f"i18n-{c}.js" for c, _, _ in LANGS if c != "en"]:
        fp = ROOT / "assets" / f
        if fp.exists():
            h.update(fp.read_bytes())
    return h.hexdigest()[:8]


def lang_head(pg):
    """The visitor's language: the one they picked (localStorage "lhh-lang"), else their phone's (the browser's language
    list, the same on iPhone and Android: the first one we have, or English when English comes first or we have none).
    In another language the page stays hidden until it's translated (at most 3 s), so English never flashes."""
    v = i18n_version()
    have = json.dumps({c: h for c, _, h in LANGS}, separators=(",", ":"))
    names = json.dumps({c: n for c, n, _ in LANGS}, separators=(",", ":"), ensure_ascii=False)
    return ("<script>(function(){var L=" + have + ";window.LHH_LANGS=" + names + ";"
            "var a=navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||'en'],ph='en';"
            "for(var i=0;i<a.length;i++){var c=String(a[i]).toLowerCase().split('-')[0];if(c==='tl')c='fil';if(c==='en'||L[c]){ph=c;break}}"
            "var l;try{l=localStorage.getItem('lhh-lang')}catch(e){}if(!L[l])l=ph;"
            "window.LHH_LANG=l;window.LHH_PHONE_LANG=ph;var h=document.documentElement;h.setAttribute('data-lang',l);h.setAttribute('data-phone-lang',ph);"
            "if(l!=='en'){h.lang=L[l];if(l==='ar')h.dir='rtl';setTimeout(function(){h.classList.add('i18n-ready')},3000);"
            f"document.write('<script src=\"{pg.p}assets/i18n.js?v={v}\"><\\/script><script src=\"{pg.p}assets/i18n-'+l+'.js?v={v}\"><\\/script>')}}}})();</script>\n"
            "<style>html:not([data-lang=en]):not(.i18n-ready) body{visibility:hidden}</style>")


def lang_switch(cls="lang-sw"):
    """At the top: nothing for English visitors. In another language, one button back to English; after choosing
    English on a phone in another language, one button back to that language (assets/site.js fills its name)."""
    return (f'<span class="{cls}" translate="no">'
            '<a href="#" data-set-lang="en" class="lang-to-en" lang="en" hreflang="en"><span aria-hidden="true">🌐</span> English</a>'
            '<a href="#" data-set-lang="" class="lang-to-phone" data-lang-phone><span aria-hidden="true">🌐</span> <span data-lang-phone-name></span></a></span>')


def lang_menu():
    """Inside the menu: every language we have, each in its own name."""
    return ('<span class="lang-list" translate="no">' + "".join(
        f'<a href="#" data-set-lang="{c}" lang="{h}" hreflang="{h}">{n}</a>' for c, n, h in LANGS) + "</span>")


def head(pg, title, desc, path):
    full = "Little Hive House · Handmade Fridge Magnets" if title is None else f"{title} · Little Hive House"
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
<link rel="icon" href="https://littlehivehouse.com/favicon.ico" sizes="48x48">
<link rel="icon" href="{pg.p}assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{pg.p}assets/favicon-96.png" type="image/png" sizes="96x96">
<link rel="apple-touch-icon" href="https://littlehivehouse.com/apple-touch-icon.png">
<meta property="og:image" content="https://littlehivehouse.com/assets/og-image.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:site_name" content="Little Hive House">
<meta property="og:url" content="https://littlehivehouse.com/{path}">
<meta name="twitter:card" content="summary_large_image">
<link rel="manifest" href="https://littlehivehouse.com/site.webmanifest">
<script>(function(){{var h=new Date().getHours(),t=(h>=6&&h<19)?'light':'dark';try{{var m=JSON.parse(localStorage.getItem('lhh-theme2')||'null');if(m&&m.until>Date.now()&&(m.t==='light'||m.t==='dark'))t=m.t;localStorage.removeItem('lhh-theme')}}catch(e){{}}document.documentElement.setAttribute('data-theme',t);var d=new Date(),k=(d.getMonth()+1)*100+d.getDate(),z='winter',T={DECOR_JS};for(var i=0;i<T.length;i++)if(k>=T[i][0]&&k<=T[i][1])z=T[i][2];document.documentElement.setAttribute('data-season',z)}})();</script>
{lang_head(pg)}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{pg.p}assets/site.css?v={VERSION}">
{GA_TAG}
</head>
<body>
"""


def header(pg, active):
    links = "\n".join(
        f'      <a href="{pg.p}{href}"{" class=" + chr(34) + ("minor" if key in ("shipping", "ideas") else "biz") + chr(34) if key in ("shipping", "ideas", "business") else ""}{CUR if key == active else ""}>{label}</a>'
        for href, label, key in NAV)   # "biz": a pill, still shown on tablets   # "minor": only on wide screens (the strip, the menu and the footer have them too)
    mobile = []
    for href, label, key in NAV:
        if key in ("business", "big"):
            continue
        mobile.append(f'      <a href="{pg.p}{href}">{label}</a>')
        if key == "photo":
            mobile.append(biz_menu(pg))
    mobile = "\n".join(mobile)
    def _sub(c):
        line = f'      <a class="sub"{season_attr(c)} href="{pg.p}collections/{c["slug"]}.html">{E(c["name"])}</a>'
        if "children" in c:
            line += "".join(f'\n      <a class="sub sub2" href="{pg.p}collections/{k["slug"]}.html">{E(k["name"])}</a>' for k in group_kids(c))
        return line
    subs = "\n".join(_sub(c) for c in top_level())
    return f"""<a class="visually-hidden" href="#main">Skip to content</a>
<div class="strip"><a class="s1" href="{pg.p}shipping.html">Free US shipping on orders over $35</a><span class="dot d1" aria-hidden="true">·</span><span class="s2">Handmade<span class="long"> in small batches</span></span><span class="dot d3" aria-hidden="true">·</span><a class="s3" href="{pg.p}business.html">Business &amp; bulk orders</a>{social_strip()}{lang_switch()}</div>

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
      <button type="button" class="theme-btn" id="theme-btn" aria-label="Switch between light and dark">
        <svg class="i-sun" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="10" cy="10" r="3.6"/><path d="M10 1.8v2.2M10 16v2.2M1.8 10H4M16 10h2.2M4.2 4.2l1.6 1.6M14.2 14.2l1.6 1.6M4.2 15.8l1.6-1.6M14.2 5.8l1.6-1.6"/></svg>
        <svg class="i-moon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" aria-hidden="true"><path d="M16.5 12.6A7 7 0 0 1 7.4 3.5a7 7 0 1 0 9.1 9.1z"/></svg>
      </button>
      {social_header()}
      <!-- store: account icon (assets/store.js shows the signed-in initial) -->
      <a class="acct-btn" href="{pg.p}account.html" data-account aria-label="Your account">
        <svg class="i-person" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="10" cy="7" r="3.4"/><path d="M3.6 17.2c.9-3.1 3.4-4.8 6.4-4.8s5.5 1.7 6.4 4.8"/></svg>
        <span class="acct-initial" data-account-initial hidden></span>
      </a>
      <!-- /store -->
      <button type="button" class="cart-btn" data-open-cart aria-haspopup="dialog">
        Cart <span class="cart-count" data-cart-count>0</span>
      </button>
    </nav>
  </div>
  <div class="mobile-menu" id="mobile-menu" hidden>
    <nav class="wrap" aria-label="Mobile">
{mobile}
      <a class="acct-link" href="{pg.p}account.html" data-account-menu>Your account</a>
      <a class="acct-link" href="{pg.p}favorites.html">Favorites</a>
      <a class="acct-link" href="{pg.p}track.html">Track an order</a>
      <div class="acct-link lang-row"><span>Language</span>{lang_menu()}</div>
{social_menu()}
{subs}
    </nav>
  </div>
</header>
<div class="garland" aria-hidden="true"></div>
"""


def tabs_links(pg, active):
    items = [f'<a class="tab" href="{pg.p}shop.html"{CUR if active == "all" else ""}>All <small>{TOTAL_TEXT}</small></a>']
    for c in COLLECTIONS:
        cur = ' aria-current="page"' if c["slug"] == active else ""
        items.append(f'<a class="tab"{season_attr(c)} href="{pg.p}collections/{c["slug"]}.html"{cur}>{E(c["name"])} <small>{count(c)}</small></a>')
    return f"""<div class="tabs-bar">
  <nav class="wrap tabs" aria-label="Collections">
    {chr(10).join("    " + i for i in items).strip()}
  </nav>
</div>
"""


def tabs_filters():
    items = [f'<button type="button" class="tab" data-filter="all" aria-pressed="true">All <small>{TOTAL_TEXT}</small></button>']
    for c in COLLECTIONS:
        items.append(f'<button type="button" class="tab" data-filter="{c["slug"]}" aria-pressed="false">{E(c["name"])} <small>{count(c)}</small></button>')
    return f"""<div class="tabs-bar">
  <div class="wrap tabs" role="group" aria-label="Filter by collection">
    {chr(10).join("    " + i for i in items).strip()}
  </div>
</div>
"""


def product(pg, col, slug, show_col=True, more=False):
    t = title_for(col, slug)
    href = f'{pg.p}collections/{col["slug"]}.html'
    meta = (f'<p class="col"><a href="{href}">{E(col["name"])}</a></p>' if show_col
            else '<p class="spec">2 × 2 in magnet</p>')
    search = E(f'{t} {col["name"]} {col["tag"]}'.lower())
    extra = " data-more hidden" if more else ""
    return f"""<li class="product" data-collection="{col["slug"]}" data-search="{search}"{extra}>
  <button type="button" class="product-art" data-view aria-label="See {E(t)} larger">{pg.svg(col["slug"], slug)}</button>
  <div class="product-info">
    <h3 translate="no"><a href="{pg.p}m/{col["slug"]}/{slug}.html">{E(t)}</a></h3>
    {meta}
    <p class="price">${PRICE}</p>
  </div>
  <button type="button" class="btn btn-small" data-add="{col["slug"]}/{slug}" data-name="{E(t)}" data-collection="{E(col["name"])}" data-href="{href}">Add to cart</button>
</li>"""


def season_attr(col):
    """data-season on seasonal collections (site.js moves them up in season, down out of season);
    data-season-anchor marks where in-season ones go (right after the place collections)."""
    if col["slug"] in SEASONAL:
        a, b = SEASONAL[col["slug"]]
        return f' data-col-season="{a:04d}-{b:04d}"'
    return ' data-col-anchor' if col["slug"] == "city-sketches" else ""


def col_card(pg, col):
    if "children" in col:
        kids = group_kids(col)
        # three magnets in the fan even when the group has only two collections: take turns between them
        picks, depth = [], 0
        while len(picks) < 3 and depth < 3:
            picks += [(k["slug"], k["order"][depth]) for k in kids if depth < len(k["order"])]
            depth += 1
        fan = "".join(f'<span class="m">{pg.svg(c, sl, cls="fan-svg")}</span>' for c, sl in picks[:3])
        n = sum(count(k) for k in kids)
        return f"""<li><a class="col-card" href="{pg.p}collections/{col["slug"]}.html">
  <div class="fan" aria-hidden="true">{fan}</div>
  <div class="col-body">
    <h3>{E(col["name"])}</h3>
    <p>{E(col["tag"])} · {len(kids)} countries · {n} designs</p>
    <span class="more">{E(", ".join(k["name"] for k in kids))} →</span>
  </div>
</a></li>"""
    fan = "".join(f'<span class="m">{pg.svg(col["slug"], s, cls="fan-svg")}</span>' for s in col["order"][:3])
    return f"""<li{season_attr(col)}><a class="col-card" href="{pg.p}collections/{col["slug"]}.html">
  <div class="fan" aria-hidden="true">{fan}</div>
  <div class="col-body">
    <h3>{E(col["name"])}</h3>
    <p>{E(col["tag"])} · {count(col)} designs</p>
    <span class="more">Shop the collection →</span>
  </div>
</a></li>"""


def has_art(col_slug, slug):
    return (ROOT / f"assets/art/{col_slug}/{slug}.webp").exists()


def more_of(col):
    """The archived designs of a collection that come back behind "See more" (only those with a picture)."""
    return [s for s in col.get("more", []) if has_art(col["slug"], s)]


TOTAL = sum(count(c) for c in COLLECTIONS)
# what the site says (owners: "more than 1000", not the exact number)
TOTAL_TEXT = f"{TOTAL // 100 * 100:,}+" if TOTAL >= 1000 else str(TOTAL)


def more_button(n, what="designs"):
    return (f'<div class="see-more"><button type="button" class="btn btn-ghost" data-see-more aria-expanded="false">'
            f'See {n} more {what}</button></div>') if n else ""


def deal():
    return f'<span class="deal">Any {BUNDLE[0]} designs for ${BUNDLE[1]}</span>'


def vol_badge():
    n, pct = VOLUME[-1]
    return f'<span class="deal alt">{pct}% off {n}+ magnets</span>'


# the Meta Pixel (1824876368823217): page views, and each store event under Meta's name, so the ads can find buyers.
# Not loaded when the browser sends Global Privacy Control (see privacy.html). Purchase carries the order number,
# the same event_id the server sends (functions/metaevents.js), so Meta counts it once.
PIXEL_JS = '(function(){if(navigator.globalPrivacyControl)return;!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version="2.0";n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,"script","https://connect.facebook.net/en_US/fbevents.js");fbq("init","1824876368823217");fbq("track","PageView");})();window.lhhTrack=function(n,p){try{gtag("event",n,p||{});}catch(e){}try{var M={view_item:"ViewContent",add_to_cart:"AddToCart",begin_checkout:"InitiateCheckout",purchase:"Purchase",add_to_wishlist:"AddToWishlist"}[n];if(M&&window.fbq){p=p||{};var it=p.items||[],d={currency:p.currency||"USD",content_type:"product",content_ids:it.map(function(i){return String(i.item_id)}),num_items:it.reduce(function(t,i){return t+(Number(i.quantity)||1)},0)};if(p.value!=null)d.value=Number(p.value)||0;if(M==="Purchase"&&p.transaction_id)fbq("track",M,d,{eventID:String(p.transaction_id)});else fbq("track",M,d);}}catch(e){}};'

# Google Analytics 4 (Firebase project little-hive-house, property 562104666): visits for the Hive Admin's Visits page.
GA_ID = "G-VHW80371B0"
GA_TAG = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>\n'
          f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());'
          f'gtag("config","{GA_ID}");' + PIXEL_JS + '</script>')

# the shop's social accounts live in tools/social.json: add a line there and every spot below picks it up
# (top strip, header, phone menu, home band, footer, contact page, Google's sameAs, business and thank-you cards).
IG_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17.4" cy="6.6" r="1.2" fill="currentColor"/></svg>'
FB_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M15.6 7.4h-1.7c-1.4 0-2.2.9-2.2 2.3V21M9.6 12.6h5.4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'
TT_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.6 3.5v11.3a3.3 3.3 0 1 1-3.3-3.3M13.6 3.5c.4 2.6 2.2 4.4 4.9 4.6" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>'
SOCIAL_ICONS = {"instagram": IG_ICON, "facebook": FB_ICON, "tiktok": TT_ICON}
SOCIAL_BG = ("instagram", "facebook", "tiktok")   # networks with their own colour in site.css (.ib-icon[data-net])
_soc = json.loads((pathlib.Path(__file__).resolve().parent / "social.json").read_text(encoding="utf-8"))["networks"]
SOCIAL = [(n["name"], n["url"], n["handle"], SOCIAL_ICONS.get(n["name"].lower(), IG_ICON)) for n in _soc]
SOCIAL_HANDLES = sorted({h for _, _, h, _ in SOCIAL})


def social_strip():
    """The top strip: each network's icon, then the @ (the same @ everywhere) or the network's name."""
    if not SOCIAL:
        return ""
    one = len(SOCIAL_HANDLES) == 1
    links = "".join(f'<a class="strip-ig" href="{u}" target="_blank" rel="noopener me" aria-label="Follow Little Hive House on {n}">{icon}'
                    f'{"" if one and len(SOCIAL) > 1 else f"<span>{E(h)}</span>"}</a>' for n, u, h, icon in SOCIAL)
    tail = f'<span class="strip-handle">{E(SOCIAL_HANDLES[0])}</span>' if one and len(SOCIAL) > 1 else ""
    return f'<span class="dot" aria-hidden="true">·</span><span class="strip-soc">{links}{tail}</span>'


def social_header():
    return "".join(f'<a class="ig-btn" href="{u}" target="_blank" rel="noopener me" aria-label="Little Hive House on {n}">{icon}</a>'
                   for n, u, h, icon in SOCIAL)


def social_menu():
    return "\n".join(f'      <a class="acct-link ig-link" href="{u}" target="_blank" rel="noopener me">{icon}Follow us on {n}</a>'
                     for n, u, h, icon in SOCIAL)


def social_band(pg):
    """The home-page band. With one network it speaks about that one; with more, about all of them."""
    if not SOCIAL:
        return ""
    one = len(SOCIAL) == 1
    eyebrow = f"On {SOCIAL[0][0]}" if one else "Follow along"
    btns = "".join(f'<a class="btn btn-honey btn-ig" href="{u}" target="_blank" rel="noopener me">{icon}'
                   f'{"Follow " + E(h) if one else E(n)}</a>' for i, (n, u, h, icon) in enumerate(SOCIAL))
    tiles = "".join(f'<a class="ib-icon" href="{u}" target="_blank" rel="noopener me" tabindex="-1" data-net="{n.lower() if n.lower() in SOCIAL_BG else "instagram"}">{icon}</a>'
                    for n, u, h, icon in SOCIAL)
    handle = E(SOCIAL_HANDLES[0]) if len(SOCIAL_HANDLES) == 1 else ""
    return f"""  <section class="tight" id="instagram">
    <div class="wrap">
      <div class="band insta">
        <div>
          <p class="eyebrow">{eyebrow}</p>
          <h2>Come see what’s on our fridge</h2>
          <p>New designs before they hit the shop, behind the scenes at the press, and photos from your fridges. Tag us when your magnets arrive and we might share yours.</p>
          <div class="actions" data-n="{min(3, len(SOCIAL))}">{btns}</div>
        </div>
        <div class="insta-badge{" many" if not one else ""}" aria-hidden="true"><div class="ib-row">{tiles}</div>{f'<span class="ib-handle">{handle}</span>' if handle else ""}</div>
      </div>
    </div>
  </section>

"""


def social_links(cls="social"):
    """Icon links to the shop's social accounts; on a phone with the app, the link opens the app."""
    items = "".join(f'<a href="{u}" target="_blank" rel="noopener me" aria-label="Little Hive House on {n}">{icon}<span>{E(h)}</span></a>'
                    for n, u, h, icon in SOCIAL)
    return f'<div class="{cls}">{items}</div>' if SOCIAL else ""


def footer(pg):
    cols = "\n".join(f'          <li><a href="{pg.p}collections/{c["slug"]}.html">{E(c["name"])}</a></li>' for c in COLLECTIONS)
    return f"""<footer>
  <div class="wrap">
    <div class="foot-cols">
      <div class="brandcol">
        {LOGO.replace('aria-hidden="true"', 'aria-hidden="true" class="foot-logo"')}
        <p>Handmade fridge magnets and little gifts, printed and pressed by hand in small batches.</p>
        {social_links()}
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
          <li><a href="{pg.p}track.html">Track your order</a></li>
          <li><a href="{pg.p}account.html">Your account</a></li>
          <li><a href="{pg.p}contact.html">Contact us</a></li>
          <li><a href="{pg.p}suggestions.html">Share an idea</a></li>
          <li><a href="{pg.p}shipping.html">Shipping</a></li>
          <li><a href="{pg.p}returns.html">Returns &amp; refunds</a></li>
          <li><a href="{pg.p}index.html#about">About us</a></li>
          <li><a href="mailto:support@littlehivehouse.com">support@<wbr>littlehivehouse.com</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-bottom">
      <span>© 2026 Little Hive House · <a href="{pg.p}privacy.html">Privacy</a> · <a href="{pg.p}terms.html">Terms</a></span>
      <span>Shipping $5.49 · free on US orders over $35</span>
    </div>
  </div>
</footer>
"""


def chrome_end(pg, extra_js=()):
    scripts = "\n".join(f'<script src="{pg.p}assets/{s}?v={VERSION}"></script>' for s in ("firebase-config.js", "delivery.js", "site.js", "store.js", "checkout.js") + tuple(extra_js))
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
    <div class="discount sale-row" id="t-sale-row" hidden><span id="t-sale-label">Sale</span><span id="t-sale">−$0</span></div>
    <div><span>Shipping</span><span id="t-ship">$5.49</span></div>
    <div class="tax-row"><span>Sales tax</span><span>Added at checkout</span></div>
    <div class="grand"><span>Total before tax</span><span id="t-total">$0</span></div>
    <p class="ship-note" id="ship-note"></p>
    <p class="ship-note eta-note" id="eta-note"></p>
    <p class="ship-note" id="vol-note" hidden></p>
    <p class="ship-note sale-note" id="sale-note" hidden></p>
    <!-- store: checkout extras (assets/checkout.js shows them once the store is connected) -->
    <div class="co" id="co" hidden>
      <details class="co-extras">
        <summary>Add a gift message or a note</summary>
        <label class="co-label" for="co-gift">Gift message <small>optional, we tuck it in the box</small></label>
        <textarea id="co-gift" maxlength="300" rows="2" placeholder="Happy birthday, Mom!"></textarea>
        <label class="co-label" for="co-notes">Note for us <small>optional</small></label>
        <textarea id="co-notes" maxlength="1000" rows="2" placeholder="Anything we should know"></textarea>
      </details>
      <label class="check co-mkt" for="co-mkt"><input type="checkbox" id="co-mkt"><span>Email me about new designs and offers</span></label>
      <div class="co-progress" id="co-progress" hidden>
        <p id="co-progress-label">Uploading your photos</p>
        <div class="co-bar" role="progressbar" id="co-bar" aria-labelledby="co-progress-label" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span id="co-bar-fill"></span></div>
      </div>
      <p class="co-error" id="co-error" role="alert" hidden></p>
    </div>
    <!-- /store -->
    <button type="button" class="btn btn-honey" id="checkout" disabled>Checkout opens soon</button>
    <p class="co-secure" id="co-secure" hidden>Secure payment with Stripe. You can review everything before you pay.</p>
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
        <li>2 × 2 inch square magnet with square corners</li>
        <li>Glossy, scratch-resistant front and a strong magnet back</li>
        <li>Made by hand and shipped in 1–2 business days</li>
        <li class="qv-eta">Order today, it arrives <strong data-eta>in about a week</strong> in the US · <a href="{pg.p}shipping.html">Shipping details</a></li>
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


# ---------------------------------------------------------------- photo magnets showcase (assets/showcase, tools/showcase/render.js)
# (id, title, line, frame the builder starts with, number of sample magnets)
OCCASIONS = [
    ("wedding", "Weddings", "The vows, the first dance, the whole crew. Favors for every guest, too.", "wedding", 3),
    ("family", "Family & grandparents", "The faces that make a house a home.", "instant", 3),
    ("baby", "Baby's first year", "Every tiny milestone, right where you see it every day.", "white", 3),
    ("pets", "Pets", "Because they are family too.", "instant", 3),
    ("graduation", "Graduation", "Caps, gowns and big proud smiles.", "instant", 3),
    ("travel", "Trips & vacations", "Postcards from the places you have been.", "postcard", 3),
]


def showcase_img(pg, occ, n, lazy=True, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{pg.p}assets/showcase/{occ}-{n}.webp" width="480" height="480" alt=""'
            f'{" loading=\"lazy\"" if lazy else ""} decoding="async">')


def occasion_cards(pg):
    out = []
    for oid, title, line, frame, n in OCCASIONS:
        fan = "".join(f'<span class="m">{showcase_img(pg, oid, i)}</span>' for i in range(1, min(n, 3) + 1))
        out.append(f"""<li><a class="col-card" href="{pg.p}photo-magnets.html?frame={frame}#custom">
  <div class="fan" aria-hidden="true">{fan}</div>
  <div class="col-body">
    <h3>{E(title)}</h3>
    <p>{E(line)}</p>
    <span class="more">Make yours →</span>
  </div>
</a></li>""")
    return "\n".join(out)


def doors(pg):
    """The two halves of the shop, side by side: our designs and the customer's own photos."""
    ours = "".join(f'<span class="m">{pg.svg(c, s, cls="fan-svg")}</span>' for c, s in FEATURED[:3])
    theirs = "".join(f'<span class="m">{showcase_img(pg, o, n, lazy=False)}</span>' for o, n in (("pets", 3), ("wedding", 1), ("baby", 1)))
    return f"""  <section class="tight doors" aria-label="Two ways to shop">
    <div class="wrap">
      <ul class="door-grid">
        <li><a class="col-card door" href="{pg.p}shop.html">
          <div class="fan" aria-hidden="true">{ours}</div>
          <div class="col-body">
            <p class="eyebrow">Our designs</p>
            <h2>{TOTAL_TEXT} original magnets</h2>
            <p>Travel posters, skylines, seasons, star signs and more, drawn by us. ${PRICE} each.</p>
            <span class="btn">Shop our designs</span>
          </div>
        </a></li>
        <li><a class="col-card door" href="{pg.p}photo-magnets.html">
          <div class="fan" aria-hidden="true">{theirs}</div>
          <div class="col-body">
            <p class="eyebrow">Your photos</p>
            <h2>Magnets from your pictures</h2>
            <p>Upload, pick a frame, move and zoom each photo. Any number from 1 to 100, from $4.</p>
            <span class="btn">Make photo magnets</span>
          </div>
        </a></li>
        <li><a class="col-card door" href="{pg.p}personalize.html">
          <div class="fan" aria-hidden="true">{"".join(f'<span class="m"><img src="{pg.p}assets/occasions/{sl}.webp" alt="" width="360" height="360" loading="lazy" decoding="async"></span>' for sl in ("p-family-2", "p-pets-1", "p-baby-2"))}</div>
          <div class="col-body">
            <p class="eyebrow">Personalize</p>
            <h2>Your name, your pet, your family</h2>
            <p>Hundreds of designs to make yours: change the words and colors, add a photo. From ${PERSONAL[3][0][1]}.</p>
            <span class="btn">Make yours</span>
          </div>
        </a></li>
      </ul>
{biz_row(pg)}
    </div>
  </section>"""


# ---------------------------------------------------------------- pages
def page_home():
    pg = Page("")
    cards = "\n".join(col_card(pg, c) for c in top_level())
    feat = "\n".join(product(pg, BY_SLUG[c], s) for c, s in FEATURED)
    body = f"""{header(pg, "home")}
<main id="main">
  <section class="hero">
    <div class="wrap hero-grid">
      <div>
        <p class="eyebrow">Handmade magnets &amp; photo gifts</p>
        <h1>Our designs or your photos, <em>made by hand.</em></h1>
        <p class="lede">{TOTAL_TEXT} original magnet designs, and custom magnets made from your own pictures: weddings, grandkids, pets, trips. Each one is printed, pressed and packed in our little house.</p>
        <div class="hero-actions">
          <a class="btn" href="shop.html">Shop our designs</a>
          <a class="btn" href="photo-magnets.html">Make photo magnets</a>
        </div>
        <a class="biz-hook" href="business.html">{BRIEFCASE}<span><strong>Ordering for a business or an event?</strong> <span class="bh-more">Bulk prices and your own logo</span></span><span class="bh-arrow" aria-hidden="true">→</span></a>
      </div>
      <div class="seal">
        {seal("hero")}
        <div class="season-scene" aria-hidden="true"></div>
      </div>
    </div>
  </section>

{doors(pg)}

{spotlight_block(pg)}
{tabs_links(pg, None)}
  <section id="collections">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="eyebrow">Shop by collection</p>
          <h2>Find your kind of magnet</h2>
        </div>
        <p>Travel posters, black and white skylines, seasonal favorites, star signs, great paintings and more. {deal()} {vol_badge()}</p>
      </div>
      <ul class="col-grid occ-grid col-limit">
{cards}
      </ul>
      <div class="see-all"><a class="btn btn-ghost" href="collections/index.html">See all {len(top_level())} collections →</a></div>
    </div>
  </section>

  <section class="tight" id="occasions">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="eyebrow">Photo magnets</p>
          <h2>Your photos, for every occasion</h2>
        </div>
        <p>Send us your favorite pictures and we turn them into glossy 2 × 2 inch magnets, with a frame and a caption if you like. Mix them with our designs in the same order.</p>
      </div>
      <ul class="col-grid occ-grid">
{occasion_cards(pg)}
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
        <a class="btn btn-ghost btn-small" href="shop.html">See all {TOTAL_TEXT} designs</a>
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
          <p>Upload your favorite pictures, choose a frame and move or zoom each one until it looks just right. We turn them into a set of glossy 2 × 2 inch magnets. As many as you like, from 1 to 100, and you can mix them with any of our designs.</p>
          <div class="actions"><a class="btn" href="photo-magnets.html">Make photo magnets</a></div>
        </div>
        <div class="band-art" aria-hidden="true">{"".join(showcase_img(pg, o, n, cls="ph") for o, n in (("family", 1), ("travel", 1), ("pets", 2), ("graduation", 1), ("baby", 2), ("wedding", 3)))}</div>
      </div>
    </div>
  </section>

  <section class="tight">
    <div class="wrap">
      <div class="band dark">
        <div>
          <p class="eyebrow">Bulk orders</p>
          <h2>For businesses, weddings and parties</h2>
          <p>Magnets with your logo, favors with your names and date, a photo for every guest. We design it with you, you approve it, we press every piece by hand.</p>
          <div class="actions"><a class="btn" href="business.html">For business</a><a class="btn btn-ghost" style="color:inherit;border-color:currentColor" href="big-orders.html">All bulk orders</a></div>
        </div>
        <ul class="occasions occasions-links">
          <li><a href="business.html"><strong>Business</strong><span>Your logo on their fridge, all year</span></a></li>
          <li><a href="weddings.html"><strong>Weddings</strong><span>Save the dates and favors</span></a></li>
          <li><a href="graduation.html"><strong>Graduation &amp; college</strong><span>Favors, welcome week, clubs</span></a></li>
          <li><a href="parties.html"><strong>Parties &amp; events</strong><span>Holiday parties, showers, reunions</span></a></li>
        </ul>
      </div>
    </div>
  </section>

  <section class="tight" id="ideas">
    <div class="wrap">
      <div class="band idea">
        <div>
          <p class="eyebrow">Ideas box</p>
          <h2>Your idea could be our next magnet</h2>
          <p>Missing your town, your dog’s breed or the saying your family always uses? Tell us. We read every idea ourselves and draw our favorites. Something on the site could be better? Tell us that too.</p>
          <div class="actions"><a class="btn btn-honey" href="suggestions.html">Share an idea</a></div>
        </div>
        <div class="band-art" aria-hidden="true">{"".join(f'<img class="ph" src="{pg.p}assets/art/{c}/{s}.webp" width="600" height="600" alt="" loading="lazy" decoding="async">' for c, s in IDEA_ART)}<span class="ph idea-tile">Your idea here</span></div>
      </div>
    </div>
  </section>

{social_band(pg)}  <section class="about" id="about">
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
    ld = ('<script type="application/ld+json">{"@context":"https://schema.org","@graph":['
          '{"@type":"Organization","@id":"https://littlehivehouse.com/#org","name":"Little Hive House","url":"https://littlehivehouse.com/",'
          '"logo":"https://littlehivehouse.com/assets/icon-512.png","email":"support@littlehivehouse.com",'
          '"sameAs":' + json.dumps([u for _, u, _, _ in SOCIAL]) + ','
          '"description":"Handmade fridge magnets and gifts, designed, printed and pressed in a small family studio near Atlanta, Georgia."},'
          '{"@type":"WebSite","name":"Little Hive House","url":"https://littlehivehouse.com/","publisher":{"@id":"https://littlehivehouse.com/#org"}}]}</script>\n')
    body = ld + body
    write("index.html", head(pg, None, f"Handmade fridge magnets: {TOTAL_TEXT} original designs in {len(COLLECTIONS)} collections, plus custom photo magnets and big orders for weddings and businesses.", "") + body + chrome_end(pg))


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
    extras = [(c, s) for c in COLLECTIONS for s in more_of(c)] + [(c, s) for c in MORE_COLLECTIONS for s in c["order"] + more_of(c) if has_art(c["slug"], s)]
    items += "\n" + "\n".join(product(pg, c, s, more=True) for c, s in extras)
    body = f"""{header(pg, "shop")}
<main id="main">
  <div class="wrap page-head">
    <ol class="crumbs"><li><a href="index.html">Home</a></li><li aria-current="page">Shop all</li></ol>
    <h1>All designs</h1>
    <p class="lede">Every magnet in the shop, {TOTAL_TEXT} designs in {len(COLLECTIONS)} collections. Pick a collection or search for a city, a sign or a saying.</p>
    <div class="head-row">
      <label class="search"><span class="visually-hidden">Search designs</span>
        <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="8.5" cy="8.5" r="6"/><path d="M13 13l5 5"/></svg>
        <input type="search" id="search" placeholder="Search designs" autocomplete="off">
      </label>
      {deal()} {vol_badge()}
      <span class="count" id="result-count" aria-live="polite" data-all="{TOTAL_TEXT} designs">{TOTAL_TEXT} designs</span>
    </div>
  </div>
{tabs_filters()}
  <section class="tight">
    <div class="wrap">
      <div class="fridge">
        <ul class="products four" id="all-products">
{items}
        </ul>
        {more_button(len(extras))}
        <p class="empty-results" id="no-results" hidden>No designs match that search. Try a city, a zodiac sign or a word like “coffee”, or <a id="no-results-idea" href="suggestions.html?kind=place">ask us to draw it</a>.</p>
      </div>
{idea_strip(pg, "Looking for something we don’t have yet?")}
    </div>
  </section>
</main>
{footer(pg)}"""
    write("shop.html", head(pg, "Shop all designs", f"All {TOTAL_TEXT} Little Hive House magnet designs. Filter by collection or search.", "shop.html") + body + chrome_end(pg))


def shop_designs():
    """Every design on sale, in shop order: [(collection, slug)] (the same set as shop.html)."""
    out = [(c, s) for c in COLLECTIONS for s in c["order"]] + [(c, s) for c in COLLECTIONS for s in more_of(c)]
    out += [(c, s) for c in MORE_COLLECTIONS for s in c["order"] + more_of(c) if has_art(c["slug"], s)]
    return out


def design_image(col_slug, slug):
    """The biggest picture of a design: the 1200 px print render when there is one, else the 600 px website WebP."""
    if (ROOT / f"assets/print/{col_slug}/{slug}.jpg").exists():
        return f"assets/print/{col_slug}/{slug}.jpg", 1200
    return f"assets/art/{col_slug}/{slug}.webp", 600


def design_text(col, t):
    return (f"{t}, a 2 x 2 inch fridge magnet from our {col['name']} collection. {col['blurb']} "
            "Printed, pressed and packed by hand, with a glossy front and a strong magnet back.")


TITLE_COUNT = {}   # design name -> how many design pages carry it (filled before the pages are written)


def page_product(col, slug, siblings):
    """m/<collection>/<slug>.html: one design on its own page (Google Shopping and search land here)."""
    pg = Page("../../")
    t = title_for(col, slug)
    img, size = design_image(col["slug"], slug)
    href = f'{pg.p}collections/{col["slug"]}.html'
    grp = PARENT.get(col["slug"]) or next((g for g in GROUPS if col["slug"] in g.get("all", [])), None)
    parent_crumb = f'<li><a href="{pg.p}collections/{grp["slug"]}.html">{E(grp["name"])}</a></li>' if grp else ""
    path = f'm/{col["slug"]}/{slug}.html'
    url = f"https://littlehivehouse.com/{path}"
    desc = design_text(col, t)
    ld = {
        "@context": "https://schema.org/", "@type": "Product", "name": f"{t} magnet", "sku": f'{col["slug"]}/{slug}',
        "image": f"https://littlehivehouse.com/{img}", "description": desc, "brand": {"@type": "Brand", "name": "Little Hive House"},
        "category": f'Fridge magnets > {col["name"]}',
        "offers": {"@type": "Offer", "url": url, "priceCurrency": "USD", "price": f"{PRICE:.2f}", "availability": "https://schema.org/InStock",
                   "itemCondition": "https://schema.org/NewCondition",
                   "shippingDetails": {"@type": "OfferShippingDetails",
                                       "shippingRate": {"@type": "MonetaryAmount", "value": f"{STORE_SHIPPING:.2f}", "currency": "USD"},
                                       "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "US"},
                                       "deliveryTime": {"@type": "ShippingDeliveryTime",
                                                        "handlingTime": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": 2, "unitCode": "DAY"},
                                                        "transitTime": {"@type": "QuantitativeValue", "minValue": 2, "maxValue": 5, "unitCode": "DAY"}}},
                   "hasMerchantReturnPolicy": {"@type": "MerchantReturnPolicy", "applicableCountry": "US",
                                               "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow", "merchantReturnDays": 30,
                                               "returnMethod": "https://schema.org/ReturnByMail", "returnFees": "https://schema.org/ReturnShippingFees"}},
    }
    import json as _json
    more = "\n".join(product(pg, col, x, show_col=False) for x in siblings)
    body = f"""{header(pg, "shop")}
<main id="main">
  <div class="wrap page-head">
    <ol class="crumbs"><li><a href="{pg.p}index.html">Home</a></li><li><a href="{pg.p}collections/index.html">Collections</a></li>{parent_crumb}<li><a href="{href}">{E(col["name"])}</a></li><li aria-current="page">{E(t)}</li></ol>
  </div>
  <section class="tight">
    <div class="wrap pdp">
      <div class="pdp-art fridge"><img class="mag" src="{pg.p}{img}" width="{size}" height="{size}" alt="{E(t)} fridge magnet" decoding="async"></div>
      <div class="pdp-info">
        <p class="eyebrow"><a href="{href}">{E(col["name"])}</a></p>
        <h1 translate="no">{E(t)}</h1>
        <p class="pdp-price">${PRICE} <span>2 × 2 in magnet</span></p>
        <div class="head-row">{deal()} {vol_badge()}</div>
        <button type="button" class="btn btn-honey" data-add="{col["slug"]}/{slug}" data-name="{E(t)}" data-collection="{E(col["name"])}" data-href="{href}">Add to cart</button>
        <p class="pdp-eta">Ships in 1–2 business days. Order today and it arrives <strong data-eta>in about a week</strong> in the US.</p>
        <p>{E(col["blurb"])}</p>
        <ul class="pdp-facts">
          <li>2 × 2 inch square with square corners</li>
          <li>Glossy front and a strong magnet back</li>
          <li>Printed, pressed and packed by hand, made to order</li>
          <li>Free US shipping on orders of ${STORE_FREE_SHIP_AT} or more</li>
        </ul>
      </div>
    </div>
  </section>
  <section class="tight">
    <div class="wrap">
      <div class="section-head">
        <div><p class="eyebrow">Pick a few more</p><h2>More from {E(col["name"])}</h2></div>
        <a class="btn btn-ghost btn-small" href="{href}">All {E(col["name"])} designs</a>
      </div>
      <div class="fridge">
        <ul class="products four">
{more}
        </ul>
      </div>
    </div>
  </section>
</main>
{footer(pg)}"""
    ld_tag = '<script type="application/ld+json">' + _json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + "</script>\n"
    # the same name in two collections (Paris in Places, Ink Cities and City Sketches): the page title names the collection
    page_title = f"{t} magnet · {col['name']}" if TITLE_COUNT.get(t.lower(), 0) > 1 else f"{t} magnet"
    html = head(pg, page_title, f"{t}: a handmade 2 x 2 in fridge magnet from the {col['name']} collection. ${PRICE}, ships in 1 to 2 business days.", path)
    html = html.replace("</head>", ld_tag + "</head>", 1)
    write(path, html + body + chrome_end(pg))


def page_products():
    """A page for every design on sale (m/<collection>/<slug>.html); old pages of designs no longer on sale are removed."""
    import shutil as _shutil
    live = shop_designs()
    by_col = {}
    for c, x in live:
        by_col.setdefault(c["slug"], (c, []))[1].append(x)
    TITLE_COUNT.clear()
    for c, x in live:
        k = title_for(c, x).lower()
        TITLE_COUNT[k] = TITLE_COUNT.get(k, 0) + 1
    for c, x in live:
        sib = [y for y in by_col[c["slug"]][1] if y != x]
        page_product(c, x, sib[:8])
    keep = {f'{c["slug"]}/{x}.html' for c, x in live}
    base = ROOT / "m"
    for f in base.glob("*/*.html"):
        if f"{f.parent.name}/{f.name}" not in keep:
            f.unlink()
    for d in base.glob("*"):
        if d.is_dir() and not any(d.iterdir()):
            _shutil.rmtree(d)


def feed_id(col_slug, slug):
    """The product id in the Google feed: "<collection>-<design>", at most 50 characters (Google's limit);
    a longer one keeps its start and gets a short fixed code, so it never changes between builds."""
    pid = f"{col_slug}-{slug}"
    if len(pid) <= 50:
        return pid
    import hashlib as _h
    return pid[:41].rstrip("-") + "-" + _h.sha1(pid.encode()).hexdigest()[:8]


def feed_jpg(img):
    """Facebook/Instagram only take JPG or PNG: a WebP design gets a JPG twin under assets/feed/ (made once, redone when the art changes)."""
    if not img.endswith(".webp"):
        return img
    src = ROOT / img
    rel = "assets/feed/" + img[len("assets/art/"):-len(".webp")] + ".jpg"
    out = ROOT / rel
    if not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
        from PIL import Image as _Im
        out.parent.mkdir(parents=True, exist_ok=True)
        im = _Im.open(src).convert("RGB")
        im.save(out, "JPEG", quality=88, optimize=True, progressive=True)
    return rel


def _sale_tags(price):
    """Google/Meta feed: the store-wide sale price (catalog.py SALE, the % of the week) with its dates, so the feed
    and the crossed-out price on the page agree. Nothing once the sale is over."""
    import datetime as _dt
    if not SALE or _dt.datetime.now(_dt.timezone.utc) >= _dt.datetime.fromisoformat(SALE["end"].replace("Z", "+00:00")):
        return ""
    sp = round(price * (100 - SALE["pct"]) / 100, 2)
    return f"    <g:sale_price>{sp:.2f} USD</g:sale_price>\n    <g:sale_price_effective_date>{SALE['start'].replace('Z', '+00:00')}/{SALE['end'].replace('Z', '+00:00')}</g:sale_price_effective_date>\n"


def write_google_feed():
    """google-products.xml: every design (and the photo packs) for Google Merchant Center, read by Google every day."""
    site = "https://littlehivehouse.com/"
    def item(pid, title, desc, link, image, price, ptype, label):
        return ("  <item>\n"
                f"    <g:id>{E(pid)}</g:id>\n    <g:title>{E(title)}</g:title>\n    <g:description>{E(desc)}</g:description>\n"
                f"    <g:link>{E(link)}</g:link>\n    <g:image_link>{E(image)}</g:image_link>\n"
                f"    <g:availability>in_stock</g:availability>\n    <g:price>{price:.2f} USD</g:price>\n" + _sale_tags(price) +
                "    <g:condition>new</g:condition>\n    <g:brand>Little Hive House</g:brand>\n    <g:identifier_exists>no</g:identifier_exists>\n"
                "    <g:google_product_category>696</g:google_product_category>\n"
                f"    <g:product_type>{E(ptype)}</g:product_type>\n    <g:custom_label_0>{E(label)}</g:custom_label_0>\n"
                "    <g:shipping_weight>1 oz</g:shipping_weight>\n"
                "  </item>")
    rows = []
    ids = {}   # feed id -> [cart id, name, collection]: Instagram/Facebook send these ids to the checkout link (assets/site.js)
    for c, x in shop_designs():
        t = title_for(c, x)
        ftitle = f"{t} Fridge Magnet, Handmade 2x2 in, {c['name']} Collection"[:150]
        ids[feed_id(c["slug"], x)] = [f'{c["slug"]}/{x}', t, c["name"], ftitle]   # [cart id, name, collection, catalog title]
        img, _ = design_image(c["slug"], x)
        img = feed_jpg(img)
        grp = PARENT.get(c["slug"]) or next((g for g in GROUPS if c["slug"] in g.get("all", [])), None)
        ptype = "Fridge magnets > " + (f'{grp["name"]} > ' if grp else "") + c["name"]
        rows.append(item(feed_id(c["slug"], x), ftitle, design_text(c, t),
                         f'{site}m/{c["slug"]}/{x}.html', site + img, PRICE, ptype, c["name"]))
    from photo_pack_images import ensure as _packs
    pack_img = _packs([n for n, _ in STORE_PHOTO_PACKS])   # a square picture per pack (the wide site banner got cut off)
    for n, price in STORE_PHOTO_PACKS:
        rows.append(item(f"photo-pack-{n}", f"Custom Photo Magnets, Pack of {n}, Personalized 2x2 in Fridge Magnets",
                         f"{n} glossy 2 x 2 inch fridge magnets made by hand from your own photos, with a frame and a caption if you like. "
                         "Printed, pressed and packed by hand, ships in 1 to 2 business days.",
                         f"{site}photo-magnets.html", site + pack_img[n], price, "Fridge magnets > Photo magnets", "Photo magnets"))
    # the bulk-order packages, so they can be tagged in posts and bought from the Instagram/Facebook shop
    BULK = {"business": ("Custom Logo Magnets for Business", "For Business", "business.html"),
            "weddings": ("Custom Wedding Magnets, Save the Dates or Favors", "Weddings", "weddings.html"),
            "graduation": ("Custom Graduation & College Magnets", "Graduation & College", "graduation.html"),
            "parties": ("Custom Party & Event Favor Magnets", "Parties & Events", "parties.html"),
            "teams": ("Custom Team & School Magnets", "Teams & Schools", "big-orders.html")}
    for title, key, desc, tiers, _ in PACKAGES:
        pid = PACKAGE_IDS[key]
        if pid not in BULK:
            continue
        name, cat, page = BULK[pid]
        for n, price in tiers:
            fid = f"pkg-{pid}-{n}"
            ftitle = f"{name}, Pack of {n}, Handmade 2x2 in"
            ids[fid] = [f"{pid}-{n}", f"{title}, {n} magnets", cat, ftitle, "package", n, price]
            rows.append(item(fid, ftitle, f"{desc} {n} glossy 2 x 2 inch magnets designed with you for free: you approve a proof before we print. "
                             "Pressed and packed by hand, ships 3 to 5 business days after the proof.",
                             f"{site}{page}#packs", f"{site}assets/feed/bulk/{pid}.jpg", price, f"Fridge magnets > {cat}", cat))
    # the design studio's designs: one product per kind of business and per Personalize theme (their pictures:
    # tools/feed_custom_images.py), so they show on Google and can be tagged in Instagram posts
    fdir = ROOT / "assets" / "feed" / "custom"
    btitle, _bk, _bd, btiers, _bp = next(p for p in PACKAGES if p[1] == "Business")
    bn, bprice = btiers[0]
    for k in KITS.K:
        fid = f"biz-{k['key']}"
        if not (fdir / f"{fid}.jpg").exists():
            continue
        ftitle = (f"Custom {k['name']} Magnets with Your Logo, Pack of {bn}, Handmade 2x2 in" if k["group"] != KITS.G_OTHER
                  else f"Custom Business Magnets with Your Logo, {k['name']}, Pack of {bn}, Handmade 2x2 in")[:150]
        ids[fid] = [f"business-{bn}", f"{btitle}, {bn} magnets", "For Business", ftitle, "package", bn, bprice]
        rows.append(item(fid, ftitle, f"{BIZ_DESIGNS.SET_N.get(k['key'], 0)} ready-made designs for a {k['name'].lower()}: coupons, your number, QR codes, "
                         f"photo designs and elegant logo designs. Pick one and make it yours: your colors, your words, your logo. {bn} glossy 2 x 2 inch "
                         "magnets; you approve a proof before we print. Pressed and packed by hand.",
                         f"{site}business.html#kind-{k['key']}", f"{site}assets/feed/custom/{fid}.jpg", bprice, f"Fridge magnets > For Business > {k['name']}", "For Business"))
    ptitle, _pk, _pd, ptiers, _pp = PERSONAL
    pn, pprice = ptiers[0]
    for key, meta in BIZ_DESIGNS.SETS.items():
        if meta["page"] != "personalize":
            continue
        fid = f"pz-{key[2:]}"
        if not (fdir / f"{fid}.jpg").exists():
            continue
        ftitle = f"Personalized Magnet, {meta['name']}, Custom 2x2 in Fridge Magnet, Handmade"[:150]
        ids[fid] = [f"personal-{pn}", f"{ptitle}, 1 magnet", "Personalized", ftitle, "package", pn, pprice]
        rows.append(item(fid, ftitle, f"{BIZ_DESIGNS.SET_N.get(key, 0)} designs to make yours: {meta['name'].lower()}. Change the words and the colors, add your photo, "
                         "and we send you a proof before we print. A glossy 2 x 2 inch magnet, pressed and packed by hand.",
                         f"{site}personalize.html#kind-{key}", f"{site}assets/feed/custom/{fid}.jpg", pprice, f"Fridge magnets > Personalized > {meta['name']}", "Personalized"))
    import json as _json
    write("assets/feed-ids.json", _json.dumps(ids, separators=(",", ":"), ensure_ascii=False) + "\n")
    write("google-products.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">\n<channel>\n'
          "  <title>Little Hive House</title>\n  <link>https://littlehivehouse.com/</link>\n  <description>Handmade fridge magnets</description>\n"
          + "\n".join(rows) + "\n</channel>\n</rss>\n")


def page_collections_index():
    pg = Page("../")
    cards = "\n".join(col_card(pg, c) for c in top_level())
    extra_cols = [c for c in MORE_COLLECTIONS if c["slug"] not in HERITAGE_ALL]
    cards += "\n" + "\n".join(col_card(pg, c).replace("<li", "<li data-more hidden", 1) for c in extra_cols)
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
      {more_button(len(extra_cols), "collections")}
    </div>
  </section>
</main>
{footer(pg)}"""
    write("collections/index.html", head(pg, "Collections", "Browse every Little Hive House magnet collection.", "collections/") + body + chrome_end(pg))


def page_group(g):
    pg = Page("../")
    kids = group_kids(g)
    n = sum(count(k) for k in kids)
    chips = "".join(f'<a class="tab" href="{k["slug"]}.html">{E(k["name"])} <small>{count(k)}</small></a>' for k in kids)
    cards = "\n".join(col_card(pg, k) for k in kids)
    extra_kids = [c for c in MORE_COLLECTIONS if c["slug"] in g.get("all", [])]
    cards += "\n" + "\n".join(col_card(pg, k).replace("<li", "<li data-more hidden", 1) for k in extra_kids)
    rows = []
    for k in kids:
        items = "\n".join(product(pg, k, s, show_col=False) for s in k["order"][:8])
        rows.append(f"""  <section class="tight">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="eyebrow">{E(k["tag"])}</p>
          <h2>{E(k["name"])}</h2>
        </div>
        <a class="btn btn-ghost btn-small" href="{k["slug"]}.html">See all {count(k)}</a>
      </div>
      <div class="fridge">
        <ul class="products">
{items}
        </ul>
      </div>
{idea_strip(pg)}
    </div>
  </section>""")
    body = f"""{header(pg, "collections")}
<main id="main">
  <div class="wrap page-head">
    <ol class="crumbs"><li><a href="../index.html">Home</a></li><li><a href="index.html">Collections</a></li><li aria-current="page">{E(g["name"])}</li></ol>
    <p class="eyebrow">{E(g["tag"])}</p>
    <h1>{E(g["name"])}</h1>
    <p class="lede">{E(g["blurb"])}</p>
    <div class="head-row">{deal()} {vol_badge()}<span class="count">{len(kids)} countries · {n} designs · ${PRICE} each</span></div>
  </div>
<div class="tabs-bar">
  <nav class="wrap tabs" aria-label="{E(g["name"])} collections">
    {chips}
  </nav>
</div>
  <section class="tight">
    <div class="wrap">
      <ul class="col-grid">
{cards}
      </ul>
      {more_button(len(extra_kids), "countries")}
    </div>
  </section>
{chr(10).join(rows)}
</main>
{footer(pg)}"""
    write(f"collections/{g['slug']}.html",
          head(pg, f"{g['name']} magnets", f"{g['name']}: {g['blurb']}", f"collections/{g['slug']}.html") + body + chrome_end(pg))


def page_collection(col):
    pg = Page("../")
    items = "\n".join(product(pg, col, s, show_col=False) for s in col["order"])
    extra = more_of(col)
    items += "\n" + "\n".join(product(pg, col, s, show_col=False, more=True) for s in extra)
    idx = COLLECTIONS.index(col) if col in COLLECTIONS else -1
    others = [COLLECTIONS[(idx + k) % len(COLLECTIONS)] for k in (1, 2, 3)]
    more = "\n".join(col_card(pg, c) for c in others)
    grp = PARENT.get(col["slug"]) or next((g for g in GROUPS if col["slug"] in g.get("all", [])), None)
    parent_crumb = f'<li><a href="{grp["slug"]}.html">{E(grp["name"])}</a></li>' if grp else ""
    if grp:
        more = "\n".join(col_card(pg, c) for c in group_kids(grp) if c is not col)
    body = f"""{header(pg, "collections")}
<main id="main">
  <div class="wrap page-head">
    <ol class="crumbs"><li><a href="../index.html">Home</a></li><li><a href="index.html">Collections</a></li>{parent_crumb}<li aria-current="page">{E(col["name"])}</li></ol>
    <p class="eyebrow">{E(col["tag"])}</p>
    <h1>{E(col["name"])}</h1>
    <p class="lede">{E(col["blurb"])}</p>
    <div class="head-row">{deal()} {vol_badge()}<span class="count">{count(col)} designs · ${PRICE} each</span></div>
  </div>
{tabs_links(pg, col["slug"])}
  <section class="tight">
    <div class="wrap">
      <div class="fridge">
        <ul class="products">
{items}
        </ul>
      </div>
      {more_button(len(extra))}
{idea_strip(pg)}
    </div>
  </section>
  <section class="tight">
    <div class="wrap">
      <div class="section-head">
        <div>
          <p class="eyebrow">Keep exploring</p>
          <h2>{("More from " + E(grp["name"])) if grp else "More collections"}</h2>
        </div>
        <a class="btn btn-ghost btn-small" href="{(grp["slug"] + ".html") if grp else "index.html"}">{("All of " + E(grp["name"])) if grp else "All collections"}</a>
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
    import json as _json
    _frames = _json.loads((ROOT / "assets" / "frames" / "frames.json").read_text(encoding="utf-8"))
    _groups = []
    for f in _frames:
        if not f.get("hidden") and f["group"] not in _groups:
            _groups.append(f["group"])
    # a few frames shown on a sample picture before any photo is added
    teaser_ids = ["instant", "wedding", "arch", "botanical", "postcard", "holly"]
    _by_id = {f["id"]: f for f in _frames}
    frame_teaser = "\n".join(
        f'            <li><span class="fprev"><svg viewBox="0 0 600 600" aria-hidden="true"><image href="{pg.p}assets/frames/sample.svg" '
        f'x="{_by_id[i]["window"][0]}" y="{_by_id[i]["window"][1]}" width="{_by_id[i]["window"][2]}" height="{_by_id[i]["window"][3]}" preserveAspectRatio="xMidYMid slice"/>'
        f'<image href="{pg.p}assets/frames/{i}.svg" width="600" height="600"/></svg></span><span class="fname">{E(_by_id[i]["name"])}</span></li>'
        for i in teaser_ids if i in _by_id)
    group_chips = "".join(f'<button type="button" class="chip" data-group="{E(g)}" aria-pressed="false">{E(g)}</button>' for g in _groups)
    frames_js = _json.dumps({"list": _frames, "groups": _groups}, separators=(",", ":"), ensure_ascii=False)
    body = f"""{header(pg, "photo")}
<main id="main">
  <div class="wrap page-head">
    <ol class="crumbs"><li><a href="index.html">Home</a></li><li aria-current="page">Photo magnets</li></ol>
    <h1>Your photos, on the fridge</h1>
    <p class="lede">Glossy 2 × 2 inch magnets made from your own pictures. Kids, pets, trips, grandparents: everyone gets a spot on the fridge.</p>
    <ul class="ideas" aria-label="Photo magnet ideas">
{chr(10).join(f'      <li><a href="?frame={frame}#custom">{showcase_img(pg, oid, 1, lazy=False)}<span>{E(title)}</span></a></li>' for oid, title, _, frame, _n in OCCASIONS)}
    </ul>
    <a class="biz-hook photo-hook" href="personalize.html#kind-p-photo"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="5" width="16" height="12" rx="2"/><circle cx="10" cy="11" r="3.2"/><path d="M7 5l1.4-2h3.2L13 5"/></svg><span><strong>Want words on your photo?</strong> <span class="bh-more">{BIZ_DESIGNS.SET_N.get("p-photo", 0)} photo designs with names, dates and captions</span></span><span class="bh-arrow" aria-hidden="true">→</span></a>
  </div>
  <section class="tight" id="custom">
    <div class="wrap custom-grid">
      <div>
        <ol class="steps">
          <li><div><h3>Upload your photos</h3><p>Pick your favorite pictures from your phone or computer, then tap each one to give it its own frame and caption.</p></div></li>
          <li><div><h3>Choose how many</h3><p>Pick a pack, or add as many photos as you like, from 1 to 100. Square magnets, each 2 × 2 inches with a glossy finish. Mix them with any of our designs in the same order.</p></div></li>
          <li><div><h3>We make and ship them</h3><p>We print, press and pack every magnet by hand, then send them to your door.</p></div></li>
        </ol>
        <p class="note">Professional photos belong to the photographer. Only upload pictures you took yourself or have permission to print.</p>
      </div>

      <form class="builder" id="builder" novalidate data-pricing='{photo_pricing_json()}'>
        <fieldset>
          <legend>How many magnets</legend>
          <div class="packs">
            <div class="pack"><input type="radio" name="pack" id="pack-1" value="1" data-price="{STORE_PHOTO_EXTRA[0]:g}"><label for="pack-1"><strong>1 to 3</strong><span>${STORE_PHOTO_EXTRA[0]:g} each</span></label></div>
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
        <div class="magnets">
          <div class="magnets-head">
            <p class="label" id="magnets-label">Your magnets</p>
            <p class="magnets-hint" id="magnets-hint" hidden>Tap a photo to choose its frame and caption.</p>
          </div>
          <div class="frame-teaser" id="frame-teaser">
            <p>{len(_frames)} frames to choose from, photo by photo: classic mats, hand-painted florals, holidays, birthdays and more.</p>
            <ul aria-label="A few of the frames">
{frame_teaser}
            </ul>
          </div>
          <ul class="thumbs" id="thumbs" aria-labelledby="magnets-label"></ul>
          <p class="counter" id="counter" aria-live="polite">0 of 9 photos added</p>
          <button type="button" class="fit-photos" id="fit-photos" hidden></button>
          <p class="more-photos" id="more-photos" aria-live="polite" hidden></p>
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
      <dialog class="studio" id="studio" aria-labelledby="studio-title">
        <div class="studio-head">
          <button type="button" class="icon-btn" id="studio-prev" aria-label="Previous photo">&#8249;</button>
          <h2 id="studio-title">Photo 1 of 1</h2>
          <button type="button" class="icon-btn" id="studio-next" aria-label="Next photo">&#8250;</button>
          <button type="button" class="icon-btn studio-x" id="studio-close" aria-label="Close frame picker">&#215;</button>
        </div>
        <div class="studio-body">
          <div class="studio-preview">
            <div class="studio-mag" id="studio-mag"></div>
            <p class="studio-fname"><strong id="studio-fname">No border</strong> <span id="studio-blurb"></span></p>
            <div class="studio-adjust" id="studio-adjust">
              <div class="zoom-row">
                <label class="label" for="studio-zoom">Zoom</label>
                <input type="range" id="studio-zoom" min="1" max="4" step="0.01" value="1" aria-describedby="adjust-help">
                <button type="button" class="linkish" id="adjust-reset">Reset</button>
              </div>
              <p class="cap-help" id="adjust-help">Drag the photo to move it. Pinch or slide to zoom.</p>
            </div>
            <div class="studio-cap" id="studio-cap-row" hidden>
              <label class="label" for="studio-cap" id="studio-cap-label">Caption</label>
              <input type="text" id="studio-cap" maxlength="24" autocomplete="off" aria-describedby="studio-cap-help">
              <p class="cap-help" id="studio-cap-help"><span id="studio-cap-count">0/24</span> · Optional, leave empty for none</p>
              <div class="chips cap-styles" id="cap-styles" role="group" aria-label="Lettering" hidden></div>
              <button type="button" class="linkish" id="cap-all" hidden>Use this caption on all photos</button>
            </div>
          </div>
          <div class="studio-pick">
            <div class="chips" role="group" aria-label="Frame styles"><button type="button" class="chip" data-group="" aria-pressed="true">All</button>{group_chips}</div>
            <fieldset class="swatches" id="swatches">
              <legend class="visually-hidden" id="swatch-legend">Frame for this photo</legend>
            </fieldset>
          </div>
        </div>
        <div class="studio-foot">
          <p class="studio-status" id="studio-status" role="status"></p>
          <button type="button" class="btn btn-ghost btn-small" id="apply-all">Apply this frame to all photos</button>
          <button type="button" class="btn btn-honey btn-small" id="studio-done">Done</button>
        </div>
      </dialog>
    </div>
  </section>

  <section class="tight">
    <div class="wrap">
      <div class="section-head"><div><p class="eyebrow">Good to know</p><h2>Photo magnet questions</h2></div></div>
      <div class="faq">
        <details><summary>What size are the magnets?</summary><p>Each magnet is a 2 × 2 inch square with square corners, a glossy front and a strong magnet back.</p></details>
        <details><summary>Which photos work best?</summary><p>Use the original photo from your camera roll. Screenshots and photos saved from chat apps are often too small and print blurry; the builder warns you when a photo looks too small.</p></details>
        <details><summary>Can every photo have a different frame?</summary><p>Yes. Tap any photo in the builder to pick its own frame and caption, or use "Apply this frame to all photos" to frame the whole pack the same way in one tap.</p></details>
        <details><summary>Will you crop my photos?</summary><p>Yes, every photo is cropped to a square. Tell us in the notes if someone must stay in the frame and we will crop around them.</p></details>
        <details><summary>How long does it take?</summary><p>Most packs ship within 1 to 2 business days. Shipping is $5.49 and free on US orders over $35.</p></details>
        <details><summary>Can I mix my photos with your designs?</summary><p>Yes. Add photo packs and any designs from the <a href="shop.html">shop</a> to the same cart. Orders with 20 or more magnets get 10% off automatically, 50 or more get 20% off and 100 or more get 25% off.</p></details>
        <details><summary>Need a custom design for an event?</summary><p>See our <a href="big-orders.html">big order packages</a> for weddings, parties, teams and businesses.</p></details>
      </div>
    </div>
  </section>
</main>
{footer(pg)}"""
    body += f'\n<script>window.LHH_FRAMES={frames_js};window.LHH_FRAMES_BASE="{pg.p}assets/frames/";</script>'
    write("photo-magnets.html", head(pg, "Custom photo magnets", "Custom 2 × 2 inch photo magnets from your own pictures, with or without a frame. Any number from 1 to 100.", "photo-magnets.html") + body + chrome_end(pg, ("custom.js",)))


PACKAGES = [
    ("Weddings & save the dates", "Weddings", "Favors with your names and date, or save-the-date photo magnets for every guest.",
     [(25, 55), (50, 95), (100, 175), (150, 250)], 100),
    ("Business & real estate", "Business", "Your logo or listing on the fridge all year. A favorite closing gift for realtors and a cheap, lasting ad for small businesses.",
     [(50, 90), (100, 160), (250, 350), (500, 650)], 100),
    ("Parties & events", "Party or event", "Holiday office parties, baby showers, quinceañeras, birthdays, reunions and memorials. A keepsake every guest takes home.",
     [(20, 45), (40, 80), (75, 140), (150, 260)], 40),
    ("Graduation & college", "Graduation", "Grad party favors, welcome-week giveaways, club and sorority keepsakes and class reunions.",
     [(25, 55), (50, 95), (100, 170), (250, 375)], 50),
    ("Teams & schools", "Team or school", "A magnet for every player, student or teacher, with their photo, name and number.",
     [(12, 30), (20, 48), (30, 69)], 20),
]


# Personalize (personalize.html): one magnet or a few, with their family name, pet, baby... (not a bulk order)
PERSONAL = ("Personalized magnets", "Personal", "Your family name, your pet, your baby or your trip, made in the design studio.",
            [(1, 6), (2, 10), (4, 18), (10, 39)], 1)

# store: package ids used by the cart, catalog.json and createCheckout ("weddings-50")
PACKAGE_IDS = {"Weddings": "weddings", "Business": "business", "Party or event": "parties", "Team or school": "teams", "Graduation": "graduation",
               "Mailing": "mailing", "Personal": "personal"}
from occasions import MAILING, OCCASIONS as BULK_PAGES   # noqa: E402  the bulk-order pages (tools/occasions.py)
import biz_designs as BIZ_DESIGNS   # noqa: E402  the design gallery and studio (tools/biz_designs.py, assets/designer.js)
import design_kits as KITS   # noqa: E402  the kinds of business and the Personalize themes (tools/design_kits.py)


def pkg_card(title, key, desc, tiers, pick, unit="magnets", styles=None):
    """A buyable package: the tiers (cart line kind "package", id like "business-100"), Buy now and Ask for a quote.
    unit "addresses": the mailing service (no magnets). styles: [(slug, name)] the example designs to start from."""
    pid = PACKAGE_IDS[key]
    chosen = min(tiers, key=lambda t: abs(t[0] - pick))[0]
    size = (lambda n: 0) if unit == "addresses" else (lambda n: n)
    rows = "".join(
        f'<label class="tier"><input type="radio" name="pkg-{pid}" value="{pid}-{n}" data-size="{size(n)}" data-price="{p}" data-title="{E(title)}"'
        f'{f" data-addresses={chr(34)}{n}{chr(34)}" if unit == "addresses" else ""}'
        f'{" checked" if n == chosen else ""}><span class="t-n">{n} {unit}</span><span class="t-p">${p}</span><span class="t-e">${p / n:.2f} each</span></label>'
        for n, p in tiers)
    price = dict(tiers)[chosen]
    pick_style = ""
    if styles:
        if styles and len(styles[0]) == 3:   # (slug, title, group): one group per kind of business
            groups = {}
            for sl, nm, g in styles: groups.setdefault(g, []).append((sl, nm))
            opts = "".join(f'<optgroup label="{E(g)}">' + "".join(f'<option value="{E(sl)}">{E(nm)}</option>' for sl, nm in v) + "</optgroup>" for g, v in groups.items())
        else:
            opts = "".join(f'<option value="{E(sl)}">{E(nm)}</option>' for sl, nm in styles)
        pick_style = (f'<div class="field pkg-style"><label for="st-{pid}">Start from a style</label>'
                      f'<select id="st-{pid}" data-pkg-style><option value="">We design it with you</option>{opts}'
                      f'<option value="own">My own logo or design (send it after checkout)</option></select></div>')
    quote = "" if unit == "addresses" else f'<button type="button" class="btn btn-ghost btn-small" data-pkg="{E(key)}" data-qty="{chosen}">Ask for a quote</button>'
    note = ("Add it next to a magnet package of the same size. After checkout we ask for your list and mail each one for you."
            if unit == "addresses" else "After checkout we email you within one business day to plan the design. You approve a proof before we print.")
    return f"""<li class="pkg" data-package="{pid}">
          <h3>{E(title)}</h3>
          <p>{E(desc)}</p>
          <fieldset class="tier-pick">
            <legend class="visually-hidden">Pack size for {E(title)}</legend>
            <div class="tier-head" aria-hidden="true"><span>Pack</span><span>Price</span><span>Per {"address" if unit == "addresses" else "magnet"}</span></div>
            {rows}
          </fieldset>
          {pick_style}
          <div class="pkg-actions">
            <button type="button" class="btn btn-honey btn-small" data-buy-package>Buy now · ${price}</button>
            {quote}
          </div>
          <p class="pkg-note">{note}</p>
        </li>"""


def page_big():
    pg = Page("")
    cards = [pkg_card(title, key, desc, tiers, pick) for title, key, desc, tiers, pick in PACKAGES]
    who = "".join(f'<li><a href="{o["slug"]}.html"><img src="assets/occasions/{o["ideas"][0][0]}.webp" alt="" width="600" height="600" loading="lazy">'
                  f'<strong>{E(o["name"])}</strong><span>{E(o["eyebrow"])}</span></a></li>' for o in BULK_PAGES)
    options = "<option>Mix &amp; match</option>" + "".join(f"<option>{E(k)}</option>" for _, k, _, _, _ in PACKAGES) + "<option>Something else</option>"
    vol_rows = "".join(f"<li><strong>{n}+ magnets</strong><span>{pct}% off designs and photo magnets</span></li>" for n, pct in reversed(VOLUME))
    body = f"""{header(pg, "big")}
<main id="main">
  <div class="wrap page-head">
    <ol class="crumbs"><li><a href="index.html">Home</a></li><li aria-current="page">Bulk orders</li></ol>
    <h1>Bulk orders, made by hand</h1>
    <p class="lede">Wedding favors, save the dates, logo magnets and party keepsakes. Every package includes a custom design with your names, date, logo or photos, and a proof to approve before we print. Buy a package now and we plan the design together after checkout, or ask us for a quote first.</p>
    <ul class="occ-who">{who}</ul>
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
        <li><strong>Free US shipping</strong><span>On every order over $35.</span></li>
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
        <details><summary>How long do big orders take?</summary><p>Most big orders ship 3 to 5 business days after you approve the proof. Need them sooner? Ask us and we will tell you honestly if we can make it.</p></details>
        <details><summary>Can I use your designs instead of my own?</summary><p>Yes. Any design from the shop can be ordered in bulk at package prices, and we can add your names or date to most of them.</p></details>
        <details><summary>Do you have envelopes for save the dates?</summary><p>Yes, kraft envelopes can be added for $0.25 each. Postage is not included.</p></details>
        <details><summary>How much is shipping?</summary><p>Shipping in the US is $5.49 and free on orders over $35, so almost every big order ships free.</p></details>
        <details><summary>What is the smallest order?</summary><p>Packages start at 12 magnets. For smaller sets, use our <a href="photo-magnets.html">photo magnet packs</a> or the <a href="shop.html">shop</a>.</p></details>
      </div>
    </div>
  </section>
</main>
{footer(pg)}"""
    write("big-orders.html", head(pg, "Big orders", "Custom magnet packages for weddings, businesses, parties, teams and schools. Custom design and proof included.", "big-orders.html") + body + chrome_end(pg, ("quote.js",)))


def occ_img(pg, slug, cls="", lazy=True, size=600):
    """An example magnet: ours in assets/occasions/, or "sc:<name>" for a photo-magnet sample in assets/showcase/."""
    src = f"assets/showcase/{slug[3:]}.webp" if slug.startswith("sc:") else f"assets/occasions/{slug}.webp"
    return f'<img src="{pg.p}{src}" alt="" width="{size}" height="{size}"{" loading=" + chr(34) + "lazy" + chr(34) if lazy else ""} decoding="async"{(" class=" + chr(34) + cls + chr(34)) if cls else ""}>'


# the studio design as a file only (no magnet), emailed after payment (studio.js, pricing.js)
DIGITAL_TITLE, DIGITAL_PRICE = "Design file (digital, no magnet)", 4.99
DESIGN_GALLERY = BIZ_DESIGNS.GALLERY   # (slug, page, group, title): tools/biz_designs.py


def studio_html(pg, page, pkg, who):
    """The design gallery, like a streaming app: kinds of business (or Personalize themes) grouped, a search box, and for
    the kind they pick, rows of designs by what the magnet is for (assets/studio.js fills the rows from
    assets/designs/<set>.json). Then the studio dialog where a design is made theirs."""
    sets = {k: v for k, v in BIZ_DESIGNS.SETS.items() if v["page"] == page}
    n_all = BIZ_DESIGNS.COUNTS.get(page, 0)
    GICON = {KITS.G_FOOD: "pizza", KITS.G_HEALTH: "tooth", KITS.G_HOME: "house", KITS.G_MONEY: "key", KITS.G_BEAUTY: "scissors", KITS.G_PETS: "paw",
             KITS.G_AUTO: "car", KITS.G_COMM: "church", KITS.G_SHOPS: "flower", KITS.G_OTHER: "star"}

    def kind(k, v):
        return (f'<button type="button" class="dz-kind" data-set="{k}" data-group="{E(v["group"])}" data-words="{E(v.get("words", ""))}">'
                f'<span class="dz-ki" data-il="{E(v.get("il", ""))}" data-icon="{E(v["icon"])}" aria-hidden="true"></span>'
                f'<span class="dz-kn">{E(v["name"])}</span><small>{BIZ_DESIGNS.SET_N.get(k, 0)} designs</small></button>')
    kinds = "".join(kind(k, v) for k, v in sets.items())
    many = len(sets) > 1
    grouped = page == "business"
    groups = ""
    if grouped:
        gs = []
        for v in sets.values():
            if v["group"] not in gs: gs.append(v["group"])
        groups = "".join(
            f'<button type="button" class="dz-grp" data-dz-grp="{E(g)}"><span class="dz-gi" data-icon="{GICON.get(g, "star")}" aria-hidden="true"></span>'
            f'<span class="dz-gn">{E(g)}</span><small>{sum(1 for v in sets.values() if v["group"] == g)} kinds · '
            f'{sum(BIZ_DESIGNS.SET_N.get(k, 0) for k, v in sets.items() if v["group"] == g)} designs</small></button>' for g in gs)
    ask = {"business": "What kind of business?", "personalize": "What would you like on your fridge?"}.get(page, "")
    hint = {"business": "Type your business: church, pizza, dentist…", "personalize": "Type: dog, grandma, baby, family name…"}.get(page, "")
    title, _key, _d, tiers, pick = pkg
    pid = PACKAGE_IDS[_key]
    chosen = min(tiers, key=lambda t: abs(t[0] - pick))[0]
    unit = lambda n: "magnet" if n == 1 else "magnets"
    packs = "".join(f'<option value="{pid}-{n}" data-size="{n}" data-price="{pr}" data-title="{E(title)}"{" selected" if n == chosen else ""}>{n} {unit(n)} · ${pr}'
                    f'{f" (${pr / n:.2f} each)" if n > 1 else ""}</option>' for n, pr in tiers)
    pals = "".join(f'<button type="button" class="dz-pal" data-pal="{k}" aria-label="{E(k)}" style="--a:{v["bg"]};--b:{v["ac"]};--c:{v["ink"]}"></button>' for k, v in BIZ_DESIGNS.P.items())
    pick_html = ""
    if many:
        pick_html = f"""
      <div class="dz-pick" data-dz-home>
        <h3 class="dz-ask">{ask}</h3>
        <div class="dz-search"><svg viewBox="0 0 20 20" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="9" cy="9" r="6"/><path d="M14 14l4 4"/></svg><input type="search" data-dz-search placeholder="{hint}" aria-label="{hint}" autocomplete="off"></div>
        <p class="dz-none" data-dz-none hidden>We don’t have that one yet. Start from one of these designs for any business and change the words, or ask us for a free design below.</p>
        {f'<div class="dz-grps" data-dz-grps>{groups}</div>' if grouped else ""}
        <div class="dz-kinds-box" data-dz-kinds-box{" hidden" if grouped else ""}>
          {'<div class="dz-crumb"><button type="button" class="dz-back" data-dz-back>← All kinds</button><h3 data-dz-ktitle></h3></div>' if grouped else ""}
          <div class="dz-kinds" data-dz-kinds>{kinds}</div>
        </div>
      </div>
      <div class="dz-feat" data-dz-feat></div>"""
    first = next(iter(sets), "")
    return f"""  <section class="tight" id="designs" data-gallery data-page="{page}"{"" if many else f' data-dz-only="{first}"'}>
    <div class="wrap">
      <div class="section-head"><div><p class="eyebrow">Design studio</p><h2>Pick a design, make it yours</h2></div><p>{n_all:,} ready-made designs for {who}. Tap one to change the colors and the words{", add your logo" if page == "business" else ", add your photo"} and see it right away.</p></div>{pick_html}
      <div class="dz-view" data-dz-view{" hidden" if many else ""}>
        {'<div class="dz-crumb"><button type="button" class="dz-back" data-dz-up>← Back</button><h3 data-dz-vtitle></h3></div>' if many else ""}
        <div class="dz-rows" data-dz-rows><p class="hint">Loading the designs…</p></div>
      </div>
    </div>
  </section>
  <dialog class="dz" data-studio aria-labelledby="dz-title">
    <div class="dz-head"><p class="eyebrow">Design studio</p><h2 id="dz-title" data-dz-title></h2><button type="button" class="dz-x" data-dz-close aria-label="Close">×</button></div>
    <div class="dz-body">
      <div class="dz-left"><div class="dz-prev" data-dz-prev></div><p class="hint">Your magnet, 2 × 2 inches. We email you a proof before we print.</p></div>
      <div class="dz-right">
        <div class="dz-sec"><h3>Colors</h3>
          <div class="dz-pals"><button type="button" class="dz-orig" data-dz-orig aria-pressed="true">Original</button>{pals}</div>
          <div class="dz-picks"><label>Background <input type="color" data-dz-c="bg"></label><label>Text <input type="color" data-dz-c="ink"></label><label>Accent <input type="color" data-dz-c="ac"></label></div></div>
        <div class="dz-sec"><h3>Words</h3><div class="dz-fields" data-dz-fields></div></div>
        <div class="dz-sec"><h3>Your logo</h3>
          <div class="dz-up"><label class="btn btn-ghost btn-small">Upload your logo<input type="file" accept="image/*" data-dz-logo hidden></label><span class="hint" data-dz-logo-name></span><button type="button" class="linkish" data-dz-nologo hidden>Remove</button></div>
          <div data-dz-icons-box><p class="hint">Or pick a drawing:</p><div class="dz-icons" data-dz-icons></div></div></div>
        <div class="dz-sec" data-dz-photo-box hidden><h3>Your photo</h3>
          <div class="dz-up"><label class="btn btn-ghost btn-small">Upload your photo<input type="file" accept="image/*" data-dz-photo hidden></label><span class="hint" data-dz-photo-name></span></div>
          <p class="hint">Or pick one of ours:</p><div class="dz-stock" data-dz-stock></div></div>
        <div class="dz-sec dz-buyrow"><div class="field"><label for="dz-pack">How many</label><select id="dz-pack" data-dz-pack>{packs}</select></div>
          <button type="button" class="btn btn-honey" data-dz-buy>Buy now</button>
          <div class="dz-digital"><button type="button" class="linkish" data-dz-digital data-price="{DIGITAL_PRICE}" data-title="{E(DIGITAL_TITLE)}">Only want the file to use online? ${DIGITAL_PRICE}</button>
          <p class="hint">A digital file of your design, high resolution, no watermark, sent to your email right after you pay. No magnet. Free with any magnet pack.</p></div>
          <p class="hint" data-dz-msg data-default="Free design check: we email you a proof within one business day. Nothing is printed until you approve it.">Free design check: we email you a proof within one business day. Nothing is printed until you approve it.</p></div>
      </div>
    </div>
  </dialog>"""


def page_occasions():
    (ROOT / "assets" / "designs.js").write_text(BIZ_DESIGNS.js() + "\n", encoding="utf-8")
    """business.html, weddings.html, graduation.html, parties.html (tools/occasions.py): for people who buy many."""
    by_key = {key: (title, key, desc, tiers, pick) for title, key, desc, tiers, pick in PACKAGES}
    for o in BULK_PAGES:
        pg = Page("")
        mine = [g for g in DESIGN_GALLERY if g[1] == o["slug"]]
        styles = [(sl, ti, gr) for sl, _, gr, ti in mine]
        cards = [pkg_card(*by_key[o["package"]], styles=styles)]
        cards += [pkg_card(*by_key[k]) for k in o.get("extra", [])]
        if o.get("mailing"):
            cards.append(pkg_card(*MAILING, unit="addresses"))
        ideas = "".join(f"""<li class="occ-idea">{occ_img(pg, sl)}<div><strong>{E(nm)}</strong><span>{E(tx)}</span>
            <button type="button" class="btn btn-ghost btn-small" data-use-style="{E(sl)}">Use this style</button></div></li>""" for sl, nm, tx in o["ideas"])
        now = "".join(f'<div class="occ-now-item" data-from="{a}" data-to="{b}" hidden><p class="eyebrow">Right now</p><h2>{E(t)}</h2><p>{E(x)}</p>'
                      f'<a class="btn btn-honey btn-small" href="#packs">Order now</a></div>' for a, b, t, x in o["now"])
        year = "".join(f"<li><strong>{E(m)}</strong><span>{E(t)}</span></li>" for m, t in o["year"])
        faq = "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in o["faq"])
        points = "".join(f"<li>{E(x)}</li>" for x in o["points"])
        qr = ""
        if o.get("qr"):
            Q = o["qr"]
            _t, _k, _d, tiers, pick = by_key[o["package"]]
            pid = PACKAGE_IDS[_k]
            chosen = min(tiers, key=lambda t: abs(t[0] - pick))[0]
            lines = "".join(f'<option data-top="{E(t)}" data-cta="{E(c)}"{" data-stars" if st else ""}>{E(t)} · {E(c.capitalize())}</option>' for t, c, st in Q["lines"])
            packs = "".join(f'<option value="{pid}-{n}" data-size="{n}" data-price="{pr}" data-title="{E(_t)}"{" selected" if n == chosen else ""}>{n} magnets · ${pr} (${pr / n:.2f} each)</option>' for n, pr in tiers)
            pals = "".join(f'<button type="button" class="qr-pal" data-pal="{k}" aria-label="{E(lab)}"{" aria-pressed=" + chr(34) + "true" + chr(34) if i == 0 else ""}></button>'
                           for i, (k, lab) in enumerate([("fern", "Sage"), ("honey", "Honey"), ("navy", "Navy"), ("blush", "Blush"), ("brick", "Brick"), ("teal", "Teal"), ("sky", "Sky"), ("plum", "Plum"), ("black", "Black & gold"), ("red", "Red"), ("sun", "Sunshine"), ("forest", "Forest"), ("lilac", "Lilac"), ("orange", "Orange")]))
            qr = f"""
  <section class="tight" id="qr">
    <div class="wrap">
      <div class="qr-maker" data-qr-maker>
        <div class="qr-form">
          <p class="eyebrow">QR magnets</p>
          <h2>{E(Q["title"])}</h2>
          <p class="qr-intro">{E(Q["intro"])}</p>
          <div class="field"><label for="qr-url">Your link</label><input id="qr-url" type="url" inputmode="url" autocomplete="url" placeholder="https://your-site.com" maxlength="200"></div>
          <div class="field"><label for="qr-name">Name on the magnet</label><input id="qr-name" maxlength="40" placeholder="{E(Q["name"])}"></div>
          <div class="field"><label for="qr-line">Message</label><select id="qr-line">{lines}</select></div>
          <div class="field"><span class="qr-label">Colors</span><div class="qr-pals">{pals}</div></div>
          <div class="field"><label for="qr-pack">How many</label><select id="qr-pack">{packs}</select></div>
          <div class="qr-actions"><button type="button" class="btn btn-honey" data-qr-buy>Buy now</button></div>
          <p class="hint" data-qr-msg>You approve a proof before we print. Any link works: Google reviews, menu, booking, Instagram.</p>
        </div>
        <div class="qr-preview">
          <div class="qrm" data-pal="fern" data-qr-preview translate="no">
            <div class="qrm-name">{E(Q["name"])}</div><div class="qrm-top"></div><div class="qrm-cta"></div>
            <div class="qrm-code" data-default="{E(Q["url"])}"></div><div class="qrm-stars">★★★★★</div>
          </div>
          <p class="hint">Point your phone camera at it: it already works.</p>
        </div>
      </div>
    </div>
  </section>"""
        options = "".join(f"<option{' selected' if k == o['quote'] else ''}>{E(k)}</option>"
                          for k in [o["quote"]] + [k for _, k, _, _, _ in PACKAGES if k not in (o["quote"], o["package"])] + ["Something else"])
        others = "".join(f'<a href="{x["slug"]}.html">{E(x["name"])}</a>' for x in BULK_PAGES if x is not o)
        body = f"""{header(pg, "business" if o["slug"] == "business" else "big")}
<main id="main" class="occ" data-occasion="{o["slug"]}">
  <div class="wrap page-head">
    <ol class="crumbs"><li><a href="index.html">Home</a></li><li><a href="big-orders.html">Bulk orders</a></li><li aria-current="page">{E(o["name"])}</li></ol>
    <div class="occ-hero">
      <div>
        <p class="eyebrow">{E(o["eyebrow"])}</p>
        <h1>{E(o["h1"])}</h1>
        <p class="lede">{E(o["lede"])}</p>
        <div class="actions"><a class="btn btn-honey" href="#designs">Design yours now</a><a class="btn btn-ghost" href="#packs">See prices</a></div>
        <ul class="occ-points">{points}</ul>
      </div>
      <img class="occ-hero-img" src="assets/occasions/{o["hero"]}.webp" alt="Example magnets on a fridge" width="1400" height="963" fetchpriority="high">
    </div>
  </div>

{studio_html(pg, o["slug"], by_key[o["package"]], {"business": "your business", "weddings": "your wedding", "graduation": "your graduation", "parties": "your party or event"}.get(o["slug"], "your event"))}

  <section class="tight occ-now" aria-label="The moment to order">
    <div class="wrap"><div class="band honey">{now}</div></div>
  </section>{qr}

  <section class="tight" id="packs">
    <div class="wrap">
      <div class="section-head"><div><p class="eyebrow">Prices</p><h2>Buy now, design together</h2></div><p>Pay for the pack now and we email you within one business day to plan the design. Nothing is printed until you approve the proof.</p></div>
      <ul class="pkg-grid">{"".join(cards)}</ul>
    </div>
  </section>

  <section class="tight">
    <div class="wrap">
      <div class="section-head"><div><p class="eyebrow">How it works</p><h2>Four easy steps</h2></div></div>
      <ol class="included occ-steps">
        <li><strong>1. Pick a design</strong><span>Change the colors and the words, add your logo, or let us design it with you.</span></li>
        <li><strong>2. Choose how many</strong><span>Buy the pack. Anything else (a logo file, a list) by email after checkout.</span></li>
        <li><strong>3. Approve the proof</strong><span>Within one business day. Change anything you want.</span></li>
        <li><strong>4. We press &amp; ship</strong><span>By hand, in 3 to 5 business days{", or mailed to your list" if o.get("mailing") else ""}.</span></li>
      </ol>
    </div>
  </section>

  <section class="tight">
    <div class="wrap">
      <div class="section-head"><div><p class="eyebrow">All year</p><h2>{E(o["year_title"])}</h2></div></div>
      <ul class="occ-year">{year}</ul>
    </div>
  </section>

  <section class="tight" id="request">
    <div class="wrap">
      <div class="section-head"><div><p class="eyebrow">Free mockup</p><h2>Tell us what you need</h2></div><p>We reply within one business day with a mockup idea, a price and a timeline.</p></div>
      <form class="quote" id="quote">
        <div class="field"><label for="q-name">Your name</label><input id="q-name" name="name" required autocomplete="name"></div>
        <div class="field"><label for="q-email">Email</label><input id="q-email" name="email" type="email" required autocomplete="email"></div>
        <div class="field"><label for="q-occasion">Occasion</label><select id="q-occasion" name="occasion">{options}</select></div>
        <div class="field"><label for="q-qty">How many magnets</label><input id="q-qty" name="quantity" type="number" min="10" step="1" value="100" required inputmode="numeric"></div>
        <div class="field"><label for="q-date">Date you need them</label><input id="q-date" name="date" type="date"></div>
        <div class="field full"><label for="q-msg">Your idea</label><textarea id="q-msg" name="message" placeholder="Your business or names, the style you liked, colors, logo…"></textarea></div>
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
      <div class="section-head"><div><p class="eyebrow">Questions</p><h2>Good to know</h2></div></div>
      <div class="faq">{faq}</div>
      <p class="occ-others">Also: {others} · <a href="big-orders.html">All bulk orders</a></p>
    </div>
  </section>
</main>
{footer(pg)}
<script>(function(){{var d=new Date(),k=(d.getMonth()+1)*100+d.getDate(),done=false;document.querySelectorAll('[data-from]').forEach(function(e){{if(done)return;var a=+e.getAttribute('data-from'),b=+e.getAttribute('data-to');if(a<=b?(k>=a&&k<=b):(k>=a||k<=b)){{e.hidden=false;done=true;}}}});if(!done){{var s=document.querySelector('.occ-now');if(s)s.hidden=true;}}}})();</script>"""
        write(f'{o["slug"]}.html', head(pg, o["name"], o["lede"][:155], f'{o["slug"]}.html') + body + chrome_end(pg, ("quote.js", "qr.js", "designs.js", "designer.js", "designer-more.js", "studio.js") + (("qrmagnet.js",) if o.get("qr") else ())))



def page_sale():
    """black-friday.html: where the sale bar's link goes (assets/site.js saleBar). Every way to shop, like the home
    page, with the deals on top. Once the sale is over the page says so and still shows everything."""
    pg = Page("")
    steps = sorted(SALE["free"], key=lambda f: f[0])
    free = " · ".join(f"buy {b}, get {g} free" for b, g in steps)
    day = (SALE.get("days") or [{}])[0]
    body = f"""{header(pg, "sale")}
<main id="main">
  <section class="sale-hero">
    <div class="wrap">
      <ol class="crumbs"><li><a href="index.html">Home</a></li><li aria-current="page">{E(SALE["name"])}</li></ol>
      <p class="eyebrow">Through Cyber Monday, November 30</p>
      <h1>{E(SALE["name"])} <em>at Little Hive House</em></h1>
      <p class="sale-ended" data-sale-ended hidden>The sale is over. Thank you! Everything below is still here at its regular price.</p>
      <ul class="sale-deals" data-sale-deals>
        <li><strong>{SALE["pct"]}% off</strong><span>everything in the shop, already in the price</span></li>
        <li><strong>Or get them free</strong><span>on our ready-made designs: {free}</span></li>
        <li class="sale-deals-day"><strong>{day.get("pct", SALE["pct"])}% off + free shipping</strong><span>Friday, November 27 only</span></li>
      </ul>
      <p class="sale-note-small" data-sale-deals>No code needed. The deals don’t add up together: your cart applies the better one for you.</p>
    </div>
  </section>

{doors(pg)}
</main>
{footer(pg)}
"""
    ended = "<script>window.addEventListener('load', function () { if (window.LHH && LHH.sale && !LHH.sale()) { var e = document.querySelector('[data-sale-ended]'); if (e) e.hidden = false; document.querySelectorAll('[data-sale-deals]').forEach(function (d) { d.hidden = true; }); } });</script>"
    write("black-friday.html", head(pg, f"{SALE['name']}: {SALE['pct']}% off everything", f"{SALE['name']} at Little Hive House: {SALE['pct']}% off everything, or buy 3 designs and get 1 free. Photo magnets, Personalize and business magnets too.", "black-friday.html")
          + body + chrome_end(pg).replace("</body>", ended + "\n</body>"))


def page_personalize():
    """personalize.html: the design studio for families. Their name, their pet, their baby, grandma's kitchen, a trip:
    one magnet or a few (PERSONAL), or just the design file."""
    pg = Page("")
    title, key, desc, tiers, pick = PERSONAL
    prices = "".join(f"<li><strong>{n} {'magnet' if n == 1 else 'magnets'}</strong><span>${p}{f' · ${p / n:.2f} each' if n > 1 else ''}</span></li>" for n, p in tiers)
    faq = "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in [
        ("How big is the magnet?", "2 × 2 inches, a glossy photo-quality print on a strong flexible magnet, pressed by hand."),
        ("Can I put my own photo?", "Yes. Designs with a photo let you upload yours, or pick one of ours. We check it before printing."),
        ("Will I see it before you print?", "Yes. We email you a proof within one business day. Nothing is printed until you approve it."),
        ("Can I just buy the design?", f"Yes. Tap the design, make it yours and choose “Only want the file”: ${DIGITAL_PRICE}, sent to your email right away, no magnet. It is free with any magnet order."),
        ("Is it a good gift?", "It is one of our favorites: grandma’s kitchen, a new home, a baby’s birth date, a pet. Ship it straight to them with a gift note."),
        ("How fast will it ship?", "We press and ship in 3 to 5 business days after you approve the proof. Free US shipping on orders over $35."),
    ])
    body = f"""{header(pg, "personalize")}
<main id="main" class="occ" data-occasion="personalize">
  <div class="wrap page-head">
    <ol class="crumbs"><li><a href="index.html">Home</a></li><li aria-current="page">Personalize</li></ol>
    <div class="occ-hero">
      <div>
        <p class="eyebrow">Personalize · just for you</p>
        <h1>Your family on the fridge</h1>
        <p class="lede">Your family name, your dog, your baby’s birth date, grandma’s kitchen, your last trip. Pick a design, change the words and the colors, add your photo and see it right away.</p>
        <div class="actions"><a class="btn btn-honey" href="#designs">Make yours now</a><a class="btn btn-ghost" href="#prices">See prices</a></div>
        <ul class="occ-points"><li>From ${tiers[0][1]} a magnet</li><li>Free proof before we print</li><li>A lovely gift, ready to mail</li></ul>
      </div>
      <img class="occ-hero-img" src="assets/occasions/hero-personalize.webp" alt="Personalized magnets on a fridge: a dog, a family name, a baby, grandma's kitchen" width="1400" height="963" fetchpriority="high">
    </div>
  </div>

{studio_html(pg, "personalize", PERSONAL, "your home")}

  <section class="tight" id="prices">
    <div class="wrap">
      <div class="section-head"><div><p class="eyebrow">Prices</p><h2>One or a few, your choice</h2></div><p>Every magnet is made just for you. Want only the design? ${DIGITAL_PRICE} for the file, free with any magnet.</p></div>
      <ul class="occ-year pz-prices">{prices}<li><strong>Design file only</strong><span>${DIGITAL_PRICE} · sent to your email</span></li></ul>
    </div>
  </section>

  <section class="tight">
    <div class="wrap">
      <div class="section-head"><div><p class="eyebrow">How it works</p><h2>Three easy steps</h2></div></div>
      <ol class="included occ-steps">
        <li><strong>1. Pick a design</strong><span>Change the words and the colors, add your photo.</span></li>
        <li><strong>2. Approve the proof</strong><span>We email it within one business day. Change anything you want.</span></li>
        <li><strong>3. We press &amp; ship</strong><span>By hand, in 3 to 5 business days. Straight to you or as a gift.</span></li>
      </ol>
    </div>
  </section>

  <section class="tight" id="faq">
    <div class="wrap">
      <div class="section-head"><div><p class="eyebrow">Questions</p><h2>Good to know</h2></div></div>
      <div class="faq">{faq}</div>
      <p class="occ-others">Also: <a href="photo-magnets.html">Photo magnets</a> · <a href="shop.html">Our designs</a> · <a href="business.html">For business</a></p>
    </div>
  </section>
</main>
{footer(pg)}"""
    write("personalize.html", head(pg, "Personalized magnets: your family, pet or baby", "Personalized fridge magnets: your family name, your pet, your baby, grandma's kitchen. Make it yours in our design studio and see it right away.", "personalize.html")
          + body + chrome_end(pg, ("qr.js", "designs.js", "designer.js", "designer-more.js", "studio.js")))


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


def page_cart():
    """cart.html: the checkout link of the Facebook/Instagram shop (Meta sends ?products=<feed id>:<qty>,...).
    The page fills the cart (assets/site.js) and opens it, so the buyer lands straight on their cart."""
    pg = Page("/")
    body = f"""{header(pg, None)}
<main id="main" data-cart-page>
  <div class="wrap page-head" style="padding-bottom:80px">
    <p class="eyebrow">Your cart</p>
    <h1>Your cart</h1>
    <p class="lede">Your magnets are in the cart. Review them and tap Checkout to pay securely.</p>
    <div class="hero-actions" style="margin-top:24px"><button type="button" class="btn" data-open-cart>View cart and checkout</button><a class="btn btn-ghost" href="/shop.html">Keep shopping</a></div>
  </div>
</main>
{footer(pg)}"""
    write("cart.html", head(pg, "Your cart", "Your Little Hive House cart.", "cart.html") + body + chrome_end(pg))


# ---- store backend: functions/catalog.json (server-side prices; must match assets/site.js totals()) ----
STORE_PHOTO_PACKS = [(4, 14), (9, 25), (16, 40), (25, 65), (50, 120)]   # same as the pack radios on photo-magnets.html
# Any number of photo magnets (15 Nov 2026, asked by a customer: "sometimes I want 10, not 9"): the price is the biggest
# pack that fits plus each extra photo at that pack's rate, never more than the next pack. Under 4 photos, $4 each.
# Same math in functions/pricing.js photoPrice() and assets/custom.js photoPrice().
STORE_PHOTO_EXTRA = {0: 4, 4: 3, 9: 2.75, 16: 2.5, 25: 2.5, 50: 2.4}
STORE_PHOTO_MAX = 100
STORE_SHIPPING, STORE_FREE_SHIP_AT = 5.49, 35


def photo_pricing_json():
    """The photo price rules for the builder (assets/custom.js), as JSON safe inside a single-quoted attribute."""
    import json as _json
    return _json.dumps({"packs": STORE_PHOTO_PACKS, "extra": {str(k): v for k, v in STORE_PHOTO_EXTRA.items()}, "max": STORE_PHOTO_MAX},
                       separators=(",", ":")).replace("'", "&#39;")


def export_store_catalog():
    import json as _json
    ids = globals().get("PACKAGE_IDS") or {}
    frames = _json.loads((ROOT / "assets" / "frames" / "frames.json").read_text(encoding="utf-8"))
    cat = {
        "designs": {f'{c["slug"]}/{s}': {"title": title_for(c, s), "collection": c["slug"], "collectionName": c["name"], "price": PRICE}
                    for c in ALL_COLLECTIONS for s in c["order"]},   # archive too: old carts and orders keep working
        "packs": {str(n): {"size": n, "price": p, "title": f"Custom photo magnets (pack of {n})"} for n, p in STORE_PHOTO_PACKS},
        "photoPricing": {"extra": {str(k): v for k, v in STORE_PHOTO_EXTRA.items()}, "max": STORE_PHOTO_MAX},
        "packages": {f'{ids.get(key) or title.split()[0].lower()}-{n}': {"title": f"{title}, {n} magnets", "group": ids.get(key) or title.split()[0].lower(),
                                                                         "size": n, "price": p}
                     for title, key, _, tiers, _ in PACKAGES + [PERSONAL] for n, p in tiers}
                    | {f"mailing-{n}": {"title": f"Mailed to your list, {n} addresses", "group": "mailing", "size": 0, "addresses": n, "price": p}
                       for n, p in MAILING[3]}
                    | {"digital-file": {"title": DIGITAL_TITLE, "group": "digital", "size": 0, "price": DIGITAL_PRICE, "digital": True}},
        "rules": {"designPrice": PRICE, "bundle": {"size": BUNDLE[0], "price": BUNDLE[1]},
                  "volume": [{"min": n, "pct": pct} for n, pct in VOLUME], "shipping": STORE_SHIPPING,
                  "freeShippingAt": STORE_FREE_SHIP_AT, "currency": "usd", "sale": SALE},
        # the calendar of the home page spotlight, for the automatic emails to subscribers (functions/newsletter.js)
        "seasons": [{"start": a, "end": b, "title": t, "label": lab, "blurb": bl, "collection": col,
                     "picks": [f"{c}/{sl}" for c, sl in picks if any(x["slug"] == c and sl in x["order"] for x in COLLECTIONS)]}
                    for a, b, t, lab, bl, col, picks, _ in SEASONS],
        "frames": {f["id"]: {"name": f["name"], "window": f.get("window") or [0, 0, 600, 600], "captionMax": (f.get("caption") or {}).get("max", 0),
                             "captionStyles": sorted(((f.get("caption") or {}).get("styles") or {}).keys())} for f in frames},
    }
    out = ROOT / "functions" / "catalog.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_json.dumps(cat, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def write_sitemap():
    """sitemap.xml (pages + every design image, so Google Images finds them) and robots.txt."""
    site = "https://littlehivehouse.com/"
    def img(col_slug, slug, title):
        return (f"\n    <image:image><image:loc>{site}assets/art/{col_slug}/{slug}.webp</image:loc>"
                f"<image:title>{E(title)} magnet</image:title></image:image>")
    entries = [("", "1.0", ""), ("shop.html", "0.9", ""), ("collections/", "0.9", ""),
               ("photo-magnets.html", "0.8", ""), ("personalize.html", "0.8", ""), ("big-orders.html", "0.8", "")] + [(f'{o["slug"]}.html', "0.8", "") for o in BULK_PAGES]
    for g in GROUPS:
        entries.append((f"collections/{g['slug']}.html", "0.8", ""))
    for c in COLLECTIONS + MORE_COLLECTIONS:
        imgs = "".join(img(c["slug"], s, c["titles"].get(s) or s.replace("-", " ").title())
                       for s in c["order"] + c.get("more", []) if (ROOT / f"assets/art/{c['slug']}/{s}.webp").exists())
        entries.append((f"collections/{c['slug']}.html", "0.8", imgs))
    for c, x in shop_designs():
        entries.append((f'm/{c["slug"]}/{x}.html', "0.6", img(c["slug"], x, title_for(c, x))))
    for p in ("contact.html", "suggestions.html", "shipping.html", "returns.html", "track.html", "privacy.html", "terms.html"):
        if (ROOT / p).exists():
            entries.append((p, "0.4", ""))
    urls = "\n".join(f"  <url>\n    <loc>{site}{loc}</loc>\n    <priority>{pri}</priority>{imgs}\n  </url>"
                     for loc, pri, imgs in entries)
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
          'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + urls + "\n</urlset>\n")
    write("robots.txt", "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /versions/\n\n"
          f"Sitemap: {site}sitemap.xml\n")


def write_archived_redirects():
    """Collections taken off the site (kept in the archive) answer old links with a redirect to all collections."""
    shown = {c["slug"] for c in COLLECTIONS + MORE_COLLECTIONS} | {g["slug"] for g in GROUPS}
    for c in ALL_COLLECTIONS:
        if c["slug"] not in shown:
            write(f"collections/{c['slug']}.html", '<!doctype html><html lang="en"><head><meta charset="utf-8">'
                  '<meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url=./">'
                  '<link rel="canonical" href="https://littlehivehouse.com/collections/"><title>Little Hive House</title></head>'
                  '<body><a href="./">See all collections</a></body></html>\n')


if __name__ == "__main__":
    page_home()
    page_shop()
    page_collections_index()
    for c in COLLECTIONS + MORE_COLLECTIONS:
        page_collection(c)
    for g in GROUPS:
        page_group(g)
    page_photo()
    page_big()
    page_occasions()        # business.html, weddings.html, graduation.html, parties.html
    page_personalize()      # personalize.html
    page_sale()             # black-friday.html (the sale bar's link)
    page_404()
    page_cart()             # cart.html: checkout link for the Facebook/Instagram shop
    # store: customer pages (account, orders, tracking, policies...) live in tools/store_pages.py
    import sys as _sys
    import store_pages
    store_pages.build(_sys.modules[__name__])
    export_store_catalog()   # store backend prices -> functions/catalog.json
    write_archived_redirects()
    page_products()          # m/<collection>/<slug>.html: a page for every design
    write_google_feed()      # google-products.xml for Google Merchant Center
    write_sitemap()          # sitemap.xml + robots.txt for Google
    import admin_icons       # admin/icons/*.png for the installable admin (only drawn when missing)
    admin_icons.main()
    print(f"built {TOTAL} designs in {len(COLLECTIONS)} collections")
