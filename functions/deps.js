"use strict";
/* Firebase Admin services, created lazily so every other module loads in plain `node --test`.
   Tests call deps.set({db, auth, bucket}) with in-memory fakes. */

let injected = null;
let app = null;
let dbReady = false;

function ensureApp() {
  if (!app) {
    const { initializeApp, getApps } = require("firebase-admin/app");
    // firebase-functions creates its own *named* app for callable checks, so look for the default app by name
    app = getApps().find((a) => a.name === "[DEFAULT]") || initializeApp();
  }
  return app;
}

module.exports = {
  set(fakes) { injected = fakes; },
  reset() { injected = null; },
  /** True when a database is there to use: test fakes are injected, or we run inside Cloud Functions. */
  available() { return !!(injected && injected.db) || !!process.env.K_SERVICE || !!process.env.FUNCTION_TARGET; },
  db() {
    if (injected && injected.db) return injected.db;
    const db = require("firebase-admin/firestore").getFirestore(ensureApp());
    if (!dbReady) {
      dbReady = true;
      try { db.settings({ ignoreUndefinedProperties: true }); } catch (e) { /* already configured */ }
    }
    return db;
  },
  auth() {
    if (injected && injected.auth) return injected.auth;
    return require("firebase-admin/auth").getAuth(ensureApp());
  },
  bucket() {
    if (injected && injected.bucket) return injected.bucket;
    return require("firebase-admin/storage").getStorage(ensureApp()).bucket();
  },
  /** firebase-admin/storage getDownloadURL, or null when not available (tests). */
  getDownloadURL(file) {
    if (injected) return injected.getDownloadURL ? injected.getDownloadURL(file) : Promise.resolve(null);
    ensureApp();
    return require("firebase-admin/storage").getDownloadURL(file);
  },
};
