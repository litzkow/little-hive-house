// Checks the Shippo key without showing it: CHECK=exists|live|accepted|usps. Exit 0 = OK.
"use strict";
const key = (process.env.SHIPPO_API_KEY || "").trim();
const check = process.env.CHECK;
(async () => {
  if (check === "exists") process.exit(key ? 0 : 1);
  if (check === "live") process.exit(/^shippo_live_/.test(key) ? 0 : 1);
  if (check === "test") process.exit(/^shippo_test_/.test(key) ? 0 : 1);
  if (check === "shippo") process.exit(/^shippo_/.test(key) ? 0 : 1);
  if (check === "quoted") process.exit(/^["']|["']$/.test(key) ? 0 : 1);
  if (check === "long") process.exit(key.length >= 30 ? 0 : 1);
  const res = await fetch("https://api.goshippo.com/carrier_accounts/?results=50", { headers: { Authorization: `ShippoToken ${key}` } });
  if (check === "accepted") process.exit(res.ok ? 0 : 1);
  const j = await res.json().catch(() => ({}));
  const usps = (j.results || []).filter((a) => /usps/i.test(a.carrier || "") && a.active !== false);
  console.log(`USPS accounts: ${usps.length}`);
  process.exit(usps.length ? 0 : 1);
})().catch((e) => { console.error(e.message); process.exit(1); });
