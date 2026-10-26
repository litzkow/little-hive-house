/* Little Hive House: the custom photo magnet builder. Needs site.js first.
   Every photo keeps its own frame, caption and placement. Tapping a photo opens the frame studio: a big live
   preview (drag to move the photo, pinch / slider to zoom), the caption field (for caption frames) and every frame
   drawn as a mini preview of that same photo. The placement prints exactly as shown (functions/crop.js). */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var NS = 'http://www.w3.org/2000/svg';
  var DATA = window.LHH_FRAMES || { list: [], groups: [] };
  var ALL = DATA.list || [];
  var FR = {};
  ALL.forEach(function (f) { FR[f.id] = f; });
  /* frames of the first edition stay in the list (old carts still draw) but are not offered any more */
  var LIST = ALL.filter(function (f) { return !f.hidden; });
  var BASE = window.LHH_FRAMES_BASE || 'assets/frames/';
  var MIN_PHOTO_PX = 600;
  var photos = [];
  var defaultFrame = 'none';
  /* links from the occasion cards (?frame=wedding) start new photos with that frame */
  try { var qf = new URLSearchParams(location.search).get('frame'); if (qf && FR[qf]) defaultFrame = qf; } catch (e) { /* old browser */ }
  var current = -1;
  var group = '';

  function packSize() { return Number(document.querySelector('input[name="pack"]:checked').value); }
  function packPrice() { return Number(document.querySelector('input[name="pack"]:checked').getAttribute('data-price')); }
  function frameOf(p) { return FR[p.frame] || FR.none || { id: 'none', name: 'No border', window: [0, 0, 600, 600], caption: null }; }
  /* the frame's caption in the lettering the customer picked (caption.styles: hand, script, classic, modern...) */
  function capOf(f, key) {
    var c = f.caption; if (!c) return null;
    var st = key && c.styles && c.styles[key]; if (!st) return c;
    var o = {}, k; for (k in c) o[k] = c[k]; for (k in st) o[k] = st[k];
    return o;
  }
  function capText(f, s, key) {
    var c = capOf(f, key);
    if (!c || !s) return '';
    s = s.trim().slice(0, c.max);
    return c.upper ? s.toUpperCase() : s;
  }

  /* ---------- drawing one magnet: photo in the window, frame overlay on top, caption last ---------- */
  function node(tag, attrs, parent) {
    var n = document.createElementNS(NS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function textNode(svg, c, s, x, y, size, ls, fam, style, weight, color, rot) {
    var t = node('text', { x: x + (ls ? ls / 2 : 0), y: y, 'text-anchor': 'middle', 'font-family': fam, 'font-style': style, 'font-weight': weight,
                           'font-size': size, fill: color }, svg);
    if (ls) t.setAttribute('letter-spacing', ls);
    if (rot) t.setAttribute('transform', 'rotate(' + rot + ' ' + x + ' ' + y + ')');
    t.textContent = s;
    return t;
  }
  /* where the customer moved / zoomed the photo: crop {x, y, z}, same math as functions/crop.js region() and the print sheet */
  var ZMAX = 4;
  function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }
  function region(w, h, ww, wh, c) {
    c = c || { x: 0.5, y: 0.5, z: 1 };
    var s = Math.max(ww / w, wh / h) * clamp(c.z || 1, 1, ZMAX);
    var rw = Math.min(w, ww / s), rh = Math.min(h, wh / s);
    return { left: clamp(c.x * w - rw / 2, 0, w - rw), top: clamp(c.y * h - rh / 2, 0, h - rh), width: rw, height: rh };
  }
  function viewBoxOf(p, w) { var r = region(p.w, p.h, w[2], w[3], p.crop); return r.left + ' ' + r.top + ' ' + r.width + ' ' + r.height; }
  function magnet(p, f, caption, cls) {
    var svg = node('svg', { viewBox: '0 0 600 600', 'aria-hidden': 'true', focusable: 'false' });
    if (cls) svg.setAttribute('class', cls);
    var w = f.window;
    if (f.id !== 'none') node('rect', { width: 600, height: 600, fill: '#FFFFFF' }, svg);
    if (p.w && p.h) {
      /* a window onto the photo: the nested svg clips it, its viewBox is the part of the photo that shows */
      var win = node('svg', { x: w[0], y: w[1], width: w[2], height: w[3], viewBox: viewBoxOf(p, w), preserveAspectRatio: 'none', 'class': 'ph' }, svg);
      node('image', { href: p.url, x: 0, y: 0, width: p.w, height: p.h, preserveAspectRatio: 'none' }, win);
    } else {
      node('image', { href: p.url, x: w[0], y: w[1], width: w[2], height: w[3], preserveAspectRatio: 'xMidYMid slice' }, svg);
    }
    if (f.id !== 'none') node('image', { href: BASE + f.id + '.svg', x: 0, y: 0, width: 600, height: 600 }, svg);
    var c = capOf(f, p.capStyle), s = capText(f, caption, p.capStyle);
    if (c && s) {
      if (c.kicker) {
        var k = c.kicker;
        textNode(svg, k, k.text, c.x, k.y, k.size, k.ls || 0, k.family, k.style, k.weight, k.color, 0);
      }
      var t = textNode(svg, c, s, c.x, c.y, c.size, c.ls, c.family, c.style, c.weight, c.color, c.rot);
      t.setAttribute('data-fit', c.size + ' ' + c.min + ' ' + c.w);
    }
    return svg;
  }
  /* shrink captions that run wider than the frame allows (the print tool uses the same rule) */
  function fitIn(root) {
    var ts = (root || document).querySelectorAll('text[data-fit]');
    Array.prototype.forEach.call(ts, function (t) {
      var fit = String(t.getAttribute('data-fit')).split(' ').map(Number);
      if (fit.length < 3 || !fit[0]) return;
      var c = { size: fit[0], min: fit[1], w: fit[2] }, size = c.size;
      t.setAttribute('font-size', size);
      for (var i = 0; i < 4; i++) {
        var L; try { L = t.getComputedTextLength(); } catch (e) { return; }
        if (!L || L <= c.w) break;
        size = Math.max(c.min, Math.floor(size * c.w / L));
        t.setAttribute('font-size', size);
        if (size === c.min) break;
      }
    });
  }
  function draw(p, f, caption, cls) { var s = magnet(p, f, caption, cls); s.setAttribute('data-frame', f.id); return s; }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { fitIn(document); });

  /* ---------- the photo grid ---------- */
  function describe(p, i) {
    var f = frameOf(p), s = capText(f, p.caption, p.capStyle);
    return 'Photo ' + (i + 1) + ': ' + f.name + ' frame' + (s ? ', caption ' + s : '') + (p.low ? ', low resolution' : '') + '. Choose frame';
  }
  function renderBuilder() {
    var size = packSize();
    var grid = $('thumbs'); grid.innerHTML = '';
    photos.forEach(function (p, i) {
      var li = document.createElement('li'); li.className = 'thumb' + (p.low ? ' low' : '');
      var b = document.createElement('button'); b.type = 'button'; b.className = 'thumb-btn'; b.setAttribute('data-i', i);
      b.setAttribute('aria-label', describe(p, i)); b.setAttribute('aria-haspopup', 'dialog');
      b.appendChild(draw(p, frameOf(p), p.caption));
      var edit = document.createElement('span'); edit.className = 'thumb-edit'; edit.setAttribute('aria-hidden', 'true'); edit.textContent = 'Edit';
      b.appendChild(edit);
      b.onclick = function () { openStudio(i); };
      var nm = document.createElement('span'); nm.className = 'thumb-name'; nm.textContent = frameOf(p).name; nm.setAttribute('aria-hidden', 'true');
      var x = document.createElement('button'); x.type = 'button'; x.className = 'thumb-x'; x.textContent = '×'; x.setAttribute('aria-label', 'Remove photo ' + (i + 1));
      x.onclick = function () { removePhoto(i); };
      li.append(b, nm, x);
      if (p.low) { var t = document.createElement('span'); t.className = 'lowtag'; t.textContent = 'Low quality'; t.setAttribute('aria-hidden', 'true'); b.appendChild(t); }
      grid.appendChild(li);
    });
    for (var k = photos.length; k < size; k++) {
      var e = document.createElement('li'); e.className = 'thumb empty'; e.setAttribute('aria-hidden', 'true');
      var sp = document.createElement('span'); sp.textContent = k + 1; e.appendChild(sp); grid.appendChild(e);
    }
    fitIn(grid);
    $('frame-teaser').hidden = photos.length > 0;
    $('magnets-hint').hidden = photos.length === 0;
    var lowCount = photos.filter(function (p) { return p.low; }).length;
    var rn = $('res-note');
    if (lowCount) {
      rn.textContent = (lowCount === 1 ? '1 photo is' : lowCount + ' photos are') + ' too small and may print blurry. For sharp magnets, use the original photo from your camera roll, not a screenshot or a photo saved from a chat app.';
      rn.hidden = false;
    } else { rn.hidden = true; }
    var c = $('counter');
    if (photos.length > size) { c.textContent = photos.length + ' photos added. This pack holds ' + size + ', so remove ' + (photos.length - size) + ' or pick a bigger pack.'; c.classList.add('warn'); }
    else { c.textContent = photos.length + ' of ' + size + ' photos added' + (photos.length && photos.length < size ? '. We will repeat your favorites to fill the pack, or tell us in the notes.' : ''); c.classList.remove('warn'); }
    $('builder-total').textContent = LHH.money(packPrice());
    $('add-custom').disabled = !(photos.length >= 1 && photos.length <= size && $('rights').checked);
  }
  function refreshThumb(i) {
    var b = document.querySelector('.thumb-btn[data-i="' + i + '"]'); if (!b) return;
    var p = photos[i];
    b.replaceChild(draw(p, frameOf(p), p.caption), b.querySelector('svg'));
    b.setAttribute('aria-label', describe(p, i));
    b.parentNode.querySelector('.thumb-name').textContent = frameOf(p).name;
    fitIn(b);
  }
  function removePhoto(i) {
    URL.revokeObjectURL(photos[i].url); photos.splice(i, 1); renderBuilder();
    var next = document.querySelector('.thumb-btn[data-i="' + Math.min(i, photos.length - 1) + '"]');
    (next || $('drop')).focus();
  }

  function addFiles(files) {
    Array.prototype.forEach.call(files, function (f) {
      if (f.type.indexOf('image/') !== 0) return;
      var p = { name: f.name, url: URL.createObjectURL(f), blob: f, low: false, frame: defaultFrame, caption: '', capStyle: null, crop: null, w: 0, h: 0 };
      photos.push(p);
      /* the size (upright, as the browser shows it) lets the customer move and zoom the photo;
         a 2 in magnet face is 600 px at 300 dpi, under that on the short side it prints soft */
      var probe = new Image();
      probe.onload = function () {
        if (photos.indexOf(p) === -1) return;
        p.w = probe.naturalWidth; p.h = probe.naturalHeight;
        p.low = Math.min(p.w, p.h) < MIN_PHOTO_PX;
        renderBuilder();
        if (studio.open && photos[current] === p) { buildSwatches(); updateStudio(); }
      };
      probe.src = p.url;
    });
    renderBuilder();
  }

  /* ---------- the frame studio (dialog) ---------- */
  var studio = $('studio');
  var capIn = $('studio-cap');
  var swTimer, stTimer;
  function say(msg) { var st = $('studio-status'); st.textContent = msg; clearTimeout(stTimer); if (msg) stTimer = setTimeout(function () { st.textContent = ''; }, 4500); }

  function buildSwatches() {
    var fs = $('swatches'), p = photos[current];
    Array.prototype.slice.call(fs.querySelectorAll('.swatch, .sw-group')).forEach(function (n) { n.remove(); });
    $('swatch-legend').textContent = 'Frame for photo ' + (current + 1);
    var lastGroup = null;
    LIST.forEach(function (f) {
      if (f.group !== lastGroup) {
        var h = document.createElement('p'); h.className = 'sw-group'; h.setAttribute('data-group', f.group); h.setAttribute('aria-hidden', 'true'); h.textContent = f.group;
        fs.appendChild(h); lastGroup = f.group;
      }
      var d = document.createElement('div'); d.className = 'swatch'; d.setAttribute('data-group', f.group);
      var r = document.createElement('input'); r.type = 'radio'; r.name = 'sw'; r.id = 'sw-' + f.id; r.value = f.id; r.checked = f.id === p.frame;
      var l = document.createElement('label'); l.htmlFor = r.id;
      var art = document.createElement('span'); art.className = 'sw-art';
      art.appendChild(draw(p, f, f.caption ? (p.caption || f.caption.placeholder) : ''));
      var nm = document.createElement('span'); nm.className = 'sw-name'; nm.textContent = f.name;
      l.append(art, nm);
      if (f.caption) { var ct = document.createElement('span'); ct.className = 'sw-tag'; ct.textContent = 'Caption'; l.appendChild(ct); }
      d.append(r, l); fs.appendChild(d);
      r.addEventListener('change', function () { if (r.checked) setFrame(f.id); });
    });
    applyGroup();
    fitIn(fs);
  }
  function refreshSwatchCaptions() {
    var p = photos[current];
    LIST.forEach(function (f) {
      if (!f.caption) return;
      var art = document.querySelector('#sw-' + f.id + ' + label .sw-art'); if (!art) return;
      art.replaceChild(draw(p, f, p.caption || f.caption.placeholder), art.firstChild);
      fitIn(art);
    });
  }
  function applyGroup() {
    document.querySelectorAll('#swatches .swatch, #swatches .sw-group').forEach(function (n) { n.hidden = !!group && n.getAttribute('data-group') !== group; });
    document.querySelectorAll('.studio .chip[data-group]').forEach(function (c) { c.setAttribute('aria-pressed', String(c.getAttribute('data-group') === group)); });
  }
  function updateStudio() {
    var p = photos[current], f = frameOf(p), n = photos.length;
    $('studio-title').textContent = 'Photo ' + (current + 1) + ' of ' + n;
    $('studio-prev').disabled = current === 0;
    $('studio-next').disabled = current === n - 1;
    var mag = $('studio-mag'); mag.innerHTML = '';
    var big = draw(p, f, p.caption, 'big');
    big.setAttribute('role', 'img'); big.removeAttribute('aria-hidden');
    big.setAttribute('aria-label', 'Preview of photo ' + (current + 1) + ' with the ' + f.name + ' frame' + (capText(f, p.caption, p.capStyle) ? ' and the caption ' + capText(f, p.caption, p.capStyle) : ''));
    mag.appendChild(big); fitIn(mag);
    $('studio-fname').textContent = f.name;
    $('studio-blurb').textContent = f.blurb ? '· ' + f.blurb : '';
    var row = $('studio-cap-row');
    row.hidden = !f.caption;
    if (f.caption) {
      $('studio-cap-label').textContent = f.caption.label || 'Caption';
      capIn.maxLength = f.caption.max;
      capIn.placeholder = 'e.g. ' + f.caption.placeholder;
      if (capIn.value !== p.caption) capIn.value = p.caption;
      $('studio-cap-count').textContent = p.caption.length + '/' + f.caption.max;
      $('cap-all').hidden = !(n > 1 && p.caption.trim());
      drawLettering(p, f);
    }
    var all = $('apply-all');
    all.hidden = n < 2;
    all.textContent = 'Apply this frame to all ' + n + ' photos';
    zoomIn.value = String(cropOf(p).z || 1);
    zoomIn.disabled = !p.w; $('adjust-reset').disabled = !p.w;
  }
  /* lettering for the caption: one chip per style the frame allows, each written in its own font */
  function drawLettering(p, f) {
    var box = $('cap-styles'), st = f.caption.styles || {}, keys = Object.keys(st);
    box.innerHTML = '';
    box.hidden = keys.length < 2;
    var cur = capOf(f, p.capStyle) === f.caption ? f.caption.default : p.capStyle;
    keys.forEach(function (k) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'chip letter';
      b.textContent = st[k].name || k;
      b.style.fontFamily = st[k].family; b.style.fontStyle = st[k].style; b.style.fontWeight = st[k].weight;
      if (st[k].upper) { b.style.textTransform = 'uppercase'; b.style.letterSpacing = '.12em'; b.style.fontSize = '12px'; }
      b.setAttribute('aria-pressed', String(k === cur));
      b.onclick = function () { p.capStyle = k; updateStudio(); refreshThumb(current); clearTimeout(swTimer); swTimer = setTimeout(refreshSwatchCaptions, 150); };
      box.appendChild(b);
    });
  }
  function setFrame(id) {
    var p = photos[current];
    p.frame = id;
    var f = frameOf(p);
    if (f.caption && p.caption.length > f.caption.max) p.caption = p.caption.slice(0, f.caption.max);
    say('');
    updateStudio(); refreshThumb(current);
  }
  function openStudio(i) {
    current = i;
    capIn.value = photos[i].caption;
    buildSwatches(); updateStudio();
    say('');
    if (!studio.open) {
      if (typeof studio.showModal === 'function') studio.showModal(); else studio.setAttribute('open', '');
      document.documentElement.classList.add('studio-open');
    }
    var sel = document.getElementById('sw-' + photos[i].frame);
    if (sel) {
      sel.focus({ preventScroll: true });
      var lab = sel.nextElementSibling; if (lab && lab.scrollIntoView) lab.scrollIntoView({ block: 'nearest' });
    }
  }
  function closeStudio() { if (studio.open) studio.close(); }
  studio.addEventListener('close', function () {
    document.documentElement.classList.remove('studio-open');
    var b = document.querySelector('.thumb-btn[data-i="' + current + '"]'); if (b) b.focus();
  });
  studio.addEventListener('click', function (e) { if (e.target === studio) closeStudio(); });
  $('studio-close').onclick = closeStudio;
  $('studio-done').onclick = closeStudio;
  $('studio-prev').onclick = function () { if (current > 0) openStudio(current - 1); };
  $('studio-next').onclick = function () { if (current < photos.length - 1) openStudio(current + 1); };
  document.querySelectorAll('.studio .chip[data-group]').forEach(function (c) {
    c.addEventListener('click', function () { group = c.getAttribute('data-group'); applyGroup(); });
  });
  capIn.addEventListener('input', function () {
    var p = photos[current]; p.caption = capIn.value;
    updateStudio(); refreshThumb(current);
    clearTimeout(swTimer); swTimer = setTimeout(refreshSwatchCaptions, 250);
  });
  $('apply-all').onclick = function () {
    var p = photos[current], f = frameOf(p);
    photos.forEach(function (q) { q.frame = p.frame; if (f.caption && q.caption.length > f.caption.max) q.caption = q.caption.slice(0, f.caption.max); });
    defaultFrame = p.frame;
    renderBuilder();
    say(f.name + ' is now on all ' + photos.length + ' photos.');
  };
  $('cap-all').onclick = function () {
    var s = photos[current].caption, st = photos[current].capStyle || null;
    photos.forEach(function (q) { q.caption = s; q.capStyle = st; });
    renderBuilder();
    say('Caption added to all ' + photos.length + ' photos. It prints on photos with a caption frame.');
  };

  /* ---------- move & zoom: drag the big preview, pinch or use the slider ---------- */
  var zoomIn = $('studio-zoom');
  var magBox = $('studio-mag');
  var ptrs = {}, gesture = null, settleTimer;
  function cropOf(p) { return p.crop || { x: 0.5, y: 0.5, z: 1 }; }
  /* stores the crop as the centre of what really shows (region() slides it back inside the photo) */
  function setCrop(p, c, live) {
    var w = frameOf(p).window, z = clamp(c.z || 1, 1, ZMAX);
    var r = region(p.w, p.h, w[2], w[3], { x: c.x, y: c.y, z: z });
    var x = (r.left + r.width / 2) / p.w, y = (r.top + r.height / 2) / p.h;
    p.crop = Math.abs(x - 0.5) < 1e-4 && Math.abs(y - 0.5) < 1e-4 && z === 1 ? null : { x: x, y: y, z: z };
    var ph = magBox.querySelector('svg.big svg.ph');
    if (ph) ph.setAttribute('viewBox', viewBoxOf(p, w));
    if (Math.abs(Number(zoomIn.value) - z) > 1e-3) zoomIn.value = String(z);
    if (!live) cropSettled();
  }
  function refreshSwatchArts() {
    if (!studio.open) return;
    var p = photos[current];
    LIST.forEach(function (f) {
      var art = document.querySelector('#sw-' + f.id + ' + label .sw-art'); if (!art) return;
      art.replaceChild(draw(p, f, f.caption ? (p.caption || f.caption.placeholder) : ''), art.firstChild);
    });
    fitIn($('swatches'));
  }
  function cropSettled() { refreshThumb(current); clearTimeout(settleTimer); settleTimer = setTimeout(refreshSwatchArts, 250); }
  function pts() { return Object.keys(ptrs).map(function (k) { return ptrs[k]; }); }
  function centroid() { var a = pts(), x = 0, y = 0; a.forEach(function (q) { x += q.x; y += q.y; }); return { x: x / a.length, y: y / a.length }; }
  function spread() { var a = pts(); return a.length < 2 ? 0 : Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y); }
  function begin() {
    var p = photos[current], w = frameOf(p).window, rect = magBox.getBoundingClientRect();
    var r = region(p.w, p.h, w[2], w[3], p.crop), c = cropOf(p);
    /* photo pixels per screen pixel, at the zoom the gesture starts with */
    gesture = { x: (r.left + r.width / 2) / p.w, y: (r.top + r.height / 2) / p.h, z: c.z || 1,
                k: (600 / rect.width) * (r.width / w[2]), at: centroid(), d: spread() };
  }
  magBox.addEventListener('pointerdown', function (e) {
    var p = photos[current]; if (!p || !p.w || !e.target.closest('svg.big')) return;
    e.preventDefault();
    try { magBox.setPointerCapture(e.pointerId); } catch (x) { /* ignore */ }
    ptrs[e.pointerId] = { x: e.clientX, y: e.clientY };
    begin();
    var big = magBox.querySelector('svg.big'); if (big) big.classList.add('dragging');
  });
  magBox.addEventListener('pointermove', function (e) {
    if (!ptrs[e.pointerId] || !gesture) return;
    ptrs[e.pointerId] = { x: e.clientX, y: e.clientY };
    var p = photos[current], g = gesture, now = centroid();
    var z = g.d > 0 && spread() > 0 ? g.z * spread() / g.d : g.z;
    z = clamp(z, 1, ZMAX);
    var k = g.k * g.z / z;
    setCrop(p, { x: g.x - (now.x - g.at.x) * k / p.w, y: g.y - (now.y - g.at.y) * k / p.h, z: z }, true);
  });
  function lift(e) {
    if (!ptrs[e.pointerId]) return;
    delete ptrs[e.pointerId];
    if (pts().length) { begin(); return; }
    gesture = null;
    var big = magBox.querySelector('svg.big'); if (big) big.classList.remove('dragging');
    cropSettled();
  }
  magBox.addEventListener('pointerup', lift);
  magBox.addEventListener('pointercancel', lift);
  magBox.addEventListener('wheel', function (e) {
    var p = photos[current]; if (!p || !p.w) return;
    e.preventDefault();
    var c = cropOf(p);
    setCrop(p, { x: c.x, y: c.y, z: (c.z || 1) * Math.exp(-e.deltaY * 0.002) }, true);
    clearTimeout(settleTimer); settleTimer = setTimeout(cropSettled, 200);
  }, { passive: false });
  zoomIn.addEventListener('input', function () { var p = photos[current], c = cropOf(p); setCrop(p, { x: c.x, y: c.y, z: Number(zoomIn.value) }, true); });
  zoomIn.addEventListener('change', cropSettled);
  $('adjust-reset').onclick = function () { var p = photos[current]; p.crop = null; updateStudio(); cropSettled(); say('Photo centred again.'); };

  /* ---------- wiring ---------- */
  $('photos').addEventListener('change', function (e) { addFiles(e.target.files); e.target.value = ''; });
  var drop = $('drop');
  drop.setAttribute('tabindex', '0'); drop.setAttribute('role', 'button'); $('photos').setAttribute('tabindex', '-1');
  drop.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); $('photos').click(); } });
  ['dragenter', 'dragover'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('is-over'); }); });
  ['dragleave', 'drop'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove('is-over'); }); });
  drop.addEventListener('drop', function (e) { if (e.dataTransfer && e.dataTransfer.files) addFiles(e.dataTransfer.files); });
  document.querySelectorAll('input[name="pack"]').forEach(function (r) { r.addEventListener('change', renderBuilder); });
  $('rights').addEventListener('change', renderBuilder);

  $('builder').addEventListener('submit', function (e) {
    e.preventDefault();
    var size = packSize();
    var lines = photos.map(function (p, i) {
      var f = frameOf(p);
      return { n: i + 1, file: p.name, frame: f.id, frameName: f.name, caption: f.caption ? p.caption.trim().slice(0, f.caption.max) : '',
               crop: p.crop || null, w: p.w || 0, h: p.h || 0, capStyle: f.caption && capOf(f, p.capStyle) !== f.caption ? p.capStyle : null,
               blob: p.blob, url: p.url };  /* blob/url: uploaded at checkout (assets/checkout.js) */
    });
    var names = [];
    lines.forEach(function (l) { if (names.indexOf(l.frameName) < 0) names.push(l.frameName); });
    var notes = $('notes').value.trim();
    var detail = size + ' magnets · ' + photos.length + ' photo' + (photos.length > 1 ? 's' : '') + ' · ' + (names.length === 1 ? names[0] : names.length + ' frames');
    var orderNotes = lines.map(function (l) {
      return 'Photo ' + l.n + ' (' + l.file + '): ' + l.frameName + ' [' + l.frame + ']' + (l.caption ? ', caption "' + l.caption + '"' : '') + (l.crop ? ', moved/zoomed' : '');
    }).join('\n');
    if (photos.length < size) orderNotes += '\nPack of ' + size + ': repeat photos in order to fill it.';
    if (notes) orderNotes += '\nNotes: ' + notes;
    LHH.addCustom({ id: 'custom-' + Date.now(), count: size, name: 'Custom photo magnets', detail: detail, price: packPrice(),
                    photos: lines, notes: notes, orderNotes: orderNotes });
    photos = []; $('notes').value = ''; $('rights').checked = false;
    renderBuilder();
  });

  renderBuilder();
})();
