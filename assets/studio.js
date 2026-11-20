/* Little Hive House: the design gallery and the studio on the bulk-order pages. The customer filters the designs by
   kind of business or event, opens one and makes it theirs (colors, words, their logo or photo, the QR link), sees it
   change at once, and buys the pack: one cart line (kind "package", style = the design) carrying their choices for the
   proof. The logo and the photo are uploaded to the store when they buy (uploads/<uid>/<design id>/1.png and 2.jpg).
   Drawing: assets/designer.js. */
(function () {
  'use strict';
  var D = window.LHHDesigner, S = window.LHHStore;
  var gal = document.querySelector('[data-gallery]'), dlg = document.querySelector('[data-studio]');
  if (!D || !gal || !dlg) return;
  var $ = function (s, r) { return (r || dlg).querySelector(s); };

  /* ---------------------------------------------------------------- the gallery, like a streaming app
     home: the groups (Restaurants & food, Health…) or, on Personalize, the themes; a group opens its kinds of business;
     a kind opens rows of designs by what the magnet is for (Bring customers back, Scan me…), each row scrolls sideways
     and "See all" opens it as a grid. The search box finds a kind from any word (English or Portuguese). The phone's
     back button walks back up (#kind-pizza in the address). */
  var DATA = D.data || {}, SETS = DATA.sets || {}, ROWN = DATA.rowNames || {}, page = gal.getAttribute('data-page');
  var only = gal.getAttribute('data-dz-only');
  var home = gal.querySelector('[data-dz-home]'), view = gal.querySelector('[data-dz-view]'), rowsBox = gal.querySelector('[data-dz-rows]');
  var grps = gal.querySelector('[data-dz-grps]'), kbox = gal.querySelector('[data-dz-kinds-box]'), feat = gal.querySelector('[data-dz-feat]');
  var search = gal.querySelector('[data-dz-search]'), none = gal.querySelector('[data-dz-none]');
  var assetBase = (document.querySelector('script[src*="studio.js"]').src || '').replace(/assets\/studio\.js.*$/, '');
  /* plain letters to compare (accents and case don't matter) */
  function plain(t) { return String(t || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function art(el) {
    var il = el.getAttribute('data-il'), k = el.getAttribute('data-icon');
    if (il && D.illus[il]) el.innerHTML = '<svg viewBox="0 0 100 100" width="100%" height="100%">' + D.illus[il] + '</svg>';
    else if (D.icons[k]) el.innerHTML = '<svg viewBox="0 0 64 64" width="100%" height="100%">' + D.icons[k].split('{c}').join('currentColor') + '</svg>';
  }
  gal.querySelectorAll('.dz-ki,.dz-gi').forEach(art);

  function card(slug) {
    return '<li class="dz-card"><button type="button" data-design="' + slug + '" aria-label="Open this design"><img src="' + assetBase + 'assets/occasions/' + slug + '.webp" alt="" width="360" height="360" loading="lazy" decoding="async"><span class="dz-go">Make it yours →</span></button></li>';
  }
  function row(title, slugs, key) {
    if (!slugs.length) return '';
    return '<div class="dz-row" data-row="' + (key || '') + '"><div class="dz-rh"><h4>' + D.esc(title) + ' <small>' + slugs.length + '</small></h4>' +
      (slugs.length > 4 ? '<button type="button" class="linkish" data-dz-all>See all</button>' : '') + '</div>' +
      '<div class="dz-track"><button type="button" class="dz-arrow dz-prevb" data-dz-scroll="-1" aria-label="Scroll left" tabindex="-1">‹</button><ul class="dz-strip">' + slugs.map(card).join('') + '</ul>' +
      '<button type="button" class="dz-arrow dz-nextb" data-dz-scroll="1" aria-label="Scroll right" tabindex="-1">›</button></div></div>';
  }

  /* featured rows on the first screen (the most loved designs), so there is something to tap right away */
  if (feat && DATA.featured && DATA.featured[page]) feat.innerHTML = DATA.featured[page].map(function (r) { return row(r[0], r[1]); }).join('');

  var level = 'home', curGroup = '', curSet = '';
  function showKinds(g, words) {
    var q = plain(words || '').trim().split(/\s+/).filter(Boolean), n = 0;
    gal.querySelectorAll('.dz-kind').forEach(function (b) {
      var ok = q.length ? q.every(function (w) { return plain(b.textContent + ' ' + b.getAttribute('data-words') + ' ' + b.getAttribute('data-group')).indexOf(w) >= 0; })
        : (!g || b.getAttribute('data-group') === g);
      b.hidden = !ok; if (ok) n++;
    });
    /* nothing found: the designs for any business, so there is always something to start from */
    if (q.length && !n) gal.querySelectorAll('.dz-kind[data-set="general"],.dz-kind[data-set="startup"]').forEach(function (b) { b.hidden = false; });
    if (kbox) kbox.hidden = !(g || q.length || !grps);
    if (grps) grps.hidden = !!(g || q.length);
    var t = gal.querySelector('[data-dz-ktitle]');
    if (t) t.textContent = q.length ? (n ? 'Results' : '') : g;
    var back = gal.querySelector('[data-dz-back]');
    if (back) back.hidden = !(g || q.length);
    if (none) none.hidden = !(q.length && !n);
    if (feat) feat.hidden = !!(g || q.length);
  }
  function openSet(k, push) {
    var meta = SETS[k]; if (!meta) return;
    curSet = k; level = 'set';
    if (home) home.hidden = true;
    if (feat) feat.hidden = true;
    view.hidden = false;
    var vt = gal.querySelector('[data-dz-vtitle]');
    if (vt) vt.textContent = meta.name;
    rowsBox.innerHTML = '<p class="hint">Loading the designs…</p>';
    D.load(k).then(function (list) {
      if (curSet !== k) return;
      var mine = list.filter(function (d) { return d.set === k; });
      var rows = (meta.rows || []).map(function (r) { return row(ROWN[r] || r, mine.filter(function (d) { return d.row === r; }).map(function (d) { return d.slug; }), r); }).join('');
      rowsBox.innerHTML = rows || '<p class="hint">No designs here yet.</p>';
      arrows();
    }, function () { rowsBox.innerHTML = '<p class="hint">We couldn’t load the designs. Check the connection and try again.</p>'; });
    if (push !== false && !only) history.pushState({ dz: k }, '', '#kind-' + k);
    if (!only) { var top = gal.getBoundingClientRect().top + window.scrollY - 70; if (Math.abs(window.scrollY - top) > 80) window.scrollTo({ top: top, behavior: 'smooth' }); }
    if (window.lhhTrack) window.lhhTrack('view_item_list', { item_list_id: k, item_list_name: meta.name });
  }
  function goHome(g) {
    level = g ? 'group' : 'home'; curGroup = g || ''; curSet = '';
    if (home) home.hidden = false;
    view.hidden = true;
    if (search && !g) search.value = '';
    showKinds(curGroup, search ? search.value : '');
  }
  /* the arrows only where a row can scroll (a mouse; on a phone the finger does it) */
  function arrows() {
    gal.querySelectorAll('.dz-track').forEach(function (t) {
      var s = t.querySelector('.dz-strip'), l = t.querySelector('.dz-prevb'), r = t.querySelector('.dz-nextb');
      var upd = function () { l.hidden = s.scrollLeft < 8; r.hidden = s.scrollLeft + s.clientWidth > s.scrollWidth - 8; };
      if (!s.dataset.on) { s.dataset.on = 1; s.addEventListener('scroll', upd, { passive: true }); }
      upd();
    });
  }
  window.addEventListener('resize', arrows);
  window.addEventListener('popstate', function () {
    var m = /^#kind-([a-z0-9-]+)$/.exec(location.hash);
    if (m && SETS[m[1]]) openSet(m[1], false); else if (!only) goHome(curGroup && level === 'set' ? curGroup : '');
  });

  if (search) search.addEventListener('input', function () {
    if (level === 'set') goHome('');
    curGroup = ''; showKinds('', search.value);
  });
  gal.addEventListener('click', function (e) {
    var t = e.target, el;
    if ((el = t.closest('[data-dz-grp]'))) { curGroup = el.getAttribute('data-dz-grp'); level = 'group'; showKinds(curGroup, ''); history.pushState({ dzg: curGroup }, '', '#designs'); kbox.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); return; }
    if ((el = t.closest('.dz-kind'))) { openSet(el.getAttribute('data-set')); return; }
    if (t.closest('[data-dz-back]')) { if (search) search.value = ''; goHome(''); return; }
    if (t.closest('[data-dz-up]')) { if (history.state && history.state.dz) history.back(); else goHome(SETS[curSet] && grps ? SETS[curSet].group : ''); return; }
    if ((el = t.closest('[data-dz-scroll]'))) { var st = el.parentNode.querySelector('.dz-strip'); st.scrollBy({ left: Number(el.getAttribute('data-dz-scroll')) * st.clientWidth * .85, behavior: 'smooth' }); return; }
    if ((el = t.closest('[data-dz-all]'))) { var sec = el.closest('.dz-row'), open_ = sec.classList.toggle('dz-open'); el.textContent = open_ ? 'Show less' : 'See all'; if (!open_) sec.scrollIntoView({ block: 'nearest' }); arrows(); return; }
    var cd = t.closest('[data-design]');
    if (cd) open(cd.getAttribute('data-design'));
  });
  if (only) openSet(only, false);
  else {
    var km = /^#kind-([a-z0-9-]+)$/.exec(location.hash);
    if (km && SETS[km[1]]) { history.replaceState({ dz: km[1] }, '', location.hash); openSet(km[1], false); } else showKinds('', '');
  }
  arrows();

  /* the drawings to pick from (the same ones the designs use) */
  var box = dlg.querySelector('[data-dz-icons]');
  if (box) box.innerHTML = Object.keys(D.illus).map(function (k) {
    return '<button type="button" class="dz-ic dz-il" data-icon="il:' + k + '" aria-label="' + k + '"><svg viewBox="0 0 100 100" width="34" height="34">' + D.illus[k] + '</svg></button>';
  }).join('') + Object.keys(D.icons).map(function (k) {
    return '<button type="button" class="dz-ic" data-icon="' + k + '" aria-label="' + k + '"><svg viewBox="0 0 64 64" width="30" height="30">' + D.icons[k].split('{c}').join('currentColor') + '</svg></button>';
  }).join('');

  /* our own photos to pick from (free stock photos, assets/stock), drawn the first time a photo design opens */
  var stockBox = dlg.querySelector('[data-dz-stock]');
  function fillStock() {
    if (!stockBox || stockBox.childElementCount || !D.stock.length) return;
    var base = (document.querySelector('script[src*="studio.js"]').src || '').replace(/assets\/studio\.js.*$/, '');
    stockBox.innerHTML = D.stock.map(function (n) {
      return '<button type="button" class="dz-st" data-stock="' + n + '" aria-label="' + n.replace(/-\d+$/, '') + '"><img src="' + base + 'assets/stock/t/' + n + '.webp" alt="" width="110" height="110" loading="lazy" decoding="async"></button>';
    }).join('');
  }

  /* the photos that fit this design come first: its own kind (a pizza design shows pizzas), then its page's */
  var PRI = {
    business: ['pizza', 'bakery', 'coffee', 'food', 'chef', 'barber', 'salon', 'gym', 'yoga', 'dentist', 'house', 'kitchen', 'home-interior', 'cleaning', 'garden', 'car', 'mechanic', 'vet', 'flowers', 'team', 'handshake', 'church', 'school', 'football'],
    weddings: ['wedding', 'bride', 'couple', 'engagement', 'flowers', 'sunset'],
    graduation: ['grad-girl', 'grad', 'school', 'party', 'family'],
    parties: ['birthday', 'party', 'baby', 'toddler', 'kids', 'family', 'grandparents', 'dog', 'puppy', 'dog-small', 'cat', 'beach', 'travel', 'christmas-family']
  };
  function sortStock() {
    if (!stockBox) return;
    var pu = /stock\/([a-z-]+?)-\d+\.webp/.exec(d.opt.photoUrl || ''), own = pu ? pu[1] : d.slug.split('-')[0], list = PRI[d.page] || PRI.parties;
    var rank = function (n) { var k = n.replace(/-\d+$/, ''); if (k === own || k.indexOf(own) === 0) return 0; var i = list.indexOf(k); return i < 0 ? 100 : i + 1; };
    Array.prototype.slice.call(stockBox.children).sort(function (a, b) { return rank(a.getAttribute('data-stock')) - rank(b.getAttribute('data-stock')); })
      .forEach(function (el) { stockBox.appendChild(el); });
    stockBox.scrollTop = 0;
  }

  /* ---------------------------------------------------------------- the studio */
  var LABEL = {
    name: 'Name', sub: 'Small line', head: 'Headline', line: 'Message', phone: 'Phone', web: 'Website or @',
    since: 'Side note', kicker: 'Label', offer: 'Offer', mono: 'Initials', a: 'First name', b: 'Second name', date: 'Date',
    place: 'Place', year: 'Year', school: 'School or team', hand0: 'Written on line 1', hand1: 'Written on line 2'
  };
  var MULTI = { head: 1, line: 1 };
  var d = null, ch = null, logoBlob = null, photoBlob = null, did = '';

  function rid() { return 'd' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8); }
  function draw() { if (d) D.paint($('[data-dz-prev]'), d, ch, { mark: true }); }
  /* the preview follows its box (the dialog opening, a phone turning) */
  if (window.ResizeObserver) {
    var lastW = 0;
    new ResizeObserver(function (en) { var w = Math.round(en[0].contentRect.width); if (w && w !== lastW) { lastW = w; draw(); } }).observe($('[data-dz-prev]'));
  }

  function field(k, v) {
    var lab = LABEL[k] || '', id = 'dz-' + k;
    if (/^items\d$/.test(k)) lab = 'Service ' + (+k.slice(5) + 1);
    var m = /^rows(\d)([ab])$/.exec(k);
    if (m) lab = (m[2] === 'a' ? 'Line ' + (+m[1] + 1) : 'Line ' + (+m[1] + 1) + ', right side');
    var multi = MULTI[k] || String(v).indexOf('\n') >= 0;
    var input = multi ? '<textarea id="' + id + '" rows="2" maxlength="120" data-dz-t="' + k + '">' + D.esc(v) + '</textarea>'
      : '<input id="' + id + '" maxlength="80" data-dz-t="' + k + '" value="' + D.esc(v) + '">';
    return '<div class="field dz-f' + (m ? ' dz-half' : '') + '"><label for="' + id + '">' + lab + '</label>' + input + '</div>';
  }

  function colorsNow() {
    if (ch.colors) return ch.colors;
    return { bg: d.colors.bg, ink: d.colors.ink, ac: d.colors.ac };
  }
  function setPickers() {
    var c = colorsNow();
    dlg.querySelectorAll('[data-dz-c]').forEach(function (inp) { var v = c[inp.getAttribute('data-dz-c')]; if (/^#[0-9a-f]{6}$/i.test(v)) inp.value = v; });
    dlg.querySelectorAll('.dz-pal').forEach(function (b) {
      var p = D.palettes[b.getAttribute('data-pal')];
      b.setAttribute('aria-pressed', ch.colors && p && p.bg === ch.colors.bg && p.ink === ch.colors.ink && p.ac === ch.colors.ac ? 'true' : 'false');
    });
    $('[data-dz-orig]').setAttribute('aria-pressed', ch.colors ? 'false' : 'true');
  }

  function open(slug) {
    if (!D.get(slug)) { D.need(slug).then(function (x) { if (x) open(slug); }); return; }
    d = D.get(slug); if (!d) return;
    ch = { text: {} }; logoBlob = photoBlob = null; did = rid();
    $('[data-dz-title]').textContent = d.title;
    $('[data-dz-fields]').innerHTML = Object.keys(d.text).map(function (k) { return field(k, d.text[k]); }).join('') +
      (D.hasQR(d) ? '<div class="field dz-f"><label for="dz-url">Link for the QR code</label><input id="dz-url" type="url" inputmode="url" maxlength="200" placeholder="https://your-site.com" data-dz-url></div>' : '');
    $('[data-dz-photo-box]').hidden = !D.hasPhoto(d);
    if (!$('[data-dz-photo-box]').hidden) { fillStock(); sortStock(); }
    dlg.querySelectorAll('.dz-st').forEach(function (b) { b.setAttribute('aria-pressed', 'false'); });
    $('[data-dz-logo-name]').textContent = '';
    $('[data-dz-photo-name]').textContent = '';
    $('[data-dz-nologo]').hidden = true;
    $('[data-dz-msg]').classList.remove('err');
    $('[data-dz-msg]').textContent = $('[data-dz-msg]').getAttribute('data-default');
    var ic = d.opt.icon;
    dlg.querySelectorAll('.dz-ic').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-icon') === ic ? 'true' : 'false'); });
    $('[data-dz-icons-box]').hidden = !ic;
    setPickers();
    price();
    if (dlg.showModal) { if (!dlg.open) dlg.showModal(); } else dlg.setAttribute('open', '');
    document.documentElement.classList.add('dz-lock');
    requestAnimationFrame(draw);
    if (window.lhhTrack) window.lhhTrack('select_item', { item_list_name: 'designs', items: [{ item_id: d.slug, item_name: d.title }] });
  }
  function close() { if (dlg.close) dlg.close(); else dlg.removeAttribute('open'); document.documentElement.classList.remove('dz-lock'); }
  dlg.addEventListener('close', function () { document.documentElement.classList.remove('dz-lock'); });

  function price() {
    var o = $('[data-dz-pack]').selectedOptions[0];
    var pr = Number(o.getAttribute('data-price'));
    $('[data-dz-buy]').innerHTML = 'Buy now · ' + (window.LHH && LHH.priceHtml ? LHH.priceHtml(pr) : '$' + pr);
  }

  /* the logo: PNG with its transparency, at most 1200 px (an SVG is drawn into a PNG too) */
  function toImage(file, kind) {
    return new Promise(function (res, rej) {
      var u = URL.createObjectURL(file), im = new Image();
      im.onload = function () {
        var max = kind === 'logo' ? 1200 : 2000, w = im.naturalWidth || 1200, h = im.naturalHeight || 1200, k = Math.min(1, max / Math.max(w, h));
        if (!im.naturalWidth) { w = h = 1200; k = 1; }
        var c = document.createElement('canvas'); c.width = Math.round(w * k); c.height = Math.round(h * k);
        var x = c.getContext('2d');
        if (kind !== 'logo') { x.fillStyle = '#fff'; x.fillRect(0, 0, c.width, c.height); }
        x.drawImage(im, 0, 0, c.width, c.height);
        URL.revokeObjectURL(u);
        c.toBlob(function (b) { b ? res(b) : rej(new Error('blob')); }, kind === 'logo' ? 'image/png' : 'image/jpeg', .9);
      };
      im.onerror = function () { URL.revokeObjectURL(u); rej(new Error('read')); };
      im.src = u;
    });
  }

  dlg.addEventListener('input', function (e) {
    var t = e.target;
    if (t.hasAttribute('data-dz-t')) { ch.text[t.getAttribute('data-dz-t')] = t.value; draw(); return; }
    if (t.hasAttribute('data-dz-url')) { var u = t.value.trim(); ch.url = u ? (/^https?:\/\//i.test(u) ? u : 'https://' + u) : ''; draw(); return; }
    if (t.hasAttribute('data-dz-c')) { var c = colorsNow(); ch.colors = { bg: c.bg, ink: c.ink, ac: c.ac }; ch.colors[t.getAttribute('data-dz-c')] = t.value.toUpperCase(); setPickers(); draw(); }
  });
  dlg.addEventListener('change', function (e) {
    var t = e.target;
    if (t.hasAttribute('data-dz-pack')) { price(); return; }
    if (t.hasAttribute('data-dz-logo') || t.hasAttribute('data-dz-photo')) {
      var f = t.files && t.files[0], kind = t.hasAttribute('data-dz-logo') ? 'logo' : 'photo';
      if (!f) return;
      var msg = $('[data-dz-msg]');
      toImage(f, kind).then(function (b) {
        if (kind === 'logo') { logoBlob = b; if (ch.logo) URL.revokeObjectURL(ch.logo); ch.logo = URL.createObjectURL(b); $('[data-dz-nologo]').hidden = false; $('[data-dz-logo-name]').textContent = f.name; }
        else { photoBlob = b; if (ch.photo && /^blob:/.test(ch.photo)) URL.revokeObjectURL(ch.photo); ch.stock = ''; ch.photo = URL.createObjectURL(b); $('[data-dz-photo-name]').textContent = f.name; dlg.querySelectorAll('.dz-st').forEach(function (x) { x.setAttribute('aria-pressed', 'false'); }); }
        msg.classList.remove('err'); draw();
      }, function () {
        msg.textContent = 'We couldn’t open that file here. Try a PNG or JPG, or send it to us by email after checkout.'; msg.classList.add('err');
      });
      t.value = '';
    }
  });
  dlg.addEventListener('click', function (e) {
    var t = e.target;
    if (t.closest('[data-dz-close]')) { close(); return; }
    if (t === dlg) { close(); return; }   /* a click on the backdrop */
    var p = t.closest('.dz-pal');
    if (p) { var c = D.palettes[p.getAttribute('data-pal')]; ch.colors = { bg: c.bg, ink: c.ink, ac: c.ac }; setPickers(); draw(); return; }
    if (t.closest('[data-dz-orig]')) { ch.colors = null; setPickers(); draw(); return; }
    var sp = t.closest('.dz-st');
    if (sp) {
      if (ch.photo && /^blob:/.test(ch.photo)) URL.revokeObjectURL(ch.photo);
      photoBlob = null; ch.stock = sp.getAttribute('data-stock'); ch.photo = 'assets/stock/' + ch.stock + '.webp';
      dlg.querySelectorAll('.dz-st').forEach(function (b) { b.setAttribute('aria-pressed', b === sp ? 'true' : 'false'); });
      $('[data-dz-photo-name]').textContent = ''; draw(); return;
    }
    var i = t.closest('.dz-ic');
    if (i) { ch.icon = i.getAttribute('data-icon'); dlg.querySelectorAll('.dz-ic').forEach(function (b) { b.setAttribute('aria-pressed', b === i ? 'true' : 'false'); }); draw(); return; }
    if (t.closest('[data-dz-nologo]')) { if (ch.logo) URL.revokeObjectURL(ch.logo); ch.logo = ''; logoBlob = null; $('[data-dz-nologo]').hidden = true; $('[data-dz-logo-name]').textContent = ''; draw(); return; }
    if (t.closest('[data-dz-buy]')) buy(false);
    if (t.closest('[data-dz-digital]')) buy(true);
  });

  function changed() {
    var out = {};
    Object.keys(ch.text).forEach(function (k) { if (ch.text[k] !== d.text[k]) out[k] = String(ch.text[k]).slice(0, 120); });
    return out;
  }

  function upload(blob, n, ext) {
    return S.ready().then(function () { return S.ensureUser(); }).then(function (u) {
      var path = 'uploads/' + u.uid + '/' + did + '/' + n + '.' + ext;
      return S.upload(path, blob, { contentType: ext === 'png' ? 'image/png' : 'image/jpeg', customMetadata: { design: d.slug } }, function () {}).then(function () { return path; });
    });
  }

  /* no "save image" on the preview (right click, long press, dragging it out) */
  ['contextmenu', 'dragstart'].forEach(function (ev) { $('[data-dz-prev]').addEventListener(ev, function (e) { e.preventDefault(); }); });

  var busy = false;
  /* the design in high resolution, without the preview mark (assets/designer.js toPng), uploaded as 3.png: the file the
     customer gets by email (a design file order, or free with a magnet pack) */
  function drawFile() {
    if (!D.toPng) return Promise.resolve(null);
    var c = { colors: ch.colors, text: ch.text, icon: ch.icon, url: ch.url, logo: ch.logo, photo: ch.photo };
    return D.toPng(d, c, 1200).then(function (b) { return upload(b, 3, 'png'); });
  }

  function buy(digital) {
    if (busy) return;
    var msg = $('[data-dz-msg]'), btn = digital ? $('[data-dz-digital]') : $('[data-dz-buy]');
    if (D.hasQR(d) && ch.url && !/^https?:\/\/[^\s/$.?#]+\.[^\s]{2,}$/i.test(ch.url)) {
      msg.textContent = 'The QR link doesn’t look like a web address.'; msg.classList.add('err'); $('[data-dz-url]').focus(); return;
    }
    busy = true; btn.disabled = true; if (!digital) btn.textContent = 'One moment…';
    var o = $('[data-dz-pack]').selectedOptions[0], n = Number(o.getAttribute('data-size'));
    if (digital) o = { value: 'digital-file', getAttribute: function (k) { return { 'data-size': '0', 'data-price': btn.getAttribute('data-price'), 'data-title': btn.getAttribute('data-title') }[k]; } }, n = 0;
    var design = { slug: d.slug, text: changed() };
    if (ch.colors) design.colors = ch.colors;
    if (ch.icon && ch.icon !== d.opt.icon) design.icon = ch.icon;
    if (ch.url) design.url = ch.url;
    if (ch.stock && !photoBlob) design.stock = ch.stock;
    var jobs = [];
    if (logoBlob) jobs.push(upload(logoBlob, 1, 'png').then(function (p) { design.logo = p; }));
    if (photoBlob) jobs.push(upload(photoBlob, 2, 'jpg').then(function (p) { design.photo = p; }));
    if (jobs.length) { msg.classList.remove('err'); msg.textContent = 'Sending your ' + (logoBlob ? 'logo' : 'photo') + '…'; }
    var file = null;
    Promise.all(jobs).then(function () {
      msg.classList.remove('err'); msg.textContent = digital ? 'Making your file…' : 'One moment…';
      /* the file: a must for a design file order; for a magnet pack a gift, so a browser that can't draw it just skips it */
      return drawFile().then(function (p) { file = p; }, function (e) { if (digital) throw e; });
    }).then(function () {
      var nm = (design.text.name || d.text.name || d.text.head || d.text.a || '').replace(/\n/g, ' ');
      var line = {
        id: o.value, name: o.getAttribute('data-title'), count: n, price: Number(o.getAttribute('data-price')), qty: 1, style: d.slug, design: design,
        detail: digital ? 'Digital file · ' + d.title + (nm ? ' · ' + nm : '') + ' · sent to your email · no magnet'
          : n + ' magnets · ' + d.title + (nm ? ' · ' + nm : '') + (design.logo ? ' · with your logo' : '') + ' · proof before we print' + (file ? ' · the digital file free' : '')
      };
      if (file) line.file = file;
      if (digital) line.digital = true;
      window.LHH.addPackage(line);
      if (window.lhhTrack) window.lhhTrack('add_to_cart', { currency: 'USD', value: Number(o.getAttribute('data-price')), items: [{ item_id: o.value, item_name: d.title, price: Number(o.getAttribute('data-price')), quantity: 1 }] });
      close();
    }, function () {
      msg.textContent = digital ? 'We couldn’t make your file in this browser. Try again, or try Chrome or Safari up to date.'
        : 'We couldn’t send your file. Check the connection and try again, or buy without it and email it to us after checkout.';
      msg.classList.add('err');
    }).then(function () { busy = false; btn.disabled = false; price(); });
  }

  /* "Use this style" anywhere on the page, or a link to #design-<slug>, opens the studio */
  var m = /^#design-([a-z0-9-]+)$/.exec(location.hash);
  if (m) setTimeout(function () { open(m[1]); }, 300);
  window.LHHStudio = { open: open };
})();
