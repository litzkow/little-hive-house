"""Writes versions/escolher.html: a private page where the owners tap the designs to keep (heart) and the strongest
ones for the home page (star), old first-version designs and current ones side by side by theme, then copy the list.
Old thumbnails: versions/thumbs/<collection>/<slug>.webp (first-version designs, commit 93c81d3).
Run: python3 tools/picker.py"""
import html
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from catalog import COLLECTIONS, title_for  # noqa: E402

BY = {c["slug"]: c for c in COLLECTIONS}

# old catalog (titles) from the first-version commit
_old_src = subprocess.check_output(["git", "-C", str(ROOT), "show", "93c81d3:tools/catalog.py"]).decode()
_ns = {}
exec(compile(_old_src, "catalog_v3", "exec"), _ns)
OLD = {c["slug"]: c for c in _ns["COLLECTIONS"]}
old_title = _ns["title_for"]

# themes in the order they will be shown: (title, old collections, current collections)
THEMES = [
    ("Lugares dos EUA", ["places"], ["places"]),
    ("Lugares do mundo", ["world"], ["world"]),
    ("Cidades em traço", ["ink-cities"], ["ink-cities", "city-sketches"]),
    ("Fall (outono)", ["fall"], ["fall"]),
    ("Halloween", ["halloween"], ["halloween"]),
    ("Terror clássico", [], ["horror"]),
    ("Natal", ["christmas"], ["christmas"]),
    ("Datas comemorativas", ["holidays"], ["holidays"]),
    ("Verão", ["summer"], ["summer"]),
    ("Brasil", ["brasil"], ["brasil"]),
    ("Abelhas (Bee Kind)", ["bee-kind"], ["bee-kind"]),
    ("Bichinhos (Furry Friends)", ["furry-friends"], ["furry-friends"]),
    ("Frases de cozinha", ["kitchen-words"], ["kitchen-words"]),
    ("Recadinhos da casa (Home Notes)", ["home-notes"], ["home-notes"]),
    ("Adesivos de para-choque", ["bumper-stickers"], ["bumper-stickers"]),
    ("Signos", ["night-sky"], ["night-sky"]),
    ("Flores de cada mês", ["birth-flowers"], ["birth-flowers"]),
    ("Países (Heritage)", [], ["americana", "mexico", "ireland", "italia", "puerto-rico", "philippines", "india", "korea", "japan", "greece", "france"]),
    ("Grandes pintores", [], ["great-masters"]),
    ("Mitologia", [], ["mythology"]),
    ("Contos de fadas", [], ["fairy-tales"]),
    ("Livros clássicos", [], ["storybook-classics"]),
    ("Grandes pensadores", [], ["wise-words"]),
]

E = html.escape


def tile(kind, col, slug, title, src):
    key = f"{kind}:{col}/{slug}"
    badge = '<span class="b old">Antigo</span>' if kind == "old" else ""
    return (f'<button type="button" class="t" data-k="{E(key)}" data-t="{E(title)}" aria-pressed="false">'
            f'<img src="{E(src)}" alt="" loading="lazy" decoding="async">{badge}<span class="m" aria-hidden="true"></span>'
            f'<span class="n">{E(title)}</span></button>')


def section(i, name, olds, news):
    tiles = []
    for c in olds:
        for s in OLD[c]["order"]:
            if (ROOT / f"versions/thumbs/{c}/{s}.webp").exists():
                tiles.append(tile("old", c, s, old_title(OLD[c], s), f"thumbs/{c}/{s}.webp"))
    groups = []
    for c in news:
        col = BY[c]
        items = "".join(tile("new", c, s, title_for(col, s), f"../assets/art/{c}/{s}.webp") for s in col["order"])
        sub = f'<h3>{E(col["name"])}</h3>' if len(news) > 1 else ""
        groups.append(f'{sub}<div class="g">{items}</div>')
    olds_html = (f'<h3>Primeira versão</h3><div class="g">{"".join(tiles)}</div>' if tiles else "")
    news_label = '<h3>Versão atual</h3>' if tiles and len(news) == 1 else ""
    n = len(tiles) + sum(len(BY[c]["order"]) for c in news)
    return (f'<section id="s{i}"><h2>{E(name)} <small>{n}</small></h2>{olds_html}{news_label}{"".join(groups)}</section>')


def main():
    nav = "".join(f'<a href="#s{i}">{E(t[0])}</a>' for i, t in enumerate(THEMES))
    body = "".join(section(i, *t) for i, t in enumerate(THEMES))
    page = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="robots" content="noindex"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Escolher os desenhos · Little Hive House</title><link rel="icon" href="../assets/favicon.svg">
