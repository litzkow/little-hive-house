/* Little Hive House admin: Returns (functions/returns.js). Problems reported with photos wait here for one tap:
   refund, free reprint, or decline. Change-of-mind returns refund by themselves when USPS says the parcel arrived;
   "Refund now" is there if tracking ever gets stuck. The screen picks its own language (T(en, pt)), translate="no". */
(function () {
  'use strict';
  var A = window.LHHAdmin, S = A.S, h = A.h, V = A.VIEWS, ACT = A.ACT;
  var esc = h.esc, money = h.money, icon = h.icon;
  function T(en, pt) { return h.LANG() === 'pt' ? pt : en; }
  var st = { tab: 'todo', photos: {}, busy: {} };

  var STATUS = {
    requested: ['Waiting for you', 'Esperando vocês'], label_sent: ['Label sent', 'Etiqueta enviada'], in_transit: ['Coming back', 'Voltando pelo correio'],
    refunded: ['Refunded', 'Reembolsado'], reprinting: ['Reprinting', 'Reimprimindo'], received: ['Arrived', 'Chegou'], declined: ['Declined', 'Recusado'], expired: ['Label not used', 'Etiqueta não usada']
  };
  var TABS = [['todo', 'To decide', 'Para decidir', ['requested']], ['open', 'In progress', 'Em andamento', ['label_sent', 'in_transit', 'reprinting']],
    ['done', 'Done', 'Concluídas', ['refunded', 'received', 'declined', 'expired']]];
  function list() { return (S.returns || []).slice().sort(function (a, b) { return String(b.createdAt).localeCompare(String(a.createdAt)); }); }

  function need() {
    if (S.returns || st.loading) return !!S.returns;
    st.loading = true;
    h.loadCol('returns').then(function () { st.loading = false; if (A.parseHash().view === 'returns') h.route(); })
      .catch(function (e) { st.loading = false; S.returns = []; st.err = h.friendlyError(e); h.route(); });
    return false;
  }

  function card(r) {
    var s = STATUS[r.status] || [r.status, r.status];
    var what = (r.lines || []).map(function (l) { return esc(l.title) + (l.qty > 1 ? ' × ' + l.qty : ''); }).join(', ');
    var mind = r.kind === 'changed_mind', est = r.estimate || {};
    var head = '<div class="rt-top"><a class="ord" href="#order/' + encodeURIComponent(r.orderId) + '">' + esc(r.number) + '</a> · <b>' + esc(r.name || r.email) + '</b>' +
      '<span class="pill ' + (r.status === 'requested' ? 'warn' : '') + '">' + esc(T(s[0], s[1])) + '</span></div>';
    var kind = mind ? T('Changed their mind', 'Mudou de ideia') : (T('Problem: ', 'Problema: ') + esc(T(r.reasonLabel || 'Other', ({ 'Arrived damaged': 'Chegou quebrado', 'Printing problem': 'Problema na impressão', 'Wrong item': 'Ímã errado', 'Something missing': 'Faltou algo', 'Something else': 'Outro' })[r.reasonLabel] || r.reasonLabel || 'Outro')));
    var lines = '<p class="rt-what">' + kind + ' · ' + what + '</p>';
    var money1 = mind
      ? '<p class="small muted">' + T('Refund when it arrives: ', 'Reembolso quando chegar: ') + '<b>' + money(est.refund) + '</b> (' + money(est.value) + T(' magnets − ', ' ímãs − ') + money(est.labelCost) + T(' return label)', ' etiqueta de volta)') + '</p>'
      : '<p class="small muted">' + (r.wants === 'reprint' ? T('Wants a free reprint', 'Quer reimpressão grátis') : T('Wants a refund of ', 'Quer reembolso de ') + '<b>' + money(r.value) + '</b>') + '</p>';
    var note = r.note ? '<blockquote class="rt-note">“' + esc(r.note) + '”</blockquote>' : '';
    var ph = '';
    if (!mind && (r.photos || []).length) {
      var got = st.photos[r.id];
      ph = '<div class="rt-photos">' + (got ? got.map(function (u, i) { return '<a href="' + esc(u) + '" target="_blank" rel="noopener"><img src="' + esc(u) + '" alt="' + T('Photo ', 'Foto ') + (i + 1) + '" loading="lazy"></a>'; }).join('')
        : '<button class="btn btn-ghost btn-sm" data-act="rtPhotos" data-id="' + esc(r.id) + '">' + icon('image') + T('See the ' + r.photos.length + ' photo(s)', 'Ver ' + (r.photos.length === 1 ? 'a foto' : 'as ' + r.photos.length + ' fotos')) + '</button>') + '</div>';
    }
    var track = r.label && r.label.tracking ? '<p class="small"><a href="https://tools.usps.com/go/TrackConfirmAction?tLabels=' + encodeURIComponent(r.label.tracking) + '" target="_blank" rel="noopener">' + T('Track the return', 'Rastrear a devolução') + ' ' + icon('external') + '</a></p>' : '';
    var done = r.refund ? '<p class="small ok">' + T('Refunded ', 'Reembolsado ') + money(r.refund.amount) + ' · ' + esc(h.fmtDate(r.refund.at)) + '</p>' : r.reprint ? '<p class="small ok">' + T('Reprint ', 'Reimpressão ') + '<a href="#order/' + encodeURIComponent(r.reprint.orderId) + '">' + esc(r.reprint.number) + '</a></p>' : r.declineNote ? '<p class="small muted">' + T('Note sent: ', 'Recado enviado: ') + esc(r.declineNote) + '</p>' : '';
    var busy = st.busy[r.id] ? ' disabled' : '';
    var acts = '';
    if (r.status === 'requested') acts = '<div class="row">' +
      '<button class="btn btn-honey btn-sm" data-act="rtDo" data-do="' + (r.wants === 'reprint' ? 'reprint' : 'refund') + '" data-id="' + esc(r.id) + '"' + busy + '>' + (r.wants === 'reprint' ? T('Reprint for free', 'Reimprimir grátis') : T('Refund ', 'Reembolsar ') + money(r.value)) + '</button>' +
      '<button class="btn btn-ghost btn-sm" data-act="rtDo" data-do="' + (r.wants === 'reprint' ? 'refund' : 'reprint') + '" data-id="' + esc(r.id) + '"' + busy + '>' + (r.wants === 'reprint' ? T('Refund ', 'Reembolsar ') + money(r.value) + T(' instead', ' em vez disso') : T('Reprint instead', 'Reimprimir em vez disso')) + '</button>' +
      '<button class="btn btn-ghost btn-sm" data-act="rtDo" data-do="decline" data-id="' + esc(r.id) + '"' + busy + '>' + T('Decline', 'Recusar') + '</button></div>';
    else if (mind && (r.status === 'label_sent' || r.status === 'in_transit')) acts = '<div class="row"><button class="btn btn-ghost btn-sm" data-act="rtDo" data-do="refund" data-id="' + esc(r.id) + '"' + busy + '>' +
      T('It arrived: refund ', 'Chegou: reembolsar ') + money(est.refund) + T(' now', ' agora') + '</button></div>';
    return '<section class="card rt-card">' + head + lines + money1 + note + ph + track + done + acts +
      '<p class="tiny faint">' + esc(h.fmtDT(r.createdAt)) + '</p></section>';
  }

  V.returns = function (r) {
    if (r.q.get('tab')) st.tab = r.q.get('tab');
    var ready = need();
    var all = list();
    var tabs = '<nav class="tabs" aria-label="' + T('Returns', 'Devoluções') + '">' + TABS.map(function (t) {
      var n = all.filter(function (x) { return t[3].indexOf(x.status) >= 0; }).length;
      return '<a href="#returns?tab=' + t[0] + '"' + (st.tab === t[0] ? ' aria-current="page"' : '') + '>' + esc(T(t[1], t[2])) + (n ? ' <span class="count">' + n + '</span>' : '') + '</a>';
    }).join('') + '</nav>';
    var tab = TABS.find(function (t) { return t[0] === st.tab; }) || TABS[0];
    var shown = all.filter(function (x) { return tab[3].indexOf(x.status) >= 0; });
    var body = !ready ? '<div class="loading"><span>' + T('Loading…', 'Carregando…') + '</span></div>'
      : st.err ? '<p class="err">' + esc(st.err) + '</p>'
      : shown.length ? shown.map(card).join('')
      : '<div class="empty">' + icon('check') + '<b>' + esc(tab[0] === 'todo' ? T('Nothing to decide', 'Nada para decidir') : T('Nothing here', 'Nada aqui')) + '</b>' +
        esc(tab[0] === 'todo' ? T('When a customer reports a problem, it shows up here with the photos.', 'Quando um cliente relatar um problema, ele aparece aqui com as fotos.') : '') + '</div>';
    var html = '<div translate="no"><div class="page-head"><div><p class="eyebrow">' + T('Customers', 'Clientes') + '</p><h1>' + T('Returns', 'Devoluções') + '</h1>' +
      '<p class="sub">' + T('Customers start returns on the site. Problems wait for you here; change-of-mind returns refund by themselves when they arrive.',
        'Os clientes começam a devolução pelo site. Problemas esperam vocês aqui; devoluções por arrependimento são reembolsadas sozinhas quando chegam.') + '</p></div></div>' +
      tabs + '<div class="rt-list">' + body + '</div></div>';
    return { title: T('Returns', 'Devoluções'), html: html };
  };

  ACT.rtPhotos = function (el) {
    var id = el.getAttribute('data-id'); el.disabled = true;
    h.call('adminReturnPhotos', { returnId: id }).then(function (r) { st.photos[id] = r.photos || []; var y = scrollY; h.route(); scrollTo(0, y); })
      .catch(function (e) { el.disabled = false; h.toast(h.friendlyError(e), true); });
  };

  /* a small form in a dialog: resolves with the form's values, or null */
  function ask(title, inner, okText) {
    return new Promise(function (resolve) {
      var d = document.createElement('dialog'); d.className = 'modal';
      d.setAttribute('translate', 'no');
      d.innerHTML = '<form method="dialog" class="in"><h2>' + esc(title) + '</h2>' + inner + '<div class="row end"><button class="btn btn-ghost" value="cancel">' + T('Cancel', 'Cancelar') + '</button><button class="btn btn-honey" value="ok">' + esc(okText) + '</button></div></form>';
      document.body.appendChild(d);
      d.addEventListener('close', function () {
        if (d.returnValue !== 'ok') { d.remove(); resolve(null); return; }
        var f = d.querySelector('form'), out = { note: (f.elements.note && f.elements.note.value) || '', photos: [] };
        Array.prototype.forEach.call(f.querySelectorAll('input[name="ph"]:checked'), function (c) { out.photos.push(Number(c.value)); });
        d.remove(); resolve(out);
      });
      if (d.showModal) d.showModal(); else d.setAttribute('open', '');
    });
  }

  ACT.rtDo = function (el) {
    var id = el.getAttribute('data-id'), action = el.getAttribute('data-do');
    var r = (S.returns || []).find(function (x) { return x.id === id; }); if (!r) return;
    var mind = r.kind === 'changed_mind';
    var prep;
    if (action === 'decline') {
      prep = ask(T('Decline this return', 'Recusar esta devolução'), '<p class="small">' + T('The customer gets an email with your note.', 'O cliente recebe um e-mail com o recado de vocês.') + '</p>' +
        '<label class="field"><span>' + T('Note for the customer (in English)', 'Recado para o cliente (em inglês)') + '</span><textarea class="input" name="note" rows="4" maxlength="1000" placeholder="The photo shows the magnet the way it was uploaded…"></textarea></label>', T('Decline and email', 'Recusar e avisar'));
    } else if (action === 'reprint') {
      var photoLines = (r.lines || []).filter(function (l) { return l.kind === 'photos'; });
      prep = !photoLines.length ? ask(T('Reprint for free', 'Reimprimir grátis'), '<p class="small">' + T('A new $0 order goes to production with these magnets, and the customer gets an email.', 'Um pedido novo de $0 vai para a produção com esses ímãs, e o cliente recebe um e-mail.') + '</p>', T('Reprint', 'Reimprimir'))
        : h.call('adminPhotoUrls', { orderId: r.orderId }).then(function (res) {
          var pack = (res.packs || []).find(function (p) { return p.index === photoLines[0].index; }) || (res.packs || [])[0] || { photos: [] };
          var need = photoLines.reduce(function (t, l) { return t + l.qty; }, 0);
          return ask(T('Which photos to reprint?', 'Quais fotos reimprimir?'), '<p class="small">' + T('The customer said ' + need + ' magnet(s). Tick them: they go to production in a new $0 order.', 'O cliente disse ' + need + (need === 1 ? ' ímã' : ' ímãs') + '. Marque quais: vão para a produção num pedido novo de $0.') + '</p>' +
            '<div class="rt-pick">' + pack.photos.map(function (p, i) { return '<label><input type="checkbox" name="ph" value="' + i + '"><img src="' + esc(p.thumb || p.url || '') + '" alt="' + (i + 1) + '"><span>' + (i + 1) + '</span></label>'; }).join('') + '</div>', T('Reprint', 'Reimprimir'));
        });
    } else {
      var amt = mind ? (r.estimate || {}).refund : r.value;
      prep = ask(T('Refund ', 'Reembolsar ') + money(amt), '<p class="small">' + (mind ? T('Use this when the parcel arrived but tracking didn’t update.', 'Use quando o pacote chegou mas o rastreio não atualizou.') : T('The money goes back to the customer’s card, and they get an email. They keep the magnets.', 'O dinheiro volta para o cartão do cliente e ele recebe um e-mail. Ele fica com os ímãs.')) + '</p>', T('Refund', 'Reembolsar'));
    }
    Promise.resolve(prep).then(function (v) {
      if (!v) return;
      if (action === 'reprint' && (r.lines || []).some(function (l) { return l.kind === 'photos'; }) && !v.photos.length) { h.toast(T('Tick at least one photo.', 'Marque pelo menos uma foto.'), true); return; }
      st.busy[id] = true; h.route();
      return h.call('adminReturnDecide', { returnId: id, action: action, note: v.note, photos: v.photos }).then(function (res) {
        h.toast(action === 'decline' ? T('Declined. The customer was emailed.', 'Recusado. O cliente foi avisado.') : action === 'reprint' ? T('Reprint ', 'Reimpressão ') + res.reprint.number + T(' is in Orders.', ' está em Pedidos.') : T('Refunded.', 'Reembolsado.'));
        return Promise.all([h.loadCol('returns'), h.loadOrders()]);
      }).catch(function (e) { h.toast(h.friendlyError(e), true); }).then(function () { st.busy[id] = false; h.updateBadges(); h.route(); });
    }).catch(function (e) { h.toast(h.friendlyError(e), true); });
  };
})();
