"use strict";
/* Conteúdo: a one-time key pair so videos can travel through the public repo locked. The private key stays in
   Firestore (settings/contentImportKey, which no client can read); the public key is printed (it's safe to show).
   import-content.js unlocks the files with it and then deletes it. */
const crypto = require("crypto");
const { Firestore } = require("@google-cloud/firestore");
const db = new Firestore({ projectId: process.env.PROJECT || "little-hive-house" });
(async () => {
  const { publicKey, privateKey } = crypto.generateKeyPairSync("rsa", { modulusLength: 3072 });
  await db.collection("settings").doc("contentImportKey").set({ pem: privateKey.export({ type: "pkcs8", format: "pem" }), at: new Date().toISOString() });
  const pub = publicKey.export({ type: "spki", format: "der" }).toString("base64");
  console.log(`::warning title=chave-publica::${pub}`);
})().catch((e) => { console.log(`::error::${e.message}`); process.exit(1); });
