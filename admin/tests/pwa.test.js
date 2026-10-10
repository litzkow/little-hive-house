/* Run: node --test admin/tests/ — the installable admin: manifest, icons and a service worker that caches only the app shell. */
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ADMIN = path.join(__dirname, '..');
const read = (p) => fs.readFileSync(path.join(ADMIN, p), 'utf8');

function pngSize(file) {
  const b = fs.readFileSync(path.join(ADMIN, file));
  assert.equal(b.toString('ascii', 1, 4), 'PNG', `${file} is a PNG`);
  return [b.readUInt32BE(16), b.readUInt32BE(20)];
}

test('manifest: Hive Admin, standalone, start_url ./, theme colour, 192 + 512 icons that exist', () => {
  const m = JSON.parse(read('manifest.webmanifest'));
  assert.equal(m.name, 'Hive Admin');
  assert.equal(m.start_url, './');
  assert.equal(m.scope, './');
  assert.equal(m.display, 'standalone');
  assert.match(m.theme_color, /^#[0-9A-F]{6}$/i);
  assert.match(m.background_color, /^#[0-9A-F]{6}$/i);
  const sizes = m.icons.map((i) => i.sizes).sort();
  assert.deepEqual(sizes, ['192x192', '512x512']);
  for (const icon of m.icons) {
    const [w, h] = pngSize(icon.src);
    assert.equal(`${w}x${h}`, icon.sizes, icon.src);
    assert.equal(icon.type, 'image/png');
    assert.match(icon.purpose, /maskable/);
  }
  assert.deepEqual(pngSize('icons/apple-touch-icon.png'), [180, 180]);
});

test('index.html links the manifest, the iPhone icon and registers sw.js', () => {
  const html = read('index.html');
  assert.match(html, /<link rel="manifest" href="manifest\.webmanifest">/);
  assert.match(html, /<link rel="apple-touch-icon" href="icons\/apple-touch-icon\.png">/);
  assert.match(html, /<meta name="theme-color" content="#2B2118">/);
  assert.match(html, /serviceWorker\.register\('sw\.js'\)/);
  assert.match(html, /noindex/);
});

/* Loads sw.js in a sandbox with fake caches/fetch and returns its event handlers. */
function loadSW() {
  const handlers = {};
  const store = new Map();
  const fetched = [];
  const caches = {
    open: async () => ({ put: async (k, v) => { store.set(String(k), v); } }),
    keys: async () => ['hive-admin-shell-v0', 'hive-admin-shell-v1', 'someone-else'],
    delete: async (k) => { store.set('deleted:' + k, true); return true; },
    match: async (k) => store.get(String(k)),
  };
  const scope = 'https://littlehivehouse.com/admin/';
  const self = {
    location: new URL(scope + 'sw.js'), registration: { scope },
    addEventListener: (t, fn) => { handlers[t] = fn; }, skipWaiting: async () => {}, clients: { claim: async () => {} },
  };
  const okRes = (url) => ({ ok: true, type: 'basic', url, clone() { return { ...this, cloned: true }; } });
  const sandbox = {
    self, caches, URL, Promise, console,
    fetch: async (u) => { const url = typeof u === 'string' ? u : u.url; fetched.push(url); if (/offline/.test(url)) throw new Error('offline'); return okRes(url); },
    Response: { error: () => ({ error: true }) },
  };
  vm.runInNewContext(read('sw.js'), sandbox, { filename: 'sw.js' });
  return { handlers, store, fetched };
}
function fetchEvent(url, method = 'GET') {
  const ev = { request: { url, method }, responded: null, respondWith(p) { this.responded = p; } };
  return ev;
}

test('service worker caches the app shell (network first) and never touches order data', async () => {
  const { handlers, store, fetched } = loadSW();
  // install pre-caches the shell under query-free keys
  let done;
  handlers.install({ waitUntil: (p) => { done = p; } });
  await done;
  for (const p of ['/admin/', '/admin/index.html', '/admin/admin.js', '/admin/admin.css', '/admin/icons/icon-512.png', '/assets/favicon.svg']) {
    assert.ok(store.has('https://littlehivehouse.com' + p), `precached ${p}`);
  }
  // shell requests are answered (with ?v= ignored for the cache key)
  const shell = fetchEvent('https://littlehivehouse.com/admin/admin.js?v=1');
  handlers.fetch(shell);
  assert.ok(shell.responded, 'shell request handled');
  await shell.responded;
  // order data and everything else is left alone: no respondWith, nothing cached
  const before = store.size;
  for (const url of [
    'https://firestore.googleapis.com/google.firestore.v1.Firestore/Listen/channel?database=projects%2Flittle-hive-house',
    'https://us-east1-little-hive-house.cloudfunctions.net/adminPhotoUrls',
    'https://firebasestorage.googleapis.com/v0/b/x/o/uploads%2Fu%2Fp%2F1.jpg?alt=media&token=t',
    'https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js',
    'https://littlehivehouse.com/assets/firebase-config.js',
    'https://littlehivehouse.com/assets/frames/frames.json',
    'https://littlehivehouse.com/admin/orders.json',
    'https://littlehivehouse.com/shop.html',
  ]) {
    const ev = fetchEvent(url);
    handlers.fetch(ev);
    assert.equal(ev.responded, null, `not intercepted: ${url}`);
  }
  const post = fetchEvent('https://littlehivehouse.com/admin/index.html', 'POST');
  handlers.fetch(post);
  assert.equal(post.responded, null, 'POST never intercepted');
  assert.equal(store.size, before, 'nothing new cached');
  assert.ok(!fetched.some((u) => /firestore|cloudfunctions|firebasestorage/.test(u)));
});

test('offline: the cached shell is served; old shell caches are removed on activate', async () => {
  const { handlers, store } = loadSW();
  store.set('https://littlehivehouse.com/admin/index.html', { cachedPage: true });
  const ev = fetchEvent('https://littlehivehouse.com/admin/index.html?offline=1');
  handlers.fetch(ev);
  assert.deepEqual(await ev.responded, { cachedPage: true });
  let done;
  handlers.activate({ waitUntil: (p) => { done = p; } });
  await done;
  assert.ok(store.get('deleted:hive-admin-shell-v0'));
  assert.ok(!store.get('deleted:hive-admin-shell-v1'), 'current cache kept');
  assert.ok(!store.get('deleted:someone-else'), 'other caches untouched');
});
