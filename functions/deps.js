"use strict";
/* Firebase Admin services, created lazily so every other module loads in plain `node --test`.
   Tests call deps.set({db, auth, bucket}) with in-memory fakes. */

let injected = null;
let app = null;
let dbReady = false;

function ensureApp() {
  if (!app) {
    const { initializeApp, getApps } = require("firebase-admin/app");
    app = getApps().length ? getApps()[0] : initializeApp();
  }
  return app;
}

module.exports = {
  set(fakes) { injected = fakes; },
  reset() { injected = null; },
  db() {
    if (injected && injected.db) return injected.db;
    ensureApp();
    const db = require("firebase-admin/firestore").getFirestore();
    if (!dbReady) {
      dbReady = true;
      try { db.settings({ ignoreUndefinedProperties: true }); } catch (e) { /* already configured */ }
    }
    return db;
  },
  auth() {
    if (injected && injected.auth) return injected.auth;
    ensureApp();
    return require("firebase-admin/auth").getAuth();
  },
  bucket() {
    if (injected && injected.bucket) return injected.bucket;
    ensureApp();
    return require("firebase-admin/storage").getStorage().bucket();
  },
  /** firebase-admin/storage getDownloadURL, or null when not available (tests). */
  getDownloadURL(file) {
    if (injected) return injected.getDownloadURL ? injected.getDownloadURL(file) : Promise.resolve(null);
    ensureApp();
    return require("firebase-admin/storage").getDownloadURL(file);
  },
};
