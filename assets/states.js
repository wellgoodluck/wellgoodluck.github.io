/* "Your State's Population" (Nov 22, 2026). Mounted on <div class="sp-mount" data-src="/assets/states.json">; fetches the
   state file that tools/make_states.py writes from the Census Bureau's latest vintage (population via FRED, components
   of change from the vintage's ALLDATA file). Everything shown is computed from that file: the two lead sentences, the
   population line since 1900 and the components bars. The reader's state goes in the link only when they copy one with
   it ("#k=<state>"), and changing the state rewrites the hash so a copied address carries it. The movers section
   (Nov 22, 2026, second batch) reads the file's "flows" block, the American Community Survey state-to-state table:
   the top five states each way, each with its net and the survey's 90% margins; a net or a ranking the margins
   can't separate is said to be too close to call. The cost-of-living section (Nov 22, batch f or later) reads "col":
   BEA's price level, income per person and income at U.S.-average prices for one year, ranked here among the 50
   states and DC. Styles: the shared calculator box (.rb) plus .sp in
   assets/site.css. */
(function () {
  var mount = document.querySelector(".sp-mount");
  if (!mount) return;
  var SVGNS = "http://www.w3.org/2000/svg";
  var D = null, ab = "NC";

  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (text != null) n.textContent = text;
    return n;
  }
  function svgEl(tag, attrs) {
    var n = document.createElementNS(SVGNS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    return n;
  }
  function fmt(n) { return (n < 0 ? "−" : "") + Math.abs(n).toLocaleString("en-US"); }
  function f1(x) { return (Math.round(x * 10) / 10).toFixed(1); }
  function ord(n) { return n + (n % 100 >= 11 && n % 100 <= 13 ? "th" : n % 10 === 1 ? "st" : n % 10 === 2 ? "nd" : n % 10 === 3 ? "rd" : "th"); }
  function millions(th) {   /* a value in thousands, in words */
    if (th >= 10000) return f1(th / 1000).replace(/\.0$/, "") + " million";
    if (th >= 950) return f1(th / 1000) + " million";
    return Math.round(th).toLocaleString("en-US") + ",000";
  }

  /* ---------- the two lead sentences, all from the data ---------- */
  function domClause(s, i, states) {
    var dom = s.dom[i];
    if (Math.abs(dom) < 500) return "about as many people moved in from other states as moved out";
    var k, r = 1;
    for (k in states) {
      if (dom > 0 && states[k].dom[i] > dom) r++;
      if (dom < 0 && states[k].dom[i] < dom) r++;
    }
    var rank = r === 1 ? "the largest" : "the " + ord(r) + "-largest";
    return dom > 0
      ? fmt(dom) + " more people moved in from other states than moved out — " + rank + " net gain from other states in the country"
      : fmt(-dom) + " more people moved out to other states than moved in — " + rank + " net loss to other states in the country";
  }
  function sentences(s) {
    var ys = D.comp_years, i = ys.length - 1, y = ys[i];
    var now = s.est["y" + y], prev = s.est["y" + (y - 1)];
    var change = now - prev, pct = Math.abs(change) / prev * 100;
    var pctTxt = pct < 0.05 ? "less than 0.1%" : f1(pct) + "%";
    var p1 = cap(the(s.name)) + " had " + fmt(now) + " residents in July " + y + ": " +
      (change >= 0 ? "up " + fmt(change) : "down " + fmt(-change)) + ", or " + pctTxt + ", over the year.";
    var nat = s.natural[i], intl = s.intl[i];
    var p2 = "Where that came from: " +
      (nat >= 0 ? "births outnumbered deaths by " + fmt(nat) : "deaths outnumbered births by " + fmt(-nat)) + "; " +
      (intl >= 0 ? fmt(intl) + " more people arrived from other countries than left" : fmt(-intl) + " more people left for other countries than arrived") + "; and " +
      domClause(s, i, D.states) + ".";
    var first = s.pop[0], last = s.pop[s.pop.length - 1], ratio = last / first;
    var times = ratio >= 10 ? Math.round(ratio) : Math.round(ratio * 10) / 10;
    var p3 = "The chart runs back to " + s.first + ", when " + the(s.name) + " had about " + millions(first) +
      " people — today's figure is about " + times + " times that.";
    return [p1, p2, p3];
  }

  /* ---------- movers: which states people came from and went to ---------- */
  function pname(k) { return D.states[k] ? D.states[k].name : (D.flows.names[k] || k); }
  function the(n) { return n === "District of Columbia" ? "the " + n : n; }   /* in a sentence; tables and the picker keep the bare name */
  function cap(t) { return t.charAt(0).toUpperCase() + t.slice(1); }
  function moe2(a, b) { return Math.sqrt(a * a + b * b); }
  function apart(e1, m1, e2, m2) { return Math.abs(e1 - e2) > moe2(m1, m2); }   /* differ by more than the margin of the difference */
  function signed(n) { return (n > 0 ? "+" : "") + fmt(n); }
  function flowSentences(s, f) {
    var y = D.flows.year, a = f.in[0], b = f.in[1], c = f.out[0], d = f.out[1], nm = the(s.name);
    var p4 = "In the " + y + " survey, the most people moving to " + nm + " came from " + the(pname(a[0])) + ": " +
      fmt(a[1]) + " (±" + fmt(a[2]) + ")" +
      (b && !apart(a[1], a[2], b[1], b[2]) ? ", though " + the(pname(b[0])) + "’s " + fmt(b[1]) + " is too close to call" : "") +
      ". The most moving out went to " + the(pname(c[0])) + ": " + fmt(c[3]) + " (±" + fmt(c[4]) + ")" +
      (d && !apart(c[3], c[4], d[3], d[4]) ? ", though " + the(pname(d[0])) + "’s " + fmt(d[3]) + " is too close to call" : "") + ".";
    function net(r) { return r[1] - r[3]; }
    function nmoe(r) { return moe2(r[2], r[4]); }
    function clause(list, word, prep) {
      if (!list || !list.length) return null;
      var r = list[0], r2 = list[1];
      return "the biggest clear net " + word + " was " + prep + " " + the(pname(r[0])) + " (" + signed(net(r)) + ")" +
        (r2 && !apart(net(r), nmoe(r), net(r2), nmoe(r2)) ? ", with " + the(pname(r2[0])) + " (" + signed(net(r2)) + ") too close to call" : "");
    }
    var gt = clause(f.gain, "gain", "from"), lt = clause(f.loss, "loss", "to"), p5;
    if (gt && lt) p5 = "Counting both directions, " + gt + "; " + lt + ".";
    else if (gt) p5 = "Counting both directions, " + gt + "; no state clearly took more people from " + nm + " than it sent.";
    else if (lt) p5 = "Counting both directions, " + lt + "; no state clearly sent " + nm + " more people than it took.";
    else p5 = "Counting both directions, no state’s exchange with " + nm + " is clearly a net gain or loss.";
    return [p4, p5 + " “Clear” means the net is larger than the survey’s margin of error."];
  }
  function flowTable(tb, rows, rank) {   /* rank: 1 = Moved in, 2 = Moved out, the column the table is sorted by, set in bold */
    tb.innerHTML = "";
    rows.forEach(function (r) {
      var tr = el("tr", {});
      tr.appendChild(el("td", {}, pname(r[0])));
      [[r[1], r[2]], [r[3], r[4]]].forEach(function (v, i) {
        var td = el("td", i + 1 === rank ? { class: "sp-rank" } : {});
        if (v[0] == null) td.textContent = "n/a";
        else { td.appendChild(document.createTextNode(fmt(v[0]))); td.appendChild(el("span", { class: "rb-tsub" }, "±" + fmt(v[1]))); }
        tr.appendChild(td);
      });
      var nt = el("td", {});
      if (r[1] == null || r[3] == null) nt.textContent = "n/a";
      else nt.textContent = signed(r[1] - r[3]) + (apart(r[1], r[2], r[3], r[4]) ? "" : "*");
      tr.appendChild(nt);
      tb.appendChild(tr);
    });
  }
  function flowBox(id, cap, rank) {
    var wrap = el("div", { class: "sp-ft" });
    var t = el("table", { class: "rb-t" });
    t.appendChild(el("caption", { class: "rb-tcap", id: id + "-c" }, cap));
    var hr = el("tr", {});
    ["State", "Moved in", "Moved out", "Net"].forEach(function (h, i) { hr.appendChild(el("th", i === rank ? { scope: "col", class: "sp-rank" } : { scope: "col" }, h)); });
    var th = el("thead", {}); th.appendChild(hr); t.appendChild(th);
    t.appendChild(el("tbody", { id: id }));
    wrap.appendChild(t);
    return wrap;
  }
  function renderFlows(s) {
    var f = D.flows && D.flows.states[ab], sec = document.getElementById("sp-flows");
    if (!sec) return;
    if (!f || !f.in.length || !f.out.length) { sec.hidden = true; return; }
    sec.hidden = false;
    var t = flowSentences(s, f);
    document.getElementById("sp-p4").textContent = t[0];
    document.getElementById("sp-p5").textContent = t[1];
    document.getElementById("sp-tin-c").textContent = "Came from: the five states that sent " + the(s.name) + " the most people";
    document.getElementById("sp-tout-c").textContent = "Went to: the five states that took the most from " + the(s.name);
    flowTable(document.getElementById("sp-tin"), f.in, 1);
    flowTable(document.getElementById("sp-tout"), f.out, 2);
  }

  /* ---------- cost of living: what a dollar is worth here ---------- */
  function rankOf(k, i) {   /* 1 = highest, among the 50 states and DC */
    var S = D.col.states, v = S[k][i], r = 1;
    Object.keys(S).forEach(function (o) { if (S[o][i] > v) r++; });
    return r;
  }
  function rankWords(r) {
    var n = Object.keys(D.col.states).length;
    if (r === 1) return "the highest";
    if (r === n) return "the lowest";
    if (r > n - 5) return "the " + ord(n - r + 1) + " lowest";
    return "the " + ord(r) + " highest";
  }
  function priceRank(r, gap) {   /* above average counts from the top, below from the bottom; only the top and bottom 15 */
    var n = Object.keys(D.col.states).length, k = gap > 0 ? r : n - r + 1;
    if (k > 15) return "";   /* a mid-pack rank says little */
    return ", " + (k === 1 ? "the " : "the " + ord(k) + " ") + (gap > 0 ? "highest" : "lowest");
  }
  function colSentences(s) {
    var c = D.col.states[ab], y = D.col.year, nm = the(s.name);
    var rn = rankOf(ab, 1), rp = rankOf(ab, 0), ra = rankOf(ab, 2), gap = c[0] - 100;
    var p6 = "In " + y + ", income per person in " + nm + " was $" + fmt(c[1]) + ", " + rankWords(rn) +
      " of the 50 states and DC (for the whole country, $" + fmt(D.col.us_pcpi) + "). ";
    if (Math.abs(gap) < 0.5) p6 += "Prices there were about at the national average.";
    else p6 += "Prices there ran " + f1(Math.abs(gap)) + "% " + (gap > 0 ? "above" : "below") +
      " the national average" + priceRank(rp, gap) + ".";
    var move = rn - ra;
    var p7 = "At national-average prices, that income would be worth about $" + fmt(c[2]) + (c[3] ? "*" : "") + ", " +
      rankWords(ra) + ". " + (move === 0 ? "Counting prices leaves " + nm + " in the same place." :
        "Counting prices moves " + nm + " " + (move > 0 ? "up " : "down ") + Math.abs(move) + (Math.abs(move) === 1 ? " place." : " places."));
    return [p6, p7];
  }
  function renderCol(s) {
    var sec = document.getElementById("sp-col");
    if (!sec) return;
    if (!D.col.states[ab]) { sec.hidden = true; return; }
    sec.hidden = false;
    var t = colSentences(s);
    document.getElementById("sp-p6").textContent = t[0];
    document.getElementById("sp-p7").textContent = t[1];
    document.getElementById("sp-colpa").hidden = !D.col.states[ab][3];
  }

  /* ---------- charts ---------- */
  function niceTicks(lo, hi, count) {
    var span = hi - lo || 1, step = Math.pow(10, Math.floor(Math.log(span / count) / Math.LN10));
    var err = span / count / step;
    step *= err >= 7.5 ? 10 : err >= 3.5 ? 5 : err >= 1.5 ? 2 : 1;
    var ticks = [], v = Math.ceil(lo / step) * step;
    for (; v <= hi + step / 1e6; v += step) ticks.push(Math.round(v * 1e6) / 1e6);
    return { ticks: ticks, step: step };
  }
  function tipFor(box) {
    var tip = box.querySelector(".tip");
    if (!tip) { tip = el("div", { class: "tip" }); box.appendChild(tip); }
    return tip;
  }
  function placeTip(tip, box, cx, cy) {
    tip.style.display = "block";
    var bw = box.clientWidth, tw = tip.offsetWidth, th = tip.offsetHeight;
    var x = Math.max(0, Math.min(cx + 12, bw - tw)), yy = cy - th - 10;
    if (yy < 0) yy = cy + 14;
    tip.style.left = x + "px"; tip.style.top = yy + "px";
  }

  function drawLine(box, s) {
    var old = box.querySelector("svg"); if (old) old.remove();
    var tip = tipFor(box);
    var width = Math.max(240, box.clientWidth || 480), height = 190, mL = 40, mR = 14, mT = 12, mB = 24;
    var iw = width - mL - mR, ih = height - mT - mB;
    var vals = s.pop, first = s.first, lastYear = first + vals.length - 1;
    var hi = 0, j;
    for (j = 0; j < vals.length; j++) if (vals[j] != null && vals[j] > hi) hi = vals[j];
    hi *= 1.08;
    var xs = function (yr) { return mL + (yr - first) / (lastYear - first) * iw; };
    var ys = function (v) { return mT + (hi - v) / hi * ih; };
    var svg = svgEl("svg", { viewBox: "0 0 " + width + " " + height, width: width, height: height, role: "img",
      "aria-label": s.name + " population, " + first + " to " + lastYear });
    var t = niceTicks(0, hi, 4), axis = svgEl("g", { class: "axis" });
    t.ticks.forEach(function (v) {
      svg.appendChild(svgEl("line", { class: v === 0 ? "zero" : "grid-line", x1: mL, x2: width - mR, y1: ys(v), y2: ys(v) }));
      var dec = t.step >= 1000 ? 0 : t.step >= 100 ? 1 : 2;
      var tx = svgEl("text", { x: mL - 6, y: ys(v) + 4, "text-anchor": "end" });
      tx.textContent = v === 0 ? "0" : (v / 1000).toFixed(dec) + "M";
      axis.appendChild(tx);
    });
    for (j = Math.ceil(first / 25) * 25; j <= lastYear; j += 25) {
      var tx2 = svgEl("text", { x: xs(j), y: height - 6, "text-anchor": "middle" });
      tx2.textContent = j;
      axis.appendChild(tx2);
    }
    svg.appendChild(axis);
    var path = "";
    for (j = 0; j < vals.length; j++) {
      if (vals[j] == null) continue;
      path += (path ? "L" : "M") + xs(first + j).toFixed(1) + "," + ys(vals[j]).toFixed(1);
    }
    svg.appendChild(svgEl("path", { class: "line", d: path }));
    svg.appendChild(svgEl("circle", { class: "end", cx: xs(lastYear), cy: ys(vals[vals.length - 1]), r: 4 }));
    var xhair = svgEl("line", { class: "xhair", x1: 0, x2: 0, y1: mT, y2: mT + ih, visibility: "hidden" });
    var hdot = svgEl("circle", { class: "hover-dot", r: 4, visibility: "hidden" });
    var hit = svgEl("rect", { class: "hit", x: mL, y: mT, width: iw, height: ih });
    svg.appendChild(xhair); svg.appendChild(hdot); svg.appendChild(hit);
    function show(clientX) {
      var rect = svg.getBoundingClientRect();
      var yr = Math.round(first + ((clientX - rect.left) * (width / rect.width) - mL) / iw * (lastYear - first));
      yr = Math.max(first, Math.min(lastYear, yr));
      var v = vals[yr - first];
      if (v == null) return;
      var cx = xs(yr), cy = ys(v);
      xhair.setAttribute("x1", cx); xhair.setAttribute("x2", cx); xhair.setAttribute("visibility", "visible");
      hdot.setAttribute("cx", cx); hdot.setAttribute("cy", cy); hdot.setAttribute("visibility", "visible");
      tip.innerHTML = "<b>" + millions(v) + "</b><br>" + yr;
      placeTip(tip, box, cx * (rect.width / width), cy * (rect.height / height));
    }
    function hide() { xhair.setAttribute("visibility", "hidden"); hdot.setAttribute("visibility", "hidden"); tip.style.display = "none"; }
    hit.addEventListener("mousemove", function (e) { show(e.clientX); });
    hit.addEventListener("touchstart", function (e) { show(e.touches[0].clientX); }, { passive: true });
    hit.addEventListener("mouseleave", hide);
    hit.addEventListener("touchend", hide);
    box.appendChild(svg);
  }

  function drawBars(box, s) {
    var old = box.querySelector("svg"); if (old) old.remove();
    var tip = tipFor(box);
    var width = Math.max(240, box.clientWidth || 480), height = 190, mL = 46, mR = 14, mT = 12, mB = 24;
    var iw = width - mL - mR, ih = height - mT - mB;
    var ys = D.comp_years, series = [s.natural, s.intl, s.dom], j, k;
    var lo = 0, hi = 0;
    for (j = 0; j < ys.length; j++) for (k = 0; k < 3; k++) {
      if (series[k][j] < lo) lo = series[k][j];
      if (series[k][j] > hi) hi = series[k][j];
    }
    var pad = (hi - lo || 1) * 0.08; hi += pad; if (lo < 0) lo -= pad;
    var yy = function (v) { return mT + (hi - v) / (hi - lo) * ih; };
    var svg = svgEl("svg", { viewBox: "0 0 " + width + " " + height, width: width, height: height, role: "img",
      "aria-label": s.name + ", yearly change from births minus deaths, other countries and other states, " + ys[0] + " to " + ys[ys.length - 1] });
    var t = niceTicks(lo, hi, 4), axis = svgEl("g", { class: "axis" });
    t.ticks.forEach(function (v) {
      svg.appendChild(svgEl("line", { class: v === 0 ? "zero" : "grid-line", x1: mL, x2: width - mR, y1: yy(v), y2: yy(v) }));
      var tx = svgEl("text", { x: mL - 6, y: yy(v) + 4, "text-anchor": "end" });
      tx.textContent = Math.abs(v) >= 1000 ? (v < 0 ? "−" : "") + Math.round(Math.abs(v) / 1000) + "k" : String(v);
      axis.appendChild(tx);
    });
    var group = iw / ys.length, bw = Math.min(26, (group - 14) / 3), cls = ["b-nat", "b-intl", "b-dom"];
    for (j = 0; j < ys.length; j++) {
      var cx0 = mL + group * j + group / 2 - bw * 1.5;
      for (k = 0; k < 3; k++) {
        var v = series[k][j], y0 = yy(Math.max(0, v)), h = Math.abs(yy(v) - yy(0));
        svg.appendChild(svgEl("rect", { class: cls[k], x: (cx0 + k * bw).toFixed(1), y: y0.toFixed(1), width: Math.max(2, bw - 2).toFixed(1), height: Math.max(1, h).toFixed(1) }));
      }
      var lbl = svgEl("text", { x: mL + group * j + group / 2, y: height - 6, "text-anchor": "middle" });
      lbl.textContent = ys[j];
      axis.appendChild(lbl);
    }
    svg.appendChild(axis);
    var hit = svgEl("rect", { class: "hit", x: mL, y: mT, width: iw, height: ih });
    svg.appendChild(hit);
    function show(clientX, clientY) {
      var rect = svg.getBoundingClientRect();
      var px = (clientX - rect.left) * (width / rect.width);
      var j2 = Math.max(0, Math.min(ys.length - 1, Math.floor((px - mL) / group)));
      tip.innerHTML = "<b>July " + (ys[j2] - 1) + " to June " + ys[j2] + "</b><br>Births minus deaths: " + fmt(s.natural[j2]) +
        "<br>Other countries, net: " + fmt(s.intl[j2]) + "<br>Other states, net: " + fmt(s.dom[j2]);
      placeTip(tip, box, px * (rect.width / width), (clientY - rect.top));
    }
    function hide() { tip.style.display = "none"; }
    hit.addEventListener("mousemove", function (e) { show(e.clientX, e.clientY); });
    hit.addEventListener("touchstart", function (e) { show(e.touches[0].clientX, e.touches[0].clientY); }, { passive: true });
    hit.addEventListener("mouseleave", hide);
    hit.addEventListener("touchend", hide);
    box.appendChild(svg);
  }

  /* ---------- page ---------- */
  function render() {
    var s = D.states[ab], lead = sentences(s);
    document.getElementById("sp-p1").textContent = lead[0];
    document.getElementById("sp-p2").textContent = lead[1];
    document.getElementById("sp-p3").textContent = lead[2];
    document.getElementById("sp-lt").textContent = "Population since " + s.first;
    drawLine(document.getElementById("sp-line"), s);
    drawBars(document.getElementById("sp-bars"), s);
    renderFlows(s);
    if (D.col) renderCol(s);
    document.getElementById("sp-copied").textContent = "";
  }

  function build() {
    var names = Object.keys(D.states).map(function (k) { return [D.states[k].name, k]; });
    names.sort(function (a, b) { return a[0] < b[0] ? -1 : 1; });
    var box = el("div", { class: "rb sp" });
    var f = el("p", { class: "rb-f" });
    var lab = el("label", { for: "sp-state" }, "State");
    var sel = el("select", { id: "sp-state" });
    names.forEach(function (n) { sel.appendChild(el("option", { value: n[1] }, n[0])); });
    f.appendChild(lab); f.appendChild(sel);
    box.appendChild(f);
    var leadBox = el("div", { class: "sp-lead" });
    ["sp-p1", "sp-p2"].forEach(function (id) { leadBox.appendChild(el("p", { id: id })); });
    box.appendChild(leadBox);
    box.appendChild(el("p", { class: "sp-ct", id: "sp-lt" }, "Population since 1900"));
    box.appendChild(el("div", { class: "sp-chart", id: "sp-line" }));
    box.appendChild(el("p", { id: "sp-p3", class: "sp-note" }));
    box.appendChild(el("p", { class: "sp-ct" }, "Where each year's change came from, people"));
    box.appendChild(el("div", { class: "sp-chart", id: "sp-bars" }));
    var key = el("p", { class: "sp-key" });
    [["b-nat", "Births minus deaths"], ["b-intl", "Other countries, net"], ["b-dom", "Other states, net"]].forEach(function (p) {
      var it = el("span", {});
      it.appendChild(el("span", { class: "sw " + p[0], "aria-hidden": "true" }));
      it.appendChild(document.createTextNode(p[1]));
      key.appendChild(it);
    });
    box.appendChild(key);
    if (D.flows) {
      var sec = el("div", { id: "sp-flows", class: "sp-flows" });
      sec.appendChild(el("p", { class: "sp-ct" }, "Where people came from and where they went, " + D.flows.year));
      sec.appendChild(el("p", { id: "sp-p4" }));
      sec.appendChild(el("p", { id: "sp-p5" }));
      var grid = el("div", { class: "sp-ftgrid" });
      grid.appendChild(flowBox("sp-tin", "Came from", 1));
      grid.appendChild(flowBox("sp-tout", "Went to", 2));
      sec.appendChild(grid);
      var fn = el("p", { class: "sp-note" });
      fn.appendChild(document.createTextNode("Moved in and moved out count people who said they had lived in the other state a year before answering the Census Bureau’s " +
        D.flows.year + " American Community Survey, a sample survey; ± is its 90% margin of error, and * marks a net smaller than its margin. It covers a different period than the estimates above, so it won’t match them. "));
      var src = el("a", { href: D.flows.source }, "Census Bureau, state-to-state migration flows, " + D.flows.year);
      fn.appendChild(src);
      fn.appendChild(document.createTextNode("."));
      sec.appendChild(fn);
      box.appendChild(sec);
    }
    if (D.col) {
      var cs = el("div", { id: "sp-col", class: "sp-col" });
      cs.appendChild(el("p", { class: "sp-ct" }, "What a dollar is worth here, " + D.col.year));
      cs.appendChild(el("p", { id: "sp-p6" }));
      cs.appendChild(el("p", { id: "sp-p7" }));
      var cn = el("p", { class: "sp-note" });
      cn.appendChild(document.createTextNode("Income per person is personal income divided by everyone who lives there, children included. Personal income counts pay, business and investment income, and government benefits, including non-cash ones such as employer-paid health insurance and Medicare; it is measured before income taxes but after Social Security and Medicare payroll taxes, and leaves out capital gains. It is an average, pulled up by high earners, not what a typical worker takes home. Prices compare what people in each state typically buy, rent included, with what it would cost at national-average prices. The worth-at-national-prices figure is the Bureau of Economic Analysis’s own estimate, adjusted so the states add up to the national total, so the three figures won’t divide out exactly. "));
      var pa = el("span", { id: "sp-colpa" }, "* For Pennsylvania, FRED doesn’t carry the bureau’s " + D.col.year + " per-person figure, so this one is the bureau’s total for the state divided by its population. ");
      cn.appendChild(pa);
      var csrc = el("a", { href: D.col.release }, "Bureau of Economic Analysis, " + D.col.released);
      cn.appendChild(csrc);
      cn.appendChild(document.createTextNode("."));
      cs.appendChild(cn);
      box.appendChild(cs);
    }
    var share = el("p", { class: "sp-share" });
    var copy = el("button", { type: "button", class: "rb-act", id: "sp-copy" }, "Copy a link with this state");
    share.appendChild(copy);
    share.appendChild(el("span", { id: "sp-copied", class: "sp-copied", role: "status" }));
    box.appendChild(share);
    mount.innerHTML = "";
    mount.appendChild(box);

    sel.value = ab;
    sel.addEventListener("change", function () {
      ab = sel.value;
      if (history.replaceState) history.replaceState(null, "", "#k=" + ab.toLowerCase());
      render();
    });
    copy.addEventListener("click", function () {
      var u = location.href.split("#")[0] + "#k=" + ab.toLowerCase(), out = document.getElementById("sp-copied");
      var fallback = function () { out.innerHTML = '<label for="sp-link">Copy this link:</label> <input type="text" id="sp-link" readonly>'; var i = document.getElementById("sp-link"); i.value = u; i.focus(); i.select(); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(u).then(function () { out.textContent = "Link copied."; }, fallback);
      else fallback();
    });
    var timer = null;
    window.addEventListener("resize", function () {
      clearTimeout(timer);
      timer = setTimeout(function () { var s = D.states[ab]; drawLine(document.getElementById("sp-line"), s); drawBars(document.getElementById("sp-bars"), s); }, 150);
    });
    render();
  }

  var m = (location.hash.match(/k=([a-z]{2})/i) || [])[1];
  var src = mount.getAttribute("data-src") || "/assets/states.json";
  fetch(src).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }).then(function (d) {
    D = d;
    if (m && D.states[m.toUpperCase()]) ab = m.toUpperCase();
    build();
  }).catch(function () {
    mount.innerHTML = '<p class="rb-noscript">The state figures didn’t load. This is usually temporary; reload the page to try again.</p>';
  });
})();
