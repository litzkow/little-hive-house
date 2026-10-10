/* Little Hive House: cart, menu, quick view and shop filters, shared by every page. */
(function () {
  var PRICE = 5, BUNDLE_N = 3, BUNDLE_PRICE = 12;
  var SHIPPING = 4.95, FREE_SHIP_AT = 35;
  var VOLUME = [[100, 25], [50, 20], [20, 10]];
  var KEY = 'lhh-cart';
  var $ = function (id) { return document.getElementById(id); };
  var money = function (n) { return '$' + (Math.round(n * 100) / 100).toFixed(n % 1 ? 2 : 0); };

  // Ready-made designs persist between pages; photo packs live only on the page where they were made.
  var cart = [];
  try {
    var saved = JSON.parse(localStorage.getItem(KEY) || '[]');
    if (Array.isArray(saved)) {
      cart = saved.filter(function (l) { return l && (l.kind === 'design' || l.kind === 'place') && l.qty > 0; })
        .map(function (l) {
          if (l.kind === 'place') { l.kind = 'design'; if (l.id.indexOf('/') < 0) l.id = 'places/' + l.id; }
          return l;
        });
    }
  } catch (e) {}

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(cart.filter(function (l) { return l.kind === 'design'; }))); } catch (e) {}
  }

  var toastTimer;
  function toast(msg) {
    var t = $('toast'); if (!t) return;
    t.textContent = msg; t.hidden = false;
    clearTimeout(toastTimer); toastTimer = setTimeout(function () { t.hidden = true; }, 2200);
  }

  function totals() {
    var sub = 0, designs = 0;
    cart.forEach(function (l) { sub += l.price * l.qty; if (l.kind === 'design') designs += l.qty; });
    var disc = Math.floor(designs / BUNDLE_N) * (BUNDLE_N * PRICE - BUNDLE_PRICE);
    var magnets = cart.reduce(function (a, l) { return a + l.qty * (l.count || 1); }, 0);
    var tier = VOLUME.find(function (v) { return magnets >= v[0]; });
    var pct = tier ? tier[1] : 0;
    var vol = Math.round((sub - disc) * pct) / 100;
    var goods = sub - disc - vol;
    var ship = goods >= FREE_SHIP_AT ? 0 : SHIPPING;
    var next = VOLUME.slice().reverse().find(function (v) { return magnets < v[0]; });
    return { sub: sub, disc: disc, vol: vol, pct: pct, magnets: magnets, next: next, goods: goods, ship: ship, total: goods + ship, count: cart.reduce(function (a, l) { return a + l.qty; }, 0) };
  }

  function render() {
    var t = totals();
    document.querySelectorAll('[data-cart-count]').forEach(function (el) { el.textContent = t.count; });
    var ul = $('lines'); if (!ul) return;
    ul.innerHTML = '';
    cart.forEach(function (l, i) {
      var li = document.createElement('li'); li.className = 'line';
      var left = document.createElement('div');
      var h = document.createElement('h3'); h.textContent = l.name; left.appendChild(h);
      var d = document.createElement('p'); d.className = 'detail'; d.textContent = l.detail; left.appendChild(d);
      var amt = document.createElement('div'); amt.className = 'amt'; amt.textContent = money(l.price * l.qty);
      var qty = document.createElement('div'); qty.className = 'qty';
      var minus = document.createElement('button'); minus.type = 'button'; minus.textContent = '−'; minus.setAttribute('aria-label', 'One less ' + l.name);
      var out = document.createElement('output'); out.textContent = l.qty;
      var plus = document.createElement('button'); plus.type = 'button'; plus.textContent = '+'; plus.setAttribute('aria-label', 'One more ' + l.name);
      minus.onclick = function () { l.qty -= 1; if (l.qty < 1) cart.splice(i, 1); save(); render(); };
      plus.onclick = function () { l.qty += 1; save(); render(); };
      qty.append(minus, out, plus);
      var rm = document.createElement('button'); rm.type = 'button'; rm.className = 'remove'; rm.textContent = 'Remove';
      rm.onclick = function () { cart.splice(i, 1); save(); render(); };
      li.append(left, amt, qty, rm);
      ul.appendChild(li);
    });
    var empty = cart.length === 0;
    $('empty-cart').hidden = !empty;
    $('totals').hidden = empty;
    $('t-sub').textContent = money(t.sub);
    $('t-disc-row').hidden = t.disc === 0;
    $('t-disc').textContent = '−' + money(t.disc);
    $('t-vol-row').hidden = t.vol === 0;
    $('t-vol-label').textContent = 'Big order, ' + t.magnets + ' magnets (' + t.pct + '% off)';
    $('t-vol').textContent = '−' + money(t.vol);
    var vn = $('vol-note');
    if (t.next && t.magnets >= 5) { vn.textContent = 'Add ' + (t.next[0] - t.magnets) + ' more magnets for ' + t.next[1] + '% off your whole order.'; vn.hidden = false; }
    else vn.hidden = true;
    $('t-ship').textContent = t.ship ? money(t.ship) : 'Free';
    $('t-total').textContent = money(t.total);
    var sn = $('ship-note');
    if (t.ship) { sn.textContent = 'Add ' + money(FREE_SHIP_AT - t.goods) + ' more for free US shipping.'; sn.classList.remove('free'); }
    else { sn.textContent = 'Your order ships free.'; sn.classList.add('free'); }
  }

  var lastFocus = null;
  function openCart() { lastFocus = document.activeElement; $('scrim').hidden = false; $('drawer').hidden = false; $('close-cart').focus(); }
  function closeCart() { $('scrim').hidden = true; $('drawer').hidden = true; if (lastFocus && lastFocus.focus) lastFocus.focus(); }
  document.querySelectorAll('[data-open-cart]').forEach(function (b) { b.addEventListener('click', openCart); });
  $('close-cart').onclick = closeCart;
  $('scrim').onclick = closeCart;
  $('empty-shop').addEventListener('click', closeCart);
  $('drawer').addEventListener('keydown', function (e) { if (e.key === 'Escape') closeCart(); });

  function addDesign(el) {
    var id = el.getAttribute('data-add');
    var name = el.getAttribute('data-name');
    var line = cart.find(function (l) { return l.id === id; });
    if (line) line.qty += 1;
    else cart.push({ id: id, kind: 'design', name: name + ' magnet', detail: '2 × 2 in · ' + el.getAttribute('data-collection'), price: PRICE, qty: 1 });
    save(); render(); toast(name + ' added to cart');
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-add]');
    if (b) addDesign(b);
  });

  // mobile menu
  var mb = $('menu-btn'), mm = $('mobile-menu');
  if (mb && mm) {
    mb.addEventListener('click', function () {
      var open = mb.getAttribute('aria-expanded') === 'true';
      mb.setAttribute('aria-expanded', String(!open)); mm.hidden = open;
    });
  }

  // seasonal drifting leaves / snow / petals in the hero
  (function () {
    var hero = document.querySelector('.hero');
    var season = document.documentElement.getAttribute('data-season');
    var sets = { fall: ['fall-leaf1', 'fall-leaf2', 'fall-leaf3', 'fall-leaf4'], halloween: ['halloween-bat', 'fall-leaf1', 'fall-leaf3'],
                 christmas: ['snow1', 'snow2', 'snow3'], winter: ['snow1', 'snow2', 'snow3'], valentine: ['heart1', 'heart2'],
                 spring: ['petal1', 'petal2', 'petal3'], summer: [] };
    var list = sets[season];
    if (!hero || !list || !list.length || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var me = document.querySelector('script[src*="site.js"]');
    var base = me ? me.src.replace(/site\.js.*$/, 'decor/') : 'assets/decor/';
    var box = document.createElement('div'); box.className = 'drift'; box.setAttribute('aria-hidden', 'true');
    for (var i = 0; i < 9; i++) {
      var el = document.createElement('i');
      var s = 18 + Math.random() * 16;
      el.style.left = (Math.random() * 96) + '%';
      el.style.width = el.style.height = s + 'px';
      el.style.backgroundImage = 'url(' + base + list[i % list.length] + '.svg)';
      el.style.animationDuration = (11 + Math.random() * 9) + 's';
      el.style.animationDelay = (-Math.random() * 18) + 's';
      box.appendChild(el);
    }
    hero.insertBefore(box, hero.firstChild);
  })();

  // day / night toggle
  var tb = $('theme-btn');
  if (tb) tb.addEventListener('click', function () {
    var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    try { localStorage.setItem('lhh-theme', next); } catch (e) {}
  });

  // quick view
  var qv = $('quick-view');
  if (qv && typeof qv.showModal === 'function') {
    var qvAdd = $('qv-add');
    document.addEventListener('click', function (e) {
      var art = e.target.closest('[data-view]');
      if (!art) return;
      var card = art.closest('.product');
      var btn = card.querySelector('[data-add]');
      $('qv-art').innerHTML = art.innerHTML;
      $('qv-title').textContent = btn.getAttribute('data-name');
      var col = $('qv-col');
      col.textContent = btn.getAttribute('data-collection') + ' collection';
      col.setAttribute('href', btn.getAttribute('data-href'));
      ['data-add', 'data-name', 'data-collection'].forEach(function (a) { qvAdd.setAttribute(a, btn.getAttribute(a)); });
      qv.showModal();
    });
    $('qv-close').addEventListener('click', function () { qv.close(); });
    qv.addEventListener('click', function (e) { if (e.target === qv) qv.close(); });
    qvAdd.addEventListener('click', function () { setTimeout(function () { qv.close(); }, 150); });
  }

  // shop page: collection filter + search
  var grid = $('all-products');
  if (grid) {
    var items = Array.prototype.slice.call(grid.querySelectorAll('.product'));
    var tabs = Array.prototype.slice.call(document.querySelectorAll('[data-filter]'));
    var q = $('search'), countEl = $('result-count'), none = $('no-results');
    var current = 'all';
    var params = new URLSearchParams(location.search);
    var fromUrl = params.get('c');
    if (params.get('q')) q.value = params.get('q');
    if (fromUrl && tabs.some(function (t) { return t.getAttribute('data-filter') === fromUrl; })) current = fromUrl;
    function apply() {
      var term = (q.value || '').trim().toLowerCase();
      var shown = 0;
      items.forEach(function (it) {
        var ok = (current === 'all' || it.getAttribute('data-collection') === current) &&
                 (!term || it.getAttribute('data-search').indexOf(term) !== -1);
        it.hidden = !ok; if (ok) shown++;
      });
      tabs.forEach(function (t) { t.setAttribute('aria-pressed', String(t.getAttribute('data-filter') === current)); });
      countEl.textContent = shown + (shown === 1 ? ' design' : ' designs');
      none.hidden = shown !== 0;
    }
    tabs.forEach(function (t) {
      t.addEventListener('click', function () {
        current = t.getAttribute('data-filter');
        var u = new URL(location.href);
        if (current === 'all') u.searchParams.delete('c'); else u.searchParams.set('c', current);
        history.replaceState(null, '', u);
        apply();
      });
    });
    q.addEventListener('input', apply);
    apply();
  }

  // home page: show the seasonal spotlight for today's date
  var spot = $('spotlight');
  if (spot) {
    var now = new Date();
    var md = String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now.getDate()).padStart(2, '0');
    var inRange = function (s, e) { return s <= e ? (md >= s && md <= e) : (md >= s || md <= e); };
    var tpl = Array.prototype.find.call(document.querySelectorAll('template[data-start]'), function (t) { return inRange(t.getAttribute('data-start'), t.getAttribute('data-end')); });
    if (tpl && spot.getAttribute('data-season') !== tpl.getAttribute('data-start') + '_' + tpl.getAttribute('data-end')) {
      spot.replaceWith(tpl.content.cloneNode(true));
    }
  }

  window.LHH = {
    addCustom: function (item) { item.kind = 'custom'; item.qty = 1; cart.push(item); render(); toast('Photo magnets added to cart'); openCart(); },
    money: money,
    toast: toast
  };
  render();
})();
