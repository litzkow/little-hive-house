/* Little Hive House admin: Materials (functions/supplies.js adminSupplies). What the shop has to make and ship orders,
   estimated from the orders (nobody counts), with "Comprei" / "Contei" / "Acabou", and the purchases: the money put
   into the shop. The screen picks its own language (T(en, pt)) and is marked translate="no". */
(function () {
  'use strict';
  var A = window.LHHAdmin, S = A.S, h = A.h, V = A.VIEWS, ACT = A.ACT;
  var esc = h.esc, money = h.money, icon = h.icon;
  function T(en, pt) { return h.LANG() === 'pt' ? pt : en; }
  var st = { data: null, err: null, loading: false, busy: false };

  function n2(v) { v = Math.round((Number(v) || 0) * 100) / 100; return v.toLocaleString(h.LANG() === 'pt' ? 'pt-BR' : 'en-US'); }
  function load(action, args) {
    st.busy = true;
    return h.call('adminSupplies', Object.assign({ action: action || 'list' }, args || {})).then(function (d) { st.data = d; st.err = null; })
      .catch(function (e) { st.err = h.friendlyError(e); if (action && action !== 'list') h.toast(st.err, true); })
      .then(function () { st.busy = false; st.loading = false; if (A.parseHash().view === 'supplies') { var y = scrollY; h.route(); scrollTo(0, y); } });
  }
  var STATUS = { ok: ['Plenty', 'Tem bastante'], low: ['Running low', 'Acabando'], out: ['Buy now', 'Comprar'], unset: ['How many?', 'Quanto tem?'] };
  var PER = { magnet: ['per magnet', 'por ímã'], sheet: ['per printed sheet', 'por folha impressa'], order: ['per order', 'por pedido'], small_order: ['per small order', 'por pedido pequeno'],
    big_order: ['per big order', 'por pedido grande'], shipment: ['per shipment', 'por envio'], manual: ['', ''] };

  function rule(s) {
    if (s.per === 'manual') return T('Not tied to orders: tap Used when you use some', 'Não depende dos pedidos: toque em Usei quando usar');
    return T('Uses ' + n2(s.rate) + ' ' + s.unit + ' ' + PER[s.per][0], 'Usa ' + n2(s.rate) + ' ' + s.unit + ' ' + PER[s.per][1]);
  }
  function card(s) {
    var label = STATUS[s.status] || STATUS.ok;
    var prev = s.after && ((st.data && st.data.supplies) || []).find(function (x) { return x.id === s.after; });
    var est = s.status === 'unset' ? T('Tell us how many you have, or tap Bought.', 'Diga quanto vocês têm, ou toque em Comprei.')
      : s.waiting && prev ? '≈ <b>' + n2(s.left) + '</b> ' + esc(s.unit) + ' · ' + esc(T('starts when “' + prev.name + '” run out', 'começa quando acabar “' + prev.name + '”'))
      : s.per === 'big_order' && !st.data.cfg.bigOrder ? '≈ <b>' + n2(s.left) + '</b> ' + esc(s.unit) + ' · ' + esc(T('set the size of a big order below', 'falta dizer quando um pedido é grande (embaixo)'))
      : '≈ <b>' + n2(s.left) + '</b> ' + esc(s.unit) + (s.ordersLeft != null ? ' · ' + T('about ' + s.ordersLeft + ' more orders', 'dá para uns ' + s.ordersLeft + ' pedidos') : '');
    var b = st.busy ? ' disabled' : '';
    return '<section class="card sp-card sp-' + s.status + '">' +
      '<div class="sp-top"><b>' + esc(s.name) + '</b><span class="sp-pill">' + esc(T(label[0], label[1])) + '</span></div>' +
      (s.status === 'unset' ? '' : '<div class="sp-bar"><i style="width:' + Math.max(2, s.pct) + '%"></i></div>') +
      '<p class="small">' + est + '</p><p class="tiny muted">' + esc(rule(s)) + (s.lastBought ? ' · ' + T('bought ', 'comprado em ') + esc(h.fmtDate(s.lastBought)) : '') + '</p>' +
      '<div class="row sp-acts">' +
      '<button class="btn btn-honey btn-sm" data-act="spBought" data-id="' + esc(s.id) + '"' + b + '>' + T('Bought', 'Comprei') + '</button>' +
      '<button class="btn btn-ghost btn-sm" data-act="spCounted" data-id="' + esc(s.id) + '"' + b + '>' + T('Counted', 'Contei') + '</button>' +
      (s.status !== 'unset' ? '<button class="btn btn-ghost btn-sm" data-act="spUsed" data-id="' + esc(s.id) + '"' + b + '>' + T('Used', 'Usei') + '</button>' +
        '<button class="btn btn-ghost btn-sm" data-act="spOut" data-id="' + esc(s.id) + '"' + b + '>' + T('Ran out', 'Acabou') + '</button>' : '') +
      '<button class="btn btn-ghost btn-sm" data-act="spEdit" data-id="' + esc(s.id) + '"' + b + ' aria-label="' + T('Edit', 'Editar') + '">' + T('Edit', 'Editar') + '</button>' +
      '</div></section>';
  }

  V.supplies = function () {
    if (!st.data && !st.loading && !st.err) { st.loading = true; load('list'); }
    var d = st.data;
    var head = '<div class="page-head"><div><p class="eyebrow">' + T('Shop', 'Loja') + '</p><h1>' + T('Materials', 'Materiais') + '</h1>' +
      '<p class="sub">' + T('Every order uses its materials up by itself. Tap Bought when you buy more; if something runs out sooner, tap Ran out and the count fixes itself.',
        'Cada pedido desconta sozinho o que usou. Quando comprarem, toquem em Comprei; se algo acabar antes, toquem em Acabou e a conta se corrige.') + '</p></div>' +
      '<div class="actions"><button class="btn btn-ghost btn-sm" data-act="spNew">' + T('+ New material', '+ Novo material') + '</button></div></div>';
    if (!d) return { title: T('Materials', 'Materiais'), html: '<div translate="no">' + head + (st.err ? '<p class="err">' + esc(st.err) + '</p>' : '<div class="loading"><span>' + T('Loading…', 'Carregando…') + '</span></div>') + '</div>' };
    var buy = d.supplies.filter(function (s) { return s.status === 'out'; }).length, low = d.supplies.filter(function (s) { return s.status === 'low'; }).length;
    var tiles = '<div class="tiles">' +
      h.tile(T('Put into the shop', 'Investido na loja'), money(d.invested.total), T(money(d.invested.before) + ' before + ' + money(d.invested.logged) + ' logged here', money(d.invested.before) + ' antes + ' + money(d.invested.logged) + ' registrados aqui'), true) +
      h.tile(T('Buy now', 'Comprar agora'), String(buy), buy ? T('Ran out', 'Acabaram') : T('Nothing ran out', 'Nada acabou')) +
      h.tile(T('Running low', 'Acabando'), String(low), T('Push alert when it happens', 'Aviso no celular quando acontece')) +
      '</div>';
    var groups = {};
    d.supplies.forEach(function (s) { (groups[s.group || 'Outros'] = groups[s.group || 'Outros'] || []).push(s); });
    var order = ['Ímãs', 'Embalagem', 'Envio'].concat(Object.keys(groups).filter(function (g) { return ['Ímãs', 'Embalagem', 'Envio'].indexOf(g) < 0; }));
    var lists = order.filter(function (g) { return groups[g]; }).map(function (g) {
      return '<h2 class="sp-h2">' + esc(g) + '</h2><div class="sp-grid">' + groups[g].map(card).join('') + '</div>';
    }).join('');
    var gift = '<p class="small muted sp-gift">' + T('Logo magnet gift in each order: ', 'Ímã de logo de brinde em cada pedido: ') + '<b>' + d.cfg.giftMagnets + '</b> · ' +
      T('Big order (goes in a box): ', 'Pedido grande (vai em caixinha): ') + '<b>' + (d.cfg.bigOrder ? T(d.cfg.bigOrder + '+ magnets', 'a partir de ' + d.cfg.bigOrder + ' ímãs') : T('not set yet', 'ainda não definido')) + '</b> · ' +
      '<button class="linkish" data-act="spGift">' + T('change', 'mudar') + '</button></p>';
    var purchases = '<section class="card gap-top"><div class="card-head"><div><h2>' + T('Purchases', 'Compras') + '</h2><p class="sub">' + T('Machines, supplies, everything you buy for the shop', 'Máquinas, materiais, tudo o que comprarem para a loja') + '</p></div>' +
      '<button class="btn btn-ghost btn-sm" data-act="spPurchase">' + T('+ Log a purchase', '+ Registrar compra') + '</button></div>' +
      (d.purchases.length ? '<ul class="sp-buys">' + d.purchases.map(function (p) {
        return '<li><span><b>' + esc(p.item || T('Purchase', 'Compra')) + '</b><small>' + esc(h.fmtDate(/^\d{4}-\d{2}-\d{2}$/.test(p.date || '') ? p.date + 'T12:00:00' : p.date)) + (p.store ? ' · ' + esc(p.store) : '') + '</small></span><span class="sp-cost">' + money(p.cost) +
          '<button class="icon-btn" data-act="spDelBuy" data-id="' + esc(p.id) + '" aria-label="' + T('Remove', 'Apagar') + '">' + icon('trash') + '</button></span></li>';
      }).join('') + '</ul>' : '<p class="small muted">' + T('Nothing logged yet.', 'Nada registrado ainda.') + '</p>') +
      '<p class="small"><b>' + T('Total put into the shop: ', 'Total investido na loja: ') + money(d.invested.total) + '</b> <span class="muted">(' + T(money(d.invested.before) + ' from before, in Settings', money(d.invested.before) + ' de antes, nas Configurações') + ')</span></p></section>';
    return { title: T('Materials', 'Materiais'), html: '<div translate="no">' + head + tiles + gift + lists + purchases + '</div>' };
  };

  /* a small form in a dialog: resolves with the form's values, or null */
  function ask(title, inner, okText) {
    return new Promise(function (resolve) {
      var d = document.createElement('dialog'); d.className = 'modal'; d.setAttribute('translate', 'no');
      d.innerHTML = '<form method="dialog" class="in"><h2>' + esc(title) + '</h2>' + inner + '<div class="row end"><button class="btn btn-ghost" value="cancel">' + T('Cancel', 'Cancelar') + '</button><button class="btn btn-honey" value="ok">' + esc(okText || 'OK') + '</button></div></form>';
      document.body.appendChild(d);
      d.addEventListener('close', function () {
        var out = null;
        if (d.returnValue === 'ok') { out = {}; Array.prototype.forEach.call(d.querySelectorAll('[name]'), function (el) { out[el.name] = el.value; }); }
        d.remove(); resolve(out);
      });
      if (d.showModal) d.showModal(); else d.setAttribute('open', '');
      var first = d.querySelector('input'); if (first) setTimeout(function () { first.focus(); }, 50);
    });
  }
  function field(name, label, value, type, extra) {
    return '<label class="field"><span>' + esc(label) + '</span><input class="input" name="' + name + '" value="' + esc(value == null ? '' : value) + '"' + (type ? ' type="' + type + '"' : '') + (type === 'number' ? ' inputmode="decimal" step="any" min="0"' : '') + (extra || '') + '></label>';
  }
  function sup(id) { return ((st.data && st.data.supplies) || []).find(function (s) { return s.id === id; }); }
  var today = function () { return new Date().toISOString().slice(0, 10); };

  ACT.spBought = function (el) {
    var s = sup(el.getAttribute('data-id')); if (!s) return;
    ask(T('Bought ', 'Comprei ') + s.name, field('qty', T('How many ', 'Quantos ') + s.unit + T(' did you buy?', ' vocês compraram?'), '', 'number') +
      field('cost', T('Price paid (optional: adds to the money put into the shop)', 'Valor pago (opcional: soma no investido na loja)'), '', 'number') +
      field('store', T('Store', 'Loja'), 'Amazon') + field('date', T('Date', 'Data'), today(), 'date'), T('Save', 'Salvar')).then(function (v) {
      if (v) load('bought', { id: s.id, qty: v.qty, cost: v.cost, store: v.store, date: v.date, item: s.name });
    });
  };
  ACT.spCounted = function (el) {
    var s = sup(el.getAttribute('data-id')); if (!s) return;
    ask(s.name, field('qty', T('How many ', 'Quantos ') + s.unit + T(' do you have now?', ' vocês têm agora?'), s.status === 'unset' ? '' : Math.round(s.left), 'number'), T('Save', 'Salvar'))
      .then(function (v) { if (v && v.qty !== '') load('counted', { id: s.id, qty: v.qty }); });
  };
  ACT.spUsed = function (el) {
    var s = sup(el.getAttribute('data-id')); if (!s) return;
    ask(s.name, '<p class="small">' + T('Used outside the orders (magnets for yourselves, tests).', 'Usado fora dos pedidos (ímãs para vocês, testes).') + '</p>' + field('qty', T('How many ', 'Quantos ') + s.unit + '?', '', 'number'), T('Save', 'Salvar'))
      .then(function (v) { if (v && v.qty) load('used', { id: s.id, qty: v.qty }); });
  };
  ACT.spOut = function (el) {
    var s = sup(el.getAttribute('data-id')); if (!s) return;
    h.dialog({ title: s.name, html: '<p>' + T('Mark it as run out? The count goes to 0 until you tap Bought.', 'Marcar que acabou? A conta vai para 0 até vocês tocarem em Comprei.') + '</p>', ok: T('It ran out', 'Acabou') })
      .then(function (ok) { if (ok) load('out', { id: s.id }); });
  };
  function editForm(s) {
    s = s || { per: 'order', rate: 1, unit: 'unidades', group: 'Embalagem', low: 5 };
    var opts = [['magnet', T('Each magnet made', 'Cada ímã feito')], ['sheet', T('Each printed sheet (9 magnets)', 'Cada folha impressa (9 ímãs)')], ['order', T('Each order', 'Cada pedido')],
      ['small_order', T('Each small order', 'Cada pedido pequeno')], ['big_order', T('Each big order', 'Cada pedido grande')], ['shipment', T('Each shipment', 'Cada envio')], ['manual', T('Not tied to orders', 'Não depende dos pedidos')]];
    return field('name', T('Name', 'Nome'), s.name) + field('unit', T('Counted in (boxes, sheets, units…)', 'Contado em (caixas, folhas, unidades…)'), s.unit) +
      '<label class="field"><span>' + T('Used by', 'Gasta com') + '</span><select class="input" name="per">' + opts.map(function (o) { return '<option value="' + o[0] + '"' + (s.per === o[0] ? ' selected' : '') + '>' + esc(o[1]) + '</option>'; }).join('') + '</select></label>' +
      field('rate', T('How much each time', 'Quanto gasta cada vez'), s.rate, 'number') + field('low', T('Warn me when there are this many left', 'Avisar quando sobrar'), s.low, 'number') +
      field('group', T('Group', 'Grupo'), s.group) + (s.id ? '' : field('qty', T('How many you have now', 'Quantos têm agora'), '', 'number'));
  }
  ACT.spEdit = function (el) {
    var s = sup(el.getAttribute('data-id')); if (!s) return;
    ask(T('Edit ', 'Editar ') + s.name, editForm(s) + '<p class="small"><button type="button" class="linkish danger" data-act="spRemove" data-id="' + esc(s.id) + '">' + T('Remove this material', 'Tirar este material da lista') + '</button></p>', T('Save', 'Salvar'))
      .then(function (v) { if (v) load('save', { id: s.id, supply: v }); });
  };
  ACT.spRemove = function (el) {
    var id = el.getAttribute('data-id'), d = el.closest('dialog'); if (d) d.close('cancel');
    h.dialog({ title: T('Remove from the list?', 'Tirar da lista?'), html: '', ok: T('Remove', 'Tirar'), danger: true }).then(function (ok) { if (ok) load('remove', { id: id }); });
  };
  ACT.spNew = function () { ask(T('New material', 'Novo material'), editForm(null), T('Add', 'Adicionar')).then(function (v) { if (v && v.name) load('save', { supply: v }); }); };
  ACT.spPurchase = function () {
    ask(T('Log a purchase', 'Registrar compra'), field('item', T('What', 'O que foi'), '') + field('cost', T('Price paid', 'Valor pago'), '', 'number') + field('store', T('Store', 'Loja'), 'Amazon') + field('date', T('Date', 'Data'), today(), 'date'), T('Save', 'Salvar'))
      .then(function (v) { if (v && v.item && v.cost) load('purchase', v); });
  };
  ACT.spDelBuy = function (el) {
    var id = el.getAttribute('data-id');
    h.dialog({ title: T('Remove this purchase?', 'Apagar esta compra?'), html: '', ok: T('Remove', 'Apagar'), danger: true }).then(function (ok) { if (ok) load('removePurchase', { id: id }); });
  };
  ACT.spGift = function () {
    ask(T('Orders', 'Pedidos'), field('giftMagnets', T('Logo magnets given in each order', 'Ímãs de logo de brinde em cada pedido'), st.data.cfg.giftMagnets, 'number') +
      field('bigOrder', T('A big order (in a box) has at least this many magnets (0 = not set)', 'Pedido grande (em caixinha) a partir de quantos ímãs (0 = ainda não)'), st.data.cfg.bigOrder || '', 'number'), T('Save', 'Salvar'))
      .then(function (v) { if (v) load('config', { giftMagnets: v.giftMagnets, bigOrder: v.bigOrder || 0 }); });
  };
})();
