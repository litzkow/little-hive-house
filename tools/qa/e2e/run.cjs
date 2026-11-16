/* Little Hive House: browser tests of the shop (cart, photo builder, checkout, problem reports), on a local copy of the
   site with a fake Firebase (fakefb.js) and a fake Stripe page: nothing real is charged, uploaded or emailed.
   Reproduces the real problems customers had (photo page reloading on iPhone, photo pack vanishing from the cart,
   items lost between tabs / with the back button, photos over 25 MB failing at checkout).
   Run:  BROWSER=webkit node tools/qa/e2e/run.cjs      (webkit = Safari's engine; chromium = Chrome)
   CI:   .github/workflows/site-tests.yml runs it in both engines on every change to the site. */
const { chromium, webkit } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..', '..');
const FAKE = fs.readFileSync(path.join(__dirname, 'fakefb.js'), 'utf8');
const ENGINE = (process.env.BROWSER || 'chromium').toLowerCase();
const ONLY = process.env.ONLY || '';
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.json': 'application/json', '.woff2': 'font/woff2', '.xml': 'application/xml', '.ico': 'image/x-icon', '.webmanifest': 'application/manifest+json' };

function serve() {
  return new Promise((res) => {
    const srv = http.createServer((req, rsp) => {
      let p = decodeURIComponent(req.url.split('?')[0]);
      if (req.method === 'POST' && p === '/__log') { let b = ''; req.on('data', (c) => (b += c)); req.on('end', () => { LOGS.push(JSON.parse(b || '{}')); rsp.writeHead(204); rsp.end(); }); return; }
      if (p.endsWith('/')) p += 'index.html';
      const f = path.join(ROOT, p);
      if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { rsp.writeHead(404); rsp.end('404'); return; }
      rsp.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
      fs.createReadStream(f).pipe(rsp);
    }).listen(0, '127.0.0.1', () => res(srv));
  });
}
const LOGS = [];
let BASE = '';
const results = [];
function ok(name, cond, extra) { results.push({ name, pass: !!cond }); console.log(`${cond ? 'PASS' : 'FAIL'} ${name}${extra !== undefined && extra !== '' ? '  [' + String(extra).slice(0, 1200) + ']' : ''}`); }

