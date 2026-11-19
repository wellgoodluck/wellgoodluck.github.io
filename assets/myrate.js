/* "What's My Own Inflation Rate?" (Nov 19, 2026). Mounted on <div class="mr-mount" data-tool="myrate">; at every build
   tools/build_articles.py writes onto the mount the month (data-m) and each line's 12-month price change (data-p, JSON),
   from tools/figures.py myrate_lines, so the page makes no requests and nothing the reader types is stored or sent. A
   link with the numbers is built only when the reader asks, with them after "#". A line the data has no figure for asks
   for the reader's own year-ago amount. Styles: the shared calculator box (.rb, .ku, .mt) plus .mr in assets/site.css. */
(function () {
  var mount = document.querySelector(".mr-mount");
  if (!mount) return;
  var $ = function (id) { return document.getElementById(id); };
  var MONTH = mount.getAttribute("data-m"), P = null;
  try { P = JSON.parse(mount.getAttribute("data-p") || "null"); } catch (e) { P = null; }
  if (!P || typeof P.all !== "number" || !MONTH) {
    mount.innerHTML = '<p class="rb-noscript">The price figures didn\'t load. This is usually temporary; reload the page to try again.</p>';
    return;
  }
  var MAX = 1e5, NEED = "The site has no national figure for this line, so it needs what you paid a year ago too.";

  /* each line: key, label, the name used in messages, which homes show it (r rent, m mortgage, o own outright; all if
     unset), "own" for a line with only the reader's figures ("opt": a blank year-ago amount means unchanged), "more"
     for a line under More lines */
  var L = [
    { k: "rent", label: "Rent", nm: "rent", homes: "r", hint: "Rent only. Utilities have their own lines." },
    { k: "mort", label: "Mortgage payment (principal and interest)", nm: "your mortgage payment", homes: "m", own: "opt", hint: "A fixed-rate payment doesn't change. If yours is adjustable, add what it was a year ago." },
    { k: "ptax", label: "Property tax and home insurance", nm: "property tax and home insurance", homes: "mo", own: "need", hint: "On your escrow statement or your bills. A year's total divided by 12." },
    { k: "elec", label: "Electricity", nm: "electricity" },
    { k: "groc", label: "Groceries", nm: "groceries" },
    { k: "eat", label: "Eating out", nm: "eating out", hint: "Restaurants, takeout and delivery." },
    { k: "gas", label: "Gasoline", nm: "gasoline" },
    { k: "carins", label: "Car insurance", nm: "car insurance", pre: 1, hint: "Your renewal notice shows the last premium. A year ago starts at what the national price change implies; replace it with yours." },
    { k: "med", label: "Doctor, dentist and prescriptions", nm: "doctor, dentist and prescriptions", hint: "What you pay yourself. Put insurance premiums in a line of your own." },
    { k: "all", label: "Everything else", nm: "everything else", hint: "Household goods, personal care, subscriptions, gifts, and anything without a line." },
    { k: "pgas", label: "Natural gas", nm: "natural gas", more: 1 },
    { k: "water", label: "Water, sewer and trash", nm: "water, sewer and trash", more: 1 },
    { k: "phone", label: "Phone service", nm: "phone service", more: 1, hint: "Cell and home phone. Internet goes in a line of your own." },
    { k: "repair", label: "Car repairs and maintenance", nm: "car repairs and maintenance", more: 1 },
    { k: "carpay", label: "Car payment (loan or lease)", nm: "your car payment", more: 1, own: "opt", hint: "A loan payment doesn't change. If you got a different car this year, leave this line out, since that's a change in what you buy." },
    { k: "transit", label: "Buses, trains and flights", nm: "buses, trains and flights", more: 1 },
    { k: "cloth", label: "Clothing and shoes", nm: "clothing and shoes", more: 1 },
    { k: "child", label: "Child care", nm: "child care", more: 1 },
    { k: "own1", label: "Your own line", nm: "your own line", more: 1, own: "need", named: 1, hint: 'Name it if you like, such as "internet" or "health insurance".' },
    { k: "own2", label: "Your own line", nm: "your own line", more: 1, own: "need", named: 1 },
    { k: "own3", label: "Your own line", nm: "your own line", more: 1, own: "need", named: 1 }
  ];
  L.forEach(function (l) { if (!l.own && typeof P[l.k] !== "number") l.own = "need"; });   /* no national figure this month */
  var KINDS = [["r", "I rent"], ["m", "I have a mortgage"], ["o", "I own outright"]];
  var BASE = { elec: 150, groc: 600, eat: 350, gas: 200, carins: 190, med: 150, all: 1000 };
  var EX = { r: Object.assign({ rent: 1500 }, BASE), m: Object.assign({ mort: 1800, ptax: 450, "ptax-a": 430 }, BASE), o: Object.assign({ ptax: 450, "ptax-a": 430 }, BASE) };
  var kind = "r", timer = null, lastEx = "", applied = "";
  var AUTO = {};                                                 /* Nov 19: a "pre" line's year-ago box still holds the national figure */
  L.forEach(function (l) { if (l.pre && !l.own) AUTO[l.k] = true; else delete l.pre; });

  /* ---------- formatting ---------- */
  function parse(v) { var s = String(v).replace(/[$,\s]/g, ""); if (s === "") return null; var n = Number(s); return isFinite(n) ? n : NaN; }
  function money(v) { return (v < 0 ? "−" : "") + "$" + Math.abs(v).toLocaleString("en-US", { maximumFractionDigits: 0 }); }
  function cash(v) { var c = Math.round(v * 100) % 100 !== 0; return "$" + v.toLocaleString("en-US", { minimumFractionDigits: c ? 2 : 0, maximumFractionDigits: 2 }); }
  function r1(x) { return Math.round(x * 10) / 10; }
  function f1(x) { return Math.abs(r1(x)).toFixed(1); }
  function signed(x) { var v = r1(x); return (v > 0 ? "+" : v < 0 ? "−" : "") + Math.abs(v).toFixed(1) + "%"; }
  function signedMoney(x) { return x > 0 ? "+" + money(x) : x < 0 ? money(x) : "$0"; }
  function andList(a) { return a.length < 2 ? a.join("") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1]; }
  function shows(l) { return !l.homes || l.homes.indexOf(kind) >= 0; }
  function nameOf(l) { var n = l.named ? $("mr-" + l.k + "-n").value.trim() : ""; return n || l.nm; }
  function labelOf(l) { var n = l.named ? $("mr-" + l.k + "-n").value.trim() : ""; return n || l.label; }

  /* ---------- markup ---------- */
  function line(l) {
    var id = "mr-" + l.k, nat = !l.own && !l.pre, desc = [l.hint ? id + "-h" : "", l.own === "need" && !l.named ? id + "-nh" : "", l.named && l.hint ? "" : ""].join(" ").trim();
    return '<div class="mr-line" id="' + id + '-row">' +
      '<div class="mr-lab"><label for="' + id + '" id="' + id + '-l">' + l.label + "</label>" +
      (l.named ? '<span class="mr-nmf"><label for="' + id + '-n" class="mr-small">Name <span class="rb-opt">(optional)</span></label><input type="text" id="' + id + '-n" class="mr-name" autocomplete="off"></span>' : "") + "</div>" +
      '<div class="mr-amts">' +
      '<span class="mr-now"><span class="mr-small" id="' + id + '-nl" aria-hidden="true"' + (nat ? " hidden" : "") + '>Each month now</span><span class="rb-in">$ <input type="text" inputmode="decimal" id="' + id + '" autocomplete="off"' + (desc ? ' aria-describedby="' + desc + '"' : "") + "></span></span>" +
      '<span class="mr-ago" id="' + id + '-ab"' + (nat ? " hidden" : "") + '><label for="' + id + '-a" class="mr-small">A year ago</label><span class="rb-in">$ <input type="text" inputmode="decimal" id="' + id + '-a" autocomplete="off" aria-describedby="' + id + '-l"></span></span>' +
      (nat ? '<button type="button" class="mr-use" id="' + id + '-u" aria-controls="' + id + '-ab" aria-expanded="false">Use what I paid a year ago</button>' : "") +
      "</div>" +
      (l.hint ? '<span class="rb-hint" id="' + id + '-h">' + l.hint + "</span>" : "") +
      (l.own === "need" && !l.named ? '<span class="rb-hint" id="' + id + '-nh">' + NEED + "</span>" : "") +
      (l.named && l.k === "own1" ? '<span class="rb-hint">' + NEED + "</span>" : "") +
      "</div>";
  }
  var main = L.filter(function (l) { return !l.more; }), more = L.filter(function (l) { return l.more; });
  mount.innerHTML = ['<section class="rb ku mt mr" aria-labelledby="mr-h">',
    '<h2 id="mr-h" class="ku-h">Work out your own inflation rate</h2>',
    '<p class="mr-kl" id="mr-kl">Your home</p>',
    '<div class="rb-seg ku-kinds" role="group" aria-labelledby="mr-kl">' + KINDS.map(function (k, i) { return '<button type="button" data-k="' + k[0] + '" aria-pressed="' + (i === 0) + '">' + k[1] + "</button>"; }).join("") + "</div>",
    '<p class="rb-intro mr-intro">What you spend in a typical month. Leave out money that goes to savings, retirement or taxes. Leave a line blank if it isn\'t yours.</p>',
    '<div class="mr-lines">' + main.map(line).join("") + "</div>",
    '<details id="mr-more"><summary>More lines: natural gas, water, phone, car repairs, car payment, transit and flights, clothing, child care, your own</summary><div class="mr-lines">' + more.map(line).join("") + "</div></details>",
    '<div class="rb-sumwrap"><a class="rb-sum off" id="mr-sum" href="#mr-out"><span id="mr-sumt"></span> <span class="rb-sumgo">Details <span aria-hidden="true">↓</span></span></a></div>',
    '<div class="rb-out" id="mr-out" tabindex="-1">',
    '<p class="rb-ex" id="mr-ex" hidden></p>',
    '<p class="ku-lead" id="mr-lead"></p>',
    '<p class="rb-warn" id="mr-w" hidden></p>',
    '<p class="rb-err" id="mr-e" hidden></p>',
    '<div id="mr-res"></div>',
    "</div>",
    '<p class="sr" aria-live="polite" id="mr-live"></p>',
    '<div class="ku-share" id="mr-share"><button type="button" class="rb-act" id="mr-copy">Copy a link with these numbers</button><span class="rb-hint">The link carries the numbers you typed, so anyone you send it to will see them.</span><p class="ku-copied" id="mr-copied" role="status"></p></div>',
    "</section>"].join("\n");

  /* ---------- inputs ---------- */
  function boxes() {                                             /* every box: [id, example key] */
    var out = [];
    L.forEach(function (l) { out.push(["mr-" + l.k, l.k]); out.push(["mr-" + l.k + "-a", l.k + "-a"]); });
    return out;
  }
  function show(id, v) { $(id).value = v == null ? "" : Number(v).toLocaleString("en-US", { maximumFractionDigits: 2 }); }
  function holds(id, key, k) { var x = parse($(id).value), e = EX[k][key]; return e == null ? x === null : x === e; }
  function fillAuto() {
    L.forEach(function (l) {
      if (!l.pre || !AUTO[l.k]) return;
      var box = $("mr-" + l.k + "-a"), now = parse($("mr-" + l.k).value);
      if (document.activeElement === box) return;
      box.value = now > 0 ? Math.round(now / (1 + P[l.k] / 100)).toLocaleString("en-US") : "";
    });
  }
  function reveal(l, focus) {
    var u = $("mr-" + l.k + "-u");
    $("mr-" + l.k + "-ab").hidden = false; $("mr-" + l.k + "-nl").hidden = false;
    if (u) { u.hidden = true; u.setAttribute("aria-expanded", "true"); }
    if (focus) $("mr-" + l.k + "-a").focus();
  }
  function setKind(k, quiet) {
    var stale = boxes().filter(function (b) { return holds(b[0], b[1], kind); });
    kind = k;
    [].forEach.call(mount.querySelectorAll(".ku-kinds button"), function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-k") === k)); });
    stale.forEach(function (b) { show(b[0], EX[k][b[1]]); });
    L.forEach(function (l) { $("mr-" + l.k + "-row").hidden = !shows(l); if (l.own === "need" || parse($("mr-" + l.k + "-a").value) != null) { if (!l.own) reveal(l); } });
    if (!quiet) calc();
  }

  /* ---------- the arithmetic ---------- */
  function largest(xs, total) {                                  /* whole dollars that add up to the rounded total */
    var fl = xs.map(Math.floor), need = Math.round(total) - fl.reduce(function (a, b) { return a + b; }, 0);
    xs.map(function (x, i) { return [x - fl[i], i]; }).sort(function (a, b) { return b[0] - a[0]; }).slice(0, Math.max(need, 0)).forEach(function (p) { fl[p[1]] += 1; });
    return fl;
  }
  function run() {
    var used = [], warn = "", err = null;
    for (var i = 0; i < L.length && !err; i++) {
      var l = L[i];
      if (!shows(l)) continue;
      var now = parse($("mr-" + l.k).value), agoBox = !$("mr-" + l.k + "-ab").hidden, ago = agoBox && !(l.pre && AUTO[l.k]) ? parse($("mr-" + l.k + "-a").value) : null, nm = nameOf(l);
      if (isNaN(now) || (now != null && (now < 0 || now > MAX))) { err = { t: "Enter what you spend a month on " + nm + " in dollars, up to $100,000, or leave it blank.", f: "mr-" + l.k, l: l }; break; }
      if (isNaN(ago) || (ago != null && (ago < 0 || ago > MAX))) { err = { t: "Enter what you paid a year ago for " + nm + " in dollars, up to $100,000.", f: "mr-" + l.k + "-a", l: l }; break; }
      if (now == null || now === 0) { if (ago != null && ago > 0) err = { t: "Enter what you pay now for " + nm + " too, or clear the year-ago amount.", f: "mr-" + l.k, l: l }; continue; }
      if (ago === 0) { err = { t: "A year-ago amount of $0 can't show a price change. If this is new this year, leave the line out.", f: "mr-" + l.k + "-a", l: l }; break; }
      var past, mine = false;
      if (ago != null) { past = ago; mine = true; }
      else if (!l.own) past = now / (1 + P[l.k] / 100);
      else if (l.own === "opt") past = now;
      else { err = { t: "Enter what you paid a year ago for " + nm + " too. The site has no national figure for this line.", f: "mr-" + l.k + "-a", l: l }; break; }
      var chg = now / past - 1;
      if (mine && !warn && Math.abs(chg) > 0.5)
        warn = "Check: " + nm + " is " + (chg > 0 ? "up " : "down ") + Math.round(Math.abs(chg) * 100) + "% from a year ago. If you changed what you buy, such as a different provider, a bigger place or a different car, that isn't a price change. Enter the same thing both years, or leave the line out.";
      used.push({ l: l, label: labelOf(l) + (mine && !l.own ? " (yours)" : ""), now: now, past: past, chg: chg });
    }
    if (!err && !used.length) err = { t: "Enter at least one amount.", f: "mr-" + (kind === "r" ? "rent" : kind === "m" ? "mort" : "ptax") };
    if (err) return { err: err };
    var sNow = 0, sPast = 0;
    used.forEach(function (u) { sNow += u.now; sPast += u.past; });
    var rate = (sNow / sPast - 1) * 100, mine1 = r1(rate), O = P.all, O1 = r1(O), per = " over the 12 months to " + MONTH;
    var overall = O1 >= 0 ? "rose " + f1(O) + "%" : "fell " + f1(O) + "%", lead;
    if (Math.abs(rate) < 0.05) lead = "Your prices were about unchanged" + per + ", while prices overall " + overall + ".";
    else if (mine1 < 0) lead = "Your prices fell about " + f1(rate) + "%" + per + ", while prices overall " + overall + ".";
    else if (Math.round(Math.abs(mine1 - O1) * 10) <= 2) lead = "Your prices rose about " + f1(rate) + "%" + per + ", about the same as prices overall (" + f1(O) + "%).";
    else if (mine1 > O1) lead = "Your prices rose about " + f1(rate) + "%" + per + ", more than the " + f1(O) + "% for prices overall.";
    else lead = "Your prices rose about " + f1(rate) + "%" + per + ", less than the " + f1(O) + "% for prices overall.";
    var d = sNow - sPast, dm = Math.round(Math.abs(d)), dy = Math.round(Math.abs(d) * 12 / 10) * 10, then = [];
    if (dm >= 1) then.push("The same things cost about " + money(dm) + " " + (d > 0 ? "more" : "less") + " a month than a year earlier, about " + money(dy) + " a year.");
    if (rate >= 0.05) then.push("To buy the same things as a year earlier takes about " + f1(rate) + "% more money: that's the raise that would keep you even.");
    else if (rate <= -0.05) then.push("To buy the same things takes about " + f1(rate) + "% less money than a year earlier.");
    used.sort(function (a, b) { return (b.now - b.past) - (a.now - a.past); });
    var adds = largest(used.map(function (u) { return u.now - u.past; }), d);
    var t = '<div class="table-scroll"><table class="rb-t mr-t"><caption class="rb-tcap">Where the change came from</caption><thead><tr><th>Line</th><th>Each month</th><th>Price change</th><th>Adds a month</th></tr></thead><tbody>' +
      used.map(function (u, i) { return "<tr><td>" + u.label.replace(/&/g, "&amp;").replace(/</g, "&lt;") + "</td><td>" + cash(u.now) + "</td><td>" + signed(u.chg * 100) + "</td><td>" + signedMoney(adds[i]) + "</td></tr>"; }).join("") +
      '<tr class="mr-tot"><td>Total</td><td>' + cash(sNow) + "</td><td>" + signed(rate) + "</td><td>" + signedMoney(Math.round(d)) + "</td></tr></tbody></table></div>";
    var notes = [];
    if (P.oer > 0 && kind === "m") notes.push("The national figure leaves out mortgage payments. For homeowners it counts what their homes would rent for, which rose " + f1(P.oer) + "% over the same 12 months. That's one reason a homeowner with a fixed-rate mortgage can come out below the national figure.");
    if (P.oer > 0 && kind === "o") notes.push("For homeowners, the national figure counts what their homes would rent for, which rose " + f1(P.oer) + "% over the same 12 months. What owners actually pay, such as property tax and insurance, isn't in it, so those lines use your own amounts.");
    notes.push("The national figures run through " + MONTH + ", the latest month the Bureau of Labor Statistics can compare with a year earlier. Your own lines compare what you pay now with a year ago.");
    var res = (then.length ? '<p class="rb-plain">' + then.join(" ") + "</p>" : "") +
      '<p class="rb-dnote"><a href="kept-up.html">Has It Kept Up With Prices?</a> checks your own pay against prices overall.</p>' + t +
      notes.map(function (n) { return '<p class="rb-dnote">' + n + "</p>"; }).join("");
    return { lead: lead, then: then.join(" "), res: res, warn: warn, sum: "your prices " + signed(rate) + " · prices overall " + signed(O) };
  }

  /* ---------- the example line, errors, the summary bar ---------- */
  function exState() {
    var vis = L.filter(shows), all = true, left = [];
    vis.forEach(function (l) {
      var a = holds("mr-" + l.k, l.k, kind), b = l.pre ? AUTO[l.k] : holds("mr-" + l.k + "-a", l.k + "-a", kind), n = !l.named || $("mr-" + l.k + "-n").value.trim() === "";
      if (!(a && b && n)) all = false;
      if (EX[kind][l.k] != null && a && b) left.push(l.nm);
    });
    if (left.length > 3) left = left.slice(0, 2).concat([(left.length - 2) + " other amounts"]);
    return { all: all, left: left };
  }
  function clearMarks() { [].forEach.call(mount.querySelectorAll("input[aria-invalid]"), function (el) { el.removeAttribute("aria-invalid"); var d = (el.getAttribute("aria-describedby") || "").replace(/\s*mr-e\b/, "").trim(); if (d) el.setAttribute("aria-describedby", d); else el.removeAttribute("aria-describedby"); }); }
  function calc() {
    fillAuto();
    clearMarks();
    var R = run(), ex = exState(), exEl = $("mr-ex"), e = $("mr-e");
    var exKey = ex.all ? "all" : ex.left.join("|");
    exEl.hidden = !exKey; exEl.innerHTML = ex.all ? "<strong>These are example figures for a made-up household.</strong> Replace them with yours." : exKey ? "<strong>Still the example's:</strong> " + andList(ex.left) + "." : "";
    if (R.err) {
      var el = $(R.err.f);
      e.hidden = false; e.textContent = "! " + R.err.t;
      el.setAttribute("aria-invalid", "true"); el.setAttribute("aria-describedby", ((el.getAttribute("aria-describedby") || "") + " mr-e").trim());
      if (R.err.l && R.err.l.more) $("mr-more").open = true;
      $("mr-lead").hidden = true; $("mr-res").innerHTML = ""; $("mr-w").hidden = true; $("mr-share").hidden = true;
      $("mr-sumt").textContent = "No result yet: " + R.err.t; announce(R.err.t); place(); return;
    }
    e.hidden = true; $("mr-share").hidden = false; $("mr-copied").textContent = "";
    $("mr-lead").hidden = false; $("mr-lead").textContent = R.lead;
    $("mr-w").hidden = !R.warn; $("mr-w").textContent = R.warn;
    $("mr-res").innerHTML = R.res;
    $("mr-sumt").textContent = (ex.all ? "Example: " : "") + R.sum;
    var exSay = exKey !== lastEx && exKey && exKey !== "all" ? " Still the example's: " + andList(ex.left) + "." : "";
    lastEx = exKey;
    announce((ex.all ? "Example figures. " : "") + R.lead + " " + R.then + (R.warn ? " " + R.warn : "") + exSay);
    place();
  }
  function announce(t) { clearTimeout(timer); timer = setTimeout(function () { $("mr-live").textContent = t; }, 700); }
  var queued = false;
  function place() {
    if (queued) return; queued = true;
    requestAnimationFrame(function () {
      queued = false;
      var H = window.innerHeight, top = $("mr-h").getBoundingClientRect().top, stuck = $("mr-sum").parentNode.getBoundingClientRect().top >= H - 1;
      $("mr-sum").classList.toggle("off", !(top < H - 90 && stuck));
    });
  }
  window.addEventListener("scroll", place, { passive: true });
  window.addEventListener("resize", place);
  $("mr-sum").addEventListener("click", function (ev) { ev.preventDefault(); $("mr-out").scrollIntoView({ block: "start" }); $("mr-out").focus({ preventScroll: true }); });

  /* ---------- share links: "#k=r&rent=1500&elec=150&carins-a=200&own1n=internet…" ---------- */
  function link() {
    var parts = ["k=" + kind];
    L.forEach(function (l) {
      [["mr-" + l.k, l.k], ["mr-" + l.k + "-a", l.k + "-a"]].forEach(function (b, i) { var x = parse($(b[0]).value); if (i && l.pre && AUTO[l.k]) return; if (x != null && !isNaN(x)) parts.push(b[1] + "=" + x); });
      if (l.named && $("mr-" + l.k + "-n").value.trim()) parts.push(l.k + "n=" + encodeURIComponent($("mr-" + l.k + "-n").value.trim().slice(0, 40)));
    });
    return location.href.split("#")[0] + "#" + parts.join("&");
  }
  function fromHash() {
    var raw = location.hash; if (!raw || raw === applied || raw === "#mr-out") return false;
    applied = raw;
    var h = {};
    try { raw.replace(/^#/, "").split("&").forEach(function (p) { var i = p.indexOf("="); if (i > 0) h[p.slice(0, i)] = decodeURIComponent(p.slice(i + 1)); }); } catch (err) { return false; }
    var any = boxes().some(function (b) { return h[b[1]] != null; });
    if (["r", "m", "o"].indexOf(h.k) >= 0 && h.k !== kind) setKind(h.k, true);
    if (!any) return h.k != null;
    var open = false;
    L.forEach(function (l) {
      [["mr-" + l.k, l.k], ["mr-" + l.k + "-a", l.k + "-a"]].forEach(function (b) { var x = Number(h[b[1]]); $(b[0]).value = h[b[1]] != null && h[b[1]] !== "" && isFinite(x) ? x.toLocaleString("en-US", { maximumFractionDigits: 6 }) : ""; });
      if (l.named) $("mr-" + l.k + "-n").value = h[l.k + "n"] || "";
      if (l.pre) AUTO[l.k] = !(h[l.k + "-a"] != null && h[l.k + "-a"] !== "");
      else if (!l.own && h[l.k + "-a"] != null) reveal(l);
      if (l.more && (h[l.k] != null || h[l.k + "-a"] != null)) open = true;
    });
    if (open) $("mr-more").open = true;
    return true;
  }
  window.addEventListener("hashchange", function () { if (fromHash()) calc(); });
  $("mr-copy").addEventListener("click", function () {
    var u = link(), out = $("mr-copied");
    var fallback = function () { out.innerHTML = '<label for="mr-link">Copy this link:</label> <input type="text" id="mr-link" readonly>'; $("mr-link").value = u; $("mr-link").focus(); $("mr-link").select(); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(u).then(function () { out.textContent = "Link copied."; }, fallback);
    else fallback();
  });

  /* ---------- start ---------- */
  mount.addEventListener("input", function (ev) {
    if (ev.target.tagName !== "INPUT") return;
    var m = ev.target.id.match(/^mr-(\w+)-a$/);
    if (m && AUTO.hasOwnProperty(m[1])) AUTO[m[1]] = ev.target.value.trim() === "";
    calc();
  });
  mount.addEventListener("focusout", function (ev) { var m = ev.target.id && ev.target.id.match(/^mr-(\w+)-a$/); if (m && AUTO[m[1]]) { setTimeout(function () { fillAuto(); }, 0); } });
  [].forEach.call(mount.querySelectorAll(".ku-kinds button"), function (b) { b.addEventListener("click", function () { setKind(b.getAttribute("data-k")); }); });
  L.forEach(function (l) { var u = $("mr-" + l.k + "-u"); if (u) u.addEventListener("click", function () { reveal(l, true); calc(); }); });
  boxes().forEach(function (b) { show(b[0], EX[kind][b[1]]); });
  setKind(kind, true);
  fromHash(); calc(); clearTimeout(timer);
})();
