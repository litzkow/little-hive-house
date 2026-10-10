/* Little Hive House: favorites.html. Shows the designs saved with the hearts (store.js keeps the list in
   localStorage and syncs it to the account when signed in). window.LHH_DESIGNS = {id: [title, collection name]}. */
(function () {
  var S = window.LHHStore, L = window.LHH;
  var $ = function (id) { return document.getElementById(id); };
  var D = window.LHH_DESIGNS || {};
  var grid = $('fav-grid'), empty = $('fav-empty'), head = $('fav-count'), all = $('fav-all'), sync = $('fav-sync');
  if (!grid) return;

  function card(id) {
    var d = D[id]; if (!d) return null;
    var col = id.split('/')[0];
    var li = document.createElement('li');
    li.className = 'product'; li.setAttribute('data-collection', col);
    var art = document.createElement('button');
    art.type = 'button'; art.className = 'product-art'; art.setAttribute('data-view', ''); art.setAttribute('aria-label', 'See ' + d[0] + ' larger');
    var img = document.createElement('img');
    img.className = 'mag'; img.src = S.base + 'assets/art/' + id + '.webp'; img.width = 600; img.height = 600; img.alt = ''; img.decoding = 'async'; img.loading = 'lazy';
    art.appendChild(img);
    var info = document.createElement('div'); info.className = 'product-info';
    var h3 = document.createElement('h3'); h3.textContent = d[0];
    var p = document.createElement('p'); p.className = 'col';
    var a = document.createElement('a'); a.href = S.base + 'collections/' + col + '.html'; a.textContent = d[1]; p.appendChild(a);
    var pr = document.createElement('p'); pr.className = 'price'; pr.textContent = '$5';
    info.append(h3, p, pr);
    var add = document.createElement('button');
    add.type = 'button'; add.className = 'btn btn-small'; add.textContent = 'Add to cart';
    add.setAttribute('data-add', id); add.setAttribute('data-name', d[0]); add.setAttribute('data-collection', d[1]); add.setAttribute('data-href', a.href);
    li.append(art, info, add);
    return li;
  }
  function render(list) {
    var ids = list.filter(function (id) { return D[id]; });
    grid.replaceChildren();
    ids.forEach(function (id) { var c = card(id); if (c) grid.appendChild(c); });
    S.addHearts(grid);
    empty.hidden = ids.length > 0;
    grid.closest('.fridge').hidden = ids.length === 0;
    all.hidden = ids.length < 2;
    all.textContent = 'Add all ' + ids.length + ' to cart';
    head.textContent = ids.length ? ids.length + (ids.length === 1 ? ' saved design' : ' saved designs') : '';
  }
  all.addEventListener('click', function () {
    var ids = S.favorites.list().filter(function (id) { return D[id]; });
    ids.forEach(function (id) { L.addLine({ id: id, kind: 'design', name: D[id][0] + ' magnet', detail: '2 × 2 in · ' + D[id][1], price: 5, qty: 1 }, true); });
    L.openCart();
  });
  render(S.favorites.list());
  /* keep un-hearted cards in place until the next visit, so a mis-tap is easy to undo */
  S.favorites.onChange(function (list) {
    var shown = Array.prototype.map.call(grid.querySelectorAll('[data-fav]'), function (b) { return b.getAttribute('data-fav'); });
    if (list.some(function (id) { return shown.indexOf(id) < 0 && D[id]; })) render(list);
  });
  if (S.configured) {
    S.onUser(function (u) { sync.hidden = false; sync.querySelector('[data-signed]').hidden = !S.isMember(u); sync.querySelector('[data-guest]').hidden = S.isMember(u); });
  }
})();
