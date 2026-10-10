"use strict";
/* In-memory stand-ins for Firestore, Auth, Storage, Stripe and Resend, just big enough for the handlers. */

let autoN = 0;
const autoId = () => `auto${String(++autoN).padStart(6, "0")}x${Math.random().toString(36).slice(2, 8)}`.replace(/[^A-Za-z0-9]/g, "");

const clone = (v) => (v === undefined ? undefined : JSON.parse(JSON.stringify(v, (k, x) => (x === undefined ? undefined : x))));

function getPath(obj, path) {
  return path.split(".").reduce((o, k) => (o && typeof o === "object" ? o[k] : undefined), obj);
}
function setPath(obj, path, value) {
  const keys = path.split(".");
  let o = obj;
  for (let i = 0; i < keys.length - 1; i++) {
    if (!o[keys[i]] || typeof o[keys[i]] !== "object") o[keys[i]] = {};
    o = o[keys[i]];
  }
  if (value === undefined) delete o[keys[keys.length - 1]];
  else o[keys[keys.length - 1]] = clone(value);
}
function deepMerge(a, b) {
  const out = { ...(a || {}) };
  for (const [k, v] of Object.entries(b || {})) {
    if (v === undefined) continue;
    if (v && typeof v === "object" && !Array.isArray(v) && out[k] && typeof out[k] === "object" && !Array.isArray(out[k])) out[k] = deepMerge(out[k], v);
    else out[k] = clone(v);
  }
  return out;
}

class Snap {
  constructor(ref, data) { this.ref = ref; this.id = ref.id; this._d = data; this.exists = data !== undefined; }
  data() { return clone(this._d); }
}

class DocRef {
  constructor(db, coll, id) { this.db = db; this.coll = coll; this.id = id; this.path = `${coll}/${id}`; }
  async get() { return new Snap(this, this.db.docs.get(this.path)); }
  async set(data, opts) { this.db._set(this.path, data, opts); }
  async update(data) { this.db._update(this.path, data); }
  async create(data) { if (this.db.docs.has(this.path)) { const e = new Error("ALREADY_EXISTS"); e.code = 6; throw e; } this.db._set(this.path, data); }
  async delete() { this.db.docs.delete(this.path); }
}

class Query {
  constructor(db, coll, filters = [], lim = null) { this.db = db; this.coll = coll; this.filters = filters; this.lim = lim; }
  where(f, op, v) { return new Query(this.db, this.coll, this.filters.concat([[f, op, v]]), this.lim); }
  orderBy() { return this; }
  limit(n) { return new Query(this.db, this.coll, this.filters, n); }
  async get() {
    const docs = [];
    for (const [path, data] of this.db.docs) {
      const [c, id] = path.split("/");
      if (c !== this.coll) continue;
      const ok = this.filters.every(([f, op, v]) => {
        const x = getPath(data, f);
        if (op === "==") return x === v;
        if (op === "in") return v.includes(x);
        if (op === "<=") return x <= v;
        if (op === ">=") return x >= v;
        throw new Error(`fake: op ${op}`);
      });
      if (ok) docs.push(new Snap(new DocRef(this.db, c, id), data));
      if (this.lim && docs.length >= this.lim) break;
    }
    return { empty: docs.length === 0, size: docs.length, docs };
  }
}

class CollRef extends Query {
  constructor(db, name) { super(db, name); this.name = name; }
  doc(id) { return new DocRef(this.db, this.name, id || autoId()); }
  async add(data) { const r = this.doc(); await r.set(data); return r; }
}

