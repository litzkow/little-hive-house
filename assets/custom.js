/* Little Hive House: the custom photo magnet builder. Needs site.js first. */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  /* custom photo builder */
  var photos = [];
  var MIN_PHOTO_PX = 600;
  function packSize() { return Number(document.querySelector('input[name="pack"]:checked').value); }
  function packPrice() { return Number(document.querySelector('input[name="pack"]:checked').getAttribute('data-price')); }

  function renderBuilder() {
    var size = packSize();
    var grid = $('thumbs'); grid.innerHTML = '';
    photos.forEach(function (p, i) {
      var d = document.createElement('div'); d.className = 'thumb';
      var img = document.createElement('img'); img.src = p.url; img.alt = 'Photo ' + (i + 1);
      var x = document.createElement('button'); x.type = 'button'; x.textContent = '×'; x.setAttribute('aria-label', 'Remove photo ' + (i + 1));
      x.onclick = function () { URL.revokeObjectURL(p.url); photos.splice(i, 1); renderBuilder(); };
      d.append(img, x);
      if (p.low) {
        d.classList.add('low');
        var t = document.createElement('span'); t.className = 'lowtag'; t.textContent = 'Low quality'; d.appendChild(t);
        img.alt += ' (low resolution, may print blurry)';
      }
      grid.appendChild(d);
    });
    var lowCount = photos.filter(function (p) { return p.low; }).length;
    var rn = $('res-note');
    if (lowCount) {
      rn.textContent = (lowCount === 1 ? '1 photo is' : lowCount + ' photos are') + ' too small and may print blurry. For sharp magnets, use the original photo from your camera roll, not a screenshot or a photo saved from a chat app.';
      rn.hidden = false;
    } else { rn.hidden = true; }
    for (var k = photos.length; k < size; k++) {
      var e = document.createElement('div'); e.className = 'thumb empty'; e.textContent = k + 1; e.setAttribute('aria-hidden', 'true'); grid.appendChild(e);
    }
    var c = $('counter');
    if (photos.length > size) { c.textContent = photos.length + ' photos added. This pack holds ' + size + ', so remove ' + (photos.length - size) + ' or pick a bigger pack.'; c.classList.add('warn'); }
    else { c.textContent = photos.length + ' of ' + size + ' photos added' + (photos.length && photos.length < size ? '. We will repeat your favorites to fill the pack, or tell us in the notes.' : ''); c.classList.remove('warn'); }
    $('builder-total').textContent = LHH.money(packPrice());
    $('add-custom').disabled = !(photos.length >= 1 && photos.length <= size && $('rights').checked);
  }

  function addFiles(files) {
    Array.prototype.forEach.call(files, function (f) {
      if (f.type.indexOf('image/') !== 0) return;
      var p = { name: f.name, url: URL.createObjectURL(f), low: false };
      photos.push(p);
      /* a 2 in magnet wraps about 2.5 in of print; under 600 px on the short side it prints soft */
      var probe = new Image();
      probe.onload = function () {
        if (Math.min(probe.naturalWidth, probe.naturalHeight) < MIN_PHOTO_PX && photos.indexOf(p) !== -1) { p.low = true; renderBuilder(); }
      };
      probe.src = p.url;
    });
    renderBuilder();
  }
  $('photos').addEventListener('change', function (e) { addFiles(e.target.files); e.target.value = ''; });
  var drop = $('drop');
  ['dragenter', 'dragover'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add('is-over'); }); });
  ['dragleave', 'drop'].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove('is-over'); }); });
  drop.addEventListener('drop', function (e) { if (e.dataTransfer && e.dataTransfer.files) addFiles(e.dataTransfer.files); });
  document.querySelectorAll('input[name="pack"]').forEach(function (r) { r.addEventListener('change', renderBuilder); });
  $('rights').addEventListener('change', renderBuilder);

  $('builder').addEventListener('submit', function (e) {
    e.preventDefault();
    var size = packSize();
    LHH.addCustom({ id: 'custom-' + Date.now(), count: size, name: 'Custom photo magnets', detail: size + ' magnets · ' + photos.length + ' photo' + (photos.length > 1 ? 's' : ''), price: packPrice() });
    photos = []; $('notes').value = ''; $('rights').checked = false;
    renderBuilder();
  });

  renderBuilder();
})();
