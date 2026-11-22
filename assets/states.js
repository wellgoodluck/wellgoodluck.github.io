/* "Your State's Population" (Nov 22, 2026). Mounted on <div class="sp-mount" data-src="/assets/states.json">; fetches the
   state file that tools/make_states.py writes from the Census Bureau's latest vintage (population via FRED, components
   of change from the vintage's ALLDATA file). Everything shown is computed from that file: the two lead sentences, the
   population line since 1900 and the components bars. The reader's state goes in the link only when they copy one with
   it ("#k=<state>"), and changing the state rewrites the hash so a copied address carries it. Styles: the shared
   calculator box (.rb) plus .sp in assets/site.css. */
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
    var p1 = s.name + " had " + fmt(now) + " residents in July " + y + ": " +
      (change >= 0 ? "up " + fmt(change) : "down " + fmt(-change)) + ", or " + pctTxt + ", over the year.";
    var nat = s.natural[i], intl = s.intl[i];
    var p2 = "Where that came from: " +
      (nat >= 0 ? "births outnumbered deaths by " + fmt(nat) : "deaths outnumbered births by " + fmt(-nat)) + "; " +
      (intl >= 0 ? fmt(intl) + " more people arrived from other countries than left" : fmt(-intl) + " more people left for other countries than arrived") + "; and " +
      domClause(s, i, D.states) + ".";
    var first = s.pop[0], last = s.pop[s.pop.length - 1], ratio = last / first;
    var times = ratio >= 10 ? Math.round(ratio) : Math.round(ratio * 10) / 10;
    var p3 = "The chart runs back to " + s.first + ", when " + s.name + " had about " + millions(first) +
      " people — today's figure is about " + times + " times that.";
    return [p1, p2, p3];
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