<style>
:root{{--bg:#FFF6E5;--ink:#2B2118;--muted:#7A6A58;--line:#EADFCB;--honey:#F2A81D}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;padding-bottom:110px}}
header{{padding:20px 14px 6px;max-width:1100px;margin:0 auto}}h1{{font-size:24px;margin:0 0 6px}}
.how{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 14px;margin:10px 0}}
.how p{{margin:4px 0}}
nav{{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);display:flex;gap:8px;overflow-x:auto;padding:10px 14px;scrollbar-width:none}}
nav a{{flex:none;color:var(--ink);text-decoration:none;border:1px solid var(--line);background:#fff;border-radius:999px;padding:6px 12px;font-size:13px}}
main{{max-width:1100px;margin:0 auto;padding:0 14px}}
h2{{font-size:20px;margin:26px 0 6px;scroll-margin-top:60px}}h2 small{{color:var(--muted);font-weight:500;font-size:14px}}
h3{{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:14px 0 8px}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));gap:10px}}
.t{{position:relative;border:0;padding:0;background:none;cursor:pointer;text-align:left;font:inherit;color:inherit;-webkit-tap-highlight-color:transparent}}
.t img{{display:block;width:100%;aspect-ratio:1;border-radius:9%;background:#eee;box-shadow:0 4px 10px -6px rgba(0,0,0,.5);transition:transform .12s, outline-color .12s;outline:3px solid transparent;outline-offset:2px}}
.t .n{{display:block;font-size:11.5px;line-height:1.25;color:var(--muted);margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.t .b{{position:absolute;left:6px;top:6px;font-size:10px;font-weight:700;background:#2B2118;color:#fff;border-radius:999px;padding:1px 7px}}
.t .m{{position:absolute;right:5px;top:5px;width:30px;height:30px;border-radius:50%;display:none;place-items:center;font-size:17px;background:#fff;box-shadow:0 2px 6px rgba(0,0,0,.35)}}
.t[data-s="1"] img{{outline-color:#D9534F}}.t[data-s="1"] .m{{display:grid}}.t[data-s="1"] .m::after{{content:"♥";color:#D9534F}}
.t[data-s="2"] img{{outline-color:var(--honey);transform:scale(.96)}}.t[data-s="2"] .m{{display:grid;background:var(--honey)}}.t[data-s="2"] .m::after{{content:"★";color:#fff}}
.bar{{position:fixed;left:0;right:0;bottom:0;z-index:6;background:#2B2118;color:#fff;padding:10px 14px calc(env(safe-area-inset-bottom,0px) + 10px);display:flex;gap:10px;align-items:center;flex-wrap:wrap}}
.bar .c{{flex:1 1 160px;font-size:14px}}.bar button{{font:600 15px inherit;border:0;border-radius:999px;padding:11px 16px;cursor:pointer}}
.bar .copy{{background:var(--honey);color:#2B2118}}.bar .clear{{background:transparent;color:#fff;border:1px solid #fff6}}
.toast{{position:fixed;left:50%;bottom:90px;transform:translateX(-50%);background:#fff;color:#2B2118;border-radius:999px;padding:10px 16px;box-shadow:0 6px 20px rgba(0,0,0,.3);display:none;font-weight:600;z-index:7}}
textarea{{width:100%;min-height:160px;margin-top:10px;font:12px ui-monospace,monospace;display:none}}
</style></head><body>
<header><h1>Quais desenhos ficam no site?</h1>
<div class="how"><p><b>Toque 1 vez</b> = ♥ fica no site.</p><p><b>Toque 2 vezes</b> = ★ é dos mais fortes (vai para a vitrine da página inicial). A ideia é ter umas 20 estrelas.</p>
<p><b>Toque 3 vezes</b> = desmarca.</p><p>O que não for marcado sai do site (fica guardado, nada é apagado). As escolhas ficam salvas neste celular, pode parar e continuar depois. No final toque em <b>Copiar minha lista</b> e cole no chat.</p></div></header>
<nav>{nav}</nav>
<main>{body}</main>
<div class="bar"><span class="c" id="count">0 escolhidos</span><button type="button" class="clear" id="clear">Limpar</button><button type="button" class="copy" id="copy">Copiar minha lista</button></div>
<div class="toast" id="toast"></div>
<script>
(function () {{
  var KEY = 'lhh-picker-v1', st = {{}};
  try {{ st = JSON.parse(localStorage.getItem(KEY) || '{{}}') || {{}}; }} catch (e) {{}}
  var tiles = document.querySelectorAll('.t');
  function save() {{ try {{ localStorage.setItem(KEY, JSON.stringify(st)); }} catch (e) {{}} }}
  function paint(t) {{ var v = st[t.dataset.k] || 0; t.setAttribute('data-s', v); t.setAttribute('aria-pressed', v ? 'true' : 'false'); }}
  function count() {{
    var h = 0, s = 0; for (var k in st) {{ if (st[k] === 1) h++; else if (st[k] === 2) s++; }}
    document.getElementById('count').textContent = (h + s) + ' escolhidos · ' + s + ' ★';
  }}
  tiles.forEach(function (t) {{
    paint(t);
    t.addEventListener('click', function () {{ var v = ((st[t.dataset.k] || 0) + 1) % 3; if (v) st[t.dataset.k] = v; else delete st[t.dataset.k]; paint(t); save(); count(); }});
  }});
  count();
  function toast(m) {{ var x = document.getElementById('toast'); x.textContent = m; x.style.display = 'block'; setTimeout(function () {{ x.style.display = 'none'; }}, 2200); }}
  document.getElementById('clear').onclick = function () {{ if (confirm('Desmarcar tudo?')) {{ st = {{}}; save(); tiles.forEach(paint); count(); }} }};
  document.getElementById('copy').onclick = function () {{
    var stars = [], keep = [];
    for (var k in st) (st[k] === 2 ? stars : keep).push(k);
    var txt = 'ESCOLHA LITTLE HIVE HOUSE\\n★ VITRINE (' + stars.length + '):\\n' + stars.join('\\n') + '\\n\\n♥ FICAM (' + keep.length + '):\\n' + keep.join('\\n');
    var done = function () {{ toast('Lista copiada! Agora cole no chat.'); }};
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, fallback); else fallback();
    function fallback() {{ var ta = document.querySelector('textarea') || document.body.appendChild(document.createElement('textarea')); ta.style.display = 'block'; ta.value = txt; ta.focus(); ta.select(); try {{ document.execCommand('copy'); done(); }} catch (e) {{ toast('Selecione o texto abaixo e copie.'); }} }}
  }};
}})();
</script></body></html>"""
    (ROOT / "versions/escolher.html").write_text(page, encoding="utf-8")
    print("tiles:", page.count('class="t"'))


if __name__ == "__main__":
    main()
