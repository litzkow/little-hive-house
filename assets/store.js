/* Little Hive House: the store client shared by every page (accounts, orders, favorites, callables, uploads).
   Needs firebase-config.js and site.js first. The Firebase compat SDK is loaded from gstatic only when
   window.LHH_FIREBASE has an apiKey; until then every helper says "not configured" and the site works as before.

   window.LHHStore
     configured                 true when assets/firebase-config.js is filled in
     ready()                    → Promise<{configured, user}> (loads app + auth + functions, waits for the first auth state)
     need(mod)                  → Promise<firebase>, loads 'firestore' or 'storage' on demand
     onUser(cb)                 cb(user|null) now and on every change (anonymous checkout sessions included, see isMember)
     isMember(u)                a real signed-in customer (not an anonymous checkout session)
     signIn(email, pw) / signUp({name, email, password, marketing}) / signOut() / sendReset(email)
     call(name, data)           → Promise<result data> of a callable function (region us-east1)
     myOrders() / getOrder(id)  orders of the signed-in customer, paid and later only, through the callables myOrders /
                                myOrder (customers can't read orders in Firestore: the rules keep admin fields private)
     verified(u)                the email address is confirmed (sign-up sends a "confirm your email" email)
     refreshUser()              → Promise<user>: reloads the user and token (after they tap the link in that email)
     resendVerify()             → Promise: sends the confirm-email again (callable sendVerifyEmail)
     getProfile() / saveProfile(fields)   users/{uid} (name, marketing, favorites)
     favorites.list() / has(id) / toggle(id) / onChange(cb)   localStorage, synced to users/{uid}.favorites
     ensureUser()               signs in anonymously when nobody is signed in (photo uploads at checkout)
     upload(path, blob, meta, onProgress(bytes, total)) → Promise<path>
     message(err, context)      a friendly sentence for any auth / functions / storage error
     toDate(v), base            helpers (Firestore Timestamp | {seconds} | ms | ISO → Date; site root prefix) */
