/* Fake Firebase compat SDK for browser tests. Behaviour is driven by window.__FAKE (set via addInitScript):
   { uploadMsPerMB, uploadFailAt: n (fail the nth upload), uploadFailCode, calls: {name: result|{error:code}}, callDelay } */
(function () {
  if (window.firebase && window.firebase.__fake) return;
  var F = window.__FAKE = window.__FAKE || {};
  F.log = F.log || []; F.uploads = F.uploads || []; F.callsMade = F.callsMade || [];
  var user = F.user || null, listeners = [];
  function mkUser(o) { return Object.assign({ uid: 'u-' + Math.random().toString(36).slice(2, 8), isAnonymous: true, emailVerified: false, email: null, displayName: null,
    getIdToken: function () { return Promise.resolve('tok'); }, reload: function () { return Promise.resolve(); }, updateProfile: function (p) { Object.assign(this, p); return Promise.resolve(); },
    linkWithCredential: function () { return Promise.resolve({ user: this }); } }, o || {}); }
  function emit() { listeners.forEach(function (cb) { setTimeout(function () { cb(user); }, 0); }); }
  var auth = { get currentUser() { return user; },
    onAuthStateChanged: function (cb) { listeners.push(cb); setTimeout(function () { cb(user); }, 5); return function () {}; },
    signInAnonymously: function () { user = mkUser(); F.log.push('anon'); emit(); return Promise.resolve({ user: user }); },
    signInWithEmailAndPassword: function (e) { user = mkUser({ isAnonymous: false, email: e, emailVerified: true, displayName: 'Test' }); emit(); return Promise.resolve({ user: user }); },
    createUserWithEmailAndPassword: function (e) { user = mkUser({ isAnonymous: false, email: e }); emit(); return Promise.resolve({ user: user }); },
    signOut: function () { user = null; emit(); return Promise.resolve(); } };
  var authFn = function () { return auth; };
  authFn.EmailAuthProvider = { credential: function () { return {}; } };
  var nUp = 0;
  function ref(path) {
    return { put: function (blob, meta) {
      var k = ++nUp, subs = null, total = blob.size || 1;
      F.uploads.push({ path: path, size: blob.size, type: blob.type, meta: meta, n: k, done: false });
      var rec = F.uploads[F.uploads.length - 1];
      function echo(what) { try { if (window.LHH_LOG_URL && navigator.sendBeacon) navigator.sendBeacon(window.LHH_LOG_URL, JSON.stringify({ kind: 'fake_upload', what: what, path: path, n: k, rule: String(F.uploadFailPath || '') })); } catch (e) {} }
      echo('start');
      var task = { on: function (ev, prog, err, done) {
        var ms = Math.max(30, (F.uploadMsPerMB || 20) * total / 1e6), steps = 5, i = 0;
        var tick = setInterval(function () {
          i++;
          if ((F.uploadFailAt === k || (F.uploadFailPath && new RegExp(F.uploadFailPath).test(path))) && i === 3) { echo('fail'); clearInterval(tick); var e = new Error('fail'); e.code = F.uploadFailCode || 'storage/retry-limit-exceeded'; err(e); return; }
          prog({ bytesTransferred: Math.min(total, Math.round(total * i / steps)), totalBytes: total });
          if (i >= steps) { clearInterval(tick); rec.done = true; done(); }
        }, ms / steps);
      } };
      return task;
    } };
  }
  var docs = {};
  function coll(name) { return { doc: function (id) { var key = name + '/' + id; return {
    get: function () { return Promise.resolve({ exists: !!docs[key], data: function () { return docs[key] || {}; } }); },
    set: function (v) { docs[key] = Object.assign(docs[key] || {}, v); return Promise.resolve(); } }; } }; }
  var app = { functions: function () { return { httpsCallable: function (name) { return function (data) {
    F.callsMade.push({ name: name, data: JSON.parse(JSON.stringify(data)) });
    var r = (F.calls || {})[name];
    return new Promise(function (res, rej) { setTimeout(function () {
      if (r && r.error) { var e = new Error(r.error); e.code = 'functions/' + r.error; rej(e); return; }
      if (typeof r === 'function') { try { res({ data: r(data) }); } catch (e) { rej(e); } return; }
      res({ data: r === undefined ? {} : r });
    }, F.callDelay || 50); });
  }; } }; } };
  window.firebase = { __fake: true, apps: [], initializeApp: function () { this.apps.push(app); return app; }, app: function () { return app; },
    auth: authFn, storage: function () { return { ref: ref }; }, firestore: function () { return { collection: coll }; } };
})();
