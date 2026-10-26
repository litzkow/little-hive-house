"use strict";
/* The edge of a photo magnet, where the photo itself has nothing more to show.

   The paper of a magnet wraps over its sides, so the print carries a photo on past the 2 in face. Where the customer's
   photo has more than they picked, that real photo is used (printsheet.js renderPhoto). Where it ends right at the
   edge (a phone photo in a square magnet ends at its left and right sides), Stability AI's outpaint draws the missing
   strip as a continuation of the same scene. The front of the magnet is never touched: only the missing strip comes
   from the AI, the real photo is put back on top of the result.

   Needs STABILITY_API_KEY (a GitHub secret, see SETUP.md). About 4 credits ($0.04) per photo; each result is kept in
   Storage (print-cache/edges/<hash>.png), so printing the same photo again, a rebuild or a test sheet doesn't pay twice.
   Without the key, or when the call fails, the print falls back to the reflected edge and says so on the notes page. */

const crypto = require("crypto");
const { env } = require("./config");
const deps = require("./deps");

const ENDPOINT = "https://api.stability.ai/v2beta/stable-image/edit/outpaint";
const CREATIVITY = "0.3";                            // 0..1: low = stays close to the photo
const PROMPT = "seamless natural continuation of the same photograph, same scene, same lighting, same colours, no new objects, no text";
const TIMEOUT_MS = 90 * 1000;
const VERSION = "1";                                 // bump to make every cached edge again

function configured() { return !!env("STABILITY_API_KEY"); }

/** Pure: the cache name for a photo + what is asked of it. */
function cacheKey(photoBuf, parts) {
  const h = crypto.createHash("sha256");
  h.update(VERSION).update("\0").update(crypto.createHash("sha256").update(photoBuf).digest()).update(JSON.stringify(parts || {}));
  return h.digest("hex").slice(0, 40);
}

/** Pure: the form fields for the request (strings), without the image. */
function fields(ext) {
  const n = (v) => String(Math.max(0, Math.min(2000, Math.round(Number(v) || 0))));
  return { left: n(ext.l), right: n(ext.r), up: n(ext.t), down: n(ext.b), creativity: CREATIVITY, prompt: PROMPT, output_format: "png" };
}

/**
 * png (Buffer) -> Buffer: the same picture grown by ext {l, t, r, b} pixels, the new strips drawn by the AI.
 * key: cacheKey(...). Throws on failure (the caller falls back).
 */
async function outpaint(png, ext, { key, fetchImpl } = {}) {
  const path = key ? `print-cache/edges/${key}.png` : null;
  let bucket = null;
  try { bucket = deps.bucket(); } catch (e) { bucket = null; }
  if (bucket && path) {
    try { const [buf] = await bucket.file(path).download(); if (buf && buf.length) return buf; } catch (e) { /* not made yet */ }
  }
  const apiKey = env("STABILITY_API_KEY");
  if (!apiKey) throw new Error("STABILITY_API_KEY is not set");
  const form = new FormData();
  form.append("image", new Blob([png], { type: "image/png" }), "photo.png");
  for (const [k, v] of Object.entries(fields(ext))) form.append(k, v);
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), TIMEOUT_MS);
  let res;
  try {
    res = await (fetchImpl || fetch)(ENDPOINT, { method: "POST", headers: { Authorization: `Bearer ${apiKey}`, Accept: "image/*" }, body: form, signal: ctl.signal });
  } finally { clearTimeout(timer); }
  if (!res.ok) {
    let msg = "";
    try { msg = (await res.text()).slice(0, 200); } catch (e) { /* ignore */ }
    throw new Error(`Stability AI answered ${res.status}${res.status === 402 ? " (no credits left)" : res.status === 401 ? " (the key is wrong)" : ""}${msg ? `: ${msg}` : ""}`);
  }
  const out = Buffer.from(await res.arrayBuffer());
  if (out.length < 100) throw new Error("Stability AI sent back an empty picture");
  if (bucket && path) {
    try { await bucket.file(path).save(out, { contentType: "image/png", resumable: false, metadata: { cacheControl: "private, max-age=0" } }); } catch (e) { /* the print still works */ }
  }
  return out;
}

module.exports = { ENDPOINT, CREATIVITY, PROMPT, VERSION, configured, cacheKey, fields, outpaint };
