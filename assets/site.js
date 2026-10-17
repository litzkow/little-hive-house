/* Little Hive House: cart, menu, quick view and shop filters, shared by every page. */
(function () {
  var PRICE = 5, BUNDLE_N = 3, BUNDLE_PRICE = 12;
  var SHIPPING = 4.95, FREE_SHIP_AT = 35;
  var VOLUME = [[100, 25], [50, 20], [20, 10]];
  var KEY = 'lhh-cart';
  /* store: a package line, or a photo pack already uploaded to the store (it survives a canceled checkout) */
  function keep(l) { return l && (l.kind === 'package' || (l.kind === 'custom' && !!l.uploaded && Array.isArray(l.photos))); }
  var $ = function (id) { return document.getElementById(id); };
  var money = function (n) { return '$' + (Math.round(n * 100) / 100).toFixed(n % 1 ? 2 : 0); };

  // Ready-made designs persist between pages; photo packs live only on the page where they were made.
  var cart = [];
  try {
    var saved = JSON.parse(localStorage.getItem(KEY) || '[]');
    if (Array.isArray(saved)) {
      /* store: packages, and photo packs whose photos are already uploaded, also persist (see keep()) */
      cart = saved.filter(function (l) { return l && (l.kind === 'design' || l.kind === 'place' || keep(l)) && l.qty > 0; })
        .map(function (l) {
          if (l.kind === 'place') { l.kind = 'design'; if (l.id.indexOf('/') < 0) l.id = 'places/' + l.id; }
          return l;
        });
    }
  } catch (e) {}

  function save() {
    try {
      localStorage.setItem(KEY, JSON.stringify(cart.filter(function (l) { return l.kind === 'design' || keep(l); }).map(function (l) {
        if (!l.photos) return l;
        var c = {}; for (var k in l) c[k] = l[k];   /* Blobs and blob: URLs only live on this page */
        c.photos = l.photos.map(function (ph) { return { n: ph.n, file: ph.file, frame: ph.frame, frameName: ph.frameName, caption: ph.caption, path: ph.path, crop: ph.crop || null, w: ph.w || 0, h: ph.h || 0 }; });
        return c;
      })));
    } catch (e) {}
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

  /* small picture of each cart line: the design itself, the frame of the first photo, or the honeycomb for packages */
  var ROOT = (function () { var me = document.querySelector('script[src*="site.js"]'); return me ? me.src.replace(/assets\/site\.js.*$/, '') : '/'; })();
  function lineThumb(l) {
    var src = '';
    if (l.kind === 'design' && /^[a-z0-9-]+\/[a-z0-9-]+$/.test(l.id || '')) src = ROOT + 'assets/art/' + l.id + '.webp';
    else if (l.photos && l.photos.length && /^[a-z0-9-]+$/.test(l.photos[0].frame || '')) src = ROOT + 'assets/email/thumbs/frames/' + l.photos[0].frame + '.jpg';
    else src = ROOT + 'assets/favicon.svg';
    var img = document.createElement('img');
    img.className = 'line-thumb' + (l.kind === 'design' ? '' : ' line-thumb-icon');
    img.src = src; img.alt = ''; img.width = 56; img.height = 56; img.loading = 'lazy'; img.decoding = 'async';
    img.onerror = function () { img.remove(); };
    return img;
  }

  function render() {
    var t = totals();
    document.querySelectorAll('[data-cart-count]').forEach(function (el) { el.textContent = t.count; });
    var ul = $('lines'); if (!ul) return;
    ul.innerHTML = '';
    cart.forEach(function (l, i) {
      var li = document.createElement('li'); li.className = 'line';
      var left = document.createElement('div'); left.className = 'line-main';
      var thumb = lineThumb(l);
      if (thumb) left.appendChild(thumb);
      var txt = document.createElement('div'); left.appendChild(txt);
      var h = document.createElement('h3'); h.textContent = l.name; txt.appendChild(h);
      var d = document.createElement('p'); d.className = 'detail'; d.textContent = l.detail; txt.appendChild(d);
      if (l.photos && l.photos.length) {  /* photo packs: the frame (and caption) chosen for each photo */
        var det = document.createElement('details'); det.className = 'line-photos';
        var sm = document.createElement('summary'); sm.textContent = 'Frame for each photo'; det.appendChild(sm);
        var ol = document.createElement('ol');
        l.photos.forEach(function (ph) {
          var it = document.createElement('li');
          it.textContent = ph.frameName + (ph.caption ? ' · “' + ph.caption + '”' : '');
          ol.appendChild(it);
        });
        det.appendChild(ol); left.appendChild(det);
      }
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

  // seasonal collections: in season they sit right after the place collections, out of season at the end
  (function () {
    var d = new Date(), md = (d.getMonth() + 1) * 100 + d.getDate();
    var inSeason = function (r) { var p = r.split('-'), a = +p[0], b = +p[1]; return a <= b ? (md >= a && md <= b) : (md >= a || md <= b); };
    var seen = [];
    document.querySelectorAll('[data-col-season]').forEach(function (el) {
      var box = el.parentNode; if (seen.indexOf(box) >= 0) return; seen.push(box);
      var items = Array.prototype.filter.call(box.children, function (c) { return c.hasAttribute('data-col-season'); });
      var anchor = Array.prototype.filter.call(box.children, function (c) { return c.hasAttribute('data-col-anchor'); })[0];
      var now = items.filter(function (c) { return inSeason(c.getAttribute('data-col-season')); });
      var later = items.filter(function (c) { return !inSeason(c.getAttribute('data-col-season')); });
      var ref = anchor ? anchor.nextSibling : box.firstChild;
      now.forEach(function (c) { box.insertBefore(c, ref); });
      later.forEach(function (c) { box.appendChild(c); });
    });
  })();

  // seasonal drifting leaves / snow / petals in the hero
  (function () {
    var hero = document.querySelector('.hero');
    var season = document.documentElement.getAttribute('data-season');
    var sets = { fall: ['fall-leaf1', 'fall-leaf2', 'fall-leaf3', 'fall-leaf4'], halloween: ['halloween-bat', 'fall-leaf1', 'fall-leaf3'],
                 christmas: ['snow1', 'snow2', 'snow3'], winter: ['snow1', 'snow2', 'snow3'], valentine: ['heart1', 'heart2'],
                 spring: ['petal1', 'petal2', 'petal3'], summer: [], thanksgiving: ['fall-leaf1', 'fall-leaf2', 'fall-leaf3', 'fall-leaf4'],
                 newyear: ['confetti1', 'confetti2', 'confetti3'], stpatricks: ['clover1', 'clover2'], july4: ['star1', 'star2', 'confetti1'] };
    var list = sets[season];
    if (!hero || !list || !list.length || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var me = document.querySelector('script[src*="site.js"]');
    var base = me ? me.src.replace(/site\.js.*$/, 'decor/') : 'assets/decor/';
    var box = document.createElement('div'); box.className = 'drift'; box.setAttribute('aria-hidden', 'true');
    for (var i = 0; i < 9; i++) {
      var el = document.createElement('i');
      var s = 18 + Math.random() * 16;
      el.style.left = 'calc(' + (Math.random() * 100).toFixed(1) + '% - ' + Math.round(s + 30) + 'px)';
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
    /* a manual choice only lasts until the next sunrise (6:00) or sunset (19:00) on the visitor's clock */
    var now = new Date(), until = new Date(now);
    if (now.getHours() < 6) until.setHours(6, 0, 0, 0);
    else if (now.getHours() < 19) until.setHours(19, 0, 0, 0);
    else { until.setDate(until.getDate() + 1); until.setHours(6, 0, 0, 0); }
    try { localStorage.setItem('lhh-theme2', JSON.stringify({ t: next, until: until.getTime() })); } catch (e) {}
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

  /* ---- store: big-order packages (big-orders.html), one buyable line per package size ---- */
  function pkgPicked(card) { return card.querySelector('.tier input:checked') || card.querySelector('.tier input'); }
  document.addEventListener('change', function (e) {
    var r = e.target.closest && e.target.closest('.tier input'); if (!r) return;
    var card = r.closest('[data-package]');
    var buy = card.querySelector('[data-buy-package]'); if (buy) buy.textContent = 'Buy now · ' + money(Number(r.getAttribute('data-price')));
    var q = card.querySelector('[data-pkg]'); if (q) q.setAttribute('data-qty', r.getAttribute('data-size'));
  });
  document.addEventListener('click', function (e) {
    var b = e.target.closest('[data-buy-package]'); if (!b) return;
    var r = pkgPicked(b.closest('[data-package]')); if (!r) return;
    var size = Number(r.getAttribute('data-size'));
    addLine({ id: r.value, kind: 'package', name: r.getAttribute('data-title'), count: size, price: Number(r.getAttribute('data-price')),
              detail: size + ' magnets · we plan the design with you by email after checkout' }, true);
    openCart();
  });
  function addLine(line, quiet) {   /* quiet: the cart drawer opens right after, so no toast over it */
    var same = line.kind !== 'custom' && cart.find(function (l) { return l.id === line.id && l.kind === line.kind; });
    if (same) same.qty += line.qty || 1;
    else { if (!line.qty) line.qty = 1; cart.push(line); }
    save(); render(); if (!quiet) toast(line.name + ' added to cart');
  }
  /* ---- /store ---- */

  window.LHH = {
    addCustom: function (item) { item.kind = 'custom'; item.qty = 1; cart.push(item); render(); toast('Photo magnets added to cart'); openCart(); },
    money: money,
    toast: toast,
    /* store: used by assets/store.js, checkout.js and orders.js */
    cart: function () { return cart; },
    totals: totals,
    addLine: addLine,
    save: function () { save(); render(); },
    clear: function () { cart.length = 0; save(); render(); },
    openCart: openCart,
    closeCart: closeCart
  };
  render();
})();