class FakeDB {
  constructor() { this.docs = new Map(); }
  collection(name) { return new CollRef(this, name); }
  _set(path, data, opts) {
    const cur = this.docs.get(path);
    this.docs.set(path, opts && opts.merge ? deepMerge(cur, data) : clone(data));
  }
  _update(path, data) {
    const cur = this.docs.get(path);
    if (cur === undefined) { const e = new Error(`NOT_FOUND: ${path}`); e.code = 5; throw e; }
    const next = clone(cur);
    for (const [k, v] of Object.entries(data)) setPath(next, k, v);
    this.docs.set(path, next);
  }
  async runTransaction(fn) {
    const writes = [];
    const tx = {
      get: (r) => r.get(),
      set: (r, d, o) => { writes.push(() => this._set(r.path, d, o)); return tx; },
      update: (r, d) => { writes.push(() => this._update(r.path, d)); return tx; },
      create: (r, d) => { writes.push(() => { if (this.docs.has(r.path)) throw new Error("ALREADY_EXISTS"); this._set(r.path, d); }); return tx; },
      delete: (r) => { writes.push(() => this.docs.delete(r.path)); return tx; },
    };
    const out = await fn(tx);
    writes.forEach((w) => w());
    return out;
  }
  get(path) { return clone(this.docs.get(path)); }
}

class FakeAuth {
  constructor() { this.users = new Map(); }
  async getUser(uid) { const u = this.users.get(uid); if (!u) { const e = new Error("no user"); e.code = "auth/user-not-found"; throw e; } return { ...u }; }
  async setCustomUserClaims(uid, claims) { this.users.set(uid, { ...(this.users.get(uid) || { uid }), customClaims: claims }); }
  async generatePasswordResetLink(email) {
    if (![...this.users.values()].some((u) => u.email === email)) { const e = new Error("no user"); e.code = "auth/user-not-found"; throw e; }
    return `https://example.firebaseapp.com/__/auth/action?mode=resetPassword&oobCode=abc&email=${encodeURIComponent(email)}`;
  }
  async generateEmailVerificationLink(email, settings) {
    this.verifyLinks = (this.verifyLinks || []).concat([{ email, settings }]);
    return `https://example.firebaseapp.com/__/auth/action?mode=verifyEmail&oobCode=v${this.verifyLinks.length}&continueUrl=${encodeURIComponent((settings && settings.url) || "")}`;
  }
}

class FakeBucket {
  constructor() { this.files = new Map(); this.name = "test-bucket"; }
  file(path) {
    const self = this;
    return {
      name: path,
      async exists() { return [self.files.has(path)]; },
      async getMetadata() { return [{ metadata: (self.files.get(path) || {}).metadata || {} }]; },
      async setMetadata(m) { const f = self.files.get(path) || {}; f.metadata = { ...(f.metadata || {}), ...(m.metadata || {}) }; self.files.set(path, f); },
    };
  }
}

/** Stripe + Resend over a fake fetch. stripe.handlers["POST /v1/refunds"] = (params) => object */
function fakeNet() {
  const calls = [];
  const emails = [];
  const handlers = {};
  async function fetchImpl(url, init = {}) {
    const method = init.method || "GET";
    const u = new URL(url);
    if (u.host === "api.resend.com") {
      const body = JSON.parse(init.body);
      emails.push(body);
      return { ok: true, status: 200, json: async () => ({ id: `em_${emails.length}` }) };
    }
    const params = new URLSearchParams(method === "GET" ? u.search : init.body || "");
    const flat = Object.fromEntries(params.entries());
    calls.push({ method, path: u.pathname, params: flat, headers: init.headers || {} });
    const key = `${method} ${u.pathname}`;
    const h = handlers[key] || Object.entries(handlers).find(([k]) => k.endsWith("*") && key.startsWith(k.slice(0, -1)))?.[1];
    if (!h) return { ok: false, status: 404, json: async () => ({ error: { message: `fake: no route ${key}` } }) };
    try {
      const out = await h(flat, u);
      return { ok: true, status: 200, json: async () => clone(out) };
    } catch (err) {
      return { ok: false, status: err.status || 400, json: async () => ({ error: { message: err.message, type: "invalid_request_error" } }) };
    }
  }
  return { fetch: fetchImpl, calls, emails, handlers };
}

module.exports = { FakeDB, FakeAuth, FakeBucket, fakeNet, clone };
