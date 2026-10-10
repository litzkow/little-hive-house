// Renders designs/<col>/<slug>.svg to PNG with the real fonts. Usage: node raster.js jobs.json
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const fontsDir = process.argv[3];
  const scale = Number(process.argv[4] || 1);
  const css = `
@font-face{font-family:"Anton";src:url("file://${fontsDir}/Anton-Regular.ttf")}
@font-face{font-family:"Bebas Neue";src:url("file://${fontsDir}/BebasNeue-Regular.ttf")}
@font-face{font-family:"Cinzel";font-weight:400 900;src:url("file://${fontsDir}/Cinzel[wght].ttf")}
@font-face{font-family:"DM Mono";font-weight:500;src:url("file://${fontsDir}/DMMono-Medium.ttf")}
@font-face{font-family:"DM Serif Display";src:url("file://${fontsDir}/DMSerifDisplay-Regular.ttf")}
@font-face{font-family:"Josefin Sans";font-weight:100 700;src:url("file://${fontsDir}/JosefinSans[wght].ttf")}
@font-face{font-family:"Jost";font-weight:100 900;src:url("file://${fontsDir}/Jost[wght].ttf")}
@font-face{font-family:"Playfair Display";font-style:italic;font-weight:400 900;src:url("file://${fontsDir}/PlayfairDisplay-Italic[wght].ttf")}
html,body{margin:0;background:transparent} #s>svg{width:600px;height:600px;display:block}`;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 600, height: 600 }, deviceScaleFactor: scale });
  const os = require('os'), path = require('path');
  const hp = path.join(os.tmpdir(), 'lhh-raster-' + process.pid + '.html');
  fs.writeFileSync(hp, `<html><head><style>${css}</style></head><body><div id="s"></div>
    <span style="font-family:Anton">a</span><span style="font-family:'Bebas Neue'">a</span><span style="font-family:Cinzel;font-weight:600">a</span>
    <span style="font-family:'DM Mono';font-weight:500">a</span><span style="font-family:'DM Serif Display'">a</span><span style="font-family:'Josefin Sans';font-weight:700">a</span>
    <span style="font-family:Jost">a</span><span style="font-family:'Playfair Display';font-style:italic;font-weight:700">a</span></body></html>`);
  await p.goto('file://' + hp);
  await p.waitForTimeout(300);
  await p.evaluate(() => document.fonts.ready);
  for (const [src, out] of jobs) {
    await p.evaluate((svg) => { document.getElementById('s').innerHTML = svg; }, fs.readFileSync(src, 'utf8'));
    await p.evaluate(() => document.fonts.ready);
    await p.locator('#s > svg').screenshot({ path: out, omitBackground: true });
  }
  await b.close();
  fs.unlinkSync(hp);
})();
