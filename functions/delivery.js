/* Little Hive House: when an order should arrive.
   One file for the site (window.LHHDelivery) and the emails (functions/delivery.js is an exact copy; a test keeps them equal).
   Making: we drop orders at the Post Office Monday to Saturday (not Sundays or the US federal holidays USPS keeps).
   An order placed by 5 pm Eastern goes out the next shipping day, a later one the day after; we promise one shipping day more.
   In the mail: USPS business days (Monday to Friday, no holidays). */
(function (root, make) {
  if (typeof module === 'object' && module.exports) module.exports = make();
  else root.LHHDelivery = make();
})(this, function () {
  'use strict';
  var MAKE = [1, 2];      // shipping days until it leaves: printed, pressed, packed and at the Post Office (one more after 5 pm)
  var CUTOFF = 17;        // 5 pm in the shop's time zone
  var TZ = 'America/New_York';
  var SHIP = [2, 5];      // USPS Ground Advantage, inside the US
  var SHIP_CA = [5, 15];  // USPS international to Canada (1 to 3 weeks)
  var MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  function U(y, m, d) { return new Date(Date.UTC(y, m, d)); }
  function key(t) { return t.toISOString().slice(0, 10); }
  function nth(y, m, wd, n) { var off = (wd - U(y, m, 1).getUTCDay() + 7) % 7; return U(y, m, 1 + off + 7 * (n - 1)); }
  function last(y, m, wd) { var e = U(y, m + 1, 0); return U(y, m, e.getUTCDate() - (e.getUTCDay() - wd + 7) % 7); }
  function observed(t) {
    var w = t.getUTCDay();
    return w === 6 ? U(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate() - 1) : w === 0 ? U(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate() + 1) : t;
  }
  var cache = {};
  function holidays(y) {
    if (cache[y]) return cache[y];
    var s = {};
    [observed(U(y, 0, 1)), nth(y, 0, 1, 3), nth(y, 1, 1, 3), last(y, 4, 1), observed(U(y, 5, 19)), observed(U(y, 6, 4)),
     nth(y, 8, 1, 1), nth(y, 9, 1, 2), observed(U(y, 10, 11)), nth(y, 10, 4, 4), observed(U(y, 11, 25)), observed(U(y + 1, 0, 1))]
      .forEach(function (t) { if (t.getUTCFullYear() === y) s[key(t)] = 1; });
    cache[y] = s;
    return s;
  }
  function workday(t) { var w = t.getUTCDay(); return w !== 0 && w !== 6 && !holidays(t.getUTCFullYear())[key(t)]; }
  /* a day we can drop packages at the Post Office: Monday to Saturday, no holidays */
  function shipday(t) { return t.getUTCDay() !== 0 && !holidays(t.getUTCFullYear())[key(t)]; }
  function addShipDays(t, n) {
    var d = U(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate());
    while (n > 0) { d = U(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() + 1); if (shipday(d)) n -= 1; }
    return d;
  }
  function addBusinessDays(t, n) {
    var d = U(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate());
    while (n > 0) { d = U(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() + 1); if (workday(d)) n -= 1; }
    return d;
  }
  /* today's calendar day in a time zone, as a UTC midnight date */
  function today(tz, now) {
    var d = now || new Date();
    if (!tz) return U(d.getFullYear(), d.getMonth(), d.getDate());
    var p = new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' }).format(d).split('-');
    return U(+p[0], +p[1] - 1, +p[2]);
  }
  /* was it ordered after the 5 pm cutoff (shop time)? */
  function late(now) {
    var d = now || new Date();
    var h = Number(new Intl.DateTimeFormat('en-US', { timeZone: TZ, hour: 'numeric', hourCycle: 'h23' }).format(d));
    return h >= CUTOFF;
  }
  /* [earliest, latest] day it leaves with USPS */
  function leaves(from, opts) {
    var extra = opts && opts.late ? 1 : 0;
    return [addShipDays(from, MAKE[0] + extra), addShipDays(from, MAKE[1] + extra)];
  }
  /* [earliest, latest] arrival. from = the order day; opts.late: ordered after 5 pm; opts.shipped: it already left that day;
     opts.country: 'CA' for Canada */
  function estimate(from, opts) {
    opts = opts || {};
    var ship = String(opts.country || 'US').toUpperCase() === 'CA' ? SHIP_CA : SHIP;
    if (opts.shipped) return [addBusinessDays(from, ship[0]), addBusinessDays(from, ship[1])];
    var out = leaves(from, opts);
    return [addBusinessDays(out[0], ship[0]), addBusinessDays(out[1], ship[1])];
  }
  /* the same, from a moment in time (the shop's day and the 5 pm cutoff) */
  function estimateAt(now, opts) {
    var d = now || new Date(), o = {};
    for (var k in (opts || {})) o[k] = opts[k];
    o.late = late(d);
    return estimate(today(TZ, d), o);
  }
  /* "Nov 9–16", "Nov 28 – Dec 3", "Dec 29 – Jan 5" */
  function range(a, b) {
    var ma = MON[a.getUTCMonth()], mb = MON[b.getUTCMonth()];
    if (key(a) === key(b)) return ma + ' ' + a.getUTCDate();
    if (ma === mb && a.getUTCFullYear() === b.getUTCFullYear()) return ma + ' ' + a.getUTCDate() + '–' + b.getUTCDate();
    return ma + ' ' + a.getUTCDate() + ' – ' + mb + ' ' + b.getUTCDate();
  }
  /* opts.from (a day, with opts.late) or opts.now (a moment, default now) */
  function arrival(opts) {
    opts = opts || {};
    var e = opts.from ? estimate(opts.from, opts) : estimateAt(opts.now, opts);
    return range(e[0], e[1]);
  }
  return { MAKE: MAKE, SHIP: SHIP, SHIP_CA: SHIP_CA, CUTOFF: CUTOFF, TZ: TZ, holidays: holidays, workday: workday, shipday: shipday,
           addBusinessDays: addBusinessDays, addShipDays: addShipDays, today: today, late: late, leaves: leaves, estimate: estimate,
           estimateAt: estimateAt, range: range, arrival: arrival };
});
