/* Economy in Context: sharing on article pages (Nov 11). Built into every article by tools/build_articles.py.
   - Top: a text button at the end of the dateline. Computers (hover + fine pointer): "Copy link". Phones and tablets:
     "Share" (the device's own menu) where the browser has one, else "Copy link". "Link copied." shows beside it.
   - End: Computers: Copy link · Email the link · Print or save as PDF. Phones: Share · Copy link (no share menu:
     Copy link · Email the link).
   - Section links (computers only, by CSS): copy the article's address with the section's #anchor.
   - #share-live (visually hidden) announces every result; the visible messages are aria-hidden. Messages clear after 6 s.
   - A refused copy shows the link in a read-only box, focused and selected, to copy by hand.
   Nothing is stored or sent; the click counts come from data-goatcounter-click on each control (assets/count.js). */
(function () {
  var top = document.getElementById('share-top'), end = document.getElementById('share-end');
  var live = document.getElementById('share-live'), status = document.getElementById('share-status');
  var canon = document.querySelector('link[rel="canonical"]');
  if (!top || !end || !live || !canon) return;
  var url = canon.href, title = document.querySelector('h1').textContent;
  var computer = window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches;
  var useShare = !computer && typeof navigator.share === 'function';
  var timers = {};

  function say(msg) { live.textContent = ''; setTimeout(function () { live.textContent = msg; }, 60); }
  function flash(el, msg, key, ms) {
    clearTimeout(timers[key]); el.textContent = msg;
    timers[key] = setTimeout(function () { el.textContent = ''; }, ms || 6000);
  }
  function clearByHand() { Array.prototype.forEach.call(document.querySelectorAll('.by-hand'), function (x) { x.parentNode.removeChild(x); }); }
  function byHand(after, link) {
    clearByHand();
    var d = document.createElement('div'); d.className = 'by-hand';
    d.innerHTML = '<label>This browser would not copy. Copy the link from here:<input type="text" readonly></label>';
    var i = d.querySelector('input'); i.value = link;
    after.parentNode.insertBefore(d, after.nextSibling);
    i.focus(); i.select(); try { i.setSelectionRange(0, i.value.length); } catch (e) {}
  }
  function copy(text, ok, no) {
    var done = function () { clearByHand(); ok(); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, no); else no();
  }
  var COPIED = 'Link copied. Paste it into a text or an email.';

  /* top */
  var tb = top.querySelector('.tbtn'), td = top.querySelector('.done');
  tb.textContent = useShare ? 'Share' : 'Copy link';
  tb.setAttribute('aria-label', useShare ? 'Share this article' : 'Copy link to this article');
  top.hidden = false;
  tb.addEventListener('click', function () {
    if (useShare) {
      try {
        navigator.share({ title: title, url: url }).catch(function (e) { if (e && e.name !== 'AbortError') shareFailed(); });
      } catch (e) { shareFailed(); }
      return;
    }
    copy(url, function () { flash(td, 'Link copied.', 'top'); say(COPIED); },
              function () { byHand(document.querySelector('.article .dateline'), url); });
  });
  function shareFailed() {
    useShare = false; tb.textContent = 'Copy link'; tb.setAttribute('aria-label', 'Copy link to this article');
    var m = 'The share menu did not open. This now copies the link.'; flash(td, m, 'top', 8000); say(m);
  }

  /* end */
  var sb = end.querySelector('.share-btn'), cb = end.querySelector('.copy-btn'), eb = end.querySelector('.email-btn'), pb = end.querySelector('.print-btn');
  sb.hidden = !useShare; eb.hidden = useShare; pb.hidden = !computer;
  end.hidden = false;
  sb.addEventListener('click', function () {
    var fail = function () { var m = 'The share menu did not open. Use Copy link instead.'; flash(status, m, 'end', 8000); say(m); };
    try { navigator.share({ title: title, url: url }).catch(function (e) { if (e && e.name !== 'AbortError') fail(); }); } catch (e) { fail(); }
  });
  cb.addEventListener('click', function () {
    copy(url, function () { flash(status, COPIED, 'end'); say(COPIED); },
              function () { byHand(end.querySelector('.share-btns'), url); });
  });
  eb.addEventListener('click', function () {
    var m = 'Your email app should open with the link in a new message. If nothing opens, use Copy link.';
    flash(status, m, 'end', 9000); say(m);
  });
  pb.addEventListener('click', function () { window.print(); });

  /* section links (shown on computers only) */
  Array.prototype.forEach.call(document.querySelectorAll('.article h2 .h-link'), function (a) {
    var name = (a.getAttribute('aria-label') || '').replace(/^Link to this section: /, '');
    a.setAttribute('aria-label', 'Copy a link to this section: ' + name);
    a.addEventListener('click', function (ev) {
      ev.preventDefault();
      var id = a.getAttribute('href'), h = a.parentNode, d = h.querySelector('.h-done');
      if (!d) { d = document.createElement('span'); d.className = 'h-done'; d.setAttribute('aria-hidden', 'true'); h.appendChild(d); }
      try { history.replaceState(null, '', location.pathname + location.search + id); } catch (e) {}
      copy(url + id, function () {
          a.classList.add('on'); flash(d, 'Link copied.', 'h' + id);
          setTimeout(function () { a.classList.remove('on'); }, 6000);
          say('Link to the section ' + name + ' copied.');
        }, function () {
          flash(d, 'The link is in the address bar.', 'h' + id, 8000); say('The link to this section is in the address bar.');
        });
    });
  });
})();
