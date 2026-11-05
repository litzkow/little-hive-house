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

test("arrival skips Sundays, weekends in the mail and US holidays (Veterans Day, Thanksgiving, Christmas, New Year)", () => {
  // ordered on a day: leaves in 1 to 2 shipping days (Mon to Sat), then 2 to 5 USPS business days
  assert.equal(D.arrival({ from: day(2026, 11, 2) }), "Nov 5–12");              // Veterans Day on the 11th
  assert.equal(D.arrival({ from: day(2026, 11, 20) }), "Nov 24 – Dec 1");      // Thanksgiving week
  assert.equal(D.arrival({ from: day(2026, 12, 22) }), "Dec 28 – Jan 4");      // Christmas and New Year
  assert.equal(D.arrival({ from: day(2026, 11, 2), shipped: true }), "Nov 4–9");
  assert.equal(D.arrival({ from: day(2026, 11, 2), country: "CA" }), "Nov 10–27");
  assert.ok(D.holidays(2027)["2027-07-05"], "July 4 on a Sunday is kept on Monday");
  assert.ok(D.holidays(2027)["2027-12-31"], "New Year 2028 on a Saturday is kept on Friday");
});

test("the 5 pm cutoff: before it, it leaves the next shipping day; after it, the day after; Saturday counts, Sunday doesn't", () => {
  const at = (s) => D.leaves(D.today(D.TZ, new Date(s)), { late: D.late(new Date(s)) }).map((t) => t.toISOString().slice(0, 10));
  assert.deepEqual(at("2026-11-05T15:00:00-05:00"), ["2026-11-06", "2026-11-07"]);   // Thursday 3 pm: Friday, Saturday at the latest
  assert.deepEqual(at("2026-11-05T17:30:00-05:00"), ["2026-11-07", "2026-11-09"]);   // Thursday 5:30 pm: Saturday, Monday at the latest
  assert.deepEqual(at("2026-11-06T20:00:00-05:00"), ["2026-11-09", "2026-11-10"]);   // Friday night: Monday
  assert.deepEqual(at("2026-11-08T10:00:00-05:00"), ["2026-11-09", "2026-11-10"]);   // Sunday: Monday
  assert.deepEqual(at("2026-11-10T16:59:00-05:00"), ["2026-11-12", "2026-11-13"]);   // the 11th is Veterans Day
  assert.equal(D.arrival({ now: new Date("2026-11-05T15:00:00-05:00") }), "Nov 10–16");
  assert.equal(D.arrival({ now: new Date("2026-11-05T20:00:00-05:00") }), "Nov 10–17");
  assert.equal(D.late(new Date("2026-11-05T21:59:00Z")), false);   // 4:59 pm Eastern
  assert.equal(D.late(new Date("2026-11-05T22:00:00Z")), true);    // 5:00 pm Eastern
});

test("emails: the confirmation shows the estimated arrival; the shipped email says when to expect it; the footer links shipping", () => {
  const E = require("../emails");
  const { SAMPLES } = require("../emails/sample-data");
  const c = E.render("order_confirmation", SAMPLES.order_confirmation), s = E.render("shipped", SAMPLES.shipped);
  assert.match(c.text, /Estimated arrival: Oct 1[0-9]–\d+/);
  assert.match(c.text, /shipping\.html/);
  assert.match(s.text, /expect it about Oct/);
});
