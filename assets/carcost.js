/* "What Does It Cost to Own a Car?" (Nov 19, 2026). Mounted on <div class="cc-mount" data-tool="own">. Six yearly costs,
   the ones AAA's Your Driving Costs study counts. With no price, the value lost and the loan interest are AAA's 2026
   averages for the type; insurance, maintenance and fees start at AAA's averages; fuel starts at the national prices
   tools/build_articles.py writes onto the mount (data-gas, data-el, with their dates) and the efficiency AAA's own fuel
   figures imply. Nothing the reader types is stored or sent; the page makes no requests. A link with the numbers is
   built only when the reader asks, with them after "#". Styles: the shared calculator box (.rb, .ku, .mt) plus .cc. */
(function () {
  var mount = document.querySelector(".cc-mount");
  if (!mount) return;
  var $ = function (id) { return document.getElementById(id); };
  var attr = function (k) { var x = parseFloat(mount.getAttribute(k)); return isFinite(x) && x > 0 ? x : null; };

  /* AAA, Your Driving Costs 2026, per year at 15,000 miles over five years: value lost (d), finance charges (f),
     insurance (i), fuel (u, at $4.152 a gallon and 18¢ a kWh), maintenance, repairs and tires (m), license, registration
     and taxes (t), and AAA's total. Due for AAA's 2027 study (September 2027). */
  var AAA = {
    sedan: { gas: [3330, 897, 1704, 2215, 1827, 609, 10582], ev: [6786, 1441, 2070, 712.5, 1602, 1051, 13662], hyb: [3739, 1016, 1706, 1436, 1619, 689, 10204] },
    csuv: { gas: [3568, 933, 2188, 2382, 1954, 631, 11656], ev: [5298, 1208, 2277, 771, 1402, 931, 11888], hyb: [3845, 1087, 2294, 1731, 1506, 739, 11201] },
    msuv: { gas: [5052, 1235, 2423, 3066, 1829, 827, 14431], ev: [7077, 1440, 2070, 909, 1784, 1052, 14332], hyb: [4822, 1412, 2534, 2087, 1902, 940, 13698] },
    pick: { gas: [6446, 1601, 2139, 3598, 1788, 1054, 16626], ev: [8624, 2149, 2294, 1222, 1618, 1507, 17414], hyb: [6370, 1730, 2178, 3153, 1539, 1148, 16117] }
  };
  var AAA_GAS = 4.152, AAA_EL = 0.18, AAA_MI = 15000;
  var TYPES = [["sedan", "Sedan", "sedan"], ["csuv", "Compact SUV", "compact SUV"], ["msuv", "Mid-size SUV", "mid-size SUV"], ["pick", "Pickup", "pickup"]];
  var POWERS = [["gas", "Gas", "gas"], ["hyb", "Hybrid", "hybrid"], ["ev", "Electric", "electric"]];
  var LOSS5 = { gas: 0.42, hyb: 0.35, ev: 0.57 };                 /* iSeeCars, value lost in five years */
  var FAST = 54, SAVE = 4;                                        /* public fast charging, ¢ a kWh (Paren, mid-2026); savings rate, % */
  var GAS = attr("data-gas"), GASW = mount.getAttribute("data-gasw") || "", EL = attr("data-el"), ELM = mount.getAttribute("data-elm") || "";
  var APR = attr("data-apr") || 7.54, APRM = mount.getAttribute("data-aprm") || "August 2026";
  var GAS0 = GAS || Math.round(AAA_GAS * 100) / 100, EL0 = EL || AAA_EL * 100;
  var EX = { a: { t: "csuv", p: "gas" }, b: { t: "csuv", p: "ev" } };
  var timer = null, lastEx = "", applied = "", hasB = true;

  /* ---------- formatting ---------- */
  function parse(v) { var s = String(v).replace(/[$,%¢\s]/g, ""); if (s === "") return null; var n = Number(s); return isFinite(n) ? n : NaN; }
  function money(v) { return (v < 0 ? "−" : "") + "$" + Math.abs(Math.round(v)).toLocaleString("en-US"); }
  function tens(v) { return money(Math.round(v / 10) * 10); }
  function num(v, d) { return v.toLocaleString("en-US", { maximumFractionDigits: d == null ? 2 : d }); }
  function andList(a) { return a.length < 2 ? a.join("") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1]; }
  function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
  function ice(p) { return p !== "ev"; }
  function typeOf(c) { return $("cc-" + c + "-t").value; }
  function powerOf(c) { return $("cc-" + c + "-p").value; }
  function noun(t) { return TYPES.filter(function (x) { return x[0] === t; })[0][2]; }
  function adj(p) { return POWERS.filter(function (x) { return x[0] === p; })[0][2]; }
  function nameOf(c) { return $("cc-" + c + "-n").value.trim(); }
  function ref(c) { return nameOf(c) || (c === "a" ? "Car A" : "Car B"); }
  function what(c) { return adj(powerOf(c)) + " " + noun(typeOf(c)); }
  function subject(c) { var n = nameOf(c); return n ? cap(n) : (powerOf(c) === "ev" ? "An " : "A ") + what(c); }

  /* ---------- starting figures ---------- */
  function eff(t, p) { var u = AAA[t][p][3], x = AAA_MI / (u / (ice(p) ? AAA_GAS : AAA_EL)); return ice(p) ? Math.round(x * 10) / 10 : Math.round(x * 100) / 100; }
  function dflt(c, f) {
    var t = typeOf(c), p = powerOf(c), A = AAA[t][p], price = parse($("cc-" + c + "-c").value), yrs = parse($("cc-yr").value);
    switch (f) {
      case "e": return eff(t, p);
      case "g": return ice(p) ? GAS0 : EL0;
      case "s": return 0;
      case "f": return FAST;
      case "i": return A[2];
      case "m": return A[4];
      case "x": return A[5];
      case "w": return price > 0 && yrs > 0 ? Math.round(price * Math.pow(1 - LOSS5[p], yrs / 5)) : null;
      case "d": return price > 0 ? Math.round(price * 0.1) : null;
      case "r": return APR;
    }
    return null;
  }
  var FILL = ["e", "g", "s", "f", "i", "m", "x", "w", "d", "r"];
  function held(c) { var out = {}; FILL.forEach(function (f) { var x = parse($("cc-" + c + "-" + f).value), d = dflt(c, f); out[f] = d == null ? x === null : x === d; }); return out; }
  function refill(c, h, force) { FILL.forEach(function (f) { if (h[f] || (force && force.indexOf(f) >= 0)) put("cc-" + c + "-" + f, dflt(c, f)); }); }
  function put(id, v) { $(id).value = v == null ? "" : num(Number(v)); }

  /* ---------- markup ---------- */
  function fld(id, label, o) {
    o = o || {};
    return '<div class="rb-f" id="' + id + '-f"' + (o.hidden ? " hidden" : "") + '><label for="' + id + '" id="' + id + '-l">' + label + (o.optional ? ' <span class="rb-opt">(optional)</span>' : "") + "</label>" +
      '<span class="rb-in">' + (o.pre ? '<span id="' + id + '-pre">' + o.pre + "</span> " : "") + '<input type="text"' + (o.text ? "" : ' inputmode="decimal"') + ' id="' + id + '" class="' + (o.cls || "") + '" autocomplete="off"' + (o.hint ? ' aria-describedby="' + id + '-h"' : "") + ">" + (o.post ? ' <span id="' + id + '-post">' + o.post + "</span>" : "") + "</span>" +
      (o.hint ? '<span class="rb-hint" id="' + id + '-h">' + o.hint + "</span>" : "") + "</div>";
  }
  function sel(id, label, opts) {
    return '<div class="rb-f"><label for="' + id + '">' + label + '</label><select id="' + id + '">' + opts.map(function (o) { return '<option value="' + o[0] + '">' + o[1] + "</option>"; }).join("") + "</select></div>";
  }
  function carBox(c) {
    var p = "cc-" + c + "-", L = c === "a" ? "Car A" : "Car B";
    return '<fieldset class="cc-car" id="cc-' + c + '"><legend id="' + p + 'lg">' + L + "</legend>" +
      fld(p + "n", "Name", { optional: true, text: true, cls: "cc-name", hint: 'Such as "the gas one". Shown as ' + L + " if blank." }) +
      '<div class="rb-pair">' + sel(p + "t", "Type", TYPES) + sel(p + "p", "Runs on", POWERS) + "</div>" +
      fld(p + "c", "Price before sales tax and fees", { pre: "$", optional: true, cls: "rb-wide", hint: "Leave blank to use AAA's averages for the value it loses and loan interest." }) +
      '<div class="cc-price" id="' + p + 'pd" hidden>' +
      fld(p + "w", "Worth when you sell it (estimate)", { pre: "$", cls: "rb-wide", hint: "The starting estimate uses five-year averages: 42% lost for cars overall, 35% for hybrids, 57% for electric cars." }) +
      fld(p + "d", "Down payment and trade-in", { pre: "$", cls: "rb-wide" }) +
      '<div class="rb-pair">' + fld(p + "r", "Loan rate (APR)", { post: "%" }) +
      sel(p + "l", "Loan length", [["36", "36 months"], ["48", "48 months"], ["60", "60 months"], ["72", "72 months"], ["84", "84 months"], ["0", "Paying cash"]]) + "</div>" +
      '<span class="rb-hint" id="' + p + 'rh">On your loan offer. The average for a 60-month new-car loan at banks was ' + num(APR) + "% in " + APRM + ".</span></div>" +
      fld(p + "e", "Miles per gallon", { hint: "Your car's rating, or what you get." }) +
      fld(p + "g", "Price of a gallon", { pre: "$", hint: "National average." }) +
      fld(p + "s", "Share charged at public fast chargers", { post: "%", hint: "Without a place to plug in at home, this could be most of it." }) +
      fld(p + "f", "Fast-charging price, cents per kWh", { post: "¢", hint: "About 54¢ in mid-2026." }) +
      fld(p + "i", "Insurance a year", { pre: "$", hint: "Your premium if you have it. Starts at AAA's average." }) +
      fld(p + "m", "Maintenance, repairs and tires a year", { pre: "$", hint: "Starts at AAA's average." }) +
      fld(p + "x", "Taxes, registration and fees a year", { pre: "$", hint: "Sales tax at purchase spread over the years, plus yearly registration. Some states add a yearly fee for electric cars." }) +
      (c === "b" ? '<button type="button" class="rb-act rb-rm" id="cc-rm">Remove this car</button>' : '<button type="button" class="rb-act rb-rm" id="cc-add" hidden>Compare with a second car</button>') +
      "</fieldset>";
  }
  mount.innerHTML = ['<section class="rb ku mt cc" aria-labelledby="cc-h">',
    '<h2 id="cc-h" class="ku-h">Add up what a car costs a year</h2>',
    '<div class="rb-pair mt-pair2">' + fld("cc-mi", "Miles a year", { hint: "AAA's figures assume 15,000." }) + fld("cc-yr", "Years you'll keep it") + "</div>",
    '<div class="cc-cars">' + carBox("a") + carBox("b") + "</div>",
    '<p class="rb-note">Starting figures are national averages. Replace any you know.</p>',
    '<div class="rb-sumwrap"><a class="rb-sum off" id="cc-sum" href="#cc-out"><span id="cc-sumt"></span> <span class="rb-sumgo">Details <span aria-hidden="true">↓</span></span></a></div>',
    '<div class="rb-out" id="cc-out" tabindex="-1">',
    '<p class="rb-ex" id="cc-ex" hidden></p>',
    '<p class="ku-lead" id="cc-lead"></p>',
    '<p class="rb-warn" id="cc-w" hidden></p>',
    '<p class="rb-err" id="cc-e" hidden></p>',
    '<div id="cc-res"></div>',
    "</div>",
    '<p class="sr" aria-live="polite" id="cc-live"></p>',
    '<div class="ku-share" id="cc-share"><button type="button" class="rb-act" id="cc-copy">Copy a link with these numbers</button><span class="rb-hint">The link carries the numbers you typed, so anyone you send it to will see them.</span><p class="ku-copied" id="cc-copied" role="status"></p></div>',
    "</section>"].join("\n");

  /* labels and boxes that follow what the car runs on, whether it has a price, and the fast-charging share */
  function layout(c) {
    var p = "cc-" + c + "-", pw = powerOf(c), price = parse($(p + "c").value), cash = $(p + "l").value === "0", share = parse($(p + "s").value);
    $(p + "pd").hidden = !(price > 0);
    $(p + "d-f").hidden = cash; $(p + "r-f").hidden = cash; $(p + "rh").hidden = cash;
    $(p + "e-l").textContent = ice(pw) ? "Miles per gallon" : "Miles per kilowatt-hour";
    $(p + "e-h").textContent = ice(pw) ? "Your car's rating, or what you get." : "On the window sticker as kWh per 100 miles: divide 100 by it.";
    $(p + "g-l").textContent = ice(pw) ? "Price of a gallon" : "Electricity price, cents per kWh";
    $(p + "g-pre").hidden = !ice(pw);
    $(p + "g-h").textContent = ice(pw) ? (GAS ? "National average, " + GASW + "." : "AAA's study price.") : (EL ? "National average, " + ELM + ". Your bill's total divided by its kWh gives yours." : "AAA's study price. Your bill's total divided by its kWh gives yours.");
    $(p + "s-f").hidden = ice(pw);
    $(p + "f-f").hidden = ice(pw) || !(share > 0);
    $(p + "lg").textContent = (c === "a" ? "Car A" : "Car B") + (nameOf(c) ? ": " + nameOf(c) : "");
  }
  function addPost(c) {                                           /* "¢" after the electricity price */
    var g = $("cc-" + c + "-g"), s = g.parentNode, post = $("cc-" + c + "-g-post2");
    if (!post) { post = document.createElement("span"); post.id = "cc-" + c + "-g-post2"; post.textContent = " ¢"; s.appendChild(post); }
    post.hidden = ice(powerOf(c));
  }

  /* ---------- the arithmetic ---------- */
  function interest(L, apr, n, keep) {
    if (!(L > 0) || !(n > 0)) return { i: 0, owed: 0 };
    var r = apr / 1200, pay = r ? L * r / (1 - Math.pow(1 + r, -n)) : L / n, bal = L, I = 0;
    for (var k = 0; k < Math.min(n, keep); k++) { var it = bal * r; I += it; bal = bal + it - pay; }
    return { i: I, owed: n > keep ? Math.max(bal, 0) : 0 };
  }
  function oneCar(c, miles, yrs) {
    var p = "cc-" + c + "-", g = function (f) { return parse($(p + f).value); };
    var t = typeOf(c), pw = powerOf(c), A = AAA[t][pw], price = g("c"), e = g("e"), fp = g("g"), share = g("s"), fast = g("f");
    var ins = g("i"), mt = g("m"), fee = g("x"), n = Number($(p + "l").value), out = { c: c, t: t, p: pw, aaa: {} };
    if (isNaN(price) || (price != null && (price <= 0 || price > 5e5))) return { err: "Enter the price in dollars, up to $500,000, or leave it blank.", f: p + "c" };
    if (price > 0) {
      var w = g("w"), d = g("d"), r = g("r");
      if (w == null || isNaN(w) || w < 0 || w >= price) return { err: "Enter what it'll be worth when you sell it, less than the price.", f: p + "w" };
      if (n > 0) {
        if (d == null) d = 0;
        if (isNaN(d) || d < 0 || d > price) return { err: "Enter the down payment and trade-in, from $0 up to the price.", f: p + "d" };
        if (r == null || isNaN(r) || r < 0 || r > 30) return { err: "Enter the loan rate as a yearly percent from 0 to 30, like 7.5.", f: p + "r" };
      } else d = price;
      var lo = n > 0 ? interest(price - d, r, n, yrs * 12) : { i: 0, owed: 0 };
      out.dep = (price - w) / yrs; out.fin = lo.i / yrs; out.price = price; out.worth = w; out.down = d; out.cash = !(n > 0); out.n = n; out.owed = lo.owed;
    } else { out.dep = A[0]; out.fin = A[1]; out.aaa.dep = out.aaa.fin = true; }
    if (ice(pw)) {
      if (e == null || isNaN(e) || e <= 0) return { err: "Enter miles per gallon, like 30.", f: p + "e" };
      if (fp == null || isNaN(fp) || fp <= 0 || fp > 50) return { err: "Enter the price of a gallon in dollars, like 3.80.", f: p + "g" };
      out.fuel = miles / e * fp; out.per = miles / e;              /* gallons a year: each $1 a gallon */
    } else {
      if (e == null || isNaN(e) || e <= 0) return { err: "Enter miles per kilowatt-hour, like 3.5.", f: p + "e" };
      if (fp == null || isNaN(fp) || fp <= 0 || fp > 500) return { err: "Enter the electricity price in cents, like 19.", f: p + "g" };
      if (share == null) share = 0;
      if (isNaN(share) || share < 0 || share > 100) return { err: "Enter the share at public fast chargers as a percent from 0 to 100.", f: p + "s" };
      if (share > 0 && (fast == null || isNaN(fast) || fast <= 0 || fast > 500)) return { err: "Enter the fast-charging price in cents, like 54.", f: p + "f" };
      var kwh = miles / e;
      out.fuel = kwh * ((1 - share / 100) * fp + share / 100 * (share > 0 ? fast : 0)) / 100; out.per = kwh / 10;   /* each 10¢ a kWh */
      out.share = share; out.kwh = kwh;
    }
    if (ins == null || isNaN(ins) || ins < 0) return { err: "Enter insurance a year in dollars, or 0.", f: p + "i" };
    if (mt == null || isNaN(mt) || mt < 0) return { err: "Enter maintenance a year in dollars, or 0.", f: p + "m" };
    if (fee == null || isNaN(fee) || fee < 0) return { err: "Enter taxes and fees a year in dollars, or 0.", f: p + "x" };
    out.ins = ins; out.mt = mt; out.fee = fee;
    out.aaa.ins = ins === A[2]; out.aaa.mt = mt === A[4]; out.aaa.fee = fee === A[5];
    out.rows = [Math.round(out.dep), Math.round(out.fin), Math.round(ins), Math.round(out.fuel), Math.round(mt), Math.round(fee)];
    out.total = out.rows.reduce(function (a, b) { return a + b; }, 0);
    out.y10 = Math.round(out.total / 10) * 10;
    var w1 = [];
    if (ice(pw) && e > 70) w1.push("Check: " + num(e) + " miles per gallon is above any gas or hybrid car's rating. For a plug-in hybrid, this tool can't split the miles; try it once as Electric and once as Gas.");
    if (!ice(pw) && e > 6) w1.push("Check: " + num(e) + " miles per kilowatt-hour is above any electric car's rating. If your sticker says 28 kWh per 100 miles, enter 100 ÷ 28, about 3.6.");
    if (ice(pw) && (fp < 1 || fp > 10)) w1.push("Check: $" + num(fp) + " a gallon is far from any U.S. average. Is that the price you meant?");
    if (!ice(pw) && (fp < 5 || fp > 80)) w1.push("Check: " + num(fp) + "¢ a kilowatt-hour is far from any U.S. average. Is that the price you meant?");
    out.warn = w1;
    return out;
  }
  var CAT = ["the value the car loses", "loan interest", "insurance", "fuel or charging", "maintenance, repairs and tires", "taxes, registration and fees"];
  function run() {
    var miles = parse($("cc-mi").value), yrs = parse($("cc-yr").value);
    if (miles == null || isNaN(miles) || miles < 1000 || miles > 100000) return { err: "Enter the miles you drive a year, from 1,000 to 100,000.", f: "cc-mi" };
    if (yrs == null || isNaN(yrs) || yrs < 1 || yrs > 20 || yrs !== Math.floor(yrs)) return { err: "Enter the years you'll keep it as a whole number from 1 to 20.", f: "cc-yr" };
    var cars = [oneCar("a", miles, yrs)];
    if (cars[0].err) return cars[0];
    if (hasB) { cars.push(oneCar("b", miles, yrs)); if (cars[1].err) return cars[1]; }
    var A = cars[0], B = cars[1], Y = yrs + (yrs === 1 ? " year" : " years");
    var lead = subject("a") + " costs about " + money(A.y10) + " a year to own and drive: about " + money(A.y10 / 12) + " a month, or " + Math.round(A.y10 / miles * 100) + "¢ a mile.";
    if (B) {
      var dy = B.y10 - A.y10;
      lead += " " + subject("b") + " costs about " + money(B.y10) + " a year, " + (Math.abs(dy) < 100 ? "about the same as " + ref("a") + "." : "about " + money(Math.abs(dy)) + " " + (dy > 0 ? "more" : "less") + " than " + ref("a") + ", or about " + money(Math.abs(dy) * yrs) + " over " + Y + ".");
    }
    /* the table */
    var head = "<th></th>" + cars.map(function (x) { return "<th>" + esc(ref(x.c)) + ": " + what(x.c) + "</th>"; }).join("");
    var note = function (on) { return on ? '<span class="rb-tsub">AAA average</span>' : ""; };
    var body = ["Value it loses", "Loan interest", "Insurance", "Fuel or charging", "Maintenance, repairs and tires", "Taxes, registration and fees"].map(function (lab, i) {
      var k = ["dep", "fin", "ins", null, "mt", "fee"][i];
      return "<tr><td>" + lab + "</td>" + cars.map(function (x) { return "<td>" + money(x.rows[i]) + note(k && x.aaa[k]) + "</td>"; }).join("") + "</tr>";
    }).join("") +
      '<tr class="mr-tot"><td>Total a year</td>' + cars.map(function (x) { return "<td>" + money(x.total) + "</td>"; }).join("") + "</tr>" +
      "<tr><td>A month</td>" + cars.map(function (x) { return "<td>" + money(x.total / 12) + "</td>"; }).join("") + "</tr>" +
      "<tr><td>A mile</td>" + cars.map(function (x) { return "<td>" + Math.round(x.total / miles * 100) + "¢</td>"; }).join("") + "</tr>";
    var t = '<div class="table-scroll"><table class="rb-t cc-t"><caption class="rb-tcap">A year, line by line</caption><thead><tr>' + head + "</tr></thead><tbody>" + body + "</tbody></table></div>";
    /* lines under the table */
    var L2 = [], big = cars.map(function (x) { var i = x.rows.indexOf(Math.max.apply(null, x.rows)); return { i: i, v: x.rows[i] }; });
    if (!B) L2.push("The biggest cost is " + CAT[big[0].i] + ": about " + tens(big[0].v) + " a year.");
    else if (big[0].i === big[1].i) L2.push("The biggest cost for both is " + CAT[big[0].i] + ": about " + tens(big[0].v) + " a year for " + esc(ref("a")) + " and " + tens(big[1].v) + " for " + esc(ref("b")) + ".");
    else L2.push("The biggest cost for " + esc(ref("a")) + " is " + CAT[big[0].i] + ", about " + tens(big[0].v) + " a year; for " + esc(ref("b")) + " it's " + CAT[big[1].i] + ", about " + tens(big[1].v) + ".");
    var share = function (x) { return Math.round(x.rows[3] / x.total * 100) + "%"; };
    L2.push(B ? "Fuel or charging is " + share(A) + " of " + esc(ref("a")) + "'s total and " + share(B) + " of " + esc(ref("b")) + "'s." : "Fuel or charging is " + share(A) + " of the total.");
    L2.push(cars.map(function (x, i) {
      var unit = ice(x.p) ? "Each $1 on a gallon" : "Each 10¢ on a kilowatt-hour";
      return unit + " changes " + esc(ref(x.c)) + "'s " + (i === 0 ? "fuel cost by about " + tens(x.per) + " a year." : "by about " + tens(x.per) + ".");
    }).join(" "));
    cars.forEach(function (x) {
      if (!ice(x.p) && !(x.share > 0)) L2.push("Charged entirely at public fast chargers at " + FAST + "¢ a kilowatt-hour, " + esc(ref(x.c)) + "'s charging would cost about " + tens(x.kwh * FAST / 100) + " a year instead of " + money(x.rows[3]) + ".");
    });
    var bits = [], seen = {};
    cars.forEach(function (x) {
      var k = x.t + x.p; if (seen[k]) return; seen[k] = 1;
      var same = cars.length > 1 && cars[0].t === cars[1].t && bits.length;
      bits.push((same ? "" : "a new " + noun(x.t) + " at ") + money(AAA[x.t][x.p][6]) + (same ? "" : " a year") + " " + (x.p === "gas" ? "on gas" : x.p === "ev" ? "electric" : "as a hybrid"));
    });
    var anyIce = cars.some(function (x) { return ice(x.p); }), anyEv = cars.some(function (x) { return !ice(x.p); });
    L2.push("AAA's 2026 study puts " + bits.join(" and ") + ", at 15,000 miles a year and its own fuel prices (" + [anyIce ? "$4.15 a gallon" : "", anyEv ? "18¢ a kilowatt-hour" : ""].filter(Boolean).join(" and ") + ").");
    cars.forEach(function (x) {
      if (!x.price || !(x.owed > 0)) return;
      var who = B ? "When you sell " + esc(ref(x.c)) + " after " + Y : "When you sell after " + Y;
      L2.push(who + ", about " + tens(x.owed) + " of the " + x.n + "-month loan would still be owed, " + (x.owed > x.worth ? "more than its estimated value of about " + tens(x.worth) + "." : "against an estimated value of about " + tens(x.worth) + "."));
    });
    cars.forEach(function (x) {
      if (!x.price || !(x.down > 0)) return;
      var earn = x.down * (Math.pow(1 + SAVE / 100, yrs) - 1);
      L2.push("Not counted above: " + (B ? esc(ref(x.c)) + "'s " : "the ") + money(x.down) + (x.cash ? " paid in cash" : " down payment") + " could have earned about " + tens(earn) + " in " + Y + " at " + SAVE + "% in savings, about " + tens(earn / yrs) + " a year.");
    });
    var warn = [];
    if (miles > 50000) warn.push("Check: " + num(miles, 0) + " miles a year is about " + ["", "", "two", "three", "four", "five", "six"][Math.min(6, Math.round(miles / 15000))] + " times the average. AAA's maintenance figures assume 15,000.");
    cars.forEach(function (x) { warn = warn.concat(x.warn); });
    return { lead: lead, res: t + L2.map(function (s) { return '<p class="rb-dnote">' + s + "</p>"; }).join(""), warn: warn.join(" "), cars: cars,
      sum: cars.map(function (x) { return esc(ref(x.c)) + " about " + money(x.y10) + (x.c === "a" ? " a year" : ""); }).join(" · ") };
  }
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;"); }

  /* ---------- the example line ---------- */
  function exState() {
    var parts = [], all = parse($("cc-mi").value) === 15000 && parse($("cc-yr").value) === 5 && hasB;
    var cars = hasB ? ["a", "b"] : ["a"], lists = {}, prices = [];
    cars.forEach(function (c) {
      var h = held(c), items = [], blankPrice = parse($("cc-" + c + "-c").value) === null;
      if (blankPrice) items.push("value lost", "loan interest");
      if (h.i) items.push("insurance"); if (h.m) items.push("maintenance"); if (h.x) items.push("fees");
      lists[c] = items;
      if (!h.e || !h.g || !blankPrice || !h.i || !h.m || !h.x || nameOf(c) || typeOf(c) !== EX[c].t || powerOf(c) !== EX[c].p || (!ice(powerOf(c)) && !h.s)) all = false;
      if (h.g) prices.push(ice(powerOf(c)) ? "gas" : "electricity");
    });
    if (all) return { all: true };
    if (cars.length > 1 && lists.a.join() === lists.b.join() && lists.a.length) parts.push("AAA's averages for both cars' " + andList(lists.a));
    else cars.forEach(function (c) { if (lists[c].length) parts.push("AAA's averages for " + esc(ref(c)) + "'s " + andList(lists[c])); });
    prices = prices.filter(function (x, i) { return prices.indexOf(x) === i; });
    if (prices.length) parts.push("the national " + andList(prices) + (prices.length > 1 ? " prices" : " price"));
    if (parse($("cc-mi").value) === 15000) parts.push("the miles (15,000)");
    if (parse($("cc-yr").value) === 5) parts.push("the years (5)");
    return { all: false, left: parts };
  }

  /* ---------- wiring ---------- */
  function clearMarks() { [].forEach.call(mount.querySelectorAll("input[aria-invalid]"), function (el) { el.removeAttribute("aria-invalid"); var d = (el.getAttribute("aria-describedby") || "").replace(/\s*cc-e\b/, "").trim(); if (d) el.setAttribute("aria-describedby", d); else el.removeAttribute("aria-describedby"); }); }
  function calc() {
    ["a", "b"].forEach(function (c) { layout(c); addPost(c); });
    $("cc-b").hidden = !hasB; $("cc-add").hidden = hasB;
    clearMarks();
    var R = run(), ex = exState(), exEl = $("cc-ex"), e = $("cc-e");
    var exKey = ex.all ? "all" : ex.left.join("|");
    exEl.hidden = !exKey; exEl.innerHTML = ex.all ? "<strong>These are AAA's averages and national prices.</strong> Replace them with yours." : exKey ? "<strong>Still the example's:</strong> " + ex.left.join("; ") + "." : "";
    if (R.err) {
      var el = $(R.f);
      e.hidden = false; e.textContent = "! " + R.err;
      el.setAttribute("aria-invalid", "true"); el.setAttribute("aria-describedby", ((el.getAttribute("aria-describedby") || "") + " cc-e").trim());
      $("cc-lead").hidden = true; $("cc-res").innerHTML = ""; $("cc-w").hidden = true; $("cc-share").hidden = true;
      $("cc-sumt").textContent = "No result yet: " + R.err; announce(R.err); place(); return;
    }
    e.hidden = true; $("cc-share").hidden = false; $("cc-copied").textContent = "";
    $("cc-lead").hidden = false; $("cc-lead").textContent = R.lead;
    $("cc-w").hidden = !R.warn; $("cc-w").textContent = R.warn;
    $("cc-res").innerHTML = R.res;
    $("cc-sumt").innerHTML = (ex.all ? "Example: " : "") + R.sum;
    var exSay = exKey !== lastEx && exKey && exKey !== "all" ? " Still the example's: " + ex.left.join("; ") + "." : "";
    lastEx = exKey;
    announce((ex.all ? "Example figures. " : "") + R.lead + (R.warn ? " " + R.warn : "") + exSay);
    place();
  }
  function announce(t) { clearTimeout(timer); timer = setTimeout(function () { $("cc-live").textContent = t.replace(/&amp;/g, "&").replace(/&lt;/g, "<"); }, 700); }
  var queued = false;
  function place() {
    if (queued) return; queued = true;
    requestAnimationFrame(function () {
      queued = false;
      var H = window.innerHeight, top = $("cc-h").getBoundingClientRect().top, stuck = $("cc-sum").parentNode.getBoundingClientRect().top >= H - 1;
      $("cc-sum").classList.toggle("off", !(top < H - 90 && stuck));
    });
  }
  window.addEventListener("scroll", place, { passive: true });
  window.addEventListener("resize", place);
  $("cc-sum").addEventListener("click", function (ev) { ev.preventDefault(); $("cc-out").scrollIntoView({ block: "start" }); $("cc-out").focus({ preventScroll: true }); });

  /* a change to the type, the power, the price or the years refills only the boxes still holding their starting figure;
     switching between gas and electric resets the efficiency and price, whose units change */
  var snap = {};
  function before() { ["a", "b"].forEach(function (c) { snap[c] = held(c); }); }
  mount.addEventListener("focusin", function (ev) { if (ev.target.matches("select, #cc-yr, #cc-a-c, #cc-b-c")) before(); });
  ["a", "b"].forEach(function (c) {
    var p = "cc-" + c + "-", was = powerOf(c);
    $(p + "t").addEventListener("change", function () { refill(c, snap[c] || {}); before(); calc(); });
    $(p + "p").addEventListener("change", function () { var flip = ice(was) !== ice(powerOf(c)); was = powerOf(c); refill(c, snap[c] || {}, flip ? ["e", "g", "s", "f"] : null); before(); calc(); });
    $(p + "l").addEventListener("change", calc);
    $(p + "c").addEventListener("input", function () { var h = snap[c] || held(c); refill(c, { w: h.w, d: h.d }); calc(); });
  });
  $("cc-yr").addEventListener("input", function () { ["a", "b"].forEach(function (c) { var h = snap[c] || held(c); refill(c, { w: h.w }); }); calc(); });
  mount.addEventListener("input", function (ev) { var id = ev.target.id; if (ev.target.tagName === "INPUT" && !/^cc-(yr|a-c|b-c)$/.test(id)) calc(); });
  $("cc-rm").addEventListener("click", function () { hasB = false; calc(); $("cc-add").focus(); });
  $("cc-add").addEventListener("click", function () { hasB = true; calc(); $("cc-b-n").focus(); });

  /* share links: "#mi=15000&yr=5&at=csuv&ap=gas&…&b=1" (each car's boxes by a- or b- plus a letter) */
  var KEYS = ["n", "t", "p", "c", "w", "d", "r", "l", "e", "g", "s", "f", "i", "m", "x"];
  function link() {
    var parts = [];
    [["cc-mi", "mi"], ["cc-yr", "yr"]].forEach(function (b) { var x = parse($(b[0]).value); if (x != null && !isNaN(x)) parts.push(b[1] + "=" + x); });
    (hasB ? ["a", "b"] : ["a"]).forEach(function (c) {
      KEYS.forEach(function (k) {
        var el = $("cc-" + c + "-" + k), v = el.tagName === "SELECT" ? el.value : k === "n" ? el.value.trim().slice(0, 40) : parse(el.value);
        if (v != null && v !== "" && !(typeof v === "number" && isNaN(v))) parts.push(c + k + "=" + encodeURIComponent(v));
      });
    });
    if (hasB) parts.push("b=1");
    return location.href.split("#")[0] + "#" + parts.join("&");
  }
  function fromHash() {
    var raw = location.hash; if (!raw || raw === applied || raw === "#cc-out") return false;
    applied = raw;
    var h = {};
    try { raw.replace(/^#/, "").split("&").forEach(function (p) { var i = p.indexOf("="); if (i > 0) h[p.slice(0, i)] = decodeURIComponent(p.slice(i + 1)); }); } catch (err) { return false; }
    if (h.mi == null && h.at == null) return false;
    hasB = h.b === "1";
    ["cc-mi", "cc-yr"].forEach(function (id, i) { var v = h[["mi", "yr"][i]]; $(id).value = v != null && isFinite(Number(v)) ? num(Number(v)) : ""; });
    ["a", "b"].forEach(function (c) {
      KEYS.forEach(function (k) {
        var el = $("cc-" + c + "-" + k), v = h[c + k];
        if (el.tagName === "SELECT") { if (v != null && [].some.call(el.options, function (o) { return o.value === v; })) el.value = v; }
        else if (k === "n") el.value = v || "";
        else el.value = v != null && v !== "" && isFinite(Number(v)) ? num(Number(v)) : "";
      });
    });
    return true;
  }
  window.addEventListener("hashchange", function () { if (fromHash()) calc(); });
  $("cc-copy").addEventListener("click", function () {
    var u = link(), out = $("cc-copied");
    var fallback = function () { out.innerHTML = '<label for="cc-link">Copy this link:</label> <input type="text" id="cc-link" readonly>'; $("cc-link").value = u; $("cc-link").focus(); $("cc-link").select(); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(u).then(function () { out.textContent = "Link copied."; }, fallback);
    else fallback();
  });

  /* ---------- start: AAA's compact SUV, gas and electric ---------- */
  put("cc-mi", 15000); put("cc-yr", 5);
  ["a", "b"].forEach(function (c) { $("cc-" + c + "-t").value = EX[c].t; $("cc-" + c + "-p").value = EX[c].p; $("cc-" + c + "-l").value = "60"; FILL.forEach(function (f) { put("cc-" + c + "-" + f, dflt(c, f)); }); });
  fromHash(); before(); calc(); clearTimeout(timer);
})();