(function () {
  var SDK = 'https://www.gstatic.com/firebasejs/10.14.1/firebase-';
  var REGION = 'us-east1';
  var SUPPORT = 'support@littlehivehouse.com';
  var C = window.LHH_FIREBASE || {};
  var configured = !!(C.apiKey && C.projectId);
  var me = document.querySelector('script[src*="store.js"]');
  var base = me ? me.getAttribute('src').replace(/assets\/store\.js.*$/, '') : '';

  function err(code, message) { var e = new Error(message || code); e.code = code; return e; }
  function store(k, v) { try { if (v === undefined) return JSON.parse(localStorage.getItem(k) || 'null'); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} return null; }

  /* ---------- SDK loading ---------- */
  var scripts = {};
  function script(name) {
    if (!scripts[name]) {
      scripts[name] = new Promise(function (res, rej) {
        var s = document.createElement('script');
        s.src = SDK + name + '-compat.js';
        s.onload = res;
        s.onerror = function () { delete scripts[name]; s.remove(); rej(err('sdk/load-failed')); };
        document.head.appendChild(s);
      });
    }
    return scripts[name];
  }
  var appP = null;
  function app() {
    if (!configured) return Promise.reject(err('store/not-configured'));
    if (!appP) {
      appP = script('app')
        .then(function () { return Promise.all([script('auth'), script('functions')]); })
        .then(function () { if (!firebase.apps.length) firebase.initializeApp(C); return firebase; });
      appP.catch(function () { appP = null; });
    }
    return appP;
  }
  function need(mod) { return app().then(function () { return script(mod); }).then(function () { return firebase; }); }

  /* ---------- auth ---------- */
  var user = null, known = false, subs = [], authP = null;
  function isMember(u) { return !!(u && !u.isAnonymous); }
  function notify() { subs.slice().forEach(function (cb) { try { cb(user); } catch (e) { console.error(e); } }); }
  function remember(u) {
    if (isMember(u)) store('lhh-who', { n: u.displayName || u.email || '' });
    else store('lhh-who', null);
  }
  function ready() {
    if (!configured) return Promise.resolve({ configured: false, user: null });
    if (!authP) {
      authP = app().then(function (fb) {
        return new Promise(function (res) {
          fb.auth().onAuthStateChanged(function (u) {
            var was = user && user.uid;
            user = u || null; known = true; remember(user); paintAccount();
            if (isMember(user) && was !== user.uid) syncFavorites();
            notify(); res();
          });
        });
      }).then(function () { return { configured: true, user: user }; });
      authP.catch(function () { authP = null; });
    }
    return authP;
  }
  function onUser(cb) {
    subs.push(cb);
    if (!configured) { setTimeout(function () { cb(null); }, 0); return; }
    if (known) setTimeout(function () { cb(user); }, 0);
    else ready().catch(function () { cb(null); });
  }
  function signIn(email, password) {
    return ready().then(function () { return firebase.auth().signInWithEmailAndPassword(email.trim(), password); })
      .then(function (r) { return r.user; });
  }
  function signUp(o) {
    return ready().then(function () {
      var a = firebase.auth(), cur = a.currentUser, email = o.email.trim();
      var made = (cur && cur.isAnonymous)
        /* keep the anonymous checkout session's uid, so photos uploaded as a guest stay with the new account */
        ? cur.linkWithCredential(firebase.auth.EmailAuthProvider.credential(email, o.password)).then(function (r) { return r.user; })
            .catch(function (e) { if (e && /already-in-use|requires-recent-login|provider-already-linked/.test(e.code || '')) throw e; return a.createUserWithEmailAndPassword(email, o.password).then(function (r) { return r.user; }); })
        : a.createUserWithEmailAndPassword(email, o.password).then(function (r) { return r.user; });
      return made.then(function (u) {
        return u.updateProfile({ displayName: o.name.trim() }).then(function () {
          user = a.currentUser || u; known = true; remember(user); paintAccount(); notify();
          return call('welcome', { name: o.name.trim(), marketing: !!o.marketing }).catch(function () {})
            .then(function () { return saveProfile({ name: o.name.trim().slice(0, 80), marketing: !!o.marketing }).catch(function () {}); })
            .then(function () { syncFavorites(); return user; });
        });
      });
    });
  }
  function signOut() { return ready().then(function () { return firebase.auth().signOut(); }).then(function () { remember(null); paintAccount(); }); }
  function sendReset(email) { return call('sendPasswordReset', { email: email.trim() }); }
  function ensureUser() {
    return ready().then(function () { return user || firebase.auth().signInAnonymously().then(function (r) { user = r.user; return r.user; }); });
  }

  /* ---------- callables, Firestore, Storage ---------- */
  function call(name, data) {
    return app().then(function (fb) { return fb.app().functions(REGION).httpsCallable(name)(data || {}); })
      .then(function (r) { return r && r.data; });
  }
  function signedIn() {
    return ready().then(function () { if (!isMember(user)) throw err('store/sign-in-required'); return user; });
  }
  function ms(v) { var d = toDate(v); return d ? d.getTime() : 0; }
  function myOrders() {
    return signedIn().then(function () { return call('myOrders'); }).then(function (r) {
      return ((r && r.orders) || []).filter(function (o) { return o.status && o.status !== 'pending'; })
        .sort(function (a, b) { return ms(b.paidAt || b.createdAt) - ms(a.paidAt || a.createdAt); });
    });
  }
  function getOrder(id) {
    return signedIn().then(function () { return call('myOrder', { id: id }); })
      .catch(function (e) { if (/not-found/.test(String(e && e.code))) return null; throw e; });
  }
  function verified(u) { u = u === undefined ? user : u; return !!(u && !u.isAnonymous && u.emailVerified); }
  function refreshUser() {
    return ready().then(function () {
      var u = firebase.auth().currentUser;
      if (!u || u.isAnonymous || !u.reload) return u;
      var was = u.emailVerified;
      return u.reload().then(function () {
        var now = firebase.auth().currentUser || u;
        user = now;
        /* a fresh ID token carries email_verified=true to the callables (myOrders, welcome) */
        return (!was && now.emailVerified ? now.getIdToken(true) : Promise.resolve()).then(function () { return now; });
      });
    });
  }
  function resendVerify() { return call('sendVerifyEmail'); }
  function getProfile() {
    return signedIn().then(function (u) { return need('firestore').then(function (fb) { return fb.firestore().collection('users').doc(u.uid).get(); }); })
      .then(function (d) { return d.exists ? d.data() : {}; });
  }
  function saveProfile(fields) {
    return signedIn().then(function (u) { return need('firestore').then(function (fb) { return fb.firestore().collection('users').doc(u.uid).set(fields, { merge: true }); }); });
  }
  function upload(path, blob, meta, onProgress) {
    return need('storage').then(function (fb) {
      return new Promise(function (res, rej) {
        var task = fb.storage().ref(path).put(blob, meta || {});
        task.on('state_changed', function (s) { if (onProgress) onProgress(s.bytesTransferred, s.totalBytes); }, rej, function () { res(path); });
      });
    });
  }

  /* ---------- favorites (work without an account; synced when signed in) ---------- */
  var FKEY = 'lhh-favs';
  var favs = (function () { var v = store(FKEY); return Array.isArray(v) ? v.filter(function (x) { return typeof x === 'string'; }) : []; })();
  var favSubs = [];
  function favChanged() { store(FKEY, favs); paintHearts(); favSubs.forEach(function (cb) { cb(favs.slice()); }); }
  var favorites = {
    list: function () { return favs.slice(); },
    has: function (id) { return favs.indexOf(id) !== -1; },
    toggle: function (id) {
      var i = favs.indexOf(id), on = i === -1;
      if (on) favs.unshift(id); else favs.splice(i, 1);
      favChanged();
      if (isMember(user)) saveProfile({ favorites: favs.slice(0, 500) }).catch(function () {});
      return on;
    },
    onChange: function (cb) { favSubs.push(cb); }
  };
  function syncFavorites() {
    getProfile().then(function (p) {
      var remote = Array.isArray(p.favorites) ? p.favorites : [];
      var merged = favs.concat(remote.filter(function (x) { return favs.indexOf(x) === -1; }));
      var changedLocal = merged.length !== favs.length;
      favs = merged;
      if (changedLocal) favChanged();
      if (merged.length !== remote.length) saveProfile({ favorites: merged.slice(0, 500) }).catch(function () {});
    }).catch(function () {});
  }

  var HEART = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 20.3s-7.6-4.6-9.2-9.4C1.7 7.6 3.8 4.4 7.1 4.4c2 0 3.6 1.1 4.9 2.9 1.3-1.8 2.9-2.9 4.9-2.9 3.3 0 5.4 3.2 4.3 6.5-1.6 4.8-9.2 9.4-9.2 9.4z"/></svg>';
  function addHearts(root) {
    (root || document).querySelectorAll('.product').forEach(function (card) {
      if (card.querySelector('[data-fav]')) return;
      var add = card.querySelector('[data-add]'); if (!add) return;
      var id = add.getAttribute('data-add');
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'fav'; b.setAttribute('data-fav', id);
      b.setAttribute('aria-label', 'Favorite: ' + add.getAttribute('data-name'));
      b.setAttribute('aria-pressed', String(favorites.has(id)));
      b.innerHTML = HEART;
      card.appendChild(b);
    });
  }
  function paintHearts() {
    document.querySelectorAll('[data-fav]').forEach(function (b) { b.setAttribute('aria-pressed', String(favorites.has(b.getAttribute('data-fav')))); });
    document.querySelectorAll('[data-fav-count]').forEach(function (el) { el.textContent = favs.length; });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-fav]'); if (!b) return;
    e.preventDefault();
    var id = b.getAttribute('data-fav');
    var on = favorites.toggle(id);
    var name = (b.getAttribute('aria-label') || '').replace(/^Favorite: /, '');
    if (window.LHH) LHH.toast(on ? name + ' saved to your favorites' : name + ' removed from favorites');
    if (on) { b.classList.remove('pop'); void b.offsetWidth; b.classList.add('pop'); }
  });

  /* ---------- header account icon ---------- */
  function paintAccount() {
    var who = isMember(user) ? (user.displayName || user.email || '') : (known || !configured ? '' : ((store('lhh-who') || {}).n || ''));
    document.querySelectorAll('[data-account]').forEach(function (a) {
      var ini = a.querySelector('[data-account-initial]'), icon = a.querySelector('.i-person');
      if (who) {
        ini.textContent = who.trim().charAt(0).toUpperCase() || '•';
        ini.hidden = false; if (icon) icon.style.display = 'none';
        a.classList.add('is-in');
        a.setAttribute('aria-label', 'Your account and orders (signed in as ' + who + ')');
      } else {
        ini.hidden = true; if (icon) icon.style.display = '';
        a.classList.remove('is-in');
        a.setAttribute('aria-label', configured ? 'Sign in or create an account' : 'Your account');
      }
    });
    document.querySelectorAll('[data-account-menu]').forEach(function (a) { a.textContent = who ? 'Your account and orders' : 'Sign in or create an account'; });
  }

  /* ---------- friendly errors ---------- */
  function message(e, context) {
    var code = String((e && e.code) || '').replace(/^functions\//, '');
    var M = {
      'auth/invalid-email': 'That email address doesn’t look right. Please check it and try again.',
      'auth/missing-email': 'Please enter your email address.',
      'auth/user-not-found': 'That email and password don’t match. Try again, or reset your password.',
      'auth/wrong-password': 'That email and password don’t match. Try again, or reset your password.',
      'auth/invalid-credential': 'That email and password don’t match. Try again, or reset your password.',
      'auth/invalid-login-credentials': 'That email and password don’t match. Try again, or reset your password.',
      'auth/missing-password': 'Please enter your password.',
      'auth/email-already-in-use': 'There’s already an account with that email. Sign in instead, or reset your password.',
      'auth/credential-already-in-use': 'There’s already an account with that email. Sign in instead, or reset your password.',
      'auth/weak-password': 'Please use a longer password, at least 8 characters.',
      'auth/too-many-requests': 'Too many tries in a row. Please wait a few minutes and try again.',
      'auth/user-disabled': 'This account is turned off. Email ' + SUPPORT + ' and we’ll sort it out.',
      'auth/network-request-failed': 'We couldn’t connect. Check your internet connection and try again.',
      'auth/operation-not-allowed': 'Accounts aren’t switched on yet. Please try again soon.',
      'auth/admin-restricted-operation': 'Checkout isn’t switched on yet. Please try again soon.',
      'sdk/load-failed': 'We couldn’t reach our store. Check your internet connection (or turn off a content blocker) and try again.',
      'store/not-configured': 'This part of the shop opens soon.',
      'store/sign-in-required': 'Please sign in first.',
      'storage/unauthorized': 'We couldn’t save one of your photos. Please use regular photos under 25 MB (JPG, PNG, HEIC or WebP) and try again, or email ' + SUPPORT + '.',
      'storage/canceled': 'The photo upload stopped. Please try again.',
      'storage/retry-limit-exceeded': 'Your connection dropped while uploading photos. Please try again on a steady connection.',
      'storage/quota-exceeded': 'We can’t take photo uploads right now. Please email ' + SUPPORT + ' and we’ll help.',
      'photos/missing': 'Your photos are no longer on this page. Please remove the photo pack from your cart and add your photos again.',
      'resource-exhausted': 'Too many tries in a row. Please wait a minute and try again.',
      'unavailable': 'We couldn’t reach our store just now. Check your connection and try again.',
      'deadline-exceeded': 'That took too long. Check your connection and try again.',
      'unauthenticated': 'Please sign in again and retry.',
      'permission-denied': context === 'order' ? 'This order isn’t in your account. You can still track it with the order number and email.' : 'Please sign in again and retry.'
    };
    if (M[code]) return M[code];
    /* our own functions send clear messages for invalid input (e.g. "That design is no longer available") */
    if (/^(invalid-argument|failed-precondition|not-found|already-exists|out-of-range)$/.test(code) && e.message && e.message.length < 220 && !/^(INTERNAL|internal)$/.test(e.message)) return e.message;
    if (code === 'internal' && !navigator.onLine) return M.unavailable;
    return 'Something went wrong on our side. Please try again, or email ' + SUPPORT + ' and we’ll help.';
  }

  function toDate(v) {
    if (!v) return null;
    if (typeof v.toDate === 'function') return v.toDate();
    if (typeof v === 'object' && (v.seconds != null || v._seconds != null)) return new Date((v.seconds != null ? v.seconds : v._seconds) * 1000);
    var d = new Date(v); return isNaN(d) ? null : d;
  }

  window.LHHStore = {
    configured: configured, base: base, support: SUPPORT,
    ready: ready, need: need, onUser: onUser, isMember: isMember, user: function () { return user; },
    signIn: signIn, signUp: signUp, signOut: signOut, sendReset: sendReset, ensureUser: ensureUser,
    call: call, myOrders: myOrders, getOrder: getOrder, getProfile: getProfile, saveProfile: saveProfile,
    verified: verified, refreshUser: refreshUser, resendVerify: resendVerify,
    upload: upload, favorites: favorites, addHearts: addHearts, message: message, toDate: toDate
  };

  addHearts(document);
  paintHearts();
  paintAccount();
  /* confirm who is signed in after the page has settled, so the header shows the right initial */
  if (configured) {
    var go = function () { ready().catch(function () {}); };
    if (document.readyState === 'complete') setTimeout(go, 0); else window.addEventListener('load', go);
  }
})();
