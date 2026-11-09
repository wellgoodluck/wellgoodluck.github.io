/* "Has It Kept Up With Prices?" (mock, Nov 8, 2026; revised after review). Builds its markup into .ku-mount, loads the
   site's own /data/tool-prices.json (CPI, average hourly pay, CPI rent), and compares an amount at one date with an
   amount at a later date against what prices did in between. Nothing the reader types is stored or sent; a link with
   the numbers is built only when the reader asks for one, and it carries them after "#", which browsers never send to
   a server. Styles: the calculator box (.rb) in assets/site.css, plus .ku. */
(function () {
  var mount = document.querySelector(".ku-mount");
  if (!mount) return;
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  /* Example figures follow the national series so the example never shows a gain or loss the national data don't
     (pay: average hourly pay; rent: CPI rent; a benefit: prices). Set once the data load. */
  var KINDS = {
    pay: { subj: "Your pay", amt: "Your pay", base: 50000, follow: "pay", step: 100, hint: "Use the same kind of figure both times: both yearly, both monthly or both hourly." },
    benefit: { subj: "Your benefit", amt: "Your benefit", base: 1800, follow: "cpi", step: 10, hint: "A pension, Social Security or another payment, the same kind of figure both times (both monthly, say)." },
    rent: { subj: "Your rent", amt: "Your rent", base: 1200, follow: "rent", step: 10, hint: "Monthly rent both times." },
    other: { subj: "The amount", amt: "The amount", base: 100, follow: null, step: 1, hint: "Any amount: a price, a bill or a salary. Leave the amount under Later blank to see what it's worth at the later date." }
  };
  mount.innerHTML = [
    '<section class="rb ku" aria-labelledby="ku-h">',
    '<h2 id="ku-h" class="ku-h">Compare two amounts with prices</h2>',
    '<div class="rb-seg ku-kinds" role="group" aria-label="What are you comparing?">',
    '<button type="button" data-k="pay" aria-pressed="true">Pay</button><button type="button" data-k="benefit" aria-pressed="false">A benefit</button><button type="button" data-k="rent" aria-pressed="false">Rent</button><button type="button" data-k="other" aria-pressed="false">Something else</button>',
    '</div>',
    '<p class="rb-hint" id="ku-ah"></p>',
    '<div id="ku-form">',
    '<fieldset class="ku-when"><legend>Then</legend>',
    '<div class="rb-f"><label for="ku-a" id="ku-al">Your pay</label><span class="rb-in">$ <input type="text" inputmode="decimal" id="ku-a" class="rb-wide" autocomplete="off" aria-describedby="ku-ah"></span></div>',
    '<div class="ku-date"><div><label for="ku-m0">Month</label><select id="ku-m0"></select></div><div><label for="ku-y0">Year</label><select id="ku-y0"></select></div></div>',
    '</fieldset>',
    '<fieldset class="ku-when"><legend>Later</legend>',
    '<div class="rb-f"><label for="ku-b" id="ku-bl">Your pay <span class="rb-opt">(optional)</span></label><span class="rb-in">$ <input type="text" inputmode="decimal" id="ku-b" class="rb-wide" autocomplete="off" aria-describedby="ku-ah"></span></div>',
    '<div class="ku-date"><div><label for="ku-m1">Month</label><select id="ku-m1"></select></div><div><label for="ku-y1">Year</label><select id="ku-y1"></select></div></div>',
    '</fieldset>',
    '</div>',
    '<div class="rb-sumwrap"><a class="rb-sum off" id="ku-sum" href="#ku-out"><span id="ku-sumt"></span> <span class="rb-sumgo">Details <span aria-hidden="true">↓</span></span></a></div>',
    '<div class="rb-out" id="ku-out" tabindex="-1">',
    '<p class="rb-ex" id="ku-ex" hidden></p>',
    '<p class="ku-lead" id="ku-lead"></p>',
    '<dl class="rb-res" id="ku-res"></dl>',
    '<p class="rb-dnote" id="ku-extra" hidden></p>',
    '<p class="rb-err" id="ku-e" hidden></p>',
    '</div>',
    '<p class="sr" aria-live="polite" id="ku-live"></p>',
    '<div class="ku-share" id="ku-share"><button type="button" class="rb-act" id="ku-copy">Copy a link with these numbers</button><span class="rb-hint">The link carries the numbers you typed, so anyone you send it to will see them.</span><p class="ku-copied" id="ku-copied" role="status"></p></div>',
    '<p class="rb-note" id="ku-src"></p>',
    '<p class="rb-note">Prices here are the national average for urban consumers. Your own prices may have risen faster or slower, depending on where you live and what you buy.</p>',
    '</section>'
  ].join("\n");
  var $ = function (id) { return document.getElementById(id); };
  var D = null, kind = "pay", timer = null, lastEx = "", applied = "";
  function parse(v) { var s = String(v).replace(/[$,\s]/g, ""); if (s === "") return null; var n = Number(s); return isFinite(n) ? n : NaN; }
  function money(v) { var a = Math.abs(v), dec = a < 100 && Math.round(a * 100) % 100 !== 0 ? 2 : 0; return "$" + a.toLocaleString("en-US", { minimumFractionDigits: dec, maximumFractionDigits: dec }); }
  function pct(v) { return (Math.abs(v) * 100).toFixed(1) + "%"; }
  function about(v) { var a = Math.abs(v) * 100; return (a >= 0.995 ? Math.round(a) : a.toFixed(1)) + "%"; }   /* leads: whole percents from 1% up */
  function signed(v) { return Math.abs(v) < 0.0005 ? "0.0%" : (v > 0 ? "+" : "−") + pct(v); }
  function moved(v) { return Math.abs(v) < 0.0005 ? "was unchanged" : (v > 0 ? "rose " : "fell ") + pct(v); }
  function vsPrices(real) { return Math.abs(real) < 0.005 ? "about the same as prices" : "or about " + about(real) + (real > 0 ? " more" : " less") + " after adjusting for prices"; }
  function andList(a) { return a.length < 2 ? a.join("") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1]; }
  function series(key) { var s = D[key], p = s.start.split("-").map(Number); return { y0: p[0], m0: p[1], v: s.v }; }
  /* a series' value in a month (m 1–12) or, with m = 0, that year's average of the months published */
  function at(key, y, m) {
    var S = series(key), i0 = (y - S.y0) * 12 + (1 - S.m0), vals = [];
    if (m) { var i = i0 + m - 1, x = i >= 0 ? S.v[i] : undefined; return x == null ? { v: null, why: i < 0 ? "early" : i >= S.v.length ? "late" : "gap" } : { v: x }; }
    for (var k = 0; k < 12; k++) { var j = i0 + k; if (j >= 0 && j < S.v.length && S.v[j] != null) vals.push(S.v[j]); }
    var lastY = S.y0 + Math.floor((S.m0 - 1 + S.v.length - 1) / 12);
    if (y === lastY && (S.m0 - 1 + S.v.length) % 12 !== 0) return { v: null, why: "partial" };
    if (!vals.length) return { v: null, why: i0 < 0 ? "early" : "late" };
    return { v: vals.reduce(function (a, b) { return a + b; }, 0) / vals.length, n: vals.length };
  }
  function when(y, m) { return m ? MONTHS[m - 1] + " " + y : String(y); }
  function whenAvg(y, m) { return m ? MONTHS[m - 1] + " " + y : "the " + y + " average"; }
  var L = null;
  function latest() { var S = series("cpi"), i = S.v.length - 1; while (i > 0 && S.v[i] == null) i--; var t = S.m0 - 1 + i; return { y: S.y0 + Math.floor(t / 12), m: t % 12 + 1 }; }
  function setExamples() {
    Object.keys(KINDS).forEach(function (k) {
      var K = KINDS[k], f = K.follow, x0 = f && at(f, 2019, 0), x1 = f && at(f, L.y, L.m);
      K.ex = [K.base, f && x0.v && x1.v ? Math.round(K.base * x1.v / x0.v / K.step) * K.step : null];
    });
  }
  function fillDates() {
    var S = series("cpi");
    ["ku-m0", "ku-m1"].forEach(function (id) { $(id).innerHTML = '<option value="0">Whole year</option>' + MONTHS.map(function (n, i) { return '<option value="' + (i + 1) + '">' + n + '</option>'; }).join(""); });
    var ys = ""; for (var y = L.y; y >= S.y0; y--) ys += '<option value="' + y + '">' + y + '</option>';
    $("ku-y0").innerHTML = ys; $("ku-y1").innerHTML = ys;
  }
  function exampleLeft() {
    var K = KINDS[kind], a = parse($("ku-a").value), b = parse($("ku-b").value);
    return { a: a === K.ex[0], b: K.ex[1] == null ? b === null : b === K.ex[1] };
  }
  function setKind(k, keepValues) {
    var wasEx = exampleLeft();
    kind = k;
    [].forEach.call(document.querySelectorAll(".ku-kinds button"), function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-k") === k)); });
    var K = KINDS[k];
    $("ku-al").textContent = K.amt; $("ku-bl").innerHTML = K.amt + ' <span class="rb-opt">(optional)</span>'; $("ku-ah").textContent = K.hint;
    if (!keepValues && wasEx.a) $("ku-a").value = K.ex[0].toLocaleString("en-US");
    if (!keepValues && wasEx.b) $("ku-b").value = K.ex[1] == null ? "" : K.ex[1].toLocaleString("en-US");
    calc();
  }
  function say(el, msg) { el.hidden = !msg; el.textContent = msg ? "! " + msg : ""; }
  function row(dt, dd, sub) { return "<dt>" + dt + (sub ? '<span class="ku-sub">' + sub + "</span>" : "") + "</dt><dd><span class=\"rb-big\">" + dd + "</span></dd>"; }
  function reason(r, part, y, m) {
    if (r.why === "gap") return "BLS couldn't collect October 2025 prices because of the federal shutdown, so there's no reading for that month. Choose September or November.";
    if (r.why === "partial") return "The " + y + " average isn't complete yet. Choose a month under " + part + ".";
    if (r.why === "late") return "Prices are measured through " + when(L.y, L.m) + ". Choose that month or an earlier one under " + part + ".";
    var S = series("cpi"); return "Prices start in " + when(S.y0, S.m0) + ". Choose that year or a later one under " + part + ".";
  }
  function calc() {
    if (!D) return;
    var K = KINDS[kind], a = parse($("ku-a").value), b = parse($("ku-b").value);
    var y0 = +$("ku-y0").value, m0 = +$("ku-m0").value, y1 = +$("ku-y1").value, m1 = +$("ku-m1").value, msg = "", bad = null;
    var p0 = at("cpi", y0, m0), p1 = at("cpi", y1, m1);
    ["ku-a", "ku-b", "ku-m0", "ku-y0", "ku-m1", "ku-y1"].forEach(function (id) { var el = $(id); el.removeAttribute("aria-invalid"); el.setAttribute("aria-describedby", (id === "ku-a" || id === "ku-b") ? "ku-ah" : ""); if (!el.getAttribute("aria-describedby")) el.removeAttribute("aria-describedby"); });
    if (a === null || isNaN(a) || a <= 0) { msg = "Enter the amount under Then, in dollars."; bad = "ku-a"; }
    else if (b !== null && (isNaN(b) || b <= 0)) { msg = "Enter the amount under Later in dollars, or leave it blank."; bad = "ku-b"; }
    else if (p0.v == null) { msg = reason(p0, "Then", y0, m0); bad = p0.why === "partial" || p0.why === "gap" ? "ku-m0" : "ku-y0"; }
    else if (p1.v == null) { msg = reason(p1, "Later", y1, m1); bad = p1.why === "partial" || p1.why === "gap" ? "ku-m1" : "ku-y1"; }
    else if (y1 * 12 + (m1 || 6.5) <= y0 * 12 + (m0 || 6.5)) { msg = "The Later date has to come after the Then date."; bad = "ku-y1"; }   /* a whole year counts as its middle */
    say($("ku-e"), msg);
    var exNow = exState();
    showExample(exNow);
    if (msg) {
      var el = $(bad); el.setAttribute("aria-invalid", "true"); el.setAttribute("aria-describedby", ((el.getAttribute("aria-describedby") || "") + " ku-e").trim());
      $("ku-lead").hidden = true; $("ku-res").innerHTML = ""; $("ku-extra").hidden = true;
      $("ku-sumt").textContent = "No result yet: " + msg;
      announce(msg); place(); return;
    }
    $("ku-lead").hidden = false;
    var pc = p1.v / p0.v - 1, need = a * (1 + pc), w0 = whenAvg(y0, m0), w1 = when(y1, m1), now = y1 === L.y && m1 === L.m, lead, rows = "", spoken;
    var subjLow = K.subj.charAt(0).toLowerCase() + K.subj.slice(1);
    if (b !== null) {
      var ac = b / a - 1, real = (1 + ac) / (1 + pc) - 1, same = Math.abs(real) < 0.005, then = when(y0, m0);
      if (kind === "pay" || kind === "benefit") {
        var amt = same ? "about the same as" : "about " + about(real) + (real > 0 ? " more than" : " less than");
        lead = now ? K.subj + " buys " + amt + " it did in " + then + "." : "In " + w1 + ", " + subjLow + " bought " + amt + " it did in " + then + ".";
      } else {
        var lvl = same ? "about the same as in " : "about " + about(real) + (real > 0 ? " higher than in " : " lower than in ");
        lead = now ? "Adjusted for prices, " + subjLow + " is " + lvl + then + "." : "In " + w1 + ", adjusted for prices, " + subjLow + " was " + lvl + then + ".";
      }
      rows += row(K.subj, signed(ac), money(a) + " to " + money(b));
      rows += row("Prices", signed(pc), w0 + " to " + w1);
      rows += row("To match prices", money(need), "what " + money(a) + " in " + then + " comes to in " + w1);
      spoken = lead + " " + K.subj + " " + signed(ac) + ", prices " + signed(pc) + ". To match prices it would be " + money(need) + ".";
    } else {
      lead = money(a) + " in " + when(y0, m0) + " is about " + money(need) + " in " + w1 + " dollars.";
      rows += row("Prices", signed(pc), w0 + " to " + w1);
      spoken = lead + " Prices " + signed(pc) + ".";
    }
    $("ku-lead").textContent = lead; $("ku-res").innerHTML = rows;
    $("ku-sumt").textContent = (exNow.key === "all" ? "Example: " : "") + lead;
    var ex = "", x0, x1, ch;
    if (kind === "pay") { x0 = at("pay", y0, m0); x1 = at("pay", y1, m1);
      if (x0.v != null && x1.v != null) { ch = x1.v / x0.v - 1; ex = 'Over the same period, <a href="' + D.pay.url + '">average hourly pay for production and nonsupervisory workers</a> ' + moved(ch) + ", " + vsPrices((1 + ch) / (1 + pc) - 1) + "."; } }
    else if (kind === "rent") { x0 = at("rent", y0, m0); x1 = at("rent", y1, m1);
      if (x0.v != null && x1.v != null) { ch = x1.v / x0.v - 1; ex = 'Over the same period, <a href="' + D.rent.url + '">rent in the Consumer Price Index</a> ' + moved(ch) + ", " + vsPrices((1 + ch) / (1 + pc) - 1) + ". That index follows all renters, including those who stayed put, so it changes more gradually than rents on new leases and turns about a year after them."; } }
    else if (kind === "benefit") ex = "Social Security raises follow a related index, the CPI-W, measured July to September and paid from January, so a raise can differ from the change in prices shown here, by more in years when prices move fast.";
    $("ku-extra").hidden = !ex; $("ku-extra").innerHTML = ex;
    var note2 = (m0 === 0 && y0 === 2025) || (m1 === 0 && y1 === 2025) ? " The 2025 average leaves out October, when BLS couldn't collect prices." : "";
    $("ku-src").innerHTML = 'Prices: <a href="' + D.cpi.url + '">' + D.cpi.label + '</a>, Bureau of Labor Statistics via FRED, through ' + when(L.y, L.m) + ". A whole year uses that year's average." + note2;
    var exSay = exNow.key !== lastEx && exNow.key && exNow.key !== "all" ? " Still the example's: " + andList(exNow.left) + "." : "";
    lastEx = exNow.key;
    announce((exNow.key === "all" ? "Example figures. " : "") + spoken + exSay);
    place();
  }
  function exState() {
    var K = KINDS[kind], e = exampleLeft(), left = [];
    if (e.a) left.push("the amount under Then (" + money(K.ex[0]) + ")");
    if (e.b && K.ex[1] != null) left.push("the amount under Later (" + money(K.ex[1]) + ")");
    var dates = +$("ku-y0").value === 2019 && +$("ku-m0").value === 0 && +$("ku-y1").value === L.y && +$("ku-m1").value === L.m;
    return { left: left, key: e.a && e.b && dates ? "all" : left.join("|") };
  }
  function showExample(s) {
    var el = $("ku-ex");
    el.hidden = !s.key; el.innerHTML = s.key === "all" ? "<strong>These are example figures</strong> that follow the national averages. Replace them with yours." : s.key ? "<strong>Still the example's:</strong> " + andList(s.left) + "." : "";
  }
  function announce(t) { clearTimeout(timer); timer = setTimeout(function () { $("ku-live").textContent = t; }, 700); }
  /* The summary bar shows only while it is stuck to the bottom of the screen, i.e. while the results are below it. */
  var queued = false;
  function place() {
    if (queued) return; queued = true;
    requestAnimationFrame(function () {
      queued = false;
      var H = window.innerHeight, top = $("ku-h").getBoundingClientRect().top, stuck = $("ku-sum").parentNode.getBoundingClientRect().top >= H - 1;
      $("ku-sum").classList.toggle("off", !(top < H - 90 && stuck));
    });
  }
  window.addEventListener("scroll", place, { passive: true });
  window.addEventListener("resize", place);
  $("ku-sum").addEventListener("click", function (e) { e.preventDefault(); $("ku-out").scrollIntoView({ block: "start" }); $("ku-out").focus({ preventScroll: true }); });
  function fromHash() {
    var raw = location.hash; if (!raw || raw === applied || raw === "#ku-out") return false;
    applied = raw;
    var h = {};
    try { raw.replace(/^#/, "").split("&").forEach(function (p) { var kv = p.split("="); if (kv[0]) h[kv[0]] = decodeURIComponent(kv[1] || ""); }); } catch (err) { return false; }
    var k = Object.prototype.hasOwnProperty.call(KINDS, h.k) ? h.k : null;
    if (!h.a && !k) return false;
    if (k) setKind(k, !!h.a);          /* a link with only a kind (from a tile or household page) keeps that kind's examples */
    if (!h.a) return true;
    var dt = function (s, ym, mm) { var p = String(s || "").split("-"); if (+p[0]) { $(ym).value = String(+p[0]); $(mm).value = String(+(p[1] || 0)); } };
    $("ku-a").value = isFinite(+h.a) ? Number(h.a).toLocaleString("en-US") : "";
    $("ku-b").value = h.b && isFinite(+h.b) ? Number(h.b).toLocaleString("en-US") : "";
    dt(h.d0, "ku-y0", "ku-m0"); dt(h.d1, "ku-y1", "ku-m1");
    return true;
  }
  window.addEventListener("hashchange", function () { if (D && fromHash()) calc(); });
  function link() {
    var a = parse($("ku-a").value), b = parse($("ku-b").value), d = function (y, m) { return y + (+m ? "-" + ("0" + m).slice(-2) : ""); };
    return location.href.split("#")[0] + "#k=" + kind + (a ? "&a=" + a : "") + (b ? "&b=" + b : "") + "&d0=" + d($("ku-y0").value, $("ku-m0").value) + "&d1=" + d($("ku-y1").value, $("ku-m1").value);
  }
  $("ku-copy").addEventListener("click", function () {
    var u = link(), out = $("ku-copied");
    var fallback = function () { out.innerHTML = '<label for="ku-link">Copy this link:</label> <input type="text" id="ku-link" readonly>'; $("ku-link").value = u; $("ku-link").focus(); $("ku-link").select(); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(u).then(function () { out.textContent = "Link copied."; }, fallback);
    else fallback();
  });
  [].forEach.call(mount.querySelectorAll(".ku-kinds button"), function (b) { b.addEventListener("click", function () { setKind(b.getAttribute("data-k")); }); });
  ["ku-a", "ku-b"].forEach(function (id) { $(id).addEventListener("input", calc); });
  ["ku-m0", "ku-y0", "ku-m1", "ku-y1"].forEach(function (id) { $(id).addEventListener("change", calc); });
  var src = mount.getAttribute("data-src") || "/data/tool-prices.json";
  fetch(src).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }).then(function (d) {
    D = d; L = latest(); setExamples(); fillDates();
    $("ku-y0").value = "2019"; $("ku-m0").value = "0"; $("ku-y1").value = String(L.y); $("ku-m1").value = String(L.m);
    $("ku-a").value = KINDS.pay.ex[0].toLocaleString("en-US"); $("ku-b").value = KINDS.pay.ex[1].toLocaleString("en-US");
    $("ku-ah").textContent = KINDS.pay.hint;
    fromHash(); calc(); clearTimeout(timer);
  }).catch(function () {
    ["ku-form", "ku-share"].forEach(function (id) { $(id).hidden = true; });
    $("ku-ah").hidden = true; mount.querySelector(".ku-kinds").hidden = true;
    var m = "The price figures didn't load. This is usually temporary; reload the page to try again.";
    $("ku-lead").textContent = m; $("ku-live").textContent = m;
  });
})();
