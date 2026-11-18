/* Little Hive House admin: Conteúdo (functions/content.js adminContent). Where the owners pass videos and photos to each
   other (the original files, never resized: uploaded and saved to the phone as they are) and see what is on Meta.
   Three tabs:
   - Compartilhados: everything they sent each other, newest first, who sent it, the video playing right there.
   - No Meta: what they marked as scheduled in Meta Business Suite (Meta doesn't let apps read that schedule) and what
     already went out on Instagram / Facebook (read from Meta by the server; Instagram videos play here).
   - Ideias: written ideas and idea videos.
   Sending something tells the other owner by push ("Thiago mandou um vídeo novo"). What's new since the last visit
   gets a "Novo" tag. The screen picks its own language (T(en, pt)) and is marked translate="no". */
(function () {
  'use strict';
  var A = window.LHHAdmin, S = A.S, h = A.h, V = A.VIEWS, ACT = A.ACT;
  var esc = h.esc;
  function T(en, pt) { return h.LANG() === 'pt' ? pt : en; }
  var SDK = 'https://www.gstatic.com/firebasejs/10.14.1/firebase-storage-compat.js';
  var SEEN_KEY = 'lhh-content-seen';
  var st = { data: null, err: null, loading: false, busy: false, tab: 'shared', urls: {}, uploads: {}, more: false, seenAt: null };

  function rerender() { if (A.parseHash().view === 'content') { var y = scrollY; h.route(); scrollTo(0, y); } }
  function load(action, args, done) {
    st.busy = true;
    return h.call('adminContent', Object.assign({ action: action || 'list' }, args || {})).then(function (d) { st.data = d; st.err = null; if (done) h.toast(done); return d; })
      .catch(function (e) { var m = h.friendlyError(e); if (!action || action === 'list') st.err = m; else h.toast(m, true); return null; })
      .then(function (d) { st.busy = false; st.loading = false; rerender(); return d; });
  }
  /* the page keeps itself up to date: every minute while it is open, and when the app comes back to the screen.
     It only redraws when something changed, and never while a video plays, a window is open or a file is going up. */
  function snap(d) { return JSON.stringify((d && d.items) || []); }
  function quietRefresh() {
    if (A.parseHash().view !== 'content' || document.hidden || st.busy || !st.data) return;
    h.call('adminContent', { action: 'list' }).then(function (d) {
      if (!d || A.parseHash().view !== 'content') return;
      var playing = Array.prototype.some.call(document.querySelectorAll('.ct video'), function (v) { return !v.paused && !v.ended; });
      var busy = st.busy || document.querySelector('dialog[open]') || Object.keys(st.uploads).length || playing;
      if (snap(d) === snap(st.data)) { st.data.sync = d.sync; st.data.today = d.today; var a = document.querySelector('[data-ct-ago]'); if (a && d.sync && d.sync.at) a.textContent = ago(d.sync.at); return; }
      if (busy) return;
      st.data = d; st.err = null; rerender();
    }).catch(function () {});
  }
  setInterval(quietRefresh, 60000);
  document.addEventListener('visibilitychange', function () { if (!document.hidden) quietRefresh(); });
  window.addEventListener('hashchange', function () { setTimeout(quietRefresh, 300); });
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
  /* after each render, the videos and photos get their links without redrawing the page (a playing video keeps playing) */
  function hydrate() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-ct-path]:not([src])'), function (el) {
      var p = el.getAttribute('data-ct-path');
      urlOf(p).then(function (u) { el.setAttribute('src', el.tagName === 'VIDEO' ? u + '#t=0.1' : u); el.classList.remove('ct-wait'); }).catch(function () {});
    });
  }

  /* ---------- words ---------- */
  var NETS = [['instagram', 'Instagram'], ['facebook', 'Facebook'], ['tiktok', 'TikTok']];
  var WEEK = { pt: ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sáb'], en: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] };
  var MON = { pt: ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'], en: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] };
  function pt() { return h.LANG() === 'pt'; }
  function hm(time) { return !time ? '' : pt() ? time.replace(':00', 'h').replace(':', 'h') : time; }
  function dayLabel(date) {
    var p = date.split('-'), d = new Date(+p[0], +p[1] - 1, +p[2]), L = pt() ? 'pt' : 'en';
    return WEEK[L][d.getDay()] + ' ' + (+p[2]) + '/' + MON[L][+p[1] - 1];
  }
  function daysFrom(date) { return Math.round((Date.parse(date + 'T12:00:00Z') - Date.parse(st.data.today + 'T12:00:00Z')) / 86400000); }
  /* "sai hoje às 19h", "amanhã às 11h30", "sex 21/nov às 9h" */
  function goesOut(it) {
    if (!it.date) return T('no date', 'sem data');
    var n = daysFrom(it.date), at = it.time ? (pt() ? ' às ' : ' at ') + hm(it.time) : '';
    return (n === 0 ? T('today', 'hoje') : n === 1 ? T('tomorrow', 'amanhã') : dayLabel(it.date)) + at;
  }
  /* "qui 20/nov às 19h (amanhã)" */
  function fullWhen(it, rel) {
    if (!it.date) return '';
    var n = daysFrom(it.date), at = it.time ? (pt() ? ' às ' : ' at ') + hm(it.time) : '';
    var tag = !rel ? '' : n === 0 ? T(' (today)', ' (hoje)') : n === 1 ? T(' (tomorrow)', ' (amanhã)') : n === -1 ? T(' (yesterday)', ' (ontem)') : '';
    return dayLabel(it.date) + at + tag;
  }
  /* "agora", "há 5 min", "há 2 h", "ontem", "há 3 dias", "15/nov" */
  function ago(iso) {
    var s = (Date.now() - Date.parse(iso)) / 1000;
    if (!isFinite(s)) return '';
    if (s < 60) return T('just now', 'agora');
    if (s < 3600) return T(Math.floor(s / 60) + ' min ago', 'há ' + Math.floor(s / 60) + ' min');
    if (s < 86400) return T(Math.floor(s / 3600) + ' h ago', 'há ' + Math.floor(s / 3600) + ' h');
    if (s < 172800) return T('yesterday', 'ontem');
    if (s < 7 * 86400) return T(Math.floor(s / 86400) + ' days ago', 'há ' + Math.floor(s / 86400) + ' dias');
    var d = new Date(iso); return d.getDate() + '/' + MON[pt() ? 'pt' : 'en'][d.getMonth()];
  }
  function size(n) { n = Number(n) || 0; return n >= 1073741824 ? (n / 1073741824).toFixed(1) + ' GB' : n >= 1048576 ? (n / 1048576).toFixed(0) + ' MB' : Math.max(1, Math.round(n / 1024)) + ' KB'; }
  function item(id) { return ((st.data && st.data.items) || []).find(function (x) { return x.id === id; }); }
  function me() {
    var u = S.user || {}, n = String(u.displayName || String(u.email || '').split('@')[0].replace(/[._\d-]+/g, ' ') || '').trim().split(/\s+/)[0] || '';
    return n.charAt(0).toUpperCase() + n.slice(1).toLowerCase();
  }
  function sender(it) { var f = (it.files || [])[(it.files || []).length - 1]; return (f && f.byName) || it.byName || ''; }
  function sentAt(it) { var f = (it.files || [])[(it.files || []).length - 1]; return (f && f.at) || it.at || ''; }
  function isNew(it) { var who = sender(it), at = sentAt(it); return !!(st.seenAt && at && at > st.seenAt && who && who !== me()); }

  /* ---------- pieces of a card ---------- */
  function avatar(name) {
    var n = name || '?', hue = n === 'Karina' ? 'ct-av-k' : n === 'Thiago' ? 'ct-av-t' : '';
    return '<span class="ct-av ' + hue + '">' + esc(n.charAt(0)) + '</span>';
  }
  function fileMedia(it, f, big) {
    var isVid = /^video\//.test(f.type), url = st.urls[f.path];
    var media = isVid
      ? '<video class="ct-media' + (url ? '' : ' ct-wait') + '" data-ct-path="' + esc(f.path) + '"' + (url ? ' src="' + esc(url) + '#t=0.1"' : '') + ' preload="metadata" playsinline controls></video>'
      : '<img class="ct-media' + (url ? '' : ' ct-wait') + '" data-ct-path="' + esc(f.path) + '"' + (url ? ' src="' + esc(url) + '"' : '') + ' alt="" loading="lazy">';
    return '<figure class="ct-file' + (big ? ' big' : '') + '">' + media + '<figcaption>' +
      '<button class="btn btn-honey btn-sm" data-act="ctSave" data-id="' + esc(it.id) + '" data-path="' + esc(f.path) + '">' + h.icon('download') + T('Save to phone', 'Baixar no celular') + '</button>' +
      '<span class="tiny muted ct-fname">' + esc(String(f.name || '').replace(/\.[a-z0-9]+$/i, '')) + ' · ' + size(f.size) + (f.dur ? ' · ' + f.dur + 's' : '') + '</span>' +
      '<button class="icon-btn" data-act="ctDelFile" data-id="' + esc(it.id) + '" data-path="' + esc(f.path) + '" aria-label="' + T('Delete file', 'Apagar arquivo') + '">' + h.icon('trash') + '</button>' +
      '</figcaption></figure>';
  }
  function metaMedia(it) {
    var link = it.igLink || it.fbLink || '';
    if (it.kind === 'video' && /^https:\/\//.test(it.mediaUrl || ''))
      return '<figure class="ct-file big"><video class="ct-media" src="' + esc(it.mediaUrl) + '" poster="' + esc(it.preview || '') + '" preload="none" playsinline controls></video>' +
        '<figcaption><a class="btn btn-honey btn-sm" href="' + esc(it.mediaUrl) + '" target="_blank" rel="noopener" download>' + h.icon('download') + T('Download', 'Baixar') + '</a>' +
        '<span class="tiny muted ct-fname">' + T('opens the video: tap Share › Save Video', 'abre o vídeo: toque em Compartilhar › Salvar vídeo') + '</span></figcaption></figure>';
    if (/^https:\/\//.test(it.preview || ''))
      return '<figure class="ct-file big"><a href="' + esc(link || it.preview) + '" target="_blank" rel="noopener"><img class="ct-media" src="' + esc(it.preview) + '" alt="" loading="lazy" referrerpolicy="no-referrer"></a></figure>';
    return '';
  }
  function upBar(it) {
    var up = st.uploads[it.id];
    return up ? '<div class="ct-up"><div class="sp-bar"><i style="width:' + Math.max(3, up.pct) + '%"></i></div><p class="tiny">' + esc(up.text) + '</p></div>' : '';
  }
  function addMore(it) {
    var up = st.uploads[it.id];
    return '<label class="btn btn-ghost btn-sm ct-pick' + (up ? ' disabled' : '') + '">' + T('+ Another file', '+ Outro arquivo') +
      '<input type="file" accept="image/*,video/*" multiple data-ct-upload="' + esc(it.id) + '" hidden' + (up ? ' disabled' : '') + '></label>';
  }
  function btn(act, it, label, honey) {
    return '<button class="btn ' + (honey ? 'btn-honey' : 'btn-ghost') + ' btn-sm" data-act="' + act + '" data-id="' + esc(it.id) + '"' + (st.busy ? ' disabled' : '') + '>' + label + '</button>';
  }
  function details(it) {
    return (it.caption ? '<details class="ct-more"><summary>' + T('Caption', 'Legenda') + '</summary><p class="ct-cap">' + esc(it.caption) + '</p>' +
      '<button class="btn btn-ghost btn-sm" data-act="ctCopy" data-id="' + esc(it.id) + '">' + h.icon('copy') + T('Copy caption', 'Copiar legenda') + '</button></details>' : '') +
      (it.notes ? '<p class="small ct-notes">📝 ' + esc(it.notes) + '</p>' : '');
  }

  /* a video or photo they sent each other (Compartilhados and Ideias) */
  function sharedCard(it) {
    var files = it.files || [], who = sender(it), at = sentAt(it);
    var head = '<div class="ct-who">' + avatar(who) + '<div><b>' + esc(who || T('Someone', 'Alguém')) + '</b> <span class="muted">' +
      (files.length ? T('sent', 'mandou') : T('wrote', 'anotou')) + ' · ' + esc(ago(at)) + '</span></div>' +
      (isNew(it) ? '<span class="ct-new">' + T('New', 'Novo') + '</span>' : '') + '</div>';
    var acts = [];
    if (it.status === 'idea') {
      acts.push(btn('ctPromote', it, T('It’s ready', 'Ficou pronto'), true));
      acts.push('<label class="btn btn-ghost btn-sm ct-pick' + (st.uploads[it.id] ? ' disabled' : '') + '">' + T('+ Video or photo', '+ Vídeo ou foto') +
        '<input type="file" accept="image/*,video/*" multiple data-ct-upload="' + esc(it.id) + '" hidden></label>');
    } else {
      if (files.length) acts.push(btn('ctSchedule', it, h.icon('calendar') + T('Schedule', 'Agendar'), true));
      acts.push(btn('ctScheduled', it, T('Scheduled in Business Suite', 'Já agendei no Business Suite')));
      acts.push(btn('ctPosted', it, T('Posted', 'Postei')));
      if (files.length) acts.push(addMore(it));
    }
    acts.push(btn('ctEdit', it, T('Edit', 'Editar')));
    return '<article class="card ct-card ct-' + esc(it.status) + '" id="ct-' + esc(it.id) + '">' + head +
      (it.title ? '<h3>' + esc(it.title) + '</h3>' : '') +
      (files.length ? '<div class="ct-files' + (files.length === 1 ? ' one' : '') + '">' + files.map(function (f) { return fileMedia(it, f, files.length === 1); }).join('') + '</div>' : '') +
      upBar(it) + details(it) + '<div class="row sp-acts">' + acts.join('') + '</div></article>';
  }

  /* on Meta: scheduled (marked by them) or already out */
  function metaCard(it) {
    var files = it.files || [], out = it.status === 'posted';
    var nets = NETS.filter(function (n) { return it.nets && it.nets[n[0]]; }).map(function (n) {
      var done = it.posted && it.posted[n[0]];
      return '<span class="ct-net' + (done ? ' done' : '') + '">' + (done ? '✓ ' : '') + n[1] + '</span>';
    }).join('');
    var sc = it.sched && !out ? it.sched : null;
    var pending = !out && !sc && (it.source === 'meta-pending' || it.source === 'bs-manual');
    var badge = out ? '<span class="sp-pill ct-st-posted">' + T('Went out ', 'Saiu ') + esc(fullWhen(it, false)) + '</span>'
      : pending ? '<span class="sp-pill ct-st-scheduled">' + (it.date ? T('Goes out ', 'Sai ') + esc(fullWhen(it, true)) : T('Scheduled in Business Suite', 'Agendado no Business Suite')) + '</span>'
      : sc && sc.state === 'processing' ? '<span class="sp-pill ct-st-scheduled">' + T('Publishing…', 'Publicando…') + '</span>'
      : sc && sc.state === 'error' ? '<span class="sp-pill ct-st-error">' + T('Didn’t go out', 'Não saiu') + '</span>'
      : '<span class="sp-pill ct-st-scheduled">' + T('Goes out ', 'Sai ') + esc(fullWhen(it, true) || T('no date', 'sem data')) + '</span>';
    var how = sc ? (sc.state === 'error' ? '<p class="small err">' + esc(sc.err || '') + '</p>'
      : '<p class="tiny muted">' + (sc.state === 'processing' ? T('Meta is processing the video; it goes out in a few minutes.', 'O Meta está processando o vídeo; sai em alguns minutos.')
        : T('The app publishes it by itself at that time.', 'O app publica sozinho nessa hora.')) + (sc.by ? ' · ' + T('scheduled by ', 'agendado por ') + esc(sc.by) : '') + '</p>')
      : pending ? '<p class="tiny muted">' + (it.date ? T('Scheduled in Business Suite; day and time noted by you. When it goes out, the real time shows.', 'Agendado no Business Suite; dia e hora anotados por vocês. Quando sair, aparece a hora real.')
        : T('Scheduled in Business Suite. Meta doesn’t tell the time: tap “Note day and time”. When it goes out, it moves to “Already out” with the real time.', 'Agendado no Business Suite. O Meta não informa a hora: toque em “Informar dia e hora”. Quando sair, passa para “Já saiu” com a hora real.')) + '</p>'
      : !out ? '<p class="tiny muted">' + T('Scheduled in Business Suite (marked by hand).', 'Agendado no Business Suite (marcado à mão).') + '</p>' : '';
    var media = files.length ? '<div class="ct-files' + (files.length === 1 ? ' one' : '') + '">' + files.map(function (f) { return fileMedia(it, f, files.length === 1); }).join('') + '</div>' : metaMedia(it);
    var stats = it.igStats ? '<span>♥ ' + it.igStats.likes + '</span><span>💬 ' + it.igStats.comments + '</span>' : '';
    var links = (it.igLink ? '<a href="' + esc(it.igLink) + '" target="_blank" rel="noopener">Instagram ›</a>' : '') + (it.fbLink ? '<a href="' + esc(it.fbLink) + '" target="_blank" rel="noopener">Facebook ›</a>' : '');
    var acts = [];
    if (sc && sc.state === 'error') acts.push(btn('ctRetry', it, T('Try again', 'Tentar de novo'), true));
    if (sc && sc.state !== 'processing') acts.push(btn('ctUnschedule', it, T('Cancel schedule', 'Cancelar agendamento')));
    if (pending) acts.push(btn('ctWhen', it, h.icon('calendar') + (it.date ? T('Change day and time', 'Mudar dia e hora') : T('Note day and time', 'Informar dia e hora')), !it.date));
    if (!out && !sc && !pending) acts.push(btn('ctPosted', it, T('Already out', 'Já saiu')));
    if (out && it.nets && it.nets.tiktok && !(it.posted && it.posted.tiktok)) acts.push(btn('ctTiktok', it, T('Posted on TikTok', 'Postei no TikTok')));
    acts.push(btn('ctEdit', it, T('Edit', 'Editar')));
    return '<article class="card ct-card ct-' + esc(it.status) + '" id="ct-' + esc(it.id) + '">' +
      '<div class="ct-top">' + badge + (nets ? '<div class="ct-nets">' + nets + '</div>' : '') + '</div>' +
      (it.title ? '<h3>' + esc(it.title) + '</h3>' : '') + how + media +
      (stats || links ? '<p class="small ct-links">' + stats + links + '</p>' : '') +
      details(it) + '<div class="row sp-acts">' + acts.join('') + '</div></article>';
  }

  V.content = function () {
    if (!st.data && !st.loading && !st.err) { st.loading = true; load('list'); }
    if (st.seenAt === null) {                       // what was new since the last visit stays "new" during this one
      try { st.seenAt = localStorage.getItem(SEEN_KEY) || ''; } catch (e) { st.seenAt = ''; }
      setTimeout(function () { try { localStorage.setItem(SEEN_KEY, new Date().toISOString()); } catch (e) { /* private mode */ } }, 3000);
    }
    var d = st.data;
    var send = '<label class="btn btn-honey ct-send">' + h.icon('upload') + T('Send a video or photo', 'Mandar vídeo ou foto') +
      '<input type="file" accept="image/*,video/*" multiple data-ct-new hidden></label>';
    var head = '<div class="page-head"><div><p class="eyebrow">Marketing</p><h1>' + T('Content', 'Conteúdo') + '</h1>' +
      '<p class="sub">' + T('Pass videos and photos to each other in full quality, and see what is on Instagram and Facebook.',
        'Troquem vídeos e fotos na qualidade original e vejam o que já está no Instagram e no Facebook.') + '</p></div></div>' +
      '<div class="ct-actions">' + send + '<button class="btn btn-ghost" data-act="ctIdea">' + T('+ Idea', '+ Ideia') + '</button></div>';
    if (!d) { setTimeout(hydrate, 0); return { title: T('Content', 'Conteúdo'), html: '<div translate="no" class="ct">' + head + (st.err ? '<p class="err">' + esc(st.err) + '</p>' : '<div class="loading"><span>' + T('Loading…', 'Carregando…') + '</span></div>') + '</div>' }; }
    var all = d.items, t = d.today;
    var newest = function (a, b) { return String(sentAt(b)).localeCompare(String(sentAt(a))); };
    var shared = all.filter(function (i) { return i.status === 'ready' || i.status === 'todo'; }).sort(newest);
    var ideas = all.filter(function (i) { return i.status === 'idea'; }).sort(newest);
    var sched = all.filter(function (i) { return i.status === 'scheduled'; }).sort(function (a, b) { return (a.date || '9').localeCompare(b.date || '9') || String(a.time).localeCompare(String(b.time)) || String(b.pendingSince || '').localeCompare(String(a.pendingSince || '')); })
      .reverse(); // one timeline: the farthest at the top, the next to go out right above the last one that went out
    var posted = all.filter(function (i) { return i.status === 'posted'; }).sort(function (a, b) { return (b.date || '').localeCompare(a.date || '') || String(b.time).localeCompare(String(a.time)); });
    var newIn = function (arr) { return arr.filter(isNew).length; };
    var TABS = [['shared', T('Shared', 'Compartilhados'), shared.length, newIn(shared)], ['meta', T('On Meta', 'No Meta'), sched.length + posted.length, 0],
      ['ideas', T('Ideas', 'Ideias'), ideas.length, newIn(ideas)]];
    var tabs = '<div class="seg ct-tabs" role="tablist">' + TABS.map(function (x) {
      return '<button role="tab" data-act="ctTab" data-tab="' + x[0] + '"' + (x[0] === st.tab ? ' class="on" aria-selected="true"' : '') + '>' + esc(x[1]) +
        (x[2] ? ' <span class="count">' + x[2] + '</span>' : '') + (x[3] ? '<i class="ct-dotnew" title="' + T('new', 'novo') + '"></i>' : '') + '</button>';
    }).join('') + '</div>';
    var tip = '<p class="tiny muted ct-tip">' + T('Full quality on iPhone: when picking, tap Options at the top and choose Current.',
      'Qualidade máxima no iPhone: ao escolher, toque em Opções, lá em cima, e escolha Atual.') + '</p>';
    var body = '';
    var cap = st.more ? 500 : 15;
    var more = function (arr) { return arr.length > cap ? '<p><button class="btn btn-ghost" data-act="ctMore">' + T('Show all ' + arr.length, 'Mostrar todos os ' + arr.length) + '</button></p>' : ''; };
    if (st.tab === 'shared') {
      body = tip + (shared.length ? '<div class="ct-feed">' + shared.slice(0, cap).map(sharedCard).join('') + '</div>' + more(shared)
        : '<div class="ct-empty"><b>' + T('Nothing here yet.', 'Nada por aqui ainda.') + '</b><p class="muted">' + T('Tap “Send a video or photo”: the other one gets a notification and can watch and save it.', 'Toque em “Mandar vídeo ou foto”: o outro recebe um aviso e pode assistir e salvar no celular.') + '</p></div>');
    } else if (st.tab === 'ideas') {
      body = '<form class="ct-quick" data-ct-quick><input class="input" name="idea" placeholder="' + T('An idea, in a few words…', 'Uma ideia, em poucas palavras…') + '" maxlength="120" autocomplete="off">' +
        '<button class="btn btn-honey btn-sm"' + (st.busy ? ' disabled' : '') + '>' + T('Save', 'Guardar') + '</button></form>' +
        (ideas.length ? '<div class="ct-feed">' + ideas.slice(0, cap).map(sharedCard).join('') + '</div>' + more(ideas) : '<p class="muted">' + T('No ideas yet.', 'Nenhuma ideia ainda.') + '</p>');
    } else {
      var sy = d.sync || {};
      var syncLine = sy.connected === false ? T('Connect Meta on the Ads page to bring in what is posted.', 'Conecte o Meta na página Anúncios para trazer o que já saiu.')
        : sy.at ? T('Updates by itself · Instagram and Facebook checked ', 'Atualiza sozinho · Instagram e Facebook conferidos ') + '<span data-ct-ago>' + esc(ago(sy.at)) + '</span>' : '';
      var syncErr = sy.errors && Object.keys(sy.errors).length ? '<p class="tiny err">' + Object.keys(sy.errors).map(function (k) { return esc(k + ': ' + sy.errors[k]); }).join(' · ') + '</p>' : '';
      body = '<button class="btn btn-honey ct-send" data-act="ctPickSchedule">' + h.icon('calendar') + T('Schedule a post', 'Agendar post') + '</button>' +
        '<div class="ct-sync"><span class="tiny muted">' + syncLine + '</span></div>' + syncErr +
        '<h2 class="ct-h">' + T('Scheduled', 'Agendados') + (sched.length ? ' <span class="count">' + sched.length + '</span>' : '') + '</h2>' +
        (sched.length ? '<div class="ct-feed">' + sched.map(metaCard).join('') + '</div>'
          : '<p class="small muted ct-note">' + T('Nothing scheduled. Tap “Schedule a post”: you pick a video from Shared, the day and time, and the app publishes it by itself. What you schedule in Business Suite also shows up here (without the time, which Meta doesn’t give).',
            'Nada agendado. Toque em “Agendar post”: você escolhe um vídeo de Compartilhados, o dia e a hora, e o app publica sozinho. O que vocês agendarem no Business Suite também aparece aqui (sem a hora, que o Meta não informa).') + '</p>') +
        '<h2 class="ct-h">' + T('Already out', 'Já saiu') + (posted.length ? ' <span class="count">' + posted.length + '</span>' : '') + '</h2>' +
        (posted.length ? '<div class="ct-feed">' + posted.slice(0, cap).map(metaCard).join('') + '</div>' + more(posted) : '<p class="muted">' + T('Nothing yet.', 'Nada ainda.') + '</p>');
    }
    setTimeout(hydrate, 0);
    return { title: T('Content', 'Conteúdo'), html: '<div translate="no" class="ct">' + head + tabs + body + '</div>' };
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
  function onlyMedia(files) { return Array.prototype.slice.call(files || []).filter(function (f) { return /^(image|video)\//.test(f.type); }); }
  function uploadAll(id, list, then) {
    if (!list.length) { h.toast(T('Only photos and videos.', 'Só fotos e vídeos.'), true); return; }
    var i = 0;
    var next = function (r) {
      if (i >= list.length) { delete st.uploads[id]; if (then) return then(r); return load('list', null, T('Sent. The other phone got a notification.', 'Enviado. O outro celular recebeu um aviso.')); }
      var f = list[i++], path = 'content/' + id + '/' + Date.now() + '-' + safeName(f.name);
      st.uploads[id] = { pct: 0, text: T('Sending ', 'Enviando ') + (list.length > 1 ? i + '/' + list.length + ' · ' : '') + size(f.size) + '…' };
      rerender();
      return Promise.all([storage(), mediaSize(f)]).then(function (r) {
        var dims = r[1];
        return new Promise(function (resolve, reject) {
          // the file goes as it is: no resizing, no re-encoding
          var task = r[0].ref(path).put(f, { contentType: f.type, customMetadata: { name: safeName(f.name) } });
          task.on('state_changed', function (s) {
            var pct = s.totalBytes ? Math.round(s.bytesTransferred / s.totalBytes * 100) : 0;
            st.uploads[id] = { pct: pct, text: T('Sending ', 'Enviando ') + (list.length > 1 ? i + '/' + list.length + ' · ' : '') + pct + '% de ' + size(f.size) };
            var bar = document.querySelector('#ct-' + id + ' .ct-up');
            if (bar) { bar.querySelector('i').style.width = Math.max(3, pct) + '%'; bar.querySelector('p').textContent = st.uploads[id].text; }
          }, reject, function () { resolve(dims); });
        });
      }).then(function (dims) {
        return h.call('adminContent', { action: 'addFile', id: id, path: path, name: f.name, type: f.type, size: f.size, w: dims.w, h: dims.h, dur: dims.dur, quiet: !!then });
      }).then(next).catch(function (e) {
        delete st.uploads[id];
        h.toast(T('The upload stopped: ', 'O envio parou: ') + h.friendlyError(e), true);
        rerender();
      });
    };
    next();
  }
  /* the big button: pick the files, give it a name (optional), choose Shared or Ideas, and it goes */
  function sendNew(files) {
    var list = onlyMedia(files);
    if (!list.length) { h.toast(T('Only photos and videos.', 'Só fotos e vídeos.'), true); return; }
    var vids = list.filter(function (f) { return /^video\//.test(f.type); }).length;
    var what = list.length === 1 ? (vids ? T('1 video', '1 vídeo') : T('1 photo', '1 foto')) : list.length + T(' files', ' arquivos');
    ask(T('Send ', 'Mandar ') + what, field('title', T('Name (optional)', 'Nome (opcional)'), '') +
      '<div class="ct-where"><label><input type="radio" name="where" value="ready" checked> <b>' + T('Shared', 'Compartilhados') + '</b><span class="tiny muted">' + T('an edit, a take, something to post', 'uma edição, uma gravação, algo para postar') + '</span></label>' +
      '<label><input type="radio" name="where" value="idea"> <b>' + T('Ideas', 'Ideias') + '</b><span class="tiny muted">' + T('a reference, an idea to make later', 'uma referência, uma ideia para fazer depois') + '</span></label></div>' +
      area('notes', T('Message to the other one (optional)', 'Recado para o outro (opcional)'), '', 2), T('Send', 'Mandar')).then(function (v) {
      if (!v) return;
      var where = v.where === 'idea' ? 'idea' : 'ready';
      st.tab = where === 'idea' ? 'ideas' : 'shared'; st.busy = true; rerender();
      h.call('adminContent', { action: 'save', withFile: true, item: { title: v.title, kind: vids ? 'video' : 'photo', status: where, notes: v.notes, nets: {} } })
        .then(function (d) { st.data = d; st.busy = false; uploadAll(d.id, list); setTimeout(function () { var c = document.getElementById('ct-' + d.id); if (c) c.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 80); })
        .catch(function (e) { st.busy = false; h.toast(h.friendlyError(e), true); rerender(); });
    });
  }
  document.addEventListener('change', function (ev) {
    var el = ev.target;
    if (!el || !el.matches) return;
    if (el.matches('[data-ct-new]')) { var fs = el.files; if (fs && fs.length) sendNew(Array.prototype.slice.call(fs)); el.value = ''; return; }
    if (el.matches('[data-ct-upload]')) { var id = el.getAttribute('data-ct-upload'), files = el.files; if (files && files.length) uploadAll(id, onlyMedia(files)); el.value = ''; }
  });

  /* ---------- saving to the phone: the same bytes that were uploaded ---------- */
  ACT.ctSave = function (el) {
    var it = item(el.getAttribute('data-id')), path = el.getAttribute('data-path');
    var f = it && (it.files || []).find(function (x) { return x.path === path; });
    if (!f) return;
    var label = el.innerHTML;
    el.disabled = true; el.textContent = T('Preparing…', 'Preparando…');
    var reset = function () { el.disabled = false; el.innerHTML = label; };
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
  ACT.ctTab = function (el) { st.tab = el.getAttribute('data-tab'); st.more = false; h.route(); scrollTo(0, 0); };
  ACT.ctMore = function () { st.more = true; rerender(); };
  ACT.ctSync = function () { load('sync', {}, T('Up to date with Instagram and Facebook.', 'Atualizado com Instagram e Facebook.')); };
  ACT.ctTiktok = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    var nets = {}; NETS.forEach(function (n) { nets[n[0]] = !!(it.posted && it.posted[n[0]]); }); nets.tiktok = true;
    load('posted', { id: it.id, nets: nets }, T('Ticked TikTok.', 'TikTok marcado.'));
  };
  ACT.ctIdea = function () { st.tab = 'ideas'; h.route(); setTimeout(function () { var i = document.querySelector('[data-ct-quick] input'); if (i) i.focus(); }, 60); };
  ACT.ctPromote = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    load('save', { id: it.id, item: { status: 'ready' } }, T('Moved to Shared.', 'Foi para Compartilhados.')).then(function () { st.tab = 'shared'; rerender(); });
  };
  /* quick idea: a few words */
  document.addEventListener('submit', function (ev) {
    var f = ev.target;
    if (!f || !f.matches || !f.matches('[data-ct-quick]')) return;
    ev.preventDefault();
    var v = (f.idea.value || '').trim(); if (!v) return;
    load('save', { item: { title: v, kind: 'idea', status: 'idea', nets: {} } }, T('Idea saved. The other one got a notification.', 'Ideia guardada. O outro recebeu um aviso.'));
  });

  /* ---------- dialogs ---------- */
  function ask(title, inner, okText, extra) {
    return new Promise(function (resolve) {
      var dlg = document.createElement('dialog'); dlg.className = 'modal'; dlg.setAttribute('translate', 'no');
      dlg.innerHTML = '<form method="dialog" class="in"><h2>' + esc(title) + '</h2>' + inner + '<div class="row end">' + (extra || '') +
        '<button class="btn btn-ghost" value="cancel">' + T('Cancel', 'Cancelar') + '</button><button class="btn btn-honey" value="ok">' + esc(okText || 'OK') + '</button></div></form>';
      document.body.appendChild(dlg);
      dlg.addEventListener('close', function () {
        var out = null;
        if (dlg.returnValue === 'ok') {
          out = {};
          Array.prototype.forEach.call(dlg.querySelectorAll('[name]'), function (e) {
            if (e.type === 'radio') { if (e.checked) out[e.name] = e.value; }
            else if (e.type === 'file') out[e.name] = Array.prototype.slice.call(e.files || []);
            else out[e.name] = e.type === 'checkbox' ? e.checked : e.value;
          });
        }
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
  var WHERE = function () {
    return [['ready', T('Shared', 'Compartilhados')], ['idea', T('Ideas', 'Ideias')], ['scheduled', T('Scheduled in Meta', 'Agendado no Meta')], ['posted', T('Already out', 'Já saiu')]];
  };
  ACT.ctEdit = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    var status = it.status === 'todo' ? 'ready' : it.status;
    ask(T('Edit', 'Editar'), field('title', T('Name', 'Nome'), it.title) +
      select('status', T('Where it is', 'Onde está'), status, WHERE()) +
      '<div class="row">' + field('date', T('Day (if scheduled)', 'Dia (se agendado)'), it.date, 'date') + field('time', T('Time', 'Hora'), it.time, 'time') + '</div>' +
      area('caption', T('Caption', 'Legenda'), it.caption, 3) + area('notes', T('Message to the other one', 'Recado para o outro'), it.notes, 2),
      T('Save', 'Salvar'), '<button class="btn btn-ghost danger" value="delete" style="margin-right:auto">' + T('Delete', 'Apagar') + '</button>').then(function (v) {
      if (!v) return;
      if (v.__delete) {
        return h.dialog({ title: T('Delete this and its files?', 'Apagar isto e os arquivos?'), html: '<p>' + T('It is deleted for both of you.', 'Some para os dois.') + '</p>', ok: T('Delete', 'Apagar'), cancel: T('Cancel', 'Cancelar'), danger: true })
          .then(function (ok) { if (ok) load('remove', { id: it.id }, T('Deleted.', 'Apagado.')); });
      }
      load('save', { id: it.id, item: { title: v.title, status: v.status, date: v.date, time: v.time, caption: v.caption, notes: v.notes } }, T('Saved.', 'Salvo.'));
    });
  };
  /* scheduling in the app: at that time the server publishes it on Instagram / Facebook */
  ACT.ctSchedule = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    var files = it.files || [];
    var pick = files.length > 1 ? '<div class="ct-where">' + files.map(function (f, k) {
      return '<label><input type="radio" name="path" value="' + esc(f.path) + '"' + (k === files.length - 1 ? ' checked' : '') + '> <b>' + esc(String(f.name || '').replace(/\.[a-z0-9]+$/i, '')) + '</b><span class="tiny muted">' + size(f.size) + '</span></label>';
    }).join('') + '</div>' : '';
    ask(T('Schedule', 'Agendar'), '<p class="small muted">' + T('At that day and time (New York), the app publishes it by itself, in full quality, and tells you both.',
      'Nesse dia e hora (horário de Nova York), o app publica sozinho, na qualidade original, e avisa vocês dois.') + '</p>' + pick +
      '<div class="row">' + field('date', T('Day', 'Dia'), it.date && it.date >= st.data.today ? it.date : addDays(st.data.today, 1), 'date') + field('time', T('Time', 'Hora'), it.time || '19:00', 'time') + '</div>' +
      '<div class="ct-checks"><label><input type="checkbox" name="ig" checked> Instagram</label><label><input type="checkbox" name="fb" checked> Facebook</label></div>' +
      area('caption', T('Caption', 'Legenda'), it.caption, 5), T('Schedule', 'Agendar')).then(function (v) {
      if (!v) return;
      load('schedule', { id: it.id, path: v.path || (files[files.length - 1] || {}).path, date: v.date, time: v.time, caption: v.caption, nets: { instagram: !!v.ig, facebook: !!v.fb } },
        T('Scheduled. It goes out by itself.', 'Agendado. Sai sozinho na hora.')).then(function (d) { if (d) { st.tab = 'meta'; rerender(); } });
    });
  };
  /* "Agendar post" in No Meta: any video or photo from the phone (or one already in Shared), caption, day and time */
  ACT.ctPickSchedule = function () {
    var choose = '<label class="btn btn-honey ct-dlgpick">' + h.icon('upload') + '<span data-ct-picked>' + T('Choose from the phone', 'Escolher do celular') + '</span>' +
      '<input type="file" name="files" accept="image/*,video/*" data-ct-dlgfile hidden></label>';
    ask(T('Schedule a post', 'Agendar post'), choose +
      field('title', T('Name (just for you two)', 'Nome (só para vocês)'), '') +
      '<div class="row">' + field('date', T('Day', 'Dia'), addDays(st.data.today, 1), 'date') + field('time', T('Time', 'Hora'), '19:00', 'time') + '</div>' +
      '<div class="ct-checks"><label><input type="checkbox" name="ig" checked> Instagram</label><label><input type="checkbox" name="fb" checked> Facebook</label></div>' +
      area('caption', T('Caption', 'Legenda'), '', 5) +
      '<p class="tiny muted">' + T('At that day and time (New York), the app publishes it by itself, in full quality, and tells you both.', 'Nesse dia e hora (horário de Nova York), o app publica sozinho, na qualidade original, e avisa vocês dois.') + '</p>',
      T('Schedule', 'Agendar')).then(function (v) {
      if (!v) return;
      var files = onlyMedia(v.files || []);
      var nets = { instagram: !!v.ig, facebook: !!v.fb };
      var sched = function (id, path) {
        return load('schedule', { id: id, path: path, date: v.date, time: v.time, caption: v.caption, nets: nets }, T('Scheduled. It goes out by itself.', 'Agendado. Sai sozinho na hora.'))
          .then(function (d) { if (d) { st.tab = 'meta'; rerender(); } });
      };
      if (!files.length) { h.toast(T('Choose the video or photo.', 'Escolha o vídeo ou a foto.'), true); return; }
      var vid = /^video\//.test(files[0].type);
      st.tab = 'shared'; st.busy = true; rerender();
      h.call('adminContent', { action: 'save', withFile: true, item: { title: v.title, kind: vid ? 'video' : 'photo', status: 'ready', caption: v.caption, nets: {} } })
        .then(function (d) {
          st.data = d; st.busy = false;
          uploadAll(d.id, files.slice(0, 1), function () {
            var it2 = item(d.id) || {};
            h.call('adminContent', { action: 'list' }).then(function (d2) {
              st.data = d2; var f = ((item(d.id) || it2).files || [])[0];
              return sched(d.id, f && f.path);
            });
          });
          setTimeout(function () { var c = document.getElementById('ct-' + d.id); if (c) c.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 80);
        })
        .catch(function (e) { st.busy = false; h.toast(h.friendlyError(e), true); rerender(); });
    });
  };
  /* the chosen file's name shows on the button */
  document.addEventListener('change', function (ev) {
    var el = ev.target;
    if (!el || !el.matches || !el.matches('[data-ct-dlgfile]')) return;
    var f = el.files && el.files[0], span = el.parentNode.querySelector('[data-ct-picked]');
    if (span && f) span.textContent = '✓ ' + f.name + ' · ' + size(f.size);
  });
  /* Business Suite doesn't tell the time: they note it */
  ACT.ctWhen = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    ask(T('When does it go out?', 'Quando sai?'), '<p class="small muted">' + T('The day and time you picked in Business Suite.', 'O dia e a hora que vocês escolheram no Business Suite.') + '</p>' +
      '<div class="row">' + field('date', T('Day', 'Dia'), it.date || st.data.today, 'date') + field('time', T('Time', 'Hora'), it.time || '19:00', 'time') + '</div>', T('Save', 'Salvar')).then(function (v) {
      if (v) load('save', { id: it.id, item: { date: v.date, time: v.time } }, T('Saved.', 'Salvo.'));
    });
  };
  ACT.ctUnschedule = function (el) {
    var id = el.getAttribute('data-id');
    h.dialog({ title: T('Cancel this schedule?', 'Cancelar o agendamento?'), html: '<p>' + T('It goes back to Shared and doesn’t go out.', 'Ele volta para Compartilhados e não sai.') + '</p>', ok: T('Cancel schedule', 'Cancelar agendamento'), cancel: T('Keep', 'Manter'), danger: true })
      .then(function (ok) { if (ok) load('unschedule', { id: id }, T('Cancelled.', 'Cancelado.')); });
  };
  ACT.ctRetry = function (el) { load('retry', { id: el.getAttribute('data-id') }, T('Trying again…', 'Tentando de novo…')); };
  ACT.ctScheduled = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    ask(T('Scheduled in Meta', 'Agendei no Meta'), '<p class="small muted">' + T('The day and time you picked in Meta Business Suite. When it goes out, the app sees it and moves it to “Already out”.',
      'O dia e a hora que vocês escolheram no Meta Business Suite. Quando sair, o app vê e passa para “Já saiu”.') + '</p>' +
      '<div class="row">' + field('date', T('Day', 'Dia'), it.date || st.data.today, 'date') + field('time', T('Time', 'Hora'), it.time || '19:00', 'time') + '</div>' +
      '<div class="ct-checks">' + NETS.map(function (n) { return '<label><input type="checkbox" name="net_' + n[0] + '"' + (n[0] !== 'tiktok' && (!it.nets || it.nets[n[0]] !== false) ? ' checked' : '') + '> ' + n[1] + '</label>'; }).join('') + '</div>' +
      area('caption', T('Caption (optional)', 'Legenda (opcional)'), it.caption, 3), T('Save', 'Salvar')).then(function (v) {
      if (!v) return;
      var nets = { instagram: !!v.net_instagram, facebook: !!v.net_facebook, tiktok: !!v.net_tiktok };
      load('save', { id: it.id, item: { status: 'scheduled', date: v.date, time: v.time, nets: nets, caption: v.caption } }, T('On Meta. It goes out by itself.', 'No Meta. Sai sozinho.'))
        .then(function () { st.tab = 'meta'; rerender(); });
    });
  };
  ACT.ctPosted = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    ask(T('Where did it go out?', 'Onde já saiu?'), '<div class="ct-checks">' + NETS.map(function (n) {
      var on = it.posted && it.posted[n[0]] || (!it.posted || !Object.keys(it.posted).length) && n[0] !== 'tiktok';
      return '<label><input type="checkbox" name="' + n[0] + '"' + (on ? ' checked' : '') + '> ' + n[1] + '</label>';
    }).join('') + '</div>', T('Save', 'Salvar')).then(function (v) {
      if (v) load('posted', { id: it.id, nets: v }, T('Saved.', 'Salvo.')).then(function () { st.tab = 'meta'; rerender(); });
    });
  };
})();
