"use strict";
// The customer emails in Portuguese (order.lang / data.lang = "pt"); the owners' alerts stay in English.
const test = require("node:test");
const assert = require("node:assert/strict");
const E = require("..");
const { SAMPLES } = require("../sample-data");

test("an order in Portuguese gets its emails in Portuguese", () => {
  const r = E.render("order_confirmation", { ...SAMPLES.order_confirmation, order: { ...SAMPLES.order_confirmation.order, lang: "pt" } });
  assert.match(r.subject, /^Obrigado! O pedido LHH-1042 está confirmado$/);
  assert.match(r.html, /<html lang="pt-BR"/);
  assert.match(r.html, /O que acontece agora/);
  assert.match(r.text, /Frete: Grátis/);
  assert.doesNotMatch(r.html, /What happens next/);
});

test("data.lang works for emails without an order, and English stays the default", () => {
  assert.match(E.render("password_reset", { ...SAMPLES.password_reset, lang: "pt" }).subject, /Troque a sua senha/);
  assert.match(E.render("password_reset", SAMPLES.password_reset).subject, /^Reset your Little Hive House password$/);
  assert.match(E.render("order_confirmation", SAMPLES.order_confirmation).html, /What happens next/);
});

test("store alerts stay in English even for a Portuguese order", () => {
  const r = E.render("admin_new_order", { ...SAMPLES.admin_new_order, order: { ...SAMPLES.admin_new_order.order, lang: "pt" } });
  assert.match(r.html, /<html lang="en"/);
});

test("every customer email in Portuguese renders, with no English sentence left from our own text", () => {
  for (const sk of Object.keys(SAMPLES).filter((k) => !/^admin_/.test(k) && k !== "newsletter")) {
    const kind = E.KINDS.find((k) => sk === k || sk.startsWith(k + "_"));
    const r = E.render(kind, { ...SAMPLES[sk], lang: "pt" });
    assert.ok(r.subject && r.html && r.text, sk);
    assert.doesNotMatch(r.text, /\b(You're getting this email|Questions\? Just reply|What happens next|Track your package)\b/, sk);
  }
});
