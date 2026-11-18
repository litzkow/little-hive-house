/* Little Hive House admin: Conteúdo (functions/content.js adminContent). The posts the owners make together: videos and
   photos passed to each other in full quality (uploaded and saved as the original files, never resized), the planned
   posts from the 6-month calendar, captions to copy, scripts, and which networks already got each post.
   The screen picks its own language (T(en, pt)) and is marked translate="no". */
(function () {
  'use strict';
  var A = window.LHHAdmin, S = A.S, h = A.h, V = A.VIEWS, ACT = A.ACT;
  var esc = h.esc;
  function T(en, pt) { return h.LANG() === 'pt' ? pt : en; }
  var SDK = 'https://www.gstatic.com/firebasejs/10.14.1/firebase-storage-compat.js';
  var st = { data: null, err: null, loading: false, busy: false, tab: 'next', urls: {}, uploads: {} };

  function rerender() { if (A.parseHash().view === 'content') { var y = scrollY; h.route(); scrollTo(0, y); } }
  function load(action, args, done) {
    st.busy = true;
    return h.call('adminContent', Object.assign({ action: action || 'list' }, args || {})).then(function (d) { st.data = d; st.err = null; if (done) h.toast(done); return d; })
      .catch(function (e) { var m = h.friendlyError(e); if (!action || action === 'list') st.err = m; else h.toast(m, true); return null; })
      .then(function (d) { st.busy = false; st.loading = false; rerender(); return d; });
  }
  var storageReady = null;
  function storage() {
    if (!storageReady) storageReady = new Promise(function (resolve, reject) {
      if (window.firebase && firebase.storage) return resolve(firebase.storage());
      var s = document.createElement('script'); s.src = SDK;
      s.onload = function () { resolve(firebase.storage()); };
      s.onerror = function () { storageReady = null; reject(new Error(T('Couldn’t load the file tools. Check the internet.', 'Não deu para carregar. Confira a internet.'))); };
      document.head.appendChild(s);
    });
    return storageReady;
  }
  function urlOf(path) {
    if (st.urls[path]) return Promise.resolve(st.urls[path]);
    return storage().then(function (s) { return s.ref(path).getDownloadURL(); }).then(function (u) { st.urls[path] = u; return u; });
  }

  /* ---------- words ---------- */
  var KIND = { video: ['Video', 'Vídeo', '🎬'], photo: ['Photo / art', 'Foto / arte', '🖼️'], idea: ['Idea', 'Ideia', '💡'] };
  var STATUS = { idea: ['Idea', 'Ideia'], todo: ['In production', 'Em produção'], ready: ['Ready to post', 'Pronto para postar'], scheduled: ['Scheduled', 'Agendado'], posted: ['Posted', 'Postado'] };
  var NETS = [['instagram', 'Instagram'], ['facebook', 'Facebook'], ['tiktok', 'TikTok']];
  var WEEK = { pt: ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'], en: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] };
  var MON = { pt: ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'], en: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] };
  function when(it) {
    if (!it.date) return T('No date', 'Sem data');
    var p = it.date.split('-'), d = new Date(+p[0], +p[1] - 1, +p[2]), L = h.LANG() === 'pt' ? 'pt' : 'en';
    var s = WEEK[L][d.getDay()] + ' ' + (+p[2]) + '/' + MON[L][+p[1] - 1];
    if (it.time) s += ' · ' + (L === 'pt' ? it.time.replace(':00', 'h').replace(':', 'h') : it.time);
    return s;
  }
  function size(n) { n = Number(n) || 0; return n >= 1073741824 ? (n / 1073741824).toFixed(1) + ' GB' : n >= 1048576 ? (n / 1048576).toFixed(0) + ' MB' : Math.max(1, Math.round(n / 1024)) + ' KB'; }
  function item(id) { return ((st.data && st.data.items) || []).find(function (x) { return x.id === id; }); }

  /* ---------- a post ---------- */
  function fileTile(it, f) {
    var isVid = /^video\//.test(f.type), url = st.urls[f.path];
    if (!url) urlOf(f.path).then(rerender).catch(function () {});
    var media = !url ? '<span class="ct-media ct-wait"></span>'
      : isVid ? '<video class="ct-media" src="' + esc(url) + '#t=0.1" preload="metadata" playsinline controls></video>'
      : '<a href="' + esc(url) + '" target="_blank" rel="noopener"><img class="ct-media" src="' + esc(url) + '" alt="" loading="lazy"></a>';
    return '<figure class="ct-file">' + media + '<figcaption><span class="tiny">' + esc(f.name) + ' · ' + size(f.size) + (f.w && f.h ? ' · ' + f.w + '×' + f.h : '') + '</span>' +
      '<span class="row"><button class="btn btn-honey btn-sm" data-act="ctSave" data-id="' + esc(it.id) + '" data-path="' + esc(f.path) + '">' + T('Save to phone', 'Salvar no celular') + '</button>' +
      '<button class="icon-btn" data-act="ctDelFile" data-id="' + esc(it.id) + '" data-path="' + esc(f.path) + '" aria-label="' + T('Remove', 'Apagar') + '">' + h.icon('trash') + '</button></span></figcaption></figure>';
  }
  function card(it) {
    var k = KIND[it.kind] || KIND.idea, s = STATUS[it.status] || STATUS.idea, b = st.busy ? ' disabled' : '';
    var up = st.uploads[it.id];
    var nets = NETS.filter(function (n) { return it.nets && it.nets[n[0]]; }).map(function (n) {
      var done = it.posted && it.posted[n[0]];
      return '<span class="ct-net' + (done ? ' done' : '') + '">' + (done ? '✓ ' : '') + n[1] + '</span>';
    }).join('');
    var late = it.date && it.status !== 'posted' && it.date < st.data.today;
    return '<article class="card ct-card ct-' + esc(it.status) + '" id="ct-' + esc(it.id) + '">' +
      '<div class="ct-top"><span class="ct-when' + (late ? ' late' : '') + '">' + k[2] + ' ' + esc(when(it)) + '</span><span class="sp-pill ct-st-' + esc(it.status) + '">' + esc(T(s[0], s[1])) + '</span></div>' +
      '<h3>' + esc(it.title || T('(no title)', '(sem título)')) + '</h3>' +
      (nets ? '<div class="ct-nets">' + nets + '</div>' : '') +
      ((it.files || []).length ? '<div class="ct-files">' + it.files.map(function (f) { return fileTile(it, f); }).join('') + '</div>'
        : /^https:\/\//.test(it.preview || '') ? '<a class="ct-prev" href="' + esc(it.igLink || it.fbLink || it.preview) + '" target="_blank" rel="noopener"><img src="' + esc(it.preview) + '" alt="" loading="lazy" referrerpolicy="no-referrer"></a>' : '') +
      (it.igLink || it.fbLink || it.igStats ? '<p class="tiny ct-links">' + (it.igStats ? '♥ ' + it.igStats.likes + ' · 💬 ' + it.igStats.comments + ' · ' : '') +
        (it.igLink ? '<a href="' + esc(it.igLink) + '" target="_blank" rel="noopener">Instagram ›</a> ' : '') + (it.fbLink ? '<a href="' + esc(it.fbLink) + '" target="_blank" rel="noopener">Facebook ›</a>' : '') + '</p>' : '') +
      (up ? '<div class="ct-up"><div class="sp-bar"><i style="width:' + Math.max(3, up.pct) + '%"></i></div><p class="tiny">' + esc(up.text) + '</p></div>' : '') +
      (it.planFile && !(it.files || []).length ? '<p class="tiny muted">' + (it.kind === 'video' ? T('Plan B, ready-made video in the month’s pack: ', 'Plano B, vídeo pronto no pacote do mês: ') : T('Art in the month’s pack: ', 'Arte no pacote do mês: ')) + '<code>' + esc(it.planFile) + '</code></p>' : '') +
      (it.caption ? '<details class="ct-more"><summary>' + T('Caption', 'Legenda') + '</summary><p class="ct-cap">' + esc(it.caption) + '</p>' +
        '<button class="btn btn-ghost btn-sm" data-act="ctCopy" data-id="' + esc(it.id) + '">' + h.icon('copy') + T('Copy caption', 'Copiar legenda') + '</button></details>' : '') +
      (it.script || it.onScreen || it.tip ? '<details class="ct-more"><summary>' + T('How to film', 'Como gravar') + '</summary>' +
        (it.script ? '<p>' + esc(it.script) + '</p>' : '') + (it.onScreen ? '<p><b>' + T('Text on screen: ', 'Texto na tela: ') + '</b>' + esc(it.onScreen) + '</p>' : '') +
        (it.tip ? '<p class="small muted">' + esc(it.tip) + '</p>' : '') + '</details>' : '') +
      (it.notes ? '<p class="small ct-notes">📝 ' + esc(it.notes) + '</p>' : '') +
      '<div class="row sp-acts">' +
      '<label class="btn btn-honey btn-sm ct-pick' + (up ? ' disabled' : '') + '">' + T('+ Video or photo', '+ Vídeo ou foto') +
        '<input type="file" accept="image/*,video/*" multiple data-ct-upload="' + esc(it.id) + '" hidden' + (up ? ' disabled' : '') + '></label>' +
      (it.status !== 'posted' ? '<button class="btn btn-ghost btn-sm" data-act="ctPosted" data-id="' + esc(it.id) + '"' + b + '>' + T('Posted', 'Postei') + '</button>' : '') +
      '<button class="btn btn-ghost btn-sm" data-act="ctEdit" data-id="' + esc(it.id) + '"' + b + '>' + T('Edit', 'Editar') + '</button>' +
      '</div></article>';
  }

  V.content = function () {
    if (!st.data && !st.loading && !st.err) { st.loading = true; load('list'); }
    var d = st.data;
    var head = '<div class="page-head"><div><p class="eyebrow">Marketing</p><h1>' + T('Content', 'Conteúdo') + '</h1>' +
      '<p class="sub">' + T('Videos and photos for Instagram, Facebook and TikTok, passed between you in full quality: what one uploads, the other gets a notification and saves to the phone, exactly the same file.',
        'Vídeos e fotos para Instagram, Facebook e TikTok, passados entre vocês na qualidade original: o que um sobe, o outro recebe um aviso e salva no celular, o mesmo arquivo, sem perder nada.') + '</p></div>' +
      '<div class="actions"><button class="btn btn-honey btn-sm" data-act="ctNew">' + T('+ New post or idea', '+ Novo post ou ideia') + '</button></div></div>';
    if (!d) return { title: T('Content', 'Conteúdo'), html: '<div translate="no">' + head + (st.err ? '<p class="err">' + esc(st.err) + '</p>' : '<div class="loading"><span>' + T('Loading…', 'Carregando…') + '</span></div>') + '</div>' };
    var all = d.items, t = d.today;
    var open = function (i) { return i.status !== 'posted' && i.status !== 'idea'; };
    var TABS = [
      ['next', T('Agenda', 'Agenda'), function (i) { return open(i) && (!i.date || i.date >= t); }],
      ['ideas', T('Ideas', 'Ideias'), function (i) { return i.status === 'idea'; }],
      ['todo', T('In production', 'Produção'), function (i) { return i.status === 'todo'; }],
      ['ready', T('Ready', 'Prontos'), function (i) { return i.status === 'ready'; }],
      ['scheduled', T('Scheduled', 'Agendados'), function (i) { return i.status === 'scheduled'; }],
      ['posted', T('Posted', 'Postados'), function (i) { return i.status === 'posted'; }],
      ['late', T('Overdue', 'Atrasados'), function (i) { return open(i) && i.date && i.date < t; }]
    ];
    var cur = TABS.find(function (x) { return x[0] === st.tab; }) || TABS[0];
    var list = all.filter(cur[2]);
    if (cur[0] === 'posted') list = list.slice().reverse();
    var ready = all.filter(function (i) { return i.status === 'ready' && (i.files || []).length; }).length;
    var week = all.filter(function (i) { return i.status !== 'posted' && i.date && i.date >= t && i.date <= addDays(t, 7); }).length;
    var lateN = all.filter(TABS[6][2]).length, postedWeek = all.filter(function (i) { return i.status === 'posted' && i.date && i.date >= addDays(t, -7); }).length;
    var tiles = '<div class="tiles">' + h.tile(T('Next 7 days', 'Próximos 7 dias'), String(week), T('posts to go out', 'posts para sair'), true) +
      h.tile(T('Ready, with file', 'Prontos, com arquivo'), String(ready), T('just post', 'é só postar')) +
      h.tile(T('Posted this week', 'Postados na semana'), String(postedWeek), T('Instagram, Facebook, TikTok', 'Instagram, Facebook, TikTok')) +
      h.tile(T('Overdue', 'Atrasados'), String(lateN), lateN ? T('the day passed', 'o dia já passou') : T('all on time', 'tudo em dia')) + '</div>';
    /* the week ahead: one chip per day with what goes out */
    var strip = '<div class="ct-week">' + [0, 1, 2, 3, 4, 5, 6].map(function (n) {
      var dd = addDays(t, n), its = all.filter(function (i) { return i.date === dd; });
      var p = dd.split('-'), L = h.LANG() === 'pt' ? 'pt' : 'en', wd = WEEK[L][new Date(+p[0], +p[1] - 1, +p[2]).getDay()];
      return '<div class="ct-day' + (n === 0 ? ' today' : '') + '"><b>' + (n === 0 ? T('Today', 'Hoje') : wd) + '</b><span>' + (+p[2]) + '</span><i>' +
        (its.length ? its.map(function (i) { return '<em class="ct-dot ct-st-' + esc(i.status) + '" title="' + esc(i.title) + '">' + (KIND[i.kind] || KIND.idea)[2] + '</em>'; }).join('') : '·') + '</i></div>';
    }).join('') + '</div>';
    var sy = d.sync || {}, syncLine = sy.connected === false ? T('Connect Meta on the Ads page to bring in what is posted and scheduled.', 'Conecte o Meta na página Anúncios para trazer o que já está postado e agendado.')
      : sy.at ? T('Meta checked ', 'Meta conferido ') + esc(h.fmtDT(sy.at)) + (sy.counts ? ' · ' + T(sy.counts.instagram + ' on Instagram, ' + sy.counts.facebook + ' on Facebook, ' + sy.counts.scheduled + ' scheduled', sy.counts.instagram + ' no Instagram, ' + sy.counts.facebook + ' no Facebook, ' + sy.counts.scheduled + ' agendados') : '') : '';
    var syncErr = sy.errors && Object.keys(sy.errors).length ? '<p class="tiny err">' + Object.keys(sy.errors).map(function (k) { return esc(k + ': ' + sy.errors[k]); }).join(' · ') + '</p>' : '';
    var syncBar = '<div class="ct-sync"><span class="tiny muted">' + syncLine + '</span><button class="btn btn-ghost btn-sm" data-act="ctSync"' + (st.busy ? ' disabled' : '') + '>' + h.icon('refresh') + T('Update from Meta', 'Atualizar do Meta') + '</button></div>' + syncErr;
    var tabs = '<div class="seg ct-tabs" role="tablist">' + TABS.map(function (x) {
      var n = all.filter(x[2]).length;
      return '<button role="tab" data-act="ctTab" data-tab="' + x[0] + '"' + (x[0] === cur[0] ? ' class="on" aria-selected="true"' : '') + '>' + esc(x[1]) + (n ? ' <span class="count">' + n + '</span>' : '') + '</button>';
    }).join('') + '</div>';
    var shown = cur[0] === 'next' ? list.slice(0, st.more ? 200 : 14) : list;
    var body = shown.length ? '<div class="ct-list">' + shown.map(card).join('') + '</div>' +
      (cur[0] === 'next' && list.length > shown.length ? '<p><button class="btn btn-ghost" data-act="ctMore">' + T('Show all ' + list.length, 'Mostrar todos os ' + list.length) + '</button></p>' : '')
      : '<p class="muted">' + T('Nothing here.', 'Nada aqui.') + '</p>';
    var tip = '<p class="tiny muted ct-tip">' + T('Full quality on iPhone: when picking a video or photo, tap Options at the top and choose Current, so the iPhone doesn’t shrink it.',
      'Qualidade máxima no iPhone: ao escolher o vídeo ou a foto, toque em Opções, lá em cima, e escolha Atual. Assim o iPhone não diminui o arquivo.') + '</p>';
    var lateBanner = lateN && cur[0] !== 'late' ? '<button class="ct-late" data-act="ctTab" data-tab="late">⚠️ ' + T(lateN + ' post(s) past their day and not posted. See them', lateN + (lateN === 1 ? ' post passou do dia e não foi postado. Ver' : ' posts passaram do dia e não foram postados. Ver')) + ' ›</button>' : '';
    return { title: T('Content', 'Conteúdo'), html: '<div translate="no" class="ct">' + head + tiles + strip + syncBar + lateBanner + tabs + tip + body + '</div>' };
  };
  function addDays(day, n) { var p = day.split('-'), d = new Date(+p[0], +p[1] - 1, +p[2] + n); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }

  /* ---------- uploads: the original file, as it is ---------- */
  function mediaSize(file) {
    return new Promise(function (resolve) {
      var url = URL.createObjectURL(file), done = function (o) { URL.revokeObjectURL(url); resolve(o); };
      if (/^video\//.test(file.type)) {
        var v = document.createElement('video'); v.preload = 'metadata'; v.muted = true;
        v.onloadedmetadata = function () { done({ w: v.videoWidth, h: v.videoHeight, dur: Math.round(v.duration || 0) }); };
        v.onerror = function () { done({}); }; v.src = url;
      } else {
        var i = new Image(); i.onload = function () { done({ w: i.naturalWidth, h: i.naturalHeight }); }; i.onerror = function () { done({}); }; i.src = url;
      }
      setTimeout(function () { done({}); }, 8000);
    });
  }
  function safeName(n) { return String(n || 'file').replace(/[^A-Za-z0-9._ ()-]/g, '_').slice(-100); }
  function uploadAll(id, files) {
    var list = Array.prototype.slice.call(files).filter(function (f) { return /^(image|video)\//.test(f.type); });
    if (!list.length) { h.toast(T('Only photos and videos.', 'Só fotos e vídeos.'), true); return; }
    var i = 0;
    var next = function () {
      if (i >= list.length) { delete st.uploads[id]; return load('list', null, T('Sent. The other phone got a notification.', 'Enviado. O outro celular recebeu um aviso.')); }
      var f = list[i++], path = 'content/' + id + '/' + Date.now() + '-' + safeName(f.name);
      st.uploads[id] = { pct: 0, text: T('Uploading ', 'Enviando ') + (list.length > 1 ? i + '/' + list.length + ' · ' : '') + size(f.size) + '…' };
      rerender();
      return Promise.all([storage(), mediaSize(f)]).then(function (r) {
        var dims = r[1];
        return new Promise(function (resolve, reject) {
          // the file goes as it is: no resizing, no re-encoding
          var task = r[0].ref(path).put(f, { contentType: f.type, customMetadata: { name: safeName(f.name) } });
          task.on('state_changed', function (s) {
            var pct = s.totalBytes ? Math.round(s.bytesTransferred / s.totalBytes * 100) : 0;
            st.uploads[id] = { pct: pct, text: T('Uploading ', 'Enviando ') + (list.length > 1 ? i + '/' + list.length + ' · ' : '') + pct + '% de ' + size(f.size) };
            var bar = document.querySelector('#ct-' + id + ' .ct-up');
            if (bar) { bar.querySelector('i').style.width = Math.max(3, pct) + '%'; bar.querySelector('p').textContent = st.uploads[id].text; }
          }, reject, function () { resolve(dims); });
        });
      }).then(function (dims) {
        return h.call('adminContent', { action: 'addFile', id: id, path: path, name: f.name, type: f.type, size: f.size, w: dims.w, h: dims.h, dur: dims.dur });
      }).then(next).catch(function (e) {
        delete st.uploads[id];
        h.toast(T('The upload stopped: ', 'O envio parou: ') + h.friendlyError(e), true);
        rerender();
      });
    };
    next();
  }
  document.addEventListener('change', function (ev) {
    var el = ev.target;
    if (!el || !el.matches || !el.matches('[data-ct-upload]')) return;
    var id = el.getAttribute('data-ct-upload'), files = el.files;
    if (files && files.length) uploadAll(id, files);
    el.value = '';
  });

  /* ---------- saving to the phone: the same bytes that were uploaded ---------- */
  ACT.ctSave = function (el) {
    var it = item(el.getAttribute('data-id')), path = el.getAttribute('data-path');
    var f = it && (it.files || []).find(function (x) { return x.path === path; });
    if (!f) return;
    var label = el.textContent;
    el.disabled = true; el.textContent = T('Preparing…', 'Preparando…');
    var reset = function () { el.disabled = false; el.textContent = label; };
    urlOf(path).then(function (url) {
      // big videos open in Safari's own player (Share › Save Video), so the phone doesn't run out of memory
      if (f.size > 350 * 1048576 || !navigator.canShare) { window.open(url, '_blank', 'noopener'); reset(); return; }
      return fetch(url).then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.blob(); }).then(function (b) {
        var file = new File([b], f.name, { type: f.type || b.type });
        if (navigator.canShare({ files: [file] })) return navigator.share({ files: [file] }).catch(function () {});
        var a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = f.name; document.body.appendChild(a); a.click(); a.remove();
      }).then(reset);
    }).catch(function (e) { reset(); h.toast(h.friendlyError(e), true); });
  };
  ACT.ctDelFile = function (el) {
    var id = el.getAttribute('data-id'), path = el.getAttribute('data-path');
    h.dialog({ title: T('Delete this file?', 'Apagar este arquivo?'), html: '<p>' + T('It is deleted for both of you.', 'Ele some para os dois.') + '</p>', ok: T('Delete', 'Apagar'), cancel: T('Cancel', 'Cancelar'), danger: true })
      .then(function (ok) { if (ok) load('removeFile', { id: id, path: path }); });
  };
  ACT.ctCopy = function (el) { var it = item(el.getAttribute('data-id')); if (it) h.copyText(it.caption, T('Caption copied.', 'Legenda copiada.')); };
  ACT.ctTab = function (el) { st.tab = el.getAttribute('data-tab'); h.route(); };
  ACT.ctMore = function () { st.more = true; h.route(); };
  ACT.ctSync = function () { load('sync', {}, T('Up to date with Meta.', 'Atualizado com o Meta.')); };

  /* ---------- the form ---------- */
  function ask(title, inner, okText, extra) {
    return new Promise(function (resolve) {
      var dlg = document.createElement('dialog'); dlg.className = 'modal'; dlg.setAttribute('translate', 'no');
      dlg.innerHTML = '<form method="dialog" class="in"><h2>' + esc(title) + '</h2>' + inner + '<div class="row end">' + (extra || '') +
        '<button class="btn btn-ghost" value="cancel">' + T('Cancel', 'Cancelar') + '</button><button class="btn btn-honey" value="ok">' + esc(okText || 'OK') + '</button></div></form>';
      document.body.appendChild(dlg);
      dlg.addEventListener('close', function () {
        var out = null;
        if (dlg.returnValue === 'ok') { out = {}; Array.prototype.forEach.call(dlg.querySelectorAll('[name]'), function (e) { out[e.name] = e.type === 'checkbox' ? e.checked : e.value; }); }
        if (dlg.returnValue === 'delete') out = { __delete: true };
        dlg.remove(); resolve(out);
      });
      if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    });
  }
  function field(name, label, value, type) {
    return '<label class="field"><span>' + esc(label) + '</span><input class="input" name="' + name + '" value="' + esc(value == null ? '' : value) + '"' + (type ? ' type="' + type + '"' : '') + '></label>';
  }
  function area(name, label, value, rows) { return '<label class="field"><span>' + esc(label) + '</span><textarea class="input" name="' + name + '" rows="' + (rows || 3) + '">' + esc(value || '') + '</textarea></label>'; }
  function select(name, label, value, opts) {
    return '<label class="field"><span>' + esc(label) + '</span><select class="input" name="' + name + '">' + opts.map(function (o) { return '<option value="' + o[0] + '"' + (o[0] === value ? ' selected' : '') + '>' + esc(o[1]) + '</option>'; }).join('') + '</select></label>';
  }
  function form(it) {
    it = it || { kind: 'video', status: 'todo', nets: { instagram: true, facebook: true, tiktok: true } };
    return field('title', T('Title', 'Título'), it.title) +
      select('kind', T('Kind', 'Tipo'), it.kind, Object.keys(KIND).map(function (k) { return [k, T(KIND[k][0], KIND[k][1])]; })) +
      select('status', T('Status', 'Situação'), it.status, Object.keys(STATUS).map(function (k) { return [k, T(STATUS[k][0], STATUS[k][1])]; })) +
      '<div class="row">' + field('date', T('Day', 'Dia'), it.date, 'date') + field('time', T('Time', 'Hora'), it.time, 'time') + '</div>' +
      '<div class="ct-checks">' + NETS.map(function (n) { return '<label><input type="checkbox" name="net_' + n[0] + '"' + (it.nets && it.nets[n[0]] ? ' checked' : '') + '> ' + n[1] + '</label>'; }).join('') + '</div>' +
      area('caption', T('Caption (English, for the post)', 'Legenda (em inglês, para o post)'), it.caption, 4) +
      area('script', T('How to film', 'Como gravar'), it.script, 2) + field('onScreen', T('Text on screen', 'Texto na tela'), it.onScreen) +
      area('notes', T('Notes between you', 'Recado entre vocês'), it.notes, 2);
  }
  function toItem(v) {
    var o = { title: v.title, kind: v.kind, status: v.status, date: v.date, time: v.time, caption: v.caption, script: v.script, onScreen: v.onScreen, notes: v.notes, nets: {} };
    NETS.forEach(function (n) { o.nets[n[0]] = !!v['net_' + n[0]]; });
    return o;
  }
  ACT.ctNew = function () {
    ask(T('New post or idea', 'Novo post ou ideia'), form(null) + '<p class="tiny muted">' + T('Save it, then add the video or photo on the card.', 'Salve e depois toque em "+ Vídeo ou foto" no cartão.') + '</p>', T('Save', 'Salvar'))
      .then(function (v) {
        if (!v) return;
        load('save', { item: toItem(v) }).then(function (d) {
          if (!d || !d.id) return;
          var it = item(d.id);
          st.tab = it && it.status === 'idea' ? 'ideas' : it && it.date && it.date < d.today ? 'late' : 'next';
          h.route();
          setTimeout(function () { var c = document.getElementById('ct-' + d.id); if (c) c.scrollIntoView({ behavior: 'smooth', block: 'center' }); }, 60);
        });
      });
  };
  ACT.ctEdit = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    ask(T('Edit', 'Editar'), form(it), T('Save', 'Salvar'), '<button class="btn btn-ghost danger" value="delete" style="margin-right:auto">' + T('Delete post', 'Apagar post') + '</button>').then(function (v) {
      if (!v) return;
      if (v.__delete) {
        return h.dialog({ title: T('Delete this post and its files?', 'Apagar este post e os arquivos dele?'), html: '', ok: T('Delete', 'Apagar'), cancel: T('Cancel', 'Cancelar'), danger: true })
          .then(function (ok) { if (ok) load('remove', { id: it.id }, T('Deleted.', 'Apagado.')); });
      }
      load('save', { id: it.id, item: toItem(v) }, T('Saved.', 'Salvo.'));
    });
  };
  ACT.ctPosted = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    var nets = NETS.filter(function (n) { return it.nets && it.nets[n[0]]; });
    if (!nets.length) nets = NETS;
    ask(T('Where did it go out?', 'Onde já foi postado?'), '<div class="ct-checks">' + nets.map(function (n) {
      return '<label><input type="checkbox" name="' + n[0] + '"' + (it.posted && it.posted[n[0]] ? ' checked' : ' checked') + '> ' + n[1] + '</label>';
    }).join('') + '</div><p class="tiny muted">' + T('When every network has it, it moves to Posted.', 'Quando todas as redes tiverem, ele vai para Postados.') + '</p>', T('Save', 'Salvar')).then(function (v) {
      if (v) load('posted', { id: it.id, nets: v }, T('Saved.', 'Salvo.'));
    });
  };
})();
