/* Rollback calculator for "How a Property Tax Rate Gets Set" (Nov 8, 2026).
   Builds its markup into .rb-mount, then estimates a reader's bill at the rollback rate and at last year's rate:
   at the rollback rate, bill x (1 + the home's taxable value change) / (1 + the average change on existing property).
   Nothing is stored or sent; every number stays in the page. Styles: .rb in assets/site.css. */
(function () {
  var mount = document.querySelector(".rb-mount");
  if (!mount) return;
  mount.innerHTML = "<section class=\"rb\" aria-labelledby=\"rb-h\">\n<h3 id=\"rb-h\">Try it with your own bill</h3>\n<p class=\"rb-intro\">A few numbers give an estimate of what the rollback rate would mean for you. The boxes start filled with the example from above. The estimate is most reliable for a home with no exemption that freezes or caps its value; for one with such an exemption, choose Line by line.</p>\n<fieldset class=\"rb-home\"><legend>Your home's value, from your assessment notice</legend>\n<div class=\"rb-pair\"><div><label for=\"rb-v0\">Last year</label><span class=\"rb-in\">$ <input type=\"text\" inputmode=\"decimal\" id=\"rb-v0\" class=\"rb-wide\" value=\"200,000\" autocomplete=\"off\" aria-describedby=\"rb-v-h\"></span></div><div><label for=\"rb-v1\">This year</label><span class=\"rb-in\">$ <input type=\"text\" inputmode=\"decimal\" id=\"rb-v1\" class=\"rb-wide\" value=\"230,000\" autocomplete=\"off\" aria-describedby=\"rb-v-h\"></span></div></div>\n<p class=\"rb-chgline\" id=\"rb-vchg\">That's a change of +15.0%.</p>\n<span class=\"rb-hint\" id=\"rb-v-h\">Use the taxable value if your notice shows it. If an exemption freezes or caps your value for some of the governments on your bill, choose Line by line below.</span>\n</fieldset>\n<div class=\"rb-seg rb-modes\" role=\"group\" aria-label=\"How to enter your bill\"><button type=\"button\" id=\"rb-m1\" aria-pressed=\"true\">The whole bill</button><button type=\"button\" id=\"rb-m2\" aria-pressed=\"false\">Line by line</button></div>\n<div id=\"rb-whole\">\n<div class=\"rb-f\"><label for=\"rb-bill\">Last year's property tax bill</label><span class=\"rb-in\">$ <input type=\"text\" inputmode=\"decimal\" id=\"rb-bill\" class=\"rb-wide\" value=\"2,000\" autocomplete=\"off\" aria-describedby=\"rb-bill-h\"></span><span class=\"rb-hint\" id=\"rb-bill-h\">The total on last year's tax bill.</span></div>\n<fieldset><legend>How much existing property changed on average</legend>\n<div class=\"rb-seg\" role=\"group\" aria-label=\"How to enter it\"><button type=\"button\" id=\"rb-t1\" aria-pressed=\"true\">I know the percent</button><button type=\"button\" id=\"rb-t2\" aria-pressed=\"false\">I have the two rates</button></div>\n<div id=\"rb-p1\"><span class=\"rb-in\"><input type=\"text\" inputmode=\"decimal\" id=\"rb-avg\" value=\"8\" autocomplete=\"off\" aria-label=\"Average change on existing property, in percent\" aria-describedby=\"rb-avg-h\"> %</span><span class=\"rb-hint\" id=\"rb-avg-h\">Rarely on an assessment notice. Assessors' annual reports often give it. A government that plans to go above its rollback rate has to advertise it; if you have that notice, choose \"I have the two rates.\"</span></div>\n<div id=\"rb-p2\" hidden><div class=\"rb-row\"><div><label for=\"rb-old\">Last year's rate</label><input type=\"text\" inputmode=\"decimal\" id=\"rb-old\" value=\"10\" autocomplete=\"off\" aria-describedby=\"rb-p2-h\"></div><div><label for=\"rb-rb\">This year's rollback rate</label><input type=\"text\" inputmode=\"decimal\" id=\"rb-rb\" value=\"9.26\" autocomplete=\"off\" aria-describedby=\"rb-p2-h\"></div></div><span class=\"rb-hint\" id=\"rb-p2-h\">Both for the same government, in the same unit. Governments publish the rollback rate when they advertise a tax increase.</span></div>\n</fieldset>\n<div class=\"rb-f\" id=\"rb-ratebox\"><label for=\"rb-rate\">Last year's rate <span class=\"rb-opt\">(optional)</span></label><span class=\"rb-in\"><input type=\"text\" inputmode=\"decimal\" id=\"rb-rate\" value=\"\" autocomplete=\"off\" aria-describedby=\"rb-rate-h\"><select id=\"rb-unit\" aria-label=\"Unit of the rate\"><option value=\"mills\">mills</option><option value=\"per100\">$ per $100</option><option value=\"pct\">percent</option></select></span><span class=\"rb-hint\" id=\"rb-rate-h\">On last year's bill, for one government. Adds the actual rate to the result.</span></div>\n</div>\n<div id=\"rb-lines\" hidden>\n<p class=\"rb-hint rb-lead\">One line for each government on your bill: the county, the school district, the city, and any special district. Each can have its own taxable value and its own average change. Line 1 starts from your whole-bill numbers until you edit a line.</p>\n<div id=\"rb-list\"></div>\n<button type=\"button\" class=\"rb-act\" id=\"rb-add\">Add a line</button>\n</div>\n<div class=\"rb-out\" id=\"rb-out\">\n<dl class=\"rb-res\">\n<dt>If every government on your bill adopts its rollback rate</dt><dd><span class=\"rb-big\" id=\"rb-a\">$2,130</span><span class=\"rb-chg\" id=\"rb-ac\" aria-hidden=\"true\">+6.5%</span><span class=\"sr\" id=\"rb-acs\">(up 6.5% from last year)</span></dd>\n<dt>If they keep last year's rates</dt><dd><span class=\"rb-big\" id=\"rb-b\">$2,300</span><span class=\"rb-chg\" id=\"rb-bc\" aria-hidden=\"true\">+15.0%</span><span class=\"sr\" id=\"rb-bcs\">(up 15.0% from last year)</span></dd>\n<dt class=\"rb-sep\" id=\"rb-dl\">Difference: the amount a rollback law requires them to advertise and vote on</dt><dd class=\"rb-sep\"><span class=\"rb-big\" id=\"rb-d\">$170</span></dd>\n</dl>\n<p class=\"rb-rate\" id=\"rb-r\">The rollback rate is 7.4% below last year's rate. At the article's example of 10 mills, it would be 9.26.</p>\n<p class=\"rb-err\" id=\"rb-e\" hidden></p><p class=\"rb-warn\" id=\"rb-w\" hidden></p><p class=\"rb-err\" id=\"rb-re\" hidden></p>\n</div>\n<p class=\"sr\" aria-live=\"polite\" id=\"rb-live\"></p>\n<details id=\"rb-townbox\"><summary>What the town collects</summary>\n<div class=\"rb-f\"><label for=\"rb-new\">New construction, as a share of last year's taxable value</label><span class=\"rb-in\"><input type=\"text\" inputmode=\"decimal\" id=\"rb-new\" value=\"2\" autocomplete=\"off\"> %</span></div>\n<p class=\"rb-err\" id=\"rb-ne\" hidden></p>\n<p id=\"rb-town\">At the rollback rate the town collects 1.9% more than last year, all of it from new construction. At last year's rate it collects 10.0% more.</p>\n</details>\n<p class=\"rb-note\">An estimate, not a tax bill. A bill is several taxes, and each government decides on its own; the county may adopt its rollback rate while the school board doesn't. Voter-approved debt and changes in exemptions from last year aren't included, and states compute the rollback rate slightly differently.</p>\n</section>";
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var mode = 1, input = 1, timer = null, lineSeq = 0, seeded = false, linesEdited = false;
  function parse(v) { var s = String(v).replace(/[$,%\s]/g, "").replace(/[−–—]/g, "-"); if (s === "") return null; var n = Number(s); return isFinite(n) ? n : NaN; }
  function num(id) { return parse($(id).value); }
  function money(v) { return (v < -0.5 ? "−" : "") + "$" + Math.round(Math.abs(v)).toLocaleString("en-US"); }
  function p1(v) { return (Math.abs(v) * 100).toFixed(1) + "%"; }
  function signed(v) { return Math.abs(v) < 0.0005 ? "0.0%" : (v > 0 ? "+" : "−") + p1(v); }
  function words(v) { return Math.abs(v) < 0.0005 ? "(no change from last year)" : "(" + (v > 0 ? "up " : "down ") + p1(v) + " from last year)"; }
  var dp = { mills: 2, per100: 4, pct: 2 };
  function fmtRate(v, u) { var s = v.toFixed(dp[u]); return u === "per100" ? "$" + s + " per $100" : u === "pct" ? s + "%" : s + " mills"; }
  function mark(el, on, msgId) {
    var d = (el.getAttribute("aria-describedby") || "").split(/\s+/).filter(function (x) { return x && !/^(rb-(e|w|ne|re)|e-\d+)$/.test(x); });
    if (on) { el.setAttribute("aria-invalid", "true"); d.push(msgId); } else el.removeAttribute("aria-invalid");
    if (d.length) el.setAttribute("aria-describedby", d.join(" ")); else el.removeAttribute("aria-describedby");
  }
  function say(el, msg) { el.hidden = !msg; el.textContent = msg ? "! " + msg : ""; }
  function sayW(el, msg) { el.hidden = !msg; el.textContent = msg ? "Check: " + msg : ""; el.className = msg ? "rb-warn" : el.className; }
  function clearMarks() { [].forEach.call(document.querySelectorAll(".rb input"), function (el) { mark(el, false); }); }
  function homeChange() {
    var v0 = num("rb-v0"), v1 = num("rb-v1"), out = { m: null, bad: null, msg: "", warn: "" };
    if (v0 === null || isNaN(v0) || v0 <= 0) { out.bad = "rb-v0"; out.msg = "Enter last year's value of your home in dollars."; }
    else if (v1 === null || isNaN(v1) || v1 <= 0) { out.bad = "rb-v1"; out.msg = "Enter this year's value of your home in dollars."; }
    else { out.m = v1 / v0 - 1; if (out.m < -0.5 || out.m > 1) out.warn = "a change of " + signed(out.m) + " in your home's value is unusual in one year."; }
    $("rb-vchg").textContent = out.m === null ? "" : "That's a change of " + signed(out.m) + ".";
    return out;
  }
  var DIFF = "Difference: the amount a rollback law requires them to advertise and vote on";
  function blank() { $("rb-dl").textContent = DIFF; ["rb-a", "rb-b", "rb-d"].forEach(function (i) { $(i).textContent = "–"; }); ["rb-ac", "rb-bc", "rb-acs", "rb-bcs"].forEach(function (i) { $(i).textContent = ""; }); $("rb-r").hidden = true; $("rb-town").textContent = "–"; }
  function totals(base, a, b) {
    $("rb-a").textContent = money(a); $("rb-ac").textContent = signed(a / base - 1); $("rb-acs").textContent = words(a / base - 1);
    $("rb-b").textContent = money(b); $("rb-bc").textContent = signed(b / base - 1); $("rb-bcs").textContent = words(b / base - 1);
    var d = b - a;
    if (d >= -0.5) { $("rb-dl").textContent = DIFF; $("rb-d").textContent = money(d); return "Difference, " + money(d) + "."; }
    $("rb-dl").textContent = "Values fell, so keeping last year's rates collects less than the rollback rate would"; $("rb-d").textContent = money(-d) + " less";
    return "Keeping last year's rates collects " + money(-d) + " less.";
  }
  function calcWhole() {
    var hc = homeChange(), bill = num("rb-bill"), mine = hc.m === null ? null : hc.m * 100, avg, oldRate = null, bad = null, msg = "", warn = "", wid = null, rateBad = false;
    if (input === 1) { avg = num("rb-avg"); oldRate = num("rb-rate"); if (avg !== null && !isNaN(avg)) avg /= 100; if (oldRate !== null && (isNaN(oldRate) || oldRate <= 0)) { rateBad = true; oldRate = null; } }
    else { var o = num("rb-old"), r = num("rb-rb"); if (o > 0 && r > 0) { avg = o / r - 1; oldRate = o; } else { avg = NaN; bad = !(o > 0) ? "rb-old" : "rb-rb"; } }
    if (hc.msg) { bad = hc.bad; msg = hc.msg; }
    else if (bill === null || isNaN(bill) || bill <= 0) { bad = "rb-bill"; msg = "Enter last year's bill in dollars."; }
    else if (false) { bad = hc.bad; msg = hc.msg; }
    else if (avg === null || isNaN(avg) || avg <= -1) { bad = bad || "rb-avg"; msg = input === 1 ? "Enter the average change, in percent." : "Enter both rates, as numbers above zero."; }
    say($("rb-e"), msg);
    if (msg) { mark($(bad), true, "rb-e"); say($("rb-w"), ""); say($("rb-re"), ""); blank(); return msg; }
    if (bill > 1e6) { wid = "rb-bill"; warn = "the bill is over $1 million."; }
    else if (hc.warn) { wid = "rb-v1"; warn = hc.warn; }
    else if (avg < -0.3 || avg > 0.5) { wid = input === 1 ? "rb-avg" : "rb-rb"; warn = "an average change of " + signed(avg) + " is unusual in one year."; }
    sayW($("rb-w"), warn); if (wid) mark($(wid), true, "rb-w");
    say($("rb-re"), rateBad ? "Enter last year's rate as a number above zero, or leave it blank." : ""); if (rateBad) mark($("rb-rate"), true, "rb-re");
    $("rb-r").hidden = false;
    var m = mine / 100, a = bill * (1 + m) / (1 + avg), b = bill * (1 + m);
    var dsay = totals(bill, a, b);
    var cut = 1 - 1 / (1 + avg), u = $("rb-unit").value;
    var line = "The rollback rate is " + (Math.abs(cut) < 0.0005 ? "the same as" : p1(cut) + (cut > 0 ? " below" : " above")) + " last year's rate";
    if (input === 1 && oldRate) line += ": " + fmtRate(oldRate, u) + " would become " + fmtRate(oldRate / (1 + avg), u) + ".";
    else if (input === 2) line += ", so existing property, taken together, " + (avg >= 0 ? "rose" : "fell") + " about " + p1(avg) + ".";
    else line += ". At the article's example of 10 mills, it would be " + (10 / (1 + avg)).toFixed(2) + ".";
    $("rb-r").textContent = line;
    var n = num("rb-new"), nbad = n !== null && (isNaN(n) || n < 0);
    say($("rb-ne"), nbad ? "Enter new construction as zero or more, in percent." : ""); if (nbad) mark($("rb-new"), true, "rb-ne");
    if (nbad) $("rb-town").textContent = "–";
    else { n = n ? n / 100 : 0;
      var g1 = n / (1 + avg), g0 = avg + n, mv = function (g) { return Math.abs(g) < 0.0005 ? "the same as" : p1(g) + (g > 0 ? " more than" : " less than"); };
      $("rb-town").textContent = "At the rollback rate the town collects " + mv(g1) + " last year" + (n ? ", all of the increase from new construction" : "") + ". At last year's rate it collects " + mv(g0) + " last year."; }
    return (warn ? "Check: " + warn + " " : "") + "At the rollback rate, " + money(a) + ". At last year's rates, " + money(b) + ". " + dsay + (rateBad ? " The rate you entered isn't a number above zero." : "") + (nbad ? " New construction should be zero or more." : "");
  }
  function calcLines() {
    var hcLine = homeChange(), homeNeeded = false;
    say($("rb-w"), ""); say($("rb-re"), ""); $("rb-r").hidden = true;
    var rows = [].slice.call($("rb-list").querySelectorAll(".rb-line")), base = 0, A = 0, B = 0, used = 0, notes = [], skipped = [];
    rows.forEach(function (row, k) {
      var id = row.getAttribute("data-id"), touched = row._touched || {}, er = $("e-" + id), res = $("r-" + id);
      var name = "Line " + (k + 1) + ($("n-" + id).value.trim() ? " (" + $("n-" + id).value.trim() + ")" : "");
      var ov = $("o-" + id).getAttribute("aria-expanded") === "true", a0 = parse($("a-" + id).value), a1 = parse($("b-" + id).value), vsrc = "your home's value change";
      var f = { t: parse($("t-" + id).value), v: null, g: parse($("g-" + id).value) };
      if (ov && (a0 !== null || a1 !== null)) { if (a0 > 0 && a1 > 0) { f.v = (a1 / a0 - 1) * 100; vsrc = "its own taxable value"; } else f.v = NaN; }
      else { homeNeeded = homeNeeded || f.t !== null || f.g !== null; f.v = hcLine.m === null ? NaN : hcLine.m * 100; }
      er.className = "rb-err"; say(er, ""); res.textContent = "";
      if (f.t === null && f.g === null && !(ov && (a0 !== null || a1 !== null))) return;
      var bad = null, msg = "";
      if (f.t !== null && (isNaN(f.t) || f.t <= 0)) { bad = "t"; msg = "enter last year's tax as more than $0."; }
      else if (isNaN(f.v)) { bad = ov ? (a0 > 0 ? "b" : "a") : null; msg = ov ? "enter this government's taxable value for both years, in dollars." : "enter your home's value for both years above."; }
      else if (f.g !== null && (isNaN(f.g) || f.g <= -100)) { bad = "g"; msg = "enter this government's average change as a percent."; }
      else { var miss = ["t", "g"].filter(function (x) { return f[x] === null; });
        if (miss.length) { var late = miss.filter(function (x) { return touched[x]; });
          if (late.length) { bad = late[0]; msg = { t: "enter last year's tax.", g: "enter this government's average change." }[bad]; }
          else { res.textContent = "Not counted yet: fill in last year's tax and the average change."; skipped.push(name); return; } } }
      if (msg) { say(er, msg.charAt(0).toUpperCase() + msg.slice(1)); if (bad) mark($(bad + "-" + id), true, "e-" + id); notes.push(name + ": " + msg); skipped.push(name); return; }
      var w = "", wf = null;
      if (ov && (f.v < -50 || f.v > 100)) { w = "a value change of " + signed(f.v / 100) + " is unusual in one year."; wf = "b"; }
      else if (f.g < -30 || f.g > 50) { w = "an average change of " + signed(f.g / 100) + " is unusual in one year."; wf = "g"; }
      if (w) { sayW(er, w); mark($(wf + "-" + id), true, "e-" + id); notes.push(name + ": check, " + w); }
      var a = f.t * (1 + f.v / 100) / (1 + f.g / 100), b = f.t * (1 + f.v / 100), cut = 1 - 1 / (1 + f.g / 100);
      base += f.t; A += a; B += b; used++;
      res.textContent = "Using " + vsrc + " (" + signed(f.v / 100) + "): at its rollback rate " + money(a) + "; at last year's rate " + money(b) + ". Its rollback rate is " + (Math.abs(cut) < 0.0005 ? "the same as" : p1(cut) + (cut > 0 ? " below" : " above")) + " last year's.";
    });
    var homeMsg = homeNeeded && hcLine.msg ? hcLine.msg : "", homeWarn = homeNeeded && hcLine.warn ? hcLine.warn : "";
    if (homeMsg) mark($(hcLine.bad), true, "rb-e");
    if (homeWarn) { mark($("rb-v1"), true, "rb-w"); notes.unshift("Check: " + homeWarn); }
    if (homeMsg) notes.unshift(homeMsg);
    if (!used) { say($("rb-e"), homeMsg ? homeMsg : notes.length ? "Fix the line marked below." : "Fill in at least one line: last year's tax and the average change."); blank(); return notes.length ? notes.join(" ") : "Fill in at least one line."; }
    say($("rb-e"), homeMsg);
    var wparts = []; if (homeWarn) wparts.push(homeWarn); if (skipped.length) wparts.push("the totals leave out " + skipped.join(", ") + ".");
    if (wparts.length) sayW($("rb-w"), wparts.join(" Also, "));
    var dsay = totals(base, A, B);
    return (notes.length ? notes.join(" ") + " " : "") + (used === 1 ? "For the 1 line counted" : "For the " + used + " lines counted") + ": at the rollback rates, " + money(A) + ". At last year's rates, " + money(B) + ". " + dsay + (skipped.length ? " Not counted: " + skipped.join(", ") + "." : "");
  }
  function calc() { clearMarks(); var t = mode === 1 ? calcWhole() : calcLines(); announce(t); }
  function announce(t) { clearTimeout(timer); timer = setTimeout(function () { $("rb-live").textContent = t; }, 700); }
  function renumber() {
    var rows = $("rb-list").querySelectorAll(".rb-line");
    [].forEach.call(rows, function (row, k) { var id = row.getAttribute("data-id"), nm = $("n-" + id).value.trim();
      row.querySelector("legend").textContent = "Line " + (k + 1) + (nm ? ": " + nm : "");
      var rm = row.querySelector(".rb-rm"); rm.textContent = "Remove line " + (k + 1); rm.hidden = rows.length < 2; });
    $("rb-add").hidden = rows.length >= 8;
  }
  function addLine(vals, focus) {
    var id = ++lineSeq; vals = vals || {};
    var f = document.createElement("fieldset"); f.className = "rb-line"; f.setAttribute("data-id", id);
    var esc = function (x) { return x == null ? "" : String(x).replace(/"/g, "&quot;"); };
    f.innerHTML = '<legend>Line</legend><div class="rb-row">' +
      '<div class="rb-nm"><label for="n-' + id + '">Government <span class="rb-opt">(optional)</span></label><input type="text" id="n-' + id + '" class="rb-name" autocomplete="off" value="' + esc(vals.n) + '"></div>' +
      '<div class="rb-tx"><label for="t-' + id + '">Last year\'s tax</label><span class="rb-in">$ <input type="text" inputmode="decimal" id="t-' + id + '" autocomplete="off" value="' + esc(vals.t) + '"></span></div>' +
      '<div><label for="g-' + id + '">This government\'s average change</label><span class="rb-in"><input type="text" inputmode="decimal" id="g-' + id + '" autocomplete="off" value="' + esc(vals.g) + '"> %</span></div>' +
      '</div><button type="button" class="rb-act rb-ov" id="o-' + id + '" aria-expanded="false" aria-controls="ob-' + id + '">Different value for this government</button>' +
      '<div class="rb-ovbox" id="ob-' + id + '" hidden><span class="rb-sub" aria-hidden="true">Its taxable value</span><div class="rb-pair"><div><label for="a-' + id + '"><span class="sr">Its taxable value, </span>Last year</label><span class="rb-in">$ <input type="text" inputmode="decimal" id="a-' + id + '" autocomplete="off" aria-describedby="oh-' + id + '"></span></div><div><label for="b-' + id + '"><span class="sr">Its taxable value, </span>This year</label><span class="rb-in">$ <input type="text" inputmode="decimal" id="b-' + id + '" autocomplete="off" aria-describedby="oh-' + id + '"></span></div></div><span class="rb-hint" id="oh-' + id + '">Each government\'s taxable value is on your tax bill. If it\'s frozen, enter the same number twice.</span></div>' +
      '<p class="rb-lres" id="r-' + id + '"></p><p class="rb-err" id="e-' + id + '" hidden></p>' +
      '<button type="button" class="rb-act rb-rm">Remove line</button>';
    $("rb-list").appendChild(f);
    f._touched = {};
    [].forEach.call(f.querySelectorAll("input"), function (el) { el.addEventListener("input", function () { linesEdited = true; if (el.classList.contains("rb-name")) renumber(); calc(); }); el.addEventListener("blur", function () { var k = el.id.split("-")[0]; if (k !== "n" && !f._touched[k]) { f._touched[k] = true; calc(); } }); });
    $("o-" + id).addEventListener("click", function () { var open = this.getAttribute("aria-expanded") !== "true"; this.setAttribute("aria-expanded", String(open)); $("ob-" + id).hidden = !open; if (open) $("a-" + id).focus(); calc(); });
    f.querySelector(".rb-rm").addEventListener("click", function () { var label = f.querySelector("legend").textContent; linesEdited = true; f.remove(); renumber(); calc(); $("rb-add").hidden ? $("rb-list").querySelector("input").focus() : $("rb-add").focus(); var n = $("rb-list").querySelectorAll(".rb-line").length; clearTimeout(timer); $("rb-live").textContent = label + " removed. " + n + (n === 1 ? " line left." : " lines left."); });
    renumber(); if (focus) $("n-" + id).focus();
  }
  function seed() {
    if (seeded && linesEdited) return;
    var first = seeded ? $("rb-list").querySelector(".rb-line") : null;
    var bill = num("rb-bill"), g = input === 1 ? num("rb-avg") : (num("rb-old") > 0 && num("rb-rb") > 0 ? (num("rb-old") / num("rb-rb") - 1) * 100 : null);
    var vals = { t: bill > 0 ? Math.round(bill) : "", g: g == null || isNaN(g) ? "" : Math.round(g * 10) / 10 };
    if (first) { var id = first.getAttribute("data-id"); $("t-" + id).value = vals.t; $("g-" + id).value = vals.g; return; }
    seeded = true; addLine(vals); addLine({});
  }
  function setMode(k) { mode = k; $("rb-m1").setAttribute("aria-pressed", String(k === 1)); $("rb-m2").setAttribute("aria-pressed", String(k === 2)); $("rb-whole").hidden = k !== 1; $("rb-lines").hidden = k !== 2; $("rb-townbox").hidden = k !== 1; if (k === 2) seed(); calc(); }
  function setInput(k) { input = k; $("rb-t1").setAttribute("aria-pressed", String(k === 1)); $("rb-t2").setAttribute("aria-pressed", String(k === 2)); $("rb-p1").hidden = k !== 1; $("rb-p2").hidden = k !== 2; $("rb-ratebox").hidden = k !== 1; calc(); }
  $("rb-m1").addEventListener("click", function () { setMode(1); });
  $("rb-m2").addEventListener("click", function () { setMode(2); });
  $("rb-t1").addEventListener("click", function () { setInput(1); });
  $("rb-t2").addEventListener("click", function () { setInput(2); });
  $("rb-add").addEventListener("click", function () { addLine({}, true); calc(); });
  ["rb-v0", "rb-v1", "rb-bill", "rb-avg", "rb-old", "rb-rb", "rb-rate", "rb-new"].forEach(function (id) { $(id).addEventListener("input", calc); });
  $("rb-unit").addEventListener("change", calc);
  calc(); clearTimeout(timer);
})();
})();
