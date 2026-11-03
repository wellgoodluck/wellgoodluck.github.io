// The section bar on the articles index: the same wayfinding as the almanac's (index.html keeps its own copy,
// inside its render). The bar stays at the top; the section whose heading has passed under it is marked
// aria-current; on phones the row scrolls sideways with edge fades and keeps the current link in view.
(function () {
  'use strict';
  const navEl = document.querySelector('.secnav'), nav = navEl && navEl.querySelector('.sections-nav');
  if (!nav) return;
  const links = Array.from(nav.querySelectorAll('a'));
  const targets = links.map(a => document.getElementById((a.getAttribute('href') || '').slice(1))).filter(Boolean);
  const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let current, ticking = false;
  function navH() { const h = navEl.offsetHeight; document.documentElement.style.setProperty('--nav-h', h + 'px'); return h; }
  function fades() { const max = nav.scrollWidth - nav.clientWidth; nav.classList.toggle('fade-l', nav.scrollLeft > 2); nav.classList.toggle('fade-r', max > 2 && nav.scrollLeft < max - 2); }
  function markCurrent() {
    ticking = false;
    const line = navH() + 24;
    let cur = null;
    targets.forEach(x => { if (x.getBoundingClientRect().top <= line) cur = x; });
    if (cur === current) return;
    current = cur;
    links.forEach(a => { if (cur && a.getAttribute('href') === '#' + cur.id) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current'); });
    const a = links.find(x => x.hasAttribute('aria-current'));
    if (a && nav.scrollWidth > nav.clientWidth) {
      const ar = a.getBoundingClientRect(), ur = nav.getBoundingClientRect();
      if (ar.left < ur.left + 24 || ar.right > ur.right - 24) nav.scrollBy({ left: ar.left - ur.left - 28, behavior: still ? 'auto' : 'smooth' });
    }
  }
  window.addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(markCurrent); } }, { passive: true });
  window.addEventListener('resize', () => { navH(); fades(); markCurrent(); });
  nav.addEventListener('scroll', fades, { passive: true });
  navH(); fades(); markCurrent();
})();
