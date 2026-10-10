// Opens the live site in Safari's engine (WebKit) on iPhone sizes and lists anything wider than the screen.
import { webkit, devices } from 'playwright';
const BASE = process.env.BASE || 'https://littlehivehouse.com/';
const pages = ['', 'shop.html', 'collections/fall.html', 'collections/places.html', 'photo-magnets.html', 'big-orders.html', 'account.html', 'track.html', 'contact.html'];
const phones = ['iPhone 15 Pro Max', 'iPhone 13', 'iPhone SE'];
const note = m => console.log('::notice::' + m.replace(/\n/g, '%0A'));
process.on('unhandledRejection', e => { console.log('::error::' + String(e && e.stack || e).replace(/\n/g, '%0A')); process.exit(1); });
const browser = await webkit.launch();
let bad = 0;
for (const name of phones) {
  for (const p of pages) { try {
    const ctx = await browser.newContext({ ...devices[name] });
    const page = await ctx.newPage();
    await page.goto(BASE + p, { waitUntil: 'load', timeout: 45000 });
    for (let y = 0; y < 15000; y += 700) { await page.evaluate(y => scrollTo(0, y), y); await page.waitForTimeout(60); }
    await page.waitForTimeout(800);
    const r = await page.evaluate(async () => {
      const vw = document.documentElement.clientWidth, out = [];
      const path = el => { const a = []; while (el && el !== document.body && a.length < 5) { a.unshift(el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className ? '.' + el.className.trim().split(/\s+/).join('.') : '')); el = el.parentElement; } return a.join(' > '); };
      for (const el of document.querySelectorAll('body *')) {
        const rc = el.getBoundingClientRect();
        if (rc.width && rc.right > vw + 1) out.push(path(el) + '  right=' + Math.round(rc.right) + ' w=' + Math.round(rc.width));
      }
      await new Promise(r => setTimeout(r, 50)); scrollTo(0, 2500); const hdr = document.querySelector('.site-header'); const sticky = hdr ? Math.round(hdr.getBoundingClientRect().top) : -1;
      return { sticky, vw, sw: document.documentElement.scrollWidth, bw: document.body.scrollWidth, out: out.slice(0, 40) };
    });
    const wide = Math.max(r.sw, r.bw) > r.vw, flag = wide ? 'OVERFLOW' : 'ok';
    if (wide) bad++;
    note(`${flag} ${name} /${p} viewport=${r.vw} scrollWidth=${r.sw} body=${r.bw} headerTop=${r.sticky}` + (wide ? '\n' + r.out.join('\n') : ''));
    await page.screenshot({ path: `shots/${name.replace(/\W+/g, '-')}-${(p || 'home').replace(/\W+/g, '-')}.png` });
    await ctx.close();
  } catch (e) { note('ERROR ' + name + ' /' + p + ': ' + String(e).slice(0, 300)); } }
}
await browser.close();
console.log(`\n${bad} page(s) wider than the screen`);
