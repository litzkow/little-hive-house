/* Hive Admin service worker: lets the admin install as a phone app and open fast.
   It caches ONLY the app shell listed below (the page, its CSS and scripts, icons, manifest). Everything else, and in
   particular all order data (Firestore, Cloud Functions, customer photos in Storage), goes straight to the network and
   is never stored: cross-origin requests and anything not on the list are not even looked at.
   Network first, cache only as a fallback, so a new admin version shows up on the next open.
   It also shows the owners' notifications (Web Push from functions/push.js: new orders, messages, card holds…). */
'use strict';

var CACHE = 'hive-admin-shell-v12';
var SHELL = ['./', 'index.html', 'admin.css', 'reports.js', 'zip.js', 'admin.js', 'admin-order.js', 'admin-more.js',
  'manifest.webmanifest', 'icons/icon-192.png', 'icons/icon-512.png', 'icons/apple-touch-icon.png', '../assets/favicon.svg'];

function shellPaths() {
  var scope = (self.registration && self.registration.scope) || self.location.href;
  return SHELL.map(function (p) { return new URL(p, scope).pathname; });
}
/** The cache key for a shell request (no ?v= query), or null when the request must not be cached. */
function shellKey(request) {
  if (request.method !== 'GET') return null;
  var url = new URL(request.url);
  if (url.origin !== self.location.origin) return null;
  if (shellPaths().indexOf(url.pathname) === -1) return null;
  return url.origin + url.pathname;
}

self.addEventListener('install', function (event) {
  event.waitUntil(caches.open(CACHE).then(function (cache) {
    var scope = (self.registration && self.registration.scope) || self.location.href;
    return Promise.all(SHELL.map(function (p) {
      var url = new URL(p, scope);
      return fetch(url.href, { cache: 'no-cache' }).then(function (res) {
        if (res.ok) return cache.put(url.origin + url.pathname, res);
      }).catch(function () { /* offline while installing: it is cached on the next visit */ });
    }));
  }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (event) {
  event.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k.indexOf('hive-admin-') === 0 && k !== CACHE; })
      .map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener('fetch', function (event) {
  var key = shellKey(event.request);
  if (!key) return;                      // not part of the app shell: the browser handles it, nothing is cached
  event.respondWith(fetch(event.request).then(function (res) {
    if (res.ok && res.type === 'basic') {
      var copy = res.clone();
      caches.open(CACHE).then(function (cache) { return cache.put(key, copy); });
    }
    return res;
  }).catch(function () {
    return caches.match(key).then(function (hit) { return hit || Response.error(); });
  }));
});

/* ---------- notifications ---------- */
self.addEventListener('push', function (event) {
  var d = {};
  try { d = event.data ? event.data.json() : {}; } catch (e) { d = { body: event.data ? event.data.text() : '' }; }
  var scope = (self.registration && self.registration.scope) || self.location.href;
  var opts = {
    body: d.body || '', icon: new URL('icons/icon-192.png', scope).href, badge: new URL('icons/icon-192.png', scope).href,
    data: { url: d.url || scope }, timestamp: Date.now(),
  };
  if (d.tag) { opts.tag = d.tag; opts.renotify = true; }
  event.waitUntil(self.registration.showNotification(d.title || 'Little Hive House', opts));
});

self.addEventListener('notificationclick', function (event) {
  event.notification.close();
  var scope = (self.registration && self.registration.scope) || self.location.href;
  var target = new URL((event.notification.data && event.notification.data.url) || scope, scope).href;
  event.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function (list) {
    for (var i = 0; i < list.length; i++) {
      var c = list[i];
      if (c.url.indexOf(scope) === 0 && 'focus' in c) {
        c.postMessage({ type: 'hive-open', url: target });   /* the open app switches screens itself (index.html) */
        return c.focus();
      }
    }
    return self.clients.openWindow ? self.clients.openWindow(target) : null;
  }));
});

if (typeof module !== 'undefined') module.exports = { SHELL: SHELL, shellKey: shellKey, CACHE: CACHE };
