/* Little Hive House admin: a small seller dashboard (hash-routed single page).
   Reads orders, reviews, messages and subscribers straight from Firestore (the rules let admins read them) and
   changes things ONLY through the admin callables (see STORE_SPEC: adminShip, adminRefund, ...).
   Numbers come from reports.js (pure, tested); the photo ZIP from zip.js. No libraries, no build step. */
(function () {
  'use strict';
  var R = window.LHHReports, Z = window.LHHZip;
  var SDK = 'https://www.gstatic.com/firebasejs/10.14.1/';
  var REGION = 'us-east1';
  var FRAMES_URL = '../assets/frames/';
  var ART_URL = '../assets/art/';
  var FRAME_ALIASES = { classic: 'white', polaroid: 'instant', honey: 'honeycomb', scallop: 'lace', autumn: 'fall', starry: 'baby' };
  var COLLECTIONS = { 'places': 'USA Places', 'world': 'World Places', 'ink-cities': 'Ink Cities', 'city-sketches': 'City Sketches', 'fall': 'Fall',
    'halloween': 'Halloween', 'christmas': 'Christmas', 'holidays': 'Holidays & Dates', 'summer': 'Summer', 'kitchen-words': 'Kitchen Words',
    'bumper-stickers': 'Bumper Stickers', 'night-sky': 'Night Sky', 'birth-flowers': 'Birth Flowers', 'bee-kind': 'Bee Kind',
    'furry-friends': 'Furry Friends', 'brasil': 'Brasil', 'home-notes': 'Home Notes' };
  var CARRIERS = [['usps', 'USPS'], ['ups', 'UPS'], ['fedex', 'FedEx'], ['dhl', 'DHL'], ['other', 'Other']];
  var TRACK_URL = {
    usps: 'https://tools.usps.com/go/TrackConfirmAction?tLabels=',
    ups: 'https://www.ups.com/track?tracknum=',
    fedex: 'https://www.fedex.com/fedextrack/?trknbr=',
    dhl: 'https://www.dhl.com/us-en/home/tracking/tracking-express.html?submit=1&tracking-id='
  };
  /* the statuses adminSetStatus accepts by hand (refund states only come from a refund) */
  var STATUSES = [['paid', 'Paid (to fulfil)'], ['in_production', 'In production'], ['shipped', 'Shipped'], ['delivered', 'Delivered'], ['canceled', 'Canceled']];
  var STAGE_LABEL = { to_fulfil: 'To fulfil', in_production: 'In production', shipped: 'Shipped', delivered: 'Delivered', refunded: 'Refunded',
    canceled: 'Canceled', pending: 'Checkout started' };
  var TABS = [['to_fulfil', 'To fulfil'], ['in_production', 'In production'], ['shipped', 'Shipped'], ['delivered', 'Delivered'],
    ['refunded', 'Refunded'], ['abandoned', 'Abandoned'], ['all', 'All']];
  /* [field in order.emails, adminResendEmail kind, label, when it goes out] */
  var EMAIL_KINDS = [['confirmation', 'order_confirmation', 'Order confirmation', 'Sent when the payment goes through.'],
    ['shipped', 'shipped', 'Shipped, with tracking', 'Sent when you mark the order shipped.'],
    ['outForDelivery', 'out_for_delivery', 'Out for delivery', 'Sent automatically when the carrier scans it out for delivery.'],
    ['delivered', 'delivered_review', 'Delivered + review request', 'Sent when tracking says delivered, or when you mark it delivered.'],
    ['refund', 'refund', 'Refund receipt', 'Sent with every refund.']];

  var S = {
    cfg: window.LHH_FIREBASE || null, auth: null, db: null, fns: null, user: null, admin: false,
    orders: [], ordersAt: 0, settings: R.settingsWithDefaults(null), settingsLoaded: false,
    reviews: null, messages: null, quotes: null, subscribers: null, promos: null, frames: null,
    photoUrls: {}, shellReady: false,
    ui: { orders: { tab: null, q: '', range: 'any', from: '', to: '', sel: {}, limit: 50 }, reports: { month: null, scope: 'month' },
          customers: { q: '' }, subscribers: { q: '' }, reviews: 'pending', messages: 'messages' }
  };
  var charts = [];

  /* ====================================================================== helpers */
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  var MONEY = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
  function money(v) { return MONEY.format(R.num(v)); }
  function moneyShort(v) {
    v = R.num(v);
    var a = Math.abs(v), s = v < 0 ? '−$' : '$';
    if (a >= 10000) return s + (a / 1000).toFixed(a >= 100000 ? 0 : 1).replace(/\.0$/, '') + 'K';
    if (a >= 1000) return s + (a / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
    return s + (a % 1 ? a.toFixed(2) : a.toFixed(0));
  }
  function signedMoney(v) { return v < 0 ? '−' + money(-v) : money(v); }
  function pct(v) { return v == null ? '—' : (Math.round(v * 10) / 10).toFixed(1).replace(/\.0$/, '') + '%'; }
  function int(v) { return new Intl.NumberFormat('en-US').format(Math.round(R.num(v))); }
  function plural(n, one, many) { return int(n) + ' ' + (n === 1 ? one : (many || one + 's')); }
  function fmtDate(v, opts) {
    var ms = R.toMs(v); if (!ms) return '—';
    var d = new Date(ms), now = new Date();
    var o = { month: 'short', day: 'numeric' };
    if (d.getFullYear() !== now.getFullYear() || (opts && opts.year)) o.year = 'numeric';
    return d.toLocaleDateString('en-US', o);
  }
  function fmtDT(v) {
    var ms = R.toMs(v); if (!ms) return '—';
    return fmtDate(ms) + ', ' + new Date(ms).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
  }
  function ago(v) {
    var ms = R.toMs(v); if (!ms) return '';
    var s = (Date.now() - ms) / 1000;
    if (s < 60) return 'just now';
    if (s < 3600) return Math.floor(s / 60) + ' min ago';
    if (s < 86400) return Math.floor(s / 3600) + ' h ago';
    if (s < 86400 * 2) return 'yesterday';
    if (s < 86400 * 30) return Math.floor(s / 86400) + ' days ago';
    return fmtDate(ms);
  }
  function days(ms) { return Math.max(0, Math.floor((Date.now() - ms) / 86400000)); }
  function colName(slug) { return COLLECTIONS[slug] || String(slug || '').replace(/-/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); }); }
  function custName(o) { return o.name || (o.shipping && o.shipping.name) || (o.email ? o.email.split('@')[0] : 'Guest'); }
  function orderNo(o) { return o.number || ('#' + String(o.id || '').slice(0, 6).toUpperCase()); }
  function findOrder(idOrNumber) {
    return S.orders.find(function (o) { return o.id === idOrNumber; }) ||
           S.orders.find(function (o) { return (o.number || '').toLowerCase() === String(idOrNumber).toLowerCase(); });
  }
  function qs(params) {
    var p = Object.keys(params).filter(function (k) { return params[k] != null && params[k] !== ''; })
      .map(function (k) { return encodeURIComponent(k) + '=' + encodeURIComponent(params[k]); });
    return p.length ? '?' + p.join('&') : '';
  }

  var ICON = {
    home: '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5.5v-6h-5v6H4a1 1 0 0 1-1-1z"/>',
    orders: '<path d="M3 7.5 12 3l9 4.5v9L12 21l-9-4.5z"/><path d="m3 7.5 9 4.5 9-4.5M12 12v9"/>',
    customers: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.8-3.6 3.4-5.5 6.5-5.5s5.7 1.9 6.5 5.5M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14.7c1.9.7 3.1 2.4 3.5 5.3"/>',
    discounts: '<path d="M3 12.2V4a1 1 0 0 1 1-1h8.2l8.8 8.8-9.2 9.2z"/><circle cx="8" cy="8" r="1.6"/>',
    links: '<path d="M10 14a4 4 0 0 0 5.7 0l3.1-3.1a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3.1 3.1a4 4 0 0 0 5.7 5.7l1-1"/>',
    reports: '<path d="M3 21h18M6.5 17v-5M11 17V7M15.5 17v-8M20 17V4"/>',
    reviews: '<path d="m12 3 2.7 5.6 6.1.8-4.5 4.2 1.1 6.1L12 16.8l-5.4 2.9 1.1-6.1-4.5-4.2 6.1-.8z"/>',
    messages: '<path d="M4 5h16a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H9l-5 4V6a1 1 0 0 1 1-1z"/>',
    subscribers: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 7 8.5 6 8.5-6"/>',
    settings: '<path d="M4 6h9M17 6h3M4 12h3M11 12h9M4 18h11M19 18h1"/><circle cx="15" cy="6" r="2"/><circle cx="9" cy="12" r="2"/><circle cx="17" cy="18" r="2"/>',
    more: '<circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/>',
    search: '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/>',
    copy: '<rect x="8.5" y="8.5" width="11.5" height="11.5" rx="2"/><path d="M15.5 8.5V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v9.5a1 1 0 0 0 1 1h3.5"/>',
    download: '<path d="M12 4v11M7 10.5l5 5 5-5M5 20h14"/>',
    print: '<path d="M7 9V3.5h10V9M7 17H5a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2"/><path d="M7 14h10v6.5H7z"/>',
    truck: '<path d="M2.5 6h11.5v10H2.5zM14 9.5h4l3.5 3.5v3H14"/><circle cx="6.5" cy="17.5" r="1.8"/><circle cx="17.5" cy="17.5" r="1.8"/>',
    external: '<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
    right: '<path d="m9 6 6 6-6 6"/>',
    back: '<path d="m15 6-6 6 6 6"/>',
    info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
    refund: '<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>',
    moon: '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
    logout: '<path d="M15 4h4a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1h-4M10 17l5-5-5-5M15 12H3"/>',
    image: '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="m21 16-5-5-9 9"/>',
    check: '<path d="m5 12.5 4.5 4.5L19 7"/>',
    hex: '<path d="M12 2.5 20.5 7.3v9.4L12 21.5l-8.5-4.8V7.3z"/>',
    refresh: '<path d="M20 11a8 8 0 0 0-14.3-4.9L4 8M4 4v4h4M4 13a8 8 0 0 0 14.3 4.9L20 16M20 20v-4h-4"/>',
    mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 7 8.5 6 8.5-6"/>',
    menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
    close: '<path d="M6 6l12 12M18 6 6 18"/>'
  };
  function icon(name, cls) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"' +
      (cls ? ' class="' + cls + '"' : '') + '>' + (ICON[name] || '') + '</svg>';
  }
  function chip(o, mainOnly) {
    var st = R.stage(o);
    var label = STAGE_LABEL[st];
    if (st === 'pending' && R.isAbandoned(o)) label = 'Abandoned';
    var cls = st;
    if (o.status === 'partially_refunded' && !mainOnly && st !== 'refunded') {
      return '<span class="chip ' + cls + '">' + esc(label) + '</span> <span class="chip partially_refunded">Partly refunded</span>';
    }
    return '<span class="chip ' + cls + '">' + esc(label) + '</span>';
  }

  var toastTimer;
  function toast(msg, bad) {
    var t = $('#toast');
    t.textContent = msg;
    t.className = 'toast on' + (bad ? ' bad' : '');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.className = 'toast'; }, bad ? 6000 : 3200);
  }
  function friendlyError(e) {
    var code = (e && e.code) || '', msg = (e && e.message) || String(e);
    if (/permission-denied|PERMISSION_DENIED/.test(code + msg)) return 'Not allowed. This account needs admin access (Settings → Admin access).';
    if (/unauthenticated/.test(code)) return 'Your sign-in expired. Please sign in again.';
    if (/unavailable|network|Failed to fetch/i.test(code + msg)) return 'The store server could not be reached. Check your internet and try again.';
    if (/deadline-exceeded/.test(code)) return 'That took too long. Check the order before trying again — it may have worked.';
    if (/internal/.test(code) && /^internal$/i.test(msg)) return 'Something went wrong on the store server. Try again in a minute.';
    return msg.replace(/^Firebase:\s*/, '').replace(/\s*\(.*\)\.?$/, '');
  }
  function busy(btn, on, label) {
    if (!btn) return;
    if (on) { btn.dataset.label = btn.innerHTML; btn.setAttribute('aria-busy', 'true'); btn.disabled = true; btn.textContent = label || 'Working…'; }
    else { btn.removeAttribute('aria-busy'); btn.disabled = false; if (btn.dataset.label) btn.innerHTML = btn.dataset.label; }
  }
  function copyText(text) {
    var done = function () { toast('Copied'); };
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text).then(done, fallback);
    fallback();
    function fallback() {
      var ta = document.createElement('textarea'); ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(); } catch (e) { toast('Could not copy. Select the text and copy it by hand.', true); }
      ta.remove();
    }
  }
  function downloadBlob(blob, name) {
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 4000);
  }
  function downloadCSV(rows, cols, name) {
    downloadBlob(new Blob(['﻿' + R.toCSV(rows, cols)], { type: 'text/csv;charset=utf-8' }), name);
    toast('Downloaded ' + name);
  }
  function today() { var d = new Date(); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }

  /* a small promise-based dialog */
  function dialog(opts) {
    return new Promise(function (resolve) {
      var d = document.createElement('dialog');
      d.className = 'modal';
      d.innerHTML = '<form method="dialog" class="in"><h2>' + esc(opts.title) + '</h2>' + (opts.html || '') +
        '<div class="row end"><button class="btn btn-ghost" value="cancel" type="submit">' + esc(opts.cancel || 'Cancel') + '</button>' +
        (opts.ok === false ? '' : '<button class="btn ' + (opts.danger ? 'btn-danger' : 'btn-honey') + '" value="ok" type="submit">' + esc(opts.ok || 'OK') + '</button>') + '</div></form>';
      document.body.appendChild(d);
      d.addEventListener('close', function () { resolve(d.returnValue === 'ok'); d.remove(); });
      if (d.showModal) d.showModal(); else { d.setAttribute('open', ''); }
      var b = d.querySelector('button[value="' + (opts.danger ? 'cancel' : 'ok') + '"]') || d.querySelector('button');
      if (b) b.focus();
    });
  }

  /* ====================================================================== boot */
  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement('script'); s.src = src; s.onload = resolve;
      s.onerror = function () { reject(new Error('Could not load ' + src)); };
      document.head.appendChild(s);
    });
  }
  function boot() {
    applyTheme();
    if (!S.cfg || !S.cfg.apiKey) return gateNotConnected();
    ['firebase-app-compat.js', 'firebase-auth-compat.js', 'firebase-firestore-compat.js', 'firebase-functions-compat.js']
      .reduce(function (p, f) { return p.then(function () { return loadScript(SDK + f); }); }, Promise.resolve())
      .then(function () {
        var app = firebase.apps && firebase.apps.length ? firebase.app() : firebase.initializeApp(S.cfg);
        S.auth = firebase.auth(); S.db = firebase.firestore(); S.fns = app.functions(REGION);
        S.auth.onAuthStateChanged(onUser);
      })
      .catch(function (e) {
        gate('<h1>Can’t reach Firebase</h1><p>The admin needs the internet to load. Check your connection and reload the page.</p>' +
          '<p class="err">' + esc(e.message) + '</p><button class="btn btn-honey" onclick="location.reload()">Reload</button>');
      });
  }
  function onUser(user) {
    S.user = user && !user.isAnonymous ? user : null;
    S.admin = false;
    if (!S.user) return gateSignIn();
    S.user.getIdTokenResult().then(function (r) {
      S.admin = !!(r && r.claims && r.claims.admin === true);
      if (!S.admin) return gateNoAdmin();
      startApp();
    }).catch(function (e) { gateSignIn(friendlyError(e)); });
  }

  /* ====================================================================== gates (not connected / sign in / no admin) */
  function gate(inner) {
    S.shellReady = false;
    $('#app').innerHTML = '<main class="gate"><div class="box"><img class="seal" src="../assets/favicon.svg" alt="">' + inner + '</div></main>';
  }
  function gateNotConnected() {
    document.title = 'Store not connected · Hive Admin';
    gate('<p class="eyebrow">Hive Admin</p><h1>Store not connected yet</h1>' +
      '<p>This is the shop’s back office: orders, refunds, shipping, reports. It wakes up once the store is connected to Firebase.</p>' +
      '<ol><li>Follow <b>SETUP.md</b> in the website folder (about 20 minutes, one time).</li>' +
      '<li>Paste the Firebase web settings into <code>assets/firebase-config.js</code>.</li>' +
      '<li>Publish the site, come back here and sign in with your store email.</li></ol>' +
      '<a class="btn btn-ghost" href="../">Back to the shop</a>');
  }
  function gateSignIn(errMsg) {
    document.title = 'Sign in · Hive Admin';
    gate('<div><p class="eyebrow">Hive Admin</p><h1>Sign in to your shop</h1></div>' +
      '<form id="signin" class="stack" novalidate>' +
      '<label class="field"><span>Email</span><input class="input" type="email" name="email" autocomplete="username" required></label>' +
      '<label class="field"><span>Password</span><input class="input" type="password" name="password" autocomplete="current-password" required></label>' +
      '<p class="err" id="signin-err"' + (errMsg ? '' : ' hidden') + '>' + esc(errMsg || '') + '</p>' +
      '<p class="ok-msg" id="signin-ok" hidden></p>' +
      '<button class="btn btn-honey btn-block" type="submit">Sign in</button>' +
      '<button class="linkish small" type="button" id="forgot">Forgot your password?</button></form>');
    var f = $('#signin');
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var btn = f.querySelector('button[type=submit]'), err = $('#signin-err');
      err.hidden = true;
      if (!f.email.value || !f.password.value) { err.textContent = 'Type your email and password.'; err.hidden = false; return; }
      busy(btn, true, 'Signing in…');
      S.auth.signInWithEmailAndPassword(f.email.value.trim(), f.password.value).catch(function (e) {
        busy(btn, false);
        var c = e.code || '';
        err.textContent = /invalid-credential|wrong-password|user-not-found|invalid-login/.test(c) ? 'That email and password don’t match. Try again or reset your password.'
          : /too-many-requests/.test(c) ? 'Too many tries. Wait a few minutes or reset your password.'
          : /invalid-email/.test(c) ? 'That doesn’t look like an email address.' : friendlyError(e);
        err.hidden = false;
      });
    });
    $('#forgot').addEventListener('click', function () {
      var email = f.email.value.trim(), err = $('#signin-err'), ok = $('#signin-ok');
      err.hidden = true; ok.hidden = true;
      if (!email) { err.textContent = 'Type your email above first, then tap “Forgot your password?”.'; err.hidden = false; f.email.focus(); return; }
      S.fns.httpsCallable('sendPasswordReset')({ email: email })
        .catch(function () { return S.auth.sendPasswordResetEmail(email); })
        .then(function () { ok.textContent = 'If that email has an account, a reset link is on its way. Check your inbox (and spam).'; ok.hidden = false; })
        .catch(function (e) { err.textContent = friendlyError(e); err.hidden = false; });
    });
  }
  function gateNoAdmin(msg) {
    document.title = 'Admin access · Hive Admin';
    gate('<div><p class="eyebrow">Hive Admin</p><h1>One more step</h1></div>' +
      '<p>You’re signed in as <b>' + esc(S.user.email) + '</b>, but this account isn’t an admin yet.</p>' +
      '<p>If this email is one of the shop owners’ emails (the <code>ADMIN_EMAILS</code> list from SETUP.md), tap the button to turn on admin access.</p>' +
      '<p class="err" id="claim-err"' + (msg ? '' : ' hidden') + '>' + esc(msg || '') + '</p>' +
      '<button class="btn btn-honey btn-block" id="claim">Activate admin access</button>' +
      '<button class="btn btn-ghost btn-block" id="out">Sign out</button>');
    $('#out').onclick = function () { S.auth.signOut(); };
    $('#claim').onclick = function () {
      var btn = this, err = $('#claim-err');
      err.hidden = true; busy(btn, true, 'Activating…');
      S.fns.httpsCallable('claimAdmin')({})
        .then(function () { return S.user.getIdToken(true); })
        .then(function () { return S.user.getIdTokenResult(); })
        .then(function (r) {
          if (r.claims && r.claims.admin === true) { S.admin = true; toast('Admin access is on. Welcome!'); startApp(); }
          else throw new Error('The server did not turn on admin access for this email.');
        })
        .catch(function (e) {
          busy(btn, false);
          err.textContent = /permission-denied/.test(e.code || '') ?
            'This email isn’t on the admin list. Add it to ADMIN_EMAILS (see SETUP.md), redeploy, then try again.' : friendlyError(e);
          err.hidden = false;
        });
    };
  }

  /* ====================================================================== data */
  function call(name, data) {
    return S.fns.httpsCallable(name)(data || {}).then(function (r) { return r && r.data; });
  }
  function docs(snap) { return snap.docs.map(function (d) { var o = d.data() || {}; o.id = d.id; return o; }); }
  function sortOrders() { S.orders.sort(function (a, b) { return (R.orderDate(b) || R.toMs(b.createdAt)) - (R.orderDate(a) || R.toMs(a.createdAt)); }); }
  function loadOrders() {
    return S.db.collection('orders').orderBy('createdAt', 'desc').limit(5000).get().then(function (snap) {
      S.orders = docs(snap); sortOrders(); S.ordersAt = Date.now();
    });
  }
  function loadSettings() {
    return S.db.collection('settings').doc('store').get().then(function (d) {
      S.settings = R.settingsWithDefaults(d.exists ? d.data() : null); S.settingsLoaded = true;
    }).catch(function () { S.settingsLoaded = true; });
  }
  function loadCol(name, key) {
    return S.db.collection(name).limit(3000).get().then(function (snap) {
      var list = docs(snap);
      list.sort(function (a, b) { return R.toMs(b.createdAt || b.at) - R.toMs(a.createdAt || a.at); });
      S[key || name] = list;
      return list;
    });
  }
  function refreshOrder(id) {
    return S.db.collection('orders').doc(id).get().then(function (d) {
      if (!d.exists) return;
      var o = d.data(); o.id = d.id;
      var i = S.orders.findIndex(function (x) { return x.id === id; });
      if (i >= 0) S.orders[i] = o; else S.orders.unshift(o);
      sortOrders();
      return o;
    });
  }
  function loadFrames() {
    if (S.frames) return Promise.resolve(S.frames);
    return fetch(FRAMES_URL + 'frames.json').then(function (r) { return r.json(); }).then(function (list) {
      S.frames = {}; list.forEach(function (f) { S.frames[f.id] = f; }); return S.frames;
    }).catch(function () { S.frames = {}; return S.frames; });
  }

  function startApp() {
    $('#app').innerHTML = '<div class="loading"><svg class="spin" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3a9 9 0 1 0 9 9" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg><span>Counting the honey…</span></div>';
    Promise.all([loadOrders(), loadSettings(), loadFrames()]).then(function () {
      renderShell();
      route();
      /* background: badges for reviews */
      loadCol('reviews').then(updateBadges).catch(function () {});
    }).catch(function (e) {
      if (/permission/i.test((e.code || '') + e.message)) return gateNoAdmin('Firestore said no: ' + friendlyError(e) + ' Try “Activate admin access” again.');
      gate('<h1>Couldn’t load the orders</h1><p class="err">' + esc(friendlyError(e)) + '</p><button class="btn btn-honey" onclick="location.reload()">Try again</button>');
    });
  }

  /* ====================================================================== shell + router */
  var NAV = [
    ['home', 'Home', 'home'], ['orders', 'Orders', 'orders'], ['customers', 'Customers', 'customers'], ['reports', 'Reports', 'reports'],
    ['sep'], ['discounts', 'Discounts', 'discounts'], ['links', 'Payment links', 'links'], ['reviews', 'Reviews', 'reviews'],
    ['messages', 'Messages', 'messages'], ['subscribers', 'Subscribers', 'subscribers'], ['sep'], ['settings', 'Settings', 'settings']
  ];
  function navHTML() {
    return NAV.map(function (n) {
      if (n[0] === 'sep') return '<div class="sep" role="separator"></div>';
      return '<a href="#' + n[0] + '" data-nav="' + n[0] + '">' + icon(n[2]) + '<span>' + n[1] + '</span><span class="count" data-count="' + n[0] + '" hidden></span></a>';
    }).join('');
  }
  function footHTML() {
    return '<div class="side-foot"><span class="who" title="' + esc(S.user.email) + '">' + esc(S.user.email) + '</span>' +
      '<div class="row"><button type="button" data-act="theme">' + themeLabel() + '</button><button type="button" data-act="signout">Sign out</button><a href="../" target="_blank" rel="noopener">View shop</a></div></div>';
  }
  function renderShell() {
    S.shellReady = true;
    $('#app').innerHTML =
      '<div class="shell">' +
      '<aside class="side" aria-label="Admin menu"><a class="brand" href="#home"><img src="../assets/favicon.svg" alt=""><span><b>Little Hive</b><small>Shop admin</small></span></a>' +
      '<nav class="nav">' + navHTML() + '</nav>' + footHTML() + '</aside>' +
      '<header class="topbar"><img src="../assets/favicon.svg" alt=""><span class="t" id="top-title">Hive Admin</span>' +
      '<button type="button" data-act="refresh" aria-label="Refresh">' + icon('refresh') + '</button></header>' +
      '<main class="main" id="main" tabindex="-1"></main>' +
      '<nav class="tabbar" aria-label="Admin sections">' +
      ['home', 'orders', 'reports', 'messages'].map(function (k) {
        var n = NAV.find(function (x) { return x[0] === k; });
        return '<a href="#' + k + '" data-nav="' + k + '">' + icon(n[2]) + '<span>' + (k === 'messages' ? 'Inbox' : n[1]) + '</span><span class="count" data-count="' + k + '" hidden></span></a>';
      }).join('') +
      '<button type="button" data-act="drawer" data-nav="more">' + icon('more') + '<span>More</span></button></nav>' +
      '</div>';
    bindGlobal();
    updateBadges();
  }
  function updateBadges() {
    var c = { orders: S.orders.filter(function (o) { var s = R.stage(o); return s === 'to_fulfil' || s === 'in_production'; }).length,
              reviews: (S.reviews || []).filter(function (r) { return (r.status || 'pending') === 'pending'; }).length };
    $$('[data-count]').forEach(function (el) {
      var n = c[el.getAttribute('data-count')];
      el.hidden = !n; el.textContent = n > 99 ? '99+' : n || '';
    });
  }
  function parseHash() {
    var h = decodeURI(location.hash.replace(/^#\/?/, '')) || 'home';
    /* older links (emails sent before Oct 2026) use #order=<id>; the admin's own format is #order/<id> */
    var old = /^([a-z]+)=([^?&]+)(.*)$/.exec(h);
    if (old) {
      h = old[1] + '/' + old[2] + old[3];
      if (history.replaceState) history.replaceState(null, '', '#' + encodeURI(h));
    }
    var parts = h.split('?'), path = parts[0].split('/');
    return { view: path[0] || 'home', arg: path.slice(1).join('/'), q: new URLSearchParams(parts[1] || '') };
  }
  var VIEWS = {};
  function route() {
    if (!S.shellReady) return;
    charts = [];
    var r = parseHash();
    var v = VIEWS[r.view] ? r.view : 'home';
    $$('[data-nav]').forEach(function (a) {
      var k = a.getAttribute('data-nav');
      if (k === v || (v === 'order' && k === 'orders')) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
    var main = $('#main');
    var out = VIEWS[v](r) || {};
    var title = out.title || 'Hive Admin';
    document.title = title + ' · Hive Admin';
    $('#top-title').textContent = title;
    main.innerHTML = out.html || '';
    if (out.after) out.after(main, r);
    drawCharts();
    if (!out.keepScroll) window.scrollTo(0, 0);
  }

  /* ---------- delegated events ---------- */
  var ACT = {};
  function bindGlobal() {
    if (bindGlobal.done) return;
    bindGlobal.done = true;
    document.addEventListener('click', function (ev) {
      var el = ev.target.closest('[data-act]');
      if (el && ACT[el.getAttribute('data-act')]) { ACT[el.getAttribute('data-act')](el, ev); return; }
      var row = ev.target.closest('tr[data-href]');
      if (row && !ev.target.closest('a, button, input, label, select')) location.hash = row.getAttribute('data-href');
    });
    document.addEventListener('keydown', function (ev) {
      var row = ev.target.closest && ev.target.closest('tr[data-href]');
      if (row && ev.key === 'Enter' && ev.target === row) location.hash = row.getAttribute('data-href');
    });
    document.addEventListener('error', function (ev) {
      var t = ev.target;
      if (t && t.tagName === 'IMG' && t.hasAttribute('data-fallback') && !t.dataset.failed) {
        t.dataset.failed = '1';
        var span = document.createElement('span'); span.className = t.className; span.innerHTML = icon('image');
        t.replaceWith(span);
      }
    }, true);
    var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(drawCharts, 120); });
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'visible' && S.shellReady && Date.now() - S.ordersAt > 5 * 60 * 1000) ACT.refresh(null, null, true);
    });
  }
  window.addEventListener('hashchange', route);

  ACT.signout = function () { S.auth.signOut(); location.hash = ''; };
  ACT.refresh = function (el, ev, quiet) {
    var main = $('#main'); if (main) main.classList.add('skeleton');
    Promise.all([loadOrders(), loadSettings()]).then(function () {
      if (S.reviews) return loadCol('reviews');
    }).then(function () {
      updateBadges(); route(); if (!quiet) toast('Up to date');
    }).catch(function (e) { toast(friendlyError(e), true); })
      .then(function () { var m = $('#main'); if (m) m.classList.remove('skeleton'); });
  };
  ACT.copy = function (el) { copyText(el.getAttribute('data-copy') || ''); };
  ACT.drawer = function () {
    var d = document.createElement('div');
    d.className = 'drawer';
    d.innerHTML = '<div class="panel" role="dialog" aria-label="Menu"><div class="row between"><a class="brand" href="#home"><img src="../assets/favicon.svg" alt=""><span><b>Little Hive</b><small>Shop admin</small></span></a>' +
      '<button type="button" class="icon-btn" data-close aria-label="Close menu">' + icon('close') + '</button></div><nav class="nav">' + navHTML() + '</nav>' + footHTML() + '</div>';
    document.body.appendChild(d);
    var v = parseHash().view;
    $$('[data-nav]', d).forEach(function (a) { if (a.getAttribute('data-nav') === v) a.setAttribute('aria-current', 'page'); });
    updateBadges();
    var close = function () { d.remove(); };
    d.addEventListener('click', function (ev) { if (ev.target === d || ev.target.closest('[data-close]') || ev.target.closest('a[href^="#"]')) close(); });
    d.querySelector('[data-close]').focus();
  };

  /* ---------- theme ---------- */
  function themePref() { try { return localStorage.getItem('lhh-admin-theme') || 'auto'; } catch (e) { return 'auto'; } }
  function themeLabel() { return { auto: 'Theme: auto', light: 'Theme: light', dark: 'Theme: dark' }[themePref()]; }
  function applyTheme() {
    var t = themePref();
    if (t === 'auto') document.documentElement.removeAttribute('data-theme'); else document.documentElement.setAttribute('data-theme', t);
  }
  ACT.theme = function (el) {
    var next = { auto: 'light', light: 'dark', dark: 'auto' }[themePref()];
    try { localStorage.setItem('lhh-admin-theme', next); } catch (e) {}
    applyTheme();
    $$('[data-act="theme"]').forEach(function (b) { b.textContent = themeLabel(); });
    drawCharts();
  };

  /* ====================================================================== charts (inline SVG, no libraries) */
  /* spec: {el, data:[{label, tick, value, tip}], format, height, highlight} — columns grow from one baseline; negatives go down */
  function chart(id, spec) { spec.id = id; charts.push(spec); return '<div class="chart" id="' + id + '" role="img" aria-label="' + esc(spec.aria || '') + '"></div>'; }
  function niceMax(v) {
    if (v <= 0) return 0;
    var p = Math.pow(10, Math.floor(Math.log10(v))), n = v / p;
    var step = n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10;
    return step * p;
  }
  function drawCharts() {
    charts.forEach(function (c) {
      var el = document.getElementById(c.id); if (!el) return;
      var W = Math.max(260, el.clientWidth || 600), H = c.height || 220;
      var data = c.data, n = data.length;
      var max = Math.max(0, Math.max.apply(null, data.map(function (d) { return d.value; })));
      var min = Math.min(0, Math.min.apply(null, data.map(function (d) { return d.value; })));
      var top = niceMax(max), bot = min < 0 ? -niceMax(-min) : 0;
      if (top === 0 && bot === 0) top = 1;
      var fmt = c.format || moneyShort;
      var padL = Math.max(34, Math.max(fmt(top).length, fmt(bot).length) * 7 + 10), padR = 6, padT = 14, padB = 26;
      var iw = W - padL - padR, ih = H - padT - padB;
      var y = function (v) { return padT + (top - v) / (top - bot) * ih; };
      var band = iw / n, bw = Math.max(3, Math.min(24, band * 0.62));
      var s = '<svg width="' + W + '" height="' + H + '" viewBox="0 0 ' + W + ' ' + H + '">';
      var ticks = [top, top / 2, 0]; if (bot < 0) ticks.push(bot);
      ticks.forEach(function (t, k) {
        var ty = Math.round(y(t)) + .5;
        if (t !== 0 && Math.abs(y(t) - y(0)) < 16) return;   /* no label squeezed against the baseline */
        s += '<line class="' + (t === 0 ? 'base' : 'gridl') + '" x1="' + padL + '" x2="' + (W - padR) + '" y1="' + ty + '" y2="' + ty + '"/>';
        s += '<text class="axis" x="' + (padL - 8) + '" y="' + (ty + 4) + '" text-anchor="end">' + esc(fmt(t)) + '</text>';
      });
      var every = Math.max(1, Math.ceil(n / Math.floor(iw / 46)));
      data.forEach(function (d, i) {
        var cx = padL + band * i + band / 2, x = cx - bw / 2;
        var y0 = y(0), y1 = y(d.value), h = Math.abs(y1 - y0), r = Math.min(4, h, bw / 2);
        var neg = d.value < 0, path;
        if (h < 0.5) path = '';
        else if (!neg) path = 'M' + x + ',' + y0 + 'V' + (y1 + r) + 'Q' + x + ',' + y1 + ' ' + (x + r) + ',' + y1 + 'H' + (x + bw - r) + 'Q' + (x + bw) + ',' + y1 + ' ' + (x + bw) + ',' + (y1 + r) + 'V' + y0 + 'Z';
        else path = 'M' + x + ',' + y0 + 'V' + (y1 - r) + 'Q' + x + ',' + y1 + ' ' + (x + r) + ',' + y1 + 'H' + (x + bw - r) + 'Q' + (x + bw) + ',' + y1 + ' ' + (x + bw) + ',' + (y1 - r) + 'V' + y0 + 'Z';
        var dim = c.highlight != null && c.highlight !== i ? ' dim' : '';
        s += '<rect class="hit" x="' + (padL + band * i) + '" y="' + padT + '" width="' + band + '" height="' + (ih + padB) + '" tabindex="0" data-i="' + i + '" aria-label="' + esc(d.label + ': ' + fmt(d.value)) + '"/>';
        s += path ? '<path class="bar' + (neg ? ' neg' : '') + dim + '" d="' + path + '"/>' : '';
        if ((n - 1 - i) % every === 0) s += '<text class="axis" x="' + cx + '" y="' + (H - 8) + '" text-anchor="middle">' + esc(d.tick || d.label) + '</text>';
      });
      if (c.labelLast && n) {
        var last = data[n - 1];
        s += '<text class="val" x="' + (padL + band * (n - 1) + band / 2) + '" y="' + (last.value >= 0 ? y(last.value) - 6 : y(last.value) + 14) + '" text-anchor="middle">' + esc(fmt(last.value)) + '</text>';
      }
      s += '</svg>';
      el.innerHTML = s;
      var tip = $('#tip');
      var show = function (ev) {
        var i = Number(ev.target.getAttribute('data-i')), d = data[i];
        tip.innerHTML = '<b>' + esc(c.tipFormat ? c.tipFormat(d.value) : money(d.value)) + '</b>' + esc(d.tip || d.label);
        tip.hidden = false;
        var r = ev.target.getBoundingClientRect(), tw = tip.offsetWidth, th = tip.offsetHeight;
        var x = ev.clientX || (r.left + r.width / 2), yy = ev.clientY || r.top + 20;
        tip.style.left = Math.min(window.innerWidth - tw - 8, Math.max(8, x - tw / 2)) + 'px';
        tip.style.top = Math.max(8, yy - th - 14) + 'px';
      };
      var hide = function () { tip.hidden = true; };
      $$('.hit', el).forEach(function (h) {
        h.addEventListener('pointermove', show); h.addEventListener('pointerleave', hide);
        h.addEventListener('focus', show); h.addEventListener('blur', hide);
      });
    });
  }
  /* horizontal bars as plain HTML (refund reasons, top lists) */
  function hbars(rows, opts) {
    var max = Math.max.apply(null, rows.map(function (r) { return r.value; }).concat([0])) || 1;
    return '<ul class="hbars">' + rows.map(function (r) {
      return '<li><div class="hb-top"><span class="hb-l">' + (r.thumb || '') + '<span>' + esc(r.label) + (r.sub ? '<small>' + esc(r.sub) + '</small>' : '') + '</span></span>' +
        '<span class="hb-v">' + esc(r.valueText) + '</span></div><div class="hb-track"><i style="width:' + Math.max(1.5, r.value / max * 100).toFixed(1) + '%"></i></div></li>';
    }).join('') + '</ul>';
  }

  /* ====================================================================== HOME */
  VIEWS.home = function () {
    var h = R.home(S.orders);
    var hour = new Date().getHours();
    var hi = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';
    var name = (S.user.displayName || '').split(' ')[0];
    var waiting = S.orders.filter(function (o) { return R.stage(o) === 'to_fulfil'; });
    var oldest = waiting.reduce(function (a, o) { return Math.min(a, R.orderDate(o) || Date.now()); }, Date.now());
    var prod = S.orders.filter(function (o) { return R.stage(o) === 'in_production'; });
    var late = S.orders.filter(function (o) { var f = o.fulfillment || {}; return R.stage(o) === 'shipped' && R.toMs(f.shippedAt) && days(R.toMs(f.shippedAt)) >= 10; });
    var abandoned = S.orders.filter(function (o) { return R.isAbandoned(o) && days(R.toMs(o.createdAt)) <= 7; });
    var pendingReviews = (S.reviews || []).filter(function (r) { return (r.status || 'pending') === 'pending'; });
    var todo = [];
    if (waiting.length) todo.push(['#orders?tab=to_fulfil', waiting.length, plural(waiting.length, 'order') + ' to make', days(oldest) ? 'Oldest is waiting ' + plural(days(oldest), 'day') : 'All paid today', false]);
    if (prod.length) todo.push(['#orders?tab=in_production', prod.length, plural(prod.length, 'order') + ' in production', 'Ship them when they’re packed', false]);
    if (late.length) todo.push(['#orders?tab=shipped', late.length, plural(late.length, 'parcel') + ' shipped 10+ days ago', 'Check tracking and mark delivered', false]);
    if (pendingReviews.length) todo.push(['#reviews', pendingReviews.length, plural(pendingReviews.length, 'review') + ' waiting', 'Publish the good ones on the shop', false]);
    if (abandoned.length) todo.push(['#orders?tab=abandoned', abandoned.length, plural(abandoned.length, 'abandoned checkout'), 'Last 7 days, never paid', true]);
    var recent = S.orders.filter(R.isSale).slice(0, 8);
    var daily = h.daily.map(function (d) {
      var dt = new Date(d.day);
      return { value: d.total, label: dt.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }), tick: (dt.getMonth() + 1) + '/' + dt.getDate(), tip: dt.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }) + ' · ' + plural(d.orders, 'order') };
    });
    var html =
      '<div class="hello"><p class="eyebrow">' + esc(new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })) + '</p>' +
      '<h1>' + hi + (name ? ', ' + esc(name) : '') + '</h1>' +
      '<p>' + (h.toFulfil ? 'You have <b>' + plural(h.toFulfil, 'order') + '</b> to fulfil.' : 'Every order is out the door. Nice work.') + '</p></div>' +
      '<div class="tiles lead">' +
      tile('Sales today', money(h.today.total), plural(h.today.orders, 'order'), true) +
      tile('Last 7 days', money(h.week.total), plural(h.week.orders, 'order')) +
      tile('Last 30 days', money(h.month30.total), plural(h.month30.orders, 'order')) +
      '<a class="tile" href="#orders?tab=to_fulfil"><span class="label">Orders to fulfil</span><span class="value">' + int(h.toFulfil) + '</span><span class="meta">' + int(h.newToFulfil) + ' new · ' + int(h.inProduction) + ' in production</span></a>' +
      '<a class="tile" href="#reports"><span class="label">Refunds this month</span><span class="value' + (h.refundsThisMonth.total ? ' neg' : '') + '">' + money(h.refundsThisMonth.total) + '</span><span class="meta">' + plural(h.refundsThisMonth.count, 'refund') + '</span></a>' +
      '</div>' +
      '<div class="cols"><div>' +
      '<section class="card"><div class="card-head"><div><h2>Sales, last 30 days</h2><p class="sub">What customers paid each day, shipping included</p></div><a class="btn btn-ghost btn-sm" href="#reports">Reports</a></div>' +
      chart('ch-daily', { data: daily, height: 210, highlight: null, labelLast: false, aria: 'Daily sales for the last 30 days. Total ' + money(h.month30.total) }) + '</section>' +
      '<section class="card flush"><div class="card-head"><h2>Recent orders</h2><a class="btn btn-ghost btn-sm" href="#orders?tab=all">All orders</a></div>' + orderTable(recent, { compact: true }) + '</section>' +
      '</div><div>' +
      '<section class="card"><div class="card-head"><h2>Needs you</h2></div>' +
      (todo.length ? '<ul class="todo">' + todo.map(function (t) {
        return '<li><a href="' + t[0] + '"><span class="dot' + (t[4] ? ' calm' : '') + '">' + int(t[1]) + '</span><span><b>' + esc(t[2]) + '</b><span>' + esc(t[3]) + '</span></span>' + icon('right') + '</a></li>';
      }).join('') + '</ul>' : '<div class="empty">' + icon('hex') + '<b>All caught up</b>Nothing is waiting on you right now.</div>') + '</section>' +
      '<section class="card"><div class="card-head"><h2>Quick actions</h2></div><div class="stack">' +
      '<a class="btn btn-ghost" href="#links">' + icon('links') + 'Send a payment link</a>' +
      '<a class="btn btn-ghost" href="#discounts">' + icon('discounts') + 'Create a discount code</a>' +
      '<button class="btn btn-ghost" type="button" data-act="refresh">' + icon('refresh') + 'Refresh orders</button></div>' +
      '<p class="tiny faint" style="margin-top:12px">Updated ' + esc(ago(S.ordersAt)) + '</p></section>' +
      '</div></div>';
    return { title: 'Home', html: html };
  };
  function tile(label, value, meta, accent, href) {
    var tag = href ? 'a' : 'div';
    return '<' + tag + ' class="tile' + (accent ? ' accent' : '') + '"' + (href ? ' href="' + href + '"' : '') + '><span class="label">' + esc(label) + '</span><span class="value">' + value + '</span>' +
      (meta ? '<span class="meta">' + meta + '</span>' : '') + '</' + tag + '>';
  }

  /* ====================================================================== ORDERS */
  function itemsSummary(o) {
    return (o.items || []).map(function (it) {
      if (it.kind === 'design') return R.num(it.qty || 1) + '× ' + (it.title || it.id);
      if (it.kind === 'photos') return R.num(it.packSize) + '-photo pack';
      if (it.kind === 'package') return (it.title || it.id) + ' (' + R.num(it.size) + ')';
      if (it.kind === 'custom') return it.title || 'Custom order';
      return it.title || it.kind;
    }).join(', ');
  }
  function fulfilNote(o) {
    var f = o.fulfillment || {}, st = R.stage(o);
    if (st === 'shipped' || st === 'delivered') return esc(carrierName(f.carrier)) + (f.tracking ? ' · ' + esc(f.tracking) : '');
    if (st === 'to_fulfil' || st === 'in_production') { var d = days(R.orderDate(o)); return d ? 'Waiting ' + plural(d, 'day') : 'Today'; }
    return '';
  }
  function carrierName(c) { var x = CARRIERS.find(function (k) { return k[0] === c; }); return x ? x[1] : (c || ''); }
  function orderTable(list, opts) {
    opts = opts || {};
    if (!list.length) return '<div class="empty">' + icon('orders') + '<b>' + esc(opts.emptyTitle || 'No orders yet') + '</b>' + esc(opts.emptyText || 'They’ll show up here as soon as someone checks out.') + '</div>';
    var sel = opts.select ? S.ui.orders.sel : null;
    var eligible = function (o) { return R.stage(o) === 'to_fulfil'; };
    var anyEligible = sel && list.some(eligible);
    var wide = '<div class="table-wrap only-wide"><table class="t' + (opts.compact ? ' compact' : '') + '"><thead><tr>' +
      (anyEligible ? '<th class="cb"><label class="check"><input type="checkbox" data-act="selall" aria-label="Select all orders to fulfil"></label></th>' : '') +
      '<th>Order</th><th>Date</th><th>Customer</th>' + (opts.compact ? '' : '<th class="num">Magnets</th>') + '<th class="num">Total</th><th>Status</th>' + (opts.compact ? '' : '<th>Shipping</th>') + '</tr></thead><tbody>' +
      list.map(function (o) {
        var href = '#order/' + encodeURIComponent(o.id);
        return '<tr class="click' + (sel && sel[o.id] ? ' sel' : '') + '" data-href="' + href + '" tabindex="0">' +
          (anyEligible ? '<td class="cb">' + (eligible(o) ? '<label class="check"><input type="checkbox" data-act="sel" data-id="' + esc(o.id) + '"' + (sel[o.id] ? ' checked' : '') + ' aria-label="Select ' + esc(orderNo(o)) + '"></label>' : '') + '</td>' : '') +
          '<td><a class="ord" href="' + href + '">' + esc(orderNo(o)) + '</a></td>' +
          '<td class="muted">' + esc(fmtDate(R.orderDate(o) || o.createdAt)) + '</td>' +
          '<td class="who"><b>' + esc(custName(o)) + '</b><span>' + esc(o.email || '') + '</span></td>' +
          (opts.compact ? '' : '<td class="num">' + int(R.magnetsOf(o)) + '</td>') +
          '<td class="num">' + money(R.pricing(o).total) + (R.refundedTotal(o) ? '<div class="tiny neg">−' + money(R.refundedTotal(o)) + '</div>' : '') + '</td>' +
          '<td>' + chip(o) + '</td>' + (opts.compact ? '' : '<td class="small muted">' + fulfilNote(o) + '</td>') + '</tr>';
      }).join('') + '</tbody></table></div>';
    var phone = '<ul class="olist only-phone">' + list.map(function (o) {
      var href = '#order/' + encodeURIComponent(o.id);
      return '<li' + (anyEligible ? ' class="has-cb"' : '') + '>' +
        (anyEligible ? '<label class="cbx">' + (eligible(o) ? '<input type="checkbox" data-act="sel" data-id="' + esc(o.id) + '"' + (sel[o.id] ? ' checked' : '') + ' aria-label="Select ' + esc(orderNo(o)) + '">' : '') + '</label>' : '') +
        '<a href="' + href + '"><span class="top"><b>' + esc(orderNo(o)) + '</b><span>' + esc(fmtDate(R.orderDate(o) || o.createdAt)) + '</span></span>' +
        '<span class="amt">' + money(R.pricing(o).total) + '</span>' +
        '<span class="who">' + esc(custName(o)) + ' · ' + plural(R.magnetsOf(o), 'magnet') + '</span><span class="st">' + chip(o, true) + '</span></a></li>';
    }).join('') + '</ul>';
    return wide + phone;
  }
  function rangeOf(u) {
    var now = new Date(), t0 = R.startOfDay(now.getTime()), end = t0 + R.DAY;
    var back = function (n) { var d = new Date(t0); d.setDate(d.getDate() - n); return d.getTime(); };
    switch (u.range) {
      case 'today': return [t0, end];
      case '7d': return [back(6), end];
      case '30d': return [back(29), end];
      case 'month': return [new Date(now.getFullYear(), now.getMonth(), 1).getTime(), end];
      case 'lastmonth': return [new Date(now.getFullYear(), now.getMonth() - 1, 1).getTime(), new Date(now.getFullYear(), now.getMonth(), 1).getTime()];
      case 'custom':
        var f = u.from ? new Date(u.from + 'T00:00:00').getTime() : 0;
        var t = u.to ? new Date(u.to + 'T00:00:00').getTime() + R.DAY : Infinity;
        return [f, t];
      default: return [0, Infinity];
    }
  }
  function filteredOrders() {
    var u = S.ui.orders, now = Date.now();
    var q = u.q.trim().toLowerCase().replace(/^#/, '');
    var rg = rangeOf(u);
    return S.orders.filter(function (o) {
      if (!R.matchesTab(o, u.tab, now)) return false;
      var t = R.orderDate(o) || R.toMs(o.createdAt);
      if (t < rg[0] || t >= rg[1]) return false;
      if (!q) return true;
      var hay = [o.number, o.email, o.name, o.shipping && o.shipping.name, o.id, o.fulfillment && o.fulfillment.tracking,
        o.shipping && o.shipping.address && o.shipping.address.city].join(' ').toLowerCase();
      return q.split(/\s+/).every(function (w) { return hay.indexOf(w) >= 0; });
    });
  }
  VIEWS.orders = function (r) {
    var u = S.ui.orders, now = Date.now();
    var counts = {};
    TABS.forEach(function (t) { counts[t[0]] = S.orders.filter(function (o) { return R.matchesTab(o, t[0], now); }).length; });
    if (r.q.get('tab')) u.tab = r.q.get('tab');
    if (r.q.has('q')) u.q = r.q.get('q');
    if (!u.tab) u.tab = counts.to_fulfil ? 'to_fulfil' : 'all';
    var html = '<div class="page-head"><div><p class="eyebrow">Orders</p><h1>Orders</h1></div><div class="actions">' +
      '<button class="btn btn-ghost btn-sm" type="button" data-act="refresh">' + icon('refresh') + 'Refresh</button>' +
      '<button class="btn btn-ghost btn-sm" type="button" data-act="ordersCsv">' + icon('download') + 'Export CSV</button></div></div>' +
      '<nav class="tabs" aria-label="Order status">' + TABS.map(function (t) {
        return '<a href="#orders?tab=' + t[0] + '"' + (u.tab === t[0] ? ' aria-current="true"' : '') + '>' + t[1] + '<span class="n">' + int(counts[t[0]]) + '</span></a>';
      }).join('') + '</nav>' +
      '<div class="filters"><label class="search"><span class="sr">Search orders</span>' + icon('search') +
      '<input class="input" type="search" id="o-q" placeholder="Search by order number, email or name" value="' + esc(u.q) + '" autocomplete="off"></label>' +
      '<label><span class="sr">Date</span><select class="input" id="o-range">' +
      [['any', 'Any date'], ['today', 'Today'], ['7d', 'Last 7 days'], ['30d', 'Last 30 days'], ['month', 'This month'], ['lastmonth', 'Last month'], ['custom', 'Custom dates…']]
        .map(function (x) { return '<option value="' + x[0] + '"' + (u.range === x[0] ? ' selected' : '') + '>' + x[1] + '</option>'; }).join('') + '</select></label>' +
      '<div class="dates" id="o-dates"' + (u.range === 'custom' ? '' : ' hidden') + '><input class="input" type="date" id="o-from" value="' + esc(u.from) + '" aria-label="From"><span class="muted">to</span><input class="input" type="date" id="o-to" value="' + esc(u.to) + '" aria-label="To"></div></div>' +
      '<div id="o-bulk"></div><section class="card flush" id="o-list"></section>';
    return {
      title: 'Orders', html: html, after: function (main) {
        renderOrderList();
        var t; $('#o-q').addEventListener('input', function () { clearTimeout(t); var v = this.value; t = setTimeout(function () { u.q = v; u.limit = 50; renderOrderList(); }, 120); });
        $('#o-range').addEventListener('change', function () { u.range = this.value; $('#o-dates').hidden = u.range !== 'custom'; renderOrderList(); });
        $('#o-from').addEventListener('change', function () { u.from = this.value; renderOrderList(); });
        $('#o-to').addEventListener('change', function () { u.to = this.value; renderOrderList(); });
      }
    };
  };
  function renderOrderList() {
    if (!$('#o-list')) return;   /* a late keystroke after leaving the page */
    var u = S.ui.orders, list = filteredOrders();
    var shown = list.slice(0, u.limit);
    var tabName = (TABS.find(function (t) { return t[0] === u.tab; }) || [0, 'orders'])[1];
    var empty = u.q || u.range !== 'any' ? { emptyTitle: 'No matches', emptyText: 'Try another search or date.' }
      : u.tab === 'to_fulfil' ? { emptyTitle: 'Nothing to fulfil', emptyText: 'Every paid order is in production or on its way.' }
      : { emptyTitle: 'Nothing here', emptyText: 'No orders are “' + tabName + '” right now.' };
    $('#o-list').innerHTML = orderTable(shown, Object.assign({ select: true }, empty)) +
      (list.length > shown.length ? '<div class="more"><button class="btn btn-ghost btn-sm" data-act="moreOrders">Show more (' + int(list.length - shown.length) + ' left)</button></div>' : '') +
      (list.length ? '<p class="tiny faint" style="padding:0 20px 14px">' + plural(list.length, 'order') + ' · ' + money(list.reduce(function (a, o) { return a + R.pricing(o).total; }, 0)) + '</p>' : '');
    renderBulk();
  }
  function renderBulk() {
    var ids = Object.keys(S.ui.orders.sel).filter(function (k) { return S.ui.orders.sel[k]; });
    var b = $('#o-bulk'); if (!b) return;
    b.innerHTML = ids.length ? '<div class="bulk"><b>' + plural(ids.length, 'order') + ' selected</b><button class="btn btn-sm" data-act="bulkProd">Mark in production</button><button class="linkish" data-act="selnone">Clear</button></div>' : '';
  }
  ACT.moreOrders = function () { S.ui.orders.limit += 100; renderOrderList(); };
  ACT.sel = function (el, ev) { ev.stopPropagation(); S.ui.orders.sel[el.getAttribute('data-id')] = el.checked; var tr = el.closest('tr'); if (tr) tr.classList.toggle('sel', el.checked); renderBulk(); };
  ACT.selall = function (el) {
    filteredOrders().slice(0, S.ui.orders.limit).forEach(function (o) { if (R.stage(o) === 'to_fulfil') S.ui.orders.sel[o.id] = el.checked; });
    renderOrderList(); var a = $('[data-act="selall"]'); if (a) a.checked = el.checked;
  };
  ACT.selnone = function () { S.ui.orders.sel = {}; renderOrderList(); };
  ACT.bulkProd = function (el) {
    var ids = Object.keys(S.ui.orders.sel).filter(function (k) { return S.ui.orders.sel[k]; });
    dialog({ title: 'Start production?', html: '<p>Mark <b>' + plural(ids.length, 'order') + '</b> as <b>In production</b>. Customers aren’t emailed; this just helps you keep track.</p>', ok: 'Mark in production' }).then(function (ok) {
      if (!ok) return;
      busy(el, true, 'Updating 0/' + ids.length + '…');
      var done = 0, failed = 0;
      ids.reduce(function (p, id) {
        return p.then(function () {
          return call('adminSetStatus', { orderId: id, status: 'in_production', note: 'Bulk: started production' })
            .then(function () { return refreshOrder(id); })
            .catch(function () { failed++; })
            .then(function () { done++; el.textContent = 'Updating ' + done + '/' + ids.length + '…'; });
        });
      }, Promise.resolve()).then(function () {
        S.ui.orders.sel = {};
        updateBadges();
        toast(failed ? (ids.length - failed) + ' updated, ' + failed + ' failed. Try those again.' : plural(ids.length, 'order') + ' moved to In production', !!failed);
        route();
      });
    });
  };
  ACT.ordersCsv = function () {
    var list = filteredOrders();
    var a = function (o) { return (o.shipping && o.shipping.address) || {}; };
    downloadCSV(list, [
      ['Order', function (o) { return orderNo(o); }], ['Date', function (o) { return new Date(R.orderDate(o) || R.toMs(o.createdAt)).toISOString().slice(0, 10); }],
      ['Status', 'status'], ['Stage', function (o) { return STAGE_LABEL[R.stage(o)]; }], ['Email', 'email'], ['Name', function (o) { return custName(o); }],
      ['Items', itemsSummary], ['Magnets', function (o) { return R.magnetsOf(o); }],
      ['Subtotal', function (o) { return R.pricing(o).subtotal; }], ['Discounts', function (o) { return R.pricing(o).discounts; }],
      ['Promo code', function (o) { return o.pricing && o.pricing.promo ? o.pricing.promo.code : ''; }],
      ['Shipping', function (o) { return R.pricing(o).shipping; }], ['Total', function (o) { return R.pricing(o).total; }],
      ['Refunded', function (o) { return R.refundedTotal(o); }], ['Stripe fee', function (o) { return R.stripeFee(o, S.settings).amount; }],
      ['Carrier', function (o) { return carrierName((o.fulfillment || {}).carrier); }], ['Tracking', function (o) { return (o.fulfillment || {}).tracking || ''; }],
      ['Label cost', function (o) { return (o.fulfillment || {}).labelCost; }],
      ['City', function (o) { return a(o).city; }], ['State', function (o) { return a(o).state; }], ['ZIP', function (o) { return a(o).postal_code; }], ['Country', function (o) { return a(o).country; }]
    ], 'orders-' + S.ui.orders.tab + '-' + today() + '.csv');
  };

  window.LHHAdmin = { parseHash: parseHash, S: S, VIEWS: VIEWS, ACT: ACT, R: R, h: { esc: esc, money: money, moneyShort: moneyShort, signedMoney: signedMoney, pct: pct, int: int, plural: plural,
    fmtDate: fmtDate, fmtDT: fmtDT, ago: ago, days: days, colName: colName, custName: custName, orderNo: orderNo, findOrder: findOrder, qs: qs, icon: icon, chip: chip,
    toast: toast, friendlyError: friendlyError, busy: busy, copyText: copyText, downloadBlob: downloadBlob, downloadCSV: downloadCSV, today: today, dialog: dialog,
    call: call, refreshOrder: refreshOrder, loadOrders: loadOrders, loadCol: loadCol, loadSettings: loadSettings, loadFrames: loadFrames, chart: chart, hbars: hbars, tile: tile,
    orderTable: orderTable, itemsSummary: itemsSummary, carrierName: carrierName, updateBadges: updateBadges, route: route,
    CARRIERS: CARRIERS, TRACK_URL: TRACK_URL, STATUSES: STATUSES, STAGE_LABEL: STAGE_LABEL, EMAIL_KINDS: EMAIL_KINDS, FRAMES_URL: FRAMES_URL, ART_URL: ART_URL,
    FRAME_ALIASES: FRAME_ALIASES, Z: Z } };
  /* the other views live in admin-order.js and admin-more.js; boot once they're loaded */
  var booted = false;
  function bootOnce() { if (!booted) { booted = true; boot(); } }
  if (document.readyState === 'loading') window.addEventListener('DOMContentLoaded', bootOnce); else setTimeout(bootOnce, 0);
})();
