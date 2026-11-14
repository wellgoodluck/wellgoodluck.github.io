/* Site search (Nov 14). The search page (/search/), the not-found page (/404.html) and the box on the articles index.
   Pagefind indexes the built site in both workflows and writes /pagefind/; this script loads its pieces from there and
   searches in the browser, so what a reader types isn't sent anywhere. The query lives after # (#q=…&n=…), never after
   ?, because the visit counter (count.js) sends the ? part of every address it counts. Synonyms are a hidden "also"
   meta field, weighted here above titles; the kind label and the chart reading are meta too, weighted 0 so they show
   but don't rank. Rules and wording: DESIGN.md, Site search. */
(function () {
  'use strict';
  var PER = 10;
  var TRY = ['inflation', 'unemployment', 'recession', 'mortgage rates', 'gas prices', 'overdraft'];
  var out = document.querySelector('[data-search-out]');
  var forms = document.querySelectorAll('[data-search-form]');

  // Away from the search page, a form just goes there.
  if (!out) {
    forms.forEach(function (f) {
      f.addEventListener('submit', function (e) {
        e.preventDefault();
        var v = f.querySelector('input').value.trim();
        if (!v) { f.querySelector('input').focus(); return; }
        location.href = '/search/#q=' + encodeURIComponent(v);
      });
    });
    return;
  }

  var form = forms[0];
  var input = form.querySelector('input');
  var live = document.getElementById('s-live');
  var pf = null, loading = null, seq = 0, liveTimer = 0, shown = 0, all = [], lastQ = null;
  var fromPath = out.hasAttribute('data-from-path');
  var nfFirst = fromPath, nfOrig = '', firstRender = true;
  // The 404 says what it did once the words from the address have been searched.
  function nfDek(n, used) {
    var dek = document.getElementById('nf-dek');
    if (!dek) return;
    var left = nfOrig.split(' ').slice(used.split(' ').length).join(' ');
    if (n) dek.textContent = 'We searched the site for the words in that address, \u201c' + used + ',\u201d' +
      (left ? ' leaving out \u201c' + left + ',\u201d' : '') + ' and found these. One of them may be what you were after.';
    else dek.textContent = 'Nothing on the site matches the words in that address. Search below, or start from one of the pages listed.';
  }

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
  }
  function hashQ() {
    var m = location.hash.match(/^#q=([^&]*)/);
    if (!m) return '';
    try { return decodeURIComponent(m[1].replace(/\+/g, ' ')); } catch (e) { return ''; }
  }
  function hashN() {
    var m = location.hash.match(/[&]n=(\d+)/);
    return m ? Math.min(parseInt(m[1], 10), 200) : PER;
  }
  var privacy = document.querySelector('.s-privacy');
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  // Coming back from a result: put the reader where they were.
  window.addEventListener('pagehide', function () {
    try { sessionStorage.setItem('s-scroll', location.hash + '|' + Math.round(scrollY)); } catch (e) {}
  });
  function restoreScroll() {
    try {
      var v = (sessionStorage.getItem('s-scroll') || '').split('|');
      if (v[0] === location.hash && v[1]) window.scrollTo(0, parseInt(v[1], 10));
    } catch (e) {}
  }

  function pathWords() {
    var p = location.pathname.replace(/\.html?$/, '').split('/').filter(Boolean).pop() || '';
    var stop = { the: 1, and: 1, a: 1, an: 1, of: 1, to: 1, it: 1, is: 1, index: 1, articles: 1, chart: 1, tools: 1, how: 1, what: 1, why: 1 };
    return p.split(/[-_.+%20]+/).filter(function (w) { return w.length > 2 && !stop[w.toLowerCase()] && !/^\d+$/.test(w); }).slice(0, 4).join(' ');
  }
  function say(msg, now) {
    clearTimeout(liveTimer);
    liveTimer = setTimeout(function () { live.textContent = ''; setTimeout(function () { live.textContent = msg; }, 30); }, now ? 50 : 900);   // cleared first, so the same message is spoken again
  }
  function load() {
    if (loading) return loading;
    var slow = setTimeout(function () { out.innerHTML = '<p class="s-msg">Loading the search…</p>'; }, 400);
    loading = import('/pagefind/pagefind.js').then(function (m) {
      clearTimeout(slow);
      pf = m;
      return pf.options({ excerptLength: 26, ranking: { metaWeights: { title: 5.0, also: 10.0, kind: 0.0, sub: 2.0, reading: 0.0 } } }).then(function () { pf.init(); return pf; });
    }).catch(function () {
      clearTimeout(slow);
      out.innerHTML = '<p class="s-msg">Search didn’t load. The <a href="/articles/">articles index</a> lists every article, and <a href="/?view=all">all the numbers</a> are on one page.</p>';
      say('Search didn’t load.', true);
      throw new Error('pagefind');
    });
    return loading;
  }

  function tryLine() {
    return '<p class="s-try"><span class="s-try-l">Try:</span> ' + TRY.map(function (t, i) {
      return '<span class="s-tryi">' + (i ? '<span class="sep" aria-hidden="true">\u00b7 </span>' : '') +
        '<a href="#q=' + encodeURIComponent(t) + '">' + esc(t) + '</a></span>';
    }).join(' ') + '</p>';
  }

  function idle() {
    lastQ = '';
    out.innerHTML = tryLine();
  }

  // Excerpts often open on the end of the title, which sits right above them.
  function stripTitle(ex, title) {
    var plain = '', map = [], i = 0;
    while (i < ex.length) {
      if (ex[i] === '<') { i = ex.indexOf('>', i) + 1; continue; }
      if (ex[i] === '&') { var e = ex.indexOf(';', i); plain += ' '; map.push(i); i = e + 1; continue; }
      plain += ex[i]; map.push(i); i++;
    }
    var t = title.toLowerCase(), p = plain.toLowerCase();
    for (var k = t.length; k >= 12; k--) {
      if (p.indexOf(t.slice(t.length - k)) === 0) {
        var cut = k;
        while (cut < plain.length && /[\s.,:;]/.test(plain[cut])) cut++;
        if (cut >= plain.length - 20) return ex;          // nothing left worth showing
        var at = map[cut];
        var opens = (ex.slice(0, at).match(/<mark>/g) || []).length - (ex.slice(0, at).match(/<\/mark>/g) || []).length;
        return (opens > 0 ? '<mark>' : '') + ex.slice(at);
      }
    }
    return ex;
  }

  function best(d) {
    // The section that holds most of the matches, if it isn't the top of the page.
    var subs = (d.sub_results || []).filter(function (s) { return s.anchor && s.anchor.id; });
    if (!subs.length) return null;
    subs.sort(function (a, b) { return (b.locations || []).length - (a.locations || []).length; });
    return subs[0];
  }

  function item(d) {
    var kind = (d.meta && d.meta.kind) || '';
    var title = (d.meta && d.meta.title) || d.url;
    // A section link only when the title doesn't already say why the page matched.
    var words = (lastQ || '').toLowerCase().split(/\s+/).filter(function (w) { return w.length > 2; });
    var tl = title.toLowerCase();
    var titleHits = words.some(function (w) { return tl.indexOf(w.replace(/s$/, '')) > -1; });
    var sub = titleHits ? null : best(d);
    var ex = sub ? sub.excerpt : d.excerpt;
    if (ex && !sub) ex = stripTitle(ex, title);
    if (ex) ex = '\u2026 ' + ex.replace(/^[\s,.;:]+/, '').replace(/[\s,;:]+$/, '') + ' \u2026';
    var url = d.url.replace(/index\.html$/, '');
    var h = '<li>';
    if (kind) h += '<span class="s-kind">' + esc(kind) + '</span>';
    h += '<a class="s-title" href="' + esc(url) + '">' + esc(title) + '</a>';
    if (kind === 'Chart' && d.meta.reading) {
      // A chart's answer is its latest reading: give it its own line, not an excerpt.
      if (d.meta.sub) h += '<p class="s-ex">' + esc(d.meta.sub) + '</p>';
      h += '<p class="s-read">' + esc(d.meta.reading.replace(/^[^:]*:\s*/, '')) + '</p>';
    } else if (ex) {
      h += '<p class="s-ex">' + ex + '</p>';
    }
    if (sub) h += '<p class="s-sec"><a href="' + esc(sub.url.replace(/index\.html(?=#|$)/, '')) + '">In the section \u201c' + esc(sub.title) + '\u201d<span class="sr-only"> of ' + esc(title) + '</span> \u2192</a></p>';
    return h + '</li>';
  }

  function more(count) {
    var next = all.slice(shown, shown + (count || PER));
    var mine = seq;
    return Promise.all(next.map(function (r) { return r.data(); })).then(function (ds) {
      if (mine !== seq) return;
      var ol = out.querySelector('ol.s-results');
      var first = shown;
      ol.insertAdjacentHTML('beforeend', ds.map(item).join(''));
      shown += ds.length;
      if (!fromPath && shown > PER) history.replaceState(null, '', location.pathname + '#q=' + encodeURIComponent(lastQ).replace(/%20/g, '+') + '&n=' + shown);
      var btn = out.querySelector('.s-more');
      if (shown >= all.length) { if (btn) btn.remove(); }
      else if (btn) btn.textContent = 'Show more results (' + (all.length - shown) + ' left)';
      return first;
    });
  }

  function run(q, now) {
    q = q.trim();
    if (q === lastQ) return;
    var mine = ++seq;
    if (privacy) privacy.hidden = !!q;
    if (!q) { idle(); say(''); setHash(''); return; }
    setHash(q);
    load().then(function () {
      var go = function (qq) {
        return pf.search(qq).then(function (s) {
          var ws = qq.split(' ');
          if (nfFirst && !s.results.length && ws.length > 1) return go(ws.slice(0, -1).join(' '));
          if (nfFirst) { q = qq; input.value = qq; nfDek(s.results.length, qq); }
          return s;
        });
      };
      return now ? go(q) : pf.debouncedSearch(q, {}, 220);
    }).then(function (s) {
      if (!s || mine !== seq) return;
      lastQ = q;
      all = s.results; shown = 0;
      if (!all.length) {
        out.innerHTML = (nfFirst ? '' : '<h2 class="s-count">No pages match “' + esc(q) + '.”</h2>') +
          (nfFirst ? '' : '<p class="s-msg">Try fewer words, or a plainer one: “gas” rather than “gasoline prices.”</p>') +
          (fromPath ? '' : '<p class="s-msg">The <a href="/articles/">articles index</a> lists every article, and <a href="/?view=all">all the numbers</a> are on one page.</p>') + tryLine();
        say('No pages match ' + q + '.', now);
        nfFirst = false;
        return;
      }
      var n = all.length;
      nfFirst = false;
      out.innerHTML = '<h2 class="s-count" id="s-count">' + n + (n === 1 ? ' page matches' : ' pages match') + ' “' + esc(q) + '”</h2>' +
        '<ol class="s-results" aria-labelledby="s-count"></ol>' +
        (n > PER ? '<button type="button" class="act s-more"></button>' : '');
      var btn = out.querySelector('.s-more');
      if (btn) btn.addEventListener('click', function () {
        more().then(function (first) {
          say('Showing ' + shown + ' of ' + all.length + '.', true);
          var li = out.querySelectorAll('ol.s-results > li')[first];
          if (li) { var a = li.querySelector('a.s-title'); if (a) a.focus(); }
        });
      });
      var want = firstRender ? hashN() : PER;
      var wasFirst = firstRender; firstRender = false;
      return more(want).then(function () {
        if (wasFirst) restoreScroll();
        say(n + (n === 1 ? ' page matches ' : ' pages match ') + q + '.', now);
      });
    }).catch(function () {});
  }

  function setHash(q) {
    var h = q ? '#q=' + encodeURIComponent(q).replace(/%20/g, '+') : '';
    if (fromPath) return;            // the 404 page keeps the address it was given
    if (q && hashQ() === q) return;  // same query: keep any &n= the reader had
    if (location.hash !== h) history.replaceState(null, '', location.pathname + h);
  }

  input.addEventListener('input', function () { run(input.value, false); });
  form.addEventListener('submit', function (e) { e.preventDefault(); lastQ = null; run(input.value, true); });
  window.addEventListener('hashchange', function () {
    var q = hashQ(); input.value = q; run(q, true);
    if (q) input.focus();
  });
  out.addEventListener('click', function (e) {
    var a = e.target.closest('.s-try a');
    if (!a) return;
    e.preventDefault();
    input.value = decodeURIComponent(a.getAttribute('href').slice(3));
    run(input.value, true);
    input.focus();
  });

  var start = fromPath ? pathWords() : hashQ();
  nfOrig = fromPath ? start : '';
  if (start) { input.value = start; run(start, true); }
  else if (fromPath) {
    nfFirst = false;
    var dk = document.getElementById('nf-dek');
    if (dk) dk.textContent = 'The address may be mistyped, or the page may have moved. Search below, or start from one of the pages listed.';
    out.innerHTML = tryLine();
  }
  else { idle(); load().catch(function () {}); input.focus(); }
})();
