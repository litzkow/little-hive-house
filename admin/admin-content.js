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
  /* what was chosen for a schedule, in a line or two; after it went out, what didn't make it */
  function schedSummary(sc, out) {
    if (!sc) return '';
    var o = sc.opts || {}, n = (sc.files || []).length || 1, parts = [];
    if (out) return (sc.warns || []).length ? '<p class="small ct-warn">' + T('Heads up: ', 'Atenção: ') + esc(sc.warns.join('; ')) + '.</p>' : '';
    parts.push(sc.format === 'story' ? 'Story' : sc.format === 'reel' ? 'Reel' : n > 1 ? T('Carousel of ', 'Carrossel de ') + n : T('Photo post', 'Post de foto'));
    if (sc.format === 'reel') {
      parts.push(sc.cover && sc.offsetMs == null ? T('cover: phone photo', 'capa: foto do celular') : sc.offsetMs != null ? T('cover: moment ', 'capa: momento ') + (sc.offsetMs / 1000).toFixed(1) + 's' : T('automatic cover', 'capa automática'));
      if (o.shareToFeed === false) parts.push(T('not on the grid', 'fora do feed'));
      if (o.trial) parts.push(T('test Reel', 'Reel de teste'));
      if (o.audioName) parts.push(T('audio: ', 'áudio: ') + o.audioName);
    }
    if ((o.collaborators || []).length) parts.push(T('with ', 'com ') + o.collaborators.map(function (u) { return '@' + u; }).join(', '));
    if ((o.tags || []).length) parts.push(o.tags.length + T(' tagged', ' marcado' + (o.tags.length > 1 ? 's' : '')));
    if (o.firstComment) parts.push(T('first comment', '1º comentário'));
    if (o.commentsOff) parts.push(T('comments off', 'comentários desligados'));
    if (o.fbCaption) parts.push(T('own caption on Facebook', 'legenda própria no Facebook'));
    return '<p class="tiny ct-opts">' + parts.map(esc).join(' · ') + '</p>';
  }
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
    var opt = schedSummary(it.sched, out);
    var media = files.length ? '<div class="ct-files' + (files.length === 1 ? ' one' : '') + '">' + files.map(function (f) { return fileMedia(it, f, files.length === 1); }).join('') + '</div>' : metaMedia(it);
    var stats = it.igStats ? '<span>♥ ' + it.igStats.likes + '</span><span>💬 ' + it.igStats.comments + '</span>' : '';
    var links = (it.igLink ? '<a href="' + esc(it.igLink) + '" target="_blank" rel="noopener">Instagram ›</a>' : '') + (it.fbLink ? '<a href="' + esc(it.fbLink) + '" target="_blank" rel="noopener">Facebook ›</a>' : '');
    var acts = [];
    if (sc && sc.state === 'error') acts.push(btn('ctRetry', it, T('Try again', 'Tentar de novo'), true));
    if (sc && sc.state !== 'processing') acts.push(btn('ctReschedule', it, T('Edit schedule', 'Editar agendamento'), sc.state !== 'error'));
    if (sc && sc.state !== 'processing') acts.push(btn('ctUnschedule', it, T('Cancel schedule', 'Cancelar agendamento')));
    if (pending) acts.push(btn('ctWhen', it, h.icon('calendar') + (it.date ? T('Change day and time', 'Mudar dia e hora') : T('Note day and time', 'Informar dia e hora')), !it.date));
    if (!out && !sc && !pending) acts.push(btn('ctPosted', it, T('Already out', 'Já saiu')));
    if (out && it.nets && it.nets.tiktok && !(it.posted && it.posted.tiktok)) acts.push(btn('ctTiktok', it, T('Posted on TikTok', 'Postei no TikTok')));
    acts.push(btn('ctEdit', it, T('Edit', 'Editar')));
    return '<article class="card ct-card ct-' + esc(it.status) + '" id="ct-' + esc(it.id) + '">' +
      '<div class="ct-top">' + badge + (nets ? '<div class="ct-nets">' + nets + '</div>' : '') + '</div>' +
      (it.title ? '<h3>' + esc(it.title) + '</h3>' : '') + how + opt + media +
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
  /* ---------- scheduling: one window with what Business Suite lets you choose ----------
     Files (1 to 10; 2 or more make a carousel), Reel / Post / Story, Instagram / Facebook, day and time, caption (and
     another one for Facebook), the Reel's cover (a moment of the video or a photo from the phone), show on the feed,
     test Reel, audio name, collaborators, tagged people (tap the photo to place them), alt text, first comment,
     comments off, the Facebook video title. Location isn't there: Meta closed place search to outside apps. */
  function schedWindow(o) {
    // o: { it (a post with files, or null), files: [entry], edit: bool }; entry: { path?, file?, type, name, url? }
    return new Promise(function (resolve) {
      var it = o.it || {}, sc = (o.edit && it.sched) || {}, op = sc.opts || {};
      var S = {
        files: o.files.slice(0, 10),
        format: sc.format === 'story' ? 'story' : '',
        alts: {}, tags: (op.tags || []).map(function (t) { return { u: t.u, x: t.x, y: t.y }; }), sel: 0,
        coverMode: sc.cover && sc.offsetMs == null ? 'photo' : 'moment', offsetMs: sc.offsetMs != null ? sc.offsetMs : null,
        coverFile: null, coverBlob: null, coverChanged: false
      };
      ((sc.files) || []).forEach(function (f) { S.alts[f.path] = f.alt || ''; });
      var key = function (e) { return e.path || e.name + ':' + (e.file && e.file.size); };
      var dlg = document.createElement('dialog'); dlg.className = 'modal ct-sch'; dlg.setAttribute('translate', 'no');
      document.body.appendChild(dlg);
      var isV = function (e) { return /^video\//.test(e.type || ''); };
      var fmt = function () {
        if (S.files.length === 1 && S.format === 'story') return 'story';
        if (S.files.length === 1 && isV(S.files[0])) return 'reel';
        return 'post';
      };
      var srcOf = function (e, cb) {
        if (e.url) return cb(e.url);
        if (e.file) { e.url = URL.createObjectURL(e.file); return cb(e.url); }
        urlOf(e.path).then(function (u) { e.url = u; cb(u); }).catch(function () {});
      };
      var thumbs = function () {
        return '<div class="ct-sch-files">' + S.files.map(function (e, k) {
          return '<div class="ct-sch-file" data-k="' + k + '">' + (isV(e) ? '<video muted playsinline preload="metadata" data-sch-src="' + k + '"></video>' : '<img alt="" data-sch-src="' + k + '">') +
            '<span class="ct-sch-n">' + (k + 1) + '</span>' +
            (S.files.length > 1 ? '<button type="button" class="ct-sch-x" data-sch-del="' + k + '" aria-label="' + T('Remove', 'Tirar') + '">×</button>' : '') +
            (k > 0 ? '<button type="button" class="ct-sch-mv" data-sch-left="' + k + '" aria-label="' + T('Move left', 'Para a esquerda') + '">‹</button>' : '') + '</div>';
        }).join('') + (S.files.length < 10 && !o.edit ? '<label class="ct-sch-add">+<input type="file" accept="image/*,video/*" multiple data-sch-more hidden></label>' : '') + '</div>';
      };
      var radio = function (name, val, cur, label) { return '<label class="ct-sch-pill"><input type="radio" name="' + name + '" value="' + val + '"' + (val === cur ? ' checked' : '') + '><span>' + label + '</span></label>'; };
      var keepVals = function () {
        var v = {}; Array.prototype.forEach.call(dlg.querySelectorAll('[name]'), function (e) { v[e.name] = e.type === 'checkbox' ? e.checked : e.type === 'radio' ? (e.checked ? e.value : v[e.name]) : e.value; });
        return v;
      };
      var V = {
        date: it.date && it.date >= st.data.today && o.edit ? it.date : addDays(st.data.today, 1), time: (o.edit && it.time) || '19:00',
        ig: o.edit ? !!(sc.nets && sc.nets.instagram) : true, fb: o.edit ? !!(sc.nets && sc.nets.facebook) : true,
        caption: it.caption || '', fbOwn: !!op.fbCaption, fbCaption: op.fbCaption || '', fbTitle: op.fbTitle || '',
        feed: op.shareToFeed !== false, trial: op.trial || '', audio: op.audioName || '',
        collab: (op.collaborators || []).map(function (u) { return '@' + u; }).join(', '),
        first: op.firstComment || '', off: !!op.commentsOff, title: it.title || ''
      };
      var draw = function () {
        var f = fmt(), one = S.files.length === 1, mixedVid = S.files.length > 1 && S.files.some(isV);
        var photoFirst = S.files.filter(function (e) { return !isV(e); })[0];
        var h1 = '<form method="dialog" class="in"><h2>' + (o.edit ? T('Edit schedule', 'Editar agendamento') : T('Schedule a post', 'Agendar post')) + '</h2>' + thumbs();
        var kind = one ? '<div class="ct-sch-pills">' + (isV(S.files[0]) ? radio('format', '', S.format, 'Reel') : radio('format', '', S.format, T('Post', 'Post'))) + radio('format', 'story', S.format, 'Story') + '</div>'
          : '<p class="tiny muted">' + T('Carousel with ', 'Carrossel com ') + S.files.length + T(' items, in this order (‹ moves one to the left).', ' itens, nessa ordem (‹ passa um para a esquerda).') + '</p>';
        var nets = '<div class="ct-checks"><label><input type="checkbox" name="ig"' + (V.ig ? ' checked' : '') + '> Instagram</label><label' + (mixedVid ? ' class="muted"' : '') + '><input type="checkbox" name="fb"' + (V.fb && !mixedVid ? ' checked' : '') + (mixedVid ? ' disabled' : '') + '> Facebook</label></div>' +
          (mixedVid ? '<p class="tiny muted">' + T('Facebook doesn’t take a carousel with a video: this one goes only to Instagram.', 'O Facebook não aceita carrossel com vídeo: este vai só para o Instagram.') + '</p>' : '');
        if (!o.edit) h1 = h1.replace('<form method="dialog" class="in">', '<form method="dialog" class="in">');
        var when = '<div class="row">' + field('date', T('Day', 'Dia'), V.date, 'date') + field('time', T('Time (New York)', 'Hora (Nova York)'), V.time, 'time') + '</div>';
        var cap = f === 'story' ? '<p class="tiny muted">' + T('Stories have no caption.', 'Story não tem legenda.') + '</p>'
          : area('caption', T('Caption', 'Legenda'), V.caption, 5) +
            '<label class="ct-sch-check"><input type="checkbox" name="fbOwn"' + (V.fbOwn ? ' checked' : '') + ' data-sch-redraw> ' + T('Another caption on Facebook', 'Legenda diferente no Facebook') + '</label>' +
            (V.fbOwn ? area('fbCaption', T('Facebook caption', 'Legenda do Facebook'), V.fbCaption, 4) : '');
        if (!o.edit && !V.title) V.title = '';
        var name = o.it ? '' : field('title', T('Name (just for you two)', 'Nome (só para vocês)'), V.title);
        var cover = '', reel = '';
        if (f === 'reel') {
          cover = '<fieldset class="ct-sch-box"><legend>' + T('Cover', 'Capa') + '</legend><div class="ct-sch-pills">' + radio('coverMode', 'moment', S.coverMode, T('A moment of the video', 'Um momento do vídeo')) + radio('coverMode', 'photo', S.coverMode, T('A photo from the phone', 'Foto do celular')) + '</div>' +
            (S.coverMode === 'moment'
              ? '<div class="ct-sch-cover"><video muted playsinline preload="auto" data-sch-cv></video></div><input type="range" min="0" max="1000" step="1" value="0" data-sch-slider class="ct-sch-range"><p class="tiny muted">' + T('Slide to the moment you want as the cover.', 'Arraste até o momento que você quer de capa.') + '</p>'
              : '<div class="ct-sch-cover">' + (S.coverFile || (o.edit && sc.cover && !S.coverChanged) ? '<img alt="" data-sch-cimg>' : '<span class="muted small">' + T('No photo yet', 'Nenhuma foto ainda') + '</span>') + '</div>' +
                '<label class="btn btn-ghost btn-sm ct-dlgpick">' + h.icon('upload') + T('Choose the cover photo', 'Escolher a foto da capa') + '<input type="file" accept="image/*" data-sch-cfile hidden></label>') + '</fieldset>';
          reel = '<fieldset class="ct-sch-box"><legend>Reel</legend>' +
            '<label class="ct-sch-check"><input type="checkbox" name="feed"' + (V.feed ? ' checked' : '') + '> ' + T('Also show it on the profile grid', 'Mostrar também no feed do perfil') + '</label>' +
            select('trial', T('Test Reel (shown to non-followers first)', 'Reel de teste (aparece primeiro para quem não segue)'), V.trial, [['', T('No', 'Não')], ['MANUAL', T('Yes; I decide in Instagram when it goes to followers', 'Sim; eu decido no Instagram quando vai para os seguidores')], ['SS_PERFORMANCE', T('Yes; Instagram shares it with followers if it does well', 'Sim; o Instagram mostra aos seguidores se for bem')]]) +
            field('audio', T('Audio name (instead of “Original audio”)', 'Nome do áudio (no lugar de “Áudio original”)'), V.audio) +
            field('fbTitle', T('Video title on Facebook', 'Título do vídeo no Facebook'), V.fbTitle) + '</fieldset>';
        }
        var people = f === 'story' ? '' : '<fieldset class="ct-sch-box"><legend>' + T('People', 'Pessoas') + '</legend>' +
          field('collab', T('Collaborators (up to 3, Instagram)', 'Colaboradores (até 3, Instagram)'), V.collab) +
          '<label class="field"><span>' + T('Tag people (Instagram)', 'Marcar pessoas (Instagram)') + '</span><div class="ct-sch-tagin"><input class="input" data-sch-tag placeholder="@usuario"><button type="button" class="btn btn-ghost btn-sm" data-sch-addtag>' + T('Add', 'Adicionar') + '</button></div></label>' +
          (S.tags.length ? '<div class="ct-sch-tags">' + S.tags.map(function (t, k) { return '<span class="ct-sch-tag' + (k === S.sel ? ' on' : '') + '" data-sch-seltag="' + k + '">@' + esc(t.u) + '<button type="button" data-sch-deltag="' + k + '" aria-label="' + T('Remove', 'Tirar') + '">×</button></span>'; }).join('') + '</div>' : '') +
          (S.tags.length && photoFirst && f !== 'reel' ? '<p class="tiny muted">' + T('Tap the photo to place the chosen tag.', 'Toque na foto para pôr a marcação escolhida.') + '</p><div class="ct-sch-place" data-sch-place><img alt="">' +
            S.tags.map(function (t, k) { return '<i style="left:' + ((t.x != null ? t.x : 0.5) * 100) + '%;top:' + ((t.y != null ? t.y : 0.5) * 100) + '%"' + (k === S.sel ? ' class="on"' : '') + '>@' + esc(t.u) + '</i>'; }).join('') + '</div>' : '') + '</fieldset>';
        var alts = S.files.some(function (e) { return !isV(e); }) && f !== 'story' ? '<details class="ct-sch-box"><summary>' + T('Alt text (for screen readers)', 'Texto alternativo (para quem usa leitor de tela)') + '</summary>' +
          S.files.map(function (e, k) { return isV(e) ? '' : '<label class="field"><span>' + T('Photo ', 'Foto ') + (k + 1) + '</span><input class="input" name="alt_' + k + '" maxlength="1000" value="' + esc(S.alts[key(e)] || '') + '"></label>'; }).join('') + '</details>' : '';
        var comments = f === 'story' ? '' : '<fieldset class="ct-sch-box"><legend>' + T('Comments', 'Comentários') + '</legend>' +
          area('first', T('First comment (goes in right after it’s out)', 'Primeiro comentário (entra logo depois que sair)'), V.first, 2) +
          '<label class="ct-sch-check"><input type="checkbox" name="off"' + (V.off ? ' checked' : '') + '> ' + T('Turn comments off on Instagram', 'Desligar os comentários no Instagram') + '</label></fieldset>';
        var note = '<p class="tiny muted">' + T('Location can’t be set from the app (Meta doesn’t allow it for outside apps). At that day and time the app publishes it by itself, in full quality, and tells you both.',
          'Local não dá para pôr pelo app (o Meta não deixa apps de fora). Nesse dia e hora o app publica sozinho, na qualidade original, e avisa vocês dois.') + '</p>';
        dlg.innerHTML = h1 + kind + name + nets + when + cap + cover + reel + people + alts + comments + note +
          '<div class="row end ct-sch-foot"><button class="btn btn-ghost" value="cancel">' + T('Cancel', 'Cancelar') + '</button><button class="btn btn-honey" value="ok">' + (o.edit ? T('Save', 'Salvar') : T('Schedule', 'Agendar')) + '</button></div></form>';
        // pictures
        Array.prototype.forEach.call(dlg.querySelectorAll('[data-sch-src]'), function (el) { srcOf(S.files[+el.getAttribute('data-sch-src')], function (u) { el.src = isV(S.files[+el.getAttribute('data-sch-src')]) ? u + '#t=0.1' : u; }); });
        var pl = dlg.querySelector('[data-sch-place] img'); if (pl && photoFirst) srcOf(photoFirst, function (u) { pl.src = u; });
        var ci = dlg.querySelector('[data-sch-cimg]');
        if (ci) { if (S.coverFile) ci.src = URL.createObjectURL(S.coverFile); else urlOf(sc.cover.path).then(function (u) { ci.src = u; }).catch(function () {}); }
        var cv = dlg.querySelector('[data-sch-cv]'), sl = dlg.querySelector('[data-sch-slider]');
        if (cv) {
          srcOf(S.files[0], function (u) { cv.src = u; });
          cv.addEventListener('loadedmetadata', function () {
            var d = cv.duration || 1, t = S.offsetMs != null ? S.offsetMs / 1000 : Math.min(0.1, d);
            sl.value = String(Math.round(t / d * 1000)); cv.currentTime = t;
          });
          var primed = false;
          sl.addEventListener('input', function () {
            if (!primed) { primed = true; var pp = cv.play(); if (pp && pp.then) pp.then(function () { cv.pause(); }).catch(function () {}); }
            var d = cv.duration || 0; if (!d) return;
            var t = +sl.value / 1000 * d; cv.currentTime = t; S.offsetMs = Math.round(t * 1000); S.coverChanged = true;
          });
        }
      };
      draw();
      var sync = function () { var v = keepVals(); Object.keys(v).forEach(function (k) { if (k.indexOf('alt_') === 0) { var e = S.files[+k.slice(4)]; if (e) S.alts[key(e)] = v[k]; } else if (k !== 'format' && k !== 'coverMode') V[k] = v[k]; }); };
      var addFiles = function (list) {
        onlyMedia(list).forEach(function (f) { if (S.files.length < 10) S.files.push({ file: f, type: f.type, name: f.name }); });
      };
      dlg.addEventListener('change', function (ev) {
        var el = ev.target;
        if (el.name === 'format') { sync(); S.format = el.value; draw(); return; }
        if (el.name === 'coverMode') { sync(); S.coverMode = el.value; S.coverChanged = true; draw(); return; }
        if (el.hasAttribute('data-sch-redraw')) { sync(); draw(); return; }
        if (el.hasAttribute('data-sch-more')) { sync(); addFiles(el.files); draw(); return; }
        if (el.hasAttribute('data-sch-cfile') && el.files && el.files[0]) { sync(); S.coverFile = el.files[0]; S.coverChanged = true; draw(); }
      });
      dlg.addEventListener('click', function (ev) {
        var b = ev.target.closest('button, [data-sch-seltag], [data-sch-place]'); if (!b) return;
        if (b.hasAttribute('data-sch-del')) { ev.preventDefault(); sync(); S.files.splice(+b.getAttribute('data-sch-del'), 1); draw(); }
        else if (b.hasAttribute('data-sch-left')) { ev.preventDefault(); sync(); var k = +b.getAttribute('data-sch-left'); var x = S.files[k]; S.files[k] = S.files[k - 1]; S.files[k - 1] = x; draw(); }
        else if (b.hasAttribute('data-sch-addtag')) {
          ev.preventDefault(); sync();
          var inp = dlg.querySelector('[data-sch-tag]'), u = String(inp.value || '').trim().replace(/^@+/, '').toLowerCase();
          if (/^[a-z0-9._]{1,30}$/.test(u) && S.tags.length < 20 && !S.tags.some(function (t) { return t.u === u; })) { S.tags.push({ u: u }); S.sel = S.tags.length - 1; }
          else if (u) h.toast(T('Type an Instagram username, like @karina.', 'Digite um usuário do Instagram, tipo @karina.'), true);
          draw();
        }
        else if (b.hasAttribute('data-sch-deltag')) { ev.preventDefault(); ev.stopPropagation(); sync(); S.tags.splice(+b.getAttribute('data-sch-deltag'), 1); S.sel = 0; draw(); }
        else if (b.hasAttribute('data-sch-seltag')) { sync(); S.sel = +b.getAttribute('data-sch-seltag'); draw(); }
        else if (b.hasAttribute('data-sch-place') && S.tags[S.sel]) {
          var r = b.getBoundingClientRect(); sync();
          S.tags[S.sel].x = Math.min(1, Math.max(0, (ev.clientX - r.left) / r.width)); S.tags[S.sel].y = Math.min(1, Math.max(0, (ev.clientY - r.top) / r.height));
          draw();
        }
      });
      dlg.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' && ev.target.hasAttribute('data-sch-tag')) { ev.preventDefault(); dlg.querySelector('[data-sch-addtag]').click(); } });
      dlg.addEventListener('close', function () {
        if (dlg.returnValue !== 'ok') { dlg.remove(); return resolve(null); }
        sync();
        var f = fmt(), finish = function (blob) {
          dlg.remove();
          resolve({
            files: S.files, format: f, date: V.date, time: V.time, title: V.title,
            nets: { instagram: !!V.ig, facebook: !!V.fb && !(S.files.length > 1 && S.files.some(isV)) },
            caption: V.caption, alts: S.alts, key: key, coverBlob: blob || null,
            coverKeep: f === 'reel' && !S.coverChanged && sc.cover ? sc.cover.path : '', offsetMs: f === 'reel' && S.coverMode === 'moment' ? S.offsetMs : null,
            opts: { shareToFeed: !!V.feed, trial: V.trial || '', audioName: V.audio || '', collaborators: V.collab || '', tags: S.tags,
              firstComment: V.first || '', commentsOff: !!V.off, fbCaption: V.fbOwn ? V.fbCaption || '' : '', fbTitle: V.fbTitle || '' }
          });
        };
        if (f !== 'reel') return finish(null);
        if (S.coverMode === 'photo') return finish(S.coverFile);
        // the chosen moment becomes a picture too (Facebook takes the cover as a picture)
        var cvv = dlg.querySelector('[data-sch-cv]');
        if (!cvv || !cvv.videoWidth || S.offsetMs == null) return finish(null);
        try {
          var c = document.createElement('canvas'); c.width = cvv.videoWidth; c.height = cvv.videoHeight;
          c.getContext('2d').drawImage(cvv, 0, 0, c.width, c.height);
          c.toBlob(function (b) { finish(b); }, 'image/jpeg', 0.92);
        } catch (e) { finish(null); }      // Instagram still gets the moment; Facebook keeps its automatic cover
      });
      if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    });
  }
  /* puts the cover picture in Storage, next to the post's files (not shown as one of them) */
  function putCover(id, blob) {
    if (!blob) return Promise.resolve('');
    var path = 'content/' + id + '/' + Date.now() + '-capa.jpg';
    return storage().then(function (s) { return s.ref(path).put(blob, { contentType: 'image/jpeg', customMetadata: { name: 'capa.jpg' } }); }).then(function () { return path; });
  }
  function sendSchedule(id, v, paths) {
    var alts = {};
    v.files.forEach(function (e, k) { if (paths[k]) alts[paths[k]] = v.alts[v.key(e)] || ''; });
    return putCover(id, v.coverBlob).then(function (cover) {
      return load('schedule', { id: id, files: paths, format: v.format, date: v.date, time: v.time, caption: v.caption, nets: v.nets,
        alts: alts, cover: cover || v.coverKeep || '', offsetMs: v.offsetMs, opts: v.opts },
        T('Scheduled. It goes out by itself.', 'Agendado. Sai sozinho na hora.'));
    }).then(function (d) { if (d) { st.tab = 'meta'; rerender(); } return d; })
      .catch(function (e) { h.toast(h.friendlyError(e), true); });
  }
  /* "Agendar" on a post in Shared: its photos and videos */
  ACT.ctSchedule = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it) return;
    var files = (it.files || []).filter(function (f) { return /^(image|video)\//.test(f.type || ''); });
    schedWindow({ it: it, files: files.map(function (f) { return { path: f.path, type: f.type, name: f.name }; }) }).then(function (v) {
      if (v) sendSchedule(it.id, v, v.files.map(function (e) { return e.path; }));
    });
  };
  /* "Editar agendamento": the same window, filled in */
  ACT.ctReschedule = function (el) {
    var it = item(el.getAttribute('data-id')); if (!it || !it.sched) return;
    var all = it.files || [];
    var files = (it.sched.files && it.sched.files.length ? it.sched.files : [{ path: it.sched.path, type: it.sched.type }])
      .map(function (f) { var x = all.find(function (a) { return a.path === f.path; }) || f; return { path: x.path, type: x.type, name: x.name }; });
    schedWindow({ it: it, files: files, edit: true }).then(function (v) {
      if (v) sendSchedule(it.id, v, v.files.map(function (e) { return e.path; }));
    });
  };
  /* "Agendar post" in No Meta: photos and videos from the phone */
  ACT.ctPickSchedule = function () {
    var inp = document.createElement('input'); inp.type = 'file'; inp.accept = 'image/*,video/*'; inp.multiple = true;
    inp.addEventListener('change', function () {
      var list = onlyMedia(inp.files).slice(0, 10);
      if (!list.length) return;
      schedWindow({ it: null, files: list.map(function (f) { return { file: f, type: f.type, name: f.name }; }) }).then(function (v) {
        if (!v) return;
        var local = v.files.map(function (e) { return e.file; });
        var vid = local.some(function (f) { return /^video\//.test(f.type); });
        st.tab = 'shared'; st.busy = true; rerender();
        h.call('adminContent', { action: 'save', withFile: true, item: { title: v.title, kind: vid ? 'video' : 'photo', status: 'ready', caption: v.caption, nets: {} } })
          .then(function (d) {
            st.data = d; st.busy = false;
            uploadAll(d.id, local, function () {
              return h.call('adminContent', { action: 'list' }).then(function (d2) {
                st.data = d2; var got = ((item(d.id) || {}).files || []).map(function (f) { return f.path; });
                return sendSchedule(d.id, v, got);
              });
            });
            setTimeout(function () { var c = document.getElementById('ct-' + d.id); if (c) c.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 80);
          })
          .catch(function (e) { st.busy = false; h.toast(h.friendlyError(e), true); rerender(); });
      });
    });
    inp.click();
  };
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