async function context(browser, o = {}) {
  const ctx = await browser.newContext({ viewport: { width: o.w || 390, height: o.h || 844 }, ...(ENGINE === 'webkit' ? {} : { deviceScaleFactor: 3, isMobile: true }), hasTouch: true,
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1' });
  await ctx.route(/gstatic\.com\/firebasejs\//, (r) => r.fulfill({ body: FAKE, contentType: 'application/javascript' }));
  await ctx.route(/googletagmanager|google-analytics|fonts\.googleapis|fonts\.gstatic|facebook|tiktok|instagram|cloudfunctions\.net/, (r) => r.abort());
  await ctx.route(/checkout\.stripe\.com/, (r) => r.fulfill({ body: '<html><body>STRIPE TEST PAGE</body></html>', contentType: 'text/html' }));
  await ctx.addInitScript(({ lang, fake, base }) => {
    try { localStorage.setItem('lhh-lang', lang); } catch (e) {}
    window.__FAKE = Object.assign(window.__FAKE || {}, fake || {});
    window.LHH_LOG_URL = base + '__log';
  }, { lang: o.lang || 'en', fake: o.fake || {}, base: BASE });
  return ctx;
}
const CONSOLE = [];
function watch(pg) { const e = []; pg.on('pageerror', (x) => e.push(x.message)); pg.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') CONSOLE.push(m.type() + ': ' + m.text().slice(0, 200)); }); return e; }
async function page(ctx, p) { const pg = await ctx.newPage(); const errs = watch(pg); await pg.goto(BASE + p, { waitUntil: 'load' }); await pg.waitForTimeout(400); return { pg, errs }; }

/* photos made in the page itself (no fixture files): kind = jpeg | png-big (noisy 4000x3000 PNG, over 20 MB) | small | junk */
async function addPhotos(pg, list) {
  await pg.evaluate(async (list) => {
    const dt = new DataTransfer();
    for (const [kind, name] of list) {
      let blob;
      if (kind === 'junk') blob = new Blob(['not a photo '.repeat(200)], { type: 'image/jpeg' });
      else {
        const [w, h] = kind === 'png-big' ? [4000, 3000] : kind === 'small' ? [300, 300] : kind === 'mid' ? [900, 1200] : [3024, 4032];
        const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d');
        if (kind === 'png-big') { const im = g.createImageData(w, h); const d = im.data; let s = 1; for (let i = 0; i < d.length; i++) { s = (s * 1103515245 + 12345) & 0x7fffffff; d[i] = i % 4 === 3 ? 255 : s & 255; } g.putImageData(im, 0, 0); }
        else { const gr = g.createLinearGradient(0, 0, w, h); gr.addColorStop(0, '#e9a'); gr.addColorStop(1, '#3a6'); g.fillStyle = gr; g.fillRect(0, 0, w, h); g.fillStyle = '#fff'; g.font = '200px sans-serif'; g.fillText(name, 100, 400); }
        blob = await new Promise((r) => c.toBlob(r, kind === 'png-big' ? 'image/png' : 'image/jpeg', 0.9));
        c.width = c.height = 0;
      }
      dt.items.add(new File([blob], name, { type: blob.type || 'image/jpeg' }));
    }
    const inp = document.getElementById('photos'); inp.files = dt.files; inp.dispatchEvent(new Event('change', { bubbles: true }));
  }, list);
}
const thumbsReady = (pg, n) => pg.waitForFunction((n) => document.querySelectorAll('.thumb-btn svg.ph image').length >= n, n, { timeout: 120000 });
async function pack(pg, size) { await pg.evaluate((s) => { const r = document.getElementById('pack-' + s); r.checked = true; r.dispatchEvent(new Event('change', { bubbles: true })); }, size); }
async function addPackToCart(pg) {
  await pg.check('#rights', { force: true });
  await pg.waitForFunction(() => !document.getElementById('add-custom').disabled, null, { timeout: 20000 })
    .catch(async () => { throw new Error('Add to cart stays disabled: ' + await pg.evaluate(() => document.getElementById('counter').textContent + ' / rights=' + document.getElementById('rights').checked)); });
  await pg.click('#add-custom'); await pg.waitForTimeout(1500);
}
const STRIPE = { url: 'https://checkout.stripe.com/c/pay/cs_test_x', orderId: 'ord1' };

const SUITES = {
  async pages(browser) {
    const files = fs.readdirSync(ROOT).filter((f) => f.endsWith('.html')).concat(['collections/brasil.html', 'm/americana/bald-eagle.html']);
    for (const lang of ['en', 'pt']) {
      const ctx = await context(browser, { lang }); const bad = [];
      for (const f of files) {
        const { pg, errs } = await page(ctx, f);
        const over = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
        if (errs.length || over > 1) bad.push(`${f} overflow=${over} ${errs.join('|')}`);
        await pg.close();
      }
      ok(`every page opens without errors and fits an iPhone screen (${lang})`, !bad.length, bad.join(' ; '));
      await ctx.close();
    }
  },
  async cart(browser) {
    const ctx = await context(browser);
    const { pg, errs } = await page(ctx, 'shop.html');
    await pg.evaluate(() => { window.__ev = []; ['pointerdown', 'click', 'storage', 'pagehide', 'pageshow'].forEach((t) => window.addEventListener(t, (e) => window.__ev.push(t + ':' + ((e.target && e.target.getAttribute && (e.target.getAttribute('data-add') || e.target.className || e.target.tagName)) || '') + ':' + LHH.totals().count), true)); });
    const add = async (p, n) => { const before = await p.evaluate(() => LHH.totals().count); /* centred and already still, like a person taps it: the site scrolls smoothly (scroll-behavior: smooth), and a tap
         during that animation lands somewhere else when the finger lifts; at the very top it would sit under the header */
      await p.locator('[data-add]').nth(n).evaluate((e) => e.scrollIntoView({ block: 'center', behavior: 'instant' }));
      await p.waitForTimeout(250); await p.locator('[data-add]').nth(n).click();
      await p.waitForFunction((b) => LHH.totals().count > b, before, { timeout: 5000 }).catch(() => {}); };
    await add(pg, 0); await add(pg, 0); await add(pg, 3);
    let c = await pg.evaluate(() => LHH.cart().map((l) => l.qty));
    const dbg = c.join() === '2,1' ? '' : JSON.stringify(await pg.evaluate(() => { const els = [...document.querySelectorAll('[data-add]')].slice(0, 4); const e = els[3], r = e.getBoundingClientRect(); const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
      return { ev: window.__ev, url: location.pathname, ids: els.map((x) => x.getAttribute('data-add')), rect: [Math.round(r.top), Math.round(r.left), Math.round(r.width), Math.round(r.height)], hit: hit && (hit.outerHTML || '').slice(0, 120), cart: LHH.cart(), ls: localStorage.getItem('lhh-cart') }; }));
    ok('cart: same design twice is one line with quantity 2', c.join() === '2,1', c.join() + ' ' + dbg.slice(0, 900));
    await pg.reload(); await pg.waitForTimeout(300);
    await pg.goto(BASE + 'collections/brasil.html'); await pg.waitForTimeout(300);
    ok('cart: survives reload and other pages', (await pg.evaluate(() => LHH.cart().length)) === 2);
    const tabB = await ctx.newPage(); await tabB.goto(BASE + 'shop.html'); await tabB.waitForTimeout(300);
    await add(pg, 1); await pg.waitForTimeout(300);
    await add(tabB, 9); await tabB.waitForTimeout(300);
    await pg.reload(); await pg.waitForTimeout(300);
    ok('cart: two tabs adding at the same time lose nothing (real bug, Nov 2026)', (await pg.evaluate(() => LHH.cart().length)) === 4, await pg.evaluate(() => LHH.cart().length));
    const st = await ctx.storageState(); const ctx2 = await browser.newContext({ storageState: st });
    await ctx2.route(/gstatic|google|facebook/, (r) => r.abort());
    const p2 = await ctx2.newPage(); await p2.goto(BASE + 'index.html'); await p2.waitForTimeout(300);
    ok('cart: survives closing and reopening the browser', (await p2.evaluate(() => LHH.cart().length)) === 4);
    await ctx2.close();
    ok('cart: no JS errors', !errs.length, errs.join('|'));
    await ctx.close();
  },
  async photos(browser) {
    const ctx = await context(browser, { lang: 'pt' });
    const { pg, errs } = await page(ctx, 'photo-magnets.html');
    await pack(pg, 9);
    await addPhotos(pg, [['jpeg', 'IMG_0001.JPG'], ['jpeg', 'foto da praia ção 🎉.jpeg'], ['small', 'tiny.jpg'], ['junk', 'not a photo.jpg'], ['jpeg', 'Ñandú #1 (cópia).jpg']]);
    await thumbsReady(pg, 4); await pg.waitForTimeout(800);
    ok('photos: real photos added, a file that is not a photo refused with a message', (await pg.$$eval('.thumb-btn', (a) => a.length)) === 4 && /arquivos|files?/i.test(await pg.$eval('#toast', (e) => e.textContent)), await pg.$eval('#toast', (e) => e.textContent));
    ok('photos: low-resolution photo flagged', (await pg.$$eval('.lowtag', (a) => a.length)) === 1);
    const href = await pg.$eval('.thumb-btn svg.ph image', (i) => i.getAttribute('href'));
    const w = await pg.evaluate(async (u) => { const im = new Image(); im.src = u; await im.decode(); return Math.max(im.naturalWidth, im.naturalHeight); }, href);
    ok('photos: the page shows light copies, never the 12 MP original (iPhone crash, Nov 2026)', w <= 640, w + ' px');
    await pg.click('.thumb-btn[data-i="0"]'); await pg.waitForSelector('#studio[open]');
    const capFrame = await pg.$$eval('#swatches .swatch', (ds) => ds.find((d) => d.querySelector('.sw-tag')).querySelector('input').value);
    await pg.click('#sw-' + capFrame, { force: true }); await pg.type('#studio-cap', 'Vovó & Vovô 1965', { delay: 10 });
    await pg.click('#studio-done'); await pg.waitForTimeout(700);
    const before = await pg.$$eval('.thumb-btn', (a) => a.map((b) => b.getAttribute('aria-label')).join('|'));
    await pg.reload();
    await thumbsReady(pg, 4).catch(async () => { throw new Error('after reload only ' + await pg.$$eval('.thumb-btn', (a) => a.length) + ' photos came back'); });
    await pg.waitForTimeout(400);
    const after = await pg.$$eval('.thumb-btn', (a) => a.map((b) => b.getAttribute('aria-label')).join('|'));
    ok('photos: a reload brings back the same photos, frames and captions (iPhone crash, Nov 2026)', before === after, after.slice(0, 120));
    await addPackToCart(pg);
    await pg.goto(BASE + 'shop.html'); await pg.waitForTimeout(500);
    const back = await pg.evaluate(() => LHH.photosReady.then(() => LHH.cart().filter((l) => l.kind === 'custom').map((l) => l.photos.filter((p) => p.blob).length)));
    ok('photos: the pack stays in the cart, with its photos, on another page (real bug, Nov 2026)', back.join() === '4', back.join());
    ok('photos: no JS errors', !errs.length, errs.join('|'));
    await ctx.close();
  },
  async checkout(browser) {
    { const ctx = await context(browser, { fake: { calls: { createCheckout: STRIPE }, uploadMsPerMB: 5, callDelay: 3000 } });
      const { pg, errs } = await page(ctx, 'photo-magnets.html');
      await pack(pg, 4); await addPhotos(pg, [['png-big', 'big screenshot.png'], ['jpeg', 'a.jpg']]); await thumbsReady(pg, 2);
      await addPackToCart(pg);
      await pg.goto(BASE + 'shop.html'); await pg.waitForTimeout(400);
      await pg.evaluate(() => LHH.openCart()); await pg.click('#checkout');
      let st = null;
      for (let i = 0; i < 900 && !st; i++) { st = await pg.evaluate(() => window.__FAKE.callsMade.find((c) => c.name === 'createCheckout') ? { up: window.__FAKE.uploads, call: window.__FAKE.callsMade.find((c) => c.name === 'createCheckout') } : null).catch(() => null); if (!st) await pg.waitForTimeout(100); }
      ok('checkout: every photo uploaded once', st && st.up.length === 2, st && st.up.length);
      ok('checkout: photos over 20 MB are shrunk before upload (store limit 25 MB)', st && st.up.every((u) => u.size <= 20 * 1024 * 1024), st && st.up.map((u) => Math.round(u.size / 1e5) / 10 + 'MB').join(' '));
      const pk = st && st.call.data.cart.find((l) => l.kind === 'photos');
      ok('checkout: the order gets exactly the uploaded photos', pk && pk.photos.map((p) => p.path).join() === st.up.map((u) => u.path).join());
      await pg.waitForURL(/stripe/, { timeout: 30000 }).catch(() => {});
      ok('checkout: reaches the (fake) Stripe page', /stripe/.test(pg.url()));
      ok('checkout: no JS errors', !errs.length, errs.join('|'));
      await ctx.close(); }
    { // a passing storage error (Instagram's browser, Nov 2026): the photo tries again by itself, the customer sees nothing
      const ctx = await context(browser, { fake: { calls: { createCheckout: STRIPE }, uploadFailAt: 2, uploadFailCode: 'storage/unknown', callDelay: 2500 } });
      const { pg } = await page(ctx, 'photo-magnets.html');
      await pack(pg, 4); await addPhotos(pg, [['jpeg', '1.jpg'], ['jpeg', '2.jpg'], ['jpeg', '3.jpg']]); await thumbsReady(pg, 3);
      await addPackToCart(pg); await pg.click('#checkout');
      let st = null;
      for (let i = 0; i < 300 && !st; i++) { st = await pg.evaluate(() => window.__FAKE.callsMade.find((c) => c.name === 'createCheckout') ? { up: window.__FAKE.uploads.length, err: !document.getElementById('co-error').hidden } : null).catch(() => null); if (!st) await pg.waitForTimeout(100); }
      ok('checkout: a passing storage error is retried by itself (Instagram, Nov 2026)', st && !st.err && st.up === 4, JSON.stringify(st));
      await ctx.close(); }
    { // a photo that keeps failing: clear message, everything stops, the photos already up are kept for the next try
      const ctx = await context(browser, { fake: { calls: { createCheckout: STRIPE }, uploadFailPath: '/3\\.jpg$', uploadFailCode: 'storage/unknown', uploadMsPerMB: 200 } });
      const { pg } = await page(ctx, 'photo-magnets.html');
      await pack(pg, 4); await addPhotos(pg, [['jpeg', '1.jpg'], ['jpeg', '2.jpg'], ['jpeg', '3.jpg'], ['jpeg', '4.jpg']]); await thumbsReady(pg, 4);
      await addPackToCart(pg); await pg.click('#checkout');
      await pg.waitForSelector('#co-error:not([hidden])', { timeout: 60000 }).catch(async () => {
        throw new Error('no error shown: ' + JSON.stringify(await pg.evaluate(() => ({ url: location.pathname, label: document.getElementById('checkout').textContent, ups: window.__FAKE.uploads.map((u) => u.path.split('/').pop() + (u.done ? '+' : '-')), calls: window.__FAKE.callsMade.map((c) => c.name), prog: (document.querySelector('.co-progress, #co-progress') || {}).textContent }))));
      });
      await pg.waitForTimeout(2500);
      const after = await pg.evaluate(() => ({ label: document.getElementById('checkout').textContent, busy: document.getElementById('checkout').disabled, msg: document.getElementById('co-error').textContent, tries: window.__FAKE.uploads.filter((u) => /\/3\.jpg$/.test(u.path)).length }));
      ok('checkout: a photo that keeps failing tries 3 times, then a clear message', after.tries === 3 && after.msg.length > 10, JSON.stringify(after));
      ok('checkout: after the error the button is back to normal (it said "Please keep this page open")', !after.busy && !/keep this page/i.test(after.label), after.label);
      ok('checkout: the owners are told which photo failed', LOGS.some((l) => l.kind === 'upload_failed' && /photo 3/.test(l.msg)), (LOGS.filter((l) => l.kind === 'upload_failed').pop() || {}).msg);
      const before = await pg.evaluate(() => window.__FAKE.uploads.length);
      await pg.evaluate(() => { window.__FAKE.uploadFailPath = ''; window.__FAKE.uploadMsPerMB = 5; });
      await pg.click('#checkout'); await pg.waitForURL(/stripe/, { timeout: 60000 }).catch(() => {});
      ok('checkout: trying again works', /stripe/.test(pg.url()));
      await ctx.close(); }
    { const ctx = await context(browser, { fake: { calls: { createCheckout: STRIPE }, callDelay: 1500 } });
      const { pg } = await page(ctx, 'shop.html');
      await pg.click('[data-add] >> nth=0'); await pg.evaluate(() => LHH.openCart());
      await pg.evaluate(() => { const b = document.getElementById('checkout'); b.click(); b.click(); b.click(); }); await pg.waitForTimeout(600);
      ok('checkout: three taps on Checkout make one order', (await pg.evaluate(() => window.__FAKE.callsMade.filter((c) => c.name === 'createCheckout').length)) === 1);
      await ctx.close(); }
  },
  async quantity(browser) {
    /* any number of photo magnets (15 Nov 2026, a customer wanted 18 and 10, not 16 and 9) */
    const P = require(path.join(ROOT, 'functions', 'pricing.js')); const cat = P.loadCatalog();
    const ctx = await context(browser);
    const { pg, errs } = await page(ctx, 'photo-magnets.html');
    const state = () => pg.evaluate(() => ({ total: document.getElementById('builder-total').textContent, counter: document.getElementById('counter').textContent,
      more: document.getElementById('more-photos').hidden ? '' : document.getElementById('more-photos').textContent,
      fit: document.getElementById('fit-photos').hidden ? '' : document.getElementById('fit-photos').textContent, pack: document.querySelector('input[name=pack]:checked').value }));
    const many = (n, tag) => Array.from({ length: n }, (_, i) => ['mid', `${tag}${i + 1}.jpg`]);
    await pack(pg, 16); await addPhotos(pg, many(18, 'a')); await thumbsReady(pg, 18); await pg.waitForTimeout(300);
    let st = await state();
    ok('quantity: 18 photos on the 16 pack = 16 + 2 extra, $45', st.total === '$45' && /pack of 16 \+ 2 extra/.test(st.counter), JSON.stringify(st));
    ok('quantity: the "add more" nudge shows the price of 1 and 2 more photos', /Add 1 more photo for \$2\.50, or 2 for \$5/.test(st.more), st.more);
    await addPackToCart(pg);
    const line = await pg.evaluate(() => LHH.cart().find((l) => l.kind === 'custom'));
    const server = P.priceCart([{ kind: 'photos', packSize: line.count, qty: 1, photos: line.photos.map((p, i) => ({ path: 'uploads/u/x/' + (i + 1) + '.jpg', frame: p.frame })) }], cat);
    ok('quantity: the cart line (18 magnets, $45) is what the server charges', line.count === 18 && line.price === 45 && server.items[0].price === 45, `${line.count} ${line.price} ${server.items[0].price}`);
    await pg.evaluate(() => { LHH.clear(); LHH.closeCart && LHH.closeCart(); }); await pg.waitForTimeout(300);
    await pack(pg, 9); await addPhotos(pg, many(15, 'b')); await thumbsReady(pg, 15); await pg.waitForTimeout(300);
    st = await state();
    ok('quantity: 15 photos cost as much as the 16 pack, so the 16 pack gets picked with room for 1 more', st.pack === '16' && st.total === '$40' && /moved you to the pack of 16/.test(st.more), JSON.stringify(st));
    for (let i = 0; i < 5; i++) await pg.click('.thumb-x >> nth=0');
    await pg.waitForTimeout(300); st = await state();
    ok('quantity: 10 photos on the 16 pack offer "make just these" for $27.75', /Make just these for \$27\.75/.test(st.fit), JSON.stringify(st));
    await pg.click('#fit-photos'); await pg.waitForTimeout(200); st = await state();
    ok('quantity: after "make just these" it is 10 magnets for $27.75', st.total === '$27.75' && st.pack === '9' && /pack of 9 \+ 1 extra/.test(st.counter), JSON.stringify(st));
    for (let i = 0; i < 8; i++) await pg.click('.thumb-x >> nth=0');
    await pack(pg, 1); await pg.evaluate(() => document.querySelector('input[name=pack]:checked').dispatchEvent(new Event('change', { bubbles: true }))); await pg.waitForTimeout(200); st = await state();
    ok('quantity: "1 to 3" with 2 photos = $8', st.total === '$8' && /2 photos added, \$4 each/.test(st.counter), JSON.stringify(st));
    ok('quantity: no JS errors', !errs.length, errs.join('|'));
    await ctx.close();
  },
  async reports(browser) {
    const ctx = await context(browser);
    const pg = await ctx.newPage(); watch(pg);
    await pg.addInitScript(() => { if (!sessionStorage.getItem('__s')) { sessionStorage.setItem('__s', '1'); sessionStorage.setItem('lhh-builder-live', '5'); } });
    await pg.goto(BASE + 'photo-magnets.html'); await pg.waitForTimeout(1200);
    ok('reports: a photo page that reloaded by itself is reported to the owners', LOGS.some((l) => l.kind === 'builder_crash' && l.photos === 5));
    const n = LOGS.filter((l) => l.kind === 'builder_crash').length;
    await pg.goto(BASE + 'shop.html'); await pg.goto(BASE + 'photo-magnets.html'); await pg.waitForTimeout(1200);
    ok('reports: leaving the page normally is not reported', LOGS.filter((l) => l.kind === 'builder_crash').length === n);
    await ctx.close();
  },
};

(async () => {
  const srv = await serve(); BASE = `http://127.0.0.1:${srv.address().port}/`;
  const browser = await (ENGINE === 'webkit' ? webkit : chromium).launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
  console.log(`Little Hive House site tests · ${ENGINE}`);
  for (const [name, fn] of Object.entries(SUITES)) {
    if (ONLY && !ONLY.split(',').includes(name)) continue;
    CONSOLE.length = 0;
    try { await fn(browser); } catch (e) { ok(`${name}: finished without crashing`, false, e.message.split('\n')[0]); if (CONSOLE.length) console.log('  browser console:\n  ' + CONSOLE.slice(-8).join('\n  ')); }
  }
  await browser.close(); srv.close();
  const failed = results.filter((r) => !r.pass);
  console.log(`\n${results.length - failed.length} of ${results.length} passed (${ENGINE})`);
  process.exit(failed.length ? 1 : 0);
})();
