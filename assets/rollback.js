/* Rollback calculator for "How a Property Tax Rate Gets Set" (Nov 8, 2026; revised Nov 8: "I don't know" table,
   example tracking, a summary that stays on screen while the results are out of view, Florida/Texas pointer,
   More detail, percent check).
   Builds its markup into .rb-mount, then estimates a reader's bill at the rollback rate and at last year's rate:
   at the rollback rate, bill x (1 + the home's taxable value change) / (1 + the average change on existing property).
   Nothing is stored or sent; every number stays in the page. Styles: .rb in assets/site.css. */
(function () {
  var mount = document.querySelector(".rb-mount");
  if (!mount) return;
  var FL = "https://m.flsenate.gov/Statutes/200.069",
      TX = "https://www.texas.gov/living-in-texas/property-tax-transparency/";
  mount.innerHTML = [
    '<section class="rb" aria-labelledby="rb-h">',
    '<h3 id="rb-h">Try it with your own bill</h3>',
    '<p class="rb-intro">Enter your own figures to estimate your bill at the rollback rate and at last year\'s rates. The boxes start with the example\'s figures from above.</p>',
    '<p class="rb-pt">Florida and Texas already show part of this: <a href="' + FL + '">Florida\'s notice of proposed property taxes</a> and <a href="' + TX + '">Texas county property tax websites</a> list your taxes at each government\'s rollback rate and at its proposed rate, but not at last year\'s.</p>',
    '<fieldset class="rb-home"><legend>Your home\'s value, from your assessment notice</legend>',
    '<div class="rb-pair"><div><label for="rb-v0">Last year</label><span class="rb-in">$ <input type="text" inputmode="decimal" id="rb-v0" class="rb-wide" value="200,000" autocomplete="off" aria-describedby="rb-v-h"></span></div><div><label for="rb-v1">This year</label><span class="rb-in">$ <input type="text" inputmode="decimal" id="rb-v1" class="rb-wide" value="230,000" autocomplete="off" aria-describedby="rb-v-h"></span></div></div>',
    '<p class="rb-chgline" id="rb-vchg">That\'s a change of +15.0%.</p>',
    '<span class="rb-hint" id="rb-v-h">Use the taxable value if your notice shows it. If an exemption freezes or caps your value for some of the governments on your bill, choose Line by line below.</span>',
    '</fieldset>',
    '<div class="rb-seg rb-modes" role="group" aria-label="How to enter your bill"><button type="button" id="rb-m1" aria-pressed="true">The whole bill</button><button type="button" id="rb-m2" aria-pressed="false">Line by line</button></div>',
    '<div id="rb-whole">',
    '<div class="rb-f"><label for="rb-bill">Last year\'s property tax bill</label><span class="rb-in">$ <input type="text" inputmode="decimal" id="rb-bill" class="rb-wide" value="2,000" autocomplete="off" aria-describedby="rb-bill-h"></span><span class="rb-hint" id="rb-bill-h">The total on last year\'s tax bill.</span></div>',
    '<fieldset><legend>How much existing property changed on average</legend>',
    '<div class="rb-seg rb-three" role="group" aria-label="How to enter it"><button type="button" id="rb-t1" aria-pressed="true">I know it</button><button type="button" id="rb-t2" aria-pressed="false">I have two rates</button><button type="button" id="rb-t3" aria-pressed="false">I don\'t know</button></div>',
    '<div id="rb-p1"><span class="rb-in"><input type="text" inputmode="decimal" id="rb-avg" value="8" autocomplete="off" aria-label="Average change on existing property, in percent" aria-describedby="rb-avg-h"> %</span><p class="rb-warn" id="rb-avg-w" hidden></p><span class="rb-hint" id="rb-avg-h">Rarely on an assessment notice; assessors\' annual reports often give it. If you have a government\'s notice of a tax increase, choose "I have two rates."</span></div>',
    '<div id="rb-p2" hidden><div class="rb-row"><div><label for="rb-old">Last year\'s rate</label><input type="text" inputmode="decimal" id="rb-old" value="10" autocomplete="off" aria-describedby="rb-p2-h"></div><div><label for="rb-rb">This year\'s rollback rate</label><input type="text" inputmode="decimal" id="rb-rb" value="9.26" autocomplete="off" aria-describedby="rb-p2-h"></div></div><span class="rb-hint" id="rb-p2-h">Both for the same government, in the same unit. Governments publish the rollback rate when they advertise a tax increase.</span></div>',
    '<div id="rb-p3" hidden><span class="rb-hint">The results show your bill at several averages, so you can see how much the figure matters.</span></div>',
    '</fieldset>',
    '</div>',
    '<div id="rb-lines" hidden>',
    '<p class="rb-hint rb-lead">One line for each government on your bill: the county, the school district, the city, and any special district. Each can have its own taxable value and its own average change. Line 1 starts from your whole-bill figures until you edit a line.</p>',
    '<div id="rb-list"></div>',
    '<button type="button" class="rb-act" id="rb-add">Add a line</button>',
    '</div>',
    '<div class="rb-sumwrap"><a class="rb-sum off" id="rb-sum" href="#rb-out"><span id="rb-sumt"></span> <span class="rb-sumgo">Details <span aria-hidden="true">↓</span></span></a></div>',
    '<div class="rb-out" id="rb-out" tabindex="-1">',
    '<p class="rb-ex" id="rb-ex" hidden></p>',
    '<dl class="rb-res" id="rb-known">',
    '<dt>If every government on your bill adopts its rollback rate</dt><dd><span class="rb-big" id="rb-a">$2,130</span><span class="rb-chg" id="rb-ac" aria-hidden="true">+6.5%</span><span class="sr" id="rb-acs">(up 6.5% from last year)</span></dd>',
    '<dt>If they keep last year\'s rates</dt><dd><span class="rb-big" id="rb-b">$2,300</span><span class="rb-chg" id="rb-bc" aria-hidden="true">+15.0%</span><span class="sr" id="rb-bcs">(up 15.0% from last year)</span></dd>',
    '<dt class="rb-sep" id="rb-dl">Difference: your share of the extra collected at last year\'s rates</dt><dd class="rb-sep"><span class="rb-big" id="rb-d">$170</span></dd>',
    '</dl>',
    '<div id="rb-unk" hidden>',
    '<p class="rb-tcap" id="rb-tcap">If every government on your bill adopts its rollback rate, your bill depends on how much existing property changed on average:</p>',
    '<table class="rb-t" aria-labelledby="rb-tcap"><thead><tr><th scope="col">Average change</th><th scope="col">Your bill</th><th scope="col">From last year</th></tr></thead><tbody id="rb-tb"></tbody></table>',
    '<dl class="rb-res"><dt>If they keep last year\'s rates</dt><dd><span class="rb-big" id="rb-b3"></span><span class="rb-chg" id="rb-b3c" aria-hidden="true"></span><span class="sr" id="rb-b3s"></span></dd></dl>',
    '</div>',
    '<p class="rb-dnote" id="rb-dn">In states with a rollback rule, a rate above the rollback rate usually counts as a tax increase and has to be announced; <a href="#what-the-requirement-looks-like">what else it requires</a> varies by state.</p>',
    '<p class="rb-rate" id="rb-r"></p>',
    '<p class="rb-plain" id="rb-n" hidden></p>',
    '<p class="rb-err" id="rb-e" hidden></p><p class="rb-warn" id="rb-w" hidden></p><p class="rb-err" id="rb-re" hidden></p>',
    '</div>',
    '<p class="sr" aria-live="polite" id="rb-live"></p>',
    '<details id="rb-more"><summary id="rb-moresum">More detail: the rate, and what the governments collect</summary>',
    '<div class="rb-f" id="rb-ratebox"><label for="rb-rate">Last year\'s rate <span class="rb-opt">(optional)</span></label><span class="rb-in"><input type="text" inputmode="decimal" id="rb-rate" value="" autocomplete="off" aria-describedby="rb-rate-h"><select id="rb-unit" aria-label="Unit of the rate"><option value="mills">mills</option><option value="per100">$ per $100</option><option value="pct">percent</option></select></span><span class="rb-hint" id="rb-rate-h">On last year\'s bill, for one government.</span><p class="rb-rl" id="rb-rl" hidden></p></div>',
    '<div class="rb-f"><label for="rb-tot">One government\'s total taxable value last year</label><span class="rb-in">$ <input type="text" inputmode="decimal" id="rb-tot" class="rb-xwide" value="500,000,000" autocomplete="off" aria-describedby="rb-tot-h"></span></div>',
    '<div class="rb-f"><label for="rb-new">New construction it added this year</label><span class="rb-in">$ <input type="text" inputmode="decimal" id="rb-new" class="rb-xwide" value="10,000,000" autocomplete="off" aria-describedby="rb-tot-h"></span><span class="rb-hint" id="rb-tot-h">Both usually appear in the government\'s budget documents or its tax roll summary.</span></div>',
    '<p class="rb-err" id="rb-ne" hidden></p>',
    '<p id="rb-town"></p>',
    '</details>',
    '<p class="rb-note">An estimate, not a tax bill. A bill is several taxes, and each government decides on its own; the county may adopt its rollback rate while the school board doesn\'t. Voter-approved debt and changes in exemptions from last year aren\'t included, and states compute the rollback rate slightly differently.</p>',
    '</section>'
  ].join("\n");
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var mode = 1, input = 1, timer = null, lineSeq = 0, seeded = false, linesEdited = false, lastEx = "";
  function parse(v) { var s = String(v).replace(/[$,%\s]/g, "").replace(/[−–—]/g, "-"); if (s === "") return null; var n = Number(s); return isFinite(n) ? n : NaN; }
  function num(id) { return parse($(id).value); }
  function money(v) { return (v < -0.5 ? "−" : "") + "$" + Math.round(Math.abs(v)).toLocaleString("en-US"); }
  function p1(v) { return (Math.abs(v) * 100).toFixed(1) + "%"; }
  function signed(v) { return Math.abs(v) < 0.0005 ? "0.0%" : (v > 0 ? "+" : "−") + p1(v); }
  function words(v) { return Math.abs(v) < 0.0005 ? "(no change from last year)" : "(" + (v > 0 ? "up " : "down ") + p1(v) + " from last year)"; }
  function andList(a) { return a.length < 2 ? a.join("") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1]; }
  var dp = { mills: 2, per100: 4, pct: 2 };
  function fmtRate(v, u) { var s = v.toFixed(dp[u]); return u === "per100" ? "$" + s + " per $100" : u === "pct" ? s + "%" : s + " mills"; }
  /* A percent typed as a decimal fraction ("0.08" for 8%): two or more decimals, above 0 and below 1, no % sign. Non-blocking. */
  function tinyPct(raw) {
    var s = String(raw).replace(/\s/g, "");
    if (!/^0?\.\d{2,}$/.test(s)) return "";
    var v = Number(s), x = Number((v * 100).toFixed(4)), shown = s.charAt(0) === "." ? "0" + s : s;
    return v > 0 && v < 1 ? shown + " here means " + shown + "%. For " + x + "%, enter " + x + "." : "";
  }
  /* The example's figures, so the results can say which boxes still hold them. */
  var EX = { "rb-v0": [200000, "home value last year ($200,000)"], "rb-v1": [230000, "home value this year ($230,000)"],
             "rb-bill": [2000, "last year's bill ($2,000)"], "rb-avg": [8, "average change (8%)"],
             "rb-old": [10, "last year's rate (10)"], "rb-rb": [9.26, "rollback rate (9.26)"],
             "rb-tot": [500000000, "total taxable value ($500,000,000)"], "rb-new": [10000000, "new construction ($10,000,000)"] };
  function exampleState() {
    var ids = ["rb-v0", "rb-v1"];
    if (mode === 1) {
      ids.push("rb-bill");
      if (input === 1) ids.push("rb-avg"); else if (input === 2) ids.push("rb-old", "rb-rb");
      if (input !== 3 && $("rb-more").open) ids.push("rb-tot", "rb-new");
    }
    var left = ids.filter(function (id) { return num(id) === EX[id][0]; }).map(function (id) { return EX[id][1]; }), total = ids.length;
    if (mode === 2) {
      var first = $("rb-list").querySelector(".rb-line"), id1 = first && first.getAttribute("data-id");
      total++;
      if (first && !linesEdited && parse($("t-" + id1).value) === 2000 && parse($("g-" + id1).value) === 8) left.push("line 1's tax and average change");
    }
    return { all: left.length === total, left: left };
  }
  function showExample(s) {
    var el = $("rb-ex");
    el.hidden = !s.left.length;
    el.innerHTML = s.all ? "<strong>These are the example's figures.</strong> Replace them with yours." : s.left.length ? "<strong>Still the example's:</strong> " + andList(s.left) + "." : "";
  }
  function mark(el, on, msgId) {
    var d = (el.getAttribute("aria-describedby") || "").split(/\s+/).filter(function (x) { return x && !/^(rb-(e|w|ne|re|avg-w)|e-\d+)$/.test(x); });
    if (on) { el.setAttribute("aria-invalid", "true"); d.push(msgId); } else el.removeAttribute("aria-invalid");
    if (d.length) el.setAttribute("aria-describedby", d.join(" ")); else el.removeAttribute("aria-describedby");
  }
  function say(el, msg) { el.hidden = !msg; el.textContent = msg ? "! " + msg : ""; }
  function sayW(el, msg) { el.hidden = !msg; el.textContent = msg ? "Check: " + msg : ""; el.className = msg ? "rb-warn" : el.className; }
  function plain(msg) { $("rb-n").hidden = !msg; $("rb-n").textContent = msg || ""; }
  function clearMarks() { [].forEach.call(document.querySelectorAll(".rb input"), function (el) { mark(el, false); }); }
  function homeChange() {
    var v0 = num("rb-v0"), v1 = num("rb-v1"), out = { m: null, bad: null, msg: "", warn: "" };
    if (v0 === null || isNaN(v0) || v0 <= 0) { out.bad = "rb-v0"; out.msg = "Enter last year's value of your home in dollars."; }
    else if (v1 === null || isNaN(v1) || v1 <= 0) { out.bad = "rb-v1"; out.msg = "Enter this year's value of your home in dollars."; }
    else { out.m = v1 / v0 - 1; if (out.m < -0.5 || out.m > 1) out.warn = "a change of " + signed(out.m) + " in your home's value is unusual in one year."; }
    $("rb-vchg").textContent = out.m === null ? "" : "That's a change of " + signed(out.m) + ".";
    return out;
  }
  /* The summary at the bottom of the screen, shown while the first result is out of view. */
  var sumPrefix = "";
  function summary(t) { $("rb-sumt").textContent = t; }
  function view(known) { $("rb-known").hidden = !known; $("rb-unk").hidden = known; }
  function blank(why) {
    view(true); $("rb-dl").textContent = "Difference: your share of the extra collected at last year's rates"; $("rb-dn").hidden = true;
    ["rb-a", "rb-b", "rb-d"].forEach(function (i) { $(i).textContent = "–"; }); ["rb-ac", "rb-bc", "rb-acs", "rb-bcs"].forEach(function (i) { $(i).textContent = ""; });
    $("rb-r").hidden = true; $("rb-town").textContent = "–"; $("rb-rl").hidden = true;
    summary(why || "No estimate yet: a box above needs fixing.");
  }
  function chg(base, v, big, c, s) { $(big).textContent = money(v); $(c).textContent = signed(v / base - 1); $(s).textContent = words(v / base - 1); }
  function totals(base, a, b) {
    view(true);
    chg(base, a, "rb-a", "rb-ac", "rb-acs"); chg(base, b, "rb-b", "rb-bc", "rb-bcs");
    var d = b - a;
    summary(sumPrefix + money(a) + " at the rollback rate · " + money(b) + " at last year's rates");
    if (d >= -0.5) { $("rb-dl").textContent = "Difference: your share of the extra collected at last year's rates"; $("rb-d").textContent = money(d); $("rb-dn").hidden = d < 0.5; return "Difference, " + money(d) + "."; }
    $("rb-dl").textContent = "Values fell, so keeping last year's rates collects less than the rollback rate would"; $("rb-d").textContent = money(-d) + " less"; $("rb-dn").hidden = true;
    return "Keeping last year's rates collects " + money(-d) + " less.";
  }
  /* "I don't know": the bill at the rollback rate for several averages, plus the home's own change exactly
     (which returns last year's bill); presets within 0.05 points of it give way to it. */
  function table(bill, m) {
    view(false); $("rb-dn").hidden = true; $("rb-r").hidden = true;
    var own = m * 100, gs = [0, 5, 10].filter(function (g) { return Math.abs(g - own) >= 0.05; }).concat([own]), rows = [];
    gs.sort(function (x, y) { return x - y; });
    gs.forEach(function (g) {
      var a = bill * (1 + m) / (1 + g / 100), isOwn = g === own;
      rows.push('<tr' + (isOwn ? ' class="rb-own"' : '') + '><td>' + signed(g / 100) + (isOwn ? '<span class="rb-tsub">same as your home</span>' : '') + '</td><td class="rb-tbill">' + money(a) + '</td><td><span aria-hidden="true">' + signed(a / bill - 1) + '</span><span class="sr">' + words(a / bill - 1).slice(1, -1) + '</span></td></tr>');
    });
    $("rb-tb").innerHTML = rows.join("");
    var b = bill * (1 + m); chg(bill, b, "rb-b3", "rb-b3c", "rb-b3s");
    summary(sumPrefix + money(b) + " at last year's rates · At the rollback rate, it depends on the average change");
    return "At last year's rates, " + money(b) + ". At the rollback rate, it depends on the average change; the table lists " + gs.length + " averages, from " + signed(gs[0] / 100) + " to " + signed(gs[gs.length - 1] / 100) + ".";
  }
  function calcWhole() {
    var hc = homeChange(), bill = num("rb-bill"), mine = hc.m === null ? null : hc.m * 100, avg, oldRate = null, bad = null, msg = "", warn = "", wid = null, rateBad = false;
    plain("");
    if (input === 1) { avg = num("rb-avg"); oldRate = num("rb-rate"); if (avg !== null && !isNaN(avg)) avg /= 100; if (oldRate !== null && (isNaN(oldRate) || oldRate <= 0)) { rateBad = true; oldRate = null; } }
    else if (input === 2) { var o = num("rb-old"), r = num("rb-rb"); if (o > 0 && r > 0) { avg = o / r - 1; oldRate = o; } else { avg = NaN; bad = !(o > 0) ? "rb-old" : "rb-rb"; } }
    var tp = input === 1 ? tinyPct($("rb-avg").value) : "";
    sayW($("rb-avg-w"), tp); if (tp) mark($("rb-avg"), true, "rb-avg-w");
    if (hc.msg) { bad = hc.bad; msg = hc.msg; }
    else if (bill === null || isNaN(bill) || bill <= 0) { bad = "rb-bill"; msg = "Enter last year's bill in dollars."; }
    else if (input !== 3 && (avg === null || isNaN(avg) || avg <= -1)) { bad = bad || "rb-avg"; msg = input === 1 ? "Enter the average change, in percent." : "Enter both rates, as numbers above zero."; }
    say($("rb-e"), msg);
    if (msg) { mark($(bad), true, "rb-e"); say($("rb-w"), ""); say($("rb-re"), ""); blank(); return msg; }
    if (bill > 1e6) { wid = "rb-bill"; warn = "the bill is over $1 million."; }
    else if (hc.warn) { wid = "rb-v1"; warn = hc.warn; }
    else if (input !== 3 && !tp && (avg < -0.3 || avg > 0.5)) { wid = input === 1 ? "rb-avg" : "rb-rb"; warn = "an average change of " + signed(avg) + " is unusual in one year."; }
    sayW($("rb-w"), warn); if (wid) mark($(wid), true, "rb-w");
    var m = mine / 100, pre = (tp ? "Check: " + tp + " " : "") + (warn ? "Check: " + warn + " " : "");
    if (input === 3) { say($("rb-re"), ""); return pre + table(bill, m); }
    say($("rb-re"), rateBad ? "Enter last year's rate as a number above zero, or leave it blank." : ""); if (rateBad) mark($("rb-rate"), true, "rb-re");
    var a = bill * (1 + m) / (1 + avg), b = bill * (1 + m);
    var dsay = totals(bill, a, b);
    var cut = 1 - 1 / (1 + avg), u = $("rb-unit").value;
    $("rb-r").hidden = false;
    $("rb-r").textContent = "The rollback rate is " + (Math.abs(cut) < 0.0005 ? "the same as" : p1(cut) + (cut > 0 ? " below" : " above")) + " last year's rate" +
      (input === 2 ? ", so existing property, taken together, " + (avg >= 0 ? "rose" : "fell") + " about " + p1(avg) + "." : ".");
    $("rb-rl").hidden = !(input === 1 && oldRate);
    $("rb-rl").textContent = input === 1 && oldRate ? "The rollback rate would be " + fmtRate(oldRate / (1 + avg), u) + "." : "";
    var tot = num("rb-tot"), nw = num("rb-new"), nmsg = "";
    if (tot === null || isNaN(tot) || tot <= 0) { nmsg = "Enter last year's total taxable value in dollars."; mark($("rb-tot"), true, "rb-ne"); }
    else if (nw !== null && (isNaN(nw) || nw < 0)) { nmsg = "Enter new construction as zero or more, in dollars."; mark($("rb-new"), true, "rb-ne"); }
    say($("rb-ne"), nmsg);
    if (nmsg) $("rb-town").textContent = "–";
    else { var n = nw ? nw / tot : 0;
      var g1 = n / (1 + avg), g0 = avg + n, mv = function (g) { return Math.abs(g) < 0.0005 ? "the same as" : p1(g) + (g > 0 ? " more than" : " less than"); };
      $("rb-town").textContent = "At the rollback rate, a government with these figures collects " + mv(g1) + " last year" + (n && g1 > 0 ? ", all of the increase from new construction" : "") + ". At last year's rate, it collects " + mv(g0) + " last year."; }
    return pre + "At the rollback rate, " + money(a) + ". At last year's rates, " + money(b) + ". " + dsay + (rateBad ? " The rate you entered isn't a number above zero." : "") + (nmsg ? " " + nmsg : "");
  }
  function calcLines() {
    var hcLine = homeChange(), homeNeeded = false;
    say($("rb-w"), ""); say($("rb-re"), ""); say($("rb-avg-w"), ""); $("rb-r").hidden = true; plain("");
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
      var w = "", wf = null, tp = tinyPct($("g-" + id).value);
      if (ov && (f.v < -50 || f.v > 100)) { w = "a value change of " + signed(f.v / 100) + " is unusual in one year."; wf = "b"; }
      else if (tp) { w = tp; wf = "g"; }
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
    if (!used) {
      if (homeMsg || notes.length) { say($("rb-e"), homeMsg ? homeMsg : "Fix the line marked below."); blank(); return notes.join(" "); }
      /* Nothing filled in yet: a plain pointer, not an error. */
      say($("rb-e"), "");
      var p = input === 3 && !linesEdited ? "Line by line needs each government's average change. If you don't know it, choose The whole bill and \"I don't know\" to see your bill at several averages." : "Fill in last year's tax and the average change for at least one line.";
      plain(p); blank("No estimate yet: fill in a line above."); return p;
    }
    say($("rb-e"), homeMsg);
    var wparts = []; if (homeWarn) wparts.push(homeWarn); if (skipped.length) wparts.push("the totals leave out " + skipped.join(", ") + ".");
    if (wparts.length) sayW($("rb-w"), wparts.join(" Also, "));
    var dsay = totals(base, A, B);
    return (notes.length ? notes.join(" ") + " " : "") + (used === 1 ? "For the 1 line counted" : "For the " + used + " lines counted") + ": at the rollback rates, " + money(A) + ". At last year's rates, " + money(B) + ". " + dsay + (skipped.length ? " Not counted: " + skipped.join(", ") + "." : "");
  }
  function calc() {
    clearMarks();
    var ex = exampleState(); sumPrefix = ex.all ? "Example: " : ex.left.length ? "With some example figures: " : "";
    var t = mode === 1 ? calcWhole() : calcLines();
    showExample(ex);
    /* Speak the example list only when it changes, not on every pause in typing. */
    var exNow = ex.all ? "all" : ex.left.join("|"), exSay = "";
    if (exNow !== lastEx) exSay = ex.all ? "" : ex.left.length ? " Still the example's: " + andList(ex.left) + "." : " None of the example's figures are left.";
    announce((ex.all ? "Example figures. " : "") + t + exSay);
    lastEx = exNow;
    place();
  }
  function announce(t) { clearTimeout(timer); timer = setTimeout(function () { $("rb-live").textContent = t; }, 700); }
  /* Show the summary while the calculator's top is well on screen and its first result isn't yet. */
  var queued = false;
  function place() {
    if (queued) return; queued = true;
    requestAnimationFrame(function () {
      queued = false;
      var H = window.innerHeight, top = $("rb-h").getBoundingClientRect().top,
          fig = !$("rb-unk").hidden ? $("rb-tb").querySelector("tr") : $("rb-a"),
          figTop = fig ? fig.getBoundingClientRect().top : -1;
      $("rb-sum").classList.toggle("off", !(top < H - 90 && figTop > H - 64));
    });
  }
  window.addEventListener("scroll", place, { passive: true });
  window.addEventListener("resize", place);
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
    var bill = num("rb-bill"), g = input === 1 ? num("rb-avg") : input === 2 && num("rb-old") > 0 && num("rb-rb") > 0 ? (num("rb-old") / num("rb-rb") - 1) * 100 : null;
    var vals = { t: bill > 0 ? Math.round(bill).toLocaleString("en-US") : "", g: g == null || isNaN(g) ? "" : Math.round(g * 10) / 10 };
    if (first) { var id = first.getAttribute("data-id"); $("t-" + id).value = vals.t; $("g-" + id).value = vals.g; return; }
    seeded = true; addLine(vals); addLine({});
  }
  function moreLabel() { $("rb-moresum").textContent = input === 1 ? "More detail: the rate, and what the governments collect" : "More detail: what the governments collect"; }
  function setMode(k) { mode = k; $("rb-m1").setAttribute("aria-pressed", String(k === 1)); $("rb-m2").setAttribute("aria-pressed", String(k === 2)); $("rb-whole").hidden = k !== 1; $("rb-lines").hidden = k !== 2; $("rb-more").hidden = k !== 1 || input === 3; if (k === 2) seed(); calc(); }
  function setInput(k) { input = k; ["rb-t1", "rb-t2", "rb-t3"].forEach(function (b, i) { $(b).setAttribute("aria-pressed", String(k === i + 1)); }); $("rb-p1").hidden = k !== 1; $("rb-p2").hidden = k !== 2; $("rb-p3").hidden = k !== 3; $("rb-ratebox").hidden = k !== 1; $("rb-more").hidden = mode !== 1 || k === 3; moreLabel(); calc(); }
  $("rb-m1").addEventListener("click", function () { setMode(1); });
  $("rb-m2").addEventListener("click", function () { setMode(2); });
  $("rb-t1").addEventListener("click", function () { setInput(1); });
  $("rb-t2").addEventListener("click", function () { setInput(2); });
  $("rb-t3").addEventListener("click", function () { setInput(3); });
  $("rb-add").addEventListener("click", function () { addLine({}, true); calc(); });
  $("rb-more").addEventListener("toggle", calc);
  ["rb-v0", "rb-v1", "rb-bill", "rb-avg", "rb-old", "rb-rb", "rb-rate", "rb-tot", "rb-new"].forEach(function (id) { $(id).addEventListener("input", calc); });
  $("rb-unit").addEventListener("change", calc);
  calc(); clearTimeout(timer);
})();
})();
