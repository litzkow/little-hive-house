/* Renders the "photo magnets for every occasion" showcase (assets/showcase/*.webp) with the real print renderer
   (functions/printsheet.js renderPhoto: the same frame, caption and touch-up a customer's magnet gets), from stock photos
   (Pexels license, free for commercial use) kept outside the repo. Usage:
     NODE_PATH=<dir with sharp> node tools/showcase/render.js <photos dir>
   Run again after the frames change. */
"use strict";
const fs = require("fs");
const path = require("path");
const ROOT = path.join(__dirname, "..", "..");
process.env.SITE_URL = "https://littlehivehouse.com";
const P = require(path.join(ROOT, "functions", "printsheet.js"));
const sharp = require("sharp");
const SRC = process.argv[2];
const OUT = path.join(ROOT, "assets", "showcase");
const LIST = require("./list.json");

const fetchImpl = async (url) => {
  const buf = fs.readFileSync(path.join(ROOT, decodeURIComponent(new URL(url).pathname.slice(1))));
  return { ok: true, status: 200, arrayBuffer: async () => buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength) };
};

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const ctx = P._internal.makeContext({ items: [{ kind: "photos" }] }, { fetchImpl, readPhoto: async (p) => fs.readFileSync(path.join(SRC, p)), cut: 2, enhance: true });
  ctx.frames = await P._internal.loadFrames(ctx);
  for (const occ of LIST) {
    for (const [i, m] of occ.magnets.entries()) {
      const tile = await P._internal.renderPhoto({ kind: "photo", n: 1, pack: 1, path: m.file, frame: m.frame, caption: m.caption || "", crop: m.crop || null }, ctx);
      const meta = await sharp(tile).metadata();
      const e = Math.round((meta.width - 600) / 2);
      const out = path.join(OUT, `${occ.id}-${i + 1}.webp`);
      await sharp(tile).extract({ left: e, top: e, width: 600, height: 600 }).resize(480, 480, { kernel: "lanczos3" }).webp({ quality: 82 }).toFile(out);
      console.log(out, ctx.warnings.splice(0).join(" "));
    }
  }
})().catch((e) => { console.error(e); process.exit(1); });
