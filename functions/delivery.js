/* Little Hive House: when an order should arrive.
   One file for the site (window.LHHDelivery) and the emails (functions/delivery.js is an exact copy; a test keeps them equal).
   Business days skip weekends and the US federal holidays USPS keeps. Day 1 is the next business day after the order. */
(function (root, make) {
  if (typeof module === 'object' && module.exports) module.exports = make();
  else root.LHHDelivery = make();
})(this, function () {
  'use strict';
  var MAKE = [3, 5];      // printed, pressed and packed
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
  /* [earliest, latest] arrival. opts.shipped: it already left today; opts.country: 'CA' for Canada */
  function estimate(from, opts) {
    opts = opts || {};
    var ship = String(opts.country || 'US').toUpperCase() === 'CA' ? SHIP_CA : SHIP;
    var a = opts.shipped ? ship[0] : MAKE[0] + ship[0];
    var b = opts.shipped ? ship[1] : MAKE[1] + ship[1];
    return [addBusinessDays(from, a), addBusinessDays(from, b)];
  }
  /* "Nov 9–16", "Nov 28 – Dec 3", "Dec 29 – Jan 5" */
  function range(a, b) {
    var ma = MON[a.getUTCMonth()], mb = MON[b.getUTCMonth()];
    if (key(a) === key(b)) return ma + ' ' + a.getUTCDate();
    if (ma === mb && a.getUTCFullYear() === b.getUTCFullYear()) return ma + ' ' + a.getUTCDate() + '–' + b.getUTCDate();
    return ma + ' ' + a.getUTCDate() + ' – ' + mb + ' ' + b.getUTCDate();
  }
  function arrival(opts) {
    opts = opts || {};
    var e = estimate(opts.from || today(opts.tz, opts.now), opts);
    return range(e[0], e[1]);
  }
  return { MAKE: MAKE, SHIP: SHIP, SHIP_CA: SHIP_CA, holidays: holidays, workday: workday, addBusinessDays: addBusinessDays,
           today: today, estimate: estimate, range: range, arrival: arrival };
});
