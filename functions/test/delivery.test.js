"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");
const D = require("../delivery");

const day = (y, m, d) => new Date(Date.UTC(y, m - 1, d));

test("delivery.js is the same file as the site's assets/delivery.js", () => {
  assert.equal(fs.readFileSync(path.join(__dirname, "..", "delivery.js"), "utf8"), fs.readFileSync(path.join(__dirname, "..", "..", "assets", "delivery.js"), "utf8"));
});

test("arrival skips weekends and US holidays (Veterans Day, Thanksgiving, Christmas, New Year)", () => {
  assert.equal(D.arrival({ from: day(2026, 11, 2) }), "Nov 9–17");             // Veterans Day on the 11th
  assert.equal(D.arrival({ from: day(2026, 11, 20) }), "Nov 30 – Dec 7");      // Thanksgiving week
  assert.equal(D.arrival({ from: day(2026, 12, 22) }), "Dec 30 – Jan 7");      // Christmas and New Year
  assert.equal(D.arrival({ from: day(2026, 11, 2), shipped: true }), "Nov 4–9");
  assert.equal(D.arrival({ from: day(2026, 11, 2), country: "CA" }), "Nov 13 – Dec 2");
  assert.ok(D.holidays(2027)["2027-07-05"], "July 4 on a Sunday is kept on Monday");
  assert.ok(D.holidays(2027)["2027-12-31"], "New Year 2028 on a Saturday is kept on Friday");
});

test("emails: the confirmation shows the estimated arrival; the shipped email says when to expect it; the footer links shipping", () => {
  const E = require("../emails");
  const { SAMPLES } = require("../emails/sample-data");
  const c = E.render("order_confirmation", SAMPLES.order_confirmation), s = E.render("shipped", SAMPLES.shipped);
  assert.match(c.text, /Estimated arrival: Oct 1[0-9]–\d+/);
  assert.match(c.text, /shipping\.html/);
  assert.match(s.text, /expect it about Oct/);
});
