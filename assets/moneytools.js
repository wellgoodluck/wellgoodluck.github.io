/* The Money Traps tools (Nov 9, 2026; revised after review) and the payment tool (Nov 11): one script for five
   calculators, each mounted on <div class="mt-mount" data-tool="card|car|plan|match|rate">. Nothing the reader types is stored or sent; the page makes no
   requests. A link with the numbers is built only when the reader asks for one, and it carries them after "#", which
   browsers never send to a server. Styles: the shared calculator box (.rb, .ku layout) in assets/site.css, plus .mt. */
(function () {
  var mount = document.querySelector(".mt-mount");
  if (!mount) return;
  var which = mount.getAttribute("data-tool");
  var $ = function (id) { return document.getElementById(id); };
  var MAX = 1e8;   /* $100 million: the largest amount any box takes */

  /* ---------- formatting ---------- */
  function parse(v) { var s = String(v).replace(/[$,%\s]/g, ""); if (s === "") return null; var n = Number(s); return isFinite(n) ? n : NaN; }
  function money(v, cents) { var a = Math.abs(v), d = cents ? 2 : 0; return (v < 0 ? "−" : "") + "$" + a.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function cash(v) { return money(v, Math.round(v * 100) % 100 !== 0 && Math.abs(v) < 10000); }   /* cents only when they matter */
  function hundreds(v) { return money(Math.round(v / 100) * 100); }
  function num(v) { return v.toLocaleString("en-US", { maximumFractionDigits: 2 }); }
  function pc(v) { return num(v) + "%"; }
  function dur(m) {
    var y = Math.floor(m / 12), r = m % 12, a = [];
    if (y) a.push(y + (y === 1 ? " year" : " years"));
    if (r) a.push(r + (r === 1 ? " month" : " months"));
    return a.join(" and ") || "0 months";
  }
  function short(m) { var y = Math.floor(m / 12), r = m % 12; return (y ? y + " yr" + (y === 1 ? "" : "s") : "") + (y && r ? " " : "") + (r || !y ? r + " mo" : ""); }
  function andList(a) { return a.length < 2 ? a.join("") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1]; }
  /* "0.22" in a rate box is read as 0.22%; say so only when the hundredfold reading is a plausible rate */
  function decCheck(id, x, top) { var raw = $(id).value; return x > 0 && x < 1 && /\./.test(raw) && x * 100 <= top ? "Check: " + raw.trim() + " is read as " + num(x) + "%. For " + num(x * 100) + "%, type " + num(x * 100) + "." : ""; }

  /* ---------- markup helpers ---------- */
  /* f: id, key (share link), label, pre ("$") or post ("%"), hint, optional, ex (example value), name ("Still the example's: …"),
     dflt (a setting with a usual value, kept out of the example line) */
  function field(f) {
    var hint = f.hint ? '<span class="rb-hint" id="' + f.id + '-h">' + f.hint + "</span>" : "";
    return '<div class="rb-f"><label for="' + f.id + '" id="' + f.id + '-l">' + f.label + (f.optional ? ' <span class="rb-opt">(optional)</span>' : "") + "</label>" +
      '<span class="rb-in">' + (f.pre ? f.pre + " " : "") + '<input type="text" inputmode="decimal" id="' + f.id + '" class="' + (f.cls || "") + '" autocomplete="off">' + (f.post ? " " + f.post : "") + "</span>" + hint + "</div>";
  }
  function select(id, label, opts) {
    return '<div class="rb-f"><label for="' + id + '">' + label + '</label><select id="' + id + '">' +
      opts.map(function (o) { return '<option value="' + o[0] + '">' + o[1] + "</option>"; }).join("") + "</select></div>";
  }
  function row(dt, dd, sub) { return "<dt>" + dt + (sub ? '<span class="ku-sub">' + sub + "</span>" : "") + '</dt><dd><span class="rb-big">' + dd + "</span></dd>"; }
  function shell(h, form, notes) {
    return ['<section class="rb ku mt" aria-labelledby="mt-h">',
      '<h2 id="mt-h" class="ku-h">' + h + "</h2>",
      '<div id="mt-form">' + form + "</div>",
      '<div class="rb-sumwrap"><a class="rb-sum off" id="mt-sum" href="#mt-out"><span id="mt-sumt"></span> <span class="rb-sumgo">Details <span aria-hidden="true">↓</span></span></a></div>',
      '<div class="rb-out" id="mt-out" tabindex="-1">',
      '<p class="rb-ex" id="mt-ex" hidden></p>',
      '<p class="ku-lead" id="mt-lead"></p>',
      '<p class="rb-warn" id="mt-w" hidden></p>',
      '<div id="mt-res"></div>',
      '<p class="rb-err" id="mt-e" hidden></p>',
      '<p class="rb-dnote" id="mt-extra" hidden></p>',
      "</div>",
      '<p class="sr" aria-live="polite" id="mt-live"></p>',
      '<div class="ku-share" id="mt-share"><button type="button" class="rb-act" id="mt-copy">Copy a link with these numbers</button><span class="rb-hint">The link carries the numbers you typed, so anyone you send it to will see them.</span><p class="ku-copied" id="mt-copied" role="status"></p></div>',
      notes || "",
      "</section>"].join("\n");
  }

  /* ---------- the four tools ---------- */
  var T = {};

  /* 1. Paying off a card */
  T.card = {
    h: "Pay off a card balance",
    fields: [
      { id: "mt-bal", key: "b", label: "Balance", pre: "$", ex: 2000, name: "the balance", cls: "rb-wide" },
      { id: "mt-apr", key: "r", label: "Interest rate (APR)", post: "%", ex: 22.36, name: "the rate", hint: "On your statement, near the interest charges. Use the rate for purchases." },
      { id: "mt-pay", key: "p", label: "What you'd pay each month", pre: "$", ex: 100, name: "the monthly payment", optional: true, hint: "Leave it blank to see the minimum only." },
      { id: "mt-mp", key: "mp", label: "Percent of the balance", post: "%", ex: 1, name: "the minimum's percent", dflt: true },
      { id: "mt-mf", key: "mf", label: "At least", pre: "$", ex: 25, name: "the minimum's floor", dflt: true }
    ],
    form: function () {
      var F = this.fields;
      return field(F[0]) + field(F[1]) + field(F[2]) +
        '<details id="mt-more"><summary>More detail: your card\'s minimum payment</summary>' +
        '<p class="rb-note">The minimum here is that month\'s interest plus a percent of the balance, with a dollar floor, a common formula. Your card agreement gives your card\'s own.</p>' +
        '<div class="rb-pair">' + field(F[3]) + field(F[4]) + "</div></details>";
    },
    notes: '<p class="rb-note">This assumes no new charges, no fees and the same rate throughout. Interest is figured monthly at one-twelfth of the yearly rate; cards figure it daily, so your statement\'s numbers can differ a little.</p>',
    run: function (v) {
      var B = v["mt-bal"], apr = v["mt-apr"], pay = v["mt-pay"], pct = v["mt-mp"], floor = v["mt-mf"];
      if (B == null || !(B > 0) || B > MAX) return { err: "Enter the balance in dollars, up to $100 million.", f: "mt-bal" };
      if (apr == null || isNaN(apr) || apr < 0 || apr > 100) return { err: "Enter the rate as a yearly percent under 100, like 22.36.", f: "mt-apr" };
      if (isNaN(pay) || (pay != null && (pay <= 0 || pay > MAX))) return { err: "Enter the monthly payment in dollars, or leave it blank.", f: "mt-pay" };
      if (pct == null || isNaN(pct) || pct <= 0 || pct > 100) return { err: "Enter the minimum's percent of the balance, like 1.", f: "mt-mp", open: true };
      if (floor == null || isNaN(floor) || floor < 0 || floor > MAX) return { err: "Enter the minimum's dollar floor, like 25, or 0 for none.", f: "mt-mf", open: true };
      var r = apr / 100 / 12;
      function run(fixed) {
        var b = B, m = 0, I = 0, first = null;
        while (b > 0.005 && m < 1200) {
          var i = b * r, due = b + i, p = fixed == null ? Math.max(i + pct / 100 * b, floor) : fixed;
          p = Math.min(p, due); if (first == null) first = p;
          b = due - p; I += i; m++;
        }
        return { m: m, I: I, first: first, done: b <= 0.005, left: b };
      }
      var mn = run(null), w = decCheck("mt-apr", apr, 100), lead, sum;
      var minTime = mn.done ? dur(mn.m) : "not paid off in 100 years";
      var rows = row("Paying only the minimum", minTime, (mn.done ? (r ? money(mn.I) + " in interest · " : "") + money(B + mn.I) + " in all · " : money(mn.left) + " still owed after 100 years · ") + "first minimum " + cash(mn.first));
      if (pay != null) {
        var i0 = B * r;
        if (pay <= i0) return { err: "At " + cash(pay) + " a month the balance never goes down: the first month's interest alone is " + cash(i0) + ". Enter more than that.", f: "mt-pay" };
        if (pay < mn.first - 0.005) return { err: cash(pay) + " is less than the first minimum payment, " + cash(mn.first) + ". Enter at least that.", f: "mt-pay" };
        var fx = run(pay), saveI = mn.I - fx.I, saveM = mn.m - fx.m;
        rows += row("Paying " + cash(pay) + " a month", dur(fx.m), (r ? money(fx.I) + " in interest · " : "") + money(B + fx.I) + " in all");
        lead = "Paying " + cash(pay) + " a month, you'd be done in " + dur(fx.m) + (r ? " and pay " + money(fx.I) + " in interest" : "");
        if (!mn.done) lead += ". Paying only the minimum, the card wouldn't be paid off in 100 years.";
        else if (saveM > 0) lead += r ? ", " + money(saveI) + " less than paying only the minimum, and " + dur(saveM) + " sooner." : ", " + dur(saveM) + " sooner than paying only the minimum.";
        else lead += ".";
        sum = cash(pay) + " a month: " + short(fx.m) + (r ? " · " + money(fx.I) + " interest" : "");
      } else {
        lead = mn.done ? "Paying only the minimum, you'd be done in " + dur(mn.m) + (r ? " and pay " + money(mn.I) + " in interest." : ".")
          : "Paying only the minimum, the card wouldn't be paid off in 100 years.";
        sum = "Minimum only: " + (mn.done ? short(mn.m) + (r ? " · " + money(mn.I) + " interest" : "") : "not paid off in 100 years");
      }
      return { lead: lead, sum: sum, res: '<dl class="rb-res">' + rows + "</dl>", warn: w, spoken: lead,
        extra: 'The <a href="../articles/credit-card-minimum-payments.html">minimum payment box</a> on your statement shows your card issuer\'s own estimate of paying only the minimum.' };
    }
  };

  /* 2. A car loan by length */
  T.car = {
    h: "Compare loan lengths",
    fields: [
      { id: "mt-price", key: "c", label: "Price, with any taxes and fees you'd finance", pre: "$", ex: 35000, name: "the price", cls: "rb-wide", hint: "If you owe more on a trade-in than it's worth, add the difference here." },
      { id: "mt-down", key: "d", label: "Down payment and trade-in", pre: "$", ex: null, name: "the down payment", optional: true, cls: "rb-wide" },
      { id: "mt-apr", key: "r", label: "Interest rate (APR)", post: "%", ex: 6.9, name: "the rate", hint: "From the offer you have, or your bank or credit union." }
    ],
    form: function () { var F = this.fields; return field(F[0]) + field(F[1]) + field(F[2]); },
    notes: '<p class="rb-note">Payments are the standard monthly loan payment at the rate shown, with no extra fees. A dealer\'s quote can differ by a few dollars.</p>',
    run: function (v) {
      var P = v["mt-price"], D = v["mt-down"] == null ? 0 : v["mt-down"], a = v["mt-apr"];
      if (P == null || !(P > 0) || P > MAX) return { err: "Enter the price in dollars, up to $100 million.", f: "mt-price" };
      if (isNaN(D) || D < 0) return { err: "Enter the down payment in dollars, or leave it blank.", f: "mt-down" };
      if (D >= P) return { err: "The down payment covers the whole price, so there's nothing to borrow.", f: "mt-down" };
      if (a == null || isNaN(a) || a < 0 || a > 40) return { err: "Enter the rate as a yearly percent under 40, like 6.9.", f: "mt-apr" };
      var L = P - D, r = a / 100 / 12, out = [];
      [48, 60, 72, 84].forEach(function (n) {
        var p = r ? L * r / (1 - Math.pow(1 + r, -n)) : L / n;
        var owe = function (k) { return k >= n ? 0 : r ? L * Math.pow(1 + r, k) - p * (Math.pow(1 + r, k) - 1) / r : L - p * k; };
        out.push({ n: n, p: p, I: p * n - L, o5: Math.max(owe(60), 0) });
      });
      var t = '<div class="table-scroll"><table class="rb-t"><caption class="sr">The loan at four lengths</caption><thead><tr><th>Loan length</th><th>Monthly payment</th><th>Total interest</th><th>Still owed after 5 years</th></tr></thead><tbody>' +
        out.map(function (o) { return "<tr><td>" + o.n / 12 + " years</td><td class=\"rb-tbill\">" + money(o.p) + "</td><td>" + money(o.I) + "</td><td>" + money(o.o5) + "</td></tr>"; }).join("") +
        "</tbody></table></div>";
      /* differences from the rounded table figures, so the sentence matches the table */
      var f = out[1], s = out[3], dp = Math.round(f.p) - Math.round(s.p), dI = Math.round(s.I) - Math.round(f.I);
      var lead = (L === P ? "" : "Borrowing " + money(L) + ". ") + "The 7-year loan's payment is " + money(dp) + " a month less than the 5-year loan's" + (r ? ", and it costs " + money(dI) + " more in interest." : ".");
      return { lead: lead, sum: "7 years vs. 5: " + money(dp) + " a month less" + (r ? " · " + money(dI) + " more interest" : ""), res: t, warn: decCheck("mt-apr", a, 40),
        spoken: lead + " After five years you'd still owe " + money(s.o5) + " on the 7-year loan.",
        extra: "After five years you'd still owe " + money(s.o5) + " on the 7-year loan. A new car has <a href=\"https://tflcar.com/2026/03/used-car-depreciation-five-years-iseecars-study/\">typically lost around 40% of its value</a> by then." };
    }
  };

  /* 3. What a payment plan costs */
  var LATER = { 52: "A week later", 26: "Two weeks later", 24: "Half a month later", 12: "A month later" };
  T.plan = {
    h: "Add up a payment plan",
    kinds: {
      rto: { b: "Rent-to-own", amt: "Price if you bought it today", nm: "the price", ex: { "mt-amt": 612, "mt-pmt": 38.99, "mt-n": 48 }, freq: "52", first: "0", hint: "The store's cash price, or what the same item costs elsewhere." },
      payday: { b: "Payday loan", amt: "Cash you get", nm: "the cash you get", ex: { "mt-amt": 300, "mt-pmt": 345, "mt-n": 1 }, freq: "26", first: "1", hint: "A payday loan is usually one payment, the loan plus the fee, on your next payday." },
      bnpl: { b: "Pay in 4", amt: "Price", nm: "the price", ex: { "mt-amt": 180, "mt-pmt": 45, "mt-n": 4 }, freq: "26", first: "0", hint: "Pay-in-4 plans usually take the first payment at checkout." },
      other: { b: "Something else", amt: "Price, or the cash you get", nm: "the price", ex: { "mt-amt": 1000, "mt-pmt": 95, "mt-n": 12 }, freq: "12", first: "1", hint: "Any plan of equal payments: a loan, a lease or an installment plan." }
    },
    fields: [
      { id: "mt-amt", key: "a", label: "Price if you bought it today", pre: "$", name: "the price", cls: "rb-wide" },
      { id: "mt-pmt", key: "p", label: "Each payment", pre: "$", name: "the payment" },
      { id: "mt-n", key: "n", label: "Number of payments", name: "the number of payments" }
    ],
    selects: [{ id: "mt-freq", key: "f", name: "how often" }, { id: "mt-first", key: "s", name: "the first payment" }],
    form: function () {
      var F = this.fields, K = this.kinds;
      return '<div class="rb-seg ku-kinds" role="group" aria-label="What kind of plan?">' +
        Object.keys(K).map(function (k, i) { return '<button type="button" data-k="' + k + '" aria-pressed="' + (i === 0) + '">' + K[k].b + "</button>"; }).join("") +
        '</div><p class="rb-hint" id="mt-kh"></p>' +
        field(F[0]) + '<div class="rb-pair">' + field(F[1]) + field(F[2]) + "</div>" +
        '<div class="rb-pair">' + select("mt-freq", "How often", [["52", "Every week"], ["26", "Every two weeks"], ["24", "Twice a month"], ["12", "Every month"]]) +
        select("mt-first", "First payment", [["0", "When you get it"], ["1", "A week later"]]) + "</div>";
    },
    notes: '<p class="rb-note">The yearly rate is the annual percentage rate a loan with these payments would carry, figured close to the method in the federal disclosure rules and counting everything above the price as the cost of borrowing. Rent-to-own and some paycheck apps usually aren\'t treated as loans under federal law, so they don\'t have to show a rate.</p>',
    run: function (v) {
      var A = v["mt-amt"], p = v["mt-pmt"], n = v["mt-n"], per = +$("mt-freq").value, today = $("mt-first").value === "0", K = this.kinds[kind];
      var what = K.nm.replace(/^the /, "");
      if (A == null || !(A > 0) || A > MAX) return { err: "Enter the " + what + " in dollars, up to $100 million.", f: "mt-amt" };
      if (p == null || !(p > 0) || p > MAX) return { err: "Enter the amount of each payment, in dollars.", f: "mt-pmt" };
      if (n == null || !(n >= 1) || n !== Math.floor(n) || n > 600) return { err: "Enter the number of payments as a whole number, like 48.", f: "mt-n" };
      var tot = p * n, extra = tot - A, times = tot / A, rate = null, why = "", rs;
      var fin = A - (today ? p : 0), m = today ? n - 1 : n;
      /* a single payment two weeks (or a week) out: the rate's period is the loan's term in days, as the disclosure rules do */
      var yr = m === 1 && n === 1 && (per === 26 || per === 52) ? 365 / (per === 26 ? 14 : 7) : per;
      if (m === 0) why = "with one payment when you get it, there's no time to put a rate on";
      else if (fin <= 0) why = "the first payment covers the price, so there's no loan to put a rate on";
      else if (Math.abs(extra) < 0.005) rate = 0;
      else {
        var f = function (r) { var s = 0; for (var k = 1; k <= m; k++) s += p / Math.pow(1 + r, k); return s - fin; };
        var lo = -0.99, hi = 50;
        if (f(hi) > 0) rate = Infinity;
        else { for (var it = 0; it < 200; it++) { var mid = (lo + hi) / 2; if (f(mid) > 0) lo = mid; else hi = mid; } rate = (lo + hi) / 2 * yr; }
      }
      if (rate === null) rs = "–";
      else if (rate === Infinity || rate > 10) rs = "more than 1,000%";
      else if (Math.abs(rate) < 0.0005) rs = "0%";
      else if (rate < 0) rs = "below 0%";
      else rs = rate >= 1 ? Math.round(rate * 100).toLocaleString("en-US") + "%" : (rate * 100).toFixed(1) + "%";
      var forWhat = kind === "payday" ? "for " + cash(A) + " in cash" : "for something priced at " + cash(A), lead;
      if (Math.abs(extra) < 0.005) lead = "You'd pay " + cash(tot) + " " + forWhat + ": nothing extra for paying over time.";
      else if (extra < 0) lead = "You'd pay " + cash(tot) + " " + forWhat + ", " + cash(-extra) + " less than the " + what + ".";
      else lead = "You'd pay " + cash(tot) + " " + forWhat + ", " + cash(extra) + " more" + (times >= 1.95 ? ", about " + num(Math.round(times * 10) / 10) + " times as much." : ".") +
        (rate != null && rate > 0 ? " As a yearly rate, that's " + (rs.indexOf("more") === 0 ? rs : "about " + rs) + "." : "");
      var share = Math.round(Math.abs(extra) / A * 100);
      var rows = row("Total you'd pay", cash(tot), n + (n === 1 ? " payment" : " payments") + " of " + cash(p)) +
        row("Extra over the " + what, extra < 0 ? "−" + cash(-extra) : cash(extra), Math.abs(extra) < 0.005 ? "" : (extra < 0 ? "−" : "") + share.toLocaleString("en-US") + "% of the " + what) +
        row("Yearly rate it works out to", rs, rate == null ? why : "as an annual percentage rate (APR)");
      var weeks = m * 52 / per, span = weeks < 1 ? "" : weeks < 9 ? Math.round(weeks) + (Math.round(weeks) === 1 ? " week" : " weeks") : dur(Math.round(weeks * 12 / 52));
      var ext = !span ? "" : (kind === "rto" ? "You'd own it after about " + span + "." : "Paid off in about " + span + ".");
      return { lead: lead, sum: cash(tot) + " in all · " + cash(extra) + " extra" + (rate != null && rate > 0 ? " · " + rs + " a year" : ""), res: '<dl class="rb-res">' + rows + "</dl>", spoken: lead, extra: ext };
    }
  };

  /* 4. The employer match */
  T.match = {
    h: "Check your match",
    fields: [
      { id: "mt-sal", key: "s", label: "Yearly pay", pre: "$", ex: 45000, name: "the pay", cls: "rb-wide" },
      { id: "mt-a1", key: "m1", label: "Adds this share of what you put in", post: "%", ex: 50, name: "the match rate", desc: "mt-fh" },
      { id: "mt-l1", key: "u1", label: "On up to this share of your pay", post: "%", ex: 6, name: "the match limit", desc: "mt-fh" },
      { id: "mt-a2", key: "m2", label: "Then adds this share", post: "%", ex: null, name: "the second step's rate", optional: true },
      { id: "mt-l2", key: "u2", label: "On the next share of your pay", post: "%", ex: null, name: "the second step's limit", optional: true },
      { id: "mt-c", key: "c", label: "Share of your pay you put in", post: "%", ex: 3, name: "what you put in" },
      { id: "mt-age", key: "g", label: "Your age now", ex: 25, name: "the age" },
      { id: "mt-ret", key: "t", label: "Retire at", ex: 65, name: "the retirement age" },
      { id: "mt-ret6", key: "x", label: "Yearly return", post: "%", ex: 6, name: "the return", hint: "An assumption, not a promise. Real returns go up and down." }
    ],
    form: function () {
      var F = this.fields;
      return field(F[0]) +
        '<fieldset class="ku-when"><legend>Your employer\'s match</legend><p class="rb-hint" id="mt-fh">Your plan\'s summary or your HR site gives the formula, often as "50% of the first 6%".</p>' +
        '<div class="rb-pair">' + field(F[1]) + field(F[2]) + "</div>" +
        '<details id="mt-more"><summary>A second step, if your plan has one</summary><p class="rb-note">Some plans match in two steps, such as 100% of the first 3% of pay and 50% of the next 2%.</p>' +
        '<div class="rb-pair">' + field(F[3]) + field(F[4]) + "</div></details></fieldset>" +
        '<fieldset class="ku-when"><legend>What you put in</legend>' + field(F[5]) + "</fieldset>" +
        '<fieldset class="ku-when"><legend>What a missed match could grow to</legend><div class="rb-pair">' + field(F[6]) + field(F[7]) + "</div>" + field(F[8]) + "</fieldset>";
    },
    notes: '<p class="rb-note">Growth assumes the same amount each year, invested at the start of each year at the return shown, with no taxes or fees. Matching money may not be yours right away: if it vests all at once, a plan can make you wait up to three years; if it vests a bit each year, up to six.</p>',
    run: function (v) {
      var S = v["mt-sal"], a1 = v["mt-a1"], l1 = v["mt-l1"], a2 = v["mt-a2"], l2 = v["mt-l2"], c = v["mt-c"];
      if (S == null || !(S > 0) || S > MAX) return { err: "Enter your yearly pay in dollars, up to $100 million.", f: "mt-sal" };
      if (a1 == null || isNaN(a1) || a1 < 0 || a1 > 200) return { err: "Enter the match as a percent of what you put in, like 50.", f: "mt-a1" };
      if (l1 == null || isNaN(l1) || l1 <= 0 || l1 > 100) return { err: "Enter how much of your pay the match covers, like 6.", f: "mt-l1" };
      var two = a2 != null || l2 != null;
      if (two && (a2 == null || isNaN(a2) || a2 < 0 || a2 > 200)) return { err: "Enter the second step's match as a percent, like 50, or leave both boxes blank.", f: "mt-a2", open: true };
      if (two && (l2 == null || isNaN(l2) || l2 <= 0 || l1 + l2 > 100)) return { err: "Enter how much more of your pay the second step covers, like 2, or leave both boxes blank.", f: "mt-l2", open: true };
      if (c == null || isNaN(c) || c < 0 || c > 100) return { err: "Enter what you put in as a percent of your pay, like 3 (or 0).", f: "mt-c" };
      if (!two) { a2 = 0; l2 = 0; }
      var mf = function (x) { return S * (a1 / 100 * Math.min(x, l1) + a2 / 100 * Math.min(Math.max(x - l1, 0), l2)) / 100; };
      var full = l1 + l2, got = mf(c), max = mf(full), miss = max - got, you = S * c / 100;
      var w = decCheck("mt-a1", a1, 200) || decCheck("mt-l1", l1, 100) || decCheck("mt-c", c, 100) ||
        (you > 24500 ? "Check: " + money(you) + " is more than the 2026 limit on your own contributions, $24,500 (higher if you're 50 or older)." : "");
      var rows = row("You put in", money(you), pc(c) + " of " + money(S)) + row("Your employer adds", money(got)) +
        row("The full match", money(max), "if you put in " + pc(full) + " or more") + row("Left behind each year", money(miss));
      var lead, grow = "", extra = "", soft = null, sum;
      if (max <= 0) { lead = "With these settings your employer adds nothing."; sum = "No match with these settings"; }
      else if (miss < 0.5) { lead = "You're getting the full match: " + money(got) + " a year from your employer."; sum = "Full match: " + money(got) + " a year"; extra = "The growth boxes are used only when part of the match is left behind."; }
      else {
        lead = "You're leaving " + money(miss) + " a year of your employer's match behind. Putting in " + pc(full) + " of your pay would get all of it.";
        sum = money(miss) + " a year left behind";
        var need = S * full / 100;
        extra = "Putting in " + pc(full) + " of " + money(S) + " is " + money(need) + " a year, about " + money(need / 26) + " a paycheck if you're paid every two weeks.";
        var age = v["mt-age"], ret = v["mt-ret"], g = v["mt-ret6"];
        if (age == null || isNaN(age) || age < 14 || age > 90 || age !== Math.floor(age)) soft = { err: "To see what it could grow to, enter your age now as a whole number, like 25.", f: "mt-age" };
        else if (ret == null || isNaN(ret) || ret !== Math.floor(ret) || ret <= age || ret > 100) soft = { err: "To see what it could grow to, enter a retirement age older than your age now, like 65.", f: "mt-ret" };
        else if (g == null || isNaN(g) || g < 0 || g > 20) soft = { err: "To see what it could grow to, enter a yearly return between 0 and 20 percent, like 6.", f: "mt-ret6" };
        else {
          var n = ret - age, r = g / 100, fv = r ? miss * (Math.pow(1 + r, n) - 1) / r * (1 + r) : miss * n;
          rows += row("What that could grow to", "about " + hundreds(fv), money(miss) + " a year from " + age + " to " + ret + " at " + pc(g) + " a year, in future dollars");
          grow = " Invested from " + age + " to " + ret + " at " + pc(g) + " a year, it could grow to about " + hundreds(fv) + ".";
          extra += " The growth is in future dollars: prices will rise too, so it would buy less than that sum does today.";
        }
      }
      return { lead: lead, sum: sum, res: '<dl class="rb-res">' + rows + "</dl>", warn: w, spoken: lead + grow, extra: extra, soft: soft };
    }
  };


  /* 5. What a rate change does to a payment (Nov 11). The starting rates are Freddie Mac's weekly averages, written onto
     the mount by tools/build_articles.py (data-r30, data-y30, data-r15, data-y15, data-week), so the page still makes no
     requests. The loan-length switch appears only when the 15-year average is there. */
  var RD = (function () {
    var g = function (k) { var x = parseFloat(mount.getAttribute(k)); return isFinite(x) && x > 0 ? x : null; };
    return { 30: { r: g("data-r30"), y: g("data-y30") }, 15: { r: g("data-r15"), y: g("data-y15") }, wk: mount.getAttribute("data-week") || "" };
  })();
  function rate2(x) { return x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 3 }) + "%"; }   /* 6.5 prints as 6.50% */
  function pmt(L, a, n) { var r = a / 1200; return r ? L * r / (1 - Math.pow(1 + r, -n)) : L / n; }
  function carries(p, a, n) { var r = a / 1200; return r ? p * (1 - Math.pow(1 + r, -n)) / r : p * n; }
  T.rate = {
    h: "Your loan at this rate, and a point either side",
    fields: [
      { id: "mt-hp", key: "h", label: "Home price", pre: "$", ex: 400000, name: "the home price", cls: "rb-wide" },
      { id: "mt-dn", key: "d", label: "Down payment", ex: 20, name: "the down payment",
        say: function (x) { return $("mt-du").value === "p" ? pc(x) : cash(x); },
        post: '<select id="mt-du" aria-label="Down payment in percent or in dollars"><option value="p">% of the price</option><option value="d">dollars</option></select>' },
      { id: "mt-rt", key: "r", label: "Interest rate", post: "%", ex: RD[30].r, name: "the rate", say: rate2, hint: "The yearly rate on the loan." }
    ],
    selects: [{ id: "mt-du", key: "u", name: "percent or dollars" }].concat(RD[15].r ? [{ id: "mt-term", key: "t", name: "the loan length" }] : []),
    form: function () {
      var F = this.fields;
      return field(F[0]) + field(F[1]) + (RD[15].r ? select("mt-term", "Loan length", [["30", "30 years"], ["15", "15 years"]]) : "") + field(F[2]);
    },
    notes: '<p class="rb-note">This is principal and interest only. It leaves out property tax, homeowner\'s insurance, mortgage insurance and any homeowners\' association dues, which are usually collected with the payment. It is arithmetic, not a quote or advice; a lender\'s offer depends on your credit, the loan type and the points you pay.</p>',
    term: function () { var el = $("mt-term"); return el ? Number(el.value) : 30; },
    init: function (calc) {
      var F = this.fields, me = this, cur = 30;
      /* keep: the numbers came from a link, so the rate box is left alone */
      me.sync = function (keep) {
        var t = me.term(), held = parse($("mt-rt").value) === RD[cur].r;   /* the rate follows the loan length only while it is still the average */
        F[2].ex = RD[t].r; cur = t;
        if (RD[t].r && RD.wk) $("mt-rt-h").textContent = "Starts at Freddie Mac's average for a " + t + "-year fixed loan, week ending " + RD.wk + ".";
        if (held && !keep && RD[t].r) $("mt-rt").value = RD[t].r.toFixed(2);
        calc();
      };
      if ($("mt-term")) $("mt-term").addEventListener("change", function () { me.sync(false); });
    },
    run: function (v) {
      var P = v["mt-hp"], d = v["mt-dn"], a = v["mt-rt"], pctDown = $("mt-du").value === "p", t = this.term(), n = t * 12;
      if (P == null || !(P > 0) || P > MAX) return { err: "Enter the home price in dollars, up to $100 million.", f: "mt-hp" };
      if (d == null) d = 0;
      if (isNaN(d) || d < 0) return { err: "Enter the down payment, or leave it blank for none.", f: "mt-dn" };
      var D = pctDown ? P * d / 100 : d;
      if (D >= P) return { err: "The down payment covers the whole price, so there's nothing to borrow.", f: "mt-dn" };
      if (a == null || isNaN(a) || a < 0 || a > 25) return { err: "Enter the rate as a yearly percent under 25, like " + (RD[t].r || 7).toFixed(2) + ".", f: "mt-rt" };
      var L = P - D, p = pmt(L, a, n), lo = a - 1, hi = a + 1, isAvg = a === RD[t].r;
      var lead = "On a " + t + "-year loan of " + money(L) + ", principal and interest at " + rate2(a) + " is about " + money(p) + " a month.";
      var rows = "", say = "";
      if (lo >= 0) { rows += row("One point lower, at " + rate2(lo), money(pmt(L, lo, n)) + " a month"); say += " One point lower, at " + rate2(lo) + ", it would be about " + money(pmt(L, lo, n)) + "."; }
      rows += row("One point higher, at " + rate2(hi), money(pmt(L, hi, n)) + " a month"); say += " One point higher, at " + rate2(hi) + ", about " + money(pmt(L, hi, n)) + ".";
      if (isAvg && RD[t].y) rows += row("At the average a year ago, " + rate2(RD[t].y), money(pmt(L, RD[t].y, n)) + " a month");
      var same = "The same " + money(p) + " a month would carry a loan of about " + hundreds(carries(p, hi, n)) + " at " + rate2(hi) +
        (lo >= 0 ? " and about " + hundreds(carries(p, lo, n)) + " at " + rate2(lo) : "") + ".";
      var total = a > 0 ? "Over " + t + " years, interest at " + rate2(a) + " adds up to about " + hundreds(p * n - L) + ", on top of the " + money(L) + " borrowed." : "";
      var w = [decCheck("mt-rt", a, 25)];
      if (D < 0.2 * P) w.push("With less than 20% down, a conventional loan usually requires mortgage insurance, which this figure leaves out.");
      return { lead: lead, sum: t + " years at " + rate2(a) + ": " + money(p) + " a month",
        res: '<dl class="rb-res">' + rows + '</dl><p class="rb-dnote">' + same + "</p>" + (total ? '<p class="rb-dnote">' + total + "</p>" : ""),
        warn: w.filter(Boolean).join(" "), spoken: lead + say };
    }
  };

  /* ---------- wiring ---------- */
  var Tool = T[which];
  if (!Tool) return;
  var kind = Tool.kinds ? Object.keys(Tool.kinds)[0] : null, timer = null, lastEx = "", applied = "";
  mount.innerHTML = shell(Tool.h, Tool.form(), Tool.notes);
  var SEL = Tool.selects || [];
  /* each box is described by its own hint, plus any shared hint (the kind hint, the match formula hint) */
  Tool.fields.forEach(function (f) { f.desc0 = [f.hint ? f.id + "-h" : "", f.desc || "", Tool.kinds && f.id === "mt-amt" ? "mt-kh" : ""].join(" ").trim(); });
  function exOf(f) { return Tool.kinds ? (Tool.kinds[kind].ex[f.id] != null ? Tool.kinds[kind].ex[f.id] : null) : f.ex; }
  function nameOf(f) { return Tool.kinds && f.id === "mt-amt" ? Tool.kinds[kind].nm : f.name; }
  function show(id, v) { $(id).value = v == null ? "" : Number(v).toLocaleString("en-US", { maximumFractionDigits: 2 }); }
  function holdsEx(f) { var x = parse($(f.id).value), e = exOf(f); return e == null ? x === null : x === e; }
  function laterLabel() { var o = $("mt-first"); if (o) o.options[1].textContent = LATER[$("mt-freq").value]; }
  function setKind(k) {
    var K0 = Tool.kinds[kind], stale = Tool.fields.filter(holdsEx), fq = $("mt-freq").value === K0.freq, fs = $("mt-first").value === K0.first;
    kind = k; var K = Tool.kinds[k];
    [].forEach.call(mount.querySelectorAll(".ku-kinds button"), function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-k") === k)); });
    $("mt-amt-l").textContent = K.amt; $("mt-kh").textContent = K.hint;
    stale.forEach(function (f) { show(f.id, exOf(f)); });
    if (fq) $("mt-freq").value = K.freq;          /* each setting follows the new kind only if it still held the old kind's */
    if (fs) $("mt-first").value = K.first;
    laterLabel(); calc();
  }
  function exState() {
    var ex = Tool.fields.filter(function (f) { return !f.dflt; });
    var left = ex.filter(function (f) { return exOf(f) != null && holdsEx(f); });
    var blanks = ex.filter(function (f) { return exOf(f) == null; }).every(holdsEx);
    var sel = !Tool.kinds || ($("mt-freq").value === Tool.kinds[kind].freq && $("mt-first").value === Tool.kinds[kind].first);
    var all = left.length === ex.filter(function (f) { return exOf(f) != null; }).length && blanks && sel;
    return { all: all, left: left.map(function (f) { return nameOf(f) + " (" + (f.say ? f.say(exOf(f)) : f.pre ? cash(exOf(f)) : f.post ? pc(exOf(f)) : exOf(f)) + ")"; }) };
  }
  function mark(R) { var el = $(R.f); el.setAttribute("aria-invalid", "true"); el.setAttribute("aria-describedby", ((el.getAttribute("aria-describedby") || "") + " mt-e").trim()); if (R.open && $("mt-more")) $("mt-more").open = true; }
  function calc() {
    var v = {};
    Tool.fields.forEach(function (f) { v[f.id] = parse($(f.id).value); var el = $(f.id); el.removeAttribute("aria-invalid"); if (f.desc0) el.setAttribute("aria-describedby", f.desc0); else el.removeAttribute("aria-describedby"); });
    var R = Tool.run.call(Tool, v), ex = exState(), exEl = $("mt-ex");
    var exKey = ex.all ? "all" : ex.left.join("|");
    exEl.hidden = !exKey; exEl.innerHTML = ex.all ? "<strong>These are the example's figures.</strong> Replace them with yours." : exKey ? "<strong>Still the example's:</strong> " + andList(ex.left) + "." : "";
    var e = $("mt-e");
    if (R.err) {
      e.hidden = false; e.textContent = "! " + R.err; mark(R);
      $("mt-lead").hidden = true; $("mt-res").innerHTML = ""; $("mt-extra").hidden = true; $("mt-w").hidden = true; $("mt-share").hidden = true;
      $("mt-sumt").textContent = "No result yet: " + R.err; announce(R.err); place(); return;
    }
    e.hidden = !R.soft; e.textContent = R.soft ? "! " + R.soft.err : ""; if (R.soft) mark(R.soft);   /* a problem in an optional part keeps the main answer */
    $("mt-share").hidden = false; $("mt-copied").textContent = "";
    $("mt-lead").hidden = false; $("mt-lead").textContent = R.lead;
    $("mt-w").hidden = !R.warn; $("mt-w").textContent = R.warn || "";
    $("mt-res").innerHTML = R.res;
    $("mt-extra").hidden = !R.extra; $("mt-extra").innerHTML = R.extra || "";
    $("mt-sumt").textContent = (ex.all ? "Example: " : "") + R.sum;
    var exSay = exKey !== lastEx && exKey && exKey !== "all" ? " Still the example's: " + andList(ex.left) + "." : "";
    lastEx = exKey;
    announce((ex.all ? "Example figures. " : "") + R.spoken + (R.warn ? " " + R.warn : "") + (R.soft ? " " + R.soft.err : "") + exSay);
    place();
  }
  function announce(t) { clearTimeout(timer); timer = setTimeout(function () { $("mt-live").textContent = t; }, 700); }
  var queued = false;
  function place() {
    if (queued) return; queued = true;
    requestAnimationFrame(function () {
      queued = false;
      var H = window.innerHeight, top = $("mt-h").getBoundingClientRect().top, stuck = $("mt-sum").parentNode.getBoundingClientRect().top >= H - 1;
      $("mt-sum").classList.toggle("off", !(top < H - 90 && stuck));
    });
  }
  window.addEventListener("scroll", place, { passive: true });
  window.addEventListener("resize", place);
  $("mt-sum").addEventListener("click", function (ev) { ev.preventDefault(); $("mt-out").scrollIntoView({ block: "start" }); $("mt-out").focus({ preventScroll: true }); });

  /* share links: "#k=rto&a=612&p=38.99…" (the kind, if any, then each box by its key); a link with only a kind keeps that kind's examples */
  function link() {
    var parts = Tool.kinds ? ["k=" + kind] : [];
    Tool.fields.forEach(function (f) { var x = parse($(f.id).value); if (x != null && !isNaN(x)) parts.push(f.key + "=" + x); });
    SEL.forEach(function (s) { parts.push(s.key + "=" + $(s.id).value); });
    return location.href.split("#")[0] + "#" + parts.join("&");
  }
  function fromHash() {
    var raw = location.hash; if (!raw || raw === applied || raw === "#mt-out") return false;
    applied = raw;
    var h = {};
    try { raw.replace(/^#/, "").split("&").forEach(function (p) { var kv = p.split("="); if (kv[0]) h[kv[0]] = decodeURIComponent(kv[1] || ""); }); } catch (err) { return false; }
    var any = Tool.fields.some(function (f) { return h[f.key] != null; });
    if (Tool.kinds && Object.prototype.hasOwnProperty.call(Tool.kinds, h.k) && h.k !== kind) setKind(h.k);
    if (!any) return Tool.kinds && h.k != null;
    Tool.fields.forEach(function (f) { var x = Number(h[f.key]); $(f.id).value = h[f.key] != null && h[f.key] !== "" && isFinite(x) ? x.toLocaleString("en-US", { maximumFractionDigits: 6 }) : ""; });
    SEL.forEach(function (s) { var o = $(s.id); if (h[s.key] != null && [].some.call(o.options, function (x) { return x.value === h[s.key]; })) o.value = h[s.key]; });
    laterLabel();
    return true;
  }
  window.addEventListener("hashchange", function () { if (fromHash()) { if (Tool.sync) Tool.sync(true); else calc(); } });
  $("mt-copy").addEventListener("click", function () {
    var u = link(), out = $("mt-copied");
    var fallback = function () { out.innerHTML = '<label for="mt-link">Copy this link:</label> <input type="text" id="mt-link" readonly>'; $("mt-link").value = u; $("mt-link").focus(); $("mt-link").select(); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(u).then(function () { out.textContent = "Link copied."; }, fallback);
    else fallback();
  });

  Tool.fields.forEach(function (f) { $(f.id).addEventListener("input", calc); });
  SEL.forEach(function (s) { $(s.id).addEventListener("change", function () { if (s.id === "mt-freq") laterLabel(); calc(); }); });
  if (Tool.kinds) {
    [].forEach.call(mount.querySelectorAll(".ku-kinds button"), function (b) { b.addEventListener("click", function () { setKind(b.getAttribute("data-k")); }); });
    var K0 = Tool.kinds[kind]; $("mt-amt-l").textContent = K0.amt; $("mt-kh").textContent = K0.hint; $("mt-freq").value = K0.freq; $("mt-first").value = K0.first;
  }
  Tool.fields.forEach(function (f) { show(f.id, exOf(f)); });
  laterLabel();
  if (Tool.init) Tool.init(calc);                                  /* Nov 11: a tool can set itself up once its boxes exist */
  var linked = fromHash(); if (Tool.sync) Tool.sync(linked); else calc(); clearTimeout(timer);
})();
